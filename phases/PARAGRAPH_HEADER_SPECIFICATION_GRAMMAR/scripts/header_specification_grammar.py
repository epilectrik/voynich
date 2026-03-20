"""
Phase 614: Paragraph Header Specification Grammar
Tests whether paragraph headers function as structured specification registers
with internal positional grammar, and how header content relates to body
composition beyond gallows type.

Produces: header_specification_results.json
"""
import sys; sys.path.insert(0, '.')
import json
import numpy as np
from scipy import stats
from numpy.linalg import lstsq
from collections import Counter, defaultdict
from itertools import combinations
from scripts.voynich import Transcript, BFolioDecoder, Morphology

tx = Transcript()
decoder = BFolioDecoder()
morph = Morphology()

folio_sections = {}
for tok in tx.currier_b():
    if tok.folio not in folio_sections:
        folio_sections[tok.folio] = tok.section

SECTION_MAP = {'S': 'Stars', 'B': 'Bio', 'H': 'Herbal', 'T': 'Cosmo', 'C': 'Cosmo'}
GALLOWS_SET = set('ktpf')
ATOMS = list('kethpfocda')

# ============================================================
# Section 1: Data loading and extraction
# ============================================================

def atom_fracs_from_tokens(token_list):
    atoms = []
    for w in token_list:
        m = morph.extract(w)
        if m.middle:
            for c in m.middle:
                if c in ATOMS:
                    atoms.append(c)
    if len(atoms) < 3:
        return None
    counts = Counter(atoms)
    total = sum(counts.values())
    return np.array([counts.get(a, 0) / total for a in ATOMS])

def cosine_sim(a, b):
    dot = np.dot(a, b)
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0
    return dot / (na * nb)

records = []
all_lines = []
all_paras = []

for fid in sorted(folio_sections.keys()):
    sec = SECTION_MAP.get(folio_sections[fid], folio_sections[fid])
    paras = decoder.analyze_folio_paragraphs(fid)
    for pi, p in enumerate(paras):
        bt = p.boundary_token
        gallows_initial = bt and bt[0] in GALLOWS_SET

        # Collect all lines/paras for uniqueness tests
        para_tokens_all = []
        for li, line in enumerate(p.lines):
            toks = [t.word.strip() for t in line.tokens if t.word.strip() and '*' not in t.word]
            if toks:
                all_lines.append({
                    'folio': fid, 'para_idx': pi, 'line_idx': li,
                    'line_str': ' '.join(toks), 'n_tokens': len(toks),
                })
                para_tokens_all.extend(toks)
        if para_tokens_all:
            all_paras.append({
                'folio': fid, 'para_idx': pi,
                'para_str': ' '.join(para_tokens_all),
            })

        if not gallows_initial or len(p.lines) < 2:
            continue

        hdr_all = [t.word.strip() for t in p.lines[0].tokens if t.word.strip() and '*' not in t.word]
        if len(hdr_all) < 2:
            continue

        bt_word = hdr_all[0]
        hdr_non_bt = hdr_all[1:]

        body_toks = []
        for li in range(1, len(p.lines)):
            for tok in p.lines[li].tokens:
                w = tok.word.strip()
                if w and '*' not in w:
                    body_toks.append(w)

        body_fracs = atom_fracs_from_tokens(body_toks)
        if body_fracs is None:
            continue

        bt_fracs = atom_fracs_from_tokens([bt_word])
        hdr_fracs = atom_fracs_from_tokens(hdr_non_bt)

        bt_atoms_set = set()
        m_bt = morph.extract(bt_word)
        if m_bt.middle:
            bt_atoms_set = set(c for c in m_bt.middle if c in ATOMS)

        pos_fracs = {}
        for pos_i, w in enumerate(hdr_non_bt[:8]):
            pf = atom_fracs_from_tokens([w])
            if pf is not None:
                pos_fracs[pos_i] = pf

        records.append({
            'folio': fid, 'section': sec, 'gallows': bt[0],
            'bt': bt_word, 'bt_fracs': bt_fracs, 'bt_atoms': bt_atoms_set,
            'hdr_non_bt': hdr_non_bt, 'hdr_fracs': hdr_fracs,
            'body_toks': body_toks, 'body_fracs': body_fracs,
            'pos_fracs': pos_fracs,
            'n_header_tokens': len(hdr_all),
        })

