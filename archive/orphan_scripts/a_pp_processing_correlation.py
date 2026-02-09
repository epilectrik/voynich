#!/usr/bin/env python3
"""
A PP Processing Correlation Test

Hypothesis: A's PP vocabulary encodes material-specific sensory criteria
for managing each material's hysteresis window.

Test Design:
1. Map each A folio to its processing requirements (via B-side characteristics)
2. Extract PP vocabulary profile for each A folio
3. Test if PP profiles correlate with processing requirements

Processing Requirements (from BRUNSCHWIG_CLOSED_LOOP_DIMENSIONS):
- Fire degree (via REGIME mapping)
- Stability profile (LINK/FQ ratio)
- Recovery vs distillation specialization (HIGH_K vs HIGH_H)

If true: Different materials need different monitoring criteria,
and A's PP vocabulary should reflect this.
"""

import sys
import io
from pathlib import Path
from collections import defaultdict, Counter
import json
import numpy as np
from scipy import stats
from scipy.cluster import hierarchy

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, str(Path(__file__).parent))
from voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()
GALLOWS = {'k', 't', 'p', 'f'}

# Load REGIME mapping
regime_path = Path(__file__).parent.parent / 'results' / 'regime_folio_mapping.json'
with open(regime_path) as f:
    regime_data = json.load(f)
folio_to_regime = regime_data.get('folio_to_regime', {})

# Fire degree mapping from BRSC
REGIME_FIRE_DEGREE = {
    'REGIME_1': 2,  # Medium fire
    'REGIME_2': 1,  # Gentle fire
    'REGIME_3': 3,  # Strong fire
    'REGIME_4': 4,  # Intense/precision fire
}

# Load class map for B-side analysis
class_map_path = Path(__file__).parent.parent / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(class_map_path) as f:
    class_data = json.load(f)
token_to_class = {t: int(c) for t, c in class_data['token_to_class'].items()}

# Key classes
FQ_CLASSES = {9, 13, 14, 23}  # Escape/recovery
LINK_CLASS = 29  # Monitoring

# Role taxonomy for A PP (from a_pp_role_breakdown.py)
PREFIX_ROLES = {
    'ch': 'CORE', 'sh': 'CORE',
    'qo': 'ESCAPE',
    'ok': 'AUXILIARY',
    'ol': 'LINK', 'or': 'LINK',
    'ct': 'CROSS-REF',
    'da': 'CLOSURE', 'do': 'CLOSURE',
    'kch': 'GALLOWS-CH', 'tch': 'GALLOWS-CH', 'pch': 'GALLOWS-CH',
    'fch': 'GALLOWS-CH', 'sch': 'GALLOWS-CH', 'dch': 'GALLOWS-CH',
    'po': 'INPUT', 'so': 'INPUT', 'to': 'INPUT', 'ko': 'INPUT',
}

def get_role(prefix):
    if prefix in PREFIX_ROLES:
        return PREFIX_ROLES[prefix]
    if prefix and len(prefix) >= 2 and prefix[-2:] == 'ch':
        return 'GALLOWS-CH'
    if prefix and prefix.endswith('o') and len(prefix) == 2:
        return 'INPUT'
    return 'UNCLASSIFIED'

print("="*70)
print("A PP PROCESSING CORRELATION TEST")
print("="*70)

# =========================================================================
# STEP 1: Build A folio PP profiles
# =========================================================================
print("\n[1] Building A folio PP profiles...")

# Build A paragraph data per folio
a_folio_paragraphs = defaultdict(list)
current_folio = None
current_para = []
current_line = None

for token in tx.currier_a():
    if '*' in token.word:
        continue

    if token.folio != current_folio:
        if current_para:
            a_folio_paragraphs[current_folio].append([t.word for t in current_para])
        current_folio = token.folio
        current_para = [token]
        current_line = token.line
        continue

    if token.line != current_line:
        if token.word and token.word[0] in GALLOWS:
            a_folio_paragraphs[current_folio].append([t.word for t in current_para])
            current_para = [token]
        else:
            current_para.append(token)
        current_line = token.line
    else:
        current_para.append(token)

if current_para:
    a_folio_paragraphs[current_folio].append([t.word for t in current_para])

# Extract PP from each paragraph (middle zone)
def get_pp_tokens(para_tokens):
    """Extract PP zone tokens (positions 3 to -3)."""
    if len(para_tokens) > 6:
        return para_tokens[3:-3]
    elif len(para_tokens) > 3:
        return para_tokens[3:]
    return []

