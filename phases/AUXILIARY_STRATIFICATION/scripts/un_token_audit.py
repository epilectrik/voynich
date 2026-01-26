"""
Q6: UN Token Audit

Resolve the mystery of ~7042 tokens not in class_token_map.
Determine: are they valid B tokens, hapax, uncertain readings, or edge cases?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

import json
from pathlib import Path
from collections import defaultdict, Counter
from scripts.voynich import Transcript, Morphology

# Paths
BASE = Path('C:/git/voynich')
CLASS_MAP = BASE / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'
RESULTS = BASE / 'phases/AUXILIARY_STRATIFICATION/results'

# Load data
tx = Transcript()
b_tokens = list(tx.currier_b())

with open(CLASS_MAP) as f:
    class_data = json.load(f)

token_to_class = {tok: int(cls) for tok, cls in class_data['token_to_class'].items()}
morph = Morphology()

print("=" * 70)
print("Q6: UN TOKEN AUDIT")
print("=" * 70)

# ============================================================
# 1. IDENTIFY UNMATCHED TOKENS
# ============================================================
print("\n" + "-" * 70)
print("1. TOKEN MATCHING STATUS")
print("-" * 70)

matched = []
unmatched = []
empty_count = 0
asterisk_count = 0

for token in b_tokens:
    raw_word = token.word
    word = raw_word.replace('*', '').strip()

    if not word:
        empty_count += 1
        continue

    if '*' in raw_word:
        asterisk_count += 1

    if word in token_to_class:
        matched.append(token)
    else:
        unmatched.append(token)

total = len(b_tokens)
print(f"\nTotal B tokens (H-track): {total}")
print(f"Empty tokens: {empty_count}")
print(f"Asterisk tokens (uncertain): {asterisk_count}")
print(f"Matched to class: {len(matched)} ({len(matched)/total*100:.1f}%)")
print(f"Unmatched (UN): {len(unmatched)} ({len(unmatched)/total*100:.1f}%)")

# ============================================================
# 2. UN TOKEN FREQUENCY DISTRIBUTION
# ============================================================
print("\n" + "-" * 70)
print("2. UN TOKEN FREQUENCY DISTRIBUTION")
print("-" * 70)

un_word_counts = Counter()
for token in unmatched:
    word = token.word.replace('*', '').strip()
    un_word_counts[word] += 1

unique_un = len(un_word_counts)
hapax_un = sum(1 for w, c in un_word_counts.items() if c == 1)
dis_un = sum(1 for w, c in un_word_counts.items() if c == 2)

print(f"\nUnique UN types: {unique_un}")
print(f"Hapax legomena (count=1): {hapax_un} ({hapax_un/unique_un*100:.1f}% of types)")
print(f"Dis legomena (count=2): {dis_un} ({dis_un/unique_un*100:.1f}% of types)")

# Show most frequent UN tokens
print(f"\nTop 30 most frequent UN tokens:")
print(f"{'Token':<20} {'Count':>5} {'Has *':>6}")
for word, count in un_word_counts.most_common(30):
    has_star = any('*' in t.word for t in unmatched if t.word.replace('*', '').strip() == word)
    print(f"  {word:<20} {count:>5} {'yes' if has_star else 'no':>6}")

# ============================================================
# 3. UNCERTAIN (*) ANALYSIS
# ============================================================
print("\n" + "-" * 70)
print("3. UNCERTAIN READING ANALYSIS")
print("-" * 70)

un_uncertain = sum(1 for t in unmatched if '*' in t.word)
un_clean = len(unmatched) - un_uncertain

print(f"\nUN tokens with asterisk: {un_uncertain} ({un_uncertain/len(unmatched)*100:.1f}%)")
print(f"UN tokens without asterisk: {un_clean} ({un_clean/len(unmatched)*100:.1f}%)")

# Check if clean unmatched tokens are in the matched set when asterisk-stripped
matched_words = set(token_to_class.keys())
clean_un_words = set()
for t in unmatched:
    word = t.word.replace('*', '').strip()
    if '*' not in t.word:
        clean_un_words.add(word)

print(f"\nUnique clean UN types: {len(clean_un_words)}")

# ============================================================
# 4. MORPHOLOGICAL ANALYSIS OF UN TOKENS
# ============================================================
print("\n" + "-" * 70)
print("4. MORPHOLOGICAL ANALYSIS OF UN TOKENS")
print("-" * 70)

prefix_dist = Counter()
middle_dist = Counter()
suffix_dist = Counter()
artic_count = 0
un_sample = set()

for word in un_word_counts:
    m = morph.extract(word)
    prefix_dist[m.prefix or 'NONE'] += un_word_counts[word]
    middle_dist[m.middle or 'NONE'] += un_word_counts[word]
    suffix_dist[m.suffix or 'NONE'] += un_word_counts[word]
    if m.has_articulator:
        artic_count += un_word_counts[word]
    un_sample.add(word)

total_un = sum(un_word_counts.values())
print(f"\nArticulator usage: {artic_count} ({artic_count/total_un*100:.1f}%)")
print(f"\nTop 10 prefixes:")
for prefix, count in prefix_dist.most_common(10):
    print(f"  {prefix:<10} {count:>5} ({count/total_un*100:.1f}%)")

print(f"\nTop 10 middles:")
for middle, count in middle_dist.most_common(10):
    print(f"  {middle:<10} {count:>5} ({count/total_un*100:.1f}%)")

print(f"\nTop 10 suffixes:")
for suffix, count in suffix_dist.most_common(10):
    print(f"  {suffix:<10} {count:>5} ({count/total_un*100:.1f}%)")

# ============================================================
# 5. NEAREST CLASS ANALYSIS
# ============================================================
print("\n" + "-" * 70)
print("5. NEAREST CLASS BY PREFIX")
print("-" * 70)

# For top UN tokens, find what class they'd belong to based on prefix similarity
# Build prefix->class mapping from known tokens
prefix_class_dist = defaultdict(lambda: Counter())
for tok, cls in token_to_class.items():
    m = morph.extract(tok)
    if m.prefix:
        prefix_class_dist[m.prefix][cls] += 1

print(f"\nFor frequent UN tokens, predicted class by prefix:")
print(f"{'Token':<20} {'Prefix':>8} {'Predicted Class':>15} {'Confidence'}")
for word, count in un_word_counts.most_common(20):
    m = morph.extract(word)
    prefix = m.prefix or 'NONE'
    if prefix in prefix_class_dist:
        top_cls = prefix_class_dist[prefix].most_common(1)[0]
        total_prefix = sum(prefix_class_dist[prefix].values())
        conf = top_cls[1] / total_prefix
        print(f"  {word:<20} {prefix:>8} {top_cls[0]:>15} {conf:.0%} (n={total_prefix})")
    else:
        print(f"  {word:<20} {prefix:>8} {'???':>15} no prefix data")

# ============================================================
# 6. FOLIO/SECTION DISTRIBUTION
# ============================================================
print("\n" + "-" * 70)
print("6. UN TOKEN DISTRIBUTION BY FOLIO")
print("-" * 70)

un_by_folio = Counter()
total_by_folio = Counter()
for token in b_tokens:
    word = token.word.replace('*', '').strip()
    if not word:
        continue
    total_by_folio[token.folio] += 1
    if word not in token_to_class:
        un_by_folio[token.folio] += 1

# Top folios by UN rate
folio_un_rates = {}
for folio in total_by_folio:
    rate = un_by_folio[folio] / total_by_folio[folio]
    folio_un_rates[folio] = rate

print(f"\nTop 10 folios by UN rate:")
for folio, rate in sorted(folio_un_rates.items(), key=lambda x: -x[1])[:10]:
    print(f"  {folio:<10} {un_by_folio[folio]:>4}/{total_by_folio[folio]:>4} = {rate:.1%}")

print(f"\nBottom 10 folios by UN rate:")
for folio, rate in sorted(folio_un_rates.items(), key=lambda x: x[1])[:10]:
    print(f"  {folio:<10} {un_by_folio[folio]:>4}/{total_by_folio[folio]:>4} = {rate:.1%}")

mean_rate = len(unmatched) / total
print(f"\nOverall UN rate: {mean_rate:.1%}")

# ============================================================
# 7. COSURVIVAL TEST METHODOLOGY CHECK
# ============================================================
print("\n" + "-" * 70)
print("7. METHODOLOGY: WHY ARE THESE TOKENS UNCLASSIFIED?")
print("-" * 70)

# The cosurvival test requires tokens to appear in multiple folios
# Hapax tokens that appear in only 1 folio can't be tested for co-survival
folio_per_un_type = defaultdict(set)
for token in unmatched:
    word = token.word.replace('*', '').strip()
    folio_per_un_type[word].add(token.folio)

single_folio = sum(1 for folios in folio_per_un_type.values() if len(folios) == 1)
multi_folio = sum(1 for folios in folio_per_un_type.values() if len(folios) > 1)

print(f"\nUN types appearing in 1 folio only: {single_folio} ({single_folio/unique_un*100:.1f}%)")
print(f"UN types appearing in 2+ folios: {multi_folio} ({multi_folio/unique_un*100:.1f}%)")

folio_dist = Counter(len(folios) for folios in folio_per_un_type.values())
print(f"\nFolio spread distribution:")
for n_folios in sorted(folio_dist.keys())[:10]:
    print(f"  {n_folios} folio(s): {folio_dist[n_folios]} types")

# Check: matched tokens' folio spread for comparison
matched_folio_spread = defaultdict(set)
for token in matched:
    word = token.word.replace('*', '').strip()
    matched_folio_spread[word].add(token.folio)

matched_single = sum(1 for folios in matched_folio_spread.values() if len(folios) == 1)
print(f"\nFor comparison - matched types in 1 folio only: {matched_single} ({matched_single/len(matched_folio_spread)*100:.1f}%)")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print(f"""
UN Token Resolution:
- {len(unmatched)} tokens ({len(unmatched)/total*100:.1f}%) are not in class_token_map
- {unique_un} unique types
- {hapax_un} are hapax legomena ({hapax_un/unique_un*100:.1f}% of UN types)
- {single_folio} appear in only 1 folio ({single_folio/unique_un*100:.1f}%)
- {un_uncertain} have uncertain readings (asterisk) ({un_uncertain/len(unmatched)*100:.1f}%)

