"""
Round-2 render harness for the COIN STORE redesign — CONVERGED direction.

The art-director converged on ONE chassis: OBSIDIAN & GOLD body + rarity
SHELF-LIGHT BAR + inset GEM BADGE. This script builds that single design at
near-shippable quality, with three within-chassis SUB-VARIANTS (A/B/C that
differ only in shelf-bar intensity, gem placement, and bezel weight), plus a
large DETAIL-CALLOUT row: the 4 rarity-tier cards + equipped + secret at scale,
the unified chip family, the polished balance header, the redesigned tab strip,
and the rebuilt buy-confirmation modal.

All visuals are procedural / pygame-only and both-target safe (no desktop- or
browser-only API). Run:  python docs/store_redesign/render_r2.py
"""
from __future__ import annotations

import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

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
    _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP, _RED_OUTLINE,
)
from game.powerup_help import _seeded_stars  # noqa: E402
from game import parrot, store_catalog, store_data  # noqa: E402
from game.surprise_box_variants import _draw_qmark  # noqa: E402

store_data.load()

# ── rarity language ──────────────────────────────────────────────────────────
# The shelf-bar is the PRIMARY rarity cue, the gem the SECONDARY. Both pull from
# the same per-tier triplet so they read as one jewel. Re-warmed toward Skybit's
# gold world but kept on the established casual ladder (gray/blue/purple/orange).
RARITY = {
    "common":    {"gem": (196, 204, 218), "glow": (170, 182, 205),
                  "deep": (74, 80, 96)},
    "rare":      {"gem": (104, 182, 255), "glow": (78, 158, 255),
                  "deep": (26, 62, 124)},
    "epic":      {"gem": (200, 126, 250), "glow": (184, 100, 248),
                  "deep": (74, 34, 116)},
    "legendary": {"gem": (255, 184, 76),  "glow": (255, 156, 46),
                  "deep": (126, 68, 14)},
}
# Mystery tier for the secret card — neutral iridescent, claims no tier.
MYSTERY = {"gem": (206, 214, 224), "glow": (150, 190, 220),
           "deep": (64, 70, 92)}

# Five tabs sit comfortably across 360px with even gutters; the right chevron
# signals the rest (SHADES/PARCELS) scroll in — real stores paginate tabs.
_TABS = ("COSTUMES", "PARROTS", "ANIMALS", "SHOES", "HATS")

_STARS = _seeded_stars()

# Obsidian body stops — near-black, subtly top-lit so the panel reads as lit
# from above rather than a flat fill.
_OBS_TOP = (26, 24, 32)
_OBS_BOT = (9, 8, 15)


# ── thumbnail cache ──────────────────────────────────────────────────────────
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


# ── premium primitives ───────────────────────────────────────────────────────

def _soft_glow(surf, cx, cy, radius, color, peak_alpha, layers=6):
    """Layered additive bloom. Cheap (no per-pixel) so cards emit light, not
    just an outline. The glow BUDGET is dialled per call to a strict hierarchy
    (balance coin brightest, then equipped rim, shelf-bar, gem, thumbnail)."""
    for i in range(layers, 0, -1):
        r = int(radius * i / layers)
        a = int(peak_alpha * (1 - (i - 1) / layers) ** 1.7)
        if r <= 0 or a <= 0:
            continue
        g = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(g, (*color, a), (r + 1, r + 1), r)
        surf.blit(g, (cx - r - 1, cy - r - 1), special_flags=pygame.BLEND_ADD)


def _vgrad_panel(w, h, radius, top, bot, alpha=255):
    """Rounded vertical-gradient panel (top brighter), corner-masked. The base
    body for every card/chip so panels read as gently lit, not flat."""
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
    """Soft drop shadow under a card — concentric expanding rounded rects at
    falling alpha give depth the translucent panels lack."""
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


def _inset_disc(surf, cx, cy, r, tint=(6, 6, 12)):
    """A clean dark inset disc for the thumbnail to sit on — a subtle inner
    shadow (darker rim, lighter centre) so the product reads as the brightest
    thing on the card. Replaces round-1's colored glow ring entirely."""
    # radial: lighter centre -> dark rim, so it reads recessed.
    disc = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    for i in range(r, 0, -1):
        f = i / r
        c = lerp_color((30, 28, 40), tint, f ** 1.3)
        pygame.draw.circle(disc, (*c, 255), (r, r), i)
    surf.blit(disc, (cx - r, cy - r))
    # inner-shadow ring: a thin dark arc top-left reading as a lip.
    ring = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
    pygame.draw.circle(ring, (0, 0, 0, 130), (r + 1, r + 1), r, 2)
    pygame.draw.circle(ring, (*_GOLD_DEEP, 60), (r + 1, r + 1), r - 1, 1)
    surf.blit(ring, (cx - r - 1, cy - r - 1))


