"""Round-2 render for the bottom-shelf buy-confirm concept (v2).

Headless. Applies the art-director punch list over R1: unified price receipt
window, brighter BUY gold, unaffordable vertical-spacing fix, inset shelf
with micro-walls, warmed shelf lip, and deeper disabled-BUY recess.
"""
import os
import math

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()
pygame.display.set_mode((8, 8))

from game.config import W, H
from game import store, store_cards, store_catalog, store_data
from game.surprise_box_variants import _draw_qmark
from game.store import _draw_qmark as _store_qmark  # same symbol, keep import parity

store_data.load()

SID = "skin_mummy"


# ── the bottom-shelf _draw_confirm ────────────────────────────────────────────
def _draw_confirm_bottom_shelf(self, surf) -> None:
    """Buy-confirm with a raised shelf panel across the card base: price row on
    the lit lip, a warm-gold BUY as the primary action, muted CANCEL below.
    Unaffordable cools the shelf, greys the price, and recesses BUY behind a
    padlock + NOT ENOUGH read so the inert state survives colour-blindness."""
    self._confirm_panel = None
    self.confirm_yes_rect = self.confirm_no_rect = None
    sid = self._confirm
    if sid is None:
        return

    scrim = pygame.Surface((W, H), pygame.SRCALPHA)
    scrim.fill((4, 4, 10, 180))
    surf.blit(scrim, (0, 0))

    secret = store_catalog.is_secret(sid) and not store_data.is_owned(sid)
    tier = store_catalog.rarity(sid)
    pal = (store_cards.MYSTERY if secret
           else store_cards.RARITY.get(tier, store_cards.RARITY["common"]))
    tier_word = "MYSTERY" if secret else tier.upper()
    name = "???" if secret else self._disp_name(sid)
    price = store_catalog.cost(sid)
    affordable = bool(getattr(self, "_force_affordable", True))

    POP_W, POP_H = 200, 340
    CX = POP_W // 2
    SS = store_cards.SS
    m = store_cards.m

    CARD_X, CARD_W, CARD_TOP, CARD_H, CARD_RAD = 8, 184, 98, 230, 18
    R_HERO, DISC_CY = 41, 104
    GEM_R, GEM_CY, GEM_L_X, GEM_R_X = 11, 117, 33, 167
    NAME_FS, Y_NAME = 30, 155
    Y_BANNER, BANNER_W = 175, 120

    # Shelf inset 5 px from card sides — gives the "raised counter" illusion
    # via micro-wall strips in the flanking gaps.
    SHELF_X, SHELF_Y, SHELF_W, SHELF_H = 13, 235, 174, 87
    Y_PRICE = 244
    Y_BUY, BUY_W, BUY_H = 273, 136, 30
    # CANCEL pushed down so the unaffordable shortfall line has breathing room.
    Y_CANCEL, CANCEL_W, CANCEL_H = 314, 80, 22

    big = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)

    # ── card body (KEEP) ──────────────────────────────────────────────────────
    rect = pygame.Rect(m(CARD_X), m(CARD_TOP), m(CARD_W), m(CARD_H))
    rad = m(CARD_RAD)
    store_cards.drop_shadow(big, rect, rad, blur=m(8), alpha=165, dy=m(4))
    big.blit(store_cards.vgrad_stops(
        rect.w, rect.h, rad,
        [(0.0, store_cards.CARD_T), (1.0, store_cards.CARD_B)], 255, gamma=1.15),
        rect.topleft)
    store_cards.top_sheen(big, rect, rad, m(30), peak=56)
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    store_cards.bevel_rim(big, rect, rad, store_cards.CARD_RING_DEEP,
                          (*store_cards.CARD_RING_BRIGHT, 230), w=max(1, m(1.9)))
    tray = rect.inflate(-m(8), -m(8))
    pygame.draw.rect(big, (*store_cards.CARD_RING_BRIGHT, 55), tray,
                     width=max(1, m(1)), border_radius=rad - m(3))

    # ── corner gem pair (KEEP) ────────────────────────────────────────────────
    store_cards.facet_gem(big, m(GEM_L_X), m(GEM_CY), m(GEM_R),
                          pal["gem"], pal["deep"])
    store_cards.facet_gem(big, m(GEM_R_X), m(GEM_CY), m(GEM_R),
                          pal["gem"], pal["deep"])

    # ── name + rarity banner (KEEP) ───────────────────────────────────────────
    store_cards.plain_text(big, name, store_cards.font(NAME_FS),
                           (m(CX), m(Y_NAME)), (250, 248, 240),
                           shadow_a=160, weight=m(0.9),
                           keyline=(6, 6, 16), kw=m(1.0))
    store_cards._ribbon_lozenge(big, tier_word, m(CX), m(Y_BANNER), m(BANNER_W), pal)

    # ══ RAISED SHELF ══════════════════════════════════════════════════════════
    shelf_rect = pygame.Rect(m(SHELF_X), m(SHELF_Y), m(SHELF_W), m(SHELF_H))
    shelf_rad = m(CARD_RAD)

    if affordable:
        shelf_stops = [(0.0, (38, 40, 82)), (1.0, (20, 22, 50))]
    else:
        # Cooler, bluer-grey shelf reads as "asleep" without touching the frame.
        shelf_stops = [(0.0, (30, 32, 52)), (0.5, (22, 22, 42)), (1.0, (14, 14, 30))]

    # Flat top (the lit front lip), rounded bottom following the card corners.
    shelf = store_cards.vgrad_stops(shelf_rect.w, shelf_rect.h, 0, shelf_stops, 255)
    shelf = shelf.copy()
    shelf_mask = pygame.Surface(shelf_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(shelf_mask, (255, 255, 255, 255), shelf_mask.get_rect(),
                     border_bottom_left_radius=shelf_rad,
                     border_bottom_right_radius=shelf_rad)
    shelf.blit(shelf_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    # Subtle top sheen so the shelf face catches a little room light.
    store_cards.top_sheen(shelf, shelf.get_rect(), 0, m(20), peak=35)
    # Warmed top lip — (100,92,120) reads as lit indigo material rather than
    # a neutral UI stroke.
    lip = (100, 92, 120) if affordable else (62, 62, 86)
    pygame.draw.line(shelf, lip, (0, 0), (shelf_rect.w - 1, 0), max(1, m(1)))
    # Seat shadow where the shelf meets the card body above.
    seat = pygame.Surface((shelf_rect.w, m(6)), pygame.SRCALPHA)
    for yy in range(m(6)):
        a = int(120 * (1 - yy / m(6)))
        pygame.draw.line(seat, (0, 0, 0, a), (0, yy), (shelf_rect.w - 1, yy))
    big.blit(seat, (shelf_rect.x, shelf_rect.y - m(6)))
    big.blit(shelf, shelf_rect.topleft)

    # Micro-walls: 5-px-wide strips in the gap between the card rim and the
    # inset shelf add lit-left / shadowed-right architectural depth.
    # Only drawn up to the card's bottom radius to avoid corner artefacts.
    wall_draw_h = m(CARD_TOP + CARD_H - CARD_RAD - SHELF_Y)
    if wall_draw_h > 0:
        wall_w = m(SHELF_X - CARD_X)   # 5 logical px → 10 device px at SS=2
        # Left face: light concentrates at the shelf edge (xx = wall_w-1).
        lwall = pygame.Surface((wall_w, wall_draw_h), pygame.SRCALPHA)
        for xx in range(wall_w):
            a = int(50 * (xx / max(1, wall_w - 1)))
            pygame.draw.line(lwall, (130, 120, 165, a), (xx, 0), (xx, wall_draw_h - 1))
        big.blit(lwall, (m(CARD_X), m(SHELF_Y)))
        # Right face: shadow concentrates at the shelf edge (xx = 0).
        rwall = pygame.Surface((wall_w, wall_draw_h), pygame.SRCALPHA)
        for xx in range(wall_w):
            a = int(50 * (1 - xx / max(1, wall_w - 1)))
            pygame.draw.line(rwall, (0, 0, 0, a), (xx, 0), (xx, wall_draw_h - 1))
        big.blit(rwall, (m(SHELF_X + SHELF_W), m(SHELF_Y)))

    # ── unified price "receipt window" ────────────────────────────────────────
    price_txt = f"{price:,}"
    f_price = store_cards.font(10)
    tw = f_price.size(price_txt)[0]
    coin_r = m(8)
    coin_d = coin_r * 2
    gap = m(4)
    total = coin_d + gap + tw
    start_x = m(CX) - total // 2
    coin_cx = start_x + coin_r
    num_cx = start_x + coin_d + gap + tw // 2
    py_price = m(Y_PRICE)

    # One dark backing plate spans both the coin and the numeral — the coin no
    # longer sits on bare shelf while the numeral floats on a separate tag.
    plate_w = total + m(14)
    plate_h = max(coin_d + m(4), f_price.get_height() + m(8))
    plate = pygame.Rect(0, 0, plate_w, plate_h)
    plate.center = (m(CX), py_price)
    plate_surf = pygame.Surface(plate.size, pygame.SRCALPHA)
    pygame.draw.rect(plate_surf, (8, 8, 20, 165), plate_surf.get_rect(),
                     border_radius=m(6))
    # 1-px dark top edge — the recess shadow that makes the window feel inset.
    pygame.draw.line(plate_surf, (2, 2, 8, 220),
                     (m(3), 0), (plate_w - m(3) - 1, 0))
    # Faint bottom catch — ambient bounce from the shelf face below.
    pygame.draw.line(plate_surf, (55, 50, 85, 70),
                     (m(3), plate_h - 1), (plate_w - m(3) - 1, plate_h - 1))
    big.blit(plate_surf, plate.topleft)

    if affordable:
        store_cards.coin_glyph(big, coin_cx, py_price, coin_r)
        num_col = (248, 238, 210)
    else:
        # Grey the coin: draw it, then knock it back to slate.
        cs = pygame.Surface((coin_d + m(2), coin_d + m(2)), pygame.SRCALPHA)
        store_cards.coin_glyph(cs, cs.get_width() // 2, cs.get_height() // 2, coin_r)
        grey = pygame.Surface(cs.get_size(), pygame.SRCALPHA)
        grey.fill((70, 74, 92, 210))
        cs.blit(grey, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        big.blit(cs, cs.get_rect(center=(coin_cx, py_price)))
        num_col = (110, 115, 130)

    store_cards.plain_text(big, price_txt, f_price, (num_cx, py_price),
                           num_col, shadow_a=0, weight=m(0.7),
                           keyline=(6, 6, 16), kw=m(0.9))

    # ── BUY button ────────────────────────────────────────────────────────────
    buy = pygame.Rect(0, 0, m(BUY_W), m(BUY_H))
    buy.center = (m(CX), m(Y_BUY))
    buy_rad = buy.h // 2

    if affordable:
        # Brighter gold body (body luma ~68–90) so the button reads as
        # coin-gold you want to tap, not dark antique brass.
        store_cards._dark_chip_body(
            big, buy, buy_rad,
            [(0.0, (115, 90, 24)), (1.0, (88, 68, 18))],
            store_cards.CARD_RING_DEEP, store_cards.CARD_RING_BRIGHT,
            gloss=25, gamma=1.05)
        # Stronger glossy cap reinforces the bright-coin read.
        store_cards.top_sheen(big, buy, buy_rad, m(12), peak=65)
        store_cards.plain_text(big, "BUY", store_cards.font(14), buy.center,
                               (250, 240, 214), shadow_a=150, weight=m(1.0),
                               keyline=(24, 16, 4), kw=m(1.0))
    else:
        # Recessed enamel — darkened base + steeper inner-shadow curve so
        # "pressed-in / dead" reads harder at 1× without relying on hue alone.
        big.blit(store_cards.vgrad_stops(
            buy.w, buy.h, buy_rad,
            [(0.0, (14, 14, 20)), (1.0, (16, 16, 22))], 255), buy.topleft)
        inv = pygame.Surface(buy.size, pygame.SRCALPHA)
        for yy in range(buy.h):
            a = int(160 * (1 - yy / buy.h) ** 1.4)    # deeper top shadow vs R1
            pygame.draw.line(inv, (0, 0, 0, a), (0, yy), (buy.w, yy))
        for yy in range(buy.h):
            a = int(60 * (yy / buy.h) ** 2.4)          # faint light at bottom edge
            pygame.draw.line(inv, (150, 152, 172, a), (0, yy), (buy.w, yy))
        inv_mask = pygame.Surface(buy.size, pygame.SRCALPHA)
        pygame.draw.rect(inv_mask, (255, 255, 255, 255), inv_mask.get_rect(),
                         border_radius=buy_rad)
        inv.blit(inv_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        big.blit(inv, buy.topleft)
        pygame.draw.rect(big, (10, 10, 14), buy, width=max(1, m(1.4)),
                         border_radius=buy_rad)

        # Padlock + BUY label — both slate, colour-blind-safe inert read.
        slate = (150, 166, 190)
        lab = store_cards.font(13)
        lw = lab.size("BUY")[0]
        lock_h = m(11)
        lock_w = int(lock_h * 0.9)
        inner_gap = m(4)
        grp = lock_w + inner_gap + lw
        gx = m(CX) - grp // 2
        _padlock(big, gx + lock_w // 2, buy.centery, lock_h, slate)
        store_cards.plain_text(big, "BUY", lab,
                               (gx + lock_w + inner_gap + lw // 2, buy.centery),
                               slate, shadow_a=0, weight=m(0.6))
        # Shortfall text snugged directly under BUY — no more floating gap
        # that collides with CANCEL.
        store_cards.plain_text(big, "NOT ENOUGH COINS", store_cards.font(7),
                               (m(CX), buy.bottom + m(4)),
                               (150, 166, 190), shadow_a=0)

    # ── CANCEL (muted, tappable) ──────────────────────────────────────────────
    can = pygame.Rect(0, 0, m(CANCEL_W), m(CANCEL_H))
    can.center = (m(CX), m(Y_CANCEL))
    can_flat = pygame.Surface(can.size, pygame.SRCALPHA)
    can_flat.fill((0, 0, 0, 0))
    pygame.draw.rect(can_flat, (16, 16, 26, 120), can_flat.get_rect(),
                     border_radius=can.h // 2)
    big.blit(can_flat, can.topleft)
    store_cards.plain_text(big, "CANCEL", store_cards.font(10), can.center,
                           (130, 124, 148), shadow_a=0)

    # ── overhanging disc + halo (KEEP, crowns the card) ───────────────────────
    cx_ss, cy_ss, r_ss = m(CX), m(DISC_CY), m(R_HERO)
    store_cards._alpha_aura(big, cx_ss, cy_ss, r_ss + m(55), pal["glow"],
                            peak=95, layers=24)
    store_cards._alpha_aura(big, cx_ss, cy_ss, r_ss + m(20), pal["glow"],
                            peak=70, layers=12)
    store_cards.cabochon(big, cx_ss, cy_ss, r_ss,
                         store_cards.CABO_LO, store_cards.CABO_HI,
                         ring=pal["gem"], ring_a=50)
    if secret:
        _store_qmark(big, cx_ss, cy_ss, int(r_ss * 1.17),
                     store.UI_CREAM, store.NEAR_BLACK, thick=5)
    else:
        store_cards.blit_thumb(big, sid, cx_ss, cy_ss, int(r_ss * 1.5))
    store_cards.cabochon_glass(big, cx_ss, cy_ss, r_ss, tint=pal["gem"])

    # ── composite ─────────────────────────────────────────────────────────────
    pop = pygame.transform.smoothscale(big, (POP_W, POP_H))
    px = (W - POP_W) // 2
    py = (H - POP_H) // 2
    self._confirm_panel = pygame.Rect(px, py, POP_W, POP_H)
    surf.blit(pop, (px, py))

    self.confirm_no_rect = pygame.Rect(
        px + CX - CANCEL_W // 2, py + Y_CANCEL - CANCEL_H // 2, CANCEL_W, CANCEL_H)
    if affordable:
        self.confirm_yes_rect = pygame.Rect(
            px + CX - BUY_W // 2, py + Y_BUY - BUY_H // 2, BUY_W, BUY_H)


def _padlock(surf, cx, cy, h, color):
    """Tiny procedural padlock — rounded body + shackle arc — for the inert BUY."""
    bw = int(h * 0.92)
    bh = int(h * 0.60)
    body = pygame.Rect(0, 0, bw, bh)
    body.center = (cx, cy + int(h * 0.20))
    pygame.draw.rect(surf, color, body, border_radius=max(1, int(h * 0.14)))
    sr = int(h * 0.30)
    arc = pygame.Rect(cx - sr, body.top - sr, sr * 2, sr * 2)
    pygame.draw.arc(surf, color, arc, math.radians(15), math.radians(165),
                    max(1, int(h * 0.17)))
    # Keyhole punched dark so the lock reads at thumbnail size.
    kh = pygame.Rect(0, 0, max(1, int(h * 0.16)), max(1, int(h * 0.20)))
    kh.center = (cx, body.centery + int(h * 0.02))
    pygame.draw.rect(surf, (20, 20, 30), kh, border_radius=1)


# ── render both states ────────────────────────────────────────────────────────
store.StoreScene._draw_confirm = _draw_confirm_bottom_shelf


def _render(affordable):
    scene = store.StoreScene()
    scene._confirm = SID
    scene._force_affordable = affordable
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    scene._draw_confirm(surf)
    r = scene._confirm_panel
    crop = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
    crop.blit(surf, (0, 0), pygame.Rect(r.x, r.y, r.w, r.h))
    return crop


aff = _render(True)
una = _render(False)

# ── review sheet ──────────────────────────────────────────────────────────────
SCALE = 2
pw, ph = aff.get_width() * SCALE, aff.get_height() * SCALE
aff = pygame.transform.smoothscale(aff, (pw, ph))
una = pygame.transform.smoothscale(una, (pw, ph))

PAD, GAP, TITLE_H, LABEL_H = 40, 44, 76, 44
sheet_w = PAD * 2 + pw * 2 + GAP
sheet_h = TITLE_H + ph + LABEL_H + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
for y in range(sheet_h):
    t = y / sheet_h
    c = (int(14 + 8 * t), int(15 + 8 * t), int(30 + 14 * t))
    pygame.draw.line(sheet, c, (0, y), (sheet_w, y))

tfont = store_cards._font(30, True)
lfont = store_cards._font(22, True)


def _center_text(fnt, txt, cx, cy, col):
    img = fnt.render(txt, True, col)
    sheet.blit(img, img.get_rect(center=(cx, cy)))


_center_text(tfont, "BUY-CONFIRM v2  —  BOTTOM-SHELF  —  round 2",
             sheet_w // 2, TITLE_H // 2, (236, 202, 116))

x0 = PAD
x1 = PAD + pw + GAP
ytop = TITLE_H
sheet.blit(aff, (x0, ytop))
sheet.blit(una, (x1, ytop))
_center_text(lfont, "AFFORDABLE", x0 + pw // 2, ytop + ph + LABEL_H // 2,
             (214, 220, 236))
_center_text(lfont, "UNAFFORDABLE", x1 + pw // 2, ytop + ph + LABEL_H // 2,
             (214, 220, 236))

out_dir = "docs/store_confirm_popup_v2/bottom-shelf"
os.makedirs(out_dir, exist_ok=True)
out = os.path.join(out_dir, "round_2.png")
pygame.image.save(sheet, out)

print("saved", out, sheet.get_size())

# ── pixel verification via PIL (never displayed) ───────────────────────────────
from PIL import Image

img_pil = Image.open(out).convert("RGB")


def lum(r, g, b):
    return 0.299 * r + 0.587 * g + 0.114 * b


def sample(x, y):
    return img_pil.getpixel((x, y))


# Samples avoid text/glyph centres: x at popup-x 60 stays inside the BUY pill
# but well left of the "BUY" label and the padlock cluster.
by = ytop + int(ph * (273 / 340))
bx_body = x0 + int(pw * (60 / 200))   # popup x=60: BUY pill body, clear of text

# BUY button body (affordable) — target luma ≥ 65.
p = sample(bx_body, by)
buy_aff_lum = lum(*p)
print(f"BUY body (affordable): {p}  luma={buy_aff_lum:.1f}  "
      f"target≥65: {'OK' if buy_aff_lum >= 65 else 'FAIL'}")

# Shelf face (affordable) — sample below price row, above BUY, outside price
# plate. popup-x 25 is clear of the plate (centered at 100, half-width ~27).
sx = x0 + int(pw * (25 / 200))        # popup x=25: shelf body
sy = ytop + int(ph * (250 / 340))     # popup y=250: between price coin and BUY
p = sample(sx, sy)
shelf_lum = lum(*p)
card_body_lum = lum(*store_cards.CARD_B)
print(f"shelf face (affordable): {p}  luma={shelf_lum:.1f}  "
      f"card body luma={card_body_lum:.1f}  "
      f"clearly lighter: {'OK' if shelf_lum > card_body_lum + 5 else 'FAIL'}")

# BUY button body (unaffordable) — target luma ≤ 30.
bx_una = x1 + int(pw * (60 / 200))   # popup x=60: left of padlock cluster
p = sample(bx_una, by)
buy_una_lum = lum(*p)
print(f"BUY body (unaffordable): {p}  luma={buy_una_lum:.1f}  "
      f"target≤30: {'OK' if buy_una_lum <= 30 else 'FAIL'}")
