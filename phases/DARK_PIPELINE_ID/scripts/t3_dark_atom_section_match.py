"""
T3: Do dark MIDDLE atom compositions match the operational profile of
their host sections?

If dark MIDDLEs are nominalized property descriptions, then:
- Dark MIDDLEs concentrated in thermal-heavy sections should have
  more k/e atoms (thermal/cooling properties)
- Dark MIDDLEs concentrated in monitoring-heavy sections should have
  more h/c atoms (watch/adjust properties)
- Dark MIDDLEs concentrated in flow-heavy sections should have
  more t/r atoms (transfer/respond properties)

Test: For each section, compare the atom composition of that section's
dark MIDDLEs to the section's GRAMMAR operational profile. If dark
MIDDLEs describe properties relevant to their section, the atom
profiles should correlate.

Also test: do dark MIDDLEs that are section-SELECTIVE (appearing in
few sections) have more extreme atom profiles than dark MIDDLEs that
are section-GENERIC (appearing everywhere)?
"""

import sys, os, io, json, math
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript, Morphology, ATOM_GLOSSES, HEAD_ATOMS

tx = Transcript()
morph = Morphology()

with open(ROOT / 'data' / 'dark_pipeline_middles.json', encoding='utf-8') as f:
    dp_set = set(json.load(f)['middles'])

from scripts.voynich import load_middle_classes
ri_middles, pp_middles = load_middle_classes()
bridge_set = pp_middles - dp_set

all_b = [t for t in tx.currier_b() if t.word.strip() and not t.is_label]

# ═══ SECTION PROFILES ═══
# For each section, compute the grammar token atom profile
# (what HEAD atoms dominate the grammar tokens?)

section_grammar_heads = defaultdict(Counter)  # section -> HEAD atom counter
section_grammar_total = defaultdict(int)
section_dark_mids = defaultdict(set)          # section -> set of dark MIDDLEs
section_dark_atoms = defaultdict(Counter)     # section -> atom counter across dark MIDDLEs

for t in all_b:
    m = morph.extract(t.word)
    mid = m.middle
    if not mid:
        continue
    sec = t.section

    if mid in dp_set:
        section_dark_mids[sec].add(mid)
        for c in mid:
            section_dark_atoms[sec][c] += 1
    elif mid not in dp_set:
        # Grammar token — get HEAD atom
        a = morph.atomize(t.word)
        for c, role, g in a.atoms:
            if role in ('HEAD', 'SOLE'):
                section_grammar_heads[sec][c] += 1
                section_grammar_total[sec] += 1

sections = sorted(section_grammar_heads.keys())
print(f"Sections: {sections}")

# ═══ SECTION GRAMMAR PROFILES ═══
print("\n" + "=" * 100)
print("SECTION GRAMMAR HEAD PROFILES (what operations dominate each section)")
print("=" * 100)

print(f"\n  {'Section':>8s}", end='')
for atom in 'keaot':
    print(f"  {atom}({ATOM_GLOSSES[atom]:>8s})", end='')
print(f"  {'Total':>7s}")
print(f"  {'-'*70}")

sec_head_pcts = {}
for sec in sections:
    total = section_grammar_total[sec]
    if total == 0:
        continue
    pcts = {}
    print(f"  {sec:>8s}", end='')
    for atom in 'keaot':
        ct = section_grammar_heads[sec].get(atom, 0)
        pct = 100 * ct / total
        pcts[atom] = pct
        print(f"  {pct:12.1f}%", end='')
    print(f"  {total:7d}")
    sec_head_pcts[sec] = pcts

# ═══ SECTION DARK ATOM PROFILES ═══
print("\n" + "=" * 100)
print("SECTION DARK MIDDLE ATOM PROFILES (what atoms are in section's dark MIDDLEs)")
print("=" * 100)

print(f"\n  {'Section':>8s} {'N_dark':>7s}", end='')
for atom in 'keaothdcpfislrnmy':
    print(f" {atom:>4s}", end='')
print()
print(f"  {'-'*100}")

