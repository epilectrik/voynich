"""
P-O9: o-density vs AXM self-transition rate (inverse dwell)

C1384 shows o-initial anticorrelates with AXM self-transition (rho=-0.427).
Replicate and extend this at both folio and paragraph level.

Tests:
1. Per folio: o-atom density vs AXM self-transition rate
2. Spearman correlation across folios
3. Rank ALL atoms by AXM self-transition correlation
4. Within-section stability
5. Paragraph-level robustness check

Pass criterion: rho < -0.30, p < 0.001. o ranked #1 AXM-anti among NEUTRAL atoms.
"""

import sys
import math
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from scripts.voynich import Transcript, Morphology, BFolioDecoder


def normal_cdf(x):
    """Approximate CDF of standard normal distribution."""
    t = 1.0 / (1.0 + 0.2316419 * abs(x))
    d = 0.3989422804014327
    p = d * t * (0.3193815 + t * (-0.3565638 + t * (1.781478 + t * (-1.8212560 + t * 1.3302744))))
    return 1.0 - p if x > 0 else p


def spearman_rho(x, y):
    """Compute Spearman rank correlation and two-tailed p-value."""
    n = len(x)
    if n < 5:
        return 0.0, 1.0

    def rank(vals):
        indexed = sorted(range(n), key=lambda i: vals[i])
        ranks = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j < n - 1 and vals[indexed[j + 1]] == vals[indexed[j]]:
                j += 1
            avg_rank = (i + j) / 2.0 + 1
            for k in range(i, j + 1):
                ranks[indexed[k]] = avg_rank
            i = j + 1
        return ranks

    rx = rank(x)
    ry = rank(y)
    mean_rx = sum(rx) / n
    mean_ry = sum(ry) / n
    num = sum((rx[i] - mean_rx) * (ry[i] - mean_ry) for i in range(n))
    den_x = math.sqrt(sum((rx[i] - mean_rx) ** 2 for i in range(n)))
    den_y = math.sqrt(sum((ry[i] - mean_ry) ** 2 for i in range(n)))
    if den_x == 0 or den_y == 0:
        return 0.0, 1.0
    rho = num / (den_x * den_y)
    t_stat = rho * math.sqrt((n - 2) / (1 - rho ** 2 + 1e-15))
    p = 2 * (1 - normal_cdf(abs(t_stat)))
    return rho, p


def get_atoms_in_middle(middle):
    """Extract individual atom characters from a MIDDLE string."""
    if not middle:
        return set()
    return set(middle)


