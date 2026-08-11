"""Game-card background ornaments — /design run 2, 5 concepts × 2 colourways.

The quatrefoil's game-card feel came from being a constructed emblem; at 4×
scale one construction layer reads sparse. Every concept here stacks ≥3
structural layers so TCG-card density survives the enlargement. Deep indigo
channel + colourway glint, injected behind the upper card, clipped y<337.

Usage: python _confirm_v8_premv1_hybrid2_scribbles2.py <round>
round 1 → colorways/scribbles2_r1.png ; round 2 → scribbles2_showcase.png
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
from _confirm_v8_premv1_hybrid2_scribbles import _clipped_layer, _apply, DESIGNS
import game.store as store_mod
import game.store_data as store_data
import game.store_catalog as store_catalog
from game.store_cards import m
from PIL import Image, ImageDraw

POP_W, POP_H = 260, 442
CHIP_CY = 300
Q_DEEP = (22, 24, 56)
CX_L, CY_L = 130, 235          # ornament centre (logical px)


def _ring(layer, col, c, r, w):
    pygame.draw.circle(layer, col, c, r, w)


def hook_arcane_sigil(glint, deep_a, glint_a):
    """Spell-circle: double ring + rune ticks + inscribed hexagram + orbit dots."""
    def hook(big):
        layer = _clipped_layer(big)
        c = (m(CX_L), m(CY_L))
        r_out, r_in = m(92), m(76)
        for r, w in ((r_out, m(2.5)), (r_in, m(2))):
            _ring(layer, (*Q_DEEP, deep_a), c, r, max(2, w))
            _ring(layer, (*glint, glint_a), c, r - m(1.5), max(1, m(1)))
        # rune ticks between the rings
        for k in range(24):
            a = math.pi * 2 * k / 24
            x0 = c[0] + (r_in + m(3)) * math.cos(a)
            y0 = c[1] + (r_in + m(3)) * math.sin(a)
            x1 = c[0] + (r_out - m(3)) * math.cos(a)
            y1 = c[1] + (r_out - m(3)) * math.sin(a)
            col = (*glint, glint_a) if k % 3 == 0 else (*Q_DEEP, deep_a)
            pygame.draw.line(layer, col, (x0, y0), (x1, y1), max(2, m(2)))
        # inscribed hexagram (two overlapping triangles)
        for phase in (0, math.pi):
            pts = []
            for k in range(3):
                a = -math.pi / 2 + phase + math.pi * 2 * k / 3
                pts.append((c[0] + r_in * math.cos(a), c[1] + r_in * math.sin(a)))
            pygame.draw.polygon(layer, (*Q_DEEP, deep_a), pts, max(2, m(2)))
            pygame.draw.polygon(layer, (*glint, glint_a - 20),
                                [(x + m(1), y + m(1)) for x, y in pts],
                                max(1, m(1)))
        # orbit dots at hexagram vertices
        for k in range(6):
            a = -math.pi / 2 + math.pi * k / 3
            pygame.draw.circle(layer, (*glint, min(255, glint_a + 50)),
                               (int(c[0] + r_in * math.cos(a)),
                                int(c[1] + r_in * math.sin(a))), m(2.5))
        _apply(big, layer)
    return hook


def hook_mandala(glint, deep_a, glint_a):
    """Rosette: outer scallop petals + counter-phase inner petals + spokes + core."""
    def hook(big):
        layer = _clipped_layer(big)
        c = (m(CX_L), m(CY_L))
        # outer petal ring: overlapping arcs whose centres orbit the core
        for n, orbit_r, pet_r, phase in ((12, m(74), m(24), 0.0),
                                         (12, m(52), m(17), math.pi / 12)):
            for k in range(n):
                a = phase + math.pi * 2 * k / n
                pc = (c[0] + orbit_r * math.cos(a), c[1] + orbit_r * math.sin(a))
                _ring(layer, (*Q_DEEP, deep_a),
                      (int(pc[0]), int(pc[1])), pet_r, max(2, m(2)))
                _ring(layer, (*glint, glint_a - 15),
                      (int(pc[0]), int(pc[1])), pet_r - m(1.5), max(1, m(1)))
        # radial spokes
        for k in range(24):
            a = math.pi * 2 * k / 24 + math.pi / 24
            x0 = c[0] + m(30) * math.cos(a)
            y0 = c[1] + m(30) * math.sin(a)
            x1 = c[0] + m(46) * math.cos(a)
            y1 = c[1] + m(46) * math.sin(a)
            pygame.draw.line(layer, (*Q_DEEP, deep_a), (x0, y0), (x1, y1),
                             max(2, m(1.8)))
        # core rings
        _ring(layer, (*glint, glint_a), c, m(28), max(2, m(2)))
        _ring(layer, (*Q_DEEP, deep_a), c, m(24), max(2, m(2)))
        _apply(big, layer)
    return hook


def hook_heraldic(glint, deep_a, glint_a):
    """Crest: nested lozenge frames + scroll arcs above/below + side wing lines."""
    def hook(big):
        layer = _clipped_layer(big)
        cx, cy = m(CX_L), m(CY_L)
        for hw, hh in ((m(92), m(96)), (m(76), m(80)), (m(60), m(64))):
            pts = [(cx, cy - hh), (cx + hw, cy), (cx, cy + hh), (cx - hw, cy)]
            pygame.draw.polygon(layer, (*Q_DEEP, deep_a), pts, max(2, m(2.2)))
            pygame.draw.polygon(layer, (*glint, glint_a - 10),
                                [(x + m(1), y + m(1)) for x, y in pts],
                                max(1, m(1)))
        # scroll flourish arcs above and below the lozenge stack
        for sy, flip in ((cy - m(96), 1), (cy + m(96), -1)):
            for dx in (-1, 1):
                rect = pygame.Rect(0, 0, m(44), m(26))
                rect.center = (cx + dx * m(26), sy)
                a0, a1 = (math.pi, math.pi * 2) if flip > 0 else (0, math.pi)
                pygame.draw.arc(layer, (*Q_DEEP, deep_a), rect, a0, a1, max(2, m(2)))
                pygame.draw.arc(layer, (*glint, glint_a - 10),
                                rect.inflate(-m(2), -m(2)), a0, a1, max(1, m(1)))
        # side wing lines
        for dx in (-1, 1):
            for k in range(3):
                x0 = cx + dx * (m(96) + m(6) * k)
                pygame.draw.line(layer, (*Q_DEEP, deep_a),
                                 (x0, cy - m(34) + m(10) * k),
                                 (x0, cy + m(34) - m(10) * k), max(2, m(2)))
        pygame.draw.circle(layer, (*glint, min(255, glint_a + 40)), (cx, cy - m(96)), m(2.5))
        pygame.draw.circle(layer, (*glint, min(255, glint_a + 40)), (cx, cy + m(96)), m(2.5))
        _apply(big, layer)
    return hook


def hook_celtic(glint, deep_a, glint_a):
    """Interlace: quatrefoil circles + centre ring woven through, corner studs."""
    def hook(big):
        layer = _clipped_layer(big)
        cx, cy = m(CX_L), m(CY_L)
        d, rl = m(46), m(52)
        lobes = [(cx, cy - d), (cx, cy + d), (cx - d, cy), (cx + d, cy)]
        ring_r = m(64)
        # weave: lobes first, centre ring on top, then re-draw lobe arc windows
        # over the ring at alternating crossings for an over/under strapwork read
        for lx, ly in lobes:
            _ring(layer, (*Q_DEEP, deep_a), (lx, ly), rl, max(2, m(4)))
            _ring(layer, (*glint, glint_a), (lx, ly), rl - m(2), max(1, m(1.2)))
        _ring(layer, (*Q_DEEP, deep_a), (cx, cy), ring_r, max(2, m(4)))
        _ring(layer, (*glint, glint_a), (cx, cy), ring_r - m(2), max(1, m(1.2)))
        # re-draw top/bottom lobe segments over the ring (over-pass)
        for lx, ly in (lobes[0], lobes[1]):
            for adeg in range(0, 360, 4):
                a = math.radians(adeg)
                px = lx + rl * math.cos(a)
                py = ly + rl * math.sin(a)
                if abs(math.hypot(px - cx, py - cy) - ring_r) < m(7):
                    pygame.draw.circle(layer, (*Q_DEEP, deep_a), (int(px), int(py)),
                                       m(2.4))
        # inner quatrefoil echo + corner studs
        for lx, ly in lobes:
            _ring(layer, (*Q_DEEP, deep_a - 20), (lx, ly), rl - m(10), max(2, m(2)))
        for sx in (-1, 1):
            for sy in (-1, 1):
                pygame.draw.circle(layer, (*glint, min(255, glint_a + 40)),
                                   (cx + sx * m(88), cy + sy * m(88)), m(2.5))
        _apply(big, layer)
    return hook


def hook_constellation(glint, deep_a, glint_a):
    """Star sigil: 4-point star nodes + connecting web + sparkles + outer ring."""
    def _star(layer, x, y, r, col):
        pts = [(x, y - r), (x + r * 0.3, y - r * 0.3), (x + r, y),
               (x + r * 0.3, y + r * 0.3), (x, y + r), (x - r * 0.3, y + r * 0.3),
               (x - r, y), (x - r * 0.3, y - r * 0.3)]
        pygame.draw.polygon(layer, col, pts)

    def hook(big):
        layer = _clipped_layer(big)
        cx, cy = m(CX_L), m(CY_L)
        nodes = [(cx, cy - m(84)), (cx + m(74), cy - m(34)), (cx + m(52), cy + m(58)),
                 (cx - m(52), cy + m(58)), (cx - m(74), cy - m(34)),
                 (cx + m(30), cy - m(6)), (cx - m(30), cy - m(6)), (cx, cy + m(30)),
                 (cx + m(88), cy + m(26)), (cx - m(88), cy + m(26))]
        web = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0),
               (0, 5), (0, 6), (1, 5), (4, 6), (5, 7), (6, 7), (2, 7), (3, 7),
               (5, 6), (1, 8), (2, 8), (4, 9), (3, 9)]
        _ring(layer, (*Q_DEEP, deep_a - 10), (cx, cy - m(6)), m(92), max(2, m(2)))
        for i, j in web:
            pygame.draw.line(layer, (*Q_DEEP, deep_a), nodes[i], nodes[j],
                             max(2, m(1.8)))
            pygame.draw.line(layer, (*glint, glint_a - 30),
                             (nodes[i][0] + m(1), nodes[i][1] + m(1)),
                             (nodes[j][0] + m(1), nodes[j][1] + m(1)),
                             max(1, m(0.8)))
        for x, y in nodes:
            _star(layer, x, y, m(5), (*glint, glint_a))
            pygame.draw.circle(layer, (*Q_DEEP, min(255, deep_a + 40)), (x, y), m(1.4))
        # sparkle crosses between nodes
        for sx, sy in [(cx + m(48), cy - m(64)), (cx - m(48), cy - m(64)),
                       (cx + m(70), cy + m(16)), (cx - m(70), cy + m(16)),
                       (cx, cy + m(74))]:
            pygame.draw.line(layer, (*glint, glint_a - 20),
                             (sx - m(3), sy), (sx + m(3), sy), max(1, m(1)))
            pygame.draw.line(layer, (*glint, glint_a - 20),
                             (sx, sy - m(3)), (sx, sy + m(3)), max(1, m(1)))
        _apply(big, layer)
    return hook


SCRIBBLES2_R1 = [
    ("#1 arcane-sigil", hook_arcane_sigil, 100, 85),
    ("#2 mandala-medallion", hook_mandala, 95, 80),
    ("#3 heraldic-crest", hook_heraldic, 100, 85),
    ("#4 celtic-knot", hook_celtic, 105, 90),
    ("#5 constellation-web", hook_constellation, 100, 95),
]
# round 2 = round 1 with the critique fixes: heraldic lifted off the density
# floor; constellation's web extended with side nodes (nodes 8/9 above) so it
# reaches the card flanks — the extension is shared code, alphas bumped here.
SCRIBBLES2_R2 = [
    ("#1 arcane-sigil", hook_arcane_sigil, 100, 85),
    ("#2 mandala-medallion", hook_mandala, 95, 80),
    ("#3 heraldic-crest", hook_heraldic, 115, 95),
    ("#4 celtic-knot", hook_celtic, 105, 90),
    ("#5 constellation-web", hook_constellation, 110, 100),
]


def main():
    round_no = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    scribbles = SCRIBBLES2_R1 if round_no == 1 else SCRIBBLES2_R2
    out_name = "scribbles2_r1.png" if round_no == 1 else "scribbles2_showcase.png"

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
                 f"game-card ornaments · round_{round_no} · bar cy=300 · EPIC",
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
