"""Does C2023's class-layer sequential structure survive a 5-gram null?

THE LOAD-BEARING TEST. C2023 found I(class; prev_class) = 0.264 vs within-line
shuffle null 0.215 +/- 0.013, z=+3.91 — "the 49-class macro-state automaton is
genuinely sequential." But that's SHUFFLE-null only. Per PHASE_729 doctrine,
shuffle-survivors (C1727, C645+C2045) have failed the sharper 5-gram null. C2023
is the constraint grounding the whole hazard-topology / disfavored-transition
framework at the load-bearing layer. It has never been 5-gram tested.

PRE-REGISTERED (locked before running):

REAL measurement (replicates C2023 T3 exactly): I(class; prev_class) over within-line
adjacent token pairs in Currier B, classes via exact token->class lookup
(class_token_map.json), tokens with middle+suffix non-None.

SANITY: reproduce the shuffle-null z (~+3.91). If I can't reproduce C2023, stop.

5-GRAM NULL: train character 5-gram on Currier B lines; generate N synthetic corpora
matched to real line/token-count structure; project synthetic tokens onto classes via
the SAME token->class map (exact match; unmapped -> dropped, exactly as real drops
unclassified); compute I(class; prev_class) on synthetic adjacent classified pairs.

COVERAGE CONTROL (crazy-expert's flag): the synthetic generates novel strings; report
synth class-coverage (fraction of synth tokens with a class_id) vs real coverage. If
synth coverage << real, the MI comparison is confounded (fewer classified pairs deflates
synth I -> false-positive "survival"). Pre-registered: if |synth_cov - real_cov| > 0.10
absolute, flag and interpret with caution; report a coverage-matched note.

VERDICT (locked):
- real I > 5gram-synth I at z_5gram >= 2.0 AND p_emp < 0.05 AND coverage comparable
    -> C2023 SURVIVES the sharp null. Class-layer sequential structure is genuinely
       above-Markov. The disfavored-transition framework is vindicated at the load-bearing layer.
- real I within 5gram-synth distribution (z_5gram < 2.0)
    -> C2023 DEMOTE candidate. Class-layer structure is Markov-reproducible (parallel to
       C1727). Major finding — propagates to the hazard-topology framework.
- coverage confound (|delta| > 0.10) -> HOLD, redesign with coverage matching.

flush=True + interim JSON writes per discipline.
"""
import json
import math
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path('C:/git/voynich')
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology

N_SHUFFLE = 30
N_SYNTH = 200
ORDER = 5
RESULTS = PROJECT_ROOT / 'phases/PHASE_733_CLASS_LAYER_5GRAM_NULL/results/class_layer_5gram_null.json'


def entropy(counts):
    total = sum(counts.values())
    if total == 0:
        return 0.0
    h = 0.0
    for c in counts.values():
        if c:
            p = c / total
            h -= p * math.log2(p)
    return h


def cond_entropy(joint, marg):
    total = sum(marg.values())
    if total == 0:
        return 0.0
    h = 0.0
    for x, n_x in marg.items():
        h += (n_x / total) * entropy(joint.get(x, {}))
    return h


def MI_from_lines(class_lines):
    """I(class; prev_class) over within-line adjacent pairs. class_lines = list of lists of class_id (None allowed)."""
    h_marg_counts = Counter()
    joint = defaultdict(Counter)
    marg = Counter()
    for line in class_lines:
        clean = [c for c in line if c is not None]
        for c in clean:
            h_marg_counts[c] += 1
        for a, b in zip(clean, clean[1:]):
            joint[a][b] += 1
            marg[a] += 1
    h_marg = entropy(h_marg_counts)
    h_cond = cond_entropy(joint, marg)
    return h_marg - h_cond, sum(marg.values())


def shuffle_null(class_lines, n_shuffles, seed=0):
    rng = random.Random(seed)
    mis = []
    # Pre-extract per-line classified sequences
    seqs = [[c for c in line if c is not None] for line in class_lines]
    for _ in range(n_shuffles):
        shuffled_lines = []
        for s in seqs:
            ss = s[:]
            rng.shuffle(ss)
            shuffled_lines.append(ss)
        mi, _ = MI_from_lines(shuffled_lines)
        mis.append(mi)
    mean = sum(mis) / len(mis)
    sd = (sum((x - mean) ** 2 for x in mis) / len(mis)) ** 0.5 if len(mis) > 1 else 0.0
    return mean, sd


