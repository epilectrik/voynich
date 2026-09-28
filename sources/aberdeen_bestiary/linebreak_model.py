"""Word-segmentation model for ambiguous line-break marks in the Aberdeen transcription.

The site marks every manuscript line end with '\\'. On most pages a mid-word break is
written 'par\\dis' and a between-word break 'et\\ vulpibus'. On the pages of quires G-I
(f41r-f64v, plus f65r, f70r) every break is written '\\ ', so 'sur\\ git' (one word) and
'fractis\\ cervicibus' (two words) look the same. This module decides such cases.

Model: unigram word probability with a character 4-gram backoff (Dirichlet mixing),
    P_w(w) = (count(w) + ALPHA * P_char(w)) / (N + ALPHA)
Decision: join L+R iff  log P_w(LR) - [log P_w(L) + log P_w(R)] > log(prior_split/prior_join).
Trained only on tokens whose boundaries are certain (see extract_latin.py).
"""
import collections
import math

# Chosen by held-out validation on explicit-convention pages (validate_linebreaks.py):
# order 6 / ALPHA 3000 / threshold 1.5 -> 96.3% agreement, net word-count bias 0.
ORDER = 6
LAMBDAS = (0.01, 0.03, 0.08, 0.18, 0.3, 0.4)   # weights for context length 0..5
ALPHA = 3000.0
ALPHABET = "abcdefghijklmnopqrstuvwxyz$"


class CharModel:
    def __init__(self, words):
        self.counts = [collections.defaultdict(collections.Counter) for _ in range(ORDER)]
        for w, c in words.items():
            s = "^" * (ORDER - 1) + w + "$"
            for i in range(ORDER - 1, len(s)):
                ch = s[i]
                for k in range(ORDER):
                    ctx = s[i - k:i] if k else ""
                    self.counts[k][ctx][ch] += c
        self.tot = [{ctx: sum(cn.values()) for ctx, cn in lvl.items()} for lvl in self.counts]

    def logp(self, w):
        s = "^" * (ORDER - 1) + w + "$"
        lp = 0.0
        for i in range(ORDER - 1, len(s)):
            ch = s[i]
            p = 0.0
            wsum = 0.0
            for k in range(ORDER):
                ctx = s[i - k:i] if k else ""
                t = self.tot[k].get(ctx, 0)
                if t:
                    p += LAMBDAS[k] * self.counts[k][ctx][ch] / t
                    wsum += LAMBDAS[k]
            p = p / wsum if wsum else 0.0
            p = 0.999 * p + 0.001 / len(ALPHABET)
            lp += math.log(p)
        return lp


class Segmenter:
    def __init__(self, word_counts):
        self.wc = collections.Counter(word_counts)
        self.N = sum(self.wc.values())
        self.cm = CharModel(self.wc)

    def logpw(self, w):
        return math.log((self.wc.get(w, 0) + ALPHA * math.exp(self.cm.logp(w))) / (self.N + ALPHA))

    def score(self, left, right):
        """>0 favours joining (before the prior)."""
        l, r = left.lower(), right.lower()
        return self.logpw(l + r) - (self.logpw(l) + self.logpw(r))
