"""
Stylish scarlet-macaw with aviator sunglasses — 4 pre-rendered wing frames.
Everything is drawn procedurally once at import with smooth alpha surfaces
(no pixel art). `get_parrot(frame_idx, tilt_deg)` returns a rotated surface,
cached by (frame, rounded-angle).
"""
import math
import pygame

from game.config import GROW_SCALE
from game.draw import (
    BIRD_RED, BIRD_RED_D, BIRD_WING, BIRD_WING_D, BIRD_TIP,
    BIRD_BELLY, BIRD_BEAK, BIRD_BEAK_D, WHITE, BLACK, NEAR_BLACK,
    lerp_color as _lerp_color,
)

SPRITE_W, SPRITE_H = 64, 60

# Shade palette
SHADE_BLACK   = (15, 15, 25)
SHADE_FRAME   = (255, 200, 50)     # gold aviator rim
SHADE_GLINT   = (255, 255, 255)
SHADE_TINT    = (35, 55, 90)       # reflected-sky blue on the lens


def _aaellipse(surf, color, center, rx, ry):
    cx, cy = center
    rect = pygame.Rect(int(cx - rx), int(cy - ry), int(rx * 2), int(ry * 2))
    pygame.draw.ellipse(surf, color, rect)


def _build_wing(angle_deg):
    """Wing polygon rotated around its shoulder anchor."""
    w = pygame.Surface((50, 50), pygame.SRCALPHA)
    # Drop shadow outline
    shadow_pts = [
        (24, 26), (46, 14), (50, 30), (34, 44), (18, 40),
    ]
    pygame.draw.polygon(w, (0, 0, 0, 110), shadow_pts)

    # Main wing feather layer (vivid blue)
    pts = [
        (24, 24), (44, 13), (48, 28), (32, 42), (18, 36),
    ]
    pygame.draw.polygon(w, BIRD_WING, pts)

    # Darker underside
    spts = [
        (24, 24), (32, 42), (18, 36),
    ]
    pygame.draw.polygon(w, BIRD_WING_D, spts)

    # Primary feather tips (green — macaw signature)
    pygame.draw.polygon(w, BIRD_TIP, [
        (44, 13), (50, 18), (48, 28),
    ])
    # A yellow secondary between blue & green for that scarlet-macaw stripe
    pygame.draw.polygon(w, (255, 200, 60), [
        (42, 18), (48, 22), (46, 28), (40, 24),
    ])

    # Feather divider lines
    pygame.draw.line(w, BIRD_WING_D, (26, 25), (42, 18), 2)
    pygame.draw.line(w, BIRD_WING_D, (28, 30), (44, 25), 2)
    pygame.draw.line(w, BIRD_WING_D, (30, 34), (46, 32), 2)
    # Crisp highlight edge
    pygame.draw.line(w, (170, 210, 255), (25, 25), (41, 15), 1)
    return pygame.transform.rotate(w, angle_deg)


def _draw_sunglasses(surf, cx, cy):
    """Aviator shades: two teardrop lenses joined by a gold bridge, with a
    tiny gold nose pad and a white sunlight glint on each lens."""
    # Lens geometry (relative to sprite)
    r_outer = 6
    # Left lens slightly back, right slightly forward because of the head tilt
    left  = (cx - 4, cy)
    right = (cx + 6, cy - 1)

    # Gold frame (outer)
    pygame.draw.circle(surf, SHADE_FRAME, left, r_outer + 1)
    pygame.draw.circle(surf, SHADE_FRAME, right, r_outer + 1)
    # Black lens body
    pygame.draw.circle(surf, SHADE_BLACK, left, r_outer)
    pygame.draw.circle(surf, SHADE_BLACK, right, r_outer)
    # Subtle sky-tint reflected on each lens (upper half)
    tint = pygame.Surface((r_outer * 2, r_outer), pygame.SRCALPHA)
    pygame.draw.ellipse(tint, (*SHADE_TINT, 130), tint.get_rect())
    surf.blit(tint, (left[0] - r_outer, left[1] - r_outer + 1))
    surf.blit(tint, (right[0] - r_outer, right[1] - r_outer + 1))
    # Bright white glint
    pygame.draw.circle(surf, SHADE_GLINT, (left[0] - 2, left[1] - 2), 2)
    pygame.draw.circle(surf, SHADE_GLINT, (right[0] - 2, right[1] - 3), 2)
    # Thin secondary glint
    pygame.draw.circle(surf, (255, 255, 255, 200), (left[0] + 2, left[1] + 2), 1)
    pygame.draw.circle(surf, (255, 255, 255, 200), (right[0] + 2, right[1] + 1), 1)

    # Gold bridge
    pygame.draw.line(surf, SHADE_FRAME, (left[0] + r_outer, left[1]), (right[0] - r_outer, right[1]), 2)
    # Top brow-bar (aviator double-bar)
    pygame.draw.line(surf, SHADE_FRAME,
                     (left[0] - r_outer + 1, left[1] - r_outer + 2),
                     (right[0] + r_outer - 1, right[1] - r_outer + 2), 1)


def _build_frame(wing_angle_deg):
    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)

    # Tail: layered feather fan, vivid red→orange→yellow
    tail_colors = [
        (200,  30,  40),
        (240,  95,  40),
        (255, 160,  55),
        (255, 220,  80),
    ]
    for i, c in enumerate(tail_colors):
        pts = [
            (2 + i * 3, 26 + i * 2),
            (14 + i, 24 + i),
            (20 + i, 30 + i * 2),
            (6 + i * 3, 36 + i * 2),
        ]
        pygame.draw.polygon(surf, c, pts)
    # Tail divider lines
    pygame.draw.line(surf, BIRD_RED_D, (4, 27), (18, 31), 1)
    pygame.draw.line(surf, BIRD_RED_D, (6, 33), (20, 35), 1)

    # Body shadow (soft drop)
    _aaellipse(surf, (120, 20, 25), (34, 35), 19, 14)
    # Body base
    _aaellipse(surf, BIRD_RED, (32, 32), 19, 14)
    # Chest feather texture: a second ellipse blend
    _aaellipse(surf, (255, 100, 100), (30, 29), 13, 8)
    # Belly highlight
    _aaellipse(surf, BIRD_BELLY, (28, 38), 12, 6)
    # Glossy top sheen
    sheen = pygame.Surface((28, 6), pygame.SRCALPHA)
    pygame.draw.ellipse(sheen, (255, 230, 230, 160), sheen.get_rect())
    surf.blit(sheen, (22, 21))

    # Wing (dynamic, behind head but over body)
    wing = _build_wing(wing_angle_deg)
    wr = wing.get_rect(center=(34, 28))
    surf.blit(wing, wr.topleft)

    # Head shadow
    _aaellipse(surf, (150, 15, 20), (48, 23), 12, 11)
    # Head base
    _aaellipse(surf, BIRD_RED, (47, 21), 12, 11)
    # Cheek flush
    _aaellipse(surf, (255, 130, 130), (44, 24), 4, 3)
    # Crown highlight
    _aaellipse(surf, (255, 170, 170), (46, 16), 7, 3)

    # Aviator sunglasses (replaces the plain eye)
    _draw_sunglasses(surf, 50, 20)

    # Beak — hooked, with a glossy highlight
    beak_pts = [
        (55, 21), (61, 24), (58, 28), (52, 26),
    ]
    pygame.draw.polygon(surf, BIRD_BEAK, beak_pts)
    pygame.draw.polygon(surf, BIRD_BEAK_D, beak_pts, 1)
    # Beak gloss
    pygame.draw.line(surf, (255, 230, 150), (55, 22), (59, 24), 1)
    # Lower-beak split line
    pygame.draw.line(surf, BIRD_BEAK_D, (52, 24), (58, 25), 1)

    # Feet tucks
    pygame.draw.line(surf, BIRD_BEAK_D, (28, 45), (26, 49), 2)
    pygame.draw.line(surf, BIRD_BEAK_D, (34, 45), (36, 49), 2)

    return surf


