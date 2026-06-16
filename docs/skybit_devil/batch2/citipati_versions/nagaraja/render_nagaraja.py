"""
Round-1 concept renderer for NAGARAJA — the bone-cobra serpent-king
(Batch 2 / Citipati-versions set, concept #1). Headless Pygame; ELEVATED
pipeline (supersample SS=6 → smoothscale) so the coil banding + rib-splines
stay crisp at downscale. Keeps the shipped house grammar: flat saturated
fills, hard 1-2px ink keyline, dark-core → flat-fill → top-left rim-sheen
triad, 1px alpha-grown outline, chibi, scary-CUTE; procedural-only.

WHY this is the anti-Citipati / the brood's ONLY serpentine kind: every other
spin-off (and the source) is a limbed upright skeleton-figure. Nagaraja has NO
arms and NO legs — it is one long bone SPINE reared into an S-coil, crowned by
a hooded cobra-skull. That legless/armless coil is the protected silhouette
tell; nothing else in the roster can be confused for it at 32px.

WHY the hood is RIGID, not bushy: a soft tail-fan would read as the Kitsune
fan or Garuda quills. So the hood is exactly seven STRAIGHT rib-splines — hard
bone struts splayed in a flat shield behind the skull, ink-keyed and slim, with
a brass trim arc tying their tips. Count-able, architectural, unmistakably a
cobra hood and not a brush.

WHY the brow-gem is a single cabochon: a facet-field would shimmer into noise
at 1×. The gem is ONE domed emerald cabochon on the brow — a single focal lit
spot — so the head reads "crowned by a glowing jewel" even at thumbnail.

WHY the vertebra coil IS the pillar: the boss's own stacked spine discs (the
same banded vertebra unit as the body) tile as the repeatable shaft; a single
hooded gap-skull with the rib-splines splayed at the gap is the creature-derived
cap — bottom-rooted, mirrored top↔bottom, never top-heavy.

WHY standalone under docs/: review art never enters the shipped bundle, so this
re-implements the triad/outline helpers rather than importing runtime modules.
"""
import math
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
pygame.init()

# ── PINNED PALETTE (locked brief) ─────────────────────────────────────────────
# Cool-pearl bone is the LIGHTEST of the five spin-offs — emerald is the single
# saturated accent so the figure reads "pearl-and-jade," recognisably cool.
BONE      = (214, 222, 224)   # cool-pearl bone (the dominant fill)
BONE_D    = (162, 174, 182)   # bone dark-core
BONE_DD   = (118, 132, 142)   # deepest bone hollow (sockets, disc foramen)
BONE_SH   = (244, 250, 250)   # bone top-left rim-sheen
SLATE     = (150, 166, 176)   # slate-pearl shade (banding grooves, undersides)
EMERALD   = ( 72, 196, 142)   # emerald serpent-glow — the accent (gem, eyes)
EM_BR     = (146, 236, 196)   # hot emerald inner / cabochon hot-spot
EM_HOT    = (214, 252, 234)   # hottest gem core (lightest, the lit pin)
JADE      = ( 34, 118,  92)   # deep-jade — gem rim, glow underbase, deep grooves
BRASS     = (206, 170,  86)   # brass hood-rib trim (the rib-spline tips/arc)
BRASS_BR  = (236, 208, 132)
BRASS_D   = (158, 126,  56)
INK       = ( 26,  30,  32)   # hard ink keyline
SHEEN     = (244, 250, 250)   # sheen highlight

BG        = ( 94, 100, 104)   # neutral grey review backdrop
PANEL     = ( 72,  78,  84)
DAY_SKY_T = (120, 196, 236)   # day biome sky (top)
DAY_SKY_B = (196, 232, 244)
NIGHT_T   = ( 22,  26,  54)   # night biome sky (top)
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


