"""
Download readable text versions of Rupescissa's De consideratione quintae essentiae.

Sources:
1. Archive.org Basel 1561 printed edition - Latin OCR text
2. MSU Dissertation - Middle English translation with commentary
"""

import requests
import os
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent

def download_archive_org_text():
    """Download Latin OCR text from Archive.org Basel 1561 edition."""
    print("Downloading Latin text from Archive.org...")

    # The item ID for the Basel 1561 edition
    item_id = "BIUSante_70211"

    # Try multiple potential URLs for the text file
    urls = [
        f"https://archive.org/download/{item_id}/{item_id}_djvu.txt",
        f"https://archive.org/download/{item_id}/70211_djvu.txt",
    ]

    for url in urls:
        try:
            print(f"  Trying: {url}")
            response = requests.get(url, timeout=60, allow_redirects=True)
            if response.status_code == 200 and len(response.content) > 1000:
                output_path = OUTPUT_DIR / "rupescissa_latin_1561.txt"
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                print(f"  SUCCESS: Saved {len(response.content):,} bytes to {output_path.name}")
                return True
        except Exception as e:
            print(f"  Failed: {e}")

    print("  Could not download Latin text automatically.")
    print(f"  Manual download: https://archive.org/details/{item_id}")
    return False

def download_msu_text():
    """Download Middle English translation from MSU dissertation."""
    print("\nDownloading Middle English translation from MSU...")

    # MSU dissertation full text
    urls = [
        "https://d.lib.msu.edu/etd/47644/datastream/FULL_TEXT/download",
        "https://d.lib.msu.edu/islandora/object/etd%3A47644/datastream/FULL_TEXT/download",
    ]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    for url in urls:
        try:
            print(f"  Trying: {url}")
            response = requests.get(url, timeout=60, headers=headers, allow_redirects=True)
            if response.status_code == 200 and len(response.content) > 1000:
                output_path = OUTPUT_DIR / "rupescissa_middle_english.txt"
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                print(f"  SUCCESS: Saved {len(response.content):,} bytes to {output_path.name}")
                return True
        except Exception as e:
            print(f"  Failed: {e}")

    print("  Could not download MSU text automatically.")
    print("  Manual download: https://d.lib.msu.edu/etd/47644")
    return False

def create_summary():
    """Create a summary of what was downloaded."""
    summary = """# Rupescissa Text Files

## Downloaded Versions

### rupescissa_latin_1561.txt
- Source: Archive.org Basel 1561 printed edition
- Language: Latin (OCR from printed text)
- Original: https://archive.org/details/BIUSante_70211
- Content: Full text of "De consideratione quintae essentiae"

### rupescissa_middle_english.txt
- Source: MSU Dissertation (2015)
- Language: Middle English translation with scholarly commentary
- Original: https://d.lib.msu.edu/etd/47644
- Content: Academic edition with introduction, notes, and translation

## Structure of the Original Text

The treatise is divided into two books:

**Book 1 (Liber Primus):** Distillation processes
- Organized in subdivisions called "canones" (rules/chapters)
- Describes extraction of quintessence from wine, plants, minerals

**Book 2 (Liber Secundus):** Medical applications
- Organized in chapters called "remedia" (remedies)
- "De generalibus remediis" - On general remedies

## Key Concepts

1. **Quinta Essentia:** The incorruptible fifth element (Aristotelian)
2. **Aqua Vitae:** Distilled wine = earthly form of celestial matter
3. **Circular Distillation:** "Continuous rising and falling" to purify
4. **Preservation:** Quintessence prevents corruption and decay

## Historical Context

Rupescissa (~1351) -> Puff (~1455) -> Brunschwig (1500)
   WHY              WHAT            HOW
   Theory           Catalog         Manual
"""

    summary_path = OUTPUT_DIR / "TEXT_SOURCES.md"
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(summary)
    print(f"\nCreated summary: {summary_path.name}")

if __name__ == "__main__":
    print("=" * 60)
    print("Rupescissa Text Downloader")
    print("=" * 60)
    print()

    latin_ok = download_archive_org_text()
    english_ok = download_msu_text()
    create_summary()

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Latin (Archive.org):    {'OK' if latin_ok else 'MANUAL DOWNLOAD NEEDED'}")
    print(f"Middle English (MSU):   {'OK' if english_ok else 'MANUAL DOWNLOAD NEEDED'}")
    print()

    if not (latin_ok and english_ok):
        print("For manual downloads, visit the URLs shown above.")
