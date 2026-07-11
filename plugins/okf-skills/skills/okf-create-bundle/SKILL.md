---
name: okf-create-bundle
description: >-
  Scaffold a new OKF (Open Knowledge Format) bundle — a portable "second brain" of interlinked
  markdown nodes that both humans and AI agents can read, with no database, runtime, or embeddings.
  Use this when the user wants to create a second brain, start a knowledge brain, set up an OKF
  folder/bundle, or build a graph of markdown notes — for ANY domain (gardening, academic,
  psychology, a product wiki, a research corpus). Triggers on phrasings like "create a second
  brain", "start an OKF bundle", "set up a knowledge brain", "make an OKF folder", "build a knowledge
  graph of markdown files". After scaffolding, hand off to okf-concept-node (to fill it with
  knowledge) and okf-write-playbook (to add procedures).
---

# Create an OKF bundle

Scaffold a new **Open Knowledge Format (OKF)** bundle: a directory of interlinked markdown files that
form a portable, vendor-neutral "brain." This skill covers the folder layout, the build process, and
the definition of done. It is **domain-agnostic** — the same structure serves a gardening brain, an
academic brain, or a company wiki.

> If the repo already contains an `okf-gold-standard.md`, treat it as the fuller source of truth and
> follow any project-specific extensions it records. This skill is the self-contained version.

## What an OKF bundle is (the mental model)

- **Just files, just markdown, just YAML frontmatter.** No database, no runtime, no proprietary SDK.
- **Each file is one concept / unit of knowledge.** The **file path is the identity** of that node.
- **Nodes interlink with ordinary markdown links**, forming a knowledge graph an agent can traverse.
- **Read `index.md` first.** An agent opens the index (progressive disclosure), finds the few files
  relevant to its task, and opens **only those** — it never loads the whole bundle. This is why nodes
  can and should carry MAXIMUM detail: findability is the index's job, not the reader's.
- **The index replaces RAG / embeddings as the retrieval layer.** Retrieval is by *curated
  navigation*, not vector search — transparent, deterministic, auditable, and needs no embedding store.
  Index-first navigation works well up to roughly a few hundred nodes; beyond that, keep the index but
  add an **on-device** search pass (BM25 + optional local vectors, with LLM re-ranking) — still local,
  still no cloud embedding infrastructure.
- **A brain is a compounding artifact, not a one-shot export.** The tedious part of a knowledge base is
  the *bookkeeping* — updating cross-references, spotting contradictions, keeping the index current —
  which is exactly what an agent does tirelessly. Humans curate sources and direct the work; the agent
  maintains the graph. Value accrues every time a source is ingested or a good answer is filed back.

## Canonical folder structure (5 typed folders + reserved files)

```
okf-bundle/
├── index.md          # generated navigation (NO frontmatter) — read first
├── log.md            # change history (newest first)
├── README.md         # human prose overview (optional)
├── concepts/         # abstract ideas, rules, methods, definitions
│   └── index.md      # per-folder listing (NO frontmatter)
├── entities/         # concrete, identity-bearing things
├── playbooks/        # reproducible step-by-step procedures
├── references/       # the source documents (1 node per source)
└── systems/          # the apparatus/pipeline itself
```

Record any project-specific axis (a pipeline stage, a section, a season) in **frontmatter**, not as
folder names. The five folders above are the only ones OKF tooling expects.

### Pick the right type for each node

| type | what it is | examples (any domain) |
| :-- | :-- | :-- |
| `concept` | an abstract idea, rule, method, threshold, definition | "companion planting", "recall-first screening", "double-entry bookkeeping" |
| `entity` | a concrete, identity-bearing thing | a person, an organisation, a tool, an instrument, a specific plant cultivar, an included study |
| `playbook` | a reproducible procedure someone can follow | "spring bed prep", "full-text screening", "month-end close" |
| `reference` | a source document (one node per source) | a book/PDF/paper/standard/web page, with bibliographic metadata + a checksum |
| `system` | the apparatus that produces or uses the bundle | "the ingestion pipeline", "the NotebookLM sync" |

