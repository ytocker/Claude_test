"""MINI UFO parcel cosmetic (PREMIUM tier).

A tiny flying saucer tractor-beaming Pip's cargo: a WIDE FLAT chrome SAUCER
disc with a domed teal CANOPY on top and a glowing trapezoid BEAM-CONE
projected DOWN below it. At 22px the read is the classic "hat-on-a-line-of-
light" — a wide thin disc capped by a small dome, with an unmistakable cone
of light spilling beneath. Nothing else in the parcel set has a beam or a
chrome body, so the sci-fi tell is exclusive.

Carry composition drives the layout: in gameplay the parcel rides centred ~12px
below Pip, so the TOP half of the 22px sprite is buried in his red belly. We
therefore weight the whole saucer LOW — the full chrome disc sits in the visible
lower half and the dome is the only part allowed to vanish into shadow. A hard
value/hue break (light rim + dark gap) along the disc's TOP edge stops the
chrome fusing into his red, and a teal rim-glow on the disc's LOWER leading edge
keeps the chrome+teal contrast in the part that actually shows.

The beam is BAKED as a downward additive vertical gradient clipped to a wide
trapezoid that flares well past the sprite floor, so the cone survives carry
occlusion AND the smoothscale, reading as light spilling beneath the saucer at
any bank angle. A brighter cool-white core stripe with a faint cool-dark edge
holds the cone's shape against the bright day sky. Rim-light dots stay tiny so
they don't muddy the disc silhouette at 22px.
"""
import pygame

from game.parrot import _lerp_color


# Day palette per brief.
CHROME = (185, 194, 204)        # #B9C2CC saucer body
CHROME_HI = (224, 230, 238)     # lit top edge of the disc
UNDER = (90, 100, 112)          # #5A6470 dark saucer underside
UNDER_LO = (58, 66, 78)         # deepest belly shade
CANOPY = (72, 214, 200)         # #48D6C8 teal dome
CANOPY_HI = (170, 246, 238)     # dome crown catch
CANOPY_LO = (40, 150, 142)      # shaded dome base
OUTLINE = (24, 34, 44)          # dark high-value keyline for the bright sky

# Teal/cool bake — beam glow, rim-light dots, and the lower-edge teal rim.
BEAM_CORE = (124, 240, 224)     # #7CF0E0 beam apex colour
BEAM_STRIPE = (210, 255, 248)   # #D2FFF8 bright core stripe (holds on day sky)
BEAM_EDGE = (30, 96, 104)       # cool-dark cone outline so day doesn't wash it
RIM_DOT = (159, 255, 240)       # #9FFFF0 rim-light pip
TEAL_RIM = (96, 232, 218)       # teal leading-edge glow on the visible disc lip


def _bake_beam(size, apex_x, apex_y, half_top, half_bot, top_y, bot_y,
               core, core_alpha):
    """A downward additive light-cone: a trapezoid that widens as it falls,
    filled with a vertical gradient that fades core→transparent. Baked onto
    its own SRCALPHA layer so the rotation in the harness carries it as one
    glowing cone trailing off the disc."""
    layer = pygame.Surface((size, size), pygame.SRCALPHA)
    span = max(1, bot_y - top_y)
    for y in range(top_y, bot_y):
        t = (y - top_y) / span
        # Cone widens linearly toward the bottom; brightness falls off so the
        # apex glows hot under the saucer and the mouth dissolves into air.
        half = half_top + (half_bot - half_top) * t
        a = int(core_alpha * (1.0 - t) ** 1.25)
        if a <= 0:
            continue
        pygame.draw.line(layer, core + (a,),
                         (apex_x - half, y), (apex_x + half, y))
    return layer


