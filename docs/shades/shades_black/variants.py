"""Three BLACK SHADES (wayfarer) explorations for the per-style design loop.

Side-profile eyewear on a right-facing macaw. +facing points toward the beak
(front/near lens), -facing toward the ear (temple arm). All geometry scales off
eye_w so the chunky wayfarer silhouette survives both product (eye_w~96) and
in-game (eye_w=22) sizes.
"""
import pygame

# Glossy black wayfarer palette — warm-neutral blacks read richer than pure 0,0,0.
FRAME_BLACK   = (20, 18, 24)
FRAME_EDGE    = (8, 7, 11)        # darkest contour, sells the gloss depth
BROW_SHEEN    = (96, 96, 110)     # specular streak along the top brow
LENS_DARK     = (26, 24, 34)
LENS_DEEP     = (12, 11, 18)      # lower lens, near-black
LENS_TINT     = (44, 52, 74)      # cool sky reflection up top
GLINT_WHITE   = (255, 255, 255)


def _i(eye_w, k, lo=1):
    return max(lo, int(round(eye_w * k)))


# ---------------------------------------------------------------------------
# Variant A — "Classic Wayfarer": bold canted trapezoid, single thick brow,
# one diagonal white glint. The textbook silhouette.
# ---------------------------------------------------------------------------
def draw_shades_A(surf, cx, cy, eye_w, facing=1):
    f = facing
    half = _i(eye_w, 0.55)
    th = _i(eye_w, 0.16)          # frame thickness
    top = cy - _i(eye_w, 0.42)
    bot = cy + _i(eye_w, 0.34)
    # Trapezoid: top edge wider and canted outward (toward beak), bottom narrower.
    nose_x = cx + f * (half + _i(eye_w, 0.10))   # toward beak
    ear_x  = cx - f * half
    outer_top = (ear_x - f * _i(eye_w, 0.04), top)
    inner_top = (nose_x + f * _i(eye_w, 0.06), top)
    inner_bot = (nose_x - f * _i(eye_w, 0.02), bot)
    outer_bot = (ear_x + f * _i(eye_w, 0.06), bot - _i(eye_w, 0.06))
    lens = [outer_top, inner_top, inner_bot, outer_bot]

    # Frame slab (drawn fat, lens punched inside).
    frame_pts = [
        (outer_top[0] - f * th, outer_top[1] - th),
        (inner_top[0] + f * th, inner_top[1] - th),
        (inner_bot[0] + f * th * 0.6, inner_bot[1] + th),
        (outer_bot[0] - f * th * 0.6, outer_bot[1] + th),
    ]
    pygame.draw.polygon(surf, FRAME_BLACK, frame_pts)
    pygame.draw.polygon(surf, FRAME_EDGE, frame_pts, _i(eye_w, 0.04))

    # Lens body: vertical dark gradient.
    pygame.draw.polygon(surf, LENS_DARK, lens)
    lower = [
        ((lens[0][0] + lens[3][0]) // 2, cy),
        ((lens[1][0] + lens[2][0]) // 2, cy),
        lens[2], lens[3],
    ]
    pygame.draw.polygon(surf, LENS_DEEP, lower)
    # Cool sky tint across the upper lens.
    tint = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(tint, (*LENS_TINT, 150),
                        [lens[0], lens[1],
                         ((lens[1][0] + lens[2][0]) // 2, cy),
                         ((lens[0][0] + lens[3][0]) // 2, cy)])
    surf.blit(tint, (0, 0))

    # Brow sheen along the very top edge.
    pygame.draw.line(surf, BROW_SHEEN,
                     (outer_top[0], outer_top[1] - th + 1),
                     (inner_top[0], inner_top[1] - th + 1), _i(eye_w, 0.05))

    # Diagonal white glint streak.
    gx = cx - f * _i(eye_w, 0.18)
    pygame.draw.line(surf, GLINT_WHITE,
                     (gx, top + _i(eye_w, 0.10)),
                     (gx - f * _i(eye_w, 0.14), cy + _i(eye_w, 0.04)),
                     _i(eye_w, 0.05))

    # Temple arm toward the ear, hinge stub at the outer top corner.
    hinge = (outer_top[0] - f * th * 0.5, outer_top[1] + _i(eye_w, 0.06))
    arm_end = (ear_x - f * _i(eye_w, 0.55), top + _i(eye_w, 0.02))
    pygame.draw.line(surf, FRAME_BLACK, hinge, arm_end, _i(eye_w, 0.09))
    pygame.draw.circle(surf, FRAME_EDGE, hinge, _i(eye_w, 0.07))
    pygame.draw.circle(surf, BROW_SHEEN, hinge, _i(eye_w, 0.03))


# ---------------------------------------------------------------------------
# Variant B — "Chunky Block": even fatter rims, squared-off bottom, double
# glint (big diagonal + small spark) and a glossy top highlight band. Reads
# heaviest at 22px.
# ---------------------------------------------------------------------------
def draw_shades_B(surf, cx, cy, eye_w, facing=1):
    f = facing
    half = _i(eye_w, 0.58)
    top = cy - _i(eye_w, 0.46)
    bot = cy + _i(eye_w, 0.36)
    nose_x = cx + f * (half + _i(eye_w, 0.14))
    ear_x  = cx - f * (half - _i(eye_w, 0.02))

    outer_top = (ear_x - f * _i(eye_w, 0.06), top)
    inner_top = (nose_x, top + _i(eye_w, 0.02))
    inner_bot = (nose_x - f * _i(eye_w, 0.10), bot)
    outer_bot = (ear_x + f * _i(eye_w, 0.02), bot)
    lens = [outer_top, inner_top, inner_bot, outer_bot]

    # Fat frame slab.
    th = _i(eye_w, 0.20)
    frame_pts = [
        (outer_top[0] - f * th, top - th),
        (inner_top[0] + f * th, top - th),
        (inner_bot[0] + f * th, bot + th * 0.5),
        (outer_bot[0] - f * th, bot + th * 0.5),
    ]
    pygame.draw.polygon(surf, FRAME_BLACK, frame_pts)
    pygame.draw.polygon(surf, FRAME_EDGE, frame_pts, _i(eye_w, 0.05))

    # Lens.
    pygame.draw.polygon(surf, LENS_DARK, lens)
    mid = cy + _i(eye_w, 0.02)
    lower = [((lens[0][0] + lens[3][0]) // 2, mid),
             ((lens[1][0] + lens[2][0]) // 2, mid), lens[2], lens[3]]
    pygame.draw.polygon(surf, LENS_DEEP, lower)
    tint = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(tint, (*LENS_TINT, 170),
                        [lens[0], lens[1],
                         ((lens[1][0] + lens[2][0]) // 2, mid),
                         ((lens[0][0] + lens[3][0]) // 2, mid)])
    surf.blit(tint, (0, 0))

    # Glossy top highlight band across the whole brow.
    pygame.draw.line(surf, BROW_SHEEN,
                     (outer_top[0] - f * th, top - th + 1),
                     (inner_top[0] + f * th, top - th + 1), _i(eye_w, 0.06))

    # Big diagonal glint + small spark.
    gx = cx - f * _i(eye_w, 0.16)
    pygame.draw.line(surf, GLINT_WHITE,
                     (gx, top + _i(eye_w, 0.12)),
                     (gx - f * _i(eye_w, 0.16), mid),
                     _i(eye_w, 0.06))
    pygame.draw.circle(surf, GLINT_WHITE,
                       (cx + f * _i(eye_w, 0.18), top + _i(eye_w, 0.16)),
                       _i(eye_w, 0.04))

    # Thick temple arm with hinge rivet.
    hinge = (outer_top[0] - f * th * 0.4, top + _i(eye_w, 0.05))
    arm_end = (ear_x - f * _i(eye_w, 0.58), top - _i(eye_w, 0.02))
    pygame.draw.line(surf, FRAME_BLACK, hinge, arm_end, _i(eye_w, 0.12))
    pygame.draw.line(surf, FRAME_EDGE, hinge, arm_end, _i(eye_w, 0.04))
    pygame.draw.circle(surf, FRAME_EDGE, hinge, _i(eye_w, 0.08))
    pygame.draw.circle(surf, BROW_SHEEN, hinge, _i(eye_w, 0.035))


# ---------------------------------------------------------------------------
# Variant C — "Sleek Cant": narrower, more sharply canted trapezoid (steep
# outward top), thinner-but-defined rim, mirror-strip glint. The sportier read.
# ---------------------------------------------------------------------------
def draw_shades_C(surf, cx, cy, eye_w, facing=1):
    f = facing
    half = _i(eye_w, 0.52)
    top = cy - _i(eye_w, 0.40)
    bot = cy + _i(eye_w, 0.30)
    nose_x = cx + f * (half + _i(eye_w, 0.06))
    ear_x  = cx - f * half

    # Steep outward cant: top corner pushed well past the bottom toward the ear.
    outer_top = (ear_x - f * _i(eye_w, 0.16), top)
    inner_top = (nose_x + f * _i(eye_w, 0.04), top + _i(eye_w, 0.04))
    inner_bot = (nose_x - f * _i(eye_w, 0.06), bot)
    outer_bot = (ear_x + f * _i(eye_w, 0.10), bot - _i(eye_w, 0.02))
    lens = [outer_top, inner_top, inner_bot, outer_bot]

    th = _i(eye_w, 0.13)
    frame_pts = [
        (outer_top[0] - f * th, top - th),
        (inner_top[0] + f * th, inner_top[1] - th),
        (inner_bot[0] + f * th * 0.5, bot + th),
        (outer_bot[0] - f * th * 0.5, outer_bot[1] + th),
    ]
    pygame.draw.polygon(surf, FRAME_BLACK, frame_pts)
    pygame.draw.polygon(surf, FRAME_EDGE, frame_pts, _i(eye_w, 0.035))

    pygame.draw.polygon(surf, LENS_DARK, lens)
    lower = [((lens[0][0] + lens[3][0]) // 2, cy),
             ((lens[1][0] + lens[2][0]) // 2, cy), lens[2], lens[3]]
    pygame.draw.polygon(surf, LENS_DEEP, lower)
    tint = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(tint, (*LENS_TINT, 140),
                        [lens[0], lens[1],
                         ((lens[1][0] + lens[2][0]) // 2, cy),
                         ((lens[0][0] + lens[3][0]) // 2, cy)])
    surf.blit(tint, (0, 0))

    # Brow sheen following the steep top cant.
    pygame.draw.line(surf, BROW_SHEEN,
                     (outer_top[0], top - th + 1),
                     (inner_top[0], inner_top[1] - th + 1), _i(eye_w, 0.05))

    # Vertical mirror-strip glint near the front of the lens.
    sx = cx + f * _i(eye_w, 0.02)
    pygame.draw.line(surf, GLINT_WHITE,
                     (sx, top + _i(eye_w, 0.10)),
                     (sx - f * _i(eye_w, 0.06), cy + _i(eye_w, 0.06)),
                     _i(eye_w, 0.06))

    # Swept-back temple arm.
    hinge = (outer_top[0] - f * th * 0.5, top + _i(eye_w, 0.03))
    arm_end = (ear_x - f * _i(eye_w, 0.52), top - _i(eye_w, 0.04))
    pygame.draw.line(surf, FRAME_BLACK, hinge, arm_end, _i(eye_w, 0.08))
    pygame.draw.circle(surf, FRAME_EDGE, hinge, _i(eye_w, 0.06))
    pygame.draw.circle(surf, BROW_SHEEN, hinge, _i(eye_w, 0.025))
