"""
Round-1 concept renderer for REGENT KOSCHEI — the royal EVOLUTION of Koschei
(KING SKULL royal brood, concept #1). Headless Pygame; ELEVATED pipeline (SS=6
-> smoothscale) so the gilt detail survives the downscale. Clones Koschei's
KIND wholesale — seated throne-emperor, two arms cupping the chartreuse SOUL-
EGG, blackened-iron SPIKE crown, indigo socket pins, corpse-tallow grey-green
bone — and gilds it. Procedural-only (no gradients/PNGs).

WHY this is an EVOLUTION, not a redesign: Koschei already reads as the only
enthroned mass off the upright skull-men. The regent KEEPS that whole silhouette
and KIND; royalty enters ONLY as thin gilt — gold ferrule caps on the crown
spikes, a single chartreuse jewel set at the centre spike tip, gilt riveted
cuffs on the iron throne frame + femur pillar, and a tiny GOLD skull-CHAIN along
the throne lip (the lineage tell). The gold is a THIN edge/ferrule/chain accent
only and is intentionally kept DARKER + LESS saturated than the egg so it never
becomes a second warm mass.

WHY the egg still owns the heat: the brief's hard gate is that the chartreuse
soul-egg stays the single brightest + warmest focal. Gold is metallic and dull
(low-key ochre with a thin specular pip), never the searing yellow-green of the
egg core; the body stays cool corpse-tallow so the lap-egg keeps all the warmth.

WHY a standalone script under docs/: review art must never enter the shipped
bundle, so it reuses only colour math + the triad/outline helpers, not runtime
sprite modules.
"""
import math
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
pygame.init()

# -- PINNED PALETTE (locked re-spec brief) -------------------------------------
BONE      = (190, 192, 158)   # corpse-tallow grey-green bone (dominant fill)
BONE_D    = (146, 130,  92)   # olive-bone shade / dark-core
BONE_DD   = (104,  94,  66)   # deepest bone hollow (rib gaps, joint sockets)
BONE_SH   = (238, 232, 206)   # bone top-left rim-sheen
# the SINGLE warm focal — the cupped soul-egg (poison-chartreuse glow).
EGG       = (196, 232,  72)
EGG_BR    = (228, 250, 132)
EGG_HOT   = (248, 255, 206)   # hottest egg core (must stay the brightest pixel)
EGG_D     = (132, 166,  48)
EGG_RIM   = (108, 138,  36)
# blackened-iron crown + throne frame (the dark structural accent)
IRON      = ( 58,  54,  60)
IRON_BR   = ( 96,  92, 100)
IRON_D    = ( 34,  32,  38)
# deep INDIGO socket pin-glow (a second cool pin, NOT cyan)
INDIGO    = (110, 118, 212)
INDIGO_BR = (176, 182, 244)
INDIGO_D  = ( 60,  66, 150)
INK       = ( 26,  26,  24)
# ROYAL GILT — a THIN metallic ochre accent ONLY (ferrule caps / cuffs / chain).
# WHY kept dull + dark, never near EGG brightness: gold must read as worked
# metal at the edges, NOT as a second saturated warm mass; the egg keeps the
# heat. GOLD_HI is a tight specular pip, GOLD_D the recessed metal shadow.
GOLD      = (196, 156,  58)   # struck-gold base (metallic, low-key)
GOLD_HI   = (240, 214, 128)   # thin specular highlight pip (deliberately < egg core)
GOLD_D    = (120,  88,  30)   # gold shadow / recessed metal

BG        = ( 96, 100, 108)
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


# -- ROYAL GILT primitives (thin metal accents) -------------------------------
def gilt_cuff(surf, cx, cy, w, h, s, rivets=2):
    """A thin gilt riveted band wrapping an iron member. WHY a low-key ochre
    band with a single top-left specular line + tiny rivet dots, never a fat
    bar: the regent's royalty must read as worked-metal banding ON the iron,
    not as a second gold mass. The band hugs the member's width so gold stays a
    thin EDGE accent at any scale."""
    band = [(cx - w * 0.5, cy - h * 0.5), (cx + w * 0.5, cy - h * 0.5),
            (cx + w * 0.5, cy + h * 0.5), (cx - w * 0.5, cy + h * 0.5)]
    pygame.draw.polygon(surf, GOLD_D, band)
    inner = [(cx - w * 0.5, cy - h * 0.5), (cx + w * 0.5, cy - h * 0.5),
             (cx + w * 0.5, cy + h * 0.16), (cx - w * 0.5, cy + h * 0.16)]
    pygame.draw.polygon(surf, GOLD, inner)
    pygame.draw.line(surf, GOLD_HI, (cx - w * 0.42, cy - h * 0.30),
                     (cx + w * 0.42, cy - h * 0.30), max(1, int(1.0 * s)))
    pygame.draw.polygon(surf, INK, band, max(1, int(1.0 * s)))
    # tiny rivet studs along the band (the riveted tell)
    for k in range(rivets):
        rx = cx + (k - (rivets - 1) / 2.0) * (w / max(1, rivets))
        pygame.draw.circle(surf, GOLD_HI, (int(rx), int(cy - h * 0.05)),
                           max(1, int(1.4 * s)))
        pygame.draw.circle(surf, GOLD_D, (int(rx), int(cy + h * 0.02)),
                           max(1, int(0.8 * s)))


