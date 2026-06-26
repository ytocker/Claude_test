"""PEEKER — Pip's baby parrot, reaching up to be carried.

The identity is the "pick me up" pose: a chibi macaw with a HUGE pair of shiny
eyes turned up at the parent, two tiny wings thrown up and outstretched toward
him, and a little beak cracked open mid-chirp. Read in this order at true size:
(1) the two big bright eyes — the focal beat — (2) the upthrown wings forming a
wide V that brackets the head, (3) the open beak. Same family as Pip so it reads
as his offspring: BIRD_RED body, BIRD_WING blue wings tipped with BIRD_TIP green
and a BIRD_BELLY yellow stripe, BIRD_BEAK yellow beak.

22px read tradeoffs (WHY): the head is oversized (chibi) so the eyes can stay
genuinely big filled discs rather than dots that mud out on downscale — the eyes
are the whole concept, so they get the most pixels and the highest value
contrast (near-white sclera, black pupil, white catch-light). The body is a
single small red mass tucked under the head so it never competes with the eyes.
The wings are raised into a V wide enough to be legible as "reaching" but pulled
in from the surface edges so the gameplay rotozoom never clips the wingtips. The
open beak is two stacked yellow triangles with a dark gap between them — at 22px
a closed beak and an open beak look identical unless that dark gap is forced, so
it is drawn as an explicit notch. A baked dark outline (drawn first, inflated)
carries the silhouette on bright DAY sky; a warm keyline rim inside is the NIGHT
lifeline; the eyes' value contrast is what survives GRAYSCALE.
"""
import pygame

# Pip's family palette so the baby reads as his kin. Values are tuned so the
# IDENTITY RIDES ON VALUE: the eyes carry the brightest (sclera/catch-light) and
# darkest (pupil) pixels in the sprite, so the big-eyed read survives grayscale
# even when the red/blue hues flatten to similar greys.
RED      = (240,  55,  55)   # BIRD_RED — body + head base
RED_D    = (170,  25,  25)   # BIRD_RED_D — head/body shade crescent
RED_HI   = (255, 120, 120)   # cheek + crown blush (lit feathers)
WING     = ( 40, 100, 255)   # BIRD_WING — the raised wings
WING_D   = ( 20,  55, 180)   # wing underside shade
WING_HI  = (150, 195, 255)   # wing top highlight edge
TIP      = ( 50, 220, 100)   # BIRD_TIP — green wingtip (macaw signature)
BELLY    = (255, 170,  50)   # BIRD_BELLY — yellow flank stripe on the wing
BEAK     = (255, 185,   0)   # BIRD_BEAK — open chirping beak
BEAK_D   = (200, 130,   0)   # beak shade / split line
SCLERA   = (255, 255, 255)   # the big eye whites — the brightest mass
PUPIL    = ( 22,  16,  20)   # eye pupil — the darkest mass (grayscale anchor)
GLINT    = (255, 255, 255)   # catch-light shine
OUTLINE  = ( 34,  18,  22)   # baked dark outline — reads on bright day sky
KEYLINE  = (255, 214, 150)   # warm keyline rim — the NIGHT lifeline


def _eye(surf, cx, cy, r):
    # One big shiny eye looking UP. The eyes are the whole concept, so they keep
    # the widest possible WHITE ring (the brightest mass) around a big dark pupil
    # (the darkest mass) — that value sandwich is what survives the downscale to
    # 22px and grayscale. A bright catch-light high on the pupil turns the gaze
    # up at the parent and reads "wet/innocent baby eye" rather than a hard lens.
    pygame.draw.circle(surf, OUTLINE, (cx, cy), r + 1)
    pygame.draw.circle(surf, SCLERA, (cx, cy), r)               # big white
    pygame.draw.circle(surf, PUPIL, (cx, cy), r - 2)            # big dark pupil
    pygame.draw.circle(surf, GLINT, (cx - 1, cy - 2), 2)        # upward catch-light
    # A tiny lower secondary glint so the eye reads wet/shiny, not flat.
    pygame.draw.circle(surf, (255, 255, 255), (cx + 1, cy + 1), 1)


def _wing(angle_deg, flip=False):
    # A small raised wing: a blue feather wedge with a green tip and a yellow
    # secondary stripe (the scarlet-macaw markings, baby-sized). Rotated up into
    # the reaching V; drawn on its own surface so each side rotates cleanly.
    w = pygame.Surface((26, 26), pygame.SRCALPHA)
    # Outline silhouette first (inflated) for the day read.
    pygame.draw.polygon(w, OUTLINE, [(5, 22), (3, 5), (12, 2), (20, 14), (14, 23)])
    pygame.draw.polygon(w, WING, [(7, 21), (5, 7), (12, 4), (18, 14), (13, 21)])
    # Darker underside lobe.
    pygame.draw.polygon(w, WING_D, [(7, 21), (13, 21), (10, 13)])
    # Green primary tip + yellow secondary stripe — the family markings.
    pygame.draw.polygon(w, TIP, [(12, 4), (18, 8), (17, 14)])
    pygame.draw.polygon(w, BELLY, [(9, 9), (15, 11), (14, 16), (8, 14)])
    # Top highlight edge so the raised wing catches light.
    pygame.draw.line(w, WING_HI, (6, 8), (12, 5), 2)
    out = pygame.transform.rotate(w, angle_deg)
    if flip:
        out = pygame.transform.flip(out, True, False)
    return out


