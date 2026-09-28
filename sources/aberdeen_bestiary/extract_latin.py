"""Extract the Latin transcription of each Aberdeen Bestiary page (Aberdeen UL MS 24).

Input : html/f{N}{r|v}.html  (cached by fetch_pages.py)
Output: aberdeen_pages.json, extraction_stats.json, linebreak_decisions.json

latin_raw  = text of <dd id="transcription"> <div class="transcription"> (the site's
             Latin transcription panel), minus its <h2> heading. Editorial marks kept
             verbatim: '\\' line ends, [..] editorial brackets, punctuation. Only
             whitespace is tidied (CRLF -> LF, runs of spaces collapsed, trimmed).
             Pages with no transcription panel (blank leaves, full-page pictures)
             get "" -- the English translation is never used.
latin_norm = reading text: lowercase, a-z and single spaces only, u/v and i/j as given.
  B2  "[x inserted]"  -> x kept (interlinear insertion present in the MS).
  B1  in-word short bracket x[ab]y / x[ab] / [ab]y (1-4 lowercase letters, no siglum)
      -> letters kept, brackets dropped (editor-supplied letters; a few bracketed
         dittographies are thereby kept too -- documented in README).
  B3  every other [...] or (...) -> removed with a hard word boundary (A:/PL: readings,
      emendations, supplied words and rubrics, text supplied for excised areas,
      'deleted'/'expuncted' notes, '[......]', numbers). A hyphen touching a removed
      bracket is removed with it, so the fragment stands alone.
  H   hyphen + optional '\\' / spaces + letter -> joined (word split at line end).
  L1  whitespace + '\\'                     -> word boundary.
  L2  letter + '\\' + letter                -> joined (mid-word line break).
  L3  letter + '\\' + whitespace + letter   -> decided per page style:
        'explicit' pages (>=2 L2 cases; the site's normal convention) -> boundary,
            unless the segmentation model is overwhelmingly for joining
            (score > TH_EXPLICIT; e.g. f94r 'ada\\ mas' -> adamas);
        'space' pages (<=1 L2 case: f41r-f64v, f65r, f70r, where the site writes
            every break as '\\ ') -> segmentation model, join iff score > TH_SPACE;
        a right-hand fragment starting with a capital -> always boundary.
  Then: lowercase, non-letters -> space, collapse spaces.
"""
import collections
import json
import os
import re
import statistics

from bs4 import BeautifulSoup

HERE = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(HERE, "html")
FOLIOS = ["f%d%s" % (n, s) for n in range(1, 104) for s in "rv"]
BLOCK = "\u00a6"      # hard-boundary marker left by removed brackets
TH_SPACE = 1.5        # best held-out accuracy / zero word-count bias (validate_linebreaks.py)
TH_EXPLICIT = 1.5     # same threshold: on explicit pages every 'ab\ cd' scoring > ~0.7 was
                      # found (by inspection of all 37 cases > -1) to be a genuine mid-word
                      # break written against the site's own convention (e.g. 'poste\ rior')


def raw_transcription(folio):
    with open(os.path.join(HTML, folio + ".html"), "rb") as fh:
        soup = BeautifulSoup(fh.read(), "html.parser")
    h1 = soup.find("h1")
    title = h1.get_text(" ", strip=True) if h1 else ""
    dd = soup.find("dd", id="transcription")
    div = dd.find("div", class_="transcription") if dd else None
    if div is None:
        return title, False, ""
    h2 = div.find("h2")
    if h2:
        h2.extract()
    txt = div.get_text()
    txt = txt.replace("\r\n", "\n").replace("\r", "\n")
    lines = [re.sub(r"[ \t\u00a0]+", " ", ln).strip() for ln in txt.split("\n")]
    txt = "\n".join(lines)
    txt = re.sub(r"\n{3,}", "\n\n", txt).strip()
    return title, True, txt


RE_INSERTED = re.compile(r"\[([A-Za-z]{1,6}) inserted\]")
RE_INWORD = re.compile(r"(?:(?<=[A-Za-z])\[([a-z]{1,4})\])|(?:\[([a-z]{1,4})\](?=[A-Za-z]))")
RE_ANYBRACKET = re.compile(r"-?[ \t]*\[[^\]]*\][ \t]*-?|-?[ \t]*\([^)]*\)[ \t]*-?")


def pre_breaks(raw, log=None):
    """Apply bracket rules B2, B1, B3 and break rules H, L1. Leaves L2/L3 cases in place."""
    def lg(key, val):
        if log is not None:
            log[key].append(val)
    t = RE_INSERTED.sub(lambda m: (lg("B2_inserted", m.group(0)), m.group(1))[1], raw)
    t = RE_INWORD.sub(lambda m: (lg("B1_inword", m.group(0)), m.group(1) or m.group(2))[1], t)
    t = RE_ANYBRACKET.sub(lambda m: (lg("B3_removed", m.group(0).strip()), " " + BLOCK + " ")[1], t)
    if "[" in t or "]" in t:
        i = max(t.find("["), t.find("]"))
        lg("unbalanced_bracket", t[max(0, i - 40):i + 40])
        t = t.replace("[", " " + BLOCK + " ").replace("]", " " + BLOCK + " ")
    t = re.sub(r"(?<=[A-Za-z])-[ \t]*\\?[ \t\n]*(?=[A-Za-z])", "", t)   # H
    t = re.sub(r"\s+\\", " ", t)                                        # L1
    return t