def gilt_skull_link(surf, cx, cy, r, s):
    """One tiny GOLD skull bead of the throne-lip chain (the lineage tell). WHY
    a bead-sized dome with two ink eye-pits, not a detailed skull: at 32px the
    chain reads as a row of gold dots; up close each dot resolves to a skull —
    the Koschei-lineage signature without becoming a second warm mass."""
    pygame.draw.circle(surf, INK, (cx, cy), r + max(1, int(0.8 * s)))
    pygame.draw.circle(surf, GOLD_D, (cx, cy), r)
    pygame.draw.circle(surf, GOLD, (cx, cy), int(r * 0.82))
    pygame.draw.circle(surf, GOLD_HI, (cx - int(r * 0.3), cy - int(r * 0.34)),
                       max(1, int(r * 0.30)))
    # two ink eye-pits so a bead reads as a skull when zoomed
    for sgn in (-1, 1):
        pygame.draw.circle(surf, INK, (cx + sgn * int(r * 0.34), cy - int(r * 0.06)),
                           max(1, int(r * 0.22)))


def gilt_chain(surf, x0, x1, y, r, s, gap=None):
    """A row of gold skull-links strung along the throne lip."""
    if gap is None:
        gap = int(r * 2.4)
    x = x0
    while x <= x1:
        # tiny linking loop between beads (a thin gold thread)
        pygame.draw.line(surf, GOLD_D, (x, y), (min(x + gap, x1), y),
                         max(1, int(1.0 * s)))
        x += gap
    x = x0
    while x <= x1:
        gilt_skull_link(surf, int(x), int(y), r, s)
        x += gap


def egg_socket(surf, cx, cy, r, s):
    sr = int(r * 1.30)
    socket = []
    for k in range(24):
        a = math.radians(k * 15)
        socket.append((cx + math.cos(a) * sr,
                       cy + math.sin(a) * sr * 1.18))
    pygame.draw.polygon(surf, INK, socket)
    pygame.draw.polygon(surf, IRON_D, [(p[0], p[1]) for p in socket])
    inner = [(cx + math.cos(math.radians(k * 15)) * sr * 0.82,
              cy + math.sin(math.radians(k * 15)) * sr * 0.98)
             for k in range(24)]
    pygame.draw.polygon(surf, INK, inner)


def soul_egg(surf, cx, cy, r, s):
    for (rr, a) in ((r * 1.85, 30), (r * 1.45, 54), (r * 1.15, 90)):
        halo = pygame.Surface((int(rr * 2) + 4, int(rr * 2) + 4), pygame.SRCALPHA)
        pygame.draw.circle(halo, EGG_BR + (a,), (int(rr) + 2, int(rr) + 2), int(rr))
        surf.blit(halo, (cx - int(rr) - 2, cy - int(rr) - 2))
    egg_pts = []
    for k in range(28):
        a = math.radians(k * (360 / 28))
        wx = 0.74 if math.sin(a) < 0 else 0.80
        egg_pts.append((cx + math.cos(a) * r * wx,
                        cy + math.sin(a) * r * 1.22))
    pygame.draw.polygon(surf, EGG_RIM, egg_pts)
    inner = [(cx + (p[0] - cx) * 0.86, cy + (p[1] - cy) * 0.88) for p in egg_pts]
    pygame.draw.polygon(surf, EGG, inner)
    pygame.draw.ellipse(surf, EGG_BR,
                        (cx - int(r * 0.52), cy - int(r * 0.62),
                         int(r * 0.84), int(r * 1.02)))
    pygame.draw.circle(surf, EGG_HOT, (cx - int(r * 0.18), cy - int(r * 0.26)),
                       max(1, int(r * 0.30)))
    pygame.draw.line(surf, EGG_D, (cx + int(r * 0.26), cy - int(r * 0.92)),
                     (cx - int(r * 0.08), cy + int(r * 1.04)), max(1, int(1.4 * s)))