def _add_outline(src: pygame.Surface, outline_color=(20, 12, 18, 220)) -> pygame.Surface:
    """Return a surface with a 1-px dark outline around the sprite silhouette.

    Makes the bird pop against warm sunset stone and dark night skies
    (REVIEW.md finding — bird was hard to track in `14_death_hitflash.png`)."""
    w, h = src.get_size()
    pad = 2
    out = pygame.Surface((w + pad * 2, h + pad * 2), pygame.SRCALPHA)
    # Build an opaque silhouette mask from the source's alpha channel.
    mask = pygame.mask.from_surface(src, threshold=8)
    silhouette = mask.to_surface(setcolor=outline_color, unsetcolor=(0, 0, 0, 0))
    # Blit the silhouette at the 8 neighbour offsets to grow it by 1 px.
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1),
                   (-1, -1), (1, -1), (-1, 1), (1, 1)):
        out.blit(silhouette, (pad + dx, pad + dy))
    # Stamp the real sprite on top.
    out.blit(src, (pad, pad))
    return out


# Four wing angles — up, mid-up, level, down
_WING_ANGLES = (50, 20, -10, -40)

# Lazy: building all four outlined frames cost ~100-300 ms on the WASM
# cold path. Deferring lets the splash paint first; the work runs the
# first time anything actually reads a frame (intro, menu, gameplay).
# Module `__getattr__` keeps `parrot.FRAMES` working for external code.
_FRAMES: "list[pygame.Surface] | None" = None

def _get_frames() -> "list[pygame.Surface]":
    global _FRAMES
    if _FRAMES is None:
        _FRAMES = [_add_outline(_build_frame(a)) for a in _WING_ANGLES]
    return _FRAMES


# ── Hi-res GROW-mode frames ──────────────────────────────────────────────────
# Round-9 picker (commit 0073175) chose v3: build the bird at 4.5× the
# base coordinates, then smoothscale DOWN to grow display size. Ports the
# same draw recipe as `_build_wing` / `_build_frame` / `_add_outline`,
# with every literal coordinate, line width, and ellipse radius
# multiplied by `s`. This produces a crisp grow-mode bird without
# upscaling the small 68×64 base sprite (the prior path's blur source).

_GROW_SS = 3.0 * GROW_SCALE                          # 3× supersample of GROW_SCALE
_GROW_W  = int((SPRITE_W + 4) * GROW_SCALE)
_GROW_H  = int((SPRITE_H + 4) * GROW_SCALE)


def _Sg(v, s): return int(round(v * s))
def _Pg(p, s): return (_Sg(p[0], s), _Sg(p[1], s))
def _Lg(pts, s): return [_Pg(p, s) for p in pts]


def _aaellipse_scaled(surf, color, center, rx, ry, s):
    cx, cy = center
    rect = pygame.Rect(_Sg(cx - rx, s), _Sg(cy - ry, s),
                       _Sg(rx * 2, s),  _Sg(ry * 2, s))
    pygame.draw.ellipse(surf, color, rect)


def _build_wing_scaled(angle_deg, s):
    box = _Sg(50, s)
    w = pygame.Surface((box, box), pygame.SRCALPHA)
    pygame.draw.polygon(w, (0, 0, 0, 110), _Lg(
        [(24, 26), (46, 14), (50, 30), (34, 44), (18, 40)], s))
    pygame.draw.polygon(w, BIRD_WING, _Lg(
        [(24, 24), (44, 13), (48, 28), (32, 42), (18, 36)], s))
    pygame.draw.polygon(w, BIRD_WING_D, _Lg(
        [(24, 24), (32, 42), (18, 36)], s))
    pygame.draw.polygon(w, BIRD_TIP, _Lg(
        [(44, 13), (50, 18), (48, 28)], s))
    pygame.draw.polygon(w, (255, 200, 60), _Lg(
        [(42, 18), (48, 22), (46, 28), (40, 24)], s))
    div_w = max(1, _Sg(2, s))
    pygame.draw.line(w, BIRD_WING_D, _Pg((26, 25), s), _Pg((42, 18), s), div_w)
    pygame.draw.line(w, BIRD_WING_D, _Pg((28, 30), s), _Pg((44, 25), s), div_w)
    pygame.draw.line(w, BIRD_WING_D, _Pg((30, 34), s), _Pg((46, 32), s), div_w)
    pygame.draw.line(w, (170, 210, 255),
                     _Pg((25, 25), s), _Pg((41, 15), s), max(1, _Sg(1, s)))
    return pygame.transform.rotate(w, angle_deg)


def _draw_sunglasses_scaled(surf, cx, cy, s):
    r_outer = 6
    left  = (cx - 4, cy)
    right = (cx + 6, cy - 1)
    pygame.draw.circle(surf, SHADE_FRAME, _Pg(left, s),  _Sg(r_outer + 1, s))
    pygame.draw.circle(surf, SHADE_FRAME, _Pg(right, s), _Sg(r_outer + 1, s))
    pygame.draw.circle(surf, SHADE_BLACK, _Pg(left, s),  _Sg(r_outer, s))
    pygame.draw.circle(surf, SHADE_BLACK, _Pg(right, s), _Sg(r_outer, s))
    tw = _Sg(r_outer * 2, s); th = _Sg(r_outer, s)
    tint = pygame.Surface((tw, th), pygame.SRCALPHA)
    pygame.draw.ellipse(tint, (*SHADE_TINT, 130), tint.get_rect())
    surf.blit(tint, (_Sg(left[0]  - r_outer, s), _Sg(left[1]  - r_outer + 1, s)))
    surf.blit(tint, (_Sg(right[0] - r_outer, s), _Sg(right[1] - r_outer + 1, s)))
    pygame.draw.circle(surf, SHADE_GLINT, _Pg((left[0]  - 2, left[1]  - 2), s), _Sg(2, s))
    pygame.draw.circle(surf, SHADE_GLINT, _Pg((right[0] - 2, right[1] - 3), s), _Sg(2, s))
    pygame.draw.circle(surf, (255, 255, 255, 200),
                       _Pg((left[0]  + 2, left[1]  + 2), s), max(1, _Sg(1, s)))
    pygame.draw.circle(surf, (255, 255, 255, 200),
                       _Pg((right[0] + 2, right[1] + 1), s), max(1, _Sg(1, s)))
    pygame.draw.line(surf, SHADE_FRAME,
                     _Pg((left[0]  + r_outer, left[1]),  s),
                     _Pg((right[0] - r_outer, right[1]), s), max(1, _Sg(2, s)))
    pygame.draw.line(surf, SHADE_FRAME,
                     _Pg((left[0]  - r_outer + 1, left[1]  - r_outer + 2), s),
                     _Pg((right[0] + r_outer - 1, right[1] - r_outer + 2), s),
                     max(1, _Sg(1, s)))


