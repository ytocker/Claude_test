"""ROUND SHADES (Lennon) — three round-1 explorations.

Each variant honours the same contract as game/shades_round.py:
    draw_shades(surf, cx, cy, eye_w, facing=1)
side-profile, near/front lens toward the beak (+facing), temple toward the
ear (-facing). All geometry scales off eye_w so it reads at product size
(eye_w=96) and in-game (eye_w=22, where a 1px rim is the whole frame).

The brief: small PERFECTLY-CIRCULAR thin metal rims, lightly TINTED lenses,
1960s rockstar vibe. The two distinct circles + delicate bridge + the tint
must survive 22px. Variants differ in metal colour, tint hue, and how the
thin rim is kept legible at tiny size.
"""
import pygame


# ─────────────────────────────────────────────────────────────────────────────
# Shared lens helper: a circular tinted glass with a vertical fade so the disc
# reads as glass, not a flat dot. Clipped to a circle via BLEND_RGBA_MIN.
# ─────────────────────────────────────────────────────────────────────────────
def _tinted_disc(r, top, bot, alpha):
    """Round glass disc r-radius, vertical top→bot tint at `alpha` opacity."""
    g = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    span = max(1, r * 2 - 1)
    for yy in range(r * 2):
        t = yy / span
        c = (int(top[0] + (bot[0] - top[0]) * t),
             int(top[1] + (bot[1] - top[1]) * t),
             int(top[2] + (bot[2] - top[2]) * t), alpha)
        pygame.draw.line(g, c, (0, yy), (r * 2, yy))
    clip = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    pygame.draw.circle(clip, (255, 255, 255, 255), (r, r), r)
    g.blit(clip, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return g


# ═════════════════════════════════════════════════════════════════════════════
# VARIANT A — GOLD WIRE / ROSE TINT (the canonical Lennon).
#   Thin warm-gold rim, rose-quartz glass with a bright top crescent so the
#   tint reads "rose" not "grey". A delicate dipped bridge + cable temple.
#   The rim is drawn as a filled ring (outer gold disc minus inner glass) so
#   even a 1px rim at 22px is solid metal, never a stippled circle outline.
# ═════════════════════════════════════════════════════════════════════════════
A_RIM    = (236, 196, 96)
A_RIM_H  = (255, 242, 188)
A_RIM_D  = (176, 132, 52)
A_ROSE_T = (236, 180, 196)          # bright rose top
A_ROSE_B = (170, 96, 124)           # deeper rose floor
A_GLINT  = (255, 255, 255)


def draw_shades_A(surf, cx, cy, eye_w, facing=1):
    f = facing
    r    = max(3, int(eye_w * 0.26))
    sep  = max(4, int(eye_w * 0.46))
    rim  = max(1, int(eye_w * 0.065))
    near = (cx + f * (sep // 2), cy)
    far  = (cx - f * (sep // 2), cy)

    # Delicate dipped bridge BEHIND the rims so the rims overlap it cleanly.
    bx0 = far[0] + f * (r - rim)
    bx1 = near[0] - f * (r - rim)
    by = cy - max(1, int(r * 0.42))
    pygame.draw.line(surf, A_RIM_D, (bx0, by + 1), (bx1, by + 1),
                     max(1, rim))
    pygame.draw.line(surf, A_RIM, (bx0, by), (bx1, by), max(1, rim))

    # Cable temple toward the ear, with a soft curl at the end.
    ex = far[0] - f * (r + max(2, int(eye_w * 0.30)))
    pygame.draw.line(surf, A_RIM_D, (far[0] - f * (r - 1), cy - 1),
                     (ex, cy - max(1, int(eye_w * 0.06))), max(1, rim))
    pygame.draw.line(surf, A_RIM, (far[0] - f * (r - 1), cy - 1),
                     (ex, cy - max(1, int(eye_w * 0.06))), max(1, rim - 1) or 1)

    for (lx, ly) in (far, near):
        # Solid gold ring = gold disc, then tinted glass disc inset by `rim`.
        pygame.draw.circle(surf, A_RIM_D, (lx, ly + 1), r)      # underside
        pygame.draw.circle(surf, A_RIM, (lx, ly), r)
        gr = max(2, r - rim)
        glass = _tinted_disc(gr, A_ROSE_T, A_ROSE_B, 205)
        surf.blit(glass, (lx - gr, ly - gr))
        # Bright top rim crescent so the round metal pops off the head.
        pygame.draw.arc(surf, A_RIM_H, (lx - r, ly - r, r * 2, r * 2),
                        0.5, 2.5, max(1, rim))

    # One pinprick glint on the near lens — sells the glossy round glass.
    pygame.draw.circle(surf, A_GLINT,
                       (near[0] - f * (r // 2), cy - r // 2),
                       max(1, int(eye_w * 0.05)))


# ═════════════════════════════════════════════════════════════════════════════
# VARIANT B — GUNMETAL / TEAL-AMBER SPLIT (rock-poster pop).
#   Cool gunmetal rim (silver-blue) for a sharper 70s look, and a two-tone
#   glass: teal up top melting into amber low — the classic gradient sunglass
#   that reads as colourful tint even at thumbnail size. Straight bar bridge.
# ═════════════════════════════════════════════════════════════════════════════
B_RIM    = (150, 162, 178)          # cool gunmetal
B_RIM_H  = (224, 232, 244)
B_RIM_D  = (96, 106, 122)
B_TEAL   = (70, 168, 168)           # teal top
B_AMBER  = (224, 150, 70)           # amber floor
B_GLINT  = (255, 255, 255)


def draw_shades_B(surf, cx, cy, eye_w, facing=1):
    f = facing
    r    = max(3, int(eye_w * 0.27))
    sep  = max(4, int(eye_w * 0.48))
    rim  = max(1, int(eye_w * 0.07))
    near = (cx + f * (sep // 2), cy)
    far  = (cx - f * (sep // 2), cy)

    # Straight gunmetal bar bridge sitting just above lens centres.
    bx0 = far[0] + f * (r - rim)
    bx1 = near[0] - f * (r - rim)
    by = cy - max(1, int(r * 0.30))
    pygame.draw.line(surf, B_RIM_D, (bx0, by + 1), (bx1, by + 1), max(1, rim))
    pygame.draw.line(surf, B_RIM, (bx0, by), (bx1, by), max(1, rim))
    pygame.draw.line(surf, B_RIM_H, (bx0, by - 1), (bx1, by - 1), 1)

    # Temple arm, straight and thin toward the ear.
    ex = far[0] - f * (r + max(2, int(eye_w * 0.32)))
    pygame.draw.line(surf, B_RIM_D, (far[0] - f * (r - 1), cy),
                     (ex, cy - max(1, int(eye_w * 0.07))), max(1, rim))
    pygame.draw.line(surf, B_RIM, (far[0] - f * (r - 1), cy - 1),
                     (ex, cy - max(1, int(eye_w * 0.07)) - 1), max(1, rim - 1) or 1)

    for (lx, ly) in (far, near):
        pygame.draw.circle(surf, B_RIM_D, (lx, ly + 1), r)
        pygame.draw.circle(surf, B_RIM, (lx, ly), r)
        gr = max(2, r - rim)
        glass = _tinted_disc(gr, B_TEAL, B_AMBER, 210)
        surf.blit(glass, (lx - gr, ly - gr))
        pygame.draw.arc(surf, B_RIM_H, (lx - r, ly - r, r * 2, r * 2),
                        0.6, 2.4, max(1, rim))

    pygame.draw.circle(surf, B_GLINT,
                       (near[0] - f * (r // 2), cy - r // 2),
                       max(1, int(eye_w * 0.05)))


# ═════════════════════════════════════════════════════════════════════════════
# VARIANT C — GOLD WIRE / AMBER TINT, DOUBLE-WIRE BRIDGE (vintage aviator-round).
#   The warmest, most 70s take: amber/whisky glass with a gold rim, and a
#   characterful TWO-bar wire bridge (the giveaway detail of period round
#   specs). Tightest lenses of the three so it reads "small round shades".
# ═════════════════════════════════════════════════════════════════════════════
C_RIM    = (240, 202, 104)
C_RIM_H  = (255, 244, 190)
C_RIM_D  = (182, 138, 56)
C_AMBER_T = (240, 196, 118)         # bright whisky top
C_AMBER_B = (190, 128, 56)          # deep amber floor
C_GLINT  = (255, 255, 255)


def draw_shades_C(surf, cx, cy, eye_w, facing=1):
    f = facing
    r    = max(3, int(eye_w * 0.24))   # tightest = most "Lennon"
    sep  = max(4, int(eye_w * 0.44))
    rim  = max(1, int(eye_w * 0.065))
    near = (cx + f * (sep // 2), cy)
    far  = (cx - f * (sep // 2), cy)

    bx0 = far[0] + f * (r - rim)
    bx1 = near[0] - f * (r - rim)
    # Double-wire bridge: an upper and a lower thin gold bar.
    for dy in (-max(1, int(r * 0.45)), max(1, int(r * 0.15))):
        pygame.draw.line(surf, C_RIM_D, (bx0, cy + dy + 1), (bx1, cy + dy + 1),
                         max(1, rim))
        pygame.draw.line(surf, C_RIM, (bx0, cy + dy), (bx1, cy + dy),
                         max(1, rim - 1) or 1)

    # Cable temple curling toward the ear.
    ex = far[0] - f * (r + max(2, int(eye_w * 0.30)))
    pygame.draw.line(surf, C_RIM_D, (far[0] - f * (r - 1), cy - 1),
                     (ex, cy - max(1, int(eye_w * 0.05))), max(1, rim))
    pygame.draw.line(surf, C_RIM, (far[0] - f * (r - 1), cy - 1),
                     (ex, cy - max(1, int(eye_w * 0.05))), max(1, rim - 1) or 1)

    for (lx, ly) in (far, near):
        pygame.draw.circle(surf, C_RIM_D, (lx, ly + 1), r)
        pygame.draw.circle(surf, C_RIM, (lx, ly), r)
        gr = max(2, r - rim)
        glass = _tinted_disc(gr, C_AMBER_T, C_AMBER_B, 210)
        surf.blit(glass, (lx - gr, ly - gr))
        pygame.draw.arc(surf, C_RIM_H, (lx - r, ly - r, r * 2, r * 2),
                        0.5, 2.5, max(1, rim))

    pygame.draw.circle(surf, C_GLINT,
                       (near[0] - f * (r // 2), cy - r // 2),
                       max(1, int(eye_w * 0.05)))


VARIANTS = [
    ("A · gold / rose", draw_shades_A, True),     # implemented pick
    ("B · gunmetal / teal-amber", draw_shades_B, False),
    ("C · gold / amber 2-wire", draw_shades_C, False),
]