print(f'Paragraphs with header + body: {len(records)}')
print(f'Total lines: {len(all_lines)}')
print(f'Total paragraphs: {len(all_paras)}')

results = {'n_paragraphs': len(records), 'n_lines': len(all_lines), 'n_paras_total': len(all_paras)}

# ============================================================
# Section 2: C1786 - Atom echo test
# ============================================================
print('\n' + '='*60)
print('C1786: Atom echo (atom-level vs token-level)')

# Token-level: do paragraphs sharing same boundary token have similar body?
by_token = defaultdict(list)
for r in records:
    by_token[r['bt']].append(r)

eligible = {bt: recs for bt, recs in by_token.items() if len(recs) >= 3}
within_sims, between_sims = [], []
for bt, recs in eligible.items():
    g = recs[0]['gallows']
    profiles = [r['body_fracs'] for r in recs]
    for i, j in combinations(range(len(profiles)), 2):
        within_sims.append(cosine_sim(profiles[i], profiles[j]))
    other = []
    for bt2, recs2 in eligible.items():
        if bt2 != bt and recs2[0]['gallows'] == g:
            other.extend([r['body_fracs'] for r in recs2])
    for p1 in profiles:
        for p2 in other[:50]:
            between_sims.append(cosine_sim(p1, p2))

token_diff = np.mean(within_sims) - np.mean(between_sims)
rng = np.random.default_rng(42)
all_sims_arr = within_sims + between_sims
labels = [1]*len(within_sims) + [0]*len(between_sims)
perm_diffs = []
for _ in range(1000):
    sh = rng.permutation(labels)
    w = [s for s, l in zip(all_sims_arr, sh) if l == 1]
    b = [s for s, l in zip(all_sims_arr, sh) if l == 0]
    perm_diffs.append(np.mean(w) - np.mean(b))
perm_diffs = np.array(perm_diffs)
token_z = (token_diff - np.mean(perm_diffs)) / (np.std(perm_diffs) + 1e-10)
token_p = float(np.mean(perm_diffs >= token_diff))
print(f'  Token-level: within={np.mean(within_sims):.4f} between={np.mean(between_sims):.4f} diff={token_diff:+.4f} z={token_z:.2f} p={token_p:.4f}')

# Atom-level echo: does atom presence in BT MIDDLE predict body enrichment?
echo_scores = []
for r in records:
    bt_vec = np.array([1 if a in r['bt_atoms'] else 0 for a in ATOMS])
    body_vec = r['body_fracs']
    if np.std(bt_vec) > 0 and np.std(body_vec) > 0:
        echo_scores.append(np.corrcoef(bt_vec, body_vec)[0, 1])

echo_mean = np.mean(echo_scores)
echo_se = np.std(echo_scores) / np.sqrt(len(echo_scores))
echo_t = echo_mean / echo_se

# Permutation null for atom echo
all_bt_atoms = [r['bt_atoms'] for r in records]
null_means = []
for _ in range(1000):
    perm_idx = rng.permutation(len(records))
    ps = []
    for i, r in enumerate(records):
        bt_vec = np.array([1 if a in all_bt_atoms[perm_idx[i]] else 0 for a in ATOMS])
        body_vec = r['body_fracs']
        if np.std(bt_vec) > 0 and np.std(body_vec) > 0:
            ps.append(np.corrcoef(bt_vec, body_vec)[0, 1])
    null_means.append(np.mean(ps))
null_means = np.array(null_means)
atom_z = (echo_mean - np.mean(null_means)) / (np.std(null_means) + 1e-10)
atom_p = float(np.mean(null_means >= echo_mean))
print(f'  Atom-level echo: mean_r={echo_mean:.4f} perm_z={atom_z:.2f} p={atom_p:.4f}')

