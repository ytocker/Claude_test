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
# The lip is authored one supersampled pixel PROUD of the nominal stroke so the
# keyline can eat its outermost row and a full device row still survives the
# downscale — a thicker, calmer lip reads as a machined edge where a thin bright
# one only read as a stray highlight.
OX_RIM_HI = lerp_color(OX_TOP, AWN_CREAM, 0.24)
OX_RIM_LO = lerp_color(OX_BOT, (0, 0, 0), 0.42)
# The boss lands ON the board, and oxblood-on-oxblood gave its ink rim nothing
# to cut against there. A brass collar seats it — same metal as the bead, so the
# ornament stays one object rather than gaining a second accent colour.
BOSS_COLLAR = GOLD_DEEP

# Cream is the brightest thing the sign owns, and the merchandise has to out-rank
# the signage that points at it — so the lit cream is compressed toward its own
# shade tone rather than run at full awning white.
CREAM_LIT = lerp_color(AWN_CREAM, AWN_CREAM_D, 0.18)

HALF = 42.0            # plank half-width, logical px
H_BOT, H_TOP = 1.75, 14.25  # plank band above body_top
CHAMFER = 2.0
BOSS_DX, BOSS_H, BOSS_R = 43.0, 12.0, 7.5
TEXT_CX = 4.5          # centre of the clear span cx-35.5 .. cx+42
# Uppercase labels leave the font's descender space empty, so a bitmap-centred
# line sits high in the band; this drops the ink block back onto the band's
# optical centre and buys the cap the same clear field the baseline gets.
TEXT_DY = 1.0


def _plank_points(cx, top_y, bot_y, half, ch):
    """Squared board with clipped corners — no steps, no fishtail, no rail. The
    chamfer is what keeps a plain rectangle from reading as a UI panel."""
    return [
        (cx - half + ch, top_y), (cx + half - ch, top_y),
        (cx + half, top_y + ch), (cx + half, bot_y - ch),
        (cx + half - ch, bot_y), (cx - half + ch, bot_y),
        (cx - half, bot_y - ch), (cx - half, top_y + ch),
    ]


def _key_pass(rw, peak):
    """ONE diagonal lighting ramp for the whole rosette, dark toward down-right.

    Per-wedge shade tones made every wedge its own local decision, and the one
    shaded cream wedge boxed in by two shaded oxblood wedges averaged to mud at
    1x. Lighting the rosette as a single object instead keeps every wedge a full
    step apart from BOTH its neighbours — the ramp moves the pair together.
    """
    d = rw * 2 + 1
    s = pygame.Surface((d, d), pygame.SRCALPHA)
    span = 2 * (d - 1)
    for k in range(span + 1):
        t = k / max(1, span)
        a = int(peak * max(0.0, (t - 0.30) / 0.70))
        if a <= 0:
            continue
        if k <= d - 1:
            p0, p1 = (0, k), (k, 0)
        else:
            p0, p1 = (k - d + 1, d - 1), (d - 1, k - d + 1)
        pygame.draw.line(s, (0, 0, 0, a), p0, p1)
    mask = pygame.Surface((d, d), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (rw, rw), rw)
    s.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return s


def _cockade(surf, bx, by, r, w1):
    """Eight 45-degree wedges rotated 22.5 degrees so no seam lands vertical or
    horizontal — that offset is the whole difference between a rosette and a
    pie chart."""
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
        col = CREAM_LIT if i % 2 == 0 else OX_TOP
        pts = [(bx, by)]
        steps = 7
        for k in range(steps + 1):
            a = a0 + (a1 - a0) * k / steps
            pts.append((int(round(bx + rw * math.cos(a))),
                        int(round(by + rw * math.sin(a)))))
        pygame.draw.polygon(surf, col, pts)

    surf.blit(_key_pass(rw, 56), (bx - rw, by - rw))
    pygame.draw.circle(surf, LABEL_KEY, (bx, by), r, rim_w)


def _collar(surf, pts, bx, by, r, w1):
    """A seated ring under the boss, clipped to the board so it exists only where
    the disc actually lies on oxblood — a collar on the board side, not a second
    outline floating over the thatch."""
    pad = r + m(4)
    s = pygame.Surface((pad * 2, pad * 2), pygame.SRCALPHA)
    pygame.draw.circle(s, BOSS_COLLAR, (pad, pad), r + m(1), max(2, w1 + 1))
    mask = pygame.Surface((pad * 2, pad * 2), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255),
                        [(x - bx + pad, y - by + pad) for x, y in pts])
    s.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(s, (bx - pad, by - pad))


def _button(surf, bx, by, br, scale):
    """The one gold in the sign: a struck bead centre, ringed in the label's own
    ink so it seats INTO the cream instead of dissolving into it. Its glow is
    scaled with the hut and kept faint — a wide warm bloom only bleached the
    cream wedges it sat on and bought the bead no extra read."""
    capped_glow(surf, bx, by, max(1, int(m(5) * scale)), GOLD, 18)
    d = br * 2
    bead = pygame.Surface((d, d), pygame.SRCALPHA)
    for y in range(d):
        pygame.draw.line(bead, lerp_color(GOLD_A_TOP, GOLD_A_BOT,
                                          y / max(1, d - 1)), (0, y), (d, y))
    mask = pygame.Surface((d, d), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (br, br), br)
    bead.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(bead, (bx - br, by - br))
    pygame.draw.circle(surf, LABEL_KEY, (bx, by), br, 2)


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
    # The cast is cut off at the board's own floor line: the plank now sits low
    # enough that an un-clipped shadow would be the one thing crossing onto the
    # awning below.
    off = max(1, int(m(1.5) * scale))
    shadow = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(shadow, (0, 0, 0, 90),
                        [(x + off, y + off) for x, y in pts])
    pygame.draw.circle(shadow, (0, 0, 0, 90), (bx + off, by + off), r)
    floor = body_top - max(1, sv(1.5))
    surf.blit(shadow, (0, 0), pygame.Rect(0, 0, surf.get_width(), floor))

    x0, y0 = cx - half, top_y
    bw, bh = half * 2, bot_y - top_y
    body = pygame.Surface((bw, bh), pygame.SRCALPHA)
    lip = w1 + 1
    cap0, cap1 = lip, bh - w1 - 1
    for y in range(bh):
        if y < lip:
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

    # The four clipped corners are the only place the board can show its
    # thickness, so each return carries an inner lit line — that is what turns a
    # chamfer into a sawn end rather than a rounded-off rectangle.
    k = w1
    for (ax, ay), (bx2, by2), (nx, ny) in (
        (pts[0], pts[7], (1, 1)), (pts[1], pts[2], (-1, 1)),
        (pts[5], pts[6], (1, -1)), (pts[4], pts[3], (-1, -1)),
    ):
        pygame.draw.line(surf, OX_RIM_HI, (ax + nx * k, ay + ny * k),
                         (bx2 + nx * k, by2 + ny * k), 1)

    f = font(11 * scale)
    gradient_text(surf, label, f,
                  (cx + sv(TEXT_CX), (top_y + bot_y) // 2 + sv(TEXT_DY)),
                  GOLD_A_TOP, GOLD_A_BOT, weight=m(1.0 * scale),
                  keyline=LABEL_KEY, kw=m(0.5), shadow=False, tracking=m(0.6))

    _collar(surf, pts, bx, by, r, w1)
    _cockade(surf, bx, by, r, w1)
    _button(surf, bx, by, sv(2.5), scale)


def install():
    import tools.stall_variant_mixed as mixed
    mixed.install()
    sh.STALL_SIGN_HOOK = _sign
