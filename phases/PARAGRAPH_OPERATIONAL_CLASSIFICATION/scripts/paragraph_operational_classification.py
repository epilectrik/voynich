"""
Phase 447: PARAGRAPH_OPERATIONAL_CLASSIFICATION
Paragraph-level operational profiling using validated gloss categories (C1250).

Primary test (T1): Does paragraph-initial gallows character predict body gloss
profile per C869 functional model? Pre-registered predictions:
  p -> highest THERMAL (main distillation process)
  t -> enriched TRANSITION/FLOW (adjustments)
  k -> THERMAL with e-bias (setup via cool pathway)
  f -> distinctive profile (opener/identification)

Success promotes C869 from Tier 3 to Tier 2.

Supporting tests (T2-T7): paragraph clustering, REGIME prediction, within-folio
complementarity, ordinal trajectory, termination context, apparatus correlation.

All tests use section control (biggest confound risk).
Body only (exclude line 1 header per C840).
Minimum 5 classified body tokens per paragraph.

References: C1250 (gloss coherence), C841 (71.5% gallows-initial),
C865 (gallows folio position), C869 (gallows functional model),
C827 (paragraph operational unit), C840 (header enrichment)
"""

import json
import sys
import time
import functools
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy import stats as sp_stats
from scipy.spatial.distance import jensenshannon

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = ROOT / "phases" / "PARAGRAPH_OPERATIONAL_CLASSIFICATION" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

N_PERM = 1000
P_THRESHOLD = 0.05 / 7  # Bonferroni across 7 tests

GALLOWS_CHARS = {'k', 't', 'p', 'f'}

GLOSS_TO_CATEGORY = {
    'heat': 'THERMAL', 'fire': 'THERMAL', 'cool': 'THERMAL',
    'sustain': 'THERMAL', 'pulse': 'THERMAL', 'steady': 'THERMAL',
    'extended': 'THERMAL', 'deep': 'THERMAL', 'long': 'THERMAL',
    'overnight': 'THERMAL',
    'seal': 'CONTAINMENT', 'hold': 'CONTAINMENT', 'lock': 'CONTAINMENT',
    'bind': 'CONTAINMENT', 'bond': 'CONTAINMENT', 'rigid': 'CONTAINMENT',
    'firm': 'CONTAINMENT', 'dense': 'CONTAINMENT',
    'transfer': 'FLOW', 'gather': 'FLOW', 'discharge': 'FLOW',
    'release': 'FLOW', 'vent': 'FLOW', 'route': 'FLOW',
    'portion': 'FLOW', 'input': 'FLOW', 'intake': 'FLOW',
    'watch': 'MONITORING', 'check': 'MONITORING', 'verify': 'MONITORING',
    'confirm': 'MONITORING', 'scan': 'MONITORING', 'measure': 'MONITORING',
    'control': 'MONITORING', 'regulate': 'MONITORING',
    'work': 'OPERATION', 'operate': 'OPERATION', 'batch': 'OPERATION',
    'pound': 'OPERATION', 'strip': 'OPERATION', 'exact': 'OPERATION',
    'precise': 'OPERATION', 'hard': 'OPERATION', 'wide': 'OPERATION',
    'start': 'TRANSITION', 'open': 'TRANSITION', 'close': 'TRANSITION',
    'end': 'TRANSITION', 'finish': 'TRANSITION', 'complete': 'TRANSITION',
    'finalize': 'TRANSITION', 'yield': 'TRANSITION', 'final': 'TRANSITION',
    'stand': 'TRANSITION', 'settle': 'TRANSITION', 'set': 'TRANSITION',
    'frame': 'STAGING', 'step': 'STAGING', 'iterate': 'STAGING',
    'sequence': 'STAGING', 'continue': 'STAGING', 'repeat': 'STAGING',
    'cycle': 'STAGING', 'loop': 'STAGING', 'path': 'STAGING',
    'mark': 'MARKING', 'flag': 'MARKING', 'note': 'MARKING',
    'pause': 'MARKING', 'diagram': 'MARKING', 'hazard': 'MARKING',
    'danger': 'MARKING', 'link': 'MARKING', 'adjust': 'MARKING',
}

ALL_CATEGORIES = sorted(set(GLOSS_TO_CATEGORY.values()))
CAT_IDX = {c: i for i, c in enumerate(ALL_CATEGORIES)}
N_CATS = len(ALL_CATEGORIES)


# ── Data loading ─────────────────────────────────────────────────────

def load_data():
    tx = Transcript()
    morph = Morphology()

    with open(ROOT / 'data' / 'middle_dictionary.json', encoding='utf-8') as f:
        mid_dict = json.load(f)['middles']
    with open(ROOT / 'data' / 'regime_folio_mapping.json', encoding='utf-8') as f:
        regime_map = {fol: v['regime']
                      for fol, v in json.load(f)['regime_assignments'].items()}

    app_path = (ROOT / 'phases' / 'APPARATUS_VOCABULARY_CLASSIFICATION'
                / 'results' / 'apparatus_profiles.json')
    with open(app_path, encoding='utf-8') as f:
        app_raw = json.load(f)
    folio_app_scores = app_raw.get('folio_scores', {})

    raw_tokens = [t for t in tx.currier_b()
                  if t.word.strip() and '*' not in t.word]

    tokens = []
    for token in raw_tokens:
        w = token.word.strip()
        m = morph.extract(w)
        mid = m.middle
        gloss = None
        if mid and mid in mid_dict:
            gloss = mid_dict[mid].get('gloss')
        gloss_cat = GLOSS_TO_CATEGORY.get(gloss) if gloss else None

        tokens.append({
            'word': w, 'folio': token.folio, 'line': token.line,
            'section': token.section,
            'par_initial': token.par_initial, 'par_final': token.par_final,
            'prefix': m.prefix, 'middle': mid, 'suffix': m.suffix,
            'gloss': gloss, 'gloss_category': gloss_cat,
            'regime': regime_map.get(token.folio, 'UNK'),
        })

    return tokens, folio_app_scores


