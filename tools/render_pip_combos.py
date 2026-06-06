"""Contact-sheet harness for Pip's power-up combination skins.

Sets the relevant Bird flags for each combination, calls Bird.draw onto a
tile, and lays the tiles into a labelled grid so every combo can be eyeballed
for clipping / double-stacked head-pieces / dropped buffs. Procedural-art
verification only; not shipped in the WASM bundle.
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((360, 640))

from game.entities import Bird  # noqa: E402

# Each combo: label -> dict of Bird-flag overrides.
COMBOS = [
    ("base", {}),
    ("3x (hat)", {"triple_active": True}),
    ("kfc", {"kfc_active": True}),
    ("ghost", {"ghost_active": True}),
    ("knight", {"knight_active": True}),
    ("knight+3x", {"knight_active": True, "triple_active": True}),
    ("knight+kfc", {"knight_active": True, "kfc_active": True}),
    ("knight+ghost", {"knight_active": True, "ghost_active": True}),
    ("skate", {"skateboard_active": True}),
    ("skate+3x", {"skateboard_active": True, "triple_active": True}),
    ("skate+grow", {"skateboard_active": True, "grow_active": True}),
    ("skate+shrink", {"skateboard_active": True, "shrink_scale": 0.6}),
    ("poison base", {"poison_active": True, "poison_t": 0.85}),
    ("poison kfc", {"poison_active": True, "poison_t": 0.85, "kfc_active": True}),
    ("poison ghost", {"poison_active": True, "poison_t": 0.85, "ghost_active": True}),
    ("poison knight", {"poison_active": True, "poison_t": 0.85, "knight_active": True}),
]

TW, TH = 150, 168
COLS = 4
PAD_TOP = 26


def tile(flags):
    s = pygame.Surface((TW, TH))
    for y in range(TH):
        t = y / TH
        s.fill((int(120 - 40 * t), int(150 - 30 * t), int(200 - 20 * t)),
               (0, y, TW, 1))
    b = Bird()
    b.x, b.y = TW / 2, TH / 2 - 6
    for k, v in flags.items():
        setattr(b, k, v)
    b.draw(s, 0, 0)
    return s


def main():
    rows = (len(COMBOS) + COLS - 1) // COLS
    sheet = pygame.Surface((TW * COLS, (TH + PAD_TOP) * rows))
    sheet.fill((22, 26, 36))
    font = pygame.font.SysFont("monospace", 14, bold=True)
    for i, (label, flags) in enumerate(COMBOS):
        c, r = i % COLS, i // COLS
        x, y = c * TW, r * (TH + PAD_TOP)
        sheet.blit(font.render(label, True, (255, 235, 140)), (x + 6, y + 5))
        sheet.blit(tile(flags), (x, y + PAD_TOP))
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "docs", "pip_combos")
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, "phase1.png")
    pygame.image.save(sheet, path)
    print("saved", path, sheet.get_size())


if __name__ == "__main__":
    main()
