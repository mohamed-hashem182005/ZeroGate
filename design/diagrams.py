"""The eleven ZeroGate diagrams, authored as inline SVG figures."""

from __future__ import annotations

from theme import (
    ACCENT,
    ACCENT_TINT,
    INK,
    LINK,
    MUTED,
    PAPER,
    PAPER2,
    SOFT,
    WHITE,
)
from svg import (
    actor_box,
    activation,
    arrow,
    class_box,
    db_table,
    end_dot,
    entity_box,
    fragment,
    hlabel,
    label_mask,
    legend,
    lifeline,
    line,
    message,
    node,
    path,
    rect,
    self_message,
    start_dot,
    state_box,
    svg_close,
    svg_open,
    text,
    text_width,
    vlabel,
    zone,
)


def oval(
    x: float,
    y: float,
    w: float,
    h: float,
    name: str,
    sublabel: str = "",
    focal: bool = False,
) -> str:
    fill = ACCENT_TINT if focal else WHITE
    stroke = ACCENT if focal else INK
    out = [rect(x, y, w, h, fill=PAPER, rx=h / 2)]
    out.append(rect(x, y, w, h, fill=fill, stroke=stroke, sw=1, rx=h / 2))
    out.append(text(x + w / 2, y + h / 2 + (0 if not sublabel else -2), name,
                    size=12, fill=INK, family="'Geist', sans-serif", weight=600,
                    anchor="middle"))
    if sublabel:
        out.append(text(x + w / 2, y + h / 2 + 15, sublabel, size=8.5, fill=MUTED,
                        family="'Geist Mono', monospace", anchor="middle"))
    return "".join(out)


