"""GENIE FLASK parcel cosmetic (HIGH tier).

A cut-sapphire genie flask: the JEWEL lives in the SILHOUETTE, not in
interior facet seams (which die below 22px). The body is an angular
briolette — flat angled SHOULDERS up top, straight tapering walls, and a
chiselled multi-faceted POINT at the base — so even as a flat fill the
outline reads "cut gem", never a round potion/gumball. A bold horizontal
GOLD COLLAR band rings the lower-visible half, double-edged with the dark
sapphire keyline so it separates from Pip's body AND his gold foot. A small
domed stopper crowns the top, divided from the body by a dark neck NOTCH so
the silhouette has a readable waist. Built at 2× (44px) then smoothscaled
to 22 so the angular outline and the gold band survive the tiny in-play
read and the bird's tilt rotation.

Carry context: Pip occludes the TOP of the parcel and his BLUE belly/wing +
GOLD foot sit right against it, so two things fight camouflage. The whole
gem is shifted OUTBOARD (down-left of sprite centre) to clear his foot, and
a dark CONTACT RIM is stamped around the silhouette so the flask reads as a
held object with a gap, not fused to Pip. The body hue is pushed off Pip's
royal blue toward a deeper VIOLET-sapphire so the wall doesn't melt into his
belly — most critical at night, where the old blue vanished into him."""
import pygame

SIZE = 22
SS = 44  # 2× supersample; smoothscaled down for a crisp outline at 22px

# DAY palette — the wall hue is pushed off Pip's royal blue (40,100,255)
# toward a deeper VIOLET-sapphire so the gem doesn't camouflage against his
# belly/wing; even the LIT plane stays darker + more purple than his blue.
GLASS = (0x2A, 0x2C, 0xA8)       # deep violet-sapphire core (off Pip's blue)
GLASS_HI = (0x52, 0x4C, 0xD6)    # lit wall plane — violet, still < Pip's value
GLASS_SH = (0x16, 0x16, 0x6E)    # shaded wall plane (opposite facet)
GLINT = (0xE6, 0xE2, 0xFF)       # icy facet glint — reserved + tight
COLLAR = (0xE8, 0xB2, 0x3C)      # gold collar band
COLLAR_HI = (0xFF, 0xDD, 0x88)   # gold sheen (top edge)
COLLAR_SH = (0xA8, 0x78, 0x1E)   # gold underside
GLOW = (0xB0, 0xA8, 0xFF)        # faint inner glow tint (night read), violet
OUTLINE = (0x0A, 0x0A, 0x30)     # near-black violet keyline
RIM = (0x05, 0x05, 0x18)         # darker contact-shadow rim vs Pip's body


def _lerp(a, b, t):
    return (round(a[0] + (b[0] - a[0]) * t),
            round(a[1] + (b[1] - a[1]) * t),
            round(a[2] + (b[2] - a[2]) * t))


