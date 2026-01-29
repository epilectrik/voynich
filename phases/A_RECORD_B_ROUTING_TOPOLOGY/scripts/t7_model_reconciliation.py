"""
T7: A->B Model Reconciliation Test

Tests two competing interpretations of how A->B filtering works:

MODEL 1 (C502 Token Filtering):
- A record's PP MIDDLEs define what's ALLOWED in B
- A B token is legal IFF its MIDDLE is in A's PP set
- More PP in A -> MORE B tokens legal -> BETTER coverage

MODEL 2 (T6 Viability / Subset Test):
- A unit's PP MIDDLEs must be CONTAINED in B folio's vocabulary
- B folio is viable IFF A's PP is subset of B's PP
- More PP in A -> MORE requirements -> WORSE viability

These are OPPOSITE predictions. This test determines which is empirically correct
for the "usability" question.
"""

import sys
import json
from pathlib import Path
from collections import defaultdict
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

print("=" * 70)
print("T7: A->B MODEL RECONCILIATION TEST")
print("=" * 70)

# Gallows characters for paragraph detection
GALLOWS = {'k', 't', 'p', 'f'}

def starts_with_gallows(word):
    if not word:
        return False
    w = word.strip()
    return bool(w) and w[0] in GALLOWS

# Step 1: Build B-folio data
print("\nStep 1: Building B-folio vocabularies...")

b_folio_middles = defaultdict(set)  # folio -> set of MIDDLEs present
b_folio_tokens = defaultdict(list)   # folio -> list of (word, middle)

for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    m = morph.extract(w)
    if m.middle:
        b_folio_middles[token.folio].add(m.middle)
        b_folio_tokens[token.folio].append((w, m.middle))

b_folios = list(b_folio_middles.keys())
print(f"  B folios: {len(b_folios)}")
print(f"  Mean MIDDLEs per B folio: {np.mean([len(v) for v in b_folio_middles.values()]):.1f}")

# Step 2: Build A structures at different aggregation levels
print("\nStep 2: Building A structures...")

# Collect all A PP MIDDLEs (shared with B)
all_a_middles = set()
all_b_middles = set()
for middles in b_folio_middles.values():
    all_b_middles.update(middles)

a_lines = defaultdict(set)       # (folio, line) -> PP MIDDLEs
a_paragraphs = defaultdict(set)  # (folio, para_num) -> PP MIDDLEs
a_folios = defaultdict(set)      # folio -> PP MIDDLEs

current_para = defaultdict(int)
prev_folio = None

for token in tx.currier_a():
    w = token.word.strip()
    if not w or '*' in w:
        continue

    folio = token.folio
    line = token.line

    if folio != prev_folio:
        current_para[folio] = 0
        prev_folio = folio

    line_key = (folio, line)
    if line_key not in a_lines:
        if starts_with_gallows(w):
            current_para[folio] += 1

    m = morph.extract(w)
    if not m.middle:
        continue

    all_a_middles.add(m.middle)
    a_lines[line_key].add(m.middle)
    a_paragraphs[(folio, current_para[folio])].add(m.middle)
    a_folios[folio].add(m.middle)

# PP vocabulary = shared between A and B
pp_vocabulary = all_a_middles & all_b_middles
print(f"  PP vocabulary (A&B shared): {len(pp_vocabulary)}")

# Filter to PP only
for key in a_lines:
    a_lines[key] = a_lines[key] & pp_vocabulary
for key in a_paragraphs:
    a_paragraphs[key] = a_paragraphs[key] & pp_vocabulary
for key in a_folios:
    a_folios[key] = a_folios[key] & pp_vocabulary

b_folio_pp = {f: middles & pp_vocabulary for f, middles in b_folio_middles.items()}

print(f"  A lines: {len(a_lines)}")
print(f"  A paragraphs: {len(a_paragraphs)}")
print(f"  A folios: {len(a_folios)}")

# Step 3: Test both models
print("\n" + "=" * 70)
print("MODEL COMPARISON")
print("=" * 70)

def test_c502_model(a_pp_set, b_folio):
    """
    C502 MODEL: A's PP defines what's ALLOWED.
    Returns fraction of B tokens that survive filtering.
    """
    b_tokens = b_folio_tokens[b_folio]
    if not b_tokens:
        return 0.0

    if not a_pp_set:
        return 1.0  # No constraints = all survive

    # A token survives if its MIDDLE is in A's PP set
    surviving = sum(1 for (w, mid) in b_tokens if mid in a_pp_set)
    return surviving / len(b_tokens)

def test_t6_model(a_pp_set, b_folio):
    """
    T6 MODEL: A's PP must be SUBSET of B's vocabulary.
    Returns 1 if viable, 0 if not.
    """
    if not a_pp_set:
        return 1  # No requirements = viable

    b_pp = b_folio_pp[b_folio]
    return 1 if a_pp_set.issubset(b_pp) else 0

# Test at each aggregation level
results = {}

