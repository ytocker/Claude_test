"""
Procedural achievement badges.

Every badge is drawn from code (project hard-rule: no PNG sprite sheets). A
badge is a gold medallion (gradient ring + dark center) stamped with a per-key
glyph; `unlocked=False` desaturates the medallion and swaps the glyph for a
locked "?" so a single code path covers both states. Results are cached by
`(icon_key, size, unlocked)`.

`draw_badge` is the only entry point the screen calls; the glyph table here is
the baseline that the graphics design-loop refines.
"""
from __future__ import annotations

import math
import pygame

from game.draw import lerp_color, blit_glow

# Medallion palette — tuned to the menu's gold-on-navy family.
_RING_HI   = (255, 226, 150)
_RING_LO   = (176, 126,  30)
_FACE_TOP  = ( 70,  52, 120)
_FACE_BOT  = ( 26,  18,  62)
_RIM_DARK  = ( 28,  16,   8)
_GLYPH     = (255, 232, 168)
_GLYPH_DK  = (150,  96,  20)
_LOCK_FACE = ( 40,  40,  58)
_LOCK_RING = ( 92,  92, 110)
_LOCK_GLY  = (120, 120, 140)

_SS = 4  # supersample for crisp edges, then smoothscale down
_BADGES: dict = {}


# ── glyph primitives (drawn in a 0..1 normalized box, scaled by caller) ───────

