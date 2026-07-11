"""check_source_refs.py — focused report of nodes that DEFER to a source artifact instead of standing alone.

A self-contained OKF node must EMBED the content (transcribe the table as markdown, describe what a
figure shows), never point at "Table 1", "Fig. 2", "see chapter 3", "on p. 42", "the diagram above" —
the reader doesn't have the textbook. This is the same check `okf_tools.py lint` runs (patterns live in
`okf_tools.SOURCE_REF_RULES`); this script just prints a focused, ranked report. Aim: 0.

Usage:
  python tools/check_source_refs.py            # report + top offenders
  python tools/check_source_refs.py --show 4   # more example matches per node
"""
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from okf_tools import load_nodes, source_ref_hits  # noqa: E402


def main() -> None:
    show = int(sys.argv[sys.argv.index("--show") + 1]) if "--show" in sys.argv else 2
    nodes = load_nodes()
    flagged, by_pattern = [], Counter()
    for p, n in nodes.items():
        hits = source_ref_hits(n["body"])
        if hits:
            flagged.append((p, hits))
            for label, _ in hits:
                by_pattern[label] += 1
    flagged.sort(key=lambda x: -len(x[1]))

    total = sum(len(h) for _, h in flagged)
    print(f"nodes with dangling source references: {len(flagged)} / {len(nodes)}  ({total} matches)")
    if by_pattern:
        print("by pattern: " + ", ".join(f"{lbl}={c}" for lbl, c in by_pattern.most_common()))
    print()
    for p, hits in flagged[:40]:
        ex = "  |  ".join(f'{lbl}: "{txt}"' for lbl, txt in hits[:show])
        print(f"  {len(hits):2d}  {p}")
        print(f"       {ex}")
    if len(flagged) > 40:
        print(f"  … and {len(flagged) - 40} more.")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
