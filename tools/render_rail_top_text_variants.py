"""Render 5 V1-Simple-Train variants with different SHORT, LARGE,
BOLD top-text captions. The chimney sits at ~14 native px from
the card top so the text has ~10 native px of vertical room.
The vendored LiberationSans-Bold font (`_get_float_font`) is
already bold; the only thing each variant changes is the WORD
and the font size.

Run headless:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        python tools/render_rail_top_text_variants.py
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

from tools.render_helmet_side_view_variants import _label_band
from tools.render_rail_train_variants import (
    _paint_ticket_chassis, NEAR_BLACK, SS, NATIVE_W, NATIVE_H,
)
from game.entities import _get_float_font


_OUT = os.path.join(_REPO, "docs", "screenshots",
                    "rail_train_variants")


TEXT_VARIANTS = [
    ("T1_RAIL",  "RAIL",  5.0, "T1: RAIL  (4 chars, font SS*5.0)"),
    ("T2_TRAIN", "TRAIN", 4.5, "T2: TRAIN (5 chars, font SS*4.5)"),
    ("T3_PASS",  "PASS",  5.0, "T3: PASS  (4 chars, font SS*5.0)"),
    ("T4_GO",    "GO!",   6.0, "T4: GO!   (3 chars, font SS*6.0)"),
    ("T5_RIDE",  "RIDE",  5.0, "T5: RIDE  (4 chars, font SS*5.0)"),
]


def _paint_loco_only(big, scale, cx, cy):
    """Copy of V1 painter (cab + boiler + chimney + cowcatcher +
    2 spoked drivers + coupling rod) — inlined to avoid pulling
    in the train-variants tool's whole VARIANTS table."""
    import math
    from tools.render_rail_train_variants import (
        INK, CREAM, _spoked_wheel, _cowcatcher,
    )
    boiler_w = int(SS * 18 * scale)
    boiler_h = int(SS * 6.5 * scale)
    boiler = pygame.Rect(0, 0, boiler_w, boiler_h)
    boiler.midright = (cx + int(SS * 8 * scale), cy)
    pygame.draw.rect(big, INK, boiler,
                     border_radius=max(1, int(SS * 0.8 * scale)))
    cab_w = int(SS * 6 * scale)
    cab_h = int(SS * 8 * scale)
    cab = pygame.Rect(0, 0, cab_w, cab_h)
    cab.midright = (boiler.left, cy)
    pygame.draw.rect(big, INK, cab,
                     border_radius=max(1, int(SS * 0.6 * scale)))
    roof = pygame.Rect(0, 0, cab_w + int(SS * 1.2 * scale),
                        max(1, int(SS * 0.8 * scale)))
    roof.midbottom = (cab.centerx, cab.top + max(1, SS // 3))
    pygame.draw.rect(big, INK, roof)
    stack_w = max(2, int(SS * 1.8 * scale))
    stack_h = max(3, int(SS * 3.5 * scale))
    stack_x = boiler.right - int(SS * 4 * scale) - stack_w // 2
    stack = pygame.Rect(stack_x, boiler.top - stack_h,
                         stack_w, stack_h)
    pygame.draw.rect(big, INK, stack)
    flare = pygame.Rect(0, 0, int(stack_w * 1.8),
                         max(1, int(SS * 0.7 * scale)))
    flare.midbottom = (stack.centerx, stack.top)
    pygame.draw.rect(big, INK, flare)
    wheel_r = max(3, int(SS * 2.4 * scale))
    gap = max(1, int(SS * 0.4 * scale))
    wheel_cy = boiler.bottom + wheel_r + gap
    ground_y = wheel_cy + wheel_r
    drive_xs = (
        boiler.left + int(boiler.width * 0.05),
        boiler.left + int(boiler.width * 0.72),
    )
    rod_h = max(2, int(SS * 0.9 * scale))
    rod_y = wheel_cy - int(wheel_r * 0.30) - rod_h // 2
    pygame.draw.rect(big, INK,
                     (drive_xs[0], rod_y,
                      drive_xs[1] - drive_xs[0], rod_h))
    for wx in drive_xs:
        _spoked_wheel(big, wx, wheel_cy, wheel_r, scale)
        pygame.draw.circle(big, CREAM, (wx, rod_y + rod_h // 2),
                           max(1, int(SS * 0.5 * scale)))
    _cowcatcher(big,
                (boiler.right, boiler.bottom - SS // 3),
                ground_y, scale)


def _build_icon(text, font_scale):
    sw, sh = NATIVE_W * SS, NATIVE_H * SS
    big = pygame.Surface((sw, sh), pygame.SRCALPHA)
    # Paint the ticket chassis MINUS its RAILWAY caption.
    card = pygame.Rect(3 * SS, 3 * SS, sw - 6 * SS, sh - 6 * SS)
    pygame.draw.rect(big, (228, 210, 170), card)  # sepia
    pygame.draw.rect(big, NEAR_BLACK, card, max(2, int(SS * 1.4)))
    inner = card.inflate(-int(SS * 3.5), -int(SS * 3.5))
    pygame.draw.rect(big, NEAR_BLACK, inner, max(1, int(SS * 0.6)))
    # Big bold black caption.
    f = _get_float_font(int(SS * font_scale))
    hdr = f.render(text, True, NEAR_BLACK)
    big.blit(hdr, hdr.get_rect(
        center=(card.centerx, card.top + int(SS * 4.5))))
    # Locomotive — centred a touch lower than usual to leave the
    # top clear for the big caption.
    _paint_loco_only(big, 1.0,
                      card.centerx, card.centery + int(SS * 3))
    return pygame.transform.smoothscale(big, (NATIVE_W, NATIVE_H))


def _zoom(icon, factor=8):
    big = pygame.transform.scale(icon,
                                  (NATIVE_W * factor, NATIVE_H * factor))
    pygame.draw.rect(big, (255, 215, 0), big.get_rect(), 2)
    return big


def main():
    saved = []
    for label, text, scale, caption in TEXT_VARIANTS:
        icon = _build_icon(text, scale)
        path = os.path.join(_OUT, f"{label}.png")
        pygame.image.save(_zoom(icon), path)
        saved.append((label, caption, _zoom(icon, factor=6)))
        print(f"saved {path}")
    cell_w = saved[0][2].get_width()
    cell_h = saved[0][2].get_height()
    band_h = 56
    gap = 12
    sheet_w = len(saved) * cell_w + (len(saved) - 1) * gap + 24
    sheet_h = cell_h + band_h + 24
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((10, 12, 24))
    for idx, (label, caption, icon) in enumerate(saved):
        x = 12 + idx * (cell_w + gap)
        sheet.blit(icon, (x, 12))
        band = _label_band(cell_w, label, caption, height=band_h)
        sheet.blit(band, (x, 12 + cell_h))
    sheet_path = os.path.join(_OUT, "00_top_text_sheet.png")
    pygame.image.save(sheet, sheet_path)
    print(f"saved {sheet_path}")
    base = ("https://raw.githubusercontent.com/ytocker/skybit/"
            "v5_powerups/docs/screenshots/rail_train_variants")
    print()
    print(f"{base}/00_top_text_sheet.png")
    for label, caption, _ in saved:
        print(f"{base}/{label}.png  -- {caption}")


if __name__ == "__main__":
    main()
