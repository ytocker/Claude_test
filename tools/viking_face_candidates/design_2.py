"""Viking FACE + AXE redesign — design_2 "BERSERKER".

A raging brute read: the moustache is a heavy bushy WALRUS that droops at the
corners and merges straight down into a BROAD SQUARE full beard — one big
shaggy mass (no braids), shaped with a few strand lines so it reads as hair and
not a blob. The eye is a single wide stare under a hard scowling brow, and the
axe is a HEAVY DOUBLE-BIT (twin crescent blades flanking one haft) hoisted with
the head HIGH above the shoulder in a two-fisted grip across the chest — the
most aggressive silhouette of the set.

Pose for the held axe is modelled on game/knight_skin._sword: grip LOW at the
belly with knuckle/claw pixels, head UP breaking the silhouette. Scratch
exploration only — nothing here registers in store_skins.BUILDERS.
"""
import pygame

from tools.viking_face_candidates import _shared as S


# Composite anchors (the un-rotated 4x base canvas store_skins draws into).
HX, HY = 47, 41
CROWN_Y = 31


def _paint_face(surf, wing_angle, P):
    beard, beard_hi = P["beard"], P["beard_hi"]
    bone = P["bone"]

    # The horned helm caps the head down to ~y45; below it the bird's CHEEK/BEAK
    # pokes out. The face reads as a clean vertical stack on that exposed front:
    # EYE on a light cheek patch (top) -> bushy WALRUS MOUSTACHE band (middle) ->
    # BROAD SQUARE BEARD onto the chest (bottom). Stacking them — rather than
    # piling dark hair over a dark eye — is what makes all three legible at 40px.
    FX, FY = 51, 50

    # ── BROAD SQUARE BEARD (bottom of the stack) ─────────────────────────────
    # One big shaggy block onto the chest, squared at the bottom so the brute
    # silhouette stays heavy. Its TOP edge stops below the moustache so the eye
    # and 'stache aren't swallowed.
    by0 = FY + 4
    beard_block = [
        (FX - 12, by0),      # left jaw
        (FX - 14, by0 + 8),
        (FX - 12, by0 + 14), # squared lower-left
        (FX - 5, by0 + 16),
        (FX + 2, by0 + 15),
        (FX + 8, by0 + 11),  # squared lower-right
        (FX + 9, by0 + 4),
        (FX + 6, by0 - 1),   # right jaw, under the beak
        (FX - 3, by0),
    ]
    S._poly(surf, beard, beard_block)
    for tx, ty in ((FX - 11, by0 + 14), (FX - 4, by0 + 16), (FX + 3, by0 + 15), (FX + 7, by0 + 10)):
        S._poly(surf, beard, [(tx - 2, ty - 2), (tx + 2, ty - 2), (tx, ty + 2)])
    # Volume highlight + strand lines so the mass reads as combed hair.
    S._poly(surf, beard_hi, [
        (FX - 12, by0 + 1), (FX - 8, by0 + 1), (FX - 9, by0 + 12), (FX - 13, by0 + 10),
    ])
    for sx in (FX - 9, FX - 5, FX - 1, FX + 3):
        pygame.draw.line(surf, beard_hi, (sx, by0 + 2), (sx + 1, by0 + 13), 1)
    for sx in (FX - 7, FX - 3, FX + 1, FX + 5):
        pygame.draw.line(surf, P["eye_pupil"], (sx, by0 + 3), (sx, by0 + 12), 1)

    # ── LIGHT CHEEK PATCH (so the eye + 'stache have contrast) ───────────────
    # A bone-pale skin patch under the helm rim where the eye sits, so the face
    # holds its value gap against the dark beard/helm even at 40px.
    S._poly(surf, P["bone"], [
        (FX - 8, FY - 7), (FX + 8, FY - 6), (FX + 9, FY + 1), (FX - 7, FY + 2),
    ])

    # ── SCOWLING BROW ────────────────────────────────────────────────────────
    # A hard dark wedge angled down toward the beak — the rage line over the eye.
    S._poly(surf, P["eye_pupil"], [
        (FX - 8, FY - 8), (FX + 8, FY - 6), (FX + 8, FY - 3), (FX - 8, FY - 5),
    ])
    pygame.draw.line(surf, P["helm_hi"], (FX - 7, FY - 8), (FX + 7, FY - 6), 1)

    # ── ONE WIDE STARING EYE ─────────────────────────────────────────────────
    # Big almond eye-white + dark pupil + white glint on the pale cheek patch —
    # oversized so the single stare survives the downscale.
    ex, ey = FX - 4, FY - 4
    pygame.draw.ellipse(surf, P["white"], (ex, ey, 10, 6))
    pygame.draw.circle(surf, P["eye_pupil"], (ex + 5, ey + 3), 3)
    pygame.draw.circle(surf, P["eye_glint"], (ex + 6, ey + 2), 1)
    pygame.draw.line(surf, P["eye_pupil"], (ex, ey + 5), (ex + 9, ey + 5), 1)

    # ── BUSHY WALRUS MOUSTACHE (middle band, framing the beak) ───────────────
    # A heavy dark band slung under the cheek that droops at both corners; sits
    # BETWEEN the light cheek and the beard so it reads as its own feature.
    mly = FY + 1
    moustache = [
        (FX - 12, mly),           # far-left swell
        (FX - 13, mly + 5),       # left droop tip
        (FX - 8, mly + 8),        # left corner curling toward the beard
        (FX - 3, mly + 4),
        (FX + 1, mly + 5),        # dip under the nose between the halves
        (FX + 6, mly + 4),
        (FX + 10, mly + 8),       # right corner droop (beak side)
        (FX + 13, mly + 4),
        (FX + 11, mly),           # far-right swell
        (FX, mly - 2),            # top centre, just under the cheek/eye
    ]
    S._poly(surf, beard, moustache)
    pygame.draw.line(surf, beard_hi, (FX - 11, mly + 1), (FX - 2, mly), 1)
    pygame.draw.line(surf, beard_hi, (FX, mly), (FX + 10, mly + 1), 1)
    for bx, byy in ((FX - 10, mly + 3), (FX - 6, mly + 5), (FX + 5, mly + 5), (FX + 9, mly + 3)):
        pygame.draw.line(surf, beard_hi, (bx, byy), (bx, byy + 2), 1)
    # Bone beads clasping the droop tips — the only ornament; keeps the V-read.
    pygame.draw.circle(surf, bone, (FX - 8, mly + 8), 1)
    pygame.draw.circle(surf, bone, (FX + 10, mly + 8), 1)


