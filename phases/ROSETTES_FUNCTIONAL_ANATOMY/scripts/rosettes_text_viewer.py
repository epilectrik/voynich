#!/usr/bin/env python3
"""
Rosettes Text Viewer — render all rosette text in Voynich font.

Shows BOTH transcription sources (Stolfi/U-track and Zandbergen) side by side,
mapped to the 9-rosette grid for visual comparison against manuscript scans.
"""
import sys
import re
import shutil
import base64
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

FONT_PATHS = {
    'EVA2': ROOT / 'vee' / 'app' / 'fonts' / 'EVA2.ttf',
    'VoynichEVA': ROOT / 'vee' / 'app' / 'fonts' / 'VoynichEVA.ttf',
    'VoynichEVAHandA': ROOT / 'vee' / 'app' / 'fonts' / 'VoynichEVAHandA.ttf',
}
OUT_DIR = ROOT / 'phases' / 'ROSETTES_FUNCTIONAL_ANATOMY' / 'results'
OUT_HTML = OUT_DIR / 'rosettes_text_viewer.html'
ZL_PATH = ROOT / 'data' / 'zl_rosettes.txt'

ROSETTE_ORDER = ['NW', 'NORTH', 'NE', 'WEST', 'CENTER', 'EAST', 'SW', 'SOUTH', 'SE']
ROSETTE_GRID = {
    'NW': (0, 0), 'NORTH': (0, 1), 'NE': (0, 2),
    'WEST': (1, 0), 'CENTER': (1, 1), 'EAST': (1, 2),
    'SW': (2, 0), 'SOUTH': (2, 1), 'SE': (2, 2),
}

# ── Zandbergen position-number to rosette mapping ──────────────────────────
# Position <!X:Y> where X = area number
# Mapped by analyzing sequential context and physical layout
ZL_AREA_TO_ROSETTE = {
    '1': 'NW',      # NW margin + interior labels
    '2': 'WEST',    # WEST labels (M1 equivalent) + NW connection labels
    '3': 'SW',      # SW labels (B1 equivalent)
    '4': 'NORTH',   # NORTH labels (U2 equivalent)
    '5': 'CENTER',  # CENTER labels (M2 equivalent)
    '6': 'SOUTH',   # SOUTH labels (B2 equivalent)
    '7': 'NE',      # NE labels (U3 equivalent)
    '8': 'EAST',    # EAST labels (M3 equivalent)
    '9': 'SE',      # SE labels (B3 equivalent)
}

# Ring text mapping by sequential position in the file
# (ring texts sit between label groups, mapping to the rosette they surround)
ZL_RING_MAP = {
    2: 'NW',       # fRos.2 = V1 (NW ring), between W1 margin and U1 labels
    20: 'NORTH',   # fRos.20 = V2 (NORTH ring), between U1/NORTH labels
    35: 'NE',      # fRos.35 = V3 (NE ring!), between NE labels groups
    36: 'NE',      # fRos.36 = Spiral text near NE
    47: 'WEST',    # fRos.47 = N1 (WEST ring), between NE and WEST labels
    62: 'CENTER',  # fRos.62 = N2 (CENTER ring), between WEST/SW-road and CENTER labels
    87: 'EAST',    # fRos.87 = N3 (EAST ring!), between CENTER labels (5:24) and EAST labels (8:1)
    94: 'SW',      # fRos.94 = C1 (SW ring), between SE labels (9:2) and SW labels (3:5)
    122: 'SOUTH',  # fRos.122 = C2 (SOUTH ring), between SW road labels and SOUTH labels
    133: 'SE',     # fRos.133 = C3 (SE ring!), between SOUTH labels (6:12) and SE labels (9:6)
}

# Clock/special text near SW rosette
ZL_SPECIAL_MAP = {
    112: 'SW',  # left of clock
    113: 'SW',  # above clock (ring)
    114: 'SW',  # below clock (ring)
    115: 'SW',  # right of clock
}


