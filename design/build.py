"""Build the ZeroGate design dossier as a self-contained HTML site.

Run from the project root:

    python design/build.py

Every page inlines its stylesheet and SVGs. The only remote asset is the
approved Google Fonts stylesheet. The OpenAPI document is emitted separately
as docs/openapi.yaml and linked from the API reference.
"""

from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

import markdown
import yaml

sys.path.insert(0, str(Path(__file__).parent))

from theme import CSS, FONT_LINK
import diagrams
import diagrams_flows


ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
UPDATED = "October 2026"


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

NAV = [
    ("Atlas", "index.html", "index"),
    ("System", "architecture.html", "system"),
    ("Domain", "domain-model.html", "system"),
    ("Data", "data-model.html", "system"),
    ("Flows", "flow-passkey.html", "flows"),
    ("Policy", "policy-engine.html", "decision"),
    ("States", "state-session.html", "states"),
    ("Risk", "risk-scoring.html", "evidence"),
    ("Requirements", "requirements.html", "evidence"),
    ("API", "api.html", "contract"),
]

PAGES = [
    {
        "slug": "architecture",
        "file": "architecture.html",
        "num": "01",
        "chapter": "SYSTEM",
        "title": "Component architecture",
        "short": "Architecture",
        "desc": "Five logical zones compressed into three bands: clients, the ZeroGate control plane, and the resources it protects.",
        "nav": "system",
    },
    {
        "slug": "domain-model",
        "file": "domain-model.html",
        "num": "02",
        "chapter": "SYSTEM",
        "title": "Domain model",
        "short": "Domain",
        "desc": "The seven objects that own identity, access, policy, session, and audit behaviour.",
        "nav": "system",
    },
    {
        "slug": "data-model",
        "file": "data-model.html",
        "num": "03",
        "chapter": "SYSTEM",
        "title": "Logical data model",
        "short": "Data model",
        "desc": "Entities, keys, and cardinalities behind the access decision.",
        "nav": "system",
    },
    {
        "slug": "database-schema",
        "file": "database-schema.html",
        "num": "04",
        "chapter": "SYSTEM",
        "title": "Database schema",
        "short": "Schema",
        "desc": "Physical PostgreSQL slices for identity, access, and audit, with explicit delete semantics.",
        "nav": "system",
    },
    {
        "slug": "flow-passkey",
        "file": "flow-passkey.html",
        "num": "05",
        "chapter": "FLOWS",
        "title": "Passkey login",
        "short": "Passkey",
        "desc": "A WebAuthn ceremony, a risk decision, and a browser session that never sees a password.",
        "nav": "flows",
    },
    {
        "slug": "flow-ssh-certificate",
        "file": "flow-ssh-certificate.html",
        "num": "06",
        "chapter": "FLOWS",
        "title": "SSH certificate issuance",
        "short": "SSH certificate",
        "desc": "Thirty minutes, one host, one principal, and no static key in authorized_keys.",
        "nav": "flows",
    },
    {
        "slug": "flow-jit-approval",
        "file": "flow-jit-approval.html",
        "num": "07",
        "chapter": "FLOWS",
        "title": "Just-in-time approval",
        "short": "JIT approval",
        "desc": "When the score is a question rather than a refusal, a human answers inside a bounded window.",
        "nav": "flows",
    },
    {
        "slug": "flow-session-kill",
        "file": "flow-session-kill.html",
        "num": "08",
        "chapter": "FLOWS",
        "title": "Mid-session kill",
        "short": "Session kill",
        "desc": "How a live session is closed when posture changes, behaviour drifts, or an admin presses the switch.",
        "nav": "flows",
    },
    {
        "slug": "policy-engine",
        "file": "policy-engine.html",
        "num": "09",
        "chapter": "DECISION",
        "title": "Policy Engine",
        "short": "Policy engine",
        "desc": "Hard gates first, arithmetic second, policy third, band last. The order is the safety property.",
        "nav": "decision",
    },
    {
        "slug": "state-session",
        "file": "state-session.html",
        "num": "10",
        "chapter": "STATES",
        "title": "Session lifecycle",
        "short": "Session state",
        "desc": "Five states, two recoverable detours, and two hard exits.",
        "nav": "states",
    },
    {
        "slug": "state-jit",
        "file": "state-jit.html",
        "num": "11",
        "chapter": "STATES",
        "title": "JIT request lifecycle",
        "short": "JIT state",
        "desc": "Submit, wait, decide, consume: a small state machine with a single-use grant.",
        "nav": "states",
    },
    {
        "slug": "state-device",
        "file": "state-device.html",
        "num": "12",
        "chapter": "STATES",
        "title": "Device trust lifecycle",
        "short": "Device state",
        "desc": "Trust is earned in stages, re-evaluated on every report, and lost in one step.",
        "nav": "states",
    },
    {
        "slug": "risk-scoring",
        "file": "risk-scoring.html",
        "num": "13",
        "chapter": "EVIDENCE",
        "title": "Risk scoring",
        "short": "Risk report",
        "desc": "A transparent additive model, bounded anomaly adjustment, and the evaluation plan behind it.",
        "nav": "evidence",
    },
    {
        "slug": "requirements",
        "file": "requirements.html",
        "num": "14",
        "chapter": "EVIDENCE",
        "title": "Functional requirements",
        "short": "Requirements",
        "desc": "Twenty-seven testable promises, fourteen non-functional targets, and an explicit scope boundary.",
        "nav": "evidence",
    },
    {
        "slug": "api",
        "file": "api.html",
        "num": "15",
        "chapter": "CONTRACT",
        "title": "API reference",
        "short": "API",
        "desc": "The OpenAPI 3.1 contract for identity, posture, authorization, sessions, SSH, JIT, policy, risk, audit, and vault.",
        "nav": "contract",
    },
]

PAGE_BY_SLUG = {page["slug"]: page for page in PAGES}


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def chip(label: str, value: str | None = None) -> str:
    if value is None:
        return f'<span class="chip">{label}</span>'
    return f'<span class="chip">{label} <strong>{value}</strong></span>'


def chips(*items: tuple[str, str | None]) -> str:
    return "".join(chip(a, b) for a, b in items)


def callout(label: str, body: str) -> str:
    return (
        '<div class="callout">'
        f'<span class="k">{label}</span>'
        f"{body}"
        "</div>"
    )


def code_block(text: str, cls: str = "") -> str:
    klass = f' class="{cls}"' if cls else ""
    return f"<pre><code{klass}>{esc(text.strip())}</code></pre>"


def table(
    headers: list[str],
    rows: list[list[str]],
    *,
    cls: str = "",
    caption: str | None = None,
    row_ids: list[str] | None = None,
) -> str:
    klass = f' class="{cls}"' if cls else ""
    cap = f"<caption>{caption}</caption>" if caption else ""
    head = "".join(f"<th>{h}</th>" for h in headers)
    def row_html(i: int, row: list[str]) -> str:
        open_tag = f'<tr id="{row_ids[i]}">' if row_ids and row_ids[i] else "<tr>"
        return open_tag + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>"

    body = "".join(row_html(i, row) for i, row in enumerate(rows))
    return (
        '<div class="table-wrap">'
        f"<table{klass}>{cap}<thead><tr>{head}</tr></thead>"
        f"<tbody>{body}</tbody></table>"
        "</div>"
    )


def cards(items: list[tuple[str, str, str]], cls: str = "") -> str:
    klass = f"cards {cls}".strip()
    out = [f'<div class="{klass}">']
    for label, title, body in items:
        out.append(
            '<div class="card">'
            f'<div class="card-label">{label}</div>'
            f"<h3>{title}</h3>"
            f"{body}"
            "</div>"
        )
    out.append("</div>")
    return "".join(out)


def link_row(links: list[tuple[str, str]]) -> str:
    return (
        '<div class="link-row">'
        + "".join(f'<a href="{href}">{label}</a>' for label, href in links)
        + "</div>"
    )


def figure(svg: str, fig_no: str, label: str, caption: str, prefix: str) -> str:
    """Embed an SVG with page-unique ids and an editorial caption."""
    svg = scope_svg(svg, prefix)
    return (
        f'<figure class="diagram-block" id="figure-{fig_no}">'
        '<div class="diagram-top">'
        f'<figcaption class="diagram-label">Fig. {fig_no} &mdash; {label}</figcaption>'
        '<span class="diagram-hint">Scroll to inspect &rarr;</span>'
        "</div>"
        f'<div class="diagram-container">{svg}</div>'
        f'<p class="caption">{caption}</p>'
        "</figure>"
    )


def scope_svg(svg: str, prefix: str) -> str:
    """Prefix every SVG id and every reference to it, so pages can hold many figures."""
    ids = re.findall(r'\bid="([^"]+)"', svg)
    mapping = {old: f"{prefix}-{old}" for old in ids}

    def id_repl(match: re.Match[str]) -> str:
        old = match.group(1)
        return f'id="{mapping.get(old, old)}"'

    svg = re.sub(r'\bid="([^"]+)"', id_repl, svg)

    def url_repl(match: re.Match[str]) -> str:
        old = match.group(1)
        return f"url(#{mapping.get(old, old)})"

    svg = re.sub(r"url\(#([^)]+)\)", url_repl, svg)

    def aria_repl(match: re.Match[str]) -> str:
        tokens = match.group(1).split()
        return 'aria-labelledby="' + " ".join(mapping.get(t, t) for t in tokens) + '"'

    svg = re.sub(r'aria-labelledby="([^"]+)"', aria_repl, svg)
    return svg


def page_head(num: str, chapter: str, title: str, lede: str, meta: str) -> str:
    return (
        '<header class="page-head">'
        '<div class="chapter">'
        f'<span class="chapter-num">{num}</span>'
        f'<span class="eyebrow">{chapter}</span>'
        "</div>"
        f"<h1>{title}</h1>"
        f'<p class="lede">{lede}</p>'
        f'<div class="meta-row">{meta}</div>'
        "</header>"
    )


def page_nav(slug: str) -> str:
    index = next(i for i, p in enumerate(PAGES) if p["slug"] == slug)
    prev_page = PAGES[index - 1] if index > 0 else {"file": "index.html", "short": "Design dossier"}
    next_page = PAGES[index + 1] if index + 1 < len(PAGES) else {"file": "index.html", "short": "Back to the atlas"}
    return (
        '<nav class="page-nav" aria-label="Previous and next pages">'
        f'<a href="{prev_page["file"]}"><span class="dir">Previous</span>'
        f'<span class="name">{prev_page["short"]}</span></a>'
        f'<a class="next" href="{next_page["file"]}"><span class="dir">Next</span>'
        f'<span class="name">{next_page["short"]}</span></a>'
        "</nav>"
    )


def footer() -> str:
    return f"""
<footer class="site-footer">
  <div class="footer-inner">
    <div>ZeroGate design dossier &middot; v0.9 &middot; {UPDATED}<br>
      NIST SP 800-207 access broker &middot; single-tenant lab scope</div>
    <div>Diagram system adapted from <a href="https://github.com/cathrynlavery/diagram-design">cathrynlavery/diagram-design</a> (MIT).<br>
      <a href="../README.md">README</a> &middot; <a href="openapi.yaml">openapi.yaml</a> &middot;
      <a href="risk-scoring-report.md">risk report</a> &middot;
      <a href="functional-requirements.md">requirements</a></div>
  </div>
</footer>"""


def shell(
    *,
    title: str,
    description: str,
    current: str,
    body: str,
    body_class: str = "",
) -> str:
    nav_links = []
    seen_current = False
    for label, href, key in NAV:
        current_attr = ""
        if key == current and not seen_current:
            current_attr = ' aria-current="page"'
            seen_current = True
        nav_links.append(f'<a href="{href}"{current_attr}>{label}</a>')
    klass = f' class="{body_class}"' if body_class else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{esc(description)}">
<meta name="color-scheme" content="light">
{FONT_LINK}
<style>{CSS}</style>
</head>
<body{klass}>
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="header-inner">
    <a class="brand" href="index.html" aria-label="ZeroGate design dossier, home">
      <span class="brand-mark" aria-hidden="true">ZG</span>
      <span class="brand-text">
        <span class="brand-name">ZeroGate</span>
        <span class="brand-sub">Zero-trust access broker &middot; dossier</span>
      </span>
    </a>
    <nav class="site-nav" aria-label="Dossier sections">
      {"".join(nav_links)}
    </nav>
  </div>
</header>
<main id="main">
{body}
</main>
{footer()}
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Index
# ---------------------------------------------------------------------------

INDEX_CARDS = {
    "system": [
        (
            "01",
            "architecture.html",
            "Component architecture",
            "Five zones, two gates, one decision. Follow a request from the employee client to the protected app.",
            "Component diagram",
        ),
        (
            "02",
            "domain-model.html",
            "Domain model",
            "Seven objects that own the rules, the relationships between them, and the invariants they protect.",
            "UML class diagram",
        ),
        (
            "03",
            "data-model.html",
            "Logical data model",
            "Entities, keys, and cardinalities behind identity, access, policy, session, and audit.",
            "ER diagram",
        ),
        (
            "04",
            "database-schema.html",
            "Database schema",
            "The physical PostgreSQL slices, with foreign keys, indexes, and explicit delete semantics.",
            "Schema",
        ),
    ],
    "behaviour": [
        (
            "05",
            "flow-passkey.html",
            "Passkey login",
            "A WebAuthn ceremony, a risk decision, and a session cookie that never carries a password.",
            "Sequence",
        ),
        (
            "06",
            "flow-ssh-certificate.html",
            "SSH certificate issuance",
            "Thirty minutes, one host, one principal, and no static key in authorized_keys.",
            "Sequence",
        ),
        (
            "07",
            "flow-jit-approval.html",
            "Just-in-time approval",
            "When the score is a question rather than a refusal, a human answers inside a bounded window.",
            "Sequence",
        ),
        (
            "08",
            "flow-session-kill.html",
            "Mid-session kill",
            "How a live session is closed when posture changes, behaviour drifts, or an admin presses the switch.",
            "Sequence",
        ),
        (
            "09",
            "policy-engine.html",
            "Policy Engine",
            "Hard gates first, arithmetic second, policy third, band last. The order is the safety property.",
            "Activity diagram",
        ),
        (
            "10",
            "state-session.html",
            "Session lifecycle",
            "Five states, two recoverable detours, and two hard exits.",
            "State machine",
        ),
        (
            "11",
            "state-jit.html",
            "JIT request lifecycle",
            "Submit, wait, decide, consume: a small state machine with a single-use grant.",
            "State machine",
        ),
        (
            "12",
            "state-device.html",
            "Device trust lifecycle",
            "Trust is earned in stages, re-evaluated on every report, and lost in one step.",
            "State machine",
        ),
    ],
    "evidence": [
        (
            "13",
            "risk-scoring.html",
            "Risk scoring",
            "The signal catalog, category caps, hard gates, worked examples, and the ML evaluation plan.",
            "Report",
        ),
        (
            "14",
            "requirements.html",
            "Functional requirements",
            "Twenty-seven testable promises, fourteen non-functional targets, and an explicit scope boundary.",
            "Register",
        ),
        (
            "15",
            "api.html",
            "API reference",
            "The OpenAPI 3.1 contract: 42 paths, 53 operations, and one explainable decision shape.",
            "OpenAPI 3.1",
        ),
    ],
}


def toc_card(num: str, href: str, title: str, desc: str, typ: str, accent: bool = False) -> str:
    klass = "toc-card accent" if accent else "toc-card"
    return (
        f'<a class="{klass}" href="{href}">'
        f'<span class="num">{num}</span>'
        f"<h3>{title}</h3>"
        f"<p>{desc}</p>"
        f'<span class="type">{typ}</span>'
        "</a>"
    )


