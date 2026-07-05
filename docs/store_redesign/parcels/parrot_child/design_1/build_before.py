"""MINI-PIP — a faithful chibi of Pip carried as the parcel (his baby).

The read must survive the gameplay rotozoom at ~22px BELOW Pip on both day and
night sky, and stay unmistakably a tiny scarlet-macaw of Pip's own family — same
red body / blue wing / yellow accent / dark face palette as the parent in
parrot.py. So this is built from Pip's exact colours, but re-proportioned as a
baby: an oversized round head sitting on a small upright body, looking UP at the
parent, with ONE big bright eye and NO sunglasses (it's a baby, not styled Pip).

22px read tradeoffs (WHY): at true size a faithful copy of the parent's hooked
beak + layered tail + feathered wing turns to mud, so the baby is reduced to
three bold legible masses — a big red head, a small red body, and ONE folded blue
wing patch — plus the two cues that carry "macaw baby": a big dark eye with a hot
white catch-light, and a short yellow hooked beak. The head is pushed large
(chibi proportion) so the eye + beak still resolve when the whole sprite is 22px.
A baked dark OUTLINE drawn first (inflated silhouette) carries the shape on bright
DAY sky; a warm cream keyline traced inside is the NIGHT lifeline. Everything is
held in toward centre so the rotozoom across Pip's bank arc never clips the head
crest, beak, or tail against the surface edge.
"""
import pygame

# Pip's own palette (mirrored from game.draw / game.config) so the baby reads as
# kin by colour alone, before silhouette even resolves.
BIRD_RED    = (240,  55,  55)
BIRD_RED_D  = (170,  25,  25)
BIRD_RED_HI = (255, 120, 120)   # cheek / crown lift
BIRD_WING   = ( 40, 100, 255)
BIRD_WING_D = ( 20,  55, 180)
BIRD_TIP    = ( 50, 220, 100)   # macaw green wing-tip flash
BIRD_BELLY  = (255, 170,  50)
BIRD_BEAK   = (255, 185,   0)
BIRD_BEAK_D = (200, 130,   0)
EYE_DARK    = ( 26,  18,  24)
WHITE       = (255, 255, 255)
OUTLINE     = ( 30,  12,  16)   # dark, warm — pops on bright day stone
KEYLINE     = (255, 224, 196)   # cream rim — the NIGHT lifeline


def _aaellipse(surf, color, center, rx, ry):
    cx, cy = center
    pygame.draw.ellipse(surf, color,
                        pygame.Rect(int(cx - rx), int(cy - ry),
                                    int(rx * 2), int(ry * 2)))


