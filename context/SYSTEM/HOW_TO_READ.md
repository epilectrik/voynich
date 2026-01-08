# How to Read This Context System

**Purpose:** Navigation instructions for AI readers and human researchers.

---

## The Core Principle

> "Read the smallest file that answers your question. If insufficient, that file tells you where to expand next."

This system uses **progressive disclosure**. Never read all files at once.

---

## Reading Protocol

### Step 1: Start at CLAUDE_INDEX.md

This is the only file that should be read automatically. It contains:
- Project identity (3 sentences)
- Tier definitions (4-row table)
- Navigation table (where to find what)
- Stop conditions (what not to do)

**Token budget:** ~4,000 tokens

### Step 2: Follow Links as Needed

When you encounter something you need to know more about:
1. Check the navigation table in CLAUDE_INDEX.md
2. Read only the linked file
3. That file will have its own navigation pointers

**Don't read adjacent files "just in case."**

### Step 3: Stop When Sufficient

You have enough context when:
- You can answer the user's question
- You've found the relevant constraint
- You understand the tier and closure status

**Common mistake:** Reading all of ARCHITECTURE/ when you only needed one section.

---

## Directory Reading Order (If You Must Read Multiple)

If a task requires broad context, read in this order:

1. **CLAUDE_INDEX.md** (always first)
2. **CORE/** (Tier 0-1 facts) - only if checking fundamentals
3. **Relevant ARCHITECTURE/** file - only the system you're working with
4. **CLAIMS/INDEX.md** - only if looking up constraints
5. **Specific claim file** - only if you need full detail

**Never start with SPECULATIVE/**. It's optional context, not foundation.

---

## File Size Expectations

All files in this system are designed to stay under the 25k token READ limit:

| Category | Typical Size | Max Size |
|----------|--------------|----------|
| Index files | 2-4k tokens | 8k |
| Topic files | 4-8k tokens | 12k |
| Grouped registries | 8-12k tokens | 15k |
| Individual claims | 500-1k tokens | 2k |

If a file is approaching 15k tokens, it should be split.

---

## Cross-Reference Conventions

### Internal Links

Files link to each other using relative paths:
- `[CORE/frozen_conclusion.md](CORE/frozen_conclusion.md)` from index
- `[../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)` from subdirectory

### Constraint Citations

Format: `C###` or `Constraint ###`
- Find in `CLAIMS/INDEX.md` first
- Full details in individual file or grouped registry

### Phase Citations

Format: `Phase PHASE_NAME` or `phases/PHASE_NAME/`
- Find in `MAPS/phase_index.md`
- Full documentation in `phases/` directory

---

## Multi-Branch Access Patterns

When a question spans multiple domains, use the appropriate pattern:

### Pattern 1: Direct Parallel Read (2-3 files)

If you need 2-3 specific files, read them directly in parallel:

```
Example: "How does the grammar relate to HT?"
→ Read ARCHITECTURE/currier_B.md AND ARCHITECTURE/human_track.md in parallel
→ Synthesize after both complete
```

### Pattern 2: Agent Exploration (unknown scope)

If you don't know which files you need, spawn Explore agents:

```
Example: "What constraints relate to hazard avoidance?"
→ Spawn agent to search CLAIMS/
→ Agent returns relevant constraint numbers
→ Read specific files based on findings
```

### Pattern 3: Cross-Branch Synthesis (complex questions)

For questions spanning multiple branches with unknown depth:

```
Example: "How do Currier A, B, and AZC interact?"
→ Option A: Read ARCHITECTURE/cross_system.md first (it may be sufficient)
→ Option B: Spawn 3 agents to explore A, B, AZC independently
→ Combine agent findings
```

### Decision Guide

| Situation | Pattern |
|-----------|---------|
| Know exactly which 2-3 files | Direct parallel read |
| Need to search for relevant content | Agent exploration |
| Complex multi-domain synthesis | Read cross-reference file first, then agents if needed |
| Tier 0/1 fundamentals | Always read CORE/ directly |

### Combining Results

When synthesizing from multiple sources:
1. Note the **Tier** of each source (higher tier = less certain)
2. Note **closure status** (CLOSED = settled, OPEN = ongoing)
3. Cite specific **constraints** when combining claims
4. Don't mix Tier 2 structure with Tier 4 speculation as if equal

---

## Context-Sufficient Summaries

Some topics have **context-sufficient summary files** - short, authoritative documents that answer common questions without requiring further reading.

### Identifying Context-Sufficient Files

Look for:
- `**Context-Sufficient:** YES` at the top
- File names ending in `_CONTEXT_SUMMARY.md`
- Links marked with "(context-sufficient)" in referencing files

### Available Context-Sufficient Summaries

| Topic | File |
|-------|------|
| Human Track (HT) | [CLAIMS/HT_CONTEXT_SUMMARY.md](../CLAIMS/HT_CONTEXT_SUMMARY.md) |

### When to Use Them

Use these when:
- You need a quick, definitive answer about a topic
- You want to verify tier status and promotion limits
- You need to confirm stop conditions for a specific claim

**After reading a context-sufficient summary, stop.** Phase reports and detailed constraint files provide methodology only - they cannot change the tier or closure status declared in the summary.

---

## What NOT to Do

1. **Don't read archive/** - that's raw memory, not curated knowledge
2. **Don't read all of phases/** - 118 directories, too much context
3. **Don't read SPECULATIVE/ first** - it's interpretation, not foundation
4. **Don't ignore STOP_CONDITIONS.md** - it prevents wasted effort

---

## Navigation Footer Convention

Every file ends with a navigation footer:

```
← [Previous.md](Previous.md) | [Next.md](Next.md) →
```

Or:

```
← [CLAIMS/INDEX.md](INDEX.md) | ↑ [CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
```

Follow these to maintain reading flow.

---

## Navigation

← [METHODOLOGY.md](METHODOLOGY.md) | [CHANGELOG.md](CHANGELOG.md) →
