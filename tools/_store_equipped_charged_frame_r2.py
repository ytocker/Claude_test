"""Round-2 review sheet for the `charged-frame` equipped-card concept.

Off-screen only: renders four panels — UNEQUIPPED, BASE EQUIPPED, CHARGED-FRAME,
and a side-by-side GREYSCALE CHECK — so the art-director can evaluate the
energized emerald frame with radiant glow, crisp tray ring, dual charge-node
corners, and structural contrast in desaturated view.
Lives under tools/ so it never ships in the pygbag bundle.
"""
import os
import sys

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

# Device-px panel matches draw_card's SS author canvas so the concept reads at
# the same fidelity the live grid caches.
PANEL_W, PANEL_H = sc.CARD_W * sc.SS, sc.CARD_H * sc.SS
rect = pygame.Rect(sc.m(sc._INSET), sc.m(sc._INSET),
                   PANEL_W - 2 * sc.m(sc._INSET), PANEL_H - 2 * sc.m(sc._INSET))
rad = sc.m(17)

# Logical-to-device-px shorthand, matching the author's authoring scale.
m = sc.m

EQ_RIM_DEEP   = (6, 44, 28)
EQ_RIM_BRIGHT = (96, 206, 140)
EQ_GLOW       = (60, 200, 120)

SID = "skin_mummy"

# --- Panel 1: UNEQUIPPED (affordable price chip) ----------------------------
# Force a fat balance so the chip reads cream/affordable rather than locked.
orig_bal = sd.balance
sd.balance = lambda: 99999
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1, SID, rect, equipped=False, secret=False)
sd.balance = orig_bal
sc._card_cache.clear()

# --- Panel 2: BASE EQUIPPED (current behaviour) -----------------------------
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=True, secret=False)
sc._card_cache.clear()

# --- Panel 3: CHARGED-FRAME concept -----------------------------------------
p3 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p3, SID, rect, equipped=True, secret=False)
sc._card_cache.clear()

# Emerald bevel over the gold one — single bevel keeps the edge crisp; a
# second stacked stroke would muddy it.
sc.bevel_rim(p3, rect, rad, EQ_RIM_DEEP, (*EQ_RIM_BRIGHT, 235), w=max(1, m(2.45)))

# Tray ring at full readable alpha so it reads as a crisp double band;
# matching the outer rim colour exactly ties the inner band to the frame.
tray = rect.inflate(-m(7), -m(7))
trad = rad - m(4)
pygame.draw.rect(p3, (*EQ_RIM_BRIGHT, 150), tray,
                 width=max(1, m(1)), border_radius=trad)

# Two charge-node corner accents: top-left and bottom-right mirror the tier
# gem in the top-right, anchoring the frame as "powered". The dark notch on
# each hypotenuse distinguishes them from plain bevel thickening — they read
# as separate hardware rather than rim continuation.
# Top-left charge node
pygame.draw.polygon(p3, EQ_RIM_BRIGHT, [
    (rect.x + m(4), rect.y + m(4)),
    (rect.x + m(13), rect.y + m(4)),
    (rect.x + m(4), rect.y + m(13)),
])
pygame.draw.line(p3, EQ_RIM_DEEP,
                 (rect.x + m(13), rect.y + m(4)),
                 (rect.x + m(4), rect.y + m(13)), 2)
# Bottom-right charge node (mirrored)
pygame.draw.polygon(p3, EQ_RIM_BRIGHT, [
    (rect.right - m(4), rect.bottom - m(4)),
    (rect.right - m(13), rect.bottom - m(4)),
    (rect.right - m(4), rect.bottom - m(13)),
])
pygame.draw.line(p3, EQ_RIM_DEEP,
                 (rect.right - m(13), rect.bottom - m(4)),
                 (rect.right - m(4), rect.bottom - m(13)), 2)

# Outer emerald glow — additive rings radiate outward from the rim so the
# frame feels energized rather than painted; BLEND_ADD prevents the dark card
# body from washing out while letting the bright rim bleed naturally.
glow_layer = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
for i in range(6, 0, -1):
    gr = rect.inflate(i * 2, i * 2)
    a = int(50 * (i / 6) ** 1.8)
    pygame.draw.rect(glow_layer, (*EQ_GLOW, a), gr,
                     width=max(1, 2), border_radius=rad + i)
