"""ROUND 1 explorations for CYBER VISOR (id shades_cyber).

Three genuinely different takes on a futuristic single-bar visor worn by
Pip in side profile (facing right). All proportional to ``eye_w`` so the
glowing slit stays the hero read at product size (~96) AND in-game (22px).

  V1  GVISOR  — cyan. Slim glossy wrap bar, one clean bright slit, soft
                additive halo. The purest Geordi/Cyclops read.
  V2  PULSE   — magenta. Recessed channel housing with a segmented LED
                slit + brighter end nodes; gamer-RGB energy.
  V3  HUD     — amber. Wrap bar that droops toward the beak (wrap-around
                cant) with a warm slit and a single HUD reticle over the
                near eye; the premium tone.

Each returns nothing; it paints onto ``surf`` centred on the eye.
"""
import math
import pygame


# ── shared additive-glow helper ──────────────────────────────────────────────
# A soft rounded-rect halo stamped with BLEND_ADD so the slit reads as
# emissive light, not paint. Kept tiny so it survives the 22px downscale.
def _add_halo(surf, rect, color, rad, layers):
    pad = 6
    halo = pygame.Surface((rect.w + pad * 2, rect.h + pad * 2), pygame.SRCALPHA)
    for grow, alpha in layers:
        pygame.draw.rect(halo, (*color, alpha),
                         (pad - grow, pad - grow,
                          rect.w + grow * 2, rect.h + grow * 2),
                         border_radius=rad + grow)
    surf.blit(halo, (rect.left - pad, rect.top - pad),
              special_flags=pygame.BLEND_ADD)


