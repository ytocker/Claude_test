"""
Coin Store — spend banked coins on cosmetics.

Reached from the menu's STORE pill (STATE_STORE). The wallet that backs it
(game/store_data.py) banks each run's coins at death, so the balance shown
here grows as the player flies.

This module owns the whole frame for STATE_STORE. The App's `_render` hands
it the screen surface; the App's `_flap_input` routes taps *into*
`handle_tap`, which returns an action token ("back" / None) — the store is
interactive, so taps are dispatched here rather than blanket-dismissing the
screen like the one-tap help explainer.

Visual language ("Obsidian & Gold", art-director locked spec B+): obsidian
top-lit cards on a night-sky gradient, a fine gold inner bezel, a rarity
SHELF-LIGHT BAR glowing up from each card base (the primary tier cue), a small
inset faceted GEM badge (secondary), the procedural thumbnail on a clean dark
inset disc, and a luxe gold balance capsule. Rarity reads by HUE *and* VALUE so
the four tiers + the mystery state stay colourblind-safe.
"""
from __future__ import annotations

import math
import pygame

from game.config import W, H
from game.hud import _font, _draw_overlay_stars, \
    _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP, _RED_OUTLINE
from game.draw import UI_CREAM, NEAR_BLACK, WHITE, rounded_rect, lerp_color
from game.powerup_help import _seeded_stars
from game import parrot
from game import store_catalog
from game import store_data
from game import store_cards
from game.surprise_box_variants import _draw_qmark

# Card grid metrics (2 columns). Thumbnails are pre-rendered once so the
# per-frame cost is a flat blit rather than eight smoothscales.
_CARD_W = 162
_CARD_H = 100
_GAP = 8
_GRID_TOP = 116        # leaves room for the title + balance + tab bar above
_THUMB_BOX = 48
_PER_PAGE = 8          # 2 columns x 4 rows; each tab pages independently

_TAB_Y = 92            # tab-bar centre line
_TABS = (("COSTUMES", "costume"), ("PARROTS", "parrot"),
         ("ANIMALS", "animal"), ("SHOES", "shoes"), ("HATS", "hats"),
         ("SHADES", "shades"), ("PARCELS", "parcels"))
# Stall group -> tab index, so a tap on a lagoon-hub stall lands on that
# category's grid. Keyed on the same group ids the hub returns its rects under.
_GROUP_TAB = {g: i for i, (_label, g) in enumerate(_TABS)}

# Night-sky gradient stops the obsidian cards were tuned against.
_BG_STOPS = ((8, 8, 24), (12, 12, 36), (18, 16, 48), (24, 20, 58))

# Obsidian card body stops — near-black, subtly top-lit (never rarity-tinted).
_OBS_TOP = (26, 24, 32)
_OBS_BOT = (9, 8, 15)

# ── rarity language (locked spec) ────────────────────────────────────────────
# The four tiers + the mystery state separate by HUE *and* VALUE so they survive
# grayscale (colourblind-safe). Both the shelf-bar and the gem pull the same
# per-tier triplet so a card reads as one jewel. Grayscale ladder (gem luma):
# epic < common < rare < legendary < mystery — five separable steps, brightest
# reserved for the un-tiered mystery.
_RARITY = {
    "common":    {"gem": (208, 178, 132), "glow": (196, 162, 110), "deep": (96, 74, 44)},
    "rare":      {"gem": (96, 196, 240),  "glow": (64, 172, 230),  "deep": (20, 78, 116)},
    "epic":      {"gem": (190, 104, 236), "glow": (170, 78, 232),  "deep": (70, 28, 104)},
    "legendary": {"gem": (255, 168, 56),  "glow": (255, 138, 30),  "deep": (132, 64, 10)},
}
# MYSTERY (secret ???): neutral iridescent silver — highest value, no saturated
# hue, so it claims NO tier and never collides with RARE's blue.
_MYSTERY = {"gem": (214, 218, 224), "glow": (176, 196, 214), "deep": (78, 84, 98)}

# Unified chip family: one pill silhouette + hairline rim for every state; only
# the fill + content differ. The can't-afford "locked" chip is dark cool slate-
# blue (never warm gold) so it can't be mistaken for the EQUIP chip.
_CHIP_STATES = {
    "price":    {"fg": _GOLD_PALE,     "bg": _GOLD_DEEP,     "rim": (*_GOLD_BRIGHT, 150)},
    "equip":    {"fg": UI_CREAM,       "bg": (96, 74, 24),   "rim": (*_GOLD_BRIGHT, 150)},
    "equipped": {"fg": (10, 30, 14),   "bg": (84, 196, 112), "rim": (200, 255, 210, 200)},
    "locked":   {"fg": (150, 166, 190), "bg": (40, 46, 62),  "rim": (88, 102, 132, 180)},
}


# ── cached primitives (the store is a menu screen; cache the heavy builds) ────
_panel_cache: dict = {}
_disc_cache: dict = {}
_shelf_cache: dict = {}
_coin_cache: dict = {}


def _vgrad_panel(w, h, radius, top, bot, alpha=255):
    """Rounded vertical-gradient panel (top brighter), corner-masked. Cached by
    args — every card shares one body surface, so this builds once."""
    key = (w, h, radius, top, bot, alpha)
    cached = _panel_cache.get(key)
    if cached is not None:
        return cached
    body = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        c = lerp_color(top, bot, y / max(1, h - 1))
        pygame.draw.line(body, (*c, alpha), (0, y), (w - 1, y))
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h), border_radius=radius)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    _panel_cache[key] = body
    return body


