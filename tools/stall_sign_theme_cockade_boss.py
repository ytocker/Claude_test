"""Awning-theme sign concept: COCKADE BOSS PLANK.

The plank says nothing. A plain oxblood board — chamfered, rimmed, keylined —
carries the name and nothing else, so the ONE piece of ornament in the whole
sign is a rosette cockade pinned off its upper-left corner like a finial on a
market awning. Historic cockades are pinwheel-pleated ribbon under a metal
button, which is exactly the read that survives a 360x640 downscale: alternating
cream/oxblood wedges plus one gold bead.

The boss is pinned OFF the corner rather than inside the board so a long label
can never crowd it — the type lives in the clear span to its right, and the
cockade's diameter is a fixed spend the label is not allowed to bid for.

Exploration-only: install() binds the chosen mix-C item hooks, then swaps ONLY
the sign hook; game/ is never edited.
"""
import math

import pygame

import game.store_hub as sh
from game.store_hub import (
    m, font, lerp_color, gradient_text, capped_glow,
    GOLD, GOLD_DEEP, GOLD_A_TOP, GOLD_A_BOT,
    AWN_CREAM, AWN_CREAM_D, LABEL_KEY,
)

OX_TOP = (88, 26, 28)
OX_BOT = (52, 16, 18)
OX_KEY = (46, 14, 16)
# Rims are the plank's only modelling: a lit lip up top, a shade lip below, both
# still far darker than lit thatch so the board never competes with the roof.
# The lit lip is pushed further than it looks on paper because at 2x the keyline
# eats its outer device pixel — only half of it survives the downscale, and a
# timid value would read as mud rather than a machined edge.
OX_RIM_HI = lerp_color(OX_TOP, AWN_CREAM, 0.26)
OX_RIM_LO = lerp_color(OX_BOT, (0, 0, 0), 0.42)

HALF = 42.0            # plank half-width, logical px
H_BOT, H_TOP = 3.0, 13.0   # plank band above body_top
CHAMFER = 2.0
BOSS_DX, BOSS_H, BOSS_R = 43.0, 12.0, 7.5
TEXT_CX = 3.25         # centre of the clear span cx-35.5 .. cx+42


def _plank_points(cx, top_y, bot_y, half, ch):
    """Squared board with clipped corners — no steps, no fishtail, no rail. The
    chamfer is what keeps a plain rectangle from reading as a UI panel."""
    return [
        (cx - half + ch, top_y), (cx + half - ch, top_y),
        (cx + half, top_y + ch), (cx + half, bot_y - ch),
        (cx + half - ch, bot_y), (cx - half + ch, bot_y),
        (cx - half, bot_y - ch), (cx - half, top_y + ch),
    ]


def _cockade(surf, bx, by, r, w1):
    """Eight 45-degree wedges rotated 22.5 degrees so no seam lands vertical or
    horizontal — that offset is the whole difference between a rosette and a
    pie chart. The down-right arc takes the shaded tone of its own colour, which
    keeps the single upper-left key light the rest of the hut is lit by."""
    # The rim is authored one supersampled pixel PROUD of a nominal 1px stroke:
    # at 2x a 2px ring can straddle the downscale box and average away against a
    # cream wedge on one side and lit thatch on the other, which would cost the
    # boss its silhouette. Three device px guarantees one fully-ink pixel at 1x.
    # Wedges are inset behind it over a solid ink disc, so a rasteriser rounding
    # a wedge vertex outward still lands INSIDE the rim — cream never touches
    # the thatch.
    rim_w = w1 + 1
    rw = r - w1
    pygame.draw.circle(surf, LABEL_KEY, (bx, by), r)
    for i in range(8):
        a0 = math.radians(22.5 + 45.0 * i)
        a1 = a0 + math.radians(45.0)
        shaded = i in (7, 0, 1)
        if i % 2 == 0:
            col = AWN_CREAM_D if shaded else AWN_CREAM
        else:
            col = OX_BOT if shaded else OX_TOP
        pts = [(bx, by)]
        steps = 7
        for k in range(steps + 1):
            a = a0 + (a1 - a0) * k / steps
            pts.append((int(round(bx + rw * math.cos(a))),
                        int(round(by + rw * math.sin(a)))))
        pygame.draw.polygon(surf, col, pts)

    pygame.draw.circle(surf, LABEL_KEY, (bx, by), r, rim_w)


def _button(surf, bx, by, br):
    """The one gold in the sign, and the one glow: a struck bead centre."""
    capped_glow(surf, bx, by, m(5), GOLD, 30)
    d = br * 2
    bead = pygame.Surface((d, d), pygame.SRCALPHA)
    for y in range(d):
        pygame.draw.line(bead, lerp_color(GOLD_A_TOP, GOLD_A_BOT,
                                          y / max(1, d - 1)), (0, y), (d, y))
    mask = pygame.Surface((d, d), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (br, br), br)
    bead.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(bead, (bx - br, by - br))
    pygame.draw.circle(surf, GOLD_DEEP, (bx, by), br, 1)


def _sign(surf, ctx):
    cx, scale, label = ctx["cx"], ctx["scale"], ctx["label"]
    body_top = ctx["body_top"]

    def sv(v):
        return int(m(v) * scale)

    w1 = max(1, int(round(m(1.0) * scale)))
    half = sv(HALF)
    top_y, bot_y = body_top - sv(H_TOP), body_top - sv(H_BOT)
    ch = sv(CHAMFER)
    pts = _plank_points(cx, top_y, bot_y, half, ch)

    bx, by = cx - sv(BOSS_DX), body_top - sv(BOSS_H)
    r = sv(BOSS_R)

    # one light, low and upper-left, so board and boss cast the SAME down-right
    # shadow onto the thatch — that shared offset is what pins them together.
    off = max(1, int(m(1.5) * scale))
    shadow = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(shadow, (0, 0, 0, 90),
                        [(x + off, y + off) for x, y in pts])
    pygame.draw.circle(shadow, (0, 0, 0, 90), (bx + off, by + off), r)
    surf.blit(shadow, (0, 0))

    x0, y0 = cx - half, top_y
    bw, bh = half * 2, bot_y - top_y
    body = pygame.Surface((bw, bh), pygame.SRCALPHA)
    cap0, cap1 = w1, bh - w1 - 1
    for y in range(bh):
        if y < w1:
            col = OX_RIM_HI
        elif y > cap1:
            col = OX_RIM_LO
        else:
            col = lerp_color(OX_TOP, OX_BOT,
                             (y - cap0) / max(1, cap1 - cap0))
        pygame.draw.line(body, col, (0, y), (bw, y))
    mask = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255),
                        [(x - x0, y - y0) for x, y in pts])
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(body, (x0, y0))

    pygame.draw.polygon(surf, OX_KEY, pts, 1)

    f = font(11 * scale)
    gradient_text(surf, label, f, (cx + sv(TEXT_CX), (top_y + bot_y) // 2),
                  GOLD_A_TOP, GOLD_A_BOT, weight=m(1.0 * scale),
                  keyline=LABEL_KEY, kw=m(1.0), shadow=False, tracking=m(0.6))

    _cockade(surf, bx, by, r, w1)
    _button(surf, bx, by, sv(2.5))


def install():
    import tools.stall_variant_mixed as mixed
    mixed.install()
    sh.STALL_SIGN_HOOK = _sign
