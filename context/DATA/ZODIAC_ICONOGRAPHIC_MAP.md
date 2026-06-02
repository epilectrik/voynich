# Zodiac Iconographic Map (LOCKED GROUND TRUTH)

**Layer:** DATA (primary-source ground truth). Supersedes any text-inferred season map.
**Source:** transcriber notes in `data/transcriptions/reference/ZL_official.txt` — explicit
iconographic sign identifications + Roman-alphabet **month inscriptions** written on the folios.
**Created:** 2026-06-01, after the inferred season-map was found flawed (see §3).

---

## 1. The map (folio → sign → conventional season)

| folio | sign (from iconography) | month inscription on page | conventional dates | season |
|-------|------------------------|---------------------------|--------------------|--------|
| f70v2 | **Pisces** (two fish) | "Mars" (March) | Feb 20 – Mar 20 | late-winter → spring |
| f70v1 | **Aries (dark)** (ram) | "Abril" (April) | Mar 21 – Apr 20 | spring |
| f71r  | **Aries (light)** | — | Mar 21 – Apr 20 | spring |
| f71v  | **Taurus (light)** (bull) | **"May"** | Apr 21 – May 20 | spring |
| f72r1 | **Taurus (dark)** | — | Apr 21 – May 20 | spring |
| f72r2 | **Gemini** | — | May 21 – Jun 20 | late spring |
| f72r3 | **Cancer** | — | Jun 21 – Jul 22 | summer |
| f72v3 | **Leo** | — | Jul 23 – Aug 22 | summer |
| f72v2 | **Virgo** | — | Aug 23 – Sep 22 | late summer → autumn |
| f72v1 | **Libra** | — | Sep 23 – Oct 22 | autumn |
| f73r  | **Scorpius** | — | Oct 23 – Nov 21 | autumn |
| f73v  | **Sagittarius** | — | Nov 22 – Dec 21 | late autumn → early winter |

**12 folios · 10 distinct signs · ~30 nymphs each.** Aries and Taurus are each **doubled**
(light/dark — two folios per sign).

## 2. The decisive structural facts

- **The zodiac is WINTERLESS.** It runs **Pisces → Sagittarius** (≈late-Feb through Dec).
  **Capricorn and Aquarius — the two mid-winter signs (≈Dec 22 – Feb 18) — are NOT in the manuscript.**
  Whether *lost* (missing folios — the mainstream lean) or *deliberately never encoded* (medieval
  spring-equinox year-start convention) is **not resolved** and bears on whether the gap is meaningful.
- **Coverage is spring-heavy:** ~6 spring folios (Pisces-late + Aries×2 + Taurus×2 + Gemini),
  ~2–3 summer, ~3–4 autumn, **0 winter**. A balanced 4-season analysis is **structurally impossible.**
- **Ordering is given exogenously** by the iconography + month inscriptions — it does NOT need to be
  inferred from the text.

## 3. Why this file exists — the inferred map was flawed (PHASE_744, 2026-06-01)

The project's seasonal analysis (C1681/C1684/C1685/C1686/C1687/C1688, and the atom-level
C1908/C1913) did **NOT** use these iconographic signs. It:
1. Declared the standard (iconographic) map "≥6 misassigned" (C1681) and **inferred** seasons from text categories.
2. **Circularly** chose the goat-folio assignment that *"preserves the seasonal signal"* (C1684: aries perm_p=0.033 selected over capricorn 0.220) — fitting labels to maximize the result (**"label-fit-to-signal"** failure pattern).
3. **Contradicted the iconography**: assigned f71v (Taurus, with **"May" written on it**) and f72r1 (Taurus) to **Winter / Capricorn-Aquarius** (C1688).
4. Forced a **4-season grid with a phantom Winter** onto the winterless zodiac.

The project's own un-fitted full-map estimate (**C1685, perm_p=0.112**) is **null** — i.e., with the
selection bias removed there is no significant seasonal signal. The "SEASONAL_SIGNAL_CONFIRMED"
headline (C1681, perm_p=0.018) was the selection-optimized value.

## 4. Valid use going forward

- Use this map (not the inferred one) for any zodiac-folio season reference.
- A 4-season test is invalid (no winter). The only structurally-supported seasonal test is a
  **monotone-by-month** trend (Pisces=1 … Sagittarius=10, with Aries/Taurus as tied ranks), or the
  iconographic **light/dark folio-pair** contrast — both **pre-registered**, given the prior null (C1685).
- The i/d MOD token-partition (former C1908/C1913) is a real **morphological** fact (≈3–7% co-occurrence
  of the aiin vs -ody families) but is **map-independent** and already covered by C1197/C1204/C1205 —
  it is NOT a seasonal finding.

**Provenance:** sign IDs and month inscriptions quoted from `ZL_official.txt` headers for f70v2, f70v1,
f71r, f71v, f72r1, f72r2, f72r3, f72v1, f72v2, f72v3, f73r, f73v.