PRIMARY CAUSE: Tokens too rare for cosurvival test (single-folio hapax)
SECONDARY CAUSE: Uncertain readings
TERTIARY: Edge cases (empty, unusual forms)

These are NOT a separate role. They are valid B tokens that lacked
sufficient distributional data for class assignment.
""")

# Save results
results = {
    'total_b_tokens': total,
    'matched': len(matched),
    'unmatched': len(unmatched),
    'un_pct': round(len(unmatched)/total*100, 1),
    'unique_un_types': unique_un,
    'hapax_un': hapax_un,
    'single_folio_un': single_folio,
    'uncertain_un': un_uncertain,
    'top_un_tokens': [
        {'word': w, 'count': c}
        for w, c in un_word_counts.most_common(50)
    ],
    'morphology': {
        'top_prefixes': [{'prefix': p, 'count': c} for p, c in prefix_dist.most_common(10)],
        'top_middles': [{'middle': m, 'count': c} for m, c in middle_dist.most_common(10)],
        'articulator_rate': round(artic_count/total_un*100, 1) if total_un > 0 else 0,
    },
    'folio_spread': {
        'single_folio_types': single_folio,
        'multi_folio_types': multi_folio,
    }
}

with open(RESULTS / 'un_audit.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)

print(f"Results saved to {RESULTS / 'un_audit.json'}")