def build(mode: str = "normal") -> pygame.Surface:
    # mode is ignored — the UFO keeps its chrome/teal look across power-ups.
    SIZE = 44
    surf = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)
    cx = SIZE // 2

    # Vertical stack tuned for CARRY occlusion: the sprite midline (y≈22 on the
    # 44px canvas, y≈11 at 22px) is where Pip's belly cuts in. Everything below
    # it shows, so the full disc lives BELOW the midline and the beam flares to
    # the floor. Only the dome pokes above the midline — it's the part allowed
    # to disappear into his shadow.
    disc_cy = 27                    # disc fully in the visible lower half
    disc_rx, disc_ry = 18, 6        # wide + flat: the saucer signature
    dome_cx, dome_cy = cx, disc_cy - 7
    dome_rx, dome_ry = 9, 8

    # ── BEAM CONE (bottom layer so the disc rim caps its apex) ──────────────
    # Apex tucked just under the disc belly; mouth flares WIDE to the canvas
    # floor so the cone spills clearly past Pip's body even when carried.
    # Cool-dark edge first (slightly wider) so the bright core reads as a shape
    # against the day sky instead of dissolving.
    beam_edge = _bake_beam(SIZE, cx, disc_cy + disc_ry, 9, 22,
                           disc_cy + disc_ry, 44, BEAM_EDGE, 180)
    surf.blit(beam_edge, (0, 0))
    beam = _bake_beam(SIZE, cx, disc_cy + disc_ry, 7, 19,
                      disc_cy + disc_ry, 44, BEAM_CORE, 215)
    surf.blit(beam, (0, 0), special_flags=pygame.BLEND_PREMULTIPLIED)
    # A brighter cool-white inner stripe sells the projector hot-spot and gives
    # the cone a hard centre line that holds against a bright sky — kept high
    # alpha so the beam reads even when its apex is occluded by Pip in carry.
    core = _bake_beam(SIZE, cx, disc_cy + disc_ry, 3, 9,
                      disc_cy + disc_ry, 43, BEAM_STRIPE, 210)
    surf.blit(core, (0, 0), special_flags=pygame.BLEND_PREMULTIPLIED)

    # ── DOME canopy ─────────────────────────────────────────────────────────
    # Dark keyline behind a teal gradient dome. Drawn before the disc so the
    # disc rim overlaps the dome's mouth — dome reads as seated in the hull.
    dome_rect = pygame.Rect(dome_cx - dome_rx, dome_cy - dome_ry,
                            dome_rx * 2, dome_ry * 2)
    pygame.draw.ellipse(surf, OUTLINE, dome_rect.inflate(4, 4))
    dome = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)
    for y in range(dome_rect.top, dome_rect.bottom):
        t = (y - dome_rect.top) / max(1, dome_rect.height - 1)
        col = _lerp_color(CANOPY_HI, CANOPY_LO, t) + (255,)
        dome.fill(col, pygame.Rect(0, y, SIZE, 1))
    dmask = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)
    pygame.draw.ellipse(dmask, (255, 255, 255, 255), dome_rect)
    dome.blit(dmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(dome, (0, 0))
    # Crown catch — bright teal glint upper-left sells the glass bubble.
    pygame.draw.ellipse(surf, CANOPY_HI,
                        pygame.Rect(dome_cx - 5, dome_cy - 6, 4, 3))

    # ── SAUCER disc ─────────────────────────────────────────────────────────
    # Dark keyline ellipse bakes the wide flat silhouette so it pops on the
    # bright day sky and holds when banked.
    disc_rect = pygame.Rect(cx - disc_rx, disc_cy - disc_ry,
                            disc_rx * 2, disc_ry * 2)
    pygame.draw.ellipse(surf, OUTLINE, disc_rect.inflate(4, 4))

    # Chrome body as a top→bottom gradient (lit crown → dark underside) so the
    # disc reads as a metal hull rounded from above.
    body = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)
    for y in range(disc_rect.top, disc_rect.bottom):
        t = (y - disc_rect.top) / max(1, disc_rect.height - 1)
        # Top half chrome, lower half darkens fast into the underside.
        if t < 0.5:
            col = _lerp_color(CHROME_HI, CHROME, t * 2)
        else:
            col = _lerp_color(CHROME, UNDER_LO, (t - 0.5) * 2)
        body.fill(col + (255,), pygame.Rect(0, y, SIZE, 1))
    bmask = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)
    pygame.draw.ellipse(bmask, (255, 255, 255, 255), disc_rect)
    body.blit(bmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(body, (0, 0))

    # ── HARD TOP-EDGE BREAK ───────────────────────────────────────────────────
    # Where the disc's top meets Pip's red belly it must not fuse into his
    # shadow. A 1px dark gap just above the disc, then a bright chrome rim on
    # the disc's top lip, makes a hard value/hue edge that snaps the chrome off
    # his body in the carry pose.
    top_y = disc_rect.top
    pygame.draw.line(surf, OUTLINE,
                     (cx - disc_rx + 4, top_y - 1),
                     (cx + disc_rx - 4, top_y - 1), 1)
    pygame.draw.line(surf, CHROME_HI,
                     (cx - disc_rx + 5, top_y + 1),
                     (cx + disc_rx - 6, top_y + 1), 1)

    # Hull seam — a dark equatorial line splits canopy-deck from underside and
    # reads as the riveted rim band of a saucer.
    pygame.draw.line(surf, UNDER_LO,
                     (cx - disc_rx + 2, disc_cy + 1),
                     (cx + disc_rx - 2, disc_cy + 1), 1)

    # ── TEAL LOWER-EDGE RIM ───────────────────────────────────────────────────
    # The disc's LOWER leading lip is the part that always shows in carry, so it
    # carries the chrome+teal signature: a teal glow rim catching the beam light
    # bouncing back up onto the saucer belly.
    lip_y = disc_cy + disc_ry - 1
    pygame.draw.line(surf, TEAL_RIM,
                     (cx - disc_rx + 4, lip_y),
                     (cx + disc_rx - 4, lip_y), 2)
    pygame.draw.line(surf, (TEAL_RIM[0], TEAL_RIM[1], TEAL_RIM[2], 120),
                     (cx - disc_rx + 2, lip_y + 1),
                     (cx + disc_rx - 2, lip_y + 1), 1)

    # ── RIM-LIGHT dots ──────────────────────────────────────────────────────
    # Three little running lights along the disc's leading edge. Kept tiny so
    # they spark the hull without breaking the silhouette at 22px; each gets a
    # soft halo so the night bake glows.
    for rx in (-11, 0, 11):
        dx, dy = cx + rx, disc_cy + disc_ry - 2
        pygame.draw.circle(surf, (RIM_DOT[0], RIM_DOT[1], RIM_DOT[2], 90),
                           (dx, dy), 3)
        pygame.draw.circle(surf, RIM_DOT, (dx, dy), 1)

    return pygame.transform.smoothscale(surf, (22, 22))
