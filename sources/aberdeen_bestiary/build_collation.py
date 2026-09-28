"""Build collation.json for Aberdeen UL MS 24 from cited evidence.

Every quote from the digital edition is pulled verbatim from the cached HTML
(html/*.html) and asserted to exist, so the evidence strings are reproducible.
Quotes from Clark 2006 were read through the Internet Archive full-text search
(snippets of item 'medievalbookofbe0000clar'; the book itself is lending-restricted)
and are recorded with that provenance.

Leaf identifiers: integers are digital-edition folio numbers. The two foliated leaves
that are physically two leaves pasted back to back get string ids:
  "56a" = leaf bearing f56r, "56b" = leaf bearing f56v,
  "93a" = leaf bearing f93r, "93b" = leaf bearing f93v.
"""
import json
import os
import re

from bs4 import BeautifulSoup

HERE = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(HERE, "html")
_cache = {}


def page_text(name, section=None):
    if (name, section) not in _cache:
        with open(os.path.join(HTML, name + ".html"), "rb") as fh:
            soup = BeautifulSoup(fh.read(), "html.parser")
        if section == "commentary":
            node = soup.find("dd", id="commentary")
            txt = node.get_text(" ", strip=True) if node else ""
        else:   # prose pages: inline <a> links must not be padded with spaces
            node = soup.find("main") or soup
            txt = node.get_text("")
        _cache[(name, section)] = re.sub(r"\s+", " ", txt)
    return _cache[(name, section)]


LABELS = ("Commentary Text ", "Comment ", "Text ", "Illustration ")
# a full stop ends a sentence only if followed by a capital, a quote/bracket, a new
# 'f.NN' reference, or the end of the text -- so 'f.56v' / 'ff. 21' never end one
RE_END = re.compile(r"[.?!](?=\s+(?:[A-Z\"'(\[]|f\.\d)|\s*$)")


def sentence(txt, needle):
    i = txt.find(needle)
    assert i >= 0, needle
    start = 0
    for m in RE_END.finditer(txt, 0, i):
        start = m.end()
    for lab in LABELS:
        j = txt.rfind(lab, start, i + 1)
        if j >= 0:
            start = max(start, j + len(lab))
    m = RE_END.search(txt, i + len(needle) - 1)
    end = m.end() if m else len(txt)
    return txt[start:end].strip()


def q(folio, needle):
    """Verbatim sentence from a folio page's Commentary containing `needle`."""
    return "%s commentary: \"%s\"" % (folio, sentence(page_text(folio, "commentary"), needle))


def cq(needle, extra=0):
    """Verbatim sentence from the codicology page (html/_codicology.html)."""
    return "codicology.php: \"%s\"" % sentence(page_text("_codicology"), needle)


JAMES = cq("The quire system was examined by MR James", extra=150)
SEQ = cq("Some are missing with the result that the sequence runs")
FOLD = cq("Although there were eight folios only the first four needed marking")
NUMQ = cq("In the Bestiary there are fifteen quires")
TABLE = ("codicology.php image 'Folio Marks' (images/folio-marks.jpg, saved as ref/folio-marks.jpg): "
         "table of leaf marks for the first to fourth folio of quires B (f.7-f.12v), D (f.19-f.24v), "
         "E (f.25-f.32v), F (f33-f40v), G (f.42-f.48v) [sic], I (f.57-f.64v), L (f.73-f.79v), M (f.80-f.87v); "
         "L has marks only for its second and fourth folio")
CLARK_MARKS = ("Clark 2006, Cat. no. 1 (via IA full-text snippets): \"Assembly marks in a variety of forms in lead point, "
               "most in outer margins, lower corners, ff. 21, 26-28, 33-36, 41-44, 57, 58, 60, 73, 75, 80-83 (forms shown on "
               "the Website). Quire signatures in capital letters are later additions; 2 leaves blank (ff. 3v-4, 6-6v), "
               "2 leaves glued together (ff. 56v-57, 93v-94).\"")
