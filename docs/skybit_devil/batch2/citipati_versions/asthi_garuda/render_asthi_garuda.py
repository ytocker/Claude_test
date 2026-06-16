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


# ── a single FAT RIGID bone-BLADE (the hard tell — a plank, never a thread) ───
def bone_blade(surf, root, ang, length, width, s, tip_blunt=0.34):
    """One FAT rigid bone-blade: a wide, near-parallel-sided plank rooted at
    `root`, swept along `ang`, ending in a stubby CHISEL tip (never a hair). WHY
    a fat plank and not a needle-quill: round-1 collapsed into a dandelion-puff
    at 32px — the AD ruling is fat rigid BLADES so the winged tell survives at
    gameplay scale. Each blade is triad-lit as its OWN form (dark-core spine →
    flat fill → top-left sheen) so it reads as a plank of bone, and is its own
    closed polygon so sky reads cleanly BETWEEN blades — the X stays an X."""
    ca, sa = math.cos(ang), math.sin(ang)
    px, py = -sa, ca                     # perpendicular = blade width axis
    hw = width * 0.5
    # the chisel tip is a blunt flat edge (a stubby chisel), not a point
    tip_c = (root[0] + ca * length, root[1] + sa * length)
    tw = hw * tip_blunt                  # half-width at the chisel tip
    # belly sits most of the way out so the plank stays wide nearly to the tip
    belly = 0.72 * length
    bx = (root[0] + ca * belly, root[1] + sa * belly)
    # 6-point near-parallel plank: root edge → full-width belly → chisel tip edge
    blade = [
        (root[0] + px * hw * 0.86, root[1] + py * hw * 0.86),
        (bx[0]   + px * hw,        bx[1]   + py * hw),
        (tip_c[0] + px * tw,       tip_c[1] + py * tw),
        (tip_c[0] - px * tw,       tip_c[1] - py * tw),
        (bx[0]   - px * hw,        bx[1]   - py * hw),
        (root[0] - px * hw * 0.86, root[1] - py * hw * 0.86),
    ]
    pygame.draw.polygon(surf, INK, blade)
    pygame.draw.polygon(surf, BONE, blade)
    # dark-core spine down the trailing (body-side) half → the plank gets volume
    core = [
        (root[0] - px * hw * 0.62, root[1] - py * hw * 0.62),
        (bx[0]   - px * hw * 0.86, bx[1]   - py * hw * 0.86),
        (tip_c[0] - px * tw,       tip_c[1] - py * tw),
        (tip_c[0] + px * tw * 0.2, tip_c[1] + py * tw * 0.2),
        (bx[0]   - px * hw * 0.10, bx[1]   - py * hw * 0.10),
    ]
    pygame.draw.polygon(surf, BONE_D, core)
    # top-left leading-edge sheen — a fat pale rail, not a thread (rigid bone read)
    lead = [
        (root[0] + px * hw * 0.70, root[1] + py * hw * 0.70),
        (bx[0]   + px * hw * 0.92, bx[1]   + py * hw * 0.92),
        (tip_c[0] + px * tw * 0.8, tip_c[1] + py * tw * 0.8),
        (tip_c[0] + px * tw * 0.1, tip_c[1] + py * tw * 0.1),
        (bx[0]   + px * hw * 0.30, bx[1]   + py * hw * 0.30),
    ]
    pygame.draw.polygon(surf, QUILL_HI, lead)
    # central shaft groove — the hard quill rib, a confident line
    pygame.draw.line(surf, BONE_DD, (bx[0], bx[1]), tip_c, max(2, int(width * 0.18)))
    pygame.draw.polygon(surf, INK, blade, max(2, int(width * 0.16)))


def blade_wing(surf, root, base_ang, s, sign, scale=1.0, length=58.0, width=12.0):
    """ONE wing as a small set of FAT bone-blades forming TWO clean RANKS — an
    outer PRIMARY rank (3 long blades that define the X-arm) + an inner COVERT
    rank (2 short fat stubs at the shoulder). WHY two ranks not one fringe: the
    brief asks for tiered fans; the longest primary points down `base_ang` and
    is THE X-limb, its siblings tuck a few degrees behind it (NOT a radial
    sunburst). `sign` (+1 right / -1 left) only mirrors the small spread offsets.
    Total = 5 blades per wing, max — the AD blade budget."""
    bw = max(4.0, width * s)
    L = length * s * scale
    # COVERT rank first (drawn behind): two short fat stubs hugging the shoulder
    for k, (off, fac, wfac) in enumerate(((22, 0.42, 1.05), (40, 0.34, 0.92))):
        a = base_ang + sign * math.radians(off)
        bone_blade(surf, root, a, L * fac, bw * wfac, s, tip_blunt=0.46)
    # PRIMARY rank: three long blades, the MIDDLE one is the X-limb (longest)
    # tight ±13° spread so they read as one bold thrust, not a spreading fan
    for k, (off, fac) in enumerate(((-13, 0.80), (0, 1.0), (13, 0.84))):
        a = base_ang + math.radians(off)
        bone_blade(surf, root, a, L * fac, bw, s, tip_blunt=0.30)


