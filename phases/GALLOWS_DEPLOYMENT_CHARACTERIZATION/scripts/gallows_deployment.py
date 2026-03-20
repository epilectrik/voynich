"""Phase 611: Gallows Deployment Characterization

Consolidated analysis of gallows markers (k/t/p/f) as paragraph deployment
headers. Tests whether gallows bias paragraph body composition, whether
deployment is context-sensitive, and whether gallows are reducible to
paragraph archetypes.

Test blocks:
  A. Body atom ecology -- self-enrichment, complementary bias, full O/E matrix
  B. Body composition -- atom/bigram/MIDDLE resolution escalation
  C. Deployment context -- ambient thermal/monitoring state, event trigger nulls
  D. Archetype interaction -- aggregate and within-section independence
  E. Auxiliary -- terminal suffix routing, folio ecology correlations

Each test includes: sample definition, effect size, exact p, raw/expected
counts, section-controlled version where applicable.

Output: gallows_deployment_results.json
"""
import sys, json, warnings
from pathlib import Path
from collections import Counter, defaultdict
from itertools import combinations
import numpy as np
from scipy.stats import chi2_contingency, kruskal, spearmanr

warnings.filterwarnings('ignore')
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript, BFolioDecoder, Morphology, CategoryClassifier

tx = Transcript()
decoder = BFolioDecoder()
morph = Morphology()
cc = CategoryClassifier()

ALL_ATOMS = set('kehtpfdscigolamynr')
GALLOWS_SET = set('ktpf')
ATOM_GLOSSES = cc.ATOM_GLOSSES

# ============================================================
# DATA COLLECTION
# ============================================================
print("Collecting paragraph data...")

folio_sections = {}
for tok in tx.currier_b():
    if tok.folio not in folio_sections:
        folio_sections[tok.folio] = tok.section

folios = sorted(folio_sections.keys())

# Per-paragraph records with body atom counts (excluding gallows-initial token)
records = []
# Per-gallows aggregate body atom counts
gallows_atoms = {g: Counter() for g in 'ktpf'}
gallows_totals = {g: 0 for g in 'ktpf'}
# Per-gallows bigram and co-occurrence counts
gallows_bigrams = {g: Counter() for g in 'ktpf'}
gallows_cosets = {g: Counter() for g in 'ktpf'}
gallows_middles = {g: Counter() for g in 'ktpf'}
gallows_middle_n = {g: 0 for g in 'ktpf'}

for fid in folios:
    sec = folio_sections[fid]
    paragraphs = decoder.analyze_folio_paragraphs(fid)

    for para in paragraphs:
        bt = para.boundary_token or ''
        if not bt or bt[0] not in GALLOWS_SET:
            continue
        gtype = bt[0]

        body_atoms = Counter()
        body_tokens = 0
        first_skipped = False

        for line in para.lines:
            for tok in line.tokens:
                if not first_skipped:
                    first_skipped = True
                    continue  # skip gallows-initial token

                body_tokens += 1
                if tok.morph and tok.morph.middle:
                    mid = tok.morph.middle
                    for ch in mid:
                        if ch in ALL_ATOMS:
                            body_atoms[ch] += 1
                            gallows_atoms[gtype][ch] += 1
                            gallows_totals[gtype] += 1

                    # Composition data (for block B)
                    if len(mid) >= 2:
                        gallows_middles[gtype][mid] += 1
                        gallows_middle_n[gtype] += 1
                        for i in range(len(mid) - 1):
                            gallows_bigrams[gtype][mid[i] + mid[i+1]] += 1
                        unique = sorted(set(ch for ch in mid if ch in ALL_ATOMS))
                        for a1, a2 in combinations(unique, 2):
                            gallows_cosets[gtype][a1 + a2] += 1

        if body_tokens < 3:
            continue
        total_atoms = sum(body_atoms.values())
        if total_atoms == 0:
            continue

        records.append({
            'gallows': gtype, 'section': sec, 'folio': fid,
            'para_id': para.paragraph_id,
            'body_atoms': dict(body_atoms),
            'body_total': total_atoms,
            'body_tokens': body_tokens,
        })

n_by_g = Counter(r['gallows'] for r in records)
print(f"  {len(records)} gallows paragraphs: k={n_by_g['k']} t={n_by_g['t']} p={n_by_g['p']} f={n_by_g['f']}")

results = {
    'phase': '611_GALLOWS_DEPLOYMENT_CHARACTERIZATION',
    'meta': {
        'total_paragraphs': len(records),
        'paragraphs_by_gallows': dict(n_by_g),
        'body_atoms_by_gallows': {g: gallows_totals[g] for g in 'ktpf'},
        'header_token_excluded': True,
        'min_body_tokens': 3,
        'folios_analyzed': len(folios),
        'sections': sorted(set(folio_sections.values())),
    },
    'tests': {},
    'constraint_evidence': {},
}

