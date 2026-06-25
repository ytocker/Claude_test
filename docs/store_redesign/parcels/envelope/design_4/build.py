"""POST OFFICE — LOW-tier ENVELOPE parcel cosmetic.

A franked vintage postal envelope: a manila slab struck by a bold round rubber-
stamp CANCELLATION mark across the top-right. The inked concentric rings are the
identity — the only "postmarked / in-transit" read in the envelope roster — so
they are drawn the boldest, biggest, most legible mark on the sprite. A small
perforated postage stamp sits in the opposite corner and a few faint address
ruling lines keep the body from reading as a blank card.

It is the FLATTEST object in the parcel roster — a slab, not a volume — and is
carried below Pip rotating with his bank, so the read must survive the rotozoom
at every flight angle on DAY *and* NIGHT sky. The cancellation rings are kept
bold and concentric (no micro-text) so the circle still reads as a postmark at
22px; the body shape stays off the surface edges so the in-game rotozoom never
clips its corners.
"""
import math

import pygame

from game.draw import lerp_color as _lerp_color

# DAY manila / shade plus a NIGHT-friendly warm keyline so the slab still reads
# on a dark sky without changing the sprite per mode.
MANILA_BASE = (217, 185, 126)   # ~#D9B97E
MANILA_SHADE = (184, 150,  90)  # ~#B8965A
MANILA_HI = (235, 208, 156)
STAMP_INK = ( 52,  48,  42)     # ~#34302A — cancellation ring ink
POSTAGE_RED = (192,  57,  43)   # ~#C0392B
POSTAGE_HI = (222, 120, 108)
RULE = (150, 122,  78)          # faint address ruling
OUTLINE = ( 44,  38,  32)       # ~#2C2620 — dark, high-value: reads on day sky
KEYLINE = (236, 210, 158)       # warm rim — the NIGHT lifeline


def build(mode="normal") -> pygame.Surface:
    # Mode-agnostic: one static slab sprite for every Pip skin.
    S = 44
    surf = pygame.Surface((S, S), pygame.SRCALPHA)

    # Slab body, kept off the edges so the gameplay rotozoom never clips corners.
    BW, BH = 34, 26
    cx, cy = S // 2, S // 2
    rect = pygame.Rect(cx - BW // 2, cy - BH // 2, BW, BH)
    rad = 4

    # Baked outline frame (drawn first, slightly inflated) — the dark silhouette
    # that survives on the bright (170,220,245) day sky.
    pygame.draw.rect(surf, OUTLINE, rect.inflate(6, 6), border_radius=rad + 2)

    # Manila body: gentle vertical gradient masked to the rounded rect.
    body = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    for y in range(rect.h):
        t = y / max(1, rect.h - 1)
        row = _lerp_color(MANILA_HI, MANILA_SHADE, t)
        body.fill(row + (255,), pygame.Rect(0, y, rect.w, 1))
    mask = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(),
                     border_radius=rad)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(body, rect.topleft)

    # Envelope flap: a shallow downward V from the top corners to a centred dip,
    # the cue that this slab is a closed envelope and not a plain card. Kept
    # faint (shade tone) so it never competes with the cancellation mark.
    apex = (cx, rect.y + 9)
    pygame.draw.lines(surf, MANILA_SHADE, False,
                      [(rect.x + 2, rect.y + 1), apex,
                       (rect.right - 3, rect.y + 1)], 1)

    # Address ruling lines — 2 faint short rules lower-left, so the body never
    # reads as a blank card. Placed clear of the stamp + cancellation marks.
    for i in range(2):
        ly = cy + 3 + i * 5
        pygame.draw.line(surf, RULE, (rect.x + 4, ly), (rect.x + 16, ly), 1)

    # Perforated postage stamp — small red square in the BOTTOM-LEFT corner,
    # opposite the cancellation mark. A dark rim reads as the perforated edge and
    # a tiny highlight keeps it from going muddy at true size.
    st = 8
    sx, sy = rect.x + 3, rect.bottom - st - 3
    srect = pygame.Rect(sx, sy, st, st)
    pygame.draw.rect(surf, OUTLINE, srect.inflate(2, 2), border_radius=1)
    pygame.draw.rect(surf, POSTAGE_RED, srect, border_radius=1)
    pygame.draw.rect(surf, POSTAGE_HI, srect, width=1, border_radius=1)
    pygame.draw.circle(surf, POSTAGE_HI, (sx + 3, sy + 3), 1)

    # CANCELLATION STAMP — the identity. A bold round rubber-stamp mark struck
    # across the TOP-RIGHT: two concentric ink rings with a star at the hub and
    # short radial bars, the universal "postmarked" read. Drawn LAST and biggest
    # so it dominates the sprite. No micro-text — bold legible geometry that holds
    # at 22px and under rotation.
    mx, my = rect.right - 9, rect.y + 10
    r_out, r_in = 9, 5
    # A faint lighter halo first: lifts the manila under the mark so the dark ink
    # rings separate from the body shade and the concentric read survives the
    # downscale instead of smearing into one blob.
    pygame.draw.circle(surf, MANILA_HI, (mx, my), r_out + 1)
    # Two concentric ink rings — the postmark.
    pygame.draw.circle(surf, STAMP_INK, (mx, my), r_out, 2)
    pygame.draw.circle(surf, STAMP_INK, (mx, my), r_in, 2)
    # Short radial cancellation bars bridging the two rings (top/bottom/sides),
    # the "killer bars" that make it read as a strike rather than a target.
    for ang in (90, 270, 0, 180):
        a = math.radians(ang)
        x0 = mx + r_in * math.cos(a)
        y0 = my - r_in * math.sin(a)
        x1 = mx + r_out * math.cos(a)
        y1 = my - r_out * math.sin(a)
        pygame.draw.line(surf, STAMP_INK, (x0, y0), (x1, y1), 2)
    # Solid inked hub dot — a firm centre reads cleaner at true size than a
    # 5-spoke star that turns to mush on the downscale.
    pygame.draw.circle(surf, STAMP_INK, (mx, my), 2)

    # Warm keyline rim INSIDE the outline — a glowing edge on night sky that
    # stays subtle against day. Drawn last so it crowns the silhouette.
    pygame.draw.rect(surf, KEYLINE, rect, width=1, border_radius=rad)

    return pygame.transform.smoothscale(surf, (22, 22))
