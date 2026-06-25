"""COCONUT DRINK — tropical-lagoon refresher parcel cosmetic.

A round brown COCONUT cracked open at the top, with a striped STRAW poking up
and a tiny cocktail UMBRELLA — the two beats that say "drink" rather than just
"ball". The identity is the contrast of three masses: a dark spherical coconut,
a pale cut-flesh cap where it's opened, and the bright straw+umbrella crown
rising out of it. No other parcel is a round tropical vessel, so the circle plus
the umbrella silhouette carries the read before colour even resolves.

22px read tradeoffs (WHY): at true size the coconut is reduced to ONE bold
filled circle with a single shading crescent — micro fibre texture just turns to
mud, so the volume is sold by a dark lower-shade arc and a small top highlight
instead. The cut-open top is a flat pale ellipse seated ON the sphere so the
"opened" read survives the downscale without a fussy rim. The straw is held
2px-thick with two hard red bands (a striped diagonal collapses at 22px) and is
tilted so it stays a distinct stroke against the umbrella rather than fusing into
it. The umbrella is a small flat fan of two pink tones with a centre pole — kept
compact and pulled toward centre so the gameplay rotozoom never clips it as the
crown swings out across Pip's bank arc. A baked dark outline (inflated, drawn
first) carries the round shape on bright DAY sky; a warm sand keyline rim inside
is the NIGHT lifeline; everything is held off the surface edges so the straw and
umbrella never clip under rotation.
"""
import pygame

# Tight tropical palette: a deep coconut brown with a darker shade for the
# sphere's lower crescent, pale flesh for the cut-open top, a saturated red straw
# (the grayscale-safe anchor against the brown), two pinks for the umbrella fan,
# a green leaf sprig, a dark outline for day, and a warm sand keyline for night.
COCO = (122,  79,  46)        # coconut husk brown (mid body)
COCO_SHADE = ( 86,  52,  24)  # darker lower crescent — gives the sphere volume
COCO_HI = (158, 112,  72)     # small upper highlight on the husk
FLESH = (240, 230, 210)       # pale cut-open top (the "opened" cue)
FLESH_SHADE = (214, 198, 170) # flesh rim shadow so the cut reads as a hollow
STRAW = (224,  72,  62)       # red striped straw — the eye-magnet
STRAW_HI = (246, 158, 150)    # straw band highlight
UMB_A = (240, 143, 176)       # umbrella pink (lit side)
UMB_B = (214,  96, 138)       # umbrella pink (shade side) — fan separation
LEAF = ( 63, 163,  90)        # green leaf sprig
OUTLINE = ( 42,  26,  14)     # dark, high-value: reads on bright day sky
KEYLINE = (236, 206, 160)     # warm sand rim — the NIGHT lifeline


