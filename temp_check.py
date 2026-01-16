from apps.azc_folio_animator.core.folio_loader import FolioLoader
loader = FolioLoader()
loader.load()
folio = loader.get_folio('1r')
line1 = folio.lines[0]
for i, t in enumerate(line1, 1):
    print(f'{i}. {t.text}')