def _shelf_bar(surf, rect, tier, intensity=1.0, mystery=False):
    """The rarity SHELF-LIGHT BAR along the card base — an additive horizontal
    gradient strip in the tier colour that glows UP into the body like a museum
    vitrine light. PRIMARY rarity cue; reads the 4 tiers at 360px without
    recolouring the obsidian body."""
    pal = MYSTERY if mystery else RARITY[tier]
    glow, gem = pal["glow"], pal["gem"]
    bw = rect.w - 28
    bx = rect.x + 14
    by = rect.bottom - 8
    # Up-wash: a SHALLOW additive gradient fading upward from the bar — a vitrine
    # spill of light, deliberately restrained so it never recolours the body.
    wash_h = int(10 * intensity) + 6
    wash = pygame.Surface((bw, wash_h), pygame.SRCALPHA)
    peak = int(22 * intensity) + 8
    for y in range(wash_h):
        f = 1.0 - y / wash_h
        # horizontal falloff toward the bar ends so it reads as a seated light.
        a = int(peak * f ** 2.6)
        if a <= 0:
            continue
        for seg in range(0, bw, 2):
            hx = abs(seg - bw / 2) / (bw / 2)
            ha = int(a * (1.0 - 0.6 * hx ** 2))
            if ha > 0:
                wash.set_at((seg, wash_h - 1 - y), (*glow, ha))
                if seg + 1 < bw:
                    wash.set_at((seg + 1, wash_h - 1 - y), (*glow, ha))
    surf.blit(wash, (bx, by - wash_h + 3), special_flags=pygame.BLEND_ADD)
    # The crisp bar itself: bright core with a hot centre.
    bar = pygame.Rect(bx, by, bw, 3)
    core = pygame.Surface((bw, 3), pygame.SRCALPHA)
    for sx in range(bw):
        hx = abs(sx - bw / 2) / (bw / 2)
        c = lerp_color(lerp_color(gem, WHITE, 0.4), pal["deep"], hx ** 1.4)
        a = int(255 * (1.0 - 0.4 * hx ** 2))
        for sy in range(3):
            core.set_at((sx, sy), (*c, a))
    mask = pygame.Surface((bw, 3), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, bw, 3), border_radius=1)
    core.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(core, bar.topleft)


def _gold_leaf(surf, cx, cy, sx):
    """A tiny two-leaf gold sprig flourish for LEGENDARY cards only. Drawn as a
    pair of small filled arcs + a stem, faint enough to stay an accent."""
    col = (*_GOLD_DEEP, 170)
    leaf = pygame.Surface((20, 16), pygame.SRCALPHA)
    pygame.draw.line(leaf, col, (10, 14), (10, 3), 1)
    pygame.draw.ellipse(leaf, (*_GOLD_BRIGHT, 150), (4, 4, 7, 9))
    pygame.draw.ellipse(leaf, (*_GOLD_BRIGHT, 150), (10, 5, 7, 9))
    if sx < 0:
        leaf = pygame.transform.flip(leaf, True, False)
    surf.blit(leaf, (cx - 10, cy - 6))


