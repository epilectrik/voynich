from vee.app.ui.folio_viewer import EVA_TO_FONT_MAP
print('Loaded mapping with', len(EVA_TO_FONT_MAP), 'entries')
print('Sample mappings:')
for k in list(EVA_TO_FONT_MAP.keys())[:10]:
    print(f'  {repr(k)} -> {repr(EVA_TO_FONT_MAP[k])}')