def parse_zl(filepath):
    """Parse Zandbergen IVTFF rosettes data."""
    rosettes = defaultdict(list)  # {rosette: [entries]}

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if not line or line.startswith('<fRos>'):
            continue

        # Parse: <fRos.NUM,TYPE>  [<!POS>]text
        m = re.match(r'^<fRos\.(\d+),([^>]+)>\s+(.*)', line)
        if not m:
            continue

        locus_num = int(m.group(1))
        locus_type = m.group(2).strip()
        rest = m.group(3).strip()

        # Extract position comment if present
        position = ''
        text = rest
        pos_m = re.match(r'<!([^>]+)>(.*)', rest)
        if pos_m:
            position = pos_m.group(1)
            text = pos_m.group(2).strip()
            # Handle double position comments like <!above clock><!08:00>
            pos_m2 = re.match(r'<!([^>]+)>(.*)', text)
            if pos_m2:
                position += ' ' + pos_m2.group(1)
                text = pos_m2.group(2).strip()

        # Determine text type
        if '@Cc' in locus_type or '=Cc' in locus_type:
            text_type = 'ring'
        elif 'Ca' in locus_type:
            text_type = 'ring'
        elif 'Pb' in locus_type:
            text_type = 'paragraph'
        else:
            text_type = 'label'

        # Clean text: remove IVTFF markup
        clean = text
        clean = re.sub(r'<[^>]*>', '', clean)   # remove tags like <-> <$> <%>
        clean = re.sub(r'\{[^}]*\}', '', clean)  # remove {annotations}
        clean = re.sub(r'@\d+;', '', clean)       # remove @NNN; references
        clean = re.sub(r'\[[^\]]*:([^\]]*)\]', r'\1', clean)  # [a:b] → b (preferred reading)
        clean = clean.strip("='\" ")

        # Split into words
        words = re.split(r'[.,\s]+', clean)
        words = [w.strip() for w in words if w.strip()]

        # Map to rosette
        rosette = None
        if locus_num in ZL_RING_MAP:
            rosette = ZL_RING_MAP[locus_num]
        elif locus_num in ZL_SPECIAL_MAP:
            rosette = ZL_SPECIAL_MAP[locus_num]
        elif locus_num >= 137:
            rosette = 'OUTSIDE'  # outside face paragraphs
        elif position:
            # Extract area number from X:Y position
            area_m = re.match(r'(\d+):', position)
            if area_m:
                area = area_m.group(1)
                rosette = ZL_AREA_TO_ROSETTE.get(area, 'UNKNOWN')
            elif position.startswith(('I', 'V', 'X')):
                rosette = 'OUTSIDE'  # Roman numerals = outside face
            elif 'clock' in position or 'spiral' in position.lower():
                rosette = 'SW'

        if not rosette:
            rosette = 'UNKNOWN'

        entry = {
            'locus': locus_num,
            'type': text_type,
            'locus_type': locus_type,
            'position': position,
            'raw': text,
            'words': words,
        }
        rosettes[rosette].append(entry)

    return rosettes