def _gem(surf, cx, cy, r, tier, t=0.0, inset=True, mystery=False):
    """A small faceted rarity gem badge inset in the card corner: lit top-left
    facet, shaded bottom-right facet, white specular pip, seated in a thin dark
    keyline so it reads as inset jewellery, not a floating sticker. Halo is
    HALVED vs round 1 and the gem ~30% smaller — SECONDARY rarity marker."""
    pal = MYSTERY if mystery else RARITY[tier]
    base, glow, deep = pal["gem"], pal["glow"], pal["deep"]
    if inset:
        # Dark seat well so the gem reads as set INTO the card.
        seat = pygame.Surface((r * 2 + 8, r * 2 + 8), pygame.SRCALPHA)
        pygame.draw.circle(seat, (0, 0, 0, 150), (r + 4, r + 4), r + 3)
        pygame.draw.circle(seat, (*_GOLD_DEEP, 90), (r + 4, r + 4), r + 3, 1)
        surf.blit(seat, (cx - r - 4, cy - r - 4))
    # Halved halo: modest additive bloom only.
    _soft_glow(surf, cx, cy, int(r * 1.5), glow,
               int(70 + 30 * (0.5 + 0.5 * math.sin(t * 3))), layers=4)
    top, bot = (cx, cy - r), (cx, cy + r)
    left, right = (cx - r, cy), (cx + r, cy)
    if mystery:
        # Iridescent mystery gem: shifting cool tint across the facets.
        f1 = lerp_color((150, 200, 230), (200, 170, 230), 0.5)
        pygame.draw.polygon(surf, lerp_color(f1, WHITE, 0.4), [top, left, (cx, cy)])
        pygame.draw.polygon(surf, f1, [top, right, (cx, cy)])
        pygame.draw.polygon(surf, lerp_color(f1, deep, 0.4), [left, bot, (cx, cy)])
        pygame.draw.polygon(surf, lerp_color(f1, deep, 0.62), [right, bot, (cx, cy)])
    else:
        pygame.draw.polygon(surf, lerp_color(base, WHITE, 0.4), [top, left, (cx, cy)])
        pygame.draw.polygon(surf, base, [top, right, (cx, cy)])
        pygame.draw.polygon(surf, lerp_color(base, deep, 0.45), [left, bot, (cx, cy)])
        pygame.draw.polygon(surf, lerp_color(base, deep, 0.7), [right, bot, (cx, cy)])
    pygame.draw.polygon(surf, lerp_color(deep, NEAR_BLACK, 0.4),
                        [top, right, bot, left], width=1)
    pip = pygame.Surface((4, 4), pygame.SRCALPHA)
    pygame.draw.circle(pip, (255, 255, 255, 235), (2, 2), 1)
    surf.blit(pip, (cx - 2 - r // 3, cy - 2 - r // 3))


# ── unified chip family ──────────────────────────────────────────────────────
# Identical pill silhouette + hairline gold rim for EVERY state. Only the fill
# and content differ. Can't-afford = DESATURATED gold + lock glyph (never grey).

_CHIP_STATES = {
    "price":     {"fg": _GOLD_PALE, "bg": _GOLD_DEEP, "rim": (*_GOLD_BRIGHT, 150)},
    "equip":     {"fg": UI_CREAM,   "bg": (96, 74, 24), "rim": (*_GOLD_BRIGHT, 150)},
    "equipped":  {"fg": (10, 30, 14), "bg": (84, 196, 112), "rim": (200, 255, 210, 200)},
    "locked":    {"fg": (212, 190, 138), "bg": (108, 92, 56), "rim": (190, 168, 112, 170)},
}


def _lock_glyph(surf, cx, cy, col):
    """Tiny padlock for the can't-afford chip — body + shackle, ~9px tall."""
    body = pygame.Rect(cx - 4, cy - 1, 8, 6)
    rounded_rect(surf, body, 2, col)
    pygame.draw.arc(surf, col, (cx - 3, cy - 6, 6, 8), 0.2, math.pi - 0.2, 2)
    surf.set_at((cx, cy + 2), NEAR_BLACK)


def _chip(surf, cx, cy, text, state, coin=False, h=24, lock=False):
    """The single chip silhouette for all states. Pill body (gradient), hairline
    gold rim, optional coin glyph or lock, centred on (cx, cy). Text weight is
    bumped one notch (bold + +1px) vs round 1 for legibility at chip scale."""
    sp = _CHIP_STATES[state]
    fsz = max(12, int(h * 0.56))
    f = _font(fsz, True)
    timg = f.render(text, True, sp["fg"])
    coin_d = int(h * 0.62)
    pre_w = (coin_d + 4) if coin else (12 if lock else 0)
    pad = 12
    w = pre_w + timg.get_width() + pad * 2
    chip = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    # No additive bloom on chips — the equipped read is carried by the card-rim,
    # so the green pill stays a flat tactile chip and the glow budget stays lean
    # (avoids the green wash bleeding over the thumbnail / neighbours).
    body = _vgrad_panel(w, h, h // 2, lerp_color(sp["bg"], WHITE, 0.18), sp["bg"])
    surf.blit(body, chip.topleft)
    # subtle top sheen for the glossy pill read shared across the family.
    sheen = pygame.Surface((w - 6, h // 2), pygame.SRCALPHA)
    for y in range(h // 2):
        a = int(46 * (1 - y / (h // 2)))
        pygame.draw.line(sheen, (255, 255, 255, a), (0, y), (w - 6, y))
    smask = pygame.Surface((w - 6, h // 2), pygame.SRCALPHA)
    pygame.draw.rect(smask, (255, 255, 255, 255), smask.get_rect(),
                     border_radius=h // 2)
    sheen.blit(smask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(sheen, (chip.x + 3, chip.y + 2))
    pygame.draw.rect(surf, sp["rim"], chip, width=1, border_radius=h // 2)
    x = chip.x + pad
    if coin:
        _coin_icon(surf, x + coin_d // 2, cy, coin_d // 2)
        x += coin_d + 4
    elif lock:
        _lock_glyph(surf, x + 4, cy, sp["fg"])
        x += 12
    surf.blit(timg, timg.get_rect(midleft=(x, cy)))
    return chip


def _state_chip(surf, sid, cx, cy, equipped, secret, h=24):
    if equipped:
        _chip(surf, cx, cy, "EQUIPPED", "equipped", h=h)
        return
    owned = store_data.is_owned(sid) and not secret
    if owned:
        _chip(surf, cx, cy, "EQUIP", "equip", h=h)
        return
    price = store_catalog.cost(sid)
    afford = store_data.balance() >= price
    if afford:
        _chip(surf, cx, cy, f"{price:,}", "price", coin=True, h=h)
    else:
        _chip(surf, cx, cy, f"{price:,}", "locked", lock=True, h=h)


def _gradient_text(surf, txt, font_obj, center, top, bot, outline=None,
                   shadow=True):
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


# ── background ───────────────────────────────────────────────────────────────

def _bg(surf, stops, t=2.0, stars=True, aurora=False):
    h = surf.get_height()
    n = len(stops)
    for y in range(h):
        f = y / max(1, h - 1)
        seg = min(n - 2, int(f * (n - 1)))
        local = (f * (n - 1)) - seg
        c = lerp_color(stops[seg], stops[seg + 1], local)
        pygame.draw.line(surf, c, (0, y), (surf.get_width() - 1, y))
    if aurora:
        # <=15% aurora ribbon wash behind the grid — never lowers card contrast
        # because it sits UNDER the obsidian cards and is capped very low.
        for i, (cx, col) in enumerate([(96, (54, 150, 150)),
                                       (264, (120, 92, 200))]):
            _soft_glow(surf, cx, 230 + i * 60, 140, col, 11, layers=6)
    if stars:
        _draw_overlay_stars(surf, _STARS, t)


# ── the converged card ───────────────────────────────────────────────────────

def _card(surf, sid, rect, equipped, secret, t, *, bar_intensity=1.0,
          gem_corner="tl", bezel_weight=1):
    """OBSIDIAN & GOLD card: obsidian top-lit body, FINE gold inner bezel, a
    rarity SHELF-LIGHT BAR at the base (primary cue), an inset GEM BADGE in a
    top corner (secondary), and the thumbnail on a clean dark inset disc. The
    three sub-variants tune bar_intensity / gem_corner / bezel_weight only."""
    tier = store_catalog.rarity(sid)
    _drop_shadow(surf, rect, 13, blur=6, alpha=140)
    body = _vgrad_panel(rect.w, rect.h, 13, _OBS_TOP, _OBS_BOT, alpha=252)
    surf.blit(body, rect.topleft)

    # Fine gold inner bezel — thin, crisp, luxe jeweller (not a fat outline).
    inner = rect.inflate(-7, -7)
    pygame.draw.rect(surf, (*_GOLD_DEEP, 210), inner, width=bezel_weight,
                     border_radius=8)
    # faint top sheen, sells the top-lit obsidian.
    sheen = pygame.Surface((rect.w - 10, 16), pygame.SRCALPHA)
    for y in range(16):
        a = int(30 * (1 - y / 16))
        pygame.draw.line(sheen, (255, 255, 255, a), (0, y), (rect.w - 10, y))
    surf.blit(sheen, (rect.x + 5, rect.y + 4))

    # Rarity shelf-light bar (PRIMARY cue), unless secret (mystery glow).
    _shelf_bar(surf, rect, tier, intensity=bar_intensity, mystery=secret)

    # Thumbnail on a clean dark inset disc — the hero, brightest thing on card.
    disc_cy = rect.y + 34
    _inset_disc(surf, rect.centerx, disc_cy, 26)
    if secret:
        _draw_qmark(surf, rect.centerx, disc_cy, 36, UI_CREAM, NEAR_BLACK,
                    thick=2)
        name = "???"
    else:
        th = _fit_skin(sid, 44)
        surf.blit(th, th.get_rect(center=(rect.centerx, disc_cy)))
        name = _disp_name(sid)

    # Legendary-only gold leaf flourish in the opposite top corner — a tiny
    # luxe accent, kept faint so it never competes with the thumbnail.
    if tier == "legendary" and not secret:
        lx = rect.right - 13 if gem_corner == "tl" else rect.x + 13
        _gold_leaf(surf, lx, rect.y + 12, -1 if gem_corner == "tl" else 1)

    # Inset gem badge in a top corner (SECONDARY cue).
    gx = rect.x + 15 if gem_corner == "tl" else rect.right - 15
    _gem(surf, gx, rect.y + 15, 6, tier, t, mystery=secret)

    nimg = _font(13, True).render(name, True, _GOLD_PALE)
    nsh = _font(13, True).render(name, True, NEAR_BLACK)
    nsh.set_alpha(150)
    nr = nimg.get_rect(center=(rect.centerx, rect.y + 62))
    surf.blit(nsh, (nr.x + 1, nr.y + 1))
    surf.blit(nimg, nr)

    _state_chip(surf, sid, rect.centerx, rect.y + 82, equipped, secret)

    # Equipped rim around the WHOLE card so it reads across the grid. A thin
    # gold frame + a faint edge-only halo (NOT a fill bloom) so the rim sits
    # above the gem in the glow hierarchy but never washes the card content.
    if equipped:
        halo = pygame.Surface((rect.w + 16, rect.h + 16), pygame.SRCALPHA)
        for k in range(4, 0, -1):
            a = int(20 * k / 4)
            pygame.draw.rect(halo, (*_GOLD_BRIGHT, a),
                             (8 - k, 8 - k, rect.w + 2 * k, rect.h + 2 * k),
                             width=2, border_radius=13 + k)
        surf.blit(halo, (rect.x - 8, rect.y - 8),
                  special_flags=pygame.BLEND_ADD)
        pygame.draw.rect(surf, lerp_color(_GOLD_BRIGHT, NEAR_BLACK, 0.4), rect,
                         width=2, border_radius=13)
        pygame.draw.rect(surf, _GOLD_BRIGHT, rect.inflate(-2, -2), width=1,
                         border_radius=12)


# ── sample cards (real items spanning all tiers + equipped + secret) ─────────

def _sample_cards():
    cos = sorted(store_catalog.ids_of_group("costume"), key=store_catalog.cost)
    ani = sorted(store_catalog.ids_of_group("animal"), key=store_catalog.cost)
    return [
        (cos[0], True, False),             # common, equipped
        (cos[3], False, False),            # common
        (ani[0], False, False),            # rare
        (ani[5], False, False),            # rare
        (ani[11], False, False),           # epic
        (ani[16], False, False),           # epic (expensive -> locked? balance huge)
        (ani[18], False, False),           # legendary
        ("skin_ufo", False, True),         # secret
    ]


# layout (2x4 grid)
_CARD_W = 162
_CARD_H = 100
_GAP = 8
_GRID_TOP = 120


def _grid_rects():
    base_x = (W - (_CARD_W * 2 + _GAP)) // 2
    rects = []
    for idx in range(8):
        col, row = idx % 2, idx // 2
        x = base_x + col * (_CARD_W + _GAP)
        y = _GRID_TOP + row * (_CARD_H + _GAP)
        rects.append(pygame.Rect(x, y, _CARD_W, _CARD_H))
    return base_x, rects


# ── chrome: header, tab strip, page, back ────────────────────────────────────

def _balance_header(surf, cx, y):
    """Luxe recessed gold capsule + gradient-gold digits. BALANCE microcopy
    dropped; coin gets ~6px breathing room from digits; the + is a clear round
    tappable button. The balance coin is the BRIGHTEST glow on the screen."""
    val = "12,480"
    vf = _font(22, True)
    vimg_w = vf.size(val)[0]
    coin_d = 24
    plus_d = 26
    gap_coin = 9
    pad = 14
    inner = coin_d + gap_coin + vimg_w + 12 + plus_d
    w = inner + pad * 2
    cap = pygame.Rect(cx - w // 2, y - 18, w, 36)
    _drop_shadow(surf, cap, 18, blur=4, alpha=90)
    body = _vgrad_panel(cap.w, cap.h, 18, (44, 32, 18), (20, 14, 8), alpha=252)
    surf.blit(body, cap.topleft)
    # recessed inner shadow lip (top) + gold rim.
    pygame.draw.rect(surf, (0, 0, 0, 120), cap.inflate(-2, -2), width=1,
                     border_radius=17)
    pygame.draw.rect(surf, (*_GOLD_BRIGHT, 190), cap, width=1, border_radius=18)
    x = cap.x + pad
    # brightest glow in the whole scene.
    _soft_glow(surf, x + coin_d // 2, y, coin_d + 4, (255, 206, 92), 110,
               layers=5)
    _coin_icon(surf, x + coin_d // 2, y, coin_d // 2)
    x += coin_d + gap_coin
    _gradient_text(surf, val, vf, (x + vimg_w // 2, y),
                   (255, 246, 196), (236, 170, 60), shadow=True)
    x += vimg_w + 12
    # round + add-coins button.
    addr = pygame.Rect(x, y - plus_d // 2, plus_d, plus_d)
    _soft_glow(surf, addr.centerx, addr.centery, plus_d // 2 + 2,
               (255, 200, 80), 38, layers=3)
    grad = _vgrad_panel(plus_d, plus_d, plus_d // 2,
                        lerp_color(_GOLD_BRIGHT, WHITE, 0.2), _GOLD_DEEP)
    surf.blit(grad, addr.topleft)
    pygame.draw.circle(surf, _GOLD_PALE, addr.center, plus_d // 2, 1)
    pimg = _font(20, True).render("+", True, (40, 24, 8))
    surf.blit(pimg, pimg.get_rect(center=(addr.centerx, addr.centery - 1)))


def _daily_pill(surf):
    f = _font(12, True)
    lbl = f.render("DAILY", True, (28, 18, 8))
    timg = f.render("+50", True, (28, 18, 8))
    w = lbl.get_width() + 6 + timg.get_width() + 22
    r = pygame.Rect(W - 12 - w, 14, w, 24)
    body = _vgrad_panel(r.w, r.h, 11, (255, 215, 120), _GOLD_DEEP, alpha=255)
    surf.blit(body, r.topleft)
    pygame.draw.rect(surf, (*_GOLD_BRIGHT, 200), r, width=1, border_radius=11)
    surf.blit(lbl, lbl.get_rect(midleft=(r.x + 11, r.centery)))
    surf.blit(timg, timg.get_rect(midleft=(r.x + 11 + lbl.get_width() + 6,
                                           r.centery)))


def _title(surf):
    f = _font(28, True)
    out = f.render("STORE", True, _RED_OUTLINE)
    r = f.render("STORE", True, WHITE).get_rect(center=(W // 2, 30))
    for ox, oy in ((-2, 0), (2, 0), (0, -2), (0, 2),
                   (-2, -2), (2, -2), (-2, 2), (2, 2)):
        surf.blit(out, (r.x + ox, r.y + oy))
    sh = f.render("STORE", True, NEAR_BLACK)
    sh.set_alpha(160)
    surf.blit(sh, (r.x + 2, r.y + 3))
    _gradient_text(surf, "STORE", f, (W // 2, 30),
                   (255, 240, 180), (236, 170, 60), shadow=False)


def _header(surf):
    _title(surf)
    _balance_header(surf, W // 2, 66)
    _daily_pill(surf)


def _tabstrip(surf, active, t):
    """ONE consistent active treatment: gold underline + brighter label on
    active, dimmed inactive; even spacing; no pills (clean, tactile). Tab labels
    are evenly distributed across the full width so it feels intentional."""
    y = 100
    f = _font(11, True)
    n = len(_TABS)
    # even cell distribution; reserve the right edge for the more-tabs chevron.
    left, right = 12, W - 24
    cell = (right - left) / n
    for i, lbl in enumerate(_TABS):
        on = (i == active)
        col = _GOLD_BRIGHT if on else (150, 142, 158)
        timg = f.render(lbl, True, col)
        if not on:
            timg.set_alpha(170)
        cxp = int(left + cell * (i + 0.5))
        tr = timg.get_rect(center=(cxp, y))
        surf.blit(timg, tr)
        if on:
            ur = pygame.Rect(tr.x - 2, y + 11, tr.w + 4, 3)
            # A short, low under-glow hugging the bar — a lit underline, not a
            # sunburst (keeps the tab label readable and the glow budget lean).
            uglow = pygame.Surface((ur.w + 12, 10), pygame.SRCALPHA)
            for gy in range(10):
                a = int(40 * (1 - gy / 10))
                pygame.draw.line(uglow, (255, 200, 80, a), (0, gy),
                                 (ur.w + 12, gy))
            surf.blit(uglow, (ur.x - 6, ur.y - 2),
                      special_flags=pygame.BLEND_ADD)
            rounded_rect(surf, ur, 2, _GOLD_BRIGHT)
    # right-edge chevron affordance (more tabs).
    cx = W - 14
    pts = [(cx - 4, y - 5), (cx + 1, y), (cx - 4, y + 5)]
    pygame.draw.lines(surf, (*_GOLD_PALE, 220), False, pts, 2)


def _page_controls(surf, base_x, page, n_pages):
    w = _CARD_W * 2 + _GAP
    y = _GRID_TOP + 4 * (_CARD_H + _GAP)
    cy = y + 10
    lbl = _font(12, True).render(f"PAGE  {page + 1} / {n_pages}", True,
                                 _GOLD_PALE)
    surf.blit(lbl, lbl.get_rect(center=(base_x + w // 2, cy)))
    for cx, glyph, on in ((base_x + 16, "<", page > 0),
                          (base_x + w - 16, ">", page < n_pages - 1)):
        r = pygame.Rect(0, 0, 30, 22)
        r.center = (cx, cy)
        rounded_rect(surf, r, 11, _GOLD_DEEP if on else (54, 48, 58))
        pygame.draw.rect(surf, _GOLD_BRIGHT if on else (88, 80, 90), r,
                         width=1, border_radius=11)
        g = _font(15, True).render(glyph, True,
                                   _GOLD_PALE if on else (140, 132, 146))
        surf.blit(g, g.get_rect(center=(cx, cy - 1)))


def _back_pill(surf):
    r = pygame.Rect(0, 0, 160, 36)
    r.center = (W // 2, H - 26)
    _drop_shadow(surf, r, 18, blur=4, alpha=90)
    body = _vgrad_panel(r.w, r.h, 18, (40, 32, 56), (22, 16, 38), alpha=240)
    surf.blit(body, r.topleft)
    pygame.draw.rect(surf, (*_GOLD_BRIGHT, 185), r, width=1, border_radius=18)
    timg = _font(18, True).render("BACK", True, _GOLD_PALE)
    surf.blit(timg, timg.get_rect(center=r.center))


# ── full-screen sub-variant ──────────────────────────────────────────────────

def render_store(surf, t=2.0, *, bar_intensity=1.0, gem_corner="tl",
                 bezel_weight=1, aurora=False):
    _bg(surf, [(8, 8, 24), (12, 12, 36), (18, 16, 48), (24, 20, 58)], t,
        aurora=aurora)
    _header(surf)
    _tabstrip(surf, active=2, t=t)
    base_x, rects = _grid_rects()
    for (sid, eq, sec), rect in zip(_sample_cards(), rects):
        _card(surf, sid, rect, eq, sec, t, bar_intensity=bar_intensity,
              gem_corner=gem_corner, bezel_weight=bezel_weight)
    _page_controls(surf, base_x, 1, 3)
    _back_pill(surf)


# ── detail callouts ──────────────────────────────────────────────────────────

def _big_card(surf, ox, oy, sid, equipped=False, secret=False, scale=1.7,
              label=None):
    # Dedicated taller proportions so disc + name + chip all seat INSIDE the
    # card with the shelf-bar clear at the base. (The grid card is shorter; the
    # callout trades that height for legibility at scale.)
    cw, ch = int(_CARD_W * scale), 196
    rect = pygame.Rect(ox, oy, cw, ch)
    tier = store_catalog.rarity(sid)
    _drop_shadow(surf, rect, 18, blur=6, alpha=140)
    body = _vgrad_panel(cw, ch, 18, _OBS_TOP, _OBS_BOT, alpha=252)
    surf.blit(body, rect.topleft)
    inner = rect.inflate(-12, -12)
    pygame.draw.rect(surf, (*_GOLD_DEEP, 215), inner, width=1, border_radius=12)
    sheen = pygame.Surface((cw - 14, 24), pygame.SRCALPHA)
    for y in range(24):
        a = int(32 * (1 - y / 24))
        pygame.draw.line(sheen, (255, 255, 255, a), (0, y), (cw - 14, y))
    surf.blit(sheen, (rect.x + 7, rect.y + 6))
    _shelf_bar(surf, rect, tier, intensity=1.0, mystery=secret)
    disc_r = 42
    disc_cy = rect.y + 16 + disc_r
    _inset_disc(surf, rect.centerx, disc_cy, disc_r)
    if secret:
        _draw_qmark(surf, rect.centerx, disc_cy, 58, UI_CREAM,
                    NEAR_BLACK, thick=3)
        name = "???"
    else:
        th = _fit_skin(sid, 72)
        surf.blit(th, th.get_rect(center=(rect.centerx, disc_cy)))
        name = _disp_name(sid)
    _gem(surf, rect.x + 18, rect.y + 18, 8, tier, mystery=secret)
    nimg = _font(17, True).render(name, True, _GOLD_PALE)
    nsh = _font(17, True).render(name, True, NEAR_BLACK)
    nsh.set_alpha(150)
    nr = nimg.get_rect(center=(rect.centerx, disc_cy + disc_r + 18))
    surf.blit(nsh, (nr.x + 1, nr.y + 1))
    surf.blit(nimg, nr)
    # Chip seats clear above the base shelf-bar.
    _state_chip(surf, sid, rect.centerx, rect.bottom - 28, equipped,
                secret, h=30)
    if equipped:
        halo = pygame.Surface((cw + 20, ch + 20), pygame.SRCALPHA)
        for k in range(5, 0, -1):
            a = int(18 * k / 5)
            pygame.draw.rect(halo, (*_GOLD_BRIGHT, a),
                             (10 - k, 10 - k, cw + 2 * k, ch + 2 * k),
                             width=2, border_radius=18 + k)
        surf.blit(halo, (rect.x - 10, rect.y - 10),
                  special_flags=pygame.BLEND_ADD)
        pygame.draw.rect(surf, lerp_color(_GOLD_BRIGHT, NEAR_BLACK, 0.4), rect,
                         width=3, border_radius=18)
        pygame.draw.rect(surf, _GOLD_BRIGHT, rect.inflate(-3, -3), width=1,
                         border_radius=16)
    cap = label or (tier.upper() if not secret else "MYSTERY")
    col = (RARITY[tier]["gem"] if not secret else MYSTERY["gem"])
    lab = _font(13, True).render(cap, True, col)
    surf.blit(lab, lab.get_rect(center=(rect.centerx, rect.bottom + 14)))


def _modal(surf, ox, oy, sid, scrim_w=300, scrim_h=330):
    """Rebuilt buy-confirmation modal on a clean centred grid: thumbnail top ->
    name -> single price chip -> two-button row (BUY gold / CANCEL brushed-dark)
    with a clear gutter. Scrim darkened to ~70%. Nothing clipped."""
    region = pygame.Rect(ox, oy, scrim_w, scrim_h)
    bg = _vgrad_panel(scrim_w, scrim_h, 0, (16, 14, 44), (26, 18, 58))
    surf.blit(bg, region.topleft)
    _draw_overlay_stars(surf, _STARS, 3.0) if False else None
    scrim = pygame.Surface((scrim_w, scrim_h), pygame.SRCALPHA)
    scrim.fill((4, 4, 10, 180))  # ~70% black
    surf.blit(scrim, region.topleft)

    tier = store_catalog.rarity(sid)
    pw, ph = 244, 268
    panel = pygame.Rect(ox + (scrim_w - pw) // 2, oy + (scrim_h - ph) // 2,
                        pw, ph)
    _drop_shadow(surf, panel, 18, blur=8, alpha=170)
    body = _vgrad_panel(pw, ph, 18, (28, 24, 38), (12, 10, 22), alpha=255)
    surf.blit(body, panel.topleft)
    pygame.draw.rect(surf, lerp_color(_GOLD_BRIGHT, NEAR_BLACK, 0.45), panel,
                     width=2, border_radius=18)
    pygame.draw.rect(surf, (*_GOLD_BRIGHT, 230), panel.inflate(-2, -2), width=1,
                     border_radius=16)

    # centred grid: header / disc+thumb / name / price chip / button row.
    cx = panel.centerx
    head = _font(13, True).render("CONFIRM PURCHASE", True, _GOLD_PALE)
    surf.blit(head, head.get_rect(center=(cx, panel.y + 24)))
    pygame.draw.line(surf, (*_GOLD_DEEP, 150), (panel.x + 28, panel.y + 40),
                     (panel.right - 28, panel.y + 40), 1)

    disc_cy = panel.y + 86
    _inset_disc(surf, cx, disc_cy, 40)
    # the rarity shelf-bar language echoed as a thin lit strip under the disc —
    # a seated vitrine light, deliberately narrow so it doesn't wash the name.
    sb = pygame.Rect(cx - 38, disc_cy + 40, 76, 3)
    bglow = pygame.Surface((sb.w + 8, 10), pygame.SRCALPHA)
    for gy in range(10):
        a = int(34 * (1 - gy / 10))
        pygame.draw.line(bglow, (*RARITY[tier]["glow"], a), (0, gy),
                         (sb.w + 8, gy))
    surf.blit(bglow, (sb.x - 4, sb.y - 6), special_flags=pygame.BLEND_ADD)
    rounded_rect(surf, sb, 2, RARITY[tier]["gem"])
    th = _fit_skin(sid, 62)
    surf.blit(th, th.get_rect(center=(cx, disc_cy)))
    _gem(surf, cx + 46, disc_cy - 30, 7, tier, inset=False)

    nimg = _font(17, True).render(_disp_name(sid), True, _GOLD_BRIGHT)
    surf.blit(nimg, nimg.get_rect(center=(cx, panel.y + 144)))
    rword = _font(11, True).render(tier.upper(), True, RARITY[tier]["gem"])
    surf.blit(rword, rword.get_rect(center=(cx, panel.y + 162)))

    _chip(surf, cx, panel.y + 186, f"{store_catalog.cost(sid):,}", "price",
          coin=True, h=28)

    # two-button row with a clear gutter, both fully inside the panel.
    bw, bh = 100, 38
    gutter = 16
    by = panel.bottom - 30
    total = bw * 2 + gutter
    nx = cx - total // 2
    yx = nx + bw + gutter
    cancel = pygame.Rect(nx, by - bh // 2, bw, bh)
    buy = pygame.Rect(yx, by - bh // 2, bw, bh)
    # CANCEL — brushed-dark, same rim family.
    cb = _vgrad_panel(bw, bh, bh // 2, (70, 62, 80), (44, 38, 56))
    surf.blit(cb, cancel.topleft)
    pygame.draw.rect(surf, (126, 116, 138), cancel, width=1,
                     border_radius=bh // 2)
    ct = _font(14, True).render("CANCEL", True, UI_CREAM)
    surf.blit(ct, ct.get_rect(center=cancel.center))
    # BUY — gradient gold with a tight edge glow (no big bloom past the panel).
    bglow2 = pygame.Surface((bw + 10, bh + 10), pygame.SRCALPHA)
    for k in range(4, 0, -1):
        a = int(22 * k / 4)
        pygame.draw.rect(bglow2, (255, 200, 80, a),
                         (5 - k, 5 - k, bw + 2 * k, bh + 2 * k),
                         border_radius=bh // 2 + k)
    surf.blit(bglow2, (buy.x - 5, buy.y - 5), special_flags=pygame.BLEND_ADD)
    yb = _vgrad_panel(bw, bh, bh // 2, lerp_color(_GOLD_BRIGHT, WHITE, 0.2),
                      _GOLD_DEEP)
    surf.blit(yb, buy.topleft)
    pygame.draw.rect(surf, _GOLD_PALE, buy, width=1, border_radius=bh // 2)
    yt = _font(15, True).render("BUY", True, (40, 24, 8))
    surf.blit(yt, yt.get_rect(center=buy.center))


# ── compose the sheet ────────────────────────────────────────────────────────

def main():
    pad = 24
    label_h = 30
    cols = 3
    sheet_w = pad + cols * (W + pad)
    detail_h = 700
    sheet_h = label_h + pad + H + pad + label_h + detail_h + pad

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((16, 14, 24))

    title = _font(20, True).render(
        "SKYBIT  COIN STORE  —  REDESIGN  ROUND 2  (converged: OBSIDIAN & GOLD"
        " + shelf-bar + inset gem)", True, _GOLD_BRIGHT)
    sheet.blit(title, (pad, 6))

    variants = [
        ("A  SUBTLE  (low bar / TL gem / 1px bezel)",
         dict(bar_intensity=0.7, gem_corner="tl", bezel_weight=1,
              aurora=False)),
        ("B  BALANCED  (med bar / TR gem / 1px bezel + aurora)",
         dict(bar_intensity=1.0, gem_corner="tr", bezel_weight=1,
              aurora=True)),
        ("C  VITRINE  (bold bar / TL gem / 2px bezel)",
         dict(bar_intensity=1.35, gem_corner="tl", bezel_weight=2,
              aurora=False)),
    ]

    for i, (name, kw) in enumerate(variants):
        screen = pygame.Surface((W, H), pygame.SRCALPHA)
        render_store(screen, t=2.0 + i * 0.7, **kw)
        x = pad + i * (W + pad)
        y = label_h + pad
        pygame.draw.rect(sheet, (40, 36, 54),
                         (x - 3, y - 3, W + 6, H + 6), border_radius=6)
        sheet.blit(screen, (x, y))
        lbl = _font(15, True).render(f"{name}", True, _GOLD_PALE)
        sheet.blit(lbl, (x + 2, label_h - 4))

    # ── detail callouts ──
    dy = label_h + pad + H + pad
    dlabel = _font(18, True).render(
        "DETAIL CALLOUTS", True, _GOLD_BRIGHT)
    sheet.blit(dlabel, (pad, dy - 26))

    cos = sorted(store_catalog.ids_of_group("costume"), key=store_catalog.cost)
    ani = sorted(store_catalog.ids_of_group("animal"), key=store_catalog.cost)

    # Row A: the 4 rarity tiers + equipped + secret at big scale.
    cards = [
        (cos[0], False, False),       # common
        (ani[0], False, False),       # rare
        (ani[11], False, False),      # epic
        (ani[18], False, False),      # legendary
        (cos[1], True, False),        # equipped
        ("skin_ufo", False, True),    # secret
    ]
    scale = 1.15
    cw = int(_CARD_W * scale)
    n = len(cards)
    row_gap = (sheet_w - 2 * pad - n * cw) // (n - 1)
    cx = pad
    row_y = dy + 8
    rowa_lbl = _font(13, True).render(
        "RARITY TIERS  +  EQUIPPED CARD-RIM  +  TAMED SECRET (mystery gem)",
        True, _GOLD_PALE)
    sheet.blit(rowa_lbl, (pad, row_y - 4))
    row_y += 16
    for sid, eq, sec in cards:
        _big_card(sheet, cx, row_y, sid, equipped=eq, secret=sec, scale=scale)
        cx += cw + row_gap

    # Row B: unified chips | balance header | tab strip | modal.
    by = row_y + 196 + 50
    col_x = pad

    # unified chip family.
    clbl = _font(13, True).render(
        "UNIFIED CHIPS", True, _GOLD_PALE)
    sheet.blit(clbl, (col_x, by - 4))
    csurf = pygame.Surface((260, 120), pygame.SRCALPHA)
    _chip(csurf, 70, 24, "1,200", "price", coin=True, h=30)
    _chip(csurf, 190, 24, "EQUIP", "equip", h=30)
    _chip(csurf, 80, 66, "EQUIPPED", "equipped", h=30)
    _chip(csurf, 200, 66, "9,000", "locked", lock=True, h=30)
    sheet.blit(csurf, (col_x, by + 16))
    sub = _font(11, True).render(
        "price / equip / equipped / can't-afford (desat-gold + lock)",
        True, (190, 178, 150))
    sheet.blit(sub, (col_x, by + 16 + 100))

    # balance header.
    col_x = pad + 300
    blbl = _font(13, True).render("BALANCE HEADER", True, _GOLD_PALE)
    sheet.blit(blbl, (col_x, by - 4))
    bsurf = pygame.Surface((360, 70), pygame.SRCALPHA)
    _balance_header(bsurf, 180, 36)
    sheet.blit(bsurf, (col_x - 4, by + 28))

    # tab strip.
    tlbl = _font(13, True).render("TAB STRIP", True, _GOLD_PALE)
    sheet.blit(tlbl, (col_x, by + 96))
    tsurf = pygame.Surface((W, 40), pygame.SRCALPHA)
    tbg = _vgrad_panel(W, 40, 8, (14, 12, 36), (18, 16, 46))
    tsurf.blit(tbg, (0, 0))
    # _tabstrip draws at y=100; capture the y∈[84,124] band.
    full = pygame.Surface((W, 160), pygame.SRCALPHA)
    full.blit(_vgrad_panel(W, 160, 8, (14, 12, 36), (18, 16, 46)), (0, 0))
    _tabstrip(full, active=2, t=2.0)
    band = full.subsurface(pygame.Rect(0, 84, W, 36)).copy()
    sheet.blit(band, (col_x - 4, by + 116))

    # buy-confirm modal.
    col_x = pad + 740
    mlbl = _font(13, True).render("BUY-CONFIRM MODAL", True, _GOLD_PALE)
    sheet.blit(mlbl, (col_x, by - 4))
    _modal(sheet, col_x, by + 16, ani[18])

    out = os.path.join(_HERE, "round_2.png")
    pygame.image.save(sheet, out)
    print("saved:", out)
    print("sheet size:", sheet.get_size())


if __name__ == "__main__":
    main()
