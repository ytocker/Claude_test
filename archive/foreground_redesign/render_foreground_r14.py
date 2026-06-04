"""Render the round-14 SIDEWALK-DRESSING sheet.

Round 13 locked the sidewalk material; round 14 dresses it with promenade
furniture (street lamps, benches, festive lantern/light strings, planters,
greenery). The grid is restructured from the round-13 (swatch × phase) layout
to (dressing STYLE × (base, phase)):

  COLUMNS (4) — two bases × day/night, dropping sunset/dusk so the night-glow
                payoff is front-and-centre:
                  Grey-Taupe · DAY   (fg_brick_running_bond_cool)
                  Grey-Taupe · NIGHT
                  Terracotta · DAY   (fg_brick_running_bond)
                  Terracotta · NIGHT
  ROWS (5)    — the mixed range of dressing styles (sidewalk_props.STYLES_R14):
                  Temple Festival / Holiday Lights / Serene Garden /
                  Elegant Minimal / The Works.

Every cell keeps the round-13 context: misty_gorge sky + gorge mist + drifting
clouds + V14 mountains + the FIXED cream pagoda pillar pair, then the floor
(base painter), then the props layer, then the parrot + scrolling coin.

Output: docs/foreground_redesign/round_14.png

    SDL_VIDEODRIVER=dummy python archive/foreground_redesign/render_foreground_r14.py
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

# Reuse the round-13 harness' context painter + actor placement wholesale, so
# the backdrop / pagoda / clouds / parrot+coin are byte-identical to round 13.
import render_foreground as r13
import foreground_grounded as fg
import sidewalk_props as sp

from game.config import W, H, GROUND_Y


# ── columns: two bases × day/night ────────────────────────────────────────────
STAGE_PHASE = r13.STAGE_PHASE
SCROLL = r13.SCROLL

BASES = [
    ("Grey-Taupe", fg.fg_brick_running_bond_cool),
    ("Terracotta", fg.fg_brick_running_bond),
]
PHASES = [("DAY", STAGE_PHASE["midday"]), ("NIGHT", STAGE_PHASE["night"])]

# Flatten to 4 columns in the requested order: GT-day, GT-night, TC-day, TC-night.
COLUMNS = []
for bname, painter in BASES:
    for pname, phase in PHASES:
        COLUMNS.append((f"{bname} · {pname}", painter, phase))

ROWS = sp.STYLES_R14

ROW_NOTES = {
    "Temple Festival": "Ornate iron lamp posts + red/gold paper-lantern garland (catenary) + prayer-flag bunting + bench + planter. The temple-festival promenade.",
    "Holiday Lights": "Warm fairy-light bunting + a wreathed post + a classic park bench + potted mini-evergreens. Cosy holiday string-lights read.",
    "Serene Garden": "Dim stone lamp + planters + a cascading vine + a cairn + a bench. Minimal festivity, natural and contemplative.",
    "Elegant Minimal": "ONE refined ornate glass lamp post + a bench + a touch of greenery. Sparse, premium, uncluttered.",
    "The Works": "Lamp posts + lantern garland + bench + planters + cairn — dense-but-tasteful, the fully-dressed promenade. Likely shippable.",
}


def _render_cell(floor_painter, props_painter, phase):
    surf, pal = r13._paint_context(phase)
    floor_painter(surf, W, GROUND_Y, H, SCROLL, pal)
    props_painter(surf, W, GROUND_Y, H, SCROLL, pal)
    r13._add_gameplay_actors(surf)
    return surf


def make_sheet(images):
    tw, th = W, H
    label_h = 30
    row_label_w = 210
    pad = 10
    sheet_w = row_label_w + pad + len(COLUMNS) * (tw + pad)
    sheet_h = label_h + pad + len(ROWS) * (th + pad)
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((20, 20, 24))

    title = pygame.font.SysFont(None, 24)
    head = pygame.font.SysFont(None, 26)
    name_f = pygame.font.SysFont(None, 26)
    note_f = pygame.font.SysFont(None, 18)
    cap_f = pygame.font.SysFont(None, 22)

    t = title.render(
        "FOREGROUND REDESIGN - round 14 - DRESS THE SIDEWALK. ROWS = dressing styles, COLS = base (Grey-Taupe / Terracotta) x phase (DAY / NIGHT). "
        "Props built from existing game/ primitives, world-anchored scroll, bird-lane kept quiet. NIGHT glow capped @ luma<=153 + gated to dark sky - coin stays brightest.",
        True, (245, 235, 210))
    sheet.blit(t, (8, 8))

    for c, (pname, _, _) in enumerate(COLUMNS):
        x = row_label_w + pad + c * (tw + pad)
        lbl = head.render(pname, True, (240, 240, 240))
        sheet.blit(lbl, (x + tw // 2 - lbl.get_width() // 2, 6))

    for r, (rname, _) in enumerate(ROWS):
        y = label_h + pad + r * (th + pad)
        sheet.blit(name_f.render(rname, True, (255, 224, 150)), (8, y + 10))
        note = ROW_NOTES.get(rname, "")
        ly = y + 38
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

        for c, (pname, _, _) in enumerate(COLUMNS):
            full = images[(rname, pname)]
            x = row_label_w + pad + c * (tw + pad)
            sheet.blit(full, (x, y))
            cap = cap_f.render(f"{rname} - {pname}", True, (250, 250, 250))
            bg = pygame.Surface((cap.get_width() + 8, cap.get_height() + 4), pygame.SRCALPHA)
            bg.fill((0, 0, 0, 120))
            sheet.blit(bg, (x + 4, y + 4))
            sheet.blit(cap, (x + 8, y + 6))

    return sheet


def main():
    images = {}
    for rname, props_painter in ROWS:
        for cname, floor_painter, phase in COLUMNS:
            images[(rname, cname)] = _render_cell(floor_painter, props_painter, phase)

    sheet = make_sheet(images)
    out = _HERE.parent.parent / "docs" / "foreground_redesign"
    out.mkdir(parents=True, exist_ok=True)
    path = out / "round_14.png"
    pygame.image.save(sheet, path)
    print(f"wrote {path}  ({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    main()
