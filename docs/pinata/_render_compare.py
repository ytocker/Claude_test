"""Final 5-up comparison: every piñata concept in the real gameplay frame.

Loads each concept's current build() and renders it into the staged scene at true
scale (HUD + Pip's parcel) on DAY (top row) and NIGHT (bottom row), side by side.

Run:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python docs/pinata/_render_compare.py
"""
import os, sys, pathlib, importlib.util

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "docs" / "showcase"))

import pygame
import render_showcase as RS
from game.config import W, H
from game import parrot
from game.animal_ufo import _make_prebuilt_skin
from game.hud import HUD

CONCEPTS = [
    ("STAR", "star"),
    ("BURRO", "burro"),
    ("CACTUS", "cactus"),
    ("HEART", "heart"),
    ("PARROT", "parrot"),
]
OUT_NAME = "gameplay_compare.png"


def load_build(folder):
    p = HERE / folder / "build.py"
    spec = importlib.util.spec_from_file_location(f"_cmp_{HERE.name}_{folder}", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.build


def scene(phase):
    RS.SCENE_PHASE = phase
    world, base = RS.build_scene()
    world.score = 42
    return world, base


def frame(world, base, getter, hud):
    parrot._store_skin_builders()["skin_ufo"] = getter
    full, _ = RS.render_look(world, base, "skin_ufo")
    try:
        hud.draw_play(full, world, best=world.score)
    except Exception:
        pass
    return full


def main():
    hud = HUD()
    day_w, day_b = scene(0.0)
    night_w, night_b = scene(0.52)

    pad, lab_h = 12, 40
    n = len(CONCEPTS)
    sheet = pygame.Surface((pad + n * (W + pad), lab_h + (H + pad) * 2))
    sheet.fill((22, 24, 30))
    title = pygame.font.SysFont("Arial", 22, bold=True)
    small = pygame.font.SysFont("Arial", 15, bold=True)

    for i, (name, folder) in enumerate(CONCEPTS):
        getter = _make_prebuilt_skin(load_build(folder))
        day = frame(day_w, day_b, getter, hud)
        night = frame(night_w, night_b, getter, hud)
        x = pad + i * (W + pad)
        sheet.blit(day, (x, lab_h))
        sheet.blit(night, (x, lab_h + H + pad))
        t = title.render(name, True, (245, 245, 250))
        sheet.blit(t, (x + (W - t.get_width()) // 2, (lab_h - t.get_height()) // 2))
        for surf_y, lbl in ((lab_h, "DAY"), (lab_h + H + pad, "NIGHT")):
            tag = small.render(lbl, True, (215, 220, 230))
            sheet.blit(tag, (x + 4, surf_y + 4))

    out = HERE / OUT_NAME
    pygame.image.save(sheet, str(out))
    print("wrote", out, sheet.get_size())


if __name__ == "__main__":
    main()
