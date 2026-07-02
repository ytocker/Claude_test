"""VOLT-WING (Design 3) — LEGENDARY cyborg/robot fly, scratch candidate.

A chunky brushed-metal fly-drone. The whole read is EYE-FIRST: two huge
touching neon hex domes own the top of the head so it screams FLY, not
spaceship. Below them a fat gunmetal barrel keeps the mass bird-sized. The
gag is ASYMMETRY — one bright organic membrane wing, one hard mechanical
fan-blade — fanning up-and-back across the 4 flap frames while the hex eyes
pulse (a scanning sweep). Everything else (thorax seam, hinge sparks,
labellum pad) is dialed down to a whisper so nothing steals the eyes.

Scratch-only: wrapped by the local `_make_prebuilt_skin` and exposed as
`build`; NOT registered in any production BUILDERS map.
"""
import math
import pygame

# Prod-shaped import with an inline fallback so the scratch file renders even
# if game.animal_skins can't be imported in isolation.
try:
    from game.animal_skins import _make_prebuilt_skin, _new
    from game.animal_skins import BCX, BCY, HCX, HCY, CROWN_Y
except Exception:  # pragma: no cover - isolated render fallback
    from game.parrot import SPRITE_W, _WING_ANGLES, _add_outline
    COMPOSITE_W, COMPOSITE_H = SPRITE_W, 84
    BCX, BCY = 32, 44
    HCX, HCY = 44, 34
    CROWN_Y = 24

    def _new():
        return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)

    def _make_prebuilt_skin(build_fn):
        state = {"frames": None, "rot": {}}

        def getter(frame_idx, tilt_deg):
            if state["frames"] is None:
                state["frames"] = [_add_outline(build_fn(a)) for a in _WING_ANGLES]
            frames = state["frames"]
            frame_idx %= len(frames)
            key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
            s = state["rot"].get(key)
            if s is None:
                s = pygame.transform.rotozoom(frames[frame_idx], key[1], 1.0)
                state["rot"][key] = s
            return s

        return getter


def _aaellipse(surf, color, center, rx, ry):
    cx, cy = center
    pygame.draw.ellipse(surf, color,
                        pygame.Rect(int(cx - rx), int(cy - ry),
                                    int(rx * 2), int(ry * 2)))


# ── palette ──────────────────────────────────────────────────────────────────
CHASSIS  = (32, 36, 42)         # #20242A  hard rim / rivet wells / vent slots
STEEL    = (90, 98, 108)        # #5A626C  brushed steel (blade wing + body)
STEEL_D  = (58, 64, 72)         # #3A4048  gunmetal shadow / labellum pad
STEEL_H  = (143, 160, 176)      # #8FA0B0  silver edge highlight
CAP      = (108, 118, 130)      # top-lit barrel cap
NEON     = (37, 224, 255)       # #25E0FF  neon cyan (hex grid, seam, dots)
PULSE    = (155, 244, 255)      # #9BF4FF  bright organic wing edge / pulse
SPARK    = (255, 230, 138)      # #FFE68A  hinge spark
EYE_BASE = (16, 24, 32)         # #101820  dark eye-dome base
WHITE    = (255, 255, 255)      # hot specular — the thing that says "eye"
WING_ORG = (207, 246, 255)      # translucent membrane fill

# Twin dome centres own the whole top of the head (y ≈ 23..38).
EYE_L, EYE_R = (37, 30), (50, 30)
EYE_R_PX = 7


def _hexagon(cx, cy, r, rot=math.pi / 6):
    return [(cx + r * math.cos(rot + i * math.pi / 3),
             cy + r * math.sin(rot + i * math.pi / 3)) for i in range(6)]


def _add_glow(surf, cx, cy, r, color, alpha):
    """Additive radial bloom — the only thing allowed to compete visually is
    the eyes, so glow is reserved for them (and, faintly, the seam)."""
    g = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
    for i in range(3):
        rr = int(r * (1.0 - i * 0.32))
        a = int(alpha * (0.4 + i * 0.3))
        _aaellipse(g, (*color, a), (r + 2, r + 2), rr, rr)
    surf.blit(g, (int(cx - r - 2), int(cy - r - 2)),
              special_flags=pygame.BLEND_RGBA_ADD)


def _organic_wing(angle_deg):
    """Translucent membrane wing with a bright #9BF4FF rim so its up-and-back
    fan reads as a distinct WING shape even at 40px. Fill kept low-alpha so the
    hex eyes stay the brightest element — the rim carries the read."""
    w = pygame.Surface((40, 34), pygame.SRCALPHA)
    body = [(6, 26), (15, 8), (28, 5), (36, 13), (28, 23), (15, 28)]
    pygame.draw.polygon(w, (*WING_ORG, 78), body)
    pygame.draw.polygon(w, (*PULSE, 235), body, 2)          # hero bright edge
    pygame.draw.lines(w, (*NEON, 190), False,
                      [(11, 23), (20, 14), (30, 9)], 1)      # circuit vein
    return pygame.transform.rotate(w, angle_deg)


