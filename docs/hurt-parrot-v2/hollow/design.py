"""
hollow — burnt-out shell hurt-parrot concept (standalone exploration).

Pip after the hit: the bird is a charcoal husk with a dying ember where its
chest used to be. Read-at-a-glance target is a near-black silhouette with one
warm fire inside it, so nothing in the normal macaw palette survives — the
scarlet body, cobalt wing, rainbow tail, gold beak and aviators are all gone
rather than tinted, because a recolour still reads as "the same bird".

Nothing here imports from `game/`; this file only renders a review sheet.
"""
import os
import sys

os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "offscreen"

import pygame

pygame.init()

SPRITE_W, SPRITE_H = 64, 60

# Compressed downward arc — the wing barely lifts any more.
_HURT_ANGLES = (10, -5, -20, -35)

# --- charcoal husk palette (replaces every core parrot colour) ---
BODY        = (28, 10, 10)
BODY_SHADOW = (15,  5,  5)
CHEST_DARK  = (20,  8,  8)
CROWN       = (35, 12, 12)
HEAD_SHADOW = (12,  4,  4)

WING        = (20, 12,  8)
WING_D      = (12,  6,  4)
WING_TIP    = (40, 20, 10)
WING_STRIPE = (55, 28, 12)
WING_HI     = (60, 30, 15)

TAIL_COLORS = ((35, 15, 10), (45, 20, 12), (55, 25, 15), (65, 30, 18))
TAIL_LINE   = (20,  8,  5)

BEAK        = (185, 168, 148)
BEAK_D      = (140, 125, 108)
BEAK_HI     = (210, 195, 175)
FOOT        = (80, 40, 20)

EMBER_OUTER = (175,  58, 18)
EMBER_MID   = (220,  95, 25)
EMBER_CORE  = (255, 165, 50)
EMBER_WHITE = (255, 230, 180)
EYE_EMBER   = (220, 100, 30)
EYE_GLINT   = (255, 220, 150)


def _aaellipse(surf, color, center, rx, ry):
    cx, cy = center
    pygame.draw.ellipse(surf, color, (cx - rx, cy - ry, rx * 2, ry * 2))


def _dim(color, k):
    return tuple(max(0, min(255, int(c * k))) for c in color)


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


def _ember_pulse(wing_angle_deg):
    """Heartbeat phase derived from the wing angle so the ember flares on the
    upstroke and gutters as the wing falls — one signature, not two."""
    lo, hi = min(_HURT_ANGLES), max(_HURT_ANGLES)
    t = (wing_angle_deg - lo) / float(hi - lo) if hi != lo else 1.0
    t = max(0.0, min(1.0, t))
    return 0.76 + 0.24 * t


def _build_wing(angle_deg):
    w = pygame.Surface((50, 50), pygame.SRCALPHA)
    d = pygame.draw
    d.polygon(w, (0, 0, 0, 80),  [(24, 26), (46, 14), (50, 30), (34, 44), (18, 40)])
    d.polygon(w, WING,           [(24, 24), (44, 13), (48, 28), (32, 42), (18, 36)])
    d.polygon(w, WING_D,         [(24, 24), (32, 42), (18, 36)])
    d.polygon(w, WING_TIP,       [(44, 13), (50, 18), (48, 28)])
    d.polygon(w, WING_STRIPE,    [(42, 18), (48, 22), (46, 28), (40, 24)])
    d.line(w, WING_D,    (26, 25), (42, 18), 2)
    d.line(w, WING_D,    (28, 30), (44, 25), 2)
    d.line(w, WING_D,    (30, 34), (46, 32), 2)
    d.line(w, WING_HI,   (25, 25), (41, 15), 1)
    # Burnt bite out of the trailing edge — the husk is damaged, not just dark.
    d.polygon(w, (0, 0, 0, 0), [(33, 41), (37, 37), (39, 42)])
    return pygame.transform.rotate(w, angle_deg)


