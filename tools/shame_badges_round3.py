"""Wall of Shame badge exploration sheet (round 3).

Round 2 committed the merged badge (V5 Tarnished Gem-Frame + V1 recessed
channel) and the locked/pinned/grid system the art-director signed off on. The
ONLY outstanding fix carried into round 3: the tier VALUE ladder had collapsed —
silver and gold-tarnished separated by HUE alone (whole-disc luma ~105 vs ~115),
so they merged in grayscale and at squint scale (the colourblind trap round 2 set
out to close). Round 3 re-opens that ladder to an obviously-stepped WHOLE-DISC
luma band and re-points the proof strip to measure the WHOLE disc (round 2's
caption sampled face luma and overstated the separation, hiding the miss):

  bronze ~68  /  silver ~102  /  gold ~131   (≥25 luma between each band)

Everything else is the shipped round-2 composition: the merged badge across three
tiers + a whole-disc grayscale proof strip, a populated 3-column wall mixing
earned tiers + locked-with-progress, the V4 drooping-ribbon as a single PINNED
hero, and one large DETAIL view keeping the crack + heavy patina the grid drops.
Procedural-only; reuses the Store's "Obsidian & Gold" primitives (esp. the
faceted gem) so it sits in the real furniture. Writes the combined PNG only.
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
    _vgrad_panel, _drop_shadow, _soft_glow, _gradient_text,
)

# ── Tarnished palette ────────────────────────────────────────────────────────
# A shame badge is the desaturated INVERSE of a gold medal. Tier reads by
# WHOLE-DISC VALUE first, so each triplet is tuned to a distinct, obviously-
# stepped grayscale band that survives desaturation AND a squint — the colour-
# blind safety net, proven by the whole-disc strip on the sheet:
#   bronze ~68 (darkest-warm) / silver ~102 (mid-cool) / gold ~131 (lightest-warm)
# with ≥25 luma between each band. Round 2's silver/gold sat ~10 apart and only
# differed in hue; round 3 drops silver into the 100s and lifts gold-tarnished to
# a clear PALE top-of-ladder band so the value ladder can't collapse in grayscale.
# `gem` stays the brightest member of each tier so the enlarged base gem (the
# single bold cue) pops against its own disc.
_TARNISH = {
    "bronze": {  # darkest band — muddy oxidised copper
        "rim":  (120, 84, 58),   "face": (84, 58, 40),
        "deep": (44, 30, 21),    "gem":  (172, 116, 74),
        "patina": (92, 116, 92),
    },
    "silver": {  # mid band, cool — dropped into the 100s so it can't crowd gold
        "rim":  (130, 134, 144), "face": (94, 98, 110),
        "deep": (50, 54, 64),    "gem":  (186, 192, 206),
        "patina": (96, 116, 120),
    },
    "gold": {  # lightest band — pale dull brass top-of-ladder (NOT wall-of-fame gold)
        "rim":  (196, 172, 112), "face": (166, 142, 86),
        "deep": (88, 72, 36),    "gem":  (240, 220, 158),
        "patina": (118, 120, 86),
    },
}

_PANEL_BG = ((20, 16, 24), (8, 7, 13))
_BG_STOPS = ((10, 9, 16), (16, 13, 26), (22, 17, 34))

# Locked state: lifted ~15% off the round-1 near-black silhouette so it reads
# DORMANT not DEAD, plus a faint COOL rim (a sleeping badge, never a smudge).
_LOCK_FACE = (66, 64, 76)
_LOCK_GLYPH_INK = (96, 96, 110)
_LOCK_GLYPH_DIM = (78, 78, 92)
_LOCK_RIM = (108, 122, 150)      # cool steel rim
_LOCK_RIM_IN = (78, 88, 112)


# ── glyph library (the demeaning icons) ───────────────────────────────────────
# Carried from round 2: every call passes a HIGH-CONTRAST ink (near the disc's
# darkest) + a brighter dim fill so the glyph — the joke — is the strongest
# contrast inside the disc. With gold lifted paler, its dark ink contrast only
# improves (verified on the sheet).
def _glyph(surf, cx, cy, r, kind, ink, dim):
    lw = max(2, int(r) // 8)

    if kind == "egg":
        pygame.draw.ellipse(surf, dim, (cx - r * 0.6, cy - r * 0.78,
                                        r * 1.2, r * 1.56))
        pygame.draw.ellipse(surf, ink, (cx - r * 0.6, cy - r * 0.78,
                                        r * 1.2, r * 1.56), lw)
        pygame.draw.ellipse(surf, ink, (cx - r * 0.24, cy - r * 0.34,
                                        r * 0.48, r * 0.68), max(1, lw - 1))

    elif kind == "icarus":
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
        fx, fy = cx + r * 0.5, cy + r * 0.55
        pygame.draw.line(surf, ink, (fx - r * 0.18, fy - r * 0.22),
                         (fx + r * 0.12, fy + r * 0.2), lw)
        for s in range(3):
            pygame.draw.line(surf, ink,
                             (fx - r * 0.1 + s * r * 0.08, fy - r * 0.12 + s * r * 0.12),
                             (fx - r * 0.22 + s * r * 0.08, fy - r * 0.04 + s * r * 0.12),
                             max(1, lw - 1))

    elif kind == "stopwatch":
        pygame.draw.circle(surf, dim, (int(cx), int(cy + r * 0.08)),
                           int(r * 0.62))
        pygame.draw.circle(surf, ink, (int(cx), int(cy + r * 0.08)),
                           int(r * 0.62), lw)
        pygame.draw.line(surf, ink, (cx, cy - r * 0.62), (cx, cy - r * 0.82), lw)
        pygame.draw.rect(surf, ink, (cx - r * 0.16, cy - r * 0.9,
                                     r * 0.32, r * 0.12))
        ang = -math.pi / 2 + 2 * math.pi * (2 / 12)
        pygame.draw.line(surf, ink, (cx, cy + r * 0.08),
                         (cx + math.cos(ang) * r * 0.42,
                          cy + r * 0.08 + math.sin(ang) * r * 0.42), lw)
        pygame.draw.circle(surf, ink, (int(cx), int(cy + r * 0.08)),
                           max(1, lw))

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

    elif kind == "fry":
        pygame.draw.line(surf, ink, (cx - r * 0.32, cy + r * 0.6),
                         (cx - r * 0.12, cy - r * 0.66), lw + 1)
        pygame.draw.line(surf, ink, (cx + r * 0.32, cy + r * 0.6),
                         (cx + r * 0.12, cy - r * 0.66), lw + 1)
        pygame.draw.line(surf, dim, (cx, cy + r * 0.6),
                         (cx, cy - r * 0.7), lw + 1)
        for s in range(-2, 3):
            yy = cy + s * r * 0.22
            pygame.draw.line(surf, ink, (cx - r * 0.28, yy + r * 0.05),
                             (cx + r * 0.28, yy - r * 0.05), max(1, lw - 1))

    elif kind == "scrooge":
        pygame.draw.circle(surf, dim, (int(cx), int(cy)), int(r * 0.64))
        pygame.draw.circle(surf, ink, (int(cx), int(cy)), int(r * 0.64), lw)
        sf = _font(max(10, int(r * 0.95)), True)
        si = sf.render("$", True, ink)
        surf.blit(si, si.get_rect(center=(cx, cy)))
        pygame.draw.line(surf, ink, (cx - r * 0.72, cy + r * 0.72),
                         (cx + r * 0.72, cy - r * 0.72), lw + 2)

    elif kind == "tomb":
        rect = pygame.Rect(cx - r * 0.5, cy - r * 0.55, r * 1.0, r * 1.2)
        pygame.draw.rect(surf, dim, rect, border_top_left_radius=int(r * 0.5),
                         border_top_right_radius=int(r * 0.5))
        pygame.draw.rect(surf, ink, rect, lw, border_top_left_radius=int(r * 0.5),
                         border_top_right_radius=int(r * 0.5))
        nf = _font(max(10, int(r * 0.62)), True)
        ni = nf.render("49", True, ink)
        surf.blit(ni, ni.get_rect(center=(cx, cy - r * 0.02)))

    elif kind == "ghostwall":
        pygame.draw.line(surf, ink, (cx + r * 0.6, cy - r * 0.8),
                         (cx + r * 0.6, cy + r * 0.8), lw + 1)
        gx = cx - r * 0.05
        pygame.draw.ellipse(surf, dim, (gx - r * 0.5, cy - r * 0.55,
                                        r * 0.95, r * 1.0))
        pygame.draw.ellipse(surf, ink, (gx - r * 0.5, cy - r * 0.55,
                                        r * 0.95, r * 1.0), lw)
        pygame.draw.circle(surf, ink, (int(gx - r * 0.16), int(cy - r * 0.1)),
                           max(1, lw))
        pygame.draw.circle(surf, ink, (int(gx + r * 0.18), int(cy - r * 0.1)),
                           max(1, lw))
        for a in range(4):
            ang = a * math.pi / 2 + 0.4
            pygame.draw.line(surf, ink,
                             (cx + r * 0.5, cy - r * 0.4 + a * r * 0.05),
                             (cx + r * 0.5 + math.cos(ang) * r * 0.22,
                              cy - r * 0.4 + a * r * 0.05 + math.sin(ang) * r * 0.22),
                             max(1, lw - 1))

    elif kind == "oneway":
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


# ── grime tells ───────────────────────────────────────────────────────────────
def _rng(seed):
    """Tiny deterministic LCG → float in [0,1); avoids reseeding global random."""
    state = [seed & 0xFFFFFFFF]

    def nxt():
        state[0] = (1103515245 * state[0] + 12345) & 0x7FFFFFFF
        return state[0] / 0x7FFFFFFF
    return nxt


def _drip(surf, cx, cy, ink, dim):
    """The ONE grubby tell kept on grid badges — a small drip oozing off the
    base. (Crack + heavy patina now live only on the large detail view, where
    they don't read as a render glitch at thumbnail scale.)"""
    pygame.draw.line(surf, ink, (cx, cy), (cx, cy + 7), 3)
    pygame.draw.circle(surf, dim, (int(cx), int(cy + 9)), 3)
    pygame.draw.circle(surf, ink, (int(cx), int(cy + 9)), 3, 1)


def _rim_patina(surf, cx, cy, r, col, seed):
    """Corrosion blooms at the EDGE only (where real verdigris creeps in from the
    rim), faint (~45 alpha) so it never muddies the glyph in the disc centre."""
    rng = _rng(seed)
    for _ in range(6):
        a = rng() * 2 * math.pi
        d = r * (0.78 + rng() * 0.16)          # hug the rim
        br = int(r * (0.10 + rng() * 0.10))
        blob = pygame.Surface((br * 2, br * 2), pygame.SRCALPHA)
        pygame.draw.circle(blob, (*col, 45), (br, br), br)
        surf.blit(blob, (cx + math.cos(a) * d - br, cy + math.sin(a) * d - br))


def _heavy_patina(surf, cx, cy, r, col, seed):
    """Full corrosion spread for the LARGE detail view only (where the badge is
    big enough that grime reads as character, not noise)."""
    rng = _rng(seed)
    for _ in range(10):
        a = rng() * 2 * math.pi
        d = rng() * r * 0.82
        br = int(r * (0.10 + rng() * 0.16))
        blob = pygame.Surface((br * 2, br * 2), pygame.SRCALPHA)
        pygame.draw.circle(blob, (*col, 70), (br, br), br)
        surf.blit(blob, (cx + math.cos(a) * d - br, cy + math.sin(a) * d - br))


def _crack(surf, cx, cy, r, ink, seed, branches=2):
    """A fine lightning fracture — RESERVED for the large detail view. Kept off
    the grid because at thumbnail scale it reads as a render glitch."""
    rng = _rng(seed)
    x, y = cx + (rng() - 0.5) * r, cy - r * 0.7
    pts = [(x, y)]
    steps = 7
    for _ in range(steps):
        y += r * 1.4 / steps
        x += (rng() - 0.5) * r * 0.5
        pts.append((x, y))
    pygame.draw.lines(surf, ink, False, pts, 2)
    for b in range(branches):
        i = 2 + b * 2
        if i < len(pts) - 1:
            bx, by = pts[i]
            ex = bx + (rng() - 0.5) * r * 0.7
            ey = by + r * 0.4
            pygame.draw.line(surf, ink, (bx, by), (ex, ey), 1)


def _progress_bar(surf, cx, y, w, cur, tot):
    """A thin gold progress bar + 'cur / tot' caption under a locked badge."""
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
    cap.set_alpha(230)
    surf.blit(cap, cap.get_rect(center=(cx, y + h + 8)))


# ── the merged badge ──────────────────────────────────────────────────────────
def _disc(surf, cx, cy, r, tier, locked):
    """Common metal disc: dark seat well + top-lit radial metal face. This is the
    whole-shape VALUE that carries tier — bronze darkest, silver mid-cool, gold
    lightest. Returns the tier triplet."""
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


def _disc_luma_measured(r, tier):
    """Render a tier disc in isolation and return its mean Rec.601 luma sampled
    over the WHOLE disc — the honest value the squint/grayscale test sees. Round
    2's proof caption sampled the single face colour, which overstated the
    separation and hid the silver↔gold collapse; this measures the rendered
    pixels instead."""
    pad = 6
    s = pygame.Surface((r * 2 + pad * 2, r * 2 + pad * 2), pygame.SRCALPHA)
    cx = cy = r + pad
    _disc(s, cx, cy, r, tier, False)
    total = 0.0
    cnt = 0
    rr2 = r * r
    for yy in range(s.get_height()):
        for xx in range(s.get_width()):
            cr, cg, cb, ca = s.get_at((xx, yy))
            if ca == 0:
                continue
            dx, dy = xx - cx, yy - cy
            if dx * dx + dy * dy > rr2:       # disc face only, skip the seat ring
                continue
            total += 0.299 * cr + 0.587 * cg + 0.114 * cb
            cnt += 1
    return total / max(1, cnt)


def _tier_gem(surf, cx, cy, r, t):
    """The ONE bold backing cue: the Store faceted gem, desaturated, enlarged to
    ~r/3.2 and seated at the disc base. A four-value cut with a BRIGHTER top
    facet (the tier read) + a white specular pip, mirroring the Store gem so the
    Wall sits in the same jewellery family. Replaces every counted cue."""
    g = t["gem"]
    gr = max(6, int(r / 3.2))               # bold — visible at 70px
    gy = cy + int(r * 0.58)
    # dark keyline well, like the store gem's seat
    seat = pygame.Surface((gr * 2 + 8, gr * 2 + 8), pygame.SRCALPHA)
    pygame.draw.circle(seat, (0, 0, 0, 150), (gr + 4, gr + 4), gr + 3)
    surf.blit(seat, (cx - gr - 4, gy - gr - 4))
    top, bot = (cx, gy - gr), (cx, gy + gr)
    left, right = (cx - gr, gy), (cx + gr, gy)
    ctr = (cx, gy)
    hi = lerp_color(g, WHITE, 0.55)         # brighter top facet = the tier read
    sh = lerp_color(g, t["deep"], 0.5)
    dk = lerp_color(t["deep"], NEAR_BLACK, 0.3)
    pygame.draw.polygon(surf, hi, [top, left, ctr])
    pygame.draw.polygon(surf, g, [top, right, ctr])
    pygame.draw.polygon(surf, sh, [left, bot, ctr])
    pygame.draw.polygon(surf, dk, [right, bot, ctr])
    pygame.draw.polygon(surf, lerp_color(t["deep"], NEAR_BLACK, 0.45),
                        [top, right, bot, left], width=1)
    pr = max(1, gr // 4)
    pip = pygame.Surface((pr * 2 + 2, pr * 2 + 2), pygame.SRCALPHA)
    pygame.draw.circle(pip, (255, 255, 255, 235), (pr + 1, pr + 1), pr)
    surf.blit(pip, (cx - pr - gr // 3, gy - pr - gr // 3),
              special_flags=pygame.BLEND_ADD)


def badge(surf, cx, cy, r, tier, kind, locked, prog=None, detail=False):
    """The merged WALL OF SHAME badge — V5 Tarnished Gem-Frame + V1's recessed
    engraved channel. Tier reads by WHOLE-SHAPE VALUE first, backed by the bold
    base gem. Grid badges keep only the drip + rim patina; `detail=True` adds the
    crack + heavy patina for the large hero/detail view."""
    t = _disc(surf, cx, cy, r, tier, locked)

    if locked:
        # Dormant, not dead: lifted silhouette + a cool steel rim that says
        # "asleep". No grime, no gem — a sleeping badge.
        _glyph(surf, cx, cy - 3, r * 0.6, kind, _LOCK_GLYPH_INK, _LOCK_GLYPH_DIM)
        pygame.draw.circle(surf, _LOCK_RIM, (cx, cy), r, 2)
        pygame.draw.circle(surf, _LOCK_RIM_IN, (cx, cy), int(r * 0.84), 1)
        if prog:
            _progress_bar(surf, cx, cy + r + 12, int(r * 1.7), *prog)
        return

    ink = lerp_color(t["deep"], NEAR_BLACK, 0.55)            # +contrast glyph ink
    glyph_dim = lerp_color(t["gem"], t["face"], 0.35)        # brighter fill

    if detail:
        _heavy_patina(surf, cx, cy, r, t["patina"], seed=hash(kind) & 0xFFFF)
    else:
        _rim_patina(surf, cx, cy, r, t["patina"], seed=hash(kind) & 0xFFFF)

    # V1's recessed engraved channel — a struck-medal inner ring
    pygame.draw.circle(surf, ink, (cx, cy), int(r * 0.84), 2)
    pygame.draw.circle(surf, lerp_color(t["rim"], WHITE, 0.25),
                       (cx, cy), int(r * 0.84) + 2, 1)

    _glyph(surf, cx, cy - 4, r * 0.58, kind, ink, glyph_dim)

    if detail:
        _crack(surf, cx, cy, r * 0.78, ink, seed=(hash(kind) & 0xFFF) + 9)

    # double-rim bezel (Store-card kin)
    pygame.draw.circle(surf, t["rim"], (cx, cy), r, 3)
    pygame.draw.circle(surf, lerp_color(t["rim"], WHITE, 0.3), (cx, cy), r - 1, 1)

    _tier_gem(surf, cx, cy, r, t)
    _drip(surf, cx, cy + r - 2, ink, t["patina"])


def pinned_badge(surf, cx, cy, r, tier, kind):
    """The PINNED-HERO treatment — V4's drooping, frayed ribbon reserved for the
    one featured badge (the wall's pinned shame). Its edge is a BOLD NOTCH (a
    coarse cog rather than fine scallop, which turns to fuzz small), and the
    ribbon colour echoes the tier. The frayed top edge uses sturdy 2px ticks so
    it doesn't dissolve to sub-pixel fuzz."""
    t = _TARNISH[tier]
    ink = lerp_color(t["deep"], NEAR_BLACK, 0.55)
    # frayed ribbon drooping above the disc
    ry = cy - r - 22
    rcol = lerp_color(t["rim"], t["deep"], 0.2)
    pygame.draw.polygon(surf, rcol, [(cx - 10, ry), (cx + 10, ry),
                                     (cx + 7, cy - r + 2), (cx - 7, cy - r + 2)])
    pygame.draw.polygon(surf, ink, [(cx - 10, ry), (cx + 10, ry),
                                    (cx + 7, cy - r + 2), (cx - 7, cy - r + 2)], 1)
    # a sad sheen down the ribbon centre
    pygame.draw.line(surf, lerp_color(t["rim"], WHITE, 0.3),
                     (cx, ry + 2), (cx, cy - r), 1)
    for fx in range(-9, 10, 4):              # frayed top edge — sturdy 2px ticks
        pygame.draw.line(surf, ink, (cx + fx, ry), (cx + fx + 1, ry - 4), 2)

    _disc(surf, cx, cy, r, tier, False)
    _rim_patina(surf, cx, cy, r, t["patina"], seed=hash(kind) & 0xFFFF)
    # recessed channel
    pygame.draw.circle(surf, ink, (cx, cy), int(r * 0.84), 2)
    pygame.draw.circle(surf, lerp_color(t["rim"], WHITE, 0.25),
                       (cx, cy), int(r * 0.84) + 2, 1)
    glyph_dim = lerp_color(t["gem"], t["face"], 0.35)
    _glyph(surf, cx, cy - 4, r * 0.58, kind, ink, glyph_dim)

    # BOLD NOTCH edge — a coarse cog (reads at small size, unlike fine scallop)
    notches = 14
    for i in range(notches):
        a = i / notches * 2 * math.pi
        nx, ny = cx + math.cos(a) * r, cy + math.sin(a) * r
        pygame.draw.circle(surf, lerp_color(t["rim"], t["deep"], 0.1),
                           (int(nx), int(ny)), max(3, r // 12))
    pygame.draw.circle(surf, t["rim"], (cx, cy), r, 3)
    pygame.draw.circle(surf, lerp_color(t["rim"], WHITE, 0.3), (cx, cy), r - 1, 1)
    _tier_gem(surf, cx, cy, r, t)
    _drip(surf, cx, cy + r - 2, ink, t["patina"])


# ── sheet assembly ────────────────────────────────────────────────────────────
# The populated wall: 9 badges, 3 columns, mixing earned tiers + locked-with-
# progress (≥2), so the grid is judged AS A WALL at pocket scale.
# (label, glyph_kind, tier, locked, progress-or-None)
WALL = [
    ("GOOSE EGG",   "egg",       "bronze", False, None),
    ("ICARUS",      "icarus",    "silver", False, None),
    ("THE SCROOGE", "scrooge",   "gold",   False, None),
    ("EARLY EXIT",  "stopwatch", "gold",   False, None),
    ("DENIAL",      "denial",    "bronze", False, None),
    ("THE KFC",     "fry",       "silver", False, None),
    ("THE 49ER",    "tomb",      "silver", True,  (3, 10)),
    ("SPLAT",       "ghostwall", "gold",   True,  (7, 25)),
    ("ONE-WAY",     "oneway",    "bronze", True,  (1, 5)),
]


def _grayscale_luma(col):
    """Rec.601 luma of a single RGB triplet (used only for the gem swatch note)."""
    r, g, b = col[:3]
    return 0.299 * r + 0.587 * g + 0.114 * b


def _panel(surf, rect):
    _drop_shadow(surf, rect, 16, blur=6, alpha=150)
    surf.blit(_vgrad_panel(rect.w, rect.h, 16, *_PANEL_BG), rect.topleft)
    pygame.draw.rect(surf, (74, 50, 40), rect.inflate(-7, -7), width=2,
                     border_radius=11)
    pygame.draw.rect(surf, (120, 92, 64), rect, width=1, border_radius=16)


def main():
    pygame.font.init()
    sheet_w, sheet_h = 1180, 760
    sheet = pygame.Surface((sheet_w, sheet_h))
    n = len(_BG_STOPS)
    for y in range(sheet_h):
        f = y / (sheet_h - 1)
        seg = min(n - 2, int(f * (n - 1)))
        local = f * (n - 1) - seg
        pygame.draw.line(sheet, lerp_color(_BG_STOPS[seg], _BG_STOPS[seg + 1], local),
                         (0, y), (sheet_w, y))

    _gradient_text(sheet, "WALL OF SHAME  —  MERGED BADGE (ROUND 3)",
                   _font(20, True), (sheet_w // 2, 28),
                   (255, 240, 180), (200, 150, 70), shadow=True)

    # Measure the honest WHOLE-DISC luma of each tier ONCE, up front, so both the
    # tier proof rows and the grayscale-strip caption print the same numbers.
    disc_luma = {tk: _disc_luma_measured(35, tk)
                 for tk in ("bronze", "silver", "gold")}

    # ── LEFT COLUMN: tier proof + grayscale strip + large detail view ─────────
    lp = pygame.Rect(20, 56, 360, sheet_h - 76)
    _panel(sheet, lp)
    _gradient_text(sheet, "TIER = WHOLE-DISC VALUE", _font(14, True),
                   (lp.centerx, lp.y + 22), (190, 170, 150), (120, 96, 70))

    tiers = [("BRONZE", "bronze"), ("SILVER", "silver"), ("GOLD-TARNISHED", "gold")]
    # the merged badge at REAL pocket scale (~70px ⇒ r≈35) across the 3 tiers
    r_real = 35
    row_y = lp.y + 88
    for tn, tk in tiers:
        bx = lp.x + 64
        badge(sheet, bx, row_y, r_real, tk, "egg", False)
        nm = _font(12, True).render(tn, True, _GOLD_PALE)
        sheet.blit(nm, nm.get_rect(midleft=(bx + 52, row_y - 6)))
        # value note: the HONEST whole-disc luma (round 2 measured face luma and
        # overstated the gap; this is the number the squint test actually sees)
        lum = int(round(disc_luma[tk]))
        ln = _font(9, True).render(f"disc luma {lum}", True, (150, 142, 150))
        sheet.blit(ln, ln.get_rect(midleft=(bx + 52, row_y + 12)))
        row_y += 96

    # grayscale strip — render the three discs, desaturate, prove the value ladder
    strip_y = row_y + 2
    sn = _font(11, True).render("GRAYSCALE — stepped light → dark",
                                True, (190, 180, 170))
    sheet.blit(sn, sn.get_rect(center=(lp.centerx, strip_y)))
    gs = pygame.Surface((lp.w - 60, 64), pygame.SRCALPHA)
    # order brightest → darkest so the strip itself reads as a deliberate ladder
    for j, (_, tk) in enumerate([("GOLD", "gold"), ("SILVER", "silver"),
                                 ("BRONZE", "bronze")]):
        gcx = 50 + j * 100
        badge(gs, gcx, 32, 28, tk, "egg", False)
    # desaturate in place
    for yy in range(gs.get_height()):
        for xx in range(gs.get_width()):
            r_, g_, b_, a_ = gs.get_at((xx, yy))
            if a_ == 0:
                continue
            v = int(0.299 * r_ + 0.587 * g_ + 0.114 * b_)
            gs.set_at((xx, yy), (v, v, v, a_))
    sheet.blit(gs, (lp.x + 30, strip_y + 14))
    # caption the proven ladder under the strip (whole-disc, not face)
    ladder = "  ▸  ".join(
        f"{tn} {int(round(disc_luma[tk]))}"
        for tn, tk in [("G", "gold"), ("S", "silver"), ("B", "bronze")])
    lc = _font(9, True).render("whole-disc luma  " + ladder, True, (170, 162, 170))
    sheet.blit(lc, lc.get_rect(center=(lp.centerx, strip_y + 14 + 64 + 10)))

    # large DETAIL view — the badge big enough to carry crack + heavy patina
    dn = _font(11, True).render("DETAIL VIEW — crack + patina reserved here",
                                True, (190, 180, 170))
    dn_y = strip_y + 14 + 64 + 34
    sheet.blit(dn, dn.get_rect(center=(lp.centerx, dn_y)))
    detail_cy = dn_y + 80
    badge(sheet, lp.centerx, detail_cy, 58, "gold", "scrooge", False, detail=True)
    dl = _font(10, True).render("THE SCROOGE", True, _GOLD_PALE)
    sheet.blit(dl, dl.get_rect(center=(lp.centerx, detail_cy + 80)))

    # ── CENTRE COLUMN: the populated WALL at pocket scale ─────────────────────
    cp = pygame.Rect(400, 56, 470, sheet_h - 76)
    _panel(sheet, cp)
    _gradient_text(sheet, "WALL OF SHAME", _font(16, True),
                   (cp.centerx, cp.y + 22), (190, 170, 150), (120, 96, 70),
                   shadow=True)
    name = _font(13, True).render("SKYDIVER_92", True, _GOLD_PALE)
    sheet.blit(name, name.get_rect(center=(cp.centerx, cp.y + 44)))
    chip_txt = "WALL INSPECTOR"
    cf = _font(10, True)
    ci = cf.render(chip_txt, True, (210, 196, 200))
    cw = ci.get_width() + 24
    chip = pygame.Rect(cp.centerx - cw // 2, cp.y + 54, cw, 18)
    sheet.blit(_vgrad_panel(cw, 18, 9, (66, 48, 56), (40, 30, 36)), chip.topleft)
    pygame.draw.rect(sheet, (140, 110, 116), chip, width=1, border_radius=9)
    sheet.blit(ci, ci.get_rect(center=chip.center))

    grid_top = cp.y + 96
    cols = 3
    col_w = cp.w // cols
    r = 35
    # Locked rows are TALLER so the progress bar + label don't collide with the
    # next badge. Row height is chosen per-ROW from whether any badge is locked.
    rows = [WALL[i:i + cols] for i in range(0, len(WALL), cols)]
    y = grid_top + r
    for row in rows:
        row_locked = any(b[3] for b in row)
        for ci_, (lbl, kind, tier, locked, prog) in enumerate(row):
            gx = cp.x + col_w // 2 + ci_ * col_w
            badge(sheet, gx, y, r, tier, kind, locked, prog)
            cap = _font(9, True).render(lbl, True,
                                        (150, 162, 186) if locked else _GOLD_PALE)
            cap_y = (y + r + 34) if locked else (y + r + 16)
            sheet.blit(cap, cap.get_rect(center=(gx, cap_y)))
        y += (148 if row_locked else 116)

    # ── RIGHT COLUMN: the PINNED hero (V4 ribbon) ─────────────────────────────
    rp = pygame.Rect(890, 56, 270, sheet_h - 76)
    _panel(sheet, rp)
    _gradient_text(sheet, "PINNED SHAME", _font(15, True),
                   (rp.centerx, rp.y + 22), (190, 170, 150), (120, 96, 70))
    note = _font(10, True).render("featured badge — ribbon reserved",
                                  True, (170, 162, 170))
    sheet.blit(note, note.get_rect(center=(rp.centerx, rp.y + 42)))

    pinned_badge(sheet, rp.centerx, rp.y + 150, 64, "gold", "icarus")
    hl = _font(12, True).render("THE ICARUS", True, _GOLD_PALE)
    sheet.blit(hl, hl.get_rect(center=(rp.centerx, rp.y + 240)))
    sub = _font(9, True).render("flew too close to the sun", True, (150, 142, 150))
    sheet.blit(sub, sub.get_rect(center=(rp.centerx, rp.y + 258)))

    # anatomy callout under the hero: the one bold cue
    _gradient_text(sheet, "ONE BOLD CUE", _font(12, True),
                   (rp.centerx, rp.y + 320), (190, 170, 150), (120, 96, 70))
    for j, (tn, tk) in enumerate(tiers):
        ty = rp.y + 360 + j * 56
        t = _TARNISH[tk]
        _tier_gem(sheet, rp.x + 60, ty + 18, 40, t)   # gem only, isolated
        nm = _font(10, True).render(tn, True, _GOLD_PALE)
        sheet.blit(nm, nm.get_rect(midleft=(rp.x + 110, ty + 6)))
        gl = int(_grayscale_luma(t["gem"]))
        gn = _font(9, True).render(f"gem luma {gl}", True, (150, 142, 150))
        sheet.blit(gn, gn.get_rect(midleft=(rp.x + 110, ty + 24)))

    out_dir = "/home/user/skybit/docs/profile/shame_badges"
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "round_3.png")
    pygame.image.save(sheet, out)
    print("WROTE", out, sheet.get_size())
    print("WHOLE-DISC LUMA LADDER:",
          {k: round(v, 1) for k, v in disc_luma.items()})


if __name__ == "__main__":
    main()
