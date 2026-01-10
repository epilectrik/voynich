#!/usr/bin/env python3
"""
Constraint Reference Validator

Validates that constraint references (C###) in text refer to real constraints.
Can be used standalone or as a Claude Code hook.

Usage:
    Standalone: python validate_constraint_reference.py "Check C074 and C999"
    As hook: Reads JSON from stdin with 'user_input' field
"""

import re
import sys
import json
from pathlib import Path

# Project root - adjust if script moves
PROJECT_ROOT = Path(__file__).parent.parent.parent
CLAIMS_INDEX = PROJECT_ROOT / "context" / "CLAIMS" / "INDEX.md"

def extract_valid_constraints():
    """Extract all valid constraint numbers from CLAIMS/INDEX.md"""
    constraints = set()

    if not CLAIMS_INDEX.exists():
        # Fallback: known range
        return set(range(74, 412))

    with open(CLAIMS_INDEX, 'r', encoding='utf-8') as f:
        for line in f:
            # Match patterns like "C074", "C121", etc.
            matches = re.findall(r'\bC(\d{3,4})\b', line)
            for m in matches:
                constraints.add(int(m))

    return constraints

def validate_references(text):
    """
    Check text for constraint references and validate them.

    Returns:
        tuple: (valid_refs, invalid_refs)
    """
    valid_constraints = extract_valid_constraints()

    # Find all constraint references in text
    refs = re.findall(r'\bC(\d{3,4})\b', text, re.IGNORECASE)

    valid_refs = []
    invalid_refs = []

    for ref in refs:
        num = int(ref)
        if num in valid_constraints:
            valid_refs.append(f"C{ref}")
        else:
            invalid_refs.append(f"C{ref}")

    return valid_refs, invalid_refs

def main():
    # Determine input source
    if len(sys.argv) > 1:
        # Command line argument
        text = ' '.join(sys.argv[1:])
    else:
        # Try to read from stdin (hook mode)
        try:
            data = json.load(sys.stdin)
            text = data.get('user_input', '')
        except Exception:
            # Silent exit on parse failure - don't disrupt terminal
            sys.exit(0)

    if not text:
        sys.exit(0)

    valid_refs, invalid_refs = validate_references(text)

    # Only output if there are constraint references to report
    if invalid_refs:
        # Use stderr for warnings so it doesn't inject into context
        print(f"WARNING: Invalid constraint references: {', '.join(invalid_refs)}", file=sys.stderr)
        if valid_refs:
            print(f"Valid constraints referenced: {', '.join(valid_refs)}", file=sys.stderr)

    # Stay silent on success - don't clutter the terminal
    sys.exit(0)

if __name__ == '__main__':
    main()
