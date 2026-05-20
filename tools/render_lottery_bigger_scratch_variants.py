"""Render 5 LOTTERY scratch-card variants with a BIGGER scratch
panel + "? ? ?" so the icon is more noticeable mid-game. Each
variant takes a different approach to enlarging the panel while
keeping the gold-card/foil-sparkle lottery identity:

  B1 — slim LUCKY banner + bottom row removed; panel fills the
       middle ~70% of the card
  B2 — corner LUCKY pennant + tiny $ chip in opposite corner;
       panel takes ~85% of the card
  B3 — banner kept; bottom row collapses into a single $ pip
       tucked inside the panel's bottom-right
  B4 — full-bleed scratch panel edge-to-edge; LUCKY caption is a
       small chip overlay riding the top edge
  B5 — 3-cell match-style scratch (each "?" in its own large
       panel) with a tiny LUCKY chip on top

Reuses the shared chassis/dashed-rim/silver-panel helpers from
`render_lottery_scratch_variants.py`. Painted at 6× supersample
on a 56×42 native canvas, tilted ±5° to mirror the live anim,
and composited on a real gameplay frame for context.

Run headless:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        python tools/render_lottery_bigger_scratch_variants.py
"""

import math
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
from tools.render_lottery_scratch_variants import (
    _font, _ss_paint, _v_gradient_rect, _sparkle,
    _gold_card_base,
    GOLD_HI, GOLD_MID, GOLD_LO, GOLD_DEEP, STROKE, CHROME,
    SILVER_HI, SILVER_LO, CREAM, NAVY, RED, RED_HI,
)


