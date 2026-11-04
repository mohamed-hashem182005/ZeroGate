"""Small SVG authoring kit for the ZeroGate dossier.

Geometry follows the diagram-design rules: 4px structural grid, opaque masks
behind every label, orthogonal rounded elbows for architecture/sequence flows,
and markers declared once per figure.
"""

from __future__ import annotations

import html
import math
from dataclasses import dataclass, field
from typing import Iterable, Sequence

from theme import (
    ACCENT,
    ACCENT_TINT,
    INK,
    INK_STRONG,
    LINK,
    MONO,
    MUTED,
    PAPER,
    PAPER2,
    RULE,
    RULE_SOLID,
    SANS,
    SERIF,
    SOFT,
    WHITE,
)


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def fmt(n: float) -> str:
    """Compact SVG number."""
    if abs(n - round(n)) < 0.01:
        return str(int(round(n)))
    return f"{n:.2f}".rstrip("0").rstrip(".")


def text_width(text: str, size: float, mono: bool = False, weight: int = 400) -> float:
    """Calibrated width budget: 0.62em mono, 0.60em sans (0.63 for 600)."""
    per = 0.62 if mono else (0.63 if weight >= 600 else 0.60)
    return len(text) * size * per


def text(
    x: float,
    y: float,
    value: str,
    size: float = 12,
    fill: str = INK,
    family: str = SANS,
    weight: int | None = None,
    anchor: str = "start",
    letter_spacing: float | None = None,
    opacity: float | None = None,
    extra: str = "",
) -> str:
    parts = [
        f'x="{fmt(x)}"',
        f'y="{fmt(y)}"',
        f'font-size="{fmt(size)}"',
        f'fill="{fill}"',
        f'font-family="{family}"',
        f'text-anchor="{anchor}"',
    ]
    if weight:
        parts.append(f'font-weight="{weight}"')
    if letter_spacing:
        parts.append(f'letter-spacing="{letter_spacing}"')
    if opacity is not None:
        parts.append(f'opacity="{opacity}"')
    if extra:
        parts.append(extra)
    return f"<text {' '.join(parts)}>{esc(value)}</text>"


def rect(
    x: float,
    y: float,
    w: float,
    h: float,
    fill: str = "none",
    stroke: str = "none",
    sw: float = 1,
    rx: float = 0,
    dash: str | None = None,
    opacity: float | None = None,
    extra: str = "",
) -> str:
    parts = [
        f'x="{fmt(x)}"',
        f'y="{fmt(y)}"',
        f'width="{fmt(w)}"',
        f'height="{fmt(h)}"',
        f'fill="{fill}"',
        f'stroke="{stroke}"',
        f'stroke-width="{fmt(sw)}"',
        f'rx="{fmt(rx)}"',
    ]
    if dash:
        parts.append(f'stroke-dasharray="{dash}"')
    if opacity is not None:
        parts.append(f'opacity="{opacity}"')
    if extra:
        parts.append(extra)
    return f"<rect {' '.join(parts)}/>"


def line(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    stroke: str = MUTED,
    sw: float = 1.2,
    dash: str | None = None,
    marker_end: str | None = None,
    marker_start: str | None = None,
    opacity: float | None = None,
) -> str:
    parts = [
        f'x1="{fmt(x1)}"',
        f'y1="{fmt(y1)}"',
        f'x2="{fmt(x2)}"',
        f'y2="{fmt(y2)}"',
        f'stroke="{stroke}"',
        f'stroke-width="{fmt(sw)}"',
    ]
    if dash:
        parts.append(f'stroke-dasharray="{dash}"')
    if marker_end:
        parts.append(f'marker-end="url(#{marker_end})"')
    if marker_start:
        parts.append(f'marker-start="url(#{marker_start})"')
    if opacity is not None:
        parts.append(f'opacity="{opacity}"')
    return f"<line {' '.join(parts)}/>"


