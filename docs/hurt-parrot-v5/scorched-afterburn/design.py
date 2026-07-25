"""
`scorched-afterburn` — hurt-parrot concept exploration (standalone, not wired in).

Elemental damage: the bird came through the fire. This concept owns the *tail*
— no other hurt concept touches it — so the injury is legible from the
silhouette alone, before any surface detail resolves. The three tail feathers
burn back to ~70% length and their tips crumble into a serrated, uneven fan,
which changes the outline in all four wing frames regardless of how the wing
sits.

Everything else is a surface read carried by *value contrast*, not by hue:
soot patches are a warm grey-brown that would vanish against BIRD_RED on its
own, so each one gets a 1-2 px ember rim on its tail-facing edge — the bright
lip is the only part that survives the 1x downscale, and it also tells the
direction the fire came from. Ember orange is rationed to those rims; a mass
of ember-gold on the body would read as a KFC/coin pickup FX rather than
damage.
"""
import math
import os, sys

os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "offscreen"
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()

SPRITE_W, SPRITE_H = 64, 60
_HURT_ANGLES = (10, -5, -20, -35)

# Base macaw palette, mirrored from game/draw.py so this sheet stands alone.
BIRD_RED    = (240,  55,  55)
BIRD_RED_D  = (170,  25,  25)
BIRD_WING   = ( 40, 100, 255)
BIRD_WING_D = ( 20,  55, 180)
BIRD_TIP    = ( 50, 220, 100)
BIRD_BELLY  = (255, 170,  50)
BIRD_BEAK   = (255, 185,   0)
BIRD_BEAK_D = (200, 130,   0)

SHADE_BLACK = ( 15,  15,  25)
SHADE_FRAME = (255, 200,  50)
SHADE_GLINT = (255, 255, 255)
SHADE_TINT  = ( 35,  55,  90)

SOOT       = ( 80,  45,  28)   # warm grey-brown burn centre
SOOT_ASH   = (118,  78,  52)   # lifted ash heart inside a patch
EMBER      = (255, 150,  60)   # 1-2 px leading edge, rear/tail-facing side
EMBER_HOT  = (255, 210, 130)   # single-pixel crackle, always sitting on a rim
CHAR       = ( 58,  36,  28)   # burnt-back tail tips
LID        = ( 40,   8,   8)   # angry squint, matches the brow dark

# The healthy bird's own four-feather fan is kept intact so the only thing that
# changed about the tail is the burn — dropping a feather outright would read as
# a different bird rather than a damaged one.
TAIL_COLORS = ((200,  30,  40), (240,  95,  40), (255, 160,  55), (255, 220,  80))
TAIL_BURN   = 0.30             # fraction of each feather burnt away


def _aaellipse(surf, color, center, rx, ry):
    cx, cy = center
    pygame.draw.ellipse(surf, color, (cx - rx, cy - ry, rx * 2, ry * 2))


def _add_outline(src, outline_color=(20, 12, 18, 220)):
    pad = 2
    w, h = src.get_size()
    mask = pygame.mask.from_surface(src, threshold=8)
    sil  = mask.to_surface(setcolor=outline_color, unsetcolor=(0, 0, 0, 0))
    out  = pygame.Surface((w + pad * 2, h + pad * 2), pygame.SRCALPHA)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == dy == 0:
                continue
            out.blit(sil, (pad + dx, pad + dy))
    out.blit(src, (pad, pad))
    return out