def build_index() -> str:
    system = "".join(toc_card(*card) for card in INDEX_CARDS["system"])
    behaviour = "".join(toc_card(*card) for card in INDEX_CARDS["behaviour"])
    evidence = "".join(toc_card(*card) for card in INDEX_CARDS["evidence"])

    body = f"""
<section class="index-hero wrap">
  <div class="chapter">
    <span class="chapter-num">ZG</span>
    <span class="eyebrow">Design dossier &middot; {UPDATED}</span>
  </div>
  <h1>Access, earned<br><em class="hero-em">per request.</em></h1>
  <p class="lede">ZeroGate is a zero-trust access broker for web applications and SSH servers. It checks identity, device posture, and a live risk score on every request, explains the decision, and can cut a session mid-flight. This dossier is the design record: the diagrams, the data model, the decision logic, the contract, and the evidence behind them.</p>
  <div class="meta-row">
    {chips(("NIST", "SP 800-207"), ("SCOPE", "Web + SSH"), ("STATUS", "Design baseline v0.9"), ("EDITION", "October 2026"))}
  </div>
  <div class="index-rule">
    <div><span class="k">What is protected</span><span class="v">Internal web applications and Linux SSH servers. Nothing else.</span></div>
    <div><span class="k">Where decisions happen</span><span class="v">A Policy Engine behind two enforcement points, never inside them.</span></div>
    <div><span class="k">How access ends</span><span class="v">A 60-second heartbeat, a live score, and a two-second kill target.</span></div>
  </div>
</section>

<div class="wrap">
  <div class="stat-strip">
    <div class="stat"><span class="n">05</span><span class="l">logical zones</span></div>
    <div class="stat"><span class="n">04</span><span class="l">trust bands</span></div>
    <div class="stat"><span class="n">15</span><span class="l">design pages</span></div>
    <div class="stat"><span class="n">27</span><span class="l">functional requirements</span></div>
  </div>
  <div class="pdf-row">
    <a class="pdf-download" href="diagrams/ZeroGate-diagram-atlas.pdf"><span class="pdf-tag">PDF</span> Diagram atlas &middot; 13 vector plates <span class="arrow">&rarr;</span></a>
  </div>

  <div class="section-head"><h2>System</h2><span class="count">04 artefacts &middot; structure</span></div>
  <div class="toc-grid four">{system}</div>

  <div class="section-head"><h2>Behaviour</h2><span class="count">08 artefacts &middot; time and state</span></div>
  <div class="toc-grid four">{behaviour}</div>

  <div class="section-head"><h2>Evidence</h2><span class="count">03 artefacts &middot; proof</span></div>
  <div class="toc-grid">{evidence}</div>

  <div class="section-head"><h2>The operating envelope</h2><span class="count">Hard gates override every score</span></div>
  <div class="band-strip">
    <div class="band-allow"><span class="k">Allow</span><span class="v">80&ndash;100</span><span class="d">Create the session, attach obligations, audit the decision.</span></div>
    <div class="band-step"><span class="k">Step-up</span><span class="v">60&ndash;79</span><span class="d">Re-authenticate within five minutes, then re-score.</span></div>
    <div class="band-approve"><span class="k">Approval</span><span class="v">40&ndash;59</span><span class="d">Suspend, open a JIT request, give an approver 15 minutes.</span></div>
    <div class="band-deny"><span class="k">Deny / kill</span><span class="v">0&ndash;39</span><span class="d">No new session; terminate any live session and revoke credentials.</span></div>
  </div>

  <div class="section-head"><h2>Reading paths</h2><span class="count">Three ways through the dossier</span></div>
  <div class="path-row">
    <span class="n">A</span>
    <div><h3>Follow one request</h3><p>Start with the component view, then trace a login, a decision, and a kill.</p></div>
    <p><a href="architecture.html">Architecture</a> &rarr; <a href="flow-passkey.html">Passkey login</a> &rarr; <a href="policy-engine.html">Policy Engine</a> &rarr; <a href="flow-session-kill.html">Mid-session kill</a></p>
  </div>
  <div class="path-row">
    <span class="n">B</span>
    <div><h3>Defend the model</h3><p>Move from the domain objects to the logical entities and the physical tables.</p></div>
    <p><a href="domain-model.html">Domain model</a> &rarr; <a href="data-model.html">Logical data model</a> &rarr; <a href="database-schema.html">Database schema</a></p>
  </div>
  <div class="path-row">
    <span class="n">C</span>
    <div><h3>Build against it</h3><p>Use the register as the promise, the contract as the interface, and the risk report as the evidence.</p></div>
    <p><a href="requirements.html">Requirements</a> &rarr; <a href="api.html">API reference</a> &rarr; <a href="risk-scoring.html">Risk report</a></p>
  </div>

  <div class="manifest">
    <div>
      <h3>About this edition</h3>
      <p>This is a design dossier, not a production runbook. It records the intended system at lab scale: one organisation, test participants, two enforcement points, and a demo attack set. Targets are design targets until the load tests exist.</p>
    </div>
    <div>
      <h3>Source documents</h3>
      <ul>
        <li><span>ZeroGate Project Scope.pdf</span> &mdash; feature scope and ownership</li>
        <li><span>zero-trust-broker-zones.pdf</span> &mdash; zones and end-to-end stories</li>
        <li><span>openapi.yaml</span> &mdash; API contract</li>
      </ul>
    </div>
    <div>
      <h3>Colophon</h3>
      <ul>
        <li><span>Type</span> Instrument Serif &middot; Geist &middot; Geist Mono</li>
        <li><span>Palette</span> warm paper, ink, brick accent</li>
        <li><span>Diagram system</span> cathrynlavery/diagram-design (MIT)</li>
      </ul>
    </div>
  </div>
</div>
"""
    return shell(
        title="ZeroGate &middot; Design dossier",
        description="ZeroGate design dossier: a zero-trust access broker for web applications and SSH servers, built on NIST SP 800-207.",
        current="index",
        body=body,
    )


# ---------------------------------------------------------------------------
# 01 Architecture
# ---------------------------------------------------------------------------

def build_architecture() -> str:
    svg = figure(
        diagrams.component_diagram(),
        "01",
        "Component architecture",
        "<b>Read it left to right.</b> The employee and admin clients prove identity and posture. The two enforcement points, the web proxy and the SSH certificate authority, ask the Policy Engine for every decision. The Policy Engine consults the risk scorer and the published policy set, while the Policy Administrator opens, suspends, and kills sessions. The audit chain records the outcome. Dashed lines are asynchronous control or telemetry; solid lines are request paths.",
        "fig01",
    )

    components = table(
        ["Zone", "Component", "Responsibility", "Owner", "Track"],
        [
            ["Employee side", "Employee client", "Passkey ceremony, posture agent, SSH helper CLI.", "Frontend / Security", "Core"],
            ["Employee side", "Admin console", "Policy authoring, device enrollment, approval queue, live sessions, kill.", "Frontend / Backend", "Core"],
            ["Enforcement", "Web proxy", "PEP in front of every internal web app; authorizes each HTTP request.", "Networking", "Core"],
            ["Enforcement", "SSH certificate authority", "Signs short-lived certificates after the Policy Engine allows.", "Security &amp; Hardware", "Core"],
            ["Decision", "Policy Engine", "Hard gates, risk, policy, and trust-band decision.", "Backend &amp; AI", "Core"],
            ["Decision", "Risk scorer + ML", "Rules and a bounded anomaly adjustment; returns a score and reasons.", "Backend &amp; AI", "Core / Add-on"],
            ["Decision", "Policy Administrator", "Opens, suspends, resumes, and kills sessions; revokes certificates.", "Backend &amp; AI", "Core"],
            ["Decision", "Audit chain", "Append-only, SHA-256 hash-chained record of every decision and lifecycle event.", "Security &amp; Hardware", "Core"],
            ["Protected", "Internal web apps and Linux servers", "Demo targets; reachable only through an enforcement point.", "Security / DevOps", "Core"],
        ],
        cls="compact",
        caption="Table 1 &mdash; The nine components in the figure, grouped by the three bands.",
    )

    latency = table(
        ["Hop", "Design target", "Measured where"],
        [
            ["Passkey login ceremony", "p95 &le; 3 s", "Portal and authenticator"],
            ["Policy decision <code>/authorize</code>", "p95 &le; 80 ms at 500 sessions", "Policy Engine"],
            ["Proxy overhead per request", "p95 &le; 50 ms", "Web proxy"],
            ["SSH certificate acquisition", "p95 &le; 300 ms", "SSH helper and CA"],
            ["Kill propagation", "p95 &le; 2 s", "Decision to proxy close and certificate revoke"],
            ["Risk inference", "p95 &le; 15 ms", "Risk scorer"],
        ],
        cls="compact",
        caption="Table 2 &mdash; Latency budgets. These are design targets, not measured production numbers.",
    )

    body = f"""
<div class="wrap">
  <div class="page">
    {page_head(
        "01", "SYSTEM / ARCHITECTURE",
        "Five zones, two gates,<br>one decision.",
        "Nothing reaches a protected resource without passing a gate that asks the Policy Engine. The employee, the admin, the enforcement points, the decision brain, and the protected resources are separated on purpose: the gate enforces, the engine decides, the administrator acts, and the audit chain remembers.",
        chips(("FIG.", "01"), ("9", "components"), ("2", "enforcement points"), ("NIST", "800-207 &sect;2.1"))
    )}
    {svg}

    <div class="prose">
      <h2>The shape of the system</h2>
      <p>The source material describes five zones: the employee side, the enforcement points, the decision brain, the protected resources, and the admin side. The figure compresses those into three bands so the request path stays legible. The admin side sits with the employee clients because both are human-facing; the enforcement points and the decision brain share the control plane because they are one conversation.</p>
      <p>The separation that matters is <strong>PDP versus PEP</strong>. The web proxy and the SSH certificate authority are Policy Enforcement Points. They hold no policy of their own and make no judgement about a person. They ask, then enforce. The Policy Engine is the Policy Decision Point. It combines hard gates, the risk score, and the published policy into one answer with obligations. NIST SP 800-207 calls for exactly this split; the trust algorithm itself is left open, which is why this project defines one.</p>

      {components}

      <h2>Two paths, one decision</h2>
      <p>A web request and an SSH connection look different at the edge and identical at the centre. The web proxy authenticates the browser session, adds the request context, and calls <code>POST /v1/authorize</code>. The SSH authority receives a certificate request from the helper, authenticates the user and device, and calls the same endpoint with a different action and resource. Both receive the same decision shape: decision, band, score, signals, obligations, audit id, and correlation id.</p>
      <p>That sameness is deliberate. It means one policy language, one explanation format, one audit record, and one place to fix a mistake. It also means the two paths can share the session cache at the enforcement point: a positive decision is valid for at most one second, and a kill invalidates it immediately.</p>

      <div class="cards two">
        <div class="card">
          <div class="card-label">The gate</div>
          <h3>Enforcement points never decide</h3>
          <p>The proxy and the CA are deliberately thin. They authenticate the channel, attach context, call the engine, and enforce the answer. If the engine is unavailable, they fail closed. If a cached decision is older than one second, they ask again.</p>
          <ul class="rule-list">
            <li>No bypass path from the lab network.</li>
            <li>No local policy exceptions.</li>
            <li>No long-lived authorization cache.</li>
          </ul>
        </div>
        <div class="card">
          <div class="card-label">The brain</div>
          <h3>The engine has one job</h3>
          <p>The Policy Engine evaluates hard gates before any arithmetic, then scores, then applies policy, then maps the result to a band. It returns obligations rather than side effects; the Policy Administrator carries them out.</p>
          <ul class="rule-list">
            <li>Hard gates cannot be outvoted.</li>
            <li>Every answer carries an audit id.</li>
            <li>The same input returns the same answer.</li>
          </ul>
        </div>
      </div>

      <h2>Why the control plane looks like this</h2>
      <p>The Policy Administrator is separate from the Policy Engine because decisions and actions have different failure modes. A decision is a pure function of context, policy version, and model version. An action touches a live session, a proxy cache, a certificate, and a notification channel. Keeping them apart makes the decision reproducible and the action retryable.</p>
      <p>The audit chain is separate from the operational database for the same reason. It is append-only, sequence-numbered, and hash-chained. The application role can insert but cannot update or delete. A reviewer can verify the chain without trusting the service that wrote it. The latency dashboard reads timings from the same event stream, so the performance claim and the security claim share one source.</p>

      {latency}

      <h2>What this figure does not show</h2>
      <p>The figure is a component view, not a deployment diagram. It does not show replicas, the HSM boundary, the lab network, or the observability stack. Those belong in a deployment view. It also does not show the stretch components: Single Packet Auth and SPIFFE/SPIRE service identity are deliberately absent from the main path so the core story stays honest.</p>

      {callout(
        "Scope boundary",
        "<p>Only web applications and SSH servers are protected. Kubernetes, databases, email security, AI-agent governance, SWG, CASB, DLP, remote browser isolation, and firewall-as-a-service are out of scope. The system is single-tenant and lab-scale; there is no production deployment claim.</p>"
      )}

      <h2>Failure posture</h2>
      <ul>
        <li><strong>Engine timeout:</strong> deny. A late allow is worse than a false deny.</li>
        <li><strong>Risk scorer unavailable:</strong> rules-only score, with a visible <code>MODEL_UNAVAILABLE</code> reason and no ML adjustment.</li>
        <li><strong>Audit chain unavailable:</strong> fail closed for new sessions; never buffer decisions in memory and call them audited.</li>
        <li><strong>CA unavailable:</strong> no certificate; the helper prints an actionable reason and exits non-zero.</li>
        <li><strong>Proxy cache stale:</strong> at most one second; a kill invalidates it before the next request is admitted.</li>
      </ul>

      {link_row([
        ("Domain model &rarr;", "domain-model.html"),
        ("Policy Engine &rarr;", "policy-engine.html"),
        ("Kill sequence &rarr;", "flow-session-kill.html"),
        ("API contract &rarr;", "api.html"),
      ])}
    </div>
  </div>
  {page_nav("architecture")}
</div>
"""
    return shell(
        title="Component architecture &middot; ZeroGate",
        description=PAGE_BY_SLUG["architecture"]["desc"],
        current="system",
        body=body,
    )


# ---------------------------------------------------------------------------
# 02 Domain model
# ---------------------------------------------------------------------------

