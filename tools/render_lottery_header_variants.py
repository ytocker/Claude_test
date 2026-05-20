"""Render 5 LOTTERY scratch-card icon candidates — third
iteration, branching from L1. Each candidate keeps L1's exact
base (gold gradient body + chrome perimeter + dashed dark-gold
inner stroke + silver "? ? ?" foil panel + corner sparkles)
and adds:

  * a header text caption above the foil panel
  * one or two extra design elements

All painted at 6× supersample to a 56×42 footprint, smoothscale
down. Saved as zoom + ingame composites + 5-cell contact sheet.

Run headless:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        python tools/render_lottery_header_variants.py
"""

import math
import os
import random
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

pygame.init()
pygame.display.set_mode((1, 1))

# Reuse L1's helpers + palette from the round-2 renderer.
from tools.render_lottery_scratch_variants import (
    _ss_paint, _font, _v_gradient_rect, _star_polygon, _sparkle,
    _dashed_rect, _gold_card_base, _silver_panel,
    GOLD_HI, GOLD_MID, GOLD_LO, GOLD_DEEP, STROKE,
    CHROME, CHROME_LO, SILVER_HI, SILVER_LO,
    CREAM, NAVY, WHITE, RED, RED_HI, SHADOW,
)
from tools.render_helmet_side_view_variants import (
    build_world, render_play_scene, _label_band,
)


_OUT = os.path.join(_REPO, "docs", "screenshots",
                    "lottery_header_variants")
os.makedirs(_OUT, exist_ok=True)


CLOVER_GREEN = (60, 140, 70)


# ── shared shape helpers ────────────────────────────────────────────────────

