"""Slot machine — top-left, compact, pro typography, with the six lottery
tiers as discrete reel outcomes.

The wheel mockups grabbed too much screen real estate; the slot cabinet
collapses to roughly 120 x 80 px in the top-left corner instead.

Proposed tier values + weights (the game's LOTTERY_TIERS in config.py
will need to match once a design is locked in):

  $ $ $   ->  JACKPOT  +100   (5 %)    matching gold dollars
  7 7 7   ->  BIG WIN  +40    (12 %)   matching red sevens
  * * *   ->  WIN      +15    (20 %)   matching gold stars
  mixed   ->  NOTHING    0    (35 %)   most common — modal outcome
  X X *   ->  LOSS     -10    (20 %)   two skulls + filler
  X X X   ->  BUST     -50    (8 %)    three skulls, deep loss

Probability bands:
  wins     37 %   (JACKPOT + BIG WIN + WIN)
  nothing  35 %   (most common — the slot doesn't always pay)
  losses   28 %   (LOSS + BUST)

Expected value per spin: +6.8 coins — slightly positive so the powerup
feels rewarding overall, but a single BUST wipes out ~7 average spins
of progress, which makes the risk real.

Everything (cabinet, reels, marquee, result strip) lives inside the
top-left footprint. The result strip flips from "LOTTERY" during the
spin to the tier name + value at reveal.

Output:
  ./screenshots/slot_pro_triptych.png        spin/settling/reveal arc
  ./screenshots/slot_pro_outcomes.png        6 outcomes at native size
  ./screenshots/slot_pro_outcomes_grid.png   2x3 zoomed comparison
  ./screenshots/slot_pro_zoom.png            4x JACKPOT close-up

Run:
    python archive/lottery_design/render_slot_pro.py
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

from game.config import W, H
from archive.lottery_design.render_lottery_variants import (
    GOLD_BRIGHT, GOLD_DEEP, GOLD_PALE,
    RED_OUTLINE, RED_DEEP, ORANGE,
    PANEL_DARK, CREAM, NEAR_BLACK, WHITE,
    _outer_glow, _confetti,
    _draw_backdrop, _draw_bird,
)


_FONT_PATH = str(pathlib.Path(__file__).parent.parent.parent
                 / "game" / "assets" / "LiberationSans-Bold.ttf")
_pro_fonts: dict[int, pygame.font.Font] = {}


def _pro_font(size: int) -> pygame.font.Font:
    f = _pro_fonts.get(size)
    if f is None:
        f = pygame.font.Font(_FONT_PATH, size)
        _pro_fonts[size] = f
    return f


# Same engraved-numeral recipe as the score plaque (cream face + tinted
# rim + drop shadow). Used for tier labels and reel numerals.
_CREAM_FACE  = (252, 244, 220)
_RIM_GOLD    = (180, 130,  30)
_RIM_RED     = (140,  25,  18)
_RIM_NEUTRAL = (110,  80,  30)


def _engraved(text: str, size: int, *,
              rim: tuple[int, int, int] = _RIM_GOLD,
              face: tuple[int, int, int] = _CREAM_FACE
              ) -> pygame.Surface:
    f = _pro_font(size)
    face_img = f.render(text, True, face)
    rim_img  = f.render(text, True, rim)
    sh_img   = f.render(text, True, NEAR_BLACK)
    pad = 4
    w = face_img.get_width() + pad * 2
    h = face_img.get_height() + pad * 2
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    sh_img.set_alpha(170)
    s.blit(sh_img, (pad + 1, pad + 2))
    for ox in (-1, 0, 1):
        for oy in (-1, 0, 1):
            if ox or oy:
                s.blit(rim_img, (pad + ox, pad + oy))
    s.blit(face_img, (pad, pad))
    return s


# ── reel symbols ─────────────────────────────────────────────────────────────
# Each symbol is a small surface (~22 x 32 px) drawn procedurally so the
# slot machine fits the project's "no PNG sprites" rule. Engraved style
# so they share visual DNA with the rest of the HUD.

def _sym_dollar(size: int) -> pygame.Surface:
    """Gold $ on cream — the JACKPOT symbol."""
    return _engraved("$", size, rim=_RIM_GOLD, face=(240, 200, 80))


def _sym_seven(size: int) -> pygame.Surface:
    """Red 7 on cream — the BIG WIN symbol."""
    return _engraved("7", size, rim=_RIM_RED, face=(220, 60, 50))


def _sym_star(size: int) -> pygame.Surface:
    """Five-point gold star — the WIN symbol. Drawn as a polygon so it
    has actual presence rather than a tiny "*" glyph."""
    pad = 4
    outer = size // 2
    inner = max(2, outer // 2)
    cx = cy = outer + pad
    pts = []
    for k in range(10):
        ang = -math.pi / 2 + k * math.pi / 5
        r = outer if k % 2 == 0 else inner
        pts.append((cx + math.cos(ang) * r,
                    cy + math.sin(ang) * r))
    s = pygame.Surface((outer * 2 + pad * 2, outer * 2 + pad * 2),
                       pygame.SRCALPHA)
    # Drop shadow.
    sh_pts = [(x + 1, y + 2) for (x, y) in pts]
    pygame.draw.polygon(s, (0, 0, 0, 150), sh_pts)
    # Gold body + rim + highlight.
    pygame.draw.polygon(s, (255, 210,  90), pts)
    pygame.draw.polygon(s, _RIM_GOLD, pts, 1)
    # Inner highlight.
    inner_pts = [(cx + (x - cx) * 0.55, cy + (y - cy) * 0.55) for (x, y) in pts]
    pygame.draw.polygon(s, (255, 240, 180), inner_pts[:5], 0)
    return s


def _sym_skull(size: int) -> pygame.Surface:
    """Tiny skull silhouette — the LOSS/BUST symbol. Drawn so it reads
    as a clear warning at small size."""
    sz = size + 6
    s = pygame.Surface((sz, sz), pygame.SRCALPHA)
    cx = cy = sz // 2
    skull_r = size // 2
    # Drop shadow.
    pygame.draw.circle(s, (0, 0, 0, 150), (cx + 1, cy + 1), skull_r + 1)
    # Skull body — cream / bone colour.
    pygame.draw.circle(s, (235, 230, 210), (cx, cy - 1), skull_r)
    pygame.draw.circle(s, (90, 60, 40), (cx, cy - 1), skull_r, 1)
    # Jaw — small trapezoid below.
    jaw_w = skull_r
    jaw = [
        (cx - jaw_w // 2, cy + skull_r - 2),
        (cx + jaw_w // 2, cy + skull_r - 2),
        (cx + jaw_w // 2 - 1, cy + skull_r + 3),
        (cx - jaw_w // 2 + 1, cy + skull_r + 3),
    ]
    pygame.draw.polygon(s, (235, 230, 210), jaw)
    pygame.draw.polygon(s, (90, 60, 40), jaw, 1)
    # Eye sockets — dark hollows.
    eye_r = max(2, skull_r // 3)
    pygame.draw.circle(s, (40, 20, 30), (cx - skull_r // 2 + 1, cy - 1), eye_r)
    pygame.draw.circle(s, (40, 20, 30), (cx + skull_r // 2 - 1, cy - 1), eye_r)
    # Nose triangle.
    nose = [
        (cx, cy + 1),
        (cx - 1, cy + 3),
        (cx + 1, cy + 3),
    ]
    pygame.draw.polygon(s, (40, 20, 30), nose)
    # Teeth marks on the jaw.
    for tx in (cx - 2, cx, cx + 2):
        pygame.draw.line(s, (90, 60, 40),
                         (tx, cy + skull_r - 1),
                         (tx, cy + skull_r + 2), 1)
    return s


# Map tier slug -> (reel_0, reel_1, reel_2) symbol functions.
# Mixed combos for NOTHING are stable but visibly non-matching.
TIER_COMBOS = {
    "JACKPOT": (_sym_dollar, _sym_dollar, _sym_dollar),
    "BIG WIN": (_sym_seven,  _sym_seven,  _sym_seven),
    "WIN":     (_sym_star,   _sym_star,   _sym_star),
    "NOTHING": (_sym_dollar, _sym_seven,  _sym_star),    # all three, no match
    "LOSS":    (_sym_skull,  _sym_skull,  _sym_star),    # two skulls + filler
    "BUST":    (_sym_skull,  _sym_skull,  _sym_skull),   # three skulls
}

TIER_VALUE = {
    "JACKPOT": +100,
    "BIG WIN":  +40,
    "WIN":      +15,
    "NOTHING":    0,
    "LOSS":     -10,
    "BUST":     -50,
}

# Proposed re-tuning — game/config.py LOTTERY_TIERS will need to match
# once a design is locked in. NOTHING becomes the modal outcome (35 %),
# wins stay enticing but rarer, and BUST is the new -50 deep loss.
# Expected value works out to +6.8 coins/spin — slightly positive so
# the powerup feels rewarding overall while still real risk.
TIER_WEIGHT = {
    "JACKPOT":  5,
    "BIG WIN": 12,
    "WIN":     20,
    "NOTHING": 35,
    "LOSS":    20,
    "BUST":     8,
}
assert sum(TIER_WEIGHT.values()) == 100


def _value_str(v: int) -> str:
    if v > 0:
        return f"+{v}"
    if v < 0:
        return str(v)
    return "0"


# ── slot cabinet (compact, top-left anchored) ───────────────────────────────
CAB_X, CAB_Y = 8, 8
CAB_W, CAB_H = 118, 86


def _draw_cabinet(surf, t: float, *,
                  tier: str | None,
                  reel_progress: tuple[float, float, float] | None = None):
    """Render the slot cabinet. tier is None during the spin and set
    at reveal. reel_progress is the spin fraction each reel has
    completed (0..1); reels with progress >= 1.0 show the final symbol."""
    cabinet = pygame.Rect(CAB_X, CAB_Y, CAB_W, CAB_H)

    # Drop shadow.
    sh = pygame.Surface((cabinet.width + 6, cabinet.height + 6),
                        pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 160),
                     (0, 0, cabinet.width + 6, cabinet.height + 6),
                     border_radius=10)
    surf.blit(sh, (cabinet.x - 3, cabinet.y + 4))

    # Cabinet body — red outer / gold middle / dark inner.
    pygame.draw.rect(surf, RED_OUTLINE, cabinet, border_radius=8)
    pygame.draw.rect(surf, GOLD_DEEP, cabinet.inflate(-4, -4),
                     border_radius=6)
    pygame.draw.rect(surf, (16, 10, 36), cabinet.inflate(-10, -10),
                     border_radius=5)

    # Marquee — slim red bar with chase bulbs + "LOTTERY".
    marquee = pygame.Rect(cabinet.x + 6, cabinet.y + 6,
                          cabinet.width - 12, 14)
    pygame.draw.rect(surf, RED_DEEP, marquee, border_radius=3)
    pygame.draw.rect(surf, GOLD_BRIGHT, marquee, width=1, border_radius=3)
    for i in range(7):
        bx = marquee.x + 6 + i * (marquee.width - 12) // 6
        on = (int(t * 8) + i) % 2 == 0
        pygame.draw.circle(surf, GOLD_PALE if on else GOLD_DEEP,
                           (bx, marquee.y + 2), 1)
    lbl = _engraved("LOTTERY", 11, rim=_RIM_GOLD)
    surf.blit(lbl, lbl.get_rect(center=marquee.center))

    # Reel windows. Three 22 x 32 cream cells with gold borders.
    reel_w, reel_h = 22, 32
    reel_y = marquee.bottom + 6
    reels_x0 = cabinet.x + 14
    reel_gap = 6

    # Cycling symbols shown during the spin (a brief rotation of all five
    # so the player gets a glimpse of every possibility).
    SPIN_CYCLE = (_sym_dollar, _sym_seven, _sym_star,
                  _sym_skull, _sym_seven, _sym_dollar)

    for i in range(3):
        rx = reels_x0 + i * (reel_w + reel_gap)
        reel = pygame.Rect(rx, reel_y, reel_w, reel_h)
        pygame.draw.rect(surf, CREAM, reel, border_radius=3)
        pygame.draw.rect(surf, GOLD_DEEP, reel, width=1, border_radius=3)
        # Inner shadow at the top — gives the "drum" feel.
        for k in range(3):
            a = max(0, 60 - k * 20)
            pygame.draw.line(surf, (0, 0, 0, a),
                             (reel.x + 1, reel.y + 1 + k),
                             (reel.right - 1, reel.y + 1 + k))

        prog = 1.0 if reel_progress is None else reel_progress[i]
        if prog >= 1.0 and tier is not None:
            # Locked: show the final symbol for this tier.
            sym_fn = TIER_COMBOS[tier][i]
            sym = sym_fn(18)
            surf.blit(sym, sym.get_rect(center=reel.center))
        else:
            # Spinning: blur a strip of cycling symbols vertically.
            speed = 14 + i * 2
            offset = (t * speed * (reel_h - 6)) % (reel_h - 6)
            for k in (-1, 0, 1, 2):
                idx = (int(t * speed) + k + i) % len(SPIN_CYCLE)
                sym = SPIN_CYCLE[idx](14)
                sy = reel.y + 6 + k * (reel_h - 6) - int(offset)
                if -14 < sy - reel.y < reel.height:
                    # Clip to reel bounds with a per-blit mask.
                    sub_rect = sym.get_rect(center=(reel.centerx,
                                                    sy + sym.get_height() // 2))
                    clip = sub_rect.clip(reel)
                    if clip.width > 0 and clip.height > 0:
                        offset_in_sym = (clip.x - sub_rect.x,
                                         clip.y - sub_rect.y)
                        surf.blit(sym, clip.topleft,
                                  pygame.Rect(offset_in_sym, clip.size))
            # Motion streaks.
            streak = pygame.Surface((reel.width - 4, reel.height - 4),
                                    pygame.SRCALPHA)
            for s_y in range(0, reel.height, 4):
                streak.fill((255, 255, 255, 25),
                            (0, s_y, reel.width - 4, 1))
            surf.blit(streak, (reel.x + 2, reel.y + 2))

    # Pay-line — thin gold horizontal under the reels' midpoint.
    pl_y = reel_y + reel_h // 2
    pygame.draw.line(surf, (*GOLD_BRIGHT, 220),
                     (reels_x0 - 2, pl_y),
                     (reels_x0 + 3 * reel_w + 2 * reel_gap + 2, pl_y), 1)

    # Lever on the right side.
    lev_top = (cabinet.right - 4, cabinet.y + 26)
    lev_bot = (cabinet.right + 3, cabinet.y + 42)
    pygame.draw.line(surf, GOLD_DEEP, lev_top, lev_bot, 3)
    pygame.draw.circle(surf, RED_OUTLINE, lev_top, 3)
    pygame.draw.circle(surf, GOLD_BRIGHT, lev_top, 3, 1)

    # Result strip at the bottom of the cabinet.
    strip = pygame.Rect(cabinet.x + 8, reel_y + reel_h + 4,
                        cabinet.width - 16, 14)
    if tier is None:
        # During spin: show three small "?" hints.
        pygame.draw.rect(surf, (8, 6, 22), strip, border_radius=3)
        pygame.draw.rect(surf, GOLD_DEEP, strip, width=1, border_radius=3)
        for x in (strip.x + 10, strip.centerx, strip.right - 10):
            q = _engraved("?", 11, rim=_RIM_GOLD)
            surf.blit(q, q.get_rect(center=(x, strip.centery)))
    else:
        # Reveal: tier name + value on a cream-on-gold pill, rim tinted
        # by sign so positive prizes glow gold and negatives bleed red.
        value = TIER_VALUE[tier]
        rim = (_RIM_GOLD if value > 0 else
               (_RIM_RED if value < 0 else _RIM_NEUTRAL))
        pygame.draw.rect(surf, _CREAM_FACE, strip,
                         border_radius=strip.height // 2)
        pygame.draw.rect(surf, rim, strip, width=1,
                         border_radius=strip.height // 2)
        # Tier abbreviation + value, fit into the 14 px strip.
        tier_short = {
            "JACKPOT": "JACKPOT", "BIG WIN": "BIG WIN", "WIN": "WIN",
            "NOTHING": "NOTHING", "LOSS": "LOSS", "BUST": "BUST",
        }[tier]
        tname_img = _engraved(tier_short, 10, rim=rim)
        vstr_img  = _engraved(_value_str(value), 11, rim=rim)
        gap = 4
        total_w = tname_img.get_width() + gap + vstr_img.get_width()
        start_x = strip.centerx - total_w // 2
        surf.blit(tname_img, tname_img.get_rect(
            midleft=(start_x, strip.centery)))
        surf.blit(vstr_img, vstr_img.get_rect(
            midleft=(start_x + tname_img.get_width() + gap - 4,
                     strip.centery)))


def _slot_machine(surf, t: float, *, tier: str = "JACKPOT"):
    """Top-level slot machine renderer. Manages reel-stop staggering and
    reveal effects so each draw is a single call."""
    # Reels stop in order: reel 0 at t=0.50, reel 1 at 0.70, reel 2 at 0.90.
    stops = (0.50, 0.70, 0.90)
    prog = tuple(1.0 if t >= s else (t / s) for s in stops)
    # The cabinet only knows the final tier once all reels are locked.
    locked_tier = tier if t >= stops[-1] else None
    _draw_cabinet(surf, t, tier=locked_tier, reel_progress=prog)

    # Reveal effects — gated to JACKPOT/BIG WIN/WIN for the positive
    # outcomes, and a dim red flash for LOSS/BUST.
    if t >= 0.92:
        cab = pygame.Rect(CAB_X, CAB_Y, CAB_W, CAB_H)
        value = TIER_VALUE[tier]
        if value > 0:
            color = GOLD_PALE if value >= 40 else (200, 220, 140)
            _outer_glow(surf, cab.center, max(cab.width, cab.height) // 2,
                        color, alpha=180)
            _confetti(surf, cab.centerx, cab.bottom + 6,
                      (t - 0.92) * 8, seed={
                          "JACKPOT": 11, "BIG WIN": 12, "WIN": 13,
                      }[tier])
        elif value < 0:
            # Soft red wash, no confetti.
            _outer_glow(surf, cab.center, max(cab.width, cab.height) // 2,
                        (210, 80, 60), alpha=140)


# ── render helpers ──────────────────────────────────────────────────────────
def _render_frame(t: float, tier: str = "JACKPOT") -> pygame.Surface:
    surf = pygame.Surface((W, H))
    _draw_backdrop(surf)
    _draw_bird(surf)
    _slot_machine(surf, t, tier=tier)
    return surf


KEYFRAMES = (0.20, 0.65, 1.00)


def _build_triptych(tier: str = "JACKPOT") -> pygame.Surface:
    pad = 6
    label_h = 22
    tri = pygame.Surface((W * 3 + pad * 4, H + label_h + pad * 2))
    tri.fill((18, 14, 28))
    bar = pygame.Surface((tri.get_width(), label_h), pygame.SRCALPHA)
    bar.fill((0, 0, 0, 160))
    tri.blit(bar, (0, 0))
    hdr = _pro_font(14).render(
        f"slot machine v2  -  spin -> settling -> reveal ({tier})",
        True, GOLD_BRIGHT)
    tri.blit(hdr, (8, 4))
    for i, t in enumerate(KEYFRAMES):
        frame = _render_frame(t, tier=tier)
        x = pad + i * (W + pad)
        tri.blit(frame, (x, label_h + pad))
        kf = _pro_font(12).render(
            ("early spin", "settling", "reveal")[i], True, WHITE)
        tri.blit(kf, (x + 6, label_h + pad + H - 18))
    return tri


def _build_outcomes_sheet() -> pygame.Surface:
    """All 6 tier outcomes side by side at the reveal frame."""
    order = ("JACKPOT", "BIG WIN", "WIN", "NOTHING", "LOSS", "BUST")
    pad = 6
    label_h = 28
    n = len(order)
    sheet_w = pad + n * (W + pad)
    sheet_h = label_h + pad * 2 + H
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((10, 8, 22))
    bar = pygame.Surface((sheet_w, label_h), pygame.SRCALPHA)
    bar.fill((0, 0, 0, 200))
    sheet.blit(bar, (0, 0))
    sheet.blit(_pro_font(16).render(
        "LOTTERY slot machine - all six tier outcomes "
        "(half of all spins net zero or negative)",
        True, GOLD_BRIGHT), (10, 5))
    for i, tier in enumerate(order):
        frame = _render_frame(1.0, tier=tier)
        # Tag the top of each frame with the tier name.
        tag = pygame.Surface((W, 18), pygame.SRCALPHA)
        tag.fill((0, 0, 0, 170))
        tag.blit(_pro_font(12).render(
            f"{tier}  {_value_str(TIER_VALUE[tier])}",
            True, GOLD_PALE), (4, 2))
        frame.blit(tag, (0, 0))
        sheet.blit(frame, (pad + i * (W + pad), label_h + pad))
    return sheet


def _expected_value() -> float:
    return sum(TIER_VALUE[t] * TIER_WEIGHT[t] for t in TIER_VALUE) / 100.0


def _build_outcomes_grid() -> pygame.Surface:
    """Compact 2x3 grid of just the slot cabinet at each tier outcome —
    same content as outcomes_sheet but laid out for easy at-a-glance
    comparison without the surrounding gameplay backdrop. Labels and
    weights are driven by TIER_WEIGHT / TIER_VALUE so the grid stays
    in sync if those are tuned."""
    order = ("JACKPOT", "BIG WIN", "WIN", "NOTHING", "LOSS", "BUST")
    crops = []
    for tier in order:
        frame = _render_frame(1.0, tier=tier)
        crops.append(frame.subsurface(pygame.Rect(0, 0, 140, 110)).copy())

    scale_w, scale_h = 350, 275       # 2.5x of the 140x110 crop
    cols, rows = 3, 2
    pad = 12
    header_h = 56
    label_h = 28
    sheet_w = pad + cols * (scale_w + pad)
    sheet_h = header_h + pad + rows * (scale_h + pad + label_h)
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((10, 8, 22))

    # Top title.
    sheet.blit(_pro_font(18).render(
        "Slot machine - 6 tier outcomes at reveal", True, GOLD_BRIGHT),
        (pad, 6))
    # Probability breakdown summary.
    pos = sum(TIER_WEIGHT[t] for t in ("JACKPOT", "BIG WIN", "WIN"))
    neg = sum(TIER_WEIGHT[t] for t in ("LOSS", "BUST"))
    nil = TIER_WEIGHT["NOTHING"]
    ev = _expected_value()
    summary = (f"wins {pos}%   nothing {nil}%   losses {neg}%"
               f"     expected value per spin: {ev:+.1f} coins")
    sheet.blit(_pro_font(13).render(summary, True, GOLD_PALE),
               (pad, 30))

    for i, (tier, crop) in enumerate(zip(order, crops)):
        row, col = divmod(i, cols)
        x = pad + col * (scale_w + pad)
        y = header_h + pad + row * (scale_h + pad + label_h)
        big = pygame.transform.scale(crop, (scale_w, scale_h))
        sheet.blit(big, (x, y))
        value = TIER_VALUE[tier]
        weight = TIER_WEIGHT[tier]
        # Render the line in two colours: tier+value in GOLD_PALE,
        # weight % in a softer cream so it reads as the secondary stat.
        head = f"{tier}  {_value_str(value)}"
        head_img = _pro_font(13).render(head, True, GOLD_PALE)
        wt_img = _pro_font(12).render(f"   ({weight} %)", True, CREAM)
        sheet.blit(head_img, (x + 4, y + scale_h + 4))
        sheet.blit(wt_img, (x + 4 + head_img.get_width(),
                            y + scale_h + 5))
    return sheet


def _build_corner_zoom() -> pygame.Surface:
    """4x zoom of just the slot cabinet at the JACKPOT reveal so the
    typography is unmistakable in a chat preview."""
    frame = _render_frame(1.0, tier="JACKPOT")
    crop = pygame.Rect(0, 0, 140, 110)
    sub = frame.subsurface(crop).copy()
    return pygame.transform.scale(
        sub, (sub.get_width() * 4, sub.get_height() * 4))


def main():
    out = _HERE / "screenshots"
    out.mkdir(parents=True, exist_ok=True)
    for fname in ("slot_pro_triptych.png", "slot_pro_outcomes.png",
                  "slot_pro_outcomes_grid.png", "slot_pro_zoom.png"):
        p = out / fname
        if p.exists():
            p.unlink()

    pygame.image.save(_build_triptych("JACKPOT"), out / "slot_pro_triptych.png")
    print(f"wrote {out / 'slot_pro_triptych.png'}")
    pygame.image.save(_build_outcomes_sheet(), out / "slot_pro_outcomes.png")
    print(f"wrote {out / 'slot_pro_outcomes.png'}")
    pygame.image.save(_build_outcomes_grid(), out / "slot_pro_outcomes_grid.png")
    print(f"wrote {out / 'slot_pro_outcomes_grid.png'}")
    pygame.image.save(_build_corner_zoom(), out / "slot_pro_zoom.png")
    print(f"wrote {out / 'slot_pro_zoom.png'}")


if __name__ == "__main__":
    main()