def build_paragraphs(tokens, min_body_classified=5):
    """Group tokens into paragraphs. Return list of paragraph dicts."""
    # Group by folio, preserving order
    folio_tokens = defaultdict(list)
    for t in tokens:
        folio_tokens[t['folio']].append(t)

    paragraphs = []
    for folio in sorted(folio_tokens.keys()):
        toks = folio_tokens[folio]
        current = []
        par_idx = 0
        for t in toks:
            if t['par_initial'] and current:
                _emit_paragraph(paragraphs, folio, par_idx, current, min_body_classified)
                par_idx += 1
                current = [t]
            else:
                current.append(t)
        if current:
            _emit_paragraph(paragraphs, folio, par_idx, current, min_body_classified)

    return paragraphs


def _emit_paragraph(paragraphs, folio, par_idx, tokens, min_body):
    """Build a paragraph dict from its tokens."""
    if not tokens:
        return

    first_word = tokens[0]['word']
    gallows = first_word[0] if first_word and first_word[0] in GALLOWS_CHARS else None

    # Header = line 1 (same line as first token); body = all other lines
    header_line = tokens[0]['line']
    header_tokens = [t for t in tokens if t['line'] == header_line]
    body_tokens = [t for t in tokens if t['line'] != header_line]

    # Body gloss profile
    body_cats = [t['gloss_category'] for t in body_tokens if t['gloss_category']]
    if len(body_cats) < min_body:
        return

    cat_counts = Counter(body_cats)
    total = len(body_cats)
    profile = np.zeros(N_CATS)
    for c, n in cat_counts.items():
        profile[CAT_IDX[c]] = n / total

    # Check if last token has -am suffix
    last_suffix = tokens[-1].get('suffix', '')
    has_am = last_suffix in ('am', 'om')

    paragraphs.append({
        'folio': folio,
        'par_idx': par_idx,
        'section': tokens[0]['section'],
        'regime': tokens[0]['regime'],
        'gallows': gallows,
        'first_word': first_word,
        'n_tokens': len(tokens),
        'n_body_tokens': len(body_tokens),
        'n_body_classified': total,
        'n_lines': len(set(t['line'] for t in tokens)),
        'n_body_lines': len(set(t['line'] for t in body_tokens)),
        'profile': profile,
        'cat_counts': dict(cat_counts),
        'has_am': has_am,
        'body_tokens': body_tokens,
    })


def profile_to_dict(profile):
    return {ALL_CATEGORIES[i]: round(float(profile[i]), 4) for i in range(N_CATS)}


# ── T1: Gallows-Gloss Prediction ─────────────────────────────────────

