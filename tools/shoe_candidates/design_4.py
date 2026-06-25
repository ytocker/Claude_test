import math

import pygame


# WING BOOTS — legendary Hermes greave boot. The whole point is that the
# silhouette BREAKS the unit box outward: feathered ankle wings flare up
# (t < 0) and back past the heel (t < 0 in x after the facing flip), so even
# at 40px the outline reads "winged relic" and not "sneaker". The gold shell
# is a metal greave (light/dark pair gives the curved sheen), wrapped by a
# laurel band with a gemmed clasp. Wings are drawn as a few BOLD feather
# wedges (not fine barbs) so the shape holds when the foot shrinks; sparkle
# motes are kept tiny so they never compete with the wing read.

_GOLD    = (244, 215, 122)   # body gold
_GOLD_L  = (251, 240, 196)   # lit gold (sheen)
_GOLD_D  = (201, 154,  58)   # deep gold (shadow / metal break)
_WHITE   = (255, 255, 255)   # feather white
_WHITE_D = (214, 222, 236)   # cool feather shadow
_LAUREL  = ( 92, 150,  78)   # olive laurel
_LAUREL_D= ( 58, 104,  52)
_GEM     = (111, 227, 255)   # cyan clasp gem / sparkle
_GEM_D   = ( 36, 138, 176)


