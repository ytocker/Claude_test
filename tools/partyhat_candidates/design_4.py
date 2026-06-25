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
# Against a night sky the body's own value sits BELOW the sky, so a continuous
# lit keyline (brighter than sky_bot ~58,117) is what keeps the silhouette from
# reading as a hole — it is the load-bearing element on the night read.
_MID = (22, 24, 46)          # #16182E midnight cylinder
_MID_HI = (70, 76, 124)      # lit flank of the cylinder (lifted above sky_bot)
_BRIM_SHADE = (42, 45, 82)   # #2A2D52 brim / band base
_BRIM_HI = (74, 80, 130)     # lit rim of the brim
_KEYLINE = (108, 116, 178)   # continuous silhouette keyline — beats night sky
_BRIM_TOP = (128, 136, 196)  # brightest single edge: anchors the eye on the brim
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
    # reads in profile. Thicker than a hat-band so it visibly sits ON the crown.
    # Drawn as a filled ellipse so the underside curves onto the round head crown
    # rather than slicing a straight line.
    brim_half = cyl_w / 2.0 + max(2.5, head_w * 0.18)
    brim_thick = max(2.5, head_w * 0.13)
    brim_rect = pygame.Rect(
        int(cx - brim_half), int(brim_y - brim_thick * 0.5),
        int(brim_half * 2), int(brim_thick * 1.8))
    pygame.draw.ellipse(surf, _BRIM_SHADE, brim_rect)
    # Lit top of the brim — kept as the BRIGHTEST single element so the eye
    # anchors here and the brim reads as the shelf the cylinder stands on.
    hi_rect = pygame.Rect(brim_rect.left + 1, brim_rect.top,
                          brim_rect.width - 2, max(2, int(brim_thick * 1.1)))
    pygame.draw.ellipse(surf, _BRIM_HI, hi_rect)
    # Re-cover the bottom half of the highlight to leave only a top rim of light.
    cover = pygame.Rect(brim_rect.left, int(brim_y - brim_thick * 0.05),
                        brim_rect.width, brim_rect.height)
    pygame.draw.ellipse(surf, _BRIM_SHADE, cover)
    # The single brightest sliver runs along the very top of the brim ellipse.
    top_hi = pygame.Rect(brim_rect.left + 2, brim_rect.top,
                         brim_rect.width - 4, max(2, int(brim_thick * 0.6)))
    pygame.draw.ellipse(surf, _BRIM_TOP, top_hi)
    recut = pygame.Rect(top_hi.left, top_hi.top + max(1, int(brim_thick * 0.34)),
                        top_hi.width, top_hi.height)
    pygame.draw.ellipse(surf, _BRIM_HI, recut)

    # ---- Cylinder body. The top is an ellipse cap; the sides are straight; the
    # bottom meets the brim. Built as a polygon for the sides + an ellipse cap so
    # the slight lean is honest.
    cap_h = max(2.0, cyl_w * 0.22)
    tl_x = cyl_cx - cyl_w / 2.0 + lean
    tr_x = cyl_cx + cyl_w / 2.0 + lean
    bl_x = cyl_cx - cyl_w / 2.0
    br_x = cyl_cx + cyl_w / 2.0

    body_bot = brim_y - brim_thick * 0.2
    body = [
        (tl_x, top_y),
        (tr_x, top_y),
        (br_x, body_bot),
        (bl_x, body_bot),
    ]
    pygame.draw.polygon(surf, _MID, body)

    # Lit flank: a broad wedge down the front edge for internal value structure
    # so the body isn't one flat dark mass against the night sky.
    lit_front = tr_x if f >= 0 else tl_x
    lit_bot = br_x if f >= 0 else bl_x
    rib_w = max(2.5, cyl_w * 0.28)
    flank = [
        (lit_front, top_y),
        (lit_front - f * rib_w, top_y),
        (lit_bot - f * rib_w, body_bot),
        (lit_bot, body_bot),
    ]
    pygame.draw.polygon(surf, _MID_HI, flank)

    # Top cap ellipse (the open mouth of the cylinder seen at a slight angle).
    cap_rect = pygame.Rect(int(tl_x), int(top_y - cap_h * 0.5),
                           int(tr_x - tl_x), int(cap_h))
    pygame.draw.ellipse(surf, _MID_HI, cap_rect)
    inner = cap_rect.inflate(-max(2, int(cyl_w * 0.16)), -max(1, int(cap_h * 0.4)))
    if inner.width > 1 and inner.height > 1:
        pygame.draw.ellipse(surf, _MID, inner)

    # ---- Continuous lit keyline tracing the WHOLE cylinder+brim silhouette.
    # The body's own value sits below a night sky, so this 1px (2px when big)
    # bright outline is what stops the hat reading as a hole in the dark. Drawn
    # last over the body so nothing covers it; the brim's own top edge stays the
    # brightest element, this keeps the rest of the outline legible.
    key_w = max(1, int(head_w * 0.05))
    # Down both straight sides + across the cylinder top + around the cap lip.
    pygame.draw.line(surf, _KEYLINE, (tl_x, top_y), (bl_x, body_bot), key_w)
    pygame.draw.line(surf, _KEYLINE, (tr_x, top_y), (br_x, body_bot), key_w)
    pygame.draw.ellipse(surf, _KEYLINE, cap_rect, key_w)

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

    band_cy = band_rect.centery
    sr = max(1, int(head_w * 0.05))
    if head_w >= 30:
        # Icon size only: the full 3-star scatter (blue sparkle / white glint)
        # plus the red confetti dot — detail the store card can afford.
        for i in range(3):
            t = (i + 0.5) / 3
            sx = band_rect.left + band_rect.width * t
            col = _SPARK if i % 2 == 0 else _GLINT
            pts = _star_points(sx, band_cy, sr * 1.3, sr * 0.5, rot=-math.pi / 2)
            pygame.draw.polygon(surf, col, pts)
        pygame.draw.circle(surf, _CONF,
                           (int(band_rect.left + band_rect.width * 0.80),
                            int(band_rect.top + band_h * 0.3)),
                           max(1, int(head_w * 0.04)))
    elif head_w >= 16:
        # In-gameplay sizes: detail collapses to noise, so keep just TWO marks —
        # one bright glint star (the focal twinkle) and the single red confetti
        # dot as garnish.
        gx = band_rect.left + band_rect.width * 0.42
        pts = _star_points(gx, band_cy, sr * 1.3, sr * 0.5, rot=-math.pi / 2)
        pygame.draw.polygon(surf, _GLINT, pts)
        pygame.draw.circle(surf, _CONF,
                           (int(band_rect.left + band_rect.width * 0.74),
                            int(band_cy)),
                           max(1, int(head_w * 0.05)))

    # ---- Gold star pick standing on top of the cylinder. The star sits LOW and
    # close to the cap so star + cylinder read as one connected silhouette rather
    # than a star floating on a wand. A short, thick stub joins the two.
    pick_top = top_y - cap_h * 0.5
    star_cy = pick_top - head_w * 0.12
    stick_w = max(2, int(head_w * 0.08))
    pygame.draw.line(surf, _GOLD_LO,
                     (cyl_cx + lean, pick_top + 1),
                     (cyl_cx + lean, star_cy + head_w * 0.10), stick_w)

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