def test_t1_gallows_gloss(paragraphs):
    """
    Pre-registered from C869: gallows type predicts body gloss profile.
    Two-stage null: shuffle gallows within section, then test residuals.
    """
    gal_paras = [p for p in paragraphs if p['gallows']]
    if len(gal_paras) < 50:
        return {'status': 'SKIP', 'reason': f'Only {len(gal_paras)} gallows paragraphs'}

    gallows_types = sorted(set(p['gallows'] for p in gal_paras))
    sections = sorted(set(p['section'] for p in gal_paras))

    # Mean profile per gallows type
    gal_profiles = {}
    gal_counts = Counter()
    for g in gallows_types:
        gp = [p['profile'] for p in gal_paras if p['gallows'] == g]
        gal_profiles[g] = np.mean(gp, axis=0)
        gal_counts[g] = len(gp)

    # Stage 1: Chi-square on gallows x category (token-weighted)
    gal_cat_table = np.zeros((len(gallows_types), N_CATS))
    g_idx = {g: i for i, g in enumerate(gallows_types)}
    for p in gal_paras:
        for c, n in p['cat_counts'].items():
            gal_cat_table[g_idx[p['gallows']], CAT_IDX[c]] += n

    # Remove zero columns
    col_ok = gal_cat_table.sum(axis=0) > 0
    row_ok = gal_cat_table.sum(axis=1) > 0
    clean = gal_cat_table[row_ok][:, col_ok]
    if clean.shape[0] < 2 or clean.shape[1] < 2:
        return {'status': 'SKIP', 'reason': 'Degenerate table'}

    real_chi2, _, _, _ = sp_stats.chi2_contingency(clean)
    n_total = clean.sum()
    min_dim = min(clean.shape) - 1
    cramers_v = np.sqrt(real_chi2 / (n_total * min_dim)) if n_total * min_dim > 0 else 0

    # Stage 1 null: shuffle gallows within section
    section_indices = defaultdict(list)
    for i, p in enumerate(gal_paras):
        section_indices[p['section']].append(i)

    print("  Stage 1: within-section gallows shuffle...")
    rng = np.random.default_rng(70)
    shuf_chi2s = []
    gallows_arr = [p['gallows'] for p in gal_paras]
    for _ in range(N_PERM):
        shuf_gal = list(gallows_arr)
        for sec, idxs in section_indices.items():
            sec_gals = [shuf_gal[i] for i in idxs]
            rng.shuffle(sec_gals)
            for i, idx in enumerate(idxs):
                shuf_gal[idx] = sec_gals[i]
        # Build shuffled table
        st = np.zeros_like(gal_cat_table)
        for i, p in enumerate(gal_paras):
            for c, n in p['cat_counts'].items():
                sg = shuf_gal[i]
                if sg in g_idx:
                    st[g_idx[sg], CAT_IDX[c]] += n
        st_c = st[st.sum(axis=1) > 0][:, st.sum(axis=0) > 0]
        if st_c.shape[0] >= 2 and st_c.shape[1] >= 2:
            shuf_chi2s.append(sp_stats.chi2_contingency(st_c)[0])

    s1_arr = np.array(shuf_chi2s) if shuf_chi2s else np.array([0])
    p_stage1 = float(np.mean(s1_arr >= real_chi2))

    # Stage 2: Section-residual test
    # Compute section mean profiles, subtract, test residual gallows effect
    sec_profiles = {}
    for sec in sections:
        sp = [p['profile'] for p in gal_paras if p['section'] == sec]
        sec_profiles[sec] = np.mean(sp, axis=0) if sp else np.zeros(N_CATS)

    residuals_by_gal = defaultdict(list)
    for p in gal_paras:
        resid = p['profile'] - sec_profiles[p['section']]
        residuals_by_gal[p['gallows']].append(resid)

    # MANOVA-like: compute between-group variance on residuals
    all_resid = np.array([p['profile'] - sec_profiles[p['section']] for p in gal_paras])
    grand_mean = all_resid.mean(axis=0)
    ss_between = 0
    for g in gallows_types:
        gresid = np.array(residuals_by_gal[g])
        if len(gresid) > 0:
            g_mean = gresid.mean(axis=0)
            ss_between += len(gresid) * np.sum((g_mean - grand_mean) ** 2)
    ss_total = np.sum((all_resid - grand_mean) ** 2) * len(all_resid)
    eta_sq = ss_between / ss_total if ss_total > 0 else 0

    # Stage 2 null: shuffle gallows within section on residuals
    print("  Stage 2: section-residual test...")
    shuf_etas = []
    for _ in range(N_PERM):
        shuf_gal = list(gallows_arr)
        for sec, idxs in section_indices.items():
            sec_gals = [shuf_gal[i] for i in idxs]
            rng.shuffle(sec_gals)
            for i, idx in enumerate(idxs):
                shuf_gal[idx] = sec_gals[i]
        shuf_by_gal = defaultdict(list)
        for i, p in enumerate(gal_paras):
            resid = p['profile'] - sec_profiles[p['section']]
            shuf_by_gal[shuf_gal[i]].append(resid)
        ss_b = 0
        for g in gallows_types:
            gr = np.array(shuf_by_gal.get(g, []))
            if len(gr) > 0:
                ss_b += len(gr) * np.sum((gr.mean(axis=0) - grand_mean) ** 2)
        shuf_etas.append(ss_b / ss_total if ss_total > 0 else 0)

    s2_arr = np.array(shuf_etas)
    p_stage2 = float(np.mean(s2_arr >= eta_sq))

    # Directional prediction tests (4 predictions from C869)
    predictions = {}

    # P1: p has highest THERMAL
    thermal_idx = CAT_IDX['THERMAL']
    thermal_by_gal = {g: float(gal_profiles[g][thermal_idx]) for g in gallows_types}
    p_is_max_thermal = (max(thermal_by_gal, key=thermal_by_gal.get) == 'p')
    predictions['p_max_thermal'] = {
        'predicted': True, 'actual': p_is_max_thermal,
        'thermal_fractions': thermal_by_gal,
    }

    # P2: t enriched in TRANSITION or FLOW
    trans_idx = CAT_IDX['TRANSITION']
    flow_idx = CAT_IDX['FLOW']
    t_trans_flow = float(gal_profiles.get('t', np.zeros(N_CATS))[trans_idx] +
                         gal_profiles.get('t', np.zeros(N_CATS))[flow_idx])
    p_trans_flow = float(gal_profiles.get('p', np.zeros(N_CATS))[trans_idx] +
                         gal_profiles.get('p', np.zeros(N_CATS))[flow_idx])
    predictions['t_enriched_trans_flow'] = {
        'predicted': True,
        'actual': t_trans_flow > p_trans_flow,
        't_trans_flow': round(t_trans_flow, 4),
        'p_trans_flow': round(p_trans_flow, 4),
    }

    # P3: k has THERMAL with e-bias (check if k's THERMAL is not the highest,
    # but k has more CONTAINMENT/TRANSITION than p -- indicating e-pathway)
    k_profile = gal_profiles.get('k', np.zeros(N_CATS))
    p_profile = gal_profiles.get('p', np.zeros(N_CATS))
    # e-bias: check if k has lower THERMAL than p but higher non-THERMAL categories
    # OR: check if k-paragraphs have distinctive profile
    k_thermal = float(k_profile[thermal_idx])
    predictions['k_thermal_with_bias'] = {
        'predicted': True,
        'actual': k_thermal > 0.15,  # k should still be thermal-oriented
        'k_thermal': round(k_thermal, 4),
        'k_profile': profile_to_dict(k_profile),
    }

    # P4: f has distinctive profile (highest JSD from mean)
    mean_profile = np.mean([gal_profiles[g] for g in gallows_types], axis=0)
    jsd_from_mean = {}
    for g in gallows_types:
        # Add small epsilon for JSD computation
        p1 = gal_profiles[g] + 1e-10
        p2 = mean_profile + 1e-10
        p1 /= p1.sum()
        p2 /= p2.sum()
        jsd_from_mean[g] = float(jensenshannon(p1, p2))
    f_most_distinctive = (max(jsd_from_mean, key=jsd_from_mean.get) == 'f') if 'f' in jsd_from_mean else False
    predictions['f_distinctive'] = {
        'predicted': True,
        'actual': f_most_distinctive,
        'jsd_from_mean': {g: round(v, 4) for g, v in jsd_from_mean.items()},
        'f_profile': profile_to_dict(gal_profiles.get('f', np.zeros(N_CATS))),
    }

    correct = sum(1 for v in predictions.values() if v['actual'])

    # Overall status: both stages must pass for tier promotion
    both_pass = p_stage1 < P_THRESHOLD and p_stage2 < P_THRESHOLD
    status = 'PASS' if both_pass else 'FAIL'

    return {
        'status': status,
        'chi2': round(float(real_chi2), 1),
        'cramers_v': round(float(cramers_v), 4),
        'p_stage1': p_stage1,
        'p_stage2': p_stage2,
        'eta_squared_residual': round(float(eta_sq), 4),
        'n_gallows_paragraphs': len(gal_paras),
        'gallows_counts': dict(gal_counts),
        'gallows_profiles': {g: profile_to_dict(gal_profiles[g]) for g in gallows_types},
        'directional_predictions': predictions,
        'correct_predictions': correct,
        'tier_promotion': correct >= 3 and both_pass,
    }


