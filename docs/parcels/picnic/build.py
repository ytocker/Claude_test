"""PICNIC BASKET parcel cosmetic (MID tier).

A wicker picnic basket: a wide rounded BASKET body, a tall DOUBLE-ARCH
handle springing from the rim, and a red-check CLOTH bulge spilling over
the rim. At 22px the read is the combined glyph — handle arch over a fat
rounded body with a bright check lump breaking the rim line. Weave is
suggested with ≤3 horizontal hatch lines (fine wicker dies at this size);
the silhouette + one warm body colour + the red/cream check carry it.

The handle is the rotation-survival anchor: a bold dark-keylined arch that
stays legible banked from −25° to 90°, so the basket still reads as a
basket at every tilt the bird flies through.
"""
import pygame

from game.parrot import _lerp_color


# Day palette per brief.
WICKER_HI = (197, 150, 88)        # lit wicker, lighter than #B98A4A base
WICKER_BASE = (185, 138, 74)      # #B98A4A wicker body
WICKER_LO = (146, 104, 54)        # shaded lower belly
WEAVE = (126, 90, 42)             # #7E5A2A darker weave hatch
CLOTH_RED = (217, 67, 58)         # #D9433A red-check cloth
CLOTH_CREAM = (244, 236, 224)     # #F4ECE0 cream check
OUTLINE = (52, 32, 16)            # dark high-value keyline for the bright sky
HANDLE_HI = (210, 166, 104)       # lit cane on the handle's inner edge


