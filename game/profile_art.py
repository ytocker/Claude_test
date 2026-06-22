"""Runtime procedural art for the Profile's witty sections — ported from the
locked design-loop generators (tools/) into game/ so the web bundle ships it.

Currently: the Wall of Shame badge (V5 tarnished gem-frame + V1 recessed
channel), its demeaning glyph library, and the three-tier value ladder
(bronze < silver < gold by whole-disc value, colourblind-safe). The crystal
ball / vending machine / Beakon curio art lands here as those get wired in.
"""
from __future__ import annotations

import math

import pygame

from game.hud import _font, _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP
from game.draw import NEAR_BLACK, WHITE, lerp_color, rounded_rect
from game.store import _vgrad_panel

# Tier reads by WHOLE-DISC VALUE first: bronze ~66 / silver ~100 / gold ~135
# luma, ≥25 apart so it survives grayscale + a squint. The gem stays the
# brightest member of each tier so the one bold base-gem cue pops on its disc.
_TARNISH = {
    "bronze": {"rim": (120, 84, 58), "face": (84, 58, 40), "deep": (44, 30, 21),
               "gem": (172, 116, 74), "patina": (92, 116, 92)},
    "silver": {"rim": (130, 134, 144), "face": (94, 98, 110), "deep": (50, 54, 64),
               "gem": (186, 192, 206), "patina": (96, 116, 120)},
    "gold": {"rim": (196, 172, 112), "face": (166, 142, 86), "deep": (88, 72, 36),
             "gem": (240, 220, 158), "patina": (118, 120, 86)},
}

_LOCK_FACE = (66, 64, 76)
_LOCK_GLYPH_INK = (96, 96, 110)
_LOCK_GLYPH_DIM = (78, 78, 92)
_LOCK_RIM = (108, 122, 150)
_LOCK_RIM_IN = (78, 88, 112)


