"""Elegant background-ornament /design run — 5 concepts × 2 colourways.

Replaces the enlarged quatrefoil with five engraved-luxury ornaments, each
drawn as a deep indigo channel plus a colourway glint so it reads as
engraving, injected behind everything via the _bg_hook base patch and clipped
to the upper card (x within the body, y<337 — never near BUY/CANCEL).

Usage: python _confirm_v8_premv1_hybrid2_scribbles.py <round>
round 1 → colorways/scribbles_r1.png ; round 2 → scribbles_showcase.png
"""
import os
import sys
import math

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _confirm_v8_premv1_hybrid2 as h2
import _confirm_v8_premv1_hybrid2_colorway as cw
import _confirm_v8_premv1_hybrid2_colorway_matched as matched
import _confirm_v8_premv1_hybrid2_bg_scribble as bgmod
import game.store as store_mod
import game.store_data as store_data
import game.store_catalog as store_catalog
from game.store_cards import m
from PIL import Image, ImageDraw

POP_W, POP_H = 260, 442
CHIP_CY = 300
Q_DEEP = (22, 24, 56)
CLIP_Y = 337

DESIGNS = [
    ("#2 two-metals · silver", matched.variant(
        "two-metals", cw.PALETTES_R2["two-metals"], True)),
    ("#4 ivory-manuscript · ivory", matched.variant(
        "ivory-manuscript", cw.PALETTES_R2["ivory-manuscript"], True)),
]


def _clipped_layer(big):
    return pygame.Surface(big.get_size(), pygame.SRCALPHA)


def _apply(big, layer):
    mask = pygame.Surface(layer.get_size(), pygame.SRCALPHA)
    mask.fill((0, 0, 0, 0))
    pygame.draw.rect(mask, (255, 255, 255, 255),
                     pygame.Rect(m(14), m(131), m(232), m(CLIP_Y - 131)),
                     border_radius=m(18))
    layer.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(layer, (0, 0))


def hook_guilloche(glint, deep_a, glint_a):
    def hook(big):
        layer = _clipped_layer(big)
        cx, cy = m(130), m(237)
        for r in (34, 46, 58, 70, 82, 94):
            pygame.draw.circle(layer, (*Q_DEEP, deep_a), (cx, cy), m(r),
                               max(2, m(2)))
            pygame.draw.circle(layer, (*glint, glint_a), (cx, cy),
                               m(r) - m(1.5), max(1, m(1)))
        _apply(big, layer)
    return hook


def hook_laurel(glint, deep_a, glint_a):
    def hook(big):
        layer = _clipped_layer(big)
        cx, cy = m(130), m(238)
        R = m(96)
        for side in (-1, 1):
            a0, a1 = (100, 250) if side < 0 else (-70, 80)
            pts = []
            for adeg in range(a0, a1 + 1, 3):
                a = math.radians(adeg)
                pts.append((cx + R * math.cos(a) * (1 if side < 0 else 1),
                            cy - R * math.sin(a)))
            pygame.draw.lines(layer, (*Q_DEEP, deep_a), False, pts, max(2, m(2.5)))
            pygame.draw.lines(layer, (*glint, glint_a), False,
                              [(x + side * m(1.5), y) for x, y in pts],
                              max(1, m(1)))
            # leaf ticks along the branch, alternating inward
            for k, adeg in enumerate(range(a0 + 8, a1 - 6, 14)):
                a = math.radians(adeg)
                bx = cx + R * math.cos(a)
                by = cy - R * math.sin(a)
                la = a + math.radians(38 if k % 2 == 0 else -38)
                tip = (bx - m(11) * math.cos(la) * side,
                       by + m(11) * math.sin(la))
                pygame.draw.line(layer, (*Q_DEEP, deep_a), (bx, by), tip,
                                 max(2, m(2)))
                pygame.draw.line(layer, (*glint, glint_a),
                                 (bx + side * m(1), by), tip, max(1, m(1)))
        _apply(big, layer)
    return hook


def hook_filigree(glint, deep_a, glint_a):
    def hook(big):
        layer = _clipped_layer(big)
        corners = [(m(30), m(152), 1, 1), (m(230), m(152), -1, 1),
                   (m(30), m(318), 1, -1), (m(230), m(318), -1, -1)]
        for bx, by, sx, sy in corners:
            for r in (12, 19, 26):
                rect = pygame.Rect(0, 0, m(r) * 2, m(r) * 2)
                rect.center = (bx, by)
                start = {(1, 1): 270, (-1, 1): 180, (1, -1): 0, (-1, -1): 90}[(sx, sy)]
                pygame.draw.arc(layer, (*Q_DEEP, deep_a), rect,
                                math.radians(start), math.radians(start + 90),
                                max(2, m(2)))
                rect2 = rect.inflate(-m(3), -m(3))
                pygame.draw.arc(layer, (*glint, glint_a), rect2,
                                math.radians(start), math.radians(start + 90),
                                max(1, m(1)))
            pygame.draw.circle(layer, (*glint, min(255, glint_a + 40)),
                               (bx + sx * m(4), by + sy * m(4)), m(2))
        _apply(big, layer)
    return hook


