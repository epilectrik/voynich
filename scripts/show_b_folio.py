"""
Display Currier B folio with configurable output columns.

Usage:
    python scripts/show_b_folio.py f26r              # All columns
    python scripts/show_b_folio.py f26r --no-calc    # Hide calculated gloss
    python scripts/show_b_folio.py f26r --no-manual  # Hide manual gloss
    python scripts/show_b_folio.py f26r --tokens-only # Just tokens
    python scripts/show_b_folio.py f26r --line 3     # Single line
    python scripts/show_b_folio.py f26r --paragraph  # Flowing paragraph view
    python scripts/show_b_folio.py f26r -p --no-color # Paragraph without colors
    python scripts/show_b_folio.py f26r --flow       # Control-flow rendering
    python scripts/show_b_folio.py f26r -s           # Raw morpheme structural view
    python scripts/show_b_folio.py f26r --detail 4   # Full metadata dump
    python scripts/show_b_folio.py f26r --profile    # Program card (Tier 2)
    python scripts/show_b_folio.py f26r --profile --interp  # Card + Tier 3-4
    python scripts/show_b_folio.py f26r --profile -p # Card + paragraph view
"""
import argparse
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.voynich import BFolioDecoder, TokenDictionary, MiddleDictionary

try:
    from colorama import init, Fore, Style
    init()
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False

# FL stage colors for --flow mode (stage-specific, kept separate from role colors)
FL_COLORS = {
    'INITIAL': Fore.CYAN,
    'EARLY': Fore.BLUE,
    'MEDIAL': Fore.YELLOW,
    'LATE': Fore.MAGENTA,
    'TERMINAL': Fore.RED,
} if HAS_COLOR else {}


def token_color(tok) -> str:
    """Semantic color by functional role. Priority: HT > FL > prefix_role.

    Bands: HOT (QO=red, CC=yellow), COOL (CHSH=cyan, FL=light blue),
    EARTH (AX=green, PREP=light green), NEUTRAL (HT=dim, BARE=white).
    """
    if not HAS_COLOR:
        return ''
    if tok.is_dark_pipeline:
        return Fore.MAGENTA
    if tok.is_ht:
        return Style.DIM + Fore.WHITE
    if tok.is_fl_role:
        return Fore.LIGHTBLUE_EX
    role = tok.prefix_role
    if role == 'EN_QO':
        return Fore.RED
    if role == 'EN_KERNEL':
        return Fore.CYAN
    if role in ('AX_SCAFFOLD', 'AX_LATE'):
        return Fore.GREEN
    if role == 'PREP_TIER':
        return Fore.LIGHTGREEN_EX
    if role == 'CC_INIT':
        return Fore.YELLOW
    return Fore.LIGHTWHITE_EX


def print_legend():
    """Print compact color legend at top of output."""
    if not HAS_COLOR:
        return
    parts = [
        f"{Fore.RED}QO:energy{Style.RESET_ALL}",
        f"{Fore.CYAN}CH/SH:monitor{Style.RESET_ALL}",
        f"{Fore.YELLOW}CC:control{Style.RESET_ALL}",
        f"{Fore.LIGHTBLUE_EX}FL:state{Style.RESET_ALL}",
        f"{Fore.GREEN}AX:scaffold{Style.RESET_ALL}",
        f"{Fore.LIGHTGREEN_EX}PREP:prep{Style.RESET_ALL}",
        f"{Fore.MAGENTA}DP:dark-pipeline{Style.RESET_ALL}",
        f"{Style.DIM}{Fore.WHITE}HT:human{Style.RESET_ALL}",
        f"{Fore.LIGHTWHITE_EX}BARE:bare{Style.RESET_ALL}",
    ]
    print(f"Legend: {' | '.join(parts)}")


# ── Control IR mode ─────────────────────────────────────────────────────────

# BCSC role census (C121, C573, C581-C583, C563-C572)
# Role follows deterministically from class membership. 4+18+19+4+4 = 49.
_BCSC_CC = frozenset({10, 11, 12, 17})
_BCSC_EN = frozenset({8, 31, 32, 33, 34, 35, 36, 37, 39, 41, 42, 43, 44, 45, 46, 47, 48, 49})
_BCSC_AX = frozenset({1, 2, 3, 4, 5, 6, 15, 16, 18, 19, 20, 21, 22, 24, 25, 26, 27, 28, 29})
_BCSC_FQ = frozenset({9, 13, 14, 23})
_BCSC_FL = frozenset({7, 30, 38, 40})

# AX sub-positions (C563-C564, Tier 2): positional stratification, NOT lanes
_AX_SUBPOS = {
    4: 'INIT', 5: 'INIT', 6: 'INIT', 24: 'INIT', 26: 'INIT',
    1: 'MED', 2: 'MED', 3: 'MED', 16: 'MED', 18: 'MED',
    27: 'MED', 28: 'MED', 29: 'MED',
    15: 'FINAL', 19: 'FINAL', 20: 'FINAL', 21: 'FINAL',
    22: 'FINAL', 25: 'FINAL',
}

# C611 PREFIX→role prediction (99.2% accuracy, Tier 2).
# Maps prefix_role strings to 5-role taxonomy for HT/UN annotation.
# This is morphological affinity, NOT classification (C740 exclusion stands).
_C611_ROLE_MAP = {
    'EN_KERNEL': 'EN', 'EN_QO': 'EN', 'PREP_TIER': 'EN',
    'AX_SCAFFOLD': 'AX', 'AX_LATE': 'AX',
    'FL_FINAL': 'FL',
    # CC_INIT excluded: C611 says CC = 0.0% of UN predictions.
}

def _c611_predicted_role(prefix_role_raw: Optional[str]) -> Optional[str]:
    """C611 role prediction from PREFIX morphology (99.2% accuracy).

    Returns predicted role (EN/AX/FQ/FL) or None if no prediction.
    CC excluded per C611 (0.0% of UN predictions).
    This is a morphological property of the token, NOT a classification.
    """
    if not prefix_role_raw:
        return None
    mapped = _C611_ROLE_MAP.get(prefix_role_raw)
    if mapped:
        return mapped
    for prefix in ('EN', 'AX', 'FL', 'FQ'):
        if prefix_role_raw.startswith(prefix):
            return prefix
    return None


