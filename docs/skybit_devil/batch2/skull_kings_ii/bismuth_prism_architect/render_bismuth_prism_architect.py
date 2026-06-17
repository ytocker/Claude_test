"""
Round-1 concept renderer for the BISMUTH PRISM ARCHITECT — a royal skull-KING
of the Skull-Kings-II brood, rendered as a STEPPED CRYSTAL ZIGGURAT rather than
a figure. Headless Pygame; ELEVATED pipeline (SS=6 supersample -> smoothscale)
so the thin rainbow facet-edges survive the downscale. Keeps the shipped house
grammar: flat saturated triad fills, a hard 1-2px ink keyline (28,22,30),
dark-core -> flat-fill -> top-left sheen, 1px alpha-grown outline, chibi
scary-CUTE proportions; procedural-only (no gradients/PNGs).

WHY this king is LIMBLESS architecture, not a body: the brood's de-collision
rule is that the sibling Oxblood Automaton already owns the humanoid-machine
read. The Architect must NOT resolve into arms/legs/torso, so it has NO cradle
and NO limbs — it is a right-angle terraced mass (a Mesoamerican-pyramid-of-
crystal) that steps OUT toward the base. The kingship is carried entirely by a
FACETED BISMUTH SKULL CAPSTONE sitting as the topmost step, plus the rainbow
edges. Read order: pyramid mass first, skull-crown capstone second.

WHY the rainbow lives in the EDGES, not a glow-core: bismuth's identity is its
iridescent oxide step-edges. The dominant MASS is a single cool steel-grey
crystal; the rainbow is a set of DISCRETE per-edge colored line STROKES walked
along each facet boundary (magenta/teal/gold cycling), never a gradient fill.
The focal = the single brightest facet-edge pip, not a warm interior. This keeps
one dominant mass + thin accents and dodges the "glowing gem" cliche.

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

# -- PINNED PALETTE ------------------------------------------------------------
# Steel-grey bismuth crystal is the dominant MASS; rainbow lives only in edges.
CRY       = (132, 138, 150)   # steel-grey crystal body (dominant fill)
CRY_D     = ( 88,  94, 108)   # crystal dark-core / recessed terrace face
CRY_DD    = ( 58,  62,  76)   # deepest crystal hollow (under-step shadow)
CRY_SH    = (196, 202, 214)   # crystal top-left rim-sheen (lit terrace top)
CRY_LIT   = (170, 176, 188)   # mid-lit facet face
# rainbow FACET-EDGE accents — drawn as discrete per-edge colored line strokes,
# cycling around the spectrum so adjacent edges never repeat a hue.
EDGE_MAG  = (206,  96, 168)   # iridescent magenta oxide edge
EDGE_TEA  = ( 96, 196, 196)   # iridescent teal oxide edge
EDGE_GLD  = (214, 184,  96)   # iridescent gold oxide edge
EDGE_MAG_H = (244, 168, 222)  # magenta edge highlight pip
EDGE_TEA_H = (176, 244, 244)  # teal edge highlight pip
EDGE_GLD_H = (250, 232, 168)  # gold edge highlight pip (brightest -> the focal)
INK       = ( 28,  22,  30)   # hard ink keyline

BG        = ( 96, 100, 108)
PANEL     = ( 74,  78,  88)
DAY_SKY_T = (120, 196, 236)
DAY_SKY_B = (196, 232, 244)
NIGHT_T   = ( 22,  26,  54)
NIGHT_B   = ( 48,  44,  82)
LABEL     = (238, 240, 244)
LABEL_DIM = (188, 196, 208)

EDGE_CYCLE   = (EDGE_MAG, EDGE_TEA, EDGE_GLD)
EDGE_CYCLE_H = (EDGE_MAG_H, EDGE_TEA_H, EDGE_GLD_H)


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


# -- the rainbow facet-edge stroke (the king's identity + focal) ---------------
def facet_edge(surf, p0, p1, hue_i, s, hot=False):
    """Walk ONE facet boundary as a discrete colored line stroke. WHY a stroke,
    not a gradient fill: bismuth's iridescence is literally the oxide film at the
    terrace EDGES; coloring the boundaries (and leaving the faces flat grey)
    reads unmistakably as bismuth while keeping the rainbow a thin accent that
    can't swell into a second warm mass. hue_i cycles magenta/teal/gold so no two
    touching edges share a hue. `hot` lays the bright highlight pip — used only
    on the capstone so the single brightest pixel lives in the skull-crown."""
    col = EDGE_CYCLE[hue_i % 3]
    pygame.draw.line(surf, INK, p0, p1, max(2, int(2.4 * s)))
    pygame.draw.line(surf, col, p0, p1, max(1, int(1.6 * s)))
    if hot:
        hc = EDGE_CYCLE_H[hue_i % 3]
        # a short bright pip on the lit (upper) third of the edge
        mx = (p0[0] + p1[0]) / 2
        my = (p0[1] + p1[1]) / 2
        pygame.draw.line(surf, hc, p0, (mx, my), max(1, int(1.1 * s)))


def crystal_block(surf, cx, top_y, half_w, h, s, hue_base, sheen=True):
    """One right-angle terrace block: a flat grey rectangular crystal face with
    a thin top-cap (the lit step surface) and rainbow strokes walked along its
    visible edges. Returns the block's top-left/right corners so the caller can
    chain the rainbow continuously up the ziggurat. WHY rectangular + right-angle:
    the silhouette must read as STEPPED ARCHITECTURE (a built pyramid), never an
    organic crystal cluster or a figure."""
    x0, x1 = cx - half_w, cx + half_w
    y0, y1 = top_y, top_y + h
    # cap thickness gives each step a lit top surface (the terrace tread)
    cap_h = max(2, int(h * 0.26))

    # front face (flat grey mass, dark-core lower-right for volume)
    face = [(x0, y0 + cap_h), (x1, y0 + cap_h), (x1, y1), (x0, y1)]
    triad_blob(surf, CRY, face,
               core_pts=[(cx, y0 + cap_h), (x1, y0 + cap_h), (x1, y1), (cx, y1)],
               sheen_pts=([(x0, y0 + cap_h), (x0 + half_w * 0.5, y0 + cap_h),
                           (x0 + half_w * 0.5, y1), (x0, y1)] if sheen else None),
               ow=max(1, int(1.4 * s)))
    # lit top tread (a brighter slab) — sells the right-angle step
    tread = [(x0, y0), (x1, y0), (x1 - max(2, int(3 * s)), y0 + cap_h),
             (x0 + max(2, int(3 * s)), y0 + cap_h)]
    triad_blob(surf, CRY_SH, tread, ow=max(1, int(1.2 * s)))
    # internal facet split — a single diagonal crease so the face reads faceted
    crease0 = (x0 + half_w * 0.62, y0 + cap_h)
    crease1 = (x0 + half_w * 0.30, y1)
    pygame.draw.line(surf, CRY_DD, crease0, crease1, max(1, int(1.2 * s)))

    # RAINBOW FACET EDGES: tread perimeter + the vertical corners + the crease.
    facet_edge(surf, (x0, y0), (x1, y0), hue_base, s)               # tread back
    facet_edge(surf, (x0, y0), (x0 + max(2, int(3 * s)), y0 + cap_h),
               hue_base + 1, s)                                     # tread left bevel
    facet_edge(surf, (x1, y0), (x1 - max(2, int(3 * s)), y0 + cap_h),
               hue_base + 2, s)                                     # tread right bevel
    facet_edge(surf, (x0, y0 + cap_h), (x0, y1), hue_base + 2, s)   # left corner
    facet_edge(surf, (x1, y0 + cap_h), (x1, y1), hue_base, s)       # right corner
    facet_edge(surf, crease0, crease1, hue_base + 1, s)            # inner crease
    return (x0, y0), (x1, y0)


# -- the FACETED BISMUTH SKULL CAPSTONE (the above-head crown) -----------------
def skull_capstone(surf, cx, base_y, w, s):
    """A faceted bismuth SKULL sitting as the topmost step of the ziggurat — the
    royal crown tell. WHY a blocky angular skull, not a rounded one: it must read
    as cut crystal continuous with the terraces below, and at 32px collapse to a
    pale faceted nub atop the grey pyramid. The brightest facet-edge pip lives
    here so the named focal is in the crown."""
    half = w * 0.5
    top_y = base_y - int(w * 0.92)
    # cranium — a faceted hexagonal dome (angular, crystal, not a smooth ball)
    cran = [(cx - half, base_y - int(w * 0.30)),
            (cx - half * 0.78, top_y + int(w * 0.10)),
            (cx - half * 0.30, top_y),
            (cx + half * 0.30, top_y),
            (cx + half * 0.78, top_y + int(w * 0.10)),
            (cx + half, base_y - int(w * 0.30)),
            (cx + half * 0.72, base_y),
            (cx - half * 0.72, base_y)]
    triad_blob(surf, CRY_LIT, cran,
               core_pts=[(cx, top_y + int(w * 0.10)),
                         (cx + half * 0.78, top_y + int(w * 0.10)),
                         (cx + half, base_y - int(w * 0.30)),
                         (cx + half * 0.72, base_y), (cx, base_y)],
               sheen_pts=[(cx - half * 0.30, top_y), (cx, top_y),
                          (cx - half * 0.20, top_y + int(w * 0.34)),
                          (cx - half * 0.62, top_y + int(w * 0.30))],
               ow=max(1, int(1.6 * s)))
    # eye sockets — deep ink hexafacets (the scary-cute read)
    for sgn in (-1, 1):
        ex = cx + sgn * int(half * 0.44)
        ey = base_y - int(w * 0.40)
        er = int(half * 0.30)
        socket = [(ex - er, ey), (ex - er * 0.4, ey - er * 0.9),
                  (ex + er * 0.6, ey - er * 0.7), (ex + er, ey + er * 0.2),
                  (ex + er * 0.3, ey + er)]
        pygame.draw.polygon(surf, CRY_DD, socket)
        pygame.draw.polygon(surf, INK, [(p[0], p[1]) for p in socket])
        # a tiny iridescent pin deep in the socket (cool spark, not a warm core)
        pygame.draw.circle(surf, EDGE_TEA, (ex, ey), max(1, int(er * 0.30)))
        pygame.draw.circle(surf, EDGE_TEA_H, (ex - 1, ey - 1), max(1, int(er * 0.16)))
    # nasal — a small down-pointing ink triangle
    pygame.draw.polygon(surf, INK,
                        [(cx - int(half * 0.12), base_y - int(w * 0.30)),
                         (cx + int(half * 0.12), base_y - int(w * 0.30)),
                         (cx, base_y - int(w * 0.16))])
    # faceted teeth band — short ink slots
    ty = base_y - int(w * 0.06)
    for k in range(-2, 3):
        tx = cx + int(k * half * 0.26)
        pygame.draw.line(surf, INK, (tx, ty - int(w * 0.06)), (tx, ty),
                         max(1, int(1.2 * s)))
    pygame.draw.line(surf, INK, (cx - int(half * 0.6), ty - int(w * 0.06)),
                     (cx + int(half * 0.6), ty - int(w * 0.06)), max(1, int(1.4 * s)))

    # RAINBOW EDGES on the cranium silhouette — the crown's identity. The TOP
    # ridge carries the single HOT pip so the brightest pixel sits in the crown.
    ring = cran + [cran[0]]
    for i in range(len(cran)):
        p0, p1 = ring[i], ring[i + 1]
        hot = (i == 2)  # the top-left ridge -> brightest gold-edge pip = focal
        facet_edge(surf, p0, p1, i, s, hot=False)
    # the explicit focal: a hot gold pip on the crown's top ridge
    rp0, rp1 = cran[2], cran[3]
    facet_edge(surf, rp0, rp1, 2, s, hot=True)
    px = int((rp0[0] + rp1[0]) / 2)
    py = int((rp0[1] + rp1[1]) / 2)
    pygame.draw.circle(surf, EDGE_GLD_H, (px, py), max(1, int(1.4 * s)))


# -- the limbless stepped-crystal ziggurat KING --------------------------------
def draw_king(surf, cx, cy, s):
    """Compose the ziggurat from wide base step up to the narrow capstone step,
    then crown it with the bismuth skull. WHY drawn bottom-up: each higher step
    must overlap the one below at its back edge so the terraces read as receding
    treads (a built pyramid), and the rainbow edges chain continuously upward."""
    n_steps = 4
    base_half = int(48 * s)
    step_h = int(20 * s)
    base_bottom = cy + int(44 * s)
    inset = int(10 * s)   # each step pulls IN by this much (steps OUT to base)

    # the steps, widest (bottom) -> narrowest (top)
    for k in range(n_steps):
        half_w = base_half - k * inset
        # higher steps sit further back/up; bottom of this step = top of prev
        block_bottom = base_bottom - k * step_h
        top_y = block_bottom - step_h - (0 if k == 0 else int(2 * s))
        crystal_block(surf, cx, top_y, half_w, step_h + int(4 * s), s,
                      hue_base=k, sheen=True)

    # the capstone step (a small grey block) the skull sits on
    cap_step_half = int(16 * s)
    cap_step_top = base_bottom - n_steps * step_h - step_h
    crystal_block(surf, cx, cap_step_top, cap_step_half, int(12 * s), s,
                  hue_base=n_steps, sheen=True)

    # the FACETED BISMUTH SKULL CAPSTONE — the above-head crown tell
    skull_capstone(surf, cx, cap_step_top, int(30 * s), s)


# -- the pillar: a single mirrored ziggurat-terrace tower ----------------------
def pillar_step(surf, cx, top_y, half_w, h, s, hue_base, flip=False):
    """One terrace block for the pillar, drawn so it can mirror top<->bottom.
    `flip` inverts the lit tread to the underside for the ceiling-rooted half."""
    x0, x1 = cx - half_w, cx + half_w
    cap_h = max(2, int(h * 0.30))
    if not flip:
        y0, y1 = top_y, top_y + h
        face = [(x0, y0 + cap_h), (x1, y0 + cap_h), (x1, y1), (x0, y1)]
        tread = [(x0, y0), (x1, y0), (x1 - max(2, int(3 * s)), y0 + cap_h),
                 (x0 + max(2, int(3 * s)), y0 + cap_h)]
        e_a, e_b = (x0, y0), (x1, y0)
        lcorner = ((x0, y0 + cap_h), (x0, y1))
        rcorner = ((x1, y0 + cap_h), (x1, y1))
    else:
        y0, y1 = top_y, top_y + h
        face = [(x0, y0), (x1, y0), (x1, y1 - cap_h), (x0, y1 - cap_h)]
        tread = [(x0 + max(2, int(3 * s)), y1 - cap_h),
                 (x1 - max(2, int(3 * s)), y1 - cap_h), (x1, y1), (x0, y1)]
        e_a, e_b = (x0, y1), (x1, y1)
        lcorner = ((x0, y0), (x0, y1 - cap_h))
        rcorner = ((x1, y0), (x1, y1 - cap_h))
    triad_blob(surf, CRY, face,
               core_pts=[(cx, face[0][1]), (x1, face[1][1]),
                         (x1, face[2][1]), (cx, face[3][1])],
               sheen_pts=[(x0, face[0][1]), (x0 + half_w * 0.5, face[0][1]),
                          (x0 + half_w * 0.5, face[3][1]), (x0, face[3][1])],
               ow=max(1, int(1.4 * s)))
    triad_blob(surf, CRY_SH, tread, ow=max(1, int(1.2 * s)))
    facet_edge(surf, e_a, e_b, hue_base, s)
    facet_edge(surf, lcorner[0], lcorner[1], hue_base + 2, s)
    facet_edge(surf, rcorner[0], rcorner[1], hue_base, s)


def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """A vertical bismuth-terrace tower: a stack of stepped crystal blocks that
    flare OUT toward the gap-edge cap (the creature-derived tell), mirrored so
    the top half hangs from the ceiling and the bottom half rises from the floor.
    A small skull capstone marks the gap edge."""
    shaft_w = int(13 * s)
    # central ink shaft for body so the tower never breaks apart at the gap
    pygame.draw.rect(surf, INK, (cx - int(3 * s), top, int(6 * s), bot - top))

    pitch = int(22 * s)
    cap_room = int(46 * s)
    flip = (cap == "top")
    if cap == "bottom":
        b0, b1 = top + int(6 * s), bot - cap_room
        order = range(b0, b1, pitch)
    else:
        b0, b1 = top + cap_room, bot - int(6 * s)
        order = range(b1 - pitch, b0, -pitch)

    hue = 0
    for y in order:
        # plain narrow shaft terraces (kept slim so the cap stays the focal flare)
        pillar_step(surf, cx, y, shaft_w, pitch - int(3 * s), s, hue, flip=flip)
        hue += 1

    # the flared gap-edge cap: 3 widening terraces ending in a skull capstone
    cap_y = (bot - int(40 * s)) if cap == "bottom" else (top + int(40 * s))
    fan_dir = -1 if cap == "bottom" else 1
    for j in range(3):
        half_w = int((11 + j * 6) * s)
        step_h = int(11 * s)
        if fan_dir < 0:
            ty = cap_y + j * step_h
            pillar_step(surf, cx, ty, half_w, step_h + int(3 * s), s, j, flip=False)
        else:
            ty = cap_y - (j + 1) * step_h
            pillar_step(surf, cx, ty, half_w, step_h + int(3 * s), s, j, flip=True)

    # skull capstone marks the gap edge (mirrored to face into the gap)
    if fan_dir < 0:
        sk_base = cap_y + 3 * int(11 * s) + int(2 * s)
        skull_capstone(surf, cx, sk_base, int(22 * s), s)
    else:
        # for the top half, build the skull pointing DOWN via a flipped sub-surf
        sub = pygame.Surface((int(60 * s), int(40 * s)), pygame.SRCALPHA)
        skull_capstone(sub, int(30 * s), int(36 * s), int(22 * s), s)
        sub = pygame.transform.flip(sub, False, True)
        sk_base = cap_y - 3 * int(11 * s) - int(2 * s)
        surf.blit(sub, (cx - int(30 * s), int(sk_base)))


# -- compose the review sheet --------------------------------------------------
SS = 6


def render_creature_chip(boxw, boxh, draw_cx, draw_cy, scale):
    big = pygame.Surface((boxw * SS, boxh * SS), pygame.SRCALPHA)
    draw_king(big, draw_cx * SS, draw_cy * SS, scale * SS)
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
    sheet.blit(font_big.render("BISMUTH PRISM ARCHITECT", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "Skull-Kings-II  ·  LIMBLESS stepped-crystal ziggurat (no figure, no cradle) · faceted bismuth SKULL CAPSTONE crown · "
        "steel-grey mass + DISCRETE rainbow facet-EDGE strokes · round 1",
        True, LABEL_DIM), (440, 26))

    # === (a) BIG HERO =========================================================
    hero = render_creature_chip(360, 470, 178, 224, 1.55)
    sheet.blit(hero, (14, 92))
    sheet.blit(font.render("King — hero", True, LABEL), (120, 566))
    sheet.blit(font_sm.render("LIMBLESS terraced crystal mass that steps OUT to the base; one steel-grey", True, LABEL_DIM), (14, 590))
    sheet.blit(font_sm.render("dominant mass, rainbow lives ONLY in the per-edge magenta/teal/gold strokes;", True, LABEL_DIM), (14, 606))
    sheet.blit(font_sm.render("faceted bismuth SKULL capstone = the crown; brightest gold-edge pip = focal.", True, LABEL_DIM), (14, 622))

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
    sheet.blit(font.render("Pillar — bismuth terrace tower", True, LABEL), (pcx - 4, 690))
    sheet.blit(font_sm.render("stacked stepped-crystal terraces; flared gap-edge cap", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("with skull capstone + rainbow edges", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("(mirrored top<->bottom, on-axis, bottom-rooted)", True, LABEL_DIM), (pcx - 4, 746))

    # === (c) TRUE 32px chips on day + night sky + SILHOUETTE proof =============
    panel_x = 660
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 560))
    sheet.blit(font.render("True 32px gameplay-scale chip", True, LABEL), (panel_x + 16, 96))

    def chip32(night=False):
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_king(big, 48 * SS, 50 * SS, (32 / 116.0) * SS)
        small = pygame.transform.smoothscale(big, (96, 96))
        # WHY a teal rim on the night chip: the cool steel mass dissolves into a
        # dark night sky; a thin iridescent teal halo carries the silhouette
        # while keeping the gold capstone pip the unambiguous brightest point.
        if night:
            base = grow_outline(small, lerp(EDGE_TEA, INK, 0.3) + (255,), 2)
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
    sheet.blit(font_sm.render("32px on night sky (teal rim)", True, LABEL_DIM), (panel_x + 20, night_y + 156))

    # silhouette proof — blacked-out hero so the stepped-ziggurat read is checked
    def silhouette():
        big = pygame.Surface((150 * SS, 200 * SS), pygame.SRCALPHA)
        draw_king(big, 75 * SS, 100 * SS, 1.15 * SS)
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
    sheet.blit(font_sm.render("(stepped pyramid + skull nub)", True, LABEL_DIM), (sil_x, day_y + 220))

    def pillar_chip32():
        big = pygame.Surface((40 * SS, 130 * SS), pygame.SRCALPHA)
        draw_pillar(big, 20 * SS, 2 * SS, 128 * SS, 0.30 * SS, cap="bottom")
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
        (CRY, "steel-grey crystal"), (CRY_D, "crystal dark-core"),
        (CRY_SH, "crystal sheen"), (CRY_DD, "deep hollow"),
        (EDGE_MAG, "edge magenta"), (EDGE_TEA, "edge teal"),
        (EDGE_GLD, "edge gold"), (EDGE_GLD_H, "edge focal pip"),
        (EDGE_TEA_H, "teal highlight"), (INK, "ink keyline"),
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
        "LIMBLESS stepped-crystal ZIGGURAT: a built pyramid of bismuth, NOT a figure (de-collides from the humanoid Oxblood Automaton).  "
        "ONE grey mass + DISCRETE per-edge rainbow STROKES (never a gradient fill); faceted SKULL CAPSTONE = crown; brightest gold-edge pip = focal.  "
        "SS=6 supersample -> smoothscale · procedural-only.",
        True, LABEL_DIM), (26, 783))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(sheet, out)
    print("wrote", out)

    self_check()


def self_check():
    """Render the hero alone and verify (1) the brightest pixel sits inside the
    skull-capstone crown (the focal owns the peak), and (2) the rainbow reads as
    thin edges — strongly-saturated edge pixels stay a small fraction of grey
    crystal mass (one dominant mass + thin accents)."""
    surf = pygame.Surface((400, 520), pygame.SRCALPHA)
    draw_king(surf, 200, 250, 1.7)
    px = pygame.surfarray.pixels3d(surf)
    a = pygame.surfarray.pixels_alpha(surf)
    w, h = surf.get_size()
    best_lum, best_xy = -1, (0, 0)
    edge_n, mass_n = 0, 0
    for x in range(0, w, 2):
        for yy in range(0, h, 2):
            if a[x, yy] < 40:
                continue
            r, g, b = int(px[x, yy][0]), int(px[x, yy][1]), int(px[x, yy][2])
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            if lum > best_lum:
                best_lum, best_xy = lum, (x, yy)
            mx, mn = max(r, g, b), min(r, g, b)
            sat = (mx - mn)
            if sat > 55:        # saturated -> a rainbow edge pixel
                edge_n += 1
            elif mx > 70 and sat <= 40:   # near-neutral grey -> crystal mass
                mass_n += 1
    bx, by = best_xy
    r, g, b = int(px[bx, by][0]), int(px[bx, by][1]), int(px[bx, by][2])
    # crown band: the capstone sits in the upper ~35% of the rendered mass
    in_crown = by < int(h * 0.42)
    del px, a
    print("self-check: brightest pixel @", best_xy, "rgb", (r, g, b),
          "lum %.0f" % best_lum, "-> in crown band?", in_crown)
    print("self-check: edge px ~%d  vs grey-mass px ~%d  -> edge fraction %.2f"
          % (edge_n, mass_n, edge_n / max(1, edge_n + mass_n)))


if __name__ == "__main__":
    main()
