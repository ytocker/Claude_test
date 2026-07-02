"""moai-monolith — a stacked megalithic idol tower (standalone candidate).

An ancestor stack: knobbly volcanic-tuff heads (heavy brow, long nose, pouty
lip, heavy jaw) piled flush head-on-head into a lumpy organic column, crowned
by a red scoria pukao topknot at the gap end. This is the ONLY organic/bulbous
silhouette in the landmark set — the scalloped side-outline (cheeks bulging
out, necks pinching in) plus the jutting brow ledges are the read at small
size, so it survives without relying on interior face relief.

Distinctness pins: a full STACK of many faces forming the whole tower (not one
`stone_face` dressing on a plain pillar), and a deliberately lumpy carved
profile (not the smooth featureless pebbles of the shipped cairn).

Column-fill: a hidden full-height core column (just under the neck width)
guarantees the central PIPE_W band is solid top-to-bottom at every section
height; the heads bulge past it for the wavy outline and pinch back only to the
core edge at the necks, so no empty vertical band can exceed a few px.

Mirror read (pinned): a symmetric two-ended ancestor totem. Both sections cap
their gap end with the red pukao and root their plinth at the world edge; the
top section is a true vertical flip, read as the far end of one totem rather
than a creepy upside-down face.

Standalone: imports biome/config only for the palette + canvas constants; it
does NOT import or modify any game drawing module.

Run:  python docs/pillar_landmarks/moai-monolith/render.py
Out:  docs/pillar_landmarks/moai-monolith/round_1.png
"""
from __future__ import annotations

import math
import os
import pathlib
import random
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game.config import GROUND_Y, PIPE_W
from game import biome

MARGIN = 64                       # matches entities.Pipe eave/ornament gutter
CACHE_W = PIPE_W + MARGIN * 2
CACHE_H = GROUND_Y
PHASE = 0.30                      # daytime so the basalt body reads


# ── local shading helpers (kept standalone; mirror pillar_pagodas idiom) ──
def _mix(a, b, t):
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


def _shade(c, d):
    return (max(0, min(255, c[0] + d)),
            max(0, min(255, c[1] + d)),
            max(0, min(255, c[2] + d)))


def _gradient_rect(surf, rect, lit, mid, shadow):
    """Horizontal 3-stop body gradient so a flat mass reads as a lit volume."""
    if rect.width < 2 or rect.height < 2:
        return
    n = rect.width
    for i in range(n):
        t = i / max(1, n - 1)
        col = _mix(lit, mid, t * 2) if t < 0.5 else _mix(mid, shadow, (t - 0.5) * 2)
        pygame.draw.line(surf, col, (rect.x + i, rect.y),
                         (rect.x + i, rect.bottom - 1), 1)


def _pukao_color(palette):
    # Red scoria topknot — the horizon role carries the day→night retint while
    # the fixed reddish target keeps it reading as volcanic scoria, not gold
    # (same helper idiom as _cedar/_plaster mixing a role toward a set tone).
    return _mix(palette['horizon'], (150, 55, 40), 0.58)


def _grass_seam(surf, cx, cy, palette, rng):
    """A few blades sprouting from a stacked-shoulder seam."""
    mid, top = palette['foliage_mid'], palette['foliage_top']
    for _ in range(4):
        dx = rng.randint(-6, 6)
        h = rng.randint(3, 6)
        lean = rng.randint(-2, 2)
        pygame.draw.line(surf, mid, (cx + dx, cy), (cx + dx + lean, cy - h), 1)
        pygame.draw.line(surf, top, (cx + dx, cy), (cx + dx + lean, cy - h + 1), 1)


