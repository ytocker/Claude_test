"""SLEEPY BABY — Pip's napping chick, curled below him as a parcel cosmetic.

The baby reads as Pip's offspring (same scarlet body / royal-blue wing / gold
beak family) but in a CALM SLEEPING pose no other concept shares: a round ball
of red feather curled into itself, the blue wing folded over its back like a
blanket, eyes CLOSED (a soft downward lash curve, not a dot), beak tucked into
the breast, and a small "z z" sleep mark rising. Those three beats — the closed
lash line, the blanket-wing, and the z's — are the identity, so they're the
masses tuned to survive the 22px downscale and the gameplay rotozoom.

22px read tradeoffs (WHY): at true size the chick collapses to ONE bold red
oval, so volume is sold by a single lower shade crescent + an upper-left
highlight rather than feather detail. The folded wing is a flat blue arc lobe
laid across the upper back (the "blanket"), kept as a bold value step against
the red so it survives grayscale. The closed eye is a 2px-thick dark curved
lash — a filled eye would read AWAKE and kill the sleep, so the curve is the
non-negotiable. The beak is a tiny gold wedge tucked low so it never becomes a
second eye. The z's are pulled IN from the top-right corner and held inside the
work surface so the rotozoom never clips them; they're the lightest mark on the
sprite so they read on DAY yet are keylined for NIGHT. A baked dark outline
(inflated, first) carries the round body on bright sky; a warm keyline rim
inside is the NIGHT lifeline.
"""
import pygame

# Pip's own family palette (from game.draw) so the chick reads as his kin,
# softened a touch for a downy baby. Identity rides on VALUE as well as hue:
# the body is a wide light->dark red so it never flattens to one disc, and the
# blanket-wing is engineered DARKER than the body for a hard grayscale step.
BODY      = (240,  78,  72)   # softened scarlet (Pip BIRD_RED, warmed/lighter)
BODY_HI   = (255, 138, 124)   # upper-left downy highlight — lifts the volume
BODY_SH   = (176,  34,  40)   # lower shade crescent (toward Pip BIRD_RED_D)
WING      = ( 48, 108, 255)   # folded blanket-wing (Pip BIRD_WING)
WING_D    = ( 22,  58, 180)   # wing underside / fold shadow (Pip BIRD_WING_D)
WING_HI   = (120, 168, 255)   # soft sheen along the blanket fold
BEAK      = (255, 188,  20)   # tucked gold beak (Pip BIRD_BEAK)
LASH      = ( 40,  20,  34)   # closed-eye lash curve — must read SLEEPING
ZZ        = (250, 250, 255)   # the "z z" sleep mark — lightest mark on sprite
OUTLINE   = ( 44,  18,  22)   # dark, high-value: reads on bright day sky
KEYLINE   = (255, 198, 150)   # warm rim — the NIGHT lifeline


