"""Game-card background ornaments — /design run 3, 5 all-new construction kinds.

Run 2's layered-emblem direction approved; these five explore constructions
none of the prior ten used: tiled armour scales, meshing gears, figurative
wings, a runic border frame, and a pedestal composition that seats the hero.
Deep indigo channel + colourway glint, behind everything, clipped y<337.

Usage: python _confirm_v8_premv1_hybrid2_scribbles3.py <round>
round 1 → colorways/scribbles3_r1.png ; round 2 → scribbles3_showcase.png
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


def hook_dragon_scales(glint, deep_a, glint_a):
    """Offset scallop rows fading upward + centre keel studs."""
    def hook(big):
        layer = _clipped_layer(big)
        scale_w, row_h = m(34), m(15)
        y0, y1 = 150, 330
        n_rows = int((y1 - y0) / (row_h / 2)) if row_h else 0
        for row in range(14):
            ry = m(y1) - row * row_h
            if ry < m(y0):
                break
            fade = 1.0 - row * 0.055
            da = int(deep_a * fade)
            ga = int(glint_a * fade)
            off = (scale_w // 2) if row % 2 else 0
            for k in range(-1, 9):
                sx = m(14) + off + k * scale_w
                rect = pygame.Rect(sx, ry - m(11), scale_w, m(22))
                pygame.draw.arc(layer, (*Q_DEEP, max(0, da)), rect,
                                0, math.pi, max(2, m(2.4)))
                pygame.draw.arc(layer, (*glint, max(0, ga)),
                                rect.inflate(-m(2), -m(2)), 0, math.pi,
                                max(1, m(1)))
        for ky in range(160, 331, 24):
            pygame.draw.circle(layer, (*glint, min(255, glint_a + 40)),
                               (m(130), m(ky)), m(1.8))
        _apply(big, layer)
    return hook


def hook_clockwork(glint, deep_a, glint_a):
    """Meshing gears: toothed rings + spoke wheels + hubs + rivets."""
    def _gear(layer, c, r, teeth, deep_a, glint_a, spokes=6):
        # toothed rim: alternating radial stubs around the ring
        pygame.draw.circle(layer, (*Q_DEEP, deep_a), c, r, max(2, m(2.4)))
        pygame.draw.circle(layer, (*glint, glint_a), c, r - m(2), max(1, m(1)))
        for k in range(teeth):
            a = math.pi * 2 * k / teeth
            x0 = c[0] + r * math.cos(a)
            y0 = c[1] + r * math.sin(a)
            x1 = c[0] + (r + m(5)) * math.cos(a)
            y1 = c[1] + (r + m(5)) * math.sin(a)
            pygame.draw.line(layer, (*Q_DEEP, deep_a), (x0, y0), (x1, y1),
                             max(2, m(2.4)))
        for k in range(spokes):
            a = math.pi * 2 * k / spokes + math.pi / spokes
            pygame.draw.line(layer, (*Q_DEEP, deep_a),
                             (c[0] + m(8) * math.cos(a), c[1] + m(8) * math.sin(a)),
                             (c[0] + (r - m(6)) * math.cos(a),
                              c[1] + (r - m(6)) * math.sin(a)), max(2, m(2)))
        pygame.draw.circle(layer, (*Q_DEEP, deep_a), c, m(7), max(2, m(2)))
        pygame.draw.circle(layer, (*glint, min(255, glint_a + 40)), c, m(2.2))

    def hook(big):
        layer = _clipped_layer(big)
        _gear(layer, (m(130), m(215)), m(62), 20, deep_a, glint_a, spokes=8)
        _gear(layer, (m(48), m(285)), m(34), 12, deep_a, glint_a, spokes=5)
        _gear(layer, (m(212), m(285)), m(34), 12, deep_a, glint_a, spokes=5)
        _gear(layer, (m(52), m(158)), m(24), 10, deep_a - 20, glint_a - 20, spokes=4)
        _gear(layer, (m(208), m(158)), m(24), 10, deep_a - 20, glint_a - 20, spokes=4)
        _apply(big, layer)
    return hook


def hook_wing_emblem(glint, deep_a, glint_a):
    """Symmetric layered feather arcs from behind the hero + keystone diamond."""
    def hook(big):
        layer = _clipped_layer(big)
        cx, cy = m(130), m(196)
        # three feather rows per wing, each row a fan of arcs
        for row, (r0, n_f, alen) in enumerate(((m(66), 5, 26),
                                               (m(88), 6, 24),
                                               (m(110), 7, 22))):
            da = deep_a - row * 8
            ga = glint_a - row * 8
            for side in (-1, 1):
                for k in range(n_f):
                    base_deg = 195 + k * alen * 0.62 if side < 0 else -15 - k * alen * 0.62
                    a_mid = math.radians(base_deg if side < 0 else base_deg + 360)
                    fx = cx + r0 * math.cos(a_mid) * side * (-1 if side < 0 else 1)
                    # feather = short arc segment bulging outward
                    rect = pygame.Rect(0, 0, m(30), m(46))
                    ang = math.radians(180 + base_deg * 0.15) if side < 0 else 0
                    px = cx + side * (m(28) + row * m(22) + k * m(9))
                    py = cy - m(6) + k * m(9) - row * m(4)
                    rect.center = (px, py)
                    a0 = math.pi * 0.9 if side < 0 else math.pi * 1.6
                    a1 = a0 + math.pi * 0.5
                    pygame.draw.arc(layer, (*Q_DEEP, max(0, da)), rect, a0, a1,
                                    max(2, m(2.4)))
                    pygame.draw.arc(layer, (*glint, max(0, ga)),
                                    rect.inflate(-m(3), -m(3)), a0, a1,
                                    max(1, m(1)))
        # trailing edge feathers sweeping down the flanks (fills the lower
        # wing silhouette so the emblem reads full-span, not tips-only)
        for side in (-1, 1):
            for k in range(3):
                rect = pygame.Rect(0, 0, m(26), m(84) - k * m(14))
                rect.center = (cx + side * (m(96) + k * m(11)),
                               m(252) + k * m(6))
                a0 = math.pi * 0.55 if side < 0 else math.pi * 1.45
                a1 = a0 + math.pi * 0.55
                pygame.draw.arc(layer, (*Q_DEEP, deep_a - 12), rect, a0, a1,
                                max(2, m(2.2)))
                pygame.draw.arc(layer, (*glint, glint_a - 15),
                                rect.inflate(-m(3), -m(3)), a0, a1,
                                max(1, m(1)))
        # keystone diamond under the hero
        pts = [(cx, cy - m(14)), (cx + m(10), cy), (cx, cy + m(14)), (cx - m(10), cy)]
        pygame.draw.polygon(layer, (*Q_DEEP, deep_a), pts, max(2, m(2)))
        pygame.draw.polygon(layer, (*glint, glint_a),
                            [(x + m(1), y + m(1)) for x, y in pts], max(1, m(1)))
        for side in (-1, 1):
            pygame.draw.circle(layer, (*glint, min(255, glint_a + 40)),
                               (cx + side * m(104), cy + m(48)), m(2.2))
        _apply(big, layer)
    return hook


def hook_runic_frame(glint, deep_a, glint_a):
    """Border construction: double keyline frame + rune dashes + corner keys."""
    def hook(big):
        layer = _clipped_layer(big)
        outer = pygame.Rect(m(22), m(140), m(216), m(188))
        inner = outer.inflate(-m(14), -m(14))
        for r, w in ((outer, m(2.2)), (inner, m(2))):
            pygame.draw.rect(layer, (*Q_DEEP, deep_a), r, max(2, w),
                             border_radius=m(10))
        pygame.draw.rect(layer, (*glint, glint_a), outer.inflate(-m(3), -m(3)),
                         max(1, m(1)), border_radius=m(9))
        # rune dashes in the channel between the two keylines
        chan_y_top = outer.top + m(7)
        chan_y_bot = outer.bottom - m(7)
        for k in range(12):
            x = outer.left + m(16) + k * m(16)
            if x > outer.right - m(16):
                break
            for yy in (chan_y_top, chan_y_bot):
                pygame.draw.line(layer, (*glint, glint_a - 15),
                                 (x, yy - m(3)), (x, yy + m(3)), max(2, m(2)))
        chan_x_l = outer.left + m(7)
        chan_x_r = outer.right - m(7)
        for k in range(9):
            yv = outer.top + m(16) + k * m(20)
            if yv > outer.bottom - m(16):
                break
            for xx in (chan_x_l, chan_x_r):
                pygame.draw.line(layer, (*glint, glint_a - 15),
                                 (xx - m(3), yv), (xx + m(3), yv), max(2, m(2)))
        # corner diamond keys + midpoint studs
        for cxk, cyk in [(outer.left, outer.top), (outer.right, outer.top),
                         (outer.left, outer.bottom), (outer.right, outer.bottom)]:
            pts = [(cxk, cyk - m(8)), (cxk + m(8), cyk), (cxk, cyk + m(8)),
                   (cxk - m(8), cyk)]
            pygame.draw.polygon(layer, (*Q_DEEP, min(255, deep_a + 30)), pts)
            pygame.draw.polygon(layer, (*glint, glint_a), pts, max(2, m(1.6)))
        for mx, my in [(outer.centerx, outer.top), (outer.centerx, outer.bottom),
                       (outer.left, outer.centery), (outer.right, outer.centery)]:
            pygame.draw.circle(layer, (*glint, min(255, glint_a + 40)),
                               (mx, my), m(2.4))
        _apply(big, layer)
    return hook


def hook_lotus_throne(glint, deep_a, glint_a):
    """Pedestal: stacked crescent tiers seating the hero + rising petal arcs."""
    def hook(big):
        layer = _clipped_layer(big)
        cx = m(130)
        # rising petal arcs behind the hero (upper halo fan)
        for k in range(9):
            spread = (k - 4) / 4.0
            px = cx + int(m(78) * spread)
            ph = m(60) - abs(int(m(22) * spread))
            rect = pygame.Rect(0, 0, m(34), ph * 2)
            rect.center = (px, m(206))
            pygame.draw.arc(layer, (*Q_DEEP, deep_a - 10), rect,
                            math.pi * 0.15, math.pi * 0.85, max(2, m(2.2)))
            pygame.draw.arc(layer, (*glint, glint_a - 15),
                            rect.inflate(-m(3), -m(3)),
                            math.pi * 0.15, math.pi * 0.85, max(1, m(1)))
        # stacked crescent tiers (the throne) under the hero, above the bar
        for t, (hw, ty) in enumerate(((m(96), 252), (m(76), 240), (m(56), 229))):
            rect = pygame.Rect(0, 0, hw * 2, m(34))
            rect.center = (cx, m(ty))
            pygame.draw.arc(layer, (*Q_DEEP, deep_a), rect,
                            math.pi * 1.08, math.pi * 1.92, max(2, m(3)))
            pygame.draw.arc(layer, (*glint, glint_a),
                            rect.inflate(-m(3), -m(3)),
                            math.pi * 1.08, math.pi * 1.92, max(1, m(1.2)))
            # tier bead studs
            for s in (-1, 1):
                pygame.draw.circle(layer, (*glint, min(255, glint_a + 30)),
                                   (cx + s * hw, m(ty) + m(2)), m(2))
        # base studs flanking the price bar seat
        for s in (-1, 1):
            pygame.draw.circle(layer, (*glint, min(255, glint_a + 40)),
                               (cx + s * m(104), m(262)), m(2.4))
        _apply(big, layer)
    return hook


SCRIBBLES3_R1 = [
    ("#1 dragon-scales", hook_dragon_scales, 85, 70),
    ("#2 clockwork-gears", hook_clockwork, 100, 85),
    ("#3 wing-emblem", hook_wing_emblem, 100, 85),
    ("#4 runic-frame", hook_runic_frame, 110, 95),
    ("#5 lotus-throne", hook_lotus_throne, 105, 90),
]
# round 2 = round 1 + critique fixes: gears lifted off the density floor;
# wings gained trailing edge feathers (shared hook code above) so the emblem
# spans the flanks — its alphas hold.
SCRIBBLES3_R2 = [
    ("#1 dragon-scales", hook_dragon_scales, 85, 70),
    ("#2 clockwork-gears", hook_clockwork, 110, 95),
    ("#3 wing-emblem", hook_wing_emblem, 100, 85),
    ("#4 runic-frame", hook_runic_frame, 110, 95),
    ("#5 lotus-throne", hook_lotus_throne, 105, 90),
]


def main():
    round_no = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    scribbles = SCRIBBLES3_R1 if round_no == 1 else SCRIBBLES3_R2
    out_name = "scribbles3_r1.png" if round_no == 1 else "scribbles3_showcase.png"

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
                 f"game-card ornaments run 3 · round_{round_no} · bar cy=300 · EPIC",
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