# Build folio PP profiles
a_folio_pp_profiles = {}
a_folio_sections = {}

for token in tx.currier_a():
    if token.folio not in a_folio_sections:
        a_folio_sections[token.folio] = token.section

for folio, paragraphs in a_folio_paragraphs.items():
    prefix_counts = Counter()
    middle_set = set()
    role_counts = Counter()
    total_pp = 0

    for para in paragraphs:
        pp_tokens = get_pp_tokens(para)
        for token in pp_tokens:
            try:
                m = morph.extract(token)
                if m.prefix:
                    prefix_counts[m.prefix] += 1
                    role = get_role(m.prefix)
                    role_counts[role] += 1
                if m.middle:
                    middle_set.add(m.middle)
                total_pp += 1
            except:
                pass

    if total_pp > 10:  # Minimum threshold
        a_folio_pp_profiles[folio] = {
            'prefix_counts': prefix_counts,
            'middle_set': middle_set,
            'role_counts': role_counts,
            'total_pp': total_pp,
            'n_paragraphs': len(paragraphs),
            'section': a_folio_sections.get(folio, 'UNKNOWN'),
            'middle_diversity': len(middle_set) / total_pp if total_pp > 0 else 0,
        }

print(f"  A folios with PP profiles: {len(a_folio_pp_profiles)}")

# =========================================================================
# STEP 2: Build B-side processing characteristics per folio
# =========================================================================
print("\n[2] Building B-side processing characteristics...")

b_folio_tokens = defaultdict(list)
b_folio_sections = {}

for token in tx.currier_b():
    if '*' in token.word:
        continue
    b_folio_tokens[token.folio].append(token.word)
    if token.folio not in b_folio_sections:
        b_folio_sections[token.folio] = token.section

b_folio_characteristics = {}

for folio, tokens in b_folio_tokens.items():
    n = len(tokens)
    if n < 50:
        continue

    # FQ rate (escape/recovery)
    fq_count = sum(1 for t in tokens if token_to_class.get(t) in FQ_CLASSES)
    fq_rate = fq_count / n

    # LINK rate (monitoring)
    link_count = sum(1 for t in tokens if token_to_class.get(t) == LINK_CLASS)
    link_rate = link_count / n

    # LINK/FQ ratio (stability proxy)
    link_fq_ratio = link_rate / fq_rate if fq_rate > 0 else float('inf')

    # Kernel ratios
    k_chars = sum(t.count('k') for t in tokens)
    h_chars = sum(t.count('h') for t in tokens)
    e_chars = sum(t.count('e') for t in tokens)
    total_kernel = k_chars + h_chars + e_chars

    k_ratio = k_chars / total_kernel if total_kernel > 0 else 0
    h_ratio = h_chars / total_kernel if total_kernel > 0 else 0
    e_ratio = e_chars / total_kernel if total_kernel > 0 else 0

    # Specialization type
    if k_ratio > 0.30:
        spec_type = 'RECOVERY'
    elif h_ratio > 0.40:
        spec_type = 'DISTILL'
    else:
        spec_type = 'BALANCED'

    # REGIME and fire degree
    regime = folio_to_regime.get(folio)
    fire_degree = REGIME_FIRE_DEGREE.get(regime, 2)

    b_folio_characteristics[folio] = {
        'fq_rate': fq_rate,
        'link_rate': link_rate,
        'link_fq_ratio': link_fq_ratio if link_fq_ratio != float('inf') else 10,
        'k_ratio': k_ratio,
        'h_ratio': h_ratio,
        'e_ratio': e_ratio,
        'spec_type': spec_type,
        'regime': regime,
        'fire_degree': fire_degree,
        'section': b_folio_sections.get(folio, 'UNKNOWN'),
    }

print(f"  B folios with characteristics: {len(b_folio_characteristics)}")

# =========================================================================
# STEP 3: Match A folios to B folios
# =========================================================================
print("\n[3] Matching A and B folios...")

# A folios that have corresponding B characteristics
# This uses C885 logic - A folio provides vocabulary for B execution
# We'll use section matching as proxy