def parse_stolfi():
    """Parse original Stolfi source (embedded)."""
    # Minimal re-parse using the same source as before
    RAW = r"""## <f85v2.W1> {}
<f85v2.W1.1;U>     ***in.**r-
<f85v2.W1.2;U>     ***dair-
<f85v2.W1.3;U>     ***kam-
<f85v2.W1.4;U>     ***rchedy=
<f85v2.W1.5;U>     ***dy.ry-
<f85v2.W1.6;U>     *chshy.o***-
<f85v2.W1.7;U>     *chor.orary-
<f85v2.W1.8;U>     *sair.ogam=
## <f85v2.V1> {}
<f85v2.V1.1;U>     oto.tos,ain.odar.otar.otar.okaiin.dar,ol,chdar.otdar.sh*chs.okos.ol.om.olkeeodaar.shol.okal.orshear.*aii*.okalol.otodr.oar.ar,ol.oqotam-{gap}oteal.cthedy.oked*.*shaiin.or,aiin.okar.okeedy=
## <f85v2.U1> {}
<f85v2.U1.1;V>     okchdarar=
<f85v2.U1.21;V>    daldar=
<f85v2.U1.22;V>    saiindy=
<f85v2.U1.23;V>    ddsschx=
<f85v2.U1.24;V>    opardy=
<f85v2.U1.25;V>    yt*dar=
<f85v2.U1.31;V>    orarol=
<f85v2.U1.41;V>    daraldy=
<f85v2.U1.42;U>    daldal=
## <f85v2.V2> {}
<f85v2.V2.1;U>     cthshr.otedy.chedaiir.cheekedy.ala*.olka*.oko.k***.okche*.otol.ary-{tower}***,aiir.oral.r.keeai*.***-{tower}okain.olkaiin.ody.{object}rair.ol.r,ar.{begin waterfall}or.okal.o**l.{end waterfall}s.al.al.okal.**.air.ol.ar.ol.al.**.okan.okod.okor.okeo.**y-{bridgehead}
## <f85v2.U2> {}
<f85v2.U2.1;V>     okory=
<f85v2.U2.2;V>     dxar=
<f85v2.U2.3;V>     adairy=
<f85v2.U2.4;V>     opar=
<f85v2.U2.5;V>     ofain=
<f85v2.U2.6;V>     ofary=
<f85v2.U2.7;V>     ofedy=
<f85v2.U2.8;V>     docfhhy=
<f85v2.U2.9;V>     daiiny=
<f85v2.U2.10;V>    oko=
## <f85v2.V3> {}
# Not transcribed yet
## <f85v2.U3> {}
<f85v2.U3.1;V>     opeol.daly=
<f85v2.U3.2;V>     okar=
<f85v2.U3.3;V>     cfhhy=
<f85v2.U3.4;V>     okar.oedody=
<f85v2.U3.21;V>    ot.edy.oto**=
<f85v2.U3.22;V>    opshedaiin=
<f85v2.U3.23;V>    sareecphdy=
<f85v2.U3.31;V>    ydashgarain=
<f85v2.U3.41;V>    opokchor.ody=
<f85v2.U3.42;V>    okody=
<f85v2.U3.43;V>    opair.ofalcfhy=
## <f85v2.N1> {}
<f85v2.N1.1;U>     oran.otar.oto,deedyoty,daiin.**eor.*ar.oked*.qotedy.otchy.otoraiin.chekad*{fold}r.or.aiin.okedal.olor.opaiir,al.cheolky.ytar.qokeol.tshed.ores.oteedaiin.odal.ch*y.otchdar.or,olkoai*.{fold}**olaiin=
## <f85v2.M1> {}
<f85v2.M1.1;V>     otedal=
<f85v2.M1.2;V>     opaiiino=
<f85v2.M1.3;V>     otchdy=
<f85v2.M1.4;V>     okchy=
<f85v2.M1.5;V>     chkeedy=
<f85v2.M1.6;V>     chpair.ain=
<f85v2.M1.7;V>     odady=
<f85v2.M1.8;V>     okody=
## <f85v2.N2> {}
<f85v2.N2.1;U>     okar.or.o*.oraiin.okeady.okch*.odsheedy.odaiin.okchdy.{fold}okar.shar.okaiin.daiin.ofair.oly.olkais,od,al.olkalo.olor.***.**.o*.sh*a.*.k.r,ol,ar.oteedaii*.otar.a*r.*,qor.aiin.ol.qota*{fold}.ol.o.r.or.or*a.okeeed*.okal.okodain.okech.okady.okedy.chdar.o.**-{gap}
## <f85v2.M2> {}
<f85v2.M2.1;V>     daral=
<f85v2.M2.2;V>     opar=
<f85v2.M2.3;V>     opchees=
<f85v2.M2.4;V>     chdy=
<f85v2.M2.5;V>     odal=
<f85v2.M2.6;V>     opy=
<f85v2.M2.7;V>     oteedy=
<f85v2.M2.11;V>    ols=
<f85v2.M2.12;V>    ypal=
<f85v2.M2.13;V>    opydch=
<f85v2.M2.14;V>    sshy=
<f85v2.M2.15;V>    ddl=
<f85v2.M2.16;V>    dtedg=
<f85v2.M2.17;V>    opey=
<f85v2.M2.18;V>    opdam=
<f85v2.M2.19;V>    ddary=
<f85v2.M2.20;V>    ot.my=
<f85v2.M2.21;V>    daindy=
<f85v2.M2.22;V>    dody=
<f85v2.M2.51;U>    otdo*aidy-
<f85v2.M2.52;U>    soshxar.arar-
<f85v2.M2.53;U>    otedaiin.otedy-
<f85v2.M2.54;U>    otedar.d*=
<f85v2.M2.55;U>    opch**aiin=
## <f85v2.N3> {}
# Not transcribed yet
## <f85v2.M3> {}
<f85v2.M3.1;V>     okchdy.kary.*drain**=
## <f85v2.C1> {}
<f85v2.C1.1;U>     oka*-{gap}okedal.orain.otody.toar.chcpar.olarckhy.opchdar.or.ar.al.xar.opar.olchedy.okalm.or.apolairi,dy-{figure}otchdair.otodar.otedar.otar,odaiin.olkaiin.otl.xar,ashe.ol.ar.ackhy.shdaiin.ocfheody.shedy-{gap}
## <f85v2.B1> {}
<f85v2.B1.1;V>     opdar.am=
<f85v2.B1.2;V>     ot.dam=
<f85v2.B1.3;V>     !okedshs=
<f85v2.B1.4;V>     otodar=
<f85v2.B1.5;V>     otedaiin=
<f85v2.B1.6;V>     okedy=
<f85v2.B1.7;V>     loltedy=
<f85v2.B1.8;V>     opedam=
<f85v2.B1.9;V>     opchdar=
<f85v2.B1.10;V>    opchdy=
<f85v2.B1.11;V>    oda=
<f85v2.B1.12;V>    okar.amal=
<f85v2.B1.13;U>    otchdy-{ring}chdain-
<f85v2.B1.14;U>    otady-{ring}ote*y=
<f85v2.B1.15;U>    otedy.oparam=
<f85v2.B1.31;V>    cfhedain=
<f85v2.B1.32;V>    otdar.shed=
<f85v2.B1.41;V>    d.dl=
<f85v2.B1.42;V>    otch*=
<f85v2.B1.43;V>    d.dy=
<f85v2.B1.44;V>    osy=
<f85v2.B1.45;V>    oteey=
<f85v2.B1.46;V>    lepcheky=
<f85v2.B1.47;U>    opashcfhedy-{circle}oteeoly=
## <f85v2.D1> {}
<f85v2.D1.1;U>     *ar.odaiin.or-{gap}
<f85v2.D1.2;U>     o.dar.air,*-{gap}
## <f85v2.C2> {}
<f85v2.C2.1;U>     okedar.okody.okair.chedy.opar.al,keody.s,ar,al,keoedy.otedaiin.olky.or.aiin.ody.osain.x*.s.odaiin.okedal.ol.ar.odaiin,alo.sal*an.okeedy.otchdaiin.otedy.okas,aiin.yky.odaiin.okal.okalar=
## <f85v2.B2> {}
<f85v2.B2.1;V>     otedy=
<f85v2.B2.2;U>     otchdam=
<f85v2.B2.3;U>     otosaiin=
<f85v2.B2.4;U>     otchdy=
<f85v2.B2.5;U>     *kedy=
<f85v2.B2.6;U>     okchdy=
<f85v2.B2.7;V>     ok**lar=
<f85v2.B2.8;V>     of!!!!araiin=
<f85v2.B2.9;U>     **=
## <f85v2.C3> {}
# Not transcribed yet
## <f85v2.B3> {}
<f85v2.B3.21;V>    darchdy=
<f85v2.B3.22;V>    opodchdal=
<f85v2.B3.31;V>    anvd*l=
<f85v2.B3.41;V>    lyshalg=
<f85v2.B3.42;U>    okar="""

    # Correct region-to-rosette (with M3 fix)
    R2R = {
        'V1': 'NW', 'V2': 'NORTH', 'V3': 'NE',
        'N1': 'WEST', 'N2': 'CENTER', 'N3': 'EAST',
        'C1': 'SW', 'C2': 'SOUTH', 'C3': 'SE',
        'U1': 'NW', 'U2': 'NORTH', 'U3': 'NE',
        'M1': 'WEST', 'M2': 'CENTER', 'M3': 'EAST',  # FIXED: was SE
        'B1': 'SW', 'B2': 'SOUTH', 'B3': 'SE',
        'D1': 'SW', 'W1': 'NW',
    }

    RING_REGIONS = {'V1', 'V2', 'V3', 'N1', 'N2', 'N3', 'C1', 'C2', 'C3'}

    rosettes = defaultdict(list)
    current_region = None
    not_transcribed = set()

    for line in RAW.strip().split('\n'):
        line = line.strip()
        m = re.match(r'^## <f85v2\.(\w+)>', line)
        if m:
            current_region = m.group(1)
            continue
        if 'Not transcribed yet' in line:
            not_transcribed.add(current_region)
            continue
        if line.startswith('#') or not line:
            continue

        m = re.match(r'^<f85v2\.(\w+)\.([^;]+);(\w)>\s+(.*)', line)
        if not m:
            continue

        region = m.group(1)
        locus = m.group(2)
        track = m.group(3)
        text_raw = m.group(4).strip()

        rosette = R2R.get(region, 'UNKNOWN')
        text_type = 'ring' if region in RING_REGIONS else 'label'

        clean = re.sub(r'\{[^}]*\}', ' ', text_raw)
        clean = clean.rstrip('=-')
        words = re.split(r'[.,\s]+', clean)
        words = [w.strip() for w in words if w.strip()]

        rosettes[rosette].append({
            'region': region,
            'locus': locus,
            'track': track,
            'type': text_type,
            'raw': text_raw,
            'words': words,
        })

    return rosettes, not_transcribed


