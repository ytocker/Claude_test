"""DESIGN 4 — NYE TOP HAT (SCRATCH candidate for the PARTY HAT redesign).

A glittery New-Year's-Eve mini top hat: a short midnight cylinder with a
star-spangled band and a gold star pick standing on top. Dressier and sparkly
than the cone party hat — the "countdown" hat. Brim stays readable in profile.

Same contract as game/hat_partyhat.draw_hat: side-profile, sized to a head of
width head_w, centred at cx, brim line at base_y.
"""
import math

import pygame

from tools.partyhat_candidates._template import make_build, make_icon


# Midnight cylinder with a star-band; gold star pick crowns it. Flat tones keep
# the read crisp at head_w~18 where gradients muddy; one lit rib fakes volume.
_MID = (22, 24, 46)          # #16182E midnight cylinder
_MID_HI = (52, 56, 96)       # lit flank of the cylinder
_BRIM_SHADE = (42, 45, 82)   # #2A2D52 brim / band base
_BRIM_HI = (74, 80, 130)     # lit rim of the brim
_GOLD = (255, 210, 63)       # #FFD23F gold star
_GOLD_LO = (206, 160, 36)    # shaded star points
_GOLD_HI = (255, 240, 170)   # star glint
_SPARK = (155, 178, 255)     # #9BB2FF blue sparkle
_GLINT = (255, 255, 255)     # #FFFFFF glints
_CONF = (232, 69, 74)        # #E8454A confetti accent


def _star_points(cx, cy, r_out, r_in, n=5, rot=-math.pi / 2):
    pts = []
    for i in range(n * 2):
        ang = rot + i * math.pi / n
        rad = r_out if i % 2 == 0 else r_in
        pts.append((cx + math.cos(ang) * rad, cy + math.sin(ang) * rad))
    return pts