def _coin_glyph(surf, cx, cy, r):
    """The one coin used everywhere (price chip, balance, modal): a flat-gold
    disc with a single diagonal bevel + a stamped "$" — no gear teeth (those
    read as muddy noise at chip scale). Cached per radius."""
    key = int(r)
    face = _coin_cache.get(key)
    if face is None:
        d = r * 2
        face = pygame.Surface((d + 2, d + 2), pygame.SRCALPHA)
        c = r + 1
        for yy in range(d + 2):
            for xx in range(d + 2):
                dx, dy = xx - c, yy - c
                if dx * dx + dy * dy > r * r:
                    continue
                diag = (dx + dy) / (2 * r) + 0.5
                col = lerp_color((255, 230, 150), (188, 132, 30),
                                 max(0.0, min(1.0, diag)) ** 0.85)
                face.set_at((xx, yy), (*col, 255))
        pygame.draw.circle(face, (*_GOLD_DEEP, 230), (c, c), r, 1)
        hl = pygame.Surface((d + 2, d + 2), pygame.SRCALPHA)
        pygame.draw.circle(hl, (255, 250, 220, 220), (c, c),
                           max(1, r - 2), max(1, r // 6))
        for yy in range(d + 2):
            for xx in range(d + 2):
                if (xx - c) + (yy - c) > -r * 0.45:
                    hl.set_at((xx, yy), (0, 0, 0, 0))
        face.blit(hl, (0, 0))
        sf = _font(max(9, int(r * 1.5)), True)
        face.blit(sf.render("$", True, (120, 80, 16)),
                  sf.render("$", True, (120, 80, 16)).get_rect(center=(c, c)))
        sg2 = sf.render("$", True, (255, 238, 180))
        face.blit(sg2, sg2.get_rect(center=(c, c - 1)))
        _coin_cache[key] = face
    surf.blit(face, face.get_rect(center=(cx, cy)))


def _soft_glow(surf, cx, cy, radius, color, peak_alpha, layers=6):
    """Layered additive bloom — cheap (no per-pixel) so elements emit light."""
    for i in range(layers, 0, -1):
        r = int(radius * i / layers)
        a = int(peak_alpha * (1 - (i - 1) / layers) ** 1.7)
        if r <= 0 or a <= 0:
            continue
        g = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(g, (*color, a), (r + 1, r + 1), r)
        surf.blit(g, (cx - r - 1, cy - r - 1), special_flags=pygame.BLEND_ADD)


def _drop_shadow(surf, rect, radius, blur=6, alpha=120, dy=4):
    """Soft drop shadow under a card."""
    for i in range(blur, 0, -1):
        a = int(alpha * (i / blur) ** 2 / blur * 2.2)
        if a <= 0:
            continue
        r = pygame.Rect(rect.x - i, rect.y - i + dy, rect.w + 2 * i, rect.h + 2 * i)
        s = pygame.Surface(r.size, pygame.SRCALPHA)
        pygame.draw.rect(s, (0, 0, 0, a), s.get_rect(), border_radius=radius + i)
        surf.blit(s, r.topleft)


def _inset_disc(surf, cx, cy, r, tint=(6, 6, 12)):
    """A clean dark inset disc for the thumbnail (never rarity-tinted). Cached."""
    key = (r, tint)
    disc = _disc_cache.get(key)
    if disc is None:
        disc = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        for i in range(r, 0, -1):
            c = lerp_color((30, 28, 40), tint, (i / r) ** 1.3)
            pygame.draw.circle(disc, (*c, 255), (r + 1, r + 1), i)
        pygame.draw.circle(disc, (0, 0, 0, 130), (r + 1, r + 1), r, 2)
        pygame.draw.circle(disc, (*_GOLD_DEEP, 60), (r + 1, r + 1), r - 1, 1)
        _disc_cache[key] = disc
    surf.blit(disc, (cx - r - 1, cy - r - 1))


def _shelf_bar(surf, rect, tier, intensity=1.0, mystery=False):
    """The rarity SHELF-LIGHT BAR along the card base — an additive horizontal
    gradient strip in the tier colour that glows UP into the body like a vitrine
    light. PRIMARY rarity cue. Cached per (width, tier)."""
    bw = rect.w - 28
    key = (bw, "mystery" if mystery else tier, round(intensity, 2))
    pair = _shelf_cache.get(key)
    if pair is None:
        pal = _MYSTERY if mystery else _RARITY[tier]
        glow, gem = pal["glow"], pal["gem"]
        wash_h = int(10 * intensity) + 6
        wash = pygame.Surface((bw, wash_h), pygame.SRCALPHA)
        peak = int(22 * intensity) + 8
        for y in range(wash_h):
            f = 1.0 - y / wash_h
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
        pair = (wash, core, wash_h)
        _shelf_cache[key] = pair
    wash, core, wash_h = pair
    bx = rect.x + 14
    by = rect.bottom - 8
    surf.blit(wash, (bx, by - wash_h + 3), special_flags=pygame.BLEND_ADD)
    surf.blit(core, (bx, by))


def _gold_leaf(surf, cx, cy, sx):
    """A tiny two-leaf gold sprig flourish for LEGENDARY cards only (faint)."""
    leaf = pygame.Surface((20, 16), pygame.SRCALPHA)
    pygame.draw.line(leaf, (*_GOLD_DEEP, 170), (10, 14), (10, 3), 1)
    pygame.draw.ellipse(leaf, (*_GOLD_BRIGHT, 150), (4, 4, 7, 9))
    pygame.draw.ellipse(leaf, (*_GOLD_BRIGHT, 150), (10, 5, 7, 9))
    if sx < 0:
        leaf = pygame.transform.flip(leaf, True, False)
    surf.blit(leaf, (cx - 10, cy - 6))


def _gem(surf, cx, cy, r, tier, t=0.0, inset=True, mystery=False):
    """Faceted rarity gem badge inset in the card corner — a three-value cut
    (lit TL, mid right, shaded BL, darker BR shadow facet) + a white specular
    pip, seated in a dark keyline well. SECONDARY rarity marker."""
    pal = _MYSTERY if mystery else _RARITY[tier]
    base, glow, deep = pal["gem"], pal["glow"], pal["deep"]
    if inset:
        seat = pygame.Surface((r * 2 + 8, r * 2 + 8), pygame.SRCALPHA)
        pygame.draw.circle(seat, (0, 0, 0, 150), (r + 4, r + 4), r + 3)
        pygame.draw.circle(seat, (*_GOLD_DEEP, 90), (r + 4, r + 4), r + 3, 1)
        surf.blit(seat, (cx - r - 4, cy - r - 4))
    _soft_glow(surf, cx, cy, int(r * 1.5), glow,
               int(70 + 30 * (0.5 + 0.5 * math.sin(t * 3))), layers=4)
    top, bot = (cx, cy - r), (cx, cy + r)
    left, right = (cx - r, cy), (cx + r, cy)
    ctr = (cx, cy)
    if mystery:
        f1 = lerp_color((196, 214, 226), (214, 202, 224), 0.5)
        hi, mid = lerp_color(f1, WHITE, 0.55), f1
        sh = lerp_color(f1, deep, 0.45)
        dk = lerp_color(deep, NEAR_BLACK, 0.25)
    else:
        hi, mid = lerp_color(base, WHITE, 0.5), base
        sh = lerp_color(base, deep, 0.5)
        dk = lerp_color(deep, NEAR_BLACK, 0.3)
    pygame.draw.polygon(surf, hi, [top, left, ctr])
    pygame.draw.polygon(surf, mid, [top, right, ctr])
    pygame.draw.polygon(surf, sh, [left, bot, ctr])
    pygame.draw.polygon(surf, dk, [right, bot, ctr])
    pygame.draw.polygon(surf, lerp_color(deep, NEAR_BLACK, 0.45),
                        [top, right, bot, left], width=1)
    pr = max(1, r // 4)
    pip = pygame.Surface((pr * 2 + 2, pr * 2 + 2), pygame.SRCALPHA)
    pygame.draw.circle(pip, (255, 255, 255, 245), (pr + 1, pr + 1), pr)
    surf.blit(pip, (cx - pr - r // 3, cy - pr - r // 3), special_flags=pygame.BLEND_ADD)


def _gold_rule(surf, x0, x1, y, peak=170):
    """A soft gold GRADIENT rule — bright at centre, fading at both ends."""
    w = x1 - x0
    line = pygame.Surface((w, 3), pygame.SRCALPHA)
    for sx in range(w):
        hx = abs(sx - w / 2) / (w / 2)
        a = int(peak * (1.0 - hx ** 1.6))
        if a <= 0:
            continue
        line.set_at((sx, 1), (*_GOLD_BRIGHT, a))
        line.set_at((sx, 0), (*_GOLD_PALE, a // 2))
        line.set_at((sx, 2), (*_GOLD_DEEP, a // 2))
    surf.blit(line, (x0, y - 1))


def _gradient_text(surf, txt, font_obj, center, top, bot, outline=None, shadow=True):
    """Vertical gold-gradient text with optional outline + drop shadow."""
    base = font_obj.render(txt, True, WHITE)
    w, h = base.get_size()
    grad = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        pygame.draw.line(grad, lerp_color(top, bot, y / max(1, h - 1)),
                         (0, y), (w, y))
    grad.blit(base, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    r = base.get_rect(center=center)
    if outline:
        out = font_obj.render(txt, True, outline)
        for ox, oy in ((-2, 0), (2, 0), (0, -2), (0, 2),
                       (-2, -2), (2, -2), (-2, 2), (2, 2)):
            surf.blit(out, (r.x + ox, r.y + oy))
    if shadow:
        sh = font_obj.render(txt, True, NEAR_BLACK)
        sh.set_alpha(150)
        surf.blit(sh, (r.x + 1, r.y + 2))
    surf.blit(grad, r.topleft)
    return r


def _lock_glyph(surf, cx, cy, col):
    """Tiny padlock for the can't-afford chip — body + shackle."""
    rounded_rect(surf, pygame.Rect(cx - 4, cy - 1, 8, 6), 2, col)
    pygame.draw.arc(surf, col, (cx - 3, cy - 6, 6, 8), 0.2, math.pi - 0.2, 2)
    surf.set_at((cx, cy + 2), (24, 28, 38))


def _chip(surf, cx, cy, text, state, coin=False, h=24, lock=False):
    """The single chip silhouette for all states: pill body (gradient), hairline
    rim, optional coin glyph or lock, centred on (cx, cy)."""
    sp = _CHIP_STATES[state]
    f = _font(max(12, int(h * 0.56)), True)
    timg = f.render(text, True, sp["fg"])
    coin_d = int(h * 0.62)
    pre_w = (coin_d + 4) if coin else (12 if lock else 0)
    pad = 12
    w = pre_w + timg.get_width() + pad * 2
    chip = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    surf.blit(_vgrad_panel(w, h, h // 2, lerp_color(sp["bg"], WHITE, 0.18),
                           sp["bg"]), chip.topleft)
    sheen_peak = 28 if state == "locked" else 46
    sheen = pygame.Surface((w - 6, h // 2), pygame.SRCALPHA)
    for y in range(h // 2):
        pygame.draw.line(sheen, (255, 255, 255, int(sheen_peak * (1 - y / (h // 2)))),
                         (0, y), (w - 6, y))
    smask = pygame.Surface((w - 6, h // 2), pygame.SRCALPHA)
    pygame.draw.rect(smask, (255, 255, 255, 255), smask.get_rect(), border_radius=h // 2)
    sheen.blit(smask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(sheen, (chip.x + 3, chip.y + 2))
    pygame.draw.rect(surf, sp["rim"], chip, width=1, border_radius=h // 2)
    x = chip.x + pad
    if coin:
        _coin_glyph(surf, x + coin_d // 2, cy, coin_d // 2)
        x += coin_d + 4
    elif lock:
        _lock_glyph(surf, x + 4, cy, sp["fg"])
        x += 12
    surf.blit(timg, timg.get_rect(midleft=(x, cy)))
    return chip


def _draw_chevron(surf, rect, direction) -> None:
    """A small ``<`` / ``>`` scroll affordance at a tab-strip edge."""
    cx, cy = rect.center
    d = direction
    pts = [(cx - 2 * d, cy - 5), (cx + 3 * d, cy), (cx - 2 * d, cy + 5)]
    pygame.draw.lines(surf, (*_GOLD_PALE, 220), False, pts, 2)


def _fit_skin(skin_id: str, box: int) -> pygame.Surface:
    """Render a skin's store thumbnail, crop to its opaque content, and fit that
    into a ``box``-square (aspect preserved). Shoes/parcels supply a product-shot
    icon via ``get_skin_icon``; everything else falls back to the in-game look."""
    src = parrot.get_skin_icon(skin_id) or parrot.get_skin_frame(skin_id, 1, 0.0)
    bb = src.get_bounding_rect()
    if bb.width > 0 and bb.height > 0:
        src = src.subsurface(bb).copy()
    sw, sh = src.get_size()
    scale = box / max(sw, sh)
    return pygame.transform.smoothscale(
        src, (max(1, int(sw * scale)), max(1, int(sh * scale))))


def _slot_of(sid: str) -> str:
    """The equip slot a store card belongs to (its catalog ``kind``), so the
    equipped-accent + tap-to-equip logic works for parcels as well as skins."""
    if sid == store_catalog.PARCEL_BASE:
        return "parcel"
    if sid == store_catalog.BASE_SKIN or not store_catalog.exists(sid):
        return "skin"
    return store_catalog.kind(sid)


class StoreScene:
    def __init__(self) -> None:
        self.t = 0.0
        # Two-level store: open onto the lagoon "hub" (a stall per category);
        # tapping a stall drills into that category's "category" grid. The hub's
        # heavy procedural backdrop is built lazily on first hub render so the
        # store-open transition isn't blocked, and is then cached process-wide.
        self.view = "hub"
        self.hub: object | None = None
        self._stars = _seeded_stars()
        self.back_rect: "pygame.Rect | None" = None
        self.item_rects: "dict[str, pygame.Rect]" = {}
        self.prev_rect: "pygame.Rect | None" = None
        self.next_rect: "pygame.Rect | None" = None
        self.tab_rects: "list[pygame.Rect]" = []
        self.tab_scroll = 0.0  # horizontal pan of the scrollable tab strip
        self.tab_chev_l: "pygame.Rect | None" = None
        self.tab_chev_r: "pygame.Rect | None" = None
        self._tab_vp = pygame.Rect(12, _TAB_Y - 13, W - 24, 26)
        self._tab_widths: "list[int]" = []
        self._tab_gap = 6
        self.daily_rect: "pygame.Rect | None" = None
        self._toast = ("", 0.0)  # (text, seconds remaining)
        # Pending buy-confirmation: the sid awaiting a CONFIRM/CANCEL, plus the
        # modal's hit rects. Coins are never spent until CONFIRM, so a stray tap
        # on an unowned card can't drain the wallet by accident.
        self._confirm: "str | None" = None
        self._confirm_panel: "pygame.Rect | None" = None
        self.confirm_yes_rect: "pygame.Rect | None" = None
        self.confirm_no_rect: "pygame.Rect | None" = None
        store_data.load()
        # Per-tab skin lists, cheapest first. PARROTS/SHADES/PARCELS are fronted
        # by a free DEFAULT card so the player can always revert.
        self._lists: "dict[str, list[str]]" = {}
        for label, g in _TABS:
            ids = sorted(store_catalog.ids_of_group(g), key=store_catalog.cost)
            if g in ("parrot", "shades"):
                ids = [store_catalog.BASE_SKIN] + ids
            elif g == "parcels":
                ids = [store_catalog.PARCEL_BASE] + ids
            self._lists[g] = ids
        self.tab = 0
        self.page = 0
        # Pre-build every thumbnail once (cropped-to-content; see _fit_skin).
        all_ids = {sid for ids in self._lists.values() for sid in ids}
        self._thumbs = {sid: _fit_skin(sid, _THUMB_BOX) for sid in all_ids}

    def _cur_ids(self) -> list:
        return self._lists[_TABS[self.tab][1]]

    @property
    def n_pages(self) -> int:
        return max(1, (len(self._cur_ids()) + _PER_PAGE - 1) // _PER_PAGE)

    @staticmethod
    def _disp_name(sid: str) -> str:
        return "DEFAULT" if sid in (store_catalog.BASE_SKIN,
                                    store_catalog.PARCEL_BASE) \
            else store_catalog.name(sid)

    def update(self, dt: float) -> None:
        self.t += dt
        text, ttl = self._toast
        if ttl > 0.0:
            self._toast = (text, max(0.0, ttl - dt))

    def _flash(self, text: str) -> None:
        self._toast = (text, 1.6)

    # ── rendering ────────────────────────────────────────────────────────────
    def render(self, surf: pygame.Surface) -> None:
        if self.view == "hub":
            self._render_hub(surf)
        else:
            self._render_category(surf)

    def _render_hub(self, surf: pygame.Surface) -> None:
        """The lagoon stilt-market landing: the cached procedural scene owns the
        STORE wordmark + balance capsule, so the chrome here is just the BACK
        affordance (which exits the store from the hub)."""
        if self.hub is None:
            from game.store_hub import LagoonHub
            self.hub = LagoonHub()
        self.hub.render(surf, store_data.balance(), self.t)
        self._draw_back(surf)

    def _render_category(self, surf: pygame.Surface) -> None:
        self._draw_bg(surf)
        self._draw_title(surf)
        self._draw_balance(surf, cx=W // 2, y=60)
        self._draw_daily(surf)
        self._draw_tabs(surf)

        base_x = (W - (_CARD_W * 2 + _GAP)) // 2
        self.item_rects = {}
        ids = self._cur_ids()
        page_skins = ids[self.page * _PER_PAGE:(self.page + 1) * _PER_PAGE]
        if not page_skins:
            msg = _font(16, True).render("COMING SOON", True, _GOLD_PALE)
            msg.set_alpha(200)
            surf.blit(msg, msg.get_rect(center=(W // 2, _GRID_TOP + 150)))
        for idx, sid in enumerate(page_skins):
            x = base_x + (idx % 2) * (_CARD_W + _GAP)
            y = _GRID_TOP + (idx // 2) * (_CARD_H + _GAP)
            rect = pygame.Rect(x, y, _CARD_W, _CARD_H)
            self.item_rects[sid] = rect
            self._draw_card(surf, sid, rect)

        grid_bot = _GRID_TOP + 4 * (_CARD_H + _GAP)
        self._draw_page_controls(surf, base_x, grid_bot - 4, _CARD_W * 2 + _GAP)

        self._draw_toast(surf)
        self._draw_back(surf)
        # The buy-confirmation overlays everything else when active.
        self._draw_confirm(surf)

    def _draw_bg(self, surf) -> None:
        n = len(_BG_STOPS)
        for y in range(H):
            f = y / (H - 1)
            seg = min(n - 2, int(f * (n - 1)))
            local = (f * (n - 1)) - seg
            pygame.draw.line(surf, lerp_color(_BG_STOPS[seg], _BG_STOPS[seg + 1],
                                              local), (0, y), (W - 1, y))
        _draw_overlay_stars(surf, self._stars, self.t + 1.4)

    def _draw_title(self, surf) -> None:
        f = _font(28, True)
        _gradient_text(surf, "STORE", f, (W // 2, 30),
                       (255, 240, 180), (236, 170, 60),
                       outline=_RED_OUTLINE, shadow=True)

    def _draw_balance(self, surf, cx, y) -> None:
        """Luxe recessed gold capsule + gradient-gold digits with the coin glyph
        — the brightest glow on the screen, per the locked glow hierarchy."""
        val = f"{store_data.balance():,}"
        vf = _font(22, True)
        vimg_w = vf.size(val)[0]
        coin_d, gap_coin, pad = 24, 9, 16
        w = coin_d + gap_coin + vimg_w + pad * 2
        cap = pygame.Rect(cx - w // 2, y - 18, w, 36)
        _drop_shadow(surf, cap, 18, blur=4, alpha=90)
        surf.blit(_vgrad_panel(cap.w, cap.h, 18, (44, 32, 18), (20, 14, 8), 252),
                  cap.topleft)
        pygame.draw.rect(surf, (0, 0, 0, 120), cap.inflate(-2, -2), width=1,
                         border_radius=17)
        pygame.draw.rect(surf, (*_GOLD_BRIGHT, 190), cap, width=1, border_radius=18)
        x = cap.x + pad
        _soft_glow(surf, x + coin_d // 2, y, coin_d + 4, (255, 206, 92), 110, layers=5)
        _coin_glyph(surf, x + coin_d // 2, y, coin_d // 2)
        x += coin_d + gap_coin
        _gradient_text(surf, val, vf, (x + vimg_w // 2, y),
                       (255, 246, 196), (236, 170, 60), shadow=True)

    def _draw_daily(self, surf) -> None:
        """Top-right daily-reward pill: claimable shows the bonus in gold,
        already-claimed mutes. The steady drip toward the higher tiers."""
        from game.config import DAILY_REWARD
        avail = store_data.daily_available()
        f = _font(12, True)
        fg = (28, 18, 8) if avail else (150, 140, 155)
        txt = ("+" + str(DAILY_REWARD)) if avail else "✓"
        timg = f.render(txt, True, fg)
        lbl = f.render("DAILY", True, fg)
        w = lbl.get_width() + 6 + timg.get_width() + 22
        r = pygame.Rect(W - 12 - w, 14, w, 24)
        self.daily_rect = r if avail else None
        if avail:
            surf.blit(_vgrad_panel(r.w, r.h, 11, (255, 215, 120), _GOLD_DEEP, 255),
                      r.topleft)
            pygame.draw.rect(surf, (*_GOLD_BRIGHT, 200), r, width=1, border_radius=11)
        else:
            surf.blit(_vgrad_panel(r.w, r.h, 11, (44, 36, 56), (28, 22, 40), 240),
                      r.topleft)
            pygame.draw.rect(surf, (80, 70, 100), r, width=1, border_radius=11)
        surf.blit(lbl, lbl.get_rect(midleft=(r.x + 11, r.centery)))
        surf.blit(timg, timg.get_rect(midleft=(r.x + 11 + lbl.get_width() + 6, r.centery)))

    def _draw_tabs(self, surf) -> None:
        """Horizontally scrollable tab strip. ONE active treatment — a brighter
        gold label + a glowing gold underline on the active tab, dimmed labels
        elsewhere (no pills). With more tabs than fit, the strip clips to a
        viewport flanked by ``< >`` chevrons; switching resets that tab to page 1
        and scrolls it into view."""
        f = _font(12, True)
        pad, gap = 11, 6
        widths = [f.size(label)[0] + 2 * pad for label, _g in _TABS]
        content_w = sum(widths) + gap * (len(_TABS) - 1)
        full_vp = pygame.Rect(12, _TAB_Y - 13, W - 24, 26)
        overflow = content_w > full_vp.width
        chev = 18 if overflow else 0
        vp = pygame.Rect(full_vp.x + chev, full_vp.y, full_vp.width - 2 * chev, 26)
        max_scroll = max(0, content_w - vp.width)
        self.tab_scroll = max(0.0, min(self.tab_scroll, float(max_scroll)))
        self._tab_vp, self._tab_widths, self._tab_gap = vp, widths, gap

        prev_clip = surf.get_clip()
        surf.set_clip(vp)
        self.tab_rects = []
        cx = 0
        for i, (label, _g) in enumerate(_TABS):
            w = widths[i]
            r = pygame.Rect(round(vp.x + cx - self.tab_scroll), _TAB_Y - 13, w, 26)
            self.tab_rects.append(r)
            active = (i == self.tab)
            col = _GOLD_BRIGHT if active else (150, 142, 158)
            timg = f.render(label, True, col)
            if not active:
                timg.set_alpha(175)
            tr = timg.get_rect(center=r.center)
            surf.blit(timg, tr)
            if active:
                ur = pygame.Rect(tr.x - 2, r.bottom - 4, tr.w + 4, 3)
                uglow = pygame.Surface((ur.w + 12, 10), pygame.SRCALPHA)
                for gy in range(10):
                    pygame.draw.line(uglow, (255, 200, 80, int(40 * (1 - gy / 10))),
                                     (0, gy), (ur.w + 12, gy))
                surf.blit(uglow, (ur.x - 6, ur.y - 2), special_flags=pygame.BLEND_ADD)
                rounded_rect(surf, ur, 2, _GOLD_BRIGHT)
            cx += w + gap
        surf.set_clip(prev_clip)

        self.tab_chev_l = self.tab_chev_r = None
        if overflow and self.tab_scroll > 1:
            self.tab_chev_l = pygame.Rect(full_vp.x, full_vp.y, chev, 26)
            _draw_chevron(surf, self.tab_chev_l, -1)
        if overflow and self.tab_scroll < max_scroll - 1:
            self.tab_chev_r = pygame.Rect(full_vp.right - chev, full_vp.y, chev, 26)
            _draw_chevron(surf, self.tab_chev_r, 1)

    def _scroll_tab_into_view(self, i: int) -> None:
        """Pan the strip so tab ``i`` is fully visible (used on tab select)."""
        if not getattr(self, "_tab_widths", None):
            return
        x = sum(self._tab_widths[:i]) + self._tab_gap * i
        w = self._tab_widths[i]
        if x < self.tab_scroll:
            self.tab_scroll = float(x)
        elif x + w > self.tab_scroll + self._tab_vp.width:
            self.tab_scroll = float(x + w - self._tab_vp.width)

    def _draw_card(self, surf, sid: str, rect: pygame.Rect) -> None:
        """Constellation jewel card (indigo body + gold bevel, glass cabochon
        thumb, faceted tier gem, notched rarity ribbon, cream name, price/EQUIPPED
        chip). The card is static per (sid, equipped, masked) state, so it is
        supersampled + cached once in game/store_cards.py and blitted here."""
        owned = store_data.is_owned(sid)
        equipped = (store_data.equipped(_slot_of(sid)) == sid)
        surf.blit(store_cards.render_card(sid, equipped=equipped, owned=owned),
                  rect.topleft)

    def _state_chip(self, surf, sid, cx, cy, owned, equipped, secret, h=24) -> None:
        """The actionable state line: EQUIPPED / EQUIP / price / can't-afford,
        in the one unified chip silhouette."""
        if equipped:
            _chip(surf, cx, cy, "EQUIPPED", "equipped", h=h)
            return
        if owned and not secret:
            _chip(surf, cx, cy, "EQUIP", "equip", h=h)
            return
        price = store_catalog.cost(sid)
        if store_data.balance() >= price:
            _chip(surf, cx, cy, f"{price:,}", "price", coin=True, h=h)
        else:
            _chip(surf, cx, cy, f"{price:,}", "locked", lock=True, h=h)

    def _draw_page_controls(self, surf, x, y, w) -> None:
        """‹  PAGE n/N  › — tap arrows to flip pages. Hidden when it all fits."""
        self.prev_rect = self.next_rect = None
        if self.n_pages <= 1:
            return
        cy = y + 11
        lbl = _font(12, True).render(f"PAGE  {self.page + 1} / {self.n_pages}",
                                     True, _GOLD_PALE)
        surf.blit(lbl, lbl.get_rect(center=(x + w // 2, cy)))
        self.prev_rect = self._arrow(surf, x + 16, cy, "<", self.page > 0)
        self.next_rect = self._arrow(surf, x + w - 16, cy, ">",
                                     self.page < self.n_pages - 1)

    def _arrow(self, surf, cx, cy, glyph, enabled) -> "pygame.Rect | None":
        r = pygame.Rect(0, 0, 30, 22)
        r.center = (cx, cy)
        surf.blit(_vgrad_panel(r.w, r.h, 11, (44, 34, 20) if enabled else (44, 40, 50),
                               (24, 18, 10) if enabled else (28, 24, 32)), r.topleft)
        pygame.draw.rect(surf, (*_GOLD_BRIGHT, 190) if enabled else (88, 80, 90),
                         r, width=1, border_radius=11)
        g = _font(15, True).render(glyph, True,
                                   _GOLD_PALE if enabled else (140, 132, 146))
        surf.blit(g, g.get_rect(center=(cx, cy - 1)))
        return r if enabled else None

    def _draw_back(self, surf) -> None:
        r = pygame.Rect(0, 0, 160, 36)
        r.center = (W // 2, H - 26)
        _drop_shadow(surf, r, 18, blur=4, alpha=90)
        surf.blit(_vgrad_panel(r.w, r.h, 18, (40, 32, 56), (22, 16, 38), 240),
                  r.topleft)
        pygame.draw.rect(surf, (*_GOLD_BRIGHT, 185), r, width=1, border_radius=18)
        timg = _font(18, True).render("BACK", True, _GOLD_PALE)
        surf.blit(timg, timg.get_rect(center=r.center))
        self.back_rect = r

    def _draw_toast(self, surf) -> None:
        text, ttl = self._toast
        if ttl <= 0.0 or not text:
            return
        alpha = int(255 * min(1.0, ttl / 0.4))  # fade out over the last 0.4 s
        timg = _font(15, True).render(text, True, _GOLD_BRIGHT)
        timg.set_alpha(alpha)
        bg = pygame.Rect(0, 0, timg.get_width() + 28, 30)
        bg.center = (W // 2, H - 70)
        panel = pygame.Surface(bg.size, pygame.SRCALPHA)
        rounded_rect(panel, panel.get_rect(), 15, (20, 12, 40),
                     alpha=min(220, alpha))
        pygame.draw.rect(panel, (*_GOLD_BRIGHT, min(150, alpha)),
                         panel.get_rect(), width=1, border_radius=15)
        surf.blit(panel, bg.topleft)
        surf.blit(timg, timg.get_rect(center=bg.center))

    def _draw_confirm(self, surf) -> None:
        """The buy-confirmation modal: a ~70% scrim + a centred obsidian panel —
        the item on a connected disc+shelf stage, its rarity word, a single price
        chip, and a BUY / CANCEL row. Spending is gated here so an accidental tap
        can never drain the wallet; BUY locks (with a note) when unaffordable."""
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
        pw, ph = 252, 286
        panel = pygame.Rect((W - pw) // 2, (H - ph) // 2, pw, ph)
        self._confirm_panel = panel
        _drop_shadow(surf, panel, 18, blur=8, alpha=170)
        surf.blit(_vgrad_panel(pw, ph, 18, (28, 24, 38), (12, 10, 22), 255),
                  panel.topleft)
        pygame.draw.rect(surf, lerp_color(_GOLD_BRIGHT, NEAR_BLACK, 0.45), panel,
                         width=2, border_radius=18)
        pygame.draw.rect(surf, (*_GOLD_BRIGHT, 230), panel.inflate(-2, -2),
                         width=1, border_radius=16)

        cx = panel.centerx
        head = _font(13, True).render("CONFIRM PURCHASE", True, _GOLD_PALE)
        surf.blit(head, head.get_rect(center=(cx, panel.y + 22)))
        _gold_rule(surf, panel.x + 28, panel.right - 28, panel.y + 38)

        # Connected disc + shelf stage so they read as one lit vitrine element.
        stage = pygame.Rect(cx - 48, panel.y + 52, 96, 96)
        surf.blit(_vgrad_panel(stage.w, stage.h, 12, (18, 16, 26), (8, 7, 14)),
                  stage.topleft)
        pygame.draw.rect(surf, (0, 0, 0, 150), stage, width=1, border_radius=12)
        disc_cy = stage.y + 40
        _inset_disc(surf, cx, disc_cy, 38)
        if secret:
            _draw_qmark(surf, cx, disc_cy, 50, UI_CREAM, NEAR_BLACK, thick=3)
            name = "???"
        else:
            thumb = self._thumbs[sid]
            surf.blit(thumb, thumb.get_rect(center=(cx, disc_cy)))
            name = self._disp_name(sid)
        _shelf_bar(surf, stage, tier, mystery=secret)
        _gem(surf, stage.right - 4, stage.y + 4, 7, tier, self.t, mystery=secret)

        nimg = _font(17, True).render(name, True, _GOLD_BRIGHT)
        surf.blit(nimg, nimg.get_rect(center=(cx, panel.y + 162)))
        rword_txt = "MYSTERY" if secret else tier.upper()
        rword_col = _MYSTERY["gem"] if secret else _RARITY[tier]["gem"]
        rword = _font(11, True).render(rword_txt, True, rword_col)
        surf.blit(rword, rword.get_rect(center=(cx, panel.y + 180)))

        price = store_catalog.cost(sid)
        affordable = store_data.balance() >= price
        if affordable:
            _chip(surf, cx, panel.y + 204, f"{price:,}", "price", coin=True, h=28)
        else:
            _chip(surf, cx, panel.y + 200, f"{price:,}", "locked", lock=True, h=28)
            warn = _font(10, True).render("NOT ENOUGH COINS", True, (150, 166, 190))
            surf.blit(warn, warn.get_rect(center=(cx, panel.y + 222)))

        bw, bh, gutter = 100, 38, 16
        by = panel.bottom - 30
        nx = cx - (bw * 2 + gutter) // 2
        cancel = pygame.Rect(nx, by - bh // 2, bw, bh)
        buy = pygame.Rect(nx + bw + gutter, by - bh // 2, bw, bh)
        surf.blit(_vgrad_panel(bw, bh, bh // 2, (70, 62, 80), (44, 38, 56)),
                  cancel.topleft)
        pygame.draw.rect(surf, (126, 116, 138), cancel, width=1, border_radius=bh // 2)
        ct = _font(14, True).render("CANCEL", True, UI_CREAM)
        surf.blit(ct, ct.get_rect(center=cancel.center))
        if affordable:
            bglow = pygame.Surface((bw + 10, bh + 10), pygame.SRCALPHA)
            for k in range(4, 0, -1):
                pygame.draw.rect(bglow, (255, 200, 80, int(22 * k / 4)),
                                 (5 - k, 5 - k, bw + 2 * k, bh + 2 * k),
                                 border_radius=bh // 2 + k)
            surf.blit(bglow, (buy.x - 5, buy.y - 5), special_flags=pygame.BLEND_ADD)
            surf.blit(_vgrad_panel(bw, bh, bh // 2,
                                   lerp_color(_GOLD_BRIGHT, WHITE, 0.2), _GOLD_DEEP),
                      buy.topleft)
            pygame.draw.rect(surf, _GOLD_PALE, buy, width=1, border_radius=bh // 2)
            yt = _font(15, True).render("BUY", True, (40, 24, 8))
            surf.blit(yt, yt.get_rect(center=buy.center))
            self.confirm_yes_rect = buy
        else:
            surf.blit(_vgrad_panel(bw, bh, bh // 2, (48, 44, 58), (30, 28, 40)),
                      buy.topleft)
            pygame.draw.rect(surf, (92, 84, 104), buy, width=1, border_radius=bh // 2)
            yt = _font(15, True).render("BUY", True, (120, 116, 134))
            surf.blit(yt, yt.get_rect(center=buy.center))
        self.confirm_no_rect = cancel

    # ── input ────────────────────────────────────────────────────────────────
    def handle_tap(self, pos) -> "str | None":
        # While the buy-confirmation is up it is modal: only its own buttons
        # (and a tap on the scrim, which cancels) are hit-testable.
        if self._confirm is not None:
            return self._handle_confirm_tap(pos)
        # Device back / escape steps OUT one level: category -> hub -> exit store.
        if pos is None:
            if self.view == "category":
                self.view = "hub"
                return None
            return "back"
        if self.view == "hub":
            return self._handle_hub_tap(pos)
        # BACK from a category returns to the hub, not all the way out, so the
        # lagoon stays the store's home.
        if self.back_rect and self.back_rect.collidepoint(pos):
            self.view = "hub"
            return None
        if self.tab_chev_l and self.tab_chev_l.collidepoint(pos):
            self.tab_scroll = max(0.0, self.tab_scroll - self._tab_vp.width * 0.6)
            return None
        if self.tab_chev_r and self.tab_chev_r.collidepoint(pos):
            self.tab_scroll += self._tab_vp.width * 0.6
            return None
        for i, r in enumerate(self.tab_rects):
            # Only count taps inside the viewport so a pill peeking under a
            # chevron isn't selectable by its hidden edge.
            if r.collidepoint(pos) and self._tab_vp.collidepoint(pos):
                if i != self.tab:
                    self.tab = i
                    self.page = 0  # each tab starts at its first page
                    self._scroll_tab_into_view(i)
                return None
        if self.daily_rect and self.daily_rect.collidepoint(pos):
            got = store_data.claim_daily()
            if got > 0:
                self._flash("DAILY BONUS  +" + str(got))
                store_cards.clear_cache()  # balance changed -> affordability tints
            return None
        if self.prev_rect and self.prev_rect.collidepoint(pos):
            self.page = max(0, self.page - 1)
            return None
        if self.next_rect and self.next_rect.collidepoint(pos):
            self.page = min(self.n_pages - 1, self.page + 1)
            return None
        for sid, rect in self.item_rects.items():
            if rect.collidepoint(pos):
                self._tap_item(sid)
                return None
        return None

    def _handle_hub_tap(self, pos) -> "str | None":
        # On the lagoon hub BACK exits the store; a stall drills into its
        # category. The hub may not be built yet on a stray first-frame tap.
        if self.back_rect and self.back_rect.collidepoint(pos):
            return "back"
        if self.hub is None:
            return None
        for group, r in self.hub.stall_rects.items():
            if r.collidepoint(pos):
                # Shut stalls (bamboo blind) are inert: a tap is a silent no-op,
                # never routing into the category or flashing a message.
                if group in self.hub.CLOSED_GROUPS:
                    return None
                self.tab = _GROUP_TAB[group]
                self.page = 0  # each category opens on its first page
                self._scroll_tab_into_view(self.tab)
                self.view = "category"
                return None
        return None

    def _tap_item(self, sid: str) -> None:
        if store_data.equipped(_slot_of(sid)) == sid:
            return  # already worn
        if store_data.is_owned(sid):
            # Equipping a look already owned is free + reversible, so it stays a
            # one-tap action; only a coin-spending purchase needs confirming.
            store_data.equip(sid)
            store_cards.clear_cache()  # EQUIPPED state moved between two cards
            self._flash(self._disp_name(sid) + " EQUIPPED")
            return
        # Unowned: a tap raises the buy-confirmation; nothing is spent yet.
        self._confirm = sid

    def _handle_confirm_tap(self, pos) -> None:
        if pos is None:                       # device back / escape cancels
            self._confirm = None
            return None
        if self.confirm_yes_rect and self.confirm_yes_rect.collidepoint(pos):
            self._commit_purchase()
            return None
        if self.confirm_no_rect and self.confirm_no_rect.collidepoint(pos):
            self._confirm = None
            return None
        # A tap on the dimmed scrim (outside the panel) dismisses; a tap inside
        # the panel that misses both buttons is ignored.
        if self._confirm_panel and not self._confirm_panel.collidepoint(pos):
            self._confirm = None
        return None

    def _commit_purchase(self) -> None:
        sid, self._confirm = self._confirm, None
        if sid is None:
            return
        ok, reason = store_data.try_purchase(sid)
        if ok:
            # Auto-equip a fresh unlock so the player immediately sees their
            # new bird — the satisfying payoff of the purchase.
            store_data.equip(sid)
            if sid == "skin_jet_fighter":
                # Bind the preview to the design just rolled for this unlock so
                # the card shows the actual jet, not a stale lazy default.
                from game import animal_jet_fighter
                animal_jet_fighter.sync_from_store()
            if sid == "parcel_whiskey":
                # Same: bind the mystery whiskey to the dram just rolled.
                from game import parcel_whiskey
                parcel_whiskey.sync_from_store()
            # Ownership + balance + EQUIPPED all changed: rebuild the cards (this
            # one reveals if it was a masked secret, and now reads EQUIPPED).
            store_cards.clear_cache()
            self._flash("UNLOCKED!  " + self._disp_name(sid))
        elif reason == "insufficient":
            self._flash("NEED MORE COINS")
