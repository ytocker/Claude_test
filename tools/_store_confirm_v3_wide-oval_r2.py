#!/usr/bin/env python3
"""
wide-oval  ·  store buy-confirmation popup v3  ·  round 2

R2 revisions (art-director punch list):
 • Price numeral flipped to dark espresso (~48,30,10) on the cooler ivory
   face — dark-on-cream for ~10:1 contrast; keyline reduced to near-nothing.
 • Oval face cooled from warm yellow-cream toward paper ivory by pulling
   yellow saturation and lifting blue, breaking the warm-on-warm conflict
   with the gold BUY pill.
 • Oval reads recessed: drop-shadow removed; 1-px inset deboss line along
   the top-inner arc signals a slot/plaque, not a dome.
 • Unaffordable oval shifted from cold slate to desaturated warm taupe so
   the price plaque reads as a plaque even when locked.
 • NOT ENOUGH label warmed from cool blue to muted amber.
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

from PIL import Image

import game.store as store_mod
import game.store_cards as sc
import game.store_data as sd
import game.store_catalog as store_catalog
from game.config import W, H

_draw_qmark = store_mod._draw_qmark
UI_CREAM = store_mod.UI_CREAM
NEAR_BLACK = store_mod.NEAR_BLACK


def _price_in_oval(big, cx_d, cy_d, price, affordable):
    """Gold coin + numeral centred together inside the ivory oval."""
    txt = f"{price:,}"
    coin_r = sc.m(15)
    coin_d = coin_r * 2
    gap = sc.m(5)
    num_font = sc.font(22)
    num_w = num_font.render(txt, True, (255, 255, 255)).get_width()
    total = coin_d + gap + num_w
    left = cx_d - total // 2
    coin_cx = left + coin_r
    num_cx = left + coin_d + gap + num_w // 2

    if affordable:
        sc.coin_glyph(big, coin_cx, cy_d, coin_r)
        # Dark espresso numeral on cooler ivory — ~10:1 contrast; keyline
        # reduced to near-invisible so it doesn't add visual noise over cream.
        sc.plain_text(big, txt, num_font, (num_cx, cy_d), (48, 30, 10),
                      shadow_a=0, weight=sc.m(0.9),
                      keyline=(38, 28, 8), kw=sc.m(0.4))
    else:
        # grey coin + grey rim so the whole plaque reads inert
        pygame.draw.circle(big, (150, 152, 162), (coin_cx, cy_d), coin_r)
        pygame.draw.circle(big, (96, 100, 114), (coin_cx, cy_d), coin_r,
                           width=max(1, sc.m(1.4)))
        pygame.draw.circle(big, (122, 126, 140), (coin_cx, cy_d),
                           coin_r - sc.m(3), width=max(1, sc.m(1)))
        sc.plain_text(big, txt, num_font, (num_cx, cy_d), (110, 115, 130),
                      shadow_a=0, weight=sc.m(0.6),
                      keyline=(22, 22, 30), kw=sc.m(0.9))


def _padlock(big, cx, cy):
    """Compact padlock silhouette with a 1px dark keyline so it reads as a lock
    at 1x screen size — the inert-BUY affordance marker."""
    pk_w, pk_h = sc.m(16), sc.m(13)
    body_r = pygame.Rect(cx - pk_w // 2, cy - pk_h // 2 + sc.m(2),
                         pk_w, pk_h - sc.m(3))
    pygame.draw.rect(big, (28, 30, 44), body_r.inflate(sc.m(2), sc.m(2)),
                     border_radius=sc.m(4))
    pygame.draw.rect(big, (108, 114, 132, 230), body_r, border_radius=sc.m(3))
    pygame.draw.rect(big, (58, 62, 78, 255), body_r, width=max(1, sc.m(1)),
                     border_radius=sc.m(3))
    sh_r = pk_w // 2 - sc.m(1)
    arc = pygame.Rect(cx - sh_r, cy - pk_h // 2 - sh_r + sc.m(2), sh_r * 2, sh_r * 2)
    pygame.draw.arc(big, (28, 30, 44), arc.inflate(sc.m(2), sc.m(2)),
                    0, 3.14159, max(2, sc.m(3)))
    pygame.draw.arc(big, (108, 114, 132, 220), arc, 0, 3.14159, max(2, sc.m(2.5)))
    pygame.draw.circle(big, (52, 56, 70, 255), (cx, cy + sc.m(1)), max(2, sc.m(2.2)))


def _oval_deboss(big, ov, ovr):
    """Thin 1-px dark line just inside the top arc of the oval — the inset
    deboss that reads the oval as a recessed SLOT (content) rather than a
    raised dome (control). Clipped to the top half so only the upper arc
    carries the shadow; the bottom arc stays clean."""
    old_clip = big.get_clip()
    # clip to the top half of the oval (+ 1px overlap so the arc end blends)
    top_half = pygame.Rect(ov.x, ov.y, ov.w, ov.h // 2 + sc.m(1))
    big.set_clip(top_half)
    inner_ov = ov.inflate(-sc.m(2), -sc.m(2))
    inner_ovr = max(1, ovr - sc.m(1))
    pygame.draw.rect(big, (30, 24, 8, 120), inner_ov,
                     width=max(1, sc.m(1)), border_radius=inner_ovr)
    big.set_clip(old_clip)


def _patched_draw_confirm(self, surf):
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

    # ── wide-oval concept metrics (logical) ───────────────────────────────────
    OV_W, OV_H, OV_TOP = 140, 48, 196
    OV_RAD = OV_H // 2                      # stadium: radius = half-height
    OV_CY = OV_TOP + OV_H // 2

    BTN_TOP, BTN_BOT = 264, 298
    BTN_W, BTN_H, BTN_RAD = 80, 34, 9
    BTN_GAP = 8
    BTN_CY = (BTN_TOP + BTN_BOT) // 2       # 281
    PAIR_W = BTN_W + BTN_GAP + BTN_W
    PAIR_L = CX - PAIR_W // 2
    BUY_CX = PAIR_L + BTN_W // 2
    CAN_CX = PAIR_L + BTN_W + BTN_GAP + BTN_W // 2
    HIT_H = BTN_H

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

    # ── name ──────────────────────────────────────────────────────────────────
    sc.plain_text(big, name, sc.font(NAME_FS),
                  (m(CX), m(Y_NAME)), (250, 248, 240),
                  shadow_a=160, weight=m(0.9), keyline=(6, 6, 16), kw=m(1.0))

    # ── rarity banner ─────────────────────────────────────────────────────────
    sc._ribbon_lozenge(big, tier_word, m(CX), m(Y_BANNER), m(BANNER_W), pal)

    # ── wide matte ivory price oval ───────────────────────────────────────────
    ov = pygame.Rect(m(CX - OV_W // 2), m(OV_TOP), m(OV_W), m(OV_H))
    ovr = m(OV_RAD)
    # Drop-shadow removed — the oval reads recessed (a slot for content), not
    # raised (a button/dome). The deboss line below signals the same.
    if affordable:
        # Cooler paper-ivory face: yellow saturation pulled, blue lifted so the
        # oval doesn't share the warm-gold family with the BUY pill. Matte — no
        # top_sheen. Finish alone separates CONTENT from CONTROL.
        face = sc.vgrad_stops(ov.w, ov.h, ovr,
                              [(0.0, (228, 220, 195)), (1.0, (200, 192, 168))],
                              255, gamma=1.0)
        big.blit(face, ov.topleft)
        # 1px keyline — just heavier than a hairline, lighter than a bevel
        pygame.draw.rect(big, (120, 74, 14), ov, width=max(1, m(1)),
                         border_radius=ovr)
        _oval_deboss(big, ov, ovr)
    else:
        # Desaturated warm taupe so the plaque reads as a plaque even when
        # locked — avoids the dark-on-dark merge with the dead button pair.
        face = sc.vgrad_stops(ov.w, ov.h, ovr,
                              [(0.0, (80, 72, 54)), (1.0, (60, 54, 40))],
                              255, gamma=1.0)
        big.blit(face, ov.topleft)
        pygame.draw.rect(big, (100, 90, 65), ov, width=max(1, m(1)),
                         border_radius=ovr)
        _oval_deboss(big, ov, ovr)
    _price_in_oval(big, m(CX), m(OV_CY), price, affordable)

    # ── BUY + CANCEL — matched GLOSSY pills (full sheen + heavy bevel) ─────────
    buy_r = pygame.Rect(m(BUY_CX - BTN_W // 2), m(BTN_CY - BTN_H // 2),
                        m(BTN_W), m(BTN_H))
    can_r = pygame.Rect(m(CAN_CX - BTN_W // 2), m(BTN_CY - BTN_H // 2),
                        m(BTN_W), m(BTN_H))
    brad = m(BTN_RAD)

    if affordable:
        # BUY GLOSSY — canonical Ramp-A gold + full press sheen + heavy bevel
        big.blit(sc.gold_a_fill(buy_r.w, buy_r.h, brad), buy_r.topleft)
        sc.top_sheen(big, buy_r, brad, m(15), peak=54)
        sc.bevel_rim(big, buy_r, brad, (86, 50, 8, 230),
                     (255, 240, 190, 235), w=max(1, m(1.8)))
        sc.plain_text(big, "BUY", sc.font(13), buy_r.center, (52, 28, 4),
                      shadow_a=0, weight=m(1.0), keyline=(255, 236, 176), kw=m(0.9))
    else:
        # inert BUY — cool slate, dimmed bevel, padlock offset from centre
        sc._dark_chip_body(big, buy_r, brad,
                           [(0.0, (42, 40, 50)), (1.0, (28, 26, 36))],
                           (20, 18, 26), (78, 76, 92), gloss=10, gamma=1.04)
        sc.bevel_rim(big, buy_r, brad, (34, 32, 44, 180),
                     (86, 84, 102, 150), w=max(1, m(1.5)))
        sc.plain_text(big, "BUY", sc.font(13),
                      (buy_r.centerx - m(11), buy_r.centery), (96, 100, 116),
                      shadow_a=0, weight=m(0.5))
        _padlock(big, buy_r.centerx + m(16), buy_r.centery)

    # CANCEL — matched glossy slate pill, always available
    sc._dark_chip_body(big, can_r, brad,
                       [(0.0, (30, 28, 44)), (1.0, (20, 18, 32))],
                       (10, 9, 18), (86, 82, 104), gloss=40, gamma=1.04)
    sc.top_sheen(big, can_r, brad, m(15), peak=44)
    sc.bevel_rim(big, can_r, brad, (12, 11, 22, 220),
                 (96, 92, 116, 200), w=max(1, m(1.8)))
    sc.plain_text(big, "CANCEL", sc.font(11), can_r.center, (130, 124, 148),
                  shadow_a=0, weight=m(0.7))

    if not affordable:
        # Warmed from cool blue to muted amber — the plaque's own hue family
        sc.plain_text(big, "NOT ENOUGH", sc.font(9), (m(CX), m(308)),
                      (190, 160, 100), shadow_a=0)

    # ── overhanging disc + spotlight halo (drawn LAST) ────────────────────────
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

    self.confirm_yes_rect = pygame.Rect(
        px + BUY_CX - BTN_W // 2, py + BTN_CY - HIT_H // 2, BTN_W, HIT_H)
    self.confirm_no_rect = pygame.Rect(
        px + CAN_CX - BTN_W // 2, py + BTN_CY - HIT_H // 2, BTN_W, HIT_H)
    if not affordable:
        self.confirm_yes_rect = None


store_mod.StoreScene._draw_confirm = _patched_draw_confirm


def render_state(affordable):
    sd.load()
    sd.balance = (lambda: 999_999) if affordable else (lambda: 0)
    sc.clear_cache()
    scene = store_mod.StoreScene()
    scene.view = "category"
    scene._confirm = "skin_mummy"
    screen = pygame.Surface((W, H))
    screen.fill((6, 7, 18))
    scene.render(screen)

    POP_W, POP_H = 200, 340
    px, py = (W - POP_W) // 2, (H - POP_H) // 2
    raw = pygame.image.tostring(screen, "RGB")
    full = Image.frombytes("RGB", (W, H), raw)
    return full.crop((px, py, px + POP_W, py + POP_H))


def _pil_to_surf(img):
    return pygame.image.fromstring(img.tobytes(), img.size, img.mode)


afford_img = render_state(True)
unafford_img = render_state(False)

SHEET_W, SHEET_H = 460, 400
sheet = pygame.Surface((SHEET_W, SHEET_H))
sheet.fill((8, 8, 20))
sheet.blit(_pil_to_surf(afford_img), (0, 30))
sheet.blit(_pil_to_surf(unafford_img), (220, 30))

hdr = store_mod._font(16, True).render("wide-oval R2 · DARK-ON-IVORY OVAL · RECESSED PLAQUE",
                                       True, (220, 190, 100))
sheet.blit(hdr, hdr.get_rect(midtop=(SHEET_W // 2, 8)))

lbl_font = store_mod._font(12, True)
la = lbl_font.render("AFFORDABLE", True, (200, 185, 140))
lu = lbl_font.render("UNAFFORDABLE", True, (200, 185, 140))
sheet.blit(la, la.get_rect(midtop=(100, 378)))
sheet.blit(lu, lu.get_rect(midtop=(320, 378)))

OUT = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_confirm_popup_v3", "wide-oval", "round_2.png")
OUT = os.path.abspath(OUT)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
print("saved", OUT, sheet.get_size())
