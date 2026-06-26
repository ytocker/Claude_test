"""Preview figure for the proposed new parcels: 5 PARROT-CHILD designs + COIN +
DIAMOND, each carried below Pip mid-flight (DAY top, NIGHT bottom). Pure capture.

    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python tools/render_newparcels_preview.py
"""
import os, sys, pathlib, importlib.util

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "docs" / "parcels"))
sys.path.insert(0, str(ROOT / "docs" / "showcase"))

import pygame
import _parcel_lib as L
from game.config import H, BIRD_X
from game import parrot


def _load(path):
    spec = importlib.util.spec_from_file_location(path.stem + str(path.parent.name), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.build


BASE = ROOT / "docs" / "store_redesign" / "parcels"
VARIANTS = [
    ("CHILD 1", "MINI-PIP", _load(BASE / "parrot_child" / "design_1" / "build.py")),
    ("CHILD 2", "DOWNY CHICK", _load(BASE / "parrot_child" / "design_2" / "build.py")),
    ("CHILD 3", "EGG HATCHLING", _load(BASE / "parrot_child" / "design_3" / "build.py")),
    ("CHILD 4", "SLEEPY BABY", _load(BASE / "parrot_child" / "design_4" / "build.py")),
    ("CHILD 5", "PEEKER", _load(BASE / "parrot_child" / "design_5" / "build.py")),
    ("COIN", "GAME COIN", _load(BASE / "coin" / "design_1" / "build.py")),
    ("DIAMOND", "DIAMOND", _load(BASE / "diamond" / "design_1" / "build.py")),
]

PW, PH = 134, 184
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
    pad, lab_h, title_h = 13, 28, 52
    cols = len(VARIANTS)
    sheet = pygame.Surface((pad + cols * (PW + pad),
                            title_h + 2 * (lab_h + PH + pad)))
    sheet.fill((22, 24, 30))
    big = pygame.font.SysFont("Arial", 22, bold=True)
    lab = pygame.font.SysFont("Arial", 14, bold=True)
    sub = pygame.font.SysFont("Arial", 11)
    sheet.blit(big.render("Proposed new parcels — 5 PARROT-CHILD looks + COIN + "
                          "DIAMOND (Pip mid-flight)", True, (245, 245, 250)),
               (pad, (title_h - 22) // 2))
    for row, (phase, tag) in enumerate(((L._DAY_PHASE, "DAY"),
                                        (L._NIGHT_PHASE, "NIGHT"))):
        y = title_h + row * (lab_h + PH + pad)
        for col, (slot, name, fn) in enumerate(VARIANTS):
            x = pad + col * (PW + pad)
            sheet.blit(_panel(fn, phase), (x, y + lab_h))
            sheet.blit(lab.render(slot, True, (255, 214, 120)), (x + 2, y))
            sheet.blit(sub.render(f"{name} · {tag}", True, (160, 166, 180)),
                       (x + 2, y + 14))
    out = BASE / "new_parcels_preview.png"
    pygame.image.save(sheet, str(out))
    print("saved", out, sheet.get_size())


if __name__ == "__main__":
    main()
