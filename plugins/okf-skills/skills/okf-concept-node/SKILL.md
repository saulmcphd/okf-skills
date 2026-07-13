---
name: okf-concept-node
description: >-
  Author a single OKF concept node — the structure of a concept.md file in an Open Knowledge Format
  "second brain": YAML frontmatter, a maximum-detail self-contained body, conventional sections, and
  bundle-relative markdown interlinks. Use this when the user wants to write, add, or structure a
  concept node / knowledge node in an OKF bundle, asks "how do I format a concept.md", or wants to add
  knowledge to a second brain — for ANY domain (gardening, academic, psychology, a wiki). The same
  frontmatter + body shape also covers entity, reference, and system nodes (only the type and slug
  prefix change). To scaffold the bundle first, use okf-create-bundle; for procedure nodes, use
  okf-write-playbook.
---

# Author an OKF concept node

A **concept** node holds one unit of *knowledge* — a definition, rule, method, model, or debate. This
skill is the file-structure spec for one `concept-<slug>.md`. It is **domain-agnostic**.

> If the repo has an `okf-gold-standard.md`, follow its project-specific extensions (e.g. required
> `provenance` fields, citation style). This skill is the self-contained baseline.

## Filename & identity

- Path: `concepts/concept-<slug>.md` (e.g. `concepts/concept-companion-planting.md`).
- **The file path IS the node's id.** Do not add an `id` field, and do not rename casually — links
  point at the path.
- Sibling types use the same body shape with a different `type:` and slug prefix:
  `entities/entity-<slug>.md`, `references/ref-<slug>.md`, `systems/system-<slug>.md`.

## Frontmatter (YAML)

Only `type` is required; the rest are recommended and **queryable**:

```yaml
---
type: concept
title: "Human-readable title"
description: "One sentence an agent uses (via index.md) to decide if THIS is the file it needs."
resource: "https://…   # canonical source URL — a provenance pointer, NOT a content crutch"
tags: [topic, subtopic, source-tag]
timestamp: 2026-07-11           # ISO-8601 date or datetime
---
```

- Write `description` to be **self-selecting**: it is the only line the reader sees in `index.md`, so it
  must let them decide to open the file without opening it. Think of the whole frontmatter as an *index
  card* an agent reads to know what the file is about before reading the body.
- **`type` may be descriptive.** It normally matches the folder (`concept`), but OKF also permits a more
  specific label (e.g. `BigQuery Table`, `Evaluation Framework`). If you use descriptive types, keep them
  consistent so the index and graph can still group by them — and always place the node in the right
  canonical folder.
- **For any AI-generated node, add a `provenance` block:**

  ```yaml
  provenance:
    ai_model: claude-opus-4-8     # exact model + version, never just "Claude"
    ai_provider: anthropic
    prompt_file: session-authored
    prompt_version: v1
    human_verified: false         # true only after a human checks it
  ```

- **Do NOT** add an `id` field (the filename is the id) or a `links:` array (interlinking lives in the
  body — see Interlinking).

## Body — MAXIMUM detail, structural markdown

- **Self-contained — no dangling source references.** Embed *all* the relevant knowledge from the
  source: every definition, list item, step, threshold, formula, worked example, and caveat. The reader
  does **not** have the source, so **never point at its artifacts**: no "**Table 1**", "**Fig. 2**", "the
  diagram/table **above**", "see **chapter** 3", "**overleaf**", "on **p. 42**". Instead **bring the
  content in** — transcribe a table as a markdown table, describe in prose what a figure shows, restate
  the referenced point. (`resource` + the citations section handle *provenance*; the body must stand
  *alone*.) A page number is legitimate only inside a citation for a direct quote — `(Author, Year, p. 42)`.
- **Maximum, not minimum.** Length is not a cost — the index makes the file findable. When in doubt,
  include more. A reader should never need to open the source to understand the topic.
- **Citation discipline.** Base every factual claim on the source; quote verbatim for lists / numbers /
  definitions. **Never fill a genuine gap with outside knowledge** — if the source doesn't cover
  something, link to the concept that does; don't invent.
- **Synthesise across sources, don't list them.** When a node draws on more than one source, weave them
  by *theme* — consensus, tension, nuance — not source-by-source ("Gross says…; the IB text says…"). A
  well-synthesised node reads as one coherent account, not a stack of summaries. See the
  **information-synthesis** skill.
- **Verify numbered ranges against the FULL source**, not a truncated/`head`-limited view, before
  trusting *or* flagging a numbered item.
- **Integrate, don't duplicate.** Before creating a node, check `index.md` for one that already covers
  the topic — *enrich or revise* it rather than adding a near-duplicate. When a new source **contradicts**
  an existing claim, surface the contradiction (state both, each dated and sourced) instead of silently
  overwriting; a brain that hides disagreement is worse than one that records it.
