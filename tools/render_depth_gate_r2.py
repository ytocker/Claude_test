#!/usr/bin/env python3
"""
item_card_redesign · depth-gate · round 2 render.

Concept unchanged: the KITSUNE stands free-standing in the mouth of a receding
ceremonial corridor; the number of nested gate-frames == the rarity tier
(legendary == 4). Round 2 sharpens the read on the art-director notes:

  * The foreground frame is now unmistakably a TORII, not a generic doorway:
    its kasagi (top lintel) OVERHANGS the pillars and its ends sway up, and a
    second beam (nuki) crosses just below it. Gate 2 echoes only the overhang.
  * Value hierarchy is re-ordered fox > gate1 > gate2 > gate3 > gate4 > ground,
    so every inter-gate slot reads as a DARK gap, never a bright seam: the gate
    bloom peak + spread are pulled way down.
  * The top-centre lintel stack is spread out so four frames count cleanly.
  * Motes drop to four and ride the floor-ray perspective — warm near, cooling
    to pale as they recede — so they read as lit corridor dust, not embers.
  * Only the two nearest (widest) floor rays remain, brighter at the wide base.
  * The price plaque is enlarged so "3,500" survives the 162x100 downscale.

Authored in a 320x200 logical space (the brief's 2x author space); every gate,
gradient and glyph is drawn oversized (SS=2 -> 640x400) then ONE smoothscale
turns the geometry crisp. Both build targets safe: pure pygame, no numpy, no
mixer, no platform branches.
"""
import os
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from game.store_cards import m, vgrad, plain_text, font
from game.draw import lerp_color
from game.hud import _font
from game.animal_kitsune import build_kitsune, build_kitsune_aura
from game.parrot import _add_outline

ADD = pygame.BLEND_ADD
MIN = pygame.BLEND_RGBA_MIN

# ── logical card metrics (320x200) — the brief's 2x author space ──────────────
CW, CH = 320, 200
CXG = CW // 2                    # horizontal centre → vanishing-point x
VP_Y = 85                        # vanishing point slightly above midheight

# Legendary gold ramp + the cool tint each receding gate lerps toward.
GOLD_TOP = (255, 202, 104)
GOLD_BOT = (150, 92, 22)
GOLD_GLOW = (255, 168, 58)
COOL_TOP = (118, 148, 208)       # gates cool + recede into corridor depth
COOL_BOT = (40, 58, 104)

# The four nested frames, foreground → deepest. Each pillar is defined by its
# OUTER x (lo left / ro right, symmetric about centre) and width w; the lintel
# by (ly0, ly1). `overhang` is the kasagi's sideways reach past the pillars,
# `rise` the upward sway of its tips, `nuki` a second cross-beam (torii only).
# The lintel y's are spread so the top-centre stack counts as four clean bars,
# and only the front gate carries the full torii (overhang + sway + nuki).
GATES = [
    {"lo": 22,  "w": 18, "ro": 298, "ly0": 6,  "ly1": 15,
     "overhang": 11, "rise": 3, "nuki": (24, 30), "alpha": 255, "cool": 0.00},
    {"lo": 52,  "w": 14, "ro": 268, "ly0": 36, "ly1": 42,
     "overhang": 7,  "rise": 0, "nuki": None,     "alpha": 170, "cool": 0.20},
    {"lo": 80,  "w": 11, "ro": 240, "ly0": 47, "ly1": 52,
     "overhang": 0,  "rise": 0, "nuki": None,     "alpha": 118, "cool": 0.38},
    {"lo": 102, "w": 8,  "ro": 218, "ly0": 56, "ly1": 60,
     "overhang": 0,  "rise": 0, "nuki": None,     "alpha": 78,  "cool": 0.55},
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
    """Only the two NEAREST floor rays survive — the widest-spread pair framing
    the corridor mouth. Each is brightest at the wide base and fades to nothing
    well before the vanishing point, so it grounds the fox without drawing a
    hard line into the depth."""
    lines = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    vp = (m(CXG), m(VP_Y))
    col = (150, 142, 180)
    for bx in (10, 310):
        base = (m(bx), m(CH))
        steps = 48
        prev = base
        for i in range(1, steps + 1):
            t = i / steps
            x = int(base[0] + (vp[0] - base[0]) * t)
            y = int(base[1] + (vp[1] - base[1]) * t)
            # widest/brightest at the base; gone by ~70% of the way to the VP.
            a = int(56 * max(0.0, 1 - t / 0.72) ** 1.4)
            if a > 0:
                pygame.draw.line(lines, (*col, a), prev, (x, y), max(1, m(0.6)))
            prev = (x, y)
    surf.blit(lines, (0, 0))


def _fill_poly(surf, pts, top, bot, alpha):
    """Fill an arbitrary polygon (author-px points) with a vertical gold ramp so
    the swayed kasagi shares the exact gradient of the rectangular members."""
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0, y0 = int(min(xs)), int(min(ys))
    w, h = int(max(xs)) - x0, int(max(ys)) - y0
    if w <= 0 or h <= 0:
        return
    grad = vgrad(w, h, 0, top, bot, alpha)
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255),
                        [(p[0] - x0, p[1] - y0) for p in pts])
    grad.blit(mask, (0, 0), special_flags=MIN)
    surf.blit(grad, (x0, y0))