def build_domain() -> str:
    svg = figure(
        diagrams.class_diagram(),
        "02",
        "Domain model",
        "<b>Seven objects, one aggregate root.</b> User is the identity root. Device and PasskeyCredential describe the endpoint and the authenticator. Policy is a versioned decision input. AccessRequest records the ask; Session records the live grant. AuditEvent is append-only and may outlive the session it describes. Cardinalities are shown at the ends of each association.",
        "fig02",
    )

    classes = table(
        ["Class", "Responsibility", "Invariant it protects"],
        [
            ["<code>User</code>", "The person: email, role, status, and the operations to enroll a passkey and request access.", "Email is unique. A disabled user cannot own a live session."],
            ["<code>Device</code>", "An enrolled endpoint and its latest posture: OS, encryption, root/jailbreak, compliance.", "A device belongs to one user. Revocation is terminal; re-enrollment creates a new device id."],
            ["<code>PasskeyCredential</code>", "The public key, AAGUID, signature counter, and verification operation.", "The private key never leaves the authenticator. The counter must increase on every assertion."],
            ["<code>Policy</code>", "A versioned condition set with an effect, evaluated against request context.", "Published versions are immutable. Explicit deny wins over allow."],
            ["<code>AccessRequest</code>", "A request for a resource and action with a requested TTL and a request state.", "Approval is a state transition, not a session. A request cannot approve itself."],
            ["<code>Session</code>", "A live grant with a trust score, state, start time, and expiry.", "Kill is idempotent and terminal. A session always has one user and one resource."],
            ["<code>AuditEvent</code>", "An append-only record with a sequence number, type, and previous hash.", "Sequence numbers are gap-free. <code>prevHash</code> must match the previous event."],
        ],
        caption="Table 1 &mdash; The seven classes, their responsibilities, and the invariant each one carries.",
    )

    relationships = table(
        ["From", "Cardinality", "To", "Meaning"],
        [
            ["User", "1 &rarr; 0..*", "Device", "A person may enroll several devices; a device has one owner."],
            ["Device", "1 &rarr; 0..*", "PasskeyCredential", "A device may hold more than one authenticator credential."],
            ["User", "1 &rarr; 0..*", "AccessRequest", "A person may ask for access many times."],
            ["AccessRequest", "0..1 &rarr; 1", "Session", "An approved request may open one session; a direct allow has no request."],
            ["Policy", "1 &rarr; 0..*", "Session", "The policy version that governed the grant is pinned to the session."],
            ["Session", "1 &rarr; 0..*", "AuditEvent", "A session produces many events; an event may survive its session."],
            ["User", "1 &rarr; 0..*", "AuditEvent", "The actor is recorded as an immutable UUID, not a cascading foreign key."],
        ],
        cls="compact",
        caption="Table 2 &mdash; Associations in the figure. The arrow points from the owner to the owned side.",
    )

    body = f"""
<div class="wrap">
  <div class="page">
    {page_head(
        "02", "SYSTEM / DOMAIN",
        "Seven objects that<br>own the rules.",
        "The domain model is deliberately small. It contains the things that must stay consistent when a request is decided: the person, the device, the credential, the policy, the request, the session, and the record. Everything else is a projection, a cache, or an operational detail.",
        chips(("FIG.", "02"), ("7", "classes"), ("7", "associations"), ("10", "operations"))
    )}
    {svg}

    <div class="prose">
      <h2>The cast</h2>
      <p><strong>User</strong> is the aggregate root. A user can hold several devices and several credentials, but the identity is singular. <strong>Device</strong> is the endpoint that carries posture; <strong>PasskeyCredential</strong> is the authenticator material bound to that device. Splitting them matters because a device can be revoked while a credential record remains useful for audit, and a credential can be replaced without inventing a new device.</p>
      <p><strong>Policy</strong> is a versioned decision input, not a mutable setting. <strong>AccessRequest</strong> captures the ask and its approval state. <strong>Session</strong> captures the grant and its live trust score. <strong>AuditEvent</strong> captures what happened. The model keeps the ask, the grant, and the record separate because they have different lifetimes: a request can expire without a session, a session can be killed while its audit record survives, and an audit record must remain verifiable after the user is gone.</p>

      {classes}

      <h2>Why these boundaries</h2>
      <p>The boundaries follow the decisions the system has to make. A passkey assertion is verified against a credential, not against a user directly, because the credential is what the authenticator signs with. Device posture is attached to a device, not to a session, because posture changes while sessions are live. A policy is pinned to a session by id and version, because a later policy edit must not retroactively change the explanation for an earlier decision.</p>
      <p>The model also keeps the <strong>Policy Administrator</strong> out of the class diagram. The administrator is a service role that carries out decisions; it is not a domain object with its own state. That is why the component view has a Policy Administrator and the domain view does not. The same is true of the risk scorer: it produces a score and reasons, but the score is an input to a decision, not an entity with a lifecycle.</p>

      {relationships}

      <h2>Invariants worth testing</h2>
      <ol>
        <li>A session always references exactly one user and one resource; both are required.</li>
        <li>A session may reference at most one access request. A direct allow has <code>request_id = NULL</code>.</li>
        <li>A credential belongs to exactly one device and one user; the user id is denormalised for owner lookup.</li>
        <li>An audit event may have <code>session_id = NULL</code>. Deleting a session must not delete its history.</li>
        <li>A published policy version is immutable. A decision records both the policy id and the version.</li>
        <li>A trust score is an integer in <code>[0, 100]</code>. The band is derived from the score and never accepted as input.</li>
        <li><code>KILLED</code> is terminal. A repeated kill returns the existing result, not a new state.</li>
      </ol>

      <div class="cards two">
        <div class="card">
          <div class="card-label">Modelling choice</div>
          <h3>Resource is a first-class entity</h3>
          <p>A resource has a name, a kind (web or SSH), a host, and a sensitivity class. Keeping it separate from the request lets policy target a catalog entry rather than a free-form URL or hostname. An unknown resource is a hard gate, not a policy miss.</p>
        </div>
        <div class="card">
          <div class="card-label">Modelling choice</div>
          <h3>Audit is not a child of session</h3>
          <p>The audit event carries a nullable session id and its own actor id. If a session is deleted, the event remains. If a user is deleted, the actor UUID remains as a historical reference. This is intentional denormalisation in service of evidence.</p>
        </div>
      </div>

      <h2>What is deliberately absent</h2>
      <p>The class model covers the access-control bounded context. SecureVault payloads, SSH certificate blobs, and policy version history are operational stores with different encryption and retention rules; they are described in the database and API pages rather than forced into this diagram. There is no <code>Tenant</code> class because the system is single-tenant. There is no <code>KubernetesWorkload</code> or <code>Database</code> class because those resources are out of scope.</p>

      {callout(
        "Reading the cardinalities",
        "<p>The diagram uses the UML convention: the label at the far end describes how many instances of that class may relate to one instance of the near class. <code>User 1 &rarr; 0..* Device</code> means one user may have zero or more devices, and each device belongs to exactly one user.</p>"
      )}

      {link_row([
        ("Logical data model &rarr;", "data-model.html"),
        ("Database schema &rarr;", "database-schema.html"),
        ("Requirements &rarr;", "requirements.html"),
        ("API contract &rarr;", "api.html"),
      ])}
    </div>
  </div>
  {page_nav("domain-model")}
</div>
"""
    return shell(
        title="Domain model &middot; ZeroGate",
        description=PAGE_BY_SLUG["domain-model"]["desc"],
        current="system",
        body=body,
    )


# ---------------------------------------------------------------------------
# 03 Logical data model
# ---------------------------------------------------------------------------

def build_data_model() -> str:
    svg = figure(
        diagrams.er_diagram(),
        "03",
        "Logical data model",
        "<b>Eight entities, seven relationships.</b> USER is the aggregate root. DEVICE and PASSKEY form the identity chain. RESOURCE is the target catalog. POLICY governs sessions. ACCESS_REQUEST records the ask; SESSION records the grant. AUDIT_EVENT is the append-only record, with a nullable session link so history survives deletion. Primary keys are marked <code>#</code>; foreign keys use an arrow.",
        "fig03",
    )

    entities = table(
        ["Entity", "What it represents", "Key attributes"],
        [
            ["<code>USER</code>", "A person with a role and an account status.", "<code>id</code>, <code>email</code>, <code>role</code>, <code>status</code>"],
            ["<code>DEVICE</code>", "An enrolled endpoint and its latest posture state.", "<code>id</code>, <code>user_id</code>, <code>hostname</code>, <code>os_version</code>, <code>encrypted</code>, <code>compliant</code>"],
            ["<code>PASSKEY</code>", "A public-key credential bound to a device and a user.", "<code>id</code>, <code>device_id</code>, <code>aaguid</code>, <code>public_key</code>, <code>sign_count</code>"],
            ["<code>RESOURCE</code>", "A protected web app or SSH host in the catalog.", "<code>id</code>, <code>name</code>, <code>kind</code>, <code>host</code>, <code>sensitivity</code>"],
            ["<code>POLICY</code>", "A versioned condition set and effect.", "<code>id</code>, <code>effect</code>, <code>conditions</code>, <code>version</code>"],
            ["<code>ACCESS_REQUEST</code>", "A request for a resource and action, with a TTL and a decision state.", "<code>id</code>, <code>user_id</code>, <code>resource_id</code>, <code>state</code>, <code>requested_ttl</code>"],
            ["<code>SESSION</code>", "A live grant with a score, state, and expiry.", "<code>id</code>, <code>user_id</code>, <code>request_id</code>, <code>trust_score</code>, <code>expires_at</code>"],
            ["<code>AUDIT_EVENT</code>", "An append-only record of a decision or lifecycle event.", "<code>id</code>, <code>seq</code>, <code>actor_id</code>, <code>session_id</code>, <code>type</code>, <code>prev_hash</code>"],
        ],
        caption="Table 1 &mdash; The eight logical entities and the attributes that carry the design.",
    )

    relationships = table(
        ["Relationship", "Cardinality", "Delete rule", "Why"],
        [
            ["USER &rarr; DEVICE", "1 : N", "Cascade", "A device has no meaning without its owner."],
            ["DEVICE &rarr; PASSKEY", "1 : N", "Cascade", "A credential is bound to one device."],
            ["USER &rarr; ACCESS_REQUEST", "1 : N", "Cascade", "Requests are owned by the requester."],
            ["RESOURCE &rarr; ACCESS_REQUEST", "1 : N", "Restrict", "A resource with history cannot be removed silently."],
            ["ACCESS_REQUEST &rarr; SESSION", "0..1 : 1", "Set null", "A session can outlive a request record."],
            ["POLICY &rarr; SESSION", "1 : N", "Restrict", "A policy version cited by a session cannot be deleted."],
            ["SESSION &rarr; AUDIT_EVENT", "1 : N", "Set null", "Evidence survives the session it describes."],
        ],
        cls="compact",
        caption="Table 2 &mdash; Cardinalities and the delete semantics they imply in the physical schema.",
    )

    classification = table(
        ["Data group", "Examples", "Sensitivity", "Retention"],
        [
            ["Identity", "Email, role, account status", "PII; access-controlled", "Life of the account"],
            ["Device posture", "Hostname, OS version, disk and root flags", "Internal; potentially sensitive", "90 days hot, then aggregate"],
            ["Credentials", "Public key, AAGUID, signature counter", "Public material; integrity-critical", "Life of the credential plus audit"],
            ["Policy", "Conditions, effect, version, publisher", "Confidential", "Versioned indefinitely"],
            ["Access and session", "Resource, action, trust score, state", "Confidential", "1 year"],
            ["Audit", "Actor, event type, hashes, sequence", "Integrity-critical", "1 year, append-only"],
        ],
        cls="compact",
        caption="Table 3 &mdash; Data classification. No biometrics, packet payloads, or file contents are stored.",
    )

    body = f"""
<div class="wrap">
  <div class="page">
    {page_head(
        "03", "SYSTEM / DATA",
        "Entities, keys,<br>and cardinality.",
        "The logical model is the bridge between the domain classes and the physical tables. It fixes the nouns, the identifiers, and the relationships, but leaves storage types, indexes, and delete rules to the schema page.",
        chips(("FIG.", "03"), ("8", "entities"), ("7", "relationships"), ("1", "aggregate root"))
    )}
    {svg}

    <div class="prose">
      <h2>The access-control core</h2>
      <p>The model tells one story: a user asks for a resource, a policy governs the session, and an audit event records what happened. <strong>USER</strong> is the aggregate root because every other identity record hangs from it. <strong>DEVICE</strong> and <strong>PASSKEY</strong> form a chain: the user owns the device, the device holds the credential. <strong>RESOURCE</strong> is a catalog entry, not a URL copied into a request, so policy can target a named target rather than a string.</p>
      <p><strong>ACCESS_REQUEST</strong> is the ask. It has a requested TTL, a state, and a decision actor. <strong>SESSION</strong> is the grant. It points back to the request when there was one, and carries the current score and expiry. That distinction is what makes JIT possible: a request can wait for a human while no session exists. <strong>AUDIT_EVENT</strong> is the record, and it is deliberately not a child of session.</p>

      {entities}

      <h2>Relationships and delete semantics</h2>
      <p>Cardinality alone does not tell you what happens when a row is deleted. The model therefore carries a delete rule for each relationship, and the physical schema implements it with foreign-key actions. The rule follows the evidence: a device or credential has no meaning without its user, so it cascades; a resource or policy cited by history cannot vanish, so it restricts; a session link in the audit log is nulled, never cascaded.</p>

      {relationships}

      <h2>Three modelling decisions</h2>
      <div class="cards">
        <div class="card">
          <div class="card-label">01 / Catalog</div>
          <h3>Resource is not a URL</h3>
          <p>A resource has a stable id, a kind (<code>web</code> or <code>ssh</code>), a host, and a sensitivity class. The proxy and the CA resolve the id to a target. An unknown id is a hard gate, not a policy miss.</p>
        </div>
        <div class="card">
          <div class="card-label">02 / Evidence</div>
          <h3>Audit outlives session</h3>
          <p><code>session_id</code> is nullable. The actor is stored as a UUID without a cascading foreign key. Deleting a user or a session must not erase the record that a decision happened.</p>
        </div>
        <div class="card">
          <div class="card-label">03 / History</div>
          <h3>Policy is versioned</h3>
          <p>A decision pins the policy id and version. A later edit creates a new version; it does not rewrite the explanation for an old session. The physical schema makes the published version immutable.</p>
        </div>
      </div>

      <h2>What the model does not store</h2>
      <p>There is no private key, no biometric template, no raw packet, and no file content. The passkey table holds a public key and a counter. The audit table holds payload hashes, not payloads. The vault is a separate encrypted store because its contents have a different threat model and a different access path. The logical model is intentionally boring about secrets: it records only what is needed to make and defend a decision.</p>

      {classification}

      {callout(
        "From logical to physical",
        "<p>The next page turns these entities into PostgreSQL tables. It splits the schema into an identity slice and an access slice, repeats the <code>users</code> table as the join point, and makes every cascade and restrict rule explicit.</p>"
      )}

      {link_row([
        ("Domain model &rarr;", "domain-model.html"),
        ("Database schema &rarr;", "database-schema.html"),
        ("Risk report &rarr;", "risk-scoring.html"),
        ("API contract &rarr;", "api.html"),
      ])}
    </div>
  </div>
  {page_nav("data-model")}
</div>
"""
    return shell(
        title="Logical data model &middot; ZeroGate",
        description=PAGE_BY_SLUG["data-model"]["desc"],
        current="system",
        body=body,
    )


# ---------------------------------------------------------------------------
# 04 Database schema
# ---------------------------------------------------------------------------

def build_database() -> str:
    identity_svg = figure(
        diagrams.db_identity(),
        "04A",
        "Identity and device schema",
        "<b>The identity slice.</b> <code>users</code> owns <code>devices</code>; <code>devices</code> owns <code>passkeys</code>; <code>users</code> owns <code>recovery_shares</code>. The passkey table also carries a denormalised <code>user_id</code> so an owner lookup does not require a join through the device. Red edges are cascading foreign keys; the accent header marks the cascade target that matters most.",
        "fig04a",
    )
    access_svg = figure(
        diagrams.db_access(),
        "04B",
        "Access, policy, and audit schema",
        "<b>The access slice.</b> <code>users</code> is repeated as the join point. <code>policies</code> restricts deletion of the requests and sessions it governs. <code>access_requests</code> becomes a session through a nullable link. <code>audit_events</code> keeps a nullable session reference, so the record survives the session. The <code>users &rarr; sessions</code> cascade is routed above the policy table to keep the reading order clear.",
        "fig04b",
    )

    tables = table(
        ["Table", "Slice", "Purpose", "Key relationships"],
        [
            ["<code>users</code>", "Identity + access", "Account, role, and status.", "Root for devices, passkeys, requests, sessions, recovery shares."],
            ["<code>devices</code>", "Identity", "Endpoint identity and latest posture.", "<code>user_id &rarr; users.id</code> (cascade)."],
            ["<code>passkeys</code>", "Identity", "WebAuthn public key and counter.", "<code>device_id &rarr; devices.id</code> (cascade); <code>user_id</code> for owner lookup."],
            ["<code>recovery_shares</code>", "Identity", "k-of-n Shamir share metadata and hashes.", "<code>user_id &rarr; users.id</code> (cascade)."],
            ["<code>policies</code>", "Access", "Published policy version and effect.", "Referenced by requests and sessions (restrict)."],
            ["<code>access_requests</code>", "Access", "The ask: resource, action, TTL, state.", "<code>user_id</code> (cascade); <code>policy_id</code> (restrict)."],
            ["<code>sessions</code>", "Access", "The live grant and current score.", "<code>user_id</code> (cascade); <code>request_id</code> (set null)."],
            ["<code>audit_events</code>", "Access", "Append-only hash chain.", "<code>session_id</code> (set null); <code>actor_id</code> intentionally not a foreign key."],
        ],
        caption="Table 1 &mdash; The eight unique tables across the two slices. <code>users</code> appears in both figures.",
    )

    cascades = table(
        ["Parent deletion", "Child", "Action", "Rationale"],
        [
            ["<code>users</code>", "<code>devices</code>", "CASCADE", "A device cannot exist without an owner."],
            ["<code>devices</code>", "<code>passkeys</code>", "CASCADE", "A credential is bound to one device."],
            ["<code>users</code>", "<code>recovery_shares</code>", "CASCADE", "Share metadata is owned by the user."],
            ["<code>users</code>", "<code>access_requests</code>", "CASCADE", "A request is owned by the requester."],
            ["<code>users</code>", "<code>sessions</code>", "CASCADE", "A session cannot outlive its user."],
            ["<code>policies</code>", "<code>access_requests</code>", "RESTRICT", "A policy cited by history cannot be deleted."],
            ["<code>policies</code>", "<code>sessions</code>", "RESTRICT", "A governing version cannot be deleted."],
            ["<code>access_requests</code>", "<code>sessions</code>", "SET NULL", "A session can outlive its request."],
            ["<code>sessions</code>", "<code>audit_events</code>", "SET NULL", "Evidence survives the session."],
        ],
        cls="compact",
        caption="Table 2 &mdash; Delete semantics. The physical schema implements every row explicitly.",
    )

    index_table = table(
        ["Index", "Table", "Why it exists"],
        [
            ["<code>uq_users_email</code>", "<code>users</code>", "Case-insensitive uniqueness for login."],
            ["<code>idx_users_status</code>", "<code>users</code>", "Admin filters for disabled and dormant accounts."],
            ["<code>idx_devices_user</code>", "<code>devices</code>", "List a user's devices without a scan."],
            ["<code>idx_devices_compliant</code>", "<code>devices</code>", "Posture dashboards and risk inputs."],
            ["<code>uq_passkeys_credential</code>", "<code>passkeys</code>", "One row per credential material."],
            ["<code>uq_recovery_user_index</code>", "<code>recovery_shares</code>", "One share per index per user."],
            ["<code>idx_policies_effect</code>", "<code>policies</code>", "Policy listing and effect filters."],
            ["<code>idx_requests_state</code>", "<code>access_requests</code>", "Approval queue and expiry sweeper."],
            ["<code>idx_requests_user</code>", "<code>access_requests</code>", "A user's request history."],
            ["<code>idx_sessions_live</code>", "<code>sessions</code>", "Live-session dashboard and kill lookup."],
            ["<code>idx_sessions_user</code>", "<code>sessions</code>", "A user's session history."],
            ["<code>uq_audit_seq</code>", "<code>audit_events</code>", "Gap-free chain verification."],
            ["<code>idx_audit_session</code>", "<code>audit_events</code>", "Reconstruct one session's timeline."],
        ],
        cls="compact",
        caption="Table 3 &mdash; Indexes named in the figures and the query each one serves.",
    )

    body = f"""
<div class="wrap">
  <div class="page">
    {page_head(
        "04", "SYSTEM / SCHEMA",
        "The tables behind<br>the decision.",
        "The physical schema is PostgreSQL 16, split into two readable slices: identity and access. The <code>users</code> table is repeated because it is the join point. Every foreign key states its delete rule, and the audit table is protected by grants rather than convention.",
        chips(("FIG.", "04A&ndash;04B"), ("8", "tables"), ("9", "delete rules"), ("POSTGRES", "16"))
    )}
    {identity_svg}
    {access_svg}

    <div class="prose">
      <h2>Conventions</h2>
      <ul>
        <li><strong>Identifiers:</strong> UUID v7 in every table, generated by the application, so ids sort by time and do not leak row counts.</li>
        <li><strong>Time:</strong> <code>timestamptz</code> everywhere; the database stores UTC and the UI renders the user's local time.</li>
        <li><strong>Enums:</strong> PostgreSQL enum types for <code>user_role</code>, <code>user_status</code>, <code>policy_effect</code>, <code>request_state</code>, <code>session_state</code>, and <code>event_type</code>. Adding a value is a migration, which is the point.</li>
        <li><strong>Names:</strong> snake_case, plural tables, singular columns, explicit <code>_at</code> suffixes.</li>
        <li><strong>Secrets:</strong> no plaintext secret, private key, biometric, or payload is stored in these tables.</li>
      </ul>

      {tables}

      <h2>Delete semantics are part of the design</h2>
      <p>A foreign key without an explicit action is a latent incident. The schema states the rule for every edge. Identity records cascade because they have no independent meaning. History-bearing records restrict because deleting a policy or a resource would break the explanation of a past decision. Session links in the audit log are nulled because evidence must survive the session.</p>

      {cascades}

      <h2>The audit chain</h2>
      <p><code>audit_events</code> is the one table the application can only append to. The row carries a gap-free <code>seq</code>, the previous event's hash, and a payload hash. The verifier walks the chain from the genesis event and stops at the first mismatch. A deletion is detectable because sequence numbers skip; an edit is detectable because the next event's <code>prev_hash</code> no longer matches.</p>
      {code_block('''
-- The application role may append, but never rewrite.
GRANT INSERT ON audit_events TO zg_app;
GRANT SELECT ON audit_events TO zg_auditor;
REVOKE UPDATE, DELETE ON audit_events FROM zg_app;

-- The chain is serialised by the insert order.
CREATE UNIQUE INDEX uq_audit_seq ON audit_events (seq);
''', "language-sql")}
      <p>Events are partitioned monthly and retained for one year. An export takes a consistent snapshot, verifies the chain before writing, and emits JSONL with the sequence number and both hashes. The verifier is a separate binary with a read-only role, so a compromised application cannot certify its own tampering.</p>

      {index_table}

      <h2>Why the same table appears twice</h2>
      <p>The identity figure and the access figure are two views of one database. <code>users</code> is shown in both because it is the join point: identity reads it for login and device ownership, access reads it for request and session ownership. In a real deployment it is one table with one set of grants. The split is a reading device, not a second copy.</p>

      {callout(
        "Beyond these slices",
        "<p>The certificate ledger, the vault payload store, and the policy-version history are separate stores with different encryption and retention rules. They are described in the SSH, JIT, and API pages. The access-control schema on this page never holds a private key, a vault plaintext, or a certificate blob.</p>"
      )}

      {link_row([
        ("Logical data model &rarr;", "data-model.html"),
        ("SSH certificate flow &rarr;", "flow-ssh-certificate.html"),
        ("API contract &rarr;", "api.html"),
        ("Requirements &rarr;", "requirements.html"),
      ])}
    </div>
  </div>
  {page_nav("database-schema")}
</div>
"""
    return shell(
        title="Database schema &middot; ZeroGate",
        description=PAGE_BY_SLUG["database-schema"]["desc"],
        current="system",
        body=body,
    )

