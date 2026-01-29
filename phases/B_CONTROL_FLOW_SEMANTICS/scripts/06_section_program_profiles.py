"""
06_section_program_profiles.py

Do different sections run different programs?
"""
import sys
import json
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

# Load class map
class_map_path = Path(__file__).resolve().parents[3] / "phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json"
with open(class_map_path) as f:
    class_data = json.load(f)

token_to_role = class_data['token_to_role']

# Section definitions (from C552)
SECTIONS = {
    'HERBAL_B': ['f26v', 'f27r', 'f27v', 'f28r', 'f28v', 'f29r', 'f29v', 'f30r', 'f30v',
                 'f31r', 'f31v', 'f32r', 'f32v', 'f33r', 'f33v', 'f34r', 'f34v', 'f35r', 'f35v',
                 'f36r', 'f36v', 'f37r', 'f37v', 'f38r', 'f38v', 'f39r', 'f39v', 'f40r', 'f40v',
                 'f41r', 'f41v', 'f42r', 'f42v', 'f43r', 'f43v', 'f44r', 'f44v', 'f45r', 'f45v',
                 'f46r', 'f46v', 'f47r', 'f47v', 'f48r', 'f48v', 'f49r', 'f49v', 'f50r', 'f50v',
                 'f51r', 'f51v', 'f52r', 'f52v', 'f53r', 'f53v', 'f54r', 'f54v', 'f55r', 'f55v',
                 'f56r', 'f56v'],
    'PHARMA': ['f88r', 'f88v', 'f89r1', 'f89r2', 'f89v1', 'f89v2', 'f90r1', 'f90r2', 'f90v1', 'f90v2',
               'f99r', 'f99v', 'f100r', 'f100v', 'f101r1', 'f101v2', 'f102r1', 'f102r2', 'f102v1', 'f102v2'],
    'BIO': ['f75r', 'f75v', 'f76r', 'f76v', 'f77r', 'f77v', 'f78r', 'f78v', 'f79r', 'f79v',
            'f80r', 'f80v', 'f81r', 'f81v', 'f82r', 'f82v', 'f83r', 'f83v', 'f84r', 'f84v'],
    'RECIPE_B': ['f103r', 'f103v', 'f104r', 'f104v', 'f105r', 'f105v', 'f106r', 'f106v',
                 'f107r', 'f107v', 'f108r', 'f108v', 'f111r', 'f111v', 'f112r', 'f112v',
                 'f113r', 'f113v', 'f114r', 'f114v', 'f115r', 'f115v', 'f116r', 'f116v']
}

# Build folio to section map
folio_to_section = {}
for section, folios in SECTIONS.items():
    for folio in folios:
        folio_to_section[folio] = section

tx = Transcript()

print("=" * 70)
print("Section Program Profiles")
print("=" * 70)

# Build section profiles
section_profiles = defaultdict(lambda: {
    'tokens': 0,
    'roles': Counter(),
    'kernel_counts': {'k': 0, 'h': 0, 'e': 0},
    'fl_count': 0,
    'fq_count': 0,
    'folios': set()
})

for t in tx.currier_b():
    section = folio_to_section.get(t.folio, 'OTHER')
    profile = section_profiles[section]

    profile['tokens'] += 1
    profile['folios'].add(t.folio)

    role = token_to_role.get(t.word, 'UN')
    profile['roles'][role] += 1

    if 'k' in t.word:
        profile['kernel_counts']['k'] += 1
    if 'h' in t.word:
        profile['kernel_counts']['h'] += 1
    if 'e' in t.word:
        profile['kernel_counts']['e'] += 1

    if role == 'FLOW_OPERATOR':
        profile['fl_count'] += 1
    if role == 'FREQUENT_OPERATOR':
        profile['fq_count'] += 1

# Report
print("\n" + "=" * 70)
print("Section Overview")
print("=" * 70)

print(f"\n{'Section':12} {'Folios':>8} {'Tokens':>8} {'k-rate':>8} {'h-rate':>8} {'e-rate':>8}")
print("-" * 60)

for section in ['HERBAL_B', 'BIO', 'PHARMA', 'RECIPE_B', 'OTHER']:
    if section not in section_profiles:
        continue
    p = section_profiles[section]
    k_rate = p['kernel_counts']['k'] / p['tokens'] * 100 if p['tokens'] > 0 else 0
    h_rate = p['kernel_counts']['h'] / p['tokens'] * 100 if p['tokens'] > 0 else 0
    e_rate = p['kernel_counts']['e'] / p['tokens'] * 100 if p['tokens'] > 0 else 0

    print(f"{section:12} {len(p['folios']):8} {p['tokens']:8} {k_rate:7.1f}% {h_rate:7.1f}% {e_rate:7.1f}%")

print("\n" + "=" * 70)
print("Role Distribution by Section")
print("=" * 70)

