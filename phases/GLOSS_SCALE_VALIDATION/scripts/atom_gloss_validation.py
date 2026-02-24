"""
Phase 446b: ATOM_GLOSS_VALIDATION
Character-level validation of atom->gloss assignments.

Tests whether the specific assignment of operational glosses to single-character
atoms (k=heat, e=cool, h=watch, y=end, i=iterate, etc.) produces structural
predictions that match reality better than random assignments.

Design principle (expert-advisor): Kernel atoms (k, e, h) are quasi-definitional
-- kernel K IS defined by k-ratio. The REAL validation targets are NON-KERNEL atoms:
  LOCKED: y=end, i=iterate, n=halt, a=yield, m=final
  SOLID: d=mark, t=transfer
  PLAUSIBLE: c=adjust, p=pause, f=flag, s=sequence, g=complete
  WEAK: o=work, l=frame, r=input

Null model: Shuffle gloss assignments among non-kernel atoms (keep k=heat, e=cool,
h=watch fixed). Re-derive structural predictions from shuffled glosses. Tests
whether our SPECIFIC mapping outperforms random alternatives.

References: C1190 (atomicity), C1195 (confidence tiers), C1207 (clusters),
C1209 (positional grammar), C1203 (ch/sh differentiation)
"""

import json
import sys
import time
import functools
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy import stats as sp_stats

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = ROOT / "phases" / "GLOSS_SCALE_VALIDATION" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

N_PERM = 1000
P_THRESHOLD = 0.01

# ── Atom gloss definitions (C1195) ─────────────────────────────────

ATOM_GLOSSES = {
    'k': 'heat', 'e': 'cool', 'h': 'watch',           # KERNEL
    'y': 'end', 'i': 'iterate', 'n': 'halt',           # LOCKED
    'a': 'yield', 'm': 'final',                         # LOCKED
    'd': 'mark', 't': 'transfer',                       # SOLID
    'c': 'adjust', 'p': 'pause', 'f': 'flag',          # PLAUSIBLE
    's': 'sequence', 'g': 'complete',                    # PLAUSIBLE
    'o': 'work', 'l': 'frame', 'r': 'input',           # WEAK
}

KERNEL_ATOMS = {'k', 'e', 'h'}

# Map atom glosses to operational categories (consistent with v2 MIDDLE-level)
ATOM_GLOSS_TO_CATEGORY = {
    'heat': 'THERMAL', 'cool': 'THERMAL',
    'watch': 'MONITORING',
    'end': 'TRANSITION', 'yield': 'TRANSITION', 'final': 'TRANSITION',
    'complete': 'TRANSITION',
    'iterate': 'STAGING', 'halt': 'STAGING', 'sequence': 'STAGING',
    'frame': 'STAGING',
    'mark': 'MARKING', 'flag': 'MARKING', 'adjust': 'MARKING',
    'pause': 'MARKING',
    'transfer': 'FLOW', 'input': 'FLOW',
    'work': 'OPERATION',
}

# For mapping human-assigned MIDDLE glosses to categories
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

# ── Pre-registered structural predictions ───────────────────────────
# Derived SOLELY from gloss meanings, before looking at structural data.

# T1: Predicted line-position rank (1=earliest, higher=later)
PREDICTED_LINE_RANK = {
    's': 1, 'l': 2, 'r': 3, 'i': 4, 'o': 5, 't': 6,
    'c': 7, 'p': 8, 'n': 9, 'f': 10, 'd': 11,
    'a': 12, 'g': 13, 'y': 14, 'm': 15,
}

# T2: Predicted suffix Mode A preference (higher = more Mode A)
# Mode A (edy, ey, dy) = specification/completion; Mode B (aiin, ain) = continuation
PREDICTED_MODE_A_SCORE = {
    'y': 0.9, 'm': 0.9, 'g': 0.85, 'a': 0.75, 'd': 0.7,
    'f': 0.5, 'n': 0.5, 'c': 0.45, 'p': 0.45,
    't': 0.3, 'o': 0.3, 'r': 0.25, 'l': 0.2, 'i': 0.15, 's': 0.2,
}