CLARK_LOSSES = ("Clark 2006, Cat. no. 1: \"Missing leaves with illustrations (34 leaves by comparison to Ashmole Bestiary): "
                "Creation scenes for days 2, 5, 6; antelope - elephant (betw. ff. 9v and 10); crocodile - parandrus "
                "(betw. ff. 15v and 16); dog (betw. ff. 18v and 19); bullock - horse (betw. ff. 21v and 22); great fish and "
                "fish 'carpet' (betw. ff. 72 and 73).\"")
CLARK_CODICO = ("Clark 2006, Cat. no. 1: \"Codicology: 302 x 210 (185 x 110/115), 1+103 folios; ... Rebound by Brit. Mus. "
                "1931-32.\"")
STD = ("regular quire of nested bifolia: in a quire of 2n leaves, leaf k is conjugate with leaf 2n+1-k "
       "(James's formula names the wanting positions on that model; the site states that the first four "
       "leaves 'were folded with the last four')")


def pairs(positions):
    """positions: list of leaf ids (or None for wanting) in quire order."""
    n = len(positions)
    out, single = [], []
    for k in range(n // 2):
        a, b = positions[k], positions[n - 1 - k]
        if a is not None and b is not None:
            out.append([a, b])
        elif a is not None:
            single.append(a)
        elif b is not None:
            single.append(b)
    return out, sorted(single, key=lambda x: str(x).zfill(4))


def quire(name, positions, structure, status, evidence, quire_mark=None, leaf_marks=None,
          caveats=None, conjugacy_basis=STD, force_pairs_null=False):
    folios = sorted({int(str(p).rstrip("ab")) for p in positions if p is not None})
    cp, single = pairs(positions)
    return {
        "quire": name,
        "folios": folios,
        "physical_leaves": [p for p in positions if p is not None],
        "positions": {str(i + 1): p for i, p in enumerate(positions)} if not force_pairs_null else None,
        "structure": structure,
        "conjugate_pairs": None if force_pairs_null else cp,
        "singletons_conjugate_lost": None if force_pairs_null else single,
        "status": status,
        "quire_mark": quire_mark,
        "leaf_marks": leaf_marks,
        "conjugacy_basis": None if force_pairs_null else conjugacy_basis,
        "evidence": evidence,
        "caveats": caveats or [],
    }


Q = []
Q.append(quire("A", [1, None, 2, 3, 4, 5, 6, None], "8 wants 2, 8", "determined",
    [JAMES, SEQ, q("f7r", "The start of quire B"),
     q("f1v", "Two illustrations of the Creation sequence are missing"),
     "Clark 2006, Cat. no. 1: \"Missing Text: Creation days 3, 4\"",
     q("f3v", "This page and f.4r were deliberately left blank"),
     CLARK_MARKS],
    quire_mark=None,
    caveats=["No quire mark ('-' in the site's sequence) and no leaf marks recorded; positions follow James.",
             "Consistency check: the centre of the quire (leaf 4v / leaf 5r) falls at f3v/f4r, the two facing blank pages; "
             "leaf 2 (lost) falls between f1v (day 2) and f2r (day 5), where days 3-4 are missing."]))
Q.append(quire("B", [7, 8, 9, None, None, 10, 11, 12], "8 wants 4, 5", "determined",
    [JAMES, q("f7r", "The start of quire B"), q("f8r", "second folio of quire B"), TABLE,
     q("f9v", "are missing between f.9v and f.10r"), CLARK_LOSSES],
    quire_mark="b (f7r)", leaf_marks={"8": "* (second folio)"}))
Q.append(quire("C", [13, 14, 15, None, 16, 17, 18, None], "8 wants 4, 8", "determined",
    [JAMES, q("f13r", "indicating the start of the next quire"), q("f19r", "a quire mark (d) at the bottom"),
     q("f15v", "there are pages missing"), q("f18v", "After this page a leaf is missing"), CLARK_LOSSES],
    quire_mark="c (f13r)", leaf_marks=None,
    caveats=["No leaf marks recorded for C; positions follow James, corroborated by the two text losses "
             "(f15v/f16r = leaf 4; after f18v = leaf 8)."]))
Q.append(quire("D", [19, 20, 21, None, None, 22, 23, 24], "8 wants 4, 5", "determined",
    [JAMES, q("f19r", "a quire mark (d) at the bottom"), q("f21r", "Folio mark of three nested chevrons"), TABLE,
     q("f21v", "After f.21v two leaves are missing"), q("f22r", "After two missing leaves")],
    quire_mark="d (f19r)", leaf_marks={"21": "three nested chevrons (third folio)"}))
Q.append(quire("E", [25, 26, 27, 28, 29, 30, 31, 32], "8", "determined",
    [JAMES, q("f25r", "Gathering mark (e) at the bottom"), q("f26r", "folio mark of two 'match sticks'"),
     q("f27r", "folio mark of three 'match sticks'"), q("f28r", "quire mark of four 'matchsticks'"), TABLE,
     q("f33r", "Gathering mark at centre bottom (f)"), FOLD],
    quire_mark="e (f25r)", leaf_marks={"25": "1 match stick", "26": "2", "27": "3", "28": "4 (site calls it 'quire mark' here)"},
    caveats=["Clark lists assembly marks at ff. 26-28 only (not 25); the site records the first mark on f25r."]))
Q.append(quire("F", [33, 34, 35, 36, 37, 38, 39, 40], "8", "determined",
    [JAMES, q("f33r", "Gathering mark at centre bottom (f)"), q("f34r", "Folio mark of two horizontal"),
     q("f35r", "Folio mark of three horizontal"), q("f36r", "Folio mark of four horizontal"), TABLE,
     q("f41r", "Two quire marks, a 'g' in pencil"), FOLD],
    quire_mark="f (f33r)", leaf_marks={"33": "1 horizontal match stick", "34": "2", "35": "3", "36": "4"}))
Q.append(quire("G", [41, 42, 43, 44, 45, 46, 47, 48], "8", "determined",
    [JAMES, q("f41r", "Two quire marks, a 'g' in pencil"), q("f41r", "Chevron folio mark at top right corner"),
     q("f42r", "Folio mark of two chevrons"), q("f43r", "Folio mark of three superimposed chevrons"),
     q("f44r", "Folio mark of four superimposed chevrons"), TABLE, q("f49r", "There is a quire mark ('h')"),
     cq("On f.48r (quire G)"), FOLD],
    quire_mark="g (f41r)", leaf_marks={"41": "1 chevron", "42": "2", "43": "3", "44": "4"},
    caveats=["The site's folio-mark table labels G 'f.42-f.48v'; this is taken as a typo because the quire mark "
             "and the first-folio chevron are both on f41r and F ends at f40v."]))
Q.append(quire("H", [49, 50, 51, 52, 53, 54, 55, "56a", "56b"], "8 per James; 9 physical leaves (f56 = two leaves pasted together)",
    "undetermined",
    [JAMES, q("f49r", "There is a quire mark ('h')"), q("f57r", "Quire indicator 'I'"),
     cq("In quire H (f.49r-f.56v)"),
     q("f56r", "Thus f. 56r and 56v are actually two sheets stuck back to back"),
     cq("f.56r has a hole in it"), cq("The two pages after the phoenix are blank and glued together"),
     CLARK_MARKS],
    quire_mark="h (f49r)", leaf_marks=None, force_pairs_null=True,
    caveats=["Membership is determined (f49r-f56v, between quire marks h and I), but conjugacy is NOT: James's "
             "'E8-L8' gives H eight leaves, whereas the site and Clark describe f56 as two leaves pasted back to back, "
             "i.e. nine physical leaves. Which leaf is additional (a singleton or pasted-on backing) is not stated by any "
             "source consulted, and no leaf marks are recorded for H.",
             "Clark's page references for the pasted pairs ('56v-57', '93v-94') do not match the site's foliation, "
             "in which f56v and f57r both carry text (f57r also carries the quire mark 'I')."]))
Q.append(quire("I", [57, 58, 59, 60, 61, 62, 63, 64], "8", "determined",
    [JAMES, q("f57r", "Quire indicator 'I'"), q("f57r", "Folio mark 'C' at bottom left"), q("f58r", "Folio mark CC'"),
     q("f59r", "The folio mark (which should be 'CCC') is missing"), q("f60r", "Folio mark 'CCCC'"), TABLE,
     q("f65r", "Quire mark 'K' at bottom centre"), FOLD],
    quire_mark="I (f57r)", leaf_marks={"57": "C", "58": "CC", "59": "(CCC expected, missing)", "60": "CCCC"},
    caveats=[q("f61v", "spliced parchment repair")]))
Q.append(quire("K", [65, 66, 67, 68, 69, 70, 71, 72], "8", "determined",
    [JAMES, q("f65r", "Quire mark 'K' at bottom centre"),
     q("f73r", "This represents folio 2 of quire 'L', but folio 1 is missing"),
     q("f72v", "A page is missing after f.72v")],
    quire_mark="K (f65r)", leaf_marks=None,
    caveats=["No leaf marks recorded for K. Extent follows from the K mark on f65r and L's second leaf being f73; "
             "eight leaves with none wanting is consistent only with reading James's 'E8-L8 (1)' as 'L wants 1' "
             "(see L). Conjugacy rests on James's formula alone (no independent corroboration)."]))
Q.append(quire("L", [None, 73, 74, 75, 76, 77, 78, 79], "8 wants 1", "determined",
    [JAMES, q("f73r", "Folio mark 'll' in top right corner"), q("f73r", "This represents folio 2 of quire 'L', but folio 1 is missing"),
     q("f75r", "In the top right corner is a folio mark 'llll'"), TABLE, q("f72v", "A page is missing after f.72v"),
     q("f80r", "Quire mark bottom of page centre 'M'"), SEQ, CLARK_LOSSES],
    quire_mark=None, leaf_marks={"73": "ll (second folio)", "75": "llll (fourth folio)"},
    caveats=["The L quire mark would have been on the lost first leaf; the site's sequence shows '-(folio missing)' "
             "between K and M."]))
Q.append(quire("M", [80, 81, 82, 83, 84, 85, 86, 87], "8", "determined",
    [JAMES, q("f80r", "Quire mark bottom of page centre 'M'"), q("f81r", "Folio mark * bottom left"),
     q("f82r", "Quire mark 'M' in top right corner"), q("f83r", "Folio mark, * in circle"), TABLE,
     q("f88r", "At the bottom centre is a quire mark 'N'"), FOLD],
    quire_mark="M (f80r; also f82r)", leaf_marks={"80": "+", "81": "*", "82": "*", "83": "* in circle"}))
Q.append(quire("N", [88, 89, 90, 91, 92, "93a", "93b", 94], "8 (f93 = two leaves pasted together, foliated once)", "determined",
    [JAMES, q("f88r", "At the bottom centre is a quire mark 'N'"), q("f93r", "This page is glued to f.93v"),
     q("f93v", "f.93v is glued to f.93r"), cq("f.93r is glued to f.93v"), q("f94v", "This folio marks the end of the high quality"),
     q("f95r", "Bottom right quire mark"), CLARK_MARKS],
    quire_mark="N (f88r)", leaf_marks=None,
    caveats=["Only 7 foliation numbers (f88-f94) but James gives N8: this closes only if the pasted f93 pair counts as two "
             "leaves (positions 6 = f93r-leaf, 7 = f93v-leaf, whose inner blank sides face each other and are pasted). "
             "No leaf marks recorded for N; conjugacy rests on James's formula plus that reconciliation."]))
Q.append(quire("O", [95, 96, 97, 98, 99, 100], "6", "determined",
    [JAMES, q("f95r", "Bottom right quire mark"), q("f96r", "Folio marks \"II II\""), q("f97r", "Folio mark \"III\""),
     q("f95r", "From f.95r - f.100v the margins change"), q("f101r", "Quire 'P' begins here"), NUMQ],
    quire_mark="O (f95r, written '0')", leaf_marks={"96": "II II", "97": "III"}))
Q.append(quire("P", [101, 102, 103, None], "4 wants 4", "determined",
    [JAMES, q("f101r", "Quire 'P' begins here"), NUMQ],
    quire_mark=None, leaf_marks=None,
    caveats=["The loss of P's fourth leaf is stated only by James; the text on f103v ends with a complete sentence, "
             "so no text break corroborates it."]))

# ---- arithmetic checks
seen = []
for qq in Q:
    seen.extend(qq["folios"])
assert sorted(seen) == list(range(1, 104)), "every folio 1..103 must be assigned exactly once"
phys = sum(len(qq["physical_leaves"]) for qq in Q)
assert phys == 105, phys
james_leaves = {"A": 6, "B": 6, "C": 6, "D": 6, "E": 8, "F": 8, "G": 8, "H": 8, "I": 8, "K": 8, "L": 7,
                "M": 8, "N": 8, "O": 6, "P": 3}

out = {
    "manuscript": "Aberdeen, University Library, MS 24 (Aberdeen Bestiary)",
    "foliation": "digital edition https://www.abdn.ac.uk/bestiary/ms24 (f1r-f103v, 206 pages); integers below are its folio numbers",
    "leaf_id_note": "'56a'/'56b' and '93a'/'93b' are the two physical leaves foliated as f56 and f93 "
                    "(a = leaf bearing the recto page, b = leaf bearing the verso page); their inner sides are blank and pasted together.",
    "james_formula_as_quoted_by_site": "A8 (wants folio 2, 8); B8 (4,5); C8 (4,8); D8 (4,5); E8-L8 (1); M8; N8; O6; P4 (4)",
    "reading_of_formula": ("Parenthetical numbers are wanting leaf positions. 'E8-L8 (1)' is read as quires E, F, G, H, I, K, L "
                           "of eight, with L wanting its first leaf: the site's own leaf marks put a first-folio mark on the "
                           "first surviving leaf of E, F, G, I and M, while f73r carries L's second-folio mark with 'folio 1 "
                           "missing'. With that reading, and with the pasted f93 pair counted as two leaves, the formula "
                           "accounts exactly for f1-f103 (A-D 24 leaves = f1-f24; E-K 48 = f25-f72; L 7 = f73-f79; "
                           "M 8 = f80-f87; N 8 leaves = f88-f94; O 6 = f95-f100; P 3 = f101-f103). James's leaves total 104; "
                           "the foliation is 103 because f93 is two leaves foliated once. The pasted f56 pair (also two "
                           "leaves per the site and Clark) is not accounted for by 'H8'; H is therefore left undetermined."),
    "james_leaf_counts": james_leaves,
    "physical_leaf_count_estimate": "105 text-block leaves (103 foliated + the second leaf of each pasted pair), plus 1 flyleaf per Clark ('1+103 folios')",
    "sources": [
        "University of Aberdeen, The Aberdeen Bestiary digital edition: codicology.php ('Gatherings, quire marks, folio marks'; "
        "quotes M. R. James's analysis), per-folio Commentary sections, and the 'Folio Marks' table image; accessed 2026-09-27.",
        "M. R. James, A Catalogue of the Medieval Manuscripts in the University Library, Aberdeen (Cambridge, 1932), "
        "MS 24 - NOT consulted directly (paywalled on Cambridge Core); known here only via the site's quotation.",
        "W. B. Clark, A Medieval Book of Beasts: The Second-Family Bestiary (Woodbridge, 2006), Cat. no. 1 - read via "
        "Internet Archive full-text-search snippets (item medievalbookofbe0000clar); gives no collation formula.",
    ],
    "clark_codicology": CLARK_CODICO,
    "quires": Q,
}
with open(os.path.join(HERE, "collation.json"), "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)
for qq in Q:
    print("%-2s %-9s folios %3d-%-3d pairs=%s single=%s" % (
        qq["quire"], qq["status"], qq["folios"][0], qq["folios"][-1], qq["conjugate_pairs"], qq["singletons_conjugate_lost"]))
print("folio coverage OK: 1..103")