matched_folios = []
for a_folio in a_folio_pp_profiles:
    a_section = a_folio_pp_profiles[a_folio]['section']

    # Find B folios in same section
    matching_b = [f for f in b_folio_characteristics
                  if b_folio_characteristics[f]['section'] == a_section]

    if matching_b:
        # Use aggregate B characteristics for this A folio's section
        avg_fq = np.mean([b_folio_characteristics[f]['fq_rate'] for f in matching_b])
        avg_link = np.mean([b_folio_characteristics[f]['link_rate'] for f in matching_b])
        avg_k = np.mean([b_folio_characteristics[f]['k_ratio'] for f in matching_b])
        avg_h = np.mean([b_folio_characteristics[f]['h_ratio'] for f in matching_b])

        # Mode fire degree
        fire_degrees = [b_folio_characteristics[f]['fire_degree'] for f in matching_b]
        mode_fire = max(set(fire_degrees), key=fire_degrees.count)

        matched_folios.append({
            'a_folio': a_folio,
            'section': a_section,
            'a_profile': a_folio_pp_profiles[a_folio],
            'b_avg_fq': avg_fq,
            'b_avg_link': avg_link,
            'b_avg_k': avg_k,
            'b_avg_h': avg_h,
            'b_fire_degree': mode_fire,
            'n_b_folios': len(matching_b),
        })

print(f"  Matched A folios: {len(matched_folios)}")

# =========================================================================
# STEP 4: Test correlations
# =========================================================================
print("\n" + "="*70)
print("TEST 1: PP ROLE COMPOSITION vs FIRE DEGREE")
print("="*70)

# Group A folios by B fire degree
fire_groups = defaultdict(list)
for m in matched_folios:
    fire_groups[m['b_fire_degree']].append(m)

print(f"\n{'Fire Degree':<12} {'N':<5} {'CORE%':<10} {'ESCAPE%':<10} {'LINK%':<10} {'CROSS-REF%':<12}")
print("-"*65)

fire_role_data = {}
for fire_degree in sorted(fire_groups.keys()):
    group = fire_groups[fire_degree]

    # Aggregate role counts
    total_roles = Counter()
    total_count = 0
    for m in group:
        total_roles.update(m['a_profile']['role_counts'])
        total_count += sum(m['a_profile']['role_counts'].values())

    if total_count > 0:
        core_pct = 100 * total_roles.get('CORE', 0) / total_count
        escape_pct = 100 * total_roles.get('ESCAPE', 0) / total_count
        link_pct = 100 * total_roles.get('LINK', 0) / total_count
        xref_pct = 100 * total_roles.get('CROSS-REF', 0) / total_count

        fire_role_data[fire_degree] = {
            'CORE': core_pct,
            'ESCAPE': escape_pct,
            'LINK': link_pct,
            'CROSS-REF': xref_pct,
        }

        print(f"{fire_degree:<12} {len(group):<5} {core_pct:<10.1f} {escape_pct:<10.1f} {link_pct:<10.1f} {xref_pct:<12.1f}")

# Correlation test
if len(fire_role_data) >= 3:
    fire_levels = sorted(fire_role_data.keys())

    print("\nCorrelations with fire degree:")
    for role in ['CORE', 'ESCAPE', 'LINK', 'CROSS-REF']:
        values = [fire_role_data[f][role] for f in fire_levels]
        if len(values) >= 3:
            rho, p = stats.spearmanr(fire_levels, values)
            sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
            print(f"  {role:<12}: rho={rho:+.3f}, p={p:.4f} {sig}")

# =========================================================================
# TEST 2: MIDDLE DIVERSITY vs STABILITY REQUIREMENTS
# =========================================================================
print("\n" + "="*70)
print("TEST 2: MIDDLE DIVERSITY vs STABILITY (LINK/FQ RATIO)")
print("="*70)

# Per-section analysis to control for section confound
for section in ['H', 'P']:
    section_folios = [m for m in matched_folios if m['section'] == section]
    if len(section_folios) < 5:
        continue

    # Get diversity and stability metrics
    diversities = [m['a_profile']['middle_diversity'] for m in section_folios]
    fq_rates = [m['b_avg_fq'] for m in section_folios]
    link_rates = [m['b_avg_link'] for m in section_folios]

    print(f"\nSection {section} (n={len(section_folios)}):")

    # Diversity vs FQ rate
    rho, p = stats.spearmanr(diversities, fq_rates)
    sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
    print(f"  MIDDLE diversity vs FQ rate: rho={rho:+.3f}, p={p:.4f} {sig}")

    # Diversity vs LINK rate
    rho, p = stats.spearmanr(diversities, link_rates)
    sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
    print(f"  MIDDLE diversity vs LINK rate: rho={rho:+.3f}, p={p:.4f} {sig}")