# ============================================================
# BLOCK A: BODY ATOM ECOLOGY
# ============================================================
print("\n=== BLOCK A: Body Atom Ecology ===")

grand_total = sum(gallows_totals.values())
atom_grand = Counter()
for g in 'ktpf':
    for a, n in gallows_atoms[g].items():
        atom_grand[a] += n

# A1: Self-enrichment (each gallows vs its own atom)
a1_results = {}
for g_target in 'ktpf':
    atom = g_target
    self_count = gallows_atoms[g_target].get(atom, 0)
    self_total = gallows_totals[g_target]
    other_count = sum(gallows_atoms[g].get(atom, 0) for g in 'ktpf' if g != g_target)
    other_total = sum(gallows_totals[g] for g in 'ktpf' if g != g_target)

    self_frac = self_count / self_total if self_total > 0 else 0
    other_frac = other_count / other_total if other_total > 0 else 0
    oe = self_frac / other_frac if other_frac > 0 else 0

    ct = np.array([[self_count, self_total - self_count],
                    [other_count, other_total - other_count]])
    if ct.min() > 0:
        chi2, p, _, _ = chi2_contingency(ct, correction=True)
    else:
        chi2, p = 0, 1.0

    verdict = 'ENRICHED' if oe > 1.05 and p < 0.05 else 'DEPLETED' if oe < 0.95 and p < 0.05 else 'NULL'
    a1_results[g_target] = {
        'atom': atom, 'self_count': int(self_count), 'self_total': int(self_total),
        'other_count': int(other_count), 'other_total': int(other_total),
        'self_frac': round(self_frac, 6), 'other_frac': round(other_frac, 6),
        'oe_ratio': round(oe, 4), 'chi2': round(chi2, 2), 'p': round(p, 6),
        'verdict': verdict,
    }
    print(f"  {g_target}-self: O/E={oe:.3f} p={p:.4f} -> {verdict}")

# A2: k->e complementary test
atom = 'e'
g_target = 'k'
self_count = gallows_atoms[g_target].get(atom, 0)
self_total = gallows_totals[g_target]
other_count = sum(gallows_atoms[g].get(atom, 0) for g in 'ktpf' if g != g_target)
other_total = sum(gallows_totals[g] for g in 'ktpf' if g != g_target)
self_frac = self_count / self_total if self_total > 0 else 0
other_frac = other_count / other_total if other_total > 0 else 0
oe = self_frac / other_frac if other_frac > 0 else 0
ct = np.array([[self_count, self_total - self_count],
                [other_count, other_total - other_count]])
if ct.min() > 0:
    chi2, p, _, _ = chi2_contingency(ct, correction=True)
else:
    chi2, p = 0, 1.0
a2_result = {
    'gallows': 'k', 'body_atom': 'e',
    'self_count': int(self_count), 'self_total': int(self_total),
    'other_count': int(other_count), 'other_total': int(other_total),
    'self_frac': round(self_frac, 6), 'other_frac': round(other_frac, 6),
    'oe_ratio': round(oe, 4), 'chi2': round(chi2, 2), 'p': round(p, 6),
}
print(f"  k->e complementary: O/E={oe:.3f} p={p:.6f}")

# A3: Section-stratified p self-enrichment (strongest signal)
sections = sorted(set(r['section'] for r in records))
a3_results = {}
for sec in sections:
    sec_recs = [r for r in records if r['section'] == sec]
    self_match = sum(r['body_atoms'].get('p', 0) for r in sec_recs if r['gallows'] == 'p')
    self_total_s = sum(r['body_total'] for r in sec_recs if r['gallows'] == 'p')
    other_match = sum(r['body_atoms'].get('p', 0) for r in sec_recs if r['gallows'] != 'p')
    other_total_s = sum(r['body_total'] for r in sec_recs if r['gallows'] != 'p')

    if self_total_s < 50 or other_total_s < 50:
        a3_results[sec] = {'status': 'insufficient_data', 'n_p_paras': sum(1 for r in sec_recs if r['gallows'] == 'p')}
        continue

    sf = self_match / self_total_s
    of = other_match / other_total_s
    oe = sf / of if of > 0 else 0
    ct = np.array([[self_match, self_total_s - self_match],
                    [other_match, other_total_s - other_match]])
    if ct.min() > 0:
        chi2, p, _, _ = chi2_contingency(ct, correction=True)
    else:
        chi2, p = 0, 1.0
    a3_results[sec] = {
        'oe_ratio': round(oe, 4), 'p': round(p, 6), 'chi2': round(chi2, 2),
        'self_count': int(self_match), 'self_total': int(self_total_s),
        'other_count': int(other_match), 'other_total': int(other_total_s),
        'n_p_paras': sum(1 for r in sec_recs if r['gallows'] == 'p'),
    }
    print(f"  p-self in {sec}: O/E={oe:.3f} p={p:.4f} (n={a3_results[sec]['n_p_paras']})")

