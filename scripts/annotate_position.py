#!/usr/bin/env python3
"""Add a single annotation note."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from voynich import TokenDictionary

if len(sys.argv) < 3:
    print("Usage: python annotate_position.py <token> <note>")
    sys.exit(1)

token = sys.argv[1]
note = ' '.join(sys.argv[2:])

td = TokenDictionary()
entry = td.get(token)
if entry:
    td.add_note(token, note)
    td.save()
    print(f"Added: {token}")
else:
    print(f"NOT FOUND: {token}")