# ---------------------------------------------------------------------------
# 05 Passkey login
# ---------------------------------------------------------------------------

def build_passkey() -> str:
    svg = figure(
        diagrams_flows.sequence_passkey(),
        "05",
        "Passkey login",
        "<b>A login is two ceremonies and a decision.</b> The authenticator signs a challenge; the portal verifies the assertion, origin, RP ID, user-verification flag, and counter; the Policy Engine scores the context; and only then is a session cookie minted. The audit append is asynchronous and never blocks the redirect.",
        "fig05",
    )

    steps = table(
        ["#", "From &rarr; to", "Message", "What happens"],
        [
            ["01", "User &rarr; Portal", "GET /login", "The portal starts a fresh ceremony and creates a single-use challenge."],
            ["02", "Portal &rarr; User", "Challenge + options", "The browser receives <code>PublicKeyCredentialRequestOptions</code> with the RP ID and an allow-list."],
            ["03", "User &rarr; Portal", "Signed assertion", "The authenticator verifies the user locally, signs the challenge, and returns the credential id and authenticator data."],
            ["04", "Portal &rarr; Policy", "POST /v1/authorize", "The portal attaches the verified subject, device context, resource, action, and request context."],
            ["05", "Policy &rarr; Risk", "Score identity", "Hard gates run first; then the rule score and bounded ML adjustment."],
            ["06", "Risk &rarr; Policy", "92 &middot; reasons", "The score, band, and top reason codes return to the engine."],
            ["07", "Policy &rarr; Portal", "ALLOW + session", "The decision includes obligations, a session grant, and an audit id."],
            ["08", "Portal &rarr; User", "Cookie + redirect", "The portal sets an HttpOnly, Secure, SameSite=Lax cookie and redirects to the requested app."],
            ["09", "Portal &rarr; Audit", "Append login", "The audit event is appended asynchronously; the redirect does not wait for the chain."],
        ],
        cls="step-table",
        caption="Table 1 &mdash; The nine messages in the figure.",
    )

    checks = table(
        ["Check", "Why it matters", "Failure"],
        [
            ["Challenge freshness", "A replayed assertion must not create a second session.", "400 <code>CHALLENGE_EXPIRED</code>"],
            ["Origin and RP ID", "A phishing site must not be able to relay the ceremony.", "401 <code>ORIGIN_MISMATCH</code>"],
            ["User-verification flag", "The policy may require a fingerprint or face check, not just possession.", "403 <code>UV_REQUIRED</code>"],
            ["Signature counter", "A cloned authenticator or replayed assertion shows a non-increasing counter.", "403 <code>PASSKEY_COUNTER_REGRESSION</code>"],
            ["User handle", "The credential must belong to the claimed user.", "401 <code>UNKNOWN_CREDENTIAL</code>"],
            ["Device status", "A revoked or unenrolled device is a hard gate, not a score deduction.", "403 <code>DEVICE_REVOKED</code>"],
        ],
        cls="compact",
        caption="Table 2 &mdash; Server-side verification. The first five are WebAuthn checks; the last is a ZeroGate gate.",
    )

    cookie = table(
        ["Attribute", "Value", "Reason"],
        [
            ["<code>HttpOnly</code>", "true", "JavaScript cannot read the session token."],
            ["<code>Secure</code>", "true", "The cookie is only sent over TLS."],
            ["<code>SameSite</code>", "Lax", "Top-level navigation works; cross-site POSTs do not carry the cookie."],
            ["<code>Path</code>", "/", "The portal and proxied apps share the session."],
            ["<code>Max-Age</code>", "8 hours absolute", "A hard ceiling independent of activity."],
            ["Idle timeout", "15 minutes", "Server-side check; the cookie alone is not enough."],
        ],
        cls="compact",
        caption="Table 3 &mdash; The browser session cookie. The server-side session is the source of truth.",
    )

    body = f"""
<div class="wrap">
  <div class="page">
    {page_head(
        "05", "FLOWS / IDENTITY",
        "A login that never<br>sends a secret.",
        "The employee touches the authenticator, the authenticator signs a challenge, and the server verifies a public-key signature. The fingerprint never leaves the key. The login is still a policy decision: identity is necessary, but posture and context decide whether this is a normal Tuesday or an approval conversation.",
        chips(("FIG.", "05"), ("5", "lifelines"), ("9", "messages"), ("P95", "&le; 3 s"))
    )}
    {svg}

    <div class="prose">
      <h2>What the ceremony proves</h2>
      <p>A WebAuthn assertion proves three things at once: the private key is present, the user verified locally, and the signature covers the server's challenge and origin. It does not prove that the device is healthy, that the user is in the office, or that the request is sensible. Those are the Policy Engine's job. The sequence keeps the two claims separate so a valid signature is never mistaken for a valid session.</p>
      <p>The portal verifies the assertion before it calls the engine. A failed ceremony never reaches the risk scorer. That ordering matters for both security and latency: malformed or replayed assertions are cheap to reject, and the expensive decision path only sees cryptographic material that already passed.</p>

      {steps}

      <h2>The checks that are easy to skip</h2>
      <p>The signature is the headline, but most real failures are in the details around it. The challenge must be single-use and short-lived. The origin must match the RP ID exactly. The user-verification flag must satisfy the policy, not just the browser's preference. The counter must increase. The credential must belong to the claimed user, and the device must still be enrolled.</p>

      {checks}

      <div class="cards two">
        <div class="card">
          <div class="card-label">Privacy</div>
          <h3>The server never sees a fingerprint</h3>
          <p>The biometric match happens inside the authenticator. The server receives a signature over the challenge and a public key it already stored. There is no biometric template in the database, no fingerprint image in the audit log, and no shared secret to phish.</p>
        </div>
        <div class="card">
          <div class="card-label">Recovery</div>
          <h3>Losing a key is not losing the account</h3>
          <p>Recovery is a separate ceremony with its own policy, rate limits, and audit trail. A Shamir rebuild lowers the next score by 12 points for 24 hours. The login path never quietly falls back to a password.</p>
        </div>
      </div>

      <h2>Where the score enters</h2>
      <p>After verification, the portal calls <code>POST /v1/authorize</code> with the subject, device, resource, action, and context. The engine runs the hard gates, scores the request, checks policy, and maps the result to a band. In the figure the result is 92 and <strong>ALLOW</strong>: a valid passkey on a compliant known device, on the office network, during working hours. The session is created with a 30-minute TTL and an audit obligation.</p>
      <p>A different context changes the answer without changing the ceremony. A fresh credential, a new ASN, and an off-hours request can land in the approval band; a counter regression is a hard deny regardless of the arithmetic. The login page explains the difference in plain language: the passkey proved who you are, and the engine decided what this request may do.</p>

      {cookie}

      {callout(
        "NIST 800-63B alignment",
        "<p>The ceremony uses a phishing-resistant authenticator with user verification, a server-generated challenge, origin binding, and a signature counter. Recovery is treated as a separate authenticator lifecycle event, not as a password reset. The design does not claim FIDO certification.</p>"
      )}

      {link_row([
        ("Session state &rarr;", "state-session.html"),
        ("Policy Engine &rarr;", "policy-engine.html"),
        ("Requirements &rarr;", "requirements.html"),
        ("Auth API &rarr;", "api.html#tag-auth"),
      ])}
    </div>
  </div>
  {page_nav("flow-passkey")}
</div>
"""
    return shell(
        title="Passkey login &middot; ZeroGate",
        description=PAGE_BY_SLUG["flow-passkey"]["desc"],
        current="flows",
        body=body,
    )


# ---------------------------------------------------------------------------
# 06 SSH certificate
# ---------------------------------------------------------------------------

def build_ssh() -> str:
    svg = figure(
        diagrams_flows.sequence_ssh(),
        "06",
        "SSH certificate issuance",
        "<b>No static key, no permanent trust.</b> The helper asks the CA for a certificate for one resource. The CA asks the Policy Engine; the engine scores the session context; the CA signs a certificate valid for about 30 minutes and bound to the principal, host, and source address. The Linux server trusts only the CA and verifies the certificate before opening the session.",
        "fig06",
    )

    steps = table(
        ["#", "From &rarr; to", "Message", "What happens"],
        [
            ["01", "Helper &rarr; CA", "CSR + resource", "The helper generates an ephemeral key pair and sends the public key with the target resource id."],
            ["02", "CA &rarr; Policy", "Authorize SSH", "The CA authenticates the user and device, then calls the same decision endpoint as the web path."],
            ["03", "Policy &rarr; Risk", "Score session", "The engine evaluates identity, device, network, behaviour, and session context."],
            ["04", "Risk &rarr; Policy", "84 &middot; OK", "The score and reasons return; hard gates have already run."],
            ["05", "Policy &rarr; CA", "ALLOW &middot; TTL 30m", "The decision carries the permitted principal, host, TTL, and audit id."],
            ["06", "CA &rarr; CA", "Sign &middot; 30m", "The CA signs the certificate with the permitted critical options and extensions."],
            ["07", "CA &rarr; Helper", "Signed cert &middot; 30m", "The certificate blob and metadata return to the helper."],
            ["08", "Helper &rarr; Server", "SSH + certificate", "The helper invokes the system SSH client with the certificate and ephemeral key."],
            ["09", "Server &rarr; Server", "Verify CA", "The server checks the CA signature, validity window, principal, source address, and revocation state."],
            ["10", "Server &rarr; Helper", "Session open", "The shell opens. The certificate expires on its own; nothing permanent is left behind."],
        ],
        cls="step-table",
        caption="Table 1 &mdash; The ten messages in the figure.",
    )

    fields = table(
        ["Certificate field", "Value in ZeroGate", "Why"],
        [
            ["Key id", "<code>zg:&lt;user&gt;:&lt;session&gt;</code>", "Joins the certificate to a user and a session without putting a secret in the key id."],
            ["Principals", "One Unix principal", "The certificate works for one account, not a shared role."],
            ["Valid after / before", "Now / now + 30 min", "Short enough that a stolen certificate becomes useless quickly."],
            ["Critical options", "<code>source-address</code>, <code>force-command</code> where required", "Binds the certificate to the source address and, for privileged targets, a command."],
            ["Extensions", "<code>permit-pty</code> only when policy allows", "No port forwarding or agent forwarding by default."],
            ["Serial", "Monotonic integer", "Revocation and replay detection."],
            ["Signature", "CA private key in HSM/KMS", "The CA key never leaves the boundary."],
        ],
        cls="compact",
        caption="Table 2 &mdash; What the CA puts inside the certificate.",
    )

    failures = table(
        ["Condition", "Result", "Reason code"],
        [
            ["Policy denies the request", "No certificate", "<code>POLICY_DENY</code>"],
            ["Score below 40", "No certificate", "<code>SCORE_BELOW_KILL</code>"],
            ["CA cannot reach the engine", "No certificate", "<code>POLICY_UNAVAILABLE</code>"],
            ["Certificate expired", "Server rejects", "<code>CERT_EXPIRED</code>"],
            ["Wrong source address", "Server rejects", "<code>CERT_SOURCE_MISMATCH</code>"],
            ["Certificate replayed on a second connection", "Server rejects; hard gate", "<code>CERT_REPLAY</code>"],
            ["Host key mismatch", "Helper aborts", "<code>HOST_KEY_MISMATCH</code>"],
        ],
        cls="compact",
        caption="Table 3 &mdash; Failure paths. The first three happen before signing; the rest happen at the host.",
    )

    body = f"""
<div class="wrap">
  <div class="page">
    {page_head(
        "06", "FLOWS / SSH",
        "Thirty minutes,<br>one host, no static key.",
        "The SSH path replaces long-lived keys with a short-lived certificate that is bound to one principal, one host, and one source address. The CA signs only after the Policy Engine allows. The server trusts only the CA. A stolen certificate expires on its own; a stolen laptop holds no permanent key.",
        chips(("FIG.", "06"), ("5", "lifelines"), ("10", "messages"), ("TTL", "30 minutes"))
    )}
    {svg}

    <div class="prose">
      <h2>The shape of the exchange</h2>
      <p>The helper is deliberately boring. It generates an ephemeral key pair, asks the CA for a certificate, and then hands the certificate to the system SSH client. It does not store the private key, edit <code>authorized_keys</code>, or keep a fallback key. If issuance fails, the connection fails with a reason code the user can act on.</p>
      <p>The CA is the second enforcement point. It authenticates the user and device, resolves the target resource, and calls <code>POST /v1/authorize</code> with action <code>ssh</code>. The engine returns an allow with a TTL and obligations. The CA signs only what the decision permits: one principal, one host, one source address, and a validity window of about 30 minutes.</p>

      {steps}

      <h2>What is inside the certificate</h2>
      <p>An OpenSSH certificate is a signed statement about a public key. The interesting design work is in the fields: the key id makes the certificate traceable, the principals limit it to one account, the validity window limits its life, the critical options bind it to a source address, and the extensions keep the session narrow. The CA key stays in an HSM or equivalent; the signing operation is the only thing that touches it.</p>

      {fields}

      <div class="cards two">
        <div class="card">
          <div class="card-label">Why short-lived</div>
          <h3>Expiry is the default revocation</h3>
          <p>A certificate that lives for 30 minutes needs no long-lived revocation list to be safe. The CA still publishes a revocation list every 60 seconds for the cases that need immediate action, but the common case is simply time.</p>
        </div>
        <div class="card">
          <div class="card-label">Why bind the source</div>
          <h3>A copied blob is not a copied session</h3>
          <p>The <code>source-address</code> critical option ties the certificate to the address that requested it. A replay from another network fails at the host even before the revocation list is consulted.</p>
        </div>
      </div>

      <h2>Failure paths</h2>
      <p>The happy path is only half the design. The helper must distinguish &ldquo;the policy said no&rdquo; from &ldquo;the CA is down&rdquo; from &ldquo;the host rejected the certificate&rdquo;, because the user's next action is different in each case. The API returns a stable reason code and a correlation id; the helper prints both.</p>

      {failures}

      {callout(
        "Single Packet Auth is a stretch goal",
        "<p>The main path keeps the SSH port reachable for the lab. The stretch goal adds a signed single packet that opens the port for one source address for a few seconds. It is deliberately not part of the core sequence: the certificate path must work without it.</p>"
      )}

      <h2>What the host checks</h2>
      <p>The host is configured to trust the ZeroGate CA, not a file of employee keys. On connection it verifies the CA signature, the validity window, the principal, the source address, and the revocation state. It does not call the Policy Engine. That is the point of the certificate: the decision happened at issuance, and the artifact carries the constraints.</p>
      <p>When the session is killed, the Policy Administrator revokes the certificate and the CA publishes the revocation within 60 seconds. The short lifetime bounds the residual risk if the publication is delayed. The audit chain records the issuance, the host, the principal, the serial, and the revocation.</p>

      {link_row([
        ("Policy Engine &rarr;", "policy-engine.html"),
        ("Mid-session kill &rarr;", "flow-session-kill.html"),
        ("SSH API &rarr;", "api.html#tag-ssh"),
        ("Requirements &rarr;", "requirements.html"),
      ])}
    </div>
  </div>
  {page_nav("flow-ssh-certificate")}
</div>
"""
    return shell(
        title="SSH certificate issuance &middot; ZeroGate",
        description=PAGE_BY_SLUG["flow-ssh-certificate"]["desc"],
        current="flows",
        body=body,
    )


