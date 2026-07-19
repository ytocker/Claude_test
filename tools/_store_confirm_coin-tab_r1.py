"""coin-tab store-confirm action-button concept — Round 1 review sheet.

Renders the buy-confirm popup exactly as StoreScene draws it, but with the
action button replaced by the `coin-tab` split-cost pill: a single ~240px
device-px pill split by an engraved seam into a warm brushed-gold coin+price
segment (hugged left) and a dark-enamel GET IT segment. Left panel = affordable,
right = unaffordable. Headless + procedural; no shipped assets touched.
"""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
import sys
sys.path.insert(0, "/home/user/skybit")
import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from game.config import W, H
from game import store as store_mod
from game.store import StoreScene
from game import store_cards as sc
from game import store_data as sd
from game import store_catalog
from game.hud import _font
from game.surprise_box_variants import _draw_qmark
from game.store import UI_CREAM, NEAR_BLACK


def _patched_draw_confirm(self, surf) -> None:
    """Copy of StoreScene._draw_confirm with the equip-chip action button
    swapped for the coin-tab split-cost pill. Everything else is identical."""
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
    Y_CHIP, CHIP_H = 229, 28
    Y_BTN, BTN_H, BTN_W = 273, 30, 136
    Y_CANCEL, CANCEL_H, CANCEL_W = 308, 22, 80

    big = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)

    # ── card body ─────────────────────────────────────────────────────────
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

    # ── corner gem pair ───────────────────────────────────────────────────
    sc.facet_gem(big, m(GEM_L_X), m(GEM_CY), m(GEM_R), pal["gem"], pal["deep"])
    sc.facet_gem(big, m(GEM_R_X), m(GEM_CY), m(GEM_R), pal["gem"], pal["deep"])

    # ── name (above banner) ───────────────────────────────────────────────
    sc.plain_text(big, name, sc.font(NAME_FS),
                  (m(CX), m(Y_NAME)), (250, 248, 240),
                  shadow_a=160, weight=m(0.9),
                  keyline=(6, 6, 16), kw=m(1.0))

    # ── rarity banner ─────────────────────────────────────────────────────
    sc._ribbon_lozenge(big, tier_word, m(CX), m(Y_BANNER), m(BANNER_W), pal)

    # ── price chip ────────────────────────────────────────────────────────
    sc.price_chip(big, m(CX), m(Y_CHIP), f"{price:,}", m(CHIP_H),
                  affordable=affordable)

    if not affordable:
        sc.plain_text(big, "NOT ENOUGH COINS", sc.font(9), (m(CX), m(251)),
                      (150, 166, 190), shadow_a=0)

    # ── coin-tab: split-cost pill (replaces the equip-chip action button) ──
    CX_D = m(100)
    Y_BTN_D = m(Y_BTN)
    BTN_H_D = m(BTN_H)
    BTN_W_D = m(BTN_W)
    SEG_SPLIT = BTN_W_D * 42 // 100

    btn_x0 = CX_D - BTN_W_D // 2
    btn_y0 = Y_BTN_D - BTN_H_D // 2
    prad = BTN_H_D // 2

    l_rect = pygame.Rect(btn_x0, btn_y0, SEG_SPLIT, BTN_H_D)
    r_rect = pygame.Rect(btn_x0 + SEG_SPLIT, btn_y0, BTN_W_D - SEG_SPLIT, BTN_H_D)
    full_rect = pygame.Rect(btn_x0, btn_y0, BTN_W_D, BTN_H_D)
    seam_x = btn_x0 + SEG_SPLIT
    coin_r = BTN_H_D // 2 - m(4)
    coin_cx = btn_x0 + m(10) + coin_r
    coin_cy = btn_y0 + BTN_H_D // 2
    price_txt = f"{price:,}"
    pf = sc.font(7.5)
    # plain_text() centres on a point; left-anchor the numeral by its own width.
    pw = sc._glyph_base(price_txt, pf, 0).get_width()
    price_x = btn_x0 + m(10) + coin_r * 2 + m(3)

    if affordable:
        sc.chip_body_stops(big, l_rect, prad,
                           [(0.0, (210, 185, 100)), (1.0, (160, 130, 60))],
                           (120, 95, 30), (255, 235, 160), gloss=55, gamma=1.04)
        sc._dark_chip_body(big, r_rect, prad,
                           [(0.0, (28, 24, 36)), (1.0, (20, 16, 28))],
                           (40, 36, 52), (90, 84, 72), gloss=14, gamma=1.04)
        sc.bevel_rim(big, full_rect, prad, (80, 72, 52, 210),
                     (200, 182, 132, 200), w=2)
        pygame.draw.line(big, (46, 38, 18, 180),
                         (seam_x, btn_y0 + 2), (seam_x, btn_y0 + BTN_H_D - 2), 2)
        sc.coin_glyph(big, coin_cx, coin_cy, coin_r)
        sc.plain_text(big, price_txt, pf, (price_x + pw // 2, coin_cy),
                      (255, 240, 190), shadow_a=0)
        sc.plain_text(big, "GET IT", sc.font(9),
                      (btn_x0 + SEG_SPLIT + (BTN_W_D - SEG_SPLIT) // 2, coin_cy),
                      (200, 190, 160), shadow_a=0, weight=m(0.9))
    else:
        sc._dark_chip_body(big, full_rect, prad,
                           [(0.0, (52, 48, 58)), (1.0, (38, 34, 46))],
                           (28, 26, 36), (80, 76, 90), gloss=10, gamma=1.04)
        sc.bevel_rim(big, full_rect, prad, (50, 46, 60, 180),
                     (100, 96, 112, 160), w=2)
        pygame.draw.line(big, (30, 28, 38, 120),
                         (seam_x, btn_y0 + 2), (seam_x, btn_y0 + BTN_H_D - 2), 2)
        coin_surf = pygame.Surface((coin_r * 2 + 2, coin_r * 2 + 2), pygame.SRCALPHA)
        sc.coin_glyph(coin_surf, coin_r + 1, coin_r + 1, coin_r)
        coin_surf.set_alpha(60)
        big.blit(coin_surf, (coin_cx - coin_r - 1, coin_cy - coin_r - 1))
        sc.plain_text(big, price_txt, pf, (price_x + pw // 2, coin_cy),
                      (90, 85, 100), shadow_a=0)
        sc.plain_text(big, "GET IT", sc.font(9),
                      (btn_x0 + SEG_SPLIT + (BTN_W_D - SEG_SPLIT) // 2, coin_cy),
                      (90, 85, 100), shadow_a=0)

    # ── cancel button ─────────────────────────────────────────────────────
    h_can = m(CANCEL_H)
    w_can = m(CANCEL_W)
    can_r = pygame.Rect(m(CX) - w_can // 2, m(Y_CANCEL) - h_can // 2, w_can, h_can)
    sc._dark_chip_body(big, can_r, h_can // 2,
                       [(0.0, (18, 16, 26)), (1.0, (12, 10, 20))],
                       (30, 28, 42), (70, 66, 82), gloss=14, gamma=1.04)
    sc.plain_text(big, "CANCEL", sc.font(11), can_r.center,
                  (130, 124, 148), shadow_a=0)

    # ── overhanging disc + spotlight halo (crowns the card) ───────────────
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

    # ── downscale and composite onto screen ───────────────────────────────
    pop = pygame.transform.smoothscale(big, (POP_W, POP_H))
    px = (W - POP_W) // 2
    py = (H - POP_H) // 2
    self._confirm_panel = pygame.Rect(px, py, POP_W, POP_H)
    surf.blit(pop, (px, py))


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

# ── review sheet ──────────────────────────────────────────────────────────
CW, CH = 460, 400
sheet = pygame.Surface((CW, CH))
sheet.fill((8, 8, 20))

hfont = _font(15, True)
htxt = hfont.render("coin-tab · SPLIT-COST PILL", True, (220, 190, 100))
sheet.blit(htxt, ((CW - htxt.get_width()) // 2, 10))

sheet.blit(affordable, (0, 30))
sheet.blit(unaffordable, (220, 30))

lfont = _font(13, True)
for label, cx in (("AFFORDABLE", 100), ("NOT ENOUGH", 320)):
    lt = lfont.render(label, True, (200, 185, 140))
    sheet.blit(lt, (cx - lt.get_width() // 2, 380))

out = "/home/user/skybit/docs/store_confirm_popup/coin-tab/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
