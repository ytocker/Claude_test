"""
`bandaged-crisis` — hurt-parrot concept exploration (standalone, not wired in).

V4 of the bloodshot line. V3 told the injury with claw-rake texture, which is
exactly the class of detail that dies at 1x — dark-on-dark cuts on a dark red
breast. So the rake is gone entirely and the whole story is carried by three
pieces of high-contrast *applied* hardware: a temple gauze strip, an adhesive
plaster on the breast, and a tape band across the wing. Off-white on red is the
strongest value pair available in this palette.

Round 2 fixes what round 1 got structurally wrong rather than cosmetically:
the gauze now goes on *under* the shades (he put them back on over it), the
wing tape lives in wing-local space so it actually rides the wing through the
flap cycle, the left lens is broken into tinted plates instead of scratched
lines, and there is exactly ONE red cross on the sprite — a second one on the
chest was competing with the hero mark for no extra information.
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
SHADE_FRAME = (220, 175, 40)

GAUZE      = (232, 228, 215)
PAD        = (255, 248, 230)
# Hem sits a full four values darker than the gauze it edges. At the old
# stitch tone the border merged with the fill at 1x and every bandage read as
# an undifferentiated white chip.
HEM        = (120, 108,  95)
CROSS      = (210,  30,  30)
BROW       = (120,  10,  14)

# Cracks read as light caught in the fracture; the plates behind them are the
# lens itself, come apart into pieces that no longer sit in the same plane.
CRACK      = (180, 210, 240)
CRACK_WEB  = (140, 170, 200)
PLATE_A    = ( 42,  52,  78)
PLATE_B    = ( 28,  34,  56)

WISP       = (220,  70,  70)
WISP_TIP   = (230, 195,  65)

# Left lens rides five pixels low and a size larger than its twin: the side that
# took the hit is the side the eye should land on first.
LENS_L, LENS_LR = (43, 24), 7
LENS_R, LENS_RR = (56, 19), 6

# The wing is drawn into an oversized surface so hardware and tear-outs near
# the primaries have room to exist; the constant offset keeps the shape in the
# same place relative to the rotation pivot as the original 50x50 build.
WING_SURF, WING_OFF = 56, 3


def _wp(pts):
    return [(x + WING_OFF, y + WING_OFF) for x, y in pts]


def _aaellipse(surf, color, center, rx, ry):
    cx, cy = center
    pygame.draw.ellipse(surf, color, (cx - rx, cy - ry, rx * 2, ry * 2))


def _stamp_clipped(surf, layer):
    """Composite a layer only where the sprite already has body. Clipping is
    what stops an overhanging bandage edge from becoming a floating white chip
    once the outline pass runs."""
    for x in range(surf.get_width()):
        for y in range(surf.get_height()):
            px = layer.get_at((x, y))
            if px[3] > 8 and surf.get_at((x, y))[3] > 8:
                surf.set_at((x, y), (px[0], px[1], px[2], surf.get_at((x, y))[3]))


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


# Tear-out through the primaries, held outboard of where the skull lands so it
# survives on the up-stroke frames as well as the down-stroke ones.
WING_TEAR = [(37, 33), (47, 30), (45, 39), (36, 38)]


TAPE_A, TAPE_B = (29.0, 34.0), (41.0, 30.0)


def _wing_tape(w):
    """Tape band across the primaries, in wing-local coordinates so it rotates
    with the wing for free. Drawn in world space it only *looked* right on one
    frame — and on that frame 96 % of it was sitting on the chest."""
    d = pygame.draw
    (ax, ay), (bx, by) = TAPE_A, TAPE_B
    dx, dy = bx - ax, by - ay
    L = math.hypot(dx, dy)
    px, py = -dy / L * 2.5, dx / L * 2.5
    quad = [(ax + px, ay + py), (bx + px, by + py),
            (bx - px, by - py), (ax - px, ay - py)]
    layer = pygame.Surface(w.get_size(), pygame.SRCALPHA)
    d.polygon(layer, GAUZE, _wp(quad))
    # Hem on all four edges, short ends included: the two ends are where the
    # eye decides whether it is looking at tape or at a smear of light.
    d.polygon(layer, HEM, _wp(quad), 1)
    mask = pygame.mask.from_surface(w, threshold=8).to_surface(
        setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0))
    layer.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    w.blit(layer, (0, 0))


def _build_wing(angle_deg, tear=True):
    WING   = (30,  70, 180)
    WING_D = (18,  42, 125)
    # Pulled back off the healthy bird's vivid green: the wing is the one large
    # colour field on the sprite, and dropping its chroma lets the white
    # hardware stay the brightest thing in the silhouette.
    TIP    = (40, 185,  80)
    STRIPE = (210, 175,  50)
    HL     = (130, 175, 240)
    w = pygame.Surface((WING_SURF, WING_SURF), pygame.SRCALPHA)
    d = pygame.draw
    d.polygon(w, (0,0,0,100), _wp([(24,26),(46,14),(50,30),(34,44),(18,40)]))
    d.polygon(w, WING,        _wp([(24,24),(44,13),(48,28),(32,42),(18,36)]))
    d.polygon(w, WING_D,      _wp([(24,24),(32,42),(18,36)]))
    d.polygon(w, TIP,         _wp([(44,13),(50,18),(48,28)]))
    d.polygon(w, STRIPE,      _wp([(42,18),(48,22),(46,28),(40,24)]))
    d.line(w, WING_D,         *_wp([(26,25),(42,18)]), 2)
    d.line(w, WING_D,         *_wp([(28,30),(44,25)]), 2)
    d.line(w, WING_D,         *_wp([(30,34),(46,32)]), 2)
    d.line(w, HL,             *_wp([(25,25),(41,15)]), 1)

    _wing_tape(w)

    # Punched as transparency rather than painted dark so the break survives
    # the outline pass and the 1x downscale. The toggle exists so the render
    # pass can diff a torn frame against an intact one and prove the tear is
    # not simply hiding behind the skull, which is what it was doing before.
    if tear:
        d.polygon(w, (0,0,0,0), _wp(WING_TEAR))
    return pygame.transform.rotate(w, angle_deg)


def _draw_plaster(surf):
    """Sticking plaster on the breast — 8x8 with the corners taken off. The
    corner punch is doing real work: a hard square at this size reads as a
    label stuck on the bird, while the rounded chip reads as an adhesive pad.

    No cross on it. Two crosses on one sprite is two hero marks, which is none;
    pad plus hem carries "plaster" on its own and lets the temple gauze own the
    medical read."""
    layer = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    d = pygame.draw
    cx, cy = 26, 38
    x0, y0, s = cx - 4, cy - 4, 8
    d.rect(layer, GAUZE, (x0, y0, s, s))
    d.rect(layer, PAD,   (x0 + 2, y0 + 2, s - 4, s - 4))
    d.rect(layer, HEM,   (x0, y0, s, s), 1)
    for ox, oy in ((0, 0), (s - 1, 0), (0, s - 1), (s - 1, s - 1)):
        layer.set_at((x0 + ox, y0 + oy), (0, 0, 0, 0))
    _stamp_clipped(surf, layer)


GAUZE_QUAD = [(29, 24), (31, 7), (48, 9), (46, 26)]
# The cross sits in the clear strip between the first two crown wisps and above
# the left rim. Centred on the dressing it was being eaten from both sides at
# once — by a wisp on the left and by the lens on the bottom.
CROSS_H    = ((41, 15), (47, 15))
CROSS_V    = ((44, 11), (44, 20))


def _draw_bandage(surf):
    """Gauze taped diagonally across the temple, and — the round-2 change —
    *under* the shades rather than over them. Over the top it was erasing the
    shatter web and half the left lens, which is the one place on the sprite
    that has to stay readable. Under it, the shades sit on the gauze the way
    they would if he had put them back on after being patched up.

    Clipped to the silhouette: the skull narrows fast above the brow, and drawn
    free the crown end of the strip hung in open sky as a loose white flag."""
    layer = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    d = pygame.draw
    d.polygon(layer, GAUZE, GAUZE_QUAD)
    d.polygon(layer, HEM, GAUZE_QUAD, 1)
    d.line(layer, CROSS, *CROSS_H, 2)
    d.line(layer, CROSS, *CROSS_V, 2)
    _stamp_clipped(surf, layer)


def _wisp(surf, pts):
    """One crown feather, tapered 3 px at the root to 1 px at the tip and
    finished in the tail's warm gold. A wisp of constant width is a twig; the
    taper plus the warm tip is what makes it read as a feather that has been
    knocked out of line."""
    samples = []
    for i in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        n = max(2, int(math.hypot(x1 - x0, y1 - y0) * 3))
        for k in range(n + 1):
            t = k / n
            samples.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
    cum, total = [0.0], 0.0
    for i in range(1, len(samples)):
        total += math.hypot(samples[i][0] - samples[i - 1][0],
                            samples[i][1] - samples[i - 1][1])
        cum.append(total)
    for i in range(1, len(samples)):
        t = cum[i] / total
        col = WISP_TIP if (total - cum[i]) <= 3.0 else WISP
        pygame.draw.line(surf, col,
                         (round(samples[i - 1][0]), round(samples[i - 1][1])),
                         (round(samples[i][0]), round(samples[i][1])),
                         max(1, int(round(3 - 2 * t))))


def _draw_head_wisps(surf):
    """Three crown feathers spread across the whole width of the skull rather
    than bunched over one spot — a fan that fights the head's clean dome is a
    posture cue, a tuft is just a hat. One forward over the brow, one straight
    up, one kicked back, all of them breaking the ellipse."""
    _wisp(surf, [(41, 15), (39, 9), (37, 6)])
    _wisp(surf, [(47, 14), (47, 8), (47, 5)])
    _wisp(surf, [(52, 15), (54, 9), (56, 6)])


def _draw_brow(surf):
    """A single downturned line above the right lens. It replaces the under-eye
    shadow, which was a soft blob sitting behind glass where nothing soft can
    survive. The exhaustion read now lives in geometry — the good eye is the
    one squinting — and it is on the intact side so it never fights the rim of
    the broken one."""
    pygame.draw.lines(surf, BROW, False, [(48, 12), (53, 14), (57, 17)], 2)


def _draw_sunglasses(surf):
    """Aviator shades, knocked crooked. The left lens rides low and a size
    wider; the bridge kinks up to meet its twin instead of running level.
    Only the right lens keeps its glint — one dead lens against one still
    catching the sun is the read."""
    d = pygame.draw
    d.circle(surf, SHADE_FRAME, LENS_L, LENS_LR + 1)
    d.circle(surf, SHADE_FRAME, LENS_R, LENS_RR + 1)
    d.circle(surf, SHADE_BLACK, LENS_L, LENS_LR)
    d.circle(surf, SHADE_BLACK, LENS_R, LENS_RR)
    for c, r in ((LENS_L, LENS_LR), (LENS_R, LENS_RR)):
        tint = pygame.Surface((r * 2, r), pygame.SRCALPHA)
        d.ellipse(tint, (*SHADE_TINT, 130), tint.get_rect())
        surf.blit(tint, (c[0] - r, c[1] - r + 1))
    d.circle(surf, SHADE_GLINT, (LENS_R[0] - 2, LENS_R[1] - 3), 2)
    d.circle(surf, (255, 255, 255, 200), (LENS_R[0] + 2, LENS_R[1] + 1), 1)
    d.line(surf, SHADE_FRAME, (49, 24), (52, 20), 2)
    d.line(surf, SHADE_FRAME,
           (LENS_L[0] - LENS_LR + 1, LENS_L[1] - LENS_LR + 2),
           (LENS_R[0] + LENS_RR - 1, LENS_R[1] - LENS_RR + 2), 1)


def _lens_clip(surf, layer, center, radius):
    """Fracture lines are clipped to the glass they belong to. Left free they
    ran off the rim and onto the skull, which read as face wounds rather than
    broken glass."""
    mask = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), center, radius)
    layer.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    # The clip leaves single orphaned pixels where a crack grazes the rim. One
    # loose bright pixel on black glass reads as dirt on the screen, not as
    # damage, so anything with no neighbour goes.
    orphans = []
    for x in range(center[0] - radius - 1, center[0] + radius + 2):
        for y in range(center[1] - radius - 1, center[1] + radius + 2):
            if not (0 <= x < layer.get_width() and 0 <= y < layer.get_height()):
                continue
            if layer.get_at((x, y))[3] <= 8:
                continue
            if not any(0 <= x + dx < layer.get_width()
                       and 0 <= y + dy < layer.get_height()
                       and layer.get_at((x + dx, y + dy))[3] > 8
                       for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                orphans.append((x, y))
    for p in orphans:
        layer.set_at(p, (0, 0, 0, 0))
    surf.blit(layer, (0, 0))


# Radials off the impact point, kept in clockwise screen order so consecutive
# pairs bound a wedge of glass.
_RADIALS = ((38, 18), (49, 19), (48, 28), (42, 29), (37, 25))
_IMPACT  = (43, 23)


def _draw_cracked_lenses(surf):
    """Left lens shatters, right lens only sympathises. The round-1 version was
    lines scratched on a flat black disc; this one floods the wedges *between*
    the radials with two off-tones first, so the lens reads as plates that have
    come apart and are catching light at different angles. Cracks then go on
    top, with the two longest carrying double width — at 1x a one-pixel crack
    on a seven-pixel lens is noise, and the long pair is what sells the axis of
    the impact."""
    d = pygame.draw
    layer = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    for i, tone in ((0, PLATE_A), (2, PLATE_B), (4, PLATE_A)):
        d.polygon(layer, tone,
                  [_IMPACT, _RADIALS[i], _RADIALS[(i + 1) % len(_RADIALS)]])
    longest = sorted(_RADIALS,
                     key=lambda p: -math.hypot(p[0] - _IMPACT[0],
                                               p[1] - _IMPACT[1]))[:2]
    for end in _RADIALS:
        d.line(layer, CRACK, _IMPACT, end, 2 if end in longest else 1)
    d.line(layer, CRACK_WEB, (39, 19), (37, 25), 1)
    d.line(layer, CRACK_WEB, (48, 19), (48, 28), 1)
    # Clipped to the rim rather than the glass: a fracture that runs right into
    # the frame is what real shattered glass does.
    _lens_clip(surf, layer, LENS_L, LENS_LR + 1)

    layer = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    d.line(layer, CRACK, (55, 19), (52, 16), 1)
    d.line(layer, CRACK, (55, 19), (58, 22), 1)
    _lens_clip(surf, layer, LENS_R, LENS_RR)


def _tail_feather(pts, damaged=False):
    """Tail feathers run root-right, tip-left. A damaged one is snapped short
    and kicked off-axis so the fan's clean outline breaks — silhouette damage
    survives the 1x downscale where any painted-on detail would not."""
    if not damaged:
        return pts
    root = ((pts[1][0] + pts[2][0]) / 2.0, (pts[1][1] + pts[2][1]) / 2.0)
    a = math.radians(18)
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


def _build_hurt_frame(wing_angle_deg, tear=True):
    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    d = pygame.draw

    BODY    = (205,  28,  28)
    BODY_SH = (130,  12,  12)
    CHEST   = (235,  80,  80)
    BELLY   = (215, 140,  45)
    BEAK    = (235, 168,   0)
    BEAK_LO = (205, 138,   0)
    BEAK_D  = (140,  92,   0)

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

    sheen = pygame.Surface((28, 6), pygame.SRCALPHA)
    d.ellipse(sheen, (205, 150, 150, 120), sheen.get_rect())
    surf.blit(sheen, (22, 21))

    wing = _build_wing(wing_angle_deg, tear=tear)
    surf.blit(wing, wing.get_rect(center=(34, 28)).topleft)

    _draw_plaster(surf)

    # Head hangs 1 px lower than the healthy build — small in absolute terms,
    # but it breaks the proud upward line of the original silhouette.
    _aaellipse(surf, (155, 15, 20), (48, 24), 12, 11)
    _aaellipse(surf, BODY,          (47, 22), 12, 11)
    _aaellipse(surf, (200, 90, 90), (44, 24),  4,  3)
    _aaellipse(surf, (230, 140, 140), (46, 17),  7,  3)

    _draw_bandage(surf)
    _draw_head_wisps(surf)
    _draw_brow(surf)
    _draw_sunglasses(surf)
    _draw_cracked_lenses(surf)

    # Beak parted only ~2 px, and the lower mandible tucked up under the upper.
    upper = [(55, 21), (61, 24), (58, 26), (52, 25)]
    lower = [(52, 26), (58, 27), (59, 30), (54, 31)]
    d.polygon(surf, BEAK,    upper)
    d.polygon(surf, BEAK_D,  upper, 1)
    d.polygon(surf, BEAK_LO, lower)
    d.polygon(surf, BEAK_D,  lower, 1)
    d.line(surf, (255, 220, 100), (55, 22), (59, 24), 1)

    d.line(surf, BEAK_D, (28, 45), (26, 49), 2)
    d.line(surf, BEAK_D, (34, 45), (36, 49), 2)

    return surf


def _count(frame, pred, box=None):
    """Counts are box-scoped on purpose. A whole-sprite tally of "white pixels"
    passes happily while one of the three bandages is being overpainted by the
    wing — each mark has to be proved present in its own region."""
    x0, y0, x1, y1 = box or (0, 0, SPRITE_W, SPRITE_H)
    n = 0
    for x in range(max(0, x0), min(x1, SPRITE_W)):
        for y in range(max(0, y0), min(y1, SPRITE_H)):
            r, g, b, a = frame.get_at((x, y))
            if a > 8 and pred(r, g, b):
                n += 1
    return n


def _blobs(frame, pred, min_size=6):
    """Connected components of bandage-coloured pixel. Pixel budgets alone
    cannot tell "three separate dressings" from "one white smear of the same
    total area", and the smear is the failure mode that actually happened."""
    seen = set()
    out = []
    for sx in range(SPRITE_W):
        for sy in range(SPRITE_H):
            if (sx, sy) in seen:
                continue
            r, g, b, a = frame.get_at((sx, sy))
            if a <= 8 or not pred(r, g, b):
                continue
            stack, comp = [(sx, sy)], []
            seen.add((sx, sy))
            while stack:
                x, y = stack.pop()
                comp.append((x, y))
                for nx, ny in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
                    if not (0 <= nx < SPRITE_W and 0 <= ny < SPRITE_H):
                        continue
                    if (nx, ny) in seen:
                        continue
                    rr, gg, bb, aa = frame.get_at((nx, ny))
                    if aa > 8 and pred(rr, gg, bb):
                        seen.add((nx, ny))
                        stack.append((nx, ny))
            if len(comp) >= min_size:
                out.append((len(comp),
                            (sum(p[0] for p in comp) / len(comp),
                             sum(p[1] for p in comp) / len(comp))))
    return out