def _build_frame_scaled(wing_angle_deg, s):
    surf = pygame.Surface((_Sg(SPRITE_W, s), _Sg(SPRITE_H, s)), pygame.SRCALPHA)
    tail_colors = [
        (200,  30,  40),
        (240,  95,  40),
        (255, 160,  55),
        (255, 220,  80),
    ]
    for i, c in enumerate(tail_colors):
        pts = [
            (2 + i * 3, 26 + i * 2),
            (14 + i,     24 + i),
            (20 + i,     30 + i * 2),
            (6 + i * 3,  36 + i * 2),
        ]
        pygame.draw.polygon(surf, c, _Lg(pts, s))
    div_w = max(1, _Sg(1, s))
    pygame.draw.line(surf, BIRD_RED_D, _Pg((4, 27), s), _Pg((18, 31), s), div_w)
    pygame.draw.line(surf, BIRD_RED_D, _Pg((6, 33), s), _Pg((20, 35), s), div_w)

    _aaellipse_scaled(surf, (120, 20, 25),  (34, 35), 19, 14, s)
    _aaellipse_scaled(surf, BIRD_RED,       (32, 32), 19, 14, s)
    _aaellipse_scaled(surf, (255, 100, 100),(30, 29), 13,  8, s)
    _aaellipse_scaled(surf, BIRD_BELLY,     (28, 38), 12,  6, s)

    sw, sh = _Sg(28, s), _Sg(6, s)
    sheen = pygame.Surface((sw, sh), pygame.SRCALPHA)
    pygame.draw.ellipse(sheen, (255, 230, 230, 160), sheen.get_rect())
    surf.blit(sheen, (_Sg(22, s), _Sg(21, s)))

    wing = _build_wing_scaled(wing_angle_deg, s)
    surf.blit(wing, wing.get_rect(center=_Pg((34, 28), s)).topleft)

    _aaellipse_scaled(surf, (150, 15, 20),  (48, 23), 12, 11, s)
    _aaellipse_scaled(surf, BIRD_RED,       (47, 21), 12, 11, s)
    _aaellipse_scaled(surf, (255, 130, 130),(44, 24),  4,  3, s)
    _aaellipse_scaled(surf, (255, 170, 170),(46, 16),  7,  3, s)

    _draw_sunglasses_scaled(surf, 50, 20, s)

    beak_pts = [(55, 21), (61, 24), (58, 28), (52, 26)]
    pygame.draw.polygon(surf, BIRD_BEAK,   _Lg(beak_pts, s))
    pygame.draw.polygon(surf, BIRD_BEAK_D, _Lg(beak_pts, s), max(1, _Sg(1, s)))
    pygame.draw.line(surf, (255, 230, 150),
                     _Pg((55, 22), s), _Pg((59, 24), s), max(1, _Sg(1, s)))
    pygame.draw.line(surf, BIRD_BEAK_D,
                     _Pg((52, 24), s), _Pg((58, 25), s), max(1, _Sg(1, s)))

    foot_w = max(1, _Sg(2, s))
    pygame.draw.line(surf, BIRD_BEAK_D, _Pg((28, 45), s), _Pg((26, 49), s), foot_w)
    pygame.draw.line(surf, BIRD_BEAK_D, _Pg((34, 45), s), _Pg((36, 49), s), foot_w)

    return surf


def _add_outline_scaled(src, scale, outline_color=(20, 12, 18, 220)):
    """Outline thickness scales with `scale` so that after smoothscale-down
    to the 102×96 display target the outline reads as ~1 px."""
    w, h = src.get_size()
    r = max(1, int(round(scale)))
    pad = r + 1
    out = pygame.Surface((w + pad * 2, h + pad * 2), pygame.SRCALPHA)
    mask = pygame.mask.from_surface(src, threshold=8)
    silhouette = mask.to_surface(setcolor=outline_color, unsetcolor=(0, 0, 0, 0))
    for dx in range(-r, r + 1):
        for dy in range(-r, r + 1):
            if dx == 0 and dy == 0:
                continue
            if max(abs(dx), abs(dy)) > r:
                continue
            out.blit(silhouette, (pad + dx, pad + dy))
    out.blit(src, (pad, pad))
    return out


def _build_grow_frame(angle_deg):
    """One grow-mode bird frame: 4.5× supersampled body + outline,
    smoothscaled DOWN to grow display size (102×96)."""
    src = _build_frame_scaled(angle_deg, _GROW_SS)
    outlined = _add_outline_scaled(src, _GROW_SS)
    return pygame.transform.smoothscale(outlined, (_GROW_W, _GROW_H))


GROW_FRAMES: "list[pygame.Surface] | None" = None

_grow_rot_cache: dict = {}


def _get_grow_frames() -> "list[pygame.Surface]":
    """Lazy-build the 4 grow-mode parrot frames. At 4.5× supersample
    each frame is expensive (~tens of ms on native, multiples of that
    on WASM) and players who never pick up the GROW power-up never
    need them — building them at import time was adding noticeable
    latency to the splash-to-menu transition. Built once on first
    call and cached for the rest of the session."""
    global GROW_FRAMES
    if GROW_FRAMES is None:
        GROW_FRAMES = [_build_grow_frame(a) for a in _WING_ANGLES]
    return GROW_FRAMES


def get_grow_parrot(frame_idx: int, tilt_deg: float) -> pygame.Surface:
    """Hi-res grow-mode parrot. Pre-built at full grow display size — the
    caller MUST NOT smoothscale-up further."""
    frames = _get_grow_frames()
    frame_idx = frame_idx % len(frames)
    key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
    s = _grow_rot_cache.get(key)
    if s is None:
        s = pygame.transform.rotozoom(frames[frame_idx], key[1], 1.0)
        _grow_rot_cache[key] = s
    return s


# ── parcel sprite (Pip's permanent companion in gameplay) ────────────────────
# Pip carries the parcel through every run. Each visual mode (KFC, ghost,
# triple-buff hat, normal) uses a hand-tuned palette so the parcel reads as
# part of Pip's silhouette in that mode rather than as a colour-tinted overlay.

PARCEL_SIZE = 22

