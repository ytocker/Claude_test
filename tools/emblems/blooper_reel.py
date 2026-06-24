"""Bespoke engraved center glyphs for the BLOOPER REEL (Wall of Shame).

Nine anti-trophy glyphs, drawn in the same single-colour engrave idiom as
``game/achievement_icons.py`` (a glyph is ``def _glyph_<id>(surf, cx, cy, r,
col)`` of bold filled polygons / thick lines / discs, stamped twice by the
builder for the struck-relief look). The tarnished cracked-pewter frame and
bronze drip supply the gloom — every glyph here puts the JOKE in the
silhouette so it reads as a comedic fail even rendered in flat pewter.

These are authored against the LOCKED v2 concepts: each id resolves to ONE
decisive shape (no figures-plus-props that mud at 44px). The two-tone accent
(the KFC box) routes through ``_accent`` so it stays bronze-monochrome until
the medal is earned — same rule the live module enforces.

Lives under ``tools/`` so it is never bundled; the render harness monkeypatches
``GLYPHS`` into the live module to preview the real medallion frame.
"""
from __future__ import annotations

import math

import pygame

import game.achievement_icons as ai

# Reuse the live module's engraved-shadow tone so the dark sockets/recesses in
# these glyphs match the cast-shadow pass the builder stamps around them.
_SH = ai._GLYPH_SH


