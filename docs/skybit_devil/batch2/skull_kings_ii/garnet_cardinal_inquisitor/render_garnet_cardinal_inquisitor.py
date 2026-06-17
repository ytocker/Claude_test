"""
Round-1 concept renderer for the GARNET CARDINAL INQUISITOR — a royal skull-KING
of the second Skull-Kings batch (DISCRETION line: no soul-cradle, 2 arms).
Headless Pygame; ELEVATED pipeline (supersample SS=6 -> smoothscale) so the thin
chain-work + the gable shrine survive the downscale. Keeps the house grammar
cloned from the regent_koschei sibling: flat triad shading (dark-core -> fill ->
top-left sheen), a hard 1-2px ink keyline (28,22,30), 1px alpha-grown outline,
chibi scary-cute proportions; procedural-only (no gradients/PNGs).

WHY this KIND is a TRUE HAIRPIN, not a candle: the de-collision lock against the
reserved Marble Pontiff is the SILHOUETTE. The cowl peak is pushed clearly
FORWARD of the toe-line and the skull head drops well BELOW the shoulder crest,
so the blackout reads as an unmistakable leaning HOOK — a person folded forward
at the waist, never an upright pillar. The robe falls as one dominant oxblood
mass; every other element is a thin accent riding that mass.

WHY the bone face owns the brightest pixel WITH a garnet eye-gem focal: the hard
gate wants ONE dominant body mass (the garnet robe) + thin accents, the named
focal being the single brightest/most-saturated point. The cool bone face is the
high-VALUE region (so he never vanishes on a dark night sky), but the garnet
eye-gem is the single most-SATURATED warm point set into it — the lit jewel of an
inquisitor sighting his mark. Antique-silver stole-chains are the only other
accent, kept thin + cool so the oxblood robe keeps the whole warm mass.

WHY a standalone script under docs/: review art must never enter the shipped
bundle, so it reuses only colour math + the triad/outline helpers re-implemented
inline, not runtime sprite modules.
"""
import math
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

# -- PINNED PALETTE (locked brief) --------------------------------------------
# oxblood-garnet robe is the dominant MASS; everything else is a thin accent.
ROBE      = (120,  28,  46)   # oxblood-garnet robe (the dominant fill)
ROBE_D    = ( 78,  18,  32)   # robe dark-core / fold shadow
ROBE_DD   = ( 50,  12,  22)   # deepest robe hollow (cowl interior, under-folds)
ROBE_SH   = (168,  56,  78)   # robe top-left rim-sheen (a lifted oxblood, not pink)
# cool BONE face — the high-VALUE region so he survives a dark night sky.
BONE      = (214, 206, 196)   # cool bone face (lighter than robe, never warm)
BONE_D    = (158, 150, 142)   # bone shade / socket rim
BONE_DD   = ( 96,  92,  88)   # deepest bone hollow (eye sockets, nasal)
BONE_SH   = (240, 236, 230)   # bone top-left sheen
# antique-silver stole-chains — a THIN cool linear accent ONLY.
SILVER    = (176, 180, 188)
SILVER_BR = (224, 228, 234)   # thin silver specular pip
SILVER_D  = (110, 114, 124)   # recessed chain shadow
# the SINGLE saturated focal — the garnet eye-gem (the inquisitor's sighting jewel)
GARNET    = (196,  40,  72)
GARNET_BR = (244, 120, 150)   # hot garnet inner
GARNET_HOT= (255, 196, 210)   # hottest garnet pip (the single brightest-warm pixel)
GARNET_D  = (132,  22,  46)
INK       = ( 28,  22,  30)   # hard ink keyline

BG        = ( 96, 100, 108)   # neutral grey review backdrop
PANEL     = ( 74,  78,  88)
DAY_SKY_T = (120, 196, 236)
DAY_SKY_B = (196, 232, 244)
NIGHT_T   = ( 22,  26,  54)
NIGHT_B   = ( 48,  44,  82)
LABEL     = (238, 240, 244)
LABEL_DIM = (188, 196, 208)


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


def bone_limb(surf, p0, p1, p2, thick, s, joint=True):
    for (a, b) in ((p0, p1), (p1, p2)):
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = max(1.0, math.hypot(dx, dy))
        nx, ny = -dy / L * thick / 2, dx / L * thick / 2
        quad = [(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny),
                (b[0] - nx, b[1] - ny), (a[0] - nx, a[1] - ny)]
        triad_blob(surf, BONE, quad,
                   sheen_pts=[(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny),
                              (b[0] + nx * 0.3, b[1] + ny * 0.3),
                              (a[0] + nx * 0.3, a[1] + ny * 0.3)],
                   ow=max(1, int(thick * 0.18)))
    if joint:
        triad_circle(surf, BONE, p1, int(thick * 0.62), ow=max(1, int(1.2 * s)),
                     core=False)


