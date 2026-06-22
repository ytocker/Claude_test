"""Wall of Shame badge exploration sheet (round 1).

Headless render of 5 medallion-FRAME treatments for the Profile's "anti-
achievement" wall. Each version draws a mini obsidian SHAME panel with a
demeaning title chip + a 2/3-column grid of example badges (mixed earned tiers
plus at least one locked-with-progress), so the frames can be judged AS A WALL.

Procedural-only; reuses the Store/HUD "Obsidian & Gold" primitives so the
explorations sit in the real game's furniture. Writes the combined PNG only.
"""
from __future__ import annotations

import os
import math

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from game.hud import _font, _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP
from game.draw import NEAR_BLACK, WHITE, UI_CREAM, lerp_color, rounded_rect
from game.store import (
    _vgrad_panel, _drop_shadow, _inset_disc, _soft_glow, _gradient_text,
    _OBS_TOP, _OBS_BOT,
)

# ── Tarnished palette ────────────────────────────────────────────────────────
# A shame badge is the desaturated INVERSE of a gold medal: greyed metals that
# survive grayscale yet never read premium. Three parody tiers give the wall
# visual rhythm; each is metal{rim, face, deep} + a muted gem.
_TARNISH = {
    "bronze": {
        "rim":  (138, 104, 74),   "face": (104, 78, 56),
        "deep": (58, 42, 30),     "gem":  (150, 110, 78),
        "patina": (96, 120, 96),  # green-grey verdigris bloom
    },
    "silver": {
        "rim":  (150, 152, 160),  "face": (108, 112, 122),
        "deep": (58, 60, 70),     "gem":  (158, 162, 172),
        "patina": (96, 112, 116),
    },
    "gold": {  # "gold-tarnished" — dull brass, NOT the bright wall-of-fame gold
        "rim":  (158, 134, 78),   "face": (120, 100, 56),
        "deep": (66, 54, 28),     "gem":  (168, 142, 84),
        "patina": (112, 116, 84),
    },
}

_PANEL_BG = ((20, 16, 24), (8, 7, 13))   # even murkier than the store obsidian
_BG_STOPS = ((10, 9, 16), (16, 13, 26), (22, 17, 34))