roles = ['ENERGY_OPERATOR', 'FLOW_OPERATOR', 'FREQUENT_OPERATOR', 'CORE_CONTROL', 'AUXILIARY', 'UN']
role_abbrev = {'ENERGY_OPERATOR': 'EN', 'FLOW_OPERATOR': 'FL', 'FREQUENT_OPERATOR': 'FQ',
               'CORE_CONTROL': 'CC', 'AUXILIARY': 'AX', 'UN': 'UN'}

print(f"\n{'Section':12}", end='')
for r in ['EN', 'FL', 'FQ', 'CC', 'AX']:
    print(f"{r:>8}", end='')
print()
print("-" * 52)

for section in ['HERBAL_B', 'BIO', 'PHARMA', 'RECIPE_B']:
    if section not in section_profiles:
        continue
    p = section_profiles[section]
    total = p['tokens']

    print(f"{section:12}", end='')
    for role in roles[:-1]:  # Skip UN
        count = p['roles'].get(role, 0)
        pct = count / total * 100 if total > 0 else 0
        print(f"{pct:7.1f}%", end='')
    print()

print("\n" + "=" * 70)
print("FL and FQ Rates by Section")
print("=" * 70)

print(f"\n{'Section':12} {'FL rate':>10} {'FQ rate':>10} {'FL/FQ ratio':>12}")
print("-" * 46)

for section in ['HERBAL_B', 'BIO', 'PHARMA', 'RECIPE_B']:
    if section not in section_profiles:
        continue
    p = section_profiles[section]
    fl_rate = p['fl_count'] / p['tokens'] * 100 if p['tokens'] > 0 else 0
    fq_rate = p['fq_count'] / p['tokens'] * 100 if p['tokens'] > 0 else 0
    ratio = fl_rate / fq_rate if fq_rate > 0 else 0

    print(f"{section:12} {fl_rate:9.1f}% {fq_rate:9.1f}% {ratio:11.2f}")

# Interpretation
print("\n" + "=" * 70)
print("Section Program Interpretation")
print("=" * 70)

# Find extremes
sections = ['HERBAL_B', 'BIO', 'PHARMA', 'RECIPE_B']
en_rates = {s: section_profiles[s]['roles'].get('ENERGY_OPERATOR', 0) / section_profiles[s]['tokens'] * 100
            for s in sections if s in section_profiles}
fl_rates = {s: section_profiles[s]['fl_count'] / section_profiles[s]['tokens'] * 100
            for s in sections if s in section_profiles}
fq_rates = {s: section_profiles[s]['fq_count'] / section_profiles[s]['tokens'] * 100
            for s in sections if s in section_profiles}

max_en = max(en_rates, key=en_rates.get)
max_fl = max(fl_rates, key=fl_rates.get)
max_fq = max(fq_rates, key=fq_rates.get)

print(f"""
SECTION CHARACTERISTICS:

Highest EN (processing intensity): {max_en} ({en_rates[max_en]:.1f}%)
Highest FL (state marking): {max_fl} ({fl_rates[max_fl]:.1f}%)
Highest FQ (escape need): {max_fq} ({fq_rates[max_fq]:.1f}%)

INTERPRETATION:

- Sections with HIGH EN = intensive processing programs
- Sections with HIGH FL = state-heavy programs (tracking material)
- Sections with HIGH FQ = error-prone or complex programs
- Sections with HIGH FL/FQ ratio = stable programs
- Sections with LOW FL/FQ ratio = unstable/complex programs
""")

# Save results
results = {
    'sections': {}
}

for section in ['HERBAL_B', 'BIO', 'PHARMA', 'RECIPE_B', 'OTHER']:
    if section not in section_profiles:
        continue
    p = section_profiles[section]
    results['sections'][section] = {
        'folio_count': len(p['folios']),
        'token_count': p['tokens'],
        'kernel_rates': {
            'k': round(p['kernel_counts']['k'] / p['tokens'] * 100, 2) if p['tokens'] > 0 else 0,
            'h': round(p['kernel_counts']['h'] / p['tokens'] * 100, 2) if p['tokens'] > 0 else 0,
            'e': round(p['kernel_counts']['e'] / p['tokens'] * 100, 2) if p['tokens'] > 0 else 0
        },
        'role_rates': {role_abbrev.get(r, r): round(c / p['tokens'] * 100, 2)
                       for r, c in p['roles'].items() if p['tokens'] > 0},
        'fl_rate': round(p['fl_count'] / p['tokens'] * 100, 2) if p['tokens'] > 0 else 0,
        'fq_rate': round(p['fq_count'] / p['tokens'] * 100, 2) if p['tokens'] > 0 else 0
    }

results_dir = Path(__file__).parent.parent / "results"
output_path = results_dir / "section_program_profiles.json"
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nSaved to {output_path}")
