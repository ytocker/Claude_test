"""ONE comparison figure for the MACHINE GUN parcel redesign (v2).

Renders the shipped MACHINE GUN (original) + the 5 design candidates, each
carried below Pip mid-flight over a real gameplay scene (DAY on top, NIGHT
below), side by side and labelled. Pure capture — production art untouched.

    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python tools/render_machine_gun_compare.py
"""
import os, sys, pathlib, importlib.util

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "docs" / "parcels"))      # _parcel_lib
sys.path.insert(0, str(ROOT / "docs" / "showcase"))

import pygame
import _parcel_lib as L
from game.config import W, H, BIRD_X, PARCEL_Y_OFFSET
from game import parrot
from game.parcel_designs import machine_gun as original


def _load_build(n):
    p = ROOT / "docs" / "store_redesign" / "parcels" / "machine_gun" / "v2" / f"design_{n}" / "build.py"
    spec = importlib.util.spec_from_file_location(f"mg_design_{n}", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.build


VARIANTS = [("ORIGINAL", original.build)] + [
    (f"DESIGN {n}", _load_build(n)) for n in range(1, 6)
]
NAMES = ["TOMMY GUN (shipped)", "GATLING GUN", "NERF BLASTER",
         "LASER MINIGUN", "GOLD DELUXE", "WATER BLASTER"]

PW, PH = 150, 200
CX, CY = int(BIRD_X), int(H * 0.42 + 6)


def _panel(build_fn, phase):
    parrot._store_parcel_builders()[L._TMP_ID] = build_fn
    hud = L.HUD()
    world, base = L._scene(phase)
    frame = L._frame(world, base, hud)
    rect = pygame.Rect(CX - PW // 2, CY - PH // 2, PW, PH)
    return frame.subsurface(rect).copy()


def main():
    pygame.init()
    pad, lab_h, title_h = 14, 26, 56
    cols = len(VARIANTS)
    sheet_w = pad + cols * (PW + pad)
    sheet_h = title_h + 2 * (lab_h + PH + pad)
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((22, 24, 30))

    big = pygame.font.SysFont("Arial", 24, bold=True)
    lab = pygame.font.SysFont("Arial", 14, bold=True)
    sub = pygame.font.SysFont("Arial", 11)
    sheet.blit(big.render("MACHINE GUN parcel — shipped vs 5 redesigns "
                          "(Pip mid-flight)", True, (245, 245, 250)),
               (pad, (title_h - 24) // 2))

    for row, (phase, tag) in enumerate(((L._DAY_PHASE, "DAY"),
                                        (L._NIGHT_PHASE, "NIGHT"))):
        y = title_h + row * (lab_h + PH + pad)
        for col, (label, build_fn) in enumerate(VARIANTS):
            x = pad + col * (PW + pad)
            panel = _panel(build_fn, phase)
            sheet.blit(panel, (x, y + lab_h))
            col_lbl = (220, 224, 235) if col else (255, 214, 120)
            sheet.blit(lab.render(label, True, col_lbl), (x + 2, y))
            sheet.blit(sub.render(f"{NAMES[col]} · {tag}", True, (150, 156, 170)),
                       (x + 2, y + 13))

    out = ROOT / "docs" / "store_redesign" / "parcels" / "machine_gun" / "v2" / "final_comparison.png"
    pygame.image.save(sheet, str(out))
    print("saved", out, sheet.get_size())


if __name__ == "__main__":
    main()
