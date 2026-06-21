"""PAPER LANTERN parcel cosmetic (HIGH tier).

A glowing red festival paper lantern: a round vermilion BODY between flat GOLD
CAPS top and bottom, with a short dark TASSEL hanging below — the first GLOWING
parcel. At 22px it reads as a luminous orb pinched between two gold discs, which
is radially clean: the symmetric orb survives the bird's tilt rotation at every
bank because it has no "up" the way a box or bottle does.

Built at 2× (44px) then smoothscaled to 22 so the dark outline, the gold cap
rims, and the ribbing survive the tiny read. The NIGHT showpiece is a soft
ADDITIVE radial glow baked UNDER the body (warm #FF7A55→#FFD08A rings) — it
reads as a faint warm halo in daylight but BLOOMS against the dark night sky.

Carry context: Pip's red body/wing occludes the TOP, and the lantern's own red
could merge into his — so the identity lives in the LOWER/visible half and leans
on the GOLD CAPS + the glow bloom for separation from Pip."""
import math
import pygame

# The lantern is the first GLOWING parcel, so the sprite is intentionally LARGER
# than the 22px base parcel: the lantern body still draws at the same pixel scale
# (~22px), but the extra margin holds the additive night-glow halo so it can
# BLOOM out onto the open sky instead of dying inside the silhouette. Centre-
# anchored in carry, so the bigger surface keeps the body where it always sat and
# only the warm glow spills past it. Collision uses PARCEL_R, not sprite size.
SIZE = 34
SS = 68  # 2× supersample; smoothscaled down for a crisp outline + glow skirt

# DAY palette — vermilion body DEEPENED so the walls read mid-dark, gold caps
# pushed LIGHT so the cap/body value gap is unambiguous in grayscale (this is
# what stops the lantern's red melting into Pip's red). Dark maroon tassel.
VERM = (0xC4, 0x2C, 0x22)        # vermilion body mid-tone
VERM_D = (0x8E, 0x1E, 0x16)      # DEEP red at the body walls (mid-dark value)
VERM_HI = (0xEC, 0x60, 0x46)     # lit spine of the orb
GOLD = (0xEE, 0xBC, 0x44)        # flat gold caps (lighter than R1)
GOLD_HI = (0xFB, 0xDF, 0x8E)     # cap top sheen — dominant LIGHT value
GOLD_D = (0xB8, 0x88, 0x26)      # cap underside / rim shadow
TASSEL = (0x6E, 0x1A, 0x14)      # dark maroon tassel cord
TASSEL_HI = (0xE0, 0xB0, 0x40)   # one gold bead on the tassel
OUTLINE = (0x33, 0x0D, 0x09)     # dark high-value edge to hold the silhouette
# Cool dark keyline where the upper-left body edge meets Pip's warm red, so the
# silhouette pops off the bird instead of melting into it.
KEYLINE = (0x2A, 0x0A, 0x0C)

# NIGHT baked glow — a hot pale core blooming WIDE; soft additive rings. The
# showpiece: it must obviously EMIT at 22px and spill onto the dark sky.
GLOW_CORE = (0xFF, 0xC9, 0x8A)   # hot pale-gold heart of the bloom
GLOW_EDGE = (0xFF, 0x82, 0x4E)   # warm coral skirt falloff


def _lerp(a, b, t):
    return (round(a[0] + (b[0] - a[0]) * t),
            round(a[1] + (b[1] - a[1]) * t),
            round(a[2] + (b[2] - a[2]) * t))


def _glow(s, cx, cy, body_hw):
    """Soft additive radial bloom centred on the body — the SHOWPIECE. Drawn
    UNDER everything so the lantern looks like a true light source. Stacked
    translucent circles with additive blend give a smooth round falloff: a hot
    pale heart and a wide warm skirt. Sized to ~1.7× the body footprint so the
    warmth visibly spills onto the dark night sky and obviously EMITS at 22px,
    while in daylight it reads as a gentle warm halo. The supersample surface
    must be big enough to hold the wide skirt without clipping it square."""
    R = int(body_hw * 1.7)              # ~1.7× footprint — wide enough to bloom
    glow = pygame.Surface((R * 2, R * 2), pygame.SRCALPHA)
    # Many thin rings from edge inward so the gradient is smooth, not banded.
    for i in range(R, 0, -1):
        t = i / R                       # 1 at the rim, 0 at the core
        col = _lerp(GLOW_CORE, GLOW_EDGE, t)
        # Falloff: a soft but PRESENT skirt at the rim, climbing to a bright
        # heart. Higher peak + a non-zero rim floor so the bloom carries onto
        # the night sky instead of dying inside the silhouette.
        a = int(150 * (1.0 - t) ** 1.7) + 16
        pygame.draw.circle(glow, col + (min(255, a),), (R, R), i)
    # A second tight, hot inner core so the heart of the lantern clearly burns.
    for i in range(int(body_hw * 0.9), 0, -1):
        a = int(120 * (1.0 - i / (body_hw * 0.9))) + 30
        pygame.draw.circle(glow, GLOW_CORE + (min(255, a),), (R, R), i)
    s.blit(glow, (cx - R, cy - R), special_flags=pygame.BLEND_RGBA_ADD)