def build(mode: str = "normal") -> pygame.Surface:
    # mode is ignored — the basket keeps its cosy look across every power-up.
    SIZE = 44
    surf = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)
    cx = SIZE // 2

    # Basket body geometry — WIDE and rounded, the cosy-domestic tell.
    rim_y = 24                     # top rim line
    bot_y = 38                     # rounded bottom
    top_hw = 15                    # half-width at the rim
    bot_hw = 12                    # slightly tapered base

    # Drop shadow grounds the basket under Pip.
    sh = pygame.Surface((34, 8), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (8, 4, 14, 120), sh.get_rect())
    surf.blit(sh, (cx - 17, bot_y - 2))

    # Double-arch HANDLE first so the rim + cloth overlap its feet — the arch
    # then reads as rising out of the basket, not floating above it. Two thin
    # arcs side by side give the "double-arch" tell; a 5px dark keyline under a
    # 3px cane keeps the handle alive through the smoothscale and the bank.
    foot_y = rim_y - 1
    arc_top = 5
    # Outer dark keyline arch.
    h_rect = pygame.Rect(cx - 11, arc_top, 22, 24)
    pygame.draw.arc(surf, OUTLINE, h_rect, 0.32, 2.82, 5)
    pygame.draw.line(surf, OUTLINE, (cx - 10, arc_top + 9), (cx - 10, foot_y), 5)
    pygame.draw.line(surf, OUTLINE, (cx + 10, arc_top + 9), (cx + 10, foot_y), 5)
    # Cane fill + inner-edge highlight; a second inner arc reads as the twin
    # handle band without adding clutter at 22px.
    pygame.draw.arc(surf, WICKER_BASE, h_rect, 0.32, 2.82, 3)
    pygame.draw.line(surf, WICKER_BASE, (cx - 10, arc_top + 9), (cx - 10, foot_y), 3)
    pygame.draw.line(surf, WICKER_BASE, (cx + 10, arc_top + 9), (cx + 10, foot_y), 3)
    pygame.draw.arc(surf, HANDLE_HI, h_rect.inflate(-4, -4), 0.5, 2.6, 1)

    # Body OUTLINE frame — an inflated rounded body behind the gradient fill.
    out_rect = pygame.Rect(cx - top_hw - 2, rim_y - 2,
                           (top_hw + 2) * 2, bot_y - rim_y + 4)
    pygame.draw.rect(surf, OUTLINE, out_rect, border_radius=7)

    # Gradient body fill clipped to a rounded basket shape.
    body_rect = pygame.Rect(cx - top_hw, rim_y, top_hw * 2, bot_y - rim_y + 1)
    fill = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)
    for y in range(body_rect.top, body_rect.bottom):
        t = (y - body_rect.top) / max(1, body_rect.height - 1)
        col = _lerp_color(WICKER_HI, WICKER_LO, t) + (255,)
        fill.fill(col, pygame.Rect(0, y, SIZE, 1))
    mask = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), body_rect, border_radius=6)
    fill.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(fill, (0, 0))

    # Weave suggestion — ≤3 horizontal hatch lines. A thicker rim band reads as
    # the bound top edge; two thin courses below hint at the wicker rows.
    pygame.draw.line(surf, WEAVE, (cx - top_hw + 1, rim_y + 3),
                     (cx + top_hw - 1, rim_y + 3), 2)
    pygame.draw.line(surf, WEAVE, (cx - top_hw + 2, rim_y + 7),
                     (cx + top_hw - 2, rim_y + 7), 1)
    pygame.draw.line(surf, WEAVE, (cx - bot_hw + 1, rim_y + 11),
                     (cx + bot_hw - 1, rim_y + 11), 1)
    # Vertical weave ticks on the rim band give a wicker over-under read.
    for vx in range(cx - top_hw + 3, cx + top_hw - 1, 5):
        pygame.draw.line(surf, WEAVE, (vx, rim_y + 1), (vx, rim_y + 5), 1)

    # Bound RIM line sits over the body top, a high-value lid edge the cloth
    # bulges over.
    pygame.draw.line(surf, OUTLINE, (cx - top_hw, rim_y),
                     (cx + top_hw, rim_y), 2)
    pygame.draw.line(surf, WICKER_HI, (cx - top_hw + 2, rim_y - 1),
                     (cx + top_hw - 4, rim_y - 1), 1)

    # CLOTH bulge — the "full" personality. A cream lobe spilling over the rim,
    # outlined dark so it pops on the bright sky, with two red check blocks so
    # the red-check tell survives even when the fine grid dies at 22px.
    cloth_pts = [
        (cx - 11, rim_y + 1), (cx - 9, rim_y - 4), (cx - 4, rim_y - 6),
        (cx + 2, rim_y - 6), (cx + 8, rim_y - 4), (cx + 11, rim_y + 1),
    ]
    pygame.draw.polygon(surf, OUTLINE, _expand(cloth_pts, cx, rim_y, 1))
    pygame.draw.polygon(surf, CLOTH_CREAM, cloth_pts)
    # Red check blocks alternating with the cream ground.
    pygame.draw.rect(surf, CLOTH_RED, pygame.Rect(cx - 9, rim_y - 4, 4, 4))
    pygame.draw.rect(surf, CLOTH_RED, pygame.Rect(cx - 1, rim_y - 5, 4, 4))
    pygame.draw.rect(surf, CLOTH_RED, pygame.Rect(cx + 5, rim_y - 3, 3, 4))
    pygame.draw.rect(surf, CLOTH_RED, pygame.Rect(cx - 5, rim_y - 1, 4, 3))
    pygame.draw.rect(surf, CLOTH_RED, pygame.Rect(cx + 3, rim_y - 1, 3, 3))
    # Cream highlight catch on the crest of the bulge.
    pygame.draw.line(surf, (255, 252, 246), (cx - 4, rim_y - 5),
                     (cx + 1, rim_y - 5), 1)

    return pygame.transform.smoothscale(surf, (22, 22))


def _expand(pts, cx, baseline, grow):
    """Push the cloth lobe points outward from its centre to bake a 1px dark
    keyline behind the bulge so it reads against a bright sky."""
    out = []
    for x, y in pts:
        dx = 1 if x > cx else (-1 if x < cx else 0)
        dy = -1 if y < baseline else 1
        out.append((x + dx * grow, y + dy * grow))
    return out