# -- antique-silver STOLE-CHAIN primitives (thin cool accents) ----------------
def silver_link(surf, cx, cy, r, s):
    """One tiny antique-silver chain bead. WHY a dome with a cool specular pip and
    NO warm tone: the stole-chain is the only accent allowed beside the eye-gem;
    keeping it cool + thin means it reads as worked metal along the robe yet never
    consolidates into a second mass that competes with the garnet focal."""
    pygame.draw.circle(surf, INK, (cx, cy), r + max(1, int(0.8 * s)))
    pygame.draw.circle(surf, SILVER_D, (cx, cy), r)
    pygame.draw.circle(surf, SILVER, (cx, cy), int(r * 0.82))
    pygame.draw.circle(surf, SILVER_BR, (cx - int(r * 0.3), cy - int(r * 0.34)),
                       max(1, int(r * 0.34)))


def silver_chain(surf, pts, r, s):
    """A thin silver stole-chain strung along a polyline of anchor points."""
    if len(pts) >= 2:
        pygame.draw.lines(surf, SILVER_D, False, pts, max(1, int(1.2 * s)))
        pygame.draw.lines(surf, SILVER, False, pts, max(1, int(0.8 * s)))
    for (x, y) in pts:
        silver_link(surf, int(x), int(y), r, s)


# -- the garnet eye-gem: the single most-saturated warm point -----------------
def garnet_gem(surf, cx, cy, r, s, halo=True):
    """The inquisitor's sighting jewel. WHY it carries a faceted bright pip but a
    SMALL, dim halo: the gate wants ONE named focal as the brightest/most-warm
    point. A tight GARNET_HOT pip guarantees the single brightest-warm pixel sits
    here; the halo is kept small so the focal is a precise point, not a glow that
    smears into the robe at 32px."""
    if halo:
        for (rr, a) in ((r * 2.6, 30), (r * 1.9, 48), (r * 1.4, 78)):
            hs = pygame.Surface((int(rr * 2) + 4, int(rr * 2) + 4), pygame.SRCALPHA)
            pygame.draw.circle(hs, GARNET_BR + (a,), (int(rr) + 2, int(rr) + 2), int(rr))
            surf.blit(hs, (cx - int(rr) - 2, cy - int(rr) - 2))
    pygame.draw.circle(surf, INK, (cx, cy), r + max(1, int(1.0 * s)))
    pygame.draw.circle(surf, GARNET_D, (cx, cy), r)
    pygame.draw.circle(surf, GARNET, (cx, cy), int(r * 0.82))
    pygame.draw.circle(surf, GARNET_BR,
                       (cx - int(r * 0.18), cy - int(r * 0.20)), max(1, int(r * 0.50)))
    pygame.draw.circle(surf, GARNET_HOT,
                       (cx - int(r * 0.28), cy - int(r * 0.30)), max(1, int(r * 0.26)))


