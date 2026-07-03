import pygame


# Sporty colorway: a white terry band reads "athletic", neon-green bill is the
# loud sun-visor signal. Kept high-contrast so the silhouette pops on a parrot
# at tiny sizes where fine detail vanishes.
_BAND = (244, 247, 240)
_BAND_SHADE = (206, 214, 200)
_STITCH = (120, 132, 116)
_BILL = (78, 214, 96)
_BILL_TOP = (138, 240, 150)
_BILL_EDGE = (44, 158, 64)


def draw_hat(surf, cx, base_y, head_w, facing=1):
    """Draw a side-profile sun VISOR sized for a head of width head_w, centered at cx, band line at base_y."""
    # All geometry is proportional so the read survives head_w 18..80. A visor
    # has NO crown: just a curved bill aimed right plus a low band hugging the
    # front of the head, leaving the top open.
    r = head_w * 0.5
    f = 1 if facing >= 0 else -1

    # Band wraps the FRONT/side arc of the head only (low, so the crown shows
    # through). Anchored just below crown-top and following the head circle.
    band_h = max(2, head_w * 0.16)
    # Front edge of the head on the facing side; band reaches from the brow
    # forward to where the bill attaches.
    front_x = cx + f * r
    band_top = base_y + head_w * 0.18

    # The band is an arc-shaped strip; approximate with a filled polygon that
    # follows the head's curve from the upper-back of the front quadrant down
    # to the brow, then back up offset by band_h.
    def head_pt(ang):
        # ang measured from straight-up, sweeping toward facing side.
        return (cx + f * r * pygame.math.Vector2(0, -1).rotate(f * -ang).x,
                base_y + r + r * pygame.math.Vector2(0, -1).rotate(f * -ang).y)

    # Simpler explicit band: sample the front head arc and build an inner/outer ring.
    outer = []
    inner = []
    # Sweep from ~25deg (near top, where band starts) down to ~115deg (below brow).
    steps = 10
    a0, a1 = 22, 118
    for i in range(steps + 1):
        ang = a0 + (a1 - a0) * i / steps
        v = pygame.math.Vector2(0, -1).rotate(ang)
        ox = cx + f * v.x * r
        oy = base_y + r + v.y * r
        ix = cx + f * v.x * (r - band_h)
        iy = base_y + r + v.y * (r - band_h)
        outer.append((ox, oy))
        inner.append((ix, iy))
    band_poly = outer + inner[::-1]
    pygame.draw.polygon(surf, _BAND, band_poly)
    # Soft inner shade along the bottom of the band for a little roundness.
    pygame.draw.lines(surf, _BAND_SHADE, False, inner, max(1, int(head_w * 0.03)))
    # Terry stitch line: a dashed seam running along the middle of the band.
    mid = []
    for i in range(steps + 1):
        ang = a0 + (a1 - a0) * i / steps
        v = pygame.math.Vector2(0, -1).rotate(ang)
        mid.append((cx + f * v.x * (r - band_h * 0.5),
                    base_y + r + v.y * (r - band_h * 0.5)))
    for i in range(0, steps, 2):
        pygame.draw.line(surf, _STITCH, mid[i], mid[i + 1], max(1, int(head_w * 0.02)))

    # The brow point where band meets bill (lowest, front-most band sample).
    brow = outer[-1]
    # Bill attaches at the band's front face, around eye/brow level on the head
    # circle rather than at the very bottom sample, so the peak springs forward
    # from the front of the head instead of hanging off the chin.
    av = pygame.math.Vector2(0, -1).rotate(96)
    attach_x = cx + f * av.x * r
    attach_y = base_y + r + av.y * r

    # Forward-projecting BILL. A sun visor's peak juts roughly HORIZONTAL out
    # in front of the brow (only a slight downward droop), with a softly rounded
    # front edge -- not a steep raked wedge. Carry the attach height out to the
    # tip so the plane reads flat/forward.
    bill_len = head_w * 1.00
    bill_thick = max(2, head_w * 0.15)
    bill_droop = head_w * 0.06  # gentle downward tilt at the far tip only

    root_y = attach_y  # bill leaves the band at its front face
    tip_x = attach_x + f * bill_len
    tip_y = root_y + bill_droop

    # Top surface: nearly level from band-front out to the rounded tip, dipping
    # only slightly. A mid control point arcs it for a soft convex peak.
    top_curve = [
        (attach_x - f * r * 0.10, root_y),
        (attach_x + f * bill_len * 0.50, root_y - head_w * 0.02),
        (attach_x + f * bill_len * 0.85, root_y - head_w * 0.005),
        (tip_x, tip_y),
    ]
    # Rounded front edge: drop straight-ish a touch at the tip, then return
    # along the underside back to the attach point, kept parallel-ish to the top
    # so the peak has even thickness rather than tapering into a wedge.
    bottom_curve = [
        (tip_x, tip_y + bill_thick * 0.55),
        (attach_x + f * bill_len * 0.85, root_y + bill_thick),
        (attach_x + f * bill_len * 0.45, root_y + bill_thick * 1.05),
        (attach_x, root_y + bill_thick * 0.5),
    ]
    bill_poly = top_curve + bottom_curve
    pygame.draw.polygon(surf, _BILL, bill_poly)
    # Lighter sheen along the bill's flat top edge sells the forward plane.
    pygame.draw.lines(surf, _BILL_TOP, False, top_curve, max(1, int(head_w * 0.045)))
    # Crisp darker leading edge under the bill.
    pygame.draw.lines(surf, _BILL_EDGE, False, bottom_curve, max(1, int(head_w * 0.03)))