def _draw_gate(surf, g):
    """One frame: two full-height pillars + its lintel, filled by the gold ramp
    lerped toward cool by the frame's corridor depth. The foreground frame adds
    an overhanging, up-swept kasagi and a nuki cross-beam so it reads as a torii
    rather than a plain rectangular portal."""
    top = lerp_color(GOLD_TOP, COOL_TOP, g["cool"])
    bot = lerp_color(GOLD_BOT, COOL_BOT, g["cool"])
    a = g["alpha"]
    lo, ro, w = g["lo"], g["ro"], g["w"]
    # pillars
    surf.blit(vgrad(m(w), m(CH), 0, top, bot, a), (m(lo), 0))
    surf.blit(vgrad(m(w), m(CH), 0, top, bot, a), (m(ro - w), 0))
    # kasagi (top lintel), reaching past the pillars by `overhang`
    ly0, ly1, oh, rise = g["ly0"], g["ly1"], g["overhang"], g["rise"]
    kx0, kx1 = lo - oh, ro + oh
    if rise > 0:
        cap = oh
        pts = [(m(kx0), m(ly0 - rise)), (m(kx0 + cap), m(ly0)),
               (m(kx1 - cap), m(ly0)), (m(kx1), m(ly0 - rise)),
               (m(kx1), m(ly1 - rise)), (m(kx1 - cap), m(ly1)),
               (m(kx0 + cap), m(ly1)), (m(kx0), m(ly1 - rise))]
        _fill_poly(surf, pts, top, bot, a)
    else:
        surf.blit(vgrad(m(kx1 - kx0), m(ly1 - ly0), 0, top, bot, a),
                  (m(kx0), m(ly0)))
    # nuki: a thinner second beam spanning the opening (pillar-inner to
    # pillar-inner), NOT overhanging — the torii's second differentiator.
    if g["nuki"]:
        ny0, ny1 = g["nuki"]
        nx0, nx1 = lo + w, ro - w
        surf.blit(vgrad(m(nx1 - nx0), m(ny1 - ny0), 0, top, bot, a),
                  (m(nx0), m(ny0)))