# T3: Predicted dominant kernel co-occurrence
PREDICTED_KERNEL_AFFINITY = {
    'd': 'H', 'c': 'H', 'p': 'H', 'f': 'H',              # monitoring-related
    'a': 'E', 'm': 'E', 'y': 'E', 'g': 'E', 'n': 'E',    # completion/settling
    'o': 'K', 't': 'K', 's': 'K', 'l': 'K', 'r': 'K', 'i': 'K',  # active process
}

# T6: Predicted paragraph-final enrichment (higher = more at par end)
PREDICTED_PAR_FINAL = {
    'y': 0.95, 'm': 0.9, 'g': 0.85, 'a': 0.8, 'd': 0.7,
    'n': 0.6, 'f': 0.55, 'c': 0.5, 'p': 0.5, 't': 0.4,
    'o': 0.35, 'r': 0.25, 'l': 0.2, 'i': 0.15, 's': 0.1,
}

MODE_A_SUFFIXES = {'edy', 'ey', 'dy', 'eey', 'hy', 'ry'}
MODE_B_SUFFIXES = {'aiin', 'ain', 'iin', 'oiin', 'l', 'r', 'in', 'ar', 'al', 's', 'an'}


# ── Data loading ─────────────────────────────────────────────────────

def load_data():
    tx = Transcript()
    morph = Morphology()

    with open(ROOT / 'data' / 'middle_dictionary.json', encoding='utf-8') as f:
        mid_dict = json.load(f)['middles']
    with open(ROOT / 'data' / 'regime_folio_mapping.json', encoding='utf-8') as f:
        regime_map = {f: v['regime']
                      for f, v in json.load(f)['regime_assignments'].items()}

    raw_tokens = [t for t in tx.currier_b()
                  if t.word.strip() and '*' not in t.word]

    line_counts = Counter((t.folio, t.line) for t in raw_tokens)
    line_pos_idx = defaultdict(int)
    tokens = []
    for token in raw_tokens:
        w = token.word.strip()
        key = (token.folio, token.line)
        idx = line_pos_idx[key]
        line_pos_idx[key] += 1
        total = line_counts[key]
        line_pos = idx / (total - 1) if total > 1 else 0.5

        m = morph.extract(w)
        atoms = list(m.middle) if m.middle else []

        tokens.append({
            'word': w, 'folio': token.folio, 'line': token.line,
            'line_pos': line_pos,
            'par_initial': token.par_initial, 'par_final': token.par_final,
            'prefix': m.prefix, 'middle': m.middle, 'suffix': m.suffix,
            'atoms': atoms,
            'regime': regime_map.get(token.folio, 'UNK'),
        })
    return tokens, mid_dict


def get_valid_atoms(tokens, min_count=50):
    """Non-kernel atoms with sufficient occurrences."""
    counts = Counter()
    for t in tokens:
        for a in t['atoms']:
            if a in ATOM_GLOSSES and a not in KERNEL_ATOMS:
                counts[a] += 1
    return {a: c for a, c in counts.items() if c >= min_count}


def shuffle_predictions(pred_dict, rng):
    """Shuffle prediction values among atoms (null model)."""
    atoms = sorted(pred_dict.keys())
    vals = [pred_dict[a] for a in atoms]
    rng.shuffle(vals)
    return dict(zip(atoms, vals))


# ── T1: Line-Position Rank Prediction ────────────────────────────────

