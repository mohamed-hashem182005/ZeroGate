"""Export every ZeroGate diagram as a vector PDF, plus a combined A4 atlas.

Individual plates keep the diagram's native aspect ratio and page size, so they
can be dropped straight into a report. The atlas adds a cover, a figure number,
a title, and a one-line caption to each plate on A4 landscape.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from theme import FONT_LINK, MONO, PAPER, SANS, SERIF, INK, MUTED, SOFT, ACCENT
import diagrams
import diagrams_flows

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "diagrams"
TMP = ROOT / "preview" / "pdf"
CHROME = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")

FIGURES = [
    {
        "slug": "components",
        "kind": "Component view",
        "file": "01-component-architecture",
        "title": "Component architecture",
        "caption": "Five zones, two enforcement points, one policy decision. Requests enter through the Web Proxy or the SSH Certificate Authority and never reach a resource without a decision.",
        "fn": diagrams.component_diagram,
    },
    {
        "slug": "domain",
        "kind": "UML class diagram",
        "file": "02-domain-model",
        "title": "Domain model",
        "caption": "The seven domain objects and the invariants they protect: identity, device, credential, resource, policy, request, session, and the audit record that ties them together.",
        "fn": diagrams.class_diagram,
    },
    {
        "slug": "er",
        "kind": "Entity–relationship",
        "file": "03-logical-data-model",
        "title": "Logical data model",
        "caption": "Entities, keys, and cardinalities across identity, policy, and access. The two physical schemas that follow resolve this model into PostgreSQL tables.",
        "fn": diagrams.er_diagram,
    },
    {
        "slug": "identity",
        "kind": "Physical schema",
        "file": "04-identity-schema",
        "title": "Identity and device schema",
        "caption": "Users, devices, passkeys, and recovery shares. Every foreign key is explicit and every delete behaviour is stated on the edge.",
        "fn": diagrams.db_identity,
    },
    {
        "slug": "access",
        "kind": "Physical schema",
        "file": "05-access-schema",
        "title": "Access, policy and audit schema",
        "caption": "Policies, access requests, sessions, and the append-only audit chain. Five foreign keys carry the cascade, restrict, and set-null rules.",
        "fn": diagrams.db_access,
    },
    {
        "slug": "seq-passkey",
        "kind": "Sequence diagram",
        "file": "06-passkey-login",
        "title": "Passkey login sequence",
        "caption": "A WebAuthn ceremony, a risk decision, and a server-side session cookie. No password is transmitted and no biometric leaves the device.",
        "fn": diagrams_flows.sequence_passkey,
    },
    {
        "slug": "seq-ssh",
        "kind": "Sequence diagram",
        "file": "07-ssh-certificate-issuance",
        "title": "SSH certificate issuance",
        "caption": "The SSH helper proves possession, requests a thirty-minute certificate for one principal and one host, and opens the SPA port only long enough to connect.",
        "fn": diagrams_flows.sequence_ssh,
    },
    {
        "slug": "seq-jit",
        "kind": "Sequence diagram",
        "file": "08-jit-approval",
        "title": "Just-in-time approval",
        "caption": "A step-up score becomes a human decision. The approver records a reason; the grant is capped at thirty minutes and the queue waits fifteen before it expires.",
        "fn": diagrams_flows.sequence_jit,
    },
    {
        "slug": "seq-kill",
        "kind": "Sequence diagram",
        "file": "09-session-kill",
        "title": "Mid-session kill",
        "caption": "A posture change drops the score below forty. The Policy Administrator kills the session at both enforcement points and revokes the outstanding certificate.",
        "fn": diagrams_flows.sequence_kill,
    },
    {
        "slug": "policy",
        "kind": "Activity diagram",
        "file": "10-policy-engine",
        "title": "Policy Engine decision logic",
        "caption": "Hard gates first, then rules plus the ML adjustment. The score selects one of four bands; a failed hard gate overrides the score and fails closed.",
        "fn": diagrams_flows.activity_policy,
    },
    {
        "slug": "state-session",
        "kind": "State machine",
        "file": "11-session-state",
        "title": "Session lifecycle",
        "caption": "Active, step-up, suspended, killed, and expired. Suspended waits for approval, step-up requires re-authentication, and killed and expired are terminal.",
        "fn": diagrams_flows.state_session,
    },
    {
        "slug": "state-jit",
        "kind": "State machine",
        "file": "12-jit-request-state",
        "title": "JIT request lifecycle",
        "caption": "Requested, pending, approved, denied, expired, and consumed. An approval is single-use and expires after thirty minutes if it is never consumed.",
        "fn": diagrams_flows.state_jit,
    },
    {
        "slug": "state-device",
        "kind": "State machine",
        "file": "13-device-state",
        "title": "Device trust lifecycle",
        "caption": "Unknown, enrolled, compliant, non-compliant, quarantined, and revoked. A quarantined device re-enrolls only after the posture finding is remediated.",
        "fn": diagrams_flows.state_device,
    },
]


def viewbox(svg: str) -> tuple[int, int]:
    match = re.search(r'viewBox="0 0 (\d+) (\d+)"', svg)
    if not match:
        raise ValueError("SVG has no viewBox")
    return int(match.group(1)), int(match.group(2))


def svg_title(svg: str) -> str:
    match = re.search(r"<title[^>]*>(.*?)</title>", svg, flags=re.S)
    return re.sub(r"<[^>]+>", "", match.group(1)) if match else "ZeroGate diagram"


def print_pdf(html_path: Path, pdf_path: Path) -> None:
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    if pdf_path.exists():
        pdf_path.unlink()
    result = subprocess.run(
        [
            str(CHROME),
            "--headless=new",
            "--disable-gpu",
            "--no-pdf-header-footer",
            "--run-all-compositor-stages-before-draw",
            "--virtual-time-budget=8000",
            f"--print-to-pdf={pdf_path}",
            html_path.as_uri(),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 or not pdf_path.exists():
        raise RuntimeError(
            f"Chrome failed for {html_path.name}\n{result.stderr[-2000:]}"
        )
    size = pdf_path.stat().st_size
    print(f"  {pdf_path.relative_to(ROOT)}  ({size / 1024:.0f} KB)")


def individual_page(svg: str, w: int, h: int) -> str:
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>{svg_title(svg)}</title>
{FONT_LINK}
<style>
  @page {{ size: {w}px {h}px; margin: 0; }}
  html, body {{ margin: 0; padding: 0; background: {PAPER}; }}
  svg {{ display: block; width: {w}px; height: {h}px; min-width: 0 !important; }}
</style></head>
<body>{svg}</body></html>"""


