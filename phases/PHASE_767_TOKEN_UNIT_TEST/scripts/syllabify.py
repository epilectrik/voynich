"""Rule-based orthographic syllabifier for Latin-script European languages (PHASE_767 controls).

Transparent and deterministic, so the syllable-separated controls are reproducible without external packages. It is
an approximation, not a phonological analysis; its only job is to turn a word-separated text into a stream of
syllable-sized units written with spaces between them, as Vietnamese or Pinyin text is.

Rules, applied per word after lower-casing:
- Nuclei are maximal vowel runs (a e i o u y and accented forms). Language-specific diphthongs stay in one nucleus;
  every other vowel pair splits (hiatus).
- Consonants between two nuclei: one consonant goes to the next syllable (V.CV). With two, the split falls between
  them (VC.CV), unless the pair is an inseparable onset (stop or f + l/r; ch, ph, th, gn, qu, sch, sp, st, and
  similar), which moves whole to the next syllable. With three or more, all but the last onset-valid cluster stay
  in the coda.
- A word with no vowel is kept as one unit.
"""
from __future__ import annotations

import unicodedata

VOWELS = set('aeiouyàáâäãåèéêëìíîïòóôöõùúûüýÿæœ')
ONSETS2 = {'bl', 'br', 'cl', 'cr', 'dr', 'fl', 'fr', 'gl', 'gr', 'pl', 'pr', 'tr', 'ch', 'ph', 'th', 'gn', 'qu', 'sc',
           'sp', 'st', 'sk', 'kl', 'kr', 'sh', 'wr', 'wh', 'gu', 'sw', 'tw', 'dw', 'kn', 'ck'}
ONSETS3 = {'sch', 'str', 'spr', 'scr', 'spl', 'chr', 'thr', 'squ', 'scl'}
DIPHTHONGS = {
    'la': {'ae', 'oe', 'au', 'eu'},
    'it': {'ia', 'ie', 'io', 'iu', 'ua', 'ue', 'uo', 'ui', 'ai', 'ei', 'oi', 'au', 'eu'},
    'es': {'ia', 'ie', 'io', 'iu', 'ua', 'ue', 'uo', 'ui', 'ai', 'ei', 'oi', 'au', 'eu', 'ay', 'ey', 'oy'},
    'de': {'ei', 'ie', 'au', 'eu', 'äu', 'ai'},
    'en': {'ea', 'ee', 'oo', 'ou', 'ai', 'ay', 'ei', 'ey', 'oa', 'oi', 'oy', 'ie', 'ue', 'ew', 'aw', 'ow'},
}


def _is_v(c):
    return c in VOWELS


def syllabify(word, lang):
    w = unicodedata.normalize('NFC', word.lower())
    if not any(_is_v(c) for c in w):
        return [w] if w else []
    diph = DIPHTHONGS.get(lang, set())
    # nuclei: maximal vowel runs split at non-diphthong pairs
    nuclei = []
    i = 0
    while i < len(w):
        if _is_v(w[i]):
            j = i + 1
            while j < len(w) and _is_v(w[j]) and (w[j - 1:j + 1] in diph):
                j += 1
            nuclei.append((i, j))
            i = j
        else:
            i += 1
    if len(nuclei) <= 1:
        return [w]
    cuts = []
    for (a0, a1), (b0, b1) in zip(nuclei, nuclei[1:]):
        cons = w[a1:b0]
        n = len(cons)
        if n == 0:
            cut = a1
        elif n == 1:
            cut = a1
        elif n == 2:
            cut = a1 if cons in ONSETS2 else a1 + 1
        else:
            if cons[-3:] in ONSETS3:
                cut = b0 - 3
            elif cons[-2:] in ONSETS2:
                cut = b0 - 2
            else:
                cut = b0 - 1
        cuts.append(cut)
    out, prev = [], 0
    for c in cuts:
        out.append(w[prev:c])
        prev = c
    out.append(w[prev:])
    return [s for s in out if s]


if __name__ == '__main__':
    tests = {'la': ['dominus', 'patrem', 'aeternus', 'spiritus', 'omnipotentem', 'christus'],
             'it': ['cielo', 'giorno', 'nostro', 'padre', 'figliuolo'],
             'de': ['himmel', 'vater', 'geschichte', 'heilige'],
             'en': ['heaven', 'father', 'kingdom', 'forgive']}
    for lang, ws in tests.items():
        print(lang, [' '.join(syllabify(w, lang)) for w in ws])
