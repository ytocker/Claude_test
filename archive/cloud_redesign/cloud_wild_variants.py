"""8 wild-divergence cloud explorations — no shared silhouette family.

The prior rounds (23 / 24 / 25) all radiated from one Ruyi-disc DNA. This
module deliberately scatters across eight unrelated formal grammars so
each variant differs from every other on at least three of: silhouette
family, aspect ratio, edge treatment, palette use, internal structure.
The aspect ratios alone span 20×80 (vertical pillar), 110×12 (horizontal
streak), 100×30 (scattered constellation), and 70×50 (faceted polygon)
— no two variants share the same bounding-box profile.

Drop-in: every variant matches `draw_cloud_<name>(surf, x, y, palette,
scale=1.0)`. Palette helpers are imported from the shared cloud module
so the night-cool branch stays single-source — re-implementing it would
desync this set from the live `_cloud_body_color` whenever that file
re-tunes its luminance threshold.
"""
from __future__ import annotations

import math
import pygame

from cloud_variants import (
    _cloud_body_color,
    _ink_shadow_color,
    _lit_edge_color,
)
from ruyi_variants import (
    _is_night,
    _lerp,
    _lerp_color,
    _seeded_jit,
    _alpha_surf,
)


# ─────────────────────────────────────────────────────────────────────────────
# Variant 1 — Yún Hanzi Glyph (雲)
# Research:
#   https://en.wiktionary.org/wiki/%E4%BA%91
#   https://palmstone.com/i-love-the-bold-and-simple-strokes-of-many-of-the-ancient-forms-of-chinese-characters-clouds-%E4%BA%91-yun-are-evoked-with-just-three-lines-in-this-old-version-of-the-character-for-me-the-lower/
#
# The ancient seal-script form of 云 (yún, cloud) is three coiled strokes:
# a top horizontal stroke, a lower horizontal, and a hooked sub-stroke
# curling under. Rendered here as the actual pictographic character —
# the cloud IS the calligraphic stroke set that originally evoked it.
# Aspect ratio is roughly square (50 × 44), heavy 3 px brush mass per
# stroke, no fill body — pure silhouette is the stroke geometry.
# ─────────────────────────────────────────────────────────────────────────────

