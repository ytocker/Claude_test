"""Render the round-18 EMBEDDED PAVING DETAIL sheet.

Round 17 (LIVING PROMENADE) dressed the walk with props + living characters ON
TOP of the floor. Round 18 adds the missing read the user asked for:
environmental detail embedded INTO the paving SURFACE itself — the ~45px floor
body (y=595..640) — beneath the r17 promenade. A NEW ground-surface detail layer
rides the floor scroll and reads as PART of the ground: hairline cracks tracking
the bond, weeds from mortar gaps, moss at joints, fallen leaves + pebbles, an
inlaid medallion on the honey slabs, a storm grate, and after-rain damp.

Everything from r17 (the 3 bases + the promenade props + characters + lights) is
preserved EXACTLY; this only INSERTS one embedded-detail call BETWEEN the base
floor painter and the phase/props painter, so the detail sits in the floor and
under the props.

  3 BASES (rows)   Terracotta running-bond / Grey-Taupe cool / Warm Honey
                   large-format flagstone
  4 PHASES (cols)  DAY · Pastoral Morning / GOLDEN HOUR · Afternoon Promenade /
                   DUSK · Lamps Lighting / NIGHT · Festival

Output: docs/foreground_redesign/round_18.png

    SDL_VIDEODRIVER=dummy python archive/foreground_redesign/render_foreground_r18.py
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
import ground_detail_r18 as gd

from game.config import W, H, GROUND_Y

# Reuse the r17/r15 backdrop scroll so the composition is identical to r17.
R17_SCROLL = 20.0

STAGE_PHASE = r13.STAGE_PHASE

BASES = [
    ("Terracotta running-bond", fg.fg_brick_running_bond),
    ("Grey-Taupe cool", fg.fg_brick_running_bond_cool),
    ("Warm Honey flagstone", fg.fg_swatch_honey_flagstone),
]

ROW_T = [0.55, 1.30, 2.05]

PHASES = [
    ("DAY · Pastoral Morning", STAGE_PHASE["midday"], pr.phase_day),
    ("GOLDEN HOUR · Afternoon Promenade", STAGE_PHASE["golden"], pr.phase_golden),
    ("DUSK · Lamps Lighting", STAGE_PHASE["dusk"], pr.phase_dusk),
    ("NIGHT · Festival", STAGE_PHASE["night"], pr.phase_night),
]

ROW_NOTES = {
    "Terracotta running-bond": "Warm worn clay walk. Embedded: ochre fallen leaves + pebbles, weeds from the mortar gaps, hairline bond-tracking cracks, a storm grate. All pinned to real joints, densest in the front courses.",
    "Grey-Taupe cool": "Shaded damp stone walk. Embedded: heavier moss/lichen at joints + after-rain damp patches (lean into dusk/night), grey pebbles, sparse weeds + grate. Cool retint; quiet behind the lanes.",
    "Warm Honey flagstone": "Dressed temple slabs. Embedded: an INLAID beveled diamond medallion on a big slab (the hero), sparse weeds + warm-tan leaves, fewer cracks - the premium read for the large-format ashlar.",
}


def _render_cell(floor_painter, phase, phase_painter, t):
    r13.SCROLL = R17_SCROLL
    surf, pal = r13._paint_context(phase)
    floor_painter(surf, W, GROUND_Y, H, R17_SCROLL, pal)
    # NEW for r18: embedded ground-surface detail, painted into the floor body
    # AFTER the base paving and BEFORE the promenade props/characters so it reads
    # as part of the ground, beneath everything else.
    gd.add_embedded_detail(floor_painter, surf, W, GROUND_Y, H, R17_SCROLL, pal)
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
        "FOREGROUND REDESIGN - round 18 - EMBEDDED PAVING DETAIL. Same 3 BASES x 4 PHASES + the r17 promenade (props/characters/lights) UNCHANGED, "
        "now with a NEW ground-surface detail layer painted INTO the floor body (y=595-640) BENEATH the props: cracks tracking the bond, weeds from mortar gaps, "
        "moss at joints, fallen leaves/pebbles, an inlaid medallion (honey), a storm grate, after-rain damp. World-anchored to the real joints; quiet behind the lanes; "
        "night-retinted with no glow (detail stays darker than the coin).",
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
    path = out / "round_18.png"
    pygame.image.save(sheet, path)
    print(f"wrote {path}  ({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    main()