# ── a single vertebra disc — the repeated coil unit (body + pillar shaft) ─────
def vertebra_disc(surf, cx, cy, rw, rh, s, ang=0.0, lit=False):
    """One stacked bone vertebra: an oval disc with a slate banding groove and a
    dark central foramen. WHY an oval, not a hexagon (anti-Citipati bead): the
    serpent reads as a smooth tubular SPINE of stacked rings, not an architectural
    column — the disc banding is the coil texture. `ang` tilts the disc so the
    coil can bend; `lit` pops the foramen emerald on the body's lit segments."""
    pts = []
    for i in range(14):
        a = (i / 14) * 2 * math.pi
        px = math.cos(a) * rw
        py = math.sin(a) * rh
        # rotate the disc to follow the coil tangent
        rx = px * math.cos(ang) - py * math.sin(ang)
        ry = px * math.sin(ang) + py * math.cos(ang)
        pts.append((cx + rx, cy + ry))
    # top-left sheen wedge of the disc
    sheen = [pts[8], pts[9], pts[10], pts[11],
             (cx + (pts[10][0]-cx)*0.4, cy + (pts[10][1]-cy)*0.4)]
    triad_blob(surf, BONE, pts, sheen_pts=sheen, ow=max(1, int(1.4 * s)))
    # slate banding groove ring just inside the rim (the stacked-disc read)
    gpts = []
    for i in range(14):
        a = (i / 14) * 2 * math.pi
        px = math.cos(a) * rw * 0.66
        py = math.sin(a) * rh * 0.66
        rx = px * math.cos(ang) - py * math.sin(ang)
        ry = px * math.sin(ang) + py * math.cos(ang)
        gpts.append((cx + rx, cy + ry))
    pygame.draw.polygon(surf, SLATE, gpts, max(1, int(1.6 * s)))
    # central foramen hollow — emerald-lit on lit segments
    fr = int(min(rw, rh) * 0.30)
    pygame.draw.circle(surf, BONE_DD, (int(cx), int(cy)), fr)
    if lit:
        pygame.draw.circle(surf, JADE, (int(cx), int(cy)), max(1, int(fr * 0.72)))
        pygame.draw.circle(surf, EMERALD, (int(cx), int(cy)), max(1, int(fr * 0.46)))
    pygame.draw.circle(surf, INK, (int(cx), int(cy)), fr, max(1, int(1 * s)))


# ── the rigid 7-spline cobra HOOD (the hard top tell — NOT a bushy fan) ────────
def cobra_hood(surf, cx, cy, span, height, s):
    """A flat shield of exactly SEVEN straight bone rib-splines splayed behind the
    skull, tied by a brass trim arc at the tips. WHY rigid + count-able: a soft or
    overlapping fan would read as Kitsune's tail-fan or Garuda's quills. Each
    spline is a slim tapered bone strut radiating from a tight neck-base fan to a
    brass-tipped point — hard ink keylines between them so sky/value shows the gaps
    and you can literally count seven. Drawn BEHIND the skull."""
    n = 7
    base_y = cy + int(height * 0.20)          # splines spring from a tight base
    base_spread = span * 0.10                 # narrow root → wide tip = a hood
    # the brass trim arc the spline tips touch (drawn first, behind splines)
    trim_pts = []
    for i in range(n):
        t = i / (n - 1)
        ang = math.radians(-152 + t * 124)    # fan across the upper arc
        tipx = cx + math.cos(ang) * span
        tipy = base_y + math.sin(ang) * height
        trim_pts.append((tipx, tipy))
    # webbing shield BEHIND the splines: a single pale-slate membrane so the hood
    # reads as one solid cobra hood mass, splines ribbing it (kept darker than the
    # bone so the splines pop as lighter struts).
    web = [(cx - base_spread, base_y)] + trim_pts + [(cx + base_spread, base_y)]
    triad_blob(surf, SLATE, web,
               core_pts=[(cx - base_spread*0.5, base_y),
                         trim_pts[1], trim_pts[5],
                         (cx + base_spread*0.5, base_y)],
               ow=max(1, int(1.8 * s)))
    # brass trim arc tying the tips
    pygame.draw.lines(surf, INK, False, trim_pts, max(2, int(3.2 * s)))
    pygame.draw.lines(surf, BRASS, False, trim_pts, max(1, int(2.2 * s)))
    pygame.draw.lines(surf, BRASS_BR, False, trim_pts[:4], max(1, int(1.1 * s)))
    # seven RIGID rib-splines — slim tapered struts, hard ink-keyed, brass caps
    for i in range(n):
        t = i / (n - 1)
        ang = math.radians(-152 + t * 124)
        rootx = cx + (t - 0.5) * 2 * base_spread
        rooty = base_y
        tipx = cx + math.cos(ang) * span
        tipy = base_y + math.sin(ang) * height
        # a slim quad strut (tapered: wider at root, point at tip)
        dx, dy = tipx - rootx, tipy - rooty
        L = max(1.0, math.hypot(dx, dy))
        nx, ny = -dy / L, dx / L
        rw_ = max(2.0, span * 0.030)          # root half-width
        strut = [(rootx + nx*rw_, rooty + ny*rw_),
                 (tipx + nx*rw_*0.30, tipy + ny*rw_*0.30),
                 (tipx - nx*rw_*0.30, tipy - ny*rw_*0.30),
                 (rootx - nx*rw_, rooty - ny*rw_)]
        triad_blob(surf, BONE, strut,
                   sheen_pts=[(rootx + nx*rw_, rooty + ny*rw_),
                              (tipx + nx*rw_*0.30, tipy + ny*rw_*0.30),
                              (tipx, tipy),
                              (rootx + nx*rw_*0.3, rooty + ny*rw_*0.3)],
                   ow=max(1, int(1.2 * s)))
        # brass bead cap at each spline tip (the hood-rib trim)
        triad_circle(surf, BRASS, (int(tipx), int(tipy)), max(2, int(span * 0.040)),
                     ow=max(1, int(1 * s)), core=False)