def test_t1_line_position(tokens, valid_atoms):
    """
    Pre-registered: atom glosses predict line position ordering.
    Spearman rho between predicted rank and actual mean position.
    Null: shuffle predicted ranks among non-kernel atoms.
    """
    atom_positions = defaultdict(list)
    for t in tokens:
        for a in t['atoms']:
            if a in valid_atoms:
                atom_positions[a].append(t['line_pos'])

    usable = sorted(a for a in valid_atoms if len(atom_positions.get(a, [])) >= 50)
    if len(usable) < 5:
        return {'status': 'SKIP', 'reason': f'Only {len(usable)} atoms'}

    actual = {a: float(np.mean(atom_positions[a])) for a in usable}
    pred = {a: PREDICTED_LINE_RANK[a] for a in usable}

    actual_v = [actual[a] for a in usable]
    pred_v = [pred[a] for a in usable]
    real_rho, real_p = sp_stats.spearmanr(pred_v, actual_v)

    print("  Running permutations...")
    rng = np.random.default_rng(60)
    shuf_rhos = []
    for _ in range(N_PERM):
        sp = shuffle_predictions(pred, rng)
        shuf_rhos.append(sp_stats.spearmanr([sp[a] for a in usable], actual_v)[0])

    shuf_arr = np.array(shuf_rhos)
    p_emp = float(np.mean(shuf_arr >= real_rho))

    return {
        'status': 'PASS' if p_emp < P_THRESHOLD else 'FAIL',
        'rho': round(float(real_rho), 4),
        'p_parametric': float(real_p),
        'p_value_empirical': p_emp,
        'n_atoms': len(usable),
        'atom_mean_positions': {a: round(actual[a], 4) for a in usable},
        'predicted_ranks': {a: pred[a] for a in usable},
        'shuffled_rho_mean': round(float(shuf_arr.mean()), 4),
    }


# ── T2: Suffix Mode Alignment ───────────────────────────────────────

def test_t2_suffix_mode(tokens, valid_atoms):
    """
    Pre-registered: completion atoms prefer Mode A suffixes,
    process atoms prefer Mode B suffixes.
    Spearman rho between predicted Mode-A-preference and actual Mode A fraction.
    """
    atom_mode_a = Counter()
    atom_mode_b = Counter()
    for t in tokens:
        sfx = t['suffix']
        if not sfx:
            continue
        is_a = sfx in MODE_A_SUFFIXES
        is_b = sfx in MODE_B_SUFFIXES
        if not is_a and not is_b:
            continue
        for a in t['atoms']:
            if a in valid_atoms:
                if is_a:
                    atom_mode_a[a] += 1
                else:
                    atom_mode_b[a] += 1

    usable = sorted(a for a in valid_atoms
                    if (atom_mode_a[a] + atom_mode_b[a]) >= 20)
    if len(usable) < 5:
        return {'status': 'SKIP', 'reason': f'Only {len(usable)} atoms'}

    actual = {}
    for a in usable:
        total = atom_mode_a[a] + atom_mode_b[a]
        actual[a] = atom_mode_a[a] / total

    pred = {a: PREDICTED_MODE_A_SCORE[a] for a in usable}
    actual_v = [actual[a] for a in usable]
    pred_v = [pred[a] for a in usable]
    real_rho, _ = sp_stats.spearmanr(pred_v, actual_v)

    print("  Running permutations...")
    rng = np.random.default_rng(61)
    shuf_rhos = []
    for _ in range(N_PERM):
        sp = shuffle_predictions(pred, rng)
        shuf_rhos.append(sp_stats.spearmanr([sp[a] for a in usable], actual_v)[0])

    shuf_arr = np.array(shuf_rhos)
    p_emp = float(np.mean(shuf_arr >= real_rho))

    return {
        'status': 'PASS' if p_emp < P_THRESHOLD else 'FAIL',
        'rho': round(float(real_rho), 4),
        'p_value_empirical': p_emp,
        'n_atoms': len(usable),
        'atom_mode_a_frac': {a: round(actual[a], 4) for a in usable},
        'predicted_scores': {a: pred[a] for a in usable},
        'shuffled_rho_mean': round(float(shuf_arr.mean()), 4),
    }


