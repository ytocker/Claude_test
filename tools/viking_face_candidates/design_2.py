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
    # IRONCLAD collapses to brown-on-brown, so every feature edge needs a hard
    # value step or a near-black keyline. The keyline RGB (alpha dropped) is the
    # darkest tone available and the same separator the base costume rings with,
    # so 1px of it reads in BOTH palettes without inventing a new colour.
    key = P["keyline"][:3]

    # The horned helm caps the head down to ~y45; below it the bird's CHEEK/BEAK
    # pokes out. The face reads as a clean vertical stack on that exposed front:
    # EYE on a light cheek patch (top) -> bushy WALRUS MOUSTACHE band (middle) ->
    # BROAD SQUARE BEARD onto the chest (bottom). Stacking them — rather than
    # piling dark hair over a dark eye — is what makes all three legible at 40px.
    FX, FY = 51, 50

    # ── BROAD SQUARE BEARD (bottom of the stack) ─────────────────────────────
    # One big shaggy block onto the chest, squared at the bottom so the brute
    # silhouette stays heavy. Its TOP edge stops below the moustache so the eye
    # and 'stache aren't swallowed. NO per-strand lines — at 40px they were noise;
    # the squared mass + one strong side highlight does the legible work.
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
    # Keyline ring first so the dark beard separates from the dark fur/body on
    # the rust BLOODAXE merge — a faint outline does what value alone can't there.
    S._poly(surf, key, [(x, y + 1) for x, y in beard_block])
    S._poly(surf, beard, beard_block)
    # ONE bold highlight carried down the LEFT face of the block — a single broad
    # band, not strands. Brighter so it survives on BLOODAXE's near-black beard.
    S._poly(surf, beard_hi, [
        (FX - 12, by0 + 1), (FX - 7, by0 + 2), (FX - 8, by0 + 12), (FX - 13, by0 + 11),
    ])
    # Hard square bottom edge keyed dark so the silhouette reads as a clean block.
    pygame.draw.line(surf, key, (FX - 12, by0 + 14), (FX + 7, by0 + 11), 1)

    # ── LIGHT CHEEK PATCH (so the eye + 'stache have contrast) ───────────────
    # A pale skin patch under the helm rim where the eye sits, so the face holds
    # its value gap against the dark beard/helm even at 40px.
    S._poly(surf, P["eye_skin"], [
        (FX - 8, FY - 7), (FX + 8, FY - 6), (FX + 9, FY + 1), (FX - 7, FY + 2),
    ])

    # ── SCOWLING BROW (lifted to open a bone gap over the eye) ───────────────
    # A hard dark wedge angled down toward the beak — the rage line. Pulled up
    # ~2px so a clean strip of pale eye_skin sits between brow and eye-white;
    # that bone gap is the strongest tell that the eye is OPEN, not a dark smear.
    S._poly(surf, P["eye_pupil"], [
        (FX - 8, FY - 10), (FX + 8, FY - 8), (FX + 8, FY - 6), (FX - 8, FY - 7),
    ])
    pygame.draw.line(surf, P["helm_hi"], (FX - 7, FY - 10), (FX + 7, FY - 8), 1)
    # The bone brow-line: a lit sliver of skin just under the brow.
    pygame.draw.line(surf, P["eye_skin"], (FX - 7, FY - 5), (FX + 8, FY - 4), 1)

    # ── ONE WIDE STARING EYE (grown ~30% to read as a bright spot) ───────────
    # Big almond eye-white + dark pupil + single white glint on the pale cheek —
    # oversized so the lone stare survives the downscale as a clear light dot.
    ex, ey = FX - 5, FY - 3
    pygame.draw.ellipse(surf, P["white"], (ex, ey, 13, 7))
    pygame.draw.ellipse(surf, key, (ex, ey, 13, 7), 1)   # crisp rim on the white
    pygame.draw.circle(surf, P["eye_pupil"], (ex + 7, ey + 4), 3)
    pygame.draw.circle(surf, P["eye_glint"], (ex + 8, ey + 2), 1)
    pygame.draw.line(surf, P["eye_pupil"], (ex, ey + 6), (ex + 12, ey + 6), 1)

    # ── BUSHY WALRUS MOUSTACHE (middle band, framing the beak) ───────────────
    # A heavy band slung under the cheek that droops at both corners; sits
    # BETWEEN the light cheek and the beard. It is filled at beard_hi — a whole
    # LIGHTER band — so it reads as a distinct walrus 'stache resting on the
    # darker beard below, not as one continuous dark mass.
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
    S._poly(surf, key, moustache)        # keyline base separates it from beard
    S._poly(surf, beard_hi, [(x, y - 1) for x, y in moustache])  # lighter band on top
    # Combed grain in the darker beard tone so the lighter band still reads hairy.
    for bx, byy in ((FX - 10, mly + 2), (FX - 6, mly + 4), (FX + 5, mly + 4), (FX + 9, mly + 2)):
        pygame.draw.line(surf, beard, (bx, byy), (bx, byy + 2), 1)
    # Continuous dark underline along the full droop so the band's lower edge
    # reads hard against the beard mass in either palette.
    pygame.draw.lines(surf, key, False,
                      [(FX - 13, mly + 5), (FX - 8, mly + 8), (FX, mly + 6),
                       (FX + 10, mly + 8), (FX + 13, mly + 4)], 1)
    # Bone beads clasping the droop tips — the only ornament; keeps the V-read.
    pygame.draw.circle(surf, bone, (FX - 8, mly + 8), 1)
    pygame.draw.circle(surf, bone, (FX + 10, mly + 8), 1)


