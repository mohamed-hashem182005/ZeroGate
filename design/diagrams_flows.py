"""Sequence, activity, and state diagrams."""

from __future__ import annotations

from theme import ACCENT, ACCENT_TINT, INK, LINK, MUTED, PAPER, PAPER2, SOFT, WHITE
from svg import (
    actor_box,
    activation,
    arrow,
    end_dot,
    hlabel,
    label_mask,
    legend,
    lifeline,
    message,
    path,
    rect,
    self_message,
    start_dot,
    state_box,
    svg_close,
    svg_open,
    text,
    vlabel,
)
from diagrams import diamond, oval


SEQ_W, SEQ_H = 1040, 760
SEQ_CENTERS = [120, 320, 520, 720, 920]
SEQ_BOXES = [40, 240, 440, 640, 840]


def _seq_header(out: list[str], actors: list[tuple[str, str, str, str, bool]]) -> None:
    for x, (name, sub, tag, kind, focal) in zip(SEQ_BOXES, actors):
        out.append(actor_box(x, 48, 160, name, sub, tag, focal=focal, kind=kind))
    for cx in SEQ_CENTERS:
        out.append(lifeline(cx, 112, 680))


def _seq_legend(out: list[str], extra: list[dict] | None = None) -> None:
    items = [
        {"kind": "line", "label": "Call", "stroke": LINK, "marker": "arrow-link"},
        {"kind": "line", "label": "Return", "stroke": MUTED, "dash": "5,4", "marker": "arrow"},
        {"kind": "line", "label": "Async", "stroke": MUTED, "dash": "5,4", "marker": "arrow-open"},
        {"kind": "box", "label": "Activation", "fill": "rgba(31,42,48,0.06)", "stroke": MUTED},
    ]
    if extra:
        items.extend(extra)
    items.append({"kind": "line", "label": "Headline success", "stroke": ACCENT, "marker": "arrow-accent"})
    out.append(legend(items, y=724, width=SEQ_W))


def sequence_passkey() -> str:
    slug = "seq-passkey"
    out = [svg_open(
        slug,
        "Passkey login sequence",
        "Sequence diagram of a WebAuthn passkey login through the login portal, Policy Engine, risk scorer, and audit chain.",
        SEQ_W, SEQ_H,
    )]
    _seq_header(out, [
        ("Employee + Passkey", "FIDO2 · fingerprint", "USER", "input", False),
        ("Login Portal", "WebAuthn · session", "PORTAL", "backend", False),
        ("Policy Engine", "allow · deny · step-up", "POLICY", "backend", True),
        ("Risk Scorer", "rules + anomaly", "RISK", "backend", False),
        ("Audit Chain", "append-only", "AUDIT", "store", False),
    ])
    # activations
    out.append(activation(120, 152, 248))
    out.append(activation(320, 152, 486))
    out.append(activation(520, 282, 436))
    out.append(activation(720, 322, 380))
    out.append(activation(920, 532, 550))
    # messages
    out.append(message(120, 320, 160, "GET /LOGIN", color=LINK))
    out.append(message(320, 120, 200, "CHALLENGE + OPTIONS", color=MUTED,
                       marker="arrow", dash="5,4"))
    out.append(message(120, 320, 240, "ASSERTION · SIGNED", color=LINK))
    out.append(message(320, 520, 290, "POST /AUTHORIZE", color=LINK))
    out.append(message(520, 720, 330, "SCORE IDENTITY", color=MUTED, marker="arrow"))
    out.append(message(720, 520, 370, "92 · REASONS", color=MUTED, marker="arrow",
                       dash="5,4"))
    out.append(message(520, 320, 420, "ALLOW + SESSION", color=ACCENT,
                       marker="arrow-accent", sw=1.4))
    out.append(message(320, 120, 470, "COOKIE · REDIRECT", color=MUTED,
                       marker="arrow", dash="5,4"))
    out.append(message(320, 920, 540, "APPEND LOGIN", color=MUTED, marker="arrow-open",
                       dash="5,4"))
    _seq_legend(out)
    out.append(svg_close())
    return "".join(out)