# ---------------------------------------------------------------------------
# 07 JIT approval
# ---------------------------------------------------------------------------

def build_jit() -> str:
    svg = figure(
        diagrams_flows.sequence_jit(),
        "07",
        "Just-in-time approval",
        "<b>The approval band is a question, not a refusal.</b> The portal submits the request; the Policy Engine returns <code>APPROVAL_REQUIRED</code> with a score of 58; the queue notifies an approver within a 15-minute SLA; the approver grants a reason; the engine resolves the grant; the portal delivers a 30-minute single-use window. The audit append is asynchronous.",
        "fig07",
    )

    steps = table(
        ["#", "From &rarr; to", "Message", "What happens"],
        [
            ["01", "Employee &rarr; Portal", "POST /v1/jit/requests", "The requester supplies the resource, action, justification, and requested TTL."],
            ["02", "Portal &rarr; Policy", "Evaluate JIT", "The engine scores the request and applies the approval policy."],
            ["03", "Policy &rarr; Portal", "Approval required &middot; 58", "The decision includes the band, top reasons, and a 15-minute SLA."],
            ["04", "Portal &rarr; Approver", "Notify queue", "The approver sees the request, the score, the reasons, and the device posture."],
            ["05", "Approver &rarr; Portal", "Approve &middot; reason", "The approver records a reason and a grant TTL, capped by policy at 30 minutes."],
            ["06", "Portal &rarr; Policy", "Resolve approval", "The engine checks that the request is still pending within the 15-minute SLA, the approver is eligible, and policy still allows."],
            ["07", "Policy &rarr; Portal", "Allow + grant", "The grant is single-use and expires at the earlier of the TTL and the policy ceiling."],
            ["08", "Portal &rarr; Employee", "Access granted &middot; 30m", "The requester gets a session or a certificate, not a permanent entitlement."],
            ["09", "Portal &rarr; Audit", "Append request", "The full lifecycle is appended: request, decision, approval, grant, consumption."],
        ],
        cls="step-table",
        caption="Table 1 &mdash; The nine messages in the figure.",
    )

    rules = table(
        ["Rule", "Enforcement", "Why"],
        [
            ["Requester cannot approve their own request", "Policy Engine + API guard", "Four-eyes control; self-approval is a conflict of interest."],
            ["Approval SLA is 15 minutes", "Queue expiry", "The request cannot sit forever waiting for a human."],
            ["Grant is at most 30 minutes", "TTL clamp", "The approval is for a task, not a standing role."],
            ["Grant is single-use", "Consumption guard", "A consumed grant cannot open a second session."],
            ["Expired request cannot be approved", "State guard", "The approver's action must be meaningful."],
            ["Policy is re-checked at approval", "Resolve step", "A policy published during the wait still applies."],
            ["Every transition is audited", "Audit obligation", "The queue is evidence, not just workflow."],
        ],
        cls="compact",
        caption="Table 2 &mdash; The JIT rules that are enforced outside the UI.",
    )

    transitions = table(
        ["From", "Event", "Guard", "To"],
        [
            ["&mdash;", "Create", "Requester is authenticated", "<code>REQUESTED</code>"],
            ["<code>REQUESTED</code>", "Submit", "Resource exists; score in approval band", "<code>PENDING</code>"],
            ["<code>PENDING</code>", "Approve", "Approver is not requester; not expired", "<code>APPROVED</code>"],
            ["<code>PENDING</code>", "Deny", "Reason supplied", "<code>DENIED</code>"],
            ["<code>PENDING</code>", "SLA elapsed", "15-minute timer", "<code>EXPIRED</code>"],
            ["<code>APPROVED</code>", "Open session", "Grant unused; not expired", "<code>CONSUMED</code>"],
            ["<code>APPROVED</code>", "Grant expires", "30-minute ceiling", "<code>EXPIRED</code>"],
        ],
        cls="compact",
        caption="Table 3 &mdash; The happy path and the exits. The full machine is on the JIT state page.",
    )

    body = f"""
<div class="wrap">
  <div class="page">
    {page_head(
        "07", "FLOWS / APPROVAL",
        "When the score is<br>a question, not a no.",
        "A request in the 40&ndash;59 band is not denied; it is suspended and sent to a human. The approver sees the score, the reasons, the device posture, and the requested resource. A grant is single-use, time-boxed, and re-checked against policy before it is issued.",
        chips(("FIG.", "07"), ("5", "lifelines"), ("9", "messages"), ("SLA", "15 minutes"))
    )}
    {svg}

    <div class="prose">
      <h2>Why a human in the loop</h2>
      <p>The approval band exists because some context is genuinely ambiguous. A contractor asking for a production wiki at 21:30 from a new ASN is not obviously an attacker, and it is not obviously safe. A score in the 50s is the system saying &ldquo;I have reasons to hesitate.&rdquo; A human with the context can resolve the ambiguity faster and more accurately than a threshold can.</p>
      <p>The important design choice is that the human does not get a blank check. The approval is bounded by the requested TTL, capped by policy, single-use, and re-checked at resolution. The approver grants a task window, not a role. The engine still owns the decision; the human supplies one missing input.</p>

      {steps}

      <h2>The rules behind the queue</h2>
      <p>Every rule in the table below is enforced server-side. The UI mirrors them, but the UI is not the control. A request that expires while the approver is reading it cannot be approved. A request whose policy changed during the wait is re-evaluated. A grant that was already consumed cannot be replayed.</p>

      {rules}

      {transitions}

      <div class="cards two">
        <div class="card">
          <div class="card-label">What the approver sees</div>
          <h3>Enough context to say yes or no</h3>
          <ul class="rule-list">
            <li>Requester, team, and role.</li>
            <li>Resource, sensitivity, and requested action.</li>
            <li>Trust score, band, and the top three reason codes.</li>
            <li>Device posture and the last posture change.</li>
            <li>Requested TTL and the policy ceiling.</li>
            <li>Prior access to the same resource, if any.</li>
          </ul>
        </div>
        <div class="card">
          <div class="card-label">What the approver does not get</div>
          <h3>No silent expansion</h3>
          <ul class="rule-list">
            <li>No ability to approve their own request.</li>
            <li>No ability to exceed the policy TTL ceiling.</li>
            <li>No ability to grant a different resource.</li>
            <li>No ability to reuse a consumed grant.</li>
            <li>No ability to suppress the audit event.</li>
          </ul>
        </div>
      </div>

      <h2>Failure and edge cases</h2>
      <ul>
        <li><strong>Two approvers race:</strong> the first decision wins; the second receives <code>409 CONFLICT</code> and the current state.</li>
        <li><strong>Approver is the requester:</strong> the API rejects with <code>403 SELF_APPROVAL</code>, even if the UI is bypassed.</li>
        <li><strong>Request expires during approval:</strong> the resolution step fails closed and the request moves to <code>EXPIRED</code>.</li>
        <li><strong>Policy changes during the wait:</strong> the engine re-evaluates at resolution; a new deny wins.</li>
        <li><strong>Grant is never consumed:</strong> it expires after 30 minutes; a sweeper records the expiry.</li>
        <li><strong>Audit append fails:</strong> the grant is not issued; the request remains pending with an error state.</li>
      </ul>

      {callout(
        "Priority note",
        "<p>JIT is an add-on in the project scope. The core system must work without it: an approval-band request can be denied by policy when the queue is not deployed. The design keeps the state machine and API ready so the add-on does not change the decision contract.</p>"
      )}

      {link_row([
        ("JIT state machine &rarr;", "state-jit.html"),
        ("JIT API &rarr;", "api.html#tag-jit"),
        ("Requirements &rarr;", "requirements.html"),
        ("Risk report &rarr;", "risk-scoring.html"),
      ])}
    </div>
  </div>
  {page_nav("flow-jit-approval")}
</div>
"""
    return shell(
        title="Just-in-time approval &middot; ZeroGate",
        description=PAGE_BY_SLUG["flow-jit-approval"]["desc"],
        current="flows",
        body=body,
    )


# ---------------------------------------------------------------------------
# 08 Mid-session kill
# ---------------------------------------------------------------------------

def build_kill() -> str:
    svg = figure(
        diagrams_flows.sequence_kill(),
        "08",
        "Mid-session kill",
        "<b>Access is not a lease signed at login.</b> The posture agent reports that disk encryption was turned off. The risk scorer recomputes 34. The Policy Engine re-evaluates and issues a kill below the 40 threshold. The Policy Administrator closes the proxy session, revokes the certificate, notifies the user, and appends the kill to the audit chain.",
        "fig08",
    )

    steps = table(
        ["#", "From &rarr; to", "Message", "What happens"],
        [
            ["01", "Device &rarr; Risk", "Posture &middot; disk off", "The posture agent reports a change; this is a scoring event, not a new login."],
            ["02", "Risk &rarr; Risk", "Recompute &middot; 34", "The rule score drops from 89 to 34; the ML adjustment is zero."],
            ["03", "Risk &rarr; Policy", "Trust drop &middot; 34", "The new score crosses the kill threshold."],
            ["04", "Policy &rarr; Policy", "Re-evaluate", "Hard gates run again; policy is checked against the live session."],
            ["05", "Policy &rarr; Admin", "Kill &middot; score &lt; 40", "The decision is <code>KILL_SESSION</code> with termination and revocation obligations."],
            ["06", "Admin &rarr; Admin", "Close at proxy", "The proxy session is closed and the one-second decision cache is invalidated."],
            ["07", "Admin &rarr; Device", "Session terminated", "The user is notified; the UI explains the reason and the correlation id."],
            ["08", "Admin &rarr; Audit", "Append kill", "The decision, the obligations, and the revocation are recorded."],
        ],
        cls="step-table",
        caption="Table 1 &mdash; The eight messages in the figure.",
    )

    triggers = table(
        ["Trigger", "Threshold", "Action", "Who can initiate"],
        [
            ["Score falls below kill threshold", "&lt; 40", "Kill and revoke", "Risk scorer event"],
            ["Administrator kill", "Immediate", "Kill and revoke", "Admin console"],
            ["Policy published that denies the session", "Immediate", "Kill", "Policy Engine"],
            ["Device revoked", "Immediate", "Kill and revoke", "Admin or device registry"],
            ["SSH certificate replay", "Immediate", "Kill and revoke", "CA / host"],
            ["Two missed heartbeats", "&minus;10 points", "Re-score; kill if below 40", "Policy Administrator"],
        ],
        cls="compact",
        caption="Table 2 &mdash; What can end a live session.",
    )

    semantics = table(
        ["Obligation", "What it means", "Target"],
        [
            ["<code>terminate_session</code>", "Close the proxy session and invalidate the cache.", "p95 &le; 2 s"],
            ["<code>revoke_ssh_certificate</code>", "Add the serial to the revocation list and publish.", "p95 &le; 2 s; list every 60 s"],
            ["<code>notify_user</code>", "Show the reason and correlation id in the portal.", "Immediate"],
            ["<code>notify_admin</code>", "Alert the security channel with the score and reasons.", "Immediate"],
            ["<code>append_audit</code>", "Record the decision and every obligation result.", "Before the API returns"],
        ],
        cls="compact",
        caption="Table 3 &mdash; The kill obligations. Each one is idempotent.",
    )

    body = f"""
<div class="wrap">
  <div class="page">
    {page_head(
        "08", "FLOWS / TERMINATION",
        "How access ends<br>in under two seconds.",
        "The score is recomputed on a 60-second heartbeat and on any posture, policy, device, or anomaly event. When it falls below 40, the Policy Administrator closes the proxy session and revokes the SSH certificate. A repeated kill returns the existing result. The audit record is written even if the user has already gone.",
        chips(("FIG.", "08"), ("5", "lifelines"), ("8", "messages"), ("P95", "&le; 2 s"))
    )}
    {svg}

    <div class="prose">
      <h2>The arithmetic in the figure</h2>
      <p>The session started at 89. Disk encryption is turned off (&minus;25), transfer volume reaches 15&times; the user's baseline (&minus;20), and two heartbeats are missed (&minus;10). The score is <code>89 &minus; 25 &minus; 20 &minus; 10 = 34</code>. The band is <strong>DENY / KILL</strong>. No human is asked; the threshold is explicit and the evidence is recorded.</p>
      <p>The example is deliberately simple. The point is not the exact weights; it is that every point is attributable to a named signal, the category caps prevent one category from dominating, and a hard gate would have stopped the session before the arithmetic. The risk report contains the full catalog and the worked examples.</p>

      {steps}

      <h2>What kill actually does</h2>
      <p>Killing is not a database flag. It is a set of obligations carried out across the proxy, the SSH CA, the notification channel, and the audit chain. The Policy Administrator is responsible for all of them. The API is idempotent: a second kill with the same idempotency key returns the same result and <code>already_killed: true</code>.</p>

      {triggers}

      <div class="cards two">
        <div class="card">
          <div class="card-label">The race</div>
          <h3>In-flight requests</h3>
          <p>The proxy keeps a session decision cache with a TTL of at most one second. A kill invalidates the entry before the next request is admitted. A request already in flight may finish; it cannot start a new one. The residual window is bounded and measured.</p>
        </div>
        <div class="card">
          <div class="card-label">The residue</div>
          <h3>Certificates and caches</h3>
          <p>The certificate revocation list is published every 60 seconds. Short certificate lifetimes bound the gap. The proxy cache is invalidated immediately. The portal session is marked killed; the cookie alone cannot revive it.</p>
        </div>
      </div>

      {semantics}

      <h2>What the user sees</h2>
      <p>The portal shows a plain-language explanation: the session ended because device encryption was disabled, the score fell below the threshold, and the correlation id is <code>req_9b3e2a</code>. The admin alert includes the same id and the top three reasons. The audit event includes the full signal list, the policy version, the model version, and the input hash.</p>

      {callout(
        "Kill is terminal",
        "<p>A killed session cannot be resumed by re-authenticating into the same session. The user may start a new request, which is scored from scratch. The old session remains in the audit chain as <code>KILLED</code>; it is never deleted or overwritten.</p>"
      )}

      <h2>Failure modes</h2>
      <ul>
        <li><strong>CA unreachable:</strong> the kill still closes the proxy session; the revocation is retried and the alert says the certificate is pending revocation.</li>
        <li><strong>Audit unavailable:</strong> the kill is not reported as complete until the event is appended; the API returns a retryable error.</li>
        <li><strong>Duplicate kill:</strong> idempotent; the second call returns the first result.</li>
        <li><strong>Heartbeat in flight:</strong> the kill decision wins; a late heartbeat cannot move the session out of <code>KILLED</code>.</li>
        <li><strong>Notification failure:</strong> the session still ends; the notification is retried and the failure is audited.</li>
      </ul>

      {link_row([
        ("Session state &rarr;", "state-session.html"),
        ("Risk report &rarr;", "risk-scoring.html"),
        ("Kill API &rarr;", "api.html#tag-sessions"),
        ("Policy Engine &rarr;", "policy-engine.html"),
      ])}
    </div>
  </div>
  {page_nav("flow-session-kill")}
</div>
"""
    return shell(
        title="Mid-session kill &middot; ZeroGate",
        description=PAGE_BY_SLUG["flow-session-kill"]["desc"],
        current="flows",
        body=body,
    )


