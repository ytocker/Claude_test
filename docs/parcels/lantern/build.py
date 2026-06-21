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

SIZE = 22
SS = 44  # 2× supersample; smoothscaled down for a crisp outline at 22px

# DAY palette — vermilion body shading to a deeper core wall, gold caps, dark
# maroon tassel. Bright inner sheen lifts the day read and seeds the night glow.
VERM = (0xD6, 0x3A, 0x2E)        # vermilion body
VERM_D = (0xA8, 0x26, 0x1E)      # deeper red at the body walls (curvature)
VERM_HI = (0xF2, 0x6E, 0x52)     # lit spine of the orb
GOLD = (0xE8, 0xB2, 0x3C)        # flat gold caps
GOLD_HI = (0xFB, 0xDF, 0x8E)     # cap top sheen
GOLD_D = (0xB0, 0x83, 0x22)      # cap underside / rim shadow
TASSEL = (0x7A, 0x20, 0x18)      # dark maroon tassel cord + fringe
OUTLINE = (0x3A, 0x10, 0x0C)     # dark high-value edge to hold the silhouette

# NIGHT baked glow — warm core blooming outward; soft additive rings.
GLOW_CORE = (0xFF, 0xD0, 0x8A)   # hot pale-gold centre of the bloom
GLOW_EDGE = (0xFF, 0x7A, 0x55)   # warm coral falloff


def _lerp(a, b, t):
    return (round(a[0] + (b[0] - a[0]) * t),
            round(a[1] + (b[1] - a[1]) * t),
            round(a[2] + (b[2] - a[2]) * t))


def _glow(s, cx, cy):
    """Soft additive radial bloom centred on the body. Drawn UNDER everything
    so the lantern looks like a light source. Stacked translucent circles with
    additive blend give a smooth round falloff that reads warm in day and
    blooms against the night sky — the showpiece moment of this parcel."""
    R = 22
    glow = pygame.Surface((R * 2, R * 2), pygame.SRCALPHA)
    # Many thin rings from edge inward so the gradient is smooth, not banded.
    for i in range(R, 0, -1):
        t = i / R                       # 1 at the rim, 0 at the core
        col = _lerp(GLOW_CORE, GLOW_EDGE, t)
        # Falloff: faint at the rim, denser near the core — quadratic so the
        # bloom has a soft skirt and a bright heart.
        a = int(70 * (1.0 - t) ** 2) + 4
        pygame.draw.circle(glow, col + (a,), (R, R), i)
    s.blit(glow, (cx - R, cy - R), special_flags=pygame.BLEND_RGBA_ADD)


