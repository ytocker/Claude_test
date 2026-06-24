"""
Bespoke engraved center glyphs for the SHAME — Lifetime Lows (Wall of Shame)
medallions, rendered TARNISHED (cracked-pewter anti-trophy).

These follow the single-colour engrave idiom of ``game.achievement_icons``:
each ``_glyph_<id>(surf, cx, cy, r, col)`` lays BOLD filled shapes in the passed
``col`` only — the builder strokes a down-right inset shadow + up-left sheen for
the struck-relief look, so the glyph hard-codes no fills of its own. Authored in
the ~22px legibility floor: nothing thinner than ~3px or smaller than ~5px.

The joke lives in the silhouette (per the v2 LOCKED spec):
  * the_scrooge   — a ``$`` coin draped with cobweb-strands from one corner and
                    a hanging dust-drip: money that gathered dust, never spent.
  * early_checkout — a counter bell rung once + ONE bold down-arrow: "rang and
                    left" — bailed in under 3 seconds.

WRITE-ONLY module: imports ``game`` read-only and never mutates it; the render
harness merges ``GLYPHS`` into a private copy of the badge glyph table.
"""
from __future__ import annotations

import math
import pygame


def _ring_dollar(surf, cx, cy, r, col, rr):
    # The in-game `$` coin read, matching `_glyph_coin`: a bold ring with a
    # struck `$` centred in it. Kept as a helper so the Scrooge coin reuses the
    # exact Riches silhouette — the neglect cue (web/dust), not the coin, is the
    # only thing that distinguishes this from a wealth emblem.
    pygame.draw.circle(surf, col, (cx, cy), rr, max(3, r // 8))
    f = _glyph_font(int(rr * 1.7))
    g = f.render("$", True, col)
    surf.blit(g, g.get_rect(center=(cx, cy)))


def _glyph_the_scrooge(surf, cx, cy, r, col):
    # A `$` coin neglected into dust: the coin sits low-right while a cobweb is
    # slung across its upper-left corner (three radiating strands + two sagging
    # cross-threads), and a single bead drips off the coin's underside. The web
    # over money is the whole read — "never spent, never taken".
    rr = int(r * 0.50)
    coin_cx = cx + int(r * 0.14)
    coin_cy = cy + int(r * 0.12)
    _ring_dollar(surf, coin_cx, coin_cy, r, col, rr)

    # Cobweb slung across the coin's upper-left corner: radiating strands from a
    # corner anchor, tied together by sagging cross-threads so the read is a
    # corner spiderweb (neglect/dust), not a starburst. Bold strands so the web
    # survives the engrave + crack at 44px.
    web_w = max(3, r // 8)
    ax = cx - int(r * 0.78)        # anchor corner (upper-left)
    ay = cy - int(r * 0.78)
    # Three radiating strands sweeping down-right, fanned wide enough to drape
    # over the coin's upper-left quadrant.
    strand_angles = (math.radians(2), math.radians(36), math.radians(70))
    strand_len = r * 1.30
    ends = []
    for a in strand_angles:
        ex = ax + math.cos(a) * strand_len
        ey = ay + math.sin(a) * strand_len
        ends.append((ex, ey))
        pygame.draw.line(surf, col, (ax, ay), (int(ex), int(ey)), web_w)

    # Two concentric arcs of cross-thread connecting adjacent strands. Each
    # segment sags outward (away from the corner) for the slack-web droop.
    cross_w = max(3, r // 11)
    for frac in (0.50, 0.84):
        prev = None
        for (ex, ey) in ends:
            px = ax + (ex - ax) * frac
            py = ay + (ey - ay) * frac
            if prev is not None:
                mx = (prev[0] + px) * 0.5 + r * 0.07
                my = (prev[1] + py) * 0.5 + r * 0.09
                pygame.draw.lines(surf, col, False,
                                  [(int(prev[0]), int(prev[1])),
                                   (int(mx), int(my)),
                                   (int(px), int(py))], cross_w)
            prev = (px, py)

    # A single dust-drip hanging off the coin's lower edge — the "gathered dust"
    # tick. A short stem + a teardrop bead, bold enough to survive at 44px.
    dx = coin_cx - int(r * 0.10)
    dsy = coin_cy + rr + max(2, r // 12)
    dby = dsy + int(r * 0.30)
    pygame.draw.line(surf, col, (dx, dsy), (dx, dby), max(3, r // 11))
    pygame.draw.circle(surf, col, (dx, dby), max(4, int(r * 0.16)))


def _glyph_early_checkout(surf, cx, cy, r, col):
    # A counter bell rung once, with ONE bold down-arrow beside it: "checked out
    # immediately". The bell is the dome + base plate + a button-cap on top; the
    # down-arrow says "left". Shifted left so the arrow has its own column.
    bx = cx - int(r * 0.22)        # bell centre column

    # Base plate — a flat rounded slab the dome sits on.
    base_w = int(r * 1.04)
    base_h = max(4, int(r * 0.20))
    base_y = cy + int(r * 0.40)
    pygame.draw.rect(surf, col, (bx - base_w // 2, base_y, base_w, base_h),
                     border_radius=max(2, r // 9))

    # Dome — a half-disc seated on the plate. Drawn as a filled circle whose
    # lower half is clipped by the plate, giving a clean bell hump.
    dome_r = int(r * 0.50)
    dome_cy = base_y - int(dome_r * 0.10)
    pygame.draw.circle(surf, col, (bx, dome_cy), dome_r)
    pygame.draw.rect(surf, col, (bx - dome_r, dome_cy, dome_r * 2,
                                 dome_r + base_h), 0)  # square off below centre

    # Button-cap — the strike knob on top of the dome.
    cap_r = max(4, int(r * 0.15))
    pygame.draw.circle(surf, col, (bx, dome_cy - dome_r - cap_r // 2 + 1), cap_r)

    # ONE bold down-arrow to the right — "leaving". A thick shaft + a wide
    # arrowhead, sized to read as a decisive exit, not a tick.
    ax = cx + int(r * 0.62)
    a_top = cy - int(r * 0.46)
    a_tip = cy + int(r * 0.56)
    shaft_w = max(4, int(r * 0.18))
    pygame.draw.line(surf, col, (ax, a_top), (ax, a_tip - int(r * 0.18)), shaft_w)
    head = int(r * 0.30)
    pygame.draw.polygon(surf, col, [
        (ax, a_tip),
        (ax - head, a_tip - head),
        (ax + head, a_tip - head),
    ])


# Font cache for the `$` glyph — mirrors `achievement_icons._glyph_font` so the
# coin face matches the Riches family exactly.
_glyph_fonts: dict = {}


def _glyph_font(px: int):
    f = _glyph_fonts.get(px)
    if f is None:
        f = pygame.font.SysFont(None, px, bold=True)
        _glyph_fonts[px] = f
    return f


GLYPHS = {
    "the_scrooge": _glyph_the_scrooge,
    "early_checkout": _glyph_early_checkout,
}
