"""
fractured — shatter hurt-parrot concept (standalone exploration).

Pip after the hit reads as a pane of glass that took a rock: one impact point
on the body throws a hard geometric crack network across the whole silhouette,
body plates slip out of register along the cracks, and a shard of the wing tip
is simply gone. The macaw palette survives (only ~15% darker, so the crack
network has something bright to cut against) because the damage language here
is structural, not a recolour — you read "broken", not "different bird".

The web is radials PLUS chords between neighbouring radials: real shatter
patterns are spiderwebs, and the chords are what turn a set of lines into
readable shards. Everything is clipped to the sprite silhouette so cracks
never trail off into empty sky at gameplay size.

Nothing here imports from `game/`; this file only renders a review sheet.
"""
import math
import os

os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "offscreen"

import pygame

pygame.init()

SPRITE_W, SPRITE_H = 64, 60

# Compressed downward arc — the wing barely lifts any more.
_HURT_ANGLES = (10, -5, -20, -35)

# --- bruised macaw palette (base colours pulled ~15% down) ---
BODY        = (195,  38,  38)
BODY_SHADOW = (140,  18,  18)
CHEST       = (240,  85,  85)
BELLY       = (240, 155,  42)
HEAD_SHADOW = (145,  15,  20)
CHEEK       = (245, 125, 125)
CROWN       = (245, 162, 162)

WING        = ( 40, 100, 255)
WING_D      = ( 20,  55, 180)
WING_TIP    = ( 50, 220, 100)
WING_STRIPE = (255, 200,  60)
WING_HI     = (170, 210, 255)

TAIL_COLORS = ((195, 30, 38), (230, 90, 38), (250, 152, 50), (255, 218, 78))
TAIL_LINE   = (145, 18, 18)

BEAK        = (255, 185,   0)
BEAK_D      = (200, 130,   0)

SHADE_FRAME = (255, 200,  50)
SHADE_LENS  = ( 15,  15,  25)
SHADE_TINT  = ( 35,  55,  90, 130)
GLINT       = (255, 255, 255)

CRACK_CORE  = ( 10,   4,   4)
CRACK_THIN  = ( 12,   5,   5)
CRACK_GAP   = (  8,   5,   5)

# The crack glow pulses frame-to-frame so the damage looks live rather than
# painted on — the wing angle is the only frame identity this build has.
_FRAME_OF_ANGLE = {10: 0, -5: 1, -20: 2, -35: 3}
_GLOW_BY_FRAME  = ((255, 145, 25), (255, 165, 40), (255, 130, 15), (255, 155, 30))

IMPACT = (36, 28)
# Ordered around the impact so neighbouring radials can be chorded into shards.
_RADIALS = ((18, 12), (52, 10), (60, 32), (48, 50), (20, 48), (10, 30))


def _aaellipse(surf, color, center, rx, ry):
    cx, cy = center
    pygame.draw.ellipse(surf, color, (cx - rx, cy - ry, rx * 2, ry * 2))


def _add_outline(src, outline_color=(20, 12, 18, 220)):
    """1-px dark keyline so the bird still separates from sunset stone."""
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


def _lerp_pt(p1, p2, t):
    return (p1[0] + (p2[0] - p1[0]) * t, p1[1] + (p2[1] - p1[1]) * t)


def _draw_fracture(surf, p1, p2, glow, core_w=3, glow_w=1):
    """Crack = black core with a hot rim on both flanks, so it reads as a
    split in the surface rather than an ink line drawn on top of it."""
    x1, y1 = p1
    x2, y2 = p2
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy)
    if length < 1:
        return
    nx, ny = -dy / length, dx / length
    for sign in (1, -1):
        a = (round(x1 + nx * sign), round(y1 + ny * sign))
        b = (round(x2 + nx * sign), round(y2 + ny * sign))
        pygame.draw.line(surf, glow, a, b, glow_w)
    pygame.draw.line(surf, CRACK_CORE, (round(x1), round(y1)),
                     (round(x2), round(y2)), core_w)


def _displace_shard(surf, rect, offset):
    """Slide a plate of the sprite off its seam and leave a dark void behind.

    The void is stamped from the plate's own alpha, not as a filled rect, so
    the gap can never bleed outside the silhouette."""
    region = pygame.Rect(rect).clip(surf.get_rect())
    if region.width < 1 or region.height < 1:
        return
    piece = surf.subsurface(region).copy()
    mask  = pygame.mask.from_surface(piece, threshold=8)
    if mask.count() == 0:
        return
    void = mask.to_surface(setcolor=CRACK_GAP, unsetcolor=(0, 0, 0, 0))
    surf.blit(void, region.topleft)
    surf.blit(piece, (region.x + offset[0], region.y + offset[1]))