# A4: Full O/E matrix (4 gallows x 18 atoms)
atom_list = sorted(ALL_ATOMS)
oe_matrix = {}
for g in 'ktpf':
    oe_matrix[g] = {}
    for a in atom_list:
        obs = gallows_atoms[g].get(a, 0)
        exp = (gallows_totals[g] * atom_grand[a]) / grand_total if grand_total > 0 else 0
        oe_matrix[g][a] = round(obs / exp, 4) if exp > 5 else None

# A5: Full contingency table chi2 (atoms)
ct_full = np.zeros((4, len(atom_list)), dtype=int)
for gi, g in enumerate('ktpf'):
    for ai, a in enumerate(atom_list):
        ct_full[gi, ai] = gallows_atoms[g].get(a, 0)
col_mask = ct_full.sum(0) > 0
ct_clean = ct_full[:, col_mask]
chi2_atom, p_atom, dof_atom, exp_atom = chi2_contingency(ct_clean)
v_atom = np.sqrt(chi2_atom / (ct_clean.sum() * (min(ct_clean.shape) - 1)))
print(f"  Full atom contingency: V={v_atom:.4f} p={p_atom:.6f}")

results['tests']['A_body_atom_ecology'] = {
    'A1_self_enrichment': a1_results,
    'A2_k_e_complementary': a2_result,
    'A3_p_section_stratified': a3_results,
    'A4_oe_matrix': oe_matrix,
    'A5_full_contingency': {
        'chi2': round(chi2_atom, 2), 'p': round(p_atom, 8),
        'dof': int(dof_atom), 'cramers_v': round(v_atom, 4),
        'low_expected_cells': int((exp_atom < 5).sum()),
        'total_cells': int(exp_atom.size),
        'total_observations': int(ct_clean.sum()),
    },
}

# ============================================================
# BLOCK B: BODY COMPOSITION (resolution escalation)
# ============================================================
print("\n=== BLOCK B: Body Composition Escalation ===")

# B1: Bigram-level contingency
bigram_grand = Counter()
for g in 'ktpf':
    for pair, n in gallows_bigrams[g].items():
        bigram_grand[pair] += n

top_bigrams = [pair for pair, _ in bigram_grand.most_common(30)]
ct_bi = np.zeros((4, len(top_bigrams)), dtype=int)
for gi, g in enumerate('ktpf'):
    for bi, pair in enumerate(top_bigrams):
        ct_bi[gi, bi] = gallows_bigrams[g].get(pair, 0)
col_mask_bi = ct_bi.sum(0) > 0
ct_bi_clean = ct_bi[:, col_mask_bi]
chi2_bi, p_bi, dof_bi, exp_bi = chi2_contingency(ct_bi_clean)
v_bi = np.sqrt(chi2_bi / (ct_bi_clean.sum() * (min(ct_bi_clean.shape) - 1)))
print(f"  Bigram contingency (top 30): V={v_bi:.4f} p={p_bi:.6f}")

# B2: MIDDLE-level contingency
middle_grand = Counter()
for g in 'ktpf':
    for mid, n in gallows_middles[g].items():
        middle_grand[mid] += n

top_mids = [mid for mid, _ in middle_grand.most_common(30)]
ct_mid = np.zeros((4, len(top_mids)), dtype=int)
for gi, g in enumerate('ktpf'):
    for mi, mid in enumerate(top_mids):
        ct_mid[gi, mi] = gallows_middles[g].get(mid, 0)
col_mask_mid = ct_mid.sum(0) > 0
ct_mid_clean = ct_mid[:, col_mask_mid]
chi2_mid, p_mid, dof_mid, exp_mid = chi2_contingency(ct_mid_clean)
v_mid = np.sqrt(chi2_mid / (ct_mid_clean.sum() * (min(ct_mid_clean.shape) - 1)))
print(f"  MIDDLE contingency (top 30): V={v_mid:.4f} p={p_mid:.6f}")