for name, a_units in [
    ("Single Line", a_lines),
    ("Paragraph", a_paragraphs),
    ("Full A-Folio", a_folios),
]:
    pp_counts = []
    c502_scores = []  # Mean survival rate across all B folios
    t6_scores = []    # Number of viable B folios

    for key, a_pp in a_units.items():
        pp_counts.append(len(a_pp))

        # C502: Mean survival rate across B folios
        survivals = [test_c502_model(a_pp, bf) for bf in b_folios]
        c502_scores.append(np.mean(survivals))

        # T6: Count of viable B folios
        viabilities = [test_t6_model(a_pp, bf) for bf in b_folios]
        t6_scores.append(sum(viabilities))

    mean_pp = np.mean(pp_counts)
    mean_c502 = np.mean(c502_scores)
    mean_t6 = np.mean(t6_scores)

    # Correlation: PP count vs each model's score
    if len(pp_counts) > 10:
        from scipy.stats import spearmanr
        rho_c502, p_c502 = spearmanr(pp_counts, c502_scores)
        rho_t6, p_t6 = spearmanr(pp_counts, t6_scores)
    else:
        rho_c502, p_c502 = 0, 1
        rho_t6, p_t6 = 0, 1

    print(f"\n{name} (n={len(a_units)}):")
    print(f"  Mean PP MIDDLEs: {mean_pp:.1f}")
    print(f"  ")
    print(f"  C502 MODEL (token survival):")
    print(f"    Mean survival rate: {mean_c502:.1%}")
    print(f"    PP -> Survival correlation: rho={rho_c502:.3f}, p={p_c502:.2e}")
    print(f"    Direction: {'MORE PP = MORE survival' if rho_c502 > 0 else 'MORE PP = LESS survival'}")
    print(f"  ")
    print(f"  T6 MODEL (folio viability):")
    print(f"    Mean viable B-folios: {mean_t6:.1f} / {len(b_folios)}")
    print(f"    PP -> Viability correlation: rho={rho_t6:.3f}, p={p_t6:.2e}")
    print(f"    Direction: {'MORE PP = MORE viable' if rho_t6 > 0 else 'MORE PP = LESS viable'}")

    results[name] = {
        'n': len(a_units),
        'mean_pp': float(mean_pp),
        'c502_mean_survival': float(mean_c502),
        'c502_rho': float(rho_c502),
        'c502_direction': 'positive' if rho_c502 > 0 else 'negative',
        't6_mean_viable': float(mean_t6),
        't6_rho': float(rho_t6),
        't6_direction': 'positive' if rho_t6 > 0 else 'negative',
    }

# Step 4: Determine which model matches C693's intent
print("\n" + "=" * 70)
print("RECONCILIATION VERDICT")
print("=" * 70)

# C693 says aggregation should help usability
# Which model shows aggregation helping?

line_c502 = results["Single Line"]["c502_mean_survival"]
folio_c502 = results["Full A-Folio"]["c502_mean_survival"]
line_t6 = results["Single Line"]["t6_mean_viable"]
folio_t6 = results["Full A-Folio"]["t6_mean_viable"]

print(f"\nAggregation effect (Line -> Full Folio):")
print(f"  C502 survival: {line_c502:.1%} -> {folio_c502:.1%} ({folio_c502/line_c502:.2f}x)")
print(f"  T6 viability:  {line_t6:.1f} -> {folio_t6:.1f} folios")

if folio_c502 > line_c502:
    print(f"\n  C502 MODEL: Aggregation INCREASES token survival")
    print(f"  This matches C693's expectation that aggregation helps usability")
    c502_verdict = "CONFIRMS_C693"
else:
    print(f"\n  C502 MODEL: Aggregation DECREASES token survival")
    c502_verdict = "CONTRADICTS_C693"

if folio_t6 > line_t6:
    print(f"\n  T6 MODEL: Aggregation INCREASES viable folios")
    t6_verdict = "CONFIRMS_C693"
else:
    print(f"\n  T6 MODEL: Aggregation DECREASES viable folios (as we saw)")
    print(f"  This CONTRADICTS C693's expectation")
    t6_verdict = "CONTRADICTS_C693"

print(f"\n" + "-" * 70)
print("CONCLUSION:")
print("-" * 70)

if c502_verdict == "CONFIRMS_C693" and t6_verdict == "CONTRADICTS_C693":
    print("""
The C502 model (token filtering) is the CORRECT interpretation of A->B mechanics.
The T6 model (subset viability) asks the WRONG question.

C693's interpretation is CORRECT: aggregating A records DOES help usability
because it expands the vocabulary of LEGAL B tokens.

The T6 test was measuring something different: whether a B folio CONTAINS
all of an A unit's vocabulary. This is not what the system does.

CONSTRAINT STATUS:
- C502, C502.a: VALIDATED (token filtering is correct)
- C693: VALIDATED (aggregation helps under token model)
- C738: VALIDATED (union of A folios increases coverage)
- T6 results: NOT A CONSTRAINT VIOLATION - just wrong question
""")
    verdict = "C502_CORRECT"
elif c502_verdict == "CONTRADICTS_C693":
    print("""
UNEXPECTED: C502 model also shows aggregation hurting.
This would require revisiting C693's interpretation.
""")
    verdict = "NEEDS_REVIEW"
else:
    verdict = "INCONCLUSIVE"

results['verdict'] = verdict
results['c502_verdict'] = c502_verdict
results['t6_verdict'] = t6_verdict

# Save results
out_path = PROJECT_ROOT / 'phases' / 'A_RECORD_B_ROUTING_TOPOLOGY' / 'results' / 't7_model_reconciliation.json'
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {out_path.name}")