# ── T2: Paragraph Gloss Clustering ───────────────────────────────────

def test_t2_clustering(paragraphs):
    """Do paragraphs form discrete operational types?"""
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score

    X = np.array([p['profile'] for p in paragraphs])
    if len(X) < 30:
        return {'status': 'SKIP', 'reason': 'Too few paragraphs'}

    best_k = 2
    best_sil = -1
    sils = {}
    for k in range(2, min(9, len(X))):
        km = KMeans(n_clusters=k, n_init=10, random_state=42)
        labels = km.fit_predict(X)
        s = silhouette_score(X, labels)
        sils[k] = round(float(s), 4)
        if s > best_sil:
            best_sil = s
            best_k = k

    # Null: permute tokens within folio to create shuffled paragraph profiles
    print("  Running permutations...")
    rng = np.random.default_rng(71)

    # Build folio token pools
    folio_cats = defaultdict(list)
    for p in paragraphs:
        for t in p.get('body_tokens', []):
            if t['gloss_category']:
                folio_cats[p['folio']].append(t['gloss_category'])

    shuf_sils = []
    for _ in range(N_PERM):
        # Shuffle categories within each folio
        for fol in folio_cats:
            rng.shuffle(folio_cats[fol])
        # Rebuild paragraph profiles from shuffled pools
        folio_idx = defaultdict(int)
        X_shuf = np.zeros_like(X)
        for pi, p in enumerate(paragraphs):
            fol = p['folio']
            n_need = p['n_body_classified']
            start = folio_idx[fol]
            pool = folio_cats[fol]
            cats = pool[start:start + n_need]
            folio_idx[fol] = start + n_need
            cc = Counter(cats)
            total = len(cats)
            if total > 0:
                for c, n in cc.items():
                    X_shuf[pi, CAT_IDX[c]] = n / total
        km_s = KMeans(n_clusters=best_k, n_init=5, random_state=42)
        lab_s = km_s.fit_predict(X_shuf)
        if len(set(lab_s)) >= 2:
            shuf_sils.append(silhouette_score(X_shuf, lab_s))

    shuf_arr = np.array(shuf_sils) if shuf_sils else np.array([0])
    p_emp = float(np.mean(shuf_arr >= best_sil))

    discrete = best_sil > 0.25
    return {
        'status': 'PASS' if p_emp < P_THRESHOLD and discrete else 'FAIL',
        'best_k': best_k,
        'best_silhouette': round(float(best_sil), 4),
        'all_silhouettes': sils,
        'discrete': discrete,
        'p_value_empirical': p_emp,
        'shuffled_sil_mean': round(float(shuf_arr.mean()), 4),
        'comparison': 'C678 line-level silhouette=0.100',
        'n_paragraphs': len(paragraphs),
    }


# ── T3: Gloss-REGIME Beyond Section ──────────────────────────────────

