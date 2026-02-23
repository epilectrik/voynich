"""
ATOM_PROFILE_SYNTHESIS: Phase 433
====================================
Builds a comprehensive behavioral profile for every atom by merging
data from C1207-C1216 into a single reference table.

T1: Lane vs Non-Lane Atom Content Separation
   Tests whether QO/CHSH lane tokens carry energy/monitoring atoms
   while non-lane tokens carry iteration/structural atoms.
   Extends C605 (two-lane architecture) with atom-level evidence.
"""
import json
import sys
import math
import random
from collections import defaultdict, Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology, MiddleAnalyzer

RESULTS_DIR = Path("phases/ATOM_PROFILE_SYNTHESIS/results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# STRUCTURAL DATA FROM C1207-C1216
# ============================================================

# C1207: Axis membership
AXIS = {
    'a': 'ITERATION', 'i': 'ITERATION', 'n': 'ITERATION', 'r': 'ITERATION',
    'c': 'MONITORING', 'h': 'MONITORING',
    'k': 'ENERGY', 'l': 'ENERGY',
    'd': 'CLOSURE', 'y': 'CLOSURE',
    'o': 'STRUCTURAL', 'p': 'STRUCTURAL',
    'e': 'STABILITY',
    't': 'FREE',
    'f': 'OTHER', 's': 'OTHER', 'm': 'OTHER', 'q': 'OTHER',
}

# C1208: Carryover class
CARRYOVER = {
    'a': 'POSITIVE', 'c': 'POSITIVE', 'h': 'POSITIVE', 'k': 'POSITIVE',
    'm': 'POSITIVE', 'p': 'POSITIVE', 'r': 'POSITIVE', 's': 'POSITIVE', 't': 'POSITIVE',
    'e': 'NEGATIVE', 'i': 'NEGATIVE', 'n': 'NEGATIVE', 'y': 'NEGATIVE',
    'd': 'NEUTRAL', 'f': 'NEUTRAL', 'l': 'NEUTRAL', 'o': 'NEUTRAL', 'q': 'NEUTRAL',
}

# C1209: Positional class
POSITION = {
    'a': 'INITIAL', 'q': 'INITIAL', 'e': 'INITIAL', 'o': 'INITIAL',
    'c': 'MEDIAL', 'i': 'MEDIAL', 'p': 'MEDIAL', 'd': 'MEDIAL', 'f': 'MEDIAL', 's': 'MEDIAL',
    'n': 'TERMINAL', 'y': 'TERMINAL', 'm': 'TERMINAL', 'r': 'TERMINAL',
    'h': 'TERMINAL', 'l': 'TERMINAL',
    'k': 'FREE', 't': 'FREE',
}

# C1209: Position concentrations (fraction at primary position)
POS_CONC = {
    'a': 0.863, 'q': 0.714, 'e': 0.572, 'o': 0.326,
    'c': 0.408, 'i': 0.444, 'p': 0.381, 'd': 0.540, 'f': 0.507, 's': 0.640,
    'n': 0.998, 'y': 0.971, 'm': 0.975, 'r': 0.886, 'h': 0.902, 'l': 0.768,
    'k': 0.478, 't': 0.524,
}

# C1210: Forbidden as INITIAL (these atoms cannot start a MIDDLE ending in...)
# Format: atom as INITIAL -> forbidden TERMINAL partners
FORBIDDEN_INIT = {
    'a': ['y'],
    'e': ['n'],
    'k': ['n'],
}

# C1210: Top affinities (INITIAL->TERMINAL enrichment from Phase 429)
TOP_AFFINITIES = {
    'k': [('e', 7.94)],
    'i': [('n', 6.78)],
    'a': [('n', 3.18)],
    'd': [('y', 3.18)],
    'c': [('h', 4.98)],
    'e': [('h', 2.50)],
    'o': [('r', 2.24)],
}

# C1212: Cross-token enrichment (TERMINAL->INITIAL of next token)
CROSS_TOKEN_ENRICHED = {
    'h': [('p', 2.61), ('t', 1.58)],
    'r': [('a', 1.99)],
    'y': [('q', 1.91)],
    'i': [('o', 1.73)],
    'e': [('k', 1.51)],
}

CROSS_TOKEN_DEPLETED = {
    'r': [('t', 0.25), ('l', 0.30), ('k', 0.37), ('i', 0.38)],
    'n': [('t', 0.37), ('l', 0.43), ('k', 0.50)],
    'i': [('d', 0.35)],
}

# C1216: Junction enrichment (TERMINAL of embedded atom -> INITIAL of next)
JUNCTION_ENRICHED = {
    'c': [('h', 11.71)],
    'l': [('k', 11.33), ('s', 6.11)],
    'o': [('l', 9.12)],
    'h': [('e', 8.47)],
    'r': [('a', 8.28), ('o', 7.99)],
    'p': [('c', 8.14), ('a', 6.07)],
    's': [('h', 8.12)],
    'q': [('e', 8.41)],
    'k': [('h', 5.86)],
    'a': [('i', 5.67), ('l', 4.65)],
    't': [('h', 5.41)],
}

# Existing Tier 4 German abbreviation interpretations
GERMAN_GLOSS = {
    'k': ('Kochen', 'to boil/cook', 'Heat application, energy input'),
    'e': ('Erkalten', 'to cool down', 'Cooling, stabilization'),
    'h': ('Halten/Hüten', 'to hold/watch over', 'Phase monitoring, verification'),
    'd': ('Dichten', 'to seal/make tight', 'Vessel sealing, closure'),
    't': ('Treiben', 'to drive off', 'Material transfer, volatilization'),
    's': ('Scheiden', 'to separate', 'Separation, fractionation'),
    'g': ('Gar', 'done/fully cooked', 'Completion marker'),
    'm': ('Messen', 'to measure', 'Measurement, precision'),
    'r': ('Rühren', 'to stir', 'Stirring, mixing'),
    'l': ('Letzt/Lassen', 'last/release', 'Output, completion'),
    'p': ('Pause', 'pause/rest', 'Pause, stabilization'),
}

# Atoms without clear German glosses
UNGLOSSED = ['a', 'i', 'n', 'o', 'c', 'q', 'y', 'f']


# ============================================================
# COMPUTE EMPIRICAL PROFILES
# ============================================================

def compute_empirical(tokens):
    """Compute empirical statistics for each atom."""
    atom_stats = defaultdict(lambda: {
        'total_appearances': 0,
        'as_initial': 0,
        'as_medial': 0,
        'as_terminal': 0,
        'in_compounds': 0,
        'in_atomic': 0,
        'sections': Counter(),
        'folios': set(),
    })

    for t in tokens:
        mid = t['middle']
        is_comp = t['is_compound']
        for pos, char in enumerate(mid):
            stats = atom_stats[char]
            stats['total_appearances'] += 1
            if pos == 0:
                stats['as_initial'] += 1
            elif pos == len(mid) - 1:
                stats['as_terminal'] += 1
            else:
                stats['as_medial'] += 1
            if is_comp:
                stats['in_compounds'] += 1
            else:
                stats['in_atomic'] += 1
            stats['sections'][t['section']] += 1
            stats['folios'].add(t['folio'])

    return atom_stats


def main():
    print("ATOM_PROFILE_SYNTHESIS -- Phase 433")
    print("=" * 70)

    # Load data
    tx = Transcript()
    morph = Morphology()
    analyzer = MiddleAnalyzer()
    analyzer.build_inventory('B')

    tokens = []
    for t in tx.currier_b():
        m = morph.extract(t.word)
        if m.middle and m.middle != '_EMPTY_' and len(m.middle) >= 2:
            is_comp = analyzer.is_compound(m.middle)
            tokens.append({
                'word': t.word,
                'middle': m.middle,
                'folio': t.folio,
                'section': t.section,
                'is_compound': is_comp,
            })

    print(f"Loaded {len(tokens)} tokens")

    # Compute empirical
    empirical = compute_empirical(tokens)

    # Build comprehensive profile for each atom
    all_atoms = sorted(set(AXIS.keys()) | set(empirical.keys()))

    profiles = {}
    print(f"\n{'='*70}")
    print("COMPREHENSIVE ATOM PROFILES")
    print("=" * 70)

    for atom in all_atoms:
        stats = empirical.get(atom, {})
        total = stats.get('total_appearances', 0)
        if total < 10:
            continue

        # Section distribution
        sec_counts = stats.get('sections', Counter())
        top_sec = sec_counts.most_common(1)[0] if sec_counts else ('?', 0)
        sec_str = ", ".join(f"{s}:{c}" for s, c in sec_counts.most_common())

        # Compound vs atomic distribution
        in_comp = stats.get('in_compounds', 0)
        in_atom = stats.get('in_atomic', 0)
        comp_rate = in_comp / total if total > 0 else 0

        # Slot instruction model
        pos = POSITION.get(atom, '?')
        if pos == 'INITIAL':
            slot_role = 'INPUT/CONTEXT'
        elif pos == 'MEDIAL':
            slot_role = 'OPERATION'
        elif pos == 'TERMINAL':
            slot_role = 'OUTPUT/OUTCOME'
        elif pos == 'FREE':
            slot_role = 'OPERATOR (any position)'
        else:
            slot_role = '?'

        profile = {
            'atom': atom,
            'total': total,
            'n_folios': len(stats.get('folios', set())),
            'axis': AXIS.get(atom, '?'),
            'position': pos,
            'position_concentration': POS_CONC.get(atom, 0),
            'slot_role': slot_role,
            'carryover': CARRYOVER.get(atom, '?'),
            'compound_rate': round(comp_rate, 3),
            'forbidden_as_initial': FORBIDDEN_INIT.get(atom, []),
            'top_affinities': TOP_AFFINITIES.get(atom, []),
            'cross_token_enriched': CROSS_TOKEN_ENRICHED.get(atom, []),
            'cross_token_depleted': CROSS_TOKEN_DEPLETED.get(atom, []),
            'junction_enriched': JUNCTION_ENRICHED.get(atom, []),
            'section_dist': dict(sec_counts),
        }

        # Add German gloss if exists
        if atom in GERMAN_GLOSS:
            g = GERMAN_GLOSS[atom]
            profile['german_word'] = g[0]
            profile['german_meaning'] = g[1]
            profile['distillation_role'] = g[2]

        profiles[atom] = profile

        # Print profile
        print(f"\n  --- {atom.upper()} ---")
        print(f"  Axis: {AXIS.get(atom, '?'):>12} | Position: {pos:>8} ({POS_CONC.get(atom, 0):.0%}) | Carryover: {CARRYOVER.get(atom, '?')}")
        print(f"  Slot role: {slot_role}")
        print(f"  Frequency: {total} appearances across {len(stats.get('folios', set()))} folios")
        print(f"  Compound rate: {comp_rate:.1%} of appearances are in compound MIDDLEs")
        print(f"  Sections: {sec_str}")
        if atom in FORBIDDEN_INIT:
            print(f"  Forbidden TERMINAL partners: {FORBIDDEN_INIT[atom]}")
        if atom in TOP_AFFINITIES:
            aff = ", ".join(f"{t}({r:.1f}x)" for t, r in TOP_AFFINITIES[atom])
            print(f"  Top INITIAL->TERMINAL affinities: {aff}")
        if atom in CROSS_TOKEN_ENRICHED:
            ct = ", ".join(f"->{t}({r:.1f}x)" for t, r in CROSS_TOKEN_ENRICHED[atom])
            print(f"  Cross-token enriched (as TERMINAL): {ct}")
        if atom in CROSS_TOKEN_DEPLETED:
            ct = ", ".join(f"->{t}({r:.1f}x)" for t, r in CROSS_TOKEN_DEPLETED[atom])
            print(f"  Cross-token depleted (as TERMINAL): {ct}")
        if atom in JUNCTION_ENRICHED:
            jn = ", ".join(f"->{t}({r:.1f}x)" for t, r in JUNCTION_ENRICHED[atom])
            print(f"  Junction enriched (as tile end): {jn}")
        if atom in GERMAN_GLOSS:
            g = GERMAN_GLOSS[atom]
            print(f"  German gloss: {g[0]} = '{g[1]}' -> {g[2]}")
        else:
            print(f"  German gloss: UNASSIGNED")

    # Summary table
    print(f"\n\n{'='*70}")
    print("SYNTHESIS TABLE: All atoms with structural + interpretive data")
    print("=" * 70)
    print(f"  {'Atom':>4}  {'Axis':>12}  {'Pos':>8}  {'Conc':>5}  {'Carry':>8}  "
          f"{'Slot':>18}  {'CompR':>5}  {'German':>15}  {'Role':>25}")
    print(f"  {'----':>4}  {'----':>12}  {'---':>8}  {'----':>5}  {'-----':>8}  "
          f"{'----':>18}  {'-----':>5}  {'------':>15}  {'----':>25}")

    for atom in sorted(profiles.keys()):
        p = profiles[atom]
        german = p.get('german_word', '???')
        role = p.get('distillation_role', '???')
        if len(role) > 25:
            role = role[:22] + '...'
        print(f"  {atom:>4}  {p['axis']:>12}  {p['position']:>8}  "
              f"{p['position_concentration']:>4.0%}  {p['carryover']:>8}  "
              f"{p['slot_role']:>18}  {p['compound_rate']:>4.0%}  "
              f"{german:>15}  {role:>25}")

    # Identify structural constraints on unglossed atoms
    print(f"\n\n{'='*70}")
    print("UNGLOSSED ATOMS: Structural constraints on interpretation")
    print("=" * 70)

    for atom in UNGLOSSED:
        if atom not in profiles:
            continue
        p = profiles[atom]
        print(f"\n  {atom.upper()}: {p['axis']} axis, {p['position']} slot, {p['carryover']} carryover")
        print(f"     Must be: {p['slot_role']}")

        # What structural constraints narrow the interpretation?
        constraints = []
        if p['carryover'] == 'NEGATIVE':
            constraints.append("PUNCTUAL (anti-clusters, fires once then disperses)")
        elif p['carryover'] == 'POSITIVE':
            constraints.append("SUSTAINED (persists across tokens, ongoing state)")
        else:
            constraints.append("NEUTRAL (neither persists nor anti-clusters)")

        if p['position_concentration'] > 0.9:
            constraints.append(f"STRONGLY {p['position']} ({p['position_concentration']:.0%})")
        elif p['position_concentration'] > 0.7:
            constraints.append(f"Preferentially {p['position']} ({p['position_concentration']:.0%})")

        if atom in FORBIDDEN_INIT:
            constraints.append(f"Cannot end in: {FORBIDDEN_INIT[atom]}")

        if atom in TOP_AFFINITIES:
            aff = TOP_AFFINITIES[atom]
            constraints.append(f"Strong affinity: {atom}->{aff[0][0]} ({aff[0][1]}x)")

        if atom in JUNCTION_ENRICHED:
            jn = JUNCTION_ENRICHED[atom]
            constraints.append(f"At junctions routes to: {jn[0][0]} ({jn[0][1]}x)")

        for c in constraints:
            print(f"     - {c}")

        # Propose interpretation based on constraints
        if atom == 'a':
            print(f"     PROPOSED: Iteration INPUT -- begins iteration cycles (86% INITIAL),")
            print(f"       sustained state, forbidden from ending in closure (y).")
            print(f"       German candidate: Anfang (beginning) or An- (on/onto)")
        elif atom == 'i':
            print(f"     PROPOSED: Iteration COUNTER -- the counting operation itself (MEDIAL),")
            print(f"       punctual (fires per count), strongest affinity i->n (count->terminal).")
            print(f"       German candidate: In (in/into) or iterative marker")
        elif atom == 'n':
            print(f"     PROPOSED: Iteration RESULT -- endpoint/count reached (99.8% TERMINAL),")
            print(f"       punctual (once reached, done). Forbidden after non-iteration INITIAL.")
            print(f"       German candidate: Null (zero/end-state) or Nach (after)")
        elif atom == 'o':
            print(f"     PROPOSED: Structural FRAME/VESSEL reference (INITIAL but only 33%),")
            print(f"       neutral carryover, affinity o->r (vessel->stir?).")
            print(f"       German candidate: Ofen (oven/furnace) or Ort (place)")
        elif atom == 'c':
            print(f"     PROPOSED: Monitoring OPERATION -- the act of checking (MEDIAL),")
            print(f"       sustained, routes EXCLUSIVELY to h at junctions (c->h 11.7x).")
            print(f"       German candidate: part of ch compound, not independent")
        elif atom == 'q':
            print(f"     PROPOSED: Heat-source REFERENCE (INITIAL 71%), neutral,")
            print(f"       part of qo=Coquo PREFIX. As standalone: references heat source.")
            print(f"       German candidate: part of qo compound")
        elif atom == 'y':
            print(f"     PROPOSED: Closure OUTCOME/SEAL (97% TERMINAL), punctual.")
            print(f"       The sealing/ending event. Forbidden after iteration-start (a).")
            print(f"       German candidate: part of -y suffix family (bare close)")
        elif atom == 'f':
            print(f"     PROPOSED: Uncertain. MEDIAL, neutral, OTHER axis. Rare.")
            print(f"       Possibly: Füllen (to fill) or Filter (filter)?")

    # ==========================================================
    # T1: Lane vs Non-Lane Atom Content Separation
    # ==========================================================
    print(f"\n\n{'='*70}")
    print("T1: LANE vs NON-LANE ATOM CONTENT SEPARATION")
    print("=" * 70)

    # Reload all B tokens (including single-char MIDDLEs)
    all_b_tokens = []
    for t in tx.currier_b():
        m = morph.extract(t.word)
        mid = m.middle
        if not mid or mid == '_EMPTY_':
            continue
        all_b_tokens.append({
            'word': t.word,
            'prefix': m.prefix or '',
            'middle': mid,
            'folio': t.folio,
        })

    print(f"Total B tokens with MIDDLE: {len(all_b_tokens)}")

    QO_PREFIXES = {'qo'}
    CHSH_PREFIXES = {'ch', 'sh'}
    LANE_PREFIXES = QO_PREFIXES | CHSH_PREFIXES
    VESSEL_PREFIXES = {'ok', 'ot'}
    INFRA_PREFIXES = {'da', 'sa'}

    # Count atoms by lane class
    lane_atoms = Counter()
    nonlane_atoms = Counter()
    qo_atoms = Counter()
    chsh_atoms = Counter()
    vessel_atoms = Counter()
    infra_atoms = Counter()
    bare_atoms = Counter()

    lane_n = 0
    nonlane_n = 0
    qo_n = 0
    chsh_n = 0
    vessel_n = 0
    infra_n = 0
    bare_n = 0

    for tok in all_b_tokens:
        pre = tok['prefix']
        mid = tok['middle']
        for ch in mid:
            if pre in QO_PREFIXES:
                qo_atoms[ch] += 1
                lane_atoms[ch] += 1
            elif pre in CHSH_PREFIXES:
                chsh_atoms[ch] += 1
                lane_atoms[ch] += 1
            elif pre in VESSEL_PREFIXES:
                vessel_atoms[ch] += 1
                nonlane_atoms[ch] += 1
            elif pre in INFRA_PREFIXES:
                infra_atoms[ch] += 1
                nonlane_atoms[ch] += 1
            elif pre == '':
                bare_atoms[ch] += 1
                nonlane_atoms[ch] += 1
            else:
                nonlane_atoms[ch] += 1

        if pre in QO_PREFIXES:
            qo_n += 1
            lane_n += 1
        elif pre in CHSH_PREFIXES:
            chsh_n += 1
            lane_n += 1
        elif pre in VESSEL_PREFIXES:
            vessel_n += 1
            nonlane_n += 1
        elif pre in INFRA_PREFIXES:
            infra_n += 1
            nonlane_n += 1
        elif pre == '':
            bare_n += 1
            nonlane_n += 1
        else:
            nonlane_n += 1

    lane_total = sum(lane_atoms.values())
    nonlane_total = sum(nonlane_atoms.values())
    qo_total = sum(qo_atoms.values())
    chsh_total = sum(chsh_atoms.values())

    print(f"LANE tokens (QO + CHSH): {lane_n} (QO={qo_n}, CHSH={chsh_n})")
    print(f"NON-LANE tokens: {nonlane_n} (VESSEL={vessel_n}, INFRA={infra_n}, BARE={bare_n})")
    print(f"MIDDLE chars: LANE={lane_total}, NON-LANE={nonlane_total}")

    all_test_atoms = sorted(set(lane_atoms.keys()) | set(nonlane_atoms.keys()))

    # Per-atom enrichment
    print(f"\n{'Atom':>4}  {'LANE':>6}  {'LANE%':>6}  {'NON-L':>6}  {'NON-L%':>6}  {'Ratio':>6}  {'Axis':>8}")
    print(f"{'----':>4}  {'----':>6}  {'-----':>6}  {'-----':>6}  {'------':>6}  {'-----':>6}  {'----':>8}")

    atom_results = {}
    for atom in all_test_atoms:
        lc = lane_atoms.get(atom, 0)
        nc = nonlane_atoms.get(atom, 0)
        lf = lc / lane_total if lane_total > 0 else 0
        nf = nc / nonlane_total if nonlane_total > 0 else 0
        ratio = lf / nf if nf > 0 else float('inf')
        axis = AXIS.get(atom, '?')
        marker = ''
        if ratio > 1.5:
            marker = '<-- LANE'
        elif ratio < 0.67:
            marker = '<-- NON-LANE'
        print(f"   {atom}  {lc:>6}  {lf:>5.1%}  {nc:>6}  {nf:>5.1%}  {ratio:>5.2f}  {axis:>8}  {marker}")
        atom_results[atom] = {
            'lane_count': lc, 'nonlane_count': nc,
            'lane_frac': round(lf, 4), 'nonlane_frac': round(nf, 4),
            'ratio': round(ratio, 2), 'axis': axis,
        }

    # Axis-level aggregation
    print(f"\nAXIS-LEVEL AGGREGATION:")
    axis_names = ['ENERGY', 'STABILITY', 'MONITORING', 'ITERATION', 'CLOSURE', 'STRUCTURAL', 'FREE', 'OTHER']
    axis_results = {}
    for axis in axis_names:
        axis_atoms_list = [a for a in all_test_atoms if AXIS.get(a) == axis]
        lc = sum(lane_atoms.get(a, 0) for a in axis_atoms_list)
        nc = sum(nonlane_atoms.get(a, 0) for a in axis_atoms_list)
        lf = lc / lane_total if lane_total > 0 else 0
        nf = nc / nonlane_total if nonlane_total > 0 else 0
        ratio = lf / nf if nf > 0 else float('inf')
        atoms_str = ','.join(axis_atoms_list)
        marker = ''
        if ratio > 1.3:
            marker = '<-- LANE'
        elif ratio < 0.77:
            marker = '<-- NON-LANE'
        print(f"  {axis:>12} ({atoms_str:>8}):  LANE={lf:>5.1%}  NON-LANE={nf:>5.1%}  ratio={ratio:.2f}  {marker}")
        axis_results[axis] = {
            'atoms': axis_atoms_list,
            'lane_frac': round(lf, 4), 'nonlane_frac': round(nf, 4),
            'ratio': round(ratio, 2),
        }

    # QO vs CHSH internal split
    print(f"\nQO vs CHSH INTERNAL SPLIT:")
    print(f"  QO: {qo_n} tokens, {qo_total} MIDDLE chars")
    print(f"  CHSH: {chsh_n} tokens, {chsh_total} MIDDLE chars")
    qo_vs_chsh = {}
    for atom in all_test_atoms:
        qc = qo_atoms.get(atom, 0)
        cc = chsh_atoms.get(atom, 0)
        qf = qc / qo_total if qo_total > 0 else 0
        cf = cc / chsh_total if chsh_total > 0 else 0
        qo_vs_chsh[atom] = {'qo_frac': round(qf, 4), 'chsh_frac': round(cf, 4)}

    # Print key atoms
    for atom in ['k', 'e', 't', 'd', 'y', 'h', 'c']:
        r = qo_vs_chsh[atom]
        print(f"  {atom}: QO={r['qo_frac']:.1%}  CHSH={r['chsh_frac']:.1%}  ({AXIS.get(atom, '?')})")

    # Shuffle permutation test: is lane/nonlane separation stronger than chance?
    # Shuffle PREFIX assignments across tokens within each folio, measure
    # how often the observed separation is exceeded
    print(f"\nSHUFFLE PERMUTATION TEST (500 iterations):")
    random.seed(42)

    # Group tokens by folio
    folio_tokens = defaultdict(list)
    for tok in all_b_tokens:
        folio_tokens[tok['folio']].append(tok)

    # Observed: ITERATION fraction difference (nonlane - lane)
    iter_atoms = {'a', 'i', 'n', 'r'}
    obs_lane_iter = sum(lane_atoms.get(a, 0) for a in iter_atoms) / lane_total
    obs_nonlane_iter = sum(nonlane_atoms.get(a, 0) for a in iter_atoms) / nonlane_total
    obs_delta = obs_nonlane_iter - obs_lane_iter

    # Also track k enrichment ratio
    obs_k_lane = lane_atoms.get('k', 0) / lane_total
    obs_k_nonlane = nonlane_atoms.get('k', 0) / nonlane_total
    obs_k_ratio = obs_k_lane / obs_k_nonlane if obs_k_nonlane > 0 else float('inf')

    n_shuffles = 500
    exceed_delta = 0
    exceed_k = 0

    for _ in range(n_shuffles):
        shuf_lane = Counter()
        shuf_nonlane = Counter()
        shuf_lane_total = 0
        shuf_nonlane_total = 0

        for folio, ftoks in folio_tokens.items():
            # Shuffle prefixes within folio
            prefixes = [t['prefix'] for t in ftoks]
            random.shuffle(prefixes)
            for i, tok in enumerate(ftoks):
                pre = prefixes[i]
                mid = tok['middle']
                is_lane = pre in LANE_PREFIXES
                for ch in mid:
                    if is_lane:
                        shuf_lane[ch] += 1
                    else:
                        shuf_nonlane[ch] += 1
                if is_lane:
                    shuf_lane_total += len(mid)
                else:
                    shuf_nonlane_total += len(mid)

        shuf_lane_iter = sum(shuf_lane.get(a, 0) for a in iter_atoms) / shuf_lane_total if shuf_lane_total > 0 else 0
        shuf_nonlane_iter = sum(shuf_nonlane.get(a, 0) for a in iter_atoms) / shuf_nonlane_total if shuf_nonlane_total > 0 else 0
        shuf_delta = shuf_nonlane_iter - shuf_lane_iter
        if shuf_delta >= obs_delta:
            exceed_delta += 1

        shuf_k_lane = shuf_lane.get('k', 0) / shuf_lane_total if shuf_lane_total > 0 else 0
        shuf_k_nonlane = shuf_nonlane.get('k', 0) / shuf_nonlane_total if shuf_nonlane_total > 0 else 0
        shuf_k_ratio = shuf_k_lane / shuf_k_nonlane if shuf_k_nonlane > 0 else float('inf')
        if shuf_k_ratio >= obs_k_ratio:
            exceed_k += 1

    p_delta = exceed_delta / n_shuffles
    p_k = exceed_k / n_shuffles
    # Estimate z from permutation
    z_delta = abs(obs_delta) / (obs_delta * 0.01 + 1e-10) if p_delta == 0 else -1  # placeholder
    print(f"  ITERATION axis delta (nonlane - lane): {obs_delta:.3f}")
    print(f"    Exceeded in {exceed_delta}/{n_shuffles} shuffles (p={p_delta:.4f})")
    print(f"  k enrichment ratio (lane/nonlane): {obs_k_ratio:.2f}")
    print(f"    Exceeded in {exceed_k}/{n_shuffles} shuffles (p={p_k:.4f})")

    # Save all results
    t1_results = {
        'lane_n': lane_n, 'nonlane_n': nonlane_n,
        'qo_n': qo_n, 'chsh_n': chsh_n,
        'vessel_n': vessel_n, 'infra_n': infra_n, 'bare_n': bare_n,
        'lane_total_chars': lane_total, 'nonlane_total_chars': nonlane_total,
        'per_atom': atom_results,
        'per_axis': axis_results,
        'qo_vs_chsh': qo_vs_chsh,
        'shuffle_test': {
            'n_shuffles': n_shuffles,
            'iteration_delta': round(obs_delta, 4),
            'iteration_p': p_delta,
            'k_ratio': round(obs_k_ratio, 2),
            'k_p': p_k,
        },
    }

    # Save
    output = {
        'profiles': profiles,
        'T1_lane_atom_separation': t1_results,
    }
    output_path = RESULTS_DIR / "atom_profiles.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\n{'='*70}")
    print(f"Results saved to {output_path}")
    print(f"{'='*70}")


if __name__ == '__main__':
    main()
