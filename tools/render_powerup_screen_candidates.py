"""Render 5 candidate "How power-ups work" explainer screens.

Each candidate is a 360x640 portrait PNG that uses the game's existing
visual language: gold-on-red outlined titles, deep-purple panels with
faint orange accents, twinkling star fields, the exact powerup icons
from the in-world sprites, and (where it fits) the welcome-screen
mountain silhouette.

Run from repo root:
    python3 tools/render_powerup_screen_candidates.py
"""
import os
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "dummy"

import math
import sys

import pygame
pygame.init()

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.config import W, H, POWERUP_R
from game.draw import (
    rounded_rect, rounded_rect_grad, lerp_color,
    UI_GOLD, UI_ORANGE, UI_RED, UI_CREAM, NEAR_BLACK, WHITE,
)
from game.hud import (
    _font, _outlined_text, _pill_btn, _dark_panel,
    _draw_overlay_stars, _draw_mountain_silhouette,
    _draw_buff_icon,
    _GOLD_BRIGHT, _GOLD_MUTED, _ORANGE_BORDER, _RED_OUTLINE,
    _PANEL_DARK, _NIGHT_DEEP,
)
from game.entities import PowerUp

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "docs", "screenshots", "powerup_screen_candidates")
os.makedirs(OUT_DIR, exist_ok=True)

# ── Powerup data — every kind in spawn order, with a short blurb ─────────────
POWERUPS = [
    ("triple",   "TRIPLE",   "Coins are worth 3x for 8 seconds."),
    ("magnet",   "MAGNET",   "Pulls nearby coins straight to Pip."),
    ("slowmo",   "SLOW-MO",  "Slows the whole world. Taps stay snappy."),
    ("kfc",      "KFC",      "Fried-chicken Pip. Coins turn to fries."),
    ("ghost",    "GHOST",    "Phase through pillars. Floor still kills."),
    ("grow",     "GROW",     "Pip grows 1.5x. Bigger and bolder."),
    ("surprise", "SURPRISE", "Random pick from the six above."),
]


# ── Shared background helpers ────────────────────────────────────────────────
def _seeded_stars(seed: int = 42, n: int = 60, top=8, bot=H - 30):
    import random
    rng = random.Random(seed)
    return [
        (rng.randint(8, W - 8), rng.randint(top, bot),
         rng.choice((1, 1, 1, 2)), rng.uniform(0, 6.28))
        for _ in range(n)
    ]


def _gradient_bg(surf):
    """Deep night-sky vertical gradient used as the screen base."""
    TOP = (8, 4, 32)
    MID = (16, 8, 50)
    BOT = (24, 14, 70)
    h = surf.get_height()
    for y in range(h):
        t = y / max(1, h - 1)
        if t < 0.5:
            c = lerp_color(TOP, MID, t * 2)
        else:
            c = lerp_color(MID, BOT, (t - 0.5) * 2)
        pygame.draw.line(surf, c, (0, y), (surf.get_width() - 1, y))


def _draw_powerup_icon(surf, kind: str, cx: int, cy: int, size_px: int):
    """Render a powerup icon at an arbitrary size. We render the actual
    `PowerUp` sprite to a 64x64 canvas (over-sized so glow/halo aren't
    clipped) then smoothscale to `size_px`. For `surprise` the source
    sprite is already a fixed-size cached surface, so we re-render it on
    the canvas just like the others."""
    canvas = pygame.Surface((64, 64), pygame.SRCALPHA)
    p = PowerUp(32, 32, kind)
    p.pulse = 1.6   # mid-animation: arc visible, hourglass animated
    p.draw(canvas)
    if size_px != 64:
        canvas = pygame.transform.smoothscale(canvas, (size_px, size_px))
    surf.blit(canvas, canvas.get_rect(center=(cx, cy)))


def _gold_text(surf, txt, center, size=14, bold=True, alpha=255):
    f = _font(size, bold)
    img = f.render(txt, True, _GOLD_BRIGHT)
    img.set_alpha(alpha)
    r = img.get_rect(center=center)
    surf.blit(img, r.topleft)
    return r