def page_style(raw):
    t = RE_ANYBRACKET.sub(" ", raw)
    return "explicit" if len(re.findall(r"[A-Za-z]\\[A-Za-z]", t)) >= 2 else "space"


def certain_tokens(pages, styles):
    """Tokens whose boundaries are certain: explicit pages resolved by the convention;
    on space pages only tokens not touching a line break."""
    wc = collections.Counter()
    for f, raw in pages.items():
        t = pre_breaks(raw)
        if styles[f] == "explicit":
            t = re.sub(r"(?<=[A-Za-z])\\(?=[A-Za-z])", "", t)
            t = t.replace("\\", " ")
            for w in re.findall(r"[A-Za-z]+", t):
                wc[w.lower()] += 1
        else:
            prev_bs = False
            for tok in t.split():
                bad = ("\\" in tok) or prev_bs
                prev_bs = tok.endswith("\\")
                if not bad:
                    for w in re.findall(r"[A-Za-z]+", tok):
                        wc[w.lower()] += 1
    return wc


def resolve_breaks(t, style, seg, folio, decisions, log):
    t = re.sub(r"(?<=[A-Za-z])\\(?=[A-Za-z])", "", t)                   # L2

    def l3(m):
        left, right = m.group(1), m.group(2)
        if right[0].isupper():
            join, s = False, None
        else:
            s = seg.score(left, right)
            join = s > (TH_EXPLICIT if style == "explicit" else TH_SPACE)
        key = "L3_%s_%s" % (style, "join" if join else "split")
        log[key].append(left + "\\ " + right)
        decisions.append({"folio": folio, "style": style, "left": left, "right": right,
                          "score": None if s is None else round(s, 2), "join": join})
        return left + right if join else left + " " + right
    t = re.sub(r"([A-Za-z]+)\\[ \t\n]+([A-Za-z]+)", l3, t)
    return t.replace("\\", " ")


def finalize(t):
    t = t.replace(BLOCK, " ").lower()
    t = re.sub(r"[^a-z]+", " ", t)
    return re.sub(r" +", " ", t).strip()


def main():
    from linebreak_model import Segmenter
    rows = []
    for f in FOLIOS:
        title, has_tr, raw = raw_transcription(f)
        rows.append({"folio": f, "leaf": int(f[1:-1]), "side": f[-1], "title": title,
                     "has_transcription": has_tr, "latin_raw": raw})
    pages = {r["folio"]: r["latin_raw"] for r in rows if r["latin_raw"]}
    styles = {f: page_style(t) for f, t in pages.items()}
    seg = Segmenter(certain_tokens(pages, styles))
    log = collections.defaultdict(list)
    decisions = []
    for r in rows:
        r["linebreak_style"] = styles.get(r["folio"])
        if not r["latin_raw"]:
            r["latin_norm"], r["n_words"] = "", 0
            continue
        t = pre_breaks(r["latin_raw"], log)
        t = resolve_breaks(t, styles[r["folio"]], seg, r["folio"], decisions, log)
        r["latin_norm"] = finalize(t)
        r["n_words"] = len(r["latin_norm"].split())
    order = ["folio", "leaf", "side", "latin_raw", "latin_norm", "n_words",
             "title", "has_transcription", "linebreak_style"]
    rows = [{k: r[k] for k in order} for r in rows]
    with open(os.path.join(HERE, "aberdeen_pages.json"), "w", encoding="utf-8") as fh:
        json.dump(rows, fh, ensure_ascii=False, indent=1)
    with open(os.path.join(HERE, "linebreak_decisions.json"), "w", encoding="utf-8") as fh:
        json.dump(decisions, fh, ensure_ascii=False, indent=0)

    wp = [r["n_words"] for r in rows if r["n_words"] > 0]
    stats = {
        "pages_total": len(rows),
        "pages_with_transcription_block": sum(r["has_transcription"] for r in rows),
        "pages_with_text": len(wp),
        "pages_empty": [r["folio"] for r in rows if r["n_words"] == 0],
        "total_words": sum(wp),
        "words_per_page_min": min(wp),
        "words_per_page_median": statistics.median(wp),
        "words_per_page_max": max(wp),
        "words_per_page_mean": round(statistics.mean(wp), 1),
        "min_page": min((r for r in rows if r["n_words"]), key=lambda r: r["n_words"])["folio"],
        "max_page": max(rows, key=lambda r: r["n_words"])["folio"],
        "space_style_pages": sorted([f for f, s in styles.items() if s == "space"],
                                    key=lambda f: (int(f[1:-1]), f[-1])),
        "thresholds": {"TH_SPACE": TH_SPACE, "TH_EXPLICIT": TH_EXPLICIT},
        "rule_counts": {k: len(v) for k, v in sorted(log.items())},
        "rule_examples": {k: v[:60] for k, v in sorted(log.items())},
    }
    with open(os.path.join(HERE, "extraction_stats.json"), "w", encoding="utf-8") as fh:
        json.dump(stats, fh, ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in stats.items() if k != "rule_examples"}, indent=1))


if __name__ == "__main__":
    main()
