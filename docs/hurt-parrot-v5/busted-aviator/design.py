"""
`busted-aviator` — hurt-parrot concept exploration (standalone, not wired in).

The shades took the hit. Pip's damage is told almost entirely through the one
accessory every player already reads as *his* — the aviators. The left lens is
simply gone: a bare gold rim over an empty socket, one squinting lid inside it.
The right lens is untouched, tinted and glinting exactly as in the healthy
sprite. That pairing is the whole story, and it is a pure shape read: a solid
disc next to a hollow ring survives the 1x downscale where painted-on texture
does not.

Reference note: real glasses almost never shatter in place — the frame warps and
a lens pops out. Drawing the loss rather than a crack is both the truthful read
and the cheaper silhouette.

One body beat only: the beak is split into a partial gape with a dark interior
showing through, so the hit lands physically and not just cosmetically. No
bandages, no soot, no torn feathers, no floating shards — every extra zone
competes with the ring/disc contrast that carries the concept.
"""
import os, sys
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "offscreen"
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()

SPRITE_W, SPRITE_H = 64, 60
_HURT_ANGLES = (10, -5, -20, -35)

BIRD_RED    = (240,  55,  55)
BIRD_RED_D  = (170,  25,  30)
BIRD_WING   = ( 40, 100, 255)
BIRD_WING_D = ( 22,  60, 175)
BIRD_TIP    = ( 50, 220, 100)
BIRD_BELLY  = (255, 170,  50)
BIRD_BEAK   = (255, 185,   0)
BIRD_BEAK_D = (170, 120,   0)

SHADE_BLACK = ( 15,  15,  25)
SHADE_FRAME = (255, 200,  50)
SHADE_GLINT = (255, 255, 255)
SHADE_TINT  = ( 35,  55,  90)

# The empty rim is filled with a near-black recess rather than punched to
# transparency: a real hole would let `_add_outline` draw a dark halo *inside*
# the ring and would break the silhouette. Kept a touch violet and a touch
# lighter than SHADE_BLACK so the socket reads as depth, not as a second lens.
SOCKET      = ( 25,  18,  30)
# Warm pale lid, borrowed from the macaw's bare facial-skin family — the only
# light value inside the socket, so it is what the eye finds there at 1x.
LID         = (235, 200, 195)
GAPE        = ( 15,  10,  10)

# Left ring rides 2 px above its healthy position and the frame axis reads ~8deg
# off level. A bigger kick starts to look like a drawing mistake rather than a
# knock; 8deg is enough asymmetry to notice and still parse as a worn object.
LEFT_C  = (46, 18)
RIGHT_C = (56, 19)
RIM_R   = 7
HOLLOW_R = 5


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
    """Untouched from the healthy bird — this concept spends its whole damage
    budget on the shades, so the wing must stay canonical for the contrast to
    land."""
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


def _draw_busted_shades(surf):
    """Aviators with the left lens knocked clean out.

    Draw order matters. The brow bar goes down first and the rims stamp over it,
    so the bar only ever supplies structural connection — at 10 px lens spacing
    the two rims overlap and a bar drawn on top would either be invisible or
    would streak gold across the empty socket. The tilt is therefore carried by
    the rim positions plus the temple stub, which is the one piece of frame that
    lives outside both lens interiors and so stays readable.
    """
    d = pygame.draw

    d.line(surf, SHADE_FRAME, (39, 19), (62, 16), 2)

    # Right: fully intact, canonical geometry. Any softening here would cost the
    # concept its whole contrast.
    d.circle(surf, SHADE_FRAME, RIGHT_C, RIM_R)
    d.circle(surf, SHADE_BLACK, RIGHT_C, RIM_R - 1)
    tint = pygame.Surface(((RIM_R - 1) * 2, RIM_R - 1), pygame.SRCALPHA)
    d.ellipse(tint, (*SHADE_TINT, 130), tint.get_rect())
    surf.blit(tint, (RIGHT_C[0] - RIM_R + 1, RIGHT_C[1] - RIM_R + 2))
    d.circle(surf, SHADE_GLINT, (RIGHT_C[0] - 2, RIGHT_C[1] - 3), 2)
    d.circle(surf, (255, 255, 255, 200), (RIGHT_C[0] + 2, RIGHT_C[1] + 1), 1)

    # Left: 2 px gold annulus over a recessed socket. The rim is deliberately
    # thicker than the right lens's 1 px rim — a hollow ring needs the extra
    # pixel to survive the downscale, and the weight difference reads as the
    # bare frame edge you'd actually see with the glass gone. Stamped after the
    # right lens because at 10 px spacing the two rims overlap: putting the
    # broken side in front keeps its ring unbroken, which is the read the whole
    # concept rests on.
    d.circle(surf, SHADE_FRAME, LEFT_C, RIM_R)
    d.circle(surf, SOCKET,      LEFT_C, HOLLOW_R)

    # Temple arm swinging back toward the ear, drawn last because it clears both
    # lens interiors. Its angle is the frame's angle, so this stub is what
    # actually sells "knocked askew" at gameplay size.
    d.line(surf, SHADE_FRAME, (40, 19), (35, 20), 2)

    # The single squinting lid. One 2 px arc, endpoints landing on the rim so the
    # lid is continuous with the frame — nothing floats, and there is no eye
    # anatomy behind it to turn to mush at 1x.
    d.arc(surf, LID,
          (LEFT_C[0] - HOLLOW_R, LEFT_C[1] - HOLLOW_R + 1,
           HOLLOW_R * 2, HOLLOW_R + 3),
          0.35, 2.79, 2)