def _dressings(frame, pred):
    """Sort the bandage blobs into the three dressings by where they sit, then
    give each its pixel budget and its centroid. Grouping by region rather than
    by blob size is what makes the check honest: a dressing that has been split
    in two by a feather wisp is still one dressing, and three fragments of one
    smear must not be able to pass as three separate marks."""
    groups = {"gauze": [], "plaster": [], "tape": []}
    for n, (cx, cy) in _blobs(frame, pred, min_size=3):
        if cy < 27 and cx > 30:
            groups["gauze"].append((n, cx, cy))
        elif cy > 32 and cx < 32:
            groups["plaster"].append((n, cx, cy))
        else:
            groups["tape"].append((n, cx, cy))
    out = {}
    for k, g in groups.items():
        n = sum(p[0] for p in g)
        out[k] = (n, (sum(p[0] * p[1] for p in g) / n if n else 0.0,
                      sum(p[0] * p[2] for p in g) / n if n else 0.0))
    return out


def _strip(frames, scale, gap, bg):
    fw, fh = frames[0].get_size()
    w = len(frames) * fw * scale + (len(frames) - 1) * gap
    s = pygame.Surface((w, fh * scale))
    s.fill(bg)
    for i, f in enumerate(frames):
        s.blit(pygame.transform.scale(f, (fw * scale, fh * scale)),
               (i * (fw * scale + gap), 0))
    return s


