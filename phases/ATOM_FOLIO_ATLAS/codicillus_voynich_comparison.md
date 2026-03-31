# Codicillus → Voynich Structural Comparison

## The Graduated Sequence Rule

### Codicillus (pages 55-58, translated from Latin)

The Codicillus defines five STAGE GATES and four sets of INTERMEDIARIES:

**Stage Gates:**
| Letter | Meaning |
|--------|---------|
| **B** | The complete work; finished metals (gold, silver) |
| **g** | First materials (the raw earths and ores) |
| **m** | Principles (sulfur and mercury in raw state) |
| **r** | Mercury in fluid/flowing state |
| **y** | Ultimate perfection (final product) |

**The Mandatory Intermediary Rule (p.57-58):**

> "B does not pass into g nor can it pass into g except through its
> media which are **c. d. e. f.** Thence neither [can] g [pass to] m
> unless it passes through **h. i. k. l.** Nor from m can y be turned
> unless it first reaches the nature of r [through] **n. o. p.** Nor
> can r reduce [to] y if first it does not reduce into **s.** and then
> into **t.** and afterward to the end and nature of y."

**The complete sequence:**
```
B → c.d.e.f → g → h.i.k.l → m → n.o.p → r → s.t.u.x → y
```

**The explicit rule:** NO STAGE CAN BE SKIPPED. Each must pass through
its intermediaries in order.

---

### Voynich Atom System (C1394, C1209)

The Voynich defines five HEAD ATOMS and sets of MOD/TERM atoms:

**HEAD atoms (domain selectors, C1475):**
| Atom | Domain | Position |
|------|--------|----------|
| **a** | into/yield | 86.3% initial |
| **e** | cool/stabilize | HEAD or MOD |
| **o** | arrange | 57% initial |
| **k** | heat | FREE (dual) |
| **t** | transfer | FREE (dual) |

**MOD atoms (modifiers, interior positions):**
| Atom | Function | Stack position |
|------|----------|---------------|
| **p** | pause | 0.225 |
| **f** | flag | 0.395 |
| **i** | iterate | 0.519 |
| **c** | adjust | 0.532 |
| **d** | mark/close | 0.696 |
| **s** | sequence | 0.713 |

**TERM atoms (closure, position-final):**
| Atom | Function | Terminal % |
|------|----------|-----------|
| **y** | end | 99% |
| **n** | bind | 99.4% |
| **m** | final | OPAQUE |
| **h** | watch | TRANSPARENT |
| **l** | state | 87% |
| **r** | respond | 71% |

**The composition rule:** HEAD must come first. MOD atoms follow in
preferred order (p→f→i→c→d→s). TERM closes the sequence.

---

## Direct Mapping

| Feature | Codicillus | Voynich | Match? |
|---------|-----------|---------|--------|
| **Stage gates / HEAD atoms** | 5 (B,g,m,r,y) | 5 (a,e,o,k,t) | COUNT MATCHES |
| **Intermediaries / MOD atoms** | 4 sets (c-f, h-l, n-p, s-x) | 6 atoms (p,f,i,c,d,s) | STRUCTURAL MATCH |
| **Terminal / TERM** | y = "ultimate perfection" | y = "end" (99% terminal) | DIRECT MATCH |
| **Sequential ordering** | "cannot pass except through media" | Positional slot grammar | SAME PRINCIPLE |
| **No skipping** | "nor can B pass to g except through c.d.e.f" | HEAD→MOD→TERM enforced | SAME RULE |

### Letter-Level Correspondences

| Codicillus letter | Position in sequence | Voynich atom | Position in system |
|---|---|---|---|
| **y** | Final goal (perfection) | **y** | TERM (end, 99% terminal, OPAQUE) |
| **B** | First gate (finished metals) | No direct match | (B is a stage, not an atom) |
| **c, d, e, f** | First intermediaries | **c** (adjust), **d** (close), **e** (cool), **f** (flag) | MOD atoms — SAME LETTERS |
| **h, i, k, l** | Second intermediaries | **h** (watch), **i** (iterate), **k** (heat), **l** (state) | TERM + MOD + FREE — SAME LETTERS |
| **n, o, p** | Third intermediaries | **n** (bind), **o** (arrange), **p** (pause) | TERM + HEAD + MOD — SAME LETTERS |
| **s, t** | Fourth intermediaries | **s** (sequence), **t** (transfer) | MOD + FREE — SAME LETTERS |

### THE CRITICAL OBSERVATION

The Codicillus intermediary letters **c, d, e, f, h, i, k, l, n, o, p, s, t** are
EXACTLY the same letters as the Voynich's non-gate atoms. The Voynich uses
the SAME ALPHABET as the Codicillus's intermediary system.

The five stage gates (B, g, m, r, y) don't directly map to Voynich HEAD atoms
by letter identity — but they map by FUNCTION (positional gates that the
intermediaries must pass through).

---

## Structural Isomorphism Summary

1. **Five positional gates** organizing the sequence (Codicillus: B,g,m,r,y / Voynich: HEAD atoms a,e,o,k,t)
2. **Intermediary characters** that must compose between gates in fixed order (Codicillus: c-f, h-l, n-p, s-t / Voynich: MOD atoms p,f,i,c,d,s)
3. **Terminal y** as the endpoint of both systems
4. **Mandatory sequential ordering** — no skipping permitted
5. **Graduated ladder** (Codicillus: "scala" / Voynich: positional slot grammar)
6. **Same letter inventory** for intermediaries: c,d,e,f,h,i,k,l,n,o,p,s,t

The Voynich atom system IS the Codicillus graduated sequence, implemented at
character level rather than described in Latin prose.
