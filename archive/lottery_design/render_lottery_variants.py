"""Render 5 visual variants of the LOTTERY power-up reveal animation.

Each variant is shown as a triptych of keyframes (early spin / mid /
reveal) composited over an authentic dusk-biome gameplay backdrop with
the bird mid-flap. The reveal frame shows the JACKPOT tier — the most
visually loaded outcome — so we can compare each variant at its peak.

Variants (see commit message and chat for rationale):
  v1_slot_machine   Vegas-style 3-reel cabinet with marquee bulbs
  v2_wheel          Wheel of Fortune with 6 tier-coloured slices
  v3_scratch_card   Scratch-off card whose foil peels diagonally
  v4_tumbler        Glass bingo dome — balls bounce, one shoots a chute
  v5_tarot          Three face-down ornate cards, middle flips reveal

Output:
  ./screenshots/v{N}_<slug>.png        triptych — frame_a | frame_b | frame_c
  ./screenshots/_contact_sheet.png     5-row strip: name + triptych
  ./screenshots/_reveal_compare.png    1-row strip of just the 5 reveal frames

Run from anywhere:
    python archive/lottery_design/render_lottery_variants.py
"""
from __future__ import annotations

import math
import os
import pathlib
import random
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

_HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(_HERE.parent.parent))

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game.config import W, H, GROUND_Y
from game import biome as _biome
from game.draw import (
    get_sky_surface_biome,
    draw_cloud,
    draw_mountains,
    draw_ground,
)
from game.entities import Bird, Pipe


# ── shared palette (gold / red / cream, consistent with HUD) ─────────────────
GOLD_BRIGHT  = (240, 192,  64)
GOLD_DEEP    = (180, 130,  30)
GOLD_PALE    = (255, 230, 140)
RED_OUTLINE  = (168,  32,  16)
RED_DEEP     = (110,  18,  10)
ORANGE       = (232, 104,  40)
PANEL_DARK   = ( 12,   8,  38)
PANEL_MID    = ( 32,  18,  68)
CREAM        = (255, 245, 215)
NEAR_BLACK   = (  8,   6,  18)
WHITE        = (255, 255, 255)

# Tier colour palette (used by wheel + tarot for the slice/border colour).
TIER_COLORS = {
    "JACKPOT": GOLD_BRIGHT,
    "BIG WIN": (255, 170,  40),
    "WIN":     (140, 200,  90),
    "NOTHING": (170, 170, 180),
    "LOSS":    (210, 110,  80),
    "BUST":    (190,  50,  40),
}


# ── backdrop (matches the look in tools/render_pillar_gameplay.py) ───────────
def _draw_backdrop(surf, phase=0.62, scroll=80.0):
    palette = _biome.palette_for_phase(phase)
    bucket = int(phase * _biome.PHASE_BUCKETS) % _biome.PHASE_BUCKETS
    sky = get_sky_surface_biome(W, H, GROUND_Y, palette, bucket)
    sky.set_alpha(None)
    surf.blit(sky, (0, 0))

    for i, (bx, by, sc, var) in enumerate((
            (40, 95, 0.9, 0), (210, 150, 1.0, 2),
            (90, 230, 0.8, 3), (270, 70, 0.7, 1))):
        ox = ((bx - scroll * (0.04 + 0.02 * i)) % (W + 160)) - 80
        draw_cloud(surf, ox, by + math.sin(0.5 + i) * 3, sc, variant=var)

    draw_mountains(surf, scroll, GROUND_Y, W,
                   palette["mtn_far"], palette["mtn_near"])

    # Single pillar mid-frame for context.
    rng = random.Random(0xC0FFEE)
    p = Pipe(220.0, 280.0, 150.0)
    p.seed = rng.randint(0, 0xFFFFFF)
    p.draw(surf)

    draw_ground(
        surf, GROUND_Y, W, H, scroll,
        palette.get("ground_top"), palette.get("ground_mid"),
        palette.get("ground_bot"),
    )


def _draw_bird(surf, y=H * 0.46):
    b = Bird()
    b.y = y
    b.vy = -90  # slight upward tilt, mid-flap
    b.frame_t = 1.4
    b.draw(surf)


# ── small primitive helpers ──────────────────────────────────────────────────
def _font(size: int, bold: bool = True) -> pygame.font.Font:
    try:
        f = pygame.font.SysFont(None, size, bold=bold)
    except Exception:
        f = pygame.font.Font(None, size)
    return f