# ===== Load corpus (replicate C2023 collection) =====
print('Loading Currier B tokens (h-only, P-placement, middle+suffix non-None)...', flush=True)
tx = Transcript(); morph = Morphology()
by_line = defaultdict(list)
for tok in tx.all(h_only=True):
    if not tok.word or tok.is_uncertain:
        continue
    if tok.language != 'B':
        continue
    if not (tok.placement and tok.placement.startswith('P')):
        continue
    by_line[(tok.folio, tok.line)].append(tok.word)

# token vocabulary check for middle+suffix filter
def has_ms(w):
    try:
        m = morph.extract(w)
        return m.middle is not None and m.suffix is not None
    except Exception:
        return False

# Build word-lines passing the filter (keep order)
word_lines = []
for key in sorted(by_line.keys()):
    wl = [w for w in by_line[key] if has_ms(w)]
    if wl:
        word_lines.append(wl)
n_tokens = sum(len(l) for l in word_lines)
print(f'  {len(word_lines)} lines, {n_tokens} filtered tokens', flush=True)

# ===== class map =====
cm = json.load(open(PROJECT_ROOT / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'))
ttc = cm['token_to_class']

def to_class_line(wl):
    return [ttc.get(w) for w in wl]

real_class_lines = [to_class_line(wl) for wl in word_lines]
real_classified = sum(1 for line in real_class_lines for c in line if c is not None)
real_cov = real_classified / n_tokens
print(f'  Real class-coverage: {real_classified}/{n_tokens} = {real_cov:.3f}', flush=True)

# ===== REAL measurement + shuffle sanity =====
print('\n=== REAL measurement (replicate C2023 T3) ===', flush=True)
real_mi, n_pairs = MI_from_lines(real_class_lines)
sh_mean, sh_sd = shuffle_null(real_class_lines, N_SHUFFLE)
z_shuffle = (real_mi - sh_mean) / sh_sd if sh_sd > 0 else float('nan')
print(f'  Real I(class;prev) = {real_mi:.4f} (n_pairs={n_pairs})', flush=True)
print(f'  Shuffle null = {sh_mean:.4f} +/- {sh_sd:.4f}', flush=True)
print(f'  z_shuffle = {z_shuffle:+.2f}  (C2023 reported +3.91)', flush=True)
sanity_ok = abs(z_shuffle - 3.91) < 2.0 or z_shuffle > 2.0
print(f'  SANITY (reproduces C2023 above-shuffle structure): {sanity_ok}', flush=True)

interim = {
    'n_lines': len(word_lines), 'n_tokens': n_tokens,
    'real_coverage': real_cov, 'real_classified': real_classified,
    'real_mi': real_mi, 'n_pairs': n_pairs,
    'shuffle_null_mean': sh_mean, 'shuffle_null_sd': sh_sd, 'z_shuffle': z_shuffle,
    'sanity_ok': bool(sanity_ok),
    'status': 'real_done_5gram_pending',
}
RESULTS.write_text(json.dumps(interim, indent=2))
print(f'  [interim written]', flush=True)

# ===== 5-GRAM training + generation =====
print(f'\n=== Training {ORDER}-gram on Currier B lines ===', flush=True)
def train_ngram(lines, order):
    counts = defaultdict(Counter)
    for wl in lines:
        s = ' '.join(wl)
        padded = '\x01' * (order - 1) + s + '\x02'
        for i in range(order - 1, len(padded)):
            counts[padded[i-(order-1):i]][padded[i]] += 1
    return counts

def sample_line(counts, order, target_n, rng):
    out = []; ctx = '\x01' * (order - 1); buf = []; attempts = 0
    while len(out) < target_n and attempts < target_n * 60:
        attempts += 1
        cand = counts.get(ctx)
        if not cand:
            ctx = '\x01' * (order - 1); continue
        ch = rng.choices(list(cand.keys()), weights=list(cand.values()), k=1)[0]
        if ch == '\x02':
            if buf: out.append(''.join(buf)); buf = []
            ctx = '\x01' * (order - 1)
            if len(out) >= target_n: break
            continue
        if ch == ' ':
            if buf: out.append(''.join(buf)); buf = []
            ctx = (ctx + ch)[-(order-1):]; continue
        buf.append(ch); ctx = (ctx + ch)[-(order-1):]
    if buf and len(out) < target_n: out.append(''.join(buf))
    return out[:target_n]

counts = train_ngram(word_lines, ORDER)
print(f'  {len(counts)} contexts', flush=True)

print(f'\n=== 5-gram null ({N_SYNTH} synthetic corpora) ===', flush=True)
rng = random.Random(42)
synth_mis = []
synth_covs = []
for s in range(N_SYNTH):
    synth_lines = [sample_line(counts, ORDER, len(wl), rng) for wl in word_lines]
    synth_class_lines = [to_class_line(wl) for wl in synth_lines]
    synth_tok = sum(len(l) for l in synth_lines)
    synth_classified = sum(1 for line in synth_class_lines for c in line if c is not None)
    synth_covs.append(synth_classified / synth_tok if synth_tok else 0)
    mi, _ = MI_from_lines(synth_class_lines)
    synth_mis.append(mi)
    if (s + 1) % 25 == 0:
        cur_mean = sum(synth_mis)/len(synth_mis)
        print(f'  [{s+1}/{N_SYNTH}] synth I mean so far = {cur_mean:.4f}, cov mean = {sum(synth_covs)/len(synth_covs):.3f}', flush=True)
        interim['synth_progress'] = s + 1
        interim['synth_mi_mean_sofar'] = cur_mean
        RESULTS.write_text(json.dumps(interim, indent=2))

synth_mean = sum(synth_mis) / len(synth_mis)
synth_sd = (sum((x - synth_mean) ** 2 for x in synth_mis) / len(synth_mis)) ** 0.5
z_5gram = (real_mi - synth_mean) / synth_sd if synth_sd > 0 else float('nan')
p_emp = sum(1 for m in synth_mis if m >= real_mi) / len(synth_mis)
synth_cov_mean = sum(synth_covs) / len(synth_covs)
cov_delta = abs(synth_cov_mean - real_cov)

print(f'\n=== RESULT ===', flush=True)
print(f'  Real I(class;prev)   = {real_mi:.4f}', flush=True)
print(f'  Shuffle null         = {sh_mean:.4f} +/- {sh_sd:.4f}  (z={z_shuffle:+.2f})', flush=True)
print(f'  5-gram synth I        = {synth_mean:.4f} +/- {synth_sd:.4f}', flush=True)
print(f'  z_5gram              = {z_5gram:+.2f}', flush=True)
print(f'  p_emp (synth >= real) = {p_emp:.4f}', flush=True)
print(f'  Real coverage = {real_cov:.3f}, synth coverage = {synth_cov_mean:.3f}, delta = {cov_delta:.3f}', flush=True)

coverage_confound = cov_delta > 0.10
print(f'\n=== VERDICT ===', flush=True)
if coverage_confound:
    print(f'  COVERAGE CONFOUND (delta={cov_delta:.3f} > 0.10) — HOLD, interpret with caution.', flush=True)
if z_5gram >= 2.0 and p_emp < 0.05:
    print(f'  C2023 SURVIVES the 5-gram null. Class-layer sequential structure is above-Markov.', flush=True)
    print(f'  The disfavored-transition framework is vindicated at the load-bearing layer.', flush=True)
    verdict = 'SURVIVES'
else:
    print(f'  C2023 DEMOTE CANDIDATE. Class-layer structure is 5-gram-reproducible (parallel to C1727).', flush=True)
    print(f'  Major finding — propagates to the hazard-topology framework.', flush=True)
    verdict = 'DEMOTE_CANDIDATE'
if coverage_confound:
    verdict += '_BUT_COVERAGE_CONFOUNDED'

interim.update({
    'synth_mi_mean': synth_mean, 'synth_mi_sd': synth_sd,
    'z_5gram': z_5gram, 'p_emp_synth_ge_real': p_emp,
    'synth_coverage_mean': synth_cov_mean, 'coverage_delta': cov_delta,
    'coverage_confound': bool(coverage_confound),
    'verdict': verdict, 'status': 'complete', 'n_synth': N_SYNTH,
})
RESULTS.write_text(json.dumps(interim, indent=2))
print(f'\nWritten to {RESULTS}', flush=True)