def orth(points: Sequence[tuple[float, float]], r: float = 8) -> str:
    """Rounded orthogonal path from a point list."""
    pts = [(float(x), float(y)) for x, y in points]
    if len(pts) < 2:
        return ""
    d = [f"M {fmt(pts[0][0])},{fmt(pts[0][1])}"]
    for i in range(1, len(pts) - 1):
        prev, cur, nxt = pts[i - 1], pts[i], pts[i + 1]
        v1 = (cur[0] - prev[0], cur[1] - prev[1])
        v2 = (nxt[0] - cur[0], nxt[1] - cur[1])
        l1 = math.hypot(*v1)
        l2 = math.hypot(*v2)
        if l1 < 0.01 or l2 < 0.01:
            d.append(f"L {fmt(cur[0])},{fmt(cur[1])}")
            continue
        rr = min(r, l1 / 2, l2 / 2, 12)
        before = (cur[0] - v1[0] / l1 * rr, cur[1] - v1[1] / l1 * rr)
        after = (cur[0] + v2[0] / l2 * rr, cur[1] + v2[1] / l2 * rr)
        d.append(f"L {fmt(before[0])},{fmt(before[1])}")
        d.append(
            f"Q {fmt(cur[0])},{fmt(cur[1])} {fmt(after[0])},{fmt(after[1])}"
        )
    d.append(f"L {fmt(pts[-1][0])},{fmt(pts[-1][1])}")
    return " ".join(d)


def path(
    d: str,
    stroke: str = MUTED,
    sw: float = 1.2,
    fill: str = "none",
    dash: str | None = None,
    marker_end: str | None = None,
    marker_start: str | None = None,
    opacity: float | None = None,
) -> str:
    parts = [
        f'd="{d}"',
        f'fill="{fill}"',
        f'stroke="{stroke}"',
        f'stroke-width="{fmt(sw)}"',
    ]
    if dash:
        parts.append(f'stroke-dasharray="{dash}"')
    if marker_end:
        parts.append(f'marker-end="url(#{marker_end})"')
    if marker_start:
        parts.append(f'marker-start="url(#{marker_start})"')
    if opacity is not None:
        parts.append(f'opacity="{opacity}"')
    return f"<path {' '.join(parts)}/>"


def arrow(
    points: Sequence[tuple[float, float]],
    color: str = MUTED,
    marker: str = "arrow",
    dash: str | None = None,
    sw: float = 1.2,
    r: float = 8,
    marker_start: str | None = None,
) -> str:
    return path(orth(points, r=r), stroke=color, sw=sw, dash=dash,
                marker_end=marker, marker_start=marker_start)


def label_mask(
    cx: float,
    cy: float,
    value: str,
    size: float = 8,
    color: str = SOFT,
    mono: bool = True,
    padding: float = 12,
    mask: str = PAPER,
    anchor: str = "middle",
) -> str:
    """Free-standing label with an opaque mask, centered at cx/cy baseline."""
    w = text_width(value, size, mono) + padding
    h = 12
    x = cx - w / 2 if anchor == "middle" else cx - 4
    y = cy - 10
    return (
        rect(x, y, w, h, fill=mask, rx=2)
        + text(cx, cy, value, size=size, fill=color, family=MONO if mono else SANS,
               anchor=anchor, letter_spacing=0.06)
    )


def hlabel(
    cx: float,
    arrow_y: float,
    value: str,
    color: str = SOFT,
    size: float = 8,
    mask: str = PAPER,
) -> str:
    """Label above a horizontal connector, 8px clear of the stroke."""
    w = text_width(value, size, True) + 12
    return (
        rect(cx - w / 2, arrow_y - 20, w, 12, fill=mask, rx=2)
        + text(cx, arrow_y - 11, value, size=size, fill=color, family=MONO,
               anchor="middle", letter_spacing=0.06)
    )


def vlabel(
    arrow_x: float,
    cy: float,
    value: str,
    color: str = SOFT,
    size: float = 8,
    mask: str = PAPER,
) -> str:
    """Label right of a vertical connector, 8px clear of the stroke."""
    w = text_width(value, size, True) + 12
    return (
        rect(arrow_x + 8, cy - 6, w, 12, fill=mask, rx=2)
        + text(arrow_x + 14, cy + 3, value, size=size, fill=color, family=MONO,
               letter_spacing=0.06)
    )