def diamond(
    cx: float,
    cy: float,
    w: float,
    h: float,
    name: str,
    sublabel: str = "",
    focal: bool = False,
) -> str:
    fill = ACCENT_TINT if focal else WHITE
    stroke = ACCENT if focal else INK
    pts = f"{cx},{cy-h/2} {cx+w/2},{cy} {cx},{cy+h/2} {cx-w/2},{cy}"
    out = [f'<polygon points="{pts}" fill="{PAPER}" stroke="none"/>']
    out.append(f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="1"/>')
    out.append(text(cx, cy - 1 if sublabel else cy + 4, name, size=12, fill=INK,
                    family="'Geist', sans-serif", weight=600, anchor="middle"))
    if sublabel:
        out.append(text(cx, cy + 16, sublabel, size=8.5, fill=MUTED,
                        family="'Geist Mono', monospace", anchor="middle"))
    return "".join(out)


def card(cx: float, cy: float, value: str, anchor: str = "middle") -> str:
    """Compact UML/ER multiplicity label."""
    return label_mask(cx, cy, value, size=7, color=INK, anchor=anchor, padding=4)


def component_diagram() -> str:
    slug = "components"
    w, h = 1280, 720
    out = [
        svg_open(
            slug,
            "ZeroGate component architecture",
            "Component view of the ZeroGate zero trust broker: employee and admin clients, enforcement points, decision brain, and protected resources.",
            w,
            h,
        )
    ]

    # zones
    out.append(zone(40, 112, 240, 432, "CLIENT SIDE"))
    out.append(zone(316, 112, 740, 480, "ZEROGATE CONTROL PLANE"))
    out.append(zone(1092, 112, 148, 432, "PROTECTED"))

    # arrows first
    # 1 employee -> web proxy
    out.append(arrow([(240, 224), (344, 224)], color=LINK, marker="arrow-link"))
    out.append(hlabel(292, 224, "HTTPS", color=MUTED))
    # 2 employee -> ssh ca
    out.append(arrow([(240, 260), (296, 260), (296, 388), (344, 388)], color=MUTED))
    out.append(vlabel(296, 324, "CSR · SPA", color=SOFT))
    # 3 employee -> risk (posture)
    out.append(arrow([(152, 176), (152, 92), (740, 92), (740, 160)],
                     color=MUTED, dash="4,3", sw=1))
    out.append(hlabel(446, 92, "DEVICE POSTURE", color=SOFT))
    # 4 proxy -> engine
    out.append(arrow([(448, 264), (448, 300), (616, 300), (616, 340), (640, 340)],
                     color=MUTED))
    out.append(hlabel(532, 300, "ASK", color=SOFT))
    # 5 ca -> engine
    out.append(arrow([(552, 388), (596, 388), (596, 364), (640, 364)], color=MUTED))
    out.append(hlabel(574, 388, "ASK", color=SOFT))
    # 6 engine -> risk
    out.append(arrow([(700, 304), (700, 248)], color=MUTED))
    out.append(vlabel(700, 276, "SCORE", color=SOFT))
    # 7 risk -> engine (return)
    out.append(arrow([(760, 248), (760, 304)], color=MUTED, dash="5,4"))
    out.append(vlabel(760, 276, "REASONS", color=SOFT))
    # 8 engine -> admin
    out.append(arrow([(840, 340), (880, 340)], color=MUTED))
    out.append(hlabel(860, 340, "KILL", color=SOFT))
    # 9 admin -> audit
    out.append(arrow([(960, 400), (960, 480)], color=MUTED))
    out.append(vlabel(960, 440, "LOG", color=SOFT))
    # 10 admin -> proxy (kill / open)
    out.append(arrow([(960, 304), (960, 124), (500, 124), (500, 176)],
                     color=MUTED, dash="4,3"))
    out.append(hlabel(730, 124, "KILL / OPEN", color=SOFT))
    # 11 proxy -> protected
    out.append(arrow([(480, 264), (480, 620), (1172, 620), (1172, 384)],
                     color=LINK, marker="arrow-link"))
    out.append(hlabel(820, 620, "ALLOWED HTTPS", color=MUTED))
    # 12 ca -> protected
    out.append(arrow([(448, 432), (448, 634), (1140, 634), (1140, 384)],
                     color=MUTED))
    out.append(label_mask(800, 646, "30-MIN CERT", size=8, color=SOFT, anchor="middle"))

    # nodes
    out.append(node(64, 176, 176, 96, "Employee Client", "passkey · posture · CLI",
                    "CLIENT", kind="input"))
    out.append(node(64, 336, 176, 88, "Admin Console", "policies · approvals · kill",
                    "ADMIN", kind="input"))
    out.append(node(344, 176, 208, 88, "Web Proxy", "PEP · every request",
                    "ENFORCE"))
    out.append(node(344, 344, 208, 88, "SSH Certificate Authority", "short-lived certs",
                    "ENFORCE"))
    out.append(node(640, 160, 200, 88, "Risk Scorer + ML", "rules + anomaly",
                    "DECIDE"))
    out.append(node(640, 304, 200, 96, "Policy Engine", "allow · deny · step-up",
                    "DECIDE", focal=True))
    out.append(node(880, 304, 160, 96, "Policy Administrator", "sessions · kill switch",
                    "DECIDE"))
    out.append(node(880, 480, 160, 88, "Audit Chain", "hash-chained log",
                    "RECORD", kind="store"))
    out.append(node(1112, 288, 120, 96, "Protected", "web · Linux",
                    "TARGET", kind="external"))

    out.append(legend([
        {"kind": "box", "label": "Focal decision", "fill": ACCENT_TINT, "stroke": ACCENT},
        {"kind": "box", "label": "Service", "fill": WHITE, "stroke": INK},
        {"kind": "box", "label": "Client / input", "fill": "rgba(82,100,108,0.10)", "stroke": SOFT},
        {"kind": "box", "label": "External", "fill": "rgba(31,42,48,0.03)", "stroke": "rgba(31,42,48,0.30)"},
        {"kind": "line", "label": "HTTP / request", "stroke": LINK, "marker": "arrow-link"},
        {"kind": "line", "label": "Async / return", "stroke": MUTED, "dash": "4,3"},
    ], y=684, width=w))
    out.append(svg_close())
    return "".join(out)


def class_diagram() -> str:
    slug = "domain"
    w, h = 1280, 720
    out = [svg_open(
        slug,
        "ZeroGate domain model",
        "UML class diagram of the ZeroGate domain: User, Device, PasskeyCredential, Policy, AccessRequest, Session, and AuditEvent with their operations and cardinalities.",
        w, h,
    )]

    # relationships first
    # User -> Device association
    out.append(arrow([(290, 140), (340, 140)], color=MUTED, marker="uml-open", r=0))
    out.append(card(304, 128, "1"))
    out.append(card(324, 128, "0..*"))
    # Device -> Passkey association
    out.append(arrow([(570, 160), (620, 160)], color=MUTED, marker="uml-open", r=0))
    out.append(card(586, 148, "1"))
    out.append(card(604, 148, "0..*"))
    # User -> AccessRequest association
    out.append(arrow([(140, 240), (140, 300), (280, 300), (280, 430), (340, 430)],
                     color=MUTED, marker="uml-open"))
    out.append(label_mask(140, 292, "REQUESTS", size=8, color=SOFT, anchor="middle"))
    out.append(card(150, 262, "1"))
    out.append(card(320, 418, "0..*"))
    # AccessRequest -> Session association
    out.append(arrow([(570, 430), (620, 430)], color=MUTED, marker="uml-open", r=0))
    out.append(card(586, 418, "0..1"))
    out.append(card(606, 418, "1"))
    # Policy -> Session association
    out.append(arrow([(1015, 240), (1015, 300), (760, 300), (760, 340)],
                     color=MUTED, marker="uml-open"))
    out.append(label_mask(890, 292, "GOVERNS", size=8, color=SOFT, anchor="middle"))
    out.append(card(1025, 262, "1"))
    out.append(card(770, 330, "0..*"))
    # Session -> AuditEvent association
    out.append(arrow([(850, 430), (900, 430)], color=MUTED, marker="uml-open", r=0))
    out.append(card(864, 418, "1"))
    out.append(card(884, 418, "0..*"))
    # User -> AuditEvent association (perimeter)
    out.append(arrow([(60, 120), (40, 120), (40, 600), (1015, 600), (1015, 508)],
                     color=MUTED, marker="uml-open"))
    out.append(vlabel(1015, 554, "ACTS", color=SOFT))

    # classes
    out.append(class_box(60, 72, 230, "User",
                         ["+ id: UUID", "+ email: Email", "+ role: Role", "+ status: Status"],
                         ["+ registerPasskey(): Credential", "+ requestAccess(): Request"],
                         focal=True)[0])
    out.append(class_box(340, 84, 230, "Device",
                         ["+ id: UUID", "+ hostname: String", "+ osVersion: String",
                          "+ encrypted: Boolean", "+ compliant: Boolean"],
                         ["+ reportPosture(): void"])[0])
    out.append(class_box(620, 96, 230, "PasskeyCredential",
                         ["+ id: UUID", "+ aaguid: String", "+ publicKey: Bytes",
                          "+ signCount: Integer", "+ counterOk: Boolean"],
                         ["+ verify(assertion): Boolean"])[0])
    out.append(class_box(900, 72, 230, "Policy",
                         ["+ id: UUID", "+ name: String", "+ effect: Effect",
                          "+ conditions: JSON", "+ version: Integer"],
                         ["+ evaluate(ctx): Decision"])[0])
    out.append(class_box(340, 340, 230, "AccessRequest",
                         ["+ id: UUID", "+ resourceId: UUID", "+ action: Action",
                          "+ requestedTtl: Minutes", "+ state: RequestState"],
                         ["+ approve(approver): void", "+ deny(reason): void"])[0])
    out.append(class_box(620, 340, 230, "Session",
                         ["+ id: UUID", "+ trustScore: Score", "+ state: SessionState",
                          "+ startedAt: Timestamp", "+ expiresAt: Timestamp"],
                         ["+ heartbeat(score): void", "+ kill(reason): void"])[0])
    out.append(class_box(900, 340, 230, "AuditEvent",
                         ["+ id: UUID", "+ seq: BigInteger", "+ type: EventType",
                          "+ prevHash: SHA256", "+ payloadHash: SHA256"],
                         ["+ append(event): Hash"])[0])

    out.append(legend([
        {"kind": "line", "label": "Association", "stroke": MUTED, "marker": "uml-open"},
        {"kind": "line", "label": "Composition", "stroke": INK, "marker": "uml-diamond-filled"},
        {"kind": "line", "label": "Aggregation", "stroke": INK, "marker": "uml-diamond-hollow"},
        {"kind": "line", "label": "Dependency", "stroke": MUTED, "dash": "4,3", "marker": "uml-open"},
        {"kind": "line", "label": "Inheritance", "stroke": INK, "marker": "uml-triangle"},
    ], y=666, width=w))
    out.append(svg_close())
    return "".join(out)


def er_diagram() -> str:
    slug = "er"
    w, h = 960, 720
    out = [svg_open(
        slug,
        "ZeroGate logical data model",
        "Entity relationship model linking users, devices, passkey credentials, resources, policies, access requests, sessions, and audit events.",
        w, h,
    )]

    # relationships first
    # User -> Device
    out.append(arrow([(240, 160), (280, 160)], color=MUTED, marker="arrow", r=0))
    out.append(card(254, 148, "1"))
    out.append(card(272, 148, "N"))
    # Device -> Passkey
    out.append(arrow([(480, 160), (520, 160)], color=MUTED, marker="arrow", r=0))
    out.append(card(494, 148, "1"))
    out.append(card(512, 148, "N"))
    # User -> AccessRequest
    out.append(arrow([(140, 206), (140, 300), (260, 300), (260, 430), (280, 430)],
                     color=MUTED, marker="arrow"))
    out.append(label_mask(140, 292, "REQUESTS", size=8, color=SOFT, anchor="middle"))
    out.append(card(150, 226, "1"))
    out.append(card(270, 418, "N"))
    # Resource -> AccessRequest
    out.append(arrow([(860, 224), (860, 320), (680, 320), (680, 430), (480, 430)],
                     color=MUTED, marker="arrow"))
    out.append(label_mask(770, 312, "TARGETS", size=8, color=SOFT, anchor="middle"))
    out.append(card(872, 244, "1"))
    out.append(card(492, 418, "N"))
    # AccessRequest -> Session
    out.append(arrow([(480, 470), (520, 470)], color=MUTED, marker="arrow", r=0))
    out.append(card(494, 458, "0..1"))
    out.append(card(512, 458, "1"))
    # Policy -> Session
    out.append(arrow([(140, 496), (140, 580), (620, 580), (620, 514)],
                     color=MUTED, marker="arrow"))
    out.append(label_mask(380, 572, "GOVERNS", size=8, color=SOFT, anchor="middle"))
    out.append(card(150, 516, "1"))
    out.append(card(632, 534, "N"))
    # Session -> AuditEvent
    out.append(arrow([(720, 430), (780, 430)], color=MUTED, marker="arrow", r=0))
    out.append(label_mask(750, 418, "RECORDS", size=8, color=SOFT, anchor="middle"))
    out.append(card(730, 448, "1"))
    out.append(card(770, 448, "N"))

    # entities
    out.append(entity_box(40, 88, 200, "USER",
                          ["# id: uuid", "email: text", "role: enum", "status: enum"],
                          focal=True)[0])
    out.append(entity_box(280, 88, 200, "DEVICE",
                          ["# id: uuid", "→ user_id: uuid", "hostname: text",
                           "os_version: text", "encrypted: bool", "compliant: bool"])[0])
    out.append(entity_box(520, 88, 200, "PASSKEY",
                          ["# id: uuid", "→ device_id: uuid", "aaguid: text",
                           "public_key: bytea", "sign_count: int"])[0])
    out.append(entity_box(760, 88, 200, "RESOURCE",
                          ["# id: uuid", "name: text", "kind: enum",
                           "host: text", "sensitivity: enum"])[0])
    out.append(entity_box(40, 360, 200, "POLICY",
                          ["# id: uuid", "name: text", "effect: enum",
                           "conditions: jsonb", "version: int"])[0])
    out.append(entity_box(280, 360, 200, "ACCESS_REQUEST",
                          ["# id: uuid", "→ user_id: uuid", "→ resource_id: uuid",
                           "state: enum", "requested_ttl: interval",
                           "decided_by: uuid"])[0])
    out.append(entity_box(520, 360, 200, "SESSION",
                          ["# id: uuid", "→ user_id: uuid", "→ request_id: uuid",
                           "trust_score: int", "state: enum", "expires_at: timestamptz"])[0])
    out.append(entity_box(780, 360, 180, "AUDIT_EVENT",
                          ["# id: uuid", "seq: bigint", "actor_id: uuid",
                           "session_id: uuid", "type: enum", "prev_hash: bytea"])[0])

    out.append(legend([
        {"kind": "box", "label": "Entity", "fill": WHITE, "stroke": INK},
        {"kind": "box", "label": "Aggregate root", "fill": ACCENT_TINT, "stroke": ACCENT},
        {"kind": "line", "label": "Relationship", "stroke": MUTED, "marker": "arrow"},
        {"kind": "text", "label": "# primary key   → foreign key"},
    ], y=672, width=w))
    out.append(svg_close())
    return "".join(out)


def db_identity() -> str:
    slug = "identity-schema"
    w, h = 1280, 720
    out = [svg_open(
        slug,
        "Identity and device schema",
        "Physical database schema for users, devices, passkeys, and recovery shares, with foreign keys and cascade rules.",
        w, h,
    )]

    # FK edges first
    # devices.user_id -> users.id
    out.append(arrow([(360, 136), (420, 136), (420, 160), (500, 160)],
                     color=MUTED, marker="arrow"))
    out.append(hlabel(460, 160, "CASCADE", color=SOFT))
    # passkeys.device_id -> devices.id
    out.append(arrow([(820, 136), (880, 136), (880, 160), (940, 160)],
                     color=ACCENT, marker="arrow-accent", sw=1.4))
    out.append(hlabel(910, 160, "CASCADE", color=ACCENT))
    # passkeys.user_id -> users.id (denormalised owner lookup)
    out.append(arrow([(200, 88), (200, 56), (960, 56), (960, 84)],
                     color=MUTED, marker="arrow"))
    out.append(hlabel(570, 56, "OWNER", color=SOFT))
    # recovery_shares.user_id -> users.id
    out.append(arrow([(280, 350), (280, 380), (460, 380), (460, 476), (500, 476)],
                     color=MUTED, marker="arrow"))
    out.append(hlabel(370, 380, "CASCADE", color=SOFT))

    out.append(db_table(60, 88, 300, "public.users", [
        {"name": "id", "type": "uuid", "chips": ["PK"]},
        {"name": "email", "type": "citext", "chips": ["UQ", "NN"]},
        {"name": "role", "type": "user_role", "chips": ["NN"]},
        {"name": "status", "type": "user_status", "chips": ["NN"]},
        {"name": "created_at", "type": "timestamptz", "chips": []},
        {"name": "updated_at", "type": "timestamptz", "chips": []},
        {"name": "last_login_at", "type": "timestamptz", "chips": []},
    ], ["uq_users_email", "idx_users_status"])[0])
    out.append(db_table(500, 88, 320, "public.devices", [
        {"name": "id", "type": "uuid", "chips": ["PK"]},
        {"name": "user_id", "type": "uuid", "chips": ["FK", "NN"]},
        {"name": "hostname", "type": "text", "chips": ["NN"]},
        {"name": "os_version", "type": "text", "chips": []},
        {"name": "disk_encrypted", "type": "bool", "chips": ["NN"]},
        {"name": "is_rooted", "type": "bool", "chips": ["NN"]},
        {"name": "compliant", "type": "bool", "chips": ["NN"]},
        {"name": "last_seen_at", "type": "timestamptz", "chips": []},
    ], ["idx_devices_user", "idx_devices_compliant"], accent_header=True)[0])
    out.append(db_table(940, 88, 280, "public.passkeys", [
        {"name": "id", "type": "uuid", "chips": ["PK"]},
        {"name": "device_id", "type": "uuid", "chips": ["FK", "NN"]},
        {"name": "user_id", "type": "uuid", "chips": ["FK", "NN"]},
        {"name": "aaguid", "type": "uuid", "chips": []},
        {"name": "public_key", "type": "bytea", "chips": ["NN"]},
        {"name": "sign_count", "type": "bigint", "chips": ["NN"]},
        {"name": "created_at", "type": "timestamptz", "chips": []},
    ], ["uq_passkeys_credential"])[0])
    out.append(db_table(500, 404, 320, "public.recovery_shares", [
        {"name": "id", "type": "uuid", "chips": ["PK"]},
        {"name": "user_id", "type": "uuid", "chips": ["FK", "NN"]},
        {"name": "share_index", "type": "smallint", "chips": ["NN"]},
        {"name": "share_hash", "type": "bytea", "chips": ["NN"]},
        {"name": "holder_label", "type": "text", "chips": []},
        {"name": "created_at", "type": "timestamptz", "chips": []},
    ], ["uq_recovery_user_index"])[0])

    # annotations
    out.append(label_mask(600, 650, "K-OF-N SHAMIR SHARES · 3 OF 5 REBUILD",
                          size=8, color=SOFT, anchor="middle"))
    out.append(legend([
        {"kind": "box", "label": "Table", "fill": WHITE, "stroke": INK},
        {"kind": "box", "label": "Cascade target", "fill": ACCENT_TINT, "stroke": ACCENT},
        {"kind": "line", "label": "FK · ON DELETE CASCADE", "stroke": MUTED, "marker": "arrow"},
        {"kind": "text", "label": "PK · FK · UQ · NN chips"},
    ], y=690, width=w))
    out.append(svg_close())
    return "".join(out)


def db_access() -> str:
    slug = "access-schema"
    w, h = 1280, 720
    out = [svg_open(
        slug,
        "Access, policy and audit schema",
        "Physical database schema for users, policies, access requests, sessions, and the append-only audit chain, with five foreign keys and explicit cascade rules.",
        w, h,
    )]

    # FK edges first, all drawn parent -> child.
    # users -> access_requests (user_id, CASCADE)
    out.append(arrow([(180, 244), (180, 452), (340, 452)],
                     color=ACCENT, marker="arrow-accent", sw=1.4))
    out.append(vlabel(180, 356, "CASCADE", color=ACCENT))
    # policies -> access_requests (policy_id, RESTRICT)
    out.append(arrow([(540, 310), (540, 320), (700, 320), (700, 500), (680, 500)],
                     color=MUTED, marker="arrow"))
    out.append(label_mask(620, 332, "RESTRICT", size=8, color=SOFT))
    # access_requests -> sessions (request_id, SET NULL)
    out.append(arrow([(680, 540), (730, 540), (730, 476), (740, 476)],
                     color=MUTED, marker="arrow"))
    out.append(label_mask(710, 532, "SET NULL", size=8, color=SOFT))
    # users -> sessions (user_id, CASCADE) over the top, clear of the policy route
    out.append(arrow([(200, 88), (200, 40), (1140, 40), (1140, 452), (1060, 452)],
                     color=MUTED, marker="arrow"))
    out.append(hlabel(600, 40, "CASCADE", color=SOFT))
    # sessions -> audit_events (session_id, SET NULL)
    out.append(arrow([(1060, 428), (1100, 428), (1100, 208), (1040, 208)],
                     color=MUTED, marker="arrow"))
    out.append(label_mask(1085, 320, "SET NULL", size=8, color=SOFT, anchor="end"))

    out.append(db_table(40, 88, 260, "public.users", [
        {"name": "id", "type": "uuid", "chips": ["PK"]},
        {"name": "email", "type": "citext", "chips": ["UQ"]},
        {"name": "role", "type": "user_role", "chips": ["NN"]},
        {"name": "status", "type": "user_status", "chips": ["NN"]},
        {"name": "created_at", "type": "timestamptz", "chips": []},
    ], [], accent_header=True)[0])
    out.append(db_table(340, 88, 320, "public.policies", [
        {"name": "id", "type": "uuid", "chips": ["PK"]},
        {"name": "name", "type": "text", "chips": ["NN"]},
        {"name": "effect", "type": "policy_effect", "chips": ["NN"]},
        {"name": "conditions", "type": "jsonb", "chips": ["NN"]},
        {"name": "version", "type": "int", "chips": ["NN"]},
        {"name": "published_at", "type": "timestamptz", "chips": []},
    ], ["idx_policies_effect"])[0])
    out.append(db_table(720, 88, 320, "public.audit_events", [
        {"name": "id", "type": "uuid", "chips": ["PK"]},
        {"name": "seq", "type": "bigint", "chips": ["UQ", "NN"]},
        {"name": "actor_id", "type": "uuid", "chips": []},
        {"name": "session_id", "type": "uuid", "chips": ["FK"]},
        {"name": "type", "type": "event_type", "chips": ["NN"]},
        {"name": "prev_hash", "type": "bytea", "chips": ["NN"]},
        {"name": "payload_hash", "type": "bytea", "chips": ["NN"]},
    ], ["uq_audit_seq", "idx_audit_session"])[0])
    out.append(db_table(340, 380, 340, "public.access_requests", [
        {"name": "id", "type": "uuid", "chips": ["PK"]},
        {"name": "user_id", "type": "uuid", "chips": ["FK", "NN"]},
        {"name": "resource_id", "type": "uuid", "chips": ["NN"]},
        {"name": "policy_id", "type": "uuid", "chips": ["FK"]},
        {"name": "state", "type": "request_state", "chips": ["NN"]},
        {"name": "requested_ttl", "type": "interval", "chips": ["NN"]},
        {"name": "decided_by", "type": "uuid", "chips": []},
        {"name": "created_at", "type": "timestamptz", "chips": []},
    ], ["idx_requests_state", "idx_requests_user"])[0])
    out.append(db_table(740, 380, 320, "public.sessions", [
        {"name": "id", "type": "uuid", "chips": ["PK"]},
        {"name": "user_id", "type": "uuid", "chips": ["FK", "NN"]},
        {"name": "request_id", "type": "uuid", "chips": ["FK"]},
        {"name": "resource_id", "type": "uuid", "chips": ["NN"]},
        {"name": "trust_score", "type": "smallint", "chips": ["NN"]},
        {"name": "state", "type": "session_state", "chips": ["NN"]},
        {"name": "started_at", "type": "timestamptz", "chips": ["NN"]},
        {"name": "expires_at", "type": "timestamptz", "chips": ["NN"]},
    ], ["idx_sessions_live", "idx_sessions_user"])[0])

    out.append(legend([
        {"kind": "box", "label": "Table", "fill": WHITE, "stroke": INK},
        {"kind": "box", "label": "Identity root", "fill": ACCENT_TINT, "stroke": ACCENT},
        {"kind": "line", "label": "FK · cascade", "stroke": ACCENT, "marker": "arrow-accent"},
        {"kind": "line", "label": "FK · restrict / set null", "stroke": MUTED, "marker": "arrow"},
    ], y=690, width=w))
    out.append(svg_close())
    return "".join(out)