def _glyph_goose_egg(surf, cx, cy, r, col):
    # A fat hollow zero — the egg ring IS the scoreless run. Dead-simple: the
    # emptiness is the whole joke, so nothing fills the centre. A short crack
    # bites the upper rim and one sad drip-tick hangs off the bottom.
    w = int(r * 0.78)
    h = int(r * 1.06)
    ring = max(4, r // 7)
    pygame.draw.ellipse(surf, col, (cx - w // 2, cy - h // 2, w, h), ring)
    # hairline crack splitting the top of the shell
    cxr = cx + int(r * 0.10)
    pygame.draw.lines(surf, _SH, False, [
        (cxr, cy - h // 2 + ring),
        (cxr - int(r * 0.10), cy - int(r * 0.18)),
        (cxr + int(r * 0.06), cy - int(r * 0.02)),
    ], max(2, r // 12))
    # one limp drip below — "nothing trickled out"
    by = cy + h // 2
    pygame.draw.line(surf, col, (cx, by), (cx, by + int(r * 0.30)), max(2, r // 12))
    pygame.draw.circle(surf, col, (cx, by + int(r * 0.34)), max(2, r // 11))


def _glyph_icarus(surf, cx, cy, r, col):
    # ONE drooping, shedding wing tilted downward beside a bold down-arrow — the
    # plummet, no figure (v2 lock). The wing sags up-top-left while the arrow
    # punches straight down on the right so the FALL reads even at 44px; a lone
    # feather peels off the wingtip.
    # Drooping wing occupying the upper-left: shoulder up-left, tip sagging down.
    sx, sy = cx - r * 0.78, cy - r * 0.52
    tx, ty = cx + r * 0.22, cy + r * 0.10
    cxp, cyp = cx - r * 0.36, cy - r * 0.78   # control bulges the camber up
    leading = []
    for i in range(9):
        t = i / 8
        mt = 1 - t
        bx = mt * mt * sx + 2 * mt * t * cxp + t * t * tx
        by = mt * mt * sy + 2 * mt * t * cyp + t * t * ty
        leading.append((bx, by))
    lobes = [
        (cx - r * 0.02, cy + r * 0.40),
        (cx - r * 0.36, cy + r * 0.30),
        (cx - r * 0.62, cy + r * 0.02),
    ]
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in leading + lobes])
    # a shed feather drifting away below the wingtip
    fx, fy = cx - int(r * 0.04), cy + int(r * 0.50)
    pygame.draw.ellipse(surf, col, (fx, fy, max(5, int(r * 0.28)),
                                    max(4, int(r * 0.14))))
    # bold downward fall-arrow on the right — the unmistakable plummet
    w = max(4, r // 6)
    ax = cx + int(r * 0.52)
    pygame.draw.line(surf, col, (ax, cy - int(r * 0.60)),
                     (ax, cy + int(r * 0.62)), w)
    pygame.draw.lines(surf, col, False, [
        (ax - int(r * 0.30), cy + int(r * 0.24)),
        (ax, cy + int(r * 0.70)),
        (ax + int(r * 0.30), cy + int(r * 0.24)),
    ], w)


def _glyph_hummingbird(surf, cx, cy, r, col):
    # A panic-flap blur: a small bird body with THREE overlapping wing-arcs
    # fanned behind it (capped at 3 so it never muds to a blob) plus a couple
    # of jitter-ticks. The over-multiplied wings are the joke vs the dignified
    # single wing of flap_life.
    bx, by = cx + int(r * 0.18), cy + int(r * 0.06)
    # bird body — a small teardrop leaning right
    body = [
        (bx - int(r * 0.10), by - int(r * 0.26)),
        (bx + int(r * 0.30), by - int(r * 0.06)),
        (bx + int(r * 0.10), by + int(r * 0.30)),
        (bx - int(r * 0.22), by + int(r * 0.14)),
    ]
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in body])
    # tiny beak
    pygame.draw.polygon(surf, col, [
        (bx + int(r * 0.28), by - int(r * 0.10)),
        (bx + int(r * 0.56), by - int(r * 0.02)),
        (bx + int(r * 0.28), by + int(r * 0.04)),
    ])
    # three motion-blur wing arcs fanned up-left from the shoulder
    w = max(3, r // 9)
    sh = (bx - int(r * 0.12), by - int(r * 0.10))
    for k, (sweep, rad) in enumerate(((0.82, 0.62), (0.58, 0.78), (0.34, 0.92))):
        rect = pygame.Rect(sh[0] - int(r * rad), sh[1] - int(r * rad),
                           int(r * rad * 2), int(r * rad * 2))
        a0 = math.radians(120)
        a1 = math.radians(120 + 110 * sweep)
        pygame.draw.arc(surf, col, rect, a0, a1, w)
    # jitter ticks — the frantic shimmer
    for sgn in (-1, 1):
        jx = bx - int(r * 0.36)
        jy = by + sgn * int(r * 0.40)
        pygame.draw.line(surf, col, (jx, jy), (jx - int(r * 0.16), jy),
                         max(2, r // 13))


def _glyph_denial(surf, cx, cy, r, col):
    # A sheet-ghost phasing INTO a pillar edge: the rounded-top scalloped ghost
    # half-overlaps a bold vertical wall on the right, with a "thunk" impact
    # burst where it hits. Ties to the Ghost power-up; the joke is phasing the
    # WRONG way — into the wall, not the gap.
    # the wall the ghost rams — a thick vertical bar on the right
    wall_x = cx + int(r * 0.46)
    wall_w = max(5, int(r * 0.26))
    pygame.draw.rect(surf, col, (wall_x, cy - int(r * 0.92), wall_w, int(r * 1.84)))
    # ghost body: rounded dome + scalloped hem, pushed left so it overlaps wall
    gx = cx - int(r * 0.18)
    gw = int(r * 0.92)
    top = cy - int(r * 0.62)
    dome = pygame.Rect(gx - gw // 2, top, gw, int(r * 0.92))
    pygame.draw.ellipse(surf, col, (dome.x, dome.y, dome.w, dome.h))
    pygame.draw.rect(surf, col, (dome.x, top + int(r * 0.30), gw, int(r * 0.62)))
    # scalloped hem — three bumps
    hy = top + int(r * 0.92)
    bump = gw // 3
    for i in range(3):
        bx = dome.x + bump // 2 + i * bump
        pygame.draw.circle(surf, col, (bx, hy), bump // 2 + 1)
    # carve the hem notches back out with the shadow tone
    for i in range(2):
        nx = dome.x + bump + i * bump
        pygame.draw.circle(surf, _SH, (nx, hy + int(r * 0.06)), bump // 3)
    # two dark eyes
    for dx in (-0.18, 0.14):
        pygame.draw.circle(surf, _SH, (gx + int(dx * r), top + int(r * 0.42)),
                           max(2, r // 9))
    # "thunk" impact burst where ghost meets wall
    ix, iy = wall_x, cy - int(r * 0.06)
    for a in (-0.5, 0.0, 0.5):
        ex = ix + int(math.cos(a) * r * 0.30)
        ey = iy + int(math.sin(a) * r * 0.30)
        pygame.draw.line(surf, col, (ix, iy), (ex, ey), max(2, r // 12))


def _glyph_kfc_incident(surf, cx, cy, r, col):
    # The fry bucket KNOCKED OVER (tipped ~35°) with fries spilling out and a
    # grease-splat tick — died in fry mode. Distinct from upright greasy_fingers
    # by the tilt + the spill. The red box accent stays bronze until earned.
    ang = math.radians(36)
    ca, sa = math.cos(ang), math.sin(ang)

    def rot(px, py):
        # rotate a local (right=+x, down=+y) point about the bucket centre
        return (cx + int(px * ca - py * sa), cy + int(px * sa + py * ca))

    # tilted trapezoid tub — wide mouth (left, where it spills), narrow base
    tl = rot(-r * 0.02, -r * 0.50)
    tr = rot(-r * 0.02, r * 0.50)
    br = rot(r * 0.70, r * 0.34)
    bl = rot(r * 0.70, -r * 0.34)
    tub = [tl, tr, br, bl]
    pygame.draw.polygon(surf, ai._accent((214, 74, 60)), tub)
    pygame.draw.polygon(surf, col, tub, max(2, r // 14))
    # fries spilling OUT of the mouth (up-left), fanned at angles
    mouth = rot(-r * 0.02, 0)
    for da, ln in ((-0.55, 0.74), (-0.18, 0.86), (0.20, 0.78)):
        fa = ang + math.pi + da   # point away from the base, out the mouth
        ex = mouth[0] + int(math.cos(fa) * r * ln)
        ey = mouth[1] + int(math.sin(fa) * r * ln)
        sx = mouth[0] + int(math.cos(fa) * r * 0.10)
        sy = mouth[1] + int(math.sin(fa) * r * 0.10)
        pygame.draw.line(surf, col, (sx, sy), (ex, ey), max(3, r // 9))
    # grease-splat tick under the spill
    gx, gy = cx - int(r * 0.30), cy + int(r * 0.62)
    pygame.draw.circle(surf, col, (gx, gy), max(3, r // 8))
    pygame.draw.circle(surf, col, (gx - int(r * 0.20), gy + int(r * 0.10)),
                       max(2, r // 13))


def _glyph_so_close(surf, cx, cy, r, col):
    # Abstract "this close" pinch (v2 lock — bars, not fingers): two short
    # opposed bars closing toward a tiny gap, a near-miss spark crackling in
    # the gap. Distinct from the nerve-spike near-misses by being a static
    # pinch, not a pulse line.
    bar_w = max(4, int(r * 0.22))
    bar_len = int(r * 0.78)
    gap = int(r * 0.16)
    # top bar pressing down toward the gap
    pygame.draw.rect(surf, col, (cx - bar_w // 2, cy - gap // 2 - bar_len,
                                 bar_w, bar_len), border_radius=max(1, r // 14))
    # bottom bar pressing up
    pygame.draw.rect(surf, col, (cx - bar_w // 2, cy + gap // 2,
                                 bar_w, bar_len), border_radius=max(1, r // 14))
    # spark in the gap — a 4-point twinkle, "so close"
    s = int(r * 0.30)
    pygame.draw.line(surf, col, (cx - s, cy), (cx + s, cy), max(2, r // 12))
    pygame.draw.line(surf, col, (cx, cy - int(s * 0.7)), (cx, cy + int(s * 0.7)),
                     max(2, r // 12))
    for dx, dy in ((-0.6, -0.6), (0.6, -0.6), (-0.6, 0.6), (0.6, 0.6)):
        pygame.draw.line(surf, col, (cx, cy),
                         (cx + int(dx * s * 0.7), cy + int(dy * s * 0.7)),
                         max(1, r // 16))


def _glyph_lottery_loser(surf, cx, cy, r, col):
    # The slot WINDOW frame with 3 bold MISMATCHED dots and a downward sad-tick.
    # The frame + tone carry it (v2 lock — don't render legible $ / star / skull
    # micro-symbols); the deliberate non-match (three different fills) reads as
    # the loss. A sad down-tick hangs under the window.
    fw = int(r * 1.56)
    fh = int(r * 1.00)
    fx = cx - fw // 2
    fy = cy - fh // 2 - int(r * 0.06)
    # slot-window frame — heavy bezel rectangle
    pygame.draw.rect(surf, col, (fx, fy, fw, fh), max(3, r // 9),
                     border_radius=max(2, r // 7))
    # two reel divider lines splitting the window into three cells
    for i in (1, 2):
        dx = fx + i * fw // 3
        pygame.draw.line(surf, col, (dx, fy + 2), (dx, fy + fh - 2), max(2, r // 14))
    # three mismatched marks — distinguished by SHAPE-fill, not legible symbol:
    # cell 0 = solid disc, cell 1 = hollow ring, cell 2 = bar. The mismatch is
    # the read.
    cyc = fy + fh // 2
    c0 = fx + fw // 6
    c1 = fx + fw // 2
    c2 = fx + 5 * fw // 6
    mr = max(4, int(r * 0.20))
    pygame.draw.circle(surf, col, (c0, cyc), mr)                       # disc
    pygame.draw.circle(surf, col, (c1, cyc), mr, max(2, r // 12))      # ring
    pygame.draw.rect(surf, col, (c2 - mr, cyc - mr // 2, mr * 2, mr),  # bar
                     border_radius=max(1, r // 16))
    # sad down-tick under the window
    sx = cx
    sy = fy + fh + int(r * 0.06)
    pygame.draw.line(surf, col, (sx, sy), (sx, sy + int(r * 0.22)), max(2, r // 12))
    pygame.draw.lines(surf, col, False, [
        (sx - int(r * 0.12), sy + int(r * 0.10)),
        (sx, sy + int(r * 0.26)),
        (sx + int(r * 0.12), sy + int(r * 0.10)),
    ], max(2, r // 13))


def _glyph_the_49er(surf, cx, cy, r, col):
    # A snapped sandstone pillar with a small lamp-wisp floating just past its
    # broken top (v2 lock — NO numerals). The snapped shaft = the death at 49;
    # the unreachable genie lamp-wisp = the irony of the 50-pillar genie you
    # never reached.
    shaft_w = max(5, int(r * 0.34))
    px = cx - int(r * 0.22)
    base_y = cy + int(r * 0.84)
    cap_h = max(3, int(r * 0.16))
    cap_w = int(shaft_w * 1.5)
    # base block
    pygame.draw.rect(surf, col, (px - cap_w // 2, base_y - cap_h, cap_w, cap_h),
                     border_radius=max(1, r // 16))
    # lower (standing) stump of the shaft, with a jagged snapped top
    break_y = cy - int(r * 0.04)
    pygame.draw.rect(surf, col, (px - shaft_w // 2, break_y, shaft_w,
                                 base_y - cap_h - break_y))
    # jagged fracture across the break
    pygame.draw.polygon(surf, col, [
        (px - shaft_w // 2, break_y),
        (px - int(shaft_w * 0.12), break_y - int(r * 0.16)),
        (px + int(shaft_w * 0.18), break_y - int(r * 0.04)),
        (px + shaft_w // 2, break_y - int(r * 0.20)),
        (px + shaft_w // 2, break_y),
    ])
    # the toppled upper chunk, fallen aside (tilted) lower-left
    chunk = [
        (px - int(r * 0.58), cy + int(r * 0.30)),
        (px - int(r * 0.18), cy + int(r * 0.18)),
        (px - int(r * 0.06), cy + int(r * 0.52)),
        (px - int(r * 0.46), cy + int(r * 0.64)),
    ]
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in chunk])
    # the unreachable lamp-wisp floating past the broken top (upper-right)
    lx, ly = cx + int(r * 0.50), cy - int(r * 0.52)
    lamp = pygame.Rect(lx - int(r * 0.26), ly, int(r * 0.50), int(r * 0.24))
    pygame.draw.ellipse(surf, col, lamp)
    # lamp spout
    pygame.draw.polygon(surf, col, [
        (lx + int(r * 0.20), ly + int(r * 0.04)),
        (lx + int(r * 0.42), ly - int(r * 0.06)),
        (lx + int(r * 0.22), ly + int(r * 0.16)),
    ])
    # a tiny wisp curling up from the spout — the genie just out of reach
    pygame.draw.arc(surf, col, (lx - int(r * 0.10), ly - int(r * 0.42),
                                int(r * 0.36), int(r * 0.40)),
                    -math.pi * 0.1, math.pi * 0.8, max(2, r // 13))


def _glyph_night_owl(surf, cx, cy, r, col):
    # An owl FACE with X-ed-out eyes and ear-tufts (v2 lock — DROP the moon).
    # A round head, two ear-tufts, two big X eyes joined by a brow ridge, and a
    # small beak. The X eyes = "the night got you" comedic-bleak read.
    head_r = int(r * 0.66)
    pygame.draw.circle(surf, col, (cx, cy + int(r * 0.04)), head_r, max(4, r // 8))
    # two ear-tufts poking up
    for sgn in (-1, 1):
        ex = cx + sgn * int(r * 0.42)
        ey = cy - int(r * 0.40)
        pygame.draw.polygon(surf, col, [
            (ex - int(r * 0.10), ey + int(r * 0.22)),
            (ex + sgn * int(r * 0.16), ey - int(r * 0.20)),
            (ex + int(r * 0.10), ey + int(r * 0.22)),
        ])
    # brow ridge joining the eyes (owl's signature facial-disc bar)
    pygame.draw.line(surf, col, (cx - int(r * 0.42), cy - int(r * 0.10)),
                     (cx + int(r * 0.42), cy - int(r * 0.10)), max(3, r // 11))
    # two X eyes
    ew = max(2, r // 11)
    ex_r = int(r * 0.20)
    for sgn in (-1, 1):
        exc = cx + sgn * int(r * 0.30)
        eyc = cy + int(r * 0.08)
        pygame.draw.line(surf, col, (exc - ex_r, eyc - ex_r),
                         (exc + ex_r, eyc + ex_r), ew)
        pygame.draw.line(surf, col, (exc - ex_r, eyc + ex_r),
                         (exc + ex_r, eyc - ex_r), ew)
    # small beak
    pygame.draw.polygon(surf, col, [
        (cx - int(r * 0.10), cy + int(r * 0.34)),
        (cx + int(r * 0.10), cy + int(r * 0.34)),
        (cx, cy + int(r * 0.54)),
    ])


GLYPHS = {
    "goose_egg": _glyph_goose_egg,
    "icarus": _glyph_icarus,
    "hummingbird": _glyph_hummingbird,
    "denial": _glyph_denial,
    "kfc_incident": _glyph_kfc_incident,
    "so_close": _glyph_so_close,
    "lottery_loser": _glyph_lottery_loser,
    "the_49er": _glyph_the_49er,
    "night_owl": _glyph_night_owl,
}
