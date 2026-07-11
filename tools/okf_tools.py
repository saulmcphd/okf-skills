"""OKF bundle tooling — reference implementation.

Drop this file into `<your-bundle>/tools/` and run from the bundle root:

  python tools/okf_tools.py index   # (re)generate index.md + per-folder indexes
  python tools/okf_tools.py graph   # write a self-contained interactive okf-graph.html
  python tools/okf_tools.py lint    # orphan links, missing fields, thin concepts
  python tools/okf_tools.py all     # all of the above

It is domain-agnostic: it reads the five canonical OKF folders and every `.md` node's YAML
frontmatter + markdown links. See the `okf-create-bundle` / `okf-dashboard` skills for context.
"""

import json
import re
import sys
from pathlib import Path

BUNDLE = Path(__file__).resolve().parent.parent   # tools/ lives inside the bundle
NODE_FOLDERS = ["concepts", "entities", "references", "systems", "playbooks"]
THIN_CONCEPT_CHARS = 3000  # body length below which a concept is flagged thin

TYPE_COLORS = {
    "concept": "#4f8ef7",
    "entity": "#f7b64f",
    "reference": "#5fc98e",
    "system": "#e05f8a",
    "playbook": "#a86ff7",
}


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Minimal YAML frontmatter parser (flat keys + [list] values + one level of nesting)."""
    if not text.startswith("---"):
        return {}, text
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?", text, re.DOTALL)
    if not m:
        return {}, text
    fm_text, body = m.group(1), text[m.end():]
    fm: dict = {}
    current_nest = None
    for line in fm_text.splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        line_s = line.strip()
        if ":" not in line_s:
            continue
        key, _, val = line_s.partition(":")
        key, val = key.strip(), val.split(" #")[0].strip().strip('"').strip("'")
        if indent > 0 and current_nest is not None:
            fm[current_nest][key] = val
            continue
        if val == "":
            current_nest = key
            fm[key] = {}
        else:
            current_nest = None
            if val.startswith("[") and val.endswith("]"):
                fm[key] = [v.strip().strip('"').strip("'")
                           for v in val[1:-1].split(",") if v.strip()]
            else:
                fm[key] = val
    return fm, body


def load_nodes() -> dict[str, dict]:
    """path (bundle-relative, e.g. /concepts/concept-x.md) -> node info."""
    nodes = {}
    for folder in NODE_FOLDERS:
        d = BUNDLE / folder
        if not d.is_dir():
            continue
        for f in sorted(d.glob("*.md")):
            if f.name.lower() in ("index.md", "readme.md"):
                continue
            text = f.read_text(encoding="utf-8")
            fm, body = parse_frontmatter(text)
            rel = f"/{folder}/{f.name}"
            nodes[rel] = {
                "path": rel, "folder": folder, "file": f, "fm": fm,
                "body": body,
                "title": fm.get("title") or f.stem,
                "description": fm.get("description", ""),
                "type": fm.get("type", folder.rstrip("s")),
                "links": extract_links(body),
            }
    return nodes


LINK_RE = re.compile(r"\[([^\]]*)\]\(((?:/|\./|\.\./)[^)#\s]+\.md)\)")


def extract_links(body: str) -> list[str]:
    links = []
    for _, target in LINK_RE.findall(body):
        t = target
        if t.startswith("./") or t.startswith("../"):
            t = "/" + t.lstrip("./")
        links.append(t)
    return links


# A self-contained node must EMBED content, never point at a source artifact the reader can't see.
SOURCE_REF_RULES = [
    ("numbered figure/table", re.compile(r"\b(?:Table|Figure|Box|Plate|Panel|Diagram|Chart)\s+\d+\b|\bFigs?\.?\s+\d+\b", re.I)),
    ("(see fig/table/chapter…)", re.compile(r"\(\s*see\s+(?:fig|figure|table|box|chapter|section|pp?\.|page)\b", re.I)),
    ("positional figure", re.compile(r"\b(?:figure|diagram|graph|chart|image|photograph|illustration|picture)\s+(?:above|below|opposite|overleaf)\b", re.I)),
    ("page deferral (see/on p.)", re.compile(r"\b(?:see|on|from|at)\s+(?:pp?\.\s*|pages?\s+)\d", re.I)),
    ("overleaf / opposite page", re.compile(r"\b(?:overleaf|opposite page|on the (?:previous|next|facing) page)\b", re.I)),
    ("as shown in fig/table", re.compile(r"\bas\s+(?:shown|illustrated|depicted|seen)\s+in\s+(?:the\s+)?(?:fig|figure|table|diagram|graph|image|chart|box)\b", re.I)),
    ("this/previous chapter/section", re.compile(r"\b(?:see\s+(?:the\s+)?|in\s+this\s+|in\s+the\s+(?:previous|next|following|preceding)\s+)(?:chapter|section)s?\b", re.I)),
]


def source_ref_hits(body: str) -> list[tuple[str, str]]:
    """Dangling references to source artifacts (Table 1, see chapter, p. 42, the diagram above…) in a
    node's PROSE — excluding the # References/# Citations list, where "pp. 100-120" is a legit citation.
    A self-contained node embeds the content instead. Edit these rules for your domain if needed."""
    m = re.search(r"^#\s*(?:References|Citations)\b", body, re.M | re.I)
    prose = body[:m.start()] if m else body
    return [(label, " ".join(mm.group(0).split())) for label, rx in SOURCE_REF_RULES for mm in rx.finditer(prose)]


def write_index(nodes: dict) -> None:
    order = ["concepts", "entities", "references", "systems", "playbooks"]
    lines = ["# OKF Bundle Index", "",
             "Read this first, then open only the files relevant to your task.", ""]
    for folder in order:
        members = [n for n in nodes.values() if n["folder"] == folder]
        if not members:
            continue
        lines.append(f"# {folder}")
        for n in sorted(members, key=lambda x: x["title"].lower()):
            desc = n["description"] or "(no description)"
            lines.append(f"* [{n['title']}]({n['path']}) - {desc}")
        lines.append("")
    (BUNDLE / "index.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"index.md written ({sum(1 for _ in nodes)} nodes)")

    for folder in order:
        d = BUNDLE / folder
        members = [n for n in nodes.values() if n["folder"] == folder]
        if not d.is_dir() or not members:
            continue
        sub = [f"# {folder} index", ""]
        for n in sorted(members, key=lambda x: x["title"].lower()):
            sub.append(f"* [{n['title']}]({n['path']}) - {n['description']}")
        (d / "index.md").write_text("\n".join(sub) + "\n", encoding="utf-8")
        print(f"{folder}/index.md written ({len(members)} nodes)")


def lint(nodes: dict) -> int:
    problems = 0
    valid = set(nodes)
    for n in nodes.values():
        fm = n["fm"]
        missing = [k for k in ("type", "title", "description", "tags", "timestamp") if k not in fm]
        if missing:
            print(f"MISSING FIELDS {n['path']}: {missing}")
            problems += 1
        if "provenance" not in fm:
            print(f"MISSING PROVENANCE {n['path']}")
            problems += 1
        for target in n["links"]:
            if target not in valid and not (BUNDLE / target.lstrip("/")).exists():
                print(f"ORPHAN LINK {n['path']} -> {target}")
                problems += 1
        if n["type"] == "concept" and len(n["body"]) < THIN_CONCEPT_CHARS:
            print(f"THIN CONCEPT {n['path']} ({len(n['body'])} chars)")
            problems += 1
        refs = source_ref_hits(n["body"])
        if refs:
            print(f"DANGLING SOURCE REF {n['path']}: " + "; ".join(f'"{t}"' for _, t in refs[:2]))
            problems += 1
    linked_to = {t for n in nodes.values() for t in n["links"]}
    for path, n in nodes.items():
        if not n["links"] and path not in linked_to:
            print(f"ISLAND NODE (no in/out links) {path}")
            problems += 1
    print(f"lint: {problems} problem(s) across {len(nodes)} nodes")
    return problems


def graph(nodes: dict) -> None:
    idx = {p: i for i, p in enumerate(nodes)}
    gnodes = [{"id": i, "label": n["title"], "path": p,
               "type": n["type"], "color": TYPE_COLORS.get(n["type"], "#999"),
               "desc": n["description"]}
              for p, (i, n) in ((p, (idx[p], nodes[p])) for p in nodes)]
    edges = []
    for p, n in nodes.items():
        for t in n["links"]:
            if t in idx:
                edges.append({"s": idx[p], "t": idx[t]})
    data = json.dumps({"nodes": gnodes, "edges": edges})
    html = HTML_TEMPLATE.replace("__DATA__", data)
    (BUNDLE / "okf-graph.html").write_text(html, encoding="utf-8")
    print(f"okf-graph.html written ({len(gnodes)} nodes, {len(edges)} edges)")


HTML_TEMPLATE = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>OKF graph</title>
<style>
 body{margin:0;background:#101318;color:#dde3ee;font:13px system-ui,sans-serif;overflow:hidden}
 #info{position:fixed;top:10px;left:10px;background:#1a1f29cc;padding:10px 14px;border-radius:8px;max-width:340px}
 #info h1{font-size:15px;margin:0 0 4px}
 #legend span{display:inline-block;margin-right:10px}
 #legend i{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:4px}
 #tip{position:fixed;display:none;background:#222a38;padding:8px 10px;border-radius:6px;max-width:300px;pointer-events:none;border:1px solid #3a4356}
 canvas{display:block}
</style></head><body>
<div id="info"><h1>OKF graph</h1>
<div id="stats"></div><div id="legend"></div>
<div style="opacity:.7;margin-top:4px">drag to pan · wheel to zoom · hover a node</div></div>
<div id="tip"></div><canvas id="c"></canvas>
<script>
const DATA=__DATA__;
const cv=document.getElementById('c'),cx=cv.getContext('2d');
let W,H;function rs(){W=cv.width=innerWidth;H=cv.height=innerHeight}rs();addEventListener('resize',rs);
const N=DATA.nodes,E=DATA.edges;
document.getElementById('stats').textContent=N.length+' nodes · '+E.length+' links';
const types=[...new Set(N.map(n=>n.type))];
document.getElementById('legend').innerHTML=types.map(t=>{const c=N.find(n=>n.type===t).color;return '<span><i style="background:'+c+'"></i>'+t+'</span>'}).join('');
N.forEach((n,i)=>{const a=i/N.length*Math.PI*2,r=Math.min(W,H)*.35;n.x=W/2+Math.cos(a)*r*(0.4+Math.random()*.6);n.y=H/2+Math.sin(a)*r*(0.4+Math.random()*.6);n.vx=0;n.vy=0;
n.deg=0});
E.forEach(e=>{N[e.s].deg++;N[e.t].deg++});
const adj=E.map(e=>[e.s,e.t]);
let tx=0,ty=0,scale=1,drag=null,hover=null;
function step(){
 for(let i=0;i<N.length;i++){const a=N[i];
  for(let j=i+1;j<N.length;j++){const b=N[j];
   let dx=a.x-b.x,dy=a.y-b.y,d2=dx*dx+dy*dy+0.01;if(d2>90000)continue;
   const f=1200/d2;dx*=f;dy*=f;a.vx+=dx;a.vy+=dy;b.vx-=dx;b.vy-=dy}}
 adj.forEach(([s,t])=>{const a=N[s],b=N[t];let dx=b.x-a.x,dy=b.y-a.y;
  const d=Math.sqrt(dx*dx+dy*dy)+.01,f=(d-90)*.004;dx=dx/d*f*d;dy=dy/d*f*d;
  a.vx+=dx;a.vy+=dy;b.vx-=dx;b.vy-=dy});
 N.forEach(n=>{n.vx+=(W/2-n.x)*.0004;n.vy+=(H/2-n.y)*.0004;
  n.vx*=.85;n.vy*=.85;n.x+=n.vx;n.y+=n.vy});
}
function draw(){cx.setTransform(1,0,0,1,0,0);cx.clearRect(0,0,W,H);
 cx.setTransform(scale,0,0,scale,tx,ty);
 cx.strokeStyle='#2c3547';cx.lineWidth=1/scale;
 adj.forEach(([s,t])=>{cx.beginPath();cx.moveTo(N[s].x,N[s].y);cx.lineTo(N[t].x,N[t].y);cx.stroke()});
 N.forEach(n=>{const r=4+Math.sqrt(n.deg)*1.6;
  cx.beginPath();cx.arc(n.x,n.y,r,0,7);cx.fillStyle=n.color;cx.fill();
  if(n===hover){cx.strokeStyle='#fff';cx.lineWidth=2/scale;cx.stroke()}
  if(scale>0.9||n.deg>6){cx.fillStyle='#dde3ee';cx.font=(11/scale)+'px system-ui';
   cx.fillText(n.label.slice(0,34),n.x+r+3,n.y+3)}});
}
let frames=0;(function loop(){if(frames++<600)step();draw();requestAnimationFrame(loop)})();
cv.addEventListener('mousedown',e=>drag={x:e.clientX,y:e.clientY});
addEventListener('mouseup',()=>drag=null);
addEventListener('mousemove',e=>{
 if(drag){tx+=e.clientX-drag.x;ty+=e.clientY-drag.y;drag={x:e.clientX,y:e.clientY};return}
 const mx=(e.clientX-tx)/scale,my=(e.clientY-ty)/scale;
 hover=null;for(const n of N){const dx=n.x-mx,dy=n.y-my;if(dx*dx+dy*dy<120){hover=n;break}}
 const tip=document.getElementById('tip');
 if(hover){tip.style.display='block';tip.style.left=(e.clientX+14)+'px';tip.style.top=(e.clientY+14)+'px';
  tip.innerHTML='<b>'+hover.label+'</b><br><span style="opacity:.7">'+hover.path+'</span><br>'+hover.desc}
 else tip.style.display='none'});
cv.addEventListener('wheel',e=>{e.preventDefault();const k=e.deltaY<0?1.12:0.89;
 tx=e.clientX-(e.clientX-tx)*k;ty=e.clientY-(e.clientY-ty)*k;scale*=k},{passive:false});
</script></body></html>
"""


def main() -> None:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    nodes = load_nodes()
    if cmd in ("index", "all"):
        write_index(nodes)
    if cmd in ("graph", "all"):
        graph(nodes)
    if cmd in ("lint", "all"):
        lint(nodes)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
