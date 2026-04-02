"""
s1_discrimination_battery.py — Multi-axis discrimination battery for 5 abstract atoms.

Evaluates candidate glosses for d, o, c, p, s across 7 independent axes:
  1. Category Shift Match (C1394 T6)
  2. Scope Consistency (C1394 T4 / C1472)
  3. Terminal Selectivity (C1484)
  4. Tautology Check (atom + terminal redundancy)
  5. Cross-System Deployment (C1503, C1514, C1507)
  6. Compound Semantic Coherence (middle dictionary)
  7. Co-occurrence Avoidance (C1472)

Each axis scores 0/1/2. Total per candidate = max 14.
"""

import sys, io, json, math
from pathlib import Path
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = Path('C:/git/voynich')
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript, Morphology, ATOM_GLOSSES

# ================================================================
# SETUP: Load data
# ================================================================
tx = Transcript()
morph = Morphology()
a_toks = list(tx.currier_a())
b_toks = list(tx.currier_b())

# Load middle dictionary for compound glosses
with open(ROOT / 'data' / 'middle_dictionary.json', 'r', encoding='utf-8') as f:
    mid_dict = json.load(f)['middles']

# ================================================================
# EMPIRICAL DATA: Atom A/B enrichment
# ================================================================
a_atom_counts = Counter()
b_atom_counts = Counter()

for tok in a_toks:
    w = tok.word.strip()
    if not w or '*' in w:
        continue
    try:
        analysis = morph.atomize(w)
        for ch, role, gl in analysis.atoms:
            a_atom_counts[ch] += 1
    except Exception:
        pass

for tok in b_toks:
    w = tok.word.strip()
    if not w or '*' in w:
        continue
    try:
        analysis = morph.atomize(w)
        for ch, role, gl in analysis.atoms:
            b_atom_counts[ch] += 1
    except Exception:
        pass

total_a = sum(a_atom_counts.values())
total_b = sum(b_atom_counts.values())

def enrichment_ratio(atom):
    """B/A frequency ratio for an atom. >1 = B-enriched, <1 = A-enriched."""
    a_rate = a_atom_counts[atom] / total_a if total_a else 0
    b_rate = b_atom_counts[atom] / total_b if total_b else 0
    return b_rate / a_rate if a_rate > 0 else float('inf')

# Pre-compute enrichment for target atoms
ENRICHMENT = {atom: enrichment_ratio(atom) for atom in 'docps'}

# ================================================================
# CANDIDATE DEFINITIONS
# ================================================================
CANDIDATES = {
    'd': ['mark', 'do/execute', 'product/yield', 'complete'],
    'o': ['arrange', 'work', 'configure', 'organize'],
    'c': ['adjust', 'classify/sort', 'check', 'correct'],
    'p': ['pause', 'specify/note', 'prepare', 'stage'],
    's': ['sequence', 'order', 'separate', 'step'],
}

# ================================================================
# LOCKED glosses for reference
# ================================================================
LOCKED = {
    'k': 'heat', 'e': 'cool', 'h': 'watch', 'y': 'end',
    'i': 'iterate', 'n': 'bind', 'a': 'into', 'm': 'final',
    't': 'transfer', 'l': 'state', 'r': 'respond', 'f': 'flag',
}

# ================================================================
# COMPOUND GLOSSES from middle dictionary (manually confirmed entries)
# ================================================================
KNOWN_COMPOUNDS = {
    # d-compounds
    'ed': 'discharge', 'od': 'collect', 'edy': 'batch',
    'ked': 'release', 'keed': 'vent', 'eod': 'stand',
    # o-compounds
    'ol': 'continue', 'or': 'portion', 'ok': 'seal',
    'op': 'start', 'eo': 'open',
    # c-compounds
    'ck': 'hard', 'ct': 'control', 'ch': 'check',
    'kch': 'pulse', 'ech': 'check',
    # p-compounds
    'cp': 'adjust-pause', 'opch': 'operate', 'ep': 'cool-pause',
    # s-compounds
    'so': 'sequence-work', 'sa': 'sequence-yield', 'os': 'work-sequence',
    'es': 'cool-sequence',
}

# ================================================================
# AXIS 1: Category Shift Match
# ================================================================
# C1394 T6 measured shifts:
#   d: +55.6% OPERATION
#   c: +30.1% MARKING
#   p: +45.6% MARKING
#   s: boosts MONITORING/STAGING (weakest modifier)
#   o: not a MOD (it's a HEAD) -- HEAD-level: 35% STAGING is primary
#
# For each candidate, predict what category it SHOULD push toward,
# then compare to measured shift.

def axis1_category_shift(atom, gloss):
    """Score: 2=MATCH, 1=PARTIAL, 0=MISMATCH."""

    # Measured category shifts from C1394 T6
    measured = {
        'd': 'OPERATION',    # +55.6% OPERATION
        'o': 'STAGING',      # HEAD: 35% STAGING primary, but also diverse
        'c': 'MARKING',      # +30.1% MARKING
        'p': 'MARKING',      # +45.6% MARKING
        's': 'MONITORING',   # boosts MONITORING/STAGING (weakest modifier)
    }

    # Predicted category for each candidate gloss
    # What category would this gloss PUSH tokens toward?
    predictions = {
        # d candidates
        'mark':           'MARKING',      # marking/labeling -> MARKING
        'do/execute':     'OPERATION',    # doing things -> OPERATION
        'product/yield':  'TRANSITION',   # yielding output -> TRANSITION
        'complete':       'TRANSITION',   # completing -> TRANSITION

        # o candidates
        'arrange':        'STAGING',      # arranging -> STAGING
        'work':           'OPERATION',    # working -> OPERATION
        'configure':      'STAGING',      # configuring -> STAGING
        'organize':       'STAGING',      # organizing -> STAGING

        # c candidates
        'adjust':         'MARKING',      # adjusting -> (could be OPERATION, but current system maps it MARKING)
        'classify/sort':  'MARKING',      # classifying -> MARKING (labeling/categorizing)
        'check':          'MONITORING',   # checking -> MONITORING
        'correct':        'OPERATION',    # correcting -> OPERATION (active fix)

        # p candidates
        'pause':          'MARKING',      # pausing -> MARKING (annotation of a stop)
        'specify/note':   'MARKING',      # noting -> MARKING
        'prepare':        'STAGING',      # preparing -> STAGING
        'stage':          'STAGING',      # staging -> STAGING

        # s candidates
        'sequence':       'STAGING',      # sequencing -> STAGING
        'order':          'STAGING',      # ordering -> STAGING
        'separate':       'OPERATION',    # separating -> OPERATION (physical action)
        'step':           'STAGING',      # stepping -> STAGING
    }

    target = measured[atom]
    pred = predictions.get(gloss, 'UNKNOWN')

    if pred == target:
        return 2
    # Partial matches: related categories
    partials = {
        ('STAGING', 'MONITORING'): True,  # both are non-action oversight
        ('MONITORING', 'STAGING'): True,
        ('OPERATION', 'MARKING'): True,   # both involve "doing" in broad sense
        ('MARKING', 'OPERATION'): True,
        ('TRANSITION', 'OPERATION'): True, # completing is adjacent to doing
        ('OPERATION', 'TRANSITION'): True,
    }
    if (pred, target) in partials:
        return 1
    return 0


