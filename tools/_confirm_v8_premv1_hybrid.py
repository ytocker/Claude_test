"""hybrid-1 · confirm_purchase_v8 · premium-v1 · user-directed hybrid

Base is the live `_draw_confirm` with the rarity banner restored to its
original seat below the item name (Y_BANNER=247) and the coin chip returned
to the shelf (CHIP_CY=402), then three premium-v1 elements grafted on top:

  · sovereign-seal (#1): amber BUY / muted-indigo CANCEL buttons and the
    quatrefoil engrave in the dead zone
  · obsidian-forge (#3): the bright bullion price bar — narrowed to 140 px so
    the original bottom gem pair still flanks it inside the shelf

The base renders through the real StoreScene._draw_confirm (exec-patched
constants only), so everything not explicitly grafted is pixel-identical to
BEFORE.
"""
import os
import sys
import re
import math
import inspect
import textwrap

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame
pygame.init()
pygame.display.set_mode((1, 1))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import game.store_cards as sc


def _safe_gloss(surf, rect, radius, peak=46):
    w, h = rect[2], rect[3]
    gsurf = pygame.Surface((w, h), pygame.SRCALPHA)
    gsurf.fill((0, 0, 0, 0))
    steps = 10
    for i in range(steps):
        t = i / (steps - 1)
        alpha = int(peak * (1 - t))
        bar_h = max(1, int(h * 0.45 * (1 - t)))
        pygame.draw.ellipse(gsurf, (255, 255, 255, alpha),
            (int(w * 0.1), int(h * 0.04 + i * 1.5), int(w * 0.8), bar_h))
    surf.blit(gsurf, (rect[0], rect[1]))
sc.gloss_sweep = _safe_gloss

import game.store as store_mod
import game.store_data as store_data
import game.store_catalog as store_catalog
from game.store import StoreScene
from game.store_cards import (m, SS, font, vgrad_stops, bevel_rim, top_sheen,
                              drop_shadow, coin_glyph, facet_gem, plain_text,
                              chip_body_stops, _glyph_base, _stamp_bold,
                              CARD_RING_BRIGHT, CARD_RING_DEEP,
                              GOLD_A_STOPS, GOLD_A_RIM_DARK, GOLD_A_RIM_BRIGHT,
                              GOLD_A_NUM)
from PIL import Image, ImageDraw

# ── fixtures (match all premium-v1 concept strips) ─────────────────────────────
TIERS = ["RARE", "EPIC", "LEGENDARY"]
SIDS = {"RARE": "skin_wizard", "EPIC": "skin_prism", "LEGENDARY": "skin_astronaut"}
NAMES = {"RARE": "FROST WING", "EPIC": "PRISM WING", "LEGENDARY": "INFERNO WING"}
PRICES = {"RARE": 720, "EPIC": 1400, "LEGENDARY": 2600}

POP_W, POP_H = 260, 442
CX = 130
BTN_W, BTN_H, BTN_RAD, BTN_CY, BTN_GAP = 99, 31, 12, 360, 10
BUY_CX = CX - (BTN_W + BTN_GAP) // 2
CAN_CX = CX + (BTN_W + BTN_GAP) // 2
CHIP_CY = 402

# sovereign-seal quatrefoil palette
Q_DEEP = (22, 24, 56)
AMBER_GLINT = (200, 165, 90)


# ── base: real _draw_confirm with banner/chip positions un-swapped ─────────────
def _patched_draw_confirm():
    src = textwrap.dedent(inspect.getsource(StoreScene._draw_confirm))
    src, n1 = re.subn(r"Y_BANNER, BANNER_W, BANNER_H = 402, 156, 23",
                      "Y_BANNER, BANNER_W, BANNER_H = 247, 156, 23", src)
    src, n2 = re.subn(r"CHIP_CY = 247", "CHIP_CY = 402", src)
    assert n1 == 1 and n2 == 1, f"constant patch failed: {n1}, {n2}"
    ns = {}
    exec(compile(src, "<hybrid_draw_confirm>", "exec"), store_mod.__dict__, ns)
    return ns["_draw_confirm"]


def render_base(draw_fn, tier):
    sid = SIDS[tier]

    class _Stub:
        _confirm = sid
        _confirm_panel = None
        confirm_yes_rect = None
        confirm_no_rect = None

        @staticmethod
        def _disp_name(_sid):
            return NAMES[tier]

    surf = pygame.Surface((360, 640))
    surf.fill((8, 8, 20))
    draw_fn(_Stub(), surf)
    return surf.subsurface(pygame.Rect(50, 40, POP_W, POP_H)).copy()


# ── graft 1: sovereign-seal BUY / CANCEL ───────────────────────────────────────
def overlay_buttons(ov):
    br = m(BTN_RAD)
    for cx_b, lbl, stops, lab_c, pk, rw, rim_d, rim_b in (
        (m(BUY_CX), "BUY",
         [(0.0, (120, 75, 18)), (1.0, (80, 45, 8))],
         (255, 248, 220), 28, m(2.0), GOLD_A_RIM_DARK, GOLD_A_RIM_BRIGHT),
        (m(CAN_CX), "CANCEL",
         [(0.0, (26, 28, 64)), (1.0, (14, 16, 44))],
         (150, 155, 200), 14, m(2.2), CARD_RING_DEEP, CARD_RING_BRIGHT),
    ):
        r = pygame.Rect(0, 0, m(BTN_W), m(BTN_H))
        r.center = (cx_b, m(BTN_CY))
        drop_shadow(ov, r, br, blur=m(3), alpha=100, dy=m(2))
        ov.blit(vgrad_stops(r.w, r.h, br, stops, 255), r.topleft)
        top_sheen(ov, r, br, m(12), peak=pk)
        bevel_rim(ov, r, br, rim_d, (*rim_b, 235), w=max(1, rw))
        plain_text(ov, lbl, font(14 if lbl == "BUY" else 13), r.center, lab_c,
                   shadow_a=110, weight=m(0.8), keyline=(8, 6, 20), kw=m(0.9))


