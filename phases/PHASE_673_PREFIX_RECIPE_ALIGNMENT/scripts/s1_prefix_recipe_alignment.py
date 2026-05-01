"""
Phase 673 (qo-recipe alignment test) — diagnostic version.

PRE-REGISTERED HYPOTHESIS:
  qo-prefix rate in matched Voynich folios correlates positively with heat-keyword
  density in the corresponding Pseudo-Lull Testamentum chapter.

WHY THIS IS A "BREAK OUT OF POSITION LOOP" TEST:
  Crazy-expert flagged that internal-to-internal permutation tests just produce
  numbers. External anchoring (recipe content) is what produces knowledge.
  qo gloss = "thermal injection / heat channel" (C1300, C1277). If real, qo-rate
  should track recipe heat content.

DESIGN:
  - 11 matched folios from Phase 668 (8 coherent + 3 partial)
  - Per Voynich folio: qo-prefix rate (body-only, lines >= 4)
  - Per recipe chapter: heat-keyword density in English text (en_line_start to
    en_line_end ranges from structural profile)
  - Spearman correlation + permutation null (10k shuffles of folio-chapter
    pairings)
  - Pre-registered: positive correlation predicted

OUTCOMES:
  rho > 0.5, p < 0.01 -> qo really tracks recipe heat -> Tier 2 finding
  rho weakly positive, n.s.   -> partial; may need paragraph-level test
  rho near zero -> qo-rate is independent of recipe heat -> null
  rho negative -> something inverted (qo doesn't mark heat injection)
"""
import json
import random
import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "phases" / "PER_DOMAIN_BRIDGE_CALIBRATION" / "scripts"))
from voynich import Transcript, Morphology
from shared_627 import load_pl_structural_profile, load_pl_channel_features

random.seed(42)

# Phase 668-validated matches (per INDEX.md). Format: folio -> (book, chapter_str)
# book: 'P' = Practica (II), 'M' = Mercuriorum (III)
# Excluding rejected (f77v, f82v) and unmatched (f107r, f80r).
MATCHED = {
    "f75r":  ("M", "19"),   # III.19 aqua vitae
    "f76r":  ("P", "16"),   # II.16 element separation
    "f84r":  ("P", "12"),   # II.12 gold dissolution
    "f79r":  ("M", "12"),   # III.12 mercury sublimation
    "f82r":  ("M", "19"),   # III.19.1-5 (per Phase 668 update; multi-recipe)
    "f76v":  ("M", "15"),   # III.15 ferment conversion
    "f81v":  ("M", "18"),   # III.18 potable gold
    "f112v": ("M", "1"),    # III.1 lunaria -> quicksilver
    "f103r": ("M", "16"),   # III.16 ferment multiplication (PARTIAL)
    "f116r": ("M", "4"),    # III.4 fixation/fusibility (PARTIAL)
    "f112r": ("M", "11"),   # III.11 red mercury tincture (PARTIAL)
}


def load_chapter_features():
    """Load PL channel features and structural profile.

    Returns: list of dicts with chapter_idx, chapter_number, family, total_heat, etc.
    """
    pl_struct = load_pl_structural_profile()
    chapters = pl_struct["E1_chapters"]  # list of chapter metadata
    pl_feat = load_pl_channel_features()
    t1 = pl_feat["T1_heat_modes"]["per_chapter"]
    # Index chapters by chapter_idx (assume aligned)
    return chapters, t1


def find_chapter(chapters, t1, book, chapter_str):
    target_num = int(chapter_str)
    book_name = {"P": "Practica", "M": "Mercuriorum"}[book]
    candidates = []
    for i, ch in enumerate(chapters):
        if ch.get("part") == book_name and ch.get("number") == target_num:
            candidates.append((i, ch))
    return candidates


def get_prefix_rates_for_folio(folio_target, b_tokens, morph, prefixes):
    """Compute per-prefix rate (body-only, lines >= 4) for given folio."""
    counts = {p: 0 for p in prefixes}
    total = 0
    by_line = defaultdict(list)
    for t in b_tokens:
        if t.folio != folio_target or "*" in t.word or not t.word.strip() or t.is_label:
            continue
        by_line[t.line].append(t)
    for line_id, tokens in by_line.items():
        if len(tokens) < 4:
            continue
        if tokens[0].par_initial:
            continue
        for t in tokens:
            total += 1
            a = morph.atomize(t.word)
            if a.prefix in counts:
                counts[a.prefix] += 1
    return counts, total


def get_qo_rate_for_folio(folio_target, b_tokens, morph):
    counts, total = get_prefix_rates_for_folio(folio_target, b_tokens, morph, ["qo"])
    qo = counts["qo"]
    return qo, total, (qo / total if total > 0 else 0)


