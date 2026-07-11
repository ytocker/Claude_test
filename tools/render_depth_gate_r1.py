#!/usr/bin/env python3
"""
item_card_redesign · depth-gate · round 1 render.

Concept: a receding ceremonial corridor. The KITSUNE stands within a wide
foreground torii-style gate; three narrower gate frames nest behind it into a
vanishing-point corridor, so rarity is legible as a countable z-stack of gates
in the side margins. Lantern-warm floor glow pools at the fox's feet; gold
motes drift up the margins; a small hanging plaque carries the price.

Authored at SS=2 (store_cards convention): every gate, gradient and glyph is
drawn oversized then ONE smoothscale turns the geometry crisp anti-aliased.
Both build targets safe: pure pygame, no numpy, no mixer, no platform branches.
"""
import os
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from game.store_cards import m, SS, vgrad, plain_text, font
from game.draw import lerp_color
from game.hud import _font
from game.animal_kitsune import build_kitsune, build_kitsune_aura
from game.parrot import _add_outline

ADD = pygame.BLEND_ADD

# ── logical card metrics (320×200) — the brief's coordinate space ────────────
CW, CH = 320, 200
CXG = CW // 2                    # horizontal centre → vanishing-point x
VP_Y = 85                        # vanishing point slightly above midheight

# Legendary gold ramp (brief) + the cool tint each receding gate lerps toward.
GOLD_TOP = (255, 202, 104)
GOLD_BOT = (150, 92, 22)
GOLD_GLOW = (255, 168, 58)
COOL_TOP = (118, 148, 208)       # gates cool + recede into corridor depth
COOL_BOT = (40, 58, 104)

# (left_x0, width, right_x0, lintel_y0, lintel_y1, alpha, cool_frac)
GATES = [
    (8, 20, 296, 10, 18, 255, 0.00),   # frame 1 — foreground, full gold
    (32, 16, 276, 22, 28, 180, 0.18),  # frame 2
    (56, 12, 256, 32, 38, 130, 0.34),  # frame 3
    (72, 8, 244, 40, 44, 80, 0.50),    # frame 4 — deepest, dimmest, coolest
]


def _body_gradient(surf):
    """Deep vanishing-point ground: a near-black card that warms to (6,6,18)
    toward the centre-bottom, so the eye is pulled down the lit processional."""
    surf.fill((1, 1, 5))
    cx, cy = m(CXG), m(175)
    maxr = m(250)
    for r in range(maxr, 0, -3):
        f = r / maxr                       # 1 = dark rim, 0 = warm core
        col = lerp_color((6, 6, 18), (1, 1, 4), f)
        pygame.draw.circle(surf, col, (cx, cy), r)


def _floor_lines(surf):
    """Very faint 1px perspective floor rays converging on the VP — just enough
    to read the corridor's receding ground without competing with the fox."""
    lines = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    vp = (m(CXG), m(VP_Y))
    for fx in (-40, 30, 90, 160, 230, 290, 360):
        pygame.draw.line(lines, (150, 142, 180, 40), (m(fx), m(CH)), vp,
                         max(1, m(0.5)))
    surf.blit(lines, (0, 0))


def _draw_gate(surf, gate):
    """One torii frame: two full-height uprights + a thin connecting lintel,
    filled by the gold ramp lerped toward cool by the frame's corridor depth."""
    x0l, w, x0r, ly0, ly1, alpha, cool = gate
    top = lerp_color(GOLD_TOP, COOL_TOP, cool)
    bot = lerp_color(GOLD_BOT, COOL_BOT, cool)
    for x0 in (x0l, x0r):
        surf.blit(vgrad(m(w), m(CH), 0, top, bot, alpha), (m(x0), 0))
    lx0, lx1 = x0l, x0r + w
    surf.blit(vgrad(m(lx1 - lx0), m(ly1 - ly0), 0, top, bot, alpha),
              (m(lx0), m(ly0)))


