"""ODINWING — Allfather Valkyrie Helm candidate for the Viking redraw (LEGENDARY).

Scratch exploration only; NOT registered in store_skins.BUILDERS, so the live
``skin_viking`` is untouched. This is the showpiece / legendary anchor of the
costume set — where the shipped Viking is a compact iron horn-helm, ODINWING
turns Pip into a war-god ascending: a glowing golden WINGED helm whose two great
feathered wings sweep up-and-out past the crown, a raven launching off one
shoulder, a royal-violet fur mantle clasped with a pulsing valknut brooch, and
Gungnir — a slender glowing spear — crossing the body luminous.

Read strategy at 40px in motion: the doubled gold wings are the boldest, widest
silhouette-breaker in the whole set, flaring past the crown on both sides so the
bird's egg outline is unmistakably crowned. It is also the ONLY light-emitting
skin in the set — the gold helm/wings/spear/valknut are additively bloomed
(BLEND_RGB_ADD) onto SRCALPHA layers so the gold reads as EMITTED light, not
paint, matching the disco-shimmer / astro-visor masking idiom already in
store_skins. The still frame already reads as a winged-helm war-god (helm dome +
nasal + two gold wings + beard-rings + raven + spear); the wing-keyed shimmer
just makes the gold breathe and the runic halo drift so it feels alive in flight.

Layering, back-to-front: gold bloom aura halo → fur+violet cape mantle → raven
at the wing-root → two great golden helm-wings flaring past the crown → winged
helm dome + nasal-guard → braided beard with gold rings → valknut brooch at the
throat → Gungnir spear crossing the body → drifting runic-mark halo + arm-rings,
all re-lit by a final additive gold bloom pass keyed to the flap.
"""
import math
import pygame

from game import store_skins, parrot
from game.store_skins import HX, HY, CROWN_Y, COMPOSITE_W, COMPOSITE_H, _poly
from game.parrot import _aaellipse

# Gold is the hero — helm, wings, spear, rings, valknut all share the gold
# family so the war-god reads as one luminous metal; the royal violet fur is the
# single cool contrast that keeps the gold from going flat, and the near-black
# raven/beard-shadow anchors the silhouette so the bloom has something to sit on.
_GOLD     = (233, 194,  74)        # #E9C24A helm / wings / spear (shimmers)
_GOLD_D   = (184, 134,  43)        # #B8862B gold shadow / underwing
_GOLD_H   = (255, 232, 150)        # bright gold highlight rim
_HOT      = (255, 244, 194)        # #FFF4C2 hot glow core / spear tip / valknut
_VIOLET   = ( 74,  58, 107)        # #4A3A6B royal-violet fur cape (cool contrast)
_VIOLET_D = ( 48,  37,  72)
_VIOLET_H = (118,  98, 160)        # fur tuft highlight so the mantle reads furry
_RAVEN    = ( 42,  32,  48)        # #2A2030 raven + beard shadow
_RAVEN_H  = ( 78,  66,  88)        # raven feather sheen so it isn't a flat blob
_FUR      = ( 62,  50,  88)        # mantle mid so the cape has 3 fur values


def _bloom_layer():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _wing_pts(sgn, cy, lift):
    """Feathered helm-wing as a swept fan of points, mirrored by `sgn`. `lift`
    (0..1, from the flap) raises the tips so the wings beat with Pip's wings —
    a war-god's helm-wings breathe with the body. Rooted at the brow band and
    sweeping HIGH and WIDE past the crown so the doubled span is the boldest
    silhouette in the set — the read can't lean on the helm dome alone."""
    rootx = HX + sgn * 8
    rooty = cy + 3
    # Four primary feather tips climbing up-and-out; the third is the hero outer
    # tip carrying the widest, tallest silhouette break (well past the crown).
    t1 = (rootx + sgn * 7,  cy - 9)
    t2 = (rootx + sgn * 14, cy - 17 - lift)
    t3 = (rootx + sgn * 19, cy - 25 - int(lift * 1.6))   # hero outer tip
    t4 = (rootx + sgn * 24, cy - 18 - lift)
    return rootx, rooty, [t1, t2, t3, t4]