@dataclass
class IRToken:
    """Single token in IR representation."""
    word: str
    position: int           # 1-based position in source line
    prefix: str
    middle: str
    suffix: str
    role_5: str             # EN/AX/CC/FL/FQ (census) | HT_UN (C740 exclusion)
    lane: str               # QO/CHSH/OTHER
    zone: str               # SETUP/WORK/CHECK/CLOSE/FL/HT_UN
    kernels: List[str]
    macro_state: Optional[str]
    fl_stage: Optional[str]
    is_fl_role: bool
    is_ht: bool
    is_dark_pipeline: bool
    t3_gloss: Optional[str]
    suffix_gloss: Optional[str]   # Dictionary gloss for suffix MIDDLE
    sister_tag: Optional[str]     # 'precision' / 'tolerance' / None
    hub_sub_role: Optional[str]
    token_class: Optional[int] = None   # 49-class number
    fq_group: Optional[str] = None      # CONN/PREFIXED/CLOSER (C593)
    prefix_phase: Optional[str] = None  # SETUP/PREP/WORK/CLOSE (C556)
    prefix_role_raw: Optional[str] = None  # Raw prefix_role for audit
    zone_basis: str = ''               # census/phase/role/ht/dp/c740/default

    def role_tag(self) -> str:
        """Role-typed notation per BCSC census (C573, C581-C583, C563-C572).

        Format: word[ROLE:SUB|cN] or word[ROLE:SUB|cN|zb:BASIS]
        - cN = 49-class number (C121), omitted if unclassified
        - EN gets lane sub-label :QO/:CHSH (C574, C643-C649: EN-internal)
        - AX gets positional sub-label :INIT/:MED/:FINAL (C563-C564)
        - zb: = zone routing basis, shown only for non-census routing
        - HT/UN = excluded from 479-type grammar (C740)
        """
        cls = f"|c{self.token_class}" if self.token_class is not None else ""
        # Zone basis: only for non-census, non-default routing
        zb = ""
        if self.zone not in ('WORK', 'HT_UN'):
            if self.zone_basis == 'phase' and self.prefix_phase:
                zb = f"|zb:ph={self.prefix_phase}"
            elif self.zone_basis == 'role' and self.prefix_role_raw:
                zb = f"|zb:r={self.prefix_role_raw}"
            # 'flag' basis removed: is_fl_role is C611 prediction, not zone routing
            # 'census' and 'default' -> no zb (implicit from role+class)

        if self.is_dark_pipeline:
            pred = _c611_predicted_role(self.prefix_role_raw)
            ptag = f"|pred:{pred}" if pred else ""
            return f"*{self.word}*[HT/UN,DP{cls}{ptag}]"  # C740 + C1137 + C611
        if self.is_ht:
            pred = _c611_predicted_role(self.prefix_role_raw)
            ptag = f"|pred:{pred}" if pred else ""
            return f"{self.word}[HT/UN{cls}{ptag}]"   # C740 + C611
        if self.role_5 == 'HT_UN':
            pred = _c611_predicted_role(self.prefix_role_raw)
            ptag = f"|pred:{pred}" if pred else ""
            return f"{self.word}[HT/UN{ptag}]"        # C740 + C611
        if self.role_5 == 'FQ' and self.fq_group:
            return f"{self.word}[FQ:{self.fq_group}{cls}{zb}]"
        if self.role_5 == 'FL':
            return f"{self.word}[FL{cls}{zb}]"
        if self.role_5 == 'CC':
            return f"{self.word}[CC{cls}{zb}]"
        if self.role_5 == 'EN':
            return f"{self.word}[EN:{self.lane}{cls}{zb}]"  # Lane is EN-internal (C574)
        if self.role_5 == 'AX':
            subpos = _AX_SUBPOS.get(self.token_class, '') if self.token_class else ''
            sp = f":{subpos}" if subpos else ""
            return f"{self.word}[AX{sp}{cls}{zb}]"
        return f"{self.word}[HT/UN]"             # Defensive fallback

    def parse_notation(self) -> str:
        """Compact parse: word[prefix:middle.suffix]"""
        p = self.prefix + ':' if self.prefix else ':'
        m = self.middle or ''
        s = '.' + self.suffix if self.suffix else ''
        return f"{self.word}[{p}{m}{s}]"


@dataclass
class IRBlock:
    """Compiled IR block for one line."""
    line_id: str
    paragraph_zone: Optional[str]
    fl_range: Optional[str]            # From genuine FL tokens only (C582)
    suffix_stage_range: Optional[str]  # From all tokens' suffix-derived fl_stage
    suffix_mode: Optional[str]         # 'A' (spec/energy) or 'B' (continuation/bare) per C1229
    kernel_summary: str
    lane_counts: Dict[str, int]

    setup_tokens: List[IRToken] = field(default_factory=list)
    work_en_chsh: List[IRToken] = field(default_factory=list)  # EN tokens, CHSH lane (C574)
    work_en_qo: List[IRToken] = field(default_factory=list)    # EN tokens, QO lane (C574)
    work_ax: List[IRToken] = field(default_factory=list)        # AX tokens (position in tag, C563)
    check_tokens: List[IRToken] = field(default_factory=list)
    close_tokens: List[IRToken] = field(default_factory=list)
    fl_tokens: List[IRToken] = field(default_factory=list)
    ht_tokens: List[IRToken] = field(default_factory=list)

    raw_sequence: List[str] = field(default_factory=list)
    t3_annotations: List[tuple] = field(default_factory=list)  # (pos, parse, gloss, word)

    # Control loop annotations (C1234, C1235, C1237)
    loop_markers: Dict[str, str] = field(default_factory=dict)  # {'setup': word, 'check': word}
    line_final_type: Optional[str] = None  # FINALIZE/LOOP_CHECK/TERMINAL/CLOSE/ROUTE/OPEN


def _ir_zone_and_basis(tok, token_class) -> tuple:
    """Map token to (zone, basis) for auditable zone routing.

    Zone: SETUP/WORK/CHECK/CLOSE/FL/HT_UN (C556).
    Basis: census/phase/role/ht/dp/c740/default — WHY token is in this zone.
    Priority: DP > HT(dict) > unclassified/C740 > census(FQ/FL/CC) > phase > WORK.
    """
    if tok.is_dark_pipeline:
        return ('HT_UN', 'dp')             # C1137: DP subset HT/UN
    if tok.is_ht:
        return ('HT_UN', 'ht')             # C740: HT/UN population (dict flag)

    if token_class is None:
        return ('HT_UN', 'c740')           # C740: unclassified = HT/UN by exclusion

    # Census-based zone routing (classified tokens only)
    if token_class in _BCSC_FQ:
        return ('CHECK', 'census')         # C583: FQ census
    if token_class in _BCSC_FL:
        return ('FL', 'census')            # C582: FL census
    if token_class in _BCSC_CC:
        return ('SETUP', 'census')         # C581: CC census

    # Classified EN/AX: prefix-based zone routing
    if tok.prefix_role == 'AX_LATE':
        return ('CHECK', 'role')
    phase = tok.prefix_phase
    if phase == 'SETUP':
        return ('SETUP', 'phase')
    if phase in ('PREP', 'WORK'):
        return ('WORK', 'phase')
    if phase == 'CLOSE':
        return ('CLOSE', 'phase')
    if tok.prefix_role == 'CC_INIT':
        return ('SETUP', 'role')
    return ('WORK', 'default')


def _ir_role_5(tok, token_class) -> str:
    """Role from BCSC census sets (C121, C573, C581-C583, C563-C572).

    Classified tokens: role is deterministic from class (census).
    Unclassified tokens: HT_UN per C740 exclusion.
    (is_fl_role is morphological affinity per C611, not classification.)
    """
    if token_class is None:
        return 'HT_UN'
    if token_class in _BCSC_CC: return 'CC'
    if token_class in _BCSC_EN: return 'EN'
    if token_class in _BCSC_AX: return 'AX'
    if token_class in _BCSC_FQ: return 'FQ'
    if token_class in _BCSC_FL: return 'FL'
    return 'HT_UN'  # Defensive: classified but not in any census set