**Rule of thumb:** a *thing* (has a name / DOI / identity) → **entity**; an *idea or rule* about it →
**concept**; the *source document* → **reference**.

**Spec vs convention (important).** The OKF spec's only *hard* rule is that every non-reserved `.md` has
parseable YAML frontmatter with a **non-empty `type`** — and `type:` is a **free-form** string (Google's
own examples include `BigQuery Table`, `API Endpoint`, `Metric`); the spec mandates **no** particular
folders, and consumers must tolerate missing fields, unknown types, and even **broken links** (which can
just mean *not-yet-written* knowledge). The five folders + matching `type:` values used here are a
widely-adopted **convention** (this guide's, and Marie Haynes' public OKF brain) that keeps the graph and
index grouping clean. Stick to them for consistency, but a descriptive `type:` like `Evaluation
Framework` is fully spec-valid — and the quality bar at the end of this skill is deliberately *stricter*
than the spec.

## Scaffold command (domain-neutral)

Bash:

```bash
BUNDLE=okf-bundle            # rename to your brain, e.g. garden-brain
mkdir -p "$BUNDLE"/{concepts,entities,playbooks,references,systems}
printf '# OKF Bundle Index\n\nRead this first, then open only the files relevant to your task.\n' > "$BUNDLE/index.md"
printf '# Directory Update Log\n' > "$BUNDLE/log.md"
printf '# OKF bundle — <Brain name>\n\nAn Open Knowledge Format brain. Read `index.md` first.\n' > "$BUNDLE/README.md"
```

PowerShell:

```powershell
$Bundle = "okf-bundle"       # rename to your brain
"concepts","entities","playbooks","references","systems" | ForEach-Object { New-Item -ItemType Directory -Force "$Bundle/$_" | Out-Null }
"# OKF Bundle Index`n`nRead this first, then open only the files relevant to your task.`n" | Set-Content "$Bundle/index.md"
"# Directory Update Log`n" | Set-Content "$Bundle/log.md"
"# OKF bundle — <Brain name>`n`nAn Open Knowledge Format brain. Read ``index.md`` first.`n" | Set-Content "$Bundle/README.md"
```

## Build process (init → fill → generate)

1. **Init** the five folders + `index.md` + `log.md` (+ optional `README.md`) with the command above.
2. **Gather sources** into a raw, immutable `resources/` (or `sources/`) area. Convert PDFs to readable
   markdown if needed (for pdfplumber, `x_tolerance=1` fixes missing-space text layers).
3. **One `reference` node per source** — bibliographic frontmatter + a `resource` URL + a `sha256`
   checksum. Slug prefix `ref-` (e.g. `references/ref-rhs-veg-guide.md`).
4. **Ingest = one source → MANY max-detail `concept` nodes, *integrated* into what already exists.** A
   700-page handbook yields dozens of self-contained, interlinked concepts. One agent per source,
   reading it in full. But ingestion is *integrate*, not blind append: before writing, check `index.md`
   for a node that already covers the topic and **enrich/revise it** instead of duplicating; where a new
   source **contradicts** an existing claim, surface the contradiction (note both, dated and sourced)
   rather than silently overwriting. Use **okf-concept-node** for each node's structure.
5. **`entity` nodes** for the concrete things (people, orgs, tools, instruments, cultivars, and the
   project's primary objects).
6. **`playbook` nodes** for each reproducible procedure (use **okf-write-playbook**); **`system`**
   nodes for the apparatus.
7. **Generate `index.md` + per-folder indexes + the graph, then lint** (see Tooling).
8. **Append to `log.md`.**

Knowledge-only bundles are valid: you can ship `concepts/` + `entities/` + `references/` and add
`playbooks/` later. Don't block on completeness.

## Reserved-file formats

**`index.md` (NO frontmatter).** Generated. Groups nodes under type headings, one line each — the
line is the node's `description` from its frontmatter:

```
# OKF Bundle Index