# ── graft 2: sovereign-seal quatrefoil in the dead zone ────────────────────────
def overlay_quatrefoil(ov):
    cx, cy = m(CX), m(297)
    d, rl = m(13), m(13)
    layer = pygame.Surface(ov.get_size(), pygame.SRCALPHA)
    centers = [(cx, cy - d), (cx, cy + d), (cx - d, cy), (cx + d, cy)]
    for lx, ly in centers:
        pygame.draw.circle(layer, (*Q_DEEP, 120), (lx, ly), rl, max(2, m(6)))
    for lx, ly in centers:
        pygame.draw.circle(layer, (*AMBER_GLINT, 180), (lx, ly), rl - m(1),
                           max(1, m(0.5)))
    ov.blit(layer, (0, 0))


# ── graft 3: obsidian-forge bullion price bar (narrowed to clear the gems) ─────
def overlay_bullion_chip(ov, price):
    txt = f"{price:,}"
    r = pygame.Rect(0, 0, m(140), m(28))
    r.center = (m(CX), m(CHIP_CY))
    chip_body_stops(ov, r, m(11), GOLD_A_STOPS, GOLD_A_RIM_DARK,
                    GOLD_A_RIM_BRIGHT, gloss=120)

    num_font = font(18)
    base = _stamp_bold(_glyph_base(txt, num_font, 0), m(0.7))
    bw = base.get_width()
    coin_d, gap = m(22), m(5)
    group_w = coin_d + gap + bw
    left = m(CX) - group_w // 2
    coin_glyph(ov, left + coin_d // 2, m(CHIP_CY), m(11))
    plain_text(ov, txt, num_font,
               (left + coin_d + gap + bw // 2, m(CHIP_CY)), GOLD_A_NUM,
               shadow_a=0, weight=m(0.7))

    for bx in (r.left + m(13), r.right - m(13)):
        _bolt_dot(ov, bx, m(CHIP_CY))


def _bolt_dot(ov, bx, by):
    pygame.draw.circle(ov, (60, 42, 12), (bx, by), m(2))
    ring = pygame.Surface((m(6), m(6)), pygame.SRCALPHA)
    pygame.draw.circle(ring, (180, 140, 60, 120), (m(3), m(3)), m(2), max(1, m(0.6)))
    ov.blit(ring, (bx - m(3), by - m(3)))
    arc_s = pygame.Surface((m(6), m(6)), pygame.SRCALPHA)
    pygame.draw.arc(arc_s, (200, 170, 100, 180),
                    pygame.Rect(0, 0, m(6) - 1, m(6) - 1),
                    3 * math.pi / 2, 2 * math.pi, 1)
    ov.blit(arc_s, (bx - m(3), by - m(3)))


def render_popup(draw_fn, tier):
    pop = render_base(draw_fn, tier)
    ov = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)
    overlay_quatrefoil(ov)
    overlay_buttons(ov)
    overlay_bullion_chip(ov, PRICES[tier])
    pop.blit(pygame.transform.smoothscale(ov, (POP_W, POP_H)), (0, 0))
    return pop


def main():
    _orig_bal = store_data.balance
    _orig_cost = store_catalog.cost
    store_data.balance = lambda: 99999
    store_catalog.cost = lambda sid: {v: PRICES[k] for k, v in SIDS.items()}.get(
        sid, _orig_cost(sid))
    try:
        draw_fn = _patched_draw_confirm()
        MARGIN, HEAD, GAP = 20, 58, 12
        strip_w = MARGIN * 2 + len(TIERS) * (POP_W + GAP) - GAP
        strip_h = HEAD + POP_H + MARGIN
        strip = Image.new("RGB", (strip_w, strip_h), (10, 9, 20))
        idr = ImageDraw.Draw(strip)
        idr.text((MARGIN, 18), "hybrid-1 · premium-v1 · base + #1 buttons/scribble + #3 chip",
                 fill=(236, 214, 160))
        for i, tier in enumerate(TIERS):
            pop = render_popup(draw_fn, tier)
            pil = Image.frombytes("RGB", (POP_W, POP_H),
                                  pygame.image.tostring(pop, "RGB"))
            x = MARGIN + i * (POP_W + GAP)
            strip.paste(pil, (x, HEAD))
            idr.text((x + POP_W // 2, HEAD + POP_H + 6), tier,
                     fill=(206, 190, 150), anchor="mt")
        out_img = strip.resize((strip_w * 2, strip_h * 2), Image.LANCZOS)
        out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                               "docs", "confirm_purchase_v8", "premium-v1", "hybrid-1")
        os.makedirs(out_dir, exist_ok=True)
        out = os.path.join(out_dir, "round_2.png")
        assert out_img.size == (1688, 1040), f"size mismatch: {out_img.size}"
        out_img.save(out)
        print("saved", out, out_img.size)
    finally:
        store_data.balance = _orig_bal
        store_catalog.cost = _orig_cost


if __name__ == "__main__":
    main()