def _assert_census_role(token_class: int, role: str):
    """Fail fast if printed role contradicts census membership (expert invariant)."""
    expected = None
    if token_class in _BCSC_CC:
        expected = 'CC'
    elif token_class in _BCSC_EN:
        expected = 'EN'
    elif token_class in _BCSC_AX:
        expected = 'AX'
    elif token_class in _BCSC_FQ:
        expected = 'FQ'
    elif token_class in _BCSC_FL:
        expected = 'FL'
    if expected and role != expected:
        raise AssertionError(
            f"CENSUS VIOLATION: class {token_class} requires role {expected}, got {role}")


def _ir_lane(tok) -> str:
    """Simplified lane for IR grouping."""
    from scripts.voynich import BTokenAnalysis
    if tok.morph and tok.morph.prefix:
        lane = BTokenAnalysis._get_prefix_lane(tok.morph.prefix)
        if lane in ('QO', 'CHSH'):
            return lane
    # Bare prefix-like tokens (e.g. word='qo' with no MIDDLE) — check word itself
    if tok.morph and not tok.morph.prefix and tok.morph.middle:
        lane = BTokenAnalysis._get_prefix_lane(tok.morph.middle)
        if lane in ('QO', 'CHSH'):
            return lane
    return 'OTHER'


def _ir_color(t: IRToken) -> str:
    """Color by role for IR mode. Priority matches zone/role priority."""
    if not HAS_COLOR:
        return ''
    if t.is_dark_pipeline:
        return Fore.MAGENTA
    if t.is_ht or t.role_5 == 'HT_UN':
        return Style.DIM + Fore.WHITE      # All HT/UN: dim white
    if t.role_5 == 'FQ':
        return Fore.GREEN
    if t.role_5 == 'FL':
        return Fore.LIGHTBLUE_EX
    if t.role_5 == 'EN' and t.lane == 'QO':
        return Fore.RED                    # EN QO lane only (C574)
    if t.role_5 == 'EN' and t.lane == 'CHSH':
        return Fore.CYAN                   # EN CHSH lane only (C574)
    if t.role_5 == 'AX':
        return Fore.GREEN
    if t.role_5 == 'CC':
        return Fore.YELLOW
    return Fore.LIGHTWHITE_EX


def _format_ir_token(t: IRToken, color_enabled: bool) -> str:
    """Format token with position and role tag (C581-C583, C591, C593)."""
    base = f"{t.position}:{t.role_tag()}"
    if color_enabled:
        c = _ir_color(t)
        return f"{c}{base}{Style.RESET_ALL}" if c else base
    return base


# PREFIX operational glosses from decoder_maps.json prefix_actions
_PREFIX_GLOSS = {
    'qo': 'energy', 'ch': 'test', 'sh': 'monitor', 'ok': 'vessel', 'ot': 'adjust',
    'ol': 'close', 'ke': 'heat-burst', 'ek': 'check-heat', 'da': 'infrastructure',
    'sa': 'begin', 'so': 'initiate', 'ct': 'control', 'kch': 'precision-heat',
    'pch': 'process', 'tch': 'process', 'dch': 'process', 'lch': 'process',
    'fch': 'process', 'rch': 'process', 'sch': 'process', 'ksh': 'process',
    'te': 'process', 'lk': 'check', 'lsh': 'link', 'yk': 'init',
    'ko': 'heat', 'ka': 'anchor', 'do': 'mark', 'po': 'setup',
    'or': 'portion', 'ar': 'close', 'al': 'close', 'ta': 'transfer',
    'to': 'transfer', 'de': 'divide', 'pe': 'start', 'se': 'scaffold',
}

# SUFFIX whole-unit glosses (BCSC operational layer — never character-expand)
_SUFFIX_GLOSS = {
    'edy': 'batch', 'dy': 'close', 'y': 'end', 'ey': 'set',
    'ar': 'close', 'aiin': 'check', 'hy': 'confirm', 'al': 'collect',
    'eey': 'deep-cool', 's': 'break', 'or': 'portion',
    'ain': 'intake', 'am': 'done', 'an': 'link', 'om': 'complete',
    'ol': 'store', 'in': 'load', 'oly': 'store-end', 'ry': 'release',
    'o': 'hold', 'oiin': 'hold-check',
}

# Character-level MIDDLE atom glosses (C1195 confidence tiers)
_CHAR_GLOSS = {
    # LOCKED (strong compound evidence, internally consistent)
    'k': 'heat', 'e': 'cool', 'h': 'watch', 'y': 'end',
    'i': 'iterate', 'n': 'halt', 'a': 'accept', 'm': 'final',
    # SOLID (good evidence, label might be refined)
    'd': 'seal', 't': 'drive',
    # PLAUSIBLE (thin evidence, nothing contradicts)
    'c': 'adjust', 'p': 'pause', 'f': 'flag', 's': 'separate', 'g': 'complete',
    # WEAK (correct direction but very generic)
    'o': 'vessel', 'l': 'collect', 'r': 'flow',
}


def _char_expand(chars: str) -> str:
    """Expand each character to its C1195 gloss, joined by hyphens."""
    return '-'.join(_CHAR_GLOSS.get(c, c) for c in chars)


def _ir_t3_gloss(t: IRToken) -> Optional[tuple]:
    """Build Tier 3 annotation as character-level kernel expansion.

    Each character in the MIDDLE and SUFFIX is expanded to its C1195 gloss.
    No dictionary lookup — purely structural, fully transparent.
    Provenance: C1195 atom gloss confidence tiers, kernel operators C089.
    """
    if t.is_dark_pipeline or t.is_ht or t.role_5 == 'HT_UN':
        return None                        # C1137/C740: not operational
    if not t.middle:
        return None                        # No MIDDLE to expand

    # Role tag: EN:QO, EN:CHSH, AX, FQ, CC, FL
    if t.role_5 == 'EN':
        role_tag = f"EN:{t.lane}" if t.lane else 'EN'
    elif t.role_5 == 'FQ':
        role_tag = 'FQ'
    else:
        role_tag = t.role_5 or '?'

    pfx = t.prefix if t.prefix else ''
    mid_exp = _char_expand(t.middle)

    # Suffix: whole-unit gloss (BCSC operational layer), never character-expand
    sfx_exp = ''
    if t.suffix:
        sfx_label = _SUFFIX_GLOSS.get(t.suffix, t.suffix)
        sfx_exp = f' ({sfx_label})'

    if pfx:
        pfx_gloss = _PREFIX_GLOSS.get(pfx, pfx)
        gloss = f"[{role_tag}] ({pfx_gloss}) {mid_exp}{sfx_exp}"
    else:
        gloss = f"[{role_tag}] {mid_exp}{sfx_exp}"
    return (t.word, gloss)


def _print_ir_wrapped(prefix: str, items: List[str], indent: int = 10, width: int = 80):
    """Print items wrapped to width with continuation indent."""
    if not items:
        print(prefix)
        return
    line = prefix + ' ' + items[0]
    for item in items[1:]:
        test = line + ' ' + item
        clean = re.sub(r'\x1b\[[0-9;]*m', '', test)
        if len(clean) > width:
            print(line)
            line = ' ' * indent + item
        else:
            line = test
    if line.strip():
        print(line)


