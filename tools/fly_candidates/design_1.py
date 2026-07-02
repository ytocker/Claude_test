"""BLOWFLY BARON (LEGENDARY) — scratch fly-skin candidate, design_1.

An iridescent metallic bottle-fly: a fat gleaming barrel abdomen under a
vertical green→cyan metallic ramp, crowned by two enormous garnet compound
eyes, wide translucent fan wings, a spongy labellum (mouth, NOT a needle),
and an animated diagonal oil-slick sheen band that shifts across the body
per frame. The two huge ruby eyes are the #1 fly tell and are sized to
dominate the head at 40px in motion.

Scratch exploration only — wrapped by animal_skins._make_prebuilt_skin and
exposed as ``build``; NEVER registered in animal_skins.BUILDERS.
"""
import pygame

from game.animal_skins import (
    BCX, BCY, HCX, HCY, CROWN_Y, _new, _make_prebuilt_skin, _flap, _rot_blit,
)
from game.parrot import _aaellipse


# ── palette ──────────────────────────────────────────────────────────────────
_BASE   = (18, 59, 52)          # #123B34 dark teal underbelly
_GREEN  = (47, 168, 114)        # #2FA872 bottle-green midtone
_CYAN   = (124, 246, 200)       # #7CF6C8 cyan rim-light / sheen head
_SEAM   = (10, 40, 34)          # darker segment seam
_EYE_C  = (139, 14, 35)         # #8B0E23 garnet eye centre
_EYE_E  = (90, 8, 24)           # #5A0818 garnet eye edge
_SHEEN  = ((124, 246, 200), (90, 209, 255), (185, 140, 255))  # cyan→azure→violet
_LAB    = (42, 81, 72)          # #2A5148 spongy labellum
_LAB_D  = (26, 54, 47)
_WING   = (207, 239, 232)       # #CFEFE8 pearly membrane
_VEIN   = (58, 112, 100)

_BODY_RX, _BODY_RY = 13, 12     # barrel abdomen half-extents


def _ramp(stops, t):
    """Linear colour interp across sorted (t, rgb) stops."""
    t = max(0.0, min(1.0, t))
    for i in range(len(stops) - 1):
        t0, c0 = stops[i]
        t1, c1 = stops[i + 1]
        if t <= t1:
            k = 0.0 if t1 == t0 else (t - t0) / (t1 - t0)
            return tuple(int(c0[j] + (c1[j] - c0[j]) * k) for j in range(3))
    return stops[-1][1]


def _barrel_gradient():
    """Vertical metallic ramp masked to the abdomen ellipse: cyan rim-light
    on top, bottle-green midriff, dark-teal belly — the chrome-fly read."""
    w, h = _BODY_RX * 2, _BODY_RY * 2
    stops = [(0.0, _CYAN), (0.42, _GREEN), (1.0, _BASE)]
    g = pygame.Surface((w, h), pygame.SRCALPHA)
    for yy in range(h):
        pygame.draw.line(g, _ramp(stops, yy / (h - 1)), (0, yy), (w, yy))
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.ellipse(mask, (255, 255, 255, 255), (0, 0, w, h))
    g.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return g


_BARREL = _barrel_gradient()


def _sheen_band(off):
    """Translucent diagonal oil-slick stripe, masked to the abdomen and
    additively blitted. `off` slides the green→cyan→violet ramp across the
    body so the sheen crawls per wing-frame — the animated signature."""
    w, h = _BODY_RX * 2, _BODY_RY * 2
    band = pygame.Surface((w, h), pygame.SRCALPHA)
    # Three parallel diagonal ribs, one per iridescent hue, offset in x.
    for i, col in enumerate(_SHEEN):
        x0 = int(off) + i * 5 - 4
        pygame.draw.line(band, (*col, 120), (x0, -6), (x0 - h - 8, h + 6), 5)
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.ellipse(mask, (255, 255, 255, 255), (0, 0, w, h))
    band.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return band


