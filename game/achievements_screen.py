"""
Achievements screen — a scrollable, category-grouped list of every unlockable.

The full list (taller than the 360×640 canvas) is rendered ONCE into a tall
supersampled surface and only rebuilt when the set of unlocked ids changes
(same cache discipline as the leaderboard). Each frame blits the visible slice
into a viewport between a fixed header and a pulsing footer prompt, plus a live
scrollbar. Scrolling is mouse-wheel + pointer-drag; a drag that barely moves is
treated as a tap to dismiss (the App decides on `pointer_up()`).
"""
from __future__ import annotations

import math
import pygame

from game.config import W, H
from game.draw import lerp_color
from game.hud import (
    _font, _outlined_text,
    _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP,
    _PANEL_DARK, _PANEL_LIGHTER, _NIGHT_DEEP,
)
from game import achievements as ach
from game.achievement_icons import draw_badge

_WHITE = (245, 246, 255)
_DIM   = (150, 150, 172)

# Layout (logical px).
_HEADER_H = 56          # taller: title + a global progress bar live here
_FOOTER_H = 30
_CAT_H    = 30
_ROW_H    = 56          # tightened ~10% for better scan density
_ROW_GAP  = 5
_PAD_X    = 12
_BADGE    = 44

# The gold underline beneath the ACHIEVEMENTS title — the category hairlines
# reuse this weight + horizontal inset so the whole screen reads as one system.
_RULE_INSET = 40

_S = 2  # supersample for the tall content surface


