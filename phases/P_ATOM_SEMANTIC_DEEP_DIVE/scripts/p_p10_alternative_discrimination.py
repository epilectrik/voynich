"""
P-P10: Alternative hypothesis discrimination -- "pause" vs "check/test" vs "try/sample"

Discriminates between three gloss hypotheses for atom p using timing
relative to state changes, post-hazard enrichment, line position,
and category dominance.

Hypotheses:
- H1 "pause" (pausieren): NEUTRAL timing (35-55%), low FL_HAZ (<=1.0x),
  early-MEDIAL position
- H2 "check/test" (pruefen): RESPONDER timing (>55%), MONITORING dominant,
  high CHSH affinity
- H3 "try/sample" (probieren): ACTOR timing (<35%), late-line (>0.55),
  OPERATION enrichment

Based on:
- p MEDIAL slot (C1209)
- p POSITIVE carryover (C1208): state-persistent
- {o,p} structural cluster r=+0.41 (C1207)
- CategoryClassifier maps p -> MARKING
"""

import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))
from scripts.voynich import Transcript, Morphology, BFolioDecoder, CategoryClassifier


CATEGORIES = ['THERMAL', 'FLOW', 'CONTAINMENT', 'STAGING', 'OPERATION', 'TRANSITION', 'MARKING', 'MONITORING']