def build_individual() -> None:
    print("Individual plates")
    TMP.mkdir(parents=True, exist_ok=True)
    for i, fig in enumerate(FIGURES, 1):
        svg = fig["fn"]()
        w, h = viewbox(svg)
        html = TMP / f"{fig['file']}.html"
        html.write_text(individual_page(svg, w, h), encoding="utf-8")
        print_pdf(html, OUT / f"{fig['file']}.pdf")


def atlas_page(svg: str, fig: dict, index: int, total: int, w: int, h: int) -> str:
    # Fit the plate to a 265 x 145 mm box; keep the native aspect ratio.
    max_w, max_h = 265.0, 145.0
    scale = min(max_w / w, max_h / h)
    dw, dh = w * scale, h * scale
    return f"""
<section class="page">
  <header class="plate-head">
    <span class="brand">ZeroGate &middot; Diagram atlas</span>
    <span class="folio">Fig. {index:02d} / {total:02d}</span>
  </header>
  <div class="plate-title">
    <h1>{fig["title"]}</h1>
    <span class="source">{fig["kind"]}</span>
  </div>
  <div class="plate-figure">
    <div class="svg-fit" style="width:{dw:.2f}mm;height:{dh:.2f}mm">{svg}</div>
  </div>
  <footer class="plate-foot">
    <p>{fig["caption"]}</p>
    <span class="nist">NIST SP 800&#8209;207 &middot; ZeroGate v0.9</span>
  </footer>
</section>"""


def cover_page(total: int) -> str:
    rows = "".join(
        f'<li><span class="n">{i:02d}</span><span class="t">{fig["title"]}</span>'
        f'<span class="p">{i}</span></li>'
        for i, fig in enumerate(FIGURES, 1)
    )
    return f"""
<section class="page cover">
  <header class="plate-head">
    <span class="brand">ZeroGate &middot; Design dossier</span>
    <span class="folio">October 2026</span>
  </header>
  <div class="cover-main">
    <div class="cover-kicker">Diagram atlas &middot; plates 01&ndash;{total:02d}</div>
    <h1>ZeroGate</h1>
    <p class="cover-sub">A zero-trust access broker for web applications and SSH servers.
    Thirteen diagrams covering the architecture, domain, schema, flows, decision logic,
    and state machines.</p>
    <div class="cover-rule"></div>
    <div class="cover-meta">
      <div><span class="k">Framework</span><span class="v">NIST SP 800&#8209;207</span></div>
      <div><span class="k">Scope</span><span class="v">Web apps &middot; SSH</span></div>
      <div><span class="k">Status</span><span class="v">Design baseline v0.9</span></div>
      <div><span class="k">Plates</span><span class="v">{total:02d} + cover</span></div>
    </div>
  </div>
  <div class="cover-contents">
    <div class="contents-head">Contents</div>
    <ol>{rows}</ol>
  </div>
  <footer class="plate-foot">
    <p>Vector plates. Every figure is also available as a separate PDF at its native page size.</p>
    <span class="nist">ZeroGate &middot; Diagram atlas</span>
  </footer>
</section>"""


