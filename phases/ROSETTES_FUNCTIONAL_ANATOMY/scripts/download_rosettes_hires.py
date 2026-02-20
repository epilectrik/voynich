"""Download and stitch high-res Rosettes foldout from jasondavies.com tiles."""

import math
import requests
from pathlib import Path
from PIL import Image
from io import BytesIO

TILE_SIZE = 256
BASE_URL = "https://voynich.jasondavies.com"

# Ros2 = main rosettes foldout (inside face with 9 rosettes)
FOLIO = "Ros2"
WIDTH = 7590
HEIGHT = 7624

def main():
    levels = math.ceil(math.log2(max(WIDTH, HEIGHT) / TILE_SIZE))
    zoom = levels  # max zoom for full resolution

    cols = math.ceil(WIDTH / TILE_SIZE)
    rows = math.ceil(HEIGHT / TILE_SIZE)

    print(f"Folio: {FOLIO}")
    print(f"Full size: {WIDTH}x{HEIGHT}")
    print(f"Zoom level: {zoom} ({cols}x{rows} = {cols*rows} tiles)")

    # Create output image
    img = Image.new('RGB', (cols * TILE_SIZE, rows * TILE_SIZE), (255, 255, 255))

    session = requests.Session()
    failed = []

    for y in range(rows):
        for x in range(cols):
            url = f"{BASE_URL}/{FOLIO}/{zoom}/{y}/{x}.jpg"
            try:
                r = session.get(url, timeout=10)
                if r.status_code == 200:
                    tile = Image.open(BytesIO(r.content))
                    img.paste(tile, (x * TILE_SIZE, y * TILE_SIZE))
                else:
                    failed.append((x, y, r.status_code))
            except Exception as e:
                failed.append((x, y, str(e)))

        pct = (y + 1) / rows * 100
        print(f"  Row {y+1}/{rows} ({pct:.0f}%)", end='\r')

    print()

    if failed:
        print(f"Warning: {len(failed)} tiles failed")
        for x, y, err in failed[:5]:
            print(f"  ({x},{y}): {err}")

    # Crop to actual dimensions
    img = img.crop((0, 0, WIDTH, HEIGHT))

    out_dir = Path(__file__).resolve().parent.parent / 'results'
    out_file = out_dir / 'rosettes_foldout_hires.jpg'
    img.save(out_file, 'JPEG', quality=95)

    print(f"\nSaved: {out_file}")
    print(f"Size: {WIDTH}x{HEIGHT} ({out_file.stat().st_size / 1024 / 1024:.1f} MB)")


if __name__ == '__main__':
    main()