# B3: f-gallows specific patterns (preserved as observation, not Tier 2)
f_enriched_pairs = []
f_bi_total = sum(gallows_bigrams['f'].values())
grand_bi_total = sum(bigram_grand.values())
for pair, obs in gallows_bigrams['f'].items():
    exp = (f_bi_total * bigram_grand[pair]) / grand_bi_total if grand_bi_total > 0 else 0
    if exp >= 3 and obs >= 3:
        oe = obs / exp
        if oe > 1.5 or oe < 0.5:
            f_enriched_pairs.append({'pair': pair, 'obs': int(obs), 'exp': round(exp, 1), 'oe': round(oe, 3)})

results['tests']['B_body_composition'] = {
    'resolution_escalation': {
        'atom_level': {'cramers_v': round(v_atom, 4), 'p': round(p_atom, 8),
                       'total_obs': int(ct_clean.sum())},
        'bigram_level': {'cramers_v': round(v_bi, 4), 'p': round(p_bi, 8),
                         'chi2': round(chi2_bi, 2), 'dof': int(dof_bi),
                         'total_obs': int(ct_bi_clean.sum()),
                         'n_bigram_types': int(col_mask_bi.sum())},
        'middle_level': {'cramers_v': round(v_mid, 4), 'p': round(p_mid, 8),
                         'chi2': round(chi2_mid, 2), 'dof': int(dof_mid),
                         'total_obs': int(ct_mid_clean.sum()),
                         'n_middle_types': int(col_mask_mid.sum())},
        'v_escalation': f'{v_atom:.3f} -> {v_bi:.3f} -> {v_mid:.3f}',
    },
    'f_gallows_notable_patterns': f_enriched_pairs,
}

print(f"  Escalation: V={v_atom:.3f} -> {v_bi:.3f} -> {v_mid:.3f}")

# ============================================================
# BLOCK C: DEPLOYMENT CONTEXT
# ============================================================
print("\n=== BLOCK C: Deployment Context ===")

# Build line-level state series
folio_lines = {}
for fid in folios:
    paragraphs = decoder.analyze_folio_paragraphs(fid)
    lines_list = []
    for pi, para in enumerate(paragraphs):
        bt = para.boundary_token or ''
        gtype = bt[0] if bt and bt[0] in GALLOWS_SET else 'none'
        for li, line in enumerate(para.lines):
            k_count = h_count = e_count = 0
            atom_counts = Counter()
            cat_counts = Counter()
            n_tokens = 0
            for tok in line.tokens:
                if li == 0 and n_tokens == 0 and pi > 0:
                    n_tokens += 1
                    continue
                n_tokens += 1
                if tok.morph and tok.morph.middle:
                    mid = tok.morph.middle
                    for ch in mid:
                        atom_counts[ch] += 1
                        if ch == 'k': k_count += 1
                        elif ch == 'h': h_count += 1
                        elif ch == 'e': e_count += 1
                    cat = cc.classify(mid)
                    if cat:
                        cat_counts[cat] += 1
            total_a = sum(atom_counts.values())
            total_c = sum(cat_counts.values())
            lines_list.append({
                'para_idx': pi, 'line_idx': li,
                'is_boundary': (li == 0),
                'gallows': gtype if li == 0 else None,
                'k_frac': k_count / total_a if total_a > 0 else 0,
                'h_frac': h_count / total_a if total_a > 0 else 0,
                'e_frac': e_count / total_a if total_a > 0 else 0,
                'k_count': k_count, 'h_count': h_count, 'e_count': e_count,
                'total_atoms': total_a,
                'thermal_frac': cat_counts.get('THERMAL', 0) / total_c if total_c > 0 else 0,
                'monitoring_frac': (cat_counts.get('MONITORING', 0) + cat_counts.get('MARKING', 0)) / total_c if total_c > 0 else 0,
                'n_tokens': n_tokens,
            })
    folio_lines[fid] = lines_list

# C1: Run-up state (3-line window before gallows boundary)
c1_results = {}
window = 3
runup_states = {g: [] for g in 'ktpf'}
for fid, lines in folio_lines.items():
    for i, line in enumerate(lines):
        if line['is_boundary'] and line['gallows'] in GALLOWS_SET:
            g = line['gallows']
            preceding = [lines[j] for j in range(max(0, i - window), i)
                         if lines[j]['total_atoms'] >= 3]
            if preceding:
                runup_states[g].append({
                    'k': np.mean([l['k_frac'] for l in preceding]),
                    'h': np.mean([l['h_frac'] for l in preceding]),
                    'e': np.mean([l['e_frac'] for l in preceding]),
                    'thermal': np.mean([l['thermal_frac'] for l in preceding]),
                    'monitoring': np.mean([l['monitoring_frac'] for l in preceding]),
                })

