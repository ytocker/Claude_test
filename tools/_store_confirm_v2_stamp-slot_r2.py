"""stamp-slot store-confirm action concept (v2) — Round 2 review sheet.

Same machined-console layout as Round 1 with three corrections from the
art-director: slot bevel inverted (dark-top / light-bottom) so the capsule
reads as cut INTO the faceplate rather than raised above it; BUY plunger
lifted to genuine lit-gold (mid-body lum ≥110); affordable coin marker
desaturated ~15% so it reads as price info, not a rival action.
"""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
import sys
import math
sys.path.insert(0, "/home/user/skybit")
import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from game.config import W, H
from game.store import StoreScene
from game import store_cards as sc
from game import store_data as sd
from game import store_catalog
from game.hud import _font
from game.surprise_box_variants import _draw_qmark
from game.store import UI_CREAM, NEAR_BLACK


def _draw_padlock(surf, cx, cy, col):
    """A tiny closed-padlock glyph — 7×9 logical body + a U-shackle arc — so the
    tarnished BUY reads as unavailable rather than merely dark."""
    bw, bh = sc.m(7), sc.m(9)
    body = pygame.Rect(cx - bw // 2, cy - bh // 2 + sc.m(1), bw, bh)
    pygame.draw.rect(surf, col, body, border_radius=max(1, sc.m(1.5)))
    sr = pygame.Rect(cx - sc.m(2.6), cy - bh // 2 - sc.m(3), sc.m(5.2), sc.m(6))
    pygame.draw.arc(surf, col, sr, 0.0, math.pi, max(1, sc.m(1.3)))


def _patched_draw_confirm(self, surf) -> None:
    """StoreScene._draw_confirm with the price+button zone swapped for the
    stamp-slot console. Kept-elements are identical to the live modal."""
    self._confirm_panel = None
    self.confirm_yes_rect = self.confirm_no_rect = None
    sid = self._confirm
    if sid is None:
        return

    scrim = pygame.Surface((W, H), pygame.SRCALPHA)
    scrim.fill((4, 4, 10, 180))
    surf.blit(scrim, (0, 0))

    secret = store_catalog.is_secret(sid) and not sd.is_owned(sid)
    tier = store_catalog.rarity(sid)
    pal = (sc.MYSTERY if secret
           else sc.RARITY.get(tier, sc.RARITY["common"]))
    tier_word = "MYSTERY" if secret else tier.upper()
    name = "???" if secret else self._disp_name(sid)
    price = store_catalog.cost(sid)
    affordable = sd.balance() >= price

    POP_W, POP_H = 200, 340
    CX = POP_W // 2
    SS = sc.SS
    m = sc.m

    CARD_X, CARD_W, CARD_TOP, CARD_H, CARD_RAD = 8, 184, 98, 230, 18
    R_HERO, DISC_CY = 41, 104
    GEM_R, GEM_CY, GEM_L_X, GEM_R_X = 11, 117, 33, 167
    NAME_FS, Y_NAME = 30, 155
    Y_BANNER, BANNER_W = 175, 120

    big = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)

    # ── card body (kept unchanged from R1) ────────────────────────────────────
    rect = pygame.Rect(m(CARD_X), m(CARD_TOP), m(CARD_W), m(CARD_H))
    rad = m(CARD_RAD)
    sc.drop_shadow(big, rect, rad, blur=m(8), alpha=165, dy=m(4))
    big.blit(sc.vgrad_stops(
        rect.w, rect.h, rad,
        [(0.0, sc.CARD_T), (1.0, sc.CARD_B)], 255, gamma=1.15),
        rect.topleft)
    sc.top_sheen(big, rect, rad, m(30), peak=56)
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    sc.bevel_rim(big, rect, rad, sc.CARD_RING_DEEP,
                 (*sc.CARD_RING_BRIGHT, 230), w=max(1, m(1.9)))
    tray = rect.inflate(-m(8), -m(8))
    pygame.draw.rect(big, (*sc.CARD_RING_BRIGHT, 55), tray,
                     width=max(1, m(1)), border_radius=rad - m(3))

    # ── corner gem pair (kept) ────────────────────────────────────────────────
    sc.facet_gem(big, m(GEM_L_X), m(GEM_CY), m(GEM_R), pal["gem"], pal["deep"])
    sc.facet_gem(big, m(GEM_R_X), m(GEM_CY), m(GEM_R), pal["gem"], pal["deep"])

    # ── name + rarity banner (kept) ───────────────────────────────────────────
    sc.plain_text(big, name, sc.font(NAME_FS),
                  (m(CX), m(Y_NAME)), (250, 248, 240),
                  shadow_a=160, weight=m(0.9),
                  keyline=(6, 6, 16), kw=m(1.0))
    sc._ribbon_lozenge(big, tier_word, m(CX), m(Y_BANNER), m(BANNER_W), pal)

    # ── stamp-slot: machined faceplate ────────────────────────────────────────
    face = pygame.Rect(m(16), m(200), m(168), m(52))
    sc._dark_chip_body(big, face, m(8),
                       [(0.0, (40, 38, 55)), (1.0, (25, 23, 38))],
                       (18, 17, 28), (96, 92, 112), gloss=16, gamma=1.04)

    # coin denomination marker (left of the slot)
    if affordable:
        # Draw coin to temp surface so we can knock saturation down ~15%,
        # making it read as price-info context rather than a rival action.
        _r_coin = m(9)
        _cc = _r_coin + 2
        _coin_tmp = pygame.Surface((_r_coin * 2 + 4, _r_coin * 2 + 4),
                                   pygame.SRCALPHA)
        sc.coin_glyph(_coin_tmp, _cc, _cc, _r_coin)
        _grey_over = pygame.Surface(_coin_tmp.get_size(), pygame.SRCALPHA)
        # 38/255 ≈ 15% neutral grey overlay within the coin silhouette
        pygame.draw.circle(_grey_over, (120, 120, 120, 38), (_cc, _cc), _r_coin)
        _coin_tmp.blit(_grey_over, (0, 0))
        big.blit(_coin_tmp, _coin_tmp.get_rect(center=(m(35), m(226))))
    else:
        # unpowered console: a grey blank disc where the gold coin would sit
        pygame.draw.circle(big, (58, 60, 72), (m(35), m(226)), m(9))
        pygame.draw.circle(big, (86, 90, 104), (m(35), m(226)), m(9),
                           width=max(1, m(1.2)))
        pygame.draw.circle(big, (44, 46, 58), (m(35), m(226)), m(6),
                           width=max(1, m(1)))

    # engraved static price slot (a capsule cut INTO the steel)
    slot = pygame.Rect(m(55), m(219), m(90), m(14))
    srad = slot.h // 2
    pygame.draw.rect(big, (14, 12, 20), slot, border_radius=srad)
    # Recessed slot bevel: dark at top (shadow cast by the overhanging slot lip),
    # bright at bottom (ambient light catching the slot floor). This is the
    # opposite of a raised ridge, which has light on top and dark below.
    pygame.draw.line(big, (8, 7, 12),
                     (slot.x + srad, slot.y + max(1, m(0.6))),
                     (slot.right - srad, slot.y + max(1, m(0.6))),
                     max(1, m(0.7)))
    pygame.draw.line(big, (80, 75, 65),
                     (slot.x + srad, slot.bottom - max(1, m(0.6))),
                     (slot.right - srad, slot.bottom - max(1, m(0.6))),
                     max(1, m(0.7)))
    slot_col = (248, 238, 210) if affordable else (110, 115, 130)
    sc.plain_text(big, f"{price:,}", sc.font(9), slot.center, slot_col,
                  shadow_a=0)

    # ── stamp-slot: BUY lever / plunger ───────────────────────────────────────
    BTN_W, BTN_H, Y_BTN = 136, 30, 273
    buy = pygame.Rect(m(CX) - m(BTN_W) // 2, m(Y_BTN) - m(BTN_H) // 2,
                      m(BTN_W), m(BTN_H))
    brad = buy.h // 2
    if affordable:
        # Lit-gold gradient: top (180,140,50) → bottom (130,100,32) gives
        # mid-body lum ≈121, well above the ≥110 target for a coin-gold button.
        sc._dark_chip_body(big, buy, brad,
                           [(0.0, (180, 140, 50)), (1.0, (130, 100, 32))],
                           (70, 52, 14), (255, 225, 120), gloss=32, gamma=1.04)
    else:
        sc._dark_chip_body(big, buy, brad,
                           [(0.0, (22, 20, 18)), (1.0, (14, 13, 12))],
                           (28, 26, 24), (70, 68, 66), gloss=10, gamma=1.04)
    # plunger stem nub on the right edge (flavour only)
    nub = pygame.Rect(buy.right - m(4), buy.centery - m(6), m(4), m(12))
    nub_col = (30, 22, 8) if affordable else (10, 9, 8)
    pygame.draw.rect(big, nub_col, nub, border_radius=max(1, m(2)))
    if affordable:
        sc.plain_text(big, "BUY", sc.font(13), (m(CX), m(Y_BTN)),
                      (248, 238, 210), shadow_a=150, weight=m(1.0),
                      keyline=(30, 22, 6), kw=m(1.0))
    else:
        _draw_padlock(big, m(CX), m(Y_BTN), (90, 85, 100))
        sc.plain_text(big, "NOT ENOUGH", sc.font(8), (m(CX), m(292)),
                      (150, 166, 190), shadow_a=0)

    # ── stamp-slot: CANCEL chip ───────────────────────────────────────────────
    CANCEL_W, CANCEL_H, Y_CANCEL = 80, 22, 308
    can_r = pygame.Rect(m(CX) - m(CANCEL_W) // 2, m(Y_CANCEL) - m(CANCEL_H) // 2,
                        m(CANCEL_W), m(CANCEL_H))
    sc._dark_chip_body(big, can_r, can_r.h // 2,
                       [(0.0, (18, 16, 26)), (1.0, (12, 10, 20))],
                       (30, 28, 42), (70, 66, 82), gloss=14, gamma=1.04)
    sc.plain_text(big, "CANCEL", sc.font(11), can_r.center,
                  (130, 124, 148), shadow_a=0)

    # ── overhanging disc + spotlight halo (kept — crowns the card) ────────────
    cx_ss, cy_ss, r_ss = m(CX), m(DISC_CY), m(R_HERO)
    sc._alpha_aura(big, cx_ss, cy_ss, r_ss + m(55), pal["glow"], peak=95, layers=24)
    sc._alpha_aura(big, cx_ss, cy_ss, r_ss + m(20), pal["glow"], peak=70, layers=12)
    sc.cabochon(big, cx_ss, cy_ss, r_ss, sc.CABO_LO, sc.CABO_HI,
                ring=pal["gem"], ring_a=50)
    if secret:
        _draw_qmark(big, cx_ss, cy_ss, int(r_ss * 1.17), UI_CREAM, NEAR_BLACK, thick=5)
    else:
        sc.blit_thumb(big, sid, cx_ss, cy_ss, int(r_ss * 1.5))
    sc.cabochon_glass(big, cx_ss, cy_ss, r_ss, tint=pal["gem"])

    # ── downscale + composite ─────────────────────────────────────────────────
    pop = pygame.transform.smoothscale(big, (POP_W, POP_H))
    px = (W - POP_W) // 2
    py = (H - POP_H) // 2
    self._confirm_panel = pygame.Rect(px, py, POP_W, POP_H)
    surf.blit(pop, (px, py))

    # Hit rects (logical coords map 1:1 post-downscale). CANCEL hit zone is
    # padded to a 32px-tall comfortable target though it draws smaller.
    self.confirm_no_rect = pygame.Rect(
        px + CX - CANCEL_W // 2, py + Y_CANCEL - 16, CANCEL_W, 32)
    if affordable:
        self.confirm_yes_rect = pygame.Rect(
            px + CX - BTN_W // 2, py + Y_BTN - BTN_H // 2, BTN_W, BTN_H)


StoreScene._draw_confirm = _patched_draw_confirm

POP_W, POP_H = 200, 340
PX, PY = (W - POP_W) // 2, (H - POP_H) // 2


def render_panel(balance):
    sd.balance = lambda: balance
    scene = StoreScene()
    scene.view = "category"
    scene._confirm = "skin_mummy"
    screen = pygame.Surface((W, H))
    scene.render(screen)
    return screen.subsurface((PX, PY, POP_W, POP_H)).copy()


affordable = render_panel(999_999)
unaffordable = render_panel(0)

# ── review sheet ────────────────────────────────────────────────────────────
CW, CH = 460, 400
sheet = pygame.Surface((CW, CH))
sheet.fill((8, 8, 20))

hfont = _font(15, True)
htxt = hfont.render("stamp-slot R2 · RECESSED SLOT · LIT GOLD BUY", True,
                    (220, 190, 100))
sheet.blit(htxt, ((CW - htxt.get_width()) // 2, 10))

sheet.blit(affordable, (0, 30))
sheet.blit(unaffordable, (220, 30))

lfont = _font(13, True)
for label, cx in (("AFFORDABLE", 100), ("NOT ENOUGH", 320)):
    lt = lfont.render(label, True, (200, 185, 140))
    sheet.blit(lt, (cx - lt.get_width() // 2, 380))

out = "/home/user/skybit/docs/store_confirm_popup_v2/stamp-slot/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())

# ── pixel verification (PIL) — never display, inspect only ──────────────────
from PIL import Image
img = Image.open(out)
w_px, h_px = img.size
print(f"sheet dimensions: {w_px}x{h_px}")

# BUY button center in the affordable (left) panel:
#   panel blitted at sheet (0, 30); BUY center at panel (CX=100, Y_BTN=273)
BUY_CX = 0 + 100
BUY_CY = 30 + 273
radius = 5
samples = []
for dy in range(-radius, radius + 1):
    for dx in range(-radius, radius + 1):
        px_val = img.getpixel((BUY_CX + dx, BUY_CY + dy))
        r, g, b = px_val[0], px_val[1], px_val[2]
        samples.append(0.299 * r + 0.587 * g + 0.114 * b)
avg_lum = sum(samples) / len(samples)
print(f"BUY face avg luminance (11×11 sample @ {BUY_CX},{BUY_CY}): {avg_lum:.1f}  target ≥110")
assert avg_lum >= 110, f"BUY face still too dark: {avg_lum:.1f}"

# Slot bevel check: sample a pixel just inside the top and bottom interior
# edges of the price slot in the affordable panel.
# Slot logical coords: y=219, h=14 → top interior ≈ y=220, bottom ≈ y=232
SLOT_CX = 0 + 100
SLOT_TOP_Y = 30 + 220
SLOT_BOT_Y = 30 + 232
top_pix = img.getpixel((SLOT_CX, SLOT_TOP_Y))[:3]
bot_pix = img.getpixel((SLOT_CX, SLOT_BOT_Y))[:3]
top_lum = 0.299 * top_pix[0] + 0.587 * top_pix[1] + 0.114 * top_pix[2]
bot_lum = 0.299 * bot_pix[0] + 0.587 * bot_pix[1] + 0.114 * bot_pix[2]
print(f"slot top  pixel {top_pix}  lum={top_lum:.1f}")
print(f"slot bot  pixel {bot_pix}  lum={bot_lum:.1f}")
print(f"bevel direction: top {'DARKER' if top_lum <= bot_lum else 'LIGHTER'} than bottom "
      f"({'✓ recessed' if top_lum <= bot_lum else '✗ still raised'})")
print("verification complete")