def compile_ir_block(la, d, middle_dict=None) -> IRBlock:
    """Compile a BLineAnalysis into an IRBlock for display."""
    ir_tokens = []
    for idx, tok in enumerate(la.tokens):
        # 49-class lookup (needed by role and zone functions)
        token_class = d._token_to_class.get(tok.word)

        zone, zone_basis = _ir_zone_and_basis(tok, token_class)
        role_5 = _ir_role_5(tok, token_class)
        lane = _ir_lane(tok)

        # Census invariant assertion (expert requirement)
        if token_class is not None:
            _assert_census_role(token_class, role_5)

        # Sister annotation (C929)
        sister_tag = None
        if tok.morph and tok.morph.prefix in ('ch',):
            sister_tag = 'precision'
        elif tok.morph and tok.morph.prefix in ('sh',):
            sister_tag = 'tolerance'

        # Tier 3 gloss: raw dictionary atom only (not composed middle_meaning)
        t3_gloss = None
        suffix_gloss = None
        if tok.morph and middle_dict:
            if tok.morph.middle:
                raw_gloss = middle_dict.get_gloss(tok.morph.middle)
                if raw_gloss and raw_gloss != 'None' and ' ' not in raw_gloss:
                    t3_gloss = raw_gloss
            if tok.morph.suffix:
                raw_sfx = middle_dict.get_gloss(tok.morph.suffix)
                if raw_sfx and raw_sfx != 'None' and ' ' not in raw_sfx:
                    suffix_gloss = raw_sfx

        # FQ sub-grouping from census (C583, C593)
        fq_group = None
        if token_class in _BCSC_FQ:
            fq_group = {9: 'CONN', 13: 'PREFIXED', 14: 'PREFIXED',
                        23: 'CLOSER'}.get(token_class)

        # FL stage: use census (C582) not just is_fl_role flag
        fl_stage = None
        if tok.fl_stage and tok.fl_stage != 'None':
            if (token_class is not None and token_class in _BCSC_FL) or tok.is_fl_role:
                fl_stage = tok.fl_stage

        ir_tokens.append(IRToken(
            word=tok.word,
            position=idx + 1,              # 1-based position in line
            prefix=tok.morph.prefix if tok.morph else '',
            middle=tok.morph.middle if tok.morph else '',
            suffix=tok.morph.suffix if tok.morph else '',
            role_5=role_5,
            lane=lane,
            zone=zone,
            kernels=tok.kernels if tok.kernels else [],
            macro_state=tok.macro_state,
            fl_stage=fl_stage,
            is_fl_role=tok.is_fl_role,
            is_ht=tok.is_ht,
            is_dark_pipeline=tok.is_dark_pipeline,
            t3_gloss=t3_gloss,
            suffix_gloss=suffix_gloss,
            sister_tag=sister_tag,
            hub_sub_role=tok.hub_sub_role,
            token_class=token_class,
            fq_group=fq_group,
            prefix_phase=tok.prefix_phase,
            prefix_role_raw=tok.prefix_role,
            zone_basis=zone_basis,
        ))

    # Partition by zone (role-first for WORK: C574 lanes are EN-internal)
    setup = [t for t in ir_tokens if t.zone == 'SETUP']
    work_en_chsh = [t for t in ir_tokens if t.zone == 'WORK' and t.role_5 == 'EN' and t.lane == 'CHSH']
    work_en_qo = [t for t in ir_tokens if t.zone == 'WORK' and t.role_5 == 'EN' and t.lane == 'QO']
    # EN tokens with OTHER lane (bare prefix-like words) — route to QO as fallback
    work_en_other = [t for t in ir_tokens if t.zone == 'WORK' and t.role_5 == 'EN' and t.lane not in ('QO', 'CHSH')]
    work_en_qo.extend(work_en_other)
    work_ax = [t for t in ir_tokens if t.zone == 'WORK' and t.role_5 == 'AX']
    check = [t for t in ir_tokens if t.zone == 'CHECK']
    close = [t for t in ir_tokens if t.zone == 'CLOSE']
    fl = [t for t in ir_tokens if t.zone == 'FL']
    ht = [t for t in ir_tokens if t.zone == 'HT_UN']

    # Bidirectional invariant (expert requirement):
    # Forward: WORK tokens must be classified (no HT/UN in WORK)
    for t in work_en_chsh + work_en_qo + work_ax:
        assert t.token_class is not None, f"Unclassified token in WORK: {t.word}"
    # Inverse: classified tokens must not land in HT_UN (no opcodes in substrate)
    for t in ht:
        if t.token_class is not None and not t.is_dark_pipeline:
            raise AssertionError(
                f"CLASSIFIED TOKEN IN HT_UN: {t.word} (class {t.token_class}). "
                f"Census-classified tokens must route to WORK/CHECK/SETUP/FL, not HT_UN.")
    # Completeness: every WORK token must appear in exactly one sub-group
    work_all = [t for t in ir_tokens if t.zone == 'WORK']
    work_captured = len(work_en_chsh) + len(work_en_qo) + len(work_ax)
    if len(work_all) != work_captured:
        dropped = [f"{t.word}(role={t.role_5},lane={t.lane})"
                   for t in work_all if t not in work_en_chsh + work_en_qo + work_ax]
        raise AssertionError(
            f"WORK PARTITION INCOMPLETE: {len(work_all) - work_captured} token(s) not "
            f"captured by EN:CHSH/EN:QO/AX sub-groups: {dropped}")

    # FL range from genuine FL census tokens only (C582)
    abbr = {'INITIAL': 'INIT', 'EARLY': 'EARLY', 'MEDIAL': 'MED',
            'LATE': 'LATE', 'TERMINAL': 'TERM'}
    genuine_fl_stages = [tok.fl_stage for tok in la.tokens
                         if tok.fl_stage and tok.fl_stage != 'None'
                         and d._token_to_class.get(tok.word) in _BCSC_FL]
    fl_range = None
    if genuine_fl_stages:
        first = abbr.get(genuine_fl_stages[0], genuine_fl_stages[0][:4])
        last = abbr.get(genuine_fl_stages[-1], genuine_fl_stages[-1][:4])
        fl_range = f"{first}->{last}" if first != last else first

    # Suffix-derived stage hints from all tokens (separate from FL census)
    all_sfx_stages = [tok.fl_stage for tok in la.tokens
                      if tok.fl_stage and tok.fl_stage != 'None']
    suffix_stage_range = None
    if all_sfx_stages:
        first = abbr.get(all_sfx_stages[0], all_sfx_stages[0][:4])
        last = abbr.get(all_sfx_stages[-1], all_sfx_stages[-1][:4])
        suffix_stage_range = f"{first}->{last}" if first != last else first

    # Kernel summary as multiset (not sequence — C961 unordered)
    all_kernels = []
    for t in ir_tokens:
        all_kernels.extend(t.kernels)
    if all_kernels:
        kc = Counter(all_kernels)
        kernel_summary = ' '.join(f"{k}:{v}" for k, v in sorted(kc.items()))
    else:
        kernel_summary = '-'

    # WORK role counts (role-first, then lane within EN)
    lane_counts = {
        'EN:QO': len(work_en_qo),
        'EN:CHSH': len(work_en_chsh),
        'AX': len(work_ax),
    }

    # Tier 3 annotations: (position, parse, gloss, word)
    t3_records = []
    for t in ir_tokens:
        ann = _ir_t3_gloss(t)
        if ann:
            parse, gloss = ann
            t3_records.append((t.position, parse, gloss, t.word))

    return IRBlock(
        line_id=la.line_id,
        paragraph_zone=la.paragraph_zone,
        fl_range=fl_range,
        suffix_stage_range=suffix_stage_range,
        suffix_mode=la.suffix_mode,
        kernel_summary=kernel_summary,
        lane_counts=dict(lane_counts),
        setup_tokens=setup,
        work_en_chsh=work_en_chsh,
        work_en_qo=work_en_qo,
        work_ax=work_ax,
        check_tokens=check,
        close_tokens=close,
        fl_tokens=fl,
        ht_tokens=ht,
        raw_sequence=[tok.word for tok in la.tokens],
        t3_annotations=t3_records,
        loop_markers=la.loop_markers if hasattr(la, 'loop_markers') else {},
        line_final_type=la.line_final_type if hasattr(la, 'line_final_type') else None,
    )