# -- the GABLED SKULL-RELIQUARY crown perched on the cowl ----------------------
def reliquary_gable(surf, cx, base_y, w, h, s):
    """A tiny pointed-arch shrine enthroning a garnet-eyed skull. WHY a gable +
    enthroned skull rather than a spike crown: it is the above-head royal tell
    and the lineage signature, and its peaked silhouette reads as a SHRINE even at
    32px (a triangle topped point above the rounded cowl). The skull inside lifts
    to bone VALUE so it stays legible against a night sky; its garnet eye echoes —
    but stays smaller/dimmer than — the face's eye-gem, so the face keeps the
    single brightest-warm focal."""
    half = w * 0.5
    # the shrine housing: two jambs + a steep pediment (oxblood worked stone)
    house = [(cx - half, base_y),
             (cx - half, base_y - h * 0.52),
             (cx, base_y - h),
             (cx + half, base_y - h * 0.52),
             (cx + half, base_y)]
    triad_blob(surf, ROBE, house,
               core_pts=[(cx + half * 0.18, base_y),
                         (cx + half * 0.18, base_y - h * 0.5),
                         (cx + half, base_y - h * 0.5),
                         (cx + half, base_y)],
               sheen_pts=[(cx - half, base_y),
                          (cx - half, base_y - h * 0.5),
                          (cx - half * 0.32, base_y - h * 0.86),
                          (cx - half * 0.5, base_y - h * 0.5)],
               ow=max(1, int(1.3 * s)))
    # a thin silver finial cross-bead at the gable peak (the reliquary tell)
    pygame.draw.line(surf, SILVER, (cx, base_y - h), (cx, base_y - h - int(5 * s)),
                     max(1, int(1.3 * s)))
    pygame.draw.line(surf, SILVER, (cx - int(3 * s), base_y - h - int(2 * s)),
                     (cx + int(3 * s), base_y - h - int(2 * s)), max(1, int(1.1 * s)))
    pygame.draw.circle(surf, SILVER_BR, (cx, base_y - h - int(5 * s)), max(1, int(1.2 * s)))
    # the pointed-arch niche cut into the housing (the enthroned recess)
    niche = [(cx - half * 0.56, base_y - h * 0.04),
             (cx - half * 0.56, base_y - h * 0.46),
             (cx, base_y - h * 0.78),
             (cx + half * 0.56, base_y - h * 0.46),
             (cx + half * 0.56, base_y - h * 0.04)]
    pygame.draw.polygon(surf, ROBE_DD, niche)
    pygame.draw.polygon(surf, INK, niche, max(1, int(1.0 * s)))
    # the enthroned skull — small bone dome with two ink sockets; one garnet eye
    sk_c = (cx, base_y - h * 0.30)
    sk_r = max(2, int(half * 0.52))
    triad_circle(surf, BONE, sk_c, sk_r, ow=max(1, int(1.0 * s)), core=False)
    # tiny jaw bump so the dome reads as a SKULL, not a pearl
    pygame.draw.polygon(surf, BONE_D,
                        [(sk_c[0] - int(sk_r * 0.42), sk_c[1] + int(sk_r * 0.5)),
                         (sk_c[0] + int(sk_r * 0.42), sk_c[1] + int(sk_r * 0.5)),
                         (sk_c[0], sk_c[1] + int(sk_r * 0.92))])
    for sgn in (-1, 1):
        pygame.draw.circle(surf, INK,
                           (sk_c[0] + sgn * int(sk_r * 0.42), sk_c[1] - int(sk_r * 0.08)),
                           max(1, int(sk_r * 0.30)))
    # the enthroned skull's garnet eye — kept smaller + dimmer (no big halo) than
    # the face gem so the FACE keeps the single brightest-warm focal.
    garnet_gem(surf, sk_c[0] - int(sk_r * 0.42), sk_c[1] - int(sk_r * 0.08),
               max(1, int(sk_r * 0.24)), s, halo=False)


