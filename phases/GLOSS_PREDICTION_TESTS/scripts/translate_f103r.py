#!/usr/bin/env python3
"""
FOLIO f103r COMPOSITIONAL READING
=================================
Applies atom-level glosses, category classification, and Brunschwig/Rupescissa
structural interpretation to produce a line-by-line reading of f103r.

f103r is a Currier B folio in Section S (Stars/Recipes), REGIME_1, Archetype 6.
"""

import sys
from pathlib import Path
from collections import defaultdict

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from scripts.voynich import (
    Transcript, Morphology, CategoryClassifier, BFolioDecoder,
    MiddleDictionary, MiddleAnalyzer
)


# ============================================================
# ATOM GLOSSES (from C1195, C1388-C1392, embedded context)
# ============================================================
# Tier: LOCKED=highest confidence, SOLID=strong, PLAUSIBLE=reasonable
ATOM_GLOSSES = {
    # LOCKED (8)
    'k': ('heat/apply-energy', 'LOCKED'),     # Kochen
    'e': ('cool/settle', 'LOCKED'),           # Erkalten
    'h': ('watch/monitor', 'LOCKED'),         # Huten
    'y': ('end/close', 'LOCKED'),
    'i': ('iterate/cycle', 'LOCKED'),
    'n': ('halt/bind', 'LOCKED'),
    'a': ('yield/open', 'LOCKED'),
    'm': ('finalize', 'LOCKED'),
    # SOLID (6)
    'd': ('mark/seal', 'SOLID'),              # Dichten
    't': ('transfer/drive', 'SOLID'),         # Treiben
    'l': ('frame/state', 'SOLID'),
    'o': ('arrange/work', 'SOLID'),           # Ordnen
    'c': ('adjust/loop', 'SOLID'),
    'p': ('pause/mark', 'SOLID'),
    # PLAUSIBLE (5)
    'f': ('flag/mark', 'PLAUSIBLE'),
    's': ('sequence/stage', 'PLAUSIBLE'),
    'g': ('complete', 'PLAUSIBLE'),
    'x': ('diagram/reference', 'PLAUSIBLE'),
    'r': ('input/respond', 'PLAUSIBLE'),
}

# PREFIX action glosses (from C929, C1218-C1219, C1313)
PREFIX_GLOSSES = {
    'pch': 'PREP: process material',
    'tch': 'PREP: process/treat material',
    'lch': 'PREP: strip/extract',
    'dch': 'PREP: seal-process',
    'fch': 'PREP: flag-process',
    'kch': 'PRECISION: controlled heat pulse',
    'ch':  'TEST: active test/check fire (ch-lane)',
    'sh':  'MONITOR: passive watch/scan fire (sh-lane)',
    'qo':  'HEAT-SRC: fire/furnace management',
    'ok':  'VESSEL-TEMP: coarse thermal check',
    'ot':  'VERIFY-OPS: fine operational check',
    'da':  'SETUP: initialize/configure apparatus',
    'ol':  'CONTINUE: maintain current operation',
    'ct':  'CONTROL: manage/restrict',
    'sa':  'SCAFFOLD: structural arrangement',
    'so':  'SCAFFOLD: structural arrangement',
    'ke':  'HEAT-BURST: short heat application',
    'ek':  'CHECK-HEAT: verify temperature',
    'ka':  'HEAT-YIELD: fire-open',
    'ta':  'TRANSFER: move material',
    'te':  'PROCESS: gather/collect',
    'de':  'DIVIDE: separate portions',
    'po':  'PRE-WORK: preliminary operation',
    'do':  'MARK: mark/annotate',
    'al':  'CLOSE: output/gather',
    'ar':  'CLOSE: release/output',
    'or':  'PORTION: divide/portion out',
    'lk':  'WATCH: observe state',
    'lsh': 'LINK: verify connection',
    'ko':  'HEAT: heat arrangement',
    'to':  'TRANSFER: transfer arrangement',
    'se':  'SCAFFOLD: stage-settle',
    'pe':  'START: begin-settle',
}

