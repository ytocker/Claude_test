"""Render the round-19 NEAR / FRONT ACTIVITY LANE sheet.

Rounds 17 (promenade) + 18 (embedded surface detail) dressed the FAR edge of the
sidewalk (the r17 cast stands at GROUND_Y=595). Round 19 uses the sidewalk's
DEPTH: it adds a SECOND, NEARER lane of life on the FRONT edge (feet near the
screen bottom, ~y=636-640), drawn LARGER and with FASTER parallax so it occludes
the far lane and reads as a busy promenade at multiple distances — people
crossing nearer the camera, the dog trotting across the front, potted plants +
on-theme ornaments, and a LIVE STREET PERFORMANCE spread across the day cycle
(acrobat by day -> musician+crowd at golden hour -> performers prep at dusk ->
the full lion dance at the night festival).

Everything from r17 + r18 is preserved EXACTLY; this only INSERTS one near-lane
call AFTER the phase/props painter and BEFORE the gameplay actors, so the near
lane sits in front of the far lane while the parrot + coin stay on top.

  3 BASES (rows)   Terracotta running-bond / Grey-Taupe cool / Warm Honey
                   large-format flagstone
  4 PHASES (cols)  DAY · Pastoral Morning / GOLDEN HOUR · Afternoon Promenade /
                   DUSK · Lamps Lighting / NIGHT · Festival

Output: docs/foreground_redesign/round_19.png

    SDL_VIDEODRIVER=dummy python archive/foreground_redesign/render_foreground_r19.py
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
import near_lane_r19 as nl

from game.config import W, H, GROUND_Y

# Reuse the r17/r15 backdrop scroll so the composition is identical to r17/r18.
R17_SCROLL = 20.0

STAGE_PHASE = r13.STAGE_PHASE

BASES = [
    ("Terracotta running-bond", fg.fg_brick_running_bond),
    ("Grey-Taupe cool", fg.fg_brick_running_bond_cool),
    ("Warm Honey flagstone", fg.fg_swatch_honey_flagstone),
]

ROW_T = [0.55, 1.30, 2.05]

# Each phase carries its short KEY so the near-lane dispatcher picks the right
# per-phase life + performance.
PHASES = [
    ("DAY · Pastoral Morning", STAGE_PHASE["midday"], pr.phase_day, "day"),
    ("GOLDEN HOUR · Afternoon Promenade", STAGE_PHASE["golden"], pr.phase_golden, "golden"),
    ("DUSK · Lamps Lighting", STAGE_PHASE["dusk"], pr.phase_dusk, "dusk"),
    ("NIGHT · Festival", STAGE_PHASE["night"], pr.phase_night, "night"),
]

ROW_NOTES = {
    "Terracotta running-bond": "Warm worn clay walk. FAR lane (r17) + embedded surface detail (r18) UNCHANGED; NEW near/front lane adds larger, closer life + a per-phase street performance.",
    "Grey-Taupe cool": "Shaded damp stone walk. Same near/front activity lane on the cool base: near pedestrians + dog + plants + ornaments, performances spread day->night.",
    "Warm Honey flagstone": "Dressed temple slabs. Near/front lane reads the depth: closer figures occlude the far promenade; acrobat (day) -> musician+crowd (golden) -> prep (dusk) -> lion dance (night).",
}


def _render_cell(floor_painter, phase, phase_painter, phase_name, t):
    r13.SCROLL = R17_SCROLL
    surf, pal = r13._paint_context(phase)
    floor_painter(surf, W, GROUND_Y, H, R17_SCROLL, pal)
    # r18: embedded ground-surface detail, painted into the floor body.
    gd.add_embedded_detail(floor_painter, surf, W, GROUND_Y, H, R17_SCROLL, pal)
    # r17: promenade props + FAR-lane characters + lights.
    phase_painter(surf, W, GROUND_Y, H, R17_SCROLL, pal, t)
    # NEW for r19: the NEAR/front activity lane — larger, closer life + the
    # per-phase performance, drawn IN FRONT of the far lane but BEHIND the
    # gameplay actors (parrot + coin stay on top / brightest).
    nl.add_near_lane(surf, W, GROUND_Y, H, R17_SCROLL, pal, phase_name, t)
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
        "FOREGROUND REDESIGN - round 19 - NEAR / FRONT ACTIVITY LANE. The r17 promenade + r18 embedded detail UNCHANGED; a NEW nearer lane on the FRONT edge "
        "(larger figures, feet near the screen bottom, faster parallax) uses the sidewalk DEPTH and OCCLUDES the far lane: pedestrians + dog + plants + on-theme "
        "ornaments, plus a LIVE PERFORMANCE spread across the day - acrobat (DAY) -> musician + crowd (GOLDEN) -> performers prep (DUSK) -> LION DANCE (NIGHT). "
        "Tall near props clear the bird/pillar lanes; night glow capped under the coin.",
        True, (245, 235, 210))
    sheet.blit(t, (8, 8))

    for c, (pname, _, _, _) in enumerate(PHASES):
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

        for c, (pname, _, _, _) in enumerate(PHASES):
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
        for cname, phase, phase_painter, phase_name in PHASES:
            images[(rname, cname)] = _render_cell(
                floor_painter, phase, phase_painter, phase_name, ROW_T[ri])

    sheet = make_sheet(images)
    out = _HERE.parent.parent / "docs" / "foreground_redesign"
    out.mkdir(parents=True, exist_ok=True)
    path = out / "round_19.png"
    pygame.image.save(sheet, path)
    print(f"wrote {path}  ({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    main()