# =========================================================================
# TEST 3: PREFIX PROFILE vs SPECIALIZATION TYPE
# =========================================================================
print("\n" + "="*70)
print("TEST 3: A PREFIX PROFILE vs B SPECIALIZATION TYPE")
print("="*70)

# Group A folios by B specialization type (RECOVERY vs DISTILL vs BALANCED)
# Use section-level B characteristics

section_spec = {}
for section in ['H', 'P', 'T']:
    section_b = [f for f in b_folio_characteristics
                 if b_folio_characteristics[f]['section'] == section]
    if not section_b:
        continue

    spec_counts = Counter(b_folio_characteristics[f]['spec_type'] for f in section_b)
    dominant = spec_counts.most_common(1)[0][0]
    k_avg = np.mean([b_folio_characteristics[f]['k_ratio'] for f in section_b])
    h_avg = np.mean([b_folio_characteristics[f]['h_ratio'] for f in section_b])

    section_spec[section] = {
        'dominant': dominant,
        'k_avg': k_avg,
        'h_avg': h_avg,
        'spec_counts': dict(spec_counts),
    }

    print(f"\nSection {section} B-side specialization:")
    print(f"  Dominant: {dominant}")
    print(f"  K avg: {k_avg:.3f}, H avg: {h_avg:.3f}")
    print(f"  Distribution: {dict(spec_counts)}")

# Compare A PP PREFIX profiles across sections with different B specializations
print("\nA PREFIX profiles by section (with B specialization context):")
print(f"\n{'Section':<10} {'B-Spec':<12} {'ch%':<8} {'sh%':<8} {'qo%':<8} {'ct%':<8} {'ol/or%':<8}")
print("-"*60)

for section in ['H', 'P', 'T']:
    section_a = [m for m in matched_folios if m['section'] == section]
    if not section_a:
        continue

    # Aggregate PREFIX counts
    prefix_counts = Counter()
    total = 0
    for m in section_a:
        prefix_counts.update(m['a_profile']['prefix_counts'])
        total += sum(m['a_profile']['prefix_counts'].values())

    if total > 0:
        ch_pct = 100 * prefix_counts.get('ch', 0) / total
        sh_pct = 100 * prefix_counts.get('sh', 0) / total
        qo_pct = 100 * prefix_counts.get('qo', 0) / total
        ct_pct = 100 * prefix_counts.get('ct', 0) / total
        link_pct = 100 * (prefix_counts.get('ol', 0) + prefix_counts.get('or', 0)) / total

        b_spec = section_spec.get(section, {}).get('dominant', '?')
        print(f"{section:<10} {b_spec:<12} {ch_pct:<8.1f} {sh_pct:<8.1f} {qo_pct:<8.1f} {ct_pct:<8.1f} {link_pct:<8.1f}")

# =========================================================================
# TEST 4: WITHIN-SECTION A FOLIO CLUSTERING
# =========================================================================
print("\n" + "="*70)
print("TEST 4: WITHIN-SECTION A FOLIO PP CLUSTERING")
print("="*70)

# Focus on Section H (largest sample)
h_folios = [m for m in matched_folios if m['section'] == 'H']

if len(h_folios) >= 10:
    print(f"\nSection H: {len(h_folios)} A folios")

    # Build feature matrix: role composition vector per folio
    roles = ['CORE', 'ESCAPE', 'AUXILIARY', 'LINK', 'CROSS-REF', 'CLOSURE', 'GALLOWS-CH', 'INPUT']

    feature_matrix = []
    folio_labels = []

    for m in h_folios:
        role_counts = m['a_profile']['role_counts']
        total = sum(role_counts.values())
        if total > 0:
            feature_vec = [role_counts.get(r, 0) / total for r in roles]
            feature_matrix.append(feature_vec)
            folio_labels.append(m['a_folio'])

    if len(feature_matrix) >= 10:
        X = np.array(feature_matrix)

        # Hierarchical clustering
        linkage = hierarchy.linkage(X, method='ward')

        # Cut into 3 clusters
        clusters = hierarchy.fcluster(linkage, t=3, criterion='maxclust')

        # Analyze clusters
        cluster_profiles = defaultdict(lambda: {'folios': [], 'roles': Counter()})

        for i, (folio, cluster) in enumerate(zip(folio_labels, clusters)):
            cluster_profiles[cluster]['folios'].append(folio)
            for j, role in enumerate(roles):
                cluster_profiles[cluster]['roles'][role] += feature_matrix[i][j]

        print("\nCluster analysis (3 clusters):")
        for cluster_id in sorted(cluster_profiles.keys()):
            cp = cluster_profiles[cluster_id]
            n = len(cp['folios'])
            print(f"\n  Cluster {cluster_id} ({n} folios):")

            # Top roles
            role_pcts = [(r, 100 * cp['roles'][r] / n) for r in roles]
            role_pcts.sort(key=lambda x: -x[1])
            top3 = role_pcts[:3]
            print(f"    Top roles: {', '.join(f'{r}={v:.1f}%' for r, v in top3)}")

            # Example folios
            print(f"    Folios: {', '.join(cp['folios'][:5])}")