# -- the blackened-iron tomb-crown of thin bent SPIKES, now GILT-CAPPED --------
def iron_crown(surf, cx, cy, r, s, n=7):
    """Koschei's tall dark iron spike comb, KEPT as the KIND tell, now royally
    gilt-capped. WHY: each spike tip gets a thin GOLD ferrule cap and the
    tallest centre spike is set with a single chartreuse jewel — the regent's
    crown. The ferrules are tiny diamonds of metal (a cap, not a coat) so the
    crown still reads as blackened iron with gold tips, not a gold crown."""
    base_y = cy
    band = [(cx - int(r * 1.02), base_y - int(2 * s)),
            (cx + int(r * 1.02), base_y - int(2 * s)),
            (cx + int(r * 0.96), base_y + int(5 * s)),
            (cx - int(r * 0.96), base_y + int(5 * s))]
    triad_blob(surf, IRON, band,
               sheen_pts=[(cx - int(r * 1.0), base_y - int(2 * s)),
                          (cx + int(r * 0.2), base_y - int(2 * s)),
                          (cx + int(r * 0.2), base_y + int(1 * s)),
                          (cx - int(r * 1.0), base_y + int(1 * s))],
               ow=max(1, int(1.4 * s)))
    # a thin gilt browband rivet-line along the iron band (the crown's gold rim)
    pygame.draw.line(surf, GOLD, (cx - int(r * 0.92), base_y + int(1 * s)),
                     (cx + int(r * 0.92), base_y + int(1 * s)), max(1, int(1.4 * s)))
    pygame.draw.line(surf, GOLD_HI, (cx - int(r * 0.86), base_y),
                     (cx + int(r * 0.40), base_y), max(1, int(0.9 * s)))
    half = (n - 1) / 2.0
    jitter = (0.0, 0.12, -0.08, 0.0, -0.08, 0.12, 0.0)
    centre_i = n // 2
    for i in range(n):
        f = (i - half) / max(1.0, half)
        bx = cx + f * r * 0.92
        h = r * (1.58 - 0.62 * abs(f) + (jitter[i] if i < len(jitter) else 0))
        lean = f * r * 0.42
        tipx = bx + lean
        tipy = base_y - h
        kinkx = bx + lean * 0.42 + (r * 0.05 if f >= 0 else -r * 0.05)
        kinky = base_y - h * 0.55
        wbot = r * 0.13
        spike = [(bx - wbot, base_y + int(2 * s)),
                 (bx + wbot, base_y + int(2 * s)),
                 (kinkx + wbot * 0.5, kinky),
                 (tipx, tipy),
                 (kinkx - wbot * 0.5, kinky)]
        triad_blob(surf, IRON, spike,
                   core_pts=[(bx, base_y), (bx + wbot, base_y + int(1 * s)),
                             (kinkx + wbot * 0.4, kinky), (tipx, tipy)],
                   sheen_pts=[(bx - wbot, base_y), (bx - wbot * 0.4, base_y),
                              (kinkx - wbot * 0.4, kinky), (tipx, tipy)],
                   ow=max(1, int(1.1 * s)))
        pygame.draw.line(surf, lerp(IRON, INDIGO, 0.5),
                         (bx - wbot * 0.6, base_y),
                         (tipx - wbot * 0.4, tipy + int(1 * s)),
                         max(1, int(1.0 * s)))
        # GOLD ferrule cap on every spike tip — a tiny diamond of metal
        cap_w = max(2, int(r * 0.16))
        cap_h = max(3, int(r * 0.26))
        ferrule = [(tipx, tipy - cap_h),
                   (tipx + cap_w, tipy),
                   (tipx, tipy + cap_h * 0.5),
                   (tipx - cap_w, tipy)]
        pygame.draw.polygon(surf, INK, ferrule)
        pygame.draw.polygon(surf, GOLD_D, ferrule)
        inner = [(tipx, tipy - cap_h * 0.7), (tipx + cap_w * 0.7, tipy),
                 (tipx, tipy + cap_h * 0.3), (tipx - cap_w * 0.7, tipy)]
        pygame.draw.polygon(surf, GOLD, inner)
        pygame.draw.line(surf, GOLD_HI, (tipx - cap_w * 0.4, tipy - cap_h * 0.2),
                         (tipx, tipy - cap_h * 0.5), max(1, int(0.9 * s)))
        # the CENTRE spike carries the single chartreuse crown-jewel at its tip
        if i == centre_i:
            jr = max(2, int(r * 0.20))
            jy = tipy - cap_h - jr
            # tiny gold setting claws cradling the jewel
            pygame.draw.circle(surf, GOLD_D, (int(tipx), int(jy)), jr + max(1, int(1.0 * s)))
            # a faint chartreuse aura so the crown-jewel reads as lit but NEVER
            # outshines the lap-egg (smaller + dimmer halo than the egg's)
            halo = pygame.Surface((jr * 4, jr * 4), pygame.SRCALPHA)
            pygame.draw.circle(halo, EGG_BR + (40,), (jr * 2, jr * 2), int(jr * 1.6))
            surf.blit(halo, (int(tipx) - jr * 2, int(jy) - jr * 2))
            pygame.draw.circle(surf, EGG_RIM, (int(tipx), int(jy)), jr)
            pygame.draw.circle(surf, EGG, (int(tipx), int(jy)), int(jr * 0.78))
            pygame.draw.circle(surf, EGG_BR, (int(tipx) - int(jr * 0.2), int(jy) - int(jr * 0.2)),
                               max(1, int(jr * 0.4)))


