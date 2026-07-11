---
name: okf-dashboard
description: >-
  Build a dashboard for an OKF (Open Knowledge Format) "second brain" — two capabilities: (1) an
  interactive GRAPH EXPLORER that renders the nodes and their links as a force-directed graph you can
  search, filter by type/tag/centrality, and click to read a node; and (2) ASK-THE-BRAIN, an
  index-first grounded Q&A that retrieves the relevant nodes and synthesises a cited answer that never
  states anything the brain doesn't support. Use this when the user wants to visualise/explore their
  knowledge graph, "see how my notes connect", build a node/graph viewer, stand up a dashboard for a
  second brain, or ask/query/search their OKF bundle. Domain-agnostic (gardening, academic, psychology).
  To create the bundle first use okf-create-bundle; to file good answers back as nodes use okf-concept-node.
---

# Build an OKF dashboard (explore + ask)

Stand up the "use the brain" layer over an existing OKF bundle. Two halves — a **graph explorer** to
*see* the brain and an **ask-the-brain** Q&A to *query* it. This skill is **domain-agnostic**: it works
over any OKF bundle (gardening, academic, a company wiki), not one project.

> A dashboard is a real piece of software — treat it as a build track, not a one-liner. But both halves
> read the *same* inputs the bundle already has: the typed markdown nodes, their frontmatter, and the
> markdown links between them. No database, no embedding store required.

## Inputs (what both halves read)

- **Nodes** — the `*.md` files under `concepts/ entities/ playbooks/ references/ systems/`. Each carries
  frontmatter (`type`, `title`, `description`, `tags`, `provenance`, …).
- **Edges** — the **bundle-relative markdown links** in each node's body (`[Title](/concepts/concept-x.md)`).
  This is the same edge source `lint`/`graph` use. (Legacy `[[wikilinks]]` may also be parsed if present.)
- **`index.md`** — the curated navigation layer; the retrieval spine for ask-the-brain.

---

## Part A — Graph explorer (see the brain)

### If the bundle already has a generator, use it
If `okf_tools.py` is present, `python okf_tools.py graph` already writes a **self-contained interactive
`okf-graph.html`** (force-directed, coloured by type). That is the reference implementation — run it, or
copy/adapt it for a new bundle. `okf_tools.py all` also refreshes the index the graph relies on.

### Building one from scratch (a bundle with no tooling)
Produce a **single self-contained HTML file** (inline the JS/CSS — no external CDN, so it stays as
portable as the bundle itself). Two steps:

1. **Extract the graph data.** Walk the node files; for each, emit a node record and parse its body for
   markdown links to build edges:
   ```json
   {
     "nodes": [
       {"id": "/concepts/concept-companion-planting.md", "label": "Companion planting",
        "type": "concept", "tags": ["pest-control"], "in_degree": 5, "out_degree": 2,
        "description": "…", "human_verified": false}
     ],
     "edges": [
       {"source": "/concepts/concept-companion-planting.md", "target": "/concepts/concept-crop-rotation.md"}
     ]
   }
   ```
2. **Render it** as a force-directed graph in one HTML file, colouring nodes **by `type`**, sizing them
   **by centrality**, and drawing edges **directed** (an arrow from the linking node to the node it links).

**Sizing a node — prefer in-degree.** A node's size should signal how *important* it is to the brain (its
**centrality**). Choose the metric deliberately:
- **In-degree (recommended)** — how many *other* nodes link **to** this one: its *referenced-ness* /
  authority, like a citation count. A node the rest of the brain repeatedly points at is a genuine hub.
- **Total degree (simpler proxy)** — in + out links combined. Easier, but it conflates "is referenced a
  lot" with "links out a lot," so a node that merely lists many links looks like a hub it isn't. Fine for
  a quick view; prefer in-degree when size is meant to convey importance.
- **Scale for readability** — grow the radius **sub-linearly** (e.g. `r = base + k·√(metric)`) and **cap**
  it, so a few mega-hubs don't dwarf everything. Expose the *same* metric everywhere it appears — the node
  panel ("N references") and the centrality filter/slider — so they all agree.

