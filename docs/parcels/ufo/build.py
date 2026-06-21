"""MINI UFO parcel cosmetic (PREMIUM tier).

A tiny flying saucer tractor-beaming Pip's cargo: a WIDE FLAT chrome SAUCER
disc with a domed teal CANOPY on top and a glowing trapezoid BEAM-CONE
projected DOWN below it. At 22px the read is the classic "hat-on-a-line-of-
light" — a wide thin disc capped by a small dome, with an unmistakable cone
of light spilling beneath. Nothing else in the parcel set has a beam or a
chrome body, so the sci-fi tell is exclusive.

Why the beam points DOWN: in carry context the parcel's TOP is occluded by
Pip's red body, so the dome lives in shadow while the wide chrome disc and
the bright beam-cone — both in the visible lower half — carry the identity.
Teal canopy + chrome rim contrast cleanly against Pip's red.

The beam is BAKED as a downward additive vertical gradient clipped to a
trapezoid, so it survives the smoothscale and reads as a cone at ANY bank
angle (rotated, it just trails off the saucer). Rim-light dots are kept tiny
so they don't muddy the disc silhouette at 22px.
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

# Night bake — a teal beam glow + cool rim-light dots.
BEAM_CORE = (124, 240, 224)     # #7CF0E0 beam apex colour
RIM_DOT = (159, 255, 240)       # #9FFFF0 rim-light pip


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
        a = int(core_alpha * (1.0 - t) ** 1.4)
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

    # Vertical stack: small dome on top, wide flat disc through the middle,
    # beam-cone spilling down. The disc sits high enough that the whole beam
    # fits in the lower (visible-in-carry) half.
    disc_cy = 19
    disc_rx, disc_ry = 18, 6        # wide + flat: the saucer signature
    dome_cx, dome_cy = cx, disc_cy - 4
    dome_rx, dome_ry = 9, 8

    # ── BEAM CONE (bottom layer so the disc rim caps its apex) ──────────────
    # Apex tucked just under the disc belly; mouth flares to the canvas floor.
    beam = _bake_beam(SIZE, cx, disc_cy + disc_ry, 6, 17,
                      disc_cy + disc_ry, 42, BEAM_CORE, 180)
    surf.blit(beam, (0, 0), special_flags=pygame.BLEND_PREMULTIPLIED)

    # A brighter inner core stripe sells the projector hot-spot.
    core = _bake_beam(SIZE, cx, disc_cy + disc_ry, 2, 7,
                      disc_cy + disc_ry, 40, (210, 255, 248), 150)
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

    # Hull seam — a dark equatorial line splits canopy-deck from underside and
    # reads as the riveted rim band of a saucer.
    pygame.draw.line(surf, UNDER_LO,
                     (cx - disc_rx + 2, disc_cy + 1),
                     (cx + disc_rx - 2, disc_cy + 1), 1)
    # Chrome catch — a bright streak along the lit upper rim.
    pygame.draw.line(surf, CHROME_HI,
                     (cx - disc_rx + 5, disc_cy - disc_ry + 2),
                     (cx + disc_rx - 7, disc_cy - disc_ry + 2), 1)

    # ── RIM-LIGHT dots ──────────────────────────────────────────────────────
    # Three little running lights along the disc's leading edge. Kept tiny so
    # they spark the hull without breaking the silhouette at 22px; each gets a
    # soft halo so the night bake glows.
    for rx in (-11, 0, 11):
        dx, dy = cx + rx, disc_cy + disc_ry - 3
        pygame.draw.circle(surf, (RIM_DOT[0], RIM_DOT[1], RIM_DOT[2], 90),
                           (dx, dy), 3)
        pygame.draw.circle(surf, RIM_DOT, (dx, dy), 1)

    return pygame.transform.smoothscale(surf, (22, 22))
