"""Standalone candidate: `smock-windmill` — a squat, steeply-battered drainage
mill throwing a 4-blade sail cross into the side gutters.

This is a colocated EXPLORATION module for the pillar-landmark design loop. It
follows the shipped pagoda idiom (`candidate_*(surf, top_rect, bot_rect,
palette, seed)`, upright `draw_one` reused for both rects, the top section a
vertical flip of a temp surface) but does NOT import into or modify any game/
module — it only borrows read-only colour + AA helpers so the exploration reads
like the real game.

Silhouette identity: the ONLY radial/diagonal tower in the set. A fat, ground-
heavy weatherboarded cone whose four latticed sails fan OUTWARD into the ±64 px
gutters as a St-Andrew's X, capped by a small boat-cap + fantail at the gap.

Column-fill contract: the collision column (central PIPE_W band) is filled by
the BODY, never the sails. The battered cone is full-column-wide from the base
up to ~three-quarters height, then the boat-cap + finial keep the centreline
continuously occupied all the way to the gap rim — so no empty vertical run
opens across the column at any section height 70–355 px. The sail-X is pure
gutter ornament laid over that solid core.

Run:  python docs/pillar_landmarks/smock-windmill/render.py
Out:  docs/pillar_landmarks/smock-windmill/round_1.png
"""
from __future__ import annotations

import math
import os
import pathlib
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pygame

from game.config import GROUND_Y, PIPE_W
from game import biome
from game.pillar_pagodas import (
    _mix,
    _shade,
    _is_dark_sky,
    _cap_lit_for_dark_sky,
    _cap_dark_for_dark_sky,
    _aa_polyline,
)
from game.pillar_variants import draw_grass_bed, draw_flower_bed


# ── Windmill colour roles (all biome-derived so day→night retints) ───────────
#
# The body is the tarred, matte weatherboard of a drainage mill — grounded in
# stone_dark so it reads near-black-brown by day and doesn't collapse into the
# sky at night (floored via _cap_dark_for_dark_sky where it shades deepest).
# The sail canvas is the bright stone_light so the X punches against the dark
# cone. The boat-cap + finial + hub carry the warm stone_accent focal.

def _body_lit(pal):
    return _cap_lit_for_dark_sky(_mix(pal['stone_dark'], pal['stone_mid'], 0.85),
                                 pal)


def _body_mid(pal):
    return _shade(pal['stone_dark'], -6)


def _body_shadow(pal):
    return _cap_dark_for_dark_sky(_shade(pal['stone_dark'], -42), pal, floor=52)


def _canvas(pal):
    return pal['stone_light']


def _spar(pal):
    return _shade(pal['stone_dark'], -30)


def _cap_col(pal):
    # Painted boat-cap — lighter than the tarred body so the crown reads as a
    # separate roof at the gap rim.
    return _mix(pal['stone_light'], pal['stone_accent'], 0.45)


def _cap_shadow(pal):
    return _shade(pal['stone_mid'], -18)


def _accent(pal):
    return _mix(pal['stone_accent'], (240, 196, 90), 0.55)


# ── Body: scan-lined battered trapezoid ──────────────────────────────────────

def _battered_body(surf, cx, top_y, base_y, hw_top, hw_base, palette):
    """Paint the steeply-battered cone as horizontal scan-lines, each a short
    left-lit → mid → right-shadow ramp, so the flat trapezoid reads as a
    rounded 3-D tarred cylinder at PIPE_W=58 (same volume trick as the pagoda
    `_gradient_rect`, adapted to a per-row sloping width). WASM-safe: uses only
    pygame.draw 1-px vertical lines, no set_at / surfarray."""
    lit, mid, shadow = _body_lit(palette), _body_mid(palette), _body_shadow(palette)
    h = base_y - top_y
    if h < 2:
        return
    for i in range(h):
        y = top_y + i
        t = i / (h - 1)                       # 0 at cap shoulder, 1 at base
        hw = int(round(hw_top + (hw_base - hw_top) * t))
        if hw < 1:
            continue
        # Lit half: cx-hw → cx, ramp lit→mid.  Shadow half: cx → cx+hw, mid→shadow.
        for j in range(hw):
            u = j / max(1, hw)
            pygame.draw.line(surf, _mix(lit, mid, u),
                             (cx - hw + j, y), (cx - hw + j, y), 1)
            pygame.draw.line(surf, _mix(mid, shadow, u),
                             (cx + j, y), (cx + j, y), 1)