def build(mode="normal"):  # mode ignored — parcel is mode-agnostic, one surface
    s = pygame.Surface((SS, SS), pygame.SRCALPHA)
    # Carry point shifted OUTBOARD: the whole gem sits down-LEFT of centre so
    # it clears Pip's foot/belly and reads as a held object, not fused to him.
    cx = SS // 2 - 3
    dy = 3               # nudge the whole gem lower so the point clears Pip

    # ---- Vertical layout, weighted LOW. The carry crop only clears the bottom
    # ~40%, so the gem's tell — angular point + gold band — lives below the
    # mid-line; the stopper crowns the top where Pip's body crops in.
    pt_y = 42 + dy           # the chiselled base POINT (lowest, sharp apex)
    waist_y = 30 + dy        # gold band pulled DOWN into the bottom slice that
                             # actually clears Pip's foot, so a clean ring of
                             # gold (not just violet) is the thing that pokes out
    shoulder_y = 16 + dy     # flat angled shoulders — the top of the cut crown
    crown_y = 13 + dy        # narrow top facet where glass meets the collar neck
    body_hw = 13             # half-width at the widest (the shoulder line)
    waist_hw = 12            # half-width at the gold band
    stop_cy = 6 + dy         # round domed stopper centre

    # ---- ANGULAR briolette silhouette as one closed polygon. HARD flat
    # shoulders (the table/crown of the cut), straight tapering girdle walls,
    # then a deep faceted chevron POINT ending in a single-pixel APEX so it
    # stays an angular gem under 45°/steep tilt instead of a rounded blob.
    body_poly = [
        (cx,               crown_y),              # narrow top crown
        (cx + body_hw,     shoulder_y),            # hard right shoulder corner
        (cx + waist_hw,    waist_y - 2),           # right girdle into the band
        (cx + waist_hw,    waist_y + 2),           # right girdle below the band
        (cx + waist_hw - 6, pt_y - 8),             # right lower facet break
        (cx + 1,           pt_y - 1),              # right side of the hard apex
        (cx,               pt_y),                  # single-pixel chevron APEX
        (cx - 1,           pt_y - 1),              # left side of the hard apex
        (cx - waist_hw + 6, pt_y - 8),             # left lower facet break
        (cx - waist_hw,    waist_y + 2),           # left girdle below the band
        (cx - waist_hw,    waist_y - 2),           # left girdle into the band
        (cx - body_hw,     shoulder_y),            # hard left shoulder corner
    ]

    # ---- CONTACT RIM — a dark halo stamped UNDER the silhouette on ALL sides
    # (fattest toward the lower-left where the flask meets Pip), so a thin dark
    # gap rings the held object and it never fuses with his blue belly / foot
    # or melts into the night sky.
    rim = pygame.Surface((SS, SS), pygame.SRCALPHA)
    for ox, oy in ((-2, 1), (-1, 1), (0, 1), (1, 1), (-1, 0), (1, 0),
                   (0, -1), (-1, 2), (-1, -1), (1, -1)):
        poly = [(x + ox, y + oy) for x, y in body_poly]
        pygame.draw.polygon(rim, RIM + (255,), poly)
    s.blit(rim, (0, 0))

    # Dark keyline pass — fat silhouette over the rim; the gem fill sits inside.
    pygame.draw.polygon(s, OUTLINE, body_poly)

    # ---- Faceted FILL by VALUE PLANES, not seam lines. A bright-lit left half
    # and a shaded right half split down the spine fake a two-plane cut so the
    # gem reads dimensional even when interior detail washes out.
    fill = pygame.Surface((SS, SS), pygame.SRCALPHA)
    pygame.draw.polygon(fill, (255, 255, 255, 255), body_poly)
    gem = pygame.Surface((SS, SS), pygame.SRCALPHA)
    left = cx - body_hw
    for x in range(left, cx + body_hw + 1):
        t = (x - left) / (2 * body_hw)
        if t < 0.42:                       # lit left plane → deep core
            col = _lerp(GLASS_HI, GLASS, t / 0.42)
        elif t < 0.58:                     # deep central spine
            col = GLASS
        else:                              # shaded right plane
            col = _lerp(GLASS, GLASS_SH, (t - 0.58) / 0.42)
        gem.fill(col + (255,), pygame.Rect(x, 0, 1, SS))
    gem.blit(fill, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    s.blit(gem, (0, 0))

    # ---- BRIGHT BEVEL on the upper-left silhouette edge. Where the flask meets
    # Pip's dark wing, a near-black contact rim alone vanishes into his shadow;
    # a 1px lit-glass bevel along the left shoulder/girdle gives a value JUMP
    # there so the gem edge separates from him whether his side is light or dark.
    bevel = _lerp(GLASS_HI, GLINT, 0.35)
    pygame.draw.line(s, bevel, (cx - body_hw + 1, shoulder_y + 1),
                     (cx - waist_hw + 1, waist_y - 4), 1)
    pygame.draw.line(s, bevel, (cx - body_hw + 1, shoulder_y + 1),
                     (cx - 1, crown_y + 1), 1)

    # ---- ONE tight angular GLINT — a sharp icy wedge on the upper-left facet,
    # the wet-cut-gem tell. A short bright triangle, not a soft blob.
    glint = [
        (cx - 5, shoulder_y + 3),
        (cx - 1, shoulder_y + 4),
        (cx - 4, waist_y - 4),
        (cx - 7, waist_y - 6),
    ]
    pygame.draw.polygon(s, GLINT, glint)
    pygame.draw.line(s, (255, 255, 255), (cx - 5, shoulder_y + 3),
                     (cx - 6, waist_y - 7), 1)

    # ---- Chiselled POINT facets in the LOWER-visible half. A central spine +
    # two angular seams split the point into bright-left / dark-right chevron
    # planes that converge on the single-pixel apex, so the base reads as a
    # faceted cut, not a smooth taper. This lives below the band where the
    # carry crop keeps it.
    pygame.draw.line(s, _lerp(OUTLINE, GLASS, 0.45),
                     (cx, waist_y + 3), (cx, pt_y - 1), 1)
    pygame.draw.line(s, GLASS_HI,
                     (cx - waist_hw + 4, waist_y + 3), (cx, pt_y - 1), 1)
    pygame.draw.line(s, GLASS_SH,
                     (cx + waist_hw - 4, waist_y + 3), (cx, pt_y - 1), 1)

    # ---- BOLD GOLD COLLAR — a wide horizontal band across the lower-visible
    # half, ringed on BOTH edges with the dark keyline so it separates from
    # Pip's body AND his gold foot in the carry crop.
    band_h = 6
    band_top = waist_y - band_h // 2
    bx_l = cx - waist_hw - 1
    bx_r = cx + waist_hw + 1
    # Dark keyline above + below the band (the both-edge ring).
    band_bg = pygame.Rect(bx_l - 1, band_top - 2, (bx_r - bx_l) + 2, band_h + 4)
    pygame.draw.rect(s, OUTLINE, band_bg, border_radius=2)
    # Gold band proper, lit top → shaded bottom for a metal sheen.
    for i in range(band_h):
        t = i / max(1, band_h - 1)
        c = _lerp(COLLAR_HI, COLLAR_SH, t) if t < 0.6 else _lerp(COLLAR, COLLAR_SH, t)
        pygame.draw.line(s, c, (bx_l, band_top + i), (bx_r, band_top + i))
    # Bright top sheen line + a couple of stud highlights so it reads as metal.
    pygame.draw.line(s, COLLAR_HI, (bx_l + 1, band_top),
                     (bx_r - 1, band_top), 1)
    for sx in (cx - 6, cx, cx + 6):
        pygame.draw.circle(s, COLLAR_HI, (sx, band_top + 1), 1)

    # ---- Short NECK + domed STOPPER crowning the top, divided by a dark NECK
    # NOTCH so the stopper doesn't merge with the collar into one gold lump —
    # the notch gives the silhouette a readable waist.
    neck_top = stop_cy + 3
    neck_bot = crown_y - 1
    pygame.draw.rect(s, OUTLINE,
                     pygame.Rect(cx - 3, neck_top, 6, neck_bot - neck_top),
                     border_radius=1)
    pygame.draw.rect(s, COLLAR,
                     pygame.Rect(cx - 2, neck_top, 4, neck_bot - neck_top))
    # Dark NOTCH ring just under the stopper, separating gold stopper from neck.
    pygame.draw.line(s, RIM, (cx - 3, neck_top), (cx + 3, neck_top), 2)
    stop_r = 4
    pygame.draw.circle(s, OUTLINE, (cx, stop_cy), stop_r + 1)
    pygame.draw.circle(s, COLLAR, (cx, stop_cy), stop_r)
    pygame.draw.circle(s, COLLAR_SH, (cx, stop_cy), stop_r, 1)
    pygame.draw.circle(s, COLLAR_HI, (cx - 1, stop_cy - 1), 1)

    # ---- Faint inner GLOW low in the gem so it still reads as lit on the dark
    # NIGHT sky — masked to the silhouette so it never blooms past the cut edge.
    glow = pygame.Surface((SS, SS), pygame.SRCALPHA)
    pygame.draw.circle(glow, GLOW + (70,), (cx, pt_y - 9), 6)
    pygame.draw.circle(glow, GLOW + (38,), (cx, pt_y - 9), 10)
    g_mask = pygame.Surface((SS, SS), pygame.SRCALPHA)
    pygame.draw.polygon(g_mask, (255, 255, 255, 255), body_poly)
    glow.blit(g_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    s.blit(glow, (0, 0))

    return pygame.transform.smoothscale(s, (SIZE, SIZE))