def _build_hurt_frame(wing_angle_deg):
    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    d = pygame.draw

    for i, c in enumerate(((200, 30, 40), (240, 95, 40),
                           (255, 160, 55), (255, 220, 80))):
        d.polygon(surf, c, [
            (2 + i * 3, 26 + i * 2), (14 + i, 24 + i),
            (20 + i, 30 + i * 2), (6 + i * 3, 36 + i * 2),
        ])
    d.line(surf, BIRD_RED_D, (4, 27), (18, 31), 1)
    d.line(surf, BIRD_RED_D, (6, 33), (20, 35), 1)

    _aaellipse(surf, (120, 20, 25),   (34, 35), 19, 14)
    _aaellipse(surf, BIRD_RED,        (32, 32), 19, 14)
    _aaellipse(surf, (255, 100, 100), (30, 29), 13,  8)
    _aaellipse(surf, BIRD_BELLY,      (28, 38), 12,  6)

    sheen = pygame.Surface((28, 6), pygame.SRCALPHA)
    d.ellipse(sheen, (255, 230, 230, 160), sheen.get_rect())
    surf.blit(sheen, (22, 21))

    wing = _build_wing(wing_angle_deg)
    surf.blit(wing, wing.get_rect(center=(34, 28)).topleft)

    _aaellipse(surf, (150, 15, 20),   (48, 23), 12, 11)
    _aaellipse(surf, BIRD_RED,        (47, 21), 12, 11)
    _aaellipse(surf, (255, 130, 130), (44, 24),  4,  3)
    _aaellipse(surf, (255, 170, 170), (46, 16),  7,  3)

    _draw_busted_shades(surf)

    # Beak split into a partial gape. The dark wedge is laid down first and the
    # two mandibles stamp over it, so the interior shows only as the 3 px sliver
    # between them — a gap that widens with the jaws rather than a painted line.
    # The lower mandible's root stays well inside the head ellipse, so the drop
    # can never orphan it into a detached island.
    upper = [(55, 21), (61, 24), (58, 26), (52, 25)]
    lower = [(52, 28), (58, 29), (59, 32), (54, 32)]
    d.polygon(surf, GAPE,        [(52, 25), (59, 26), (59, 31), (53, 31)])
    d.polygon(surf, BIRD_BEAK,   upper)
    d.polygon(surf, BIRD_BEAK_D, upper, 1)
    d.polygon(surf, BIRD_BEAK,   lower)
    d.polygon(surf, BIRD_BEAK_D, lower, 1)
    d.line(surf, (255, 230, 150), (55, 22), (59, 24), 1)

    d.line(surf, BIRD_BEAK_D, (28, 45), (26, 49), 2)
    d.line(surf, BIRD_BEAK_D, (34, 45), (36, 49), 2)

    return surf


def _count_in_disc(frame, color, center, radius, tol=0):
    cx, cy = center
    n = 0
    for x in range(max(0, cx - radius), min(SPRITE_W, cx + radius + 1)):
        for y in range(max(0, cy - radius), min(SPRITE_H, cy + radius + 1)):
            if (x - cx) ** 2 + (y - cy) ** 2 > radius * radius:
                continue
            r, g, b, a = frame.get_at((x, y))
            if a <= 8:
                continue
            if (abs(r - color[0]) <= tol and abs(g - color[1]) <= tol
                    and abs(b - color[2]) <= tol):
                n += 1
    return n


def _islands(frame):
    """Number of 8-connected alpha blobs. Anything above 1 means a floating
    fragment, which the outline pass would ring in dark and make look like dirt."""
    seen = set()
    blobs = 0
    for sx in range(SPRITE_W):
        for sy in range(SPRITE_H):
            if (sx, sy) in seen or frame.get_at((sx, sy))[3] <= 8:
                continue
            blobs += 1
            stack = [(sx, sy)]
            seen.add((sx, sy))
            while stack:
                x, y = stack.pop()
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        nx, ny = x + dx, y + dy
                        if not (0 <= nx < SPRITE_W and 0 <= ny < SPRITE_H):
                            continue
                        if (nx, ny) in seen or frame.get_at((nx, ny))[3] <= 8:
                            continue
                        seen.add((nx, ny))
                        stack.append((nx, ny))
    return blobs


if __name__ == "__main__":
    OUT_DIR = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(OUT_DIR, exist_ok=True)

    raw    = [_build_hurt_frame(a) for a in _HURT_ANGLES]
    frames = [_add_outline(f) for f in raw]

    f0 = raw[0]
    ring_px   = _count_in_disc(f0, SHADE_FRAME, LEFT_C, RIM_R + 1)
    left_fill = _count_in_disc(f0, SHADE_BLACK, LEFT_C, HOLLOW_R)
    lid_px    = _count_in_disc(f0, LID, LEFT_C, RIM_R)
    right_fill = _count_in_disc(f0, SHADE_BLACK, RIGHT_C, RIM_R - 1)
    gape_px   = _count_in_disc(f0, GAPE, (56, 28), 8)

    print(f"left ring (gold)   : {ring_px}   (want > 15)")
    print(f"left fill (dark)   : {left_fill}   (want 0 / very few)")
    print(f"squint arc         : {lid_px}   (want > 3)")
    print(f"right lens fill    : {right_fill}   (want > 20)")
    print(f"beak gape interior : {gape_px}")
    print(f"islands per frame  : {[_islands(f) for f in raw]}   (want all 1)")

    BG = (8, 8, 20)
    fw, fh = frames[0].get_size()
    strip = pygame.Surface((fw * len(frames), fh))
    strip.fill(BG)
    for i, f in enumerate(frames):
        strip.blit(f, (i * fw, 0))

    out_path = os.path.join(OUT_DIR, "round_1.png")
    pygame.image.save(strip, out_path)
    print(f"Saved {strip.get_width()}x{strip.get_height()} -> {out_path}")
