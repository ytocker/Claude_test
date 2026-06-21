"""TAKEOUT PAIL parcel cosmetic (LOW tier).

The classic Chinese-takeout paper pail: a trapezoid narrower at the BASE,
two folded top flaps, and a thin arched wire handle. The trapezoid + the
half-circle handle loop is the whole glyph at 22px — so the body stays a
single bold silhouette and the handle is drawn 2px (4px at 2×) to survive
the smoothscale and the tilt-row banking.
"""
import pygame

from game.parrot import _lerp_color


# Day palette per brief; night relies on the white body self-lighting, with
# only a faint cool keyline so the box doesn't smear into the dark sky.
BODY_HI = (244, 241, 234)        # #F4F1EA white paper, lit edge
BODY_LO = (212, 206, 192)        # shaded fold side for a touch of form
FLAP = (211, 58, 44)             # #D33A2C red fold-flap accent
FLAP_HI = (236, 110, 96)
WIRE = (122, 122, 130)           # #7A7A82 grey wire
WIRE_HI = (170, 170, 180)
OUTLINE = (40, 28, 24)           # dark high-value keyline for the bright sky


def build(mode: str = "normal") -> pygame.Surface:
    # mode is ignored — the pail keeps its own look across every power-up.
    SIZE = 44
    surf = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)

    cx = SIZE // 2

    # Trapezoid body — WIDER at the top, NARROWER at the base (the pail tell).
    top_y, bot_y = 18, 38
    top_hw, bot_hw = 14, 10
    body = [
        (cx - top_hw, top_y),
        (cx + top_hw, top_y),
        (cx + bot_hw, bot_y),
        (cx - bot_hw, bot_y),
    ]

    # Drop shadow grounds the pail under Pip.
    sh = pygame.Surface((30, 8), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (8, 4, 14, 120), sh.get_rect())
    surf.blit(sh, (cx - 15, bot_y - 2))

    # Wire handle FIRST so the body's top edge overlaps its feet — the arch
    # then reads as rising out of the box rather than floating above it.
    hl_x, hr_x = cx - 10, cx + 10
    foot_y = top_y + 2
    arc_top = 5
    pygame.draw.line(surf, OUTLINE, (hl_x, foot_y), (cx - 9, arc_top + 2), 5)
    pygame.draw.line(surf, OUTLINE, (hr_x, foot_y), (cx + 9, arc_top + 2), 5)
    arc_rect = pygame.Rect(cx - 9, arc_top - 4, 18, 16)
    pygame.draw.arc(surf, OUTLINE, arc_rect, 0.15, 3.0, 5)
    # Grey wire on top of the dark keyline, 2px@22 (4px@2×).
    pygame.draw.line(surf, WIRE, (hl_x, foot_y), (cx - 9, arc_top + 2), 3)
    pygame.draw.line(surf, WIRE, (hr_x, foot_y), (cx + 9, arc_top + 2), 3)
    pygame.draw.arc(surf, WIRE, arc_rect, 0.15, 3.0, 3)
    pygame.draw.arc(surf, WIRE_HI, arc_rect.inflate(0, -2), 1.2, 2.6, 1)

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
                     (cx - top_hw + 2, top_y + 2),
                     (cx - bot_hw + 2, bot_y - 2), 1)

    # Red folded top flaps — a wide band with a central notch reads as the two
    # crimped flaps even when fine detail dies at 22px.
    flap_y0, flap_y1 = top_y, top_y + 6
    pygame.draw.polygon(surf, FLAP, [
        (cx - top_hw, flap_y0), (cx + top_hw, flap_y0),
        (cx + top_hw - 2, flap_y1), (cx - top_hw + 2, flap_y1),
    ])
    # Central V notch between the two flaps.
    pygame.draw.polygon(surf, OUTLINE, [
        (cx - 2, flap_y0), (cx + 2, flap_y0), (cx, flap_y0 + 4),
    ])
    pygame.draw.line(surf, FLAP_HI,
                     (cx - top_hw + 2, flap_y0 + 1),
                     (cx - 2, flap_y0 + 1), 1)

    return pygame.transform.smoothscale(surf, (22, 22))