def _gate_glow(surf, g, color, peak, spread):
    """A restrained additive bloom hugging the front frame's members. Peak +
    spread are kept low so the bloom stays skinned to the gold face and never
    lights the dark slot between gate1 and gate2 brighter than the face itself.
    Feathered with BLEND_RGBA_MAX on its own layer (overlaps take the MAX alpha,
    never sum) then blitted additively ONCE so corners can't blow to white."""
    lo, ro, w = g["lo"], g["ro"], g["w"]
    ly0, ly1, oh = g["ly0"], g["ly1"], g["overhang"]
    glow = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    rects = [(lo, 0, w, CH), (ro - w, 0, w, CH),
             (lo - oh, ly0, (ro + oh) - (lo - oh), ly1 - ly0)]
    for rx, ry, rw, rh in rects:
        for i in range(spread, 0, -1):
            a = int(peak * (1 - (i - 1) / spread) ** 2.1)
            if a <= 0:
                continue
            gg = pygame.Surface((m(rw) + 2 * m(i), m(rh) + 2 * m(i)),
                                pygame.SRCALPHA)
            pygame.draw.rect(gg, (*color, a), gg.get_rect(), border_radius=m(i))
            glow.blit(gg, (m(rx) - m(i), m(ry) - m(i)),
                      special_flags=pygame.BLEND_RGBA_MAX)
    surf.blit(glow, (0, 0), special_flags=ADD)


def _floor_glow(surf):
    """A warm lantern bloom pooling on the floor where the fox stands: an
    ellipse stack feathered with BLEND_RGBA_MAX then alpha-composited ONCE, so
    it lights the fox's feet without out-brightening the front gate face."""
    cx, cy = m(CXG), m(187)
    glow = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    layers = 12
    for i in range(layers, 0, -1):
        rx = int(m(28 + 80 * i / layers))
        ry = int(m(5 + 17 * i / layers))
        a = int(46 * (1 - (i - 1) / layers) ** 1.5)
        if a <= 0:
            continue
        e = pygame.Surface((rx * 2 + 2, ry * 2 + 2), pygame.SRCALPHA)
        pygame.draw.ellipse(e, (*GOLD_GLOW, a), e.get_rect())
        glow.blit(e, (cx - rx, cy - ry), special_flags=pygame.BLEND_RGBA_MAX)
    # Normal alpha-composite (NOT additive): BLEND_ADD ignores src alpha for RGB
    # and would blow the whole floor to solid gold.
    surf.blit(glow, (0, 0))


def _build_fox():
    """Aura BEHIND the already-outlined fox on a shared 64x84 frame so both
    scale together; the outline pass pads by 2px, offset back onto origin."""
    raw = build_kitsune(20)                 # 64x84
    aura = build_kitsune_aura()             # 64x84
    combined = pygame.Surface(raw.get_size(), pygame.SRCALPHA)
    combined.blit(aura, (0, 0))
    combined.blit(_add_outline(raw), (-2, -2))
    return pygame.transform.smoothscale(combined, (m(80), m(105)))  # 160x210 dev


def _mote(surf, x, y, r, a, tint):
    """One soft corridor mote: a feathered disc built large→small on its own
    layer (each ring overwrites, never sums) then blitted additively once, so
    the peak stays the intended alpha instead of blowing to white."""
    layers = 6
    g = pygame.Surface((m(r) * 2 + 2, m(r) * 2 + 2), pygame.SRCALPHA)
    gc = m(r) + 1
    for i in range(layers, 0, -1):
        rr = int(m(r) * i / layers)
        aa = int(a * (1 - (i - 1) / layers) ** 1.6)
        if rr <= 0 or aa <= 0:
            continue
        pygame.draw.circle(g, (*tint, aa), (gc, gc), rr)
    surf.blit(g, (m(x) - gc, m(y) - gc), special_flags=ADD)


# Four motes only, riding the two floor-ray diagonals (base 10/310 → VP 160,85)
# in the side margins: the NEAR pair warm gold, the receding pair cooled to a
# pale amber so they read as lit dust settling down the corridor, not embers.
MOTE_WARM = (255, 214, 128)
MOTE_COOL = (214, 220, 226)
MOTES = [
    (56, 150, 5, 88, MOTE_WARM),    # left, near + low → warm
    (96, 101, 4, 60, MOTE_COOL),    # left, receding + high → cool pale
    (264, 150, 5, 88, MOTE_WARM),   # right, near + low → warm
    (224, 101, 4, 60, MOTE_COOL),   # right, receding + high → cool pale
]


def _motes(surf):
    for x, y, r, a, tint in MOTES:
        _mote(surf, x, y, r, a, tint)