def draw_cloud_yun_glyph(surf, x, y, palette, scale=1.0):
    """Pictographic 云 character — three calligraphic strokes ARE the cloud."""
    body = _cloud_body_color(palette)
    edge = _ink_shadow_color(palette)
    lit = _lit_edge_color(palette)
    night = _is_night(palette)

    w = int(50 * scale)
    h = int(44 * scale)
    pad = 4
    s = _alpha_surf(w + pad * 2, h + pad * 2)

    # Stroke colour is the body tint pushed slightly toward the lit edge
    # so the calligraphy reads as luminous brush-paint against the sky,
    # not as ink contour — the silhouette has no separate fill, so the
    # strokes themselves carry the cloud's luminance value.
    stroke = _lerp_color(body, lit, 0.18)
    contour = edge if not night else _lerp_color(edge, lit, 0.30)
    stroke_w = max(3, int(round(4 * scale)))

    # Top horizontal — the heaven-stroke. Slight downward bow at right so
    # the stroke reads as a swept calligraphic horizontal rather than a
    # ruled line; the bow ALSO breaks alignment with the second stroke so
    # the two horizontals don't look like a clip-art equals sign.
    top_y = pad + int(h * 0.18)
    top_pts = (
        (pad + int(w * 0.10), top_y),
        (pad + int(w * 0.40), top_y - 1),
        (pad + int(w * 0.70), top_y + 1),
        (pad + int(w * 0.92), top_y + 3),
    )
    pygame.draw.lines(s, (*stroke, 235), False, top_pts, stroke_w)

    # Second horizontal — wider, with a leftward sweep into the curl. The
    # leftward sweep is what tells the eye the lower mass is one stroke
    # that continues into the hook, not two separate strokes.
    mid_y = pad + int(h * 0.46)
    mid_pts = (
        (pad + int(w * 0.05), mid_y + 2),
        (pad + int(w * 0.35), mid_y),
        (pad + int(w * 0.65), mid_y + 1),
        (pad + int(w * 0.95), mid_y + 4),
    )
    pygame.draw.lines(s, (*stroke, 240), False, mid_pts, stroke_w)

    # The defining hook curl — the sub-glyph 厶 evolved into 私; here it
    # reads as the cloud's coiling underbody. Painted as two arcs that
    # join so the hook completes a calligraphic ㄣ — left-flick into a
    # rising curl. The hook is what makes the glyph read as 云 / 雲
    # rather than two parallel sticks.
    hook_cx = pad + int(w * 0.55)
    hook_cy = pad + int(h * 0.72)
    hook_r = int(h * 0.22)
    pygame.draw.arc(
        s, (*stroke, 240),
        pygame.Rect(hook_cx - hook_r, hook_cy - hook_r,
                    hook_r * 2, hook_r * 2),
        math.radians(40), math.radians(330), stroke_w)
    # Trailing flick — the brush lifts to the lower-right. Painted as a
    # short tapered line so the gesture reads as a confident stroke
    # release rather than a clipped arc end.
    flick_a = (hook_cx + int(hook_r * 0.88), hook_cy + int(hook_r * 0.50))
    flick_b = (hook_cx + int(hook_r * 1.25), hook_cy + int(hook_r * 1.05))
    pygame.draw.line(s, (*stroke, 230), flick_a, flick_b, stroke_w - 1)

    # A whisper of ink-shadow under each horizontal — gated to non-night
    # phases because deep-blue night turns the under-shadow into smudge.
    if not night:
        pygame.draw.lines(s, (*contour, 80), False,
                          [(px, py + 2) for px, py in top_pts], 1)
        pygame.draw.lines(s, (*contour, 80), False,
                          [(px, py + 2) for px, py in mid_pts], 1)

    surf.blit(s, (int(x - (pad + w // 2)), int(y - (pad + h // 2))))


# ─────────────────────────────────────────────────────────────────────────────
# Variant 2 — Vertical Sumeru Pillar
# Research:
#   https://en.wikipedia.org/wiki/Mount_Meru_(Buddhism)
#   https://www.hdasianart.com/blogs/news/mount-meru-in-buddhism-the-cosmic-axis-of-the-universe
#
# Mount Sumeru in Buddhist cosmology is described as hourglass-shaped:
# wide base + wide top, pinched waist. Rendered here as a vertical cloud
# column — a rising thunderhead pillar reading as a cosmic axis rather
# than a horizontal drift. 20 × 80 px aspect locks it as the lineup's
# vertical anchor; no other variant runs taller than wide.
# ─────────────────────────────────────────────────────────────────────────────

def draw_cloud_sumeru_pillar(surf, x, y, palette, scale=1.0):
    """Hourglass thunderhead pillar — vertical Sumeru-axis cloud column."""
    body = _cloud_body_color(palette)
    edge = _ink_shadow_color(palette)
    lit = _lit_edge_color(palette)
    night = _is_night(palette)

    w = int(28 * scale)
    h = int(80 * scale)
    pad = 6
    s = _alpha_surf(w + pad * 2, h + pad * 2)

    cx = pad + w // 2

    # Hourglass profile: 3 stacked horizontal bands — top cap, pinched
    # waist, bottom anvil. Sumeru is described as 80 000 yojanas top/base
    # and 20 000 at the waist, so the waist is ~25% of the cap width.
    bands = (
        # (y_frac, half_w_frac, alpha)
        (0.05, 0.95, 235),
        (0.18, 0.78, 240),
        (0.34, 0.46, 230),
        (0.50, 0.28, 215),  # pinched waist
        (0.66, 0.46, 225),
        (0.82, 0.78, 235),
        (0.95, 0.95, 230),
    )
    for (yf, hwf, a) in bands:
        by = pad + int(h * yf)
        hw = max(2, int(w * 0.5 * hwf))
        # Slight vertical thickness per band so the column reads as a
        # stack of soft ink discs, not stripes — discs overlap so the
        # silhouette is continuous from cap to anvil.
        band_h = max(3, int(h * 0.14))
        pygame.draw.ellipse(
            s, (*body, a),
            pygame.Rect(cx - hw, by - band_h // 2, hw * 2, band_h))

    # Sunlit edge along the column's leading (left) flank — a single thin
    # vertical highlight stroke. Drawn as a chain of tiny dabs so it
    # reads as scattered light catching each band's rim rather than a
    # ruled vertical line. Gated to non-night so the rim doesn't blow
    # out the moonlit-pillar read at NIGHT.
    if not night:
        for (yf, hwf, _a) in bands:
            by = pad + int(h * yf)
            hw = max(2, int(w * 0.5 * hwf))
            pygame.draw.circle(s, (*lit, 200),
                               (cx - hw + 1, by), max(1, int(scale * 1.3)))

    # Ink-shadow on the trailing (right) flank — symmetric counterweight
    # to the highlight so the pillar reads as round volume, not flat
    # paper. Painted as a low-alpha vertical ellipse hugging the right
    # edges of the bands.
    for (yf, hwf, _a) in bands:
        by = pad + int(h * yf)
        hw = max(2, int(w * 0.5 * hwf))
        pygame.draw.ellipse(
            s, (*edge, 65),
            pygame.Rect(cx + hw - 3, by - 2,
                        max(3, int(scale * 4)), max(3, int(scale * 5))))

    # A single calligraphic "axis" stroke down the pillar's centre — the
    # cosmic-axis read that distinguishes Sumeru from a generic cumulus
    # column. Thin, low alpha so it reads as an inner light line rather
    # than dividing the silhouette.
    axis_col = lit if night else _lerp_color(body, edge, 0.45)
    pygame.draw.line(s, (*axis_col, 110),
                     (cx, pad + 4), (cx, pad + h - 4),
                     max(1, int(scale)))

    surf.blit(s, (int(x - cx), int(y - (pad + h // 2))))


# ─────────────────────────────────────────────────────────────────────────────
# Variant 3 — Cirrus Mare's-Tail Streak
# Research:
#   https://en.wikipedia.org/wiki/Cirrus_uncinus_cloud
#   https://earthsky.org/earth/mares-tails-cirrus-uncinus-clouds/
#
# Cirrus uncinus — the "horse's tail" cloud — appears as a thin curled
# hook trailing a long feathered streak. Sailors read it as the
# leading edge of a warm front. Rendered here as a 110 × 12 horizontal
# wisp with a curled head on the leading (left) side, ice-crystal fall-
# streak feathers raining from the spine. Edge treatment is pure
# feathered alpha — no closed silhouette, no keyline.
# ─────────────────────────────────────────────────────────────────────────────

def draw_cloud_mares_tail(surf, x, y, palette, scale=1.0):
    """Cirrus uncinus — hooked head dragging a feathered fall-streak."""
    body = _cloud_body_color(palette)
    edge = _ink_shadow_color(palette)
    lit = _lit_edge_color(palette)

    length = int(110 * scale)
    h = int(28 * scale)
    pad = 6
    s = _alpha_surf(length + pad * 2, h + pad * 2)
    cy = pad + h // 2

    # Spine — a long thin alpha-tapered ellipse that fades from head to
    # tail. Drawn as a chain of overlapping thin ellipses so the alpha
    # falloff is continuous, not stepped.
    n = 18
    for i in range(n):
        t = i / (n - 1)
        sx = pad + int(t * length)
        sy = cy - int(math.sin(t * math.pi * 0.6) * 3 * scale)
        sw = max(2, int(8 * scale * (1 - t * 0.85)))
        sh = max(1, int(3 * scale))
        # Alpha bell so the streak is densest near the head's hook and
        # wisps off the tail tip.
        a = int(_lerp(220, 50, t))
        pygame.draw.ellipse(s, (*body, a),
                            pygame.Rect(sx - sw // 2, sy - sh // 2, sw, sh))

    # Curled hook at the leading (left) head — the defining cirrus uncinus
    # signature. Painted as a partial arc with the body tint so the hook
    # reads as a continuation of the streak, not a separate symbol.
    hook_r = max(4, int(h * 0.45))
    hook_cx = pad + hook_r
    hook_cy = cy + 1
    pygame.draw.arc(
        s, (*body, 230),
        pygame.Rect(hook_cx - hook_r, hook_cy - hook_r,
                    hook_r * 2, hook_r * 2),
        math.radians(40), math.radians(260), max(2, int(scale * 3)))
    pygame.draw.arc(
        s, (*lit, 180),
        pygame.Rect(hook_cx - hook_r + 1, hook_cy - hook_r + 1,
                    hook_r * 2 - 2, hook_r * 2 - 2),
        math.radians(50), math.radians(200), max(1, int(scale * 2)))

    # Fall-streak feathers — short downward diagonal slants raining from
    # the spine, simulating ice crystals sublimating into drier air. The
    # diagonal angle (not vertical) is what reads as wind shear; perfect
    # verticals would look like rain.
    rng_seed = (int(x) * 0x9E37) ^ (int(y) * 0x85EB)
    n_fall = 9
    for k in range(n_fall):
        t = 0.15 + (k / (n_fall - 1)) * 0.75
        fx = pad + int(t * length)
        fy_top = cy + 1
        # Feather length tapers with position so the densest fall-streaks
        # cluster mid-streak — same way uncinus actually disperses.
        flen = max(3, int(h * 0.55 * (0.5 + 0.5 * math.sin(t * math.pi))))
        jit = ((rng_seed >> (k % 12)) & 0x7) - 3
        # Slant the feathers right-down per typical jetstream shear; the
        # micro-jitter keeps any two from being parallel.
        fy_bot = fy_top + flen
        fx_bot = fx + max(2, int(flen * 0.25)) + jit // 2
        a = int(_lerp(140, 40, t))
        pygame.draw.line(s, (*body, a),
                         (fx, fy_top), (fx_bot, fy_bot),
                         max(1, int(scale)))

    # Soft ink-shadow whisper under the head only — the hook is the
    # silhouette's heaviest mass and benefits from a hint of depth so
    # the streak reads as 3D foreshortening rather than flat tape.
    pygame.draw.ellipse(
        s, (*edge, 45),
        pygame.Rect(pad + 1, cy + 1, hook_r * 2 + 2, max(3, int(h * 0.35))))

    surf.blit(s, (int(x - length // 2 - pad), int(y - cy)))


# ─────────────────────────────────────────────────────────────────────────────
# Variant 4 — Constellation Dot-Cloud
# Research:
#   https://en.wikipedia.org/wiki/Thirty-six_Views_of_Mount_Fuji
#   https://www.metmuseum.org/art/collection/search/36490
#
# Hokusai's Edo prints render distant haze and dust as scattered ink-flick
# stipple. This variant pushes that to the extreme: the cloud is a
# loose constellation of 30–40 dots arranged in a soft elliptical
# distribution, no connecting silhouette. The eye Gestalt-groups them
# into one cloud mass. 100 × 30 px scattered footprint reads from a
# distance as ink-mist rather than a discrete puff.
# ─────────────────────────────────────────────────────────────────────────────

def draw_cloud_constellation(surf, x, y, palette, scale=1.0):
    """Scattered ink-flick stipple — Gestalt cloud assembled from 30+ dots."""
    body = _cloud_body_color(palette)
    edge = _ink_shadow_color(palette)
    lit = _lit_edge_color(palette)
    night = _is_night(palette)

    w = int(100 * scale)
    h = int(30 * scale)
    pad = 6
    s = _alpha_surf(w + pad * 2, h + pad * 2)
    cx = pad + w // 2
    cy = pad + h // 2

    # Density map: dots cluster toward the centre with a soft elliptical
    # falloff. A normal-distribution sampler is heavier than needed — a
    # cheap radial probability check on a hash-jittered grid keeps the
    # call count predictable for the WASM target without bias toward any
    # particular pixel column.
    rng_seed = (int(x) * 0x9E37) ^ (int(y) * 0xC2B2)
    n_dots = 36

    # Pre-compute a 2D bell centred on (cx, cy) — dots survive if their
    # radial probability beats their hash-derived threshold.
    for k in range(n_dots):
        v1 = ((rng_seed + k * 0x27D4EB2F) & 0xFFFF) / 0xFFFF
        v2 = ((rng_seed + k * 0x9E3779B1) & 0xFFFF) / 0xFFFF
        v3 = ((rng_seed + k * 0x85EBCA77) & 0xFFFF) / 0xFFFF
        # Map (v1, v2) into the bounding box with a slight bias toward
        # centre so the cluster's silhouette is elliptical.
        bias = math.cos((v1 - 0.5) * math.pi)
        dx = int(_lerp(-w * 0.5, w * 0.5, v1))
        dy = int(_lerp(-h * 0.5, h * 0.5, v2) * bias)
        px = cx + dx
        py = cy + dy
        # Dots vary in radius and alpha so the constellation has rhythm
        # — uniform dots would read as a halftone print.
        rr = max(1, int(scale * (1.0 + v3 * 2.2)))
        a = int(_lerp(120, 240, v3))
        pygame.draw.circle(s, (*body, a), (px, py), rr)

    # 4 sparse warm-rim accent dots near the cluster's upper edge —
    # picks up sunset/golden light. Few enough that they read as
    # luminous flecks, not a halo. Gated by phase so night uses cool
    # lit-edge variants instead.
    accent_n = 4
    for k in range(accent_n):
        v = ((rng_seed + (k + 11) * 0x7F4A7C15) & 0xFFFF) / 0xFFFF
        ang = (k / accent_n) * math.tau
        ax = cx + int(math.cos(ang) * w * 0.30)
        ay = cy - int(h * 0.35) + int(v * h * 0.10)
        col = lit if not night else _lerp_color(lit, body, 0.4)
        pygame.draw.circle(s, (*col, 220), (ax, ay), max(1, int(scale * 1.4)))

    # A few darker ink-shadow dots clustered low so the constellation
    # has a centre-of-gravity rather than floating uniformly. Gated to
    # daytime — at night these read as gnats against the deep sky.
    if not night:
        for k in range(5):
            v1 = ((rng_seed + (k + 21) * 0xA9F86F1D) & 0xFFFF) / 0xFFFF
            v2 = ((rng_seed + (k + 21) * 0x9E3779B1) & 0xFFFF) / 0xFFFF
            sx = cx + int(_lerp(-w * 0.30, w * 0.30, v1))
            sy = cy + int(h * 0.25 + v2 * h * 0.15)
            pygame.draw.circle(s, (*edge, 130),
                               (sx, sy), max(1, int(scale * 1.5)))

    surf.blit(s, (int(x - cx), int(y - cy)))


# ─────────────────────────────────────────────────────────────────────────────
# Variant 5 — Origami Folded Crane-Cloud
# Research:
#   https://en.wikipedia.org/wiki/Origami
#   https://en.wikipedia.org/wiki/Orizuru
#
# Geometric ceremonial origami — pre-recreational, used for ritual gift
# decoration in the Heian period. Faceted crane-base silhouette
# rendered as a flat polygon cloud — angular planes catch a single
# bright "fold-crease" highlight, the rest is shaded. No round edges
# anywhere; the cloud is paper, not vapour. Aspect roughly 70 × 50, the
# faceted polygon family alone disqualifies the cumulus-puff read.
# ─────────────────────────────────────────────────────────────────────────────

def draw_cloud_origami(surf, x, y, palette, scale=1.0):
    """Faceted origami crane-base cloud — flat paper polygon planes."""
    body = _cloud_body_color(palette)
    edge = _ink_shadow_color(palette)
    lit = _lit_edge_color(palette)
    night = _is_night(palette)

    w = int(70 * scale)
    h = int(50 * scale)
    pad = 6
    s = _alpha_surf(w + pad * 2, h + pad * 2)

    cx = pad + w // 2
    cy = pad + h // 2

    # Two faceted plane tones — lit (top-left) and shaded (bottom-right)
    # — so the polygon reads as a folded sheet catching directional
    # light. Cool shadow tone is the body tint pulled toward edge to
    # keep the cloud in-key with the sky palette.
    face_lit = _lerp_color(body, lit, 0.35)
    face_shadow = _lerp_color(body, edge, 0.30)
    crease = _lerp_color(edge, body, 0.40)

    # Crane-base polygon — a stylised silhouette with a horizontal upper
    # body slab, two flanking wing-tips, and a tail-flick on the right.
    # Coordinates relative to (pad, pad); fold lines drawn over.
    body_poly = [
        (pad + int(w * 0.10), pad + int(h * 0.55)),  # left wing tip
        (pad + int(w * 0.28), pad + int(h * 0.28)),  # upper left fold
        (pad + int(w * 0.55), pad + int(h * 0.18)),  # apex / neck base
        (pad + int(w * 0.78), pad + int(h * 0.32)),  # upper right fold
        (pad + int(w * 0.92), pad + int(h * 0.50)),  # right wing tip
        (pad + int(w * 0.80), pad + int(h * 0.70)),  # tail flick out
        (pad + int(w * 0.55), pad + int(h * 0.78)),  # belly low
        (pad + int(w * 0.30), pad + int(h * 0.72)),  # belly left
    ]
    # Shadow plane base — the entire silhouette in the shaded tone first.
    pygame.draw.polygon(s, (*face_shadow, 240), body_poly)

    # Lit plane — the upper-left half of the silhouette. Polygon shares
    # the apex / wing-tip vertices but the diagonal split runs from the
    # left wing tip up through the apex and out the right shoulder, so
    # the brighter triangle sits where a top-left light source would
    # actually catch a folded paper plane.
    lit_poly = [
        (pad + int(w * 0.10), pad + int(h * 0.55)),
        (pad + int(w * 0.28), pad + int(h * 0.28)),
        (pad + int(w * 0.55), pad + int(h * 0.18)),
        (pad + int(w * 0.78), pad + int(h * 0.32)),
        (pad + int(w * 0.55), pad + int(h * 0.55)),
        (pad + int(w * 0.30), pad + int(h * 0.50)),
    ]
    pygame.draw.polygon(s, (*face_lit, 235), lit_poly)

    # Crease keyline — 1-px line running along the central fold from
    # belly up through apex out to right wing. This is the single line
    # that signals "paper" rather than "blob".
    crease_pts = [
        (pad + int(w * 0.55), pad + int(h * 0.78)),
        (pad + int(w * 0.55), pad + int(h * 0.18)),
        (pad + int(w * 0.92), pad + int(h * 0.50)),
    ]
    pygame.draw.lines(s, (*crease, 220), False, crease_pts,
                      max(1, int(scale * 1.2)))

    # Secondary crease — from apex down the diagonal of the lit plane to
    # the left wing's inner edge. A second crease is what makes the
    # silhouette read as crane-base (two wings + body) rather than a
    # generic kite shape.
    pygame.draw.line(
        s, (*crease, 180),
        (pad + int(w * 0.55), pad + int(h * 0.18)),
        (pad + int(w * 0.30), pad + int(h * 0.50)),
        max(1, int(scale)))

    # Full silhouette outline — 1 px line tracing the polygon perimeter
    # in a darker keyline so the paper edge stays crisp against busy
    # backdrops. Day-only alpha pulled higher because bright sky tends
    # to dissolve the lit-plane's perimeter.
    outline_a = 220 if not night else 170
    pygame.draw.lines(s, (*edge, outline_a), True, body_poly,
                      max(1, int(scale * 1.2)))

    # One sharp lit highlight at the apex peak — paper catches a sun
    # specular at fold vertices. Drawn as a tiny lit triangle so the
    # highlight has angular character matching the folded geometry.
    apex = (pad + int(w * 0.55), pad + int(h * 0.18))
    hi_pts = [
        apex,
        (apex[0] - max(2, int(scale * 3)), apex[1] + max(3, int(scale * 4))),
        (apex[0] + max(2, int(scale * 3)), apex[1] + max(3, int(scale * 4))),
    ]
    pygame.draw.polygon(s, (*lit, 230), hi_pts)

    surf.blit(s, (int(x - cx), int(y - cy)))


# ─────────────────────────────────────────────────────────────────────────────
# Variant 6 — Incense Smoke Volute
# Research:
#   https://www.angelicalbalance.com/spirituality/incense-smoke-pattern-meaning/
#   https://monianlife.com/blogs/news/how-to-interpret-incense-smoke-patterns
#
# Rising incense smoke curls in a vertical volute spiral that disperses
# at the top — read in East Asian temple iconography as the link
# between the offering and the heavens. Rendered here as a vertical
# coil: a tight inner spiral at the base growing into a loose dispersed
# alpha-bloom at the top. 40 × 80 px aspect — second vertical variant
# but the spiral DNA differs entirely from Sumeru's banded hourglass.
# ─────────────────────────────────────────────────────────────────────────────

def draw_cloud_smoke_volute(surf, x, y, palette, scale=1.0):
    """Rising incense-smoke spiral — tight coil dispersing into bloom."""
    body = _cloud_body_color(palette)
    edge = _ink_shadow_color(palette)
    lit = _lit_edge_color(palette)
    night = _is_night(palette)

    w = int(48 * scale)
    h = int(80 * scale)
    pad = 6
    s = _alpha_surf(w + pad * 2, h + pad * 2)

    cx = pad + w // 2

    # Parametric vertical spiral: r(t) widens with height, theta accumu-
    # lates around the column. The smoke is drawn as a chain of soft
    # alpha discs along the parametric curve, so the silhouette is the
    # smoke's path, not a fixed shape.
    n = 32
    for i in range(n):
        t = i / (n - 1)
        # Vertical position rises from bottom to top; radius bell grows
        # then disperses near the very top.
        py = pad + int(h * (1.0 - t))
        # Radius profile — tight near base (0.10w), bulges mid (0.45w),
        # disperses wide near top (0.55w). The bulge is the volute's
        # signature visible widening.
        if t < 0.3:
            r_amp = _lerp(0.10, 0.30, t / 0.3)
        elif t < 0.75:
            r_amp = _lerp(0.30, 0.50, (t - 0.3) / 0.45)
        else:
            r_amp = _lerp(0.50, 0.58, (t - 0.75) / 0.25)
        radius = w * 0.5 * r_amp
        # Angular sweep: 3 full revolutions across the column so the
        # spiral has visible coil structure at thumbnail scales.
        theta = t * math.tau * 2.5
        px = cx + int(math.cos(theta) * radius)
        # Disc radius shrinks toward the top so the bloom dissipates
        # rather than terminating with a hard cap.
        disc_r = max(2, int(scale * _lerp(4.5, 1.8, t)))
        # Alpha bell — dense at base, fading toward top.
        a = int(_lerp(220, 50, t))
        pygame.draw.circle(s, (*body, a), (px, py), disc_r)

    # Secondary inner spiral — half-radius, opposite phase — paints the
    # inside of the volute so the coil reads as 3D, not a flat ribbon.
    for i in range(n // 2):
        t = i / (n // 2 - 1)
        py = pad + int(h * (1.0 - t * 0.85))
        r_amp = _lerp(0.06, 0.28, t)
        radius = w * 0.5 * r_amp
        theta = t * math.tau * 2.0 + math.pi  # opposite phase
        px = cx + int(math.cos(theta) * radius)
        disc_r = max(1, int(scale * _lerp(3, 1.2, t)))
        a = int(_lerp(160, 30, t))
        pygame.draw.circle(s, (*edge, a), (px, py), disc_r)

    # Glowing source ember at the base — a single warm-lit dab anchors
    # the column so the spiral has an origin point. Night switches to
    # cool-lit so the ember reads as moonlit incense, not flame.
    ember_col = lit if not night else _lerp_color(lit, body, 0.40)
    ember_y = pad + h - 4
    pygame.draw.circle(s, (*ember_col, 230), (cx, ember_y),
                       max(2, int(scale * 3)))
    pygame.draw.circle(s, (*ember_col, 80), (cx, ember_y),
                       max(3, int(scale * 5)))

    surf.blit(s, (int(x - cx), int(y - (pad + h // 2))))


# ─────────────────────────────────────────────────────────────────────────────
# Variant 7 — Suzhou Embroidery Stitch
# Research:
#   https://www.suembroidery.com/chinese-silk-embroidery-blog/stitches-of-suzhou-embroidery
#   https://en.wikipedia.org/wiki/Chinese_embroidery
#
# Su xiu (苏绣) — the most celebrated Chinese silk embroidery — uses
# dense satin-stitch fill bound by couched-stitch outlines. Rendered
# here as a cloud silhouette stitched onto the sky: filled body with
# visible parallel stitch hatching, edge bound by an evenly-spaced
# chain of dot-stitches. The dots-on-contour edge treatment is what
# distinguishes this from every other variant — no smooth-arc keyline,
# no alpha gradient edge, the perimeter is explicitly granular.
# ─────────────────────────────────────────────────────────────────────────────

def draw_cloud_embroidery(surf, x, y, palette, scale=1.0):
    """Couched-stitch cloud — silk-embroidered silhouette with dot perimeter."""
    body = _cloud_body_color(palette)
    edge = _ink_shadow_color(palette)
    lit = _lit_edge_color(palette)
    night = _is_night(palette)

    w = int(72 * scale)
    h = int(38 * scale)
    pad = 6
    s = _alpha_surf(w + pad * 2, h + pad * 2)
    cx = pad + w // 2
    cy = pad + h // 2

    # Silk thread tone — body pushed slightly toward lit so the fill
    # reads as woven sheen, not flat paint.
    thread = _lerp_color(body, lit, 0.20)
    thread_shadow = _lerp_color(body, edge, 0.30)
    couch = _lerp_color(edge, body, 0.25)

    # Compute the cloud silhouette as a parametric closed curve — two
    # stacked half-lobes joined into a long pillow. Used both to fill
    # and to anchor the perimeter dots, so the stitches sit exactly on
    # the silhouette boundary.
    n_perim = 28
    perim = []
    for k in range(n_perim):
        t = k / n_perim
        ang = t * math.tau
        # Lemon-shape parametric: wider horizontally with a soft cosine
        # falloff vertically. Three rounded humps on the top, flatter
        # bottom so the silhouette has cloud rhythm without being a
        # geometric oval.
        rx = w * 0.45 * (1.0 + 0.08 * math.cos(ang * 3))
        ry = h * 0.45 * (1.0 + 0.15 * math.sin(ang * 2))
        # Top heavy, bottom flat: scale ry by cos-bias.
        if math.sin(ang) > 0:
            ry *= 1.10
        else:
            ry *= 0.75
        px = cx + int(math.cos(ang) * rx)
        py = cy - int(math.sin(ang) * ry)
        perim.append((px, py))

    # Satin-stitch fill — solid silhouette in the thread tone.
    pygame.draw.polygon(s, (*thread, 245), perim)

    # Horizontal satin-stitch hatching — short parallel lines simulating
    # the thread direction. Drawn as 1-px lines across the fill so the
    # cloud reads as textured silk, not flat colour. Lines clip to the
    # polygon naturally because anything outside ends up alpha-zero
    # against the surrounding transparent pixels.
    hatch_step = max(2, int(scale * 2.3))
    for hy in range(pad + 2, pad + h - 1, hatch_step):
        # Each hatch line spans the cloud's horizontal extent at this y.
        # Estimate the extent from the perimeter polygon's silhouette
        # half-width at this y via a cheap cosine model matching the
        # parametric above.
        rel_y = (cy - hy) / (h * 0.45)
        if abs(rel_y) >= 1.0:
            continue
        # Inverse of the parametric: solve for ang such that sin(ang) ≈
        # rel_y / vertical_scale. The hump pattern gives slightly
        # uneven extents, but the average is good enough for a hatch.
        if rel_y > 0:
            v_scale = 1.10
        else:
            v_scale = 0.75
        adj = max(-1.0, min(1.0, rel_y / v_scale))
        ang = math.asin(adj)
        rx = w * 0.45 * (1.0 + 0.08 * math.cos(ang * 3))
        half_w = int(abs(math.cos(ang)) * rx) - 2
        if half_w <= 1:
            continue
        # Alternate hatch tone every other line so the satin sheen has
        # subtle ridge variation — actual satin stitching shows this on
        # close inspection.
        col = thread if (hy // hatch_step) % 2 == 0 else thread_shadow
        pygame.draw.line(s, (*col, 220),
                         (cx - half_w, hy), (cx + half_w, hy), 1)

    # Couched-stitch perimeter — dots evenly spaced along the silhouette
    # boundary. Each dot is a tiny filled circle in the couch tone with
    # a 1-px inner highlight so it reads as a bead of thread, not a
    # screen artifact.
    dot_r = max(1, int(scale * 1.6))
    for (px, py) in perim:
        pygame.draw.circle(s, (*couch, 230), (px, py), dot_r)
        # Inner highlight only on day phases where the dots otherwise
        # blend with the lit body fill.
        if not night:
            pygame.draw.circle(s, (*lit, 200), (px - 1, py - 1),
                               max(1, dot_r - 1))

    # One curved "running-stitch" accent inside the body — a single
    # short arc of 3-4 dots near the cloud's top, simulating a
    # decorative inner stitch line. This is the silk-cloud's auspicious-
    # detail nod, kept very small so the perimeter dots stay the
    # dominant edge treatment.
    inner_arc_r = max(4, int(h * 0.20))
    for k in range(4):
        t = k / 3
        ang = math.radians(_lerp(195, 345, t))
        ix = cx + int(math.cos(ang) * inner_arc_r * 1.3)
        iy = cy - int(h * 0.15) + int(math.sin(ang) * inner_arc_r * 0.7)
        pygame.draw.circle(s, (*couch, 200), (ix, iy), max(1, dot_r - 1))

    surf.blit(s, (int(x - cx), int(y - cy)))


# ─────────────────────────────────────────────────────────────────────────────
# Variant 8 — Ruyi Lattice Window (the explicit single-Ruyi allowance)
# Research:
#   https://www.chinese-showcase.com/blogs/chinese-symbols/traditional-chinese-window-lattice
#   https://www.cits.net/china-travel-guide/fanciful-latticework-on-doors-and-windows.html
#
# Traditional Chinese paper-and-wood lattice windows used geometric
# cloud-cell motifs as translucent panels — the shadow of the lattice
# IS the window feature, not the view through it. This is the lineup's
# single allowed Ruyi reference, reframed entirely: a Ruyi-cell pattern
# rendered as a flat lattice silhouette inside a round moon-frame
# (月洞窗). The Ruyi shape lives inside an architectural window, not
# floating as a heraldic cloud — different formal language from rounds
# 23/24/25.
# ─────────────────────────────────────────────────────────────────────────────

def draw_cloud_ruyi_lattice(surf, x, y, palette, scale=1.0):
    """Moon-frame lattice window — Ruyi cell pattern as flat architecture."""
    body = _cloud_body_color(palette)
    edge = _ink_shadow_color(palette)
    lit = _lit_edge_color(palette)
    night = _is_night(palette)

    r = int(28 * scale)
    pad = 6
    s = _alpha_surf(r * 2 + pad * 2, r * 2 + pad * 2)
    cx = pad + r
    cy = pad + r

    # Moon-frame fill — translucent paper colour. Body pulled slightly
    # cool so the frame reads as a window panel against the sky, not a
    # second sun. Frame alpha kept moderate so the lattice silhouette
    # reads against the frame, not as a solid disc.
    frame_fill = _lerp_color(body, lit, 0.10)
    pygame.draw.circle(s, (*frame_fill, 180), (cx, cy), r)

    # Heavy round frame border — 2-3 px ring. Tone is the edge ink
    # pulled toward horizon so warm at sunset, cool at night.
    border = _lerp_color(edge, palette['horizon'], 0.30)
    pygame.draw.circle(s, (*border, 235), (cx, cy), r,
                       max(2, int(scale * 2)))

    # Inner Ruyi-cell lattice — three small interlocking ruyi-head shapes
    # arranged horizontally inside the moon. Drawn as line-only silhou-
    # ettes (no fills) so the lattice reads as a paper-stencil. Each
    # cell is a circle + downward arc tail = compressed ruyi glyph.
    cell_r = max(3, int(r * 0.32))
    cell_xs = (cx - int(r * 0.42), cx, cx + int(r * 0.42))
    lattice_a = 220 if not night else 170
    for i, lcx in enumerate(cell_xs):
        lcy = cy - int(r * 0.05)
        # Ruyi head — flat lattice circle.
        pygame.draw.circle(s, (*border, lattice_a), (lcx, lcy), cell_r,
                           max(1, int(scale)))
        # Inner curl — the lattice's calligraphic flourish, painted as
        # a short concentric arc so each cell still SAYS Ruyi at
        # thumbnail.
        inner_r = max(2, cell_r - 2)
        pygame.draw.arc(
            s, (*border, lattice_a - 30),
            pygame.Rect(lcx - inner_r, lcy - inner_r,
                        inner_r * 2, inner_r * 2),
            math.radians(20), math.radians(200), max(1, int(scale)))
        # Vertical lattice strut connecting cell to lower frame ring —
        # what makes the cells read as WINDOW LATTICE, not floating
        # symbols. Strut bottom touches the inner border ring.
        strut_top = (lcx, lcy + cell_r)
        strut_bot = (lcx, cy + int(r * 0.78))
        pygame.draw.line(s, (*border, lattice_a),
                         strut_top, strut_bot, max(1, int(scale)))

    # Horizontal cross-strut — single horizontal lattice bar tying the
    # three cells together at the strut joints. Without this the three
    # cells float; with it the lattice reads as one architectural
    # window unit.
    bar_y = cy + int(r * 0.45)
    pygame.draw.line(s, (*border, lattice_a),
                     (cx - int(r * 0.85), bar_y),
                     (cx + int(r * 0.85), bar_y),
                     max(1, int(scale)))

    # Lit crescent on the frame's upper-left rim — single moonlight
    # specular so the window has directional lighting without breaking
    # the flat-architecture read.
    pygame.draw.arc(
        s, (*lit, 220),
        pygame.Rect(cx - r + 2, cy - r + 2, r * 2 - 4, r * 2 - 4),
        math.radians(120), math.radians(220), max(1, int(scale * 2)))

    surf.blit(s, (int(x - cx), int(y - cy)))


# ── registries ───────────────────────────────────────────────────────────────

VARIANTS = {
    1: draw_cloud_yun_glyph,
    2: draw_cloud_sumeru_pillar,
    3: draw_cloud_mares_tail,
    4: draw_cloud_constellation,
    5: draw_cloud_origami,
    6: draw_cloud_smoke_volute,
    7: draw_cloud_embroidery,
    8: draw_cloud_ruyi_lattice,
}

VARIANT_NAMES = {
    1: "Yún Hanzi Glyph (雲)",
    2: "Sumeru Vertical Pillar",
    3: "Cirrus Mare's-Tail Streak",
    4: "Constellation Dot-Cloud",
    5: "Origami Folded Crane",
    6: "Incense Smoke Volute",
    7: "Suzhou Embroidery Stitch",
    8: "Ruyi Lattice Moon-Window",
}

VARIANT_SOURCES = {
    1: "https://en.wiktionary.org/wiki/%E4%BA%91 (云 yun pictographic)",
    2: "https://en.wikipedia.org/wiki/Mount_Meru_(Buddhism)",
    3: "https://en.wikipedia.org/wiki/Cirrus_uncinus_cloud",
    4: "https://en.wikipedia.org/wiki/Thirty-six_Views_of_Mount_Fuji",
    5: "https://en.wikipedia.org/wiki/Orizuru",
    6: "https://www.angelicalbalance.com/spirituality/incense-smoke-pattern-meaning/",
    7: "https://www.suembroidery.com/chinese-silk-embroidery-blog/stitches-of-suzhou-embroidery",
    8: "https://www.chinese-showcase.com/blogs/chinese-symbols/traditional-chinese-window-lattice",
}