_PARCEL_PALETTES = {
    "normal": dict(
        BOX_BASE=(180, 130,  80), BOX_SHADE=(110,  75,  40), BOX_HI=(220, 175, 120),
        RIBBON  =(200,  50,  60), RIBBON_HI=(255, 110, 100),
        BOW_FILL=(200,  50,  60), BOW_HI   =(255, 130, 120),
        OUTLINE =( 26,  10,  12),
    ),
    "kfc": dict(  # warm fried-chicken amber to match KFC_FRAMES
        BOX_BASE=(210, 138,  42), BOX_SHADE=(148,  82,  18), BOX_HI=(238, 178,  72),
        RIBBON  =(110,  46,  22), RIBBON_HI=(180, 100,  52),
        BOW_FILL=(110,  46,  22), BOW_HI   =(180, 100,  52),
        OUTLINE =( 60,  32,  16),
    ),
    "ghost": dict(  # cool spectral cyan; alpha breath applied at draw-time
        BOX_BASE=(140, 200, 230), BOX_SHADE=( 88, 150, 190), BOX_HI=(200, 235, 250),
        RIBBON  =(110, 170, 210), RIBBON_HI=(180, 225, 250),
        BOW_FILL=(110, 170, 210), BOW_HI   =(180, 225, 250),
        OUTLINE =( 40,  90, 140),
    ),
    "triple": dict(  # kraft box, gold ribbon to harmonise with the stovepipe hat
        BOX_BASE=(180, 130,  80), BOX_SHADE=(110,  75,  40), BOX_HI=(220, 175, 120),
        RIBBON  =(210, 170,  60), RIBBON_HI=(255, 225, 140),
        BOW_FILL=(210, 170,  60), BOW_HI   =(255, 225, 140),
        OUTLINE =( 50,  32,  12),
    ),
}