# Per-atom enrichment (gallows-controlled)
atom_echo_detail = {}
for atom in ATOMS:
    all_present, all_absent = [], []
    for g in 'ktpf':
        sub = [r for r in records if r['gallows'] == g]
        present = [r['body_fracs'][ATOMS.index(atom)] for r in sub if atom in r['bt_atoms']]
        absent = [r['body_fracs'][ATOMS.index(atom)] for r in sub if atom not in r['bt_atoms']]
        if len(present) >= 3 and len(absent) >= 3:
            cm = np.mean([r['body_fracs'][ATOMS.index(atom)] for r in sub])
            all_present.extend([v - cm for v in present])
            all_absent.extend([v - cm for v in absent])
    if len(all_present) >= 10 and len(all_absent) >= 10:
        t_val, p_val = stats.ttest_ind(all_present, all_absent)
        diff = np.mean(all_present) - np.mean(all_absent)
        atom_echo_detail[atom] = {'diff': float(diff), 't': float(t_val), 'p': float(p_val),
                                   'n_present': len(all_present), 'n_absent': len(all_absent)}
        sig = '***' if p_val < 0.001 else '**' if p_val < 0.01 else '*' if p_val < 0.05 else ''
        print(f'    {atom}: diff={diff:+.4f} t={t_val:.2f} p={p_val:.4f} {sig}')

results['C1786'] = {
    'token_level': {'diff': float(token_diff), 'z': float(token_z), 'p': token_p},
    'atom_level': {'mean_echo': float(echo_mean), 'z': float(atom_z), 'p': atom_p, 'n': len(echo_scores)},
    'per_atom': atom_echo_detail,
}

# ============================================================
# Section 3: C1787 - Positional decay
# ============================================================
print('\n' + '='*60)
print('C1787: Header positional decay')

pos_results = {}
for pos in range(8):
    corrs = []
    for r in records:
        if pos in r['pos_fracs']:
            pv = r['pos_fracs'][pos]
            bv = r['body_fracs']
            if np.std(pv) > 0 and np.std(bv) > 0:
                corrs.append(np.corrcoef(pv, bv)[0, 1])
    if len(corrs) >= 50:
        mc = np.mean(corrs)
        se = np.std(corrs) / np.sqrt(len(corrs))
        t_val = mc / se if se > 0 else 0
        pos_results[str(pos + 2)] = {'mean_corr': float(mc), 'se': float(se), 't': float(t_val), 'n': len(corrs)}
        print(f'  Position {pos+2}: r={mc:.4f} +/- {se:.4f} t={t_val:.2f} n={len(corrs)}')

# Position-2 PREFIX composition
pos2_prefixes = Counter()
for r in records:
    if r['hdr_non_bt']:
        m = morph.extract(r['hdr_non_bt'][0])
        pos2_prefixes[m.prefix or '(none)'] += 1
print(f'  Position-2 PREFIX distribution (top 10):')
for pfx, ct in pos2_prefixes.most_common(10):
    print(f'    {pfx}: {ct} ({100*ct/sum(pos2_prefixes.values()):.1f}%)')

results['C1787'] = {
    'position_decay': pos_results,
    'pos2_prefixes': dict(pos2_prefixes.most_common(10)),
}

# ============================================================
# Section 4: C1788 - Specification register characterization
# ============================================================
print('\n' + '='*60)
print('C1788: Specification register (header vs body atom fracs)')

hdr_words = Counter()
body_words = Counter()
for r in records:
    for w in r['hdr_non_bt']:
        hdr_words[w] += 1
    for w in r['body_toks']:
        body_words[w] += 1

def atom_fracs_from_counter(wc):
    atoms = Counter()
    for w, ct in wc.items():
        m = morph.extract(w)
        if m.middle:
            for c in m.middle:
                if c in ATOMS:
                    atoms[c] += ct
    total = sum(atoms.values())
    return {a: atoms.get(a, 0) / total for a in ATOMS}

hdr_af = atom_fracs_from_counter(hdr_words)
body_af = atom_fracs_from_counter(body_words)