# ================================================================
# AXIS 2: Scope Consistency (modifier stacking position)
# ================================================================
# C1472 best-fit ordering: p->f->c->s->d->i
# C1394 mean positions: p=0.225, f=0.395, i=0.519, c=0.532, d=0.696, s=0.713
# C1472 refined: p=0.261, f=0.408, c=0.508, i=0.532, d=0.589, s=0.631
#
# Outermost (early) = wrapper/annotation meanings
# Innermost (late) = direct modification of HEAD meaning
# o is a HEAD, not a modifier -- evaluate as domain-setter

def axis2_scope_consistency(atom, gloss):
    """Score: 2=YES, 1=MAYBE, 0=NO."""

    # Position data (C1472, 0=outermost, 1=innermost)
    positions = {
        'p': 0.261,  # outermost modifier
        'c': 0.508,  # middle modifier
        'd': 0.589,  # late modifier (near HEAD)
        's': 0.631,  # latest modifier (closest to HEAD)
        'o': None,   # HEAD, not modifier
    }

    pos = positions[atom]

    if atom == 'o':
        # o is a HEAD -- domain setter. Evaluate: does the gloss make sense
        # as a domain that other atoms modify?
        domain_glosses = {
            'arrange': 2,     # "arranging" is a domain others can modify -> YES
            'work': 2,        # "working" is a broad domain -> YES
            'configure': 2,   # "configuring" is a domain -> YES
            'organize': 2,    # "organizing" is a domain -> YES
        }
        return domain_glosses.get(gloss, 1)

    if atom == 'p':
        # p is OUTERMOST (pos 0.261). Should be a wrapper/annotation meaning.
        # Wrapper = something that frames the operation, doesn't change its core.
        wrapper_score = {
            'pause': 2,          # pausing wraps an operation (do X, but pause) -> YES
            'specify/note': 2,   # noting/specifying wraps (add annotation to operation) -> YES
            'prepare': 1,        # preparing is more of an action than wrapper -> MAYBE
            'stage': 1,          # staging is preparatory but also directly modifies -> MAYBE
        }
        return wrapper_score.get(gloss, 1)

    if atom == 'c':
        # c is MIDDLE (pos 0.508). Should be a mid-level modification.
        # Not a pure wrapper, not direct HEAD modification.
        mid_score = {
            'adjust': 2,          # adjusting is exactly mid-level modification -> YES
            'classify/sort': 1,   # classifying is more of a wrapper (annotation) -> MAYBE
            'check': 1,           # checking is more of a wrapper (monitoring) -> MAYBE
            'correct': 2,         # correcting is active mid-level modification -> YES
        }
        return mid_score.get(gloss, 1)

    if atom == 'd':
        # d is LATE (pos 0.589). Should directly modify the HEAD's action.
        # Late = close to the action, not wrapping it.
        late_score = {
            'mark': 0,           # marking is annotation/wrapper, NOT direct modification -> NO
            'do/execute': 2,     # executing directly modifies the action -> YES
            'product/yield': 1,  # yielding is somewhat direct but also output-focused -> MAYBE
            'complete': 2,       # completing directly closes the action -> YES
        }
        return late_score.get(gloss, 1)

    if atom == 's':
        # s is LATEST (pos 0.631). Should be the most direct modification of HEAD.
        # Closest to core action.
        latest_score = {
            'sequence': 1,    # sequencing structures the action but at arms-length -> MAYBE
            'order': 1,       # ordering similarly -> MAYBE
            'separate': 2,    # separating directly modifies what HEAD does -> YES
            'step': 2,        # stepping directly modifies HEAD execution -> YES
        }
        return latest_score.get(gloss, 1)

    return 1


# ================================================================
# AXIS 3: Terminal Selectivity
# ================================================================
# C1484:
#   y selects ONLY d (d=2.868x, all others <0.03x)
#   h selects {c, p, f, s} (c=9.1x, p=7.7x, f=6.4x, s=5.0x; d and i excluded at 0.1x)
#   n selects ONLY i
#   l/r/m resist modification entirely
#
# Question: does the gloss EXPLAIN the selectivity pattern?
#   y="end" selects d because... [candidate] things have natural endpoints?
#   h="watch" selects c,p,f,s but NOT d because... [candidate] doesn't benefit from monitoring?

