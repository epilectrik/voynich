#!/usr/bin/env python3
"""
Extract priority folio images for the comparative annotation system.
Priority folios are needed to test specific hypotheses about:
1. Multi-folio category visual consistency (pchor, tshor, kooiin, kshody)
2. Hub category characterization (tol, pol, tor, kor, par)
3. Prefix-visual correlations (ko-prefix, po-prefix folios)
"""

import fitz
import os
import json

PDF_PATH = r'C:\git\voynich\data\scans\Voynich_Manuscript.pdf'
OUTPUT_DIR = r'C:\git\voynich\data\scans\extracted'

# Priority folios needed for annotation system
PRIORITY_FOLIOS = [
    # Multi-folio categories (test category visual consistency)
    "f19r",   # pchor
    "f21r",   # pchor
    "f52v",   # pchor
    "f15r",   # tshor
    "f53v",   # tshor
    "f2v",    # kooiin (f29v exists)
    "f37v",   # kshody (f5r exists)

    # Hub categories (characterize major categories)
    "f58v",   # tol - 34 in-degree, opener role
    "f22r",   # pol - 25 in-degree, closer role
    "f96r",   # tor - 14 in-degree, closer role
    "f58r",   # kor - 10 in-degree, support role
    "f35v",   # par - 9 in-degree, opener role
]

# Already extracted (from pilot set)
ALREADY_EXTRACTED = [
    "f38r", "f25r", "f11r", "f11v", "f5v", "f10v", "f38v", "f5r", "f36r", "f30v",
    "f22v", "f9v", "f90v2", "f32v", "f17r", "f18r", "f9r", "f20v", "f2r", "f47v",
    "f24v", "f56r", "f42r", "f49v", "f51v", "f45v", "f3v", "f29v", "f4v", "f23v"
]


def parse_folio_id(folio_id):
    """Parse folio ID into number and side."""
    # Handle special cases like f90v2
    if 'v' in folio_id:
        parts = folio_id.split('v')
        num_str = parts[0][1:]  # Remove 'f'
        side = 'v'
    else:
        parts = folio_id.split('r')
        num_str = parts[0][1:]  # Remove 'f'
        side = 'r'

    try:
        folio_num = int(num_str)
        return folio_num, side
    except ValueError:
        return None, None


def get_page_number(folio_id, offset=2):
    """
    Calculate PDF page number for a folio.

    The holybooks PDF structure:
    - Pages 0-2: Cover/intro
    - Page 3+: Manuscript (f1r = page 3, f1v = page 4, etc.)

    Formula: page = offset + (folio_num - 1) * 2 + (0 if recto else 1)
    """
    folio_num, side = parse_folio_id(folio_id)

    if folio_num is None:
        return None

    side_offset = 0 if side == 'r' else 1
    page_num = offset + (folio_num - 1) * 2 + side_offset

    return page_num


def extract_folio_image(doc, page_num, folio_id, output_dir, dpi=150):
    """Extract a single page as a PNG image."""
    if page_num is None or page_num >= doc.page_count:
        print(f"  Invalid page number for {folio_id}: {page_num} (PDF has {doc.page_count} pages)")
        return None

    page = doc[page_num]

    # Convert to image at specified DPI
    mat = fitz.Matrix(dpi/72, dpi/72)
    pix = page.get_pixmap(matrix=mat)

    output_path = os.path.join(output_dir, f"{folio_id}.png")
    pix.save(output_path)

    return output_path


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Filter to folios that need extraction
    to_extract = [f for f in PRIORITY_FOLIOS if f not in ALREADY_EXTRACTED]

    print("Priority Folio Extraction")
    print("=" * 50)
    print(f"Priority folios requested: {len(PRIORITY_FOLIOS)}")
    print(f"Already extracted: {len([f for f in PRIORITY_FOLIOS if f in ALREADY_EXTRACTED])}")
    print(f"Need to extract: {len(to_extract)}")
    print()

    if not to_extract:
        print("All priority folios already extracted!")
        return

    print(f"Folios to extract: {to_extract}")
    print()

    # Open PDF
    print(f"Opening PDF: {PDF_PATH}")
    doc = fitz.open(PDF_PATH)
    print(f"PDF has {doc.page_count} pages")
    print()

    # Build page mapping and extract
    extracted = []
    failed = []

    for folio in to_extract:
        page_num = get_page_number(folio)
        print(f"Extracting {folio} (page {page_num})...", end=" ")

        result = extract_folio_image(doc, page_num, folio, OUTPUT_DIR)

        if result:
            print("OK")
            extracted.append(folio)
        else:
            print("FAILED")
            failed.append(folio)

    doc.close()

    # Summary
    print()
    print("=" * 50)
    print("Extraction Summary")
    print("=" * 50)
    print(f"Successfully extracted: {len(extracted)}/{len(to_extract)}")

    if extracted:
        print(f"  Extracted: {extracted}")

    if failed:
        print(f"  Failed: {failed}")
        print()
        print("Note: Failed extractions may need manual page number verification.")
        print("Check the PDF structure and update PAGE_OVERRIDES if needed.")

    # Create metadata file for priority folios
    metadata = {
        "description": "Priority folios for comparative annotation system",
        "purpose": {
            "multi_folio_categories": {
                "pchor": ["f19r", "f21r", "f52v"],
                "tshor": ["f15r", "f53v"],
                "kooiin": ["f2v", "f29v"],
                "kshody": ["f37v", "f5r"]
            },
            "hub_categories": {
                "tol": {"folio": "f58v", "in_degree": 34, "role": "opener"},
                "pol": {"folio": "f22r", "in_degree": 25, "role": "closer"},
                "tor": {"folio": "f96r", "in_degree": 14, "role": "closer"},
                "kor": {"folio": "f58r", "in_degree": 10, "role": "support"},
                "par": {"folio": "f35v", "in_degree": 9, "role": "opener"}
            }
        },
        "extraction_results": {
            "requested": PRIORITY_FOLIOS,
            "already_present": [f for f in PRIORITY_FOLIOS if f in ALREADY_EXTRACTED],
            "newly_extracted": extracted,
            "failed": failed
        },
        "total_available": len(ALREADY_EXTRACTED) + len(extracted)
    }

    metadata_path = os.path.join(OUTPUT_DIR, 'priority_folio_metadata.json')
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"\nSaved metadata to: {metadata_path}")


if __name__ == "__main__":
    main()
