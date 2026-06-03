"""W4 treasure-box pickup sprite + open-lid variant for the cycle-
finale reward animation.

Extracted from `tools/render_treasure_box_grandiose_options.py` (round
3, cell W4 — walnut + brass + 5-pointed brass star). The runtime module
needs to live under `game/` because the WASM bundle only stages
`main.py`, `inject_theme.py`, `pyproject.toml`, and `game/` per the
deploy-hygiene rule in CLAUDE.md.

Two sprites, cached at module scope:

  closed  — the normal in-air pickup icon (walnut chest with the brass
            star lock plate centred on the seam).
  open    — drawn for ~0.6 s after pickup: lid lifted off the body,
            warm gold-glow interior visible in the gap, brass lock
            plate stays bolted to the body so the brass star reads
            above the spilled light.
"""
from __future__ import annotations

import math

import pygame


# ── Footprint + supersample ─────────────────────────────────────────────────
PICKUP_W = 56
PICKUP_H = 46
SS = 7

# ── Palette (verbatim copies of the design-tool constants) ──────────────────
INK   = (22, 18, 34)
CREAM = (250, 244, 222)

WALNUT_HI    = (154, 98, 56)
WALNUT_MID   = (124, 74, 40)
WALNUT_LO    = (78, 42, 20)
WALNUT_GRAIN = (52, 26, 10)

BRASS_HI  = (236, 204, 132)
BRASS_MID = (202, 164, 84)
BRASS_LO  = (140, 108, 44)
BRASS_INK = (90, 62, 18)

GOLD_INK = (110, 72, 10)

# Interior treasure-light gradient — used only by the open variant to
# fill the gap between the raised lid and the body.
GLOW_HI = (255, 244, 196)
GLOW_LO = (220, 152, 48)

# Lid grain ticks reuse the design tool's neutral wood-grain ink so the
# walnut top has the same dark ladder of cross-strokes the docs sheet
# shows.
LID_GRAIN = (72, 40, 18)


def _lerp(a, b, t):
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


def _vgrad_rect(surf, rect, top_col, bot_col, radius=0):
    tmp = pygame.Surface(rect.size, pygame.SRCALPHA)
    h_ = rect.height
    for y in range(h_):
        t = y / max(1, h_ - 1)
        pygame.draw.line(tmp, _lerp(top_col, bot_col, t),
                         (0, y), (rect.width, y))
    if radius:
        mask = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255),
                         mask.get_rect(), border_radius=radius)
        tmp.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(tmp, rect.topleft)


def _chest_body(big, rect, ink_w, top_col, mid_col, lo_col, radius=None):
    if radius is None:
        radius = max(2, int(rect.width * 0.06))
    _vgrad_rect(big, rect, top_col, mid_col, radius=radius)
    foot = pygame.Rect(rect.left, rect.top + int(rect.height * 0.62),
                       rect.width, int(rect.height * 0.40))
    _vgrad_rect(big, foot, mid_col, lo_col, radius=radius)
    pygame.draw.rect(big, INK, rect, ink_w, border_radius=radius)


