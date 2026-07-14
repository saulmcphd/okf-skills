---
name: okf-gap-scan
description: >-
  Find where an OKF (Open Knowledge Format) "second brain" is incomplete — a completeness audit, not a
  broken-link lint. Four kinds of gap: STRUCTURAL (a node missing or thin on its expected `#` sections,
  scored against a per-type section schema), COVERAGE (an important topic/person the brain names but
  has no node for), SOURCE-COMPARISON (auditing a node against the actual text of a source it draws
  on or should — topic/keyword/depth-mechanistic/recency gaps, plus verbatim quote/stat verification that
  catches misquotes a schema check can't), and SEARCHER-DEMAND (a 100-question audit from the reader's/
  searcher's perspective — does the node answer what a person searching the topic would ask? — surfacing
  answer-box/featured-snippet and topical-coverage opportunities, each reported with ready-to-drop-in text
  and placement). Produces a ranked enrichment backlog. Use this when the user asks what's missing or
  incomplete in their brain, which nodes are thin or need enriching, where the coverage gaps are, whether a
  node captures everything a source says, whether a node answers a searcher's likely questions, wants a
  topical-coverage / answer-box / SEO gap audit, or wants to build an enrichment to-do list. Domain-agnostic.
  Feeds okf-ingest-source (which section a new source should fill) and okf-concept-node (the enrichment work).
---

# Scan an OKF brain for gaps

A **completeness** audit. This is distinct from link-lint (orphans / missing frontmatter / broken links,
handled by `okf_tools.py lint`): gap-scan asks *"what knowledge is missing or thin?"* — both **within**
nodes (incomplete sections) and **across** the brain (topics with no node at all). Output is a **ranked
enrichment backlog**. Domain-agnostic; this is the generic form of a project's gap plan (e.g. `plan.md`
§6C).

## Gap type 1 — Structural completeness (section-schema check)

Define the **canonical `#` sections** expected of each node type, then score every node against its
schema, flagging **missing** sections (a gap to *fill*) and **thin** sections (a gap to *enrich*).

A reasonable default schema (adjust per bundle/domain):

| Type | Expected `#` sections |
| :-- | :-- |
| `concept` | `# Definition`, topic sections, `# Evaluation` (balanced criticisms), `# Related`, `# References`/`# Citations` |
| `entity` | `# Definition`, `# Key contributions`, `# Significance`, `# Related`, `# References` |
| `reference` | `# What it is`, `# What this brain draws from it`, `# Where it lives`, `# Related` |
| `playbook` | `# Goal`, `# Inputs → Outputs`, `# Steps`, `# How to judge`, `# Guardrails`, `# Hand-off` |

Score each node → `{node, missing: [...], thin: [...]}`. "Thin" = a section present but far below the
depth bar (e.g. a `# Evaluation` with one line). Rank by **centrality** (well-linked hubs first) and, if
you have it, **traffic**.

## Gap type 2 — Coverage (missing nodes)

Topics the brain *should* have but doesn't. Strongest signals first:

1. **Named-but-nodeless (strongest — the brain's own writing implies the gap).** A person/theory/source
   the prose *names* (or a `# References` surname) with **no matching node**. High precision: if 20 nodes
   mention someone with no entity node, they deserve one.
2. **Broken / absent internal links** — a `[Title](/…/x.md)` whose target doesn't exist yet (the spec
   *tolerates* these as "not-yet-written knowledge"; gap-scan turns them into a to-do).