def sequence_ssh() -> str:
    slug = "seq-ssh"
    out = [svg_open(
        slug,
        "SSH certificate issuance sequence",
        "Sequence diagram of the SSH helper requesting a short-lived certificate from the SSH CA, with Policy Engine and risk checks before the Linux server accepts it.",
        SEQ_W, SEQ_H,
    )]
    _seq_header(out, [
        ("SSH Helper", "ssh myserver", "CLI", "input", False),
        ("SSH CA", "signs · 30 min", "CA", "backend", False),
        ("Policy Engine", "authorize · obligations", "POLICY", "backend", True),
        ("Risk Scorer", "session risk", "RISK", "backend", False),
        ("Linux Server", "trusts CA only", "HOST", "external", False),
    ])
    out.append(activation(120, 152, 478))
    out.append(activation(320, 202, 470))
    out.append(activation(520, 252, 360))
    out.append(activation(720, 252, 312))
    out.append(activation(920, 532, 632))
    out.append(message(120, 320, 160, "CSR · RESOURCE", color=LINK))
    out.append(message(320, 520, 210, "AUTHORIZE SSH", color=LINK))
    out.append(message(520, 720, 260, "SCORE SESSION", color=MUTED, marker="arrow"))
    out.append(message(720, 520, 300, "84 · OK", color=MUTED, marker="arrow", dash="5,4"))
    out.append(message(520, 320, 350, "ALLOW · TTL 30M", color=MUTED, marker="arrow",
                       dash="5,4"))
    out.append(self_message(320, 400, "SIGN · 30M", color=MUTED))
    out.append(message(320, 120, 460, "SIGNED CERT · 30M", color=ACCENT,
                       marker="arrow-accent", dash="5,4", sw=1.4))
    out.append(message(120, 920, 520, "SSH · CERT", color=LINK))
    out.append(self_message(920, 570, "VERIFY CA", color=MUTED))
    out.append(message(920, 120, 630, "SESSION OPEN", color=MUTED, marker="arrow",
                       dash="5,4"))
    _seq_legend(out)
    out.append(svg_close())
    return "".join(out)


def sequence_jit() -> str:
    slug = "seq-jit"
    out = [svg_open(
        slug,
        "Just-in-time approval sequence",
        "Sequence diagram of an employee requesting just-in-time access, the Policy Engine returning approval-required, and an approver granting a thirty-minute session.",
        SEQ_W, SEQ_H,
    )]
    _seq_header(out, [
        ("Employee", "access request", "USER", "input", False),
        ("Login Portal", "JIT queue", "PORTAL", "backend", False),
        ("Policy Engine", "approval policy", "POLICY", "backend", True),
        ("Approver", "admin console", "ADMIN", "input", False),
        ("Audit Chain", "append-only", "AUDIT", "store", False),
    ])
    out.append(activation(120, 152, 510))
    out.append(activation(320, 152, 510))
    # Two activations keep the portal-to-approver messages clear of the
    # Policy Engine bar while it is not executing.
    out.append(activation(520, 195, 260))
    out.append(activation(520, 390, 460))
    out.append(activation(720, 292, 358))
    out.append(activation(920, 552, 570))
    out.append(message(120, 320, 160, "POST /ACCESS-REQUESTS", color=LINK))
    out.append(message(320, 520, 205, "EVALUATE · JIT", color=LINK))
    out.append(message(520, 320, 250, "APPROVAL REQUIRED · 58", color=MUTED,
                       marker="arrow", dash="5,4"))
    out.append(message(320, 720, 300, "NOTIFY · QUEUE", color=MUTED,
                       marker="arrow-open", dash="5,4"))
    out.append(message(720, 320, 350, "APPROVE · REASON", color=LINK))
    out.append(message(320, 520, 400, "RESOLVE APPROVAL", color=LINK))
    out.append(message(520, 320, 450, "ALLOW · GRANT", color=ACCENT,
                       marker="arrow-accent", sw=1.4))
    out.append(message(320, 120, 500, "ACCESS GRANTED · 30M", color=MUTED,
                       marker="arrow", dash="5,4"))
    out.append(message(520, 920, 560, "APPEND REQUEST", color=MUTED,
                       marker="arrow-open", dash="5,4"))
    _seq_legend(out)
    out.append(svg_close())
    return "".join(out)


