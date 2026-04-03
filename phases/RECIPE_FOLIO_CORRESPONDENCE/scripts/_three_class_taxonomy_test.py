"""Test whether the three dark pipeline classes (equipment/process/material) are
structurally distinguishable beyond frequency differences.

If the taxonomy is real, the classes should differ on measurable dimensions
AFTER controlling for folio span (frequency)."""
import sys, io, json, math
from collections import Counter, defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

with open('C:/git/voynich/data/dark_pipeline_middles.json', encoding='utf-8') as f:
    dp_set = set(json.load(f)['middles'])

all_b = [t for t in tx.currier_b() if t.word.strip() and not t.is_label]

# Three classes from the dictionary
EQUIPMENT = ['lch', 'lk', 'eed']
PROCESS = ['cth', 'lsh', 'eet', 'ksh', 'ir', 'eke', 'tsh', 'ro', 'ep', 'cfh', 'dyt', 'es', 'ta', 'octh', 'ockh', 'eok']
MATERIAL = ['fch', 'cs', 'eckh', 'rai']

ALL_TESTED = EQUIPMENT + PROCESS + MATERIAL
CLASS_MAP = {}
for m in EQUIPMENT: CLASS_MAP[m] = 'EQUIPMENT'
for m in PROCESS: CLASS_MAP[m] = 'PROCESS'
for m in MATERIAL: CLASS_MAP[m] = 'MATERIAL'

# Build per-dark-MIDDLE structural profiles
all_folios = sorted(set(t.folio for t in all_b))
folio_tokens = {f: [t for t in all_b if t.folio == f] for f in all_folios}

# For each dark MIDDLE, compute structural features
profiles = {}
for dark_mid in ALL_TESTED:
    tokens = []
    for t in all_b:
        m = morph.extract(t.word)
        if m.middle == dark_mid:
            tokens.append(t)

    if len(tokens) < 3:
        continue

    n = len(tokens)
    folios = set(t.folio for t in tokens)
    n_folios = len(folios)
    sections = Counter(t.section for t in tokens)

    # 1. PREFIX affiliation strength (entropy of PREFIX distribution)
    prefixes = Counter()
    for t in tokens:
        a = morph.atomize(t.word)
        if a.prefix:
            prefixes[a.prefix] += 1
        else:
            prefixes['BARE'] += 1
    total_pfx = sum(prefixes.values())
    pfx_entropy = 0
    for count in prefixes.values():
        p = count / total_pfx
        if p > 0:
            pfx_entropy -= p * math.log2(p)
    # Normalize by max possible entropy
    max_entropy = math.log2(len(prefixes)) if len(prefixes) > 1 else 1
    pfx_concentration = 1 - (pfx_entropy / max_entropy) if max_entropy > 0 else 1
    # Top PREFIX share
    top_pfx, top_count = prefixes.most_common(1)[0]
    top_pfx_share = top_count / total_pfx

    # 2. Section modulation (how much does usage vary by section?)
    section_counts = Counter()
    section_totals = Counter()
    for f in all_folios:
        f_toks = folio_tokens[f]
        if not f_toks:
            continue
        sec = f_toks[0].section
        section_totals[sec] += len(f_toks)
        for t in f_toks:
            m_ext = morph.extract(t.word)
            if m_ext.middle == dark_mid:
                section_counts[sec] += 1

    # Section CV (coefficient of variation of per-section rates)
    section_rates = []
    for sec in section_totals:
        if section_totals[sec] > 100:
            rate = 1000 * section_counts.get(sec, 0) / section_totals[sec]
            section_rates.append(rate)
    if len(section_rates) >= 2:
        mean_rate = sum(section_rates) / len(section_rates)
        var_rate = sum((r - mean_rate)**2 for r in section_rates) / len(section_rates)
        section_cv = math.sqrt(var_rate) / mean_rate if mean_rate > 0 else 0
    else:
        section_cv = 0

    # 3. Line position (mean normalized position within line)
    positions = []
    for t in tokens:
        line_toks = [x for x in folio_tokens[t.folio] if x.line == t.line]
        if len(line_toks) > 1:
            idx = next((i for i, x in enumerate(line_toks) if x.word == t.word and x is t), 0)
            positions.append(idx / (len(line_toks) - 1))
    mean_pos = sum(positions) / len(positions) if positions else 0.5

    # 4. Paragraph-initial rate
    par_init = sum(1 for t in tokens if t.par_initial)
    par_init_rate = par_init / n

    # 5. Line-initial rate
    line_init = sum(1 for t in tokens if t.line_initial)
    line_init_rate = line_init / n

    # 6. Co-occurrence with other dark MIDDLEs on same line
    same_line_darks = Counter()
    for t in tokens:
        line_toks = [x for x in folio_tokens[t.folio] if x.line == t.line]
        for x in line_toks:
            if x is not t:
                m_ext = morph.extract(x.word)
                if m_ext.middle and m_ext.middle in dp_set and m_ext.middle != dark_mid:
                    same_line_darks[m_ext.middle] += 1
    dark_cooccurrence_rate = sum(same_line_darks.values()) / n if n > 0 else 0

    # 7. Suffix diversity
    suffixes = Counter()
    for t in tokens:
        m_ext = morph.extract(t.word)
        if m_ext.suffix:
            suffixes[m_ext.suffix] += 1
        else:
            suffixes['BARE'] += 1
    n_suffix_types = len(suffixes)

    profiles[dark_mid] = {
        'class': CLASS_MAP[dark_mid],
        'n_tokens': n,
        'n_folios': n_folios,
        'pfx_concentration': pfx_concentration,
        'top_pfx': top_pfx,
        'top_pfx_share': top_pfx_share,
        'section_cv': section_cv,
        'mean_line_pos': mean_pos,
        'par_init_rate': par_init_rate,
        'line_init_rate': line_init_rate,
        'dark_cooccurrence': dark_cooccurrence_rate,
        'n_suffix_types': n_suffix_types,
    }

