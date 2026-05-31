"""
Render the sky color-field exploration sheet: 8 treatments (rows) across the 7
times of day (columns). Each cell is the pure sky field on a 360x640 tile with
only a faint ground strip + ridge silhouette at the very bottom for scale — the
sky itself is the subject under review.

Run:
    python archive/sky_redesign/render_field_variants.py [round_N]
Writes docs/sky_redesign/<round>.png  (default: field_round_1.png)
"""
import os, sys, pathlib
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent.parent))

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from game import biome as _biome
from archive.sky_redesign.field_variants import (
    VARIANTS, VARIANT_NAMES, VARIANT_NOTES,
)

W, H, GROUND_Y = 360, 640, 595

# 7 day-cycle columns aligned to the biome keyframes.
PHASES = [
    ("DAY",     0.00),
    ("GOLDEN",  0.18),
    ("SUNSET",  0.32),
    ("DUSK",    0.48),
    ("NIGHT",   0.62),
    ("PREDAWN", 0.78),
    ("SUNRISE", 0.90),
]

# Display scale of each tile in the sheet, plus margins for labels.
TILE_W, TILE_H = 180, 320
PAD = 6
LABEL_L = 150          # left gutter for treatment names
LABEL_T = 26           # top strip for phase names


def _ground_strip(surf):
    """A faint neutral ground band + low ridge so the sky has a horizon to read
    against. Deliberately desaturated/dim so it never competes with the sky."""
    gy = GROUND_Y
    pygame.draw.rect(surf, (30, 32, 38), (0, gy, W, H - gy))
    ridge = [(0, gy)]
    import math
    for x in range(0, W + 1, 12):
        ridge.append((x, gy - int(10 + 8 * math.sin(x * 0.05))))
    ridge += [(W, gy), (W, H), (0, H)]
    pygame.draw.polygon(surf, (24, 26, 32), ridge)


def render_tile(name, phase):
    palette = _biome.palette_for_phase(phase)
    tile = pygame.Surface((W, H))
    sky = VARIANTS[name](W, GROUND_Y, palette)
    tile.blit(sky, (0, 0))
    _ground_strip(tile)
    return pygame.transform.smoothscale(tile, (TILE_W, TILE_H))


def main():
    round_name = sys.argv[1] if len(sys.argv) > 1 else "field_round_1"
    cols, rows = len(PHASES), len(VARIANT_NAMES)
    sheet_w = LABEL_L + cols * (TILE_W + PAD) + PAD
    sheet_h = LABEL_T + rows * (TILE_H + PAD) + PAD
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((18, 18, 22))

    font = pygame.font.SysFont("dejavusans", 14, bold=True)
    small = pygame.font.SysFont("dejavusans", 11)

    for ci, (pname, _) in enumerate(PHASES):
        x = LABEL_L + ci * (TILE_W + PAD) + TILE_W // 2
        lab = font.render(pname, True, (230, 230, 235))
        sheet.blit(lab, (x - lab.get_width() // 2, 6))

    for ri, name in enumerate(VARIANT_NAMES):
        y = LABEL_T + ri * (TILE_H + PAD)
        lab = font.render(name, True, (235, 235, 240))
        sheet.blit(lab, (8, y + 6))
        note = VARIANT_NOTES.get(name, "")
        for li, chunk in enumerate(_wrap(note, 22)):
            n = small.render(chunk, True, (150, 150, 158))
            sheet.blit(n, (8, y + 28 + li * 13))
        for ci, (_, phase) in enumerate(PHASES):
            x = LABEL_L + ci * (TILE_W + PAD) + PAD
            sheet.blit(render_tile(name, phase), (x, y))

    out_dir = pathlib.Path(__file__).resolve().parent.parent.parent / "docs" / "sky_redesign"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{round_name}.png"
    pygame.image.save(sheet, out)
    print(f"wrote {out}  ({sheet_w}x{sheet_h}, {rows} treatments x {cols} phases)")


def _wrap(text, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width:
            lines.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lines.append(cur)
    return lines[:3]


if __name__ == "__main__":
    main()
