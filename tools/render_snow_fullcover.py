"""DESIGN EXPLORATION — extend Pip's snow accumulation past today's max
(face still readable) all the way to FULLY COVERED, for the predawn snow
squall whiteout. Throwaway sheet tool; touches NO game code.

The shipped look is snow_fx.py's W2 "sculpted blanket": per-column depth
following the bird's top silhouette, drawn as 3 vertical-line layers
(off-white body + bright crest + cool-blue under-edge), with a head cap
`if xf > 0.60: d = min(d, 7.0 + hi*11*(1-headfrac))` that deliberately
keeps the face readable. We extend PAST that cap.

We add a single `extra` knob in [0,1] that drives accumulation beyond the
shipped peak (load>=1.0): it (a) lifts the head cap so snow creeps over
crown->face->beak, (b) deepens the pile, and (c) widens coverage forward.
extra=0 reproduces the shipped peak; extra=1.0 is fully covered. Each of
the 5 versions reuses this column scaffold but applies a DISTINCT finish so
the visibility spectrum (camouflage in the whiteout) spans medium..hidden.

The technique stays numpy-free / pure pygame so it ports straight into
snow_fx.py later.

Run from repo root:
  SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python -m tools.render_snow_fullcover
Output: docs/snow_full_cover/round_2.png
"""
from __future__ import annotations

import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

pygame.init()
pygame.display.set_mode((360, 640))

import game.entities as E
from game.entities import Bird
from game import parrot, snow_fx, biome
from game.draw import make_gradient_surface

OUT_DIR = os.path.join(ROOT, "docs", "snow_full_cover")
os.makedirs(OUT_DIR, exist_ok=True)

# Palette (cohesive with shipped snow_fx).
WHITE = (255, 255, 255)
OFF = (236, 244, 252)
BLUE = (188, 206, 230)
SHADOW = (150, 168, 198)
GLAZE = (172, 214, 238)          # V4 glassy cyan-blue sheen
RED = (240, 55, 55)              # shipped BIRD_RED — peeks must match exactly

# Silhouette landmarks on the 64x60 _REF_FRAME (level-wing). Used to punch
# character peeks (eye glint / beak nub / red sliver) back THROUGH the snow so
# Pip stays recognisable at full cover. xf = x/64.
EYE_PX = (50, 20)                # aviator centre
BEAK_TIP_PX = (61, 24)           # hooked beak point
HEAD_BACK_PX = (40, 16)          # crown→back-of-head break (the hard edge)
RED_CHEEK_PX = (44, 26)          # lower cheek where scarlet shows under the lens

ZOOM = 6                         # sprite is 64x60; render big for detail


# ── shared extended column scaffold (numpy-free, snow_fx-portable) ───────────
def _columns(extra, *, cap_lift, depth_gain, front_reach,
             cornice=1.6, lump=0.0, noise_amp=2.4):
    """Yield (x, y0, y1, d) snow bands per column for the FULLY-COVERED
    extension. `extra` in [0,1] continues past the shipped peak (load=1.0):

      cap_lift   - how far the head cap is released (snow climbs the face)
      depth_gain - how much deeper the pile grows beyond shipped MAXD
      front_reach- how far coverage pushes toward the beak (front columns)

    extra=0 ~ shipped peak; extra=1 ~ buried. Each version passes its own
    gains so the same scaffold yields different finishes."""
    top, x_min, w, h = snow_fx._topline(snow_fx._REF_FRAME)
    if x_min < 0:
        return []
    taper_w = 13.0
    out = []
    for x in range(w):
        yt = top[x]
        if yt < 0:
            continue
        xf = x / w
        # Coverage spreads forward as `extra` grows. At extra=0 this matches
        # the shipped _cov(xf, load=1.0); `extra` then lowers the rear-first
        # onset threshold so front (beak) columns reach full coverage too.
        thr = 0.55 * xf * (1.0 - front_reach * extra)
        load = 1.0
        cov = 0.0 if load <= thr else min(1.0, (load - thr) / (1.0 - thr))
        if cov <= 0.0:
            continue
        rear = 1.0 - xf
        bulge = math.exp(-((xf - 0.40) / 0.26) ** 2)
        d = snow_fx.MAXD * cov * (0.50 + 0.45 * rear + 0.45 * bulge)
        d *= (1.0 + depth_gain * extra)                  # whole pile thickens
        if xf > 0.60:
            # Shipped cap: d = min(d, 7.0 + hi*11*(1-headfrac)) at peak (hi=1).
            # We RAISE the ceiling by cap_lift*extra so snow climbs crown->
            # face->beak. The (1-headfrac) bias keeps the very beak-tip the
            # last thing buried, so silhouette stays parrot-shaped longest.
            headfrac = (xf - 0.60) / 0.40
            base_cap = 7.0 + 11.0 * (1.0 - headfrac)
            cap = base_cap + cap_lift * extra * (13.0 + 9.0 * (1.0 - headfrac))
            d = min(d, cap)
        te = snow_fx._smooth((x - x_min) / taper_w)
        d *= te
        if d < 0.6:
            continue
        over = cornice * rear * te
        if lump:
            over += lump * (0.5 + 0.5 * math.sin(x * 0.9)) * (0.35 + rear) * te
        nb = (math.sin(x * 1.26) + math.sin(x * 0.34)) * 0.25 + 0.5
        y0 = yt - over
        y1 = yt + d + (nb - 0.5) * noise_amp
        out.append((x, y0, y1, y1 - y0))
    return out


