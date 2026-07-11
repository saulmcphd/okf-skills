# OKF Skills

Seven skills for building and using an **OKF (Open Knowledge Format)** "second brain" — a portable,
vendor-neutral graph of interlinked markdown files that both humans and AI agents can read. No database,
no runtime, no embeddings.

These skills are **domain-agnostic**: use them to build a gardening brain, an academic/research brain, a
company wiki, or anything else. They're distilled from Google's OKF spec and two reference
implementations (see [Credits](#credits)).

> **What is OKF?** A bundle is just a directory of markdown files. Each file is one node with YAML
> frontmatter and a body that links to other nodes with ordinary markdown links. An agent reads
> `index.md` first, then opens only the few nodes relevant to its task — curated navigation instead of
> vector search. Spec: `GoogleCloudPlatform/knowledge-catalog/okf/SPEC.md`.

## The skills (a full lifecycle)

| Stage | Skill | What it does |
| :-- | :-- | :-- |
| **Scaffold** | `okf-create-bundle` | Create the folder structure + `index.md`/`log.md`, the build process, and the compounding maintenance loop. |
| **Author** | `okf-concept-node` | Write a concept node: frontmatter, a maximum-detail self-contained body, `# Related`, and citations. |
| | `okf-node-types` | Write the non-concept nodes: **entity**, **reference** (the one-per-source provenance layer), and **system**. |
| | `okf-write-playbook` | Write a playbook: a reproducible, step-by-step procedure node. |
| **Cite** | `okf-bibliography` | *Academic brains:* manage the references registry (`references.json`) — verified **primary** citations, no fabrication. |
| **Use** | `okf-dashboard` | Build a graph explorer (see the brain) + an ask-the-brain grounded Q&A (query it). |
| **Grow** | `okf-ingest-source` | Add a new PDF/URL safely: assess → **human approves** → enrich (new node vs. enrich existing). |
| **Maintain** | `okf-gap-scan` | Find what's incomplete (missing/thin sections + coverage gaps) → a ranked enrichment backlog. |

The skills cross-reference each other, so an agent chains them naturally (scaffold → author → use → grow
→ maintain).

## Install

### Claude ecosystem (Claude Code) — one-click, auto-triggering

```
/plugin marketplace add YOUR-GITHUB-USERNAME/okf-skills
/plugin install okf-skills@okf-skills
```

Once installed, the right skill triggers automatically — e.g. *"help me start a gardening second brain"*
surfaces `okf-create-bundle`; *"add a concept node for composting"* surfaces `okf-concept-node`. Agent
Skills also work in the Claude apps and the Claude Agent SDK.

### Using with other agents (Gemini, ChatGPT / Codex, etc.)

The auto-triggering plugin mechanism is Claude-specific, **but the skills are just markdown instruction
files**, so any agent can use their content:

- **Point your agent at this repo** and ask it to follow the relevant `skills/*/SKILL.md`.
- **Or paste** the `SKILL.md` you need into the conversation / add it as a context or knowledge file
  (e.g. a Gemini `GEMINI.md`, a Codex `AGENTS.md`, or a custom-GPT knowledge file).

The **OKF bundles you build are fully model-neutral** — that's the whole point of the format. Only the
convenience of automatic triggering is Claude-specific.

## Repository layout

```
okf-skills/
├── .claude-plugin/
│   └── marketplace.json          # makes the repo installable as a marketplace
├── plugins/
│   └── okf-skills/
│       ├── .claude-plugin/
│       │   └── plugin.json        # the plugin manifest
│       └── skills/
│           ├── okf-create-bundle/SKILL.md
│           ├── okf-concept-node/SKILL.md
│           ├── okf-node-types/SKILL.md
│           ├── okf-bibliography/SKILL.md
│           ├── okf-write-playbook/SKILL.md
│           ├── okf-dashboard/SKILL.md
│           ├── okf-ingest-source/SKILL.md
│           └── okf-gap-scan/SKILL.md
├── README.md
└── LICENSE
```

## Credits

Distilled from **Google's OKF specification** (`GoogleCloudPlatform/knowledge-catalog/okf/SPEC.md`), and
enriched with two reference implementations: **Andrej Karpathy's "LLM wiki" pattern** (the compounding,
agent-maintained knowledge base) and **Marie Haynes' OKF brain** ([mariehaynes.com/okf](https://www.mariehaynes.com/okf/)).
Conceptual ancestor: the LLM-wiki idea of a knowledge base an agent reads by navigation, not retrieval.

## License

MIT © Saul McLeod — see [LICENSE](LICENSE).