def zone(x: float, y: float, w: float, h: float, label: str) -> str:
    return (
        rect(x, y, w, h, fill="rgba(31,42,48,0.018)",
             stroke="rgba(31,42,48,0.10)", sw=0.8, rx=8)
        + rect(x + 10, y + 2, text_width(label, 7, True) + 14, 12, fill=PAPER, rx=2)
        + text(x + 17, y + 11, label, size=7, fill=SOFT, family=MONO,
               letter_spacing=0.14)
    )


NODE_TREATMENTS = {
    "focal": (ACCENT_TINT, ACCENT, ACCENT),
    "backend": (WHITE, INK, INK),
    "store": ("rgba(31,42,48,0.05)", MUTED, MUTED),
    "external": ("rgba(31,42,48,0.03)", "rgba(31,42,48,0.30)", MUTED),
    "input": ("rgba(82,100,108,0.10)", SOFT, MUTED),
    "optional": ("rgba(31,42,48,0.02)", "rgba(31,42,48,0.20)", MUTED),
    "security": ("rgba(181,68,39,0.05)", "rgba(181,68,39,0.50)", ACCENT),
}


def node(
    x: float,
    y: float,
    w: float,
    h: float,
    name: str,
    sublabel: str = "",
    tag: str = "",
    kind: str = "backend",
    focal: bool = False,
    dash: str | None = None,
    name_size: float = 12,
) -> str:
    fill, stroke, tag_color = NODE_TREATMENTS[kind]
    if focal:
        fill, stroke, tag_color = NODE_TREATMENTS["focal"]
    out = [rect(x, y, w, h, fill=PAPER, rx=6)]
    out.append(rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.1 if focal else 1,
                    rx=6, dash=dash))
    if tag:
        tw = max(24, text_width(tag, 7, True) + 10)
        out.append(rect(x + 8, y + 7, tw, 12, fill="none",
                        stroke=stroke if focal else "rgba(31,42,48,0.30)",
                        sw=0.8, rx=2))
        out.append(text(x + 8 + tw / 2, y + 16, tag, size=7, fill=tag_color,
                        family=MONO, anchor="middle", letter_spacing=0.08))
    cx = x + w / 2
    if sublabel:
        out.append(text(cx, y + h / 2 + 3, name, size=name_size, fill=INK,
                        family=SANS, weight=600, anchor="middle"))
        out.append(text(cx, y + h / 2 + 20, sublabel, size=9, fill=MUTED,
                        family=MONO, anchor="middle"))
    else:
        out.append(text(cx, y + h / 2 + 4, name, size=name_size, fill=INK,
                        family=SANS, weight=600, anchor="middle"))
    return "".join(out)


def legend(items: Sequence[dict], y: float, width: float = 960,
           start_x: float = 40, gap: float = 28) -> str:
    """Bottom legend strip. Item kinds: box, line, text."""
    out = [line(start_x, y - 10, width - start_x, y - 10,
                stroke="rgba(31,42,48,0.10)", sw=0.8)]
    out.append(text(start_x, y + 8, "LEGEND · KEY", size=8, fill=SOFT,
                    family=MONO, letter_spacing=0.16))
    cx = start_x + 112
    for item in items:
        kind = item.get("kind", "text")
        label = item["label"]
        if kind == "box":
            out.append(rect(cx, y - 5, 14, 11, rx=2,
                            fill=item.get("fill", WHITE),
                            stroke=item.get("stroke", INK),
                            dash=item.get("dash")))
            text_x = cx + 20
        elif kind == "line":
            marker = item.get("marker")
            out.append(line(cx, y + 1, cx + 24, y + 1,
                            stroke=item.get("stroke", MUTED),
                            sw=item.get("sw", 1.2),
                            dash=item.get("dash"),
                            marker_end=marker))
            # UML diamonds and triangles draw forward of the line end.
            marker_clearance = 0
            if marker in ("uml-diamond-filled", "uml-diamond-hollow",
                          "uml-diamond-hollow-end"):
                marker_clearance = 20
            elif marker == "uml-triangle":
                marker_clearance = 10
            elif marker:
                marker_clearance = 6
            text_x = cx + 31 + marker_clearance
        else:
            text_x = cx
        out.append(text(text_x, y + 4, label, size=8.5, fill=MUTED, family=SANS))
        cx = text_x + text_width(label, 8.5, False) + gap
    return "".join(out)


