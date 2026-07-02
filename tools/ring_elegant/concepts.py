"""Five SLIM/ELEGANT paired outer-RING concepts for the achievement medallion.

Same approved Fame -> Shame TRADE-OFF as ``tools/ring_tradeoff`` — Fame is the
beautiful ring, Shame is the SAME ring quietly gone bad — but the perimeter is
made THIN, delicate and refined so the center medal + emblem is the calm
dominant element and the ring is a graceful jeweller's accent. The previous
round's rings (coin/gem/flame/seal/enamel) overpowered the emblem; every ring
here is a hairline-weight accent riding a slim frame around a LARGE calm navy
face, with generous negative space.

  * ``fame_<name>``  — the accent at its most premium: crisp, lit, delicate.
  * ``shame_<name>`` — the SAME slim accent RESTRAINEDLY ruined (tarnished,
    faded, a piece missing) — the ruin still reads, gently; never gory.

The five are distinct in what the accent IS and how it fails:

  1) FILIGREE  fine wire scrollwork  -> tarnished, a curl broken / unravelled
  2) PEARLS    a row of small beads   -> dulled grey, one or two missing (gap)
  3) HAIRLINE  a slim double gold line -> faded/broken, tiny accents chipped
  4) SOLITAIRE 3-4 small spaced gems   -> clouded, one empty socket
  5) HALO      a soft luminous rim     -> glow faded to a dim, broken line

The CENTER emblem is never redesigned — every composer stamps the live engraved
glyph through ``ai._stamp_glyph`` (``pillar_100`` in Fame, ``goose_egg`` in
Shame). NO diagonal crack cue. NO laurel / leaf / twig.

WRITE-ONLY scratch under ``tools/`` — never bundled; imports ``game`` read-only.
Composers render at the REAL badge geometry (``R = 0.46 * px``); the slim rings
sit well inside the badge square with generous margin.
"""
from __future__ import annotations

import math
import pygame

import game.achievement_icons as ai
from game.draw import lerp_color, blit_glow

_LIGHT = ai._LIGHT  # share the family's one upper-left light source

# ── shared geometry — a big calm navy field, a hairline rim, a floating accent ─
# The navy face is nearly full so the emblem + negative space dominate; the metal
# rim is a true hairline, and the ornament floats as a delicate ring ON the field
# (a moat of navy on either side) rather than a chunky decorated bezel.
_FACE_F   = 0.92    # face radius / R  (near-full -> generous negative space)
_BAND_IN  = 0.88    # metal rim's inner radius / R (visible hairline rim ~0.08R)
_ORN_R    = 0.80    # ornament centre radius / R (floats on the navy field)
_GLYPH_F  = 0.62    # glyph radius / R (the prominent, calm focal point)

# ── shared palettes ──────────────────────────────────────────────────────────
# Fame gold — the family's warm struck gold; the only fully saturated accent.
_G_HI   = (255, 232, 160)
_G_MID  = (232, 186,  74)
_G_LO   = (150, 102,  22)
_G_EDGE = ( 70,  44,   8)
_G_SPEC = (255, 250, 222)
_FACE_TOP = (44, 32, 92)
_FACE_BOT = (16, 10, 44)
_FACE_REC = (10,  6, 28)
_GLY    = (255, 236, 184)
_GLY_SH = ( 32,  18,  44)

# Shame pewter — the SAME frame gone cold; lifted a touch so a thin ruined ring
# still reads at 44px (never a flat grey blob). A muted, restrained tarnish tone
# is the only "colour" here, mirroring gold as Fame's only accent.
_P_HI   = (176, 180, 192)
_P_MID  = (118, 122, 138)
_P_LO   = ( 60,  64,  80)
_P_EDGE = ( 26,  26,  34)
_P_TARN = (120, 108,  86)   # dull warm tarnish creep
_P_TARN2 = ( 84,  76,  62)
_P_FACE_TOP = (52, 54, 74)
_P_FACE_BOT = (28, 30, 48)
_P_FACE_REC = (14, 14, 26)
_P_GLY  = (196, 200, 214)
_P_GLY_SH = (16, 16, 26)


