"""VOLT-WING (Design 3) — LEGENDARY cyborg/robot fly, scratch candidate.

A chunky brushed-metal fly-drone. The read is EYE-FIRST but the two hex
sensors are deliberately UNEQUAL: a hot near (right) dome that wins focus
and a dimmer teal far (left) dome, split by a dark gunmetal gutter so they
never fuse into one patch. Below sits a solid dark-grey barrel that holds
its own blob silhouette even with the cyan accent stripped. The legendary
gag is ASYMMETRY read in silhouette — one bright organic membrane wing and
one hard gunmetal fan-blade catching a silver edge — fanning up-and-back
across the 4 flap frames while the near eye pulses.

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
# Barrel is lifted to a solid mid-dark grey so the body reads as a plump blob
# on its own — the cyan accent is now a garnish, not the whole silhouette.
CHASSIS  = (32, 36, 42)         # #20242A  hard rim / rivet wells / eye gutter
STEEL    = (104, 112, 124)      # #68707C  brushed barrel body (lifted value)
STEEL_D  = (66, 72, 82)         # gunmetal shadow / labellum pad
STEEL_H  = (143, 160, 176)      # #8FA0B0  silver blade edge highlight
CAP      = (128, 138, 150)      # top-lit barrel cap
NEON     = (37, 224, 255)       # #25E0FF  neon cyan (near eye, hex grid)
PULSE    = (155, 244, 255)      # #9BF4FF  bright organic wing edge / pulse
TEAL_F   = (24, 118, 128)       # far-eye teal at ~60% brightness (no ring)
SPARK    = (255, 230, 138)      # #FFE68A  hinge spark
EYE_BASE = (16, 24, 32)         # #101820  dark eye-dome base
WHITE    = (255, 255, 255)      # hot specular — the "fly" tell (near eye only)
WING_ORG = (207, 246, 255)      # translucent membrane fill

# Twin domes, pushed apart to leave a hard gunmetal gutter between them so they
# read as TWO sensors at 40px. Right (near) dome wins focus; left (far) is dim.
EYE_R_PX = 7
EYE_F = (36, 30)               # far / left — dim teal, sits back
EYE_N = (51, 30)               # near / right — hot cyan, hero focus
GUTTER_X = 43                  # dark seam between the two domes


def _hexagon(cx, cy, r, rot=math.pi / 6):
    return [(cx + r * math.cos(rot + i * math.pi / 3),
             cy + r * math.sin(rot + i * math.pi / 3)) for i in range(6)]


def _add_glow(surf, cx, cy, r, color, alpha):
    """Additive radial bloom — reserved for the eyes. Kept modest so the barrel
    (not the neon rim) carries the silhouette against bright day biomes."""
    g = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
    for i in range(3):
        rr = int(r * (1.0 - i * 0.32))
        a = int(alpha * (0.4 + i * 0.3))
        _aaellipse(g, (*color, a), (r + 2, r + 2), rr, rr)
    surf.blit(g, (int(cx - r - 2), int(cy - r - 2)),
              special_flags=pygame.BLEND_RGBA_ADD)


def _organic_wing(angle_deg):
    """Translucent membrane wing — the ORGANIC half of the asymmetry gag. Bright
    #9BF4FF rim, but dialed ~30% off the old neon so the barrel keeps the read."""
    w = pygame.Surface((40, 34), pygame.SRCALPHA)
    body = [(6, 26), (15, 8), (28, 5), (36, 13), (28, 23), (15, 28)]
    pygame.draw.polygon(w, (*WING_ORG, 70), body)
    pygame.draw.polygon(w, (*PULSE, 200), body, 2)          # hero bright edge
    pygame.draw.lines(w, (*NEON, 130), False,
                      [(11, 23), (20, 14), (30, 9)], 1)      # circuit vein
    return pygame.transform.rotate(w, angle_deg)


def _blade_wing(angle_deg):
    """Solid gunmetal fan-blade — the METAL half of the gag. A hard #68707C shape
    ringed by a BRIGHT 2px silver edge (#8FA0B0) so it fans up-and-back as a
    distinct short-wide wing at 40px, selling the organic/metal contrast."""
    w = pygame.Surface((46, 42), pygame.SRCALPHA)
    blade = [(6, 31), (17, 7), (32, 4), (42, 13), (34, 26), (19, 33)]
    pygame.draw.polygon(w, STEEL_D, blade)                  # underside
    pygame.draw.polygon(w, STEEL, [(9, 29), (18, 10), (30, 8),
                                   (37, 15), (30, 24), (19, 29)])
    # Bright silver leading edge, 2px — the light-catch that makes the blade a
    # readable second wing in pure silhouette.
    pygame.draw.lines(w, STEEL_H, False,
                      [(11, 26), (18, 10), (30, 7), (39, 13)], 2)
    for i, sx in enumerate((22, 26, 30)):                   # machined vents
        pygame.draw.line(w, CHASSIS, (sx, 16 + i), (sx - 3, 24 + i), 1)
    return pygame.transform.rotate(w, angle_deg)