def _outlined_text(surf, txt, center, size, fill=GOLD_BRIGHT,
                   outline=RED_OUTLINE, px=2):
    f = _font(size, True)
    img = f.render(txt, True, fill)
    out = f.render(txt, True, outline)
    r = img.get_rect(center=center)
    for ox in (-px, 0, px):
        for oy in (-px, 0, px):
            if ox or oy:
                surf.blit(out, (r.x + ox, r.y + oy))
    surf.blit(img, r.topleft)


def _glow_circle(surf, center, radius, color, alpha=120):
    """Soft halo. Drawn as a stack of 4 fading concentric SRCALPHA disks
    so the centre stays visible — no BLEND_ADD wash."""
    g = pygame.Surface((radius * 2 + 4, radius * 2 + 4), pygame.SRCALPHA)
    cx = cy = radius + 2
    for k in range(4):
        rr = radius - k * (radius // 5)
        a = max(0, int(alpha * (1 - k / 4) * 0.45))
        pygame.draw.circle(g, (*color, a), (cx, cy), rr)
    surf.blit(g, (center[0] - cx, center[1] - cy))


def _outer_glow(surf, center, radius, color, alpha=110):
    """Ring-shaped halo around an object so its centre stays untouched.
    Used for reveal-frame celebration without washing out the artwork."""
    g = pygame.Surface((radius * 2 + 4, radius * 2 + 4), pygame.SRCALPHA)
    cx = cy = radius + 2
    for k in range(5):
        rr = radius + k * 3
        a = max(0, int(alpha * (1 - k / 5) * 0.55))
        pygame.draw.circle(g, (*color, a), (cx, cy), rr, 3)
    surf.blit(g, (center[0] - cx, center[1] - cy))


def _confetti(surf, cx, cy, t, seed=42):
    """Small radial spray of gold/cream/red flakes — used on the JACKPOT
    reveal frame across all variants for consistent celebration energy."""
    rng = random.Random(seed)
    n = 60
    for _ in range(n):
        ang = rng.uniform(0, math.tau)
        speed = rng.uniform(40, 220)
        col = rng.choice((GOLD_BRIGHT, GOLD_PALE, CREAM, ORANGE, RED_OUTLINE))
        d = speed * t
        x = cx + math.cos(ang) * d
        y = cy + math.sin(ang) * d - 60 * t * t
        sz = rng.choice((2, 2, 3, 4))
        rot = rng.uniform(0, math.tau)
        if rng.random() < 0.5:
            pygame.draw.circle(surf, col, (int(x), int(y)), sz // 2 + 1)
        else:
            flake = pygame.Surface((sz * 2, sz * 2), pygame.SRCALPHA)
            pygame.draw.rect(flake, col, (0, 0, sz * 2, sz))
            r = pygame.transform.rotate(flake, math.degrees(rot))
            surf.blit(r, r.get_rect(center=(int(x), int(y))))


# ─────────────────────────────────────────────────────────────────────────────
# V1 — Vegas slot machine
# ─────────────────────────────────────────────────────────────────────────────
def _v1_slot_machine(surf, t, *, cx=180, cy=H * 0.36):
    """Tall cabinet with marquee bulbs + 3 reels. t in [0,1] over the
    full anim. The reveal triptych chooses three sample t values."""
    cabinet_w, cabinet_h = 160, 130
    rect = pygame.Rect(0, 0, cabinet_w, cabinet_h)
    rect.center = (cx, cy)

    # Drop shadow.
    sh = pygame.Surface((cabinet_w + 8, cabinet_h + 8), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 130),
                     (0, 0, cabinet_w + 8, cabinet_h + 8), border_radius=10)
    surf.blit(sh, (rect.x - 4, rect.y + 6))

    # Cabinet body.
    pygame.draw.rect(surf, RED_OUTLINE, rect, border_radius=10)
    pygame.draw.rect(surf, GOLD_DEEP,
                     rect.inflate(-6, -6), border_radius=8)
    pygame.draw.rect(surf, PANEL_DARK,
                     rect.inflate(-14, -14), border_radius=6)

    # Marquee strip (top 22 px).
    marquee = pygame.Rect(rect.x + 7, rect.y + 7, cabinet_w - 14, 22)
    pygame.draw.rect(surf, RED_DEEP, marquee, border_radius=4)
    pygame.draw.rect(surf, GOLD_BRIGHT, marquee, width=1, border_radius=4)
    # Marquee bulbs — alternating bright/dim based on t to suggest chase.
    for i in range(9):
        bx = marquee.x + 8 + i * (marquee.width - 16) // 8
        by = marquee.y + marquee.height // 2
        phase = (t * 8 + i) % 2 < 1
        col = GOLD_PALE if phase else GOLD_DEEP
        pygame.draw.circle(surf, col, (bx, by + 5), 2)
    _outlined_text(surf, "LOTTERY", marquee.center, 18,
                   fill=GOLD_BRIGHT, outline=NEAR_BLACK, px=1)

    # Reel window (3 reels, each 38×56).
    reel_y = rect.y + 36
    reel_h = 56
    reels_x0 = rect.x + 14
    GLYPHS = ("?", "$", "*", "7", "B", "?", "$", "*")
    finals = ("7", "7", "7")  # JACKPOT reveal triple-7

    for i in range(3):
        rx = reels_x0 + i * 44
        reel = pygame.Rect(rx, reel_y, 38, reel_h)
        pygame.draw.rect(surf, CREAM, reel, border_radius=3)
        pygame.draw.rect(surf, GOLD_DEEP, reel, width=2, border_radius=3)

        # Each reel stops at staggered times: reel0 stops at t=0.45,
        # reel1 at t=0.65, reel2 at t=0.85. Before stop, the reel is
        # blurred; after stop, the final glyph is shown.
        stop_t = 0.45 + i * 0.20
        if t < stop_t:
            # Spinning: render 3 glyphs in a vertical strip with
            # motion blur.
            speed = 12 + i * 3
            offset = (t * speed * 26) % 26
            for k in (-1, 0, 1, 2):
                gx = (int(t * speed) + k + i) % len(GLYPHS)
                ch = GLYPHS[gx]
                gy = reel.y + 6 + k * 26 - int(offset)
                if -10 < gy - reel.y < reel.height:
                    img = _font(22, True).render(ch, True, RED_DEEP)
                    surf.blit(img, img.get_rect(center=(reel.centerx, gy + 10)))
            # vertical streak overlay to suggest motion
            streak = pygame.Surface((reel.width - 6, reel.height - 6),
                                    pygame.SRCALPHA)
            for s in range(0, reel.height, 4):
                streak.fill((255, 255, 255, 30),
                            (0, s, reel.width - 6, 1))
            surf.blit(streak, (reel.x + 3, reel.y + 3))
        else:
            ch = finals[i]
            img = _font(28, True).render(ch, True, RED_DEEP)
            surf.blit(img, img.get_rect(center=reel.center))

    # Side lever.
    lever_top = (rect.right - 3, rect.y + 40)
    lever_bot = (rect.right + 4, rect.y + 64)
    pygame.draw.line(surf, GOLD_DEEP, lever_top, lever_bot, 4)
    pygame.draw.circle(surf, RED_OUTLINE, lever_top, 4)

    # Pay-line gold underline across reels.
    pl_y = reel_y + reel_h // 2
    pygame.draw.line(surf, GOLD_BRIGHT,
                     (reels_x0, pl_y), (reels_x0 + 3 * 44 - 6, pl_y), 1)

    # Result banner (only after all reels stop).
    if t >= 0.90:
        banner = pygame.Rect(rect.x + 10, rect.bottom - 22,
                             cabinet_w - 20, 14)
        pygame.draw.rect(surf, GOLD_BRIGHT, banner, border_radius=3)
        pygame.draw.rect(surf, RED_DEEP, banner, width=1, border_radius=3)
        _outlined_text(surf, "JACKPOT +100", banner.center, 14,
                       fill=RED_DEEP, outline=GOLD_PALE, px=1)
        _confetti(surf, cx, cy - 10, (t - 0.90) * 4)


# ─────────────────────────────────────────────────────────────────────────────
# V2 — Wheel of Fortune
# ─────────────────────────────────────────────────────────────────────────────
def _v2_wheel(surf, t, *, cx=180, cy=H * 0.4):
    radius = 70
    TIERS_ORDER = ("JACKPOT", "WIN", "LOSS", "BIG WIN", "NOTHING", "BUST")

    # Rotation eases out so reveal lands JACKPOT under the pointer.
    # Target final angle: JACKPOT slice centered at top (-90 deg).
    spins = 3.5
    ease = 1 - (1 - t) ** 3
    target_deg = -90 - (360 / 6) * 0.5  # JACKPOT slice index 0, want its centre at -90
    rot = ease * (spins * 360 + (target_deg - (-90)))

    # Pre-render wheel onto its own surface to enable rotation.
    wheel = pygame.Surface((radius * 2 + 12, radius * 2 + 12), pygame.SRCALPHA)
    wcx = wcy = radius + 6
    n = len(TIERS_ORDER)
    for i, name in enumerate(TIERS_ORDER):
        col = TIER_COLORS[name]
        start = (-90 + i * 360 / n) * math.pi / 180
        end = (-90 + (i + 1) * 360 / n) * math.pi / 180
        pts = [(wcx, wcy)]
        steps = 18
        for s in range(steps + 1):
            ang = start + (end - start) * s / steps
            pts.append((wcx + math.cos(ang) * radius,
                        wcy + math.sin(ang) * radius))
        pygame.draw.polygon(wheel, col, pts)
        pygame.draw.polygon(wheel, NEAR_BLACK, pts, 1)
        # Slice label.
        mid_ang = (start + end) / 2
        label_r = radius - 22
        lx = wcx + math.cos(mid_ang) * label_r
        ly = wcy + math.sin(mid_ang) * label_r
        f = _font(11, True)
        txt = f.render(name[:3] if name != "NOTHING" else "NIL",
                       True, NEAR_BLACK)
        rotated = pygame.transform.rotate(txt, -math.degrees(mid_ang) - 90)
        wheel.blit(rotated, rotated.get_rect(center=(lx, ly)))

    # Outer rim + bulbs.
    pygame.draw.circle(wheel, GOLD_DEEP, (wcx, wcy), radius + 3, 4)
    pygame.draw.circle(wheel, GOLD_BRIGHT, (wcx, wcy), radius + 5, 1)
    for i in range(16):
        ang = i * math.tau / 16
        bx = wcx + math.cos(ang) * (radius + 4)
        by = wcy + math.sin(ang) * (radius + 4)
        on = (int(t * 12) + i) % 2 == 0
        pygame.draw.circle(wheel,
                           GOLD_PALE if on else GOLD_DEEP,
                           (int(bx), int(by)), 2)

    rotated = pygame.transform.rotate(wheel, -rot)
    rr = rotated.get_rect(center=(cx, cy))
    surf.blit(rotated, rr.topleft)

    # Hub.
    pygame.draw.circle(surf, RED_DEEP, (cx, cy), 8)
    pygame.draw.circle(surf, GOLD_BRIGHT, (cx, cy), 4)

    # Pointer at top.
    pointer = [
        (cx,     cy - radius - 12),
        (cx - 7, cy - radius - 2),
        (cx + 7, cy - radius - 2),
    ]
    pygame.draw.polygon(surf, RED_OUTLINE, pointer)
    pygame.draw.polygon(surf, GOLD_BRIGHT, pointer, 1)

    # Reveal: ring halo around the rim + banner below. (Ring, not disc,
    # so the wheel face stays readable.)
    if t >= 0.92:
        _outer_glow(surf, (cx, cy), radius + 10, GOLD_PALE, alpha=160)
        banner = pygame.Rect(0, 0, 180, 24)
        banner.center = (cx, cy + radius + 28)
        pygame.draw.rect(surf, RED_DEEP, banner, border_radius=4)
        pygame.draw.rect(surf, GOLD_BRIGHT, banner, width=1, border_radius=4)
        _outlined_text(surf, "JACKPOT +100", banner.center, 18,
                       fill=GOLD_BRIGHT, outline=RED_DEEP, px=1)
        _confetti(surf, cx, cy - 10, (t - 0.92) * 5)


# ─────────────────────────────────────────────────────────────────────────────
# V3 — Scratch card peel
# ─────────────────────────────────────────────────────────────────────────────
def _v3_scratch_card(surf, t, *, cx=180, cy=H * 0.4):
    card_w, card_h = 170, 110
    rect = pygame.Rect(0, 0, card_w, card_h)
    rect.center = (cx, cy)

    # Card shadow.
    sh = pygame.Surface((card_w + 10, card_h + 10), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 140),
                     (0, 0, card_w + 10, card_h + 10), border_radius=10)
    surf.blit(sh, (rect.x - 5, rect.y + 6))

    # Card backing (the "prize" layer underneath the foil).
    pygame.draw.rect(surf, RED_OUTLINE, rect, border_radius=10)
    pygame.draw.rect(surf, GOLD_DEEP, rect.inflate(-6, -6), border_radius=8)
    pygame.draw.rect(surf, CREAM, rect.inflate(-14, -14), border_radius=6)

    # The prize text under the foil.
    inner = rect.inflate(-22, -22)
    _outlined_text(surf, "JACKPOT", (inner.centerx, inner.centery - 16),
                   28, fill=RED_DEEP, outline=GOLD_BRIGHT, px=2)
    _outlined_text(surf, "+100", (inner.centerx, inner.centery + 14),
                   30, fill=GOLD_DEEP, outline=RED_DEEP, px=2)
    # Small star sparkles in corners.
    for sx, sy in ((inner.x + 8, inner.y + 8),
                   (inner.right - 8, inner.y + 8),
                   (inner.x + 8, inner.bottom - 8),
                   (inner.right - 8, inner.bottom - 8)):
        pygame.draw.line(surf, GOLD_BRIGHT, (sx - 4, sy), (sx + 4, sy), 1)
        pygame.draw.line(surf, GOLD_BRIGHT, (sx, sy - 4), (sx, sy + 4), 1)

    # Foil overlay — diagonal swipe peels it off based on t.
    # Coverage: 1.0 at t=0, 0.0 at t=1.
    coverage = max(0.0, 1.0 - t)
    if coverage > 0.01:
        foil = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        # Brushed silver gradient.
        for y in range(card_h):
            shade = 150 + int(40 * math.sin(y * 0.3))
            foil.fill((shade, shade, shade + 8, 255), (0, y, card_w, 1))
        # Three big "?" hint glyphs.
        f = _font(40, True)
        for i, qx in enumerate((card_w * 0.25, card_w * 0.5, card_w * 0.75)):
            qimg = f.render("?", True, (90, 90, 110))
            foil.blit(qimg, qimg.get_rect(center=(qx, card_h * 0.5)))
        # Diagonal mask: keep pixels where x*0.6 + y*0.4 > threshold.
        # threshold runs from 0 (full foil) to card_w*0.6 + card_h*0.4 (gone).
        diag_max = card_w * 0.6 + card_h * 0.4
        threshold = (1 - coverage) * diag_max
        mask = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        for y in range(card_h):
            for x in range(0, card_w, 2):
                v = x * 0.6 + y * 0.4
                # soft edge ~10px wide
                if v < threshold - 6:
                    a = 0
                elif v > threshold + 6:
                    a = 255
                else:
                    a = int(255 * (v - (threshold - 6)) / 12)
                mask.fill((255, 255, 255, a), (x, y, 2, 1))
        foil.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        surf.blit(foil, rect.topleft)

        # Scrape line + metal-shaving particles along the peel edge.
        # Edge runs perpendicular to the diagonal at threshold.
        if 0.05 < t < 0.98:
            # Pick a representative x along the edge and draw a glint line.
            edge_t = threshold / diag_max
            edge_x = rect.x + int(edge_t * card_w * 0.7) + 8
            edge_y_top = rect.y + 6
            edge_y_bot = rect.bottom - 6
            pygame.draw.line(surf, GOLD_PALE,
                             (edge_x, edge_y_top),
                             (edge_x - 18, edge_y_bot), 2)
            pygame.draw.line(surf, WHITE,
                             (edge_x + 1, edge_y_top),
                             (edge_x - 17, edge_y_bot), 1)
            rng = random.Random(int(t * 100))
            for _ in range(14):
                pa = rng.uniform(-0.4, 0.4)
                px = edge_x + int(math.cos(pa) * rng.uniform(4, 22))
                py = rect.centery + int(math.sin(pa) * rng.uniform(-30, 30))
                pygame.draw.circle(surf,
                                   rng.choice((CREAM, GOLD_PALE, (200, 200, 210))),
                                   (px, py), rng.choice((1, 1, 2)))

    # Outer card border re-stroked on top for clean edge.
    pygame.draw.rect(surf, GOLD_BRIGHT, rect, width=2, border_radius=10)

    if t >= 0.95:
        _outer_glow(surf, rect.center, max(card_w, card_h) // 2 + 4,
                    GOLD_PALE, alpha=180)
        _confetti(surf, cx, cy, (t - 0.95) * 8)


