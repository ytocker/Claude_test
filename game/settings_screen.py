"""
Settings screen — a full-screen list of launchers, in the achievements-screen
family (night-sky bg + gilded header + grounded MENU pill). Today it holds two
items, How to Play and Power-Ups, each a tappable row that opens the matching
scene; it is laid out to take more rows later (audio, reduced-motion, …) without
a redesign. Pure procedural render; no target-divergent code.
"""
from __future__ import annotations

import math
import random

import pygame

from game.config import W, H
from game.draw import lerp_color
from game.hud import (
    _font, _outlined_text, _outline_pill_btn, _volume_panel, _draw_gear,
    _draw_overlay_stars, _draw_mountain_silhouette,
    _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP, _NIGHT_DEEP,
)

_WHITE    = (245, 246, 255)
_DIM      = (150, 150, 172)
_NAVY_INK = (10, 6, 30)          # near-black ink for glyphs on the gold discs

_HEADER_H = 56
_FOOTER_H = 54


# Seeded twinkle field so Settings lives in the same night world as the menu +
# achievements wall (same seed-42 discipline).
_STARS: list = []
def _star_field():
    if not _STARS:
        rng = random.Random(42)
        for _ in range(46):
            _STARS.append((rng.randint(6, W - 6), rng.randint(8, H - 150),
                           rng.choice((1, 1, 1, 2)), rng.uniform(0, 6.28)))
    return _STARS


def _section_header(surf, text, y):
    """Gold diamond pip + tracked caps + a fading engraved rule — the
    achievements category band, so the group reads as one system."""
    py = y + 9
    d = 4
    px0 = 14
    pip = [(px0, py), (px0 + d, py - d), (px0 + 2 * d, py), (px0 + d, py + d)]
    pygame.draw.polygon(surf, _GOLD_BRIGHT, pip)
    pygame.draw.polygon(surf, _GOLD_DEEP, pip, 1)
    lab = _font(14, True).render(text, True, _GOLD_BRIGHT)
    lx = px0 + 3 * d
    surf.blit(lab, (lx, y + 1))
    rail_l = lx + lab.get_width() + 8
    rail_r = W - 12
    if rail_r > rail_l:
        rail = pygame.Surface((rail_r - rail_l, 2), pygame.SRCALPHA)
        for xx in range(rail.get_width()):
            fade = 1.0 - xx / max(1, rail.get_width())
            rail.fill((*_GOLD_BRIGHT, int(150 * fade)), (xx, 0, 1, 2))
        surf.blit(rail, (rail_l, py))


def _chevron(surf, cx, cy, s, color, w=3):
    pygame.draw.line(surf, color, (cx - s * 0.35, cy - s), (cx + s * 0.4, cy), w)
    pygame.draw.line(surf, color, (cx + s * 0.4, cy), (cx - s * 0.35, cy + s), w)


def _icon_disc(surf, cx, cy, r):
    """Gold coin-like backer the row glyph sits on — a struck disc, top-lit body
    gradient + a dark rim (no highlight dot, so the disc reads clean)."""
    disc = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
    cc = r + 2
    for yy in range(r * 2):
        f = yy / max(1, r * 2 - 1)
        col = lerp_color(_GOLD_PALE, _GOLD_DEEP, f)
        half = int(math.sqrt(max(0, r * r - (yy - r) ** 2)))
        pygame.draw.line(disc, col, (cc - half, yy + 2), (cc + half, yy + 2))
    pygame.draw.circle(disc, _GOLD_DEEP, (cc, cc), r, 2)
    surf.blit(disc, (cx - cc, cy - cc))


def _g_book(surf, cx, cy, s, ink=_NAVY_INK):
    left = [(cx, cy - s * 0.8), (cx - s, cy - s * 0.5),
            (cx - s, cy + s * 0.8), (cx, cy + s * 0.5)]
    right = [(cx, cy - s * 0.8), (cx + s, cy - s * 0.5),
             (cx + s, cy + s * 0.8), (cx, cy + s * 0.5)]
    pygame.draw.polygon(surf, ink, left, 2)
    pygame.draw.polygon(surf, ink, right, 2)
    pygame.draw.line(surf, ink, (cx, cy - s * 0.8), (cx, cy + s * 0.5), 2)
    for k in range(1, 3):
        yy = cy - s * 0.35 + k * s * 0.4
        pygame.draw.line(surf, ink, (cx - s * 0.75, yy), (cx - s * 0.2, yy + 0.15 * s), 1)
        pygame.draw.line(surf, ink, (cx + s * 0.2, yy + 0.15 * s), (cx + s * 0.75, yy), 1)


