"""THEME C — "LAST LIGHT ON THE PASS": main-menu candidate `first-light`, round 2.

Standalone review renderer. Imports the live game modules READ-ONLY (sky,
biome, parrot, store_data, store_hub primitives) and writes PNGs under
docs/menu-v2/first-light/. Nothing here edits game/*.py.

THE PICTURE
    The top of the world at the moment the sun leaves it. A low sun sits just
    off the far peaks on the right and every landform is contre-jour: ridges
    are silhouettes wearing incandescent rims, and the LIT AIR between them —
    not any surface — is the brightest thing in frame. Lit air always is; that
    value order is the whole difference between a backlit painting and a
    gradient with mountains on it. The only warm thing left at ground level is
    the trailhead lamp, and the plate that lamp lights is START.

CONSTRUCTION (why it does not look cheap)
    Everything is authored at SS=2 (720x1280) and smoothscaled down ONCE, so
    near-horizontal ridgelines, hairline rims and 12px enamel type resolve as
    anti-aliased edges instead of stair-steps. Every fill is a multi-stop ramp;
    there are no two-stop lerps and no flat fills outside the deliberately flat
    near-black foreground. The primitives are store_hub's, vendored by import
    rather than re-typed, so this shares one DNA with the shipped store.

    Warm bloom uses capped_glow (BLEND_RGBA_MAX rings), never soft_glow: an
    additive stack over the cyan day sky is a white-out engine.

PHASE
    The landscape is baked per PHASE BUCKET (8, lazily, LRU-capped) and two
    adjacent buckets cross-fade in one alpha blit — the pattern the project
    already uses for the sky and the floor strip. A single neutral master
    tinted by one BLEND_RGBA_MULT pass was tried first per the brief and
    rejected: see LIGHT_KF's note. The sun stays in frame at every phase and
    only changes character — gold, then coral, then a small cool moon — so the
    screen is never "the day version" or "the night version", it is always the
    same place at the same dramatic moment.

Both build targets safe: pure pygame, no numpy, no mixer, no per-frame
per-pixel loops.
"""
import math
import os
import random
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((360, 640))

from collections import OrderedDict  # noqa: E402

from game import biome as _biome  # noqa: E402
from game import parrot, sky_designs, store_data  # noqa: E402
from game.config import GROUND_Y, H, PARCEL_Y_OFFSET, W  # noqa: E402
from game.draw import lerp_color  # noqa: E402
from game.store_hub import (  # noqa: E402
    DH, DW, GOLD_A_STOPS, SS, bevel_rim, capped_glow,
    contact_shadow, downscale, drop_shadow, font, gold_rule, gradient_text,
    lerp_stops, m, plain_text, top_sheen, vgrad_stops,
)

OUT = os.path.join(_ROOT, "docs", "menu-v2", "first-light")

PHASES = [("day", 0.12), ("golden", 0.27), ("plum", 0.47), ("night", 0.70)]


# =============================================================================
# Light rig — the one thing that changes with phase.
# =============================================================================
# Per-phase keyframes for EVERY light-dependent colour in the scene. A single
# neutral master multiplied by a per-bucket tint (the cheaper option in the
# brief) cannot express this table: the sun has to become a small cool moon
# while the snow stays warm-lit, and the rosy alpenglow has to appear only
# between golden and plum. A global multiply can only scale all three together,
# so it turns the moon into a dim sun and the alpenglow into grey. Baking 8
# buckets buys those two character changes for ~3.6 MB of LRU.
LIGHT_KF = [
    (0.12, dict(  # cyan day
        sun_r=19.0, sun_core=(255, 253, 243), sun_edge=(255, 231, 176),
        halo=(255, 236, 192), halo_a=175.0, halo_r=104.0, moon=0.0,
        shaft=(255, 248, 226), shaft_a=52.0,
        haze=(247, 249, 248), haze_a=236.0,
        far=(178, 192, 212), far_lo=(138, 156, 186),
        alpen=(255, 216, 200), alpen_a=26.0,
        mid=(74, 92, 128), mid_lo=(44, 58, 90), mid_rim=(255, 244, 214),
        mid_rim_a=180.0,
        snow_hi=(216, 224, 230), snow_mid=(190, 204, 222),
        snow_lo=(152, 172, 204), snow_rim=(255, 248, 226), snow_rim_a=225.0,
        sparkle_a=130.0, rock=(16, 18, 26), bounce=(78, 70, 60), bounce_a=54.0,
        lamp_a=86.0, lamp_pool=64.0, drift=(250, 250, 246), drift_a=120.0,
        pip_dark=0.42, pip_rim=(255, 246, 220), pip_rim_a=210.0,
    )),
    (0.235, dict(  # the sky turns; the air goes warm before the snow does
        sun_r=20.0, sun_core=(255, 250, 226), sun_edge=(255, 206, 138),
        halo=(255, 200, 130), halo_a=195.0, halo_r=122.0, moon=0.0,
        shaft=(255, 226, 178), shaft_a=68.0,
        haze=(255, 240, 220), haze_a=232.0,
        far=(192, 188, 202), far_lo=(148, 150, 178),
        alpen=(255, 200, 176), alpen_a=74.0,
        mid=(72, 76, 116), mid_lo=(42, 46, 82), mid_rim=(255, 218, 162),
        mid_rim_a=195.0,
        snow_hi=(224, 214, 200), snow_mid=(194, 194, 208),
        snow_lo=(152, 162, 194), snow_rim=(255, 236, 194), snow_rim_a=235.0,
        sparkle_a=126.0, rock=(17, 17, 25), bounce=(96, 74, 52), bounce_a=64.0,
        lamp_a=110.0, lamp_pool=80.0, drift=(255, 244, 226), drift_a=126.0,
        pip_dark=0.44, pip_rim=(255, 226, 176), pip_rim_a=225.0,
    )),
    (0.30, dict(  # golden hour — coral sky, hot rims
        sun_r=21.0, sun_core=(255, 246, 216), sun_edge=(255, 178, 108),
        halo=(255, 166, 100), halo_a=205.0, halo_r=136.0, moon=0.0,
        shaft=(255, 202, 142), shaft_a=80.0,
        haze=(255, 232, 208), haze_a=230.0,
        far=(198, 176, 190), far_lo=(150, 138, 172),
        alpen=(255, 182, 154), alpen_a=118.0,
        mid=(64, 56, 100), mid_lo=(36, 32, 66), mid_rim=(255, 196, 132),
        mid_rim_a=205.0,
        snow_hi=(222, 204, 180), snow_mid=(188, 178, 194),
        snow_lo=(146, 148, 186), snow_rim=(255, 222, 172), snow_rim_a=240.0,
        sparkle_a=118.0, rock=(18, 16, 24), bounce=(108, 74, 46), bounce_a=72.0,
        lamp_a=132.0, lamp_pool=88.0, drift=(255, 236, 210), drift_a=130.0,
        pip_dark=0.46, pip_rim=(255, 210, 152), pip_rim_a=235.0,
    )),
    (0.40, dict(  # the fire minute
        sun_r=21.0, sun_core=(255, 234, 206), sun_edge=(255, 146, 116),
        halo=(250, 128, 112), halo_a=200.0, halo_r=142.0, moon=0.0,
        shaft=(255, 166, 146), shaft_a=78.0,
        haze=(255, 214, 198), haze_a=224.0,
        far=(186, 152, 176), far_lo=(138, 116, 158),
        alpen=(255, 158, 142), alpen_a=142.0,
        mid=(54, 42, 84), mid_lo=(30, 24, 58), mid_rim=(255, 158, 124),
        mid_rim_a=205.0,
        snow_hi=(246, 202, 186), snow_mid=(196, 170, 192),
        snow_lo=(132, 128, 172), snow_rim=(255, 190, 156), snow_rim_a=238.0,
        sparkle_a=104.0, rock=(19, 15, 23), bounce=(112, 66, 48), bounce_a=76.0,
        lamp_a=160.0, lamp_pool=98.0, drift=(255, 222, 202), drift_a=126.0,
        pip_dark=0.48, pip_rim=(255, 176, 138), pip_rim_a=238.0,
    )),
    (0.47, dict(  # plum — alpenglow at its most specific
        sun_r=19.0, sun_core=(255, 224, 200), sun_edge=(255, 128, 112),
        halo=(238, 108, 108), halo_a=196.0, halo_r=140.0, moon=0.0,
        shaft=(252, 146, 138), shaft_a=72.0,
        haze=(255, 198, 190), haze_a=216.0,
        far=(164, 128, 162), far_lo=(118, 96, 144),
        alpen=(255, 146, 138), alpen_a=150.0,
        mid=(44, 36, 76), mid_lo=(24, 20, 52), mid_rim=(252, 136, 116),
        mid_rim_a=200.0,
        snow_hi=(230, 168, 162), snow_mid=(178, 142, 176),
        snow_lo=(122, 118, 164), snow_rim=(255, 164, 142), snow_rim_a=232.0,
        sparkle_a=92.0, rock=(18, 15, 24), bounce=(104, 58, 52), bounce_a=74.0,
        lamp_a=182.0, lamp_pool=108.0, drift=(248, 198, 194), drift_a=120.0,
        pip_dark=0.54, pip_rim=(255, 150, 132), pip_rim_a=236.0,
    )),
    (0.56, dict(  # the disc has become a moon
        sun_r=12.0, sun_core=(246, 250, 255), sun_edge=(206, 220, 246),
        halo=(158, 180, 226), halo_a=132.0, halo_r=86.0, moon=1.0,
        shaft=(184, 202, 240), shaft_a=40.0,
        haze=(178, 196, 226), haze_a=226.0,
        far=(96, 104, 142), far_lo=(66, 74, 114),
        alpen=(160, 132, 168), alpen_a=52.0,
        mid=(30, 32, 62), mid_lo=(18, 20, 44), mid_rim=(196, 212, 244),
        mid_rim_a=150.0,
        snow_hi=(156, 168, 198), snow_mid=(134, 146, 182),
        snow_lo=(110, 124, 164), snow_rim=(214, 228, 252), snow_rim_a=200.0,
        sparkle_a=110.0, rock=(14, 15, 22), bounce=(70, 66, 78), bounce_a=54.0,
        lamp_a=210.0, lamp_pool=126.0, drift=(206, 220, 244), drift_a=104.0,
        pip_dark=0.72, pip_rim=(212, 228, 255), pip_rim_a=210.0,
    )),
    (0.82, dict(  # deep night, same place, same moment
        sun_r=12.0, sun_core=(248, 251, 255), sun_edge=(208, 222, 248),
        halo=(156, 178, 226), halo_a=130.0, halo_r=86.0, moon=1.0,
        shaft=(184, 202, 240), shaft_a=40.0,
        haze=(178, 196, 226), haze_a=226.0,
        far=(96, 104, 142), far_lo=(66, 74, 114),
        alpen=(160, 132, 168), alpen_a=50.0,
        mid=(30, 32, 62), mid_lo=(18, 20, 44), mid_rim=(196, 212, 244),
        mid_rim_a=150.0,
        snow_hi=(156, 168, 198), snow_mid=(134, 146, 182),
        snow_lo=(110, 124, 164), snow_rim=(214, 228, 252), snow_rim_a=200.0,
        sparkle_a=110.0, rock=(14, 15, 22), bounce=(70, 66, 78), bounce_a=54.0,
        lamp_a=210.0, lamp_pool=126.0, drift=(206, 220, 244), drift_a=104.0,
        pip_dark=0.72, pip_rim=(212, 228, 255), pip_rim_a=210.0,
    )),
    (0.92, dict(  # first light coming back round
        sun_r=18.0, sun_core=(255, 244, 224), sun_edge=(255, 186, 150),
        halo=(255, 178, 148), halo_a=180.0, halo_r=120.0, moon=0.0,
        shaft=(255, 214, 186), shaft_a=64.0,
        haze=(255, 228, 214), haze_a=228.0,
        far=(186, 172, 192), far_lo=(142, 136, 174),
        alpen=(255, 190, 172), alpen_a=104.0,
        mid=(62, 62, 104), mid_lo=(34, 36, 72), mid_rim=(255, 202, 168),
        mid_rim_a=190.0,
        snow_hi=(248, 228, 214), snow_mid=(200, 194, 208),
        snow_lo=(130, 142, 182), snow_rim=(255, 226, 196), snow_rim_a=230.0,
        sparkle_a=120.0, rock=(17, 16, 25), bounce=(96, 70, 56), bounce_a=62.0,
        lamp_a=150.0, lamp_pool=94.0, drift=(255, 238, 226), drift_a=122.0,
        pip_dark=0.50, pip_rim=(255, 216, 180), pip_rim_a=230.0,
    )),
]