def _build_wing(angle_deg):
    w = pygame.Surface((50, 50), pygame.SRCALPHA)
    d = pygame.draw
    d.polygon(w, (0, 0, 0, 110), [(24, 26), (46, 14), (50, 30), (34, 44), (18, 40)])
    d.polygon(w, WING,           [(24, 24), (44, 13), (48, 28), (32, 42), (18, 36)])
    d.polygon(w, WING_D,         [(24, 24), (32, 42), (18, 36)])
    d.polygon(w, WING_TIP,       [(44, 13), (50, 18), (48, 28)])
    d.polygon(w, WING_STRIPE,    [(42, 18), (48, 22), (46, 28), (40, 24)])
    d.line(w, WING_D, (26, 25), (42, 18), 2)
    d.line(w, WING_D, (28, 30), (44, 25), 2)
    d.line(w, WING_D, (30, 34), (46, 32), 2)
    d.line(w, WING_HI, (25, 25), (41, 15), 1)

    # A primary is missing outright — punched clean out along crack angles.
    # pygame.draw writes RGBA verbatim, so a zero-alpha polygon erases.
    d.polygon(w, (0, 0, 0, 0), [(45, 12), (52, 20), (47, 29), (43, 22)])
    # Torn edges either side of the void.
    d.line(w, CRACK_CORE, (45, 12), (43, 22), 1)
    d.line(w, CRACK_CORE, (47, 29), (43, 22), 1)

    return pygame.transform.rotate(w, angle_deg)