# Print profiles by class
print("=" * 120)
print("DARK PIPELINE THREE-CLASS TAXONOMY: STRUCTURAL DISTINGUISHABILITY TEST")
print("=" * 120)

header = (f"{'MIDDLE':>6s} {'Class':>10s} {'Tok':>4s} {'Fol':>4s} {'PfxConc':>7s} {'TopPfx':>6s} {'TopSh%':>6s} "
          f"{'SecCV':>6s} {'LinePos':>7s} {'ParInit':>7s} {'LnInit':>7s} {'DkCooc':>6s} {'SfxTyp':>6s}")
print(header)
print("-" * 120)

for cls in ['EQUIPMENT', 'PROCESS', 'MATERIAL']:
    for mid in sorted(profiles, key=lambda m: -profiles[m]['n_tokens']):
        p = profiles[mid]
        if p['class'] != cls:
            continue
        print(f"  {mid:>6s} {p['class']:>10s} {p['n_tokens']:4d} {p['n_folios']:4d} {p['pfx_concentration']:7.3f} "
              f"{p['top_pfx']:>6s} {p['top_pfx_share']:6.2f} {p['section_cv']:6.2f} {p['mean_line_pos']:7.3f} "
              f"{p['par_init_rate']:7.3f} {p['line_init_rate']:7.3f} {p['dark_cooccurrence']:6.2f} {p['n_suffix_types']:6d}")
    print()

# Class-level averages
print("\n" + "=" * 120)
print("CLASS AVERAGES (controlling for frequency by averaging per-MIDDLE, not per-token)")
print("=" * 120)

for cls in ['EQUIPMENT', 'PROCESS', 'MATERIAL']:
    members = [p for p in profiles.values() if p['class'] == cls]
    if not members:
        continue
    n_members = len(members)
    avg = {}
    for key in ['pfx_concentration', 'top_pfx_share', 'section_cv', 'mean_line_pos',
                'par_init_rate', 'line_init_rate', 'dark_cooccurrence', 'n_suffix_types',
                'n_tokens', 'n_folios']:
        avg[key] = sum(m[key] for m in members) / n_members

    print(f"\n  {cls} ({n_members} members, avg {avg['n_tokens']:.0f} tok, {avg['n_folios']:.0f} folios):")
    print(f"    PREFIX concentration:  {avg['pfx_concentration']:.3f} (1.0 = one PREFIX only, 0.0 = uniform)")
    print(f"    Top PREFIX share:      {avg['top_pfx_share']:.2f}")
    print(f"    Section CV:            {avg['section_cv']:.2f} (higher = more section-specific)")
    print(f"    Mean line position:    {avg['mean_line_pos']:.3f} (0.0 = line-initial, 1.0 = line-final)")
    print(f"    Paragraph-initial %:   {avg['par_init_rate']:.3f}")
    print(f"    Line-initial %:        {avg['line_init_rate']:.3f}")
    print(f"    Dark co-occurrence:    {avg['dark_cooccurrence']:.2f} (other darks on same line)")
    print(f"    Suffix types:          {avg['n_suffix_types']:.1f}")

# Statistical test: are the classes distinguishable on each dimension?
print("\n\n" + "=" * 120)
print("DIMENSION-BY-DIMENSION CLASS SEPARATION")
print("=" * 120)

