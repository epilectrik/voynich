#!/usr/bin/env python3
"""
Phase 380: Morphological Joint Space Architecture

5-test battery combining PREFIX x SUFFIX compatibility analysis with
within-compound atom ordering grammar.

T1: PREFIX x SUFFIX Forbidden Pair Enumeration
T2: PREFIX x SUFFIX Joint Role Classification Gain
T3: Within-Compound Atom Bigram Grammar
T4: Atom String-Position vs Line-Position Alignment
T5: Atom Terminal-Character Positional Bias

All Tier 2 targets. Expert-advisor validated (2x review).
"""

import sys
import json
import functools
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from scipy.stats import chi2_contingency, spearmanr, mannwhitneyu, binomtest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript, Morphology, MiddleAnalyzer

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS = ROOT / "phases" / "MORPHOLOGICAL_JOINT_SPACE_ARCHITECTURE" / "results"
RESULTS.mkdir(parents=True, exist_ok=True)


# ============================================================
# ROLE TAXONOMY (from BCSC)
# ============================================================

ROLE_TAXONOMY = {
    'CC': {10, 11, 12, 17},
    'EN': {8, 31, 32, 33, 34, 35, 36, 37, 39, 41, 42, 43, 44, 45, 46, 47, 48, 49},
    'FL': {7, 30, 38, 40},
    'FQ': {9, 13, 14, 23},
    'AX': {1, 2, 3, 4, 5, 6, 15, 16, 18, 19, 20, 21, 22, 24, 25, 26, 27, 28, 29},
}

CLASS_TO_ROLE = {}
for role, classes in ROLE_TAXONOMY.items():
    for cls in classes:
        CLASS_TO_ROLE[cls] = role

PREFIX_ROLE_MAP = {
    'ch': 'EN', 'sh': 'EN',
    'qo': 'AX',
    'da': 'AX', 'sa': 'AX',
    'ok': 'AX', 'ot': 'AX', 'ol': 'AX', 'ct': 'AX',
}

# C588 per-role suffix strata: fraction of tokens that are bare (no suffix)
C588_BARE_RATE = {
    'CC': 1.00, 'FL': 0.94, 'FQ': 0.93, 'AX': 0.62, 'EN': 0.39,
}


# ============================================================
# DATA LOADING
# ============================================================

def load_data():
    """Load all shared data."""
    tx = Transcript()
    morph = Morphology()
    mid_analyzer = MiddleAnalyzer()
    mid_analyzer.build_inventory('B')

    # Load 49-class mapping
    ctm_path = ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(ctm_path, 'r', encoding='utf-8') as f:
        ctm = json.load(f)
    token_to_class = {t: int(c) for t, c in ctm['token_to_class'].items()}

    # Build PREFIX→dominant role from classified tokens
    prefix_role_counts = defaultdict(Counter)
    for word, cls in token_to_class.items():
        m = morph.extract(word)
        role = CLASS_TO_ROLE.get(cls, 'UN')
        prefix_key = m.prefix if m.prefix else '_BARE_'
        prefix_role_counts[prefix_key][role] += 1

    prefix_dominant_role = {}
    for prefix, counts in prefix_role_counts.items():
        prefix_dominant_role[prefix] = counts.most_common(1)[0][0]

    # Build token list with morphology + class + role + line position
    tokens = []
    line_groups = defaultdict(list)
    for t in tx.currier_b():
        m = morph.extract(t.word)
        cls = token_to_class.get(t.word)
        if cls:
            role = CLASS_TO_ROLE.get(cls, 'UN')
        else:
            prefix_key = m.prefix if m.prefix else '_BARE_'
            role = prefix_dominant_role.get(prefix_key,
                   PREFIX_ROLE_MAP.get(m.prefix, 'UN'))
        tok = {
            'word': t.word,
            'folio': t.folio,
            'line': t.line,
            'section': t.section,
            'prefix': m.prefix,
            'middle': m.middle,
            'suffix': m.suffix,
            'cls': cls,
            'role': role,
        }
        tokens.append(tok)
        line_groups[(t.folio, t.line)].append(tok)

    # Compute line position (O(n))
    for key, toks in line_groups.items():
        n = len(toks)
        for i, tok in enumerate(toks):
            tok['line_pos'] = i / max(n - 1, 1) if n > 1 else 0.5

    # Pre-compute compound atoms sorted by string position
    unique_middles = set(t['middle'] for t in tokens if t['middle'])
    middle_atoms = {}
    for mid in unique_middles:
        if mid_analyzer.is_compound(mid):
            atoms = mid_analyzer.get_maximal_atoms(mid)
            if atoms and len(atoms) >= 2:
                atom_positions = [(mid.find(a), a) for a in atoms]
                atom_positions.sort()
                middle_atoms[mid] = [a for _, a in atom_positions]

    return tokens, token_to_class, morph, mid_analyzer, middle_atoms, line_groups


def cramers_v(contingency_table):
    """Compute Cramér's V from a contingency table."""
    table = np.array(contingency_table)
    if table.sum() == 0:
        return 0.0
    chi2, _, _, _ = chi2_contingency(table)
    n = table.sum()
    r, k = table.shape
    return float(np.sqrt(chi2 / (n * (min(r, k) - 1)))) if min(r, k) > 1 else 0.0


def save_result(data, filename):
    """Save result JSON."""
    path = RESULTS / filename
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, default=str)
    print(f"\nSaved: {path}")


# ============================================================
# T1: PREFIX x SUFFIX FORBIDDEN PAIR ENUMERATION
# ============================================================