def build_volt_wing(wing_angle_deg):
    surf = _new()

    # Per-frame scanning pulse on the NEAR eye only: dim → mid → bright → mid.
    f = (wing_angle_deg + 40) / 90.0
    fi = max(0, min(3, int(round(f * 3))))
    eye_lvl = (0.30, 0.62, 1.0, 0.62)[fi]
    eye_col = tuple(int(NEON[i] + (PULSE[i] - NEON[i]) * eye_lvl)
                    for i in range(3))
    grid_a = int(120 + 135 * eye_lvl)
    glow_a = int(48 + 92 * eye_lvl)                          # ~30% softer bloom

    # ── far mechanical blade wing (behind the body, steeper of the two so metal
    #    vs organic reads as a splayed asymmetric fan) ──
    blade = _blade_wing(wing_angle_deg * 0.5 + 44)
    surf.blit(blade, blade.get_rect(center=(29, 21)).topleft)

    # ── gunmetal barrel body — solid dark-grey blob, hard rim, no edge fuzz.
    #    Values are high enough that this shape reads WITHOUT any cyan help. ──
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

    # Roundness cue: a soft off-centre body-tone highlight (NOT neon) instead of
    # the old cyan seam that split the barrel in two at 40px.
    pygame.draw.line(surf, CAP, (BCX - 4, BCY - 7), (BCX - 4, BCY + 6), 1)

    # Two short steel antenna bristles — dim tips so they don't fight the eyes.
    for sgn, ax in ((-1, 30), (1, 33)):
        tipy = CROWN_Y - 2 - int(f * 2)
        pygame.draw.line(surf, STEEL, (ax, CROWN_Y + 4), (ax + sgn * 2, tipy), 1)
        pygame.draw.circle(surf, STEEL_H, (ax + sgn * 2, tipy), 1)

    # Mechanical labellum nozzle — a small dim nub with a single cyan dot,
    # sitting below and dimmer than the eyes (no glow, no bloom).
    pygame.draw.circle(surf, STEEL_D, (47, 46), 4)
    pygame.draw.circle(surf, CHASSIS, (47, 46), 4, 1)
    pygame.draw.circle(surf, NEON, (47, 46), 1)

    # ── HERO: two hex-eye domes with a DEPTH HIERARCHY ──
    # Far (left) dome first: dim teal, no glow, no bright ring — it recedes.
    fx, fy = EYE_F
    pygame.draw.circle(surf, EYE_BASE, (fx, fy), EYE_R_PX)
    pygame.draw.circle(surf, CHASSIS, (fx, fy), EYE_R_PX, 1)
    for hx, hy in ((fx, fy - 3), (fx - 3, fy), (fx + 3, fy),
                   (fx, fy + 3), (fx - 3, fy + 4), (fx + 3, fy + 4)):
        if (hx - fx) ** 2 + (hy - fy) ** 2 <= (EYE_R_PX - 1) ** 2:
            pygame.draw.lines(surf, (*TEAL_F, 200), True,
                              _hexagon(hx, hy, 2.0), 1)
    pygame.draw.circle(surf, (*PULSE, 120), (fx - 3, fy - 3), 1)  # faint hint

    # Dark gunmetal gutter between the domes so they never bleed into one patch.
    pygame.draw.line(surf, CHASSIS, (GUTTER_X, fy - 5), (GUTTER_X, fy + 5), 2)

    # Near (right) dome: hot cyan, pulsing hex grid, glow + hot specular — wins.
    nx, ny = EYE_N
    _add_glow(surf, nx, ny, EYE_R_PX + 3, eye_col, glow_a)
    pygame.draw.circle(surf, EYE_BASE, (nx, ny), EYE_R_PX)
    pygame.draw.circle(surf, CHASSIS, (nx, ny), EYE_R_PX, 1)
    for hx, hy in ((nx, ny - 3), (nx - 3, ny), (nx + 3, ny),
                   (nx, ny + 3), (nx - 3, ny + 4), (nx + 3, ny + 4)):
        if (hx - nx) ** 2 + (hy - ny) ** 2 <= (EYE_R_PX - 1) ** 2:
            pygame.draw.lines(surf, (*eye_col, grid_a), True,
                              _hexagon(hx, hy, 2.0), 1)
    pygame.draw.circle(surf, WHITE, (nx - 3, ny - 3), 2)
    pygame.draw.circle(surf, (*PULSE, 220), (nx - 1, ny - 1), 1)

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
