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

from game.config import W, H, PRIZE_MACHINE_COST
from game.hud import _font, _draw_overlay_stars, _pill_btn, _coin_icon, \
    _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP
from game.draw import UI_CREAM, NEAR_BLACK, rounded_rect
from game.powerup_help import _gradient_bg, _outlined_title, _seeded_stars, \
    _dark_panel
from game import parrot
from game import prize_machine
from game import store_catalog
from game import store_data

# Card grid metrics (2 columns). Thumbnails are pre-rendered once so the
# per-frame cost is a flat blit rather than six smoothscales.
_CARD_W = 162
_CARD_H = 112
_GAP = 8
_GRID_TOP = 104
_THUMB_BOX = 54

# Owned-but-equipped accent + buy/locked chip tints.
_EQUIP_GREEN = (96, 210, 120)
_LOCK_GREY = (150, 140, 155)


def _build_thumb(skin_id: str, box: int) -> pygame.Surface:
    """Render a skin's idle frame and fit it into a ``box``-square, aspect
    preserved. Built once per store open."""
    src = parrot.get_skin_frame(skin_id, 1, 0.0)
    sw, sh = src.get_size()
    scale = box / max(sw, sh)
    return pygame.transform.smoothscale(
        src, (max(1, int(sw * scale)), max(1, int(sh * scale))))


