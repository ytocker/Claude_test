"""
Headless render harness for the COIN STORE redesign exploration.

Renders ONE combined review sheet (docs/store_redesign/round_1.png) holding
five DISTINCT full-screen store directions plus a detail-callout strip so the
art-director can judge the small stuff at scale.

Each direction is a complete 360x640 store mockup built from REAL catalog
items, REAL procedural thumbnails (parrot.get_skin_icon / get_skin_frame), the
real rarity ladder, equipped/secret states, tabs, page controls and BACK. The
directions are written as self-contained draw functions that share a small set
of premium primitives (gem badges, foil glow, brushed panels, bevels) so the
explorations differ in APPROACH rather than colour.

Run:  python docs/store_redesign/render.py
"""
from __future__ import annotations

import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

# Repo root on sys.path so `import game...` resolves when run from anywhere.
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import pygame  # noqa: E402

pygame.init()
pygame.font.init()

from game.config import W, H  # noqa: E402
from game.draw import (  # noqa: E402
    rounded_rect, lerp_color, UI_CREAM, NEAR_BLACK, WHITE,
)
from game.hud import (  # noqa: E402
    _font, _coin_icon, _draw_overlay_stars,
    _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP, _RED_OUTLINE, _ORANGE_BORDER,
)
from game.powerup_help import _seeded_stars  # noqa: E402
from game import parrot, store_catalog, store_data  # noqa: E402
from game.surprise_box_variants import _draw_qmark  # noqa: E402

store_data.load()

# ── shared palette ───────────────────────────────────────────────────────────
# Tropical night-sky family, but each direction picks its own gradient stops so
# the palette richness differs. These rarity tints reuse the established casual-
# game language (white/blue/purple/orange) re-warmed toward Skybit's gold world.
RARITY = {
    "common":    {"gem": (188, 196, 210), "glow": (150, 160, 180),
                  "deep": (70, 76, 92)},
    "rare":      {"gem": (96, 174, 255),  "glow": (70, 150, 255),
                  "deep": (28, 60, 120)},
    "epic":      {"gem": (196, 120, 248), "glow": (180, 96, 244),
                  "deep": (70, 32, 110)},
    "legendary": {"gem": (255, 178, 70),  "glow": (255, 150, 40),
                  "deep": (120, 64, 12)},
}

_TABS = ("COSTUMES", "PARROTS", "ANIMALS", "SHOES", "HATS", "SHADES", "PARCELS")
_GROUPS = ("costume", "parrot", "animal", "shoes", "hats", "shades", "parcels")

_STARS = _seeded_stars()


# ── thumbnail cache (cropped-to-content, fit to a box) ───────────────────────
_thumb_cache: dict = {}


def _fit_skin(sid: str, box: int) -> pygame.Surface:
    key = (sid, box)
    cached = _thumb_cache.get(key)
    if cached is not None:
        return cached
    src = parrot.get_skin_icon(sid) or parrot.get_skin_frame(sid, 1, 0.0)
    bb = src.get_bounding_rect()
    if bb.width > 0 and bb.height > 0:
        src = src.subsurface(bb).copy()
    sw, sh = src.get_size()
    scale = box / max(sw, sh)
    out = pygame.transform.smoothscale(
        src, (max(1, int(sw * scale)), max(1, int(sh * scale))))
    _thumb_cache[key] = out
    return out


def _disp_name(sid: str) -> str:
    if sid in (store_catalog.BASE_SKIN, store_catalog.PARCEL_BASE):
        return "DEFAULT"
    return store_catalog.name(sid)


# ── premium primitives (shared, procedural, pygame-only) ─────────────────────

def _soft_glow(surf, cx, cy, radius, color, peak_alpha, layers=6):
    """Soft radial bloom — the workhorse for rarity halos and modal auras.
    Layered translucent circles (cheap, no per-pixel work) so an epic/legendary
    card visibly emits light, not just a hard outline."""
    for i in range(layers, 0, -1):
        r = int(radius * i / layers)
        a = int(peak_alpha * (1 - (i - 1) / layers) ** 1.7)
        if r <= 0 or a <= 0:
            continue
        g = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(g, (*color, a), (r + 1, r + 1), r)
        surf.blit(g, (cx - r - 1, cy - r - 1), special_flags=pygame.BLEND_ADD)


def _vgrad_panel(w, h, radius, top, bot, alpha=255):
    """A rounded vertical-gradient panel surface (top brighter), corner-masked.
    The base body for every card so panels read as gently lit rather than flat
    fills. Returned as its own SRCALPHA surface to blit where needed."""
    body = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        c = lerp_color(top, bot, y / max(1, h - 1))
        pygame.draw.line(body, (*c, alpha), (0, y), (w - 1, y))
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h),
                     border_radius=radius)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return body


def _drop_shadow(surf, rect, radius, blur=6, alpha=120, dy=4):
    """A soft drop shadow under a card — concentric expanding rounded rects at
    falling alpha give the depth that the flat translucent panels lack."""
    for i in range(blur, 0, -1):
        a = int(alpha * (i / blur) ** 2 / blur * 2.2)
        if a <= 0:
            continue
        r = pygame.Rect(rect.x - i, rect.y - i + dy,
                        rect.w + 2 * i, rect.h + 2 * i)
        s = pygame.Surface(r.size, pygame.SRCALPHA)
        pygame.draw.rect(s, (0, 0, 0, a), s.get_rect(),
                         border_radius=radius + i)
        surf.blit(s, r.topleft)


def _inner_bevel(surf, rect, radius, hi_a=90, lo_a=110):
    """Top-left pale highlight + bottom-right black accent, 1px inboard, split
    by a diagonal mask so the stroke follows the corner radius. Sells the raise
    of the panel as if lit from the top-left."""
    w, h = rect.size
    band = (2, 2, w - 4, h - 4)
    brad = max(1, radius - 2)

    def _half(color, a, top_left):
        layer = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(layer, (*color, a), band, width=1, border_radius=brad)
        mask = pygame.Surface((w, h), pygame.SRCALPHA)
        tri = ([(0, 0), (w, 0), (0, h)] if top_left
               else [(w, 0), (w, h), (0, h)])
        pygame.draw.polygon(mask, (255, 255, 255, 255), tri)
        layer.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        surf.blit(layer, rect.topleft)

    _half(_GOLD_PALE, hi_a, True)
    _half((0, 0, 0), lo_a, False)