# ── glyph library (the demeaning icons, drawn in a muted ink) ─────────────────
def _glyph(surf, cx, cy, r, kind, ink, dim):
    """Draw badge ICON `kind` centred on (cx, cy) at radius r, in tarnished ink
    (`ink` line, `dim` fill) — deliberately crude/comic to read as a demerit."""
    lw = max(2, r // 9)

    if kind == "egg":  # The Goose Egg — a big fat zero / egg
        pygame.draw.ellipse(surf, dim, (cx - r * 0.6, cy - r * 0.78,
                                        r * 1.2, r * 1.56))
        pygame.draw.ellipse(surf, ink, (cx - r * 0.6, cy - r * 0.78,
                                        r * 1.2, r * 1.56), lw)
        # inner void so it reads "zero" not "blob"
        pygame.draw.ellipse(surf, ink, (cx - r * 0.24, cy - r * 0.34,
                                        r * 0.48, r * 0.68), max(1, lw - 1))

    elif kind == "icarus":  # sun + tiny falling feather
        for a in range(8):
            ang = a * math.pi / 4
            x0 = cx + math.cos(ang) * r * 0.42
            y0 = cy - r * 0.2 + math.sin(ang) * r * 0.42
            x1 = cx + math.cos(ang) * r * 0.66
            y1 = cy - r * 0.2 + math.sin(ang) * r * 0.66
            pygame.draw.line(surf, ink, (x0, y0), (x1, y1), lw)
        pygame.draw.circle(surf, dim, (int(cx), int(cy - r * 0.2)), int(r * 0.42))
        pygame.draw.circle(surf, ink, (int(cx), int(cy - r * 0.2)),
                           int(r * 0.42), lw)
        # a single feather tumbling away, bottom-right
        fx, fy = cx + r * 0.5, cy + r * 0.55
        pygame.draw.line(surf, ink, (fx - r * 0.18, fy - r * 0.22),
                         (fx + r * 0.12, fy + r * 0.2), lw)
        for s in range(3):
            pygame.draw.line(surf, ink,
                             (fx - r * 0.1 + s * r * 0.08, fy - r * 0.12 + s * r * 0.12),
                             (fx - r * 0.22 + s * r * 0.08, fy - r * 0.04 + s * r * 0.12),
                             max(1, lw - 1))

    elif kind == "hummingbird":  # frantic motion-blur wings
        pygame.draw.ellipse(surf, dim, (cx - r * 0.14, cy - r * 0.3,
                                        r * 0.28, r * 0.66))
        pygame.draw.ellipse(surf, ink, (cx - r * 0.14, cy - r * 0.3,
                                        r * 0.28, r * 0.66), lw)
        # blurred wing arcs, fading out, on both sides
        for side in (-1, 1):
            for i, a in enumerate((255, 150, 80)):
                rr = r * (0.32 + i * 0.16)
                col = lerp_color(dim, _PANEL_BG[1], i / 3.0)
                rect = pygame.Rect(0, 0, rr, rr * 0.7)
                rect.center = (cx + side * rr * 0.55, cy - r * 0.05)
                pygame.draw.arc(surf, col, rect,
                                -0.8 if side > 0 else math.pi - 0.8 + 1.6,
                                0.8 if side > 0 else math.pi + 0.8, max(1, lw - i))
        # long pointed beak
        pygame.draw.line(surf, ink, (cx, cy - r * 0.28),
                         (cx, cy - r * 0.72), lw)

    elif kind == "stopwatch":  # a stopwatch at ~2 seconds
        pygame.draw.circle(surf, dim, (int(cx), int(cy + r * 0.08)),
                           int(r * 0.62))
        pygame.draw.circle(surf, ink, (int(cx), int(cy + r * 0.08)),
                           int(r * 0.62), lw)
        pygame.draw.line(surf, ink, (cx, cy - r * 0.62), (cx, cy - r * 0.82), lw)
        pygame.draw.rect(surf, ink, (cx - r * 0.16, cy - r * 0.9,
                                     r * 0.32, r * 0.12))
        # hand pointing to ~2 o'clock (the "early checkout" tell)
        ang = -math.pi / 2 + 2 * math.pi * (2 / 12)
        pygame.draw.line(surf, ink, (cx, cy + r * 0.08),
                         (cx + math.cos(ang) * r * 0.42,
                          cy + r * 0.08 + math.sin(ang) * r * 0.42), lw)
        pygame.draw.circle(surf, ink, (int(cx), int(cy + r * 0.08)),
                           max(1, lw))

    elif kind == "denial":  # a wasted power-up star with an X
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

    elif kind == "habit":  # a pillar with a loop arrow (creature of habit)
        pygame.draw.rect(surf, dim, (cx - r * 0.22, cy - r * 0.5,
                                     r * 0.44, r * 1.0))
        pygame.draw.rect(surf, ink, (cx - r * 0.22, cy - r * 0.5,
                                     r * 0.44, r * 1.0), lw)
        loop = pygame.Rect(0, 0, r * 1.05, r * 0.95)
        loop.center = (cx, cy - r * 0.05)
        pygame.draw.arc(surf, ink, loop, -0.5, math.pi + 1.0, lw)
        # arrowhead closing the loop
        ax, ay = cx + r * 0.5, cy - r * 0.32
        pygame.draw.polygon(surf, ink, [(ax, ay), (ax - r * 0.2, ay - r * 0.12),
                                        (ax - r * 0.06, ay + r * 0.2)])

    elif kind == "fry":  # The KFC Incident — a single fry
        pygame.draw.line(surf, ink, (cx - r * 0.32, cy + r * 0.6),
                         (cx - r * 0.12, cy - r * 0.66), lw + 1)
        pygame.draw.line(surf, ink, (cx + r * 0.32, cy + r * 0.6),
                         (cx + r * 0.12, cy - r * 0.66), lw + 1)
        pygame.draw.line(surf, dim, (cx, cy + r * 0.6),
                         (cx, cy - r * 0.7), lw + 1)
        # crinkle hatch
        for s in range(-2, 3):
            yy = cy + s * r * 0.22
            pygame.draw.line(surf, ink, (cx - r * 0.28, yy + r * 0.05),
                             (cx + r * 0.28, yy - r * 0.05), max(1, lw - 1))

    elif kind == "scrooge":  # a coin with a slash
        pygame.draw.circle(surf, dim, (int(cx), int(cy)), int(r * 0.6))
        pygame.draw.circle(surf, ink, (int(cx), int(cy)), int(r * 0.6), lw)
        sf = _font(max(10, int(r * 0.9)), True)
        si = sf.render("$", True, ink)
        surf.blit(si, si.get_rect(center=(cx, cy)))
        # the slash (no money earned)
        pygame.draw.line(surf, ink, (cx - r * 0.7, cy + r * 0.7),
                         (cx + r * 0.7, cy - r * 0.7), lw + 2)

    elif kind == "tomb":  # The 49er — a "49" tombstone
        rect = pygame.Rect(cx - r * 0.5, cy - r * 0.55, r * 1.0, r * 1.2)
        pygame.draw.rect(surf, dim, rect, border_top_left_radius=int(r * 0.5),
                         border_top_right_radius=int(r * 0.5))
        pygame.draw.rect(surf, ink, rect, lw, border_top_left_radius=int(r * 0.5),
                         border_top_right_radius=int(r * 0.5))
        nf = _font(max(10, int(r * 0.6)), True)
        ni = nf.render("49", True, ink)
        surf.blit(ni, ni.get_rect(center=(cx, cy - r * 0.02)))

    elif kind == "ghostwall":  # a ghost splatted on a wall
        # the wall (right edge)
        pygame.draw.line(surf, ink, (cx + r * 0.6, cy - r * 0.8),
                         (cx + r * 0.6, cy + r * 0.8), lw + 1)
        # squashed ghost body
        gx = cx - r * 0.05
        pygame.draw.ellipse(surf, dim, (gx - r * 0.5, cy - r * 0.55,
                                        r * 0.95, r * 1.0))
        pygame.draw.ellipse(surf, ink, (gx - r * 0.5, cy - r * 0.55,
                                        r * 0.95, r * 1.0), lw)
        # flat compressed side against the wall + spiral eyes
        pygame.draw.circle(surf, ink, (int(gx - r * 0.16), int(cy - r * 0.1)),
                           max(1, lw))
        pygame.draw.circle(surf, ink, (int(gx + r * 0.18), int(cy - r * 0.1)),
                           max(1, lw))
        # impact stars
        for a in range(4):
            ang = a * math.pi / 2 + 0.4
            pygame.draw.line(surf, ink,
                             (cx + r * 0.5, cy - r * 0.4 + a * r * 0.05),
                             (cx + r * 0.5 + math.cos(ang) * r * 0.22,
                              cy - r * 0.4 + a * r * 0.05 + math.sin(ang) * r * 0.22),
                             max(1, lw - 1))

    elif kind == "oneway":  # frequent flyer one-way — a paper plane down
        pygame.draw.polygon(surf, dim, [
            (cx - r * 0.5, cy - r * 0.55), (cx + r * 0.55, cy - r * 0.1),
            (cx - r * 0.1, cy + r * 0.55)])
        pygame.draw.polygon(surf, ink, [
            (cx - r * 0.5, cy - r * 0.55), (cx + r * 0.55, cy - r * 0.1),
            (cx - r * 0.1, cy + r * 0.55)], lw)
        pygame.draw.line(surf, ink, (cx - r * 0.5, cy - r * 0.55),
                         (cx - r * 0.1, cy + r * 0.55), lw)
        pygame.draw.line(surf, ink, (cx - r * 0.1, cy - r * 0.05),
                         (cx + r * 0.55, cy - r * 0.1), lw)


# ── shared frame helpers ─────────────────────────────────────────────────────
def _crack(surf, cx, cy, r, ink, seed, branches=2):
    """A fine code-drawn lightning crack across the medallion face — the core
    'tarnished/damaged' tell. Deterministic per seed so a badge looks the same
    each frame."""
    rng = _rng(seed)
    x, y = cx + (rng() - 0.5) * r, cy - r * 0.7
    pts = [(x, y)]
    steps = 7
    for _ in range(steps):
        y += r * 1.4 / steps
        x += (rng() - 0.5) * r * 0.5
        pts.append((x, y))
    pygame.draw.lines(surf, ink, False, pts, 2)
    # hairline halo so the crack reads as a recessed split, not a drawn line
    pygame.draw.lines(surf, (*ink, 90) if len(ink) == 4 else ink, False, pts, 1)
    for b in range(branches):
        i = 2 + b * 2
        if i < len(pts) - 1:
            bx, by = pts[i]
            ex = bx + (rng() - 0.5) * r * 0.7
            ey = by + r * 0.4
            pygame.draw.line(surf, ink, (bx, by), (ex, ey), 1)


def _drip(surf, cx, cy, ink, dim):
    """A small grubby drip oozing off the badge base — earned-but-grubby."""
    pygame.draw.line(surf, ink, (cx, cy), (cx, cy + 7), 3)
    pygame.draw.circle(surf, dim, (int(cx), int(cy + 9)), 3)
    pygame.draw.circle(surf, ink, (int(cx), int(cy + 9)), 3, 1)


def _rng(seed):
    """Tiny deterministic LCG → float in [0,1); avoids reseeding global random."""
    state = [seed & 0xFFFFFFFF]

    def nxt():
        state[0] = (1103515245 * state[0] + 12345) & 0x7FFFFFFF
        return state[0] / 0x7FFFFFFF
    return nxt


def _patina(surf, cx, cy, r, col, seed):
    """Scattered verdigris/grime blotches over the metal — corrosion bloom."""
    rng = _rng(seed)
    for _ in range(7):
        a = rng() * 2 * math.pi
        d = rng() * r * 0.7
        br = int(r * (0.12 + rng() * 0.16))
        blob = pygame.Surface((br * 2, br * 2), pygame.SRCALPHA)
        pygame.draw.circle(blob, (*col, 70), (br, br), br)
        surf.blit(blob, (cx + math.cos(a) * d - br, cy + math.sin(a) * d - br))


def _progress_bar(surf, cx, y, w, cur, tot):
    """A thin gold progress bar with a 'cur / tot' caption under a locked badge."""
    h = 5
    track = pygame.Rect(cx - w // 2, y, w, h)
    rounded_rect(surf, track, h // 2, (40, 36, 30))
    pygame.draw.rect(surf, (*_GOLD_DEEP, 160), track, width=1, border_radius=h // 2)
    f = max(0.0, min(1.0, cur / tot))
    if f > 0:
        fill = pygame.Rect(track.x, track.y, max(h, int(w * f)), h)
        surf.blit(_vgrad_panel(fill.w, fill.h, h // 2,
                               lerp_color(_GOLD_BRIGHT, WHITE, 0.2), _GOLD_DEEP),
                  fill.topleft)
    cap = _font(9, True).render(f"{cur} / {tot}", True, _GOLD_PALE)
    cap.set_alpha(220)
    surf.blit(cap, cap.get_rect(center=(cx, y + h + 8)))


# ── medallion frame treatments (one per version) ─────────────────────────────
def _medallion_base(surf, cx, cy, r, tier, locked):
    """Common metal disc: dark seat well + radial metal face + beveled rim. The
    five versions differ in the RIM/edge style layered on top of this."""
    t = _TARNISH[tier]
    seat = pygame.Surface((r * 2 + 10, r * 2 + 10), pygame.SRCALPHA)
    pygame.draw.circle(seat, (0, 0, 0, 150), (r + 5, r + 5), r + 4)
    surf.blit(seat, (cx - r - 5, cy - r - 5))
    face = t["deep"] if locked else t["face"]
    for i in range(r, 0, -1):
        # top-lit radial: brighter toward upper-left
        f = i / r
        c = lerp_color(lerp_color(t["rim"], face, 0.4), t["deep"], (1 - f) ** 1.3)
        pygame.draw.circle(surf, c, (cx, cy), i)
    return t


def version_engraved(surf, cx, cy, r, tier, kind, locked, prog=None):
    """V1 — ENGRAVED RING. A recessed inner ring channel (like a struck medal),
    a deep crack, a drip. Tier reads by metal hue + an engraved tier ring count."""
    t = _medallion_base(surf, cx, cy, r, tier, locked)
    ink = lerp_color(t["deep"], NEAR_BLACK, 0.4)
    if locked:
        # greyed silhouette: glyph only, in flat shadow, no crack/drip
        _glyph(surf, cx, cy, r * 0.62, kind, (52, 50, 60), (40, 38, 48))
        pygame.draw.circle(surf, (70, 66, 78), (cx, cy), r, 2)
        pygame.draw.circle(surf, (50, 48, 58), (cx, cy), int(r * 0.82), 1)
        if prog:
            _progress_bar(surf, cx, cy + r + 8, int(r * 1.7), *prog)
        return
    # recessed channel
    pygame.draw.circle(surf, ink, (cx, cy), int(r * 0.84), 2)
    pygame.draw.circle(surf, lerp_color(t["rim"], WHITE, 0.2),
                       (cx, cy), int(r * 0.84) + 2, 1)
    _patina(surf, cx, cy, r, t["patina"], seed=hash(kind) & 0xFFFF)
    _glyph(surf, cx, cy, r * 0.6, kind, ink, lerp_color(t["face"], t["deep"], 0.4))
    _crack(surf, cx, cy, r * 0.78, ink, seed=(hash(kind) & 0xFFF) + 7)
    # rim + tier ring engraving
    pygame.draw.circle(surf, t["rim"], (cx, cy), r, 3)
    pygame.draw.circle(surf, lerp_color(t["rim"], WHITE, 0.35),
                       (cx, cy), r, 1)
    rings = {"bronze": 1, "silver": 2, "gold": 3}[tier]
    for k in range(rings):
        pygame.draw.circle(surf, lerp_color(t["rim"], t["deep"], 0.3),
                           (cx, cy + r - 4), 2 + k, 1)
    _drip(surf, cx, cy + r - 2, ink, t["patina"])


def version_cracked_seal(surf, cx, cy, r, tier, kind, locked, prog=None):
    """V2 — CRACKED WAX SEAL. A blobby hand-pressed seal silhouette (not a clean
    disc) with a big fracture splitting it + ooze drip. Comic, grubby, organic."""
    t = _TARNISH[tier]
    # irregular seal blob via jittered polygon
    rng = _rng((hash(kind) & 0xFFFF) + 3)
    pts = []
    n = 18
    for i in range(n):
        a = i / n * 2 * math.pi
        rr = r * (0.92 + (rng() - 0.5) * 0.14)
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    shadow = [(x + 2, y + 3) for x, y in pts]
    pygame.draw.polygon(surf, (0, 0, 0, 140), shadow)
    face = t["deep"] if locked else t["face"]
    pygame.draw.polygon(surf, face, pts)
    ink = lerp_color(t["deep"], NEAR_BLACK, 0.4)
    if locked:
        _glyph(surf, cx, cy, r * 0.6, kind, (52, 50, 60), (42, 40, 50))
        pygame.draw.polygon(surf, (70, 66, 78), pts, 2)
        if prog:
            _progress_bar(surf, cx, cy + r + 10, int(r * 1.7), *prog)
        return
    # top-light wash inside the blob
    light = pygame.Surface((r * 2, r), pygame.SRCALPHA)
    for y in range(r):
        pygame.draw.line(light, (255, 255, 255, int(40 * (1 - y / r))),
                         (0, y), (r * 2, y))
    surf.blit(light, (cx - r, cy - r))
    _patina(surf, cx, cy, r, t["patina"], seed=hash(kind) & 0xFFFF)
    _glyph(surf, cx, cy, r * 0.58, kind, ink, lerp_color(face, t["deep"], 0.4))
    _crack(surf, cx, cy, r * 0.86, ink, seed=(hash(kind) & 0xFFF) + 1, branches=3)
    pygame.draw.polygon(surf, t["rim"], pts, 3)
    # tier pips embossed at the base
    pips = {"bronze": 1, "silver": 2, "gold": 3}[tier]
    for k in range(pips):
        px = cx - (pips - 1) * 4 + k * 8
        pygame.draw.circle(surf, lerp_color(t["rim"], WHITE, 0.3),
                           (px, cy + int(r * 0.62)), 2)
    _drip(surf, cx, cy + int(r * 0.84), ink, t["patina"])


def version_riveted_plate(surf, cx, cy, r, tier, kind, locked, prog=None):
    """V3 — RIVETED PLATE. A heavy industrial badge: octagon metal plate, corner
    rivets, a structural crack + rust drip. Tier reads by metal + rivet count."""
    t = _TARNISH[tier]
    pts = [(cx + math.cos(math.pi / 8 + i * math.pi / 4) * r,
            cy + math.sin(math.pi / 8 + i * math.pi / 4) * r) for i in range(8)]
    pygame.draw.polygon(surf, (0, 0, 0, 140), [(x + 2, y + 3) for x, y in pts])
    face = t["deep"] if locked else t["face"]
    # radial-ish fill
    for i in range(int(r), 0, -1):
        f = i / r
        c = lerp_color(lerp_color(t["rim"], face, 0.4), t["deep"], (1 - f) ** 1.3)
        sub = [(cx + (x - cx) * f, cy + (y - cy) * f) for x, y in pts]
        pygame.draw.polygon(surf, c, sub)
    ink = lerp_color(t["deep"], NEAR_BLACK, 0.4)
    if locked:
        _glyph(surf, cx, cy, r * 0.58, kind, (52, 50, 60), (42, 40, 50))
        pygame.draw.polygon(surf, (70, 66, 78), pts, 2)
        if prog:
            _progress_bar(surf, cx, cy + r + 8, int(r * 1.7), *prog)
        return
    _patina(surf, cx, cy, r, t["patina"], seed=hash(kind) & 0xFFFF)
    _glyph(surf, cx, cy, r * 0.56, kind, ink, lerp_color(face, t["deep"], 0.4))
    _crack(surf, cx, cy, r * 0.8, ink, seed=(hash(kind) & 0xFFF) + 5)
    pygame.draw.polygon(surf, t["rim"], pts, 3)
    pygame.draw.polygon(surf, lerp_color(t["rim"], WHITE, 0.3), pts, 1)
    # rivets — count encodes tier
    rivets = {"bronze": 4, "silver": 6, "gold": 8}[tier]
    for i in range(rivets):
        a = i / rivets * 2 * math.pi - math.pi / 2
        rx, ry = cx + math.cos(a) * r * 0.82, cy + math.sin(a) * r * 0.82
        pygame.draw.circle(surf, lerp_color(t["rim"], WHITE, 0.4),
                           (int(rx), int(ry)), 2)
        pygame.draw.circle(surf, ink, (int(rx), int(ry)), 2, 1)
    _drip(surf, cx, cy + r - 2, ink, t["patina"])


def version_ribbon(surf, cx, cy, r, tier, kind, locked, prog=None):
    """V4 — DROOPING RIBBON. A medal hung from a sad, frayed ribbon (the parody
    of a Wall-of-Fame ribbon), tarnished disc with crack + drip. Ribbon colour
    is the tier cue."""
    t = _TARNISH[tier]
    # frayed ribbon above the disc
    ry = cy - r - 14
    rcol = lerp_color(t["rim"], t["deep"], 0.2)
    pygame.draw.polygon(surf, rcol, [(cx - 7, ry), (cx + 7, ry),
                                     (cx + 5, cy - r + 2), (cx - 5, cy - r + 2)])
    pygame.draw.polygon(surf, ink_of(t), [(cx - 7, ry), (cx + 7, ry),
                                          (cx + 5, cy - r + 2),
                                          (cx - 5, cy - r + 2)], 1)
    # frayed top edge
    for fx in range(-6, 7, 3):
        pygame.draw.line(surf, ink_of(t), (cx + fx, ry),
                         (cx + fx + 1, ry - 3), 1)
    _medallion_base(surf, cx, cy, r, tier, locked)
    ink = ink_of(t)
    if locked:
        _glyph(surf, cx, cy, r * 0.6, kind, (52, 50, 60), (42, 40, 50))
        pygame.draw.circle(surf, (70, 66, 78), (cx, cy), r, 2)
        if prog:
            _progress_bar(surf, cx, cy + r + 8, int(r * 1.7), *prog)
        return
    _patina(surf, cx, cy, r, t["patina"], seed=hash(kind) & 0xFFFF)
    _glyph(surf, cx, cy, r * 0.58, kind, ink, lerp_color(t["face"], t["deep"], 0.4))
    _crack(surf, cx, cy, r * 0.78, ink, seed=(hash(kind) & 0xFFF) + 2)
    # scalloped rim (struck-medal edge), tier hue
    for i in range(24):
        a = i / 24 * 2 * math.pi
        pygame.draw.circle(surf, lerp_color(t["rim"], t["deep"], 0.2),
                           (int(cx + math.cos(a) * r), int(cy + math.sin(a) * r)), 2)
    pygame.draw.circle(surf, t["rim"], (cx, cy), r, 2)
    _drip(surf, cx, cy + r - 2, ink, t["patina"])


def version_cracked_gem(surf, cx, cy, r, tier, kind, locked, prog=None):
    """V5 — TARNISHED GEM-FRAME. Closest kin to the Store's gem cards: a clean
    medallion with a small MUTED rarity gem inset at the base (mirroring the
    store's faceted gem, but desaturated) + a hairline crack running THROUGH the
    gem. Tier = gem hue/value."""
    t = _medallion_base(surf, cx, cy, r, tier, locked)
    ink = lerp_color(t["deep"], NEAR_BLACK, 0.4)
    if locked:
        _glyph(surf, cx, cy - 3, r * 0.6, kind, (52, 50, 60), (42, 40, 50))
        pygame.draw.circle(surf, (70, 66, 78), (cx, cy), r, 2)
        if prog:
            _progress_bar(surf, cx, cy + r + 8, int(r * 1.7), *prog)
        return
    _patina(surf, cx, cy, r, t["patina"], seed=hash(kind) & 0xFFFF)
    _glyph(surf, cx, cy - 4, r * 0.56, kind, ink,
           lerp_color(t["face"], t["deep"], 0.4))
    _crack(surf, cx, cy, r * 0.78, ink, seed=(hash(kind) & 0xFFF) + 9)
    # double-rim bezel like the store cards
    pygame.draw.circle(surf, t["rim"], (cx, cy), r, 3)
    pygame.draw.circle(surf, lerp_color(t["rim"], WHITE, 0.3), (cx, cy), r - 1, 1)
    # muted faceted gem at the base (the tarnished echo of store _gem)
    gr = max(4, r // 5)
    gy = cy + int(r * 0.62)
    g = t["gem"]
    top, bot = (cx, gy - gr), (cx, gy + gr)
    left, right = (cx - gr, gy), (cx + gr, gy)
    ctr = (cx, gy)
    pygame.draw.polygon(surf, lerp_color(g, WHITE, 0.35), [top, left, ctr])
    pygame.draw.polygon(surf, g, [top, right, ctr])
    pygame.draw.polygon(surf, lerp_color(g, t["deep"], 0.5), [left, bot, ctr])
    pygame.draw.polygon(surf, lerp_color(t["deep"], NEAR_BLACK, 0.3),
                        [right, bot, ctr])
    pygame.draw.polygon(surf, ink, [top, right, bot, left], 1)
    _drip(surf, cx, cy + r - 2, ink, t["patina"])


def ink_of(t):
    return lerp_color(t["deep"], NEAR_BLACK, 0.4)


VERSIONS = [
    ("V1  ENGRAVED RING", version_engraved),
    ("V2  CRACKED WAX SEAL", version_cracked_seal),
    ("V3  RIVETED PLATE", version_riveted_plate),
    ("V4  DROOPING RIBBON", version_ribbon),
    ("V5  TARNISHED GEM-FRAME", version_cracked_gem),
]

# Per-version example wall: 6 badges, mixed tiers, ≥1 locked-with-progress.
# (label, glyph_kind, tier, locked, progress-or-None)
EXAMPLES = [
    ("GOOSE EGG",    "egg",         "bronze", False, None),
    ("ICARUS",       "icarus",      "silver", False, None),
    ("THE SCROOGE",  "scrooge",     "gold",   False, None),
    ("EARLY EXIT",   "stopwatch",   "bronze", False, None),
    ("THE 49ER",     "tomb",        "silver", True,  (3, 10)),
    ("SPLAT",        "ghostwall",   "gold",   True,  (7, 25)),
]


def _draw_panel(surf, ox, oy, pw, ph, title, draw_fn):
    """One version's mini SHAME wall: obsidian panel, demeaning title chip + the
    player's (mock) name, and a 2-column badge grid."""
    panel = pygame.Rect(ox, oy, pw, ph)
    _drop_shadow(surf, panel, 16, blur=6, alpha=150)
    surf.blit(_vgrad_panel(pw, ph, 16, *_PANEL_BG), panel.topleft)
    pygame.draw.rect(surf, (74, 50, 40), panel.inflate(-7, -7), width=2,
                     border_radius=11)
    pygame.draw.rect(surf, (120, 92, 64), panel, width=1, border_radius=16)

    cx = panel.centerx
    # header: WALL OF SHAME + demeaning title chip under a mock player name
    _gradient_text(surf, "WALL OF SHAME", _font(15, True), (cx, oy + 20),
                   (190, 170, 150), (120, 96, 70), shadow=True)
    name = _font(13, True).render("SKYDIVER_92", True, _GOLD_PALE)
    surf.blit(name, name.get_rect(center=(cx, oy + 40)))
    # demeaning title chip (the demerit rank shown under the name)
    chip_txt = "WALL INSPECTOR"
    cf = _font(10, True)
    ci = cf.render(chip_txt, True, (210, 196, 200))
    cw = ci.get_width() + 24
    chip = pygame.Rect(cx - cw // 2, oy + 50, cw, 18)
    surf.blit(_vgrad_panel(cw, 18, 9, (66, 48, 56), (40, 30, 36)), chip.topleft)
    pygame.draw.rect(surf, (140, 110, 116), chip, width=1, border_radius=9)
    surf.blit(ci, ci.get_rect(center=chip.center))

    # badge grid, 2 columns
    grid_top = oy + 88
    col_w = pw // 2
    r = 29
    row_h = 100
    for idx, (lbl, kind, tier, locked, prog) in enumerate(EXAMPLES):
        gx = panel.x + col_w // 2 + (idx % 2) * col_w
        gy = grid_top + (idx // 2) * row_h + r
        draw_fn(surf, gx, gy, r, tier, kind, locked, prog)
        cap = _font(9, True).render(lbl, True,
                                    (120, 116, 124) if locked else _GOLD_PALE)
        # Earned: label tucks just under the medallion. Locked: the progress bar
        # + its "cur / tot" caption already sit there, so the name drops below it.
        cap_y = (gy + r + 32) if locked else (gy + r + 14)
        surf.blit(cap, cap.get_rect(center=(gx, cap_y)))


def main():
    pygame.font.init()
    cols, rows = 3, 2  # 5 versions + 1 legend tile
    pw, ph = 300, 500
    pad = 18
    sheet_w = cols * pw + (cols + 1) * pad
    sheet_h = rows * ph + (rows + 1) * pad + 56
    sheet = pygame.Surface((sheet_w, sheet_h))
    # backdrop gradient (match the menu night sky)
    n = len(_BG_STOPS)
    for y in range(sheet_h):
        f = y / (sheet_h - 1)
        seg = min(n - 2, int(f * (n - 1)))
        local = f * (n - 1) - seg
        pygame.draw.line(sheet, lerp_color(_BG_STOPS[seg], _BG_STOPS[seg + 1], local),
                         (0, y), (sheet_w, y))

    _gradient_text(sheet, "WALL OF SHAME  —  FRAME EXPLORATIONS (ROUND 1)",
                   _font(20, True), (sheet_w // 2, 30),
                   (255, 240, 180), (200, 150, 70), shadow=True)

    for i, (title, fn) in enumerate(VERSIONS):
        ox = pad + (i % cols) * (pw + pad)
        oy = 56 + pad + (i // cols) * (ph + pad)
        _draw_panel(sheet, ox, oy, pw, ph, title, fn)
        tag = _font(12, True).render(title, True, _GOLD_BRIGHT)
        sheet.blit(tag, (ox + 4, oy - 16))

    # legend tile (6th slot): tier swatches + locked anatomy
    lx = pad + (5 % cols) * (pw + pad)
    ly = 56 + pad + (5 // cols) * (ph + pad)
    lp = pygame.Rect(lx, ly, pw, ph)
    surf = sheet
    surf.blit(_vgrad_panel(pw, ph, 16, *_PANEL_BG), lp.topleft)
    pygame.draw.rect(surf, (74, 50, 40), lp.inflate(-7, -7), 2, border_radius=11)
    pygame.draw.rect(surf, (120, 92, 64), lp, 1, border_radius=16)
    _gradient_text(surf, "TARNISHED TIERS", _font(15, True), (lp.centerx, ly + 22),
                   (190, 170, 150), (120, 96, 70))
    tiers = [("BRONZE", "bronze"), ("SILVER", "silver"), ("GOLD-TARNISHED", "gold")]
    for j, (tn, tk) in enumerate(tiers):
        tcx = lp.centerx
        tcy = ly + 80 + j * 84
        version_engraved(surf, tcx - 50, tcy, 28, tk, "egg", False, None)
        nm = _font(11, True).render(tn, True, _GOLD_PALE)
        surf.blit(nm, nm.get_rect(midleft=(tcx - 6, tcy)))
    # locked anatomy demo
    _gradient_text(surf, "LOCKED STATE", _font(13, True),
                   (lp.centerx, ly + ph - 96), (190, 170, 150), (120, 96, 70))
    version_engraved(surf, lp.centerx, ly + ph - 60, 28, "silver", "tomb",
                     True, (3, 10))
    note = _font(9, True).render("greyed silhouette + gold progress",
                                 True, (150, 142, 150))
    surf.blit(note, note.get_rect(center=(lp.centerx, ly + ph - 14)))

    out_dir = "/home/user/skybit/docs/profile/shame_badges"
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "round_1.png")
    pygame.image.save(sheet, out)
    print("WROTE", out, sheet.get_size())


if __name__ == "__main__":
    main()