def axis3_terminal_selectivity(atom, gloss):
    """Score: 2=YES, 1=MAYBE, 0=NO."""

    if atom == 'd':
        # d is EXCLUSIVELY selected by y-terminal (y="end").
        # d is EXCLUDED by h-terminal (h="watch", d at 0.1x).
        # Why would "end" want this atom but "watch" reject it?
        scores = {
            'mark':           1,  # marking+end: marks have endpoints, sure. But why would
                                  # "watch" reject marking? Marking IS something you'd monitor.
                                  # Weak: MAYBE.
            'do/execute':     2,  # execute+end: executions naturally end. Watch rejects execute
                                  # because execution is a one-shot action, not something you
                                  # monitor over time. STRONG: YES.
            'product/yield':  1,  # product+end: products have endpoints (done producing).
                                  # But watch should like products (monitor quality). MAYBE.
            'complete':       0,  # complete+end: TAUTOLOGICAL (complete=end). Also, why would
                                  # watch reject completion? You DO watch for completion. NO.
        }
        return scores.get(gloss, 1)

    if atom == 'o':
        # o is a HEAD, not a modifier, so terminal selectivity doesn't apply
        # in the same way. But o-HEAD tokens have terminal distribution:
        # o→l (98.1% STAGING), o→r (~99% FLOW). o strongly selects l and r.
        # Does the gloss explain why o pairs with l="state" and r="respond"?
        scores = {
            'arrange':   2,  # arrange+state=arranging states, arrange+respond=portion/flow.
                             # Arrangement naturally produces states or responds. YES.
            'work':      1,  # work+state=working states(?), work+respond=work-respond.
                             # "work" is too generic to explain l/r selectivity. MAYBE.
            'configure': 2,  # configure+state=configured states, configure+respond=config-flow.
                             # Configuration produces states. YES.
            'organize':  1,  # organize+state=organized states. OK but "organize" and "arrange"
                             # are near-synonyms, and organize doesn't add discrimination. MAYBE.
        }
        return scores.get(gloss, 1)

    if atom == 'c':
        # c is selected by h-terminal (h="watch", c=9.1x enrichment).
        # c is in h's exclusive pool {c, p, f, s}.
        # c does NOT pair with y ("end") or n ("bind").
        # Why would "watch" want this atom?
        scores = {
            'adjust':         2,  # adjust+watch: you watch while adjusting, iterative tuning.
                                  # This is exactly what a monitoring terminal wants. YES.
            'classify/sort':  1,  # classify+watch: monitor while classifying? Less natural.
                                  # Classification is a discrete action, not monitored. MAYBE.
            'check':          0,  # check+watch: TAUTOLOGICAL. Checking IS watching.
                                  # h="watch" selects c because c="check"="watch"? Circular. NO.
            'correct':        2,  # correct+watch: watch while correcting, monitor the fix.
                                  # Correction requires ongoing monitoring. YES.
        }
        return scores.get(gloss, 1)

    if atom == 'p':
        # p is selected by h-terminal (h="watch", p=7.7x enrichment).
        # p is in h's exclusive pool {c, p, f, s}.
        # p does NOT pair with y ("end") or n ("bind").
        # Why would "watch" want p?
        scores = {
            'pause':          2,  # pause+watch: watch during a pause, monitor the waiting period.
                                  # Pausing IS something you monitor (is it ready yet?). YES.
            'specify/note':   1,  # specify+watch: watch while specifying? Less natural.
                                  # Specification is a discrete act. MAYBE.
            'prepare':        2,  # prepare+watch: monitor preparation. Natural -- watch while
                                  # things are being set up. YES.
            'stage':          2,  # stage+watch: monitor staging. Same logic. YES.
        }
        return scores.get(gloss, 1)

    if atom == 's':
        # s is selected by h-terminal (h="watch", s=5.0x enrichment).
        # s is in h's exclusive pool {c, p, f, s}.
        # s does NOT pair with y ("end") or n ("bind").
        # Why would "watch" want s?
        scores = {
            'sequence':  2,  # sequence+watch: monitor the sequence, watch ordering.
                             # Sequences need monitoring (is the order right?). YES.
            'order':     2,  # order+watch: monitor ordering. Same logic. YES.
            'separate':  1,  # separate+watch: watch separation? Possible but separation
                             # is a physical action, not something you inherently monitor. MAYBE.
            'step':      2,  # step+watch: monitor each step. Very natural. YES.
        }
        return scores.get(gloss, 1)

    return 1


# ================================================================
# AXIS 4: Tautology Check
# ================================================================
# Check if atom + its primary terminal produces semantic redundancy.
# d+y: d+end. If d="complete" then dy="complete+end" = TAUTOLOGICAL.
# c+h: c+watch. If c="check" then ch="check+watch" = TAUTOLOGICAL.
# p+h: p+watch. Score for each.

def axis4_tautology(atom, gloss):
    """Score: 2=NOT tautological, 1=MILD redundancy, 0=TAUTOLOGICAL."""

    if atom == 'd':
        # d's primary terminal is y ("end"). dy is hard-fused (C1394 T2).
        # Also check: d+h should NOT be tautological (d excluded from h).
        scores = {
            'mark':           2,  # mark+end = "marking done" -> distinct meanings. NOT taut.
            'do/execute':     2,  # execute+end = "execution done" -> distinct. NOT taut.
            'product/yield':  1,  # yield+end = "yielded" -> mild. Yielding implies near-end. MILD.
            'complete':       0,  # complete+end = same thing twice. TAUTOLOGICAL.
        }
        return scores.get(gloss, 1)

    if atom == 'o':
        # o's primary terminals are l ("state") and r ("respond").
        # ol = "continue" (STAGING), or = "portion" (FLOW)
        scores = {
            'arrange':   2,  # arrange+state="arranged state", arrange+respond="portion". DISTINCT.
            'work':      1,  # work+state="work state"? Mild. Work implies a state of working. MILD.
            'configure': 2,  # configure+state="configured state". DISTINCT.
            'organize':  2,  # organize+state="organized state". DISTINCT.
        }
        return scores.get(gloss, 1)

    if atom == 'c':
        # c's primary terminal is h ("watch"). ch = "check" (known gloss).
        # Also: c+k (ck = "hard"), c+t (ct = "control")
        scores = {
            'adjust':         2,  # adjust+watch="adjust while watching". DISTINCT.
            'classify/sort':  2,  # classify+watch="classify while watching". DISTINCT.
            'check':          0,  # check+watch="check while watching". CHECK IS WATCHING.
                                  # TAUTOLOGICAL. The compound ch is glossed "check" --
                                  # if c itself means "check", ch = "check+watch" = redundant.
            'correct':        2,  # correct+watch="correct while watching". DISTINCT.
        }
        return scores.get(gloss, 1)

    if atom == 'p':
        # p's primary terminal is h ("watch"). cp = "adjust-pause" compound.
        # Also p appears in opch = "operate"
        scores = {
            'pause':          2,  # pause+watch="pause while watching". DISTINCT (different actions).
            'specify/note':   2,  # note+watch="note while watching". DISTINCT.
            'prepare':        2,  # prepare+watch="prepare while watching". DISTINCT.
            'stage':          1,  # stage+watch="stage while watching". Staging implies waiting
                                  # which is close to watching. MILD redundancy.
        }
        return scores.get(gloss, 1)

    if atom == 's':
        # s's primary terminal is h ("watch"). s also appears with a,o,d.
        scores = {
            'sequence':  2,  # sequence+watch="sequence while watching". DISTINCT.
            'order':     2,  # order+watch="order while watching". DISTINCT.
            'separate':  2,  # separate+watch="separate while watching". DISTINCT.
            'step':      1,  # step+watch="step while watching". Stepping through IS a form
                             # of watching/monitoring. MILD redundancy.
        }
        return scores.get(gloss, 1)

    return 1