- **Favor structure — mirror the source's shape.** Prefer headings, lists, tables, fenced code over
  freeform prose. **When the source presents a bulleted or numbered list, keep it as a markdown list**
  (`- item` / `1. item`) rather than flattening it into a paragraph. **When it presents data as a table,
  reproduce it as a real markdown table** (`| col | col |` with a `|---|---|` separator row) — not a
  prose summary, and never a pointer like "see Table 1". Structure preserved this way keeps the node
  self-contained *and* renders properly in the dashboard's node reader (lists, tables, code — see
  okf-dashboard).

### Conventional sections (`# Definition` first, `# Citations` last)

```
# Definition
…the precise definition…

# <Topic sections with tables/lists embedding the FULL detail>

# Expert opinion          # OPTIONAL (human-experience topics only) — attributed analysis from a named, VERIFIED expert; see E-E-A-T below
# Lived experience        # OPTIONAL (human-experience topics only) — attributed first-hand personal narrative

# Related
* [Other concept title](/concepts/concept-x.md) - why it's related
* [A playbook](/playbooks/playbook-y.md) - where this is applied

# Expert & experiential sources   # OPTIONAL — provenance for the two attributed sections above; kept SEPARATE from # Citations/# References
- Expert, A. (Year). [Talk / interview / book title]. Venue. https://…

# Citations
[1] Author. Title. Year. https://doi.org/…
```

## Interlinking

- Link to other nodes with **bundle-relative absolute markdown links** (recommended):
  `[Title](/concepts/concept-x.md)`, `[Title](/playbooks/playbook-y.md)`. Relative `./other.md` is also
  valid.
- Put the main cross-links in a **`# Related`** section; inline links in the prose are fine too.
- **Do NOT use `[[wikilinks]]`** — they are Obsidian-only; OKF tooling parses markdown links.

## Worked skeleton (domain-neutral — a gardening concept)

```markdown
---
type: concept
title: "Companion planting"
description: "Placing mutually beneficial plants together to deter pests, attract pollinators, and lift yield — principles, classic pairings, and cautions."
resource: "https://www.rhs.org.uk/advice/companion-planting"
tags: [companion-planting, pest-control, vegetable-garden]
timestamp: 2026-07-11
provenance:
  ai_model: claude-opus-4-8
  ai_provider: anthropic
  prompt_file: session-authored
  prompt_version: v1
  human_verified: false
---
# Definition
Companion planting is the practice of growing particular species near one another so that at least one
benefits — through pest deterrence, pollinator attraction, nutrient sharing, or physical support.

# Mechanisms
| Mechanism | How it works | Example pairing |
| :-- | :-- | :-- |
| Pest confusion | Strong scents mask the host crop | Carrots + onions |
| Trap cropping | A sacrificial plant lures pests away | Nasturtium + brassicas |
| Nitrogen sharing | Legumes fix nitrogen for heavy feeders | Beans + corn |

# Classic pairings
* Tomatoes + basil — basil is said to deter whitefly…
* The "three sisters" — corn, beans, squash…

# When it fails / cautions
Evidence is uneven; some pairings are folklore. Avoid pairing heavy feeders that compete for the same
nutrients…

# Related
* [Crop rotation](/concepts/concept-crop-rotation.md) - the complementary temporal practice.
* [Spring bed preparation](/playbooks/playbook-spring-bed-prep.md) - where pairings are laid out on the ground.

# Citations
[1] Royal Horticultural Society. Companion planting. https://www.rhs.org.uk/advice/companion-planting
```

## Citing sources (especially for an academic brain)

Provenance in the body lives in a citations section — `# Citations` (numbered, the OKF-spec convention)
or, for a scholarly brain, `# References` (an alphabetised APA/Vancouver-style list). Pick **one** style
per bundle and be consistent. For an **academic / research brain**, apply this discipline:

- **Cite PRIMARY sources, not the secondary text you read them in.** If a textbook summarises Milgram's
  1963 study, cite Milgram (1963) — not the textbook. Re-attribute each claim to the original work.
- **In-text + list.** Put `(Author, Year)` in the prose **and** a matching entry in `# References` for
  every cited work, in one consistent style.
- **Provenance ≠ citation.** Record *what you wrote the node from* as frontmatter provenance (e.g. a
  `source-<slug>` tag / `primary_source`), kept **separate** from the scholarly citations — the reader
  sees citations, the pipeline tracks provenance.
- **Never fabricate.** No invented citations or DOIs; if a generic fact has no clear primary source,
  leave it uncited rather than guessing.
- **Draw from the bibliography registry.** In an academic brain, pull each `# References` entry from the
  shared references registry (one verified record per work) rather than re-typing it, so citations are
  consistent and every one resolves to a real source — see **okf-bibliography**.
- **Match the house style.** If the brain backs a specific publication or site, mirror its citation
  style and depth. Pin the rules once in a bundle-level `CITATION-STYLE.md` (see okf-create-bundle).