def run_t1(tokens):
    """Enumerate forbidden PREFIX x SUFFIX combinations (C911 methodology)."""
    print("\n" + "=" * 60)
    print("T1: PREFIX x SUFFIX Forbidden Pair Enumeration")
    print("=" * 60)

    # Normalize PREFIX and SUFFIX
    prefix_counts = Counter()
    suffix_counts = Counter()
    pair_counts = Counter()

    for t in tokens:
        p = t['prefix'] if t['prefix'] else '_BARE_'
        s = t['suffix'] if t['suffix'] else '_BARE_'
        prefix_counts[p] += 1
        suffix_counts[s] += 1
        pair_counts[(p, s)] += 1

    # Filter to common (>=50 tokens)
    common_prefixes = sorted([p for p, c in prefix_counts.items() if c >= 50])
    common_suffixes = sorted([s for s, c in suffix_counts.items() if c >= 50])
    N = sum(c for (p, s), c in pair_counts.items()
            if p in common_prefixes and s in common_suffixes)

    print(f"  Common PREFIXes (>=50): {len(common_prefixes)}")
    print(f"  Common SUFFIXes (>=50): {len(common_suffixes)}")
    print(f"  Total tokens in common space: {N}")

    # Build contingency table
    p_idx = {p: i for i, p in enumerate(common_prefixes)}
    s_idx = {s: i for i, s in enumerate(common_suffixes)}
    table = np.zeros((len(common_prefixes), len(common_suffixes)), dtype=float)
    for (p, s), c in pair_counts.items():
        if p in p_idx and s in s_idx:
            table[p_idx[p], s_idx[s]] = c

    # Row/column marginals
    row_totals = table.sum(axis=1)
    col_totals = table.sum(axis=0)
    grand_total = table.sum()

    # Chi-square
    chi2, p_chi2, dof, expected = chi2_contingency(table)
    v = cramers_v(table)
    print(f"\n  Overall chi²={chi2:.1f}, p={p_chi2:.2e}, V={v:.4f}")

    # Enumerate forbidden (expected >= 5, observed = 0)
    forbidden = []
    enriched = []
    depleted = []

    for i, p in enumerate(common_prefixes):
        for j, s in enumerate(common_suffixes):
            obs = table[i, j]
            exp = expected[i, j]
            if exp >= 5:
                z = (obs - exp) / np.sqrt(exp) if exp > 0 else 0
                if obs == 0:
                    forbidden.append({'prefix': p, 'suffix': s, 'expected': round(exp, 1)})
                elif z > 3.0:
                    enriched.append({'prefix': p, 'suffix': s,
                                     'observed': int(obs), 'expected': round(exp, 1),
                                     'z': round(z, 2)})
                elif z < -3.0:
                    depleted.append({'prefix': p, 'suffix': s,
                                     'observed': int(obs), 'expected': round(exp, 1),
                                     'z': round(z, 2)})

    print(f"\n  Forbidden pairs (expected>=5, observed=0): {len(forbidden)}")
    for fp in sorted(forbidden, key=lambda x: -x['expected'])[:15]:
        print(f"    {fp['prefix']:8s} x {fp['suffix']:8s}  expected={fp['expected']:.1f}")

    print(f"\n  Enriched pairs (z > 3.0): {len(enriched)}")
    for ep in sorted(enriched, key=lambda x: -x['z'])[:10]:
        print(f"    {ep['prefix']:8s} x {ep['suffix']:8s}  obs={ep['observed']:4d} exp={ep['expected']:6.1f} z={ep['z']:+.2f}")

    print(f"  Depleted pairs (z < -3.0): {len(depleted)}")
    for dp in sorted(depleted, key=lambda x: x['z'])[:10]:
        print(f"    {dp['prefix']:8s} x {dp['suffix']:8s}  obs={dp['observed']:4d} exp={dp['expected']:6.1f} z={dp['z']:+.2f}")

    # LATE prefix check (al, ar, or)
    late_prefixes = ['al', 'ar', 'or']
    late_forbidden = {}
    for lp in late_prefixes:
        if lp in p_idx:
            count = sum(1 for fp in forbidden if fp['prefix'] == lp)
            late_forbidden[lp] = count
            print(f"\n  LATE prefix {lp}: {count} forbidden suffixes")

    # ch/sh check
    sister_forbidden = {}
    for sp in ['ch', 'sh']:
        if sp in p_idx:
            count = sum(1 for fp in forbidden if fp['prefix'] == sp)
            sister_forbidden[sp] = count
            print(f"  Sister prefix {sp}: {count} forbidden suffixes")

    # Role-composition decomposition (C588)
    # For each forbidden pair, compute expected suffix rate from PREFIX's role composition
    # Build PREFIX -> role distribution
    prefix_role_dist = defaultdict(Counter)
    for t in tokens:
        p = t['prefix'] if t['prefix'] else '_BARE_'
        if p in p_idx:
            prefix_role_dist[p][t['role']] += 1

    n_role_explained = 0
    n_novel = 0
    for fp in forbidden:
        p = fp['prefix']
        s = fp['suffix']
        # Expected suffix rate: weighted average of (1 - bare_rate) for each role
        role_dist = prefix_role_dist[p]
        total = sum(role_dist.values())
        if s == '_BARE_':
            # Expected bare rate from role composition
            expected_rate = sum(C588_BARE_RATE.get(r, 0.5) * c / total
                                for r, c in role_dist.items())
        else:
            # Expected non-bare: 1 - bare_rate, then further divided by suffix count
            # Simplified: if role is 100% bare (CC), suffix s is mechanically forbidden
            expected_nonbare = sum((1 - C588_BARE_RATE.get(r, 0.5)) * c / total
                                    for r, c in role_dist.items())
            expected_rate = expected_nonbare  # simplified: is there room for this suffix?

        # If expected non-bare rate < 0.05, this forbidden pair is role-explained
        if s != '_BARE_' and expected_rate < 0.05:
            n_role_explained += 1
            fp['decomposition'] = 'role_explained'
        else:
            n_novel += 1
            fp['decomposition'] = 'novel'

    print(f"\n  Decomposition: {n_role_explained} role-explained, {n_novel} novel")

    # Verdict
    late_confirmed = all(late_forbidden.get(lp, 0) >= 3 for lp in late_prefixes if lp in p_idx)
    sister_ok = all(sister_forbidden.get(sp, 0) <= 5 for sp in ['ch', 'sh'] if sp in p_idx)
    criteria = [
        len(forbidden) > 0,
        len(forbidden) < 50,
        p_chi2 < 0.001,
        late_confirmed,
    ]
    n_met = sum(criteria)

    if n_met == 4:
        verdict = "PASS"
    elif n_met >= 2:
        verdict = "PARTIAL"
    else:
        verdict = "FAIL"

    print(f"\n  Criteria: forbidden>0={criteria[0]}, <50={criteria[1]}, p<0.001={criteria[2]}, LATE={criteria[3]}")
    print(f"  ch/sh <= 5 each: {sister_ok}")
    print(f"  >>> VERDICT: {verdict} ({len(forbidden)} forbidden, V={v:.4f})")

    result = {
        'test': 'T1_prefix_suffix_forbidden',
        'verdict': verdict,
        'n_common_prefixes': len(common_prefixes),
        'n_common_suffixes': len(common_suffixes),
        'n_tokens': N,
        'chi2': round(chi2, 1),
        'p': p_chi2,
        'V': round(v, 4),
        'n_forbidden': len(forbidden),
        'n_enriched': len(enriched),
        'n_depleted': len(depleted),
        'forbidden_pairs': forbidden,
        'enriched_pairs': sorted(enriched, key=lambda x: -x['z'])[:20],
        'depleted_pairs': sorted(depleted, key=lambda x: x['z'])[:20],
        'late_forbidden': late_forbidden,
        'sister_forbidden': sister_forbidden,
        'decomposition': {'role_explained': n_role_explained, 'novel': n_novel},
        'constraints_referenced': ['C911', 'C278', 'C539', 'C1059', 'C588', 'C275'],
    }
    save_result(result, 't1_prefix_suffix_forbidden.json')
    return result