def _blend_light(a, b, t):
    out = {}
    for k, va in a.items():
        vb = b[k]
        out[k] = lerp_color(va, vb, t) if isinstance(va, tuple) else va + (vb - va) * t
    return out


def light_for_phase(phase):
    """Sample the light rig at `phase`, wrapping across midnight so the cycle
    is seamless (the sky table wraps the same way)."""
    p = phase % 1.0
    ks = LIGHT_KF
    if p <= ks[0][0] or p >= ks[-1][0]:
        p0, a = ks[-1]
        p1, b = ks[0]
        span = (1.0 - p0) + p1
        d = (p - p0) if p >= p0 else (p + 1.0 - p0)
        return _blend_light(a, b, d / span)
    for i in range(len(ks) - 1):
        if ks[i][0] <= p <= ks[i + 1][0]:
            p0, a = ks[i]
            p1, b = ks[i + 1]
            return _blend_light(a, b, (p - p0) / (p1 - p0))
    return dict(ks[0][1])


# =============================================================================
# Composition — logical 360x640 coordinates, scaled through m() at draw time.
# =============================================================================
SUN = (300.0, 262.0)          # in frame at EVERY phase; only its character moves

# Six planes of aerial perspective. Each ridge is a control polyline; the
# fractal detail and the haze band that separates it from the next plane are
# added by the builder.
FAR_CTRL = [(0, 268), (46, 236), (92, 258), (134, 230), (186, 248),
            (232, 268), (286, 288), (330, 296), (360, 302)]
MID_A_CTRL = [(0, 300), (58, 284), (118, 304), (178, 292), (238, 312),
              (300, 322), (360, 328)]
MID_B_CTRL = [(0, 332), (52, 322), (112, 340), (168, 330), (226, 350),
              (292, 360), (360, 356)]
# The near ridge: a summit on the left falling to the COL at x~268 — the pass
# the whole screen is named for, and the notch the shafts rake through.
NEAR_CTRL = [(0, 366), (40, 352), (88, 336), (130, 328), (176, 342),
             (224, 362), (268, 384), (310, 372), (360, 360)]
# Where wind strips the snow off and bare rock starts. Kept ABOVE y=424
# everywhere so the START plate at y=433 can never touch snow.
SNOWLINE_CTRL = [(0, 422), (60, 418), (120, 410), (190, 404), (250, 412),
                 (310, 402), (360, 408)]

# Plane 6: a deliberately flat, empty near-black silhouette. No ornament here —
# it exists to stop the eye being dragged down off the hero.
FORE_CTRL = [(0, 546), (26, 566), (48, 600), (120, 596), (180, 602),
             (250, 597), (312, 599), (330, 560), (360, 542)]

# ── tap targets (logical px) ────────────────────────────────────────────────
START_RECT = pygame.Rect(66, 433, 236, 74)
PROFILE_RECT = pygame.Rect(24, 370, 108, 48)
SIGN_RECTS = [
    ("STORE", pygame.Rect(50, 528, 81, 56)),
    ("TOP 10", pygame.Rect(140, 528, 81, 56)),
    ("SETTINGS", pygame.Rect(230, 528, 81, 56)),
]
POST_X = 36.0                 # the weathered timber waypost
LAMP = (36.0, 336.0)          # the only light SOURCE the player can tap toward

PIP_POS = (232, 198)
PIP_TILT = 11.0
PIP_TARGET = 88
# The menu portrait hangs the parcel a touch lower than the in-game rig: at the
# game's offset it sits entirely inside the hull, and a hull is all a
# backlit silhouette shows.
PARCEL_DROP = 8

ENAMEL_HI = (34, 38, 50)
ENAMEL_LO = (18, 20, 29)
ENAMEL_EDGE = (196, 158, 96)
CREAM = (240, 233, 218)
IRON_HI = (30, 30, 38)
IRON_LO = (11, 12, 17)
INK = (10, 11, 16)


# =============================================================================
# Small primitives that store_hub does not carry.
# =============================================================================
def hgrad_stops(w, h, stops, alpha=255):
    """Horizontal multi-stop ramp — the sun-ward gradient across the snowfield.
    store_hub only ships the vertical form."""
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    for x in range(w):
        c = lerp_stops(stops, x / max(1, w - 1))
        pygame.draw.line(surf, (*c, alpha), (x, 0), (x, h - 1))
    return surf


def scratch(surf):
    """A transparent scratch the size of `surf`.

    pygame's draw functions WRITE the colour+alpha they are given instead of
    compositing it, so a semi-transparent shape drawn straight onto a layer
    punches a hole in whatever is under it (and on an opaque surface it is
    drawn at full strength, alpha ignored). Everything soft in this scene —
    rims, ramps, sastrugi, shafts, hairlines — is therefore drawn on one of
    these and BLITTED, which is the only path that actually blends."""
    return pygame.Surface(surf.get_size(), pygame.SRCALPHA)


def mask_min(layer, mask):
    """Clip `layer` to `mask`'s alpha. BLEND_RGBA_MIN keeps the layer's colour
    and takes the smaller alpha, which is the cheap stencil pygame gives us."""
    layer.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return layer


def _value_noise(n, cells, seed, amp):
    rnd = random.Random(seed)
    vals = [rnd.uniform(-1.0, 1.0) for _ in range(cells + 2)]
    out = []
    for i in range(n):
        t = i / max(1, n - 1) * cells
        k = int(t)
        f = t - k
        f = f * f * (3 - 2 * f)
        out.append((vals[k] * (1 - f) + vals[k + 1] * f) * amp)
    return out


def ridge_ys(controls, seed, octaves=((6, 4.2), (17, 1.9), (43, 0.85))):
    """A ridgeline as one y-per-device-column array. Arrays (not polygons) are
    the load-bearing choice: silhouette fill, haze masks, rim lighting, snow
    stencils, sparkle placement and the trail all read the SAME array, so every
    layer lines up to the pixel with no re-derivation."""
    xs = [m(c[0]) for c in controls]
    ys = [m(c[1]) for c in controls]
    out = []
    seg = 0
    for x in range(DW):
        while seg < len(xs) - 2 and x > xs[seg + 1]:
            seg += 1
        x0, x1 = xs[seg], xs[seg + 1]
        t = 0.0 if x1 == x0 else (x - x0) / (x1 - x0)
        t = max(0.0, min(1.0, t))
        t = t * t * (3 - 2 * t)
        out.append(ys[seg] * (1 - t) + ys[seg + 1] * t)
    for cells, amp in octaves:
        for i, v in enumerate(_value_noise(DW, cells, seed + cells, m(amp))):
            out[i] += v
    return out


def ys_poly(ys, bottom, step=2):
    pts = [(x, ys[x]) for x in range(0, DW, step)]
    pts.append((DW - 1, ys[-1]))
    pts += [(DW - 1, bottom), (0, bottom)]
    return pts


def ys_mask(ys, bottom=None):
    """White stencil covering everything below a ridgeline."""
    mask = pygame.Surface((DW, DH), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255),
                        ys_poly(ys, DH if bottom is None else bottom))
    return mask


def band_mask(top_ys, bot_ys, step=2):
    """White stencil for the field between two ridgelines (the snowfield)."""
    mask = pygame.Surface((DW, DH), pygame.SRCALPHA)
    pts = [(x, top_ys[x]) for x in range(0, DW, step)]
    pts.append((DW - 1, top_ys[-1]))
    pts += [(x, bot_ys[x]) for x in range(DW - 1, 0, -step)]
    pygame.draw.polygon(mask, (255, 255, 255, 255), pts)
    return mask


def sun_facing(ys, x, sun_dev, step=None):
    """cos(angle) between the ridge's outward normal at column x and the
    direction to the sun. This one number drives every rim, every alpenglow
    face and every sastrugi highlight, which is why the light reads as ONE
    light instead of a set of decorated edges."""
    step = step or m(3)
    x0 = max(0, min(DW - 1, x))
    x1 = max(0, min(DW - 1, x + step))
    dx = float(x1 - x0) or 1.0
    dy = ys[x1] - ys[x0]
    L = math.hypot(dx, dy) or 1.0
    nx, ny = dy / L, -dx / L
    sx, sy = sun_dev[0] - x0, sun_dev[1] - ys[x0]
    SL = math.hypot(sx, sy) or 1.0
    return nx * sx / SL + ny * sy / SL


