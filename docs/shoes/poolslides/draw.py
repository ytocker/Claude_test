import pygame


# Pool-slide palette: matte black band, crisp white stripes, charcoal footbed.
# Kept deliberately high-contrast so the three-stripe read survives at 15px.
_BAND = (24, 24, 28)
_BAND_HI = (52, 52, 60)
_STRIPE = (244, 244, 248)
_FOOTBED = (40, 40, 48)
_FOOTBED_HI = (66, 66, 78)
_SOLE = (22, 22, 28)


def _lerp(a, b, t):
    return a + (b - a) * t


def _mirror_pts(pts, cx):
    return [(2 * cx - px, py) for (px, py) in pts]


def draw_shoe(surf, x, y, w, h, facing=1):
    """Draw a single side-profile POOL SLIDE sandal into box (x,y,w,h)."""
    cx = x + w * 0.5

    # Footbed/sole: a contoured slab sitting in the bottom third of the box so
    # the open slide profile (band floating above) has room to read. The top
    # surface scoops up under the arch and the toe lip flips up like a molded bed.
    bed_top = y + h * 0.74          # top surface where the foot rests
    bed_bot = y + h                 # ground line
    arch_lift = h * 0.07            # how far the arch pulls up at mid-span
    heel_x = x + w * 0.03
    toe_x = x + w * 0.98

    footbed = [
        (heel_x, bed_top - h * 0.05),                 # heel back-top, slightly raised
        (x + w * 0.22, bed_top + h * 0.01),
        (cx, bed_top - arch_lift),                     # arch scoop (foot dips in here)
        (x + w * 0.72, bed_top + h * 0.00),
        (toe_x, bed_top - h * 0.12),                   # toe lip flips up
        (toe_x, bed_bot - h * 0.10),                   # toe sole curls off the ground
        (x + w * 0.58, bed_bot),
        (x + w * 0.22, bed_bot),
        (heel_x, bed_bot - h * 0.08),                  # heel sole curls off the ground
    ]
    if facing == -1:
        footbed = _mirror_pts(footbed, cx)

    # Darker sole underbody first, then the lighter footbed surface on top so
    # the contoured top edge gets a subtle highlight lip.
    sole = [(px, py + h * 0.04) for (px, py) in footbed]
    pygame.draw.polygon(surf, _SOLE, sole)
    pygame.draw.polygon(surf, _FOOTBED, footbed)

    # Thin highlight skim along the footbed top to sell the molded surface.
    top_edge = [
        (heel_x, bed_top - h * 0.05),
        (x + w * 0.22, bed_top + h * 0.01),
        (cx, bed_top - arch_lift),
        (x + w * 0.72, bed_top + h * 0.00),
        (toe_x, bed_top - h * 0.12),
    ]
    if facing == -1:
        top_edge = _mirror_pts(top_edge, cx)
    pygame.draw.lines(surf, _FOOTBED_HI, False, top_edge, max(1, int(h * 0.05)))

    # The midfoot BAND: a single thick arched strap whose underside floats well
    # above the footbed. The clear daylight gap between them is the OPEN-SLIDE
    # read (foot slides in there); toe and heel stay fully open.
    band_under = y + h * 0.46              # bottom edge of the band / top of gap
    band_peak = y + h * 0.07               # crown of the arched band
    b_back = x + w * 0.28                  # band spans the midfoot only
    b_front = x + w * 0.72

    band = [
        (b_back, band_under),
        (b_back - w * 0.03, band_under - h * 0.16),
        (x + w * 0.35, band_peak + h * 0.05),
        (cx, band_peak),                                # crown of the arch
        (x + w * 0.65, band_peak + h * 0.05),
        (b_front + w * 0.03, band_under - h * 0.16),
        (b_front, band_under),
        # inner underside (defines the open gap); thickness ~ a chunky strap
        (b_front - w * 0.06, band_under - h * 0.05),
        (cx, band_under - h * 0.26),
        (b_back + w * 0.06, band_under - h * 0.05),
    ]
    if facing == -1:
        band = _mirror_pts(band, cx)
    pygame.draw.polygon(surf, _BAND, band)

    # Soft top highlight on the band crown for a little rounded-rubber sheen.
    crown = [
        (x + w * 0.39, band_peak + h * 0.06),
        (cx, band_peak + h * 0.02),
        (x + w * 0.61, band_peak + h * 0.06),
    ]
    if facing == -1:
        crown = _mirror_pts(crown, cx)
    pygame.draw.lines(surf, _BAND_HI, False, crown, max(1, int(h * 0.05)))

    # HERO CUE: three bold diagonal stripes across the band. Each is a slanted
    # parallelogram from the band's lower-front edge up to its upper-back edge,
    # so the trio keeps the same diagonal rhythm at any size.
    sw = max(1.0, w * 0.05)                # stripe half-width, scales with box
    gap = w * 0.13                         # spacing between stripe centers
    base = cx - gap                        # center the trio on the arch crown
    dx = w * 0.09                          # horizontal slant run
    for i in range(3):
        c = base + i * gap
        low = (c + dx * 0.5, band_under - h * 0.04)
        high = (c - dx * 0.5, band_peak + h * 0.12)
        quad = [
            (low[0] - sw, low[1]),
            (low[0] + sw, low[1]),
            (high[0] + sw, high[1]),
            (high[0] - sw, high[1]),
        ]
        if facing == -1:
            quad = _mirror_pts(quad, cx)
        pygame.draw.polygon(surf, _STRIPE, quad)

    # Subtle 1px darker edge under the band to seat it against the open gap.
    seam = [(b_back + w * 0.06, band_under - h * 0.05),
            (cx, band_under - h * 0.24),
            (b_front - w * 0.06, band_under - h * 0.05)]
    if facing == -1:
        seam = _mirror_pts(seam, cx)
    pygame.draw.lines(surf, _SOLE, False, seam, 1)