def main():
    tx = Transcript()
    morph = Morphology()
    decoder = BFolioDecoder()

    # All atoms we care about
    ALL_ATOMS = list('abcdefghiklmnopqrsty')
    NEUTRAL_ATOMS = {'d', 'y', 'o', 'i'}

    # ---------------------------------------------------------------------------
    # Build per-folio data: tokens with line ordering for transition detection
    # ---------------------------------------------------------------------------
    # Structure: folio -> line -> [(position, word, middle, macro_state)]
    folio_line_tokens = defaultdict(lambda: defaultdict(list))

    for token in tx.currier_b():
        w = token.word
        if not w or '*' in w:
            continue
        folio = token.folio
        line = token.line
        m = morph.extract(w)
        mid = m.middle if m.middle else ''
        ms = decoder.analyze_token(w)
        macro = ms.macro_state if ms else None
        folio_line_tokens[folio][line].append((w, mid, macro))

    # Get sections
    folio_sections = {}
    for folio in folio_line_tokens:
        fi = decoder.analyze_folio(folio)
        if fi and fi.section:
            folio_sections[folio] = fi.section

    # ---------------------------------------------------------------------------
    # Test 1 & 2: Per folio compute o-atom density and AXM self-transition rate
    # ---------------------------------------------------------------------------
    print("=" * 70)
    print("P-O9: o-density vs AXM self-transition rate")
    print("=" * 70)

    folio_o_density = {}
    folio_axm_self = {}
    # Also compute per-atom densities for ranking
    folio_atom_density = defaultdict(dict)  # atom -> folio -> density

    for folio, lines in folio_line_tokens.items():
        total_tokens = 0
        o_count = 0
        atom_counts = defaultdict(int)
        axm_first = 0
        axm_both = 0

        for line_id in sorted(lines.keys()):
            toks = lines[line_id]
            total_tokens += len(toks)

            for i, (w, mid, macro) in enumerate(toks):
                atoms = get_atoms_in_middle(mid)
                if 'o' in atoms:
                    o_count += 1
                for a in atoms:
                    if a in ALL_ATOMS:
                        atom_counts[a] += 1

                # AXM self-transition: check if current is AXM and next on same line is also AXM
                if macro == 'AXM' and i < len(toks) - 1:
                    axm_first += 1
                    next_macro = toks[i + 1][2]
                    if next_macro == 'AXM':
                        axm_both += 1

        if total_tokens > 0:
            folio_o_density[folio] = o_count / total_tokens
            for a in ALL_ATOMS:
                folio_atom_density[a][folio] = atom_counts.get(a, 0) / total_tokens

        if axm_first >= 5:  # Minimum threshold for meaningful rate
            folio_axm_self[folio] = axm_both / axm_first

    # Common folios
    common_folios = sorted(set(folio_o_density.keys()) & set(folio_axm_self.keys()))
    print(f"\nFolios with both metrics: {len(common_folios)}")

    if len(common_folios) >= 10:
        x_o = [folio_o_density[f] for f in common_folios]
        y_axm = [folio_axm_self[f] for f in common_folios]
        rho, p = spearman_rho(x_o, y_axm)
        print(f"\nTest 1: o-density vs AXM self-transition")
        print(f"  Spearman rho = {rho:+.4f}, p = {p:.6f}")
        print(f"  Mean o-density: {sum(x_o)/len(x_o):.4f}")
        print(f"  Mean AXM self-transition: {sum(y_axm)/len(y_axm):.4f}")

        # Quintile analysis
        sorted_by_o = sorted(range(len(common_folios)), key=lambda i: x_o[i])
        q_size = len(sorted_by_o) // 5
        if q_size > 0:
            print(f"\n  Quintile analysis (o-density -> AXM self-transition):")
            for qi in range(5):
                start = qi * q_size
                end = start + q_size if qi < 4 else len(sorted_by_o)
                indices = sorted_by_o[start:end]
                mean_o = sum(x_o[i] for i in indices) / len(indices)
                mean_axm = sum(y_axm[i] for i in indices) / len(indices)
                print(f"    Q{qi+1}: o-density={mean_o:.4f}, AXM-self={mean_axm:.4f}")
    else:
        rho, p = 0.0, 1.0
        print("  INSUFFICIENT DATA for correlation")

    # ---------------------------------------------------------------------------
    # Test 3: Rank ALL atoms by AXM self-transition correlation
    # ---------------------------------------------------------------------------
    print(f"\n{'='*70}")
    print("Test 3: All atoms ranked by AXM self-transition correlation")
    print("=" * 70)

    atom_rho_list = []
    for a in ALL_ATOMS:
        if a not in folio_atom_density:
            continue
        cf = sorted(set(folio_atom_density[a].keys()) & set(folio_axm_self.keys()))
        if len(cf) < 10:
            continue
        xa = [folio_atom_density[a][f] for f in cf]
        ya = [folio_axm_self[f] for f in cf]
        r, pv = spearman_rho(xa, ya)
        carryover_class = 'NEUTRAL' if a in NEUTRAL_ATOMS else ('POS' if a in {'c','h','k','m','p','r','s','t'} else 'NEG' if a in {'e','i','n','y'} else 'OTHER')
        atom_rho_list.append((a, r, pv, len(cf), carryover_class))

    atom_rho_list.sort(key=lambda x: x[1])  # Sort ascending (most anti-AXM first)

    print(f"\n{'Atom':<6} {'rho':>8} {'p-value':>10} {'N':>5} {'Class':>10}")
    print("-" * 45)
    for a, r, pv, n, cls in atom_rho_list:
        marker = " <-- O" if a == 'o' else ""
        print(f"  {a:<4}  {r:>+.4f}  {pv:>10.6f}  {n:>4}  {cls:>10}{marker}")

    # Find o's rank among NEUTRAL atoms
    neutral_ranked = [(a, r) for a, r, pv, n, cls in atom_rho_list if cls == 'NEUTRAL']
    o_rank_neutral = None
    for i, (a, r) in enumerate(neutral_ranked):
        if a == 'o':
            o_rank_neutral = i + 1
            break

    print(f"\n  o rank among NEUTRAL atoms {{d,y,o,i}}: #{o_rank_neutral} of {len(neutral_ranked)} (1 = most anti-AXM)")

    # Find o's rank overall
    o_rank_overall = None
    for i, (a, r, pv, n, cls) in enumerate(atom_rho_list):
        if a == 'o':
            o_rank_overall = i + 1
            o_rho = r
            break

    print(f"  o rank overall: #{o_rank_overall} of {len(atom_rho_list)}")

    # ---------------------------------------------------------------------------
    # Test 4: Within-section stability
    # ---------------------------------------------------------------------------
    print(f"\n{'='*70}")
    print("Test 4: Within-section o-AXM correlation")
    print("=" * 70)

    section_folios = defaultdict(list)
    for f in common_folios:
        sec = folio_sections.get(f, 'UNK')
        section_folios[sec].append(f)

    section_results = {}
    for sec in sorted(section_folios.keys()):
        sf = section_folios[sec]
        if len(sf) < 8:
            print(f"  Section {sec}: N={len(sf)} (too few)")
            continue
        xs = [folio_o_density[f] for f in sf]
        ys = [folio_axm_self[f] for f in sf]
        r, pv = spearman_rho(xs, ys)
        section_results[sec] = (r, pv, len(sf))
        print(f"  Section {sec}: rho={r:+.4f}, p={pv:.4f}, N={len(sf)}")

    # ---------------------------------------------------------------------------
    # Test 5: Paragraph-level robustness
    # ---------------------------------------------------------------------------
    print(f"\n{'='*70}")
    print("Test 5: Paragraph-level o-density vs AXM self-transition")
    print("=" * 70)

    # Build paragraphs: gallows-initial starts new paragraph
    GALLOWS = {'t', 'k', 'p', 'f'}
    para_o_density = []
    para_axm_self = []

    for folio, lines in folio_line_tokens.items():
        sorted_lines = sorted(lines.keys())
        current_para_lines = []
        paragraphs = []

        for line_id in sorted_lines:
            toks = lines[line_id]
            if toks:
                first_word = toks[0][0]
                if first_word and first_word[0] in GALLOWS and current_para_lines:
                    paragraphs.append(current_para_lines)
                    current_para_lines = []
            current_para_lines.append((line_id, toks))

        if current_para_lines:
            paragraphs.append(current_para_lines)

        for para_lines in paragraphs:
            if len(para_lines) < 4:
                continue

            # Skip header (first line), use body
            body_lines = para_lines[1:]
            total = 0
            o_count = 0
            axm_first = 0
            axm_both = 0

            for line_id, toks in body_lines:
                total += len(toks)
                for i, (w, mid, macro) in enumerate(toks):
                    if 'o' in get_atoms_in_middle(mid):
                        o_count += 1
                    if macro == 'AXM' and i < len(toks) - 1:
                        axm_first += 1
                        if toks[i + 1][2] == 'AXM':
                            axm_both += 1

            if total >= 10 and axm_first >= 3:
                para_o_density.append(o_count / total)
                para_axm_self.append(axm_both / axm_first)

    print(f"  Paragraphs with sufficient data: {len(para_o_density)}")
    if len(para_o_density) >= 20:
        rho_para, p_para = spearman_rho(para_o_density, para_axm_self)
        print(f"  Spearman rho = {rho_para:+.4f}, p = {p_para:.6f}")
    else:
        rho_para, p_para = 0.0, 1.0
        print("  INSUFFICIENT DATA")

    # ---------------------------------------------------------------------------
    # SUMMARY
    # ---------------------------------------------------------------------------
    print(f"\n{'='*70}")
    print("SUMMARY: P-O9 o-density vs AXM self-transition anticorrelation")
    print("=" * 70)

    t1_pass = rho < -0.30 and p < 0.001
    t3_pass = o_rank_neutral == 1 if o_rank_neutral else False
    t4_pass = sum(1 for s, (r, pv, n) in section_results.items() if r < 0) >= len(section_results) * 0.5 if section_results else False
    t5_pass = rho_para < -0.15 if len(para_o_density) >= 20 else False

    print(f"\n  Test 1 (folio correlation):      rho={rho:+.4f}, p={p:.6f}")
    print(f"    Pass (rho<-0.30, p<0.001)?     {'PASS' if t1_pass else 'FAIL'}")
    print(f"\n  Test 3 (o rank in NEUTRAL):       #{o_rank_neutral} of {len(neutral_ranked)}")
    print(f"    Pass (rank #1)?                 {'PASS' if t3_pass else 'FAIL'}")
    print(f"\n  Test 4 (within-section stability): {sum(1 for s,(r,pv,n) in section_results.items() if r < 0)}/{len(section_results)} sections negative")
    print(f"    Pass (majority negative)?       {'PASS' if t4_pass else 'FAIL'}")
    print(f"\n  Test 5 (paragraph-level):         rho={rho_para:+.4f}" if len(para_o_density) >= 20 else "\n  Test 5: INSUFFICIENT DATA")
    print(f"    Pass (rho<-0.15)?               {'PASS' if t5_pass else 'FAIL'}")

    tests_passed = sum([t1_pass, t3_pass, t4_pass, t5_pass])
    total_tests = 4
    print(f"\n  OVERALL: {tests_passed}/{total_tests} tests passed")
    print(f"  VERDICT: {'PASS' if tests_passed >= 3 else 'FAIL'} (need 3/4)")


if __name__ == '__main__':
    main()