# ================================================================
# AXIS 5: Cross-System Deployment
# ================================================================
# C1503, C1507, C1514:
#   B-enriched atoms should have ACTION/VERB glosses (execution)
#   A-enriched atoms should have PROPERTY/STATE/ARRANGEMENT glosses (description)
#   Neutral atoms: either is OK
#
# Measured enrichment (B/A ratio):
#   d: 2.110 -> STRONGLY B-ENRICHED -> should be action/verb
#   o: 0.419 -> STRONGLY A-ENRICHED -> should be state/arrangement
#   c: 0.687 -> A-ENRICHED -> should be state/property
#   p: 0.962 -> NEUTRAL -> either OK
#   s: 0.567 -> A-ENRICHED -> should be state/arrangement

def axis5_cross_system(atom, gloss):
    """Score: 2=MATCHES, 1=NEUTRAL, 0=CONTRADICTS."""

    # Classification of each gloss as ACTION (verb) or STATE (property/arrangement)
    gloss_type = {
        # d candidates
        'mark':           'ACTION',     # marking is doing something
        'do/execute':     'ACTION',     # obvious action
        'product/yield':  'STATE',      # a product is a noun/state
        'complete':       'ACTION',     # completing is an action

        # o candidates
        'arrange':        'STATE',      # arrangement is a configuration/state
        'work':           'ACTION',     # working is an action
        'configure':      'STATE',      # configuration is a state
        'organize':       'STATE',      # organization is a state

        # c candidates
        'adjust':         'ACTION',     # adjusting is an action
        'classify/sort':  'STATE',      # classification is a property assignment
        'check':          'ACTION',     # checking is an action
        'correct':        'ACTION',     # correcting is an action

        # p candidates
        'pause':          'STATE',      # pause is a state (not moving)
        'specify/note':   'STATE',      # specification is a property
        'prepare':        'ACTION',     # preparing is an action
        'stage':          'STATE',      # staging is a state/arrangement

        # s candidates
        'sequence':       'STATE',      # sequence is an arrangement
        'order':          'STATE',      # order is an arrangement
        'separate':       'ACTION',     # separating is an action
        'step':           'ACTION',     # stepping is an action
    }

    # What the enrichment predicts
    enrichment_prediction = {
        'd': 'ACTION',   # B-enriched (2.110) -> ACTION
        'o': 'STATE',    # A-enriched (0.419) -> STATE
        'c': 'STATE',    # A-enriched (0.687) -> STATE
        'p': 'EITHER',   # Neutral (0.962) -> either
        's': 'STATE',    # A-enriched (0.567) -> STATE
    }

    gt = gloss_type.get(gloss, 'UNKNOWN')
    pred = enrichment_prediction[atom]

    if pred == 'EITHER':
        return 1  # Neutral enrichment, any gloss type is fine
    if gt == pred:
        return 2  # Matches enrichment
    return 0      # Contradicts enrichment


# ================================================================
# AXIS 6: Compound Semantic Coherence
# ================================================================
# For each atom, check the TOP 5 compound glosses from the middle dictionary.
# Read each compound as candidate_gloss(atom1) + LOCKED_gloss(atom2).
# Score: ALL coherent=2, MOST coherent=1, SOME incoherent=0.

