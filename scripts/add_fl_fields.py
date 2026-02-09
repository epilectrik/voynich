#!/usr/bin/env python3
"""
Migration script to add FL state fields to token_dictionary.json.

Adds:
- fl_state: INITIAL/EARLY/MEDIAL/LATE/TERMINAL (or null)
- fl_meaning: Semantic description of the state
- is_fl_role: True if token is actual FL-role (pure FL vocabulary, no kernel/helper chars)

Based on:
- C770-C772: FL primitive character set
- C777: FL state index
- BCSC: FL role = classes {7, 30, 38, 40}, 4.7% of B
"""

import json
import sys
sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Morphology

# FL primitive character set (C770, C772)
FL_CHARS = set('adilmnory')
KERNEL_CHARS = set('khe')
HELPER_CHARS = set('cst')

# CC (Core Control) tokens - these use FL chars but are NOT FL-role
# They serve a distinct control function (C788, C874)
CC_TOKENS = {'daiin', 'ol', 'or', 'ar'}

# FL state map (from BFolioDecoder.FL_STAGE_MAP)
# Meanings should be clear but preserve distinctions
FL_STAGE_MAP = {
    # INITIAL: Material entering
    'ii': ('INITIAL', 'raw input'),      # Unprocessed material
    'i': ('INITIAL', 'input'),           # Material entering
    'an': ('INITIAL', 'adding'),         # Active addition
    'a': ('INITIAL', 'begin'),

    # EARLY: Material received
    'in': ('EARLY', 'loaded'),

    # MEDIAL: Transformation in progress
    'r': ('MEDIAL', 'reacting'),
    'ar': ('MEDIAL', 'needs adjust'),    # Signal: adjustment needed
    'al': ('MEDIAL', 'adjusting'),       # Action: making adjustment
    'l': ('MEDIAL', 'separating'),
    'ol': ('MEDIAL', 'processing'),
    's': ('MEDIAL', 'next'),
    'aiin': ('MEDIAL', 'still separating'),  # Continuation
    'ain': ('MEDIAL', 'separating'),
    'or': ('MEDIAL', 'continue'),
    'yl': ('MEDIAL', 'pouring'),
    'd': ('MEDIAL', 'during'),
    't': ('MEDIAL', 'transfer'),

    # LATE: Approaching completion
    'o': ('LATE', 'nearly done'),
    'ly': ('LATE', 'settling out'),
    'oiin': ('LATE', 'settling'),

    # TERMINAL: Step complete (differentiated by suffix semantics)
    # -Vm (am/om/im/m) = line-final completion (C375: 82% line-final)
    # -y = basic terminal (step done)
    # -dy = herb/gentle terminal with yield (C527)
    # -ry = process complete terminal
    'am': ('TERMINAL', 'complete'),
    'om': ('TERMINAL', 'complete'),
    'm': ('TERMINAL', 'complete'),
    'im': ('TERMINAL', 'complete'),
    'y': ('TERMINAL', 'done'),
    'dy': ('TERMINAL', 'yielded'),
    'ry': ('TERMINAL', 'finished'),
}

def is_pure_fl_vocabulary(word: str) -> bool:
    """
    Check if token uses ONLY FL vocabulary characters AND is not CC.

    FL-role tokens (classes 7, 30, 38, 40) are characterized by:
    - Using ONLY FL characters {a,d,i,l,m,n,o,r,y}
    - NO kernel chars (k,h,e)
    - NO helper chars (c,s,t)
    - NO other chars (q, p, f, etc.)
    - NOT a CC token (daiin, ol, or, ar serve control function)
    """
    # Exclude CC tokens - they use FL chars but are Core Control, not Flow
    if word in CC_TOKENS:
        return False

    chars = set(word)
    # Token must use ONLY FL characters - nothing else
    return chars <= FL_CHARS

def get_fl_state(word: str, middle: str) -> tuple:
    """
    Get FL state for a token.

    Returns (fl_state, fl_meaning) or (None, None)
    """
    # Check MIDDLE first (most specific)
    if middle and middle in FL_STAGE_MAP:
        return FL_STAGE_MAP[middle]

    # Check whole word for standalone tokens
    if word in FL_STAGE_MAP:
        return FL_STAGE_MAP[word]

    # Check suffix patterns (for absorbed suffixes)
    if middle:
        # Check longest matches first
        for pattern in sorted(FL_STAGE_MAP.keys(), key=len, reverse=True):
            if middle.endswith(pattern) and len(pattern) >= 1:
                return FL_STAGE_MAP[pattern]

    return None, None

def main():
    # Load token dictionary
    with open('data/token_dictionary.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    morph = Morphology()

    # Stats tracking
    stats = {
        'total': 0,
        'fl_state_assigned': 0,
        'is_fl_role_true': 0,
        'state_counts': {}
    }

    # Process each token
    for token, entry in data['tokens'].items():
        stats['total'] += 1

        # Get morphology
        m = morph.extract(token)
        middle = m.middle if m.middle else token

        # Get FL state
        fl_state, fl_meaning = get_fl_state(token, middle)

        # Check if FL-role token (pure FL vocabulary)
        is_fl_role = is_pure_fl_vocabulary(token)

        # Add fields
        entry['fl_state'] = fl_state
        entry['fl_meaning'] = fl_meaning
        entry['is_fl_role'] = is_fl_role

        # Track stats
        if fl_state:
            stats['fl_state_assigned'] += 1
            stats['state_counts'][fl_state] = stats['state_counts'].get(fl_state, 0) + 1
        if is_fl_role:
            stats['is_fl_role_true'] += 1

    # Update metadata
    data['meta']['version'] = '6.0'
    data['meta']['schema_notes'] += ' v6: Added fl_state, fl_meaning, is_fl_role fields (C770-C777).'

    # Save
    with open('data/token_dictionary.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # Report
    print("FL Fields Migration Complete")
    print("=" * 50)
    print(f"Total tokens processed: {stats['total']}")
    print(f"Tokens with FL state:   {stats['fl_state_assigned']} ({100*stats['fl_state_assigned']/stats['total']:.1f}%)")
    print(f"Tokens with FL role:    {stats['is_fl_role_true']} ({100*stats['is_fl_role_true']/stats['total']:.1f}%)")
    print()
    print("FL State Distribution:")
    for state, count in sorted(stats['state_counts'].items()):
        print(f"  {state:12}: {count:5} tokens")

if __name__ == '__main__':
    main()