def _gate_glow(surf, gate, color, peak, spread):
    """Additive outer bloom hugging the foreground gate's uprights + lintel, so
    the near frame reads as the brightest lantern-lit structure. The feather is
    composited with BLEND_RGBA_MAX onto its own layer (overlapping bars + rings
    take the MAX alpha, never summing) then blitted additively ONCE, so the
    top-corner upright/lintel overlaps can't blow out to white."""
    x0l, w, x0r, ly0, ly1, _, _ = gate
    glow = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    rects = [(x0l, 0, w, CH), (x0r, 0, w, CH), (x0l, ly0, x0r + w - x0l, ly1 - ly0)]
    for rx, ry, rw, rh in rects:
        for i in range(spread, 0, -1):
            a = int(peak * (1 - (i - 1) / spread) ** 1.9)
            if a <= 0:
                continue
            g = pygame.Surface((m(rw) + 2 * m(i), m(rh) + 2 * m(i)),
                               pygame.SRCALPHA)
            pygame.draw.rect(g, (*color, a), g.get_rect(), border_radius=m(i))
            glow.blit(g, (m(rx) - m(i), m(ry) - m(i)),
                      special_flags=pygame.BLEND_RGBA_MAX)
    surf.blit(glow, (0, 0), special_flags=ADD)


def _floor_glow(surf):
    """A warm lantern bloom spreading across the floor where the fox stands: a
    wide ellipse stack feathered with BLEND_RGBA_MAX (so the pool doesn't sum to
    a hot core) then blitted additively ONCE — lit from below at the fox's feet."""
    cx, cy = m(CXG), m(187)
    glow = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    layers = 12
    for i in range(layers, 0, -1):
        rx = int(m(30 + 84 * i / layers))
        ry = int(m(5 + 18 * i / layers))
        a = int(52 * (1 - (i - 1) / layers) ** 1.5)
        if a <= 0:
            continue
        e = pygame.Surface((rx * 2 + 2, ry * 2 + 2), pygame.SRCALPHA)
        pygame.draw.ellipse(e, (*GOLD_GLOW, a), e.get_rect())
        glow.blit(e, (cx - rx, cy - ry), special_flags=pygame.BLEND_RGBA_MAX)
    # Normal alpha-composite (NOT additive): BLEND_ADD ignores src alpha for RGB
    # and would blow the whole floor to solid gold; a carried-alpha blit keeps
    # the pool at the intended low 30-50 alpha.
    surf.blit(glow, (0, 0))


def _build_fox():
    """Aura BEHIND the already-outlined fox, composited on a shared 64×84 frame
    so both scale together and stay aligned; the outline is offset back onto
    that frame's origin (the outline pass pads by 2px)."""
    raw = build_kitsune(20)                 # 64×84
    aura = build_kitsune_aura()             # 64×84
    combined = pygame.Surface(raw.get_size(), pygame.SRCALPHA)
    combined.blit(aura, (0, 0))
    combined.blit(_add_outline(raw), (-2, -2))
    return pygame.transform.smoothscale(combined, (m(80), m(105)))  # 160×210 dev


def _mote(surf, x, y, r, a):
    """One soft gold mote: a feathered disc built on its own layer (rings drawn
    large→small so each overwrites, never summing) then blitted additively once,
    so the mote's peak stays the intended alpha instead of blowing to white."""
    layers = 6
    g = pygame.Surface((m(r) * 2 + 2, m(r) * 2 + 2), pygame.SRCALPHA)
    gc = m(r) + 1
    for i in range(layers, 0, -1):
        rr = int(m(r) * i / layers)
        aa = int(a * (1 - (i - 1) / layers) ** 1.6)
        if rr <= 0 or aa <= 0:
            continue
        pygame.draw.circle(g, (255, 214, 128, aa), (gc, gc), rr)
    surf.blit(g, (m(x) - gc, m(y) - gc), special_flags=ADD)


def _motes(surf):
    """Soft gold motes drifting up the side margins between the gate frames —
    never over the fox — for a legendary ceremonial shimmer."""
    spots = [
        (100, 152, 5, 84), (113, 112, 6, 76), (91, 74, 4, 66),
        (216, 146, 5, 86), (206, 100, 6, 74), (225, 70, 5, 68),
    ]
    for x, y, r, a in spots:
        _mote(surf, x, y, r, a)


