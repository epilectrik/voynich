"""
C131 audit: re-measure role consistency with proper null calibration.

C131 says: "Role consistency LOW (23.8%, threshold >80%)" - Tier 2 statistical
falsification of DSL/language hypothesis from Phase X.5
(`phase_x5_discriminator.py`, function `test_symbolic_reuse`).

Original metric (re-implementing exactly):
  For high-frequency A-text tokens (>=5 occurrences) that also appear in
  B-text (>=2 occurrences):
    - In B-text, collect (prev, token, next) bigram contexts
    - role_consistency(token) = (P(most-common prev) + P(most-common next)) / 2
  Average across top 50 such tokens.

Audit questions:
  1. Does 23.8% reproduce on current data?
  2. What is the null under within-line shuffle (preserve line length + line membership)?
  3. What is the null under fully random token order (vocab-preserving)?
  4. How does the metric scale with token frequency (N)? Low-N tokens get
     artificially-high role_consistency by chance.
  5. Is the threshold ">80% = DSL" calibrated against any NL baseline, or
     just asserted?

Pre-registered audit decision rules:
  - If observed (23.8%) > null + 2*null_std: claim survives (effect real)
  - If observed within 2*null_std of null: 23.8% is at noise floor, C131
    Tier 2 framing requires revision
  - If observed below null: would be very surprising

The crazy-expert prediction: null is around 15-20%, so observed +5pp above
null at the metric scale. C131 might be at noise floor.
"""
from __future__ import annotations

import json
import math
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path("C:/git/voynich")
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript

OUT_PATH = ROOT / 'phases' / 'C131_AUDIT' / 'results' / 'role_consistency_audit.json'

N_PERM_SHUFFLE = 50  # within-line shuffle permutations
N_PERM_RANDOM = 50   # fully-random vocab-preserving permutations
N_TOKENS_ANALYZED = 50  # match original methodology
MIN_A_OCCURRENCES = 5
MIN_B_OCCURRENCES = 2


def collect_records():
    """Collect (folio, line, position, word, language) records."""
    tx = Transcript()
    records = []
    line_positions = defaultdict(list)  # (folio, line) -> [word, ...]
    for t in tx.all(h_only=True):
        if not t.word.strip() or '*' in t.word:
            continue
        word = t.word.lower()
        key = (t.folio, t.line)
        if t.line is None or t.line == '':
            continue
        pos_in_line = len(line_positions[key])
        line_positions[key].append(word)
        records.append({
            'folio': t.folio,
            'line': t.line,
            'pos': pos_in_line,
            'word': word,
            'language': t.language,
        })
    return records, dict(line_positions)


def get_bigram_contexts(records, lang_filter=None):
    """Build {word: [{'prev': ..., 'next': ...}]} per token, using line as scope."""
    contexts = defaultdict(list)
    # Group by (folio, line)
    by_line = defaultdict(list)
    for r in records:
        if lang_filter and r['language'] != lang_filter:
            continue
        by_line[(r['folio'], r['line'])].append(r)
    for line_recs in by_line.values():
        line_recs.sort(key=lambda x: x['pos'])
        for i, r in enumerate(line_recs):
            prev = line_recs[i-1]['word'] if i > 0 else '<START>'
            nxt = line_recs[i+1]['word'] if i < len(line_recs)-1 else '<END>'
            contexts[r['word']].append({'prev': prev, 'next': nxt})
    return dict(contexts)


def compute_role_consistency(a_contexts, b_contexts, min_a=MIN_A_OCCURRENCES,
                              min_b=MIN_B_OCCURRENCES, n_tokens=N_TOKENS_ANALYZED):
    """Reproduces phase_x5_discriminator.test_symbolic_reuse."""
    # High-frequency A-text tokens
    a_token_counts = {w: len(ctxs) for w, ctxs in a_contexts.items()}
    high_freq_a = sorted([t for t, c in a_token_counts.items() if c >= min_a],
                          key=lambda t: -a_token_counts[t])

    role_consistencies = []
    per_token = []
    for token in high_freq_a[:n_tokens]:
        if token not in b_contexts or len(b_contexts[token]) < min_b:
            continue
        b_ctxs = b_contexts[token]
        b_prevs = Counter(c['prev'] for c in b_ctxs)
        b_nexts = Counter(c['next'] for c in b_ctxs)
        prev_frac = b_prevs.most_common(1)[0][1] / len(b_ctxs) if b_prevs else 0
        next_frac = b_nexts.most_common(1)[0][1] / len(b_ctxs) if b_nexts else 0
        rc = (prev_frac + next_frac) / 2
        role_consistencies.append(rc)
        per_token.append({
            'token': token,
            'b_n': len(b_ctxs),
            'prev_frac': prev_frac,
            'next_frac': next_frac,
            'role_consistency': rc,
        })

    avg_rc = sum(role_consistencies) / len(role_consistencies) if role_consistencies else 0
    return avg_rc, per_token, role_consistencies


