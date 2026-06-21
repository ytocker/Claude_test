"""TAKEOUT PAIL parcel cosmetic (LOW tier).

The classic Chinese-takeout oyster pail: a trapezoid that SPLAYS wide at the
top and pinches NARROW at the base, a folded red top of two angled fold-tabs
meeting at a centre notch (an inverted-V break along the top edge), and a tall
thin near-semicircular WIRE bail rising clearly above the body.

The whole glyph has to survive a smoothscale down to 22px and the tilt-row
banking, so it is drawn at 2× and the proportions are pushed hard: the
top is twice as wide as the base, the fold-notch is several px across, and the
bail is a 2px wire (4px at 2×) over a dark keyline so it never breaks up. Pinch
dimples at the top rim corners are the cheap, instantly-readable pail cue.
"""
import pygame

from game.parrot import _lerp_color


# Day palette per brief; night relies on the white body self-lighting, with
# only a faint cool keyline so the box doesn't smear into the dark sky.
BODY_HI = (244, 241, 234)        # #F4F1EA white paper, lit edge
BODY_LO = (208, 202, 188)        # shaded fold side for a touch of form
FLAP = (211, 58, 44)             # #D33A2C red fold-tab accent
FLAP_HI = (236, 110, 96)
FLAP_LO = (158, 38, 30)          # shadowed second tab so the fold reads
WIRE = (132, 132, 140)           # #7A7A82-ish grey wire, a touch brighter
WIRE_HI = (188, 188, 198)
OUTLINE = (40, 28, 24)           # dark high-value keyline for the bright sky


def build(mode: str = "normal") -> pygame.Surface:
    # mode is ignored — the pail keeps its own look across every power-up.
    SIZE = 44
    surf = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)

    cx = SIZE // 2

    # Trapezoid body — WIDE at the top, NARROW at the base. Pushed hard so the
    # inverted-taper oyster-pail silhouette survives the smoothscale: the top is
    # twice the base half-width (16 vs 8 at this 2× scale).
    top_y, bot_y = 16, 39
    top_hw, bot_hw = 16, 8
    body = [
        (cx - top_hw, top_y),
        (cx + top_hw, top_y),
        (cx + bot_hw, bot_y),
        (cx - bot_hw, bot_y),
    ]

    # Drop shadow grounds the pail under Pip.
    sh = pygame.Surface((26, 8), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (8, 4, 14, 120), sh.get_rect())
    surf.blit(sh, (cx - 13, bot_y - 1))

    # Tall thin near-semicircular WIRE bail FIRST so the body top edge overlaps
    # its feet — the arch then reads as a flimsy wire rising out of the pail
    # rather than a purse strap. Feet land at the inner top corners; the arch
    # rises well above the body to a clear semicircle. Dark keyline backing so
    # it never breaks up at 22px, then a 2px@22 (4px@2×) grey wire on top.
    foot_y = top_y + 1
    fl_x, fr_x = cx - 9, cx + 9
    arc_top = 3
    arc_rect = pygame.Rect(fl_x, arc_top, (fr_x - fl_x), (foot_y - arc_top) * 2)
    # Keyline backing: stubby legs + the full half-circle arch.
    pygame.draw.line(surf, OUTLINE, (fl_x, foot_y), (fl_x, arc_top + 6), 5)
    pygame.draw.line(surf, OUTLINE, (fr_x, foot_y), (fr_x, arc_top + 6), 5)
    pygame.draw.arc(surf, OUTLINE, arc_rect, 0.0, 3.1416, 5)
    # Grey wire over the keyline.
    pygame.draw.line(surf, WIRE, (fl_x, foot_y), (fl_x, arc_top + 6), 4)
    pygame.draw.line(surf, WIRE, (fr_x, foot_y), (fr_x, arc_top + 6), 4)
    pygame.draw.arc(surf, WIRE, arc_rect, 0.0, 3.1416, 4)
    # Thin top highlight so the wire catches light and reads as round metal.
    pygame.draw.arc(surf, WIRE_HI, arc_rect.inflate(0, -3), 0.5, 2.6, 1)

    # Body outline frame, then a vertical gradient fill clipped to the shape.
    out_body = [
        (cx - top_hw - 2, top_y - 1),
        (cx + top_hw + 2, top_y - 1),
        (cx + bot_hw + 2, bot_y + 2),
        (cx - bot_hw - 2, bot_y + 2),
    ]
    pygame.draw.polygon(surf, OUTLINE, out_body)
    fill = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)
    for y in range(top_y, bot_y + 1):
        t = (y - top_y) / max(1, bot_y - top_y)
        col = _lerp_color(BODY_HI, BODY_LO, t) + (255,)
        fill.fill(col, pygame.Rect(0, y, SIZE, 1))
    mask = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), body)
    fill.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(fill, (0, 0))

    # Lit left edge — gives the white paper a crisp self-lit keyline at night.
    pygame.draw.line(surf, (255, 253, 248),
                     (cx - top_hw + 2, top_y + 3),
                     (cx - bot_hw + 2, bot_y - 2), 1)

    # Folded RED TOP — the hero tell. Two overlapping angled fold-tabs that meet
    # at a centre peak, leaving a wide inverted-V notch break along the top edge
    # so the silhouette is unmistakably the crimped paper top, NOT a flat band.
    notch_w = 5                                  # well past 1px so it survives downscale
    peak_y = top_y - 3                           # tabs rise above the rim into a peak
    fold_y = top_y + 7                           # how far the tabs fold down the body
    # Left tab: rises from the left rim up to the centre peak, folds down.
    pygame.draw.polygon(surf, FLAP, [
        (cx - top_hw, top_y),
        (cx - notch_w, peak_y),
        (cx, top_y + 2),
        (cx - top_hw + 1, fold_y),
    ])
    # Right tab: the second, slightly shadowed flap behind the centre notch.
    pygame.draw.polygon(surf, FLAP_LO, [
        (cx + top_hw, top_y),
        (cx + notch_w, peak_y),
        (cx, top_y + 2),
        (cx + top_hw - 1, fold_y),
    ])
    # Keyline the centre notch + peak edges so the inverted-V break is crisp.
    pygame.draw.line(surf, OUTLINE, (cx - notch_w, peak_y), (cx, top_y + 2), 2)
    pygame.draw.line(surf, OUTLINE, (cx + notch_w, peak_y), (cx, top_y + 2), 2)
    pygame.draw.line(surf, OUTLINE, (cx - top_hw, top_y), (cx - notch_w, peak_y), 1)
    pygame.draw.line(surf, OUTLINE, (cx + top_hw, top_y), (cx + notch_w, peak_y), 1)
    # Lit crease on the front tab.
    pygame.draw.line(surf, FLAP_HI,
                     (cx - top_hw + 2, top_y + 1), (cx - 1, top_y + 1), 1)

    # Wire-attachment PINCH DIMPLES at the top rim corners — small dark notches
    # where the bail pinches the paper, an instantly-readable pail cue.
    pygame.draw.line(surf, OUTLINE, (fl_x - 1, top_y), (fl_x + 1, top_y + 2), 2)
    pygame.draw.line(surf, OUTLINE, (fr_x - 1, top_y + 2), (fr_x + 1, top_y), 2)

    return pygame.transform.smoothscale(surf, (22, 22))