def _cap(s, cx, y, half_w, h, flip=False):
    """Flat gold cap disc: dark rim, gold body, and a BROAD light sheen so the
    cap is the dominant LIGHT value (clearly lighter than the body in grayscale
    — this is the move that names the lantern and stops the red-on-red mush).
    `flip` shades it as the underside cap (sheen migrates to the bottom edge)."""
    rect = pygame.Rect(cx - half_w, y, half_w * 2, h)
    pygame.draw.rect(s, OUTLINE, rect.inflate(3, 3), border_radius=3)
    fill = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    for ry in range(rect.h):
        t = ry / max(1, rect.h - 1)
        if flip:
            t = 1.0 - t
        # Top ~45% of the cap rides the LIGHT sheen colour so the cap reads as a
        # bright disc, not a mid-gold band; only the underside drops to GOLD_D.
        if t < 0.45:
            col = _lerp(GOLD_HI, GOLD, t / 0.45)
        else:
            col = _lerp(GOLD, GOLD_D, (t - 0.45) / 0.55)
        fill.fill(col + (255,), pygame.Rect(0, ry, rect.w, 1))
    mask = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(),
                     border_radius=2)
    fill.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    s.blit(fill, rect.topleft)
    sheen_y = rect.bottom - 2 if flip else rect.y + 1
    pygame.draw.line(s, GOLD_HI, (rect.x + 2, sheen_y),
                     (rect.right - 3, sheen_y), 1)