# ============================================================
# T2: PREFIX x SUFFIX JOINT ROLE CLASSIFICATION GAIN
# ============================================================

def run_t2(tokens, token_to_class):
    """Test classification gain from joint PREFIX+SUFFIX over individual."""
    print("\n" + "=" * 60)
    print("T2: PREFIX x SUFFIX Joint Role Classification Gain")
    print("=" * 60)

    # Only classified tokens
    classified = [t for t in tokens if t['cls'] is not None]
    print(f"  Classified tokens: {len(classified)}")

    # Extract features
    for t in classified:
        t['_prefix'] = t['prefix'] if t['prefix'] else '_BARE_'
        t['_suffix'] = t['suffix'] if t['suffix'] else '_BARE_'
        t['_joint'] = (t['_prefix'], t['_suffix'])

    roles = sorted(set(t['role'] for t in classified))
    role_idx = {r: i for i, r in enumerate(roles)}

    # 5-fold CV using naive Bayes (frequency-based)
    np.random.seed(42)
    indices = np.arange(len(classified))
    np.random.shuffle(indices)
    folds = np.array_split(indices, 5)

    prefix_accs = []
    suffix_accs = []
    joint_accs = []

    for fold_i in range(5):
        test_idx = set(folds[fold_i])
        train = [classified[i] for i in range(len(classified)) if i not in test_idx]
        test = [classified[i] for i in test_idx]

        # Train: build P(role | feature) via counts
        def train_classifier(feature_key):
            """Train frequency-based naive Bayes for a single feature."""
            counts = defaultdict(Counter)
            for t in train:
                feat = t[feature_key]
                counts[feat][t['role']] += 1
            # Marginal role prior
            role_prior = Counter(t['role'] for t in train)
            return counts, role_prior

        def predict(counts, role_prior, feature_key, test_set):
            """Predict roles."""
            correct = 0
            for t in test_set:
                feat = t[feature_key]
                if feat in counts and counts[feat]:
                    pred = counts[feat].most_common(1)[0][0]
                else:
                    pred = role_prior.most_common(1)[0][0]
                if pred == t['role']:
                    correct += 1
            return correct / len(test_set) if test_set else 0

        p_counts, p_prior = train_classifier('_prefix')
        s_counts, s_prior = train_classifier('_suffix')
        j_counts, j_prior = train_classifier('_joint')

        prefix_accs.append(predict(p_counts, p_prior, '_prefix', test))
        suffix_accs.append(predict(s_counts, s_prior, '_suffix', test))
        joint_accs.append(predict(j_counts, j_prior, '_joint', test))

    mean_p = np.mean(prefix_accs) * 100
    mean_s = np.mean(suffix_accs) * 100
    mean_j = np.mean(joint_accs) * 100
    best_single = max(mean_p, mean_s)
    gain = mean_j - best_single

    print(f"\n  5-fold CV accuracy:")
    print(f"    PREFIX-only:  {mean_p:.1f}%")
    print(f"    SUFFIX-only:  {mean_s:.1f}%")
    print(f"    Joint:        {mean_j:.1f}%")
    print(f"    Gain over best single: {gain:+.1f}pp")

    # Per-PREFIX decomposition
    print(f"\n  Per-PREFIX gain (n>=50):")
    prefix_gains = {}
    prefix_groups = defaultdict(list)
    for t in classified:
        prefix_groups[t['_prefix']].append(t)

    for prefix in sorted(prefix_groups.keys()):
        group = prefix_groups[prefix]
        if len(group) < 50:
            continue
        # Within this PREFIX, can suffix predict role?
        suf_counts = defaultdict(Counter)
        for t in group:
            suf_counts[t['_suffix']][t['role']] += 1
        # Accuracy of majority-class per suffix
        correct = 0
        for suf, role_counts in suf_counts.items():
            correct += role_counts.most_common(1)[0][0] if False else max(role_counts.values())
        # ... simplified: V of role x suffix within this PREFIX
        roles_here = sorted(set(t['role'] for t in group))
        suffs_here = sorted(set(t['_suffix'] for t in group))
        if len(roles_here) < 2 or len(suffs_here) < 2:
            prefix_gains[prefix] = {'n': len(group), 'suffix_useful': False}
            print(f"    {prefix:8s}: n={len(group):5d}, <2 roles or <2 suffixes")
            continue

        sub_table = np.zeros((len(roles_here), len(suffs_here)))
        r_idx = {r: i for i, r in enumerate(roles_here)}
        su_idx = {s: i for i, s in enumerate(suffs_here)}
        for t in group:
            sub_table[r_idx[t['role']], su_idx[t['_suffix']]] += 1
        within_v = cramers_v(sub_table)
        prefix_gains[prefix] = {'n': len(group), 'V': round(within_v, 4), 'suffix_useful': within_v > 0.05}
        print(f"    {prefix:8s}: n={len(group):5d}, within-PREFIX suffix V={within_v:.4f}")

    # Verdict
    # Interpretable pattern: QO-family (ok, ot, ol, da) higher gains than ch/sh
    qo_family = ['ok', 'ot', 'ol', 'da']
    sister_family = ['ch', 'sh']
    qo_vs = [prefix_gains[p]['V'] for p in qo_family if p in prefix_gains and 'V' in prefix_gains[p]]
    sis_vs = [prefix_gains[p]['V'] for p in sister_family if p in prefix_gains and 'V' in prefix_gains[p]]
    interpretable = (np.mean(qo_vs) > np.mean(sis_vs)) if qo_vs and sis_vs else False

    if gain >= 2.0 and interpretable:
        verdict = "PASS"
    elif gain > 0:
        verdict = "PARTIAL"
    else:
        verdict = "FAIL"

    print(f"\n  QO-family mean V: {np.mean(qo_vs):.4f}" if qo_vs else "")
    print(f"  Sister mean V: {np.mean(sis_vs):.4f}" if sis_vs else "")
    print(f"  Interpretable pattern (QO > sister): {interpretable}")
    print(f"\n  >>> VERDICT: {verdict} (gain={gain:+.1f}pp)")

    result = {
        'test': 'T2_prefix_suffix_role_gain',
        'verdict': verdict,
        'n_classified': len(classified),
        'cv_prefix_acc': round(mean_p, 2),
        'cv_suffix_acc': round(mean_s, 2),
        'cv_joint_acc': round(mean_j, 2),
        'gain_pp': round(gain, 2),
        'per_prefix': prefix_gains,
        'interpretable_pattern': interpretable,
        'constraints_referenced': ['C1059', 'C588', 'C662', 'C1003'],
    }
    save_result(result, 't2_prefix_suffix_role_gain.json')
    return result


