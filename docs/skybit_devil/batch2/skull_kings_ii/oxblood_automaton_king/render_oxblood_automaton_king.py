"""
Round-1 concept renderer for the OXBLOOD AUTOMATON KING — a royal skull-KING of
the Skull-Kings-II brood, rendered as a RIGID BLOCKY HUMANOID MACHINE. Headless
Pygame; ELEVATED pipeline (SS=6 supersample -> smoothscale) so the riveted plate
detail survives the downscale. Clones the sibling regent's house grammar wholesale:
flat triad fill (dark-core -> flat -> top-left sheen), a hard 1-2px ink keyline
(28,22,30), 1px alpha-grown outline, chibi proportions, scary-CUTE. Procedural-
only (no gradients/PNGs).

WHY this reads as a MACHINE, not a bone-lord: the whole figure is boxed —
riveted rectangular copper plates, a square torso, square pauldrons, PEG LEGS,
and CIRCULAR gear-rings at every joint. Two stiff geometric arms with gear-elbows;
no cradle. The de-collider from the sibling Bismuth Prism-Architect (a LIMBLESS
stepped-crystal mass) is the HUMANOID lock: peg legs + square pauldrons + visible
limbs + at least one prominent CIRCULAR gear-ring, so the two never twin.

WHY the heat stays WARM copper: the body is patinated copper-bronze (the dominant
mass); oxblood-lacquer panels are thin rectangular inlays; verdigris is kept to a
FEW thin ticks so the figure never cools toward green (it must NOT twin Malachite).
The single brightest pixel is the BRASS GEAR-EYE — a glowing toothed iris socket —
which owns the focal. Above the head: a brass skull finial on a clockwork
gear-spindle spire (the royal skull-crown tell).

WHY a standalone script under docs/: review art must never enter the shipped
bundle, so it reuses only colour math + the triad/outline helpers, not runtime
sprite modules.
"""
import math
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

# -- PINNED PALETTE (locked brief) --------------------------------------------
# Patinated copper-bronze is the DOMINANT warm mass; everything else is thin.
COPPER     = (178, 120,  78)   # patinated copper-bronze body (dominant fill)
COPPER_D   = (128,  82,  50)   # copper dark-core / recessed plate
COPPER_DD  = ( 92,  58,  36)   # deepest copper hollow (seams, joint gaps)
COPPER_SH  = (224, 168, 116)   # copper top-left rim-sheen
# oxblood-lacquer panel inlays — thin rectangular accents only
OXBLOOD    = (116,  36,  40)
OXBLOOD_BR = (158,  60,  58)
OXBLOOD_D  = ( 78,  24,  28)
# the SINGLE warm focal — the brass gear-eye iris (must stay brightest pixel).
BRASS      = (232, 196, 108)
BRASS_BR   = (252, 230, 168)   # hottest brass core (the brightest pixel)
BRASS_D    = (176, 142,  62)
# verdigris — kept MINIMAL (a few thin oxidation ticks) so body stays warm.
VERD       = (120, 168, 150)
VERD_D     = ( 84, 124, 110)
# dark structural iron (rivets, deep frame shadow)
IRON       = ( 58,  54,  56)
IRON_D     = ( 36,  34,  36)
INK        = ( 28,  22,  30)   # hard ink keyline

BG         = ( 96, 100, 108)   # neutral grey review backdrop
PANEL      = ( 74,  78,  88)
DAY_SKY_T  = (120, 196, 236)
DAY_SKY_B  = (196, 232, 244)
NIGHT_T    = ( 22,  26,  54)
NIGHT_B    = ( 48,  44,  82)
LABEL      = (238, 240, 244)
LABEL_DIM  = (188, 196, 208)


def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return (int(a[0] + (b[0]-a[0])*t),
            int(a[1] + (b[1]-a[1])*t),
            int(a[2] + (b[2]-a[2])*t))


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


def rivet_plate(surf, x, y, w, h, color, s, rivets=True, inlay=False):
    """A riveted rectangular copper plate — the machine's building block. WHY a
    boxed rect with corner rivet pips: the blocky-humanoid silhouette is built
    from stacked plates, and the rivet dots read as 'worked metal' at hero scale
    while dissolving cleanly at 32px. `inlay` swaps the fill to oxblood lacquer."""
    fill = OXBLOOD if inlay else color
    core = OXBLOOD_D if inlay else lerp(color, INK, 0.40)
    sh = OXBLOOD_BR if inlay else lerp(color, (255, 255, 255), 0.40)
    rect = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
    triad_blob(surf, fill, rect,
               core_pts=[(x + w * 0.40, y + h * 0.42), (x + w, y + h * 0.30),
                         (x + w, y + h), (x + w * 0.40, y + h)],
               sheen_pts=[(x, y), (x + w * 0.55, y), (x + w * 0.30, y + h * 0.40),
                          (x, y + h * 0.50)],
               ow=max(1, int(1.3 * s)))
    if rivets:
        rr = max(1, int(1.6 * s))
        for rx in (x + w * 0.13, x + w * 0.87):
            for ry in (y + h * 0.16, y + h * 0.84):
                pygame.draw.circle(surf, IRON_D, (int(rx), int(ry)), rr + max(1, int(0.6 * s)))
                pygame.draw.circle(surf, lerp(color, (255, 255, 255), 0.25),
                                   (int(rx - rr * 0.3), int(ry - rr * 0.3)), rr)


