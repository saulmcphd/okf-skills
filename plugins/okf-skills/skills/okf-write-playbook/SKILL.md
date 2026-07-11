---
name: okf-write-playbook
description: >-
  Author a single OKF playbook node — a reproducible, step-by-step procedure ("runbook") for one stage
  of work in an Open Knowledge Format "second brain." Covers the playbook.md frontmatter (concept keys
  plus procedure fields), the "fuse two sources" authoring method, and the action-oriented H1 body
  sections (Goal, Inputs → Outputs, Steps, How to judge, Guardrails, Concepts used, Skills & scripts,
  Hand-off). Use this when the user wants to create/write a playbook, add a procedure or runbook node,
  or asks "how do I structure a playbook.md" — for ANY domain (gardening, academic, ops). A concept
  holds the knowledge; a playbook says what to do, in order. To scaffold the bundle first use
  okf-create-bundle; for the knowledge nodes a playbook links to, use okf-concept-node.
---

# Author an OKF playbook node

A **playbook** is the *procedure* layer of an OKF bundle: a reproducible, actionable runbook for one
stage of the work. A **concept** holds the *knowledge* (definitions, rules, thresholds); a playbook
says **what to do, in order**, and links the concepts that justify each rule. This skill is
**domain-agnostic**.

> If the repo has an `okf-gold-standard.md`, follow its project-specific extensions. This skill is the
> self-contained baseline. (Note: a bundle can be knowledge-only — playbooks are added when there's a
> repeatable procedure worth capturing.)

## Filename & identity

- Path: `playbooks/playbook-<slug>.md` (e.g. `playbooks/playbook-spring-bed-prep.md`).
- The file path is the node id. No `id` field, no `links:` array.

## How to build the `# Steps` — fuse two sources

Build the procedure by **fusing two inputs**:

1. **The operational step sequence** from the authoring **skill/tool** for this stage — lift and
   *adapt* it to this bundle; don't re-derive it.
2. **The concept knowledge** — each step **links the concept(s) that justify its rule/threshold**.

Select the relevant concepts by reading `index.md` (curated navigation). Where a skill step and a
concept conflict, **the concept wins** (it's grounded in the primary standard) — and you note it.
Mental model: a triage runbook — *when this fires → do this → how to weigh it → guardrails*.

## Frontmatter (YAML)

The standard concept keys **plus** procedure-specific, queryable fields:

```yaml
---
type: playbook
title: "Human-readable stage title"
description: "One sentence an agent uses (via index.md) to decide if THIS procedure is the one it needs."
resource: "https://…   # canonical source for the procedure, if any"
tags: [stage-tag, domain-tag]
timestamp: 2026-07-11
stage: bed-prep                # short stage key
stage_number: "1"             # optional ordering within a pipeline
status: built                  # draft | built | deprecated
provider_agnostic: true        # true if it doesn't hard-depend on one vendor/tool
uses_skills: []                # authoring skills this stage runs
scripts: []                    # scripts/tools that perform it
inputs: [garden-plan.md]       # what it consumes
outputs: [this-season-layout.md]  # the artefacts it writes
provenance:
  ai_model: claude-opus-4-8
  ai_provider: anthropic
  prompt_file: session-authored
  prompt_version: v1
  human_verified: false
---
```

Add `data_sources` / `mcp_tools` where relevant. Omit fields that don't apply.

## Body — action-oriented H1 sections

```
# Goal             — what this stage produces and when it runs (its trigger / place in the pipeline)
# Inputs → Outputs — what it consumes and the artefacts it writes (the join spine)
# Steps            — numbered, do-this-then-that; each step links the concept(s) that justify it and names the skill/script that performs it
# How to judge     — the decision points and thresholds, each linked to the concept holding the rule
# Guardrails       — the non-negotiables (the fail-safe defaults, human-in-the-loop rules, provenance, do-not-regress)
# Concepts used    — the concept nodes this procedure draws on (the knowledge layer)
# Skills & scripts — the authoring skills + scripts that implement it
# Hand-off         — what the next stage consumes
```

An optional `# Example` section (illustrative, "fill every bracket from your bundle; never invent a
number") sits well between `# Steps` and `# How to judge`.

## The judging bar (definition of done)

A playbook is judged on whether **a competent person could execute the stage from it alone**, opening
the linked concepts only when they need the underlying rule. If they'd have to guess, the step is too
thin or a concept link is missing.

## Worked micro-skeleton (domain-neutral — a gardening playbook)

```markdown
---
type: playbook
title: "Spring bed preparation"
description: "Get a vegetable bed ready for spring planting — clear, amend, and lay out beds per companion-planting and rotation rules."
tags: [spring, bed-prep, vegetable-garden]
timestamp: 2026-07-11
stage: bed-prep
status: built
provider_agnostic: true
inputs: [garden-plan.md, last-season-layout.md]
outputs: [this-season-layout.md]
provenance:
  ai_model: claude-opus-4-8
  ai_provider: anthropic
  prompt_file: session-authored
  prompt_version: v1
  human_verified: false
---
# Goal
Turn an over-wintered bed into a planted, correctly laid-out spring bed, ready for sowing.

# Inputs → Outputs
**Consumes** last season's layout + this year's plan. **Writes** `this-season-layout.md` (what goes where).

# Steps
1. Clear weeds and spent crops; test soil pH.
2. Amend with compost to the depth the crop needs.
3. Assign beds so no family follows itself ([crop rotation](/concepts/concept-crop-rotation.md)).
4. Place mutually beneficial pairings within each bed ([companion planting](/concepts/concept-companion-planting.md)).

# How to judge
- No plant family repeats its last-season bed ([crop rotation](/concepts/concept-crop-rotation.md)).
- Every heavy feeder has a compatible neighbour, no antagonistic pairings ([companion planting](/concepts/concept-companion-planting.md)).

# Guardrails
- Never plant into un-amended, compacted soil.
- Record the final layout before sowing — next spring's rotation depends on it.

# Concepts used
- [Crop rotation](/concepts/concept-crop-rotation.md) — the temporal rule the bed assignment obeys.
- [Companion planting](/concepts/concept-companion-planting.md) — the within-bed pairing rules.

# Skills & scripts
- Skill (authoring): (none — manual stage). Scripts: (none).

# Hand-off
- `this-season-layout.md` → the sowing/planting stage.
```