def _lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def _burnt_feather(pts, seed):
    """Return a feather polygon burnt back to ~70% with a serrated tip edge.

    `pts` is the healthy quad in root/tip order (TL, TR, BR, BL); the tip edge
    is the left side, BL->TL. Both tip corners are pulled toward their own root
    corner so the feather shortens along its own axis instead of pivoting, then
    the tip edge is rebuilt as an alternating in/out chain. Serration is baked
    into the polygon rather than punched as transparency because a punched
    notch inside a fan gets covered by the next feather layer, while a jagged
    edge stays in the silhouette.
    """
    tl, tr, br, bl = pts
    tip_t = _lerp(tl, tr, TAIL_BURN)
    tip_b = _lerp(bl, br, TAIL_BURN)

    # Inward = along the feather axis, toward the root; notches bite backwards
    # rather than sideways so they read as crumbled ends, not as a torn side.
    ax, ay = tr[0] - tl[0], tr[1] - tl[1]
    L = max(1e-3, math.hypot(ax, ay))
    ax, ay = ax / L, ay / L

    # Uneven depths beat a uniform comb: an even sawtooth reads as decoration,
    # a ragged one reads as burnt-off material.
    depths = ((0.0, 3.0, 0.0, 2.0, 0.0, 3.5, 0.0)
              if seed % 2 == 0 else
              (0.0, 2.5, 0.0, 3.5, 0.0, 2.0, 0.0))
    edge = []
    n = len(depths)
    for i, dpt in enumerate(depths):
        s = i / (n - 1.0)
        x, y = _lerp(tip_b, tip_t, s)
        edge.append((x + ax * dpt, y + ay * dpt))
    return [*edge, tr, br]


def _draw_tail(surf):
    for i, c in enumerate(TAIL_COLORS):
        pts = [
            (2 + i * 3, 26 + i * 2), (14 + i, 24 + i),
            (20 + i, 30 + i * 2), (6 + i * 3, 36 + i * 2),
        ]
        poly = _burnt_feather(pts, i)
        pygame.draw.polygon(surf, c, poly)
        # Char creeps back from the break. Drawn as a thick outline on the
        # burnt polygon so it hugs every serration instead of needing a second
        # hand-fitted shape per feather.
        pygame.draw.polygon(surf, CHAR, poly[:len(poly) - 2], 2)
    pygame.draw.line(surf, BIRD_RED_D, (7, 27), (18, 31), 1)
    pygame.draw.line(surf, BIRD_RED_D, (9, 33), (20, 35), 1)


def _build_wing(angle_deg):
    w = pygame.Surface((50, 50), pygame.SRCALPHA)
    d = pygame.draw
    d.polygon(w, (0, 0, 0, 110), [(24, 26), (46, 14), (50, 30), (34, 44), (18, 40)])
    d.polygon(w, BIRD_WING,      [(24, 24), (44, 13), (48, 28), (32, 42), (18, 36)])
    d.polygon(w, BIRD_WING_D,    [(24, 24), (32, 42), (18, 36)])
    d.polygon(w, BIRD_TIP,       [(44, 13), (50, 18), (48, 28)])
    d.polygon(w, (255, 200, 60), [(42, 18), (48, 22), (46, 28), (40, 24)])
    d.line(w, BIRD_WING_D,   (26, 25), (42, 18), 2)
    d.line(w, BIRD_WING_D,   (28, 30), (44, 25), 2)
    d.line(w, BIRD_WING_D,   (30, 34), (46, 32), 2)
    d.line(w, (170, 210, 255), (25, 25), (41, 15), 1)
    return pygame.transform.rotate(w, angle_deg)


# Patch outlines, drawn to overrun the body edge on purpose: clipping them to
# the existing silhouette guarantees each burn meets the outline instead of
# floating as an island the outline pass would ring into a blob.
#
# Kept small on purpose. Scaled up to "half the breast" the bird stops reading
# as scarred and starts reading as charred-through and morbid; the damage has
# to lose the value fight against the plumage, not win it.
_SOOT_PATCHES = (
    [(14, 27), (21, 22), (27, 21), (29, 26), (24, 30), (18, 32)],
    [(16, 37), (23, 34), (27, 37), (25, 42), (19, 43), (15, 41)],
    [(34, 20), (40, 20), (42, 24), (37, 26), (33, 24)],
)