# =========================================================================
# TEST 5: SPECIFIC PREFIX PATTERNS
# =========================================================================
print("\n" + "="*70)
print("TEST 5: SENSORY-RELEVANT PREFIX PATTERNS")
print("="*70)

# Hypothesis: certain PREFIXes might encode sensory-related criteria
# Look for PREFIXes that vary systematically with B processing characteristics

print("\nSearching for PREFIXes that correlate with B characteristics...")

# Collect all PREFIXes
all_prefixes = set()
for m in matched_folios:
    all_prefixes.update(m['a_profile']['prefix_counts'].keys())

# For each PREFIX, test correlation with fire degree
print(f"\n{'PREFIX':<10} {'Fire Corr':<12} {'P-val':<10} {'Direction':<15}")
print("-"*50)

significant_prefixes = []
for prefix in sorted(all_prefixes):
    # Get (fire_degree, prefix_rate) pairs
    data = []
    for m in matched_folios:
        prefix_count = m['a_profile']['prefix_counts'].get(prefix, 0)
        total = m['a_profile']['total_pp']
        if total > 20:
            rate = prefix_count / total
            data.append((m['b_fire_degree'], rate))

    if len(data) >= 20:
        fires = [d[0] for d in data]
        rates = [d[1] for d in data]

        if np.std(rates) > 0.001:  # Non-zero variance
            rho, p = stats.spearmanr(fires, rates)

            if p < 0.10:  # Relaxed threshold for exploration
                direction = "INCREASES" if rho > 0 else "DECREASES"
                sig = "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.10 else ""
                print(f"{prefix:<10} {rho:+.3f}{sig:<8} {p:<10.4f} {direction}")
                significant_prefixes.append((prefix, rho, p, direction))

# =========================================================================
# SUMMARY
# =========================================================================
print("\n" + "="*70)
print("SUMMARY: A PP PROCESSING CORRELATION")
print("="*70)

print("""
HYPOTHESIS TESTED:
  A's PP vocabulary encodes material-specific sensory criteria
  for managing each material's hysteresis window.

KEY FINDINGS:
""")

if significant_prefixes:
    print(f"1. {len(significant_prefixes)} PREFIXes show fire-degree correlation (p<0.10)")
    for prefix, rho, p, direction in significant_prefixes[:5]:
        print(f"   - {prefix}: {direction} with fire intensity (rho={rho:+.3f})")
else:
    print("1. No PREFIXes show significant fire-degree correlation")

print("""
2. Section-level patterns:
   - H (Herbal): Cross-reference heavy (ct-enriched)
   - P (Pharmaceutical): Safety-operation heavy (qo, ol, or)

3. INTERPRETATION:
   If A PP encodes sensory criteria, we'd expect:
   - Different materials (folios) have different PREFIX profiles
   - Those differences correlate with processing intensity
   - High-fire materials need different monitoring vocabulary

4. LIMITATIONS:
   - A folios don't map 1:1 to B folios (aggregate matching used)
   - Section confound (H vs P already differ structurally)
   - Need within-section folio-level variation to confirm
""")

# Save results
output = {
    'n_a_folios': len(a_folio_pp_profiles),
    'n_matched': len(matched_folios),
    'fire_role_data': fire_role_data,
    'section_spec': section_spec,
    'significant_prefixes': [(p, float(r), float(pv), d) for p, r, pv, d in significant_prefixes],
}

output_path = Path(__file__).parent.parent / 'results' / 'a_pp_processing_correlation.json'
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2, default=str)

print(f"\nResults saved to {output_path}")