def build(mode="normal"):  # mode ignored — parcel is mode-agnostic, one surface
    s = pygame.Surface((SS, SS), pygame.SRCALPHA)
    cx = SS // 2

    # Vertical layout: top cap, round body, bottom cap, tassel — body anchored a
    # touch above canvas centre so the visible LOWER half (body + bottom cap +
    # tassel) carries the read, and the glow halo has room to bloom all around.
    body_cy = SS // 2 - 5
    body_hw = 14          # body half-width (orb radius-ish)
    body_hh = 12          # body half-height — slightly squashed barrel

    # ---- NIGHT GLOW first, baked UNDER the body so the lantern emits light.
    _glow(s, cx, body_cy, body_hw)

    # ---- TASSEL — short dark cord + a small fringe tuft hanging below the
    # bottom cap. Kept narrow + centred so it survives rotation without smearing
    # into a tail, and so the gold cap above it stays the dominant cue.
    bot_cap_y = body_cy + body_hh - 1
    tass_top = bot_cap_y + 6
    pygame.draw.line(s, OUTLINE, (cx, bot_cap_y), (cx, tass_top + 1), 4)
    pygame.draw.line(s, TASSEL, (cx, bot_cap_y), (cx, tass_top), 2)
    # One clear GOLD BEAD on the cord, just above the fringe — a small bright
    # accent that ties the tassel back to the gold caps and reads at size.
    pygame.draw.circle(s, OUTLINE, (cx, tass_top - 1), 3)
    pygame.draw.circle(s, TASSEL_HI, (cx, tass_top - 1), 2)
    pygame.draw.circle(s, GOLD_HI, (cx - 1, tass_top - 2), 1)
    # Darker fringe tuft below the bead — a small trapezoid of strands.
    tuft = [(cx - 4, tass_top + 1), (cx + 4, tass_top + 1),
            (cx + 5, tass_top + 8), (cx - 5, tass_top + 8)]
    pygame.draw.polygon(s, OUTLINE, tuft)
    pygame.draw.polygon(s, TASSEL,
                        [(cx - 3, tass_top + 2), (cx + 3, tass_top + 2),
                         (cx + 4, tass_top + 7), (cx - 4, tass_top + 7)])
    # Strand splits so the fringe reads as threads, not a block.
    for dx in (-2, 0, 2):
        pygame.draw.line(s, OUTLINE, (cx + dx, tass_top + 3),
                         (cx + dx, tass_top + 7), 1)

    # ---- BODY — round vermilion barrel. Outline frame first, then a horizontal
    # red→deep-red banded fill so the orb reads as a lit cylinder with a bright
    # spine down the centre and shaded walls (sells curvature + emission).
    body = pygame.Rect(cx - body_hw, body_cy - body_hh,
                       body_hw * 2, body_hh * 2)
    pygame.draw.ellipse(s, OUTLINE, body.inflate(3, 3))
    fill = pygame.Surface((body.w, body.h), pygame.SRCALPHA)
    for x in range(body.w):
        t = abs(x - body.w / 2) / (body.w / 2)   # 0 at spine, 1 at the wall
        # Lit warm spine in the middle, deepening to the DEEP wall red so the
        # body reads mid-dark in grayscale (away from the light gold caps).
        col = _lerp(_lerp(VERM_HI, VERM, 0.5), VERM_D, t ** 0.85)
        fill.fill(col + (255,), pygame.Rect(x, 0, 1, body.h))
    mask = pygame.Surface((body.w, body.h), pygame.SRCALPHA)
    pygame.draw.ellipse(mask, (255, 255, 255, 255), mask.get_rect())
    fill.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    s.blit(fill, body.topleft)

    # ---- COOL DARK KEYLINE on the upper-left arc — where the body meets Pip's
    # warm red in carry. A cool near-black rim there makes the silhouette pop
    # off the bird instead of melting into his red.
    pygame.draw.arc(s, KEYLINE, body.inflate(1, 1),
                    math.radians(95), math.radians(205), 2)

    # ---- RIBBING — TWO clean catch-light bands flanking the spine (paper
    # panels), not a row of faint seams. A light band reads as panel sheen; the
    # paired soft shadow gives each panel a rounded edge.
    for side in (-1, 1):
        lx = cx + side * 4                       # catch-light band
        sx = cx + side * 8                       # panel shadow at the wall turn
        lh = int(body_hh * 0.86)
        sh = int(body_hh * 0.62)
        pygame.draw.line(s, _lerp(VERM_HI, GLOW_CORE, 0.35) + (190,),
                         (lx, body_cy - lh), (lx, body_cy + lh), 1)
        pygame.draw.line(s, VERM_D, (sx, body_cy - sh), (sx, body_cy + sh), 1)

    # ---- Bright vertical specular sheen on the spine — the wet-paper
    # catch-light that makes the body feel lit from within.
    pygame.draw.line(s, _lerp(VERM_HI, GLOW_CORE, 0.55) + (210,),
                     (cx - 1, body_cy - body_hh + 4),
                     (cx - 1, body_cy + body_hh - 4), 1)

    # ---- GOLD CAPS top and bottom — the high-contrast keyline that separates
    # the lantern from Pip's red body. Bottom cap drawn after the body so it
    # sits crisply over the tassel cord root.
    cap_hw = 9
    cap_h = 5
    _cap(s, cx, body_cy - body_hh - cap_h + 2, cap_hw, cap_h)          # top
    # Bottom cap is the PRIMARY identifier (top is occluded by Pip), so it is
    # thicker + a touch wider, with its own gold ribs to carry the name.
    bot_hw, bot_h = cap_hw + 1, cap_h + 1
    _cap(s, cx, body_cy + body_hh - 3, bot_hw, bot_h, flip=True)
    for dx in (-4, 0, 4):                        # short gold ribs on bottom cap
        pygame.draw.line(s, GOLD_D,
                         (cx + dx, body_cy + body_hh - 1),
                         (cx + dx, body_cy + body_hh + bot_h - 4), 1)

    # ---- Tiny top hanger loop so it reads as a hung lantern (mostly occluded
    # by Pip in carry, but completes the silhouette on the store card).
    loop_y = body_cy - body_hh - cap_h
    pygame.draw.arc(s, GOLD_D, pygame.Rect(cx - 4, loop_y - 5, 8, 8),
                    math.radians(20), math.radians(160), 2)
    pygame.draw.arc(s, GOLD_HI, pygame.Rect(cx - 4, loop_y - 6, 8, 8),
                    math.radians(40), math.radians(140), 1)

    return pygame.transform.smoothscale(s, (SIZE, SIZE))
