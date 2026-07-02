"""VOLT-WING (Design 3) — LEGENDARY cyborg/robot fly, scratch candidate.

A chunky brushed-metal fly-drone: fat gunmetal barrel body so it still reads
FLY, not spaceship. The design's gag is ASYMMETRY — one organic translucent
wing, one hard mechanical fan-blade wing — paired with neon hex compound eyes
that pulse across the 4 flap frames (a scanning sweep) and sparks flicking off
the mechanical wing hinge.

Scratch-only: wrapped by the local `_make_prebuilt_skin` and exposed as
`build`; NOT registered in any production BUILDERS map.
"""
import math
import pygame

from game.animal_skins import (
    _make_prebuilt_skin, _new, _aaellipse,
    BCX, BCY, HCX, HCY, CROWN_Y,
)

# ── palette ──────────────────────────────────────────────────────────────────
CHASSIS   = (32, 36, 42)        # #20242A  dark chassis / rivet wells
STEEL     = (90, 98, 108)       # #5A626C  brushed steel
STEEL_D   = (58, 64, 72)        # #3A4048  gunmetal shadow
STEEL_H   = (143, 160, 176)     # #8FA0B0  silver edge highlight
NEON      = (37, 224, 255)      # #25E0FF  neon cyan
PULSE     = (155, 244, 255)     # #9BF4FF  bright pulse highlight
SPARK     = (255, 230, 138)     # #FFE68A  spark
EYE_BASE  = (16, 24, 32)        # #101820  dark eye dome base
WING_ORG  = (207, 246, 255)     # #CFF6FF  organic membrane


def _hexagon(cx, cy, r, rot=math.pi / 6):
    """Flat honeycomb hexagon points about (cx, cy)."""
    return [(cx + r * math.cos(rot + i * math.pi / 3),
             cy + r * math.sin(rot + i * math.pi / 3)) for i in range(6)]


def _add_glow(surf, cx, cy, r, color, alpha):
    """Additive radial bloom — sells the 'this thing is powered' cyborg read."""
    g = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
    for i in range(3):
        rr = int(r * (1.0 - i * 0.32))
        a = int(alpha * (0.4 + i * 0.3))
        _aaellipse(g, (*color, a), (r + 2, r + 2), rr, rr)
    surf.blit(g, (int(cx - r - 2), int(cy - r - 2)),
              special_flags=pygame.BLEND_RGBA_ADD)


def _organic_wing(angle_deg):
    """Translucent membrane wing with two glowing circuit-veins."""
    w = pygame.Surface((46, 40), pygame.SRCALPHA)
    body = [(8, 20), (22, 6), (40, 8), (44, 18), (38, 28), (22, 32), (10, 28)]
    pygame.draw.polygon(w, (*WING_ORG, 128), body)
    pygame.draw.polygon(w, (*PULSE, 150), body, 1)
    # Circuit-veins glow along the membrane like traces on a PCB.
    pygame.draw.lines(w, (*NEON, 200), False, [(12, 22), (26, 16), (40, 14)], 1)
    pygame.draw.lines(w, (*NEON, 160), False, [(13, 26), (27, 22), (37, 22)], 1)
    return pygame.transform.rotate(w, angle_deg)


def _blade_wing(angle_deg):
    """Solid mechanical fan-blade with three slot cutouts."""
    w = pygame.Surface((46, 40), pygame.SRCALPHA)
    blade = [(8, 18), (26, 8), (42, 12), (43, 22), (28, 30), (10, 26)]
    pygame.draw.polygon(w, STEEL_D, blade)
    pygame.draw.polygon(w, STEEL, [(9, 18), (26, 10), (40, 14), (39, 21),
                                   (26, 27), (11, 24)])
    pygame.draw.line(w, STEEL_H, (12, 18), (38, 14), 1)
    # Rectangular slot cutouts read as machined vents at 40px.
    for i, sx in enumerate((18, 25, 32)):
        pygame.draw.rect(w, CHASSIS, (sx, 15 + i, 3, 8))
    return pygame.transform.rotate(w, angle_deg)


