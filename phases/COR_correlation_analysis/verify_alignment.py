#!/usr/bin/env python3
"""Verify folio-to-page alignment by cross-referencing data sources."""

import json
import csv

# Load visual coding
with open('visual_coding_complete.json') as f:
    vc = json.load(f)

# Load transcription (H transcriber only)
with open('data/transcriptions/interlinear_full_words.txt', newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    trans_rows = []
    for row in reader:
        transcriber = row.get('transcriber', '').strip().strip('"')
        if transcriber == 'H':
            trans_rows.append(row)

print("=" * 60)
print("ALIGNMENT VERIFICATION")
print("=" * 60)

# Test 1: Check if our heading words match first words in transcription
print("\nTest 1: Heading word verification")
print("-" * 40)

folios_to_check = ['f38r', 'f42r', 'f11r', 'f23v', 'f2r', 'f25r']

for fid in folios_to_check:
    if fid in vc['folios']:
        our_heading = vc['folios'][fid].get('heading', 'N/A')

        # Get first word from transcription for this folio
        folio_rows = [r for r in trans_rows if r['folio'] == fid]
        if len(folio_rows) > 0:
            first_word = folio_rows[0]['word']
            # Check line 1 specifically
            line1_rows = [r for r in folio_rows if r['line_number'] == '1']
            if len(line1_rows) > 0:
                first_line1_word = line1_rows[0]['word']
            else:
                first_line1_word = "N/A"
        else:
            first_word = "NO_DATA"
            first_line1_word = "NO_DATA"

        match = "MATCH" if our_heading == first_line1_word else "DIFF"
        print(f"  {fid}: our_heading={our_heading}, trans_first_word={first_line1_word} [{match}]")

# Test 2: Check unique folios in transcription
print("\n" + "-" * 40)
print("Test 2: Folio count verification")
print("-" * 40)
trans_folios = list(dict.fromkeys(r['folio'] for r in trans_rows))  # Preserve order, unique
print(f"  Unique folios in transcription: {len(trans_folios)}")
print(f"  First 10: {trans_folios[:10]}")

# Test 3: Cross-check with heading_word_analysis results
print("\n" + "-" * 40)
print("Test 3: Cross-reference with heading_word_analysis.json")
print("-" * 40)

try:
    with open('heading_word_analysis_report.json') as f:
        hwa = json.load(f)

    # Get heading assignments from that analysis
    if 'heading_assignments' in hwa:
        print("  Heading assignments found in analysis report")
        ha = hwa['heading_assignments']

        # Spot check
        for fid in ['f38r', 'f42r']:
            if fid in ha and fid in vc['folios']:
                report_heading = ha[fid]
                our_heading = vc['folios'][fid]['heading']
                match = "MATCH" if report_heading == our_heading else f"DIFF: {report_heading} vs {our_heading}"
                print(f"    {fid}: {match}")
except FileNotFoundError:
    print("  heading_word_analysis_report.json not found")

# Test 4: Check h2_2_hub_singleton_contrast.json for authoritative folio-heading mapping
print("\n" + "-" * 40)
print("Test 4: Cross-reference with hub_singleton_contrast")
print("-" * 40)

try:
    with open('h2_2_hub_singleton_contrast.json') as f:
        hub = json.load(f)

    # Find folio-heading mappings
    if 'hub_headings' in hub:
        for entry in hub['hub_headings'][:5]:
            folio = entry.get('folio')
            heading = entry.get('heading')
            if folio and heading and folio in vc['folios']:
                our_heading = vc['folios'][folio]['heading']
                match = "MATCH" if heading == our_heading else f"DIFF"
                print(f"    {folio}: hub_analysis={heading}, visual_coding={our_heading} [{match}]")
except (FileNotFoundError, KeyError) as e:
    print(f"  Error: {e}")

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print("If headings match across sources, the folio IDs are correctly aligned.")
print("The transcription data is authoritative (scholarly source).")
