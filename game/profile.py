"""
Profile — the player's cosmetics home.

Reached from the menu's PROFILE pill (STATE_PROFILE). Where the Store sells
cosmetics, the Profile is where the player lives with what they already own: a
persistent loadout stage at the top shows the bird exactly as it flies right now
(equipped skin + carried parcel, wing animation and all), and the tabbed grid
below lists only the items they've unlocked so they can swap their look with a
single tap. Coins are never spent here — every card is already owned, so a tap
just re-equips (free + reversible), unlike the Store's buy-confirmation gate.

It deliberately reuses the Store's "Obsidian & Gold" primitives (card body,
shelf-light bar, rarity gem, inset disc, chips, tab strip) so the two screens
read as one product. A statistics block (games played, coins, pillars passed)
is planned to slot in around this inventory later; the layout leaves the band
between the loadout stage and the grid free for it.
"""
from __future__ import annotations

import pygame

from game.config import W, H, PARCEL_Y_OFFSET
from game.hud import _font, _draw_overlay_stars, \
    _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP, _RED_OUTLINE
from game.draw import UI_CREAM, NEAR_BLACK, WHITE, rounded_rect, lerp_color
from game.powerup_help import _seeded_stars
from game import parrot
from game import store_catalog
from game import store_data
# The Store owns the locked visual language; the Profile borrows its primitives
# wholesale so the two screens can never drift apart.
from game.store import (
    _vgrad_panel, _drop_shadow, _inset_disc, _shelf_bar, _gem, _gold_leaf,
    _gradient_text, _gold_rule, _chip, _draw_chevron, _fit_skin, _slot_of,
    _coin_glyph, _soft_glow,
    _CARD_W, _CARD_H, _GAP, _THUMB_BOX, _TABS, _BG_STOPS, _OBS_TOP, _OBS_BOT,
)

# The loadout stage eats the band the Store gives to the balance + daily pills,
# so the grid starts lower and pages 2x3 (six) rather than the Store's 2x4.
_GRID_TOP = 232
_PER_PAGE = 6
_TAB_Y = 214           # tab-bar centre line, below the loadout stage


