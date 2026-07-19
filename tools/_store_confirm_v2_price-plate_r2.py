#!/usr/bin/env python3
"""
price-plate  ·  store buy-confirmation popup v2  ·  round 2

Concept: horizontal embossed enamel plaque with coin+numeral, flanked by
BUY + CANCEL side-by-side below.

R2 changes (art-director punch list):
  - Plaque face raised to mid-tone warm enamel (~110,88,44)→(74,58,26) so
    the plate reads as a distinct object off the card body.
  - Plaque is MATTE (top_sheen peak 18) vs BUY GLOSSY (full sheen, bevel) —
    content vs control is unambiguous by finish alone.
  - Knurl simplified to 4 bolder ridges at wider light/dark spread; bands
    are legible against the lifted face.
  - Inner bevel highlight pushed to (255,236,178) full-width with a matching
    dark inner line — emboss reads as crisp raised edge.
  - Padlock enlarged ~25% and given a 1px dark keyline so it reads as a
    recognisable lock silhouette at 1× screen size.
  - BUY top stop nudged up ~8% toward (110,84,34) so it remains the single
    brightest actionable element after the plate lift.
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


def _knurl(surf, rect, light, dark):
    """4 bolder ridges at ~2 px logical pitch across the two short end-caps.
    Wider light/dark spread reads legibly against the lifted enamel face."""
    strip_w = sc.m(5)
    n = 4
    step = sc.m(2.2)
    y0 = rect.centery - int((n * step) // 2)
    lw = max(2, sc.m(1.0))          # bolder strokes than R1's 0.6px
    for left_cap in (True, False):
        x0 = rect.x + sc.m(3) if left_cap else rect.right - sc.m(3) - strip_w
        for i in range(n):
            yy = int(y0 + i * step)
            col = light if i % 2 == 0 else dark
            pygame.draw.line(surf, col, (x0, yy), (x0 + strip_w, yy), lw)


def _inner_bevel(surf, rect, radius, highlight, shadow):
    """Crisp embossed inner edge: a full-width bright top line + a matching
    dark line just below it so the plate reads as a raised object, not a slot.
    Drawn after the face fill and before knurl + price content."""
    w = max(1, sc.m(1.4))
    inset = sc.m(1)
    # bright highlight hugging the top inner edge
    hl = pygame.Surface(rect.size, pygame.SRCALPHA)
    hl_rect = pygame.Rect(0, 0, rect.w, rect.h)
    pygame.draw.rect(hl, (*highlight, 230), hl_rect, width=w, border_radius=radius)
    # fade it so only the top arc contributes strongly
    grad = pygame.Surface(rect.size, pygame.SRCALPHA)
    for y in range(rect.h):
        a = int(255 * (1 - y / max(1, rect.h)) ** 1.2)
        pygame.draw.line(grad, (255, 255, 255, a), (0, y), (rect.w - 1, y))
    hl.blit(grad, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(hl, rect.topleft)
    # dark inner line just below the bright highlight — the shadow side of the bevel
    dk_r = pygame.Rect(rect.x + inset, rect.y + w, rect.w - inset * 2, rect.h - w * 2)
    dk = pygame.Surface(dk_r.size, pygame.SRCALPHA)
    pygame.draw.rect(dk, (*shadow, 160),
                     dk.get_rect(), width=w,
                     border_radius=max(1, radius - w))
    dk_grad = pygame.Surface(dk_r.size, pygame.SRCALPHA)
    for y in range(dk_r.h):
        # dark line only visible at top — fades to nothing at bottom
        a = int(200 * (1 - y / max(1, dk_r.h)) ** 2.0)
        pygame.draw.line(dk_grad, (255, 255, 255, a), (0, y), (dk_r.w - 1, y))
    dk.blit(dk_grad, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(dk, dk_r.topleft)


def _price_in_plate(big, cx_d, cy_d, price, affordable):
    """Coin glyph + numeral centred together on the plate baseline."""
    txt = f"{price:,}"
    coin_r = sc.m(8)
    coin_d = coin_r * 2
    gap = sc.m(4)
    num_font = sc.font(16)
    num_w = num_font.render(txt, True, (255, 255, 255)).get_width()
    total = coin_d + gap + num_w
    left = cx_d - total // 2
    coin_cx = left + coin_r
    num_cx = left + coin_d + gap + num_w // 2

    if affordable:
        sc.coin_glyph(big, coin_cx, cy_d, coin_r)
        sc.plain_text(big, txt, num_font, (num_cx, cy_d), (248, 238, 210),
                      shadow_a=150, weight=sc.m(0.9),
                      keyline=(38, 28, 8), kw=sc.m(1.0))
    else:
        pygame.draw.circle(big, (150, 152, 162), (coin_cx, cy_d), coin_r)
        pygame.draw.circle(big, (96, 100, 114), (coin_cx, cy_d), coin_r,
                           width=max(1, sc.m(1)))
        pygame.draw.circle(big, (122, 126, 140), (coin_cx, cy_d),
                           coin_r - sc.m(2), width=max(1, sc.m(1)))
        sc.plain_text(big, txt, num_font, (num_cx, cy_d), (110, 115, 130),
                      shadow_a=0, weight=sc.m(0.6),
                      keyline=(22, 22, 30), kw=sc.m(0.9))


def _padlock(big, cx, cy):
    """Padlock ~25% larger than R1 with a 1px dark keyline so the silhouette
    reads unambiguously as a lock at 1× screen size."""
    pk_w, pk_h = sc.m(17), sc.m(14)   # ~30% wider/taller than R1's 13/11
    body_r = pygame.Rect(cx - pk_w // 2, cy - pk_h // 2 + sc.m(2),
                         pk_w, pk_h - sc.m(3))
    # 1px dark keyline drawn first so body sits inside a defined edge
    pygame.draw.rect(big, (28, 30, 44), body_r.inflate(sc.m(2), sc.m(2)),
                     border_radius=sc.m(4))
    pygame.draw.rect(big, (108, 114, 132, 230), body_r, border_radius=sc.m(3))
    pygame.draw.rect(big, (58, 62, 78, 255), body_r, width=max(1, sc.m(1)),
                     border_radius=sc.m(3))
    sh_r = pk_w // 2 - sc.m(1)
    arc = pygame.Rect(cx - sh_r, cy - pk_h // 2 - sh_r + sc.m(2), sh_r * 2, sh_r * 2)
    # keyline arc behind the shackle
    pygame.draw.arc(big, (28, 30, 44), arc.inflate(sc.m(2), sc.m(2)),
                    0, 3.14159, max(2, sc.m(3)))
    pygame.draw.arc(big, (108, 114, 132, 220), arc, 0, 3.14159, max(2, sc.m(2.5)))
    pygame.draw.circle(big, (52, 56, 70, 255), (cx, cy + sc.m(1)), max(2, sc.m(2.2)))


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

    # ── price-plate concept metrics (logical) ─────────────────────────────────
    PL_TOP, PL_W, PL_H, PL_RAD = 215, 120, 34, 7
    PL_CY = PL_TOP + PL_H // 2
    Y_ACT = 278
    BUY_W, BUY_H = 88, 30
    CAN_W, CAN_H = 64, 30
    PAIR_GAP = 8
    HIT_H = 32
    PAIR_W = BUY_W + PAIR_GAP + CAN_W
    PAIR_L = CX - PAIR_W // 2
    BUY_CX = PAIR_L + BUY_W // 2
    CAN_CX = PAIR_L + BUY_W + PAIR_GAP + CAN_W // 2

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

    # ── enamel price plaque ───────────────────────────────────────────────────
    pl = pygame.Rect(m(CX - PL_W // 2), m(PL_TOP), m(PL_W), m(PL_H))
    plr = m(PL_RAD)
    sc.drop_shadow(big, pl, plr, blur=m(4), alpha=120, dy=m(2))
    if affordable:
        # MATTE warm enamel — raised mid-tone so it clearly separates from the
        # card body, but shallow sheen so it reads as content, not a button.
        face = sc.vgrad_stops(pl.w, pl.h, plr,
                              [(0.0, (110, 88, 44)), (0.5, (92, 72, 34)),
                               (1.0, (74, 58, 26))], 255, gamma=1.05)
        big.blit(face, pl.topleft)
        # matte peak=18 (vs BUY gloss which stays at full sheen) — finish
        # difference signals content vs control
        sc.top_sheen(big, pl, plr, m(14), peak=18)
        _knurl(big, pl, (150, 128, 80), (46, 34, 12))
        # crisp inner bevel: bright highlight + dark sub-line for raised-edge read
        _inner_bevel(big, pl, plr, (255, 236, 178), (22, 16, 6))
        pygame.draw.rect(big, (14, 11, 4), pl, width=max(1, m(1)), border_radius=plr)
        sc.bevel_rim(big, pl, plr, (78, 52, 12, 210),
                     (255, 236, 178, 230), w=max(1, m(1.4)))
    else:
        # tarnished cool-grey plaque — same matte finish, no warmth
        face = sc.vgrad_stops(pl.w, pl.h, plr,
                              [(0.0, (52, 52, 64)), (1.0, (34, 34, 46))],
                              255, gamma=1.02)
        big.blit(face, pl.topleft)
        sc.top_sheen(big, pl, plr, m(14), peak=14)
        _knurl(big, pl, (82, 82, 96), (26, 26, 36))
        _inner_bevel(big, pl, plr, (160, 162, 178), (14, 14, 22))
        pygame.draw.rect(big, (14, 14, 20), pl, width=max(1, m(1)), border_radius=plr)
        sc.bevel_rim(big, pl, plr, (52, 54, 68, 200),
                     (150, 154, 172, 200), w=max(1, m(1.4)))
    _price_in_plate(big, m(CX), m(PL_CY), price, affordable)

    # ── BUY + CANCEL action pair ──────────────────────────────────────────────
    buy_r = pygame.Rect(m(BUY_CX - BUY_W // 2), m(Y_ACT - BUY_H // 2),
                        m(BUY_W), m(BUY_H))
    can_r = pygame.Rect(m(CAN_CX - CAN_W // 2), m(Y_ACT - CAN_H // 2),
                        m(CAN_W), m(CAN_H))
    brad = m(8)

    if affordable:
        # BUY GLOSSY — top stop nudged ~8% brighter so BUY remains the single
        # brightest actionable element now that the plate is lifted
        sc._dark_chip_body(big, buy_r, brad,
                           [(0.0, (110, 84, 34)), (1.0, (60, 44, 14))],
                           (36, 26, 8), (255, 226, 150), gloss=54, gamma=1.06)
        sc.top_sheen(big, buy_r, brad, m(13), peak=54)
        sc.bevel_rim(big, buy_r, brad, (40, 28, 8, 220),
                     (255, 232, 162, 220), w=max(1, m(1.5)))
        sc.plain_text(big, "BUY", sc.font(13), buy_r.center, (252, 244, 224),
                      shadow_a=130, weight=m(0.9), keyline=(40, 26, 6), kw=m(0.9))
    else:
        sc._dark_chip_body(big, buy_r, brad,
                           [(0.0, (42, 40, 50)), (1.0, (28, 26, 36))],
                           (20, 18, 26), (78, 76, 92), gloss=10, gamma=1.04)
        sc.bevel_rim(big, buy_r, brad, (34, 32, 44, 180),
                     (86, 84, 102, 150), w=max(1, m(1.4)))
        sc.plain_text(big, "BUY", sc.font(13),
                      (buy_r.centerx - m(9), buy_r.centery), (96, 100, 116),
                      shadow_a=0, weight=m(0.5))
        _padlock(big, buy_r.centerx + m(15), buy_r.centery)

    # CANCEL — flat dark chip, always available
    sc._dark_chip_body(big, can_r, brad,
                       [(0.0, (18, 16, 26)), (1.0, (12, 10, 20))],
                       (30, 28, 42), (70, 66, 82), gloss=14, gamma=1.04)
    sc.plain_text(big, "CANCEL", sc.font(11), can_r.center, (150, 144, 166),
                  shadow_a=0, weight=m(0.6))

    if not affordable:
        sc.plain_text(big, "NOT ENOUGH", sc.font(8), (m(CX), m(302)),
                      (150, 166, 190), shadow_a=0)

    # ── overhanging disc + spotlight halo ─────────────────────────────────────
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
        px + BUY_CX - BUY_W // 2, py + Y_ACT - HIT_H // 2, BUY_W, HIT_H)
    self.confirm_no_rect = pygame.Rect(
        px + CAN_CX - CAN_W // 2, py + Y_ACT - HIT_H // 2, CAN_W, HIT_H)
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
    # non-SRCALPHA surface: read as RGB to avoid garbage alpha channel
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

hdr = store_mod._font(16, True).render("price-plate R2 · MATTE PLAQUE + GLOSSY BUY",
                                       True, (220, 190, 100))
sheet.blit(hdr, hdr.get_rect(midtop=(SHEET_W // 2, 8)))

lbl_font = store_mod._font(12, True)
la = lbl_font.render("AFFORDABLE", True, (200, 185, 140))
lu = lbl_font.render("UNAFFORDABLE", True, (200, 185, 140))
sheet.blit(la, la.get_rect(midtop=(100, 378)))
sheet.blit(lu, lu.get_rect(midtop=(320, 378)))

OUT = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_confirm_popup_v2", "price-plate", "round_2.png")
OUT = os.path.abspath(OUT)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
print("saved", OUT, sheet.get_size())