# ============================================================
# T3: WITHIN-COMPOUND ATOM BIGRAM GRAMMAR
# ============================================================

def run_t3(mid_analyzer, middle_atoms):
    """Test ordered atom bigram grammar within compound MIDDLEs."""
    print("\n" + "=" * 60)
    print("T3: Within-Compound Atom Bigram Grammar")
    print("=" * 60)

    # Extract ordered atom bigrams (type-level)
    bigram_counts = Counter()
    atom_counts = Counter()
    all_pairs = []  # (atom_a, atom_b) where a is before b in string

    for mid, atoms in middle_atoms.items():
        # All ordered pairs (not just consecutive)
        for i in range(len(atoms)):
            atom_counts[atoms[i]] += 1
            for j in range(i + 1, len(atoms)):
                pair = (atoms[i], atoms[j])
                bigram_counts[pair] += 1
                all_pairs.append(pair)

    # Also track reverse pairs for asymmetry
    pair_direction = Counter()  # (a,b) sorted alphabetically -> count of a-before-b
    pair_reverse = Counter()    # (a,b) sorted alphabetically -> count of b-before-a
    for a, b in all_pairs:
        key = tuple(sorted([a, b]))
        if key[0] == a:
            pair_direction[key] += 1
        else:
            pair_reverse[key] += 1

    n_compounds = len(middle_atoms)
    n_bigrams = len(all_pairs)
    unique_atoms = sorted(atom_counts.keys())

    print(f"  Compounds analyzed: {n_compounds}")
    print(f"  Total ordered pairs: {n_bigrams}")
    print(f"  Unique atoms: {len(unique_atoms)}")

    # Build transition matrix (atom_i -> atom_j)
    atom_idx = {a: i for i, a in enumerate(unique_atoms)}
    n_atoms = len(unique_atoms)
    trans_matrix = np.zeros((n_atoms, n_atoms), dtype=float)
    for (a, b), c in bigram_counts.items():
        if a in atom_idx and b in atom_idx:
            trans_matrix[atom_idx[a], atom_idx[b]] = c

    # Chi-square on transition matrix (rows with sufficient data)
    # Filter to atoms with >= 5 bigrams as source
    row_sums = trans_matrix.sum(axis=1)
    col_sums = trans_matrix.sum(axis=0)
    mask = (row_sums >= 5) & (col_sums >= 5)
    filtered_matrix = trans_matrix[np.ix_(mask, mask)]

    if filtered_matrix.sum() > 0 and filtered_matrix.shape[0] >= 2 and filtered_matrix.shape[1] >= 2:
        chi2, p_chi2, dof, _ = chi2_contingency(filtered_matrix)
        v = cramers_v(filtered_matrix)
    else:
        chi2, p_chi2, v = 0, 1, 0

    print(f"\n  Transition matrix (filtered): {filtered_matrix.shape[0]} atoms")
    print(f"  Chi²={chi2:.1f}, p={p_chi2:.2e}, V={v:.4f}")

    # Kernel asymmetry test
    # k-containing vs e-containing atoms: which comes first?
    k_before_e = 0
    e_before_k = 0
    h_before_e = 0
    e_before_h = 0

    for mid, atoms in middle_atoms.items():
        for i in range(len(atoms)):
            for j in range(i + 1, len(atoms)):
                a_has_k = 'k' in atoms[i]
                a_has_e = 'e' in atoms[i]
                a_has_h = 'h' in atoms[i]
                b_has_k = 'k' in atoms[j]
                b_has_e = 'e' in atoms[j]
                b_has_h = 'h' in atoms[j]

                # k-before-e: atom[i] has k, atom[j] has e (and not vice versa)
                if a_has_k and b_has_e and not (a_has_e and b_has_k):
                    k_before_e += 1
                elif a_has_e and b_has_k and not (a_has_k and b_has_e):
                    e_before_k += 1

                # e-before-h
                if a_has_e and b_has_h and not (a_has_h and b_has_e):
                    e_before_h += 1
                elif a_has_h and b_has_e and not (a_has_e and b_has_h):
                    h_before_e += 1

    total_ke = k_before_e + e_before_k
    total_eh = e_before_h + h_before_e
    ke_rate = k_before_e / total_ke if total_ke > 0 else 0.5
    eh_rate = e_before_h / total_eh if total_eh > 0 else 0.5

    ke_p = binomtest(k_before_e, total_ke, 0.5).pvalue if total_ke > 0 else 1.0
    eh_p = binomtest(e_before_h, total_eh, 0.5).pvalue if total_eh > 0 else 1.0

    print(f"\n  Kernel asymmetry:")
    print(f"    k-before-e: {k_before_e}/{total_ke} = {ke_rate:.1%}, p={ke_p:.4f}")
    print(f"    e-before-h: {e_before_h}/{total_eh} = {eh_rate:.1%}, p={eh_p:.4f}")
    print(f"    (C521 predicts: k-before-e elevated, e-before-h near 0%)")

    # Strongly asymmetric pairs
    asymmetric = []
    for key in set(list(pair_direction.keys()) + list(pair_reverse.keys())):
        fwd = pair_direction.get(key, 0)
        rev = pair_reverse.get(key, 0)
        total = fwd + rev
        if total >= 5:
            rate = fwd / total
            if rate > 0.80 or rate < 0.20:
                dominant = key[0] if rate > 0.5 else key[1]
                subordinate = key[1] if rate > 0.5 else key[0]
                asym_rate = max(rate, 1 - rate)
                asymmetric.append({
                    'dominant': dominant, 'subordinate': subordinate,
                    'fwd': fwd, 'rev': rev, 'total': total,
                    'rate': round(asym_rate, 3),
                })

    asymmetric.sort(key=lambda x: -x['rate'])
    print(f"\n  Strongly asymmetric pairs (rate > 0.80, n>=5): {len(asymmetric)}")
    for ap in asymmetric[:15]:
        print(f"    {ap['dominant']:8s} before {ap['subordinate']:8s}: "
              f"{max(ap['fwd'],ap['rev'])}/{ap['total']} = {ap['rate']:.1%}")

    # Permutation null (1000x shuffle atom order within each compound)
    print(f"\n  Permutation null (1000 shuffles)...")
    null_chi2s = []
    rng = np.random.default_rng(42)
    for _ in range(1000):
        null_bigrams = Counter()
        for mid, atoms in middle_atoms.items():
            shuffled = list(atoms)
            rng.shuffle(shuffled)
            for i in range(len(shuffled)):
                for j in range(i + 1, len(shuffled)):
                    null_bigrams[(shuffled[i], shuffled[j])] += 1

        null_matrix = np.zeros((n_atoms, n_atoms), dtype=float)
        for (a, b), c in null_bigrams.items():
            if a in atom_idx and b in atom_idx:
                null_matrix[atom_idx[a], atom_idx[b]] = c
        null_filtered = null_matrix[np.ix_(mask, mask)]
        if null_filtered.sum() > 0 and null_filtered.shape[0] >= 2:
            try:
                nc2, _, _, _ = chi2_contingency(null_filtered)
                null_chi2s.append(nc2)
            except ValueError:
                pass

    perm_p = np.mean([nc >= chi2 for nc in null_chi2s]) if null_chi2s else 1.0
    print(f"  Observed chi²={chi2:.1f}, null mean={np.mean(null_chi2s):.1f}, perm p={perm_p:.4f}")

    # Verdict
    criteria = [
        p_chi2 < 0.001 and v > 0.15,
        ke_rate > 0.60 and total_ke >= 10,
        len(asymmetric) >= 5,
    ]
    n_met = sum(criteria)

    if n_met == 3:
        verdict = "PASS"
    elif n_met >= 2:
        verdict = "PARTIAL"
    else:
        verdict = "FAIL"

    print(f"\n  Criteria: chi²+V={criteria[0]}, k-before-e={criteria[1]}, asymmetric>5={criteria[2]}")
    print(f"  >>> VERDICT: {verdict} (V={v:.4f}, ke_rate={ke_rate:.1%}, n_asym={len(asymmetric)})")

    result = {
        'test': 'T3_atom_bigram_grammar',
        'verdict': verdict,
        'n_compounds': n_compounds,
        'n_bigrams': n_bigrams,
        'n_unique_atoms': len(unique_atoms),
        'chi2': round(chi2, 1),
        'p': p_chi2,
        'V': round(v, 4),
        'kernel_asymmetry': {
            'k_before_e': k_before_e, 'e_before_k': e_before_k,
            'ke_rate': round(ke_rate, 4), 'ke_p': round(ke_p, 4),
            'e_before_h': e_before_h, 'h_before_e': h_before_e,
            'eh_rate': round(eh_rate, 4), 'eh_p': round(eh_p, 4),
        },
        'n_asymmetric': len(asymmetric),
        'asymmetric_pairs': asymmetric[:20],
        'permutation_null': {
            'n_shuffles': 1000,
            'observed_chi2': round(chi2, 1),
            'null_mean_chi2': round(np.mean(null_chi2s), 1) if null_chi2s else 0,
            'perm_p': round(perm_p, 4),
        },
        'constraints_referenced': ['C1060', 'C521', 'C517', 'C873'],
    }
    save_result(result, 't3_atom_bigram_grammar.json')
    return result