# ---------------------------------------------------------------------------
# 09 Policy Engine
# ---------------------------------------------------------------------------

def build_policy() -> str:
    svg = figure(
        diagrams_flows.activity_policy(),
        "09",
        "Policy Engine decision logic",
        "<b>The order is the safety property.</b> A request enters, hard gates run, the request is scored, policy is applied, and the trust band selects the action. A failed hard gate goes straight to deny; a policy deny goes straight to deny; the 40&ndash;79 range splits into step-up and approval. No arithmetic can turn a gate failure into an allow.",
        "fig09",
    )

    gates = table(
        ["Gate", "Code", "Effect"],
        [
            ["Invalid or unknown passkey", "<code>PASSKEY_INVALID</code>", "Deny"],
            ["Signature-counter regression", "<code>PASSKEY_COUNTER_REGRESSION</code>", "Deny, revoke credential, alert"],
            ["Device revoked or not enrolled", "<code>DEVICE_REVOKED</code> / <code>DEVICE_NOT_ENROLLED</code>", "Deny"],
            ["Resource not in the catalog", "<code>RESOURCE_NOT_IN_CATALOG</code>", "Deny"],
            ["Explicit policy deny", "<code>POLICY_DENY</code>", "Deny"],
            ["Session already killed", "<code>SESSION_ALREADY_KILLED</code>", "Return the existing kill result"],
            ["Administrator kill", "<code>ADMIN_KILL</code>", "Kill immediately"],
            ["Score below kill threshold", "<code>SCORE_BELOW_KILL</code>", "Kill immediately"],
        ],
        cls="compact",
        caption="Table 1 &mdash; Hard gates. They run before the score and cannot be outvoted.",
    )

    bands = table(
        ["Band", "Score", "Decision", "Default action"],
        [
            ["<strong>ALLOW</strong>", "80&ndash;100", "<code>ALLOW</code>", "Create the session, attach obligations, audit."],
            ["<strong>STEP-UP</strong>", "60&ndash;79", "<code>STEP_UP_REQUIRED</code>", "Re-authenticate within five minutes; re-score on success."],
            ["<strong>APPROVAL</strong>", "40&ndash;59", "<code>APPROVAL_REQUIRED</code>", "Suspend, open a JIT request, 15-minute approval SLA."],
            ["<strong>DENY / KILL</strong>", "0&ndash;39", "<code>DENY</code> / <code>KILL_SESSION</code>", "No new session; terminate a live session and revoke credentials."],
        ],
        cls="compact",
        caption="Table 2 &mdash; The four trust bands. The band is derived; it is never an input.",
    )

    obligations = table(
        ["Obligation", "Parameters", "Carried out by"],
        [
            ["<code>limit_ttl</code>", "Seconds; at most the policy ceiling.", "Policy Administrator / portal"],
            ["<code>reauth_within</code>", "Seconds; default 300.", "Portal"],
            ["<code>require_approval</code>", "SLA seconds; default 900.", "JIT queue"],
            ["<code>terminate_session</code>", "Session id.", "Policy Administrator"],
            ["<code>revoke_ssh_certificate</code>", "Certificate id or serial.", "SSH CA"],
            ["<code>notify_admin</code>", "Channel and severity.", "Notification service"],
            ["<code>append_audit</code>", "Event type and payload hash.", "Audit chain"],
        ],
        cls="compact",
        caption="Table 3 &mdash; Obligations returned with a decision. The engine does not perform them.",
    )

    pseudocode = """function authorize(request):
    context = load(request.subject, request.device, request.resource)

    for gate in HARD_GATES:
        if gate.fails(context):
            return deny(gate, audit=True)

    score = risk.evaluate(context)           # rules + bounded ML
    policy = policies.match(context)         # pinned version
    if policy.effect == "deny":
        return deny("POLICY_DENY", score, audit=True)

    band = band_for(score)                   # 80 / 60 / 40 / 0
    decision = action_for(band, policy)
    return decision_with(score, reasons, obligations, audit_id)"""

    body = f"""
<div class="wrap">
  <div class="page">
    {page_head(
        "09", "DECISION / ENGINE",
        "Hard gates first,<br>arithmetic second.",
        "The engine runs a fixed sequence: hard gates, score, policy, band. The order is not an implementation detail; it is the reason a stolen credential cannot be rescued by a high score. Every branch returns the same explanation shape, and every answer carries an audit id.",
        chips(("FIG.", "09"), ("8", "hard gates"), ("4", "bands"), ("P95", "&le; 80 ms"))
    )}
    {svg}

    <div class="prose">
      <h2>The algorithm</h2>
      <p>The engine is a pure function of context, policy version, and model version. It does not open sockets, revoke certificates, or write sessions. It returns a decision with obligations, and the Policy Administrator carries them out. That separation makes the decision reproducible and the action retryable.</p>
      {code_block(pseudocode, "language-text")}
      <p>The pseudocode is deliberately small. The complexity lives in the gate predicates, the signal catalog, and the policy matcher, not in a branching maze. A reviewer should be able to read the top-level order and know that a hard gate cannot be outvoted.</p>

      {gates}

      <h2>Why hard gates run first</h2>
      <p>A hard gate is a fact that makes the request invalid regardless of context. A revoked device is not a little bit risky; it is not eligible. An unknown resource is not a policy miss; it is not in the catalog. A counter regression is not a deduction; it is evidence of a cloned authenticator. Running the gates first means the score only ever ranks requests that are eligible to be ranked.</p>
      <p>The same rule applies to an explicit policy deny. If the published policy says no, a score of 99 does not matter. The engine returns <code>POLICY_DENY</code> with the policy id and version, and the UI explains which rule matched. A deny is a decision, not an error.</p>

      {bands}

      <h2>From band to action</h2>
      <p>The band is a small state machine on top of the score. <strong>ALLOW</strong> creates a session with obligations. <strong>STEP-UP</strong> creates a challenge, not a session; the user re-authenticates within five minutes and the request is scored again. <strong>APPROVAL</strong> creates a JIT request and suspends the decision until a human resolves it. <strong>DENY / KILL</strong> creates no session and terminates any live one.</p>

      {obligations}

      <div class="cards two">
        <div class="card">
          <div class="card-label">Determinism</div>
          <h3>The same input, the same answer</h3>
          <p>The decision records the policy id, policy version, model version, and input hash. Replaying the same inputs against the same versions produces the same decision, even if the current policy has moved on. That is what makes an audit review possible.</p>
        </div>
        <div class="card">
          <div class="card-label">Failure posture</div>
          <h3>Fail closed, never open</h3>
          <p>A timeout, a missing policy, a malformed request, or an unavailable model all resolve to deny. A rules-only score is allowed when the model is down, but the decision is marked <code>MODEL_UNAVAILABLE</code> and the ML adjustment is zero.</p>
        </div>
      </div>

      <h2>What the engine does not do</h2>
      <ul>
        <li>It does not inspect packet payloads or file contents.</li>
        <li>It does not open, proxy, or terminate a connection.</li>
        <li>It does not train the ML model; it consumes a pinned version.</li>
        <li>It does not decide resource sensitivity; that is a policy input.</li>
        <li>It does not keep a long-lived authorization cache.</li>
      </ul>

      {callout(
        "NIST 800-207 &sect;3.1",
        "<p>The standard names the Policy Decision Point and the Policy Enforcement Point but leaves the trust algorithm open. This activity diagram is the project's concrete answer: named gates, a named score, a named policy step, and four named bands, all returning one explanation shape.</p>"
      )}

      {link_row([
        ("Risk scoring &rarr;", "risk-scoring.html"),
        ("Architecture &rarr;", "architecture.html"),
        ("Session state &rarr;", "state-session.html"),
        ("Authorize API &rarr;", "api.html#op-authorize"),
      ])}
    </div>
  </div>
  {page_nav("policy-engine")}
</div>
"""
    return shell(
        title="Policy Engine &middot; ZeroGate",
        description=PAGE_BY_SLUG["policy-engine"]["desc"],
        current="decision",
        body=body,
    )


# ---------------------------------------------------------------------------
# 10 Session lifecycle
# ---------------------------------------------------------------------------

def build_session_state() -> str:
    svg = figure(
        diagrams_flows.state_session(),
        "10",
        "Session lifecycle",
        "<b>Five states, two recoverable detours, two hard exits.</b> A session starts in ACTIVE. A score of 60&ndash;79 moves it to STEP-UP; a successful re-authentication returns it to ACTIVE. A score of 40&ndash;59 moves it to SUSPENDED while a JIT request waits. A score below 40, an admin kill, or a policy deny moves it to KILLED. A TTL or idle timeout moves it to EXPIRED. KILLED and EXPIRED are terminal.",
        "fig10",
    )

    states = table(
        ["State", "Meaning", "Allowed exits"],
        [
            ["<code>ACTIVE</code>", "The session is admitted and requests are flowing.", "STEP_UP, SUSPENDED, KILLED, EXPIRED"],
            ["<code>STEP_UP</code>", "The score is 60&ndash;79; the user must re-authenticate within five minutes.", "ACTIVE, KILLED, EXPIRED"],
            ["<code>SUSPENDED</code>", "The score is 40&ndash;59; a JIT request is waiting for a human.", "ACTIVE, KILLED, EXPIRED"],
            ["<code>KILLED</code>", "A hard stop: score below 40, admin kill, policy deny, or replay.", "None; terminal"],
            ["<code>EXPIRED</code>", "The TTL or idle timeout elapsed before a kill.", "None; terminal"],
        ],
        cls="compact",
        caption="Table 1 &mdash; The five session states and their exits.",
    )

    transitions = table(
        ["From", "Event", "Guard", "To", "Action"],
        [
            ["&mdash;", "Authorize", "Decision is ALLOW", "ACTIVE", "Create session, attach obligations."],
            ["ACTIVE", "Heartbeat / event", "Score 60&ndash;79", "STEP_UP", "Issue a re-auth challenge; start 5-minute timer."],
            ["STEP_UP", "Re-auth success", "Score &ge; 80", "ACTIVE", "Extend the session; record the step-up."],
            ["STEP_UP", "Timer elapses", "No re-auth", "KILLED", "Close and revoke."],
            ["ACTIVE", "Heartbeat / event", "Score 40&ndash;59", "SUSPENDED", "Open or attach a JIT request."],
            ["SUSPENDED", "Approval granted", "Grant valid", "ACTIVE", "Resume with a bounded TTL."],
            ["SUSPENDED", "Approval denied or expired", "No grant", "KILLED", "Close and revoke."],
            ["ACTIVE / STEP_UP / SUSPENDED", "Score &lt; 40", "Kill threshold", "KILLED", "Close proxy, revoke certificates."],
            ["ACTIVE / STEP_UP / SUSPENDED", "Admin kill", "Authorized admin", "KILLED", "Close proxy, revoke certificates."],
            ["ACTIVE / STEP_UP / SUSPENDED", "TTL or idle timeout", "Timer", "EXPIRED", "Close gracefully."],
        ],
        cls="compact",
        caption="Table 2 &mdash; Transitions. The recovery edges are STEP_UP &rarr; ACTIVE and SUSPENDED &rarr; ACTIVE.",
    )

    timers = table(
        ["Timer", "Default", "Applies to", "Notes"],
        [
            ["Heartbeat", "60 s", "Every live session", "Missed heartbeat is a signal, not an automatic kill."],
            ["Step-up window", "5 min", "STEP_UP", "Failure or timeout kills the session."],
            ["Approval SLA", "15 min", "SUSPENDED / JIT", "The request expires; the session does not resume."],
            ["Access session TTL", "30 min", "ACTIVE", "Bounded by policy; can be shorter."],
            ["Portal idle timeout", "15 min", "Browser session", "Separate from the access session."],
            ["Portal absolute lifetime", "8 h", "Browser session", "Hard ceiling; re-login required."],
        ],
        cls="compact",
        caption="Table 3 &mdash; Timers. The portal session and the access session are different lifetimes.",
    )

    body = f"""
<div class="wrap">
  <div class="page">
    {page_head(
        "10", "STATES / SESSION",
        "Five states,<br>two hard exits.",
        "A session is a live thing, not a token. It can be stepped up, suspended for approval, killed by the engine, or expired by time. The two recovery edges are the only ways back to ACTIVE; KILLED and EXPIRED are terminal.",
        chips(("FIG.", "10"), ("5", "states"), ("10", "transitions"), ("HEARTBEAT", "60 s"))
    )}
    {svg}

    <div class="prose">
      <h2>The states</h2>
      <p><strong>ACTIVE</strong> is the only state in which requests flow without an additional condition. <strong>STEP-UP</strong> and <strong>SUSPENDED</strong> are detours: the session still exists, but the enforcement point stops admitting new work until the condition is resolved. <strong>KILLED</strong> and <strong>EXPIRED</strong> are terminal. A killed session is an incident; an expired session is a normal end.</p>
      <p>The distinction between suspended and killed matters for the user and the audit. A suspended session can become active again if a human approves. A killed session cannot. The UI says which one happened, and the audit event records the reason.</p>

      {states}

      <h2>The transitions</h2>
      <p>The recovery edges are deliberately narrow. STEP_UP returns to ACTIVE only after a successful re-authentication that produces a score of at least 80. SUSPENDED returns to ACTIVE only after a valid, unconsumed grant. A late heartbeat cannot move a session out of KILLED; the decision is terminal.</p>

      {transitions}

      <div class="cards two">
        <div class="card">
          <div class="card-label">Kill semantics</div>
          <h3>Idempotent and terminal</h3>
          <p>A kill closes the proxy session, invalidates the cache, revokes the certificate, notifies the user, and appends the event. A second kill returns the first result with <code>already_killed: true</code>. There is no transition out of KILLED.</p>
        </div>
        <div class="card">
          <div class="card-label">Expiry semantics</div>
          <h3>Graceful, not an incident</h3>
          <p>An expired session closes at the TTL or idle timeout. It is not a security event, but it is still audited. The user can start a new request, which is scored from scratch.</p>
        </div>
      </div>

      {timers}

      <h2>Invariants</h2>
      <ol>
        <li>A session in <code>KILLED</code> or <code>EXPIRED</code> never returns to <code>ACTIVE</code>.</li>
        <li>Every transition writes an audit event with the previous and next state.</li>
        <li><code>STEP_UP</code> has a hard five-minute ceiling; a timer cannot be extended by activity.</li>
        <li><code>SUSPENDED</code> does not admit new work; the proxy returns a pending-approval response.</li>
        <li>A kill is valid even if the session record is already being updated; the database uses a conditional update on the current state.</li>
        <li>The portal session and the access session expire independently.</li>
      </ol>

      {callout(
        "Two lifetimes, one browser",
        "<p>The portal cookie has a 15-minute idle timeout and an 8-hour absolute lifetime. The access session has a 30-minute TTL, capped by policy. A user can still be logged into the portal while an access session has expired; the next request starts a new access decision.</p>"
      )}

      {link_row([
        ("Mid-session kill &rarr;", "flow-session-kill.html"),
        ("Policy Engine &rarr;", "policy-engine.html"),
        ("Session API &rarr;", "api.html#tag-sessions"),
        ("JIT state &rarr;", "state-jit.html"),
      ])}
    </div>
  </div>
  {page_nav("state-session")}
</div>
"""
    return shell(
        title="Session lifecycle &middot; ZeroGate",
        description=PAGE_BY_SLUG["state-session"]["desc"],
        current="states",
        body=body,
    )


# ---------------------------------------------------------------------------
# 11 JIT state
# ---------------------------------------------------------------------------