def defs(extra: str = "") -> str:
    return f"""<defs>
<marker id="arrow" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{MUTED}"/></marker>
<marker id="arrow-accent" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{ACCENT}"/></marker>
<marker id="arrow-link" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{LINK}"/></marker>
<marker id="arrow-open" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polyline points="0 0, 8 3, 0 6" fill="none" stroke="{MUTED}" stroke-width="1.2"/></marker>
<marker id="arrow-open-link" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polyline points="0 0, 8 3, 0 6" fill="none" stroke="{LINK}" stroke-width="1.2"/></marker>
<marker id="uml-open" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto" markerUnits="userSpaceOnUse"><path d="M0,0 L9,4 L0,8" fill="none" stroke="{MUTED}" stroke-width="1"/></marker>
<marker id="uml-triangle" markerWidth="16" markerHeight="12" refX="15" refY="6" orient="auto" markerUnits="userSpaceOnUse"><polygon points="0 0, 16 6, 0 12" fill="{PAPER}" stroke="{INK}" stroke-width="1"/></marker>
<marker id="uml-diamond-filled" markerWidth="18" markerHeight="10" refX="0" refY="5" orient="auto" markerUnits="userSpaceOnUse"><polygon points="0 5, 9 0, 18 5, 9 10" fill="{INK}"/></marker>
<marker id="uml-diamond-hollow" markerWidth="18" markerHeight="10" refX="0" refY="5" orient="auto" markerUnits="userSpaceOnUse"><polygon points="0 5, 9 0, 18 5, 9 10" fill="{PAPER}" stroke="{INK}" stroke-width="1"/></marker>
<marker id="uml-diamond-hollow-end" markerWidth="18" markerHeight="10" refX="18" refY="5" orient="auto" markerUnits="userSpaceOnUse"><polygon points="0 5, 9 0, 18 5, 9 10" fill="{PAPER}" stroke="{INK}" stroke-width="1"/></marker>
{extra}
</defs>"""


def svg_open(slug: str, title: str, desc: str, w: int, h: int) -> str:
    return (
        f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" '
        f'role="img" aria-labelledby="{slug}-title {slug}-desc" '
        f'style="min-width:{w}px">'
        f'<title id="{slug}-title">{esc(title)}</title>'
        f'<desc id="{slug}-desc">{esc(desc)}</desc>'
        f"{defs()}"
        f'<rect width="100%" height="100%" fill="{PAPER}"/>'
    )


def svg_close() -> str:
    return "</svg>"


# ---------------------------------------------------------------------------
# UML class / ER / database primitives
# ---------------------------------------------------------------------------