class AchievementsScene:
    WHEEL_STEP = 56
    _TAP_SLOP = 8

    def __init__(self):
        self.scroll_offset = 0.0
        self.max_scroll = 0.0
        self._t = 0.0
        self._drag_active = False
        self._drag_last = 0
        self._drag_moved = 0
        self._content: "pygame.Surface | None" = None
        self._content_h = 0          # logical content height
        self._cache_key = None

    # ── input ────────────────────────────────────────────────────────────
    def scroll_by(self, dpx: float) -> None:
        self.scroll_offset = max(0.0, min(self.max_scroll, self.scroll_offset + dpx))

    def pointer_down(self, y: int) -> None:
        self._drag_active = True
        self._drag_last = y
        self._drag_moved = 0

    def pointer_move(self, y: int) -> None:
        if not self._drag_active:
            return
        dy = y - self._drag_last
        self.scroll_by(-dy)
        self._drag_moved += abs(dy)
        self._drag_last = y

    def pointer_up(self) -> bool:
        """Return True when the gesture was a tap (dismiss), False for a drag."""
        if not self._drag_active:
            return False
        self._drag_active = False
        return self._drag_moved < self._TAP_SLOP

    def update(self, dt: float) -> None:
        self._t += dt

    # ── content build (cached) ───────────────────────────────────────────
    def _viewport(self) -> "tuple[int, int]":
        top = _HEADER_H
        bot = H - _FOOTER_H
        return top, bot

    def _ensure_content(self, store: dict) -> None:
        key = (ach.unlocked_signature(store),)
        if self._content is not None and key == self._cache_key:
            return
        self._cache_key = key

        # Measure logical height first.
        h = 4
        for cat in ach.CATEGORY_ORDER:
            h += _CAT_H
            h += len(ach.BY_CAT[cat]) * (_ROW_H + _ROW_GAP)
        h += 6
        self._content_h = h

        S = _S
        surf = pygame.Surface((W * S, h * S), pygame.SRCALPHA)
        y = 4
        for cat in ach.CATEGORY_ORDER:
            self._draw_cat_header(surf, cat, y, store, S)
            y += _CAT_H
            for a in ach.BY_CAT[cat]:
                self._draw_row(surf, a, y, store, S)
                y += _ROW_H + _ROW_GAP
        self._content = surf

        top, bot = self._viewport()
        self.max_scroll = max(0.0, self._content_h - (bot - top))
        self.scroll_offset = min(self.scroll_offset, self.max_scroll)

    def _draw_cat_header(self, surf, cat, y, store, S):
        got, total = ach.category_progress(store, cat)
        complete = got >= total and total > 0
        head_col = _GOLD_PALE if complete else _GOLD_BRIGHT

        # A small gold diamond pip leads the section title — a struck-metal
        # bullet that echoes the badge rim and sets the title off the rail.
        py = int((y + _CAT_H * 0.5) * S)
        d = int(4 * S)
        pip = [(_PAD_X * S, py), (_PAD_X * S + d, py - d),
               (_PAD_X * S + 2 * d, py), (_PAD_X * S + d, py + d)]
        pygame.draw.polygon(surf, head_col, pip)
        pygame.draw.polygon(surf, _GOLD_DEEP, pip, max(1, S))

        label = self._scaled_text(cat.upper(), 15 * S, head_col)
        lx = _PAD_X * S + 3 * d
        surf.blit(label, (lx, int((y + 5) * S)))

        cnt = self._scaled_text(f"{got}/{total}", 13 * S, _GOLD_DEEP)
        cnt_x = int((W - _PAD_X) * S - cnt.get_width())
        surf.blit(cnt, (cnt_x, int((y + 6) * S)))

        # Engraved rule between the title and the count — same weight + fade as
        # the gold underline under the ACHIEVEMENTS title, so the category bands
        # and the header read as one system rather than two unrelated rules.
        ry = int((y + _CAT_H - 6) * S)
        rail_l = lx + label.get_width() + 6 * S
        rail_r = cnt_x - 6 * S
        if rail_r > rail_l:
            rail = pygame.Surface((rail_r - rail_l, max(2, 2 * S)), pygame.SRCALPHA)
            for xx in range(rail.get_width()):
                fade = 1.0 - xx / max(1, rail.get_width())
                rail.fill((*_GOLD_BRIGHT, int(160 * fade)),
                          (xx, 0, 1, max(2, 2 * S)))
            surf.blit(rail, (rail_l, ry))

    def _scaled_text(self, txt, size, color):
        return _font(int(size), True).render(txt, True, color)

    def _draw_row(self, surf, a: "ach.Achievement", y, store, S):
        unlocked = ach.is_unlocked(store, a.id)
        rx = _PAD_X * S
        rw = (W - _PAD_X * 2) * S
        ry = y * S
        rh = _ROW_H * S
        rad = 12 * S

        # Row panel.
        body_top = _PANEL_LIGHTER if unlocked else (18, 14, 40)
        body_bot = _PANEL_DARK if unlocked else (10, 7, 26)
        panel = pygame.Surface((rw, rh), pygame.SRCALPHA)
        for yy in range(rh):
            t = yy / max(1, rh - 1)
            pygame.draw.line(panel, lerp_color(body_top, body_bot, t), (0, yy), (rw, yy))
        mask = pygame.Surface((rw, rh), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, rw, rh), border_radius=rad)
        panel.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        border = (*_GOLD_BRIGHT, 180) if unlocked else (90, 86, 120, 140)
        pygame.draw.rect(panel, border, (0, 0, rw, rh), width=max(1, S), border_radius=rad)
        # Earned rows wear a bright gold accent stripe down the left edge — a
        # quick "this one's yours" read while scanning a long list.
        if unlocked:
            stripe = pygame.Surface((max(3, 4 * S), rh - 8 * S), pygame.SRCALPHA)
            for yy in range(stripe.get_height()):
                t = yy / max(1, stripe.get_height() - 1)
                stripe.fill(lerp_color(_GOLD_PALE, _GOLD_DEEP, t), (0, yy, stripe.get_width(), 1))
            sm = pygame.Surface(stripe.get_size(), pygame.SRCALPHA)
            pygame.draw.rect(sm, (255, 255, 255, 255), sm.get_rect(), border_radius=max(1, 2 * S))
            stripe.blit(sm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            panel.blit(stripe, (3 * S, 4 * S))
        surf.blit(panel, (rx, ry))

        # Badge.
        badge_rect = pygame.Rect(int(rx + 8 * S), int(ry + (rh - _BADGE * S) // 2),
                                 _BADGE * S, _BADGE * S)
        draw_badge(surf, a.icon_key, badge_rect, unlocked, a.hidden)

        # Text block.
        tx = int(rx + (8 + _BADGE + 10) * S)
        hidden_locked = a.hidden and not unlocked
        title = "???" if hidden_locked else a.title
        if unlocked:
            desc = a.desc
            tcol, dcol = _GOLD_PALE, _WHITE
        elif hidden_locked:
            desc = "Hidden — keep playing to discover it."
            tcol, dcol = _DIM, _DIM
        else:
            desc = a.desc
            tcol, dcol = (200, 196, 220), _DIM

        ts = self._scaled_text(title, 17 * S, tcol)
        surf.blit(ts, (tx, int(ry + 9 * S)))

        # Description / requirement (wrapped to one or two short lines).
        self._blit_wrapped(surf, desc, tx, int(ry + 30 * S),
                           int((W - _PAD_X) * S - tx - 8 * S), 12 * S, dcol)

        # Unlocked check, or progress bar for incremental life-scope locks.
        if unlocked:
            star_cx = int((W - _PAD_X) * S - 12 * S)
            star_cy = int(ry + 16 * S)
            self._draw_star(surf, star_cx, star_cy, 8 * S)
        else:
            cur = ach.current_value(store, a)
            if cur is not None and a.target > 1:
                frac = max(0.0, min(1.0, cur / a.target))
                self._draw_progress(surf, tx, int(ry + rh - 14 * S),
                                    int((W - _PAD_X) * S - tx - 8 * S), S,
                                    frac, f"{min(cur, a.target)}/{a.target}")

    def _gilded_count(self, txt, size):
        """The header counter rendered with a vertical gold gradient fill (pale
        crest → deep base) so it matches the gilded title rather than sitting as
        a flat orphaned label."""
        base = _font(size, True).render(txt, True, _GOLD_PALE)
        w, h = base.get_size()
        grad = pygame.Surface((w, h), pygame.SRCALPHA)
        for yy in range(h):
            t = yy / max(1, h - 1)
            grad.fill(lerp_color(_GOLD_PALE, _GOLD_DEEP, t), (0, yy, w, 1))
        grad.blit(base, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        out = pygame.Surface((w + 2, h + 2), pygame.SRCALPHA)
        sh = _font(size, True).render(txt, True, (20, 12, 4))
        out.blit(sh, (1, 1))
        out.blit(grad, (0, 0))
        return out

    def _draw_star(self, surf, cx, cy, rad):
        """Procedural five-point "earned" star — the bundled bold font has no
        U+2605 glyph, so the badge family's star is drawn instead of typeset."""
        pts = []
        for i in range(10):
            ang = -math.pi / 2 + i * math.pi / 5
            rr = rad if i % 2 == 0 else rad * 0.42
            pts.append((cx + math.cos(ang) * rr, cy + math.sin(ang) * rr))
        pygame.draw.polygon(surf, _GOLD_BRIGHT, [(int(x), int(y)) for x, y in pts])
        pygame.draw.polygon(surf, _GOLD_DEEP, [(int(x), int(y)) for x, y in pts], max(1, _S))

    def _blit_wrapped(self, surf, text, x, y, maxw, size, color):
        f = _font(int(size), True)
        words = text.split(" ")
        lines, cur = [], ""
        for w in words:
            trial = (cur + " " + w).strip()
            if f.size(trial)[0] <= maxw or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        for i, ln in enumerate(lines[:2]):
            img = f.render(ln, True, color)
            surf.blit(img, (x, y + i * int(size * 1.15)))

    def _draw_progress(self, surf, x, y, w, S, frac, label):
        h = 7 * S
        pygame.draw.rect(surf, (8, 5, 24), (x, y, w, h), border_radius=h // 2)
        fw = int(w * frac)
        if fw > 0:
            bar = pygame.Surface((fw, h), pygame.SRCALPHA)
            for yy in range(h):
                t = yy / max(1, h - 1)
                pygame.draw.line(bar, lerp_color(_GOLD_PALE, _GOLD_DEEP, t), (0, yy), (fw, yy))
            pygame.draw.rect(bar, (255, 255, 255, 0), (0, 0, fw, h), border_radius=h // 2)
            surf.blit(bar, (x, y))
        pygame.draw.rect(surf, (*_GOLD_BRIGHT, 120), (x, y, w, h), width=max(1, S), border_radius=h // 2)
        lab = self._scaled_text(label, 11 * S, _GOLD_PALE)
        surf.blit(lab, (x + w - lab.get_width(), y - int(13 * S)))

    # ── per-frame render ─────────────────────────────────────────────────
    def render(self, surf, dt: float, store: dict) -> None:
        self._t += dt
        self._ensure_content(store)

        # Background — deep night gradient.
        for yy in range(H):
            t = yy / (H - 1)
            pygame.draw.line(surf, lerp_color(_NIGHT_DEEP, (14, 8, 36), t), (0, yy), (W, yy))

        top, bot = self._viewport()
        view_h = bot - top
        S = _S

        # Visible slice of the tall content surface.
        src_y = int(self.scroll_offset * S)
        src_h = min(view_h * S, self._content.get_height() - src_y)
        if src_h > 0:
            slice_src = pygame.Rect(0, src_y, W * S, src_h)
            sub = self._content.subsurface(slice_src)
            scaled = pygame.transform.smoothscale(sub, (W, src_h // S))
            surf.blit(scaled, (0, top))

        # Scrollbar.
        if self.max_scroll > 0:
            track_x = W - 5
            pygame.draw.rect(surf, (255, 255, 255, 30), (track_x, top, 3, view_h),
                             border_radius=2)
            thumb_h = max(24, int(view_h * view_h / (self._content_h)))
            travel = view_h - thumb_h
            thumb_y = top + int((self.scroll_offset / self.max_scroll) * travel)
            pygame.draw.rect(surf, _GOLD_BRIGHT, (track_x, thumb_y, 3, thumb_h),
                             border_radius=2)

        # Header bar (over the scrolling content).
        hdr = pygame.Surface((W, _HEADER_H), pygame.SRCALPHA)
        hdr.fill((*_NIGHT_DEEP, 235))
        pygame.draw.line(hdr, (*_GOLD_BRIGHT, 120), (0, _HEADER_H - 1), (W, _HEADER_H - 1), 1)
        surf.blit(hdr, (0, 0))
        _outlined_text(surf, "ACHIEVEMENTS", (W // 2, 16),
                       size=26, px=2, shadow_offset=(2, 3))
        # Gilded gold underline under the title — the visual anchor the category
        # hairlines echo.
        uw = 132
        ux = W // 2 - uw // 2
        pygame.draw.line(surf, _GOLD_BRIGHT, (ux, 30), (ux + uw, 30), 2)

        total = len(ach.ACHIEVEMENTS)
        got = len(store.get("unlocked") or {})

        # Gilded "N / total" counter — same gradient treatment as the title so
        # it reads as part of the header, not an orphaned label.
        cnt = self._gilded_count(f"{got} / {total}", 14)
        surf.blit(cnt, (W - cnt.get_width() - 8, 6))

        # Global progress bar — a gold bar spanning the header inset, showing
        # total unlocked / total at a glance. Thickened and given a faint inner
        # top-shadow on the empty track so the filled gold portion reads as a
        # filled vessel, matching the minted-metal language of the badges.
        gbh = 6
        gbx = _RULE_INSET
        gbw = W - _RULE_INSET * 2
        gby = _HEADER_H - 11
        frac = (got / total) if total else 0.0
        pygame.draw.rect(surf, (8, 5, 24), (gbx, gby, gbw, gbh), border_radius=gbh // 2)
        # inner top-shadow line so the track reads as a sunken channel
        pygame.draw.line(surf, (4, 2, 14), (gbx + 1, gby + 1), (gbx + gbw - 2, gby + 1), 1)
        fw = int(gbw * max(0.0, min(1.0, frac)))
        if fw > 0:
            bar = pygame.Surface((fw, gbh), pygame.SRCALPHA)
            for xx in range(fw):
                t = xx / max(1, fw - 1)
                bar.fill(lerp_color(_GOLD_PALE, _GOLD_BRIGHT, t), (xx, 0, 1, gbh))
            surf.blit(bar, (gbx, gby))
        pygame.draw.rect(surf, (*_GOLD_BRIGHT, 110), (gbx, gby, gbw, gbh),
                         width=1, border_radius=gbh // 2)

        # Footer prompt — pulsing.
        ftr = pygame.Surface((W, _FOOTER_H), pygame.SRCALPHA)
        ftr.fill((*_NIGHT_DEEP, 230))
        pygame.draw.line(ftr, (*_GOLD_BRIGHT, 100), (0, 0), (W, 0), 1)
        surf.blit(ftr, (0, H - _FOOTER_H))
        a = int(180 + 60 * math.sin(self._t * 4.0))
        tip = _font(13, True).render("TAP TO RETURN  ·  DRAG TO SCROLL", True, _GOLD_PALE)
        tip.set_alpha(a)
        surf.blit(tip, tip.get_rect(center=(W // 2, H - _FOOTER_H // 2)))
