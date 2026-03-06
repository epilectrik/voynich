"""
Phase 529: Paragraph-Level Hazard Gradient
============================================

Phase 528 (C1463) proved lines have a monotonic hazard gradient:
ZERO at SPECIFICATION -> IMMUNE at THERMAL_WORK -> HIGH at CLOSURE.

This phase tests whether the safety architecture repeats at paragraph scale:
do HEADER lines concentrate safe frames while TAIL lines concentrate
hazardous frames -- creating a fractal safety design at two nested levels?

Tests:
  T1. Paragraph zone x frame hazard contingency (chi-squared + Cramer's V)
  T2. e->y safe pathway by paragraph zone
  T3. k-IMMUNE by paragraph zone
  T4. HIGH hazard by paragraph zone
  T5. Per-line hazard rate across paragraph position (normalized)
  T6. Fractal comparison: paragraph V vs line V (0.085 from C1463)
  T7. Paragraph length interaction (short 2-3 vs long 6+)
  T8. Header-line vs body-line hazard composition

Output: phases/PARAGRAPH_HAZARD_GRADIENT/results/paragraph_hazard_gradient.json
"""

import sys
import io
import json
import math
from pathlib import Path
from collections import Counter, defaultdict

import numpy as np
from scipy.stats import chi2_contingency, spearmanr, mannwhitneyu, fisher_exact

# Force UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology, decompose_middle_hmt

RESULTS_DIR = Path(__file__).resolve().parents[1] / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Gallows characters that mark paragraph boundaries (C827, C864)
GALLOWS = {'k', 't', 'p', 'f'}


# ============================================================
# FRAME HAZARD MAP (from data/decoder_maps.json, C1448)
# ============================================================
def load_frame_hazard_map():
    """Load the frame hazard classification map."""
    path = PROJECT_ROOT / 'data' / 'decoder_maps.json'
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    entries = data['maps']['frame_hazard']['entries']
    return {k: v['value'] for k, v in entries.items()}


def cramers_v(table):
    """Compute Cramer's V from a contingency table (numpy array)."""
    chi2, _, _, _ = chi2_contingency(table)
    n = table.sum()
    min_dim = min(table.shape) - 1
    if min_dim == 0 or n == 0:
        return 0.0
    return math.sqrt(chi2 / (n * min_dim))


# ============================================================
# DATA LOADING: Build paragraphs from raw transcript
# ============================================================

def load_b_tokens_with_paragraphs():
    """Load Currier B tokens with paragraph and line-within-paragraph assignments.

    Paragraphs are detected by gallows-initial lines (C827, C864).
    Each token gets:
        - folio, line_key, word
        - paragraph_id (folio-scoped)
        - line_in_para (0-indexed line within paragraph)
        - para_length (number of lines in this paragraph)
        - para_zone: HEADER (line 0), BODY (lines 1..n-2), TAIL (last line)
        - frame hazard classification from HMT decomposition
        - line-level position quintile (for cross-referencing C1463)
    """
    tx = Transcript()
    morph = Morphology()
    frame_map = load_frame_hazard_map()

    # Step 1: Group tokens by (folio, line) preserving order
    folio_lines = defaultdict(lambda: defaultdict(list))
    line_order_in_folio = defaultdict(list)  # folio -> [line_key in order]
    seen_lines = set()

    for token in tx.currier_b():
        if token.placement.startswith('L'):
            continue
        if '*' in token.word:
            continue
        w = token.word.strip()
        if not w:
            continue

        line_key = (token.folio, token.line)
        folio_lines[token.folio][line_key].append(token)

        if line_key not in seen_lines:
            seen_lines.add(line_key)
            line_order_in_folio[token.folio].append(line_key)

    # Step 2: For each folio, detect paragraph boundaries (gallows-initial)
    # and assign paragraph zones
    all_tokens = []

    for folio in sorted(folio_lines.keys()):
        ordered_lines = line_order_in_folio[folio]

        # Detect paragraph boundaries
        para_boundaries = []  # indices into ordered_lines where new paragraphs start
        for i, lk in enumerate(ordered_lines):
            toks = folio_lines[folio][lk]
            if toks:
                first_word = toks[0].word.strip()
                if first_word and first_word[0] in GALLOWS:
                    para_boundaries.append(i)

        # If no gallows-initial lines, treat entire folio as one paragraph
        if not para_boundaries:
            para_boundaries = [0]
        # Ensure first line is included
        if para_boundaries[0] != 0:
            para_boundaries.insert(0, 0)

        # Build paragraphs
        paragraphs = []
        for pi in range(len(para_boundaries)):
            start = para_boundaries[pi]
            end = para_boundaries[pi + 1] if pi + 1 < len(para_boundaries) else len(ordered_lines)
            para_line_keys = ordered_lines[start:end]
            paragraphs.append(para_line_keys)

        # Step 3: For each paragraph, assign zones and process tokens
        for para_idx, para_line_keys in enumerate(paragraphs):
            para_len = len(para_line_keys)
            para_id = f"{folio}_P{para_idx + 1}"

            for line_idx, lk in enumerate(para_line_keys):
                toks = folio_lines[folio][lk]
                line_len = len(toks)
                if line_len < 2:
                    continue  # Skip degenerate lines

                # Paragraph zone assignment
                if line_idx == 0:
                    para_zone = 'HEADER'
                elif line_idx == para_len - 1:
                    para_zone = 'TAIL'
                else:
                    para_zone = 'BODY'

                # Normalized position within paragraph [0, 1]
                if para_len > 1:
                    para_frac = line_idx / (para_len - 1)
                else:
                    para_frac = 0.5

                for tok_idx, tok in enumerate(toks):
                    # Line-level fractional position
                    frac_pos = tok_idx / (line_len - 1) if line_len > 1 else 0.5
                    quintile = min(int(frac_pos * 5), 4)

                    # Morphological decomposition
                    m = morph.extract(tok.word.strip())
                    if not m.middle:
                        continue

                    # HEAD+MOD*+TERM decomposition
                    head, mods, term, frame_str = decompose_middle_hmt(m.middle)

                    # Frame hazard classification
                    if head == 'k':
                        hazard_class = 'IMMUNE'
                    elif frame_str:
                        hazard_class = frame_map.get(frame_str, 'LOW')
                    else:
                        hazard_class = 'LOW'

                    all_tokens.append({
                        'word': tok.word.strip(),
                        'folio': tok.folio,
                        'section': tok.section,
                        'line_key': f"{tok.folio}_{tok.line}",
                        'para_id': para_id,
                        'para_length': para_len,
                        'line_in_para': line_idx,
                        'para_frac': para_frac,
                        'para_zone': para_zone,
                        'position_in_line': tok_idx,
                        'line_length': line_len,
                        'frac_pos': frac_pos,
                        'quintile': quintile,
                        'middle': m.middle,
                        'prefix': m.prefix,
                        'head': head,
                        'term': term,
                        'frame_str': frame_str,
                        'hazard_class': hazard_class,
                    })

    return all_tokens


