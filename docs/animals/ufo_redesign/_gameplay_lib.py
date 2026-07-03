"""Shared render helpers for the UFO concept design loops.

The decisive acceptance artifact for every concept is how it reads in the REAL
staged gameplay frame at true scale (sky, mountains, pillar, coins, ground, live
HUD, and Pip's parcel) — NOT a flattering hero shot. This module renders any
single concept's 4-frame builder into that frame on a DAY and a NIGHT sky, plus a
hero/40px reference strip, into one comparison sheet.

Concept loops import `render_concept_sheet(build_fn, name, out_png)`.

Run a concept's own render script with:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python <concept>/render.py
"""
import os, sys, pathlib

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "docs" / "showcase"))

import pygame
import render_showcase as RS                 # does pygame.init + a 1x1 display
from game.config import W, H, BIRD_X
from game import parrot
from game.animal_ufo import _make_prebuilt_skin
from game.hud import HUD

_DAY_PHASE = 0.0       # bright daytime keyframe (render_showcase default)
_NIGHT_PHASE = 0.52    # deep-night keyframe in the 5-min biome cycle


def _scene(phase):
    RS.SCENE_PHASE = phase
    world, base = RS.build_scene()
    world.score = 42
    return world, base


def _gameplay_frame(world, base, getter, hud):
    parrot._store_skin_builders()["skin_ufo"] = getter   # hot-swap dispatch
    full, _ = RS.render_look(world, base, "skin_ufo")
    try:
        hud.draw_play(full, world, best=world.score)
    except Exception:
        pass
    return full


def _checker(w, h, s=8):
    """Transparency backdrop so the 40px hero tiles show true alpha edges."""
    surf = pygame.Surface((w, h))
    a, b = (210, 210, 214), (170, 170, 176)
    for y in range(0, h, s):
        for x in range(0, w, s):
            surf.fill(a if ((x // s + y // s) % 2 == 0) else b,
                      pygame.Rect(x, y, s, s))
    return surf


def render_concept_sheet(build_fn, name, out_png):
    """DAY frame | NIGHT frame | reference column (4 frames @3x + a true-40px
    day/night/grayscale strip). The two gameplay frames are the verdict; the
    reference column is secondary detail."""
    getter = _make_prebuilt_skin(build_fn)
    hud = HUD()

    day_world, day_base = _scene(_DAY_PHASE)
    night_world, night_base = _scene(_NIGHT_PHASE)
    day = _gameplay_frame(day_world, day_base, getter, hud)
    night = _gameplay_frame(night_world, night_base, getter, hud)

    # Reference column: 4 frames at 3x on a checker, then the same frames at TRUE
    # 40px-ish (the in-play size) on a day swatch, a night swatch, and grayscale.
    col_w = 232
    frames = [getter(i, 0.0) for i in range(4)]
    fw, fh = frames[0].get_size()
    scale = 3
    col = pygame.Surface((col_w, H))
    col.fill((28, 30, 36))
    cb = _checker(fw * scale, fh * scale)
    x = (col_w - fw * scale) // 2
    col.blit(cb, (x, 18))
    for i, f in enumerate(frames):
        big = pygame.transform.scale(f, (fw * scale, fh * scale))
        col.blit(big, (x, 18) if i == 0 else (x, 18))  # overlay frame 0 only here
    # show all four frames in a row lower down at ~1.6x
    s2 = 1.6
    row_y = fh * scale + 40
    rb = _checker(int(fw * s2) * 4 + 12, int(fh * s2))
    col.blit(rb, (10, row_y))
    for i, f in enumerate(frames):
        col.blit(pygame.transform.scale(f, (int(fw * s2), int(fh * s2))),
                 (10 + i * (int(fw * s2) + 3), row_y))
    # true in-play size (~44px tall) strip on day / night / grayscale swatches
    play_h = 44
    pw = int(fw * play_h / fh)
    strip_y = row_y + int(fh * s2) + 26
    swatches = [((170, 220, 245), "DAY"), ((18, 22, 48), "NIGHT")]
    sx = 12
    for col_bg, _lbl in swatches:
        sw = pygame.Surface((pw * 4 + 18, play_h + 12))
        sw.fill(col_bg)
        for i, f in enumerate(frames):
            sm = pygame.transform.smoothscale(f, (pw, play_h))
            sw.blit(sm, (6 + i * (pw + 2), 6))
        col.blit(sw, (sx, strip_y))
        sx += pw * 4 + 26
    # grayscale strip (colorblind check) under, on mid-grey
    gs = pygame.Surface((pw * 4 + 18, play_h + 12))
    gs.fill((120, 120, 120))
    for i, f in enumerate(frames):
        sm = pygame.transform.smoothscale(f, (pw, play_h)).convert_alpha()
        gray = pygame.transform.grayscale(sm) if hasattr(pygame.transform, "grayscale") else sm
        gs.blit(gray, (6 + i * (pw + 2), 6))
    col.blit(gs, (12, strip_y + play_h + 22))

    pad, lab_h = 12, 40
    sheet = pygame.Surface((pad * 4 + W * 2 + col_w, lab_h + H + pad))
    sheet.fill((22, 24, 30))
    font = pygame.font.SysFont("Arial", 22, bold=True)
    small = pygame.font.SysFont("Arial", 16, bold=True)
    title = font.render(name, True, (245, 245, 250))
    sheet.blit(title, (pad, (lab_h - title.get_height()) // 2))

    x = pad
    for surf, lbl in ((day, "GAMEPLAY — DAY"), (night, "GAMEPLAY — NIGHT")):
        sheet.blit(surf, (x, lab_h))
        t = small.render(lbl, True, (210, 215, 225))
        sheet.blit(t, (x + 4, lab_h + 4))
        x += W + pad
    sheet.blit(col, (x, lab_h))
    t = small.render("REFERENCE  (3x / play-size / grayscale)", True, (210, 215, 225))
    sheet.blit(t, (x + 6, lab_h + 2))

    out = pathlib.Path(out_png)
    out.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(sheet, str(out))
    return str(out)