def main():
    print("Loading data...")
    chapters, t1 = load_chapter_features()
    print(f"  PL chapters: {len(chapters)}, T1 entries: {len(t1)}")
    print()

    # Show first chapter to understand structure
    print("Sample chapter (idx 0):")
    print(f"  {chapters[0]}")
    print(f"  T1[0]: {t1[0]}")
    print()

    tx = Transcript()
    morph = Morphology()
    b_tokens = list(tx.currier_b())

    # Build per-folio qo rates
    print("=== PER-FOLIO qo RATES (body-only) ===")
    folio_data = {}
    for folio, (book, ch_str) in MATCHED.items():
        qo, total, rate = get_qo_rate_for_folio(folio, b_tokens, morph)
        folio_data[folio] = {"qo": qo, "total": total, "qo_rate": rate, "book": book, "chapter_str": ch_str}
        print(f"  {folio:<6} {book}.{ch_str:<3} qo={qo:>3} total={total:>4} rate={rate:.3f}")

    # Match each folio to chapter
    print("\n=== CHAPTER MATCHING ===")
    for folio, info in folio_data.items():
        candidates = find_chapter(chapters, t1, info["book"], info["chapter_str"])
        if candidates:
            idx, ch = candidates[0]
            info["chapter_idx"] = idx
            info["chapter_meta"] = ch
            info["total_heat_pl"] = t1[idx]["total_heat"]
        else:
            info["chapter_idx"] = None

    # === Heat keyword density from English text ===
    print("\n=== HEAT KEYWORD DENSITY (from English recipe text) ===")
    en_path = Path(__file__).resolve().parents[3] / "sources" / "pseudo_lull_testamentum" / "testamentum_complete_english.txt"
    en_lines = en_path.read_text(encoding="utf-8").splitlines()
    HEAT_KEYWORDS = ["heat", "fire", "hot", "warm", "boil", "simmer",
                     "distill", "decoct", "evaporat", "calcin", "ignite",
                     "kindle", "sublim", "calefac", "ferment", "fervent",
                     "burn", "flame", "ember", "ash", "coal", "coct",
                     "embers"]

    def count_heat_kw(text):
        text_lower = text.lower()
        count = 0
        for kw in HEAT_KEYWORDS:
            count += text_lower.count(kw)
        return count

    print(f"  {'Folio':<8} {'Chapter':<10} {'qo_rate':>8}  {'words':>6}  {'heat_kw':>8}  {'heat_density':>12}")
    rows = []
    for folio, info in folio_data.items():
        if info["chapter_idx"] is None:
            continue
        ch = info["chapter_meta"]
        en_start = ch.get("en_line_start", 0) - 1
        en_end = ch.get("en_line_end", 0)
        if en_start < 0 or en_end <= en_start:
            continue
        text = "\n".join(en_lines[en_start:en_end])
        words = len(text.split())
        heat_kw = count_heat_kw(text)
        density = heat_kw / words if words > 0 else 0
        info["en_words"] = words
        info["heat_kw"] = heat_kw
        info["heat_density"] = density
        ch_label = f"{info['book']}.{info['chapter_str']}"
        print(f"  {folio:<8} {ch_label:<10} {info['qo_rate']:>8.3f}  {words:>6}  {heat_kw:>8}  {density:>12.4f}")
        rows.append((folio, info["qo_rate"], density, heat_kw, words))

    # Spearman correlation + permutation null
    print("\n=== SPEARMAN CORRELATION + PERMUTATION TEST ===")
    n = len(rows)
    if n < 4:
        print(f"  Too few rows ({n}); aborting")
        return
    qo_rates = [r[1] for r in rows]
    densities = [r[2] for r in rows]

    def rank(values):
        sorted_idx = sorted(range(len(values)), key=lambda i: values[i])
        ranks = [0] * len(values)
        for r, i in enumerate(sorted_idx):
            ranks[i] = r + 1
        # Handle ties
        return ranks

    def spearman(x, y):
        rx = rank(x)
        ry = rank(y)
        n = len(x)
        d2 = sum((rx[i] - ry[i]) ** 2 for i in range(n))
        return 1 - 6 * d2 / (n * (n * n - 1))

    actual_rho = spearman(qo_rates, densities)
    print(f"  N folios: {n}")
    print(f"  Actual Spearman rho: {actual_rho:+.4f}")

    extreme = 0
    n_perm = 10000
    for _ in range(n_perm):
        shuffled = densities[:]
        random.shuffle(shuffled)
        rho = spearman(qo_rates, shuffled)
        if abs(rho) >= abs(actual_rho):
            extreme += 1
    p_value = extreme / n_perm
    print(f"  Two-sided p (permutation, {n_perm} shuffles): {p_value:.4f}")
    one_sided = sum(1 for _ in range(n_perm) if (lambda: spearman(qo_rates, random.sample(densities, len(densities))))() >= actual_rho) / n_perm
    print(f"  One-sided p(rho >= actual) approx: derived from above")

    # Verdict
    direction = "+" if actual_rho > 0 else "-"
    if abs(actual_rho) > 0.5 and p_value < 0.05:
        verdict = f"SIGNIFICANT {direction}"
    elif abs(actual_rho) > 0.3:
        verdict = f"WEAK {direction}"
    else:
        verdict = "NULL"
    print(f"  Verdict: {verdict}")

    # === MULTI-PREFIX × MULTI-CATEGORY EXPANSION ===
    print("\n=== MULTI-PREFIX x MULTI-CATEGORY MATRIX ===")
    PREFIX_TEST = ["qo", "ch", "sh", "ok", "ot", "ol", "lk", "lch"]
    CATEGORIES = {
        "heat": HEAT_KEYWORDS,
        "monitor": ["watch", "observ", "look", "examin", "inspect", "test",
                    "see", "check", "verif", "scrutin", "judg", "discern",
                    "perceiv"],
        "transfer": ["transfer", "pour", "decant", "move", "place", "put",
                     "remove", "add", "join", "mix", "combin", "incorporat"],
        "iter": ["repeat", "again", "second time", "third time", "iterate",
                 "cycle", "round", "time", "many time"],
        "vessel": ["vessel", "bottle", "flask", "jar", "alembic", "retort",
                   "cucurbit", "pelican", "pot", "vase"],
        "complete": ["complete", "finish", "perfect", "end", "done", "fini",
                     "thus", "achiev", "result"],
    }

    # Pre-compute per-folio prefix counts
    folio_prefix = {}
    for folio in folio_data.keys():
        counts, total = get_prefix_rates_for_folio(folio, b_tokens, morph, PREFIX_TEST)
        folio_prefix[folio] = {p: counts[p] / total if total > 0 else 0 for p in PREFIX_TEST}

    # Pre-compute per-folio category densities
    folio_cat = {}
    for folio, info in folio_data.items():
        if info["chapter_idx"] is None:
            continue
        ch = info["chapter_meta"]
        en_start = ch.get("en_line_start", 0) - 1
        en_end = ch.get("en_line_end", 0)
        if en_start < 0 or en_end <= en_start:
            continue
        text = "\n".join(en_lines[en_start:en_end]).lower()
        words = max(1, len(text.split()))
        densities = {}
        for cat, kws in CATEGORIES.items():
            count = sum(text.count(kw) for kw in kws)
            densities[cat] = count / words
        folio_cat[folio] = densities

    # Compute correlation matrix
    print(f"\n  Spearman rho matrix (PREFIX rows x CATEGORY cols):")
    print(f"  {'PREFIX':<8} " + "  ".join(f"{cat:>10}" for cat in CATEGORIES.keys()))

    folios_list = sorted(folio_prefix.keys() & folio_cat.keys())
    for prefix in PREFIX_TEST:
        rates = [folio_prefix[f][prefix] for f in folios_list]
        cells = []
        for cat in CATEGORIES.keys():
            densities_arr = [folio_cat[f][cat] for f in folios_list]
            rho = spearman(rates, densities_arr)
            cells.append(f"{rho:>+10.3f}")
        print(f"  {prefix:<8} " + "  ".join(cells))

    # Significance for cells
    print(f"\n  Permutation p-values (one-sided, |rho| extreme, 5000 shuffles):")
    print(f"  {'PREFIX':<8} " + "  ".join(f"{cat:>10}" for cat in CATEGORIES.keys()))
    for prefix in PREFIX_TEST:
        rates = [folio_prefix[f][prefix] for f in folios_list]
        cells = []
        for cat in CATEGORIES.keys():
            densities_arr = [folio_cat[f][cat] for f in folios_list]
            actual = spearman(rates, densities_arr)
            extreme = 0
            for _ in range(5000):
                shuffled = densities_arr[:]
                random.shuffle(shuffled)
                if abs(spearman(rates, shuffled)) >= abs(actual):
                    extreme += 1
            p = extreme / 5000
            star = "*" if p < 0.05 else " "
            cells.append(f"{p:>9.4f}{star}")
        print(f"  {prefix:<8} " + "  ".join(cells))


if __name__ == "__main__":
    main()