def _draw_lens_web(surf, center, glow):
    """Fracture web confined to the left lens — clipped to the glass circle
    so the cracks stop dead at the gold rim like real spidered glass."""
    r = 6
    web = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
    c   = (r + 1, r + 1)
    spokes = ((-6, -6), (6, -6), (-6, 6), (6, 6), (-2, 7))
    for dx, dy in spokes:
        tip = (c[0] + dx, c[1] + dy)
        pygame.draw.line(web, (10, 5, 5), c, tip, 1)
        pygame.draw.line(web, (255, 200, 80), (c[0] + 1, c[1]), (tip[0] + 1, tip[1]), 1)
    # Chord ties turn the spokes into glass shards rather than a starburst.
    pygame.draw.lines(web, (10, 5, 5), False,
                      [(c[0] - 3, c[1] - 3), (c[0] + 3, c[1] - 3), (c[0] + 3, c[1] + 3)], 1)

    hole = pygame.Surface(web.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(hole, (255, 255, 255, 255), c, r)
    web.blit(hole, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(web, (center[0] - c[0], center[1] - c[1]))

    pygame.draw.circle(surf, glow, center, 2)
    pygame.draw.circle(surf, GLINT, center, 1)


def _build_hurt_frame(wing_angle_deg):
    fidx = _FRAME_OF_ANGLE.get(int(round(wing_angle_deg)), 0)
    glow = _GLOW_BY_FRAME[fidx]

    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    d    = pygame.draw

    # --- tail: outer feathers knocked out of the fan ---
    tail_pts = (
        [(2, 21), (14, 24), (20, 30), (7, 32)],
        [(5, 28), (15, 25), (21, 32), (9, 38)],
        [(8, 30), (16, 26), (22, 34), (12, 40)],
        [(12, 38), (17, 26), (22, 36), (17, 46)],
    )
    for pts, tc in zip(tail_pts, TAIL_COLORS):
        d.polygon(surf, tc, pts)
    d.line(surf, TAIL_LINE, (4, 27), (18, 31), 1)
    d.line(surf, TAIL_LINE, (6, 33), (20, 35), 1)

    # --- body ---
    _aaellipse(surf, BODY_SHADOW, (34, 35), 19, 14)
    _aaellipse(surf, BODY,        (32, 32), 19, 14)
    _aaellipse(surf, CHEST,       (30, 29), 13, 8)
    _aaellipse(surf, BELLY,       (28, 38), 12, 6)

    # --- wing ---
    wing = _build_wing(wing_angle_deg)
    surf.blit(wing, wing.get_rect(center=(34, 28)).topleft)

    # --- head ---
    _aaellipse(surf, HEAD_SHADOW, (48, 23), 12, 11)
    _aaellipse(surf, BODY,        (47, 21), 12, 11)
    _aaellipse(surf, CHEEK,       (44, 24), 4, 3)
    _aaellipse(surf, CROWN,       (46, 16), 7, 3)

    # --- aviators ---
    left, right = (46, 20), (56, 19)
    for pos in (left, right):
        d.circle(surf, SHADE_FRAME, pos, 7)
        d.circle(surf, SHADE_LENS, pos, 6)
    tint = pygame.Surface((12, 6), pygame.SRCALPHA)
    d.ellipse(tint, SHADE_TINT, tint.get_rect())
    for pos in (left, right):
        surf.blit(tint, (pos[0] - 6, pos[1] - 5))
    d.circle(surf, GLINT, (right[0] - 2, right[1] - 2), 2)
    d.line(surf, SHADE_FRAME, (52, 20), (50, 19), 2)
    d.line(surf, SHADE_FRAME, (41, 14), (63, 14), 1)
    _draw_lens_web(surf, left, glow)

    # --- beak ---
    beak_pts = [(55, 21), (61, 24), (58, 28), (52, 26)]
    d.polygon(surf, BEAK, beak_pts)
    d.polygon(surf, BEAK_D, beak_pts, 1)
    d.line(surf, (255, 230, 150), (55, 22), (59, 24), 1)
    d.line(surf, BEAK_D, (52, 24), (58, 25), 1)

    # --- feet ---
    d.line(surf, BEAK_D, (28, 45), (26, 49), 2)
    d.line(surf, BEAK_D, (34, 45), (36, 49), 2)

    # --- plates slipping out of register along the seams ---
    _displace_shard(surf, (18, 14, 12, 10), (3, -2))
    _displace_shard(surf, (40, 32, 10, 8), (-2, 3))
    _displace_shard(surf, (40, 16, 9, 9), (4, 2))

    # --- fracture network, masked to the silhouette and drawn over all of it ---
    frac = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    for tip in _RADIALS:
        _draw_fracture(frac, IMPACT, tip, glow)

    # Chords between neighbouring radials — these are what close the web into
    # shards; without them the radials read as scratches, not shattered glass.
    for i, tip in enumerate(_RADIALS):
        nxt = _RADIALS[(i + 1) % len(_RADIALS)]
        _draw_fracture(frac, _lerp_pt(IMPACT, tip, 0.45),
                       _lerp_pt(IMPACT, nxt, 0.45), glow, core_w=2)
        if i % 2 == 0:
            _draw_fracture(frac, _lerp_pt(IMPACT, tip, 0.82),
                           _lerp_pt(IMPACT, nxt, 0.82), glow, core_w=1)

    for a, b in (((27, 20), (22, 15)), ((27, 20), (20, 25)),
                 ((48, 30), (52, 24)), ((48, 30), (55, 36)),
                 ((28, 38), (24, 42)), ((28, 38), (32, 44))):
        pygame.draw.line(frac, CRACK_THIN, a, b, 1)

    keep = pygame.mask.from_surface(surf, threshold=8).to_surface(
        setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0))
    frac.blit(keep, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(frac, (0, 0))

    # Impact crater sits above the mask so the hit point always reads.
    d.circle(surf, CRACK_CORE, IMPACT, 3)
    d.circle(surf, glow, IMPACT, 2)
    d.circle(surf, (255, 245, 225), IMPACT, 1)

    return surf


if __name__ == "__main__":
    OUT_DIR = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(OUT_DIR, exist_ok=True)

    scale  = 4
    frames = [_add_outline(_build_hurt_frame(a)) for a in _HURT_ANGLES]
    fw, fh = frames[0].get_size()
    margin, gap, label_h = 20, 8, 30

    canvas_w = margin + len(frames) * fw * scale + (len(frames) - 1) * gap + margin
    canvas_h = (margin + label_h + gap + fh * scale + gap * 3
                + label_h + fh * 2 + margin)
    canvas   = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((8, 8, 20))

    try:
        font = pygame.font.SysFont("dejavusans", 16)
        small = pygame.font.SysFont("dejavusans", 12)
    except Exception:
        font = pygame.font.Font(None, 16)
        small = pygame.font.Font(None, 12)
    lbl = font.render("fractured — round 1", True, (220, 220, 240))
    canvas.blit(lbl, (margin, margin + (label_h - lbl.get_height()) // 2))

    y = margin + label_h + gap
    for i, frame in enumerate(frames):
        px = margin + i * (fw * scale + gap)
        canvas.blit(pygame.transform.scale(frame, (fw * scale, fh * scale)), (px, y))

    # Gameplay-size band: the crack web has to survive at 2x and at 1x.
    y += fh * scale + gap * 3
    cap = small.render("2x  /  1x  (in-game size)", True, (150, 150, 175))
    canvas.blit(cap, (margin, y))
    y += label_h - 6
    x = margin
    for s in (2, 1):
        for frame in frames:
            canvas.blit(pygame.transform.scale(frame, (fw * s, fh * s)),
                        (x, y + (fh * 2 - fh * s) // 2))
            x += fw * s + gap
        x += gap * 3

    out_path = os.path.join(OUT_DIR, "round_1.png")
    pygame.image.save(canvas, out_path)
    print(f"Saved {canvas_w}x{canvas_h} -> {out_path}")