def _g_bolt(surf, cx, cy, s, ink=_NAVY_INK):
    pts = [
        (cx + s * 0.18, cy - s),
        (cx - s * 0.55, cy + s * 0.12),
        (cx - s * 0.05, cy + s * 0.12),
        (cx - s * 0.22, cy + s),
        (cx + s * 0.55, cy - s * 0.18),
        (cx + s * 0.05, cy - s * 0.18),
    ]
    pygame.draw.polygon(surf, ink, pts)
    pygame.draw.polygon(surf, _NAVY_INK, pts, 1)


_GLYPHS = {"book": _g_book, "bolt": _g_bolt}


class SettingsScene:
    """Static two-row launcher list. Taps route through App._flap_input, which
    hit-tests the row rects + MENU button this scene publishes each frame."""

    # Row order + which App action each opens (resolved by scenes.py).
    ROWS = (
        ("book", "How to Play", "Controls & the basics", "howto"),
        ("bolt", "Power-Ups",   "What every pickup does", "powerups"),
    )

    def __init__(self):
        self._t = 0.0
        # Published each frame for the tap router: [(rect, action), …] + MENU.
        self.row_rects: list = []
        self.menu_btn_rect: "pygame.Rect | None" = None

    def update(self, dt: float) -> None:
        self._t += dt

    def render(self, surf, dt: float) -> None:
        # Background — the menu/achievements night world.
        for yy in range(H):
            f = yy / (H - 1)
            pygame.draw.line(surf, lerp_color(_NIGHT_DEEP, (14, 8, 36), f),
                             (0, yy), (W, yy))
        _draw_overlay_stars(surf, _star_field(), self._t)
        _draw_mountain_silhouette(surf, alpha=130)

        # Header — a struck cog + outlined SETTINGS + gold underline rule.
        hdr = pygame.Surface((W, _HEADER_H), pygame.SRCALPHA)
        hdr.fill((*_NIGHT_DEEP, 235))
        surf.blit(hdr, (0, 0))
        _draw_gear(surf, 26, 22, 11)
        _outlined_text(surf, "SETTINGS", (W // 2, 16), size=22, px=2,
                       shadow_offset=(2, 3))
        uw = 152
        ux = W // 2 - uw // 2
        pygame.draw.line(surf, _GOLD_BRIGHT, (ux, 30), (ux + uw, 30), 2)
        pygame.draw.line(surf, (*_GOLD_BRIGHT, 90),
                         (0, _HEADER_H - 1), (W, _HEADER_H - 1), 1)

        # HELP group, vertically centred in the open body so two rows don't
        # cling to the top and strand the canvas.
        row_h, gap, hdr_gap = 68, 12, 34
        group_h = hdr_gap + len(self.ROWS) * row_h + (len(self.ROWS) - 1) * gap
        body_top, body_bot = _HEADER_H, H - _FOOTER_H
        top = body_top + (body_bot - body_top - group_h) // 2
        _section_header(surf, "HELP", top)

        self.row_rects = []
        y = top + hdr_gap
        for kind, label, sub, action in self.ROWS:
            rect = pygame.Rect(6, y, W - 12, row_h)
            _volume_panel(surf, rect, radius=13)
            cy = rect.centery
            _icon_disc(surf, 42, cy, 21)
            _GLYPHS[kind](surf, 42, cy, 13)
            surf.blit(_font(18, True).render(label, True, _GOLD_PALE), (78, y + 15))
            surf.blit(_font(12, True).render(sub, True, _DIM), (78, y + 40))
            _chevron(surf, W - 28, cy, 8, _GOLD_BRIGHT)
            self.row_rects.append((rect, action))
            y += row_h + gap

        # Footer — the grounded MENU pill, the only way back.
        fy = H - _FOOTER_H
        ftr = pygame.Surface((W, _FOOTER_H), pygame.SRCALPHA)
        ftr.fill((*_NIGHT_DEEP, 236))
        surf.blit(ftr, (0, fy))
        pygame.draw.line(surf, (*_GOLD_BRIGHT, 120), (0, fy), (W, fy), 1)
        self.menu_btn_rect = _outline_pill_btn(
            surf, (W // 2, fy + _FOOTER_H // 2), "MENU", size=15, min_width=150)