def gear_ring(surf, cx, cy, r, s, teeth=10, color=COPPER, hub=True):
    """A prominent CIRCULAR toothed gear-ring — the de-collider from the sibling
    Bismuth's angular facets. WHY drawn as a notched disc with a dark hub: the
    round teeth read unmistakably as a cog at hero scale, and the circular
    silhouette stays legible (a clean dark ring) at 32px against any sky."""
    # toothed outer rim built as a star-ish polygon (alternating r / r*1.18)
    pts = []
    n = teeth * 2
    for k in range(n):
        a = math.radians(k * (360.0 / n))
        rr = r * (1.20 if k % 2 == 0 else 0.98)
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    pygame.draw.polygon(surf, INK, pts)
    pygame.draw.polygon(surf, lerp(color, INK, 0.30), pts)
    # flat disc face
    triad_circle(surf, color, (cx, cy), int(r * 0.92), ow=max(1, int(1.3 * s)),
                 core=False)
    if hub:
        # dark recessed hub with a bright bolt pip
        pygame.draw.circle(surf, COPPER_DD, (cx, cy), max(2, int(r * 0.36)))
        pygame.draw.circle(surf, INK, (cx, cy), max(2, int(r * 0.36)), max(1, int(1.0 * s)))
        pygame.draw.circle(surf, BRASS, (cx, cy), max(1, int(r * 0.18)))
        pygame.draw.circle(surf, BRASS_BR,
                           (cx - int(r * 0.07), cy - int(r * 0.08)), max(1, int(r * 0.09)))