def _draw_soot(surf):
    """Burn patches composited over the wing and clipped to the silhouette.

    Under the wing they vanished on the upstroke frames — and fire that caught
    the breast would have caught the coverts on the way past anyway, so
    carrying the soot across the wing is both the truthful read and the only
    one that holds for all four frames.

    The ember rim is made by stamping the same polygon 2 px toward the tail
    first: whatever the soot body does not cover is left as a crescent on the
    rear-facing side, which is where the fire came from.
    """
    layer = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    d = pygame.draw
    for poly in _SOOT_PATCHES:
        rim = [(x - 2, y) for x, y in poly]
        d.polygon(layer, EMBER, rim)
        d.polygon(layer, SOOT, poly)
        # A smaller inner shape keeps the patch from reading as one flat decal.
        # Ash is drawn *lighter* than the burn, not darker: a near-black heart
        # punches a hole in the bird's value structure, while a grey heart
        # ringed by darker char still reads as depth and costs nothing.
        cx = sum(p[0] for p in poly) / len(poly)
        cy = sum(p[1] for p in poly) / len(poly)
        d.polygon(layer, SOOT_ASH,
                  [(cx + (x - cx) * 0.5, cy + (y - cy) * 0.5) for x, y in poly])
        # Crackle sits on the rim itself, never off the body — detached sparks
        # would collide with the game's own particle FX.
        hot = _lerp(rim[0], rim[1], 0.5)
        d.line(layer, EMBER_HOT, (hot[0], hot[1] - 1), (hot[0], hot[1] + 1), 1)

    for x in range(surf.get_width()):
        for y in range(surf.get_height()):
            if layer.get_at((x, y))[3] > 8 and surf.get_at((x, y))[3] > 8:
                surf.set_at((x, y), layer.get_at((x, y)))


def _draw_sunglasses(surf, cx, cy):
    r = 6
    left  = (cx - 4, cy)
    right = (cx + 6, cy - 1)
    d = pygame.draw
    d.circle(surf, SHADE_FRAME, left, r + 1)
    d.circle(surf, SHADE_FRAME, right, r + 1)
    d.circle(surf, SHADE_BLACK, left, r)
    d.circle(surf, SHADE_BLACK, right, r)
    tint = pygame.Surface((r * 2, r), pygame.SRCALPHA)
    d.ellipse(tint, (*SHADE_TINT, 130), tint.get_rect())
    surf.blit(tint, (left[0] - r, left[1] - r + 1))
    surf.blit(tint, (right[0] - r, right[1] - r + 1))
    d.circle(surf, SHADE_GLINT, (right[0] - 2, right[1] - 3), 2)
    d.circle(surf, (255, 255, 255, 200), (right[0] + 2, right[1] + 1), 1)
    d.line(surf, SHADE_FRAME, (left[0] + r, left[1]), (right[0] - r, right[1]), 2)
    d.line(surf, SHADE_FRAME,
           (left[0] - r + 1, left[1] - r + 2), (right[0] + r - 1, right[1] - r + 2), 1)
    return left, r


def _draw_squint(surf, center, r):
    """Heavy lid dropped over the top ~40% of the rear lens.

    Filled rather than stroked: a 3 px arc alone leaves lit lens above it and
    reads as a reflection, while a solid lid subtracts the lens's top edge and
    the whole eye narrows. The lower edge slants down toward the beak, which is
    the universal shorthand for a scowl.
    """
    cx, cy = center
    size = (r + 2) * 2
    lid = pygame.Surface((size, size), pygame.SRCALPHA)
    lc = r + 2
    top = lc - r
    pygame.draw.polygon(lid, LID, [
        (0, top), (size, top),
        (size, top + int(r * 2 * 0.60)), (0, top + int(r * 2 * 0.34)),
    ])
    mask = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (lc, lc), r)
    lid.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(lid, (cx - lc, cy - lc))
    # A lash line one value up keeps the lid from merging with the black lens.
    pygame.draw.line(surf, (90, 22, 18),
                     (cx - r + 1, cy - r + int(r * 2 * 0.34) - 1),
                     (cx + r - 1, cy - r + int(r * 2 * 0.57) - 1), 1)