# ── T3: Kernel Co-occurrence Affinity ────────────────────────────────

def test_t3_kernel_affinity(tokens, valid_atoms):
    """
    Pre-registered: non-kernel atoms have predicted dominant kernel partners.
    d,c,p,f -> H; a,m,y,g,n -> E; o,t,s,l,r,i -> K.
    Count correct predictions vs shuffled.
    """
    atom_kernel = {a: Counter() for a in valid_atoms}
    for t in tokens:
        atoms_set = set(t['atoms'])
        kernels = atoms_set & KERNEL_ATOMS
        non_kernels = atoms_set & valid_atoms
        for nk in non_kernels:
            for kk in kernels:
                atom_kernel[nk][kk.upper()] += 1

    usable = sorted(a for a in valid_atoms
                    if sum(atom_kernel[a].values()) >= 20)
    if len(usable) < 5:
        return {'status': 'SKIP', 'reason': f'Only {len(usable)} atoms'}

    actual_dom = {}
    profiles = {}
    for a in usable:
        c = atom_kernel[a]
        total = sum(c.values())
        profiles[a] = {k: round(c.get(k, 0) / total, 3) for k in ['K', 'E', 'H']}
        actual_dom[a] = max(['K', 'E', 'H'], key=lambda k: c.get(k, 0))

    pred = {a: PREDICTED_KERNEL_AFFINITY[a] for a in usable}
    real_correct = sum(1 for a in usable if actual_dom[a] == pred[a])

    print("  Running permutations...")
    rng = np.random.default_rng(62)
    shuf_scores = []
    for _ in range(N_PERM):
        sp = shuffle_predictions(pred, rng)
        shuf_scores.append(sum(1 for a in usable if actual_dom[a] == sp[a]))

    shuf_arr = np.array(shuf_scores)
    p_emp = float(np.mean(shuf_arr >= real_correct))

    return {
        'status': 'PASS' if p_emp < P_THRESHOLD else 'FAIL',
        'correct': real_correct,
        'total': len(usable),
        'p_value_empirical': p_emp,
        'predictions': {a: {'predicted': pred[a], 'actual': actual_dom[a],
                            'hit': actual_dom[a] == pred[a],
                            'profile': profiles[a]} for a in usable},
        'shuffled_mean': round(float(shuf_arr.mean()), 2),
    }


# ── T4: REGIME Differentiation (Null-B) ─────────────────────────────

def test_t4_regime(tokens, valid_atoms):
    """
    Do non-kernel atoms differentiate REGIMEs more than random per-token labels?
    Chi-square on atom x REGIME. Null B: shuffle atom labels among tokens.
    """
    pairs = []  # (atom, regime)
    for t in tokens:
        if t['regime'] == 'UNK':
            continue
        for a in t['atoms']:
            if a in valid_atoms:
                pairs.append((a, t['regime']))

    if len(pairs) < 200:
        return {'status': 'SKIP', 'reason': 'Too few observations'}

    atoms_list = sorted(valid_atoms)
    regimes = sorted(set(p[1] for p in pairs))
    a_idx = {a: i for i, a in enumerate(atoms_list)}
    r_idx = {r: i for i, r in enumerate(regimes)}

    def build_table(pair_list):
        t = np.zeros((len(atoms_list), len(regimes)))
        for a, r in pair_list:
            if a in a_idx and r in r_idx:
                t[a_idx[a], r_idx[r]] += 1
        return t

    real_table = build_table(pairs)
    real_chi2, _, _, _ = sp_stats.chi2_contingency(real_table)
    n = real_table.sum()
    min_dim = min(real_table.shape) - 1
    cramers_v = np.sqrt(real_chi2 / (n * min_dim)) if n * min_dim > 0 else 0

    # Null B: shuffle atom labels
    atoms_arr = np.array([p[0] for p in pairs])
    regimes_arr = [p[1] for p in pairs]

    print("  Running permutations...")
    rng = np.random.default_rng(63)
    shuf_chi2s = []
    for _ in range(N_PERM):
        shuf = atoms_arr.copy()
        rng.shuffle(shuf)
        sp = list(zip(shuf, regimes_arr))
        st = build_table(sp)
        row_ok = st.sum(axis=1) > 0
        col_ok = st.sum(axis=0) > 0
        st_c = st[row_ok][:, col_ok]
        if st_c.shape[0] >= 2 and st_c.shape[1] >= 2:
            shuf_chi2s.append(sp_stats.chi2_contingency(st_c)[0])

    shuf_arr = np.array(shuf_chi2s) if shuf_chi2s else np.array([0])
    p_emp = float(np.mean(shuf_arr >= real_chi2))

    return {
        'status': 'PASS' if p_emp < P_THRESHOLD else 'FAIL',
        'chi2': round(float(real_chi2), 1),
        'cramers_v': round(float(cramers_v), 4),
        'p_value_empirical': p_emp,
        'n_atoms': len(atoms_list),
        'n_observations': int(n),
        'ratio': round(float(real_chi2 / shuf_arr.mean()), 1) if shuf_arr.mean() > 0 else None,
        'shuffled_chi2_mean': round(float(shuf_arr.mean()), 1),
    }


