"""MONOCLE — a single dapper round lens over Pip's near eye, in side profile.

Aristocratic read: ONE thin gold-rimmed lens sits over the front (+facing)
eye, with a tiny gold "brow pinch" at the top of the rim and a delicate chain
hanging down/back toward the ear (-facing). Because Pip is shown in side
profile a single near-eye lens reads perfectly — no far lens, no bridge.

The rim is a FILLED ring (gold disc, then the tinted glass inset by the rim
width) rather than a stroked circle — a 1px stroked outline stipples and breaks
at tiny radii (eye_w=22), but an inset disc is always solid metal. The chain is
a run of small filled dots so it survives the same tiny scale.
"""
import pygame

_RIM    = (236, 196, 96)            # warm gold metal
_RIM_H  = (255, 242, 188)           # bright top-rim crescent
_RIM_D  = (176, 132, 52)            # underside / shadow side of the wire
_GLASS_T = (214, 224, 232)          # cool top of the clear glass
_GLASS_B = (150, 170, 190)          # deeper floor (vertical fade reads as curve)
_GLINT  = (255, 255, 255)


def _tinted_disc(r, top, bot, alpha):
    """Round glass disc of radius r with a vertical top→bot tint at `alpha`.
    The vertical fade gives the flat disc a sense of curved glass."""
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


def draw_shades(surf, cx, cy, eye_w, facing=1):
    f = facing
    r   = max(3, int(eye_w * 0.30))
    rim = max(1, int(eye_w * 0.07))
    # Sit the lens over the near eye, nudged to the +facing side of (cx,cy).
    lx = cx + f * int(eye_w * 0.18)
    ly = cy

    # Chain hangs from the BACK-bottom of the rim (toward the ear, -facing) and
    # curves down. Small filled dots keep it solid at eye_w=22 where a stroked
    # poly-line would vanish; a slight S-curve sells "delicate dangling chain".
    cr = max(1, int(eye_w * 0.035))
    ax = lx - f * int(r * 0.78)             # rim anchor, back-bottom of the lens
    ay = ly + int(r * 0.62)
    drop = eye_w * 0.62
    for i in range(1, 7):
        t = i / 6.0
        px = ax - f * int(eye_w * 0.10 * (t - t * t) * 4.0)   # bows outward, back
        py = ay + int(drop * t)
        pygame.draw.circle(surf, _RIM_D, (px, py + 1), cr)
        pygame.draw.circle(surf, _RIM, (px, py), cr)
    # A slightly fatter "fixing ring" where the chain meets the rim.
    pygame.draw.circle(surf, _RIM_D, (ax, ay + 1), cr + 1)
    pygame.draw.circle(surf, _RIM, (ax, ay), cr + 1)

    # Solid gold ring = gold disc, then the tinted glass disc inset by rim.
    pygame.draw.circle(surf, _RIM_D, (lx, ly + 1), r)         # underside wire
    pygame.draw.circle(surf, _RIM, (lx, ly), r)
    gr = max(2, r - rim)
    glass = _tinted_disc(gr, _GLASS_T, _GLASS_B, 170)
    surf.blit(glass, (lx - gr, ly - gr))

    # Bright top crescent so the round metal pops off the scarlet head.
    pygame.draw.arc(surf, _RIM_H, (lx - r, ly - r, r * 2, r * 2),
                    0.5, 2.5, max(1, rim))

    # Gold "brow pinch" at the very top of the rim — the dapper tell of a
    # monocle that grips under the brow. A short thick stub of gold, capped
    # with a bright bead so it reads even at tiny scale.
    bx = lx + f * int(r * 0.22)
    by = ly - r
    pygame.draw.line(surf, _RIM_D, (bx, by + 1),
                     (bx + f * int(r * 0.34), by - int(r * 0.30) + 1),
                     max(2, rim + 1))
    pygame.draw.line(surf, _RIM, (bx, by),
                     (bx + f * int(r * 0.34), by - int(r * 0.30)),
                     max(2, rim + 1))
    pygame.draw.circle(surf, _RIM_H,
                       (bx + f * int(r * 0.34), by - int(r * 0.30)),
                       max(1, rim))

    # One pinprick glint on the lens — sells the glossy round glass.
    pygame.draw.circle(surf, _GLINT, (lx - f * (r // 2), ly - r // 2),
                       max(1, int(eye_w * 0.055)))