# ── a single FAT triad-lit bone CLAW / toe (talons read at 32px) ──────────────
def fat_claw(surf, a, b, width, s, bend=0.0):
    """A fat tapered bone claw from `a` to `b`, optionally hooked by `bend`. WHY
    fat & triad-lit: round-1 talons read as scribbled thread-bundles; the AD
    note is 3 FAT triad-lit toes that survive at 32px. Built as a tapering
    polygon (wide root → clawed tip) with a dark-core underside + pale top sheen
    so each toe reads as a solid claw, not a line."""
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    nx, ny = -uy, ux                 # perpendicular (width axis)
    # a slight hook: pull the tip sideways by `bend`
    bx += nx * bend * width
    by += ny * bend * width
    hw = width * 0.5
    claw = [
        (ax + nx * hw, ay + ny * hw),
        (ax + nx * hw * 0.5 + ux * L * 0.5, ay + ny * hw * 0.5 + uy * L * 0.5),
        (bx, by),                     # clawed tip (point)
        (ax - nx * hw * 0.5 + ux * L * 0.5, ay - ny * hw * 0.5 + uy * L * 0.5),
        (ax - nx * hw, ay - ny * hw),
    ]
    pygame.draw.polygon(surf, INK, claw)
    pygame.draw.polygon(surf, BONE, claw)
    # dark-core underside (the lower/right of the toe) for volume
    pygame.draw.polygon(surf, BONE_D, [
        (ax - nx * hw * 0.6, ay - ny * hw * 0.6),
        (ax - nx * hw * 0.3 + ux * L * 0.5, ay - ny * hw * 0.3 + uy * L * 0.5),
        (bx, by),
    ])
    # pale top sheen rail
    pygame.draw.line(surf, QUILL_HI, (ax + nx * hw * 0.5, ay + ny * hw * 0.5),
                     (bx, by), max(1, int(width * 0.18)))
    pygame.draw.polygon(surf, INK, claw, max(1, int(width * 0.16)))


