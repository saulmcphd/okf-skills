---
name: okf-ingest-source
description: >-
  Safely add a new source (a PDF, paper, article, or URL) to an existing OKF (Open Knowledge Format)
  "second brain" using the ASSESS → HUMAN APPROVES → ENRICH loop: read the source, propose per-item
  changes (which existing nodes to enrich and in which section, which new nodes to create, where it
  contradicts current claims), let a human approve/reject each item, then write only the approved
  changes to standard. Use this when the user wants to ingest/add a new source or document into their
  brain, process a PDF/article into nodes, grow the knowledge base from new material, or asks how to add
  new knowledge without duplicating or overwriting. Domain-agnostic. Pairs with okf-gap-scan (which
  section needs it), okf-concept-node / okf-node-types (how to write), and okf-create-bundle (the loop).
---

# Ingest a new source into an OKF brain

The safe way to grow a brain from new material. Ingestion is **integrate, not append**, and it is
**human-gated**: the agent proposes, a human decides, then the agent writes. A single source usually
does several things at once — enrich a few existing nodes *and* spawn a new one. Domain-agnostic.

> This is the detailed procedure behind the "Ingest" step of **okf-create-bundle**'s maintenance loop,
> and the generic form of a project's ingestion plan (e.g. `plan.md` §6B). Marie Haynes' public OKF
> brain implements the same "Review Proposed Changes → Approve/Reject" gate.

## The loop: ASSESS → HUMAN APPROVES → ENRICH

### 1. Assess (automated proposal — nothing is written yet)
Read the **whole** source, then match its content against the existing brain via `index.md` (curated
navigation) and produce a **per-item proposal**:

- **Enrich existing nodes** — list each node the source strengthens **and the specific `#` section**:
  fill a **missing** section or expand a **thin** one. Use **okf-gap-scan** to know which section of
  which node is incomplete.
- **New node(s)** — genuinely new topics / people / sources the brain lacks (a new concept, entity, or —
  for the source document itself — a `reference` node; see **okf-node-types**).
- **Fill known gaps (check the backlog).** Cross-check the source against the standing **missing-node
  backlog** from **okf-gap-scan** (its `candidate_nodes` — topics your nodes already name but have no node
  of their own): for each candidate, ask whether *this* source carries enough to **create that node now**.
  This closes the loop — gap-scan finds what's missing, ingestion fills it the moment a source provides the
  material — so no upload is ever triaged in isolation from what you already know you're missing.
- **Contradictions** — where the source disagrees with an existing claim, flag it (both statements,
  each dated and sourced) rather than silently overwriting.

Present it as a checklist the human can act on item-by-item, e.g.:

```
Proposed from "companion-planting-trials-2024.pdf":
  [enrich] concept-companion-planting.md → add a "# Contemporary research" section (currently missing)
  [enrich] concept-crop-rotation.md      → expand thin "# Evidence" section
  [new]    concept-trap-cropping.md      → source covers this; no node yet
  [new]    references/ref-companion-trials-2024.md → one reference node for the source
  [contra] concept-companion-planting.md claims X; source finds not-X → record both
```

**How to decide — new node vs. enrich existing (the core judgement):**
- **Match by topic, not filename.** Slugs differ (`zone-of-proximal-development` vs `concept-zpd`), so
  search `index.md` *descriptions*, not just names.
- **Default to enrich.** If a node already covers the topic, add or expand the relevant `#` section — a
  brain of near-duplicates is worse than a few rich, well-linked nodes.
- **New node only when genuinely distinct:** a different concept; a person / org / study with its own
  identity (→ an **entity**); or the source document itself (→ one **reference** node). A substantial
  sub-topic that can stand alone → a new node linked from its parent; a minor one → a section *inside*
  the parent.
- **Unsure if two things are "the same"?** Prefer one richer node + a cross-link over two thin ones, and
  flag genuine merge candidates for the human.
- Expect **both** from one upload: enrich several existing nodes **and** spawn one or two new ones.

### 2. Human approves / rejects (the only manual step)
The human **approves, rejects, or edits each item**. **Nothing is written until approved** — the agent
does the work, the human decides *what lands*. Do not batch-approve on the human's behalf.

### 3. Enrich (on approval only) — to the same standard
For every approved item:
- **Write/expand** the node per **okf-concept-node** (concepts) or **okf-node-types** (entity / reference
  / system). New nodes follow the bundle's citation standard **from creation**.
- **Cite primary sources.** Attribute claims to the original works the source rests on (if the new source
  *is* a primary work, cite it directly); never fabricate a citation or a DOI.
- **One `reference` node per new source** (bibliographic + integrity frontmatter — see okf-node-types).
- **For an academic source, harvest its reference list.** Extract the primary works the source cites into
  the brain's **bibliography registry** (`references.json`) so each claim can be attached to a verified
  **primary** work, not the secondary source — see **okf-bibliography**.
- **Record provenance, separate from citations.** Tag each enriched node with where the addition came
  from (e.g. a `source-<slug>` frontmatter tag / `enriched_from`), so the brain always knows *which*
  source fed *which* section — without turning provenance into a citation.
- **Reconcile & regenerate.** Reconcile in-text ↔ references; regenerate `index.md` + graph
  (`okf_tools.py all` if present); run lint; **append to `log.md`** (newest first) noting what was
  created/updated.

## Guardrails
- **Human-gated.** Never write an unapproved change.
- **Integrate, don't duplicate.** Enrich an existing node before creating a near-duplicate; dedupe by
  *topic* (slugs differ), not by filename.
- **Surface contradictions**, don't bury them.
- **Provenance ≠ citation.** Record the ingested source as provenance; cite the primary literature.
- **No fabrication.** No invented facts, citations, or DOIs; if a section can't be sourced, leave it and
  flag it rather than filling it from outside knowledge.
- **Strip source artifacts — the node must stand alone.** When lifting from the source, never carry over
  its cross-references: no "Table 1", "Fig. 2", "see chapter 3", "the diagram above", "p. 42". The reader
  won't have the source — **embed the content instead** (transcribe the table, describe the figure). See
  the self-containment rule in **okf-concept-node**; a `check_source_refs`-style scan catches leftovers.

## Related skills
- **okf-gap-scan** — tells you *which section of which node* a source should feed (drives step 1).
- **okf-concept-node** / **okf-node-types** — how to write the approved nodes.
- **okf-create-bundle** — the wider maintenance loop this fits inside.