# -- the hooded forward-stoop inquisitor (TRUE HAIRPIN) -----------------------
def draw_inquisitor(surf, cx, cy, s):
    """Geometry note: the figure is a forward HAIRPIN. The toe-line sits at the
    rear (toward +x is forward). The robe column rises, then the cowl+head FOLD
    forward and DROP below the shoulder crest, so the blackout is a leaning hook.
    cx,cy is the chest/shoulder-crest anchor; the robe falls below, the cowl
    pitches forward-and-down above-and-ahead."""
    # forward = +x. Lay out key anatomy around the chest anchor.
    shoulder_y = cy - int(6 * s)
    hem_y = cy + int(70 * s)
    # the cowl peak is pushed FORWARD of the toe and DOWN below the shoulder.
    cowl_cx = cx + int(30 * s)         # clearly forward of the rear toe-line
    cowl_cy = shoulder_y + int(14 * s) # head dropped BELOW the shoulder crest
    head_c = (cowl_cx + int(2 * s), cowl_cy + int(8 * s))
    hr = int(17 * s)

    # === ROBE HEM + FEET (the rear root of the hook) =========================
    # toe-line sits at the REAR so the forward cowl overhangs it -> hook read.
    toe_x = cx - int(26 * s)
    hem = [(toe_x - int(8 * s), hem_y),
           (cx + int(20 * s), hem_y - int(4 * s)),
           (cx + int(26 * s), hem_y + int(10 * s)),
           (toe_x - int(14 * s), hem_y + int(16 * s))]
    triad_blob(surf, ROBE, hem,
               core_pts=[(cx, hem_y), (cx + int(20 * s), hem_y - int(3 * s)),
                         (cx + int(24 * s), hem_y + int(9 * s)), (cx, hem_y + int(11 * s))],
               ow=max(1, int(1.6 * s)))
    # two bone toe-tips peeking from under the rear hem
    for k in (0, 1):
        fx = toe_x - int(2 * s) + k * int(9 * s)
        triad_circle(surf, BONE, (fx, hem_y + int(13 * s)), int(4 * s),
                     ow=max(1, int(1.0 * s)), core=False)

    # === ROBE COLUMN — the dominant oxblood MASS, leaning forward at the top ===
    # a single tapering bell from the wide hem up to the forward-pitched shoulders.
    robe = [(toe_x - int(6 * s), hem_y + int(4 * s)),          # rear hem
            (cx - int(22 * s), cy + int(20 * s)),              # rear flank
            (cx - int(16 * s), shoulder_y + int(2 * s)),       # rear shoulder
            (cowl_cx - int(20 * s), cowl_cy - int(20 * s)),    # forward cowl shoulder
            (cowl_cx + int(20 * s), cowl_cy - int(14 * s)),    # forward cowl crest
            (cowl_cx + int(22 * s), cowl_cy + int(18 * s)),    # forward cowl front
            (cx + int(30 * s), cy + int(26 * s)),              # forward belly (overhang)
            (cx + int(24 * s), hem_y - int(2 * s))]            # forward hem
    triad_blob(surf, ROBE, robe,
               core_pts=[(cx + int(2 * s), cy + int(24 * s)),
                         (cx + int(28 * s), cy + int(24 * s)),
                         (cx + int(22 * s), hem_y - int(2 * s)),
                         (cx + int(2 * s), hem_y)],
               sheen_pts=[(toe_x - int(4 * s), hem_y),
                          (cx - int(20 * s), cy + int(18 * s)),
                          (cx - int(14 * s), shoulder_y + int(4 * s)),
                          (cx - int(6 * s), shoulder_y + int(8 * s)),
                          (cx - int(8 * s), hem_y)],
               ow=max(1, int(1.8 * s)))
    # vertical fold lines down the robe (thin dark-core seams, the cloth read)
    for fx in (-10, 2, 14):
        pygame.draw.line(surf, ROBE_D,
                         (cx + int(fx * s), cy + int(22 * s)),
                         (cx + int((fx - 6) * s), hem_y), max(1, int(1.4 * s)))

    # === COWL — the forward-and-down hood that makes the hairpin peak =========
    # a deep cowl whose OPENING faces forward-down, framing the dropped skull.
    cowl = [(cowl_cx - int(22 * s), cowl_cy - int(18 * s)),
            (cowl_cx - int(6 * s), cowl_cy - int(26 * s)),    # peak (the forward tip)
            (cowl_cx + int(16 * s), cowl_cy - int(18 * s)),
            (cowl_cx + int(22 * s), cowl_cy + int(6 * s)),
            (cowl_cx + int(10 * s), cowl_cy + int(22 * s)),   # forward-down lip
            (cowl_cx - int(16 * s), cowl_cy + int(18 * s)),
            (cowl_cx - int(24 * s), cowl_cy - int(2 * s))]
    triad_blob(surf, ROBE, cowl,
               core_pts=[(cowl_cx - int(2 * s), cowl_cy - int(18 * s)),
                         (cowl_cx + int(16 * s), cowl_cy - int(16 * s)),
                         (cowl_cx + int(20 * s), cowl_cy + int(6 * s)),
                         (cowl_cx + int(2 * s), cowl_cy + int(16 * s))],
               sheen_pts=[(cowl_cx - int(22 * s), cowl_cy - int(16 * s)),
                          (cowl_cx - int(6 * s), cowl_cy - int(24 * s)),
                          (cowl_cx - int(4 * s), cowl_cy - int(14 * s)),
                          (cowl_cx - int(20 * s), cowl_cy - int(2 * s))],
               ow=max(1, int(1.8 * s)))
    # the dark cowl-interior recess that the bone face sits inside
    inner = [(cowl_cx - int(14 * s), cowl_cy - int(6 * s)),
             (cowl_cx + int(2 * s), cowl_cy - int(14 * s)),
             (cowl_cx + int(16 * s), cowl_cy - int(2 * s)),
             (cowl_cx + int(8 * s), cowl_cy + int(18 * s)),
             (cowl_cx - int(12 * s), cowl_cy + int(12 * s))]
    pygame.draw.polygon(surf, ROBE_DD, inner)

    # === SKULL FACE — the cool high-VALUE bone tucked into the forward cowl ===
    # WHY drawn light + tilted forward-down: night legibility rides on the bone
    # value, and the downward tilt sells the hairpin stoop (a face peering at the
    # floor it points to).
    triad_circle(surf, BONE, head_c, hr, ow=max(2, int(2 * s)))
    # cheek shading
    for sgn in (-1, 1):
        pygame.draw.circle(surf, BONE_D,
                           (head_c[0] + sgn * int(hr * 0.62), head_c[1] + int(hr * 0.34)),
                           int(hr * 0.26))
    # eye sockets — tilted so the forward (right) one carries the garnet gem
    for sgn in (-1, 1):
        ex = head_c[0] + sgn * int(hr * 0.42)
        ey = head_c[1] - int(hr * 0.02) + int(hr * 0.10) * sgn  # forward eye sits lower
        pygame.draw.circle(surf, BONE_DD, (ex, ey), int(hr * 0.34))
        pygame.draw.circle(surf, INK, (ex, ey), int(hr * 0.28))
    # the SINGLE garnet eye-gem set in the FORWARD socket (the named focal)
    fex = head_c[0] + int(hr * 0.42)
    fey = head_c[1] - int(hr * 0.02) + int(hr * 0.10)
    garnet_gem(surf, fex, fey, max(2, int(hr * 0.20)), s, halo=True)
    # angular brow ridges (the inquisitor's glare)
    for sgn in (-1, 1):
        brow = [(head_c[0] + sgn * int(hr * 0.72), head_c[1] - int(hr * 0.30)),
                (head_c[0] + sgn * int(hr * 0.08), head_c[1] - int(hr * 0.06)),
                (head_c[0] + sgn * int(hr * 0.10), head_c[1] + int(hr * 0.02)),
                (head_c[0] + sgn * int(hr * 0.76), head_c[1] - int(hr * 0.18))]
        pygame.draw.polygon(surf, BONE_DD, brow)
    # nasal + clenched teeth
    pygame.draw.polygon(surf, BONE_DD,
                        [(head_c[0] - int(hr * 0.12), head_c[1] + int(hr * 0.30)),
                         (head_c[0] + int(hr * 0.12), head_c[1] + int(hr * 0.30)),
                         (head_c[0], head_c[1] + int(hr * 0.54))])
    my = head_c[1] + int(hr * 0.74)
    pygame.draw.line(surf, INK, (head_c[0] - int(hr * 0.40), my),
                     (head_c[0] + int(hr * 0.42), my + int(hr * 0.06)), max(1, int(2 * s)))
    for k in range(-2, 3):
        pygame.draw.line(surf, INK,
                         (head_c[0] + int(k * hr * 0.17), my - int(hr * 0.06)),
                         (head_c[0] + int(k * hr * 0.17), my + int(hr * 0.10)),
                         max(1, int(1 * s)))

    # === STOLE-CHAINS — thin antique-silver swag down the robe front ==========
    # WHY a shallow front swag from the cowl shoulders to the belly: it is the
    # only other accent, kept cool + thin so the oxblood robe keeps the warm mass.
    swag = [(cowl_cx - int(16 * s), cowl_cy + int(12 * s)),
            (cx + int(2 * s), cy + int(28 * s)),
            (cx + int(20 * s), cy + int(20 * s))]
    silver_chain(surf, swag, max(2, int(2.2 * s)), s)

    # === ARMS — TWO. left arm tucked into the robe; right arm POINTS forward ===
    # the menace: one bony hand jabs HORIZONTAL against the vertical robe.
    arm_th = int(6 * s)
    # tucked left arm (rear), low-key, just establishes the second arm
    l_sh = (cx - int(12 * s), shoulder_y + int(10 * s))
    l_el = (cx - int(20 * s), cy + int(26 * s))
    l_hand = (cx - int(8 * s), cy + int(40 * s))
    bone_limb(surf, l_sh, l_el, l_hand, arm_th, s)
    # the POINTING right arm — driven forward off the cowl, ending in a level jab
    r_sh = (cowl_cx - int(2 * s), cowl_cy + int(16 * s))
    r_el = (cx + int(40 * s), cy + int(20 * s))
    r_wrist = (cx + int(62 * s), cy + int(18 * s))
    bone_limb(surf, r_sh, r_el, r_wrist, arm_th, s, joint=True)
    # the pointing HAND: a fist with ONE extended index finger, dead horizontal
    fist_c = (r_wrist[0] + int(2 * s), r_wrist[1])
    triad_circle(surf, BONE, fist_c, int(5 * s), ow=max(1, int(1.2 * s)), core=False)
    finger = [(fist_c[0], fist_c[1] - int(3 * s)),
              (fist_c[0] + int(18 * s), fist_c[1] - int(2 * s)),
              (fist_c[0] + int(18 * s), fist_c[1] + int(2 * s)),
              (fist_c[0], fist_c[1] + int(3 * s))]
    triad_blob(surf, BONE, finger,
               sheen_pts=[(fist_c[0], fist_c[1] - int(3 * s)),
                          (fist_c[0] + int(18 * s), fist_c[1] - int(2 * s)),
                          (fist_c[0] + int(18 * s), fist_c[1] - int(1 * s)),
                          (fist_c[0], fist_c[1] - int(1 * s))],
               ow=max(1, int(1.2 * s)))
    # the fingertip bone-knuckle (the precise end of the jab)
    triad_circle(surf, BONE, (fist_c[0] + int(18 * s), fist_c[1]), int(2 * s),
                 ow=max(1, int(0.9 * s)), core=False, sheen=False)

    # === the GABLED SKULL-RELIQUARY crown perched on the cowl peak ============
    reliquary_gable(surf, cowl_cx - int(4 * s), cowl_cy - int(22 * s),
                    int(26 * s), int(28 * s), s)