def test_t3_regime(paragraphs):
    """Does gloss profile predict REGIME beyond section?"""
    valid = [p for p in paragraphs if p['regime'] != 'UNK']
    if len(valid) < 50:
        return {'status': 'SKIP', 'reason': 'Too few paragraphs with REGIME'}

    sections = sorted(set(p['section'] for p in valid))
    regimes = sorted(set(p['regime'] for p in valid))

    # Section-only baseline: majority class per section
    sec_regime = defaultdict(Counter)
    for p in valid:
        sec_regime[p['section']][p['regime']] += 1

    baseline_correct = 0
    for p in valid:
        majority = sec_regime[p['section']].most_common(1)[0][0]
        if majority == p['regime']:
            baseline_correct += 1
    baseline_acc = baseline_correct / len(valid)

    # Gloss + section: nearest centroid per (section, regime) group
    group_profiles = defaultdict(list)
    for p in valid:
        group_profiles[(p['section'], p['regime'])].append(p['profile'])
    centroids = {k: np.mean(v, axis=0) for k, v in group_profiles.items()}

    gloss_correct = 0
    for p in valid:
        sec = p['section']
        best_r = None
        best_dist = float('inf')
        for r in regimes:
            key = (sec, r)
            if key in centroids:
                d = np.sum((p['profile'] - centroids[key]) ** 2)
                if d < best_dist:
                    best_dist = d
                    best_r = r
        if best_r == p['regime']:
            gloss_correct += 1
    gloss_acc = gloss_correct / len(valid)
    increment = gloss_acc - baseline_acc

    # Null: shuffle REGIME within section
    print("  Running permutations...")
    rng = np.random.default_rng(72)
    section_indices = defaultdict(list)
    for i, p in enumerate(valid):
        section_indices[p['section']].append(i)

    shuf_increments = []
    regimes_arr = [p['regime'] for p in valid]
    for _ in range(N_PERM):
        shuf_reg = list(regimes_arr)
        for sec, idxs in section_indices.items():
            sec_regs = [shuf_reg[i] for i in idxs]
            rng.shuffle(sec_regs)
            for i, idx in enumerate(idxs):
                shuf_reg[idx] = sec_regs[i]
        # Rebuild centroids
        sg = defaultdict(list)
        for i, p in enumerate(valid):
            sg[(p['section'], shuf_reg[i])].append(p['profile'])
        sc = {k: np.mean(v, axis=0) for k, v in sg.items()}
        s_correct = 0
        for i, p in enumerate(valid):
            best_r = None
            best_d = float('inf')
            for r in regimes:
                key = (p['section'], r)
                if key in sc:
                    d = np.sum((p['profile'] - sc[key]) ** 2)
                    if d < best_d:
                        best_d = d
                        best_r = r
            if best_r == shuf_reg[i]:
                s_correct += 1
        shuf_increments.append(s_correct / len(valid) - baseline_acc)

    shuf_arr = np.array(shuf_increments)
    p_emp = float(np.mean(shuf_arr >= increment))

    return {
        'status': 'PASS' if p_emp < P_THRESHOLD and increment > 0.05 else 'FAIL',
        'baseline_accuracy': round(baseline_acc, 4),
        'gloss_accuracy': round(gloss_acc, 4),
        'increment': round(increment, 4),
        'p_value_empirical': p_emp,
        'n_paragraphs': len(valid),
    }


# ── T4: Within-Folio Complementarity ─────────────────────────────────

def test_t4_complementarity(paragraphs):
    """Do paragraphs within a folio diversify their gloss profiles?"""
    folio_paras = defaultdict(list)
    for p in paragraphs:
        folio_paras[p['folio']].append(p)

    # Only folios with 2+ paragraphs
    multi = {f: ps for f, ps in folio_paras.items() if len(ps) >= 2}
    if len(multi) < 10:
        return {'status': 'SKIP', 'reason': f'Only {len(multi)} multi-paragraph folios'}

    def mean_pairwise_jsd(para_list):
        jsds = []
        for i in range(len(para_list)):
            for j in range(i + 1, len(para_list)):
                p1 = para_list[i]['profile'] + 1e-10
                p2 = para_list[j]['profile'] + 1e-10
                p1 /= p1.sum()
                p2 /= p2.sum()
                jsds.append(jensenshannon(p1, p2))
        return np.mean(jsds) if jsds else 0

    # Within-folio JSD
    within_jsds = []
    for f, ps in multi.items():
        within_jsds.append(mean_pairwise_jsd(ps))
    real_within = np.mean(within_jsds)

    # Between-folio JSD (within same section)
    section_paras = defaultdict(list)
    for p in paragraphs:
        section_paras[p['section']].append(p)

    between_jsds = []
    rng_b = np.random.default_rng(99)
    for sec, sps in section_paras.items():
        if len(sps) < 4:
            continue
        for _ in range(200):
            i, j = rng_b.choice(len(sps), 2, replace=False)
            if sps[i]['folio'] != sps[j]['folio']:
                p1 = sps[i]['profile'] + 1e-10
                p2 = sps[j]['profile'] + 1e-10
                p1 /= p1.sum()
                p2 /= p2.sum()
                between_jsds.append(jensenshannon(p1, p2))
    real_between = np.mean(between_jsds) if between_jsds else 0

    delta = real_within - real_between  # positive = diversification, negative = specialization

    # Null: permute paragraph-folio within section
    print("  Running permutations...")
    rng = np.random.default_rng(73)
    shuf_deltas = []
    for _ in range(N_PERM):
        # Shuffle paragraph folio assignments within section
        shuf_paras = list(paragraphs)
        for sec, idxs_list in section_paras.items():
            folios = [p['folio'] for p in idxs_list]
            rng.shuffle(folios)
            for i, p in enumerate(idxs_list):
                p['_shuf_folio'] = folios[i]

        shuf_multi = defaultdict(list)
        for p in shuf_paras:
            sf = p.get('_shuf_folio', p['folio'])
            shuf_multi[sf].append(p)

        sw_jsds = []
        for f, ps in shuf_multi.items():
            if len(ps) >= 2:
                sw_jsds.append(mean_pairwise_jsd(ps))
        shuf_within = np.mean(sw_jsds) if sw_jsds else 0
        shuf_deltas.append(shuf_within - real_between)

    shuf_arr = np.array(shuf_deltas)
    # Two-sided: is real delta significantly different from null?
    p_emp = float(np.mean(np.abs(shuf_arr) >= abs(delta)))

    return {
        'status': 'PASS' if p_emp < P_THRESHOLD else 'FAIL',
        'within_folio_jsd': round(float(real_within), 4),
        'between_folio_jsd': round(float(real_between), 4),
        'delta': round(float(delta), 4),
        'direction': 'diversification' if delta > 0 else 'specialization',
        'p_value_empirical': p_emp,
        'n_multi_folios': len(multi),
    }