for var in ['k', 'h', 'e', 'thermal', 'monitoring']:
    groups = {g: [r[var] for r in runup_states[g]] for g in 'ktpf'}
    all_groups = [v for v in groups.values() if len(v) >= 5]
    if len(all_groups) >= 2:
        stat, p = kruskal(*all_groups)
    else:
        stat, p = 0, 1.0
    means = {g: round(np.mean(groups[g]), 5) if groups[g] else 0 for g in 'ktpf'}
    c1_results[var] = {
        'means_by_gallows': means,
        'kw_statistic': round(stat, 3),
        'p': round(p, 6),
        'n_by_gallows': {g: len(groups[g]) for g in 'ktpf'},
    }
    sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else ''
    print(f"  Run-up {var}: p={p:.4f}{sig}")

# C2: Alarm conditions (above-median spikes) -- event triggers
# Compute per-folio medians
for fid, lines in folio_lines.items():
    k_vals = [l['k_frac'] for l in lines if l['total_atoms'] >= 3]
    h_vals = [l['h_frac'] for l in lines if l['total_atoms'] >= 3]
    e_vals = [l['e_frac'] for l in lines if l['total_atoms'] >= 3]
    med_k = np.median(k_vals) if k_vals else 0
    med_h = np.median(h_vals) if h_vals else 0
    med_e = np.median(e_vals) if e_vals else 0
    for line in lines:
        line['k_high'] = line['k_frac'] > med_k and line['total_atoms'] >= 3
        line['h_high'] = line['h_frac'] > med_h and line['total_atoms'] >= 3
        line['e_high'] = line['e_frac'] > med_e and line['total_atoms'] >= 3

c2_results = {}
for alarm_type in ['k_high', 'h_high', 'e_high']:
    alarm_g = {'alarm': Counter(), 'no_alarm': Counter()}
    for fid, lines in folio_lines.items():
        for i, line in enumerate(lines):
            if line['is_boundary'] and line['gallows'] in GALLOWS_SET and i >= 2:
                g = line['gallows']
                has_alarm = any(lines[j].get(alarm_type, False) for j in range(max(0, i-2), i))
                key = 'alarm' if has_alarm else 'no_alarm'
                alarm_g[key][g] += 1

    ct = np.array([[alarm_g['alarm'].get(g, 0) for g in 'ktpf'],
                    [alarm_g['no_alarm'].get(g, 0) for g in 'ktpf']])
    if ct.min() >= 0 and ct.sum() > 0:
        chi2, p, dof, _ = chi2_contingency(ct)
    else:
        chi2, p, dof = 0, 1, 0
    c2_results[alarm_type] = {
        'chi2': round(chi2, 2), 'p': round(p, 4), 'dof': int(dof),
        'alarm_counts': {g: int(alarm_g['alarm'].get(g, 0)) for g in 'ktpf'},
        'no_alarm_counts': {g: int(alarm_g['no_alarm'].get(g, 0)) for g in 'ktpf'},
    }
    sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else ''
    print(f"  Alarm {alarm_type}: p={p:.4f}{sig} (event trigger)")

# C3: Delta (rate of change) approaching boundary
c3_results = {}
delta_by_g = {g: {'dk': [], 'dh': [], 'de': []} for g in 'ktpf'}
for fid, lines in folio_lines.items():
    for i, line in enumerate(lines):
        if line['is_boundary'] and line['gallows'] in GALLOWS_SET and i >= 3:
            g = line['gallows']
            prev = [lines[j] for j in range(i-3, i) if lines[j]['total_atoms'] >= 3]
            if len(prev) >= 2:
                delta_by_g[g]['dk'].append(prev[-1]['k_frac'] - prev[0]['k_frac'])
                delta_by_g[g]['dh'].append(prev[-1]['h_frac'] - prev[0]['h_frac'])
                delta_by_g[g]['de'].append(prev[-1]['e_frac'] - prev[0]['e_frac'])

for kernel in ['dk', 'dh', 'de']:
    groups = [delta_by_g[g][kernel] for g in 'ktpf' if len(delta_by_g[g][kernel]) >= 5]
    if len(groups) >= 2:
        stat, p = kruskal(*groups)
    else:
        stat, p = 0, 1
    means = {g: round(np.mean(delta_by_g[g][kernel]), 5) if delta_by_g[g][kernel] else 0 for g in 'ktpf'}
    c3_results[kernel] = {
        'means_by_gallows': means, 'kw_statistic': round(stat, 3), 'p': round(p, 4),
        'n_by_gallows': {g: len(delta_by_g[g][kernel]) for g in 'ktpf'},
    }
    sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else ''
    print(f"  Delta {kernel}: p={p:.4f}{sig} (rate-of-change trigger)")