3. **External-hub diff (discovery lens ONLY).** Crawl an authoritative hub for the domain (e.g. a
   Wikipedia category, a syllabus, a source's index) and diff its topic list against live nodes to surface
   structurally-important missing concepts, ranked by centrality.

## Gap type 3 — Source-comparison audit (node ↔ the actual text of a source)

The structural check (type 1) asks *"does the node have the expected `#` sections?"* — a schema can't see
that a present section is **shallow, hand-wavy, or wrong**. When you hold a **specific source** in hand (an
uploaded PDF/textbook, a synced notebook, a canonical primary) that a node draws on or should, audit the node
**against that source's real text** for four failure points:

1. **Topic gap** — a theory, researcher, study, criticism, worked example, or application in the source but
   absent from the node.
2. **Keyword gap** — technical terminology a definitive treatment uses (e.g. "long-term potentiation",
   "reciprocal inhibition") that the node never names.
3. **Depth / mechanistic gap (the high-value one)** — the node states a conclusion but skips the *mechanics*
   the source explains. If the node says a neuron "fires" but the source describes the sodium–potassium pump
   and the action-potential threshold, that is a depth gap. Prefer mechanism over hand-waving.
4. **Recency gap** — a claim/figure in the node that newer material in the source supersedes.

**Verbatim verification** is part of this pass and catches the highest-value errors: check every **quotation
and statistic** in the node against the source's actual text and flag misquotes/misattributions — they hide
even in flagship nodes (a real case: a hierarchy-of-needs node rendered Maslow's 1943 line "…if he is to be
ultimately *happy*" as "…*at peace with himself*" and misdated it 1968; only reading the primary caught it).

Report each finding as: **Gap Type · Missing piece · Evidence from the source (quote/summarise) · Impact ·
Fix** (a high-rigour paragraph to bridge it). Note that mature, well-built nodes are often already complete at
*textbook* depth — so this audit yields **corrections and mechanistic detail more than bulk**; front-load nodes
whose source is a **citable primary** (where verbatim verification pays off), and don't pad.

## Gap type 4 — Searcher-demand (the 100-question audit)

Types 1–3 are **supply-side**: does the node cover its expected sections and the sources it draws on? Type 4 is
**demand-side**: does the node answer *what a real person searching this topic would ask?* This is the sharpest
test for **deciding whether/what to enrich** a node, and for capturing **answer-box / featured-snippet** traffic
and full **topical coverage**. Run it in the voice of an SEO strategist — critical, detailed, results-oriented,
aiming for comprehensive coverage.

Method:

1. **Embody the searcher — generate ~100 questions.** Write ~100 highly relevant questions a user searching the
   topic would likely have, spread across **intent clusters**, not 100 rewordings of one: *what-is / one-line
   definition*, *how it works (mechanism)*, *discovery & history*, *who / where*, *types & sub-kinds*, *functions
   & uses*, *applications & self-help*, *comparisons* ("X vs Y", "difference between…"), *controversy & criticism*,
   *development & evolution*, and *quick-fact / everyday-example / FAQ* queries (the ones that win answer boxes).
   Breadth of intent is the goal.
2. **Fix the unit of analysis.** For an *enrichment decision*, analyse the **node as it stands**; to scope *what a
   comprehensive article should cover*, analyse a candidate **source/URL**. If a URL can't be fetched, ask for the
   content pasted in. Don't analyse a node that is being actively rewritten.
3. **Verdict each question** against the content: **✓** clear, obvious answer · **◐** partial/weak · **✗** no
   clear answer = an **opportunity**.
4. **Turn each opportunity into drop-in copy.** For every ✗, give the **question**, **three** ready-to-use text
   options, and the **exact placement** (which `#`/`##` section — existing, or a new one to add). The suggested
   text must be factually sound and **primary-attributable** — a *draft to verify and cite*, never fabricated (see
   Guardrails).
5. **Score & prioritise.** Report a coverage score (answered / partial / gap, out of 100) and a **prioritised
   opportunity list** — highest answer-box + topical-coverage impact first. This list feeds the enrichment brief
   directly.

**Reading the result.** This audit discriminates best on a **reasonably complete** node: on a very thin node
nearly every question is a gap, so the finding collapses to "enrich" — but the opportunity list then doubles as
the **enrichment spec**. On a mature node it surfaces the *subtle residual gaps* and high-value FAQ / answer-box
additions that a schema check (type 1) and even a source audit (type 3) miss, because it starts from **reader
demand** rather than from what any one source happens to contain.

## Output & double duty

A ranked report with, per node, **(a) missing/thin sections** (type 1), a **source-comparison gap table**
(type 3: each gap's Type · Missing piece · Evidence · Fix, plus any quote/stat corrections), a
**searcher-demand coverage score + prioritised opportunity list** (type 4: each opportunity's question · three
drop-in texts · placement), and across the brain **(b) missing-node candidates** (type 2). It serves two
consumers:
- **okf-ingest-source** reads it to route a new source to the *exact section of the exact node* it should
  feed (step 1 of that loop).
- **A human** reads it as the standalone **enrichment backlog** — what to deepen next, prioritised by
  centrality/traffic rather than scanning the whole corpus by hand.

## Guardrails
- **Discovery signal, not an auto-writer.** Gap-scan *finds* gaps; filling them is enrichment work
  (**okf-concept-node** / **okf-node-types**), done in your own words and cited to **primary** sources.
- **A source read for depth is not automatically a citation.** In the type-3 audit you read textbooks/notebooks
  to *find* depth and mechanism, but the fix cites the **original/primary** work the claim belongs to — never
  the textbook or notebook you happened to read it in. Verify quotes verbatim before trusting them.
- **External hubs are a lens, never a source.** Use a Wikipedia/hub crawl only to *notice* a gap; write
  the node from a real source and **never cite the hub**.
- **Proportional effort.** Don't try to bring every node to flagship depth — rank by centrality/traffic
  and enrich top-down; log what you deliberately deprioritised.
- **Drop-in text is a draft, not a citation.** The type-4 audit proposes copy to *close* a searcher gap, but
  every suggested sentence is a draft to verify and cite to a **primary** source before it enters a node —
  never fabricate a stat, quote, or DOI to answer a question, and prioritise by answer-box/coverage impact
  rather than mechanically filling all 100 (log what you deprioritised).

## Related skills
- **okf-ingest-source** — consumes this report to place new material precisely.
- **okf-concept-node** / **okf-node-types** — how to fill a flagged gap to standard.
- **okf-create-bundle** — the maintenance loop and the (stricter-than-spec) quality bar.