def draw_shoe(surf, x, y, w, h, facing=1):
    """Draw a side-profile WING BOOTS greave into box (x,y,w,h).

    Wings deliberately exceed the box (t<0 above, t<0 behind the heel) so the
    winged silhouette is unmistakable — callers must leave head/side room.
    """
    def px(t):
        return x + (t * w if facing == 1 else (1.0 - t) * w)

    def py(t):
        return y + t * h

    def poly(color, pts):
        pygame.draw.polygon(surf, color, [(px(a), py(b)) for a, b in pts])

    def line(color, a, b, width):
        pygame.draw.line(surf, color, (px(a[0]), py(a[1])),
                         (px(b[0]), py(b[1])), max(1, int(round(width))))

    def dot(color, t, s):
        pygame.draw.circle(surf, color, (int(px(t[0])), int(py(t[1]))),
                           max(1, int(round(s))))

    sole_top = 0.86

    # ── ANKLE WINGS (drawn FIRST so the gold shell overlaps their roots) ───────
    # Three stacked feather wedges sweeping UP-and-BACK from the ankle, past the
    # box behind the heel (negative x after flip) and above the top (t<0). Bold
    # filled wedges read as a wing at 40px; a white core + cool shadow give the
    # white-gold two-tone the spec calls for.
    wing_root = (0.18, 0.30)
    # Lower (longest, sweeps furthest back).
    poly(_WHITE_D, [
        wing_root, (-0.30, 0.04), (-0.42, 0.16),
        (-0.10, 0.22), (0.10, 0.30),
    ])
    poly(_WHITE, [
        wing_root, (-0.30, 0.04), (-0.34, 0.13), (-0.04, 0.18), (0.10, 0.27),
    ])
    # Middle feather.
    poly(_WHITE_D, [
        (0.16, 0.18), (-0.26, -0.16), (-0.40, -0.06),
        (-0.10, 0.06), (0.10, 0.18),
    ])
    poly(_WHITE, [
        (0.16, 0.18), (-0.26, -0.16), (-0.32, -0.07), (-0.04, 0.02), (0.10, 0.15),
    ])
    # Top feather (shortest, points furthest UP past the box top).
    poly(_WHITE_D, [
        (0.18, 0.10), (-0.14, -0.34), (-0.30, -0.28),
        (-0.06, -0.10), (0.12, 0.08),
    ])
    poly(_WHITE, [
        (0.18, 0.10), (-0.14, -0.34), (-0.22, -0.30), (-0.02, -0.12), (0.12, 0.05),
    ])
    # Gold leading-edge spar tying the feathers to the boot — the metallic root
    # so the wings read as forged onto the greave, not loose plumage.
    line(_GOLD_D, (-0.30, 0.02), (0.18, 0.22), max(1, w * 0.030))
    line(_GOLD_L, (-0.30, 0.00), (0.16, 0.18), max(1, w * 0.018))

    # ── GREAVE OUTSOLE (winged sandal sole, dark-gold tread) ───────────────────
    poly(_GOLD_D, [
        (0.06, 1.00), (0.94, 1.00), (0.98, 0.93),
        (0.90, 0.90), (0.10, 0.90), (0.06, 0.94),
    ])
    poly(_GOLD, [
        (0.08, 0.92), (0.10, sole_top), (0.90, sole_top),
        (0.95, 0.91), (0.95, 0.94), (0.10, 0.945),
    ])
    poly(_GOLD_L, [
        (0.10, sole_top), (0.90, sole_top), (0.88, 0.895), (0.12, 0.895),
    ])

    # ── GREAVE BOOT SHELL (curved gold metal, rises into a cuff) ───────────────
    # Toe-to-cuff metal body. The light/dark split runs vertically so the shell
    # reads as a rounded forged plate catching light along its front ridge.
    shell = [
        (0.10, sole_top), (0.12, 0.40), (0.22, 0.28),
        (0.40, 0.24), (0.62, 0.30), (0.84, 0.46),
        (0.93, 0.66), (0.93, sole_top),
    ]
    poly(_GOLD, shell)
    # Lit front ridge (toe side catches light).
    poly(_GOLD_L, [
        (0.62, 0.30), (0.84, 0.46), (0.93, 0.66), (0.93, 0.74),
        (0.80, 0.54), (0.60, 0.40),
    ])
    # Shadowed heel side of the shell.
    poly(_GOLD_D, [
        (0.10, sole_top), (0.12, 0.40), (0.22, 0.28), (0.26, 0.34),
        (0.18, 0.44), (0.17, sole_top),
    ])
    # Vertical greave seam (forged plate split) — survives shrink as one stroke.
    line(_GOLD_D, (0.50, 0.30), (0.50, sole_top), max(1, w * 0.018))

    # ── ANKLE CUFF + GEMMED CLASP ──────────────────────────────────────────────
    # The cuff rounds the top of the boot where the wings spring from.
    poly(_GOLD, [
        (0.14, 0.36), (0.20, 0.24), (0.40, 0.21),
        (0.52, 0.26), (0.50, 0.36), (0.30, 0.40),
    ])
    poly(_GOLD_L, [
        (0.20, 0.24), (0.40, 0.21), (0.40, 0.26), (0.22, 0.29),
    ])
    # Gemmed clasp at the cuff front — the one cool accent on all that gold.
    clasp = (0.45, 0.31)
    dot(_GOLD_D, clasp, w * 0.055)
    dot(_GEM_D, clasp, w * 0.040)
    dot(_GEM, (clasp[0] - 0.010, clasp[1] - 0.010), w * 0.022)

    # ── LAUREL ANKLE WRAP (olive band over the cuff base) ──────────────────────
    # A short laurel sprig wraps the ankle — the mythic tell. Kept as a couple
    # of bold leaf wedges so it survives downscale rather than dissolving.
    poly(_LAUREL_D, [
        (0.18, 0.44), (0.30, 0.40), (0.50, 0.42), (0.50, 0.50),
        (0.30, 0.49), (0.18, 0.52),
    ])
    poly(_LAUREL, [
        (0.18, 0.44), (0.30, 0.40), (0.50, 0.42), (0.48, 0.46), (0.30, 0.45),
        (0.20, 0.48),
    ])
    for lt in (0.24, 0.34, 0.44):
        poly(_LAUREL, [
            (lt, 0.40), (lt + 0.04, 0.34), (lt + 0.07, 0.40),
        ])
        poly(_LAUREL_D, [
            (lt + 0.07, 0.40), (lt + 0.04, 0.34), (lt + 0.045, 0.40),
        ])

    # ── SPARKLE MOTES (tiny — never compete with the wing read) ────────────────
    for mt, ms in (((-0.20, -0.18), w * 0.020),
                   ((0.02, -0.06), w * 0.014),
                   ((0.70, 0.78), w * 0.016)):
        dot(_GEM, mt, ms)
        dot(_WHITE, (mt[0], mt[1]), max(1, ms * 0.45))