# ============================================================
# TEST FUNCTIONS
# ============================================================

def t1_paragraph_zone_hazard_contingency(tokens):
    """T1: Paragraph zone (HEADER/BODY/TAIL) x frame hazard class contingency.

    The core test: does hazard distribute uniformly across paragraph zones
    or follow a gradient similar to C1463's line-level gradient?
    """
    print("\n=== T1: Paragraph Zone x Hazard Contingency ===")

    zones = ['HEADER', 'BODY', 'TAIL']
    hazard_classes = ['HIGH', 'LOW', 'ZERO', 'IMMUNE']

    counts = defaultdict(lambda: defaultdict(int))
    total_by_zone = Counter()
    total_by_h = Counter()

    for t in tokens:
        z = t['para_zone']
        h = t['hazard_class']
        counts[z][h] += 1
        total_by_zone[z] += 1
        total_by_h[h] += 1

    N = len(tokens)

    print(f"\nTotal tokens: {N}")
    print(f"\nZone distribution:")
    for z in zones:
        print(f"  {z}: {total_by_zone[z]} ({total_by_zone[z]/N*100:.1f}%)")

    print(f"\nParagraph Zone x Hazard Class (enrichment vs marginal):")
    print(f"{'Zone':>8s}  {'N':>6s}", end='')
    for h in hazard_classes:
        print(f"  {h:>8s}", end='')
    print()

    enrichments = {}
    for z in zones:
        n_z = total_by_zone[z]
        enrichments[z] = {}
        print(f"{z:>8s}  {n_z:6d}", end='')
        for h in hazard_classes:
            observed = counts[z][h]
            expected_rate = total_by_h[h] / N
            enrichment = (observed / n_z) / expected_rate if n_z > 0 and expected_rate > 0 else 0
            enrichments[z][h] = enrichment
            print(f"  {enrichment:8.3f}", end='')
        print()

    # Chi-squared
    table = np.array([[counts[z][h] for h in hazard_classes] for z in zones])
    col_sums = table.sum(axis=0)
    valid_cols = col_sums > 0
    table_valid = table[:, valid_cols]
    valid_classes = [h for h, v in zip(hazard_classes, valid_cols) if v]

    if table_valid.shape[1] >= 2 and table_valid.shape[0] >= 2:
        chi2, p, dof, _ = chi2_contingency(table_valid)
        V = cramers_v(table_valid)
        print(f"\nChi-squared: {chi2:.1f}, dof={dof}, p={p:.2e}")
        print(f"Cramer's V: {V:.4f}")
    else:
        chi2, p, dof, V = 0, 1, 0, 0

    # Pairwise comparisons
    pairwise = {}
    for za, zb in [('HEADER', 'BODY'), ('BODY', 'TAIL'), ('HEADER', 'TAIL')]:
        pair_table = np.array([[counts[za][h] for h in valid_classes],
                               [counts[zb][h] for h in valid_classes]])
        if pair_table.sum() > 0 and all(pair_table.sum(axis=1) > 0):
            c2, pp, dd, _ = chi2_contingency(pair_table)
            pv = cramers_v(pair_table)
            pairwise[f"{za}_vs_{zb}"] = {'chi2': float(c2), 'p': float(pp), 'V': float(pv)}
            print(f"  {za} vs {zb}: chi2={c2:.1f}, p={pp:.2e}, V={pv:.4f}")

    # Mean hazard class position in paragraph
    print(f"\nMean paragraph-fractional position by hazard class:")
    pos_by_class = defaultdict(list)
    for t in tokens:
        pos_by_class[t['hazard_class']].append(t['para_frac'])

    mean_pos = {}
    for h in hazard_classes:
        if pos_by_class[h]:
            mp = float(np.mean(pos_by_class[h]))
            mean_pos[h] = mp
            print(f"  {h}: mean={mp:.4f}, N={len(pos_by_class[h])}")

    return {
        'test': 'T1_paragraph_zone_hazard_contingency',
        'N': N,
        'zone_counts': dict(total_by_zone),
        'hazard_class_counts': dict(total_by_h),
        'enrichments': enrichments,
        'chi2': float(chi2), 'p': float(p), 'dof': int(dof), 'cramers_v': float(V),
        'pairwise': pairwise,
        'mean_para_position_by_class': mean_pos,
    }


