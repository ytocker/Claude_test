"""SCALLOP-NEGATIVE PENNANT — awning-themed sign concept for the hub stalls.

Thesis: INVERT the awning. The awning above the goods is cream-and-red striped
with scalloped voids cut UP into it; the sign is the negative of that — a solid
oxblood field whose cream hem lobes DOWN, each lobe centred on an awning stripe
boundary so the two hems interlock like a tongue-and-groove joint. The sign
therefore reads as the same bolt of cloth as the awning, cut the other way
round, instead of as a board that happens to hang above it.

Sign hook only: the per-stall ITEM presentation stays exactly as the chosen
mix-C assignment renders it, so this concept is judged on the sign alone.
Concept module for the design loop — it installs into the store_hub hook seam
and never edits the stall architecture.
"""
import math

import pygame

import game.store_hub as sh
from game.store_hub import (m, font, lerp_color, gradient_text, vgrad,
                            WOOD_HI, WOOD_MID, WOOD_LO, WOOD_EDGE,
                            AWN_RED, AWN_CREAM, AWN_CREAM_D,
                            GOLD_A_TOP, GOLD_A_BOT, LABEL_KEY)
# The rigging vocabulary is shared with the pennant base on purpose: cord and
# lashing are the same material across every cloth sign in the market.
from tools.stall_variant_sailcloth_pennant import _rope_run, _lashing

# Field ramp. Two full steps DOWN from the awning's red so the sign can never
# out-value the goods, and dark enough that GOLD_A ink clears 2.3:1 on it.
CLOTH_HI = (92, 28, 30)
CLOTH_LO = (58, 18, 18)
# The lobe's outer arc is the whole silhouette against lit thatch, so it gets a
# dedicated ink one step below the field rather than borrowing AWN_RED_D.
HEM_KEY = (74, 22, 24)

INK_TOP = GOLD_A_TOP
INK_BOT = GOLD_A_BOT

# --- shared frame, in logical px above body_top (h grows upward) --------------
SPAR_H = 18.0
SPAR_T = 2.5
SPAR_HALF = 36.0
SLEEVE_H = 17.0        # visible top fold; the FILL runs 0.5 higher, under the spar
SLEEVE_SAG = 1.5
FILL_TOP_H = 17.5
CAP_TOP_H = 14.5
CAP_BOT_H = 6.5
HEM_H = 3.0            # trailing hem line: the cusp level of the lobed edge
HEM_BAND = 2.0
LOBE_DEEP = 2.5        # cusp h=3 -> apex h=0.5, the full ornament spend downward
LOBE_PITCH = 12.5
FLARE_HALF = 42.0      # the hem is wider than its spar: a gathered, flared valance

# The awning's stripe grid is asymmetric about cx (its stripes are laid from the
# left eave, not from the centre). Lobes are centred on the stripe BOUNDARIES and
# cusps land on the stripe MIDPOINTS, so the sign hem and the awning scallops
# interlock. Never centre-symmetrise these — that breaks the interlock.
LOBE_CENTRES = (-33.0, -20.5, -8.0, 4.5, 17.0, 29.5)
CUSPS = (-42.0, -39.25, -26.75, -14.25, -1.75, 10.75, 23.25, 35.75, 42.0)


def _arc_h(x):
    """Height of the lobed outer edge at logical offset x from cx.

    Each span between cusps carries one half-sine lobe. The two end spans are
    short leftovers of the stripe grid and are unequal by construction, so their
    depth scales with their width — a stubby end lobe kept at full depth would
    read as a torn corner rather than as the last scallop in the run."""
    for a, b in zip(CUSPS[:-1], CUSPS[1:]):
        if a <= x <= b:
            u = (x - a) / (b - a)
            d = LOBE_DEEP * min(1.0, (b - a) / LOBE_PITCH)
            return HEM_H - d * math.sin(math.pi * u)
    return HEM_H


