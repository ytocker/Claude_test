"""ONE comparison figure for the new SECRET "finest whiskey" parcel.

Renders the 5 design candidates, each carried below Pip mid-flight over a real
gameplay scene (DAY on top, NIGHT below), side by side and labelled. New item,
so there is no original — the five designs are the comparison. Pure capture.

    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python tools/render_whiskey_compare.py
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
from game.config import H, BIRD_X
from game import parrot


def _load_build(n):
    p = ROOT / "docs" / "store_redesign" / "parcels" / "whiskey" / f"design_{n}" / "build.py"
    spec = importlib.util.spec_from_file_location(f"whiskey_design_{n}", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.build


NAMES = ["CRYSTAL DECANTER", "SCOTCH FIFTH", "SQUARE BOURBON",
         "GOLD RESERVE", "CASKED DRAM"]
VARIANTS = [(f"DESIGN {n}", _load_build(n)) for n in range(1, 6)]

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
    sheet.blit(big.render("FINEST WHISKEY (secret parcel) — 5 designs "
                          "(Pip mid-flight)", True, (245, 245, 250)),
               (pad, (title_h - 24) // 2))

    for row, (phase, tag) in enumerate(((L._DAY_PHASE, "DAY"),
                                        (L._NIGHT_PHASE, "NIGHT"))):
        y = title_h + row * (lab_h + PH + pad)
        for col, (label, build_fn) in enumerate(VARIANTS):
            x = pad + col * (PW + pad)
            sheet.blit(_panel(build_fn, phase), (x, y + lab_h))
            sheet.blit(lab.render(label, True, (220, 224, 235)), (x + 2, y))
            sheet.blit(sub.render(f"{NAMES[col]} · {tag}", True, (150, 156, 170)),
                       (x + 2, y + 13))

    out = ROOT / "docs" / "store_redesign" / "parcels" / "whiskey" / "final_comparison.png"
    pygame.image.save(sheet, str(out))
    print("saved", out, sheet.get_size())


if __name__ == "__main__":
    main()
