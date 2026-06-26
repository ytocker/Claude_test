"""GAME COIN — the gold coin Pip collects in-game, carried below him as the gift.

The whole point of this parcel is recognition: it must read as THE coin, not a
generic gold disc. So it borrows the in-game coin's exact identity — the
COIN_GOLD/COIN_DARK palette, a darker rim ring, an embossed "$" face glyph, and
a hard upper-left specular pinprick that says shiny metal — and bakes that into
a fat round disc held below Pip.

22px read tradeoffs (WHY): the in-game coin's twisted-rope rim and parrot
emboss turn to mud at true size below Pip, so identity is rebuilt from the three
masses that actually survive the downscale — a bold gold disc, a deep rim ring,
and a single bright "$" glyph — plus one hot specular dot. Gold is engineered to
read as METAL through VALUE, not hue: a near-white sheen crescent up top, a
mid-gold body, and a deep-amber rim crescent at the bottom give a wide
light->dark sweep so the disc still reads as a lit metal sphere in grayscale
instead of a flat token. A baked dark outline (inflated, drawn first) carries
the circle on bright DAY sky; a warm amber keyline rim inside is the NIGHT
lifeline; the disc is held off the surface edges so nothing clips under the
gameplay rotozoom as Pip banks.
"""
import pygame

# In-game coin palette (game.config / game.draw) so the parcel reads as the
# exact coin, plus value-spread tones engineered so the gold survives grayscale:
# a near-white sheen tops everything, a deep-amber rim bottoms it, the body sits
# between — a wide luminance sweep that reads as lit metal, not a flat disc.
COIN_GOLD  = (255, 210,  20)   # in-game body gold
COIN_DARK  = (200, 140,   0)   # in-game rim
GOLD_HI    = (255, 244, 150)   # bright upper sheen crescent (lit metal top)
GOLD_LO    = (170, 110,  10)   # lower body shade (volume into the rim)
RIM_DK     = (120,  72,   0)   # deep rim ring — the value floor, sells metal
RIM_LT     = (236, 188,  60)   # warm rim highlight on the lit upper arc
SHEEN      = (255, 252, 224)   # near-white specular pinprick (the brightest px)
GLYPH      = (150,  92,   0)   # embossed "$" shade — reads as struck into metal
GLYPH_HI   = (255, 240, 140)   # glyph lit edge so the "$" has cut depth
OUTLINE    = ( 70,  40,   0)   # dark, drawn first — the DAY read on bright sky
KEYLINE    = (255, 214, 120)   # warm amber rim — the NIGHT lifeline


def build(mode="normal") -> pygame.Surface:
    # Mode-agnostic: one static coin sprite for every Pip skin.
    S = 44
    surf = pygame.Surface((S, S), pygame.SRCALPHA)
    cx = cy = S // 2

    R = 17                         # fat disc, held off the edges for the rotozoom

    # --- Baked dark outline (drawn first, inflated) — the DAY read on bright sky.
    pygame.draw.circle(surf, OUTLINE, (cx, cy), R + 2)

    # --- Deep rim ring: the value floor that makes the gold read as struck metal.
    pygame.draw.circle(surf, RIM_DK, (cx, cy), R)

    # --- Coin body as a vertical gold gradient masked to the inner disc, so the
    # face is a lit sphere (bright sheen top -> mid gold -> dark bottom) and the
    # metal read survives grayscale. Inner radius leaves the rim ring exposed.
    r_body = R - 3
    body = pygame.Surface((S, S), pygame.SRCALPHA)
    y0, y1 = cy - r_body, cy + r_body
    for yy in range(y0, y1 + 1):
        t = (yy - y0) / max(1, (y1 - y0))
        if t < 0.45:
            u = t / 0.45
            col = (int(GOLD_HI[0] + (COIN_GOLD[0] - GOLD_HI[0]) * u),
                   int(GOLD_HI[1] + (COIN_GOLD[1] - GOLD_HI[1]) * u),
                   int(GOLD_HI[2] + (COIN_GOLD[2] - GOLD_HI[2]) * u))
        else:
            u = (t - 0.45) / 0.55
            col = (int(COIN_GOLD[0] + (GOLD_LO[0] - COIN_GOLD[0]) * u),
                   int(COIN_GOLD[1] + (GOLD_LO[1] - COIN_GOLD[1]) * u),
                   int(COIN_GOLD[2] + (GOLD_LO[2] - COIN_GOLD[2]) * u))
        pygame.draw.line(body, col, (0, yy), (S, yy))
    mask = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (cx, cy), r_body)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(body, (0, 0))

    # --- Rim highlight on the lit upper-left arc so the rim ring catches light
    # like real metal rather than reading as a flat dark band all the way round.
    rim_arc = pygame.Rect(cx - R + 1, cy - R + 1, (R - 1) * 2, (R - 1) * 2)
    pygame.draw.arc(surf, RIM_LT, rim_arc, 0.6, 2.7, 2)

    # --- Embossed "$": the glyph that names this as THE coin. The two S bowls
    # must separate from the stem to read as a "$" at true size, so the stem is
    # kept narrow and the S is built from two wide arcs whose openings face
    # opposite sides (upper-left, lower-right) and sit just clear of the stem.
    # Drawn as a dark emboss with an offset lit edge so it reads struck INTO the
    # metal. The stem overshoots the bowls top and bottom — the classic "$" tick.
    def stamp(dx, dy, color):
        w = 3
        # Vertical stem, overshooting the bowls (the "$" tick).
        pygame.draw.line(surf, color, (cx + dx, cy - 9 + dy),
                         (cx + dx, cy + 9 + dy), w)
        # Upper bowl — a C opening to the LOWER-LEFT.
        pygame.draw.arc(surf, color,
                        pygame.Rect(cx - 5 + dx, cy - 8 + dy, 11, 9),
                        -0.5, 2.9, w)
        # Lower bowl — a C opening to the UPPER-RIGHT (mirror), making the S.
        pygame.draw.arc(surf, color,
                        pygame.Rect(cx - 6 + dx, cy - 1 + dy, 11, 9),
                        2.6, 6.0, w)

    stamp(1, 1, GLYPH_HI)          # lit edge, offset down-right (catches light)
    stamp(0, 0, GLYPH)             # dark emboss on top so the "$" has cut depth

    # --- Warm amber keyline rim INSIDE the outline — the NIGHT lifeline glowing
    # on dark sky while staying subtle on day. Traces the disc rim.
    pygame.draw.circle(surf, KEYLINE, (cx, cy), R, 1)

    # --- Hard specular pinprick upper-left: the single brightest pixel cluster,
    # the cue that instantly says "shiny gold metal" even at true size.
    pygame.draw.circle(surf, SHEEN, (cx - 6, cy - 7), 3)
    pygame.draw.circle(surf, (255, 255, 255), (cx - 6, cy - 7), 1)

    return pygame.transform.smoothscale(surf, (22, 22))