(A non-academic brain — e.g. gardening — can keep this light: a `# Related` link or a single source URL
is often enough. The discipline above scales *up* for scholarly work; it isn't mandatory for every brain.)

## Expert opinion & lived experience (the first two E's of E-E-A-T)

Peer-reviewed citations give a node **Authoritativeness and Trustworthiness**. Two further quality signals —
**Experience** (first-hand, lived) and **Expertise** (a named authority's analysis) — answer a *different*
question than the evidence base does: not "is this claim true?" but "how do knowledgeable people interpret it,
and how do people who have lived it experience it?" On applied, human-facing topics (mental health,
relationships, coping, wellbeing; or, in a gardening brain, hands-on craft) these add the "huh, never knew
that" insight and the relatable first-person texture a purely academic node lacks. Capture them in **two
optional `#` sections, kept clearly separate from the evidence layer**:

- **`# Expert opinion`** — attributed analysis/interpretation from a named, verified expert (e.g. a clinician's
  view on *why* a technique works; a horticulturist's rule of thumb).
- **`# Lived experience`** — first-hand personal narrative: what the thing is actually like from someone who
  has been through it. Sources include published memoirs / first-person essays, verbatim participant quotes
  from qualitative studies, or on-the-record personal accounts.

**When to include (topic-gated, optional).** Expect them on human-experience topics — mental health,
relationships, coping, life challenges, applied practice. **Omit both** on pure mechanism / method / history
nodes (e.g. "action potential", "counterbalancing", "the founding of Wundt's lab") where lived experience is
irrelevant and there is no distinct expert opinion beyond the literature. **Never pad a node with an empty
section** — leave the sections out when they don't apply.

**Three rules that keep the attributed layer honest:**

1. **Label the epistemic status.** The `# Expert opinion` / `# Lived experience` heading tells the reader
   "this is viewpoint / narrative, *not* peer-reviewed fact." Never blur the two.
2. **Attribute, never launder.** Always name the person *and* the exact source in the prose — "On the
   *Huberman Lab* podcast, Andrew Huberman argues…", "In *Feeling Good*, David Burns describes…", "Monty Don
   recommends…". Opinion is always on the record as someone's view, never voiced as the node's own.
3. **Trace empirical claims to a primary anyway.** If an expert states a *fact* ("X raises dopamine ~250%"),
   that fact still needs the underlying study cited in `# References` — the interview is where you *found* it;
   the study is what you *cite*. Only genuine opinion / interpretation / lived narrative stays in the
   attributed sections.

**Record the sources SEPARATELY — not in `# References`.** Keep `# References` for primary/original works only
(the citation rules above). Put expert-opinion and lived-experience provenance in a distinct
**`# Expert & experiential sources`** list (or attribute fully inline). This preserves the primary-only
guarantee of `# References` while still crediting the source, e.g.
`Huberman, A. (Year). [Episode title]. Huberman Lab podcast. https://…`.

**The expertise gate — is this person actually an expert?** Before treating anyone as a citable expert,
verify genuine, *topical* authority. Two conditions, **both** required:

- **Established public standing** — a Google **Knowledge Panel** is a good first filter (it is Google's own
  entity-authority signal); an equivalent (a Wikipedia biography, a named institutional post) also works.
- **Genuine credentials in *this* topic** — a relevant qualification, an academic / clinical / professional
  position, or a recognised body of work in the field. A Knowledge Panel **alone is not enough**: a celebrity
  has one without topical expertise; a neuroscientist is an authority on neuroscience, not on nutrition.

Podcasts and YouTube interviews **may** be quoted as **attributed expert opinion** once the speaker passes
this gate — but only as opinion, never as fact (rule 3), and **note any documented reliability caveat** for
that speaker right where you quote them (e.g. a host with a flagged tendency to overstate), preferring to
trace their factual claims to the primary literature.

**Give a recurring expert their own entity node.** When an expert is quoted across several nodes, create an
`entity-<name>` node recording who they are, their expertise domain, *why* they qualify (the Knowledge-Panel /
credential check), and any reliability caveat — then link every quoting node to it. The "is this person an
expert?" judgement then lives in one authoritative place instead of being re-litigated per node.

## Quality bar

- `type` present + queryable fields filled; AI nodes carry `provenance`.
- Self-contained and maximally detailed — no "see the source" deferrals.
- `# Related` present where relevant; links are bundle-relative markdown (no wikilinks).
- On human-experience topics, `# Expert opinion` / `# Lived experience` present, each **attributed** to a
  gated expert or a named first-hand account, with provenance in `# Expert & experiential sources` (never in
  `# References`); opinion is never stated as fact, and any factual claim traces to a primary. Omitted (not
  empty) on pure method / mechanism / history nodes.
- Would survive `lint`: not a **thin** stub, no orphan links.
