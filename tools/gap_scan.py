"""gap_scan.py — OKF completeness + coverage gap scanner (reference implementation of okf-gap-scan).

Scores every node's `#` sections against a per-type schema (missing / thin / ok), ranks the
incomplete nodes by in-degree centrality, finds missing-node candidates (broken links — a target
your nodes reference but no node exists for), and writes:

  - <bundle>/gaps.json          — the full machine-readable enrichment backlog
  - <bundle>/gap-dashboard.html — a self-contained viewer (real data injected into the template)

Self-contained and domain-agnostic. Drop `tools/` into your bundle and run from the bundle root, or
point it anywhere with --bundle. EDIT the SCHEMA below to match your bundle's section conventions.

Usage:
  python tools/gap_scan.py
  python tools/gap_scan.py --bundle /path/to/bundle --limit 250 --thin-chars 300
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

# ---- config ------------------------------------------------------------------
THIN_SECTION_CHARS = 250     # a prose section shorter than this is "thin"
MIN_RELATED_LINKS = 2        # a # Related with fewer outgoing links is "thin"
THIN_CONCEPT_CHARS = 3000    # a concept shorter than this is a stub (Evaluation not expected)
CAND_CAP = 30

TYPE_BY_FOLDER = {"concepts": "concept", "entities": "entity", "references": "reference",
                  "systems": "system", "playbooks": "playbook"}

# EDIT THIS for your bundle. spec = (display_name, [heading aliases], kind).
# kind: "prose" (thin if < THIN_SECTION_CHARS) | "related" (thin if < MIN_RELATED_LINKS) | "cite".
# `system` is omitted on purpose — add it if your systems follow a fixed structure.
SCHEMA = {
    "concept": [
        ("Definition", ["Definition"], "prose"),
        ("Evaluation", ["Evaluation", "Criticisms", "Limitations"], "prose"),   # scored only for detailed concepts
        ("Related", ["Related"], "related"),
        ("References", ["References", "Citations"], "cite"),
    ],
    "entity": [
        ("Definition", ["Definition"], "prose"),
        ("Related", ["Related"], "related"),
        ("References", ["References", "Citations"], "cite"),
    ],
    "reference": [
        ("What it is", ["What it is"], "prose"),
        ("Related", ["Related"], "related"),
    ],
    "playbook": [
        ("Goal", ["Goal"], "prose"),
        ("Steps", ["Steps"], "prose"),
        ("Related", ["Related", "Hand-off"], "related"),
    ],
}

# ---- bundle IO (self-contained; no external deps) ----------------------------
LINK_RE = re.compile(r"\[([^\]]*)\]\(((?:/|\./|\.\./)[^)#\s]+\.md)\)")
H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.M)


def parse_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?", text, re.DOTALL)
    if not m:
        return {}, text
    fm_text, body, fm = m.group(1), text[m.end():], {}
    for line in fm_text.splitlines():
        s = line.strip()
        if not s or s.startswith("#") or ":" not in s or (len(line) - len(line.lstrip())) > 0:
            continue
        k, _, v = s.partition(":")
        fm[k.strip()] = v.split(" #")[0].strip().strip('"').strip("'")
    return fm, body


def norm_target(t: str) -> str:
    return "/" + t.lstrip("./") if t.startswith(("./", "../")) else t


def load_nodes(bundle: Path) -> dict[str, dict]:
    nodes = {}
    for folder in TYPE_BY_FOLDER:
        d = bundle / folder
        if not d.is_dir():
            continue
        for f in sorted(d.glob("*.md")):
            if f.name.lower() in ("index.md", "readme.md"):
                continue
            fm, body = parse_frontmatter(f.read_text(encoding="utf-8"))
            rel = f"/{folder}/{f.name}"
            nodes[rel] = {"path": rel, "folder": folder, "fm": fm, "body": body,
                          "title": fm.get("title") or f.stem,
                          "type": fm.get("type", TYPE_BY_FOLDER[folder])}
    return nodes


def links_with_text(body: str):
    return [(text, norm_target(t)) for text, t in LINK_RE.findall(body)]


# ---- scoring -----------------------------------------------------------------
def split_sections(body: str) -> dict[str, str]:
    out, ms = {}, list(H1_RE.finditer(body))
    for i, m in enumerate(ms):
        end = ms[i + 1].start() if i + 1 < len(ms) else len(body)
        out[m.group(1).strip().lower()] = body[m.end():end].strip()
    return out


def heading_matches(h: str, a: str) -> bool:
    h, a = h.lower(), a.lower()
    return h.startswith(a) and (len(h) == len(a) or h[len(a)] in " (:,-s/&")


def find_section(aliases, secmap):
    for h, content in secmap.items():
        if any(heading_matches(h, a) for a in aliases):
            return content
    return None


def schema_for(node: dict):
    specs = SCHEMA.get(node["type"])
    if node["type"] == "concept" and len(node["body"]) < THIN_CONCEPT_CHARS and specs:
        specs = [s for s in specs if s[0] != "Evaluation"]   # don't expect Evaluation on a stub
    return specs


def score_section(spec, secmap, thin_chars):
    display, aliases, kind = spec
    content = find_section(aliases, secmap)
    if content is None:
        return {"name": display, "state": "missing"}
    if kind == "related":
        n = len(links_with_text(content))
        if n < MIN_RELATED_LINKS:
            return {"name": display, "state": "thin", "note": f"only {n} outgoing link{'' if n == 1 else 's'}"}
    elif kind == "cite":
        if not [ln for ln in content.splitlines() if ln.strip()]:
            return {"name": display, "state": "thin", "note": "section is empty"}
    elif len(content) < thin_chars:
        return {"name": display, "state": "thin", "note": f"only {len(content)} chars"}
    return {"name": display, "state": "ok"}


def broken_link_candidates(nodes: dict) -> list:
    """Missing-node candidates: link targets your nodes reference but no node exists for."""
    agg: dict[str, dict] = {}
    for n in nodes.values():
        for text, target in links_with_text(n["body"]):
            if target in nodes:
                continue
            d = agg.setdefault(target, {"count": 0, "texts": Counter(), "refs": []})
            d["count"] += 1
            if text.strip():
                d["texts"][text.strip()] += 1
            if len(d["refs"]) < 3:
                d["refs"].append({"title": n["title"], "type": n["type"]})
    cands = []
    for target, d in agg.items():
        folder = target.strip("/").split("/")[0]
        name = d["texts"].most_common(1)[0][0] if d["texts"] else target.split("/")[-1][:-3]
        cands.append({
            "name": name, "mentions": d["count"],
            "suggestedType": TYPE_BY_FOLDER.get(folder, "concept"),
            "why": f"Linked from {d['count']} node(s) but no node exists at {target}.",
            "refs": d["refs"],
        })
    cands.sort(key=lambda c: -c["mentions"])
    return cands[:CAND_CAP]


def replace_js_array(html: str, varname: str, arr_json: str) -> str:
    m = re.search(rf"const\s+{varname}\s*=\s*", html)
    if not m:
        raise SystemExit(f"template is missing `const {varname} =`")
    j = html.index("[", m.end())
    depth, k, instr, esc = 0, j, None, False
    while k < len(html):
        c = html[k]
        if instr:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == instr:
                instr = None
        elif c in "\"'`":
            instr = c
        elif c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
            if depth == 0:
                break
        k += 1
    return html[:j] + arr_json + html[k + 1:]


def main() -> None:
    args = sys.argv[1:]
    bundle = Path(args[args.index("--bundle") + 1]) if "--bundle" in args else Path(__file__).resolve().parent.parent
    limit = int(args[args.index("--limit") + 1]) if "--limit" in args else 0
    thin_chars = int(args[args.index("--thin-chars") + 1]) if "--thin-chars" in args else THIN_SECTION_CHARS
    template = Path(__file__).resolve().parent / "gap_dashboard_template.html"

    nodes = load_nodes(bundle)
    indeg = {p: 0 for p in nodes}
    for p, n in nodes.items():
        for _, t in {(x, y) for x, y in links_with_text(n["body"])}:
            if t in indeg and t != p:
                indeg[t] += 1
    maxdeg = max(indeg.values(), default=0) or 1

    scanned, incomplete = 0, []
    for p, n in nodes.items():
        specs = schema_for(n)
        if not specs:
            continue
        scanned += 1
        secmap = split_sections(n["body"])
        sections = [score_section(s, secmap, thin_chars) for s in specs]
        if any(s["state"] != "ok" for s in sections):
            incomplete.append({"path": p, "title": n["title"], "type": n["type"],
                               "centrality": round(indeg[p] / maxdeg, 3), "in_degree": indeg[p],
                               "sections": sections})
    incomplete.sort(key=lambda x: (-x["in_degree"], x["path"]))
    candidates = broken_link_candidates(nodes)

    tmiss = sum(sum(s["state"] == "missing" for s in x["sections"]) for x in incomplete)
    tthin = sum(sum(s["state"] == "thin" for s in x["sections"]) for x in incomplete)
    (bundle / "gaps.json").write_text(json.dumps({
        "_note": "Completeness gaps (nodes with >=1 missing/thin section vs their per-type schema) + "
                 "candidate_nodes (broken-link targets with no node). Discovery only. Regenerate with gap_scan.py.",
        "scanned_nodes": scanned, "incomplete_nodes": len(incomplete),
        "missing_sections": tmiss, "thin_sections": tthin, "candidates": len(candidates),
        "nodes": incomplete, "candidate_nodes": candidates,
    }, ensure_ascii=False, indent=1), encoding="utf-8")

    shown = incomplete[:limit] if limit else incomplete
    nodes_js = [{"path": x["path"], "title": x["title"], "type": x["type"],
                 "centrality": x["centrality"], "sections": x["sections"]} for x in shown]
    html = template.read_text(encoding="utf-8")
    html = replace_js_array(html, "NODES", json.dumps(nodes_js, ensure_ascii=False))
    html = replace_js_array(html, "CANDIDATES", json.dumps(candidates, ensure_ascii=False))
    (bundle / "gap-dashboard.html").write_text(html, encoding="utf-8")

    missing_tmpl = Path(__file__).resolve().parent / "missing_nodes_template.html"
    if missing_tmpl.exists():
        mh = replace_js_array(missing_tmpl.read_text(encoding="utf-8"), "CANDIDATES",
                              json.dumps(candidates, ensure_ascii=False))
        (bundle / "missing-nodes.html").write_text(mh, encoding="utf-8")

    print(f"scanned {scanned} nodes -> {len(incomplete)} incomplete ({tmiss} missing + {tthin} thin), "
          f"{len(candidates)} candidates")
    print(f"wrote {bundle / 'gaps.json'}")
    print(f"wrote {bundle / 'gap-dashboard.html'} (table shows {len(nodes_js)})")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
