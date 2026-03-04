"""
P-O11: o-density predicts paragraph mode cycling (pro-cycling)

If o = "vessel", vessel management interrupts the main thermal process,
causing mode alternation. More o = more cycling.

Tests:
1. Per paragraph (>=8 body lines): o-atom density vs suffix-mode cycling rate
2. Spearman correlation
3. All atoms ranked by cycling correlation
4. Within-section stability
5. Separate o-initial from o-terminal density effects

Pass criterion: rho > +0.15, p < 0.01. o ranked top 3 for positive cycling.
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


def main():
    tx = Transcript()
    morph = Morphology()
    decoder = BFolioDecoder()

    ALL_ATOMS = list('abcdefghiklmnopqrsty')
    GALLOWS = {'t', 'k', 'p', 'f'}

    # ---------------------------------------------------------------------------
    # Build per-folio line data with suffix mode
    # ---------------------------------------------------------------------------
    # folio -> line -> [words with middles]
    folio_line_words = defaultdict(lambda: defaultdict(list))

    for token in tx.currier_b():
        w = token.word
        if not w or '*' in w:
            continue
        m = morph.extract(w)
        mid = m.middle if m.middle else ''
        folio_line_words[token.folio][token.line].append((w, mid))

    # Get suffix modes per folio per line
    folio_line_mode = {}  # (folio, line) -> mode
    folio_sections = {}

    for folio in folio_line_words:
        fi = decoder.analyze_folio(folio)
        if fi and fi.section:
            folio_sections[folio] = fi.section

        try:
            line_analyses = decoder.analyze_folio_lines(folio)
            if line_analyses:
                for la in line_analyses:
                    if hasattr(la, 'line_id') and hasattr(la, 'suffix_mode'):
                        folio_line_mode[(folio, la.line_id)] = la.suffix_mode
        except Exception:
            pass

    # ---------------------------------------------------------------------------
    # Build paragraphs: gallows-initial starts new paragraph
    # ---------------------------------------------------------------------------
    paragraphs = []  # list of (folio, section, [(line_id, words_mids)])

    for folio in sorted(folio_line_words.keys()):
        lines = folio_line_words[folio]
        sorted_lines = sorted(lines.keys())
        current_para = []
        sec = folio_sections.get(folio, 'UNK')

        for line_id in sorted_lines:
            toks = lines[line_id]
            if toks:
                first_word = toks[0][0]
                if first_word and first_word[0] in GALLOWS and current_para:
                    paragraphs.append((folio, sec, current_para))
                    current_para = []
            current_para.append((line_id, toks))

        if current_para:
            paragraphs.append((folio, sec, current_para))

    print("=" * 70)
    print("P-O11: o-density predicts paragraph mode cycling")
    print("=" * 70)
    print(f"\nTotal paragraphs: {len(paragraphs)}")

    # ---------------------------------------------------------------------------
    # Per paragraph: compute atom densities and cycling rate
    # ---------------------------------------------------------------------------
    para_data = []  # list of dicts with atom densities + cycling_rate + section

    for folio, sec, para_lines in paragraphs:
        if len(para_lines) < 2:  # Need header + body
            continue

        # Body = skip first line (header)
        body_lines = para_lines[1:]
        if len(body_lines) < 8:
            continue

        # Compute atom densities
        total_tokens = 0
        atom_counts = defaultdict(int)
        o_initial_count = 0
        o_terminal_count = 0
        o_any_count = 0

        for line_id, toks in body_lines:
            total_tokens += len(toks)
            for w, mid in toks:
                if not mid:
                    continue
                atoms = set(mid)
                for a in atoms:
                    if a in ALL_ATOMS:
                        atom_counts[a] += 1
                if mid[0] == 'o':
                    o_initial_count += 1
                if mid[-1] == 'o':
                    o_terminal_count += 1
                if 'o' in mid:
                    o_any_count += 1

        if total_tokens < 20:
            continue

        # Compute cycling rate: mode switches / (n_modes - 1)
        body_modes = []
        for line_id, toks in body_lines:
            mode = folio_line_mode.get((folio, line_id))
            if mode and mode in ('A', 'B'):
                body_modes.append(mode)

        if len(body_modes) < 4:
            continue

        switches = sum(1 for i in range(1, len(body_modes)) if body_modes[i] != body_modes[i - 1])
        cycling_rate = switches / (len(body_modes) - 1)

        entry = {
            'folio': folio,
            'section': sec,
            'total_tokens': total_tokens,
            'cycling_rate': cycling_rate,
            'n_modes': len(body_modes),
            'o_any_density': o_any_count / total_tokens,
            'o_initial_density': o_initial_count / total_tokens,
            'o_terminal_density': o_terminal_count / total_tokens,
        }
        for a in ALL_ATOMS:
            entry[f'atom_{a}'] = atom_counts.get(a, 0) / total_tokens

        para_data.append(entry)

    print(f"Paragraphs with >= 8 body lines and mode data: {len(para_data)}")

    if len(para_data) < 20:
        print("\nINSUFFICIENT DATA for analysis")
        print("\nSUMMARY: P-O11 CANNOT BE EVALUATED")
        return

    # ---------------------------------------------------------------------------
    # Test 1-2: o-density vs cycling rate
    # ---------------------------------------------------------------------------
    print(f"\n{'='*70}")
    print("Test 1-2: o-atom density vs suffix-mode cycling rate")
    print("=" * 70)

    x_o = [d['o_any_density'] for d in para_data]
    y_cyc = [d['cycling_rate'] for d in para_data]
    rho_o, p_o = spearman_rho(x_o, y_cyc)

    print(f"\n  o-any-density vs cycling: rho={rho_o:+.4f}, p={p_o:.6f}, N={len(para_data)}")
    print(f"  Mean o-density: {sum(x_o)/len(x_o):.4f}")
    print(f"  Mean cycling rate: {sum(y_cyc)/len(y_cyc):.4f}")

    # Quartile analysis
    sorted_idx = sorted(range(len(para_data)), key=lambda i: x_o[i])
    q_size = len(sorted_idx) // 4
    if q_size > 0:
        print(f"\n  Quartile analysis (o-density -> cycling rate):")
        for qi in range(4):
            start = qi * q_size
            end = start + q_size if qi < 3 else len(sorted_idx)
            indices = sorted_idx[start:end]
            mean_o = sum(x_o[i] for i in indices) / len(indices)
            mean_cyc = sum(y_cyc[i] for i in indices) / len(indices)
            print(f"    Q{qi+1}: o-density={mean_o:.4f}, cycling={mean_cyc:.4f}")

    # ---------------------------------------------------------------------------
    # Test 3: All atoms ranked by cycling correlation
    # ---------------------------------------------------------------------------
    print(f"\n{'='*70}")
    print("Test 3: All atoms ranked by cycling rate correlation")
    print("=" * 70)

    atom_cycling = []
    for a in ALL_ATOMS:
        xa = [d[f'atom_{a}'] for d in para_data]
        r, pv = spearman_rho(xa, y_cyc)
        atom_cycling.append((a, r, pv))

    atom_cycling.sort(key=lambda x: x[1], reverse=True)  # Most positive first

    print(f"\n{'Atom':<6} {'rho':>8} {'p-value':>10}")
    print("-" * 30)
    for a, r, pv in atom_cycling:
        marker = " <-- O" if a == 'o' else ""
        print(f"  {a:<4}  {r:>+.4f}  {pv:>10.6f}{marker}")

    o_rank = next(i + 1 for i, (a, r, pv) in enumerate(atom_cycling) if a == 'o')
    print(f"\n  o rank for positive cycling correlation: #{o_rank} of {len(atom_cycling)}")

    # ---------------------------------------------------------------------------
    # Test 4: Within-section stability
    # ---------------------------------------------------------------------------
    print(f"\n{'='*70}")
    print("Test 4: Within-section o-cycling correlation")
    print("=" * 70)

    section_groups = defaultdict(list)
    for d in para_data:
        section_groups[d['section']].append(d)

    section_rho = {}
    for sec in sorted(section_groups.keys()):
        sd = section_groups[sec]
        if len(sd) < 10:
            print(f"  Section {sec}: N={len(sd)} (too few)")
            continue
        xs = [d['o_any_density'] for d in sd]
        ys = [d['cycling_rate'] for d in sd]
        r, pv = spearman_rho(xs, ys)
        section_rho[sec] = (r, pv, len(sd))
        print(f"  Section {sec}: rho={r:+.4f}, p={pv:.4f}, N={len(sd)}")

    # ---------------------------------------------------------------------------
    # Test 5: o-initial vs o-terminal effects
    # ---------------------------------------------------------------------------
    print(f"\n{'='*70}")
    print("Test 5: o-initial vs o-terminal density effects on cycling")
    print("=" * 70)

    x_o_init = [d['o_initial_density'] for d in para_data]
    x_o_term = [d['o_terminal_density'] for d in para_data]

    rho_init, p_init = spearman_rho(x_o_init, y_cyc)
    rho_term, p_term = spearman_rho(x_o_term, y_cyc)

    print(f"\n  o-initial density vs cycling: rho={rho_init:+.4f}, p={p_init:.6f}")
    print(f"  o-terminal density vs cycling: rho={rho_term:+.4f}, p={p_term:.6f}")
    print(f"  o-any density vs cycling:      rho={rho_o:+.4f}, p={p_o:.6f}")
    print(f"\n  Stronger effect: {'o-initial' if abs(rho_init) > abs(rho_term) else 'o-terminal'}")

    # ---------------------------------------------------------------------------
    # SUMMARY
    # ---------------------------------------------------------------------------
    print(f"\n{'='*70}")
    print("SUMMARY: P-O11 o-density predicts cycling")
    print("=" * 70)

    t1_pass = rho_o > 0.15 and p_o < 0.01
    t2_pass = o_rank <= 3
    t3_pass = sum(1 for s, (r, pv, n) in section_rho.items() if r > 0) >= len(section_rho) * 0.5 if section_rho else False

    print(f"\n  Test 1-2 (o-cycling correlation):  rho={rho_o:+.4f}, p={p_o:.6f}")
    print(f"    Pass (rho>+0.15, p<0.01)?       {'PASS' if t1_pass else 'FAIL'}")
    print(f"\n  Test 3 (o rank in all atoms):      #{o_rank} of {len(atom_cycling)}")
    print(f"    Pass (top 3)?                    {'PASS' if t2_pass else 'FAIL'}")
    print(f"\n  Test 4 (within-section stability):")
    n_positive = sum(1 for s, (r, pv, n) in section_rho.items() if r > 0)
    print(f"    {n_positive}/{len(section_rho)} sections show positive correlation")
    print(f"    Pass (majority positive)?        {'PASS' if t3_pass else 'FAIL'}")
    print(f"\n  Test 5 (initial vs terminal):")
    print(f"    o-initial: rho={rho_init:+.4f}")
    print(f"    o-terminal: rho={rho_term:+.4f}")

    tests_passed = sum([t1_pass, t2_pass, t3_pass])
    print(f"\n  OVERALL: {tests_passed}/3 core tests passed")
    print(f"  VERDICT: {'PASS' if tests_passed >= 2 else 'FAIL'} (need 2/3)")


if __name__ == '__main__':
    main()