def _gem(surf, cx, cy, r, tier, t=0.0):
    """A faceted rarity gem badge — a diamond cut with a bright top-left facet,
    a dark bottom-right facet, a white specular pip, and a tier glow. This is
    the premium rarity language: a real little jewel, not a 2px outline."""
    pal = RARITY[tier]
    base, glow = pal["gem"], pal["glow"]
    deep = pal["deep"]
    _soft_glow(surf, cx, cy, r * 2.4, glow,
               int(120 + 60 * (0.5 + 0.5 * math.sin(t * 3))), layers=5)
    top = (cx, cy - r)
    bot = (cx, cy + r)
    left = (cx - r, cy)
    right = (cx + r, cy)
    # Two halves: upper-left lit, lower-right shaded.
    pygame.draw.polygon(surf, lerp_color(base, WHITE, 0.35),
                        [top, left, (cx, cy)])
    pygame.draw.polygon(surf, base, [top, right, (cx, cy)])
    pygame.draw.polygon(surf, lerp_color(base, deep, 0.45),
                        [left, bot, (cx, cy)])
    pygame.draw.polygon(surf, lerp_color(base, deep, 0.7),
                        [right, bot, (cx, cy)])
    pygame.draw.polygon(surf, lerp_color(deep, NEAR_BLACK, 0.4),
                        [top, right, bot, left], width=1)
    # Specular pip.
    pip = pygame.Surface((4, 4), pygame.SRCALPHA)
    pygame.draw.circle(pip, (255, 255, 255, 230), (2, 2), 1)
    surf.blit(pip, (cx - 2 - r // 3, cy - 2 - r // 3))


def _coin_chip(surf, cx, cy, text, fg, bg, coin=True, glow=None, h=24):
    """A price / EQUIP / EQUIPPED chip with optional coin, hairline gold rim,
    and an optional under-glow. Pill-shaped, padded, centred on (cx, cy)."""
    f = _font(13, True)
    timg = f.render(text, True, fg)
    coin_d = 15
    cgap = 4 if coin else 0
    inner = (coin_d + cgap if coin else 0) + timg.get_width()
    pad = 11
    w = inner + pad * 2
    chip = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    if glow is not None:
        _soft_glow(surf, cx, cy, w // 2 + 2, glow, 46, layers=4)
    body = _vgrad_panel(w, h, h // 2,
                        lerp_color(bg, WHITE, 0.18), bg)
    surf.blit(body, chip.topleft)
    pygame.draw.rect(surf, (*_GOLD_BRIGHT, 120), chip, width=1,
                     border_radius=h // 2)
    x = chip.x + pad
    if coin:
        _coin_icon(surf, x + coin_d // 2, cy, coin_d // 2)
        x += coin_d + cgap
    surf.blit(timg, timg.get_rect(midleft=(x, cy)))
    return chip


def _gradient_text(surf, txt, font_obj, center, top, bot, outline=None,
                   shadow=True):
    """Vertical gradient-filled text with optional outline + shadow — for
    headers and prominent labels. Built by masking a gradient with the glyph
    alpha so it stays crisp."""
    base = font_obj.render(txt, True, WHITE)
    w, h = base.get_size()
    grad = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        c = lerp_color(top, bot, y / max(1, h - 1))
        pygame.draw.line(grad, c, (0, y), (w, y))
    grad.blit(base, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    r = base.get_rect(center=center)
    if outline:
        out = font_obj.render(txt, True, outline)
        for ox, oy in ((-1, 0), (1, 0), (0, -1), (0, 1),
                       (-1, -1), (1, -1), (-1, 1), (1, 1)):
            surf.blit(out, (r.x + ox, r.y + oy))
    if shadow:
        sh = font_obj.render(txt, True, NEAR_BLACK)
        sh.set_alpha(150)
        surf.blit(sh, (r.x + 1, r.y + 2))
    surf.blit(grad, r.topleft)
    return r


# ── per-direction backgrounds ────────────────────────────────────────────────

def _bg(surf, stops, t=2.0, stars=True):
    h = surf.get_height()
    n = len(stops)
    for y in range(h):
        f = y / max(1, h - 1)
        seg = min(n - 2, int(f * (n - 1)))
        local = (f * (n - 1)) - seg
        c = lerp_color(stops[seg], stops[seg + 1], local)
        pygame.draw.line(surf, c, (0, y), (surf.get_width() - 1, y))
    if stars:
        _draw_overlay_stars(surf, _STARS, t)


# Sample item ids per direction so cards show real variety incl. rarity tiers,
# an equipped card and a secret. Each entry: (sid, force_equipped, force_secret)
def _sample_cards():
    ani = store_catalog.ids_of_group("animal")
    cos = store_catalog.ids_of_group("costume")
    # cheapest-first so rarity tiers spread nicely.
    cos = sorted(cos, key=store_catalog.cost)
    ani = sorted(ani, key=store_catalog.cost)
    return [
        (cos[0], True, False),    # common, equipped (gold)
        (cos[3], False, False),   # common
        (ani[0], False, False),   # rare
        (ani[8], False, False),   # epic
        (ani[14], False, False),  # legendary-ish
        (cos[10], False, False),  # epic/legendary
        ("skin_ufo", False, True),       # secret (masked)
        ("skin_jet_fighter", False, True),  # secret (masked)
    ]


# Layout metrics shared across directions (a 2x4 grid).
_CARD_W = 162
_CARD_H = 100
_GAP = 8
_GRID_TOP = 118


def _grid_rects():
    base_x = (W - (_CARD_W * 2 + _GAP)) // 2
    rects = []
    for idx in range(8):
        col, row = idx % 2, idx // 2
        x = base_x + col * (_CARD_W + _GAP)
        y = _GRID_TOP + row * (_CARD_H + _GAP)
        rects.append(pygame.Rect(x, y, _CARD_W, _CARD_H))
    return base_x, rects


# ═══════════════════════════════════════════════════════════════════════════
# DIRECTION 1 — "GEM VITRINE"
# Museum-vitrine treatment: each card is a glass display case with a faceted
# rarity gem badge in the top-right corner, a soft per-rarity floor-glow under
# the thumbnail (a lit pedestal), and brushed-gold framing. Rich indigo sky.
# ═══════════════════════════════════════════════════════════════════════════

def dir_gem_vitrine(surf, t=2.0):
    _bg(surf, [(10, 6, 38), (20, 12, 58), (34, 20, 78), (44, 26, 96)], t)
    _header_classic(surf, "STORE", t, accent_top=(255, 232, 150),
                    accent_bot=(232, 150, 40))
    _tabstrip_pill(surf, active=2, t=t)
    base_x, rects = _grid_rects()
    for (sid, eq, sec), rect in zip(_sample_cards(), rects):
        _card_gem_vitrine(surf, sid, rect, eq, sec, t)
    _page_controls(surf, base_x, 1, 3)
    _back_pill(surf)


def _card_gem_vitrine(surf, sid, rect, equipped, secret, t):
    tier = store_catalog.rarity(sid)
    pal = RARITY[tier]
    _drop_shadow(surf, rect, 14, blur=5, alpha=110)
    body = _vgrad_panel(rect.w, rect.h, 14, (30, 22, 56), (14, 9, 34), alpha=236)
    surf.blit(body, rect.topleft)
    # Pedestal floor-glow under the thumbnail, tinted by rarity. Held modest so
    # it lights the pedestal without washing the thumbnail or the name beneath.
    _soft_glow(surf, rect.centerx, rect.y + 30, 30, pal["glow"],
               62 if tier in ("epic", "legendary") else 38, layers=5)
    rim_col = _GOLD_BRIGHT if equipped else pal["gem"]
    # Two-ply metallic rim.
    pygame.draw.rect(surf, lerp_color(rim_col, NEAR_BLACK, 0.45), rect,
                     width=2, border_radius=14)
    pygame.draw.rect(surf, rim_col, rect.inflate(-2, -2), width=1,
                     border_radius=13)
    _inner_bevel(surf, rect, 14, hi_a=70, lo_a=95)
    # Glass sheen across the top.
    sheen = pygame.Surface((rect.w - 6, 22), pygame.SRCALPHA)
    for y in range(22):
        a = int(40 * (1 - y / 22))
        pygame.draw.line(sheen, (255, 255, 255, a), (0, y), (rect.w - 6, y))
    surf.blit(sheen, (rect.x + 3, rect.y + 3))

    if secret:
        _draw_qmark(surf, rect.centerx, rect.y + 30, 38, UI_CREAM, NEAR_BLACK,
                    thick=2)
        name = "???"
    else:
        th = _fit_skin(sid, 46)
        surf.blit(th, th.get_rect(center=(rect.centerx, rect.y + 32)))
        name = _disp_name(sid)
    # Faceted gem badge, top-right.
    _gem(surf, rect.right - 16, rect.y + 16, 8, tier, t)
    nr = _font(13, True).render(name, True, _GOLD_PALE).get_rect(
        center=(rect.centerx, rect.y + 60))
    nsh = _font(13, True).render(name, True, NEAR_BLACK)
    nsh.set_alpha(160)
    surf.blit(nsh, (nr.x + 1, nr.y + 1))
    surf.blit(_font(13, True).render(name, True, _GOLD_PALE), nr)
    _state_chip(surf, sid, rect.centerx, rect.y + 82, equipped, secret)


# ═══════════════════════════════════════════════════════════════════════════
# DIRECTION 2 — "FOIL CARDS"
# Trading-card treatment: tall-feeling cards with a colour-banner header strip
# per rarity (the gem language as a full ribbon), a holographic diagonal foil
# sweep on epic/legendary, and a clean product-shot thumbnail on a lighter
# inset. Warm teal-to-plum sky. Typography sits on the banner.
# ═══════════════════════════════════════════════════════════════════════════

def dir_foil_cards(surf, t=2.0):
    _bg(surf, [(8, 10, 40), (16, 22, 64), (40, 28, 78), (58, 34, 84)], t)
    _header_classic(surf, "STORE", t, accent_top=(255, 224, 160),
                    accent_bot=(255, 130, 90))
    _tabstrip_underline(surf, active=2, t=t)
    base_x, rects = _grid_rects()
    for (sid, eq, sec), rect in zip(_sample_cards(), rects):
        _card_foil(surf, sid, rect, eq, sec, t)
    _page_controls(surf, base_x, 1, 3)
    _back_pill(surf)


def _card_foil(surf, sid, rect, equipped, secret, t):
    tier = store_catalog.rarity(sid)
    pal = RARITY[tier]
    _drop_shadow(surf, rect, 13, blur=5, alpha=110)
    body = _vgrad_panel(rect.w, rect.h, 13, (38, 30, 60), (18, 12, 38),
                        alpha=240)
    surf.blit(body, rect.topleft)
    # Holographic diagonal foil sweep on the premium tiers.
    if tier in ("epic", "legendary"):
        foil = pygame.Surface(rect.size, pygame.SRCALPHA)
        for i in range(-rect.h, rect.w, 10):
            phase = (i / 40.0 + t) % 3.0
            a = int(34 * max(0.0, math.sin(phase * 2.1)))
            col = lerp_color(pal["glow"], (255, 255, 255), 0.4)
            pygame.draw.line(foil, (*col, a), (i, 0), (i + rect.h, rect.h), 6)
        mask = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(),
                         border_radius=13)
        foil.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        surf.blit(foil, rect.topleft, special_flags=pygame.BLEND_ADD)
    # Rarity banner header strip with the item name on it.
    banner_h = 20
    banner = _vgrad_panel(rect.w - 6, banner_h, 9,
                          lerp_color(pal["gem"], WHITE, 0.2),
                          pal["deep"], alpha=255)
    surf.blit(banner, (rect.x + 3, rect.y + 4))
    name = "???" if secret else _disp_name(sid)
    fg = NEAR_BLACK if tier in ("common", "legendary") else WHITE
    nimg = _font(12, True).render(name, True, fg)
    surf.blit(nimg, nimg.get_rect(center=(rect.centerx, rect.y + 14)))
    # Inset product-shot panel.
    inset = pygame.Rect(rect.x + 10, rect.y + 30, rect.w - 20, 38)
    rounded_rect(surf, inset, 8, (10, 7, 26), alpha=200)
    pygame.draw.rect(surf, (*pal["gem"], 120), inset, width=1, border_radius=8)
    if secret:
        _draw_qmark(surf, rect.centerx, rect.y + 49, 30, UI_CREAM, NEAR_BLACK,
                    thick=2)
    else:
        th = _fit_skin(sid, 36)
        surf.blit(th, th.get_rect(center=(rect.centerx, rect.y + 49)))
    rim_col = _GOLD_BRIGHT if equipped else pal["gem"]
    pygame.draw.rect(surf, rim_col, rect, width=2, border_radius=13)
    _state_chip(surf, sid, rect.centerx, rect.y + 84, equipped, secret)


# ═══════════════════════════════════════════════════════════════════════════
# DIRECTION 3 — "TROPICAL TICKET"
# Warm, playful arcade-ticket treatment: cream/sand cards (a daytime tropical
# break from the dark family) with a notched ticket edge, a chunky rarity tab
# corner-fold, leafy gold corner flourishes, and bold dark type. The most
# distinctly Skybit-tropical, casual + collectible. Sunset-band sky.
# ═══════════════════════════════════════════════════════════════════════════

_SAND_TOP = (250, 238, 212)
_SAND_BOT = (228, 206, 168)
_INK = (60, 36, 24)


def dir_tropical_ticket(surf, t=2.0):
    _bg(surf, [(18, 14, 52), (44, 26, 76), (96, 46, 78), (150, 78, 70)], t)
    _header_banner(surf, "STORE", t)
    _tabstrip_ticket(surf, active=2, t=t)
    base_x, rects = _grid_rects()
    for (sid, eq, sec), rect in zip(_sample_cards(), rects):
        _card_ticket(surf, sid, rect, eq, sec, t)
    _page_controls(surf, base_x, 1, 3)
    _back_pill(surf)


def _card_ticket(surf, sid, rect, equipped, secret, t):
    tier = store_catalog.rarity(sid)
    pal = RARITY[tier]
    _drop_shadow(surf, rect, 12, blur=5, alpha=130)
    body = _vgrad_panel(rect.w, rect.h, 12, _SAND_TOP, _SAND_BOT, alpha=255)
    surf.blit(body, rect.topleft)
    # Punched ticket notches down the left & right mid edges.
    for ny in (rect.centery,):
        for nx in (rect.x, rect.right):
            n = pygame.Surface((10, 10), pygame.SRCALPHA)
            pygame.draw.circle(n, (0, 0, 0, 0), (5, 5), 5)
            hole = pygame.Surface((10, 10), pygame.SRCALPHA)
            # carve a dark sky-colored notch
            pygame.draw.circle(hole, (24, 16, 44, 235), (5, 5), 5)
            surf.blit(hole, (nx - 5, ny - 5))
    # Corner-fold rarity tab (top-left dog-ear in the rarity colour).
    fold = [(rect.x, rect.y), (rect.x + 30, rect.y), (rect.x, rect.y + 30)]
    pygame.draw.polygon(surf, pal["gem"], fold)
    pygame.draw.polygon(surf, lerp_color(pal["deep"], NEAR_BLACK, 0.3),
                        [(rect.x + 30, rect.y), (rect.x, rect.y + 30),
                         (rect.x + 30, rect.y + 30)])
    _gem(surf, rect.x + 11, rect.y + 11, 6, tier, t)
    # Leafy gold corner flourishes (tropical).
    for cx, cy, sx in ((rect.right - 12, rect.y + 10, -1),
                       (rect.right - 12, rect.bottom - 10, -1)):
        pygame.draw.arc(surf, (*_GOLD_DEEP, 220),
                        (cx - 8, cy - 8, 16, 16),
                        0.2, 2.0, 2)
    if secret:
        _draw_qmark(surf, rect.centerx, rect.y + 32, 36, _INK,
                    (200, 180, 150), thick=2)
        name = "???"
    else:
        th = _fit_skin(sid, 44)
        surf.blit(th, th.get_rect(center=(rect.centerx, rect.y + 32)))
        name = _disp_name(sid)
    nimg = _font(13, True).render(name, True, _INK)
    surf.blit(nimg, nimg.get_rect(center=(rect.centerx, rect.y + 60)))
    # Dashed tear line above the chip.
    for dx in range(rect.x + 10, rect.right - 10, 8):
        pygame.draw.line(surf, (*_INK, 90), (dx, rect.y + 70),
                         (dx + 4, rect.y + 70), 1)
    rim_col = _GOLD_BRIGHT if equipped else lerp_color(pal["gem"], _INK, 0.15)
    pygame.draw.rect(surf, rim_col, rect, width=2, border_radius=12)
    _state_chip(surf, sid, rect.centerx, rect.y + 84, equipped, secret,
                light=True)


# ═══════════════════════════════════════════════════════════════════════════
# DIRECTION 4 — "OBSIDIAN & GOLD"
# Luxury-jeweller treatment: near-black obsidian cards with a fine gold inner
# frame, a thin rarity light-bar that runs along the card's BASE (a glowing
# shelf-light), big confident thumbnail, and a minimalist gem dot. The most
# restrained / premium / AAA-mobile look. Deep cool sky, sparse stars.
# ═══════════════════════════════════════════════════════════════════════════

def dir_obsidian(surf, t=2.0):
    _bg(surf, [(6, 6, 20), (10, 10, 32), (16, 14, 44), (22, 18, 54)], t)
    _header_minimal(surf, "STORE", t)
    _tabstrip_minimal(surf, active=2, t=t)
    base_x, rects = _grid_rects()
    for (sid, eq, sec), rect in zip(_sample_cards(), rects):
        _card_obsidian(surf, sid, rect, eq, sec, t)
    _page_controls(surf, base_x, 1, 3)
    _back_pill(surf)


def _card_obsidian(surf, sid, rect, equipped, secret, t):
    tier = store_catalog.rarity(sid)
    pal = RARITY[tier]
    _drop_shadow(surf, rect, 12, blur=6, alpha=140)
    body = _vgrad_panel(rect.w, rect.h, 12, (20, 18, 26), (8, 7, 14), alpha=250)
    surf.blit(body, rect.topleft)
    # Fine gold inner frame (the jeweller's bezel).
    inner = rect.inflate(-8, -8)
    pygame.draw.rect(surf, (*_GOLD_DEEP, 200), inner, width=1, border_radius=8)
    # Rarity shelf-light bar along the base (glowing underline).
    bar = pygame.Rect(rect.x + 14, rect.bottom - 7, rect.w - 28, 3)
    _soft_glow(surf, bar.centerx, bar.centery, rect.w // 2, pal["glow"],
               80 if tier in ("epic", "legendary") else 45, layers=5)
    rounded_rect(surf, bar, 2, pal["gem"])
    if secret:
        _draw_qmark(surf, rect.centerx, rect.y + 32, 40, UI_CREAM, NEAR_BLACK,
                    thick=2)
        name = "???"
    else:
        th = _fit_skin(sid, 48)
        surf.blit(th, th.get_rect(center=(rect.centerx, rect.y + 34)))
        name = _disp_name(sid)
    # Minimalist gem dot, top-right.
    _gem(surf, rect.right - 15, rect.y + 15, 6, tier, t)
    nimg = _font(13, True).render(name, True, _GOLD_PALE)
    surf.blit(nimg, nimg.get_rect(center=(rect.centerx, rect.y + 62)))
    rim_col = _GOLD_BRIGHT if equipped else (52, 46, 40)
    pygame.draw.rect(surf, rim_col, rect, width=2, border_radius=12)
    _inner_bevel(surf, rect, 12, hi_a=46, lo_a=120)
    _state_chip(surf, sid, rect.centerx, rect.y + 82, equipped, secret)


# ═══════════════════════════════════════════════════════════════════════════
# DIRECTION 5 — "AURORA SHELF"
# Boutique-shelf treatment: cards grouped as if on a lit display shelf — a
# soft aurora wash behind the whole grid, each card a frosted-glass panel with
# a coloured corner gem AND a matching aura bloom, plus a subtle glass-frost
# texture. Most "alive"/atmospheric. Aurora teal-green-violet sky.
# ═══════════════════════════════════════════════════════════════════════════

def dir_aurora_shelf(surf, t=2.0):
    _bg(surf, [(8, 14, 40), (14, 34, 66), (26, 30, 78), (40, 22, 70)], t)
    # Aurora ribbons behind everything.
    for i, (cx, col) in enumerate([(110, (60, 200, 180)),
                                   (250, (150, 110, 240)),
                                   (180, (90, 150, 250))]):
        _soft_glow(surf, cx, 150 + i * 30, 150,
                   col, 26, layers=6)
    _header_classic(surf, "STORE", t, accent_top=(190, 255, 230),
                    accent_bot=(120, 200, 255))
    _tabstrip_pill(surf, active=2, t=t, cool=True)
    base_x, rects = _grid_rects()
    for (sid, eq, sec), rect in zip(_sample_cards(), rects):
        _card_aurora(surf, sid, rect, eq, sec, t)
    _page_controls(surf, base_x, 1, 3)
    _back_pill(surf)


def _card_aurora(surf, sid, rect, equipped, secret, t):
    tier = store_catalog.rarity(sid)
    pal = RARITY[tier]
    # Aura bloom behind the card matched to rarity.
    _soft_glow(surf, rect.centerx, rect.centery, rect.w // 2 + 6, pal["glow"],
               60 if tier in ("epic", "legendary") else 32, layers=5)
    _drop_shadow(surf, rect, 16, blur=5, alpha=90)
    # Frosted-glass body: cool translucent with a top sheen.
    body = _vgrad_panel(rect.w, rect.h, 16, (54, 64, 96), (24, 30, 56),
                        alpha=180)
    surf.blit(body, rect.topleft)
    # Frost speckle.
    fr = pygame.Surface(rect.size, pygame.SRCALPHA)
    rng = (sid.__hash__() & 0xffff)
    for k in range(40):
        rng = (rng * 1103515245 + 12345) & 0x7fffffff
        fx = rng % rect.w
        rng = (rng * 1103515245 + 12345) & 0x7fffffff
        fy = rng % rect.h
        fr.set_at((fx, fy), (255, 255, 255, 24))
    mask = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(),
                     border_radius=16)
    fr.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(fr, rect.topleft)
    # Top sheen.
    sheen = pygame.Surface((rect.w - 8, 18), pygame.SRCALPHA)
    for y in range(18):
        a = int(55 * (1 - y / 18))
        pygame.draw.line(sheen, (255, 255, 255, a), (0, y), (rect.w - 8, y))
    surf.blit(sheen, (rect.x + 4, rect.y + 4))
    if secret:
        _draw_qmark(surf, rect.centerx, rect.y + 32, 38, WHITE, NEAR_BLACK,
                    thick=2)
        name = "???"
    else:
        th = _fit_skin(sid, 46)
        surf.blit(th, th.get_rect(center=(rect.centerx, rect.y + 32)))
        name = _disp_name(sid)
    _gem(surf, rect.x + 15, rect.y + 15, 7, tier, t)
    nimg = _font(13, True).render(name, True, WHITE)
    sh = _font(13, True).render(name, True, NEAR_BLACK)
    sh.set_alpha(150)
    nr = nimg.get_rect(center=(rect.centerx, rect.y + 60))
    surf.blit(sh, (nr.x + 1, nr.y + 1))
    surf.blit(nimg, nr)
    rim_col = _GOLD_BRIGHT if equipped else lerp_color(pal["gem"], WHITE, 0.25)
    pygame.draw.rect(surf, (*rim_col, 230), rect, width=2, border_radius=16)
    _state_chip(surf, sid, rect.centerx, rect.y + 82, equipped, secret)


# ── shared chrome (headers, tabs, balance, page, back) ───────────────────────

def _state_chip(surf, sid, cx, cy, equipped, secret, light=False):
    if equipped:
        _coin_chip(surf, cx, cy, "EQUIPPED", NEAR_BLACK, (96, 210, 120),
                   coin=False, glow=(96, 210, 120))
    else:
        owned = store_data.is_owned(sid) and not secret
        if owned:
            _coin_chip(surf, cx, cy, "EQUIP", UI_CREAM, _GOLD_DEEP, coin=False)
        else:
            price = store_catalog.cost(sid)
            afford = store_data.balance() >= price
            bg = _GOLD_DEEP if afford else (70, 60, 70)
            fg = _GOLD_PALE if afford else (150, 140, 155)
            _coin_chip(surf, cx, cy, str(price), fg, bg, coin=True)


def _balance_bar(surf, cx, y, style="classic"):
    """A luxe coin-balance readout: a recessed dark capsule with a glowing coin,
    the value in gold-gradient digits, and a + add affordance. style tweaks tint
    so each direction's header reads as one family with its cards."""
    val = "12,480"
    vf = _font(22, True)
    vimg_w = vf.size(val)[0]
    coin_d = 24
    plus_w = 26
    pad = 14
    inner = coin_d + 8 + vimg_w + 10 + plus_w
    w = inner + pad * 2
    cap = pygame.Rect(cx - w // 2, y - 17, w, 34)
    _drop_shadow(surf, cap, 17, blur=4, alpha=90)
    body = _vgrad_panel(cap.w, cap.h, 17, (40, 30, 18), (20, 14, 8), alpha=250)
    surf.blit(body, cap.topleft)
    pygame.draw.rect(surf, (*_GOLD_BRIGHT, 180), cap, width=1,
                     border_radius=17)
    _inner_bevel(surf, cap, 17, hi_a=60, lo_a=90)
    x = cap.x + pad
    _soft_glow(surf, x + coin_d // 2, y, coin_d, (255, 200, 80), 80, layers=4)
    _coin_icon(surf, x + coin_d // 2, y, coin_d // 2)
    x += coin_d + 8
    _gradient_text(surf, val, vf, (x + vimg_w // 2, y),
                   (255, 244, 190), (236, 170, 60), shadow=True)
    x += vimg_w + 10
    # + add-coins button.
    addr = pygame.Rect(x, y - 11, plus_w, 22)
    rounded_rect(surf, addr, 8, _GOLD_DEEP)
    pygame.draw.rect(surf, _GOLD_BRIGHT, addr, width=1, border_radius=8)
    pimg = _font(18, True).render("+", True, _GOLD_PALE)
    surf.blit(pimg, pimg.get_rect(center=addr.center))


def _daily_pill(surf):
    f = _font(12, True)
    lbl = f.render("DAILY", True, (28, 18, 8))
    timg = f.render("+50", True, (28, 18, 8))
    w = lbl.get_width() + 6 + timg.get_width() + 22
    r = pygame.Rect(W - 12 - w, 14, w, 24)
    _soft_glow(surf, r.centerx, r.centery, w // 2, (255, 200, 80), 50, layers=3)
    body = _vgrad_panel(r.w, r.h, 11, (255, 215, 120), _GOLD_DEEP, alpha=255)
    surf.blit(body, r.topleft)
    pygame.draw.rect(surf, _GOLD_BRIGHT, r, width=1, border_radius=11)
    surf.blit(lbl, lbl.get_rect(midleft=(r.x + 11, r.centery)))
    surf.blit(timg, timg.get_rect(midleft=(r.x + 11 + lbl.get_width() + 6,
                                           r.centery)))


def _header_classic(surf, txt, t, accent_top, accent_bot):
    _outlined_redgold(surf, txt, (W // 2, 30), 28)
    _balance_bar(surf, W // 2, 64)
    _daily_pill(surf)


def _header_banner(surf, txt, t):
    # A scalloped sandstone banner behind the title (tropical).
    bw, bh = 150, 40
    br = pygame.Rect(W // 2 - bw // 2, 12, bw, bh)
    _drop_shadow(surf, br, 12, blur=4, alpha=90)
    body = _vgrad_panel(br.w, br.h, 12, (255, 224, 150), (224, 140, 50),
                        alpha=255)
    surf.blit(body, br.topleft)
    pygame.draw.rect(surf, _RED_OUTLINE, br, width=2, border_radius=12)
    _gradient_text(surf, txt, _font(26, True), (W // 2, 32),
                   (90, 30, 16), (150, 40, 20), shadow=False)
    _balance_bar(surf, W // 2, 70)
    _daily_pill(surf)


def _header_minimal(surf, txt, t):
    # Thin gold hairline-framed wordmark, very restrained.
    _gradient_text(surf, txt, _font(28, True), (W // 2, 30),
                   (255, 244, 196), (210, 150, 50),
                   outline=(40, 30, 10))
    pygame.draw.line(surf, (*_GOLD_DEEP, 180), (W // 2 - 70, 48),
                     (W // 2 + 70, 48), 1)
    _balance_bar(surf, W // 2, 70)
    _daily_pill(surf)


def _outlined_redgold(surf, txt, center, size):
    """The shared gold-on-red outlined title (matches the menu family) but with
    a gold gradient fill for extra richness."""
    f = _font(size, True)
    out = f.render(txt, True, _RED_OUTLINE)
    r = f.render(txt, True, WHITE).get_rect(center=center)
    for ox, oy in ((-2, 0), (2, 0), (0, -2), (0, 2),
                   (-2, -2), (2, -2), (-2, 2), (2, 2)):
        surf.blit(out, (r.x + ox, r.y + oy))
    sh = f.render(txt, True, NEAR_BLACK)
    sh.set_alpha(160)
    surf.blit(sh, (r.x + 2, r.y + 3))
    _gradient_text(surf, txt, f, center, (255, 240, 180), (236, 170, 60),
                   shadow=False)


# Tab strip variants ---------------------------------------------------------

def _tab_layout():
    f = _font(12, True)
    pad, gap = 11, 6
    widths = [f.size(lbl)[0] + 2 * pad for lbl in _TABS]
    return f, widths, gap, 12


def _tabstrip_pill(surf, active, t, cool=False):
    f, widths, gap, x0 = _tab_layout()
    y = 94
    cx = x0
    for i, lbl in enumerate(_TABS):
        w = widths[i]
        r = pygame.Rect(cx, y - 13, w, 26)
        on = (i == active)
        if on:
            _soft_glow(surf, r.centerx, r.centery, w // 2 + 4,
                       (255, 200, 80) if not cool else (120, 200, 255),
                       70, layers=3)
            body = _vgrad_panel(r.w, r.h, 9,
                                lerp_color(_GOLD_BRIGHT, WHITE, 0.2),
                                _GOLD_DEEP, alpha=255)
            surf.blit(body, r.topleft)
            pygame.draw.rect(surf, _GOLD_PALE, r, width=1, border_radius=9)
            col = (40, 24, 8)
        else:
            rounded_rect(surf, r, 9, (30, 24, 50), alpha=210)
            pygame.draw.rect(surf, (80, 72, 110), r, width=1, border_radius=9)
            col = _GOLD_PALE
        timg = f.render(lbl, True, col)
        surf.blit(timg, timg.get_rect(center=r.center))
        cx += w + gap
        if cx > W - 18:
            break
    _draw_chev(surf, W - 13, y)


def _tabstrip_underline(surf, active, t):
    f, widths, gap, x0 = _tab_layout()
    y = 94
    cx = x0
    for i, lbl in enumerate(_TABS):
        w = widths[i]
        on = (i == active)
        col = _GOLD_BRIGHT if on else _GOLD_PALE
        timg = f.render(lbl, True, col)
        if not on:
            timg.set_alpha(150)
        tr = timg.get_rect(center=(cx + w // 2, y))
        surf.blit(timg, tr)
        if on:
            ur = pygame.Rect(tr.x, y + 11, tr.w, 3)
            _soft_glow(surf, ur.centerx, ur.centery, tr.w, (255, 200, 80),
                       70, layers=3)
            rounded_rect(surf, ur, 2, _GOLD_BRIGHT)
        cx += w + gap
        if cx > W - 18:
            break
    _draw_chev(surf, W - 13, y)


def _tabstrip_ticket(surf, active, t):
    f, widths, gap, x0 = _tab_layout()
    y = 94
    cx = x0
    for i, lbl in enumerate(_TABS):
        w = widths[i]
        r = pygame.Rect(cx, y - 13, w, 26)
        on = (i == active)
        if on:
            body = _vgrad_panel(r.w, r.h, 6, _SAND_TOP, _SAND_BOT, alpha=255)
            surf.blit(body, r.topleft)
            pygame.draw.rect(surf, _RED_OUTLINE, r, width=2, border_radius=6)
            col = _INK
        else:
            rounded_rect(surf, r, 6, (40, 26, 60), alpha=200)
            pygame.draw.rect(surf, (110, 70, 90), r, width=1, border_radius=6)
            col = (236, 200, 170)
        timg = f.render(lbl, True, col)
        surf.blit(timg, timg.get_rect(center=r.center))
        cx += w + gap
        if cx > W - 18:
            break
    _draw_chev(surf, W - 13, y)


def _tabstrip_minimal(surf, active, t):
    f, widths, gap, x0 = _tab_layout()
    y = 94
    cx = x0
    for i, lbl in enumerate(_TABS):
        w = widths[i]
        on = (i == active)
        col = _GOLD_BRIGHT if on else (130, 124, 140)
        timg = f.render(lbl, True, col)
        tr = timg.get_rect(center=(cx + w // 2, y))
        surf.blit(timg, tr)
        if on:
            dot = (tr.centerx, y + 12)
            pygame.draw.circle(surf, _GOLD_BRIGHT, dot, 2)
        cx += w + gap
        if cx > W - 18:
            break
    _draw_chev(surf, W - 13, y)


def _draw_chev(surf, x, y):
    r = pygame.Rect(x - 16, y - 13, 16, 26)
    rounded_rect(surf, r, 8, (34, 26, 56), alpha=220)
    pygame.draw.rect(surf, (90, 78, 120), r, width=1, border_radius=8)
    cxp, cyp = r.center
    pts = [(cxp - 2, cyp - 5), (cxp + 3, cyp), (cxp - 2, cyp + 5)]
    pygame.draw.lines(surf, _GOLD_BRIGHT, False, pts, 2)


def _page_controls(surf, base_x, page, n_pages):
    w = _CARD_W * 2 + _GAP
    y = _GRID_TOP + 4 * (_CARD_H + _GAP)
    cy = y + 8
    lbl = _font(12, True).render(f"PAGE  {page + 1} / {n_pages}", True,
                                 _GOLD_PALE)
    surf.blit(lbl, lbl.get_rect(center=(base_x + w // 2, cy)))
    for cx, glyph, on in ((base_x + 16, "<", page > 0),
                          (base_x + w - 16, ">", page < n_pages - 1)):
        r = pygame.Rect(0, 0, 30, 22)
        r.center = (cx, cy)
        rounded_rect(surf, r, 11, _GOLD_DEEP if on else (60, 52, 64))
        pygame.draw.rect(surf, _GOLD_BRIGHT if on else (90, 82, 92), r,
                         width=1, border_radius=11)
        g = _font(15, True).render(glyph, True,
                                   _GOLD_PALE if on else (150, 140, 155))
        surf.blit(g, g.get_rect(center=(cx, cy - 1)))


def _back_pill(surf):
    r = pygame.Rect(0, 0, 160, 36)
    r.center = (W // 2, H - 28)
    _drop_shadow(surf, r, 18, blur=4, alpha=90)
    body = _vgrad_panel(r.w, r.h, 18, (40, 32, 56), (22, 16, 38), alpha=235)
    surf.blit(body, r.topleft)
    pygame.draw.rect(surf, (*_GOLD_BRIGHT, 180), r, width=1, border_radius=18)
    timg = _font(18, True).render("BACK", True, _GOLD_PALE)
    surf.blit(timg, timg.get_rect(center=r.center))


# ── buy-confirmation modal close-up ──────────────────────────────────────────

def _modal_closeup(surf, ox, oy, sid):
    """The redesigned buy-confirmation modal, drawn into a 360x300 region at
    (ox, oy) over a dimmed scrim so the art-director sees its depth + chrome."""
    region = pygame.Rect(ox, oy, 360, 300)
    # mini night-sky behind so the scrim reads.
    bg = _vgrad_panel(360, 300, 0, (18, 12, 46), (30, 18, 64))
    surf.blit(bg, region.topleft)
    scrim = pygame.Surface((360, 300), pygame.SRCALPHA)
    scrim.fill((6, 6, 14, 180))
    surf.blit(scrim, region.topleft)

    tier = store_catalog.rarity(sid)
    pal = RARITY[tier]
    pw, ph = 280, 230
    panel = pygame.Rect(ox + (360 - pw) // 2, oy + (300 - ph) // 2, pw, ph)
    _drop_shadow(surf, panel, 18, blur=8, alpha=160)
    _soft_glow(surf, panel.centerx, panel.y + 70, 70, pal["glow"], 70,
               layers=6)
    body = _vgrad_panel(pw, ph, 18, (40, 30, 64), (18, 12, 38), alpha=250)
    surf.blit(body, panel.topleft)
    pygame.draw.rect(surf, lerp_color(_GOLD_BRIGHT, NEAR_BLACK, 0.4), panel,
                     width=3, border_radius=18)
    pygame.draw.rect(surf, _GOLD_BRIGHT, panel.inflate(-3, -3), width=1,
                     border_radius=16)
    _inner_bevel(surf, panel, 18, hi_a=70, lo_a=110)

    head = _font(14, True).render("CONFIRM PURCHASE", True, _GOLD_PALE)
    surf.blit(head, head.get_rect(center=(panel.centerx, panel.y + 24)))
    # Gem + rarity word.
    _gem(surf, panel.centerx - 52, panel.y + 24, 6, tier)
    rword = _font(11, True).render(tier.upper(), True, pal["gem"])
    surf.blit(rword, rword.get_rect(midleft=(panel.centerx + 40, panel.y + 24)))

    th = _fit_skin(sid, 56)
    surf.blit(th, th.get_rect(center=(panel.centerx, panel.y + 70)))
    nimg = _font(17, True).render(_disp_name(sid), True, _GOLD_BRIGHT)
    surf.blit(nimg, nimg.get_rect(center=(panel.centerx, panel.y + 110)))
    _coin_chip(surf, panel.centerx, panel.y + 138, str(store_catalog.cost(sid)),
               _GOLD_PALE, _GOLD_DEEP, coin=True, glow=(255, 200, 80))

    bw, bh = 116, 38
    by = panel.bottom - 26
    no = pygame.Rect(panel.x + 14, by - bh // 2, bw, bh)
    yes = pygame.Rect(panel.right - 14 - bw, by - bh // 2, bw, bh)
    nb = _vgrad_panel(bw, bh, bh // 2, (74, 64, 84), (50, 42, 62))
    surf.blit(nb, no.topleft)
    pygame.draw.rect(surf, (132, 122, 144), no, width=1, border_radius=bh // 2)
    ct = _font(14, True).render("CANCEL", True, UI_CREAM)
    surf.blit(ct, ct.get_rect(center=no.center))
    _soft_glow(surf, yes.centerx, yes.centery, bw // 2, (255, 200, 80), 70,
               layers=4)
    yb = _vgrad_panel(bw, bh, bh // 2, lerp_color(_GOLD_BRIGHT, WHITE, 0.2),
                      _GOLD_DEEP)
    surf.blit(yb, yes.topleft)
    pygame.draw.rect(surf, _GOLD_PALE, yes, width=1, border_radius=bh // 2)
    yt = _font(14, True).render("BUY", True, (40, 24, 8))
    surf.blit(yt, yt.get_rect(center=yes.center))


# ── detail callout strip ─────────────────────────────────────────────────────

def _single_card(surf, ox, oy, sid, tier_override=None, equipped=False,
                 secret=False, scale=1.6):
    """A redesigned single card at larger scale (the GEM VITRINE language, the
    most representative of the set) so the art-director can read the small
    details: gem, glow, bevel, sheen, chip."""
    cw, ch = int(_CARD_W * scale), int(_CARD_H * scale)
    rect = pygame.Rect(ox, oy, cw, ch)
    tier = tier_override or store_catalog.rarity(sid)
    pal = RARITY[tier]
    _drop_shadow(surf, rect, 20, blur=6, alpha=120)
    body = _vgrad_panel(cw, ch, 20, (30, 22, 56), (14, 9, 34), alpha=238)
    surf.blit(body, rect.topleft)
    _soft_glow(surf, rect.centerx, rect.y + int(54 * scale), int(50 * scale),
               pal["glow"], 95 if tier in ("epic", "legendary") else 55,
               layers=6)
    rim = _GOLD_BRIGHT if equipped else pal["gem"]
    pygame.draw.rect(surf, lerp_color(rim, NEAR_BLACK, 0.45), rect, width=3,
                     border_radius=20)
    pygame.draw.rect(surf, rim, rect.inflate(-3, -3), width=2,
                     border_radius=18)
    _inner_bevel(surf, rect, 20, hi_a=70, lo_a=95)
    sheen = pygame.Surface((cw - 10, 34), pygame.SRCALPHA)
    for y in range(34):
        a = int(46 * (1 - y / 34))
        pygame.draw.line(sheen, (255, 255, 255, a), (0, y), (cw - 10, y))
    surf.blit(sheen, (rect.x + 5, rect.y + 5))
    if secret:
        _draw_qmark(surf, rect.centerx, rect.y + int(52 * scale), int(60 * scale),
                    UI_CREAM, NEAR_BLACK, thick=3)
        name = "???"
    else:
        th = _fit_skin(sid, int(72 * scale))
        surf.blit(th, th.get_rect(center=(rect.centerx, rect.y + int(52 * scale))))
        name = _disp_name(sid)
    _gem(surf, rect.right - int(26 * scale), rect.y + int(26 * scale),
         int(13 * scale), tier)
    nimg = _font(int(15 * scale), True).render(name, True, _GOLD_PALE)
    surf.blit(nimg, nimg.get_rect(center=(rect.centerx, rect.y + int(96 * scale))))
    _state_chip2(surf, sid, rect.centerx, rect.y + int(128 * scale), equipped,
                 secret)
    # Tier label under the card.
    lab = _font(13, True).render(tier.upper(), True, pal["gem"])
    surf.blit(lab, lab.get_rect(center=(rect.centerx, rect.bottom + 12)))


def _state_chip2(surf, sid, cx, cy, equipped, secret):
    """Larger chip for the detail strip."""
    if equipped:
        _coin_chip(surf, cx, cy, "EQUIPPED", NEAR_BLACK, (96, 210, 120),
                   coin=False, glow=(96, 210, 120), h=30)
    elif secret:
        _coin_chip(surf, cx, cy, str(store_catalog.cost(sid)), _GOLD_PALE,
                   _GOLD_DEEP, coin=True, glow=(255, 200, 80), h=30)
    else:
        _coin_chip(surf, cx, cy, str(store_catalog.cost(sid)), _GOLD_PALE,
                   _GOLD_DEEP, coin=True, glow=(255, 200, 80), h=30)


# ── compose the combined sheet ───────────────────────────────────────────────

def main():
    pad = 24
    label_h = 30
    screen_w, screen_h = W, H
    cols = 5
    sheet_w = pad + cols * (screen_w + pad)
    detail_h = 560
    sheet_h = label_h + pad + screen_h + pad + label_h + detail_h + pad

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((18, 16, 26))

    directions = [
        ("GEM VITRINE", dir_gem_vitrine),
        ("FOIL CARDS", dir_foil_cards),
        ("TROPICAL TICKET", dir_tropical_ticket),
        ("OBSIDIAN & GOLD", dir_obsidian),
        ("AURORA SHELF", dir_aurora_shelf),
    ]

    title = _font(20, True).render(
        "SKYBIT  COIN STORE  —  REDESIGN  ROUND 1", True, _GOLD_BRIGHT)
    sheet.blit(title, (pad, 6))

    for i, (name, fn) in enumerate(directions):
        screen = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
        fn(screen, t=2.0 + i * 0.6)
        x = pad + i * (screen_w + pad)
        y = label_h + pad
        # frame
        pygame.draw.rect(sheet, (40, 36, 54),
                         (x - 3, y - 3, screen_w + 6, screen_h + 6),
                         border_radius=6)
        sheet.blit(screen, (x, y))
        lbl = _font(16, True).render(f"{i + 1}.  {name}", True, _GOLD_PALE)
        sheet.blit(lbl, (x + 4, label_h - 4))

    # ── detail callout row ──
    dy = label_h + pad + screen_h + pad
    dlabel = _font(18, True).render(
        "DETAIL CALLOUTS  —  rarity tiers, equipped, secret, chips, balance, modal",
        True, _GOLD_BRIGHT)
    sheet.blit(dlabel, (pad, dy - 26))

    # Cards: 4 rarity tiers + equipped + secret.
    ani = sorted(store_catalog.ids_of_group("animal"), key=store_catalog.cost)
    cos = sorted(store_catalog.ids_of_group("costume"), key=store_catalog.cost)
    card_specs = [
        (cos[0], "common", False, False),
        (ani[0], "rare", False, False),
        (ani[10], "epic", False, False),
        (ani[16], "legendary", False, False),
        (cos[1], None, True, False),       # equipped
        ("skin_ufo", None, False, True),   # secret
    ]
    cw = int(_CARD_W * 1.6)
    cx = pad
    for sid, ov, eq, sec in card_specs:
        _single_card(sheet, cx, dy + 10, sid, tier_override=ov,
                     equipped=eq, secret=sec, scale=1.6)
        cx += cw + 20

    # Balance bar + chip examples + modal, in the remaining right column.
    rx = cx + 20
    bsurf = pygame.Surface((360, 60), pygame.SRCALPHA)
    _balance_bar(bsurf, 180, 30)
    sheet.blit(bsurf, (rx, dy + 10))
    lbl = _font(13, True).render("BALANCE", True, _GOLD_PALE)
    sheet.blit(lbl, (rx + 130, dy + 50))

    # chip row
    cy2 = dy + 110
    csurf = pygame.Surface((360, 80), pygame.SRCALPHA)
    _coin_chip(csurf, 60, 24, "EQUIPPED", NEAR_BLACK, (96, 210, 120),
               coin=False, glow=(96, 210, 120), h=30)
    _coin_chip(csurf, 175, 24, "EQUIP", UI_CREAM, _GOLD_DEEP, coin=False, h=30)
    _coin_chip(csurf, 290, 24, "1200", _GOLD_PALE, _GOLD_DEEP, coin=True,
               glow=(255, 200, 80), h=30)
    _coin_chip(csurf, 110, 58, "9000", (150, 140, 155), (70, 60, 70),
               coin=True, h=30)
    sheet.blit(csurf, (rx, cy2 - 20))
    lbl2 = _font(13, True).render("STATE CHIPS  (equipped / equip / afford / locked)",
                                  True, _GOLD_PALE)
    sheet.blit(lbl2, (rx, cy2 + 60))

    # modal close-up
    _modal_closeup(sheet, rx, dy + 180, ani[16])
    mlbl = _font(13, True).render("BUY-CONFIRM MODAL", True, _GOLD_PALE)
    sheet.blit(mlbl, (rx + 110, dy + 180 + 305))

    out = os.path.join(_HERE, "round_1.png")
    pygame.image.save(sheet, out)
    print("saved:", out)
    print("sheet size:", sheet.get_size())


if __name__ == "__main__":
    main()