def _price_tag(surf):
    """A hanging plaque suspended from the foreground lintel: a 1px cord to a
    dark-wood plate with a gold edge and the price in bright gold."""
    ax, ay = 258, 18                        # cord anchor: right of the lintel
    pcx, pcy, pw, ph = 258, 160, 60, 22
    px0, py0 = pcx - pw // 2, pcy - ph // 2
    # cord
    pygame.draw.line(surf, (150, 120, 60), (m(ax), m(ay)), (m(pcx), m(py0)),
                     max(1, m(0.7)))
    pygame.draw.circle(surf, (210, 172, 78), (m(ax), m(ay)), max(1, m(1.2)))
    # plate — subtle wood gradient, dark contact keyline, gold edge
    rect = pygame.Rect(m(px0), m(py0), m(pw), m(ph))
    surf.blit(vgrad(rect.w, rect.h, m(3), (48, 34, 16), (30, 20, 8), 255),
              rect.topleft)
    pygame.draw.rect(surf, (12, 8, 4), rect, width=max(1, m(1.4)),
                     border_radius=m(3))
    pygame.draw.rect(surf, (200, 162, 60), rect.inflate(-m(2), -m(2)),
                     width=max(1, m(1.0)), border_radius=m(2))
    plain_text(surf, "3,500", font(9), rect.center, (255, 202, 104),
               shadow_a=0, weight=m(0.9), keyline=(20, 12, 4), kw=m(0.7))


def render_card():
    """Author the full depth-gate card oversized, return the crisp 320×200."""
    big = pygame.Surface((m(CW), m(CH)), pygame.SRCALPHA)
    _body_gradient(big)
    _floor_lines(big)
    # receding gates FIRST (deepest → nearer), so they read as a z-stack behind.
    for gate in reversed(GATES[1:]):
        _draw_gate(big, gate)
    _floor_glow(big)
    fox = _build_fox()
    big.blit(fox, (m(CXG) - fox.get_width() // 2, m(185) - fox.get_height()))
    # foreground gate LAST + its bloom, so the near frame owns the front plane.
    _gate_glow(big, GATES[0], GOLD_GLOW, peak=26, spread=8)
    _draw_gate(big, GATES[0])
    _motes(big)
    _price_tag(big)
    return pygame.transform.smoothscale(big, (CW, CH))


# =============================================================================
# Review canvas — the card at 1× plus a 2× detail view, labelled.
# =============================================================================
def main():
    card1 = render_card()
    card2 = pygame.transform.smoothscale(card1, (CW * 2, CH * 2))

    PAD = 24
    canvas_w = CW * 2 + PAD * 2
    y_title = 12
    y_card1 = 46
    y_lab1 = y_card1 + CH + 6
    y_card2 = y_lab1 + 22
    y_lab2 = y_card2 + CH * 2 + 6
    canvas_h = y_lab2 + 22
    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((12, 12, 20))

    title = _font(18, True)
    tt = title.render("item_card_redesign  ·  depth-gate  ·  round 1  ·  LEGENDARY",
                      True, (232, 224, 200))
    canvas.blit(tt, tt.get_rect(midtop=(canvas_w // 2, y_title)))

    lab = _font(13, True)
    canvas.blit(card1, ((canvas_w - CW) // 2, y_card1))
    l1 = lab.render("1×  ·  320×200 card", True, (200, 196, 216))
    canvas.blit(l1, l1.get_rect(midtop=(canvas_w // 2, y_lab1)))

    canvas.blit(card2, ((canvas_w - CW * 2) // 2, y_card2))
    l2 = lab.render("2× detail", True, (200, 196, 216))
    canvas.blit(l2, l2.get_rect(midtop=(canvas_w // 2, y_lab2)))

    out = "/home/user/skybit/docs/item_card_redesign/depth-gate/round_1.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(canvas, out)
    print("saved", out, canvas.get_size())


if __name__ == "__main__":
    main()
