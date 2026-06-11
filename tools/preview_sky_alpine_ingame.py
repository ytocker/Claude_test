"""Headless 10x12 IN-GAME sheet for the Alpine Haze sunset/sunrise study.

Same rows/columns as `tools/preview_sky_alpine_sunsets.py` (10 study designs x
12 day-phase samples) but every cell is a real engine frame instead of a bare
sky swatch: the candidate sky is baked through the live `game.biome_sky`
gradient, then the actual in-game **mountains + pagodas** (phase-driven), the
empty sandstone **ground/sidewalk**, and the **parrot** are composited over it
exactly as `App._draw_background` does. This lets the palette be judged the way
it reads in gameplay — the hollow ink-wash mountains show the candidate's lower
sky gradient THROUGH them, which a sky-only swatch can't reveal.

Deliberately omitted so the figure stays about the SKY+terrain palette: pillars,
coins, power-ups, weather, HUD, and the promenade's people/props (the sidewalk
is rendered but left empty). The pagodas DO retint across the day because the
mountain layer keys off `world.biome_phase`.

Why the engine bake (not the Catmull preview bake): this sheet answers "what
does activating this design look like in the running game", so it uses the same
`game.biome_sky.paint_sky` the live `_draw_background` uses. Dev aid only; the
game never imports this and `ACTIVE_SKY_DESIGN` stays untouched.

    python tools/preview_sky_alpine_ingame.py
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

import pygame  # noqa: E402

pygame.init()

import game.scenes as scenes                       # noqa: E402
from game import foreground                         # noqa: E402
from game import sky_designs as _sky_designs        # noqa: E402
from game.config import W, H, GROUND_Y             # noqa: E402
from game.scenes import App, STATE_PLAY            # noqa: E402
from game.world import World                       # noqa: E402
from game.biome_sky import paint_sky               # noqa: E402
from tools.sky_alpine_sunsets import CONCEPTS      # noqa: E402

# Force the live-bake path so our per-cell sky shim is the only sky source
# (an active design would short-circuit `_draw_background` and paint one sky
# in every row).
_sky_designs.ACTIVE_SKY_DESIGN = None

CYCLE_SECONDS = 320.0  # game/biome.py: phase = (t / 320) % 1

# Same 12-phase day arc and order as the sky-only study sheet, so the columns
# line up with the sheets already under review.
PHASES = [
    ("predawn", 0.80),
    ("dawn", 0.88),
    ("sunrise", 0.94),
    ("early-morning", 0.02),
    ("morning", 0.10),
    ("midday", 0.20),
    ("afternoon", 0.32),
    ("golden", 0.42),
    ("sunset", 0.50),
    ("dusk", 0.60),
    ("twilight", 0.68),
    ("night", 0.74),
]

# Native frame downscaled to a legible tile (~440 px tall, matching the study
# sheet's cell height).
TILE_H = 440
TILE_SCALE = TILE_H / H
TW, TH = int(W * TILE_SCALE), int(H * TILE_SCALE)
GUT = 220          # left gutter for the design name + note
HEAD = 34          # top strip for phase labels
PAD = 4


# ── per-cell sky swap ─────────────────────────────────────────────────────────
# `_draw_background` calls get_sky_surface_biome(w,h,ground_y,palette,bucket)
# (twice, for the bucket cross-fade); we ignore the live palette/bucket and hand
# back the current cell's pre-baked study sky. Both calls share one phase so the
# cross-fade is a no-op and the cell shows a single clean design sky.
_CUR = {"spec": None, "phase": 0.0}
_sky_cache = {}


def _design_sky_shim(w, h, ground_y, palette, phase_bucket):
    spec = _CUR["spec"]
    key = (id(spec), _CUR["phase"])
    surf = _sky_cache.get(key)
    if surf is None:
        surf = pygame.Surface((W, H))
        paint_sky(surf, spec, W, H, _CUR["phase"], stars=True, ground_y=GROUND_Y)
        _sky_cache[key] = surf
    return surf.copy()


f_title = pygame.font.SysFont("dejavusans", 20, bold=True)
f_phase = pygame.font.SysFont("dejavusans", 15, bold=True)
f_name = pygame.font.SysFont("dejavusans", 19, bold=True)
f_note = pygame.font.SysFont("dejavusans", 12)


def _wrap(text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if font.size(trial)[0] <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def main():
    # Empty sidewalk: keep the sandstone floor, drop the promenade's people/props
    # and the near-lane cast so the figure stays about the sky+terrain palette.
    foreground.draw_promenade = lambda *a, **k: None
    foreground.draw_near_lane = lambda *a, **k: None
    scenes.get_sky_surface_biome = _design_sky_shim

    app = App()
    if hasattr(app, "_splash_covering"):
        app._splash_covering = False
    app._cloud_phase = 0.0
    if hasattr(app, "_cloud_variant"):
        app._cloud_variant = 0

    world = World()
    world.ready_t = 0.0
    world.bird.y = H * 0.42          # mid-air, clear of the mountains + floor
    app.world = world
    app.state = STATE_PLAY

    cols, rows = PHASES, CONCEPTS
    sheet_w = GUT + len(cols) * (TW + PAD) + PAD
    sheet_h = HEAD + len(rows) * (TH + PAD) + PAD
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((20, 20, 24))

    sheet.blit(f_title.render(
        "Skybit Alpine Haze — in-game (mountains + pagodas + parrot, empty walk) "
        "— v3 round 1", True, (245, 246, 250)), (10, 6))

    for c, (label, _ph) in enumerate(cols):
        x = GUT + c * (TW + PAD)
        lbl = f_phase.render(label, True, (250, 232, 184))
        sheet.blit(lbl, (x + (TW - lbl.get_width()) // 2, HEAD - 22))

    for r, (cid, spec) in enumerate(rows):
        y = HEAD + r * (TH + PAD)
        _CUR["spec"] = spec
        nm = f_name.render(spec.name, True, (248, 248, 252))
        sheet.blit(nm, (10, y + 8))
        ny = y + 8 + nm.get_height() + 6
        for line in _wrap(spec.note, f_note, GUT - 18):
            sheet.blit(f_note.render(line, True, (176, 180, 190)), (10, ny))
            ny += f_note.get_height() + 2
        for c, (_label, phase) in enumerate(cols):
            x = GUT + c * (TW + PAD)
            _CUR["phase"] = phase
            world.biome_time = phase * CYCLE_SECONDS
            app._draw_background(app.screen)
            world.bird.draw(app.screen, 0, 0)
            sheet.blit(pygame.transform.smoothscale(app.screen, (TW, TH)), (x, y))

    out = os.path.join(_ROOT, "docs", "biome_redesign",
                       "alpine_sunsets_v3_ingame_round_1.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print(f"wrote {out}  ({sheet.get_width()}x{sheet.get_height()}, "
          f"{len(rows)} rows x {len(cols)} cols, cell {TW}x{TH})")


if __name__ == "__main__":
    main()
