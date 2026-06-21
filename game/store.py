"""
Coin Store — spend banked coins on cosmetics.

Reached from the menu's STORE pill (STATE_STORE). The wallet that backs it
(game/store_data.py) banks each run's coins at death, so the balance shown
here grows as the player flies.

This module owns the whole frame for STATE_STORE. The App's `_render` hands
it the screen surface; the App's `_flap_input` routes taps *into*
`handle_tap`, which returns an action token ("back" / "open_prize" / None) —
the store is interactive, so taps are dispatched here rather than blanket-
dismissing the screen like the one-tap help explainer.

Visual language is shared with the power-ups explainer and the menu (night-
sky gradient, twinkling stars, gold-on-red title, Pip Scarlet cards) so the
store reads as part of the same family.
"""
from __future__ import annotations

import pygame

from game.config import W, H
from game.hud import _font, _draw_overlay_stars, _pill_btn, _coin_icon, \
    _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP
from game.draw import UI_CREAM, NEAR_BLACK, rounded_rect
from game.powerup_help import _gradient_bg, _outlined_title, _seeded_stars, \
    _dark_panel
from game import parrot
from game import store_catalog
from game import store_data
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

# Owned-but-equipped accent + buy/locked chip tints.
_EQUIP_GREEN = (96, 210, 120)
_LOCK_GREY = (150, 140, 155)
# Mystery-violet rim that marks a still-masked secret card as special.
_SECRET_RIM = (150, 110, 214)


def _draw_chevron(surf, rect, direction) -> None:
    """A small ``<`` / ``>`` scroll affordance at a tab-strip edge."""
    rounded_rect(surf, rect, 9, (34, 26, 56))
    pygame.draw.rect(surf, (90, 78, 120), rect, width=1, border_radius=9)
    cx, cy = rect.center
    d = direction  # -1 = left arrow, +1 = right arrow
    pts = [(cx - 2 * d, cy - 5), (cx + 3 * d, cy), (cx - 2 * d, cy + 5)]
    pygame.draw.lines(surf, _GOLD_BRIGHT, False, pts, 2)


def _fit_skin(skin_id: str, box: int) -> pygame.Surface:
    """Render a skin's store thumbnail, crop to its opaque content, and fit that
    into a ``box``-square (aspect preserved). Cropping first normalises the
    different canvas sizes across skins (tall headgear composites vs the 64px
    redraws) so every thumbnail fills its box consistently. Shoes supply a
    product-shot icon (the sneaker itself) via ``get_skin_icon``; everything
    else falls back to the in-game look."""
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
    equipped-accent + tap-to-equip logic works for parcels as well as skins.
    The two free defaults aren't in the catalog, so map them explicitly."""
    if sid == store_catalog.PARCEL_BASE:
        return "parcel"
    if sid == store_catalog.BASE_SKIN or not store_catalog.exists(sid):
        return "skin"
    return store_catalog.kind(sid)