def verd_ticks(surf, x, y, w, s, n=3):
    """A FEW small verdigris PATINA ticks riding a recessed seam. WHY kept tiny +
    sparse but now grounded in a dark seam (round 2): verdigris is a seasoning,
    not a mass — too much cools the copper toward green and twins the Malachite
    king. Each tick is a short stack of a dark VERD_D base + a VERD highlight, so
    it reads as oxidation crusting a shadow line rather than a phantom palette
    slot, while the broad plates stay warm copper."""
    for k in range(n):
        tx = int(x + (k + 0.5) * (w / n))
        ty = int(y)
        h = int(3 * s)
        pygame.draw.line(surf, VERD_D, (tx, ty), (tx, ty + h), max(1, int(1.4 * s)))
        pygame.draw.line(surf, VERD, (tx, ty), (tx, ty + max(1, h // 2)),
                         max(1, int(1.0 * s)))


def peg_leg(surf, hip, s, sgn):
    """A stiff square-shouldered PEG LEG — a boxed thigh plate tapering to a
    tapered peg foot, with a gear-ring at the hip. WHY a peg (not a bone limb):
    pegs lock the silhouette as a rigid machine and read clean against the sky."""
    hx, hy = hip
    thigh_w = int(13 * s)
    thigh_h = int(26 * s)
    rivet_plate(surf, hx - thigh_w // 2, hy, thigh_w, thigh_h, COPPER, s)
    # tapered peg shank below the thigh plate
    peg_top = hy + thigh_h
    peg = [(hx - int(6 * s), peg_top), (hx + int(6 * s), peg_top),
           (hx + int(4 * s), peg_top + int(22 * s)),
           (hx - int(4 * s), peg_top + int(22 * s))]
    triad_blob(surf, COPPER, peg,
               sheen_pts=[(hx - int(6 * s), peg_top), (hx - int(2 * s), peg_top),
                          (hx - int(2 * s), peg_top + int(22 * s)),
                          (hx - int(4 * s), peg_top + int(22 * s))],
               ow=max(1, int(1.2 * s)))
    # blocky foot pad
    foot = [(hx - int(9 * s), peg_top + int(22 * s)),
            (hx + int(10 * s), peg_top + int(22 * s)),
            (hx + int(10 * s), peg_top + int(30 * s)),
            (hx - int(9 * s), peg_top + int(30 * s))]
    triad_blob(surf, COPPER_D, foot, ow=max(1, int(1.2 * s)))
    # gear-ring at the hip (joint tell)
    gear_ring(surf, hx, hy, int(7 * s), s, teeth=8)


# -- the brass skull finial on a clockwork gear-spindle spire (royal crown) ----
def skull_spire(surf, cx, base_y, r, s, night_rim=False):
    """A CHUNKY brass SKULL on a clockwork gear-spindle spire rising from the head
    — the royal skull-KING crown tell, and the thematic identity. WHY rebuilt big
    + blocky for round 2: at 32px a small round finial collapsed to 2-3 dots, so
    the skull (the whole point of a Skull King) was lost. The cranium is now a
    chunky brass BLOCK with two dark socket pixels and a dark jaw notch so it reads
    as a SKULL SHAPE — not a bead — through the downscale, sitting as the brightest
    warm value above the head. The spire is ONE bold 3-4px vertical stroke with a
    SINGLE gear-ring node mid-shaft, so head→spindle→skull are three separable
    tiers that survive in motion. `night_rim` adds a faint brass rim-light on the
    skull+spire only, so the crown carries against a dim night sky."""
    # the bold spindle column rising from the crown — one clear vertical stroke
    spindle_h = int(r * 2.2)
    sw = max(2, int(3.4 * s) // 2)          # half-width: a fat 3-4px stroke at 32px
    spire_top = base_y - spindle_h
    spire_rect = [(cx - sw, base_y), (cx + sw, base_y),
                  (cx + sw, spire_top), (cx - sw, spire_top)]
    if night_rim:
        # faint warm rim on the spire stroke so it carries on dark night sky
        pygame.draw.polygon(surf, BRASS_D,
                            [(cx - sw - max(1, int(0.9 * s)), base_y),
                             (cx + sw + max(1, int(0.9 * s)), base_y),
                             (cx + sw + max(1, int(0.9 * s)), spire_top),
                             (cx - sw - max(1, int(0.9 * s)), spire_top)])
    triad_blob(surf, BRASS, spire_rect,
               sheen_pts=[(cx - sw, base_y), (cx, base_y),
                          (cx, spire_top), (cx - sw, spire_top)],
               ow=max(1, int(1.0 * s)))
    # ONE gear-ring node at mid-shaft (the clockwork tell, kept legible)
    node_y = base_y - int(spindle_h * 0.46)
    gear_ring(surf, cx, node_y, int(r * 0.52), s, teeth=7, color=BRASS, hub=False)

    # === the CHUNKY brass skull cranium block ================================
    skw = int(r * 1.30)                     # a broad block, not a round bead
    skh = int(r * 1.10)
    skx = cx - skw // 2
    sky_top = spire_top - skh
    cranium = [(skx, sky_top + int(skh * 0.16)),
               (skx + int(skw * 0.16), sky_top),
               (skx + skw - int(skw * 0.16), sky_top),
               (skx + skw, sky_top + int(skh * 0.16)),
               (skx + skw, sky_top + int(skh * 0.62)),
               (skx + int(skw * 0.78), sky_top + int(skh * 0.78)),
               (skx + int(skw * 0.22), sky_top + int(skh * 0.78)),
               (skx, sky_top + int(skh * 0.62))]
    if night_rim:
        # tight warm halo on the cranium so the skull stays the night focal
        rim = grow_outline(_blob_surface(surf.get_size(), BRASS, cranium),
                           BRASS_BR + (255,), max(2, int(1.4 * s)))
        surf.blit(rim, (0, 0))
    # the skull is the BRIGHTEST warm value — fill the cranium hot brass
    triad_blob(surf, BRASS_BR, cranium,
               sheen_pts=[(skx, sky_top + int(skh * 0.16)),
                          (skx + int(skw * 0.50), sky_top),
                          (skx + int(skw * 0.30), sky_top + int(skh * 0.45)),
                          (skx, sky_top + int(skh * 0.50))],
               ow=max(1, int(1.2 * s)))
    # two DARK socket pixels — the eyes that make it read as a skull
    eye_r = max(2, int(skw * 0.17))
    ey = sky_top + int(skh * 0.40)
    for sg in (-1, 1):
        pygame.draw.circle(surf, INK,
                           (cx + sg * int(skw * 0.24), ey), eye_r + max(1, int(0.6 * s)))
        pygame.draw.circle(surf, IRON_D,
                           (cx + sg * int(skw * 0.24), ey), eye_r)
    # a DARK jaw notch under the cranium — completes the skull silhouette
    jw = int(skw * 0.46)
    jy = sky_top + int(skh * 0.78)
    jaw = [(cx - jw // 2, jy), (cx + jw // 2, jy),
           (cx + int(jw * 0.32), jy + int(skh * 0.26)),
           (cx - int(jw * 0.32), jy + int(skh * 0.26))]
    pygame.draw.polygon(surf, INK, jaw)
    pygame.draw.polygon(surf, IRON_D, jaw)
    # two tiny tooth gaps so the jaw reads as a maw at hero scale
    for sg in (-1, 1):
        tx = cx + sg * int(jw * 0.16)
        pygame.draw.line(surf, INK, (tx, jy), (tx, jy + int(skh * 0.18)),
                         max(1, int(1.0 * s)))


def _blob_surface(size, color, pts):
    """A throwaway surface holding just one filled polygon — used to build a
    tight rim-light halo around the skull cranium without rimming the whole sheet."""
    s2 = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.polygon(s2, color, pts)
    return s2


# -- the rigid blocky humanoid machine-king -----------------------------------
def draw_automaton(surf, cx, cy, s, night_rim=False):
    head_c = (cx, cy - int(34 * s))
    hr = int(20 * s)
    torso_y = cy - int(8 * s)

    # === PEG LEGS (behind torso) ============================================
    for sg in (-1, 1):
        peg_leg(surf, (cx + sg * int(15 * s), cy + int(26 * s)), s, sg)

    # === SQUARE BOXY TORSO ===================================================
    tw = int(46 * s)
    th = int(40 * s)
    tx = cx - tw // 2
    rivet_plate(surf, tx, torso_y, tw, th, COPPER, s)
    # a central oxblood-lacquer chest inlay panel (thin rectangular accent)
    rivet_plate(surf, cx - int(11 * s), torso_y + int(8 * s),
                int(22 * s), int(22 * s), COPPER, s, rivets=False, inlay=True)
    # a small brass boiler-bolt centred on the oxblood panel
    triad_circle(surf, BRASS, (cx, torso_y + int(19 * s)), int(4 * s),
                 ow=max(1, int(1.0 * s)), core=False)
    # waist gear-ring (joint between torso and pelvis block)
    gear_ring(surf, cx, torso_y + th, int(8 * s), s, teeth=9)
    # a few verdigris PATINA ticks crusting the lower-SIDE seams (drawn AFTER the
    # waist gear-ring so the hub never overpaints them) — off-centre so they sit
    # in the recessed plate-edge shadow and never twin Malachite's green mass.
    seam_y = torso_y + th - int(5 * s)
    verd_ticks(surf, tx + int(3 * s), seam_y, int(12 * s), s, n=2)
    verd_ticks(surf, tx + tw - int(15 * s), seam_y, int(12 * s), s, n=2)

    # === SQUARE PAULDRONS + STIFF GEOMETRIC ARMS (gear-elbows) ===============
    arm_th = int(11 * s)
    for sg in (-1, 1):
        # square pauldron plate capping the shoulder
        pw = int(16 * s)
        px = cx + sg * int(22 * s) - pw // 2
        py = torso_y - int(2 * s)
        rivet_plate(surf, px, py, pw, int(15 * s), COPPER, s)
        # shoulder gear-ring
        sh_c = (cx + sg * int(22 * s), torso_y + int(13 * s))
        # upper-arm boxed plate (straight down)
        ua_x = sh_c[0] - sg * 0 - arm_th // 2
        rivet_plate(surf, sh_c[0] - arm_th // 2, sh_c[1], arm_th, int(18 * s),
                    COPPER, s, rivets=False)
        # gear-elbow
        elbow = (sh_c[0], sh_c[1] + int(18 * s))
        gear_ring(surf, elbow[0], elbow[1], int(6 * s), s, teeth=8)
        # forearm boxed plate angling inward to the hip (stiff, geometric)
        fa_top = elbow
        fa_bot = (cx + sg * int(14 * s), torso_y + th - int(2 * s))
        dx, dy = fa_bot[0] - fa_top[0], fa_bot[1] - fa_top[1]
        L = max(1.0, math.hypot(dx, dy))
        nx, ny = -dy / L * arm_th * 0.42, dx / L * arm_th * 0.42
        fa = [(fa_top[0] + nx, fa_top[1] + ny), (fa_bot[0] + nx, fa_bot[1] + ny),
              (fa_bot[0] - nx, fa_bot[1] - ny), (fa_top[0] - nx, fa_top[1] - ny)]
        triad_blob(surf, COPPER, fa,
                   sheen_pts=[(fa_top[0] + nx, fa_top[1] + ny),
                              (fa_bot[0] + nx, fa_bot[1] + ny),
                              (fa_bot[0] + nx * 0.3, fa_bot[1] + ny * 0.3),
                              (fa_top[0] + nx * 0.3, fa_top[1] + ny * 0.3)],
                   ow=max(1, int(1.2 * s)))
        # blocky three-finger claw hand
        hand = [(fa_bot[0] - sg * int(5 * s), fa_bot[1]),
                (fa_bot[0] + sg * int(6 * s), fa_bot[1]),
                (fa_bot[0] + sg * int(5 * s), fa_bot[1] + int(9 * s)),
                (fa_bot[0] - sg * int(4 * s), fa_bot[1] + int(9 * s))]
        triad_blob(surf, COPPER_D, hand, ow=max(1, int(1.1 * s)))
        # shoulder gear-ring drawn last so it caps the joint cleanly
        gear_ring(surf, sh_c[0], sh_c[1], int(7 * s), s, teeth=9)

    # === SQUARE MACHINE SKULL HEAD ===========================================
    hw = int(40 * s)
    hx = head_c[0] - hw // 2
    hy = head_c[1] - int(18 * s)
    rivet_plate(surf, hx, hy, hw, int(36 * s), COPPER, s)
    # a thin oxblood brow band across the top of the face plate
    rivet_plate(surf, hx + int(3 * s), hy + int(3 * s), hw - int(6 * s), int(6 * s),
                COPPER, s, rivets=False, inlay=True)
    # the BRASS GEAR-EYE — a SECONDARY focal. WHY demoted in round 2: on a Skull
    # King the above-head skull must win the brightest-warm tie, so the torso eye
    # is shrunk a notch and its hottest pip is plain BRASS (not BRASS_BR), keeping
    # it a glowing iris while ceding top value to the crown.
    eye_c = (head_c[0], head_c[1] + int(4 * s))
    eye_r = int(9 * s)
    # dark recessed socket box
    pygame.draw.circle(surf, INK, eye_c, eye_r + max(1, int(1.4 * s)))
    pygame.draw.circle(surf, COPPER_DD, eye_c, eye_r)
    # toothed brass iris ring (a tiny gear inside the eye)
    gear_ring(surf, eye_c[0], eye_c[1], int(eye_r * 0.74), s, teeth=10,
              color=BRASS_D, hub=False)
    # glowing brass pupil — capped at BRASS so the crown skull stays brightest
    pygame.draw.circle(surf, BRASS_D, eye_c, int(eye_r * 0.42))
    pygame.draw.circle(surf, BRASS, (eye_c[0] - int(eye_r * 0.16),
                                     eye_c[1] - int(eye_r * 0.18)),
                       max(2, int(eye_r * 0.24)))
    # a small dark riveted jaw vent under the eye (mouth grille)
    grille_y = head_c[1] + int(15 * s)
    pygame.draw.rect(surf, IRON_D,
                     (head_c[0] - int(9 * s), grille_y, int(18 * s), int(5 * s)))
    pygame.draw.rect(surf, INK,
                     (head_c[0] - int(9 * s), grille_y, int(18 * s), int(5 * s)),
                     max(1, int(1.0 * s)))
    for k in range(-2, 3):
        gx = head_c[0] + int(k * 4 * s)
        pygame.draw.line(surf, COPPER_DD, (gx, grille_y),
                         (gx, grille_y + int(5 * s)), max(1, int(1.0 * s)))
    # neck gear-ring between head and torso
    gear_ring(surf, head_c[0], hy + int(36 * s), int(6 * s), s, teeth=8)

    # === ABOVE-HEAD royal CROWN — brass skull on clockwork gear-spire =========
    skull_spire(surf, head_c[0], hy + int(1 * s), int(13 * s), s, night_rim=night_rim)


# -- the boxed copper-column -> pillar mirror ---------------------------------
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """A stacked riveted copper-plate column with periodic gear-ring lashings —
    a direct continuation of the king's torso plates + joint gears. WHY this
    tiles cleanly: each segment is a boxed plate pair cinched by a gear-ring, and
    the gap-cap fans into a small machine-head crowned by a brass gear-eye + a
    skull-spire stub (the creature-derived gap edge, mirrored top<->bottom)."""
    shaft_w = int(20 * s)
    pygame.draw.rect(surf, IRON_D, (cx - int(4 * s), top, int(8 * s), bot - top))

    pitch = int(30 * s)
    cap_room = int(46 * s)
    if cap == "bottom":
        b0, b1 = top + int(10 * s), bot - cap_room
    else:
        b0, b1 = top + cap_room, bot - int(10 * s)
    y = b0
    while y <= b1:
        # a boxed copper plate segment
        rivet_plate(surf, cx - shaft_w // 2, int(y - pitch * 0.42),
                    shaft_w, int(pitch * 0.78), COPPER, s)
        # a thin oxblood inlay stripe down the centre of the plate
        rivet_plate(surf, cx - int(4 * s), int(y - pitch * 0.30),
                    int(8 * s), int(pitch * 0.54), COPPER, s, rivets=False, inlay=True)
        verd_ticks(surf, cx - shaft_w * 0.4, int(y + pitch * 0.30),
                   shaft_w * 0.8, s, n=3)
        # a gear-ring lashing cinching the segment joint
        gear_ring(surf, cx, int(y + pitch * 0.40), int(8 * s), s, teeth=9)
        y += pitch

    cap_y = (bot - int(30 * s)) if cap == "bottom" else (top + int(30 * s))
    fan_dir = -1 if cap == "bottom" else 1
    # the gap-cap machine-head block
    head_h = int(26 * s)
    hy = cap_y - (head_h if fan_dir < 0 else 0)
    rivet_plate(surf, cx - int(17 * s), hy, int(34 * s), head_h, COPPER, s)
    # a brass gear-eye on the cap (the creature focal echoed at the gap edge)
    eye_c = (cx, hy + head_h // 2)
    pygame.draw.circle(surf, INK, eye_c, int(8 * s))
    pygame.draw.circle(surf, COPPER_DD, eye_c, int(7 * s))
    gear_ring(surf, eye_c[0], eye_c[1], int(5 * s), s, teeth=9, color=BRASS, hub=False)
    pygame.draw.circle(surf, BRASS_BR, eye_c, int(3 * s))
    # a small skull-spire stub pointing into the gap — echoes the king's crown:
    # one bold stroke + a chunky brass skull block with sockets + a jaw notch.
    spr_base = hy if fan_dir < 0 else hy + head_h
    sw = max(1, int(2.4 * s))
    sp = [(cx - sw, spr_base), (cx + sw, spr_base),
          (cx + sw, spr_base + fan_dir * int(11 * s)),
          (cx - sw, spr_base + fan_dir * int(11 * s))]
    triad_blob(surf, BRASS, sp, ow=max(1, int(1.0 * s)))
    sk_c_y = spr_base + fan_dir * int(16 * s)
    skw = int(11 * s)
    skh = int(9 * s)
    skull = [(cx - skw // 2, sk_c_y - skh // 2 + int(skh * 0.18)),
             (cx - int(skw * 0.32), sk_c_y - skh // 2),
             (cx + int(skw * 0.32), sk_c_y - skh // 2),
             (cx + skw // 2, sk_c_y - skh // 2 + int(skh * 0.18)),
             (cx + skw // 2, sk_c_y + int(skh * 0.10)),
             (cx + int(skw * 0.24), sk_c_y + skh // 2),
             (cx - int(skw * 0.24), sk_c_y + skh // 2),
             (cx - skw // 2, sk_c_y + int(skh * 0.10))]
    triad_blob(surf, BRASS_BR, skull, ow=max(1, int(1.0 * s)))
    er = max(1, int(skw * 0.16))
    for sg in (-1, 1):
        pygame.draw.circle(surf, IRON_D,
                           (cx + sg * int(skw * 0.22), sk_c_y - int(skh * 0.06)), er)
    pygame.draw.line(surf, INK, (cx, sk_c_y + int(skh * 0.18)),
                     (cx, sk_c_y + int(skh * 0.42)), max(1, int(1.0 * s)))


# -- compose the review sheet -------------------------------------------------
SS = 6


def vgrad(surf, rect, top_col, bot_col):
    x, y, w, h = rect
    for j in range(h):
        pygame.draw.line(surf, lerp(top_col, bot_col, j / max(1, h - 1)),
                         (x, y + j), (x + w, y + j))


def load_fonts():
    """FONT is five levels up from this script; SysFont fallback if missing."""
    base = os.path.dirname(os.path.abspath(__file__))
    fp = os.path.join(base, "..", "..", "..", "..", "..",
                      "game", "assets", "LiberationSans-Bold.ttf")
    try:
        return (pygame.font.Font(fp, 30), pygame.font.Font(fp, 17),
                pygame.font.Font(fp, 12))
    except Exception:
        return (pygame.font.SysFont("DejaVu Sans", 30, bold=True),
                pygame.font.SysFont("DejaVu Sans", 17, bold=True),
                pygame.font.SysFont("DejaVu Sans", 12))


def render_hero():
    big = pygame.Surface((360 * SS, 470 * SS), pygame.SRCALPHA)
    draw_automaton(big, 180 * SS, 250 * SS, 1.78 * SS)
    small = pygame.transform.smoothscale(big, (360, 470))
    return grow_outline(small, INK + (255,), 1)


def main():
    W, H = 1180, 820
    font_big, font, font_sm = load_fonts()

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    pygame.draw.rect(sheet, PANEL, (0, 0, W, 56))
    sheet.blit(font_big.render("OXBLOOD AUTOMATON KING", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "Skull-Kings-II  ·  rigid BLOCKY humanoid machine · riveted copper plates + peg legs + square pauldrons · "
        "circular GEAR-RINGS at joints · brass gear-eye focal · CHUNKY skull-on-gear-spire crown (brightest warm) · round 2",
        True, LABEL_DIM), (360, 26))

    # === (a) BIG HERO =========================================================
    hero = render_hero()
    sheet.blit(hero, (14, 92))
    sheet.blit(font.render("Creature - hero", True, LABEL), (110, 566))
    sheet.blit(font_sm.render("Boxy copper machine: square torso + pauldrons, PEG LEGS, two stiff geometric", True, LABEL_DIM), (14, 590))
    sheet.blit(font_sm.render("arms w/ gear-elbows. Circular GEAR-RINGS at every joint (the de-collider).", True, LABEL_DIM), (14, 606))
    sheet.blit(font_sm.render("CHUNKY brass SKULL on a bold gear-spire = crown + brightest warm value; torso gear-eye demoted to 2nd focal.", True, LABEL_DIM), (14, 622))

    # === (b) PILLAR assembled - mirrored ======================================
    pcx = 470
    top_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(top_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="bottom")
    top_seg = grow_outline(pygame.transform.smoothscale(top_big, (150, 250)), INK + (255,), 1)
    sheet.blit(top_seg, (pcx, 86))
    bot_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(bot_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="top")
    bot_seg = grow_outline(pygame.transform.smoothscale(bot_big, (150, 250)), INK + (255,), 1)
    sheet.blit(bot_seg, (pcx, 86 + 250 + 96))
    pygame.draw.rect(sheet, (60, 64, 72), (pcx + 8, 86 + 250, 134, 96))
    sheet.blit(font_sm.render("GAP", True, LABEL_DIM), (pcx + 56, 86 + 250 + 40))
    sheet.blit(font.render("Pillar - copper plate column", True, LABEL), (pcx - 4, 690))
    sheet.blit(font_sm.render("stacked riveted plates + oxblood inlay stripe,", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("gear-ring lashings; gap-cap machine-head w/", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("gear-eye + skull-spire (mirrored top<->bottom)", True, LABEL_DIM), (pcx - 4, 746))

    # === (c) TRUE 32px chips on day + night sky + SILHOUETTE proof =============
    panel_x = 660
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 560))
    sheet.blit(font.render("True 32px gameplay-scale chip", True, LABEL), (panel_x + 16, 96))

    def chip32(night=False):
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        # WHY night_rim is targeted (round 2): the warm halo now rides the SKULL +
        # spire only (drawn inside skull_spire), so the crown survives the dim
        # night sky without globally bleaching the body — the skull, not the whole
        # figure, is what must stay legible as the brightest warm value.
        draw_automaton(big, 48 * SS, 52 * SS, (32 / 124.0) * SS, night_rim=night)
        small = pygame.transform.smoothscale(big, (96, 96))
        if night:
            # a faint warm body-edge + crisp ink keyline so the dimmed copper mass
            # still parts from the night sky (the loud warm rim lives on the skull)
            base = grow_outline(small, COPPER_D + (210,), 1)
            return grow_outline(base, INK + (220,), 1)
        return grow_outline(small, INK + (255,), 1)

    day_chip = chip32(night=False)
    night_chip = chip32(night=True)

    day_y = 128
    vgrad(sheet, (panel_x + 20, day_y, 150, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, day_y, 150, 150), 1)
    sheet.blit(day_chip, (panel_x + 20 + 27, day_y + 27))
    sheet.blit(font_sm.render("32px on day sky", True, LABEL), (panel_x + 20, day_y + 156))

    night_y = day_y + 184
    vgrad(sheet, (panel_x + 20, night_y, 150, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, night_y, 150, 150), 1)
    sheet.blit(night_chip, (panel_x + 20 + 27 - 1, night_y + 27 - 1))
    sheet.blit(font_sm.render("32px night (warm rim on SKULL+spire)", True, LABEL_DIM), (panel_x + 20, night_y + 156))

    # silhouette proof - blacked-out hero so the blocky machine read is checked
    def silhouette():
        big = pygame.Surface((150 * SS, 200 * SS), pygame.SRCALPHA)
        draw_automaton(big, 75 * SS, 96 * SS, 1.28 * SS)
        small = pygame.transform.smoothscale(big, (150, 200))
        mask = pygame.mask.from_surface(small)
        sil = pygame.Surface((150, 200), pygame.SRCALPHA)
        solid = mask.to_surface(setcolor=(18, 18, 20, 255), unsetcolor=(0, 0, 0, 0))
        sil.blit(solid, (0, 0))
        return sil

    sil_x = panel_x + 196
    pygame.draw.rect(sheet, (210, 212, 216), (sil_x, day_y, 150, 200))
    pygame.draw.rect(sheet, INK, (sil_x, day_y, 150, 200), 1)
    sheet.blit(silhouette(), (sil_x, day_y))
    sheet.blit(font_sm.render("silhouette proof", True, LABEL_DIM), (sil_x, day_y + 204))
    sheet.blit(font_sm.render("(blocky humanoid + spire)", True, LABEL_DIM), (sil_x, day_y + 220))

    def pillar_chip32():
        big = pygame.Surface((44 * SS, 130 * SS), pygame.SRCALPHA)
        draw_pillar(big, 22 * SS, 2 * SS, 128 * SS, 0.34 * SS, cap="bottom")
        small = pygame.transform.smoothscale(big, (44, 130))
        return grow_outline(small, INK + (255,), 1)

    pc = pillar_chip32()
    px2 = sil_x + 168
    vgrad(sheet, (px2, day_y, 56, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (px2, day_y, 56, 150), 1)
    sheet.blit(pc, (px2 + 6, day_y + 10))
    vgrad(sheet, (px2, night_y, 56, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (px2, night_y, 56, 150), 1)
    sheet.blit(pc, (px2 + 6, night_y + 10))
    sheet.blit(font_sm.render("pillar", True, LABEL_DIM), (px2 + 4, day_y - 16))
    sheet.blit(font_sm.render("gap-cap", True, LABEL_DIM), (px2 - 2, night_y - 16))

    # palette swatches
    sheet.blit(font.render("Pinned palette", True, LABEL), (panel_x + 16, 510))
    swatches = [
        (COPPER, "patinated copper"), (COPPER_D, "copper shade"),
        (OXBLOOD, "oxblood lacquer"), (OXBLOOD_BR, "oxblood lit"),
        (BRASS, "brass gear-eye"), (BRASS_BR, "brass hot core"),
        (VERD, "verdigris tick"), (IRON, "iron rivet"),
        (COPPER_SH, "copper sheen"), (INK, "ink keyline"),
    ]
    sxp, syp = panel_x + 16, 538
    for i, (c, name) in enumerate(swatches):
        col, row = i % 2, i // 2
        rx = sxp + col * 188
        ry = syp + row * 24
        pygame.draw.rect(sheet, INK, (rx - 1, ry - 1, 20, 20))
        pygame.draw.rect(sheet, c, (rx, ry, 18, 18))
        sheet.blit(font_sm.render(name, True, LABEL), (rx + 26, ry + 3))

    pygame.draw.rect(sheet, PANEL, (14, 770, W - 28, 40))
    sheet.blit(font_sm.render(
        "RIGID BLOCKY HUMANOID MACHINE: peg legs + square pauldrons + circular GEAR-RINGS (vs Bismuth's limbless angular crystal).  "
        "WARM copper dominant mass; oxblood = thin inlays; verdigris = a FEW patina ticks at recessed seams.  CHUNKY brass SKULL crown = brightest warm value (wins ties); torso gear-eye demoted.  "
        "SS=6 supersample -> smoothscale · procedural-only.",
        True, LABEL_DIM), (26, 783))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_2.png")
    pygame.image.save(sheet, out)
    print("wrote", out)
    self_check()


def self_check():
    """Verify (round 2) that the CROWN SKULL — not the torso gear-eye — owns the
    single brightest pixel, since on a Skull King the skull must win ties, and
    that the body stays WARM (copper) with verdigris a tiny fraction (never twins
    Malachite). The crown sits above the head, so the brightest pixel must land in
    the upper band of the figure."""
    cx, cy = 200, 280
    surf = pygame.Surface((400, 560), pygame.SRCALPHA)
    draw_automaton(surf, cx, cy, 2.0)
    px = pygame.surfarray.pixels3d(surf)
    a = pygame.surfarray.pixels_alpha(surf)
    w, h = surf.get_size()
    best_lum, best_xy = -1, (0, 0)
    warm_n, cool_n = 0, 0
    for x in range(0, w, 2):
        for yy in range(0, h, 2):
            if a[x, yy] < 40:
                continue
            r, g, b = int(px[x, yy][0]), int(px[x, yy][1]), int(px[x, yy][2])
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            if lum > best_lum:
                best_lum, best_xy = lum, (x, yy)
            if r > g and r > b and r > 90:        # warm: copper/brass/oxblood
                warm_n += 1
            if g > r and g > b and g > 90:        # cool: verdigris green
                cool_n += 1
    bx, by = best_xy
    r, g, b = int(px[bx, by][0]), int(px[bx, by][1]), int(px[bx, by][2])
    is_brass = (r > 220 and g > 175 and b < 215 and r >= b)
    # the crown skull sits well above the head centre; the torso eye is below it.
    head_top = cy - int(34 * 2.0) - int(18 * 2.0)     # top of the face plate
    in_crown = by < head_top
    del px, a
    print("self-check: brightest pixel @", best_xy, "rgb", (r, g, b),
          "lum %.0f" % best_lum, "-> brass-core?", is_brass,
          "-> in CROWN band (above head)?", in_crown)
    print("self-check: warm px ~%d  vs cool px ~%d  -> cool fraction %.3f (must be small)"
          % (warm_n, cool_n, cool_n / max(1, warm_n + cool_n)))


if __name__ == "__main__":
    main()
