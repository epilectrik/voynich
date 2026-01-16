"""Debug token matching issue."""
from apps.azc_folio_animator.core.folio_loader import FolioLoader
from apps.azc_folio_animator.core.azc_folio_model import AZCFolioRegistry
from apps.script_explorer.parsing.currier_a import parse_currier_a_token

loader = FolioLoader()
loader.load()

folio = loader.get_folio('1r')
if folio and len(folio.lines) >= 4:
    line = folio.lines[3]  # 0-indexed, so line 4 = index 3
    if len(line) >= 2:
        token = line[1]  # Position 2 = index 1
        print(f'Token at f1r line 4 pos 2: "{token.text}"')
        result = parse_currier_a_token(token.text)
        print(f'Parsed: prefix={result.prefix}, middle={result.middle}, suffix={result.suffix}')
        print()

        # Now check what folios are activated
        registry = AZCFolioRegistry(loader)

        activated = registry.get_activated_folios(token.text)
        print(f'Activated folios (by exact token): {len(activated)}')
        for af in activated:
            print(f'  {af.folio_id}')
            # Check what tokens in this folio match by MIDDLE
            matching = af.get_tokens_by_middle(token.text)
            print(f'    Tokens by MIDDLE "{result.middle}": {matching}')
            # Check exact positions
            exact = af.get_positions(token.text)
            print(f'    Exact token positions: {len(exact)}')