def build_atlas() -> None:
    print("Combined atlas")
    figures = []
    for i, fig in enumerate(FIGURES, 1):
        svg = fig["fn"]()
        w, h = viewbox(svg)
        figures.append(atlas_page(svg, fig, i, len(FIGURES), w, h))

    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>ZeroGate diagram atlas</title>
{FONT_LINK}
<style>
  @page {{ size: A4 landscape; margin: 0; }}
  *, *::before, *::after {{ box-sizing: border-box; }}
  html, body {{ margin: 0; padding: 0; background: #ffffff; color: {INK};
    font-family: {SANS}; -webkit-font-smoothing: antialiased; }}
  .page {{
    width: 297mm; height: 210mm; padding: 11mm 16mm 9mm; overflow: hidden;
    background: {PAPER}; position: relative; break-after: page;
  }}
  .page:last-child {{ break-after: auto; }}
  .plate-head {{
    display: flex; justify-content: space-between; align-items: baseline;
    border-bottom: 0.35mm solid {INK}; padding-bottom: 2.2mm;
    font-family: {MONO}; font-size: 6.4pt; letter-spacing: 0.13em;
    text-transform: uppercase; color: {SOFT};
  }}
  .plate-title {{ display: flex; align-items: baseline; justify-content: space-between;
    gap: 8mm; margin-top: 3.6mm; }}
  h1 {{ font-family: {SERIF}; font-weight: 400; font-size: 20pt; line-height: 1.02;
    letter-spacing: -0.015em; margin: 0; }}
  .source {{ font-family: {MONO}; font-size: 6pt; letter-spacing: 0.08em;
    text-transform: uppercase; color: {SOFT}; text-align: right; }}
  .plate-figure {{ height: 149mm; display: flex; align-items: center;
    justify-content: center; padding: 2mm 0 1mm; }}
  .svg-fit svg {{ display: block; width: 100%; height: 100%; min-width: 0 !important; }}
  .plate-foot {{ display: flex; justify-content: space-between; align-items: flex-end;
    gap: 12mm; border-top: 0.2mm solid rgba(31,42,48,0.2); padding-top: 2.2mm; }}
  .plate-foot p {{ font-family: {SANS}; font-size: 7.6pt; line-height: 1.45;
    color: {MUTED}; max-width: 205mm; }}
  .nist {{ font-family: {MONO}; font-size: 5.8pt; letter-spacing: 0.1em;
    text-transform: uppercase; color: {SOFT}; white-space: nowrap; }}
  /* cover */
  .cover {{ padding: 14mm 18mm 10mm; }}
  .cover-main {{ margin-top: 10mm; max-width: 220mm; }}
  .cover-kicker {{ font-family: {MONO}; font-size: 7pt; letter-spacing: 0.18em;
    text-transform: uppercase; color: {ACCENT}; }}
  .cover h1 {{ font-size: 62pt; margin: 3mm 0 2mm; }}
  .cover-sub {{ font-size: 11pt; line-height: 1.55; color: {MUTED}; max-width: 154mm; }}
  .cover-rule {{ border-top: 0.3mm solid {INK}; margin: 9mm 0 3mm; width: 154mm; }}
  .cover-meta {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 3mm 12mm;
    width: 154mm; }}
  .cover-meta div {{ display: flex; flex-direction: column; gap: 1mm; }}
  .cover-meta .k {{ font-family: {MONO}; font-size: 6pt; letter-spacing: 0.14em;
    text-transform: uppercase; color: {SOFT}; }}
  .cover-meta .v {{ font-size: 9pt; color: {INK}; }}
  .cover-contents {{ position: absolute; right: 18mm; top: 120mm; width: 92mm; }}
  .contents-head {{ font-family: {MONO}; font-size: 6pt; letter-spacing: 0.16em;
    text-transform: uppercase; color: {SOFT}; border-bottom: 0.25mm solid {INK};
    padding-bottom: 2mm; margin-bottom: 2mm; }}
  .cover-contents ol {{ list-style: none; margin: 0; padding: 0; }}
  .cover-contents li {{ display: flex; align-items: baseline; gap: 3mm;
    font-size: 7.1pt; line-height: 1.2; padding: 0.45mm 0;
    border-bottom: 0.15mm solid rgba(31,42,48,0.1); }}
  .cover-contents .n {{ font-family: {MONO}; font-size: 6pt; color: {ACCENT}; }}
  .cover-contents .t {{ flex: 1; color: {INK}; }}
  .cover-contents .p {{ font-family: {MONO}; font-size: 6pt; color: {SOFT}; }}
  .cover .plate-foot {{ position: absolute; left: 18mm; right: 18mm; bottom: 9mm; }}
</style></head>
<body>
{cover_page(len(FIGURES))}
{"".join(figures)}
</body></html>"""
    html_path = TMP / "ZeroGate-diagram-atlas.html"
    html_path.write_text(html, encoding="utf-8")
    pdf_path = OUT / "ZeroGate-diagram-atlas.pdf"
    print_pdf(html_path, pdf_path)
    # The same file at the repository root is easier to hand in or attach.
    root_copy = ROOT / "ZeroGate-diagram-atlas.pdf"
    root_copy.write_bytes(pdf_path.read_bytes())
    print(f"  {root_copy.relative_to(ROOT)}  ({root_copy.stat().st_size / 1024:.0f} KB)")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    TMP.mkdir(parents=True, exist_ok=True)
    if not CHROME.exists():
        raise SystemExit(f"Chrome not found at {CHROME}")
    build_individual()
    build_atlas()


if __name__ == "__main__":
    main()
