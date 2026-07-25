"""
gaunt — emaciation hurt-parrot concept (standalone exploration).

Pip after the hit reads as *structurally* damaged rather than recoloured: the
body ellipses collapse to 62%, the head droops off a bared neck, ribs show
through the belly and the wing thins down to a bone. The empty canvas the
shrunken silhouette leaves behind is the point — a tinted bird still looks
healthy, a smaller one does not.

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

# --- starved palette: same hues as the healthy macaw, drained of energy ---
BODY        = (190,  42,  42)
BODY_SHADOW = (108,  18,  22)
CHEST       = (230,  90,  90)
BELLY       = (210, 140,  40)
HEAD_SHADOW = (135,  13,  18)
CHEEK       = (230, 148, 148)
CROWN       = (230, 160, 160)

NECK_DARK   = ( 55,  12,  12)
NECK_LIT    = ( 75,  18,  18)
SOCKET      = ( 42,   8,   8)
RIB         = ( 70,  12,  12)
RIB_LOW     = ( 65,  10,  10)

TAIL_COLORS = ((165, 22, 32), (190, 78, 28), (210, 128, 42), (228, 192, 68))
TAIL_LINE   = (120, 18,  24)

BEAK        = (210, 152,   0)
BEAK_D      = (165, 108,   0)
FOOT        = (190, 130,   0)

SHADE_FRAME = (200, 155,  35)
SHADE_LENS  = ( 15,  15,  25)
SHADE_GLINT = (230, 230, 240)


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


def _build_wing(angle_deg):
    """Skeletal wing — the healthy plan pulled 60% toward its own shoulder so
    the span shortens without changing the feather layout, plus an exposed
    bone ridge where the leading-edge highlight used to catch the light."""
    def _s(px, py, cx=24, cy=24, f=0.6):
        return (int(cx + (px - cx) * f), int(cy + (py - cy) * f))

    WING   = ( 30,  70, 180, 180)
    WING_D = ( 15,  40, 130, 160)
    TIP    = ( 70, 150,  60)
    STRIPE = (180, 140,  35)
    HL     = (130, 175, 235)
    BONE   = (210, 195, 162)

    w = pygame.Surface((50, 50), pygame.SRCALPHA)
    d = pygame.draw

    d.polygon(w, (0, 0, 0, 80),
              [_s(*p) for p in ((24, 26), (46, 14), (50, 30), (34, 44), (18, 40))])
    d.polygon(w, WING,
              [_s(*p) for p in ((24, 24), (44, 13), (48, 28), (32, 42), (18, 36))])
    d.polygon(w, WING_D,
              [_s(*p) for p in ((24, 24), (32, 42), (18, 36))])
    d.polygon(w, TIP,
              [_s(*p) for p in ((44, 13), (50, 18), (48, 28))])
    d.polygon(w, STRIPE,
              [_s(*p) for p in ((42, 18), (48, 22), (46, 28), (40, 24))])

    # 1-px dividers: at this span 2-px lines would swallow the whole feather.
    d.line(w, WING_D, _s(26, 25), _s(42, 18), 1)
    d.line(w, WING_D, _s(28, 30), _s(44, 25), 1)
    d.line(w, WING_D, _s(30, 34), _s(46, 32), 1)
    d.line(w, HL,     _s(25, 25), _s(41, 15), 1)

    # Bone stays 2-px: it has to out-read every feather line on the wing.
    d.line(w, BONE,   _s(24, 24), _s(42, 14), 2)

    return pygame.transform.rotate(w, angle_deg)


def _build_hurt_frame(wing_angle_deg):
    frame_map = {10: 0, -5: 1, -20: 2, -35: 3}
    fidx      = frame_map.get(int(round(wing_angle_deg)), 0)
    # The head sags one more pixel per frame, so the flap cycle itself reads as
    # the bird losing the fight rather than as a neutral loop.
    dy = fidx

    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    d    = pygame.draw

    # --- TAIL (full-length fan, drained colour) ---
    # Geometry is untouched: against the collapsed body the unchanged tail is
    # what makes the shrinkage legible.
    for i, c in enumerate(TAIL_COLORS):
        d.polygon(surf, c, [
            (2 + i * 3, 26 + i * 2), (14 + i, 24 + i),
            (20 + i, 30 + i * 2), (6 + i * 3, 36 + i * 2),
        ])
    d.line(surf, TAIL_LINE, (4, 27), (18, 31), 1)
    d.line(surf, TAIL_LINE, (6, 33), (20, 35), 1)

    # --- EYE SOCKETS (under the head, so only the hollow rim survives) ---
    _aaellipse(surf, SOCKET, (45, 24 + dy), 9, 8)
    _aaellipse(surf, SOCKET, (55, 23 + dy), 8, 7)

    # --- NECK (bared by the shrunken body and the dropped head) ---
    _aaellipse(surf, NECK_DARK, (44, 32), 4, 7)
    _aaellipse(surf, NECK_LIT,  (43, 31), 3, 5)

    # --- BODY (every radius at 62%, centre dropped 2 px) ---
    _aaellipse(surf, BODY_SHADOW, (34, 37), 12, 9)
    _aaellipse(surf, BODY,        (32, 34), 12, 9)
    _aaellipse(surf, CHEST,       (30, 31),  8, 5)
    _aaellipse(surf, BELLY,       (28, 40),  7, 4)

    # --- RIBS ---
    # Drawn on their own layer and min-blended against a body-shaped stencil:
    # the lower ribs are wider than what is left of the belly, and unclipped
    # they would float free below the silhouette. Spacing is a flat 3 px so the
    # four bands read as a ribcage rhythm instead of as stray scratches.
    ribs = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    _aaellipse(ribs, RIB,     (30, 33), 8, 1)
    _aaellipse(ribs, RIB,     (30, 36), 7, 1)
    _aaellipse(ribs, RIB,     (29, 39), 6, 1)
    _aaellipse(ribs, RIB_LOW, (28, 42), 5, 1)
    stencil = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    _aaellipse(stencil, (255, 255, 255, 255), (32, 34), 12, 9)
    ribs.blit(stencil, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(ribs, (0, 0))

    # --- WING ---
    # Shoulder rides 2 px lower than on the healthy bird to stay seated on the
    # collapsed back instead of hovering above it.
    wing = _build_wing(wing_angle_deg)
    surf.blit(wing, wing.get_rect(center=(34, 30)).topleft)

    # --- HEAD (shrunk, drooping) ---
    _aaellipse(surf, HEAD_SHADOW, (47, 26 + dy), 10, 9)
    _aaellipse(surf, BODY,        (46, 24 + dy), 10, 9)
    _aaellipse(surf, CHEEK,       (43, 27 + dy),  3, 2)
    _aaellipse(surf, CROWN,       (45, 18 + dy),  6, 2)

    # --- AVIATORS (dulled gold, sunk into the sockets) ---
    left  = (45, 24 + dy)
    right = (54, 23 + dy)
    for lens in (left, right):
        d.circle(surf, SHADE_FRAME, lens, 5)
        d.circle(surf, SHADE_LENS,  lens, 4)
        d.circle(surf, SHADE_GLINT, (lens[0] - 2, lens[1] - 2), 1)
    d.line(surf, SHADE_FRAME, (left[0] + 4, left[1]), (right[0] - 4, right[1]), 1)

    # --- BEAK (shorter, no sheen) ---
    beak_pts = [(54, 22 + dy), (59, 25 + dy), (57, 28 + dy), (52, 27 + dy)]
    d.polygon(surf, BEAK,   beak_pts)
    d.polygon(surf, BEAK_D, beak_pts, 1)

    # --- FEET ---
    # Toes keep their healthy reach while the legs now start higher up the
    # smaller body, so they read as spindly rather than as detached strokes.
    d.line(surf, FOOT, (28, 42), (26, 49), 2)
    d.line(surf, FOOT, (34, 42), (36, 49), 2)

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
    lbl = font.render("gaunt — round 1", True, (220, 220, 240))
    canvas.blit(lbl, (margin, margin + (label_h - lbl.get_height()) // 2))

    for i, frame in enumerate(frames):
        canvas.blit(pygame.transform.scale(frame, (fw * scale, fh * scale)),
                    (margin + i * (fw * scale + gap), margin + label_h + gap))

    pygame.image.save(canvas, os.path.join(OUT_DIR, "round_1.png"))
    print(f"Saved {canvas_w}x{canvas_h}")
