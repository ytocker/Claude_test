"""ODINWING — Allfather Valkyrie Helm candidate for the Viking redraw (LEGENDARY).

Scratch exploration only; NOT registered in store_skins.BUILDERS, so the live
``skin_viking`` is untouched. This is the showpiece / legendary anchor of the
costume set — where the shipped Viking is a compact iron horn-helm, ODINWING
turns Pip into a war-god ascending: a gold WINGED helm whose two great feathered
wings sweep up-and-out past the crown, a royal-violet-bodied god in a wider fur
mantle, a gold beard with a valknut brooch, and Gungnir carried behind one
shoulder to frame the silhouette.

Read strategy at 40px in priority order: (1) a gold winged HELM with a clear
dome-GAP-wing on each side, (2) a VIOLET-bodied god — the body is recoloured to
deep royal violet via a dedicated palette so the scarlet macaw can't bleed
through and clash with KFC fry-mode — wearing a gold beard + valknut, (3) one
luminous spear framing the SIDE. Gold is the ONLY light-emitting metal in the
set (additive bloom), so the upper ~40% reads as emitted gold and the lower
~60% as solid violet — the body-colour war is won by violet.

The animated tell is the wing-beat: the helm-wings rise on the flap, their
hot-white tips flare on the up-beat, the valknut pulses at the throat, and a
faint gold rim breathes along the violet cape edge at the flap peak.
"""
import math
import pygame

from game import store_skins, parrot
from game.store_skins import HX, HY, CROWN_Y, COMPOSITE_W, COMPOSITE_H, _poly
from game.parrot import _aaellipse
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette

# Gold is the hero metal — helm, wings, spear, valknut share the gold family so
# the war-god's crown reads as one luminous metal. Royal violet is the BODY now
# (not just a cape): a dedicated palette repaints the whole macaw deep violet so
# no scarlet/cobalt parrot wedge survives the 40px shrink and clashes with KFC
# fry-mode. The near-black raven/beard-shadow anchors the bloom.
_GOLD     = (233, 194,  74)        # #E9C24A helm / wings / spear (shimmers)
_GOLD_D   = (176, 126,  40)        # #B07E28 gold shadow / underwing / dark notch
_GOLD_H   = (255, 232, 150)        # bright gold highlight rim
_HOT      = (255, 244, 194)        # #FFF4C2 hot glow core / spear tip / wing-tip
_VIOLET   = ( 86,  64, 128)        # mantle mid
_VIOLET_D = ( 52,  38,  82)        # mantle shadow + lower-body wash
_VIOLET_H = (126, 102, 176)        # fur tuft highlight so the mantle reads furry
_VIOLET_L = ( 68,  50, 104)        # third violet value on the lower body
_RAVEN    = ( 36,  28,  44)        # beard shadow anchor
_FUR      = ( 70,  54,  98)        # mantle mid-tuft so the cape has 3 fur values


# Deep royal-violet repaint of the macaw so the body OWNS the silhouette. Gold
# is reserved for the helm above, so the body palette stays violet end-to-end
# (cheek/crown/lens kept gold-rimmed only as Pip's signature aviator tell). The
# tail and wings carry the darkest violet so the lower-body read is unambiguous.
P_ODIN = _pal(
    tail=[(40, 30, 78), (50, 38, 96), (62, 48, 116), (78, 60, 136)],
    tail_line=(28, 20, 60),
    body_shadow=(44, 32, 82), body_main=(78, 58, 120),
    body_chest=(96, 74, 144), body_belly=(110, 86, 160),
    sheen=(255, 255, 255, 60),
    wing_main=(70, 52, 112), wing_dark=(40, 28, 76), wing_tip=(98, 76, 150),
    wing_secondary=None, wing_highlight=(140, 116, 190),
    head_shadow=(44, 32, 82), head_main=(82, 62, 124),
    head_cheek=(120, 96, 168), head_crown=(96, 74, 144),
    lens_frame=(233, 194, 74), lens_body=(20, 16, 34),
    lens_tint=(80, 60, 140, 120), lens_glint=(255, 255, 255),
    beak_main=(30, 26, 38), beak_dark=(14, 12, 20), beak_gloss=(96, 88, 110),
    foot=(48, 40, 60),
)