def hook_fan(glint, deep_a, glint_a):
    def hook(big):
        layer = _clipped_layer(big)
        cx, cy = m(130), m(135)
        for k in range(26):
            a = math.radians(360 * k / 26)
            x0 = cx + m(72) * math.cos(a)
            y0 = cy + m(72) * math.sin(a)
            x1 = cx + m(200) * math.cos(a)
            y1 = cy + m(200) * math.sin(a)
            pygame.draw.line(layer, (*Q_DEEP, deep_a), (x0, y0), (x1, y1),
                             max(2, m(2)))
            pygame.draw.line(layer, (*glint, glint_a),
                             (x0 + m(1), y0 + m(1)), (x1 + m(1), y1 + m(1)),
                             max(1, m(1)))
        _apply(big, layer)
    return hook


def hook_lattice(glint, deep_a, glint_a):
    def hook(big):
        layer = _clipped_layer(big)
        w, h = layer.get_size()
        pitch = m(26)
        for off in range(-h, w + h, pitch):
            pygame.draw.line(layer, (*Q_DEEP, deep_a), (off, 0), (off + h, h),
                             max(2, m(1.6)))
            pygame.draw.line(layer, (*Q_DEEP, deep_a), (off + h, 0), (off, h),
                             max(2, m(1.6)))
        # glint studs at lattice crossings on the vertical card axis grid
        for gy in range(m(150), m(330), pitch):
            for gx in range(m(26), m(240), pitch):
                pygame.draw.circle(layer, (*glint, glint_a), (gx, gy), m(1.4))
        _apply(big, layer)
    return hook


SCRIBBLES_R1 = [
    ("#1 guilloche-rosette", hook_guilloche, 95, 70),
    ("#2 laurel-arcs", hook_laurel, 110, 80),
    ("#3 filigree-corners", hook_filigree, 120, 95),
    ("#4 radiant-fan", hook_fan, 80, 55),
    ("#5 damask-lattice", hook_lattice, 60, 75),
]
# round 2 = round 1 with the critique's visibility lifts: fan rays and
# lattice glint studs sat under the 1x readability threshold; the other three
# passed unchanged.
SCRIBBLES_R2 = [
    ("#1 guilloche-rosette", hook_guilloche, 95, 70),
    ("#2 laurel-arcs", hook_laurel, 110, 80),
    ("#3 filigree-corners", hook_filigree, 120, 95),
    ("#4 radiant-fan", hook_fan, 95, 70),
    ("#5 damask-lattice", hook_lattice, 60, 95),
]


def main():
    round_no = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    scribbles = SCRIBBLES_R1 if round_no == 1 else SCRIBBLES_R2
    out_name = "scribbles_r1.png" if round_no == 1 else "scribbles_showcase.png"

    _orig_bal = store_data.balance
    _orig_cost = store_catalog.cost
    _orig_chip_cy = h2.CHIP_CY
    store_data.balance = lambda: 99999
    store_catalog.cost = lambda sid: {v: h2.PRICES[k] for k, v in h2.SIDS.items()}.get(sid, 0)
    h2._DRAW_FN[0] = bgmod._patched_draw_with_hook()
    h2.overlay_quatrefoil = lambda ov: None
    h2.CHIP_CY = CHIP_CY
    try:
        MARGIN, HEAD, GAP, ROW_FOOT = 20, 46, 12, 26
        strip_w = MARGIN * 2 + len(scribbles) * (POP_W + GAP) - GAP
        strip_h = HEAD + len(DESIGNS) * (POP_H + ROW_FOOT + 24) + MARGIN
        grid = Image.new("RGB", (strip_w, strip_h), (10, 9, 20))
        idr = ImageDraw.Draw(grid)
        idr.text((MARGIN, 14),
                 f"elegant background ornaments · round_{round_no} · bar cy=300 · EPIC",
                 fill=(236, 214, 160))

        y = HEAD
        for row_label, pal in DESIGNS:
            h2.overlay_bullion_chip = cw.make_chip_fn(pal["bar"])
            h2.overlay_buttons = cw.make_buttons_fn(pal["buy"], pal["can"])
            idr.text((MARGIN, y + 2), row_label, fill=(206, 190, 150))
            y += 20
            for i, (tag, factory, deep_a, glint_a) in enumerate(scribbles):
                store_mod._bg_hook = factory(pal["glint"], deep_a, glint_a)
                pop = h2.render_popup("EPIC")
                pil = Image.frombytes("RGB", (POP_W, POP_H),
                                      pygame.image.tostring(pop, "RGB"))
                x = MARGIN + i * (POP_W + GAP)
                grid.paste(pil, (x, y))
                idr.text((x + POP_W // 2, y + POP_H + 5), tag,
                         fill=(170, 170, 195), anchor="mt")
            y += POP_H + ROW_FOOT + 4

        out_img = grid.resize((strip_w * 2, strip_h * 2), Image.LANCZOS)
        out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "confirm_purchase_v8", "premium-v1", "colorways",
                           out_name)
        out_img.save(out)
        print("saved", out, out_img.size)
    finally:
        store_data.balance = _orig_bal
        store_catalog.cost = _orig_cost
        h2.CHIP_CY = _orig_chip_cy
        if hasattr(store_mod, "_bg_hook"):
            del store_mod._bg_hook


if __name__ == "__main__":
    main()