if __name__ == "__main__":
    OUT_DIR = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(OUT_DIR, exist_ok=True)

    raw    = [_build_hurt_frame(a) for a in _HURT_ANGLES]
    notear = [_build_hurt_frame(a, tear=False) for a in _HURT_ANGLES]
    frames = [_add_outline(f) for f in raw]

    is_white = lambda r, g, b: (r, g, b) in (GAUZE, PAD)
    is_glass = lambda r, g, b: (r, g, b) in (CRACK, CRACK_WEB, PLATE_A, PLATE_B)
    is_wisp  = lambda r, g, b: (r, g, b) in (WISP, WISP_TIP)
    is_cross = lambda r, g, b: (r, g, b) == CROSS

    stats = []
    for idx, f in enumerate(raw):
        marks   = _dressings(f, is_white)
        gauze   = marks["gauze"][0]
        plaster = marks["plaster"][0]
        tape    = marks["tape"][0]
        glass   = _count(f, is_glass, (34, 14, 54, 34))
        wisps   = _count(f, is_wisp,  ( 0,  0, 64, 12))
        cross   = _count(f, is_cross, (30,  6, 50, 26))
        total   = _count(f, is_white)

        assert gauze   >= 40, f"f{idx}: temple bandage too faint: {gauze}"
        assert plaster >= 15, f"f{idx}: chest plaster too small: {plaster}"
        assert tape    >= 15, f"f{idx}: wing tape not visible: {tape}"
        assert glass   >= 45, f"f{idx}: shattered glass not legible: {glass}"
        assert wisps   >= 30, f"f{idx}: wisps not protruding past head: {wisps}"
        assert cross   >=  8, f"f{idx}: red cross missing: {cross}"
        # Exactly one cross on the sprite — the chest plaster must not have one.
        assert _count(f, is_cross) == cross, f"f{idx}: second cross on sprite"

        cents = [marks[k][1] for k in ("gauze", "plaster", "tape")]
        dmin = min(math.hypot(a[0] - b[0], a[1] - b[1])
                   for i, a in enumerate(cents) for b in cents[i + 1:])
        assert dmin >= 12, f"f{idx}: bandages merging, min centroid gap {dmin:.1f}"

        delta = sum(1 for x in range(SPRITE_W) for y in range(SPRITE_H)
                    if f.get_at((x, y)) != notear[idx].get_at((x, y)))
        assert delta >= 25, f"f{idx}: wing tear hidden, delta {delta}"

        stats.append((gauze, plaster, tape, glass, wisps, cross, total,
                      dmin, delta))

    NIGHT, DAY = (8, 8, 20), (100, 160, 220)
    margin, gap = 20, 10
    row1  = _strip(frames, 4, gap, NIGHT)
    row2  = _strip(frames, 2, gap, NIGHT)
    row3a = _strip(frames, 1, gap, DAY)
    row3b = _strip(frames, 1, gap, (5, 8, 30))

    label_h, pad3 = 30, 12
    canvas_w = margin * 2 + max(row1.get_width(), row2.get_width())
    canvas_h = (margin + row1.get_height() + gap + row2.get_height() + gap +
                row3a.get_height() + pad3 * 2 + label_h + margin)
    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill(NIGHT)

    canvas.blit(row1, (margin, margin))
    y = margin + row1.get_height() + gap
    canvas.blit(row2, (margin, y))
    y += row2.get_height() + gap

    # Day and night side by side at shipping size: the whole point of the white
    # hardware and the ice-blue cracks is that they hold on both backgrounds.
    for i, (panel, bg) in enumerate(((row3a, DAY), (row3b, (5, 8, 30)))):
        px = margin + i * (panel.get_width() + pad3 * 2 + gap * 2)
        pygame.draw.rect(canvas, bg, (px, y, panel.get_width() + pad3 * 2,
                                      panel.get_height() + pad3 * 2))
        canvas.blit(panel, (px + pad3, y + pad3))
    y += row3a.get_height() + pad3 * 2

    try:
        font  = pygame.font.SysFont("dejavusans", 17)
        small = pygame.font.SysFont("dejavusans", 12)
    except Exception:
        font = small = pygame.font.Font(None, 17)
    canvas.blit(small.render("1x on day sky", True, (10, 20, 40)),
                (margin + pad3, y - pad3 + 1))
    canvas.blit(small.render("1x on night sky", True, (200, 205, 230)),
                (margin + row3a.get_width() + pad3 * 3 + gap * 2, y - pad3 + 1))
    lbl = font.render("bandaged-crisis — round 2   (4x / 2x / 1x day + night)",
                      True, (225, 225, 245))
    canvas.blit(lbl, (margin, canvas_h - margin - lbl.get_height() + 4))

    out_path = os.path.join(OUT_DIR, "round_2.png")
    pygame.image.save(canvas, out_path)
    print(f"Saved {canvas_w}x{canvas_h} -> {out_path}")
    for i, s in enumerate(stats):
        print(f"f{i}: gauze={s[0]} plaster={s[1]} tape={s[2]} glass={s[3]} "
              f"wisps={s[4]} cross={s[5]} white_total={s[6]} "
              f"blobgap={s[7]:.1f} tear_delta={s[8]}")