sec_dark_pcts = {}
for sec in sections:
    dark_total = sum(section_dark_atoms[sec].values())
    if dark_total == 0:
        continue
    pcts = {}
    print(f"  {sec:>8s} {len(section_dark_mids[sec]):>7d}", end='')
    for atom in 'keaothdcpfislrnmy':
        ct = section_dark_atoms[sec].get(atom, 0)
        pct = 100 * ct / dark_total
        pcts[atom] = pct
        print(f" {pct:4.1f}", end='')
    print()
    sec_dark_pcts[sec] = pcts

# ═══ CORRELATION: Do dark atom profiles match grammar HEAD profiles? ═══
print("\n" + "=" * 100)
print("CORRELATION: Dark atom profile vs grammar HEAD profile per section")
print("=" * 100)

# For each HEAD atom (k,e,a,o,t), across sections:
# Does the fraction of that atom in dark MIDDLEs correlate with the
# fraction of that atom as HEAD in grammar tokens?

for atom in 'keaot':
    grammar_vals = []
    dark_vals = []
    sec_labels = []
    for sec in sections:
        if sec in sec_head_pcts and sec in sec_dark_pcts:
            grammar_vals.append(sec_head_pcts[sec].get(atom, 0))
            dark_vals.append(sec_dark_pcts[sec].get(atom, 0))
            sec_labels.append(sec)

    if len(grammar_vals) < 3:
        continue

    # Pearson correlation
    n = len(grammar_vals)
    mg = sum(grammar_vals) / n
    md = sum(dark_vals) / n
    cov = sum((grammar_vals[i] - mg) * (dark_vals[i] - md) for i in range(n)) / n
    sg = (sum((x - mg)**2 for x in grammar_vals) / n) ** 0.5
    sd = (sum((x - md)**2 for x in dark_vals) / n) ** 0.5
    r = cov / (sg * sd) if sg > 0 and sd > 0 else 0

    print(f"\n  Atom '{atom}' ({ATOM_GLOSSES[atom]}):")
    print(f"    Grammar HEAD %: {['%.1f' % v for v in grammar_vals]}")
    print(f"    Dark atom %:    {['%.1f' % v for v in dark_vals]}")
    print(f"    Sections:       {sec_labels}")
    print(f"    Correlation: r = {r:.3f}  {'POSITIVE' if r > 0.3 else 'NEGATIVE' if r < -0.3 else 'WEAK'}")

# ═══ OVERALL PROFILE CORRELATION ═══
print("\n" + "=" * 100)
print("OVERALL: For each section, correlate its grammar HEAD profile")
print("with its dark atom profile (across the 5 HEAD atoms)")
print("=" * 100)

for sec in sections:
    if sec not in sec_head_pcts or sec not in sec_dark_pcts:
        continue
    g_vec = [sec_head_pcts[sec].get(a, 0) for a in 'keaot']
    d_vec = [sec_dark_pcts[sec].get(a, 0) for a in 'keaot']

    n = 5
    mg = sum(g_vec) / n
    md = sum(d_vec) / n
    cov = sum((g_vec[i] - mg) * (d_vec[i] - md) for i in range(n)) / n
    sg = (sum((x - mg)**2 for x in g_vec) / n) ** 0.5
    sd = (sum((x - md)**2 for x in d_vec) / n) ** 0.5
    r = cov / (sg * sd) if sg > 0 and sd > 0 else 0

    print(f"  {sec:>8s}: grammar=[{', '.join('%.1f' % v for v in g_vec)}] dark=[{', '.join('%.1f' % v for v in d_vec)}] r={r:.3f}")

# ═══ SELECTIVE vs GENERIC DARK MIDDLEs ═══
print("\n" + "=" * 100)
print("SELECTIVE vs GENERIC: Do section-specific dark MIDDLEs have")
print("more extreme atom profiles?")
print("=" * 100)

# For each dark MIDDLE, count how many sections it appears in
mid_sections = defaultdict(set)
for t in all_b:
    m = morph.extract(t.word)
    if m.middle and m.middle in dp_set:
        mid_sections[m.middle].add(t.section)

