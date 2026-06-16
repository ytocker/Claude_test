"""Look-dev sheet for the Skybit BOSS — "HAMAGURI-SHINKIROU"
(Umibozu-versions set, concept #4) — mirage clam, mouth of a drowned city.

A serene old hamaguri clam sits gaping on its hinge and softly HUMS a whole
ghost-city out of its mouth. The exhaled drowned-city is a translucent
pagoda-tower of pearl-green mirage light, threaded with tiny drowned souls.
Cuted to the Umibozu lineage: NOT a bodiless head — the creature IS the wide
gaping clam, and the exhaled mirage-TOWER is what becomes the pillar.

KIND lock (cross-set pin): this is the ONLY HORIZONTAL-GRIN silhouette in the
roster. The whole distinctness is the wide horizontal split of the two shell
halves — a long sideways grin gaping open to the right. The shell halves must
NOT round up into a vertical blob; the silhouette stays a flat, wide oval cut
across the middle.

House style this obeys (the elevated Umibozu "epic" grammar):
  - CHIBI proportions — one oversized rounded subject; serene scary-CUTE.
  - FLAT saturated fills + a hard 1-2px ink keyline (28,22,30). No within-shape
    gradients, no soft/feathered edges, no bevels.
  - Form via the TRIAD: dark-core ring -> flat fill -> top-left rim sheen.
  - Silhouette POP via a 1px ink keyline grown from the alpha mask.
  - EPIC pass: render BIG at SS, then smoothscale down for a crisp downscale.

Palette read (pinned): BROWN-WARM sea-rust shell, NEVER teal. Pearl-cream
sheen. The mirage glow is the PALER / greyer pearl-GREEN (pinned apart from
sibling Tehom's deeper, sourer embryo-green). Shell relief = bold RADIATING
fan-ribs (distinct from Tehom's continuous spiral whorl).

Prop -> pillar mirror: the exhaled mirage-TOWER is the pillar. A translucent
pearl-green pagoda SHAFT tiles one pagoda TIER per repeat (a stack of
balcony-and-roof storeys, faintly haunted with souls) = the repeatable PILLAR
BODY; a single mirage-pagoda ROOF FINIAL (~shaft+30%) = the detachable GAP-EDGE
CAP glowing pearl-green at the gap. Naturally vertical + symmetric — clean
mirror, no top-heavy cap.

    SDL_VIDEODRIVER=dummy PYTHONPATH=/home/user/skybit python \
        docs/skybit_devil/batch2/umibozu_versions/hamaguri/render_hamaguri.py
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.draw import _shade_c, lerp_color, make_glow_surface
from game.config import PIPE_W


pygame.init()

# ── PINNED PALETTE (hamaguri-shinkirou) ──────────────────────────────────────
# Sea-rust shell — a warm sandy brown. The whole accessibility tell is that the
# SHELL reads brown-warm (never teal), while the exhaled mirage reads cool pale
# pearl-GREEN. The warm shell vs cool mirage value/hue split carries the read.
SHELL       = (178, 142, 96)    # sea-rust shell fill (warm sandy brown)
SHELL_DK    = (120, 86, 52)     # umber-shell shade (dark-core ring / rib hollows)
SHELL_DEEP  = (84, 58, 34)      # deepest umber (the gape interior / hinge well)
PEARL       = (236, 224, 196)   # pearl-cream sheen (top-left lit rim + inner lip)
PEARL_DK    = (198, 182, 150)   # cream shade for the lip seat

# Ghost pearl-GREEN mirage — the PALER / greyer green, pinned apart from Tehom's
# deeper sourer embryo-green. This is the only cool focal; it lanterns the city.
MIRAGE      = (170, 222, 186)   # ghost pearl-green mirage glow (pale, greyed)
MIRAGE_DK   = (112, 162, 134)   # mirage shade (tower facets / dark-core)
MIRAGE_LT   = (212, 244, 222)   # hot mirage core (finial pip / soul sparks)

HINGE_EYE   = (60, 72, 74)      # slate hinge-eyes (cool dark, at the shell hinge)
INK         = (28, 26, 24)      # the house keyline (warm-neutral ink)
FACE_INK    = (40, 38, 34)      # face marks in a warm near-ink

# Night keyline: a lifted pearl-cream rim so the brown shell edge survives on a
# midnight sky (dark ink would vanish there); grown 2px so the wide grin
# silhouette reads on SHAPE, not on the mirage glow alone.
INK_NIGHT   = (232, 222, 198)


def _add_outline(src, outline_color=(*INK, 235), width=1):
    """Grow a keyline from the alpha mask so the silhouette POPS on any sky (the
    parrot `_add_outline` recipe). On night the keyline is a lifted pearl-cream
    tone, grown thicker, so the wide clam edge survives on dark sky by SHAPE."""
    w, h = src.get_size()
    pad = width + 1
    out = pygame.Surface((w + pad * 2, h + pad * 2), pygame.SRCALPHA)
    mask = pygame.mask.from_surface(src, threshold=8)
    sil = mask.to_surface(setcolor=outline_color, unsetcolor=(0, 0, 0, 0))
    offs = [(dx, dy) for dx in range(-width, width + 1)
            for dy in range(-width, width + 1) if (dx, dy) != (0, 0)]
    for dx, dy in offs:
        out.blit(sil, (pad + dx, pad + dy))
    out.blit(src, (pad, pad))
    return out


def _soul_spark(surf, cx, cy, r, ss, *, night=False, core=True):
    """A tiny drowned-SOUL spark inside the mirage — a contained pearl-green
    point-glow + a flat mint disc + (optionally) a hot mint core. Kept small +
    discrete so the souls read as a haunted dusting, never a bright wash."""
    gr = int(r * (3.0 if night else 2.2))
    gl = make_glow_surface(max(1, gr), MIRAGE, alpha_center=170 if night else 110,
                           falloff=2.0)
    surf.blit(gl, (int(cx - gr), int(cy - gr)), special_flags=pygame.BLEND_ADD)
    pygame.draw.circle(surf, MIRAGE_DK, (int(cx), int(cy)), max(1, int(r)))
    pygame.draw.circle(surf, MIRAGE, (int(cx), int(cy)), max(1, int(r * 0.74)))
    if core:
        pygame.draw.circle(surf, MIRAGE_LT, (int(cx), int(cy)), max(1, int(r * 0.34)))


# ── one radiating fan-rib (the shell relief tell) ────────────────────────────

def _fan_ribs(surf, hinge_x, hinge_y, r, ss, *, up, col, n=7,
              ang0=None, ang1=None):
    """Bold RADIATING fan-ribs fanning out from the shell HINGE — the locked
    relief tell (distinct from Tehom's continuous spiral whorl). Each rib is a
    tapering umber groove that radiates from the hinge to the shell rim, so the
    eye reads a clean fan, not a spiral. `up` selects the upper vs lower half so
    the two halves fan away from the horizontal split."""
    d = -1 if up else 1
    # The ribs sweep across the half-shell's angular span. Hinge is on the LEFT,
    # the gape opens RIGHT — so ribs fan from the back-left across to the lip.
    a0 = math.radians(8) if ang0 is None else ang0
    a1 = math.radians(150) if ang1 is None else ang1
    for i in range(n):
        t = i / (n - 1)
        a = a0 + (a1 - a0) * t
        # A rib is a thin wedge from a point near the hinge out to the rim.
        ox = hinge_x + math.cos(a) * r * 0.18
        oy = hinge_y + d * math.sin(a) * r * 0.14
        rx = hinge_x + math.cos(a) * r * 1.02
        ry = hinge_y + d * math.sin(a) * r * 0.78
        gw = max(1, int(r * 0.05 * ss / ss))
        pygame.draw.line(surf, _shade_c(col, -34), (int(ox), int(oy)),
                         (int(rx), int(ry)), max(2, int(2.2 * ss)))
    # A bright pearl-cream catch-light rib pair on the top-left lit ribs.
    if up:
        for i in (1, 2):
            t = i / (n - 1)
            a = a0 + (a1 - a0) * t
            ox = hinge_x + math.cos(a) * r * 0.34
            oy = hinge_y + d * math.sin(a) * r * 0.20
            rx = hinge_x + math.cos(a) * r * 0.92
            ry = hinge_y + d * math.sin(a) * r * 0.70
            pygame.draw.line(surf, _shade_c(PEARL, -6), (int(ox), int(oy)),
                             (int(rx), int(ry)), max(1, int(1.0 * ss)))


def _shell_half(surf, hinge_x, hinge_y, r, ss, *, up, night=False):
    """ONE flat-triad shell half — a wide, low, horizontally-stretched half-shell
    hinged on the LEFT and gaping toward the RIGHT. Deliberately wide + flat
    (the half is ~1.9x as wide as it is tall) so the assembled clam keeps the
    long HORIZONTAL grin and never rounds into a vertical blob. Dark-core ->
    flat fill -> top-left pearl rim-sheen, then the radiating fan-ribs."""
    d = -1 if up else 1
    col = _shade_c(SHELL, 10) if night else SHELL
    # The half-shell as a wide low ellipse, sitting above/below the split line.
    # Center is pushed toward the hinge so the gape opens to the right.
    hw = r * 1.10            # horizontal half-width (wide)
    hh = r * 0.58            # vertical half-height (low -> flat grin)
    cx_e = hinge_x + hw * 0.62
    cy_e = hinge_y + d * hh * 0.58
    rect = pygame.Rect(0, 0, int(hw * 2), int(hh * 2))
    rect.center = (int(cx_e), int(cy_e))
    # Dark-core ring.
    pygame.draw.ellipse(surf, _shade_c(col, -32), rect)
    pygame.draw.ellipse(surf, col, rect.inflate(-int(hw * 0.10), -int(hh * 0.12)))

    # Clip the half to its side of the split so the two halves meet on a clean
    # horizontal line (the GRIN). Re-fill the wrong side with transparent by
    # painting the split band — instead we simply draw a deep-umber gape wedge
    # over the inner mouth so the lip reads open.
    _fan_ribs(surf, hinge_x, hinge_y, r, ss, up=up, col=col)

    # Pearl-cream inner LIP along the split edge — a flat bright band so the
    # gaping mouth reads, the clam's lit lip. Drawn on the gape-facing rim.
    lip_y = hinge_y + d * hh * 0.06
    lpts = []
    steps = 18
    for i in range(steps + 1):
        t = i / steps
        lx = hinge_x + t * hw * 1.55
        # The lip bows gently away from the split toward the rim.
        ly = lip_y + d * math.sin(t * math.pi) * hh * 0.10
        lpts.append((int(lx), int(ly)))
    pygame.draw.lines(surf, PEARL, False, lpts, max(2, int(2.2 * ss)))
    pygame.draw.lines(surf, PEARL_DK, False,
                      [(x, y + d * max(1, int(1.4 * ss))) for x, y in lpts],
                      max(1, int(1.2 * ss)))

    # Top-left pearl rim-sheen lobe — only on the UPPER half's pate (the lit
    # side). A single crisp crescent: lit disc minus a body-color bite.
    if up:
        sx = cx_e - hw * 0.34
        sy = cy_e - hh * 0.40
        sr = hh * 0.46
        pygame.draw.circle(surf, PEARL, (int(sx), int(sy)), max(2, int(sr)))
        pygame.draw.circle(surf, col,
                           (int(sx + sr * 0.46), int(sy + sr * 0.50)),
                           max(2, int(sr * 0.84)))


# ── one mirage pagoda tier (city storey + soul motes) ────────────────────────

def _pagoda_tier(surf, cx, cy, tw, th, ss, *, night=False, souls=True,
                 facets=True):
    """ONE translucent mirage-pagoda STOREY — a flat pearl-green body block with a
    sweeping upturned roof on top, a thin balcony lip below the roof, and a few
    drowned-soul motes in the window band. This is the repeatable PILLAR TIER:
    storeys stack body-to-roof up the shaft. Drawn translucent (low-alpha mirage
    fills) so the exhaled city reads as ghost-light, not solid masonry."""
    # Translucent storey BODY block (a flat, slightly trapezoidal wall).
    body_top = cy - th * 0.18
    body_bot = cy + th * 0.50
    wall_hw_t = tw * 0.40
    wall_hw_b = tw * 0.46
    wall = [
        (cx - wall_hw_t, body_top), (cx + wall_hw_t, body_top),
        (cx + wall_hw_b, body_bot), (cx - wall_hw_b, body_bot),
    ]
    body_a = 150 if night else 120
    _poly_a(surf, [(int(x), int(y)) for x, y in wall],
            (*MIRAGE_DK, body_a))
    # Lit inner wall panel.
    inset = [
        (cx - wall_hw_t * 0.74, body_top + th * 0.06),
        (cx + wall_hw_t * 0.74, body_top + th * 0.06),
        (cx + wall_hw_b * 0.74, body_bot - th * 0.04),
        (cx - wall_hw_b * 0.74, body_bot - th * 0.04),
    ]
    _poly_a(surf, [(int(x), int(y)) for x, y in inset],
            (*MIRAGE, body_a + 30))
    # Faint vertical window mullions so the storey reads as a building facet.
    if facets:
        for fxi in (-0.5, 0.0, 0.5):
            mx = cx + fxi * tw * 0.5
            _line_a(surf, (int(mx), int(body_top + th * 0.08)),
                    (int(mx), int(body_bot - th * 0.06)),
                    (*MIRAGE_DK, 150), max(1, int(1.2 * ss)))

    # Sweeping upturned PAGODA ROOF — a wide low chevron with curled eaves, the
    # storey crown that gives the tower its city-skyline read.
    roof_y = body_top
    eave_hw = tw * 0.62
    ridge = th * 0.34
    roof = [
        (cx - eave_hw, roof_y),
        (cx - eave_hw * 0.42, roof_y - ridge * 0.62),
        (cx, roof_y - ridge),
        (cx + eave_hw * 0.42, roof_y - ridge * 0.62),
        (cx + eave_hw, roof_y),
        (cx + eave_hw * 0.70, roof_y + ridge * 0.18),
        (cx - eave_hw * 0.70, roof_y + ridge * 0.18),
    ]
    _poly_a(surf, [(int(x), int(y)) for x, y in roof], (*MIRAGE_DK, body_a + 20))
    # Lit roof slope (top-left catch).
    lit = [
        (cx - eave_hw * 0.86, roof_y - ridge * 0.04),
        (cx, roof_y - ridge * 0.92),
        (cx - eave_hw * 0.10, roof_y - ridge * 0.16),
    ]
    _poly_a(surf, [(int(x), int(y)) for x, y in lit], (*MIRAGE_LT, body_a))
    # Thin balcony lip under the roof eaves.
    _line_a(surf, (int(cx - eave_hw * 0.84), int(roof_y + ridge * 0.20)),
            (int(cx + eave_hw * 0.84), int(roof_y + ridge * 0.20)),
            (*MIRAGE_LT, 180), max(1, int(1.4 * ss)))

    # Drowned-soul motes in the window band — a sparse haunted dusting.
    if souls:
        for sxi in (-0.36, 0.0, 0.36):
            _soul_spark(surf, cx + sxi * tw * 0.5, cy + th * 0.22,
                        max(2, tw * 0.05), ss, night=night,
                        core=(sxi == 0.0))


def _poly_a(surf, pts, rgba):
    """Alpha polygon helper — paints a translucent shape onto its own scratch
    surface then blits, so the mirage city layers as ghost-light."""
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0, y0 = min(xs), min(ys)
    w = max(1, max(xs) - x0 + 2)
    h = max(1, max(ys) - y0 + 2)
    tmp = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(tmp, rgba, [(x - x0, y - y0) for x, y in pts])
    surf.blit(tmp, (x0, y0))


def _line_a(surf, p0, p1, rgba, width):
    x0 = min(p0[0], p1[0]) - width - 1
    y0 = min(p0[1], p1[1]) - width - 1
    w = abs(p1[0] - p0[0]) + 2 * width + 2
    h = abs(p1[1] - p0[1]) + 2 * width + 2
    tmp = pygame.Surface((max(1, w), max(1, h)), pygame.SRCALPHA)
    pygame.draw.line(tmp, rgba, (p0[0] - x0, p0[1] - y0),
                     (p1[0] - x0, p1[1] - y0), width)
    surf.blit(tmp, (x0, y0))


# ── the mirage-city THREAD rising from the clam mouth (hero) ──────────────────

def _mirage_thread(surf, base_x, base_y, height, ss, *, night=False, tiers=3):
    """The thin exhaled drowned-city THREAD — a slender stack of mirage-pagoda
    tiers shrinking as it rises out of the gape, capped by a tiny finial pip.
    Narrow on the hero so it reads as a humming wisp, not the full pillar."""
    # A faint vertical mirage haze column behind the city so it reads exhaled.
    haze_w = int(height * 0.16)
    gl = make_glow_surface(haze_w, MIRAGE, alpha_center=70 if night else 46,
                           falloff=1.6)
    for k in range(tiers + 1):
        yy = base_y - height * (k / (tiers + 0.5))
        surf.blit(gl, (int(base_x - haze_w), int(yy - haze_w)),
                  special_flags=pygame.BLEND_ADD)

    for k in range(tiers):
        t = k / max(1, tiers - 1)
        yy = base_y - height * (0.16 + 0.74 * t)
        tw = (1.0 - 0.46 * t) * height * 0.30
        th = (1.0 - 0.40 * t) * height * 0.24
        _pagoda_tier(surf, base_x, yy, tw, th, ss, night=night,
                     souls=True, facets=True)
    # Finial pip crowning the thread.
    _soul_spark(surf, base_x, base_y - height * 0.96,
                max(2, height * 0.04), ss, night=night, core=True)


# ── the serene old clam head/body ─────────────────────────────────────────────

def _clam(surf, hinge_x, hinge_y, r, ss, *, night=False, tell=False):
    """The serene old hamaguri: two wide flat shell halves hinged on the LEFT,
    gaping open to the RIGHT, with the slate hinge-EYES at the back hinge and a
    deep-umber gape interior between the halves. The whole thing is a long
    HORIZONTAL grin — wide + low. `tell` bakes a bolder low-res read for 32px."""
    # Deep-umber gape interior FIRST so the open mouth sits behind the lips.
    gape = pygame.Rect(0, 0, int(r * 1.9), int(r * 0.62))
    gape.center = (int(hinge_x + r * 0.74), int(hinge_y))
    pygame.draw.ellipse(surf, SHELL_DEEP, gape)
    pygame.draw.ellipse(surf, _shade_c(SHELL_DEEP, -14),
                        gape.inflate(-int(r * 0.5), -int(r * 0.14)))

    # The exhaled mirage-city thread rises FROM the gape (drawn before the upper
    # shell so the upper lip overlaps its root — humming it out of the mouth).
    _mirage_thread(surf, hinge_x + r * 0.78, hinge_y - r * 0.06,
                   r * (1.5 if tell else 2.05), ss, night=night,
                   tiers=2 if tell else 3)

    # Lower shell half (drawn first; upper half overlaps at the hinge).
    _shell_half(surf, hinge_x, hinge_y, r, ss, up=False, night=night)
    # Upper shell half.
    _shell_half(surf, hinge_x, hinge_y, r, ss, up=True, night=night)

    # The umbo / hinge knuckle at the back-left where the halves pivot — a small
    # rounded umber boss so the hinge reads as the pivot of the grin.
    pygame.draw.circle(surf, SHELL_DK, (int(hinge_x), int(hinge_y)),
                       max(2, int(r * 0.22)))
    pygame.draw.circle(surf, _shade_c(SHELL_DK, 18),
                       (int(hinge_x - r * 0.05), int(hinge_y - r * 0.05)),
                       max(1, int(r * 0.13)))

    # — Slate hinge-EYES: two small calm slate ovals sitting just forward of the
    #   hinge knuckle, one on the upper lid, one on the lower — a serene
    #   heavy-lidded gaze looking out along the grin (the scary-cute beat: an
    #   ancient placid creature, not a snarl).
    for d in (-1, 1):
        ex = hinge_x + r * 0.30
        ey = hinge_y + d * r * 0.20
        er = r * (0.13 if not tell else 0.16)
        pygame.draw.circle(surf, HINGE_EYE, (int(ex), int(ey)), max(2, int(er)))
        # A calm heavy lid: a short slate arc capping the eye toward its shell.
        pygame.draw.circle(surf, _shade_c(SHELL, -18 if not night else 6),
                           (int(ex), int(ey - d * er * 0.7)),
                           max(2, int(er * 0.9)))
        # Tiny pearl catch-light so the eye reads alive but calm.
        pygame.draw.circle(surf, PEARL,
                           (int(ex - er * 0.3), int(ey - er * 0.3)),
                           max(1, int(er * 0.34)))

    if tell:
        # Baked low-res tell: bolden the two slate eyes + the gape lip so the
        # 32px chip keeps a clear horizontal-grin clam read.
        for d in (-1, 1):
            ex = hinge_x + r * 0.30
            ey = hinge_y + d * r * 0.22
            pygame.draw.circle(surf, HINGE_EYE, (int(ex), int(ey)),
                               max(2, int(r * 0.16)))
        # A bold pearl grin line across the split.
        pygame.draw.line(surf, PEARL,
                         (int(hinge_x + r * 0.2), int(hinge_y)),
                         (int(hinge_x + r * 1.6), int(hinge_y)),
                         max(2, int(2.6 * ss)))


# ── the whole creature: clam + mirage thread ──────────────────────────────────

def build_hamaguri(scale=1.0, ss=5, *, night=False, compact=False):
    """The full creature on a transparent surface: the wide gaping clam low in
    the frame, the thin mirage-city thread rising from its mouth. EPIC pass
    renders BIG at SS then smoothscales down. `compact` is the gameplay/32px
    variant — clam grown to dominate, thread shortened, a baked low-res tell."""
    r = int(40 * scale) * ss
    side_pad = int(14 * scale) * ss
    top_pad = int(12 * scale) * ss
    bot_pad = int(16 * scale) * ss

    thread_h = r * (1.5 if compact else 2.05)
    # Clam sits low; the thread climbs above it.
    W = int(side_pad * 2 + r * 2.7)
    H = int(top_pad + thread_h + r * 1.4 + bot_pad)
    surf = pygame.Surface((W, H), pygame.SRCALPHA)

    hinge_x = side_pad + r * 0.30
    hinge_y = top_pad + thread_h + r * 0.62

    _clam(surf, hinge_x, hinge_y, r, ss, night=night, tell=compact)

    out_w = int(surf.get_width() / ss)
    out_h = int(surf.get_height() / ss)
    smallv = pygame.transform.smoothscale(surf, (out_w, out_h))
    oc = (*INK_NIGHT, 245) if night else (*INK, 235)
    return _add_outline(smallv, outline_color=oc, width=2 if night else 1)


# ── pillar pair (prop -> pillar mirror proof) ─────────────────────────────────

OVERHANG = 12


def _tower_column(surf, cx, top_y, bot_y, span, ss, *, night=False):
    """The repeatable PILLAR BODY: the exhaled mirage-TOWER as a straight tiling
    shaft — translucent pearl-green pagoda STOREYS stacked one tier per repeat,
    each with its upturned roof + soul-motes, on a faint mirage haze spine.
    Drawn vertical so the storey cadence tiles cleanly top<->bottom."""
    length = bot_y - top_y
    tw = span * 0.92
    th = span * 0.78
    # Faint vertical mirage haze spine so the shaft reads as exhaled ghost-light.
    haze_w = int(span * 0.62)
    gl = make_glow_surface(haze_w, MIRAGE, alpha_center=64 if night else 42,
                           falloff=1.7)
    n_haze = max(2, int(length / (haze_w * 1.1)))
    for k in range(n_haze + 1):
        yy = top_y + length * (k / n_haze)
        surf.blit(gl, (int(cx - haze_w), int(yy - haze_w)),
                  special_flags=pygame.BLEND_ADD)

    # Stack storeys so a roof tops each storey body — one TIER per repeat.
    n_tier = max(2, int(length / (th * 1.06)))
    for k in range(n_tier):
        t = (k + 0.5) / n_tier
        yy = top_y + length * t
        _pagoda_tier(surf, cx, yy, tw, th, ss, night=night, souls=True,
                     facets=True)


def _finial_cap(surf, cx, cap_base_y, span, ss, *, point_up, night=False):
    """The detachable GAP-EDGE CAP: a single mirage-pagoda ROOF FINIAL
    (~shaft span +30%) sitting at the tower's gap end, glowing pearl-green INTO
    the gap. `point_up` orients the roof so its sweeping eaves + finial spike
    face the gap. Kept compact so the cap is never top-heavy vs the shaft."""
    d = -1 if point_up else 1
    roof_w = span * 1.30               # ~shaft +30% — modest crown
    ridge = roof_w * 0.42
    # Roof base sits at the cap band edge; the spike points INTO the gap.
    base_y = cap_base_y
    tip_y = base_y + d * ridge
    eave_hw = roof_w * 0.56
    body_a = 165 if night else 130

    # The big sweeping pagoda roof — a wide chevron with curled eaves.
    roof = [
        (cx - eave_hw, base_y),
        (cx - eave_hw * 0.44, base_y + d * ridge * 0.60),
        (cx, tip_y),
        (cx + eave_hw * 0.44, base_y + d * ridge * 0.60),
        (cx + eave_hw, base_y),
        (cx + eave_hw * 0.72, base_y - d * ridge * 0.16),
        (cx - eave_hw * 0.72, base_y - d * ridge * 0.16),
    ]
    _poly_a(surf, [(int(x), int(y)) for x, y in roof], (*MIRAGE_DK, body_a + 30))
    # Lit roof slope.
    lit = [
        (cx - eave_hw * 0.86, base_y + d * ridge * 0.02),
        (cx, tip_y - d * ridge * 0.08),
        (cx - eave_hw * 0.10, base_y + d * ridge * 0.10),
    ]
    _poly_a(surf, [(int(x), int(y)) for x, y in lit], (*MIRAGE_LT, body_a))
    # Balcony lip under the eaves (on the shaft side).
    _line_a(surf, (int(cx - eave_hw * 0.84), int(base_y - d * ridge * 0.18)),
            (int(cx + eave_hw * 0.84), int(base_y - d * ridge * 0.18)),
            (*MIRAGE_LT, 190), max(1, int(1.6 * ss)))

    # Finial SPIKE + glowing pip at the gap-facing tip — the single bright focal
    # that lanterns the gap (a slim mast and a hot mint pearl).
    mast_y = tip_y + d * ridge * 0.42
    _line_a(surf, (int(cx), int(tip_y)), (int(cx), int(mast_y)),
            (*MIRAGE_LT, 220), max(2, int(1.8 * ss)))
    _soul_spark(surf, cx, mast_y, max(2, roof_w * 0.07), ss, night=night,
                core=True)


def _tower_pillar_obstacle(height, ss, *, flip, night=False):
    """One mirage-tower PILLAR obstacle: the pagoda-storey shaft fills the post
    and a single roof-FINIAL CAP sits at the GAP-facing edge, glowing pearl-green
    INTO the gap. `flip=True` is the TOP pillar (cap at the bottom/gap edge,
    finial pointing DOWN); `flip=False` is the BOTTOM pillar (cap at the top/gap
    edge, finial pointing UP). Both mirror the same tower body — clean vertical,
    no top-heavy cap."""
    bw = (PIPE_W + 2 * OVERHANG) * ss
    bh = max(1, int(height)) * ss
    surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
    cx = bw // 2
    span = (PIPE_W - 8) * ss
    cap_band = int(48 * ss)
    if flip:
        _tower_column(surf, cx, 0, bh - cap_band, span, ss, night=night)
        _finial_cap(surf, cx, bh - cap_band, span, ss, point_up=False, night=night)
    else:
        _tower_column(surf, cx, cap_band, bh, span, ss, night=night)
        _finial_cap(surf, cx, cap_band, span, ss, point_up=True, night=night)
    out = pygame.transform.smoothscale(surf, (PIPE_W + 2 * OVERHANG, max(1, int(height))))
    oc = (*INK_NIGHT, 245) if night else (*INK, 235)
    return _add_outline(out, outline_color=oc, width=2 if night else 1)


# ── sheet composition ──────────────────────────────────────────────────────────

def _label(surf, font, text, x, y, color=(238, 240, 236)):
    surf.blit(font.render(text, True, (0, 0, 0)), (x + 1, y + 1))
    surf.blit(font.render(text, True, color), (x, y))


def _sky(w, h, top, mid, bot, *, stars=False):
    s = pygame.Surface((w, h))
    for i in range(h):
        t = i / max(1, h - 1)
        if t < 0.5:
            c = lerp_color(top, mid, t / 0.5)
        else:
            c = lerp_color(mid, bot, (t - 0.5) / 0.5)
        pygame.draw.line(s, c, (0, i), (w, i))
    if stars:
        import random as _r
        rng = _r.Random(77)
        for _ in range(26):
            sx = rng.randint(0, w - 1)
            sy = rng.randint(0, int(h * 0.7))
            pygame.draw.circle(s, (220, 230, 255), (sx, sy), rng.choice((1, 1, 2)))
    return s


def _to_gray(src):
    g = pygame.Surface(src.get_size(), pygame.SRCALPHA)
    g.blit(src, (0, 0))
    arr = pygame.surfarray.pixels3d(g)
    lum = (arr[:, :, 0] * 0.3 + arr[:, :, 1] * 0.59 + arr[:, :, 2] * 0.11).astype("uint8")
    arr[:, :, 0] = lum
    arr[:, :, 1] = lum
    arr[:, :, 2] = lum
    del arr
    return g


def main():
    pygame.font.init()
    font = pygame.font.SysFont("dejavusans", 15, bold=True)
    small = pygame.font.SysFont("dejavusans", 12)

    SW, SH = 1040, 770
    sheet = pygame.Surface((SW, SH))
    sheet.fill((52, 50, 46))          # warm neutral grey bg
    _label(sheet, font,
            "HAMAGURI-SHINKIROU  —  Umibozu-versions #4  —  mirage clam, mouth of a drowned city  —  round 1", 18, 12)
    _label(sheet, small,
            "KIND: horizontal clam-grin (the ONLY one in the roster). Sea-rust BROWN shell + bold RADIATING fan-ribs; pearl-cream sheen; PALE pearl-GREEN mirage-city (pinned apart from Tehom's sourer green).",
            18, 32, (210, 200, 178))

    # — Cell A: BIG hero, on a warm sea-haze sky (clam + mirage thread).
    panel = pygame.Rect(18, 56, 320, 660)
    bgA = _sky(panel.w, panel.h, (70, 96, 110), (120, 140, 140), (170, 168, 142))
    sheet.blit(bgA, panel.topleft)
    pygame.draw.rect(sheet, (150, 140, 110), panel, 2, border_radius=8)
    hero = build_hamaguri(scale=1.85, ss=6)
    sheet.blit(hero, (panel.centerx - hero.get_width() // 2, panel.y + 44))
    _label(sheet, font, "(a) HERO  big scale (SS=6)", panel.x + 8, panel.y + 8)
    _label(sheet, small, "serene clam hums a ghost-city; slate hinge-eyes; souls in the city",
           panel.x + 8, panel.y + 28, (220, 230, 210))

    # — Cell B: mirage-tower as a tileable PILLAR pair at TRUE obstacle scale
    #   (night), plus a 2x zoom on the cap band showing the finial roof.
    panelB = pygame.Rect(352, 56, 330, 660)
    bg = _sky(panelB.w, panelB.h, (8, 14, 24), (14, 24, 38), (22, 38, 46), stars=True)
    sheet.blit(bg, panelB.topleft)
    pygame.draw.rect(sheet, (150, 140, 110), panelB, 2, border_radius=8)
    _label(sheet, font, "(b) PILLAR  @ TRUE scale  (NIGHT)", panelB.x + 8, panelB.y + 8)
    _label(sheet, small, "mirage pagoda-storeys tile + roof-finial cap (~shaft+30%)",
           panelB.x + 8, panelB.y + 28, (210, 230, 210))

    pw = PIPE_W + 2 * OVERHANG
    slice_h = 540
    slice_x = panelB.x + 22
    slice_y = panelB.y + 50
    gap_top = 178
    gap_h = 132
    top_h = gap_top
    bot_h = slice_h - gap_top - gap_h
    top_pillar = _tower_pillar_obstacle(top_h, 4, flip=True, night=True)
    bot_pillar = _tower_pillar_obstacle(bot_h, 4, flip=False, night=True)
    sheet.blit(top_pillar, (slice_x - 2, slice_y - 2))
    sheet.blit(bot_pillar, (slice_x - 2, slice_y + gap_top + gap_h - 2))
    pygame.draw.rect(sheet, (180, 210, 190), (slice_x - 4, slice_y - 4, pw + 8, slice_h + 8), 1)
    _label(sheet, small, "1x native (82px): tower", slice_x - 2, slice_y + slice_h + 6, (210, 230, 210))
    _label(sheet, small, "tiles; finial lanterns gap", slice_x - 2, slice_y + slice_h + 22, (180, 230, 196))

    # 2x zoom of the cap band (mirror visible).
    cap_band = 48
    zw, zh = pw, 170
    zoom_src = pygame.Surface((zw, zh), pygame.SRCALPHA)
    top_anchor = 16
    zoom_src.blit(top_pillar, (-2, -(top_h - cap_band - top_anchor) - 2))
    zoom_gap = zh - 2 * cap_band - 2 * top_anchor
    bot_anchor = top_anchor + cap_band + zoom_gap
    zoom_src.blit(bot_pillar, (-2, bot_anchor - 2))
    zoom = pygame.transform.scale(zoom_src, (zw * 2, zh * 2))
    zx = panelB.x + 168
    zy = panelB.y + 116
    zbg = _sky(zw * 2, zh * 2, (8, 14, 24), (12, 22, 36), (18, 32, 42))
    sheet.blit(zbg, (zx, zy))
    pygame.draw.rect(sheet, (180, 210, 190), (zx - 1, zy - 1, zw * 2 + 2, zh * 2 + 2), 1)
    sheet.blit(zoom, (zx, zy))
    _label(sheet, small, "2x zoom: roof-finial", zx - 2, zy - 16, (255, 255, 255))
    _label(sheet, small, "MIRROR @ gap", zx - 2, zy + zh * 2 + 6, (180, 230, 196))

    # — Cell C: TRUE 32px gameplay chip on day + night, plus a 4x audit + grayscale.
    panelC = pygame.Rect(696, 56, 326, 660)
    pygame.draw.rect(sheet, (44, 42, 38), panelC, border_radius=8)
    pygame.draw.rect(sheet, (150, 140, 110), panelC, 2, border_radius=8)
    _label(sheet, font, "(c) TRUE 32px gameplay chip", panelC.x + 8, panelC.y + 8)
    _label(sheet, small, "clam-dominant compact / day + night sky", panelC.x + 8, panelC.y + 28,
           (210, 230, 210))

    # Compact gameplay creature, day + night, at a readable mid scale.
    boss_day = build_hamaguri(scale=0.62, ss=6, compact=True)
    boss_night = build_hamaguri(scale=0.62, ss=6, night=True, compact=True)
    day = _sky(150, 300, (60, 140, 215), (110, 185, 235), (180, 222, 246))
    night = _sky(150, 300, (8, 14, 26), (12, 24, 40), (20, 44, 54), stars=True)
    dy = panelC.y + 50
    sheet.blit(day, (panelC.x + 12, dy))
    sheet.blit(night, (panelC.x + 170, dy))
    sheet.blit(boss_day, (panelC.x + 12 + 75 - boss_day.get_width() // 2, dy + 8))
    sheet.blit(boss_night, (panelC.x + 170 + 75 - boss_night.get_width() // 2, dy + 8))
    _label(sheet, small, "DAY", panelC.x + 18, dy + 6, (16, 28, 40))
    _label(sheet, small, "NIGHT", panelC.x + 176, dy + 6, (180, 230, 196))

    # TRUE 32px chips on day + night skies, then a 4x nearest-neighbour blow-up
    # + grayscale audit.
    gy = dy + 318
    _label(sheet, small, "TRUE 32px chip on day + night sky:", panelC.x + 12, gy - 2,
           (210, 226, 210))
    icon_src = build_hamaguri(scale=1.0, ss=6, compact=True)
    sc32 = 32 / icon_src.get_height()
    icon32 = pygame.transform.smoothscale(
        icon_src, (max(1, int(icon_src.get_width() * sc32)), 32))

    chips = [
        (_sky(86, 86, (60, 140, 215), (110, 185, 235), (180, 222, 246)), "day"),
        (_sky(86, 86, (8, 14, 26), (12, 24, 40), (20, 44, 54), stars=True), "night"),
    ]
    sx = panelC.x + 12
    for bg_chip, lab in chips:
        chip = pygame.Rect(sx, gy + 16, 86, 86)
        sheet.blit(bg_chip, chip.topleft)
        pygame.draw.rect(sheet, (160, 160, 130), chip, 1, border_radius=4)
        sheet.blit(icon32, (chip.centerx - icon32.get_width() // 2,
                            chip.centery - icon32.get_height() // 2))
        _label(sheet, small, lab, chip.x + 4, chip.y + 2, (240, 244, 240))
        sx += 96

    # 4x blow-up + grayscale of the true-32 chip.
    blow = pygame.transform.scale(icon32, (icon32.get_width() * 4, icon32.get_height() * 4))
    bx = panelC.x + 12
    byy = gy + 118
    pygame.draw.rect(sheet, (62, 60, 56), (bx - 2, byy - 2, blow.get_width() + 4, blow.get_height() + 4),
                     border_radius=4)
    sheet.blit(blow, (bx, byy))
    _label(sheet, small, "4x blow-up of the 32px chip", bx, byy + blow.get_height() + 4,
           (210, 226, 210))

    gray = _to_gray(blow)
    gx = bx + blow.get_width() + 24
    pygame.draw.rect(sheet, (112, 110, 106), (gx - 2, byy - 2, gray.get_width() + 4, gray.get_height() + 4),
                     border_radius=4)
    sheet.blit(gray, (gx, byy))
    _label(sheet, small, "grayscale value check", gx, byy + gray.get_height() + 4, (24, 24, 24))

    # — Footer captions.
    _label(sheet, small,
           "STYLE: flat warm fills, hard 1-2px ink keyline (28,26,24), dark-core -> flat-fill -> pearl-cream rim-sheen triad, 1px grown outline, chibi, scary-CUTE.",
           18, SH - 40, (210, 200, 178))
    _label(sheet, small,
           "PILLAR: the exhaled mirage-TOWER IS the shaft (pagoda storeys tile, one tier per repeat, w/ soul-motes); a single roof-FINIAL (~shaft+30%) caps + lanterns the gap pearl-green. On-axis mirror, no top-heavy cap.",
           18, SH - 22, (210, 200, 178))

    out_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(out_dir, "round_1.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path)


if __name__ == "__main__":
    main()
