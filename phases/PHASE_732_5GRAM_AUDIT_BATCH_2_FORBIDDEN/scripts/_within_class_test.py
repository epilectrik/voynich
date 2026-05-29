"""Within-class anomaly test for the 17 forbidden-pair source tokens.

QUESTION (user-posed 2026-05-28): The 17 forbidden pairs are 0% at MIDDLE level
but ~65-73% compliance (26.5% violation) when expanded to 84 class-level pairs.
Does the leakiness mean the forbidden-pair SOURCE token is anomalous within its
49-instruction-class (a possible miscategorization signal), or is the prohibition
genuinely token-specific (C627 "token-specific lookup table") with the class
correctly grouping tokens by a different axis?

TEST: For each forbidden pair (src_middle -> tgt_middle):
  1. Find src_middle's 49-instruction-class.
  2. Find all OTHER MIDDLEs in that class (classmates).
  3. Measure: do the classmates also avoid tgt_middle, or do they transition to it freely?

INTERPRETATION:
  - Classmates ALSO avoid tgt (low classmate->tgt rate) => prohibition is class-wide;
    src correctly categorized; class-level disfavoring is real.
  - Classmates FREELY transition to tgt (high classmate->tgt rate) while src=0 =>
    src is anomalous within class => EITHER miscategorization OR token-specific
    prohibition (C627). Distinguish by checking if src is anomalous on OTHER axes too.

This is a counting test (no synthetic generation). Uses flush=True per discipline.
"""
import sys
import json
from collections import defaultdict, Counter
from pathlib import Path

sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Transcript, Morphology

FORBIDDEN = [
    (1, 'PHASE_ORDERING', 'shey', 'aiin'),
    (2, 'PHASE_ORDERING', 'shey', 'al'),
    (3, 'PHASE_ORDERING', 'shey', 'c'),
    (4, 'PHASE_ORDERING', 'dy', 'aiin'),
    (5, 'PHASE_ORDERING', 'dy', 'chey'),
    (6, 'PHASE_ORDERING', 'chey', 'chedy'),
    (7, 'PHASE_ORDERING', 'chey', 'shedy'),
    (8, 'COMPOSITION_JUMP', 'chedy', 'ee'),
    (9, 'COMPOSITION_JUMP', 'c', 'ee'),
    (10, 'COMPOSITION_JUMP', 'shedy', 'aiin'),
    (11, 'COMPOSITION_JUMP', 'shedy', 'o'),
    (12, 'CONTAINMENT_TIMING', 'chol', 'r'),
    (13, 'CONTAINMENT_TIMING', 'l', 'chol'),
    (14, 'CONTAINMENT_TIMING', 'or', 'dal'),
    (15, 'CONTAINMENT_TIMING', 'he', 'or'),
    (16, 'RATE_MISMATCH', 'ar', 'dal'),
    (17, 'ENERGY_OVERSHOOT', 'he', 't'),
]

print('Loading class map + corpus...', flush=True)
cm = json.load(open('phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'))
token_to_class = cm['token_to_class']
class_to_tokens = cm['class_to_tokens']
token_to_middle = cm['token_to_middle']

# Build MIDDLE -> set of classes (a MIDDLE can map to multiple full-tokens in multiple classes)
middle_to_classes = defaultdict(set)
for tok, cls in token_to_class.items():
    mid = token_to_middle.get(tok)
    if mid:
        middle_to_classes[mid].add(cls)

# Build class -> set of MIDDLEs
class_to_middles = defaultdict(set)
for tok, cls in token_to_class.items():
    mid = token_to_middle.get(tok)
    if mid:
        class_to_middles[str(cls)].add(mid)

# Load Currier B lines (MIDDLE sequences per line)
tx = Transcript(); morph = Morphology()
lines_mid = []
for_count_token = Counter()
lines_dict = defaultdict(list)
for t in tx.currier_b(exclude_labels=True, exclude_uncertain=True):
    w = t.word.strip()
    if not w or '*' in w: continue
    lines_dict[(t.folio, t.line)].append(w)
lines = list(lines_dict.values())

# Convert each line to MIDDLE sequence
def to_middle(w):
    try:
        return morph.extract(w).middle
    except Exception:
        return None

mid_lines = []
for line in lines:
    mid_lines.append([to_middle(w) for w in line])

print(f'  {len(lines)} B lines loaded.', flush=True)


def middle_bigram_rate(src_mid, tgt_mid):
    """Within-line rate: P(next MIDDLE == tgt | current MIDDLE == src)."""
    total = 0; match = 0
    for ml in mid_lines:
        for i in range(len(ml) - 1):
            if ml[i] == src_mid:
                total += 1
                if ml[i+1] == tgt_mid:
                    match += 1
    return match, total