spec_register = {}
print(f'  {"atom":>4s}  {"header":>8s}  {"body":>8s}  {"ratio":>6s}')
for a in ATOMS:
    ratio = hdr_af[a] / body_af[a] if body_af[a] > 0 else float('inf')
    spec_register[a] = {'header': float(hdr_af[a]), 'body': float(body_af[a]), 'ratio': float(ratio)}
    marker = ' <--' if abs(ratio - 1) > 0.3 else ''
    print(f'  {a:>4s}  {hdr_af[a]:8.4f}  {body_af[a]:8.4f}  {ratio:6.2f}{marker}')

# Header length distribution
hdr_lens = [r['n_header_tokens'] for r in records]
print(f'  Header length: mean={np.mean(hdr_lens):.1f} median={np.median(hdr_lens):.0f} sd={np.std(hdr_lens):.1f}')

results['C1788'] = {
    'atom_ratios': spec_register,
    'header_length': {'mean': float(np.mean(hdr_lens)), 'median': float(np.median(hdr_lens)), 'sd': float(np.std(hdr_lens))},
}

# ============================================================
# Section 5: C1789 - Vocabulary exclusivity
# ============================================================
print('\n' + '='*60)
print('C1789: Vocabulary exclusivity')

# Boundary token exclusivity
bt_counter = Counter(r['bt'] for r in records)
bt_vocab = set(bt_counter.keys())
body_vocab = set(body_words.keys())
bt_shared = bt_vocab & body_vocab
bt_exclusive = bt_vocab - body_vocab

print(f'  Boundary tokens: {len(bt_vocab)} types')
print(f'  Exclusive to boundaries: {len(bt_exclusive)} ({100*len(bt_exclusive)/len(bt_vocab):.1f}%)')
print(f'  Also in body: {len(bt_shared)} ({100*len(bt_shared)/len(bt_vocab):.1f}%)')

# Header non-BT exclusivity
hdr_vocab = set(hdr_words.keys())
hdr_shared = hdr_vocab & body_vocab
hdr_exclusive = hdr_vocab - body_vocab
print(f'  Header non-BT: {len(hdr_vocab)} types')
print(f'  Header-exclusive: {len(hdr_exclusive)} ({100*len(hdr_exclusive)/len(hdr_vocab):.1f}%)')

# Body gallows-containing rate
body_gallows_count = sum(ct for w, ct in body_words.items() if any(c in GALLOWS_SET for c in w))
body_total = sum(body_words.values())
print(f'  Body tokens with gallows chars: {body_gallows_count}/{body_total} = {100*body_gallows_count/body_total:.1f}%')

results['C1789'] = {
    'bt_types': len(bt_vocab),
    'bt_exclusive_pct': float(100 * len(bt_exclusive) / len(bt_vocab)),
    'hdr_types': len(hdr_vocab),
    'hdr_exclusive_pct': float(100 * len(hdr_exclusive) / len(hdr_vocab)),
    'body_gallows_pct': float(100 * body_gallows_count / body_total),
}

# ============================================================
# Section 6: C1790 - Uniqueness census
# ============================================================
print('\n' + '='*60)
print('C1790: Uniqueness census')

line_counts = Counter(l['line_str'] for l in all_lines)
dup_lines = sum(1 for c in line_counts.values() if c > 1)
para_counts = Counter(p['para_str'] for p in all_paras)
dup_paras = sum(1 for c in para_counts.values() if c > 1)

print(f'  Unique lines: {len(line_counts)}/{len(all_lines)} (duplicates: {dup_lines})')
print(f'  Unique paragraphs: {len(para_counts)}/{len(all_paras)} (duplicates: {dup_paras})')

# Near-duplicates (Jaccard >= 0.8, 5+ tokens)
long_lines = [l for l in all_lines if l['n_tokens'] >= 5]
by_len = defaultdict(list)
for i, l in enumerate(long_lines):
    by_len[l['n_tokens']].append(i)