# ── one carved head unit ──────────────────────────────────────────────────
def _draw_head(surf, cx, cy, hw, hh, palette):
    """A single tuff head centered at (cx, cy). The bulging ovoid + jutting
    brow break the outline; interior relief (sockets, nose, lip) is close-up
    reward. Lit from the upper-left, matching the roster."""
    tuff_d = palette['stone_dark']
    tuff_m = palette['stone_mid']
    tuff_l = palette['stone_light']
    accent = palette['stone_accent']

    x = cx - hw // 2
    y = cy - hh // 2

    # Base ovoid: dark rim → mid body → lit upper-left cheek for volume.
    pygame.draw.ellipse(surf, tuff_d, (x - 1, y - 1, hw + 2, hh + 2))
    pygame.draw.ellipse(surf, tuff_m, (x + 1, y + 1, hw - 2, hh - 2))
    pygame.draw.ellipse(surf, _mix(tuff_m, tuff_l, 0.6),
                        (x + 2, y + int(hh * 0.14),
                         int(hw * 0.60), int(hh * 0.52)))

    # Heavy brow ledge — a wide lozenge that overhangs the cheeks (breaks the
    # outline sideways) with a lit top ridge and a deep under-shadow.
    bw = hw + 6
    bh = max(4, int(hh * 0.16))
    by = y + int(hh * 0.26)
    pygame.draw.ellipse(surf, tuff_d, (cx - bw // 2, by + 1, bw, bh))        # overhang shadow
    pygame.draw.ellipse(surf, _mix(tuff_m, accent, 0.55),
                        (cx - bw // 2, by - 1, bw, max(3, bh - 1)))          # lit ridge

    # Eye sockets — deep recesses tucked under the brow.
    ew = max(3, int(hw * 0.17))
    eh = max(2, int(hh * 0.11))
    ey = by + bh
    for sgn in (-1, 1):
        ex = cx + sgn * int(hw * 0.21) - ew // 2
        pygame.draw.ellipse(surf, tuff_d, (ex, ey, ew, eh))
        if ew >= 5:  # coral inlay glint, close-up only
            pygame.draw.circle(surf, _shade(accent, 20),
                               (ex + ew // 2, ey + eh // 2), 1)

    # Long straight nose wedge — lit ridge with a shadowed right flank and a
    # fish-hook nostril flare at the base.
    nose_top = by + bh
    nose_bot = y + int(hh * 0.80)
    nw = max(4, int(hw * 0.18))
    if nose_bot > nose_top + 3:
        pygame.draw.polygon(surf, _mix(tuff_m, tuff_l, 0.55),
                            [(cx - 2, nose_top), (cx + 2, nose_top),
                             (cx + nw // 2, nose_bot), (cx - nw // 2, nose_bot)])
        pygame.draw.polygon(surf, _shade(tuff_d, 15),
                            [(cx + 1, nose_top), (cx + 2, nose_top),
                             (cx + nw // 2, nose_bot), (cx + nw // 2 - 2, nose_bot)])
        pygame.draw.line(surf, tuff_d, (cx - nw // 2, nose_bot),
                         (cx + nw // 2, nose_bot), 1)

    # Pouty lip + lit chin ledge across the heavy jaw.
    lw = int(hw * 0.42)
    ly = y + int(hh * 0.88)
    pygame.draw.line(surf, tuff_d, (cx - lw // 2, ly), (cx + lw // 2, ly), 2)
    pygame.draw.line(surf, _mix(tuff_m, accent, 0.5),
                     (cx - lw // 3, ly + 2), (cx + lw // 3, ly + 2), 1)


def _draw_pukao(surf, cx, y_top, pw, ph, palette):
    """Red scoria topknot cylinder capping the gap end — presents a solid wide
    edge at the rim so the collision column stays filled to the tip."""
    puk = _pukao_color(palette)
    lit, mid, shadow = _shade(puk, 34), puk, _shade(puk, -48)
    x = cx - pw // 2
    # Rounded crown.
    pygame.draw.ellipse(surf, shadow, (x - 1, y_top - 1, pw + 2, int(ph * 0.9) + 2))
    pygame.draw.ellipse(surf, mid, (x, y_top, pw, int(ph * 0.9)))
    pygame.draw.ellipse(surf, lit,
                        (x + 3, y_top + 2, int(pw * 0.5), int(ph * 0.5)))
    # Cylinder wall below the crown, shaded for volume.
    body = pygame.Rect(x, y_top + int(ph * 0.42), pw, int(ph * 0.58) + 2)
    _gradient_rect(surf, body, lit, mid, shadow)
    # Dark seat line where the topknot rests on the head.
    pygame.draw.line(surf, shadow, (x + 2, body.bottom - 1),
                     (x + pw - 2, body.bottom - 1), 1)


def _draw_tower_upright(surf, cx, y_top, y_bottom, palette, seed):
    """Draw the idol stack upright with the plinth at y_bottom and the pukao at
    y_top. Callers flip the whole surface for the ceiling-hung top section."""
    rng = random.Random(seed)
    sect_h = y_bottom - y_top
    if sect_h < 8:
        return

    tuff_d = palette['stone_dark']
    tuff_m = palette['stone_mid']
    tuff_l = palette['stone_light']
    accent = palette['stone_accent']

    plinth_h = max(4, min(10, int(sect_h * 0.06)))
    pukao_h = max(12, min(26, int(sect_h * 0.17)))
    # Very short sections can't afford both caps and a head — shed the pukao
    # budget first so a lone head still fills the stub.
    if sect_h < 64:
        pukao_h = max(10, min(pukao_h, sect_h // 4))

    heads_bottom = y_bottom - plinth_h
    heads_top = y_top + pukao_h
    heads_h = heads_bottom - heads_top
    if heads_h < 8:
        heads_top = y_top
        heads_h = heads_bottom - heads_top

    # Height-adaptive head COUNT keyed off a natural head height (~46 px): one
    # big head at ~70 px, a tall stack toward ~355 px.
    head_target = 46
    n = max(1, int(round(heads_h / head_target)))
    pitch = heads_h / n

    # Hidden core column — just under the neck width so it is invisible behind
    # the cheeks yet guarantees the central PIPE_W band is solid at the necks.
    core_w = 54
    core = pygame.Rect(cx - core_w // 2, heads_top - 2, core_w, heads_h + 4)
    _gradient_rect(surf, core, tuff_l, tuff_m, tuff_d)

    hw = 70                                   # cheeks bulge past PIPE_W (58)
    # Heads bottom→top so each upper head overlaps the neck of the one below.
    for i in range(n):
        cy = int(heads_bottom - pitch * (i + 0.5))
        hh = int(pitch * 1.5)
        _draw_head(surf, cx, cy, hw, hh, palette)

    # Grass tufts sprouting from the shoulder seams between heads.
    for i in range(n - 1):
        jy = int(heads_bottom - pitch * (i + 1))
        _grass_seam(surf, cx - 30, jy + 3, palette, rng)
        _grass_seam(surf, cx + 30, jy + 3, palette, rng)

    # Pukao topknot caps the top head at the gap end — wide enough to present a
    # solid edge across the full PIPE_W band at the rim.
    pw = 60
    _draw_pukao(surf, cx, y_top, pw, pukao_h, palette)

    # Base plinth slab — a wide, short footing rooted at the world edge.
    pl_w = 74
    ply = y_bottom - plinth_h
    pygame.draw.rect(surf, tuff_d, (cx - pl_w // 2, ply, pl_w, plinth_h))
    pygame.draw.rect(surf, tuff_m, (cx - pl_w // 2 + 1, ply + 1, pl_w - 2, plinth_h - 2))
    pygame.draw.line(surf, _mix(tuff_m, accent, 0.4),
                     (cx - pl_w // 2 + 3, ply), (cx + pl_w // 2 - 3, ply), 1)


def candidate_moai_monolith(surf, top_rect, bot_rect, palette, seed):
    """Bottom is an ancestor stack rising from the ground, pukao at the gap.
    Top is the same builder flipped — a symmetric two-ended totem hung from the
    ceiling, its pukao pointing into the gap."""
    if bot_rect.height > 0:
        _draw_tower_upright(surf, bot_rect.centerx, bot_rect.y, bot_rect.bottom,
                            palette, seed)

    if top_rect.height > 0:
        tmp = pygame.Surface((surf.get_width(), top_rect.height), pygame.SRCALPHA)
        _draw_tower_upright(tmp, top_rect.centerx, 0, top_rect.height,
                            palette, seed + 1)
        surf.blit(pygame.transform.flip(tmp, False, True), (0, top_rect.y))


# ── review harness ─────────────────────────────────────────────────────────
def _bg(w, h, pal, ground_line):
    """Daytime sky gradient + ground band, matching the comparison sheet."""
    cell = pygame.Surface((w, h))
    for y in range(min(ground_line, h)):
        t = y / max(1, ground_line - 1)
        pygame.draw.line(cell, _mix(pal["sky_top"], pal["horizon"], t), (0, y), (w, y))
    for y in range(ground_line, h):
        t = (y - ground_line) / max(1, h - ground_line)
        pygame.draw.line(cell, _mix(pal["ground_top"], pal["ground_mid"], t),
                         (0, y), (w, y))
    return cell


def _max_empty_run(surf, x0, x1, y0, y1):
    """Longest contiguous vertical run of transparent pixels within the band —
    a numeric feasibility check (never viewed as an image)."""
    worst = 0
    for x in range(x0, x1):
        run = 0
        for y in range(y0, y1):
            if surf.get_at((x, y))[3] == 0:
                run += 1
                worst = max(worst, run)
            else:
                run = 0
    return worst


def main():
    pal = biome.palette_for_phase(PHASE)

    # ── HERO: a tall upright + ceiling-mirrored tower over a daytime sky ──
    gap_y, gap_h = 150, 150
    top_h = int(gap_y - gap_h / 2)
    bot_top = int(gap_y + gap_h / 2)
    full = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    top_rect = pygame.Rect(MARGIN, 0, PIPE_W, top_h)
    bot_rect = pygame.Rect(MARGIN, bot_top, PIPE_W, GROUND_Y - bot_top)
    candidate_moai_monolith(full, top_rect, bot_rect, pal, seed=7)

    tip_y = bot_top - 12
    base_y = GROUND_Y + 8
    hero_h = base_y - tip_y
    hero = _bg(CACHE_W, hero_h, pal, hero_h - (base_y - GROUND_Y))
    hero.blit(full, (0, -tip_y))
    # Column edges on the hero too, so the collision band is legible.
    for ex in (MARGIN, MARGIN + PIPE_W):
        pygame.draw.line(hero, (230, 60, 60), (ex, 0), (ex, hero_h), 1)

    # ── FEASIBILITY STRIP: bottom section at three heights, column edges ──
    strip_heights = [70, 210, 355]
    strips = []
    for h in strip_heights:
        s = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
        br = pygame.Rect(MARGIN, GROUND_Y - h, PIPE_W, h)
        tr = pygame.Rect(MARGIN, 0, PIPE_W, 0)
        candidate_moai_monolith(s, tr, br, pal, seed=7)
        run = _max_empty_run(s, MARGIN, MARGIN + PIPE_W, GROUND_Y - h, GROUND_Y)
        crop = pygame.Surface((CACHE_W, h + 8))
        crop.blit(_bg(CACHE_W, h + 8, pal, h - 0), (0, 0))
        crop.blit(s, (0, -(GROUND_Y - h)))
        for ex in (MARGIN, MARGIN + PIPE_W):
            pygame.draw.line(crop, (230, 60, 60), (ex, 0), (ex, h + 8), 1)
        strips.append((h, crop, run))
        print(f"  strip h={h:3d}  max empty vertical run in PIPE_W band = {run}px")

    # ── compose the sheet ──
    pad = 12
    label_h = 24
    strip_col_w = CACHE_W
    strips_total_h = sum(c.get_height() + label_h + pad for _, c, _ in strips)
    head_h = 60
    sheet_w = pad + CACHE_W + pad + strip_col_w + pad
    sheet_h = head_h + max(hero_h + label_h, strips_total_h) + pad * 2
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((24, 25, 30))

    title = pygame.font.SysFont(None, 32)
    sub = pygame.font.SysFont(None, 19)
    lab = pygame.font.SysFont(None, 20)
    sheet.blit(title.render("moai-monolith — stacked ancestor idol tower",
                            True, (245, 240, 230)), (pad, 12))
    sheet.blit(sub.render("daytime PHASE 0.30  ·  red column edges = PIPE_W (58px) "
                          "collision band  ·  round_1", True, (170, 172, 182)),
               (pad, 38))

    hx, hy = pad, head_h
    sheet.blit(hero, (hx, hy))
    pygame.draw.rect(sheet, (60, 62, 72), (hx, hy, CACHE_W, hero_h), 1)
    sheet.blit(lab.render("HERO — upright + ceiling-mirror totem", True,
                          (255, 224, 150)), (hx, hy + hero_h + 4))

    sx = pad + CACHE_W + pad
    sy = head_h
    sheet.blit(lab.render("FEASIBILITY — bottom section fill", True,
                          (255, 224, 150)), (sx, sy - 20))
    for h, crop, run in strips:
        sheet.blit(crop, (sx, sy))
        pygame.draw.rect(sheet, (60, 62, 72), (sx, sy, CACHE_W, crop.get_height()), 1)
        ok = "OK" if run <= 12 else "FAIL"
        sheet.blit(lab.render(f"h={h}px  ·  max empty run {run}px  [{ok}]", True,
                              (200, 235, 170) if run <= 12 else (255, 140, 140)),
                   (sx, sy + crop.get_height() + 4))
        sy += crop.get_height() + label_h + pad

    out = pathlib.Path(__file__).resolve().parent / "round_1.png"
    pygame.image.save(sheet, out)
    print(f"wrote {out}  ({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    main()
