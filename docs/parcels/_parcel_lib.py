"""Shared render harness for the PARCEL concept design loops.

A parcel is tiny (~22px) and rotates with the bird's tilt, so the verdict is how
it reads carried below Pip in the REAL gameplay frame. This renders any concept's
`build(mode="normal") -> Surface` into the staged scene (base bird skin, the
concept hot-swapped as the equipped parcel) on a DAY and a NIGHT sky, plus a 4×
zoom on the parcel and a true-size TILT ROW (the parcel rotated across the flight
arc) on day / night / grayscale swatches.

Concept loops import `render_concept_sheet(build_fn, name, out_png)`.
Run a concept's render.py with:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python <concept>/render.py
"""
import os, sys, pathlib

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "docs" / "showcase"))

import pygame
import render_showcase as RS
from game.config import W, H, BIRD_X, PARCEL_Y_OFFSET
from game import parrot
from game.hud import HUD

_TMP_ID = "parcel_concept"          # hot-swap slot in the parcel registry
_DAY_PHASE = 0.0
_NIGHT_PHASE = 0.52
_TILTS = (-25, 0, 30, 60, 90)       # representative flight-arc bank angles


def _scene(phase):
    RS.SCENE_PHASE = phase
    world, base = RS.build_scene()
    world.score = 42
    world.bird.equipped_skin = "skin_base"
    world.bird.equipped_parcel = _TMP_ID
    return world, base


def _frame(world, base, hud):
    full = base.copy()
    world.bird.draw(full, 0, 0)
    try:
        hud.draw_play(full, world, best=world.score)
    except Exception:
        pass
    return full


def _checker(w, h, s=8):
    surf = pygame.Surface((w, h))
    a, b = (210, 210, 214), (170, 170, 176)
    for y in range(0, h, s):
        for x in range(0, w, s):
            surf.fill(a if ((x // s + y // s) % 2 == 0) else b,
                      pygame.Rect(x, y, s, s))
    return surf


def render_concept_sheet(build_fn, name, out_png):
    # Register the concept as the equipped parcel.
    parrot._store_parcel_builders()[_TMP_ID] = build_fn
    hud = HUD()
    day_w, day_b = _scene(_DAY_PHASE)
    night_w, night_b = _scene(_NIGHT_PHASE)
    day = _frame(day_w, day_b, hud)
    night = _frame(night_w, night_b, hud)

    sprite = build_fn("normal")
    sw, sh = sprite.get_size()

    # Zoom box centred on the parcel anchor (below bird centre).
    zb = 70
    px = int(BIRD_X)
    py = int(H * 0.42 + PARCEL_Y_OFFSET)
    zoom_day = pygame.transform.scale(
        day.subsurface(pygame.Rect(px - zb // 2, py - zb // 2, zb, zb)).copy(),
        (zb * 3, zb * 3))

    col_w = 250
    col = pygame.Surface((col_w, H))
    col.fill((28, 30, 36))
    # 5× hero on a checker
    scale = 5
    cb = _checker(sw * scale, sh * scale)
    x = (col_w - sw * scale) // 2
    col.blit(cb, (x, 16))
    col.blit(pygame.transform.scale(sprite, (sw * scale, sh * scale)), (x, 16))
    # zoom of the in-scene parcel
    col.blit(zoom_day, ((col_w - zoom_day.get_width()) // 2, sh * scale + 30))

    # true-size tilt row on day / night / grayscale swatches
    play = 26                                   # ~ in-play parcel size
    strip_y = sh * scale + 30 + zoom_day.get_height() + 24
    swatches = (((170, 220, 245), "DAY"), ((18, 22, 48), "NIGHT"))
    sy = strip_y
    small = pygame.font.SysFont("Arial", 13, bold=True)
    for bg, lbl in swatches:
        sw_surf = pygame.Surface((play * len(_TILTS) + 18, play + 14))
        sw_surf.fill(bg)
        for i, ang in enumerate(_TILTS):
            r = pygame.transform.rotozoom(sprite, ang, play / max(sw, sh))
            sw_surf.blit(r, r.get_rect(center=(9 + i * play + play // 2,
                                               7 + play // 2)))
        col.blit(sw_surf, (10, sy))
        col.blit(small.render(lbl, True, (220, 225, 235)), (12, sy - 14))
        sy += play + 30
    # grayscale tilt row
    gs = pygame.Surface((play * len(_TILTS) + 18, play + 14))
    gs.fill((120, 120, 120))
    for i, ang in enumerate(_TILTS):
        r = pygame.transform.rotozoom(sprite, ang, play / max(sw, sh))
        r = pygame.transform.grayscale(r) if hasattr(pygame.transform, "grayscale") else r
        gs.blit(r, r.get_rect(center=(9 + i * play + play // 2, 7 + play // 2)))
    col.blit(gs, (10, sy))
    col.blit(small.render("GRAYSCALE", True, (220, 225, 235)), (12, sy - 14))

    pad, lab_h = 12, 40
    sheet = pygame.Surface((pad * 4 + W * 2 + col_w, lab_h + H + pad))
    sheet.fill((22, 24, 30))
    title = pygame.font.SysFont("Arial", 22, bold=True)
    sheet.blit(title.render(name, True, (245, 245, 250)),
               (pad, (lab_h - 22) // 2))
    x = pad
    for surf, lbl in ((day, "GAMEPLAY — DAY"), (night, "GAMEPLAY — NIGHT")):
        sheet.blit(surf, (x, lab_h))
        sheet.blit(small.render(lbl, True, (210, 215, 225)), (x + 4, lab_h + 4))
        x += W + pad
    sheet.blit(col, (x, lab_h))
    sheet.blit(small.render("HERO / ZOOM / TILT", True, (210, 215, 225)),
               (x + 6, lab_h + 2))

    out = pathlib.Path(out_png)
    out.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(sheet, str(out))
    return str(out)
