# OKF tools — runnable reference implementations

Domain-agnostic Python that backs the skills. Drop this `tools/` folder into your own OKF bundle so it
sits at `<your-bundle>/tools/`, then run from the bundle root. **No dependencies beyond the Python
standard library.** These are references to read, copy, and adapt — not a framework.

## `okf_tools.py` — index / graph / lint
*(backs `okf-create-bundle` + `okf-dashboard`)*

```
python tools/okf_tools.py index   # (re)generate index.md + per-folder indexes
python tools/okf_tools.py graph   # self-contained interactive okf-graph.html
python tools/okf_tools.py lint    # orphan links, missing fields, thin concepts, dangling source refs
python tools/okf_tools.py all
```

## `gap_scan.py` — completeness + coverage gaps
*(backs `okf-gap-scan`)*

Scores every node's `#` sections against a per-type schema (missing / thin / ok), ranks the incomplete
nodes by **in-degree centrality**, and finds **missing-node candidates** (broken links — a target your
nodes reference but no node exists for). Writes `gaps.json` + a self-contained `gap-dashboard.html` (the
real data is injected into `gap_dashboard_template.html`, the light-theme viewer from `demo/`).

```
python tools/gap_scan.py
python tools/gap_scan.py --bundle /path/to/bundle --limit 250 --thin-chars 300
```

**Edit the `SCHEMA` dict** at the top of `gap_scan.py` to match your bundle's section conventions — the
default covers the canonical OKF types (concept / entity / reference / playbook).

## `check_source_refs.py` — self-containment check

A self-contained node must **embed** content, never point at a source artifact the reader can't see
("Table 1", "Fig. 2", "see chapter 3", "on p. 42", "the diagram above"). This prints a focused, ranked
report of any node that defers — the same check `okf_tools.py lint` runs (patterns live in
`okf_tools.SOURCE_REF_RULES`; page numbers inside a `# References` citation are not flagged). Aim: 0.

```
python tools/check_source_refs.py
```
