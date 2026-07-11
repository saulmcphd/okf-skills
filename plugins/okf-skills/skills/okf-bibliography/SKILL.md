---
name: okf-bibliography
description: >-
  Manage the bibliography / references registry for an ACADEMIC OKF (Open Knowledge Format) brain — a
  machine-readable `references.json` of the primary works cited across the brain, keyed by author-year,
  used to attach accurate PRIMARY citations, dedupe references, and verify that every citation resolves
  to a real source (no fabrication). Use this when building an academic/research brain, setting up a
  references.json / bibliography, extracting a reference list from an uploaded PDF or article, matching
  claims to primary sources, verifying citations or DOIs, or resolving "reference pending verification".
  Not needed for a non-academic brain. Distinct from reference *nodes* (see okf-node-types); populated on
  ingest (okf-ingest-source) and consumed by concept nodes' # References (okf-concept-node).
---

# Manage an academic brain's bibliography registry

The **references layer** of an academic OKF brain. This skill is only for **scholarly / research**
brains that must cite verifiable primary sources; a gardening or product-wiki brain does not need it.

## First, the crucial distinction — two "reference" things

| | What it is | Where it lives | How many |
| :-- | :-- | :-- | :-- |
| **Reference *node*** | one OKF node per **top-level source** the brain is built from (a book, a site) | `references/ref-<slug>.md` | a handful (see **okf-node-types**) |
| **Bibliography *registry*** | a machine-readable table of every **primary work cited** across the brain | `references/bibliography.json` (or `sources/bibliography-<slug>.json` per source for large brains) | hundreds–thousands |

**Do not make a node per citation.** An academic brain cites thousands of primary works; a markdown node
each would drown the graph. The registry is their scalable home; each node's `# References` list is
*drawn from* it. The registry is a plain data file — OKF tooling ignores non-`.md` files, so it sits
happily inside the bundle.

## Registry format (recommended shape)

Key each entry by a stable **citation key** (`author-year`, disambiguated `-a/-b` when needed):

```json
{
  "milgram-1963": {
    "authors": ["Milgram, S."],
    "year": 1963,
    "title": "Behavioral study of obedience",
    "container": "Journal of Abnormal and Social Psychology",
    "volume": "67(4)",
    "pages": "371–378",
    "doi": "10.1037/h0040525",
    "apa": "Milgram, S. (1963). Behavioral study of obedience. Journal of Abnormal and Social Psychology, 67(4), 371–378. https://doi.org/10.1037/h0040525",
    "verified": true,
    "found_in": ["ref-gross", "ref-simplypsychology"]
  }
}
```

- `apa` (or your chosen style) is the ready-to-paste `# References` line — nodes copy it verbatim so
  formatting is consistent everywhere.
- `verified` = the citation was resolved to a real work (DOI / Crossref match), not just typed.
- `found_in` = which source(s) the reference was harvested from — provenance, kept separate from the
  citation itself.

## Building & maintaining the registry

1. **Harvest on ingest.** When an academic source is added (see **okf-ingest-source**), extract its
   **reference list** (back-matter / bibliography) and normalise each entry into the shape above. One
   textbook yields hundreds of primary-work entries.
2. **Merge, don't duplicate.** Dedupe by DOI first, then fuzzy author-year-title. Merge `found_in` lists
   so one work has one registry entry regardless of how many sources cite it.
3. **Verify against Crossref / DOI.** For each entry, confirm it resolves to a real work — query Crossref
   by `title` + `author` + `year`, accept an exact match, and record the DOI. Mark `verified: true`.
   **Never invent or guess a DOI**; an unresolved entry stays `verified: false` and is flagged, not
   fabricated. Re-validate periodically (DOIs rot; publishers re-issue).

## Primary-citation matching (the whole point)

When a **secondary** source (a textbook) states a claim while citing a primary work, attach the citation
to the **primary** work — looked up and verified in the registry — **not** to the textbook:

> Textbook says: "Milgram found 65% obeyed (Milgram, 1963)."
> → cite `milgram-1963` from the registry, **not** the textbook.

This enforces the primary-sources-only standard (see the citation section of **okf-concept-node**). If no
clear primary source exists for a generic fact, leave the claim uncited — do not attribute it to the
secondary text, and do not invent a source.

## How a node uses the registry

A concept/entity node's `# References` (or `# Citations`) list is **generated from the registry**: for
each work the node cites, copy that entry's formatted line. Result: consistent formatting, no duplicate
references, and every citation already verified. Frontmatter provenance (`source-<slug>` / `primary_source`)
still records *which source the node was written from* — provenance stays separate from citations.

## Guardrails
- **Primary, not secondary** — cite the original work, never the textbook that summarised it.
- **Verified, not fabricated** — every citation resolves to a real work; never guess a DOI; flag
  unresolved refs (`verified: false` / "reference pending verification") rather than inventing them.
- **One record per work** — the registry is the single source of truth for bibliographic detail; nodes
  copy from it, they don't re-type it.
- **Provenance ≠ citation** — `found_in` / `source-<slug>` tracks where a reference came from, separate
  from the scholarly citation the reader sees.

## Related skills
- **okf-node-types** — the `references/ref-*.md` *source* nodes (distinct from this registry).
- **okf-concept-node** — the citation section that consumes the registry for each node's `# References`.
- **okf-ingest-source** — harvests a new source's reference list into the registry.
- **okf-gap-scan** — can flag substantive claims that carry no citation (registry gaps to resolve).