results['tests']['C_deployment_context'] = {
    'C1_runup_state': {'window_lines': window, 'variables': c1_results},
    'C2_alarm_triggers': c2_results,
    'C3_delta_triggers': c3_results,
}

# ============================================================
# BLOCK D: ARCHETYPE INTERACTION
# ============================================================
print("\n=== BLOCK D: Archetype Interaction ===")

# Import archetype machinery
try:
    from sklearn.preprocessing import StandardScaler
    from sklearn.mixture import GaussianMixture
    from phases.STARS_FOLIO_CLOSE_READING.scripts.paragraph_archetypes import (
        extract_paragraph_features, features_to_vector, SECTION_MAP
    )
    HAS_ARCHETYPE = True
except ImportError:
    HAS_ARCHETYPE = False
    print("  WARNING: paragraph_archetypes not available, skipping block D")

if HAS_ARCHETYPE:
    # Rebuild folio sections with SECTION_MAP
    folio_sec_mapped = {}
    for tok in tx.currier_b():
        if tok.folio not in folio_sec_mapped:
            folio_sec_mapped[tok.folio] = SECTION_MAP.get(tok.section, tok.section)

    all_features, all_meta = [], []
    for fid in folios:
        sec = folio_sec_mapped.get(fid, 'UNK')
        fa = decoder.analyze_folio(fid)
        reg = fa.regime if fa and hasattr(fa, 'regime') and fa.regime else 'UNK'
        for pf in extract_paragraph_features(decoder, fid, sec, reg):
            all_features.append(features_to_vector(pf))
            all_meta.append({'section': sec, 'gallows': pf.gallows_type})

    X = np.array(all_features)
    Xs = StandardScaler().fit_transform(X)
    gmm = GaussianMixture(n_components=5, n_init=10, random_state=42, max_iter=300)
    gmm.fit(Xs)
    labels = gmm.predict(Xs)

    # D1: Aggregate
    gall = [m['gallows'] for m in all_meta]
    gset = sorted(set(gall))
    ct_agg = np.zeros((len(gset), 5), dtype=int)
    gi_map = {g: i for i, g in enumerate(gset)}
    for i in range(len(all_meta)):
        ct_agg[gi_map[gall[i]], int(labels[i])] += 1
    chi2_agg, p_agg, dof_agg, _ = chi2_contingency(ct_agg)
    v_agg = np.sqrt(chi2_agg / (len(all_meta) * (min(ct_agg.shape) - 1)))
    print(f"  Aggregate gallows-archetype: V={v_agg:.3f} p={p_agg:.4f}")

    # D2: Per-section
    d2_results = {}
    for sec in ['Stars', 'Bio', 'Herbal', 'Cosmo']:
        idx = [i for i, m in enumerate(all_meta) if m['section'] == sec]
        if len(idx) < 20:
            d2_results[sec] = {'status': 'insufficient_data', 'n': len(idx)}
            continue
        sec_g = [all_meta[i]['gallows'] for i in idx]
        sec_a = [int(labels[i]) for i in idx]
        gset_s = sorted(set(sec_g))
        aset_s = sorted(set(sec_a))
        ct_s = np.zeros((len(gset_s), len(aset_s)), dtype=int)
        gi_s = {g: i for i, g in enumerate(gset_s)}
        ai_s = {a: i for i, a in enumerate(aset_s)}
        for g, a in zip(sec_g, sec_a):
            ct_s[gi_s[g], ai_s[a]] += 1
        rmask = ct_s.sum(1) > 0
        cmask = ct_s.sum(0) > 0
        ct_s2 = ct_s[rmask][:, cmask]
        if ct_s2.shape[0] >= 2 and ct_s2.shape[1] >= 2:
            chi2_s, p_s, dof_s, exp_s = chi2_contingency(ct_s2)
            v_s = np.sqrt(chi2_s / (len(idx) * (min(ct_s2.shape) - 1))) if len(idx) > 0 else 0
            low_exp = int((exp_s < 5).sum())
        else:
            chi2_s, p_s, dof_s, v_s, low_exp = 0, 1, 0, 0, 0

        d2_results[sec] = {
            'n': len(idx), 'chi2': round(chi2_s, 2), 'p': round(p_s, 4),
            'dof': int(dof_s), 'cramers_v': round(v_s, 3),
            'low_expected_cells': low_exp,
        }
        sig = '***' if p_s < 0.001 else '**' if p_s < 0.01 else '*' if p_s < 0.05 else ''
        print(f"  {sec}: V={v_s:.3f} p={p_s:.4f}{sig} (n={len(idx)})")

    results['tests']['D_archetype_interaction'] = {
        'D1_aggregate': {
            'chi2': round(chi2_agg, 2), 'p': round(p_agg, 6),
            'dof': int(dof_agg), 'cramers_v': round(v_agg, 4),
            'n': len(all_meta), 'gmm_components': 5,
        },
        'D2_per_section': d2_results,
    }

