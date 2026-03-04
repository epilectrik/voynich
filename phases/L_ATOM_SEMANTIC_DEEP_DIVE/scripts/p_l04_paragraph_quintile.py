"""P-L4: l-atom tokens should front-load within paragraphs.

If l = "arrange/lay", staging operations should concentrate in early
paragraph positions (quintile 0) vs late positions (quintile 4).
Prediction: enrichment ratio >= 1.5x, surviving section control.
"""

import json
import math
import sys
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scripts.voynich import Transcript, Morphology

PROJECT = Path(__file__).resolve().parent


def normal_cdf(z):
    if z < -8: return 0.0
    if z > 8: return 1.0
    a1, a2, a3, a4, a5 = 0.254829592, -0.284496736, 1.421413741, -1.453152027, 1.061405429
    p = 0.3275911
    sign = 1 if z >= 0 else -1
    t = 1.0 / (1.0 + p * abs(z))
    y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * math.exp(-z * z / 2.0)
    return 0.5 * (1.0 + sign * y)


tx = Transcript()
morph = Morphology()

# Load section data
with open(PROJECT / 'phases' / 'AXM_RESIDUAL_DECOMPOSITION' / 'results' /
          'axm_residual_decomposition.json', encoding='utf-8') as f:
    axm_data = json.load(f)
folio_section = {f: d['section'] for f, d in axm_data['folio_data'].items()}

# ============================================================
# Build paragraph structure from transcript
# ============================================================
# A paragraph = tokens between gallows-initial lines (C357)
# We need to identify paragraph boundaries and assign quintiles

# First, collect all B tokens with their folio, line, position
lines_by_folio = defaultdict(lambda: defaultdict(list))
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    lines_by_folio[token.folio][token.line].append(w)

# Gallows characters that mark paragraph starts
GALLOWS = {'t', 'k', 'p', 'f'}

def is_gallows_initial(words):
    """Check if first word starts with a gallows character."""
    if not words:
        return False
    first = words[0]
    m = morph.extract(first)
    # Check if the word starts with a gallows (prefix or middle initial)
    if first and first[0] in GALLOWS:
        return True
    if m.prefix and m.prefix[0] in GALLOWS:
        return True
    if not m.prefix and m.middle and m.middle[0] in GALLOWS:
        return True
    return False

# Build paragraphs per folio
# Paragraph = sequence of lines starting with a gallows-initial line
all_paragraphs = []  # list of (folio, section, [words_in_order])

for folio in sorted(lines_by_folio.keys()):
    sec = folio_section.get(folio)
    if not sec:
        continue
    line_keys = sorted(lines_by_folio[folio].keys())

    current_para = []
    for lk in line_keys:
        words = lines_by_folio[folio][lk]
        if is_gallows_initial(words) and current_para:
            # Save previous paragraph
            all_paragraphs.append((folio, sec, current_para))
            current_para = list(words)
        else:
            current_para.extend(words)
    if current_para:
        all_paragraphs.append((folio, sec, current_para))

print(f"Total paragraphs: {len(all_paragraphs)}")
print(f"Paragraphs by section: {Counter(p[1] for p in all_paragraphs)}")

# Filter to paragraphs with >= 10 tokens (enough for quintile analysis)
paras = [(f, s, ws) for f, s, ws in all_paragraphs if len(ws) >= 10]
print(f"Paragraphs with >=10 tokens: {len(paras)}")

# ============================================================
# P-L4: l-atom fraction by paragraph quintile
# ============================================================
print(f"\n{'='*70}")
print("P-L4: l-ATOM FRACTION BY PARAGRAPH BODY QUINTILE")
print(f"{'='*70}")
print("Prediction: Q0 (first 20%) enriched over Q4 (last 20%) at >= 1.5x\n")

# Skip first token (gallows-initial = paragraph header) and use body only
quintile_l = defaultdict(int)
quintile_total = defaultdict(int)

# Also per-section
sec_quintile_l = defaultdict(lambda: defaultdict(int))
sec_quintile_total = defaultdict(lambda: defaultdict(int))

