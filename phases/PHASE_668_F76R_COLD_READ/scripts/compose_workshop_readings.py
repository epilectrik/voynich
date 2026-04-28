"""
Compose workshop readings for all tokens on a folio using v2 B Dictionary + compositional rules.
Outputs markdown tables ready for cold read insertion.
"""
import json, sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, '.')
from scripts.voynich import Transcript, Morphology

morph = Morphology()

# Load v2 dictionary
v2 = {}
with open('phases/B_OPERATIONAL_DICTIONARY/results/b_dictionary_top100_v3.md', encoding='utf-8') as f:
    for line in f:
        m = re.match(r'\|\s*\d+\s*\|\s*(\S+)\s*\|\s*\d+\s*\|\s*(D\d)\s*\|\s*(.+?)\s*\|', line)
        if m:
            token, tier, reading = m.group(1), m.group(2), m.group(3).strip()
            v2[token] = (tier, reading)

# Prefix domain labels for workshop composition
PREFIX_WORKSHOP = {
    'qo': 'Fire',
    'ch': 'Test',
    'sh': 'Watch',
    'ok': 'Vessel',
    'ot': 'Output',
    'ol': 'Steady',
    'da': 'Load',
    'sa': 'Scaffold',
    'lk': 'Check equipment',
    'ke': 'Balneum',
    'te': 'Transfer step',
    'to': 'Note transfer',
    'do': 'Execute',
    'so': 'Sequence',
    'ar': 'Note the yield',
    'or': 'Note what happened',
    'po': 'Pause',
    'ta': 'Transfer',
    'ka': 'Heat',
    'yk': 'Adjust',
    'sch': 'Quick check',
    'pch': 'Setup',
    'al': 'Product settled',
    'fch': 'Mercury marker (C1939)',
    'dch': 'Setup-check',
    'lsh': 'Watch equipment',
    'lch': 'Check equipment',
    'rch': 'Respond-check',
    'tch': 'Transfer-check',
    'ko': 'Heat',
    'kch': 'Heat-check',
}

ATOM_WORKSHOP = {
    'k': 'heat', 'e': 'steady', 'h': 'watch', 'y': '',
    'i': 'iterate', 'n': 'bind', 'a': 'bring to', 'm': 'finalize',
    'd': 'do', 't': 'transfer', 'l': 'hold', 'o': 'set up',
    'c': 'adjust', 'r': 'respond', 'f': 'flag', 'p': 'pause',
    's': 'sequence',
}

def compose_workshop(token, atomized):
    """Compose a workshop reading from prefix + atoms."""
    prefix = atomized.prefix or ''
    atoms = atomized.atoms

    if not atoms:
        return '*unrecognized*', '---'

    pfx_label = PREFIX_WORKSHOP.get(prefix, '')
    if not pfx_label and not prefix:
        # No prefix at all
        if len(token) <= 3:
            # Short bare token — give atom reading
            parts = [ATOM_WORKSHOP.get(a[0], a[0]) for a in atoms]
            reading = ', '.join(parts)
            return f'*bare token: {reading}*', '---'
        else:
            atom_parts = '.'.join(a[0] for a in atoms)
            parts = [ATOM_WORKSHOP.get(a[0], a[0]) for a in atoms]
            return f'*unrecognized* ({", ".join(parts)})', '---'

    # Build body description from atoms
    body_parts = []
    e_count = sum(1 for a in atoms if a[0] == 'e')
    i_count = sum(1 for a in atoms if a[0] == 'i')
    has_h = any(a[0] == 'h' for a in atoms)
    has_k = any(a[0] == 'k' for a in atoms)
    has_ckh = False
    has_cth = False
    has_ecth = False

    # Check for observation MIDDLEs
    atom_str = ''.join(a[0] for a in atoms)
    if 'ckh' in atom_str:
        has_ckh = True
    if 'cth' in atom_str and 'ecth' not in atom_str:
        has_cth = True
    if 'ecth' in atom_str:
        has_ecth = True

    # Compose based on key patterns
    if has_ckh:
        body = 'temperature check'
        if has_h and atom_str.count('h') > 1:
            body += ' with extended observation'
        if e_count >= 2:
            body += ' (gentle level)'
    elif has_ecth:
        body = 'cooled-transfer-watch'
    elif has_cth:
        body = 'observe material moving'
        if 'hh' in atom_str:
            body = 'extended transfer-watch — prolonged observation'
    elif has_k and e_count >= 2 and 'd' in atom_str:
        body = 'one gentle balneum cycle'
    elif has_k and e_count >= 2:
        body = 'gentle steady heat — balneum level'
    elif has_k and e_count == 1 and 'd' in atom_str:
        body = 'one standard heat cycle'
    elif has_k and 'a' in atom_str and i_count >= 2:
        body = 'sustained deep heating cycles'
    elif has_k and 'a' in atom_str and 'i' in atom_str:
        body = 'heat through one cycle'
    elif has_k and 'a' in atom_str and 'l' in atom_str:
        body = 'heat until stable'
    elif has_k and 'a' in atom_str and 'r' in atom_str:
        body = 'heat and note response'
    elif has_k and 'o' in atom_str and 'l' in atom_str:
        body = 'heat and hold'
    elif has_k and 'c' in atom_str and has_h:
        body = 'heat with active monitoring'
    elif has_k and 'y' in atom_str and len(atoms) <= 3:
        body = 'set — stop adjusting'
    elif 't' in atom_str and e_count >= 2:
        body = 'gentle steady transfer'
    elif 't' in atom_str and 'a' in atom_str and i_count >= 2:
        body = 'sustained transfer cycles'
    elif 't' in atom_str and 'a' in atom_str and 'r' in atom_str:
        body = 'transfer and note result'
    elif 't' in atom_str and 'e' in atom_str and 'd' in atom_str:
        body = 'transfer, system steady'
    elif 't' in atom_str and 'o' in atom_str:
        body = 'transfer and hold'
    elif 'e' in atom_str and 'd' in atom_str and 'y' in atom_str and len(atoms) <= 4:
        body = 'system steady, confirmed'
    elif 'a' in atom_str and i_count >= 2 and 'n' in atom_str:
        body = 'extended iteration cycles'
    elif 'a' in atom_str and 'i' in atom_str and 'n' in atom_str:
        body = 'one processing cycle'
    elif 'a' in atom_str and 'r' in atom_str:
        body = 'bring to and note result'
    elif 'a' in atom_str and 'l' in atom_str:
        body = 'bring to stable state'
    elif 'o' in atom_str and 'l' in atom_str and 'y' in atom_str:
        body = 'holding, confirmed'
    elif 'o' in atom_str and 'l' in atom_str:
        body = 'hold current state'
    elif 'o' in atom_str and 'r' in atom_str:
        body = 'note what happened'
    elif 'l' in atom_str and len(atoms) == 1:
        body = 'hold'
    elif 'r' in atom_str and len(atoms) == 1:
        body = 'respond'
    elif 'y' in atom_str and len(atoms) == 1:
        body = 'complete'
    elif 'd' in atom_str and 'y' in atom_str and len(atoms) == 2:
        body = 'cycle close'
    elif 's' in atom_str and 'h' in atom_str and 'e' in atom_str:
        body = 'watch sequence steady'
    elif 's' in atom_str and 'e' in atom_str:
        body = 'sequence steady'
    else:
        parts = [ATOM_WORKSHOP.get(a[0], a[0]) for a in atoms if ATOM_WORKSHOP.get(a[0])]
        body = ', '.join(p for p in parts if p)

    if pfx_label:
        reading = f'{pfx_label}: {body}'
    else:
        reading = body

    return reading, 'Comp-v2'