def _fill_poly(surf, pts, top, bot, sheen=0):
    """Fill a polygon with a vertical ramp built on the polygon's own bbox, plus
    an optional up-left key wash so a broad flat field still turns in the light."""
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0, y0 = int(min(xs)) - 1, int(min(ys)) - 1
    w = max(1, int(max(xs)) - x0 + 2)
    h = max(1, int(max(ys)) - y0 + 2)
    body = vgrad(w, h, 0, top, bot)
    if sheen:
        wash = pygame.Surface((w, h), pygame.SRCALPHA)
        for i in range(w):
            a = int(sheen * max(0.0, 1.0 - i / (w * 0.62)) ** 1.5)
            if a > 0:
                pygame.draw.line(wash, (255, 206, 168, a), (i, 0), (i, h))
        body.blit(wash, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255),
                        [(p[0] - x0, p[1] - y0) for p in pts])
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(body, (x0, y0))


def sign_hook(surf, ctx):
    cx = ctx["cx"]
    body_top = ctx["body_top"]
    scale = ctx["scale"]
    half_w, eave = ctx["half_w"], ctx["eave"]
    apex_y = ctx["roof_apex_y"]
    label = ctx["label"]

    limit = half_w + eave
    # Sub-logical detail (a 0.5 px lobe apex, a 1.5 px rim) has to survive the
    # frame maths, so geometry is carried in float device px and only rounded
    # by the rasteriser.
    unit = m(1) * scale

    def X(v):
        return cx + v * unit

    def Y(h):
        return body_top - h * unit

    # ---- the lobed hem, sampled dense enough that the arcs stay arcs at SS.
    arc = []
    for a, b in zip(CUSPS[:-1], CUSPS[1:]):
        n = max(6, int((b - a) * 1.6))
        for i in range(n + 1):
            if i == 0 and arc:
                continue
            x = a + (b - a) * i / n
            arc.append((x, _arc_h(x)))
    arc_pts = [(X(x), Y(h)) for x, h in arc]
    field_bot = [(X(x), Y(h + HEM_BAND)) for x, h in arc]

    field = ([(X(-SPAR_HALF), Y(FILL_TOP_H)), (X(SPAR_HALF), Y(FILL_TOP_H))]
             + field_bot[::-1])

    # ---- cast onto the thatch, clipped to the roof triangle so the shadow can
    # never leak into open sky past the rake.
    seam_stop = body_top - max(2, int(m(1.5) * scale))
    roof = [(cx - limit, seam_stop), (cx + limit, seam_stop), (cx, apex_y)]
    sx, sy = max(1, int(m(2.0) * scale)), max(1, int(m(3.0) * scale))
    shp = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(shp, (18, 10, 6, 96), [(x + sx, y + sy) for x, y in field])
    rmask = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(rmask, (255, 255, 255, 255), roof)
    shp.blit(rmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(shp, (0, 0))

    # ---- spar first: the cloth's sleeve has to swallow it the way a real
    # sleeve swallows its pole, so it is laid down before the fill.
    spar_y = Y(SPAR_H)
    spar_t = max(2, int(SPAR_T * unit))
    sl, sr = X(-SPAR_HALF), X(SPAR_HALF)
    pygame.draw.line(surf, WOOD_LO, (sl, spar_y + spar_t * 0.5),
                     (sr, spar_y + spar_t * 0.5), spar_t)
    pygame.draw.line(surf, WOOD_MID, (sl, spar_y), (sr, spar_y), spar_t)
    pygame.draw.line(surf, WOOD_HI, (sl, spar_y - spar_t * 0.34),
                     (sr, spar_y - spar_t * 0.34), max(1, int(spar_t * 0.42)))
    for s in (-1, 1):
        nx = X(s * SPAR_HALF * 0.58)
        pygame.draw.line(surf, WOOD_LO, (nx, spar_y - spar_t),
                         (nx, spar_y + spar_t), max(1, int(unit)))
        pygame.draw.circle(surf, WOOD_EDGE, (int(X(s * SPAR_HALF)), int(spar_y)),
                           max(1, int(spar_t * 0.7)))

    _fill_poly(surf, field, CLOTH_HI, CLOTH_LO, sheen=26)

    # ---- the sleeve fold. Only the free top EDGE sags; the fill above it stays
    # flat, or a gap of sky opens between spar and cloth at mid-span and the
    # pennant reads as unhooked.
    fold = []
    for i in range(41):
        u = i / 40.0
        fold.append((X(-SPAR_HALF + 2 * SPAR_HALF * u),
                     Y(SLEEVE_H - SLEEVE_SAG * math.sin(math.pi * u))))
    pygame.draw.lines(surf, lerp_color(CLOTH_LO, (0, 0, 0), 0.45), False,
                      [(x, y + unit * 0.7) for x, y in fold],
                      max(1, int(unit * 0.9)))
    pygame.draw.lines(surf, AWN_RED, False, fold, max(1, int(unit * 0.55)))

    # ---- the cream hem. Three runs instead of one bbox ramp: the band wanders
    # 2.5 px vertically, so a bbox gradient would light it by lobe position
    # rather than across its own width.
    def band(off_lo, off_hi, col):
        poly = ([(x, y - off_lo * unit) for x, y in arc_pts]
                + [(x, y - off_hi * unit) for x, y in arc_pts][::-1])
        pygame.draw.polygon(surf, col, poly)

    band(0.0, HEM_BAND, AWN_CREAM_D)
    band(0.72, HEM_BAND, lerp_color(AWN_CREAM, AWN_CREAM_D, 0.40))
    band(1.30, HEM_BAND, AWN_CREAM)

    # The outer arc is THE silhouette pixel of the whole sign, so it is inked
    # flush-inside rather than centred: the keyline's outer edge IS the hem,
    # and nothing of the sign reaches below it toward the awning seam.
    kw = max(2, int(round(unit)))
    pygame.draw.lines(surf, HEM_KEY, False,
                      [(x, y - kw * 0.5) for x, y in arc_pts], kw)

    for c in CUSPS[1:-1]:
        pygame.draw.circle(surf, AWN_RED,
                           (int(X(c)), int(Y(HEM_H + HEM_BAND * 0.5))),
                           max(1, int(unit * 0.6)))

    # ---- lashings. The spar tips land all but flush with the thatch rake, so
    # the only tie-able crossing IS the tip: clamp inboard of it rather than
    # letting the wrap hang off the end of the spar.
    rake = limit * (spar_y - apex_y) / max(1.0, float(body_top - apex_y))
    lash = min(rake, (SPAR_HALF - 2.5) * unit)
    for s in (-1, 1):
        # Wraps hug the spar rather than standing proud of it: the h=20 ceiling
        # is only 1.25 px clear of the spar's own top edge.
        _lashing(surf, cx + s * lash, spar_y, max(2, int(unit * 2.6)),
                 spar_t * 0.58, 3, max(2, int(unit * 1.2)))

    # Corner ties run DOWN THE FACE of the dark field, where bleached cord
    # actually reads; run outside the flare they would sit pale-on-pale against
    # the lit thatch and vanish.
    for s in (-1, 1):
        _rope_run(surf, [(X(s * SPAR_HALF), Y(SPAR_H - 0.4)),
                         (X(s * 36.4), Y(14.5)), (X(s * 37.0), Y(11.2))],
                  max(2, int(unit * 1.2)), twist=False)

    # ---- type on the cap band: h=14.5 -> 6.5, 1.5 of clear field to the sleeve
    # fold above and to the cream hem below. gradient_text centres the glyph BOX
    # and caps sit high inside it, so re-centre on the INK or the wordmark floats
    # off the band it is supposed to sit on.
    f = font(11 * scale)
    base = sh._glyph_base(label, f, m(0.6))
    bb = base.get_bounding_rect()
    cy = int(round((Y(CAP_TOP_H) + Y(CAP_BOT_H)) * 0.5
                   + base.get_height() * 0.5 - bb.centery))
    gradient_text(surf, label, f, (cx, cy), INK_TOP, INK_BOT,
                  weight=m(1.0 * scale), keyline=LABEL_KEY, kw=max(1, m(1.0)),
                  shadow=False, tracking=m(0.6))


def install():
    # The chosen mix binds the per-stall ITEM hooks (and its own signs); this
    # concept then claims the sign seam alone, so the item read is held constant
    # across every sign theme under review.
    from tools import stall_variant_mixed
    stall_variant_mixed.install()
    sh.STALL_SIGN_HOOK = sign_hook