def rim_edge(surf, ys, sun_dev, col, peak, width, power=1.5, step=None,
             bloom=True):
    """The incandescent contour a backlit ridge wears. Alpha tracks sun_facing,
    so the rim is hot where the slope turns into the light and dies out where
    it turns away — the thing that separates a lit edge from a drawn outline."""
    step = step or m(3)
    lay = scratch(surf)
    for x in range(0, DW - step, step):
        f = sun_facing(ys, x, sun_dev, step)
        if f <= 0:
            continue
        a = int(peak * f ** power)
        if a <= 2:
            continue
        p0 = (x, ys[x])
        p1 = (x + step, ys[x + step])
        if bloom:
            pygame.draw.line(lay, (*col, a // 5), p0, p1, width * 5)
            pygame.draw.line(lay, (*col, a // 3), p0, p1, width * 2)
        pygame.draw.line(lay, (*col, a), p0, p1, width)
    surf.blit(lay, (0, 0))


def crest_ramp(surf, ys, depth, col, peak, steps=9, power=1.7, sun_dev=None,
               seg=None, facing_power=0.9, up=False):
    """A colour that fades away from a ridgeline over `depth` px — alpenglow on
    snow faces, warm bounce under a rock lip, brightening beneath a crest.
    Drawn as quads (not per-pixel), and optionally modulated by sun_facing so
    e.g. alpenglow lands ONLY on the faces actually turned to the light."""
    seg = seg or m(8)
    sign = -1.0 if up else 1.0
    lay = scratch(surf)
    for k in range(steps):
        t0 = k / steps
        t1 = (k + 1) / steps
        a0 = peak * (1.0 - t0) ** power
        if a0 <= 1:
            continue
        x = 0
        while x < DW - 1:
            x2 = min(DW - 1, x + seg)
            f = 1.0
            if sun_dev is not None:
                f = max(0.0, sun_facing(ys, x, sun_dev)) ** facing_power
            a = int(a0 * f)
            if a > 1:
                pygame.draw.polygon(lay, (*col, a), [
                    (x, ys[x] + sign * t0 * depth),
                    (x2, ys[x2] + sign * t0 * depth),
                    (x2, ys[x2] + sign * t1 * depth),
                    (x, ys[x] + sign * t1 * depth)])
            x = x2
    surf.blit(lay, (0, 0))


def haze_band(surf, y_top, y_bot, col, peak_a, sun_x, spread, gamma=1.0):
    """The luminous air that separates one plane from the next. Drawn OVER the
    plane rather than fading the plane out, because that is what real distance
    does — it adds light in front of a silhouette, it does not grey it. Two
    cheap 1-D passes (vertical colour+alpha, then a horizontal falloff toward
    the sun) stand in for a 2-D field."""
    y_top = int(y_top)
    h = int(y_bot) - y_top
    if h <= 0:
        return
    band = pygame.Surface((DW, h), pygame.SRCALPHA)
    for y in range(h):
        t = y / max(1, h - 1)
        a = int(peak_a * (math.sin(t * math.pi) ** gamma))
        if a <= 0:
            continue
        pygame.draw.line(band, (*col, a), (0, y), (DW - 1, y))
    falloff = pygame.Surface((DW, h), pygame.SRCALPHA)
    for x in range(DW):
        d = abs(x - sun_x) / spread
        a = int(255 * max(0.03, 1.0 - d ** 1.4))
        pygame.draw.line(falloff, (255, 255, 255, a), (x, 0), (x, h - 1))
    mask_min(band, falloff)
    surf.blit(band, (0, y_top))


# =============================================================================
# The scene, plane by plane.
# =============================================================================
def _sky_ss(phase):
    """The LIVE sky, at 1x so paint_sky's star sprinkle keeps its authored size,
    then nearest-upscaled into the SS canvas. Nearest up + box down is an exact
    round trip for the stars and lossless for a gradient, so the sky pays no
    quality tax for being composed at SS with everything else."""
    sky = pygame.Surface((W, H))
    if not sky_designs.render_active(sky, W, H, GROUND_Y,
                                     _biome.palette_for_phase(phase), phase):
        sky.fill((120, 170, 210))
    return pygame.transform.scale(sky, (DW, DH))


def _draw_sun(surf, L, sun_dev):
    """The key light, in frame. Its halo is capped_glow, never soft_glow: an
    additive warm stack over the cyan day sky sums past 255 in every channel
    and blows the top third of the screen to white."""
    r = int(m(L["sun_r"]))
    capped_glow(surf, int(sun_dev[0]), int(sun_dev[1]), int(m(L["halo_r"])),
                tuple(int(v) for v in L["halo"]), int(L["halo_a"]), layers=13)
    capped_glow(surf, int(sun_dev[0]), int(sun_dev[1]), int(m(L["halo_r"] * 0.42)),
                tuple(int(v) for v in L["sun_edge"]), int(L["halo_a"] * 0.85),
                layers=10)
    disc = pygame.Surface((r * 2 + m(4), r * 2 + m(4)), pygame.SRCALPHA)
    c = r + m(2)
    for i in range(r, 0, -1):
        t = (i / r) ** 1.5
        col = lerp_color(L["sun_core"], L["sun_edge"], t)
        pygame.draw.circle(disc, (*col, 255), (c, c), i)
    if L["moon"] > 0.5:
        # Same disc, cool and small: a shallow terminator + two maria so it
        # reads as a moon rather than a dimmed sun.
        mn = scratch(disc)
        pygame.draw.circle(mn, (*lerp_color(L["sun_edge"], (150, 168, 200), 0.5),
                                int(150 * L["moon"])),
                           (c - int(r * 0.34), c + int(r * 0.10)), int(r * 0.86))
        pygame.draw.circle(mn, (*lerp_color(L["sun_edge"], (168, 184, 214), 0.6), 120),
                           (c + int(r * 0.22), c - int(r * 0.26)), max(1, int(r * 0.20)))
        pygame.draw.circle(mn, (*lerp_color(L["sun_edge"], (168, 184, 214), 0.6), 96),
                           (c - int(r * 0.10), c + int(r * 0.34)), max(1, int(r * 0.14)))
        keep = scratch(disc)
        pygame.draw.circle(keep, (255, 255, 255, 255), (c, c), r)
        mask_min(mn, keep)
        disc.blit(mn, (0, 0))
    surf.blit(disc, (int(sun_dev[0]) - c, int(sun_dev[1]) - c))


def _draw_lenticulars(surf, L, sun_dev):
    """Three lens clouds standing over the range. They earn their place by
    being lit from BENEATH — the only hour a cloud's underside is its bright
    side — so they say the same thing about the light that everything else in
    the frame says."""
    lay = scratch(surf)
    for cx, cy, w, hh, a in ((96, 156, 74, 11, 0.72), (198, 120, 108, 13, 0.58),
                             (74, 228, 62, 9, 0.86)):
        cx, cy = m(cx), m(cy)
        w, hh = m(w), m(hh)
        for k in range(3):
            t = k / 2.0
            ww = int(w * (1.0 - 0.30 * t))
            h2 = int(hh * (1.0 - 0.34 * t))
            yy = cy - int(hh * 0.75 * t)
            top = lerp_color(L["mid"], L["haze"], 0.60 - 0.18 * t)
            pygame.draw.ellipse(lay, (*top, int(96 * a * (1 - 0.18 * t))),
                                (cx - ww, yy - h2, ww * 2, h2 * 2))
            pygame.draw.arc(lay, (*L["snow_rim"], int(150 * a)),
                            (cx - ww, yy - h2, ww * 2, h2 * 2),
                            math.radians(188), math.radians(352), max(1, m(1.2)))
            pygame.draw.arc(lay, (*L["haze"], int(70 * a)),
                            (cx - ww, yy - h2 - m(1), ww * 2, h2 * 2),
                            math.radians(14), math.radians(166), max(1, m(0.8)))
    surf.blit(lay, (0, 0))


def _draw_shafts(surf, L, sun_dev, near_ys, mid_ys):
    """Crepuscular shafts fanning out of the pass. Built once as a soft fan,
    then stencilled: full strength over open sky, half over the mid ridges
    (there IS air in front of them), nothing over the near ridge, which is too
    close to the eye to carry a visible shaft. That stencil is what makes them
    read as light coming THROUGH the notches."""
    fan = pygame.Surface((DW, DH), pygame.SRCALPHA)
    ray = pygame.Surface((DW, DH), pygame.SRCALPHA)
    rnd = random.Random(9021)
    base = math.radians(118.0)
    for k in range(15):
        ang = base + math.radians(-46.0 + 92.0 * (k / 14.0)) * 0.62
        ang += math.radians(rnd.uniform(-2.6, 2.6))
        halfw = math.radians(rnd.uniform(0.9, 2.4))
        power = rnd.uniform(0.45, 1.0)
        length = m(rnd.uniform(300, 480))
        ray.fill((0, 0, 0, 0))
        segs = 9
        for s in range(segs):
            t0 = s / segs
            t1 = (s + 1) / segs
            a = int(L["shaft_a"] * power * (1.0 - t0) ** 1.25)
            if a <= 1:
                continue
            for spread, alpha in ((3.4, a // 7), (2.1, a // 3), (1.0, a)):
                if alpha <= 1:
                    continue
                pygame.draw.polygon(ray, (*tuple(int(v) for v in L["shaft"]), alpha), [
                    (sun_dev[0] + math.cos(ang - halfw * spread) * length * t0,
                     sun_dev[1] + math.sin(ang - halfw * spread) * length * t0),
                    (sun_dev[0] + math.cos(ang + halfw * spread) * length * t0,
                     sun_dev[1] + math.sin(ang + halfw * spread) * length * t0),
                    (sun_dev[0] + math.cos(ang + halfw * spread) * length * t1,
                     sun_dev[1] + math.sin(ang + halfw * spread) * length * t1),
                    (sun_dev[0] + math.cos(ang - halfw * spread) * length * t0,
                     sun_dev[1] + math.sin(ang - halfw * spread) * length * t0)])
        fan.blit(ray, (0, 0), special_flags=pygame.BLEND_RGBA_MAX)
    stencil = pygame.Surface((DW, DH), pygame.SRCALPHA)
    stencil.fill((255, 255, 255, 255))
    pygame.draw.polygon(stencil, (255, 255, 255, 132), ys_poly(mid_ys, DH))
    pygame.draw.polygon(stencil, (255, 255, 255, 0), ys_poly(near_ys, DH))
    mask_min(fan, stencil)
    surf.blit(fan, (0, 0))


def _draw_far_range(surf, L, sun_dev, ys):
    """Plane 2 — the far snow range: high value, low saturation, and the ONLY
    plane that takes alpenglow, on its sun-facing snow faces alone. That
    specificity is what makes it read as alpenglow and not as a sunset wash."""
    layer = pygame.Surface((DW, DH), pygame.SRCALPHA)
    body = vgrad_stops(DW, DH, 0, [(0.0, L["far"]), (0.16, L["far"]),
                                   (0.36, L["far_lo"]), (1.0, L["far_lo"])], 255)
    mask_min(body, ys_mask(ys))
    layer.blit(body, (0, 0))
    crest_ramp(layer, ys, m(30), L["alpen"], L["alpen_a"], steps=9, power=1.5,
               sun_dev=sun_dev, facing_power=1.1)
    crest_ramp(layer, ys, m(9), lerp_color(L["snow_hi"], (255, 255, 255), 0.25),
               110, steps=5, power=1.2, sun_dev=sun_dev, facing_power=1.4)
    rim_edge(layer, ys, sun_dev, tuple(int(v) for v in L["snow_rim"]),
             int(L["snow_rim_a"] * 0.75), max(1, m(0.8)), power=1.7)
    surf.blit(layer, (0, 0))


def _draw_mid_ridge(surf, L, sun_dev, ys, depth_t, rim_scale=1.0):
    """Plane 3 — cool blue-violet shadow masses with a thin warm sun-side rim.
    `depth_t` walks the body colour toward the far plane so the two mid ridges
    are not the same silhouette twice."""
    layer = pygame.Surface((DW, DH), pygame.SRCALPHA)
    top = lerp_color(L["mid"], L["far"], depth_t * 0.42)
    bot = lerp_color(L["mid_lo"], L["mid"], depth_t * 0.30)
    body = vgrad_stops(DW, DH, 0, [(0.0, top), (0.22, top), (0.55, bot),
                                   (1.0, bot)], 255)
    mask_min(body, ys_mask(ys))
    layer.blit(body, (0, 0))
    crest_ramp(layer, ys, m(14), lerp_color(L["mid_rim"], L["mid"], 0.55), 96,
               steps=6, power=1.6, sun_dev=sun_dev, facing_power=1.2)
    rim_edge(layer, ys, sun_dev, tuple(int(v) for v in L["mid_rim"]),
             int(L["mid_rim_a"] * rim_scale), max(1, m(0.9)), power=1.4)
    surf.blit(layer, (0, 0))


def _sastrugi(layer, L, sun_dev, crest, snow, seed=771):
    """Wind-carved scalloping on the snow. Real sastrugi are furrows cut
    parallel to the wind with a hard upwind lip and a soft lee slope, so each
    scallop is a bright arc with its shadow tucked under it — never a symmetric
    ripple."""
    rnd = random.Random(seed)
    lay = scratch(layer)
    for row in range(5):
        rt = 0.06 + row * 0.19
        for _ in range(26 - row * 3):
            x = rnd.randrange(m(4), DW - m(4))
            top = crest[x]
            bot = snow[x]
            if bot - top < m(10):
                continue
            y = top + (bot - top) * (rt + rnd.uniform(-0.045, 0.045))
            w = m(rnd.uniform(8, 26)) * (1.0 - row * 0.10)
            h = max(m(1.4), w * rnd.uniform(0.16, 0.30))
            f = max(0.0, sun_facing(crest, x, sun_dev))
            hi = int((60 + 120 * f) * (1.0 - row * 0.12))
            rect = pygame.Rect(int(x - w / 2), int(y - h / 2), int(w), int(h))
            pygame.draw.arc(lay, (*L["snow_hi"], min(255, hi)),
                            rect, math.radians(18), math.radians(162),
                            max(1, m(0.8)))
            sh = rect.move(int(m(1.2)), int(h * 0.55))
            pygame.draw.arc(lay, (*L["snow_lo"], int(hi * 0.62)),
                            sh, math.radians(196), math.radians(344),
                            max(1, m(0.8)))
    layer.blit(lay, (0, 0))


def _trail_to_the_pass(layer, L, crest, snow):
    """A faint switchback climbing the snowfield to the col. Landscape, not
    ornament: it is the reason a trailhead is standing at the bottom of the
    frame at all."""
    pts = [(m(60), 0.80), (m(112), 0.58), (m(150), 0.70), (m(196), 0.44),
           (m(228), 0.52), (m(262), 0.22), (m(268), 0.05)]
    path = []
    for x, t in pts:
        x = int(max(0, min(DW - 1, x)))
        path.append((x, crest[x] + (snow[x] - crest[x]) * t))
    lay = scratch(layer)
    for i in range(len(path) - 1):
        pygame.draw.line(lay, (*L["snow_lo"], 92), path[i], path[i + 1],
                         max(1, m(1.1)))
        pygame.draw.line(lay, (*L["snow_hi"], 60),
                         (path[i][0], path[i][1] - m(1.0)),
                         (path[i + 1][0], path[i + 1][1] - m(1.0)),
                         max(1, m(0.6)))
    layer.blit(lay, (0, 0))


def _draw_near_ridge(surf, L, sun_dev, crest, snow):
    """Plane 4 — the hero landform, built as TWO LARGE FIELDS so it never needs
    a rim to survive: a broad lit snowfield on the sun-facing slope (the bright
    leg, which carries the plum/night sky) meeting an opaque near-black rock
    face at a hard crest line (the dark leg, which carries day/dawn). Two-tone
    at scale, so the silhouette holds at 90x160 and at every phase."""
    layer = pygame.Surface((DW, DH), pygame.SRCALPHA)

    rock = tuple(int(v) for v in L["rock"])
    rock_body = vgrad_stops(DW, DH, 0, [
        (0.00, lerp_color(rock, (44, 44, 56), 0.55)),
        (0.10, rock),
        (0.55, lerp_color(rock, (0, 0, 0), 0.35)),
        (1.00, lerp_color(rock, (0, 0, 0), 0.55))], 255)
    mask_min(rock_body, ys_mask(crest))
    layer.blit(rock_body, (0, 0))

    facets = pygame.Surface((DW, DH), pygame.SRCALPHA)
    rnd = random.Random(4412)
    for _ in range(22):
        x = rnd.randrange(0, DW)
        y = rnd.randrange(int(m(410)), DH)
        w = m(rnd.uniform(30, 120))
        h = m(rnd.uniform(20, 80))
        v = rnd.choice((6, 9, -5, -7, 4))
        pygame.draw.polygon(facets, (max(0, rock[0] + v), max(0, rock[1] + v),
                                     max(0, rock[2] + v), 120), [
            (x, y), (x + w * rnd.uniform(0.5, 1.0), y - h * rnd.uniform(0.2, 0.8)),
            (x + w, y + h * rnd.uniform(0.3, 1.0)),
            (x + w * rnd.uniform(0.1, 0.5), y + h)])
    mask_min(facets, ys_mask(snow))
    layer.blit(facets, (0, 0))

    snow_layer = pygame.Surface((DW, DH), pygame.SRCALPHA)
    ramp = hgrad_stops(DW, DH, [(0.00, L["snow_lo"]), (0.34, L["snow_mid"]),
                                (0.74, L["snow_hi"]),
                                (1.00, lerp_color(L["snow_hi"], L["snow_rim"], 0.10))])
    snow_layer.blit(ramp, (0, 0))
    hollow = pygame.Surface((DW, DH), pygame.SRCALPHA)
    for k in range(10):
        t0 = k / 10
        a = int(36 * t0 ** 1.5)
        if a <= 1:
            continue
        x = 0
        while x < DW - 1:
            x2 = min(DW - 1, x + m(8))
            pygame.draw.polygon(hollow, (*L["snow_lo"], a), [
                (x, crest[x] + (snow[x] - crest[x]) * t0),
                (x2, crest[x2] + (snow[x2] - crest[x2]) * t0),
                (x2, crest[x2] + (snow[x2] - crest[x2]) * (t0 + 0.1)),
                (x, crest[x] + (snow[x] - crest[x]) * (t0 + 0.1))])
            x = x2
    snow_layer.blit(hollow, (0, 0))
    _sastrugi(snow_layer, L, sun_dev, crest, snow)
    _trail_to_the_pass(snow_layer, L, crest, snow)
    crest_ramp(snow_layer, crest, m(16), L["snow_rim"], 70, steps=7, power=1.5,
               sun_dev=sun_dev, facing_power=1.2)
    mask_min(snow_layer, band_mask(crest, snow))
    layer.blit(snow_layer, (0, 0))

    sparkle = pygame.Surface((DW, DH), pygame.SRCALPHA)
    rnd = random.Random(1301)
    for _ in range(150):
        x = rnd.randrange(m(3), DW - m(3))
        top, bot = crest[x], snow[x]
        if bot - top < m(12):
            continue
        y = int(rnd.uniform(top + m(4), bot - m(3)))
        f = 0.35 + 0.65 * (x / DW)
        a = int(L["sparkle_a"] * f * rnd.uniform(0.35, 1.0))
        if a <= 3:
            continue
        r = max(1, int(m(rnd.uniform(0.5, 1.2))))
        pygame.draw.circle(sparkle, (*L["snow_rim"], a), (x, y), r)
        if rnd.random() < 0.22:
            ln = int(m(rnd.uniform(2.0, 3.6)))
            pygame.draw.line(sparkle, (*L["snow_rim"], a // 2),
                             (x - ln, y), (x + ln, y), max(1, m(0.5)))
            pygame.draw.line(sparkle, (*L["snow_rim"], a // 2),
                             (x, y - ln), (x, y + ln), max(1, m(0.5)))
    layer.blit(sparkle, (0, 0))

    # The hard crest line, then the snow/rock boundary: a dark seat with a
    # warm bounce right under it. That bounce — snow throwing light back at
    # the rock — is the whole difference between "rock" and "a black shape".
    rim_edge(layer, crest, sun_dev, tuple(int(v) for v in L["snow_rim"]),
             int(L["snow_rim_a"]), max(1, m(1.0)), power=1.25)
    crest_ramp(layer, snow, m(11), L["bounce"], L["bounce_a"], steps=7,
               power=1.4, sun_dev=sun_dev, facing_power=0.5)
    crest_ramp(layer, snow, m(4), (0, 0, 0), 120, steps=4, power=1.2, up=True)
    surf.blit(layer, (0, 0))


def _draw_foreground(surf, L, ys):
    """Plane 6 — flat, empty, near-black. Ornament is withheld here on purpose:
    anything interesting in this band drags the eye down off the trailhead."""
    layer = pygame.Surface((DW, DH), pygame.SRCALPHA)
    pygame.draw.polygon(layer, (*INK, 255), ys_poly(ys, DH))
    crest_ramp(layer, ys, m(2.5), lerp_color(L["bounce"], L["snow_rim"], 0.25),
               int(L["bounce_a"] * 1.1), steps=3, power=1.0)
    surf.blit(layer, (0, 0))


def _draw_lamp_pool(surf, L):
    """The lamp's throw on the rock. Capped so a warm pool laid over the day
    sky's brightest hour cannot creep to white."""
    capped_glow(surf, int(m(LAMP[0])), int(m(LAMP[1])), int(m(46)),
                (255, 206, 138), int(L["lamp_a"]), layers=12)
    # The throw on the rock, kept BELOW the snowline: a lamp that reached the
    # snowfield would flatten the one boundary the whole layout leans on.
    pool = pygame.Surface((DW, DH), pygame.SRCALPHA)
    capped_glow(pool, int(m(122)), int(m(504)), int(m(168)),
                (255, 196, 128), int(L["lamp_pool"]), layers=12)
    g = geometry()
    mask_min(pool, ys_mask(g["snow"]))
    surf.blit(pool, (0, 0))


# =============================================================================
# Plane 5 — the trailhead. Bare timber, bare iron, plain enamel. Every bit of
# richness in this picture is in the LIGHT; none of it is allowed onto anything
# man-made, which is what keeps the lamp reading as the only made thing worth
# looking at.
# =============================================================================
def _draw_waypost(surf, L, sun_dev):
    x0, x1 = m(POST_X - 6), m(POST_X + 6)
    top, bot = m(352), m(604)
    post = vgrad_stops(x1 - x0, bot - top, 0, [
        (0.00, (46, 40, 34)), (0.35, (30, 26, 22)), (1.00, (14, 13, 12))], 255)
    surf.blit(post, (x0, top))
    grain = scratch(surf)
    for k in range(7):
        gy = top + m(14) + k * m(34)
        pygame.draw.line(grain, (8, 8, 8, 150), (x0 + m(1), gy),
                         (x1 - m(1), gy + m(2)), max(1, m(0.6)))
    surf.blit(grain, (0, 0))
    # Sun-side rim only; the lamp sits on top of this post, so its own light
    # never reaches the shaft's flank.
    lay = scratch(surf)
    pygame.draw.line(lay, (*L["snow_rim"], 165), (x1 - m(0.6), top),
                     (x1 - m(0.6), bot), max(1, m(1.0)))
    pygame.draw.line(lay, (*L["bounce"], 150), (x0 + m(0.6), top),
                     (x0 + m(0.6), bot), max(1, m(0.8)))
    surf.blit(lay, (0, 0))


def _draw_lamp(surf, L):
    """A bare storm lantern: cap, glass, base, bail. No filigree — the lamp
    earns its place by being the only warm SOURCE left on the mountain."""
    cx, cy = m(LAMP[0]), m(LAMP[1])
    hw, hh = m(9), m(13)
    capped_glow(surf, cx, cy, m(34), (255, 216, 150), 210, layers=10)
    pygame.draw.arc(surf, (28, 26, 26),
                    (cx - m(6), cy - hh - m(11), m(12), m(12)),
                    math.radians(20), math.radians(160), max(1, m(1.2)))
    pygame.draw.polygon(surf, (34, 31, 30), [
        (cx - m(10), cy - hh), (cx + m(10), cy - hh),
        (cx + m(6), cy - hh - m(6)), (cx - m(6), cy - hh - m(6))])
    glass = vgrad_stops(hw * 2, hh * 2, m(2), [
        (0.00, (255, 244, 206)), (0.35, (255, 206, 122)),
        (0.72, (255, 168, 78)), (1.00, (208, 118, 44))], 255)
    surf.blit(glass, (cx - hw, cy - hh))
    pygame.draw.rect(surf, (26, 24, 24), (cx - hw, cy - hh, hw * 2, hh * 2),
                     width=max(1, m(1.1)), border_radius=m(2))
    lay = scratch(surf)
    pygame.draw.line(lay, (255, 252, 236, 220), (cx - m(4), cy - m(6)),
                     (cx - m(4), cy + m(6)), max(1, m(1.0)))
    surf.blit(lay, (0, 0))
    pygame.draw.polygon(surf, (36, 32, 30), [
        (cx - m(11), cy + hh), (cx + m(11), cy + hh),
        (cx + m(8), cy + hh + m(5)), (cx - m(8), cy + hh + m(5))])
    capped_glow(surf, cx, cy, m(15), (255, 236, 186), 190, layers=8)


def _draw_cairn(surf, L, sun_dev, cx, base_y, scale, seed):
    """A trail cairn: stacked stones, near-black, each with a sun-side rim and
    a wind-packed snow cap. Depth for free at the foot of the post."""
    rnd = random.Random(seed)
    lay = scratch(surf)
    y = base_y
    n = 6
    for i in range(n):
        t = i / (n - 1)
        w = m(scale * (17 - 10 * t)) * rnd.uniform(0.88, 1.12)
        h = m(scale * (7.5 - 2.6 * t))
        rect = pygame.Rect(int(cx - w / 2 + m(rnd.uniform(-1.4, 1.4))),
                           int(y - h), int(w), int(h))
        pygame.draw.ellipse(surf, (18, 18, 24), rect)
        pygame.draw.arc(lay, (*L["snow_rim"], 140),
                        rect, math.radians(-64), math.radians(46), max(1, m(0.9)))
        pygame.draw.arc(lay, (*L["snow_hi"], 100),
                        rect.move(0, -m(0.8)), math.radians(24),
                        math.radians(156), max(1, m(0.8)))
        pygame.draw.arc(lay, (*L["bounce"], 120),
                        rect, math.radians(150), math.radians(210), max(1, m(0.8)))
        y -= h * 0.86
    surf.blit(lay, (0, 0))


def _enamel_plate(surf, rect_dev, radius):
    """A plain enamel trail sign: a single dark body, one hairline warm border,
    a seated contact shadow. One glyph and one word go on it and nothing else."""
    drop_shadow(surf, rect_dev, radius, blur=m(6), alpha=150, dy=m(3))
    surf.blit(vgrad_stops(rect_dev.w, rect_dev.h, radius,
                          [(0.00, ENAMEL_HI), (0.42, ENAMEL_LO),
                           (1.00, (11, 12, 18))], 255), rect_dev.topleft)
    top_sheen(surf, rect_dev, radius, m(12), peak=30)
    contact_shadow(surf, rect_dev, radius, m(4), alpha=120)
    lay = scratch(surf)
    pygame.draw.rect(lay, (0, 0, 0, 210), rect_dev, width=max(1, m(1.2)),
                     border_radius=radius)
    surf.blit(lay, (0, 0))
    lay = scratch(surf)
    pygame.draw.rect(lay, (*ENAMEL_EDGE, 150), rect_dev.inflate(-m(2), -m(2)),
                     width=max(1, m(0.7)), border_radius=max(1, radius - m(1)))
    surf.blit(lay, (0, 0))


def _glyph_coin(surf, cx, cy, r, col):
    pygame.draw.circle(surf, col, (cx, cy), r, max(1, m(1.4)))
    pygame.draw.circle(surf, col, (cx, cy), int(r * 0.52), max(1, m(1.1)))
    pygame.draw.line(surf, col, (cx, cy - int(r * 0.78)), (cx, cy + int(r * 0.78)),
                     max(1, m(1.2)))


def _glyph_trophy(surf, cx, cy, r, col):
    w = int(r * 1.15)
    pygame.draw.polygon(surf, col, [
        (cx - w, cy - r), (cx + w, cy - r),
        (cx + int(w * 0.66), cy + int(r * 0.28)),
        (cx - int(w * 0.66), cy + int(r * 0.28))])
    for s in (-1, 1):
        pygame.draw.arc(surf, col,
                        (cx + s * w - int(r * 0.5), cy - r,
                         int(r * 1.0), int(r * 1.0)),
                        math.radians(-90 if s > 0 else 90),
                        math.radians(90 if s > 0 else 270), max(1, m(1.3)))
    pygame.draw.rect(surf, col, (cx - max(1, m(1.6)), cy + int(r * 0.24),
                                 max(2, m(3.2)), int(r * 0.5)))
    pygame.draw.rect(surf, col, (cx - int(w * 0.78), cy + int(r * 0.70),
                                 int(w * 1.56), max(2, m(3.0))),
                     border_radius=m(1))


def _glyph_gear(surf, cx, cy, r, col):
    teeth = 8
    for k in range(teeth):
        a = math.radians(k * 360 / teeth)
        pygame.draw.line(surf, col,
                         (cx + math.cos(a) * r * 0.62, cy + math.sin(a) * r * 0.62),
                         (cx + math.cos(a) * r * 1.06, cy + math.sin(a) * r * 1.06),
                         max(2, m(2.4)))
    pygame.draw.circle(surf, col, (cx, cy), int(r * 0.70), max(1, m(1.8)))
    pygame.draw.circle(surf, col, (cx, cy), int(r * 0.26), max(1, m(1.4)))


def _glyph_pip(surf, cx, cy, r, col):
    """A parrot head in one silhouette — profile skull, beak, crest tick."""
    pygame.draw.circle(surf, col, (cx, cy), int(r * 0.72))
    pygame.draw.polygon(surf, col, [
        (cx + int(r * 0.34), cy - int(r * 0.30)),
        (cx + int(r * 1.16), cy + int(r * 0.06)),
        (cx + int(r * 0.30), cy + int(r * 0.48))])
    pygame.draw.polygon(surf, col, [
        (cx - int(r * 0.30), cy - int(r * 0.60)),
        (cx - int(r * 1.02), cy - int(r * 0.98)),
        (cx - int(r * 0.18), cy - int(r * 0.10))])
    pygame.draw.circle(surf, ENAMEL_LO, (cx + int(r * 0.12), cy - int(r * 0.16)),
                       max(1, int(r * 0.16)))


def _draw_signs(surf, L):
    for label, rect in SIGN_RECTS:
        r = pygame.Rect(m(rect.x), m(rect.y), m(rect.w), m(rect.h))
        _enamel_plate(surf, r, m(5))
        gx, gy = r.centerx, r.centery - m(10)
        if label == "STORE":
            _glyph_coin(surf, gx, gy, m(10), (*CREAM, 255))
        elif label == "TOP 10":
            _glyph_trophy(surf, gx, gy, m(9), (*CREAM, 255))
        else:
            _glyph_gear(surf, gx, gy, m(10), (*CREAM, 255))
        plain_text(surf, label, font(12), (r.centerx, r.centery + m(16)),
                   CREAM, shadow_a=170, tracking=m(0.6), weight=m(0.5))
        # Two bolts: the whole vocabulary of fastening on this screen.
        lay = scratch(surf)
        for bx in (r.left + m(6), r.right - m(6)):
            pygame.draw.circle(lay, (0, 0, 0, 170), (bx, r.top + m(6)), m(1.8))
        surf.blit(lay, (0, 0))
        lay = scratch(surf)
        for bx in (r.left + m(6), r.right - m(6)):
            pygame.draw.circle(lay, (*ENAMEL_EDGE, 120), (bx, r.top + m(6)), m(1.0))
        surf.blit(lay, (0, 0))


def _draw_profile(surf, L, name):
    r = pygame.Rect(m(PROFILE_RECT.x), m(PROFILE_RECT.y),
                    m(PROFILE_RECT.w), m(PROFILE_RECT.h))
    # A timber waypost plate rather than enamel, so PROFILE reads as a
    # different KIND of thing from the three utility signs.
    drop_shadow(surf, r, m(4), blur=m(6), alpha=150, dy=m(3))
    surf.blit(vgrad_stops(r.w, r.h, m(4), [
        (0.00, (58, 47, 36)), (0.30, (40, 32, 25)), (1.00, (20, 17, 14))], 255),
        r.topleft)
    lay = scratch(surf)
    for k in range(5):
        pygame.draw.line(lay, (10, 9, 8, 110),
                         (r.left + m(4), r.top + m(7) + k * m(9)),
                         (r.right - m(4), r.top + m(8) + k * m(9)), max(1, m(0.6)))
    surf.blit(lay, (0, 0))
    contact_shadow(surf, r, m(4), m(4), alpha=120)
    lay = scratch(surf)
    pygame.draw.rect(lay, (0, 0, 0, 200), r, width=max(1, m(1.2)),
                     border_radius=m(4))
    surf.blit(lay, (0, 0))
    lay = scratch(surf)
    pygame.draw.rect(lay, (*ENAMEL_EDGE, 120), r.inflate(-m(2), -m(2)),
                     width=max(1, m(0.7)), border_radius=m(3))
    surf.blit(lay, (0, 0))
    _glyph_pip(surf, r.left + m(17), r.centery, m(11), (*CREAM, 255))
    plain_text(surf, "PROFILE", font(12), (r.left + m(70), r.centery - m(10)),
               CREAM, shadow_a=170, tracking=m(0.6), weight=m(0.5))
    gradient_text(surf, name[:8].upper(), font(15),
                  (r.left + m(70), r.centery + m(10)),
                  GOLD_A_STOPS[0][1], GOLD_A_STOPS[-1][1],
                  keyline=(0, 0, 0), kw=m(0.9), shadow=False, tracking=m(0.5))
    lay = scratch(surf)
    pygame.draw.circle(lay, (0, 0, 0, 180), (r.right - m(7), r.top + m(7)), m(1.8))
    surf.blit(lay, (0, 0))
    lay = scratch(surf)
    pygame.draw.circle(lay, (*ENAMEL_EDGE, 110), (r.right - m(7), r.top + m(7)), m(1.0))
    surf.blit(lay, (0, 0))


def _draw_start(surf, L):
    """START: a heavy iron trail plate seated on the rock face, lit by the lamp.
    It sits ENTIRELY inside the opaque near-black rock — it never crosses sky at
    any phase — so gold on this body is a fixed ~10:1 read forever, by
    construction rather than by tuning."""
    r = pygame.Rect(m(START_RECT.x), m(START_RECT.y),
                    m(START_RECT.w), m(START_RECT.h))
    rad = m(7)
    capped_glow(surf, r.centerx, r.centery, int(r.w * 0.66), (255, 184, 112),
                int(32 + L["lamp_a"] * 0.18), layers=12)
    drop_shadow(surf, r, rad, blur=m(9), alpha=185, dy=m(4))
    surf.blit(vgrad_stops(r.w, r.h, rad, [
        (0.00, IRON_HI), (0.30, (19, 20, 26)), (0.72, IRON_LO),
        (1.00, (8, 9, 13))], 255), r.topleft)
    # The lamp's throw across the plate: warm on the lamp side, falling off to
    # bare iron on the far side.
    wash = hgrad_stops(r.w, r.h, [(0.0, (255, 198, 132)), (0.55, (255, 176, 110)),
                                  (1.0, (120, 96, 80))], 28)
    wm = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
    pygame.draw.rect(wm, (255, 255, 255, 255), wm.get_rect(), border_radius=rad)
    mask_min(wash, wm)
    surf.blit(wash, r.topleft)
    top_sheen(surf, r, rad, m(18), peak=22)
    contact_shadow(surf, r, rad, m(6), alpha=140)
    lay = scratch(surf)
    pygame.draw.rect(lay, (0, 0, 0, 220), r, width=max(1, m(1.6)),
                     border_radius=rad)
    surf.blit(lay, (0, 0))
    bevel_rim(surf, r, rad, (58, 40, 16), (250, 214, 146, 210), w=max(1, m(1.6)))
    gold_rule(surf, r.left + m(26), r.right - m(26), r.top + m(13),
              (250, 206, 128), peak=110, thick=max(1, m(0.8)))
    gold_rule(surf, r.left + m(26), r.right - m(26), r.bottom - m(13),
              (250, 206, 128), peak=110, thick=max(1, m(0.8)))
    gradient_text(surf, "START", font(30), (r.centerx, r.centery + m(0.5)),
                  GOLD_A_STOPS[0][1], GOLD_A_STOPS[-1][1],
                  keyline=(24, 12, 0), kw=m(1.1), tracking=m(5), weight=m(1.2))
    lay = scratch(surf)
    for bx in (r.left + m(11), r.right - m(11)):
        pygame.draw.circle(lay, (0, 0, 0, 190), (bx, r.centery), m(2.6))
    surf.blit(lay, (0, 0))
    lay = scratch(surf)
    for bx in (r.left + m(11), r.right - m(11)):
        pygame.draw.circle(lay, (232, 196, 132, 150), (bx, r.centery - m(0.6)), m(1.4))
    surf.blit(lay, (0, 0))


def _draw_wordmark(surf, L):
    gradient_text(surf, "SKYBIT", font(34), (m(180), m(66)),
                  GOLD_A_STOPS[0][1], GOLD_A_STOPS[-1][1],
                  keyline=(12, 10, 8), kw=m(1.6), tracking=m(7), weight=m(1.1))
    gold_rule(surf, m(112), m(248), m(88), (240, 200, 130), peak=120,
              thick=max(1, m(0.7)))
    plain_text(surf, "LAST LIGHT ON THE PASS", font(12), (m(180), m(99)),
               (232, 226, 214), shadow_a=170, tracking=m(1.6), weight=m(0.4),
               keyline=(12, 10, 8), kw=m(0.8))


# =============================================================================
# Bake — one SS compose + one downscale, cached per phase bucket.
# =============================================================================
BUCKETS = 8
_CACHE_MAX = 4
_base_cache = "OrderedDict[int, pygame.Surface]"
_base_cache = OrderedDict()
_breath_cache = OrderedDict()
_pip_cache = OrderedDict()
_drift_cache = None

_GEOM = None


def geometry():
    """Ridge arrays are phase-independent, so they are derived ONCE and shared
    by every bucket bake."""
    global _GEOM
    if _GEOM is None:
        _GEOM = dict(
            far=ridge_ys(FAR_CTRL, 11),
            mid_a=ridge_ys(MID_A_CTRL, 27, ((6, 3.4), (15, 1.6), (39, 0.7))),
            mid_b=ridge_ys(MID_B_CTRL, 43, ((6, 3.0), (15, 1.4), (37, 0.6))),
            near=ridge_ys(NEAR_CTRL, 61, ((7, 2.6), (19, 1.3), (47, 0.55))),
            snow=ridge_ys(SNOWLINE_CTRL, 83, ((9, 3.0), (23, 1.5), (51, 0.7))),
            fore=ridge_ys(FORE_CTRL, 97, ((5, 2.0), (13, 1.0))),
        )
    return _GEOM


def _build_base(bucket, name="PIP"):
    """The whole picture at SS=2, downscaled ONCE. Everything expensive lives
    here; the per-frame path is two blits plus Pip and the spindrift."""
    phase = (bucket + 0.5) / BUCKETS
    L = light_for_phase(phase)
    g = geometry()
    sun_dev = (m(SUN[0]), m(SUN[1]))

    surf = pygame.Surface((DW, DH))
    surf.blit(_sky_ss(phase), (0, 0))
    _draw_sun(surf, L, sun_dev)
    _draw_lenticulars(surf, L, sun_dev)

    # Plane 2, then its own band of luminous air over it. Each plane gets one:
    # depth here is air ADDED in front, never a plane faded out.
    _draw_far_range(surf, L, sun_dev, g["far"])
    haze_band(surf, m(288), m(324), L["haze"], L["haze_a"] * 0.70,
              sun_dev[0], m(210), gamma=0.85)

    _draw_mid_ridge(surf, L, sun_dev, g["mid_a"], 0.55, rim_scale=0.85)
    haze_band(surf, m(318), m(352), L["haze"], L["haze_a"] * 0.88,
              sun_dev[0], m(200), gamma=0.9)

    _draw_mid_ridge(surf, L, sun_dev, g["mid_b"], 0.22, rim_scale=1.0)
    _draw_shafts(surf, L, sun_dev, g["near"], g["mid_b"])
    haze_band(surf, m(340), m(380), L["haze"], L["haze_a"], sun_dev[0],
              m(190), gamma=0.95)

    _draw_near_ridge(surf, L, sun_dev, g["near"], g["snow"])
    haze_band(surf, m(360), m(392), L["haze"], L["haze_a"] * 0.22,
              sun_dev[0], m(170), gamma=1.1)

    _draw_lamp_pool(surf, L)
    _draw_cairn(surf, L, sun_dev, m(332), m(596), 1.25, 5)
    _draw_waypost(surf, L, sun_dev)
    _draw_cairn(surf, L, sun_dev, m(60), m(600), 0.85, 17)
    _draw_lamp(surf, L)
    _draw_start(surf, L)
    _draw_profile(surf, L, name)
    _draw_signs(surf, L)
    _draw_foreground(surf, L, g["fore"])
    _draw_wordmark(surf, L)

    vig = pygame.Surface((DW, DH), pygame.SRCALPHA)
    for y in range(0, DH, 2):
        f = y / DH
        a = int(36 * (1 - f / 0.16) ** 1.5) if f < 0.16 else 0
        if a > 0:
            pygame.draw.rect(vig, (10, 12, 20, a), (0, y, DW, 2))
    surf.blit(vig, (0, 0))
    vig = pygame.Surface((DW, DH), pygame.SRCALPHA)
    for x in range(0, DW, 2):
        d = abs(x - DW / 2) / (DW / 2)
        a = int(34 * d ** 2.6)
        if a > 0:
            pygame.draw.rect(vig, (8, 10, 18, a), (x, 0, 2, DH))
    surf.blit(vig, (0, 0))
    return downscale(surf)


def base_for(bucket, name="PIP"):
    key = (bucket, name)
    s = _base_cache.get(key)
    if s is None:
        s = _build_base(bucket, name)
        _base_cache[key] = s
        while len(_base_cache) > _CACHE_MAX:
            _base_cache.popitem(last=False)
    else:
        _base_cache.move_to_end(key)
    return s


def _build_breath(bucket):
    """The breathing half of the haze: the same bands again at a small alpha,
    stencilled off everything from the near ridge forward. One varying-alpha
    blit per frame makes the air move without re-baking anything."""
    phase = (bucket + 0.5) / BUCKETS
    L = light_for_phase(phase)
    g = geometry()
    layer = pygame.Surface((DW, DH), pygame.SRCALPHA)
    haze_band(layer, m(288), m(326), L["haze"], 150, m(SUN[0]), m(210), gamma=0.85)
    haze_band(layer, m(318), m(354), L["haze"], 175, m(SUN[0]), m(200), gamma=0.9)
    haze_band(layer, m(340), m(382), L["haze"], 200, m(SUN[0]), m(190), gamma=0.95)
    stencil = pygame.Surface((DW, DH), pygame.SRCALPHA)
    stencil.fill((255, 255, 255, 255))
    pygame.draw.polygon(stencil, (255, 255, 255, 0), ys_poly(g["near"], DH))
    mask_min(layer, stencil)
    return downscale(layer)


def breath_for(bucket):
    s = _breath_cache.get(bucket)
    if s is None:
        s = _build_breath(bucket)
        _breath_cache[bucket] = s
        while len(_breath_cache) > _CACHE_MAX:
            _breath_cache.popitem(last=False)
    else:
        _breath_cache.move_to_end(bucket)
    return s


# =============================================================================
# Pip — a rimmed silhouette carrying his REAL equipped parcel.
# =============================================================================
def equipped_key():
    store_data.load()
    return (store_data.equipped("skin") or "skin_base",
            store_data.equipped("parcel") or "parcel_base")


def _dir_rim(sil, col, alpha, dx, dy):
    """A contour highlight on the side facing a light: the silhouette nudged
    toward the source, minus the body, tinted with the SOURCE's colour."""
    rim = pygame.Surface(sil.get_size(), pygame.SRCALPHA)
    tint = sil.copy()
    tint.fill((*col, 255), special_flags=pygame.BLEND_RGBA_MULT)
    rim.blit(tint, (dx, dy))
    rim.blit(sil, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
    rim.set_alpha(max(0, min(255, alpha)))
    return rim


def _build_pip(skin, parcel_id, bucket):
    """Contre-jour Pip: the live equipped skin knocked back toward the shadow
    family, a hot sun-side rim, a cool lamp-side bounce, and — because a
    silhouette swallows anything inside its own hull — the parcel given its own
    lit contour and a crease where it tucks under him. Baked at SS and
    downscaled like the rest of the scene."""
    L = light_for_phase((bucket + 0.5) / BUCKETS)
    body = parrot.get_skin_frame(skin, 1, 0.0)
    parcel = parrot.get_parcel("normal", parcel_id)
    k = PIP_TARGET / float(max(body.get_size()))
    bw, bh = body.get_size()
    body = pygame.transform.smoothscale(body, (m(bw * k), m(bh * k)))
    pw, ph = parcel.get_size()
    parcel = pygame.transform.smoothscale(parcel, (m(pw * k), m(ph * k)))

    off = pygame.math.Vector2(0, m((PARCEL_Y_OFFSET + PARCEL_DROP) * k))
    off = off.rotate(-PIP_TILT)
    body = pygame.transform.rotate(body, PIP_TILT)
    parcel = pygame.transform.rotate(parcel, PIP_TILT)
    br = body.get_rect()
    pr = parcel.get_rect(center=(br.centerx + off.x, br.centery + off.y))
    span = br.union(pr).inflate(m(14), m(14))

    b_lay = pygame.Surface(span.size, pygame.SRCALPHA)
    b_lay.blit(body, (br.x - span.x, br.y - span.y))
    p_lay = pygame.Surface(span.size, pygame.SRCALPHA)
    p_lay.blit(parcel, (pr.x - span.x, pr.y - span.y))
    plate = b_lay.copy()
    plate.blit(p_lay, (0, 0))

    def darken(img, f):
        d = max(0, min(255, int(255 * f)))
        out = img.copy()
        out.fill((d, d, min(255, int(d * 1.06)), 255),
                 special_flags=pygame.BLEND_RGBA_MULT)
        amb = img.copy()
        amb.fill((22, 26, 40, 0), special_flags=pygame.BLEND_RGB_ADD)
        amb.set_alpha(120)
        out.blit(amb, (0, 0))
        return out

    def silhouette(img):
        sil = img.copy()
        sil.fill((255, 255, 255, 255), special_flags=pygame.BLEND_RGBA_MULT)
        return sil

    out = pygame.Surface(span.size, pygame.SRCALPHA)
    out.blit(darken(b_lay, L["pip_dark"]), (0, 0))
    # The parcel reads a step lighter than the bird and carries a crease where
    # his body occludes it — two objects, not one blob.
    out.blit(darken(p_lay, min(0.95, L["pip_dark"] * 1.34)), (0, 0))
    ao = silhouette(b_lay)
    ao.fill((0, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)
    crease = pygame.Surface(span.size, pygame.SRCALPHA)
    crease.blit(ao, (0, m(2.0)))
    mask_min(crease, silhouette(p_lay))
    crease.set_alpha(150)
    out.blit(crease, (0, 0))

    # A white silhouette drives the rims so they take the LIGHT's colour, not
    # the bird's: sun rim up-right at full strength, a weaker lamp rim
    # down-left. Two sources, the same two the landscape is lit by.
    sil = silhouette(plate)
    out.blit(_dir_rim(sil, tuple(int(v) for v in L["pip_rim"]),
                      int(L["pip_rim_a"]), m(1.0), -m(1.0)), (0, 0))
    out.blit(_dir_rim(sil, (255, 202, 138), int(L["lamp_a"] * 0.55),
                      -m(0.9), m(0.9)), (0, 0))
    out.blit(_dir_rim(silhouette(p_lay), (255, 210, 150),
                      int(120 + L["lamp_a"] * 0.35), -m(0.8), m(0.8)), (0, 0))
    small = pygame.transform.smoothscale(
        out, (max(1, span.w // SS), max(1, span.h // SS)))
    return small, k


def pip_for(skin, parcel_id, bucket):
    key = (skin, parcel_id, bucket)
    v = _pip_cache.get(key)
    if v is None:
        v = _build_pip(skin, parcel_id, bucket)
        _pip_cache[key] = v
        while len(_pip_cache) > 6:
            _pip_cache.popitem(last=False)
    else:
        _pip_cache.move_to_end(key)
    return v


# =============================================================================
# Spindrift — a slow ribbon of wind-blown snow crossing the crest.
# =============================================================================
def drift_sprites(L):
    """~40 cached particle sprites, warm-rimmed on the sun side. Built once;
    the per-frame cost is 40 blits of tiny surfaces."""
    global _drift_cache
    if _drift_cache is not None:
        return _drift_cache
    rnd = random.Random(3307)
    out = []
    for i in range(40):
        w = rnd.randint(7, 22)
        h = rnd.randint(2, 4)
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        for x in range(w):
            t = x / max(1, w - 1)
            a = int(255 * math.sin(t * math.pi) ** 1.4)
            col = lerp_color((214, 224, 238), (255, 240, 214), t)
            pygame.draw.line(s, (*col, a), (x, 0), (x, h - 1))
        out.append(s)
    _drift_cache = out
    return out


def draw_drift(surf, L, t):
    g = geometry()
    sprites = drift_sprites(L)
    for i, s in enumerate(sprites):
        speed = 26.0 + (i % 7) * 5.0
        x = ((t * speed + i * 41.0) % (W + 120.0)) - 60.0
        xd = int(max(0, min(DW - 1, m(x))))
        band = i % 3
        y = g["near"][xd] / SS - 3.0 - band * 5.0 \
            + math.sin(t * 1.1 + i) * 3.2
        img = s
        a = int(L["drift_a"] * (0.35 + 0.65 * math.sin(
            max(0.0, min(1.0, (x + 60.0) / (W + 120.0))) * math.pi)))
        if a <= 2:
            continue
        img = img.copy()
        img.set_alpha(a)
        surf.blit(img, (int(x), int(y)))
        if band == 0 and i % 2 == 0:
            # the same wind, down in the near-black foreground
            low = img.copy()
            low.set_alpha(max(0, a // 2))
            surf.blit(low, (int(x - 14), 612 + (i % 3) * 7))


# =============================================================================
# Per-frame render.
# =============================================================================
def render_frame(phase, t=0.0, name="PIP"):
    """Two cached blits (adjacent buckets, cross-faded), one breathing-haze
    blit, Pip, spindrift. No per-pixel work on this path."""
    bf = (phase % 1.0) * BUCKETS
    a = int(bf) % BUCKETS
    b = (a + 1) % BUCKETS
    f = bf - int(bf)
    surf = pygame.Surface((W, H))
    base_a = base_for(a, name)
    base_a.set_alpha(None)
    surf.blit(base_a, (0, 0))
    if f > 0:
        base_b = base_for(b, name)
        base_b.set_alpha(int(f * 255))
        surf.blit(base_b, (0, 0))
        base_b.set_alpha(None)

    L = light_for_phase(phase)
    breath = breath_for(a)
    # ±8 alpha over ~14 s: the air breathes without anything being redrawn.
    breath.set_alpha(max(0, int(8 + 8 * math.sin(t * 2 * math.pi / 14.0))))
    surf.blit(breath, (0, 0))

    skin, parcel_id = equipped_key()
    sprite, k = pip_for(skin, parcel_id, a)
    bob = math.sin(t * 1.7) * 3.0
    surf.blit(sprite, sprite.get_rect(center=(PIP_POS[0], PIP_POS[1] + bob)))
    draw_drift(surf, L, t)
    return surf


# =============================================================================
# Verification — every claim in the brief, measured on the rendered pixels.
# =============================================================================
def _lin(c):
    c /= 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def lum(rgb):
    r, g, b = (_lin(v) for v in rgb[:3])
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def cr(a, b):
    la, lb = lum(a) + 0.05, lum(b) + 0.05
    return round(max(la, lb) / min(la, lb), 2)


def mean_rgb(surf, rect, step=2):
    n = 0
    r = g = b = 0
    for y in range(rect.top, rect.bottom, step):
        for x in range(rect.left, rect.right, step):
            c = surf.get_at((x, y))
            r += c[0]
            g += c[1]
            b += c[2]
            n += 1
    return (r // max(1, n), g // max(1, n), b // max(1, n))


def max_lum_in(surf, rect, step=1, ys_top=None, ys_bot=None):
    best = -1.0
    px = (0, 0, 0)
    for y in range(rect.top, rect.bottom, step):
        for x in range(rect.left, rect.right, step):
            if ys_top is not None and y < ys_top(x):
                continue
            if ys_bot is not None and y > ys_bot(x):
                continue
            c = surf.get_at((x, y))
            v = lum(c)
            if v > best:
                best = v
                px = (c[0], c[1], c[2])
    return best, px


def sky_only(phase):
    s = pygame.Surface((W, H))
    if not sky_designs.render_active(s, W, H, GROUND_Y,
                                     _biome.palette_for_phase(phase), phase):
        s.fill((120, 170, 210))
    return s


def _sheet_text(sheet, txt, xy, size, col, bold=True):
    from game.hud import _font as hud_font
    img = hud_font(size, bold).render(txt, True, col)
    sheet.blit(img, xy)
    return img.get_width()


def build_sheet(frames, thumbs, crops, film):
    from game.hud import _font as hud_font
    gap, pad, head = 22, 28, 100
    sw = pad * 2 + W * 4 + gap * 3
    thumb_h = 160
    crop_h = 2 * 96
    sh = (head + 24 + H + 34 + thumb_h + 46 + crop_h + 40 + 200)
    sheet = pygame.Surface((sw, sh))
    sheet.fill((17, 17, 22))
    _sheet_text(sheet, "THEME C — LAST LIGHT ON THE PASS", (pad, 22), 32,
                (244, 206, 128))
    _sheet_text(sheet, "menu-v2 / first-light / round 2   ·   SS=2 compose + one "
                "downscale   ·   6 planes of air   ·   sun stays in frame and "
                "becomes the moon", (pad, 60), 16, (196, 196, 208))
    x = pad
    for name, ph in PHASES:
        _sheet_text(sheet, "%s   t=%.2f" % (name.upper(), ph), (x, head), 17,
                    (232, 226, 210))
        sheet.blit(frames[name], (x, head + 22))
        pygame.draw.rect(sheet, (74, 74, 88),
                         pygame.Rect(x - 1, head + 21, W + 2, H + 2), 1)
        x += W + gap

    ty = head + 22 + H + 30
    _sheet_text(sheet, "90x160 GREYSCALE — squint test", (pad, ty - 20), 15,
                (198, 198, 210))
    x = pad
    for name, _ph in PHASES:
        sheet.blit(thumbs[name], (x, ty))
        pygame.draw.rect(sheet, (74, 74, 88), pygame.Rect(x - 1, ty - 1, 92, 162), 1)
        _sheet_text(sheet, name.upper(), (x + 98, ty + 4), 15, (222, 216, 200))
        x += 132

    notes = [
        "TWO STRUCTURAL FIXES, BY CONSTRUCTION",
        "  START is an opaque near-black iron plate seated wholly inside the",
        "  rock face — it never touches sky at any phase, so gold-on-plate is a",
        "  fixed ~10:1 read instead of 1.02:1 against a day sky.",
        "  The near ridge is TWO LARGE FIELDS: a lit snowfield (bright leg,",
        "  carries plum + night) meeting a near-black rock face at a hard crest",
        "  (dark leg, carries day + dawn). No 3px rim is doing any work.",
        "",
        "VALUE ORDER — lit air is the brightest surface in frame at every phase.",
        "Ornament is withheld from everything man-made and from the foreground.",
    ]
    ny = ty - 20
    nx = pad + 4 * 132 + 10
    for line in notes:
        _sheet_text(sheet, line, (nx, ny), 15,
                    (244, 206, 128) if line and not line.startswith(" ") else
                    (216, 212, 202))
        ny += 21

    cy = ty + thumb_h + 46
    _sheet_text(sheet, "DETAIL @2x — trailhead lamp + waypost / the sun and alpenglow on the far peaks / near crest, sastrugi + spindrift / Pip",
                (pad, cy - 20), 15, (198, 198, 210))
    x = pad
    for cimg in crops:
        sheet.blit(cimg, (x, cy))
        pygame.draw.rect(sheet, (74, 74, 88),
                         pygame.Rect(x - 1, cy - 1, cimg.get_width() + 2,
                                     cimg.get_height() + 2), 1)
        x += cimg.get_width() + 16

    fy = cy + crop_h + 34
    _sheet_text(sheet, "MOTION — spindrift ribbon + haze breathing, t = 0.0 / "
                "3.5 / 7.0 s (cached sprites, one varying-alpha blit)",
                (pad, fy - 20), 15, (198, 198, 210))
    x = pad
    for fimg in film:
        sheet.blit(fimg, (x, fy))
        pygame.draw.rect(sheet, (74, 74, 88),
                         pygame.Rect(x - 1, fy - 1, fimg.get_width() + 2,
                                     fimg.get_height() + 2), 1)
        x += fimg.get_width() + 16
    return sheet


def crop2x(surf, rect):
    sub = surf.subsurface(rect).copy()
    return pygame.transform.scale(sub, (rect.width * 2, rect.height * 2))


def main():
    os.makedirs(OUT, exist_ok=True)
    g = geometry()
    frames, thumbs = {}, {}
    for name, ph in PHASES:
        f = render_frame(ph, t=0.0)
        frames[name] = f
        thumbs[name] = pygame.transform.grayscale(
            pygame.transform.smoothscale(f, (90, 160)))
        pygame.image.save(f, os.path.join(OUT, "round_2_%s.png" % name))

    crops = [
        crop2x(frames["plum"], pygame.Rect(10, 320, 168, 96)),
        crop2x(frames["golden"], pygame.Rect(192, 214, 168, 96)),
        crop2x(frames["day"], pygame.Rect(96, 316, 168, 96)),
        crop2x(frames["night"], pygame.Rect(168, 150, 168, 96)),
    ]
    film = [pygame.transform.scale(
        render_frame(0.27, t=tt).subsurface(pygame.Rect(0, 300, 360, 120)).copy(),
        (360, 120)) for tt in (0.0, 3.5, 7.0)]

    sheet = build_sheet(frames, thumbs, crops, film)
    pygame.image.save(sheet, os.path.join(OUT, "round_2.png"))

    # ── report ──────────────────────────────────────────────────────────────
    gold = GOLD_A_STOPS[0][1]
    gold_mid = lerp_stops(GOLD_A_STOPS, 0.5)
    UI = [START_RECT, PROFILE_RECT] + [r for _n, r in SIGN_RECTS]
    LAMPZONE = pygame.Rect(0, 300, 78, 240)

    def in_ui(x, y):
        for r in UI:
            if r.collidepoint(x, y):
                return True
        return LAMPZONE.collidepoint(x, y)

    def band_px(surf, top, bot, pad_t=2, pad_b=2, x0=0, x1=W, skip_ui=True,
                skip_sun=False, step=2):
        out = []
        for x in range(x0, x1, step):
            xd = min(DW - 1, x * SS)
            ya = int(top[xd] / SS) + pad_t
            yb = int(bot[xd] / SS) - pad_b
            for y in range(max(0, ya), min(H, yb), step):
                if skip_ui and in_ui(x, y):
                    continue
                if skip_sun and math.hypot(x - SUN[0], y - SUN[1]) < 46:
                    continue
                c = surf.get_at((x, y))
                out.append((c[0], c[1], c[2]))
        return out

    def px_mean(px):
        n = max(1, len(px))
        return (sum(p[0] for p in px) // n, sum(p[1] for p in px) // n,
                sum(p[2] for p in px) // n)

    def block_max(surf, cells):
        """Brightest 5x5 block mean inside a region — a FIELD value. A single
        light-wrap rim pixel is 4% of a block and cannot carry it."""
        best, bp = -1.0, (0, 0, 0)
        for (x, y) in cells:
            r = gg = b = 0
            for yy in range(y - 2, y + 3):
                for xx in range(x - 2, x + 3):
                    c = surf.get_at((max(0, min(W - 1, xx)),
                                     max(0, min(H - 1, yy))))
                    r += c[0]
                    gg += c[1]
                    b += c[2]
            p = (r // 25, gg // 25, b // 25)
            v = lum(p)
            if v > best:
                best, bp = v, p
        return best, bp

    def band_cells(top, bot, pad_t=2, pad_b=2, skip_sun=False, step=3):
        out = []
        for x in range(3, W - 3, step):
            xd = min(DW - 1, x * SS)
            ya = int(top[xd] / SS) + pad_t
            yb = int(bot[xd] / SS) - pad_b
            for y in range(max(3, ya), min(H - 3, yb), step):
                if in_ui(x, y):
                    continue
                if skip_sun and math.hypot(x - SUN[0], y - SUN[1]) < 46:
                    continue
                out.append((x, y))
        return out

    def px_max(px):
        best, bp = -1.0, (0, 0, 0)
        for p in px:
            v = lum(p)
            if v > best:
                best, bp = v, p
        return best, bp

    def offset_ys(ys, d):
        return [v + m(d) for v in ys]

    print("\n" + "=" * 78)
    print("1. STRUCTURAL FIX A — gold START vs the ground it sits on")
    print("=" * 78)
    print("   %-7s %-16s %-16s %8s %8s %8s" %
          ("phase", "plate body", "rock in the lamp pool", "gold:plt", "goldmid",
           "gold:rock"))
    for name, ph in PHASES:
        f = frames[name]
        plate = px_mean([f.get_at((x, y))[:3]
                         for y in range(START_RECT.centery - 9,
                                        START_RECT.centery + 9)
                         for x in range(START_RECT.x + 16, START_RECT.x + 46)])
        rock = px_mean([f.get_at((x, y))[:3]
                        for y in range(START_RECT.bottom + 4, START_RECT.bottom + 16)
                        for x in range(START_RECT.x + 10, START_RECT.right - 10, 2)])
        print("   %-7s %-16s %-16s %8.2f %8.2f %8.2f"
              % (name, str(plate), str(rock), cr(gold, plate),
                 cr(gold_mid, plate), cr(gold, rock)))
    lowest_snow = max(g["snow"][m(START_RECT.left):m(START_RECT.right)]) / SS
    print("   START rect %s — plate top y=%d; across the plate's x-span the "
          "rock/snow boundary never falls below y=%.1f, so the plate sits "
          "wholly inside opaque rock with %.1fpx to spare, at every phase."
          % (tuple(START_RECT), START_RECT.top, lowest_snow,
             START_RECT.top - lowest_snow))

    print("\n" + "=" * 78)
    print("2. STRUCTURAL FIX B — the near ridge's two legs vs the sky")
    print("=" * 78)
    print("   %-7s %-16s %-16s %-16s %8s %8s" %
          ("phase", "sky @ crest", "snowfield mean", "rock face mean",
           "snow:sky", "rock:sky"))
    for name, ph in PHASES:
        f = frames[name]
        sky = px_mean([sky_only(ph).get_at((x, y))[:3]
                       for y in range(296, 330, 2) for x in range(0, W, 4)])
        snow = px_mean(band_px(f, g["near"], g["snow"], 3, 3))
        rock = px_mean(band_px(f, g["snow"], g["fore"], 6, 6))
        best = max(cr(snow, sky), cr(rock, sky))
        print("   %-7s %-16s %-16s %-16s %8.2f %8.2f   %s (best leg %.2f)"
              % (name, str(sky), str(snow), str(rock), cr(snow, sky),
                 cr(rock, sky), "PASS" if best >= 3.0 else "FAIL", best))

    print("\n" + "=" * 78)
    print("3. VALUE ORDER — is the lit AIR the brightest surface in frame?")
    print("=" * 78)
    print("   (light sources excluded: sun/moon disc + halo core, the lantern)")
    for name, ph in PHASES:
        f = frames[name]
        air = block_max(f, band_cells(offset_ys(g["mid_b"], 1), g["near"],
                                      1, 2, skip_sun=True))
        nsnow = block_max(f, band_cells(g["near"], g["snow"], 4, 4))
        fsnow = block_max(f, band_cells(g["far"], offset_ys(g["far"], 26), 2, 0,
                                        skip_sun=True))
        rock = block_max(f, band_cells(g["snow"], g["fore"], 7, 7))
        plate = block_max(f, [(x, y)
                              for y in range(START_RECT.y + 4,
                                             START_RECT.bottom - 4, 3)
                              for x in range(START_RECT.x + 4,
                                             START_RECT.right - 4, 3)])
        top = max(nsnow[0], fsnow[0], rock[0], plate[0])
        print("   %-7s AIR=%.3f %-16s | nearsnow=%.3f  farsnow=%.3f  rock=%.3f"
              "  START=%.3f  ->  air is the brightest surface: %s (margin %+.3f)"
              % (name, air[0], str(air[1]), nsnow[0], fsnow[0], rock[0],
                 plate[0], "YES" if air[0] > top else "NO", air[0] - top))

    print("\n" + "=" * 78)
    print("4. LABEL / GLYPH CONTRAST, each against its own ground")
    print("=" * 78)
    for name, ph in PHASES:
        f = frames[name]
        sk = sky_only(ph)
        row = []
        for label, r in SIGN_RECTS:
            ground = px_mean([f.get_at((x, y))[:3]
                              for y in range(r.y + r.h - 22, r.y + r.h - 14)
                              for x in range(r.x + 8, r.right - 8, 2)])
            row.append("%-9s %5.2f" % (label, cr(CREAM, ground)))
        pg = px_mean([f.get_at((x, y))[:3]
                      for y in range(PROFILE_RECT.y + 6, PROFILE_RECT.y + 14)
                      for x in range(PROFILE_RECT.x + 48, PROFILE_RECT.right - 8, 2)])
        pn = px_mean([f.get_at((x, y))[:3]
                      for y in range(PROFILE_RECT.centery + 4,
                                     PROFILE_RECT.centery + 16)
                      for x in range(PROFILE_RECT.x + 48, PROFILE_RECT.right - 8, 2)])
        wsky = px_mean([sk.get_at((x, y))[:3]
                        for y in range(54, 80, 2) for x in range(110, 250, 3)])
        print("   %-7s cream:enamel  %s" % (name, "   ".join(row)))
        print("           PROFILE cream:plate=%5.2f  name gold:plate=%5.2f  |"
              "  wordmark gold:sky=%5.2f  keyline:sky=%5.2f  gold:keyline=%5.2f"
              % (cr(CREAM, pg), cr(gold, pn), cr(gold, wsky),
                 cr((12, 10, 8), wsky), cr(gold, (12, 10, 8))))

    print("\n" + "=" * 78)
    print("5. TAP TARGETS")
    print("=" * 78)
    rects = [("START", START_RECT), ("PROFILE", PROFILE_RECT)] + SIGN_RECTS
    for nm, r in rects:
        print("   %-9s %-26s w=%3d h=%3d  bottom=%d" %
              (nm, str(tuple(r)), r.w, r.h, r.bottom))
    ok = True
    for i2 in range(len(rects)):
        for j2 in range(i2 + 1, len(rects)):
            if rects[i2][1].colliderect(rects[j2][1]):
                ok = False
                print("   OVERLAP", rects[i2][0], rects[j2][0])
    gaps = []
    for i2 in range(len(rects)):
        for j2 in range(i2 + 1, len(rects)):
            a, b = rects[i2][1], rects[j2][1]
            dx = max(a.left - b.right, b.left - a.right, 0)
            dy = max(a.top - b.bottom, b.top - a.bottom, 0)
            gaps.append(max(dx, dy))
    print("   pairwise disjoint: %s   min gap between any two: %dpx   "
          "all >= 48dp: %s   lowest edge: %d (limit 624)"
          % (ok, min(gaps), all(r.w >= 48 and r.h >= 48 for _, r in rects),
             max(r.bottom for _, r in rects)))
    from game.hud import _font as hud_font
    for label, r in SIGN_RECTS + [("PROFILE", PROFILE_RECT)]:
        fw = hud_font(12, True).size(label)[0]
        print("   label %-9s rendered at 12px = %2dx%dpx   plate %3dx%-3d  "
              "side margin %.1fpx" % (label, fw, hud_font(12, True).get_height(),
                                      r.w, r.h, (r.w - fw) / 2.0))

    print("\n" + "=" * 78)
    print("6. THUMBNAIL READ (90x160 greyscale, band means)")
    print("=" * 78)
    for name, _ph in PHASES:
        th = thumbs[name]
        bands = []
        for y0, y1, tag in ((0, 55, "sky"), (58, 82, "air+far"),
                            (84, 104, "snowfield"), (108, 132, "rock+START"),
                            (132, 160, "signs+fore")):
            vals = [th.get_at((xx, yy))[0]
                    for yy in range(y0, y1) for xx in range(0, 90, 2)]
            bands.append("%s=%3d" % (tag, sum(vals) // len(vals)))
        print("   %-7s %s" % (name, "  ".join(bands)))

    print("\n" + "=" * 78)
    print("7. PIP")
    print("=" * 78)
    skin, parcel_id = equipped_key()
    print("   equipped read LIVE via store_data.equipped(): skin=%s parcel=%s"
          % (skin, parcel_id))
    raw = parrot.get_skin_frame(skin, 1, 0.0)
    print("   source frame %s -> logical scale k=%.2f -> long edge %dpx at (%d,%d)"
          % (str(raw.get_size()), PIP_TARGET / float(max(raw.get_size())),
             PIP_TARGET, PIP_POS[0], PIP_POS[1]))
    for name, ph in PHASES:
        L = light_for_phase(ph)
        bucket = int((ph % 1.0) * BUCKETS) % BUCKETS
        sprite, k = pip_for(skin, parcel_id, bucket)
        px = [sprite.get_at((x, y)) for y in range(0, sprite.get_height(), 2)
              for x in range(0, sprite.get_width(), 2)]
        body = [p[:3] for p in px if p[3] > 200]
        rim = px_max(body)
        print("   %-7s sprite=%dx%d  body_mean=%-16s rim_peak=%-16s "
              "body:rim=%.2f  darken=%.2f" %
              (name, sprite.get_width(), sprite.get_height(),
               str(px_mean(body)), str(rim[1]), cr(px_mean(body), rim[1]),
               L["pip_dark"]))
    pbody = parrot.get_skin_frame(skin, 1, 0.0)
    pparcel = parrot.get_parcel("normal", parcel_id)
    kk = PIP_TARGET / float(max(pbody.get_size()))
    pbody = pygame.transform.rotate(pygame.transform.smoothscale(
        pbody, (int(pbody.get_width() * kk), int(pbody.get_height() * kk))),
        PIP_TILT)
    pparcel = pygame.transform.rotate(pygame.transform.smoothscale(
        pparcel, (int(pparcel.get_width() * kk), int(pparcel.get_height() * kk))),
        PIP_TILT)
    poff = pygame.math.Vector2(0, (PARCEL_Y_OFFSET + PARCEL_DROP) * kk).rotate(-PIP_TILT)
    brr = pbody.get_rect()
    prr = pparcel.get_rect(center=(brr.centerx + poff.x, brr.centery + poff.y))
    total = free = 0
    for y in range(pparcel.get_height()):
        for x in range(pparcel.get_width()):
            if pparcel.get_at((x, y))[3] < 128:
                continue
            total += 1
            bx, by = prr.x + x - brr.x, prr.y + y - brr.y
            if not (0 <= bx < brr.w and 0 <= by < brr.h) or \
                    pbody.get_at((bx, by))[3] < 128:
                free += 1
    print("   parcel: parrot.get_parcel('normal', %r), %dx%d at k, drawn AFTER "
          "the body at +%dpx (entities.Bird order + menu drop) — %d of its %d solid px "
          "(%.0f%%) sit clear of the hull"
          % (parcel_id, pparcel.get_width(), pparcel.get_height(),
             PARCEL_Y_OFFSET + PARCEL_DROP, free, total,
             100.0 * free / max(1, total)))
    print("   rim light: _dir_rim off a WHITE silhouette so the contour takes "
          "the LIGHT's colour — sun rim up-right at alpha %d, lamp rim "
          "down-left at %d%%, plus the parcel's own lamp-side contour."
          % (int(light_for_phase(0.12)["pip_rim_a"]), 55))

    print("\n" + "=" * 78)
    print("8. TECHNIQUE")
    print("=" * 78)
    print("   SS=%d compose at %dx%d -> ONE smoothscale to %dx%d "
          "(store_hub.downscale)" % (SS, DW, DH, W, H))
    print("   bake-once: %d phase buckets, LRU %d.  Per-frame path = 2 base "
          "blits (cross-fade) + 1 varying-alpha breath blit + 1 Pip blit + "
          "%d cached drift sprites." % (BUCKETS, _CACHE_MAX,
                                        len(drift_sprites(light_for_phase(0.12)))))
    print("   resident caches: base=%d breath=%d pip=%d"
          % (len(_base_cache), len(_breath_cache), len(_pip_cache)))
    print("   numpy: not imported and never called here (the only occurrences "
          "of the string in this file are in prose). It shows up in "
          "sys.modules on desktop because pygame imports it itself; nothing "
          "on this draw path touches it, so the same code runs on pygbag.")
    print("   per-pixel loops on the per-frame path: none (all loops live in "
          "_build_base / _build_breath / _build_pip, which are bakes)")
    print("\n   wrote %s" % os.path.join(OUT, "round_2.png"))


if __name__ == "__main__":
    main()