# ── T5: Compositional Consistency (Human-Glossed) ────────────────────

def gloss_to_cat(gloss):
    """Map a gloss string to category, trying full then individual words."""
    if not gloss:
        return None
    if gloss in GLOSS_TO_CATEGORY:
        return GLOSS_TO_CATEGORY[gloss]
    for word in gloss.split():
        if word in GLOSS_TO_CATEGORY:
            return GLOSS_TO_CATEGORY[word]
    return None


def test_t5_compositional(mid_dict):
    """
    For human-glossed MIDDLEs with 2+ atoms (incl. >=1 non-kernel),
    do composed atom glosses predict the MIDDLE's assigned category?
    Non-circular: human glosses predate atom formalization (Phase 424).
    Null: shuffle atom->gloss among non-kernel atoms.
    """
    # Human-glossed MIDDLEs: have 'gloss' field (91 of them)
    testable = []
    for mid, info in mid_dict.items():
        g = info.get('gloss')
        if not g:
            continue
        cat = gloss_to_cat(g)
        if not cat:
            continue
        atoms = list(mid)
        if len(atoms) < 2:
            continue
        # Must have at least 1 non-kernel atom
        if not any(a in ATOM_GLOSSES and a not in KERNEL_ATOMS for a in atoms):
            continue
        testable.append((mid, atoms, cat))

    if len(testable) < 10:
        return {'status': 'SKIP', 'reason': f'Only {len(testable)} testable MIDDLEs'}

    def predict_category(atoms, atom_gloss_map):
        cats = []
        for a in atoms:
            g = atom_gloss_map.get(a)
            if g:
                c = ATOM_GLOSS_TO_CATEGORY.get(g)
                if c:
                    cats.append(c)
        if not cats:
            return None
        return Counter(cats).most_common(1)[0][0]

    real_matches = 0
    details = []
    for mid, atoms, actual_cat in testable:
        pred = predict_category(atoms, ATOM_GLOSSES)
        hit = pred == actual_cat
        if hit:
            real_matches += 1
        details.append({'middle': mid, 'actual': actual_cat,
                        'predicted': pred, 'match': hit})

    # Null: shuffle non-kernel glosses
    nk_atoms = sorted(a for a in ATOM_GLOSSES if a not in KERNEL_ATOMS)
    nk_glosses = [ATOM_GLOSSES[a] for a in nk_atoms]

    print("  Running permutations...")
    rng = np.random.default_rng(64)
    shuf_matches = []
    for _ in range(N_PERM):
        sg = list(nk_glosses)
        rng.shuffle(sg)
        shuf_map = {**{a: ATOM_GLOSSES[a] for a in KERNEL_ATOMS},
                    **dict(zip(nk_atoms, sg))}
        sm = sum(1 for mid, atoms, actual_cat in testable
                 if predict_category(atoms, shuf_map) == actual_cat)
        shuf_matches.append(sm)

    shuf_arr = np.array(shuf_matches)
    p_emp = float(np.mean(shuf_arr >= real_matches))

    return {
        'status': 'PASS' if p_emp < P_THRESHOLD else 'FAIL',
        'matches': real_matches,
        'total': len(testable),
        'match_rate': round(real_matches / len(testable), 3),
        'p_value_empirical': p_emp,
        'shuffled_mean': round(float(shuf_arr.mean()), 2),
        'shuffled_std': round(float(shuf_arr.std()), 2),
        'examples': details[:15],
    }