def _silver_panel(big, rect, radius=None):
    """Clipped silver scratch-panel: gradient fill + diagonal hatch
    + navy outline, all painted to a sub-surface so the hatch
    diagonals can't bleed past the panel rect onto the card body.
    (The shared `_silver_panel` from render_lottery_scratch_variants
    paints the hatch directly onto the parent surface, which leaks
    when the panel is large.)"""
    if radius is None:
        radius = max(1, rect.height // 8)
    sub = pygame.Surface(rect.size, pygame.SRCALPHA)
    sub_rect = sub.get_rect()
    # Gradient fill.
    _v_gradient_rect(sub, sub_rect, SILVER_HI, SILVER_LO,
                     radius=radius)
    # Diagonal cross-hatch painted ONTO a fully-opaque rounded mask so
    # it can't slip outside the panel.
    hatch = pygame.Surface(rect.size, pygame.SRCALPHA)
    for off in range(-rect.height, rect.width,
                     max(8, rect.height // 6)):
        x0 = off
        x1 = x0 + rect.height
        pygame.draw.line(hatch, (180, 185, 200, 90),
                         (x0, 0), (x1, rect.height),
                         max(1, rect.height // 60))
    mask = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255),
                     mask.get_rect(), border_radius=radius)
    hatch.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    sub.blit(hatch, (0, 0))
    # Outline.
    pygame.draw.rect(sub, NAVY, sub_rect,
                     width=max(1, rect.height // 18),
                     border_radius=radius)
    big.blit(sub, rect.topleft)


_OUT = os.path.join(_REPO, "docs", "screenshots",
                    "lottery_bigger_scratch")
os.makedirs(_OUT, exist_ok=True)


def _draw_question_marks(big, panel, text="? ? ?",
                          font_frac=0.85, shadow=True,
                          pad_x_frac=0.06, pad_y_frac=0.08):
    """Bold navy "? ? ?" centred in the panel with a cream highlight
    above + a dark stroke shadow for legibility on the silver foil.

    Auto-scales the font down so the rendered text fits within
    `panel` minus a fractional horizontal+vertical padding, so the
    glyphs never crash into the panel border."""
    max_w = max(1, panel.width - int(panel.width * pad_x_frac * 2))
    max_h = max(1, panel.height - int(panel.height * pad_y_frac * 2))
    size = max(4, int(panel.height * font_frac))
    # Walk down by 2 px until the rendered text fits both dimensions.
    while size > 6:
        f = _font(size)
        w_, h_ = f.size(text)
        if w_ <= max_w and h_ <= max_h:
            break
        size -= 2
    f = _font(size)
    txt = f.render(text, True, NAVY)
    hl  = f.render(text, True, CREAM)
    tr = txt.get_rect(center=panel.center)
    if shadow:
        sh_ = f.render(text, True, STROKE)
        big.blit(sh_, sh_.get_rect(center=(tr.centerx + 1,
                                            tr.centery + 1)))
    big.blit(hl, hl.get_rect(center=(tr.centerx, tr.centery - 1)))
    big.blit(txt, tr)


def _lucky_banner(big, rect, SS, font_frac=0.9):
    """Standard red gradient banner with ribbon notches + LUCKY text."""
    _v_gradient_rect(big, rect, RED_HI, RED, radius=2 * SS)
    pygame.draw.rect(big, STROKE, rect, max(1, SS // 2),
                     border_radius=2 * SS)
    notch_w = int(2 * SS)
    pygame.draw.polygon(big, RED, [
        (rect.left, rect.top),
        (rect.left - notch_w, rect.centery),
        (rect.left, rect.bottom),
    ])
    pygame.draw.polygon(big, RED, [
        (rect.right, rect.top),
        (rect.right + notch_w, rect.centery),
        (rect.right, rect.bottom),
    ])
    fb = _font(int(rect.height * font_frac))
    sh_ = fb.render("LUCKY", True, STROKE)
    bt  = fb.render("LUCKY", True, CREAM)
    big.blit(sh_, sh_.get_rect(center=(rect.centerx + 1,
                                         rect.centery + 1)))
    big.blit(bt, bt.get_rect(center=rect.center))


def _coin_chip(big, cx, cy, r, label="$"):
    """Compact gold coin disc with $ glyph — for corner accents."""
    for shrink, col in ((1.00, GOLD_DEEP), (0.86, GOLD_LO),
                        (0.70, GOLD_MID), (0.52, GOLD_HI)):
        pygame.draw.circle(big, col, (cx, cy),
                           max(1, int(r * shrink)))
    pygame.draw.circle(big, CHROME, (cx, cy), r, 1)
    pygame.draw.circle(big, STROKE, (cx, cy), r, 1)
    f = _font(int(r * 1.7))
    sh_ = f.render(label, True, STROKE)
    glyph = f.render(label, True, CREAM)
    gr = glyph.get_rect(center=(cx, cy))
    big.blit(sh_, sh_.get_rect(center=(gr.centerx + 1,
                                         gr.centery + 1)))
    big.blit(glyph, gr)


# ── 5 variants ──────────────────────────────────────────────────────────────

def draw_b1_slim_banner(surf, cx, cy, pulse):
    """B1 — Slim LUCKY banner at top + giant scratch panel below.
    Bottom decorative row removed entirely."""

    def paint(big, SS):
        card, inner = _gold_card_base(big, SS)
        # Slim banner — thinner than the live version but tall enough
        # to keep the LUCKY caption legible.
        banner_h = 7 * SS
        banner = pygame.Rect(inner.left + 4 * SS, inner.top + SS,
                             inner.width - 8 * SS, banner_h)
        _lucky_banner(big, banner, SS, font_frac=0.85)
        # Scratch panel fills everything below the banner — no bottom
        # row, so the panel extends all the way to the inner bottom.
        panel = pygame.Rect(inner.left + 2 * SS,
                            banner.bottom + 2 * SS,
                            inner.width - 4 * SS,
                            inner.bottom - banner.bottom - 3 * SS)
        _silver_panel(big, panel, radius=2 * SS)
        # Wider horizontal padding so the outer "?"s don't kiss the
        # silver foil border.
        _draw_question_marks(big, panel, font_frac=0.85,
                              pad_x_frac=0.12, pad_y_frac=0.10)

    icon = _ss_paint(paint)
    tilt = math.sin(pulse * 0.7) * 5
    rot = pygame.transform.rotate(icon, tilt)
    surf.blit(rot, rot.get_rect(center=(cx, cy)))


def draw_b2_corner_pennant(surf, cx, cy, pulse):
    """B2 — LUCKY shrunk to a tiny corner pennant (top-left). Tiny $
    coin chip in the opposite corner (top-right). Panel dominates
    ~85% of the card."""

    def paint(big, SS):
        card, inner = _gold_card_base(big, SS)
        # Corner pennant — small red rounded chip with LUCKY text.
        # 5*SS tall keeps the LUCKY caption legible at icon scale.
        chip = pygame.Rect(0, 0, 17 * SS, 5 * SS)
        chip.topleft = (inner.left + 1 * SS, inner.top + SS)
        _v_gradient_rect(big, chip, RED_HI, RED, radius=int(SS * 1.5))
        pygame.draw.rect(big, STROKE, chip, max(1, SS // 2),
                         border_radius=int(SS * 1.5))
        fc = _font(int(chip.height * 0.85))
        sh_ = fc.render("LUCKY", True, STROKE)
        ct  = fc.render("LUCKY", True, CREAM)
        big.blit(sh_, sh_.get_rect(center=(chip.centerx + 1,
                                             chip.centery + 1)))
        big.blit(ct, ct.get_rect(center=chip.center))
        # Mini $ chip top-right.
        coin_r = int(SS * 2.0)
        _coin_chip(big, inner.right - coin_r - SS,
                    inner.top + coin_r + SS, coin_r, "$")
        # Giant scratch panel — everything below the chip row.
        panel = pygame.Rect(inner.left + 2 * SS,
                            chip.bottom + 2 * SS,
                            inner.width - 4 * SS,
                            inner.bottom - chip.bottom - 3 * SS)
        _silver_panel(big, panel, radius=2 * SS)
        _draw_question_marks(big, panel, font_frac=0.9)

    icon = _ss_paint(paint)
    tilt = math.sin(pulse * 0.7) * 5
    rot = pygame.transform.rotate(icon, tilt)
    surf.blit(rot, rot.get_rect(center=(cx, cy)))


def draw_b3_banner_plus_inline_coin(surf, cx, cy, pulse):
    """B3 — Full LUCKY banner kept (so the lottery identity reads
    strong at-a-glance) but the bottom row collapses into a single
    small $ coin tucked INSIDE the panel's bottom-right corner.
    Panel is taller than the live version since no row is below."""

    def paint(big, SS):
        card, inner = _gold_card_base(big, SS)
        banner_h = 7 * SS
        banner = pygame.Rect(inner.left + 4 * SS, inner.top + SS,
                             inner.width - 8 * SS, banner_h)
        _lucky_banner(big, banner, SS, font_frac=0.92)
        # Panel takes the rest of the card.
        panel = pygame.Rect(inner.left + 2 * SS,
                            banner.bottom + 2 * SS,
                            inner.width - 4 * SS,
                            inner.bottom - banner.bottom - 3 * SS)
        _silver_panel(big, panel, radius=2 * SS)
        _draw_question_marks(big, panel, font_frac=0.88)
        # Mini $ coin inside the bottom-right corner of the panel,
        # overlapping the silver foil so it reads as "what you might
        # win".
        coin_r = int(SS * 2.2)
        _coin_chip(big, panel.right - coin_r - SS,
                    panel.bottom - coin_r - SS, coin_r, "$")

    icon = _ss_paint(paint)
    tilt = math.sin(pulse * 0.7) * 5
    rot = pygame.transform.rotate(icon, tilt)
    surf.blit(rot, rot.get_rect(center=(cx, cy)))


def draw_b4_full_bleed(surf, cx, cy, pulse):
    """B4 — Full-bleed scratch panel covering the card edge-to-edge
    inside the chrome rim. LUCKY is a small overlay chip riding the
    top edge of the panel. Most extreme "scratch is the icon"
    variant."""

    def paint(big, SS):
        card, inner = _gold_card_base(big, SS)
        # Panel fills the entire `inner` area.
        panel = inner.inflate(-2 * SS, -2 * SS)
        _silver_panel(big, panel, radius=2 * SS)
        _draw_question_marks(big, panel, font_frac=0.95)
        # LUCKY chip overlay along the top edge.
        chip = pygame.Rect(0, 0, 20 * SS, 5 * SS)
        chip.midtop = (panel.centerx, panel.top - 1 * SS)
        _v_gradient_rect(big, chip, RED_HI, RED,
                         radius=int(SS * 1.5))
        pygame.draw.rect(big, STROKE, chip, max(1, SS // 2),
                         border_radius=int(SS * 1.5))
        fc = _font(int(chip.height * 0.88))
        sh_ = fc.render("LUCKY", True, STROKE)
        ct  = fc.render("LUCKY", True, CREAM)
        big.blit(sh_, sh_.get_rect(center=(chip.centerx + 1,
                                             chip.centery + 1)))
        big.blit(ct, ct.get_rect(center=chip.center))

    icon = _ss_paint(paint)
    tilt = math.sin(pulse * 0.7) * 5
    rot = pygame.transform.rotate(icon, tilt)
    surf.blit(rot, rot.get_rect(center=(cx, cy)))


def draw_b5_triple_cell(surf, cx, cy, pulse):
    """B5 — Three large scratch cells side-by-side, each with a
    single big "?". Mimics a real-world scratch ticket where each
    box is its own panel. Tiny LUCKY chip riding the top edge."""

    def paint(big, SS):
        card, inner = _gold_card_base(big, SS)
        # Tiny LUCKY chip riding the top.
        chip = pygame.Rect(0, 0, 20 * SS, 5 * SS)
        chip.midtop = (inner.centerx, inner.top + 1)
        _v_gradient_rect(big, chip, RED_HI, RED,
                         radius=int(SS * 1.5))
        pygame.draw.rect(big, STROKE, chip, max(1, SS // 2),
                         border_radius=int(SS * 1.5))
        fc = _font(int(chip.height * 0.88))
        sh_ = fc.render("LUCKY", True, STROKE)
        ct  = fc.render("LUCKY", True, CREAM)
        big.blit(sh_, sh_.get_rect(center=(chip.centerx + 1,
                                             chip.centery + 1)))
        big.blit(ct, ct.get_rect(center=chip.center))
        # Cell row below the chip.
        cell_top = chip.bottom + 2 * SS
        cell_bot = inner.bottom - 2 * SS
        cell_h = cell_bot - cell_top
        gap = 1 * SS
        cell_w = (inner.width - 4 * SS - 2 * gap) // 3
        for i in range(3):
            x0 = inner.left + 2 * SS + i * (cell_w + gap)
            cell = pygame.Rect(x0, cell_top, cell_w, cell_h)
            _silver_panel(big, cell, radius=int(SS * 1.5))
            # Generous inset so the "?" sits comfortably inside the
            # silver cell, not bleeding past the navy border.
            _draw_question_marks(big, cell, text="?", font_frac=0.95,
                                  pad_x_frac=0.18, pad_y_frac=0.18)

    icon = _ss_paint(paint)
    tilt = math.sin(pulse * 0.7) * 5
    rot = pygame.transform.rotate(icon, tilt)
    surf.blit(rot, rot.get_rect(center=(cx, cy)))


VARIANTS = [
    ("B1_slim_banner",     draw_b1_slim_banner,
     "B1: slim LUCKY banner + bottom row gone, panel ~70% of card"),
    ("B2_corner_pennant",  draw_b2_corner_pennant,
     "B2: corner LUCKY pennant + tiny $ chip, panel ~85% of card"),
    ("B3_banner_inline_$", draw_b3_banner_plus_inline_coin,
     "B3: full LUCKY banner kept, $ tucked inside panel bottom-right"),
    ("B4_full_bleed",      draw_b4_full_bleed,
     "B4: full-bleed scratch panel, LUCKY rides the top edge"),
    ("B5_triple_cell",     draw_b5_triple_cell,
     "B5: three big match-3 cells with one ? each + tiny LUCKY chip"),
]


def _icon_zoom_png(draw_fn, label):
    base = pygame.Surface((56, 42), pygame.SRCALPHA)
    draw_fn(base, 28, 21, pulse=1.6)
    big = pygame.transform.scale(base, (56 * 6, 42 * 6))
    pygame.draw.rect(big, (255, 215, 0), big.get_rect(), 2)
    return big


def _ingame_png(draw_fn, label):
    world = build_world()
    frame = render_play_scene(world)
    icon_cx = int(world.bird.x) + 110
    icon_cy = int(world.bird.y)
    base = pygame.Surface((56, 42), pygame.SRCALPHA)
    draw_fn(base, 28, 21, pulse=1.6)
    frame.blit(base, base.get_rect(center=(icon_cx, icon_cy)))
    return frame


def main():
    saved = []
    for label, fn, caption in VARIANTS:
        icon_zoom = _icon_zoom_png(fn, label)
        ingame = _ingame_png(fn, label)
        zoom_path = os.path.join(_OUT, f"{label}.png")
        ingame_path = os.path.join(_OUT, f"{label}_ingame.png")
        pygame.image.save(icon_zoom, zoom_path)
        pygame.image.save(ingame, ingame_path)
        saved.append((label, caption, icon_zoom))
        print(f"saved {zoom_path}")
        print(f"saved {ingame_path}")

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
    sheet_path = os.path.join(_OUT, "00_contact_sheet.png")
    pygame.image.save(sheet, sheet_path)
    print(f"saved {sheet_path}")

    base = ("https://raw.githubusercontent.com/ytocker/skybit/"
            "v5_powerups/docs/screenshots/lottery_bigger_scratch")
    print()
    print(f"{base}/00_contact_sheet.png")
    for label, caption, _ in saved:
        print(f"{base}/{label}.png  -- {caption}")
        print(f"{base}/{label}_ingame.png")


if __name__ == "__main__":
    main()