def t2_ey_by_paragraph_zone(tokens):
    """T2: Where does e->y concentrate by paragraph zone?

    C1459 says e->y is preventive (line-initial enriched). Does this extend
    to paragraph-initial (HEADER lines)?
    """
    print("\n=== T2: e->y Safe Pathway by Paragraph Zone ===")

    zones = ['HEADER', 'BODY', 'TAIL']

    ey_tokens = [t for t in tokens if t['frame_str'] == 'e->y']
    N_ey = len(ey_tokens)

    # Baseline zone distribution
    total_by_zone = Counter(t['para_zone'] for t in tokens)
    N = len(tokens)

    # e->y zone distribution
    ey_by_zone = Counter(t['para_zone'] for t in ey_tokens)

    print(f"\ne->y tokens: {N_ey}")
    print(f"\ne->y enrichment by paragraph zone:")

    ey_enrichment = {}
    for z in zones:
        corpus_rate = total_by_zone[z] / N if N > 0 else 0
        ey_rate = ey_by_zone[z] / N_ey if N_ey > 0 else 0
        enrich = ey_rate / corpus_rate if corpus_rate > 0 else 0
        ey_enrichment[z] = float(enrich)
        print(f"  {z}: {enrich:.3f}x ({ey_by_zone[z]}/{N_ey} e->y vs {total_by_zone[z]}/{N} corpus)")

    # e->y mean paragraph position
    ey_para_pos = [t['para_frac'] for t in ey_tokens]
    non_ey_para_pos = [t['para_frac'] for t in tokens if t['frame_str'] != 'e->y']
    print(f"\nMean paragraph position: e->y={np.mean(ey_para_pos):.4f} vs non-e->y={np.mean(non_ey_para_pos):.4f}")

    # Mann-Whitney: e->y vs HIGH by paragraph position
    high_para_pos = [t['para_frac'] for t in tokens if t['hazard_class'] == 'HIGH']
    if ey_para_pos and high_para_pos:
        u, p_mw = mannwhitneyu(ey_para_pos, high_para_pos, alternative='two-sided')
        n1, n2 = len(ey_para_pos), len(high_para_pos)
        rbc = 1 - (2 * u) / (n1 * n2)
        print(f"Mann-Whitney e->y vs HIGH (para position): U={u:.0f}, p={p_mw:.2e}, r={rbc:.4f}")
    else:
        p_mw, rbc = 1.0, 0.0

    return {
        'test': 'T2_ey_by_paragraph_zone',
        'N_ey': N_ey,
        'ey_enrichment_by_zone': ey_enrichment,
        'mean_para_pos_ey': float(np.mean(ey_para_pos)),
        'mean_para_pos_high': float(np.mean(high_para_pos)) if high_para_pos else None,
        'ey_vs_high_para': {'p': float(p_mw), 'rank_biserial': float(rbc)},
    }


def t3_immune_by_paragraph_zone(tokens):
    """T3: Where do k-HEAD (IMMUNE) frames concentrate by paragraph zone?

    At line level, IMMUNE peaks at Q1 (THERMAL_WORK onset, C1464).
    Do they also concentrate in BODY lines at paragraph level?
    """
    print("\n=== T3: k-IMMUNE by Paragraph Zone ===")

    zones = ['HEADER', 'BODY', 'TAIL']

    immune_tokens = [t for t in tokens if t['hazard_class'] == 'IMMUNE']
    N_imm = len(immune_tokens)
    N = len(tokens)

    total_by_zone = Counter(t['para_zone'] for t in tokens)
    imm_by_zone = Counter(t['para_zone'] for t in immune_tokens)

    print(f"\nIMMUNE (k-HEAD) tokens: {N_imm}")

    imm_enrichment = {}
    for z in zones:
        corpus_rate = total_by_zone[z] / N if N > 0 else 0
        imm_rate = imm_by_zone[z] / N_imm if N_imm > 0 else 0
        enrich = imm_rate / corpus_rate if corpus_rate > 0 else 0
        imm_enrichment[z] = float(enrich)
        print(f"  {z}: {enrich:.3f}x ({imm_by_zone[z]}/{N_imm} IMMUNE vs {total_by_zone[z]}/{N} corpus)")

    imm_para_pos = [t['para_frac'] for t in immune_tokens]
    print(f"\nMean paragraph position IMMUNE: {np.mean(imm_para_pos):.4f}")

    return {
        'test': 'T3_immune_by_paragraph_zone',
        'N_immune': N_imm,
        'immune_enrichment_by_zone': imm_enrichment,
        'mean_para_pos_immune': float(np.mean(imm_para_pos)),
    }


