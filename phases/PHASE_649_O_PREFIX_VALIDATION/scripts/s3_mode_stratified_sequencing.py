"""
Phase 649 Step 3: Mode-stratified within-line bigram analysis.

Re-run Test 2 separately for Mode A (specification/terminal-heavy) lines and
Mode B (execution/bare-heavy) lines.

Per C1230/C1231/C1236/C1246:
- Mode A: 43% terminal-suffix, 47% bare; energy + specific measurement coupling
- Mode B: 16% terminal-suffix, 74% bare; sustained / passive monitoring

Predictions:
- Mode A: predicted control-loop topology (qo->o-prefixes, o-prefixes->ch/sh) should appear
- Mode B: channel persistence (self-loops) should dominate

Method:
1. Classify each Currier B line as Mode A or Mode B from suffix profile
2. Re-run bigram enrichment for each mode independently
3. Compare hit rates against the same predictions used in Test 2
"""
import sys
import json
import math
import random
sys.path.insert(0, '.')
from scripts.voynich import Transcript, Morphology
from collections import defaultdict, Counter

tx = Transcript()
morph = Morphology()

# Group tokens by line
lines = defaultdict(list)
for t in tx.currier_b():
    lines[(t.folio, t.line)].append(t)

# Terminal-suffix set (per C1230/C1236)
TERMINAL_SUFFIXES = {'dy', 'edy', 'eedy', 'y', 'ey', 'ody', 'eody'}

def classify_line_mode(toks, threshold=0.30):
    """Classify a line as Mode A or Mode B based on terminal-suffix fraction.

    Per C1231: Mode A terminal=0.430/bare=0.466, Mode B terminal=0.155/bare=0.741.
    Threshold of 0.30 splits the two means roughly at midpoint.
    """
    if len(toks) < 3:
        return None
    n_terminal = 0
    n_with_suffix = 0
    for t in toks:
        m = morph.extract(t.word)
        if m.suffix:
            n_with_suffix += 1
            if m.suffix in TERMINAL_SUFFIXES:
                n_terminal += 1
    if n_with_suffix == 0:
        return None
    terminal_frac = n_terminal / len(toks)  # use total tokens as denominator
    return 'A' if terminal_frac >= threshold else 'B'

# Classify lines
line_modes = {}
for key, toks in lines.items():
    mode = classify_line_mode(toks)
    if mode:
        line_modes[key] = mode

n_a = sum(1 for m in line_modes.values() if m == 'A')
n_b = sum(1 for m in line_modes.values() if m == 'B')
print(f"Total Currier B lines classified: {len(line_modes):,}")
print(f"  Mode A (specification/terminal-heavy): {n_a:,} ({n_a/len(line_modes)*100:.1f}%)")
print(f"  Mode B (execution/bare-heavy):         {n_b:,} ({n_b/len(line_modes)*100:.1f}%)")
print(f"  Reference rate per C1231: ~32% Mode A / ~68% Mode B (across paragraph bodies)")

def prefix_of(w):
    if w.startswith('ch'): return 'ch'
    if w.startswith('sh'): return 'sh'
    if w.startswith('qo'): return 'qo'
    if len(w) >= 2 and w[0] == 'o' and w[1] in ('k','t','l','r'):
        return 'o' + w[1]
    return None

prefixes = ['ch','sh','qo','ok','ot','ol','or']

def build_seqs(mode):
    seqs = []
    for key, toks in lines.items():
        if line_modes.get(key) != mode:
            continue
        seq = [prefix_of(t.word) for t in toks]
        seq_filt = [p for p in seq if p is not None]
        if len(seq_filt) >= 2:
            seqs.append(seq_filt)
    return seqs

def compute_enrichment(seqs):
    observed = Counter()
    marginal = Counter()
    for seq in seqs:
        for p in seq:
            marginal[p] += 1
        for i in range(len(seq) - 1):
            observed[(seq[i], seq[i+1])] += 1
    total = sum(marginal.values())
    enr = {}
    expected = {}
    for p1 in prefixes:
        bg_starting_p1 = sum(observed[(p1, p2_)] for p2_ in prefixes)
        for p2 in prefixes:
            obs = observed[(p1, p2)]
            if marginal[p1] == 0 or marginal[p2] == 0 or bg_starting_p1 == 0:
                enr[(p1, p2)] = None
                continue
            exp = bg_starting_p1 * marginal[p2] / total
            expected[(p1, p2)] = exp
            if exp < 0.5 or obs == 0:
                enr[(p1, p2)] = None
            else:
                enr[(p1, p2)] = math.log2(obs / exp)
    return enr, observed, expected, marginal

PREDICTED_ENRICHED = [
    ('qo','ol'), ('qo','ok'), ('qo','ot'),
    ('ol','ok'), ('ol','ot'),
    ('ok','ch'), ('ot','ch'),
    ('sh','qo'), ('ch','qo'),
]
PREDICTED_SUPPRESSED = [
    ('ch','ch'), ('ch','sh'), ('sh','sh'),
]