def _paint_axe(surf, wing_angle, P):
    blade, blade_dk, blade_hi = P["blade"], P["blade_dk"], P["blade_hi"]
    haft, haft_hi = P["haft"], P["haft_hi"]
    ring, white = P["ring"], P["white"]

    # Two-fisted grip across the chest/belly, head hoisted HIGH over the far
    # (back) shoulder so it clears the helm AND the right-side face entirely and
    # breaks the silhouette on the upper-left — the classic raised-axe brute pose.
    gx, gy = 47, 60          # lower fist at the belly
    ux, uy = 40, 48          # upper fist across the chest
    tx, ty = 27, 14          # axe head centre, hoisted high-left over the shoulder

    # ── HAFT ─────────────────────────────────────────────────────────────────
    pygame.draw.line(surf, (0, 0, 0), (gx, gy), (tx, ty), 5)      # dark core
    pygame.draw.line(surf, haft, (gx, gy), (tx, ty), 4)
    pygame.draw.line(surf, haft_hi, (gx - 1, gy), (tx - 1, ty), 1)
    # Whipping bands so the haft reads as wrapped wood.
    for t in (0.30, 0.55, 0.78):
        wx = int(gx + (tx - gx) * t)
        wy = int(gy + (ty - gy) * t)
        pygame.draw.line(surf, blade_dk, (wx - 2, wy), (wx + 2, wy), 1)
    # Butt cap below the lower fist.
    pygame.draw.circle(surf, ring, (gx - 1, gy + 2), 2)
    pygame.draw.circle(surf, white, (gx - 2, gy + 1), 1)

    # ── HEAVY DOUBLE-BIT HEAD (twin crescent blades flanking the haft) ───────
    # Each bit is a crescent with a CONCAVE inner waist so the two read as
    # blades on a slim socket — not a solid block (which looked like a helmet).
    # The horns flare past the cutting edge so the silhouette stays brutal.
    # Left bit (cutting edge faces back-left, breaking the silhouette). Horns
    # come to sharp points so it reads as an axe, never a hammer.
    left_bit = [
        (tx - 3, ty - 7),      # inner top (near the haft)
        (tx - 14, ty - 11),    # upper horn POINT (flared past the edge)
        (tx - 18, ty - 1),     # cutting-edge waist
        (tx - 14, ty + 11),    # lower horn POINT
        (tx - 3, ty + 7),      # inner bottom
        (tx - 6, ty),          # concave neck toward the socket
    ]
    # Right bit (mirror).
    right_bit = [
        (tx + 3, ty - 7),
        (tx + 14, ty - 11),
        (tx + 18, ty - 1),
        (tx + 14, ty + 11),
        (tx + 3, ty + 7),
        (tx + 6, ty),
    ]
    for bit in (left_bit, right_bit):
        S._poly(surf, blade_dk, bit)
    # Inner brighter steel facet on each bit for the bevel.
    S._poly(surf, blade, [
        (tx - 4, ty - 6), (tx - 12, ty - 8), (tx - 14, ty), (tx - 12, ty + 8), (tx - 4, ty + 6),
    ])
    S._poly(surf, blade, [
        (tx + 4, ty - 6), (tx + 12, ty - 8), (tx + 14, ty), (tx + 12, ty + 8), (tx + 4, ty + 6),
    ])
    # Hot cutting-edge highlights along each crescent's outer arc.
    pygame.draw.lines(surf, blade_hi, False,
                      [(tx - 14, ty - 11), (tx - 18, ty - 1), (tx - 14, ty + 11)], 2)
    pygame.draw.lines(surf, blade_hi, False,
                      [(tx + 14, ty - 11), (tx + 18, ty - 1), (tx + 14, ty + 11)], 2)
    pygame.draw.line(surf, white, (tx - 18, ty - 1), (tx - 17, ty), 1)
    pygame.draw.line(surf, white, (tx + 18, ty - 1), (tx + 17, ty), 1)
    # Slim socket where the bits clamp the haft — a thin dark band, one ring stud.
    pygame.draw.rect(surf, blade_dk, (tx - 2, ty - 8, 4, 16))
    pygame.draw.circle(surf, ring, (tx, ty), 1)

    # ── TWO FISTS / CLAW KNUCKLES on the haft (grip read) ────────────────────
    for fx, fy in ((gx, gy), (ux, uy)):
        pygame.draw.circle(surf, P["beard"], (fx, fy), 3)
        pygame.draw.circle(surf, P["beard_hi"], (fx - 1, fy - 1), 2)
        # Three knuckle pips across each fist.
        for k in (-2, 0, 2):
            pygame.draw.circle(surf, P["eye_pupil"], (fx + k, fy - 2), 1)


build_ironclad = S.make_build(_paint_face, _paint_axe, S.IRONCLAD)
build_bloodaxe = S.make_build(_paint_face, _paint_axe, S.BLOODAXE)