def t4_high_by_paragraph_zone(tokens):
    """T4: Do HIGH-hazard frames cluster in TAIL lines?

    At line level, HIGH is CLOSURE-enriched 1.134x (C1463).
    Does the same pattern hold at paragraph TAIL?
    """
    print("\n=== T4: HIGH Hazard by Paragraph Zone ===")

    zones = ['HEADER', 'BODY', 'TAIL']

    high_tokens = [t for t in tokens if t['hazard_class'] == 'HIGH']
    N_high = len(high_tokens)
    N = len(tokens)

    total_by_zone = Counter(t['para_zone'] for t in tokens)
    high_by_zone = Counter(t['para_zone'] for t in high_tokens)

    print(f"\nHIGH-hazard tokens: {N_high}")

    high_enrichment = {}
    for z in zones:
        corpus_rate = total_by_zone[z] / N if N > 0 else 0
        high_rate = high_by_zone[z] / N_high if N_high > 0 else 0
        enrich = high_rate / corpus_rate if corpus_rate > 0 else 0
        high_enrichment[z] = float(enrich)
        print(f"  {z}: {enrich:.3f}x ({high_by_zone[z]}/{N_high} HIGH vs {total_by_zone[z]}/{N} corpus)")

    high_para_pos = [t['para_frac'] for t in high_tokens]
    print(f"\nMean paragraph position HIGH: {np.mean(high_para_pos):.4f}")

    # HIGH rate per zone (absolute)
    print(f"\nHIGH hazard rate per zone:")
    for z in zones:
        rate = high_by_zone[z] / total_by_zone[z] if total_by_zone[z] > 0 else 0
        print(f"  {z}: {rate*100:.1f}% ({high_by_zone[z]}/{total_by_zone[z]})")

    return {
        'test': 'T4_high_by_paragraph_zone',
        'N_high': N_high,
        'high_enrichment_by_zone': high_enrichment,
        'mean_para_pos_high': float(np.mean(high_para_pos)),
        'high_rate_by_zone': {z: float(high_by_zone[z] / total_by_zone[z]) if total_by_zone[z] > 0 else 0.0 for z in zones},
    }


def t5_per_position_hazard_gradient(tokens):
    """T5: Mean hazard rate across normalized paragraph position.

    For paragraphs with 4+ lines, compute HIGH hazard rate per line ordinal.
    Is there a monotonic gradient (Spearman rho)?
    """
    print("\n=== T5: Per-Position Hazard Gradient ===")

    # Only use paragraphs with 4+ lines for meaningful positional analysis
    MIN_PARA_LINES = 4

    # Group tokens by paragraph
    para_tokens = defaultdict(list)
    para_lengths = {}
    for t in tokens:
        pid = t['para_id']
        para_tokens[pid].append(t)
        para_lengths[pid] = t['para_length']

    # Filter to long paragraphs
    long_paras = {pid: toks for pid, toks in para_tokens.items()
                  if para_lengths[pid] >= MIN_PARA_LINES}
    print(f"\nParagraphs with {MIN_PARA_LINES}+ lines: {len(long_paras)}")
    print(f"Total tokens in long paragraphs: {sum(len(v) for v in long_paras.values())}")

    # Compute HIGH rate per normalized position quintile (within paragraph)
    # Use 5 bins: first line, second line, ..., last line -> map to quintile
    para_quintile_counts = defaultdict(lambda: defaultdict(int))  # quintile -> hazard_class -> count
    para_quintile_totals = Counter()

    for pid, toks in long_paras.items():
        pl = para_lengths[pid]
        for t in toks:
            # Normalize line position within paragraph to quintile
            if pl > 1:
                line_frac = t['line_in_para'] / (pl - 1)
            else:
                line_frac = 0.5
            q = min(int(line_frac * 5), 4)
            para_quintile_counts[q][t['hazard_class']] += 1
            para_quintile_totals[q] += 1

    # Print quintile x hazard_class
    hazard_classes = ['HIGH', 'LOW', 'ZERO', 'IMMUNE']
    print(f"\nParagraph quintile x hazard rate (long paragraphs only):")
    print(f"{'PQ':>4s}  {'N':>6s}  {'HIGH%':>8s}  {'LOW%':>8s}  {'ZERO%':>8s}  {'IMMUNE%':>8s}")

    high_rates = []
    for q in range(5):
        n_q = para_quintile_totals[q]
        rates = {}
        row = f"PQ{q}  {n_q:6d}"
        for h in hazard_classes:
            rate = para_quintile_counts[q][h] / n_q * 100 if n_q > 0 else 0
            rates[h] = rate
            row += f"  {rate:8.1f}"
        print(row)
        high_rates.append(rates['HIGH'])

    # Spearman correlation: quintile vs HIGH rate
    if len(high_rates) >= 3:
        rho, p_rho = spearmanr(list(range(5)), high_rates)
        print(f"\nSpearman (para quintile vs HIGH rate): rho={rho:.4f}, p={p_rho:.4f}")
    else:
        rho, p_rho = 0, 1

    # Also compute for all paragraphs (not just long)
    all_first_line_high = sum(1 for t in tokens if t['line_in_para'] == 0 and t['hazard_class'] == 'HIGH')
    all_first_line_total = sum(1 for t in tokens if t['line_in_para'] == 0)
    all_last_line_high = sum(1 for t in tokens if t['line_in_para'] == t['para_length'] - 1 and t['hazard_class'] == 'HIGH')
    all_last_line_total = sum(1 for t in tokens if t['line_in_para'] == t['para_length'] - 1)

    first_rate = all_first_line_high / all_first_line_total if all_first_line_total > 0 else 0
    last_rate = all_last_line_high / all_last_line_total if all_last_line_total > 0 else 0

    print(f"\nAll paragraphs (any length):")
    print(f"  First-line HIGH rate: {first_rate*100:.1f}% ({all_first_line_high}/{all_first_line_total})")
    print(f"  Last-line HIGH rate: {last_rate*100:.1f}% ({all_last_line_high}/{all_last_line_total})")
    print(f"  Ratio (last/first): {last_rate/first_rate:.3f}" if first_rate > 0 else "  (cannot compute ratio)")

    return {
        'test': 'T5_per_position_hazard_gradient',
        'n_long_paras': len(long_paras),
        'high_rate_by_para_quintile': {str(q): high_rates[q] for q in range(5)},
        'spearman_gradient': {'rho': float(rho), 'p': float(p_rho)},
        'all_paras_first_line_high_rate': float(first_rate),
        'all_paras_last_line_high_rate': float(last_rate),
        'first_last_ratio': float(last_rate / first_rate) if first_rate > 0 else None,
    }


