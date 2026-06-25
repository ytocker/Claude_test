"""Compose the v4 design_5 (ETCHED WOODCUT) review sheet (scratch).

Adds a HATCH-OFF proof: the bare bold-contour skeleton (engrave pass skipped)
at 40px, so the round-2 rule — the skeleton must read with the hatch turned off
— is verified visually on the sheet itself.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from tools import ninja_render as NR
from tools.skeleton_candidates import v4_design_5 as D5
from tools.skeleton_candidates import _v4_xray_base as XB
from tools.skeleton_candidates.v4_design_5 import build

OUT = "docs/store_redesign/costume/skeleton/v4/design_5/round_2.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)

font = pygame.font.SysFont("dejavusans", 16, bold=True)
small = pygame.font.SysFont("dejavusans", 13)


def label(surf, text, x, y, col=(230, 232, 240)):
    surf.blit(small.render(text, True, (8, 8, 12)), (x + 1, y + 1))
    surf.blit(small.render(text, True, col), (x, y))


def truth40(builder):
    """Scale a builder's mid-flight frame to 40px wide (nearest), upscale x5."""
    src = builder(2, 10.0)
    bb = src.get_bounding_rect()
    src = src.subsurface(bb).copy() if bb.width else src
    sw, sh = src.get_size()
    t40 = pygame.transform.scale(src, (40, max(1, int(40 * sh / sw))))
    tw, th = t40.get_size()
    return pygame.transform.scale(t40, (tw * 5, th * 5))


# Hatch-OFF builder: same paint minus the engrave pass, to prove the contours
# alone carry the skeleton.
def _paint_no_hatch(surf, angle):
    XB.paint_skeleton(surf, angle, style=D5.STYLE)
    D5._beak_hero(surf)


build_no_hatch = XB._frames_from_paint(_paint_no_hatch)


# Panels.
hero = NR.hero_panel(build, 360)
day = NR.gameplay_panel(build, 220, 392)

# NIGHT: bird on a dark navy fill.
night = pygame.Surface((220, 200), pygame.SRCALPHA)
night.fill((18, 20, 34))
nf = build(2, 10.0)
night.blit(nf, nf.get_rect(center=(110, 100)))

truth = truth40(build)
truth_off = truth40(build_no_hatch)

# ── compose sheet ────────────────────────────────────────────────────────────
SW, SH = 900, 540
sheet = pygame.Surface((SW, SH))
sheet.fill((20, 21, 30))   # ink-plate background

sheet.blit(font.render("v4 SKELETON · design_5 — ETCHED WOODCUT (round 2)",
                       True, (236, 238, 246)), (16, 12))
label(sheet, "bold white line-art bones carry the read · dim sparse hatch is tone only · "
             "thick 3px hooked beak-bone hero · understroke for day clouds", 16, 36)

# Hero (large product shot).
sheet.blit(hero, (16, 64))
label(sheet, "HERO — bold contours, hatch as tone", 16, 64 + 360 + 4)

# Day gameplay.
sheet.blit(day, (400, 64))
label(sheet, "DAY gameplay (over clouds)", 400, 64 + 392 + 4)

# Right column: night, then the two 40px truth reads (hatch ON vs OFF).
sheet.blit(night, (640, 64))
label(sheet, "NIGHT navy fill", 640, 64 + 200 + 4)

sheet.blit(truth, (640, 300))
label(sheet, "40px TRUTH (x5) — hatch ON", 640, 300 + truth.get_height() + 2)

sheet.blit(truth_off, (640, 410))
label(sheet, "40px PROOF (x5) — hatch OFF: skeleton must still read",
      640, 410 + truth_off.get_height() + 2)

pygame.image.save(sheet, OUT)
print("wrote", OUT, sheet.get_size())