def build_jit_state() -> str:
    svg = figure(
        diagrams_flows.state_jit(),
        "11",
        "JIT request lifecycle",
        "<b>Submit, wait, decide, consume.</b> A request is created, submitted to the queue, approved or rejected, and then either consumed by a session or expired. The approved grant is single-use and valid for 30 minutes. A cancel before approval closes the request without a grant; the audit reason distinguishes it from an SLA expiry.",
        "fig11",
    )

    states = table(
        ["State", "Meaning", "Allowed exits"],
        [
            ["<code>REQUESTED</code>", "The requester has created the request but not submitted it.", "PENDING, EXPIRED (withdrawn)"],
            ["<code>PENDING</code>", "The request is in the approver queue with a 15-minute SLA.", "APPROVED, DENIED, EXPIRED"],
            ["<code>APPROVED</code>", "A human approved a single-use grant valid for 30 minutes.", "CONSUMED, EXPIRED"],
            ["<code>DENIED</code>", "A human rejected the request with a reason.", "None; terminal"],
            ["<code>EXPIRED</code>", "The SLA elapsed, the grant elapsed, or the requester withdrew.", "None; terminal"],
            ["<code>CONSUMED</code>", "The grant opened a session; it cannot be reused.", "None; terminal"],
        ],
        cls="compact",
        caption="Table 1 &mdash; The six JIT states.",
    )

    transitions = table(
        ["From", "Event", "Guard", "To"],
        [
            ["&mdash;", "Create", "Requester authenticated", "<code>REQUESTED</code>"],
            ["<code>REQUESTED</code>", "Submit", "Resource exists; score in approval band", "<code>PENDING</code>"],
            ["<code>REQUESTED</code>", "Withdraw", "Requester owns the request", "<code>EXPIRED</code>"],
            ["<code>PENDING</code>", "Approve", "Approver &ne; requester; not expired", "<code>APPROVED</code>"],
            ["<code>PENDING</code>", "Deny", "Reason supplied; not expired", "<code>DENIED</code>"],
            ["<code>PENDING</code>", "SLA elapsed", "15-minute timer", "<code>EXPIRED</code>"],
            ["<code>APPROVED</code>", "Open session", "Grant unused; not expired", "<code>CONSUMED</code>"],
            ["<code>APPROVED</code>", "Grant elapsed", "30-minute ceiling", "<code>EXPIRED</code>"],
        ],
        cls="compact",
        caption="Table 2 &mdash; Transitions and the guard that protects each one.",
    )

    guards = table(
        ["Guard", "Checked where", "Failure"],
        [
            ["Requester is not the approver", "API + engine", "<code>403 SELF_APPROVAL</code>"],
            ["Request is still pending", "Resolution step", "<code>409 CONFLICT</code>"],
            ["SLA has not elapsed", "Resolution step", "<code>409 EXPIRED</code>"],
            ["Policy still allows the resource", "Engine", "<code>403 POLICY_DENY</code>"],
            ["Grant is unused", "Consumption step", "<code>409 ALREADY_CONSUMED</code>"],
            ["Grant TTL is within the policy ceiling", "Approval step", "Clamp to ceiling"],
        ],
        cls="compact",
        caption="Table 3 &mdash; Guards. The UI is not trusted to enforce any of them.",
    )

    body = f"""
<div class="wrap">
  <div class="page">
    {page_head(
        "11", "STATES / JIT",
        "A small machine<br>with a single-use grant.",
        "The JIT state machine is intentionally boring. It exists to make the approval window auditable and to prevent an approval from becoming a standing entitlement. The hard parts are the guards, not the state names.",
        chips(("FIG.", "11"), ("6", "states"), ("8", "transitions"), ("GRANT", "30 min"))
    )}
    {svg}

    <div class="prose">
      <h2>Why the states are separate</h2>
      <p><strong>REQUESTED</strong> and <strong>PENDING</strong> are different because a draft is not yet in the queue. <strong>APPROVED</strong> is not access; it is a grant that has not been used. <strong>CONSUMED</strong> is the only state that proves a session was opened. <strong>DENIED</strong> and <strong>EXPIRED</strong> are both no-grant outcomes, but they carry different reasons and different UI copy.</p>
      <p>The machine has no transition from <code>DENIED</code> or <code>EXPIRED</code> back to <code>PENDING</code>. A new attempt is a new request with a new id. That keeps the audit trail linear and prevents an approver from resurrecting an old decision.</p>

      {states}

      {transitions}

      <h2>The guards are the design</h2>
      <p>Every guard is checked server-side. A requester cannot approve their own request even if they craft the HTTP call directly. A request that expired while the approver was reading it cannot be approved. A policy published during the wait is applied at resolution. A grant that was consumed cannot be replayed.</p>

      {guards}

      <div class="cards two">
        <div class="card">
          <div class="card-label">Timeouts</div>
          <h3>Two clocks, two meanings</h3>
          <p>The 15-minute SLA bounds the wait for a human. The 30-minute grant bounds the access window after approval. They are independent: a fast approval does not extend the grant, and a slow approval does not shorten it below the policy ceiling.</p>
        </div>
        <div class="card">
          <div class="card-label">Cancellation</div>
          <h3>Withdraw is not a denial</h3>
          <p>A requester can withdraw before approval. The request closes as <code>EXPIRED</code> with <code>decision_reason = REQUESTER_CANCELLED</code>; it is not a human denial and it does not count against the requester. The API exposes this as <code>POST /v1/jit/requests/{id}/cancel</code>.</p>
        </div>
      </div>

      <h2>Audit events</h2>
      <table>
        <thead><tr><th>Event</th><th>When</th><th>Payload</th></tr></thead>
        <tbody>
          <tr><td><code>jit.requested</code></td><td>Create</td><td>Requester, resource, action, justification, score.</td></tr>
          <tr><td><code>jit.submitted</code></td><td>Requested &rarr; pending</td><td>Queue id, SLA expiry.</td></tr>
          <tr><td><code>jit.approved</code> / <code>jit.denied</code></td><td>Human decision</td><td>Approver, reason, grant TTL.</td></tr>
          <tr><td><code>jit.consumed</code></td><td>Grant used</td><td>Session id, resource, timestamp.</td></tr>
          <tr><td><code>jit.expired</code></td><td>SLA or grant elapsed</td><td>Which clock expired, prior state.</td></tr>
        </tbody>
      </table>

      {callout(
        "Approved is not access",
        "<p>The only state that proves access is <code>CONSUMED</code>. An approved grant that is never used expires and is recorded as such. The UI must not tell the user &ldquo;you have access&rdquo; until the grant has been consumed by a real session.</p>"
      )}

      {link_row([
        ("JIT sequence &rarr;", "flow-jit-approval.html"),
        ("JIT API &rarr;", "api.html#tag-jit"),
        ("Session state &rarr;", "state-session.html"),
        ("Requirements &rarr;", "requirements.html"),
      ])}
    </div>
  </div>
  {page_nav("state-jit")}
</div>
"""
    return shell(
        title="JIT request lifecycle &middot; ZeroGate",
        description=PAGE_BY_SLUG["state-jit"]["desc"],
        current="states",
        body=body,
    )


# ---------------------------------------------------------------------------
# 12 Device state
# ---------------------------------------------------------------------------

def build_device_state() -> str:
    svg = figure(
        diagrams_flows.state_device(),
        "12",
        "Device trust lifecycle",
        "<b>Trust is earned in stages and lost in one step.</b> A device is first seen as UNKNOWN, enrolled after attestation, and compliant after a passing posture report. A failed posture moves it to NON-COMPLIANT; remediation returns it to COMPLIANT. A score below 40 or a lost-device report moves it to QUARANTINED or REVOKED. Re-enrollment creates a new device id; the old record remains for audit.",
        "fig12",
    )

    states = table(
        ["State", "Meaning", "Allowed exits"],
        [
            ["<code>UNKNOWN</code>", "First contact; no attestation yet.", "ENROLLED, REVOKED"],
            ["<code>ENROLLED</code>", "Attested and bound to a user.", "COMPLIANT, NON_COMPLIANT, REVOKED"],
            ["<code>COMPLIANT</code>", "Posture passes every required check.", "NON_COMPLIANT, QUARANTINED, REVOKED"],
            ["<code>NON_COMPLIANT</code>", "A posture check failed; remediation is possible.", "COMPLIANT, QUARANTINED, REVOKED"],
            ["<code>QUARANTINED</code>", "Blocked by policy or a score below 40.", "REVOKED, COMPLIANT (after review)"],
            ["<code>REVOKED</code>", "Lost, stolen, or administratively revoked.", "None; terminal"],
        ],
        cls="compact",
        caption="Table 1 &mdash; The six device states.",
    )

    transitions = table(
        ["From", "Event", "Guard", "To"],
        [
            ["&mdash;", "First seen", "No device record", "<code>UNKNOWN</code>"],
            ["<code>UNKNOWN</code>", "Attest", "Signed enrollment bundle", "<code>ENROLLED</code>"],
            ["<code>ENROLLED</code>", "Posture pass", "All required checks pass", "<code>COMPLIANT</code>"],
            ["<code>ENROLLED</code>", "Posture fail", "Disk, root, OS, or lock check fails", "<code>NON_COMPLIANT</code>"],
            ["<code>COMPLIANT</code>", "Posture fail", "A required check regresses", "<code>NON_COMPLIANT</code>"],
            ["<code>NON_COMPLIANT</code>", "Remediate", "Next report passes", "<code>COMPLIANT</code>"],
            ["<code>COMPLIANT</code> / <code>NON_COMPLIANT</code>", "Score &lt; 40", "Session-level kill", "<code>QUARANTINED</code>"],
            ["<code>COMPLIANT</code>", "Lost / stolen", "Admin or user report", "<code>REVOKED</code>"],
            ["<code>REVOKED</code>", "Re-enroll", "New device identity", "<code>ENROLLED</code> (new id)"],
        ],
        cls="compact",
        caption="Table 2 &mdash; Transitions. Re-enrollment never revives the old device id.",
    )

    posture = table(
        ["Signal", "Source", "Why it matters"],
        [
            ["OS major version", "Posture agent", "An out-of-date OS is a known vulnerability surface."],
            ["Disk encryption", "Posture agent", "A lost laptop should not expose the local cache."],
            ["Root / jailbreak", "Posture agent", "A compromised OS can lie about the other signals."],
            ["Screen lock", "Posture agent", "An unattended device should not be an open session."],
            ["Last seen", "Posture agent", "A stale report is weaker evidence than a fresh one."],
        ],
        cls="compact",
        caption="Table 3 &mdash; The posture inputs. The agent reports state, not file contents or browsing data.",
    )

    body = f"""
<div class="wrap">
  <div class="page">
    {page_head(
        "12", "STATES / DEVICE",
        "Trust is earned<br>in stages.",
        "A device is not trusted because it exists. It is trusted because it was attested, bound to a user, and reported a passing posture. The state machine makes the stages explicit and makes revocation a one-step, terminal action.",
        chips(("FIG.", "12"), ("6", "states"), ("9", "transitions"), ("POSTURE", "&le; 24 h"))
    )}
    {svg}

    <div class="prose">
      <h2>Why a device state machine</h2>
      <p>Posture is not a boolean. A device can be enrolled but not yet compliant, compliant but one report away from non-compliance, or quarantined while an admin investigates. The state machine gives the UI and the Policy Engine a shared vocabulary. It also makes the recovery paths explicit: remediation returns a non-compliant device to compliant; re-enrollment creates a new identity rather than reviving an old one.</p>

      {states}

      {transitions}

      <h2>Revocation is a one-way door</h2>
      <p>A revoked device cannot be un-revoked. The record stays in the database with its audit history, and a re-enrollment creates a new device id with a new key. That rule prevents a stolen device from being quietly restored by flipping a flag. It also means the admin UI must be clear: &ldquo;revoke&rdquo; is not &ldquo;disable temporarily.&rdquo;</p>
      <p>Revocation cascades to the device's passkeys, live sessions, and SSH certificates. The proxy cache is invalidated, the CA revokes outstanding certificates, and the user is notified. The audit event records the actor, the reason, and the affected sessions.</p>

      {posture}

      <div class="cards two">
        <div class="card">
          <div class="card-label">Staleness</div>
          <h3>A report has a shelf life</h3>
          <p>A posture report older than 24 hours is a signal, not a fact. The device remains enrolled, but the risk score takes an 8-point deduction and the UI shows the age. A device that has not reported in 7 days is quarantined pending review.</p>
        </div>
        <div class="card">
          <div class="card-label">Re-enrollment</div>
          <h3>New identity, old history</h3>
          <p>Re-enrollment issues a new device id and a new credential. The old record remains readable for audit. A session created under the old device id cannot be resumed under the new one; the user starts a new request.</p>
        </div>
      </div>

      <h2>What the agent does not collect</h2>
      <ul>
        <li>No file contents, browser history, clipboard, or screen capture.</li>
        <li>No precise location; the server derives coarse network context from the request.</li>
        <li>No biometric data; the passkey handles user verification locally.</li>
        <li>No persistent device fingerprint beyond the enrolled id and posture fields.</li>
      </ul>

      {callout(
        "A revoked device is not deleted history",
        "<p>The row remains, the passkeys remain as revoked records, and the audit chain remains verifiable. Deleting the device would break the explanation of every decision it participated in. The state machine is terminal, not destructive.</p>"
      )}

      {link_row([
        ("Passkey flow &rarr;", "flow-passkey.html"),
        ("Risk report &rarr;", "risk-scoring.html"),
        ("Device API &rarr;", "api.html#tag-devices"),
        ("Requirements &rarr;", "requirements.html"),
      ])}
    </div>
  </div>
  {page_nav("state-device")}
</div>
"""
    return shell(
        title="Device trust lifecycle &middot; ZeroGate",
        description=PAGE_BY_SLUG["state-device"]["desc"],
        current="states",
        body=body,
    )


# ---------------------------------------------------------------------------
# Markdown reports
# ---------------------------------------------------------------------------

def wrap_tables(html_text: str) -> str:
    return re.sub(
        r"<table>(.*?)</table>",
        r'<div class="table-wrap"><table>\1</table></div>',
        html_text,
        flags=re.S,
    )


def decorate_priority(html_text: str) -> str:
    mapping = {"Core": "core", "Add-on": "add-on", "Stretch": "stretch"}
    for label, klass in mapping.items():
        html_text = re.sub(
            rf"<td>{label}</td>",
            f'<td><span class="badge {klass}">{label}</span></td>',
            html_text,
        )
    return html_text


def markdown_report(path: Path, *, decorate: bool = False) -> tuple[str, list[dict]]:
    text = path.read_text(encoding="utf-8")
    md = markdown.Markdown(
        extensions=["tables", "fenced_code", "toc", "sane_lists", "attr_list"],
        extension_configs={"toc": {"permalink": False, "toc_depth": "2-2"}},
    )
    body = md.convert(text)
    body = wrap_tables(body)
    if decorate:
        body = decorate_priority(body)
    toc = [token for token in md.toc_tokens if token["level"] == 2]
    return body, toc


def report_aside(toc: list[dict], source: str, meta: str, extra_links: str = "") -> str:
    items = "".join(
        f'<a href="#{token["id"]}">{token["name"]}</a>' for token in toc
    )
    return f"""
<aside class="report-aside" aria-label="On this page">
  <div class="card-label">On this page</div>
  <nav>{items}</nav>
  <div class="aside-rule"></div>
  <div class="aside-meta">{meta}<br>Source: <code>{source}</code></div>
  <div class="aside-rule"></div>
  <a href="{source}">Raw Markdown &rarr;</a>
  {extra_links}
</aside>"""


# ---------------------------------------------------------------------------
# 13 Risk scoring
# ---------------------------------------------------------------------------

def build_risk() -> str:
    body_md, toc = markdown_report(DOCS / "risk-scoring-report.md")
    aside = report_aside(
        toc,
        "risk-scoring-report.md",
        "Signal catalog<br>Scoring model<br>Evaluation plan",
    )

    body = f"""
<div class="wrap">
  <div class="page">
    {page_head(
        "13", "EVIDENCE / RISK",
        "A score a human<br>can defend.",
        "ZeroGate needs a trust score that survives a review. The model is a transparent additive score with a bounded anomaly adjustment, not a black box. Every point is attributable to a named signal, every category is capped, and every hard gate is evaluated before the arithmetic.",
        chips(("REPORT", "13"), ("27", "signals"), ("5", "categories"), ("ML CAP", "&minus;15"))
    )}
    <div class="stat-strip">
      <div class="stat"><span class="n">27</span><span class="l">named signals</span></div>
      <div class="stat"><span class="n">05</span><span class="l">category caps</span></div>
      <div class="stat"><span class="n">04</span><span class="l">trust bands</span></div>
      <div class="stat"><span class="n">&minus;15</span><span class="l">maximum ML deduction</span></div>
    </div>

    <div class="report-layout">
      <article class="prose report-body">
        {body_md}
      </article>
      {aside}
    </div>

    {link_row([
      ("Policy Engine &rarr;", "policy-engine.html"),
      ("Requirements &rarr;", "requirements.html"),
      ("API contract &rarr;", "api.html"),
      ("Mid-session kill &rarr;", "flow-session-kill.html"),
    ])}
  </div>
  {page_nav("risk-scoring")}
</div>
"""
    return shell(
        title="Risk scoring &middot; ZeroGate",
        description=PAGE_BY_SLUG["risk-scoring"]["desc"],
        current="evidence",
        body=body,
    )


