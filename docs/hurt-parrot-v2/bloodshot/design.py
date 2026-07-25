"""
`bloodshot` — hurt-parrot concept exploration (standalone, not wired in).

Medical-crisis read: the macaw is not "a normal parrot with a hurt marker on
top" — the construction itself changes. Aviators are gone so the eyes can do
the acting, the beak breaks into two jaws that hang a real gape open, and the
plumage drops a full value step into bruised, oxygen-starved reds. Silhouette,
value and colour all carry the state at 1x so a player reads it in a single
glance mid-flap.
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
    # A chunk bitten clean out of the primaries: punched as transparency rather
    # than painted dark, so the hole survives the outline pass and the 1x
    # downscale as a genuine break in the silhouette.
    d.polygon(w, (0,0,0,0),   [(43,12),(51,17),(47,23),(44,17)])
    return pygame.transform.rotate(w, angle_deg)


def _clip_to_body(layer, body):
    """Keep a paint layer inside whatever has already been drawn. Bruises hang
    off the belly edge otherwise, and a stray purple lump outside the body gets
    picked up by the outline pass as if it were anatomy."""
    keep = pygame.mask.from_surface(body, threshold=8).to_surface(
        setcolor=(255, 255, 255, 255), unsetcolor=(255, 255, 255, 0))
    layer.blit(keep, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)


def _draw_bruises(surf, alpha_boost):
    """Subdermal haemorrhage layer, painted translucent so the red plumage
    still shows through — an opaque purple patch would read as a sticker."""
    layer = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    # Shoulder, low-left belly and flank. The belly patch is placed clear of
    # the wing's sweep arc, which swallows anything sitting mid-chest on half
    # the frames.
    bruises = (
        ((90, 15, 52), (30, 25), 8, 5, 205),
        ((90, 15, 52), (24, 42), 7, 4, 205),
        ((90, 15, 52), (38, 35), 5, 3, 195),
    )
    for rgb, center, rx, ry, base_a in bruises:
        a = min(255, base_a + alpha_boost)
        _aaellipse(layer, (*rgb, a), center, rx, ry)
        cx, cy = center
        pygame.draw.ellipse(layer, (50, 5, 28, min(255, a + 40)),
                            (cx - rx, cy - ry, rx * 2, ry * 2), 1)
    _clip_to_body(layer, surf)
    surf.blit(layer, (0, 0))


def _draw_bloodshot_eye(surf, cx, cy, rx, ry, iris_r, lid=True):
    """Engorged eye. The sclera is deliberately pale bone rather than red —
    against red plumage a red sclera has almost no luma delta and the whole eye
    dissolves into the head. Bone + red veins is the only version that reads."""
    SCLERA = (240, 228, 196)
    SCLERA_SH = (216, 200, 166)
    IRIS   = (120, 15, 15)
    VEIN   = (200, 30, 30)
    LID    = (188, 46, 46)

    _aaellipse(surf, SCLERA, (cx, cy), rx, ry)
    _aaellipse(surf, SCLERA_SH, (cx, cy + 1), rx - 1, max(1, ry - 2))
    _aaellipse(surf, SCLERA, (cx, cy), rx - 1, ry - 1)

    # Iris rides high and forward, which leaves the widest run of bare sclera
    # exactly where the veins are angled — a centred iris would bury them.
    ix, iy = cx + 1, cy - 1

    for deg in (30, 75, 120, 165, 210):
        a = math.radians(deg)
        ca, sa = math.cos(a), math.sin(a)
        # Ray length solved against the sclera ellipse so a vein dies at the
        # rim (+1 px onto the lid skin) instead of bleeding across the cheek.
        edge = 1.0 / math.sqrt((ca / rx) ** 2 + (sa / ry) ** 2)
        pygame.draw.line(surf, VEIN,
                         (cx + ca * 1.5, cy + sa * 1.5),
                         (cx + ca * (edge + 1.0), cy + sa * (edge + 1.0)), 1)

    pygame.draw.circle(surf, IRIS, (ix, iy), iris_r)
    pygame.draw.circle(surf, (70, 8, 8), (ix, iy), iris_r, 1)
    pygame.draw.circle(surf, (0, 0, 0), (ix, iy), 2)
    pygame.draw.circle(surf, (255, 255, 255), (ix - 1, iy - 2), 1)

    if lid:
        # A hooded top edge is the single strongest "barely conscious" cue; it
        # is kept to a sliver so it never eats the bone the concept rests on.
        drop = cy - ry + 1
        pts = [(cx - rx, drop)]
        for i in range(9):
            t = i / 8.0
            x = cx - rx + t * rx * 2
            k = max(0.0, 1.0 - ((x - cx) / float(rx)) ** 2) ** 0.5
            pts.append((x, cy - ry * k))
        pts.append((cx + rx, drop))
        pygame.draw.polygon(surf, LID, pts)
        pygame.draw.line(surf, (120, 25, 30), (cx - rx + 1, drop),
                         (cx + rx - 1, drop), 1)


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
    BELLY   = (180, 80, 20)
    BEAK    = (220, 160,  0)
    BEAK_LO = (190, 130,  0)
    BEAK_D  = (140,  92,  0)
    THROAT  = (30, 10, 10)

    # Tail — same fan construction, dropped a value step so it no longer
    # out-saturates the head where the acting happens.
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
    _aaellipse(surf, (150, 40, 45), (40, 27),  4,  3)
    _aaellipse(surf, (175, 60, 60), (46, 17),  7,  3)

    # Both eyes are pulled inboard of the skull's right edge; the beak owns
    # everything past x=51 now that the jaws hang open.
    _draw_bloodshot_eye(surf, 44, 20, 7, 6, 5)
    _draw_bloodshot_eye(surf, 53, 19, 5, 4, 3, lid=False)

    # Jaws hang a full 6 px apart. The throat void goes down first so both
    # beak halves stamp over it with clean edges against the gap.
    d.polygon(surf, THROAT, [(51, 24), (58, 26), (58, 32), (51, 30)])
    upper = [(55, 20), (61, 24), (58, 26), (51, 25)]
    lower = [(51, 30), (58, 31), (60, 34), (54, 36)]
    d.polygon(surf, THROAT, [(52, 26), (57, 27), (57, 30), (52, 29)])
    _aaellipse(surf, (200, 60, 60), (55, 29), 3, 2)
    d.polygon(surf, BEAK,    upper)
    d.polygon(surf, BEAK_D,  upper, 1)
    d.polygon(surf, BEAK_LO, lower)
    d.polygon(surf, BEAK_D,  lower, 1)
    d.line(surf, (255, 220, 100), (55, 21), (59, 24), 1)

    d.line(surf, BEAK_D, (28, 45), (26, 49), 2)
    d.line(surf, BEAK_D, (34, 45), (36, 49), 2)

    return surf


if __name__ == "__main__":
    OUT_DIR = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(OUT_DIR, exist_ok=True)
    scale   = 4
    raw     = [_build_hurt_frame(a) for a in _HURT_ANGLES]
    frames  = [_add_outline(f) for f in raw]
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
    lbl = font.render("bloodshot — round 2", True, (220, 220, 240))
    canvas.blit(lbl, (margin, margin + (label_h - lbl.get_height()) // 2))
    for i, frame in enumerate(frames):
        px = margin + i * (fw * scale + gap)
        py = margin + label_h + gap
        canvas.blit(pygame.transform.scale(frame, (fw*scale, fh*scale)), (px, py))
    out_path = os.path.join(OUT_DIR, "round_2.png")
    pygame.image.save(canvas, out_path)
    print(f"Saved {canvas_w}x{canvas_h} -> {out_path}")

    sclera = throat = bruise = 0
    for f in raw:
        for x in range(SPRITE_W):
            for y in range(SPRITE_H):
                r, g, b, a = f.get_at((x, y))
                if a < 8:
                    continue
                if r > 200 and g > 180 and b > 140:
                    sclera += 1
                if 48 <= x <= 62 and 22 <= y <= 38 and r < 50 and g < 20:
                    throat += 1
                if r > 60 and g < 25 and b > 30:
                    bruise += 1
    print(f"sclera={sclera} (need >200)  throat={throat} (need >10)  "
          f"bruise={bruise} (need >50)")