# ============================================================
# T4: ATOM STRING-POSITION VS LINE-POSITION ALIGNMENT
# ============================================================

def run_t4(tokens, middle_atoms):
    """Test alignment between atom string position and token line position."""
    print("\n" + "=" * 60)
    print("T4: Atom String-Position vs Line-Position Alignment")
    print("=" * 60)

    # For each token with a compound MIDDLE, record (atom, string_pos, line_pos, prefix)
    observations = []
    for t in tokens:
        mid = t['middle']
        if mid and mid in middle_atoms:
            atoms = middle_atoms[mid]
            mid_len = len(mid)
            for atom in atoms:
                idx = mid.find(atom)
                string_pos = idx / max(mid_len - 1, 1) if mid_len > 1 else 0.5
                observations.append({
                    'atom': atom,
                    'string_pos': string_pos,
                    'line_pos': t['line_pos'],
                    'prefix': t['prefix'] if t['prefix'] else '_BARE_',
                })

    print(f"  Observations (token-level, one per atom per token): {len(observations)}")

    if len(observations) < 20:
        print("  Insufficient data")
        result = {'test': 'T4_string_vs_line_position', 'verdict': 'FAIL',
                  'reason': 'insufficient_data', 'constraints_referenced': ['C1060', 'C522', 'C1001']}
        save_result(result, 't4_string_vs_line_position.json')
        return result

    string_pos = np.array([o['string_pos'] for o in observations])
    line_pos = np.array([o['line_pos'] for o in observations])

    # Raw Spearman
    rho, p_rho = spearmanr(string_pos, line_pos)
    print(f"\n  Raw: Spearman rho={rho:.4f}, p={p_rho:.2e}, n={len(observations)}")

    # PREFIX-conditioned partial correlation
    # Residualize both string_pos and line_pos on PREFIX
    prefixes = [o['prefix'] for o in observations]
    unique_prefixes = sorted(set(prefixes))
    prefix_to_idx = {p: i for i, p in enumerate(unique_prefixes)}

    # Compute residuals: for each PREFIX group, subtract group mean
    prefix_groups = defaultdict(list)
    for i, o in enumerate(observations):
        prefix_groups[o['prefix']].append(i)

    string_resid = np.copy(string_pos)
    line_resid = np.copy(line_pos)
    for prefix, indices in prefix_groups.items():
        idx = np.array(indices)
        string_resid[idx] -= np.mean(string_pos[idx])
        line_resid[idx] -= np.mean(line_pos[idx])

    partial_rho, partial_p = spearmanr(string_resid, line_resid)
    print(f"  Partial (controlling PREFIX): rho={partial_rho:.4f}, p={partial_p:.2e}")

    # Per-prefix correlation
    print(f"\n  Per-PREFIX (n>=50):")
    prefix_corrs = {}
    for prefix in sorted(prefix_groups.keys()):
        idx = prefix_groups[prefix]
        if len(idx) >= 50:
            sp = string_pos[idx]
            lp = line_pos[idx]
            r, p = spearmanr(sp, lp)
            prefix_corrs[prefix] = {'n': len(idx), 'rho': round(r, 4), 'p': round(p, 4)}
            print(f"    {prefix:8s}: n={len(idx):5d}, rho={r:+.4f}, p={p:.4f}")

    # Verdict
    abs_rho = abs(rho)
    abs_partial = abs(partial_rho)

    if abs_rho > 0.30:
        verdict = "FAIL"  # violates C522
        reason = "rho > 0.30 violates C522"
    elif p_rho < 0.001 and 0.04 <= abs_rho <= 0.20 and abs_partial > 0.03:
        verdict = "PASS"
        reason = f"weak alignment rho={rho:.4f}, partial={partial_rho:.4f}"
    elif p_rho < 0.001 and abs_partial <= 0.03:
        verdict = "PARTIAL"
        reason = "significant but PREFIX-mediated"
    elif p_rho >= 0.05:
        verdict = "FAIL"
        reason = "no correlation (confirms C522)"
    else:
        verdict = "PARTIAL"
        reason = f"ambiguous: rho={rho:.4f}, partial={partial_rho:.4f}"

    print(f"\n  >>> VERDICT: {verdict} ({reason})")

    result = {
        'test': 'T4_string_vs_line_position',
        'verdict': verdict,
        'reason': reason,
        'n_observations': len(observations),
        'raw_rho': round(rho, 4),
        'raw_p': p_rho,
        'partial_rho': round(partial_rho, 4),
        'partial_p': partial_p,
        'per_prefix': prefix_corrs,
        'constraints_referenced': ['C1060', 'C522', 'C1001', 'C873'],
    }
    save_result(result, 't4_string_vs_line_position.json')
    return result


