"""
Script 5: Paragraph Freedom Budget
Question: How does folio-level design freedom decompose into paragraph-level choices?

For each atom feature, computes within-folio paragraph variance vs between-folio
variance. Identifies which features are folio-locked "settings" vs paragraph-variable
"accents", connects to C1573 distributional shape recovery.
"""

import sys, json
import numpy as np
import pandas as pd
from pathlib import Path
from collections import Counter
from scipy.stats import spearmanr
from scipy.spatial.distance import jensenshannon

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

RESULTS = Path(__file__).resolve().parent.parent / 'results'

# === Load Folio Features ===

with open(RESULTS / '01_freedom_space_pca.json') as f:
    pca_results = json.load(f)

sections = pd.Series(pca_results['sections'])

# === Build Paragraph-Level Features ===

tx = Transcript()
morph = Morphology()

HEAD_ATOMS = {'a', 'e', 'o', 'k', 't'}
TERM_ATOMS = {'h', 'l', 'm', 'n', 'r', 'y'}
MOD_ATOMS = {'c', 'd', 'f', 'i', 'p', 's'}

# Collect tokens with paragraph assignment
# Paragraphs in B are delimited by gallows-initial tokens
# Use line grouping as proxy: detect gallows-initial lines

token_records = []
for tok in tx.currier_b():
    if '*' in tok.word or not tok.word.strip():
        continue
    m = morph.extract(tok.word)
    a = morph.atomize(tok.word)
    atoms = a.atoms if a.atoms else []

    head = 'headless'
    if atoms and atoms[0][0] in HEAD_ATOMS:
        head = atoms[0][0]

    term = 'bare'
    if atoms and atoms[-1][0] in TERM_ATOMS:
        term = atoms[-1][0]

    mods_present = set()
    for atom_char, slot, _ in atoms:
        if atom_char in MOD_ATOMS:
            mods_present.add(atom_char)

    token_records.append({
        'folio': tok.folio,
        'line': tok.line,
        'position': tok.token_id if hasattr(tok, 'token_id') else 0,
        'word': tok.word,
        'prefix': m.prefix or 'BARE',
        'middle': m.middle,
        'suffix': m.suffix or '',
        'head': head,
        'term': term,
        'mods': frozenset(mods_present),
        'e_depth': a.e_depth,
        'is_headless': a.is_headless,
    })

df = pd.DataFrame(token_records)
print(f"Total B tokens: {len(df)}")

# === Paragraph Detection ===

# Gallows characters that mark paragraph starts (C841, C864)
GALLOWS = {'k', 'p', 'f', 't'}

# Assign paragraph IDs within each folio
df['para_id'] = 0
for folio, fgroup in df.groupby('folio'):
    # Sort by line
    lines = sorted(fgroup['line'].unique())
    para_id = 0

    for line in lines:
        line_tokens = fgroup[fgroup['line'] == line].sort_index()
        if len(line_tokens) == 0:
            continue
        first_word = line_tokens.iloc[0]['word']

        # Check if first character is a gallows
        if first_word and first_word[0] in GALLOWS:
            para_id += 1

        df.loc[line_tokens.index, 'para_id'] = para_id

# Create unique paragraph key
df['para_key'] = df['folio'] + '_p' + df['para_id'].astype(str)

# Filter: only paragraphs with >= 10 tokens
para_sizes = df.groupby('para_key').size()
valid_paras = para_sizes[para_sizes >= 10].index
df_valid = df[df['para_key'].isin(valid_paras)]

n_paras = len(valid_paras)
n_folios = df_valid['folio'].nunique()
print(f"Valid paragraphs (>=10 tokens): {n_paras} across {n_folios} folios")

# === Build Per-Paragraph Feature Vectors ===

def para_features(group):
    """Build feature vector for one paragraph."""
    n = len(group)
    if n < 10:
        return None

    features = {}

    # HEAD fractions
    head_counts = group['head'].value_counts()
    for h in ['a', 'e', 'o', 'k', 't', 'headless']:
        features[f'head_{h}'] = head_counts.get(h, 0) / n

    # TERMINAL fractions
    term_counts = group['term'].value_counts()
    for t in ['h', 'l', 'm', 'n', 'r', 'y', 'bare']:
        features[f'term_{t}'] = term_counts.get(t, 0) / n

    # MODIFIER fractions
    for mod in ['c', 'd', 'f', 'i', 'p', 's']:
        features[f'mod_{mod}'] = group['mods'].apply(lambda ms: mod in ms).mean()

    # PREFIX fractions
    pfx_counts = group['prefix'].value_counts()
    for pfx in ['qo', 'ch', 'sh', 'ok', 'ot', 'ol', 'da', 'BARE']:
        features[f'pfx_{pfx}'] = pfx_counts.get(pfx, 0) / n

    # Derived
    features['suffix_rate'] = (group['suffix'] != '').mean()
    features['e_depth_mean'] = group['e_depth'].mean()
    features['headless_rate'] = group['is_headless'].mean()
    features['ey_rate'] = ((group['head'] == 'e') & (group['term'] == 'y')).mean()

    return features

