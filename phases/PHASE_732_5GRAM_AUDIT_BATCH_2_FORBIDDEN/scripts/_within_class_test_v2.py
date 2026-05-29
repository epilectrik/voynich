"""Within-class anomaly test v2 — CORRECTED to use direct token->49-class lookup.

The Phase 18 forbidden pairs are FULL TOKENS from the frequent-token graph
(shey, chey, chedy are tokens, not MIDDLE strings). v1 wrongly looked up via
MIDDLE decomposition. v2 uses token_to_class directly.

QUESTION: For each forbidden pair (src_token -> tgt_token), do the OTHER tokens
in class(src_token) also avoid tgt_token? If classmates freely transition to
tgt while src=0, src is anomalous (miscategorization OR token-specific prohibition).
If classmates also avoid tgt, the prohibition is class-wide and src is correctly placed.

Counting test, flush=True per discipline.
"""
import sys
import json
from collections import defaultdict, Counter
from pathlib import Path

sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Transcript

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
ttc = cm['token_to_class']                 # token -> class id
ctt = {str(k): v for k, v in cm['class_to_tokens'].items()}   # class id -> [tokens]

tx = Transcript()
lines_dict = defaultdict(list)
for t in tx.currier_b(exclude_labels=True, exclude_uncertain=True):
    w = t.word.strip()
    if not w or '*' in w: continue
    lines_dict[(t.folio, t.line)].append(w)
lines = list(lines_dict.values())
print(f'  {len(lines)} B lines.', flush=True)


def token_bigram(src, tgt):
    total = match = 0
    for line in lines:
        for i in range(len(line) - 1):
            if line[i] == src:
                total += 1
                if line[i+1] == tgt: match += 1
    return match, total


def classmates_to_target(src, tgt):
    cls = ttc.get(src)
    if cls is None:
        return None
    classmates = [t for t in ctt.get(str(cls), []) if t != src]
    cm_set = set(classmates)
    total = match = 0
    per_mate = {}
    for line in lines:
        for i in range(len(line) - 1):
            if line[i] in cm_set:
                total += 1
                hit = (line[i+1] == tgt)
                if hit: match += 1
                pm = per_mate.setdefault(line[i], [0, 0])
                pm[1] += 1
                if hit: pm[0] += 1
    return {
        'class': cls,
        'n_classmates': len(classmates),
        'classmate_total_transitions': total,
        'classmate_to_tgt_count': match,
        'classmate_to_tgt_rate': match / total if total else None,
        'n_classmates_hit': sum(1 for v in per_mate.values() if v[0] > 0),
        'n_classmates_observed': len(per_mate),
        'top_hitters': sorted([(k, v[0], v[1]) for k, v in per_mate.items() if v[0] > 0],
                              key=lambda x: -x[1])[:5],
    }


print('\n' + '=' * 100, flush=True)
print('WITHIN-CLASS ANOMALY TEST v2 (direct token->49-class)', flush=True)
print('=' * 100, flush=True)
print(f'{"#":>3} {"src":>7} {"tgt":>7} {"s_cls":>6} {"t_cls":>6} {"src->tgt":>9} '
      f'{"mate_rate":>10} {"mates_hit":>10} {"verdict":>17}', flush=True)
print('-' * 100, flush=True)

results = []
for n, hcls, src, tgt in FORBIDDEN:
    s_cls = ttc.get(src, 'none')
    t_cls = ttc.get(tgt, 'none')
    s_match, s_total = token_bigram(src, tgt)
    cmi = classmates_to_target(src, tgt)

    if s_cls == 'none':
        verdict = 'SRC_NOT_IN_49CLASS'
    elif cmi is None or cmi['classmate_total_transitions'] == 0:
        verdict = 'NO_CLASSMATE_DATA'
    else:
        rate = cmi['classmate_to_tgt_rate']
        hit = cmi['n_classmates_hit']
        if rate is not None and rate < 0.005 and hit == 0:
            verdict = 'CLASS_WIDE_AVOID'
        elif hit >= 1 and rate is not None and rate >= 0.01:
            verdict = 'SRC_ANOMALOUS'
        else:
            verdict = 'WEAK_MIXED'

    rate_str = f'{cmi["classmate_to_tgt_rate"]:.4f}' if cmi and cmi['classmate_to_tgt_rate'] is not None else 'n/a'
    hit_str = f'{cmi["n_classmates_hit"]}/{cmi["n_classmates_observed"]}' if cmi else 'n/a'
    print(f'{n:>3} {src:>7} {tgt:>7} {str(s_cls):>6} {str(t_cls):>6} {str(s_match)+"/"+str(s_total):>9} '
          f'{rate_str:>10} {hit_str:>10} {verdict:>17}', flush=True)
    results.append({
        'pair': n, 'hazard_class': hcls, 'src': src, 'tgt': tgt,
        'src_class': s_cls, 'tgt_class': t_cls,
        'src_to_tgt_count': s_match, 'src_to_tgt_total': s_total,
        'classmate_info': cmi, 'verdict': verdict,
    })

print('\n=== AGGREGATE ===', flush=True)
vc = Counter(r['verdict'] for r in results)
for v, c in vc.most_common():
    print(f'  {v}: {c}', flush=True)

# Show the SRC_ANOMALOUS cases in detail
print('\n=== SRC_ANOMALOUS detail (classmates that DO transition to forbidden target) ===', flush=True)
for r in results:
    if r['verdict'] == 'SRC_ANOMALOUS':
        cmi = r['classmate_info']
        print(f'  Pair {r["pair"]}: {r["src"]}(cls {r["src_class"]}) -> {r["tgt"]} is 0/{r["src_to_tgt_total"]}, '
              f'but classmates -> {r["tgt"]} at {cmi["classmate_to_tgt_rate"]:.4f} '
              f'({cmi["n_classmates_hit"]}/{cmi["n_classmates_observed"]} classmates hit)', flush=True)
        print(f'    Top hitters (token, hits, total): {cmi["top_hitters"]}', flush=True)

out = Path('phases/PHASE_732_5GRAM_AUDIT_BATCH_2_FORBIDDEN/results/within_class_anomaly_v2.json')
out.write_text(json.dumps(results, indent=2))
print(f'\nWritten to {out}', flush=True)
