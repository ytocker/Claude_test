"""coin-tab store-confirm action button — Round 2 review sheet.

Addresses every art-director critique point:
  1. Dark enamel well (recessed circle) behind coin so coin reads against the
     gold plate with ≥40 luma contrast, not gold-on-gold.
  2. price_chip call removed; the button is the sole price display.
     "NOT ENOUGH COINS" state message is preserved.
  3. Price numeral bumped to 9.5 logical px, cream (255,240,190), slightly
     bolder weight.
  4. Max catalog price (12,000) stress-tested: numeral + coin + 5px margin
     all fit in the 50% gold segment without touching the seam.
  5. Seam rebuilt as an engraved groove: pre-shadow on gold side, 2px dark
     channel (12,10,20), 1px bright bevel on enamel side (80,75,65).
  6. GET IT brightened to (230,215,175); right-pointing chevron triangle
     appended as tap-affordance indicator.
  7. Unaffordable pill is flat near-neutral grey — warm ghost left / cool
     ghost right, overall value dropped so the pill recedes behind CANCEL.

Same SS=2 + monkey-patch pattern as Round 1; no live game files touched.
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
from game.store import StoreScene
from game import store_cards as sc
from game import store_data as sd
from game import store_catalog
from game.hud import _font
from game.surprise_box_variants import _draw_qmark
from game.store import UI_CREAM, NEAR_BLACK


def _patched_draw_confirm(self, surf) -> None:
    """Coin-tab split-cost pill replacing the equip-chip action button.
    The button is the sole price display — price_chip is not drawn."""
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
    m = sc.m

    CARD_X, CARD_W, CARD_TOP, CARD_H, CARD_RAD = 8, 184, 98, 230, 18
    R_HERO, DISC_CY = 41, 104
    GEM_R, GEM_CY, GEM_L_X, GEM_R_X = 11, 117, 33, 167
    NAME_FS, Y_NAME = 30, 155
    Y_BANNER, BANNER_W = 175, 120
    # price_chip row intentionally absent — button IS the price
    Y_BTN, BTN_H, BTN_W = 273, 30, 136
    Y_CANCEL, CANCEL_H, CANCEL_W = 308, 22, 80

    big = pygame.Surface((POP_W * sc.SS, POP_H * sc.SS), pygame.SRCALPHA)

    # ── card body ─────────────────────────────────────────────────────────────
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

    # ── corner gem pair ───────────────────────────────────────────────────────
    sc.facet_gem(big, m(GEM_L_X), m(GEM_CY), m(GEM_R), pal["gem"], pal["deep"])
    sc.facet_gem(big, m(GEM_R_X), m(GEM_CY), m(GEM_R), pal["gem"], pal["deep"])

    # ── item name ─────────────────────────────────────────────────────────────
    sc.plain_text(big, name, sc.font(NAME_FS),
                  (m(CX), m(Y_NAME)), (250, 248, 240),
                  shadow_a=160, weight=m(0.9),
                  keyline=(6, 6, 16), kw=m(1.0))

    # ── rarity banner ─────────────────────────────────────────────────────────
    sc._ribbon_lozenge(big, tier_word, m(CX), m(Y_BANNER), m(BANNER_W), pal)

    # ── unaffordable state message — a status label, not a price duplicate ────
    if not affordable:
        sc.plain_text(big, "NOT ENOUGH COINS", sc.font(9), (m(CX), m(251)),
                      (150, 166, 190), shadow_a=0)

    # ── coin-tab split-cost pill ──────────────────────────────────────────────
    BTN_H_D = m(BTN_H)          # 60 device px
    BTN_W_D = m(BTN_W)          # 272 device px
    prad    = BTN_H_D // 2      # 30px — full stadium cap

    # Gold segment occupies 50% of pill width so the max catalog price
    # ("12,000" at 9.5px logical) fits with ≥4px gap before the seam.
    SEG_SPLIT = BTN_W_D * 50 // 100   # 136 device px

    btn_x0 = m(CX) - BTN_W_D // 2
    btn_y0 = m(Y_BTN) - BTN_H_D // 2
    seam_x = btn_x0 + SEG_SPLIT
    sy0, sy1 = btn_y0 + m(2), btn_y0 + BTN_H_D - m(2)

    full_rect = pygame.Rect(btn_x0, btn_y0, BTN_W_D, BTN_H_D)
    l_rect    = pygame.Rect(btn_x0,           btn_y0, SEG_SPLIT,              BTN_H_D)
    r_rect    = pygame.Rect(btn_x0 + SEG_SPLIT, btn_y0, BTN_W_D - SEG_SPLIT, BTN_H_D)

    # Coin position — 8 logical-px left margin from gold segment left arc
    coin_margin = m(8)
    coin_r   = BTN_H_D // 2 - m(4)          # 22 device px
    coin_cx  = btn_x0 + coin_margin + coin_r  # btn_x0 + 38
    coin_cy  = btn_y0 + BTN_H_D // 2

    # Price numeral metrics — 9.5px logical font, left-anchored after coin
    price_txt = f"{price:,}"
    pf  = sc.font(9.5)
    pw  = sc._glyph_base(price_txt, pf, 0).get_width()
    price_gap = m(4)                            # 8px gap coin-right → text-left
    price_x   = coin_cx + coin_r + price_gap   # btn_x0 + 68

    # Right-segment centre for GET IT label unit
    right_seg_cx = btn_x0 + SEG_SPLIT + (BTN_W_D - SEG_SPLIT) // 2

    if affordable:
        # ── brushed gold segment (left) ───────────────────────────────────────
        sc.chip_body_stops(big, l_rect, prad,
                           [(0.0, (210, 185, 100)), (1.0, (160, 130, 60))],
                           (120, 95, 30), (255, 235, 160), gloss=55, gamma=1.04)

        # ── dark enamel segment (right) ───────────────────────────────────────
        sc._dark_chip_body(big, r_rect, prad,
                           [(0.0, (28, 24, 36)), (1.0, (20, 16, 28))],
                           (40, 36, 52), (90, 84, 72), gloss=14, gamma=1.04)

        # ── outer rim around the full pill ────────────────────────────────────
        sc.bevel_rim(big, full_rect, prad,
                     (80, 72, 52, 210), (200, 182, 132, 200), w=2)

        # ── engraved seam: pre-shadow / deep groove / bright bevel ────────────
        # The shadow lands on the gold side, the highlight on the enamel side,
        # so the groove reads as a recessed join between two fused materials.
        pygame.draw.line(big, (42, 34, 16),
                         (seam_x - 1, sy0), (seam_x - 1, sy1), 1)
        pygame.draw.line(big, (12, 10, 20),
                         (seam_x, sy0), (seam_x, sy1), 2)
        pygame.draw.line(big, (80, 75, 65),
                         (seam_x + 2, sy0), (seam_x + 2, sy1), 1)

        # ── dark enamel well — makes the coin visible against the gold plate ──
        # The well's luma (~14) vs coin face (~190+) gives >40 contrast units.
        well_r = coin_r + m(3)   # 28 device px
        pygame.draw.circle(big, (20, 15, 7), (coin_cx, coin_cy), well_r)
        pygame.draw.circle(big, (58, 44, 18), (coin_cx, coin_cy),
                           well_r, max(1, m(1)))

        # ── coin face on dark well ────────────────────────────────────────────
        sc.coin_glyph(big, coin_cx, coin_cy, coin_r)

        # ── price numeral: 9.5px logical, cream, payload typography ──────────
        sc.plain_text(big, price_txt, pf, (price_x + pw // 2, coin_cy),
                      (255, 240, 190), shadow_a=0, weight=m(1.0))

        # ── GET IT label + right-pointing chevron (tap affordance) ────────────
        get_it_f    = sc.font(9)
        get_it_col  = (230, 215, 175)
        get_it_raw_w = sc._glyph_base("GET IT", get_it_f, 0).get_width()
        chev_gap = m(3)   # 6 device px gap between label and chevron
        chev_w   = m(3)   # 6 device px chevron width
        chev_h   = m(4)   # 8 device px chevron half-height

        # Centre the [GET IT ▶] unit in the right segment
        text_cx = right_seg_cx - (chev_gap + chev_w) // 2
        sc.plain_text(big, "GET IT", get_it_f, (text_cx, coin_cy),
                      get_it_col, shadow_a=0, weight=m(0.9))

        chev_x = text_cx + get_it_raw_w // 2 + chev_gap
        pygame.draw.polygon(big, get_it_col, [
            (chev_x,          coin_cy - chev_h),
            (chev_x + chev_w, coin_cy),
            (chev_x,          coin_cy + chev_h),
        ])

    else:
        # ── flat desaturated grey pill, warm/cool ghost split ─────────────────
        # Overall value is dropped well below the affordable state so this pill
        # recedes behind the CANCEL button in the popup hierarchy.
        # Left half breathes just a tick of warmth; right stays cool — the
        # ghost of the two-material metaphor without any chroma.
        sc._dark_chip_body(big, l_rect, prad,
                           [(0.0, (46, 43, 42)), (1.0, (30, 28, 27))],
                           (24, 22, 22), (76, 72, 70), gloss=5, gamma=1.02)
        sc._dark_chip_body(big, r_rect, prad,
                           [(0.0, (40, 40, 45)), (1.0, (26, 26, 31))],
                           (22, 22, 26), (68, 68, 76), gloss=5, gamma=1.02)

        # ── barely-there outer rim ────────────────────────────────────────────
        sc.bevel_rim(big, full_rect, prad,
                     (28, 26, 32, 120), (80, 78, 88, 90), w=2)

        # ── muted seam groove ─────────────────────────────────────────────────
        pygame.draw.line(big, (18, 18, 22),
                         (seam_x, sy0), (seam_x, sy1), 2)
        pygame.draw.line(big, (50, 50, 56),
                         (seam_x + 2, sy0), (seam_x + 2, sy1), 1)

        # ── dim well + ghost coin (locked state signal) ───────────────────────
        well_r = coin_r + m(3)
        pygame.draw.circle(big, (18, 17, 17), (coin_cx, coin_cy), well_r)
        pygame.draw.circle(big, (42, 40, 40), (coin_cx, coin_cy),
                           well_r, max(1, m(1)))
        coin_surf = pygame.Surface((coin_r * 2 + 2, coin_r * 2 + 2), pygame.SRCALPHA)
        sc.coin_glyph(coin_surf, coin_r + 1, coin_r + 1, coin_r)
        coin_surf.set_alpha(42)
        big.blit(coin_surf, (coin_cx - coin_r - 1, coin_cy - coin_r - 1))

        # ── ghost price numeral ───────────────────────────────────────────────
        sc.plain_text(big, price_txt, pf, (price_x + pw // 2, coin_cy),
                      (70, 68, 76), shadow_a=0, weight=m(1.0))

        # ── ghost GET IT (no chevron — pill is untappable) ────────────────────
        sc.plain_text(big, "GET IT", sc.font(9),
                      (right_seg_cx, coin_cy),
                      (68, 67, 74), shadow_a=0)

    # ── cancel button ─────────────────────────────────────────────────────────
    h_can = m(CANCEL_H)
    w_can = m(CANCEL_W)
    can_r = pygame.Rect(m(CX) - w_can // 2, m(Y_CANCEL) - h_can // 2, w_can, h_can)
    sc._dark_chip_body(big, can_r, h_can // 2,
                       [(0.0, (18, 16, 26)), (1.0, (12, 10, 20))],
                       (30, 28, 42), (70, 66, 82), gloss=14, gamma=1.04)
    sc.plain_text(big, "CANCEL", sc.font(11), can_r.center,
                  (130, 124, 148), shadow_a=0)

    # ── overhanging hero disc + spotlight halo (crowns the card) ─────────────
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

    # ── downscale and composite onto screen ───────────────────────────────────
    pop = pygame.transform.smoothscale(big, (POP_W, POP_H))
    px  = (W - POP_W) // 2
    py  = (H - POP_H) // 2
    self._confirm_panel = pygame.Rect(px, py, POP_W, POP_H)
    surf.blit(pop, (px, py))


StoreScene._draw_confirm = _patched_draw_confirm

POP_W, POP_H = 200, 340
PX, PY = (W - POP_W) // 2, (H - POP_H) // 2


def render_panel(balance, item_id):
    sd.balance = lambda: balance
    scene = StoreScene()
    scene.view = "category"
    scene._confirm = item_id
    screen = pygame.Surface((W, H))
    scene.render(screen)
    return screen.subsurface((PX, PY, POP_W, POP_H)).copy()


# Use the max-price catalog item (12,000) to stress-test the gold segment.
TEST_ITEM = "skin_jet_fighter"
affordable   = render_panel(999_999, TEST_ITEM)
unaffordable = render_panel(0, TEST_ITEM)

# ── review sheet ──────────────────────────────────────────────────────────────
CW, CH = 460, 400
sheet = pygame.Surface((CW, CH))
sheet.fill((8, 8, 20))

hfont = _font(15, True)
htxt  = hfont.render("coin-tab · SPLIT-COST PILL  r2", True, (220, 190, 100))
sheet.blit(htxt, ((CW - htxt.get_width()) // 2, 10))

sheet.blit(affordable,   (0,   30))
sheet.blit(unaffordable, (220, 30))

# price annotation below each panel
pfont = _font(11, False)
for label, note, cx in (
    ("AFFORDABLE",  "12,000 coins", 100),
    ("UNAFFORDABLE", "0 / 12,000",  320),
):
    lt = _font(13, True).render(label, True, (200, 185, 140))
    sheet.blit(lt, (cx - lt.get_width() // 2, 378))
    nt = pfont.render(note, True, (130, 120, 100))
    sheet.blit(nt, (cx - nt.get_width() // 2, 392))

out = "/home/user/skybit/docs/store_confirm_popup/coin-tab/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