def _glyph_pillar(surf, cx, cy, r, col):
    w = int(r * 0.34)
    h = int(r * 1.15)
    gap = int(r * 0.30)
    for sgn in (-1, 1):
        x = cx + sgn * (gap // 2 + w // 2) - w // 2
        pygame.draw.rect(surf, col, (x, cy - h // 2, w, h), border_radius=int(r * 0.12))


def _glyph_coin(surf, cx, cy, r, col):
    rr = int(r * 0.62)
    pygame.draw.circle(surf, col, (cx, cy), rr)
    pygame.draw.circle(surf, _RIM_DARK, (cx, cy), rr, max(2, r // 12))
    f = pygame.font.SysFont(None, int(rr * 1.7))
    g = f.render("$", True, _RIM_DARK)
    surf.blit(g, g.get_rect(center=(cx, cy)))


def _glyph_day(surf, cx, cy, r, col):
    rr = int(r * 0.5)
    pygame.draw.circle(surf, col, (cx, cy), rr)
    for i in range(8):
        a = i * math.pi / 4
        x1 = cx + int(math.cos(a) * rr * 1.25)
        y1 = cy + int(math.sin(a) * rr * 1.25)
        x2 = cx + int(math.cos(a) * rr * 1.7)
        y2 = cy + int(math.sin(a) * rr * 1.7)
        pygame.draw.line(surf, col, (x1, y1), (x2, y2), max(2, r // 10))


def _glyph_storm(surf, cx, cy, r, col):
    s = r * 0.9
    pts = [
        (cx - s * 0.10, cy - s * 0.65),
        (cx - s * 0.45, cy + s * 0.08),
        (cx - s * 0.08, cy + s * 0.08),
        (cx - s * 0.28, cy + s * 0.65),
        (cx + s * 0.45, cy - s * 0.18),
        (cx + s * 0.05, cy - s * 0.18),
    ]
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in pts])


def _glyph_nerve(surf, cx, cy, r, col):
    # A needle's eye — two near-touching arcs (threadneedle).
    rr = int(r * 0.6)
    pygame.draw.circle(surf, col, (cx, cy), rr, max(3, r // 9))
    pygame.draw.line(surf, col, (cx, cy - int(r * 0.95)),
                     (cx, cy - rr), max(2, r // 12))


def _glyph_clock(surf, cx, cy, r, col):
    rr = int(r * 0.62)
    pygame.draw.circle(surf, col, (cx, cy), rr, max(3, r // 9))
    pygame.draw.line(surf, col, (cx, cy), (cx, cy - int(rr * 0.7)), max(2, r // 11))
    pygame.draw.line(surf, col, (cx, cy), (cx + int(rr * 0.5), cy), max(2, r // 11))


def _glyph_wing(surf, cx, cy, r, col):
    pts = [
        (cx - r * 0.7, cy + r * 0.15),
        (cx + r * 0.2, cy - r * 0.55),
        (cx + r * 0.6, cy - r * 0.15),
        (cx + r * 0.15, cy + r * 0.1),
        (cx + r * 0.55, cy + r * 0.5),
        (cx - r * 0.2, cy + r * 0.45),
    ]
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in pts])


def _glyph_magnet(surf, cx, cy, r, col):
    rr = int(r * 0.7)
    rect = pygame.Rect(cx - rr, cy - rr, rr * 2, rr * 2)
    pygame.draw.arc(surf, col, rect, math.pi, math.tau, max(4, r // 5))
    leg_w = max(4, r // 5)
    for sgn in (-1, 1):
        x = cx + sgn * rr - (leg_w // 2 if sgn > 0 else -leg_w // 2)
        pygame.draw.rect(surf, (210, 60, 60), (cx + sgn * rr - leg_w // 2, cy, leg_w, int(r * 0.5)))


def _glyph_kfc(surf, cx, cy, r, col):
    # A bucket of fries — trapezoid tub + a few sticks.
    tub = [(cx - r * 0.5, cy + r * 0.6), (cx + r * 0.5, cy + r * 0.6),
           (cx + r * 0.35, cy - r * 0.05), (cx - r * 0.35, cy - r * 0.05)]
    pygame.draw.polygon(surf, (220, 70, 60), [(int(x), int(y)) for x, y in tub])
    for dx in (-0.22, 0.0, 0.22):
        x = int(cx + dx * r)
        pygame.draw.rect(surf, col, (x - max(2, r // 14), int(cy - r * 0.55),
                                     max(3, r // 7), int(r * 0.6)))


def _glyph_skate(surf, cx, cy, r, col):
    deck = pygame.Rect(int(cx - r * 0.7), int(cy - r * 0.1), int(r * 1.4), max(4, r // 5))
    pygame.draw.rect(surf, col, deck, border_radius=max(2, r // 8))
    for dx in (-0.45, 0.45):
        pygame.draw.circle(surf, _GLYPH_DK, (int(cx + dx * r), int(cy + r * 0.35)), max(3, r // 8))


def _glyph_genie(surf, cx, cy, r, col):
    # Magic lamp.
    body = pygame.Rect(int(cx - r * 0.6), int(cy - r * 0.05), int(r * 1.1), int(r * 0.55))
    pygame.draw.ellipse(surf, col, body)
    pygame.draw.polygon(surf, col, [(int(cx + r * 0.45), int(cy + r * 0.05)),
                                    (int(cx + r * 0.8), int(cy - r * 0.25)),
                                    (int(cx + r * 0.55), int(cy + r * 0.2))])
    pygame.draw.circle(surf, col, (int(cx - r * 0.55), int(cy + r * 0.05)), max(3, r // 8))


def _glyph_knight(surf, cx, cy, r, col):
    # Helmet with a visor slit.
    pygame.draw.circle(surf, col, (cx, cy), int(r * 0.62))
    pygame.draw.rect(surf, _RIM_DARK, (int(cx - r * 0.5), int(cy - r * 0.12),
                                       int(r), max(3, r // 8)))
    pygame.draw.line(surf, col, (cx, cy - int(r * 0.62)), (cx, cy - int(r * 0.95)),
                     max(2, r // 10))


def _glyph_treasure(surf, cx, cy, r, col):
    base = pygame.Rect(int(cx - r * 0.62), int(cy - r * 0.1), int(r * 1.24), int(r * 0.7))
    pygame.draw.rect(surf, col, base, border_radius=max(2, r // 10))
    lid = pygame.Rect(int(cx - r * 0.66), int(cy - r * 0.5), int(r * 1.32), int(r * 0.45))
    pygame.draw.rect(surf, _GLYPH_DK, lid, border_radius=max(2, r // 8))
    pygame.draw.circle(surf, _RIM_DARK, (cx, int(cy + r * 0.05)), max(3, r // 9))


def _glyph_lottery(surf, cx, cy, r, col):
    # A seven-point star burst (jackpot).
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rad = r * 0.72 if i % 2 == 0 else r * 0.3
        pts.append((cx + math.cos(ang) * rad, cy + math.sin(ang) * rad))
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in pts])


def _glyph_rail(surf, cx, cy, r, col):
    for dx in (-0.22, 0.22):
        x = int(cx + dx * r)
        pygame.draw.line(surf, col, (x, int(cy - r * 0.7)), (x, int(cy + r * 0.7)),
                         max(3, r // 9))
    for dy in (-0.4, 0.0, 0.4):
        y = int(cy + dy * r)
        pygame.draw.line(surf, _GLYPH_DK, (int(cx - r * 0.45), y),
                         (int(cx + r * 0.45), y), max(2, r // 12))


def _glyph_poison(surf, cx, cy, r, col):
    # Skull-ish: a round face with two dark eyes.
    pygame.draw.circle(surf, col, (cx, cy - int(r * 0.1)), int(r * 0.55))
    pygame.draw.rect(surf, col, (int(cx - r * 0.3), int(cy + r * 0.3),
                                 int(r * 0.6), int(r * 0.25)))
    for dx in (-0.22, 0.22):
        pygame.draw.circle(surf, _RIM_DARK, (int(cx + dx * r), int(cy - r * 0.15)),
                           max(3, r // 8))


def _glyph_powerup(surf, cx, cy, r, col):
    # A four-point sparkle.
    for ang in (0, math.pi / 2):
        for sgn in (-1, 1):
            pass
    pts = [(cx, cy - r * 0.75), (cx + r * 0.2, cy - r * 0.2),
           (cx + r * 0.75, cy), (cx + r * 0.2, cy + r * 0.2),
           (cx, cy + r * 0.75), (cx - r * 0.2, cy + r * 0.2),
           (cx - r * 0.75, cy), (cx - r * 0.2, cy - r * 0.2)]
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


def _build(icon_key: str, size: int, unlocked: bool) -> pygame.Surface:
    S = _SS
    px = size * S
    surf = pygame.Surface((px, px), pygame.SRCALPHA)
    cx = cy = px // 2
    R = px // 2 - S

    ring_hi, ring_lo = (_RING_HI, _RING_LO) if unlocked else (_LOCK_RING, (60, 60, 74))
    face_top, face_bot = (_FACE_TOP, _FACE_BOT) if unlocked else (_LOCK_FACE, (22, 22, 32))

    if unlocked:
        blit_glow(surf, cx, cy, int(R * 1.05), (255, 200, 90), 90)

    # Ring: concentric rings from outer (hi) to inner (lo) for a beveled coin.
    for i in range(R, int(R * 0.74), -1):
        t = (R - i) / max(1, R - int(R * 0.74))
        pygame.draw.circle(surf, lerp_color(ring_hi, ring_lo, t), (cx, cy), i)
    pygame.draw.circle(surf, _RIM_DARK, (cx, cy), R, max(2, S))

    # Inner face — vertical gradient disc.
    fr = int(R * 0.74)
    face = pygame.Surface((fr * 2, fr * 2), pygame.SRCALPHA)
    for yy in range(fr * 2):
        t = yy / max(1, fr * 2 - 1)
        pygame.draw.line(face, lerp_color(face_top, face_bot, t), (0, yy), (fr * 2, yy))
    mask = pygame.Surface((fr * 2, fr * 2), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (fr, fr), fr)
    face.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(face, (cx - fr, cy - fr))

    # Glyph (or lock "?").
    gcol = _GLYPH if unlocked else _LOCK_GLY
    if unlocked:
        drawer = _GLYPHS.get(icon_key, _glyph_powerup)
        drawer(surf, cx, cy, int(R * 0.62), gcol)
    else:
        f = pygame.font.SysFont(None, int(R * 1.1), bold=True)
        q = f.render("?", True, gcol)
        surf.blit(q, q.get_rect(center=(cx, cy)))

    return pygame.transform.smoothscale(surf, (size, size))


def get_badge(icon_key: str, size: int, unlocked: bool) -> pygame.Surface:
    key = (icon_key, size, unlocked)
    s = _BADGES.get(key)
    if s is None:
        s = _build(icon_key, size, unlocked)
        _BADGES[key] = s
    return s


def draw_badge(surf, icon_key: str, rect: "pygame.Rect", unlocked: bool) -> None:
    """Blit a badge centered in ``rect`` (uses the smaller rect dimension)."""
    size = min(rect.width, rect.height)
    badge = get_badge(icon_key, size, unlocked)
    surf.blit(badge, badge.get_rect(center=rect.center))
