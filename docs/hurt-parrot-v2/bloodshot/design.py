"""
`bloodshot` — hurt-parrot concept exploration (standalone, not wired in).

Medical-crisis read: the macaw is not "a normal parrot with a hurt marker on
top" — the construction itself changes. Aviators are gone so the eyes can do
the acting, the beak breaks into two jaws that hang open, and the plumage
drops a full value step into bruised, oxygen-starved reds. Silhouette + colour
carry the state at 1x so a player reads it in a single glance mid-flap.
"""
import math
import os, sys
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "offscreen"

import pygame
pygame.init()

SPRITE_W, SPRITE_H = 64, 60
_HURT_ANGLES = (10, -5, -20, -35)


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
    TIP    = (110, 155,  38)
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
    # A torn-out primary reads as injury in silhouette, which survives the
    # rotation and the 1x downscale better than any painted-on detail would.
    d.polygon(w, (0,0,0,0),   [(44,13),(50,18),(48,22),(46,16)])
    return pygame.transform.rotate(w, angle_deg)


def _draw_bruises(surf, alpha_boost):
    """Subdermal haemorrhage layer, painted translucent so the red plumage
    still shows through — an opaque purple patch would read as a sticker."""
    layer = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    # The flank patch sits low and aft of the shoulder because the flapping
    # wing sweeps over the mid-chest and would swallow it on half the frames.
    bruises = (
        ((90, 15, 52), (28, 30), 9, 6, 205),
        ((80, 12, 45), (40, 39), 7, 5, 195),
        ((70, 10, 38), (25, 38), 5, 4, 185),
    )
    for rgb, center, rx, ry, base_a in bruises:
        a = min(255, base_a + alpha_boost)
        _aaellipse(layer, (*rgb, a), center, rx, ry)
        cx, cy = center
        pygame.draw.ellipse(layer, (50, 5, 28, min(255, a + 40)),
                            (cx - rx, cy - ry, rx * 2, ry * 2), 1)
    surf.blit(layer, (0, 0))


def _draw_bloodshot_eye(surf, cx, cy):
    """Engorged, lidded eye. The sclera is bigger than the aviator lens it
    replaces so the head silhouette still balances against the open beak."""
    SCLERA = (210, 45, 45)
    IRIS   = (40,   8,  8)
    PUPIL  = (10,   5,  5)
    VESSEL = (180, 20, 20)
    LID    = (185, 45, 45)
    rx, ry = 7, 6

    _aaellipse(surf, SCLERA, (cx, cy), rx, ry)

    # Burst capillaries radiate outward, so they must be drawn under the iris
    # to look like they surface from behind it rather than sit on the glass.
    for deg in (205, 250, 315, 25):
        a = math.radians(deg)
        x0, y0 = cx + math.cos(a) * 3.2, cy + math.sin(a) * 2.8
        x1, y1 = cx + math.cos(a) * (rx - 0.5), cy + math.sin(a) * (ry - 0.5)
        pygame.draw.line(surf, VESSEL, (x0, y0), (x1, y1), 1)

    pygame.draw.circle(surf, IRIS,  (cx, cy), 4)
    pygame.draw.circle(surf, PUPIL, (cx, cy), 2)
    pygame.draw.circle(surf, (255, 255, 255), (cx - 2, cy - 2), 1)

    # Heavy upper lid — the single strongest "barely conscious" cue, and the
    # only thing that stops two big round eyes reading as startled instead.
    lid = [(cx - rx, cy - 1)]
    for i in range(9):
        t = i / 8.0
        x = cx - rx + t * rx * 2
        # Ellipse top arc, sampled so the lid hugs the sclera edge exactly.
        k = max(0.0, 1.0 - ((x - cx) / rx) ** 2) ** 0.5
        lid.append((x, cy - ry * k))
    lid.append((cx + rx, cy - 1))
    pygame.draw.polygon(surf, LID, lid)
    pygame.draw.line(surf, (120, 25, 30), (cx - rx, cy - 1), (cx + rx, cy - 1), 1)


def _build_hurt_frame(wing_angle_deg):
    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    d = pygame.draw

    BODY    = (205, 28, 28)
    BODY_SH = (130, 12, 12)
    CHEST   = (160, 22, 22)
    BELLY   = (175, 70, 20)
    BEAK    = (220, 160,  0)
    BEAK_LO = (190, 130,  0)
    BEAK_D  = (140,  92,  0)

    # Tail — same fan construction, dropped a value step so it no longer
    # out-saturates the head where the acting happens.
    for i, c in enumerate(((180, 25, 35), (190, 70, 30),
                           (210, 130, 40), (230, 195, 65))):
        d.polygon(surf, c, [
            (2 + i * 3, 26 + i * 2), (14 + i, 24 + i),
            (20 + i, 30 + i * 2), (6 + i * 3, 36 + i * 2),
        ])
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

    try:
        boost = (0, 5, 8, 5)[_HURT_ANGLES.index(wing_angle_deg)]
    except ValueError:
        boost = 0
    _draw_bruises(surf, boost)

    wing = _build_wing(wing_angle_deg)
    surf.blit(wing, wing.get_rect(center=(34, 28)).topleft)

    # Head hangs 1 px lower than the healthy build — small in absolute terms,
    # but it breaks the proud upward line of the original silhouette.
    _aaellipse(surf, (155, 15, 20), (48, 24), 12, 11)
    _aaellipse(surf, BODY,          (47, 22), 12, 11)
    _aaellipse(surf, (150, 40, 45), (44, 25),  4,  3)
    _aaellipse(surf, (175, 60, 60), (46, 17),  7,  3)

    _draw_bloodshot_eye(surf, 46, 20)
    _draw_bloodshot_eye(surf, 56, 19)

    # Open beak: the dark throat void is laid down first so both jaws can be
    # stamped over it and keep clean edges against the gap.
    d.polygon(surf, (30, 10, 10), [(51, 24), (57, 26), (60, 28), (57, 28), (51, 26)])
    upper = [(55, 21), (61, 24), (57, 26), (51, 24)]
    lower = [(51, 26), (57, 28), (60, 30), (54, 32)]
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
    scale   = 4
    frames  = [_add_outline(_build_hurt_frame(a)) for a in _HURT_ANGLES]
    fw, fh  = frames[0].get_size()
    margin, gap, label_h = 20, 8, 30
    canvas_w = margin + len(frames)*fw*scale + (len(frames)-1)*gap + margin
    canvas_h = margin + label_h + gap + fh*scale + margin
    canvas   = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((8, 8, 20))
    try:
        font = pygame.font.SysFont("dejavusans", 16)
    except Exception:
        font = pygame.font.Font(None, 16)
    lbl = font.render("bloodshot — round 1", True, (220, 220, 240))
    canvas.blit(lbl, (margin, margin + (label_h - lbl.get_height()) // 2))
    for i, frame in enumerate(frames):
        px = margin + i * (fw * scale + gap)
        py = margin + label_h + gap
        canvas.blit(pygame.transform.scale(frame, (fw*scale, fh*scale)), (px, py))
    out_path = os.path.join(OUT_DIR, "round_1.png")
    pygame.image.save(canvas, out_path)
    print(f"Saved {canvas_w}x{canvas_h} → {out_path}")