# ── T5: Ordinal Trajectory ───────────────────────────────────────────

def test_t5_ordinal(paragraphs):
    """Does gloss profile shift across paragraph ordinals?"""
    folio_paras = defaultdict(list)
    for p in paragraphs:
        folio_paras[p['folio']].append(p)

    # Assign ordinals
    for f, ps in folio_paras.items():
        for i, p in enumerate(ps):
            p['ordinal'] = i

    # Only use paragraphs from folios with 3+ paragraphs
    valid = [p for p in paragraphs if len(folio_paras[p['folio']]) >= 3]
    if len(valid) < 50:
        return {'status': 'SKIP', 'reason': 'Too few paragraphs'}

    # Max ordinal to consider (enough data)
    max_ord = max(p['ordinal'] for p in valid)
    ordinals = [p['ordinal'] for p in valid]

    # Spearman per category
    rho_results = {}
    for cat in ALL_CATEGORIES:
        ci = CAT_IDX[cat]
        vals = [p['profile'][ci] for p in valid]
        rho, p_val = sp_stats.spearmanr(ordinals, vals)
        rho_results[cat] = {'rho': round(float(rho), 4), 'p': float(p_val)}

    # Null: permute ordinals within folio
    print("  Running permutations...")
    rng = np.random.default_rng(74)
    max_rho_real = max(abs(v['rho']) for v in rho_results.values())

    shuf_max_rhos = []
    for _ in range(N_PERM):
        shuf_ords = list(ordinals)
        # Shuffle ordinals within folio
        folio_idx_map = defaultdict(list)
        for i, p in enumerate(valid):
            folio_idx_map[p['folio']].append(i)
        for f, idxs in folio_idx_map.items():
            ords = [shuf_ords[i] for i in idxs]
            rng.shuffle(ords)
            for i, idx in enumerate(idxs):
                shuf_ords[idx] = ords[i]
        # Max |rho| across categories
        max_r = 0
        for cat in ALL_CATEGORIES:
            ci = CAT_IDX[cat]
            vals = [valid[i]['profile'][ci] for i in range(len(valid))]
            r, _ = sp_stats.spearmanr(shuf_ords, vals)
            max_r = max(max_r, abs(r))
        shuf_max_rhos.append(max_r)

    shuf_arr = np.array(shuf_max_rhos)
    p_emp = float(np.mean(shuf_arr >= max_rho_real))

    return {
        'status': 'PASS' if p_emp < P_THRESHOLD and max_rho_real > 0.3 else 'FAIL',
        'max_abs_rho': round(float(max_rho_real), 4),
        'category_rhos': rho_results,
        'p_value_empirical': p_emp,
        'n_paragraphs': len(valid),
    }


# ── T6: Termination Context ──────────────────────────────────────────