# ── the cobra SKULL head — chibi, scary-cute, single brow-gem cabochon ────────
def cobra_skull(surf, cx, cy, r, s, lit=True, look=1.0):
    """Hooded serpent skull: a tapered cranium (round dome narrowing to a blunt
    snout), two emerald slit-eyes, a single domed brow-gem cabochon, and two tiny
    down-fangs. `look` skews the snout to face the figure's right (the reared
    hiss). The brow-gem is ONE cabochon focal — not a facet-field."""
    # cranium dome — slightly egg-shaped, snout pulled toward `look` direction
    dome = [(cx - int(r*0.92), cy - int(r*0.10)),
            (cx - int(r*0.70), cy - int(r*0.86)),
            (cx + int(r*0.10), cy - int(r*1.02)),
            (cx + int(r*0.86)*int(look>=0)*0 + int(r*0.84), cy - int(r*0.62)),
            (cx + int(r*1.10), cy + int(r*0.06)),     # blunt snout point (right)
            (cx + int(r*0.74), cy + int(r*0.50)),
            (cx + int(r*0.10), cy + int(r*0.62)),
            (cx - int(r*0.66), cy + int(r*0.42))]
    triad_blob(surf, BONE, dome,
               core_pts=[(cx + int(r*0.10), cy + int(r*0.10)),
                         (cx + int(r*1.06), cy + int(r*0.06)),
                         (cx + int(r*0.70), cy + int(r*0.48)),
                         (cx + int(r*0.10), cy + int(r*0.58))],
               sheen_pts=[(cx - int(r*0.70), cy - int(r*0.80)),
                          (cx + int(r*0.06), cy - int(r*0.96)),
                          (cx - int(r*0.10), cy - int(r*0.40)),
                          (cx - int(r*0.80), cy - int(r*0.06))],
               ow=max(2, int(2 * s)))
    # supraorbital brow ridge (slate groove) over the eyes
    pygame.draw.line(surf, SLATE,
                     (cx - int(r*0.58), cy - int(r*0.18)),
                     (cx + int(r*0.74), cy - int(r*0.30)), max(2, int(2.4 * s)))
    # two emerald slit-eyes — scary-cute reptilian slits, lit pins inside
    for sgn, off in ((-1, 0.34), (1, 0.34)):
        ex = cx + int(r * (0.10 + sgn * 0.40))
        ey = cy - int(r * 0.02)
        # ink almond socket
        sock = [(ex - int(r*0.26), ey), (ex, ey - int(r*0.20)),
                (ex + int(r*0.26), ey), (ex, ey + int(r*0.18))]
        pygame.draw.polygon(surf, INK, sock)
        pygame.draw.polygon(surf, JADE, sock)
        # vertical emerald slit pupil
        pygame.draw.line(surf, EMERALD, (ex, ey - int(r*0.15)), (ex, ey + int(r*0.13)),
                         max(1, int(1.8 * s)))
        pygame.draw.circle(surf, EM_HOT, (ex, ey - int(r*0.02)), max(1, int(r * 0.07)))
    # nostril ticks on the snout
    for sgn in (-1, 1):
        pygame.draw.circle(surf, BONE_DD,
                           (cx + int(r*0.86), cy + int(r*(0.06 + sgn*0.12))),
                           max(1, int(r * 0.06)))
    # tiny down-fangs at the snout underside (the hiss tell, scary-CUTE small)
    fx = cx + int(r * 0.62)
    fy = cy + int(r * 0.54)
    for sgn in (-1, 1):
        fang = [(fx + sgn*int(r*0.16) - int(r*0.05), fy),
                (fx + sgn*int(r*0.16) + int(r*0.05), fy),
                (fx + sgn*int(r*0.16), fy + int(r*0.34))]
        pygame.draw.polygon(surf, INK, fang)
        pygame.draw.polygon(surf, SHEEN, [(fang[0][0]+1, fang[0][1]),
                                          (fang[1][0]-1, fang[1][1]),
                                          (fang[2][0], fang[2][1]-int(r*0.06))])
    # === the single BROW-GEM CABOCHON (the crown-jewel focal) ================
    # WHY one domed cabochon: a facet-field shimmers into noise at 1×. This is a
    # single emerald dome with a jade rim, a hot inner ring and one bright sheen
    # pip — the lit jewel that crowns the head and survives the 32px downscale.
    gx, gy = cx + int(r * 0.04), cy - int(r * 0.56)
    gr = int(r * 0.36)
    if lit:
        # soft jade halo so the gem glows on both biomes
        halo = pygame.Surface((gr*6, gr*6), pygame.SRCALPHA)
        pygame.draw.circle(halo, JADE + (90,), (gr*3, gr*3), int(gr*2.0))
        pygame.draw.circle(halo, EMERALD + (70,), (gr*3, gr*3), int(gr*1.3))
        surf.blit(halo, (gx - gr*3, gy - gr*3), special_flags=pygame.BLEND_RGBA_ADD)
    pygame.draw.circle(surf, INK, (gx, gy), gr + max(1, int(1 * s)))
    pygame.draw.circle(surf, JADE, (gx, gy), gr)
    pygame.draw.circle(surf, EMERALD, (gx, gy), int(gr * 0.78))
    pygame.draw.circle(surf, EM_BR, (gx, gy), int(gr * 0.46))
    pygame.draw.circle(surf, EM_HOT, (gx - int(gr*0.26), gy - int(gr*0.30)),
                       max(1, int(gr * 0.24)))


