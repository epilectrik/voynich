"""Test 7: C645+C2045 post-hazard CHSH recovery against 5-gram null.

Real Voynich Currier B:
  Post-hazard CHSH rate = 75.2% (504 events) vs baseline 55.3%
  +19.9 pp above baseline; passed within-folio shuffle null at p<0.001

Test: train 5-gram on Voynich, generate synthetic with matched line structure,
identify hazards (tokens in classes 7/30), measure post-hazard CHSH rate
on synthetic. Compare residual.

If synthetic shows ~75% post-hazard CHSH: Markov-trivial.
If synthetic shows ~55% (=baseline): C2045 SURVIVES.
"""
import json
import random
import sys
from collections import defaultdict, Counter
from pathlib import Path

sys.path.insert(0, 'C:/git/voynich')
random.seed(42)

from scripts.voynich import Transcript, Morphology

ROOT = Path('C:/git/voynich')
morph = Morphology()
tx = Transcript()

# Load class/subfamily mappings
with open(ROOT / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json') as f:
    ctm = json.load(f)
token_to_class = {t: int(c) for t, c in ctm['token_to_class'].items()}

with open(ROOT / 'phases/EN_ANATOMY/results/en_census.json') as f:
    en_census = json.load(f)
qo_classes = set(en_census['prefix_families']['QO'])
chsh_classes = set(en_census['prefix_families']['CH_SH'])
all_en_classes = qo_classes | chsh_classes

HAZ_CLASSES = {7, 30}


def classify(word):
    """Return ('haz', 'en_qo', 'en_chsh', None)."""
    cls = token_to_class.get(word)
    if cls is None:
        # Token not in class map — classify by prefix as fallback
        try:
            m = morph.extract(word)
            if m.prefix == 'qo':
                return ('en_qo', None)
            if m.prefix in ('ch', 'sh'):
                return ('en_chsh', None)
        except Exception:
            pass
        return (None, None)
    is_haz = cls in HAZ_CLASSES
    en_type = None
    try:
        m = morph.extract(word)
        if cls in all_en_classes:
            if m.prefix == 'qo':
                en_type = 'en_qo'
            elif m.prefix in ('ch', 'sh'):
                en_type = 'en_chsh'
    except Exception:
        pass
    return (en_type, is_haz)


def post_hazard_chsh_rate(lines):
    """Returns (rate, total_post_haz_en, chsh_count)."""
    chsh, qo, total = 0, 0, 0
    for words in lines:
        classified = [classify(w) for w in words]
        for i, (_, is_haz) in enumerate(classified):
            if not is_haz:
                continue
            for j in range(i + 1, len(classified)):
                en_type = classified[j][0]
                if en_type == 'en_chsh':
                    chsh += 1
                    total += 1
                    break
                elif en_type == 'en_qo':
                    qo += 1
                    total += 1
                    break
    rate = chsh / total if total else 0
    return rate, total, chsh


def baseline_chsh_rate(lines):
    """Fraction of all EN tokens that are CHSH (the null/baseline rate)."""
    chsh, qo = 0, 0
    for words in lines:
        for w in words:
            en_type, _ = classify(w)
            if en_type == 'en_chsh':
                chsh += 1
            elif en_type == 'en_qo':
                qo += 1
    total = chsh + qo
    return chsh / total if total else 0


# ----------- 1. Real Currier B baseline -----------
lines_dict = defaultdict(list)
for t in tx.currier_b(exclude_labels=True, exclude_uncertain=True):
    w = t.word.strip()
    if not w:
        continue
    lines_dict[(t.folio, t.line)].append(w)
real_lines = list(lines_dict.values())
print(f'Real Currier B: {len(real_lines)} lines')

real_base = baseline_chsh_rate(real_lines)
real_rate, real_total, real_chsh = post_hazard_chsh_rate(real_lines)
print(f'\n--- Real Currier B ---')
print(f'  Baseline CHSH/(CHSH+QO) rate: {real_base:.3f}')
print(f'  Post-hazard CHSH rate: {real_rate:.3f} ({real_chsh}/{real_total})')
print(f'  Enrichment above baseline: {(real_rate - real_base) * 100:+.1f} pp')

# ----------- 2. Train 5-gram, generate synthetic -----------
def train_ngram(line_lists, order):
    counts = defaultdict(Counter)
    for words in line_lists:
        s = ' '.join(words)
        padded = '\x01' * (order - 1) + s + '\x02'
        for i in range(order - 1, len(padded)):
            ctx = padded[i - (order - 1):i]
            counts[ctx][padded[i]] += 1
    return counts


def sample_line(counts, order, target_n):
    out = []; ctx = '\x01' * (order - 1); buf = []; attempts = 0
    while len(out) < target_n and attempts < target_n * 30:
        attempts += 1
        cand = counts.get(ctx)
        if not cand:
            ctx = '\x01' * (order - 1); continue
        chars = list(cand.keys()); weights = list(cand.values())
        ch = random.choices(chars, weights=weights, k=1)[0]
        if ch == '\x02':
            if buf:
                out.append(''.join(buf)); buf = []
            break
        if ch == ' ':
            if buf:
                out.append(''.join(buf)); buf = []
            ctx = (ctx + ch)[-(order - 1):] if order > 1 else ''
            continue
        buf.append(ch); ctx = (ctx + ch)[-(order - 1):] if order > 1 else ''
    if buf and len(out) < target_n:
        out.append(''.join(buf))
    return out[:target_n]


print('\nTraining 5-gram...')
ngram = train_ngram(real_lines, 5)
print('Generating synthetic Currier B with matched line lengths...')
synth_lines = [sample_line(ngram, 5, len(w)) for w in real_lines]
print(f'Generated {len(synth_lines)} synthetic lines')

# ----------- 3. Same metric on synthetic -----------
syn_base = baseline_chsh_rate(synth_lines)
syn_rate, syn_total, syn_chsh = post_hazard_chsh_rate(synth_lines)
print(f'\n--- Synthetic 5-gram ---')
print(f'  Baseline CHSH/(CHSH+QO) rate: {syn_base:.3f}')
print(f'  Post-hazard CHSH rate: {syn_rate:.3f} ({syn_chsh}/{syn_total})')
print(f'  Enrichment above baseline: {(syn_rate - syn_base) * 100:+.1f} pp')

# ----------- 4. Verdict -----------
real_enrich_pp = (real_rate - real_base) * 100
syn_enrich_pp = (syn_rate - syn_base) * 100
residual = real_enrich_pp - syn_enrich_pp

print('\n=== VERDICT ===')
print(f'Real enrichment above baseline:  {real_enrich_pp:+.1f} pp')
print(f'Synth enrichment above baseline: {syn_enrich_pp:+.1f} pp')
print(f'Residual signal beyond Markov:   {residual:+.1f} pp')

if residual > 10:
    print('  --> C645+C2045 hazard recovery SURVIVES Markov null. Real signal.')
elif residual > 3:
    print('  --> C645+C2045 PARTIALLY survives. Moderate residual.')
elif abs(residual) < 3:
    print('  --> C645+C2045 is Markov-reproducible. Effect emerges from local stats.')
else:
    print(f'  --> Anomalous: synthetic shows MORE post-hazard CHSH than real.')
