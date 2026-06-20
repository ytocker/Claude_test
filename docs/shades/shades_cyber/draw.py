"""CYBER VISOR — single-bar wraparound shade for Pip (side profile).

ONE continuous dark glossy band across both eyes (Kamina / Cyclops /
Geordi idiom), NOT two lenses. The read is three things stacked: a deep
near-black band with a vertical top->bottom gloss, ONE bright neon edge
line running its full length, and a faint diagonal scanline sheen. The
leading (near, +facing) edge is raked forward a touch so the bar reads as
a wraparound visor rather than a flat plate, with a short temple bar
trailing toward the ear (-facing).

The band is a FILLED rounded-rect (polygon, since the lead edge is raked)
rather than a stroked outline, and the neon is a solid 1-2px line, not a
soft blur: at eye_w=22 a blur washes out to nothing, but a filled band +
a hard bright line both survive the downscale and still read as a visor.
Everything scales off `eye_w` so the same code is a crisp 22px overlay and
a glossy 96px product shot.
"""
import pygame

_BAND_T = (44, 50, 66)              # cool top of the band (catches sky light)
_BAND_B = (10, 12, 20)              # near-black underside (vertical gloss)
_FRAME  = (70, 80, 104)             # brushed-metal rim around the glass
_FRAME_D = (24, 28, 40)             # rim shadow underside
_NEON   = (60, 240, 255)           # cyan signature edge line
_NEON_H = (200, 255, 255)           # hot core of the neon (1px highlight)
_SCAN   = (130, 220, 255)           # scanline sheen tint
_GLINT  = (236, 252, 255)


def _gloss_band(w, h, top, bot, alpha):
    """Filled w x h surface with a vertical top->bot tint at `alpha`.
    The vertical fade fakes the curve of glossy glass on a flat band."""
    g = pygame.Surface((w, h), pygame.SRCALPHA)
    span = max(1, h - 1)
    for yy in range(h):
        t = yy / span
        c = (int(top[0] + (bot[0] - top[0]) * t),
             int(top[1] + (bot[1] - top[1]) * t),
             int(top[2] + (bot[2] - top[2]) * t), alpha)
        pygame.draw.line(g, c, (0, yy), (w, yy))
    return g


def draw_shades(surf, cx, cy, eye_w, facing=1):
    f = facing
    half_w = max(4, int(eye_w * 0.50))      # ~1.0*eye_w total span
    half_h = max(2, int(eye_w * 0.17))      # ~0.34*eye_w total height
    rake = max(2, int(eye_w * 0.16))        # forward lean of the near edge
    rim = max(1, int(eye_w * 0.05))

    near_x = cx + f * half_w
    far_x = cx - f * half_w
    top = cy - half_h
    bot = cy + half_h

    # Raked wraparound silhouette: the near (+facing) edge slants forward
    # at top and pulls back at bottom so the bar reads as a curved visor.
    quad = [
        (far_x,          top),
        (near_x + f * rake, top),
        (near_x,         bot),
        (far_x - f * rake // 2, bot),
    ]

    # Short temple bar trailing toward the ear so it anchors on the head.
    tx = far_x - f * max(2, int(eye_w * 0.22))
    ty = cy - max(1, int(eye_w * 0.04))
    pygame.draw.line(surf, _FRAME_D, (far_x, cy + 1), (tx, ty + 1),
                     max(2, rim + 1))
    pygame.draw.line(surf, _FRAME, (far_x, cy), (tx, ty), max(1, rim))

    # Metal rim = a slightly larger band drawn first, then the glass inset.
    rim_quad = [(x - f * (rim if i in (0, 3) else -rim),
                 y - rim if i < 2 else y + rim) for i, (x, y) in enumerate(quad)]
    pygame.draw.polygon(surf, _FRAME_D, [(x, y + 1) for x, y in rim_quad])
    pygame.draw.polygon(surf, _FRAME, rim_quad)

    # Glass: a vertical-gloss band masked to the raked quad. Building the
    # tint on its own surface and clipping by the polygon keeps the gloss
    # axis-aligned (top bright, bottom black) regardless of the rake.
    bx0 = min(p[0] for p in quad)
    bx1 = max(p[0] for p in quad)
    bw = max(2, bx1 - bx0)
    bh = max(2, bot - top)
    band = _gloss_band(bw, bh, _BAND_T, _BAND_B, 255)
    mask = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255),
                        [(x - bx0, y - top) for x, y in quad])
    band.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(band, (bx0, top))

    # Diagonal scanline sheen — a few faint slashes across the glass sell the
    # "screen" feel. Kept low-alpha so it never competes with the neon read.
    sheen = pygame.Surface((bw, bh), pygame.SRCALPHA)
    step = max(3, int(eye_w * 0.10))
    for sx in range(-bh, bw, step * 2):
        pygame.draw.line(sheen, (*_SCAN, 26),
                         (sx, bh), (sx + bh, 0), max(1, rim))
    sheen.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(sheen, (bx0, top))

    # SIGNATURE: one bright neon line along the lower edge, full span. A dim
    # under-pass first widens the glow, then the hot 1px core on top keeps a
    # crisp line at tiny sizes where a soft blur would vanish.
    lo_a = (far_x - f * rake // 2, bot)
    lo_b = (near_x, bot)
    pygame.draw.line(surf, _NEON, lo_a, lo_b, max(2, rim + 1))
    pygame.draw.line(surf, _NEON_H,
                     (lo_a[0], lo_a[1] - 1), (lo_b[0], lo_b[1] - 1),
                     max(1, rim - 1) or 1)

    # A thin, dimmer neon tick along the top edge ties the wrap together
    # without competing with the bottom hero line. Drawn as a dark-cyan
    # half-bright accent so the lower edge stays the unambiguous signature.
    _TOP = (40, 150, 168)
    pygame.draw.line(surf, _TOP,
                     (far_x, top + 1), (near_x + f * rake, top + 1),
                     max(1, rim - 1) or 1)

    # Single pinprick glint on the leading edge — sells the glossy surface.
    pygame.draw.circle(surf, _GLINT,
                       (near_x - f * max(2, int(eye_w * 0.10)),
                        cy - max(1, int(eye_w * 0.06))),
                       max(1, int(eye_w * 0.045)))