def _coin_disc(surf, cx, cy, r, SS, label="$"):
    """Small shaded gold coin with chrome rim + cream label."""
    pygame.draw.circle(surf, (0, 0, 0, 60), (cx, cy + SS + 1), r + SS)
    for shrink, col in ((1.00, GOLD_DEEP),
                        (0.86, GOLD_LO),
                        (0.70, GOLD_MID),
                        (0.52, GOLD_HI)):
        pygame.draw.circle(surf, col, (cx, cy), max(1, int(r * shrink)))
    pygame.draw.circle(surf, CHROME, (cx, cy), r, max(1, SS // 2))
    pygame.draw.circle(surf, STROKE, (cx, cy), r, max(1, SS // 3))
    f = _font(int(r * 1.7))
    glyph = f.render(label, True, STROKE)
    hl    = f.render(label, True, CREAM)
    gr = glyph.get_rect(center=(cx, cy))
    surf.blit(hl, hl.get_rect(center=(gr.centerx, gr.centery - SS)))
    surf.blit(glyph, gr)


def _clover(surf, cx, cy, leaf_r, SS):
    """Tiny 4-leaf clover stamp."""
    offsets = [(-leaf_r // 2, -leaf_r // 2),
               ( leaf_r // 2, -leaf_r // 2),
               (-leaf_r // 2,  leaf_r // 2),
               ( leaf_r // 2,  leaf_r // 2)]
    for ox, oy in offsets:
        pygame.draw.circle(surf, CLOVER_GREEN,
                           (cx + ox, cy + oy), leaf_r)
        pygame.draw.circle(surf, STROKE,
                           (cx + ox, cy + oy), leaf_r,
                           max(1, SS // 3))
    # Stem.
    pygame.draw.line(surf, STROKE,
                     (cx, cy + leaf_r),
                     (cx + SS, cy + int(leaf_r * 2.2)),
                     max(1, SS // 2))


def _crown(surf, cx, cy_base, w, h, SS):
    """Three-pointed crown silhouette centred at (cx, cy_base) with
    cy_base = bottom edge of crown."""
    # Crown shape: rectangle base + 3 spikes.
    base_h = int(h * 0.35)
    base = pygame.Rect(0, 0, w, base_h)
    base.midbottom = (cx, cy_base)
    pygame.draw.rect(surf, CREAM, base, border_radius=SS)
    pygame.draw.rect(surf, STROKE, base, max(1, SS // 2),
                     border_radius=SS)
    # 3 spike triangles above the base.
    spike_top = cy_base - h
    spike_w = w // 3
    for i in (0, 1, 2):
        x = base.left + spike_w * i + spike_w // 2
        # Middle spike is tallest.
        peak_y = spike_top + (0 if i == 1 else int(h * 0.25))
        pts = [
            (x - spike_w // 2 + SS, base.top + SS),
            (x,                      peak_y),
            (x + spike_w // 2 - SS, base.top + SS),
        ]
        pygame.draw.polygon(surf, CREAM, pts)
        pygame.draw.polygon(surf, STROKE, pts, max(1, SS // 2))
        # Tiny gem dot at each peak.
        pygame.draw.circle(surf, RED_HI, (x, peak_y + SS), max(1, SS))


def _starburst_seal(surf, cx, cy, r, SS, points=8):
    """Red 8-point foil seal with cream centre + small star."""
    pts = _star_polygon(cx, cy, r, r * 0.62, points)
    pygame.draw.polygon(surf, RED_HI, pts)
    pygame.draw.polygon(surf, STROKE, pts, max(1, SS // 2))
    pygame.draw.circle(surf, CREAM, (cx, cy), int(r * 0.50))
    pygame.draw.circle(surf, RED, (cx, cy), int(r * 0.50),
                       max(1, SS // 2))
    _sparkle(surf, cx, cy, int(r * 0.40), colour=CREAM)


def _header_plaque(surf, rect, text, SS, fill=NAVY, text_col=CREAM,
                   top_hl=CHROME):
    """Dark plaque with chrome top-edge highlight + cream caption."""
    pygame.draw.rect(surf, fill, rect, border_radius=SS)
    pygame.draw.rect(surf, STROKE, rect, max(1, SS // 2),
                     border_radius=SS)
    # 1-SS chrome highlight along the top edge.
    pygame.draw.line(surf, top_hl,
                     (rect.left + SS, rect.top + 1),
                     (rect.right - SS, rect.top + 1),
                     max(1, SS // 2))
    f = _font(int(rect.height * 0.78))
    t = f.render(text, True, text_col)
    surf.blit(t, t.get_rect(center=rect.center))


def _l1_panel_and_text(big, panel_rect, SS, q="? ? ?"):
    """Standard L1 silver scratch panel with bold-navy '? ? ?'
    centred + 1-SS cream highlight stamp above."""
    _silver_panel(big, panel_rect, radius=2 * SS)
    f = _font(int(panel_rect.height * 0.78))
    text = f.render(q, True, NAVY)
    hl   = f.render(q, True, CREAM)
    tr = text.get_rect(center=panel_rect.center)
    big.blit(hl, hl.get_rect(center=(tr.centerx, tr.centery - SS)))
    big.blit(text, tr)


def _l1_sparkles(big, card, SS):
    """The 3 sparkle stars L1 uses at fixed card-corner offsets."""
    _sparkle(big, card.right - 6 * SS, card.top + 6 * SS, 3 * SS)
    _sparkle(big, card.left + 8 * SS, card.bottom - 8 * SS, 2 * SS)
    _sparkle(big, card.right - 10 * SS, card.bottom - 5 * SS, 2 * SS,
             colour=(255, 230, 120))


# ── 5 header variants ───────────────────────────────────────────────────────

def draw_d1_scratch_and_win(surf, cx, cy, pulse):
    """D1 — 'SCRATCH & WIN' header + prize tier strip footer."""

    def paint(big, SS):
        card, inner = _gold_card_base(big, SS)
        # Header plaque — thin band across the top of the inner area.
        header = pygame.Rect(inner.left + 2 * SS, inner.top + SS,
                             inner.width - 4 * SS, int(5.5 * SS))
        _header_plaque(big, header, "SCRATCH & WIN", SS)

        # Tier-pill strip along the bottom.
        tier_h = 4 * SS
        tier_y = inner.bottom - tier_h - SS
        # Foil panel between header and tier strip.
        panel = pygame.Rect(inner.left + 2 * SS,
                            header.bottom + SS,
                            inner.width - 4 * SS,
                            tier_y - (header.bottom + SS) - SS)
        _l1_panel_and_text(big, panel, SS)
        # Tiny gold fleck specks across the panel (partial-scratched).
        rng = random.Random(7)
        for _ in range(14):
            fx = rng.randint(panel.left + 2 * SS, panel.right - 2 * SS)
            fy = rng.randint(panel.top + 2 * SS, panel.bottom - 2 * SS)
            pygame.draw.circle(big, (220, 200, 130, 140),
                                (fx, fy), max(1, SS // 2))

        # 5 chip pills at the bottom — chrome rounded rects with navy
        # text.
        labels = ["$5", "$10", "$50", "$100", "★"]
        pill_w = (inner.width - 4 * SS) // 5
        for i, lab in enumerate(labels):
            px = inner.left + 2 * SS + i * pill_w
            pill = pygame.Rect(px + SS, tier_y, pill_w - 2 * SS, tier_h)
            pygame.draw.rect(big, CHROME, pill, border_radius=SS)
            pygame.draw.rect(big, STROKE, pill, max(1, SS // 2),
                             border_radius=SS)
            f = _font(int(pill.height * 0.78))
            t = f.render(lab, True, NAVY)
            big.blit(t, t.get_rect(center=pill.center))

        _l1_sparkles(big, card, SS)

    icon = _ss_paint(paint)
    tilt = math.sin(pulse * 0.7) * 5
    rotated = pygame.transform.rotate(icon, tilt)
    surf.blit(rotated, rotated.get_rect(center=(cx, cy)))


def draw_d2_lucky_arch(surf, cx, cy, pulse):
    """D2 — 'LUCKY' arched red banner + clover + coin stamps."""

    def paint(big, SS):
        card, inner = _gold_card_base(big, SS)
        # Red banner with ribbon-fold notches — sits pinned across the
        # very top, slightly overlapping the chrome perimeter.
        banner = pygame.Rect(card.left + 6 * SS, card.top + SS,
                             card.width - 12 * SS, 6 * SS)
        _v_gradient_rect(big, banner, RED_HI, RED, radius=2 * SS)
        pygame.draw.rect(big, STROKE, banner, max(1, SS // 2),
                         border_radius=2 * SS)
        notch_w = 2 * SS
        pygame.draw.polygon(big, RED, [
            (banner.left, banner.top),
            (banner.left - notch_w, banner.centery),
            (banner.left, banner.bottom),
        ])
        pygame.draw.polygon(big, RED, [
            (banner.right, banner.top),
            (banner.right + notch_w, banner.centery),
            (banner.right, banner.bottom),
        ])
        f = _font(int(banner.height * 0.88))
        bt = f.render("LUCKY", True, CREAM)
        big.blit(bt, bt.get_rect(center=banner.center))

        # Foil panel — slightly smaller than L1 to leave room for the
        # stamps below.
        panel = pygame.Rect(inner.left + 2 * SS,
                            banner.bottom + 2 * SS,
                            inner.width - 4 * SS,
                            inner.bottom - banner.bottom - 8 * SS)
        _l1_panel_and_text(big, panel, SS)

        # Clover stamp lower-left + coin lower-right.
        _clover(big, card.left + 6 * SS, card.bottom - 6 * SS,
                int(SS * 1.6), SS)
        _coin_disc(big, card.right - 7 * SS, card.bottom - 6 * SS,
                   int(SS * 2.4), SS, label="$")

        _l1_sparkles(big, card, SS)

    icon = _ss_paint(paint)
    tilt = math.sin(pulse * 0.7) * 5
    rotated = pygame.transform.rotate(icon, tilt)
    surf.blit(rotated, rotated.get_rect(center=(cx, cy)))


def draw_d3_jackpot_embossed(surf, cx, cy, pulse):
    """D3 — 'JACKPOT' embossed directly on gold + foil seal."""

    def paint(big, SS):
        card, inner = _gold_card_base(big, SS)
        # Embossed JACKPOT — painted directly on the gold body, no
        # plaque. Dark-gold fill, then a 1-SS cream highlight pass
        # offset upward for the engraved look.
        f = _font(int(6.2 * SS))
        word = "JACKPOT"
        shadow = f.render(word, True, STROKE)
        fill   = f.render(word, True, GOLD_DEEP)
        hl     = f.render(word, True, CREAM)
        # Header text positioned just below the top dashed stroke.
        wc = (inner.centerx - 4 * SS,  # nudge left so the seal fits
              inner.top + int(3.6 * SS))
        big.blit(shadow, shadow.get_rect(center=(wc[0] + SS, wc[1] + SS)))
        big.blit(fill,   fill.get_rect(center=wc))
        big.blit(hl,     hl.get_rect(center=(wc[0], wc[1] - SS)))

        # Foil panel — sized to leave room for the embossed word.
        panel = pygame.Rect(inner.left + 2 * SS,
                            inner.top + int(7.5 * SS),
                            inner.width - 4 * SS,
                            inner.bottom - (inner.top + int(7.5 * SS))
                            - 2 * SS)
        _l1_panel_and_text(big, panel, SS)

        # 8-point red foil seal at the upper-right corner, overlapping
        # the perimeter ring for a pinned-on look.
        _starburst_seal(big, card.right - 5 * SS, card.top + 5 * SS,
                        int(SS * 3.6), SS, points=8)

        _l1_sparkles(big, card, SS)

    icon = _ss_paint(paint)
    tilt = math.sin(pulse * 0.7) * 5
    rotated = pygame.transform.rotate(icon, tilt)
    surf.blit(rotated, rotated.get_rect(center=(cx, cy)))


def draw_d4_win_up_to(surf, cx, cy, pulse):
    """D4 — 'WIN UP TO $$$' two-tier header + barcode footer."""

    def paint(big, SS):
        card, inner = _gold_card_base(big, SS)
        # Two-tier header — cream "WIN UP TO" small line above bone
        # "$$$" large emblem, both directly on the gold body.
        f_small = _font(int(2.8 * SS))
        small   = f_small.render("WIN UP TO", True, STROKE)
        small_hl= f_small.render("WIN UP TO", True, CREAM)
        sc_y = inner.top + int(2.8 * SS)
        sc_x = inner.centerx
        big.blit(small_hl, small_hl.get_rect(center=(sc_x, sc_y - 1)))
        big.blit(small,    small.get_rect(center=(sc_x, sc_y)))

        f_big = _font(int(5.5 * SS))
        emblem  = f_big.render("$$$", True, STROKE)
        em_fill = f_big.render("$$$", True, CREAM)
        em_hl   = f_big.render("$$$", True, WHITE)
        ec_y = sc_y + int(4.2 * SS)
        big.blit(emblem,  emblem.get_rect(center=(sc_x + SS, ec_y + SS)))
        big.blit(em_fill, em_fill.get_rect(center=(sc_x, ec_y)))
        big.blit(em_hl,   em_hl.get_rect(center=(sc_x, ec_y - SS)))

        # Foil panel below the header.
        panel = pygame.Rect(inner.left + 2 * SS,
                            ec_y + int(3.8 * SS),
                            inner.width - 4 * SS,
                            inner.bottom - (ec_y + int(3.8 * SS))
                            - 6 * SS)
        _l1_panel_and_text(big, panel, SS)

        # Barcode strip along the bottom inner edge.
        bar_y = panel.bottom + SS
        bar_h = 4 * SS
        barcode_rect = pygame.Rect(inner.left + 4 * SS, bar_y,
                                    inner.width - 8 * SS, bar_h)
        pygame.draw.rect(big, NAVY, barcode_rect, border_radius=SS)
        # 14 random-width vertical lines.
        rng = random.Random(11)
        col_x = barcode_rect.left + SS
        while col_x < barcode_rect.right - SS:
            w_line = rng.choice((SS // 2, SS, int(SS * 1.5)))
            pygame.draw.rect(big, CHROME,
                              (col_x, barcode_rect.top + SS,
                               w_line, bar_h - 2 * SS))
            col_x += w_line + rng.choice((SS // 2, SS))
        # 4-digit cream serial number under the bar.
        f_serial = _font(int(2.6 * SS))
        sn = f_serial.render("0042", True, CREAM)
        big.blit(sn, sn.get_rect(midtop=(barcode_rect.centerx,
                                          barcode_rect.bottom + SS // 2)))

        _l1_sparkles(big, card, SS)

    icon = _ss_paint(paint)
    tilt = math.sin(pulse * 0.7) * 4
    rotated = pygame.transform.rotate(icon, tilt)
    surf.blit(rotated, rotated.get_rect(center=(cx, cy)))


def draw_d5_golden_ticket(surf, cx, cy, pulse):
    """D5 — 'GOLDEN TICKET' plaque + crown + coin chip corners."""

    def paint(big, SS):
        card, inner = _gold_card_base(big, SS)
        # Crown above plaque — sits in the top SS strip of the inner
        # area, centred over where the plaque will be.
        crown_w = int(8 * SS)
        crown_h = int(4 * SS)
        crown_cx = inner.centerx
        crown_cy_base = inner.top + crown_h + SS
        _crown(big, crown_cx, crown_cy_base, crown_w, crown_h, SS)

        # Plaque under the crown.
        plaque = pygame.Rect(inner.left + 4 * SS,
                             crown_cy_base + SS // 2,
                             inner.width - 8 * SS,
                             int(4.5 * SS))
        _header_plaque(big, plaque, "GOLDEN TICKET", SS)

        # Foil panel below — sized to leave room for coin chips.
        panel = pygame.Rect(inner.left + 2 * SS,
                            plaque.bottom + 2 * SS,
                            inner.width - 4 * SS,
                            inner.bottom - plaque.bottom - 8 * SS)
        _l1_panel_and_text(big, panel, SS)

        # Two coin chips in the lower corners.
        coin_r = int(SS * 2.4)
        _coin_disc(big, card.left + 6 * SS, card.bottom - 6 * SS,
                   coin_r, SS, label="$")
        _coin_disc(big, card.right - 6 * SS, card.bottom - 6 * SS,
                   coin_r, SS, label="$")

        _l1_sparkles(big, card, SS)

    icon = _ss_paint(paint)
    tilt = math.sin(pulse * 0.7) * 5
    rotated = pygame.transform.rotate(icon, tilt)
    surf.blit(rotated, rotated.get_rect(center=(cx, cy)))


VARIANTS = [
    ("D1_scratch_and_win",  draw_d1_scratch_and_win,
     "D1: SCRATCH & WIN header + $5/$10/$50/$100/star tier strip"),
    ("D2_lucky_arch",       draw_d2_lucky_arch,
     "D2: LUCKY red arch banner + clover + $ coin stamps"),
    ("D3_jackpot_embossed", draw_d3_jackpot_embossed,
     "D3: JACKPOT embossed on gold + 8-point foil seal"),
    ("D4_win_up_to",        draw_d4_win_up_to,
     "D4: WIN UP TO $$$ tiered header + barcode footer"),
    ("D5_golden_ticket",    draw_d5_golden_ticket,
     "D5: GOLDEN TICKET plaque + crown + corner coin chips"),
]


# ── output ──────────────────────────────────────────────────────────────────

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
        ingame    = _ingame_png(fn, label)
        zoom_path   = os.path.join(_OUT, f"{label}.png")
        ingame_path = os.path.join(_OUT, f"{label}_ingame.png")
        pygame.image.save(icon_zoom, zoom_path)
        pygame.image.save(ingame, ingame_path)
        saved.append((label, caption, icon_zoom))
        print(f"saved {zoom_path}")
        print(f"saved {ingame_path}")

    cell_w = saved[0][2].get_width()
    cell_h = saved[0][2].get_height()
    band_h = 56
    gap    = 12
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
            "v5_powerups/docs/screenshots/lottery_header_variants")
    print()
    print(f"{base}/00_contact_sheet.png")
    for label, caption, _ in saved:
        print(f"{base}/{label}.png  -- {caption}")
        print(f"{base}/{label}_ingame.png")


if __name__ == "__main__":
    main()