def _base_violet(angle_deg):
    return _build_parrot_with_palette(angle_deg, P_ODIN)


def _bloom_layer():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _wing_pts(sgn, cy, lift):
    """Feathered helm-wing as a swept fan of points, mirrored by `sgn`. `lift`
    (0..1, from the flap) raises the tips so the wings beat with Pip's wings.

    Rooted on the dome's SHOULDER (HX ± 11), not its top, so a dark notch can
    sit between the bright dome-top and each wing — the read becomes
    dome-GAP-wing on each side. The inner feather is LOWERED (starts near brow
    height) so the wings clearly spring off the helm's flanks rather than
    sprouting as horns from the crown."""
    rootx = HX + sgn * 11
    rooty = cy + 4
    # Four primary feather tips climbing up-and-out; the third is the hero outer
    # tip carrying the widest, tallest silhouette break (well past the crown).
    t1 = (rootx + sgn * 5,  cy + 1)                       # low inner feather
    t2 = (rootx + sgn * 11, cy - 11 - lift)
    # Round the t3/t4 lift identically (round, not truncate) so the outer tip and
    # trailing tip sit at the SAME height on both wings — the int() truncation
    # used to bias one side a pixel lower/fatter in the store beauty-shot.
    lift16 = int(round(lift * 1.6))
    t3 = (rootx + sgn * 16, cy - 22 - lift16)             # hero outer tip
    t4 = (rootx + sgn * 22, cy - 14 - lift)
    return rootx, rooty, [t1, t2, t3, t4]