def class_box(
    x: float,
    y: float,
    w: float,
    name: str,
    attrs: Sequence[str] = (),
    ops: Sequence[str] = (),
    stereo: str = "",
    focal: bool = False,
    abstract: bool = False,
) -> tuple[str, float]:
    header_h = 52 if stereo else 40
    attr_h = (len(attrs) * 18 + 10) if attrs else 0
    op_h = (len(ops) * 18 + 10) if ops else 0
    h = header_h + attr_h + op_h
    stroke = ACCENT if focal else INK
    base_fill = "rgba(181,68,39,0.04)" if focal else WHITE
    out = [rect(x, y, w, h, fill=base_fill, stroke=stroke, sw=1, rx=6)]
    if focal:
        out.append(rect(x, y, w, header_h, fill=ACCENT_TINT, rx=6))
        out.append(rect(x, y + header_h - 8, w, 8, fill=ACCENT_TINT))
    if stereo:
        out.append(text(x + w / 2, y + 15, stereo, size=8, fill=ACCENT if focal else MUTED,
                        family=MONO, anchor="middle", letter_spacing=0.08))
        out.append(text(x + w / 2, y + 38, name, size=12, fill=INK, family=SANS,
                        weight=600, anchor="middle",
                        extra='font-style="italic"' if abstract else ""))
    else:
        out.append(text(x + w / 2, y + 26, name, size=12, fill=INK, family=SANS,
                        weight=600, anchor="middle",
                        extra='font-style="italic"' if abstract else ""))
    cursor = y + header_h
    if attrs:
        out.append(line(x, cursor, x + w, cursor, stroke="rgba(31,42,48,0.22)", sw=1))
        ty = cursor + 16
        for a in attrs:
            out.append(text(x + 12, ty, a, size=9, fill=INK, family=MONO))
            ty += 18
        cursor += attr_h
    if ops:
        out.append(line(x, cursor, x + w, cursor, stroke="rgba(31,42,48,0.22)", sw=1))
        ty = cursor + 16
        for o in ops:
            out.append(text(x + 12, ty, o, size=9, fill=INK, family=MONO))
            ty += 18
    return "".join(out), h


def entity_box(
    x: float,
    y: float,
    w: float,
    name: str,
    fields: Sequence[str],
    focal: bool = False,
) -> tuple[str, float]:
    header_h = 36
    h = header_h + len(fields) * 18 + 10
    stroke = ACCENT if focal else INK
    out = [rect(x, y, w, h, fill="rgba(181,68,39,0.04)" if focal else WHITE,
                stroke=stroke, sw=1, rx=6)]
    if focal:
        out.append(rect(x, y, w, header_h, fill=ACCENT_TINT, rx=6))
        out.append(rect(x, y + header_h - 8, w, 8, fill=ACCENT_TINT))
    out.append(rect(x + 8, y + 7, 38, 12, fill="none",
                    stroke="rgba(181,68,39,0.45)" if focal else "rgba(31,42,48,0.30)",
                    sw=0.8, rx=2))
    out.append(text(x + 27, y + 16, "ENTITY", size=6.5,
                    fill=ACCENT if focal else MUTED, family=MONO,
                    anchor="middle", letter_spacing=0.07))
    out.append(text(x + w / 2, y + 25, name, size=12, fill=INK, family=SANS,
                    weight=600, anchor="middle"))
    out.append(line(x, y + header_h, x + w, y + header_h,
                    stroke="rgba(31,42,48,0.22)", sw=1))
    ty = y + header_h + 16
    for f in fields:
        out.append(text(x + 12, ty, f, size=9, fill=INK, family=MONO))
        ty += 18
    return "".join(out), h


