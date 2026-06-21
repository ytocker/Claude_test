"""GENIE FLASK parcel cosmetic (HIGH tier).

A cut-sapphire genie flask: the JEWEL lives in the SILHOUETTE, not in
interior facet seams (which die below 22px). The body is an angular
briolette — flat angled SHOULDERS up top, straight tapering walls, and a
chiselled multi-faceted POINT at the base — so even as a flat fill the
outline reads "cut gem", never a round potion/gumball. A bold horizontal
GOLD COLLAR band rings the lower-visible half, double-edged with the dark
sapphire keyline so it separates from Pip's red body AND his gold goggles.
A small domed stopper crowns the top. Built at 2× (44px) then smoothscaled
to 22 so the angular outline and the gold band survive the tiny in-play
read and the bird's tilt rotation.

Carry context: Pip's red body occludes the TOP ~60%, so the design is
weighted LOW — the faceted point + gold band sit in the bottom ~40% that
actually clears Pip. The angular gem outline is what separates it from the
ROUND message-bottle sibling in a grayscale silhouette."""
import pygame

SIZE = 22
SS = 44  # 2× supersample; smoothscaled down for a crisp outline at 22px

# DAY palette — DEEP saturated sapphire so the gem out-values the day sky;
# a tight icy facet glint, a bold gold band, and a faint inner glow for night.
GLASS = (0x1E, 0x4F, 0xC0)       # deep saturated sapphire core
GLASS_HI = (0x4E, 0x86, 0xF0)    # lit sapphire wall (one facet plane)
GLASS_SH = (0x14, 0x33, 0x86)    # shaded sapphire wall (opposite plane)
GLINT = (0xDC, 0xEB, 0xFF)       # icy white facet glint — reserved + tight
COLLAR = (0xE8, 0xB2, 0x3C)      # gold collar band
COLLAR_HI = (0xFF, 0xDD, 0x88)   # gold sheen (top edge)
COLLAR_SH = (0xA8, 0x78, 0x1E)   # gold underside
GLOW = (0x9F, 0xC0, 0xFF)        # faint inner glow tint (night read)
OUTLINE = (0x0C, 0x1A, 0x44)     # near-black sapphire keyline


def _lerp(a, b, t):
    return (round(a[0] + (b[0] - a[0]) * t),
            round(a[1] + (b[1] - a[1]) * t),
            round(a[2] + (b[2] - a[2]) * t))


def build(mode="normal"):  # mode ignored — parcel is mode-agnostic, one surface
    s = pygame.Surface((SS, SS), pygame.SRCALPHA)
    cx = SS // 2

    # ---- Vertical layout, weighted LOW. The carry crop only clears the bottom
    # ~40%, so the gem's tell — angular point + gold band — lives below the
    # mid-line; the stopper crowns the top where Pip's body crops in.
    pt_y = 42            # the chiselled base POINT (lowest)
    waist_y = 28         # gold band sits here, high enough that the faceted
                         # point dominates the lower-visible carry half
    shoulder_y = 17      # flat angled shoulders — the top of the cut crown
    crown_y = 14         # narrow top facet where glass meets the collar neck
    body_hw = 13         # half-width at the widest (the shoulder line)
    waist_hw = 12        # half-width at the gold band
    stop_cy = 8          # round domed stopper centre

    # ---- ANGULAR briolette silhouette as one closed polygon. HARD flat
    # shoulders (the table/crown of the cut), straight tapering girdle walls,
    # then a deep faceted chevron POINT — a hard-edged gem outline, no curves.
    body_poly = [
        (cx,               crown_y),              # narrow top crown
        (cx + body_hw,     shoulder_y),            # hard right shoulder corner
        (cx + waist_hw,    waist_y - 2),           # right girdle into the band
        (cx + waist_hw,    waist_y + 2),           # right girdle below the band
        (cx + waist_hw - 6, pt_y - 7),             # right lower facet break
        (cx,               pt_y),                  # chiselled base point
        (cx - waist_hw + 6, pt_y - 7),             # left lower facet break
        (cx - waist_hw,    waist_y + 2),           # left girdle below the band
        (cx - waist_hw,    waist_y - 2),           # left girdle into the band
        (cx - body_hw,     shoulder_y),            # hard left shoulder corner
    ]

    # Dark keyline pass — fat silhouette first; the gem fill sits inside it.
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
    # planes so the base reads as a faceted cut, not a smooth taper. This lives
    # below the band where the carry crop keeps it.
    pygame.draw.line(s, _lerp(OUTLINE, GLASS, 0.45),
                     (cx, waist_y + 3), (cx, pt_y - 2), 1)
    pygame.draw.line(s, GLASS_HI,
                     (cx - waist_hw + 4, waist_y + 3), (cx, pt_y - 2), 1)
    pygame.draw.line(s, GLASS_SH,
                     (cx + waist_hw - 4, waist_y + 3), (cx, pt_y - 2), 1)

    # ---- BOLD GOLD COLLAR — a wide horizontal band across the lower-visible
    # half, ringed on BOTH edges with the dark keyline so it separates from
    # Pip's red body AND his gold goggles in the carry crop.
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

    # ---- Short NECK + domed STOPPER crowning the top (mostly under Pip, but it
    # crowns the gem on the hero/tilt rows). Kept compact and high.
    pygame.draw.rect(s, OUTLINE,
                     pygame.Rect(cx - 3, stop_cy + 3, 6, crown_y - stop_cy - 2),
                     border_radius=1)
    pygame.draw.rect(s, COLLAR,
                     pygame.Rect(cx - 2, stop_cy + 3, 4, crown_y - stop_cy - 2))
    stop_r = 4
    pygame.draw.circle(s, OUTLINE, (cx, stop_cy), stop_r + 1)
    pygame.draw.circle(s, COLLAR, (cx, stop_cy), stop_r)
    pygame.draw.circle(s, COLLAR_SH, (cx, stop_cy), stop_r, 1)
    pygame.draw.circle(s, COLLAR_HI, (cx - 1, stop_cy - 1), 1)

    # ---- Faint inner GLOW low in the gem so it still reads as lit on the dark
    # NIGHT sky — masked to the silhouette so it never blooms past the cut edge.
    glow = pygame.Surface((SS, SS), pygame.SRCALPHA)
    pygame.draw.circle(glow, GLOW + (70,), (cx, pt_y - 8), 6)
    pygame.draw.circle(glow, GLOW + (38,), (cx, pt_y - 8), 10)
    g_mask = pygame.Surface((SS, SS), pygame.SRCALPHA)
    pygame.draw.polygon(g_mask, (255, 255, 255, 255), body_poly)
    glow.blit(g_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    s.blit(glow, (0, 0))

    return pygame.transform.smoothscale(s, (SIZE, SIZE))