def test_t6_termination(paragraphs):
    """Does body gloss profile predict -am paragraph termination?"""
    am_paras = [p for p in paragraphs if p['has_am']]
    non_am = [p for p in paragraphs if not p['has_am']]

    if len(am_paras) < 10:
        return {'status': 'SKIP', 'reason': f'Only {len(am_paras)} -am paragraphs'}

    am_profile = np.mean([p['profile'] for p in am_paras], axis=0)
    non_am_profile = np.mean([p['profile'] for p in non_am], axis=0)

    # Per-category KW test
    cat_tests = {}
    for cat in ALL_CATEGORIES:
        ci = CAT_IDX[cat]
        am_vals = [p['profile'][ci] for p in am_paras]
        non_vals = [p['profile'][ci] for p in non_am]
        if len(set(am_vals)) > 1 or len(set(non_vals)) > 1:
            stat, pval = sp_stats.mannwhitneyu(am_vals, non_vals, alternative='two-sided')
            cat_tests[cat] = {
                'am_mean': round(float(np.mean(am_vals)), 4),
                'non_am_mean': round(float(np.mean(non_vals)), 4),
                'u_stat': float(stat),
                'p_value': float(pval),
            }

    # Overall: JSD between am and non-am profiles
    p1 = am_profile + 1e-10
    p2 = non_am_profile + 1e-10
    p1 /= p1.sum()
    p2 /= p2.sum()
    real_jsd = float(jensenshannon(p1, p2))

    # Null: shuffle am labels within section
    print("  Running permutations...")
    rng = np.random.default_rng(75)
    section_indices = defaultdict(list)
    for i, p in enumerate(paragraphs):
        section_indices[p['section']].append(i)

    am_labels = [p['has_am'] for p in paragraphs]
    shuf_jsds = []
    for _ in range(N_PERM):
        shuf_am = list(am_labels)
        for sec, idxs in section_indices.items():
            sec_labs = [shuf_am[i] for i in idxs]
            rng.shuffle(sec_labs)
            for i, idx in enumerate(idxs):
                shuf_am[idx] = sec_labs[i]
        s_am = np.mean([paragraphs[i]['profile'] for i in range(len(paragraphs))
                        if shuf_am[i]], axis=0)
        s_non = np.mean([paragraphs[i]['profile'] for i in range(len(paragraphs))
                         if not shuf_am[i]], axis=0)
        sp1 = s_am + 1e-10
        sp2 = s_non + 1e-10
        sp1 /= sp1.sum()
        sp2 /= sp2.sum()
        shuf_jsds.append(jensenshannon(sp1, sp2))

    shuf_arr = np.array(shuf_jsds)
    p_emp = float(np.mean(shuf_arr >= real_jsd))

    sig_cats = [c for c, v in cat_tests.items() if v['p_value'] < 0.05]

    return {
        'status': 'PASS' if p_emp < P_THRESHOLD else 'FAIL',
        'jsd_am_vs_non': round(real_jsd, 4),
        'p_value_empirical': p_emp,
        'n_am': len(am_paras),
        'n_non_am': len(non_am),
        'am_profile': profile_to_dict(am_profile),
        'non_am_profile': profile_to_dict(non_am_profile),
        'significant_categories': sig_cats,
        'category_tests': cat_tests,
    }


# ── T7: Apparatus Correlation ────────────────────────────────────────

def test_t7_apparatus(paragraphs, folio_app_scores):
    """Does paragraph-level gloss-apparatus correlation match token-level?"""
    thermal_idx = CAT_IDX['THERMAL']

    valid = [(p, folio_app_scores[p['folio']])
             for p in paragraphs
             if p['folio'] in folio_app_scores]
    if len(valid) < 30:
        return {'status': 'SKIP', 'reason': f'Only {len(valid)} paragraphs with apparatus'}

    thermal_fracs = [p['profile'][thermal_idx] for p, _ in valid]
    dist_scores = [s.get('DISTILLATION', 0) for _, s in valid]

    real_rho, real_p = sp_stats.spearmanr(dist_scores, thermal_fracs)

    # Null: shuffle paragraphs within section
    print("  Running permutations...")
    rng = np.random.default_rng(76)
    section_indices = defaultdict(list)
    for i, (p, _) in enumerate(valid):
        section_indices[p['section']].append(i)

    shuf_rhos = []
    for _ in range(N_PERM):
        shuf_thermal = list(thermal_fracs)
        for sec, idxs in section_indices.items():
            sec_vals = [shuf_thermal[i] for i in idxs]
            rng.shuffle(sec_vals)
            for i, idx in enumerate(idxs):
                shuf_thermal[idx] = sec_vals[i]
        r, _ = sp_stats.spearmanr(dist_scores, shuf_thermal)
        shuf_rhos.append(r)

    shuf_arr = np.array(shuf_rhos)
    p_emp = float(np.mean(shuf_arr >= real_rho))

    return {
        'status': 'PASS' if p_emp < P_THRESHOLD else 'FAIL',
        'rho_paragraph': round(float(real_rho), 4),
        'p_parametric': float(real_p),
        'p_value_empirical': p_emp,
        'rho_token_level': 0.758,  # C1250 T6 reference
        'n_paragraphs': len(valid),
        'shuffled_rho_mean': round(float(shuf_arr.mean()), 4),
    }


# ── Synthesis ────────────────────────────────────────────────────────

def synthesize(results):
    pc = sum(1 for r in results.values() if r.get('status') == 'PASS')
    fc = sum(1 for r in results.values() if r.get('status') == 'FAIL')
    sc = sum(1 for r in results.values() if r.get('status') == 'SKIP')
    tr = pc + fc
    if tr == 0:
        verdict = 'NO_DATA'
    elif pc >= 5:
        verdict = 'STRONG'
    elif pc >= 3:
        verdict = 'MODERATE'
    elif pc >= 1:
        verdict = 'WEAK'
    else:
        verdict = 'NULL'
    return {
        'pass_count': pc, 'fail_count': fc, 'skip_count': sc,
        'total_tests': 7, 'tests_run': tr, 'verdict': verdict,
        'summary': f'{pc}/{tr} tests pass (Bonferroni p<{P_THRESHOLD:.4f}), {sc} skipped',
    }


# ── Main ─────────────────────────────────────────────────────────────

