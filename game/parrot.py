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


# ── Grandiose phoenix variants (Ashes lineage) ──────────────────────────────
# Five hand-painted phoenix designs that BREAK the parrot silhouette: bigger
# canvas (100×76), longer wings, dramatic tails, distinctive body shapes.
# All inherit the Ashes gameplay (ash + falling egg + safe-gap respawn).
#
#   imperial  — eagle-of-fire, wings spread the full width of the canvas
#   fenghuang — Eastern phoenix, 7-plume fan-tail in iridescent colours
#   dragon    — sinuous S-curve body, flame banners instead of feathers
#   comet     — small bird at the front of a massive flame-trail tail
#   royal     — halo-crown of 9 plumes radiating around the head

GRAND_W, GRAND_H = 100, 76
GRAND_CX, GRAND_CY = GRAND_W // 2, GRAND_H // 2  # body anchor


def _grand_canvas() -> pygame.Surface:
    return pygame.Surface((GRAND_W, GRAND_H), pygame.SRCALPHA)


def _draw_small_eye(surf, x, y, glow=False, size: int = 2,
                    glow_color=(255, 240, 160, 220), friendly: bool = False):
    """Tiny eye glyph used by the grandiose variants. `size` scales the
    sclera/pupil; `friendly=True` adds a soft sclera + downsized pupil
    (less menacing read); `glow_color` lets variants tone down the
    intense gold eye-glow."""
    sclera_r = size + (1 if friendly else 0)
    pupil_r  = max(1, size - (1 if friendly else 1))
    pygame.draw.circle(surf, (255, 250, 220), (x, y), sclera_r + 1)
    pygame.draw.circle(surf, ( 20,  10,  10), (x, y), pupil_r)
    # Tiny white catch-light gives a friendlier "alive" eye
    if friendly:
        pygame.draw.circle(surf, (255, 255, 255),
                           (x - max(0, pupil_r - 1),
                            y - max(0, pupil_r - 1)), 1)
    if glow:
        glow_surf = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, glow_color, (5, 5), 4)
        pygame.draw.circle(glow_surf, (255, 255, 230, 255), (5, 5), 2)
        surf.blit(glow_surf, (x - 5, y - 5),
                  special_flags=pygame.BLEND_RGBA_ADD)


# ────────────────────────────────────────────────────────────────────────────
# Variant 1 — IMPERIAL PHOENIX (eagle of fire)
# ────────────────────────────────────────────────────────────────────────────

_IMPERIAL_FLAME = [
    (110,  18, 26), (200,  55, 30), (245, 120, 40),
    (255, 200,  80), (255, 245, 180),
]
_IMPERIAL_BODY = [
    (110, 25, 28), (210,  55,  40),
    (245, 130,  60), (255, 200, 100),
]


def _build_imperial_wing(angle_deg):
    """Eagle wing: long, sweeping, with 5 distinct primary feathers
    fanned at the wingtip. Rendered as a deep-crimson silhouette with
    orange / gold / yellow / white-hot accents along the leading edge."""
    box = 72
    w = pygame.Surface((box, box), pygame.SRCALPHA)
    f = _IMPERIAL_FLAME
    # Drop shadow under the wing silhouette
    pygame.draw.polygon(w, (10, 5, 12, 150), [
        (36, 38), (62, 18), (70, 30), (64, 42), (50, 52), (28, 46),
    ])
    # Outer layer (deep crimson silhouette)
    pygame.draw.polygon(w, f[0], [
        (36, 36), (60, 16), (68, 28), (62, 40), (48, 50), (28, 44),
    ])
    # 5 distinct primary feathers fanned at the wingtip
    primaries = [
        # (root_x, root_y, tip_x, tip_y, half_w)
        (52, 18, 68,  6, 3),
        (54, 22, 70, 14, 3),
        (56, 26, 72, 22, 3),
        (54, 32, 70, 32, 3),
        (52, 38, 66, 42, 3),
    ]
    for rx, ry, tx, ty, hw in primaries:
        # Each primary is a long thin teardrop in deep crimson
        pygame.draw.polygon(w, f[0], [
            (rx - hw, ry), (rx + hw, ry),
            (tx + 1, ty), (tx - 1, ty),
        ])
        # Gold mid-stripe down the feather
        pygame.draw.line(w, f[2], (rx, ry + 1), (tx, ty), 1)
    # Inner orange feather layer
    pygame.draw.polygon(w, f[1], [
        (36, 36), (54, 22), (60, 30), (54, 38), (40, 44),
    ])
    # Gold inner sheen
    pygame.draw.polygon(w, f[2], [
        (38, 36), (50, 28), (54, 32), (48, 38),
    ])
    # White-hot edge highlight along the leading sweep
    pygame.draw.line(w, f[4], (38, 36), (54, 20), 1)
    pygame.draw.line(w, f[4], (40, 39), (58, 28), 1)
    # Feather divider strokes
    pygame.draw.line(w, f[0], (38, 38), (58, 18), 2)
    pygame.draw.line(w, f[0], (40, 42), (58, 28), 2)
    pygame.draw.line(w, f[0], (42, 46), (54, 38), 2)
    return pygame.transform.rotate(w, angle_deg)


