"""Render the round-15 SIDEWALK-DRESSING sheet (composition pass over r14).

Same grid as r14 — 5 dressing STYLES (rows) × (base × phase) columns:

  COLUMNS (4)  Grey-Taupe · DAY / Grey-Taupe · NIGHT /
               Terracotta · DAY / Terracotta · NIGHT
  ROWS (5)     Temple Festival / Holiday Lights / Serene Garden /
               Elegant Minimal / The Works  (sidewalk_props_r15.STYLES_R15)

The r14 verdict was ITERATE — concept + night-glow cap good, silhouette /
composition needed surgery. Two things change here vs the r14 harness:

  * WORLD SCROLL is moved to R15_SCROLL so the dark BACKGROUND near-pagoda (a
    mountain-band silhouette, not a prop) no longer abuts the cream pillar's
    left shoulder — the "doubled-tower". At this scroll the pillar lane reads as
    clean sky to the pillar's left.
  * The props come from sidewalk_props_r15 (posts pulled out of the bird lane +
    shortened, fairy-lights simplified, serene night-core, truly-minimal Elegant
    row, prayer-flags cut).

Everything else — misty_gorge sky, gorge mist, clouds, V14 mountains, the FIXED
cream pagoda pillar pair, the parrot + scrolling coin — is byte-identical to the
r13/r14 context painter.

Output: docs/foreground_redesign/round_15.png

    SDL_VIDEODRIVER=dummy python archive/foreground_redesign/render_foreground_r15.py
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
import sidewalk_props_r15 as sp

from game.config import W, H, GROUND_Y


# A scroll where the background near-pagodas clear the WHOLE playfield band
# (pillar lane AND the bird/coin corridor), leaving clean sky around the cream
# pillar — the "doubled-tower" fix. Verified by scanning the pagoda band for
# near-black columns across x≈70..250.
R15_SCROLL = 20.0

STAGE_PHASE = r13.STAGE_PHASE

BASES = [
    ("Grey-Taupe", fg.fg_brick_running_bond_cool),
    ("Terracotta", fg.fg_brick_running_bond),
]
PHASES = [("DAY", STAGE_PHASE["midday"]), ("NIGHT", STAGE_PHASE["night"])]

COLUMNS = []
for bname, painter in BASES:
    for pname, phase in PHASES:
        COLUMNS.append((f"{bname} · {pname}", painter, phase))

ROWS = sp.STYLES_R15

ROW_NOTES = {
    "Temple Festival": "Ornate iron lamp posts (short, out of the bird lane) + red/gold paper-lantern garland. Prayer-flags CUT — garland carries the festive read. Bench + planter.",
    "Holiday Lights": "ONE clean fairy-light catenary: fewer, larger, brighter bulbs. Simplified glass-lantern post (no wreath). Classic bench + potted mini-evergreens.",
    "Serene Garden": "Stone lamp now keeps a small present-but-dim warm core at night. Chunky barrel-planter at far left + a larger cairn + a cascading vine + a bench.",
    "Elegant Minimal": "ACTUALLY minimal — exactly ONE refined glass-lantern lamp + ONE bench + ONE small planter. Negative space sells the elegance.",
    "The Works": "Lamp posts (short) + lantern garland + bench + planters + a far-left cairn — dense-but-tasteful promenade. Likely shippable.",
}


def _render_cell(floor_painter, props_painter, phase):
    # Hold the harness scroll so the shared context painter places the backdrop
    # (incl. the background pagodas) clear of the pillar lane.
    r13.SCROLL = R15_SCROLL
    surf, pal = r13._paint_context(phase)
    floor_painter(surf, W, GROUND_Y, H, R15_SCROLL, pal)
    props_painter(surf, W, GROUND_Y, H, R15_SCROLL, pal)
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
        "FOREGROUND REDESIGN - round 15 - DRESS THE SIDEWALK (composition pass). ROWS = dressing styles, COLS = base (Grey-Taupe / Terracotta) x phase (DAY / NIGHT). "
        "Doubled-tower cleared (backdrop scroll), posts pulled out of the bird lane + shortened, fairy-lights simplified, serene night-core added, Elegant row truly minimal. NIGHT glow capped - coin stays brightest.",
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
    path = out / "round_15.png"
    pygame.image.save(sheet, path)
    print(f"wrote {path}  ({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    main()