def _render_ir_block(block: IRBlock, color_enabled: bool):
    """Render a single IRBlock as pseudocode."""
    # Header line
    _zone_abbrev = {'HEADER': 'HEADER', 'SPECIFICATION': 'SPEC', 'EXECUTION': 'EXEC'}
    zone_tag = f" [{_zone_abbrev.get(block.paragraph_zone, block.paragraph_zone)}]" if block.paragraph_zone else ""
    # FL tag: genuine FL tokens (C582) vs suffix-derived hints
    if block.fl_range:
        fl_tag = f" FL:({block.fl_range})"
    elif block.suffix_stage_range:
        fl_tag = f" sfx_hint:({block.suffix_stage_range})"
    else:
        fl_tag = ""
    kern_tag = f" kern({block.kernel_summary})" if block.kernel_summary != '-' else ""
    mode_tag = f" mode:{block.suffix_mode}" if block.suffix_mode else ""

    # Control loop: iteration markers (C1234)
    lm = block.loop_markers
    if lm:
        parts = []
        if 'setup' in lm:
            parts.append(f"setup({lm['setup']})")
        if 'check' in lm:
            parts.append(f"check({lm['check']})")
        loop_tag = f" loop:{'->'.join(parts)}"
    else:
        loop_tag = ""

    # Control loop: line-final classification (C1235, C1237)
    lft = block.line_final_type
    if lft and lft != 'OPEN':
        final_word = block.raw_sequence[-1] if block.raw_sequence else '?'
        final_tag = f" final:{lft}({final_word})"
    elif lft == 'OPEN':
        final_tag = " final:OPEN"
    else:
        final_tag = ""

    role_parts = []
    for k in ('EN:CHSH', 'EN:QO', 'AX'):
        if block.lane_counts.get(k, 0) > 0:
            role_parts.append(f"{k}:{block.lane_counts[k]}")
    lane_tag = '  ' + ' '.join(role_parts) if role_parts else ''

    print(f"L{block.line_id}{zone_tag}{loop_tag}{final_tag}{kern_tag}{mode_tag}{lane_tag}")

    # SETUP zone
    if block.setup_tokens:
        tok_strs = [_format_ir_token(t, color_enabled) for t in block.setup_tokens]
        print(f"  SETUP {{ {' '.join(tok_strs)} }}")

    # HT_UN zone (C740: identification/specification substrate)
    if block.ht_tokens:
        tok_strs = [_format_ir_token(t, color_enabled) for t in block.ht_tokens]
        print(f"  HT_UN {{ {' '.join(tok_strs)} }}")

    # WORK zone (role-first grouping: C574 lanes are EN-internal)
    has_work = block.work_en_chsh or block.work_en_qo or block.work_ax
    if has_work:
        print(f"  WORK {{                                    # unordered (C961)")
        if block.work_en_chsh:
            tok_strs = [_format_ir_token(t, color_enabled) for t in block.work_en_chsh]
            _print_ir_wrapped("    EN:CHSH:", tok_strs, indent=12)
        if block.work_en_qo:
            tok_strs = [_format_ir_token(t, color_enabled) for t in block.work_en_qo]
            _print_ir_wrapped("    EN:QO:  ", tok_strs, indent=12)
        if block.work_ax:
            tok_strs = [_format_ir_token(t, color_enabled) for t in block.work_ax]
            _print_ir_wrapped("    AX:     ", tok_strs, indent=12)
        print(f"  }}")

    # CHECK zone
    if block.check_tokens:
        tok_strs = [_format_ir_token(t, color_enabled) for t in block.check_tokens]
        print(f"  CHECK {{ {' '.join(tok_strs)} }}")

    # FL zone
    if block.fl_tokens:
        fl_strs = []
        for t in block.fl_tokens:
            stage = t.fl_stage or '?'
            fl_strs.append(f"{t.word}:{stage}")
        print(f"  FL {{ {' '.join(fl_strs)} }}")

    # CLOSE zone
    if block.close_tokens:
        tok_strs = [_format_ir_token(t, color_enabled) for t in block.close_tokens]
        print(f"  CLOSE {{ {' '.join(tok_strs)} }}")

    # Tier 3 annotations: character-level kernel expansion (C1195)
    if block.t3_annotations:
        print(f"  # T3 {{unordered}}")
        for pos, word, gloss, _orig in block.t3_annotations:
            print(f"  #   {pos}: {word} = {gloss}")

    # SRC line (raw tokens)
    print(f"  > {' '.join(block.raw_sequence)}")
    print()