def shuffle_within_line(records, line_positions, rng):
    """Return new records with words shuffled within each line (preserves line
    membership, line length, per-folio vocabulary)."""
    new_recs = []
    for (folio, line), words in line_positions.items():
        words_shuffled = list(words)
        rng.shuffle(words_shuffled)
        for pos, w in enumerate(words_shuffled):
            new_recs.append({
                'folio': folio, 'line': line, 'pos': pos, 'word': w,
                # Preserve original language per position
                'language': None,
            })
    # Carry language through: just look it up from the original by position
    # Actually easier: build language mapping per (folio,line,pos) from originals
    orig_lang = {(r['folio'], r['line'], r['pos']): r['language'] for r in records}
    for r in new_recs:
        r['language'] = orig_lang.get((r['folio'], r['line'], r['pos']))
    return new_recs


def shuffle_fully_random(records, rng):
    """Fully random permutation of all words across all positions (preserves
    vocabulary frequencies but breaks all positional structure)."""
    all_words = [r['word'] for r in records]
    rng.shuffle(all_words)
    new_recs = []
    for i, r in enumerate(records):
        new_recs.append({**r, 'word': all_words[i]})
    return new_recs


def run_null(records, line_positions, null_fn, n_perm, label):
    """Run null permutation and collect role-consistency distribution."""
    rng = random.Random(13131)
    null_avgs = []
    for i in range(n_perm):
        if null_fn == 'within_line':
            shuffled = shuffle_within_line(records, line_positions, rng)
        else:
            shuffled = shuffle_fully_random(records, rng)
        a_ctx = get_bigram_contexts(shuffled, lang_filter='A')
        b_ctx = get_bigram_contexts(shuffled, lang_filter='B')
        avg, _, _ = compute_role_consistency(a_ctx, b_ctx)
        null_avgs.append(avg)
        if (i + 1) % 10 == 0:
            print(f"  {label} permutation {i+1}/{n_perm}: avg_rc = {avg:.4f}")
    return null_avgs


