"""Round-2 review sheet — 'teal-weave' equipped-card concept.

Retargets body hue from rarity-green to teal-cyan (blue channel >= green at
every stop), switches the sunburst watermark from additive-bright to
dark-on-dark (alpha-40 darken so it reads as woven texture rather than glow),
and proves rarity-agnosticism by rendering the treatment on two skins from
different cost tiers (skin_mummy at 1100 and skin_ninja at 560).

The vgrad monkey-patch approach from round-1 is preserved intact: only the
body fill gradient (keyed on CARD_T/CARD_B) is intercepted; gold frame, dome,
gem, ribbon, name and chip are all untouched.
"""
import os
import sys
import math

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.store_cards as sc
import game.store_data as sd
from game.hud import _font as hud_font

sd.load()

PANEL_W, PANEL_H = 324, 200
rect = pygame.Rect(8, 8, 308, 184)

# Body gradient: teal-cyan bias (blue channel >= green at every stop) so the
# material reads enchanted/energized rather than rarity-green.
TEAL_STOPS = [
    (0.0,  (16, 44, 62)),   # top: cool dark teal-blue
    (0.45, (8,  44, 58)),   # mid: deep teal (green+blue balanced, B>G)
    (0.78, (5,  28, 42)),   # lower: near-navy
    (1.0,  (3,  12, 24)),   # bottom: near-black
]

CARD_T = sc.CARD_T   # (28, 30, 70) — intercept key
CARD_B = sc.CARD_B   # (12, 13, 38) — intercept key

_orig_vgrad = sc.vgrad

def _patched_vgrad(w, h, radius, top, bot, alpha=255, gamma=1.0):
    if top == CARD_T and bot == CARD_B:
        return sc.vgrad_stops(w, h, radius, TEAL_STOPS, 252, 1.15)
    return _orig_vgrad(w, h, radius, top, bot, alpha, gamma)


def _engage_patch():
    sc.vgrad = _patched_vgrad
    sc._card_cache.clear()


def _disengage_patch():
    sc.vgrad = _orig_vgrad
    sc._card_cache.clear()


# Dome centre in device px (the same panel/rect geometry as round-1).
dome_cx = rect.centerx
dome_cy = rect.y + sc.m(sc.CY_DISC) + sc._DOME_DY   # 8 + 68 + 10 = 86


def _make_watermark():
    """Sunburst spokes drawn dark-on-dark so they subtract lightness from the
    teal body rather than adding a glow — alpha-40 dark teal at normal blend
    reads as a woven textile watermark, invisible against the dome glass."""
    wm = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    wm.fill((0, 0, 0, 0))
    for i in range(24):
        if i % 2 == 0:                          # 12 alternating spokes
            angle = math.pi * 2 * i / 24
            pts = [
                (dome_cx + int(math.cos(angle - 0.06) * sc.m(28)),
                 dome_cy + int(math.sin(angle - 0.06) * sc.m(28))),
                (dome_cx + int(math.cos(angle + 0.06) * sc.m(28)),
                 dome_cy + int(math.sin(angle + 0.06) * sc.m(28))),
                (int(dome_cx + math.cos(angle + 0.04) * sc.m(52)),
                 int(dome_cy + math.sin(angle + 0.04) * sc.m(52))),
                (int(dome_cx + math.cos(angle - 0.04) * sc.m(52)),
                 int(dome_cy + math.sin(angle - 0.04) * sc.m(52))),
            ]
            pygame.draw.polygon(wm, (0, 12, 18, 40), pts)
    return wm


# --- Panel 1: UNEQUIPPED skin_mummy (baseline / price chip) ------------------
# Wallet stubbed high so the cream "price" chip appears (not the locked state)
# and the indigo body is the honest unequipped baseline for comparison.
orig_bal = sd.balance
sd.balance = lambda: 99999
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1, "skin_mummy", rect, equipped=False, secret=False)
sd.balance = orig_bal
sc._card_cache.clear()

# --- Panel 2: EQUIPPED skin_mummy — teal-weave + dark watermark --------------
_engage_patch()
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, "skin_mummy", rect, equipped=True, secret=False)
_disengage_patch()
p2.blit(_make_watermark(), (0, 0))   # normal alpha-blend: spokes darken body

# --- Panel 3: EQUIPPED skin_ninja — teal-weave + dark watermark --------------
_engage_patch()
p3 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p3, "skin_ninja", rect, equipped=True, secret=False)
_disengage_patch()
p3.blit(_make_watermark(), (0, 0))


# --- Pixel sanity checks (no PIL needed — pygame.Surface.get_at) -------------
def _luma(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]

# Lower card body — beneath dome, on the teal gradient, below the glass disc.
mid_body = p2.get_at((dome_cx, rect.bottom - sc.m(20)))
dome_area = p2.get_at((dome_cx, dome_cy))

r_mid, g_mid, b_mid = mid_body[:3]
print(f"mid-body RGBA : {mid_body}  (B={b_mid} >= G={g_mid} ?  {'PASS' if b_mid >= g_mid else 'FAIL'})")
assert b_mid >= g_mid, f"teal check FAIL: B({b_mid}) < G({g_mid}) — still reads green"

luma_mid  = _luma(mid_body[:3])
luma_dome = _luma(dome_area[:3])
print(f"mid-body luma : {luma_mid:.1f}   dome luma: {luma_dome:.1f}  ({'PASS' if luma_dome > luma_mid else 'FAIL — mid brighter than dome'})")
assert luma_dome > luma_mid, "value check FAIL: mid-body luma >= dome luma"


# --- Compose the review sheet ------------------------------------------------
BG   = (8,  8,  20)
PAD, GAP, HDR_H, LBL_H = 20, 16, 54, 34
GOLD = (222, 184, 92)
GREY = (150, 152, 168)
TEAL_COL = (0, 200, 210)

sheet_w = PAD + 3 * PANEL_W + 2 * GAP + PAD
sheet_h = PAD + HDR_H + LBL_H + PANEL_H + PAD
sheet   = pygame.Surface((sheet_w, sheet_h), pygame.SRCALPHA)
sheet.fill(BG)

title_f = hud_font(26, True)
lbl_f   = hud_font(18, True)

title_surf = title_f.render(
    "TEAL-WEAVE rarity test — reads equipped not rarity-change", True, GOLD)
sheet.blit(title_surf, (PAD, PAD + (HDR_H - title_surf.get_height()) // 2))

panels = [
    (p1, "UNEQUIPPED (mummy)", GREY),
    (p2, "EQUIPPED — mummy",   TEAL_COL),
    (p3, "EQUIPPED — ninja",   TEAL_COL),
]
row_y = PAD + HDR_H
for idx, (panel, label, col) in enumerate(panels):
    x   = PAD + idx * (PANEL_W + GAP)
    lbl = lbl_f.render(label, True, col)
    sheet.blit(lbl, (x + (PANEL_W - lbl.get_width()) // 2,
                     row_y + (LBL_H - lbl.get_height()) // 2))
    sheet.blit(panel, (x, row_y + LBL_H))

out = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..",
                 "docs", "store_equipped", "emerald_weave", "round_2.png"))
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
assert os.path.exists(out), "render did not save"
print("saved", out, sheet.get_size())