def sequence_kill() -> str:
    slug = "seq-kill"
    out = [svg_open(
        slug,
        "Mid-session kill sequence",
        "Sequence diagram of a device posture change and anomaly dropping the trust score below forty, triggering the Policy Administrator to kill the live session and audit the event.",
        SEQ_W, SEQ_H,
    )]
    _seq_header(out, [
        ("Employee Device", "posture agent", "DEVICE", "input", False),
        ("Risk Scorer", "rules + anomaly", "RISK", "backend", False),
        ("Policy Engine", "re-evaluate", "POLICY", "backend", True),
        ("Policy Administrator", "proxy · kill switch", "ADMIN", "backend", False),
        ("Audit Chain", "append-only", "AUDIT", "store", False),
    ])
    out.append(activation(120, 152, 170))
    out.append(activation(320, 152, 270))
    out.append(activation(520, 252, 380))
    out.append(activation(720, 362, 550))
    out.append(activation(920, 532, 550))
    out.append(message(120, 320, 160, "POSTURE · DISK OFF", color=MUTED,
                       marker="arrow-open", dash="5,4"))
    out.append(self_message(320, 210, "RECOMPUTE · 34", color=MUTED))
    out.append(message(320, 520, 260, "TRUST DROP · 34", color=LINK))
    out.append(self_message(520, 310, "RE-EVALUATE", color=MUTED))
    out.append(message(520, 720, 370, "KILL · SCORE <40", color=ACCENT,
                       marker="arrow-accent", sw=1.4))
    out.append(self_message(720, 420, "CLOSE AT PROXY", color=MUTED))
    out.append(message(720, 120, 480, "SESSION TERMINATED", color=MUTED,
                       marker="arrow-open", dash="5,4"))
    out.append(message(720, 920, 540, "APPEND KILL", color=MUTED,
                       marker="arrow-open", dash="5,4"))
    _seq_legend(out)
    out.append(svg_close())
    return "".join(out)


def activity_policy() -> str:
    slug = "policy-flow"
    w, h = 960, 860
    out = [svg_open(
        slug,
        "Policy Engine decision logic",
        "Activity diagram of the Policy Engine: hard gates, rule and ML scoring, policy evaluation, and the four trust bands that produce allow, step-up, approval, or deny.",
        w, h,
    )]
    # transitions first
    out.append(arrow([(480, 96), (480, 136)], color=MUTED))
    out.append(arrow([(600, 192), (760, 192)], color=MUTED))
    out.append(hlabel(680, 192, "NO", color=SOFT))
    out.append(arrow([(480, 248), (480, 304)], color=MUTED))
    out.append(vlabel(480, 276, "YES", color=SOFT))
    out.append(arrow([(480, 368), (480, 408)], color=MUTED))
    # policy no -> deny via right spine
    out.append(arrow([(600, 464), (940, 464), (940, 192), (920, 192)], color=MUTED))
    out.append(hlabel(760, 464, "NO", color=SOFT))
    out.append(arrow([(480, 520), (480, 560)], color=MUTED))
    out.append(vlabel(480, 540, "YES", color=SOFT))
    # trust -> allow
    out.append(arrow([(340, 620), (200, 620), (200, 728)], color=MUTED))
    out.append(hlabel(270, 620, "80–100", color=SOFT))
    # trust -> approval / step-up
    out.append(arrow([(480, 680), (480, 724)], color=MUTED))
    out.append(vlabel(480, 702, "40–79", color=SOFT))
    # trust -> deny
    out.append(arrow([(620, 620), (800, 620), (800, 728)], color=MUTED))
    out.append(hlabel(690, 620, "<40", color=SOFT))
    # approval -> allow
    out.append(arrow([(380, 756), (280, 756)], color=MUTED))
    out.append(hlabel(330, 756, "APPROVED", color=SOFT))

    # nodes
    out.append(oval(400, 48, 160, 48, "Request received"))
    out.append(diamond(480, 192, 240, 112, "Hard gates pass?",
                       "identity · device · resource"))
    out.append(oval(760, 164, 160, 56, "Deny / kill", "hard gate"))
    out.append(rect(380, 304, 200, 64, fill=WHITE, stroke=INK, sw=1, rx=6))
    out.append(text(480, 328, "Score the request", size=12, fill=INK,
                    family="'Geist', sans-serif", weight=600, anchor="middle"))
    out.append(text(480, 346, "rules + ML anomaly", size=8.5, fill=MUTED,
                    family="'Geist Mono', monospace", anchor="middle"))
    out.append(diamond(480, 464, 240, 112, "Policy allows?", "effect · conditions"))
    out.append(diamond(480, 620, 280, 120, "Trust band?", "0–100", focal=True))
    out.append(oval(80, 728, 200, 56, "Allow + obligations", "session · audit"))
    out.append(rect(380, 724, 200, 64, fill=WHITE, stroke=INK, sw=1, rx=6))
    out.append(text(480, 748, "Step-up / JIT", size=12, fill=INK,
                    family="'Geist', sans-serif", weight=600, anchor="middle"))
    out.append(text(480, 766, "60–79 re-auth · 40–59 approve", size=8.5, fill=MUTED,
                    family="'Geist Mono', monospace", anchor="middle"))
    out.append(oval(760, 728, 160, 56, "Deny / kill", "score < 40"))
    out.append(legend([
        {"kind": "box", "label": "Start / terminal", "fill": WHITE, "stroke": INK},
        {"kind": "box", "label": "Decision", "fill": WHITE, "stroke": INK},
        {"kind": "box", "label": "Focal decision", "fill": ACCENT_TINT, "stroke": ACCENT},
        {"kind": "line", "label": "Flow", "stroke": MUTED, "marker": "arrow"},
    ], y=832, width=w))
    out.append(svg_close())
    return "".join(out)