### Features worth including (from plan §6A.1)
- **Search** nodes by title/description.
- **Filter** by `type`, `tag`, and centrality (hide the long tail; focus on hubs).
- **Click a node → read it**: **render the node's markdown to HTML** — headings, lists, fenced code, and
  **tables as real HTML tables** (so a table transcribed from a source displays as a table, not raw
  `| … |` text) — plus its in/out links, citations/references, `provenance`, and verification status, so
  the graph is a reader, not just a picture. (Use a small inline markdown renderer; keep it self-contained.)
- **Colour by type**, **size by centrality** (in-degree — how referenced a node is; see *Sizing* above);
  highlight a node's neighbourhood on hover.

---

## Part B — Ask-the-brain (query the brain)

The query pattern, and the integrity bar that makes it trustworthy.

### The retrieval loop (index-first, no embeddings needed)
1. **Read `index.md` first.** It lists every node under type headings with a one-line description — the
   curated map.
2. **Select the few relevant nodes** by their descriptions (curated navigation, not vector search).
3. **Open only those nodes** (and follow their `# Related` links one hop if needed).
4. **Synthesise a grounded answer** from what those nodes actually say — **thematically, not as a list**.
   When the answer draws on several nodes, weave them by *theme* (consensus, tension, nuance) rather than
   node-by-node ("Node A says…; Node B says…"), weigh evidence quality where sources differ, and use
   bridging language. See the **information-synthesis** skill for the method.

### The hard integrity rule (non-negotiable — plan §6A.2)
- **Ground every claim in the nodes.** The answer must **cite the nodes it drew on and their primary
  references**, with links back.
- **Match the brain's citation style.** Format those citations the way the brain itself is written — for
  an **academic brain** that means **APA 7th**: in-text `(Author, Year)` (a page number for a direct
  quote) and a **References** list at the end of the answer. Draw the reference records from the
  bibliography registry (**okf-bibliography**) and apply the format with the **apa-style** skill, so the
  reader can lift the answer straight into their own writing.
- **Never state anything the brain doesn't support.** No fabrication — the same integrity bar as the
  content itself.
- **If the brain doesn't cover it, say so.** "The brain has no node on X" is a correct answer — and it
  doubles as a **gap signal** (feed it to `lint`/coverage-gap detection). Asking questions is also a QA
  tool: a weak answer surfaces a thin node, a missing node, or a contradiction.

### Compounding — file good answers back
When a synthesised answer is good enough to reuse, **write it back into the brain as a new node** (use
**okf-concept-node**), cited to the primary sources it rests on. The brain grows from *use*, not only
from ingestion.

### Scaling the retrieval
- Index-first navigation works well up to **a few hundred nodes**.
- **Beyond that**, keep the index but add an **on-device search pass** — BM25 (+ optional local vectors)
  with **LLM re-ranking**, all local. Still **no cloud embedding infrastructure**; the index stays the
  human-readable spine, the local search just narrows the candidate set the agent then reads in full.

### A minimal query UI (optional)
The retrieval loop above is the substance and works with no UI at all. If a UI is wanted, the lightest
form is a **query box bolted onto the graph HTML**: type a question → the page surfaces the candidate
nodes (by index/description match or the local search pass) → the answer links back to those nodes. Keep
it self-contained, same as the graph.

---

## Quality bar

- **Graph:** single self-contained HTML (no external fetches); nodes coloured by type, sized by
  centrality; search + type/tag/centrality filters; click-to-read shows content, links, citations,
  provenance, verification.
- **Ask-the-brain:** answers are **grounded and cited** (nodes + primary refs), **never fabricated**, and
  **admit gaps**; good answers are filed back as nodes; retrieval degrades gracefully at scale via local
  search, never a cloud embedding store.
- Both read the live bundle (regenerate after `okf_tools.py all`), so the dashboard never drifts from the
  nodes.

## Related skills
- **okf-create-bundle** — the bundle this dashboard views and queries (and its maintenance loop).
- **okf-concept-node** — the node structure used when filing a good answer back into the brain.
- **okf-write-playbook** — capture the "ingest a new source" or "run the Q&A QA sweep" procedures as playbooks.