def _blur(s, downs):
    w, h = s.get_size()
    if w < downs * 2 or h < downs * 2:
        return s
    sm = pygame.transform.smoothscale(s, (w // downs, h // downs))
    return pygame.transform.smoothscale(sm, (w, h))


def _native_size():
    _, _, w, h = snow_fx._topline(snow_fx._REF_FRAME)
    return w, h


# ── V1 · Icicle-fringe finish ────────────────────────────────────────────────
# A smooth packed blanket over crown/back PLUS a row of small hanging icicles +
# drip points along the lower/front edge — a distinct silhouette signature no
# other version has. Eye glint + beak-tip nub survive. MEDIUM read.
def v1_icicle_fringe(extra):
    w, h = _native_size()
    ov = pygame.Surface((w, h), pygame.SRCALPHA)
    cols = _columns(extra, cap_lift=1.0, depth_gain=0.95, front_reach=0.85,
                    cornice=1.2, noise_amp=0.8)
    if not cols:
        return None
    # Smooth, low-noise packed blanket (rounded, dense surface).
    edge_y = {}
    for x, y0, y1, d in cols:
        pygame.draw.line(ov, (*OFF, 255), (x, int(y0)), (x, int(y1)), 1)
        pygame.draw.line(ov, (*WHITE, 255), (x, int(y0)), (x, int(y0 + d * 0.22)), 1)
        pygame.draw.line(ov, (*BLUE, 255), (x, int(y1 - d * 0.20)), (x, int(y1)), 1)
        edge_y[x] = y1
    ov = _blur(ov, 2)                                    # smooth the surface
    if extra > 0.2:
        amt = (extra - 0.2) / 0.8
        # Hanging icicles: a row of tapered teeth along the lower edge, longer
        # toward the front (where blown snow over-hangs the face). Each tooth is
        # a fat 3px white shaft narrowing to a cool-blue tip with a bead drip —
        # the distinct silhouette signature no other version carries.
        xs = sorted(edge_y)
        for x in xs:
            xf = x / w
            sel = (math.sin(x * 0.7) * 0.5 + 0.5)
            if sel < 0.55 or x % 4 != 0:
                continue
            length = (5.0 + 11.0 * amt) * (0.45 + 0.8 * xf) * (0.55 + 0.6 * sel)
            ybase = edge_y[x] - 1
            tip = ybase + length
            mid = tip - length * 0.4
            # tapering shaft: wide (3px) at the root, single px at the point
            for dx, a in ((-1, 230), (0, 255), (1, 230)):
                pygame.draw.line(ov, (*WHITE, a), (x + dx, int(ybase)),
                                 (x + dx, int(mid)), 1)
            pygame.draw.line(ov, (*WHITE, 255), (x, int(mid)),
                             (x, int(tip - 1)), 1)
            pygame.draw.line(ov, (*BLUE, 235), (x, int(tip - 1)), (x, int(tip)), 1)
            # melt-bead drip clinging just below the point
            pygame.draw.circle(ov, (*OFF, 235), (x, int(tip + 1)), 1)
    ov = _clip_to_body(ov, extra, front_reach=0.85, cap_lift=1.0)
    # Surviving eye glint + beak-tip nub through the blanket (medium read).
    if extra > 0.5:
        _peek_eye(ov)
        _peek_beak(ov)
    return ov


# ── V2 · Chunky caked drift ──────────────────────────────────────────────────
# Heavy lumpy sculpted clumps + a wind cornice over the crown. LOWER read:
# bumpy white mass, only a small eye peek.
def v2_chunky_drift(extra):
    w, h = _native_size()
    ov = pygame.Surface((w, h), pygame.SRCALPHA)
    cols = _columns(extra, cap_lift=1.05, depth_gain=1.15, front_reach=0.8,
                    cornice=3.0, lump=3.2, noise_amp=3.4)
    if not cols:
        return None
    for x, y0, y1, d in cols:
        pygame.draw.line(ov, (*OFF, 255), (x, int(y0)), (x, int(y1)), 1)
        pygame.draw.line(ov, (*WHITE, 255), (x, int(y0)), (x, int(y0 + d * 0.16)), 1)
        # De-mudded under-edge: the lower-body shadow is now mostly the shipped
        # cool-blue snow shadow (BLUE) with only a thin deepest-crease SHADOW
        # band, so the caked drift reads as cold snow — never grey-blue slush.
        pygame.draw.line(ov, (*BLUE, 255), (x, int(y1 - d * 0.34)),
                         (x, int(y1 - d * 0.08)), 1)
        pygame.draw.line(ov, (*SHADOW, 165), (x, int(y1 - d * 0.08)), (x, int(y1)), 1)
    # Caked clumps ANCHORED to the silhouette edge: stamp straddling the cornice
    # over-hang line (y0) of the rear/crown columns so the clump's mass sits ON
    # the snow surface — none float detached above it. The clump's own blue
    # under-shadow ties it down to the surface below.
    for x, y0, y1, d in cols:
        lump = 0.5 + 0.5 * math.sin(x * 0.9)
        if lump > 0.72 and d > 4.0:
            r = max(2, int(2.2 + 2.4 * lump))
            anchor = y0 + r * 0.5                         # clump centre sits ON the edge
            _stamp(ov, x, anchor, r, OFF, 255)
            _stamp(ov, x, anchor - r * 0.3, max(1, r - 1), WHITE, 240)
            # tie-down shadow merges the clump into the surface below it
            pygame.draw.line(ov, (*BLUE, 210),
                             (x, int(anchor + r * 0.5)),
                             (x, int(anchor + r * 1.2)), 1)
    ov = _blur(ov, 1)
    ov = _clip_to_body(ov, extra, front_reach=0.8, cap_lift=1.05)
    if extra > 0.45:
        # Preserve a 2-3px dark eye-socket notch through full cover — a shadowed
        # pit pressed into the drift (cool-blue rim around a dark core) so the
        # face still has one fixed landmark even when fully caked.
        _carve(ov, EYE_PX[0], EYE_PX[1], 3.0)
        pygame.draw.circle(ov, (*BLUE, 230), EYE_PX, 3)
        pygame.draw.circle(ov, (24, 30, 42), EYE_PX, 2)
    return ov


# ── V3 · Soft powder puff ────────────────────────────────────────────────────
# Fluffy, fuzzy-edged fresh powder, soft alpha falloff. STRONG camouflage:
# nearly dissolves into the whiteout, just a faint eye glint.
def v3_powder_puff(extra):
    w, h = _native_size()
    ov = pygame.Surface((w * 2, h * 2), pygame.SRCALPHA)   # 2x for soft stamps
    cols = _columns(extra, cap_lift=1.1, depth_gain=1.1, front_reach=0.92,
                    cornice=1.0, noise_amp=2.0)
    if not cols:
        return None
    # Higher base alpha + cooler palette: the round-1 powder read warm/pink
    # because the parrot's scarlet bled through thin low-alpha discs. Denser
    # opaque stamps (alpha 170) skewed toward white/off-white kill the warm
    # haze so it reads as cold snow, not pink fog.
    for x, y0, y1, d in cols:
        n = max(2, int(d / 1.6) + 2)
        for i in range(n + 1):
            t = i / max(1, n)
            yy = (y0 + (y1 - y0) * t) * 2
            col = WHITE if t < 0.55 else (OFF if t < 0.82 else BLUE)
            _stamp(ov, x * 2, yy, 4.4, col, 170)
    ov = _blur(ov, 4)                                       # heavy fuzz
    ov = pygame.transform.smoothscale(ov, (w, h))
    # ONE hard internal edge: a carved cool-shadow valley at the crown->back
    # seam so the soft mound still reads "bird" (a head over a body) before it
    # dissolves into the whiteout. The only crisp feature on this row.
    if extra > 0.4:
        _hard_break(ov)
        # a single faint eye glint is the only other surviving cue (camo row)
        ex, ey = EYE_PX
        pygame.draw.circle(ov, (210, 222, 238, 200), (ex, ey), 1)
    return _clip_to_body(ov, extra, front_reach=0.92, cap_lift=1.1)


# ── V4 · Icy glaze / frost ───────────────────────────────────────────────────
# Snow + a bluish glassy glaze + sparkles; Pip's red shows faintly THROUGH
# the ice (frozen-in look), eye + beak visible. MEDIUM-HIGH read.
def v4_icy_glaze(extra):
    w, h = _native_size()
    ov = pygame.Surface((w, h), pygame.SRCALPHA)
    # Wider mid step (front_reach high) so the mid cell clearly differs from
    # current-max; front_reach lets coverage push forward but we trim the chin
    # in _clip_to_body so snow doesn't creep under the jaw.
    cols = _columns(extra, cap_lift=0.92, depth_gain=0.85, front_reach=0.9,
                    cornice=1.1, noise_amp=1.2)
    if not cols:
        return None
    # OPAQUE-FIRST: lay a solid white/off-white snow base (alpha 255) so the
    # whole cap reads as cold packed snow, not wet melt. The icy character is
    # added AFTER, as a glaze confined to the lower third.
    for x, y0, y1, d in cols:
        pygame.draw.line(ov, (*OFF, 255), (x, int(y0)), (x, int(y1)), 1)
        pygame.draw.line(ov, (*WHITE, 255), (x, int(y0)), (x, int(y0 + d * 0.20)), 1)
        pygame.draw.line(ov, (*BLUE, 255), (x, int(y1 - d * 0.22)), (x, int(y1)), 1)
    ov = _blur(ov, 1)
    # Glaze pass: a glassy cyan sheen ONLY on the lower third of each column,
    # where melt-refreeze ice would pool — the upper two-thirds stay matte snow.
    glaze = pygame.Surface((w, h), pygame.SRCALPHA)
    for x, y0, y1, d in cols:
        if d < 3.0:
            continue
        gtop = y0 + d * 0.62
        pygame.draw.line(glaze, (*GLAZE, 130), (x, int(gtop)), (x, int(y1)), 1)
        pygame.draw.line(glaze, (*GLAZE, 90),
                         (x, int(gtop - 2)), (x, int(gtop)), 1)
    glaze = _blur(glaze, 1)
    ov.blit(glaze, (0, 0))
    # Sharp glassy glints (4-point stars) deterministically scattered on the
    # glazed band — the frost sparkle that sells the ice without translucency.
    for x, y0, y1, d in cols:
        g = (math.sin(x * 12.99) * 4375.5) % 1.0
        if g > 0.88 and d > 3.0:
            sx, sy = x, int(y0 + d * 0.78)
            for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
                pygame.draw.line(ov, (*WHITE, 240), (sx, sy), (sx + dx, sy + dy), 1)
            pygame.draw.circle(ov, (*WHITE, 255), (sx, sy), 1)
    # glaze_red lets a faint scarlet/blue read FROZEN-IN on the lower third
    # only (handled in _clip_to_body), keeping the goggles-through-frost charm.
    ov = _clip_to_body(ov, extra, front_reach=0.9, cap_lift=0.92,
                       glaze_red=True)
    # Goggles peek: punch the aviator lens through the frost (charming, on-brand)
    # plus a faint frozen beak nub. Eye stays the clearest cue on this row.
    if extra > 0.45:
        _peek_eye(ov)
        _peek_beak(ov)
    return ov


# ── V5 · Layered ridge blanket (extends shipped W2) ──────────────────────────
# Continuous connected sculpted blanket tail->back->nape->crown->over-face
# with defined ridge layers. HIGHEST read: eye + beak + thin red sliver peek.
def v5_ridge_blanket(extra):
    w, h = _native_size()
    ov = pygame.Surface((w, h), pygame.SRCALPHA)
    # Lower noise_amp so the ridge bands stay clean (not shimmery) at montage
    # size; cap_lift kept modest so the face keeps the most parrot of any row.
    cols = _columns(extra, cap_lift=0.82, depth_gain=0.78, front_reach=0.72,
                    cornice=1.8, noise_amp=1.0)
    if not cols:
        return None
    # Shipped W2 fill: off-white body + bright crest + cool-blue under-edge.
    for x, y0, y1, d in cols:
        pygame.draw.line(ov, (*OFF, 255), (x, int(y0)), (x, int(y1)), 1)
        pygame.draw.line(ov, (*WHITE, 255), (x, int(y0)), (x, int(y0 + d * 0.16)), 1)
        pygame.draw.line(ov, (*BLUE, 255), (x, int(y1 - d * 0.24)), (x, int(y1)), 1)
    # Exactly THREE thick ridge bands (overlapping wind-drifts). Each band is a
    # broad blue shadow trough (the drift's downhill face) crested by a thick
    # white lip — drawn fat (3-4px) so the ridge survives the 34px montage and
    # reads as sculpture, not a flat slab. Only three, so it never shimmers.
    cmap = {c[0]: c for c in cols}
    for ridge, lip in ((0.30, 1.0), (0.55, 0.9), (0.80, 0.8)):
        for x, y0, y1, d in cols:
            if d < 5.0:
                continue
            # Slow phase so the ridge undulates gently across columns (1 wave
            # over the body) instead of jittering column-to-column.
            ry = y0 + d * ridge + math.sin(x * 0.28) * 1.4
            # Thick bright crest lip above the trough.
            pygame.draw.line(ov, (*WHITE, 235),
                             (x, int(ry - 2)), (x, int(ry)), 1)
            pygame.draw.line(ov, (*OFF, 255),
                             (x, int(ry - 3)), (x, int(ry - 2)), 1)
            # Broad cool-blue shadow trough just below the lip.
            pygame.draw.line(ov, (*BLUE, 210),
                             (x, int(ry + 1)), (x, int(ry + 2)), 1)
            pygame.draw.line(ov, (*SHADOW, int(150 * lip)),
                             (x, int(ry + 2)), (x, int(ry + 4)), 1)
    ov = _clip_to_body(ov, extra, front_reach=0.72, cap_lift=0.82)
    # Character peeks survive at full cover: aviator lens + glint, beak nub,
    # and a thin scarlet sliver in the shipped BIRD_RED — the readable lead.
    if extra > 0.5:
        _peek_eye(ov)
        _peek_beak(ov)
        _peek_red(ov, color=RED)
    return ov


# ── helpers ──────────────────────────────────────────────────────────────────
def _stamp(layer, x, y, r, color, alpha):
    d = max(2, int(r * 2))
    s = pygame.Surface((d, d), pygame.SRCALPHA)
    pygame.draw.circle(s, (*color, alpha), (d // 2, d // 2), max(1, d // 2 - 1))
    layer.blit(s, (int(x - d / 2), int(y - d / 2)))


def _carve(ov, x, y, r):
    """Punch a transparent hole in the snow overlay so the sprite underneath
    (eye lens, beak, scarlet cheek) shows through — the silhouette cue that
    keeps Pip a parrot at full cover. Pure alpha erase, WASM-safe."""
    d = max(2, int(r * 2) + 1)
    hole = pygame.Surface((d, d), pygame.SRCALPHA)
    pygame.draw.circle(hole, (0, 0, 0, 255), (d // 2, d // 2), max(1, int(r)))
    ov.blit(hole, (int(x - d / 2), int(y - d / 2)),
            special_flags=pygame.BLEND_RGBA_SUB)


def _peek_eye(ov, scale=1.0):
    # A small dark lens + bright glint reads as Pip's aviator at montage size.
    ex, ey = EYE_PX
    _carve(ov, ex, ey, 2.4 * scale)
    pygame.draw.circle(ov, (28, 34, 46), (ex, ey), max(2, int(2.4 * scale)))
    pygame.draw.circle(ov, (235, 242, 252), (ex - 1, ey - 1), 1)


def _peek_beak(ov, scale=1.0):
    bx, by = BEAK_TIP_PX
    _carve(ov, bx - 1, by, 2.0 * scale)
    pygame.draw.polygon(ov, (255, 185, 0),
                        [(bx, by - 2), (bx + 1, by + 1), (bx - 3, by)])


def _peek_red(ov, scale=1.0, color=RED):
    # A thin scarlet sliver under the lens — the brand colour, shipped value.
    rx, ry = RED_CHEEK_PX
    _carve(ov, rx, ry, 2.2 * scale)
    pygame.draw.line(ov, color, (rx - 3, ry + 1), (rx + 3, ry), 2)


def _hard_break(ov):
    """One carved cool-shadow valley at the crown→back-of-head seam so a
    front (head) / back (body) split survives even under heavy cover — the
    minimum cue that the white mound is still bird-shaped."""
    hx, hy = HEAD_BACK_PX
    for i in range(-2, 7):
        pygame.draw.line(ov, (*SHADOW, 210),
                         (hx, hy + i), (hx + 4, hy + i + 5), 1)
        pygame.draw.line(ov, (*BLUE, 150),
                         (hx + 4, hy + i), (hx + 8, hy + i + 5), 1)


def _clip_to_body(ov, extra, *, front_reach, cap_lift, glaze_red=False):
    """Allow snow to extend a little BELOW the top silhouette only where the
    bird's body actually is — masks stray blur outside Pip and, at high
    extra, lets a translucent skim run down the front so he's fully enclosed
    rather than just top-capped. Returns the overlay unchanged for the simple
    cases; the bird sprite under it provides the lower body."""
    # The overlay is meant to sit on top of the bird sprite; lower-body
    # enclosure at full cover is approximated by an extra soft front skim.
    if extra < 0.55:
        return ov
    top, x_min, w, h = snow_fx._topline(snow_fx._REF_FRAME)
    skim = pygame.Surface((w, h), pygame.SRCALPHA)
    amt = (extra - 0.55) / 0.45
    for x in range(w):
        yt = top[x]
        if yt < 0:
            continue
        xf = x / w
        # V4 only: trim the chin — don't let snow creep under the front/jaw
        # (xf>0.78) so the goggles-through-frost stays clean, not muffled.
        if glaze_red and xf > 0.78:
            continue
        # Front/lower skim: faint snow clinging down the body face so the
        # silhouette fills with white at full cover (keeps red from dominating).
        depth = (8.0 + 14.0 * amt) * (0.4 + 0.6 * (1.0 - abs(xf - 0.45) * 1.4))
        if depth < 1.0:
            continue
        a = int(110 * amt) if not glaze_red else int(70 * amt)
        col = OFF if not glaze_red else GLAZE
        pygame.draw.line(skim, (*col, a), (x, yt + 2), (x, int(yt + depth)), 1)
        if glaze_red:
            # FROZEN-IN colour on the LOWER third only: a faint scarlet then
            # cool-blue hint sealed under the ice, so Pip's brand red glows
            # dimly through the glaze (charming) without reading as wet melt.
            lo = int(yt + depth * 0.66)
            pygame.draw.line(skim, (*RED, int(40 * amt)),
                             (x, lo), (x, int(yt + depth * 0.85)), 1)
            pygame.draw.line(skim, (*BLUE, int(55 * amt)),
                             (x, int(yt + depth * 0.85)), (x, int(yt + depth)), 1)
    skim = _blur(skim, 2)
    ov.blit(skim, (0, 0))
    return ov


# ── parcel snow: extend the shipped cap to fully covered too ──────────────────
def parcel_overlay(mode, extra, version):
    """Snow cap on the parcel that thickens with `extra` so the parcel stays
    VISIBLE but snow-covered. Reuses snow_fx's parcel column technique,
    deepened past PARCEL_MAXD; finish loosely matches the body version."""
    top, x_min, w, h = snow_fx._parcel_topline(mode)
    if x_min < 0:
        return None
    ov = pygame.Surface((w, h), pygame.SRCALPHA)
    taper_w = 4.0
    depth = snow_fx.PARCEL_MAXD * (1.0 + 1.4 * extra)
    for x in range(w):
        yt = top[x]
        if yt < 0:
            continue
        rear = 1.0 - x / w
        te = snow_fx._smooth((x - x_min) / taper_w)
        d = depth * (0.65 + 0.5 * rear) * te
        if d < 0.6:
            continue
        nb = math.sin(x * 1.7) * 0.25 + 0.5
        y0 = yt - 0.6 * te
        y1 = yt + d + (nb - 0.5) * 1.4
        if version == 4:        # icy glaze parcel
            pygame.draw.line(ov, (*OFF, 210), (x, int(y0)), (x, int(y1)), 1)
            pygame.draw.line(ov, (*GLAZE, 150), (x, int(y0 + d * 0.4)),
                             (x, int(y1)), 1)
        else:
            pygame.draw.line(ov, (*OFF, 255), (x, int(y0)), (x, int(y1)), 1)
        pygame.draw.line(ov, (*WHITE, 255), (x, int(y0)), (x, int(y0 + d * 0.22)), 1)
        pygame.draw.line(ov, (*BLUE, 255), (x, int(y1 - d * 0.3)), (x, int(y1)), 1)
    return ov


# ── compose one Pip cell: bird sprite + body overlay + parcel + parcel snow ──
def render_cell(version_fn, extra, version_idx, *, glaze_red=False):
    """Build a native-size cell with Pip + extended snow, then scale up.
    Mirrors Bird.draw's compositing order (sprite, body snow, parcel,
    parcel snow) without touching game code."""
    nw, nh = _native_size()
    pad = 6
    cw, ch = nw + pad * 2, nh + pad * 2 + 14   # +room for the lower parcel
    cell = pygame.Surface((cw, ch), pygame.SRCALPHA)
    spr = parrot._get_frames()[snow_fx._REF_FRAME]
    bx, by = pad, pad
    # Parcel sits PARCEL_Y_OFFSET below the bird centre; bird sprite centre
    # is at (nw/2, nh/2) within its frame box.
    parcel = parrot.get_parcel("normal")
    pw, ph = parcel.get_size()
    pcx = bx + nw / 2
    pcy = by + nh / 2 + 12
    # Frozen-in red look (V4): tint the visible red faintly cyan AFTER snow.
    cell.blit(spr, (bx, by))
    # Parcel under the snow line (drawn before body snow so body snow can
    # overlap its top edge, matching how Pip's body sits in front).
    cell.blit(parcel, (int(pcx - pw / 2), int(pcy - ph / 2)))
    pov = parcel_overlay("normal", extra, version_idx)
    if pov is not None:
        cell.blit(pov, (int(pcx - pw / 2), int(pcy - ph / 2)))
    # Body snow overlay on top.
    ov = version_fn(extra)
    if ov is not None:
        cell.blit(ov, (bx, by))
    return pygame.transform.scale(cell, (cw * ZOOM, ch * ZOOM)), (cw, ch)


# ── reference row via the REAL Bird.draw ─────────────────────────────────────
def render_reference(load):
    """The shipped render: set Bird.snow_load and call the real Bird.draw."""
    nw, nh = _native_size()
    pad = 6
    cw, ch = nw + pad * 2, nh + pad * 2 + 14
    cell = pygame.Surface((cw, ch), pygame.SRCALPHA)
    b = Bird()
    b.x = pad + nw / 2
    b.y = pad + nh / 2
    b.vy = 0  # tilt_deg is a read-only property derived from vy; 0 = level
    b.snow_load = load
    b.draw(cell, 0, 0)
    return pygame.transform.scale(cell, (cw * ZOOM, ch * ZOOM)), (cw, ch)


# ── backdrops ────────────────────────────────────────────────────────────────
def neutral_panel(w, h):
    return make_gradient_surface(w, h, [(0.0, (34, 40, 54)), (1.0, (22, 26, 36))])


def whiteout_panel(w, h):
    """Snowstorm whiteout: bright pale-grey gradient + scattered flakes, to
    judge how well Pip hides."""
    s = make_gradient_surface(w, h, [(0.0, (214, 224, 236)), (1.0, (188, 200, 218))])
    for i in range(int(w * h / 90)):
        x = (math.sin(i * 12.9898) * 43758.5) % 1.0 * w
        y = (math.sin(i * 78.233) * 12543.7) % 1.0 * h
        r = 1 + int((math.sin(i * 3.1) * 0.5 + 0.5) * 2)
        a = 120 + int((math.sin(i * 1.7) * 0.5 + 0.5) * 100)
        fl = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(fl, (255, 255, 255, a), (r, r), r)
        s.blit(fl, (int(x), int(y)))
    return s


def on_panel(cell, panel_fn):
    """Composite a transparent Pip cell onto a backdrop panel."""
    w, h = cell.get_size()
    panel = panel_fn(w, h)
    panel.blit(cell, (0, 0))
    return panel


# ── sheet layout ─────────────────────────────────────────────────────────────
# Rows ordered along the visibility spectrum (easiest-to-track lead first):
# V5 ridge -> V4 ice -> V2 chunky -> V1 icicle -> V3 camo.
VERSIONS = [
    ("V5 - Layered ridge blanket (extends W2)",
     "3 thick connected ridge bands over face; HIGHEST read - eye+beak+red sliver",
     v5_ridge_blanket, 5, False),
    ("V4 - Icy glaze / frost",
     "opaque snow base + cyan glaze on lower third; MED-HIGH - goggles+red thru ice",
     v4_icy_glaze, 4, True),
    ("V2 - Chunky caked drift",
     "lumpy clumps + crown cornice, cool-blue shadow; LOWER read - eye-socket notch",
     v2_chunky_drift, 2, False),
    ("V1 - Icicle-fringe finish",
     "smooth blanket + hanging icicle teeth + drips; MEDIUM - eye glint + beak nub",
     v1_icicle_fringe, 1, False),
    ("V3 - Soft powder puff",
     "fuzzy cool powder + 1 hard head-break; STRONG camo - dissolves into whiteout",
     v3_powder_puff, 3, False),
]

# Per-row extension progression. The FIRST cell is the shipped load=1.0 frame
# (rendered via the REAL Bird.draw, identical to the reference row's last cell)
# so every row reads as continuous accumulation from the exact same start; the
# version finish only diverges from the mid cell onward. extra: mid / full.
EXT_STEPS = [
    ("mid extension", 0.55),
    ("FULLY COVERED", 1.0),
]


def main():
    label_w = 232
    gap = 8
    pad_out = 18
    title_h = 76

    # Probe cell pixel size.
    _, (cw, ch) = render_reference(1.0)
    cell_w, cell_h = cw * ZOOM, ch * ZOOM

    # Reference row: 4 loads, single panel each.
    ref_loads = [0.0, 0.35, 0.70, 1.00]
    ref_cols = len(ref_loads)
    # Version rows: 2 progression cells + a final FULLY-COVERED cell shown on
    # TWO panels (dark + whiteout) side by side -> 4 cell-widths total.
    ver_cols = 4

    cols_max = max(ref_cols, ver_cols)
    row_h = cell_h + 30
    sheet_w = label_w + cols_max * (cell_w + gap) + pad_out * 2
    rows = 1 + len(VERSIONS)
    sheet_h = title_h + rows * (row_h + gap) + pad_out

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((14, 16, 24))

    fbig = pygame.font.SysFont("Arial", 26, bold=True)
    frow = pygame.font.SysFont("Arial", 17, bold=True)
    fnote = pygame.font.SysFont("Arial", 13)
    fcell = pygame.font.SysFont("Arial", 13, bold=True)

    GOLD = (240, 206, 120)
    WLBL = (228, 236, 248)
    DIM = (170, 184, 206)

    sheet.blit(fbig.render("Pip - snow FULL COVER extension  (predawn squall whiteout)",
                           True, GOLD), (pad_out, 14))
    sheet.blit(fnote.render(
        "Each row CELL 1 = real shipped Bird.draw(load 1.00) (= ref row's last "
        "cell) for continuity; then mid + FULLY COVERED. Rows ordered by "
        "visibility: V5 (lead) -> V4 -> V2 -> V1 -> V3 (camo). Last cell on dark + whiteout.",
        True, DIM), (pad_out, 46))

    y = title_h

    def cell_label(txt, x, yy, col=WLBL):
        sheet.blit(fcell.render(txt, True, col), (x + 4, yy))

    # ── reference row ──
    sheet.blit(frow.render("CURRENT - shipped", True, GOLD), (pad_out, y + 14))
    sheet.blit(fnote.render("(stops here, face readable)", True, DIM),
               (pad_out, y + 36))
    cx = label_w + pad_out
    for i, ld in enumerate(ref_loads):
        cell, _ = render_reference(ld)
        panel = on_panel(cell, neutral_panel)
        sheet.blit(panel, (cx, y + 18))
        pygame.draw.rect(sheet, (90, 104, 130),
                         (cx - 1, y + 17, cell_w + 2, cell_h + 2), 1)
        cell_label(f"load {ld:.2f}", cx, y)
        cx += cell_w + gap
    y += row_h + gap + 16

    # ── version rows ──
    for name, note, fn, vidx, glaze in VERSIONS:
        # wrap the label
        sheet.blit(frow.render(name.split(" (")[0], True, GOLD), (pad_out, y + 12))
        if " (" in name:
            sheet.blit(fnote.render("(" + name.split(" (")[1], True, DIM),
                       (pad_out, y + 32))
        # note, wrapped to two lines
        words = note.split(" ")
        line1, line2 = "", ""
        for wword in words:
            if len(line1) < 30:
                line1 += wword + " "
            else:
                line2 += wword + " "
        sheet.blit(fnote.render(line1.strip(), True, DIM), (pad_out, y + 54))
        sheet.blit(fnote.render(line2.strip(), True, DIM), (pad_out, y + 70))

        cx = label_w + pad_out
        # Continuity lock: cell 1 is the REAL shipped Bird.draw(load=1.0),
        # byte-identical to the reference row's last cell, so the extension
        # reads as one accumulation curve rather than a separate look.
        ref_cell, _ = render_reference(1.0)
        panel = on_panel(ref_cell, neutral_panel)
        sheet.blit(panel, (cx, y + 18))
        pygame.draw.rect(sheet, (90, 104, 130),
                         (cx - 1, y + 17, cell_w + 2, cell_h + 2), 1)
        cell_label("current max (load 1.00)", cx, y)
        cx += cell_w + gap
        # then the single mid-extension step (dark panel)
        for sname, extra in EXT_STEPS[:1]:
            cell, _ = render_cell(fn, extra, vidx, glaze_red=glaze)
            panel = on_panel(cell, neutral_panel)
            sheet.blit(panel, (cx, y + 18))
            pygame.draw.rect(sheet, (90, 104, 130),
                             (cx - 1, y + 17, cell_w + 2, cell_h + 2), 1)
            cell_label(sname, cx, y)
            cx += cell_w + gap
        # fully covered on TWO panels
        full_cell, _ = render_cell(fn, 1.0, vidx, glaze_red=glaze)
        dark = on_panel(full_cell.copy(), neutral_panel)
        sheet.blit(dark, (cx, y + 18))
        pygame.draw.rect(sheet, (120, 140, 170),
                         (cx - 1, y + 17, cell_w + 2, cell_h + 2), 1)
        cell_label("FULLY COVERED / dark", cx, y, GOLD)
        cx += cell_w + gap
        white = on_panel(full_cell.copy(), whiteout_panel)
        sheet.blit(white, (cx, y + 18))
        pygame.draw.rect(sheet, (120, 140, 170),
                         (cx - 1, y + 17, cell_w + 2, cell_h + 2), 1)
        cell_label("FULLY COVERED / whiteout", cx, y, GOLD)

        y += row_h + gap + 22

    out = os.path.join(OUT_DIR, "round_2.png")
    pygame.image.save(sheet, out)
    print(f"saved {out}  ({sheet_w}x{sheet_h})")


if __name__ == "__main__":
    main()