para_feat_list = {}
para_folios = {}
for para_key, group in df_valid.groupby('para_key'):
    feat = para_features(group)
    if feat is not None:
        para_feat_list[para_key] = feat
        para_folios[para_key] = group['folio'].iloc[0]

para_df = pd.DataFrame(para_feat_list).T
para_df['folio'] = [para_folios[p] for p in para_df.index]
para_df['section'] = [sections.get(f, 'Unknown') for f in para_df['folio']]

feature_cols = [c for c in para_df.columns if c not in ('folio', 'section')]
print(f"Paragraph features: {len(feature_cols)} per paragraph")
print(f"Paragraphs: {len(para_df)}, Folios: {para_df['folio'].nunique()}")

# === Variance Decomposition: Within-Folio vs Between-Folio ===

print(f"\n=== Variance Decomposition ===")

def variance_decomposition(values, groups):
    """Decompose total variance into between-group and within-group."""
    grand_mean = values.mean()
    total_ss = ((values - grand_mean) ** 2).sum()

    if total_ss == 0:
        return 0, 0, 0

    between_ss = 0
    within_ss = 0
    for g in set(groups):
        g_vals = values[groups == g]
        g_mean = g_vals.mean()
        between_ss += len(g_vals) * (g_mean - grand_mean) ** 2
        within_ss += ((g_vals - g_mean) ** 2).sum()

    return between_ss / total_ss, within_ss / total_ss, total_ss

decomp_results = {}
for col in feature_cols:
    values = para_df[col].values
    folio_groups = para_df['folio'].values

    between_frac, within_frac, total_var = variance_decomposition(values, folio_groups)

    # Also decompose between-folio into between-section and within-section-between-folio
    section_groups = para_df['section'].values
    section_between, section_within, _ = variance_decomposition(values, section_groups)

    decomp_results[col] = {
        'total_var': float(total_var),
        'between_folio_frac': float(between_frac),
        'within_folio_frac': float(within_frac),
        'between_section_frac': float(section_between),
        'within_section_between_folio_frac': float(max(0, between_frac - section_between)),
        'folio_icc_approx': float(between_frac),  # ICC(1) approximation
    }

# Sort by within-folio fraction (paragraph-variable features)
sorted_by_within = sorted(decomp_results.items(), key=lambda x: x[1]['within_folio_frac'], reverse=True)

print(f"\nMost PARAGRAPH-VARIABLE features (high within-folio variance):")
for col, res in sorted_by_within[:10]:
    print(f"  {col}: within_folio={res['within_folio_frac']:.3f}, between_folio={res['between_folio_frac']:.3f}, section={res['between_section_frac']:.3f}")

print(f"\nMost FOLIO-LOCKED features (high between-folio variance):")
sorted_by_between = sorted(decomp_results.items(), key=lambda x: x[1]['between_folio_frac'], reverse=True)
for col, res in sorted_by_between[:10]:
    print(f"  {col}: between_folio={res['between_folio_frac']:.3f}, within_folio={res['within_folio_frac']:.3f}, section={res['between_section_frac']:.3f}")

# === Partition: Folio Setting vs Paragraph Accent ===

SETTING_THRESHOLD = 0.50  # > 50% between-folio = folio setting
ACCENT_THRESHOLD = 0.50   # > 50% within-folio = paragraph accent

settings = [col for col, res in decomp_results.items() if res['between_folio_frac'] > SETTING_THRESHOLD]
accents = [col for col, res in decomp_results.items() if res['within_folio_frac'] > ACCENT_THRESHOLD]
mixed = [col for col in feature_cols if col not in settings and col not in accents]

print(f"\n=== Partition ===")
print(f"FOLIO SETTINGS (>{SETTING_THRESHOLD*100}% between-folio): {len(settings)}")
for col in sorted(settings, key=lambda c: decomp_results[c]['between_folio_frac'], reverse=True):
    print(f"  {col}: {decomp_results[col]['between_folio_frac']:.3f}")

print(f"\nPARAGRAPH ACCENTS (>{ACCENT_THRESHOLD*100}% within-folio): {len(accents)}")
for col in sorted(accents, key=lambda c: decomp_results[c]['within_folio_frac'], reverse=True):
    print(f"  {col}: {decomp_results[col]['within_folio_frac']:.3f}")

print(f"\nMIXED: {len(mixed)}")

# === C1573 Connection: Distributional Shape Recovery ===

print(f"\n=== C1573 Distributional Shape Test ===")
print("Do paragraph distributions of ACCENT features recover within-section folio identity?")

# For each folio with 3+ paragraphs, compute pairwise JSD of accent feature vectors
# Compare within-folio vs between-folio-same-section

# Only use sections with enough folios
section_folio_map = {}
for folio in para_df['folio'].unique():
    sec = sections.get(folio, 'Unknown')
    if sec not in section_folio_map:
        section_folio_map[sec] = []
    section_folio_map[sec].append(folio)