class StoreScene:
    def __init__(self) -> None:
        self.t = 0.0
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
        store_data.load()
        # Per-tab skin lists, cheapest first. The PARROTS and SHADES tabs are
        # fronted by a free DEFAULT card (the base macaw / its default aviators)
        # so the player can always revert — on SHADES it reads as the full
        # eyewear set: DEFAULT aviators, the alternatives, then NO SHADES.
        self._lists: "dict[str, list[str]]" = {}
        for label, g in _TABS:
            ids = sorted(store_catalog.ids_of_group(g), key=store_catalog.cost)
            if g in ("parrot", "shades"):
                ids = [store_catalog.BASE_SKIN] + ids
            elif g == "parcels":
                # Front the PARCELS tab with the free DEFAULT box so the player
                # can always revert to Pip's classic parcel.
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
        _gradient_bg(surf)
        _draw_overlay_stars(surf, self._stars, self.t + 1.4)

        _outlined_title(surf, "STORE", (W // 2, 30),
                        size=28, px=2, shadow_offset=(2, 3))
        self._draw_balance(surf, cx=W // 2, y=62)
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
            col = idx % 2
            row = idx // 2
            x = base_x + col * (_CARD_W + _GAP)
            y = _GRID_TOP + row * (_CARD_H + _GAP)
            rect = pygame.Rect(x, y, _CARD_W, _CARD_H)
            self.item_rects[sid] = rect
            self._draw_card(surf, sid, rect)

        grid_bot = _GRID_TOP + 4 * (_CARD_H + _GAP)
        self._draw_page_controls(surf, base_x, grid_bot - 4, _CARD_W * 2 + _GAP)

        self._draw_toast(surf)
        self.back_rect = _pill_btn(
            surf, (W // 2, H - 28), "BACK",
            size=18, alpha=235, min_width=160, dim=True, shadow=False)

    def _draw_tabs(self, surf) -> None:
        """A horizontally scrollable strip of natural-width tab pills (the
        active one gold-filled). With more tabs than fit the 360px row, the
        strip clips to a viewport flanked by ``< >`` chevrons; the full font
        stays readable and the item grid below keeps its place. Switching a
        tab resets that view to page 1 and scrolls it into view."""
        f = _font(12, True)
        pad, gap = 11, 6
        widths = [f.size(label)[0] + 2 * pad for label, _g in _TABS]
        content_w = sum(widths) + gap * (len(_TABS) - 1)
        full_vp = pygame.Rect(12, _TAB_Y - 13, W - 24, 26)
        overflow = content_w > full_vp.width
        chev = 18 if overflow else 0
        vp = pygame.Rect(full_vp.x + chev, full_vp.y,
                         full_vp.width - 2 * chev, 26)
        max_scroll = max(0, content_w - vp.width)
        self.tab_scroll = max(0.0, min(self.tab_scroll, float(max_scroll)))
        # Stash layout so handle_tap can hit-test + scroll with the same metrics.
        self._tab_vp, self._tab_widths, self._tab_gap = vp, widths, gap

        prev_clip = surf.get_clip()
        surf.set_clip(vp)
        self.tab_rects = []
        cx = 0
        for i, (label, _g) in enumerate(_TABS):
            w = widths[i]
            r = pygame.Rect(round(vp.x + cx - self.tab_scroll),
                            _TAB_Y - 13, w, 26)
            self.tab_rects.append(r)
            active = (i == self.tab)
            rounded_rect(surf, r, 9, _GOLD_DEEP if active else (34, 26, 56))
            pygame.draw.rect(surf, _GOLD_BRIGHT if active else (90, 78, 120),
                             r, width=1, border_radius=9)
            col = (28, 18, 8) if active else _GOLD_PALE
            t = f.render(label, True, col)
            surf.blit(t, t.get_rect(center=r.center))
            cx += w + gap
        surf.set_clip(prev_clip)

        # Chevrons only when there's hidden content that way.
        self.tab_chev_l = self.tab_chev_r = None
        if overflow and self.tab_scroll > 1:
            self.tab_chev_l = pygame.Rect(full_vp.x, full_vp.y, chev, 26)
            _draw_chevron(surf, self.tab_chev_l, -1)
        if overflow and self.tab_scroll < max_scroll - 1:
            self.tab_chev_r = pygame.Rect(full_vp.right - chev, full_vp.y,
                                          chev, 26)
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

    def _draw_daily(self, surf) -> None:
        """Top-right daily-reward pill: claimable shows the bonus in gold,
        already-claimed greys out. The steady drip toward the higher tiers."""
        from game.config import DAILY_REWARD
        avail = store_data.daily_available()
        txt = ("+" + str(DAILY_REWARD)) if avail else "✓"
        f = _font(12, True)
        timg = f.render(txt, True, (28, 18, 8) if avail else _LOCK_GREY)
        lbl = f.render("DAILY", True, (28, 18, 8) if avail else _LOCK_GREY)
        w = lbl.get_width() + 6 + timg.get_width() + 20
        r = pygame.Rect(W - 12 - w, 14, w, 24)
        self.daily_rect = r if avail else None
        rounded_rect(surf, r, 11, _GOLD_DEEP if avail else (44, 36, 56))
        pygame.draw.rect(surf, _GOLD_BRIGHT if avail else (80, 70, 100),
                         r, width=1, border_radius=11)
        surf.blit(lbl, lbl.get_rect(midleft=(r.x + 10, r.centery)))
        surf.blit(timg, timg.get_rect(midleft=(r.x + 10 + lbl.get_width() + 6,
                                               r.centery)))

    def _draw_page_controls(self, surf, x, y, w) -> None:
        """‹  PAGE n/N  › — tap arrows to flip pages (drag-scroll isn't
        available on the tap-only input path). Hidden when it all fits."""
        self.prev_rect = self.next_rect = None
        if self.n_pages <= 1:
            return
        cy = y + 11
        lbl = _font(12, True).render(
            f"PAGE  {self.page + 1} / {self.n_pages}", True, _GOLD_PALE)
        surf.blit(lbl, lbl.get_rect(center=(x + w // 2, cy)))
        self.prev_rect = self._arrow(surf, x + 16, cy, "<", self.page > 0)
        self.next_rect = self._arrow(surf, x + w - 16, cy, ">",
                                     self.page < self.n_pages - 1)

    def _arrow(self, surf, cx, cy, glyph, enabled) -> "pygame.Rect | None":
        r = pygame.Rect(0, 0, 30, 22)
        r.center = (cx, cy)
        rounded_rect(surf, r, 11, _GOLD_DEEP if enabled else (60, 52, 64))
        g = _font(15, True).render(glyph, True,
                                   _GOLD_PALE if enabled else _LOCK_GREY)
        surf.blit(g, g.get_rect(center=(cx, cy - 1)))
        return r if enabled else None

    def _draw_balance(self, surf, cx, y) -> None:
        val = str(store_data.balance())
        vf = _font(22, True)
        vimg = vf.render(val, True, _GOLD_BRIGHT)
        coin_d = 22
        gap = 6
        total_w = coin_d + gap + vimg.get_width()
        x0 = cx - total_w // 2
        _coin_icon(surf, x0 + coin_d // 2, y, coin_d // 2)
        surf.blit(vimg, vimg.get_rect(midleft=(x0 + coin_d + gap, y)))

    def _draw_card(self, surf, sid: str, rect: pygame.Rect) -> None:
        owned = store_data.is_owned(sid)
        equipped = (store_data.equipped(_slot_of(sid)) == sid)
        # A secret stays masked (??? + a "?" glyph) until bought; the price chip
        # still shows, so the lure is a mystery card with a steep cost. Buying is
        # blind and reveals the real art the moment ownership flips.
        secret = store_catalog.is_secret(sid) and not owned
        _dark_panel(surf, rect, radius=14, alpha=215)

        # Equipped cards get a bright gold rim so the current look is obvious
        # at a glance; an unbought secret gets a mystery-violet rim instead.
        if equipped:
            pygame.draw.rect(surf, _GOLD_BRIGHT, rect, width=2, border_radius=14)
        elif secret:
            pygame.draw.rect(surf, _SECRET_RIM, rect, width=2, border_radius=14)

        if secret:
            _draw_qmark(surf, rect.centerx, rect.y + 30, 40,
                        UI_CREAM, NEAR_BLACK, thick=2)
            label = "???"
        else:
            thumb = self._thumbs[sid]
            surf.blit(thumb, thumb.get_rect(center=(rect.centerx, rect.y + 30)))
            label = self._disp_name(sid)

        nimg = _font(14, True).render(label, True, _GOLD_BRIGHT)
        surf.blit(nimg, nimg.get_rect(center=(rect.centerx, rect.y + 60)))

        self._draw_state_chip(surf, sid, rect, owned, equipped)

    def _draw_state_chip(self, surf, sid, rect, owned, equipped) -> None:
        """The actionable state line: EQUIPPED / EQUIP / BUY <cost>, tinted so
        affordability and ownership read without reading the text."""
        cy = rect.y + 82
        if equipped:
            self._chip(surf, rect.centerx, cy, "EQUIPPED",
                       fg=NEAR_BLACK, bg=_EQUIP_GREEN, coin=0)
        elif owned:
            self._chip(surf, rect.centerx, cy, "EQUIP",
                       fg=UI_CREAM, bg=_GOLD_DEEP, coin=0)
        else:
            price = store_catalog.cost(sid)
            affordable = store_data.balance() >= price
            bg = _GOLD_DEEP if affordable else (70, 60, 70)
            fg = _GOLD_PALE if affordable else _LOCK_GREY
            self._chip(surf, rect.centerx, cy, str(price), fg=fg, bg=bg,
                       coin=1)

    def _chip(self, surf, cx, cy, text, fg, bg, coin: int) -> None:
        f = _font(13, True)
        timg = f.render(text, True, fg)
        coin_d = 16
        cgap = 4 if coin else 0
        inner = (coin_d + cgap if coin else 0) + timg.get_width()
        pad = 12
        w = inner + pad * 2
        h = 24
        chip = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
        rounded_rect(surf, chip, h // 2, bg)
        pygame.draw.rect(surf, (*_GOLD_BRIGHT, 90), chip, width=1,
                         border_radius=h // 2)
        x = chip.x + pad
        if coin:
            _coin_icon(surf, x + coin_d // 2, cy, coin_d // 2)
            x += coin_d + cgap
        surf.blit(timg, timg.get_rect(midleft=(x, cy)))

    def _draw_toast(self, surf) -> None:
        text, ttl = self._toast
        if ttl <= 0.0 or not text:
            return
        alpha = int(255 * min(1.0, ttl / 0.4))  # fade out over the last 0.4 s
        f = _font(15, True)
        timg = f.render(text, True, _GOLD_BRIGHT)
        timg.set_alpha(alpha)
        bg = pygame.Rect(0, 0, timg.get_width() + 28, 30)
        bg.center = (W // 2, H - 66)
        panel = pygame.Surface(bg.size, pygame.SRCALPHA)
        rounded_rect(panel, panel.get_rect(), 15, (20, 12, 40),
                     alpha=min(220, alpha))
        surf.blit(panel, bg.topleft)
        surf.blit(timg, timg.get_rect(center=bg.center))

    # ── input ────────────────────────────────────────────────────────────────
    def handle_tap(self, pos) -> "str | None":
        if pos is None:
            return "back"
        if self.back_rect and self.back_rect.collidepoint(pos):
            return "back"
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

    def _tap_item(self, sid: str) -> None:
        if store_data.equipped(_slot_of(sid)) == sid:
            return  # already worn
        if store_data.is_owned(sid):
            store_data.equip(sid)
            self._flash(self._disp_name(sid) + " EQUIPPED")
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
            self._flash("UNLOCKED!  " + self._disp_name(sid))
        elif reason == "insufficient":
            self._flash("NEED MORE COINS")