def t6_fractal_comparison(tokens):
    """T6: Compare paragraph-level effect size with line-level (C1463 V=0.085).

    Is the paragraph gradient stronger, weaker, or comparable?
    """
    print("\n=== T6: Fractal Comparison (Paragraph vs Line) ===")

    LINE_LEVEL_V = 0.085  # From C1463

    zones = ['HEADER', 'BODY', 'TAIL']
    hazard_classes = ['HIGH', 'LOW', 'ZERO', 'IMMUNE']

    # Paragraph-level V (recompute from T1)
    counts = defaultdict(lambda: defaultdict(int))
    for t in tokens:
        counts[t['para_zone']][t['hazard_class']] += 1

    table = np.array([[counts[z][h] for h in hazard_classes] for z in zones])
    col_sums = table.sum(axis=0)
    valid_cols = col_sums > 0
    table_valid = table[:, valid_cols]

    if table_valid.shape[1] >= 2 and table_valid.shape[0] >= 2:
        chi2_para, p_para, dof_para, _ = chi2_contingency(table_valid)
        V_para = cramers_v(table_valid)
    else:
        chi2_para, p_para, V_para = 0, 1, 0

    # For same-granularity comparison: line-level but only within paragraphs
    # (i.e., line zones WITHIN each paragraph zone)
    # This is just the line-level test from C1463 applied to this dataset
    line_zone_counts = defaultdict(lambda: defaultdict(int))
    for t in tokens:
        q = t['quintile']
        if q == 0:
            lz = 'SPECIFICATION'
        elif q <= 3:
            lz = 'THERMAL_WORK'
        else:
            lz = 'CLOSURE'
        line_zone_counts[lz][t['hazard_class']] += 1

    line_zones = ['SPECIFICATION', 'THERMAL_WORK', 'CLOSURE']
    line_table = np.array([[line_zone_counts[lz][h] for h in hazard_classes] for lz in line_zones])
    col_sums_l = line_table.sum(axis=0)
    valid_l = col_sums_l > 0
    line_table_v = line_table[:, valid_l]

    if line_table_v.shape[1] >= 2:
        chi2_line, p_line, _, _ = chi2_contingency(line_table_v)
        V_line = cramers_v(line_table_v)
    else:
        V_line = 0

    ratio = V_para / LINE_LEVEL_V if LINE_LEVEL_V > 0 else 0

    print(f"\nLine-level V (C1463): {LINE_LEVEL_V:.4f}")
    print(f"Line-level V (this dataset): {V_line:.4f}")
    print(f"Paragraph-level V: {V_para:.4f}")
    print(f"Ratio (para/line): {ratio:.3f}")
    print(f"Paragraph chi2: {chi2_para:.1f}, p={p_para:.2e}")

    if V_para > LINE_LEVEL_V:
        verdict = "PARAGRAPH_STRONGER"
    elif V_para > LINE_LEVEL_V * 0.5:
        verdict = "COMPARABLE"
    elif V_para > 0.02:
        verdict = "PARAGRAPH_WEAKER"
    else:
        verdict = "NO_PARAGRAPH_GRADIENT"

    print(f"Verdict: {verdict}")

    return {
        'test': 'T6_fractal_comparison',
        'line_level_V_C1463': LINE_LEVEL_V,
        'line_level_V_this_dataset': float(V_line),
        'paragraph_level_V': float(V_para),
        'paragraph_chi2': float(chi2_para),
        'paragraph_p': float(p_para),
        'ratio': float(ratio),
        'verdict': verdict,
    }