p3.blit(glow_layer, (0, 0), special_flags=pygame.BLEND_ADD)

# --- Panel 4: GREYSCALE CHECK ------------------------------------------------
# Desaturating BASE EQUIPPED and CHARGED side by side confirms that the emerald
# frame holds structural contrast independent of its hue.
def to_greyscale(surf):
    """Luminance-weighted desaturation (BT.601) preserving per-pixel alpha."""
    import PIL.Image
    raw = pygame.image.tobytes(surf, "RGBA")
    img = PIL.Image.frombytes("RGBA", surf.get_size(), raw)
    r, g, b, a = img.split()
    grey = PIL.Image.merge("RGB", (r, g, b)).convert("L").convert("RGB")
    grey_rgba = PIL.Image.merge("RGBA", (*grey.split(), a))
    return pygame.image.frombytes(grey_rgba.tobytes(), surf.get_size(), "RGBA")

p2_gs = to_greyscale(p2)
p3_gs = to_greyscale(p3)

# Fit both greyscale cards into one PANEL_W-wide panel, each at half width.
GAP_INNER = 4
SUB_W = (PANEL_W - GAP_INNER) // 2
SUB_H = int(round(SUB_W * PANEL_H / PANEL_W))
p2_gs_s = pygame.transform.smoothscale(p2_gs, (SUB_W, SUB_H))
p3_gs_s = pygame.transform.smoothscale(p3_gs, (SUB_W, SUB_H))

p4 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
# Centre the sub-cards vertically; leave room below for tiny sub-labels.
tiny_f = hud_font(10)
sub_lbl_h = tiny_f.get_height() + 3
y_off = (PANEL_H - SUB_H - sub_lbl_h) // 2
p4.blit(p2_gs_s, (0, y_off))
p4.blit(p3_gs_s, (SUB_W + GAP_INNER, y_off))

lbl_base = tiny_f.render("BASE", True, (160, 160, 160))
lbl_chg  = tiny_f.render("CHGD", True, (160, 160, 160))
p4.blit(lbl_base, ((SUB_W - lbl_base.get_width()) // 2,
                   y_off + SUB_H + 2))
p4.blit(lbl_chg,  (SUB_W + GAP_INNER + (SUB_W - lbl_chg.get_width()) // 2,
                   y_off + SUB_H + 2))

# --- Compose the 4-panel sheet -----------------------------------------------
BG = (8, 8, 20)
PAD, GAP, HDR_H, LBL_H = 20, 16, 48, 34
sheet_w = PAD + 4 * PANEL_W + 3 * GAP + PAD
sheet_h = PAD + HDR_H + LBL_H + PANEL_H + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

title_f = hud_font(26)
lbl_f   = hud_font(18)
GOLD = (236, 202, 116)
GREY = (150, 150, 168)
MINT = EQ_RIM_BRIGHT

title = title_f.render(
    "equipped card — charged-frame · skin_mummy  [round 2]", True, GOLD)
sheet.blit(title, (PAD, PAD + (HDR_H - title.get_height()) // 2))

panels = [
    (p1, "UNEQUIPPED",      GREY),
    (p2, "BASE EQUIPPED",   GREY),
    (p3, "CHARGED-FRAME",   MINT),
    (p4, "GREYSCALE CHECK", (140, 140, 140)),
]
for i, (panel, label, col) in enumerate(panels):
    px = PAD + i * (PANEL_W + GAP)
    ly = PAD + HDR_H
    lbl = lbl_f.render(label, True, col)
    sheet.blit(lbl, (px + (PANEL_W - lbl.get_width()) // 2,
                     ly + (LBL_H - lbl.get_height()) // 2))
    # SRCALPHA panels alpha-composite onto the dark sheet fill directly.
    sheet.blit(panel, (px, ly + LBL_H))

out = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_equipped", "charged_frame", "round_2.png")
out = os.path.abspath(out)
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved:", out, os.path.getsize(out), "bytes")