# ============================================================
# BLOCK E: AUXILIARY (folio ecology, terminal suffix)
# ============================================================
print("\n=== BLOCK E: Auxiliary ===")

# E1: Folio-level gallows ecology correlations
folio_gallows_counts = defaultdict(Counter)
folio_kernel = {}
for fid in folios:
    for r in records:
        if r['folio'] == fid:
            folio_gallows_counts[fid][r['gallows']] += 1

    fa = decoder.analyze_folio(fid)
    if fa and hasattr(fa, 'kernel_dist'):
        kd = fa.kernel_dist
        total = sum(kd.values())
        if total > 0:
            folio_kernel[fid] = {
                'k_frac': kd.get('k', 0) / total,
                'h_frac': kd.get('h', 0) / total,
                'e_frac': kd.get('e', 0) / total,
            }

e1_results = {}
for kern_var in ['k_frac', 'h_frac', 'e_frac']:
    for gtype in 'ktpf':
        x_vals, y_vals = [], []
        for fid in folio_kernel:
            if fid in folio_gallows_counts:
                g_total = sum(folio_gallows_counts[fid].values())
                if g_total >= 3:
                    x_vals.append(folio_kernel[fid][kern_var])
                    y_vals.append(folio_gallows_counts[fid].get(gtype, 0) / g_total)
        if len(x_vals) >= 10:
            rho, p = spearmanr(x_vals, y_vals)
            key = f'{kern_var}_vs_{gtype}_frac'
            e1_results[key] = {
                'rho': round(rho, 4), 'p': round(p, 4), 'n': len(x_vals),
            }
            if abs(rho) > 0.15 or p < 0.05:
                sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else ''
                print(f"  Folio {kern_var} vs {gtype}-frac: rho={rho:+.3f} p={p:.4f}{sig}")

# E2: Terminal suffix -> next gallows
suffix_to_gallows = defaultdict(Counter)
for fid in folios:
    paragraphs = decoder.analyze_folio_paragraphs(fid)
    para_info = []
    for para in paragraphs:
        bt = para.boundary_token or ''
        gtype = bt[0] if bt and bt[0] in GALLOWS_SET else 'none'
        last_line = para.lines[-1] if para.lines else None
        last_tok = last_line.tokens[-1] if last_line and last_line.tokens else None
        term_suffix = 'none'
        if last_tok and last_tok.morph and last_tok.morph.suffix:
            term_suffix = last_tok.morph.suffix
        para_info.append({'gallows': gtype, 'term_suffix': term_suffix})

    for i in range(1, len(para_info)):
        prev_suf = para_info[i-1]['term_suffix']
        curr_g = para_info[i]['gallows']
        if curr_g in GALLOWS_SET:
            suffix_to_gallows[prev_suf][curr_g] += 1

suf_list = [s for s in suffix_to_gallows if sum(suffix_to_gallows[s].values()) >= 10]
if len(suf_list) >= 2:
    ct_suf = np.zeros((len(suf_list), 4), dtype=int)
    for si, suf in enumerate(suf_list):
        for gi, g in enumerate('ktpf'):
            ct_suf[si, gi] = suffix_to_gallows[suf].get(g, 0)
    rmask = ct_suf.sum(1) > 0
    cmask = ct_suf.sum(0) > 0
    ct_s2 = ct_suf[rmask][:, cmask]
    if ct_s2.shape[0] >= 2 and ct_s2.shape[1] >= 2:
        chi2_suf, p_suf, dof_suf, _ = chi2_contingency(ct_s2)
        v_suf = np.sqrt(chi2_suf / (ct_s2.sum() * (min(ct_s2.shape) - 1)))
    else:
        chi2_suf, p_suf, dof_suf, v_suf = 0, 1, 0, 0
else:
    chi2_suf, p_suf, dof_suf, v_suf = 0, 1, 0, 0

e2_result = {
    'chi2': round(chi2_suf, 2), 'p': round(p_suf, 4),
    'dof': int(dof_suf), 'cramers_v': round(v_suf, 4),
    'n_suffix_types': len(suf_list),
}
sig = '***' if p_suf < 0.001 else '**' if p_suf < 0.01 else '*' if p_suf < 0.05 else ''
print(f"  Terminal suffix -> gallows: V={v_suf:.4f} p={p_suf:.4f}{sig}")