def t7_paragraph_length_interaction(tokens):
    """T7: Does the paragraph-level gradient hold for short vs long paragraphs?

    Short (2-3 lines) vs long (6+ lines).
    """
    print("\n=== T7: Paragraph Length Interaction ===")

    zones = ['HEADER', 'BODY', 'TAIL']
    hazard_classes = ['HIGH', 'LOW', 'ZERO', 'IMMUNE']

    short = [t for t in tokens if 2 <= t['para_length'] <= 3]
    long_ = [t for t in tokens if t['para_length'] >= 6]
    medium = [t for t in tokens if 4 <= t['para_length'] <= 5]

    print(f"\nShort paragraphs (2-3 lines): {len(short)} tokens")
    print(f"Medium paragraphs (4-5 lines): {len(medium)} tokens")
    print(f"Long paragraphs (6+ lines): {len(long_)} tokens")

    def compute_zone_hazard(toks, label):
        """Compute zone x hazard enrichment for a subset."""
        N = len(toks)
        if N < 50:
            print(f"  {label}: N={N} too small for analysis")
            return None

        counts_z = defaultdict(lambda: defaultdict(int))
        total_z = Counter()
        total_h = Counter()
        for t in toks:
            z = t['para_zone']
            h = t['hazard_class']
            counts_z[z][h] += 1
            total_z[z] += 1
            total_h[h] += 1

        print(f"\n{label} (N={N}) paragraph zone x hazard enrichment:")
        enrichments = {}
        for z in zones:
            n_z = total_z[z]
            enrichments[z] = {}
            if n_z == 0:
                continue
            for h in hazard_classes:
                expected_rate = total_h[h] / N if N > 0 else 0
                observed_rate = counts_z[z][h] / n_z if n_z > 0 else 0
                enrich = observed_rate / expected_rate if expected_rate > 0 else 0
                enrichments[z][h] = float(enrich)
            print(f"  {z}: HIGH={enrichments[z].get('HIGH', 0):.3f}x, ZERO={enrichments[z].get('ZERO', 0):.3f}x, IMMUNE={enrichments[z].get('IMMUNE', 0):.3f}x")

        # Chi-squared
        table = np.array([[counts_z[z].get(h, 0) for h in hazard_classes] for z in zones if total_z[z] > 0])
        used_zones = [z for z in zones if total_z[z] > 0]
        col_sums = table.sum(axis=0)
        valid = col_sums > 0
        table_v = table[:, valid]

        chi2, p, V = 0, 1, 0
        if table_v.shape[0] >= 2 and table_v.shape[1] >= 2:
            chi2, p, _, _ = chi2_contingency(table_v)
            V = cramers_v(table_v)
            print(f"  Chi2={chi2:.1f}, p={p:.2e}, V={V:.4f}")

        return {
            'N': N,
            'enrichments': enrichments,
            'chi2': float(chi2), 'p': float(p), 'cramers_v': float(V),
        }

    short_res = compute_zone_hazard(short, "SHORT (2-3 lines)")
    medium_res = compute_zone_hazard(medium, "MEDIUM (4-5 lines)")
    long_res = compute_zone_hazard(long_, "LONG (6+ lines)")

    return {
        'test': 'T7_paragraph_length_interaction',
        'short': short_res,
        'medium': medium_res,
        'long': long_res,
    }


def t8_header_vs_body_composition(tokens):
    """T8: Header lines vs body lines hazard composition.

    C1426 says HEADER lines are enriched in specification tokens.
    Does this translate to frame-level safety enrichment?
    """
    print("\n=== T8: Header vs Body Hazard Composition ===")

    hazard_classes = ['HIGH', 'LOW', 'ZERO', 'IMMUNE']

    header_tokens = [t for t in tokens if t['para_zone'] == 'HEADER']
    body_tokens = [t for t in tokens if t['para_zone'] == 'BODY']
    tail_tokens = [t for t in tokens if t['para_zone'] == 'TAIL']

    print(f"\nHeader tokens: {len(header_tokens)}")
    print(f"Body tokens: {len(body_tokens)}")
    print(f"Tail tokens: {len(tail_tokens)}")

    # Hazard rate comparison
    def hazard_profile(toks, label):
        N = len(toks)
        profile = Counter(t['hazard_class'] for t in toks)
        print(f"\n{label} hazard profile:")
        result = {}
        for h in hazard_classes:
            rate = profile[h] / N * 100 if N > 0 else 0
            result[h] = float(rate)
            print(f"  {h}: {rate:.1f}% ({profile[h]}/{N})")
        return result

    header_prof = hazard_profile(header_tokens, "HEADER")
    body_prof = hazard_profile(body_tokens, "BODY")
    tail_prof = hazard_profile(tail_tokens, "TAIL")

    # Header vs Body comparison
    header_counts = Counter(t['hazard_class'] for t in header_tokens)
    body_counts = Counter(t['hazard_class'] for t in body_tokens)

    table_hb = np.array([[header_counts.get(h, 0) for h in hazard_classes],
                          [body_counts.get(h, 0) for h in hazard_classes]])
    col_valid = table_hb.sum(axis=0) > 0
    table_hb_v = table_hb[:, col_valid]

    if table_hb_v.shape[1] >= 2:
        chi2_hb, p_hb, _, _ = chi2_contingency(table_hb_v)
        V_hb = cramers_v(table_hb_v)
        print(f"\nHeader vs Body: chi2={chi2_hb:.1f}, p={p_hb:.2e}, V={V_hb:.4f}")
    else:
        chi2_hb, p_hb, V_hb = 0, 1, 0

    # Header vs Tail comparison
    tail_counts = Counter(t['hazard_class'] for t in tail_tokens)
    table_ht = np.array([[header_counts.get(h, 0) for h in hazard_classes],
                          [tail_counts.get(h, 0) for h in hazard_classes]])
    col_valid_ht = table_ht.sum(axis=0) > 0
    table_ht_v = table_ht[:, col_valid_ht]

    if table_ht_v.shape[1] >= 2:
        chi2_ht, p_ht, _, _ = chi2_contingency(table_ht_v)
        V_ht = cramers_v(table_ht_v)
        print(f"Header vs Tail: chi2={chi2_ht:.1f}, p={p_ht:.2e}, V={V_ht:.4f}")
    else:
        chi2_ht, p_ht, V_ht = 0, 1, 0

    # KEY: Does HEADER have LOWER HIGH rate than BODY?
    header_high_rate = header_counts.get('HIGH', 0) / len(header_tokens) if header_tokens else 0
    body_high_rate = body_counts.get('HIGH', 0) / len(body_tokens) if body_tokens else 0
    tail_high_rate = tail_counts.get('HIGH', 0) / len(tail_tokens) if tail_tokens else 0

    print(f"\nHIGH hazard rate: HEADER={header_high_rate*100:.1f}%, BODY={body_high_rate*100:.1f}%, TAIL={tail_high_rate*100:.1f}%")

    # ZERO rate comparison (safe)
    header_zero_rate = header_counts.get('ZERO', 0) / len(header_tokens) if header_tokens else 0
    body_zero_rate = body_counts.get('ZERO', 0) / len(body_tokens) if body_tokens else 0
    tail_zero_rate = tail_counts.get('ZERO', 0) / len(tail_tokens) if tail_tokens else 0

    print(f"ZERO (safe) rate: HEADER={header_zero_rate*100:.1f}%, BODY={body_zero_rate*100:.1f}%, TAIL={tail_zero_rate*100:.1f}%")

    # Does the line-level gradient WITHIN each paragraph zone differ?
    print(f"\nWithin-zone line-level gradients:")
    for zone_name, zone_tokens in [('HEADER', header_tokens), ('BODY', body_tokens), ('TAIL', tail_tokens)]:
        if len(zone_tokens) < 50:
            continue
        # High rate at line Q0 vs Q4 within this paragraph zone
        q0_high = sum(1 for t in zone_tokens if t['quintile'] == 0 and t['hazard_class'] == 'HIGH')
        q0_total = sum(1 for t in zone_tokens if t['quintile'] == 0)
        q4_high = sum(1 for t in zone_tokens if t['quintile'] == 4 and t['hazard_class'] == 'HIGH')
        q4_total = sum(1 for t in zone_tokens if t['quintile'] == 4)
        q0_rate = q0_high / q0_total if q0_total > 0 else 0
        q4_rate = q4_high / q4_total if q4_total > 0 else 0
        print(f"  {zone_name}: line-Q0 HIGH={q0_rate*100:.1f}%, line-Q4 HIGH={q4_rate*100:.1f}%, ratio={q4_rate/q0_rate:.2f}" if q0_rate > 0 else f"  {zone_name}: Q0 HIGH=0%")

    return {
        'test': 'T8_header_vs_body_composition',
        'header_profile': header_prof,
        'body_profile': body_prof,
        'tail_profile': tail_prof,
        'header_vs_body': {'chi2': float(chi2_hb), 'p': float(p_hb), 'V': float(V_hb)},
        'header_vs_tail': {'chi2': float(chi2_ht), 'p': float(p_ht), 'V': float(V_ht)},
        'high_rate_header': float(header_high_rate),
        'high_rate_body': float(body_high_rate),
        'high_rate_tail': float(tail_high_rate),
        'zero_rate_header': float(header_zero_rate),
        'zero_rate_body': float(body_zero_rate),
        'zero_rate_tail': float(tail_zero_rate),
    }


