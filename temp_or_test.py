"""Test the 'or' token parsing."""
from apps.script_explorer.parsing.currier_a import parse_currier_a_token

# Test "or" token
result = parse_currier_a_token('or')
print(f'Token: or')
print(f'Prefix: {result.prefix}')
print(f'Middle: {result.middle}')
print(f'Suffix: {result.suffix}')
print(f'Status: {result.a_status}')
print(f'Reason: {result.reason}')
print()

# Also test other minimal tokens
for token in ['ol', 'ar', 'al', 'or', 'ok', 'ot', 'op']:
    r = parse_currier_a_token(token)
    print(f'{token}: prefix={r.prefix}, middle={r.middle}, suffix={r.suffix}, status={r.a_status.name}')
