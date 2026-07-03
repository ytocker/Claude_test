"""Headless preview for the COURT GREEN shoe core.

Renders draw_shoe at hero / mid / foot sizes in a labelled row on a dark navy
field so the silhouette and cues can be checked across the full scale range.
Run with SDL_VIDEODRIVER=dummy; saves preview.png beside this file.
"""
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from draw import draw_shoe


_NAVY = (18, 14, 40)
_LABEL = (220, 224, 235)
# (box_w, box_h, caption) — the three sizes the same core must serve.
_SIZES = [(120, 72, "120x72"), (48, 30, "48x30"), (16, 11, "16x11")]


def main():
    pygame.init()
    font = pygame.font.SysFont("monospace", 13)

    pad = 26
    gap = 34
    cell_w = max(bw for bw, _, _ in _SIZES) + gap
    total_w = pad * 2 + sum(cell_w for _ in _SIZES)
    total_h = 248

    surf = pygame.Surface((total_w, total_h))
    surf.fill(_NAVY)

    cx = pad
    base_y = 24
    row_h = max(bh for _, bh, _ in _SIZES)
    for bw, bh, cap in _SIZES:
        # Bottom-align each shoe on a shared ground line so soles agree.
        bx = cx + (cell_w - gap - bw) // 2
        by = base_y + (row_h - bh)
        draw_shoe(surf, bx, by, bw, bh, facing=1)
        label = font.render(cap, True, _LABEL)
        surf.blit(label, (cx + (cell_w - gap - label.get_width()) // 2,
                          base_y + row_h + 14))
        cx += cell_w

    # A facing=-1 (toe-left) check beside the hero, so mirroring is verified.
    draw_shoe(surf, pad, base_y + row_h + 44, 120, 72, facing=-1)
    flip_lbl = font.render("facing=-1", True, _LABEL)
    surf.blit(flip_lbl, (pad, base_y + row_h + 44 + 74))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "preview.png")
    pygame.image.save(surf, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
