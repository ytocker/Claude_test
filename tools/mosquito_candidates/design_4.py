"""MOSQUITO candidate — DESIGN 4 · VAMPING FANG (scratch exploration only).

Gothic-horror "just bit you" mosquito: a swollen crimson blood-belly is the
hero beat, a glossy near-black fang proboscis and a wide drooping spider stance
sell the menace. Scratch candidate — never registered in BUILDERS / catalog.
Wrapped by the local `_make_prebuilt_skin` so `tools/ninja_render.py` can pose
it in a real gameplay scene exactly like the shipped skins.
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

BLACKBERRY   = (26, 10, 14)      # near-black body / legs / fang
DARK_BLOOD   = (110, 15, 28)     # belly rim + smoky wing
BRIGHT_BLOOD = (216, 30, 52)     # gorged belly core
GLINT        = (232, 184, 190)   # cold highlight specks
RUFF         = (58, 42, 46)      # raised collar scales


def _vamp_wing(angle_deg):
    """A smoky dark-red translucent blade. The flap is a broad motion (unlike
    the bee's damped buzz) so the threatening wing arc reads at 40px."""
    w = pygame.Surface((36, 22), pygame.SRCALPHA)
    pygame.draw.ellipse(w, (*DARK_BLOOD, 100), (2, 4, 32, 14))
    pygame.draw.ellipse(w, (*BRIGHT_BLOOD, 90), (5, 6, 22, 10))
    pygame.draw.ellipse(w, (*DARK_BLOOD, 170), (2, 4, 32, 14), 1)
    # A single vein line keeps the membrane from reading as a flat blob.
    pygame.draw.line(w, (*DARK_BLOOD, 150), (8, 11), (30, 9), 1)
    return pygame.transform.rotate(w, angle_deg)


def _leg(surf, hip, knee, foot):
    """One long crooked BLACKBERRY leg with a distinct knee bend, tapering to a
    hair-thin ankle so the six-leg rig stays spindly, not stumpy."""
    pygame.draw.line(surf, BLACKBERRY, hip, knee, 2)
    pygame.draw.line(surf, BLACKBERRY, knee, foot, 1)


def build_mosquito_vamp(wing_angle_deg):
    surf = _new()
    f = (wing_angle_deg + 40) / 90.0            # 0..1 wing-up factor
    swing = (f - 0.5) * 6                        # legs sway with the beat

    # ── Far wing tucked behind, damped so the near wing leads the read. ──
    fw = _vamp_wing(38 + (f - 0.5) * 40)
    surf.blit(fw, fw.get_rect(center=(BCX + 12, BCY - 12)))

    # ── Legs first (behind the body): wide drooping spider stance. The three
    #    on each side splay forward/mid/back and dangle low, swaying with f. ──
    s = int(swing)
    # rear pair
    _leg(surf, (22, 46), (18, 54), (14, 62 + s))
    _leg(surf, (24, 47), (21, 57), (16, 66 + s))
    # mid pair (near-vertical drop)
    _leg(surf, (32, 48), (33, 56), (33, 64 + s))
    _leg(surf, (34, 49), (36, 58), (37, 67 + s))
    # front pair reaching forward-down
    _leg(surf, (40, 46), (46, 53), (50, 62 - s))
    _leg(surf, (41, 48), (47, 56), (52, 66 - s))

    # ── Abdomen: the HERO — a swollen, gorged blood-belly slung low-left. ──
    _aaellipse(surf, DARK_BLOOD, (24, 49), 14, 10)          # full rim
    _aaellipse(surf, BRIGHT_BLOOD, (24, 48), 9, 7)          # engorged core
    _aaellipse(surf, GLINT, (20, 44), 3, 2)                 # cold wet gleam
    # Dark banding cinches the taut belly into segments.
    for bx in (17, 24, 31):
        pygame.draw.line(surf, BLACKBERRY, (bx, 41), (bx - 2, 56), 1)

    # ── Thorax: a high arched BLACKBERRY hump — exaggerated hunch. ──
    _aaellipse(surf, BLACKBERRY, (BCX + 2, BCY - 3), 11, 12)
    _aaellipse(surf, (46, 22, 28), (BCX, BCY - 6), 6, 5)    # top rim-light

    # ── Ruff/collar: raised scale spikes at the neck for the caped-villain
    #    silhouette. ──
    for i, (rx, ry) in enumerate(((38, 40), (40, 42), (42, 40), (40, 38))):
        tip = (rx + (i - 1) * 2, ry - 5)
        pygame.draw.polygon(surf, RUFF,
                            [(rx - 2, ry + 2), (rx + 2, ry + 2), tip])

    # ── Head + blood-red compound eye with a cold catchlight. ──
    _aaellipse(surf, BLACKBERRY, (HCX, HCY), 9, 9)
    _aaellipse(surf, DARK_BLOOD, (HCX, HCY), 8, 8)
    _aaellipse(surf, BRIGHT_BLOOD, (HCX - 1, HCY - 1), 5, 5)
    pygame.draw.circle(surf, GLINT, (HCX - 3, HCY - 3), 2)  # cold catchlight

    # ── Proboscis: the FANG — a thick near-black needle drooping to a tip. A
    #    short curve (three segments) gives the downward hook a feeding tool
    #    would have; a white tip glint sharpens the point. ──
    fang = [(44, 37), (52, 38), (58, 39), (63, 40)]
    pygame.draw.lines(surf, BLACKBERRY, False, fang, 2)
    pygame.draw.lines(surf, (58, 30, 36), False,
                      [(44, 36), (52, 37)], 1)            # glossy top ridge
    pygame.draw.circle(surf, (255, 255, 255), (63, 40), 1)

    # ── Near wing over the thorax leads the flap read. ──
    nw = _vamp_wing(30 + (f - 0.5) * 60)
    surf.blit(nw, nw.get_rect(center=(BCX - 2, BCY - 13)))

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