Read this first, then open only the files relevant to your task.

# concepts
* [Companion planting](/concepts/concept-companion-planting.md) - mutually beneficial plant pairings.
# entities
* [RHS](/entities/entity-rhs.md) - the Royal Horticultural Society.
```

A per-folder `index.md` (also no frontmatter) lists just that folder. The **one** exception to the
no-frontmatter rule: the **bundle-root** `index.md` may carry a single key, `okf_version: "0.1"`, to
declare the spec version it targets — the only place frontmatter is permitted in an index file.

**`log.md` — change history, newest first.** Date headings MUST be ISO-8601 `YYYY-MM-DD`. Leading bold
word (**Creation** / **Update** / **Deprecation**) is a convention:

```
# Directory Update Log

## 2026-07-11
* **Creation**: seeded the bundle with concepts for companion planting and crop rotation.
```

## Tooling (optional but recommended)

If a Python `okf_tools.py` is available (copy it from a sibling bundle), it automates the generated
artefacts:

- `align` — backfill queryable frontmatter fields.
- `index` — (re)generate `index.md` + per-folder indexes (no frontmatter, bundle-relative links).
- `graph` — write an interactive `okf-graph.html` (force-directed "brain", coloured by type).
- `lint` — report orphan links, missing fields, and **thin concepts** (flag, then deepen). A fuller
  lint also hunts **contradictions** between nodes, **stale claims**, and **coverage gaps** (an
  important concept with no node of its own yet).
- `python okf_tools.py all` runs all four. Graph/lint read edges from **markdown links**.

A bundle is fully valid without the tooling; the index and links can be hand-written or synthesised on
the fly.

## Maintenance loop (a brain compounds)

Scaffolding is day one. The value is in the ongoing loop the agent runs as sources arrive and questions
get asked:

- **Ingest** — read a new source, extract, and **integrate** it: update the entity/concept nodes it
  touches, revise summaries, add missing cross-links, and **note where it contradicts** existing claims
  (see build step 4). New nodes only for genuinely new topics. For anything beyond a trivial addition,
  **propose the changes first and let a human approve or reject each one** before writing (an *assess →
  approve → enrich* loop) — the agent does the work, the human decides what lands. One source often does
  several things at once (enrich N nodes + spawn 1 new node), so present the proposal per item.
- **Query** — answer from the index (read it, open only the relevant nodes, synthesise **with
  citations**). When an answer is good enough to reuse, **file it back** as a new node — the brain grows
  from use, not just from ingestion.
- **Lint** — periodically sweep for orphans, thin/stale nodes, contradictions, and coverage gaps; then
  regenerate `index.md` + the graph and append to `log.md`.

**State the conventions in the bundle itself.** Keep a short schema doc at the root (the `README.md`, or
a `CLAUDE.md`) that tells any agent how this bundle is organised and which workflows to follow when
ingesting or maintaining it — so the loop is reproducible without this skill in context. For a
**scholarly / academic brain**, also pin a **citation standard** here (a `CITATION-STYLE.md`): which
style (APA / Vancouver / numbered), whether to cite **primary sources only** (not the secondary text a
claim was read in), and that in-text `(Author, Year)` cites match a `# References` list — so every node
is sourced consistently. See **okf-concept-node**.

## Definition of done

- Every node has `type` + the recommended queryable fields; AI-authored nodes carry a `provenance`
  block.
- Concepts are **self-contained and maximally detailed** — no "see the source" deferrals.
- Interlinking uses **bundle-relative markdown links**; a `# Related` section is present where relevant.
- `index.md` + per-folder indexes are regenerated; `lint` shows **0 orphans, 0 thin concepts**.
- `log.md` is updated.

## Hand-off

- To fill the bundle with knowledge, use **okf-concept-node** (concept / entity / reference / system
  nodes share the same shape).
- To add reproducible procedures, use **okf-write-playbook**.
