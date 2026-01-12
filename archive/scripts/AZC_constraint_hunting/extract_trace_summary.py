"""Extract summary from activation trace results."""
import json

with open('results/b_azc_activation_trace.json') as f:
    d = json.load(f)

# Print just the summary parts
print("=== F-AZC-015 SUMMARY ===\n")
print(f"Fit ID: {d['fit_id']}")
print(f"Question: {d['question']}")
print(f"\nParameters: {d['parameters']}")

print("\n=== TYPE ANALYSIS ===")
for folio_type, summary in d['type_analysis'].items():
    print(f"\n{folio_type.upper()}:")
    for k, v in summary.items():
        print(f"  {k}: {v}")

print("\n=== INTERPRETATION ===")
for k, v in d['interpretation'].items():
    print(f"{k}: {v}")

# Per-folio summaries (exclude window details)
print("\n=== PER-FOLIO SUMMARIES ===")
for trace in d['traces']:
    folio = trace['folio']
    if 'summary' in trace:
        s = trace['summary']
        print(f"\n{folio}:")
        print(f"  n_tokens: {trace['n_tokens']}")
        print(f"  n_windows: {trace['n_windows']}")
        print(f"  n_folios_mean: {s['n_folios_mean']} (min={s['n_folios_min']}, max={s['n_folios_max']}, std={s['n_folios_std']})")
        print(f"  zodiac_fraction_mean: {s['zodiac_fraction_mean']}")
        print(f"  phase_suffix_mean: {s['phase_suffix_mean']}")
        print(f"  pattern: {s['pattern']}")
        print(f"  persistence: {s['persistence']}")
    else:
        print(f"\n{folio}: {trace.get('status', 'unknown')}")
