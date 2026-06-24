"""Five PAIRED outer-RING concepts where the ring is a CROWN WOVEN FROM TWIGS,
BRANCHES AND LEAVES — a rustic woodland twig crown (NOT an Olympic laurel
head-wreath, NOT a jewelled royal coronet).

Each concept is a MATCHED PAIR sharing ONE twig-crown construction + palette:

  * ``fame_<name>``  — a pristine GILDED twig crown: branches/twigs struck in
    warm gold under the family's one upper-left light, elegant and whole.
  * ``shame_<name>`` — the SAME twig crown DEGRADED so it reads as that crown
    fallen from grace: twigs SNAPPED to bare stubs, the weave coming apart with
    GAPS in the silhouette, leaves browned & shed and tumbling off the lower
    rim. The degradation is to the SILHOUETTE, not just desaturation. NO
    diagonal crack.

The five differ in KIND (per distinct-design-variants):
  1 CORONA  — a radial corona of forked twig POINTS all around (spiky sunburst
              of branches).
  2 CIRCLET — a woven horizontal branch BAND with three TALLER crown PEAKS/spires
              at the top.
  3 THORN   — a thin sinuous THORNY branch ring with paired barbs + sparse leaves.
  4 IVY     — a dense leafy IVY/VINE crown of overlapping rounded leaves.
  5 BIRCH   — slender drooping BIRCH/WILLOW twigs hung with little buds/catkins.

The CENTER emblem is NOT redesigned — every composer stamps the real engraved
glyph through the live ``_stamp_glyph`` (``pillar_100`` in Fame samples, a shame
emblem in Shame samples), so only the twig-crown ring/frame changes.

HARD FIT RULE: rendered at the REAL badge geometry (``_build`` uses R=0.46*size).
Every twig tip and leaf must fit INSIDE the badge square (within ~0.49*size of
center). Because the crown extends OUTWARD past the disc, each composer draws the
medal CORE smaller (CORE≈0.36*R-of-badge worth of radius) so the crown sits
around it INSIDE the badge bounds. The composers receive the BADGE radius ``R``
and derive a smaller ``core`` disc radius internally.

WRITE-ONLY scratch — never bundled. Imports ``game`` read-only.
"""
from __future__ import annotations

import math
import pygame

import game.achievement_icons as ai
from game.draw import lerp_color, blit_glow

_LIGHT = ai._LIGHT  # share the family's one upper-left light source

# The crown reaches OUTWARD to the badge edge, so the struck medal core is drawn
# smaller than the badge radius — the twigs live in the annulus between CORE and
# the badge bound. ~0.62 keeps every tip inside ~0.49*size even for the spiky
# corona; the enamel face stays large enough to host the engraved glyph.
_CORE = 0.62


# ── shared low-level helpers ────────────────────────────────────────────────