def axis6_compound_coherence(atom, gloss):
    """Score: 2=ALL coherent, 1=MOST coherent, 0=SOME incoherent."""

    # For each atom, define the key compounds and what they're glossed as.
    # Then check: does candidate_gloss + partner_gloss => compound_gloss make sense?

    if atom == 'd':
        # Key compounds:
        # ed = "discharge" -> e(cool) + d(?) = discharge
        # od = "collect"   -> o(?) + d(?) = collect
        # edy = "batch"    -> e(cool) + d(?) + y(end) = batch/cycle-done
        # ked = "release"  -> k(heat) + e(cool) + d(?) = release
        # eod = "stand"    -> e(cool) + o(?) + d(?) = stand/hold

        tests = {
            'mark': {
                'ed':  ('cool+mark=discharge?', True),   # cool marking = discharge is a stretch but OK
                'od':  ('arrange+mark=collect?', True),   # arrange+mark = collect? Marking what you arranged = gathering. OK.
                'edy': ('cool+mark+end=batch?', True),    # cool marking done = batch. Mark implies "done/noted". Plausible.
                'ked': ('heat+cool+mark=release?', False), # heat, cool, then mark = release? Mark doesn't help. INCOHERENT.
                'eod': ('cool+arrange+mark=stand?', False),# cool, arrange, mark = stand? Mark is irrelevant. INCOHERENT.
            },
            'do/execute': {
                'ed':  ('cool+execute=discharge?', True),  # cool+execute = discharge. Execute the cooling = release. YES.
                'od':  ('arrange+execute=collect?', True),  # arrange+execute = collect. Execute the arrangement. YES.
                'edy': ('cool+execute+end=batch?', True),   # cool+execute+end = batch-done. YES.
                'ked': ('heat+cool+execute=release?', True),# heat, cool, execute = release (execute the heat-cool). YES.
                'eod': ('cool+arrange+execute=stand?', True),# cool+arrange+execute = stand (execute the arrangement). OK.
            },
            'product/yield': {
                'ed':  ('cool+product=discharge?', True),   # cooling product = discharge. YES (discharge is what cooling yields).
                'od':  ('arrange+product=collect?', True),   # arrangement product = collection. YES.
                'edy': ('cool+product+end=batch?', True),    # cooling product done = batch. YES.
                'ked': ('heat+cool+product=release?', True), # heat+cool product = release. OK.
                'eod': ('cool+arrange+product=stand?', False),# cool+arrange product = stand? Product doesn't explain "stand". NO.
            },
            'complete': {
                'ed':  ('cool+complete=discharge?', True),  # cool+complete = discharge? Completing cooling = discharge. OK.
                'od':  ('arrange+complete=collect?', True),  # arrange+complete = collection done. OK.
                'edy': ('cool+complete+end=batch?', False),  # cool+complete+end = TRIPLE closure. Redundant with y=end. NO.
                'ked': ('heat+cool+complete=release?', True),# heat+cool complete = release. OK.
                'eod': ('cool+arrange+complete=stand?', True),# cool+arrange complete = standing. OK.
            },
        }

        return _score_compounds(gloss, tests)

    if atom == 'o':
        # Key compounds:
        # ol = "continue" -> o(?) + l(state) = continue/staging
        # or = "portion"  -> o(?) + r(respond) = portion/flow
        # ok = "seal"     -> o(?) + k(heat) = seal
        # op = "start"    -> o(?) + p(?) = start/transition
        # eo = "open"     -> e(cool) + o(?) = open

        tests = {
            'arrange': {
                'ol': ('arrange+state=continue?', True),    # arranged state = continuation. YES.
                'or': ('arrange+respond=portion?', True),   # arrange+respond = portion out. YES.
                'ok': ('arrange+heat=seal?', True),         # arrange heat = seal (heat arrangement). YES.
                'op': ('arrange+pause=start?', True),       # arrange+pause = start (pause to arrange before starting). OK.
                'eo': ('cool+arrange=open?', True),         # cool+arrange = open (arrange cooling = open). YES.
            },
            'work': {
                'ol': ('work+state=continue?', True),       # work state = continue working. OK.
                'or': ('work+respond=portion?', True),      # work+respond = portion. OK.
                'ok': ('work+heat=seal?', False),           # work+heat = seal? Working with heat doesn't mean sealing. NO.
                'op': ('work+pause=start?', False),         # work+pause = start? Opposite. Pausing work = start? NO.
                'eo': ('cool+work=open?', False),           # cool+work = open? Cool working doesn't mean opening. NO.
            },
            'configure': {
                'ol': ('configure+state=continue?', True),  # configured state = continuation. YES.
                'or': ('configure+respond=portion?', True), # configure+respond = portion. OK.
                'ok': ('configure+heat=seal?', True),       # configure heat = seal (set up heat for sealing). YES.
                'op': ('configure+pause=start?', True),     # configure+pause = start (configure pause before starting). OK.
                'eo': ('cool+configure=open?', True),       # cool+configure = open (configure cooling = open). YES.
            },
            'organize': {
                'ol': ('organize+state=continue?', True),   # organized state = continuation. YES.
                'or': ('organize+respond=portion?', True),  # organize+respond = portion out. YES.
                'ok': ('organize+heat=seal?', True),        # organize heat = seal. YES.
                'op': ('organize+pause=start?', True),      # organize+pause = start. OK.
                'eo': ('cool+organize=open?', False),       # cool+organize = open? Organizing doesn't imply opening. NO.
            },
        }

        return _score_compounds(gloss, tests)

    if atom == 'c':
        # Key compounds:
        # ck = "hard"    -> c(?) + k(heat) = hard
        # ct = "control" -> c(?) + t(transfer) = control
        # ch = "check"   -> c(?) + h(watch) = check
        # kch = "pulse"  -> k(heat) + c(?) + h(watch) = pulse
        # ech = "check"  -> e(cool) + c(?) + h(watch) = check

        tests = {
            'adjust': {
                'ck':  ('adjust+heat=hard?', True),         # adjust heat = hard (heat adjustment = hardening). YES.
                'ct':  ('adjust+transfer=control?', True),  # adjust transfer = control. YES.
                'ch':  ('adjust+watch=check?', True),       # adjust+watch = check. YES (checking = watching + adjusting).
                'kch': ('heat+adjust+watch=pulse?', True),  # heat+adjust+watch = pulse (adjust heat monitoring). YES.
                'ech': ('cool+adjust+watch=check?', True),  # cool+adjust+watch = check. YES.
            },
            'classify/sort': {
                'ck':  ('classify+heat=hard?', False),      # classify heat = hard? Sorting heat doesn't mean hardening. NO.
                'ct':  ('classify+transfer=control?', True), # classify transfer = control? Sorting transfers = control. OK.
                'ch':  ('classify+watch=check?', True),     # classify+watch = check. OK.
                'kch': ('heat+classify+watch=pulse?', False),# heat+classify+watch = pulse? Classifying heat =/= pulsing. NO.
                'ech': ('cool+classify+watch=check?', True), # cool+classify+watch = check. OK.
            },
            'check': {
                'ck':  ('check+heat=hard?', False),          # check heat = hard? Checking heat =/= hardening. NO.
                'ct':  ('check+transfer=control?', True),    # check transfer = control. YES.
                'ch':  ('check+watch=check?', True),         # TAUTOLOGICAL but still "coherent" as a compound. MILD.
                'kch': ('heat+check+watch=pulse?', False),   # heat+check+watch = pulse? Checking =/= pulsing. NO.
                'ech': ('cool+check+watch=check?', True),    # TAUTOLOGICAL again.
            },
            'correct': {
                'ck':  ('correct+heat=hard?', True),         # correct heat = hard. Correcting heat = hardening process. OK.
                'ct':  ('correct+transfer=control?', True),  # correct transfer = control. YES.
                'ch':  ('correct+watch=check?', True),       # correct+watch = check. YES.
                'kch': ('heat+correct+watch=pulse?', True),  # heat+correct+watch = pulse (correct heat monitoring). OK.
                'ech': ('cool+correct+watch=check?', True),  # cool+correct+watch = check. YES.
            },
        }

        return _score_compounds(gloss, tests)

    if atom == 'p':
        # Key compounds:
        # op = "start"       -> o(arrange) + p(?) = start
        # cp = "adjust-pause" -> c(adjust) + p(?) = adjust-pause
        # opch = "operate"   -> o(arrange) + p(?) + c(adjust) + h(watch) = operate
        # ep = "cool-pause"  -> e(cool) + p(?) = cool-pause
        # pd = "pause-mark"  -> p(?) + d(?) = pause-mark (2 tokens only)

        tests = {
            'pause': {
                'op':   ('arrange+pause=start?', True),      # arrange then pause = start (pause before beginning). YES.
                'cp':   ('adjust+pause=adjust-pause?', True), # adjust+pause. Literally matches. YES.
                'opch': ('arrange+pause+adjust+watch=operate?', True), # arrange, pause, adjust, watch = operate. YES.
                'ep':   ('cool+pause=cool-pause?', True),    # Matches. YES.
                'pd':   ('pause+mark=pause-mark?', True),    # Matches. YES.
            },
            'specify/note': {
                'op':   ('arrange+specify=start?', True),    # arrange+specify = start (specify the arrangement). OK.
                'cp':   ('adjust+specify=adjust-note?', True),# adjust+specify. OK.
                'opch': ('arrange+specify+adjust+watch=operate?', True), # specify within operation. OK.
                'ep':   ('cool+specify=cool-note?', True),   # cool+specify. OK.
                'pd':   ('specify+mark=note-mark?', False),  # specify+mark = note+mark. REDUNDANT. Specify IS noting/marking. NO.
            },
            'prepare': {
                'op':   ('arrange+prepare=start?', True),    # arrange+prepare = start. YES.
                'cp':   ('adjust+prepare=adjust-prepare?', True), # adjust+prepare. OK.
                'opch': ('arrange+prepare+adjust+watch=operate?', True), # prepare within operation. YES.
                'ep':   ('cool+prepare=cool-prepare?', True),# cool+prepare. OK.
                'pd':   ('prepare+mark=prepare-mark?', True),# prepare+mark. OK.
            },
            'stage': {
                'op':   ('arrange+stage=start?', True),      # arrange+stage = start. YES.
                'cp':   ('adjust+stage=adjust-stage?', True),# adjust+stage. OK.
                'opch': ('arrange+stage+adjust+watch=operate?', True), # stage within operation. YES.
                'ep':   ('cool+stage=cool-stage?', True),    # cool+stage. OK.
                'pd':   ('stage+mark=stage-mark?', True),    # stage+mark. OK.
            },
        }

        return _score_compounds(gloss, tests)

    if atom == 's':
        # Key compounds:
        # so = "sequence-work" -> s(?) + o(arrange) = sequence-work (3 tokens)
        # sa = "sequence-yield" -> s(?) + a(into) = sequence-yield (3 tokens)
        # os = "work-sequence" -> o(arrange) + s(?) = work-sequence (16 tokens)
        # es = "cool-sequence" -> e(cool) + s(?) = cool-sequence (14 tokens)
        # sd = "sequence-mark" -> s(?) + d(?) = sequence-mark (3 tokens)

        tests = {
            'sequence': {
                'so': ('sequence+arrange=sequence-work?', True),   # sequence+arrange. Direct match. YES.
                'sa': ('sequence+into=sequence-yield?', True),     # sequence+into. OK.
                'os': ('arrange+sequence=work-sequence?', True),   # arrange+sequence. Direct match. YES.
                'es': ('cool+sequence=cool-sequence?', True),      # cool+sequence. Direct match. YES.
                'sd': ('sequence+mark=sequence-mark?', True),      # sequence+mark. Direct match. YES.
            },
            'order': {
                'so': ('order+arrange=order-work?', True),         # order+arrange. OK.
                'sa': ('order+into=order-yield?', True),           # order+into. OK.
                'os': ('arrange+order=work-order?', True),         # arrange+order. OK.
                'es': ('cool+order=cool-order?', True),            # cool+order. OK.
                'sd': ('order+mark=order-mark?', True),            # order+mark. OK.
            },
            'separate': {
                'so': ('separate+arrange=separate-work?', True),   # separate+arrange. OK.
                'sa': ('separate+into=separate-yield?', True),     # separate+into. OK.
                'os': ('arrange+separate=work-separate?', True),   # arrange+separate. OK.
                'es': ('cool+separate=cool-separate?', True),      # cool+separate = distillation! YES.
                'sd': ('separate+mark=separate-mark?', True),      # separate+mark. OK.
            },
            'step': {
                'so': ('step+arrange=step-work?', True),           # step+arrange. OK.
                'sa': ('step+into=step-yield?', True),             # step+into. OK.
                'os': ('arrange+step=work-step?', True),           # arrange+step. OK.
                'es': ('cool+step=cool-step?', True),              # cool+step. OK.
                'sd': ('step+mark=step-mark?', True),              # step+mark. OK.
            },
        }

        return _score_compounds(gloss, tests)

    return 1