def _curved_lid(big, lid_rect, ink_w, top_col, mid_col, lo_col,
                grain=True, sheen=True):
    arc_h = int(lid_rect.height * 0.65)
    cx = lid_rect.centerx
    pts = []
    n = 18
    top_y = lid_rect.top - arc_h
    half_w = lid_rect.width // 2
    for i in range(n + 1):
        t = i / n
        ang = math.pi * (1 - t)
        ax = cx + math.cos(ang) * half_w
        ay = lid_rect.top - math.sin(ang) * arc_h
        pts.append((ax, ay))
    pts.append((lid_rect.right, lid_rect.bottom))
    pts.append((lid_rect.left, lid_rect.bottom))
    pygame.draw.polygon(big, mid_col, pts)
    grad_rect = pygame.Rect(lid_rect.left, top_y,
                            lid_rect.width, lid_rect.bottom - top_y)
    grad = pygame.Surface(grad_rect.size, pygame.SRCALPHA)
    for y in range(grad_rect.height):
        t = y / max(1, grad_rect.height - 1)
        pygame.draw.line(grad, _lerp(top_col, lo_col, t),
                         (0, y), (grad_rect.width, y))
    mask = pygame.Surface(grad_rect.size, pygame.SRCALPHA)
    local_pts = [(p[0] - grad_rect.left, p[1] - grad_rect.top) for p in pts]
    pygame.draw.polygon(mask, (255, 255, 255, 255), local_pts)
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(grad, grad_rect.topleft)
    if sheen:
        sh = pygame.Surface((lid_rect.width, arc_h * 2), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (255, 248, 222, 90),
                            (int(lid_rect.width * 0.18),
                             int(arc_h * 0.20),
                             int(lid_rect.width * 0.42),
                             int(arc_h * 0.45)))
        big.blit(sh, (lid_rect.left, top_y))
    if grain:
        for frac in (0.30, 0.55, 0.78):
            y = top_y + int(arc_h * 2 * frac)
            dy = (lid_rect.top - y) / max(1, arc_h)
            dy = max(-1.0, min(1.0, dy))
            hx = int(half_w * math.sqrt(max(0.0, 1.0 - dy * dy)))
            pygame.draw.line(big, LID_GRAIN,
                             (cx - hx + ink_w * 2, y),
                             (cx + hx - ink_w * 2, y),
                             max(1, ink_w // 2))
    pygame.draw.polygon(big, INK, pts, ink_w)
    return pts, top_y


def _new_big():
    return pygame.Surface((PICKUP_W * SS, PICKUP_H * SS), pygame.SRCALPHA)


def _common_layout():
    px_w = PICKUP_W * SS
    px_h = PICKUP_H * SS
    margin_x = int(px_w * 0.08)
    body_top = int(px_h * 0.38)
    body_bot = int(px_h * 0.92)
    lid_top  = int(px_h * 0.20)
    body = pygame.Rect(margin_x, body_top,
                       px_w - 2 * margin_x, body_bot - body_top)
    lid  = pygame.Rect(margin_x, lid_top,
                       px_w - 2 * margin_x, body_top - lid_top)
    return body, lid


def _brass_bands_and_grain(big, body, ink):
    bw = int(body.width * 0.10)
    band_h = body.height - int(body.height * 0.20)
    left_band = pygame.Rect(body.left + int(body.width * 0.08),
                            body.top + int(body.height * 0.10),
                            bw, band_h)
    right_band = pygame.Rect(body.right - int(body.width * 0.08) - bw,
                             body.top + int(body.height * 0.10),
                             bw, band_h)
    for r in (left_band, right_band):
        _vgrad_rect(big, r, BRASS_HI, BRASS_LO, radius=max(1, ink))
        pygame.draw.rect(big, BRASS_INK, r, ink, border_radius=max(1, ink))
        rivet_r = max(2, int(r.height * 0.06))
        for ry in (r.top + r.height // 12, r.bottom - r.height // 12):
            cx = r.centerx
            pygame.draw.circle(big, BRASS_HI, (cx, ry), rivet_r)
            pygame.draw.circle(big, BRASS_INK, (cx, ry), rivet_r,
                               max(1, ink // 2))
    for i in range(1, 4):
        gy = body.top + int(body.height * (i / 4))
        x0 = body.left + int(body.width * 0.10)
        x1 = body.right - int(body.width * 0.10)
        pygame.draw.line(big, WALNUT_GRAIN, (x0, gy), (x1, gy),
                         max(1, ink // 2))


def _lid_strap(big, lid, ink):
    strap_y = lid.top + int(lid.height * 0.10)
    pygame.draw.line(big, BRASS_MID,
                     (lid.left + int(lid.width * 0.04), strap_y),
                     (lid.right - int(lid.width * 0.04), strap_y),
                     max(3, ink))
    pygame.draw.line(big, BRASS_INK,
                     (lid.left + int(lid.width * 0.04), strap_y),
                     (lid.right - int(lid.width * 0.04), strap_y),
                     max(1, ink // 2))


def _brass_star(b, cx, cy, ink_w):
    r_out = max(4, int(SS * 2.6))
    r_in  = max(2, int(r_out * 0.42))
    pts = []
    for k in range(10):
        ang = -math.pi / 2 + k * (math.pi / 5)
        rr = r_out if k % 2 == 0 else r_in
        pts.append((cx + math.cos(ang) * rr,
                    cy + math.sin(ang) * rr))
    pygame.draw.polygon(b, BRASS_HI, pts)
    pygame.draw.polygon(b, BRASS_INK, pts, max(1, ink_w // 2))


def _brass_lock_plate(big, body, ink, with_clasp=True):
    lock_w = int(body.width * 0.30)
    lock_h = int(body.height * 0.55)
    lock_cx = body.centerx
    lock_cy = body.top + lock_h // 2 - int(body.height * 0.08)
    lock = pygame.Rect(0, 0, lock_w, lock_h)
    lock.center = (lock_cx, lock_cy)
    _vgrad_rect(big, lock, BRASS_HI, BRASS_LO, radius=max(2, lock_w // 8))
    pygame.draw.rect(big, BRASS_INK, lock, ink,
                     border_radius=max(2, lock_w // 8))
    _brass_star(big, lock_cx, lock_cy, ink)
    if with_clasp:
        clasp = pygame.Rect(0, 0, int(lock_w * 0.35), int(lock_h * 0.45))
        clasp.midbottom = (lock_cx, body.top + int(lock_h * 0.18))
        _vgrad_rect(big, clasp, BRASS_HI, BRASS_LO,
                    radius=max(2, clasp.width // 6))
        pygame.draw.rect(big, BRASS_INK, clasp, max(1, ink // 2),
                         border_radius=max(2, clasp.width // 6))


def _apply_unifiers(big, body, lid):
    arc_h = int(lid.height * 0.65)
    cx = lid.centerx
    half_w = lid.width // 2
    pts = []
    n = 24
    for i in range(n + 1):
        t = i / n
        ang = math.pi * (1 - t)
        ax = cx + math.cos(ang) * (half_w - max(1, SS // 3))
        ay = lid.top - math.sin(ang) * (arc_h - max(1, SS // 3))
        pts.append((ax, ay))
    if len(pts) >= 2:
        pygame.draw.lines(big, (255, 226, 158), False, pts,
                          max(1, SS // 3))
    L = max(2, int(SS * 0.9))
    for (px, py) in (
        (body.left  + int(body.width * 0.10), body.top  + int(body.height * 0.10)),
        (body.right - int(body.width * 0.10), body.top  + int(body.height * 0.10)),
        (body.left  + int(body.width * 0.10), body.bottom - int(body.height * 0.18)),
        (body.right - int(body.width * 0.10), body.bottom - int(body.height * 0.18)),
    ):
        pygame.draw.circle(big, CREAM, (px, py), max(1, L // 2))
        pygame.draw.line(big, CREAM, (px - L, py), (px + L, py),
                         max(1, SS // 3))
        pygame.draw.line(big, CREAM, (px, py - L), (px, py + L),
                         max(1, SS // 3))


def _smoothscale(big):
    return pygame.transform.smoothscale(big, (PICKUP_W, PICKUP_H))


# ── Builders ────────────────────────────────────────────────────────────────


def _build_closed() -> pygame.Surface:
    big = _new_big()
    ink = max(3, int(SS * 1.05))
    body, lid = _common_layout()

    _chest_body(big, body, ink, WALNUT_HI, WALNUT_MID, WALNUT_LO)
    _brass_bands_and_grain(big, body, ink)
    _curved_lid(big, lid, ink, WALNUT_HI, WALNUT_MID, WALNUT_LO,
                grain=True, sheen=True)
    _lid_strap(big, lid, ink)
    _brass_lock_plate(big, body, ink)
    _apply_unifiers(big, body, lid)
    return _smoothscale(big)


def _build_open() -> pygame.Surface:
    """Lid lifted, gold interior visible through the gap. The brass
    lock stays on the body (where it'd really be bolted); the brass
    star reads as a focal anchor over the spilled treasure light."""
    big = _new_big()
    ink = max(3, int(SS * 1.05))
    body, lid = _common_layout()

    _chest_body(big, body, ink, WALNUT_HI, WALNUT_MID, WALNUT_LO)
    _brass_bands_and_grain(big, body, ink)

    rise = int(body.height * 0.18)
    raised_lid = lid.move(0, -rise)
    _curved_lid(big, raised_lid, ink, WALNUT_HI, WALNUT_MID, WALNUT_LO,
                grain=True, sheen=True)
    _lid_strap(big, raised_lid, ink)

    # Gold-glow interior fills the vertical gap exposed by the lift.
    glow_top = raised_lid.bottom
    glow_bot = body.top + int(body.height * 0.06)
    glow_w = body.width - int(body.width * 0.18)
    glow_h = max(SS, glow_bot - glow_top)
    glow = pygame.Rect(0, 0, glow_w, glow_h)
    glow.midtop = (body.centerx, glow_top)
    _vgrad_rect(big, glow, GLOW_HI, GLOW_LO,
                radius=max(2, int(glow.width * 0.10)))
    pygame.draw.rect(big, GOLD_INK, glow, max(1, ink // 2),
                     border_radius=max(2, int(glow.width * 0.10)))

    # Lock + brass star — drawn AFTER the glow so the focal ornament
    # sits above the spilled light. Clasp dropped (the lid took it).
    _brass_lock_plate(big, body, ink, with_clasp=False)

    _apply_unifiers(big, body, raised_lid)
    return _smoothscale(big)


# ── Public API ──────────────────────────────────────────────────────────────


_CLOSED_CACHE: "pygame.Surface | None" = None
_OPEN_CACHE: "pygame.Surface | None" = None


def _closed_sprite() -> pygame.Surface:
    global _CLOSED_CACHE
    if _CLOSED_CACHE is None:
        _CLOSED_CACHE = _build_closed()
    return _CLOSED_CACHE


def _open_sprite() -> pygame.Surface:
    global _OPEN_CACHE
    if _OPEN_CACHE is None:
        _OPEN_CACHE = _build_open()
    return _OPEN_CACHE


def draw_pickup_icon(surf, cx, cy, pulse):
    """Closed-lid in-air sprite. Gentle sine bob on `pulse`, same idiom
    as the rest of the procedural icon family."""
    icon = _closed_sprite()
    bob = int(round(math.sin(pulse * 1.0) * 2))
    r = icon.get_rect(center=(int(cx), int(cy) + bob))
    surf.blit(icon, r.topleft)


def draw_open_sprite(surf, cx, cy, fade_alpha):
    """Open-lid sprite for the post-pickup lid-pop animation. The
    caller fades alpha 255 → 0 over the animation duration."""
    icon = _open_sprite()
    sprite = icon.copy()
    sprite.set_alpha(max(0, min(255, int(fade_alpha))))
    r = sprite.get_rect(center=(int(cx), int(cy)))
    surf.blit(sprite, r.topleft)