def _build_imperial_frame(wing_angle_deg):
    surf = _grand_canvas()
    f = _IMPERIAL_FLAME
    b = _IMPERIAL_BODY
    cx, cy = GRAND_CX, GRAND_CY
    # 1. Tail — banded flame fan trailing down (eagle has a SHORT tail)
    tail_layers = [
        (f[0], [(cx - 12, cy + 12), (cx + 12, cy + 12),
                (cx + 16, cy + 30), (cx + 8, cy + 36),
                (cx, cy + 38), (cx - 8, cy + 36),
                (cx - 16, cy + 30)]),
        (f[1], [(cx - 10, cy + 14), (cx + 10, cy + 14),
                (cx + 12, cy + 28), (cx + 4, cy + 34),
                (cx, cy + 36), (cx - 4, cy + 34),
                (cx - 12, cy + 28)]),
        (f[2], [(cx - 7, cy + 16), (cx + 7, cy + 16),
                (cx + 8, cy + 26), (cx, cy + 32), (cx - 8, cy + 26)]),
        (f[3], [(cx - 4, cy + 18), (cx + 4, cy + 18),
                (cx + 4, cy + 24), (cx, cy + 28), (cx - 4, cy + 24)]),
    ]
    for col, pts in tail_layers:
        pygame.draw.polygon(surf, col, pts)
    # 2. Body — slim vertical oval (eagle proportions)
    pygame.draw.ellipse(surf, b[0],
                        pygame.Rect(cx - 9, cy - 12, 18, 28))
    pygame.draw.ellipse(surf, b[1],
                        pygame.Rect(cx - 8, cy - 11, 16, 26))
    pygame.draw.ellipse(surf, b[2],
                        pygame.Rect(cx - 6, cy - 6, 12, 14))
    pygame.draw.ellipse(surf, b[3],
                        pygame.Rect(cx - 4, cy + 0, 8, 8))
    # 3. Wings — built and rotated by _build_imperial_wing
    wing_right = _build_imperial_wing(wing_angle_deg)
    wing_left  = pygame.transform.flip(wing_right, True, False)
    surf.blit(wing_right, wing_right.get_rect(center=(cx + 16, cy - 4)).topleft)
    surf.blit(wing_left,  wing_left.get_rect(center=(cx - 16, cy - 4)).topleft)
    # 4. Head — small raptor head, forward-facing
    pygame.draw.ellipse(surf, b[0], pygame.Rect(cx - 7, cy - 24, 14, 14))
    pygame.draw.ellipse(surf, b[1], pygame.Rect(cx - 6, cy - 23, 12, 12))
    pygame.draw.ellipse(surf, b[2], pygame.Rect(cx - 4, cy - 19,  6,  4))
    # 5. Hooked raptor beak (replaces the parrot's rounded beak)
    pygame.draw.polygon(surf, (255, 200,  60), [
        (cx + 5, cy - 18), (cx + 11, cy - 14),
        (cx + 7, cy - 12), (cx + 5, cy - 14),
    ])
    pygame.draw.polygon(surf, (140,  90,  20), [
        (cx + 5, cy - 18), (cx + 11, cy - 14),
        (cx + 7, cy - 12), (cx + 5, cy - 14),
    ], 1)
    # 6. Fierce forward-facing eye
    _draw_small_eye(surf, cx + 3, cy - 18, glow=True)
    # 7. Crown — 5 tall plumes rising from the head crown
    for fx_off, fy_top, hw, hh in (
        (cx + 0, cy - 38, 4, 14),  # tallest centre
        (cx - 6, cy - 32, 3,  9),
        (cx + 6, cy - 32, 3,  9),
        (cx -11, cy - 28, 2,  6),  # outer plumes
        (cx +11, cy - 28, 2,  6),
    ):
        base_y = fy_top + hh
        pygame.draw.polygon(surf, f[0], [
            (fx_off - hw, base_y), (fx_off + hw, base_y),
            (fx_off, fy_top)])
        pygame.draw.polygon(surf, f[2], [
            (fx_off - max(1, hw - 1), base_y - 1),
            (fx_off + max(1, hw - 1), base_y - 1),
            (fx_off, fy_top + 3)])
        pygame.draw.polygon(surf, f[4], [
            (fx_off - max(1, hw // 2), base_y - 2),
            (fx_off + max(1, hw // 2), base_y - 2),
            (fx_off, fy_top + 5)])
    # 8. Body ember sparks scattered around
    for ex, ey in ((-18, -12), (-8, -20), (8, -20), (18, -8),
                   (20, 10), (12, 28), (-12, 28), (-20, 8),
                   (-30, -4), (30, -4), (-26, 18), (26, 18)):
        pygame.draw.circle(surf, f[3], (cx + ex, cy + ey), 1)
    return surf


# ────────────────────────────────────────────────────────────────────────────
# Variant 2 — FENGHUANG (Eastern phoenix)
# ────────────────────────────────────────────────────────────────────────────

# Iridescent Eastern palette: teal-blue base, gold mid, red highlights.
_FENGHUANG_BLUE   = ( 40,  80, 140)
_FENGHUANG_TEAL   = ( 60, 130, 170)
_FENGHUANG_AQUA   = (110, 200, 210)
_FENGHUANG_GOLD   = (255, 200,  80)
_FENGHUANG_AMBER  = (255, 160,  50)
_FENGHUANG_RED    = (220,  60,  50)
_FENGHUANG_WHITE  = (255, 250, 220)
_FENGHUANG_PURPLE = (140,  60, 160)


def _build_fenghuang_wing(angle_deg):
    """Smaller ornate wing with scaled feather pattern in iridescent
    blue → teal → aqua tones. Three primary feathers at the tip
    rendered in gold-red so the wing reads as 'jeweled' rather than 'on fire.'"""
    box = 56
    w = pygame.Surface((box, box), pygame.SRCALPHA)
    # Drop shadow
    pygame.draw.polygon(w, (10, 12, 30, 150), [
        (26, 28), (44, 14), (48, 24), (40, 36), (24, 38),
    ])
    # Outer blue layer
    pygame.draw.polygon(w, _FENGHUANG_BLUE, [
        (26, 26), (42, 12), (46, 22), (38, 34), (24, 36),
    ])
    # Teal mid layer
    pygame.draw.polygon(w, _FENGHUANG_TEAL, [
        (26, 26), (38, 14), (42, 22), (36, 30), (26, 32),
    ])
    # Aqua inner sheen
    pygame.draw.polygon(w, _FENGHUANG_AQUA, [
        (28, 26), (36, 18), (38, 24), (32, 28),
    ])
    # 3 gold-red primary feathers at the wingtip
    for rx, ry, tx, ty in ((38, 14, 46, 8), (40, 18, 48, 16), (42, 22, 48, 24)):
        pygame.draw.polygon(w, _FENGHUANG_GOLD, [
            (rx - 1, ry), (rx + 1, ry), (tx, ty)])
        pygame.draw.line(w, _FENGHUANG_RED, (rx, ry), (tx, ty), 1)
    # Scale dots (jewel texture) scattered on the wing body
    for sx, sy in ((30, 22), (32, 26), (34, 30), (28, 30), (36, 24)):
        pygame.draw.circle(w, _FENGHUANG_GOLD, (sx, sy), 1)
    return pygame.transform.rotate(w, angle_deg)


def _build_fenghuang_frame(wing_angle_deg):
    surf = _grand_canvas()
    cx, cy = GRAND_CX, GRAND_CY
    # 1. HERO TAIL FAN — 7 long curving plumes radiating back from the
    #    body, each individually gradient-rendered. This is the dominant
    #    silhouette element.
    tail_origin = (cx - 8, cy + 4)
    plume_specs = [
        # (tip_x_off, tip_y_off, mid_color, tip_color, half_width)
        (-44,  -8, _FENGHUANG_GOLD, _FENGHUANG_RED, 4),    # top plume
        (-46,   6, _FENGHUANG_TEAL, _FENGHUANG_GOLD, 5),   # upper mid
        (-48,  20, _FENGHUANG_BLUE, _FENGHUANG_GOLD, 5),   # CENTRE longest
        (-44,  30, _FENGHUANG_TEAL, _FENGHUANG_RED, 5),    # lower mid
        (-38,  38, _FENGHUANG_GOLD, _FENGHUANG_AMBER, 4),  # lowest
        (-32, -18, _FENGHUANG_PURPLE, _FENGHUANG_GOLD, 3), # top short
        (-28,  44, _FENGHUANG_AMBER, _FENGHUANG_RED, 3),   # bottom short
    ]
    ox, oy = tail_origin
    for tx_off, ty_off, mid, tip, hw in plume_specs:
        tx, ty = ox + tx_off, oy + ty_off
        # Drop shadow first (offset 2,2)
        pygame.draw.polygon(surf, (10, 12, 30, 130), [
            (ox + 1, oy - hw + 1), (ox + 1, oy + hw + 1),
            (tx + 2, ty + 1)])
        # Outer dark blue silhouette
        pygame.draw.polygon(surf, _FENGHUANG_BLUE, [
            (ox, oy - hw), (ox, oy + hw), (tx, ty)])
        # Mid colour (gradient)
        pygame.draw.polygon(surf, mid, [
            (ox + 2, oy - max(1, hw - 1)),
            (ox + 2, oy + max(1, hw - 1)),
            (tx - max(2, abs(tx_off) // 8), ty)])
        # Tip highlight
        pygame.draw.circle(surf, tip,
                           (tx, ty), max(2, hw - 1))
        pygame.draw.circle(surf, _FENGHUANG_WHITE, (tx, ty), 1)
        # Plume divider line down the centre
        pygame.draw.line(surf, _FENGHUANG_GOLD, (ox, oy), (tx, ty), 1)
    # 2. Body — slim oval, blue base
    pygame.draw.ellipse(surf, _FENGHUANG_BLUE,
                        pygame.Rect(cx - 6, cy - 6, 18, 18))
    pygame.draw.ellipse(surf, _FENGHUANG_TEAL,
                        pygame.Rect(cx - 5, cy - 5, 16, 16))
    pygame.draw.ellipse(surf, _FENGHUANG_AQUA,
                        pygame.Rect(cx - 3, cy - 2, 10, 6))
    # Gold belly accent
    pygame.draw.ellipse(surf, _FENGHUANG_GOLD,
                        pygame.Rect(cx - 4, cy + 4, 12, 6))
    # 3. Wings (small + ornate, tucked above the body)
    wing_right = _build_fenghuang_wing(wing_angle_deg)
    wing_left  = pygame.transform.flip(wing_right, True, False)
    surf.blit(wing_right, wing_right.get_rect(center=(cx + 6, cy - 6)).topleft)
    surf.blit(wing_left,  wing_left.get_rect(center=(cx - 12, cy - 6)).topleft)
    # 4. S-curve neck (3 px wide, drawn as a chain of small circles)
    for nx, ny in ((cx + 3, cy - 4), (cx + 5, cy - 8),
                   (cx + 7, cy - 12), (cx + 8, cy - 16),
                   (cx + 9, cy - 20)):
        pygame.draw.circle(surf, _FENGHUANG_BLUE, (nx, ny), 3)
        pygame.draw.circle(surf, _FENGHUANG_TEAL, (nx, ny), 2)
    # 5. Head — small jewel head
    head_x, head_y = cx + 11, cy - 22
    pygame.draw.ellipse(surf, _FENGHUANG_BLUE,
                        pygame.Rect(head_x - 5, head_y - 4, 12, 10))
    pygame.draw.ellipse(surf, _FENGHUANG_TEAL,
                        pygame.Rect(head_x - 4, head_y - 3, 10, 8))
    pygame.draw.ellipse(surf, _FENGHUANG_GOLD,
                        pygame.Rect(head_x - 2, head_y, 4, 3))
    # 6. Long curved beak — gold
    pygame.draw.polygon(surf, _FENGHUANG_GOLD, [
        (head_x + 5, head_y - 2), (head_x + 11, head_y),
        (head_x + 8, head_y + 2), (head_x + 5, head_y)])
    pygame.draw.polygon(surf, _FENGHUANG_RED, [
        (head_x + 5, head_y - 2), (head_x + 11, head_y),
        (head_x + 8, head_y + 2), (head_x + 5, head_y)], 1)
    # 7. Ornate crest — 4 curling feathers flowing back over the neck
    crest_specs = [
        # (start_x, start_y, ctrl_x, ctrl_y, end_x, end_y, color)
        (head_x - 2, head_y - 4, head_x - 4, head_y - 10,
         head_x - 10, head_y - 8, _FENGHUANG_GOLD),
        (head_x,     head_y - 5, head_x - 2, head_y - 13,
         head_x -  8, head_y - 14, _FENGHUANG_RED),
        (head_x + 2, head_y - 4, head_x + 2, head_y - 12,
         head_x -  4, head_y - 16, _FENGHUANG_GOLD),
        (head_x + 4, head_y - 3, head_x + 5, head_y - 10,
         head_x +  1, head_y - 14, _FENGHUANG_PURPLE),
    ]
    for sx, sy, cx_c, cy_c, ex, ey, col in crest_specs:
        # Curved feather drawn as a teardrop polygon
        pygame.draw.polygon(surf, col, [
            (sx, sy), (cx_c - 1, cy_c), (ex, ey),
            (ex + 1, ey + 2), (cx_c + 1, cy_c + 2)])
        # Highlight stripe down the centre
        pygame.draw.line(surf, _FENGHUANG_WHITE, (sx, sy), (ex, ey), 1)
    # 8. Eye
    _draw_small_eye(surf, head_x + 2, head_y - 1, glow=False)
    # 9. Jewel ember sparks (gold + red)
    for ex, ey in ((-40, -20), (-44, 0), (-46, 20), (-34, 40),
                   (16, -22), (20, 14), (-22, 18), (8, 20)):
        col = _FENGHUANG_GOLD if (ex + ey) % 2 == 0 else _FENGHUANG_RED
        pygame.draw.circle(surf, col, (cx + ex, cy + ey), 1)
    return surf


# ────────────────────────────────────────────────────────────────────────────
# Variant 3 — DRAGON PHOENIX (sinuous, flame banners, mane)
# ────────────────────────────────────────────────────────────────────────────

_DRAGON_FLAME = [
    (100, 16, 24), (190,  50, 30), (240, 110, 40),
    (255, 200,  80), (255, 245, 180),
]
_DRAGON_BODY = [
    (90, 18, 22), (190,  50,  40),
    (240, 130,  60), (255, 210, 110),
]


def _build_dragon_wing(angle_deg):
    """Flame BANNER (not a feathered wing) — a tall curved sweep of
    layered flame that reads as a cloak of fire trailing the body."""
    box = 80
    w = pygame.Surface((box, box), pygame.SRCALPHA)
    f = _DRAGON_FLAME
    # Outer crimson sweep — a long curved banner
    pygame.draw.polygon(w, f[0], [
        (40, 50), (38, 40), (32, 28), (24, 16),
        (16,  6), (12, 18), (20, 32), (32, 46), (40, 54),
    ])
    # Orange inner layer
    pygame.draw.polygon(w, f[1], [
        (40, 48), (36, 38), (30, 28), (22, 18),
        (18, 12), (18, 22), (26, 34), (34, 44), (40, 50),
    ])
    # Gold core
    pygame.draw.polygon(w, f[2], [
        (40, 46), (36, 38), (30, 28), (24, 22),
        (24, 26), (30, 34), (36, 42), (40, 48),
    ])
    # Yellow inner streak
    pygame.draw.polygon(w, f[3], [
        (40, 44), (34, 34), (30, 28), (32, 28),
        (38, 36), (40, 46),
    ])
    # White-hot core line
    pygame.draw.line(w, f[4], (38, 44), (28, 24), 2)
    pygame.draw.line(w, f[4], (40, 42), (32, 28), 1)
    return pygame.transform.rotate(w, angle_deg)


def _build_dragon_frame(wing_angle_deg):
    surf = _grand_canvas()
    f = _DRAGON_FLAME
    b = _DRAGON_BODY
    cx, cy = GRAND_CX, GRAND_CY
    # 1. Long wispy tail extending back-left into a comet trail.
    # Each layer narrows to the tip.
    tail_pts_outer = [
        (cx - 4, cy + 8), (cx - 16, cy + 16),
        (cx - 30, cy + 20), (cx - 42, cy + 22),
        (cx - 50, cy + 18), (cx - 44, cy + 12),
        (cx - 30, cy + 6), (cx - 16, cy + 4),
    ]
    pygame.draw.polygon(surf, (10, 5, 12, 130), tail_pts_outer)  # shadow
    pygame.draw.polygon(surf, f[0], tail_pts_outer)
    tail_pts_mid = [
        (cx - 4, cy + 8), (cx - 14, cy + 14),
        (cx - 28, cy + 16), (cx - 40, cy + 18),
        (cx - 44, cy + 14), (cx - 36, cy + 10),
        (cx - 24, cy + 8), (cx - 14, cy + 6),
    ]
    pygame.draw.polygon(surf, f[1], tail_pts_mid)
    tail_pts_inner = [
        (cx - 4, cy + 9), (cx - 12, cy + 12),
        (cx - 24, cy + 14), (cx - 32, cy + 14),
        (cx - 30, cy + 10), (cx - 18, cy + 9),
    ]
    pygame.draw.polygon(surf, f[2], tail_pts_inner)
    # White-hot core line through the tail
    pygame.draw.line(surf, f[4], (cx - 4, cy + 10), (cx - 40, cy + 14), 1)
    # Ember sparks trailing further behind
    for ex, ey in ((-50, 14), (-54, 20), (-58, 16), (-60, 22)):
        pygame.draw.circle(surf, f[3], (cx + ex, cy + ey), 1)
    # 2. S-curve sinuous body — chain of overlapping ellipses.
    body_segs = [
        # (x, y, rx, ry)
        (cx - 8, cy + 6, 10, 8),
        (cx - 2, cy + 2, 11, 9),
        (cx + 4, cy - 4,  9, 8),
        (cx + 9, cy - 11, 7, 7),
        (cx + 13, cy - 18, 6, 5),
    ]
    for x, y, rx, ry in body_segs:
        pygame.draw.ellipse(surf, b[0],
                            pygame.Rect(x - rx, y - ry, rx * 2, ry * 2))
        pygame.draw.ellipse(surf, b[1],
                            pygame.Rect(x - rx + 1, y - ry + 1,
                                        rx * 2 - 2, ry * 2 - 2))
    # Belly highlight along the lower curve
    pygame.draw.ellipse(surf, b[2],
                        pygame.Rect(cx - 12, cy + 8,  10,  4))
    pygame.draw.ellipse(surf, b[2],
                        pygame.Rect(cx -  4, cy + 4,  10,  4))
    pygame.draw.ellipse(surf, b[3],
                        pygame.Rect(cx + 4, cy - 4, 6, 3))
    # 3. Flame banner wings — left + right (via flip)
    wing_right = _build_dragon_wing(wing_angle_deg)
    wing_left  = pygame.transform.flip(wing_right, True, False)
    surf.blit(wing_right, wing_right.get_rect(center=(cx + 14, cy - 18)).topleft)
    surf.blit(wing_left,  wing_left.get_rect(center=(cx - 18, cy - 12)).topleft)
    # 4. Flame mane along the neck — 5 short flame tufts
    for nx, ny, h in ((cx +  5, cy -  3,  8), (cx +  8, cy -  9, 10),
                      (cx + 11, cy - 15,  9), (cx + 14, cy - 22, 8),
                      (cx + 16, cy - 27,  6)):
        pygame.draw.polygon(surf, f[0], [
            (nx - 3, ny), (nx + 3, ny), (nx + 2, ny - h),
        ])
        pygame.draw.polygon(surf, f[2], [
            (nx - 2, ny - 1), (nx + 2, ny - 1), (nx + 1, ny - h + 2),
        ])
        pygame.draw.line(surf, f[4], (nx, ny), (nx + 1, ny - h + 1), 1)
    # 5. Dragon head — small, elongated
    head_x, head_y = cx + 17, cy - 28
    pygame.draw.ellipse(surf, b[0], pygame.Rect(head_x - 5, head_y - 4, 14, 10))
    pygame.draw.ellipse(surf, b[1], pygame.Rect(head_x - 4, head_y - 3, 12, 8))
    pygame.draw.ellipse(surf, b[2], pygame.Rect(head_x - 2, head_y, 4, 3))
    # 6. Two horn-shaped flame plumes on the head
    for fx, fy_top, hw, hh in (
        (head_x - 2, head_y - 14, 2, 10),
        (head_x + 4, head_y - 14, 2, 10),
    ):
        base_y = fy_top + hh
        pygame.draw.polygon(surf, f[0], [
            (fx - hw, base_y), (fx + hw, base_y), (fx + 1, fy_top)])
        # Hot inner stripe — a thin bright line up the centre of the horn
        pygame.draw.line(surf, f[2],
                         (fx, base_y - 1), (fx + 1, fy_top + 2), 1)
    # 7. Long dragon snout
    pygame.draw.polygon(surf, b[0], [
        (head_x + 5, head_y - 1), (head_x + 12, head_y),
        (head_x + 10, head_y + 3), (head_x + 5, head_y + 2),
    ])
    pygame.draw.polygon(surf, (255, 200, 60), [
        (head_x + 10, head_y), (head_x + 13, head_y + 1),
        (head_x + 10, head_y + 2)])
    # 8. Eye — golden glow
    _draw_small_eye(surf, head_x + 3, head_y, glow=True)
    # 9. Ember sparks around the whole creature
    for ex, ey in ((-40, -10), (-30, -20), (-10, -28),
                   (22, -34), (28, -20), (24, 6), (4, 14)):
        pygame.draw.circle(surf, f[3], (cx + ex, cy + ey), 1)
    return surf


# ────────────────────────────────────────────────────────────────────────────
# Variant 4 — COMET PHOENIX (massive flame trail, small bird at the front)
# ────────────────────────────────────────────────────────────────────────────

_COMET_FLAME = [
    (180,  30, 20), (240,  90, 30), (255, 160, 50),
    (255, 220,  80), (255, 250, 220),
]
_COMET_BODY = [
    (120, 28, 30), (220,  60,  40),
    (255, 130,  60), (255, 220, 110),
]


def _build_comet_wing(angle_deg):
    """Tiny streamlined wing — barely visible, swept tight against the
    body. The hero element is the tail, not the wings."""
    box = 36
    w = pygame.Surface((box, box), pygame.SRCALPHA)
    f = _COMET_FLAME
    # Drop shadow
    pygame.draw.polygon(w, (10, 5, 12, 130), [
        (18, 20), (28, 12), (32, 18), (26, 24), (18, 24),
    ])
    pygame.draw.polygon(w, f[0], [
        (18, 18), (28, 10), (30, 16), (24, 22), (18, 22),
    ])
    pygame.draw.polygon(w, f[1], [
        (18, 18), (26, 12), (28, 16), (22, 20),
    ])
    pygame.draw.line(w, f[3], (18, 18), (28, 11), 1)
    pygame.draw.line(w, f[4], (19, 19), (26, 14), 1)
    return pygame.transform.rotate(w, angle_deg)


def _build_comet_frame(wing_angle_deg):
    surf = _grand_canvas()
    f = _COMET_FLAME
    b = _COMET_BODY
    cx, cy = GRAND_CX, GRAND_CY
    # Comet body sits forward (right) — body anchor (cx + 22, cy)
    body_x = cx + 22
    body_y = cy
    # 1. MASSIVE FLAME TRAIL extending back to the left, widest in the
    #    middle and tapering at both ends. Five layers outer → inner.
    # Layer 1 — deepest crimson outer envelope
    pygame.draw.polygon(surf, (10, 5, 12, 130), [
        (body_x - 8, body_y),
        (body_x - 32, body_y - 18), (body_x - 56, body_y - 22),
        (body_x - 72, body_y - 14), (body_x - 80, body_y - 4),
        (body_x - 80, body_y + 4),  (body_x - 72, body_y + 14),
        (body_x - 56, body_y + 22), (body_x - 32, body_y + 18),
    ])
    pygame.draw.polygon(surf, f[0], [
        (body_x - 8, body_y - 2),
        (body_x - 32, body_y - 16), (body_x - 56, body_y - 20),
        (body_x - 70, body_y - 12), (body_x - 78, body_y - 4),
        (body_x - 78, body_y + 4),  (body_x - 70, body_y + 12),
        (body_x - 56, body_y + 20), (body_x - 32, body_y + 16),
    ])
    # Layer 2 — orange mid
    pygame.draw.polygon(surf, f[1], [
        (body_x - 8, body_y),
        (body_x - 28, body_y - 12), (body_x - 50, body_y - 14),
        (body_x - 64, body_y -  8), (body_x - 68, body_y),
        (body_x - 64, body_y +  8), (body_x - 50, body_y + 14),
        (body_x - 28, body_y + 12),
    ])
    # Layer 3 — gold
    pygame.draw.polygon(surf, f[2], [
        (body_x - 8, body_y),
        (body_x - 24, body_y - 8), (body_x - 44, body_y - 10),
        (body_x - 54, body_y -  6), (body_x - 56, body_y),
        (body_x - 54, body_y +  6), (body_x - 44, body_y + 10),
        (body_x - 24, body_y +  8),
    ])
    # Layer 4 — bright yellow inner
    pygame.draw.polygon(surf, f[3], [
        (body_x - 8, body_y),
        (body_x - 20, body_y - 4), (body_x - 36, body_y - 6),
        (body_x - 44, body_y - 2), (body_x - 44, body_y + 2),
        (body_x - 36, body_y + 6), (body_x - 20, body_y + 4),
    ])
    # Layer 5 — white-hot core line through the tail
    pygame.draw.line(surf, f[4], (body_x - 8, body_y),
                     (body_x - 50, body_y), 3)
    pygame.draw.line(surf, f[4], (body_x - 12, body_y - 2),
                     (body_x - 38, body_y - 2), 1)
    pygame.draw.line(surf, f[4], (body_x - 12, body_y + 2),
                     (body_x - 38, body_y + 2), 1)
    # 2. Ember sparks trailing further behind the tail
    for ex, ey in ((-86, -2), (-90, 4), (-94, -6),
                   (-96, 8), (-100, 0)):
        pygame.draw.circle(surf, f[3], (body_x + ex, body_y + ey), 1)
        pygame.draw.circle(surf, f[2], (body_x + ex - 1, body_y + ey + 1), 1)
    # 3. Compact body — small forward-leaning oval
    pygame.draw.ellipse(surf, b[0],
                        pygame.Rect(body_x - 6, body_y - 7, 14, 14))
    pygame.draw.ellipse(surf, b[1],
                        pygame.Rect(body_x - 5, body_y - 6, 12, 12))
    pygame.draw.ellipse(surf, b[2],
                        pygame.Rect(body_x - 3, body_y - 3, 6, 6))
    pygame.draw.ellipse(surf, b[3],
                        pygame.Rect(body_x - 2, body_y + 0, 4, 3))
    # 4. Tucked wings (small, swept back)
    wing_right = _build_comet_wing(wing_angle_deg)
    wing_left  = pygame.transform.flip(wing_right, True, False)
    surf.blit(wing_right, wing_right.get_rect(center=(body_x - 2, body_y - 6)).topleft)
    surf.blit(wing_left,  wing_left.get_rect(center=(body_x - 6, body_y + 4)).topleft)
    # 5. Forward-leaning head
    head_x, head_y = body_x + 8, body_y - 4
    pygame.draw.ellipse(surf, b[0],
                        pygame.Rect(head_x - 4, head_y - 4, 10, 10))
    pygame.draw.ellipse(surf, b[1],
                        pygame.Rect(head_x - 3, head_y - 3,  8,  8))
    pygame.draw.ellipse(surf, b[2],
                        pygame.Rect(head_x - 1, head_y - 1,  4,  3))
    # 6. Forward-pointing beak
    pygame.draw.polygon(surf, (255, 200, 60), [
        (head_x + 4, head_y - 1), (head_x + 9, head_y),
        (head_x + 4, head_y + 2)])
    # 7. Eye with glow
    _draw_small_eye(surf, head_x + 2, head_y, glow=True)
    # 8. Streamlined crown — a single short flame off the head
    pygame.draw.polygon(surf, f[0], [
        (head_x - 1, head_y - 5), (head_x + 3, head_y - 5),
        (head_x - 4, head_y - 11)])
    pygame.draw.polygon(surf, f[2], [
        (head_x, head_y - 5), (head_x + 2, head_y - 5),
        (head_x - 3, head_y - 10)])
    pygame.draw.line(surf, f[4], (head_x + 1, head_y - 5),
                     (head_x - 3, head_y - 10), 1)
    return surf


# ────────────────────────────────────────────────────────────────────────────
# Variant 5 — ROYAL PHOENIX (halo-crown of 9 plumes radiating outward)
# ────────────────────────────────────────────────────────────────────────────

_ROYAL_FLAME = [
    (120, 18, 28), (215,  55, 30), (255, 130, 40),
    (255, 215,  85), (255, 250, 220),
]
_ROYAL_BODY = [
    (110, 25, 30), (210,  55,  40),
    (245, 130,  60), (255, 200, 100),
]


def _build_royal_wing(angle_deg):
    """Mid-size ornate flame wing — half-spread regal pose, three
    feather tiers from crimson through gold."""
    box = 56
    w = pygame.Surface((box, box), pygame.SRCALPHA)
    f = _ROYAL_FLAME
    pygame.draw.polygon(w, (10, 5, 12, 150), [
        (26, 30), (44, 12), (50, 22), (44, 36), (26, 40),
    ])
    pygame.draw.polygon(w, f[0], [
        (26, 28), (42, 10), (48, 22), (42, 34), (26, 38),
    ])
    pygame.draw.polygon(w, f[1], [
        (26, 28), (38, 14), (44, 22), (38, 32), (28, 34),
    ])
    pygame.draw.polygon(w, f[2], [
        (28, 28), (36, 18), (40, 24), (34, 30),
    ])
    pygame.draw.polygon(w, f[3], [
        (30, 28), (34, 22), (36, 26), (32, 28),
    ])
    pygame.draw.line(w, f[4], (28, 28), (40, 12), 1)
    pygame.draw.line(w, f[4], (29, 31), (42, 22), 1)
    # Feather divider strokes
    pygame.draw.line(w, f[0], (28, 30), (42, 14), 1)
    pygame.draw.line(w, f[0], (30, 34), (44, 26), 1)
    return pygame.transform.rotate(w, angle_deg)


def _build_royal_frame(wing_angle_deg):
    surf = _grand_canvas()
    f = _ROYAL_FLAME
    b = _ROYAL_BODY
    cx, cy = GRAND_CX, GRAND_CY
    # 1. Long ornate tail — 3 plumes radiating back
    tail_specs = [
        # (tip_x_off, tip_y_off, hw)
        (-24, 18, 5),   # lower-left longest
        (-26, 28, 4),
        (-22,  6, 4),
    ]
    for tx_off, ty_off, hw in tail_specs:
        tx, ty = cx + tx_off, cy + ty_off
        ox, oy = cx - 4, cy + 8
        # Outer crimson plume
        pygame.draw.polygon(surf, f[0], [
            (ox, oy - hw), (ox, oy + hw), (tx, ty)])
        # Gold mid
        pygame.draw.polygon(surf, f[2], [
            (ox + 2, oy - hw + 1), (ox + 2, oy + hw - 1),
            (tx - 4, ty)])
        # Yellow tip
        pygame.draw.circle(surf, f[3], (tx, ty), max(2, hw - 2))
        pygame.draw.circle(surf, f[4], (tx, ty), 1)
        # Stripe
        pygame.draw.line(surf, f[3], (ox, oy), (tx, ty), 1)
    # 2. Elegant upright body
    pygame.draw.ellipse(surf, b[0],
                        pygame.Rect(cx - 8, cy - 6, 18, 24))
    pygame.draw.ellipse(surf, b[1],
                        pygame.Rect(cx - 7, cy - 5, 16, 22))
    pygame.draw.ellipse(surf, b[2],
                        pygame.Rect(cx - 5, cy - 2, 10, 10))
    pygame.draw.ellipse(surf, b[3],
                        pygame.Rect(cx - 4, cy + 6, 8, 6))
    # 3. Half-spread wings
    wing_right = _build_royal_wing(wing_angle_deg)
    wing_left  = pygame.transform.flip(wing_right, True, False)
    surf.blit(wing_right, wing_right.get_rect(center=(cx + 16, cy - 2)).topleft)
    surf.blit(wing_left,  wing_left.get_rect(center=(cx - 16, cy - 2)).topleft)
    # 4. Forward-facing head
    pygame.draw.ellipse(surf, b[0], pygame.Rect(cx - 6, cy - 22, 14, 14))
    pygame.draw.ellipse(surf, b[1], pygame.Rect(cx - 5, cy - 21, 12, 12))
    pygame.draw.ellipse(surf, b[2], pygame.Rect(cx - 3, cy - 17, 4, 3))
    # 5. Beak
    pygame.draw.polygon(surf, (255, 200, 60), [
        (cx + 6, cy - 17), (cx + 12, cy - 14),
        (cx + 6, cy - 12)])
    pygame.draw.polygon(surf, (140, 90, 20), [
        (cx + 6, cy - 17), (cx + 12, cy - 14),
        (cx + 6, cy - 12)], 1)
    # 6. Gold-glow eye
    _draw_small_eye(surf, cx + 3, cy - 16, glow=True)
    # 7. THE HALO-CROWN — 9 plumes radiating outward from the head
    head_cx, head_cy = cx + 1, cy - 16
    halo_specs = []
    for i in range(9):
        # Spread plumes across a ~280° arc above the head (avoid the chin)
        ang = math.radians(-140 + i * (280 / 8))
        # Vary plume length: top plume longest, sides medium, bottom-outer shortest
        if 3 <= i <= 5:
            length = 22  # top plumes
            hw = 4
        elif 1 <= i <= 6:
            length = 17
            hw = 3
        else:
            length = 12  # outer-bottom
            hw = 2
        halo_specs.append((ang, length, hw))
    for ang, length, hw in halo_specs:
        # Plume runs from the head outward along the angle
        root_x = head_cx + int(math.cos(ang) * 8)
        root_y = head_cy + int(math.sin(ang) * 8)
        tip_x  = head_cx + int(math.cos(ang) * (8 + length))
        tip_y  = head_cy + int(math.sin(ang) * (8 + length))
        # Perpendicular vector for the plume's base width
        perp_x = -math.sin(ang)
        perp_y =  math.cos(ang)
        base_l = (int(root_x + perp_x * hw), int(root_y + perp_y * hw))
        base_r = (int(root_x - perp_x * hw), int(root_y - perp_y * hw))
        # Outer crimson layer
        pygame.draw.polygon(surf, f[0], [base_l, base_r, (tip_x, tip_y)])
        # Gold mid
        mid_w = max(1, hw - 1)
        base_l2 = (int(root_x + perp_x * mid_w + math.cos(ang) * 2),
                   int(root_y + perp_y * mid_w + math.sin(ang) * 2))
        base_r2 = (int(root_x - perp_x * mid_w + math.cos(ang) * 2),
                   int(root_y - perp_y * mid_w + math.sin(ang) * 2))
        pygame.draw.polygon(surf, f[2], [
            base_l2, base_r2,
            (int(tip_x - math.cos(ang) * 2),
             int(tip_y - math.sin(ang) * 2))])
        # White-hot tip dot
        pygame.draw.circle(surf, f[4], (tip_x, tip_y), 1)
    # 8. Bright white halo glow centered on the head
    halo = pygame.Surface((50, 50), pygame.SRCALPHA)
    pygame.draw.circle(halo, (255, 240, 160,  60), (25, 25), 24)
    pygame.draw.circle(halo, (255, 250, 220, 100), (25, 25), 14)
    pygame.draw.circle(halo, (255, 255, 240, 160), (25, 25),  8)
    surf.blit(halo, (head_cx - 25, head_cy - 25),
              special_flags=pygame.BLEND_RGBA_ADD)
    # 9. Body ember sparks
    for ex, ey in ((-30, -12), (-20, -28), (8, -32), (24, -22),
                   (28, 0), (24, 18), (-26, 14), (-32, -2)):
        pygame.draw.circle(surf, f[3], (cx + ex, cy + ey), 1)
    return surf


# ────────────────────────────────────────────────────────────────────────────
# Fire-Fenghuang variants — Imperial fire palette + Fenghuang silhouette
# (slim S-curve body, peacock fan-tail, ornate curling crest).
# Five versions vary tail-fan layout, crest, and wing geometry.
# ────────────────────────────────────────────────────────────────────────────

# Shared Imperial fire palette (re-used from _IMPERIAL_FLAME above).
_FF_FLAME = _IMPERIAL_FLAME       # [crimson, orange, gold, yellow, white-hot]
_FF_BODY  = [
    (115, 22, 28), (215, 60, 38),
    (250, 140, 60), (255, 215, 110),
]


def _build_ff_wing(angle_deg, length: int = 36, layered: int = 3):
    """Compact ornate flame-feather wing for fire-fenghuang variants.
    `length` controls the wing reach; `layered` (3 / 4) controls the
    number of feather tiers."""
    box = max(56, length + 20)
    w = pygame.Surface((box, box), pygame.SRCALPHA)
    f = _FF_FLAME
    cx_, cy_ = box // 2, box // 2
    tip = (cx_ + length // 2 + 4, cy_ - length // 3 - 4)
    # Outer crimson sweep
    pygame.draw.polygon(w, (10, 5, 12, 150), [
        (cx_ - 4, cy_ + 4), (tip[0] + 1, tip[1] + 1),
        (tip[0] + 6, tip[1] + 8), (cx_, cy_ + 12),
    ])
    pygame.draw.polygon(w, f[0], [
        (cx_ - 4, cy_ + 2), tip,
        (tip[0] + 4, tip[1] + 8), (cx_ + 2, cy_ + 10),
    ])
    # Orange
    pygame.draw.polygon(w, f[1], [
        (cx_ - 2, cy_ + 2), (tip[0] - 2, tip[1] + 2),
        (tip[0] + 2, tip[1] + 6), (cx_ + 2, cy_ + 8),
    ])
    # Gold
    pygame.draw.polygon(w, f[2], [
        (cx_, cy_ + 2), (tip[0] - 4, tip[1] + 4),
        (tip[0], tip[1] + 6), (cx_ + 2, cy_ + 6),
    ])
    if layered >= 4:
        # Bright yellow inner accent
        pygame.draw.polygon(w, f[3], [
            (cx_ + 2, cy_ + 3), (tip[0] - 6, tip[1] + 5),
            (tip[0] - 2, tip[1] + 6),
        ])
    # 3 distinct primary feathers off the wingtip
    n_primaries = 3 if layered == 3 else 4
    for k in range(n_primaries):
        t = k / max(1, n_primaries - 1)
        # Distribute primaries radially around the tip
        ang = math.radians(-30 + t * 60)
        plen = length // 2
        p_tip = (tip[0] + int(math.cos(ang) * plen),
                 tip[1] + int(math.sin(ang) * plen))
        pygame.draw.line(w, f[0], tip, p_tip, 2)
        pygame.draw.line(w, f[3], tip, p_tip, 1)
        pygame.draw.circle(w, f[4], p_tip, 1)
    # White-hot leading-edge highlight
    pygame.draw.line(w, f[4], (cx_ - 2, cy_ + 2), tip, 1)
    # Feather divider strokes
    pygame.draw.line(w, f[0],
                     (cx_ - 2, cy_ + 4), (tip[0] - 2, tip[1] + 4), 1)
    return pygame.transform.rotate(w, angle_deg)


def _paint_ff_body_and_neck(surf, cx, cy, neck_shape: str = "s_curve",
                            body_palette=None, friendly_face: bool = False,
                            eye_glow_color=(255, 240, 160, 220)):
    """Common slim phoenix body + S-curve neck + head. `neck_shape`:
      's_curve' — classic fenghuang S
      'upright' — straight vertical neck
      'forward' — neck angled forward (motion-implying)
    `body_palette` lets variants override the molten-gold gradient.
    `friendly_face` enables a bigger sclera + catch-light + softer
    beak so the bird reads as cute rather than predatory.
    Returns (head_x, head_y) for the caller to attach crest + beak."""
    b = body_palette if body_palette is not None else _FF_BODY
    # 1. Slim body (smaller than parrot)
    pygame.draw.ellipse(surf, b[0],
                        pygame.Rect(cx - 7, cy - 4, 18, 22))
    pygame.draw.ellipse(surf, b[1],
                        pygame.Rect(cx - 6, cy - 3, 16, 20))
    pygame.draw.ellipse(surf, b[2],
                        pygame.Rect(cx - 4, cy - 0, 10,  8))
    pygame.draw.ellipse(surf, b[3],
                        pygame.Rect(cx - 3, cy + 6,  8,  6))
    # 2. Neck (chain of small circles)
    if neck_shape == "upright":
        path = [(cx + 2, cy - 4), (cx + 2, cy - 8),
                (cx + 2, cy - 12), (cx + 2, cy - 16),
                (cx + 2, cy - 20)]
    elif neck_shape == "forward":
        path = [(cx + 3, cy - 4), (cx + 6, cy - 8),
                (cx + 9, cy - 12), (cx + 12, cy - 15),
                (cx + 15, cy - 18)]
    else:  # s_curve
        path = [(cx + 3, cy - 4), (cx + 5, cy - 8),
                (cx + 7, cy - 12), (cx + 8, cy - 16),
                (cx + 9, cy - 20)]
    for nx, ny in path:
        pygame.draw.circle(surf, b[0], (nx, ny), 3)
        pygame.draw.circle(surf, b[1], (nx, ny), 2)
    head_x, head_y = path[-1][0], path[-1][1] - 2
    # 3. Head
    pygame.draw.ellipse(surf, b[0],
                        pygame.Rect(head_x - 5, head_y - 4, 12, 10))
    pygame.draw.ellipse(surf, b[1],
                        pygame.Rect(head_x - 4, head_y - 3, 10,  8))
    pygame.draw.ellipse(surf, b[2],
                        pygame.Rect(head_x - 2, head_y - 0,  4,  3))
    # 4. Beak — hooked gold (friendly variant softens the hook into a
    # rounded triangle that reads as cute rather than predatory).
    if friendly_face:
        pygame.draw.polygon(surf, (255, 200, 60), [
            (head_x + 5, head_y - 1), (head_x + 9, head_y + 1),
            (head_x + 5, head_y + 3)])
        pygame.draw.polygon(surf, (180, 120, 30), [
            (head_x + 5, head_y - 1), (head_x + 9, head_y + 1),
            (head_x + 5, head_y + 3)], 1)
    else:
        pygame.draw.polygon(surf, (255, 200, 60), [
            (head_x + 5, head_y - 2), (head_x + 11, head_y),
            (head_x + 7, head_y + 2), (head_x + 5, head_y)])
        pygame.draw.polygon(surf, (140,  90, 20), [
            (head_x + 5, head_y - 2), (head_x + 11, head_y),
            (head_x + 7, head_y + 2), (head_x + 5, head_y)], 1)
    # 5. Eye
    _draw_small_eye(surf, head_x + 2, head_y - 1, glow=True,
                    size=(3 if friendly_face else 2),
                    glow_color=eye_glow_color, friendly=friendly_face)
    return head_x, head_y


def _paint_ff_tail_fan(surf, ox, oy, plume_specs):
    """Paint a fan of fire plumes radiating from (ox, oy).
    `plume_specs` is a list of (angle_deg, length, half_width) tuples."""
    f = _FF_FLAME
    for ang_deg, length, hw in plume_specs:
        ang = math.radians(ang_deg)
        tx = ox + math.cos(ang) * length
        ty = oy + math.sin(ang) * length
        perp_x = -math.sin(ang)
        perp_y =  math.cos(ang)
        base_l = (int(ox + perp_x * hw), int(oy + perp_y * hw))
        base_r = (int(ox - perp_x * hw), int(oy - perp_y * hw))
        tip = (int(tx), int(ty))
        # Drop shadow
        pygame.draw.polygon(surf, (10, 5, 12, 120), [
            (base_l[0] + 1, base_l[1] + 1),
            (base_r[0] + 1, base_r[1] + 1),
            (tip[0] + 1, tip[1] + 1)])
        # Outer crimson layer
        pygame.draw.polygon(surf, f[0], [base_l, base_r, tip])
        # Orange mid
        mid_w = max(1, hw - 1)
        ml = (int(ox + perp_x * mid_w + math.cos(ang) * 2),
              int(oy + perp_y * mid_w + math.sin(ang) * 2))
        mr = (int(ox - perp_x * mid_w + math.cos(ang) * 2),
              int(oy - perp_y * mid_w + math.sin(ang) * 2))
        pygame.draw.polygon(surf, f[1], [ml, mr, tip])
        # Gold inner
        in_w = max(1, hw - 2)
        il = (int(ox + perp_x * in_w + math.cos(ang) * 4),
              int(oy + perp_y * in_w + math.sin(ang) * 4))
        ir = (int(ox - perp_x * in_w + math.cos(ang) * 4),
              int(oy - perp_y * in_w + math.sin(ang) * 4))
        pygame.draw.polygon(surf, f[2], [il, ir, tip])
        # Yellow tip blob
        pygame.draw.circle(surf, f[3], tip, max(2, hw - 1))
        # White-hot tip pinpoint
        pygame.draw.circle(surf, f[4], tip, 1)
        # Stripe down the centre
        pygame.draw.line(surf, f[3], (int(ox), int(oy)), tip, 1)


def _paint_ff_crest(surf, head_x, head_y, style: str,
                    flame_palette=None):
    """Crest of curling flame-tinted feathers above the head.
    `style`: 'curl3', 'tall1+2', 'twin_trail', 'short3', 'grand5'.
    `flame_palette` lets variants tint the crest (e.g. warmer)."""
    f = flame_palette if flame_palette is not None else _FF_FLAME
    # Helper to draw one curling feather as a teardrop polygon + stripe
    def _curl(sx, sy, cx_c, cy_c, ex, ey, hw, color):
        pygame.draw.polygon(surf, color, [
            (sx, sy), (cx_c - hw, cy_c), (ex, ey),
            (ex + hw, ey + hw), (cx_c + hw, cy_c + hw)])
        pygame.draw.line(surf, f[4], (sx, sy), (ex, ey), 1)

    if style == "curl3":
        _curl(head_x - 2, head_y - 4, head_x - 4, head_y - 10,
              head_x -  8, head_y - 8,  1, f[0])
        _curl(head_x,     head_y - 5, head_x - 2, head_y - 13,
              head_x -  6, head_y - 14, 1, f[2])
        _curl(head_x + 2, head_y - 4, head_x + 1, head_y - 11,
              head_x -  3, head_y - 14, 1, f[1])
    elif style == "tall1+2":
        # Single tall central flame plume
        pygame.draw.polygon(surf, f[0], [
            (head_x - 3, head_y - 4),
            (head_x + 3, head_y - 4),
            (head_x, head_y - 22)])
        pygame.draw.polygon(surf, f[2], [
            (head_x - 2, head_y - 5),
            (head_x + 2, head_y - 5),
            (head_x, head_y - 20)])
        pygame.draw.polygon(surf, f[4], [
            (head_x - 1, head_y - 6),
            (head_x + 1, head_y - 6),
            (head_x, head_y - 17)])
        # Two short curling side feathers
        _curl(head_x - 4, head_y - 2, head_x - 6, head_y - 8,
              head_x - 10, head_y - 6, 1, f[2])
        _curl(head_x + 4, head_y - 2, head_x + 6, head_y - 8,
              head_x + 10, head_y - 6, 1, f[2])
    elif style == "twin_trail":
        # Two LONG trailing crest feathers (signature)
        _curl(head_x - 1, head_y - 5, head_x - 6, head_y - 12,
              head_x - 14, head_y - 8, 2, f[0])
        _curl(head_x + 1, head_y - 5, head_x - 2, head_y - 14,
              head_x - 10, head_y - 16, 2, f[2])
    elif style == "short3":
        # 3 short flame nubs swept BACK over the neck (motion implied)
        for ox, oy, length, col in (
            (-1, -4, 8, f[0]), (-3, -3, 6, f[2]), (-5, -1, 5, f[3])
        ):
            sx, sy = head_x + ox, head_y + oy
            tx, ty = sx - length, sy - length // 2
            pygame.draw.polygon(surf, col, [
                (sx, sy), (sx + 1, sy + 2), (tx, ty)])
            pygame.draw.line(surf, f[4], (sx, sy), (tx, ty), 1)
    elif style == "grand5":
        # Central tall flame + 4 curling sides
        pygame.draw.polygon(surf, f[0], [
            (head_x - 3, head_y - 4), (head_x + 3, head_y - 4),
            (head_x, head_y - 24)])
        pygame.draw.polygon(surf, f[2], [
            (head_x - 2, head_y - 5), (head_x + 2, head_y - 5),
            (head_x, head_y - 22)])
        pygame.draw.polygon(surf, f[4], [
            (head_x - 1, head_y - 6), (head_x + 1, head_y - 6),
            (head_x, head_y - 18)])
        _curl(head_x - 3, head_y - 4, head_x - 6, head_y - 10,
              head_x - 11, head_y - 12, 1, f[0])
        _curl(head_x + 3, head_y - 4, head_x + 6, head_y - 10,
              head_x + 11, head_y - 12, 1, f[0])
        _curl(head_x - 4, head_y - 2, head_x - 9, head_y - 4,
              head_x - 14, head_y - 2, 1, f[2])
        _curl(head_x + 4, head_y - 2, head_x + 9, head_y - 4,
              head_x + 14, head_y - 2, 1, f[2])


# ── Fire-Fenghuang variant configs ──────────────────────────────────────

# Each entry: (tail_fan_specs, crest_style, wing_length, wing_layered, neck_shape).
# Tail fan specs anchor at (cx - 8, cy + 4) — same as the original fenghuang.
_FF_VARIANTS = {
    # 1. BLAZE — balanced moderate fan, classic curling crest
    "blaze": dict(
        tail_origin_off=(-8, 4),
        tail_fan=[
            (200, 36, 4),   # back-upper
            (190, 44, 5),   # mid-upper
            (180, 48, 5),   # CENTRE longest
            (170, 44, 5),   # mid-lower
            (160, 38, 4),   # back-lower
            (215, 26, 3),   # top short
        ],
        crest="curl3",
        wing_length=36,
        wing_layered=3,
        neck="s_curve",
    ),
    # 2. SUNBURST — wide radial spread, single tall crown plume
    "sunburst": dict(
        tail_origin_off=(-4, 0),
        tail_fan=[
            (260, 28, 3),   # back-top
            (220, 38, 3),   # upper plumes
            (200, 44, 4),
            (180, 50, 5),   # CENTRE longest
            (160, 44, 4),
            (140, 38, 3),
            (120, 30, 3),   # lower-back
            (100, 24, 2),
            ( 80, 20, 2),   # nearly straight down
        ],
        crest="tall1+2",
        wing_length=40,
        wing_layered=4,
        neck="upright",
    ),
    # 3. TWIN — minimalist 5-plume tail, twin-trail signature crest
    "twin": dict(
        tail_origin_off=(-6, 4),
        tail_fan=[
            (200, 32, 3),
            (185, 42, 4),
            (175, 46, 4),   # CENTRE
            (165, 40, 4),
            (150, 32, 3),
        ],
        crest="twin_trail",
        wing_length=30,
        wing_layered=3,
        neck="s_curve",
    ),
    # 4. SWIFT — all plumes trailing back (motion), swept-back crest
    "swift": dict(
        tail_origin_off=(-4, 2),
        tail_fan=[
            (192, 28, 2),
            (188, 38, 3),
            (184, 46, 4),
            (180, 50, 4),   # straight-back CENTRE longest
            (176, 46, 4),
            (172, 38, 3),
            (168, 28, 2),
        ],
        crest="short3",
        wing_length=38,
        wing_layered=3,
        neck="forward",
    ),
    # 5. GRAND — ornate 9-plume wide fan, elaborate central crown
    "grand": dict(
        tail_origin_off=(-8, 4),
        tail_fan=[
            (230, 30, 3),
            (210, 42, 4),
            (195, 48, 5),
            (180, 54, 5),   # CENTRE longest
            (165, 48, 5),
            (150, 42, 4),
            (130, 32, 3),
            (245, 20, 2),
            (115, 20, 2),
        ],
        crest="grand5",
        wing_length=42,
        wing_layered=4,
        neck="s_curve",
    ),
}


def _build_ff_variant(angle_deg, config: dict):
    """Generic fire-fenghuang frame builder driven by a config dict."""
    surf = _grand_canvas()
    cx, cy = GRAND_CX, GRAND_CY
    f = _FF_FLAME
    # 1. Tail fan — HERO ELEMENT, painted first so the body overlaps it
    ox = cx + config["tail_origin_off"][0]
    oy = cy + config["tail_origin_off"][1]
    _paint_ff_tail_fan(surf, ox, oy, config["tail_fan"])
    # 2. Body + neck + head (returns head anchor for the crest)
    head_x, head_y = _paint_ff_body_and_neck(surf, cx, cy,
                                              neck_shape=config["neck"])
    # 3. Wings (compact ornate, tucked above/beside body)
    wing_right = _build_ff_wing(angle_deg, length=config["wing_length"],
                                layered=config["wing_layered"])
    wing_left  = pygame.transform.flip(wing_right, True, False)
    surf.blit(wing_right,
              wing_right.get_rect(center=(cx + 8, cy - 6)).topleft)
    surf.blit(wing_left,
              wing_left.get_rect(center=(cx - 12, cy - 6)).topleft)
    # 4. Crest
    _paint_ff_crest(surf, head_x, head_y, config["crest"])
    # 5. Ember sparks scattered around the silhouette
    for ex, ey in ((-30, -16), (-38, 0), (-42, 14), (-32, 28),
                   (12, -18), (16, 6), (-20, 18), (22, 16)):
        col = f[3] if (ex + ey) % 2 == 0 else f[2]
        pygame.draw.circle(surf, col, (cx + ex, cy + ey), 1)
    return surf


def _build_blaze_frame(angle):     return _build_ff_variant(angle, _FF_VARIANTS["blaze"])
def _build_sunburst_frame(angle):  return _build_ff_variant(angle, _FF_VARIANTS["sunburst"])
def _build_twin_frame(angle):      return _build_ff_variant(angle, _FF_VARIANTS["twin"])
def _build_swift_frame(angle):     return _build_ff_variant(angle, _FF_VARIANTS["swift"])
def _build_grand_frame(angle):     return _build_ff_variant(angle, _FF_VARIANTS["grand"])


# ────────────────────────────────────────────────────────────────────────────
# Wide-Wing phoenix iterations (Grand-lineage v2)
#
# The original fire-fenghuang variants had radial fan tails which read as
# "turkey." These five iterations fix that: longer wings (the hero element),
# short cascade tails (flowing ribbon-flames trailing down/back, NOT a fan),
# slim Imperial-fire body inherited from `_paint_ff_body_and_neck`.
#
# All five share Ashes-style gameplay via the dispatch in world.py.
# ────────────────────────────────────────────────────────────────────────────


def _paint_cascade_tail(surf, ox, oy, plumes,
                        flame_palette=_FF_FLAME):
    """Paint a phoenix tail as a *cascade* of flowing ribbon-flames
    trailing back / down from (ox, oy). Each plume is a curved teardrop
    polygon, NOT a radial fan slice — width tapers along the length,
    creating the flowing-ribbon read of a phoenix tail.

    `plumes` is a list of (angle_deg, length, base_half_w, curve_strength)
    tuples. `curve_strength` (0.0 = straight, 1.0 = strong curl) bends
    the plume toward gravity so it reads as flowing rather than radiating."""
    f = flame_palette
    for ang_deg, length, hw, curve in plumes:
        ang = math.radians(ang_deg)
        # End point (straight ray)
        ex = ox + math.cos(ang) * length
        ey = oy + math.sin(ang) * length
        # Curve the tip toward downward gravity for the ribbon look
        ex += curve * length * 0.15
        ey += abs(curve) * length * 0.35
        # Mid control point for the curve
        mx = ox + math.cos(ang) * (length * 0.55)
        my = oy + math.sin(ang) * (length * 0.55) + abs(curve) * length * 0.15
        # Perpendicular at root
        perp_x = -math.sin(ang)
        perp_y =  math.cos(ang)
        # Plume edges: wider at root, tapering to the tip
        root_l = (int(ox + perp_x * hw), int(oy + perp_y * hw))
        root_r = (int(ox - perp_x * hw), int(oy - perp_y * hw))
        mid_l  = (int(mx + perp_x * (hw - 0.5)),
                  int(my + perp_y * (hw - 0.5)))
        mid_r  = (int(mx - perp_x * (hw - 0.5)),
                  int(my - perp_y * (hw - 0.5)))
        tip    = (int(ex), int(ey))
        # 6-point teardrop polygon — root_l, mid_l, tip, mid_r, root_r
        outer_poly = [root_l, mid_l, tip, mid_r, root_r]
        # Drop shadow
        shadow_poly = [(p[0] + 1, p[1] + 2) for p in outer_poly]
        pygame.draw.polygon(surf, (10, 5, 12, 130), shadow_poly)
        # Outer crimson layer
        pygame.draw.polygon(surf, f[0], outer_poly)
        # Orange mid layer (one px inset)
        mid_w = max(1, hw - 1)
        mid_root_l = (int(ox + perp_x * mid_w),
                      int(oy + perp_y * mid_w))
        mid_root_r = (int(ox - perp_x * mid_w),
                      int(oy - perp_y * mid_w))
        mid_mid_l  = (int(mx + perp_x * (mid_w - 0.5)),
                      int(my + perp_y * (mid_w - 0.5)))
        mid_mid_r  = (int(mx - perp_x * (mid_w - 0.5)),
                      int(my - perp_y * (mid_w - 0.5)))
        pygame.draw.polygon(surf, f[1],
                            [mid_root_l, mid_mid_l, tip,
                             mid_mid_r, mid_root_r])
        # Gold inner core stripe
        pygame.draw.line(surf, f[2], (int(ox), int(oy)), tip, 2)
        # Bright yellow rachis line
        pygame.draw.line(surf, f[3], (int(ox), int(oy)), tip, 1)
        # White-hot tip pinpoint
        pygame.draw.circle(surf, f[4], tip, 1)


def _draw_primary_feathers(w, tip, count: int, radial_deg: float,
                           fan_deg: float = 50.0, length: int = 14,
                           flame_palette=None,
                           rounded: bool = False):
    """Paint `count` distinct primary feathers radiating from `tip` in a
    fan. `rounded=True` ends each feather in a soft gold circle (less
    spiky), `flame_palette` lets variants brighten the feather tones."""
    f = flame_palette if flame_palette is not None else _FF_FLAME
    for k in range(count):
        t = k / max(1, count - 1)
        ang = math.radians(radial_deg + (t - 0.5) * fan_deg)
        plen = length + int(t * 3)        # outer primaries a touch longer
        ptip = (int(tip[0] + math.cos(ang) * plen),
                int(tip[1] + math.sin(ang) * plen))
        if rounded:
            # Rounder primary: thicker line + filled gold tip circle
            # (no sharp triangle), reads as feather pad not spike.
            pygame.draw.line(w, f[1], tip, ptip, 3)
            pygame.draw.line(w, f[2], tip, ptip, 1)
            pygame.draw.circle(w, f[3], ptip, 2)
            pygame.draw.circle(w, f[4], ptip, 1)
        else:
            # Original sharp-triangle primary
            perp = (-math.sin(ang) * 1.4, math.cos(ang) * 1.4)
            base_l = (int(tip[0] + perp[0]), int(tip[1] + perp[1]))
            base_r = (int(tip[0] - perp[0]), int(tip[1] - perp[1]))
            pygame.draw.polygon(w, f[0], [base_l, base_r, ptip])
            pygame.draw.line(w, f[2], tip, ptip, 1)
            pygame.draw.circle(w, f[4], ptip, 1)


# ── 1. SOAR — horizontal sweep with tips back ──────────────────────────────

def _build_soar_wing(angle_deg):
    """Eagle-glider wing: 56 px long, sweeping outward and slightly back,
    with 6 distinct primary feathers fanned at the tip."""
    box = 84
    w = pygame.Surface((box, box), pygame.SRCALPHA)
    f = _FF_FLAME
    shoulder = (box // 2 - 26, box // 2)
    tip = (box // 2 + 24, box // 2 - 6)
    # Drop shadow silhouette
    pygame.draw.polygon(w, (10, 5, 12, 150), [
        shoulder, (shoulder[0] + 8, shoulder[1] - 12),
        (tip[0] - 4, tip[1] - 2), (tip[0] + 1, tip[1] + 1),
        (tip[0] - 6, tip[1] + 8), (shoulder[0] + 10, shoulder[1] + 8),
    ])
    # Outer crimson layer
    pygame.draw.polygon(w, f[0], [
        shoulder, (shoulder[0] + 8, shoulder[1] - 10),
        tip, (tip[0] - 6, tip[1] + 6), (shoulder[0] + 10, shoulder[1] + 6),
    ])
    # Orange mid
    pygame.draw.polygon(w, f[1], [
        shoulder, (shoulder[0] + 10, shoulder[1] - 7),
        (tip[0] - 4, tip[1] + 1), (tip[0] - 8, tip[1] + 4),
        (shoulder[0] + 12, shoulder[1] + 4),
    ])
    # Gold inner
    pygame.draw.polygon(w, f[2], [
        shoulder, (shoulder[0] + 14, shoulder[1] - 4),
        (tip[0] - 10, tip[1] + 2), (shoulder[0] + 16, shoulder[1] + 2),
    ])
    # Feather divider strokes
    pygame.draw.line(w, f[0], (shoulder[0] + 4, shoulder[1] + 2),
                              (tip[0] - 6, tip[1] + 2), 1)
    pygame.draw.line(w, f[0], (shoulder[0] + 4, shoulder[1] - 1),
                              (tip[0] - 8, tip[1]), 1)
    # White-hot leading-edge highlight
    pygame.draw.line(w, f[4], shoulder, tip, 1)
    # 6 primaries fanned from the tip going back (angles ~150°–210°)
    _draw_primary_feathers(w, tip, count=6, radial_deg=170,
                           fan_deg=80, length=14)
    return pygame.transform.rotate(w, angle_deg)


def _build_soar_frame(angle):
    surf = _grand_canvas()
    cx, cy = GRAND_CX, GRAND_CY
    # Cascade tail — 3 ribbon-flames trailing down-back from the body base
    _paint_cascade_tail(surf, cx - 4, cy + 12, [
        # (angle_deg, length, half_w, curve_strength)
        (200, 30, 4, 0.6),   # upper, gentle down-back curl
        (190, 32, 5, 0.7),   # CENTRE longest, more pronounced curl
        (180, 28, 4, 0.5),
    ])
    # Body + neck + head + crest base
    head_x, head_y = _paint_ff_body_and_neck(surf, cx, cy, neck_shape="s_curve")
    # Wings — horizontal sweep with tips back
    wing_right = _build_soar_wing(angle)
    wing_left  = pygame.transform.flip(wing_right, True, False)
    surf.blit(wing_right, wing_right.get_rect(center=(cx + 28, cy - 4)).topleft)
    surf.blit(wing_left,  wing_left.get_rect(center=(cx - 28, cy - 4)).topleft)
    # 3-plume crest (medium)
    _paint_ff_crest(surf, head_x, head_y, "curl3")
    # Ember sparks
    for ex, ey in ((-44, -8), (-40, 8), (44, -8), (40, 10),
                   (-30, -22), (30, -22), (-20, 26), (20, 24)):
        pygame.draw.circle(surf, _FF_FLAME[3], (cx + ex, cy + ey), 1)
    return surf


# ── 2. RISE — wings raised UP ───────────────────────────────────────────────

def _build_rise_wing(angle_deg):
    """Wing raised upward: 48 px long, swept up and slightly out."""
    box = 72
    w = pygame.Surface((box, box), pygame.SRCALPHA)
    f = _FF_FLAME
    shoulder = (box // 2 - 8, box // 2 + 16)
    tip = (box // 2 + 14, box // 2 - 26)
    # Drop shadow
    pygame.draw.polygon(w, (10, 5, 12, 150), [
        shoulder, (shoulder[0] - 4, shoulder[1] - 6),
        (tip[0] - 6, tip[1] + 2), (tip[0] + 1, tip[1] + 1),
        (tip[0] + 6, tip[1] + 8), (shoulder[0] + 8, shoulder[1] - 4),
    ])
    # Outer crimson — long sweeping curve up
    pygame.draw.polygon(w, f[0], [
        shoulder, (shoulder[0] - 4, shoulder[1] - 8),
        (tip[0] - 6, tip[1]), tip, (tip[0] + 4, tip[1] + 6),
        (shoulder[0] + 8, shoulder[1] - 6),
    ])
    # Orange mid
    pygame.draw.polygon(w, f[1], [
        shoulder, (shoulder[0] - 2, shoulder[1] - 6),
        (tip[0] - 4, tip[1] + 2), (tip[0] + 2, tip[1] + 5),
        (shoulder[0] + 8, shoulder[1] - 4),
    ])
    # Gold inner
    pygame.draw.polygon(w, f[2], [
        shoulder, (shoulder[0], shoulder[1] - 4),
        (tip[0] - 2, tip[1] + 4), (shoulder[0] + 6, shoulder[1] - 2),
    ])
    # White-hot leading edge
    pygame.draw.line(w, f[4], shoulder, tip, 1)
    # 5 primaries fanned UP from the tip (angles ~250°–310°, pointing upward)
    _draw_primary_feathers(w, tip, count=5, radial_deg=280,
                           fan_deg=60, length=13)
    return pygame.transform.rotate(w, angle_deg)


def _build_rise_frame(angle):
    surf = _grand_canvas()
    cx, cy = GRAND_CX, GRAND_CY
    # Single short cascade plume trailing straight back
    _paint_cascade_tail(surf, cx - 4, cy + 10, [
        (185, 24, 4, 0.5),
    ])
    head_x, head_y = _paint_ff_body_and_neck(surf, cx, cy, neck_shape="upright")
    # Wings — raised up + outward
    wing_right = _build_rise_wing(angle)
    wing_left  = pygame.transform.flip(wing_right, True, False)
    surf.blit(wing_right, wing_right.get_rect(center=(cx + 18, cy - 12)).topleft)
    surf.blit(wing_left,  wing_left.get_rect(center=(cx - 18, cy - 12)).topleft)
    # Tall central plume + 2 short sides
    _paint_ff_crest(surf, head_x, head_y, "tall1+2")
    # Ember sparks — concentrated above where the rising wings reach
    for ex, ey in ((-30, -28), (30, -28), (-12, -36), (14, -36),
                   (0, -42), (-40, -10), (40, -10), (0, 24)):
        pygame.draw.circle(surf, _FF_FLAME[3], (cx + ex, cy + ey), 1)
    return surf


# ── 3. STOOP — wings swept BACK along the body ──────────────────────────────

def _build_stoop_wing(angle_deg):
    """Falcon-stoop wing: swept back from shoulder along body. 56 px tucked."""
    box = 76
    w = pygame.Surface((box, box), pygame.SRCALPHA)
    f = _FF_FLAME
    shoulder = (box // 2 + 18, box // 2 - 4)
    tip = (box // 2 - 26, box // 2 + 6)
    # Drop shadow
    pygame.draw.polygon(w, (10, 5, 12, 150), [
        shoulder, (shoulder[0] - 4, shoulder[1] - 8),
        (tip[0] + 4, tip[1] - 1), (tip[0] - 1, tip[1] + 1),
        (tip[0] + 6, tip[1] + 5), (shoulder[0] - 6, shoulder[1] + 8),
    ])
    # Outer crimson — long sweep back along body
    pygame.draw.polygon(w, f[0], [
        shoulder, (shoulder[0] - 6, shoulder[1] - 8),
        tip, (tip[0] + 6, tip[1] + 5), (shoulder[0] - 6, shoulder[1] + 6),
    ])
    # Orange mid
    pygame.draw.polygon(w, f[1], [
        shoulder, (shoulder[0] - 8, shoulder[1] - 4),
        (tip[0] + 6, tip[1]), (tip[0] + 8, tip[1] + 3),
        (shoulder[0] - 6, shoulder[1] + 4),
    ])
    # Gold inner
    pygame.draw.polygon(w, f[2], [
        shoulder, (shoulder[0] - 12, shoulder[1] - 2),
        (tip[0] + 10, tip[1] + 2), (shoulder[0] - 6, shoulder[1] + 2),
    ])
    # White-hot leading edge
    pygame.draw.line(w, f[4], shoulder, tip, 1)
    # 4 primaries streaming back from the tip (angles ~150°–210°)
    _draw_primary_feathers(w, tip, count=4, radial_deg=180,
                           fan_deg=40, length=12)
    return pygame.transform.rotate(w, angle_deg)


def _build_stoop_frame(angle):
    surf = _grand_canvas()
    cx, cy = GRAND_CX, GRAND_CY
    # 3 plumes streaming straight back (no down-curl — motion implied)
    _paint_cascade_tail(surf, cx - 4, cy + 6, [
        (185, 28, 3, 0.1),    # almost-straight upper
        (180, 32, 4, 0.05),   # CENTRE longest, straight back
        (175, 26, 3, 0.1),    # almost-straight lower
    ])
    head_x, head_y = _paint_ff_body_and_neck(surf, cx, cy, neck_shape="forward")
    # Wings — swept back along the body
    wing_right = _build_stoop_wing(angle)
    wing_left  = pygame.transform.flip(wing_right, True, False)
    surf.blit(wing_right, wing_right.get_rect(center=(cx + 4, cy - 4)).topleft)
    surf.blit(wing_left,  wing_left.get_rect(center=(cx - 12, cy + 2)).topleft)
    # Mohawk crest (short flame nubs swept back)
    _paint_ff_crest(surf, head_x, head_y, "short3")
    # Ember sparks trailing back (motion lines)
    for ex, ey in ((-44, 4), (-50, 0), (-46, 12), (-40, -4),
                   (-30, -10), (-30, 16), (-10, -22)):
        pygame.draw.circle(surf, _FF_FLAME[3], (cx + ex, cy + ey), 1)
    return surf


# ── 4. DIVE — wings spread + angled FORWARD ─────────────────────────────────

def _build_dive_wing(angle_deg):
    """Predator-strike wing: swept forward and outward. 50 px reaching forward."""
    box = 76
    w = pygame.Surface((box, box), pygame.SRCALPHA)
    f = _FF_FLAME
    shoulder = (box // 2 - 8, box // 2 - 4)
    tip = (box // 2 + 22, box // 2 + 10)
    # Drop shadow
    pygame.draw.polygon(w, (10, 5, 12, 150), [
        shoulder, (shoulder[0] - 2, shoulder[1] - 6),
        (tip[0] - 2, tip[1] - 5), (tip[0] + 1, tip[1] + 1),
        (tip[0] - 6, tip[1] + 6), (shoulder[0] - 4, shoulder[1] + 8),
    ])
    # Outer crimson sweep — angled forward
    pygame.draw.polygon(w, f[0], [
        shoulder, (shoulder[0] - 2, shoulder[1] - 8),
        (tip[0] - 4, tip[1] - 4), tip,
        (tip[0] - 8, tip[1] + 4), (shoulder[0] - 4, shoulder[1] + 6),
    ])
    pygame.draw.polygon(w, f[1], [
        shoulder, (shoulder[0], shoulder[1] - 5),
        (tip[0] - 4, tip[1] - 2), (tip[0] - 6, tip[1] + 3),
        (shoulder[0], shoulder[1] + 4),
    ])
    pygame.draw.polygon(w, f[2], [
        shoulder, (shoulder[0] + 4, shoulder[1] - 3),
        (tip[0] - 8, tip[1]), (shoulder[0] + 2, shoulder[1] + 3),
    ])
    pygame.draw.line(w, f[4], shoulder, tip, 1)
    # 5 primaries fanned forward (angles ~330°–30°)
    _draw_primary_feathers(w, tip, count=5, radial_deg=10,
                           fan_deg=60, length=13)
    return pygame.transform.rotate(w, angle_deg)


def _build_dive_frame(angle):
    surf = _grand_canvas()
    cx, cy = GRAND_CX, GRAND_CY
    # 3 plumes tucked under and short (out of the wings' way)
    _paint_cascade_tail(surf, cx - 2, cy + 12, [
        (215, 18, 3, 0.4),   # tucked-back upper
        (205, 20, 3, 0.5),
        (195, 18, 3, 0.4),
    ])
    head_x, head_y = _paint_ff_body_and_neck(surf, cx, cy, neck_shape="forward")
    # Wings angled FORWARD
    wing_right = _build_dive_wing(angle)
    wing_left  = pygame.transform.flip(wing_right, True, False)
    surf.blit(wing_right, wing_right.get_rect(center=(cx + 24, cy)).topleft)
    surf.blit(wing_left,  wing_left.get_rect(center=(cx - 24, cy)).topleft)
    # 5-plume elaborate crown
    _paint_ff_crest(surf, head_x, head_y, "grand5")
    # Ember sparks scattered around the strike pose
    for ex, ey in ((-40, 8), (40, 8), (-30, -16), (30, -16),
                   (0, -28), (-20, 22), (20, 22)):
        pygame.draw.circle(surf, _FF_FLAME[3], (cx + ex, cy + ey), 1)
    return surf


# ── 5. ETERNAL — wings in a graceful S-curve, long ribbon-tail ──────────────

def _build_eternal_wing(angle_deg, flame_palette=None,
                        shadow_alpha: int = 150,
                        rounded_tips: bool = False,
                        primary_count: int = 6):
    """The storybook eternal phoenix wing: 60 px long with a graceful
    S-curve — top edge sweeps up then back, bottom edge sweeps down then
    back. Tweakables let less-creepy variants tone down the dark
    shadow, soften primary feather tips, and shift the palette warmer."""
    box = 88
    w = pygame.Surface((box, box), pygame.SRCALPHA)
    f = flame_palette if flame_palette is not None else _FF_FLAME
    shoulder = (box // 2 - 26, box // 2)
    tip = (box // 2 + 26, box // 2 - 4)
    # Drop shadow (alpha tunable — friendly variants halve it)
    pygame.draw.polygon(w, (10, 5, 12, shadow_alpha), [
        shoulder,
        (shoulder[0] + 6, shoulder[1] - 14),
        (shoulder[0] + 22, shoulder[1] - 16),
        (tip[0] - 4, tip[1] - 2),
        (tip[0] + 1, tip[1] + 1),
        (tip[0] - 6, tip[1] + 8),
        (shoulder[0] + 18, shoulder[1] + 10),
        (shoulder[0] + 6, shoulder[1] + 6),
    ])
    # Outer crimson — S-curve top edge
    pygame.draw.polygon(w, f[0], [
        shoulder,
        (shoulder[0] + 6, shoulder[1] - 12),
        (shoulder[0] + 22, shoulder[1] - 14),
        tip,
        (tip[0] - 6, tip[1] + 6),
        (shoulder[0] + 18, shoulder[1] + 8),
        (shoulder[0] + 6, shoulder[1] + 4),
    ])
    # Orange mid
    pygame.draw.polygon(w, f[1], [
        shoulder,
        (shoulder[0] + 8, shoulder[1] - 9),
        (shoulder[0] + 22, shoulder[1] - 10),
        (tip[0] - 4, tip[1] + 1),
        (tip[0] - 8, tip[1] + 4),
        (shoulder[0] + 18, shoulder[1] + 6),
    ])
    # Gold inner
    pygame.draw.polygon(w, f[2], [
        shoulder, (shoulder[0] + 12, shoulder[1] - 5),
        (shoulder[0] + 26, shoulder[1] - 6), (tip[0] - 10, tip[1] + 2),
        (shoulder[0] + 20, shoulder[1] + 4),
    ])
    # Bright yellow inner streak (extra layer, ornate)
    pygame.draw.polygon(w, f[3], [
        shoulder, (shoulder[0] + 16, shoulder[1] - 1),
        (tip[0] - 16, tip[1] + 2), (shoulder[0] + 22, shoulder[1] + 2),
    ])
    # White-hot leading-edge highlight
    pygame.draw.line(w, f[4], shoulder, tip, 1)
    # Feather divider strokes (S-curve hints)
    pygame.draw.line(w, f[0], (shoulder[0] + 6, shoulder[1] - 6),
                              (tip[0] - 8, tip[1] + 1), 1)
    pygame.draw.line(w, f[0], (shoulder[0] + 4, shoulder[1] + 2),
                              (tip[0] - 10, tip[1] + 3), 1)
    # 6 primaries fanned at the tip (broader fan than other variants).
    # Tunable: friendly variants use fewer + rounder tips.
    _draw_primary_feathers(w, tip, count=primary_count, radial_deg=175,
                           fan_deg=85, length=15,
                           flame_palette=f, rounded=rounded_tips)
    return pygame.transform.rotate(w, angle_deg)


def _build_eternal_frame(angle):
    return _build_eternal_variant(angle, _ETERNAL_VARIANTS["eternal"])


# ── Less-creepy Eternal palettes ───────────────────────────────────────────
# The original Eternal reads as creepy because of the dark blood-red outer
# crimson + sharp triangular primaries + heavy drop shadow + cold gold-glow
# eye + 4 long trailing tail ribbons. Each less-creepy palette/config tones
# one or more of those down.

# Warmer — brighter mid-red instead of dark crimson; everything else default.
_FF_FLAME_WARM = [
    (200,  60, 35), (240, 120, 45), (255, 175, 60),
    (255, 225,  95), (255, 248, 200),
]
_FF_BODY_WARM = [
    (180,  80,  45), (235, 120,  55),
    (255, 175,  80), (255, 225, 120),
]

# Dawn — warm yellow/gold/peach dominant, NO dark red. The "daybreak phoenix."
_FF_FLAME_DAWN = [
    (230, 130,  50), (255, 180,  80), (255, 220, 110),
    (255, 245, 170), (255, 252, 230),
]
_FF_BODY_DAWN = [
    (210, 130,  60), (250, 190,  90),
    (255, 225, 130), (255, 248, 200),
]

# Each entry mixes a palette choice with shape softness, tail size, and
# face friendliness so the 5 alternatives sit at different points on the
# "creepy ←→ cute" axis.
_ETERNAL_VARIANTS = {
    # Reference (current shipped Eternal) — kept here for symmetry; the
    # dispatcher routes "eternal" to it for the legacy contact sheets.
    "eternal": dict(
        flame=_FF_FLAME, body=_FF_BODY,
        tail=[(200, 32, 5, 0.8), (190, 36, 5, 0.9),
              (180, 34, 4, 0.7), (170, 28, 4, 0.6)],
        shadow_alpha=150, rounded_tips=False, primary_count=6,
        friendly_face=False,
        eye_glow=(255, 240, 160, 220),
    ),
    # 1. WARM — palette only: lighter, warmer fire; same silhouette.
    "eternal_warm": dict(
        flame=_FF_FLAME_WARM, body=_FF_BODY_WARM,
        tail=[(200, 32, 5, 0.8), (190, 36, 5, 0.9),
              (180, 34, 4, 0.7), (170, 28, 4, 0.6)],
        shadow_alpha=150, rounded_tips=False, primary_count=6,
        friendly_face=False,
        eye_glow=(255, 230, 140, 200),
    ),
    # 2. SOFT — original palette + rounded primary tips + light drop shadow.
    "eternal_soft": dict(
        flame=_FF_FLAME, body=_FF_BODY,
        tail=[(200, 32, 5, 0.8), (190, 36, 5, 0.9),
              (180, 34, 4, 0.7), (170, 28, 4, 0.6)],
        shadow_alpha=70, rounded_tips=True, primary_count=5,
        friendly_face=False,
        eye_glow=(255, 240, 160, 180),
    ),
    # 3. DAWN — much brighter palette; short 3-plume tail; gentler curve.
    "eternal_dawn": dict(
        flame=_FF_FLAME_DAWN, body=_FF_BODY_DAWN,
        tail=[(195, 26, 4, 0.5), (185, 30, 4, 0.6),
              (175, 24, 3, 0.4)],
        shadow_alpha=60, rounded_tips=True, primary_count=5,
        friendly_face=False,
        eye_glow=(255, 250, 200, 160),
    ),
    # 4. FRIEND — original palette + bigger sclera + soft beak + catch-light.
    "eternal_friend": dict(
        flame=_FF_FLAME, body=_FF_BODY,
        tail=[(200, 32, 5, 0.8), (190, 36, 5, 0.9),
              (180, 34, 4, 0.7), (170, 28, 4, 0.6)],
        shadow_alpha=110, rounded_tips=False, primary_count=6,
        friendly_face=True,
        eye_glow=(255, 240, 160, 120),
    ),
    # 5. LITE — everything turned friendly. Warm palette + soft tips +
    # short tail + light shadow + friendly face. The "all-in" cute pick.
    "eternal_lite": dict(
        flame=_FF_FLAME_WARM, body=_FF_BODY_WARM,
        tail=[(195, 26, 4, 0.5), (185, 30, 4, 0.6),
              (175, 24, 3, 0.4)],
        shadow_alpha=60, rounded_tips=True, primary_count=5,
        friendly_face=True,
        eye_glow=(255, 230, 140, 140),
    ),
}


def _build_eternal_variant(angle, cfg):
    surf = _grand_canvas()
    cx, cy = GRAND_CX, GRAND_CY
    # 1. Cascade tail (palette + plume list configurable)
    _paint_cascade_tail(surf, cx - 4, cy + 12,
                         cfg["tail"], flame_palette=cfg["flame"])
    # 2. Body + neck + head + beak + eye
    head_x, head_y = _paint_ff_body_and_neck(
        surf, cx, cy, neck_shape="s_curve",
        body_palette=cfg["body"],
        friendly_face=cfg["friendly_face"],
        eye_glow_color=cfg["eye_glow"])
    # 3. Wings — graceful S-curve, fully spread
    wing_right = _build_eternal_wing(
        angle, flame_palette=cfg["flame"],
        shadow_alpha=cfg["shadow_alpha"],
        rounded_tips=cfg["rounded_tips"],
        primary_count=cfg["primary_count"])
    wing_left  = pygame.transform.flip(wing_right, True, False)
    surf.blit(wing_right, wing_right.get_rect(center=(cx + 30, cy - 4)).topleft)
    surf.blit(wing_left,  wing_left.get_rect(center=(cx - 30, cy - 4)).topleft)
    # 4. 5-feather elaborate crown (palette tinted)
    _paint_ff_crest(surf, head_x, head_y, "grand5",
                    flame_palette=cfg["flame"])
    # 5. Ember sparks — elaborate scatter (palette tinted)
    for ex, ey in ((-46, -6), (46, -6), (-38, -18), (38, -18),
                   (-24, -32), (24, -32), (-32, 22), (32, 22),
                   (-20, 28), (20, 28), (0, -42)):
        pygame.draw.circle(surf, cfg["flame"][3], (cx + ex, cy + ey), 1)
    return surf


def _build_eternal_warm_frame(angle):   return _build_eternal_variant(angle, _ETERNAL_VARIANTS["eternal_warm"])
def _build_eternal_soft_frame(angle):   return _build_eternal_variant(angle, _ETERNAL_VARIANTS["eternal_soft"])
def _build_eternal_dawn_frame(angle):   return _build_eternal_variant(angle, _ETERNAL_VARIANTS["eternal_dawn"])
def _build_eternal_friend_frame(angle): return _build_eternal_variant(angle, _ETERNAL_VARIANTS["eternal_friend"])
def _build_eternal_lite_frame(angle):   return _build_eternal_variant(angle, _ETERNAL_VARIANTS["eternal_lite"])


# Dispatch table the lazy frame-builder reads in `_get_phoenix_frames`.
_GRANDIOSE_BUILDERS = {
    "imperial":  _build_imperial_frame,
    "fenghuang": _build_fenghuang_frame,
    "dragon":    _build_dragon_frame,
    "comet":     _build_comet_frame,
    "royal":     _build_royal_frame,
    # Wide-Wing Grand-lineage v2 (longer wings, short cascade tails)
    "soar":      _build_soar_frame,
    "rise":      _build_rise_frame,
    "stoop":     _build_stoop_frame,
    "dive":      _build_dive_frame,
    "eternal":   _build_eternal_frame,
    # Less-creepy Eternal iterations (palette + softness + face tweaks)
    "eternal_warm":   _build_eternal_warm_frame,
    "eternal_soft":   _build_eternal_soft_frame,
    "eternal_dawn":   _build_eternal_dawn_frame,
    "eternal_friend": _build_eternal_friend_frame,
    "eternal_lite":   _build_eternal_lite_frame,
    # Fire-fenghuang hybrids (imperial palette + fenghuang silhouette)
    "blaze":     _build_blaze_frame,
    "sunburst":  _build_sunburst_frame,
    "twin":      _build_twin_frame,
    "swift":     _build_swift_frame,
    "grand":     _build_grand_frame,
}


def _get_phoenix_frames(variant: str) -> "list[pygame.Surface]":
    frames = _PHOENIX_FRAMES_BY_VARIANT.get(variant)
    if frames is None:
        # Grandiose variants build on a bigger canvas via their own
        # dispatchers; the legacy variants share `_build_phoenix_frame`.
        if variant in _GRANDIOSE_BUILDERS:
            builder = _GRANDIOSE_BUILDERS[variant]
            frames = [_add_outline(builder(a)) for a in _WING_ANGLES]
        else:
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