def _blade_wing(angle_deg):
    """Solid gunmetal fan-blade — a HARD filled #5A626C shape (no fuzz) so the
    flap clearly breaks the barrel outline across the 4 frames."""
    w = pygame.Surface((42, 38), pygame.SRCALPHA)
    blade = [(6, 29), (16, 7), (30, 4), (39, 12), (32, 24), (18, 31)]
    pygame.draw.polygon(w, STEEL_D, blade)                  # underside
    pygame.draw.polygon(w, STEEL, [(9, 27), (17, 10), (28, 8),
                                   (34, 14), (28, 22), (18, 27)])
    pygame.draw.line(w, STEEL_H, (12, 23), (29, 9), 1)      # silver edge
    for i, sx in enumerate((20, 24, 28)):                   # machined vents
        pygame.draw.line(w, CHASSIS, (sx, 15 + i), (sx - 3, 22 + i), 1)
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
    glow_a = int(70 + 130 * eye_lvl)

    # ── far mechanical blade wing (behind the body, the higher/steeper of the
    #    two so metal vs organic reads as a splayed asymmetric fan) ──
    blade = _blade_wing(wing_angle_deg * 0.5 + 44)
    surf.blit(blade, blade.get_rect(center=(30, 22)).topleft)

    # ── gunmetal barrel body — clean round, hard rim, no stray edge fuzz ──
    _aaellipse(surf, STEEL_D, (BCX, BCY + 1), 14, 13)       # drop shadow base
    _aaellipse(surf, STEEL, (BCX, BCY), 13, 12)             # body
    _aaellipse(surf, CAP, (BCX - 1, BCY - 4), 9, 6)         # top-lit cap
    pygame.draw.ellipse(surf, CHASSIS,                      # hard 1px rim
                        pygame.Rect(BCX - 13, BCY - 12, 26, 24), 1)
    # Two clean rivets per flank (dark well + bright speck), no scatter.
    for ry in (BCY - 5, BCY + 5):
        for rx in (BCX - 9, BCX + 9):
            pygame.draw.circle(surf, CHASSIS, (rx, ry), 2)
            pygame.draw.circle(surf, STEEL_H, (rx - 1, ry - 1), 1)

    # Thorax seam demoted to a single 1px cyan hairline dead-centre (x=32).
    pygame.draw.line(surf, NEON, (BCX, BCY - 9), (BCX, BCY + 9), 1)

    # Two short steel antenna bristles — dim tips so they don't fight the eyes.
    for sgn, ax in ((-1, 30), (1, 33)):
        tipy = CROWN_Y - 2 - int(f * 2)
        pygame.draw.line(surf, STEEL, (ax, CROWN_Y + 4), (ax + sgn * 2, tipy), 1)
        pygame.draw.circle(surf, STEEL_H, (ax + sgn * 2, tipy), 1)

    # Mechanical labellum pad — a small dim #3A4048 nub with a single cyan
    # dot, sitting BELOW and dimmer than the eyes (no glow, no bloom).
    pygame.draw.circle(surf, STEEL_D, (46, 46), 4)
    pygame.draw.circle(surf, CHASSIS, (46, 46), 4, 1)
    pygame.draw.circle(surf, NEON, (46, 46), 1)

    # ── HERO: two huge touching hex-eye domes ──
    for (ex, ey) in (EYE_L, EYE_R):
        _add_glow(surf, ex, ey, EYE_R_PX + 3, eye_col, glow_a)
        pygame.draw.circle(surf, EYE_BASE, (ex, ey), EYE_R_PX)
        pygame.draw.circle(surf, CHASSIS, (ex, ey), EYE_R_PX, 1)
        # Honeycomb etched across the dome, brightening with the scan pulse.
        for hx, hy in ((ex, ey - 3), (ex - 3, ey), (ex + 3, ey),
                       (ex, ey + 3), (ex - 3, ey + 4), (ex + 3, ey + 4)):
            if (hx - ex) ** 2 + (hy - ey) ** 2 <= (EYE_R_PX - 1) ** 2:
                pygame.draw.lines(surf, (*eye_col, grid_a), True,
                                  _hexagon(hx, hy, 2.0), 1)
    # CRITICAL: hot-white specular upper-left of EACH dome — the "fly" tell.
    for (ex, ey) in (EYE_L, EYE_R):
        pygame.draw.circle(surf, WHITE, (ex - 3, ey - 3), 2)
        pygame.draw.circle(surf, (*PULSE, 220), (ex - 1, ey - 1), 1)

    # ── near organic wing (lower + more horizontal than the blade so the two
    #    splay apart; anchored left so it never creeps over the eyes) ──
    org = _organic_wing(wing_angle_deg * 0.7 + 8)
    surf.blit(org, org.get_rect(center=(20, 28)).topleft)

    # Two tiny sparks tight at the mechanical hinge (24,30) — signal only.
    jit = ((0, 0), (1, -1), (-1, 1), (0, -1))[fi]
    for (sx, sy) in ((24, 30), (26, 32)):
        pygame.draw.circle(surf, SPARK, (sx + jit[0], sy + jit[1]), 1)

    return surf


build = _make_prebuilt_skin(build_volt_wing)