near_dup_count = 0
for n_tok in sorted(by_len.keys()):
    candidates = []
    for delta in [-1, 0, 1]:
        if n_tok + delta in by_len:
            candidates.extend(by_len[n_tok + delta])
    candidates = sorted(set(candidates))
    for ii, idx_i in enumerate(by_len[n_tok]):
        toks_i = set(long_lines[idx_i]['line_str'].split())
        for idx_j in candidates:
            if idx_j <= idx_i:
                continue
            toks_j = set(long_lines[idx_j]['line_str'].split())
            inter = len(toks_i & toks_j)
            union = len(toks_i | toks_j)
            if union > 0 and inter / union >= 0.8:
                if long_lines[idx_i]['line_str'] != long_lines[idx_j]['line_str']:
                    near_dup_count += 1

print(f'  Near-duplicate line pairs (Jaccard>=0.8): {near_dup_count}')

# N-gram cross-folio census
ngram_stats = {}
for n in [3, 4, 5]:
    ngram_locs = defaultdict(set)
    for l in all_lines:
        toks = l['line_str'].split()
        for i in range(len(toks) - n + 1):
            ng = tuple(toks[i:i+n])
            ngram_locs[ng].add(l['folio'])
    cross = sum(1 for ng, fols in ngram_locs.items() if len(fols) >= 3)
    ngram_stats[str(n)] = {'total_unique': len(ngram_locs), 'in_3plus_folios': cross}
    print(f'  {n}-grams: {len(ngram_locs)} unique, {cross} in 3+ folios')

results['C1790'] = {
    'duplicate_lines': dup_lines,
    'duplicate_paras': dup_paras,
    'near_duplicate_pairs': near_dup_count,
    'total_lines': len(all_lines),
    'total_paras': len(all_paras),
    'ngram_stats': ngram_stats,
}

# ============================================================
# Section 7: C1791 - Universality and residual analysis
# ============================================================
print('\n' + '='*60)
print('C1791: Universality and residual analysis')

# Cross-folio header-body correspondence per section
section_corr = {}
for sec in ['Stars', 'Bio', 'Herbal']:
    sub = [r for r in records if r['section'] == sec and r['hdr_fracs'] is not None]
    if len(sub) < 20:
        continue
    hdr_sims_s, body_sims_s = [], []
    pair_indices = list(combinations(range(len(sub)), 2))
    rng2 = np.random.default_rng(42)
    if len(pair_indices) > 3000:
        sample = rng2.choice(len(pair_indices), 3000, replace=False)
        pair_indices = [pair_indices[i] for i in sample]
    for i, j in pair_indices:
        if sub[i]['folio'] == sub[j]['folio']:
            continue
        hs = cosine_sim(sub[i]['hdr_fracs'], sub[j]['hdr_fracs'])
        bs = cosine_sim(sub[i]['body_fracs'], sub[j]['body_fracs'])
        hdr_sims_s.append(hs)
        body_sims_s.append(bs)
    if len(hdr_sims_s) >= 50:
        r_corr, p_corr = stats.pearsonr(hdr_sims_s, body_sims_s)
        section_corr[sec] = {'r': float(r_corr), 'p': float(p_corr), 'n_pairs': len(hdr_sims_s)}
        print(f'  {sec}: cross-folio header-body r={r_corr:.4f} p={p_corr:.4f} n={len(hdr_sims_s)}')

# BT-residualized header echo
bt_present = [r for r in records if r['bt_fracs'] is not None and r['hdr_fracs'] is not None]
if len(bt_present) >= 20:
    X_bt = np.array([r['bt_fracs'] for r in bt_present])
    Y_bt = np.array([r['body_fracs'] for r in bt_present])
    X_hdr = np.array([r['hdr_fracs'] for r in bt_present])
    beta_bt, _, _, _ = lstsq(np.hstack([X_bt, np.ones((len(bt_present), 1))]), Y_bt, rcond=None)
    Y_resid = Y_bt - np.hstack([X_bt, np.ones((len(bt_present), 1))]) @ beta_bt
    X_hdr_int = np.hstack([X_hdr, np.ones((len(bt_present), 1))])
    ss_res_null = np.sum(Y_resid**2)
    beta_hdr, _, _, _ = lstsq(X_hdr_int, Y_resid, rcond=None)
    Y_pred = X_hdr_int @ beta_hdr
    ss_res_hdr = np.sum((Y_resid - Y_pred)**2)
    r2_hdr_resid = float(1 - ss_res_hdr / ss_res_null)
    print(f'  BT-residualized header R2: {r2_hdr_resid:.4f} (n={len(bt_present)})')
