#!/usr/bin/env python3
"""Round-2 review render for the `bead-clasp-nameplate` equipped indicator:
nameplate seats in the name band (cy=164, where _name_on wrote the cream
name), item display name stamped in dark ink as the equipped indicator, plate
gold matched to the frame beads via a shallow ramp, recessed via a cast-shadow
lip rather than floating above the card. Clasps are dropped because the inner
bead rails (x=18, x=306) fall entirely outside the plate x-span (74→250)."""
import os, sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import pygame; pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)
import game.store_cards as sc
import game.store_data as sd
from game.hud import _font as hud_font
sd.load()

SID = "skin_mummy"
PANEL_W, PANEL_H = sc.CARD_W * sc.SS, sc.CARD_H * sc.SS   # 324×200
ri = sc.m(sc._INSET)
rect = pygame.Rect(ri, ri, PANEL_W - 2 * ri, PANEL_H - 2 * ri)

# ── approved palette (note 6 — no Ramp-A values) ─────────────────────────────
_PLATE_TOP  = (255, 240, 190)   # inner cream — lighter ramp crown
_PLATE_BOT  = (236, 202, 116)   # outer bead gold — same metal as the frame
_DARK_LIP   = (9,   9,  22)    # cast-shadow top+left (light source top-left)
_CREAM_LGHT = (255, 240, 190)   # catch light bottom+right
_INK        = (46,  38,  18)   # dark stamp for the name
_KEY        = (9,   9,  22)    # outer keyline ring


def _half_rim(w, h, rad, col, alpha, stroke_w, top_heavy):
    """A full rounded-rect border masked by a vertical gradient so only the
    top-lit half (top_heavy=True) or bottom-lit half stays visible; avoids
    per-edge polygon drawing on a rounded shape, which breaks at the corner
    arcs on a shallow pill."""
    rim = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(rim, (*col, alpha), rim.get_rect(),
                     width=stroke_w, border_radius=rad)
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        t = y / max(1, h - 1)
        a = int(255 * (1 - t) ** 0.7) if top_heavy else int(255 * t ** 0.7)
        pygame.draw.line(mask, (255, 255, 255, a), (0, y), (w - 1, y))
    rim.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return rim


def draw_bead_clasp_nameplate(surf, sid):
    """Nameplate occupying the name band: a shallow frame-matched gold ramp,
    recessed into the card body with a cast-shadow lip (dark top+left, cream
    bottom+right), item display name as the dark-ink equipped indicator.
    No drop-shadow or floating geometry. Clasps are dropped because the inner
    bead rails sit outside the plate x-span — they would hover in open air."""
    m = sc.m
    cx, cy = 162, 164              # exact lane _name_on occupied
    w, h, rad = 176, 26, 8
    r = pygame.Rect(cx - w // 2, cy - h // 2, w, h)   # x:74→250, bottom:177

    # body fill — shallow ramp from cream crown to outer-bead-gold foot so the
    # plate reads as the same metal as the regalia frame surrounding it
    surf.blit(sc.vgrad_stops(r.w, r.h, rad,
                             [(0.0, _PLATE_TOP), (1.0, _PLATE_BOT)]),
              r.topleft)

    # recess: 2px dark cast-shadow on top+left, fading to nothing at the foot
    surf.blit(_half_rim(r.w, r.h, rad, _DARK_LIP, 230,
                        max(1, m(1.5)), top_heavy=True),
              r.topleft)
    # catch light: 1px cream on bottom+right, fading to nothing at the crown
    surf.blit(_half_rim(r.w, r.h, rad, _CREAM_LGHT, 190,
                        max(1, m(1)), top_heavy=False),
              r.topleft)

    # thin outer keyline closes the plate edge against the dark card ground
    kl = pygame.Surface(r.size, pygame.SRCALPHA)
    pygame.draw.rect(kl, (*_KEY, 160), kl.get_rect(),
                     width=max(1, m(1)), border_radius=rad)
    surf.blit(kl, r.topleft)

    # item name in dark ink — the name IS the equipped indicator on this plate
    name = sc._name(sid)
    sc.plain_text(surf, name.upper(), sc.font(10), (cx, cy), _INK,
                  shadow_a=0, tracking=m(1.0), weight=m(0.8))


# Panel 0 — UNEQUIPPED
sc._card_cache.clear()
p0 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p0, SID, rect, equipped=False, secret=False, owned=False)

# Panel 1 — EQUIPPED BASE (hang-tag + regalia frame, no nameplate)
sc._card_cache.clear()
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1, SID, rect, equipped=True, secret=False, owned=False)

# Panel 2 — CONCEPT: _name_on is monkey-patched to a no-op so the plate owns
# the name band without two overlapping text layers; restored immediately after
sc._card_cache.clear()
_orig_name_on = sc._name_on
sc._name_on = lambda *a, **kw: None       # plate owns this band; silence card
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=True, secret=False, owned=False)
sc._name_on = _orig_name_on               # restore for any downstream draws

draw_bead_clasp_nameplate(p2, SID)


# ── compose review sheet ──────────────────────────────────────────────────────
BG = (8, 8, 20)
PAD = 20
LBL_H = 34
SGAP = 20
SLBL_H = 24
xs = [20, 360, 700]
panel_y = 102

GOLD = (236, 202, 116)
GREY = (150, 150, 168)
CREAM = (246, 244, 232)

# zoom: full panel 2 at 2× so the nameplate detail is legible
zoom = pygame.transform.smoothscale(p2, (162, 100))
zoom = pygame.transform.scale2x(zoom)    # 324×200

sheet_w = xs[-1] + PANEL_W + PAD
sheet_h = panel_y + PANEL_H + LBL_H + SGAP + SLBL_H + zoom.get_height() + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)


def label(txt, x, y, w, col, size=18):
    f = hud_font(size, True)
    g = f.render(txt, True, col)
    sheet.blit(g, (x + (w - g.get_width()) // 2, y))


hf = hud_font(22, True)
hg = hf.render("equipped v4c — bead-clasp-nameplate · round 2 · skin_mummy", True, GOLD)
sheet.blit(hg, (PAD, PAD))

panels = [(p0, "UNEQUIPPED", GREY),
          (p1, "EQUIPPED BASE", GREY),
          (p2, "+ BEAD CLASP NAMEPLATE", CREAM)]
for (panel, lbl, col), x in zip(panels, xs):
    sheet.blit(panel, (x, panel_y))
    label(lbl, x, panel_y + PANEL_H + 8, PANEL_W, col)

zx = xs[2]
zy = panel_y + PANEL_H + LBL_H + SGAP
label("ZOOM · PANEL 2", zx, zy, PANEL_W, GREY, size=15)
sheet.blit(zoom, (zx, zy + SLBL_H))

out = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_equipped_v4c", "bead_clasp_nameplate", "round_2.png")
out = os.path.abspath(out)
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("wrote", out)
