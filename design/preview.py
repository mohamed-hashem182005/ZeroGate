"""Render every figure to a standalone PNG-friendly HTML page."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from theme import CSS
import diagrams
import diagrams_flows


FIGURES = {
    "components": diagrams.component_diagram,
    "domain": diagrams.class_diagram,
    "er": diagrams.er_diagram,
    "identity": diagrams.db_identity,
    "access": diagrams.db_access,
    "seq-passkey": diagrams_flows.sequence_passkey,
    "seq-ssh": diagrams_flows.sequence_ssh,
    "seq-jit": diagrams_flows.sequence_jit,
    "seq-kill": diagrams_flows.sequence_kill,
    "policy": diagrams_flows.activity_policy,
    "state-session": diagrams_flows.state_session,
    "state-jit": diagrams_flows.state_jit,
    "state-device": diagrams_flows.state_device,
}


def page(svg: str, slug: str) -> str:
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{slug}</title>
<style>{CSS}
body {{ background: #d9d3c6; }}
.preview {{ padding: 20px; width: max-content; }}
.preview svg {{ display:block; }}
</style></head>
<body><div class="preview">{svg}</div></body></html>"""


def main() -> None:
    out_dir = Path(__file__).parent.parent / "preview" / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = []
    for slug, fn in FIGURES.items():
        svg = fn()
        (out_dir / f"{slug}.html").write_text(page(svg, slug), encoding="utf-8")
        # Pull the viewBox dimensions straight from the generated SVG.
        import re

        m = re.search(r'viewBox="0 0 (\d+) (\d+)"', svg)
        width, height = int(m.group(1)), int(m.group(2))
        manifest.append(f"{slug} {width + 40} {height + 40}")
    (out_dir / "manifest.txt").write_text("\n".join(manifest), encoding="utf-8")
    print("\n".join(manifest))


if __name__ == "__main__":
    main()
