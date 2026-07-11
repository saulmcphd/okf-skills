---
name: okf-node-types
description: >-
  Author the non-concept node types in an OKF (Open Knowledge Format) "second brain" — ENTITY,
  REFERENCE, and SYSTEM nodes. They share the concept node's frontmatter+body shape but each has
  distinct conventions: entities carry an entity_kind and stay identity-focused; references are the
  one-node-per-source provenance layer with bibliographic + checksum frontmatter; systems describe the
  apparatus that builds/uses the bundle. Use this when the user wants to add an entity (a person,
  organisation, tool, instrument, or study), create a reference/source node for a book/paper/URL, add a
  system node, or asks how to structure a non-concept node. Domain-agnostic. For the shared node shape
  see okf-concept-node; for folder roles see okf-create-bundle.
---

# Author entity, reference & system nodes

The three OKF node types that are **not** concepts. Per the OKF spec these are all just "concepts with a
different `type`" — the split into folders is a widely-used **convention** (ours + Marie Haynes' public
OKF brain), not a spec rule. They **reuse the concept node's shape** (frontmatter → structural body →
`# Related` → citations → `provenance` for AI nodes — see **okf-concept-node**); this skill covers only
what differs per type. Domain-agnostic (gardening, academic, ops).

## Entity — a concrete, identity-bearing thing

Path `entities/entity-<slug>.md`. Use for a **person, organisation, tool, instrument, or a specific
study** — anything with a name/identity (vs a `concept`, which is an *idea/rule* about such things).

- **Frontmatter:** the standard keys **plus `entity_kind:`** (`person` | `organisation` | `tool` |
  `instrument` | `study` | …).
- **Body — identity-focused, not a full treatise.** Keep it to who/what it is; the deep knowledge lives
  in the *concept* nodes it links to. Conventional sections: `# Definition` (who/what) → `# Key
  contributions` (or key facts) → `# Significance` → `# Related` → `# References`.

```markdown
---
type: entity
title: "Royal Horticultural Society (RHS)"
description: "UK gardening charity; authority on horticultural practice, plant trials, and the Award of Garden Merit."
entity_kind: organisation
tags: [organisation, horticulture, uk]
timestamp: 2026-07-11
---
# Definition
The Royal Horticultural Society (founded 1804) is the UK's leading gardening charity…
# Key contributions
- Runs plant trials and awards the **Award of Garden Merit (AGM)**…
- Publishes advice used across this brain (companion planting, pest control)…
# Significance
The AGM is the reference standard several concept nodes cite for cultivar choice.
# Related
* [Companion planting](/concepts/concept-companion-planting.md) - RHS guidance underpins the pairings.
# References
Royal Horticultural Society. (n.d.). About the RHS. https://www.rhs.org.uk/about-the-rhs
```

## Reference — one node per source (the provenance layer)

Path `references/ref-<slug>.md`. **The one type structurally distinct from a concept.** Create **exactly
one per source document** (a book, paper, standard, or URL). It is the node other nodes *cite back to*.

- **Frontmatter — bibliographic + integrity.** Standard keys, plus: `slug`, `authors` (list), `year`,
  `edition`, `publisher`, `isbn`/`doi`, `audience`; and for a local/ingested file the integrity +
  location extensions `sha256`, `bytes`, `pages`, `source_files`, `source_dir`. (`resource` holds the
  canonical URL.) These extra keys are spec-legal *extensions* — consumers preserve them.
- **Body — describe the source and its role, don't reproduce it.** Conventional sections: `# What it is`
  → `# What this brain draws from it` → `# Where it lives` (path to the raw page-marked text, if
  ingested) → `# Related`.

```markdown
---
type: reference
title: "RHS Grow Your Own Vegetables"
description: "Practical UK vegetable-growing manual — the how-to backbone for bed-prep and sowing nodes."
resource: "https://www.rhs.org.uk/vegetables"
slug: rhs-veg
authors: ["Royal Horticultural Society"]
year: 2022
publisher: "Dorling Kindersley"
isbn: "9780241534878"
sha256: "…"        # if a local copy was ingested
source_dir: "/sources/rhs-veg/"
tags: [reference, vegetables, how-to]
timestamp: 2026-07-11
---
# What it is
A practical single-volume vegetable-growing manual covering sowing, spacing, and harvest by crop.
# What this brain draws from it
The how-to backbone for the bed-prep and sowing procedure nodes; spacing tables feed several concepts.
# Where it lives
Raw page-marked text: `/sources/rhs-veg/part-001.md …` (`<!-- page N -->` markers).
# Related
* [Spring bed preparation](/playbooks/playbook-spring-bed-prep.md) - built from this source.
```

> **Citation discipline still applies.** A reference node records the *source*; individual claims in
> concept nodes should cite the **primary** works, not necessarily the textbook they were summarised
> from (follow the bundle's citation standard).

## System — the apparatus that builds or uses the bundle

Path `systems/system-<slug>.md`. Use for a **pipeline, sync, or tool** that produces or consumes the
brain (an ingestion pipeline, a crawler, a dashboard). Concept-like shape.

- **Body:** `# What it is` → `# What it does` (inputs → outputs, the scripts/steps) → `# Related`
  (the nodes/playbooks it produces or feeds).

```markdown
---
type: system
title: "Garden-brain ingestion pipeline"
description: "Turns source PDFs/URLs into concept and reference nodes; regenerates the index and graph."
tags: [system, pipeline, ingestion]
timestamp: 2026-07-11
---
# What it is
The scripted pipeline that extracts sources and writes OKF nodes for this bundle.
# What it does
Inputs: files in `/sources/`. Outputs: `references/ref-*.md`, `concepts/concept-*.md`, a refreshed
`index.md` + graph. Steps: extract → draft nodes → dedupe → lint.
# Related
* [Spring bed preparation](/playbooks/playbook-spring-bed-prep.md) - a procedure this pipeline can seed.
```

## Quality bar
- Right folder + `type`; **entities** carry `entity_kind` and stay identity-focused; **references** are
  one-per-source with bibliographic + integrity frontmatter and the provenance-layer body; **systems**
  describe the apparatus.
- Same shared rules as concepts: `# Related` present, bundle-relative markdown links (no wikilinks), and
  a `provenance` block on AI-authored nodes.

## Related skills
- **okf-concept-node** — the shared frontmatter+body shape (and the main `concept` type).
- **okf-create-bundle** — what each folder/type is for, and the maintenance loop.
- **okf-ingest-source** — creates one reference node per new source, then enriches concepts/entities.