selective = []  # dark MIDDLEs in 1-2 sections
generic = []    # dark MIDDLEs in 3+ sections

for mid in dp_set:
    n_sec = len(mid_sections.get(mid, set()))
    if n_sec == 0:
        continue
    # Compute atom HEAD concentration (fraction of HEAD-class atoms)
    head_atoms_in_mid = sum(1 for c in mid if c in HEAD_ATOMS)
    head_frac = head_atoms_in_mid / len(mid) if mid else 0

    if n_sec <= 2:
        selective.append((mid, n_sec, head_frac, len(mid)))
    else:
        generic.append((mid, n_sec, head_frac, len(mid)))

print(f"\n  Selective (1-2 sections): {len(selective)} dark MIDDLEs")
print(f"  Generic (3+ sections): {len(generic)} dark MIDDLEs")

if selective and generic:
    sel_head = [h for _, _, h, _ in selective]
    gen_head = [h for _, _, h, _ in generic]
    sel_len = [l for _, _, _, l in selective]
    gen_len = [l for _, _, _, l in generic]

    print(f"\n  HEAD-atom fraction:")
    print(f"    Selective: mean={sum(sel_head)/len(sel_head):.3f}")
    print(f"    Generic:   mean={sum(gen_head)/len(gen_head):.3f}")

    print(f"  MIDDLE length:")
    print(f"    Selective: mean={sum(sel_len)/len(sel_len):.1f}")
    print(f"    Generic:   mean={sum(gen_len)/len(gen_len):.1f}")

    # Atom profile comparison
    sel_atoms = Counter()
    gen_atoms = Counter()
    for mid, _, _, _ in selective:
        for c in mid:
            sel_atoms[c] += 1
    for mid, _, _, _ in generic:
        for c in mid:
            gen_atoms[c] += 1

    sel_total = sum(sel_atoms.values())
    gen_total = sum(gen_atoms.values())

    print(f"\n  Atom profiles (selective vs generic):")
    print(f"  {'Atom':>6s} {'Sel%':>6s} {'Gen%':>6s} {'Ratio':>7s} {'Gloss':>10s}")
    print(f"  {'-'*45}")
    for atom in sorted(set(list(sel_atoms.keys()) + list(gen_atoms.keys())),
                       key=lambda a: -(sel_atoms.get(a,0)/sel_total if sel_total else 0)):
        sp = 100 * sel_atoms.get(atom, 0) / sel_total if sel_total else 0
        gp = 100 * gen_atoms.get(atom, 0) / gen_total if gen_total else 0
        ratio = sp / gp if gp > 0 else 99.9
        gloss = ATOM_GLOSSES.get(atom, '?')
        marker = ' **' if ratio > 1.5 or ratio < 0.67 else ''
        print(f"  {atom:>6s} {sp:6.1f} {gp:6.1f} {ratio:7.2f} {gloss:>10s}{marker}")

# ═══ SHOW EXAMPLES OF SELECTIVE DARK MIDDLEs ═══
print("\n" + "=" * 100)
print("MOST SELECTIVE DARK MIDDLEs (1 section only)")
print("These describe properties specific to one operational domain")
print("=" * 100)

single_sec = [(mid, list(mid_sections[mid])[0], sum(1 for t in all_b if morph.extract(t.word).middle == mid))
              for mid in dp_set if len(mid_sections.get(mid, set())) == 1]
single_sec.sort(key=lambda x: -x[2])

print(f"\n  {len(single_sec)} dark MIDDLEs appear in exactly 1 section")
print(f"\n  {'MIDDLE':>10s} {'Section':>8s} {'N':>4s} {'Atoms':>30s}")
print(f"  {'-'*60}")
for mid, sec, n in single_sec[:25]:
    atoms = '.'.join(ATOM_GLOSSES.get(c, '?') for c in mid)
    print(f"  {mid:>10s} {sec:>8s} {n:4d} {atoms:>30s}")

print("\n" + "=" * 100)
print("DONE")
print("=" * 100)
