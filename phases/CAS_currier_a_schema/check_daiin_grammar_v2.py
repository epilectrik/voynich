"""Check what grammar class daiin belongs to in Currier B."""
import json
from pathlib import Path

project_root = Path(__file__).parent.parent.parent

# Load the canonical grammar
grammar_path = project_root / 'results' / 'canonical_grammar.json'
with open(grammar_path) as f:
    grammar = json.load(f)

print("=" * 70)
print("DAIIN IN CURRIER B GRAMMAR")
print("=" * 70)

# Check terminals
print("\nSearching terminals...")
terminals = grammar.get('terminals', {})
print(f"Terminals count: {terminals.get('count', 0)}")

terminal_list = terminals.get('list', [])
daiin_terminal = None
for t in terminal_list:
    if t.get('symbol') == 'daiin':
        daiin_terminal = t
        print(f"\nFOUND daiin in terminals:")
        print(f"  ID: {t.get('id')}")
        print(f"  Role: {t.get('role')}")
        break

if not daiin_terminal:
    print("\ndaiin NOT in terminal list")
    # Search for daiin-like
    daiin_like = [t for t in terminal_list if 'daiin' in t.get('symbol', '')]
    if daiin_like:
        print(f"Found {len(daiin_like)} daiin-related terminals:")
        for t in daiin_like:
            print(f"  {t.get('symbol')}: {t.get('role')}")

# Check non-terminals
print("\n" + "-" * 70)
print("Searching non-terminals...")
non_terminals = grammar.get('non_terminals', {})
print(f"Non-terminals count: {non_terminals.get('count', 0)}")

nt_list = non_terminals.get('list', [])
for nt in nt_list:
    members = nt.get('members', [])
    if 'daiin' in members:
        print(f"\nFOUND daiin in non-terminal:")
        print(f"  ID: {nt.get('id')}")
        print(f"  Name: {nt.get('name')}")
        print(f"  Class size: {len(members)}")
        print(f"  First 20 members: {members[:20]}")
        break
else:
    print("\ndaiin NOT found in non-terminal members")
    # Search all non-terminals for daiin-related
    for nt in nt_list:
        members = nt.get('members', [])
        if any('daiin' in m for m in members):
            print(f"\nNon-terminal {nt.get('id')} ({nt.get('name')}) has daiin-related:")
            daiin_members = [m for m in members if 'daiin' in m]
            print(f"  {daiin_members[:10]}")

# Show all roles
print("\n" + "=" * 70)
print("ALL TERMINAL ROLES")
print("=" * 70)
roles = {}
for t in terminal_list:
    role = t.get('role', 'UNKNOWN')
    if role not in roles:
        roles[role] = []
    roles[role].append(t.get('symbol'))

for role, symbols in sorted(roles.items()):
    print(f"\n{role} ({len(symbols)} tokens):")
    for s in symbols[:10]:
        print(f"  {s}")
    if len(symbols) > 10:
        print(f"  ... and {len(symbols)-10} more")

# Show all non-terminal names
print("\n" + "=" * 70)
print("ALL NON-TERMINAL CLASSES")
print("=" * 70)
for nt in nt_list:
    print(f"  {nt.get('id')}: {nt.get('name')} ({len(nt.get('members', []))} members)")

# Check productions for daiin patterns
print("\n" + "=" * 70)
print("DAIIN IN PRODUCTIONS")
print("=" * 70)
productions = grammar.get('productions', {})
prod_list = productions.get('list', [])
daiin_prods = [p for p in prod_list if 'daiin' in str(p)]
print(f"Productions mentioning daiin: {len(daiin_prods)}")
for p in daiin_prods[:5]:
    print(f"  {p}")