def main():
    print("=" * 70)
    print("P-P10: Alternative hypothesis discrimination")
    print("          pause vs check/test vs try/sample")
    print("=" * 70)

    tx = Transcript()
    morph = Morphology()
    decoder = BFolioDecoder()
    cc = CategoryClassifier()

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

        cat = cc.classify(mid)

        line_key = (token.folio, token.line)
        line_tokens[line_key].append({
            'word': w,
            'middle': mid,
            'initial': mid[0] if mid else '',
            'macro': macro,
            'category': cat,
        })

    # --- Compute per-line normalized positions ---
    for line_key, tokens in line_tokens.items():
        n = len(tokens)
        for i, tok in enumerate(tokens):
            tok['norm_pos'] = i / (n - 1) if n > 1 else 0.5

    # --- Test 1: Post-state-change rate ---
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
        marker = " <-- p" if atom == 'p' else ""
        print(f"{atom:<6} {d['post']:>6} {d['no_post']:>6} {total:>6} {rate * 100:>6.1f}% {enrich:>7.2f}x{marker}")

    p_post_rate = atom_rates.get('p', (0, 0, 0))[0]
    p_post_enrich = atom_rates.get('p', (0, 0, 0))[1]

    # --- Test 2: Post-hazard-adjacent enrichment ---
    atom_post_fl = defaultdict(lambda: {'post_haz': 0, 'other': 0})

    for line_key in sorted(line_tokens.keys()):
        tokens = line_tokens[line_key]
        for i in range(1, len(tokens)):
            prev_macro = tokens[i - 1]['macro']
            initial = tokens[i]['initial']
            if not initial or prev_macro == 'UNK':
                continue

            is_post_haz = prev_macro in ('FLh', 'FL_HAZ', 'FQ', 'CC')
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

    p_haz_enrich = 1.0
    for atom in sorted(atom_post_fl.keys()):
        d = atom_post_fl[atom]
        total = d['post_haz'] + d['other']
        if total < 10:
            continue
        rate = d['post_haz'] / total
        enrich = rate / baseline_haz_rate if baseline_haz_rate > 0 else 0
        if atom == 'p':
            p_haz_enrich = enrich
        marker = " <-- p" if atom == 'p' else ""
        print(f"{atom:<6} {d['post_haz']:>7} {d['other']:>7} {total:>7} {rate * 100:>6.1f}% {enrich:>7.2f}x{marker}")

    # --- Test 3: Mean normalized line position ---
    atom_positions = defaultdict(list)

    for line_key in sorted(line_tokens.keys()):
        tokens = line_tokens[line_key]
        for tok in tokens:
            initial = tok['initial']
            if not initial:
                continue
            atom_positions[initial].append(tok['norm_pos'])

    print(f"\n--- Mean normalized line position ---\n")
    print(f"{'Atom':<6} {'Mean pos':>8} {'N':>7}")
    print("-" * 25)

    p_mean_pos = 0.5
    for atom in sorted(atom_positions.keys()):
        positions = atom_positions[atom]
        if len(positions) < 10:
            continue
        mean_pos = sum(positions) / len(positions)
        if atom == 'p':
            p_mean_pos = mean_pos
        marker = " <-- p" if atom == 'p' else ""
        print(f"{atom:<6} {mean_pos:>8.3f} {len(positions):>7}{marker}")

    # --- Test 4: Category dominance for p-initial ---
    p_cat_counts = defaultdict(int)
    p_cat_total = 0
    for line_key in sorted(line_tokens.keys()):
        tokens = line_tokens[line_key]
        for tok in tokens:
            if tok['initial'] == 'p' and tok['category'] in CATEGORIES:
                p_cat_counts[tok['category']] += 1
                p_cat_total += 1

    print(f"\n--- Category distribution for p-initial MIDDLEs (N={p_cat_total}) ---\n")
    print(f"{'Category':<15} {'Count':>7} {'Rate%':>8}")
    print("-" * 35)
    p_dominant_cat = None
    p_dominant_frac = 0
    for cat in CATEGORIES:
        cnt = p_cat_counts[cat]
        rate = cnt / p_cat_total if p_cat_total > 0 else 0
        if rate > p_dominant_frac:
            p_dominant_frac = rate
            p_dominant_cat = cat
        print(f"{cat:<15} {cnt:>7} {rate * 100:>7.1f}%")

    print(f"\nDominant category for p: {p_dominant_cat} ({p_dominant_frac * 100:.1f}%)")

    # --- CHSH affinity check (proxy: check if p-initial tokens are more often
    #     in ch/sh-prefixed contexts) ---
    p_prefix_counts = defaultdict(int)
    p_prefix_total = 0
    for line_key in sorted(line_tokens.keys()):
        tokens = line_tokens[line_key]
        for tok in tokens:
            if tok['initial'] == 'p':
                w = tok['word']
                m = morph.extract(w)
                if m and m.prefix:
                    p_prefix_counts[m.prefix] += 1
                    p_prefix_total += 1
                else:
                    p_prefix_counts['BARE'] += 1
                    p_prefix_total += 1

    chsh_frac = 0
    if p_prefix_total > 0:
        chsh_count = sum(p_prefix_counts.get(pfx, 0) for pfx in ['ch', 'sh'])
        chsh_frac = chsh_count / p_prefix_total

    print(f"\np-initial CHSH PREFIX affinity: {chsh_frac * 100:.1f}% (of {p_prefix_total} tokens)")

    # --- Hypothesis comparison table ---
    print("\n" + "=" * 70)
    print("HYPOTHESIS COMPARISON")
    print("=" * 70)

    p_timing_pct = p_post_rate * 100

    print(f"\n{'Metric':<30} {'Observed':>12} {'H1 pause':>12} {'H2 check':>12} {'H3 try':>12}")
    print("-" * 80)

    print(f"{'Post-state-change rate':<30} {p_timing_pct:>11.1f}% {'35-55%':>12} {'>55%':>12} {'<35%':>12}")
    print(f"{'Post-hazard enrichment':<30} {p_haz_enrich:>11.2f}x {'<=1.0x':>12} {'>=1.5x':>12} {'any':>12}")
    print(f"{'Mean line position':<30} {p_mean_pos:>11.3f} {'0.35-0.55':>12} {'>0.55':>12} {'>0.55':>12}")
    print(f"{'Dominant category':<30} {p_dominant_cat:>12} {'MARKING':>12} {'MONITORING':>12} {'OPERATION':>12}")

    # --- Score each hypothesis ---
    h1_score = 0
    h2_score = 0
    h3_score = 0

    # Timing
    if 35 <= p_timing_pct <= 55:
        h1_score += 1
    if p_timing_pct > 55:
        h2_score += 1
    if p_timing_pct < 35:
        h3_score += 1

    # Post-hazard
    if p_haz_enrich <= 1.0:
        h1_score += 1
    if p_haz_enrich >= 1.5:
        h2_score += 1
    # H3: no constraint on hazard

    # Line position
    if 0.35 <= p_mean_pos <= 0.55:
        h1_score += 1
    if p_mean_pos > 0.55:
        h2_score += 1
        h3_score += 1
    if p_mean_pos < 0.35:
        h3_score += 1

    print(f"\n{'Hypothesis scores:':<30}")
    print(f"  H1 'pause':      {h1_score}/3 criteria met")
    print(f"  H2 'check/test': {h2_score}/3 criteria met")
    print(f"  H3 'try/sample': {h3_score}/2 criteria met")

    # --- Verdicts ---
    print("\n" + "=" * 70)
    print("VERDICTS")
    print("=" * 70)

    # V1: Timing discriminant
    if 35 <= p_timing_pct <= 55:
        timing_label = "NEUTRAL (H1 pause)"
    elif p_timing_pct > 55:
        timing_label = "RESPONDER (H2 check/test)"
    else:
        timing_label = "ACTOR (H3 try/sample)"
    v1 = 35 <= p_timing_pct <= 55
    print(f"V1: p post-state-change rate = {p_timing_pct:.1f}% -> {timing_label}: {'PASS' if v1 else 'FAIL'}")

    # V2: Post-hazard enrichment
    v2 = p_haz_enrich <= 1.0
    print(f"V2: p post-hazard enrichment = {p_haz_enrich:.2f}x <= 1.0x: {'PASS' if v2 else 'FAIL'}")

    # V3: Line position
    v3 = 0.35 <= p_mean_pos <= 0.55
    print(f"V3: p mean line position = {p_mean_pos:.3f} in [0.35, 0.55]: {'PASS' if v3 else 'FAIL'}")

    overall = h1_score >= 2
    print(f"\nOVERALL: {'PASS' if overall else 'FAIL'} (H1 'pause' scores >= 2/3 discriminants)")

    if h1_score >= 3:
        winner = "H1 'pause' (pausieren)"
    elif h2_score >= 3:
        winner = "H2 'check/test' (pruefen)"
    elif h3_score >= 2:
        winner = "H3 'try/sample' (probieren)"
    elif h1_score >= 2:
        winner = "H1 'pause' (pausieren) [partial]"
    elif h2_score >= 2:
        winner = "H2 'check/test' (pruefen) [partial]"
    else:
        winner = "INCONCLUSIVE"

    print(f"Best-fit hypothesis: {winner}")

    if h1_score >= 2:
        print("  Timing and position consistent with neutral pause/hold function.")
        print("  p marks operational pauses rather than reactive checking or exploratory sampling.")
    elif h2_score >= 2:
        print("  Evidence points toward checking/testing function (RESPONDER pattern).")
    elif h3_score >= 2:
        print("  Evidence points toward trial/sampling function (ACTOR pattern).")
    else:
        print("  No clear winner among the three hypotheses.")


if __name__ == '__main__':
    main()