def get_reading(token_word):
    """Get workshop reading for a token: v2 dict first, then compose."""
    # Check v2 dictionary
    if token_word in v2:
        tier, reading = v2[token_word]
        return reading, f'B Dict {tier}'

    # Atomize and compose
    a = morph.atomize(token_word)
    if not a or not a.atoms:
        return f'*unrecognized*', '---'

    reading, source = compose_workshop(token_word, a)
    return reading, source


# Parse the raw decode file
import sys
folio = sys.argv[1] if len(sys.argv) > 1 else 'f84r'
txt_path = f'phases/PHASE_668_F76R_COLD_READ/results/data/{folio}_cold_read.txt'

current_para = None
current_line = None
tokens_by_line = {}  # (para, line) -> [(token, prefix_tag, reading, source)]

with open(txt_path, encoding='utf-8') as f:
    for raw_line in f:
        raw_line = raw_line.rstrip()
        m = re.match(r'^PARAGRAPH (\d+)', raw_line)
        if m:
            current_para = int(m.group(1))
            continue
        m = re.match(r'^\s+--- Line (\d+) ---', raw_line)
        if m:
            current_line = int(m.group(1))
            tokens_by_line[(current_para, current_line)] = []
            continue
        m = re.match(r'^\s+(\S+)\s+\[([^\]]*)\]\s+(\S+)\s+(.*)', raw_line)
        if m and current_para and current_line:
            word = m.group(1)
            prefix_tag = m.group(2).strip()
            atom_codes = m.group(3)
            atom_glosses = m.group(4)

            reading, source = get_reading(word)

            # Check for observation MIDDLE annotations
            obs = ''
            if '<< heat-level-check' in raw_line:
                obs = ' **«ckh»**'
            elif '<< cooled-transfer-watch' in raw_line:
                obs = ' **«ecth»**'
            elif '<< transfer-watch' in raw_line:
                if 'extended' in raw_line:
                    obs = ' **«cthh»**'
                else:
                    obs = ' **«cth»**'
            elif '<< hh-EXTENDED' in raw_line:
                obs = ' **«hh»**'

            # Use clean prefix code instead of decode label
            a = morph.atomize(word)
            clean_pfx = (a.prefix if a and a.prefix else '---')

            tokens_by_line[(current_para, current_line)].append(
                (word, clean_pfx, reading + obs, source)
            )

# Output markdown tables
for key in sorted(tokens_by_line.keys()):
    para, line_num = key
    tokens = tokens_by_line[key]
    if not tokens:
        continue

    n = len(tokens)

    # Count recognized
    recognized = sum(1 for t in tokens if t[3] != '---')

    print(f'**L{line_num} ({n} tokens)**')
    print('| Token | Prefix | Reading | Source |')
    print('|-------|--------|---------|--------|')
    for word, pfx, reading, source in tokens:
        pfx_display = pfx if pfx and pfx != '?' else '---'
        print(f'| {word} | {pfx_display} | {reading} | {source} |')
    print()
    print(f'→ {recognized}/{n} recognized ({100*recognized//n}%).')
    print()
