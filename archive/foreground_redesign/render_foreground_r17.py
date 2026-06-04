"""Render the round-17 LIVING PROMENADE sheet.

A direction change from rounds 14-16. Instead of presenting the sidewalk
dressing as five separate STYLES, round 17 treats the layers as one promenade
escalating from a sparse pastoral morning to a full night festival, and
populates it with LIVING characters (sheep, dog, kids, an old man, a vendor) so
the world feels inhabited.

  3 BASES (rows)   Terracotta running-bond / Grey-Taupe cool / Warm Honey
                   large-format flagstone
  4 PHASES (cols)  DAY · Pastoral Morning / GOLDEN HOUR · Afternoon Promenade /
                   DUSK · Lamps Lighting / NIGHT · Festival

Every cell keeps the fixed cream pagoda pillar + drifting clouds + parrot + coin
(continuity from r13-r16), composed exactly as render_foreground_r15 does.
Characters are shown as one representative animation frame (a static sheet can't
animate).

Output: docs/foreground_redesign/round_17.png

    SDL_VIDEODRIVER=dummy python archive/foreground_redesign/render_foreground_r17.py
"""
from __future__ import annotations

import os
import pathlib
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

_HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(_HERE))

import pygame

import render_foreground as r13
import foreground_grounded as fg
import promenade_r17 as pr

from game.config import W, H, GROUND_Y

# Reuse the r15 backdrop scroll so the background near-pagoda clears the pillar
# lane (the "doubled-tower" fix) — identical composition to r15.
R17_SCROLL = 20.0

STAGE_PHASE = r13.STAGE_PHASE

# Rows: the three sidewalk BASES under comparison. The third is the Warm Honey
# large-format flagstone — a genuinely different PATTERN (a few big ashlar slabs
# per course) rather than a third running-bond recolor, so the user sees a real
# alternative to the two bond bases.
BASES = [
    ("Terracotta running-bond", fg.fg_brick_running_bond),
    ("Grey-Taupe cool", fg.fg_brick_running_bond_cool),
    ("Warm Honey flagstone", fg.fg_swatch_honey_flagstone),
]

# A per-row representative gait time so the characters strike different poses
# down the sheet (a still frame each).
ROW_T = [0.55, 1.30, 2.05]

# Columns: the four escalating phase-events.
PHASES = [
    ("DAY · Pastoral Morning", STAGE_PHASE["midday"], pr.phase_day),
    ("GOLDEN HOUR · Afternoon Promenade", STAGE_PHASE["golden"], pr.phase_golden),
    ("DUSK · Lamps Lighting", STAGE_PHASE["dusk"], pr.phase_dusk),
    ("NIGHT · Festival", STAGE_PHASE["night"], pr.phase_night),
]

ROW_NOTES = {
    "Terracotta running-bond": "Warm red clay paver bond (fg_brick_running_bond). The known terracotta lead; recessed-dark mortar, vertical-edge bevel only, flush@595.",
    "Grey-Taupe cool": "Cool grey-taupe paver (fg_brick_running_bond_cool). Best night coherence; day value dropped a notch so the walk never competes with the bird lane.",
    "Warm Honey flagstone": "DIFFERENT PATTERN - large-format honey ashlar (fg_swatch_honey_flagstone): 3 deep courses of big slabs, half-block stagger. A real alternative to a running bond.",
}


def _render_cell(floor_painter, phase, phase_painter, t):
    r13.SCROLL = R17_SCROLL
    surf, pal = r13._paint_context(phase)
    floor_painter(surf, W, GROUND_Y, H, R17_SCROLL, pal)
    phase_painter(surf, W, GROUND_Y, H, R17_SCROLL, pal, t)
    r13._add_gameplay_actors(surf)
    return surf


def make_sheet(images):
    tw, th = W, H
    label_h = 30
    row_label_w = 210
    pad = 10
    sheet_w = row_label_w + pad + len(PHASES) * (tw + pad)
    sheet_h = label_h + pad + len(BASES) * (th + pad)
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((20, 20, 24))

    title = pygame.font.SysFont(None, 24)
    head = pygame.font.SysFont(None, 24)
    name_f = pygame.font.SysFont(None, 26)
    note_f = pygame.font.SysFont(None, 18)
    cap_f = pygame.font.SysFont(None, 22)

    t = title.render(
        "FOREGROUND REDESIGN - round 17 - LIVING PROMENADE. ROWS = sidewalk BASE (undecided: Terracotta / Grey-Taupe / Honey flagstone), "
        "COLS = time-of-day EVENT escalating sparse DAY -> full NIGHT festival, each populated with LIVING characters (sheep/dog/kids/old-man/vendor/strollers). "
        "Night glow capped under the coin + gated to a dark sky; DAY/GOLDEN unlit. Fixed cream pagoda + clouds + parrot + coin in every cell.",
        True, (245, 235, 210))
    sheet.blit(t, (8, 8))

    for c, (pname, _, _) in enumerate(PHASES):
        x = row_label_w + pad + c * (tw + pad)
        lbl = head.render(pname, True, (255, 236, 180))
        sheet.blit(lbl, (x + tw // 2 - lbl.get_width() // 2, 6))

    for r, (rname, _) in enumerate(BASES):
        y = label_h + pad + r * (th + pad)
        sheet.blit(name_f.render(rname.split(" ")[0], True, (255, 224, 150)), (8, y + 10))
        note = ROW_NOTES.get(rname, "")
        ly = y + 36
        nline = ""
        for word in note.split():
            test = (nline + " " + word).strip()
            if note_f.size(test)[0] > row_label_w - 14 and nline:
                sheet.blit(note_f.render(nline, True, (180, 180, 188)), (8, ly))
                ly += 16
                nline = word
            else:
                nline = test
        if nline:
            sheet.blit(note_f.render(nline, True, (180, 180, 188)), (8, ly))

        for c, (pname, _, _) in enumerate(PHASES):
            full = images[(rname, pname)]
            x = row_label_w + pad + c * (tw + pad)
            sheet.blit(full, (x, y))
            cap = cap_f.render(pname.split(" · ")[0], True, (250, 250, 250))
            bg = pygame.Surface((cap.get_width() + 8, cap.get_height() + 4), pygame.SRCALPHA)
            bg.fill((0, 0, 0, 120))
            sheet.blit(bg, (x + 4, y + 4))
            sheet.blit(cap, (x + 8, y + 6))

    return sheet


def main():
    images = {}
    for ri, (rname, floor_painter) in enumerate(BASES):
        for cname, phase, phase_painter in PHASES:
            images[(rname, cname)] = _render_cell(
                floor_painter, phase, phase_painter, ROW_T[ri])

    sheet = make_sheet(images)
    out = _HERE.parent.parent / "docs" / "foreground_redesign"
    out.mkdir(parents=True, exist_ok=True)
    path = out / "round_17.png"
    pygame.image.save(sheet, path)
    print(f"wrote {path}  ({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    main()