def _glyph(surf, cx, cy, r, kind, ink, dim):
    """The demeaning icons — high-contrast ink (near the disc's darkest) over a
    brighter fill, so the glyph (the joke) is the strongest contrast in the disc."""
    lw = max(2, int(r) // 8)
    if kind == "egg":
        pygame.draw.ellipse(surf, dim, (cx - r * 0.6, cy - r * 0.78, r * 1.2, r * 1.56))
        pygame.draw.ellipse(surf, ink, (cx - r * 0.6, cy - r * 0.78, r * 1.2, r * 1.56), lw)
        pygame.draw.ellipse(surf, ink, (cx - r * 0.24, cy - r * 0.34, r * 0.48, r * 0.68),
                            max(1, lw - 1))
    elif kind == "icarus":
        for a in range(8):
            ang = a * math.pi / 4
            pygame.draw.line(surf, ink,
                             (cx + math.cos(ang) * r * 0.42, cy - r * 0.2 + math.sin(ang) * r * 0.42),
                             (cx + math.cos(ang) * r * 0.66, cy - r * 0.2 + math.sin(ang) * r * 0.66), lw)
        pygame.draw.circle(surf, dim, (int(cx), int(cy - r * 0.2)), int(r * 0.42))
        pygame.draw.circle(surf, ink, (int(cx), int(cy - r * 0.2)), int(r * 0.42), lw)
        fx, fy = cx + r * 0.5, cy + r * 0.55
        pygame.draw.line(surf, ink, (fx - r * 0.18, fy - r * 0.22), (fx + r * 0.12, fy + r * 0.2), lw)
    elif kind == "humming":
        pygame.draw.ellipse(surf, dim, (cx - r * 0.28, cy - r * 0.3, r * 0.56, r * 0.7))
        pygame.draw.ellipse(surf, ink, (cx - r * 0.28, cy - r * 0.3, r * 0.56, r * 0.7), lw)
        pygame.draw.line(surf, ink, (cx + r * 0.2, cy - r * 0.2), (cx + r * 0.7, cy - r * 0.34), lw)
        for s in range(3):
            yy = cy - r * 0.45 + s * r * 0.42
            pygame.draw.line(surf, ink, (cx - r * 0.7, yy), (cx - r * 0.28, yy + r * 0.08),
                             max(1, lw - 1))
    elif kind == "stopwatch":
        pygame.draw.circle(surf, dim, (int(cx), int(cy + r * 0.08)), int(r * 0.62))
        pygame.draw.circle(surf, ink, (int(cx), int(cy + r * 0.08)), int(r * 0.62), lw)
        pygame.draw.line(surf, ink, (cx, cy - r * 0.62), (cx, cy - r * 0.82), lw)
        pygame.draw.rect(surf, ink, (cx - r * 0.16, cy - r * 0.9, r * 0.32, r * 0.12))
        ang = -math.pi / 2 + 2 * math.pi * (2 / 12)
        pygame.draw.line(surf, ink, (cx, cy + r * 0.08),
                         (cx + math.cos(ang) * r * 0.42, cy + r * 0.08 + math.sin(ang) * r * 0.42), lw)
    elif kind == "denial":
        pts = []
        for i in range(10):
            ang = -math.pi / 2 + i * math.pi / 5
            rr = r * 0.62 if i % 2 == 0 else r * 0.26
            pts.append((cx + math.cos(ang) * rr, cy + math.sin(ang) * rr))
        pygame.draw.polygon(surf, dim, pts)
        pygame.draw.polygon(surf, ink, pts, lw)
        d = r * 0.34
        pygame.draw.line(surf, ink, (cx - d, cy - d), (cx + d, cy + d), lw + 1)
        pygame.draw.line(surf, ink, (cx + d, cy - d), (cx - d, cy + d), lw + 1)
    elif kind == "loop":
        rect = pygame.Rect(cx - r * 0.5, cy - r * 0.5, r, r)
        pygame.draw.arc(surf, ink, rect, math.radians(40), math.radians(330), lw)
        ax, ay = cx + math.cos(math.radians(40)) * r * 0.5, cy - math.sin(math.radians(40)) * r * 0.5
        pygame.draw.polygon(surf, ink, [(ax, ay), (ax - r * 0.2, ay - r * 0.05),
                                        (ax - r * 0.02, ay + r * 0.22)])
    elif kind == "fry":
        pygame.draw.line(surf, ink, (cx - r * 0.32, cy + r * 0.6), (cx - r * 0.12, cy - r * 0.66), lw + 1)
        pygame.draw.line(surf, ink, (cx + r * 0.32, cy + r * 0.6), (cx + r * 0.12, cy - r * 0.66), lw + 1)
        pygame.draw.line(surf, dim, (cx, cy + r * 0.6), (cx, cy - r * 0.7), lw + 1)
        for s in range(-2, 3):
            yy = cy + s * r * 0.22
            pygame.draw.line(surf, ink, (cx - r * 0.28, yy + r * 0.05), (cx + r * 0.28, yy - r * 0.05),
                             max(1, lw - 1))
    elif kind == "scrooge":
        pygame.draw.circle(surf, dim, (int(cx), int(cy)), int(r * 0.64))
        pygame.draw.circle(surf, ink, (int(cx), int(cy)), int(r * 0.64), lw)
        sf = _font(max(10, int(r * 0.95)), True)
        surf.blit(sf.render("$", True, ink), sf.render("$", True, ink).get_rect(center=(cx, cy)))
        pygame.draw.line(surf, ink, (cx - r * 0.72, cy + r * 0.72), (cx + r * 0.72, cy - r * 0.72), lw + 2)
    elif kind == "tomb":
        rect = pygame.Rect(cx - r * 0.5, cy - r * 0.55, r * 1.0, r * 1.2)
        pygame.draw.rect(surf, dim, rect, border_top_left_radius=int(r * 0.5),
                         border_top_right_radius=int(r * 0.5))
        pygame.draw.rect(surf, ink, rect, lw, border_top_left_radius=int(r * 0.5),
                         border_top_right_radius=int(r * 0.5))
        nf = _font(max(10, int(r * 0.62)), True)
        surf.blit(nf.render("49", True, ink), nf.render("49", True, ink).get_rect(center=(cx, cy - r * 0.02)))
    elif kind == "ghostwall":
        pygame.draw.line(surf, ink, (cx + r * 0.6, cy - r * 0.8), (cx + r * 0.6, cy + r * 0.8), lw + 1)
        gx = cx - r * 0.05
        pygame.draw.ellipse(surf, dim, (gx - r * 0.5, cy - r * 0.55, r * 0.95, r * 1.0))
        pygame.draw.ellipse(surf, ink, (gx - r * 0.5, cy - r * 0.55, r * 0.95, r * 1.0), lw)
        pygame.draw.circle(surf, ink, (int(gx - r * 0.16), int(cy - r * 0.1)), max(1, lw))
        pygame.draw.circle(surf, ink, (int(gx + r * 0.18), int(cy - r * 0.1)), max(1, lw))
    elif kind == "oneway":
        tri = [(cx - r * 0.5, cy - r * 0.55), (cx + r * 0.55, cy - r * 0.1), (cx - r * 0.1, cy + r * 0.55)]
        pygame.draw.polygon(surf, dim, tri)
        pygame.draw.polygon(surf, ink, tri, lw)


def _disc(surf, cx, cy, r, tier, locked):
    t = _TARNISH[tier]
    seat = pygame.Surface((r * 2 + 10, r * 2 + 10), pygame.SRCALPHA)
    pygame.draw.circle(seat, (0, 0, 0, 150), (r + 5, r + 5), r + 4)
    surf.blit(seat, (cx - r - 5, cy - r - 5))
    face = _LOCK_FACE if locked else t["face"]
    deep = lerp_color(_LOCK_FACE, NEAR_BLACK, 0.4) if locked else t["deep"]
    rim = lerp_color(_LOCK_FACE, WHITE, 0.2) if locked else t["rim"]
    for i in range(r, 0, -1):
        f = i / r
        c = lerp_color(lerp_color(rim, face, 0.4), deep, (1 - f) ** 1.3)
        pygame.draw.circle(surf, c, (cx, cy), i)
    return t


def _tier_gem(surf, cx, cy, r, t):
    g = t["gem"]
    gr = max(5, int(r / 3.2))
    gy = cy + int(r * 0.58)
    seat = pygame.Surface((gr * 2 + 8, gr * 2 + 8), pygame.SRCALPHA)
    pygame.draw.circle(seat, (0, 0, 0, 150), (gr + 4, gr + 4), gr + 3)
    surf.blit(seat, (cx - gr - 4, gy - gr - 4))
    top, bot, left, right, ctr = (cx, gy - gr), (cx, gy + gr), (cx - gr, gy), (cx + gr, gy), (cx, gy)
    hi = lerp_color(g, WHITE, 0.55)
    sh = lerp_color(g, t["deep"], 0.5)
    dk = lerp_color(t["deep"], NEAR_BLACK, 0.3)
    pygame.draw.polygon(surf, hi, [top, left, ctr])
    pygame.draw.polygon(surf, g, [top, right, ctr])
    pygame.draw.polygon(surf, sh, [left, bot, ctr])
    pygame.draw.polygon(surf, dk, [right, bot, ctr])
    pygame.draw.polygon(surf, lerp_color(t["deep"], NEAR_BLACK, 0.45), [top, right, bot, left], width=1)


def _drip(surf, cx, cy, ink, dim):
    pygame.draw.line(surf, ink, (cx, cy), (cx, cy + 6), 3)
    pygame.draw.circle(surf, dim, (int(cx), int(cy + 8)), 3)
    pygame.draw.circle(surf, ink, (int(cx), int(cy + 8)), 3, 1)


def _rim_patina(surf, cx, cy, r, col, seed):
    state = seed & 0xFFFFFFFF

    def nxt():
        nonlocal state
        state = (1103515245 * state + 12345) & 0x7FFFFFFF
        return state / 0x7FFFFFFF
    for _ in range(5):
        a = nxt() * 2 * math.pi
        d = r * (0.78 + nxt() * 0.16)
        br = max(2, int(r * (0.10 + nxt() * 0.10)))
        blob = pygame.Surface((br * 2, br * 2), pygame.SRCALPHA)
        pygame.draw.circle(blob, (*col, 45), (br, br), br)
        surf.blit(blob, (cx + math.cos(a) * d - br, cy + math.sin(a) * d - br))


def shame_badge(surf, cx, cy, r, tier, kind, locked):
    """The Wall of Shame badge: tarnished gem-frame disc, recessed engraved
    channel, demeaning glyph, and the bold base-gem tier cue. Locked = a dormant
    cool-rim silhouette (the caller draws any progress bar)."""
    t = _disc(surf, cx, cy, r, tier, locked)
    if locked:
        _glyph(surf, cx, cy - 2, r * 0.6, kind, _LOCK_GLYPH_INK, _LOCK_GLYPH_DIM)
        pygame.draw.circle(surf, _LOCK_RIM, (cx, cy), r, 2)
        pygame.draw.circle(surf, _LOCK_RIM_IN, (cx, cy), int(r * 0.84), 1)
        return
    ink = lerp_color(t["deep"], NEAR_BLACK, 0.55)
    glyph_dim = lerp_color(t["gem"], t["face"], 0.35)
    _rim_patina(surf, cx, cy, r, t["patina"], seed=hash(kind) & 0xFFFF)
    pygame.draw.circle(surf, ink, (cx, cy), int(r * 0.84), 2)
    pygame.draw.circle(surf, lerp_color(t["rim"], WHITE, 0.25), (cx, cy), int(r * 0.84) + 2, 1)
    _glyph(surf, cx, cy - 3, r * 0.58, kind, ink, glyph_dim)
    pygame.draw.circle(surf, t["rim"], (cx, cy), r, 3)
    pygame.draw.circle(surf, lerp_color(t["rim"], WHITE, 0.3), (cx, cy), r - 1, 1)
    _tier_gem(surf, cx, cy, r, t)
    _drip(surf, cx, cy + r - 2, ink, t["patina"])


# ── ARCADE curio icons (compact, faithful to the locked element designs) ─────

def curio_crystal(surf, cx, cy, r=18):
    """Teal/gold fortune orb on a gold claw cradle (the locked crystal-ball
    look, idle state) — never purple, so it stays clear of the rarity-gem hue."""
    for dx in (-0.7, 0.0, 0.7):
        pygame.draw.line(surf, (200, 160, 84),
                         (cx + dx * r * 0.5, cy + r * 0.5),
                         (cx + dx * r, cy + r * 1.15), 3)
    pygame.draw.ellipse(surf, (176, 138, 70),
                        (cx - r * 0.85, cy + r * 0.9, r * 1.7, r * 0.55))
    for i in range(r, 0, -1):
        f = i / r
        c = lerp_color((156, 208, 228), (26, 52, 72), (1 - f) ** 1.2)
        pygame.draw.circle(surf, c, (cx, cy), i)
    pygame.draw.circle(surf, (66, 116, 146), (int(cx + r * 0.16), int(cy + r * 0.18)),
                       int(r * 0.42))
    pygame.draw.circle(surf, (236, 250, 255),
                       (int(cx - r * 0.32), int(cy - r * 0.34)), max(2, int(r * 0.18)))
    pygame.draw.circle(surf, (230, 200, 120), (cx, cy), r, 2)


def _capsule(surf, cx, cy, w, h, col):
    """A two-tone gachapon capsule: glossy clear dome over a solid base, one pip
    and a crisp equator seam — the look that says cheap plastic, not gem."""
    top = pygame.Rect(int(cx - w / 2), int(cy - h / 2), int(w), int(h / 2))
    bot = pygame.Rect(int(cx - w / 2), int(cy), int(w), int(h / 2))
    pygame.draw.ellipse(surf, lerp_color(col, WHITE, 0.55), top)
    pygame.draw.ellipse(surf, col, bot)
    pygame.draw.line(surf, lerp_color(col, NEAR_BLACK, 0.3),
                     (cx - w / 2, cy), (cx + w / 2, cy), 1)
    pygame.draw.circle(surf, (255, 255, 255), (int(cx - w * 0.18), int(cy - h * 0.22)),
                       max(1, int(w * 0.1)))


def curio_vending(surf, cx, cy, s=1.0):
    """Obsidian gachapon cabinet: gold-crowned capsule globe, coin slot, and a
    capsule sitting in the chute (the locked vending look)."""
    w, h = int(34 * s), int(46 * s)
    body = pygame.Rect(int(cx - w / 2), int(cy - h / 2), w, h)
    surf.blit(_vgrad_panel(body.w, body.h, 6, (48, 40, 62), (26, 22, 38), 255),
              body.topleft)
    pygame.draw.rect(surf, (150, 130, 190), body, 1, border_radius=6)
    gcy = body.y + int(13 * s)
    gr = int(12 * s)
    pygame.draw.circle(surf, (16, 20, 32), (cx, gcy), gr)
    for ox, oy, col in ((-0.35, -0.1, (224, 96, 96)), (0.28, 0.12, (96, 156, 224)),
                        (-0.08, 0.4, (236, 204, 96)), (0.42, -0.3, (120, 204, 144))):
        _capsule(surf, cx + ox * gr, gcy + oy * gr, gr * 0.62, gr * 0.7, col)
    pygame.draw.circle(surf, (224, 188, 112), (cx, gcy), gr, 2)
    pygame.draw.arc(surf, (236, 204, 120),
                    (cx - gr, gcy - gr - int(5 * s), gr * 2, gr * 2),
                    math.radians(20), math.radians(160), 2)
    pygame.draw.circle(surf, (228, 196, 110), (int(cx + w * 0.22), int(cy + h * 0.04)),
                       max(2, int(3 * s)))
    pygame.draw.rect(surf, (228, 196, 110), (cx - w * 0.28, cy + h * 0.02, w * 0.16, 2))
    chute = pygame.Rect(int(cx - w * 0.32), int(body.bottom - 11 * s), int(w * 0.64),
                        int(8 * s))
    pygame.draw.rect(surf, (14, 12, 20), chute, border_radius=2)
    _capsule(surf, chute.centerx, chute.centery, gr * 0.7, gr * 0.7, (236, 204, 96))


def curio_beakon(surf, cx, cy, s=1.0):
    """Compact bust of the elder-macaw sage: heavy brow, half-lidded deadpan eye,
    hooked beak, single forked wedge-beard, folded wing hint (the locked option-A
    look). Aged/muted scarlet so he's recognizably the game's macaw, grown old."""
    hr = int(16 * s)
    pygame.draw.ellipse(surf, (66, 86, 148),
                        (cx - hr * 1.15, cy + hr * 0.1, hr * 1.7, hr * 1.4))
    pygame.draw.ellipse(surf, (40, 56, 104),
                        (cx - hr * 1.15, cy + hr * 0.1, hr * 1.7, hr * 1.4), 1)
    pygame.draw.line(surf, (236, 196, 96), (cx - hr * 0.5, cy + hr * 0.8),
                     (cx - hr * 0.1, cy + hr * 1.0), 2)            # folded-wing tip
    pygame.draw.circle(surf, (196, 70, 56), (cx, cy), hr)
    pygame.draw.circle(surf, (150, 46, 40), (cx, cy), hr, 1)
    pygame.draw.line(surf, (120, 34, 30), (cx - hr * 0.55, cy - hr * 0.18),
                     (cx + hr * 0.4, cy - hr * 0.42), max(2, int(3 * s)))   # brow
    pygame.draw.circle(surf, (242, 240, 244), (int(cx - hr * 0.06), int(cy - hr * 0.02)),
                       max(2, int(hr * 0.24)))
    pygame.draw.circle(surf, (20, 20, 26), (int(cx), int(cy)), max(1, int(hr * 0.12)))
    pygame.draw.line(surf, (150, 46, 40), (cx - hr * 0.32, cy - hr * 0.14),
                     (cx + hr * 0.22, cy - hr * 0.2), max(2, int(2 * s)))   # heavy lid
    pygame.draw.polygon(surf, (44, 40, 50),
                        [(cx + hr * 0.5, cy - hr * 0.12), (cx + hr * 1.12, cy + hr * 0.12),
                         (cx + hr * 0.5, cy + hr * 0.36)])                  # hooked beak
    pygame.draw.line(surf, (20, 18, 24), (cx + hr * 0.55, cy + hr * 0.12),
                     (cx + hr * 1.0, cy + hr * 0.12), 1)
    by = cy + hr * 0.7
    beard = [(cx - hr * 0.32, by), (cx + hr * 0.32, by), (cx + hr * 0.2, by + hr * 0.85),
             (cx, by + hr * 0.5), (cx - hr * 0.2, by + hr * 0.85)]
    pygame.draw.polygon(surf, (206, 206, 212), beard)
    pygame.draw.polygon(surf, (150, 150, 158), beard, 1)
