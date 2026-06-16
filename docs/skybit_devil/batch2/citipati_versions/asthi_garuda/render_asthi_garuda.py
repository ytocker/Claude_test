"""
Round-1 concept renderer for ASTHI-GARUDA — the bone-winged charnel sky-eater
(Citipati-versions set, concept #4). Headless Pygame; ELEVATED pipeline
(supersample SS=6 → smoothscale) so the tiered quill geometry stays crisp at
downscale. Keeps the shipped house grammar: flat fills, hard 1-2px ink keyline,
dark-core → flat-fill → top-left rim-sheen triad, 1px alpha-grown outline,
chibi proportions, scary-CUTE; procedural-only (no gradients/PNGs).

WHY this is the SPREAD-WING / BEAKED-SKULL of the brood: the roster is
skeleton-dense, so Asthi-Garuda is deliberately the ONLY aerial X-silhouette
and the ONLY beaked skull. The top read is a hard X — a beaked bone-skull
centred over two tiered fans of RIGID quill-BLADES (bone splines, never Pazul's
faceted membranes). The cross-set bone-cast rule is honoured by VALUE/HUE: the
bone carries a LAVENDER cast pushed up so the blood-orange beak pops, but it
stays DESATURATED so it never reads as Necrarch's saturated robe-violet — the
violet lives in the bone, never as a glow. Blood-orange is the SOLE glow, in the
beak gape + eye sockets only.

WHY the perch-totem IS the pillar: a banded bone perch-pole wound with quill
rings (a continuation of the wing-quill motif) tiles as the repeatable shaft; a
single wing-skull cap — wings half-FOLDED into a hard scalloped fan, beak/eye
glowing, talons gripping toward the gap line — is the creature-derived gap-edge
cap. Bottom-weighted (talons + beak hang toward the gap), on-axis, symmetric.

WHY a standalone script under docs/: review art must never enter the shipped
bundle, so it imports nothing from game.* — only colour math + the triad/outline
helpers cloned from the lineage template.
"""
import math
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
pygame.init()

# ── PINNED PALETTE (locked brief) ─────────────────────────────────────────────
# Dusk-violet-grey bone is the dominant mass; lavender cast pushed UP so the
# blood-orange beak pops, but kept DESATURATED so it never tips into Necrarch's
# saturated robe-violet. The violet lives in the BONE, never in a glow.
BONE      = (186, 176, 196)   # dusk-violet-grey bone (the dominant fill)
BONE_D    = (118, 108, 134)   # deep-slate-violet bone shade / dark-core
BONE_DD   = ( 78,  70,  96)   # deepest bone hollow (sockets, quill gaps)
BONE_SH   = (232, 228, 238)   # pale-quill rim-sheen / highlight
QUILL_HI  = (232, 228, 238)   # pale-quill highlight (named for clarity at use)
SHEEN     = (244, 240, 248)   # hottest bone sheen
GLOW      = (238, 114,  52)   # blood-orange beak + eye glow (the SOLE glow)
GLOW_BR   = (255, 176,  96)   # hot inner glow
GLOW_HOT  = (255, 224, 168)   # hottest glow core
RUST      = (170,  66,  34)   # rust shade under the glow
INK       = ( 26,  24,  30)   # hard ink keyline

BG        = ( 92,  88, 100)   # neutral grey-violet review backdrop
PANEL     = ( 72,  68,  82)
DAY_SKY_T = (120, 196, 236)   # day biome sky (top)
DAY_SKY_B = (196, 232, 244)
NIGHT_T   = ( 22,  26,  54)   # night biome sky (top)
NIGHT_B   = ( 48,  44,  82)
LABEL     = (238, 240, 244)
LABEL_DIM = (190, 196, 208)


def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return (int(a[0] + (b[0]-a[0])*t),
            int(a[1] + (b[1]-a[1])*t),
            int(a[2] + (b[2]-a[2])*t))