# -- the reliquary-column -> pillar mirror, from the king's own forms ---------
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """A stacked oxblood RELIQUARY column — repeating gable niches strung with a
    silver chain — capped at the gap by a single garnet-skull gable lifted off the
    king's own crown. Mirrors top<->bottom on-axis."""
    shaft_w = int(15 * s)
    # the dark robe-core spine running the full shaft
    pygame.draw.rect(surf, ROBE_DD, (cx - int(3 * s), top, int(6 * s), bot - top))

    pitch = int(28 * s)
    cap_room = int(40 * s)
    if cap == "bottom":
        b0, b1 = top + int(8 * s), bot - cap_room
    else:
        b0, b1 = top + cap_room, bot - int(8 * s)
    y = b0
    while y <= b1:
        # one robe segment with a small recessed gable niche (the reliquary motif)
        seg = [(cx - shaft_w, y - int(11 * s)),
               (cx + shaft_w, y - int(11 * s)),
               (cx + shaft_w - int(2 * s), y + int(11 * s)),
               (cx - shaft_w + int(2 * s), y + int(11 * s))]
        triad_blob(surf, ROBE, seg,
                   sheen_pts=[(cx - shaft_w, y - int(11 * s)),
                              (cx - int(2 * s), y - int(11 * s)),
                              (cx - int(2 * s), y + int(11 * s)),
                              (cx - shaft_w, y + int(11 * s))],
                   ow=max(1, int(1.2 * s)))
        niche = [(cx - int(7 * s), y + int(8 * s)),
                 (cx - int(7 * s), y - int(2 * s)),
                 (cx, y - int(9 * s)),
                 (cx + int(7 * s), y - int(2 * s)),
                 (cx + int(7 * s), y + int(8 * s))]
        pygame.draw.polygon(surf, ROBE_DD, niche)
        pygame.draw.polygon(surf, INK, niche, max(1, int(1.0 * s)))
        y += pitch
    # the thin silver stole-chain threaded down the shaft centre
    cdir = -1 if cap == "bottom" else 1
    chain_pts = [(cx, top + int(6 * s) if cap == "bottom" else top + cap_room - int(6 * s))]
    yy = b0
    while yy <= b1:
        chain_pts.append((cx, yy))
        yy += pitch
    silver_chain(surf, chain_pts, max(2, int(2.0 * s)), s)

    # === gap-edge CAP — a single garnet-skull gable from the king's crown ======
    cap_y = (bot - int(30 * s)) if cap == "bottom" else (top + int(30 * s))
    fan_dir = -1 if cap == "bottom" else 1
    # a broad oxblood gable lip facing the gap
    lip = [(cx - int(20 * s), cap_y),
           (cx + int(20 * s), cap_y),
           (cx + int(16 * s), cap_y - fan_dir * int(12 * s)),
           (cx, cap_y - fan_dir * int(22 * s)),
           (cx - int(16 * s), cap_y - fan_dir * int(12 * s))]
    triad_blob(surf, ROBE, lip, ow=max(1, int(1.3 * s)))
    # mount the king's reliquary gable on the cap, oriented toward the gap
    if cap == "bottom":
        reliquary_gable(surf, cx, cap_y - int(2 * s), int(24 * s), int(26 * s), s)
    else:
        # for the top segment the gable points DOWN into the gap (mirrored)
        sub = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        reliquary_gable(sub, cx, int(40 * s), int(24 * s), int(26 * s), s)
        flipped = pygame.transform.flip(sub, False, True)
        # align the flipped gable's base to the cap lip
        surf.blit(flipped, (0, cap_y - (surf.get_height() - int(40 * s))))