def _slit_glow(surf, x0, x1, y, color, core_w, halo_w):
    """Emissive horizontal slit: a wide soft additive underglow + a crisp
    bright core line on top, so the line reads luminous even at 22px."""
    if halo_w > 0:
        w = int(x1 - x0) + halo_w * 2
        h = halo_w * 2 + 2
        g = pygame.Surface((max(1, w), max(1, h)), pygame.SRCALPHA)
        pygame.draw.line(g, (*color, 90), (halo_w, h // 2),
                         (w - halo_w, h // 2), halo_w)
        surf.blit(g, (int(x0) - halo_w, int(y) - h // 2),
                  special_flags=pygame.BLEND_ADD)
    pygame.draw.line(surf, color, (x0, y), (x1, y), core_w)


# ─────────────────────────────────────────────────────────────────────────────
# V1 · GVISOR (cyan) — the clean classic
# ─────────────────────────────────────────────────────────────────────────────
V1_BODY   = (24, 27, 38)
V1_BODY_D = (12, 14, 22)
V1_BODY_H = (96, 104, 134)
V1_CAP    = (158, 166, 186)
V1_CAP_H  = (236, 242, 252)
V1_NEON   = (60, 240, 224)
V1_NEON_H = (210, 255, 250)


def draw_v1(surf, cx, cy, eye_w, facing=1):
    f = facing
    w = max(9, int(eye_w * 1.20))
    h = max(3, int(eye_w * 0.34))
    rad = max(1, int(eye_w * 0.16))

    rect = pygame.Rect(0, 0, w, h)
    rect.center = (cx, cy)

    _add_halo(surf, rect, V1_NEON, rad, [(4, 32), (2, 60)])

    # Glossy dark housing: dark base, lighter inset face, bright top catch-light.
    pygame.draw.rect(surf, V1_BODY_D, rect, border_radius=rad)
    inner = rect.inflate(-2, -2)
    pygame.draw.rect(surf, V1_BODY, inner, border_radius=max(1, rad - 1))
    pygame.draw.line(surf, V1_BODY_H, (rect.left + rad, rect.top + 1),
                     (rect.right - rad, rect.top + 1), max(1, int(eye_w * 0.03)))

    # One clean emissive slit running the visor.
    inset = max(2, int(w * 0.12))
    slit_y = cy + max(0, int(h * 0.06))
    _slit_glow(surf, rect.left + inset, rect.right - inset, slit_y,
               V1_NEON, max(1, int(eye_w * 0.10)), max(1, int(eye_w * 0.07)))
    # Hot core highlight on the front third (toward the beak = +f).
    hi0 = cx + f * int(w * 0.04)
    hi1 = cx + f * int(w * 0.34)
    pygame.draw.line(surf, V1_NEON_H, (hi0, slit_y - 1), (hi1, slit_y - 1),
                     max(1, int(eye_w * 0.04)))

    _draw_earcap(surf, cx, cy, eye_w, w, h, rad, f, V1_CAP, V1_CAP_H, V1_BODY_D)


# ─────────────────────────────────────────────────────────────────────────────
# V2 · PULSE (magenta) — recessed channel + segmented LED strip
# ─────────────────────────────────────────────────────────────────────────────
V2_BODY   = (30, 22, 38)
V2_BODY_D = (14, 10, 20)
V2_BODY_H = (110, 86, 130)
V2_CHAN   = (10, 6, 14)            # recessed channel the LEDs sit in
V2_CAP    = (170, 160, 180)
V2_CAP_H  = (244, 240, 250)
V2_NEON   = (255, 70, 200)
V2_NEON_H = (255, 200, 245)


def draw_v2(surf, cx, cy, eye_w, facing=1):
    f = facing
    w = max(9, int(eye_w * 1.22))
    h = max(4, int(eye_w * 0.42))
    rad = max(1, int(eye_w * 0.20))

    rect = pygame.Rect(0, 0, w, h)
    rect.center = (cx, cy)

    _add_halo(surf, rect, V2_NEON, rad, [(4, 34), (2, 66)])

    # Chunky bevelled housing.
    pygame.draw.rect(surf, V2_BODY_D, rect, border_radius=rad)
    pygame.draw.rect(surf, V2_BODY, rect.inflate(-2, -2),
                     border_radius=max(1, rad - 1))
    pygame.draw.line(surf, V2_BODY_H, (rect.left + rad, rect.top + 1),
                     (rect.right - rad, rect.top + 1), max(1, int(eye_w * 0.03)))

    # Recessed dark channel running the bar — the LED strip nests inside it.
    inset = max(2, int(w * 0.11))
    chan_y = cy + max(0, int(h * 0.04))
    chan_h = max(2, int(h * 0.42))
    chan = pygame.Rect(rect.left + inset, chan_y - chan_h // 2,
                       w - inset * 2, chan_h)
    pygame.draw.rect(surf, V2_CHAN, chan, border_radius=max(1, chan_h // 2))

    # Base emissive glow along the channel.
    _slit_glow(surf, chan.left + 1, chan.right - 1, chan_y,
               V2_NEON, max(1, int(eye_w * 0.07)), max(1, int(eye_w * 0.08)))

    # Brighter LED nodes spaced along the strip (segmented gamer-RGB read).
    n = max(3, int(w / max(4, eye_w * 0.22)))
    nr = max(1, int(eye_w * 0.05))
    for i in range(n):
        t = i / (n - 1)
        nx = chan.left + 2 + t * (chan.w - 4)
        pygame.draw.circle(surf, V2_NEON, (int(nx), chan_y), nr + 1)
        pygame.draw.circle(surf, V2_NEON_H, (int(nx), chan_y), nr)
    # Hot end-cap node toward the beak.
    end = chan.right - 2 if f > 0 else chan.left + 2
    pygame.draw.circle(surf, (255, 255, 255), (int(end), chan_y),
                       max(1, int(eye_w * 0.04)))

    _draw_earcap(surf, cx, cy, eye_w, w, h, rad, f, V2_CAP, V2_CAP_H, V2_BODY_D)


# ─────────────────────────────────────────────────────────────────────────────
# V3 · HUD (amber) — wrap-around droop + a reticle over the near eye
# ─────────────────────────────────────────────────────────────────────────────
V3_BODY   = (34, 30, 26)
V3_BODY_D = (18, 15, 12)
V3_BODY_H = (130, 116, 96)
V3_CAP    = (184, 170, 150)
V3_CAP_H  = (250, 240, 224)
V3_NEON   = (255, 168, 40)
V3_NEON_H = (255, 232, 170)


def _wrap_visor_poly(cx, cy, w, h, f, droop):
    """A bar whose FRONT edge (toward the beak, +f) droops down a little so
    the visor reads as wrapping around the face rather than a flat slab."""
    hw, hh = w / 2, h / 2
    front = f                     # +1 toward beak
    return [
        (cx - hw * front, cy - hh),                 # ear-top
        (cx + hw * front, cy - hh + droop * 0.3),   # front-top (droops)
        (cx + hw * front, cy + hh + droop),         # front-bottom (droops more)
        (cx - hw * front, cy + hh),                 # ear-bottom
    ]


def draw_v3(surf, cx, cy, eye_w, facing=1):
    f = facing
    w = max(9, int(eye_w * 1.20))
    h = max(3, int(eye_w * 0.32))
    rad = max(1, int(eye_w * 0.14))
    droop = max(1, int(eye_w * 0.10))

    rect = pygame.Rect(0, 0, w, int(h + droop + 2))
    rect.center = (cx, cy + droop // 2)
    _add_halo(surf, rect, V3_NEON, rad, [(4, 30), (2, 58)])

    # Wrap-around housing as a canted quad (front edge droops toward beak).
    outer = _wrap_visor_poly(cx, cy, w + 2, h + 2, f, droop)
    pygame.draw.polygon(surf, V3_BODY_D, outer)
    inner = _wrap_visor_poly(cx, cy, w - 2, h - 2, f, droop)
    pygame.draw.polygon(surf, V3_BODY, inner)
    # Top catch-light following the cant.
    top = [outer[0], outer[1]]
    pygame.draw.line(surf, V3_BODY_H, top[0], top[1], max(1, int(eye_w * 0.03)))

    # Emissive amber slit following the same droop.
    inset = max(2, int(w * 0.12))
    y_ear = cy + max(0, int(h * 0.10))
    y_front = y_ear + int(droop * 0.7)
    x_ear = cx - f * (w // 2 - inset)
    x_front = cx + f * (w // 2 - inset)
    core_w = max(1, int(eye_w * 0.09))
    # Soft underglow stroke.
    halo_w = max(1, int(eye_w * 0.07))
    g = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.line(g, (*V3_NEON, 90), (x_ear, y_ear), (x_front, y_front),
                     core_w + halo_w)
    surf.blit(g, (0, 0), special_flags=pygame.BLEND_ADD)
    pygame.draw.line(surf, V3_NEON, (x_ear, y_ear), (x_front, y_front), core_w)
    # Hot front segment.
    mx = cx + f * int(w * 0.10)
    my = y_ear + int(droop * 0.4)
    pygame.draw.line(surf, V3_NEON_H, (mx, my), (x_front, y_front),
                     max(1, int(eye_w * 0.035)))

    # HUD reticle over the near eye (toward the beak) — small bright ring + dot.
    rx = cx + f * int(w * 0.26)
    ry = y_ear + int(droop * 0.5)
    rr = max(2, int(eye_w * 0.10))
    ring = pygame.Surface((rr * 4, rr * 4), pygame.SRCALPHA)
    pygame.draw.circle(ring, (*V3_NEON_H, 200), (rr * 2, rr * 2), rr, 1)
    surf.blit(ring, (rx - rr * 2, ry - rr * 2), special_flags=pygame.BLEND_ADD)
    pygame.draw.circle(surf, V3_NEON_H, (rx, ry), max(1, int(eye_w * 0.03)))

    _draw_earcap(surf, cx, cy, eye_w, w, h, rad, f, V3_CAP, V3_CAP_H, V3_BODY_D)


# ── shared metal ear-cap (all three) ─────────────────────────────────────────
def _draw_earcap(surf, cx, cy, eye_w, w, h, rad, f, cap_col, cap_hi, dark):
    """Brushed-metal cap where the visor meets the ear (-facing), with a
    short stem flicking back toward the ear so the bar reads as worn."""
    ear_x = cx - f * (w // 2)
    cw = max(2, int(eye_w * 0.14))
    ch = h + max(2, int(eye_w * 0.06))
    cap = pygame.Rect(0, 0, cw, ch)
    cap.center = (ear_x, cy)
    pygame.draw.rect(surf, dark, cap.inflate(2, 2), border_radius=max(1, rad // 2))
    pygame.draw.rect(surf, cap_col, cap, border_radius=max(1, rad // 2))
    pygame.draw.line(surf, cap_hi, (cap.centerx - f, cap.top + 1),
                     (cap.centerx - f, cap.bottom - 1), max(1, int(eye_w * 0.03)))
    # Stem toward the ear.
    sx = ear_x - f * max(2, int(eye_w * 0.18))
    sy = cy - max(1, int(eye_w * 0.05))
    pygame.draw.line(surf, cap_col, (ear_x, cy), (sx, sy),
                     max(1, int(eye_w * 0.07)))