def _core_disc(surf, cx, cy, core, rim_hi, rim_mid, rim_lo, spec,
               face_top, face_bot, recess, step_hi, step_lo,
               glyph_key, gly, gly_sh, sheen=None):
    """Draw the struck-metal core (rim band + step + enamel face + engraved
    glyph) at radius ``core`` — the SAME minted disc the live family uses, just
    pulled in so the twig crown can ring it inside the badge bounds."""
    ai._draw_face  # touch so the dependency is obvious to a reader
    _metal_band(surf, cx, cy, core, int(core * 0.74), rim_hi, rim_lo,
                spec=spec, edge=_rim_edge(rim_lo))
    pygame.draw.circle(surf, rim_mid, (cx, cy), core, max(2, core // 24))
    fr = int(core * 0.70)
    ai._draw_step(surf, cx, cy, fr + max(2, core // 16), step_hi, step_lo)
    ai._draw_face(surf, cx, cy, fr, face_top, face_bot, recess)
    gr = int(core * 0.56)
    ai._stamp_glyph(surf, glyph_key, cx, cy, gr, gly, gly_sh, sheen)


def _rim_edge(lo):
    # a slightly darker keyline than the rim's shadow tone
    return tuple(max(0, int(c * 0.55)) for c in lo)


def _metal_band(surf, cx, cy, R, inner, hi, lo, spec=None,
                spec_span=0.55, light=_LIGHT, edge=None):
    """Lit metal rim band from R inward to ``inner`` under the one upper-left
    light — the shared bevel math (lifted from the live family) so the strike
    reads identical; each concept feeds its own gold/pewter palette."""
    for i in range(R, inner, -1):
        t = (R - i) / max(1, R - inner)
        pygame.draw.circle(surf, lerp_color(hi, lo, t * 0.6 + 0.2), (cx, cy), i)
    steps = 56
    band = (R - inner)
    for seg in range(steps):
        a0 = seg / steps * math.tau
        a1 = (seg + 1) / steps * math.tau
        d = (math.cos(a0 - light) + 1) * 0.5
        col = lerp_color(lo, hi, d ** 1.4)
        rect = pygame.Rect(cx - R + band // 3, cy - R + band // 3,
                           (R - band // 3) * 2, (R - band // 3) * 2)
        pygame.draw.arc(surf, col, rect, -a1, -a0, max(2, band - band // 3))
    if spec is not None:
        mid_r = (R + inner) // 2
        hot = pygame.Rect(cx - mid_r, cy - mid_r, mid_r * 2, mid_r * 2)
        pygame.draw.arc(surf, spec, hot, light - spec_span, light + spec_span,
                        max(2, band // 2))
    if edge is not None:
        pygame.draw.circle(surf, edge, (cx, cy), R, max(1, R // 36))


def _dir_shade(a, lo, hi, p=1.25):
    # tone a twig by its angle to the one upper-left light
    d = (math.cos(a - _LIGHT) + 1) * 0.5
    return lerp_color(lo, hi, d ** p)


def _twig(surf, x0, y0, x1, y1, w, col, edge=None):
    """A single tapered twig stroke from base to tip. Drawn as a slim quad so it
    has woody THICKNESS (a stick, not a hairline) tapering to a point at the
    tip; an optional darker ``edge`` underlines the shadow flank."""
    dx, dy = x1 - x0, y1 - y0
    ln = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / ln, dx / ln
    pts = [(x0 + nx * w, y0 + ny * w), (x0 - nx * w, y0 - ny * w),
           (x1, y1)]
    if edge is not None:
        pygame.draw.line(surf, edge, (int(x0), int(y0)), (int(x1), int(y1)),
                         max(2, int(w * 2.2)))
    pygame.draw.polygon(surf, col, [(int(a), int(b)) for a, b in pts])


def _leaf(surf, bx, by, ang, ln, wd, fill, edge):
    """One small almond leaf swept along ``ang`` — a filled lens with a midrib so
    it reads as foliage tucked into the twigs, not a spike."""
    ca, sa = math.cos(ang), math.sin(ang)
    nx, ny = -sa, ca
    pts = []
    for f, w in ((0.0, 0.0), (0.32, wd), (0.64, wd * 0.78), (1.0, 0.0)):
        pts.append((bx + ca * ln * f + nx * w, by + sa * ln * f + ny * w))
    for f, w in ((1.0, 0.0), (0.64, wd * 0.78), (0.32, wd), (0.0, 0.0)):
        pts.append((bx + ca * ln * f - nx * w, by + sa * ln * f - ny * w))
    pygame.draw.polygon(surf, fill, [(int(x), int(y)) for x, y in pts])
    pygame.draw.line(surf, edge, (int(bx), int(by)),
                     (int(bx + ca * ln), int(by + sa * ln)), max(1, int(wd * 0.5)))


def _ivy_leaf(surf, cx0, cy0, ang, sz, fill, edge):
    """A rounded, fat heart-shaped ivy leaf — drawn as a filled disc-pair blob so
    it reads SOFT and round (the lush ivy read), the opposite of a pointed
    spike. A tiny stem + midrib anchor it to the vine along ``ang``."""
    ca, sa = math.cos(ang), math.sin(ang)
    # leaf body sits at the far end of a short stem; two overlapping circles make
    # the broad rounded lobes, a small one fills the rounded tip
    sx, sy = cx0 + ca * sz * 0.30, cy0 + sa * sz * 0.30        # stem base
    bx, by = cx0 + ca * sz * 0.70, cy0 + sa * sz * 0.70        # leaf centre
    nx, ny = -sa, ca
    lobe = max(2, int(sz * 0.34))
    for sgn in (-1, 1):
        pygame.draw.circle(surf, fill,
                           (int(bx + nx * sz * 0.22 * sgn),
                            int(by + ny * sz * 0.22 * sgn)), lobe)
    pygame.draw.circle(surf, fill,
                       (int(bx + ca * sz * 0.30), int(by + sa * sz * 0.30)),
                       max(2, int(sz * 0.26)))
    # short woody stem + a faint midrib so it's clearly a leaf on a vine
    pygame.draw.line(surf, edge, (int(sx), int(sy)), (int(bx), int(by)),
                     max(1, int(sz * 0.10)))
    pygame.draw.line(surf, edge, (int(bx), int(by)),
                     (int(bx + ca * sz * 0.34), int(by + sa * sz * 0.34)),
                     max(1, int(sz * 0.08)))


def _shed_leaf(surf, x, y, ln, ang, col, edge):
    _leaf(surf, x, y, ang, ln, ln * 0.36, col, edge)


# ── palette pairs (gold Fame / withered Shame) ──────────────────────────────
# One shared gold family for every Fame so the five read as one gilded set; one
# shared cold-pewter-with-brown family for every Shame.

_G_RIM_HI, _G_RIM_MID, _G_RIM_LO = (255, 234, 168), (236, 186, 72), (150, 102, 20)
_G_SPEC = (255, 250, 222)
_G_FACE_TOP, _G_FACE_BOT, _G_RECESS = (44, 32, 92), (16, 10, 44), (10, 6, 28)
_G_STEP_HI, _G_STEP_LO = (255, 226, 150), (140, 96, 22)
_G_GLY, _G_GLY_SH = (255, 236, 184), (32, 18, 44)
_G_TWIG_HI, _G_TWIG_LO = (250, 212, 108), (148, 100, 24)   # gilded branch
_G_LEAF_HI, _G_LEAF_LO = (244, 222, 130), (150, 108, 34)   # gilded leaf
_G_BUD = (255, 244, 196)

_S_RIM_HI, _S_RIM_MID, _S_RIM_LO = (150, 150, 156), (98, 96, 100), (54, 52, 56)
_S_FACE_TOP, _S_FACE_BOT, _S_RECESS = (50, 48, 54), (26, 24, 30), (16, 14, 20)
_S_STEP_HI, _S_STEP_LO = (150, 150, 156), (54, 52, 56)
_S_GLY, _S_GLY_SH = (176, 168, 156), (18, 16, 18)
_S_TWIG_HI, _S_TWIG_LO = (120, 110, 100), (66, 58, 52)     # bare grey deadwood
_S_LEAF_HI, _S_LEAF_LO = (138, 104, 56), (78, 54, 30)      # browned dry leaf
_S_LEAF_DEAD = (104, 88, 58)
_S_BUD = (96, 86, 70)


def _gold_kw():
    return dict(rim_hi=_G_RIM_HI, rim_mid=_G_RIM_MID, rim_lo=_G_RIM_LO,
                spec=_G_SPEC, face_top=_G_FACE_TOP, face_bot=_G_FACE_BOT,
                recess=_G_RECESS, step_hi=_G_STEP_HI, step_lo=_G_STEP_LO,
                gly=_G_GLY, gly_sh=_G_GLY_SH, sheen=ai._GLYPH_SHEEN)


def _shame_kw():
    return dict(rim_hi=_S_RIM_HI, rim_mid=_S_RIM_MID, rim_lo=_S_RIM_LO,
                spec=None, face_top=_S_FACE_TOP, face_bot=_S_FACE_BOT,
                recess=_S_RECESS, step_hi=_S_STEP_HI, step_lo=_S_STEP_LO,
                gly=_S_GLY, gly_sh=_S_GLY_SH, sheen=None)


# ═══════════════════════════════════════════════════════════════════════════
# 1) CORONA — a radial corona of forked twig POINTS all around the rim, like a
#    sunburst built from rough branches. Each point is a Y-forked twig (a main
#    spike with two short side prongs) so the silhouette is spiky AND woody.
#    Shame: many twigs SNAPPED to bare stubs, deterministic GAPS where whole
#    points broke off, the survivors crooked & grey, dead leaves shed below.
# ═══════════════════════════════════════════════════════════════════════════

def _gnarled_branch(surf, x0, y0, a, length, w, hi, lo, kinks, broken=False):
    """A gnarled branch grown outward from (x0,y0) along ``a`` in 2-3 KINKED
    segments (each segment swerves a little, so the branch bends like real wood,
    not a straight metal ray), forking a side-twig off a mid joint. ``kinks`` is a
    fixed per-branch angle list so the irregularity is deterministic. ``broken``
    snaps it after the first segment to a frayed bare stub."""
    segs = 2 if broken else 3
    px, py, pa = x0, y0, a
    seg_len = length / 3
    for s in range(segs):
        pa = a + kinks[s % len(kinks)]
        nx = px + math.cos(pa) * seg_len * (0.78 if s == segs - 1 else 1.0)
        ny = py + math.sin(pa) * seg_len * (0.78 if s == segs - 1 else 1.0)
        col = _dir_shade(pa, lo, hi)
        _twig(surf, px, py, nx, ny, max(2, int(w * (1.0 - 0.18 * s))), col, edge=lo)
        # a short side-twig forking off the first joint — the woody branch read
        if s == 0 and not broken:
            fa = pa + kinks[0] * 2.2 + math.radians(30)
            fx = nx + math.cos(fa) * seg_len * 0.62
            fy = ny + math.sin(fa) * seg_len * 0.62
            _twig(surf, nx, ny, fx, fy, max(1, int(w * 0.6)),
                  _dir_shade(fa, lo, hi), edge=lo)
        px, py = nx, ny
    if broken:
        # frayed snapped tip — a tiny split
        for sgn in (-1, 1):
            sx = px + math.cos(pa + sgn * 0.6) * seg_len * 0.18
            sy = py + math.sin(pa + sgn * 0.6) * seg_len * 0.18
            pygame.draw.line(surf, lo, (int(px), int(py)), (int(sx), int(sy)),
                             max(1, int(w * 0.5)))


def _corona_twigs(surf, cx, cy, R, core, hi, lo, n=13, broken=False):
    """An IRREGULAR corona of gnarled forked branches — varying length, angle and
    bark kinks per branch (deterministic jitter) so the silhouette reads as a
    tangle of woven branches, NOT a stamped metal sunburst. ``broken`` removes a
    cluster of branches (a clear gap) and snaps several survivors to bare stubs."""
    base = int(core * 1.0)
    gone = {2, 3, 8} if broken else set()          # a clustered gap, not scattered
    stub = {5, 10} if broken else set()
    span = R - base
    for i in range(n):
        if i in gone:
            continue
        # uneven angular spacing + a per-branch lean so no two branches are alike
        jit = (((i * 53) % 17) - 8) / 8.0
        a = (i / n) * math.tau - math.pi / 2 + math.radians(10) * jit
        # length varies branch-to-branch (long/medium/short, pseudo-random)
        lf = (0.62 + 0.40 * (((i * 31) % 11) / 10.0))
        length = span * lf
        if broken:
            a += math.radians(((i * 41) % 19) - 9)   # everything leans crooked
        if i in stub:
            length *= 0.42
        bx, by = cx + math.cos(a) * base, cy + math.sin(a) * base
        w = max(2, int(R * 0.05))
        kinks = [math.radians(((i * 7) % 5) - 2) * (1 if i % 2 else -1),
                 math.radians(((i * 13) % 7) - 3),
                 math.radians(((i * 5) % 5) - 2) * (-1 if i % 2 else 1)]
        _gnarled_branch(surf, bx, by, a, length, w, hi, lo, kinks,
                        broken=(i in stub))


def fame_corona(surf, cx, cy, R, glyph_key):
    blit_glow(surf, cx, cy, int(R * 1.02), (255, 206, 110), 60)
    core = int(R * _CORE)
    _corona_twigs(surf, cx, cy, R, core, _G_TWIG_HI, _G_TWIG_LO, n=13)
    _core_disc(surf, cx, cy, core, glyph_key=glyph_key, **_gold_kw())


def shame_corona(surf, cx, cy, R, glyph_key):
    core = int(R * _CORE)
    _corona_twigs(surf, cx, cy, R, core, _S_TWIG_HI, _S_TWIG_LO, n=13,
                  broken=True)
    # a couple of dead leaves shed below, pulled inside the badge bound
    for fx, fy, fl, fa in ((-0.30, 0.86, 0.26, 1.7), (0.34, 0.80, 0.24, 2.4)):
        _shed_leaf(surf, cx + R * fx, cy + R * fy, R * fl, fa,
                   _S_LEAF_DEAD, _S_LEAF_LO)
    _core_disc(surf, cx, cy, core, glyph_key=glyph_key, **_shame_kw())


# ═══════════════════════════════════════════════════════════════════════════
# 2) CIRCLET — a woven horizontal branch BAND hugging the rim with THREE taller
#    crown PEAKS rising at the top (a centre spire flanked by two shorter ones),
#    the rustic "king's twig crown". The band is two counter-wound branches
#    crossing in an X-weave; small leaves tuck into the peaks.
#    Shame: the weave UNRAVELS (a branch springs loose), the side peaks SNAP to
#    bare stubs, leaves browned & shed.
# ═══════════════════════════════════════════════════════════════════════════

def _woven_band(surf, cx, cy, core, hi, lo, unravel=False):
    """A basket-weave band: short twig segments laid at alternating +/- diagonals
    so they read as branches woven OVER and UNDER each other around the rim — a
    real plaited circlet, not a smooth blob. ``unravel`` springs a stretch of the
    upper-right band loose (segments lift away + a gap) so the weave comes apart."""
    band = core * 1.08
    n = 22
    seg = math.tau / n
    loose_lo, loose_hi = math.radians(300), math.radians(360)
    for i in range(n):
        a = (i + 0.5) * seg
        loose = unravel and loose_lo < a < loose_hi
        if unravel and math.radians(320) < a < math.radians(344):
            continue                          # a gap where the weave broke open
        col = _dir_shade(a, lo, hi)
        # each strand is a short diagonal twig spanning ~1.4 segments, tilted +/-
        tilt = seg * 0.7 * (1 if i % 2 == 0 else -1)
        lift = (a - loose_lo) / (loose_hi - loose_lo) * core * 0.22 if loose else 0.0
        a0, a1 = a - tilt, a + tilt
        x0 = cx + math.cos(a0) * (band - core * 0.05 + lift)
        y0 = cy + math.sin(a0) * (band - core * 0.05 + lift)
        x1 = cx + math.cos(a1) * (band + core * 0.05 + lift)
        y1 = cy + math.sin(a1) * (band + core * 0.05 + lift)
        _twig(surf, x0, y0, x1, y1, max(2, int(core * 0.05)), col, edge=lo)


def _peak(surf, cx, cy, base_r, ax, h, w, hi, lo, snapped=False, leafy=True):
    """One upswept crown peak — a tapered twig spire rising radially off the band
    at angle ``ax``, with a small leaf cluster at the tip (Fame). ``snapped``
    lops it to a jagged bare stub."""
    bx = cx + math.cos(ax) * base_r
    by = cy + math.sin(ax) * base_r
    ph = h * (0.34 if snapped else 1.0)
    tx = cx + math.cos(ax) * (base_r + ph)
    ty = cy + math.sin(ax) * (base_r + ph)
    col = _dir_shade(ax, lo, hi)
    _twig(surf, bx, by, tx, ty, w, col, edge=lo)
    if snapped:
        # frayed broken top — two tiny split slivers
        for sgn in (-1, 1):
            sx = tx + math.cos(ax + sgn * 0.5) * h * 0.10
            sy = ty + math.sin(ax + sgn * 0.5) * h * 0.10
            pygame.draw.line(surf, lo, (int(tx), int(ty)), (int(sx), int(sy)),
                             max(1, int(w * 0.6)))
        return
    if leafy:
        # a small paired leaf tuft at the tip — kept tight so the spire's POINT
        # stays the silhouette, the leaves just soften it
        for sgn in (-1, 1):
            _leaf(surf, tx, ty, ax + sgn * math.radians(58), h * 0.20, h * 0.08,
                  lerp_color(lo, hi, 0.62), lo)
        pygame.draw.circle(surf, hi, (int(tx), int(ty)), max(2, int(w * 0.8)))


def fame_circlet(surf, cx, cy, R, glyph_key):
    blit_glow(surf, cx, cy, int(R * 0.98), (255, 206, 110), 52)
    core = int(R * _CORE)
    base_r = int(core * 1.02)
    _woven_band(surf, cx, cy, core, _G_TWIG_HI, _G_TWIG_LO)
    # peaks reach from the band toward the badge bound — the dominant read. The
    # spire stops short of R so its tip LEAF CLUSTER still fits inside the bound.
    peak_h = (R - base_r)
    # centre spire tallest, two flanking shorter & splayed wide — three clearly
    # separate crown spires above the band
    _peak(surf, cx, cy, base_r, math.radians(-90), peak_h * 0.92,
          max(4, int(R * 0.07)), _G_TWIG_HI, _G_TWIG_LO)
    for sgn in (-1, 1):
        _peak(surf, cx, cy, base_r, math.radians(-90 + sgn * 46), peak_h * 0.62,
              max(3, int(R * 0.06)), _G_TWIG_HI, _G_TWIG_LO)
    _core_disc(surf, cx, cy, core, glyph_key=glyph_key, **_gold_kw())


def shame_circlet(surf, cx, cy, R, glyph_key):
    core = int(R * _CORE)
    base_r = int(core * 1.02)
    _woven_band(surf, cx, cy, core, _S_TWIG_HI, _S_TWIG_LO, unravel=True)
    peak_h = (R - base_r)
    # centre spire survives but bare & leafless; both flanks snapped to stubs
    _peak(surf, cx, cy, base_r, math.radians(-90), peak_h * 0.92,
          max(4, int(R * 0.07)), _S_TWIG_HI, _S_TWIG_LO, leafy=False)
    for sgn in (-1, 1):
        _peak(surf, cx, cy, base_r, math.radians(-90 + sgn * 46), peak_h * 0.62,
              max(3, int(R * 0.06)), _S_TWIG_HI, _S_TWIG_LO, snapped=True)
    for fx, fy, fl, fa in ((-0.26, 0.88, 0.24, 1.7), (0.30, 0.82, 0.22, 2.5)):
        _shed_leaf(surf, cx + R * fx, cy + R * fy, R * fl, fa,
                   _S_LEAF_DEAD, _S_LEAF_LO)
    _core_disc(surf, cx, cy, core, glyph_key=glyph_key, **_shame_kw())


# ═══════════════════════════════════════════════════════════════════════════
# 3) THORN — a thin sinuous THORNY branch ring: one slender wiry branch winding
#    around the rim, studded with paired sharp barbs/thorns and a few sparse
#    leaves. The read is delicate-but-dangerous (crown-of-thorns lineage), the
#    OPPOSITE of the heavy corona.
#    Shame: the branch withers & SPLITS open (a gap where it snapped), most
#    thorns broken to blunt nubs, the sparse leaves gone, a thorn or two shed.
# ═══════════════════════════════════════════════════════════════════════════

def _thorn_ring(surf, cx, cy, core, hi, lo, withered=False):
    ring_r = core * 1.10
    amp = core * 0.05
    N = 80
    pts = []
    gap_lo, gap_hi = math.radians(36), math.radians(70)   # where it splits
    drawn = []
    for k in range(N + 1):
        a = k / N * math.tau
        if withered and gap_lo < a < gap_hi:
            if pts:
                drawn.append(pts); pts = []
            continue
        rr = ring_r + math.sin(a * 5) * amp
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr, a))
    if pts:
        drawn.append(pts)
    col = _dir_shade(math.radians(135), lo, hi)
    for seg in drawn:
        line = [(int(x), int(y)) for x, y, _ in seg]
        if len(line) < 2:
            continue
        pygame.draw.lines(surf, lo, False, line, max(3, int(core * 0.07)))
        pygame.draw.lines(surf, col, False, line, max(2, int(core * 0.04)))
    # paired barbs every few steps, pointing out then in (thorn lineage)
    barb_n = 22
    broken = {2, 5, 9, 12, 16, 19} if withered else set()
    for j in range(barb_n):
        a = j / barb_n * math.tau
        if withered and gap_lo < a < gap_hi:
            continue
        rr = ring_r + math.sin(a * 5) * amp
        bx, by = cx + math.cos(a) * rr, cy + math.sin(a) * rr
        tcol = _dir_shade(a, lo, hi)
        tl = core * (0.10 if (j in broken) else 0.22)
        for outward in (1, -1):
            ta = a if outward > 0 else a + math.pi
            # tangential lean so barbs hook rather than radiate straight
            ta += math.radians(26) * (1 if j % 2 else -1)
            tx = bx + math.cos(ta) * tl * outward
            ty = by + math.sin(ta) * tl * outward
            if withered and outward < 0:
                continue                       # inner barbs broke off
            _twig(surf, bx, by, tx, ty, max(1, int(core * 0.028)), tcol, edge=lo)
    if not withered:
        # a few sparse leaves at the cardinal flanks
        for a in (math.radians(150), math.radians(210), math.radians(30)):
            rr = ring_r + math.sin(a * 5) * amp
            lx, ly = cx + math.cos(a) * rr, cy + math.sin(a) * rr
            _leaf(surf, lx, ly, a + math.radians(40), core * 0.26, core * 0.10,
                  lerp_color(lo, hi, 0.6), lo)


def fame_thorn(surf, cx, cy, R, glyph_key):
    core = int(R * _CORE)
    _thorn_ring(surf, cx, cy, core, _G_TWIG_HI, _G_TWIG_LO)
    _core_disc(surf, cx, cy, core, glyph_key=glyph_key, **_gold_kw())


def shame_thorn(surf, cx, cy, R, glyph_key):
    core = int(R * _CORE)
    _thorn_ring(surf, cx, cy, core, _S_TWIG_HI, _S_TWIG_LO, withered=True)
    # a snapped-off thorn shard tumbling at the lower rim (inside the bound)
    bx, by = cx - R * 0.20, cy + R * 0.80
    _twig(surf, bx, by, bx + R * 0.18, by + R * 0.10, max(1, int(R * 0.03)),
          _S_TWIG_LO, edge=_S_RIM_LO)
    _core_disc(surf, cx, cy, core, glyph_key=glyph_key, **_shame_kw())


# ═══════════════════════════════════════════════════════════════════════════
# 4) IVY — a dense leafy IVY/VINE crown: a vine winding the rim smothered in
#    overlapping ROUNDED three-lobe ivy leaves, lush and full. The silhouette is
#    soft, bumpy and continuous (the opposite of the spiky corona).
#    Shame: the leaves brown, curl and THIN OUT to bare patches of vine, a clear
#    gap of naked stem on one flank, several leaves shed and tumbling.
# ═══════════════════════════════════════════════════════════════════════════

def _ivy_crown(surf, cx, cy, core, vine_hi, vine_lo, leaf_hi, leaf_lo,
               leaf_dead=None, withered=False):
    ring_r = core * 1.08
    # the woody vine the leaves ride on
    N = 64
    vpts = []
    for k in range(N + 1):
        a = k / N * math.tau
        rr = ring_r + math.sin(a * 4) * core * 0.03
        vpts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    pygame.draw.lines(surf, vine_lo, False,
                      [(int(x), int(y)) for x, y in vpts], max(2, int(core * 0.05)))
    leaves = 22
    bare_lo, bare_hi = math.radians(330), math.radians(360)   # naked-stem gap
    drop = {1, 4, 6, 9, 13, 17, 20} if withered else set()
    for i in range(leaves):
        a = i / leaves * math.tau + math.radians(8)
        if withered and bare_lo < (a % math.tau) < bare_hi:
            continue                       # a stretch of bare vine
        if i in drop:
            continue                       # thinned out
        rr = ring_r + math.sin(a * 4) * core * 0.03
        lx, ly = cx + math.cos(a) * rr, cy + math.sin(a) * rr
        sz = core * (0.30 if not withered else 0.24)
        out = a + (math.radians(18) if i % 2 else math.radians(-14))
        col_hi, col_lo = (leaf_hi, leaf_lo)
        if withered and i % 3 == 0:
            col_hi, col_lo = leaf_dead, leaf_lo
        col = _dir_shade(a, col_lo, col_hi)
        _ivy_leaf(surf, lx, ly, out, sz, col, leaf_lo)


def fame_ivy(surf, cx, cy, R, glyph_key):
    blit_glow(surf, cx, cy, int(R * 0.98), (255, 210, 120), 48)
    core = int(R * _CORE)
    _ivy_crown(surf, cx, cy, core, _G_TWIG_HI, _G_TWIG_LO, _G_LEAF_HI, _G_LEAF_LO)
    _core_disc(surf, cx, cy, core, glyph_key=glyph_key, **_gold_kw())


def shame_ivy(surf, cx, cy, R, glyph_key):
    core = int(R * _CORE)
    _ivy_crown(surf, cx, cy, core, _S_TWIG_HI, _S_TWIG_LO, _S_LEAF_HI,
               _S_LEAF_LO, leaf_dead=_S_LEAF_DEAD, withered=True)
    # shed ivy leaves tumbling below (rounded, so they read as the same leaf)
    for fx, fy, fa in ((-0.28, 0.86, 1.8), (0.10, 0.92, 2.3), (0.40, 0.80, 2.7)):
        _ivy_leaf(surf, cx + R * fx, cy + R * fy, fa, R * 0.18,
                  _S_LEAF_DEAD, _S_LEAF_LO)
    _core_disc(surf, cx, cy, core, glyph_key=glyph_key, **_shame_kw())


# ═══════════════════════════════════════════════════════════════════════════
# 5) BIRCH — slender drooping BIRCH/WILLOW twig crown: fine whip-like twigs
#    arching up off the rim and DRAOPING back down, each hung with little oval
#    buds/catkins like beads. Delicate, weeping, airy — distinct from every
#    other concept's read.
#    Shame: the buds have DROPPED off (bare whips), several twigs snapped, the
#    whips withered grey, a scatter of fallen buds at the base.
# ═══════════════════════════════════════════════════════════════════════════

def _weeping_whip(surf, cx, cy, base_r, a, length, hi, lo, bud_col,
                  snapped=False, budless=False):
    """One drooping willow whip: rises radially then curls back tangentially
    (a weeping arc), strung with small oval buds. ``snapped`` cuts it short and
    bare; ``budless`` keeps the whip but drops every bud."""
    bx = cx + math.cos(a) * base_r
    by = cy + math.sin(a) * base_r
    rise = length * (0.34 if snapped else 1.0)
    # control point pushed out + tangential so the tip weeps sideways-down
    cax = a + math.radians(40)
    px = bx + math.cos(a) * rise
    py = by + math.sin(a) * rise
    tx = px + math.cos(cax) * rise * 0.5
    ty = py + math.sin(cax) * rise * 0.5 + rise * 0.25     # droop
    pts = []
    for k in range(11):
        t = k / 10
        mt = 1 - t
        x = mt * mt * bx + 2 * mt * t * px + t * t * tx
        y = mt * mt * by + 2 * mt * t * py + t * t * ty
        pts.append((x, y))
    col = _dir_shade(a, lo, hi)
    pygame.draw.lines(surf, lo, False,
                      [(int(x), int(y)) for x, y in pts], max(2, int(length * 0.10)))
    pygame.draw.lines(surf, col, False,
                      [(int(x), int(y)) for x, y in pts], max(1, int(length * 0.06)))
    if snapped or budless:
        return
    # oval buds/catkins strung along the outer half of the whip
    for k in (4, 6, 8, 10):
        x, y = pts[k]
        br = max(2, int(length * 0.10))
        pygame.draw.ellipse(surf, bud_col,
                            (int(x - br * 0.7), int(y - br), int(br * 1.4), int(br * 2)))


def fame_birch(surf, cx, cy, R, glyph_key):
    blit_glow(surf, cx, cy, int(R * 1.0), (255, 214, 130), 50)
    core = int(R * _CORE)
    base_r = int(core * 1.04)
    length = (R - base_r) * 0.94
    n = 12
    for i in range(n):
        a = i / n * math.tau - math.pi / 2
        _weeping_whip(surf, cx, cy, base_r, a, length, _G_TWIG_HI, _G_TWIG_LO,
                      _G_BUD)
    _core_disc(surf, cx, cy, core, glyph_key=glyph_key, **_gold_kw())


def shame_birch(surf, cx, cy, R, glyph_key):
    core = int(R * _CORE)
    base_r = int(core * 1.04)
    length = (R - base_r) * 0.94
    n = 12
    snap = {1, 4, 8, 11}
    for i in range(n):
        a = i / n * math.tau - math.pi / 2
        _weeping_whip(surf, cx, cy, base_r, a, length, _S_TWIG_HI, _S_TWIG_LO,
                      _S_BUD, snapped=(i in snap), budless=True)
    # fallen buds scattered at the base, inside the badge bound
    for fx, fy in ((-0.22, 0.84), (0.06, 0.92), (0.30, 0.82), (-0.04, 0.78)):
        x, y = cx + R * fx, cy + R * fy
        br = max(2, int(R * 0.035))
        pygame.draw.ellipse(surf, _S_BUD, (int(x - br), int(y - br),
                                           int(br * 2), int(br * 2.4)))
    _core_disc(surf, cx, cy, core, glyph_key=glyph_key, **_shame_kw())


# Each concept pairs a Fame composer with its degraded Shame twin.
CONCEPTS = [
    ("corona", fame_corona, shame_corona),
    ("circlet", fame_circlet, shame_circlet),
    ("thorn", fame_thorn, shame_thorn),
    ("ivy", fame_ivy, shame_ivy),
    ("birch", fame_birch, shame_birch),
]
