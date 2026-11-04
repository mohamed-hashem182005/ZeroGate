"""ZeroGate design dossier — shared theme tokens and page chrome.

The visual system is adapted from cathrynlavery/diagram-design (MIT).
The skin is a warm editorial paper palette with a single brick accent.
"""

PAPER = "#f4f1e9"
PAPER2 = "#ebe6da"
WHITE = "#ffffff"
INK = "#1f2a30"
INK_STRONG = "#111111"
MUTED = "#52646c"
SOFT = "#5c6f77"
RULE = "rgba(31,42,48,0.12)"
RULE_SOLID = "#c9c2b4"
ACCENT = "#b54427"
ACCENT_TINT = "rgba(181,68,39,0.08)"
LINK = "#2c5d8a"
LINK_TINT = "rgba(44,93,138,0.07)"

SANS = "'Geist', system-ui, sans-serif"
SERIF = "'Instrument Serif', 'Noto Serif', serif"
MONO = "'Geist Mono', ui-monospace, monospace"

FONT_LINK = (
    '<link href="https://fonts.googleapis.com/css2?'
    "family=Instrument+Serif:ital@0;1&"
    "family=Geist:wght@400;500;600&"
    "family=Geist+Mono:wght@400;500;600&display=swap"
    '" rel="stylesheet">'
)

