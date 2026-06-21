"""MINI UFO parcel cosmetic (PREMIUM tier).

A tiny flying saucer tractor-beaming Pip's cargo: a WIDE FLAT chrome SAUCER
disc with a domed teal CANOPY on top and a glowing HARD-EDGED BEAM projected
DOWN below it. At 22px the read is the classic "hat-on-a-line-of-light" — a
wide thin disc capped by a small dome, with an unmistakable column of light
spilling beneath. Nothing else in the parcel set has a beam or a chrome body,
so the sci-fi tell is exclusive.

Carry composition drives the layout: in gameplay the parcel rides centred ~12px
below Pip, so the TOP-LEFT of the 22px sprite is buried in his red belly and
TAIL. We therefore weight the whole saucer LOW and nudge it slightly RIGHT so
the full chrome disc + both rim points clear his wing/tail; the dome is the only
part allowed to vanish into shadow. A hard value/hue break (light rim + dark
gap) along the disc's TOP edge stops the chrome fusing into his red, and a teal
rim-glow on the disc's LOWER leading edge keeps the chrome+teal contrast in the
part that actually shows.

The beam is the required tractor-beam tell, and a soft gradient cone DIES in
carry (it became a few pale specks under Pip). It is therefore baked as a
HARD-EDGED trapezoid with a SOLID near-white CORE COLUMN and a thin teal
outline — value, not hue, carries the read so it survives the grayscale /
colourblind check and wins the value fight against both day clouds and the
night purple. The column is weighted to the BOTTOM of the sprite so a solid
chunk of unambiguous beam survives below the disc rim at 1× in both biomes.
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

# Teal/cool bake — beam, rim-light dots, and the lower-edge teal rim.
BEAM_CORE = (244, 255, 252)     # near-white solid beam column (value-first tell)
BEAM_GLOW = (150, 246, 232)     # teal flare flanking the core inside the trapezoid
BEAM_EDGE = (26, 110, 116)      # thin teal outline that frames the hard beam
RIM_DOT = (159, 255, 240)       # #9FFFF0 rim-light pip
TEAL_RIM = (96, 232, 218)       # teal leading-edge glow on the visible disc lip


def _hard_beam(size, apex_x, apex_y, half_top, half_bot, top_y, bot_y,
               colour, alpha, taper=0.55):
    """A HARD-EDGED downward trapezoid filled with a near-flat colour. Unlike a
    soft cone, the alpha holds (only a gentle taper toward the mouth) so the
    shape is an unmistakable solid bar of light, not a vanishing gradient — this
    is what lets the beam survive carry occlusion + smoothscale in both biomes."""
    layer = pygame.Surface((size, size), pygame.SRCALPHA)
    span = max(1, bot_y - top_y)
    for y in range(top_y, bot_y):
        t = (y - top_y) / span
        half = half_top + (half_bot - half_top) * t
        # Near-flat alpha: keep the column solid, only soften the very mouth so
        # it doesn't end in a hard horizontal line.
        a = int(alpha * (1.0 - taper * t))
        if a <= 0 or half < 0.5:
            continue
        pygame.draw.line(layer, colour + (a,),
                         (apex_x - half, y), (apex_x + half, y))
    return layer


def build(mode: str = "normal") -> pygame.Surface:
    # mode is ignored — the UFO keeps its chrome/teal look across power-ups.
    SIZE = 44
    surf = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)

    # Carry nudge: the parcel rides centred below Pip but his TAIL eats the
    # sprite's left third. Shift the whole UFO ~2px RIGHT (4px on the 44px
    # canvas) and ~2px LOWER so the full chrome ellipse + both rim points clear
    # his wing/tail. cx is no longer the canvas centre — it's the UFO centreline.
    cx = SIZE // 2 + 4

    disc_cy = 26                    # low enough for carry, high enough for beam
    disc_rx, disc_ry = 18, 6        # wide + flat: the saucer signature
    dome_cx, dome_cy = cx, disc_cy - 7
    dome_rx, dome_ry = 9, 8

    # ── BEAM (bottom layer so the disc rim caps its apex) ───────────────────
    # A HARD-EDGED trapezoid built in three stacked passes: a thin teal OUTLINE
    # frame (slightly wider/darker), a teal GLOW fill, and a SOLID near-white
    # CORE COLUMN down the middle. The core is the tell: a value-bright bar that
    # holds against day clouds AND night purple, and survives grayscale.
    beam_top = disc_cy + disc_ry - 1
    beam_bot = 44
    # Outline frame — thin teal border so the hard beam has a defined edge.
    frame = _hard_beam(SIZE, cx, beam_top, 8, 12, beam_top, beam_bot,
                       BEAM_EDGE, 235, taper=0.30)
    surf.blit(frame, (0, 0))
    # Teal glow fill inside the frame.
    glow = _hard_beam(SIZE, cx, beam_top, 6, 9, beam_top, beam_bot,
                      BEAM_GLOW, 230, taper=0.40)
    surf.blit(glow, (0, 0))
    # SOLID near-white core column — the load-bearing tell. Kept narrow + tall
    # so ~6-8px of unambiguous bright beam survives below the disc rim at 1×.
    core = _hard_beam(SIZE, cx, beam_top, 3, 5, beam_top, beam_bot,
                      BEAM_CORE, 255, taper=0.35)
    surf.blit(core, (0, 0))

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
    # bouncing back up onto the saucer belly. It also snaps the disc off Pip's
    # red where the beam erupts beneath it.
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

    # ── BEAM CORE RE-EMIT (over the disc) ─────────────────────────────────────
    # The disc + its inflated keyline are drawn AFTER the beam and overpaint the
    # column's top rows down to ~y+2 past the rim, which crushed the surviving
    # beam to ~2px after smoothscale. Re-emit the SOLID core + teal frame just
    # below the lip, on TOP of the disc, so a full hard column erupts from the
    # rim and ~6-8px of unambiguous beam survives below the disc at 1× in both
    # biomes. The disc keyline still caps the apex visually a couple px up.
    re_top = disc_cy + disc_ry
    re_frame = _hard_beam(SIZE, cx, re_top, 7, 12, re_top, 44,
                          BEAM_EDGE, 235, taper=0.30)
    surf.blit(re_frame, (0, 0))
    re_glow = _hard_beam(SIZE, cx, re_top, 5, 9, re_top, 44,
                         BEAM_GLOW, 230, taper=0.40)
    surf.blit(re_glow, (0, 0))
    re_core = _hard_beam(SIZE, cx, re_top, 3, 5, re_top, 44,
                         BEAM_CORE, 255, taper=0.30)
    surf.blit(re_core, (0, 0))

    return pygame.transform.smoothscale(surf, (22, 22))
