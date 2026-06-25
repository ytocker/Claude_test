import pygame


# MEGA DAD — rare chunky "dad shoe" runner. The whole read is BULK: a bulbous
# triple-stacked foam midsole eats the bottom ~45% of the box (versus ~22% on a
# normal sneaker), so even at 16px the eye sees a fat wedge of sole carrying a
# squat colour-blocked upper. No glow, no fantasy — believable footwear that is
# simply enormous. Three stacked foam tiers separated by carved grooves give the
# "stack height" cue; a grey body with a teal toe overlay + orange mudguard reads
# as the colour-block; a reflective lace cage and a fat heel pull-loop are the
# two small cues clamped to >=1px so they survive the worn-foot shrink.
#
# All geometry is proportional in facing=1 (toe right) space; coordinates mirror
# for facing=-1 so one body of shapes serves both directions. Unlike the slim
# homages the upper is deliberately short and round-shouldered so the sole — not
# the upper — dominates the silhouette.

_OFFW   = (232, 230, 224)   # off-white foam (top midsole tier + highlights)
_OFFW_D = (205, 203, 196)   # foam shade between tiers
_GREY   = (185, 192, 196)   # cool grey upper body (mesh/suede)
_GREY_D = (150, 158, 163)   # upper shadow / panel seams
_TEAL   = ( 42, 166, 160)   # teal toe overlay pop
_TEAL_D = ( 28, 122, 118)   # teal shade
_ORANGE = (240, 121,  46)   # orange mudguard pop
_ORANGE_D = (196,  92,  30) # orange shade
_DARK   = ( 43,  46,  51)   # dark seams / outsole / pull-loop
_DARK_HI = (96, 102, 110)   # reflective lace-cage / metallic sheen


def draw_shoe(surf, x, y, w, h, facing=1):
    """Draw a single side-profile MEGA DAD sneaker into box (x,y,w,h)."""
    def px(t):
        return x + (t * w if facing == 1 else (1.0 - t) * w)

    def py(t):
        return y + t * h

    def poly(color, pts):
        pygame.draw.polygon(surf, color, [(px(a), py(b)) for a, b in pts])

    def line(color, a, b, width):
        pygame.draw.line(surf, color, (px(a[0]), py(a[1])),
                         (px(b[0]), py(b[1])), max(1, int(round(width))))

    # The foam stack owns the bottom ~45%; the upper is squeezed into the top
    # half so the silhouette reads sole-heavy. This split IS the dad-shoe cue.
    stack_top = 0.56

    # ── dark outsole on the ground line ────────────────────────────────────────
    poly(_DARK, [
        (0.05, 0.985), (0.13, 1.00), (0.90, 1.00),
        (0.98, 0.94), (0.95, 0.90), (0.08, 0.90), (0.03, 0.95),
    ])

    # ── bulbous triple-stacked foam midsole (the hero mass) ─────────────────────
    # One fat outer foam wall, rounded out at toe and heel so it bulges past the
    # upper. Drawn as a single big block first; carved grooves + a shade band
    # then split it into three readable tiers.
    poly(_OFFW, [
        (0.06, 0.93), (0.02, 0.82), (0.05, 0.70),
        (0.14, stack_top), (0.86, stack_top), (0.95, 0.68),
        (0.99, 0.80), (0.95, 0.92),
    ])
    # Lower-tier shade so the bottom of the stack reads as a separate slab.
    poly(_OFFW_D, [
        (0.045, 0.86), (0.95, 0.86), (0.965, 0.90),
        (0.92, 0.93), (0.085, 0.93), (0.035, 0.88),
    ])

    # Carved grooves between the three foam tiers — gentle scallops, not straight
    # lines, so the foam reads as stacked pillows. Clamped so they survive 16px.
    groove_w = max(1, int(round(h * 0.045)))
    for gy in (0.71, 0.82):
        pygame.draw.lines(
            surf, _OFFW_D, False,
            [(px(t), py(gy + 0.012 * (1 if i % 2 else -1)))
             for i, t in enumerate((0.07, 0.28, 0.50, 0.72, 0.93))],
            groove_w,
        )

    # ── upper: cool-grey colour-blocked body (squat, round-shouldered) ──────────
    # Sits low and stubby on the foam. The collar opening notch at the top sells
    # a worn shoe rather than a slab.
    poly(_GREY, [
        (0.12, stack_top), (0.13, 0.34), (0.22, 0.22),
        (0.40, 0.18), (0.58, 0.20), (0.66, 0.30),
        (0.74, 0.42), (0.88, 0.50), (0.88, stack_top),
    ])
    # Heel-counter shadow gives the rear upper depth.
    poly(_GREY_D, [
        (0.12, stack_top), (0.125, 0.40), (0.20, 0.26),
        (0.27, 0.30), (0.22, 0.44), (0.215, stack_top),
    ])

    # ── teal toe overlay (front colour pop) ─────────────────────────────────────
    poly(_TEAL, [
        (0.74, 0.42), (0.88, 0.50), (0.88, stack_top),
        (0.66, stack_top), (0.66, 0.46),
    ])
    poly(_TEAL_D, [
        (0.84, 0.52), (0.88, 0.50), (0.88, stack_top),
        (0.84, stack_top),
    ])

    # ── orange mudguard wrapping the foot/foam join (mid colour pop) ────────────
    # A thick band riding along the top of the foam stack — the loudest stripe.
    poly(_ORANGE, [
        (0.10, stack_top), (0.88, stack_top), (0.88, 0.625),
        (0.66, 0.65), (0.30, 0.64), (0.12, 0.655),
    ])
    poly(_ORANGE_D, [
        (0.10, stack_top + 0.02), (0.88, stack_top + 0.02),
        (0.88, 0.625), (0.10, 0.635),
    ])

    # ── reflective lace cage across the throat ──────────────────────────────────
    # External webbing straps (the dad-shoe "cage") rather than thin laces: short
    # bright bars stepping up the instep with a dark seam under each so the cage
    # reads metallic/reflective even when it collapses to a few pixels.
    cage_w = max(1, int(round(h * 0.085)))
    for tx0, ty0, tx1, ty1 in (
        (0.36, 0.30, 0.50, 0.28),
        (0.34, 0.40, 0.52, 0.37),
        (0.33, 0.50, 0.54, 0.46),
    ):
        line(_DARK, (tx0, ty0 + 0.02), (tx1, ty1 + 0.02), cage_w)
        line(_DARK_HI, (tx0, ty0), (tx1, ty1), cage_w)

    # Dark throat/tongue gap behind the cage so the laces read as crossing a hole.
    poly(_DARK, [
        (0.34, 0.28), (0.56, 0.24), (0.60, 0.30),
        (0.40, 0.36),
    ])

    # ── fat heel pull-loop at the back (signature dad-shoe tab) ─────────────────
    # A chunky rounded loop standing proud of the heel — its own little arch with
    # a dark core so it reads as a graspable loop, not a flat flap.
    poly(_DARK_HI, [
        (0.10, 0.30), (0.07, 0.16), (0.13, 0.10),
        (0.24, 0.10), (0.29, 0.18), (0.26, 0.30),
        (0.21, 0.24), (0.16, 0.22), (0.13, 0.26),
    ])
    poly(_DARK, [
        (0.135, 0.245), (0.13, 0.165), (0.165, 0.135),
        (0.225, 0.135), (0.255, 0.18), (0.235, 0.235),
        (0.205, 0.205), (0.16, 0.20),
    ])
