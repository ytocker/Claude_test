"""
Round-1 concept renderer for ZHENMUSHOU — the antlered sancai tomb-guardian
BEAST (Jiangshi-epic set, concept #2). Headless Pygame; supersample (SS=6) →
smoothscale, the elevated "epic" pipeline of this set (bigger render, more
geometry, richer triad, stronger glow than the Jiangshi source).

House grammar held from the lineage: chibi + scary-CUTE, flat saturated fills,
hard 1-2px ink keyline (28,22,30), dark-core -> flat-fill -> top-left rim-sheen
triad, 1px alpha-grown outline. Procedural only — no gradients/PNGs.

WHY a squat seated quadruped block: this is the ONLY beast in the lineage, so
the read must be bottom-heavy seated mass on straight forelegs — never the
upright humanoid box the rest of the set uses. The wide lion-mask face, two
upswept oxidized-red horns, and a back-fan of EXACTLY 5 triangular spine-plates
(bottom-rooted) carry the silhouette. Sancai owns a lane nobody else has:
cream-glaze base + an earned amber-glaze mid-band + a brown-OLIVE ceramic accent
(deliberately NOT leaf green, to stay clear of pine/yellow-green neighbours),
with a kiln-amber mouth glow. The pillar is the spine-spike stela: the same
triad-lit spike-plates stacked edge-on with sparse crackle-glaze banding, capped
at the gap by a smaller MIRRORED beast-mask with a glowing amber kiln-mouth —
bottom-rooted, on-axis, no top-heavy cap.

WHY standalone: review art must never enter the shipped bundle, so it lives
under docs/ and reuses only colour math, not runtime sprite modules.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
pygame.init()

# ── PINNED SANCAI PALETTE ─────────────────────────────────────────────────────
# The earned three-glaze lane: cream / amber / brown-olive. Each colour carries
# its own dark-core + rim-sheen helper so the flat triad reads on every mass.
CREAM     = (236, 220, 168)   # cream-glaze base (the dominant body mass)
CREAM_D   = (176, 154, 104)   # cream dark-core
CREAM_T   = (250, 240, 206)   # cream rim-sheen helper
AMBER     = (206, 142,  48)   # amber-glaze mid-band (earned extra band)
AMBER_D   = (150,  96,  30)   # amber dark-core
AMBER_T   = (240, 188,  92)   # amber rim-sheen helper / mouth-glow anchor
OLIVE     = ( 96,  96,  44)   # brown-OLIVE ceramic accent (NOT leaf green)
OLIVE_D   = ( 60,  62,  28)   # olive dark-core
OLIVE_T   = (140, 138,  78)   # olive rim-sheen helper
HORN      = (170,  56,  38)   # oxidized-red horn (thin LINEAR accent, never mass)
HORN_D    = (112,  34,  24)   # horn dark-core
HORN_T    = (208,  96,  66)   # horn rim-sheen
KILN      = (255, 176,  70)   # kiln-amber mouth glow (hot focal)
KILN_HOT  = (255, 226, 150)   # mouth glow hottest core
TOOTH     = (244, 236, 210)   # ivory fang / tusk
INK       = ( 28,  22,  30)   # hard ink keyline (locked)
EYE_GLOW  = (255, 198, 120)   # warm eye pinpoint

BG        = (104, 104, 104)   # neutral grey review backdrop
PANEL     = ( 84,  84,  84)
DAY_SKY   = (126, 196, 226)   # gameplay day sky
NIGHT_SKY = ( 28,  34,  62)   # gameplay night sky
LABEL     = (240, 240, 240)
LABEL_DIM = (196, 196, 196)


def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return (int(a[0] + (b[0]-a[0])*t),
            int(a[1] + (b[1]-a[1])*t),
            int(a[2] + (b[2]-a[2])*t))


# ── outline grown from the alpha mask (the house keyline) ────────────────────
def grow_outline(surf, color, px):
    mask = pygame.mask.from_surface(surf)
    outline_pts = mask.outline()
    if len(outline_pts) < 2:
        return surf
    base = surf.copy()
    ring = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    for (ox, oy) in outline_pts:
        pygame.draw.circle(ring, color, (ox, oy), px)
    ring.blit(base, (0, 0))
    return ring


def triad_blob(surf, color, pts, sheen_pts=None, core_pts=None, outline=True, ow=2):
    """Flat fill + optional dark-core + top-left rim-sheen + ink keyline."""
    if outline:
        pygame.draw.polygon(surf, INK, pts)
    pygame.draw.polygon(surf, color, pts)
    if core_pts:
        pygame.draw.polygon(surf, lerp(color, INK, 0.42), core_pts)
    if sheen_pts:
        pygame.draw.polygon(surf, lerp(color, (255, 255, 255), 0.35), sheen_pts)
    if outline:
        pygame.draw.polygon(surf, INK, pts, ow)


def kiln_glow(surf, cx, cy, r, s, strength=120):
    """Additive kiln-amber bloom — the hot focal that anchors the warm read on
    both day and night sky. WHY additive: keeps the glaze fills flat (no
    gradient) while still throwing real light at the mouth."""
    glow = pygame.Surface((r*4, r*4), pygame.SRCALPHA)
    for rr in range(r*2, 0, -1):
        a = int(strength * (1 - rr/(r*2)) ** 1.6)
        pygame.draw.circle(glow, (*KILN, a), (r*2, r*2), rr)
    surf.blit(glow, (cx-r*2, cy-r*2), special_flags=pygame.BLEND_ADD)


def spine_plate(surf, cx, base_y, w, h, s, lit=True):
    """One triangular spine-plate, bottom-rooted (wide base at base_y, apex up).
    Triad-lit: olive dark-core on the right flank, cream rim-sheen up the left.
    These same plates are stacked edge-on to BECOME the pillar shaft."""
    half = w // 2
    apex = (cx, base_y - h)
    bl   = (cx - half, base_y)
    br   = (cx + half, base_y)
    pts  = [apex, br, bl]
    pygame.draw.polygon(surf, INK, pts)
    pygame.draw.polygon(surf, AMBER if lit else OLIVE, pts)
    # dark-core on the right flank (away from the top-left light)
    pygame.draw.polygon(surf, AMBER_D if lit else OLIVE_D,
                        [apex, br, (cx + int(2*s), base_y)])
    # olive ridge groove up the centre — the ceramic accent, kept linear
    pygame.draw.line(surf, OLIVE_D, apex, (cx, base_y - int(2*s)), max(1, int(2*s)))
    # top-left rim-sheen flank
    pygame.draw.polygon(surf, AMBER_T if lit else OLIVE_T,
                        [apex, bl, (cx - half + int(5*s), base_y),
                         (cx - int(2*s), base_y - int(4*s))])
    pygame.draw.polygon(surf, INK, pts, max(2, int(2*s)))


def crackle(surf, x0, y0, x1, y1, s):
    """A sparse hard hairline crackle-glaze seam — drawn as a thin ink triad
    groove. Kept sparse per brief so seams never fuzz the form at 1x."""
    pygame.draw.line(surf, OLIVE_D, (x0, y0), (x1, y1), max(1, int(1.5*s)))


# ── the creature ─────────────────────────────────────────────────────────────
def draw_zhenmushou(surf, cx, cy, s):
    """Squat SEATED antlered sancai beast on straight forelegs. Bottom-heavy:
    the haunch + foreleg block is the widest, lowest mass; the wide lion-mask
    face sits on top with two upswept red horns; a bottom-rooted back-fan of
    EXACTLY 5 triangular spine-plates rises behind. `s` is a unit scale around a
    ~150-unit-tall figure."""

    # ── geometry anchors (defined up front so layers can key off them) ────────
    body_w  = int(96*s)
    body_h  = int(60*s)
    body_cx = cx
    body_cy = cy + int(22*s)               # seated mass sits LOW
    haunch_y = body_cy + int(8*s)
    ground_y = body_cy + int(46*s)         # where the forelegs plant

    # ── (1) back-fan of EXACTLY 5 spine-plates (drawn FIRST → behind body) ────
    # bottom-rooted: every plate's wide base sits on the spine line; apexes fan
    # outward. Centre plate tallest so the fan reads as a fan, not a fringe.
    spine_base = body_cy - int(6*s)
    fan = [
        (-int(40*s), int(34*s)),   # outer-left, short
        (-int(20*s), int(50*s)),   # inner-left, tall
        (   0,       int(60*s)),   # centre, tallest
        ( int(20*s), int(50*s)),   # inner-right, tall
        ( int(40*s), int(34*s)),   # outer-right, short
    ]
    pw = int(26*s)
    for dx, ph in fan:
        spine_plate(surf, body_cx + dx, spine_base, pw, ph, s, lit=True)

    # ── (2) haunches + straight forelegs (the bottom-heavy base block) ────────
    # Hind haunch — a rounded cream mound either side, low and wide.
    for sgn in (-1, 1):
        hx = body_cx + sgn*int(34*s)
        haunch = [
            (hx - sgn*int(6*s), haunch_y - int(20*s)),
            (hx + sgn*int(22*s), haunch_y - int(10*s)),
            (hx + sgn*int(24*s), ground_y),
            (hx - sgn*int(14*s), ground_y),
        ]
        triad_blob(
            surf, CREAM, haunch,
            core_pts=[(hx + sgn*int(8*s), haunch_y - int(2*s)),
                      (hx + sgn*int(22*s), haunch_y - int(6*s)),
                      (hx + sgn*int(24*s), ground_y),
                      (hx + sgn*int(6*s), ground_y)],
            sheen_pts=[(hx - sgn*int(4*s), haunch_y - int(17*s)),
                       (hx + sgn*int(6*s), haunch_y - int(13*s)),
                       (hx + sgn*int(6*s), haunch_y + int(4*s)),
                       (hx - sgn*int(8*s), haunch_y + int(2*s))],
            ow=max(2, int(2.4*s)),
        )

    # straight forelegs planted at front (the "seated on straight forelegs" tell)
    for sgn in (-1, 1):
        lx = body_cx + sgn*int(26*s)
        leg = [
            (lx - int(9*s), haunch_y + int(2*s)),
            (lx + int(9*s), haunch_y + int(2*s)),
            (lx + int(11*s), ground_y + int(20*s)),
            (lx - int(11*s), ground_y + int(20*s)),
        ]
        triad_blob(
            surf, CREAM, leg,
            core_pts=[(lx + int(2*s), haunch_y + int(2*s)),
                      (lx + int(9*s), haunch_y + int(2*s)),
                      (lx + int(11*s), ground_y + int(20*s)),
                      (lx + int(2*s), ground_y + int(20*s))],
            sheen_pts=[(lx - int(7*s), haunch_y + int(4*s)),
                       (lx - int(1*s), haunch_y + int(4*s)),
                       (lx - int(1*s), ground_y + int(16*s)),
                       (lx - int(7*s), ground_y + int(16*s))],
            ow=max(2, int(2.2*s)),
        )
        # cloven hoof / clawed paw block at the foot — amber-banded
        paw = [(lx - int(13*s), ground_y + int(14*s)),
               (lx + int(13*s), ground_y + int(14*s)),
               (lx + int(14*s), ground_y + int(24*s)),
               (lx - int(14*s), ground_y + int(24*s))]
        triad_blob(surf, AMBER, paw, ow=max(2, int(2*s)))
        # three claw splits
        for i in (-1, 0, 1):
            ncx = lx + i*int(7*s)
            pygame.draw.line(surf, INK, (ncx, ground_y + int(15*s)),
                             (ncx, ground_y + int(24*s)), max(1, int(1.6*s)))

    # ── (3) body / chest block — cream base with an EARNED amber mid-band ─────
    body = [
        (body_cx - body_w//2, body_cy - body_h//2 + int(6*s)),
        (body_cx + body_w//2, body_cy - body_h//2 + int(6*s)),
        (body_cx + body_w//2 + int(2*s), body_cy + body_h//2),
        (body_cx - body_w//2 - int(2*s), body_cy + body_h//2),
    ]
    triad_blob(
        surf, CREAM, body,
        core_pts=[(body_cx, body_cy - int(6*s)),
                  (body_cx + body_w//2, body_cy - int(10*s)),
                  (body_cx + body_w//2, body_cy + body_h//2),
                  (body_cx, body_cy + body_h//2)],
        sheen_pts=[(body_cx - body_w//2 + int(4*s), body_cy - body_h//2 + int(8*s)),
                   (body_cx - int(6*s), body_cy - body_h//2 + int(8*s)),
                   (body_cx - int(6*s), body_cy + int(2*s)),
                   (body_cx - body_w//2 + int(4*s), body_cy - int(2*s))],
        ow=max(2, int(2.6*s)),
    )
    # the earned amber-glaze mid-band across the chest (sancai's middle colour)
    band_y = body_cy - int(2*s)
    band_h = int(16*s)
    bx0 = body_cx - body_w//2 + int(3*s)
    bw  = body_w - int(6*s)
    pygame.draw.rect(surf, AMBER, (bx0, band_y, bw, band_h))
    pygame.draw.rect(surf, AMBER_D, (bx0, band_y + band_h - int(4*s), bw, int(4*s)))
    pygame.draw.rect(surf, AMBER_T, (bx0, band_y, bw, int(3*s)))
    pygame.draw.rect(surf, INK, (bx0, band_y, bw, band_h), max(1, int(1.6*s)))
    # sparse crackle-glaze seams on the chest (kept few)
    crackle(surf, body_cx - int(20*s), body_cy - int(18*s),
            body_cx - int(14*s), band_y, s)
    crackle(surf, body_cx + int(16*s), body_cy - int(20*s),
            body_cx + int(22*s), band_y, s)

    # ── (4) the WIDE lion-mask face (the dominant top read) ───────────────────
    face_cx = body_cx
    face_cy = body_cy - int(58*s)
    face_w  = int(86*s)
    face_h  = int(64*s)
    face = [
        (face_cx - face_w//2, face_cy - int(10*s)),
        (face_cx - face_w//2 + int(8*s), face_cy - face_h//2),
        (face_cx + face_w//2 - int(8*s), face_cy - face_h//2),
        (face_cx + face_w//2, face_cy - int(10*s)),
        (face_cx + face_w//2 - int(6*s), face_cy + face_h//2),
        (face_cx + int(16*s), face_cy + face_h//2 + int(6*s)),
        (face_cx - int(16*s), face_cy + face_h//2 + int(6*s)),
        (face_cx - face_w//2 + int(6*s), face_cy + face_h//2),
    ]
    triad_blob(
        surf, CREAM, face,
        core_pts=[(face_cx, face_cy - int(6*s)),
                  (face_cx + face_w//2, face_cy - int(6*s)),
                  (face_cx + face_w//2 - int(6*s), face_cy + face_h//2),
                  (face_cx, face_cy + face_h//2 + int(4*s))],
        sheen_pts=[(face_cx - face_w//2 + int(6*s), face_cy - int(6*s)),
                   (face_cx - int(4*s), face_cy - face_h//2 + int(4*s)),
                   (face_cx - int(4*s), face_cy + int(6*s)),
                   (face_cx - face_w//2 + int(8*s), face_cy + int(10*s))],
        ow=max(2, int(2.8*s)),
    )

    # olive ceramic ear-flowers blooming from the sides (the accent, kept linear)
    for sgn in (-1, 1):
        ex = face_cx + sgn*int(46*s)
        ey = face_cy - int(6*s)
        ear = [(ex - sgn*int(4*s), ey - int(16*s)),
               (ex + sgn*int(16*s), ey - int(8*s)),
               (ex + sgn*int(12*s), ey + int(10*s)),
               (ex - sgn*int(6*s), ey + int(12*s))]
        triad_blob(surf, OLIVE, ear,
                   core_pts=[(ex + sgn*int(4*s), ey - int(4*s)),
                             (ex + sgn*int(16*s), ey - int(8*s)),
                             (ex + sgn*int(12*s), ey + int(10*s)),
                             (ex + sgn*int(2*s), ey + int(10*s))],
                   sheen_pts=[(ex - sgn*int(2*s), ey - int(13*s)),
                              (ex + sgn*int(4*s), ey - int(9*s)),
                              (ex + sgn*int(4*s), ey + int(2*s)),
                              (ex - sgn*int(2*s), ey + int(2*s))],
                   ow=max(2, int(2*s)))

    # heavy ink brow ridge (fierce-cute) over big sunken sockets
    pygame.draw.line(surf, INK,
                     (face_cx - int(30*s), face_cy - int(18*s)),
                     (face_cx - int(4*s), face_cy - int(10*s)), max(2, int(4*s)))
    pygame.draw.line(surf, INK,
                     (face_cx + int(30*s), face_cy - int(18*s)),
                     (face_cx + int(4*s), face_cy - int(10*s)), max(2, int(4*s)))

    # big round eyes — amber iris, warm pinpoint, scary-CUTE (large + bright)
    for sgn in (-1, 1):
        ex = face_cx + sgn*int(20*s)
        ey = face_cy - int(2*s)
        pygame.draw.circle(surf, INK, (ex, ey), int(13*s))
        pygame.draw.circle(surf, CREAM_T, (ex, ey), int(11*s))
        pygame.draw.circle(surf, AMBER, (ex, ey), int(9*s))
        pygame.draw.circle(surf, INK, (ex, ey), int(5*s))
        pygame.draw.circle(surf, EYE_GLOW, (ex - int(2*s), ey - int(2*s)), int(3*s))
        pygame.draw.circle(surf, (255, 255, 255),
                           (ex - int(3*s), ey - int(3*s)), max(1, int(1.4*s)))

    # broad flat snout / nose pad
    snout = [(face_cx - int(12*s), face_cy + int(10*s)),
             (face_cx + int(12*s), face_cy + int(10*s)),
             (face_cx + int(10*s), face_cy + int(22*s)),
             (face_cx - int(10*s), face_cy + int(22*s))]
    triad_blob(surf, AMBER, snout,
               core_pts=[(face_cx, face_cy + int(10*s)),
                         (face_cx + int(12*s), face_cy + int(10*s)),
                         (face_cx + int(10*s), face_cy + int(22*s)),
                         (face_cx, face_cy + int(22*s))],
               ow=max(2, int(2*s)))
    for sgn in (-1, 1):
        pygame.draw.circle(surf, INK,
                           (face_cx + sgn*int(5*s), face_cy + int(17*s)), int(3*s))

    # ── (5) the kiln-amber MOUTH GLOW (hot focal) — drawn over the lower face ─
    mouth_cy = face_cy + int(34*s)
    kiln_glow(surf, face_cx, mouth_cy, int(20*s), s, strength=150)
    mouth = [(face_cx - int(22*s), mouth_cy - int(6*s)),
             (face_cx + int(22*s), mouth_cy - int(6*s)),
             (face_cx + int(16*s), mouth_cy + int(12*s)),
             (face_cx - int(16*s), mouth_cy + int(12*s))]
    pygame.draw.polygon(surf, INK, mouth)
    pygame.draw.polygon(surf, KILN, mouth)
    pygame.draw.polygon(surf, KILN_HOT,
                        [(face_cx - int(14*s), mouth_cy - int(2*s)),
                         (face_cx + int(14*s), mouth_cy - int(2*s)),
                         (face_cx + int(9*s), mouth_cy + int(7*s)),
                         (face_cx - int(9*s), mouth_cy + int(7*s))])
    pygame.draw.polygon(surf, INK, mouth, max(2, int(2*s)))
    # ivory fangs over the glow (top + bottom rows, scary-cute)
    for i in (-1, 1):
        fx = face_cx + i*int(13*s)
        pygame.draw.polygon(surf, TOOTH,
                            [(fx - int(4*s), mouth_cy - int(6*s)),
                             (fx + int(4*s), mouth_cy - int(6*s)),
                             (fx, mouth_cy + int(4*s))])
        pygame.draw.polygon(surf, INK,
                            [(fx - int(4*s), mouth_cy - int(6*s)),
                             (fx + int(4*s), mouth_cy - int(6*s)),
                             (fx, mouth_cy + int(4*s))], max(1, int(1.4*s)))
    # tusks curling up at the corners
    for sgn in (-1, 1):
        tx = face_cx + sgn*int(20*s)
        pygame.draw.polygon(surf, TOOTH,
                            [(tx, mouth_cy - int(4*s)),
                             (tx + sgn*int(6*s), mouth_cy - int(14*s)),
                             (tx + sgn*int(2*s), mouth_cy - int(2*s))])
        pygame.draw.polygon(surf, INK,
                            [(tx, mouth_cy - int(4*s)),
                             (tx + sgn*int(6*s), mouth_cy - int(14*s)),
                             (tx + sgn*int(2*s), mouth_cy - int(2*s))], max(1, int(1.4*s)))

    # ── (6) two upswept oxidized-red HORNS (thin linear accent, never a mass) ─
    for sgn in (-1, 1):
        rx = face_cx + sgn*int(22*s)
        ry = face_cy - int(30*s)
        horn = [
            (rx, ry + int(6*s)),
            (rx + sgn*int(6*s), ry - int(2*s)),
            (rx + sgn*int(20*s), ry - int(34*s)),
            (rx + sgn*int(28*s), ry - int(56*s)),
            (rx + sgn*int(22*s), ry - int(54*s)),
            (rx + sgn*int(13*s), ry - int(30*s)),
            (rx - sgn*int(2*s), ry - int(2*s)),
        ]
        triad_blob(
            surf, HORN, horn,
            core_pts=[(rx + sgn*int(2*s), ry + int(2*s)),
                      (rx + sgn*int(20*s), ry - int(34*s)),
                      (rx + sgn*int(28*s), ry - int(56*s)),
                      (rx + sgn*int(24*s), ry - int(54*s)),
                      (rx + sgn*int(13*s), ry - int(30*s))],
            ow=max(2, int(2.2*s)),
        )
        # horn ridge ribs (the elevated detail, kept as thin linear grooves)
        for t in (0.3, 0.55, 0.78):
            hx = int(rx + sgn*(6 + (22)*t)*s)
            hy = int(ry - (2 + 52*t)*s)
            pygame.draw.line(surf, HORN_D, (hx - sgn*int(3*s), hy),
                             (hx + sgn*int(3*s), hy - int(2*s)), max(1, int(1.6*s)))
        # bright rim-sheen up the front of the horn
        pygame.draw.line(surf, HORN_T,
                         (rx + sgn*int(2*s), ry),
                         (rx + sgn*int(24*s), ry - int(50*s)), max(1, int(2*s)))


# ── the spine-spike stela pillar (creature-derived; clean tileable shaft) ─────
def draw_pillar_segment(surf, cx, top, bot, s, cap_at=None):
    """Spine-spike stela: a column of the same triad-lit triangular spike-plates
    stacked edge-on, with sparse crackle-glaze banding — a clean tileable shaft.
    `cap_at` ('top' or 'bottom') places a smaller MIRRORED beast-mask with a
    glowing amber kiln-mouth at the gap edge. Bottom-rooted, on-axis."""
    shaft_w = int(34*s)
    x0 = cx - shaft_w//2
    # core cream shaft with an olive shade flank + cream rim-sheen flank (triad)
    pygame.draw.rect(surf, INK, (x0-1, top, shaft_w+2, bot-top))
    pygame.draw.rect(surf, CREAM, (x0, top, shaft_w, bot-top))
    pygame.draw.rect(surf, OLIVE_D, (x0 + shaft_w - int(8*s), top, int(8*s), bot-top))
    pygame.draw.rect(surf, CREAM_T, (x0, top, int(6*s), bot-top))

    # stacked edge-on spike-plates running the length — the spine continued.
    # each plate points AWAY from the gap so the shaft reads as a spine ridge.
    point_dir = 1 if cap_at == "top" else -1     # apex points toward the root
    pitch = int(30*s)
    plate_w = shaft_w + int(10*s)
    y = top + int(14*s)
    band_toggle = 0
    while y < bot - int(10*s):
        half = plate_w // 2
        if point_dir < 0:
            apex = (cx, y + int(20*s)); a = (cx - half, y); b = (cx + half, y)
        else:
            apex = (cx, y - int(6*s)); a = (cx - half, y + int(14*s)); b = (cx + half, y + int(14*s))
        pts = [apex, b, a]
        col   = AMBER if band_toggle % 2 == 0 else CREAM
        col_d = AMBER_D if band_toggle % 2 == 0 else CREAM_D
        col_t = AMBER_T if band_toggle % 2 == 0 else CREAM_T
        pygame.draw.polygon(surf, INK, pts)
        pygame.draw.polygon(surf, col, pts)
        pygame.draw.polygon(surf, col_d, [apex, b, (apex[0]+int(2*s), b[1])])
        pygame.draw.line(surf, OLIVE_D, apex, ((a[0]+b[0])//2, a[1]), max(1, int(1.6*s)))
        pygame.draw.polygon(surf, col_t,
                            [apex, a, (a[0]+int(5*s), a[1]), (apex[0]-int(2*s), apex[1]+int(4*s))])
        pygame.draw.polygon(surf, INK, pts, max(2, int(2*s)))
        # sparse crackle-glaze seam on alternating plates only (kept sparse)
        if band_toggle % 2 == 1:
            crackle(surf, cx - int(8*s), y + int(4*s), cx - int(2*s), y + int(12*s), s)
        y += pitch
        band_toggle += 1

    # ── the mirrored beast-mask gap-cap (smaller; glowing amber kiln-mouth) ───
    if cap_at:
        my = bot - int(26*s) if cap_at == "bottom" else top + int(26*s)
        flip = 1 if cap_at == "bottom" else -1   # mirror about the mask centre
        mw, mh = int(56*s), int(40*s)
        mask = [
            (cx - mw//2, my - flip*int(8*s)),
            (cx - mw//2 + int(6*s), my - flip*mh//2),
            (cx + mw//2 - int(6*s), my - flip*mh//2),
            (cx + mw//2, my - flip*int(8*s)),
            (cx + mw//2 - int(4*s), my + flip*mh//2),
            (cx, my + flip*(mh//2 + int(4*s))),
            (cx - mw//2 + int(4*s), my + flip*mh//2),
        ]
        triad_blob(
            surf, CREAM, mask,
            core_pts=[(cx, my), (cx + mw//2, my - flip*int(4*s)),
                      (cx + mw//2 - int(4*s), my + flip*mh//2),
                      (cx, my + flip*(mh//2 + int(2*s)))],
            ow=max(2, int(2.4*s)),
        )
        # two small upswept red horns on the cap (echo the hero)
        for sgn in (-1, 1):
            hx = cx + sgn*int(16*s)
            hy = my - flip*int(16*s)
            pygame.draw.polygon(surf, INK,
                                [(hx, hy),
                                 (hx + sgn*int(12*s), hy - flip*int(22*s)),
                                 (hx + sgn*int(7*s), hy - flip*int(2*s))])
            pygame.draw.polygon(surf, HORN,
                                [(hx, hy),
                                 (hx + sgn*int(11*s), hy - flip*int(20*s)),
                                 (hx + sgn*int(7*s), hy - flip*int(2*s))])
        # two eyes
        for sgn in (-1, 1):
            ex = cx + sgn*int(13*s)
            ey = my - flip*int(2*s)
            pygame.draw.circle(surf, INK, (ex, ey), int(7*s))
            pygame.draw.circle(surf, AMBER, (ex, ey), int(5*s))
            pygame.draw.circle(surf, EYE_GLOW, (ex - int(1*s), ey - int(1*s)), int(2*s))
        # the glowing amber kiln-mouth at the gap edge
        gy = my + flip*int(16*s)
        kiln_glow(surf, cx, gy, int(15*s), s, strength=150)
        mo = [(cx - int(15*s), gy - flip*int(4*s)),
              (cx + int(15*s), gy - flip*int(4*s)),
              (cx + int(10*s), gy + flip*int(9*s)),
              (cx - int(10*s), gy + flip*int(9*s))]
        pygame.draw.polygon(surf, INK, mo)
        pygame.draw.polygon(surf, KILN, mo)
        pygame.draw.polygon(surf, KILN_HOT,
                            [(cx - int(9*s), gy - flip*int(1*s)),
                             (cx + int(9*s), gy - flip*int(1*s)),
                             (cx, gy + flip*int(6*s))])
        pygame.draw.polygon(surf, INK, mo, max(1, int(1.6*s)))
        for i in (-1, 1):
            fx = cx + i*int(8*s)
            pygame.draw.polygon(surf, TOOTH,
                                [(fx - int(3*s), gy - flip*int(4*s)),
                                 (fx + int(3*s), gy - flip*int(4*s)),
                                 (fx, gy + flip*int(3*s))])


# ── compose the review sheet ─────────────────────────────────────────────────
SS = 6


def render_creature(boxw, boxh, draw_cx, draw_cy, scale):
    big = pygame.Surface((boxw*SS, boxh*SS), pygame.SRCALPHA)
    draw_zhenmushou(big, draw_cx*SS, draw_cy*SS, scale*SS)
    small = pygame.transform.smoothscale(big, (boxw, boxh))
    return grow_outline(small, INK + (255,), 1)


def render_pillar(boxw, boxh, top, bot, scale, cap_at):
    big = pygame.Surface((boxw*SS, boxh*SS), pygame.SRCALPHA)
    draw_pillar_segment(big, (boxw//2)*SS, top*SS, bot*SS, scale*SS, cap_at=cap_at)
    small = pygame.transform.smoothscale(big, (boxw, boxh))
    return grow_outline(small, INK + (255,), 1)


def main():
    W, H = 1000, 860
    font_big = pygame.font.SysFont("DejaVu Sans", 30, bold=True)
    font = pygame.font.SysFont("DejaVu Sans", 17, bold=True)
    font_sm = pygame.font.SysFont("DejaVu Sans", 12)

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    pygame.draw.rect(sheet, PANEL, (0, 0, W, 56))
    sheet.blit(font_big.render("ZHENMUSHOU", True, LABEL), (24, 12))
    sheet.blit(font_sm.render(
        "antlered sancai tomb-guardian beast  ·  cream + amber + brown-olive + oxidized-red horns + kiln-amber mouth  ·  round 1",
        True, LABEL_DIM), (250, 24))

    # ── (a) BIG hero sprite ───────────────────────────────────────────────────
    hero = render_creature(360, 470, 180, 215, 1.55)
    sheet.blit(hero, (12, 78))
    sheet.blit(font.render("Hero — seated antlered beast", True, LABEL), (60, 548))
    sheet.blit(font_sm.render("bottom-heavy seated mass on straight forelegs; wide lion-mask;", True, LABEL_DIM), (16, 572))
    sheet.blit(font_sm.render("2 upswept red horns; back-fan of EXACTLY 5 spine-plates", True, LABEL_DIM), (16, 588))

    # ── (b) pillar assembled — top + gap + bottom, MIRRORED ───────────────────
    px = 392
    pygame.draw.rect(sheet, PANEL, (px, 78, 196, 700))
    sheet.blit(font.render("Pillar — mirrored", True, LABEL), (px+14, 86))
    pcx = px + 98
    # top segment: cap faces DOWN into the gap (so its mouth glows at the gap)
    top_seg = render_pillar(160, 250, 4, 246, 1.0, cap_at="bottom")
    sheet.blit(top_seg, (pcx - 80, 114))
    # gap
    gap_top = 114 + 250
    gap_h = 96
    # bottom segment: MIRRORED — cap faces UP into the gap
    bot_seg = render_pillar(160, 300, 4, 296, 1.0, cap_at="top")
    sheet.blit(bot_seg, (pcx - 80, gap_top + gap_h))
    sheet.blit(font_sm.render("stacked spike-plate shaft +", True, LABEL_DIM), (px+10, 760))
    sheet.blit(font_sm.render("mirrored beast-mask gap-caps", True, LABEL_DIM), (px+10, 776))

    # ── (c) TRUE 32px gameplay chips on day + night sky ───────────────────────
    rx = 612
    pygame.draw.rect(sheet, PANEL, (rx, 78, 376, 360))
    sheet.blit(font.render("32px gameplay chip", True, LABEL), (rx+16, 86))
    sheet.blit(font_sm.render("true gameplay scale — does the seated beast read?", True, LABEL_DIM), (rx+16, 110))

    # day
    chip_day = render_creature(64, 84, 32, 40, (32/170.0))
    pygame.draw.rect(sheet, DAY_SKY, (rx+40, 140, 160, 200))
    sheet.blit(chip_day, (rx+40 + 48, 196))
    # show a 32px pillar gap-cap chip beside it on day
    pchip_day = render_pillar(40, 130, 2, 128, (32/100.0), cap_at="bottom")
    sheet.blit(pchip_day, (rx+40 + 110, 170))
    sheet.blit(font_sm.render("DAY", True, LABEL), (rx+40 + 70, 344))

    # night
    chip_night = render_creature(64, 84, 32, 40, (32/170.0))
    pygame.draw.rect(sheet, NIGHT_SKY, (rx+220, 140, 140, 200))
    sheet.blit(chip_night, (rx+220 + 40, 196))
    pchip_night = render_pillar(40, 130, 2, 128, (32/100.0), cap_at="bottom")
    sheet.blit(pchip_night, (rx+220 + 96, 170))
    sheet.blit(font_sm.render("NIGHT", True, LABEL), (rx+220 + 56, 344))

    # ── palette swatch row ────────────────────────────────────────────────────
    pygame.draw.rect(sheet, PANEL, (rx, 452, 376, 326))
    sheet.blit(font.render("Pinned sancai palette", True, LABEL), (rx+16, 460))
    swatches = [
        (CREAM, "cream-glaze base"), (CREAM_D, "cream dark-core"),
        (AMBER, "amber mid-band"), (AMBER_D, "amber dark-core"),
        (OLIVE, "brown-olive accent"), (OLIVE_D, "olive dark-core"),
        (HORN, "oxidized-red horn"), (HORN_T, "horn rim-sheen"),
        (KILN, "kiln-amber glow"), (KILN_HOT, "kiln hot-core"),
        (TOOTH, "ivory fang"), (INK, "ink keyline"),
    ]
    sx, sy = rx+16, 494
    for i, (c, name) in enumerate(swatches):
        col = i % 2
        row = i // 2
        bx = sx + col*180
        by = sy + row*44
        pygame.draw.rect(sheet, INK, (bx-1, by-1, 26, 26))
        pygame.draw.rect(sheet, c, (bx, by, 24, 24))
        sheet.blit(font_sm.render(name, True, LABEL), (bx+32, by+1))
        sheet.blit(font_sm.render("%d,%d,%d" % c, True, LABEL_DIM), (bx+32, by+14))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