# ── T6: Paragraph Position Gradient ──────────────────────────────────

def test_t6_paragraph_position(tokens, valid_atoms):
    """
    Completion atoms (y, m, g, a) enriched at paragraph ends;
    iteration atoms (i, s) enriched at paragraph starts.
    Spearman rho between predicted par-final score and actual rate.
    """
    atom_pf = Counter()
    atom_total = Counter()
    for t in tokens:
        for a in t['atoms']:
            if a in valid_atoms:
                atom_total[a] += 1
                if t['par_final']:
                    atom_pf[a] += 1

    usable = sorted(a for a in valid_atoms if atom_total[a] >= 50)
    if len(usable) < 5:
        return {'status': 'SKIP', 'reason': f'Only {len(usable)} atoms'}

    actual = {a: atom_pf[a] / atom_total[a] for a in usable}
    pred = {a: PREDICTED_PAR_FINAL.get(a, 0.5) for a in usable}

    actual_v = [actual[a] for a in usable]
    pred_v = [pred[a] for a in usable]
    real_rho, _ = sp_stats.spearmanr(pred_v, actual_v)

    print("  Running permutations...")
    rng = np.random.default_rng(65)
    shuf_rhos = []
    for _ in range(N_PERM):
        sp = shuffle_predictions(pred, rng)
        shuf_rhos.append(sp_stats.spearmanr([sp[a] for a in usable], actual_v)[0])

    shuf_arr = np.array(shuf_rhos)
    p_emp = float(np.mean(shuf_arr >= real_rho))

    return {
        'status': 'PASS' if p_emp < P_THRESHOLD else 'FAIL',
        'rho': round(float(real_rho), 4),
        'p_value_empirical': p_emp,
        'n_atoms': len(usable),
        'atom_par_final_rates': {a: round(actual[a], 4) for a in usable},
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
    elif pc >= 4:
        verdict = 'COHERENT'
    elif pc >= 2:
        verdict = 'PARTIALLY_COHERENT'
    else:
        verdict = 'INCOHERENT'
    return {
        'pass_count': pc, 'fail_count': fc, 'skip_count': sc,
        'total_tests': 6, 'tests_run': tr,
        'verdict': verdict,
        'summary': f'{pc}/{tr} tests pass (p<{P_THRESHOLD}), {sc} skipped',
    }


# ── Main ─────────────────────────────────────────────────────────────

def main():
    t0 = time.time()
    print("=" * 60)
    print("ATOM GLOSS VALIDATION")
    print("Character-level validation of atom->gloss assignments")
    print("=" * 60)

    print("\n[1/7] Loading data...")
    tokens, mid_dict = load_data()
    va = get_valid_atoms(tokens, min_count=50)
    print(f"  {len(tokens)} B tokens")
    print(f"  {len(va)} non-kernel atoms with >=50 occurrences:")
    for a in sorted(va):
        print(f"    {a} ({ATOM_GLOSSES[a]:10s}): {va[a]:6d}")

    valid_set = set(va.keys())
    results = {}

    print("\n[2/7] T1: Line-Position Rank Prediction...")
    results['T1_line_position'] = test_t1_line_position(tokens, valid_set)
    r = results['T1_line_position']
    print(f"  -> {r['status']} (rho={r.get('rho', 'N/A')}, "
          f"p_emp={r.get('p_value_empirical', 'N/A'):.4f})")

    print("\n[3/7] T2: Suffix Mode Alignment...")
    results['T2_suffix_mode'] = test_t2_suffix_mode(tokens, valid_set)
    r = results['T2_suffix_mode']
    print(f"  -> {r['status']} (rho={r.get('rho', 'N/A')}, "
          f"p_emp={r.get('p_value_empirical', 'N/A'):.4f})")

    print("\n[4/7] T3: Kernel Co-occurrence Affinity...")
    results['T3_kernel_affinity'] = test_t3_kernel_affinity(tokens, valid_set)
    r = results['T3_kernel_affinity']
    print(f"  -> {r['status']} ({r.get('correct', 'N/A')}/{r.get('total', 'N/A')} "
          f"correct, p_emp={r.get('p_value_empirical', 'N/A'):.4f})")

    print("\n[5/7] T4: REGIME Differentiation (Null-B)...")
    results['T4_regime'] = test_t4_regime(tokens, valid_set)
    r = results['T4_regime']
    print(f"  -> {r['status']} (chi2={r.get('chi2', 'N/A')}, V={r.get('cramers_v', 'N/A')}, "
          f"ratio={r.get('ratio', 'N/A')}x, p_emp={r.get('p_value_empirical', 'N/A'):.4f})")

    print("\n[6/7] T5: Compositional Consistency (Human-Glossed)...")
    results['T5_compositional'] = test_t5_compositional(mid_dict)
    r = results['T5_compositional']
    print(f"  -> {r['status']} ({r.get('matches', 'N/A')}/{r.get('total', 'N/A')} "
          f"[{r.get('match_rate', 0)*100:.0f}%], p_emp={r.get('p_value_empirical', 'N/A'):.4f})")

    print("\n[7/7] T6: Paragraph Position Gradient...")
    results['T6_paragraph_position'] = test_t6_paragraph_position(tokens, valid_set)
    r = results['T6_paragraph_position']
    print(f"  -> {r['status']} (rho={r.get('rho', 'N/A')}, "
          f"p_emp={r.get('p_value_empirical', 'N/A'):.4f})")

    syn = synthesize(results)
    elapsed = time.time() - t0

    output = {
        '_metadata': {
            'phase': 'GLOSS_SCALE_VALIDATION',
            'phase_number': '446b',
            'description': 'Atom-level character->gloss validation',
            'design': 'Tests non-kernel atom gloss predictions against structure',
            'null_model': 'Shuffle gloss assignments among non-kernel atoms '
                          '(kernel k=heat, e=cool, h=watch fixed)',
            'n_tokens': len(tokens),
            'n_non_kernel_atoms': len(va),
            'n_permutations': N_PERM,
            'p_threshold': P_THRESHOLD,
            'elapsed_seconds': round(elapsed, 1),
            'atom_glosses': ATOM_GLOSSES,
            'confidence_tiers': {
                'KERNEL': ['k', 'e', 'h'],
                'LOCKED': ['y', 'i', 'n', 'a', 'm'],
                'SOLID': ['d', 't'],
                'PLAUSIBLE': ['c', 'p', 'f', 's', 'g'],
                'WEAK': ['o', 'l', 'r'],
            },
        },
        'synthesis': syn,
        'tests': results,
    }

    out_path = RESULTS_DIR / 'atom_gloss_validation.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\n{'=' * 60}")
    print(f"VERDICT: {syn['verdict']}")
    print(f"  {syn['summary']}")
    print(f"  Elapsed: {elapsed:.1f}s")
    print(f"  Results: {out_path}")
    print(f"{'=' * 60}")


if __name__ == '__main__':
    main()