def build(mode="normal") -> pygame.Surface:
    # Mode-agnostic: one static baby-Pip for every parent skin.
    S = 44
    surf = pygame.Surface((S, S), pygame.SRCALPHA)
    cx = S // 2

    # Chibi proportions: an oversized head (the baby read) high on the surface,
    # a small compact body below. Both biased toward centre so the rotozoom
    # envelope never clips the crest or the tail against the 44px edge.
    head_cx, head_cy, head_rx, head_ry = cx, 17, 13, 12
    body_cx, body_cy, body_rx, body_ry = cx - 1, 32, 9, 8

    # --- Baked dark outline (drawn first, inflated) — the DAY silhouette read.
    _aaellipse(surf, OUTLINE, (body_cx, body_cy), body_rx + 2, body_ry + 2)
    _aaellipse(surf, OUTLINE, (head_cx, head_cy), head_rx + 2, head_ry + 2)

    # --- Tail: one short stubby red wedge below the body (a baby's tail is tiny).
    # Kept as a single mass with a yellow tip so it reads as Pip's tail, not a leg.
    tail = [(body_cx - 9, body_cy + 4), (body_cx - 3, body_cy + 7),
            (body_cx - 5, body_cy + 13), (body_cx - 11, body_cy + 9)]
    pygame.draw.polygon(surf, OUTLINE, [(p[0] - 1, p[1] + 1) for p in tail])
    pygame.draw.polygon(surf, BIRD_RED_D, tail)
    pygame.draw.polygon(surf, BIRD_BELLY,
                        [(body_cx - 9, body_cy + 8), (body_cx - 5, body_cy + 9),
                         (body_cx - 6, body_cy + 13), (body_cx - 10, body_cy + 11)])

    # --- Body: small red ellipse with a warm belly so the chest reads two-tone.
    _aaellipse(surf, BIRD_RED, (body_cx, body_cy), body_rx, body_ry)
    _aaellipse(surf, BIRD_RED_D, (body_cx - 2, body_cy + 4), body_rx - 3, body_ry - 4)
    _aaellipse(surf, BIRD_BELLY, (body_cx - 1, body_cy + 3), 6, 4)

    # --- Folded wing: ONE bold blue patch on the body's far side with a green tip
    # flash + a bright top edge — the macaw signature reduced to a single legible
    # mass (feather divider lines collapse to mud at 22px).
    wing = [(body_cx + 1, body_cy - 5), (body_cx + 9, body_cy - 2),
            (body_cx + 7, body_cy + 6), (body_cx, body_cy + 4)]
    pygame.draw.polygon(surf, OUTLINE, [(p[0] + 1, p[1] + 1) for p in wing])
    pygame.draw.polygon(surf, BIRD_WING, wing)
    pygame.draw.polygon(surf, BIRD_WING_D,
                        [(body_cx, body_cy + 4), (body_cx + 7, body_cy + 6),
                         (body_cx + 4, body_cy + 5)])
    pygame.draw.polygon(surf, BIRD_TIP,
                        [(body_cx + 7, body_cy - 2), (body_cx + 10, body_cy + 1),
                         (body_cx + 8, body_cy + 4)])
    pygame.draw.line(surf, (170, 205, 255),
                     (body_cx + 2, body_cy - 4), (body_cx + 8, body_cy - 1), 1)

    # --- Head: big red dome with a brighter crown + cheek flush so the volume
    # lifts without fussy texture. A tiny upward crest tuft sells "baby parrot".
    _aaellipse(surf, BIRD_RED, (head_cx, head_cy), head_rx, head_ry)
    _aaellipse(surf, BIRD_RED_HI, (head_cx - 2, head_cy - 5), 6, 4)
    _aaellipse(surf, BIRD_RED_HI, (head_cx - 5, head_cy + 1), 3, 3)
    # Crest: two short up-pointing red flicks at the crown.
    for dx in (-3, 1):
        pygame.draw.polygon(surf, OUTLINE,
                            [(head_cx + dx - 2, head_cy - head_ry + 2),
                             (head_cx + dx + 1, head_cy - head_ry - 4),
                             (head_cx + dx + 2, head_cy - head_ry + 2)])
        pygame.draw.polygon(surf, BIRD_RED,
                            [(head_cx + dx - 1, head_cy - head_ry + 2),
                             (head_cx + dx + 1, head_cy - head_ry - 3),
                             (head_cx + dx + 2, head_cy - head_ry + 2)])

    # --- Eye: ONE big dark eye with a pale bare-skin patch (the scarlet macaw's
    # signature) and a hot white catch-light. Pushed large + slightly up because
    # the baby is looking UP at its parent. This is THE load-bearing cue at 22px,
    # so it is sized as the single dominant feature of the head.
    eye_cx, eye_cy = head_cx + 3, head_cy - 1
    _aaellipse(surf, (250, 243, 236), (eye_cx, eye_cy), 6, 6)        # bare patch
    pygame.draw.circle(surf, EYE_DARK, (eye_cx + 1, eye_cy), 5)       # iris
    pygame.draw.circle(surf, (8, 6, 10), (eye_cx + 1, eye_cy), 5, 1)  # ring
    pygame.draw.circle(surf, WHITE, (eye_cx - 1, eye_cy - 2), 2)      # catch-light
    pygame.draw.circle(surf, (255, 255, 255), (eye_cx + 2, eye_cy + 3), 1)

    # --- Beak: short yellow hooked beak under the eye, angled slightly up toward
    # the parent. Two-tone so the hook reads; kept compact so it doesn't fuse with
    # the body at true size.
    beak = [(head_cx + 7, head_cy + 2), (head_cx + 13, head_cy + 3),
            (head_cx + 11, head_cy + 7), (head_cx + 7, head_cy + 6)]
    pygame.draw.polygon(surf, OUTLINE, [(p[0] + 1, p[1] + 1) for p in beak])
    pygame.draw.polygon(surf, BIRD_BEAK, beak)
    pygame.draw.polygon(surf, BIRD_BEAK_D,
                        [(head_cx + 7, head_cy + 5), (head_cx + 11, head_cy + 7),
                         (head_cx + 7, head_cy + 6)])
    pygame.draw.line(surf, (255, 232, 150),
                     (head_cx + 8, head_cy + 3), (head_cx + 12, head_cy + 4), 1)

    # --- Tiny tucked feet under the body so the baby reads as perched/sat upright.
    for fx in (-3, 3):
        pygame.draw.line(surf, BIRD_BEAK_D,
                         (body_cx + fx, body_cy + body_ry - 1),
                         (body_cx + fx, body_cy + body_ry + 3), 2)

    # --- Warm cream keyline traced inside the outline on head + body — the NIGHT
    # lifeline that lifts the silhouette off dark sky without shouting on day.
    pygame.draw.ellipse(surf, KEYLINE,
                        pygame.Rect(head_cx - head_rx, head_cy - head_ry,
                                    head_rx * 2, head_ry * 2), 1)
    pygame.draw.ellipse(surf, KEYLINE,
                        pygame.Rect(body_cx - body_rx, body_cy - body_ry,
                                    body_rx * 2, body_ry * 2), 1)

    return pygame.transform.smoothscale(surf, (22, 22))