# -- compose the review sheet -------------------------------------------------
SS = 6


def render_creature_chip(boxw, boxh, draw_cx, draw_cy, scale):
    big = pygame.Surface((boxw * SS, boxh * SS), pygame.SRCALPHA)
    draw_inquisitor(big, draw_cx * SS, draw_cy * SS, scale * SS)
    small = pygame.transform.smoothscale(big, (boxw, boxh))
    return grow_outline(small, INK + (255,), 1)


def vgrad(surf, rect, top_col, bot_col):
    x, y, w, h = rect
    for j in range(h):
        pygame.draw.line(surf, lerp(top_col, bot_col, j / max(1, h - 1)),
                         (x, y + j), (x + w, y + j))


def load_fonts():
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


def main():
    W, H = 1180, 820
    font_big, font, font_sm = load_fonts()

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    pygame.draw.rect(sheet, PANEL, (0, 0, W, 56))
    sheet.blit(font_big.render("GARNET CARDINAL INQUISITOR", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "skull-KING (discretion line, 2 arms) · hooded FORWARD-STOOP HAIRPIN · gabled skull-reliquary crown · "
        "pointing hand · garnet eye-gem focal · round 1",
        True, LABEL_DIM), (480, 26))

    # === (a) BIG HERO =========================================================
    hero = render_creature_chip(360, 470, 150, 230, 1.70)
    sheet.blit(hero, (14, 92))
    sheet.blit(font.render("Creature — hero", True, LABEL), (110, 566))
    sheet.blit(font_sm.render("TRUE HAIRPIN: cowl peak forward of the toe-line, skull dropped below the", True, LABEL_DIM), (14, 590))
    sheet.blit(font_sm.render("shoulder crest -> a leaning HOOK. ONE oxblood robe mass; thin silver stole-", True, LABEL_DIM), (14, 606))
    sheet.blit(font_sm.render("chains + a level POINTING finger; garnet eye-gem = single brightest-warm point.", True, LABEL_DIM), (14, 622))

    # === (b) PILLAR assembled — mirrored ======================================
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
    sheet.blit(font.render("Pillar — reliquary column", True, LABEL), (pcx - 4, 690))
    sheet.blit(font_sm.render("stacked oxblood gable niches + silver stole-chain;", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("garnet-skull gable cap from the king's own crown", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("(mirrored top<->bottom, on-axis, bottom-rooted)", True, LABEL_DIM), (pcx - 4, 746))

    # === (c) TRUE 32px chips + silhouette proof ===============================
    panel_x = 660
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 560))
    sheet.blit(font.render("True 32px gameplay-scale chip", True, LABEL), (panel_x + 16, 96))

    def chip32(night=False):
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_inquisitor(big, 40 * SS, 46 * SS, (32 / 150.0) * SS)
        small = pygame.transform.smoothscale(big, (96, 96))
        # WHY a thin cool SILVER rim on the night chip (not a warm one): the dark
        # oxblood robe can sink into a dark night sky; a cool silver halo carries
        # the hooked silhouette while keeping the garnet gem the brightest-warm
        # point and not adding a second warm read.
        if night:
            base = grow_outline(small, SILVER_D + (255,), 2)
            return grow_outline(base, INK + (200,), 1)
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
    sheet.blit(font_sm.render("32px on night sky (silver rim)", True, LABEL_DIM), (panel_x + 20, night_y + 156))

    # silhouette proof — blacked-out hero so the HAIRPIN hook read is checked
    def silhouette():
        big = pygame.Surface((170 * SS, 200 * SS), pygame.SRCALPHA)
        draw_inquisitor(big, 70 * SS, 92 * SS, 1.20 * SS)
        small = pygame.transform.smoothscale(big, (170, 200))
        mask = pygame.mask.from_surface(small)
        sil = pygame.Surface((170, 200), pygame.SRCALPHA)
        solid = mask.to_surface(setcolor=(18, 18, 20, 255), unsetcolor=(0, 0, 0, 0))
        sil.blit(solid, (0, 0))
        return sil

    sil_x = panel_x + 196
    pygame.draw.rect(sheet, (210, 212, 216), (sil_x, day_y, 170, 200))
    pygame.draw.rect(sheet, INK, (sil_x, day_y, 170, 200), 1)
    sheet.blit(silhouette(), (sil_x, day_y))
    sheet.blit(font_sm.render("silhouette proof", True, LABEL_DIM), (sil_x, day_y + 204))
    sheet.blit(font_sm.render("(leaning HOOK, not a candle)", True, LABEL_DIM), (sil_x, day_y + 220))

    def pillar_chip32():
        big = pygame.Surface((40 * SS, 130 * SS), pygame.SRCALPHA)
        draw_pillar(big, 20 * SS, 2 * SS, 128 * SS, 0.32 * SS, cap="bottom")
        small = pygame.transform.smoothscale(big, (40, 130))
        return grow_outline(small, INK + (255,), 1)

    pc = pillar_chip32()
    px2 = sil_x + 188
    vgrad(sheet, (px2, day_y, 56, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (px2, day_y, 56, 150), 1)
    sheet.blit(pc, (px2 + 8, day_y + 10))
    vgrad(sheet, (px2, night_y, 56, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (px2, night_y, 56, 150), 1)
    sheet.blit(pc, (px2 + 8, night_y + 10))
    sheet.blit(font_sm.render("pillar", True, LABEL_DIM), (px2 + 4, day_y - 16))
    sheet.blit(font_sm.render("gap-cap", True, LABEL_DIM), (px2 - 2, night_y - 16))

    # palette swatches
    sheet.blit(font.render("Pinned palette", True, LABEL), (panel_x + 16, 510))
    swatches = [
        (ROBE, "oxblood-garnet robe"), (ROBE_D, "robe shade"),
        (BONE, "cool bone face"), (BONE_SH, "bone sheen"),
        (SILVER, "antique-silver chain"), (SILVER_BR, "silver pip"),
        (GARNET, "garnet eye-gem"), (GARNET_HOT, "garnet hot pip"),
        (ROBE_DD, "cowl interior"), (INK, "ink keyline"),
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
        "DISCRETION skull-KING: forward-stoop HAIRPIN (de-collides the upright Marble Pontiff).  ONE oxblood robe mass; silver stole-chain + pointing finger are thin accents; "
        "garnet eye-gem = single brightest-warm focal; gabled skull-reliquary crown is the above-head tell.  SS=6 supersample -> smoothscale · procedural-only.",
        True, LABEL_DIM), (26, 783))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(sheet, out)
    print("wrote", out)
    self_check()


def self_check():
    """Render the hero alone and verify the single most-SATURATED warm pixel sits
    inside the garnet eye-gem, and that the bone face holds high value for night
    legibility (peak bone value high)."""
    surf = pygame.Surface((400, 540), pygame.SRCALPHA)
    draw_inquisitor(surf, 170, 270, 1.9)
    px = pygame.surfarray.pixels3d(surf)
    a = pygame.surfarray.pixels_alpha(surf)
    w, h = surf.get_size()
    best_warm, best_xy = -1.0, (0, 0)
    bone_peak = 0.0
    for x in range(0, w, 2):
        for yy in range(0, h, 2):
            if a[x, yy] < 40:
                continue
            r, g, b = int(px[x, yy][0]), int(px[x, yy][1]), int(px[x, yy][2])
            # warm-saturation score: red-dominant, low green/blue -> garnet
            warm = r - 0.5 * g - 0.5 * b
            if warm > best_warm:
                best_warm, best_xy = warm, (x, yy)
            # bone: bright near-neutral
            if r > 150 and g > 150 and abs(r - g) < 30:
                bone_peak = max(bone_peak, 0.299 * r + 0.587 * g + 0.114 * b)
    bx, by = best_xy
    r, g, b = int(px[bx, by][0]), int(px[bx, by][1]), int(px[bx, by][2])
    is_garnet = (r > 180 and r > g + 30 and r > b + 20)
    del px, a
    print("self-check: most-saturated WARM pixel @", best_xy, "rgb", (r, g, b),
          "-> garnet-gem?", is_garnet)
    print("self-check: bone face peak value %.0f (night-legible if high)" % bone_peak)
    hairpin_check()


def hairpin_check():
    """Confirm the silhouette is a forward HOOK, not a candle: the topmost solid
    band's horizontal centroid must sit clearly FORWARD (+x) of the bottom band's
    centroid (the cowl overhangs the rear toe-line)."""
    big = pygame.Surface((170 * SS, 200 * SS), pygame.SRCALPHA)
    draw_inquisitor(big, 70 * SS, 92 * SS, 1.20 * SS)
    small = pygame.transform.smoothscale(big, (170, 200))
    mask = pygame.mask.from_surface(small)
    w, h = small.get_size()

    def band_centroid(y0, y1):
        sx, n = 0, 0
        for y in range(y0, y1):
            for x in range(w):
                if mask.get_at((x, y)):
                    sx += x
                    n += 1
        return (sx / n) if n else None, n

    top_cx, top_n = band_centroid(0, h // 4)
    bot_cx, bot_n = band_centroid(3 * h // 4, h)
    forward = (top_cx is not None and bot_cx is not None and top_cx > bot_cx + 6)
    print("self-check hairpin: top-band cx=%.1f (n=%d) | bottom-band cx=%.1f (n=%d) "
          "-> cowl forward of toe? %s"
          % (top_cx or -1, top_n, bot_cx or -1, bot_n, forward))


if __name__ == "__main__":
    main()