# ─────────────────────────────────────────────────────────────────────────────
# V4 — Bingo tumbler
# ─────────────────────────────────────────────────────────────────────────────
def _v4_tumbler(surf, t, *, cx=180, cy=H * 0.4):
    radius = 60
    # Glass dome — radial gradient via concentric circles.
    for r, a in ((radius + 4, 60), (radius, 220), (radius - 6, 40)):
        layer = pygame.Surface((radius * 2 + 10, radius * 2 + 10),
                               pygame.SRCALPHA)
        col = (180, 200, 220, a) if r == radius else (40, 30, 80, a)
        pygame.draw.circle(layer, col, (radius + 5, radius + 5), r)
        surf.blit(layer, (cx - radius - 5, cy - radius - 5))

    # Dome frame ring.
    pygame.draw.circle(surf, GOLD_DEEP, (cx, cy), radius + 3, 3)
    pygame.draw.circle(surf, GOLD_BRIGHT, (cx, cy), radius + 5, 1)

    # Base — wooden plinth.
    base = pygame.Rect(cx - radius - 4, cy + radius - 6,
                       (radius + 4) * 2, 14)
    pygame.draw.rect(surf, RED_DEEP, base, border_radius=4)
    pygame.draw.rect(surf, GOLD_BRIGHT, base, width=1, border_radius=4)

    # Chute on the right — vertical tube the winner ball rises through.
    chute = pygame.Rect(cx + radius - 2, cy - radius - 24, 12, radius + 18)
    pygame.draw.rect(surf, (60, 50, 100, 220), chute, border_radius=4)
    pygame.draw.rect(surf, GOLD_BRIGHT, chute, width=1, border_radius=4)

    # Bouncing balls inside the dome. 6 colored balls, one per tier.
    TIERS_ORDER = ("JACKPOT", "BIG WIN", "WIN", "NOTHING", "LOSS", "BUST")
    rng = random.Random(7)
    if t < 0.70:
        # Chaotic bounce phase.
        for i, name in enumerate(TIERS_ORDER):
            phase = i * 1.3
            # Constrained motion inside the dome radius (~radius - 12).
            R = radius - 14
            ang = phase + t * (4 + i * 0.7) * math.tau
            rad = R * (0.4 + 0.6 * abs(math.sin(phase + t * 5 + i)))
            bx = cx + math.cos(ang) * rad
            by = cy + math.sin(ang) * rad * 0.85
            col = TIER_COLORS[name]
            pygame.draw.circle(surf, NEAR_BLACK, (int(bx), int(by)), 8)
            pygame.draw.circle(surf, col, (int(bx), int(by)), 7)
            pygame.draw.circle(surf, WHITE, (int(bx - 2), int(by - 2)), 2)
            label = "J" if name == "JACKPOT" else name[0]
            txt = _font(11, True).render(label, True, NEAR_BLACK)
            surf.blit(txt, txt.get_rect(center=(int(bx), int(by) + 1)))
    else:
        # Winner ball rising in the chute, others still settling at the bottom.
        for i, name in enumerate(TIERS_ORDER):
            if name == "JACKPOT":
                continue
            settle_x = cx - radius + 18 + i * 14
            settle_y = cy + radius - 16
            col = TIER_COLORS[name]
            pygame.draw.circle(surf, NEAR_BLACK,
                               (settle_x, settle_y), 7)
            pygame.draw.circle(surf, col, (settle_x, settle_y), 6)
        # JACKPOT ball rising through chute.
        rise_t = (t - 0.70) / 0.30  # 0..1
        rise_t = max(0.0, min(1.0, rise_t))
        bx = chute.centerx
        by = chute.bottom - 6 - int(rise_t * (chute.height - 10))
        _glow_circle(surf, (bx, by), 14, GOLD_PALE, alpha=140)
        pygame.draw.circle(surf, NEAR_BLACK, (bx, by), 8)
        pygame.draw.circle(surf, GOLD_BRIGHT, (bx, by), 7)
        pygame.draw.circle(surf, WHITE, (bx - 2, by - 2), 2)
        txt = _font(12, True).render("J", True, NEAR_BLACK)
        surf.blit(txt, txt.get_rect(center=(bx, by + 1)))

    # Result tray below the dome.
    if t >= 0.95:
        _outer_glow(surf, (cx, cy), radius + 8, GOLD_PALE, alpha=160)
        tray = pygame.Rect(0, 0, 160, 22)
        tray.center = (cx, cy + radius + 30)
        pygame.draw.rect(surf, RED_DEEP, tray, border_radius=4)
        pygame.draw.rect(surf, GOLD_BRIGHT, tray, width=1, border_radius=4)
        _outlined_text(surf, "JACKPOT +100", tray.center, 18,
                       fill=GOLD_BRIGHT, outline=RED_DEEP, px=1)
        _confetti(surf, cx, cy, (t - 0.95) * 5)