def _cap(s, cx, y, half_w, h, flip=False):
    """Flat gold cap disc: dark rim, gold body with a lit top sheen. `flip`
    shades it as the underside cap (sheen on the bottom edge instead)."""
    rect = pygame.Rect(cx - half_w, y, half_w * 2, h)
    pygame.draw.rect(s, OUTLINE, rect.inflate(3, 3), border_radius=3)
    fill = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    for ry in range(rect.h):
        t = ry / max(1, rect.h - 1)
        if flip:
            t = 1.0 - t
        fill.fill(_lerp(GOLD, GOLD_D, t) + (255,),
                  pygame.Rect(0, ry, rect.w, 1))
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

    # Vertical layout (2× space): top cap, round body, bottom cap, tassel.
    # Kept centred a touch high so the visible LOWER half — body + bottom cap +
    # tassel — carries the read where Pip doesn't occlude it.
    body_cy = 21
    body_hw = 14          # body half-width (orb radius-ish)
    body_hh = 12          # body half-height — slightly squashed barrel

    # ---- NIGHT GLOW first, baked UNDER the body so the lantern emits light.
    _glow(s, cx, body_cy)

    # ---- TASSEL — short dark cord + a small fringe tuft hanging below the
    # bottom cap. Kept narrow + centred so it survives rotation without smearing
    # into a tail, and so the gold cap above it stays the dominant cue.
    bot_cap_y = body_cy + body_hh - 1
    tass_top = bot_cap_y + 5
    pygame.draw.line(s, OUTLINE, (cx, bot_cap_y), (cx, tass_top + 1), 4)
    pygame.draw.line(s, TASSEL, (cx, bot_cap_y), (cx, tass_top), 2)
    # Fringe tuft — a small dark trapezoid of strands.
    tuft = [(cx - 4, tass_top), (cx + 4, tass_top),
            (cx + 5, tass_top + 7), (cx - 5, tass_top + 7)]
    pygame.draw.polygon(s, OUTLINE, tuft)
    pygame.draw.polygon(s, TASSEL,
                        [(cx - 3, tass_top + 1), (cx + 3, tass_top + 1),
                         (cx + 4, tass_top + 6), (cx - 4, tass_top + 6)])
    # A couple of strand splits so the fringe reads as threads, not a block.
    for dx in (-2, 0, 2):
        pygame.draw.line(s, OUTLINE, (cx + dx, tass_top + 2),
                         (cx + dx, tass_top + 6), 1)

    # ---- BODY — round vermilion barrel. Outline frame first, then a horizontal
    # red→deep-red banded fill so the orb reads as a lit cylinder with a bright
    # spine down the centre and shaded walls (sells curvature + emission).
    body = pygame.Rect(cx - body_hw, body_cy - body_hh,
                       body_hw * 2, body_hh * 2)
    pygame.draw.ellipse(s, OUTLINE, body.inflate(3, 3))
    fill = pygame.Surface((body.w, body.h), pygame.SRCALPHA)
    for x in range(body.w):
        t = abs(x - body.w / 2) / (body.w / 2)   # 0 at spine, 1 at the wall
        # Lit warm spine in the middle, deepening to VERM_D at the rounded
        # walls; the spine slightly hotter than flat vermilion sells the glow.
        col = _lerp(_lerp(VERM_HI, VERM, 0.45), VERM_D, t)
        fill.fill(col + (255,), pygame.Rect(x, 0, 1, body.h))
    mask = pygame.Surface((body.w, body.h), pygame.SRCALPHA)
    pygame.draw.ellipse(mask, (255, 255, 255, 255), mask.get_rect())
    fill.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    s.blit(fill, body.topleft)

    # ---- RIBBING — 2 faint vertical seams either side of the spine. Subtle so
    # the glow does the work; just enough to say "paper lantern panels".
    for dx in (-7, -2, 4, 9):
        x = cx + dx
        # Arc the seam to the barrel curve: shorten toward the walls.
        edge = abs(dx) / body_hw
        h = int(body_hh * (1.0 - 0.45 * edge))
        shade = _lerp(VERM_D, VERM, 0.3) if abs(dx) <= 4 else VERM_D
        pygame.draw.line(s, shade, (x, body_cy - h), (x, body_cy + h), 1)

    # ---- Bright vertical specular sheen just left of the spine — the wet-paper
    # catch-light that makes the body feel lit from within.
    pygame.draw.line(s, _lerp(VERM_HI, GLOW_CORE, 0.5) + (200,),
                     (cx - 3, body_cy - body_hh + 4),
                     (cx - 3, body_cy + body_hh - 4), 1)

    # ---- GOLD CAPS top and bottom — the high-contrast keyline that separates
    # the lantern from Pip's red body. Bottom cap drawn after the body so it
    # sits crisply over the tassel cord root.
    cap_hw = 9
    cap_h = 5
    _cap(s, cx, body_cy - body_hh - cap_h + 2, cap_hw, cap_h)          # top
    _cap(s, cx, body_cy + body_hh - 3, cap_hw, cap_h, flip=True)       # bottom

    # ---- Tiny top hanger loop so it reads as a hung lantern (mostly occluded
    # by Pip in carry, but completes the silhouette on the store card).
    loop_y = body_cy - body_hh - cap_h
    pygame.draw.arc(s, GOLD_D, pygame.Rect(cx - 4, loop_y - 5, 8, 8),
                    math.radians(20), math.radians(160), 2)
    pygame.draw.arc(s, GOLD_HI, pygame.Rect(cx - 4, loop_y - 6, 8, 8),
                    math.radians(40), math.radians(140), 1)

    return pygame.transform.smoothscale(s, (SIZE, SIZE))