def draw_hat(surf, cx, base_y, head_w, facing=1):
    """Draw a side-profile NYE TOP HAT sized for a head of width head_w, centered at cx, brim line at base_y."""
    f = 1 if facing >= 0 else -1
    r = head_w * 0.5

    # A NYE mini top hat is SHORT and dressy: the cylinder rises ~0.78x head_w,
    # well under a true topper, so it reads as a perched party hat not a costume
    # topper. A slight forward lean sells it as worn.
    cyl_w = head_w * 0.62
    cyl_h = head_w * 0.78
    lean = f * head_w * 0.05  # top edge nudged toward the beak

    cyl_cx = cx
    brim_y = base_y
    top_y = base_y - cyl_h

    # ---- Brim: a flat slightly-curved slab, wider than the cylinder so it
    # reads in profile. Drawn as a filled ellipse so the underside curves onto
    # the round head crown rather than slicing a straight line.
    brim_half = cyl_w / 2.0 + max(2.5, head_w * 0.18)
    brim_thick = max(2.0, head_w * 0.10)
    brim_rect = pygame.Rect(
        int(cx - brim_half), int(brim_y - brim_thick * 0.5),
        int(brim_half * 2), int(brim_thick * 1.8))
    pygame.draw.ellipse(surf, _BRIM_SHADE, brim_rect)
    # Lit top sliver of the brim so it separates from the dark cylinder.
    hi_rect = pygame.Rect(brim_rect.left + 1, brim_rect.top,
                          brim_rect.width - 2, max(2, int(brim_thick)))
    pygame.draw.ellipse(surf, _BRIM_HI, hi_rect)
    # Re-cover the bottom half of the highlight to leave only a top rim of light.
    cover = pygame.Rect(brim_rect.left, int(brim_y - brim_thick * 0.1),
                        brim_rect.width, brim_rect.height)
    pygame.draw.ellipse(surf, _BRIM_SHADE, cover)

    # ---- Cylinder body. The top is an ellipse cap; the sides are straight; the
    # bottom meets the brim. Built as a polygon for the sides + an ellipse cap so
    # the slight lean is honest.
    cap_h = max(2.0, cyl_w * 0.22)
    tl_x = cyl_cx - cyl_w / 2.0 + lean
    tr_x = cyl_cx + cyl_w / 2.0 + lean
    bl_x = cyl_cx - cyl_w / 2.0
    br_x = cyl_cx + cyl_w / 2.0

    body = [
        (tl_x, top_y),
        (tr_x, top_y),
        (br_x, brim_y - brim_thick * 0.2),
        (bl_x, brim_y - brim_thick * 0.2),
    ]
    pygame.draw.polygon(surf, _MID, body)

    # Lit flank: a thin wedge down the front edge for cheap roundness.
    lit_front = tr_x if f >= 0 else tl_x
    lit_bot = br_x if f >= 0 else bl_x
    rib_w = max(2.0, cyl_w * 0.16)
    flank = [
        (lit_front, top_y),
        (lit_front - f * rib_w, top_y),
        (lit_bot - f * rib_w, brim_y - brim_thick * 0.2),
        (lit_bot, brim_y - brim_thick * 0.2),
    ]
    pygame.draw.polygon(surf, _MID_HI, flank)

    # Top cap ellipse (the open mouth of the cylinder seen at a slight angle).
    cap_rect = pygame.Rect(int(tl_x), int(top_y - cap_h * 0.5),
                           int(tr_x - tl_x), int(cap_h))
    pygame.draw.ellipse(surf, _MID_HI, cap_rect)
    inner = cap_rect.inflate(-max(2, int(cyl_w * 0.16)), -max(1, int(cap_h * 0.4)))
    if inner.width > 1 and inner.height > 1:
        pygame.draw.ellipse(surf, _MID, inner)

    # ---- Star-spangled band: a brim-shade ribbon hugging the base of the
    # cylinder, with tiny sparkle stars/dots. Gated so the smallest size keeps a
    # clean band instead of a muddy speckle.
    band_h = max(2.5, cyl_h * 0.26)
    band_top = brim_y - brim_thick * 0.2 - band_h
    band_rect = pygame.Rect(int(bl_x), int(band_top),
                            int(br_x - bl_x), int(band_h))
    pygame.draw.rect(surf, _BRIM_SHADE, band_rect)
    # Band lit edge along the front so it doesn't merge with the cylinder.
    pygame.draw.line(surf, _BRIM_HI,
                     (band_rect.left + 1, band_rect.top),
                     (band_rect.right - 1, band_rect.top), max(1, int(band_h * 0.18)))

    if head_w >= 18:
        # A scatter of sparkle stars across the band — alternating blue sparkle
        # and white glint, with one red confetti dot for the party accent.
        band_cy = band_rect.centery
        n = 3 if head_w >= 24 else 2
        for i in range(n):
            t = (i + 0.5) / n
            sx = band_rect.left + band_rect.width * t
            col = _SPARK if i % 2 == 0 else _GLINT
            sr = max(1, int(head_w * 0.045))
            if head_w >= 26:
                pts = _star_points(sx, band_cy, sr * 1.4, sr * 0.55, rot=-math.pi / 2)
                pygame.draw.polygon(surf, col, pts)
            else:
                pygame.draw.circle(surf, col, (int(sx), int(band_cy)), sr)
        # One red confetti dot riding the upper band.
        pygame.draw.circle(surf, _CONF,
                           (int(band_rect.left + band_rect.width * 0.78),
                            int(band_rect.top + band_h * 0.3)),
                           max(1, int(head_w * 0.04)))

    # ---- Gold star pick standing on top of the cylinder. A slim stick lifts the
    # star above the cap so it reads as a "topper" pick, the NYE centrepiece.
    pick_top = top_y - cap_h * 0.5
    star_cy = pick_top - head_w * 0.30
    stick_w = max(1, int(head_w * 0.04))
    pygame.draw.line(surf, _GOLD_LO,
                     (cyl_cx + lean, pick_top),
                     (cyl_cx + lean, star_cy + head_w * 0.05), stick_w + 1)

    star_r = head_w * 0.26
    sx = cyl_cx + lean
    # Shaded backing star (offset down/back) then the bright face for a 3D pop.
    back = _star_points(sx - f * star_r * 0.06, star_cy + star_r * 0.06,
                        star_r, star_r * 0.42, rot=-math.pi / 2)
    pygame.draw.polygon(surf, _GOLD_LO, back)
    face = _star_points(sx, star_cy, star_r, star_r * 0.42, rot=-math.pi / 2)
    pygame.draw.polygon(surf, _GOLD, face)
    # Centre glint on the star.
    if head_w >= 16:
        pygame.draw.circle(surf, _GOLD_HI,
                           (int(sx - f * star_r * 0.12), int(star_cy - star_r * 0.12)),
                           max(1, int(star_r * 0.22)))

    # A faint twinkle dot near the star tip — the "sparkle" of the countdown.
    if head_w >= 22:
        tw_x = sx + f * star_r * 0.9
        tw_y = star_cy - star_r * 0.8
        pygame.draw.circle(surf, _GLINT, (int(tw_x), int(tw_y)),
                           max(1, int(head_w * 0.03)))


# Seat tuned so the brim rests on the head crown and the cylinder + star rise
# above without clipping the canvas top (crown anchor y~31 on a 64x100 canvas).
seat = {"hw": 27, "dx": -1, "dy": 9}

build = make_build(draw_hat, seat=seat)
icon = make_icon(draw_hat)
