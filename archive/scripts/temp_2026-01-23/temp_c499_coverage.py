import json
d=json.load(open('C:/git/voynich/phases/BRUNSCHWIG_CANDIDATE_LABELING/results/material_class_priors.json'))

results = d['results']
high_conf = [r for r in results if r['top_class_probability'] >= 0.7]
med_conf = [r for r in results if 0.5 <= r['top_class_probability'] < 0.7]
low_conf = [r for r in results if r['top_class_probability'] < 0.5]

print('C499 Coverage:')
print(f'  Total RI MIDDLEs: 349')
print(f'  With probability vectors: 128 (36.7%)')
print(f'  No data (no classified folios): 221 (63.3%)')
print()
print('Of 128 analyzed:')
print(f'  High confidence (P >= 0.7): {len(high_conf)} ({100*len(high_conf)/128:.1f}%)')
print(f'  Medium confidence (0.5-0.7): {len(med_conf)} ({100*len(med_conf)/128:.1f}%)')
print(f'  Low confidence (P < 0.5): {len(low_conf)} ({100*len(low_conf)/128:.1f}%)')
print()
print(f"Mean entropy: {d['summary']['mean_entropy']:.2f} bits")
print(f"Entropy range: {d['summary']['min_entropy']:.2f} - {d['summary']['max_entropy']:.2f} bits")
