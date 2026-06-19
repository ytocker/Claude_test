"""
Procedural achievement badges — the "Courier's Commendation" medallion family.

Every badge is drawn from code (project hard-rule: no PNG sprite sheets). A
badge is a struck-metal medallion: a faceted gold rim lit from the upper-left
(specular hot-spot + lower-right shadow arc, so it reads as a real coin rather
than a flat ring), a beveled inner step, and a recessed enamel field stamped
with an engraved per-key glyph. A twin-laurel sprig sits at the base so the
whole family shares one silhouette.

State is one code path, three looks:
  * unlocked            — warm gold rim + navy enamel (+ amethyst & a rarity
                          sparkle-ring for the hidden "Mysteries" tier).
  * locked (known)      — dormant pewter: desaturated rim, the glyph still
                          embossed faintly so its SHAPE teases the unlock.
  * locked (hidden)     — a riveted iron blank stamped "?", no shape leaked.

Results are cached by ``(icon_key, size, unlocked, hidden)``. ``draw_badge`` is
the only entry point the screen calls; the glyph table is the baseline the
graphics design-loop refines.
"""
from __future__ import annotations

import math
import pygame

from game.draw import lerp_color, blit_glow

# Medallion palette — tuned to the menu's gold-on-navy family.
_RING_HI   = (255, 234, 168)   # specular crest of the rim bevel
_RING_MID  = (236, 186,  72)   # body gold
_RING_LO   = (150, 102,  20)   # shadowed underside of the bevel
_RIM_EDGE  = ( 70,  44,   8)   # thin outer keyline
_FACE_TOP  = ( 44,  32,  92)   # enamel field, lit top
_FACE_BOT  = ( 16,  10,  44)   # enamel field, shadowed base
_STEP_HI   = (255, 226, 150)
_STEP_LO   = (140,  96,  22)
_GLYPH     = (255, 236, 184)   # engraved glyph highlight
_GLYPH_SH  = ( 32,  18,  44)   # engraved glyph inset shadow
_GLYPH_DK  = (150,  96,  20)

# Hidden / secret tier — amethyst enamel reads as "rare".
_SECRET_TOP = ( 74,  40, 116)
_SECRET_BOT = ( 32,  14,  64)

# Dormant (locked, known) — cool pewter that keeps the glyph shape readable.
_LOCK_HI   = (150, 152, 170)
_LOCK_MID  = (104, 106, 126)
_LOCK_LO   = ( 58,  60,  78)
_LOCK_FACE_TOP = ( 40,  42,  58)
_LOCK_FACE_BOT = ( 22,  23,  34)
_LOCK_GLY  = (132, 134, 152)
_LOCK_GLY_SH = ( 18, 19, 28)

# Hidden + locked — a colder riveted-iron blank.
_IRON_HI   = (118, 120, 138)
_IRON_MID  = ( 78,  80,  98)
_IRON_LO   = ( 40,  42,  56)
_IRON_FACE_TOP = ( 30,  31,  44)
_IRON_FACE_BOT = ( 16,  17,  26)

_SS = 4  # supersample for crisp edges, then smoothscale down
_BADGES: dict = {}

# Hidden-tier icon keys get the amethyst enamel + rarity ring automatically so
# the screen needn't pass a flag; mirrors the secret roster in achievements.py.
_HIDDEN_KEYS = frozenset({"genie", "knight", "treasure", "lottery", "rail", "poison"})


# ── glyph primitives (drawn in a 0..1 normalized box, scaled by caller) ───────
#
# Each takes (surf, cx, cy, r, col) and is stroked twice by the builder: a dark
# inset 1px down-right, then the lit colour on top, for an engraved look. So
# glyphs use the passed ``col`` only — no hard-coded fills that would skip the
# emboss. The handful of two-tone props (coin face, magnet poles) keep a small
# accent but still inherit the emboss pass.

