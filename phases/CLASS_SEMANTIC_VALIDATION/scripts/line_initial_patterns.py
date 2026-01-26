"""
Q14: Line-Initial Role Patterns

Which roles prefer line-initial position? This extends C543 (Role Positional Grammar)
with systematic analysis of initial position preferences.
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

import json
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy import stats
from scripts.voynich import Transcript

# Paths
BASE = Path('C:/git/voynich')
CLASS_MAP = BASE / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'
RESULTS = BASE / 'phases/CLASS_SEMANTIC_VALIDATION/results'

# Load transcript
tx = Transcript()
tokens = list(tx.currier_b())

with open(CLASS_MAP) as f:
    class_data = json.load(f)

token_to_class = {tok: int(cls) for tok, cls in class_data['token_to_class'].items()}

# Role mapping
ROLE_MAP = {
    10: 'CC', 11: 'CC', 17: 'CC',
    8: 'EN', 31: 'EN', 32: 'EN', 33: 'EN', 34: 'EN', 36: 'EN',
    7: 'FL', 30: 'FL', 38: 'FL', 40: 'FL',
    9: 'FQ', 20: 'FQ', 21: 'FQ', 23: 'FQ',
}

ROLE_NAMES = {
    'CC': 'CORE_CONTROL',
    'EN': 'ENERGY',
    'FL': 'FLOW',
    'FQ': 'FREQUENT',
    'AX': 'AUXILIARY',
    'UN': 'UNCLASSIFIED'
}

def get_role(cls):
    if cls is None:
        return 'UN'
    return ROLE_MAP.get(cls, 'AX')

print("=" * 70)
print("Q14: LINE-INITIAL ROLE PATTERNS")
print("=" * 70)

# Group tokens by line
lines = defaultdict(list)
for token in tokens:
    word = token.word.replace('*', '').strip()
    folio = token.folio
    line = token.line
    cls = token_to_class.get(word)
    role = get_role(cls)
    lines[(folio, line)].append({'word': word, 'class': cls, 'role': role})

print(f"\nTotal lines: {len(lines)}")

# 1. ROLE AT LINE-INITIAL POSITION
print("\n" + "-" * 70)
print("1. LINE-INITIAL ROLE DISTRIBUTION")
print("-" * 70)

initial_roles = defaultdict(int)
all_roles = defaultdict(int)

for (folio, line), word_data in lines.items():
    if not word_data:
        continue

    # Count initial role
    initial_role = word_data[0]['role']
    initial_roles[initial_role] += 1

    # Count all roles
    for wd in word_data:
        all_roles[wd['role']] += 1

total_lines = len(lines)
total_tokens = sum(all_roles.values())

print("\n| Role | Initial | Initial% | Corpus% | Enrichment |")
print("|------|---------|----------|---------|------------|")

roles = ['CC', 'EN', 'FL', 'FQ', 'AX', 'UN']
initial_enrichments = {}

for role in roles:
    initial = initial_roles[role]
    initial_pct = initial / total_lines * 100
    corpus_pct = all_roles[role] / total_tokens * 100
    enrichment = initial_pct / corpus_pct if corpus_pct > 0 else 0
    initial_enrichments[role] = enrichment

    marker = "+" if enrichment > 1.3 else ("-" if enrichment < 0.7 else "")
    print(f"| {ROLE_NAMES[role]:15s} | {initial:7d} | {initial_pct:7.1f}% | {corpus_pct:6.1f}% | {enrichment:.2f}x{marker}      |")

# 2. CLASS-LEVEL INITIAL PATTERNS
print("\n" + "-" * 70)
print("2. LINE-INITIAL CLASS DISTRIBUTION")
print("-" * 70)

initial_classes = defaultdict(int)
all_classes = defaultdict(int)

for (folio, line), word_data in lines.items():
    if not word_data:
        continue

    initial_cls = word_data[0]['class']
    if initial_cls is not None:
        initial_classes[initial_cls] += 1

    for wd in word_data:
        if wd['class'] is not None:
            all_classes[wd['class']] += 1

print("\nTop 10 line-initial classes:")
print("| Class | Role | Initial | Initial% | Corpus% | Enrichment |")
print("|-------|------|---------|----------|---------|------------|")

class_enrichments = []
for cls in all_classes:
    initial = initial_classes[cls]
    corpus = all_classes[cls]
    initial_pct = initial / total_lines * 100
    corpus_pct = corpus / total_tokens * 100
    enrichment = initial_pct / corpus_pct if corpus_pct > 0 else 0

    if corpus >= 50:  # Filter for meaningful classes
        class_enrichments.append({
            'class': cls,
            'role': get_role(cls),
            'initial': initial,
            'initial_pct': initial_pct,
            'corpus_pct': corpus_pct,
            'enrichment': enrichment
        })

# Sort by enrichment
class_enrichments.sort(key=lambda x: x['enrichment'], reverse=True)
for e in class_enrichments[:10]:
    marker = "+" if e['enrichment'] > 1.5 else ""
    print(f"| {e['class']:5d} | {e['role']}   | {e['initial']:7d} | {e['initial_pct']:7.1f}% | {e['corpus_pct']:6.1f}% | {e['enrichment']:.2f}x{marker}      |")

print("\nBottom 10 line-initial classes (most initial-depleted):")
print("| Class | Role | Initial | Initial% | Corpus% | Enrichment |")
print("|-------|------|---------|----------|---------|------------|")
for e in class_enrichments[-10:]:
    marker = "-" if e['enrichment'] < 0.5 else ""
    print(f"| {e['class']:5d} | {e['role']}   | {e['initial']:7d} | {e['initial_pct']:7.1f}% | {e['corpus_pct']:6.1f}% | {e['enrichment']:.2f}x{marker}      |")

# 3. INITIAL TOKENS
print("\n" + "-" * 70)
print("3. MOST COMMON LINE-INITIAL TOKENS")
print("-" * 70)

initial_tokens = defaultdict(int)
for (folio, line), word_data in lines.items():
    if word_data:
        initial_tokens[word_data[0]['word']] += 1

print("\nTop 20 line-initial tokens:")
print("| Token | Count | % of lines | Class | Role |")
print("|-------|-------|------------|-------|------|")
for tok, count in sorted(initial_tokens.items(), key=lambda x: -x[1])[:20]:
    cls = token_to_class.get(tok)
    role = get_role(cls)
    print(f"| {tok:12s} | {count:5d} | {count/total_lines*100:9.1f}% | {cls if cls else 'N/A':>5} | {role}   |")

# 4. LINE-FINAL COMPARISON
print("\n" + "-" * 70)
print("4. LINE-FINAL ROLE DISTRIBUTION (comparison)")
print("-" * 70)

final_roles = defaultdict(int)
for (folio, line), word_data in lines.items():
    if not word_data:
        continue
    final_role = word_data[-1]['role']
    final_roles[final_role] += 1

print("\n| Role | Initial% | Final% | Init Enrich | Final Enrich | Bias |")
print("|------|----------|--------|-------------|--------------|------|")

for role in roles:
    initial_pct = initial_roles[role] / total_lines * 100
    final_pct = final_roles[role] / total_lines * 100
    corpus_pct = all_roles[role] / total_tokens * 100

    init_enrich = initial_pct / corpus_pct if corpus_pct > 0 else 0
    final_enrich = final_pct / corpus_pct if corpus_pct > 0 else 0

    if init_enrich > final_enrich * 1.2:
        bias = "INITIAL"
    elif final_enrich > init_enrich * 1.2:
        bias = "FINAL"
    else:
        bias = "NONE"

    print(f"| {ROLE_NAMES[role]:15s} | {initial_pct:7.1f}% | {final_pct:5.1f}% | {init_enrich:10.2f}x | {final_enrich:11.2f}x | {bias:6s} |")

# 5. STATISTICAL TEST
print("\n" + "-" * 70)
print("5. STATISTICAL TESTS")
print("-" * 70)

# Chi-square test: Is initial role distribution different from corpus?
observed_initial = [initial_roles[r] for r in roles]
expected_initial = [all_roles[r] / total_tokens * total_lines for r in roles]

chi2, p = stats.chisquare(observed_initial, expected_initial)
print(f"\nChi-square (initial vs corpus distribution):")
print(f"  Chi2 = {chi2:.1f}, p = {p:.2e}")
print(f"  {'SIGNIFICANT' if p < 0.001 else 'Not significant'}: Initial positions {'ARE' if p < 0.001 else 'are not'} role-biased")

# 6. INITIAL BIGRAMS
print("\n" + "-" * 70)
print("6. INITIAL ROLE BIGRAMS (first two positions)")
print("-" * 70)

bigrams = defaultdict(int)
for (folio, line), word_data in lines.items():
    if len(word_data) >= 2:
        r1 = word_data[0]['role']
        r2 = word_data[1]['role']
        bigrams[(r1, r2)] += 1

print("\nTop 15 initial bigrams:")
print("| First | Second | Count | % |")
print("|-------|--------|-------|---|")
for (r1, r2), count in sorted(bigrams.items(), key=lambda x: -x[1])[:15]:
    print(f"| {r1:5s} | {r2:6s} | {count:5d} | {count/total_lines*100:4.1f}% |")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

# Identify strongest initial-biased roles
initial_biased = [(r, initial_enrichments[r]) for r in roles if initial_enrichments[r] > 1.3]
final_biased = [(r, final_roles[r]/total_lines / (all_roles[r]/total_tokens)) for r in roles
                if final_roles[r]/total_lines / (all_roles[r]/total_tokens) > 1.3]

print(f"""
1. INITIAL-BIASED ROLES (>1.3x enrichment):
{chr(10).join(f'   - {ROLE_NAMES[r]}: {e:.2f}x' for r, e in initial_biased) if initial_biased else '   None'}

2. FINAL-BIASED ROLES (>1.3x enrichment):
{chr(10).join(f'   - {ROLE_NAMES[r]}: {e:.2f}x' for r, e in final_biased) if final_biased else '   None'}

3. STATISTICAL SIGNIFICANCE:
   - Initial role distribution is {'DIFFERENT' if p < 0.001 else 'similar to'} corpus (p={p:.2e})

4. TOP INITIAL CLASSES:
   - Class {class_enrichments[0]['class']} ({class_enrichments[0]['role']}): {class_enrichments[0]['enrichment']:.2f}x
   - Class {class_enrichments[1]['class']} ({class_enrichments[1]['role']}): {class_enrichments[1]['enrichment']:.2f}x
""")

# Save results
results = {
    'initial_role_enrichments': {ROLE_NAMES[r]: float(initial_enrichments[r]) for r in roles},
    'class_enrichments': class_enrichments[:20],
    'chi2_test': {'chi2': float(chi2), 'p': float(p)},
    'top_initial_tokens': dict(sorted(initial_tokens.items(), key=lambda x: -x[1])[:20])
}

with open(RESULTS / 'line_initial_patterns.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {RESULTS / 'line_initial_patterns.json'}")