# ============================================================
# T5: ATOM TERMINAL-CHARACTER POSITIONAL BIAS
# ============================================================

def run_t5(middle_atoms, tokens):
    """Test whether atom terminal/initial characters predict compound position."""
    print("\n" + "=" * 60)
    print("T5: Atom Terminal-Character Positional Bias")
    print("=" * 60)

    # Collect atom position observations (type-level: each compound counts once)
    atom_obs = []  # (atom, terminal_char, initial_char, position_class, norm_pos)
    for mid, atoms in middle_atoms.items():
        mid_len = len(mid)
        for atom in atoms:
            idx = mid.find(atom)
            end_idx = idx + len(atom)
            # Position class
            if idx == 0:
                pos_class = 'INITIAL'
            elif end_idx == mid_len:
                pos_class = 'FINAL'
            else:
                pos_class = 'MEDIAL'

            norm_pos = idx / max(mid_len - 1, 1) if mid_len > 1 else 0.5
            terminal_char = atom[-1]
            initial_char = atom[0]

            atom_obs.append({
                'atom': atom,
                'terminal_char': terminal_char,
                'initial_char': initial_char,
                'pos_class': pos_class,
                'norm_pos': norm_pos,
                'compound': mid,
            })

    print(f"  Atom observations (type-level): {len(atom_obs)}")

    # Primary: terminal-character x position-class chi-square
    terminal_chars = sorted(set(o['terminal_char'] for o in atom_obs))
    pos_classes = ['INITIAL', 'MEDIAL', 'FINAL']

    tc_idx = {c: i for i, c in enumerate(terminal_chars)}
    pc_idx = {c: i for i, c in enumerate(pos_classes)}
    term_table = np.zeros((len(terminal_chars), 3), dtype=float)

    for o in atom_obs:
        term_table[tc_idx[o['terminal_char']], pc_idx[o['pos_class']]] += 1

    # Filter to terminal chars with >= 10 observations
    tc_mask = term_table.sum(axis=1) >= 10
    term_filtered = term_table[tc_mask]
    filtered_tc = [c for c, m in zip(terminal_chars, tc_mask) if m]

    if term_filtered.shape[0] >= 2:
        chi2_term, p_term, _, _ = chi2_contingency(term_filtered)
        v_term = cramers_v(term_filtered)
    else:
        chi2_term, p_term, v_term = 0, 1, 0

    print(f"\n  Terminal character x position:")
    print(f"    Testable chars (n>=10): {len(filtered_tc)}")
    print(f"    Chi²={chi2_term:.1f}, p={p_term:.2e}, V={v_term:.4f}")

    # Per terminal char: mean position
    print(f"\n  Per terminal character:")
    tc_stats = {}
    for tc in filtered_tc:
        obs = [o for o in atom_obs if o['terminal_char'] == tc]
        positions = [o['norm_pos'] for o in obs]
        counts = Counter(o['pos_class'] for o in obs)
        mean_pos = np.mean(positions)
        tc_stats[tc] = {
            'n': len(obs),
            'mean_pos': round(mean_pos, 4),
            'INITIAL': counts.get('INITIAL', 0),
            'MEDIAL': counts.get('MEDIAL', 0),
            'FINAL': counts.get('FINAL', 0),
        }
        print(f"    '{tc}': n={len(obs):4d}, mean={mean_pos:.3f}, "
              f"I={counts.get('INITIAL', 0):3d} M={counts.get('MEDIAL', 0):3d} F={counts.get('FINAL', 0):3d}")

    # Symmetry: initial-character x position-class
    initial_chars = sorted(set(o['initial_char'] for o in atom_obs))
    ic_idx = {c: i for i, c in enumerate(initial_chars)}
    init_table = np.zeros((len(initial_chars), 3), dtype=float)
    for o in atom_obs:
        init_table[ic_idx[o['initial_char']], pc_idx[o['pos_class']]] += 1

    ic_mask = init_table.sum(axis=1) >= 10
    init_filtered = init_table[ic_mask]
    filtered_ic = [c for c, m in zip(initial_chars, ic_mask) if m]

    if init_filtered.shape[0] >= 2:
        chi2_init, p_init, _, _ = chi2_contingency(init_filtered)
        v_init = cramers_v(init_filtered)
    else:
        chi2_init, p_init, v_init = 0, 1, 0

    print(f"\n  Initial character x position:")
    print(f"    Testable chars (n>=10): {len(filtered_ic)}")
    print(f"    Chi²={chi2_init:.1f}, p={p_init:.2e}, V={v_init:.4f}")

    ic_stats = {}
    for ic in filtered_ic:
        obs = [o for o in atom_obs if o['initial_char'] == ic]
        positions = [o['norm_pos'] for o in obs]
        counts = Counter(o['pos_class'] for o in obs)
        mean_pos = np.mean(positions)
        ic_stats[ic] = {
            'n': len(obs),
            'mean_pos': round(mean_pos, 4),
            'INITIAL': counts.get('INITIAL', 0),
            'MEDIAL': counts.get('MEDIAL', 0),
            'FINAL': counts.get('FINAL', 0),
        }
        print(f"    '{ic}': n={len(obs):4d}, mean={mean_pos:.3f}, "
              f"I={counts.get('INITIAL', 0):3d} M={counts.get('MEDIAL', 0):3d} F={counts.get('FINAL', 0):3d}")

    # kc case study
    print(f"\n  kc case study:")
    kc_obs = [o for o in atom_obs if o['atom'] == 'kc']
    if kc_obs:
        kc_counts = Counter(o['pos_class'] for o in kc_obs)
        kc_final_rate = kc_counts.get('FINAL', 0) / len(kc_obs)
        print(f"    Type-level: n={len(kc_obs)}, FINAL={kc_counts.get('FINAL', 0)}/{len(kc_obs)} = {kc_final_rate:.1%}")

        # Token-level: count tokens containing compounds with kc
        kc_compounds = set(o['compound'] for o in kc_obs)
        kc_token_obs = []
        for t in tokens:
            mid = t['middle']
            if mid and mid in kc_compounds and mid in middle_atoms:
                atoms = middle_atoms[mid]
                idx_kc = mid.find('kc')
                if idx_kc >= 0:
                    mid_len = len(mid)
                    if idx_kc == 0:
                        pc = 'INITIAL'
                    elif idx_kc + 2 == mid_len:
                        pc = 'FINAL'
                    else:
                        pc = 'MEDIAL'
                    kc_token_obs.append({
                        'pos_class': pc,
                        'line_pos': t['line_pos'],
                    })

        if kc_token_obs:
            kc_tok_counts = Counter(o['pos_class'] for o in kc_token_obs)
            kc_tok_final = kc_tok_counts.get('FINAL', 0) / len(kc_token_obs)
            print(f"    Token-level: n={len(kc_token_obs)}, FINAL={kc_tok_counts.get('FINAL', 0)}/{len(kc_token_obs)} = {kc_tok_final:.1%}")

            # H1 (intrinsic): kc FINAL rate at token level
            # H3 (line-position): correlation
            lp_final = [o['line_pos'] for o in kc_token_obs if o['pos_class'] == 'FINAL']
            lp_other = [o['line_pos'] for o in kc_token_obs if o['pos_class'] != 'FINAL']
            if lp_final and lp_other:
                u_stat, lp_p = mannwhitneyu(lp_final, lp_other, alternative='two-sided')
                print(f"    H3 (line-position): FINAL mean_lp={np.mean(lp_final):.3f} vs other={np.mean(lp_other):.3f}, MW p={lp_p:.4f}")
            else:
                lp_p = 1.0
                print(f"    H3: insufficient data for comparison")
        else:
            kc_tok_final = 0
            lp_p = 1.0
    else:
        kc_final_rate = 0
        kc_tok_final = 0
        lp_p = 1.0
        print(f"    No kc atoms found")

    # Verdict
    term_sig = p_term < 0.001 and v_term > 0.10
    kc_confirmed = kc_final_rate > 0.75 if kc_obs else False

    if term_sig and kc_confirmed:
        verdict = "PASS"
    elif term_sig:
        verdict = "PARTIAL"
    else:
        verdict = "FAIL"

    print(f"\n  >>> VERDICT: {verdict} (terminal V={v_term:.4f}, kc FINAL={kc_final_rate:.1%})")

    result = {
        'test': 'T5_terminal_character_bias',
        'verdict': verdict,
        'n_atom_obs': len(atom_obs),
        'terminal_char': {
            'chi2': round(chi2_term, 1),
            'p': p_term,
            'V': round(v_term, 4),
            'n_testable': len(filtered_tc),
            'per_char': tc_stats,
        },
        'initial_char': {
            'chi2': round(chi2_init, 1),
            'p': p_init,
            'V': round(v_init, 4),
            'n_testable': len(filtered_ic),
            'per_char': ic_stats,
        },
        'kc_case_study': {
            'type_level_n': len(kc_obs),
            'type_level_final_rate': round(kc_final_rate, 4) if kc_obs else None,
            'token_level_n': len(kc_token_obs) if kc_obs else 0,
            'token_level_final_rate': round(kc_tok_final, 4) if kc_obs else None,
            'h3_line_position_p': round(lp_p, 4),
        },
        'constraints_referenced': ['C1060', 'C521', 'C985'],
    }
    save_result(result, 't5_terminal_character_bias.json')
    return result


