"""Render the round-3 GROUNDED foreground/ground comparison sheet.

Rounds 1-2 leaned on summed-sine bank crests that read as ocean waves and as a
near echo of the ink-wash mountain ridges (see foreground_variants.py + the
round_1/round_2 sheets). Round 3 is a fresh direction: five STABLE, FLAT land
planes (foreground_grounded.py) whose identity is their SURFACE TEXTURE —
paving joints, clay cracks, rake furrows, grass blades, plank grain — opaque to
the bottom edge, distinct from the mountains and sky while still belonging to
the misty-gorge world.

6 rows (Original meadow + the 5 grounded concepts) × 4 columns
(day / sunset / dusk / night). Every cell is a FULL in-context 360x640 scene
with the biome held constant at misty_gorge so the foreground is the only
variable: misty_gorge sky + gorge mist + the V14 "Pagoda-Crowned Ridges"
mountains + a Songyue-sandstone pillar pair (one obstacle showing the gap) +
the candidate foreground. The backdrop is context only — each foreground must
read as its OWN thing against it, not a continuation of the ridges.

The misty_gorge palette drives the sky, is shimmed into the mountain module's
`game.biome` reference so V14 retints to the same stage, and is handed straight
to the Songyue pillar. The Original row replicates game.draw.draw_ground's
meadow look via game.ground_variants (read-only) for honest contrast.

Output: docs/foreground_redesign/round_3.png

Run from anywhere:
    SDL_VIDEODRIVER=dummy python archive/foreground_redesign/render_foreground.py
"""
from __future__ import annotations

import math
import os
import pathlib
import sys
import types

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

_HERE = pathlib.Path(__file__).parent
_REPO = _HERE.parent.parent
sys.path.insert(0, str(_REPO))
sys.path.insert(0, str(_REPO / "archive" / "biome_redesign"))
sys.path.insert(0, str(_REPO / "archive" / "mountain_redesign"))
sys.path.insert(0, str(_REPO / "archive" / "pillar_redesign"))
sys.path.insert(0, str(_HERE))

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game.config import W, H, GROUND_Y, PIPE_W
import scene_engine as se
import biome_variants as bv
import pillar_pagoda_variants as pgv
import mountain_variants_r2 as mv
import foreground_grounded as fg
import game.ground_variants as gv
import game.parrot as parrot
from game.config import BIRD_X, BIRD_R, COIN_R
from game.draw import COIN_GOLD, COIN_LIGHT, COIN_DARK


# ── biome held constant: misty_gorge, one of the locked sky winners ───────────
SPEC = bv.MISTY_GORGE

# Four times of day pulled from the redesign STAGES arc.
STAGE_PHASE = dict(bv.STAGES)
COLUMNS = [
    ("DAY", STAGE_PHASE["midday"]),
    ("SUNSET", STAGE_PHASE["sunset"]),
    ("DUSK", STAGE_PHASE["dusk"]),
    ("NIGHT", STAGE_PHASE["night"]),
]

# A fixed scroll so every tile composites the same world layout; only the
# foreground + stage change across the grid.
SCROLL = 760.0


def _stage_palette(phase):
    """misty_gorge palette at a phase, augmented with stone_* aliases so the
    Songyue pillar and the production pine/foliage helpers consume it
    unchanged. This single dict drives sky + mountains + pillar + foreground so
    the whole frame retints together."""
    pal = SPEC.palette_for_phase(phase)
    return se.to_draw_palette(pal)


class _BiomeShim(types.SimpleNamespace):
    """Stand-in for `game.biome` that returns the misty_gorge stage palette, so
    the V14 mountain painter (which reads a module-level `_biome`) retints to
    the held biome instead of the game's own default sky."""
    def __init__(self, pal):
        super().__init__()
        self._pal = pal

    def palette_for_phase(self, _phase):
        return self._pal


