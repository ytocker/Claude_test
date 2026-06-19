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
    _GOLD_BRIGHT, _GOLD_PALE
from game.draw import UI_CREAM
from game.powerup_help import _gradient_bg, _outlined_title, _seeded_stars
from game import store_data


class StoreScene:
    def __init__(self) -> None:
        self.t = 0.0
        self._stars = _seeded_stars()
        self.back_rect: "pygame.Rect | None" = None
        # Ensure the wallet is loaded before the first balance read (lazy
        # load is also triggered by store_data itself, but doing it here
        # keeps the very first frame's balance correct on the web bridge).
        store_data.load()

    def update(self, dt: float) -> None:
        self.t += dt

    # ── rendering ────────────────────────────────────────────────────────────
    def render(self, surf: pygame.Surface) -> None:
        _gradient_bg(surf)
        _draw_overlay_stars(surf, self._stars, self.t + 1.4)

        _outlined_title(surf, "STORE", (W // 2, 36),
                        size=32, px=2, shadow_offset=(2, 3))

        self._draw_balance(surf, cx=W // 2, y=78)

        # Placeholder until the item grid lands — keeps the shell shippable
        # and lets the menu wiring + layout be verified on their own.
        msg = _font(16, True).render("COMING SOON", True, _GOLD_PALE)
        msg.set_alpha(210)
        surf.blit(msg, msg.get_rect(center=(W // 2, H // 2 - 10)))
        sub = _font(12, True).render("Spend your coins on cool stuff",
                                     True, UI_CREAM)
        sub.set_alpha(190)
        surf.blit(sub, sub.get_rect(center=(W // 2, H // 2 + 14)))

        self.back_rect = _pill_btn(
            surf, (W // 2, H - 40), "BACK",
            size=18, alpha=235, min_width=160, dim=True, shadow=False)

    def _draw_balance(self, surf, cx, y) -> None:
        """Gold coin glyph + the wallet balance, centred as a unit so the
        player always sees what they have to spend."""
        val = str(store_data.balance())
        vf = _font(22, True)
        vimg = vf.render(val, True, _GOLD_BRIGHT)
        coin_d = 22
        gap = 6
        total_w = coin_d + gap + vimg.get_width()
        x0 = cx - total_w // 2
        _coin_icon(surf, x0 + coin_d // 2, y, coin_d // 2)
        surf.blit(vimg, vimg.get_rect(midleft=(x0 + coin_d + gap, y)))

    # ── input ────────────────────────────────────────────────────────────────
    def handle_tap(self, pos) -> "str | None":
        """Return an action token for the App to route on. Keyboard taps
        (pos is None) dismiss the store, matching the other menu sub-screens."""
        if pos is None:
            return "back"
        if self.back_rect and self.back_rect.collidepoint(pos):
            return "back"
        return None
