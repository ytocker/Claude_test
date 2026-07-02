"""MOSQUITO candidate — DESIGN 4 · VAMPING FANG (scratch exploration only).

Gothic-horror "just bit you" mosquito. Silhouette does the whole job at 40px:
a long forward FANG needle and three crooked spider legs dangling wide are the
two non-negotiable tells, hung on a hunched inverted-V body whose swollen
crimson blood-belly sags low-back off a near-black thorax. Every near-black
element carries a cool sky-side rim so the whole shape survives night sky.
Scratch candidate — never registered in BUILDERS / catalog. Wrapped by the
local `_make_prebuilt_skin` so `tools/ninja_render.py` can pose it in a real
gameplay scene exactly like the shipped skins.
"""
import pygame
import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
pygame.init()

from game.parrot import _WING_ANGLES, _add_outline, _aaellipse
from game.animal_skins import (
    _make_prebuilt_skin, COMPOSITE_W, COMPOSITE_H, BCX, BCY, HCX, HCY, _new)

BLACKBERRY   = (26, 10, 14)      # #1A0A0E glossy near-black fang / head / legs
THORAX_DK    = (58, 42, 46)      # #3A2A2E dark thorax hump — reads darker than belly
DARK_BLOOD   = (110, 15, 28)     # #6E0F1C banding / wing membrane / sky-side rim
BRIGHT_BLOOD = (216, 30, 52)     # #D81E34 gorged blood-belly — the HERO focal
GLINT        = (232, 184, 190)   # #E8B8BE cold highlight — the ONE bright point
DIM_SHEEN    = (118, 92, 96)     # ~50% value of GLINT — soft belly sheen, no 2nd eye
SPECULAR     = (96, 62, 68)      # glossy top ridge on the near-black fang