def build_fly_wing(wing_angle_deg):
    """Wide rounded fan wing (fly wings are broad teardrops, not blades):
    translucent pearl membrane, pearlescent green rim, three dark veins.
    Returned pre-rotated by `wing_angle_deg`."""
    w = pygame.Surface((48, 40), pygame.SRCALPHA)
    memb = (207, 239, 232, 140)     # ~55% alpha
    # Broad ovate blade + a taper toward the thorax root (lower-left).
    _aaellipse(w, memb, (29, 17), 16, 12)
    pygame.draw.polygon(w, memb, [(8, 28), (22, 10), (26, 26)])
    # Pearlescent green leading edge.
    pygame.draw.ellipse(w, (124, 246, 200, 205), (13, 4, 32, 26), 1)
    # Three splayed veins fanning from the wing base.
    for tx, ty in ((40, 10), (43, 18), (36, 27)):
        pygame.draw.line(w, (*_VEIN, 170), (11, 27), (tx, ty), 1)
    return pygame.transform.rotate(w, wing_angle_deg)


def _eye_dome(surf, cx, cy, r):
    """Deep garnet compound eye: radial jewel-red gradient + hot white
    upper-left specular dot. The single loudest fly cue."""
    for rr in range(r, 0, -1):
        surf and pygame.draw.circle(
            surf, _ramp([(0.0, _EYE_C), (1.0, _EYE_E)], rr / r), (cx, cy), rr)
    pygame.draw.circle(surf, (66, 6, 18), (cx, cy), r, 1)
    gx, gy = cx - r // 3, cy - r // 3
    pygame.draw.circle(surf, (255, 255, 255), (gx, gy), max(1, r // 3))
    pygame.draw.circle(surf, (255, 206, 214), (gx + 1, gy + 1), 1)


def build_fly_baron(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)                 # 1 = wings up, 0 = wings down
    up = 18 + f * 34                          # wings sweep higher on the up-beat

    # Far wing (behind the body) for depth — mirrored of the near wing.
    far = pygame.transform.flip(build_fly_wing(up), True, False)
    _rot_blit(surf, far, (BCX - 8, BCY - 9))

    # Green rim-glow bloom behind the body for night-sky visibility.
    glow = _new()
    for pad, a in ((3, 42), (2, 74), (1, 118)):
        pygame.draw.ellipse(
            glow, (124, 246, 200, a),
            (BCX - _BODY_RX - pad, BCY - _BODY_RY - pad,
             _BODY_RX * 2 + pad * 2, _BODY_RY * 2 + pad * 2), 1)
    surf.blit(glow, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    # Chrome barrel abdomen (vertical metallic ramp).
    surf.blit(_BARREL, (BCX - _BODY_RX, BCY - _BODY_RY))
    # Two faint chevron segment seams across the lower abdomen.
    for yy in (BCY + 3, BCY + 8):
        pygame.draw.lines(surf, _SEAM, False,
                          [(BCX - 9, yy - 2), (BCX, yy + 2), (BCX + 9, yy - 2)], 1)

    # Animated oil-slick sheen crawling across the body.
    surf.blit(_sheen_band((1.0 - f) * 12), (BCX - _BODY_RX, BCY - _BODY_RY),
              special_flags=pygame.BLEND_RGBA_ADD)

    # Bristly thorax setae poking off the top (drawn before the head mass).
    for bx in (26, 30, 34):
        pygame.draw.line(surf, _SEAM, (bx, HCY - 2), (bx - 1, HCY - 6), 1)

    # Head mass under the eyes.
    _aaellipse(surf, _BASE, (HCX, HCY + 1), 11, 8)
    _aaellipse(surf, _GREEN, (HCX, HCY - 1), 9, 6)

    # HERO: two enormous garnet compound eyes nearly touching.
    _eye_dome(surf, 38, 32, 7)
    _eye_dome(surf, 50, 32, 7)

    # Spongy labellum (mouth pad) below the head — rounded, grooved, NO needle.
    _aaellipse(surf, _LAB, (46, 45), 4, 3)
    _aaellipse(surf, _LAB_D, (46, 46), 4, 2)
    for gx in (44, 47):
        pygame.draw.line(surf, _LAB_D, (gx, 43), (gx, 47), 1)

    # Near wing over the body — the hero fan on the near side.
    _rot_blit(surf, build_fly_wing(up), (BCX + 8, BCY - 9))
    return surf


build = _make_prebuilt_skin(build_fly_baron)