def _paint(surf, wing_angle_deg):
    cy = CROWN_Y
    # Base wing angles run +50..-40; map to a 0..1 "flap lift" so the helm-wings,
    # gold shimmer band, and runic halo all pulse with the body's wingbeat.
    lift = int(round((wing_angle_deg + 40) / 90.0 * 5))          # 0..5 px
    pulse = (wing_angle_deg + 40) / 90.0                          # 0..1
    shimmer = int(120 + 110 * (0.5 + 0.5 * math.sin(pulse * math.pi)))

    # ── soft gold aura RING behind the head — a thin annulus of glow that sits
    # OUTSIDE the helm dome so it reads as a halo, never a flood that swallows
    # the face. Kept faint so the metal detail wins; it's the legendary's tell
    # that this is the one light-emitting skin. ──
    aura = _bloom_layer()
    for r, a in ((22, 20), (19, 26), (16, 30)):
        pygame.draw.circle(aura, (_GOLD[0], _GOLD[1], _GOLD[2], a), (HX, cy + 1), r, 3)
    surf.blit(aura, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    # ── fur + royal-violet cape mantle over the shoulders/back (drawn first so
    # everything else sits on it). Deep fur collar sweeping from the back of the
    # neck around the throat. ──
    mantle = [(HX - 16, HY + 3), (HX - 6, HY - 2), (HX + 9, HY - 1),
              (HX + 14, HY + 8), (HX + 6, HY + 17), (HX - 12, HY + 16)]
    _poly(surf, _VIOLET_D, mantle)
    _poly(surf, _VIOLET, [(HX - 13, HY + 3), (HX - 5, HY - 1), (HX + 8, HY),
                          (HX + 11, HY + 7), (HX + 4, HY + 14), (HX - 10, HY + 13)])
    # Fur tufts ringing the collar — alternating mid/highlight nubs so the cape
    # reads as deep fur, not flat cloth, at 40px.
    for i, ang in enumerate(range(-150, 60, 30)):
        rad = math.radians(ang)
        fx = HX + int(13 * math.cos(rad))
        fy = HY + 6 + int(11 * math.sin(rad))
        col = _VIOLET_H if i % 2 == 0 else _FUR
        pygame.draw.circle(surf, col, (fx, fy), 2)

    # ── raven (Huginn/Muninn) perched at the LEFT wing-root, wings half-open as
    # if about to launch — a near-black silhouette accent breaking the shoulder.
    rx, ry = HX - 14, HY - 2
    _aaellipse(surf, _RAVEN, (rx, ry), 4, 5)                       # body
    _aaellipse(surf, _RAVEN, (rx + 1, ry - 5), 3, 3)              # head
    # Half-open wings flaring up — the launch read.
    _poly(surf, _RAVEN, [(rx - 1, ry - 2), (rx - 8, ry - 8), (rx - 3, ry + 2)])
    _poly(surf, _RAVEN, [(rx + 2, ry - 2), (rx - 2, ry - 9), (rx + 4, ry - 1)])
    pygame.draw.line(surf, _RAVEN_H, (rx - 1, ry - 3), (rx - 6, ry - 7), 1)
    _poly(surf, _GOLD, [(rx + 3, ry - 5), (rx + 6, ry - 5), (rx + 4, ry - 3)])  # beak
    pygame.draw.circle(surf, _HOT, (rx + 2, ry - 6), 1)            # eye glint

    # ── winged helm dome — bright gold so it carries the head read; the metal
    # mass the wings spring from. Drawn FIRST so the wings clearly stand off it. ──
    _aaellipse(surf, _GOLD_D, (HX, cy - 1), 13, 10)
    _aaellipse(surf, _GOLD,   (HX, cy - 1), 12, 9)
    _aaellipse(surf, _GOLD_H, (HX - 5, cy - 3), 6, 3)             # dome sheen

    # ── two great golden helm-wings flaring up-and-out PAST the crown — the
    # boldest silhouette-breaker in the set. Each wing leads with a DARK base
    # edge against the dome so it reads as a separate feathered wing, not more
    # dome; bright gold membrane, dark feather-split ribs, hot outer tip. ──
    for sgn in (-1, 1):
        rootx, rooty, tips = _wing_pts(sgn, cy, lift)
        web = [(rootx, rooty + 2)] + tips
        _poly(surf, _GOLD_D, web)                                  # underwing shadow
        web_up = [(rootx, rooty)] + [(p[0], p[1] + 1) for p in tips]
        _poly(surf, _GOLD, web_up)                                 # gold membrane
        # Dark trailing/inner edge welds the wing-root to the helm AND separates
        # the two wings from the bright dome between them.
        pygame.draw.line(surf, _GOLD_D, (rootx, rooty), tips[0], 2)
        # Feather-split ribs fanning to each tip + a bright leading edge.
        for tp in tips:
            pygame.draw.line(surf, _GOLD_D, (rootx, rooty), tp, 1)
        pygame.draw.line(surf, _GOLD_H, (rootx, rooty), tips[-1], 1)
        pygame.draw.line(surf, _GOLD_H, (tips[1][0], tips[1][1]), tips[-1], 1)
        # Hot tip cap so the outer point survives downscale + carries the glow.
        tip = tips[2]
        pygame.draw.circle(surf, _GOLD_H, tip, 2)
        pygame.draw.circle(surf, _HOT, (tip[0] - sgn, tip[1] - 1), 1)
    # Riveted brow band rooting the wings to the helm.
    pygame.draw.line(surf, _GOLD_D, (HX - 12, cy + 5), (HX + 12, cy + 4), 4)
    pygame.draw.line(surf, _GOLD_H, (HX - 12, cy + 4), (HX + 12, cy + 3), 1)
    for rxp in (HX - 8, HX, HX + 8):
        pygame.draw.circle(surf, _GOLD_H, (rxp, cy + 5), 1)
    # Nasal guard dropping over the brow — the war-helm signature.
    pygame.draw.rect(surf, _GOLD_D, (HX, cy + 4, 3, 12))
    pygame.draw.rect(surf, _GOLD, (HX, cy + 4, 2, 11))
    pygame.draw.circle(surf, _HOT, (HX + 1, cy + 5), 1)

    # ── regal braided beard with gold beard-rings, faintly lit from the helm. ──
    _aaellipse(surf, _RAVEN, (HX + 2, HY + 8), 9, 8)             # beard shadow mass
    _aaellipse(surf, (58, 46, 60), (HX + 2, HY + 7), 8, 7)      # beard mid
    # Two plaited tails with stacked gold rings.
    for bx in (HX - 1, HX + 6):
        for j in range(3):
            yy = HY + 11 + j * 3
            pygame.draw.circle(surf, (74, 60, 76), (bx, yy), 2)
            pygame.draw.circle(surf, _GOLD, (bx, yy), 2, 1)       # gold ring
        pygame.draw.circle(surf, _GOLD_H, (bx, HY + 19), 2)      # bright end-ring
        pygame.draw.circle(surf, _HOT, (bx - 1, HY + 18), 1)

    # ── valknut brooch at the throat — three interlocking triangles, pulsing
    # soft gold (the pulse alpha rides the wingbeat). ──
    vx, vy = HX - 6, HY + 9
    val = _bloom_layer()
    pc = (_HOT[0], _HOT[1], _HOT[2], 70 + int(60 * pulse))
    for off in (0, 3, 6):
        a = (vx + off, vy - 4)
        b = (vx + off - 4, vy + 3)
        c = (vx + off + 4, vy + 3)
        pygame.draw.lines(val, pc, True, [a, b, c], 1)
    surf.blit(val, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
    for off in (0, 3, 6):                                         # crisp painted core
        a = (vx + off, vy - 4)
        b = (vx + off - 4, vy + 3)
        c = (vx + off + 4, vy + 3)
        pygame.draw.lines(surf, _GOLD, True, [a, b, c], 1)

    # ── Gungnir — slender glowing spear held diagonally across the body, tip
    # catching a hot gold-white glint up past the wing on the far side. Drawn as
    # a bloomed shaft so it reads luminous, then a crisp painted core. ──
    lo = (HX - 20, HY + 24)          # butt, down past the body
    hi = (HX + 20, CROWN_Y - 14)     # tip, up past the wing
    dx, dy = hi[0] - lo[0], hi[1] - lo[1]
    blen = math.hypot(dx, dy)
    ux, uy = dx / blen, dy / blen
    px, py = -uy, ux
    glow = _bloom_layer()
    pygame.draw.line(glow, (_GOLD[0], _GOLD[1], _GOLD[2], 70), lo, hi, 5)
    surf.blit(glow, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
    pygame.draw.line(surf, _GOLD_D, lo, hi, 3)
    pygame.draw.line(surf, _GOLD, lo, hi, 1)
    # Leaf-shaped spearhead at the tip.
    head = [
        (hi[0] + ux * 5, hi[1] + uy * 5),
        (hi[0] + px * 3, hi[1] + py * 3),
        (hi[0] - ux * 4, hi[1] - uy * 4),
        (hi[0] - px * 3, hi[1] - py * 3),
    ]
    _poly(surf, _GOLD_D, head)
    pygame.draw.polygon(surf, _GOLD, head, 1)
    pygame.draw.circle(surf, _HOT, (int(hi[0] + ux * 4), int(hi[1] + uy * 4)), 2)
    # Gold haft-ring binding near the grip.
    gxp = lo[0] + ux * blen * 0.42
    gyp = lo[1] + uy * blen * 0.42
    pygame.draw.line(surf, _GOLD_H, (gxp + px * 2, gyp + py * 2),
                     (gxp - px * 2, gyp - py * 2), 2)

    # ── gold arm-ring at the wing-root (the war-god's torc). ──
    pygame.draw.circle(surf, _GOLD, (HX + 13, HY + 11), 3, 1)
    pygame.draw.circle(surf, _GOLD_H, (HX + 14, HY + 9), 1)

    # ── drifting runic-mark halo orbiting the head — small gold tick-marks at
    # orbit angles offset by the flap so they appear to drift; additively
    # bloomed as a soft particle shimmer. ──
    halo = _bloom_layer()
    base = pulse * math.tau
    for i in range(7):
        ang = base + i * (math.tau / 7)
        ox = HX + int(22 * math.cos(ang))
        oy = (cy + 1) + int(15 * math.sin(ang))
        a = shimmer if i % 2 == 0 else shimmer // 2
        # Tiny rune tick (a short diagonal stroke) — a drifting gold mark.
        pygame.draw.line(halo, (_GOLD_H[0], _GOLD_H[1], _GOLD_H[2], a),
                         (ox - 1, oy + 1), (ox + 1, oy - 1), 1)
    surf.blit(halo, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    # ── final gold bloom re-light: a faint additive shimmer that travels ALONG
    # the wing leading-edges and the spear, NOT a disc over the dome — so the
    # gold breathes on the flap peak without washing the face flat. This is the
    # legendary's animated shimmer that justifies the tier. ──
    relight = _bloom_layer()
    for sgn in (-1, 1):
        rootx, rooty, tips = _wing_pts(sgn, cy, lift)
        pygame.draw.line(relight, (_GOLD_H[0], _GOLD_H[1], _GOLD_H[2], shimmer // 4),
                         (rootx, rooty), tips[-1], 1)
        pygame.draw.circle(relight, (_HOT[0], _HOT[1], _HOT[2], shimmer // 3),
                           tips[2], 2)
    surf.blit(relight, (0, 0), special_flags=pygame.BLEND_RGB_ADD)


build = store_skins._make_skin(_paint)