def display_ir(folio_id: str, line_num=None, para_num=None, use_color=True):
    """Display folio as Control IR - typed control blocks per line."""
    d = BFolioDecoder()
    middle_dict = MiddleDictionary()
    paragraphs = d.analyze_folio_paragraphs(folio_id)

    if para_num:
        target = f"P{para_num}"
        paragraphs = [p for p in paragraphs if p.paragraph_id == target]
        if not paragraphs:
            print(f"Paragraph {para_num} not found in {folio_id}")
            return

    color_enabled = use_color and HAS_COLOR
    W = 80

    # Epistemological header
    print(f"\n{'=' * W}")
    print(f"FOLIO: {folio_id}  [CONTROL IR - Tier 2 + Tier 3 annotations]")
    print(f"Token format: pos:word[ROLE:SUB|cN] where cN = grammar class (C121).")
    print(f"Role is deterministic from class: BCSC census (C573, C581-C583, C563-C572).")
    print(f"EN sub-label = lane :QO/:CHSH (C574, EN-internal). AX = :INIT/:MED/:FINAL (C563).")
    print(f"WORK grouped by role (EN/AX), then lane within EN. AX is lane-independent (C574).")
    print(f"WORK zones are unordered sets (C961). T3 annotations are unordered.")
    print(f"T3: character-level kernel expansion (C1195). MIDDLE.[SUFFIX] per character. k=heat e=cool h=watch.")
    print(f"sfx_hint is NOT FL state (C1004). FL zone = census only (C582: classes 7,30,38,40).")
    print(f"HT/UN = excluded from 479-type grammar (C740). pred:X = C611 PREFIX morphology (99.2%).")
    print(f"pred is affinity, not classification — HT/UN tokens never appear in role groups.")
    print(f"DP = dark pipeline subset (C1137).")
    print(f"|zb: shown only for non-census zone routing (ph=prefix_phase, r=prefix_role).")
    print(f"loop: C1234 iteration (setup=line-initial iin/in, check=penultimate aiin/ain).")
    print(f"final: C1235/C1237 line ending (FINALIZE/LOOP_CHECK/TERMINAL/CLOSE/ROUTE/OPEN).")
    print(f"term: C1237 paragraph termination by -am.")
    print(f"{'=' * W}")
    if color_enabled:
        print_legend()
    print()

    total_tokens = 0

    for para in paragraphs:
        if line_num:
            lines = [la for la in para.lines if la.line_id == str(line_num)]
        else:
            lines = para.lines

        if not lines:
            continue

        # Paragraph header
        kt = sum(para.kernel_dist.values()) or 1
        kp = int(100 * para.kernel_dist.get('k', 0) / kt)
        hp = int(100 * para.kernel_dist.get('h', 0) / kt)
        ep = int(100 * para.kernel_dist.get('e', 0) / kt)
        bt = para.boundary_token[0].upper() if para.boundary_token else '-'

        # EN% from 5-role counts (census-deterministic)
        role_counts = Counter()
        for la in para.lines:
            for tok in la.tokens:
                tc = d._token_to_class.get(tok.word)
                role_counts[_ir_role_5(tok, tc)] += 1
        total_r = sum(role_counts.values()) or 1
        en_count = role_counts.get('EN', 0)  # Census-only (C740: no predictions)
        en_pct = int(100 * en_count / total_r)

        # Cycling info (C1229-C1232)
        cycling_str = ''
        if para.suffix_mode_sequence:
            mode_seq = ''.join(para.suffix_mode_sequence)
            cycling_str = f' modes=[{mode_seq}]({para.mode_interleave_rate:.0%})'
        if para.tail_product_signature:
            cycling_str += f' tail={para.tail_product_signature}'

        # Paragraph termination (C1237)
        term_str = ''
        if hasattr(para, 'termination_type') and para.termination_type:
            term_str = f' term:AM({para.termination_token})'
        else:
            term_str = ' term:-'

        print(f"-- {para.paragraph_id} ({bt}-gallows, "
              f"{para.line_count}L/{para.token_count}T) "
              f"k{kp}/h{hp}/e{ep} EN:{en_pct}%{cycling_str}{term_str} "
              + '-' * 20)

        for la in lines:
            block = compile_ir_block(la, d, middle_dict)
            total_tokens += len(la.tokens)
            _render_ir_block(block, color_enabled)

    print(f"{'=' * W}")
    print(f"Total: {total_tokens} tokens")


def display_flow(folio_id: str, line_num: int = None, para_num: int = None, use_color: bool = True):
    """Display folio with control-flow rendering: FL stage + operation + suffix semantics."""

    d = BFolioDecoder()

    # Get lines through paragraph analysis (sets paragraph_zone per C932)
    paragraphs = d.analyze_folio_paragraphs(folio_id)
    if para_num:
        paragraphs = [p for p in paragraphs if p.paragraph_id == f"P{para_num}"]
        if not paragraphs:
            print(f"Paragraph {para_num} not found in {folio_id}")
            return
    lines = []
    for p in paragraphs:
        lines.extend(p.lines)

    if not lines:
        print(f"No lines found for {folio_id}")
        return

    if line_num:
        lines = [la for la in lines if la.line_id == str(line_num)]
        if not lines:
            print(f"Line {line_num} not found in {folio_id}")
            return

    color_enabled = use_color and HAS_COLOR and FL_COLORS
    total_count = 0

    # Paragraph structure summary
    all_paras = d.analyze_folio_paragraphs(folio_id)
    para_summary = ", ".join([f"{p.paragraph_id}(L{p.lines[0].line_id}-L{p.lines[-1].line_id})"
                               for p in all_paras if p.lines])

    print(f"\n{'='*100}")
    print(f"FOLIO: {folio_id}  [FLOW VIEW]")
    if para_num:
        print(f"SHOWING: Paragraph {para_num}")
    print(f"STRUCTURE: {para_summary}")
    print(f"{'='*100}")

    # Legend
    if color_enabled:
        print_legend()
        print(f"FL markers shown inline as (FL:STAGE) - only on FL-role tokens")
    print()

    for la in lines:
        total_count += len(la.tokens)

        # Build macro sigils for all tokens (always available)
        sigils = []
        for tok in la.tokens:
            fg = tok.flow_gloss()
            macro = fg.get('macro_state', '') or ''
            if macro.startswith('FL_'):
                sigils.append('FL')
            else:
                sigils.append(macro[:3] if macro else '---')
        sigil_line = ' '.join(sigils)

        # Build flow rendering with colors
        if color_enabled:
            tok_parts = []
            for tok in la.tokens:
                fg = tok.flow_gloss()
                tc = token_color(tok)
                reset = Style.RESET_ALL
                s = f"{tc}{fg['operation']}{reset}"
                # Inline FL marker (stage-colored) — only for FL-role tokens
                if fg['fl_stage']:
                    fl_color = FL_COLORS.get(fg['fl_stage'], '')
                    s += f" {fl_color}{{FL:{fg['fl_stage']}}}{reset}"
                # Control-flow label (bright)
                if fg['flow']:
                    s += f" {Style.BRIGHT}[{fg['flow']}]{reset}"
                tok_parts.append((s, tok.prefix_phase, tok.suffix_continuation))

            # Join with zone-aware separators (C961, C964, C1058)
            if len(tok_parts) <= 1:
                flow_line = tok_parts[0][0] if tok_parts else ''
            else:
                flow_line = tok_parts[0][0]
                for j in range(1, len(tok_parts)):
                    prev_phase = tok_parts[j-1][1]
                    curr_phase = tok_parts[j][1]
                    is_cont = tok_parts[j][2]
                    # Suffix continuation: batch repetition (C1058)
                    if is_cont and prev_phase == 'WORK' and curr_phase == 'WORK':
                        sep = ' = '
                    elif prev_phase == 'WORK' and curr_phase == 'WORK':
                        sep = ' | '
                    else:
                        sep = ' -> '
                    flow_line += sep + tok_parts[j][0]
        else:
            flow_line = la.flow_render()

        # Token row (colored by role)
        if color_enabled:
            token_row = ' '.join(f"{token_color(tok)}{tok.word}{Style.RESET_ALL}" for tok in la.tokens)
        else:
            token_row = ' '.join(tok.word for tok in la.tokens)

        zone_tag = f" [{la.paragraph_zone}]" if la.paragraph_zone else ""
        print(f"L{la.line_id}{zone_tag}: {flow_line}")
        print(f"    macro: {sigil_line}")
        print(f"    [{token_row}]")
        print()

    print(f"{'='*100}")
    print(f"Total: {total_count} tokens")
    print(f"{'='*100}")