def _cream_text_wrapped(surf, txt, center_x, top_y, max_w, size=12, color=UI_CREAM,
                        line_h_extra=2, bold=False):
    """Word-wrap blurb in a small cream-coloured font, returns total height."""
    f = _font(size, bold)
    words = txt.split()
    lines = []
    cur = ""
    for w in words:
        test = (cur + " " + w).strip()
        if f.size(test)[0] <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    total = 0
    for i, line in enumerate(lines):
        img = f.render(line, True, color)
        r = img.get_rect(midtop=(center_x, top_y + i * (size + line_h_extra)))
        surf.blit(img, r.topleft)
        total = r.bottom - top_y
    return total


def _save(surf, name):
    path = os.path.join(OUT_DIR, name)
    pygame.image.save(surf, path)
    print(f"  saved {os.path.relpath(path)}")


# ── Candidate 1: Vertical list — clean rows ─────────────────────────────────
def candidate_1():
    surf = pygame.Surface((W, H))
    _gradient_bg(surf)
    _draw_overlay_stars(surf, _seeded_stars(seed=11, n=55), t=0.7)
    _draw_mountain_silhouette(surf, alpha=140)

    # Title — same gold-on-red outlined styling as SKYBIT
    _outlined_text(surf, "POWER-UPS", (W // 2, 50),
                   size=38, px=2, shadow_offset=(2, 3))
    # Subtitle
    sub = _font(11, False).render("GRAB ONE FROM A PILLAR GAP",
                                  True, _GOLD_MUTED)
    sub.set_alpha(190)
    surf.blit(sub, sub.get_rect(center=(W // 2, 80)))
    pygame.draw.line(surf, (*_ORANGE_BORDER, 110),
                     (W // 2 - 80, 92), (W // 2 + 80, 92), 1)

    # 7 rows
    row_h = 58
    row_w = W - 24
    base_x = 12
    base_y = 108
    icon_size = 40

    for i, (kind, name, blurb) in enumerate(POWERUPS):
        ry = base_y + i * (row_h + 4)
        rect = pygame.Rect(base_x, ry, row_w, row_h)
        _dark_panel(surf, rect, radius=12, alpha=205)

        # Icon plate on the left
        icon_pad = 8
        icon_rect = pygame.Rect(rect.x + icon_pad, rect.y + (row_h - icon_size) // 2,
                                icon_size, icon_size)
        rounded_rect(surf, icon_rect, 8, (15, 25, 60), 215)
        _draw_powerup_icon(surf, kind,
                           icon_rect.centerx, icon_rect.centery, icon_size)

        # Name + blurb on the right
        text_x = icon_rect.right + 12
        name_img = _font(15, True).render(name, True, _GOLD_BRIGHT)
        surf.blit(name_img, (text_x, rect.y + 8))
        # Cream blurb, word-wrapped to fit the remaining width
        f = _font(11, False)
        words = blurb.split()
        cur = ""
        lines = []
        max_w = rect.right - text_x - 8
        for w in words:
            test = (cur + " " + w).strip()
            if f.size(test)[0] <= max_w:
                cur = test
            else:
                if cur: lines.append(cur)
                cur = w
        if cur: lines.append(cur)
        for li, line in enumerate(lines[:2]):
            img = f.render(line, True, UI_CREAM)
            surf.blit(img, (text_x, rect.y + 28 + li * 13))

    _save(surf, "candidate_1_list.png")


# ── Candidate 2: Card grid (2x3 + surprise full-width footer) ───────────────
def candidate_2():
    surf = pygame.Surface((W, H))
    _gradient_bg(surf)
    _draw_overlay_stars(surf, _seeded_stars(seed=22, n=60), t=1.4)

    _outlined_text(surf, "POWER-UPS", (W // 2, 46),
                   size=36, px=2, shadow_offset=(2, 3))
    sub = _font(11, False).render("SIX BOOSTS PLUS A WILD CARD",
                                  True, _GOLD_MUTED)
    sub.set_alpha(190)
    surf.blit(sub, sub.get_rect(center=(W // 2, 76)))

    # 2x3 grid for the six real kinds, then a full-width surprise card.
    grid_top = 96
    card_w = 162
    card_h = 116
    gap = 8
    base_x = (W - (card_w * 2 + gap)) // 2

    six = POWERUPS[:6]
    for idx, (kind, name, blurb) in enumerate(six):
        col = idx % 2
        row = idx // 2
        x = base_x + col * (card_w + gap)
        y = grid_top + row * (card_h + gap)
        card = pygame.Rect(x, y, card_w, card_h)
        _dark_panel(surf, card, radius=14, alpha=215)

        _draw_powerup_icon(surf, kind, card.centerx, card.y + 32, 48)

        nimg = _font(14, True).render(name, True, _GOLD_BRIGHT)
        surf.blit(nimg, nimg.get_rect(center=(card.centerx, card.y + 66)))

        _cream_text_wrapped(surf, blurb,
                            card.centerx, card.y + 80,
                            card_w - 16, size=10, line_h_extra=2)

    # Surprise full-width card sitting safely below the 3rd grid row
    sy = grid_top + 3 * (card_h + gap) + 4
    surprise_card = pygame.Rect(base_x, sy, card_w * 2 + gap, 70)
    _dark_panel(surf, surprise_card, radius=14, alpha=220)
    _draw_powerup_icon(surf, "surprise",
                       surprise_card.x + 40, surprise_card.centery, 50)
    nimg = _font(15, True).render("SURPRISE", True, _GOLD_BRIGHT)
    surf.blit(nimg, (surprise_card.x + 80, surprise_card.y + 12))
    _cream_text_wrapped(
        surf,
        "Gift box rerolls into one of the six above.",
        center_x=(surprise_card.x + 80 + surprise_card.right) // 2,
        top_y=surprise_card.y + 34,
        max_w=surprise_card.right - (surprise_card.x + 80) - 12,
        size=11, line_h_extra=2)

    _pill_btn(surf, (W // 2, H - 26), "TAP TO CONTINUE", size=13, alpha=220)

    _save(surf, "candidate_2_grid.png")


# ── Candidate 3: Hero carousel (single power-up, paginated) ─────────────────
def candidate_3():
    surf = pygame.Surface((W, H))
    _gradient_bg(surf)
    _draw_overlay_stars(surf, _seeded_stars(seed=7, n=50), t=2.1)
    _draw_mountain_silhouette(surf, alpha=170)

    # Showcase MAGNET as the first page
    page_idx = 1   # 0=triple, 1=magnet, 2=slowmo …
    kind, name, blurb = POWERUPS[page_idx]

    # Top-of-screen header: "POWER-UPS — 2/7"
    _outlined_text(surf, "POWER-UPS", (W // 2, 56),
                   size=36, px=2, shadow_offset=(2, 3))
    counter = _font(12, False).render(f"{page_idx + 1} / {len(POWERUPS)}",
                                      True, _GOLD_MUTED)
    counter.set_alpha(200)
    surf.blit(counter, counter.get_rect(center=(W // 2, 90)))

    # Hero panel
    panel = pygame.Rect(28, 122, W - 56, 348)
    _dark_panel(surf, panel, radius=20, alpha=220)

    # Big icon on a soft pulse-glow disc — additive, so it stays subtle
    cx, cy = panel.centerx, panel.y + 116
    glow_r = 78
    glow = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
    for i in range(glow_r, 0, -3):
        alpha = max(0, int(18 * (1 - i / glow_r)))
        pygame.draw.circle(glow, (255, 170, 70, alpha),
                           (glow_r, glow_r), i)
    surf.blit(glow, glow.get_rect(center=(cx, cy)),
              special_flags=pygame.BLEND_ADD)
    # Inner darker plate so the icon contrasts against the panel
    plate_r = 58
    plate = pygame.Surface((plate_r * 2, plate_r * 2), pygame.SRCALPHA)
    pygame.draw.circle(plate, (10, 6, 36, 220), (plate_r, plate_r), plate_r)
    pygame.draw.circle(plate, (*_ORANGE_BORDER, 150),
                       (plate_r, plate_r), plate_r, width=2)
    surf.blit(plate, plate.get_rect(center=(cx, cy)))
    _draw_powerup_icon(surf, kind, cx, cy, 96)

    # Name (bigger, outlined like the title)
    _outlined_text(surf, name, (panel.centerx, panel.y + 226),
                   size=34, px=2, shadow_offset=(2, 3))
    # Divider
    pygame.draw.line(surf, (*_ORANGE_BORDER, 130),
                     (panel.x + 36, panel.y + 252),
                     (panel.right - 36, panel.y + 252), 1)
    # Blurb in cream
    _cream_text_wrapped(surf, blurb,
                        panel.centerx, panel.y + 268,
                        panel.width - 50, size=14, line_h_extra=4)
    # Duration / tag chip
    chip = pygame.Rect(panel.centerx - 50, panel.bottom - 50, 100, 26)
    rounded_rect(surf, chip, 13, (40, 18, 80), 220)
    pygame.draw.rect(surf, (*_ORANGE_BORDER, 180), chip,
                     border_radius=13, width=1)
    dur = _font(11, True).render("LASTS  8s", True, _GOLD_BRIGHT)
    surf.blit(dur, dur.get_rect(center=chip.center))

    # Pagination dots
    dot_y = H - 78
    spacing = 16
    total = len(POWERUPS)
    base_x = W // 2 - (spacing * (total - 1)) // 2
    for i in range(total):
        x = base_x + i * spacing
        if i == page_idx:
            pygame.draw.circle(surf, _GOLD_BRIGHT, (x, dot_y), 4)
            pygame.draw.circle(surf, WHITE, (x, dot_y), 2)
        else:
            pygame.draw.circle(surf, (90, 70, 130), (x, dot_y), 3)

    # Left/right hint arrows
    af = _font(20, True)
    la = af.render("‹", True, _GOLD_MUTED)
    ra = af.render("›", True, _GOLD_MUTED)
    la.set_alpha(180); ra.set_alpha(180)
    surf.blit(la, la.get_rect(center=(36, H // 2 + 40)))
    surf.blit(ra, ra.get_rect(center=(W - 36, H // 2 + 40)))

    _pill_btn(surf, (W // 2, H - 36), "BACK", size=14, alpha=220)

    _save(surf, "candidate_3_hero_carousel.png")


# ── Candidate 4: Zigzag ribbon (alternating left/right) ─────────────────────
def candidate_4():
    surf = pygame.Surface((W, H))
    _gradient_bg(surf)
    _draw_overlay_stars(surf, _seeded_stars(seed=33, n=55), t=0.4)

    _outlined_text(surf, "POWER-UPS", (W // 2, 46),
                   size=34, px=2, shadow_offset=(2, 3))
    sub = _font(10, False).render("ICON   →   EFFECT",
                                  True, _GOLD_MUTED)
    sub.set_alpha(180)
    surf.blit(sub, sub.get_rect(center=(W // 2, 76)))

    row_h = 70
    base_y = 96
    icon_size = 50

    for i, (kind, name, blurb) in enumerate(POWERUPS):
        flip = (i % 2 == 1)
        ry = base_y + i * row_h

        # Icon position
        if flip:
            ix = W - 50
            tx_left = 14
            tx_right = ix - 36
        else:
            ix = 50
            tx_left = ix + 36
            tx_right = W - 14

        # Connector dotted line from the icon to the next icon
        if i < len(POWERUPS) - 1:
            next_flip = ((i + 1) % 2 == 1)
            nix = W - 50 if next_flip else 50
            x0, x1 = sorted([ix, nix])
            y_mid = ry + row_h - 10
            for px in range(x0 + 4, x1 - 4, 8):
                pygame.draw.circle(surf, (*_ORANGE_BORDER, 80),
                                   (px, y_mid), 1)

        # Icon halo plate
        halo_r = icon_size // 2 + 6
        halo = pygame.Surface((halo_r * 2, halo_r * 2), pygame.SRCALPHA)
        pygame.draw.circle(halo, (40, 22, 90, 230), (halo_r, halo_r), halo_r)
        pygame.draw.circle(halo, (*_ORANGE_BORDER, 140),
                           (halo_r, halo_r), halo_r, width=2)
        surf.blit(halo, halo.get_rect(center=(ix, ry + icon_size // 2)))
        _draw_powerup_icon(surf, kind, ix, ry + icon_size // 2, icon_size)

        # Text block on the opposite side
        text_w = tx_right - tx_left
        # Name
        nf = _font(15, True)
        name_img = nf.render(name, True, _GOLD_BRIGHT)
        if flip:
            nx = tx_right - name_img.get_width()
        else:
            nx = tx_left
        surf.blit(name_img, (nx, ry + 4))
        # Blurb wrap (1-2 lines)
        f = _font(11, False)
        words = blurb.split()
        cur = ""
        lines = []
        for w in words:
            test = (cur + " " + w).strip()
            if f.size(test)[0] <= text_w:
                cur = test
            else:
                if cur: lines.append(cur)
                cur = w
        if cur: lines.append(cur)
        for li, line in enumerate(lines[:2]):
            line_img = f.render(line, True, UI_CREAM)
            if flip:
                lx = tx_right - line_img.get_width()
            else:
                lx = tx_left
            surf.blit(line_img, (lx, ry + 24 + li * 13))

    _save(surf, "candidate_4_zigzag.png")


# ── Candidate 5: Codex (compact two-column with ornate header) ──────────────
def candidate_5():
    surf = pygame.Surface((W, H))
    _gradient_bg(surf)
    _draw_overlay_stars(surf, _seeded_stars(seed=55, n=70), t=2.7)

    # Ornate gold horizontal divider above + below the title
    def gold_rule(y):
        pygame.draw.line(surf, (*_GOLD_BRIGHT, 200),
                         (40, y), (W - 40, y), 1)
        pygame.draw.line(surf, (*_ORANGE_BORDER, 160),
                         (40, y + 1), (W - 40, y + 1), 1)
        # Center diamond ornament
        pts = [(W // 2, y - 4), (W // 2 + 4, y),
               (W // 2, y + 4), (W // 2 - 4, y)]
        pygame.draw.polygon(surf, _GOLD_BRIGHT, pts)
        pygame.draw.polygon(surf, _RED_OUTLINE, pts, 1)

    gold_rule(38)
    _outlined_text(surf, "POWER-UPS", (W // 2, 70),
                   size=32, px=2, shadow_offset=(2, 3))
    cap = _font(10, False).render("— A FIELD GUIDE —", True, _GOLD_MUTED)
    cap.set_alpha(200)
    surf.blit(cap, cap.get_rect(center=(W // 2, 96)))
    gold_rule(112)

    # Two-column compact list
    col_top = 130
    col_w   = (W - 36) // 2
    cell_h  = 70
    gap_x   = 12

    for i, (kind, name, blurb) in enumerate(POWERUPS):
        col = i % 2
        row = i // 2
        x = 12 + col * (col_w + gap_x)
        y = col_top + row * (cell_h + 8)
        cell = pygame.Rect(x, y, col_w, cell_h)
        _dark_panel(surf, cell, radius=10, alpha=210)

        # Icon left
        icon_size = 44
        _draw_powerup_icon(surf, kind,
                           cell.x + 28, cell.centery, icon_size)
        # Vertical separator
        pygame.draw.line(surf, (*_ORANGE_BORDER, 80),
                         (cell.x + 56, cell.y + 8),
                         (cell.x + 56, cell.bottom - 8), 1)
        # Name
        nf = _font(12, True)
        nimg = nf.render(name, True, _GOLD_BRIGHT)
        surf.blit(nimg, (cell.x + 64, cell.y + 8))
        # Blurb (wrapped, 2 lines max)
        f = _font(9, False)
        words = blurb.split()
        cur = ""
        lines = []
        text_w = cell.right - (cell.x + 64) - 6
        for w in words:
            test = (cur + " " + w).strip()
            if f.size(test)[0] <= text_w:
                cur = test
            else:
                if cur: lines.append(cur)
                cur = w
        if cur: lines.append(cur)
        for li, line in enumerate(lines[:3]):
            img = f.render(line, True, UI_CREAM)
            surf.blit(img, (cell.x + 64, cell.y + 24 + li * 11))

    # Bottom rule + footer caption
    gold_rule(H - 60)
    foot = _font(10, False).render("8 SECONDS · 14% SPAWN CHANCE",
                                   True, _GOLD_MUTED)
    foot.set_alpha(210)
    surf.blit(foot, foot.get_rect(center=(W // 2, H - 36)))

    _save(surf, "candidate_5_codex.png")


def main():
    candidate_1()
    candidate_2()
    candidate_3()
    candidate_4()
    candidate_5()
    print(f"\nDone. Output dir: {OUT_DIR}")


if __name__ == "__main__":
    main()