def _vamp_wing(angle_deg, alpha):
    """A long translucent mid-red blade. It is deliberately longer than the body
    so, arced up-back, its far end pokes past the outline and NOTCHES the
    silhouette instead of filling the back hump."""
    w = pygame.Surface((46, 18), pygame.SRCALPHA)
    pygame.draw.ellipse(w, (*DARK_BLOOD, alpha), (0, 3, 46, 12))
    pygame.draw.ellipse(w, (*BRIGHT_BLOOD, alpha // 2), (7, 5, 26, 8))
    pygame.draw.ellipse(w, (*DARK_BLOOD, min(255, alpha + 70)), (0, 3, 46, 12), 1)
    pygame.draw.line(w, (*DARK_BLOOD, min(255, alpha + 40)), (7, 9), (40, 8), 1)
    return pygame.transform.rotate(w, angle_deg)


def _leg(surf, hip, knee, foot):
    """One long crooked leg: a thicker thigh, a kinked knee, then a hair-thin
    shin. The kink is what reads as SPIDER rather than antenna. A 1px sky-side
    (upper-left) rim in dim blood-red keeps the black leg alive on night sky."""
    pygame.draw.line(surf, BLACKBERRY, hip, knee, 2)
    pygame.draw.line(surf, BLACKBERRY, knee, foot, 1)
    rim = [(hip[0] - 1, hip[1]), (knee[0] - 1, knee[1]), (foot[0] - 1, foot[1])]
    pygame.draw.lines(surf, DARK_BLOOD, False, rim, 1)


def _rim_arc(surf, center, rx, ry, color, start, stop):
    """A thin night-sky guard along the upper-left contour of a near-black mass
    so the full mosquito silhouette survives against dark sky."""
    cx, cy = center
    rect = pygame.Rect(int(cx - rx), int(cy - ry), int(rx * 2), int(ry * 2))
    pygame.draw.arc(surf, color, rect, start, stop, 1)


def build_mosquito_vamp(wing_angle_deg):
    surf = _new()
    f = (wing_angle_deg + 40) / 90.0            # 0..1 wing-up factor
    swing = int((f - 0.5) * 5)                   # legs sway with the beat

    # ── Far wing, faint, tucked behind so the near wing leads the read. ──
    fw = _vamp_wing(44 + (f - 0.5) * 34, 70)
    surf.blit(fw, fw.get_rect(center=(30, 20)))

    # ── Legs BEHIND the body: three per side in a wide drooping spider spread,
    #    tips fanning from x18 to x52 and dangling past y66. Each is kinked. ──
    s = swing
    _leg(surf, (27, 45), (20, 57), (18, 72 + s))     # rear (leftmost)
    _leg(surf, (30, 46), (25, 59), (24, 74 + s))
    _leg(surf, (33, 47), (32, 60), (33, 73 + s))     # mid drop
    _leg(surf, (37, 46), (41, 58), (43, 71 - s))
    _leg(surf, (40, 45), (47, 56), (49, 69 - s))
    _leg(surf, (42, 44), (50, 54), (52, 67 - s))     # front (rightmost)

    # ── Abdomen: the HERO — a swollen gorged blood-bead sagging LOW-BACK off a
    #    dark waist, so the body forms a hunched inverted-V with the thorax. ──
    petiole = [(30, 40), (34, 41), (30, 48), (26, 47)]
    pygame.draw.polygon(surf, BLACKBERRY, petiole)   # dark waist it hangs from
    _aaellipse(surf, DARK_BLOOD, (21, 51), 13, 11)   # engorged rim
    _aaellipse(surf, BRIGHT_BLOOD, (21, 50), 10, 8)  # bright-blood core
    # Curved dark bands cinch the taut belly into full-blood segments.
    pygame.draw.lines(surf, DARK_BLOOD, False, [(13, 47), (15, 52), (15, 58)], 1)
    pygame.draw.lines(surf, DARK_BLOOD, False, [(19, 44), (22, 51), (22, 59)], 1)
    pygame.draw.lines(surf, DARK_BLOOD, False, [(26, 46), (28, 52), (28, 57)], 1)
    _aaellipse(surf, DIM_SHEEN, (16, 45), 3, 2)      # soft sheen — NOT a 2nd eye
    _rim_arc(surf, (21, 51), 13, 11, DARK_BLOOD, 1.9, 3.5)

    # ── Thorax: a high, hunched, near-black hump — the PEAK of the inverted-V,
    #    pushed dark so the crimson belly reads as a separate bead below it. ──
    _aaellipse(surf, BLACKBERRY, (34, 38), 10, 11)
    _aaellipse(surf, THORAX_DK, (33, 35), 6, 5)      # faint top form
    _rim_arc(surf, (34, 38), 10, 11, GLINT, 2.0, 3.4)

    # ── Bristle-crown: a minimal raised nub on the thorax top edge with a cold
    #    tick, just enough to break the top contour (the old ruff vanished). ──
    for bx in (30, 33, 36):
        pygame.draw.line(surf, THORAX_DK, (bx, 27), (bx, 24), 2)
    pygame.draw.circle(surf, GLINT, (33, 24), 1)

    # ── Head, tucked up-forward at the peak, near-black with sky-side rim. ──
    _aaellipse(surf, BLACKBERRY, (44, 35), 8, 8)
    _rim_arc(surf, (44, 35), 8, 8, GLINT, 2.1, 3.6)

    # ── Blood-red compound eye with the single cold catchlight: THE bright pt. ──
    _aaellipse(surf, DARK_BLOOD, (45, 33), 6, 6)
    _aaellipse(surf, BRIGHT_BLOOD, (45, 32), 4, 4)
    pygame.draw.circle(surf, GLINT, (43, 31), 2)

    # ── Proboscis: the FANG — a long straight forward needle, ~18px, stabbing
    #    down-forward off the head. Glossy near-black with a specular top streak
    #    and a white glint at the very tip. Mosquito is 40% beak — commit. ──
    tip = (63, 44)
    pygame.draw.line(surf, BLACKBERRY, (46, 38), tip, 3)
    pygame.draw.line(surf, SPECULAR, (46, 37), (60, 42), 1)   # glossy top ridge
    pygame.draw.circle(surf, GLINT, tip, 1)                    # white tip glint

    # ── Near wing over the thorax, arced up-back, its tip notching the top. ──
    nw = _vamp_wing(52 + (f - 0.5) * 46, 130)
    surf.blit(nw, nw.get_rect(center=(24, 22)))

    return surf


build = _make_prebuilt_skin(build_mosquito_vamp)


if __name__ == "__main__":
    # Standalone render of the exploration sheet: hero | day | night.
    import tools.ninja_render as nr

    hero = nr.hero_panel(build, 220)
    panel_day = nr.gameplay_panel(build, 220, 392)
    panel_night = nr.gameplay_panel(build, 220, 392, frame_idx=0, tilt=-8.0)

    pad = 14
    title_h = 46
    pw = 220
    sheet_w = pad * 4 + pw * 3
    sheet_h = title_h + pad * 2 + 392
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((18, 14, 22))

    font = pygame.font.SysFont("dejavusans", 22, bold=True)
    label_font = pygame.font.SysFont("dejavusans", 14)
    title = font.render("DESIGN 4 — VAMPING FANG", True, (232, 184, 190))
    sheet.blit(title, (pad, pad + 4))

    y = title_h + pad
    for i, (panel, name) in enumerate((
            (hero, "hero"), (panel_day, "day flight"),
            (panel_night, "night flight"))):
        x = pad + i * (pw + pad)
        # Vertically centre the square hero against the tall gameplay panels.
        py = y + (392 - panel.get_height()) // 2
        sheet.blit(panel, (x, py))
        lab = label_font.render(name, True, (200, 200, 210))
        sheet.blit(lab, (x, y + 392 + 2))

    repo_root = os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))))
    out = os.path.join(
        repo_root, "docs", "store_redesign", "animal", "mosquito",
        "design_4", "round_1.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("wrote", out)