def _build_hurt_frame(wing_angle_deg):
    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    d    = pygame.draw
    k    = _ember_pulse(wing_angle_deg)

    # --- TAIL (scorched feather fan) ---
    for i, tc in enumerate(TAIL_COLORS):
        d.polygon(surf, tc, [
            (2 + i * 3, 26 + i * 2), (14 + i, 24 + i),
            (20 + i, 30 + i * 2), (6 + i * 3, 36 + i * 2),
        ])
    d.line(surf, TAIL_LINE, (4, 27), (18, 31), 1)
    d.line(surf, TAIL_LINE, (6, 33), (20, 35), 1)

    # --- BODY (hollow husk) ---
    _aaellipse(surf, BODY_SHADOW, (34, 35), 19, 14)
    _aaellipse(surf, BODY,        (32, 32), 19, 14)
    _aaellipse(surf, CHEST_DARK,  (30, 29), 13,  8)

    # Cracks first, so the heat reads as bleeding out from under the shell
    # rather than as a glowing decal painted on top of it.
    crack = _dim((150, 52, 16), k)
    for a, b in (((30, 30), (20, 24)), ((30, 30), (22, 38)),
                 ((30, 30), (41, 24)), ((30, 30), (38, 39))):
        d.line(surf, crack, a, b, 1)

    # --- EMBER CORE ---
    _aaellipse(surf, _dim(EMBER_OUTER, k * 0.86), (32, 32), 13, 8)
    _aaellipse(surf, _dim(EMBER_MID,   k),        (31, 31), 8 if k > 0.95 else 7, 4)
    _aaellipse(surf, _dim(EMBER_CORE,  k),        (30, 30), 3, 2)
    if k > 0.86:
        _aaellipse(surf, EMBER_WHITE, (30, 30), 1, 1)

    # Hard charcoal rim keeps the glow contained inside the husk.
    d.ellipse(surf, (10, 4, 4), (32 - 19, 32 - 14, 38, 28), 2)

    # Ash speckle on the lower shell — cooled crust below the live coal.
    for px, py in ((22, 40), (27, 42), (33, 41), (38, 38), (18, 34), (41, 33)):
        surf.set_at((px, py), (52, 46, 44))

    # --- WING (soot-dark) ---
    wing = _build_wing(wing_angle_deg)
    surf.blit(wing, wing.get_rect(center=(34, 28)).topleft)

    # --- HEAD (charcoal) ---
    _aaellipse(surf, HEAD_SHADOW, (48, 23), 12, 11)
    _aaellipse(surf, BODY,        (47, 21), 12, 11)
    _aaellipse(surf, CHEST_DARK,  (44, 24),  4,  3)
    _aaellipse(surf, CROWN,       (46, 16),  7,  3)

    # --- EMBER EYES (aviators gone) ---
    for ex, ey in ((46, 20), (56, 19)):
        d.circle(surf, _dim((120, 48, 16), k), (ex, ey), 4)
        d.circle(surf, _dim(EYE_EMBER, k),     (ex, ey), 3)
        d.circle(surf, _dim(EYE_GLINT, k),     (ex, ey), 1)

    # --- BEAK (ashen, chipped) ---
    beak_pts = [(55, 21), (61, 24), (58, 28), (52, 26)]
    d.polygon(surf, BEAK,   beak_pts)
    d.polygon(surf, BEAK_D, beak_pts, 1)
    d.line(surf, BEAK_HI, (55, 22), (59, 24), 1)
    d.line(surf, BEAK_D,  (52, 24), (58, 25), 1)
    d.line(surf, (96, 84, 72), (58, 26), (60, 24), 1)

    # --- FEET ---
    d.line(surf, FOOT, (28, 45), (26, 49), 2)
    d.line(surf, FOOT, (34, 45), (36, 49), 2)

    return surf


if __name__ == "__main__":
    OUT_DIR = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(OUT_DIR, exist_ok=True)

    scale  = 4
    frames = [_add_outline(_build_hurt_frame(a)) for a in _HURT_ANGLES]
    fw, fh = frames[0].get_size()
    margin, gap, label_h = 20, 8, 30

    canvas_w = margin + len(frames) * fw * scale + (len(frames) - 1) * gap + margin
    canvas_h = margin + label_h + gap + fh * scale + margin
    canvas   = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((8, 8, 20))

    try:
        font = pygame.font.SysFont("dejavusans", 16)
    except Exception:
        font = pygame.font.Font(None, 16)
    lbl = font.render("hollow — round 1", True, (220, 220, 240))
    canvas.blit(lbl, (margin, margin + (label_h - lbl.get_height()) // 2))

    for i, frame in enumerate(frames):
        px  = margin + i * (fw * scale + gap)
        py  = margin + label_h + gap
        big = pygame.transform.scale(frame, (fw * scale, fh * scale))
        canvas.blit(big, (px, py))

    out_path = os.path.join(OUT_DIR, "round_1.png")
    pygame.image.save(canvas, out_path)
    print(f"Saved {canvas_w}x{canvas_h} -> {out_path}")