def t_extra_nested_interaction(tokens):
    """Extra: Test the NESTED interaction -- line-level gradient WITHIN each paragraph zone.

    The fractal hypothesis predicts that the line-level hazard gradient (C1463)
    operates WITHIN every paragraph zone. Compute line-zone x hazard V for each
    paragraph zone separately.
    """
    print("\n=== T-Extra: Nested Line-in-Paragraph Interaction ===")

    hazard_classes = ['HIGH', 'LOW', 'ZERO', 'IMMUNE']

    for zone_name in ['HEADER', 'BODY', 'TAIL']:
        zone_tokens = [t for t in tokens if t['para_zone'] == zone_name]
        N = len(zone_tokens)
        if N < 100:
            print(f"\n{zone_name}: N={N} too small")
            continue

        # Compute line-zone x hazard
        line_zones = ['SPECIFICATION', 'THERMAL_WORK', 'CLOSURE']
        counts = defaultdict(lambda: defaultdict(int))
        for t in zone_tokens:
            q = t['quintile']
            if q == 0:
                lz = 'SPECIFICATION'
            elif q <= 3:
                lz = 'THERMAL_WORK'
            else:
                lz = 'CLOSURE'
            counts[lz][t['hazard_class']] += 1

        table = np.array([[counts[lz].get(h, 0) for h in hazard_classes] for lz in line_zones])
        col_valid = table.sum(axis=0) > 0
        table_v = table[:, col_valid]

        if table_v.shape[0] >= 2 and table_v.shape[1] >= 2:
            chi2, p, _, _ = chi2_contingency(table_v)
            V = cramers_v(table_v)
            print(f"\n{zone_name} (N={N}): line-zone x hazard chi2={chi2:.1f}, p={p:.2e}, V={V:.4f}")
        else:
            print(f"\n{zone_name}: degenerate table")


def t_extra_section_interaction(tokens):
    """Extra: Does the paragraph-level gradient differ by section?"""
    print("\n=== T-Extra: Section x Paragraph Zone Interaction ===")

    zones = ['HEADER', 'BODY', 'TAIL']
    hazard_classes = ['HIGH', 'LOW', 'ZERO', 'IMMUNE']

    section_map = defaultdict(list)
    for t in tokens:
        section_map[t['section']].append(t)

    section_results = {}
    for sec, toks in sorted(section_map.items()):
        if len(toks) < 200:
            continue

        counts = defaultdict(lambda: defaultdict(int))
        total_z = Counter()
        total_h = Counter()
        for t in toks:
            counts[t['para_zone']][t['hazard_class']] += 1
            total_z[t['para_zone']] += 1
            total_h[t['hazard_class']] += 1

        N = len(toks)
        high_rates = {}
        for z in zones:
            rate = counts[z].get('HIGH', 0) / total_z[z] if total_z[z] > 0 else 0
            high_rates[z] = float(rate)

        table = np.array([[counts[z].get(h, 0) for h in hazard_classes] for z in zones if total_z[z] > 0])
        col_valid = table.sum(axis=0) > 0
        table_v = table[:, col_valid]

        V = 0.0
        if table_v.shape[0] >= 2 and table_v.shape[1] >= 2:
            chi2, p, _, _ = chi2_contingency(table_v)
            V = cramers_v(table_v)

        print(f"  {sec} (N={N}): HIGH rates: H={high_rates.get('HEADER',0)*100:.1f}%, B={high_rates.get('BODY',0)*100:.1f}%, T={high_rates.get('TAIL',0)*100:.1f}%, V={V:.4f}")
        section_results[sec] = {'high_rates': high_rates, 'cramers_v': float(V), 'N': N}

    return section_results