# ── the reared bone-cobra (hero) ──────────────────────────────────────────────
def draw_nagaraja(surf, cx, cy, s):
    """A reared cobra of ONE long bone spine, S-coiled, hood splayed, head hissing
    at the top. No arms, no legs — the only serpentine silhouette. `s` = unit
    scale around a ~130-unit-tall figure."""

    # === the coiled SPINE path — bottom-rooted base loop rising to a reared neck =
    # WHY a base coil + an S-neck: the bottom loop roots the mass low (anti
    # top-heavy) and gives the unmistakable serpent-coil read; the neck rears up
    # and curves so the head faces the figure's right in a hiss.
    head_y = cy - int(54 * s)
    head_x = cx + int(10 * s)
    hr = int(20 * s)

    # control path from the grounded coil tip up to the neck base under the skull.
    # sampled as a smooth chain; each sample drops a vertebra disc.
    base_cx = cx - int(2 * s)
    base_cy = cy + int(46 * s)
    coil_r = int(30 * s)

    # build an ordered list of (x, y) spine samples from tail-tip → neck-base
    spine = []
    # 1) the grounded base coil — almost a full loop, bottom-rooted
    for i in range(22):
        t = i / 21.0
        a = math.radians(40 + t * 300)        # sweep most of a circle
        rr = coil_r * (0.55 + 0.45 * t)        # spiral opening outward
        sx = base_cx + math.cos(a) * rr
        sy = base_cy + math.sin(a) * rr * 0.78  # squash so it sits as a coil
        spine.append((sx, sy))
    # 2) the reared NECK — an S rising from the coil top to under the skull
    neck0 = spine[-1]
    neck_pts = [neck0,
                (cx - int(14 * s), cy + int(8 * s)),
                (cx + int(18 * s), cy - int(18 * s)),
                (head_x - int(2 * s), head_y + int(26 * s))]
    for i in range(1, 16):
        t = i / 15.0
        # quadratic-ish blend through the neck control points (Catmull-rough)
        x = ((1-t)**3*neck_pts[0][0] + 3*(1-t)**2*t*neck_pts[1][0]
             + 3*(1-t)*t**2*neck_pts[2][0] + t**3*neck_pts[3][0])
        y = ((1-t)**3*neck_pts[0][1] + 3*(1-t)**2*t*neck_pts[1][1]
             + 3*(1-t)*t**2*neck_pts[2][1] + t**3*neck_pts[3][1])
        spine.append((x, y))

    # draw discs along the spine — taper from fat coil → slim neck. The discs are
    # stacked so close they read as one tubular banded serpent body.
    nseg = len(spine)
    for i, (sx, sy) in enumerate(spine):
        t = i / (nseg - 1)
        # tangent angle for disc orientation
        j = min(i + 1, nseg - 1)
        k = max(i - 1, 0)
        ang = math.atan2(spine[j][1] - spine[k][1], spine[j][0] - spine[k][0])
        # body radius tapers tail→neck; widest in the lower coil
        body = (14.0 - 7.0 * t) * s
        rw = body * 0.66
        rh = body
        lit = (i % 3 == 0) and t > 0.25      # periodic emerald foramen up the body
        vertebra_disc(surf, sx, sy, rw, rh, s, ang=ang + math.pi/2, lit=lit)

    # === HOOD (behind skull) then SKULL on top ================================
    cobra_hood(surf, head_x, head_y, span=int(40 * s), height=int(34 * s), s=s)
    cobra_skull(surf, head_x, head_y, hr, s, lit=True, look=1.0)