# ── a half-FOLDED wing = a tight hard SCALLOPED fan of fat blades (pillar cap) ─
def folded_fan(surf, root, base_ang, s, sign):
    """Three FAT bone-blades fanned in a TIGHT arc — the wing half-folded into a
    hard scalloped edge. WHY on the prop: round-1's cap read as 'another vertebra
    knot'; the winged tell has to live on the pillar too. A close ±16° fan of fat
    blades gives the scalloped folded-wing edge (NOT Nagaraja's splayed rib-spline
    hood), each blade triad-lit so the scallop reads as layered bone planks."""
    bw = max(3.5, 6.0 * s)
    for k, (off, fac) in enumerate(((-16, 0.82), (0, 1.0), (16, 0.86))):
        a = base_ang + math.radians(off)
        bone_blade(surf, root, a, 30 * s * fac, bw, s, tip_blunt=0.38)


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

    # === deep ANGULAR bone sockets pinned with blood-orange glow =============
    # WHY angular hollows, not round rims: round-1's round bone rings + a bridge
    # read as goggles/steampunk owl. A raptor's sockets are deep ANGULAR holes
    # bored straight into the skull bone under the brow — so each eye is a hard
    # keyhole hollow (no raised lens ring), the glow nested deep, with a WIDE
    # bony FOREHEAD KEEL between them (not a thin bridge bar). Reads raw
    # bone-vulture, not spectacles.
    for sgn in (-1, 1):
        ex = cx + sgn * int(r * 0.50)
        ey = cy - int(r * 0.02)
        # an angular socket hollow bored into the bone — top-outer corner sharp,
        # inner-bottom rounded, slanting down toward the beak (the scowl)
        socket = [
            (ex - sgn * int(r * 0.30), ey - int(r * 0.30)),   # inner top
            (ex + sgn * int(r * 0.34), ey - int(r * 0.24)),   # outer top
            (ex + sgn * int(r * 0.30), ey + int(r * 0.22)),   # outer bottom
            (ex - sgn * int(r * 0.20), ey + int(r * 0.30)),   # inner bottom (toward beak)
        ]
        pygame.draw.polygon(surf, BONE_DD, socket)
        pygame.draw.polygon(surf, INK, socket)
        if lit:
            # rust floor → orange glow nested DEEP in the hollow, not on a lens
            pygame.draw.circle(surf, RUST, (ex, ey), int(r * 0.24))
            pygame.draw.circle(surf, GLOW, (ex + sgn * int(1 * s), ey + int(1 * s)),
                               int(r * 0.17))
            pygame.draw.circle(surf, GLOW_HOT, (ex - int(1 * s), ey - int(1 * s)),
                               max(1, int(r * 0.07)))
        else:
            pygame.draw.polygon(surf, INK, [
                (ex - int(r * 0.16), ey - int(r * 0.14)),
                (ex + int(r * 0.16), ey - int(r * 0.10)),
                (ex, ey + int(r * 0.16))])
    # WIDE bony forehead keel between the sockets — a solid wedge of skull,
    # triad-lit, that physically SEPARATES the eyes (kills the bridge read)
    keel = [(cx - int(r * 0.16), cy - int(r * 0.34)),
            (cx + int(r * 0.16), cy - int(r * 0.34)),
            (cx + int(r * 0.12), cy + int(r * 0.30)),
            (cx - int(r * 0.12), cy + int(r * 0.30))]
    pygame.draw.polygon(surf, INK, keel)
    pygame.draw.polygon(surf, BONE, keel)
    pygame.draw.line(surf, QUILL_HI, (cx - int(r * 0.06), cy - int(r * 0.30)),
                     (cx - int(r * 0.04), cy + int(r * 0.24)), max(1, int(1.4 * s)))
    pygame.draw.line(surf, BONE_DD, (cx + int(r * 0.08), cy - int(r * 0.28)),
                     (cx + int(r * 0.06), cy + int(r * 0.24)), max(1, int(1.4 * s)))


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

    # === WINGS — FOUR bold X-arms of FAT bone-BLADES (the X-silhouette) =======
    # WHY drawn first/behind: the body breastbone overlaps the wing roots so the
    # blades look anchored INTO the shoulders. The four limbs of a CAPITAL X —
    # two thrust up-and-out, two down-and-out — each a wing of fat blades whose
    # longest primary IS the X-limb. The span is wider than the body is tall so
    # the blacked-out 32px silhouette reads ONLY as a spread-wing X.
    # four limbs of a CAPITAL X radiating from the shoulder wing-joints. Upper
    # limbs thrust up-and-out; lower limbs are rooted at the SHOULDER (not the
    # waist) and swept down-and-out far enough that their fat primaries clear the
    # body silhouette — so the bottom of the X punches OUT past the torso instead
    # of collapsing into a fluffy base. Span is wider than the figure is tall.
    upL = (cx - shoulder_dx, shoulder_y - int(2 * s))
    upR = (cx + shoulder_dx, shoulder_y - int(2 * s))
    dnL = (cx - shoulder_dx, shoulder_y + int(4 * s))
    dnR = (cx + shoulder_dx, shoulder_y + int(4 * s))
    blade_wing(surf, upL, math.radians(218), s, sign=+1, scale=1.10, length=62, width=14)
    blade_wing(surf, upR, math.radians(-38), s, sign=-1, scale=1.10, length=62, width=14)
    blade_wing(surf, dnL, math.radians(150), s, sign=-1, scale=1.02, length=60, width=13)
    blade_wing(surf, dnR, math.radians(30),  s, sign=+1, scale=1.02, length=60, width=13)

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
        # shank — a fat triad-lit bone, not a scribble
        fat_claw(surf, (cx + sgn * int(6 * s), cy + int(20 * s)), (fx, foot_y),
                 max(5.0, 6.0 * s), s, bend=0.0)
        # exactly THREE fat triad-lit toes, kept TIGHT and short so they read as a
        # compact gripping claw under the keel — the lower wing-blades, not the
        # talons, carry the bottom of the X silhouette
        for k in (-1, 0, 1):
            a = math.radians(78 + k * 26)
            tx = fx + math.cos(a) * int(11 * s)
            ty = foot_y + abs(math.sin(a)) * int(11 * s)
            fat_claw(surf, (fx, foot_y), (tx, ty), max(4.0, 5.0 * s), s, bend=k * 0.3)

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
        fold_y = cap_y - int(8 * s)
        # half-FOLDED wings: 3 FAT blades per side, swept back-and-DOWN along the
        # pole into a tight HARD SCALLOPED fan (the winged tell on the prop, NOT a
        # rib-spline hood). Steep angle + short length = folded, not flared.
        folded_fan(surf, (cx - int(10 * s), fold_y), math.radians(238), s, +1)
        folded_fan(surf, (cx + int(10 * s), fold_y), math.radians(-58), s, -1)
        talon_y = cap_y + int(cap_skull_r * 1.3)
        talon_dir = 1
    else:
        cap_y = top + int(24 * s)
        fold_y = cap_y + int(8 * s)
        folded_fan(surf, (cx - int(10 * s), fold_y), math.radians(122), s, +1)
        folded_fan(surf, (cx + int(10 * s), fold_y), math.radians(58), s, -1)
        talon_y = cap_y - int(cap_skull_r * 1.3)
        talon_dir = -1

    # three FAT triad-lit talons gripping TOWARD the gap line (bottom-weight)
    for sgn in (-1, 1):
        gx = cx + sgn * int(7 * s)
        for k in (-1, 0, 1):
            a = math.radians(74 + k * 32)
            tx = gx + math.cos(a) * int(12 * s)
            ty = talon_y + talon_dir * abs(math.sin(a)) * int(12 * s)
            fat_claw(surf, (gx, talon_y), (tx, ty), max(3.0, 4.0 * s), s, bend=k * 0.3)

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
    W, H = 1010, 900
    font_big = pygame.font.SysFont("DejaVu Sans", 30, bold=True)
    font = pygame.font.SysFont("DejaVu Sans", 17, bold=True)
    font_sm = pygame.font.SysFont("DejaVu Sans", 12)

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    pygame.draw.rect(sheet, PANEL, (0, 0, W, 56))
    sheet.blit(font_big.render("ASTHI-GARUDA", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "bone-winged charnel sky-eater  ·  BOLD X · beaked skull · 4-5 FAT bone-BLADES · round 2",
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
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 720))
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

    # blacked-out 32px silhouette — the X-read TEST: it must read ONLY as a
    # spread-wing X, never a ball / radial fan / starburst
    def silhouette32():
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_asthi_garuda(big, 48 * SS, 50 * SS, (32 / 132.0) * SS)
        small = pygame.transform.smoothscale(big, (96, 96))
        small = grow_outline(small, INK + (255,), 1)
        # flatten every opaque pixel to solid ink → pure silhouette
        mask = pygame.mask.from_surface(small, 24)
        sil = mask.to_surface(setcolor=INK + (255,), unsetcolor=(0, 0, 0, 0))
        return sil

    sil_y = night_y + 188
    sx = panel_x + 20
    pygame.draw.rect(sheet, (212, 214, 220), (sx, sil_y, 96, 96))
    pygame.draw.rect(sheet, INK, (sx, sil_y, 96, 96), 1)
    sheet.blit(silhouette32(), (sx, sil_y))
    sheet.blit(font_sm.render("32px BLACKED-OUT silhouette —", True, LABEL), (sx + 104, sil_y + 30))
    sheet.blit(font_sm.render("must read ONLY as spread-wing X", True, LABEL_DIM), (sx + 104, sil_y + 48))

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

    sheet.blit(font.render("Pinned palette", True, LABEL), (panel_x + 16, 636))
    swatches = [
        (BONE, "violet-grey bone"), (BONE_D, "slate-violet sh"),
        (GLOW, "blood-orange glow"), (RUST, "rust shade"),
        (QUILL_HI, "pale-quill hi"), (SHEEN, "sheen"),
        (BONE_DD, "deep hollow"), (INK, "ink keyline"),
    ]
    sxp, syp = panel_x + 16, 664
    for i, (c, name) in enumerate(swatches):
        col, row = i % 2, i // 2
        rx = sxp + col * 158
        ry = syp + row * 26
        pygame.draw.rect(sheet, INK, (rx - 1, ry - 1, 20, 20))
        pygame.draw.rect(sheet, c, (rx, ry, 18, 18))
        sheet.blit(font_sm.render(name, True, LABEL), (rx + 26, ry + 3))

    pygame.draw.rect(sheet, PANEL, (14, 850, W - 28, 40))
    sheet.blit(font_sm.render(
        "ELEVATED pipeline: SS=6 supersample → smoothscale.  STAY: flat fills · hard ink keyline (26,24,30) · "
        "dark-core→fill→top-left sheen triad · 1px grown outline · chibi · scary-CUTE · procedural-only · violet in BONE not glow.",
        True, LABEL_DIM), (26, 863))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_2.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