def _build_hurt_frame(wing_angle_deg):
    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    d = pygame.draw

    _draw_tail(surf)

    _aaellipse(surf, (120, 20, 25),   (34, 35), 19, 14)
    _aaellipse(surf, BIRD_RED,        (32, 32), 19, 14)
    _aaellipse(surf, (255, 100, 100), (30, 29), 13,  8)
    _aaellipse(surf, BIRD_BELLY,      (28, 38), 12,  6)
    sheen = pygame.Surface((28, 6), pygame.SRCALPHA)
    d.ellipse(sheen, (255, 230, 230, 160), sheen.get_rect())
    surf.blit(sheen, (22, 21))

    wing = _build_wing(wing_angle_deg)
    surf.blit(wing, wing.get_rect(center=(34, 28)).topleft)

    _draw_soot(surf)

    _aaellipse(surf, (150, 15, 20),   (48, 23), 12, 11)
    _aaellipse(surf, BIRD_RED,        (47, 21), 12, 11)
    _aaellipse(surf, (255, 130, 130), (44, 24),  4,  3)
    _aaellipse(surf, (255, 170, 170), (46, 16),  7,  3)

    left, r = _draw_sunglasses(surf, 50, 20)
    _draw_squint(surf, left, r)

    beak = [(55, 21), (61, 24), (58, 28), (52, 26)]
    d.polygon(surf, BIRD_BEAK, beak)
    d.polygon(surf, BIRD_BEAK_D, beak, 1)
    d.line(surf, (255, 230, 150), (55, 22), (59, 24), 1)
    d.line(surf, BIRD_BEAK_D, (52, 24), (58, 25), 1)

    d.line(surf, BIRD_BEAK_D, (28, 45), (26, 49), 2)
    d.line(surf, BIRD_BEAK_D, (34, 45), (36, 49), 2)

    return surf


def build_frames():
    return [_add_outline(_build_hurt_frame(a)) for a in _HURT_ANGLES]


def _count(frame, pred, x0=0):
    n = 0
    for x in range(x0, frame.get_width()):
        for y in range(frame.get_height()):
            r, g, b, a = frame.get_at((x, y))
            if a > 8 and pred(r, g, b):
                n += 1
    return n


def _tail_extent(frame):
    for x in range(frame.get_width()):
        for y in range(20, 52):
            if frame.get_at((x, y))[3] > 8:
                return x
    return frame.get_width()


if __name__ == "__main__":
    OUT_DIR = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(OUT_DIR, exist_ok=True)

    raw    = [_build_hurt_frame(a) for a in _HURT_ANGLES]
    frames = [_add_outline(f) for f in raw]

    # x >= 24 keeps the ember probe off the tail and the orange belly, both of
    # which sit inside a naive R/G threshold.
    for i, f in enumerate(raw):
        soot  = _count(f, lambda r, g, b: r < 120 and g < 80 and b < 90, 12)
        ember = _count(f, lambda r, g, b: r > 200 and 100 < g < 180, 24)
        print(f"frame {i}: soot={soot} (need >=20)  ember_rim={ember} "
              f"(need >=8)  tail_leftmost_x={_tail_extent(f)} (healthy=2)")

    NIGHT = (8, 8, 20)
    fw, fh = frames[0].get_size()
    strip = pygame.Surface((fw * len(frames), fh))
    strip.fill(NIGHT)
    for i, f in enumerate(frames):
        strip.blit(f, (i * fw, 0))

    out_path = os.path.join(OUT_DIR, "round_1.png")
    pygame.image.save(strip, out_path)
    print(f"Saved {strip.get_width()}x{strip.get_height()} -> {out_path}")