# ============================================================
# MAIN
# ============================================================

def main():
    print("Phase 529: Paragraph-Level Hazard Gradient")
    print("=" * 60)

    # Load data
    print("\nLoading Currier B tokens with paragraph structure...")
    tokens = load_b_tokens_with_paragraphs()
    print(f"Loaded {len(tokens)} tokens")

    # Summary stats
    para_ids = set(t['para_id'] for t in tokens)
    print(f"Paragraphs detected: {len(para_ids)}")

    # Paragraph length distribution
    para_lengths = {}
    for t in tokens:
        para_lengths[t['para_id']] = t['para_length']
    length_dist = Counter(para_lengths.values())
    print(f"\nParagraph length distribution:")
    for length in sorted(length_dist.keys()):
        print(f"  {length} lines: {length_dist[length]} paragraphs")

    # Zone distribution
    zone_dist = Counter(t['para_zone'] for t in tokens)
    print(f"\nParagraph zone token distribution:")
    for z in ['HEADER', 'BODY', 'TAIL']:
        print(f"  {z}: {zone_dist[z]} ({zone_dist[z]/len(tokens)*100:.1f}%)")

    # Hazard distribution
    hazard_dist = Counter(t['hazard_class'] for t in tokens)
    print(f"\nHazard class distribution:")
    for h, c in hazard_dist.most_common():
        print(f"  {h}: {c} ({c/len(tokens)*100:.1f}%)")

    # Run all tests
    results = {}
    results['t1'] = t1_paragraph_zone_hazard_contingency(tokens)
    results['t2'] = t2_ey_by_paragraph_zone(tokens)
    results['t3'] = t3_immune_by_paragraph_zone(tokens)
    results['t4'] = t4_high_by_paragraph_zone(tokens)
    results['t5'] = t5_per_position_hazard_gradient(tokens)
    results['t6'] = t6_fractal_comparison(tokens)
    results['t7'] = t7_paragraph_length_interaction(tokens)
    results['t8'] = t8_header_vs_body_composition(tokens)

    # Extra tests
    t_extra_nested_interaction(tokens)
    results['t_extra_sections'] = t_extra_section_interaction(tokens)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY OF FINDINGS")
    print("=" * 60)

    # Key finding 1: Is hazard positionally structured at paragraph level?
    v_para = results['t1']['cramers_v']
    p_para = results['t1']['p']
    print(f"\n1. Paragraph Zone x Hazard Contingency: V={v_para:.4f}, p={p_para:.2e}")

    # Key finding 2: Fractal comparison
    v_line = results['t6']['line_level_V_C1463']
    ratio = results['t6']['ratio']
    verdict = results['t6']['verdict']
    print(f"2. Fractal comparison: line V={v_line:.4f}, para V={v_para:.4f}, ratio={ratio:.3f} -> {verdict}")

    # Key finding 3: Header safety
    h_high = results['t8']['high_rate_header']
    b_high = results['t8']['high_rate_body']
    t_high = results['t8']['high_rate_tail']
    print(f"3. HIGH rate: HEADER={h_high*100:.1f}%, BODY={b_high*100:.1f}%, TAIL={t_high*100:.1f}%")

    # Key finding 4: e->y enrichment
    ey_e = results['t2']['ey_enrichment_by_zone']
    print(f"4. e->y enrichment: HEADER={ey_e.get('HEADER',0):.3f}x, BODY={ey_e.get('BODY',0):.3f}x, TAIL={ey_e.get('TAIL',0):.3f}x")

    # Key finding 5: Gradient
    if results['t5']['spearman_gradient']['p'] < 0.05:
        rho = results['t5']['spearman_gradient']['rho']
        print(f"5. Paragraph position gradient: rho={rho:.4f} (SIGNIFICANT)")
    else:
        print(f"5. Paragraph position gradient: NOT significant (p={results['t5']['spearman_gradient']['p']:.4f})")

    # Key finding 6: First-line vs last-line
    first_r = results['t5']['all_paras_first_line_high_rate']
    last_r = results['t5']['all_paras_last_line_high_rate']
    fl_ratio = results['t5']['first_last_ratio']
    print(f"6. First-line HIGH={first_r*100:.1f}%, Last-line HIGH={last_r*100:.1f}%, ratio={fl_ratio:.3f}" if fl_ratio else f"6. Cannot compute first/last ratio")

    # Save results
    output_path = RESULTS_DIR / 'paragraph_hazard_gradient.json'

    def clean(obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        elif isinstance(obj, (np.floating,)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {str(k): clean(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [clean(v) for v in obj]
        return obj

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(clean(results), f, indent=2)

    print(f"\nResults saved to {output_path}")


if __name__ == '__main__':
    main()