def display_paragraph(folio_id: str, line_num: int = None, para_num: int = None, use_color: bool = True, show_calc: bool = True):
    """Display folio as flowing paragraphs with tokens underneath."""

    d = BFolioDecoder()
    td = TokenDictionary()
    md = MiddleDictionary()

    # Get paragraph structure
    paragraphs = d.analyze_folio_paragraphs(folio_id)

    if para_num:
        # Filter to specific paragraph
        paragraphs = [p for p in paragraphs if p.paragraph_id == f"P{para_num}"]
        if not paragraphs:
            print(f"Paragraph {para_num} not found in {folio_id}")
            print(f"Available paragraphs: {[p.paragraph_id for p in d.analyze_folio_paragraphs(folio_id)]}")
            return
        # Get lines from this paragraph
        lines = []
        for p in paragraphs:
            lines.extend(p.lines)
    else:
        lines = d.analyze_folio_lines(folio_id)

    if not lines:
        print(f"No lines found for {folio_id}")
        return

    if line_num:
        lines = [la for la in lines if la.line_id == str(line_num)]
        if not lines:
            print(f"Line {line_num} not found in {folio_id}")
            return

    glossed_count = 0
    total_count = 0
    color_enabled = use_color and HAS_COLOR

    # Show paragraph structure summary
    all_paras = d.analyze_folio_paragraphs(folio_id)
    para_summary = ", ".join([f"{p.paragraph_id}(L{p.lines[0].line_id}-L{p.lines[-1].line_id})"
                               for p in all_paras if p.lines])

    print(f"\n{'='*80}")
    print(f"FOLIO: {folio_id}")
    if para_num:
        print(f"SHOWING: Paragraph {para_num}")
    print(f"STRUCTURE: {para_summary}")
    if color_enabled:
        print_legend()
    print(f"{'='*80}\n")

    for la in lines:
        # Build the flowing gloss line with colors
        glosses = []
        structural_glosses = []
        tokens = []

        for i, tok in enumerate(la.tokens):
            total_count += 1

            # Get both glosses
            raw_manual = td.get_gloss(tok.word)

            # Expanded manual gloss (with *middle substitution)
            expanded_manual = tok.interpretive() if raw_manual else None

            # Auto-composed gloss (with MIDDLE dictionary, without whole-token override)
            tok._token_dict = None  # Suppress whole-token gloss (shown on line 1)
            structural = tok.interpretive()
            tok._token_dict = td  # Restore

            if raw_manual:
                glossed_count += 1

            # Build separate lists for manual, structural, and tokens
            manual_display = expanded_manual if expanded_manual else "___"

            # Apply semantic role color
            if color_enabled:
                color = token_color(tok)
                reset = Style.RESET_ALL
                glosses.append(f"{color}{manual_display}{reset}")
                structural_glosses.append(f"{color}{structural}{reset}")
                tokens.append(f"{color}{tok.word}{reset}")
            else:
                glosses.append(manual_display)
                structural_glosses.append(structural)
                tokens.append(tok.word)

        # Print line: manual gloss, structural (if enabled), tokens
        print(f"L{la.line_id}: {' '.join(glosses)}")
        if show_calc:
            print(f"    {' '.join(structural_glosses)}")
        print(f"    [{' '.join(tokens)}]")
        print()

    print(f"{'='*80}")
    print(f"Total: {total_count} | Glossed: {glossed_count} | Remaining: {total_count - glossed_count}")
    print(f"* = has manual gloss")
    print(f"{'='*80}")


def display_folio(folio_id: str,
                  show_token: bool = True,
                  show_calc: bool = True,
                  show_manual: bool = True,
                  line_num: int = None,
                  debug_ht: bool = False,
                  structural_mode: bool = False,
                  detail_level: int = 2,
                  use_color: bool = True):
    """Display a B folio with configurable columns."""

    d = BFolioDecoder()
    d._debug_ht = debug_ht
    td = TokenDictionary()

    lines = d.analyze_folio_lines(folio_id)
    if not lines:
        print(f"No lines found for {folio_id}")
        return

    # Filter to specific line if requested
    if line_num:
        lines = [la for la in lines if la.line_id == str(line_num)]
        if not lines:
            print(f"Line {line_num} not found in {folio_id}")
            return

    # Count glossed tokens for summary
    glossed_count = 0
    total_count = 0

    # Header
    color_enabled = use_color and HAS_COLOR
    print(f"\n{'='*80}")
    print(f"FOLIO: {folio_id}")
    if color_enabled:
        print_legend()
    print(f"{'='*80}")

    # Epistemological warning (expert recommendation)
    if show_calc:
        mode_label = "STRUCTURAL" if structural_mode else "GLOSS"
        print(f"  [{mode_label} PROJECTION] This output is structural, not")
        print(f"  semantic. Sequential appearance does not imply procedural")
        print(f"  order. Labels are display tokens, not translations.")
        if not structural_mode:
            print(f"  Use --structural-mode to compare raw morphemes.")
        print()

    # Column headers
    headers = []
    if show_token:
        headers.append(f"{'TOKEN':<14}")
    if show_calc:
        col_name = 'STRUCTURAL' if structural_mode else 'CALCULATED'
        headers.append(f"{col_name:<35}")
    if show_manual:
        headers.append(f"{'MANUAL GLOSS':<30}")
    print(' | '.join(headers))
    print('-' * 80)

    for la in lines:
        print(f"\n[Line {la.line_id}]")

        for tok in la.tokens:
            total_count += 1

            # Get manual gloss
            manual_gloss = td.get_gloss(tok.word)
            if manual_gloss:
                glossed_count += 1

            # Get calculated gloss (temporarily disable dict lookup)
            tok._token_dict = None  # Force fallback
            if structural_mode:
                calc_gloss = tok.structural_gloss()
            else:
                calc_gloss = tok.interpretive()
            tok._token_dict = td  # Restore

            # Build row
            cols = []
            if show_token:
                if color_enabled:
                    tc = token_color(tok)
                    cols.append(f"{tc}{tok.word:<14}{Style.RESET_ALL}")
                else:
                    cols.append(f"{tok.word:<14}")
            if show_calc:
                cols.append(f"{calc_gloss:<35}")
            if show_manual:
                manual_display = manual_gloss if manual_gloss else "-"
                cols.append(f"{manual_display:<30}")

            print(' | '.join(cols))

            # Detail level 4: full metadata dump per token
            if detail_level >= 4:
                meta_parts = []
                if tok.macro_state:
                    desc = tok.MACRO_LABELS.get(tok.macro_state, tok.macro_state)
                    meta_parts.append(f"macro:{tok.macro_state} ({desc})")
                if tok.hub_sub_role:
                    meta_parts.append(f"hub:{tok.hub_sub_role}")
                if tok.middle_affordance_bin:
                    meta_parts.append(f"bin:{tok.middle_affordance_bin}")
                if tok.middle_affordance_family:
                    meta_parts.append(f"family:{tok.middle_affordance_family}")
                if tok.prefix_zone:
                    meta_parts.append(f"zone:{tok.prefix_zone}")
                if tok.terminal_group:
                    meta_parts.append(f"tc:{tok.terminal_char}({tok.terminal_group})")
                if tok.compound_depth > 0:
                    meta_parts.append(f"depth:{tok.compound_depth}")
                if tok.compound_atoms:
                    meta_parts.append(f"atoms:{'+'.join(tok.compound_atoms)}")
                if tok.is_dark_pipeline:
                    meta_parts.append(f"DP:True")
                if tok.suffix_continuation:
                    meta_parts.append(f"cont:True")
                if tok.prefix_base:
                    mod_str = tok.prefix_modifier or '-'
                    meta_parts.append(f"pfx:{mod_str}+{tok.prefix_base}")
                if meta_parts:
                    print(f"{'':>14}   {'  '.join(meta_parts)}")

                # HT structural internals (C935: compound specification)
                # Shows raw morpheme identity only — never operational glosses
                if tok.is_ht:
                    ht_parts = []
                    if tok.morph:
                        if tok.morph.prefix:
                            ht_parts.append(f"prefix:{tok.morph.prefix}")
                        if tok.morph.middle:
                            ht_parts.append(f"middle:{tok.morph.middle}")
                        if tok.morph.suffix:
                            ht_parts.append(f"suffix:{tok.morph.suffix}")
                    if tok.middle_kernel:
                        ht_parts.append(f"kernel:{tok.middle_kernel}")
                    if ht_parts:
                        print(f"{'':>14}   HT structure: {'  '.join(ht_parts)}")

    # Summary
    print()
    print(f"{'='*80}")
    print(f"Total tokens: {total_count} | Glossed: {glossed_count} | Remaining: {total_count - glossed_count}")
    print(f"{'='*80}")