def generate_html(zl_data, stolfi_data, not_transcribed):
    """Generate dual-source HTML viewer."""

    # Copy fonts
    font_faces = []
    for name, path in FONT_PATHS.items():
        dest = OUT_DIR / path.name
        shutil.copy2(path, dest)
        with open(path, 'rb') as f:
            b64 = base64.b64encode(f.read()).decode('ascii')
        font_faces.append(f"""@font-face {{
    font-family: '{name}';
    src: url('{path.name}') format('truetype'),
         url(data:font/truetype;base64,{b64}) format('truetype');
}}""")
    all_font_faces = '\n'.join(font_faces)

    def render_words(words, css_extra=''):
        parts = []
        for w in words:
            display = w.replace('*', '?').replace('!', '?')
            has_unc = '?' in display
            cls = 'word uncertain' if has_unc else f'word {css_extra}'
            parts.append(
                f'<span class="{cls}" title="{w}">'
                f'<span class="voynich">{display}</span>'
                f'<span class="eva">{w}</span>'
                f'</span>'
            )
        return ' '.join(parts)

    html_parts = []

    for rosette in ROSETTE_ORDER:
        row, col = ROSETTE_GRID[rosette]
        zl_entries = zl_data.get(rosette, [])
        st_entries = stolfi_data.get(rosette, [])

        html_parts.append(f'<div class="rosette" style="grid-row:{row+1};grid-column:{col+1}">')
        html_parts.append(f'<h2>{rosette}</h2>')

        # Zandbergen section
        html_parts.append('<div class="source zl">')
        html_parts.append('<h3>Zandbergen (ZL)</h3>')
        if zl_entries:
            # Group by type
            rings = [e for e in zl_entries if e['type'] == 'ring']
            labels = [e for e in zl_entries if e['type'] == 'label']

            if rings:
                html_parts.append('<div class="text-group"><span class="group-label">Ring text</span>')
                for e in rings:
                    pos = f' [{e["position"]}]' if e.get('position') else ''
                    html_parts.append(f'<div class="entry" title="fRos.{e["locus"]}{pos}">')
                    html_parts.append(render_words(e['words'], 'zl'))
                    html_parts.append('</div>')
                html_parts.append('</div>')

            if labels:
                html_parts.append('<div class="text-group"><span class="group-label">Labels</span>')
                for e in labels:
                    pos = f' [{e["position"]}]' if e.get('position') else ''
                    html_parts.append(f'<div class="entry" title="fRos.{e["locus"]}{pos}">')
                    html_parts.append(render_words(e['words'], 'zl'))
                    html_parts.append('</div>')
                html_parts.append('</div>')
        else:
            html_parts.append('<p class="empty">No ZL data</p>')
        html_parts.append('</div>')

        # Stolfi section
        html_parts.append('<div class="source stolfi">')
        html_parts.append('<h3>Stolfi (fRos_tr)</h3>')
        if st_entries:
            rings = [e for e in st_entries if e['type'] == 'ring']
            labels = [e for e in st_entries if e['type'] != 'ring']

            if rings:
                html_parts.append('<div class="text-group"><span class="group-label">Ring text</span>')
                for e in rings:
                    html_parts.append(f'<div class="entry" title="{e["region"]}.{e["locus"]} [{e["track"]}]">')
                    html_parts.append(render_words(e['words'], 'stolfi'))
                    html_parts.append('</div>')
                html_parts.append('</div>')

            if labels:
                html_parts.append('<div class="text-group"><span class="group-label">Labels</span>')
                for e in labels:
                    html_parts.append(f'<div class="entry" title="{e["region"]}.{e["locus"]} [{e["track"]}]">')
                    html_parts.append(render_words(e['words'], 'stolfi'))
                    html_parts.append('</div>')
                html_parts.append('</div>')

            # Check for not-transcribed ring text
            nt_for_rosette = []
            ring_map = {'NW': 'V1', 'NORTH': 'V2', 'NE': 'V3', 'WEST': 'N1',
                        'CENTER': 'N2', 'EAST': 'N3', 'SW': 'C1', 'SOUTH': 'C2', 'SE': 'C3'}
            ring_code = ring_map.get(rosette)
            if ring_code in not_transcribed:
                html_parts.append(f'<p class="not-trans">Ring ({ring_code}): NOT TRANSCRIBED</p>')
        else:
            # Check if whole rosette is missing
            ring_map = {'NW': 'V1', 'NORTH': 'V2', 'NE': 'V3', 'WEST': 'N1',
                        'CENTER': 'N2', 'EAST': 'N3', 'SW': 'C1', 'SOUTH': 'C2', 'SE': 'C3'}
            ring_code = ring_map.get(rosette)
            if ring_code in not_transcribed:
                html_parts.append(f'<p class="not-trans">Ring ({ring_code}): NOT TRANSCRIBED</p>')
            html_parts.append('<p class="empty">No Stolfi data</p>')
        html_parts.append('</div>')

        html_parts.append('</div>')

    # Outside face data from ZL
    outside = zl_data.get('OUTSIDE', [])

    content = '\n'.join(html_parts)

    # Count words
    zl_total = sum(len(e['words']) for entries in zl_data.values() for e in entries if entries)
    st_total = sum(len(e['words']) for entries in stolfi_data.values() for e in entries if entries)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Rosettes Text Viewer — Dual Source Comparison</title>