def _glyph_pillar(surf, cx, cy, r, col):
    # Two sandstone pillars with a flared capital + base — a temple-gate read,
    # not a tally or a pause icon.
    shaft_w = max(3, int(r * 0.30))
    cap_w = int(shaft_w * 1.6)
    h = int(r * 1.0)
    top = cy - h // 2
    cap_h = max(2, int(r * 0.16))
    gap = int(r * 0.42)
    for sgn in (-1, 1):
        cx_p = cx + sgn * (gap // 2 + cap_w // 2)
        pygame.draw.rect(surf, col, (cx_p - shaft_w // 2, top + cap_h,
                                     shaft_w, h - cap_h * 2))
        for yy in (top, cy + h // 2 - cap_h):  # capital + base
            pygame.draw.rect(surf, col, (cx_p - cap_w // 2, yy, cap_w, cap_h),
                             border_radius=max(1, int(r * 0.05)))


def _glyph_coin(surf, cx, cy, r, col):
    rr = int(r * 0.66)
    pygame.draw.circle(surf, col, (cx, cy), rr, max(3, r // 8))
    f = _glyph_font(int(rr * 1.7))
    g = f.render("$", True, col)
    surf.blit(g, g.get_rect(center=(cx, cy)))


def _glyph_day(surf, cx, cy, r, col):
    rr = int(r * 0.46)
    pygame.draw.circle(surf, col, (cx, cy), rr)
    for i in range(8):
        a = i * math.pi / 4
        x1 = cx + int(math.cos(a) * rr * 1.32)
        y1 = cy + int(math.sin(a) * rr * 1.32)
        x2 = cx + int(math.cos(a) * rr * 1.78)
        y2 = cy + int(math.sin(a) * rr * 1.78)
        pygame.draw.line(surf, col, (x1, y1), (x2, y2), max(2, r // 9))


def _glyph_storm(surf, cx, cy, r, col):
    s = r * 0.92
    pts = [
        (cx - s * 0.10, cy - s * 0.68),
        (cx - s * 0.46, cy + s * 0.06),
        (cx - s * 0.08, cy + s * 0.06),
        (cx - s * 0.30, cy + s * 0.68),
        (cx + s * 0.46, cy - s * 0.20),
        (cx + s * 0.05, cy - s * 0.20),
    ]
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in pts])


def _glyph_nerve(surf, cx, cy, r, col):
    # A sewing needle threaded through its eye — the long shaft + an oval eye
    # near the top, with the thread looping out (Threadneedle / Close Shave).
    nx0, ny0 = cx - int(r * 0.42), cy + int(r * 0.78)
    nx1, ny1 = cx + int(r * 0.30), cy - int(r * 0.78)
    pygame.draw.line(surf, col, (nx0, ny0), (nx1, ny1), max(3, r // 8))
    # eye near the upper end
    ex, ey = cx + int(r * 0.16), cy - int(r * 0.42)
    pygame.draw.ellipse(surf, _GLYPH_SH,
                        (ex - max(2, r // 9), ey - max(3, r // 6),
                         max(4, r // 4), max(6, r // 3)))
    # thread looping through
    pygame.draw.arc(surf, col, (cx - int(r * 0.35), cy - int(r * 0.7),
                                int(r * 0.7), int(r * 0.7)),
                    math.radians(20), math.radians(220), max(2, r // 12))


def _glyph_clock(surf, cx, cy, r, col):
    rr = int(r * 0.66)
    pygame.draw.circle(surf, col, (cx, cy), rr, max(3, r // 9))
    # crown nub so it reads as a stopwatch, not a plain ring
    pygame.draw.rect(surf, col, (cx - max(2, r // 10), cy - rr - int(r * 0.18),
                                 max(4, r // 5), max(3, int(r * 0.18))),
                     border_radius=max(1, r // 14))
    pygame.draw.line(surf, col, (cx, cy), (cx, cy - int(rr * 0.66)), max(2, r // 10))
    pygame.draw.line(surf, col, (cx, cy), (cx + int(rr * 0.52), cy + int(rr * 0.12)), max(2, r // 11))


def _glyph_wing(surf, cx, cy, r, col):
    # Layered macaw wing — three feather strokes for a courier-bird read.
    base = [
        (cx - r * 0.78, cy + r * 0.20),
        (cx + r * 0.10, cy - r * 0.58),
        (cx + r * 0.62, cy - r * 0.10),
        (cx + r * 0.10, cy + r * 0.16),
        (cx + r * 0.52, cy + r * 0.52),
        (cx - r * 0.24, cy + r * 0.50),
    ]
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in base])
    for k in (0.0, 0.30):
        pygame.draw.line(surf, _GLYPH_SH,
                         (int(cx - r * 0.55 + k * r), int(cy + r * 0.18)),
                         (int(cx + r * 0.18 + k * r), int(cy - r * 0.34)),
                         max(2, r // 12))


def _glyph_magnet(surf, cx, cy, r, col):
    rr = int(r * 0.66)
    rect = pygame.Rect(cx - rr, cy - rr, rr * 2, rr * 2)
    pygame.draw.arc(surf, col, rect, math.pi, math.tau, max(5, r // 4))
    leg_w = max(5, r // 4)
    for sgn, tip in ((-1, (210, 70, 60)), (1, (235, 235, 245))):
        x = cx + sgn * rr - leg_w // 2
        pygame.draw.rect(surf, col, (x, cy, leg_w, int(r * 0.5)))
        pygame.draw.rect(surf, tip, (x, cy + int(r * 0.34), leg_w, int(r * 0.16)))


def _glyph_kfc(surf, cx, cy, r, col):
    # A bucket of fries — trapezoid tub + a few sticks.
    tub = [(cx - r * 0.5, cy + r * 0.62), (cx + r * 0.5, cy + r * 0.62),
           (cx + r * 0.36, cy - r * 0.02), (cx - r * 0.36, cy - r * 0.02)]
    pygame.draw.polygon(surf, (214, 74, 60), [(int(x), int(y)) for x, y in tub])
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in tub], max(2, r // 14))
    for dx in (-0.22, 0.0, 0.22):
        x = int(cx + dx * r)
        pygame.draw.rect(surf, col, (x - max(2, r // 14), int(cy - r * 0.58),
                                     max(3, r // 7), int(r * 0.62)),
                         border_radius=max(1, r // 16))


def _glyph_skate(surf, cx, cy, r, col):
    deck = pygame.Rect(int(cx - r * 0.72), int(cy - r * 0.12), int(r * 1.44), max(5, r // 4))
    pygame.draw.rect(surf, col, deck, border_radius=max(3, r // 6))
    for dx in (-0.46, 0.46):
        pygame.draw.line(surf, col, (int(cx + dx * r), int(cy + r * 0.06)),
                         (int(cx + dx * r), int(cy + r * 0.28)), max(2, r // 12))
        pygame.draw.circle(surf, col, (int(cx + dx * r), int(cy + r * 0.4)), max(3, r // 9))


def _glyph_genie(surf, cx, cy, r, col):
    # Magic lamp with a wisp of smoke.
    body = pygame.Rect(int(cx - r * 0.6), int(cy + r * 0.02), int(r * 1.05), int(r * 0.5))
    pygame.draw.ellipse(surf, col, body)
    pygame.draw.polygon(surf, col, [(int(cx + r * 0.42), int(cy + r * 0.1)),
                                    (int(cx + r * 0.82), int(cy - r * 0.14)),
                                    (int(cx + r * 0.5), int(cy + r * 0.26))])
    pygame.draw.circle(surf, col, (int(cx - r * 0.56), int(cy + r * 0.12)), max(3, r // 9))
    # smoke wisp
    pygame.draw.arc(surf, col, (int(cx - r * 0.3), int(cy - r * 0.85),
                                int(r * 0.6), int(r * 0.7)),
                    -math.pi * 0.2, math.pi * 0.9, max(2, r // 12))


def _glyph_knight(surf, cx, cy, r, col):
    # Great-helm with a visor slit + a plume tick.
    helm = pygame.Rect(int(cx - r * 0.5), int(cy - r * 0.5), int(r), int(r * 1.05))
    pygame.draw.rect(surf, col, helm, border_radius=max(3, r // 4))
    pygame.draw.rect(surf, _GLYPH_SH, (int(cx - r * 0.4), int(cy - r * 0.14),
                                       int(r * 0.8), max(3, r // 7)),
                     border_radius=max(1, r // 12))
    pygame.draw.line(surf, col, (cx, cy - int(r * 0.5)),
                     (cx + int(r * 0.18), cy - int(r * 0.98)), max(3, r // 9))


def _glyph_treasure(surf, cx, cy, r, col):
    base = pygame.Rect(int(cx - r * 0.64), int(cy - r * 0.06), int(r * 1.28), int(r * 0.66))
    pygame.draw.rect(surf, col, base, border_radius=max(2, r // 10))
    lid = pygame.Rect(int(cx - r * 0.68), int(cy - r * 0.5), int(r * 1.36), int(r * 0.42))
    pygame.draw.rect(surf, col, lid, border_radius=max(3, r // 7))
    pygame.draw.line(surf, _GLYPH_SH, (int(cx - r * 0.64), int(cy - r * 0.06)),
                     (int(cx + r * 0.64), int(cy - r * 0.06)), max(2, r // 12))
    pygame.draw.circle(surf, _GLYPH_SH, (cx, int(cy + r * 0.06)), max(3, r // 9))
    pygame.draw.circle(surf, col, (cx, int(cy + r * 0.06)), max(3, r // 9), max(1, r // 18))


def _glyph_lottery(surf, cx, cy, r, col):
    # A five-point star burst (jackpot / score milestone).
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rad = r * 0.78 if i % 2 == 0 else r * 0.32
        pts.append((cx + math.cos(ang) * rad, cy + math.sin(ang) * rad))
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in pts])


def _glyph_rail(surf, cx, cy, r, col):
    for dx in (-0.24, 0.24):
        x = int(cx + dx * r)
        pygame.draw.line(surf, col, (x, int(cy - r * 0.72)), (x, int(cy + r * 0.72)),
                         max(3, r // 9))
    for dy in (-0.42, 0.0, 0.42):
        y = int(cy + dy * r)
        pygame.draw.line(surf, col, (int(cx - r * 0.46), y),
                         (int(cx + r * 0.46), y), max(2, r // 12))


def _glyph_poison(surf, cx, cy, r, col):
    # Skull — round cranium, jaw, two dark sockets.
    pygame.draw.circle(surf, col, (cx, cy - int(r * 0.12)), int(r * 0.56))
    jaw = pygame.Rect(int(cx - r * 0.32), int(cy + r * 0.26), int(r * 0.64), int(r * 0.3))
    pygame.draw.rect(surf, col, jaw, border_radius=max(2, r // 10))
    for dx in (-0.24, 0.24):
        pygame.draw.circle(surf, _GLYPH_SH, (int(cx + dx * r), int(cy - r * 0.16)),
                           max(3, r // 7))


def _glyph_powerup(surf, cx, cy, r, col):
    # A four-point sparkle.
    pts = [(cx, cy - r * 0.78), (cx + r * 0.2, cy - r * 0.2),
           (cx + r * 0.78, cy), (cx + r * 0.2, cy + r * 0.2),
           (cx, cy + r * 0.78), (cx - r * 0.2, cy + r * 0.2),
           (cx - r * 0.78, cy), (cx - r * 0.2, cy - r * 0.2)]
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in pts])


_GLYPHS = {
    "pillar": _glyph_pillar,
    "coin": _glyph_coin,
    "day": _glyph_day,
    "score": _glyph_lottery,   # a star for score milestones
    "powerup": _glyph_powerup,
    "magnet": _glyph_magnet,
    "kfc": _glyph_kfc,
    "nerve": _glyph_nerve,
    "clock": _glyph_clock,
    "storm": _glyph_storm,
    "wing": _glyph_wing,
    "skate": _glyph_skate,
    "genie": _glyph_genie,
    "knight": _glyph_knight,
    "treasure": _glyph_treasure,
    "lottery": _glyph_lottery,
    "rail": _glyph_rail,
    "poison": _glyph_poison,
}

_glyph_fonts: dict = {}


def _glyph_font(px: int):
    f = _glyph_fonts.get(px)
    if f is None:
        f = pygame.font.SysFont(None, px, bold=True)
        _glyph_fonts[px] = f
    return f


# ── medallion construction ────────────────────────────────────────────────────

def _draw_rim(surf, cx, cy, R, hi, mid, lo):
    """A lit gold rim: concentric arcs whose tone sweeps from the upper-left
    specular crest round to the lower-right shadow, so the bevel reads as a
    struck coin rather than a flat concentric ring."""
    inner = int(R * 0.72)
    # Base body ring (flat) — fills any seam the directional pass leaves.
    for i in range(R, inner, -1):
        t = (R - i) / max(1, R - inner)
        pygame.draw.circle(surf, lerp_color(hi, lo, t * 0.6 + 0.2), (cx, cy), i)
    # Directional sheen: thin arcs whose colour depends on angle from the light.
    light = math.radians(135)  # upper-left
    steps = 48
    band = (R - inner)
    for seg in range(steps):
        a0 = seg / steps * math.tau
        a1 = (seg + 1) / steps * math.tau
        # cosine falloff: 1 facing the light, 0 facing away
        d = (math.cos(a0 - light) + 1) * 0.5
        col = lerp_color(lo, hi, d ** 1.4)
        rect = pygame.Rect(cx - R + band // 3, cy - R + band // 3,
                           (R - band // 3) * 2, (R - band // 3) * 2)
        pygame.draw.arc(surf, col, rect, -a1, -a0, max(2, band - band // 3))
    pygame.draw.circle(surf, mid, (cx, cy), R, max(2, R // 22))
    pygame.draw.circle(surf, _RIM_EDGE, (cx, cy), R, max(1, R // 36))


def _draw_face(surf, cx, cy, fr, top, bot):
    """Recessed enamel disc — a vertical gradient masked to a circle, with a
    soft inner shadow at the top edge so it reads as sunk below the rim."""
    face = pygame.Surface((fr * 2, fr * 2), pygame.SRCALPHA)
    for yy in range(fr * 2):
        t = yy / max(1, fr * 2 - 1)
        pygame.draw.line(face, lerp_color(top, bot, t), (0, yy), (fr * 2, yy))
    mask = pygame.Surface((fr * 2, fr * 2), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (fr, fr), fr)
    face.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    # inner top shadow for the sunk look
    pygame.draw.arc(face, (0, 0, 0, 120), (2, 2, fr * 2 - 4, fr * 2 - 4),
                    math.radians(20), math.radians(160), max(2, fr // 8))
    surf.blit(face, (cx - fr, cy - fr))


def _draw_step(surf, cx, cy, fr, hi, lo):
    """The bevelled step ring between rim and enamel — a 2px lit/shadow keyline
    that gives the medallion its layered, minted depth."""
    pygame.draw.arc(surf, hi, (cx - fr, cy - fr, fr * 2, fr * 2),
                    math.radians(30), math.radians(210), max(2, fr // 10))
    pygame.draw.arc(surf, lo, (cx - fr, cy - fr, fr * 2, fr * 2),
                    math.radians(210), math.radians(390), max(2, fr // 10))


def _draw_laurel(surf, cx, cy, R, col_l, col_d):
    """A twin-laurel sprig hugging the medallion's base — the shared signature
    that ties the family together. Two arcs of leaf ticks sweeping up the
    lower flanks toward a small bottom knot."""
    leaves = 5
    for sgn in (-1, 1):
        base_a = math.radians(255 if sgn < 0 else 285)  # lower-left / lower-right
        spread = math.radians(58)
        for i in range(leaves):
            f = i / (leaves - 1)
            a = base_a + sgn * spread * f
            rr = R * (1.02 + 0.0 * f)
            bx = cx + math.cos(a) * rr
            by = cy + math.sin(a) * rr
            # each leaf: a short tapered ellipse pointing tangentially up-out
            leaf_len = R * (0.20 - 0.05 * f)
            ang = a - sgn * math.radians(60)
            tip = (bx + math.cos(ang) * leaf_len, by + math.sin(ang) * leaf_len)
            mid = (bx + math.cos(ang) * leaf_len * 0.5 - sgn * math.sin(ang) * leaf_len * 0.4,
                   by + math.sin(ang) * leaf_len * 0.5 + sgn * math.cos(ang) * leaf_len * 0.4)
            pygame.draw.polygon(surf, col_l,
                                [(int(bx), int(by)), (int(mid[0]), int(mid[1])),
                                 (int(tip[0]), int(tip[1]))])
            pygame.draw.line(surf, col_d, (int(bx), int(by)),
                             (int(tip[0]), int(tip[1])), max(1, R // 40))
    # bottom knot
    pygame.draw.circle(surf, col_l, (cx, int(cy + R * 1.0)), max(2, R // 14))
    pygame.draw.circle(surf, col_d, (cx, int(cy + R * 1.0)), max(2, R // 14), max(1, R // 40))


def _stamp_glyph(surf, icon_key, cx, cy, gr, hi, sh):
    """Engrave the glyph: a dark inset pass offset down-right, then the lit
    pass on top — so every glyph in the family shares the same struck-metal
    relief regardless of its silhouette."""
    drawer = _GLYPHS.get(icon_key, _glyph_powerup)
    off = max(1, gr // 18)
    drawer(surf, cx + off, cy + off, gr, sh)
    drawer(surf, cx, cy, gr, hi)


def _build(icon_key: str, size: int, unlocked: bool, hidden: bool) -> pygame.Surface:
    S = _SS
    px = size * S
    surf = pygame.Surface((px, px), pygame.SRCALPHA)
    cx = cy = px // 2
    R = int(px * 0.46)
    is_secret = unlocked and icon_key in _HIDDEN_KEYS

    if unlocked:
        glow_col = (190, 120, 255) if is_secret else (255, 200, 90)
        blit_glow(surf, cx, cy, int(R * 1.12), glow_col, 95)

    if unlocked:
        rim_hi, rim_mid, rim_lo = _RING_HI, _RING_MID, _RING_LO
        face_top, face_bot = (_SECRET_TOP, _SECRET_BOT) if is_secret else (_FACE_TOP, _FACE_BOT)
        step_hi, step_lo = _STEP_HI, _STEP_LO
        laurel_l, laurel_d = _RING_HI, _RING_LO
    elif hidden:
        rim_hi, rim_mid, rim_lo = _IRON_HI, _IRON_MID, _IRON_LO
        face_top, face_bot = _IRON_FACE_TOP, _IRON_FACE_BOT
        step_hi, step_lo = _IRON_HI, _IRON_LO
        laurel_l, laurel_d = _IRON_MID, _IRON_LO
    else:
        rim_hi, rim_mid, rim_lo = _LOCK_HI, _LOCK_MID, _LOCK_LO
        face_top, face_bot = _LOCK_FACE_TOP, _LOCK_FACE_BOT
        step_hi, step_lo = _LOCK_HI, _LOCK_LO
        laurel_l, laurel_d = _LOCK_MID, _LOCK_LO

    # Laurel sits behind the medallion body.
    _draw_laurel(surf, cx, cy, R, laurel_l, laurel_d)
    _draw_rim(surf, cx, cy, R, rim_hi, rim_mid, rim_lo)
    fr = int(R * 0.70)
    _draw_step(surf, cx, cy, fr + max(2, R // 16), step_hi, step_lo)
    _draw_face(surf, cx, cy, fr, face_top, face_bot)

    # Rarity sparkle-ring for the unlocked secret tier — eight twinkles riding
    # just inside the rim so the hidden achievements feel like a trophy.
    if is_secret:
        for i in range(8):
            a = i * math.tau / 8 - math.radians(20)
            sx = cx + int(math.cos(a) * fr * 0.92)
            sy = cy + int(math.sin(a) * fr * 0.92)
            sr = max(2, R // 20)
            pygame.draw.line(surf, _GLYPH, (sx - sr, sy), (sx + sr, sy), max(1, R // 40))
            pygame.draw.line(surf, _GLYPH, (sx, sy - sr), (sx, sy + sr), max(1, R // 40))

    # Glyph (or the lock "?").
    gr = int(R * 0.56)
    if unlocked:
        _stamp_glyph(surf, icon_key, cx, cy, gr, _GLYPH, _GLYPH_SH)
    elif hidden:
        f = _glyph_font(int(R * 1.05))
        for o, c in (((max(1, R // 18), max(1, R // 18)), _IRON_LO), ((0, 0), _IRON_HI)):
            q = f.render("?", True, c)
            surf.blit(q, q.get_rect(center=(cx + o[0], cy + o[1])))
    else:
        # Dormant: the real glyph shape is embossed faintly so it teases the
        # unlock — desaturated, low-contrast, but unmistakably its shape.
        _stamp_glyph(surf, icon_key, cx, cy, gr, _LOCK_GLY, _LOCK_GLY_SH)

    return pygame.transform.smoothscale(surf, (size, size))


def get_badge(icon_key: str, size: int, unlocked: bool,
              hidden: bool = False) -> pygame.Surface:
    key = (icon_key, size, unlocked, hidden)
    s = _BADGES.get(key)
    if s is None:
        s = _build(icon_key, size, unlocked, hidden)
        _BADGES[key] = s
    return s


def draw_badge(surf, icon_key: str, rect: "pygame.Rect", unlocked: bool,
               hidden: bool = False) -> None:
    """Blit a badge centered in ``rect`` (uses the smaller rect dimension).
    ``hidden`` (locked + secret) swaps the dormant pewter look for a riveted
    iron blank so the achievement's shape stays a mystery."""
    size = min(rect.width, rect.height)
    badge = get_badge(icon_key, size, unlocked, hidden and not unlocked)
    surf.blit(badge, badge.get_rect(center=rect.center))