# For folios with 3+ paragraphs
folio_para_counts = para_df.groupby('folio').size()
multi_para_folios = folio_para_counts[folio_para_counts >= 3].index.tolist()

print(f"Folios with 3+ paragraphs: {len(multi_para_folios)}")

if accents:
    # Build per-paragraph accent vectors
    accent_vectors = para_df[accents + ['folio', 'section']].copy()

    within_jsds = []
    between_jsds = []

    for sec, sec_folios in section_folio_map.items():
        sec_multi = [f for f in sec_folios if f in multi_para_folios]
        if len(sec_multi) < 2:
            continue

        for folio in sec_multi:
            folio_paras = accent_vectors[accent_vectors['folio'] == folio][accents].values
            if len(folio_paras) < 2:
                continue

            # Within-folio: pairwise JSD between paragraphs of same folio
            for i in range(len(folio_paras)):
                for j in range(i+1, len(folio_paras)):
                    p = folio_paras[i] + 1e-10
                    q = folio_paras[j] + 1e-10
                    p = p / p.sum()
                    q = q / q.sum()
                    jsd = jensenshannon(p, q)
                    if not np.isnan(jsd):
                        within_jsds.append(jsd)

        # Between-folio (same section): compare random paragraphs across folios
        for i, f1 in enumerate(sec_multi):
            for f2 in sec_multi[i+1:]:
                paras_f1 = accent_vectors[accent_vectors['folio'] == f1][accents].values
                paras_f2 = accent_vectors[accent_vectors['folio'] == f2][accents].values
                if len(paras_f1) == 0 or len(paras_f2) == 0:
                    continue
                # Random sample: 1 para from each
                p = paras_f1[0] + 1e-10
                q = paras_f2[0] + 1e-10
                p = p / p.sum()
                q = q / q.sum()
                jsd = jensenshannon(p, q)
                if not np.isnan(jsd):
                    between_jsds.append(jsd)

    if within_jsds and between_jsds:
        within_mean = np.mean(within_jsds)
        between_mean = np.mean(between_jsds)
        ratio = between_mean / max(within_mean, 1e-10)

        from scipy.stats import mannwhitneyu
        U, p_mwu = mannwhitneyu(between_jsds, within_jsds, alternative='greater')

        print(f"\n  Within-folio JSD: {within_mean:.4f} (n={len(within_jsds)})")
        print(f"  Between-folio (same section) JSD: {between_mean:.4f} (n={len(between_jsds)})")
        print(f"  Ratio: {ratio:.3f}")
        print(f"  Mann-Whitney p: {p_mwu:.6f}")
        print(f"  Verdict: {'FOLIO_RECOVERABLE' if p_mwu < 0.05 and ratio > 1.05 else 'NOT_RECOVERABLE'}")
    else:
        print("  Insufficient data for JSD comparison")
        ratio, p_mwu = 0, 1
else:
    print("  No accent features identified")
    ratio, p_mwu = 0, 1

# === Cross-Reference with C1811 (PREFIX ICC=0.185) ===

print(f"\n=== C1811 Cross-Reference ===")
print("C1811: PREFIX ICC=0.185 (paragraph-level, not folio-level)")
for col in feature_cols:
    if col.startswith('pfx_'):
        res = decomp_results[col]
        print(f"  {col}: folio_ICC={res['folio_icc_approx']:.3f}, within_folio={res['within_folio_frac']:.3f}")

# === Summary Statistics ===

setting_frac = len(settings) / len(feature_cols)
accent_frac = len(accents) / len(feature_cols)
mean_folio_icc = np.mean([decomp_results[c]['between_folio_frac'] for c in feature_cols])

print(f"\n=== Summary ===")
print(f"Total features: {len(feature_cols)}")
print(f"Folio settings: {len(settings)} ({setting_frac*100:.1f}%)")
print(f"Paragraph accents: {len(accents)} ({accent_frac*100:.1f}%)")
print(f"Mixed: {len(mixed)}")
print(f"Mean folio ICC: {mean_folio_icc:.3f}")
print(f"Folio identity = {setting_frac*100:.0f}% setting + {accent_frac*100:.0f}% accent + {(1-setting_frac-accent_frac)*100:.0f}% mixed")

# === Save Results ===

results = {
    'n_paragraphs': int(n_paras),
    'n_folios': int(n_folios),
    'n_features': len(feature_cols),
    'decomposition': decomp_results,
    'partition': {
        'settings': settings,
        'accents': accents,
        'mixed': mixed,
    },
    'partition_counts': {
        'settings': len(settings),
        'accents': len(accents),
        'mixed': len(mixed),
    },
    'mean_folio_icc': float(mean_folio_icc),
    'c1573_test': {
        'within_folio_jsd': float(np.mean(within_jsds)) if within_jsds else None,
        'between_folio_jsd': float(np.mean(between_jsds)) if between_jsds else None,
        'ratio': float(ratio),
        'p_value': float(p_mwu),
    },
}

with open(RESULTS / '05_paragraph_budget.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {RESULTS / '05_paragraph_budget.json'}")
print("Done.")