# ── shared low-level helpers ────────────────────────────────────────────────

def _center(surf, glyph_key, cx, cy, R, gly, gly_sh, sheen=None):
    ai._stamp_glyph(surf, glyph_key, cx, cy, int(R * _GLYPH_F), gly, gly_sh, sheen)


def _slim_band(surf, cx, cy, R, hi, mid, lo, spec=None, edge=None,
               light=_LIGHT, spec_span=0.5):
    """A SLIM struck-metal frame from ``R`` in to ``_BAND_IN*R`` under the one
    upper-left light — the same strike geometry as the live family but a fraction
    of its width, so the perimeter reads as a refined bezel, not a chunky bevel."""
    inner = int(R * _BAND_IN)
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
    pygame.draw.circle(surf, mid, (cx, cy), R, max(1, R // 30))
    if edge is not None:
        pygame.draw.circle(surf, edge, (cx, cy), R, max(1, R // 44))


def _finish_center(surf, cx, cy, R, hi, lo, ftop, fbot, frec, gk, gly, gly_sh,
                   sheen=None):
    """Draw the shared large calm center: a thin step keyline, the big recessed
    face, and the live engraved emblem — identical construction across concepts
    so only the perimeter carries the trade-off."""
    fr = int(R * _FACE_F)
    ai._draw_step(surf, cx, cy, fr + max(1, R // 22), hi, lo)
    ai._draw_face(surf, cx, cy, fr, ftop, fbot, frec)
    _center(surf, gk, cx, cy, R, gly, gly_sh, sheen)


def _tarnish_creep(surf, cx, cy, R, seed, n=16):
    """A few faint, restrained oxide flecks on the pewter frame — enough to read
    'tarnished', never a corroded mess."""
    s = seed
    for i in range(n):
        s = (s * 1103515245 + 12345) & 0x7fffffff
        a = (s / 0x7fffffff) * math.tau
        s = (s * 1103515245 + 12345) & 0x7fffffff
        rad = R * (_BAND_IN + (1.0 - _BAND_IN) * (s / 0x7fffffff))
        px = cx + int(math.cos(a) * rad)
        py = cy + int(math.sin(a) * rad)
        col = _P_TARN if i % 2 else _P_TARN2
        pygame.draw.circle(surf, col, (px, py), max(1, R // 60))


# ═══════════════════════════════════════════════════════════════════════════
# 1) FILIGREE — a fine wire scrollwork ring.
#    Fame: delicate gold double-C scrolls repeated round a slim band, hairline
#    weight, openwork so the navy face breathes between them. Shame: the SAME
#    scrolls tarnished to pewter, faded thinner, and one scroll BROKEN — its
#    wire come loose and unravelled into a trailing curl, leaving a gap.
# ═══════════════════════════════════════════════════════════════════════════

def _scroll(surf, cx, cy, a, rc, size, col, dark, w, unravelled=False):
    """One filigree motif centred at angle ``a`` on the band: a symmetric pair of
    small C-curls meeting at a stem — the classic scrollwork unit, stroked with a
    faint dark under-offset so the wire reads engraved. ``unravelled`` breaks it
    into a loose trailing wisp instead of a tidy pair."""
    mx = cx + math.cos(a) * rc
    my = cy + math.sin(a) * rc
    # tangent / normal frame so the motif lies along the ring
    tx, ty = -math.sin(a), math.cos(a)
    nx, ny = math.cos(a), math.sin(a)
    if unravelled:
        # a wire come loose: a slack sagging thread curling off the ring
        pts = []
        for k in range(9):
            f = k / 8
            off_t = (f - 0.5) * size * 2.6
            off_n = math.sin(f * math.pi * 2.4) * size * 0.5 - f * size * 0.9
            pts.append((mx + tx * off_t + nx * off_n,
                        my + ty * off_t + ny * off_n))
        pygame.draw.lines(surf, dark, False,
                          [(int(x + 1), int(y + 1)) for x, y in pts], max(1, w))
        pygame.draw.lines(surf, col, False,
                          [(int(x), int(y)) for x, y in pts], max(1, w))
        return
    for sgn in (-1, 1):
        # a C-curl: a ~270deg arc of a small circle, offset to one side of the stem
        ccx = mx + tx * sgn * size * 0.72
        ccy = my + ty * sgn * size * 0.72
        cr = size * 0.66
        a0 = a - sgn * math.radians(50)
        a1 = a + sgn * math.radians(215)
        rect = pygame.Rect(int(ccx - cr), int(ccy - cr), int(cr * 2), int(cr * 2))
        pygame.draw.arc(surf, dark, rect.move(1, 1),
                        min(a0, a1), max(a0, a1), max(1, w))
        pygame.draw.arc(surf, col, rect, min(a0, a1), max(a0, a1), max(1, w))
    # a small central bud where the two curls meet
    pygame.draw.circle(surf, col, (int(mx), int(my)), max(1, int(size * 0.18)))


def _filigree_ring(surf, cx, cy, R, col, dark, tarnished=False):
    n = 8
    rc = R * _ORN_R
    size = R * 0.115
    w = max(1, R // 30)
    broken = 4 if tarnished else -1        # one scroll comes undone
    for i in range(n):
        a = i / n * math.tau - math.pi / 2
        _scroll(surf, cx, cy, a, rc, size, col, dark, w,
                unravelled=(i == broken))


def fame_filigree(surf, cx, cy, R, glyph_key):
    _slim_band(surf, cx, cy, R, _G_HI, _G_MID, _G_LO, spec=_G_SPEC, edge=_G_EDGE)
    _finish_center(surf, cx, cy, R, _G_HI, _G_LO, _FACE_TOP, _FACE_BOT, _FACE_REC,
                   glyph_key, _GLY, _GLY_SH, ai._GLYPH_SHEEN)
    _filigree_ring(surf, cx, cy, R, _G_HI, _G_LO)


def shame_filigree(surf, cx, cy, R, glyph_key):
    _slim_band(surf, cx, cy, R, _P_HI, _P_MID, _P_LO, spec=None, edge=_P_EDGE)
    _tarnish_creep(surf, cx, cy, R, seed=13)
    _finish_center(surf, cx, cy, R, _P_HI, _P_LO, _P_FACE_TOP, _P_FACE_BOT,
                   _P_FACE_REC, glyph_key, _P_GLY, _P_GLY_SH)
    _filigree_ring(surf, cx, cy, R, _P_MID, _P_LO, tarnished=True)


# ═══════════════════════════════════════════════════════════════════════════
# 2) PEARLS — a single delicate row of small beads on a slim band.
#    Fame: evenly spaced luminous pearls, each cupped in a tiny gold seat, with a
#    soft upper-left highlight + lower shadow so each reads round. Shame: the SAME
#    row dulled to chalky grey, glints gone, and one or two pearls MISSING —
#    empty seats left as small dark cups (a gap in the strand).
# ═══════════════════════════════════════════════════════════════════════════
_PEARL_HI  = (255, 252, 246)
_PEARL_MID = (226, 220, 224)
_PEARL_LO  = (170, 162, 172)
_PD_MID    = (150, 150, 158)   # dulled chalky pearl
_PD_LO     = (104, 104, 112)


def _pearl_row(surf, cx, cy, R, seat_hi, seat_lo, pearl=True, dulled=False):
    n = 15
    rc = R * _ORN_R
    pr = int(R * 0.072)
    missing = {3, 4} if not pearl else set()   # a two-bead gap in the strand
    for i in range(n):
        a = i / n * math.tau - math.pi / 2
        gx = int(cx + math.cos(a) * rc)
        gy = int(cy + math.sin(a) * rc)
        # tiny gold seat cup under every position
        pygame.draw.circle(surf, seat_lo, (gx, gy), pr + max(1, R // 46))
        pygame.draw.circle(surf, seat_hi, (gx, gy), pr + max(1, R // 46),
                           max(1, R // 60))
        if i in missing:
            # empty seat: a small dark socket with a faint lit lower lip
            pygame.draw.circle(surf, (14, 14, 20), (gx, gy), pr)
            pygame.draw.arc(surf, seat_lo,
                            (gx - pr, gy - pr, pr * 2, pr * 2),
                            math.radians(200), math.radians(340), max(1, R // 50))
            continue
        base = _PD_LO if dulled else _PEARL_LO
        body = _PD_MID if dulled else _PEARL_MID
        pygame.draw.circle(surf, base, (gx, gy), pr)
        pygame.draw.circle(surf, body, (gx, gy), int(pr * 0.92))
        if dulled:
            # a faint hairline flaw so the survivors look chalky, not fresh
            pygame.draw.line(surf, _PD_LO, (gx - pr // 2, gy),
                             (gx + pr // 3, gy + pr // 2), max(1, R // 70))
        else:
            pygame.draw.circle(surf, _PEARL_HI,
                               (gx - pr // 3, gy - pr // 3), max(1, pr // 3))


def fame_pearls(surf, cx, cy, R, glyph_key):
    _slim_band(surf, cx, cy, R, _G_HI, _G_MID, _G_LO, spec=_G_SPEC, edge=_G_EDGE)
    _finish_center(surf, cx, cy, R, _G_HI, _G_LO, _FACE_TOP, _FACE_BOT, _FACE_REC,
                   glyph_key, _GLY, _GLY_SH, ai._GLYPH_SHEEN)
    _pearl_row(surf, cx, cy, R, _G_HI, _G_LO, pearl=True)


def shame_pearls(surf, cx, cy, R, glyph_key):
    _slim_band(surf, cx, cy, R, _P_HI, _P_MID, _P_LO, spec=None, edge=_P_EDGE)
    _tarnish_creep(surf, cx, cy, R, seed=29)
    _finish_center(surf, cx, cy, R, _P_HI, _P_LO, _P_FACE_TOP, _P_FACE_BOT,
                   _P_FACE_REC, glyph_key, _P_GLY, _P_GLY_SH)
    _pearl_row(surf, cx, cy, R, _P_MID, _P_LO, pearl=False, dulled=True)


# ═══════════════════════════════════════════════════════════════════════════
# 3) HAIRLINE — a slim double gold line with a few tiny refined accents.
#    Fame: two crisp concentric gold hairlines hugging the rim, with a small
#    quatrefoil fleuron accent at each of the four cardinals between them —
#    minimal, architectural, all negative space. Shame: the SAME lines faded and
#    BROKEN into an uneven dashed remnant, one line gone over an arc, and the
#    accents chipped down to bare nubs (one missing).
# ═══════════════════════════════════════════════════════════════════════════

def _fleuron(surf, cx, cy, r, col, dark):
    """A tiny four-lobe quatrefoil accent — a refined jeweller's dot cluster."""
    for k in range(4):
        a = k * math.pi / 2 - math.pi / 4
        lx = int(cx + math.cos(a) * r)
        ly = int(cy + math.sin(a) * r)
        pygame.draw.circle(surf, dark, (lx + 1, ly + 1), max(1, int(r * 0.7)))
        pygame.draw.circle(surf, col, (lx, ly), max(1, int(r * 0.7)))
    pygame.draw.circle(surf, col, (int(cx), int(cy)), max(1, int(r * 0.5)))


def _dashed_arc(surf, cx, cy, rad, col, w, gaps):
    """A ring drawn as short arc dashes with a few ``gaps`` (a0,a1) skipped — a
    faded hairline that has worn through in places."""
    seg = 40
    for k in range(seg):
        a0 = k / seg * math.tau
        a1 = (k + 1) / seg * math.tau
        amid = (a0 + a1) / 2 % math.tau
        if any(g0 <= amid <= g1 for g0, g1 in gaps):
            continue
        if k % 3 == 2:                       # thin the surviving line to a dash
            continue
        rect = pygame.Rect(int(cx - rad), int(cy - rad), int(rad * 2), int(rad * 2))
        pygame.draw.arc(surf, col, rect, -a1, -a0, max(1, w))


def _hairlines(surf, cx, cy, R, col, dark, accent, broken=False):
    r_out = R * 0.865
    r_in = R * 0.735
    w = max(1, R // 32)
    if broken:
        _dashed_arc(surf, cx, cy, r_out, col, w,
                    gaps=[(math.radians(20), math.radians(70))])
        _dashed_arc(surf, cx, cy, r_in, col, w,
                    gaps=[(math.radians(190), math.radians(300))])
    else:
        pygame.draw.circle(surf, dark, (cx, cy), int(r_out) + 1, max(1, R // 44))
        pygame.draw.circle(surf, col, (cx, cy), int(r_out), w)
        pygame.draw.circle(surf, dark, (cx, cy), int(r_in) + 1, max(1, R // 44))
        pygame.draw.circle(surf, col, (cx, cy), int(r_in), w)
    rc = (r_out + r_in) / 2
    fr = R * 0.055
    for k in range(4):
        a = k * math.pi / 2 - math.pi / 2
        fx = cx + math.cos(a) * rc
        fy = cy + math.sin(a) * rc
        if broken and k == 1:                # one accent chipped away to a nub
            pygame.draw.circle(surf, dark, (int(fx), int(fy)), max(1, R // 44))
            continue
        _fleuron(surf, fx, fy, fr, col, dark)


def fame_hairline(surf, cx, cy, R, glyph_key):
    _slim_band(surf, cx, cy, R, _G_HI, _G_MID, _G_LO, spec=_G_SPEC, edge=_G_EDGE)
    _finish_center(surf, cx, cy, R, _G_HI, _G_LO, _FACE_TOP, _FACE_BOT, _FACE_REC,
                   glyph_key, _GLY, _GLY_SH, ai._GLYPH_SHEEN)
    _hairlines(surf, cx, cy, R, _G_HI, _G_LO, _G_MID)


def shame_hairline(surf, cx, cy, R, glyph_key):
    _slim_band(surf, cx, cy, R, _P_HI, _P_MID, _P_LO, spec=None, edge=_P_EDGE)
    _tarnish_creep(surf, cx, cy, R, seed=47)
    _finish_center(surf, cx, cy, R, _P_HI, _P_LO, _P_FACE_TOP, _P_FACE_BOT,
                   _P_FACE_REC, glyph_key, _P_GLY, _P_GLY_SH)
    _hairlines(surf, cx, cy, R, _P_MID, _P_LO, _P_MID, broken=True)


# ═══════════════════════════════════════════════════════════════════════════
# 4) SOLITAIRE — a slim band set with four small spaced gems.
#    Fame: four tiny bezel-set ice-blue brilliants at the cardinals on a thin
#    gold band, each with a bright upper-left glint; the band between is bare and
#    calm. Shame: the SAME stones clouded to milky grey, glints dead, and one
#    prised OUT to leave an empty dark bezel socket; band tarnished.
# ═══════════════════════════════════════════════════════════════════════════
_SOL_TABLE = (226, 240, 255)
_SOL_MID   = (150, 196, 244)
_SOL_DK    = ( 78, 128, 190)
_SOL_GLINT = (255, 255, 255)
_SD_TABLE  = (158, 160, 168)   # clouded milky stone
_SD_MID    = (120, 122, 130)
_SD_DK     = ( 78,  80,  88)


def _solitaire(surf, cx, cy, gr, bez_hi, bez_lo, table, mid, dk,
               glint=None, empty=False):
    """A tiny bezel-set stone: a gold rub-over bezel ring, then a small faceted
    brilliant (octagon girdle + kite facets + table). ``empty`` leaves the bezel
    holding a dark socket."""
    pygame.draw.circle(surf, bez_lo, (cx, cy), int(gr * 1.32))
    pygame.draw.circle(surf, bez_hi, (cx, cy), int(gr * 1.32), max(1, gr // 4))
    if empty:
        pygame.draw.circle(surf, (12, 12, 18), (cx, cy), int(gr * 1.0))
        pygame.draw.arc(surf, bez_lo, (cx - gr, cy - gr, gr * 2, gr * 2),
                        math.radians(200), math.radians(340), max(1, gr // 3))
        return
    verts = [(cx + math.cos(i / 8 * math.tau - math.pi / 8) * gr,
              cy + math.sin(i / 8 * math.tau - math.pi / 8) * gr) for i in range(8)]
    pygame.draw.polygon(surf, mid, [(int(x), int(y)) for x, y in verts])
    tv = [(cx + (x - cx) * 0.46, cy + (y - cy) * 0.46) for x, y in verts]
    for i in range(8):
        j = (i + 1) % 8
        shade = table if i % 2 == 0 else dk
        pygame.draw.polygon(surf, shade, [
            (int(verts[i][0]), int(verts[i][1])),
            (int(verts[j][0]), int(verts[j][1])),
            (int(tv[j][0]), int(tv[j][1])),
            (int(tv[i][0]), int(tv[i][1]))])
    pygame.draw.polygon(surf, table, [(int(x), int(y)) for x, y in tv])
    if glint is not None:
        pygame.draw.circle(surf, glint,
                           (int(cx - gr * 0.28), int(cy - gr * 0.28)),
                           max(1, gr // 3))


def _solitaire_ring(surf, cx, cy, R, bez_hi, bez_lo, palette, wrecked=False):
    table, mid, dk = palette
    rc = R * _ORN_R
    gr = int(R * 0.085)
    empty_idx = 1 if wrecked else -1
    for k in range(4):
        a = k * math.pi / 2 - math.pi / 2
        gx = int(cx + math.cos(a) * rc)
        gy = int(cy + math.sin(a) * rc)
        _solitaire(surf, gx, gy, gr, bez_hi, bez_lo, table, mid, dk,
                   glint=None if wrecked else _SOL_GLINT,
                   empty=(k == empty_idx))


def fame_solitaire(surf, cx, cy, R, glyph_key):
    _slim_band(surf, cx, cy, R, _G_HI, _G_MID, _G_LO, spec=_G_SPEC, edge=_G_EDGE)
    _finish_center(surf, cx, cy, R, _G_HI, _G_LO, _FACE_TOP, _FACE_BOT, _FACE_REC,
                   glyph_key, _GLY, _GLY_SH, ai._GLYPH_SHEEN)
    _solitaire_ring(surf, cx, cy, R, _G_HI, _G_LO, (_SOL_TABLE, _SOL_MID, _SOL_DK))


def shame_solitaire(surf, cx, cy, R, glyph_key):
    _slim_band(surf, cx, cy, R, _P_HI, _P_MID, _P_LO, spec=None, edge=_P_EDGE)
    _tarnish_creep(surf, cx, cy, R, seed=61)
    _finish_center(surf, cx, cy, R, _P_HI, _P_LO, _P_FACE_TOP, _P_FACE_BOT,
                   _P_FACE_REC, glyph_key, _P_GLY, _P_GLY_SH)
    _solitaire_ring(surf, cx, cy, R, _P_MID, _P_LO, (_SD_TABLE, _SD_MID, _SD_DK),
                    wrecked=True)


# ═══════════════════════════════════════════════════════════════════════════
# 5) HALO — a soft luminous thin light rim.
#    Fame: a fine bright rim of light — a crisp white-gold hairline over a soft
#    warm glow, with a few faint radiant ticks — so the medal seems to give off
#    a delicate halo. Shame: the SAME rim EXTINGUISHED — the glow gone, the line
#    guttered to a dim, uneven, broken remnant flickering out (segments faded).
# ═══════════════════════════════════════════════════════════════════════════
_HL_GLOW = (255, 214, 120)
_HL_LINE = (255, 248, 214)
_HL_SOFT = (255, 230, 170)
_HD_LINE = ( 96, 100, 116)   # a cold, dim guttered remnant
_HD_FAINT = ( 60,  64,  78)


def _halo_ring(surf, cx, cy, R, line, soft, glow=None, ticks_col=None,
               broken=False):
    rc = R * 0.86
    if glow is not None:
        blit_glow(surf, cx, cy, int(R * 1.28), glow, 90)
    if broken:
        # a dim line guttering out: uneven dashes at low, varying alpha
        seg = 46
        for k in range(seg):
            a0 = k / seg * math.tau
            a1 = (k + 1) / seg * math.tau
            amid = (a0 + a1) / 2
            fade = (math.sin(k * 2.3) + 1) * 0.5    # deterministic flicker
            if fade < 0.42 or k % 4 == 0:           # whole stretches gone dark
                continue
            rect = pygame.Rect(int(cx - rc), int(cy - rc), int(rc * 2), int(rc * 2))
            col = lerp_color(_HD_FAINT, line, fade)
            pygame.draw.arc(surf, col, rect, -a1, -a0, max(1, R // 26))
        return
    # a soft under-halo line then a crisp bright hairline crest
    pygame.draw.circle(surf, soft, (cx, cy), int(rc), max(2, R // 16))
    pygame.draw.circle(surf, line, (cx, cy), int(rc), max(1, R // 34))
    if ticks_col is not None:
        for k in range(24):
            a = k / 24 * math.tau
            r0 = rc + R * 0.02
            r1 = rc + R * 0.075
            pygame.draw.line(surf, ticks_col,
                             (int(cx + math.cos(a) * r0), int(cy + math.sin(a) * r0)),
                             (int(cx + math.cos(a) * r1), int(cy + math.sin(a) * r1)),
                             max(1, R // 60))


def fame_halo(surf, cx, cy, R, glyph_key):
    blit_glow(surf, cx, cy, int(R * 1.24), _HL_GLOW, 90)   # soft halo, behind all
    _slim_band(surf, cx, cy, R, _G_HI, _G_MID, _G_LO, spec=_G_SPEC, edge=_G_EDGE)
    _finish_center(surf, cx, cy, R, _G_HI, _G_LO, _FACE_TOP, _FACE_BOT, _FACE_REC,
                   glyph_key, _GLY, _GLY_SH, ai._GLYPH_SHEEN)
    _halo_ring(surf, cx, cy, R, _HL_LINE, _HL_SOFT, glow=None, ticks_col=_HL_SOFT)


def shame_halo(surf, cx, cy, R, glyph_key):
    _slim_band(surf, cx, cy, R, _P_HI, _P_MID, _P_LO, spec=None, edge=_P_EDGE)
    _tarnish_creep(surf, cx, cy, R, seed=83)
    _finish_center(surf, cx, cy, R, _P_HI, _P_LO, _P_FACE_TOP, _P_FACE_BOT,
                   _P_FACE_REC, glyph_key, _P_GLY, _P_GLY_SH)
    _halo_ring(surf, cx, cy, R, _HD_LINE, _HD_FAINT, glow=None, broken=True)


# Each concept pairs a Fame composer with its slim degraded Shame twin.
CONCEPTS = [
    ("filigree", fame_filigree, shame_filigree),
    ("pearls", fame_pearls, shame_pearls),
    ("hairline", fame_hairline, shame_hairline),
    ("solitaire", fame_solitaire, shame_solitaire),
    ("halo", fame_halo, shame_halo),
]