def _price_tag(surf):
    """A hanging plaque suspended from the foreground kasagi, enlarged so the
    price survives the downscale to 162x100. It sits lower-right, partly inside
    the front frame: a dark-wood plate with a gold edge and bright-gold price."""
    ax, ay = 250, 15                        # cord anchor under the kasagi
    pcx, pcy, pw, ph = 250, 160, 74, 26
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
    plain_text(surf, "3,500", font(11), rect.center, (255, 206, 112),
               shadow_a=0, weight=m(1.0), keyline=(20, 12, 4), kw=m(0.8))


def render_big():
    """Author the full depth-gate card oversized; return the 640x400 surface so
    the caller can smoothscale ONCE to any review/in-game size."""
    big = pygame.Surface((m(CW), m(CH)), pygame.SRCALPHA)
    _body_gradient(big)
    _floor_lines(big)
    # receding frames FIRST (deepest → nearer) so they stack behind the fox.
    for g in reversed(GATES[1:]):
        _draw_gate(big, g)
    _floor_glow(big)
    fox = _build_fox()
    big.blit(fox, (m(CXG) - fox.get_width() // 2, m(185) - fox.get_height()))
    # foreground torii LAST + its restrained bloom, owning the front plane.
    _gate_glow(big, GATES[0], GOLD_GLOW, peak=15, spread=5)
    _draw_gate(big, GATES[0])
    _motes(big)
    _price_tag(big)
    return big


# =============================================================================
# Display sheet — BEFORE (live card) · ROUND 1 · ROUND 2, at true 162x100.
# =============================================================================
def _before_card():
    """The current live store card for skin_kitsune (162x100)."""
    from game import store_cards
    return store_cards.render_card("skin_kitsune", equipped=False, owned=True)


def _round1_card():
    """The 1x card lifted out of round_1.png's review sheet, scaled to 162x100
    so the three panels compare like-for-like at true in-game size."""
    sheet = pygame.image.load(
        "/home/user/skybit/docs/item_card_redesign/depth-gate/round_1.png")
    card = sheet.subsurface(pygame.Rect(184, 46, 320, 200)).copy()
    return pygame.transform.smoothscale(card, (162, 100))


def main():
    big = render_big()
    r2 = pygame.transform.smoothscale(big, (162, 100))     # true in-game size

    panels = [("BEFORE  ·  live card", _before_card()),
              ("ROUND 1", _round1_card()),
              ("ROUND 2  (NEW)", r2)]

    CWp, CHp = 162, 100
    margin, gap = 12, 14
    y_title = 12
    y_cap = 50
    y_card = 72
    y_note = y_card + CHp + 8
    canvas_w = margin * 2 + CWp * 3 + gap * 2
    canvas_h = y_note + 30
    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((14, 14, 22))

    title = _font(18, True)
    tt = title.render(
        "item_card_redesign  ·  depth-gate  ·  round 2  ·  LEGENDARY (skin_kitsune)",
        True, (232, 224, 200))
    canvas.blit(tt, tt.get_rect(midtop=(canvas_w // 2, y_title)))

    cap = _font(13, True)
    note = _font(11, False)
    for i, (label, card) in enumerate(panels):
        x = margin + i * (CWp + gap)
        cx = x + CWp // 2
        cl = cap.render(label, True, (206, 202, 224))
        canvas.blit(cl, cl.get_rect(midtop=(cx, y_cap)))
        # thin frame so each 162x100 card reads as a discrete panel
        pygame.draw.rect(canvas, (60, 60, 78),
                         pygame.Rect(x - 2, y_card - 2, CWp + 4, CHp + 4), 1)
        canvas.blit(card, (x, y_card))
        nt = note.render("162x100 · in-game size", True, (150, 148, 168))
        canvas.blit(nt, nt.get_rect(midtop=(cx, y_note)))

    out = "/home/user/skybit/docs/item_card_redesign/depth-gate/round_2.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(canvas, out)
    print("saved", out, canvas.get_size())


if __name__ == "__main__":
    main()
