"""Build operational profiles for all 82 Currier B folios.

Extracts per-folio vectors: prep MIDDLEs, thermo MIDDLEs, kernel ratios,
suffix control-flow rates, material/output categories, paragraph count.

Output: results/folio_operational_profiles.json
"""
import json
import sys
from collections import Counter, defaultdict

sys.path.insert(0, '.')
from scripts.voynich import BFolioDecoder, Transcript, Morphology

# --- Config ---
PREP_MIDDLES = {'te', 'pch', 'lch', 'tch'}
THERMO_MIDDLES = {'ke', 'kch'}
CHECKPOINT_SUFFIXES = {'aiin', 'ain'}
ITERATION_SUFFIXES = {'iin'}
TERMINAL_SUFFIXES = {'y', 'dy', 'ry', 'oly', 'am', 'om', 'im'}

# --- Get all B folios ---
tx = Transcript()
b_folios = sorted(set(t.folio for t in tx.currier_b()))
print(f"Found {len(b_folios)} Currier B folios")

# --- Build decoder (expensive, do once) ---
decoder = BFolioDecoder()
morph = Morphology()

profiles = []

for i, folio in enumerate(b_folios):
    folio_tokens = [t for t in tx.currier_b() if t.folio == folio]
    if not folio_tokens:
        continue

    # Analyze folio
    analysis = decoder.analyze_folio(folio)
    if not analysis:
        continue

    # Count prep and thermo MIDDLEs from raw morphology
    prep_counts = Counter()
    thermo_counts = Counter()
    suffix_counts = Counter()
    total_suffixes = 0
    paragraph_ids = set()

    for t in folio_tokens:
        m = morph.extract(t.word)
        if m and m.middle:
            # Check prep MIDDLEs (exact match or contained)
            for pm in PREP_MIDDLES:
                if m.middle == pm or (len(m.middle) > len(pm) and pm in m.middle):
                    prep_counts[pm] += 1
            # Check thermo MIDDLEs
            for tm in THERMO_MIDDLES:
                if m.middle == tm or (len(m.middle) > len(tm) and tm in m.middle):
                    thermo_counts[tm] += 1

        if m and m.suffix:
            total_suffixes += 1
            if m.suffix in CHECKPOINT_SUFFIXES:
                suffix_counts['checkpoint'] += 1
            if m.suffix in ITERATION_SUFFIXES:
                suffix_counts['iteration'] += 1
            if m.suffix in TERMINAL_SUFFIXES:
                suffix_counts['terminal'] += 1

        # Track paragraphs (from line ID: P1.L1 → P1)
        if '.' in t.line:
            paragraph_ids.add(t.line.split('.')[0])
        else:
            paragraph_ids.add(t.line)

    # Kernel ratios
    kd = analysis.kernel_dist
    k_total = sum(kd.values()) or 1
    k_ratio = kd.get('k', 0) / k_total
    h_ratio = kd.get('h', 0) / k_total
    e_ratio = kd.get('e', 0) / k_total

    # Suffix rates
    ts = total_suffixes or 1
    iteration_rate = suffix_counts.get('iteration', 0) / ts
    checkpoint_rate = suffix_counts.get('checkpoint', 0) / ts
    terminal_rate = suffix_counts.get('terminal', 0) / ts

    # Prep proportions (normalize to per-token)
    tc = analysis.token_count or 1
    profile = {
        'folio': folio,
        'token_count': analysis.token_count,
        'paragraph_count': len(paragraph_ids),
        # Prep MIDDLEs (per-token rates)
        'prep_te': prep_counts.get('te', 0) / tc,
        'prep_pch': prep_counts.get('pch', 0) / tc,
        'prep_lch': prep_counts.get('lch', 0) / tc,
        'prep_tch': prep_counts.get('tch', 0) / tc,
        # Thermo MIDDLEs (per-token rates)
        'thermo_ke': thermo_counts.get('ke', 0) / tc,
        'thermo_kch': thermo_counts.get('kch', 0) / tc,
        # Kernel ratios
        'k_ratio': round(k_ratio, 4),
        'h_ratio': round(h_ratio, 4),
        'e_ratio': round(e_ratio, 4),
        # Suffix control-flow rates
        'iteration_rate': round(iteration_rate, 4),
        'checkpoint_rate': round(checkpoint_rate, 4),
        'terminal_rate': round(terminal_rate, 4),
        # Categorical
        'material_category': analysis.material_category,
        'output_category': analysis.output_category,
        'kernel_balance': analysis.kernel_balance,
        # Raw counts for reference
        'raw_prep_counts': dict(prep_counts),
        'raw_thermo_counts': dict(thermo_counts),
        'raw_kernel_dist': dict(kd),
    }
    profiles.append(profile)

    if (i + 1) % 10 == 0:
        print(f"  Processed {i + 1}/{len(b_folios)} folios...")

# --- Output ---
output = {
    'title': 'Voynich B Folio Operational Profiles',
    'folio_count': len(profiles),
    'dimensions': [
        'prep_te', 'prep_pch', 'prep_lch', 'prep_tch',
        'thermo_ke', 'thermo_kch',
        'k_ratio', 'h_ratio', 'e_ratio',
        'iteration_rate', 'checkpoint_rate', 'terminal_rate',
    ],
    'profiles': profiles,
}

with open('results/folio_operational_profiles.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"\nWrote {len(profiles)} folio profiles to results/folio_operational_profiles.json")

# --- Quick summary ---
cats = Counter(p['material_category'] for p in profiles)
outs = Counter(p['output_category'] for p in profiles)
bals = Counter(p['kernel_balance'] for p in profiles)
print(f"\nMaterial categories: {dict(cats)}")
print(f"Output categories: {dict(outs)}")
print(f"Kernel balance: {dict(bals)}")

# Mean prep rates
for dim in ['prep_te', 'prep_pch', 'prep_lch', 'prep_tch', 'thermo_ke', 'thermo_kch']:
    vals = [p[dim] for p in profiles]
    mean_val = sum(vals) / len(vals) if vals else 0
    nonzero = sum(1 for v in vals if v > 0)
    print(f"  {dim}: mean={mean_val:.4f}, nonzero={nonzero}/{len(profiles)}")