def build(mode="normal") -> pygame.Surface:
    # Mode-agnostic: one static baby-parrot sprite for every Pip skin.
    S = 44
    surf = pygame.Surface((S, S), pygame.SRCALPHA)
    cx = S // 2

    # Layout: chibi proportions. Big head high-centre, small body tucked beneath,
    # wings thrown up on either side of the head into a reaching V. Everything is
    # held off the edges so the wingtips never clip under the gameplay rotozoom.
    head_cy = 19
    head_r = 12

    # --- Wings FIRST (behind the head) so the head/eyes sit on top and stay the
    # hero. Thrown up-and-out: left wing tilts up-left, right up-right, forming
    # the wide "pick me up" V that brackets the head.
    lw = _wing(38, flip=True)
    rw = _wing(38, flip=False)
    surf.blit(lw, lw.get_rect(center=(cx - 11, head_cy - 1)))
    surf.blit(rw, rw.get_rect(center=(cx + 11, head_cy - 1)))

    # --- Body: a small red mass below the head. Outline first, then fill, with a
    # lower-right shade crescent for volume and a yellow belly patch tying it to
    # Pip's underside colour.
    body_cy = 33
    pygame.draw.ellipse(surf, OUTLINE, pygame.Rect(cx - 9, body_cy - 8, 18, 16))
    pygame.draw.ellipse(surf, RED, pygame.Rect(cx - 8, body_cy - 7, 16, 14))
    # Shade crescent (lower-right) masked to the body disc.
    shade = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.ellipse(shade, RED_D, pygame.Rect(cx - 4, body_cy - 3, 16, 14))
    mask = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.ellipse(mask, (255, 255, 255, 255),
                        pygame.Rect(cx - 8, body_cy - 7, 16, 14))
    shade.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(shade, (0, 0))
    # Yellow belly patch (Pip's underside colour).
    pygame.draw.ellipse(surf, BELLY, pygame.Rect(cx - 5, body_cy, 10, 6))
    # Tiny tucked feet so it reads as a whole bird, not a floating head+body.
    pygame.draw.line(surf, BEAK_D, (cx - 3, body_cy + 6), (cx - 4, body_cy + 9), 2)
    pygame.draw.line(surf, BEAK_D, (cx + 3, body_cy + 6), (cx + 4, body_cy + 9), 2)

    # --- Head: the oversized chibi dome. Outline, red fill, shade crescent,
    # cheek + crown blush. Big enough that the two eyes can be large filled discs.
    pygame.draw.circle(surf, OUTLINE, (cx, head_cy), head_r + 1)
    pygame.draw.circle(surf, RED, (cx, head_cy), head_r)
    hshade = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.circle(hshade, RED_D, (cx + 4, head_cy + 4), head_r)
    hmask = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.circle(hmask, (255, 255, 255, 255), (cx, head_cy), head_r)
    hshade.blit(hmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(hshade, (0, 0))
    # Crown highlight + cheek blush.
    pygame.draw.ellipse(surf, RED_HI, pygame.Rect(cx - 7, head_cy - 10, 10, 5))
    pygame.draw.circle(surf, RED_HI, (cx - 7, head_cy + 3), 3)
    pygame.draw.circle(surf, RED_HI, (cx + 7, head_cy + 3), 3)

    # --- The HUGE eyes: the focal beat. Two big shiny discs side by side,
    # gazing up. Sized to nearly fill the head width so they dominate the read at
    # true size; a 1px red bridge between them keeps two eyes legible, not one
    # cyclops blob, after the downscale.
    _eye(surf, cx - 5, head_cy - 1, 5)
    _eye(surf, cx + 5, head_cy - 1, 5)

    # --- Open chirping beak: two stacked yellow triangles with a forced dark gap
    # between them so the "open mouth" reads at 22px (a closed beak looks the
    # same without the notch). Sits just below the eyes, centred.
    beak_y = head_cy + 6
    # Upper mandible.
    pygame.draw.polygon(surf, OUTLINE, [(cx - 4, beak_y - 1), (cx + 4, beak_y - 1),
                                        (cx, beak_y + 2)])
    pygame.draw.polygon(surf, BEAK, [(cx - 3, beak_y), (cx + 3, beak_y),
                                     (cx, beak_y + 2)])
    # Dark open gap.
    pygame.draw.line(surf, OUTLINE, (cx - 2, beak_y + 2), (cx + 2, beak_y + 2), 1)
    # Lower mandible (smaller, dropped) — the open chirp.
    pygame.draw.polygon(surf, OUTLINE, [(cx - 3, beak_y + 3), (cx + 3, beak_y + 3),
                                        (cx, beak_y + 6)])
    pygame.draw.polygon(surf, BEAK_D, [(cx - 2, beak_y + 3), (cx + 2, beak_y + 3),
                                       (cx, beak_y + 5)])

    # --- Warm keyline rim INSIDE the outline — the NIGHT lifeline tracing the
    # head dome (the most recognisable contour), subtle on day, glowing on dark.
    pygame.draw.circle(surf, KEYLINE, (cx, head_cy), head_r, 1)

    return pygame.transform.smoothscale(surf, (22, 22))