# ── the vertebra-coil column → pillar mirror ──────────────────────────────────
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """The vertebral coil IS the pillar: a stacked column of vertebra discs (the
    same body unit) = the tileable shaft; a single hooded cobra-skull with the
    7-spline hood splayed at the gap = the creature-derived cap. Bottom-rooted,
    on-axis, mirrored top↔bottom, never top-heavy. `cap` names the gap-facing end."""
    # the shaft: a tight stack of vertebra discs reading as a banded bone spine.
    disc_pitch = int(15 * s)
    cap_room = int(46 * s)
    if cap == "bottom":
        d0, d1 = top + int(8 * s), bot - cap_room
    else:
        d0, d1 = top + cap_room, bot - int(8 * s)
    y = d0
    idx = 0
    while y <= d1:
        rw = int(15 * s)
        rh = int(10 * s)
        lit = (idx % 3 == 1)
        vertebra_disc(surf, cx, y, rw, rh, s, ang=0.0, lit=lit)
        y += disc_pitch
        idx += 1

    # === gap-edge cap: hooded skull + splayed 7-spline hood ===================
    cap_y = (bot - int(26 * s)) if cap == "bottom" else (top + int(26 * s))
    cap_hr = int(13 * s)
    # mirror the whole cap vertically when it faces UP (cap == "top")
    flip = (cap == "top")
    if flip:
        sub = pygame.Surface((int(120 * s), int(90 * s)), pygame.SRCALPHA)
        scx, scy = int(60 * s), int(62 * s)
        cobra_hood(sub, scx, scy, span=int(34 * s), height=int(28 * s), s=s)
        cobra_skull(sub, scx, scy, cap_hr, s, lit=True, look=1.0)
        sub = pygame.transform.flip(sub, False, True)
        surf.blit(sub, (cx - scx, cap_y - (int(90 * s) - scy)))
    else:
        cobra_hood(surf, cx, cap_y, span=int(34 * s), height=int(28 * s), s=s)
        cobra_skull(surf, cx, cap_y, cap_hr, s, lit=True, look=1.0)


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
    sheet.blit(font_big.render("NAGARAJA", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "bone-cobra serpent-king  ·  KIND: serpent-coil  ·  the ONLY legless/armless coil  ·  round 1",
        True, LABEL_DIM), (240, 26))

    # === (a) BIG HERO =========================================================
    def hero_chip(boxw, boxh, dcx, dcy, scale):
        big = pygame.Surface((boxw * SS, boxh * SS), pygame.SRCALPHA)
        draw_nagaraja(big, dcx * SS, dcy * SS, scale * SS)
        small = pygame.transform.smoothscale(big, (boxw, boxh))
        return grow_outline(small, INK + (255,), 1)

    hero = hero_chip(360, 470, 178, 232, 1.85)
    sheet.blit(hero, (14, 92))
    sheet.blit(font.render("Creature — hero", True, LABEL), (110, 566))
    sheet.blit(font_sm.render("ONE long bone SPINE reared into an S-coil — no arms, no legs (the only", True, LABEL_DIM), (14, 590))
    sheet.blit(font_sm.render("serpentine silhouette). Bottom-rooted base loop; reared hissing neck.", True, LABEL_DIM), (14, 606))
    sheet.blit(font_sm.render("7 RIGID rib-splines = cobra hood; single emerald brow-gem cabochon; tiny fangs.", True, LABEL_DIM), (14, 622))

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
    pygame.draw.rect(sheet, (60, 64, 72), (pcx + 8, 86 + 250, 134, 96))
    sheet.blit(font_sm.render("GAP", True, LABEL_DIM), (pcx + 56, 86 + 250 + 40))
    sheet.blit(font.render("Pillar — vertebral coil", True, LABEL), (pcx - 4, 690))
    sheet.blit(font_sm.render("stacked vertebra discs = tileable shaft;", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("hooded skull + 7-spline hood caps each gap edge", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("(mirrored top↔bottom, on-axis, bottom-rooted)", True, LABEL_DIM), (pcx - 4, 746))

    # === (c) TRUE 32px gameplay chips on day + night sky ======================
    panel_x = 660
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 560))
    sheet.blit(font.render("True 32px gameplay-scale chip", True, LABEL), (panel_x + 16, 96))

    # render the hero at a genuine 32px-tall figure
    def chip32():
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_nagaraja(big, 46 * SS, 48 * SS, (32 / 130.0) * SS)
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

    # a 32px pillar gap-cap chip beside, on both skies
    def pillar_chip32():
        big = pygame.Surface((40 * SS, 130 * SS), pygame.SRCALPHA)
        draw_pillar(big, 20 * SS, 2 * SS, 128 * SS, 0.30 * SS, cap="bottom")
        small = pygame.transform.smoothscale(big, (40, 130))
        return grow_outline(small, INK + (255,), 1)

    pc = pillar_chip32()
    px2 = panel_x + 192
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
        (BONE, "cool-pearl bone"), (SLATE, "slate-pearl sh"),
        (EMERALD, "emerald glow"), (JADE, "deep-jade"),
        (BRASS, "brass hood-trim"), (BONE_DD, "bone hollow"),
        (SHEEN, "sheen"), (INK, "ink keyline"),
    ]
    sxp, syp = panel_x + 16, 538
    for i, (c, name) in enumerate(swatches):
        col, row = i % 2, i // 2
        rx = sxp + col * 158
        ry = syp + row * 26
        pygame.draw.rect(sheet, INK, (rx - 1, ry - 1, 20, 20))
        pygame.draw.rect(sheet, c, (rx, ry, 18, 18))
        sheet.blit(font_sm.render(name, True, LABEL), (rx + 26, ry + 3))

    # bottom note strip
    pygame.draw.rect(sheet, PANEL, (14, 770, W - 28, 40))
    sheet.blit(font_sm.render(
        "ELEVATED pipeline: SS=6 supersample → smoothscale.  STAY: flat triad fills · hard ink keyline (26,30,32) · "
        "dark-core→fill→top-left sheen · 1px grown outline · chibi · scary-cute · pearl-and-jade · procedural-only.",
        True, LABEL_DIM), (26, 783))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
