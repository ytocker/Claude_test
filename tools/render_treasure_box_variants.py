"""Render 5 TREASURE BOX visual-variant mockups for review.

For each variant in `game.treasure_box_variants.VARIANTS`, build the
same base scene (day-biome sky + ground + 2 stone pillars + Pip
mid-flight) and overlay the variant's carried-box + spill trail. Write
one PNG per variant under docs/treasure_box_variants/ at 3× scale with
a title strip so the design board reads clearly on GitHub.

Run headless:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        python tools/render_treasure_box_variants.py

Outputs five files plus a single contact-sheet `_all.png` that lays
the five variants side-by-side for quick comparison.
"""
import os
import pathlib
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

_REPO = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(_REPO))

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game import biome
from game.config import W, H, GROUND_Y, BIRD_X
from game.draw import (
    draw_mountains, draw_ground, lerp_color,
    UI_GOLD, UI_CREAM, NEAR_BLACK, WHITE,
)
from game.parrot import get_parrot
from game.entities import Pipe
from game.pillar_variants import _VARIANTS as PILLAR_VARIANTS, VARIANT_COUNT, _paint_stone
from game.treasure_box_variants import VARIANTS

SCALE   = 3
PAD     = 16
TITLE_H = 56


def _font(size):
    return pygame.font.Font(str(_REPO / "game" / "assets" / "LiberationSans-Bold.ttf"), size)


def _render_base() -> pygame.Surface:
    """Build the canonical day-time scene used as the backdrop for every
    variant: gradient sky, distant mountains, ground band, two stone
    pillars in the right two-thirds, Pip rendered mid-flap at BIRD_X."""
    pal = biome.palette_for_phase(0.0)  # day
    base = pygame.Surface((W, H)).convert()

    # Sky gradient
    top, mid, bot = pal["sky_top"], pal["sky_mid"], pal["sky_bot"]
    for y in range(H):
        if y < H * 0.5:
            t = y / (H * 0.5)
            base.fill(lerp_color(top, mid, t), pygame.Rect(0, y, W, 1))
        else:
            t = (y - H * 0.5) / (H * 0.5)
            base.fill(lerp_color(mid, bot, t), pygame.Rect(0, y, W, 1))

    draw_mountains(base, scroll=120.0, ground_y=GROUND_Y, w=W)
    draw_ground(base, ground_y=GROUND_Y, w=W, h=H, scroll=120.0)

    # Two stone pillars in the right portion of the scene so the scale
    # of the carried box reads against real gameplay scenery.
    for px, gy, seed_off in ((W * 0.55, H * 0.40, 3), (W * 0.85, H * 0.48, 11)):
        pipe = Pipe(x=px, gap_y=gy, gap_h=170.0)
        pipe.seed = seed_off
        idx = pipe.seed % VARIANT_COUNT
        top_sil, bot_sil, _decor = PILLAR_VARIANTS[idx]
        _paint_stone(base, pipe.top_rect, top_sil, pal, pipe.seed)
        _paint_stone(base, pipe.bot_rect, bot_sil, pal, pipe.seed + 1)

    return base


def _render_variant(name: str, label: str, draw_fn) -> pygame.Surface:
    base = _render_base().copy()

    # Pip mid-flap (frame 1 = wings down), slight tilt for "shaking" energy.
    # Bird sits high in the frame so the container + 4-coin spill cascade
    # below him has clean air to read against.
    bird_y = int(H * 0.30)
    parrot = get_parrot(frame_idx=1, tilt_deg=-6)
    base.blit(parrot, parrot.get_rect(center=(BIRD_X, bird_y)))

    # Variant overlay: the carried container + spill trail relative to Pip.
    draw_fn(base, bird_cx=BIRD_X, bird_cy=bird_y)

    # Upscale for a crisp review render.
    big = pygame.transform.scale(base, (W * SCALE, H * SCALE))
    bw, bh = big.get_size()

    out_w = bw + PAD * 2
    out_h = bh + PAD * 2 + TITLE_H
    out = pygame.Surface((out_w, out_h))
    # Title strip background — match the navy used by surprise-box preview.
    for y in range(out_h):
        t = y / max(1, out_h - 1)
        c = lerp_color((18, 28, 64), (8, 14, 36), t)
        pygame.draw.line(out, c, (0, y), (out_w - 1, y))
    out.blit(big, (PAD, PAD))

    # Caption
    f = _font(28)
    title = f.render(f"TREASURE BOX — {label}", True, UI_GOLD)
    sh    = f.render(f"TREASURE BOX — {label}", True, NEAR_BLACK)
    tr    = title.get_rect(center=(out_w // 2, bh + PAD * 2 + TITLE_H // 2 - 8))
    out.blit(sh, (tr.x + 2, tr.y + 2))
    out.blit(title, tr.topleft)
    sub = _font(16).render(
        "Pip shakes the box mid-flight — each flap drops a coin",
        True, UI_CREAM,
    )
    out.blit(sub, sub.get_rect(center=(out_w // 2, bh + PAD * 2 + TITLE_H // 2 + 14)))

    return out


def _render_contact_sheet(rendered: list[tuple[str, pygame.Surface]]) -> pygame.Surface:
    """5-up horizontal strip: all variants on one canvas for quick A/B."""
    if not rendered:
        return pygame.Surface((1, 1))
    cell_w, cell_h = rendered[0][1].get_size()
    gap = 24
    out_w = cell_w * len(rendered) + gap * (len(rendered) + 1)
    out_h = cell_h + gap * 2 + 56
    out = pygame.Surface((out_w, out_h))
    for y in range(out_h):
        t = y / max(1, out_h - 1)
        c = lerp_color((22, 30, 60), (6, 10, 28), t)
        pygame.draw.line(out, c, (0, y), (out_w - 1, y))
    for i, (_name, surf) in enumerate(rendered):
        x = gap + i * (cell_w + gap)
        out.blit(surf, (x, gap + 40))
    f = _font(34)
    title = f.render("TREASURE BOX — 5 design directions", True, UI_GOLD)
    sh    = f.render("TREASURE BOX — 5 design directions", True, NEAR_BLACK)
    tr    = title.get_rect(center=(out_w // 2, 28))
    out.blit(sh, (tr.x + 2, tr.y + 2))
    out.blit(title, tr.topleft)
    return out


def main() -> int:
    out_dir = _REPO / "docs" / "treasure_box_variants"
    out_dir.mkdir(parents=True, exist_ok=True)

    rendered = []
    for slug, label, fn in VARIANTS:
        surf = _render_variant(slug, label, fn)
        path = out_dir / f"{slug}.png"
        pygame.image.save(surf, path)
        print(f"wrote {path}")
        rendered.append((slug, surf))

    sheet = _render_contact_sheet(rendered)
    sheet_path = out_dir / "_all.png"
    pygame.image.save(sheet, sheet_path)
    print(f"wrote {sheet_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