def rib_blade(surf, x0, y0, x1, y1, w, s, curve=0.0):
    mx = (x0 + x1) / 2 + curve
    my = (y0 + y1) / 2
    left = [(x0 - w * 0.5, y0), (mx - w * 0.5, my), (x1, y1),
            (mx + w * 0.5, my), (x0 + w * 0.5, y0)]
    triad_blob(surf, BONE, left,
               sheen_pts=[(x0 - w * 0.5, y0), (mx - w * 0.5, my),
                          (mx - w * 0.2, my), (x0 - w * 0.1, y0)],
               ow=max(1, int(1.1 * s)))


# -- the enthroned bone-sorcerer, now ROYAL -----------------------------------
def draw_koschei(surf, cx, cy, s):
    head_c = (cx, cy - int(38 * s))
    hr = int(22 * s)
    seat_y = cy + int(40 * s)
    base_w = int(54 * s)

    # === THRONE BACK + SEAT (behind the king) ================================
    dais = [(cx - base_w, seat_y + int(20 * s)),
            (cx + base_w, seat_y + int(20 * s)),
            (cx + base_w - int(6 * s), seat_y + int(40 * s)),
            (cx - base_w + int(6 * s), seat_y + int(40 * s))]
    triad_blob(surf, IRON, dais,
               core_pts=[(cx - int(4 * s), seat_y + int(22 * s)),
                         (cx + base_w - int(6 * s), seat_y + int(21 * s)),
                         (cx + base_w - int(10 * s), seat_y + int(39 * s)),
                         (cx - int(4 * s), seat_y + int(39 * s))],
               ow=max(1, int(1.6 * s)))
    # gilt riveted cuff along the dais front edge (royal base banding)
    gilt_cuff(surf, cx, seat_y + int(33 * s), base_w * 1.7, int(7 * s), s, rivets=5)

    for sgn in (-1, 1):
        sx0 = cx + sgn * int(30 * s)
        sx1 = cx + sgn * int(36 * s)
        stile = [(sx0 - int(5 * s), seat_y + int(22 * s)),
                 (sx0 + int(5 * s), seat_y + int(22 * s)),
                 (sx1 + int(5 * s), cy - int(24 * s)),
                 (sx1 - int(5 * s), cy - int(24 * s))]
        triad_blob(surf, IRON, stile, ow=max(1, int(1.4 * s)))
        armrest = [(cx + sgn * int(10 * s), seat_y - int(6 * s)),
                   (sx0 + sgn * int(5 * s), seat_y - int(2 * s)),
                   (sx0 + sgn * int(5 * s), seat_y + int(7 * s)),
                   (cx + sgn * int(10 * s), seat_y + int(3 * s))]
        triad_blob(surf, IRON, armrest, ow=max(1, int(1.3 * s)))
        pygame.draw.line(surf, lerp(IRON, INDIGO, 0.45),
                         (sx0 + sgn * int(5 * s), seat_y + int(20 * s)),
                         (sx1 + sgn * int(5 * s), cy - int(23 * s)),
                         max(1, int(1.4 * s)))
        # gilt riveted cuff wrapping each throne stile at mid-height
        cuff_y = cy + int(2 * s)
        gilt_cuff(surf, (sx0 + sx1) // 2, cuff_y, int(13 * s), int(7 * s), s, rivets=2)
        # iron finial knob atop each stile, now with a thin gold collar
        triad_circle(surf, IRON, (sx1, cy - int(26 * s)), int(6 * s),
                     ow=max(1, int(1.2 * s)), core=False)
        pygame.draw.circle(surf, GOLD, (sx1, cy - int(26 * s)), int(6 * s),
                           max(1, int(1.4 * s)))
        pygame.draw.circle(surf, GOLD_HI, (sx1 - int(2 * s), cy - int(28 * s)),
                           max(1, int(1.2 * s)))

    for i in range(-2, 3):
        f = i / 2.0
        bx = cx + f * int(26 * s)
        h = int((54 - 14 * abs(f)) * s)
        rib_blade(surf, bx, seat_y + int(16 * s), bx + f * int(8 * s),
                  seat_y + int(16 * s) - h, int(7 * s), s, curve=f * int(5 * s))

    # === SEATED LEGS =========================================================
    leg_th = int(13 * s)
    for sgn in (-1, 1):
        hip = (cx + sgn * int(12 * s), seat_y + int(4 * s))
        knee = (cx + sgn * int(34 * s), seat_y + int(10 * s))
        foot = (cx + sgn * int(34 * s), seat_y + int(34 * s))
        bone_limb(surf, hip, knee, foot, leg_th, s)
        fb = [(foot[0] - sgn * int(2 * s), foot[1] - int(3 * s)),
              (foot[0] + sgn * int(16 * s), foot[1] - int(1 * s)),
              (foot[0] + sgn * int(15 * s), foot[1] + int(8 * s)),
              (foot[0] - sgn * int(3 * s), foot[1] + int(7 * s))]
        triad_blob(surf, BONE, fb, ow=max(1, int(1.2 * s)))

    # === PELVIS + SPINE + HUNCHED RIBCAGE ====================================
    pelvis = [(cx - int(18 * s), seat_y - int(4 * s)),
              (cx + int(18 * s), seat_y - int(4 * s)),
              (cx + int(14 * s), seat_y + int(10 * s)),
              (cx, seat_y + int(13 * s)),
              (cx - int(14 * s), seat_y + int(10 * s))]
    triad_blob(surf, BONE, pelvis,
               core_pts=[(cx - int(6 * s), seat_y + int(2 * s)),
                         (cx + int(14 * s), seat_y - int(2 * s)),
                         (cx + int(13 * s), seat_y + int(9 * s)),
                         (cx, seat_y + int(12 * s))],
               ow=max(1, int(1.6 * s)))
    pygame.draw.circle(surf, BONE_DD, (cx, seat_y + int(2 * s)), int(4 * s))

    spine = [(cx, seat_y - int(2 * s)),
             (cx - int(4 * s), cy + int(6 * s)),
             (cx - int(2 * s), cy - int(14 * s))]
    pygame.draw.lines(surf, INK, False, spine, int(8 * s))
    pygame.draw.lines(surf, BONE, False, spine, int(5 * s))

    rc_cx, rc_cy = cx - int(2 * s), cy - int(4 * s)
    rc_w, rc_h = int(30 * s), int(36 * s)
    cage = [(rc_cx - rc_w // 2, rc_cy - rc_h // 2 + int(2 * s)),
            (rc_cx + rc_w // 2, rc_cy - rc_h // 2),
            (rc_cx + int(rc_w * 0.42), rc_cy + rc_h // 2),
            (rc_cx - int(rc_w * 0.42), rc_cy + rc_h // 2)]
    triad_blob(surf, BONE, cage,
               core_pts=[(rc_cx + int(2 * s), rc_cy - rc_h // 2 + int(3 * s)),
                         (rc_cx + rc_w // 2, rc_cy - rc_h // 2 + int(2 * s)),
                         (rc_cx + int(rc_w * 0.42), rc_cy + rc_h // 2),
                         (rc_cx + int(2 * s), rc_cy + rc_h // 2)],
               sheen_pts=[(rc_cx - rc_w // 2 + int(2 * s), rc_cy - rc_h // 2 + int(3 * s)),
                          (rc_cx - int(4 * s), rc_cy - rc_h // 2 + int(2 * s)),
                          (rc_cx - int(6 * s), rc_cy + int(6 * s)),
                          (rc_cx - rc_w // 2 + int(2 * s), rc_cy + int(4 * s))],
               ow=max(1, int(1.8 * s)))
    for i in range(4):
        ry = rc_cy - rc_h // 2 + int(8 * s) + i * int(7 * s)
        bw = int(rc_w * (0.44 - i * 0.05))
        pygame.draw.arc(surf, BONE_DD,
                        (rc_cx - bw, ry - int(7 * s), bw * 2, int(15 * s)),
                        math.radians(205), math.radians(335), max(2, int(2.2 * s)))
    pygame.draw.line(surf, BONE_DD, (rc_cx, rc_cy - rc_h // 2 + int(6 * s)),
                     (rc_cx, rc_cy + int(5 * s)), max(1, int(2 * s)))

    # === the GOLD skull-CHAIN draped across the chest/throne lip (lineage tell)
    # WHY a shallow swag under the ribcage, sitting on the lap behind the egg:
    # it is the Koschei-evolution signature and a clearly royal regalia note,
    # but kept tiny + dull so it never competes with the egg.
    chain_y = rc_cy + rc_h // 2 + int(2 * s)
    gilt_chain(surf, cx - int(20 * s), cx + int(20 * s), chain_y,
               max(2, int(2.6 * s)), s)

    # === SOUL-EGG cupped in the lap (drawn AFTER the chain -> the egg owns the
    # foreground + the single brightest focal) ================================
    egg_c = (cx + int(1 * s), cy + int(21 * s))
    egg_r = int(16 * s)
    egg_socket(surf, egg_c[0], egg_c[1], egg_r, s)
    soul_egg(surf, egg_c[0], egg_c[1], egg_r, s)

    # === ARMS — both cradling the egg from below =============================
    arm_th = int(7 * s)
    for sgn in (-1, 1):
        shoulder = (rc_cx + sgn * int(15 * s), rc_cy - rc_h // 2 + int(7 * s))
        elbow = (cx + sgn * int(25 * s), cy + int(8 * s))
        hand = (egg_c[0] + sgn * int(12 * s), egg_c[1] + int(12 * s))
        bone_limb(surf, shoulder, elbow, hand, arm_th, s)
    for sgn in (-1, 1):
        bx = egg_c[0] + sgn * int(13 * s)
        by = egg_c[1] + int(13 * s)
        tip = (egg_c[0] + sgn * int(4 * s), egg_c[1] + int(int(egg_r) * 1.18))
        mid = (egg_c[0] + sgn * int(11 * s), egg_c[1] + int(int(egg_r) * 1.30))
        thumb = [(bx - sgn * int(3 * s), by - int(3 * s)),
                 (bx + sgn * int(4 * s), by - int(1 * s)),
                 (mid[0], mid[1]),
                 (tip[0], tip[1]),
                 (tip[0] - sgn * int(2 * s), tip[1] - int(4 * s))]
        triad_blob(surf, BONE, thumb,
                   sheen_pts=[(bx - sgn * int(3 * s), by - int(3 * s)),
                              (bx + sgn * int(1 * s), by - int(2 * s)),
                              (mid[0] - sgn * int(2 * s), mid[1] - int(1 * s)),
                              (tip[0], tip[1] - int(2 * s))],
                   ow=max(1, int(1.3 * s)))

    # === SKULL HEAD ==========================================================
    triad_circle(surf, BONE, head_c, hr, ow=max(2, int(2 * s)))
    for sgn in (-1, 1):
        pygame.draw.circle(surf, BONE_D,
                           (head_c[0] + sgn * int(hr * 0.66), head_c[1] + int(hr * 0.30)),
                           int(hr * 0.28))
    for sgn in (-1, 1):
        ex = head_c[0] + sgn * int(hr * 0.44)
        ey = head_c[1] + int(hr * 0.06)
        pygame.draw.circle(surf, BONE_DD, (ex, ey), int(hr * 0.36))
        pygame.draw.circle(surf, INK, (ex, ey), int(hr * 0.30))
        pygame.draw.circle(surf, INDIGO_D, (ex, ey), int(hr * 0.22))
        pygame.draw.circle(surf, INDIGO, (ex + sgn * int(1 * s), ey + int(2 * s)),
                           int(hr * 0.15))
        pygame.draw.circle(surf, INDIGO_BR, (ex, ey + int(1 * s)),
                           max(1, int(hr * 0.07)))
    for sgn in (-1, 1):
        brow = [(head_c[0] + sgn * int(hr * 0.74), head_c[1] - int(hr * 0.34)),
                (head_c[0] + sgn * int(hr * 0.10), head_c[1] - int(hr * 0.08)),
                (head_c[0] + sgn * int(hr * 0.12), head_c[1] + int(hr * 0.02)),
                (head_c[0] + sgn * int(hr * 0.78), head_c[1] - int(hr * 0.22))]
        pygame.draw.polygon(surf, lerp(BONE_DD, INDIGO_D, 0.45), brow)
        pygame.draw.aalines(surf, INK, False, brow[:2])
    pygame.draw.polygon(surf, BONE_DD,
                        [(head_c[0] - int(hr * 0.13), head_c[1] + int(hr * 0.32)),
                         (head_c[0] + int(hr * 0.13), head_c[1] + int(hr * 0.32)),
                         (head_c[0], head_c[1] + int(hr * 0.58))])
    my = head_c[1] + int(hr * 0.74)
    pygame.draw.line(surf, INK, (head_c[0] - int(hr * 0.42), my - int(hr * 0.02)),
                     (head_c[0] + int(hr * 0.42), my + int(hr * 0.06)),
                     max(1, int(2 * s)))
    for k in range(-2, 3):
        pygame.draw.line(surf, INK,
                         (head_c[0] + int(k * hr * 0.18), my - int(hr * 0.06)),
                         (head_c[0] + int(k * hr * 0.18), my + int(hr * 0.10)),
                         max(1, int(1 * s)))

    # === TOMB-CROWN of blackened-iron spikes, now GILT-CAPPED + jewelled ======
    iron_crown(surf, head_c[0], head_c[1] - int(hr * 0.86), int(hr * 0.96), s, n=7)


# -- the femur-throne-column -> pillar mirror, now with GILT cuffs ------------
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    shaft_w = int(16 * s)
    pygame.draw.rect(surf, INK, (cx - int(3 * s), top, int(6 * s), bot - top))

    pitch = int(26 * s)
    cap_room = int(40 * s)
    if cap == "bottom":
        b0, b1 = top + int(8 * s), bot - cap_room
    else:
        b0, b1 = top + cap_room, bot - int(8 * s)
    y = b0
    while y <= b1:
        for sgn in (-1, 1):
            fx = cx + sgn * int(7 * s)
            top_y = y - int(8 * s)
            bot_y = y + int(8 * s)
            shaft = [(fx - int(4 * s), top_y), (fx + int(4 * s), top_y),
                     (fx + int(3 * s), y), (fx + int(4 * s), bot_y),
                     (fx - int(4 * s), bot_y), (fx - int(3 * s), y)]
            triad_blob(surf, BONE, shaft,
                       sheen_pts=[(fx - int(4 * s), top_y), (fx - int(1 * s), top_y),
                                  (fx - int(1 * s), bot_y), (fx - int(4 * s), bot_y)],
                       ow=max(1, int(1.2 * s)))
            for ky in (top_y, bot_y):
                triad_circle(surf, BONE, (fx - int(3 * s), ky), int(3 * s),
                             ow=max(1, int(1.0 * s)), core=False)
                triad_circle(surf, BONE, (fx + int(3 * s), ky), int(3 * s),
                             ow=max(1, int(1.0 * s)), core=False)
        # iron lashing band cinching the pair, now a GILT riveted cuff (royal)
        band = [(cx - shaft_w * 0.66, y - int(4 * s)),
                (cx + shaft_w * 0.66, y - int(4 * s)),
                (cx + shaft_w * 0.66, y + int(4 * s)),
                (cx - shaft_w * 0.66, y + int(4 * s))]
        triad_blob(surf, IRON, band,
                   sheen_pts=[(cx - shaft_w * 0.66, y - int(4 * s)),
                              (cx, y - int(4 * s)), (cx, y - int(1 * s)),
                              (cx - shaft_w * 0.66, y - int(1 * s))],
                   ow=max(1, int(1.0 * s)))
        gilt_cuff(surf, cx, y, shaft_w * 1.28, int(6 * s), s, rivets=2)
        y += pitch

    cap_y = (bot - int(26 * s)) if cap == "bottom" else (top + int(26 * s))
    fan_dir = -1 if cap == "bottom" else 1
    lip = [(cx - int(18 * s), cap_y - fan_dir * int(2 * s)),
           (cx + int(18 * s), cap_y - fan_dir * int(2 * s)),
           (cx + int(14 * s), cap_y - fan_dir * int(11 * s)),
           (cx - int(14 * s), cap_y - fan_dir * int(11 * s))]
    triad_blob(surf, IRON, lip, ow=max(1, int(1.2 * s)))
    # gilt skull-chain along the cap lip (the femur-throne lineage tell)
    gilt_chain(surf, cx - int(15 * s), cx + int(15 * s),
               cap_y - fan_dir * int(2 * s), max(2, int(2.2 * s)), s)
    for i in (-2, -1, 1, 2):
        f = i / 2.0
        bx = cx + f * int(18 * s)
        h = int((30 - 8 * abs(f)) * s)
        rib_blade(surf, bx, cap_y - fan_dir * int(8 * s),
                  bx + f * int(6 * s), cap_y - fan_dir * int(8 * s) - fan_dir * h,
                  int(6 * s), s, curve=f * int(4 * s))
    egg_y = cap_y + fan_dir * int(11 * s)
    egg_pr = int(13 * s)
    egg_socket(surf, cx, egg_y, egg_pr, s)
    soul_egg(surf, cx, egg_y, egg_pr, s)


# -- compose the review sheet -------------------------------------------------
SS = 6


def render_creature_chip(boxw, boxh, draw_cx, draw_cy, scale):
    big = pygame.Surface((boxw * SS, boxh * SS), pygame.SRCALPHA)
    draw_koschei(big, draw_cx * SS, draw_cy * SS, scale * SS)
    small = pygame.transform.smoothscale(big, (boxw, boxh))
    return grow_outline(small, INK + (255,), 1)


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


def main():
    W, H = 1180, 820
    font_big, font, font_sm = load_fonts()

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    pygame.draw.rect(sheet, PANEL, (0, 0, W, 56))
    sheet.blit(font_big.render("REGENT KOSCHEI", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "royal EVOLUTION of Koschei  ·  seated throne-emperor · GILT iron-spike crown + chartreuse crown-jewel · "
        "gold skull-chain (lineage) · cupped soul-egg focal · round 1",
        True, LABEL_DIM), (320, 26))

    # === (a) BIG HERO =========================================================
    hero = render_creature_chip(360, 470, 178, 232, 1.80)
    sheet.blit(hero, (14, 92))
    sheet.blit(font.render("Creature — hero", True, LABEL), (110, 566))
    sheet.blit(font_sm.render("KOSCHEI's KIND kept whole: seated throne-emperor, iron-spike crown, indigo", True, LABEL_DIM), (14, 590))
    sheet.blit(font_sm.render("pins, cupped chartreuse soul-egg. ROYAL = thin gilt ONLY: gold ferrule caps", True, LABEL_DIM), (14, 606))
    sheet.blit(font_sm.render("+ chartreuse crown-jewel, gilt riveted cuffs, gold skull-chain (the lineage tell).", True, LABEL_DIM), (14, 622))

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
    sheet.blit(font.render("Pillar — gilt femur-throne", True, LABEL), (pcx - 4, 690))
    sheet.blit(font_sm.render("paired-femur column, lashings now GILT cuffs;", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("rib-spire fan + gold skull-chain + soul-egg cap", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("(mirrored top<->bottom, on-axis, bottom-rooted)", True, LABEL_DIM), (pcx - 4, 746))

    # === (c) TRUE 32px chips on day + night sky + SILHOUETTE proof =============
    panel_x = 660
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 560))
    sheet.blit(font.render("True 32px gameplay-scale chip", True, LABEL), (panel_x + 16, 96))

    def chip32():
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_koschei(big, 48 * SS, 52 * SS, (32 / 132.0) * SS)
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

    # silhouette proof — blacked-out hero so the seated-caged read is checked
    def silhouette():
        big = pygame.Surface((150 * SS, 200 * SS), pygame.SRCALPHA)
        draw_koschei(big, 75 * SS, 96 * SS, 1.30 * SS)
        small = pygame.transform.smoothscale(big, (150, 200))
        mask = pygame.mask.from_surface(small)
        sil = pygame.Surface((150, 200), pygame.SRCALPHA)
        for ox, oy in mask.outline():
            pass
        # fill the mask solid black
        solid = mask.to_surface(setcolor=(18, 18, 20, 255), unsetcolor=(0, 0, 0, 0))
        sil.blit(solid, (0, 0))
        return sil

    sil_x = panel_x + 196
    pygame.draw.rect(sheet, (210, 212, 216), (sil_x, day_y, 150, 200))
    pygame.draw.rect(sheet, INK, (sil_x, day_y, 150, 200), 1)
    sheet.blit(silhouette(), (sil_x, day_y))
    sheet.blit(font_sm.render("silhouette proof", True, LABEL_DIM), (sil_x, day_y + 204))
    sheet.blit(font_sm.render("(low caged seated mass)", True, LABEL_DIM), (sil_x, day_y + 220))

    def pillar_chip32():
        big = pygame.Surface((40 * SS, 130 * SS), pygame.SRCALPHA)
        draw_pillar(big, 20 * SS, 2 * SS, 128 * SS, 0.32 * SS, cap="bottom")
        small = pygame.transform.smoothscale(big, (40, 130))
        return grow_outline(small, INK + (255,), 1)

    pc = pillar_chip32()
    px2 = sil_x + 168
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
        (BONE, "corpse-tallow bone"), (BONE_D, "olive-bone shade"),
        (EGG, "chartreuse soul-egg"), (EGG_HOT, "egg hot core"),
        (IRON, "blackened iron"), (GOLD, "royal gilt"),
        (GOLD_HI, "gilt highlight"), (INDIGO, "indigo socket"),
        (INDIGO_BR, "indigo pin"), (INK, "ink keyline"),
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
        "ROYAL EVOLUTION of Koschei: gild, don't redesign.  GOLD = thin ferrule/cuff/chain accent ONLY (dull metal, never near egg-bright); "
        "chartreuse egg stays the single brightest+warmest focal.  SS=6 supersample -> smoothscale · procedural-only.",
        True, LABEL_DIM), (26, 783))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(sheet, out)
    print("wrote", out)

    # ----- SELF-CHECK: egg must be the single brightest pixel; gold thin -----
    self_check()


def self_check():
    """Render the hero alone and verify (1) the brightest pixel sits inside the
    chartreuse egg (the warm focal owns the peak), and (2) gold reads as a thin
    accent — the count of strongly-gold pixels stays a small fraction of bone."""
    surf = pygame.Surface((400, 520), pygame.SRCALPHA)
    draw_koschei(surf, 200, 260, 2.0)
    px = pygame.surfarray.pixels3d(surf)
    a = pygame.surfarray.pixels_alpha(surf)
    w, h = surf.get_size()
    best_lum, best_xy = -1, (0, 0)
    gold_n, bone_n = 0, 0
    for x in range(0, w, 2):
        for yy in range(0, h, 2):
            if a[x, yy] < 40:
                continue
            r, g, b = int(px[x, yy][0]), int(px[x, yy][1]), int(px[x, yy][2])
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            if lum > best_lum:
                best_lum, best_xy = lum, (x, yy)
            # crude gold detector: warm, mid-bright, low blue, g<r-ish
            if r > 140 and 70 < g < 200 and b < 120 and r >= g and (r - b) > 60:
                gold_n += 1
            # crude bone detector: bright, near-neutral grey-green
            if r > 150 and g > 150 and abs(r - g) < 40 and b > 120:
                bone_n += 1
    bx, by = best_xy
    r, g, b = int(px[bx, by][0]), int(px[bx, by][1]), int(px[bx, by][2])
    # egg-core hue: very bright, green-dominant or near-white-green
    is_egg = (g > 180 and r > 160 and b < 220 and g >= b)
    del px, a
    print("self-check: brightest pixel @", best_xy, "rgb", (r, g, b),
          "lum %.0f" % best_lum, "-> egg-core?", is_egg)
    print("self-check: gold px ~%d  vs bone px ~%d  -> gold fraction %.2f"
          % (gold_n, bone_n, gold_n / max(1, gold_n + bone_n)))


if __name__ == "__main__":
    main()