def build_volt_wing(wing_angle_deg):
    surf = _new()

    # Per-frame scanning pulse: dim → mid → bright → mid across the flap.
    f = (wing_angle_deg + 40) / 90.0
    fi = max(0, min(3, int(round(f * 3))))
    eye_lvl = (0.30, 0.62, 1.0, 0.62)[fi]
    eye_col = tuple(int(NEON[i] + (PULSE[i] - NEON[i]) * eye_lvl)
                    for i in range(3))
    grid_a = int(120 + 135 * eye_lvl)
    glow_a = int(60 + 120 * eye_lvl)

    # Wings fan from a shared hinge; asymmetry is the gag so each swings
    # on its own sense. Far mechanical blade first (behind the body).
    blade = _blade_wing(-wing_angle_deg * 0.5 + 16)
    surf.blit(blade, blade.get_rect(center=(24, 30)).topleft)

    # ── gunmetal barrel body (fat oval → reads FLY) ──
    _aaellipse(surf, STEEL_D, (BCX + 1, BCY + 1), 14, 13)
    _aaellipse(surf, STEEL, (BCX, BCY), 13, 12)
    # Top-lit ramp: brighter cap up top, silver rim on the upper-right.
    _aaellipse(surf, (108, 118, 130), (BCX - 1, BCY - 4), 10, 6)
    pygame.draw.arc(surf, STEEL_H, (BCX - 12, BCY - 12, 26, 22),
                    math.radians(10), math.radians(80), 2)
    # Rivets down each flank: dark well + bright speck.
    for ry in (BCY - 6, BCY, BCY + 6):
        for rx in (BCX - 10, BCX + 9):
            pygame.draw.circle(surf, CHASSIS, (rx, ry), 2)
            pygame.draw.circle(surf, STEEL_H, (rx - 1, ry - 1), 1)

    # Glowing cyan cyborg seam down the thorax centre, with bloom.
    _add_glow(surf, BCX - 1, BCY, 6, NEON, 90)
    pygame.draw.line(surf, PULSE, (BCX - 1, BCY - 9), (BCX - 1, BCY + 9), 1)

    # Mechanical labellum nozzle (the fly's "mouth" pad) under the head.
    pygame.draw.circle(surf, STEEL_D, (46, 45), 4)
    pygame.draw.circle(surf, CHASSIS, (46, 45), 4, 1)
    _add_glow(surf, 46, 45, 3, NEON, glow_a)
    pygame.draw.circle(surf, eye_col, (46, 45), 1)

    # ── two hex-eye domes ──
    for ex in (38, 50):
        _add_glow(surf, ex, 32, 9, eye_col, glow_a)
        pygame.draw.circle(surf, EYE_BASE, (ex, 32), 7)
        pygame.draw.circle(surf, STEEL_D, (ex, 32), 7, 1)
        # Honeycomb of small hexagons etched over the dome, brightening
        # with the scan pulse.
        clip = surf.get_clip()
        for hx, hy in ((ex, 29), (ex - 3, 32), (ex + 3, 32),
                       (ex - 3, 35), (ex + 3, 35), (ex, 35)):
            if (hx - ex) ** 2 + (hy - 32) ** 2 <= 36:
                pygame.draw.lines(surf, (*eye_col, grid_a), True,
                                  _hexagon(hx, hy, 2.0), 1)
        surf.set_clip(clip)
        pygame.draw.circle(surf, (*PULSE, int(200 * eye_lvl + 40)),
                           (ex - 2, 30), 1)

    # ── 3 antenna-wire bristles off the thorax top ──
    for sgn, ax in ((-1, 25), (0, 27), (1, 29)):
        tipx = ax + sgn * 3
        tipy = CROWN_Y - 2 - int(f * 2)
        pygame.draw.line(surf, STEEL_H, (ax, CROWN_Y + 6), (tipx, tipy), 1)
        pygame.draw.circle(surf, NEON, (tipx, tipy), 1)

    # ── near organic wing over the body (the translucent one) ──
    _rot_center = _organic_wing(wing_angle_deg)
    surf.blit(_rot_center, _rot_center.get_rect(center=(30, 28)).topleft)

    # ── spark FX at the mechanical wing hinge, jittered per frame ──
    jitter = ((0, 0, 1, 0), (-1, 1, 0, -1), (1, -1, -1, 1))
    for k, (bx, by) in enumerate(((24, 30), (22, 27), (26, 33))):
        if fi == 3 and k == 2:
            continue                      # thin out on the calm pose
        sx = bx + jitter[k][fi]
        sy = by - jitter[(k + 1) % 3][fi]
        _add_glow(surf, sx, sy, 2, SPARK, 150)
        pygame.draw.circle(surf, SPARK, (sx, sy), 1)

    return surf


build = _make_prebuilt_skin(build_volt_wing)