def _paint(surf, wing_angle_deg):
    cy = CROWN_Y
    # Base wing angles run +50..-40; map to a 0..1 "flap lift" so the helm-wings,
    # gold shimmer band, and valknut pulse all ride the body's wingbeat. The
    # up-beat (high pulse) is where the wing-tips flare and the cape rim lights.
    lift = int(round((wing_angle_deg + 40) / 90.0 * 5))          # 0..5 px
    pulse = (wing_angle_deg + 40) / 90.0                          # 0..1
    shimmer = int(120 + 110 * (0.5 + 0.5 * math.sin(pulse * math.pi)))

    # ── faint gold aura RING behind the head — a thin annulus that sits OUTSIDE
    # the helm dome so it reads as the legendary's light-emitting tell, never a
    # flood that swallows the violet body. ──
    aura = _bloom_layer()
    for r, a in ((21, 18), (18, 24)):
        pygame.draw.circle(aura, (_GOLD[0], _GOLD[1], _GOLD[2], a), (HX, cy + 1), r, 3)
    surf.blit(aura, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    # ── Gungnir, carried BEHIND the shoulder on one side (near-vertical) so it
    # frames the silhouette without bisecting the face. Drawn FIRST (behind the
    # body) — butt low past the body, hot tip up past the wing-root. ──
    lo = (HX - 17, HY + 26)          # butt, low behind the body
    hi = (HX - 15, CROWN_Y - 16)     # tip, up past the wing on the same side
    dx, dy = hi[0] - lo[0], hi[1] - lo[1]
    blen = math.hypot(dx, dy)
    ux, uy = dx / blen, dy / blen
    px, py = -uy, ux
    glow = _bloom_layer()
    pygame.draw.line(glow, (_GOLD[0], _GOLD[1], _GOLD[2], 70), lo, hi, 5)
    surf.blit(glow, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
    pygame.draw.line(surf, _GOLD_D, lo, hi, 3)
    pygame.draw.line(surf, _GOLD, lo, hi, 1)
    head = [
        (hi[0] + ux * 5, hi[1] + uy * 5),
        (hi[0] + px * 3, hi[1] + py * 3),
        (hi[0] - ux * 4, hi[1] - uy * 4),
        (hi[0] - px * 3, hi[1] - py * 3),
    ]
    _poly(surf, _GOLD_D, head)
    pygame.draw.polygon(surf, _GOLD, head, 1)
    tipglow = _bloom_layer()
    pygame.draw.circle(tipglow, (_HOT[0], _HOT[1], _HOT[2], 150),
                       (int(hi[0] + ux * 4), int(hi[1] + uy * 4)), 2)
    surf.blit(tipglow, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    # ── wider + lower royal-violet fur mantle over the shoulders/back. Pushed
    # out to roughly body width and DOWN past HY+18 so at 40px the lower ~60% of
    # the silhouette is solidly violet — no red/blue parrot wedge survives. Three
    # violet values (shadow / mid / a lower wash) give it furred depth. ──
    mantle = [(HX - 19, HY + 2), (HX - 6, HY - 3), (HX + 11, HY - 2),
              (HX + 17, HY + 9), (HX + 13, HY + 21), (HX - 2, HY + 25),
              (HX - 16, HY + 21)]
    _poly(surf, _VIOLET_D, mantle)
    _poly(surf, _VIOLET, [(HX - 16, HY + 2), (HX - 5, HY - 2), (HX + 9, HY - 1),
                          (HX + 14, HY + 8), (HX + 10, HY + 18), (HX - 3, HY + 21),
                          (HX - 13, HY + 18)])
    # A third, lighter violet wash on the lower-body chest so the belly never
    # falls back to the macaw's underlying tone at the shrink.
    _poly(surf, _VIOLET_L, [(HX - 9, HY + 11), (HX + 8, HY + 12),
                            (HX + 6, HY + 22), (HX - 6, HY + 22)])
    # Fur tufts ringing the collar — alternating mid/highlight nubs so the cape
    # reads as deep fur, not flat cloth, at 40px.
    for i, ang in enumerate(range(-160, 70, 26)):
        rad = math.radians(ang)
        fx = HX + int(15 * math.cos(rad))
        fy = HY + 8 + int(13 * math.sin(rad))
        col = _VIOLET_H if i % 2 == 0 else _FUR
        pygame.draw.circle(surf, col, (fx, fy), 2)

    # ── winged helm dome — bright gold so it carries the head read; the metal
    # mass the wings spring from. Drawn before the wings so they stand off it. ──
    _aaellipse(surf, _GOLD_D, (HX, cy - 1), 13, 10)
    _aaellipse(surf, _GOLD,   (HX, cy - 1), 12, 9)
    _aaellipse(surf, _GOLD_H, (HX - 5, cy - 3), 6, 3)             # dome sheen

    # ── two great golden helm-wings flaring up-and-out PAST the crown — the
    # boldest silhouette-breaker in the set, the showpiece. Each wing roots on
    # the dome's SHOULDER and is separated from the bright dome by a dark notch,
    # so the read is dome-GAP-wing on each side, not a continuous antler. ──
    for sgn in (-1, 1):
        rootx, rooty, tips = _wing_pts(sgn, cy, lift)
        web = [(rootx, rooty + 2)] + tips
        _poly(surf, _GOLD_D, web)                                  # underwing shadow
        web_up = [(rootx, rooty)] + [(p[0], p[1] + 1) for p in tips]
        _poly(surf, _GOLD, web_up)                                 # gold membrane
        # Dark NOTCH: a _GOLD_D wedge pulled 2-3px INWARD off the dome so a clear
        # dark gap sits between dome-top and the wing root on each side.
        notch = [(HX + sgn * 9, cy - 5), (rootx + sgn * 2, rooty - 1),
                 (rootx, rooty + 3)]
        _poly(surf, _GOLD_D, notch)
        # Feather-split ribs fanning to each tip + a bright leading edge.
        for tp in tips:
            pygame.draw.line(surf, _GOLD_D, (rootx, rooty), tp, 1)
        pygame.draw.line(surf, _GOLD_H, (rootx, rooty), tips[-1], 1)
        pygame.draw.line(surf, _GOLD_H, (tips[1][0], tips[1][1]), tips[-1], 1)
        # Hot tip cap — the one tertiary detail that survives downscale; lean on
        # it as the animated accent (it flares on the up-beat in the relight).
        tip = tips[2]
        pygame.draw.circle(surf, _GOLD_H, tip, 2)
        pygame.draw.circle(surf, _HOT, (tip[0] - sgn, tip[1] - 1), 1)
    # Riveted brow band rooting the wings to the helm.
    pygame.draw.line(surf, _GOLD_D, (HX - 12, cy + 5), (HX + 12, cy + 4), 4)
    pygame.draw.line(surf, _GOLD_H, (HX - 12, cy + 4), (HX + 12, cy + 3), 1)

    # ── NASAL guard — a bold gold T: a wide brow band plus a chunky 3px nasal
    # dropping to a point between the eyes. The war-helm signature; spear stays
    # OFF it. ──
    pygame.draw.rect(surf, _GOLD_D, (HX - 6, cy + 3, 14, 4))      # wide brow bar
    pygame.draw.rect(surf, _GOLD,   (HX - 5, cy + 3, 12, 3))
    pygame.draw.polygon(surf, _GOLD_D, [(HX - 1, cy + 6), (HX + 3, cy + 6),
                                        (HX + 1, cy + 17)])        # nasal to a point
    pygame.draw.polygon(surf, _GOLD,   [(HX, cy + 6), (HX + 2, cy + 6),
                                        (HX + 1, cy + 15)])
    pygame.draw.circle(surf, _HOT, (HX + 1, cy + 5), 1)

    # ── one chunky braided beard with ONE bright gold end-ring (tertiary clutter
    # cut: no second tail, no stacked rings). ──
    _aaellipse(surf, _RAVEN, (HX + 2, HY + 9), 8, 8)             # beard shadow mass
    _aaellipse(surf, (58, 48, 64), (HX + 2, HY + 8), 7, 7)      # beard mid
    bx = HX + 2
    pygame.draw.line(surf, (74, 62, 80), (bx, HY + 10), (bx, HY + 19), 3)  # braid
    pygame.draw.circle(surf, _GOLD, (bx, HY + 19), 3)            # one bright end-ring
    pygame.draw.circle(surf, _GOLD_H, (bx - 1, HY + 18), 1)
    pygame.draw.circle(surf, _HOT, (bx - 1, HY + 18), 1)
    # A 1px bright-gold pip on the upper rim of the end-ring (between the valknut
    # base ~HY+10 and the ring ~HY+19) so on the down-beat the dark beard mass and
    # the violet/valknut chest don't merge into one lump — it keeps a lit gold
    # separation line through the throat cluster.
    pygame.draw.circle(surf, _GOLD_H, (bx, HY + 15), 1)

    # ── valknut brooch at the throat — the single bright gold knot, now BIGGER
    # (~7px) and the animated tell: three interlocking triangles whose bloom
    # alpha PULSES on the wingbeat. ──
    vx, vy = HX, HY + 6
    val = _bloom_layer()
    pc = (_HOT[0], _HOT[1], _HOT[2], 80 + int(80 * pulse))
    for off in (-3, 0, 3):
        a = (vx + off, vy - 5)
        b = (vx + off - 5, vy + 4)
        c = (vx + off + 5, vy + 4)
        pygame.draw.lines(val, pc, True, [a, b, c], 1)
    surf.blit(val, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
    for off in (-3, 0, 3):                                        # crisp painted core
        a = (vx + off, vy - 5)
        b = (vx + off - 5, vy + 4)
        c = (vx + off + 5, vy + 4)
        pygame.draw.lines(surf, _GOLD, True, [a, b, c], 1)

    # ── final additive re-light keyed to the flap: the wing-tips flare hot on
    # the up-beat, and a faint gold rim breathes along the violet cape edge so
    # the whole body lifts at the flap peak. The halo/arm-ring budget is spent
    # here instead. ──
    relight = _bloom_layer()
    flare = int(shimmer * pulse)                                  # strongest on up-beat
    for sgn in (-1, 1):
        rootx, rooty, tips = _wing_pts(sgn, cy, lift)
        pygame.draw.line(relight, (_GOLD_H[0], _GOLD_H[1], _GOLD_H[2], shimmer // 4),
                         (rootx, rooty), tips[-1], 1)
        pygame.draw.circle(relight, (_HOT[0], _HOT[1], _HOT[2], 80 + flare // 2),
                           tips[2], 2)
    # Faint gold rim along the violet cape's lower edge — the body breathing.
    rim = [(HX - 16, HY + 18), (HX - 3, HY + 21), (HX + 13, HY + 21)]
    pygame.draw.lines(relight, (_GOLD_H[0], _GOLD_H[1], _GOLD_H[2], 40 + flare // 3),
                      False, rim, 1)
    surf.blit(relight, (0, 0), special_flags=pygame.BLEND_RGB_ADD)


build = store_skins._make_skin(_paint, base_fn=_base_violet)