def _paint_context(phase):
    """Paint sky + gorge mist + V14 mountains + Songyue pillar pair into a fresh
    360x640 surface, returning (surf, pal). The foreground is layered on top by
    the caller so each row shares an identical backdrop."""
    pal = _stage_palette(phase)
    surf = pygame.Surface((W, H))

    # 1. misty_gorge sky (OKLab + dithered) over the full canvas, with the
    # night star sprinkle gated on the stage star_alpha.
    se.paint_sky(surf, SPEC, W, H, phase, stars=True, ground_y=GROUND_Y)

    # 2. gorge mist over the sky (the shan-shui veil that dissolves the ranks).
    ctx = se.SceneCtx(surf, W, H, GROUND_Y, phase, SCROLL, SPEC._pal(phase), pal)
    import biome_motifs as bm
    bm.gorge_mist(ctx)

    # 3. V14 "Pagoda-Crowned Ridges" — shim the mountain module's biome so it
    # reads the held misty_gorge palette, then restore.
    saved_biome = mv._biome
    mv._biome = _BiomeShim(pal)
    try:
        mv.set_phase(phase)
        mv.draw_mountains_pagoda(surf, SCROLL, GROUND_Y, W,
                                 pal['mtn_far'], pal['mtn_near'])
    finally:
        mv._biome = saved_biome

    # 4. Songyue-sandstone pillar pair — one obstacle showing the gap.
    gap_y, gap_h = 285, 150
    px = W - 116
    top_rect = pygame.Rect(px, 0, PIPE_W, gap_y - gap_h // 2)
    bot_rect = pygame.Rect(px, gap_y + gap_h // 2, PIPE_W,
                           GROUND_Y - (gap_y + gap_h // 2))
    pgv.candidate_songyue_sandstone(surf, top_rect, bot_rect, pal, seed=7)

    return surf, pal


def _render_original(phase):
    """The current game ground: misty_gorge backdrop + today's bright kelly-green
    meadow (via game.ground_variants, the same logic game.draw.draw_ground
    dispatches to). Shown for honest contrast against the candidates."""
    surf, pal = _paint_context(phase)
    # The meadow takes top/mid/bot tint args; feed the stage ground tones so it
    # gets the same day/night retint the live game gives it — yet it still reads
    # as the bright cartoon meadow that clashes with the ink-wash frame.
    gv.draw_ground_v1(surf, GROUND_Y, W, H, SCROLL,
                      pal.get('ground_top'), pal.get('ground_mid'),
                      pal.get('ground_bot'))
    return surf


def _draw_coin_standin(surf, cx, cy):
    """A faithful gameplay-scale gold coin stand-in (the live Coin spins a cached
    face; here a static disc with rim + sheen at COIN_R is enough to verify the
    foreground stays quiet behind a scrolling coin in the bird lane). Read-only —
    reuses the game's coin palette so the tone matches the real pickup."""
    r = COIN_R
    pygame.draw.circle(surf, COIN_DARK, (cx, cy), r)
    pygame.draw.circle(surf, COIN_GOLD, (cx, cy), r - 1)
    pygame.draw.circle(surf, COIN_LIGHT, (cx - r // 3, cy - r // 3), max(2, r // 2))
    pygame.draw.circle(surf, COIN_GOLD, (cx, cy), r - 1, 1)
    # Bright rim arc (upper-left) so the disc reads as metal, like the live face.
    pygame.draw.arc(surf, (255, 250, 210),
                    (cx - r + 1, cy - r + 1, 2 * r - 2, 2 * r - 2),
                    math.radians(60), math.radians(170), 2)


def _add_gameplay_actors(surf):
    """Drop the parrot at gameplay scale + a scrolling coin into the bird lane so
    the surface can be verified to stay quiet behind the player and the pillar
    base. The parrot comes straight from game.parrot (read-only, cached); the
    coin is a faithful stand-in. Only used on the two LEAD rows' DAY/NIGHT cells
    so the other rows stay uncluttered."""
    # Bird at its true on-screen position/scale, mid-flap frame, slight tilt.
    sprite = parrot.get_parrot(1, -8)
    rect = sprite.get_rect(center=(BIRD_X, GROUND_Y - 150))
    surf.blit(sprite, rect.topleft)
    # A coin a little ahead of the bird, riding the lane toward it.
    _draw_coin_standin(surf, BIRD_X + 78, GROUND_Y - 138)


def _render_concept(painter, phase, actors=False):
    surf, pal = _paint_context(phase)
    painter(surf, W, GROUND_Y, H, SCROLL, pal)
    if actors:
        _add_gameplay_actors(surf)
    return surf


# ── contact-sheet assembly (matches the mountain/biome sheet conventions) ─────

ROWS = [(name, fn) for name, fn in fg.CONCEPTS_R12]

ROW_NOTES = {
    "ORIGINAL GAME FLOOR": "HEIGHT REFERENCE - the LIVE floor at y=595 (45px strip). Mountains start at the floor TOP. Every row below nets to this exact top edge.",
    "Running-Bond UNTUNED (r11)": "BEFORE - the round-11 lead as-is. Brick field starts ~6px LOW, mortar/bevel + worn spread + brick ratio all pre-tuning. The contrast row.",
    "Tuned Running-Bond Clay (warm)": "VERSION A LEAD - top@595 FLUSH, 45px. Warm clay running bond, recessed-dark mortar (no bright seam), held-down bevel, wider worn spread, longer paver-ratio bricks. Bird + coin in DAY/NIGHT.",
    "Running-Bond Cool Pavers": "VERSION B - top@595, 45px. SAME tuned geometry in the cool grey-taupe paver palette (best night coherence), day value dropped ~9%. The day/night-biome counterpoint. Bird + coin in DAY/NIGHT.",
}


def make_sheet(images):
    tw, th = W, H
    label_h = 30
    row_label_w = 200
    pad = 10
    sheet_w = row_label_w + pad + len(COLUMNS) * (tw + pad)
    sheet_h = label_h + pad + len(ROWS) * (th + pad)
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((20, 20, 24))

    title = pygame.font.SysFont(None, 26)
    head = pygame.font.SysFont(None, 26)
    name_f = pygame.font.SysFont(None, 24)
    note_f = pygame.font.SysFont(None, 18)
    cap_f = pygame.font.SysFont(None, 22)

    t = title.render("FOREGROUND REDESIGN - round 12 - TUNE the chosen Running-Bond clay walkway + add its COOL counterpoint. Original ref + r11 UNTUNED before + Version A (tuned warm clay) + Version B (cool pavers) - flush@595, v8 lip, recessed-dark mortar, world-anchored seamless scroll - biome @ misty_gorge",
                     True, (245, 235, 210))
    sheet.blit(t, (8, 6))

    for c, (pname, _) in enumerate(COLUMNS):
        x = row_label_w + pad + c * (tw + pad)
        lbl = head.render(pname, True, (240, 240, 240))
        sheet.blit(lbl, (x + tw // 2 - lbl.get_width() // 2, 8))

    for r, (rname, _) in enumerate(ROWS):
        y = label_h + pad + r * (th + pad)
        # Row name (wrapped) + a one-line strategy note in the gutter.
        words = rname.split()
        line, ly = "", y + 10
        for word in words:
            test = (line + " " + word).strip()
            if name_f.size(test)[0] > row_label_w - 14 and line:
                sheet.blit(name_f.render(line, True, (255, 224, 150)), (8, ly))
                ly += 22
                line = word
            else:
                line = test
        if line:
            sheet.blit(name_f.render(line, True, (255, 224, 150)), (8, ly))
            ly += 24
        # Wrapped strategy note.
        note = ROW_NOTES.get(rname, "")
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

        for c, (pname, _) in enumerate(COLUMNS):
            full = images[(rname, pname)]
            x = row_label_w + pad + c * (tw + pad)
            sheet.blit(full, (x, y))
            cap = cap_f.render(f"{rname[:20]} - {pname}", True, (250, 250, 250))
            bg = pygame.Surface((cap.get_width() + 8, cap.get_height() + 4),
                                pygame.SRCALPHA)
            bg.fill((0, 0, 0, 120))
            sheet.blit(bg, (x + 4, y + 4))
            sheet.blit(cap, (x + 8, y + 6))

    return sheet


# Both version rows (warm A + cool B) get the bird + scrolling coin in their
# DAY and NIGHT cells so bird-lane quietness is judged on each palette.
LEAD_ROWS = {"Tuned Running-Bond Clay (warm)", "Running-Bond Cool Pavers"}
ACTOR_COLS = {"DAY", "NIGHT"}


def main():
    images = {}
    for rname, fn in ROWS:
        for pname, phase in COLUMNS:
            if fn is None:
                images[(rname, pname)] = _render_original(phase)
            else:
                actors = rname in LEAD_ROWS and pname in ACTOR_COLS
                images[(rname, pname)] = _render_concept(fn, phase, actors=actors)

    sheet = make_sheet(images)
    out = _REPO / "docs" / "foreground_redesign"
    out.mkdir(parents=True, exist_ok=True)
    path = out / "round_12.png"
    pygame.image.save(sheet, path)
    print(f"wrote {path}  ({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    main()