def classmates_to_target_rate(src_mid, tgt_mid):
    """For all OTHER MIDDLEs sharing src_mid's class(es), aggregate their -> tgt rate."""
    src_classes = middle_to_classes.get(src_mid, set())
    if not src_classes:
        return None
    classmate_mids = set()
    for cls in src_classes:
        classmate_mids |= class_to_middles.get(str(cls), set())
    classmate_mids.discard(src_mid)
    total = 0; match = 0
    per_mate = {}
    for ml in mid_lines:
        for i in range(len(ml) - 1):
            if ml[i] in classmate_mids:
                total += 1
                hit = (ml[i+1] == tgt_mid)
                if hit: match += 1
                pm = per_mate.setdefault(ml[i], [0, 0])
                pm[1] += 1
                if hit: pm[0] += 1
    return {
        'src_classes': sorted(src_classes),
        'n_classmate_middles': len(classmate_mids),
        'classmate_total_transitions': total,
        'classmate_to_tgt_count': match,
        'classmate_to_tgt_rate': match / total if total else None,
        'n_classmates_that_hit_tgt': sum(1 for v in per_mate.values() if v[0] > 0),
        'n_classmates_observed': len(per_mate),
    }


print('\n' + '=' * 95, flush=True)
print('WITHIN-CLASS ANOMALY TEST', flush=True)
print('=' * 95, flush=True)
print(f'{"#":>3} {"src":>8} {"tgt":>8} {"src_cls":>20} {"src->tgt":>9} {"mates->tgt":>11} {"#mates_hit":>11} {"verdict":>16}', flush=True)
print('-' * 95, flush=True)

results = []
for n, hcls, src, tgt in FORBIDDEN:
    src_classes = middle_to_classes.get(src, set())
    src_match, src_total = middle_bigram_rate(src, tgt)
    src_rate = src_match / src_total if src_total else None
    cm_info = classmates_to_target_rate(src, tgt)

    # Verdict logic
    if not src_classes:
        verdict = 'SRC_NO_CLASS'
    elif cm_info is None or cm_info['classmate_total_transitions'] == 0:
        verdict = 'NO_CLASSMATE_DATA'
    else:
        mate_rate = cm_info['classmate_to_tgt_rate']
        mates_hit = cm_info['n_classmates_that_hit_tgt']
        if mate_rate is not None and mate_rate < 0.005 and mates_hit == 0:
            verdict = 'CLASS_WIDE_AVOID'   # classmates also avoid -> not anomalous
        elif mates_hit >= 1 and mate_rate is not None and mate_rate >= 0.01:
            verdict = 'SRC_ANOMALOUS'      # classmates transition freely, src=0
        else:
            verdict = 'WEAK_MIXED'
    cls_str = ','.join(str(c) for c in sorted(src_classes)) if src_classes else 'none'
    mate_rate_str = f'{cm_info["classmate_to_tgt_rate"]:.4f}' if cm_info and cm_info['classmate_to_tgt_rate'] is not None else 'n/a'
    mates_hit_str = f'{cm_info["n_classmates_that_hit_tgt"]}/{cm_info["n_classmates_observed"]}' if cm_info else 'n/a'
    print(f'{n:>3} {src:>8} {tgt:>8} {cls_str:>20} {str(src_match)+"/"+str(src_total):>9} '
          f'{mate_rate_str:>11} {mates_hit_str:>11} {verdict:>16}', flush=True)
    results.append({
        'pair': n, 'hazard_class': hcls, 'src': src, 'tgt': tgt,
        'src_classes': sorted(src_classes),
        'src_to_tgt_count': src_match, 'src_to_tgt_total': src_total, 'src_to_tgt_rate': src_rate,
        'classmate_info': cm_info, 'verdict': verdict,
    })

print('\n=== AGGREGATE ===', flush=True)
vc = Counter(r['verdict'] for r in results)
for v, c in vc.most_common():
    print(f'  {v}: {c}', flush=True)

print('\nINTERPRETATION:', flush=True)
print('  CLASS_WIDE_AVOID  = classmates also avoid target => src correctly categorized, prohibition class-wide', flush=True)
print('  SRC_ANOMALOUS     = classmates transition to target freely while src=0 => src behaves unlike classmates', flush=True)
print('                      (either miscategorization OR token-specific prohibition per C627)', flush=True)
print('  WEAK_MIXED        = intermediate', flush=True)

out = Path('phases/PHASE_732_5GRAM_AUDIT_BATCH_2_FORBIDDEN/results/within_class_anomaly.json')
out.write_text(json.dumps(results, indent=2))
print(f'\nWritten to {out}', flush=True)
