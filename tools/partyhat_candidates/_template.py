"""Shared scaffolding for PARTY HAT redesign candidates (SCRATCH ONLY).

Each design_N.py defines its own ``draw_hat(surf, cx, base_y, head_w, facing)``
side-profile drawer, then calls ``make_build(draw_hat, seat=...)`` to expose the
``build(frame_idx, tilt_deg) -> Surface`` the render harness consumes.

Mirrors game/hat_skins.py exactly: the in-game look is the base macaw with the
hat drawn small on its head via store_skins._make_skin; the head centres on HX
with crown-top at CROWN_Y. ``seat`` is the per-hat trim (dx/dy/hw/facing) the
production _SEAT dict applies — tune it so the hat sits ON the crown.
"""
from game import parrot  # noqa: F401 — ensure pygame/display set up by caller
from game.store_skins import _make_skin, HX, CROWN_Y

_HEAD_CX = HX
_HEAD_BASE_Y = CROWN_Y + 3
_HEAD_HW = 30


def make_build(draw_hat, *, seat=None):
    """Wrap a side-profile draw_hat into a build(frame_idx, tilt) skin getter."""
    s = seat or {}
    cx = _HEAD_CX + s.get("dx", 0)
    base_y = _HEAD_BASE_Y + s.get("dy", 0)
    head_w = s.get("hw", _HEAD_HW)
    facing = s.get("facing", 1)

    def paint(comp, _wing_angle_deg):  # head is stationary across wing frames
        draw_hat(comp, cx, base_y, head_w, facing)

    return _make_skin(paint)


# ── product-shot icon (store card) — matches hat_skins._build_icon ───────────
import pygame  # noqa: E402

_ICON_HW = 78
_ICON_CANVAS = 208
_ICON_CX = _ICON_CANVAS // 2
_ICON_BASE_Y = 138


def make_icon(draw_hat) -> pygame.Surface:
    surf = pygame.Surface((_ICON_CANVAS, _ICON_CANVAS), pygame.SRCALPHA)
    draw_hat(surf, _ICON_CX, _ICON_BASE_Y, _ICON_HW, 1)
    return parrot._add_outline(surf)