dims = ['pfx_concentration', 'top_pfx_share', 'section_cv', 'mean_line_pos',
        'par_init_rate', 'line_init_rate', 'dark_cooccurrence', 'n_suffix_types']

for dim in dims:
    vals = {'EQUIPMENT': [], 'PROCESS': [], 'MATERIAL': []}
    for mid, p in profiles.items():
        vals[p['class']].append(p[dim])

    # Check if any class is clearly separated
    e_mean = sum(vals['EQUIPMENT']) / len(vals['EQUIPMENT']) if vals['EQUIPMENT'] else 0
    p_mean = sum(vals['PROCESS']) / len(vals['PROCESS']) if vals['PROCESS'] else 0
    m_mean = sum(vals['MATERIAL']) / len(vals['MATERIAL']) if vals['MATERIAL'] else 0

    # Overall mean and variance
    all_vals = vals['EQUIPMENT'] + vals['PROCESS'] + vals['MATERIAL']
    overall_mean = sum(all_vals) / len(all_vals) if all_vals else 0

    # Between-class variance / total variance (eta-squared approximation)
    between = (len(vals['EQUIPMENT']) * (e_mean - overall_mean)**2 +
               len(vals['PROCESS']) * (p_mean - overall_mean)**2 +
               len(vals['MATERIAL']) * (m_mean - overall_mean)**2)
    total = sum((v - overall_mean)**2 for v in all_vals)
    eta_sq = between / total if total > 0 else 0

    verdict = 'STRONG' if eta_sq > 0.25 else 'MODERATE' if eta_sq > 0.10 else 'WEAK'

    print(f"\n  {dim}:")
    print(f"    EQUIPMENT={e_mean:.3f}  PROCESS={p_mean:.3f}  MATERIAL={m_mean:.3f}")
    print(f"    eta²={eta_sq:.3f} ({verdict})")

# Overall assessment
print("\n\n" + "=" * 120)
print("OVERALL ASSESSMENT")
print("=" * 120)

strong = sum(1 for dim in dims for vals in [{'EQUIPMENT': [], 'PROCESS': [], 'MATERIAL': []}]
             if True)  # placeholder

# Recompute properly
strong_dims = []
moderate_dims = []
weak_dims = []
for dim in dims:
    vals = {'EQUIPMENT': [], 'PROCESS': [], 'MATERIAL': []}
    for mid, p in profiles.items():
        vals[p['class']].append(p[dim])
    e_mean = sum(vals['EQUIPMENT']) / len(vals['EQUIPMENT']) if vals['EQUIPMENT'] else 0
    p_mean = sum(vals['PROCESS']) / len(vals['PROCESS']) if vals['PROCESS'] else 0
    m_mean = sum(vals['MATERIAL']) / len(vals['MATERIAL']) if vals['MATERIAL'] else 0
    all_vals = vals['EQUIPMENT'] + vals['PROCESS'] + vals['MATERIAL']
    overall_mean = sum(all_vals) / len(all_vals) if all_vals else 0
    between = (len(vals['EQUIPMENT']) * (e_mean - overall_mean)**2 +
               len(vals['PROCESS']) * (p_mean - overall_mean)**2 +
               len(vals['MATERIAL']) * (m_mean - overall_mean)**2)
    total = sum((v - overall_mean)**2 for v in all_vals)
    eta_sq = between / total if total > 0 else 0
    if eta_sq > 0.25:
        strong_dims.append(dim)
    elif eta_sq > 0.10:
        moderate_dims.append(dim)
    else:
        weak_dims.append(dim)

print(f"\n  Dimensions with STRONG class separation (eta² > 0.25): {len(strong_dims)}")
for d in strong_dims:
    print(f"    {d}")
print(f"  Dimensions with MODERATE separation (eta² 0.10-0.25): {len(moderate_dims)}")
for d in moderate_dims:
    print(f"    {d}")
print(f"  Dimensions with WEAK separation (eta² < 0.10): {len(weak_dims)}")
for d in weak_dims:
    print(f"    {d}")

if len(strong_dims) >= 2:
    print(f"\n  VERDICT: TAXONOMY STRUCTURALLY SUPPORTED — {len(strong_dims)} dimensions strongly separate classes")
elif len(strong_dims) + len(moderate_dims) >= 3:
    print(f"\n  VERDICT: TAXONOMY PARTIALLY SUPPORTED — {len(strong_dims)} strong + {len(moderate_dims)} moderate dimensions")
else:
    print(f"\n  VERDICT: TAXONOMY NOT STRUCTURALLY DISTINGUISHABLE — may be frequency artifact")