<style>
{all_font_faces}

* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
    background: #1a1a2e; color: #e0e0e0;
    font-family: 'Segoe UI', sans-serif; padding: 20px;
}}

h1 {{ text-align: center; margin-bottom: 5px; color: #e9c46a; }}
.subtitle {{ text-align: center; color: #888; margin-bottom: 15px; font-size: 13px; }}

.stats {{
    text-align: center; margin-bottom: 20px;
    font-size: 14px; color: #aaa;
}}
.stats .zl-stat {{ color: #3498db; }}
.stats .st-stat {{ color: #e67e22; }}

.legend {{
    display: flex; justify-content: center; gap: 20px;
    margin-bottom: 20px; font-size: 12px;
}}
.legend-item {{ display: flex; align-items: center; gap: 5px; }}
.legend-swatch {{ width: 14px; height: 14px; border-radius: 3px; display: inline-block; }}

.grid {{
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    grid-template-rows: auto auto auto;
    gap: 12px;
    max-width: 1600px;
    margin: 0 auto;
}}

.rosette {{
    background: #16213e; border: 1px solid #333; border-radius: 8px;
    padding: 12px;
}}
.rosette h2 {{
    color: #e9c46a; font-size: 16px; margin-bottom: 8px;
    border-bottom: 1px solid #333; padding-bottom: 4px;
}}

.source {{ margin-bottom: 10px; padding: 8px; border-radius: 6px; }}
.source.zl {{ background: rgba(52, 152, 219, 0.08); border: 1px solid rgba(52, 152, 219, 0.2); }}
.source.stolfi {{ background: rgba(230, 126, 34, 0.08); border: 1px solid rgba(230, 126, 34, 0.2); }}

.source h3 {{
    font-size: 11px; text-transform: uppercase; letter-spacing: 1px;
    margin-bottom: 6px;
}}
.source.zl h3 {{ color: #3498db; }}
.source.stolfi h3 {{ color: #e67e22; }}

.text-group {{
    margin-bottom: 6px;
}}
.group-label {{
    font-size: 10px; color: #666; text-transform: uppercase;
    display: block; margin-bottom: 3px;
}}

.entry {{
    margin-bottom: 4px; line-height: 2.2;
}}

.word {{
    display: inline-block; margin: 1px 2px; padding: 2px 5px;
    border-radius: 3px; cursor: default;
}}

.word .voynich {{
    font-family: 'EVA2', 'VoynichEVAHandA', 'VoynichEVA', monospace;
    font-size: 24px; display: block; line-height: 1.2;
}}
.word .eva {{
    font-size: 9px; color: #666; display: block;
    text-align: center; font-family: monospace;
}}

.word.zl {{
    background: rgba(52, 152, 219, 0.12);
    border: 1px solid rgba(52, 152, 219, 0.25);
}}
.word.zl .voynich {{ color: #5dade2; }}

.word.stolfi {{
    background: rgba(230, 126, 34, 0.12);
    border: 1px solid rgba(230, 126, 34, 0.25);
}}
.word.stolfi .voynich {{ color: #f0a050; }}

.word.uncertain {{
    background: rgba(200, 200, 200, 0.08);
    border: 1px solid rgba(200, 200, 200, 0.15);
}}
.word.uncertain .voynich {{ color: #888; }}

.empty {{ color: #555; font-style: italic; font-size: 12px; }}
.not-trans {{ color: #e74c3c; font-style: italic; font-size: 11px; margin-top: 4px; }}

.toggle-btn {{
    display: inline-block; margin: 5px; padding: 6px 16px;
    background: #264653; color: #e9c46a; border: 1px solid #e9c46a;
    border-radius: 5px; cursor: pointer; font-size: 13px;
}}
.toggle-btn:hover {{ background: #2a9d8f; }}
.controls {{ text-align: center; margin-bottom: 15px; }}

.outside-section {{
    max-width: 1600px; margin: 20px auto 0;
    background: #16213e; padding: 15px; border-radius: 8px;
    border: 1px solid #333;
}}
.outside-section h3 {{ color: #e9c46a; margin-bottom: 10px; }}
</style>
</head>
<body>
<h1>Rosettes Foldout — Dual Transcription Viewer</h1>
<p class="subtitle">Compare Zandbergen (ZL) and Stolfi sources — hover words for locus info</p>

<div class="stats">
    <span class="zl-stat">Zandbergen: {zl_total} words</span> &nbsp;|&nbsp;
    <span class="st-stat">Stolfi: {st_total} words</span>
</div>

<div class="legend">
    <div class="legend-item"><div class="legend-swatch" style="background:rgba(52,152,219,0.3)"></div> Zandbergen (ZL)</div>
    <div class="legend-item"><div class="legend-swatch" style="background:rgba(230,126,34,0.3)"></div> Stolfi</div>
    <div class="legend-item"><div class="legend-swatch" style="background:rgba(200,200,200,0.15)"></div> Uncertain (?/*)</div>
</div>

<div class="controls">
    <button class="toggle-btn" onclick="document.querySelectorAll('.eva').forEach(e=>e.style.display=e.style.display==='none'?'block':'none')">Toggle EVA</button>
    <button class="toggle-btn" onclick="document.querySelectorAll('.source.stolfi').forEach(e=>e.style.display=e.style.display==='none'?'block':'none')">Toggle Stolfi</button>
    <button class="toggle-btn" onclick="document.querySelectorAll('.source.zl').forEach(e=>e.style.display=e.style.display==='none'?'block':'none')">Toggle ZL</button>
</div>

<div class="grid">
{content}
</div>

{'<div class="outside-section"><h3>Outside Face (ZL only, paragraphs I-VIII)</h3>' + ''.join(
    f'<div class="entry" title="fRos.{e["locus"]} [{e.get("position","")}]">{render_words(e["words"], "zl")}</div>'
    for e in outside
) + '</div>' if outside else ''}

</body>
</html>"""
    return html


def main():
    print('Parsing Zandbergen transcription...')
    zl_data = parse_zl(ZL_PATH)
    for r in ROSETTE_ORDER:
        entries = zl_data.get(r, [])
        words = sum(len(e['words']) for e in entries)
        rings = sum(1 for e in entries if e['type'] == 'ring')
        labels = sum(1 for e in entries if e['type'] == 'label')
        print(f'  {r:8s}: {words:3d} words ({rings} ring, {labels} label entries)')
    outside = zl_data.get('OUTSIDE', [])
    if outside:
        words = sum(len(e['words']) for e in outside)
        print(f'  {"OUTSIDE":8s}: {words:3d} words ({len(outside)} entries)')

    print('\nParsing Stolfi transcription...')
    stolfi_data, not_transcribed = parse_stolfi()
    for r in ROSETTE_ORDER:
        entries = stolfi_data.get(r, [])
        words = sum(len(e['words']) for e in entries)
        print(f'  {r:8s}: {words:3d} words')
    print(f'  Not transcribed: {not_transcribed}')

    print('\nGenerating HTML...')
    html = generate_html(zl_data, stolfi_data, not_transcribed)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f'\nSaved to: {OUT_HTML}')


if __name__ == '__main__':
    main()
