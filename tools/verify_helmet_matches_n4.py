"""Forensic pixel-by-pixel verifier — proves the live `_draw_helmet`
renders byte-identical to N4 from `_h4_variant_at(fa_x=8, ra_x=4,
jx=6, cx=14)`.

Outputs four PNGs under
docs/screenshots/skateboard_variants/side_view_v2/verify/ :

  LIVE.png         — current game/entities.py `_draw_helmet`
  N4_iterator.png  — iterator's N4 painted on the same bird
  DIFF.png         — bright red where pixels differ, dim grey
                     where they match
  SIDE_BY_SIDE.png — labelled comparison

Bird state is identical between the two renders (same world,
helmet is the only thing that changes between draws).
"""

import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

pygame.init()
pygame.display.set_mode((1, 1))

from tools.render_helmet_side_view_variants import (
    build_world, render_play_scene, _label_band,
)
from tools.render_helmet_chinstrap_iterate import _h4_variant_at


_OUT = os.path.join(_REPO, "docs", "screenshots",
                    "skateboard_variants", "side_view_v2", "verify")
os.makedirs(_OUT, exist_ok=True)


def _render_one_world_twice():
    """Build ONE world, render it twice — first with the LIVE
    _draw_helmet (the live Bird method), then with the N4 iterator
    variant monkey-patched onto the SAME bird. This guarantees
    everything except the helmet is pixel-identical (no pipe-seed
    drift from a second build_world call)."""
    world = build_world()
    original_helmet = world.bird._draw_helmet  # bound method

    # Render 1 — LIVE helmet.
    img_live = render_play_scene(world)

    # Render 2 — monkey-patch to N4 variant.
    n4_fn = _h4_variant_at(fa_x=8, ra_x=4, jx=6, cx=14)
    world.bird._draw_helmet = (
        lambda surf, cx, cy, flipped, b=world.bird, _fn=n4_fn:
            _fn(b, surf, cx, cy, flipped)
    )
    img_n4 = render_play_scene(world)

    # Restore (not strictly needed; we're done with the world).
    world.bird._draw_helmet = original_helmet
    return img_live, img_n4


def _pixel_diff(a, b):
    """Returns (diff_surf, n_diff_pixels, total_pixels)."""
    w, h = a.get_size()
    assert b.get_size() == (w, h), "size mismatch"
    diff = pygame.Surface((w, h))
    diff.fill((20, 20, 24))
    a_pa = pygame.PixelArray(a)
    b_pa = pygame.PixelArray(b)
    d_pa = pygame.PixelArray(diff)
    n_diff = 0
    diff_red = a.map_rgb((255, 40, 40))
    for y in range(h):
        for x in range(w):
            if a_pa[x, y] != b_pa[x, y]:
                d_pa[x, y] = diff_red
                n_diff += 1
    del a_pa, b_pa, d_pa
    return diff, n_diff, w * h


def main():
    print("rendering LIVE + N4 on the same world ...")
    img_live, img_n4 = _render_one_world_twice()

    pygame.image.save(img_live, os.path.join(_OUT, "LIVE.png"))
    pygame.image.save(img_n4,   os.path.join(_OUT, "N4_iterator.png"))

    print("computing pixel diff ...")
    img_diff, n_diff, total = _pixel_diff(img_live, img_n4)
    pygame.image.save(img_diff, os.path.join(_OUT, "DIFF.png"))

    pct = 100.0 * n_diff / total
    print()
    print(f"  total pixels:     {total}")
    print(f"  differing pixels: {n_diff} ({pct:.3f}%)")
    print(f"  identical:        {total - n_diff}")

    # Side-by-side composite with labels.
    w, h = img_live.get_size()
    band_h = 56
    gap = 12
    sheet = pygame.Surface((3 * w + 2 * gap + 24, h + band_h + 24))
    sheet.fill((10, 12, 24))
    sheet.blit(img_live, (12, 12))
    sheet.blit(img_n4,   (12 + w + gap, 12))
    sheet.blit(img_diff, (12 + 2 * (w + gap), 12))
    sheet.blit(_label_band(w, "LIVE", "game/entities.py:_draw_helmet"),
               (12, 12 + h))
    sheet.blit(_label_band(w, "N4 ITERATOR",
                           "_h4_variant_at(8,4,6,14) @ commit 8464059"),
               (12 + w + gap, 12 + h))
    sheet.blit(_label_band(w, "DIFF",
                           f"{n_diff} of {total} px ({pct:.3f}%) differ"),
               (12 + 2 * (w + gap), 12 + h))
    pygame.image.save(sheet, os.path.join(_OUT, "SIDE_BY_SIDE.png"))
    print(f"saved 4 files to {_OUT}")


if __name__ == "__main__":
    main()