def _build_parcel_variant(palette: dict) -> pygame.Surface:
    """Render a 22×22 parcel sprite using the supplied palette. Geometry
    ported from `game.intro._build_parcel` so the silhouette matches the
    intro exactly. Render at 2× detail then smoothscale-down once for crisp
    outlines + tiny pixel reads."""
    BOX_BASE = palette["BOX_BASE"]
    BOX_SHADE = palette["BOX_SHADE"]
    BOX_HI = palette["BOX_HI"]
    RIBBON = palette["RIBBON"]
    RIBBON_HI = palette["RIBBON_HI"]
    BOW_FILL = palette["BOW_FILL"]
    BOW_HI = palette["BOW_HI"]
    OUTLINE = palette["OUTLINE"]

    SIZE = 56
    surf = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)
    BOX_W, BOX_H = 40, 34
    cx, cy = SIZE // 2, SIZE // 2 + 2
    rect = pygame.Rect(cx - BOX_W // 2, cy - BOX_H // 2 + 2, BOX_W, BOX_H)

    # Drop shadow
    sh = pygame.Surface((BOX_W + 8, 10), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (8, 4, 22, 130), sh.get_rect())
    surf.blit(sh, (cx - (BOX_W + 8) // 2, rect.bottom - 4))

    # Box body — outline frame + vertical-gradient fill + top sheen line
    pygame.draw.rect(surf, OUTLINE, rect.inflate(4, 4), border_radius=8)
    body = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    for y in range(rect.h):
        t = y / max(1, rect.h - 1)
        col = _lerp_color(BOX_BASE, BOX_SHADE, t) + (255,)
        body.fill(col, pygame.Rect(0, y, rect.w, 1))
    mask = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(),
                     border_radius=6)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(body, rect.topleft)
    pygame.draw.line(surf, BOX_HI,
                     (rect.x + 4, rect.y + 3),
                     (rect.right - 5, rect.y + 3), 2)

    # Vertical ribbon
    rv_w = 6
    rvx = rect.centerx - rv_w // 2
    pygame.draw.rect(surf, RIBBON, (rvx, rect.y, rv_w, rect.h))
    pygame.draw.line(surf, RIBBON_HI,
                     (rvx + 1, rect.y), (rvx + 1, rect.bottom - 1), 1)

    # Horizontal ribbon
    rh_w = 6
    rhy = rect.y + rect.h // 2 - rh_w // 2
    pygame.draw.rect(surf, RIBBON, (rect.x, rhy, rect.w, rh_w))
    pygame.draw.line(surf, RIBBON_HI, (rect.x, rhy + 1),
                     (rect.right - 1, rhy + 1), 1)

    # Bow on top — two puffy loops + knot + trailing tails
    bx, by = cx, rect.y - 6
    pygame.draw.ellipse(surf, OUTLINE,
                        pygame.Rect(bx - 13, by - 6, 13, 12))
    pygame.draw.ellipse(surf, BOW_FILL,
                        pygame.Rect(bx - 12, by - 5, 11, 10))
    pygame.draw.ellipse(surf, OUTLINE,
                        pygame.Rect(bx,       by - 6, 13, 12))
    pygame.draw.ellipse(surf, BOW_FILL,
                        pygame.Rect(bx + 1,   by - 5, 11, 10))
    pygame.draw.ellipse(surf, BOW_HI, pygame.Rect(bx - 10, by - 4, 4, 3))
    pygame.draw.ellipse(surf, BOW_HI, pygame.Rect(bx + 6,  by - 4, 4, 3))
    pygame.draw.rect(surf, OUTLINE, pygame.Rect(bx - 4, by - 6, 9, 12),
                     border_radius=2)
    pygame.draw.rect(surf, BOW_FILL,  pygame.Rect(bx - 3, by - 5, 7, 10),
                     border_radius=2)
    pygame.draw.line(surf, BOW_HI, (bx - 1, by - 4), (bx - 1, by + 3), 1)
    pygame.draw.line(surf, OUTLINE, (bx - 2, by + 4), (bx - 7, by + 11), 4)
    pygame.draw.line(surf, OUTLINE, (bx + 2, by + 4), (bx + 7, by + 11), 4)
    pygame.draw.line(surf, BOW_FILL, (bx - 2, by + 4), (bx - 6, by + 10), 2)
    pygame.draw.line(surf, BOW_FILL, (bx + 2, by + 4), (bx + 6, by + 10), 2)

    return pygame.transform.smoothscale(surf, (PARCEL_SIZE, PARCEL_SIZE))


# Lazy: building all four parcel variants up front costs ~40-80 ms on
# the WASM cold path. Built on first get_parcel() call instead.
_PARCELS: "dict[str, pygame.Surface] | None" = None


def get_parcel(mode: str = "normal") -> pygame.Surface:
    """Return the parcel sprite for a visual mode. Falls back to 'normal'
    on unknown keys so the parcel never disappears."""
    global _PARCELS
    if _PARCELS is None:
        _PARCELS = {name: _build_parcel_variant(pal)
                    for name, pal in _PARCEL_PALETTES.items()}
    return _PARCELS.get(mode, _PARCELS["normal"])


_rot_cache: dict = {}


def get_parrot(frame_idx: int, tilt_deg: float) -> pygame.Surface:
    """Return rotated parrot surface, cached by (frame, rounded-angle)."""
    frames = _get_frames()
    frame_idx = frame_idx % len(frames)
    key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
    s = _rot_cache.get(key)
    if s is None:
        s = pygame.transform.rotozoom(frames[frame_idx], key[1], 1.0)
        _rot_cache[key] = s
    return s


def __getattr__(name: str):
    """Lazy module attribute: external code reading `parrot.FRAMES`
    triggers the build on first access. Keeps the previous public API
    working without forcing every caller to switch to `_get_frames()`."""
    if name == "FRAMES":
        return _get_frames()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# ── Fried-chicken variant (KFC powerup) ──────────────────────────────────────

_CRISPY_GOLD  = (210, 138,  42)
_CRISPY_DARK  = (148,  82,  18)
_CRISPY_LIGHT = (238, 178,  72)
_CRISPY_SPOT  = (125,  68,  12)


def _build_fried_wing(angle_deg):
    w = pygame.Surface((62, 62), pygame.SRCALPHA)
    # Drop shadow
    pygame.draw.polygon(w, (0, 0, 0, 120),
                        [(22, 28), (52, 10), (58, 32), (40, 50), (16, 44)])
    # Dark crust outline layer
    pygame.draw.polygon(w, _CRISPY_DARK,
                        [(22, 26), (50,  9), (56, 30), (38, 48), (16, 42)])
    # Main batter
    pygame.draw.polygon(w, _CRISPY_GOLD,
                        [(22, 24), (48,  8), (54, 28), (36, 46), (16, 40)])
    # Underside shadow
    pygame.draw.polygon(w, _CRISPY_DARK, [(22, 24), (36, 46), (16, 40)])
    # Bright ridge highlight
    _aaellipse(w, _CRISPY_LIGHT, (38, 22), 12, 6)
    # Dense crispy spots on wing
    for px, py, pr in ((40, 14, 3), (50, 20, 3), (44, 28, 3),
                       (30, 18, 2), (54, 28, 2), (34, 36, 2), (46, 34, 2)):
        pygame.draw.circle(w, _CRISPY_SPOT, (px, py), pr)
    # Crackle lines
    pygame.draw.line(w, _CRISPY_DARK,  (25, 27), (47, 15), 2)
    pygame.draw.line(w, _CRISPY_DARK,  (28, 34), (50, 24), 2)
    pygame.draw.line(w, _CRISPY_DARK,  (30, 40), (52, 32), 1)
    pygame.draw.line(w, _CRISPY_LIGHT, (24, 25), (46, 13), 1)
    pygame.draw.line(w, _CRISPY_LIGHT, (27, 32), (49, 22), 1)
    return pygame.transform.rotate(w, angle_deg)


def _build_fried_frame(wing_angle_deg):
    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)

    # Tail — golden-brown crispy wedges
    for i, c in enumerate([(148, 82, 18), (178, 108, 28), (208, 138, 42), (228, 162, 58)]):
        pts = [(2 + i*3, 26 + i*2), (14 + i, 24 + i),
               (20 + i, 30 + i*2), (6 + i*3, 36 + i*2)]
        pygame.draw.polygon(surf, c, pts)
    pygame.draw.line(surf, _CRISPY_DARK, (4, 27), (18, 31), 1)
    pygame.draw.line(surf, _CRISPY_DARK, (6, 33), (20, 35), 1)

    # Body — plumper, more layered
    _aaellipse(surf, ( 85,  44,  5),   (34, 36), 23, 17)  # deep drop shadow
    _aaellipse(surf, _CRISPY_DARK,     (33, 35), 22, 16)  # dark base crust
    _aaellipse(surf, _CRISPY_GOLD,     (32, 33), 21, 15)  # main batter coat
    _aaellipse(surf, _CRISPY_LIGHT,    (29, 28), 15, 10)  # bright breast peak
    _aaellipse(surf, (242, 190, 80),   (27, 39), 14,  8)  # belly warmth
    _aaellipse(surf, _CRISPY_DARK,     (32, 45), 18,  5)  # bottom shadow

    # Dense crispy spots — varied sizes
    for px, py, pr in ((20, 30, 3), (37, 27, 3), (43, 35, 3),
                       (24, 39, 2), (38, 39, 2), (28, 34, 2),
                       (32, 26, 2), (44, 30, 2), (16, 37, 2),
                       (34, 42, 2), (40, 24, 1), (22, 43, 1)):
        pygame.draw.circle(surf, _CRISPY_SPOT, (px, py), pr)

    # Crackle lines — dark valley + gold ridge = raised batter texture
    for x1, y1, x2, y2 in [(14, 30, 23, 25), (37, 25, 47, 30),
                            (15, 39, 25, 44), (40, 38, 50, 33),
                            (22, 34, 31, 29), (34, 39, 43, 36)]:
        pygame.draw.line(surf, _CRISPY_DARK,  (x1,   y1  ), (x2,   y2  ), 1)
        pygame.draw.line(surf, _CRISPY_LIGHT, (x1-1, y1-1), (x2-1, y2-1), 1)

    # Golden grease sheen
    sheen = pygame.Surface((30, 7), pygame.SRCALPHA)
    pygame.draw.ellipse(sheen, (255, 225, 145, 130), sheen.get_rect())
    surf.blit(sheen, (17, 20))

    # Wing — larger, anchored higher so it fans out prominently
    wing = _build_fried_wing(wing_angle_deg)
    surf.blit(wing, wing.get_rect(center=(32, 24)).topleft)

    # Head — slightly bigger
    _aaellipse(surf, ( 95,  50,  6),   (49, 23), 13, 12)
    _aaellipse(surf, _CRISPY_GOLD,     (48, 21), 13, 12)
    _aaellipse(surf, _CRISPY_LIGHT,    (45, 24),  5,  4)
    _aaellipse(surf, (232, 172, 68),   (47, 15),  8,  4)
    for px, py, pr in ((52, 18, 2), (45, 22, 2), (51, 25, 1)):
        pygame.draw.circle(surf, _CRISPY_SPOT, (px, py), pr)

    # Eyes
    pygame.draw.circle(surf, WHITE,        (51, 20), 4)
    pygame.draw.circle(surf, (15, 15, 25), (52, 20), 2)
    pygame.draw.circle(surf, WHITE,        (53, 18), 1)

    # Beak
    beak_pts = [(55, 21), (61, 24), (58, 28), (52, 26)]
    pygame.draw.polygon(surf, BIRD_BEAK,   beak_pts)
    pygame.draw.polygon(surf, BIRD_BEAK_D, beak_pts, 1)
    pygame.draw.line(surf, (255, 230, 150), (55, 22), (59, 24), 1)
    pygame.draw.line(surf, BIRD_BEAK_D,    (52, 24), (58, 25), 1)

    # Simple tucked legs (original style)
    for lx, ly, ex, ey in ((28, 44, 24, 51), (34, 44, 38, 51)):
        pygame.draw.line(surf, _CRISPY_DARK, (lx, ly), (ex, ey), 3)
        pygame.draw.circle(surf, _CRISPY_GOLD, (ex, ey), 3)
        pygame.draw.circle(surf, _CRISPY_DARK, (ex, ey), 3, 1)

    return surf


KFC_FRAMES: "list[pygame.Surface] | None" = None

_kfc_rot_cache: dict = {}


def _get_kfc_frames() -> "list[pygame.Surface]":
    """Lazy-build the 4 KFC-mode parrot frames (same reasoning as
    _get_grow_frames — players who never pick up the KFC power-up
    never need them, so we don't pay the cost at boot)."""
    global KFC_FRAMES
    if KFC_FRAMES is None:
        KFC_FRAMES = [_add_outline(_build_fried_frame(a)) for a in _WING_ANGLES]
    return KFC_FRAMES


def get_fried_parrot(frame_idx: int, tilt_deg: float) -> pygame.Surface:
    """Return rotated fried-chicken parrot, cached by (frame, rounded-angle)."""
    frames = _get_kfc_frames()
    frame_idx = frame_idx % len(frames)
    key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
    s = _kfc_rot_cache.get(key)
    if s is None:
        s = pygame.transform.rotozoom(frames[frame_idx], key[1], 1.0)
        _kfc_rot_cache[key] = s
    return s


# ── Phoenix variants ────────────────────────────────────────────────────────
# Hand-painted phoenix sprite — built from scratch rather than tinting Pip,
# so the silhouette is visibly different from the base parrot: long flame-
# plume tail, sweeping flame-feathered wings, multi-layer crown of fire,
# molten-gold body gradient, and embedded ember sparks around the body.
# Sunglasses and beak are kept so Pip is still recognizable inside the
# fire. Per-variant differentiation is purely a palette swap — every
# variant gets the same hand-painted base.

_PHOENIX_FRAMES_BY_VARIANT: "dict[str, list[pygame.Surface]]" = {}
_phoenix_rot_cache_by_variant: "dict[str, dict]" = {}

# Each palette is (outer→inner) for fire layers + body colour stops + crown
# stack + ember dot colour + whether the eye glows through the sunglasses.
# The five fire layers run deepest→hottest (outer dark crimson edge through
# white-hot core) so polygons can be stacked outermost-first.
PHOENIX_PALETTES = {
    "classic": dict(
        flame=[(120, 18, 26), (215, 55, 30), (255, 130, 40),
               (255, 215,  85), (255, 245, 180)],
        body_shadow=(120, 28,  28),
        body_base  =(230, 65,  40),
        body_hi    =(255, 150, 60),
        body_belly =(255, 215, 110),
        body_sheen =(255, 240, 200, 170),
        crown      =[(240, 100, 30), (255, 200, 80), (255, 245, 180)],
        ember      =(255, 220, 110),
        eye_glow   =False,
    ),
    "solar": dict(
        # Solar is the Eastern fenghuang/hō-ō reading — gold and white-hot
        # rather than red and burning. Body stays warm-gold so it doesn't
        # vanish against the sun-ray halo.
        flame=[(180,  95, 30), (240, 170, 50), (255, 220, 100),
               (255, 245, 170), (255, 252, 230)],
        body_shadow=(170, 110,  40),
        body_base  =(245, 195,  70),
        body_hi    =(255, 230, 150),
        body_belly =(255, 248, 215),
        body_sheen =(255, 252, 230, 180),
        crown      =[(220, 150, 50), (255, 220, 110), (255, 252, 230)],
        ember      =(255, 245, 180),
        eye_glow   =True,
    ),
    # Ember/Mythic/Ashes share the classic palette — they differentiate
    # at the halo / rebirth / perk layers, not at the body palette.
    "ember":  None,
    "mythic": None,
    "ashes":  None,
}
PHOENIX_PALETTES["ember"]  = PHOENIX_PALETTES["classic"]
PHOENIX_PALETTES["ashes"]  = PHOENIX_PALETTES["classic"]
# Mythic copies classic but flips the eye glow on and brightens the crown
# tip so the storybook variant reads as more elaborate.
_mythic = dict(PHOENIX_PALETTES["classic"])
_mythic["eye_glow"] = True
_mythic["crown"]    = [(220,  80, 30), (255, 180, 70), (255, 252, 220)]
PHOENIX_PALETTES["mythic"] = _mythic


def _build_phoenix_wing(angle_deg, palette):
    """A sweeping flame-feather wing — 5 stacked layers from deepest
    crimson down through orange / gold / white-hot, with three feather
    divider lines etched in the deep crimson. Bigger and more dramatic
    than `_build_wing` so the bird's silhouette reads as 'wings on fire'
    rather than 'parrot with extra red.'"""
    box = 60
    w = pygame.Surface((box, box), pygame.SRCALPHA)
    f = palette["flame"]
    # Drop shadow silhouette (translucent black so the wing looks lit
    # from inside against any background).
    pygame.draw.polygon(w, (10, 5, 12, 150), [
        (22, 32), (36, 12), (52, 8), (58, 22), (52, 38), (32, 46), (18, 38),
    ])
    # 1. Deep crimson outer feather (longest sweep top-back, longest plume bottom)
    pygame.draw.polygon(w, f[0], [
        (22, 30), (36, 10), (50, 6), (56, 20), (50, 36), (32, 44), (18, 36),
    ])
    # 2. Orange mid feather
    pygame.draw.polygon(w, f[1], [
        (22, 30), (34, 14), (46, 12), (50, 22), (44, 34), (28, 40), (20, 34),
    ])
    # 3. Gold inner feather
    pygame.draw.polygon(w, f[2], [
        (22, 30), (32, 18), (42, 18), (44, 26), (38, 34), (26, 36), (22, 34),
    ])
    # 4. Bright yellow accent
    pygame.draw.polygon(w, f[3], [
        (24, 30), (32, 22), (38, 24), (36, 30), (28, 32),
    ])
    # 5. White-hot pinpoint along the leading edge
    pygame.draw.line(w, f[4], (25, 30), (38, 12), 1)
    pygame.draw.line(w, f[4], (26, 33), (44, 20), 1)
    # Feather divider strokes in deep crimson — give the wing visible
    # plumage lines without breaking the gradient.
    pygame.draw.line(w, f[0], (24, 30), (46, 12), 2)
    pygame.draw.line(w, f[0], (26, 34), (48, 22), 2)
    pygame.draw.line(w, f[0], (28, 38), (44, 32), 2)
    # Trailing ember sparks off the wing tips.
    pygame.draw.circle(w, f[3], (52,  8), 1)
    pygame.draw.circle(w, f[3], (56, 20), 1)
    pygame.draw.circle(w, f[3], (52, 38), 1)
    return pygame.transform.rotate(w, angle_deg)


def _paint_phoenix_tail(surf, palette):
    """Long multi-layered flame plume trailing back from the body.
    Five stacked flame tongues with outermost = darkest crimson, innermost
    = white-hot. Anchored at the body and sweeping left+down, with a
    secondary plume curling up-back so the silhouette reads as a banner
    of fire rather than a tail."""
    f = palette["flame"]
    # Drop shadow under the tail for depth.
    pygame.draw.polygon(surf, (10, 5, 12, 130), [
        (22, 30), (4, 26), (-3, 31), (2, 39), (12, 41), (22, 36),
    ])
    # Layer 1 — deepest crimson outer flame plume
    pygame.draw.polygon(surf, f[0], [
        (22, 28), (4, 23), (-3, 28), (1, 37), (10, 40), (22, 36),
    ])
    # Secondary upper plume (curls up over the back)
    pygame.draw.polygon(surf, f[0], [
        (22, 26), (8, 16), (3, 18), (12, 26),
    ])
    # Layer 2 — orange
    pygame.draw.polygon(surf, f[1], [
        (22, 28), (6, 24), (1, 28), (4, 35), (12, 38), (22, 34),
    ])
    pygame.draw.polygon(surf, f[1], [
        (22, 26), (10, 18), (6, 19), (14, 26),
    ])
    # Layer 3 — gold
    pygame.draw.polygon(surf, f[2], [
        (22, 28), (10, 26), (6, 29), (8, 33), (14, 35), (22, 32),
    ])
    # Layer 4 — bright yellow inner
    pygame.draw.polygon(surf, f[3], [
        (22, 28), (14, 27), (12, 30), (14, 33), (20, 33),
    ])
    # Layer 5 — white-hot core line
    pygame.draw.line(surf, f[4], (4, 28), (20, 30), 1)
    pygame.draw.line(surf, f[4], (8, 32), (18, 32), 1)
    # Ember sparks drifting off the tail tip.
    pygame.draw.circle(surf, f[3], (-2, 30), 1)
    pygame.draw.circle(surf, f[3], (-4, 33), 1)
    pygame.draw.circle(surf, f[3], (1, 22), 1)


def _paint_phoenix_crown(surf, palette):
    """5-plume flame crown rising from the top of the head. Each plume
    is three stacked triangles (crimson base, orange mid, hot tip) so
    the crown reads as a layered fire rather than a single triangle."""
    crown = palette["crown"]
    for fx, fy_top, hw, hh in (
        (47,  0,  6, 14),  # tallest central plume
        (41,  6,  4, 10),
        (53,  6,  4, 10),
        (36, 10,  3,  6),  # outer wing plumes
        (58, 10,  3,  6),
    ):
        base_y = fy_top + hh
        pygame.draw.polygon(surf, crown[0], [
            (fx - hw, base_y),
            (fx + hw, base_y),
            (fx,      fy_top),
        ])
        pygame.draw.polygon(surf, crown[1], [
            (fx - max(1, hw - 1), base_y - 1),
            (fx + max(1, hw - 1), base_y - 1),
            (fx,                  fy_top + 3),
        ])
        pygame.draw.polygon(surf, crown[2], [
            (fx - max(1, hw // 2), base_y - 2),
            (fx + max(1, hw // 2), base_y - 2),
            (fx,                   fy_top + 5),
        ])


def _build_phoenix_frame(wing_angle_deg, variant: str) -> pygame.Surface:
    """One hand-painted phoenix frame. Drawn from scratch so the silhouette
    is genuinely a phoenix (long flame tail + flame wings + crown) rather
    than a tinted parrot. Coordinates are native (64×60); the existing
    rotation/cache pipeline handles the rest."""
    palette = PHOENIX_PALETTES[variant]
    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)

    # 1. Tail — long flame plume painted BEFORE the body so the body
    #    overlaps it at the anchor seam.
    _paint_phoenix_tail(surf, palette)

    # 2. Body — molten-gold gradient. Slightly bigger drop shadow than
    #    the base parrot to ground the bird against the flame plume.
    _aaellipse(surf, palette["body_shadow"], (34, 35), 20, 14)
    _aaellipse(surf, palette["body_base"],   (32, 32), 19, 14)
    _aaellipse(surf, palette["body_hi"],     (30, 28), 14, 8)
    _aaellipse(surf, palette["body_belly"],  (28, 38), 12, 6)
    # Glossy top sheen — pushes the body's centre toward bright gold.
    sheen = pygame.Surface((30, 6), pygame.SRCALPHA)
    pygame.draw.ellipse(sheen, palette["body_sheen"], sheen.get_rect())
    surf.blit(sheen, (21, 21))

    # 3. Wing (dynamic — rotated per `_WING_ANGLES` for flap animation).
    wing = _build_phoenix_wing(wing_angle_deg, palette)
    wr = wing.get_rect(center=(34, 27))
    surf.blit(wing, wr.topleft)

    # 4. Head — same molten gradient as the body so the bird reads as one
    #    creature rather than a body wearing a head.
    _aaellipse(surf, palette["body_shadow"], (48, 23), 12, 11)
    _aaellipse(surf, palette["body_base"],   (47, 21), 12, 11)
    _aaellipse(surf, palette["body_hi"],     (44, 24),  4,  3)
    _aaellipse(surf, palette["body_belly"],  (46, 16),  7,  3)

    # 5. Crown of flame (drawn ON TOP of the head so the plumes overlap
    #    the head's upper rim).
    _paint_phoenix_crown(surf, palette)

    # 6. Sunglasses (Pip's identity — same coordinates as the base parrot).
    _draw_sunglasses(surf, 50, 20)
    # Optional eye glow that pierces through the lens — used by solar
    # and mythic to sell "the bird's eyes are alight."
    if palette.get("eye_glow"):
        glow = pygame.Surface((14, 14), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 240, 160, 220), (7, 7), 6)
        pygame.draw.circle(glow, (255, 255, 230, 255), (7, 7), 3)
        pygame.draw.circle(glow, (255, 255, 255, 255), (7, 7), 1)
        surf.blit(glow, (50 - 7, 20 - 7), special_flags=pygame.BLEND_RGBA_ADD)

    # 7. Beak — hooked, with a glossy highlight matching the base parrot.
    beak_pts = [(56, 21), (62, 24), (58, 28), (53, 26)]
    pygame.draw.polygon(surf, BIRD_BEAK,   beak_pts)
    pygame.draw.polygon(surf, BIRD_BEAK_D, beak_pts, 1)
    pygame.draw.line(surf,    (255, 240, 180), (56, 22), (60, 24), 1)
    pygame.draw.line(surf,    BIRD_BEAK_D,     (54, 25), (60, 26), 1)

    # 8. Body ember sparks — small bright pixel dots scattered around
    #    the silhouette so the bird visibly throws sparks at rest.
    ember = palette["ember"]
    for ex, ey in (
        (16, 18), (24, 12), (38, 10), (50, 8),
        (60,  28), (58, 38), (44, 46), (28, 48),
        (12, 36), (8, 22), (32, 14), (20, 26),
    ):
        pygame.draw.circle(surf, ember, (ex, ey), 1)
    # Two slightly bigger highlight sparks
    pygame.draw.circle(surf, palette["body_belly"], (44, 12), 2)
    pygame.draw.circle(surf, palette["body_belly"], (16, 40), 2)

    return surf


def _get_phoenix_frames(variant: str) -> "list[pygame.Surface]":
    frames = _PHOENIX_FRAMES_BY_VARIANT.get(variant)
    if frames is None:
        frames = [_add_outline(_build_phoenix_frame(a, variant))
                  for a in _WING_ANGLES]
        _PHOENIX_FRAMES_BY_VARIANT[variant] = frames
        _phoenix_rot_cache_by_variant[variant] = {}
    return frames


def get_phoenix_parrot(frame_idx: int, tilt_deg: float,
                       variant: "str | None" = None) -> pygame.Surface:
    """Return rotated phoenix-mode parrot, cached by (frame, rounded-angle).
    Reads PHOENIX_VARIANT from config when `variant` is None."""
    if variant is None:
        from game.config import PHOENIX_VARIANT
        variant = PHOENIX_VARIANT
    frames = _get_phoenix_frames(variant)
    cache = _phoenix_rot_cache_by_variant[variant]
    frame_idx = frame_idx % len(frames)
    key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
    s = cache.get(key)
    if s is None:
        s = pygame.transform.rotozoom(frames[frame_idx], key[1], 1.0)
        cache[key] = s
    return s


# ── Ghost variant ─────────────────────────────────────────────────────────────
#
# The ghost-parrot frames are built procedurally in
# `game.dollar_parrot_ghost.build_spectral_frame` — a full hand-drawn parrot
# in cool cyan tones with a soft halo. Lazy-init avoids the circular import
# (dollar_parrot_ghost imports FRAMES / _add_outline from this module).

_ghost_frames: "list[pygame.Surface] | None" = None
_ghost_cache: dict = {}


def _ensure_ghost_frames():
    global _ghost_frames
    if _ghost_frames is None:
        from game.dollar_parrot_ghost import (
            build_ghost_variant_frames, build_spectral_frame,
        )
        _ghost_frames = build_ghost_variant_frames(build_spectral_frame)
    return _ghost_frames


def get_ghost_parrot(frame_idx: int, tilt_deg: float) -> pygame.Surface:
    """Return rotated ghost parrot, cached by (frame, rounded-angle)."""
    frames = _ensure_ghost_frames()
    frame_idx = frame_idx % len(frames)
    key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
    s = _ghost_cache.get(key)
    if s is None:
        s = pygame.transform.rotozoom(frames[frame_idx], key[1], 1.0)
        _ghost_cache[key] = s
    return s


# ── Triple-buff hat variant ───────────────────────────────────────────────────
# Lazily built on first use to avoid a circular import (dollar_parrot_hat
# imports from parrot for the body sprite).
_hat_frames: "list | None" = None
_hat_cache: dict = {}


def _ensure_hat_frames():
    global _hat_frames
    if _hat_frames is None:
        from game.dollar_parrot_hat import build_hat_frames, draw_stovepipe
        _hat_frames = build_hat_frames(draw_stovepipe)
    return _hat_frames


def get_hat_parrot(frame_idx: int, tilt_deg: float) -> pygame.Surface:
    """Return rotated stovepipe-hatted parrot, cached by (frame, rounded-angle)."""
    frames = _ensure_hat_frames()
    frame_idx = frame_idx % len(frames)
    key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
    s = _hat_cache.get(key)
    if s is None:
        s = pygame.transform.rotozoom(frames[frame_idx], key[1], 1.0)
        _hat_cache[key] = s
    return s


# ── Stacked-powerup combo helpers ────────────────────────────────────────────
# When kfc, ghost, and triple flags can all be true simultaneously, the
# default cascade in Bird.draw silently dropped all but the top-priority
# mode. These accessors give Bird.draw a dedicated sprite for every
# reachable combo. Themed hats live in dollar_parrot_hat; the cyan tint
# helper sits here (parrot.py) since both hatted and bare-fried-ghost
# combos use it.

def _cyan_tint_in_place(sprite, tint=(170, 230, 255), strength=0.55):
    """Shift a sprite's RGB toward cool cyan while preserving its alpha
    silhouette. Cheap derivation that turns a fried-chicken sprite into a
    spectral-fried hybrid without rebuilding a full palette pixel-by-
    pixel.

    `strength` is the alpha of the cyan overlay (0 = no effect, 1 = full
    cyan replacement). Implementation: build a solid cyan layer, mask it
    to the sprite silhouette so cyan doesn't leak into transparent
    regions, then alpha-blend onto the sprite."""
    sw, sh = sprite.get_size()
    overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
    overlay.fill((*tint, int(255 * strength)))
    overlay.blit(sprite, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    sprite.blit(overlay, (0, 0))


# kfc + triple — fried bird + crispy KFC hat
_kfc_hat_frames: "list | None" = None
_kfc_hat_cache: dict = {}


def _ensure_kfc_hat_frames():
    global _kfc_hat_frames
    if _kfc_hat_frames is None:
        from game.dollar_parrot_hat import build_kfc_hat_frames
        _kfc_hat_frames = build_kfc_hat_frames()
    return _kfc_hat_frames


def get_kfc_hat_parrot(frame_idx: int, tilt_deg: float) -> pygame.Surface:
    frames = _ensure_kfc_hat_frames()
    frame_idx = frame_idx % len(frames)
    key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
    s = _kfc_hat_cache.get(key)
    if s is None:
        s = pygame.transform.rotozoom(frames[frame_idx], key[1], 1.0)
        _kfc_hat_cache[key] = s
    return s


# ghost + triple — spectral bird + spectral hat
_ghost_hat_frames: "list | None" = None
_ghost_hat_cache: dict = {}


def _ensure_ghost_hat_frames():
    global _ghost_hat_frames
    if _ghost_hat_frames is None:
        from game.dollar_parrot_hat import build_ghost_hat_frames
        _ghost_hat_frames = build_ghost_hat_frames()
    return _ghost_hat_frames


def get_ghost_hat_parrot(frame_idx: int, tilt_deg: float) -> pygame.Surface:
    frames = _ensure_ghost_hat_frames()
    frame_idx = frame_idx % len(frames)
    key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
    s = _ghost_hat_cache.get(key)
    if s is None:
        s = pygame.transform.rotozoom(frames[frame_idx], key[1], 1.0)
        _ghost_hat_cache[key] = s
    return s


# kfc + ghost — fried body cyan-tinted to read as spectral fried (no hat)
_kfc_ghost_frames: "list | None" = None
_kfc_ghost_cache: dict = {}


def _ensure_kfc_ghost_frames():
    global _kfc_ghost_frames
    if _kfc_ghost_frames is None:
        frames = []
        for a in _WING_ANGLES:
            f = _build_fried_frame(a).copy()
            _cyan_tint_in_place(f)
            frames.append(_add_outline(f))
        _kfc_ghost_frames = frames
    return _kfc_ghost_frames


def get_kfc_ghost_parrot(frame_idx: int, tilt_deg: float) -> pygame.Surface:
    frames = _ensure_kfc_ghost_frames()
    frame_idx = frame_idx % len(frames)
    key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
    s = _kfc_ghost_cache.get(key)
    if s is None:
        s = pygame.transform.rotozoom(frames[frame_idx], key[1], 1.0)
        _kfc_ghost_cache[key] = s
    return s


# kfc + ghost + triple — full stack: fried + KFC hat composite, all cyan-tinted
_kfc_ghost_hat_frames: "list | None" = None
_kfc_ghost_hat_cache: dict = {}


def _ensure_kfc_ghost_hat_frames():
    global _kfc_ghost_hat_frames
    if _kfc_ghost_hat_frames is None:
        from game.dollar_parrot_hat import build_kfc_ghost_hat_frames
        _kfc_ghost_hat_frames = build_kfc_ghost_hat_frames()
    return _kfc_ghost_hat_frames


def get_kfc_ghost_hat_parrot(frame_idx: int, tilt_deg: float) -> pygame.Surface:
    frames = _ensure_kfc_ghost_hat_frames()
    frame_idx = frame_idx % len(frames)
    key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
    s = _kfc_ghost_hat_cache.get(key)
    if s is None:
        s = pygame.transform.rotozoom(frames[frame_idx], key[1], 1.0)
        _kfc_ghost_hat_cache[key] = s
    return s