def _score_compounds(gloss, tests):
    """Helper: score compound coherence from test dict."""
    if gloss not in tests:
        return 1
    results = tests[gloss]
    coherent = sum(1 for _, (_, ok) in results.items() if ok)
    total = len(results)
    if coherent == total:
        return 2
    elif coherent >= total - 1:
        return 1
    else:
        return 0


# ================================================================
# AXIS 7: Co-occurrence Avoidance
# ================================================================
# C1472: avoidance pairs (never co-occur in modifier slot):
#   c/i (0.40x), c/s (0.48x), i/s (0.52x), d/f (0.50x)
#   Also 8/15 pairs categorically absent: p-f, p-i, p-c, p-d, f-c, f-d, i-c, i-d
#
# If two atoms avoid each other, their glosses should be FUNCTIONALLY REDUNDANT
# (you don't need both in the same compound because they do similar things).

def axis7_co_occurrence(atom, gloss):
    """Score: 2=avoidance makes sense, 1=partially, 0=contradicts."""

    if atom == 'd':
        # d avoids: f(flag), i(iterate), p(all non-s), c(not noted but i-d is absent)
        # Key avoidance: d/f (0.50x). d and f avoid each other.
        # If d="X" and f="flag", are they functionally redundant?
        # Also: d never co-occurs with i (absent pair), p (absent pair).
        scores = {
            'mark':           2,  # mark/flag: YES redundant! Both are annotation/labeling actions.
                                  # d avoids f because mark~=flag. PERFECT FIT.
            'do/execute':     0,  # execute/flag: NOT redundant. Executing is action, flagging is annotation.
                                  # Why would "execute" avoid "flag"? No reason. CONTRADICTS.
            'product/yield':  1,  # product/flag: flagging a product? Not obviously redundant. PARTIAL.
            'complete':       1,  # complete/flag: flagging completion? Not obviously redundant. PARTIAL.
        }
        return scores.get(gloss, 1)

    if atom == 'o':
        # o is a HEAD, not a modifier. Modifier co-occurrence rules don't apply.
        # Give neutral score.
        return 1

    if atom == 'c':
        # c avoids: i(iterate), s(sequence), f(flag), d(mark), p(pause).
        # c has the MOST avoidance partners (co-occurs only with s somewhat, and barely with d).
        # Wait, C1472 says c/s = 0.48x (reduced but not zero), c/i = 0.40x (strong avoidance).
        # And 8 absent pairs include i-c and f-c.
        # Key: c avoids i. If c="X" and i="iterate", are they redundant?
        scores = {
            'adjust':         2,  # adjust/iterate: adjusting = iterative refinement. Redundant in that
                                  # adjusting implies repeated tries. Also adjust/flag: adjusting annotates.
                                  # c avoids all annotation atoms (f) and iteration atoms (i). YES.
            'classify/sort':  1,  # classify/iterate: classifying involves iterating through items.
                                  # Somewhat redundant. PARTIAL.
            'check':          1,  # check/iterate: checking involves iteration (check each thing).
                                  # But check/flag: checking =/= flagging. Mixed. PARTIAL.
            'correct':        1,  # correct/iterate: correcting involves iteration (try again).
                                  # correct/flag: correcting =/= flagging. Mixed. PARTIAL.
        }
        return scores.get(gloss, 1)

    if atom == 'p':
        # p avoids: f(flag), i(iterate), c(adjust), d(mark) -- avoids ALL except s.
        # p is the most isolated modifier.
        # Key: p avoids f(flag) and d(mark). If p="X" and f="flag" and d="mark",
        # is p redundant with BOTH flagging and marking?
        scores = {
            'pause':          2,  # pause/flag: pausing annotates a stop, flagging annotates danger.
                                  # Both are annotation actions. pause/mark: same. pause/iterate:
                                  # pausing stops iteration. p avoids everything because it's
                                  # a meta-operation that supersedes other modifications. YES.
            'specify/note':   2,  # specify/flag: noting and flagging are BOTH annotation. REDUNDANT.
                                  # specify/mark: noting and marking are BOTH annotation. REDUNDANT.
                                  # This explains why p avoids {f, d, c} -- all are annotation. YES.
            'prepare':        0,  # prepare/flag: preparing =/= flagging. NOT redundant.
                                  # prepare/mark: preparing =/= marking. NOT redundant.
                                  # Why would preparation avoid annotation? No reason. CONTRADICTS.
            'stage':          0,  # stage/flag: staging =/= flagging. NOT redundant.
                                  # stage/iterate: staging =/= iterating. NOT redundant.
                                  # Staging is an arrangement action, not annotation. CONTRADICTS.
        }
        return scores.get(gloss, 1)

    if atom == 's':
        # s avoids: c(adjust), i(iterate). c/s = 0.48x, i/s = 0.52x.
        # If s="X" and i="iterate" and c="adjust", is s redundant with both?
        scores = {
            'sequence':  2,  # sequence/iterate: sequencing IS a form of iteration (going through
                             # items in order). REDUNDANT. sequence/adjust: sequencing imposes
                             # order which is a form of adjustment. YES.
            'order':     2,  # order/iterate: ordering IS iterating through options. REDUNDANT.
                             # order/adjust: ordering adjusts arrangement. YES.
            'separate':  0,  # separate/iterate: separating =/= iterating. NOT redundant.
                             # separate/adjust: separating =/= adjusting. NOT redundant.
                             # Why would separation avoid iteration? No reason. CONTRADICTS.
            'step':      1,  # step/iterate: stepping IS iterating (step through = iterate through).
                             # VERY REDUNDANT. step/adjust: stepping =/= adjusting. Mixed. PARTIAL.
        }
        return scores.get(gloss, 1)

    return 1