def main():
    t0 = time.time()
    print("=" * 60)
    print("PARAGRAPH OPERATIONAL CLASSIFICATION")
    print("Paragraph-level profiling with validated gloss categories")
    print("=" * 60)

    print("\n[1/8] Loading data...")
    tokens, folio_app_scores = load_data()
    paragraphs = build_paragraphs(tokens, min_body_classified=5)

    n_gal = sum(1 for p in paragraphs if p['gallows'])
    sections = Counter(p['section'] for p in paragraphs)
    gal_counts = Counter(p['gallows'] for p in paragraphs if p['gallows'])
    print(f"  {len(tokens)} B tokens -> {len(paragraphs)} paragraphs (min 5 body classified)")
    print(f"  {n_gal} gallows-initial ({100*n_gal/len(paragraphs):.0f}%)")
    for g in sorted(gal_counts):
        print(f"    {g}: {gal_counts[g]}")
    print(f"  Sections: {dict(sections)}")

    results = {}

    print("\n[2/8] T1: Gallows-Gloss Prediction (PRIMARY, C869 promotion)...")
    results['T1_gallows_gloss'] = test_t1_gallows_gloss(paragraphs)
    r = results['T1_gallows_gloss']
    print(f"  -> {r['status']} (V={r.get('cramers_v', 'N/A')}, "
          f"p1={r.get('p_stage1', 'N/A'):.4f}, p2={r.get('p_stage2', 'N/A'):.4f}, "
          f"eta2={r.get('eta_squared_residual', 'N/A')}, "
          f"predictions={r.get('correct_predictions', 'N/A')}/4)")

    print("\n[3/8] T2: Paragraph Gloss Clustering...")
    results['T2_clustering'] = test_t2_clustering(paragraphs)
    r = results['T2_clustering']
    print(f"  -> {r['status']} (best_k={r.get('best_k', 'N/A')}, "
          f"sil={r.get('best_silhouette', 'N/A')}, "
          f"p={r.get('p_value_empirical', 'N/A'):.4f})")

    print("\n[4/8] T3: Gloss-REGIME Beyond Section...")
    results['T3_regime'] = test_t3_regime(paragraphs)
    r = results['T3_regime']
    print(f"  -> {r['status']} (baseline={r.get('baseline_accuracy', 'N/A')}, "
          f"gloss={r.get('gloss_accuracy', 'N/A')}, "
          f"incr={r.get('increment', 'N/A')}, p={r.get('p_value_empirical', 'N/A'):.4f})")

    print("\n[5/8] T4: Within-Folio Complementarity...")
    results['T4_complementarity'] = test_t4_complementarity(paragraphs)
    r = results['T4_complementarity']
    print(f"  -> {r['status']} (within={r.get('within_folio_jsd', 'N/A')}, "
          f"between={r.get('between_folio_jsd', 'N/A')}, "
          f"delta={r.get('delta', 'N/A')}, p={r.get('p_value_empirical', 'N/A'):.4f})")

    print("\n[6/8] T5: Ordinal Trajectory...")
    results['T5_ordinal'] = test_t5_ordinal(paragraphs)
    r = results['T5_ordinal']
    print(f"  -> {r['status']} (max|rho|={r.get('max_abs_rho', 'N/A')}, "
          f"p={r.get('p_value_empirical', 'N/A'):.4f})")

    print("\n[7/8] T6: Termination Context (-am)...")
    results['T6_termination'] = test_t6_termination(paragraphs)
    r = results['T6_termination']
    print(f"  -> {r['status']} (JSD={r.get('jsd_am_vs_non', 'N/A')}, "
          f"n_am={r.get('n_am', 'N/A')}, p={r.get('p_value_empirical', 'N/A'):.4f})")

    print("\n[8/8] T7: Apparatus Correlation...")
    results['T7_apparatus'] = test_t7_apparatus(paragraphs, folio_app_scores)
    r = results['T7_apparatus']
    print(f"  -> {r['status']} (rho_par={r.get('rho_paragraph', 'N/A')}, "
          f"rho_tok=0.758, p={r.get('p_value_empirical', 'N/A'):.4f})")

    syn = synthesize(results)
    elapsed = time.time() - t0

    output = {
        '_metadata': {
            'phase': 'PARAGRAPH_OPERATIONAL_CLASSIFICATION',
            'phase_number': 447,
            'description': 'Paragraph-level operational profiling with validated gloss categories',
            'primary_test': 'T1: gallows-gloss prediction (C869 tier promotion)',
            'n_tokens': len(tokens),
            'n_paragraphs': len(paragraphs),
            'min_body_classified': 5,
            'n_permutations': N_PERM,
            'p_threshold_bonferroni': round(P_THRESHOLD, 4),
            'elapsed_seconds': round(elapsed, 1),
        },
        'synthesis': syn,
        'tests': results,
    }

    out_path = RESULTS_DIR / 'paragraph_operational_classification.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\n{'=' * 60}")
    print(f"VERDICT: {syn['verdict']}")
    print(f"  {syn['summary']}")
    t1 = results.get('T1_gallows_gloss', {})
    if t1.get('tier_promotion'):
        print(f"  ** C869 TIER PROMOTION: Tier 3 -> Tier 2 **")
    print(f"  Elapsed: {elapsed:.1f}s")
    print(f"  Results: {out_path}")
    print(f"{'=' * 60}")


if __name__ == '__main__':
    main()
