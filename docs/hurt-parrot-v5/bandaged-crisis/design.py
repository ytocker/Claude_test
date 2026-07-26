"""
`bandaged-crisis` — hurt-parrot concept, V5 (standalone, not wired in).

V4 told the injury with six damage beats. Six is a list, not a read: at 1x the
chest plaster and the downturned brow were two extra marks competing for the
same glance, and neither survived the downscale as anything but noise. V5 cuts
to four beats and spends the recovered budget on *structure* instead of more
hardware.

The four beats: temple gauze + red cross, wing tape band, five-crack left lens,
three crown wisps — plus the two structural breaks that now carry the read
before any of the medical detail resolves. The wing tear is no longer a nick in
the trailing edge; it is a wedge that takes the whole lower-trailing corner and
bites two thirds of the way toward the root. The tail loses a feather to a snap
— truncated and kicked off the fan axis, so the fan's outline is broken in
silhouette. Silhouette damage is the only kind that reads at 1x; everything
else is a reward for looking closer.

Palette is unchanged from V4 minus the deleted beats: gauze/hem/cross and the
glass tones are still the only non-body colours on the sprite.
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

GAUZE      = (198, 190, 172)
PAD        = (255, 248, 230)
HEM        = (120, 108,  95)
CROSS      = (190,  20,  35)

CRACK      = (180, 210, 240)
CRACK_WEB  = (140, 170, 200)
PLATE_A    = ( 42,  52,  78)
PLATE_B    = ( 28,  34,  56)

WISP       = (220,  70,  70)
WISP_TIP   = (230, 195,  65)

LENS_L, LENS_LR = (43, 24), 7
LENS_R, LENS_RR = (56, 19), 6

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


def _clip_to_wing(w, layer):
    mask = pygame.mask.from_surface(w, threshold=8).to_surface(
        setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0))
    layer.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    w.blit(layer, (0, 0))


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


# The wedge. Its apex sits ~7 px off the root edge and its mouth swallows the
# whole lower-trailing corner, so the missing material is a shape the eye reads
# as a shape — V4's notch was a dent, and a dent at 1x is just a soft edge. The
# two cut edges carry a 2 px zigzag: a straight cut reads as scissors, and the
# bird did not have scissors.
WING_TEAR = [(32, 21), (37, 19), (43, 22), (46, 27), (44, 32),
             (39, 35), (33, 31), (30, 26)]


def _tear_lip(pts, grow=1.35):
    """Cut edges get a dark lip by drawing the wedge once, oversized, before it
    is punched. Without it the tear is blue meeting red with no transition and
    reads as a paint fill rather than as a hole through a feathered surface."""
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    out = []
    for x, y in pts:
        dx, dy = x - cx, y - cy
        L = max(1e-3, math.hypot(dx, dy))
        out.append((x + dx / L * grow, y + dy / L * grow))
    return out


# Tape moved inboard, onto the shoulder. Its old mid-wing run is now inside the
# wedge, and the two places it could go instead are both worse: high on the
# primaries the skull sits on top of it for three frames out of four, and out
# by the tip it rotates off the sprite. On the root it clears both, sits on the
# darkest field the wing has, and barely moves through the flap cycle.
TAPE_A, TAPE_B = (20.0, 36.0), (31.0, 29.0)


def _wing_tape(w):
    """Tape band across the primaries, in wing-local coordinates so it rotates
    with the wing for free."""
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
    _clip_to_wing(w, layer)


def _build_wing(angle_deg, tear=True):
    WING   = (30,  70, 180)
    WING_D = (18,  42, 125)
    TIP    = (40, 185,  80)
    STRIPE = (210, 175,  50)
    HL     = (130, 175, 240)
    TORN   = (12,  28,  86)
    w = pygame.Surface((WING_SURF, WING_SURF), pygame.SRCALPHA)
    d = pygame.draw
    d.polygon(w, (0,0,0,100), _wp([(24,26),(46,14),(50,30),(34,44),(18,40)]))
    d.polygon(w, WING,        _wp([(24,24),(44,13),(48,28),(32,42),(18,36)]))
    d.polygon(w, WING_D,      _wp([(24,24),(32,42),(18,36)]))
    d.polygon(w, TIP,         _wp([(44,13),(50,18),(48,28)]))
    d.polygon(w, STRIPE,      _wp([(42,18),(48,22),(46,28),(40,24)]))
    d.line(w, WING_D,         *_wp([(26,25),(42,18)]), 2)
    d.line(w, WING_D,         *_wp([(28,30),(44,25)]), 2)
    d.line(w, HL,             *_wp([(25,25),(41,15)]), 1)

    _wing_tape(w)

    # Punched as transparency rather than painted dark so the break survives
    # the outline pass and the 1x downscale. The toggle exists so the render
    # pass can diff a torn frame against an intact one and prove the tear is
    # not simply hiding behind the body.
    if tear:
        lip = pygame.Surface(w.get_size(), pygame.SRCALPHA)
        d.polygon(lip, TORN, _wp(_tear_lip(WING_TEAR)))
        _clip_to_wing(w, lip)
        d.polygon(w, (0,0,0,0), _wp(WING_TEAR))
    return pygame.transform.rotate(w, angle_deg)


GAUZE_QUAD = [(41, 10), (56, 13), (54, 22), (39, 19)]
CROSS_H    = ((46, 15), (52, 15))
CROSS_V    = ((49, 12), (49, 19))


def _draw_bandage(surf):
    """Gauze taped diagonally across the temple and *under* the shades — he put
    them back on after being patched up. Over the top it erased the shatter web
    and half the left lens, which is the one place that has to stay readable.

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
    posture cue, a tuft is just a hat."""
    _wisp(surf, [(41, 15), (39, 9), (37, 6)])
    _wisp(surf, [(47, 14), (47, 8), (47, 5)])
    _wisp(surf, [(52, 15), (54, 9), (56, 6)])


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


# Three radials only — 15-18% coverage target. Five radials + two web lines
# produced a bright mess; dropping to three (two at 2px, one at 1px) and one
# web line keeps the shatter readable without flooding the lens with light.
_RADIALS = ((38, 18), (49, 19), (42, 29))
_IMPACT  = (43, 23)


def _draw_cracked_lenses(surf):
    """Left lens shatters, right lens only sympathises. One wedge fill between
    the two longest radials; three crack lines, the two longest at 2px. At 1x
    a single-pixel crack on a seven-pixel lens is noise — the coverage limit
    keeps the dark field dominant so the lens reads as *glass* not confetti."""
    d = pygame.draw
    layer = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    # One wedge fill (between radials 0 and 1) — reduces coverage vs round 1
    d.polygon(layer, PLATE_A, [_IMPACT, _RADIALS[0], _RADIALS[1]])
    longest = sorted(_RADIALS,
                     key=lambda p: -math.hypot(p[0] - _IMPACT[0],
                                               p[1] - _IMPACT[1]))[:2]
    for end in _RADIALS:
        d.line(layer, CRACK, _IMPACT, end, 2 if end in longest else 1)
    d.line(layer, CRACK_WEB, (39, 19), (37, 25), 1)
    # Clipped to the rim rather than the glass: a fracture that runs right into
    # the frame is what real shattered glass does.
    _lens_clip(surf, layer, LENS_L, LENS_LR + 1)

    layer = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    d.line(layer, CRACK, (55, 19), (52, 16), 1)
    d.line(layer, CRACK, (55, 19), (58, 22), 1)
    _lens_clip(surf, layer, LENS_R, LENS_RR)


TAIL_TRUNCATE = 0.75
# Kicked up, away from the stack. Down is into the other three feathers, where
# a broken feather is a feather nobody can see: the fan is drawn back-to-front
# and the body ellipse lands on top of everything inboard of x~13.
TAIL_KICK_DEG = 15.0


def _tail_feather(pts, damaged=False):
    """Tail feathers run root-right, tip-left. The damaged one keeps three
    quarters of its length, is kicked off the fan axis, and ends in a notch
    rather than a clean edge — a shortened feather with a straight tip reads as
    a *smaller* feather, and the notch is what makes it read as a snapped one.

    It is the outermost feather on purpose. The three inboard ones are almost
    entirely behind the body ellipse — snapping one of those is a change only a
    pixel diff can find. The outer feather is the one that owns the fan's top
    outline, and outline damage is the only damage that survives 1x."""
    if not damaged:
        return pts
    root = ((pts[1][0] + pts[2][0]) / 2.0, (pts[1][1] + pts[2][1]) / 2.0)
    a = math.radians(TAIL_KICK_DEG)
    ca, sa = math.cos(a), math.sin(a)
    moved = []
    for i, (x, y) in enumerate(pts):
        if i in (0, 3):
            x = root[0] + (x - root[0]) * TAIL_TRUNCATE
            y = root[1] + (y - root[1]) * TAIL_TRUNCATE
        vx, vy = x - root[0], y - root[1]
        moved.append((root[0] + vx * ca - vy * sa, root[1] + vx * sa + vy * ca))
    tip_a, tip_b = moved[0], moved[3]
    mx, my = (tip_a[0] + tip_b[0]) / 2.0, (tip_a[1] + tip_b[1]) / 2.0
    dx, dy = root[0] - mx, root[1] - my
    L = max(1e-3, math.hypot(dx, dy))
    notch = (mx + dx / L * 3.0, my + dy / L * 3.0)
    return [moved[0], moved[1], moved[2], moved[3], notch]


def _build_hurt_frame(wing_angle_deg, tear=True, snap=True):
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
        d.polygon(surf, c, _tail_feather(pts, damaged=(snap and i == 0)))
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

    # Head hangs 1 px lower than the healthy build — small in absolute terms,
    # but it breaks the proud upward line of the original silhouette.
    _aaellipse(surf, (155, 15, 20), (48, 24), 12, 11)
    _aaellipse(surf, BODY,          (47, 22), 12, 11)
    _aaellipse(surf, (200, 90, 90), (44, 24),  4,  3)
    _aaellipse(surf, (230, 140, 140), (46, 17),  7,  3)

    _draw_head_wisps(surf)
    _draw_bandage(surf)
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
    passes happily while a dressing is being overpainted by the wing — each
    mark has to be proved present in its own region."""
    x0, y0, x1, y1 = box or (0, 0, SPRITE_W, SPRITE_H)
    n = 0
    for x in range(max(0, x0), min(x1, SPRITE_W)):
        for y in range(max(0, y0), min(y1, SPRITE_H)):
            r, g, b, a = frame.get_at((x, y))
            if a > 8 and pred(r, g, b):
                n += 1
    return n


