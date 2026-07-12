"""Item-name size + position options: BEFORE vs 4 variants.

Patches sc._name_on per panel before calling sc.draw_card; no production
code changes. Each panel is a full card (skin_mummy, affordable, no
equipped flag) at SS scale.

Output: docs/store_card_v5_name_size/showcase.png
"""
import os, sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.store_cards as sc
from game.hud import _font as hud_font

SID    = "skin_mummy"
CARD_W = sc.CARD_W * sc.SS          # 324
CARD_H = sc.CARD_H * sc.SS + 16     # 216 — extra room so chip bottom isn't clipped
_INSET = sc._INSET

docs_dir = os.path.join(os.path.dirname(__file__), "..",
                        "docs", "store_card_v5_name_size")

_orig_name_on = sc._name_on


def make_name_on(sz_logical, dy_logical):
    """Return a _name_on drop-in that shifts center-y up by dy_logical logical px."""
    def _patched(surf, name, cx, cy, max_w):
        sz = sz_logical
        f = sc.font(sz)
        while sc._glyph_base(name, f, 0).get_width() > max_w and sz > 9:
            sz -= 0.5
            f = sc.font(sz)
        sc.plain_text(surf, name, f, (cx, cy - sc.m(dy_logical)),
                      (250, 248, 240), shadow_a=160,
                      weight=sc.m(0.9), keyline=(6, 6, 16), kw=sc.m(1.0))
    return _patched


def render_card(sz_logical, dy_logical):
    sc._name_on = make_name_on(sz_logical, dy_logical)
    surf = pygame.Surface((CARD_W, CARD_H), pygame.SRCALPHA)
    rect = pygame.Rect(sc.m(_INSET), sc.m(_INSET),
                       CARD_W - 2 * sc.m(_INSET),
                       CARD_H - 2 * sc.m(_INSET))
    sc.draw_card(surf, SID, rect, equipped=False, secret=False)
    sc._name_on = _orig_name_on
    return surf


# ── options ──────────────────────────────────────────────────────────────────
# (panel-id, sublabel, font-sz-logical, y-shift-logical)
OPTIONS = [
    ("BEFORE", "sz 13.5 · dy 0",  13.5, 0),
    ("A",      "sz 15.5 · dy 2↑", 15.5, 2),
    ("B",      "sz 15.5 · dy 4↑", 15.5, 4),
    ("C",      "sz 17 · dy 2↑",   17.0, 2),
    ("D",      "sz 17 · dy 4↑",   17.0, 4),
]

# ── layout ───────────────────────────────────────────────────────────────────
BG     = (8, 8, 20)
MARGIN = 24
GAP    = 10
HDR_H  = 44
LBL_H  = 44

n        = len(OPTIONS)
canvas_w = MARGIN * 2 + CARD_W * n + GAP * (n - 1)
canvas_h = MARGIN + HDR_H + CARD_H + LBL_H + MARGIN

canvas = pygame.Surface((canvas_w, canvas_h))
canvas.fill(BG)

hf   = hud_font(18, True)
htxt = hf.render(
    f"v5 item name — size + position options ({SID})",
    True, (210, 206, 224))
canvas.blit(htxt, ((canvas_w - htxt.get_width()) // 2,
                   MARGIN + (HDR_H - htxt.get_height()) // 2))

lbl_id = hud_font(16, True)
lbl_sm = hud_font(10, False)
panel_y = MARGIN + HDR_H

for col, (oid, sublabel, sz, dy) in enumerate(OPTIONS):
    x = MARGIN + col * (CARD_W + GAP)
    card = render_card(sz, dy)
    canvas.blit(card, (x, panel_y))

    ly = panel_y + CARD_H + 4
    tid = lbl_id.render(oid, True, (255, 230, 120))
    canvas.blit(tid, (x + (CARD_W - tid.get_width()) // 2, ly))
    ly += tid.get_height() + 1

    t = lbl_sm.render(sublabel, True, (130, 126, 150))
    canvas.blit(t, (x + (CARD_W - t.get_width()) // 2, ly))

out = os.path.join(docs_dir, "showcase.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print(f"Saved: {out}  ({canvas_w}×{canvas_h})")