for folio, sec, words in paras:
    # Body = all tokens after first (the gallows-initial token is the header)
    body = words[1:] if len(words) > 1 else words
    n = len(body)
    if n < 5:
        continue

    for i, w in enumerate(body):
        q = int(i / n * 5)  # quintile 0-4
        if q > 4:
            q = 4
        mid = morph.extract(w).middle
        if not mid:
            continue

        quintile_total[q] += 1
        sec_quintile_total[sec][q] += 1

        if 'l' in mid:
            quintile_l[q] += 1
            sec_quintile_l[sec][q] += 1

# Overall quintile results
global_l_frac = sum(quintile_l.values()) / sum(quintile_total.values())
print(f"  {'Quintile':<10s} {'l-atom':>8s} {'total':>8s} {'fraction':>10s} {'enrichment':>12s}")
print(f"  {'-'*10} {'-'*8} {'-'*8} {'-'*10} {'-'*12}")
for q in range(5):
    lc = quintile_l[q]
    tc = quintile_total[q]
    frac = lc / tc if tc > 0 else 0
    enrich = frac / global_l_frac if global_l_frac > 0 else 0
    label = f"Q{q} ({'first' if q == 0 else 'last' if q == 4 else 'mid'})"
    print(f"  {label:<10s} {lc:>8d} {tc:>8d} {frac:>10.4f} {enrich:>11.3f}x")

q0_frac = quintile_l[0] / quintile_total[0] if quintile_total[0] > 0 else 0
q4_frac = quintile_l[4] / quintile_total[4] if quintile_total[4] > 0 else 0
q0q4_ratio = q0_frac / q4_frac if q4_frac > 0 else float('inf')

# Chi-square Q0 vs Q4
a_val = quintile_l[0]
b_val = quintile_total[0] - quintile_l[0]
c_val = quintile_l[4]
d_val = quintile_total[4] - quintile_l[4]
n = a_val + b_val + c_val + d_val
denom = (a_val + b_val) * (c_val + d_val) * (a_val + c_val) * (b_val + d_val)
chi2 = (n * (a_val * d_val - b_val * c_val) ** 2) / denom if denom > 0 else 0
z_val = math.sqrt(chi2)
p_val = 2 * (1 - normal_cdf(z_val))

print(f"\n  Q0 vs Q4: {q0_frac:.4f} vs {q4_frac:.4f}")
print(f"  Q0/Q4 ratio: {q0q4_ratio:.3f}x")
print(f"  Chi-square: {chi2:.2f}, p={p_val:.6f}")

# ============================================================
# Within-section control
# ============================================================
print(f"\n{'='*70}")
print("WITHIN-SECTION: l-atom Q0/Q4 ratio")
print(f"{'='*70}")

for sec in sorted(set(s for _, s, _ in paras)):
    q0l = sec_quintile_l[sec][0]
    q0t = sec_quintile_total[sec][0]
    q4l = sec_quintile_l[sec][4]
    q4t = sec_quintile_total[sec][4]
    if q0t < 10 or q4t < 10:
        continue
    q0f = q0l / q0t if q0t > 0 else 0
    q4f = q4l / q4t if q4t > 0 else 0
    ratio = q0f / q4f if q4f > 0 else float('inf')
    print(f"  {sec}: Q0={q0f:.4f} Q4={q4f:.4f} ratio={ratio:.3f}x (Q0 n={q0t}, Q4 n={q4t})")

# ============================================================
# Comprehensive: ALL atoms by quintile (who front-loads?)
# ============================================================
print(f"\n{'='*70}")
print("ALL ATOMS: Q0/Q4 ENRICHMENT RANKING")
print(f"{'='*70}")
print("(Which atoms front-load in paragraphs?)\n")

all_atoms = 'a d e h k o n i m y c p f s t r l q'.split()
atom_quintile = defaultdict(lambda: defaultdict(int))

for folio, sec, words in paras:
    body = words[1:] if len(words) > 1 else words
    n_body = len(body)
    if n_body < 5:
        continue
    for i, w in enumerate(body):
        q = int(i / n_body * 5)
        if q > 4:
            q = 4
        mid = morph.extract(w).middle
        if not mid:
            continue
        for atom in set(mid):
            if atom in 'adehkonimycpfstrlq':
                atom_quintile[atom][q] += 1

print(f"  {'Atom':<5s} {'Q0':>8s} {'Q4':>8s} {'Q0/Q4':>8s} {'gradient':>10s}")
print(f"  {'-'*5} {'-'*8} {'-'*8} {'-'*8} {'-'*10}")