# ================================================================
# SCORING ENGINE
# ================================================================

AXES = [
    ('Cat-Shift', axis1_category_shift),
    ('Scope', axis2_scope_consistency),
    ('Terminal', axis3_terminal_selectivity),
    ('Tautology', axis4_tautology),
    ('CrossSys', axis5_cross_system),
    ('Compounds', axis6_compound_coherence),
    ('CoOccur', axis7_co_occurrence),
]

def run_battery():
    """Run the full 7-axis battery for all 5 atoms."""

    results = {}

    for atom, candidates in CANDIDATES.items():
        print(f"\n{'='*80}")
        print(f"ATOM: {atom}  (current gloss: {ATOM_GLOSSES[atom]})")
        print(f"Enrichment B/A: {ENRICHMENT[atom]:.3f}  "
              f"({'B-enriched' if ENRICHMENT[atom] > 1.2 else 'A-enriched' if ENRICHMENT[atom] < 0.8 else 'neutral'})")
        print(f"{'='*80}")

        # Header
        header = f"{'Candidate':<20}"
        for name, _ in AXES:
            header += f" {name:>10}"
        header += f" {'TOTAL':>7}"
        print(header)
        print("-" * len(header))

        best_score = -1
        best_gloss = None
        all_scores = {}

        for gloss in candidates:
            row = f"{atom} = \"{gloss}\"".ljust(20)
            total = 0
            scores = {}
            for name, func in AXES:
                score = func(atom, gloss)
                scores[name] = score
                total += score
                row += f" {score:>10}"
            row += f" {total:>7}"
            all_scores[gloss] = (total, scores)
            print(row)

            if total > best_score:
                best_score = total
                best_gloss = gloss

        # Find margin of victory
        sorted_scores = sorted(all_scores.items(), key=lambda x: x[1][0], reverse=True)
        winner = sorted_scores[0]
        runner_up = sorted_scores[1] if len(sorted_scores) > 1 else (None, (0, {}))
        margin = winner[1][0] - runner_up[1][0]

        print()
        print(f"  WINNER: {atom} = \"{winner[0]}\" (score {winner[1][0]}/14)")
        print(f"  Runner-up: {atom} = \"{runner_up[0]}\" (score {runner_up[1][0]}/14)")
        print(f"  Margin of victory: {margin} points")

        # Report any HARD FAILS (score=0)
        for gloss, (total, scores) in all_scores.items():
            zeros = [name for name, s in scores.items() if s == 0]
            if zeros:
                print(f"  HARD FAILS for \"{gloss}\": {', '.join(zeros)}")

        results[atom] = {
            'winner': winner[0],
            'winner_score': winner[1][0],
            'runner_up': runner_up[0],
            'runner_up_score': runner_up[1][0],
            'margin': margin,
            'all_scores': {g: {'total': t, 'axes': s} for g, (t, s) in all_scores.items()},
        }

    # ================================================================
    # SUMMARY
    # ================================================================
    print(f"\n{'='*80}")
    print("DISCRIMINATION BATTERY SUMMARY")
    print(f"{'='*80}")
    print()
    print(f"{'Atom':<6} {'Current':<12} {'Winner':<16} {'Score':<8} {'Margin':<8} {'Verdict'}")
    print("-" * 70)

    for atom in 'docps':
        r = results[atom]
        current = ATOM_GLOSSES[atom]
        winner = r['winner']
        score = r['winner_score']
        margin = r['margin']

        if winner == current:
            verdict = "CONFIRMED"
        elif margin >= 4:
            verdict = "STRONG REPLACE"
        elif margin >= 2:
            verdict = "REPLACE"
        elif margin >= 1:
            verdict = "WEAK REPLACE"
        else:
            verdict = "TIE - KEEP CURRENT"

        print(f"{atom:<6} {current:<12} {winner:<16} {score:<8} {margin:<8} {verdict}")

    # ================================================================
    # DETAILED REASONING (axis-by-axis for winners)
    # ================================================================
    print(f"\n{'='*80}")
    print("DETAILED AXIS REASONING FOR WINNERS")
    print(f"{'='*80}")

    reasoning = {
        'd': {
            'do/execute': {
                'Cat-Shift': 'd shifts +55.6% OPERATION. "do/execute" -> OPERATION. EXACT MATCH.',
                'Scope': 'd is late modifier (pos 0.589). "execute" = direct action on HEAD. FITS late position.',
                'Terminal': 'y("end") exclusively selects d. Executions naturally end. h("watch") rejects d at 0.1x -- you don\'t watch an execution in progress, you watch preparations/adjustments.',
                'Tautology': 'd+y = "execute+end" = "execution complete". Two distinct concepts. NOT tautological.',
                'CrossSys': 'd is 2.11x B-enriched. B is execution system. "do/execute" is an action verb. PERFECT FIT.',
                'Compounds': 'ed="discharge" (cool+execute=discharge). od="collect" (arrange+execute=collect). edy="batch" (cool+execute+end). ked="release" (heat+cool+execute). ALL COHERENT.',
                'CoOccur': 'd avoids f("flag"). execute/flag are NOT redundant. CONTRADICTS. This is the ONE weakness.',
            },
            'mark': {
                'Cat-Shift': 'd shifts +55.6% OPERATION but "mark" -> MARKING. MISMATCH.',
                'CoOccur': 'd avoids f("flag"). mark/flag ARE redundant (both annotation). PERFECT FIT.',
            },
        },
        'o': {
            'arrange': {
                'Cat-Shift': 'o HEAD = 35% STAGING. "arrange" -> STAGING. MATCH.',
                'Terminal': 'o selects l("state") and r("respond"). arrange+state=continuation, arrange+respond=portioning. Both natural.',
                'CrossSys': 'o is 0.42x A-enriched. A is arrangement system (C1507). "arrange" is a state/property. PERFECT FIT.',
                'Compounds': 'ol="continue", or="portion", ok="seal", op="start", eo="open". ALL coherent with "arrange".',
            },
            'configure': {
                'Cat-Shift': '"configure" -> STAGING. Same as "arrange". Both match.',
                'Compounds': 'Nearly as coherent as "arrange" but eo="open" requires more stretch for "configure".',
            },
        },
        'c': {
            'adjust': {
                'Cat-Shift': 'c shifts +30.1% MARKING. "adjust" maps to MARKING in the system. MATCH.',
                'Scope': 'c is mid-position (0.508). "adjust" is exactly mid-level modification. FITS.',
                'Terminal': 'h("watch") selects c at 9.1x. You watch while adjusting. NATURAL.',
                'Tautology': 'c+h = "adjust+watch" = "check". Two distinct actions composing. NOT tautological.',
                'Compounds': 'ck="hard" (adjust+heat=hardening). ct="control" (adjust+transfer). ch="check". kch="pulse". ALL COHERENT.',
                'CoOccur': 'c avoids i("iterate"). Adjusting IS iterative refinement. REDUNDANT. c avoids f("flag"). Adjusting annotates. FITS.',
            },
            'check': {
                'Tautology': 'c+h = "check+watch". Check IS watching. TAUTOLOGICAL.',
                'Compounds': 'ck="hard" (check+heat=hard?). NO. kch="pulse" (heat+check+watch=pulse?). NO.',
            },
        },
        'p': {
            'pause': {
                'Cat-Shift': 'p shifts +45.6% MARKING. "pause" -> MARKING. MATCH.',
                'Scope': 'p is outermost modifier (0.261). Pausing wraps an operation. FITS wrapper position.',
                'Terminal': 'h("watch") selects p at 7.7x. Watch during a pause. NATURAL.',
                'Compounds': 'op="start" (arrange+pause=start). Pausing the arrangement initiates the next phase. ALL coherent.',
                'CoOccur': 'p avoids {f,i,c,d}. Pausing is a meta-annotation that supersedes other modifications. FITS isolation pattern.',
            },
            'specify/note': {
                'CoOccur': 'p avoids f("flag") and d("mark"). Noting/specifying IS flagging/marking. REDUNDANT. FITS.',
                'Compounds': 'pd="pause-mark" but if p="specify" then pd="specify+mark" = REDUNDANT compound. FAILS.',
            },
        },
        's': {
            'sequence': {
                'Cat-Shift': 's boosts MONITORING/STAGING. "sequence" -> STAGING. MATCH.',
                'Scope': 's is latest modifier (0.631). Sequencing directly structures the HEAD action.',
                'Terminal': 'h("watch") selects s at 5.0x. Monitor the sequence. NATURAL.',
                'Compounds': 'All 5 compounds are auto-glossed with "sequence". TRIVIALLY COHERENT.',
                'CoOccur': 's avoids i("iterate"). Sequencing IS iterating in order. REDUNDANT. s avoids c("adjust"). Sequencing adjusts order. FITS.',
            },
            'order': {
                'Cat-Shift': '"order" -> STAGING. Same match as "sequence".',
                'CoOccur': 'order/iterate also redundant. Same fit as "sequence".',
            },
        },
    }

    for atom in 'docps':
        r = results[atom]
        winner = r['winner']
        print(f"\n--- {atom} = \"{winner}\" ---")
        if atom in reasoning and winner in reasoning[atom]:
            for axis_name, reason in reasoning[atom][winner].items():
                print(f"  {axis_name}: {reason}")

    # ================================================================
    # SAVE RESULTS
    # ================================================================
    out_path = ROOT / 'phases' / 'ATOM_GLOSS_RECIPE_VALIDATION' / 'results' / 's1_discrimination_battery.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to {out_path}")

    return results


if __name__ == '__main__':
    run_battery()