# ---------------------------------------------------------------------------
# 14 Requirements
# ---------------------------------------------------------------------------

def build_requirements() -> str:
    body_md, toc = markdown_report(
        DOCS / "functional-requirements.md", decorate=True
    )
    aside = report_aside(
        toc,
        "functional-requirements.md",
        "27 functional<br>14 non-functional<br>6 exclusions",
    )

    body = f"""
<div class="wrap">
  <div class="page">
    {page_head(
        "14", "EVIDENCE / REGISTER",
        "Twenty-seven promises,<br>fourteen targets.",
        "The register is the contract between the design and the implementation. Each functional requirement has a priority, an owning team, and acceptance criteria. The non-functional requirements set the performance, privacy, and operability targets. The out-of-scope list is part of the design, not an afterthought.",
        chips(("REGISTER", "14"), ("27", "functional"), ("14", "non-functional"), ("6", "exclusions"))
    )}
    <div class="stat-strip">
      <div class="stat"><span class="n">19</span><span class="l">core requirements</span></div>
      <div class="stat"><span class="n">06</span><span class="l">add-on requirements</span></div>
      <div class="stat"><span class="n">02</span><span class="l">stretch requirements</span></div>
      <div class="stat"><span class="n">14</span><span class="l">non-functional targets</span></div>
    </div>

    <div class="callout" style="margin-top:28px">
      <span class="k">Priority key</span>
      <p><span class="badge core">Core</span> required for the defence &nbsp; <span class="badge add-on">Add-on</span> strengthens the thesis &nbsp; <span class="badge stretch">Stretch</span> only if the core and add-ons are stable.</p>
    </div>

    <div class="report-layout">
      <article class="prose report-body">
        {body_md}
      </article>
      {aside}
    </div>

    {link_row([
      ("Risk report &rarr;", "risk-scoring.html"),
      ("API contract &rarr;", "api.html"),
      ("Architecture &rarr;", "architecture.html"),
      ("Traceability in the raw register &rarr;", "functional-requirements.md"),
    ])}
  </div>
  {page_nav("requirements")}
</div>
"""
    return shell(
        title="Functional requirements &middot; ZeroGate",
        description=PAGE_BY_SLUG["requirements"]["desc"],
        current="evidence",
        body=body,
    )


# ---------------------------------------------------------------------------
# 15 API reference
# ---------------------------------------------------------------------------

API_SPEC = yaml.safe_load((DOCS / "openapi.yaml").read_text(encoding="utf-8"))
METHODS = ("get", "post", "put", "patch", "delete")
TAG_SLUG = lambda name: re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def operations() -> list[dict]:
    out = []
    for path, item in API_SPEC["paths"].items():
        for method in METHODS:
            op = item.get(method)
            if not op:
                continue
            security = op.get("security", API_SPEC.get("security", []))
            public = security == []
            success = next((code for code in op["responses"] if code.startswith("2")), "200")
            response = op["responses"].get(success, {})
            label = "No content"
            if "$ref" in response:
                label = response["$ref"].split("/")[-1]
            else:
                content = response.get("content", {}).get("application/json", {})
                schema = content.get("schema", {})
                if "$ref" in schema:
                    label = schema["$ref"].split("/")[-1]
                elif schema.get("type") == "array":
                    items = schema.get("items", {})
                    item_ref = items.get("$ref", "")
                    label = "Array" + (f" &lt;{item_ref.split('/')[-1]}&gt;" if item_ref else "")
                elif schema.get("type"):
                    label = schema["type"]
            out.append(
                {
                    "path": path,
                    "method": method,
                    "op": op,
                    "tag": op["tags"][0],
                    "public": public,
                    "success": success,
                    "schema": label,
                }
            )
    return out


def operation_table(ops: list[dict]) -> str:
    rows = []
    for entry in ops:
        method = entry["method"]
        op = entry["op"]
        auth = "Public" if entry["public"] else "Cookie / Bearer"
        rows.append(
            [
                f'<span class="method {method}">{method}</span>',
                f'<span class="path">{esc(entry["path"])}</span>'
                f'<span class="op-id">{esc(op.get("operationId", ""))}</span>',
                esc(op.get("summary", "")),
                f'<span class="auth">{auth}</span>',
                f'<span class="success">{entry["success"]} &middot; {entry["schema"]}</span>',
            ]
        )
    return table(
        ["Method", "Path", "Summary", "Auth", "Success"],
        rows,
        cls="api-table",
        row_ids=[f'op-{entry["op"].get("operationId", "")}' for entry in ops],
    )


def build_api() -> str:
    ops = operations()
    by_tag: dict[str, list[dict]] = {tag["name"]: [] for tag in API_SPEC["tags"]}
    for entry in ops:
        by_tag.setdefault(entry["tag"], []).append(entry)

    tag_sections = []
    for tag in API_SPEC["tags"]:
        name = tag["name"]
        entries = by_tag.get(name, [])
        if not entries:
            continue
        tag_sections.append(
            f'<section class="api-group" id="tag-{TAG_SLUG(name)}">'
            '<div class="api-group-head">'
            f"<h2>{esc(name)}</h2>"
            f'<span class="count">{len(entries)} operations</span>'
            "</div>"
            f'<p class="api-group-desc">{esc(tag.get("description", ""))}</p>'
            f"{operation_table(entries)}"
            "</section>"
        )

    tag_counts = table(
        ["Tag", "Operations", "What it covers"],
        [
            [f'<a href="#tag-{TAG_SLUG(t["name"])}">{esc(t["name"])}</a>', str(len(by_tag.get(t["name"], []))), esc(t.get("description", ""))]
            for t in API_SPEC["tags"]
        ],
        cls="compact",
        caption="Table 2 &mdash; Operations by tag. The endpoint index below follows this order.",
    )

    schemas = sorted(API_SPEC["components"]["schemas"].keys())
    schema_chips = "".join(f'<span class="schema-chip">{esc(name)}</span>' for name in schemas)

    authorize_response = """{
  "decision": "ALLOW",
  "band": "ALLOW",
  "trust_score": 92,
  "reason_codes": ["BAND_ALLOW"],
  "signals": [],
  "ml_adjustment": 0,
  "model_version": "iforest-0.3.0",
  "policy_id": "pol_web_default",
  "policy_version": 12,
  "obligations": [{"type": "limit_ttl", "seconds": 1800}],
  "session": {
    "id": "ses_01J8Z8",
    "state": "ACTIVE",
    "trust_score": 92,
    "expires_at": "2026-10-14T10:42:00Z"
  },
  "audit_id": "evt_01J8Z9K4",
  "decided_at": "2026-10-14T10:12:00Z",
  "correlation_id": "req_5f2b1c"
}"""

    kill_response = """{
  "session_id": "ses_01J8Z8",
  "state": "KILLED",
  "killed_at": "2026-10-14T10:31:07Z",
  "revoked_certificate_ids": ["sshcert_77a1"],
  "audit_id": "evt_01J8ZA7Q",
  "already_killed": false
}"""

    errors = table(
        ["Status", "Shared response", "When"],
        [
            ["400", "&mdash;", "Malformed JSON, missing field, or invalid enum."],
            ["401", "<code>Unauthorized</code>", "No session cookie, expired bearer, or invalid assertion."],
            ["403", "<code>Forbidden</code>", "Authenticated but not allowed; includes self-approval and hard gates."],
            ["404", "<code>NotFound</code>", "Unknown device, session, policy, request, or certificate."],
            ["409", "<code>Conflict</code>", "State transition refused, duplicate decision, or idempotency conflict."],
            ["422", "<code>UnprocessableEntity</code>", "Semantically valid but rejected by policy or validation."],
            ["429", "<code>TooManyRequests</code>", "Rate limit; includes <code>retry_after_seconds</code>."],
            ["5XX", "&mdash;", "Unexpected server failure; fail closed and correlate with the request id."],
        ],
        cls="compact",
        caption="Table 3 &mdash; The shared error surface. Every error uses the same Problem envelope.",
    )

    error_example = """{
  "error": {
    "code": "SELF_APPROVAL",
    "message": "The requester cannot approve their own request.",
    "correlation_id": "req_9b3e2a",
    "details": {"request_id": "jit_01J8ZB"}
  }
}"""

    body = f"""
<div class="wrap">
  <div class="page">
    {page_head(
        "15", "CONTRACT / API",
        "One contract,<br>every gate.",
        "The OpenAPI 3.1 document is the interface between the portal, the two enforcement points, the Policy Administrator, and the admin console. It exposes 42 paths and 53 operations over twelve tags. The central call is <code>POST /v1/authorize</code>; every enforcement path speaks the same decision shape.",
        chips(("OPENAPI", "3.1"), ("42", "paths"), ("53", "operations"), ("76", "schemas"))
    )}
    <div class="stat-strip">
      <div class="stat"><span class="n">42</span><span class="l">paths</span></div>
      <div class="stat"><span class="n">53</span><span class="l">operations</span></div>
      <div class="stat"><span class="n">76</span><span class="l">schemas</span></div>
      <div class="stat"><span class="n">12</span><span class="l">tags</span></div>
    </div>

    <div class="callout" style="margin-top:28px;max-width:900px">
      <span class="k">Source of truth</span>
      <p>The rendered index on this page is generated from <a href="openapi.yaml"><code>openapi.yaml</code></a>. If the two disagree, the YAML wins. The spec is validated with Redocly and a local reference checker in CI.</p>
    </div>

    <div class="api-deep">
      <div class="card">
        <div class="card-label"><span class="method post">post</span> /v1/authorize</div>
        <h3>The decision shape</h3>
        <p>One call returns the decision, band, score, reason codes, signals, obligations, session grant, and audit id. Enforcement points never see a different schema.</p>
        {code_block(authorize_response, "language-json")}
      </div>
      <div class="card">
        <div class="card-label"><span class="method post">post</span> /v1/sessions/{{sessionId}}/kill</div>
        <h3>The idempotent kill</h3>
        <p>The kill closes the proxy session, revokes certificates, and records the event. A retry with the same idempotency key returns the first result and sets <code>already_killed</code>.</p>
        {code_block(kill_response, "language-json")}
      </div>
    </div>

    <div class="prose wide">
      <h2>Conventions</h2>
      <div class="cards three">
        <div class="card">
          <div class="card-label">01 / Versioning</div>
          <h3>Everything under <code>/v1</code></h3>
          <p>Paths are versioned. Additive changes are allowed inside a version; a breaking change requires a new prefix. Deprecated operations carry a <code>deprecated: true</code> flag.</p>
        </div>
        <div class="card">
          <div class="card-label">02 / Auth</div>
          <h3>Cookie or bearer</h3>
          <p>Browsers use the <code>zg_session</code> cookie. The CLI and internal services use a short-lived bearer token. Public operations are limited to health, the two passkey ceremonies, the CA public key, and the SPA knock.</p>
        </div>
        <div class="card">
          <div class="card-label">03 / Mutations</div>
          <h3>Idempotency keys</h3>
          <p>Every state-changing operation accepts an <code>Idempotency-Key</code>. Replaying the same key with the same body returns the original result; a different body returns <code>409</code>.</p>
        </div>
        <div class="card">
          <div class="card-label">04 / Errors</div>
          <h3>One envelope</h3>
          <p>Every error is a <code>Problem</code> with <code>code</code>, <code>message</code>, optional <code>details</code>, and a <code>correlation_id</code>. The UI shows the correlation id, not a stack trace.</p>
        </div>
        <div class="card">
          <div class="card-label">05 / Lists</div>
          <h3>Cursor pagination</h3>
          <p>List endpoints take <code>limit</code> and <code>cursor</code> and return <code>PageInfo</code>. Cursors are opaque and stable for the life of the query.</p>
        </div>
        <div class="card">
          <div class="card-label">06 / Time</div>
          <h3>ISO 8601, UTC</h3>
          <p>All timestamps are RFC 3339 strings in UTC. Durations are integer seconds. The API never returns a local-time string.</p>
        </div>
      </div>

      <h2>Authentication</h2>
      <div class="cards two">
        <div class="card">
          <div class="card-label">Browser</div>
          <h3><code>sessionCookie</code></h3>
          <p>An HttpOnly, Secure, SameSite=Lax cookie named <code>zg_session</code>, minted after a successful passkey verification. The server-side session has a 15-minute idle timeout and an 8-hour absolute lifetime.</p>
        </div>
        <div class="card">
          <div class="card-label">CLI / service</div>
          <h3><code>bearerAuth</code></h3>
          <p>A short-lived JWT signed by the identity service. The SSH helper and internal services use it. It carries the user, device, and role claims; it is never stored in a URL or a log.</p>
        </div>
      </div>
      <p>Five operations are public: <code>GET /v1/health</code>, <code>POST /v1/auth/passkey/options</code>, <code>POST /v1/auth/passkey/verify</code>, <code>GET /v1/ssh/ca/public-key</code>, and <code>POST /v1/spa/knock</code>. Everything else requires a session or a bearer token and is subject to rate limits.</p>

      {tag_counts}

      <h2>Endpoint index</h2>
      <p>Operations are grouped by tag in the order declared by the spec. Each row links to its operation id; the full request and response schemas live in <code>openapi.yaml</code>.</p>
      <p class="mini-note api-mobile-note">On narrow screens the auth and success columns are hidden to keep the path and summary readable. Both remain in the YAML and in the desktop table.</p>
      {"".join(tag_sections)}

      <h2>Error model</h2>
      <p>The error envelope is the same for validation, authentication, policy, and rate limiting. A client can branch on <code>error.code</code> without parsing prose, and a support engineer can correlate the request with the audit chain through <code>correlation_id</code>.</p>
      {errors}
      {code_block(error_example, "language-json")}

      <h2>Schema lexicon</h2>
      <p>The contract defines 76 schemas. The names are stable; a rename is a breaking change. The most important are <code>AuthorizeRequest</code>, <code>AuthorizeResponse</code>, <code>Decision</code>, <code>Band</code>, <code>Obligation</code>, <code>Session</code>, <code>KillResult</code>, <code>SshCertificate</code>, <code>JitRequest</code>, <code>Policy</code>, <code>AuditEvent</code>, and <code>Problem</code>.</p>
      <div class="schema-grid">{schema_chips}</div>

      <h2>Validation</h2>
      <p>The spec is linted with <code>@redocly/cli</code> using the recommended ruleset and checked by a local resolver that walks every internal <code>$ref</code>. The build fails on a missing reference, a duplicate operation id, or an undocumented 4XX on an operation that requires authentication.</p>

      {callout(
        "Scope of the contract",
        "<p>The API covers web apps and SSH servers only. There is no Kubernetes, database, email, SWG, CASB, DLP, or multi-tenancy surface. Vault operations are included because SecureVault is core; they are a separate encrypted store, not part of the access-control schema.</p>"
      )}

      {link_row([
        ("Download openapi.yaml &rarr;", "openapi.yaml"),
        ("Requirements &rarr;", "requirements.html"),
        ("Architecture &rarr;", "architecture.html"),
        ("Risk report &rarr;", "risk-scoring.html"),
      ])}
    </div>
  </div>
  {page_nav("api")}
</div>
"""
    return shell(
        title="API reference &middot; ZeroGate",
        description=PAGE_BY_SLUG["api"]["desc"],
        current="contract",
        body=body,
    )


BUILDERS = {
    "index": build_index,
    "architecture": build_architecture,
    "domain-model": build_domain,
    "data-model": build_data_model,
    "database-schema": build_database,
    "flow-passkey": build_passkey,
    "flow-ssh-certificate": build_ssh,
    "flow-jit-approval": build_jit,
    "flow-session-kill": build_kill,
    "policy-engine": build_policy,
    "state-session": build_session_state,
    "state-jit": build_jit_state,
    "state-device": build_device_state,
    "risk-scoring": build_risk,
    "requirements": build_requirements,
    "api": build_api,
}


def main() -> None:
    DOCS.mkdir(parents=True, exist_ok=True)
    written = []
    for key, builder in BUILDERS.items():
        path = DOCS / ("index.html" if key == "index" else PAGE_BY_SLUG[key]["file"])
        path.write_text(builder(), encoding="utf-8")
        written.append(path)
    print(f"wrote {len(written)} pages to {DOCS}")


if __name__ == "__main__":
    main()