# ─────────────────────────────────────────────────────────────────────────────
# V5 — Tarot card flip
# ─────────────────────────────────────────────────────────────────────────────
def _v5_tarot(surf, t, *, cx=180, cy=H * 0.4):
    card_w, card_h = 70, 110
    spacing = 10

    def _card_back(target, w, h, scale_x=1.0, hover=0.0):
        """Render a face-down tarot card to a fresh surface at the given
        horizontal scale (for flip perspective). hover adds a soft bob."""
        if scale_x <= 0.02:
            return None
        cw = max(2, int(w * scale_x))
        s = pygame.Surface((cw, h), pygame.SRCALPHA)
        pygame.draw.rect(s, RED_OUTLINE, (0, 0, cw, h), border_radius=4)
        pygame.draw.rect(s, GOLD_DEEP, (2, 2, cw - 4, h - 4), border_radius=3)
        pygame.draw.rect(s, RED_DEEP, (4, 4, cw - 8, h - 8), border_radius=3)
        # Filigree star centered.
        sx = cw // 2
        sy = h // 2
        pygame.draw.line(s, GOLD_BRIGHT, (sx - 8, sy), (sx + 8, sy), 1)
        pygame.draw.line(s, GOLD_BRIGHT, (sx, sy - 16), (sx, sy + 16), 1)
        pygame.draw.line(s, GOLD_BRIGHT, (sx - 6, sy - 12), (sx + 6, sy + 12), 1)
        pygame.draw.line(s, GOLD_BRIGHT, (sx + 6, sy - 12), (sx - 6, sy + 12), 1)
        pygame.draw.circle(s, GOLD_BRIGHT, (sx, sy), 4, 1)
        # Top + bottom corner markers.
        for cy_ in (8, h - 9):
            pygame.draw.circle(s, GOLD_PALE, (sx, cy_), 1)
        return s

    def _card_face(w, h, tier, scale_x=1.0):
        if scale_x <= 0.02:
            return None
        cw = max(2, int(w * scale_x))
        s = pygame.Surface((cw, h), pygame.SRCALPHA)
        col = TIER_COLORS[tier]
        pygame.draw.rect(s, NEAR_BLACK, (0, 0, cw, h), border_radius=4)
        pygame.draw.rect(s, col, (2, 2, cw - 4, h - 4), border_radius=3)
        pygame.draw.rect(s, GOLD_BRIGHT, (4, 4, cw - 8, h - 8),
                         width=1, border_radius=3)
        if cw > 18:
            # Big tier glyph in centre.
            glyph_map = {
                "JACKPOT": "$", "BIG WIN": "$", "WIN": "+",
                "NOTHING": "-", "LOSS": "X", "BUST": "X",
            }
            ch = glyph_map.get(tier, "?")
            img = _font(56, True).render(ch, True, NEAR_BLACK)
            # Horizontally squash to match flip perspective. Use
            # smoothscale so the antialiased glyph doesn't blob out.
            target_w = max(2, int(img.get_width() * scale_x))
            if abs(scale_x - 1.0) > 0.02:
                img = pygame.transform.smoothscale(
                    img, (target_w, img.get_height()))
            s.blit(img, img.get_rect(center=(cw // 2, h // 2 - 4)))
            # Tier label at bottom.
            lbl = _font(13, True).render(tier, True, NEAR_BLACK)
            target_w = max(2, int(lbl.get_width() * scale_x))
            if abs(scale_x - 1.0) > 0.02:
                lbl = pygame.transform.smoothscale(
                    lbl, (target_w, lbl.get_height()))
            s.blit(lbl, lbl.get_rect(center=(cw // 2, h - 12)))
        return s

    # Side cards stay face-down. Centre card flips: scale_x goes
    # 1 → 0 → 1 as t goes 0.3 → 0.6 → 0.9. The back is shown for
    # t < 0.6, the face for t >= 0.6.
    flip_t = max(0.0, min(1.0, (t - 0.30) / 0.60))
    if flip_t <= 0.5:
        scale_x = 1 - flip_t * 2
        centre_surf = _card_back(None, card_w, card_h, scale_x=scale_x)
        is_face = False
    else:
        scale_x = (flip_t - 0.5) * 2
        centre_surf = _card_face(card_w, card_h, "JACKPOT", scale_x=scale_x)
        is_face = True

    # Position the three cards in a fan.
    positions = (
        (cx - card_w - spacing, cy + 4, -8),
        (cx, cy, 0),
        (cx + card_w + spacing, cy + 4, 8),
    )
    # Side cards
    back = _card_back(None, card_w, card_h)
    for i, (px, py, ang) in enumerate(positions):
        if i == 1:
            continue
        rotated = pygame.transform.rotate(back, ang)
        # Slight bob for the early "dealt" feel.
        bob = math.sin(t * 4 + i) * 1 if t < 0.3 else 0
        surf.blit(rotated, rotated.get_rect(center=(px, py + bob)))

    # Confetti backdrop (drawn first so it doesn't blot the face card).
    if t >= 0.95:
        _confetti(surf, cx, cy - 30, (t - 0.95) * 4)

    # Centre card.
    if centre_surf is not None:
        rect = centre_surf.get_rect(center=(cx, cy))
        if is_face and flip_t > 0.95:
            _outer_glow(surf, (cx, cy), card_w // 2 + 12,
                        TIER_COLORS["JACKPOT"], alpha=200)
        surf.blit(centre_surf, rect.topleft)

    # Tier banner below.
    if t >= 0.95:
        banner = pygame.Rect(0, 0, 180, 24)
        banner.center = (cx, cy + card_h // 2 + 22)
        pygame.draw.rect(surf, RED_DEEP, banner, border_radius=4)
        pygame.draw.rect(surf, GOLD_BRIGHT, banner, width=1, border_radius=4)
        _outlined_text(surf, "JACKPOT +100", banner.center, 18,
                       fill=GOLD_BRIGHT, outline=RED_DEEP, px=1)


# ─────────────────────────────────────────────────────────────────────────────
VARIANTS = (
    ("v1_slot_machine", "Vegas slot machine",      _v1_slot_machine),
    ("v2_wheel",        "Wheel of fortune",        _v2_wheel),
    ("v3_scratch_card", "Scratch-off peel",        _v3_scratch_card),
    ("v4_tumbler",      "Bingo ball tumbler",      _v4_tumbler),
    ("v5_tarot",        "Tarot card flip",         _v5_tarot),
)

# Three keyframes per variant — chosen so each shows a distinct phase
# of its animation arc.
KEYFRAMES = (0.20, 0.65, 1.00)


def _render_frame(draw_fn, t) -> pygame.Surface:
    surf = pygame.Surface((W, H))
    _draw_backdrop(surf)
    _draw_bird(surf)
    draw_fn(surf, t)
    return surf


def _build_triptych(slug, label, draw_fn) -> pygame.Surface:
    pad = 6
    label_h = 22
    triptych = pygame.Surface((W * 3 + pad * 4, H + label_h + pad * 2))
    triptych.fill((18, 14, 28))

    # Top label bar.
    bar = pygame.Surface((triptych.get_width(), label_h), pygame.SRCALPHA)
    bar.fill((0, 0, 0, 160))
    triptych.blit(bar, (0, 0))
    font = _font(16, True)
    triptych.blit(font.render(f"{slug}  —  {label}", True, GOLD_BRIGHT),
                  (8, 4))

    for i, t in enumerate(KEYFRAMES):
        frame = _render_frame(draw_fn, t)
        x = pad + i * (W + pad)
        triptych.blit(frame, (x, label_h + pad))
        # Sub-label for the keyframe.
        kf_lbl = ("early spin", "settling", "reveal")[i]
        triptych.blit(_font(13, True).render(kf_lbl, True, WHITE),
                      (x + 6, label_h + pad + H - 18))

    return triptych


def _build_contact_sheet(triptychs) -> pygame.Surface:
    pad = 10
    # Scale each triptych down to fit nicely in the sheet.
    scale = 0.55
    tw = int(triptychs[0].get_width() * scale)
    th = int(triptychs[0].get_height() * scale)
    sheet_w = tw + pad * 2
    sheet_h = pad + (th + pad) * len(triptychs)
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((10, 8, 22))

    for i, tri in enumerate(triptychs):
        scaled = pygame.transform.smoothscale(tri, (tw, th))
        sheet.blit(scaled, (pad, pad + i * (th + pad)))
    return sheet


def _build_reveal_compare() -> pygame.Surface:
    """One-row sheet of just the reveal frame from each variant — useful
    for picking a direction at a glance."""
    pad = 6
    label_h = 28
    n = len(VARIANTS)
    sheet_w = pad + n * (W + pad)
    sheet_h = label_h + pad * 2 + H
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((10, 8, 22))

    bar = pygame.Surface((sheet_w, label_h), pygame.SRCALPHA)
    bar.fill((0, 0, 0, 200))
    sheet.blit(bar, (0, 0))
    sheet.blit(_font(18, True).render(
        "LOTTERY reveal — variants compared at JACKPOT result",
        True, GOLD_BRIGHT), (10, 5))

    for i, (slug, label, draw_fn) in enumerate(VARIANTS):
        frame = _render_frame(draw_fn, 1.0)
        # Annotate variant slug at top of the frame.
        tag = pygame.Surface((W, 18), pygame.SRCALPHA)
        tag.fill((0, 0, 0, 170))
        tag.blit(_font(13, True).render(f"{slug}", True, GOLD_PALE), (4, 2))
        frame.blit(tag, (0, 0))
        sheet.blit(frame, (pad + i * (W + pad), label_h + pad))

    return sheet


def main() -> None:
    out = _HERE / "screenshots"
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.png"):
        old.unlink()

    triptychs = []
    for slug, label, draw_fn in VARIANTS:
        tri = _build_triptych(slug, label, draw_fn)
        path = out / f"{slug}.png"
        pygame.image.save(tri, path)
        print(f"wrote {path}")
        triptychs.append(tri)

    sheet = _build_contact_sheet(triptychs)
    sheet_path = out / "_contact_sheet.png"
    pygame.image.save(sheet, sheet_path)
    print(f"wrote {sheet_path}")

    reveal = _build_reveal_compare()
    reveal_path = out / "_reveal_compare.png"
    pygame.image.save(reveal, reveal_path)
    print(f"wrote {reveal_path}")


if __name__ == "__main__":
    main()
