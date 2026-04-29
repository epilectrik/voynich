"""
Phase 640 Sub-Phase 1b: Seed the dictionary with D0/D1 definitions.

These are tokens where operational meaning is forced by distribution,
hazard topology, recipe context, or validated constraints.

Reads baseline JSON, adds definitions, writes updated JSON.
"""
import sys, io, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

results_dir = os.path.join(os.path.dirname(__file__), '..', 'results')
baseline_path = os.path.join(results_dir, 'b_dictionary_baseline.json')

with open(baseline_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

entries = data['entries']

# ============================================================
# SEED DEFINITIONS
# Format: token -> (confidence, operational_def, workshop_reading, evidence, notes)
# ============================================================

seeds = {
    # === D0: LOCKED (forced by multiple converging evidence) ===

    'dar': ('D0',
        'Introduce new material into vessel',
        'Add a new substance — vigorous material introduction event',
        ['C1925: 6/6 partition on matched folios', 'Extended to 21/21 matched folios (session 2026-04-11)',
         'dar=0 on all cohobation/separation recipes', 'dar count tracks material events precisely'],
        'The material introduction marker. Each dar = one physical addition event.'),

    'dal': ('D0',
        'Careful passive placement or transfer of material',
        'Place material carefully — gentle/measured transfer or output',
        ['C1925: complement of dar', 'dal=6 on f77v (furnace spec, careful arrangement)',
         'dal > dar on specification folios (f75v)'],
        'Passive counterpart to dar. Careful placement vs vigorous addition.'),

    'chekar': ('D0',
        'Post-thermal quality check',
        'Test the product quality — active quality verification after heating',
        ['C1926: 7/83 folios, balneum-monitoring signature',
         'f84r L29: appears between precipitation and melting = gold detection test',
         'qo depleted 0.48x, daiin enriched 3.7x on chekar folios'],
        'Formal quality checkpoint. Appears once per folio where product verification is needed.'),

    'ol': ('D0',
        'Sustain current state / continue',
        'Hold steady — maintain current arrangement without change',
        ['C609: 13.2% of B tokens (LINK morphology)', 'C1174: morphological substrate',
         'C1388: o+l = arrange+state = STAGING, 100% STAGING per C1556',
         'Class 11 singleton (C558)'],
        'The continuation/sustain token. Most common operational word. "Keep going as you are."'),

    'or': ('D0',
        'Respond to current state / flow routing',
        'Note what happened — acknowledge and route to next action',
        ['C1563: line-final routing architecture', 'C1235: flow routing token',
         'o+r = arrange+respond'],
        'Line-boundary flow marker. "This step responds to what just happened."'),

    'daiin': ('D0',
        'Begin iteration cycle / trigger energy sequence',
        'Start a new cycle — initiate the next heating-monitoring loop',
        ['C557: Class 10 singleton, 27.7% line-initial', 'C558: 47.1% ENERGY followers',
         'C1234: bounded iteration construct', 'C1909/C1914: CC trigger function'],
        'The cycle trigger. Signals "begin the next iteration of the process."'),

    'aiin': ('D0',
        'Yield into iteration cycle',
        'Yield product into the next processing cycle',
        ['C1234: iteration construct (ain/aiin/aiiin family)',
         'a+i+i+n = yield.iterate.iterate.bind'],
        'Iteration with yield. "The output from this step feeds into the next cycle."'),

    'am': ('D0',
        'Phase complete / yield final',
        'This phase is done — yield the result and close',
        ['C1237: -am 5.19x at paragraph-final', 'a+m = yield.final',
         'Paragraph termination signal'],
        'Phase completion marker. Signals end of a major operational phase.'),

    'dam': ('D0',
        'Process finalization',
        'Finalize this process step — material handling complete',
        ['C912: finalization anchor', 'C1237/C1240: paragraph-final marker',
         'da+m = material.final', 'f84r: appears at 2 major phase endings'],
        'Stronger than am. Marks completion of a material-handling process.'),

    'otaly': ('D0',
        'Final transfer complete — pour product and end',
        'Pour the finished product — transfer, yield, done',
        ['f84r coda: final token on gold dissolution folio',
         'ot+a+l+y = transfer.yield.state.end'],
        'Process completion coda. "Pour out the product. Process finished."'),

    # === D1: STRONG (atom gloss + independent confirmation) ===

    'chedy': ('D1',
        'Active check: cool and execute',
        'Check the state — active verification that cooling/stabilization is proceeding',
        ['C929: ch = active test/checkpoint', 'Most common token in corpus (freq=491)',
         'ch+e+d+y = check.cool.do.end'],
        'The workhorse checkpoint token. "Actively verify the current cooling state."'),

    'shedy': ('D1',
        'Passive monitoring: cool and execute',
        'Watch the state — passive observation of cooling/stabilization process',
        ['C929: sh = passive monitoring', 'freq=416, 66 folios',
         'sh+e+d+y = watch.cool.do.end'],
        'The workhorse monitoring token. "Observe without intervening."'),

    'qokedy': ('D1',
        'Apply moderate heat cycle',
        'Heat source: apply standard heat, cool, execute, done',
        ['C1300: qo = near-pure THERMAL channel', 'C1225: e_depth=1 = moderate',
         'qo+k+e+d+y = heat.cool.do.end', 'freq=271, 61 folios'],
        'Standard heat application. Not gentle (that is qokeedy) but not aggressive.'),

    'qokeedy': ('D1',
        'Apply gentle sustained heat (balneum mariae)',
        'Heat source: gentle heat in water bath, execute, done',
        ['C1225: e_depth=2 = gentle/stabilized (balneum signature)',
         'C1735: Brunschwig gentle/elevated fire distinction',
         'qo+k+e+e+d+y = heat.cool.cool.do.end', 'freq=306, 54 folios',
         'f108v: e_depth=0.99, pure balneum folio dominated by this token'],
        'Gentle balneum heat. "Maintain steady gentle heat in the water bath."'),

    'qokeey': ('D1',
        'Set gentle heat level',
        'Heat source: establish gentle heat state',
        ['C1225: e_depth=2', 'qo+k+e+e+y = heat.cool.cool.end (no d=execute)',
         'freq=264, 52 folios', '-ey suffix = set/stabilize (vs -edy = execute)'],
        'Heat level setting, not execution. "Set the heat to gentle/balneum level."'),

    'qokain': ('D1',
        'Heat with iterative binding',
        'Heat source: apply heat and iterate — sustained cyclic heating',
        ['qo+k+a+i+n = heat.yield.iterate.bind', 'freq=275, 43 folios',
         'The iterative heat token. Appears during sustained/repeated heating phases.'],
        'Cyclic heat application. "Continue heating through another cycle."'),

    'qokaiin': ('D1',
        'Deep iterative heating',
        'Heat source: sustained deep cyclic heating — multiple iterations',
        ['qo+k+a+i+i+n = heat.yield.iterate.iterate.bind', 'freq=240, 54 folios',
         'Deeper iteration than qokain. Extended heating sequences.'],
        'Extended cyclic heating. "Continue sustained heat through multiple cycles."'),

    'qokal': ('D1',
        'Heat to completion / steady state',
        'Heat source: bring heat to yield state — heat until stable',
        ['qo+k+a+l = heat.yield.state', 'freq=167, 51 folios',
         '-al suffix = yield+state = completion state',
         'f75r: appears at distillation pass endpoints'],
        'Heat completion marker. "Heat until the process reaches steady state."'),

    'qokar': ('D1',
        'Heat and respond to result',
        'Heat source: apply heat and note the response',
        ['qo+k+a+r = heat.yield.respond', 'freq=129, 37 folios',
         '-ar suffix = yield+respond = note what happened'],
        'Responsive heating. "Heat and observe what the material does."'),

    'qotar': ('D1',
        'Heat transfer and respond',
        'Heat source: transfer heat/material and note result',
        ['qo+t+a+r = heat-transfer.yield.respond', 'freq=70, 29 folios'],
        'Heat-induced transfer with observation. "Apply heat to drive transfer, note result."'),

    'qotedy': ('D1',
        'Heat transfer cycle',
        'Heat source: execute a heat-driven transfer operation',
        ['qo+t+e+d+y = heat-transfer.cool.do.end', 'freq=96, 30 folios',
         't-HEAD = FLOW/transfer domain (C1475)'],
        'Heat-driven transfer step. "Drive material through by heating."'),

    'shey': ('D1',
        'Brief passive observation',
        'Watch briefly — quick passive check',
        ['sh+e+y = watch.cool.end', 'freq=204, 45 folios',
         'Shorter/lighter version of shedy (no d=execute component)'],
        'Quick look. "Briefly observe the current state."'),

    'chey': ('D1',
        'Brief active check',
        'Quick active verification',
        ['ch+e+y = check.cool.end', 'freq=250, 59 folios',
         'Shorter version of chedy'],
        'Quick check. "Briefly verify the state."'),

    'okain': ('D1',
        'Seal/secure vessel with iteration',
        'Vessel management: seal the vessel for a processing cycle',
        ['ok+a+i+n = vessel.yield.iterate.bind', 'freq=94, 40 folios',
         'n-terminal = contain/secure. ok = vessel channel.',
         'Appears at moments of sealing in f84r, f82r'],
        'Vessel sealing. "Seal the vessel for the next processing cycle."'),

    'okaiin': ('D1',
        'Deep vessel cycling / extended sealed operation',
        'Vessel management: extended sealed processing through multiple cycles',
        ['ok+a+i+i+n = vessel.yield.iterate.iterate.bind', 'freq=168, 58 folios',
         'Deeper iteration variant of okain'],
        'Extended sealed vessel operation. "Maintain sealed vessel through many cycles."'),

    'otedy': ('D1',
        'Monitor transfer rate: cool and execute',
        'Transfer rate: check the drip/flow rate during cooling',
        ['C1958: ot = transfer rate / drip rate', 'ot+e+d+y = transfer.cool.do.end',
         'freq=150, 52 folios'],
        'Transfer monitoring. "Check the drip rate during this cooling step."'),

    'dy': ('D1',
        'Execute and end / done',
        'Cycle close — this action is complete',
        ['d+y = do.end (C1934)', 'freq=124, 48 folios',
         'Headless closure. Bare execution marker.'],
        'Minimal closure. "Done."'),

    'al': ('D1',
        'Yield to state / output ready',
        'The product is at rest — yield has reached stable state',
        ['a+l = yield.state', 'freq=186, 49 folios',
         'Mode B continuation token'],
        'Output state. "The yield is now in a stable state."'),

    'ar': ('D1',
        'Yield and respond',
        'Note the yield — observe what was produced',
        ['a+r = yield.respond', 'freq=248, 68 folios',
         'Very common bare token, line-medial/final'],
        'Output observation. "Note what came out."'),

    'sain': ('D1',
        'Iterate and bind',
        'Begin a binding iteration cycle',
        ['sa+i+n = iterate.iterate.bind', 'freq=97, 42 folios',
         'sa PREFIX = iteration channel'],
        'Iteration trigger. "Start the next binding/containment cycle."'),

    'saiin': ('D1',
        'Deep iteration and bind',
        'Begin an extended binding iteration cycle',
        ['sa+i+i+n = iterate.iterate.iterate.bind', 'freq=67, 30 folios',
         'Deeper version of sain'],
        'Extended iteration. "Start a long iterative processing cycle."'),

    'dain': ('D1',
        'Material iteration binding',
        'Infrastructure: bind material into iteration cycle',
        ['da+i+n = material.iterate.bind', 'freq=109, 48 folios',
         'da PREFIX = infrastructure/material handling channel'],
        'Material cycling. "Bind this material into the next iteration."'),

    # === D1: Dark pipeline material markers ===

    'qokeor': ('D1',
        'Heat source: gentle heat then respond/observe',
        'Apply gentle heat and observe the result',
        ['qo+k+e+o+r = heat.cool.arrange.respond', 'freq=18, 14 folios'],
        'Gentle heat with observation. "Heat gently and see what happens."'),

    'okeedy': ('D1',
        'Vessel at gentle temperature',
        'Vessel management: maintain vessel at gentle balneum temperature',
        ['ok+e+e+d+y = vessel.cool.cool.do.end', 'freq=62, 28 folios',
         'ok channel + e_depth=2 = vessel at balneum temperature'],
        'Vessel temperature control. "Keep the vessel at gentle bath temperature."'),

    'okedy': ('D1',
        'Vessel check: cool and done',
        'Vessel management: check vessel during cooling',
        ['ok+e+d+y = vessel.cool.do.end', 'freq=86, 34 folios'],
        'Vessel monitoring during cooling. "Check the vessel state."'),

    'olchey': ('D1',
        'Continue with checking adjustment',
        'Sustain state while checking adjustment',
        ['ol+ch+e+y = sustain.adjust.watch.cool.end', 'freq=35, 18 folios'],
        'Sustained checking. "Maintain state while verifying adjustment."'),

    'qol': ('D1',
        'Heat source: maintain state',
        'Heat source: hold current heat level',
        ['qo+l = heat.state (bare, no suffix)', 'freq=145, 32 folios',
         'Minimal heat maintenance token'],
        'Heat hold. "Keep the fire at its current level."'),

    'sol': ('D1',
        'Sequence: state marker',
        'Sequence position: mark current state in sequence',
        ['so+l = sequence.state', 'freq=59, 22 folios'],
        'Sequence marker. "Note position in the operational sequence."'),

    'pol': ('D1',
        'Position/state: begin new phase',
        'State specification: mark a new operational position',
        ['po+l = position.state', 'freq=34, 18 folios',
         'po PREFIX = state/position opener (C1396)'],
        'Phase marker. "Begin a new operational state."'),

    'lchedy': ('D1',
        'Equipment check: cool and execute',
        'Check equipment state during cooling',
        ['lch+e+d+y = equipment.cool.do.end', 'freq=67, 25 folios',
         'lch = apparatus/equipment dark pipeline marker (C1941)'],
        'Equipment monitoring. "Check the apparatus is functioning correctly."'),

    'qoky': ('D1',
        'Heat: end',
        'Heat source: cease heating',
        ['qo+k+y = heat.heat.end', 'freq=83, 24 folios',
         'Minimal heat token with y-terminal = end'],
        'Heat cessation or completion. "Stop heating" or "heating step done."'),

    'qokam': ('D1',
        'Heat to finality',
        'Heat source: bring to final heat state — distillation pass complete',
        ['qo+k+a+m = heat.yield.final', 'freq=26, 16 folios',
         '-am = yield.final = completion. Appears at pass endpoints.',
         'f75r: appears at P5 and P6 = end of distillation passes'],
        'Distillation pass completion. "This heating pass is done."'),

    'rom': ('D1',
        'Respond and finalize',
        'Respond to the result and close this phase',
        ['r+o+m = respond.arrange.final', 'freq=9, 8 folios',
         'Phase boundary marker. Appears at zone transitions in f84r.'],
        'Phase finalization. "Acknowledge the result and close."'),
}

# Apply seeds to dictionary
seeded = 0
for token, (conf, opdef, workshop, evidence, notes) in seeds.items():
    if token in entries:
        entries[token]['confidence'] = conf
        entries[token]['operational_def'] = opdef
        entries[token]['workshop_reading'] = workshop
        entries[token]['evidence'] = evidence
        entries[token]['notes'] = notes
        seeded += 1
    else:
        print(f"WARNING: seed token '{token}' not found in baseline!")

print(f"\nSeeded {seeded} definitions ({sum(1 for t,v in seeds.items() if v[0]=='D0')} D0, {sum(1 for t,v in seeds.items() if v[0]=='D1')} D1)")

# Save updated dictionary
output_path = os.path.join(results_dir, 'b_dictionary_v0.1.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
print(f"Wrote {output_path}")

# Generate cheat sheet for seeded tokens
cheat_path = os.path.join(results_dir, 'b_dictionary_seeds.md')
with open(cheat_path, 'w', encoding='utf-8') as f:
    f.write("# Voynich B Dictionary — Seed Definitions\n\n")
    f.write(f"**Seeded:** {seeded} tokens ({sum(1 for t,v in seeds.items() if v[0]=='D0')} D0, {sum(1 for t,v in seeds.items() if v[0]=='D1')} D1)\n\n")

    f.write("## D0 — LOCKED (forced by multiple converging evidence)\n\n")
    f.write(f"| Token | Freq | Folios | Operational Definition | Workshop Reading |\n")
    f.write(f"|-------|------|--------|----------------------|------------------|\n")
    for token in sorted(seeds.keys(), key=lambda t: -entries.get(t, {}).get('frequency', 0)):
        conf, opdef, workshop, evidence, notes = seeds[token]
        if conf != 'D0':
            continue
        e = entries.get(token, {})
        f.write(f"| {token} | {e.get('frequency',0)} | {e.get('folio_count',0)} | {opdef} | {workshop} |\n")

    f.write("\n## D1 — STRONG (atom gloss + independent confirmation)\n\n")
    f.write(f"| Token | Freq | Folios | Operational Definition | Workshop Reading |\n")
    f.write(f"|-------|------|--------|----------------------|------------------|\n")
    for token in sorted(seeds.keys(), key=lambda t: -entries.get(t, {}).get('frequency', 0)):
        conf, opdef, workshop, evidence, notes = seeds[token]
        if conf != 'D1':
            continue
        e = entries.get(token, {})
        f.write(f"| {token} | {e.get('frequency',0)} | {e.get('folio_count',0)} | {opdef} | {workshop} |\n")

print(f"Wrote {cheat_path}")

# Coverage stats
d0_freq = sum(entries[t]['frequency'] for t in seeds if seeds[t][0] == 'D0' and t in entries)
d1_freq = sum(entries[t]['frequency'] for t in seeds if seeds[t][0] == 'D1' and t in entries)
total = data['metadata']['total_tokens']
print(f"\nCoverage: D0 tokens cover {d0_freq} occurrences ({100*d0_freq/total:.1f}%)")
print(f"          D1 tokens cover {d1_freq} occurrences ({100*d1_freq/total:.1f}%)")
print(f"          D0+D1 total: {d0_freq+d1_freq} occurrences ({100*(d0_freq+d1_freq)/total:.1f}%)")