def _tear_stats(torn, intact):
    """Two numbers, because they answer different questions. `changed` is how
    much of the sprite the wedge altered at all; `opened` is how much of it
    became sky. The wedge overlaps the body for part of the flap cycle, so
    `opened` alone would under-report a tear that is plainly visible as blue
    giving way to red."""
    changed = opened = 0
    for x in range(SPRITE_W):
        for y in range(SPRITE_H):
            a, b = torn.get_at((x, y)), intact.get_at((x, y))
            if a != b:
                changed += 1
                if a[3] <= 8 < b[3]:
                    opened += 1
    return changed, opened


def _strip(frames, bg):
    fw, fh = frames[0].get_size()
    s = pygame.Surface((len(frames) * fw, fh))
    s.fill(bg)
    for i, f in enumerate(frames):
        s.blit(f, (i * fw, 0))
    return s


if __name__ == "__main__":
    OUT_DIR = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(OUT_DIR, exist_ok=True)

    raw    = [_build_hurt_frame(a) for a in _HURT_ANGLES]
    notear = [_build_hurt_frame(a, tear=False) for a in _HURT_ANGLES]
    nosnap = [_build_hurt_frame(a, snap=False) for a in _HURT_ANGLES]
    frames = [_add_outline(f) for f in raw]

    is_white = lambda r, g, b: (r, g, b) in (GAUZE, PAD)
    is_glass = lambda r, g, b: (r, g, b) in (CRACK, CRACK_WEB, PLATE_A, PLATE_B)
    is_wisp  = lambda r, g, b: (r, g, b) in (WISP, WISP_TIP)
    is_cross = lambda r, g, b: (r, g, b) == CROSS

    strip = _strip(frames, (8, 8, 20))
    out_path = os.path.join(OUT_DIR, "round_2.png")
    pygame.image.save(strip, out_path)
    print(f"Saved {strip.get_width()}x{strip.get_height()} -> {out_path}")

    for idx, f in enumerate(raw):
        gauze = _count(f, is_white, (28, 4, 50, 28))
        tape  = _count(f, is_white) - gauze
        glass = _count(f, is_glass, (34, 14, 54, 34))
        wisps = _count(f, is_wisp,  (0, 0, SPRITE_W, 12))
        cross = _count(f, is_cross)
        changed, opened = _tear_stats(f, notear[idx])
        # For the tail the silhouette number is the only one worth having: the
        # snap is meant to be read as a broken outline, not as recoloured
        # pixels somewhere under the body.
        t_changed, t_sil = _tear_stats(f, nosnap[idx])
        flag = lambda ok: "ok " if ok else "LOW"
        print(f"f{idx}: gauze={gauze:3d} {flag(gauze >= 30)}  "
              f"glass={glass:3d} {flag(glass >= 80)}  "
              f"wisps={wisps:3d} {flag(wisps >= 30)}  "
              f"tear_changed={changed:3d} tear_opened={opened:3d} "
              f"{flag(changed >= 20)}  "
              f"snap_changed={t_changed:3d} snap_silhouette={t_sil:3d} "
              f"{flag(t_sil >= 20)}  tape={tape:3d} cross={cross:2d}")
