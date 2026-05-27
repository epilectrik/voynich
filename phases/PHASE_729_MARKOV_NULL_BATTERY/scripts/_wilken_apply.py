"""Apply Wilken Key v4.0 cipher mechanically to a folio she didn't translate.

Wilken's framework:
- Slot 0: state prefix (qo-, y-, dy-, ol-)
- Slot 1: gallows (T=t, F=p, K=k, P=cph, CH=ch/sh)
- Slot 2-8: vowel/process core
- Slot 9-11: terminal suffix (dy=present cont., edy=past, aiin=plural,
  ain=imperative, an=sequential, in=contained, on=absence, etc.)

Compound table (Layer 1B):
  ol=essence/core   al=outer/bark     or=prepared/ready  ar=raw/as-found
  ot=take/admin     at=receive/absorb et=the given       od=earth-substance
  ad=descend        os=refined        as=raw refined     on=without
  an=and-then       en=do-not         ok=cold app        ak=cold herb
  og=heating app    ag=heating herb   oy=dried essence   ay=dried outer
  om=mixed essence  am=combine        op=pressed         ap=press method
  of=dissolved      af=dissolving     ob=sealed          ab=vessel

Confirmed lexicon entries (Layer 2-3):
  dau=to/into  ag=at/by  ar=upon/on  ai=at(variant)
  -no=or  and=and  goi tao=which-flows  2cor=step/turn
  Tay=is/am/are  qo-=Readiness particle  ol-=essence/core
"""
from collections import defaultdict
from scripts.voynich import Transcript

WILKEN_PREFIXES = {
    'qo': 'qo[Readiness]',
    'y':  'y[Readiness-S0]',
    'dy': 'dy[Readiness-S0v]',
    'ol': 'ol[essence-core]',
}

WILKEN_GALLOWS = {
    'k': 'K[Core-seed-extract]',
    't': 'T[Old-Warrior/root-primary]',
    'f': 'F[Fringe-surface]',
    'p': 'P[discourse-particle]',
    'ch': 'CH[earth-anchor]',
    'sh': 'CH-variant[earth]',
}

WILKEN_COMPOUNDS = {
    'ol': 'essence',     'al': 'outer/bark',     'or': 'prepared',    'ar': 'raw',
    'ot': 'take',        'at': 'absorb',         'et': 'the-given',   'od': 'earth-subst',
    'ad': 'descend',     'os': 'refined',        'as': 'semi-refined','on': 'without',
    'an': 'and-then',    'en': 'do-not',         'ok': 'cooling-app', 'ak': 'cooling-herb',
    'og': 'heating-app', 'ag': 'heating-herb',   'oy': 'dried-essence','ay': 'dried-outer',
    'om': 'mixed-essence','am': 'combine',       'op': 'pressed',     'ap': 'press-method',
    'of': 'dissolved',   'af': 'dissolving',     'ob': 'sealed',      'ab': 'vessel',
}

WILKEN_SUFFIXES = {
    'edy':  'PAST-completed',
    'aiin': 'PLURAL',
    'ain':  'IMPERATIVE',
    'aun':  'RESULT-state',
    'an':   'SEQUENTIAL',
    'in':   'CONTAINED',
    'on':   'ABSENCE',
    'os':   'SUPERLATIVE',
    'as':   'COMPARATIVE',
    'ot':   'TAKE-IMP',
    'od':   'LOCATIVE-below',
    'or':   'PREPARED',
    'ol':   'ESSENCE-retained',
    'dy':   'PRESENT-cont',
}

WILKEN_LEXICON_HIGH_CONF = {
    # Wilken's confirmed crib entries
    '8':        'BARAND[deep-root/bone]',
    '8ar':      'BARAND[deep-root/bone]',
    'olloen':   'first-oil-vessel/spring-opening',
    'ollaig':   'oil-destination',
    'ottco':    'sealed-earth-vessel',
    'ottceg':   'sealed-earth-destination',
    'chedy':    'CH-earth-destination',
    'gott9':    'recipe-terminal[sealed+verified]',
    'cnoti':    'core/kernel-vessel',
    'canoa':    'pure-spring-water',
    'ag':       'at/by',
    'ar':       'upon/on',
    'ai':       'at(var)',
    'dau':      'to/into',
    'Tay':      'is/am/are',
    'and':      'AND',
    'auo':      'water-vessel',
    'auio':     'water-vessel(var)',
    'qokedy':   'qo+Core+e+d+y[Readiness-Core-preparation-PAST]',
    'qokeedy':  'qo+Core+ee+d+y',
    'qokain':   'qo+Core+ain[IMP]',
    'shedy':    'CHv+earth-destination-PAST',
}

def parse_token_wilken(w):
    """Apply Wilken's slot decomposition + lookup."""
    if w in WILKEN_LEXICON_HIGH_CONF:
        return f'[{WILKEN_LEXICON_HIGH_CONF[w]}]'
    parts = []
    rem = w
    # Slot 0: state prefix
    for p in ('qo', 'dy', 'ol', 'y'):
        if rem.startswith(p):
            parts.append(WILKEN_PREFIXES[p])
            rem = rem[len(p):]
            break
    # Slot 1: gallows
    for g in ('ch', 'sh', 'k', 't', 'f', 'p'):
        if rem.startswith(g):
            parts.append(WILKEN_GALLOWS[g])
            rem = rem[len(g):]
            break
    # Slot 9-11: terminal suffix (longest match)
    suffix_match = ''
    for s in sorted(WILKEN_SUFFIXES.keys(), key=len, reverse=True):
        if rem.endswith(s) and len(rem) > len(s):
            suffix_match = s
            rem = rem[:-len(s)]
            break
    # Whatever's left in the middle — check for compounds
    middle_parts = []
    i = 0
    while i < len(rem):
        # try 2-char compound first
        if i + 2 <= len(rem) and rem[i:i+2] in WILKEN_COMPOUNDS:
            middle_parts.append(WILKEN_COMPOUNDS[rem[i:i+2]])
            i += 2
        else:
            middle_parts.append(rem[i])
            i += 1
    if middle_parts:
        parts.append('+'.join(middle_parts))
    if suffix_match:
        parts.append(WILKEN_SUFFIXES[suffix_match])
    if not parts:
        return f'[{w}]'
    return '+'.join(parts)


def render_folio(folio_id, n_lines=8):
    tx = Transcript()
    lines = defaultdict(list)
    for t in tx.currier_b(exclude_labels=True, exclude_uncertain=True):
        if t.folio != folio_id:
            continue
        w = t.word.strip()
        if not w:
            continue
        lines[t.line].append(w)

    print(f'\n========== {folio_id} via WILKEN KEY v4.0 ==========\n')
    sorted_lines = sorted(lines.keys(), key=lambda x: int(x) if str(x).isdigit() else 999)
    for L in sorted_lines[:n_lines]:
        words = lines[L]
        print(f'L{L} ({len(words)} tokens):')
        print(f'  raw:    {" ".join(words)}')
        glosses = [parse_token_wilken(w) for w in words]
        for w, g in zip(words, glosses):
            print(f'    {w:<14} -> {g}')
        print()


# Pick folios Wilken DID NOT translate
# She covers: f15r, f17r, f42r, f70v, f71r, f71v, f72r-v, f73r-v, f86v, f88v/89r
# Pick: f80r (recipe, Currier B, undocumented in her work)
# and f102v (another recipe folio)
render_folio('f80r', n_lines=6)
render_folio('f102v', n_lines=4)