def _paint_axe(surf, wing_angle, P):
    blade, blade_dk, blade_hi = P["blade"], P["blade_dk"], P["blade_hi"]
    haft, haft_hi = P["haft"], P["haft_hi"]
    ring, white, bone = P["ring"], P["white"], P["bone"]
    key = P["keyline"][:3]

    # Two-fisted grip across the chest/belly, head hoisted HIGH over the far
    # (back) shoulder so it clears the helm AND the right-side face entirely and
    # breaks the silhouette on the upper-left. Nudged 3px further up-left (tx-3,
    # ty-2) so the big head sits tight over the shoulder and stops crowding the
    # face — the head was the dominant mass before.
    gx, gy = 47, 60          # lower fist at the belly
    ux, uy = 40, 48          # upper fist across the chest
    tx, ty = 24, 12          # axe head centre, hoisted high-left over the shoulder

    # ── HAFT (thicker so the held shaft reads at 40px) ───────────────────────
    pygame.draw.line(surf, key, (gx, gy), (tx, ty), 6)           # dark core
    pygame.draw.line(surf, haft, (gx, gy), (tx, ty), 5)
    pygame.draw.line(surf, haft_hi, (gx - 1, gy), (tx - 1, ty), 1)
    # Whipping bands so the haft reads as wrapped wood.
    for t in (0.30, 0.55, 0.78):
        wx = int(gx + (tx - gx) * t)
        wy = int(gy + (ty - gy) * t)
        pygame.draw.line(surf, blade_dk, (wx - 2, wy), (wx + 2, wy), 1)

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

    # ── TWO FISTS gripping the haft (grip read) ──────────────────────────────
    # Upper fist: a small knuckled fist across the chest.
    pygame.draw.circle(surf, key, (ux, uy), 4)
    pygame.draw.circle(surf, P["beard"], (ux, uy), 3)
    pygame.draw.circle(surf, P["beard_hi"], (ux - 1, uy - 1), 2)
    for k in (-2, 0, 2):
        pygame.draw.circle(surf, key, (ux + k, uy - 2), 1)

    # LOWER fist at the belly: an unmistakable contrasting gripping blob. A
    # bone/ring knuckle wrap over a keyed fist anchors the "hand holding the
    # haft" read — the brightest non-steel mass at the belly so the grip is
    # never ambiguous, in either palette.
    pygame.draw.circle(surf, key, (gx, gy), 5)
    pygame.draw.circle(surf, P["beard"], (gx, gy), 4)
    pygame.draw.circle(surf, ring, (gx + 1, gy), 3)        # bronze/steel knuckle wrap
    for k in (-2, 1):
        pygame.draw.circle(surf, bone, (gx + k, gy - 1), 1)  # lit knuckle bumps
    pygame.draw.line(surf, key, (gx - 3, gy + 3), (gx + 4, gy + 3), 1)  # base of fist


build_ironclad = S.make_build(_paint_face, _paint_axe, S.IRONCLAD)
build_bloodaxe = S.make_build(_paint_face, _paint_axe, S.BLOODAXE)