def db_table(
    x: float,
    y: float,
    w: float,
    title: str,
    rows: Sequence[dict],
    indexes: Sequence[str] = (),
    accent_header: bool = False,
    tag: str = "TABLE",
) -> tuple[str, float, list[float]]:
    header_h = 36
    row_h = 24
    idx_h = (len(indexes) * 16 + 26) if indexes else 0
    h = header_h + len(rows) * row_h + idx_h
    out = [rect(x, y, w, h, fill=WHITE, stroke=INK, sw=1, rx=6)]
    if accent_header:
        out.append(rect(x, y, w, header_h, fill=ACCENT_TINT, rx=6))
        out.append(rect(x, y + header_h - 8, w, 8, fill=ACCENT_TINT))
    out.append(rect(x + 8, y + 7, max(38, text_width(tag, 6.5, True) + 12), 12,
                    fill="none", stroke="rgba(31,42,48,0.30)", sw=0.8, rx=2))
    out.append(text(x + 8 + max(38, text_width(tag, 6.5, True) + 12) / 2,
                    y + 16, tag, size=6.5, fill=MUTED, family=MONO,
                    anchor="middle", letter_spacing=0.07))
    out.append(text(x + 12, y + 25, title, size=12, fill=INK, family=SANS, weight=600))
    out.append(line(x, y + header_h, x + w, y + header_h,
                    stroke="rgba(31,42,48,0.22)", sw=1))
    centers: list[float] = []
    for i, row in enumerate(rows):
        ry = y + header_h + i * row_h
        if i % 2 == 1:
            out.append(rect(x + 1, ry, w - 2, row_h, fill="rgba(31,42,48,0.02)"))
        centers.append(ry + row_h / 2)
        name = row["name"]
        typ = row.get("type", "")
        chips = row.get("chips", [])
        out.append(text(x + 12, ry + 16, name, size=12, fill=INK, family=SANS))
        type_w = text_width(typ, 9, True)
        out.append(text(x + w - 12, ry + 16, typ, size=9, fill=MUTED,
                        family=MONO, anchor="end"))
        chip_x = x + w - 12 - type_w - 8
        for chip in reversed(chips):
            cw = max(20, text_width(chip, 7, True) + 8)
            chip_x -= cw
            out.append(rect(chip_x, ry + 6, cw, 12, fill="none",
                            stroke="rgba(31,42,48,0.24)", sw=0.8, rx=2))
            out.append(text(chip_x + cw / 2, ry + 15, chip, size=7,
                            fill=MUTED, family=MONO, anchor="middle",
                            letter_spacing=0.04))
            chip_x -= 4
        out.append(line(x, ry + row_h, x + w, ry + row_h,
                        stroke="rgba(31,42,48,0.08)", sw=0.8))
    if indexes:
        iy = y + header_h + len(rows) * row_h
        out.append(line(x, iy, x + w, iy, stroke="rgba(31,42,48,0.22)", sw=1))
        out.append(text(x + 12, iy + 15, "INDEXES", size=7, fill=SOFT,
                        family=MONO, letter_spacing=0.12))
        ty = iy + 30
        for idx in indexes:
            out.append(text(x + 12, ty, idx, size=8.5, fill=MUTED, family=MONO))
            ty += 16
    return "".join(out), h, centers


# ---------------------------------------------------------------------------
# Sequence primitives
# ---------------------------------------------------------------------------

def actor_box(
    x: float,
    y: float,
    w: float,
    name: str,
    sublabel: str,
    tag: str,
    focal: bool = False,
    kind: str = "backend",
) -> str:
    fill, stroke, tag_color = NODE_TREATMENTS[kind]
    if focal:
        fill, stroke, tag_color = NODE_TREATMENTS["focal"]
    out = [rect(x, y, w, 64, fill=PAPER, rx=6)]
    out.append(rect(x, y, w, 64, fill=fill, stroke=stroke, sw=1.1 if focal else 1, rx=6))
    tw = max(28, text_width(tag, 6.5, True) + 10)
    out.append(rect(x + 8, y + 8, tw, 12, fill="none",
                    stroke=stroke if focal else "rgba(31,42,48,0.30)", sw=0.8, rx=2))
    out.append(text(x + 8 + tw / 2, y + 17, tag, size=6.5, fill=tag_color,
                    family=MONO, anchor="middle", letter_spacing=0.07))
    out.append(text(x + w / 2, y + 40, name, size=12, fill=INK, family=SANS,
                    weight=600, anchor="middle"))
    out.append(text(x + w / 2, y + 55, sublabel, size=8.5, fill=MUTED,
                    family=MONO, anchor="middle"))
    return "".join(out)


def lifeline(cx: float, top: float, bottom: float) -> str:
    return line(cx, top, cx, bottom, stroke="rgba(31,42,48,0.22)", sw=1,
                dash="3,3")


def activation(cx: float, top: float, bottom: float) -> str:
    return rect(cx - 4, top, 8, bottom - top, fill="rgba(31,42,48,0.06)",
                stroke=MUTED, sw=0.8)


