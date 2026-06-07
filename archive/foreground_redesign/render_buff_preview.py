"""Preview: the PALE BUFF SANDSTONE running-bond base carrying the FULL foreground
stack (r18 embedded detail + r17 promenade + r19 near/front activity lane with the
per-phase performances), across all four day->night phases.

The user likes the pale-buff swatch (round 13) and wants to see it WITH the
foreground elements that the three round-19 finalists already show. This renders
one base row x four phase columns so it reads exactly like a round-19 row.

Output: docs/foreground_redesign/round_20_buff.png

    SDL_VIDEODRIVER=dummy python archive/foreground_redesign/render_buff_preview.py
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

R17_SCROLL = 20.0
STAGE_PHASE = r13.STAGE_PHASE

BASE = ("Pale Buff sandstone - running-bond", fg.fg_swatch_buff_running_bond)

PHASES = [
    ("DAY · Pastoral Morning", STAGE_PHASE["midday"], pr.phase_day, "day"),
    ("GOLDEN HOUR · Afternoon Promenade", STAGE_PHASE["golden"], pr.phase_golden, "golden"),
    ("DUSK · Lamps Lighting", STAGE_PHASE["dusk"], pr.phase_dusk, "dusk"),
    ("NIGHT · Festival", STAGE_PHASE["night"], pr.phase_night, "night"),
]


def _render_cell(floor_painter, phase, phase_painter, phase_name, t):
    r13.SCROLL = R17_SCROLL
    surf, pal = r13._paint_context(phase)
    floor_painter(surf, W, GROUND_Y, H, R17_SCROLL, pal)
    gd.add_embedded_detail(floor_painter, surf, W, GROUND_Y, H, R17_SCROLL, pal)
    phase_painter(surf, W, GROUND_Y, H, R17_SCROLL, pal, t)
    nl.add_near_lane(surf, W, GROUND_Y, H, R17_SCROLL, pal, phase_name, t)
    r13._add_gameplay_actors(surf)
    return surf


def main():
    tw, th = W, H
    label_h = 30
    row_label_w = 210
    pad = 10
    sheet_w = row_label_w + pad + len(PHASES) * (tw + pad)
    sheet_h = label_h + pad + (th + pad)
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((20, 20, 24))

    title = pygame.font.SysFont(None, 24)
    head = pygame.font.SysFont(None, 24)
    name_f = pygame.font.SysFont(None, 26)
    note_f = pygame.font.SysFont(None, 18)
    cap_f = pygame.font.SysFont(None, 22)

    sheet.blit(title.render(
        "FOREGROUND PREVIEW - PALE BUFF SANDSTONE base with the FULL foreground stack "
        "(r18 embedded detail + r17 promenade + r19 near/front activity lane + per-phase performances), "
        "day -> night. Same scene as a round-19 row, swapped onto the pale-buff running-bond.",
        True, (245, 235, 210)), (8, 8))

    for c, (pname, _, _, _) in enumerate(PHASES):
        x = row_label_w + pad + c * (tw + pad)
        lbl = head.render(pname, True, (255, 236, 180))
        sheet.blit(lbl, (x + tw // 2 - lbl.get_width() // 2, 6))

    rname, painter = BASE
    y = label_h + pad
    sheet.blit(name_f.render("Buff", True, (255, 224, 150)), (8, y + 10))
    note = "Pale buff / warm sandstone running-bond. Light, low-chroma cream-tan; tone-on-tone with the cream pagoda. Shown here with the full promenade + performances."
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

    for c, (pname, phase, phase_painter, phase_name) in enumerate(PHASES):
        cell = _render_cell(painter, phase, phase_painter, phase_name, 1.0)
        x = row_label_w + pad + c * (tw + pad)
        sheet.blit(cell, (x, y))
        cap = cap_f.render(pname.split(" · ")[0], True, (250, 250, 250))
        bg = pygame.Surface((cap.get_width() + 8, cap.get_height() + 4), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 120))
        sheet.blit(bg, (x + 4, y + 4))
        sheet.blit(cap, (x + 8, y + 6))

    out = _HERE.parent.parent / "docs" / "foreground_redesign"
    out.mkdir(parents=True, exist_ok=True)
    path = out / "round_20_buff.png"
    pygame.image.save(sheet, path)
    print(f"wrote {path}  ({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    main()