# SUFFIX glosses (from BCSC suffix_flow)
SUFFIX_GLOSSES = {
    'y':    'END (.)',
    'dy':   'SEAL-END (close.)',
    'edy':  'THOROUGH-END (batch close.)',
    'eey':  'EXTENDED-END (deep.)',
    'ey':   'SELECTIVE-END (set.)',
    'hy':   'VERIFY-END (confirm.)',
    'ry':   'COMPLETE-END (finish.)',
    'ly':   'SETTLED-END (end.)',
    'aiin': 'GATE (bounded loop)',
    'ain':  'CHECK (intake)',
    'iin':  'LOOP (iterate)',
    'oiin': 'SETTLE (vessel loop)',
    'ar':   'CLOSE-CONT (release,)',
    'or':   'PORTION-CONT (divide,)',
    'ol':   'HOLD-CONT (hold)',
    'al':   'TRANSFER-CONT (transfer)',
    'r':    'CONTINUE (,)',
    'l':    'FRAME (|)',
    's':    'NEXT (; step)',
    'in':   'STEP (, step)',
    'an':   'BIND (~)',
    'am':   'FINAL (. stop)',
    'om':   'SEAL-FINAL (. seal)',
    'im':   'CYCLE-FINAL (. cycle)',
}


def decompose_middle_to_atoms(middle):
    """Decompose a MIDDLE into its constituent atoms."""
    if not middle:
        return []
    atoms = list(middle)
    return atoms


def gloss_atoms(atoms):
    """Return glosses for a list of atoms."""
    glosses = []
    for a in atoms:
        if a in ATOM_GLOSSES:
            glosses.append(f"{a}={ATOM_GLOSSES[a][0]}")
        else:
            glosses.append(f"{a}=?")
    return glosses


def compose_reading(middle, atoms, mid_dict):
    """Build a compositional reading from atoms, preferring dictionary if available."""
    # First check the dictionary for a curated gloss
    dict_gloss = mid_dict.get_gloss(middle)
    if dict_gloss:
        return dict_gloss

    # Otherwise compose from atoms
    if not atoms:
        return '?'
    parts = []
    for a in atoms:
        if a in ATOM_GLOSSES:
            parts.append(ATOM_GLOSSES[a][0])
        else:
            parts.append(f'[{a}]')
    return '+'.join(parts)


def build_token_reading(word, morph_obj, mid_dict, cat_classifier):
    """Build a complete interpretive reading for one token."""
    m = morph_obj.extract(word)

    prefix = m.prefix or ''
    middle = m.middle or ''
    suffix = m.suffix or ''
    articulator = m.articulator or ''

    # Atom decomposition of MIDDLE
    atoms = decompose_middle_to_atoms(middle)
    atom_glosses = gloss_atoms(atoms)

    # Compositional reading
    mid_reading = compose_reading(middle, atoms, mid_dict)

    # Category
    category = cat_classifier.classify(middle) if middle else '?'

    # PREFIX gloss
    pfx_gloss = PREFIX_GLOSSES.get(prefix, f'({prefix})' if prefix else 'BARE')

    # SUFFIX gloss
    sfx_gloss = SUFFIX_GLOSSES.get(suffix, f'({suffix})' if suffix else 'NONE')

    return {
        'word': word,
        'articulator': articulator,
        'prefix': prefix,
        'middle': middle,
        'suffix': suffix,
        'atoms': atoms,
        'atom_glosses': atom_glosses,
        'mid_reading': mid_reading,
        'pfx_gloss': pfx_gloss,
        'sfx_gloss': sfx_gloss,
        'category': category,
    }


def build_line_interpretation(token_readings, decoder, line_tokens_raw):
    """Build a line-level interpretation string from token readings."""
    # Get line-level analysis from decoder
    analyzed_tokens = [decoder.analyze_token(t['word']) for t in token_readings]

    # Collect kernel chars across line
    kernels_in_line = []
    categories_in_line = []
    for tr in token_readings:
        for a in tr['atoms']:
            if a in ('k', 'h', 'e'):
                kernels_in_line.append(a)
        categories_in_line.append(tr['category'])

    # Build interpretive sentence
    phrases = []
    for tr in token_readings:
        pfx_action = PREFIX_GLOSSES.get(tr['prefix'], '').split(':')[0] if tr['prefix'] else ''
        if pfx_action:
            pfx_action = f"[{pfx_action}] "

        mid = tr['mid_reading']
        sfx_marker = ''
        if tr['suffix']:
            sfx_short = SUFFIX_GLOSSES.get(tr['suffix'], '')
            if sfx_short:
                # Extract just the parenthetical
                if '(' in sfx_short:
                    sfx_marker = sfx_short[sfx_short.index('(')+1:sfx_short.index(')')]
                else:
                    sfx_marker = sfx_short.split(' ')[0]

        phrase = f"{pfx_action}{mid}"
        if sfx_marker:
            phrase += f" [{sfx_marker}]"
        phrases.append(phrase)

    return ' | '.join(phrases)