# ---------------------------------------------------------------------------
# State machines
# ---------------------------------------------------------------------------

def state_session() -> str:
    slug = "state-session"
    w, h = 1000, 620
    out = [svg_open(
        slug,
        "Session lifecycle",
        "State machine for a ZeroGate session: active, step-up, suspended, killed, and expired, with score-band transitions and a terminal state.",
        w, h,
    )]
    # transitions
    out.append(arrow([(76, 284), (140, 284)], color=MUTED))
    out.append(label_mask(108, 272, "AUTHORIZE", size=8, color=SOFT))
    out.append(arrow([(320, 264), (380, 264), (380, 132), (420, 132)], color=MUTED))
    out.append(vlabel(380, 198, "60–79", color=SOFT))
    out.append(arrow([(420, 140), (350, 140), (350, 224), (300, 224), (300, 240)],
                     color=MUTED, dash="5,4"))
    out.append(label_mask(340, 176, "RE-AUTH", size=8, color=SOFT, anchor="end"))
    out.append(arrow([(320, 304), (360, 304), (360, 380), (420, 380)], color=MUTED))
    out.append(vlabel(360, 342, "40–59", color=SOFT))
    out.append(arrow([(510, 424), (510, 480), (300, 480), (300, 328)], color=MUTED,
                     dash="5,4"))
    out.append(hlabel(405, 480, "APPROVED", color=SOFT))
    out.append(arrow([(320, 284), (700, 284)], color=MUTED))
    out.append(hlabel(510, 284, "SCORE < 40", color=SOFT))
    out.append(arrow([(600, 380), (780, 380), (780, 308)], color=MUTED))
    out.append(hlabel(690, 380, "DENIED", color=SOFT))
    out.append(arrow([(600, 132), (740, 132), (740, 220)], color=MUTED))
    out.append(vlabel(740, 176, "TIMEOUT", color=SOFT))
    out.append(arrow([(260, 328), (260, 540), (660, 540), (660, 464), (700, 464)],
                     color=MUTED))
    out.append(hlabel(460, 540, "TTL", color=SOFT))
    out.append(arrow([(880, 264), (940, 264), (940, 356)], color=MUTED))
    out.append(arrow([(880, 464), (940, 464), (940, 372)], color=MUTED))

    # states
    out.append(start_dot(70, 284))
    out.append(state_box(140, 240, 180, 88, "Active", "session open"))
    out.append(state_box(420, 88, 180, 88, "Step-up", "re-auth required"))
    out.append(state_box(420, 336, 180, 88, "Suspended", "approval pending"))
    out.append(state_box(700, 220, 180, 88, "Killed", "score < 40 / admin",
                         focal=True))
    out.append(state_box(700, 420, 180, 88, "Expired", "ttl elapsed"))
    out.append(end_dot(940, 364))
    out.append(legend([
        {"kind": "box", "label": "Active state", "fill": WHITE, "stroke": INK},
        {"kind": "box", "label": "Terminal / focal", "fill": ACCENT_TINT, "stroke": ACCENT},
        {"kind": "line", "label": "Transition", "stroke": MUTED, "marker": "arrow"},
        {"kind": "line", "label": "Recovery", "stroke": MUTED, "dash": "5,4"},
    ], y=576, width=w))
    out.append(svg_close())
    return "".join(out)