class ProfileScene:
    def __init__(self) -> None:
        self.t = 0.0
        self._stars = _seeded_stars()
        self.back_rect: "pygame.Rect | None" = None
        self.item_rects: "dict[str, pygame.Rect]" = {}
        self.prev_rect: "pygame.Rect | None" = None
        self.next_rect: "pygame.Rect | None" = None
        self.tab_rects: "list[pygame.Rect]" = []
        self.tab_scroll = 0.0
        self.tab_chev_l: "pygame.Rect | None" = None
        self.tab_chev_r: "pygame.Rect | None" = None
        self._tab_vp = pygame.Rect(12, _TAB_Y - 13, W - 24, 26)
        self._tab_widths: "list[int]" = []
        self._tab_gap = 6
        self._toast = ("", 0.0)
        store_data.load()

        # Owned-only per-tab lists, cheapest first — same ordering + free DEFAULT
        # card the Store fronts each revertable group with, but filtered to what
        # the player actually has. A tab with nothing owned (and no default) is
        # dropped so the strip only ever shows categories with content; the
        # DEFAULT cards keep PARROTS / SHADES / PARCELS present from run one.
        self._tabs: "list[tuple[str, str]]" = []
        self._lists: "dict[str, list[str]]" = {}
        for label, g in _TABS:
            ids = [i for i in sorted(store_catalog.ids_of_group(g),
                                     key=store_catalog.cost)
                   if store_data.is_owned(i)]
            if g in ("parrot", "shades"):
                ids = [store_catalog.BASE_SKIN] + ids
            elif g == "parcels":
                ids = [store_catalog.PARCEL_BASE] + ids
            if ids:
                self._tabs.append((label, g))
                self._lists[g] = ids
        self.tab = 0
        self.page = 0

        # Pre-build every grid thumbnail once (cropped-to-content; see _fit_skin).
        all_ids = {sid for ids in self._lists.values() for sid in ids}
        self._thumbs = {sid: _fit_skin(sid, _THUMB_BOX) for sid in all_ids}
        # The animated loadout composite is cached per (skin, parcel, frame); a
        # re-equip just adds a new key rather than rebuilding every frame.
        self._loadout_cache: dict = {}

    def _cur_ids(self) -> list:
        if not self._tabs:
            return []
        return self._lists[self._tabs[self.tab][1]]

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
        self._draw_bg(surf)
        self._draw_title(surf)
        self._draw_loadout(surf)
        self._draw_tabs(surf)

        base_x = (W - (_CARD_W * 2 + _GAP)) // 2
        self.item_rects = {}
        ids = self._cur_ids()
        page_ids = ids[self.page * _PER_PAGE:(self.page + 1) * _PER_PAGE]
        for idx, sid in enumerate(page_ids):
            x = base_x + (idx % 2) * (_CARD_W + _GAP)
            y = _GRID_TOP + (idx // 2) * (_CARD_H + _GAP)
            rect = pygame.Rect(x, y, _CARD_W, _CARD_H)
            self.item_rects[sid] = rect
            self._draw_card(surf, sid, rect)

        grid_bot = _GRID_TOP + 3 * (_CARD_H + _GAP)
        self._draw_page_controls(surf, base_x, grid_bot - 4, _CARD_W * 2 + _GAP)

        self._draw_toast(surf)
        self._draw_back(surf)

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
        _gradient_text(surf, "PROFILE", f, (W // 2, 28),
                       (255, 240, 180), (236, 170, 60),
                       outline=_RED_OUTLINE, shadow=True)

    # ── loadout stage ──────────────────────────────────────────────────────────
    def _loadout_sprite(self, skin: str, parcel_id: "str | None",
                        fidx: int) -> pygame.Surface:
        """The live bird as it flies: the equipped skin frame with the equipped
        parcel composited the same PARCEL_Y_OFFSET below its centre the entity
        uses, cropped to content. Built once per (skin, parcel, frame)."""
        key = (skin, parcel_id, fidx)
        s = self._loadout_cache.get(key)
        if s is not None:
            return s
        bird = parrot.get_skin_frame(skin, fidx, 0.0)
        parcel = parrot.get_parcel("normal", parcel_id)
        bw, bh = bird.get_size()
        pw, ph = parcel.get_size()
        cw = max(bw, pw) + 8
        ch = bh + PARCEL_Y_OFFSET + ph
        comp = pygame.Surface((cw, ch), pygame.SRCALPHA)
        comp.blit(bird, ((cw - bw) // 2, 0))
        comp.blit(parcel, ((cw - pw) // 2, bh // 2 + PARCEL_Y_OFFSET - ph // 2))
        bb = comp.get_bounding_rect()
        if bb.width > 0 and bb.height > 0:
            comp = comp.subsurface(bb).copy()
        self._loadout_cache[key] = comp
        return comp

    def _draw_loadout(self, surf) -> None:
        """The persistent hero stage: a wide obsidian panel with the live bird on
        a lit disc at the left, and the equipped skin/parcel names + coin balance
        at the right. Always on screen so the player sees their current look while
        they browse the grid below."""
        panel = pygame.Rect(12, 48, W - 24, 140)
        _drop_shadow(surf, panel, 16, blur=6, alpha=140)
        surf.blit(_vgrad_panel(panel.w, panel.h, 16, _OBS_TOP, _OBS_BOT, 252),
                  panel.topleft)
        pygame.draw.rect(surf, (*_GOLD_DEEP, 210), panel.inflate(-7, -7),
                         width=2, border_radius=11)
        pygame.draw.rect(surf, (*_GOLD_BRIGHT, 150), panel, width=1,
                         border_radius=16)

        skin = store_data.equipped("skin") or store_catalog.BASE_SKIN
        pid = store_data.equipped("parcel") or store_catalog.PARCEL_BASE

        # Lit stage disc + the animated bird (wings cycle off self.t at the
        # entity's idle flap rate; four frames, modulo'd by the skin builders).
        stage_cx = panel.x + 78
        stage_cy = panel.centery + 4
        _soft_glow(surf, stage_cx, stage_cy, 56, (90, 110, 170), 60, layers=5)
        _inset_disc(surf, stage_cx, stage_cy, 50)
        fidx = int(self.t * 8.0) % 4
        sprite = self._loadout_sprite(skin, pid, fidx)
        box = 86
        sw, sh = sprite.get_size()
        scale = box / max(sw, sh)
        sprite = pygame.transform.smoothscale(
            sprite, (max(1, int(sw * scale)), max(1, int(sh * scale))))
        surf.blit(sprite, sprite.get_rect(center=(stage_cx, stage_cy)))

        # Right column: what's worn + the wallet.
        tx = panel.x + 142
        lbl = _font(10, True).render("CURRENTLY EQUIPPED", True, _GOLD_PALE)
        lbl.set_alpha(200)
        surf.blit(lbl, (tx, panel.y + 18))

        sname = self._disp_name(skin)
        _gradient_text(surf, sname, _font(19, True),
                       (tx + _font(19, True).size(sname)[0] // 2, panel.y + 46),
                       (255, 246, 196), (236, 170, 60), shadow=True)
        _gold_rule(surf, tx, panel.right - 18, panel.y + 62)

        pf = _font(11, True)
        plabel = pf.render("PARCEL", True, (150, 142, 158))
        surf.blit(plabel, (tx, panel.y + 74))
        pname = _font(14, True).render(self._disp_name(pid), True, UI_CREAM)
        surf.blit(pname, (tx, panel.y + 88))

        # Coin balance — quieter than the Store's hero capsule (nothing is spent
        # here), just a small ledger of what the player has banked.
        by = panel.y + 116
        _coin_glyph(surf, tx + 8, by, 8)
        bimg = _font(15, True).render(f"{store_data.balance():,}", True, _GOLD_BRIGHT)
        surf.blit(bimg, bimg.get_rect(midleft=(tx + 22, by)))

    # ── tab strip (owned tabs only) ────────────────────────────────────────────
    def _draw_tabs(self, surf) -> None:
        """Scrollable tab strip, identical treatment to the Store (bright active
        label + glowing underline, dimmed elsewhere, ``< >`` chevrons on
        overflow) — but only the tabs the player owns something in."""
        f = _font(12, True)
        pad, gap = 11, 6
        widths = [f.size(label)[0] + 2 * pad for label, _g in self._tabs]
        content_w = sum(widths) + gap * max(0, len(self._tabs) - 1)
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
        for i, (label, _g) in enumerate(self._tabs):
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
        if not getattr(self, "_tab_widths", None):
            return
        x = sum(self._tab_widths[:i]) + self._tab_gap * i
        w = self._tab_widths[i]
        if x < self.tab_scroll:
            self.tab_scroll = float(x)
        elif x + w > self.tab_scroll + self._tab_vp.width:
            self.tab_scroll = float(x + w - self._tab_vp.width)

    # ── card (owned-only: EQUIP / EQUIPPED, never price/locked/secret) ──────────
    def _draw_card(self, surf, sid: str, rect: pygame.Rect) -> None:
        """Same B+ obsidian card as the Store, but every item here is owned, so a
        secret is already revealed and the chip is only EQUIP or EQUIPPED."""
        equipped = (store_data.equipped(_slot_of(sid)) == sid)
        tier = store_catalog.rarity(sid)

        _drop_shadow(surf, rect, 13, blur=6, alpha=140)
        surf.blit(_vgrad_panel(rect.w, rect.h, 13, _OBS_TOP, _OBS_BOT, 252),
                  rect.topleft)
        pygame.draw.rect(surf, (*_GOLD_DEEP, 210), rect.inflate(-7, -7),
                         width=2, border_radius=8)
        sheen = pygame.Surface((rect.w - 10, 16), pygame.SRCALPHA)
        for y in range(16):
            pygame.draw.line(sheen, (255, 255, 255, int(30 * (1 - y / 16))),
                             (0, y), (rect.w - 10, y))
        surf.blit(sheen, (rect.x + 5, rect.y + 4))

        _shelf_bar(surf, rect, tier)

        disc_cy = rect.y + 34
        _inset_disc(surf, rect.centerx, disc_cy, 27)
        thumb = self._thumbs[sid]
        surf.blit(thumb, thumb.get_rect(center=(rect.centerx, disc_cy)))
        name = self._disp_name(sid)

        if tier == "legendary":
            _gold_leaf(surf, rect.x + 13, rect.y + 12, 1)
        _gem(surf, rect.right - 15, rect.y + 15, 6, tier, self.t)

        nimg = _font(13, True).render(name, True, _GOLD_PALE)
        nsh = _font(13, True).render(name, True, NEAR_BLACK)
        nsh.set_alpha(150)
        nr = nimg.get_rect(center=(rect.centerx, rect.y + 62))
        surf.blit(nsh, (nr.x + 1, nr.y + 1))
        surf.blit(nimg, nr)

        _chip(surf, rect.centerx, rect.y + 82,
              "EQUIPPED" if equipped else "EQUIP",
              "equipped" if equipped else "equip", h=24)

        if equipped:
            halo = pygame.Surface((rect.w + 16, rect.h + 16), pygame.SRCALPHA)
            for k in range(4, 0, -1):
                pygame.draw.rect(halo, (*_GOLD_BRIGHT, int(20 * k / 4)),
                                 (8 - k, 8 - k, rect.w + 2 * k, rect.h + 2 * k),
                                 width=2, border_radius=13 + k)
            surf.blit(halo, (rect.x - 8, rect.y - 8), special_flags=pygame.BLEND_ADD)
            pygame.draw.rect(surf, lerp_color(_GOLD_BRIGHT, NEAR_BLACK, 0.4), rect,
                             width=2, border_radius=13)
            pygame.draw.rect(surf, _GOLD_BRIGHT, rect.inflate(-2, -2), width=1,
                             border_radius=12)

    def _draw_page_controls(self, surf, x, y, w) -> None:
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
        alpha = int(255 * min(1.0, ttl / 0.4))
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
            if r.collidepoint(pos) and self._tab_vp.collidepoint(pos):
                if i != self.tab:
                    self.tab = i
                    self.page = 0
                    self._scroll_tab_into_view(i)
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
            return  # already worn — the loadout stage already shows it
        store_data.equip(sid)
        self._flash(self._disp_name(sid) + " EQUIPPED")