def build(mode="normal") -> pygame.Surface:
    # Mode-agnostic: one static coconut sprite for every Pip skin.
    S = 44
    surf = pygame.Surface((S, S), pygame.SRCALPHA)
    cx = S // 2

    # Coconut sphere geometry. A big bold circle held low on the surface so the
    # straw + umbrella crown has room above without clipping the surface edge
    # under the gameplay rotozoom.
    R = 13                        # coconut radius
    ccy = 27                      # coconut centre y (biased low)
    ccx = cx

    # The cut-open top: a flat pale ellipse seated on the upper sphere. Its line
    # is where the straw + umbrella emerge.
    cut_w, cut_h = 18, 6
    cut_cy = ccy - 8
    cut_rect = pygame.Rect(ccx - cut_w // 2, cut_cy - cut_h // 2, cut_w, cut_h)

    # --- Baked dark outline (drawn first, slightly inflated) for the DAY read.
    pygame.draw.circle(surf, OUTLINE, (ccx, ccy), R + 2)

    # --- Coconut husk body: filled circle, then a darker lower crescent and a
    # small upper highlight so it reads as a sphere, not a flat disc.
    pygame.draw.circle(surf, COCO, (ccx, ccy), R)
    # Lower-right shade crescent: a shifted darker circle clipped to the husk.
    shade = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.circle(shade, COCO_SHADE, (ccx + 3, ccy + 4), R)
    mask = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (ccx, ccy), R)
    shade.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(shade, (0, 0))
    # Upper-left highlight to lift the lit side of the husk.
    pygame.draw.circle(surf, COCO_HI, (ccx - 4, ccy - 3), 4)

    # --- Cut-open pale top: outline ellipse, flesh fill, and a shadow rim so the
    # opening reads as a hollow the straw drinks from.
    pygame.draw.ellipse(surf, OUTLINE, cut_rect.inflate(3, 3))
    pygame.draw.ellipse(surf, FLESH, cut_rect)
    # A thin lower-rim shadow inside the flesh so it reads concave, not domed.
    inner = cut_rect.inflate(-4, -2)
    pygame.draw.arc(surf, FLESH_SHADE, inner, 3.5, 6.0, 2)

    # --- STRAW: a tilted bright stroke rising from the flesh. Held 2px wide with
    # two hard bands so the "drink" read survives the downscale; tilted away from
    # the umbrella so the two crown elements stay separable.
    straw_bot = (ccx + 3, cut_cy)
    straw_top = (ccx + 9, cut_cy - 15)
    pygame.draw.line(surf, OUTLINE, straw_bot, straw_top, 5)   # baked outline
    pygame.draw.line(surf, STRAW, straw_bot, straw_top, 3)
    # Two highlight bands across the straw (the "striped" cue, simplified).
    pygame.draw.line(surf, STRAW_HI, (ccx + 4, cut_cy - 4),
                     (ccx + 6, cut_cy - 7), 2)
    pygame.draw.line(surf, STRAW_HI, (ccx + 7, cut_cy - 10),
                     (ccx + 8, cut_cy - 13), 2)

    # --- LEAF sprig: a small green wedge tucked at the back-left of the opening,
    # the tropical garnish that fills the dead space opposite the umbrella.
    pygame.draw.polygon(surf, OUTLINE, [
        (ccx - 6, cut_cy - 1), (ccx - 12, cut_cy - 6), (ccx - 7, cut_cy - 7)])
    pygame.draw.polygon(surf, LEAF, [
        (ccx - 6, cut_cy - 2), (ccx - 11, cut_cy - 6), (ccx - 7, cut_cy - 6)])

    # --- UMBRELLA: a compact flat fan of two pinks on a short pole, pulled toward
    # centre so the rotozoom never clips it. The pole grounds it into the flesh;
    # the two-tone fan gives parasol separation at a glance.
    fan_y = cut_cy - 9                 # the umbrella's brim line
    apex = (ccx - 5, cut_cy - 13)      # parasol tip, above and left of the cut
    pole_bot = (ccx - 3, cut_cy - 1)
    pygame.draw.line(surf, OUTLINE, pole_bot, apex, 3)         # baked outline
    pygame.draw.line(surf, COCO_SHADE, pole_bot, apex, 1)
    # Fan: a symmetric outlined triangle split into a lit and a shade half so it
    # reads as a parasol, not a flat shard, at true size.
    left = (apex[0] - 6, fan_y)
    right = (apex[0] + 6, fan_y)
    apex_pt = (apex[0], apex[1] + 1)
    pygame.draw.polygon(surf, OUTLINE, [
        (apex[0], apex[1] - 1), (left[0] - 1, fan_y + 1),
        (right[0] + 1, fan_y + 1)])
    pygame.draw.polygon(surf, UMB_A, [apex_pt, left, (apex[0], fan_y)])
    pygame.draw.polygon(surf, UMB_B, [apex_pt, (apex[0], fan_y), right])
    # A scalloped brim shadow + a topknot so the parasol reads finished.
    pygame.draw.line(surf, UMB_B, (left[0], fan_y), (right[0], fan_y), 1)
    pygame.draw.circle(surf, STRAW, (apex[0], apex[1] - 1), 1)

    # --- Warm sand keyline rim INSIDE the outline — the NIGHT lifeline that glows
    # on dark sky while staying subtle on day. Traces the coconut sphere.
    pygame.draw.circle(surf, KEYLINE, (ccx, ccy), R, 1)

    return pygame.transform.smoothscale(surf, (22, 22))
