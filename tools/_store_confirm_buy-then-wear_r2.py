#!/usr/bin/env python3
"""buy-then-wear buy-confirm action button — round 2 render.

Two-row control: a warm Skybit-house-gold pill ("BUY & EQUIP") with a stable
micro-caption directly below it in both wallet states. The caption is the
delight hook — it explains the auto-equip side effect and doubles as the state
signal when the user lacks funds. Affordable: warm gold pill, "▸ AUTO-EQUIPS"
dimmed to ~70% opacity. Unaffordable: muted pewter pill, "NOT ENOUGH" in cool
warning grey. Both states share the same caption baseline so layout never
shifts between states.

Addresses round-1 art-director notes: caption row reinstated and stabilised;
gold warmed a step toward Skybit house gold; vertical room made for the caption
by nudging pill up 5px and cancel down 4px; floating "NOT ENOUGH COINS" copy
removed (caption carries that signal instead); legibility verified via PIL
pixel sampling after render.
"""
import os
import sys
import types

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

from PIL import Image, ImageDraw, ImageFont

import game.store as store_mod
import game.store_cards as sc
import game.store_data as sd
from game.config import W, H


# The stock gloss_sweep blits pure-white (255,255,255,a) under BLEND_ADD, which
# ignores source alpha — on a saturated gold fill the additive channel forces
# all three components toward white, destroying the gradient warmth. Keep the
# sheen intensity in the RGB magnitude instead so the warm-gold pill reads gold.
def _gloss_sweep_add_safe(surf, rect, radius, peak=120):
    sweep = pygame.Surface(rect.size, pygame.SRCALPHA)
    h = max(1, rect.h)
    for y in range(h):
        v = int(peak * (1 - y / h) ** 2.4)
        if v <= 0:
            continue
        pygame.draw.line(sweep, (v, v, v, 255), (0, y), (rect.w, y))
    sm = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(sm, (255, 255, 255, 255), sm.get_rect(), border_radius=radius)
    sweep.blit(sm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(sweep, rect.topleft, special_flags=pygame.BLEND_ADD)


sc.gloss_sweep = _gloss_sweep_add_safe


# ── replacement _draw_confirm ─────────────────────────────────────────────────
# Verbatim copy of StoreScene._draw_confirm rebinding only the action-button
# block. __globals__ is rebound to store_mod.__dict__ so every module-level
# name (store_catalog / store_data / store_cards / _draw_qmark / UI_CREAM /
# NEAR_BLACK) resolves exactly as in the real render path.
def _patched_draw_confirm(self, surf) -> None:
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
    affordable = store_data.balance() >= price

    POP_W, POP_H = 200, 340
    CX = POP_W // 2
    SS = store_cards.SS
    m = store_cards.m

    CARD_X, CARD_W, CARD_TOP, CARD_H, CARD_RAD = 8, 184, 98, 230, 18
    R_HERO, DISC_CY = 41, 104
    GEM_R, GEM_CY, GEM_L_X, GEM_R_X = 11, 117, 33, 167
    NAME_FS, Y_NAME = 30, 155
    Y_BANNER, BANNER_W = 175, 120
    Y_CHIP, CHIP_H = 229, 28

    # Pill raised 5 logical px from R1 (273→268); cancel lowered 4px (308→312).
    # The recovered 9px gap holds the caption row: 10px below pill-bottom, and
    # ~4px of clear space above cancel-top at the 1x output resolution.
    Y_BTN, BTN_H, BTN_W = 268, 30, 136
    Y_CAPTION = 293    # pill-bottom = 268+15 = 283; +10 logical px = 293
    Y_CANCEL, CANCEL_H, CANCEL_W = 312, 22, 80

    big = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)

    # ── card body ─────────────────────────────────────────────────────────────
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

    # ── corner gem pair ───────────────────────────────────────────────────────
    store_cards.facet_gem(big, m(GEM_L_X), m(GEM_CY), m(GEM_R),
                          pal["gem"], pal["deep"])
    store_cards.facet_gem(big, m(GEM_R_X), m(GEM_CY), m(GEM_R),
                          pal["gem"], pal["deep"])

    # ── name (above banner) ───────────────────────────────────────────────────
    store_cards.plain_text(big, name, store_cards.font(NAME_FS),
                           (m(CX), m(Y_NAME)), (250, 248, 240),
                           shadow_a=160, weight=m(0.9),
                           keyline=(6, 6, 16), kw=m(1.0))

    # ── rarity banner ─────────────────────────────────────────────────────────
    store_cards._ribbon_lozenge(big, tier_word, m(CX), m(Y_BANNER), m(BANNER_W), pal)

    # ── price chip ────────────────────────────────────────────────────────────
    store_cards.price_chip(big, m(CX), m(Y_CHIP), f"{price:,}",
                           m(CHIP_H), affordable=affordable)

    # ── action button: buy-then-wear pill ─────────────────────────────────────
    CX_D = m(CX)
    Y_BTN_D = m(Y_BTN)
    BTN_H_D = m(BTN_H)
    BTN_W_D = m(BTN_W)
    btn_x0 = CX_D - BTN_W_D // 2
    btn_y0 = Y_BTN_D - BTN_H_D // 2
    btn_rad = BTN_H_D // 2
    pill_r = pygame.Rect(btn_x0, btn_y0, BTN_W_D, BTN_H_D)

    if affordable:
        # Three-stop warm-gold ramp. The top stop echoes CARD_RING_BRIGHT
        # (236,202,116) to tie the pill into the card's gold family; the middle
        # stop anchors the mid-tone near the target (200,175,95) so the gradient
        # doesn't slide olive through the centre; the bottom stop deepens to
        # amber to preserve the top-lit shape read.
        store_cards.chip_body_stops(big, pill_r, btn_rad,
            [(0.0, (244, 214, 126)),
             (0.40, (218, 188, 102)),
             (1.0,  (166, 134,  56))],
            (76, 52, 8), (255, 242, 168), gloss=70, gamma=1.05)
        store_cards.bevel_rim(big, pill_r, btn_rad,
                              (108, 76, 16, 222), (255, 244, 170, 200), w=2)
        store_cards.plain_text(big, "BUY & EQUIP", store_cards.font(8.5),
                               (CX_D, Y_BTN_D),
                               (30, 22, 8), shadow_a=0, weight=m(0.9),
                               tracking=m(1.2))
    else:
        # Pewter disabled state: a value/saturation fall from gold, not a hue
        # swap — colorblind-safe. The "NOT ENOUGH" caption below carries the
        # primary state signal; no other copy is needed.
        store_cards._dark_chip_body(big, pill_r, btn_rad,
                                    [(0.0, (52, 48, 58)), (1.0, (38, 34, 46))],
                                    (28, 26, 36), (80, 76, 90), gloss=10, gamma=1.04)
        store_cards.bevel_rim(big, pill_r, btn_rad,
                              (50, 46, 60, 180), (100, 96, 112, 160), w=2)
        store_cards.plain_text(big, "BUY & EQUIP", store_cards.font(8.5),
                               (CX_D, Y_BTN_D),
                               (90, 85, 100), shadow_a=0, tracking=m(1.2))

    # ── caption row — identical baseline in both states ───────────────────────
    # Drawn unconditionally after the pill so the two-row control is always
    # the same height. Only text content and colour change between states.
    Y_CAP_D = m(Y_CAPTION)
    CAP_H_D = m(20)    # generous headroom for 7px glyphs at the SS=2 device size
    if affordable:
        # Draw to a temp SRCALPHA surface so a BLEND_RGBA_MULT pass can reduce
        # all pixel alphas to ~70% uniformly — the caption reads as a secondary
        # cue, subordinate to the pill label above it.
        tmp_cap = pygame.Surface((m(POP_W), CAP_H_D), pygame.SRCALPHA)
        store_cards.plain_text(tmp_cap, "▸ AUTO-EQUIPS",
                               store_cards.font(7),
                               (m(CX), CAP_H_D // 2),
                               (230, 214, 180),
                               shadow_a=0, tracking=m(1.0), weight=0)
        # 178/255 ≈ 0.698 — pulls alpha of every text pixel to ~70%.
        tmp_cap.fill((255, 255, 255, 178), special_flags=pygame.BLEND_RGBA_MULT)
        big.blit(tmp_cap, (0, Y_CAP_D - CAP_H_D // 2))
    else:
        store_cards.plain_text(big, "NOT ENOUGH",
                               store_cards.font(7),
                               (m(CX), Y_CAP_D),
                               (150, 166, 190),
                               shadow_a=0, tracking=m(1.0), weight=0)

    # ── cancel button ─────────────────────────────────────────────────────────
    h_can = m(CANCEL_H)
    w_can = m(CANCEL_W)
    can_r = pygame.Rect(m(CX) - w_can // 2, m(Y_CANCEL) - h_can // 2,
                        w_can, h_can)
    store_cards._dark_chip_body(big, can_r, h_can // 2,
                                [(0.0, (18, 16, 26)), (1.0, (12, 10, 20))],
                                (30, 28, 42), (70, 66, 82), gloss=14, gamma=1.04)
    store_cards.plain_text(big, "CANCEL", store_cards.font(11),
                           can_r.center, (130, 124, 148), shadow_a=0)

    # ── overhanging disc + spotlight halo (crowns the card) ───────────────────
    cx_ss, cy_ss, r_ss = m(CX), m(DISC_CY), m(R_HERO)
    store_cards._alpha_aura(big, cx_ss, cy_ss, r_ss + m(55), pal["glow"],
                            peak=95, layers=24)
    store_cards._alpha_aura(big, cx_ss, cy_ss, r_ss + m(20), pal["glow"],
                            peak=70, layers=12)
    store_cards.cabochon(big, cx_ss, cy_ss, r_ss,
                         store_cards.CABO_LO, store_cards.CABO_HI,
                         ring=pal["gem"], ring_a=50)
    if secret:
        _draw_qmark(big, cx_ss, cy_ss, int(r_ss * 1.17), UI_CREAM, NEAR_BLACK,
                    thick=5)
    else:
        store_cards.blit_thumb(big, sid, cx_ss, cy_ss, int(r_ss * 1.5))
    store_cards.cabochon_glass(big, cx_ss, cy_ss, r_ss, tint=pal["gem"])

    # ── downscale and composite onto screen ───────────────────────────────────
    pop = pygame.transform.smoothscale(big, (POP_W, POP_H))
    px = (W - POP_W) // 2
    py = (H - POP_H) // 2
    self._confirm_panel = pygame.Rect(px, py, POP_W, POP_H)
    surf.blit(pop, (px, py))


store_mod.StoreScene._draw_confirm = types.FunctionType(
    _patched_draw_confirm.__code__, store_mod.__dict__, "_draw_confirm")


# ── per-state render → PIL crop ───────────────────────────────────────────────
POP_W, POP_H = 200, 340
CROP_X, CROP_Y = (W - POP_W) // 2, (H - POP_H) // 2


def render_state(balance_val):
    sd.load()
    sd.balance = lambda: balance_val
    sc._card_cache.clear()
    scene = store_mod.StoreScene()
    scene.view = "category"
    scene._confirm = "skin_mummy"
    screen = pygame.Surface((W, H))
    scene.render(screen)
    raw = pygame.image.tostring(screen, "RGB")
    img = Image.frombytes("RGB", (W, H), raw)
    return img.crop((CROP_X, CROP_Y, CROP_X + POP_W, CROP_Y + POP_H))


afford = render_state(999_999)
locked = render_state(0)


# ── legibility probe via PIL pixel sampling ───────────────────────────────────
# Caption centre lands at (CX=100, Y_CAPTION=293) in the 1x 200×340 popup.
# Sampling at the caption Y against a background-only pixel on the same row but
# far left (x=10, clear of all text) proves the glyphs are distinct from the
# dark card body at 1× output resolution.
Y_CAPTION = 293
cap_a = afford.getpixel((100, Y_CAPTION))
bg_a  = afford.getpixel((10,  Y_CAPTION))   # same Y, no text here
cap_l = locked.getpixel((100, Y_CAPTION))
bg_l  = locked.getpixel((10,  Y_CAPTION))
delta_a = sum(abs(cap_a[i] - bg_a[i]) for i in range(3))
delta_l = sum(abs(cap_l[i] - bg_l[i]) for i in range(3))
print(f"legibility check — affordable:   caption={cap_a}  bg={bg_a}  ΔRgb={delta_a}")
print(f"legibility check — unaffordable: caption={cap_l}  bg={bg_l}  ΔRgb={delta_l}")
print("caption font: 7 logical px (14 device px at SS=2, downscaled to ~7px at 1x)")
if delta_a >= 30 and delta_l >= 30:
    print("PASS — both captions clearly distinct from card background (ΔRgb ≥ 30).")
else:
    print("WARN — low contrast; consider bumping font to 8px.")


# ── compose review sheet ──────────────────────────────────────────────────────
CANVAS_W, CANVAS_H = 460, 400
canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), (8, 8, 20))
canvas.paste(afford, (0, 30))
canvas.paste(locked, (220, 30))

draw = ImageDraw.Draw(canvas)
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
try:
    f_hdr = ImageFont.truetype(FONT_PATH, 11)
    f_lab = ImageFont.truetype(FONT_PATH, 13)
    f_ann = ImageFont.truetype(FONT_PATH, 9)
except Exception:
    f_hdr = f_lab = f_ann = ImageFont.load_default()


def _ctext(x, y, txt, fnt, col):
    w = draw.textlength(txt, font=fnt)
    draw.text((x - w / 2, y), txt, font=fnt, fill=col)


_ctext(CANVAS_W // 2, 8,
       "buy-then-wear  ·  BUY & EQUIP PILL  ·  round 2",
       f_hdr, (220, 190, 100))

# Annotate caption position on each side
_ctext(110, 378, "AFFORDABLE", f_lab, (200, 185, 140))
_ctext(330, 378, "NOT ENOUGH", f_lab, (200, 185, 140))

# Light annotation lines pointing at the caption strip
ann_y = 30 + Y_CAPTION        # caption y in canvas coords (left panel)
draw.line([(0, ann_y), (4, ann_y)], fill=(80, 80, 100), width=1)
draw.line([(220, ann_y), (224, ann_y)], fill=(80, 80, 100), width=1)
draw.line([(440, ann_y), (444, ann_y)], fill=(80, 80, 100), width=1)
_ctext(448, ann_y - 4, "caption", f_ann, (80, 80, 100))

OUT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..",
    "docs", "store_confirm_popup", "buy-then-wear", "round_2.png"))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
canvas.save(OUT)
print("saved", OUT, canvas.size)
