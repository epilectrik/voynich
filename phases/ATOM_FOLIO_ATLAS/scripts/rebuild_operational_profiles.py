"""
Rebuild folio operational profiles using atomize()-corrected features.

Replaces results/folio_operational_profiles.json with corrected values.
The key fix: thermo_ke and terminal_rate are recomputed using atomize()
which doesn't suffer from the -edy suffix stealing terminal 'e'.

Dimensions (matching Phase 628 schema):
  - prep_te, prep_pch, prep_lch, prep_tch: prefix prep rates
  - thermo_ke, thermo_kch: thermal prefix rates
  - k_ratio, h_ratio, e_ratio: kernel ratios (unchanged - these use kernel classification)
  - iteration_rate, checkpoint_rate, terminal_rate: structural rates
"""

import sys, io, json
from collections import Counter
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

all_b = [t for t in tx.currier_b() if t.word.strip() and not t.is_label]
folios = sorted(set(t.folio for t in all_b))

# Load the ORIGINAL profiles to preserve fields we don't recompute
with open(ROOT / 'results' / 'folio_operational_profiles.json', encoding='utf-8') as f:
    orig = json.load(f)

orig_by_folio = {}
for p in orig.get('profiles', []):
    orig_by_folio[p['folio']] = p

print(f"Rebuilding operational profiles for {len(folios)} folios using atomize()")

profiles = []

for folio in folios:
    toks = [t for t in all_b if t.folio == folio]
    n = len(toks)
    if n < 20:
        continue

    # Prefix counts using extract() (unchanged — prefix detection is the same)
    pre_counts = Counter()
    for t in toks:
        m = morph.extract(t.word)
        if m.prefix:
            pre_counts[m.prefix] += 1

    # Kernel ratios from extract() (unchanged — kernel is MIDDLE-based, not atom-based)
    # Keep original values
    orig_prof = orig_by_folio.get(folio, {})
    k_ratio = orig_prof.get('k_ratio', 0)
    h_ratio = orig_prof.get('h_ratio', 0)
    e_ratio = orig_prof.get('e_ratio', 0)

    # CORRECTED: thermo_ke using atomize()
    # Count tokens where PREFIX is qo/ko/ke AND e_depth >= 1
    thermo_ke_count = 0
    thermo_kch_count = 0
    for t in toks:
        a = morph.atomize(t.word)
        if a.prefix in ('qo', 'ko', 'ke', 'lk'):
            if a.e_depth >= 1:
                thermo_ke_count += 1
        if a.prefix in ('qo', 'ko', 'ke', 'lk'):
            # kch = thermal tokens with HEAD k and MOD containing c+h
            atoms = [c for c, r, g in a.atoms]
            if 'k' in atoms and 'c' in atoms and 'h' in atoms:
                thermo_kch_count += 1
    thermo_ke = thermo_ke_count / n
    thermo_kch = thermo_kch_count / n

    # CORRECTED: terminal_rate using atomize()
    # Count tokens with OPAQUE terminal (y, n, m) — this is what "terminal" means
    terminal_count = 0
    for t in toks:
        a = morph.atomize(t.word)
        if a.terminal_opacity == 'OPAQUE':
            terminal_count += 1
    terminal_rate = terminal_count / n

    # Prefix prep rates (unchanged — prefix detection same)
    prep_te = pre_counts.get('te', 0) / n
    prep_pch = pre_counts.get('pch', 0) / n
    prep_lch = pre_counts.get('lch', 0) / n
    prep_tch = pre_counts.get('tch', 0) / n

    # Iteration and checkpoint rates
    # iteration_rate: tokens with i-depth >= 1
    iter_count = sum(1 for t in toks if morph.atomize(t.word).i_depth >= 1)
    iteration_rate = iter_count / n

    # checkpoint_rate: ch-prefix tokens
    checkpoint_count = sum(1 for t in toks
                          if morph.atomize(t.word).prefix in ('ch', 'pch', 'tch', 'dch', 'lch', 'fch'))
    checkpoint_rate = checkpoint_count / n

    # Preserve other fields from original
    prof = {
        'folio': folio,
        'token_count': n,
        'paragraph_count': orig_prof.get('paragraph_count', 0),
        'prep_te': prep_te,
        'prep_pch': prep_pch,
        'prep_lch': prep_lch,
        'prep_tch': prep_tch,
        'thermo_ke': thermo_ke,
        'thermo_kch': thermo_kch,
        'k_ratio': k_ratio,
        'h_ratio': h_ratio,
        'e_ratio': e_ratio,
        'iteration_rate': iteration_rate,
        'checkpoint_rate': checkpoint_rate,
        'terminal_rate': terminal_rate,
        'material_category': orig_prof.get('material_category', 'UNKNOWN'),
        'output_category': orig_prof.get('output_category', 'UNKNOWN'),
        'kernel_balance': orig_prof.get('kernel_balance', 'UNKNOWN'),
    }
    profiles.append(prof)

# Output
output = {
    'title': 'Voynich B Folio Operational Profiles (atomize-corrected)',
    'folio_count': len(profiles),
    'dimensions': ['prep_te', 'prep_pch', 'prep_lch', 'prep_tch',
                   'thermo_ke', 'thermo_kch',
                   'k_ratio', 'h_ratio', 'e_ratio',
                   'iteration_rate', 'checkpoint_rate', 'terminal_rate'],
    'profiles': profiles,
    'correction_note': 'thermo_ke, terminal_rate, iteration_rate, checkpoint_rate recomputed via atomize() (C1897 fix). k_ratio, h_ratio, e_ratio preserved from original kernel classification.',
}

out_path = ROOT / 'results' / 'folio_operational_profiles_v2.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)
print(f"\nSaved: {out_path}")

# Show differences from original
print(f"\n{'=' * 80}")
print("CHANGES FROM ORIGINAL PROFILES")
print(f"{'=' * 80}")

changed_folios = 0
for prof in profiles:
    folio = prof['folio']
    orig_p = orig_by_folio.get(folio, {})
    if not orig_p:
        continue

    diffs = []
    for key in ['thermo_ke', 'terminal_rate', 'iteration_rate', 'checkpoint_rate']:
        old = orig_p.get(key, 0) or 0
        new = prof[key]
        if abs(old - new) > 0.001:
            diffs.append(f"{key}: {old:.4f} -> {new:.4f} ({new-old:+.4f})")

    if diffs:
        changed_folios += 1
        if changed_folios <= 10:  # Show first 10
            print(f"\n  {folio}:")
            for d in diffs:
                print(f"    {d}")

print(f"\n  Total folios with changes: {changed_folios}/{len(profiles)}")
print(f"\n{'=' * 80}")
print("DONE")
print(f"{'=' * 80}")
