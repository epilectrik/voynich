"""
P-C12: Alternative hypothesis discrimination — "adjust" vs "correct" vs "calibrate"

Discriminates between three gloss hypotheses using timing relative to
state changes and contextual enrichment patterns.

Predictions:
- "adjust" (H1): NEUTRAL timing (35-55% post-state-change), R4-late <= 1.3x, post-FL_HAZ <= 1.3x
- "correct" (H2): RESPONDER timing (>55% post-state-change), post-FL_HAZ >= 1.5x
- "calibrate" (H3): ACTOR timing (<35% post-state-change), R4-late >= 1.5x

Based on:
- c MEDIAL slot mean 0.408 (C1209) — mid-line, neither early nor late
- c POSITIVE carryover z=+3.23 (C1208) — state-persistent
- {c,h} monitoring cluster (C1207)
- CategoryClassifier maps c → MARKING
"""

import sys
import math
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))
from scripts.voynich import Transcript, Morphology, BFolioDecoder, CategoryClassifier


CATEGORIES = ['THERMAL', 'FLOW', 'CONTAINMENT', 'STAGING', 'OPERATION', 'TRANSITION', 'MARKING', 'MONITORING']


def main():
    print("=" * 70)
    print("P-C12: Alternative hypothesis discrimination")
    print("         adjust vs correct vs calibrate")
    print("=" * 70)

    tx = Transcript()
    morph = Morphology()
    decoder = BFolioDecoder()

    # --- Collect tokens with macro-state annotations ---
    # Group by (folio, line), preserving order
    line_tokens = defaultdict(list)

    for token in tx.currier_b():
        w = token.word
        if not w or '*' in w:
            continue
        m = morph.extract(w)
        if not m or not m.middle:
            continue
        mid = m.middle

        try:
            ts = decoder.analyze_token(w)
            macro = ts.macro_state if ts.macro_state else 'UNK'
        except Exception:
            macro = 'UNK'

        line_key = (token.folio, token.line)
        line_tokens[line_key].append({
            'word': w,
            'middle': mid,
            'initial': mid[0] if mid else '',
            'macro': macro,
            'position': token.position if hasattr(token, 'position') else 0,
        })

    # --- Compute per-line normalized positions ---
    for line_key, tokens in line_tokens.items():
        n = len(tokens)
        for i, tok in enumerate(tokens):
            tok['norm_pos'] = i / (n - 1) if n > 1 else 0.5

    # --- Test 1: Post-state-change rate ---
    # For each token at position i>0, check if macro_state differs from i-1
    # Compute: for each initial atom, fraction of tokens that follow a state change
    atom_post_change = defaultdict(lambda: {'post': 0, 'no_post': 0})
    total_post_change = 0
    total_no_change = 0

    for line_key in sorted(line_tokens.keys()):
        tokens = line_tokens[line_key]
        for i in range(1, len(tokens)):
            prev_macro = tokens[i - 1]['macro']
            curr_macro = tokens[i]['macro']
            initial = tokens[i]['initial']
            if not initial or prev_macro == 'UNK' or curr_macro == 'UNK':
                continue

            is_post_change = (curr_macro != prev_macro)
            if is_post_change:
                atom_post_change[initial]['post'] += 1
                total_post_change += 1
            else:
                atom_post_change[initial]['no_post'] += 1
                total_no_change += 1

    # Baseline post-change rate
    baseline_post_rate = total_post_change / (total_post_change + total_no_change) if (total_post_change + total_no_change) > 0 else 0

    print(f"\nBaseline post-state-change rate: {baseline_post_rate * 100:.1f}%")
    print(f"Total transitions: {total_post_change + total_no_change} ({total_post_change} changes, {total_no_change} same)")

    print("\n--- Post-state-change rate by initial atom ---\n")
    print(f"{'Atom':<6} {'Post':>6} {'Same':>6} {'Total':>6} {'Rate%':>7} {'Enrich':>8}")
    print("-" * 45)

    atom_rates = {}
    for atom in sorted(atom_post_change.keys()):
        d = atom_post_change[atom]
        total = d['post'] + d['no_post']
        if total < 10:
            continue
        rate = d['post'] / total
        enrich = rate / baseline_post_rate if baseline_post_rate > 0 else 0
        atom_rates[atom] = (rate, enrich, total)
        marker = " <-- c" if atom == 'c' else ""
        print(f"{atom:<6} {d['post']:>6} {d['no_post']:>6} {total:>6} {rate * 100:>6.1f}% {enrich:>7.2f}x{marker}")

    c_post_rate = atom_rates.get('c', (0, 0, 0))[0]
    c_post_enrich = atom_rates.get('c', (0, 0, 0))[1]

    # --- Test 2: Post-FL_HAZ enrichment ---
    # FL_HAZ classes: {7, 30} per C582/C586
    # Approximate: check if previous token's macro_state indicates hazard
    # Use macro_state 'FLh' or just check if previous token is in FL hazard
    # Simpler: check if previous macro_state != current (any transition) AND previous was a high-risk state
    # Even simpler: check post-FQ or post-hazard-related transitions

    # Actually, let's use a simpler proxy: tokens following FL-classified MIDDLEs
    # FL MIDDLEs are those in classes {7, 30, 38, 40} — short MIDDLEs like am, ar, ary, etc.
    # FL_HAZ = {7, 30}, FL_SAFE = {38, 40}
    # We approximate by checking if preceding token is in hazard zone of macro-automaton

    atom_post_fl = defaultdict(lambda: {'post_haz': 0, 'other': 0})

    for line_key in sorted(line_tokens.keys()):
        tokens = line_tokens[line_key]
        for i in range(1, len(tokens)):
            prev_macro = tokens[i - 1]['macro']
            initial = tokens[i]['initial']
            if not initial or prev_macro == 'UNK':
                continue

            # FLh (hazard FL) and FLs (safe FL) are macro-states if available
            # Otherwise approximate: if previous macro is FL-related
            is_post_haz = prev_macro in ('FLh', 'FL_HAZ', 'FQ', 'CC')  # hazard-adjacent states
            if is_post_haz:
                atom_post_fl[initial]['post_haz'] += 1
            else:
                atom_post_fl[initial]['other'] += 1

    total_post_haz = sum(v['post_haz'] for v in atom_post_fl.values())
    total_other = sum(v['other'] for v in atom_post_fl.values())
    baseline_haz_rate = total_post_haz / (total_post_haz + total_other) if (total_post_haz + total_other) > 0 else 0

    print(f"\n--- Post-hazard-adjacent context enrichment ---")
    print(f"Baseline post-hazard-adjacent rate: {baseline_haz_rate * 100:.1f}%\n")
    print(f"{'Atom':<6} {'PostHaz':>7} {'Other':>7} {'Total':>7} {'Rate%':>7} {'Enrich':>8}")
    print("-" * 50)

    c_haz_enrich = 1.0
    for atom in sorted(atom_post_fl.keys()):
        d = atom_post_fl[atom]
        total = d['post_haz'] + d['other']
        if total < 10:
            continue
        rate = d['post_haz'] / total
        enrich = rate / baseline_haz_rate if baseline_haz_rate > 0 else 0
        if atom == 'c':
            c_haz_enrich = enrich
        marker = " <-- c" if atom == 'c' else ""
        print(f"{atom:<6} {d['post_haz']:>7} {d['other']:>7} {total:>7} {rate * 100:>6.1f}% {enrich:>7.2f}x{marker}")

    # --- Test 3: Late-position enrichment (precision/calibration proxy) ---
    # "R4 context" = tokens at normalized position 0.7-1.0 (late line positions)
    atom_late = defaultdict(lambda: {'late': 0, 'other': 0})

    for line_key in sorted(line_tokens.keys()):
        tokens = line_tokens[line_key]
        for tok in tokens:
            initial = tok['initial']
            if not initial:
                continue
            if tok['norm_pos'] >= 0.7:
                atom_late[initial]['late'] += 1
            else:
                atom_late[initial]['other'] += 1

    total_late = sum(v['late'] for v in atom_late.values())
    total_early = sum(v['other'] for v in atom_late.values())
    baseline_late_rate = total_late / (total_late + total_early) if (total_late + total_early) > 0 else 0

    print(f"\n--- Late-position (0.7-1.0) enrichment ---")
    print(f"Baseline late rate: {baseline_late_rate * 100:.1f}%\n")
    print(f"{'Atom':<6} {'Late':>6} {'Other':>7} {'Total':>7} {'Rate%':>7} {'Enrich':>8}")
    print("-" * 50)

    c_late_enrich = 1.0
    for atom in sorted(atom_late.keys()):
        d = atom_late[atom]
        total = d['late'] + d['other']
        if total < 10:
            continue
        rate = d['late'] / total
        enrich = rate / baseline_late_rate if baseline_late_rate > 0 else 0
        if atom == 'c':
            c_late_enrich = enrich
        marker = " <-- c" if atom == 'c' else ""
        print(f"{atom:<6} {d['late']:>6} {d['other']:>7} {total:>7} {rate * 100:>6.1f}% {enrich:>7.2f}x{marker}")

    # --- Hypothesis comparison table ---
    print("\n" + "=" * 70)
    print("HYPOTHESIS COMPARISON")
    print("=" * 70)

    print(f"\n{'Metric':<30} {'Observed':>10} {'H1 adjust':>12} {'H2 correct':>12} {'H3 calibr':>12}")
    print("-" * 80)

    c_timing_pct = c_post_rate * 100

    # Post-state-change rate
    h1_timing = "35-55%"
    h2_timing = ">55%"
    h3_timing = "<35%"
    obs_timing = f"{c_timing_pct:.1f}%"
    print(f"{'Post-state-change rate':<30} {obs_timing:>10} {h1_timing:>12} {h2_timing:>12} {h3_timing:>12}")

    # Post-FL_HAZ enrichment
    obs_haz = f"{c_haz_enrich:.2f}x"
    print(f"{'Post-hazard-adj enrichment':<30} {obs_haz:>10} {'<=1.3x':>12} {'>=1.5x':>12} {'any':>12}")

    # Late-position enrichment
    obs_late = f"{c_late_enrich:.2f}x"
    print(f"{'Late-position enrichment':<30} {obs_late:>10} {'<=1.3x':>12} {'any':>12} {'>=1.5x':>12}")

    # --- Score each hypothesis ---
    h1_score = 0
    h2_score = 0
    h3_score = 0

    # Timing
    if 35 <= c_timing_pct <= 55:
        h1_score += 1
    if c_timing_pct > 55:
        h2_score += 1
    if c_timing_pct < 35:
        h3_score += 1

    # Post-hazard
    if c_haz_enrich <= 1.3:
        h1_score += 1
    if c_haz_enrich >= 1.5:
        h2_score += 1
    # H3: no constraint on hazard

    # Late-position
    if c_late_enrich <= 1.3:
        h1_score += 1
    if c_late_enrich >= 1.5:
        h3_score += 1
    # H2: no constraint on late position

    print(f"\n{'Hypothesis scores:':<30}")
    print(f"  H1 'adjust':    {h1_score}/3 criteria met")
    print(f"  H2 'correct':   {h2_score}/2 criteria met")
    print(f"  H3 'calibrate': {h3_score}/2 criteria met")

    # --- Verdicts ---
    print("\n" + "=" * 70)
    print("VERDICTS")
    print("=" * 70)

    # P1: NEUTRAL timing 35-55%
    p1 = 35 <= c_timing_pct <= 55
    print(f"P1: c post-state-change rate = {c_timing_pct:.1f}% in [35%, 55%]: {'PASS' if p1 else 'FAIL'}")

    # P2: R4/late enrichment <= 1.3x
    p2 = c_late_enrich <= 1.3
    print(f"P2: c late-position enrichment = {c_late_enrich:.2f}x <= 1.3x: {'PASS' if p2 else 'FAIL'}")

    # P3: Post-FL_HAZ enrichment <= 1.3x
    p3 = c_haz_enrich <= 1.3
    print(f"P3: c post-hazard-adj enrichment = {c_haz_enrich:.2f}x <= 1.3x: {'PASS' if p3 else 'FAIL'}")

    overall = p1 and p2 and p3
    print(f"\nOVERALL: {'PASS' if overall else 'FAIL'}")

    if h1_score >= 3:
        winner = "H1 'adjust'"
    elif h2_score >= 2:
        winner = "H2 'correct'"
    elif h3_score >= 2:
        winner = "H3 'calibrate'"
    else:
        winner = "INCONCLUSIVE"

    print(f"Best-fit hypothesis: {winner}")

    if overall:
        print("  All three 'adjust' criteria met: c is timing-neutral, not hazard-reactive,")
        print("  and not precision-concentrated. Consistent with general-purpose adjustment.")
    else:
        if not p1:
            if c_timing_pct > 55:
                print("  Timing suggests RESPONDER pattern (correct)")
            else:
                print("  Timing suggests ACTOR pattern (calibrate)")
        if not p2:
            print("  Late-position concentration suggests precision/calibration role")
        if not p3:
            print("  Post-hazard enrichment suggests corrective/reactive role")


if __name__ == '__main__':
    main()