def main():
    print("Loading Voynich tools...")
    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()
    decoder = BFolioDecoder()
    mid_dict = MiddleDictionary()

    # Get folio-level context
    fa = decoder.analyze_folio('f103r')
    paras = decoder.analyze_folio_paragraphs('f103r')

    # Get all tokens
    tokens = [tok for tok in tx.currier_b() if tok.folio == 'f103r']
    print(f"f103r: {len(tokens)} tokens, {fa.paragraph_count} lines, Section {fa.section}")

    # Group tokens by line
    lines = defaultdict(list)
    for tok in tokens:
        lines[tok.line].append(tok)

    # Group lines by paragraph (using par_initial markers)
    paragraphs = []
    current_para = []
    current_para_lines = set()
    for line_num in sorted(lines.keys()):
        line_toks = lines[line_num]
        # Check if any token in line is par_initial
        is_new_para = any(t.par_initial for t in line_toks)
        if is_new_para and current_para:
            paragraphs.append(current_para)
            current_para = []
            current_para_lines = set()
        current_para.append((line_num, line_toks))
        current_para_lines.add(line_num)
    if current_para:
        paragraphs.append(current_para)

    # Build output
    output_lines = []

    # Header
    output_lines.append("=" * 100)
    output_lines.append(f"FOLIO f103r: COMPOSITIONAL READING")
    output_lines.append("=" * 100)
    output_lines.append(f"Section: S (Stars/Recipes) | REGIME_1 | Archetype 6 (HAZARD_TOLERANT)")
    kd = fa.kernel_dist or {}
    k_total = sum(kd.values()) or 1
    output_lines.append(f"Kernel Balance: {fa.kernel_balance} (k={kd.get('k',0)/k_total:.0%} h={kd.get('h',0)/k_total:.0%} e={kd.get('e',0)/k_total:.0%})")
    output_lines.append(f"Category Profile: {dict(fa.category_profile)}")
    output_lines.append(f"Token count: {fa.token_count} | Paragraphs: {len(paragraphs)} | Lines: {len(lines)}")
    output_lines.append(f"QO-lane: {fa.qo_fraction:.1%} | ch-sister: {fa.sister_ratio:.1%}")
    output_lines.append("")

    # Brunschwig context
    output_lines.append("BRUNSCHWIG CONTEXT:")
    output_lines.append("  REGIME_1 = First-degree fire (balneum mariae / gentle water-bath heating)")
    output_lines.append("  Section S = Recipe/procedure reference (Stars section)")
    output_lines.append("  ESCAPE_DOMINANT kernel = e-heavy (cooling/stabilization emphasis)")
    output_lines.append("  Archetype 6 = HAZARD_TOLERANT (forgiving program, fewer critical failures)")
    output_lines.append("")
    output_lines.append("-" * 100)
    output_lines.append("")

    # Process each paragraph
    for p_idx, para in enumerate(paragraphs):
        # Paragraph header
        if p_idx < len(paras):
            p_info = paras[p_idx]
            p_kernel = p_info.kernel_balance
            p_cat = p_info.category_key
            p_mode_seq = ''.join(p_info.suffix_mode_sequence) if p_info.suffix_mode_sequence else ''
            p_term = p_info.termination_type or 'none'
        else:
            p_kernel = '?'
            p_cat = ['?']
            p_mode_seq = ''
            p_term = '?'

        # Get first token to check gallows
        first_word = para[0][1][0].word if para[0][1] else '?'
        gallows_char = ''
        for gc in ['k', 'f', 'p', 't']:
            if first_word.startswith(gc) or (len(first_word) > 1 and first_word[0] == 'y' and first_word[1:].startswith(gc)):
                gallows_char = gc
                break
        # Check prefix for gallows
        first_morph = morph.extract(first_word)
        if first_morph.prefix:
            for gc in ['k', 'f', 'p', 't']:
                if first_morph.prefix.startswith(gc) or (first_morph.prefix[0] == 'y' and len(first_morph.prefix) > 1 and first_morph.prefix[1] == gc):
                    gallows_char = gc
                    break

        output_lines.append(f"{'=' * 100}")
        output_lines.append(f"PARAGRAPH {p_idx + 1} of {len(paragraphs)}")
        output_lines.append(f"  Lines: {len(para)} | Kernel: {p_kernel} | Top categories: {p_cat}")
        output_lines.append(f"  Mode sequence: {p_mode_seq} | Termination: {p_term}")
        if gallows_char:
            gallows_map = {'k': 'k-gallows (energy/opener)', 'f': 'f-gallows (flag/opener)',
                          'p': 'p-gallows (stable mode)', 't': 't-gallows (transition mode)'}
            output_lines.append(f"  Gallows: {gallows_map.get(gallows_char, gallows_char)}")
        output_lines.append(f"{'=' * 100}")
        output_lines.append("")

        for line_num, line_toks in para:
            # Build token readings for this line
            readings = []
            for tok in line_toks:
                r = build_token_reading(tok.word, morph, mid_dict, cc)
                r['line_initial'] = tok.line_initial
                r['line_final'] = tok.line_final
                r['par_initial'] = tok.par_initial
                readings.append(r)

            # Line header
            output_lines.append(f"  --- Line {line_num} ({len(readings)} tokens) ---")

            # Token-by-token analysis
            for r in readings:
                pos_markers = []
                if r.get('line_initial'):
                    pos_markers.append('LINE-INIT')
                if r.get('line_final'):
                    pos_markers.append('LINE-FINAL')
                if r.get('par_initial'):
                    pos_markers.append('PAR-INIT')
                pos_str = f" [{','.join(pos_markers)}]" if pos_markers else ''

                atom_str = ' '.join(r['atom_glosses']) if r['atom_glosses'] else '-'

                word_s = r['word'] or '???'
                pfx_s = r['prefix'] or '-'
                mid_s = r['middle'] or '-'
                sfx_s = r['suffix'] or '-'
                cat_s = r['category'] or '?'
                pfx_g = r['pfx_gloss'] or '-'
                mid_r = r['mid_reading'] or '?'
                sfx_g = r['sfx_gloss'] or '-'

                output_lines.append(
                    f"    {word_s:20s} | "
                    f"PFX:{pfx_s:6s} | "
                    f"MID:{mid_s:10s} | "
                    f"SFX:{sfx_s:6s} | "
                    f"CAT:{cat_s:14s} | "
                    f"atoms: {atom_str}"
                )
                output_lines.append(
                    f"    {'':20s}   "
                    f"pfx: {pfx_g:30s} | "
                    f"mid: {mid_r:15s} | "
                    f"sfx: {sfx_g}"
                    f"{pos_str}"
                )

            # Line interpretation
            interp = build_line_interpretation(readings, decoder, line_toks)
            output_lines.append(f"")
            output_lines.append(f"    >> READING: {interp}")
            output_lines.append("")

        # Paragraph-level interpretation
        para_cats = defaultdict(int)
        para_kernels = []
        for _, line_toks in para:
            for tok in line_toks:
                m = morph.extract(tok.word)
                if m.middle:
                    cat = cc.classify(m.middle)
                    para_cats[cat] += 1
                    for c in m.middle:
                        if c in ('k', 'h', 'e'):
                            para_kernels.append(c)

        k_count = para_kernels.count('k')
        h_count = para_kernels.count('h')
        e_count = para_kernels.count('e')
        total_k = k_count + h_count + e_count

        output_lines.append(f"  PARAGRAPH SUMMARY:")
        output_lines.append(f"    Kernel profile: k={k_count}({k_count/total_k:.0%}) h={h_count}({h_count/total_k:.0%}) e={e_count}({e_count/total_k:.0%})" if total_k else "    Kernel profile: none")
        output_lines.append(f"    Category breakdown: {dict(para_cats)}")

        # Interpretive paragraph gloss
        top_cat = max(para_cats, key=para_cats.get) if para_cats else '?'

        # Build paragraph interpretation based on kernel and category
        if e_count > k_count and e_count > h_count:
            thermal_read = "cooling/settling emphasis"
        elif k_count > e_count:
            thermal_read = "active heating emphasis"
        else:
            thermal_read = "balanced heat/cool"

        cat_reads = {
            'THERMAL': 'temperature management',
            'FLOW': 'material flow control',
            'CONTAINMENT': 'vessel/seal management',
            'STAGING': 'arrangement/setup',
            'OPERATION': 'active processing',
            'TRANSITION': 'state change operations',
            'MARKING': 'labeling/identification',
            'MONITORING': 'observation/checking',
        }

        cat_summary = ', '.join([cat_reads.get(c, c) for c in (p_cat if isinstance(p_cat, list) else [p_cat])[:3]])

        output_lines.append(f"    INTERPRETATION: {thermal_read} | focus on {cat_summary}")
        output_lines.append("")

    # Final folio-level interpretation
    output_lines.append("=" * 100)
    output_lines.append("FOLIO-LEVEL INTERPRETATION")
    output_lines.append("=" * 100)
    output_lines.append("")
    output_lines.append(fa.program_card())
    output_lines.append("")

    # Write output
    output_path = Path(__file__).resolve().parent.parent / 'results' / 'f103r_reading.txt'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))

    print(f"\nOutput written to: {output_path}")
    print(f"Total lines of output: {len(output_lines)}")

    # Also print to stdout
    print('\n'.join(output_lines))


if __name__ == '__main__':
    main()