def _hoop(surf, cx, y, hw, palette):
    """A single string-course hoop banding the cone — sparse by design (2–3
    total) so the tarred body never stipples into noise against a busy sky."""
    if hw < 4:
        return
    pygame.draw.line(surf, _shade(palette['stone_dark'], -30),
                     (cx - hw, y + 1), (cx + hw, y + 1), 1)
    pygame.draw.line(surf, _mix(palette['stone_mid'], palette['stone_light'], 0.4),
                     (cx - hw, y), (cx + hw, y), 1)


# ── Cap + finial + fantail ───────────────────────────────────────────────────

def _boat_cap(surf, cx, shoulder_y, top_y, hw_cap, palette):
    """Ogee boat-cap from the body shoulder up to the gap tip. Presents a solid
    roofed edge (curb ring + rounded cap) and keeps the centreline continuously
    filled from shoulder to finial so the collision column never breaks."""
    cap_h = shoulder_y - top_y
    if cap_h < 4:
        pygame.draw.line(surf, _cap_col(palette),
                         (cx - hw_cap, shoulder_y), (cx + hw_cap, shoulder_y), 2)
        return
    # Curb ring the cap rotates on — a touch wider than the shoulder.
    pygame.draw.rect(surf, _cap_shadow(palette),
                     (cx - hw_cap - 1, shoulder_y - 2, (hw_cap + 1) * 2, 3))
    pygame.draw.line(surf, _mix(palette['stone_light'], palette['stone_accent'], 0.5),
                     (cx - hw_cap - 1, shoulder_y - 2), (cx + hw_cap, shoulder_y - 2), 1)
    # Ogee profile: bulge out low, sweep in to a rounded tip.
    steps = 10
    left = []
    for k in range(steps + 1):
        tt = k / steps                        # 0 shoulder, 1 tip
        y = shoulder_y - 2 - tt * (cap_h - 2)
        hw = hw_cap * (1.0 - tt ** 1.5) + (1.0 - tt) * tt * hw_cap * 0.35
        left.append((cx - hw, y))
    right = [(cx + (cx - x), y) for (x, y) in reversed(left)]
    poly = left + right
    pygame.draw.polygon(surf, _cap_shadow(palette), poly)
    inner = [(x + 1 if x < cx else x - 1, y) for (x, y) in poly]
    pygame.draw.polygon(surf, _cap_col(palette), inner)
    _aa_polyline(surf, _shade(_cap_shadow(palette), -20), poly, closed=True)
    # Sun-catching highlight down the lit flank of the cap.
    hl = _mix(palette['stone_light'], palette['stone_accent'], 0.7)
    pygame.draw.line(surf, hl, left[1], left[len(left) // 2], 1)


def _fantail(surf, cx, shoulder_y, hw_cap, palette):
    """A small rear fantail spur off the cap — the automatic wind-vane that
    identifies a real mill. Sits to one side over the gutter, pointing down-and-
    out so it never intrudes on the flyable gap."""
    hub_x = cx + hw_cap + 3
    hub_y = shoulder_y + 4
    # Stalk from the cap curb to the little fan hub.
    pygame.draw.line(surf, _spar(palette), (cx + hw_cap - 1, shoulder_y - 1),
                     (hub_x, hub_y), 2)
    blade = _mix(palette['stone_light'], palette['stone_mid'], 0.3)
    for a in (-0.9, -0.45, 0.0, 0.45, 0.9):
        ang = 0.5 + a                          # fan opening down-and-out
        ex = hub_x + math.cos(ang) * 6
        ey = hub_y + math.sin(ang) * 6
        pygame.draw.line(surf, blade, (hub_x, hub_y), (int(ex), int(ey)), 1)
    pygame.draw.circle(surf, _spar(palette), (hub_x, hub_y), 2)


# ── The sail cross ───────────────────────────────────────────────────────────

def _sail_arm(surf, hx, hy, dirx, diry, length, palette):
    """One bold sail arm: a tapered canvas quad with a dark leading spar and
    2–3 rung ticks. Deliberately chunky (not filigree) so the X reads as four
    confident bars at PIPE_W=58 rather than aliasing into noise."""
    tx, ty = hx + dirx * length, hy + diry * length
    px, py = -diry, dirx                       # unit perpendicular
    w0, w1 = 4.2, 1.6                          # wide at hub, taper to tip
    quad = [(hx + px * w0, hy + py * w0),
            (tx + px * w1, ty + py * w1),
            (tx - px * w1, ty - py * w1),
            (hx - px * w0, hy - py * w0)]
    quad = [(int(x), int(y)) for (x, y) in quad]
    pygame.draw.polygon(surf, _canvas(palette), quad)
    _aa_polyline(surf, _spar(palette), quad, closed=True)
    # Rung ticks across the arm (the sail bars).
    rung = _shade(palette['stone_dark'], -18)
    for f in (0.32, 0.58, 0.82):
        mx, my = hx + dirx * length * f, hy + diry * length * f
        wf = w0 + (w1 - w0) * f
        pygame.draw.line(surf, rung,
                         (int(mx + px * wf), int(my + py * wf)),
                         (int(mx - px * wf), int(my - py * wf)), 1)
    # Leading-edge spar down the arm centre.
    pygame.draw.line(surf, _spar(palette), (int(hx), int(hy)), (int(tx), int(ty)), 1)


def _sail_cross(surf, cx, hub_y, arm_len, palette):
    """Four arms fanned as a St-Andrew's X. The angle is shallow (leaning
    toward horizontal) so the arms spill sideways into the ±64 px gutters while
    their VERTICAL reach stays short — the upper tips stop below the gap rim so
    a mirrored pair never bridges or clutters the flyable channel."""
    a = math.radians(34.0)                     # 34° above horizontal — flat-ish X
    ca, sa = math.cos(a), math.sin(a)
    for dirx, diry in ((ca, -sa), (-ca, -sa), (ca, sa), (-ca, sa)):
        _sail_arm(surf, cx, hub_y, dirx, diry, arm_len, palette)
    # Central hub canister + poll-end.
    pygame.draw.circle(surf, _spar(palette), (cx, hub_y), 5)
    pygame.draw.circle(surf, _accent(palette), (cx, hub_y), 3)
    pygame.draw.circle(surf, _mix(palette['stone_light'], palette['stone_accent'], 0.8),
                       (cx - 1, hub_y - 1), 1)


# ── The candidate ────────────────────────────────────────────────────────────

def _draw_one(surf, cx, base_y, top_y, body_w, palette, seed, *, apron=True):
    """One upright smock-mill silhouette filling [top_y, base_y]. Height-
    adaptive: short sections get a stubbier cap, fewer hoops and a smaller
    sail-X, but the battered body always fills the collision column."""
    total_h = base_y - top_y
    if total_h < 20:
        return

    hw_base = int(body_w * 0.74)               # base spills into the gutters
    hw_cap = max(6, int(body_w * 0.42))        # shoulder stays ≥ ~48 px wide
    cap_h = min(int(total_h * 0.16), 24)
    shoulder_y = top_y + cap_h

    # Plinth / stone apron ring under the cone.
    plinth_h = 5 if total_h > 60 else 3
    plinth_w = hw_base * 2 + 8
    pygame.draw.rect(surf, _shade(palette['stone_dark'], -12),
                     (cx - plinth_w // 2, base_y - plinth_h, plinth_w, plinth_h))
    pygame.draw.line(surf, palette['stone_light'],
                     (cx - plinth_w // 2, base_y - plinth_h),
                     (cx + plinth_w // 2, base_y - plinth_h), 1)

    body_base_y = base_y - plinth_h
    _battered_body(surf, cx, shoulder_y, body_base_y, hw_cap, hw_base, palette)

    # Sparse hoop string-courses, count keyed off body height so tall cones get
    # a couple and short ones stay clean.
    body_h = body_base_y - shoulder_y
    n_hoops = max(0, min(3, body_h // 40))
    for k in range(n_hoops):
        ht = (k + 1) / (n_hoops + 1)
        y = int(shoulder_y + body_h * (1 - ht))
        hw = int(round(hw_cap + (hw_base - hw_cap) * (1 - ht)))
        _hoop(surf, cx, y, hw, palette)

    # A single tarred plank door low on the sunlit face — one bold shape, not a
    # field of seams.
    if body_h > 26 and hw_base > 12:
        dw = max(5, hw_base // 4)
        dh = min(14, body_h // 3)
        dx = cx - hw_base // 2
        dy = body_base_y - dh
        pygame.draw.rect(surf, _shade(palette['stone_dark'], -40), (dx, dy, dw, dh))
        pygame.draw.line(surf, _mix(palette['stone_mid'], palette['stone_light'], 0.5),
                         (dx, dy), (dx, dy + dh - 1), 1)

    # Cap + fantail crown the shoulder and hold the centreline to the gap rim.
    _boat_cap(surf, cx, shoulder_y, top_y, hw_cap, palette)
    if total_h > 70:
        _fantail(surf, cx, shoulder_y, hw_cap, palette)
    # Finial ball at the very tip.
    pygame.draw.circle(surf, _accent(palette), (cx, top_y + 1), 2)

    # Sail cross — hub mounted just under the cap, arms fanning into the gutters.
    arm_len = int(min(total_h * 0.44, body_w * 1.28))
    arm_len = max(14, arm_len)
    hub_y = int(top_y + math.sin(math.radians(34.0)) * arm_len + 3)
    # Keep the hub on the upper body / cap shoulder so the X reads mounted, not
    # floating; clamp so the upper arm tips never cross above the gap rim.
    hub_y = max(hub_y, shoulder_y - 1)
    _sail_cross(surf, cx, hub_y, arm_len, palette)

    if apron:
        draw_grass_bed(surf, cx, base_y - 1, plinth_w + 4, 12, palette, seed=seed)
        draw_flower_bed(surf, cx, base_y - 2, plinth_w - 6, 5, seed=seed)


def candidate_smock_windmill(surf, top_rect, bot_rect, palette, seed):
    bcx = bot_rect.x + bot_rect.width // 2
    tcx = top_rect.x + top_rect.width // 2

    if bot_rect.height > 24:
        _draw_one(surf, bcx, bot_rect.bottom, bot_rect.y,
                  bot_rect.width, palette, seed, apron=True)

    if top_rect.height > 24:
        # Structural mirror: draw upright into a temp sized to top_rect.height,
        # flip vertically, blit hanging from the ceiling — the sail-hub end then
        # points at the gap exactly like the bottom section (an X either way up).
        w = surf.get_width()
        tmp = pygame.Surface((w, top_rect.height), pygame.SRCALPHA)
        _draw_one(tmp, tcx, top_rect.height, 0,
                  top_rect.width, palette, seed, apron=False)
        flipped = pygame.transform.flip(tmp, False, True)
        surf.blit(flipped, (0, top_rect.y))


# ── Review harness ───────────────────────────────────────────────────────────

MARGIN = 64
CACHE_W = PIPE_W + MARGIN * 2
PHASE = 0.30
SEED = 13


def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _sky_ground(w, h, pal, ground_h):
    cell = pygame.Surface((w, h))
    sky_h = h - ground_h
    for y in range(sky_h):
        t = y / max(1, sky_h - 1)
        pygame.draw.line(cell, _lerp(pal['sky_top'], pal['horizon'], t), (0, y), (w, y))
    for y in range(sky_h, h):
        t = (y - sky_h) / max(1, h - sky_h)
        pygame.draw.line(cell, _lerp(pal['ground_top'], pal['ground_mid'], t),
                         (0, y), (w, y))
    return cell


def _render_hero(pal):
    # A tall pillar pair over a daytime sky, cropped like the comparison sheet.
    gap_y, gap_h = 150, 150
    top_h = int(gap_y - gap_h / 2)
    bot_top = int(gap_y + gap_h / 2)
    tip_y = bot_top - 12
    base_y = GROUND_Y + 8
    tower_h = base_y - tip_y

    surf = pygame.Surface((CACHE_W, GROUND_Y), pygame.SRCALPHA)
    top_rect = pygame.Rect(MARGIN, 0, PIPE_W, top_h)
    bot_rect = pygame.Rect(MARGIN, bot_top, PIPE_W, GROUND_Y - bot_top)
    candidate_smock_windmill(surf, top_rect, bot_rect, pal, SEED)

    cell = _sky_ground(CACHE_W, tower_h, pal, base_y - GROUND_Y)
    cell.blit(surf, (0, 0), pygame.Rect(0, tip_y, CACHE_W, tower_h))
    return cell


def _render_feas(pal, section_h):
    # Bottom-only section at a fixed height, with the PIPE_W collision column
    # edges overlaid so the fill is auditable.
    head = 16
    cell_h = section_h + head + 10
    surf = pygame.Surface((CACHE_W, GROUND_Y), pygame.SRCALPHA)
    bot_rect = pygame.Rect(MARGIN, GROUND_Y - section_h, PIPE_W, section_h)
    top_rect = pygame.Rect(MARGIN, 0, PIPE_W, 0)
    candidate_smock_windmill(surf, top_rect, bot_rect, pal, SEED)

    cell = _sky_ground(CACHE_W, cell_h, pal, 10)
    crop_top = GROUND_Y - section_h - head
    cell.blit(surf, (0, head - head), pygame.Rect(0, crop_top, CACHE_W, cell_h))
    # Column edges (the true 58 px hitbox) drawn on top.
    cx = MARGIN + PIPE_W // 2
    for ex in (cx - PIPE_W // 2, cx + PIPE_W // 2):
        pygame.draw.line(cell, (255, 60, 60), (ex, 0), (ex, cell_h), 1)
    return cell, cell_h


def main():
    pygame.init()
    pygame.display.set_mode((1, 1))
    pal = biome.palette_for_phase(PHASE)

    hero = _render_hero(pal)
    heights = [70, 210, 355]
    feas = [_render_feas(pal, h) for h in heights]

    pad = 14
    label_h = 26
    title_h = 58
    hero_w, hero_h = hero.get_width(), hero.get_height()
    feas_w = max(c.get_width() for c, _ in feas)
    feas_col_h = title_h + sum(h + label_h + pad for _, h in feas)

    left_w = hero_w + pad * 2
    right_w = feas_w + pad * 2
    sheet_w = left_w + right_w
    sheet_h = max(title_h + hero_h + label_h + pad * 2, feas_col_h + pad)
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((24, 25, 30))

    title = pygame.font.SysFont(None, 30)
    sub = pygame.font.SysFont(None, 18)
    label = pygame.font.SysFont(None, 20)

    sheet.blit(title.render("smock-windmill — round 1", True, (245, 240, 230)),
               (pad, 12))
    sheet.blit(sub.render("battered weatherboard cone + St-Andrew's sail-X  ·  "
                          "daytime PHASE=0.30", True, (170, 172, 182)), (pad, 38))

    # Hero (left).
    hx, hy = pad, title_h
    sheet.blit(hero, (hx, hy))
    pygame.draw.rect(sheet, (60, 62, 72), (hx, hy, hero_w, hero_h), 1)
    lab = label.render("HERO — full pillar pair", True, (255, 224, 150))
    sheet.blit(lab, (hx + (hero_w - lab.get_width()) // 2, hy + hero_h + 4))

    # Feasibility strip (right column).
    fx = left_w + pad
    fy = title_h
    sheet.blit(sub.render("FEASIBILITY — collision-column fill (red = PIPE_W)",
                          True, (255, 224, 150)), (fx, fy - 22))
    for (cell, ch), h in zip(feas, heights):
        sheet.blit(cell, (fx, fy))
        pygame.draw.rect(sheet, (60, 62, 72), (fx, fy, cell.get_width(), ch), 1)
        lab = label.render(f"bottom section  {h} px", True, (210, 212, 222))
        sheet.blit(lab, (fx, fy + ch + 3))
        fy += ch + label_h + pad

    out = _REPO / "docs" / "pillar_landmarks" / "smock-windmill" / "round_1.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(sheet, out)
    print(f"wrote {out}  ({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    main()
