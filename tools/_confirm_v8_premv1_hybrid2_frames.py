"""Card-frame /design run — 5 outline concepts on the locked silver design.

The base's gold bevel_rim + faint tray ring are patched out and a
`_frame_hook(big, rect, rad)` is injected right after the background
ornament, so every frame sits above the B5 web but below gems, name and the
overhanging hero — the natural z-order of a collectible-card frame.

Usage: python _confirm_v8_premv1_hybrid2_frames.py <round>
round 1 → colorways/frames_r1.png ; round 2 → frames_showcase_v2.png
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

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _confirm_v8_premv1_hybrid2 as h2
import _confirm_v8_premv1_hybrid2_colorway as cw
from _confirm_v8_premv1_hybrid2_scribbles import DESIGNS
from _confirm_v8_premv1_hybrid2_scribbles2 import hook_constellation
from _confirm_v8_premv1_hybrid2_name_layout import (NAME_ZONE_C, CHIP_CY,
                                                    BG_DEEP_A, BG_GLINT_A,
                                                    _chip_cy_zone)
import game.store as store_mod
import game.store_cards as sc
import game.store_data as store_data
import game.store_catalog as store_catalog
from game.store import StoreScene
from game.store_cards import m, bevel_rim, facet_gem
from PIL import Image, ImageDraw

POP_W, POP_H = 260, 442

# Frame stays in the popup's ORIGINAL outline gold (CARD_RING family) — the
# constructions add presence, the colour identity is untouched.
SIL_DEEP = (58, 48, 22)          # CARD_RING_DEEP
SIL_MID = (190, 154, 74)         # mid-gold between deep and bright
SIL_BRIGHT = (236, 202, 116)     # CARD_RING_BRIGHT
GEM_SIL = (220, 170, 60)
GEM_SIL_DEEP = (100, 62, 12)


def _patched_draw_frames():
    src = textwrap.dedent(inspect.getsource(StoreScene._draw_confirm))
    subs = [
        (r"_chip\(m\(CX\), m\(CHIP_CY\)\)", "pass"),
        (r'_btn\(buy_r, "BUY", locked=not affordable\)', "pass"),
        (r'_btn\(can_r, "CANCEL", is_cancel=True\)', "pass"),
        (r"NAME_FS, Y_NAME = 45, 213", f"NAME_FS, Y_NAME = 45, {NAME_ZONE_C}"),
        (r"_cy1 = _disc_bot_ss \+ _nfnt\.get_height\(\) // 2",
         f"_cy1 = m({NAME_ZONE_C}) - int(_nfnt.get_height() * 1.15) // 2"),
        # strip the stock gold frame: bevel + tray ring
        (r"store_cards\.bevel_rim\(big, rect, rad, store_cards\.CARD_RING_DEEP,"
         r"\s*\(\*store_cards\.CARD_RING_BRIGHT, 230\), w=max\(1, m\(1\.9\)\)\)",
         "pass"),
        (r"pygame\.draw\.rect\(big, \(\*store_cards\.CARD_RING_BRIGHT, 55\), tray,"
         r"\s*width=max\(1, m\(1\)\), border_radius=rad - m\(3\)\)",
         "pass"),
        # bg ornament then the frame, both under gems/name/hero
        (r"(\n\s*# ── corner gem pair)",
         r"\n    _bg_hook(big)\n    _frame_hook(big, rect, rad)\1"),
    ]
    for pat, rep in subs:
        src, n = re.subn(pat, rep, src)
        assert n == 1, f"patch failed: {pat}"
    ns = {}
    exec(compile(src, "<frames_draw>", "exec"), store_mod.__dict__, ns)
    return ns["_draw_confirm"]


# ── D1 · platinum double bevel ────────────────────────────────────────────────
def frame_double_bevel(big, rect, rad, _r2=True):
    # filled mid-band gives the frame body; the bevel rides on top of it
    band = rect.inflate(-m(3), -m(3))
    pygame.draw.rect(big, (*SIL_MID, 150), band, width=max(3, m(5)),
                     border_radius=rad - m(1))
    bevel_rim(big, rect, rad, SIL_DEEP, (*SIL_BRIGHT, 245), w=max(2, m(4)))
    inner = rect.inflate(-m(11), -m(11))
    pygame.draw.rect(big, (*SIL_BRIGHT, 170), inner, width=max(1, m(1.2)),
                     border_radius=rad - m(5))
    pygame.draw.rect(big, (*SIL_DEEP, 210), rect.inflate(-m(8), -m(8)),
                     width=max(1, m(1)), border_radius=rad - m(4))


# ── D2 · beaded silver (coin-edge milling) ────────────────────────────────────
def frame_beaded(big, rect, rad):
    bevel_rim(big, rect, rad, SIL_DEEP, (*SIL_BRIGHT, 235), w=max(2, m(2.4)))
    chan = rect.inflate(-m(11), -m(11))
    pygame.draw.rect(big, (*SIL_DEEP, 190), chan, width=max(1, m(1)),
                     border_radius=rad - m(5))
    bead_r, pitch = m(1.7), m(9)
    inset = m(7)
    bx0, bx1 = rect.left + m(20), rect.right - m(20)
    by0, by1 = rect.top + m(20), rect.bottom - m(20)
    x = bx0
    while x <= bx1:
        for yy in (rect.top + inset, rect.bottom - inset):
            pygame.draw.circle(big, (*SIL_BRIGHT, 225), (x, yy), bead_r)
        x += pitch
    y = by0
    while y <= by1:
        for xx in (rect.left + inset, rect.right - inset):
            pygame.draw.circle(big, (*SIL_BRIGHT, 225), (xx, y), bead_r)
        y += pitch
    for cxk, cyk in [(rect.left + m(11), rect.top + m(11)),
                     (rect.right - m(11), rect.top + m(11)),
                     (rect.left + m(11), rect.bottom - m(11)),
                     (rect.right - m(11), rect.bottom - m(11))]:
        pygame.draw.circle(big, (*SIL_BRIGHT, 250), (cxk, cyk), m(2.4))


# ── D3 · corner plates (TCG brackets) ─────────────────────────────────────────
def frame_corner_plates(big, rect, rad):
    bevel_rim(big, rect, rad, SIL_DEEP, (*SIL_BRIGHT, 230), w=max(2, m(2.2)))
    pygame.draw.rect(big, (*SIL_DEEP, 180), rect.inflate(-m(7), -m(7)),
                     width=max(1, m(1)), border_radius=rad - m(3))
    L = m(30)
    for cxk, cyk, sx, sy in [(rect.left, rect.top, 1, 1),
                             (rect.right, rect.top, -1, 1),
                             (rect.left, rect.bottom, 1, -1),
                             (rect.right, rect.bottom, -1, -1)]:
        ox, oy = cxk + sx * m(4), cyk + sy * m(4)
        for w_off, col, wid in ((0, (*SIL_MID, 235), m(3)),
                                (m(4), (*SIL_BRIGHT, 200), m(1.4))):
            o2x, o2y = ox + sx * w_off, oy + sy * w_off
            pygame.draw.lines(big, col, False,
                              [(o2x + sx * L, o2y + sy * m(10)),
                               (o2x + sx * m(10), o2y + sy * m(10)),
                               (o2x + sx * m(10), o2y + sy * L)],
                              max(2, int(wid)))
        pygame.draw.circle(big, (*SIL_BRIGHT, 250),
                           (ox + sx * m(13), oy + sy * m(13)), m(2.2))
    for exk, eyk in [(rect.left + m(5), rect.centery),
                     (rect.right - m(5), rect.centery)]:
        pygame.draw.line(big, (*SIL_BRIGHT, 210), (exk, eyk - m(12)),
                         (exk, eyk + m(12)), max(2, m(2)))


# ── D4 · filigree inlay channel ───────────────────────────────────────────────
def frame_filigree_inlay(big, rect, rad):
    bevel_rim(big, rect, rad, SIL_DEEP, (*SIL_BRIGHT, 225), w=max(2, m(1.8)))
    inner = rect.inflate(-m(12), -m(12))
    pygame.draw.rect(big, (*SIL_MID, 220), inner, width=max(2, m(1.8)),
                     border_radius=rad - m(5))
    tick, pitch, inset = m(4), m(8), m(6)
    x = rect.left + m(20)
    while x <= rect.right - m(20):
        for yy, s in ((rect.top + inset, 1), (rect.bottom - inset, -1)):
            pygame.draw.line(big, (*SIL_MID, 185),
                             (x - tick // 2, yy + s * tick // 2),
                             (x + tick // 2, yy - s * tick // 2), max(2, m(1.6)))
        x += pitch
    y = rect.top + m(20)
    while y <= rect.bottom - m(20):
        for xx, s in ((rect.left + inset, 1), (rect.right - inset, -1)):
            pygame.draw.line(big, (*SIL_MID, 185),
                             (xx + s * tick // 2, y - tick // 2),
                             (xx - s * tick // 2, y + tick // 2), max(2, m(1.6)))
        y += pitch
    for cxk, cyk in [(rect.left + m(9), rect.top + m(9)),
                     (rect.right - m(9), rect.top + m(9)),
                     (rect.left + m(9), rect.bottom - m(9)),
                     (rect.right - m(9), rect.bottom - m(9))]:
        pts = [(cxk, cyk - m(5)), (cxk + m(5), cyk), (cxk, cyk + m(5)),
               (cxk - m(5), cyk)]
        pygame.draw.polygon(big, (*SIL_BRIGHT, 235), pts)


# ── D5 · gem-set frame ────────────────────────────────────────────────────────
def frame_gemset(big, rect, rad):
    bevel_rim(big, rect, rad, SIL_DEEP, (*SIL_BRIGHT, 235), w=max(2, m(2.6)))
    pygame.draw.rect(big, (*SIL_DEEP, 190), rect.inflate(-m(8), -m(8)),
                     width=max(1, m(1)), border_radius=rad - m(4))
    stones = [(rect.left + m(13), rect.top + m(13), m(6)),
              (rect.right - m(13), rect.top + m(13), m(6)),
              (rect.left + m(13), rect.bottom - m(13), m(6)),
              (rect.right - m(13), rect.bottom - m(13), m(6)),
              (rect.left + m(6), rect.centery, m(5)),
              (rect.right - m(6), rect.centery, m(5))]
    for gx, gy, gr in stones:
        pygame.draw.circle(big, (*SIL_DEEP, 255), (gx, gy), gr + m(2.5))
        pygame.draw.circle(big, (*SIL_BRIGHT, 220), (gx, gy), gr + m(2.5),
                           max(1, m(1)))
        facet_gem(big, gx, gy, gr, GEM_SIL, GEM_SIL_DEEP)


FRAMES_R1 = [
    ("D1 · platinum-double-bevel", frame_double_bevel),
    ("D2 · beaded-silver", frame_beaded),
    ("D3 · corner-plates", frame_corner_plates),
    ("D4 · filigree-inlay", frame_filigree_inlay),
    ("D5 · gemset-frame", frame_gemset),
]
FRAMES_R2 = list(FRAMES_R1)


def main():
    round_no = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    frames = FRAMES_R1 if round_no == 1 else FRAMES_R2
    out_name = "frames_r1.png" if round_no == 1 else "frames_showcase_v2.png"

    _orig_bal = store_data.balance
    _orig_cost = store_catalog.cost
    _orig_chip_cy = h2.CHIP_CY
    store_data.balance = lambda: 99999
    store_catalog.cost = lambda sid: 1400
    h2._DRAW_FN[0] = _patched_draw_frames()
    h2.overlay_quatrefoil = lambda ov: None
    h2.CHIP_CY = CHIP_CY
    h2._chip_cy = _chip_cy_zone
    silver_label, silver = DESIGNS[0]
    store_mod._bg_hook = hook_constellation(silver["glint"], BG_DEEP_A, BG_GLINT_A)
    h2.overlay_bullion_chip = cw.make_chip_fn(silver["bar"])
    h2.overlay_buttons = cw.make_buttons_fn(silver["buy"], silver["can"])
    try:
        MARGIN, HEAD, GAP = 20, 58, 12
        strip_w = MARGIN * 2 + len(frames) * (POP_W + GAP) - GAP
        strip_h = HEAD + POP_H + MARGIN
        strip = Image.new("RGB", (strip_w, strip_h), (10, 9, 20))
        idr = ImageDraw.Draw(strip)
        idr.text((MARGIN, 18),
                 f"FIGURE D · card frames · round_{round_no} · {silver_label} · EPIC",
                 fill=(236, 214, 160))
        for i, (label, frame_fn) in enumerate(frames):
            store_mod._frame_hook = frame_fn
            pop = h2.render_popup("EPIC")
            pil = Image.frombytes("RGB", (POP_W, POP_H),
                                  pygame.image.tostring(pop, "RGB"))
            x = MARGIN + i * (POP_W + GAP)
            strip.paste(pil, (x, HEAD))
            idr.text((x + POP_W // 2, HEAD + POP_H + 6), label,
                     fill=(170, 170, 195), anchor="mt")

        out_img = strip.resize((strip_w * 2, strip_h * 2), Image.LANCZOS)
        out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "confirm_purchase_v8", "premium-v1", "colorways",
                           out_name)
        out_img.save(out)
        print("saved", out, out_img.size)
    finally:
        store_data.balance = _orig_bal
        store_catalog.cost = _orig_cost
        h2.CHIP_CY = _orig_chip_cy
        for attr in ("_bg_hook", "_frame_hook"):
            if hasattr(store_mod, attr):
                delattr(store_mod, attr)


if __name__ == "__main__":
    main()