def build(mode="normal") -> pygame.Surface:
    # Mode-agnostic: one static sleeping-chick sprite for every Pip skin.
    S = 44
    surf = pygame.Surface((S, S), pygame.SRCALPHA)
    cx = S // 2

    # Curled body geometry. A bold oval biased low + left so the z's have room
    # up-right without clipping the surface edge under the gameplay rotozoom.
    bcx, bcy = cx - 2, 26
    bw, bh = 15, 13                     # body half-extents (a fat round egg)

    body_rect = pygame.Rect(bcx - bw, bcy - bh, bw * 2, bh * 2)

    # --- Baked dark outline (drawn first, inflated) for the DAY silhouette.
    pygame.draw.ellipse(surf, OUTLINE, body_rect.inflate(4, 4))

    # --- Body: a lit red ball. Mid fill, then a lower-right shade crescent so
    # it reads as a curled volume, then a broad upper-left downy highlight.
    pygame.draw.ellipse(surf, BODY, body_rect)
    shade = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.ellipse(shade, BODY_SH,
                        body_rect.move(4, 5))
    mask = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.ellipse(mask, (255, 255, 255, 255), body_rect)
    shade.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(shade, (0, 0))
    pygame.draw.ellipse(surf, BODY_HI,
                        pygame.Rect(bcx - bw + 1, bcy - bh + 1, 12, 9))

    # --- Tucked tail: a small red wedge curling up the lower-left, the cue that
    # the chick is rolled into a ball rather than a plain egg.
    pygame.draw.polygon(surf, OUTLINE, [
        (bcx - bw + 1, bcy + 5), (bcx - bw - 5, bcy - 1), (bcx - bw - 2, bcy + 7)])
    pygame.draw.polygon(surf, BODY_SH, [
        (bcx - bw + 2, bcy + 4), (bcx - bw - 3, bcy + 0), (bcx - bw - 1, bcy + 6)])

    # --- Folded BLANKET-WING: a flat blue lobe laid across the upper-right back,
    # the single boldest value step on the sprite. Outline first, then the blue
    # fill, an underside fold shadow, and a sheen line so it reads as a wing
    # draped over the sleeping body — the "blanket" beat.
    wing_pts = [
        (bcx - 3, bcy - bh + 1),       # shoulder, near the nape
        (bcx + bw + 1, bcy - 5),       # top of the draped fold
        (bcx + bw - 1, bcy + 6),       # wing tip down the flank
        (bcx + 4, bcy + 8),            # tucks under the body
        (bcx - 1, bcy + 2),
    ]
    pygame.draw.polygon(surf, OUTLINE, [(x + 1, y) for x, y in wing_pts])
    pygame.draw.polygon(surf, WING, wing_pts)
    # Underside fold shadow along the lower wing edge.
    pygame.draw.polygon(surf, WING_D, [
        (bcx + bw - 1, bcy + 6), (bcx + 4, bcy + 8), (bcx + 7, bcy + 3)])
    # Sheen along the top of the fold so the blanket has a lit edge.
    pygame.draw.line(surf, WING_HI, (bcx + 1, bcy - bh + 3),
                     (bcx + bw - 2, bcy - 3), 2)

    # --- Tucked BEAK: a tiny gold wedge low on the breast, kept SMALL and held
    # below the closed eye so the face reads "head down, asleep" — it must never
    # out-mass the lash and flip the read to a single open eye.
    pygame.draw.polygon(surf, OUTLINE, [
        (bcx - bw + 2, bcy + 3), (bcx - bw + 7, bcy + 2), (bcx - bw + 6, bcy + 6)])
    pygame.draw.polygon(surf, BEAK, [
        (bcx - bw + 3, bcy + 3), (bcx - bw + 7, bcy + 3), (bcx - bw + 6, bcy + 5)])

    # --- CLOSED EYE: the identity stroke, the strongest face mark so the sleep
    # read never flips to awake. A bold downward-curving lash (lashes down) on
    # the upper face is what sells "asleep"; held 3px so it stays the dominant
    # facial feature even after the downscale + rotozoom. Drawn last, crisp.
    eye_rect = pygame.Rect(bcx - 10, bcy - 7, 10, 8)
    pygame.draw.arc(surf, LASH, eye_rect, 3.35, 6.05, 3)
    # A short tick at the outer corner so the closed lid reads as a lash curve.
    pygame.draw.line(surf, LASH, (bcx - 10, bcy - 3), (bcx - 11, bcy - 1), 2)

    # --- Warm keyline rim INSIDE the outline — the NIGHT lifeline that traces
    # the curled body on dark sky while staying subtle on day.
    pygame.draw.ellipse(surf, KEYLINE, body_rect, 1)

    # --- "z z" sleep mark rising up-right, pulled IN from the corner so the
    # rotozoom never clips it. The smaller z sits lower/left, the larger z up
    # and right — a rising drift. Lightest mark on the sprite (reads on day);
    # backed by a faint dark stub so it survives on day sky too.
    def _z(ox, oy, sz):
        top = (ox, oy)
        topr = (ox + sz, oy)
        botl = (ox, oy + sz)
        botr = (ox + sz, oy + sz)
        for col, dx in ((OUTLINE, 1), (ZZ, 0)):
            pygame.draw.line(surf, col, (top[0] + dx, top[1]), (topr[0] + dx, topr[1]), 2)
            pygame.draw.line(surf, col, (topr[0] + dx, topr[1]), (botl[0] + dx, botl[1]), 2)
            pygame.draw.line(surf, col, (botl[0] + dx, botl[1]), (botr[0] + dx, botr[1]), 2)

    _z(bcx + bw - 2, bcy - bh - 1, 4)     # near z (smaller, lower)
    _z(bcx + bw + 4, bcy - bh - 8, 5)     # far z (larger, higher drift)

    return pygame.transform.smoothscale(surf, (22, 22))
