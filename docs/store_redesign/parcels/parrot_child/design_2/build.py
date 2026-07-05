"""DOWNY CHICK — a round, max-cute baby-parrot parcel carried below Pip.

The identity is CHIBI PROPORTION: an oversized round head sitting on a tiny body,
crowned by a wispy 3-strand head TUFT. That silhouette — a big circle, a small
circle, and three little antenna-like strands above — is what makes this read as
a freshly-downy baby rather than a tiny adult, and it's the single thing that has
to survive the gameplay rotozoom. So everything is built as bold, legible masses:
two stacked discs for head+body, one big sparkly eye, stubby half-formed wing
nubs, and a paler downy belly. Pip's own palette (red body, blue wing, yellow
beak/tuft tips) is reused so the chick reads unmistakably as his offspring.

22px read tradeoffs (WHY): at true size fine fluff texture turns to mud, so
"downiness" is sold by SHAPE and VALUE instead — a slightly fuzzed-out body
silhouette, a broad pale belly crescent, and a soft top-of-head highlight, not
per-feather strokes. The eye is pushed deliberately large and high-contrast (dark
iris + a bright catch-light) because at 22px a single big eye is the whole face;
two small eyes would collapse to noise. The 3 tuft strands are drawn THICK with
yellow tips and pulled toward centre so the rotozoom never clips them and they
stay three distinct ticks rather than fusing into a blob. A baked dark outline
(inflated, drawn first) carries the round head/body on bright DAY sky; a warm
keyline rim inside is the NIGHT lifeline; all extremities are held off the surface
edges so the tuft and wing nubs never clip at extreme bank.
"""
import pygame

# Pip's own family palette so the chick reads as his offspring, plus a softer,
# downier set of body tones. Value is engineered so identity survives grayscale:
# the belly fluff is the brightest body mass, the eye the darkest point, and the
# tuft tips a bright spark above the head.
RED      = (240,  55,  55)     # Pip red — chick body/head base
RED_D    = (170,  25,  25)     # Pip dark red — lower shade crescent
RED_HI   = (255, 120, 120)     # soft downy highlight on the crown
BELLY    = (255, 195, 130)     # paler downy belly fluff (lifted from BIRD_BELLY)
BELLY_HI = (255, 224, 186)     # near-white belly crest — brightest body pixel
WING     = ( 40, 100, 255)     # Pip wing blue — stubby half-formed wing nub
WING_HI  = (150, 195, 255)     # wing nub rim light
TUFT     = (240,  55,  55)     # tuft strands start as body red...
TUFT_TIP = (255, 200,  40)     # ...and end in Pip's yellow accent (the spark)
BEAK     = (255, 185,   0)     # Pip beak yellow
BEAK_D   = (200, 130,   0)     # beak shade
EYE      = ( 26,  16,  20)     # near-black iris — the darkest point / focal cue
EYE_HI   = (255, 255, 255)     # catch-light sparkle
OUTLINE  = ( 40,  16,  18)     # dark, fairly high-value: reads on bright day sky
KEYLINE  = (255, 198, 150)     # warm down rim — the NIGHT lifeline