else:
    r2_hdr_resid = None

# Incremental R2 beyond gallows + section + folio
Y = np.array([r['body_fracs'] for r in records])
gallows_cats = sorted(set(r['gallows'] for r in records))
section_cats = sorted(set(r['section'] for r in records))
folio_cats = sorted(set(r['folio'] for r in records))

def one_hot(val, cats):
    v = np.zeros(len(cats))
    if val in cats:
        v[cats.index(val)] = 1
    return v

X_ctrl = np.array([np.concatenate([one_hot(r['gallows'], gallows_cats),
                                     one_hot(r['section'], section_cats),
                                     one_hot(r['folio'], folio_cats), [1]])
                    for r in records])
X_hdr_all = np.array([r['hdr_fracs'] if r['hdr_fracs'] is not None else np.zeros(10) for r in records])
X_full = np.hstack([X_ctrl, X_hdr_all])

def r2(X, Y):
    try:
        beta, _, _, _ = lstsq(X, Y, rcond=None)
        ss_res = np.sum((Y - X @ beta)**2)
        ss_tot = np.sum((Y - np.mean(Y, axis=0))**2)
        return float(1 - ss_res / ss_tot)
    except:
        return float('nan')

r2_ctrl = r2(X_ctrl, Y)
r2_full = r2(X_full, Y)
dr2 = r2_full - r2_ctrl

# Permutation null
null_dr2 = []
for _ in range(200):
    X_hdr_perm = X_hdr_all[rng.permutation(len(records))]
    X_full_perm = np.hstack([X_ctrl, X_hdr_perm])
    null_dr2.append(r2(X_full_perm, Y) - r2_ctrl)
null_dr2 = np.array(null_dr2)
inc_z = float((dr2 - np.mean(null_dr2)) / (np.std(null_dr2) + 1e-10))
inc_p = float(np.mean(null_dr2 >= dr2))

print(f'  Incremental R2 (header after controls): dR2={dr2:+.4f} z={inc_z:.2f} p={inc_p:.4f}')

results['C1791'] = {
    'section_cross_folio': section_corr,
    'bt_residualized_r2': r2_hdr_resid,
    'bt_residualized_n': len(bt_present) if bt_present else 0,
    'incremental_r2': float(dr2),
    'incremental_z': inc_z,
    'incremental_p': inc_p,
    'r2_controls': float(r2_ctrl),
    'r2_full': float(r2_full),
}

# ============================================================
# Section 8: Summary and output
# ============================================================
print('\n' + '='*60)
print('SUMMARY')
print(f'  C1786 atom echo: z={atom_z:.2f} p={atom_p:.4f} | token echo: z={token_z:.2f} p={token_p:.4f}')
print(f'  C1787 pos2 r={pos_results.get("2", {}).get("mean_corr", "N/A")} decaying to pos7')
print(f'  C1788 p-atom ratio={spec_register["p"]["ratio"]:.1f}x, f-atom={spec_register["f"]["ratio"]:.1f}x')
print(f'  C1789 BT exclusive={results["C1789"]["bt_exclusive_pct"]:.1f}%')
print(f'  C1790 duplicates: lines={dup_lines} paras={dup_paras} near={near_dup_count}')
print(f'  C1791 dR2={dr2:+.4f} z={inc_z:.2f} p={inc_p:.4f}')

outpath = 'phases/PARAGRAPH_HEADER_SPECIFICATION_GRAMMAR/results/header_specification_results.json'
with open(outpath, 'w') as f:
    json.dump(results, f, indent=2)
print(f'\nResults written to {outpath}')
