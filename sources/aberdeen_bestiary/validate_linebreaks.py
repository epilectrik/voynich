"""Validate linebreak_model on explicit-convention pages (truth known from the site's convention).

Pages whose transcription writes mid-word breaks as 'ab\\cd' (>=2 such cases) are
'explicit' pages: there 'ab\\cd' = one word and 'ab\\ cd' = two words (by convention).
Train on even-numbered leaves, test on odd-numbered leaves and vice versa; report the
accuracy of the join/split decision for several decision thresholds.
Output: linebreak_validation.json
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import extract_latin as E  # noqa: E402
from linebreak_model import Segmenter  # noqa: E402

rows = json.load(open(os.path.join(HERE, "aberdeen_pages.json"), encoding="utf-8"))
pages = {r["folio"]: r["latin_raw"] for r in rows if r["latin_raw"]}
style = {f: E.page_style(t) for f, t in pages.items()}
explicit = [f for f in pages if style[f] == "explicit"]


def breaks(raw):
    t = E.pre_breaks(raw)
    out = []
    for m in re.finditer(r"([A-Za-z]+)\\([ \t\n]*)([A-Za-z]+)", t):
        L, sp, R = m.group(1), m.group(2), m.group(3)
        if R[0].isupper():
            continue
        out.append((L, R, 1 if sp else 0))   # 1 = truth split ('ab\ cd'), 0 = truth join ('ab\cd')
    return out


results = {}
thresholds = [-2, -1, 0, 1, 1.5, 2, 3, 5, 8, 10]
agg = {th: [0, 0, 0, 0] for th in thresholds}   # tp_join, fp_join, tn, fn
for parity in (0, 1):
    train = [f for f in explicit if int(f[1:-1]) % 2 == parity]
    test = [f for f in explicit if int(f[1:-1]) % 2 != parity]
    wc = E.certain_tokens({f: pages[f] for f in train}, {f: "explicit" for f in train})
    seg = Segmenter(wc)
    for f in test:
        for L, R, split in breaks(pages[f]):
            s = seg.score(L, R)
            for th in thresholds:
                join_pred = s > th
                if join_pred and not split:
                    agg[th][0] += 1
                elif join_pred and split:
                    agg[th][1] += 1
                elif not join_pred and split:
                    agg[th][2] += 1
                else:
                    agg[th][3] += 1
for th, (tp, fp, tn, fn) in agg.items():
    n = tp + fp + tn + fn
    results[str(th)] = {"n": n, "accuracy": round((tp + tn) / n, 4),
                        "true_join": tp, "false_join": fp, "true_split": tn, "missed_join": fn,
                        "word_count_bias": fp - fn}
print(json.dumps(results, indent=1))
json.dump({"explicit_pages": len(explicit), "by_threshold": results},
          open(os.path.join(HERE, "linebreak_validation.json"), "w"), indent=1)