def build(mode="normal") -> pygame.Surface:
    # Mode-agnostic: one static chick sprite for every Pip skin so the baby keeps
    # its own look across power-ups.
    S = 44
    surf = pygame.Surface((S, S), pygame.SRCALPHA)
    cx = S // 2

    # Chibi geometry: a big HEAD disc over a smaller BODY disc, both biased low on
    # the surface so the tuft has clear air above and nothing clips under rotation.
    head_r = 12
    head_cx, head_cy = cx, 22
    body_r = 9
    body_cx, body_cy = cx, 34

    # --- 3-STRAND TUFT (drawn first so the head disc overlaps its roots, seating
    # the strands INTO the crown). Thick strokes, pulled toward centre, each tipped
    # in Pip-yellow so three distinct ticks survive the downscale.
    tuft_base = head_cy - head_r + 4
    strands = (
        ((head_cx - 5, tuft_base), (head_cx - 8, tuft_base - 11)),  # left lean
        ((head_cx,     tuft_base), (head_cx,     tuft_base - 14)),  # centre tall
        ((head_cx + 5, tuft_base), (head_cx + 8, tuft_base - 11)),  # right lean
    )
    for bot, top in strands:
        pygame.draw.line(surf, OUTLINE, bot, top, 5)              # baked outline
    for bot, top in strands:
        pygame.draw.line(surf, TUFT, bot, top, 3)
        pygame.draw.circle(surf, OUTLINE, top, 3)                # tip outline
        pygame.draw.circle(surf, TUFT_TIP, top, 2)               # the yellow spark

    # --- BODY disc (behind/below head). Baked outline, base fill, dark lower
    # crescent for volume, then a broad pale belly so the downy chest is the
    # brightest body mass — the grayscale value anchor.
    pygame.draw.circle(surf, OUTLINE, (body_cx, body_cy), body_r + 2)
    pygame.draw.circle(surf, RED, (body_cx, body_cy), body_r)
    _crescent(surf, S, RED_D, (body_cx + 3, body_cy + 4), body_cx, body_cy, body_r)
    # Belly fluff: a pale crescent low-front on the body, plus a near-white crest.
    pygame.draw.circle(surf, BELLY, (body_cx - 1, body_cy + 3), 6)
    pygame.draw.circle(surf, BELLY_HI, (body_cx - 1, body_cy + 4), 3)

    # --- WING NUBS: two stubby half-formed wing nubs flanking the body. Kept tiny
    # and rounded (a baby's wings aren't grown in) and pulled inward so they never
    # clip at extreme bank.
    for sx in (-1, 1):
        nub = (body_cx + sx * (body_r + 1), body_cy + 1)
        pygame.draw.circle(surf, OUTLINE, nub, 4)
        pygame.draw.circle(surf, WING, nub, 3)
        pygame.draw.circle(surf, WING_HI, (nub[0] - sx, nub[1] - 1), 1)

    # --- HEAD disc (drawn over body + wing roots so it sits forward). Same volume
    # recipe: outline, base, lower shade crescent, soft crown highlight.
    pygame.draw.circle(surf, OUTLINE, (head_cx, head_cy), head_r + 2)
    pygame.draw.circle(surf, RED, (head_cx, head_cy), head_r)
    _crescent(surf, S, RED_D, (head_cx + 4, head_cy + 5), head_cx, head_cy, head_r)
    # Soft downy crown highlight (broad, upper-left) so the big head reads round.
    pygame.draw.circle(surf, RED_HI, (head_cx - 4, head_cy - 5), 5)

    # --- ONE BIG EYE: the whole face at 22px. Large pale ring, dark iris low-set
    # so the chick looks up toward its parent, plus a bright catch-light sparkle.
    eye_c = (head_cx + 1, head_cy - 1)
    pygame.draw.circle(surf, (255, 250, 246), eye_c, 5)
    pygame.draw.circle(surf, OUTLINE, eye_c, 5, 1)
    pygame.draw.circle(surf, EYE, (eye_c[0] + 1, eye_c[1] + 1), 3)
    pygame.draw.circle(surf, EYE_HI, (eye_c[0] - 1, eye_c[1] - 1), 2)
    pygame.draw.circle(surf, (190, 210, 255), (eye_c[0] + 2, eye_c[1] + 2), 1)

    # --- BEAK: a small soft baby beak under the eye, Pip-yellow with a shade line.
    beak_y = head_cy + 5
    beak_pts = [
        (head_cx - 3, beak_y),
        (head_cx + 4, beak_y),
        (head_cx, beak_y + 4),
    ]
    pygame.draw.polygon(surf, OUTLINE, [
        (head_cx - 4, beak_y - 1), (head_cx + 5, beak_y - 1),
        (head_cx, beak_y + 5)])
    pygame.draw.polygon(surf, BEAK, beak_pts)
    pygame.draw.line(surf, BEAK_D, (head_cx - 2, beak_y + 1),
                     (head_cx + 3, beak_y + 1), 1)

    # --- Warm down keyline rims INSIDE the outlines — the NIGHT lifeline tracing
    # the two chibi discs so the big-head/tiny-body read glows on dark sky.
    pygame.draw.circle(surf, KEYLINE, (head_cx, head_cy), head_r, 1)
    pygame.draw.circle(surf, KEYLINE, (body_cx, body_cy), body_r, 1)

    return pygame.transform.smoothscale(surf, (22, 22))


def _crescent(surf, S, color, off_center, cx, cy, r):
    """A lower shade crescent clipped to a disc — gives a flat circle volume
    without a second full fill swallowing the base tone."""
    shade = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.circle(shade, color, off_center, r)
    mask = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (cx, cy), r)
    shade.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(shade, (0, 0))