def main():
    print("=" * 80)
    print("C131 AUDIT: Role consistency 23.8% vs proper null calibration")
    print("=" * 80)

    print("\nLoading transcript...")
    records, line_positions = collect_records()
    print(f"  {len(records)} H-track tokens across {len(line_positions)} lines")

    # ---- Observed (replicate original) ----
    print("\n--- OBSERVED (reproducing C131) ---")
    a_ctx = get_bigram_contexts(records, lang_filter='A')
    b_ctx = get_bigram_contexts(records, lang_filter='B')
    obs_avg, obs_per_token, obs_rcs = compute_role_consistency(a_ctx, b_ctx)
    print(f"  Tokens analyzed: {len(obs_per_token)}")
    print(f"  Observed average role_consistency: {obs_avg:.4f}")
    print(f"  Original published value: 0.238 (23.8%)")
    print(f"  Matches original: {abs(obs_avg - 0.238) < 0.05}")

    if obs_per_token:
        sorted_t = sorted(obs_per_token, key=lambda x: -x['role_consistency'])
        print(f"\n  Top-5 highest role_consistency tokens:")
        for t in sorted_t[:5]:
            print(f"    {t['token']:<12} N_b={t['b_n']:<5} rc={t['role_consistency']:.3f}")
        print(f"  Bottom-5 lowest role_consistency tokens:")
        for t in sorted_t[-5:]:
            print(f"    {t['token']:<12} N_b={t['b_n']:<5} rc={t['role_consistency']:.3f}")

    # ---- Within-line shuffle null ----
    print(f"\n--- WITHIN-LINE SHUFFLE NULL ({N_PERM_SHUFFLE} permutations) ---")
    print("  (preserves line membership, line length, per-folio vocab; breaks within-line order)")
    null_within = run_null(records, line_positions, 'within_line', N_PERM_SHUFFLE, 'within-line')

    null_within_mean = sum(null_within) / len(null_within)
    null_within_std = (sum((x - null_within_mean) ** 2 for x in null_within) / len(null_within)) ** 0.5
    z_within = (obs_avg - null_within_mean) / null_within_std if null_within_std > 0 else float('inf')
    print(f"\n  Within-line null mean: {null_within_mean:.4f}, std: {null_within_std:.4f}")
    print(f"  Observed: {obs_avg:.4f}")
    print(f"  z-score: {z_within:+.2f}")
    print(f"  Effect size: observed - null = {obs_avg - null_within_mean:+.4f} ({(obs_avg - null_within_mean) * 100:+.1f}pp)")

    # ---- Fully random shuffle null ----
    print(f"\n--- FULLY RANDOM SHUFFLE NULL ({N_PERM_RANDOM} permutations) ---")
    print("  (preserves vocab frequencies; breaks all positional structure)")
    null_random = run_null(records, line_positions, 'random', N_PERM_RANDOM, 'random')

    null_random_mean = sum(null_random) / len(null_random)
    null_random_std = (sum((x - null_random_mean) ** 2 for x in null_random) / len(null_random)) ** 0.5
    z_random = (obs_avg - null_random_mean) / null_random_std if null_random_std > 0 else float('inf')
    print(f"\n  Random null mean: {null_random_mean:.4f}, std: {null_random_std:.4f}")
    print(f"  Observed: {obs_avg:.4f}")
    print(f"  z-score: {z_random:+.2f}")
    print(f"  Effect size: observed - null = {obs_avg - null_random_mean:+.4f} ({(obs_avg - null_random_mean) * 100:+.1f}pp)")

    # ---- Verdict ----
    print("\n" + "=" * 80)
    print("AUDIT VERDICT")
    print("=" * 80)
    print(f"\n  Observed role_consistency: {obs_avg:.4f} ({obs_avg*100:.1f}%)")
    print(f"  Original C131 value: 0.238 (23.8%)")
    print(f"  Original threshold for 'DSL signal': 0.80 (80%)")
    print(f"\n  vs Within-line shuffle null:")
    print(f"    null mean: {null_within_mean:.4f}, observed-null delta: {(obs_avg - null_within_mean)*100:+.1f}pp")
    print(f"    z = {z_within:+.2f}")
    print(f"\n  vs Random shuffle null:")
    print(f"    null mean: {null_random_mean:.4f}, observed-null delta: {(obs_avg - null_random_mean)*100:+.1f}pp")
    print(f"    z = {z_random:+.2f}")

    if obs_avg < null_within_mean + 2 * null_within_std:
        verdict_within = ("23.8% at within-line noise floor. Below null + 2*std. "
                          "The 'low role consistency' framing is uninformative under "
                          "this null — random within-line shuffles produce comparable values.")
    elif obs_avg > null_within_mean + 2 * null_within_std and obs_avg < null_within_mean + 0.05:
        verdict_within = ("23.8% marginally above within-line null but effect size small "
                          "(< 5pp above null mean). C131's '23.8% LOW' framing is descriptively "
                          "accurate but the discriminating power against null is weak.")
    else:
        verdict_within = ("23.8% above within-line null AND effect size > 5pp. "
                          "C131's framing is well-supported.")

    print(f"\n  WITHIN-LINE NULL VERDICT: {verdict_within}")

    interpretation = (
        "C131 was registered as falsification of DSL/language hypothesis. "
        "The original threshold (>80% = DSL signal) is theoretical, not calibrated "
        "against natural-language baselines. The 23.8% observation is below the "
        "threshold but the null distribution shows what 'low role consistency' "
        "actually means for a structured non-language corpus."
    )

    out = {
        "method": "C131 audit: re-measure role_consistency with proper null calibration",
        "original_methodology": "phases/X_adversarial_audit/phase_x5_discriminator.py:test_symbolic_reuse",
        "original_value": 0.238,
        "original_threshold_for_DSL": 0.80,
        "observed_avg_role_consistency": obs_avg,
        "n_tokens_analyzed": len(obs_per_token),
        "per_token_results": obs_per_token,
        "within_line_null": {
            "n_permutations": N_PERM_SHUFFLE,
            "null_mean": null_within_mean,
            "null_std": null_within_std,
            "z_score": z_within,
            "effect_size_pp": (obs_avg - null_within_mean) * 100,
            "null_distribution": null_within,
        },
        "random_null": {
            "n_permutations": N_PERM_RANDOM,
            "null_mean": null_random_mean,
            "null_std": null_random_std,
            "z_score": z_random,
            "effect_size_pp": (obs_avg - null_random_mean) * 100,
        },
        "verdict": verdict_within,
        "interpretation": interpretation,
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out, indent=2, default=str), encoding='utf-8')
    print(f"\nResults written to {OUT_PATH.relative_to(ROOT)}")


if __name__ == '__main__':
    main()