atom_ratios = []
for atom in all_atoms:
    q0 = atom_quintile[atom][0]
    q4 = atom_quintile[atom][4]
    q0_total = quintile_total[0]
    q4_total = quintile_total[4]
    q0f = q0 / q0_total if q0_total > 0 else 0
    q4f = q4 / q4_total if q4_total > 0 else 0
    ratio = q0f / q4f if q4f > 0 else 0
    atom_ratios.append((atom, q0f, q4f, ratio))

atom_ratios.sort(key=lambda x: -x[3])
for atom, q0f, q4f, ratio in atom_ratios:
    direction = 'FRONT' if ratio > 1.1 else 'BACK' if ratio < 0.9 else 'FLAT'
    marker = ' <-- l' if atom == 'l' else ''
    print(f"  {atom:<5s} {q0f:>8.4f} {q4f:>8.4f} {ratio:>7.3f}x {direction:>10s}{marker}")

# ============================================================
# BONUS: l-atom by line position within paragraph
# ============================================================
print(f"\n{'='*70}")
print("BONUS: l-ATOM FRACTION BY LINE NUMBER WITHIN PARAGRAPH")
print(f"{'='*70}")

line_l = defaultdict(int)
line_total = defaultdict(int)

for folio, sec, words in all_paragraphs:
    # Re-collect with line structure preserved
    pass

# Use a different approach: directly track by line index within paragraph
line_in_para_l = defaultdict(int)
line_in_para_total = defaultdict(int)

for folio in sorted(lines_by_folio.keys()):
    sec = folio_section.get(folio)
    if not sec:
        continue
    line_keys = sorted(lines_by_folio[folio].keys())

    para_line_idx = 0
    for lk in line_keys:
        words = lines_by_folio[folio][lk]
        if is_gallows_initial(words) and para_line_idx > 0:
            para_line_idx = 0  # reset for new paragraph

        for w in words:
            mid = morph.extract(w).middle
            if not mid:
                continue
            # Cap at line 6+ to avoid sparse bins
            line_bin = min(para_line_idx, 6)
            line_in_para_total[line_bin] += 1
            if 'l' in mid:
                line_in_para_l[line_bin] += 1

        para_line_idx += 1

global_l_rate = sum(line_in_para_l.values()) / sum(line_in_para_total.values())
print(f"\n  {'Line':>6s} {'l-atom':>8s} {'total':>8s} {'fraction':>10s} {'enrichment':>12s}")
print(f"  {'-'*6} {'-'*8} {'-'*8} {'-'*10} {'-'*12}")
for line in sorted(line_in_para_total.keys()):
    lc = line_in_para_l[line]
    tc = line_in_para_total[line]
    frac = lc / tc if tc > 0 else 0
    enrich = frac / global_l_rate if global_l_rate > 0 else 0
    label = f"L{line}{'+'if line == 6 else ''}"
    print(f"  {label:>6s} {lc:>8d} {tc:>8d} {frac:>10.4f} {enrich:>11.3f}x")

# ============================================================
# SUMMARY
# ============================================================
print(f"\n{'='*70}")
print("P-L4 SUMMARY")
print(f"{'='*70}")
print(f"\n  l-atom Q0 fraction: {q0_frac:.4f}")
print(f"  l-atom Q4 fraction: {q4_frac:.4f}")
print(f"  Q0/Q4 ratio: {q0q4_ratio:.3f}x")
print(f"  Predicted: >= 1.500x")
print(f"  Chi-square: {chi2:.2f}, p={p_val:.6f}")

if q0q4_ratio >= 1.5 and p_val < 0.05:
    print(f"  RESULT: CONFIRMED (Q0/Q4={q0q4_ratio:.3f}x >= 1.5x, p={p_val:.6f})")
elif q0q4_ratio > 1.0 and p_val < 0.05:
    print(f"  RESULT: SIGNIFICANT but below 1.5x threshold (Q0/Q4={q0q4_ratio:.3f}x)")
elif q0q4_ratio > 1.0:
    print(f"  RESULT: DIRECTIONALLY CORRECT but not significant (p={p_val:.6f})")
else:
    print(f"  RESULT: FAILED (Q0/Q4={q0q4_ratio:.3f}x)")