def display_profile(folio_id: str, interp: bool = False):
    """Display program card for a Currier B folio.

    --profile: Tier 2 structural card (default, safe for public)
    --profile --interp: Adds Tier 3-4 blocks (material, output, operational gloss)
    """
    d = BFolioDecoder()
    analysis = d.analyze_folio(folio_id)
    if not analysis:
        print(f"Folio {folio_id} not found in Currier B")
        return

    # Print program card
    print(analysis.program_card(interp=interp))

    # Paragraph summary (Tier 2, always shown with profile)
    print(f'\n  PARAGRAPH SUMMARY (C855: independent parallel programs)')
    print(f'  {"=" * 82}')
    print(f'  {"PARA":4s} | G | {"KERNEL k/h/e%":14s} | ROLE | SIZE      | T%  | {"MODES":>12s} | TAIL')
    print(f'  {"-" * 82}')
    para_lines = d.paragraph_summary_lines(folio_id)
    for line in para_lines:
        print(line)
    print(f'  {"=" * 82}')

    # Paragraph architecture summary
    paragraphs = d.analyze_folio_paragraphs(folio_id)
    if paragraphs and len(paragraphs) > 1:
        sizes = sorted([p.token_count for p in paragraphs], reverse=True)
        # Threshold: "dominant" if largest paragraph > 2x the second-largest
        if sizes[0] > 2 * sizes[1]:
            size_detail = ', '.join(f'{s}T' for s in sizes[1:])
            pattern = f'1 dominant ({sizes[0]}T) + {len(sizes)-1} supplements ({size_detail})'
        else:
            pattern = f'{len(sizes)} paragraphs, balanced ({min(sizes)}-{max(sizes)}T)'
        gallows_seq = [p.boundary_token[0].upper() if p.boundary_token else '-'
                       for p in paragraphs]
        print(f'  Size pattern: {pattern}')
        print(f'  Gallows sequence: {" ".join(gallows_seq)}')
    elif paragraphs and len(paragraphs) == 1:
        print(f'  Size pattern: single paragraph ({paragraphs[0].token_count}T)')
    print()


def main():
    parser = argparse.ArgumentParser(description='Display Currier B folio')
    parser.add_argument('folio', help='Folio ID (e.g., f26r)')
    parser.add_argument('--no-token', action='store_true', help='Hide token column')
    parser.add_argument('--no-calc', action='store_true', help='Hide calculated gloss')
    parser.add_argument('--no-manual', action='store_true', help='Hide manual gloss')
    parser.add_argument('--tokens-only', action='store_true', help='Show only tokens')
    parser.add_argument('--line', type=int, help='Show only specific line number')
    parser.add_argument('--paragraph', '-p', action='store_true',
                        help='Flowing paragraph view (gloss + tokens per line)')
    parser.add_argument('--flow', '-f', action='store_true',
                        help='Control-flow view (FL stage + operation + suffix semantics)')
    parser.add_argument('--para', type=int, help='Show only specific paragraph number (1, 2, etc.)')
    parser.add_argument('--no-color', action='store_true', help='Disable color output')
    parser.add_argument('--debug-ht', action='store_true', help='Show HT atom details')
    parser.add_argument('--structural-mode', '-s', action='store_true',
                        help='Raw morpheme notation (strips English MIDDLE/suffix labels)')
    parser.add_argument('--detail', type=int, default=2, choices=[1, 2, 3, 4],
                        help='Detail level: 1=macro only, 2=macro+refinement (default), 3=all layers, 4=full metadata')
    parser.add_argument('--profile', action='store_true',
                        help='Program card: folio-level characterization (Tier 2)')
    parser.add_argument('--interp', action='store_true',
                        help='Add Tier 3-4 interpretive blocks (use with --profile)')
    parser.add_argument('--ir', action='store_true',
                        help='Control IR: typed control blocks per line (Tier 2 + Tier 3)')
    args = parser.parse_args()

    # Profile mode (composable with --paragraph, --flow, or --ir)
    if args.profile:
        display_profile(args.folio, interp=args.interp)
        if args.ir:
            display_ir(args.folio, line_num=args.line, para_num=args.para,
                       use_color=not args.no_color)
        elif args.paragraph:
            display_paragraph(args.folio, line_num=args.line, para_num=args.para,
                              use_color=not args.no_color, show_calc=not args.no_calc)
        elif args.flow:
            display_flow(args.folio, line_num=args.line, para_num=args.para,
                         use_color=not args.no_color)
        return

    if args.ir:
        display_ir(args.folio, line_num=args.line, para_num=args.para,
                   use_color=not args.no_color)
        return

    if args.flow:
        display_flow(args.folio, line_num=args.line, para_num=args.para,
                     use_color=not args.no_color)
        return

    if args.paragraph:
        display_paragraph(args.folio, line_num=args.line, para_num=args.para,
                          use_color=not args.no_color, show_calc=not args.no_calc)
        return

    show_token = not args.no_token
    show_calc = not args.no_calc
    show_manual = not args.no_manual

    if args.tokens_only:
        show_calc = False
        show_manual = False

    display_folio(
        args.folio,
        show_token=show_token,
        show_calc=show_calc,
        show_manual=show_manual,
        line_num=args.line,
        debug_ht=args.debug_ht,
        structural_mode=args.structural_mode,
        detail_level=args.detail,
        use_color=not args.no_color,
    )


if __name__ == '__main__':
    main()
