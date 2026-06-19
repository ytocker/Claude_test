"""
Prize Machine — the Store's gacha centerpiece.

Spend a fixed coin cost to roll a random *unowned* cosmetic, revealed through
the slot-machine cabinet the LOTTERY power-up already uses (reused from
game.lottery_slot at a centred, store-sized anchor). Because the roll only
ever draws from the unowned pool, every paid roll is a guaranteed-new unlock —
there are no duplicates to refund.

The store gates the spend before opening a reveal (see game/store.py): an
unaffordable tap or an everything-already-owned tap never charges and never
enters this scene. ``roll`` here is the pure selection used by both the live
flow and the unit tests.
"""
from __future__ import annotations

import math
import random

import pygame

from game.config import W, H
from game.hud import _font, _draw_overlay_stars, _GOLD_BRIGHT, _GOLD_PALE
from game.draw import UI_CREAM
from game.powerup_help import _gradient_bg, _outlined_title, _seeded_stars
from game.lottery_slot import draw_prize_reveal, PRIZE_SPIN, CAB_W, CAB_H
from game import parrot
from game import store_catalog
from game import store_data

_rng = random.Random()

# Cabinet anchor: horizontally centred, in the upper third so the won-skin
# hero has room to burst out below it.
_CAB_ORIGIN = ((W - CAB_W) // 2, 118)
_HERO_BOX = 132  # max dimension of the revealed skin sprite
_POP_TIME = 0.45  # hero scale-in duration after the reels lock


def unowned_pool() -> list:
    """Cosmetic ids the player doesn't own yet — the Prize Machine pool."""
    return [i for i in store_catalog.cosmetic_ids() if not store_data.is_owned(i)]


def roll():
    """Return a random unowned cosmetic id, or None if everything is owned.
    Pure selection — never spends or grants (the caller commits the spend and
    records the win), so a test can assert it never returns an owned item."""
    pool = unowned_pool()
    if not pool:
        return None
    return _rng.choice(pool)


def _build_hero(item_id: str) -> pygame.Surface:
    # Crop to opaque content first so skins with tall headgear composites and
    # the 64px redraws all fill the hero box consistently.
    src = parrot.get_skin_frame(item_id, 1, 0.0)
    bb = src.get_bounding_rect()
    if bb.width > 0 and bb.height > 0:
        src = src.subsurface(bb).copy()
    sw, sh = src.get_size()
    scale = _HERO_BOX / max(sw, sh)
    return pygame.transform.smoothscale(
        src, (max(1, int(sw * scale)), max(1, int(sh * scale))))


class PrizeReveal:
    """Owns the Store's "prize" sub-mode: animates one already-decided roll
    (``item_id`` won, already granted by the store) through the cabinet spin,
    the lock, and a popping hero reveal of the new skin."""

    def __init__(self, item_id: str) -> None:
        self.item_id = item_id
        self.win = item_id is not None
        self.t = 0.0
        self._stars = _seeded_stars()
        self._hero = _build_hero(item_id) if self.win else None

    def update(self, dt: float) -> None:
        self.t += dt

    def can_dismiss(self) -> bool:
        # Hold the reveal a beat after the pop so the player registers the
        # prize before a stray tap dismisses it.
        return self.t >= PRIZE_SPIN + _POP_TIME + 0.35

    # ── rendering ────────────────────────────────────────────────────────────
    def render(self, surf: pygame.Surface) -> None:
        _gradient_bg(surf)
        _draw_overlay_stars(surf, self._stars, self.t + 1.4)
        _outlined_title(surf, "PRIZE MACHINE", (W // 2, 40),
                        size=26, px=2, shadow_offset=(2, 3))

        draw_prize_reveal(surf, {"t": self.t, "win": self.win}, _CAB_ORIGIN)

        revealed = self.t - PRIZE_SPIN
        if self.win and revealed >= 0.0:
            self._draw_hero(surf, revealed)
        elif not self.win and revealed >= 0.0:
            self._draw_all_owned(surf)

        if self.can_dismiss():
            prompt = _font(13, True).render("TAP TO CONTINUE", True, _GOLD_PALE)
            prompt.set_alpha(int(190 + 60 * math.sin(self.t * 4)))
            surf.blit(prompt, prompt.get_rect(center=(W // 2, H - 54)))

    def _draw_hero(self, surf, revealed: float) -> None:
        # Pop the hero with a slight overshoot for juice.
        p = min(1.0, revealed / _POP_TIME)
        ease = 1 - (1 - p) * (1 - p)
        scale = (0.2 + 0.8 * ease) * (1.0 + 0.12 * math.sin(p * math.pi))
        cy = 400
        hero = self._hero
        hw, hh = hero.get_size()
        scaled = pygame.transform.smoothscale(
            hero, (max(1, int(hw * scale)), max(1, int(hh * scale))))
        surf.blit(scaled, scaled.get_rect(center=(W // 2, cy)))

        if p >= 0.6:
            _outlined_title(surf, "NEW SKIN!", (W // 2, cy - _HERO_BOX // 2 - 14),
                            size=22, px=2, shadow_offset=(2, 2))
            nimg = _font(20, True).render(store_catalog.name(self.item_id),
                                          True, _GOLD_BRIGHT)
            surf.blit(nimg, nimg.get_rect(center=(W // 2, cy + _HERO_BOX // 2 + 12)))
            sub = _font(12, True).render("Added to your collection", True, UI_CREAM)
            sub.set_alpha(200)
            surf.blit(sub, sub.get_rect(center=(W // 2, cy + _HERO_BOX // 2 + 34)))

    def _draw_all_owned(self, surf) -> None:
        msg = _font(18, True).render("EVERYTHING UNLOCKED!", True, _GOLD_BRIGHT)
        surf.blit(msg, msg.get_rect(center=(W // 2, 360)))
        sub = _font(13, True).render("No coins spent", True, UI_CREAM)
        sub.set_alpha(200)
        surf.blit(sub, sub.get_rect(center=(W // 2, 388)))

    # ── input ────────────────────────────────────────────────────────────────
    def handle_tap(self, pos) -> "str | None":
        """Tap fast-forwards the spin; once the reveal has settled a tap
        returns "done" so the store drops back to the grid."""
        if self.can_dismiss():
            return "done"
        # Skip the build-up straight to the lock so an impatient player isn't
        # forced to watch the full spin.
        self.t = max(self.t, PRIZE_SPIN)
        return None