class StoreScene:
    def __init__(self) -> None:
        self.t = 0.0
        self._stars = _seeded_stars()
        self.back_rect: "pygame.Rect | None" = None
        self.item_rects: "dict[str, pygame.Rect]" = {}
        self.prize_rect: "pygame.Rect | None" = None
        self._toast = ("", 0.0)  # (text, seconds remaining)
        # Sub-mode: the grid, or the Prize Machine reveal playing over it.
        # Kept internal so the gacha needs no extra App scene-state.
        self.mode = "grid"
        self.prize: "prize_machine.PrizeReveal | None" = None
        store_data.load()
        # Catalog skins, cheapest first, with pre-built thumbnails.
        self._skins = sorted(store_catalog.skin_ids(), key=store_catalog.cost)
        self._thumbs = {sid: _build_thumb(sid, _THUMB_BOX) for sid in self._skins}

    def update(self, dt: float) -> None:
        self.t += dt
        text, ttl = self._toast
        if ttl > 0.0:
            self._toast = (text, max(0.0, ttl - dt))
        if self.mode == "prize" and self.prize is not None:
            self.prize.update(dt)

    def _flash(self, text: str) -> None:
        self._toast = (text, 1.6)

    # ── rendering ────────────────────────────────────────────────────────────
    def render(self, surf: pygame.Surface) -> None:
        if self.mode == "prize" and self.prize is not None:
            self.prize.render(surf)
            return

        _gradient_bg(surf)
        _draw_overlay_stars(surf, self._stars, self.t + 1.4)

        _outlined_title(surf, "STORE", (W // 2, 32),
                        size=30, px=2, shadow_offset=(2, 3))
        self._draw_balance(surf, cx=W // 2, y=68)

        base_x = (W - (_CARD_W * 2 + _GAP)) // 2
        for idx, sid in enumerate(self._skins):
            col = idx % 2
            row = idx // 2
            x = base_x + col * (_CARD_W + _GAP)
            y = _GRID_TOP + row * (_CARD_H + _GAP)
            rect = pygame.Rect(x, y, _CARD_W, _CARD_H)
            self.item_rects[sid] = rect
            self._draw_card(surf, sid, rect)

        grid_bot = _GRID_TOP + 3 * (_CARD_H + _GAP)
        self._draw_prize_card(surf, base_x, grid_bot + 2, _CARD_W * 2 + _GAP)

        self._draw_toast(surf)
        self.back_rect = _pill_btn(
            surf, (W // 2, H - 30), "BACK",
            size=18, alpha=235, min_width=160, dim=True, shadow=False)

    def _draw_prize_card(self, surf, x, y, w) -> None:
        """The gacha entry — a wide gold-rimmed card that stands apart from
        the skin grid as the store's headline feature."""
        rect = pygame.Rect(x, y, w, 56)
        self.prize_rect = rect
        _dark_panel(surf, rect, radius=14, alpha=225)
        pygame.draw.rect(surf, _GOLD_BRIGHT, rect, width=2, border_radius=14)
        # Gift-box "?" glyph on the left.
        self._draw_gift(surf, rect.x + 34, rect.centery)
        title = _font(16, True).render("PRIZE MACHINE", True, _GOLD_BRIGHT)
        surf.blit(title, (rect.x + 64, rect.y + 9))
        sub = _font(11, True).render("Roll for a random new skin", True, UI_CREAM)
        sub.set_alpha(205)
        surf.blit(sub, (rect.x + 64, rect.y + 31))
        # Cost chip on the right.
        affordable = store_data.balance() >= PRIZE_MACHINE_COST
        self._chip(surf, rect.right - 44, rect.centery, str(PRIZE_MACHINE_COST),
                   fg=_GOLD_PALE if affordable else _LOCK_GREY,
                   bg=_GOLD_DEEP if affordable else (70, 60, 70), coin=1)

    def _draw_gift(self, surf, cx, cy) -> None:
        box = pygame.Rect(cx - 13, cy - 9, 26, 22)
        rounded_rect(surf, box, 4, (200, 40, 40))
        pygame.draw.rect(surf, _GOLD_BRIGHT, (cx - 2, cy - 9, 4, 22))
        pygame.draw.rect(surf, _GOLD_BRIGHT, (cx - 13, cy - 1, 26, 4))
        qm = _font(13, True).render("?", True, _GOLD_PALE)
        surf.blit(qm, qm.get_rect(center=(cx, cy + 1)))

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
        equipped = (store_data.equipped("skin") == sid)
        _dark_panel(surf, rect, radius=14, alpha=215)

        # Equipped cards get a bright gold rim so the current look is obvious
        # at a glance across the grid.
        if equipped:
            pygame.draw.rect(surf, _GOLD_BRIGHT, rect, width=2, border_radius=14)

        thumb = self._thumbs[sid]
        surf.blit(thumb, thumb.get_rect(center=(rect.centerx, rect.y + 34)))

        nimg = _font(14, True).render(store_catalog.name(sid), True, _GOLD_BRIGHT)
        surf.blit(nimg, nimg.get_rect(center=(rect.centerx, rect.y + 70)))

        self._draw_state_chip(surf, sid, rect, owned, equipped)

    def _draw_state_chip(self, surf, sid, rect, owned, equipped) -> None:
        """The actionable state line: EQUIPPED / EQUIP / BUY <cost>, tinted so
        affordability and ownership read without reading the text."""
        cy = rect.y + 92
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
        if self.mode == "prize" and self.prize is not None:
            if self.prize.handle_tap(pos) == "done":
                self.prize = None
                self.mode = "grid"
            return None
        if pos is None:
            return "back"
        if self.back_rect and self.back_rect.collidepoint(pos):
            return "back"
        if self.prize_rect and self.prize_rect.collidepoint(pos):
            self._tap_prize()
            return None
        for sid, rect in self.item_rects.items():
            if rect.collidepoint(pos):
                self._tap_item(sid)
                return None
        return None

    def _tap_prize(self) -> None:
        """Gate the gacha before charging: never spend when everything's
        already owned or the wallet can't cover a roll. On a valid roll, spend
        + grant the winner, then open the reveal."""
        if not prize_machine.unowned_pool():
            self._flash("EVERYTHING UNLOCKED!")
            return
        if store_data.balance() < PRIZE_MACHINE_COST:
            self._flash("NEED MORE COINS")
            return
        won = prize_machine.roll()
        store_data.try_spend(PRIZE_MACHINE_COST)
        store_data.grant(won)
        self.prize = prize_machine.PrizeReveal(won)
        self.mode = "prize"

    def _tap_item(self, sid: str) -> None:
        if store_data.equipped("skin") == sid:
            return  # already worn
        if store_data.is_owned(sid):
            store_data.equip(sid)
            self._flash(store_catalog.name(sid) + " EQUIPPED")
            return
        ok, reason = store_data.try_purchase(sid)
        if ok:
            # Auto-equip a fresh unlock so the player immediately sees their
            # new bird — the satisfying payoff of the purchase.
            store_data.equip(sid)
            self._flash("UNLOCKED!  " + store_catalog.name(sid))
        elif reason == "insufficient":
            self._flash("NEED MORE COINS")