def message(
    x1: float,
    x2: float,
    y: float,
    value: str,
    color: str = LINK,
    marker: str = "arrow-link",
    dash: str | None = None,
    sw: float = 1.2,
    label_color: str | None = None,
    label_dy: float = 0,
) -> str:
    out = [line(x1, y, x2, y, stroke=color, sw=sw, dash=dash, marker_end=marker)]
    if value:
        cx = (x1 + x2) / 2
        out.append(hlabel(cx, y + label_dy, value, color=label_color or color))
    return "".join(out)


def self_message(
    cx: float,
    y: float,
    value: str,
    color: str = MUTED,
    marker: str = "arrow",
    dash: str | None = None,
    loop: float = 44,
) -> str:
    d = orth([(cx + 4, y), (cx + loop, y), (cx + loop, y + 26), (cx + 4, y + 26)],
             r=8)
    out = [path(d, stroke=color, sw=1.2, dash=dash, marker_end=marker)]
    out.append(label_mask(cx + loop + 10, y + 16, value, size=8, color=SOFT,
                          anchor="start"))
    return "".join(out)


def fragment(
    x: float,
    y: float,
    w: float,
    h: float,
    op: str,
    guard: str,
    guard_y: float | None = None,
    divider_y: float | None = None,
    second_guard: str | None = None,
) -> str:
    out = [rect(x, y, w, h, rx=4, fill="rgba(31,42,48,0.02)",
                stroke="rgba(31,42,48,0.22)", sw=1)]
    out.append(rect(x, y, 42, 16, rx=2, fill=PAPER,
                    stroke="rgba(31,42,48,0.22)", sw=1))
    out.append(text(x + 21, y + 12, op, size=8, fill=MUTED, family=MONO,
                    anchor="middle", letter_spacing=0.12))
    gy = guard_y if guard_y is not None else y + 36
    out.append(text(x + 12, gy, guard, size=8, fill=MUTED, family=MONO,
                    letter_spacing=0.04))
    if divider_y is not None:
        out.append(line(x + 8, divider_y, x + w - 8, divider_y,
                        stroke="rgba(31,42,48,0.20)", sw=1, dash="4,3"))
        if second_guard:
            out.append(text(x + 12, divider_y + 24, second_guard, size=8,
                            fill=MUTED, family=MONO, letter_spacing=0.04))
    return "".join(out)


def state_box(
    x: float,
    y: float,
    w: float,
    h: float,
    name: str,
    sublabel: str = "",
    focal: bool = False,
    kind: str = "backend",
) -> str:
    fill, stroke, tag_color = NODE_TREATMENTS[kind]
    if focal:
        fill, stroke, tag_color = NODE_TREATMENTS["focal"]
    out = [rect(x, y, w, h, fill=PAPER, rx=8)]
    out.append(rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.1 if focal else 1, rx=8))
    out.append(rect(x + 8, y + 8, 40, 12, fill="none",
                    stroke=stroke if focal else "rgba(31,42,48,0.30)", sw=0.8, rx=2))
    out.append(text(x + 28, y + 17, "STATE", size=6.5, fill=tag_color,
                    family=MONO, anchor="middle", letter_spacing=0.07))
    out.append(text(x + w / 2, y + h / 2 + 2, name, size=14, fill=INK,
                    family=SANS, weight=600, anchor="middle"))
    if sublabel:
        out.append(text(x + w / 2, y + h / 2 + 20, sublabel, size=9, fill=MUTED,
                        family=MONO, anchor="middle"))
    return "".join(out)


def start_dot(cx: float, cy: float) -> str:
    return f'<circle cx="{fmt(cx)}" cy="{fmt(cy)}" r="6" fill="{INK}"/>'


def end_dot(cx: float, cy: float) -> str:
    return (
        f'<circle cx="{fmt(cx)}" cy="{fmt(cy)}" r="8" fill="none" stroke="{INK}" stroke-width="1"/>'
        f'<circle cx="{fmt(cx)}" cy="{fmt(cy)}" r="5" fill="{INK}"/>'
    )
