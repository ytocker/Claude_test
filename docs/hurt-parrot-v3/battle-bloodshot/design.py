"""
`battle-bloodshot` — hurt-parrot concept exploration (standalone, not wired in).

V3 of the bloodshot line. The V2 read was medical-crisis: bare bloodshot eyes,
a jaw hanging six pixels open, purple haemorrhage. That crossed from "hurt" into
"dying", and it threw away the aviators — the single strongest piece of Pip's
identity. This version keeps the shades on and tells the story as an injury
sustained in a fight rather than a body failing: fresh claw-scratches raked
across the breast, a taped bandage over the brow, and one lens starred with
cracks under a drooping lid. Battle-worn, still Pip, still readable at 1x.
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

SHADE_BLACK = (15, 15, 25)
SHADE_GLINT = (255, 255, 255)
SHADE_TINT  = (35, 55, 90)
# Tarnished rather than the healthy bird's bright gold — the frame took the same
# beating the lens did.
SHADE_FRAME = (220, 175, 40)


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
    WING   = (30,  70, 180)
    WING_D = (18,  42, 125)
    TIP    = (50, 200,  95)
    STRIPE = (210, 175,  50)
    HL     = (130, 175, 240)
    w = pygame.Surface((50, 50), pygame.SRCALPHA)
    d = pygame.draw
    d.polygon(w, (0,0,0,100), [(24,26),(46,14),(50,30),(34,44),(18,40)])
    d.polygon(w, WING,        [(24,24),(44,13),(48,28),(32,42),(18,36)])
    d.polygon(w, WING_D,      [(24,24),(32,42),(18,36)])
    d.polygon(w, TIP,         [(44,13),(50,18),(48,28)])
    d.polygon(w, STRIPE,      [(42,18),(48,22),(46,28),(40,24)])
    d.line(w, WING_D,         (26,25),(42,18), 2)
    d.line(w, WING_D,         (28,30),(44,25), 2)
    d.line(w, WING_D,         (30,34),(46,32), 2)
    d.line(w, HL,             (25,25),(41,15), 1)
    # A chunk torn out of the primaries, punched as transparency rather than
    # painted dark so the break survives the outline pass and the 1x downscale.
    d.polygon(w, (0,0,0,0),   [(43,12),(51,17),(47,23),(44,17)])
    return pygame.transform.rotate(w, angle_deg)


def _draw_scratches(surf):
    """Three raked claw-marks across the breast. Each is a dark cut with a pale
    lip drawn one pixel off-normal: the value pair is what makes it read as a
    torn ridge of feather rather than a flat drawn-on stripe, and it survives
    the downscale where a single dark line just dissolves into the plumage."""
    SCRATCH_D  = (100, 10, 10)
    SCRATCH_HL = (230, 110, 90)
    cuts = (
        ((22, 29), (36, 23)),
        ((23, 33), (37, 27)),
        ((24, 37), (38, 31)),
    )
    for (x0, y0), (x1, y1) in cuts:
        dx, dy = x1 - x0, y1 - y0
        L = max(1e-3, math.hypot(dx, dy))
        # Unit normal, rounded to whole pixels so the highlight stays a crisp
        # neighbour line instead of an antialiased smear.
        ox, oy = round(-dy / L), round(dx / L)
        pygame.draw.line(surf, SCRATCH_D, (x0, y0), (x1, y1), 1)
        pygame.draw.line(surf, SCRATCH_HL,
                         (x0 + ox, y0 + oy), (x1 + ox, y1 + oy), 1)


def _draw_bandage(surf):
    """Taped gauze across the brow. The red cross is the one piece of universal
    shorthand in the whole sprite — a player parses "patched up" from it before
    they have resolved anything else on the head."""
    GAUZE  = (240, 240, 230)
    STITCH = (180, 170, 160)
    CROSS  = (210, 30, 30)
    pygame.draw.rect(surf, GAUZE, pygame.Rect(38, 14, 17, 5))
    pygame.draw.line(surf, STITCH, (38, 14), (54, 14), 1)
    pygame.draw.line(surf, STITCH, (38, 18), (54, 18), 1)
    pygame.draw.rect(surf, CROSS, pygame.Rect(43, 15, 6, 2))
    pygame.draw.rect(surf, CROSS, pygame.Rect(45, 13, 2, 6))


def _draw_sunglasses(surf, cx, cy):
    """Aviator shades: two teardrop lenses joined by a gold bridge, with a tiny
    gold nose pad and a white sunlight glint on each lens. Carried over from the
    healthy build unchanged so the hurt bird is unmistakably the same bird."""
    r_outer = 6
    left  = (cx - 4, cy)
    right = (cx + 6, cy - 1)

    pygame.draw.circle(surf, SHADE_FRAME, left, r_outer + 1)
    pygame.draw.circle(surf, SHADE_FRAME, right, r_outer + 1)
    pygame.draw.circle(surf, SHADE_BLACK, left, r_outer)
    pygame.draw.circle(surf, SHADE_BLACK, right, r_outer)
    tint = pygame.Surface((r_outer * 2, r_outer), pygame.SRCALPHA)
    pygame.draw.ellipse(tint, (*SHADE_TINT, 130), tint.get_rect())
    surf.blit(tint, (left[0] - r_outer, left[1] - r_outer + 1))
    surf.blit(tint, (right[0] - r_outer, right[1] - r_outer + 1))
    pygame.draw.circle(surf, SHADE_GLINT, (left[0] - 2, left[1] - 2), 2)
    pygame.draw.circle(surf, SHADE_GLINT, (right[0] - 2, right[1] - 3), 2)
    pygame.draw.circle(surf, (255, 255, 255, 200), (left[0] + 2, left[1] + 2), 1)
    pygame.draw.circle(surf, (255, 255, 255, 200), (right[0] + 2, right[1] + 1), 1)
    pygame.draw.line(surf, SHADE_FRAME, (left[0] + r_outer, left[1]),
                     (right[0] - r_outer, right[1]), 2)
    pygame.draw.line(surf, SHADE_FRAME,
                     (left[0] - r_outer + 1, left[1] - r_outer + 2),
                     (right[0] + r_outer - 1, right[1] - r_outer + 2), 1)


def _draw_cracked_lens(surf):
    """Star fracture radiating from the middle of the near lens. Near-black on
    black is deliberate: the crack should catch the eye as a texture break at
    2x, not read as a bright drawn X at 1x where it would look like a cartoon
    dead-eye cross."""
    CRACK = (12, 5, 5)
    for end in ((41, 16), (52, 16), (40, 25), (50, 25)):
        pygame.draw.line(surf, CRACK, (46, 20), end, 1)


def _draw_droopy_lid(surf):
    """Half-mast eyelid hanging over the cracked lens. Translucent so the lens
    still reads as glass underneath — an opaque red bar would look like the
    shades had been painted over."""
    lid = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    pygame.draw.polygon(lid, (180, 35, 35),
                        [(40, 14), (52, 14), (52, 18), (40, 18)])
    lid.set_alpha(140)
    surf.blit(lid, (0, 0))


def _tail_feather(pts, damaged=False):
    """Tail feathers run root-right, tip-left. A damaged one is snapped short
    and kicked off-axis so the fan's clean outline breaks — silhouette damage
    survives the 1x downscale where any painted-on detail would not."""
    if not damaged:
        return pts
    root = ((pts[1][0] + pts[2][0]) / 2.0, (pts[1][1] + pts[2][1]) / 2.0)
    a = math.radians(12)
    ca, sa = math.cos(a), math.sin(a)
    out = []
    for i, (x, y) in enumerate(pts):
        if i in (0, 3):
            dx, dy = root[0] - x, root[1] - y
            L = max(1e-3, math.hypot(dx, dy))
            x, y = x + dx / L * 8.0, y + dy / L * 8.0
        vx, vy = x - root[0], y - root[1]
        out.append((root[0] + vx * ca - vy * sa, root[1] + vx * sa + vy * ca))
    return out


def _build_hurt_frame(wing_angle_deg):
    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    d = pygame.draw

    BODY    = (205, 28, 28)
    BODY_SH = (130, 12, 12)
    CHEST   = (160, 22, 22)
    BELLY   = (195, 120, 30)
    BEAK    = (235, 168, 0)
    BEAK_LO = (205, 138, 0)
    BEAK_D  = (140,  92, 0)

    # Tail — same fan construction as the healthy bird, dropped a value step so
    # it no longer out-saturates the head where the acting happens.
    for i, c in enumerate(((180, 25, 35), (190, 70, 30),
                           (210, 130, 40), (230, 195, 65))):
        pts = [
            (2 + i * 3, 26 + i * 2), (14 + i, 24 + i),
            (20 + i, 30 + i * 2), (6 + i * 3, 36 + i * 2),
        ]
        d.polygon(surf, c, _tail_feather(pts, damaged=(i == 1)))
    d.line(surf, BODY_SH, (4, 27), (18, 31), 1)
    d.line(surf, BODY_SH, (6, 33), (20, 35), 1)

    _aaellipse(surf, BODY_SH, (34, 35), 19, 14)
    _aaellipse(surf, BODY,    (32, 32), 19, 14)
    _aaellipse(surf, CHEST,   (30, 29), 13,  8)
    _aaellipse(surf, BELLY,   (28, 38), 12,  6)

    # Sheen kept, but dulled to a matte film — healthy gloss would fight the
    # whole premise.
    sheen = pygame.Surface((28, 6), pygame.SRCALPHA)
    d.ellipse(sheen, (205, 150, 150, 70), sheen.get_rect())
    surf.blit(sheen, (22, 21))

    _draw_scratches(surf)

    wing = _build_wing(wing_angle_deg)
    surf.blit(wing, wing.get_rect(center=(34, 28)).topleft)

    # Head hangs 1 px lower than the healthy build — small in absolute terms,
    # but it breaks the proud upward line of the original silhouette.
    _aaellipse(surf, (155, 15, 20), (48, 24), 12, 11)
    _aaellipse(surf, BODY,          (47, 22), 12, 11)
    _aaellipse(surf, (150, 40, 45), (40, 27),  4,  3)
    _aaellipse(surf, (175, 60, 60), (46, 17),  7,  3)

    _draw_bandage(surf)
    _draw_sunglasses(surf, 50, 20)
    _draw_cracked_lens(surf)
    _draw_droopy_lid(surf)

    # Beak parted only 2 px. Enough to read as a winded, open-mouthed pant; a
    # wider gape tips over into the dying-bird register V2 got stuck in.
    upper = [(55, 21), (61, 24), (58, 26), (52, 25)]
    lower = [(52, 28), (58, 29), (60, 31), (54, 33)]
    d.line(surf, BEAK_D, (52, 27), (59, 28), 1)
    d.polygon(surf, BEAK,    upper)
    d.polygon(surf, BEAK_D,  upper, 1)
    d.polygon(surf, BEAK_LO, lower)
    d.polygon(surf, BEAK_D,  lower, 1)
    d.line(surf, (255, 220, 100), (55, 22), (59, 24), 1)

    d.line(surf, BEAK_D, (28, 45), (26, 49), 2)
    d.line(surf, BEAK_D, (34, 45), (36, 49), 2)

    return surf


if __name__ == "__main__":
    OUT_DIR = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(OUT_DIR, exist_ok=True)

    raw    = [_build_hurt_frame(a) for a in _HURT_ANGLES]
    frames = [_add_outline(f) for f in raw]
    fw, fh = frames[0].get_size()

    scale, margin, gap, label_h = 4, 20, 8, 28
    strip_w  = len(frames) * fw * scale + (len(frames) - 1) * gap
    small_h  = fh * 2
    canvas_w = margin * 2 + strip_w
    canvas_h = margin * 2 + fh * scale + gap + small_h + gap + label_h
    canvas   = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((8, 8, 20))

    for i, frame in enumerate(frames):
        canvas.blit(pygame.transform.scale(frame, (fw * scale, fh * scale)),
                    (margin + i * (fw * scale + gap), margin))

    # In-game scale reference: 2x and 1x side by side, because every decision
    # above is only worth anything if it still reads at the size it ships at.
    y = margin + fh * scale + gap
    x = margin
    for frame in frames:
        canvas.blit(pygame.transform.scale(frame, (fw * 2, fh * 2)), (x, y))
        x += fw * 2 + gap
    x += gap * 2
    for frame in frames:
        canvas.blit(frame, (x, y + (small_h - fh) // 2))
        x += fw + gap

    try:
        font = pygame.font.SysFont("dejavusans", 16)
    except Exception:
        font = pygame.font.Font(None, 16)
    lbl = font.render("battle-bloodshot — round 1  (4x / 2x / 1x)",
                      True, (220, 220, 240))
    canvas.blit(lbl, (margin, canvas_h - margin - label_h +
                      (label_h - lbl.get_height()) // 2))

    out_path = os.path.join(OUT_DIR, "round_1.png")
    pygame.image.save(canvas, out_path)
    print(f"Saved {canvas_w}x{canvas_h} -> {out_path}")

    red = gauze = hl = 0
    for f in raw:
        for x in range(SPRITE_W):
            for y in range(SPRITE_H):
                r, g, b, a = f.get_at((x, y))
                if a < 8:
                    continue
                if r > 150 and g < 100:
                    red += 1
                if r > 220 and g > 220 and b > 200:
                    gauze += 1
                if r > 200 and g > 80 and b < 100:
                    hl += 1
    print(f"bird-red={red} (need >800)  bandage={gauze} (need >30)  "
          f"scratch-highlight={hl} (need >20)")