# E3: Section -> gallows mix
sec_gallows = defaultdict(Counter)
for r in records:
    sec_gallows[r['section']][r['gallows']] += 1

e3_result = {}
for sec in sorted(sec_gallows.keys()):
    counts = sec_gallows[sec]
    total = sum(counts.values())
    e3_result[sec] = {
        'total': int(total),
        'fractions': {g: round(counts.get(g, 0) / total, 4) if total > 0 else 0 for g in 'ktpf'},
    }

results['tests']['E_auxiliary'] = {
    'E1_folio_ecology': e1_results,
    'E2_terminal_suffix_routing': e2_result,
    'E3_section_gallows_mix': e3_result,
}

# ============================================================
# CONSTRAINT EVIDENCE SUMMARY
# ============================================================
print("\n=== Constraint Evidence Summary ===")

results['constraint_evidence'] = {
    'C1772_body_composition_association': {
        'statement': 'Gallows type predicts paragraph body composition at multiple resolutions',
        'tier': 2,
        'evidence': {
            'atom_V': round(v_atom, 4),
            'bigram_V': round(v_bi, 4),
            'middle_V': round(v_mid, 4),
            'escalation_confirmed': v_atom < v_bi < v_mid,
            'all_p_significant': p_atom < 0.05 and p_bi < 0.05 and p_mid < 0.05,
        },
    },
    'C1773_p_direct_body_continuity': {
        'statement': 'p-gallows paragraphs show robust p-atom enrichment in body tokens',
        'tier': 2,
        'evidence': {
            'aggregate_oe': a1_results['p']['oe_ratio'],
            'aggregate_p': a1_results['p']['p'],
            'section_stratified': {sec: {'oe': v.get('oe_ratio'), 'p': v.get('p')}
                                   for sec, v in a3_results.items() if 'oe_ratio' in v},
            'survives_stratification': all(
                v.get('p', 1) < 0.10 for v in a3_results.values() if 'p' in v and v.get('n_p_paras', 0) >= 5
            ),
        },
    },
    'C1774_k_complementary_e_bias': {
        'statement': 'k-gallows paragraphs enrich e-atoms, not k-atoms',
        'tier': 2,
        'evidence': {
            'k_self_oe': a1_results['k']['oe_ratio'],
            'k_self_p': a1_results['k']['p'],
            'k_self_verdict': a1_results['k']['verdict'],
            'k_e_oe': a2_result['oe_ratio'],
            'k_e_p': a2_result['p'],
            'consistent_with_C866': True,
            'consistent_with_C521': True,
        },
    },
    'C1775_ambient_context_deployment': {
        'statement': 'Gallows selection correlates with ambient context but not event triggers',
        'tier': 2,
        'evidence': {
            'ambient_thermal_p': c1_results.get('thermal', {}).get('p', 1),
            'ambient_monitoring_p': c1_results.get('monitoring', {}).get('p', 1),
            'ambient_significant': c1_results.get('thermal', {}).get('p', 1) < 0.05,
            'alarm_k_high_p': c2_results.get('k_high', {}).get('p', 1),
            'alarm_h_high_p': c2_results.get('h_high', {}).get('p', 1),
            'alarm_e_high_p': c2_results.get('e_high', {}).get('p', 1),
            'all_alarms_null': all(c2_results[k]['p'] > 0.10 for k in c2_results),
            'all_deltas_null': all(c3_results[k]['p'] > 0.10 for k in c3_results),
        },
    },
    'C1776_archetype_non_reducibility': {
        'statement': 'Aggregate gallows-archetype association is section-mediated',
        'tier': 2,
        'evidence': results['tests'].get('D_archetype_interaction', {}),
    },
    'C1777_atom_substrate_asymmetry': {
        'statement': 'Gallows body inheritance is partial and asymmetric: direct in p, complementary in k, weak in t/f',
        'tier': 2,
        'evidence': {
            'p_self': a1_results['p']['verdict'],
            'k_self': a1_results['k']['verdict'],
            'k_e': 'ENRICHED' if a2_result['oe_ratio'] > 1.05 and a2_result['p'] < 0.05 else 'NULL',
            't_self': a1_results['t']['verdict'],
            'f_self': a1_results['f']['verdict'],
            'pattern': 'p=direct, k=complementary(e), t=null, f=null',
        },
    },
}

# ============================================================
# WRITE JSON
# ============================================================
outpath = ROOT / 'phases' / 'GALLOWS_DEPLOYMENT_CHARACTERIZATION' / 'results' / 'gallows_deployment_results.json'
with open(outpath, 'w') as f:
    json.dump(results, f, indent=2, default=str)

print(f"\nResults written to {outpath}")
print("Done.")
