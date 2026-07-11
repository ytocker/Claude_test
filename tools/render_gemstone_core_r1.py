"""Round-1 concept render for the `gemstone-core` item-card redesign.

Headless-only exploration harness (never imported by the game): authors the
legendary GEMSTONE-CORE card on a 2x supersample canvas so the reviewer can
judge the asymmetric facet fan + caustic light-play + kitsune contrast on git.
"""
import os
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, "/home/user/skybit")

import math
import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game.draw import lerp_color, NEAR_BLACK, WHITE          # noqa: E402
from game.hud import _font                                    # noqa: E402
from game.animal_kitsune import build_kitsune, build_kitsune_aura  # noqa: E402


# ── legendary palette (locked) ───────────────────────────────────────────────
GEM = (255, 202, 104)
GLOW = (255, 168, 58)
DEEP = (150, 92, 22)
CARD_BASE = (8, 8, 20)
SPEC = (255, 240, 200)

# 2x author canvas for the card body.
CW, CH = 324, 200
# Fan origin sits BEHIND the fox (slightly left of centre) so facets fan
# asymmetrically outward — NOT a card-centred starburst.
ORIGIN = (140, 100)
R_INNER = 15            # facet bases carry width so the fan never pinches to a dot


def _pt(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def _facet(surf, p_i, p_j, inner_col, outer_col, bands=44):
    """One flat crystalline facet: a wedge from the fan origin out to the card
    edge, filled by a radial gradient (bright gem at the deep interior, deepening
    to the near-black rim). The inner edge carries width off R_INNER so the base
    reads as a cut plane, not a spoke."""
    ox, oy = ORIGIN
    di = math.hypot(p_i[0] - ox, p_i[1] - oy) or 1
    dj = math.hypot(p_j[0] - ox, p_j[1] - oy) or 1
    inner_a = (ox + (p_i[0] - ox) / di * R_INNER, oy + (p_i[1] - oy) / di * R_INNER)
    inner_b = (ox + (p_j[0] - ox) / dj * R_INNER, oy + (p_j[1] - oy) / dj * R_INNER)
    for k in range(bands):
        t0, t1 = k / bands, (k + 1) / bands
        a0 = _pt(inner_a, p_i, t0)
        a1 = _pt(inner_a, p_i, t1)
        b0 = _pt(inner_b, p_j, t0)
        b1 = _pt(inner_b, p_j, t1)
        col = lerp_color(inner_col, outer_col, (t0 + t1) * 0.5)
        pygame.draw.polygon(surf, col, [a0, a1, b1, b0])
    return inner_a, inner_b


def _spec_line(surf, inner, outer):
    """Thin 1px specular glint raking the UPPER radial edge of a facet so each
    cut plane catches a hard highlight along its lit lip."""
    ln = pygame.Surface((CW, CH), pygame.SRCALPHA)
    pygame.draw.line(ln, (*SPEC, 120), inner, outer, 1)
    surf.blit(ln, (0, 0), special_flags=pygame.BLEND_ADD)


def build_card():
    surf = pygame.Surface((CW, CH), pygame.SRCALPHA)
    # Deep near-black crystal interior.
    surf.fill((*CARD_BASE, 255))

    # Perimeter split points, CLOCKWISE from top-left, corners INCLUDED so no
    # facet straddles a corner. Chosen asymmetric: the widest, brightest facets
    # own the LEFT and RIGHT margins (where the real estate is) and no facet
    # collapses to a sliver at the top or bottom edge.
    perim = [
        (0, 0), (112, 0), (206, 0),            # top edge
        (CW - 1, 0), (CW - 1, 66), (CW - 1, 138),   # right edge (wide margin)
        (CW - 1, CH - 1), (214, CH - 1), (118, CH - 1),  # bottom edge
        (0, CH - 1), (0, 148), (0, 58),        # left edge (wide margin)
    ]

    # Draw each facet, then a dark keyline + a top-edge specular so the ~12
    # planes stay broad + well-separated (the legendary facet-count signal).
    n = len(perim)
    edges = []
    for i in range(n):
        p_i = perim[i]
        p_j = perim[(i + 1) % n]
        # Slight per-facet brightness jitter keeps the cut from reading uniform;
        # every facet still stays BELOW the fox — the fox is drawn last, on top.
        warm = 0.86 + 0.14 * math.sin(i * 1.7)
        inner_col = lerp_color(GEM, GLOW, 0.22 * (1 - warm) + 0.0)
        outer_col = lerp_color(DEEP, NEAR_BLACK, 0.30)
        ia, ib = _facet(surf, p_i, p_j, inner_col, outer_col)
        edges.append((ia, ib, p_i, p_j))

    # Dark separator keylines down each shared radial seam.
    for ia, ib, p_i, p_j in edges:
        pygame.draw.line(surf, (4, 4, 12), ia, p_i, 1)
    # Specular on the UPPER radial lip of every facet (whichever seam sits higher).
    for ia, ib, p_i, p_j in edges:
        if p_i[1] <= p_j[1]:
            _spec_line(surf, ia, p_i)
        else:
            _spec_line(surf, ib, p_j)

    # ── caustic light-streaks (LEGENDARY-ONLY) ───────────────────────────────
    # Diagonal refracted glints raking across 2-3 facets at ~30deg — the
    # internal light-play that reads as premium cut stone. Additive, so they
    # only ever brighten, never muddy the facet gradient.
    caustics = pygame.Surface((CW, CH), pygame.SRCALPHA)
    streaks = [
        ((250, 40), 62, (255, 244, 210), 110),
        ((280, 96), 74, (255, 226, 168), 96),
        ((60, 150), 66, (255, 236, 190), 100),
        ((46, 78), 52, (255, 240, 200), 88),
    ]
    ang = math.radians(-30)
    dx, dy = math.cos(ang), math.sin(ang)
    for (sx, sy), length, col, a in streaks:
        x0 = (sx - dx * length / 2, sy - dy * length / 2)
        x1 = (sx + dx * length / 2, sy + dy * length / 2)
        pygame.draw.line(caustics, (*col, a), x0, x1, 3)
        pygame.draw.line(caustics, (*col, max(0, a - 45)), x0, x1, 1)
    surf.blit(caustics, (0, 0), special_flags=pygame.BLEND_ADD)

    # ── kitsune hero — aura BEHIND, sprite on top; the brightest element ──────
    sprite = build_kitsune(20)
    aura = build_kitsune_aura()
    fox = pygame.transform.smoothscale(sprite, (160, 210))
    halo = pygame.transform.smoothscale(aura, (160, 210))
    fr = fox.get_rect(center=(140, 100))
    surf.blit(halo, fr.topleft)
    surf.blit(fox, fr.topleft)

    # ── price plaque: beveled rhombus in the lower-right margin ───────────────
    pcx, pcy = 264, 160
    hw, hh = 30, 14
    dia = [(pcx - hw, pcy), (pcx, pcy - hh), (pcx + hw, pcy), (pcx, pcy + hh)]
    plaque = pygame.Surface((CW, CH), pygame.SRCALPHA)
    pygame.draw.polygon(plaque, (*CARD_BASE, 235), dia)          # dark card fill
    pygame.draw.polygon(plaque, (*lerp_color(DEEP, NEAR_BLACK, 0.2), 255), dia, 3)
    pygame.draw.polygon(plaque, (*GEM, 210), dia, 1)             # thin gold bevel
    surf.blit(plaque, (0, 0))
    pf = _font(16, True)
    price = pf.render("3,500", True, GEM)
    surf.blit(price, price.get_rect(center=(pcx, pcy - 1)))

    # thin card keyline so the body reads as a discrete card on the sheet.
    pygame.draw.rect(surf, (*lerp_color(DEEP, NEAR_BLACK, 0.15), 255),
                     surf.get_rect(), 2)
    return surf


def main():
    card = build_card()

    # Review sheet: hero card at 2x author scale + a 1x downscale for scale check.
    pad = 26
    small = pygame.transform.smoothscale(card, (162, 100))
    sheet_w = CW + pad * 2
    sheet_h = pad + 26 + CH + 30 + 100 + pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((18, 18, 26))

    tf = _font(15, True)
    lf = _font(11, True)
    sheet.blit(tf.render("gemstone-core  ·  LEGENDARY  ·  round 1",
                         True, (236, 226, 244)), (pad, 8))
    y = pad + 26
    sheet.blit(card, (pad, y))
    sheet.blit(lf.render("324x200 · 2x author canvas", True, (150, 150, 168)),
               (pad, y + CH + 4))
    y2 = y + CH + 30
    sheet.blit(small, (pad, y2))
    sheet.blit(lf.render("1x in-game scale (162x100)", True, (150, 150, 168)),
               (pad + 172, y2 + 40))

    out = "/home/user/skybit/docs/item_card_redesign/gemstone-core/round_1.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("saved:", out)


if __name__ == "__main__":
    main()