# ── outline grown from the alpha mask (the house keyline) ────────────────────
def grow_outline(surf, color, px):
    mask = pygame.mask.from_surface(surf)
    pts = mask.outline()
    if len(pts) < 2:
        return surf
    base = surf.copy()
    ring = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    for (ox, oy) in pts:
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
        pygame.draw.polygon(surf, lerp(color, (255, 255, 255), 0.4), sheen_pts)
    if outline:
        pygame.draw.polygon(surf, INK, pts, ow)


def triad_circle(surf, color, c, r, ow=2, sheen=True, core=True):
    """Round equivalent of triad_blob — dark core bottom-right, sheen top-left."""
    pygame.draw.circle(surf, INK, c, r + max(1, ow // 2))
    pygame.draw.circle(surf, color, c, r)
    if core:
        pygame.draw.circle(surf, lerp(color, INK, 0.4),
                           (c[0] + int(r * 0.28), c[1] + int(r * 0.30)),
                           int(r * 0.74))
        pygame.draw.circle(surf, color, c, int(r * 0.82))
    if sheen:
        pygame.draw.circle(surf, lerp(color, (255, 255, 255), 0.45),
                           (c[0] - int(r * 0.38), c[1] - int(r * 0.40)),
                           max(1, int(r * 0.26)))
    pygame.draw.circle(surf, INK, c, r, ow)


# ── a single RIGID quill-BLADE (the hard tell — bone spline, not a membrane) ──
def quill_blade(surf, root, ang, length, width, s, lit_tip=False):
    """One rigid tapered bone quill: a hard lens-shaped spline rooted at `root`,
    swept along `ang`, narrowing to a sharp tip. WHY a hard spline and not a
    webbed membrane: this is the cross-set TELL — Asthi-Garuda's wings are tiered
    HARD quill-BLADES (rigid bone), explicitly NOT Pazul's faceted membranes. A
    central dark shaft groove + a pale-quill leading-edge sheen sell it as bone,
    not skin. Each blade is its own closed polygon so sky reads BETWEEN blades."""
    ca, sa = math.cos(ang), math.sin(ang)
    # perpendicular for the blade width
    px, py = -sa, ca
    tip = (root[0] + ca * length, root[1] + sa * length)
    belly = 0.42 * length            # widest point sits out from the root
    bx = (root[0] + ca * belly, root[1] + sa * belly)
    hw = width * 0.5
    # a four-point lens that tapers to a sharp tip (rigid feather/blade read)
    blade = [
        (root[0] + px * hw * 0.55, root[1] + py * hw * 0.55),
        (bx[0] + px * hw, bx[1] + py * hw),
        tip,
        (bx[0] - px * hw, bx[1] - py * hw),
        (root[0] - px * hw * 0.55, root[1] - py * hw * 0.55),
    ]
    pygame.draw.polygon(surf, INK, blade)
    pygame.draw.polygon(surf, BONE, blade)
    # dark-core down the trailing half (toward the body) so the blade has volume
    core = [
        (root[0] - px * hw * 0.30, root[1] - py * hw * 0.30),
        (bx[0] - px * hw * 0.55, bx[1] - py * hw * 0.55),
        tip,
        (bx[0] - px * hw * 0.10, bx[1] - py * hw * 0.10),
    ]
    pygame.draw.polygon(surf, BONE_D, core)
    # pale-quill leading-edge sheen (top-left lit edge → the rigid bone read)
    lead = [
        (root[0] + px * hw * 0.40, root[1] + py * hw * 0.40),
        (bx[0] + px * hw * 0.78, bx[1] + py * hw * 0.78),
        tip,
    ]
    pygame.draw.polygon(surf, QUILL_HI, lead)
    # central shaft groove — the hard quill rib
    pygame.draw.line(surf, BONE_DD, (bx[0], bx[1]), tip, max(1, int(width * 0.10)))
    pygame.draw.polygon(surf, INK, blade, max(1, int(width * 0.12)))
    if lit_tip:
        pygame.draw.circle(surf, GLOW, (int(tip[0]), int(tip[1])), max(1, int(width * 0.16)))


def scalloped_fan(surf, root, base_ang, spread, n, length, width, s, tier_drop=0.0):
    """A tiered fan of rigid quill-blades sweeping from `root`. WHY scalloped &
    tiered: the wing silhouette reads as a hard scalloped edge (bone splines), and
    a second shorter inner tier gives the layered-feather depth without any
    membrane webbing. Returns nothing; draws longest blades first so the inner
    tier overlaps cleanly toward the body."""
    # outer (long) tier
    for i in range(n):
        t = i / max(1, n - 1)
        a = base_ang - spread * 0.5 + spread * t
        # quills lengthen toward the wrist (mid of the arc) for a wing taper
        taper = 1.0 - abs(t - 0.5) * 0.7
        quill_blade(surf, root, a, length * (0.62 + 0.38 * taper), width, s)
    # inner (short) tier nested between the outer blades — the scallop layering
    for i in range(n - 1):
        t = (i + 0.5) / max(1, n - 1)
        a = base_ang - spread * 0.5 + spread * t
        taper = 1.0 - abs(t - 0.5) * 0.7
        quill_blade(surf, root, a, length * (0.40 + 0.26 * taper), width * 0.82, s)


# ── the beaked bone-skull (vulture head — reused for hero + pillar cap) ───────
def bird_skull(surf, cx, cy, r, s, lit=True, agape=True):
    """A grumpy little bone-vulture skull: a domed lavender-grey cranium, a heavy
    hooked BEAK that is the unmistakable read (the ONLY beaked skull in the
    roster), and two deep sockets pinned with blood-orange glow. `agape` cracks
    the beak open (the sky-eater gape); `lit` lights the gape + sockets."""
    # cranium dome (the bone mass that owns the silhouette centre)
    triad_circle(surf, BONE, (cx, cy), r, ow=max(1, int(1.8 * s)), core=False)
    # a low brow ridge sweeping forward over the eyes — the grumpy vulture scowl
    brow = [(cx - int(r * 0.92), cy - int(r * 0.10)),
            (cx + int(r * 0.92), cy - int(r * 0.10)),
            (cx + int(r * 0.70), cy + int(r * 0.18)),
            (cx - int(r * 0.70), cy + int(r * 0.18))]
    triad_blob(surf, BONE_D, brow, ow=max(1, int(1.2 * s)))

    # === the HOOKED BEAK — the defining read =================================
    # upper mandible: a heavy wedge hooking DOWN past the jaw, glowing inside.
    beak_top = cy + int(r * 0.18)
    hook_y = cy + int(r * 1.18)
    upper = [(cx - int(r * 0.46), beak_top),
             (cx + int(r * 0.46), beak_top),
             (cx + int(r * 0.30), cy + int(r * 0.74)),
             (cx + int(r * 0.16), hook_y),                 # hooked tip
             (cx - int(r * 0.02), cy + int(r * 0.92)),
             (cx - int(r * 0.30), cy + int(r * 0.74))]
    triad_blob(surf, BONE, upper,
               core_pts=[(cx + int(r * 0.04), beak_top + int(r * 0.06)),
                         (cx + int(r * 0.44), beak_top),
                         (cx + int(r * 0.28), cy + int(r * 0.72)),
                         (cx + int(r * 0.16), hook_y)],
               sheen_pts=[(cx - int(r * 0.44), beak_top + int(r * 0.04)),
                          (cx - int(r * 0.10), beak_top + int(r * 0.02)),
                          (cx - int(r * 0.18), cy + int(r * 0.6)),
                          (cx - int(r * 0.40), cy + int(r * 0.5))],
               ow=max(1, int(1.4 * s)))
    # cere nostril slit on the beak
    pygame.draw.line(surf, BONE_DD,
                     (cx - int(r * 0.10), beak_top + int(r * 0.16)),
                     (cx - int(r * 0.22), cy + int(r * 0.5)), max(1, int(1.4 * s)))

    if agape:
        # the GAPE — a dark wedge between the mandibles, glowing blood-orange
        gape = [(cx - int(r * 0.30), cy + int(r * 0.42)),
                (cx + int(r * 0.30), cy + int(r * 0.42)),
                (cx + int(r * 0.10), cy + int(r * 0.70)),
                (cx - int(r * 0.10), cy + int(r * 0.70))]
        pygame.draw.polygon(surf, INK, gape)
        if lit:
            inner = [(cx - int(r * 0.22), cy + int(r * 0.46)),
                     (cx + int(r * 0.22), cy + int(r * 0.46)),
                     (cx, cy + int(r * 0.66))]
            pygame.draw.polygon(surf, GLOW, inner)
            pygame.draw.polygon(surf, GLOW_BR,
                                [(cx - int(r * 0.12), cy + int(r * 0.48)),
                                 (cx + int(r * 0.12), cy + int(r * 0.48)),
                                 (cx, cy + int(r * 0.60))])
        # lower mandible hooking up under the gape
        lower = [(cx - int(r * 0.24), cy + int(r * 0.66)),
                 (cx + int(r * 0.24), cy + int(r * 0.66)),
                 (cx + int(r * 0.12), cy + int(r * 0.96)),
                 (cx - int(r * 0.12), cy + int(r * 0.96))]
        triad_blob(surf, BONE, lower, ow=max(1, int(1.2 * s)))

    # === deep sockets pinned with blood-orange glow ==========================
    for sgn in (-1, 1):
        ex = cx + sgn * int(r * 0.46)
        ey = cy - int(r * 0.04)
        pygame.draw.circle(surf, BONE_DD, (ex, ey), int(r * 0.36))
        pygame.draw.circle(surf, INK, (ex, ey), int(r * 0.30))
        if lit:
            # rust ring under the glow so it doesn't blow out flat
            pygame.draw.circle(surf, RUST, (ex, ey), int(r * 0.22))
            pygame.draw.circle(surf, GLOW, (ex + sgn * int(1 * s), ey + int(1 * s)),
                               int(r * 0.16))
            pygame.draw.circle(surf, GLOW_HOT, (ex - int(1 * s), ey - int(1 * s)),
                               max(1, int(r * 0.07)))


# ── the spread-wing hero ──────────────────────────────────────────────────────
def draw_asthi_garuda(surf, cx, cy, s):
    """Bone-vulture spirit in a hard X: beaked skull centred over two tiered fans
    of rigid quill-blades flared wide, talons gripping below. `s` = unit scale
    around a ~130-unit figure. Drawn back-to-front: far quills → body → near
    quills overlap the shoulders → head last so the beak owns the centre."""

    head_c = (cx, cy - int(34 * s))
    hr = int(22 * s)
    shoulder_y = cy - int(8 * s)
    shoulder_dx = int(15 * s)

    # === WINGS — two tiered fans of RIGID quill-BLADES (the X-silhouette) =====
    # WHY drawn first/behind: the body breastbone overlaps the wing roots so the
    # quills look anchored INTO the shoulders. Wings flared up-and-out → the hard
    # X read at 32px. Blade width scaled with `s` so they stay rigid splines, not
    # threads, after smoothscale.
    bw = max(3.0, 7.0 * s)
    qlen = 56 * s
    # left wing fan (sweeps up-left)
    scalloped_fan(surf, (cx - shoulder_dx, shoulder_y),
                  math.radians(196), math.radians(96), 6, qlen, bw, s)
    # right wing fan (sweeps up-right) — mirror
    scalloped_fan(surf, (cx + shoulder_dx, shoulder_y),
                  math.radians(-16), math.radians(96), 6, qlen, bw, s)

    # === BODY — a compact keeled breastbone (chibi, short) ===================
    body = [(cx - int(16 * s), shoulder_y - int(2 * s)),
            (cx + int(16 * s), shoulder_y - int(2 * s)),
            (cx + int(13 * s), cy + int(20 * s)),
            (cx, cy + int(28 * s)),                       # keel point
            (cx - int(13 * s), cy + int(20 * s))]
    triad_blob(surf, BONE, body,
               core_pts=[(cx + int(2 * s), shoulder_y),
                         (cx + int(15 * s), shoulder_y - int(1 * s)),
                         (cx + int(12 * s), cy + int(19 * s)),
                         (cx + int(1 * s), cy + int(26 * s))],
               sheen_pts=[(cx - int(15 * s), shoulder_y),
                          (cx - int(3 * s), shoulder_y - int(1 * s)),
                          (cx - int(6 * s), cy + int(12 * s)),
                          (cx - int(13 * s), cy + int(14 * s))],
               ow=max(1, int(1.8 * s)))
    # keel/sternum ridge + two rib-band grooves (the quill-ring motif echo)
    pygame.draw.line(surf, BONE_DD, (cx, shoulder_y + int(2 * s)),
                     (cx, cy + int(24 * s)), max(1, int(2 * s)))
    for i in range(2):
        ry = shoulder_y + int(8 * s) + i * int(9 * s)
        bw2 = int(13 * s) - i * int(2 * s)
        pygame.draw.arc(surf, BONE_DD, (cx - bw2, ry - int(6 * s), bw2 * 2, int(14 * s)),
                        math.radians(200), math.radians(340), max(1, int(2 * s)))

    # === TALONS — three-toe bone claws gripping below the keel ===============
    # WHY bottom-set: the hook charts that the pillar cap is bottom-weighted; the
    # hero shows the same grip so the silhouette has a clear "perched-then-launched"
    # bottom anchor (anti top-heavy).
    foot_y = cy + int(30 * s)
    for sgn in (-1, 1):
        fx = cx + sgn * int(9 * s)
        # shin
        pygame.draw.line(surf, INK, (cx + sgn * int(6 * s), cy + int(20 * s)),
                         (fx, foot_y), max(2, int(4 * s)))
        pygame.draw.line(surf, BONE, (cx + sgn * int(6 * s), cy + int(20 * s)),
                         (fx, foot_y), max(1, int(2.4 * s)))
        # three curved talons
        for k in (-1, 0, 1):
            a = math.radians(74 + k * 30)
            tx = fx + math.cos(a) * int(13 * s)
            ty = foot_y + abs(math.sin(a)) * int(13 * s)
            pygame.draw.line(surf, INK, (fx, foot_y), (tx, ty), max(2, int(3 * s)))
            pygame.draw.line(surf, BONE, (fx, foot_y), (tx, ty), max(1, int(1.6 * s)))
            pygame.draw.circle(surf, BONE_D, (int(tx), int(ty)), max(1, int(1.6 * s)))

    # === wing roots overlapping the shoulders (anchor read) ==================
    for sgn in (-1, 1):
        triad_circle(surf, BONE, (cx + sgn * shoulder_dx, shoulder_y),
                     int(8 * s), ow=max(1, int(1.2 * s)), core=False)
        pygame.draw.circle(surf, BONE_DD, (cx + sgn * shoulder_dx, shoulder_y),
                           int(3 * s))

    # === HEAD last — beak owns the centre ====================================
    # short neck vertebrae linking skull to keel
    pygame.draw.line(surf, INK, (cx, head_c[1] + int(hr * 0.9)),
                     (cx, shoulder_y - int(2 * s)), max(2, int(6 * s)))
    pygame.draw.line(surf, BONE, (cx, head_c[1] + int(hr * 0.9)),
                     (cx, shoulder_y - int(2 * s)), max(1, int(3.4 * s)))
    bird_skull(surf, head_c[0], head_c[1], hr, s, lit=True, agape=True)


# ── the perch-totem → pillar mirror ──────────────────────────────────────────
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """The perch-totem IS the pillar: a banded bone perch-pole wound with quill
    RINGS (the wing-quill motif continued) = the tileable shaft; a single
    wing-skull cap — wings half-FOLDED into a hard scalloped fan, beak/eye
    glowing, talons gripping toward the gap line — is the creature-derived
    gap-edge cap. Bottom-weighted toward the gap, on-axis, symmetric.

    `cap` names the END that faces the GAP."""
    shaft_w = int(14 * s)
    # central ink rod the bone segments thread onto
    pygame.draw.rect(surf, INK, (cx - int(3 * s), top, int(6 * s), bot - top))

    # === banded perch-pole segments wound with quill rings ===================
    seg_pitch = int(22 * s)
    cap_room = int(40 * s)
    if cap == "bottom":
        b0, b1 = top + int(6 * s), bot - cap_room
    else:
        b0, b1 = top + cap_room, bot - int(6 * s)
    y = b0
    while y <= b1:
        # a bone barrel segment
        seg = [(cx - shaft_w, y + int(2 * s)),
               (cx - int(shaft_w * 0.7), y - int(8 * s)),
               (cx + int(shaft_w * 0.7), y - int(8 * s)),
               (cx + shaft_w, y + int(2 * s)),
               (cx + int(shaft_w * 0.7), y + int(12 * s)),
               (cx - int(shaft_w * 0.7), y + int(12 * s))]
        triad_blob(surf, BONE, seg,
                   core_pts=[(cx, y - int(1 * s)), (cx + shaft_w, y + int(2 * s)),
                             (cx + int(shaft_w * 0.7), y + int(12 * s)), (cx, y + int(10 * s))],
                   sheen_pts=[(cx - shaft_w, y + int(2 * s)),
                              (cx - int(shaft_w * 0.5), y - int(7 * s)),
                              (cx - int(shaft_w * 0.2), y - int(5 * s)),
                              (cx - int(shaft_w * 0.7), y + int(6 * s))],
                   ow=max(1, int(1.4 * s)))
        # a quill RING wound around the segment — short rigid quill ticks fanning
        # out either side (the wing-quill motif tiled down the pole)
        for sgn in (-1, 1):
            for k in range(3):
                a = math.radians(sgn * (110 + k * 30) if sgn > 0 else (250 - k * 30))
                rx = cx + sgn * shaft_w
                tip = (rx + sgn * int(9 * s), y + int(2 * s) - int((k - 1) * 5 * s))
                pygame.draw.line(surf, INK, (rx, y + int(2 * s)), tip, max(1, int(2.2 * s)))
                pygame.draw.line(surf, QUILL_HI if k == 1 else BONE,
                                 (rx, y + int(2 * s)), tip, max(1, int(1.2 * s)))
        # central foramen + transverse groove (the band)
        pygame.draw.circle(surf, BONE_DD, (cx, y + int(2 * s)), int(3 * s))
        pygame.draw.line(surf, BONE_DD, (cx - int(shaft_w * 0.6), y - int(6 * s)),
                         (cx + int(shaft_w * 0.6), y - int(6 * s)), max(1, int(1.4 * s)))
        y += seg_pitch

    # === gap-edge cap: wing-skull with half-FOLDED scalloped fan =============
    # WHY bottom-weighted: the beak + talons hang toward the gap so the heavy mass
    # sits at the gap edge, never top-heavy. Wings are half-folded into a tight
    # hard scalloped fan tucked back along the pole, not flared wide.
    cap_skull_r = int(15 * s)
    if cap == "bottom":
        cap_y = bot - int(24 * s)
        # half-folded fans sweep UP-and-back along the pole (away from gap)
        scalloped_fan(surf, (cx - int(11 * s), cap_y - int(6 * s)),
                      math.radians(214), math.radians(58), 4, 34 * s, max(3.0, 6.0 * s), s)
        scalloped_fan(surf, (cx + int(11 * s), cap_y - int(6 * s)),
                      math.radians(-34), math.radians(58), 4, 34 * s, max(3.0, 6.0 * s), s)
        talon_y = cap_y + int(cap_skull_r * 1.3)
        talon_dir = 1
    else:
        cap_y = top + int(24 * s)
        scalloped_fan(surf, (cx - int(11 * s), cap_y + int(6 * s)),
                      math.radians(146), math.radians(58), 4, 34 * s, max(3.0, 6.0 * s), s)
        scalloped_fan(surf, (cx + int(11 * s), cap_y + int(6 * s)),
                      math.radians(34), math.radians(58), 4, 34 * s, max(3.0, 6.0 * s), s)
        talon_y = cap_y - int(cap_skull_r * 1.3)
        talon_dir = -1

    # talons gripping TOWARD the gap line (bottom-weight)
    for sgn in (-1, 1):
        gx = cx + sgn * int(7 * s)
        for k in (-1, 0, 1):
            a = math.radians(74 + k * 30)
            tx = gx + math.cos(a) * int(12 * s)
            ty = talon_y + talon_dir * abs(math.sin(a)) * int(12 * s)
            pygame.draw.line(surf, INK, (gx, talon_y), (tx, ty), max(2, int(3 * s)))
            pygame.draw.line(surf, BONE, (gx, talon_y), (tx, ty), max(1, int(1.6 * s)))

    # the skull caps the gap, beak + eyes glowing toward it
    # flip the skull so the beak points at the gap on the top segment
    if cap == "bottom":
        bird_skull(surf, cx, cap_y, cap_skull_r, s, lit=True, agape=True)
    else:
        # mirror vertically: draw onto a temp surface and flip so the beak/talons
        # point UP toward the gap, proving the clean top↔bottom mirror
        tmp = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        bird_skull(tmp, cx, surf.get_height() - cap_y, cap_skull_r, s, lit=True, agape=True)
        flipped = pygame.transform.flip(tmp, False, True)
        surf.blit(flipped, (0, 0))


# ── compose the review sheet ─────────────────────────────────────────────────
SS = 6


def vgrad(surf, rect, top_col, bot_col):
    x, y, w, h = rect
    for j in range(h):
        pygame.draw.line(surf, lerp(top_col, bot_col, j / max(1, h - 1)),
                         (x, y + j), (x + w, y + j))


def main():
    W, H = 1010, 820
    font_big = pygame.font.SysFont("DejaVu Sans", 30, bold=True)
    font = pygame.font.SysFont("DejaVu Sans", 17, bold=True)
    font_sm = pygame.font.SysFont("DejaVu Sans", 12)

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    pygame.draw.rect(sheet, PANEL, (0, 0, W, 56))
    sheet.blit(font_big.render("ASTHI-GARUDA", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "bone-winged charnel sky-eater  ·  SPREAD-WING X · beaked skull · rigid quill-BLADES · round 1",
        True, LABEL_DIM), (290, 26))

    # === (a) BIG HERO =========================================================
    def render_hero():
        big = pygame.Surface((360 * SS, 470 * SS), pygame.SRCALPHA)
        draw_asthi_garuda(big, 178 * SS, 240 * SS, 1.95 * SS)
        small = pygame.transform.smoothscale(big, (360, 470))
        return grow_outline(small, INK + (255,), 1)

    sheet.blit(render_hero(), (14, 92))
    sheet.blit(font.render("Creature — hero", True, LABEL), (110, 566))
    sheet.blit(font_sm.render("hard X-silhouette: beaked bone-skull over two tiered fans of RIGID quill-", True, LABEL_DIM), (14, 590))
    sheet.blit(font_sm.render("BLADES (bone splines, NOT membranes). Beak agape + sockets glow blood-orange.", True, LABEL_DIM), (14, 606))
    sheet.blit(font_sm.render("Talons grip below = bottom anchor. Lavender-grey bone DESATURATED, no violet glow.", True, LABEL_DIM), (14, 622))

    # === (b) PILLAR assembled — mirrored, clean tileable shaft ================
    pcx = 470
    top_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(top_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="bottom")
    top_seg = grow_outline(pygame.transform.smoothscale(top_big, (150, 250)), INK + (255,), 1)
    sheet.blit(top_seg, (pcx, 86))
    bot_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(bot_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="top")
    bot_seg = grow_outline(pygame.transform.smoothscale(bot_big, (150, 250)), INK + (255,), 1)
    sheet.blit(bot_seg, (pcx, 86 + 250 + 96))
    pygame.draw.rect(sheet, (58, 56, 68), (pcx + 8, 86 + 250, 134, 96))
    sheet.blit(font_sm.render("GAP", True, LABEL_DIM), (pcx + 56, 86 + 250 + 40))
    sheet.blit(font.render("Pillar — perch-totem", True, LABEL), (pcx - 4, 690))
    sheet.blit(font_sm.render("banded bone perch-pole wound with quill", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("rings = shaft; wing-skull (half-folded fan,", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("talons gripping the gap) caps each edge — mirror visible", True, LABEL_DIM), (pcx - 4, 746))

    # === (c) TRUE 32px gameplay chips on day + night sky ======================
    panel_x = 660
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 560))
    sheet.blit(font.render("True 32px gameplay-scale chip", True, LABEL), (panel_x + 16, 96))

    def chip32():
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_asthi_garuda(big, 48 * SS, 50 * SS, (32 / 132.0) * SS)
        small = pygame.transform.smoothscale(big, (96, 96))
        return grow_outline(small, INK + (255,), 1)

    chip = chip32()

    day_y = 128
    vgrad(sheet, (panel_x + 20, day_y, 150, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, day_y, 150, 150), 1)
    sheet.blit(chip, (panel_x + 20 + 27, day_y + 27))
    sheet.blit(font_sm.render("32px on day sky", True, LABEL), (panel_x + 20, day_y + 156))

    night_y = day_y + 184
    vgrad(sheet, (panel_x + 20, night_y, 150, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, night_y, 150, 150), 1)
    sheet.blit(chip, (panel_x + 20 + 27, night_y + 27))
    sheet.blit(font_sm.render("32px on night sky", True, LABEL_DIM), (panel_x + 20, night_y + 156))

    def pillar_chip32():
        big = pygame.Surface((44 * SS, 130 * SS), pygame.SRCALPHA)
        draw_pillar(big, 22 * SS, 2 * SS, 128 * SS, 0.34 * SS, cap="bottom")
        small = pygame.transform.smoothscale(big, (44, 130))
        return grow_outline(small, INK + (255,), 1)

    pc = pillar_chip32()
    px2 = panel_x + 192
    vgrad(sheet, (px2, day_y, 56, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (px2, day_y, 56, 150), 1)
    sheet.blit(pc, (px2 + 6, day_y + 10))
    vgrad(sheet, (px2, night_y, 56, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (px2, night_y, 56, 150), 1)
    sheet.blit(pc, (px2 + 6, night_y + 10))
    sheet.blit(font_sm.render("pillar", True, LABEL_DIM), (px2 + 4, day_y - 16))
    sheet.blit(font_sm.render("gap-cap", True, LABEL_DIM), (px2 - 2, night_y - 16))

    sheet.blit(font.render("Pinned palette", True, LABEL), (panel_x + 16, 510))
    swatches = [
        (BONE, "violet-grey bone"), (BONE_D, "slate-violet sh"),
        (GLOW, "blood-orange glow"), (RUST, "rust shade"),
        (QUILL_HI, "pale-quill hi"), (SHEEN, "sheen"),
        (BONE_DD, "deep hollow"), (INK, "ink keyline"),
    ]
    sxp, syp = panel_x + 16, 538
    for i, (c, name) in enumerate(swatches):
        col, row = i % 2, i // 2
        rx = sxp + col * 158
        ry = syp + row * 26
        pygame.draw.rect(sheet, INK, (rx - 1, ry - 1, 20, 20))
        pygame.draw.rect(sheet, c, (rx, ry, 18, 18))
        sheet.blit(font_sm.render(name, True, LABEL), (rx + 26, ry + 3))

    pygame.draw.rect(sheet, PANEL, (14, 770, W - 28, 40))
    sheet.blit(font_sm.render(
        "ELEVATED pipeline: SS=6 supersample → smoothscale.  STAY: flat fills · hard ink keyline (26,24,30) · "
        "dark-core→fill→top-left sheen triad · 1px grown outline · chibi · scary-CUTE · procedural-only · violet in BONE not glow.",
        True, LABEL_DIM), (26, 783))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