# ============================================================
# MAIN
# ============================================================

def main():
    print("Phase 380: Morphological Joint Space Architecture")
    print("5-test battery | Tier 2 targets")
    print("=" * 60)

    print("\nLoading data...")
    tokens, token_to_class, morph, mid_analyzer, middle_atoms, line_groups = load_data()
    print(f"  Currier B tokens: {len(tokens)}")
    print(f"  Compound MIDDLEs with 2+ atoms: {len(middle_atoms)}")

    t1 = run_t1(tokens)
    t2 = run_t2(tokens, token_to_class)
    t3 = run_t3(mid_analyzer, middle_atoms)
    t4 = run_t4(tokens, middle_atoms)
    t5 = run_t5(middle_atoms, tokens)

    # Summary
    summary = {
        'phase': 380,
        'name': 'MORPHOLOGICAL_JOINT_SPACE_ARCHITECTURE',
        'description': '5-test battery: PREFIX x SUFFIX compatibility + atom ordering grammar',
        'tier': 2,
        'tests': [
            {'id': 'T1', 'name': 'PREFIX x SUFFIX Forbidden Pairs', 'verdict': t1['verdict']},
            {'id': 'T2', 'name': 'PREFIX x SUFFIX Role Classification Gain', 'verdict': t2['verdict']},
            {'id': 'T3', 'name': 'Atom Bigram Grammar', 'verdict': t3['verdict']},
            {'id': 'T4', 'name': 'String-Position vs Line-Position', 'verdict': t4['verdict']},
            {'id': 'T5', 'name': 'Terminal-Character Positional Bias', 'verdict': t5['verdict']},
        ],
        'constraints_referenced': sorted(set(
            t1.get('constraints_referenced', []) +
            t2.get('constraints_referenced', []) +
            t3.get('constraints_referenced', []) +
            t4.get('constraints_referenced', []) +
            t5.get('constraints_referenced', [])
        )),
    }
    save_result(summary, 'morphological_joint_space_summary.json')

    print("\n" + "=" * 60)
    print("RESULTS:")
    for t in summary['tests']:
        print(f"  {t['id']}: {t['name']} -> {t['verdict']}")
    print("=" * 60)


if __name__ == '__main__':
    main()