def state_jit() -> str:
    slug = "state-jit"
    w, h = 1100, 620
    out = [svg_open(
        slug,
        "JIT request lifecycle",
        "State machine for a just-in-time access request: requested, pending, approved, denied, expired, consumed, and closed.",
        w, h,
    )]
    out.append(arrow([(66, 284), (140, 284)], color=MUTED))
    out.append(label_mask(103, 272, "CREATE", size=8, color=SOFT))
    out.append(arrow([(310, 284), (380, 284)], color=MUTED))
    out.append(hlabel(345, 284, "SUBMIT", color=SOFT))
    out.append(arrow([(465, 240), (465, 180), (640, 180)], color=MUTED))
    out.append(hlabel(550, 180, "APPROVE", color=SOFT))
    out.append(arrow([(465, 328), (465, 404), (640, 404)], color=MUTED))
    out.append(hlabel(550, 404, "REJECT", color=SOFT))
    out.append(arrow([(430, 328), (430, 420)], color=MUTED))
    out.append(vlabel(430, 374, "SLA 15M", color=SOFT))
    out.append(arrow([(820, 164), (880, 164)], color=MUTED))
    out.append(hlabel(850, 164, "OPENS", color=SOFT))
    out.append(arrow([(1040, 164), (1060, 164), (1060, 420), (968, 420)], color=MUTED))
    out.append(arrow([(820, 404), (960, 404), (960, 412)], color=MUTED))
    out.append(arrow([(550, 464), (900, 464), (900, 420), (952, 420)], color=MUTED))

    out.append(start_dot(60, 284))
    out.append(state_box(140, 240, 170, 88, "Requested", "form submitted"))
    out.append(state_box(380, 240, 170, 88, "Pending", "approver queue"))
    out.append(state_box(640, 120, 180, 88, "Approved", "grant valid 30m",
                         focal=True))
    out.append(state_box(640, 360, 180, 88, "Denied", "reason recorded"))
    out.append(state_box(380, 420, 170, 88, "Expired", "SLA elapsed"))
    out.append(state_box(880, 120, 160, 88, "Consumed", "session opened"))
    out.append(end_dot(960, 420))
    out.append(legend([
        {"kind": "box", "label": "State", "fill": WHITE, "stroke": INK},
        {"kind": "box", "label": "Approved", "fill": ACCENT_TINT, "stroke": ACCENT},
        {"kind": "line", "label": "Transition", "stroke": MUTED, "marker": "arrow"},
        {"kind": "text", "label": "Approved grants expire after 30 minutes if unused"},
    ], y=566, width=w))
    out.append(svg_close())
    return "".join(out)


def state_device() -> str:
    slug = "state-device"
    w, h = 1100, 620
    out = [svg_open(
        slug,
        "Device trust lifecycle",
        "State machine for a device: unknown, enrolled, compliant, non-compliant, quarantined, revoked, and closed.",
        w, h,
    )]
    out.append(arrow([(66, 284), (140, 284)], color=MUTED))
    out.append(label_mask(103, 272, "FIRST SEEN", size=8, color=SOFT))
    out.append(arrow([(310, 284), (380, 284)], color=MUTED))
    out.append(hlabel(345, 284, "ATTEST", color=SOFT))
    out.append(arrow([(550, 284), (620, 284)], color=MUTED))
    out.append(hlabel(585, 284, "POSTURE", color=SOFT))
    out.append(arrow([(690, 328), (690, 400)], color=MUTED))
    out.append(label_mask(682, 364, "DISK OFF / ROOT", size=8, color=SOFT, anchor="end"))
    out.append(arrow([(730, 400), (730, 328)], color=MUTED, dash="5,4"))
    out.append(vlabel(730, 364, "REMEDIATED", color=SOFT))
    out.append(arrow([(800, 444), (880, 444)], color=MUTED))
    out.append(hlabel(840, 444, "SCORE < 40", color=SOFT))
    out.append(arrow([(965, 488), (965, 540), (330, 540), (330, 312), (380, 312)],
                     color=MUTED))
    out.append(hlabel(640, 540, "RE-ENROLL", color=SOFT))
    out.append(arrow([(800, 284), (880, 284)], color=MUTED))
    out.append(hlabel(840, 284, "LOST", color=SOFT))
    out.append(arrow([(1050, 284), (1080, 284), (1080, 540), (1038, 540)], color=MUTED))
    out.append(hlabel(1060, 540, "REVOKE", color=SOFT))

    out.append(start_dot(60, 284))
    out.append(state_box(140, 240, 170, 88, "Unknown", "first contact"))
    out.append(state_box(380, 240, 170, 88, "Enrolled", "attested"))
    out.append(state_box(620, 240, 180, 88, "Compliant", "posture pass", focal=True))
    out.append(state_box(620, 400, 180, 88, "Non-compliant", "signal raised"))
    out.append(state_box(880, 400, 170, 88, "Quarantined", "blocked"))
    out.append(state_box(880, 240, 170, 88, "Revoked", "lost / stolen"))
    out.append(end_dot(1030, 540))
    out.append(legend([
        {"kind": "box", "label": "State", "fill": WHITE, "stroke": INK},
        {"kind": "box", "label": "Trusted", "fill": ACCENT_TINT, "stroke": ACCENT},
        {"kind": "line", "label": "Transition", "stroke": MUTED, "marker": "arrow"},
        {"kind": "line", "label": "Recovery", "stroke": MUTED, "dash": "5,4"},
    ], y=576, width=w))
    out.append(svg_close())
    return "".join(out)