def score_predictions(enr, observed, expected):
    h_e = h_s = 0
    enriched_results = []
    suppressed_results = []
    for pair in PREDICTED_ENRICHED:
        e = enr.get(pair)
        ok_pred = (e is not None and e > 0.2)
        if ok_pred: h_e += 1
        enriched_results.append((pair, e, observed.get(pair, 0), expected.get(pair, 0)))
    for pair in PREDICTED_SUPPRESSED:
        e = enr.get(pair)
        ok_pred = (e is not None and e < -0.2)
        if ok_pred: h_s += 1
        suppressed_results.append((pair, e, observed.get(pair, 0), expected.get(pair, 0)))
    return h_e, h_s, enriched_results, suppressed_results

def fmt_e(e):
    return f"{e:+.2f}" if e is not None else '  --'

# Run for each mode
for mode in ('A', 'B'):
    print()
    print("="*72)
    print(f"MODE {mode} — within-line bigram enrichment "
          f"({'specification/terminal' if mode == 'A' else 'execution/bare'})")
    print("="*72)
    seqs = build_seqs(mode)
    n_bigrams = sum(len(s) - 1 for s in seqs)
    print(f"Lines: {len(seqs):,}  Bigrams: {n_bigrams:,}")

    enr, observed, expected, marginal = compute_enrichment(seqs)
    h_e, h_s, enriched, suppressed = score_predictions(enr, observed, expected)

    print()
    print("Full enrichment matrix log2(obs/exp):")
    print("        " + "  ".join(f"{p:>6s}" for p in prefixes))
    for p1 in prefixes:
        row = [f"{p1:>4s}  "]
        for p2 in prefixes:
            row.append(f"{fmt_e(enr.get((p1,p2))):>6s}")
        print("  ".join(row))

    print()
    print("PREDICTED ENRICHED (target: log2 > +0.2):")
    for pair, e, obs, exp in enriched:
        verdict = 'YES' if (e is not None and e > 0.2) else 'no'
        print(f"  {pair[0]:>3s} -> {pair[1]:<3s}  obs={obs:5d}  exp={exp:7.1f}  log2={fmt_e(e):>6s}  {verdict}")
    print(f"  Hits: {h_e}/{len(PREDICTED_ENRICHED)}")

    print()
    print("PREDICTED SUPPRESSED (target: log2 < -0.2):")
    for pair, e, obs, exp in suppressed:
        verdict = 'YES' if (e is not None and e < -0.2) else 'no'
        print(f"  {pair[0]:>3s} -> {pair[1]:<3s}  obs={obs:5d}  exp={exp:7.1f}  log2={fmt_e(e):>6s}  {verdict}")
    print(f"  Hits: {h_s}/{len(PREDICTED_SUPPRESSED)}")

    print(f"\nMODE {mode} TOTAL: {h_e + h_s}/{len(PREDICTED_ENRICHED) + len(PREDICTED_SUPPRESSED)}")

# Direct mode-vs-mode comparison
print()
print("="*72)
print("MODE-VS-MODE DIRECT COMPARISON")
print("="*72)

enr_a, obs_a, exp_a, _ = compute_enrichment(build_seqs('A'))
enr_b, obs_b, exp_b, _ = compute_enrichment(build_seqs('B'))

print(f"\n{'pair':>10s}  {'Mode A':>9s}  {'Mode B':>9s}  {'A-B delta':>10s}  Comment")
all_pairs = list(PREDICTED_ENRICHED) + list(PREDICTED_SUPPRESSED) + [
    ('ot','ot'), ('ol','ol'), ('ok','ok'), ('or','or')]
for pair in all_pairs:
    ea = enr_a.get(pair)
    eb = enr_b.get(pair)
    delta = (ea - eb) if (ea is not None and eb is not None) else None
    delta_str = f"{delta:+.2f}" if delta is not None else "  --"
    comment = ''
    if pair in PREDICTED_ENRICHED:
        comment = 'predicted ENR'
    elif pair in PREDICTED_SUPPRESSED:
        comment = 'predicted SUP'
    elif pair[0] == pair[1]:
        comment = 'self-loop'
    print(f"  {pair[0]} -> {pair[1]:<2s}  {fmt_e(ea):>9s}  {fmt_e(eb):>9s}  {delta_str:>10s}  {comment}")

# Save
out = {
    'mode_classification': {'n_a': n_a, 'n_b': n_b, 'n_total': len(line_modes)},
    'mode_a_enrichment': {f'{p1}->{p2}': enr_a.get((p1,p2))
                          for p1 in prefixes for p2 in prefixes},
    'mode_b_enrichment': {f'{p1}->{p2}': enr_b.get((p1,p2))
                          for p1 in prefixes for p2 in prefixes},
}
with open('phases/PHASE_649_O_PREFIX_VALIDATION/results/mode_stratified.json', 'w') as f:
    json.dump(out, f, indent=2, default=str)