CSS = r"""
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
:root {
  --paper: #f4f1e9;
  --paper-2: #ebe6da;
  --white: #ffffff;
  --ink: #1f2a30;
  --muted: #52646c;
  --soft: #5c6f77;
  --rule: rgba(31,42,48,0.12);
  --rule-solid: #c9c2b4;
  --accent: #b54427;
  --accent-tint: rgba(181,68,39,0.08);
  --link: #2c5d8a;
  --sans: 'Geist', system-ui, sans-serif;
  --serif: 'Instrument Serif', 'Noto Serif', serif;
  --mono: 'Geist Mono', ui-monospace, monospace;
}
html { scroll-behavior: smooth; }
body {
  font-family: var(--sans);
  background: var(--paper);
  color: var(--ink);
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}
::selection { background: rgba(181,68,39,0.18); }

/* ---------- header ---------- */
.site-header {
  border-bottom: 1px solid var(--rule);
  padding: 18px 0;
}
.header-inner {
  width: min(1300px, calc(100% - 64px));
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
}
.brand {
  display: flex; align-items: center; gap: 12px;
  text-decoration: none; color: var(--ink);
}
.brand-mark {
  width: 30px; height: 30px;
  display: grid; place-items: center;
  background: var(--accent); color: var(--paper);
  font-family: var(--serif); font-size: 15px; line-height: 1;
  border-radius: 3px;
}
.brand-text { display: flex; flex-direction: column; gap: 1px; }
.brand-name { font-family: var(--serif); font-size: 19px; letter-spacing: -0.01em; }
.brand-sub {
  font-family: var(--mono); font-size: 8px; letter-spacing: 0.18em;
  text-transform: uppercase; color: var(--muted);
}
.site-nav { display: flex; align-items: center; gap: 22px; flex-wrap: wrap; }
.site-nav a {
  font-family: var(--mono); font-size: 10px; letter-spacing: 0.1em;
  text-transform: uppercase; color: var(--muted); text-decoration: none;
  border-bottom: 1px solid transparent; padding-bottom: 2px;
}
.site-nav a:hover, .site-nav a[aria-current="page"] {
  color: var(--ink); border-bottom-color: var(--accent);
}

/* ---------- page ---------- */
.wrap { width: min(1300px, calc(100% - 64px)); margin: 0 auto; }
.page { padding: 64px 0 72px; }
.chapter {
  display: flex; align-items: center; gap: 12px; margin-bottom: 18px;
}
.chapter-num {
  font-family: var(--mono); font-size: 10px; letter-spacing: 0.12em;
  color: var(--accent); border: 1px solid rgba(181,68,39,0.35);
  border-radius: 2px; padding: 3px 6px; line-height: 1;
}
.eyebrow {
  font-family: var(--mono); font-size: 10px; font-weight: 500;
  letter-spacing: 0.18em; text-transform: uppercase; color: var(--muted);
}
h1 {
  font-family: var(--serif); font-weight: 400; font-size: clamp(2.3rem, 4vw + 1rem, 3.6rem);
  line-height: 1.02; letter-spacing: -0.025em; max-width: 980px;
}
.lede {
  font-size: 19px; line-height: 1.62; color: var(--muted);
  max-width: 790px; margin-top: 20px;
}
.meta-row { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 26px; }
.chip {
  font-family: var(--mono); font-size: 9px; letter-spacing: 0.08em;
  text-transform: uppercase; color: var(--muted);
  border: 1px solid var(--rule); border-radius: 2px;
  padding: 5px 8px; background: rgba(255,255,255,0.45);
}
.chip strong { color: var(--ink); font-weight: 500; }

/* ---------- diagram ---------- */
.diagram-block { margin: 44px 0 0; }
.diagram-top {
  display: flex; align-items: baseline; justify-content: space-between;
  gap: 20px; border-top: 1px solid var(--rule); padding-top: 16px;
}
.diagram-label {
  font-family: var(--mono); font-size: 9px; letter-spacing: 0.16em;
  text-transform: uppercase; color: var(--soft);
}
.diagram-hint {
  display: none; white-space: nowrap;
  font-family: var(--mono); font-size: 9px; letter-spacing: 0.04em;
  color: var(--soft); text-align: right;
}
.diagram-container {
  width: 100%; overflow-x: auto; margin-top: 8px;
  scrollbar-width: thin; scrollbar-color: var(--rule-solid) transparent;
}
.diagram-container svg { width: 100%; display: block; }
.caption {
  font-size: 12.5px; line-height: 1.6; color: var(--muted);
  max-width: 900px; margin-top: 12px;
}
.caption b { color: var(--ink); font-weight: 600; }

/* ---------- cards ---------- */
.cards {
  display: grid; grid-template-columns: 1.15fr 0.95fr 0.9fr;
  gap: 16px; margin: 40px 0 0;
}
.cards.two { grid-template-columns: 1.25fr 0.75fr; }
.cards.four { grid-template-columns: 1.1fr 1fr 0.9fr 0.9fr; }
.card {
  background: var(--white); border: 1px solid var(--rule);
  border-radius: 6px; padding: 20px; min-width: 0;
}
.card-label {
  font-family: var(--mono); font-size: 8px; letter-spacing: 0.16em;
  text-transform: uppercase; color: var(--soft); margin-bottom: 10px;
}
.card h3 {
  font-size: 15px; font-weight: 600; letter-spacing: -0.01em;
  line-height: 1.3; margin-bottom: 10px;
}
.card p, .card li { font-size: 12.5px; line-height: 1.62; color: var(--muted); }
.card ul, .card ol { padding-left: 16px; display: grid; gap: 6px; }
.card li::marker { color: var(--accent); }
.card .rule-list { list-style: none; padding-left: 0; }
.card .rule-list li {
  border-top: 1px solid var(--rule); padding-top: 8px;
}
.card .rule-list li:first-child { border-top: 0; padding-top: 0; }
.card .mono { font-family: var(--mono); font-size: 10.5px; letter-spacing: 0.02em; color: var(--ink); }
.card-dot {
  display: inline-block; width: 7px; height: 7px; border-radius: 50%;
  margin-right: 7px; vertical-align: 1px;
}
.dot-accent { background: var(--accent); }
.dot-ink { background: var(--ink); }
.dot-muted { background: var(--muted); }
.dot-link { background: var(--link); }
.dot-soft { background: var(--soft); }

/* ---------- prose ---------- */
.prose { max-width: 900px; margin-top: 52px; }
.prose.wide { max-width: 100%; }
.prose.wide > p { max-width: 760px; }
.prose.wide > .callout { max-width: 900px; }
.prose h2 {
  font-family: var(--serif); font-weight: 400; font-size: 32px;
  line-height: 1.12; letter-spacing: -0.02em; margin: 54px 0 16px;
}
.prose h2:first-child { margin-top: 0; }
.prose h3 {
  font-size: 16px; font-weight: 600; letter-spacing: -0.01em;
  margin: 32px 0 10px;
}
.prose h4 {
  font-family: var(--mono); font-size: 10px; font-weight: 500;
  letter-spacing: 0.14em; text-transform: uppercase; color: var(--muted);
  margin: 26px 0 8px;
}
.prose p { font-size: 15px; line-height: 1.72; color: var(--muted); margin: 12px 0; }
.prose p strong, .prose li strong { color: var(--ink); font-weight: 600; }
.prose ul, .prose ol { margin: 12px 0 12px 22px; display: grid; gap: 7px; }
.prose li { font-size: 14.5px; line-height: 1.65; color: var(--muted); }
.prose li::marker { color: var(--accent); }
.prose a { color: var(--link); text-decoration-thickness: 1px; text-underline-offset: 2px; }
.prose code {
  font-family: var(--mono); font-size: 12px; background: var(--paper-2);
  border: 1px solid rgba(31,42,48,0.06); border-radius: 2px;
  padding: 1px 4px; color: var(--ink);
}
.prose pre {
  background: var(--ink); color: #ece7db; border-radius: 6px;
  padding: 20px 22px; overflow-x: auto; margin: 18px 0;
  font-family: var(--mono); font-size: 12px; line-height: 1.65;
}
.prose pre code { background: none; border: 0; padding: 0; color: inherit; }
.prose blockquote {
  border-left: 2px solid var(--accent); padding: 2px 0 2px 20px;
  margin: 22px 0; font-family: var(--serif); font-size: 21px;
  line-height: 1.5; color: var(--ink);
}
.prose blockquote p { font-size: inherit; color: inherit; }
.prose hr { border: 0; border-top: 1px solid var(--rule); margin: 36px 0; }

/* ---------- tables ---------- */
.table-wrap { width: 100%; overflow-x: auto; margin: 18px 0 24px; }
table {
  width: 100%; border-collapse: collapse; font-size: 12.5px;
  line-height: 1.5; background: rgba(255,255,255,0.38);
}
th {
  font-family: var(--mono); font-size: 8.5px; font-weight: 500;
  letter-spacing: 0.12em; text-transform: uppercase; color: var(--soft);
  text-align: left; padding: 10px 12px; border-bottom: 1px solid var(--ink);
  vertical-align: bottom; white-space: nowrap;
}
td {
  padding: 10px 12px; border-bottom: 1px solid var(--rule);
  color: var(--muted); vertical-align: top;
}
td:first-child { color: var(--ink); }
tbody tr:hover td { background: rgba(255,255,255,0.55); }
td code, th code { font-family: var(--mono); font-size: 11px; }
table.compact td, table.compact th { padding: 7px 10px; }

/* ---------- method tags ---------- */
.method {
  display: inline-block; font-family: var(--mono); font-size: 9px;
  font-weight: 500; letter-spacing: 0.06em; line-height: 1;
  padding: 4px 5px 3px; border-radius: 2px; min-width: 42px;
  text-align: center; color: var(--ink); border: 1px solid var(--rule-solid);
  background: var(--paper);
}
.method.get { color: #2c5d8a; border-color: rgba(44,93,138,0.4); background: rgba(44,93,138,0.06); }
.method.post { color: #6d5a1f; border-color: rgba(109,90,31,0.4); background: rgba(109,90,31,0.06); }
.method.put, .method.patch { color: #61522b; border-color: rgba(97,82,43,0.4); background: rgba(97,82,43,0.06); }
.method.delete { color: var(--accent); border-color: rgba(181,68,39,0.4); background: rgba(181,68,39,0.06); }

/* ---------- page nav / footer ---------- */
.page-nav {
  display: grid; grid-template-columns: 1fr 1fr; gap: 16px;
  margin-top: 64px; padding-top: 24px; border-top: 1px solid var(--rule);
}
.page-nav a {
  display: block; text-decoration: none; color: var(--ink);
  border: 1px solid var(--rule); border-radius: 6px; padding: 16px 18px;
  background: rgba(255,255,255,0.35);
}
.page-nav a:hover { border-color: var(--rule-solid); background: var(--white); }
.page-nav .dir {
  font-family: var(--mono); font-size: 8px; letter-spacing: 0.14em;
  text-transform: uppercase; color: var(--soft); display: block; margin-bottom: 5px;
}
.page-nav .name { font-family: var(--serif); font-size: 20px; }
.page-nav .next { text-align: right; }
.site-footer {
  border-top: 1px solid var(--rule); padding: 24px 0 40px;
}
.footer-inner {
  width: min(1300px, calc(100% - 64px)); margin: 0 auto;
  display: flex; justify-content: space-between; gap: 24px; flex-wrap: wrap;
  font-family: var(--mono); font-size: 9.5px; line-height: 1.7;
  letter-spacing: 0.04em; color: var(--soft);
}
.footer-inner a { color: var(--muted); text-decoration: none; border-bottom: 1px solid var(--rule); }

/* ---------- index ---------- */
.index-hero { padding: 80px 0 44px; }
.index-hero h1 { font-size: clamp(3rem, 7vw + 0.5rem, 6.2rem); max-width: 1000px; }
.index-hero .lede { max-width: 680px; font-size: 20px; }
.index-rule {
  display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 24px;
  border-top: 1px solid var(--ink); border-bottom: 1px solid var(--rule);
  padding: 20px 0; margin-top: 40px;
}
.index-rule div { display: flex; flex-direction: column; gap: 4px; }
.index-rule .k {
  font-family: var(--mono); font-size: 8px; letter-spacing: 0.16em;
  text-transform: uppercase; color: var(--soft);
}
.index-rule .v { font-size: 13px; color: var(--ink); }
.section-head {
  display: flex; align-items: baseline; justify-content: space-between;
  gap: 20px; margin: 64px 0 20px; border-bottom: 1px solid var(--ink);
  padding-bottom: 10px;
}
.section-head h2 {
  font-family: var(--serif); font-weight: 400; font-size: 34px;
  letter-spacing: -0.02em;
}
.section-head .count {
  font-family: var(--mono); font-size: 9px; letter-spacing: 0.12em;
  text-transform: uppercase; color: var(--soft);
}
.toc-grid {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px;
}
.toc-grid.four { grid-template-columns: repeat(4, 1fr); }
.toc-grid .wide { grid-column: span 2; }
.toc-card {
  display: block; text-decoration: none; color: var(--ink);
  background: rgba(255,255,255,0.45); border: 1px solid var(--rule);
  border-radius: 6px; padding: 20px; min-height: 148px;
  transition: background 120ms ease, border-color 120ms ease;
}
.toc-card:hover { background: var(--white); border-color: var(--rule-solid); }
.toc-card .num {
  font-family: var(--mono); font-size: 9px; letter-spacing: 0.1em;
  color: var(--accent); margin-bottom: 18px; display: block;
}
.toc-card h3 {
  font-family: var(--serif); font-weight: 400; font-size: 24px;
  line-height: 1.1; letter-spacing: -0.015em; margin-bottom: 8px;
}
.toc-card p { font-size: 12.5px; line-height: 1.55; color: var(--muted); }
.toc-card .type {
  display: block; margin-top: 14px; font-family: var(--mono);
  font-size: 8px; letter-spacing: 0.12em; text-transform: uppercase; color: var(--soft);
}
.toc-card.accent { border-color: rgba(181,68,39,0.4); background: var(--accent-tint); }
.toc-card.accent:hover { background: rgba(181,68,39,0.12); }
.manifest {
  margin-top: 64px; border-top: 1px solid var(--ink); padding-top: 20px;
  display: grid; grid-template-columns: 1.4fr 1fr 1fr; gap: 32px;
}
.manifest p { font-size: 13px; line-height: 1.65; color: var(--muted); }
.manifest h3 {
  font-family: var(--mono); font-size: 9px; letter-spacing: 0.14em;
  text-transform: uppercase; color: var(--soft); margin-bottom: 10px;
}
.manifest ul { list-style: none; display: grid; gap: 6px; }
.manifest li { font-size: 12.5px; color: var(--muted); }
.manifest li span { color: var(--ink); font-family: var(--mono); font-size: 10px; }

/* ---------- risk specific ---------- */
.risk-band {
  display: grid; grid-template-columns: 1.4fr 1fr 1fr 1.4fr;
  border: 1px solid var(--rule); border-radius: 6px; overflow: hidden;
  margin: 24px 0;
}
.risk-band div { padding: 14px 16px; border-left: 1px solid var(--rule); }
.risk-band div:first-child { border-left: 0; }
.risk-band .band-name {
  font-family: var(--mono); font-size: 9px; letter-spacing: 0.12em;
  text-transform: uppercase; margin-bottom: 4px;
}
.risk-band .band-range { font-family: var(--serif); font-size: 26px; line-height: 1; }
.risk-band .band-action { font-size: 11px; color: var(--muted); margin-top: 6px; }
.band-allow { background: rgba(111,130,100,0.10); }
.band-step { background: rgba(166,124,61,0.10); }
.band-approve { background: rgba(44,93,138,0.08); }
.band-deny { background: rgba(181,68,39,0.10); }

/* ---------- additions for the dossier ---------- */
.skip {
  position: absolute; left: -9999px; top: 0; z-index: 20;
  background: var(--ink); color: var(--paper); padding: 10px 14px;
  font-family: var(--mono); font-size: 11px; text-decoration: none;
}
.skip:focus { left: 16px; top: 16px; }
.figure-stack .diagram-block { margin-top: 40px; }
.figure-stack .diagram-block:first-child { margin-top: 44px; }
.callout {
  border: 1px solid var(--rule); border-left: 2px solid var(--accent);
  background: rgba(255,255,255,0.46); border-radius: 4px;
  padding: 16px 20px; margin: 22px 0;
}
.callout .k {
  font-family: var(--mono); font-size: 8px; letter-spacing: 0.16em;
  text-transform: uppercase; color: var(--soft); display: block; margin-bottom: 7px;
}
.callout p { margin: 0; font-size: 13px; line-height: 1.65; color: var(--muted); }
.callout p + p { margin-top: 8px; }
.badge {
  display: inline-block; font-family: var(--mono); font-size: 8px;
  letter-spacing: 0.06em; text-transform: uppercase; line-height: 1;
  padding: 4px 6px 3px; border: 1px solid var(--rule-solid);
  border-radius: 2px; white-space: nowrap; color: var(--ink);
  background: var(--paper);
}
.badge.core { color: #3f5a3a; border-color: rgba(63,90,58,0.35); background: rgba(63,90,58,0.07); }
.badge.add-on { color: #6d5a1f; border-color: rgba(109,90,31,0.35); background: rgba(109,90,31,0.07); }
.badge.stretch { color: var(--link); border-color: rgba(44,93,138,0.35); background: rgba(44,93,138,0.07); }
.stat-strip {
  display: grid; grid-template-columns: repeat(4, 1fr);
  border-top: 1px solid var(--ink); border-bottom: 1px solid var(--rule);
  margin: 36px 0 0;
}
.stat-strip .stat { padding: 16px 18px 14px; border-left: 1px solid var(--rule); }
.stat-strip .stat:first-child { border-left: 0; padding-left: 0; }
.stat-strip .n {
  display: block; font-family: var(--serif); font-size: 34px;
  line-height: 1; letter-spacing: -0.02em;
}
.stat-strip .l {
  display: block; margin-top: 5px; font-family: var(--mono);
  font-size: 8px; letter-spacing: 0.14em; text-transform: uppercase; color: var(--soft);
}
.api-table td:first-child { width: 66px; white-space: nowrap; }
.api-table td:nth-child(2) { white-space: nowrap; }
.api-table .path {
  font-family: var(--mono); font-size: 11.5px; color: var(--ink);
  letter-spacing: -0.01em;
}
.api-table td:last-child { font-size: 11.5px; }
caption {
  caption-side: top; text-align: left; padding-bottom: 8px;
  font-family: var(--mono); font-size: 8px; letter-spacing: 0.14em;
  text-transform: uppercase; color: var(--soft);
}
.mini-note {
  font-family: var(--mono); font-size: 9px; line-height: 1.6;
  letter-spacing: 0.03em; color: var(--soft); margin-top: 10px;
}
.link-row { display: flex; gap: 18px; flex-wrap: wrap; margin-top: 18px; }
.link-row a {
  font-family: var(--mono); font-size: 9px; letter-spacing: 0.1em;
  text-transform: uppercase; color: var(--link); text-decoration: none;
  border-bottom: 1px solid rgba(44,93,138,0.35); padding-bottom: 3px;
}
.link-row a:hover { border-bottom-color: var(--link); }
.pdf-row { margin-top: 16px; }
.pdf-download {
  display: inline-flex; align-items: center; gap: 9px;
  font-family: var(--mono); font-size: 9px; letter-spacing: 0.08em;
  text-transform: uppercase; color: var(--ink); text-decoration: none;
  border: 1px solid var(--rule-solid); padding: 8px 11px;
  background: rgba(255,255,255,0.5); border-radius: 2px;
}
.pdf-download:hover { border-color: var(--ink); background: var(--white); }
.pdf-download .pdf-tag { color: var(--accent); font-weight: 600; letter-spacing: 0.12em; }
.pdf-download .arrow { color: var(--accent); }

/* ---------- report layout ---------- */
.report-layout {
  display: grid; grid-template-columns: minmax(0, 1fr) 216px;
  gap: 56px; align-items: start; margin-top: 44px;
}
.report-body.prose { max-width: none; margin-top: 0; }
.report-aside {
  position: sticky; top: 22px; border-top: 1px solid var(--ink);
  padding-top: 12px;
}
.report-aside .card-label { margin-bottom: 12px; }
.report-aside nav { display: grid; gap: 7px; }
.report-aside a {
  font-family: var(--mono); font-size: 9px; line-height: 1.5;
  letter-spacing: 0.02em; color: var(--muted); text-decoration: none;
  display: block; border-left: 1px solid transparent; padding-left: 9px;
}
.report-aside a:hover { color: var(--ink); border-left-color: var(--accent); }
.report-aside .aside-rule {
  border-top: 1px solid var(--rule); margin: 14px 0 12px;
}
.report-aside .aside-meta {
  font-family: var(--mono); font-size: 8px; letter-spacing: 0.08em;
  line-height: 1.7; color: var(--soft); text-transform: uppercase;
}
.report-body h2, .report-body h3 { scroll-margin-top: 18px; }
.report-body h2:first-child { margin-top: 0; }
.report-body table { font-size: 11.8px; }
.report-body td, .report-body th { padding: 8px 10px; }
.report-body .table-wrap { margin: 14px 0 20px; }
.report-body pre { font-size: 11.5px; }

/* ---------- API reference ---------- */
.api-mobile-note { display: none; }
.api-group { margin-top: 46px; }
.api-group-head {
  display: flex; align-items: baseline; justify-content: space-between;
  gap: 20px; border-top: 1px solid var(--ink); padding-top: 10px;
  margin-bottom: 4px;
}
.api-group-head h2 {
  font-family: var(--serif); font-weight: 400; font-size: 29px;
  letter-spacing: -0.02em; margin: 0;
}
.api-group-head .count {
  font-family: var(--mono); font-size: 8px; letter-spacing: 0.14em;
  text-transform: uppercase; color: var(--soft); white-space: nowrap;
}
.api-group-desc {
  font-size: 13px; line-height: 1.6; color: var(--muted);
  max-width: 760px; margin: 0 0 12px;
}
.api-table td { vertical-align: top; }
.api-table tr[id] { scroll-margin-top: 24px; }
.api-table .op-id {
  display: block; font-family: var(--mono); font-size: 8px;
  letter-spacing: 0.03em; color: var(--soft); margin-top: 3px;
}
.api-table .auth {
  font-family: var(--mono); font-size: 8px; letter-spacing: 0.06em;
  text-transform: uppercase; color: var(--muted); white-space: nowrap;
}
.api-table .success {
  font-family: var(--mono); font-size: 9px; color: var(--muted);
  white-space: nowrap;
}
.api-deep {
  display: grid; grid-template-columns: 1fr 1fr; gap: 16px;
  margin-top: 26px;
}
.api-deep .card { background: rgba(255,255,255,0.5); }
.api-deep .card h3 { font-family: var(--serif); font-size: 24px; font-weight: 400; }
.api-deep .card .mono { margin-bottom: 10px; }
.api-deep .card pre { margin: 10px 0 0; font-size: 10.5px; padding: 14px 16px; }
.api-deep .card .method { margin-right: 6px; }
.schema-grid { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 12px; }
.schema-chip {
  font-family: var(--mono); font-size: 8.5px; letter-spacing: 0.02em;
  color: var(--muted); border: 1px solid var(--rule); border-radius: 2px;
  padding: 4px 6px; background: rgba(255,255,255,0.45);
}
.op-index { display: grid; gap: 8px; }
.op-index a {
  display: flex; gap: 10px; align-items: baseline; text-decoration: none;
  color: var(--muted); font-size: 12.5px;
}
.op-index a:hover { color: var(--ink); }
.op-index .method { flex: 0 0 44px; }
.op-index .path { font-family: var(--mono); font-size: 10.5px; color: var(--ink); }

/* ---------- extra editorial bits ---------- */
.hero-em { color: var(--accent); font-style: italic; }
.section-note {
  font-family: var(--mono); font-size: 9px; letter-spacing: 0.04em;
  color: var(--soft); margin-top: 10px;
}
.band-strip {
  display: grid; grid-template-columns: repeat(4, 1fr);
  border: 1px solid var(--rule); border-radius: 6px; overflow: hidden;
  margin: 24px 0 28px;
}
.band-strip div { padding: 16px 18px; border-left: 1px solid var(--rule); }
.band-strip div:first-child { border-left: 0; }
.band-strip .k {
  font-family: var(--mono); font-size: 8px; letter-spacing: 0.14em;
  text-transform: uppercase; color: var(--soft); display: block; margin-bottom: 5px;
}
.band-strip .v { font-family: var(--serif); font-size: 22px; line-height: 1; display: block; }
.band-strip .d { font-size: 10.5px; line-height: 1.45; color: var(--muted); margin-top: 6px; display: block; }
.rule-table td:first-child { font-family: var(--mono); font-size: 10px; white-space: nowrap; }
.step-table td:first-child {
  font-family: var(--mono); font-size: 9px; color: var(--accent);
  width: 42px; white-space: nowrap;
}
.step-table td:nth-child(2) { color: var(--ink); white-space: nowrap; }
.step-table td:nth-child(3) { font-family: var(--mono); font-size: 10px; white-space: nowrap; }
.kv { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 18px; }
.kv .card { padding: 16px 18px; }
.kv .card h3 { font-size: 13px; }
.path-row {
  display: grid; grid-template-columns: 54px 1.1fr 1.6fr; gap: 16px;
  align-items: start; border-top: 1px solid var(--rule); padding: 14px 0;
}
.path-row:last-child { border-bottom: 1px solid var(--rule); }
.path-row .n {
  font-family: var(--mono); font-size: 9px; letter-spacing: 0.1em;
  color: var(--accent); padding-top: 2px;
}
.path-row h3 { font-size: 14px; font-weight: 600; margin-bottom: 3px; }
.path-row p { font-size: 12px; line-height: 1.6; color: var(--muted); }
.path-row a { color: var(--link); text-decoration: none; border-bottom: 1px solid rgba(44,93,138,0.3); }

/* ---------- responsive ---------- */
@media (max-width: 980px) {
  .report-layout { grid-template-columns: minmax(0, 1fr); gap: 24px; }
  .report-aside { display: none; }
  .diagram-hint { display: inline; }
  .api-deep { grid-template-columns: 1fr; }
  .band-strip { grid-template-columns: 1fr 1fr; }
  .band-strip div:nth-child(3) { border-left: 0; }
  .band-strip div:nth-child(n+3) { border-top: 1px solid var(--rule); }
  .cards, .cards.four { grid-template-columns: 1fr 1fr; }
  .cards .card:last-child { grid-column: span 2; }
  .toc-grid, .toc-grid.four { grid-template-columns: 1fr 1fr; }
  .toc-grid .wide { grid-column: span 2; }
  .manifest { grid-template-columns: 1fr 1fr; }
  .index-rule { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 700px) {
  .header-inner, .wrap, .footer-inner { width: calc(100% - 40px); }
  .api-table th:nth-child(4), .api-table td:nth-child(4),
  .api-table th:nth-child(5), .api-table td:nth-child(5) { display: none; }
  .api-table td:nth-child(2) { white-space: normal; }
  .api-table .path { overflow-wrap: anywhere; }
  .api-mobile-note { display: block; }
  .report-body td:first-child { white-space: nowrap; }
  .site-header { padding: 14px 0; }
  .site-nav { gap: 12px; }
  .site-nav a { font-size: 9px; }
  .page { padding: 44px 0 56px; }
  h1 { font-size: clamp(2rem, 10vw, 3rem); }
  .lede { font-size: 17px; }
  .cards, .cards.two, .cards.four, .toc-grid, .toc-grid.four, .manifest, .index-rule { grid-template-columns: 1fr; }
  .cards .card:last-child, .toc-grid .wide { grid-column: auto; }
  .page-nav { grid-template-columns: 1fr; }
  .stat-strip { grid-template-columns: 1fr 1fr; }
  .stat-strip .stat:nth-child(3) { border-left: 0; padding-left: 0; }
  .stat-strip .stat:nth-child(n+3) { border-top: 1px solid var(--rule); }
  .risk-band { grid-template-columns: 1fr 1fr; }
  .risk-band div:nth-child(3) { border-left: 0; }
  .risk-band div:nth-child(n+3) { border-top: 1px solid var(--rule); }
  .prose h2 { font-size: 28px; }
  .path-row { grid-template-columns: 38px 1fr; }
  .path-row p { grid-column: 2; }
}
@media print {
  .site-header, .site-footer, .page-nav, .diagram-hint, .report-aside { display: none; }
  body { background: #fff; }
  .page { padding: 0; }
  .wrap { width: 100%; }
  .report-layout { display: block; margin-top: 24px; }
  .diagram-container { overflow-x: visible; }
  .diagram-container svg { min-width: 0 !important; }
  .card, .callout, .risk-band, .band-strip { break-inside: avoid; }
  table { break-inside: auto; }
  tr { break-inside: avoid; }
}
"""
