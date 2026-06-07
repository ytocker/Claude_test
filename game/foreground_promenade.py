"""LIVING PROMENADE — one Chinese-market street told as a full day's arc.

The sidewalk is driven by a DAY-ARC DIRECTOR (see `draw_promenade` below): a single
continuous story rather than a loop of interchangeable styles. Two signals from the
caller drive it — `phase` (biome day-cycle position) selects the dressing + cast
vocabulary and a crowd-density curve; `t` (= biome_time, 0 at run-start) ramps the
street in from empty as a run opens (the market "opening"). The arc:

  DAY    Morning market — prayer-flag bunting + a kiosk; vendors setting up
         (crate stacks), a songbird-cage stand, kids, a dog, a wish-tree.
  GOLDEN Afternoon — lamp posts + lantern garland go up; the elder on a bench.
  DUSK   Lamps lighting — a LAMPLIGHTER kindling the lanterns, strollers.
  NIGHT  Festival PEAK — garland + fairy lights + lamps glowing (capped), a
         campfire, a busy kiosk, full crowd. Then a near-empty PRE-DAWN teardown.

Dressing primitives (lamp posts, lantern garland, fairy lights, planters) come from
game.foreground_props; prayer-flag bunting from game.pillar_variants. The kids, the
elder, the kiosk, and the re-themed cast (wish-tree, songbird cage, lamplighter,
dawn set-up) are drawn here.

Glow contract preserved: capped under the coin (NIGHT_LUMA_CAP), gated to a dark
sky, and given a gentle dusk->night fade-in so dusk reads "lamps just lighting"
rather than dead-then-on. DAY/GOLDEN are unlit shells.

Pure-Pygame / pygbag-safe (fill, blit, draw.*, SRCALPHA, BLEND_RGB_ADD only).
No numpy / gfxdraw / per-frame surfarray. Nothing here is written into game/.
"""
from __future__ import annotations

import math
import random

import pygame

from game import foreground_props as sp
from game import biome as _biome
from game.config import W, H
from game.pillar_variants import draw_prayer_flags

# Read-only access to the live ambient characters — instantiated, stepped a few
# frames to a pleasant gait, then drawn at a chosen world-x.
from game.ambient import (
    _RunningDog, _WishingWell, _Bench, _Napper,
)

GROUND_Y = sp.GROUND_Y  # 595 — the sidewalk top edge; feet rest here.

_mix = sp._mix
_shade = sp._shade
_clamp = sp._clamp
_nightf = sp._nightf

# The festival's hard luma ceiling. The shared pillar-ornament cap is 153
# (0.60×coin), but the art-director measured a coin reading ~206 with isolated
# promenade lights hitting 255, so the promenade clamps every emitted core/glow
# colour a hair lower at 150 — comfortably under the coin, leaving the gold
# pickup the single brightest object anywhere on the night ground.
NIGHT_GLOW_CAP = 150


def _cap150(color):
    """Clamp each RGB channel to NIGHT_GLOW_CAP so no promenade light can rival
    the coin. Applied to every lit core, bulb and additive-halo colour."""
    return (min(int(color[0]), NIGHT_GLOW_CAP),
            min(int(color[1]), NIGHT_GLOW_CAP),
            min(int(color[2]), NIGHT_GLOW_CAP))


# ── glow gate: one monotonic dusk->night fade-in for the whole festival ───────
#
# r15's _add_lamp_glow only begins above night-ness 0.45 (dead at dusk) while its
# lit bulb FACES snapped to full brightness the instant the sky went dark — so
# dusk blew out (faces near-full, no halo) instead of "lamps just beginning".
# The promenade now drives BOTH the lit-face colour AND the halo from one shared
# intensity curve so the ramp is monotonic: dusk lands at ~45% of night, night
# at 100%, and nothing is lit by day. Every emitted colour is then clamped to
# NIGHT_GLOW_CAP so the coin stays the brightest object.

def _lit_intensity(pal):
    """0 by day, ~0.40 at dusk (lamps JUST beginning to glow), 1.0 at full night.
    Monotonic in night-ness. Drives lit faces and halos in lockstep.

    The dusk floor is held a notch under night so EVERY emitter face is dimmer at
    dusk than at night (per-element, not just on average) — the dusk bulb/lamp
    faces were landing marginally hotter than the full-night set, so the floor was
    pulled from 0.45 to 0.40 (~10% down) while night stays pinned at 1.0."""
    if not sp._is_dark_sky(pal):
        return 0.0
    night = _nightf(pal)
    # Map the dusk night-ness (~0.38) to 0.40 and full night (~1.0) to 1.0 with a
    # gentle floor so the first lit phase reads as "coming on", not dead.
    return 0.40 + 0.60 * max(0.0, min(1.0, (night - 0.38) / 0.62))


def _glow_strength(pal):
    """Halo strength shares the lit-intensity curve (kept as a name for the
    primitives), so a dusk halo is a soft ~45% of the full night bloom."""
    return _lit_intensity(pal)


def _glow(surf, cx, cy, pal, *, radius=14, color=(255, 196, 110), scale=1.0):
    """Capped warm halo with the promenade's monotonic dusk->night curve. The
    halo colour is capped at NIGHT_GLOW_CAP before the peak ratio so even a halo
    landing on a lit face can't sum past the coin."""
    s = _glow_strength(pal)
    if s <= 0.02:
        return
    peak = int(sp._GLOW_PEAK * scale * s)
    if peak <= 1:
        return
    g = sp._warm_glow(radius, _cap150(color), peak)
    surf.blit(g, (cx - radius - 1, cy - radius - 1), special_flags=pygame.BLEND_RGB_ADD)


# ── retrofit the borrowed r15 primitives to the 150 cap + dusk ramp ───────────
#
# The lamp posts, lantern garland and fairy lights are r15 helpers that bake in
# the old 153 cap and the dead-at-dusk halo gate. Rather than fork them, the
# promenade rebinds the two seams they share — the night-luma clamp and the halo
# blitter — so every borrowed light obeys NIGHT_GLOW_CAP and the monotonic
# dusk->night intensity. _CUR_PAL is set by each phase painter so the seam funcs
# (which don't receive `pal`) can read the current intensity.

_CUR_PAL = None

# Additive halos sum onto whatever they sit over, so the peak is held LOW and the
# lit faces underneath are capped well below 150 (see _LIT_FACE_CAP) — base-face +
# full halo must still land ≤150 luma so no promenade light can rival the coin.
sp._GLOW_PEAK = 24

# Lit faces (bulbs, lantern panels) are capped here, BELOW NIGHT_GLOW_CAP, so a
# warm additive halo summed on top still clears the 150 ceiling.
_LIT_FACE_CAP = 122


def _capped_clamp_night(color, alpha=255):
    """Replacement for sp._clamp_night: clamp each lit face to _LIT_FACE_CAP (under
    NIGHT_GLOW_CAP, leaving headroom for an additive halo), then pull the face
    toward a dark ember by the dusk ramp so dusk faces are clearly dimmer than
    night faces (no snap-to-bright at first dark)."""
    r, g, b = color[:3]
    lit = (min(int(r), _LIT_FACE_CAP),
           min(int(g), _LIT_FACE_CAP),
           min(int(b), _LIT_FACE_CAP))
    s = _lit_intensity(_CUR_PAL) if _CUR_PAL is not None else 1.0
    # Unlit ember the face fades toward when the lamps are only "coming on".
    ember = (int(lit[0] * 0.42), int(lit[1] * 0.34), int(lit[2] * 0.30))
    out = _mix(ember, lit, s)
    return (out[0], out[1], out[2], alpha)


def _capped_add_glow(surf, cx, cy, pal, *, radius=16, alpha=120, color=(255, 196, 110)):
    """Replacement for sp._add_lamp_glow using the promenade's monotonic intensity
    (alive from dusk) and the 150-capped halo colour."""
    if not sp._is_dark_sky(pal):
        return 0.0
    s = _lit_intensity(pal)
    if s <= 0.02:
        return 0.0
    peak = int(min(sp._GLOW_PEAK, sp._GLOW_PEAK * (alpha / 120.0)) * s)
    if peak <= 1:
        return s
    g = sp._warm_glow(radius, _cap150(color), peak)
    surf.blit(g, (cx - radius - 1, cy - radius - 1), special_flags=pygame.BLEND_RGB_ADD)
    return s


sp._clamp_night = _capped_clamp_night
sp._add_lamp_glow = _capped_add_glow


# ── lighten the festival WIRE so the eye reads "bulbs on a line" ──────────────
#
# The r15 garland rope / fairy wire were dark (≈62,52,44) so at night the strung
# spans read as black scribble crisscrossing the upper band. The promenade draws
# the wire as ONE thin catenary per span lifted toward the sky value (a faint
# semi-transparent line), so only the bulbs carry weight. Both strand drawers are
# re-bound to use this faint-wire variant; only the rope colour changes.

def _faint_wire_color(pal):
    """A single hairline wire tinted toward the night sky so it nearly dissolves —
    the bulbs, not the string, should read."""
    sky = pal.get('sky_top', (60, 120, 200))
    # Lift a dark cord most of the way to the sky value; semi-transparent on top.
    # Pulled one step further toward sky (0.55 -> 0.64) so the whole catenary set
    # reads at one uniform faint value — no single span squiggles darker than the
    # rest where it crosses a darker patch of sky.
    return _mix((60, 54, 50), sky, 0.64)


def _draw_faint_catenary(surf, xl, xr, top_y, sag, steps, pal):
    col = _faint_wire_color(pal)
    pts = sp._catenary_pts(xl, xr, top_y, sag, steps)
    layer = pygame.Surface((surf.get_width(), surf.get_height()), pygame.SRCALPHA)
    pygame.draw.lines(layer, (*col, 150), False,
                      [(int(x), int(y)) for x, y in pts], 1)
    surf.blit(layer, (0, 0))


def _garland_faint(surf, w, scroll, pal, *, top_y, period=120, sag=24,
                   per_span=3, colors=('red', 'gold')):
    """r15 lantern garland with the faint single-catenary wire."""
    for xl, xr in sp._garland_spans(scroll, w, period, x0=12):
        _draw_faint_catenary(surf, xl, xr, top_y, sag, 16, pal)
        for j in range(per_span):
            tt = (j + 0.5) / per_span
            bx, by = sp._span_point(xl, xr, top_y, sag, tt)
            sp._draw_lantern_head(surf, int(bx), int(by), pal,
                                  color=colors[j % len(colors)], scale=0.6,
                                  glow_radius=7, glow_alpha=52)


def _fairy_faint(surf, w, scroll, pal, *, top_y, period=200, sag=26, per_span=5):
    """r15 fairy lights with the faint single-catenary wire + capped warm bulbs."""
    dark = sp._is_dark_sky(pal)
    warm = (250, 200, 120)
    bead = _mix(warm, (118, 108, 94), 0.55)
    for xl, xr in sp._garland_spans(scroll, w, period, x0=8):
        _draw_faint_catenary(surf, xl, xr, top_y, sag, 20, pal)
        for j in range(per_span):
            tt = (j + 0.5) / per_span
            bx, by = sp._span_point(xl, xr, top_y, sag, tt)
            bx, by = int(bx), int(by) + 2
            if dark:
                lit = sp._clamp_night(warm)[:3]
                pygame.draw.circle(surf, _mix(lit, (110, 78, 46), 0.4), (bx, by), 3)
                pygame.draw.circle(surf, lit, (bx, by), 2)
                sp._add_lamp_glow(surf, bx, by, pal, radius=7, alpha=54, color=warm)
            else:
                pygame.draw.circle(surf, _shade(bead, -10), (bx, by), 3)
                pygame.draw.circle(surf, bead, (bx, by), 2)


sp._draw_lantern_garland = _garland_faint
sp._draw_fairy_lights = _fairy_faint


# ══════════════════════════════════════════════════════════════════════════
# NEW characters
# ══════════════════════════════════════════════════════════════════════════
#
# All live in the lower promenade band (feet at GROUND_Y) and are kept clear of
# the bird lane (x≈48..188) and the pillar lane (x≈212..320) by their chosen
# world-x anchors. They borrow the _draw_bench_person body idiom so the new
# people match the existing bench couple in scale and palette.


def _retint_person(col, night):
    """Cool a clothing colour toward the night ground band so a new figure sits
    in the same value family as the retinted floor (matches the bench tint)."""
    if night <= 0.05:
        return col
    # A firm floor on the cool so even at dusk a bright skin/cloth face is pulled
    # well under the festival lights; ramps further toward full night.
    return _mix(col, (54, 64, 96), min(0.55, 0.40 * night + 0.20))


def _draw_bench_person(surf, x_base, body_y, shirt, shirt_dk, hair, *, night=0.0):
    """A small seated/standing figure, mirroring the live game body idiom but with
    the skin RETINTED at night so a face never reads brighter than 150 luma (the
    live helper hardcodes a (235,195,150) skin that out-shone the cap after dusk)."""
    skin = _retint_person((235, 195, 150), night)
    pygame.draw.rect(surf, shirt, (x_base, body_y, 6, 8))
    pygame.draw.rect(surf, shirt_dk, (x_base, body_y, 6, 8), 1)
    head_y = body_y - 3
    pygame.draw.circle(surf, skin, (x_base + 3, head_y), 3)
    pygame.draw.polygon(surf, hair,
                        [(x_base, head_y), (x_base + 6, head_y),
                         (x_base + 3, head_y - 4)])
    pygame.draw.circle(surf, (30, 20, 15), (x_base + 2, head_y + 1), 0)
    pygame.draw.circle(surf, (30, 20, 15), (x_base + 4, head_y + 1), 0)


def draw_kids(surf, sx, pal, *, t=0.0, n=3):
    """2-3 small walking/playing children: shorter, rounder, brighter-clothed
    than the bench adults. Built from a scaled-down _draw_bench_person idiom — a
    little body block + round head + simple hair — with a playful gait bob and a
    couple of stubby running legs so they read as kids at play, not statues."""
    night = _nightf(pal)
    skin = _retint_person((235, 195, 150), night)
    # Bright primary clothes so the kids pop against the muted shan-shui floor.
    kit = [
        ((235, 95, 90), (175, 55, 60), (90, 55, 35)),    # red shirt
        ((90, 165, 220), (50, 110, 165), (60, 45, 35)),  # blue shirt
        ((250, 200, 70), (200, 150, 40), (70, 50, 35)),  # yellow shirt
    ]
    # Wider spread so the kids don't stack; depth-staggered lift keeps them apart.
    spread = (-13, 9, 26)
    for i in range(n):
        dx = spread[i]
        shirt, shirt_dk, hair = (_retint_person(c, night) for c in kit[i])
        # Each kid bobs on its own phase so the group reads as alive — but SLOW
        # and small (ground-locked; a fast run cycle would moonwalk).
        gait = math.sin(t * 1.8 + i * 1.7)
        lift = -max(0.0, gait) * 0.8  # only the up-swing lifts
        bx = sx + dx
        feet_y = GROUND_Y - 1 + int(round(lift))
        # CHIBI proportions: a tiny 4px torso under a big 3px head -> total ~7px,
        # ~60% the adult's ~11px so a kid beside an adult instantly reads "child".
        body_h = 4
        body_w = 4
        head_r = 3
        body_y = feet_y - body_h - 2
        # Rounder torso (filled ellipse, not a hard rect) + bright shirt.
        pygame.draw.ellipse(surf, shirt, (bx, body_y, body_w, body_h + 1))
        pygame.draw.ellipse(surf, shirt_dk, (bx, body_y, body_w, body_h + 1), 1)
        # Oversized head relative to body — the universal "child" cue.
        hx, hy = bx + body_w // 2, body_y - head_r + 1
        pygame.draw.circle(surf, skin, (hx, hy), head_r)
        # ROUND-CAP hair, NOT a cone: a domed half-disc capping the crown so the
        # kids read as round-headed children (day AND night), never as the
        # conical-hatted pilgrims/gnomes the old triangle suggested.
        pygame.draw.arc(surf, hair, (hx - head_r, hy - head_r, head_r * 2 + 1, head_r * 2 + 1),
                        math.radians(0), math.radians(180), head_r)
        pygame.draw.circle(surf, (30, 20, 15), (hx - 1, hy), 0)
        pygame.draw.circle(surf, (30, 20, 15), (hx + 1, hy), 0)
        # Two stubby legs with a small shuffle (not a sprint).
        leg = _shade(shirt_dk, -18)
        swing = int(round(gait * 1))
        pygame.draw.line(surf, leg, (bx + 1, body_y + body_h),
                         (bx + 1 - swing, feet_y), 1)
        pygame.draw.line(surf, leg, (bx + body_w - 1, body_y + body_h),
                         (bx + body_w - 1 + swing, feet_y), 1)
        # Most kids reach an arm up (chasing / waving) — the playful pose the AD
        # liked; alternate which arm so the group has varied silhouettes.
        if i != 1:
            ax = bx + body_w - 1 if i % 2 == 0 else bx
            adx = 2 if i % 2 == 0 else -2
            pygame.draw.line(surf, shirt, (ax, body_y + 1),
                             (ax + adx, body_y - 2 - max(0, swing)), 1)


def draw_old_man(surf, sx, pal, *, t=0.0, seated_bench=False):
    """A TEMPLE ELDER — built so the 1× silhouette alone reads "old man with a
    cane": a bald/grey domed head (NO conical hat — that's the kids), a deeply
    STOOPED back, a long wispy grey beard reaching the chest, a muted plum/indigo
    robe so he can't be mistaken for the bright-shirted children, and a long
    hooked CANE whose shaft runs the full body height down to the deck. The cane +
    stoop + beard are the three unmistakable elder cues, sized up from the prior
    too-subtle figure. `seated_bench` sits him a touch lower."""
    night = _nightf(pal)
    skin = _retint_person((222, 186, 148), night)
    # A muted plum/indigo robe — a cool violet that sits apart from the kids'
    # warm primaries and the bench couple's reds, so the elder owns his own hue.
    robe = _retint_person((92, 72, 108), night)
    robe_dk = _retint_person((58, 44, 74), night)
    grey = _retint_person((212, 210, 202), night)      # grey hair/beard, near-white
    cane_c = _retint_person((118, 80, 48), night)

    feet_y = GROUND_Y - 1
    # A TALLER robe block than the adults so the stoop has room to curve, and a
    # wider hem so the bent-over posture reads as a heavy robe, not a thin coat.
    body_h = 11 if not seated_bench else 9
    body_w = 7
    body_y = feet_y - body_h - (2 if not seated_bench else 0)
    # PRONOUNCED forward stoop: the shoulders lean a full 3-4px over the feet so
    # the silhouette is a clear hunched curve, the universal "elder" read.
    lean = 4 if not seated_bench else 2
    # Robe as a bent-over wedge: narrow stooped shoulders up front, broad hem.
    pygame.draw.polygon(surf, robe, [
        (sx + lean, body_y + 2), (sx + body_w + lean - 1, body_y),
        (sx + body_w + 1, body_y + body_h), (sx - 1, body_y + body_h)])
    pygame.draw.polygon(surf, robe_dk, [
        (sx + lean, body_y + 2), (sx + body_w + lean - 1, body_y),
        (sx + body_w + 1, body_y + body_h), (sx - 1, body_y + body_h)], 1)
    # A hunched upper-back hump where the stoop bends — extra elder cue.
    pygame.draw.circle(surf, robe_dk, (sx + 1, body_y + 2), 2)
    # Head tipped forward over the stoop. BALD/grey dome (a thin grey skull-cap of
    # hair, no peak) so it can never read as a kid's conical hat.
    hx, hy = sx + body_w // 2 + lean, body_y - 2
    pygame.draw.circle(surf, skin, (hx, hy), 3)
    # Domed grey hair fringe — a flat semicircle hugging the skull, not a cone.
    pygame.draw.arc(surf, grey, (hx - 3, hy - 4, 7, 7),
                    math.radians(0), math.radians(180), 2)
    # LONG wispy beard — a tapering grey wedge reaching well down the chest, the
    # clearest temple-elder cue at 1×.
    pygame.draw.polygon(surf, grey, [
        (hx - 2, hy + 2), (hx + 2, hy + 2), (hx + 1, hy + 8), (hx - 1, hy + 8)])
    pygame.draw.circle(surf, _shade(grey, -30), (hx, hy + 6), 1)  # beard tip wisp
    pygame.draw.circle(surf, (30, 20, 15), (hx, hy), 0)
    # The CANE — drawn for both standing and seated so the elder always carries
    # it. A long shaft from the leading hand all the way DOWN to the deck plus a
    # clear hooked crook, so the silhouette plainly says "old man with a cane".
    tap = int(round(math.sin(t * 1.3) * 1)) if not seated_bench else 0
    cx0 = sx + body_w + lean + 2
    hand_y = body_y + 3
    pygame.draw.line(surf, cane_c, (cx0, hand_y), (cx0 + tap, feet_y), 2)
    # Hooked crook curling back toward the hand.
    pygame.draw.line(surf, cane_c, (cx0, hand_y), (cx0 - 3, hand_y), 2)
    pygame.draw.line(surf, cane_c, (cx0 - 3, hand_y), (cx0 - 3, hand_y + 2), 2)
    if not seated_bench:
        # Two robe-hem feet shuffling.
        pygame.draw.line(surf, robe_dk, (sx + 1, body_y + body_h),
                         (sx + 1, feet_y), 1)
        pygame.draw.line(surf, robe_dk, (sx + body_w - 1, body_y + body_h),
                         (sx + body_w - 1 + tap, feet_y), 1)


def draw_flock(surf, sx, pal, *, t=0.0, n=3):
    """A grazing flock of WOOLLY sheep. The live _SheepPack sprite reads at 1× as
    a small dark-headed blob on thin tall legs — ambiguous, almost a bird on a
    post. These are unmistakably sheep: each body is a fat rounded woolly OVAL
    (clearly wider than tall) with a bumpy fleece top, SHORT stubby legs, and one
    dark head bump at the front. A trailing lamb closes the group."""
    night = _nightf(pal)
    wool = _retint_person((238, 234, 226), night)
    wool_sh = _retint_person((205, 198, 188), night)
    wool_hi = _retint_person((250, 248, 244), night)
    face = _retint_person((70, 62, 60), night)         # dark head + legs
    spread = (-26, -6, 16, 32)   # 3 ewes + a trailing lamb
    for i in range(n + 1):
        adult = i < n
        dx = spread[i]
        bw = 16 if adult else 11        # body WIDER than tall -> reads woolly
        bh = 9 if adult else 6
        bx = sx + dx
        # A gentle grazing bob so the still frame still feels alive.
        bob = int(round(max(0.0, math.sin(t * 2.0 + i * 1.3)) * 1.0))
        feet_y = GROUND_Y - 1
        body_y = feet_y - bh - 2 - bob
        # SHORT stubby legs (2px) — not the thin tall posts that read as a bird perch.
        for lx in (bx + 3, bx + bw - 4):
            pygame.draw.line(surf, face, (lx, body_y + bh - 1), (lx, feet_y), 1)
        # Fat woolly body oval.
        pygame.draw.ellipse(surf, wool_sh, (bx, body_y, bw, bh))
        pygame.draw.ellipse(surf, wool, (bx, body_y, bw, bh - 1))
        # Bumpy fleece across the top so it clearly reads as wool, not a smooth egg.
        br = 2
        cx = bx + br + 1
        while cx <= bx + bw - br - 1:
            pygame.draw.circle(surf, wool_hi, (cx, body_y + br), br)
            cx += br + 1
        # One clear DARK head bump at the front (right) — the "this is a sheep" cue.
        hx = bx + bw - 1
        pygame.draw.circle(surf, face, (hx, body_y + 2), 3 if adult else 2)
        pygame.draw.circle(surf, _shade(face, 18), (hx + 1, body_y + 1), 1)  # ear/snout nub


def draw_strollers(surf, sx, pal, *, t=0.0):
    """A couple of strolling adults for the quiet DUSK event — the bench-person
    idiom walking, with a slow gait and a small head bob. Calm, unhurried."""
    night = _nightf(pal)
    pairs = [((180, 120, 170), (130, 80, 120), (70, 50, 40)),   # plum coat
             ((90, 140, 165), (55, 95, 115), (60, 45, 35))]      # teal coat
    for i, (shirt, shirt_dk, hair) in enumerate(pairs):
        shirt, shirt_dk, hair = (_retint_person(c, night) for c in (shirt, shirt_dk, hair))
        dx = -8 + i * 14
        # Slow, small gait: these figures are pinned to the deck, so a brisk walk
        # cycle reads as moonwalking. Gentle weight-shift + nearly-planted feet.
        gait = math.sin(t * 0.8 + i * 1.1)
        feet_y = GROUND_Y - 1 - int(round(max(0.0, gait) * 0.5))
        body_y = feet_y - 8 - 3
        _draw_bench_person(surf, sx + dx, body_y, shirt, shirt_dk, hair, night=night)
        # Legs barely shift under the body block.
        leg = _shade(shirt_dk, -16)
        sw = int(round(gait * 1))
        pygame.draw.line(surf, leg, (sx + dx + 1, body_y + 8),
                         (sx + dx + 1 - sw, feet_y), 1)
        pygame.draw.line(surf, leg, (sx + dx + 4, body_y + 8),
                         (sx + dx + 4 + sw, feet_y), 1)


# ── KIOSK / vendor stall: a pagoda-roofed market stall ───────────────────────
#
# Net-new. A small temple-market stall: a tiered curved pagoda roof, a striped
# awning, a counter with goods, a hanging paper lantern, and (optionally) a tiny
# vendor head behind the counter. World-anchored on the sidewalk at GROUND_Y,
# kept narrow so it slots into a clear strip without crowding the bird/pillar
# lanes. Its "open-ness" escalates: shutter down by day, goods + awning by
# golden, the lantern lit at dusk/night.

def _pagoda_roof(surf, cx, ridge_y, half_w, pal, *, tiers=2):
    """A tiered, upswept temple roof. Each tier is a low trapezoid with curled
    eave tips drawn as short up-flicks, in the stage stone tones so it belongs to
    the pagoda pillar's masonry family."""
    night = _nightf(pal)
    tile = _mix(pal.get('stone_dark', (95, 80, 70)), (120, 96, 78), 0.5)
    tile = _mix(tile, (54, 60, 86), 0.32 * night)
    tile_lt = _shade(tile, 18)
    ridge = _shade(tile, -22)
    y = ridge_y
    hw = half_w
    for ti in range(tiers):
        eave_y = y + 7
        # Roof slab as a trapezoid wider at the eave.
        pygame.draw.polygon(surf, tile, [
            (cx - hw * 0.4, y), (cx + hw * 0.4, y),
            (cx + hw, eave_y), (cx - hw, eave_y)])
        pygame.draw.line(surf, tile_lt, (cx - hw * 0.4, y), (cx + hw * 0.4, y), 1)
        # Upswept eave tips (the temple curl).
        pygame.draw.line(surf, ridge, (cx - hw, eave_y), (cx - hw - 2, eave_y - 3), 2)
        pygame.draw.line(surf, ridge, (cx + hw, eave_y), (cx + hw + 2, eave_y - 3), 2)
        y = eave_y - 1
        hw = int(hw * 0.78)
    # A small finial knob on the ridge.
    pygame.draw.circle(surf, _shade(tile_lt, 10), (int(cx), int(ridge_y - 2)), 1)


def draw_kiosk(surf, sx, pal, *, t=0.0, openness=1.0):
    """A pagoda-roofed vendor stall on the sidewalk. `openness` 0..1 escalates
    the read: 0 -> just opening (low shutter, no goods), 1 -> fully open (awning
    out, goods on the counter, a vendor, a lit hanging lantern at night)."""
    night = _nightf(pal)
    base_y = GROUND_Y - 1
    half_w = 22
    counter_h = 16
    post_top = base_y - 34   # counter + a head-height opening under the roof

    # Two corner posts (timber).
    post = _mix((92, 64, 40), (60, 66, 92), 0.30 * night)
    post_dk = _shade(post, -20)
    for px in (sx - half_w + 3, sx + half_w - 3):
        pygame.draw.rect(surf, post, (px - 1, post_top, 3, base_y - post_top))
        pygame.draw.line(surf, post_dk, (px + 1, post_top), (px + 1, base_y), 1)

    # Back wall panel between posts (so the stall reads as enclosed, not a frame).
    wall = _mix(pal.get('stone_mid', (150, 132, 110)), (150, 124, 96), 0.5)
    wall = _mix(wall, (56, 62, 88), 0.32 * night)
    pygame.draw.rect(surf, _shade(wall, -10),
                     (sx - half_w + 4, post_top + 2, (half_w - 4) * 2, 14))

    # The pagoda roof crowning the posts.
    _pagoda_roof(surf, sx, post_top - 8, half_w + 2, pal, tiers=2)

    # Counter / shop front.
    counter = _mix((120, 84, 52), (60, 66, 92), 0.30 * night)
    counter_lt = _shade(counter, 16)
    cy = base_y - counter_h
    pygame.draw.rect(surf, counter, (sx - half_w + 1, cy, (half_w - 1) * 2, counter_h))
    pygame.draw.rect(surf, counter_lt, (sx - half_w + 1, cy, (half_w - 1) * 2, 2))
    pygame.draw.rect(surf, _shade(counter, -22),
                     (sx - half_w + 1, base_y - 4, (half_w - 1) * 2, 4))

    if openness > 0.25:
        # A striped awning rolled out over the counter (the "open for business"
        # cue). Two-tone scalloped valance.
        aw = half_w + 1
        ay = cy - 5
        # The cream stripe is pulled HARD toward the night ground from dusk on so
        # the unlit awning never reads brighter than the festival lights or coin.
        dimk = min(0.72, 1.3 * night)
        stripe_a = _mix((210, 70, 60), (70, 70, 96), min(0.6, 0.9 * night))
        stripe_b = _mix((240, 228, 210), (74, 80, 104), dimk)
        for i, ax in enumerate(range(sx - aw, sx + aw, 6)):
            col = stripe_a if i % 2 == 0 else stripe_b
            pygame.draw.polygon(surf, col, [
                (ax, ay), (ax + 6, ay), (ax + 6, ay + 4), (ax + 3, ay + 6), (ax, ay + 4)])

    if openness > 0.5:
        # Goods on the counter — a few coloured produce/jar lumps so it reads as
        # a market stall, not an empty booth.
        goods = [((230, 120, 60), 3), ((90, 160, 90), 2), ((220, 200, 90), 3),
                 ((200, 80, 90), 2)]
        gx = sx - half_w + 6
        for col, r in goods:
            col = _mix(col, (58, 66, 96), min(0.6, 0.85 * night))
            pygame.draw.circle(surf, _shade(col, -16), (gx, cy - 1), r)
            pygame.draw.circle(surf, col, (gx, cy - 2), r - 1)
            gx += r + 5
        # A tiny vendor head peeking over the counter behind the goods.
        vx = sx + half_w - 9
        skin = _retint_person((226, 190, 150), night)
        pygame.draw.circle(surf, skin, (vx, cy - 4), 3)
        pygame.draw.polygon(surf, _retint_person((70, 50, 40), night),
                            [(vx - 3, cy - 4), (vx + 3, cy - 4), (vx, cy - 8)])

    # A hanging paper lantern under the eave — lit (capped) once the sky darkens.
    lx = sx + half_w - 7
    ly = post_top - 1
    # Drive the WHOLE lantern (dark shell + lit face) off the shared dusk->night
    # intensity so the kiosk lantern is strictly dimmer at dusk than at night,
    # per-element — the dark shell no longer brightens as the sky lightens.
    s = _lit_intensity(pal)
    lan_dark = _mix((96, 28, 28), (150, 38, 38), s)
    lan_lit = (sp._clamp_night((250, 110, 80))[:3] if sp._is_dark_sky(pal)
               else (210, 110, 80))
    pygame.draw.line(surf, (50, 35, 25), (lx, ly), (lx, ly + 4), 1)
    body = pygame.Rect(lx - 4, ly + 4, 8, 10)
    pygame.draw.ellipse(surf, lan_dark, body)
    pygame.draw.ellipse(surf, lan_lit, body.inflate(-3, -2))
    _glow(surf, lx, ly + 9, pal, radius=10, color=(255, 150, 110), scale=0.7)


# ── capped campfire + capped napper Z's ───────────────────────────────────────
#
# The live _Campfire and _Napper paint pure-white hot pixels (flame tip
# (255,250,220), sparks (255,240,200), sleep-"z" (215,215,235)) that blew past
# the coin at night. They live in game/ and must not be edited, so the promenade
# reuses their cached tent/logs/halo geometry but repaints the LIT parts with a
# warm amber core and capped sparks of its own, and draws its own dimmed Z's.

import game.ambient as _amb

# A warm amber spark palette in place of the live white-ish set; kept dim so even
# an additive spark summed over the warm halo + floor stays under the 150 ceiling.
_CAMP_SPARKS = ((92, 60, 26), (92, 70, 32), (84, 52, 24))


def draw_campfire(surf, sx, pal, *, t=0.0):
    """A world-anchored campfire matching the live one's silhouette, but with a
    warm amber (capped) core instead of a white-hot centre and amber sparks, so
    no fire pixel exceeds NIGHT_GLOW_CAP and the coin stays brightest."""
    x = sx
    y = GROUND_Y - 24
    s = _lit_intensity(pal)
    # Cached tent + logs (unlit geometry) and the warm radial halo. The halo is
    # scaled DOWN hard (and by the dusk->night intensity) so that even where it
    # sums onto the solid amber flame the total stays ≤150 luma — additive light
    # cannot push the fire past the coin.
    if s > 0.02:
        halo = _amb._build_campfire_halo().copy()
        k = int(255 * 0.12 * s)
        halo.fill((k, k, k, 255), special_flags=pygame.BLEND_RGBA_MULT)
        hr = _amb._CAMPFIRE_HALO_RADIUS
        surf.blit(halo, (x - hr, y - 4 - hr), special_flags=pygame.BLEND_RGB_ADD)
    solid = _amb._get_campfire_solid()
    surf.blit(solid, (x - _amb._CAMP_FIRE_LX, y - _amb._CAMP_FIRE_LY))
    # Amber flame — warm amber core, NOT the live white tip. Channels kept low so
    # base flame + the (already small) additive halo above stays under 150 luma.
    flicker = (math.sin(t * 12.0) * 0.5 + math.sin(t * 7.5 * 1.3) * 0.5)
    h_off = int(round(flicker * 1.5))
    amber_lo = (110, 48, 26)
    amber_mid = (128, 72, 36)
    amber_hi = (138, 96, 46)   # warm amber core (luma ≈101), never white
    pygame.draw.ellipse(surf, amber_lo, (x - 5, y - 7 - h_off, 10, 8 + h_off))
    pygame.draw.ellipse(surf, amber_mid, (x - 4, y - 8 - h_off, 8, 8 + h_off))
    pygame.draw.ellipse(surf, amber_hi, (x - 2, y - 8 - h_off, 5, 7 + h_off))
    pygame.draw.ellipse(surf, amber_hi, (x - 1, y - 6 - h_off, 3, 4 + h_off))
    # Amber sparks rising — capped and started ABOVE the flame tip so an additive
    # spark never sums onto the solid flame core (which would blow the cap).
    for i in range(6):
        ph = (t * 0.9 + i * 0.37) % 1.0
        spx = x + int(math.sin(i * 1.7 + t) * 6)
        spy = y - 12 - int(ph * 20)   # origin above the flame, rising into dark sky
        a = int(120 * (1.0 - ph) * max(0.2, s))
        if a > 6:
            layer = pygame.Surface((2, 2), pygame.SRCALPHA)
            layer.fill((*_CAMP_SPARKS[i % 3], a))
            surf.blit(layer, (spx, spy), special_flags=pygame.BLEND_RGB_ADD)


def draw_napper(surf, sx, pal, *, t=0.0):
    """The live napper sprite (a sleeping figure on a mat) plus dimmed, warm-grey
    sleep-Z's. The live Z colour (215,215,235) is a near-white that blew the dusk
    luma cap, so the promenade redraws the Z's at <=150 luma in a cool grey that
    matches the night ground rather than glowing."""
    night = _nightf(pal)
    obj = _stepped(_Napper, pal, 24, sx)
    breath = math.sin(t * 1.0)
    # Cool the cached napper sprite toward night so its hardcoded bright skin
    # (235,195,150) doesn't out-shine the dressing once the sky darkens.
    if night > 0.05 and obj._sprite is not None:
        obj._sprite = obj._sprite.copy()
        k = int(255 * (1 - 0.42 * night))
        kb = int(255 * (1 - 0.30 * night))
        obj._sprite.fill((k, k, kb, 255), special_flags=pygame.BLEND_RGBA_MULT)
    obj._blit_sprite(surf, y_off=-max(0, int(round(breath * 1.2))))
    # Two dimmed Z's rising + fading; capped so no pixel exceeds NIGHT_GLOW_CAP.
    zc = _cap150((150, 150, 150))
    for i in range(2):
        cycle = ((t * 0.45) + i * 0.55) % 1.0
        zy = GROUND_Y - 14 - int(cycle * 16)
        zx = int(sx) - 4 + i * 5 + int(math.sin(cycle * math.pi * 2) * 1)
        a = int(170 * (1.0 - cycle))
        if a <= 8:
            continue
        layer = pygame.Surface((6, 6), pygame.SRCALPHA)
        pygame.draw.line(layer, (*zc, a), (0, 0), (3, 0), 1)
        pygame.draw.line(layer, (*zc, a), (3, 0), (0, 3), 1)
        pygame.draw.line(layer, (*zc, a), (0, 3), (3, 3), 1)
        surf.blit(layer, (zx, zy))


# ── bring the literal glow cap home on the cream pillar's BASE trim ───────────
#
# The pillar art (painted into the scene before any phase painter runs) carries
# two warm highlights at its foot that read brighter than the 150 ceiling — a
# small gold base sill (~rgb 255,230,100, luma 223) and a doorway-shrine trim
# band (~rgb 208,187,131, luma 187). The pillar itself is praised and must NOT be
# dulled, so this clamp touches ONLY the two narrow foot bands: any over-cap pixel
# there is pulled DOWN to NIGHT_GLOW_CAP luma while keeping its hue, so the coin
# stays the single brightest object even at the frame edge. The pillar body and
# its lit niches higher up are untouched.

# (x0, x1, y0, y1) — the cream pillar's FOOT, where its gold base sill and the
# golden doorway-shrine trim band carry warm highlights that ran past 150 luma.
# The tower's praised silhouette and lit niches live higher up (y < ~530) and are
# left untouched; only the ground-level foot trim (which sits closest to the coin)
# is clamped, so the coin stays the single brightest object even at the corner.
_TRIM_BANDS = (
    (244, 302, 530, GROUND_Y),
)


def _clamp_pillar_base_trim(surf, pal=None, cap=NIGHT_GLOW_CAP):
    """Pull any pillar-foot trim pixel above `cap` luma down to it, hue-preserved,
    so no static masonry highlight competes with the gold coin. Gated to a dark
    sky — by day the foot is legitimately lit stone and is left alone; the cap is
    a NIGHT contract, so only dusk/night foot trim is brought home."""
    if pal is not None and not sp._is_dark_sky(pal):
        return
    for x0, x1, y0, y1 in _TRIM_BANDS:
        for yy in range(y0, y1):
            for xx in range(x0, x1):
                r, g, b, a = surf.get_at((xx, yy))
                lum = 0.299 * r + 0.587 * g + 0.114 * b
                if lum > cap:
                    k = cap / lum
                    surf.set_at((xx, yy), (int(r * k), int(g * k), int(b * k), a))


# ══════════════════════════════════════════════════════════════════════════
# Phase events — each recombines dressing layers + a living cast. Painters take
# (surf, w, gy, h, scroll, pal, t) so the characters can show a gait frame.
# ══════════════════════════════════════════════════════════════════════════
#
# Anchor strategy: the cream pillar sits at the right (base x≈244); the bird
# flies at x≈90. Static dressing uses r15's lane gates. Characters are placed by
# their own clear-zone anchors in the lower band — most live left of the bird
# lane (far left, x<46) or in the mid promenade gap (x≈150..200), never on the
# bird column or the pillar base.

# Character clear zones in the lower band. The bird-lane character ban is a touch
# narrower than the tall-prop ban (characters are short and sit below the bird),
# but we still keep their CENTRES out of x≈70..110 and the pillar base.
def _char_x_ok(sx, half=14):
    if 70 - half < sx < 116 + half:        # bird column
        return False
    if 222 - half < sx < 312 + half:       # pillar base
        return False
    return True


# Cached borrowed-ambient characters: rebuilt only when the biome bucket changes
# (so they retint), pinned to screen-x, and animated from the live clock. The
# pristine sprite is restored each frame so callers that tint it (draw_napper)
# don't compound the tint. `frames` is vestigial (kept for the call sites).
_CHAR_CACHE: dict = {}
_CUR_BUCKET = 0
_CUR_T = 0.0

def _stepped(cls, pal, frames, x, *, rng_seed=7):
    ent = _CHAR_CACHE.get(cls)
    if ent is None or ent[1] != _CUR_BUCKET:
        obj = cls(pal, random.Random(rng_seed))
        pristine = obj._sprite.copy() if getattr(obj, "_sprite", None) is not None else None
        ent = [obj, _CUR_BUCKET, pristine]
        _CHAR_CACHE[cls] = ent
    obj, _bk, pristine = ent
    if pristine is not None:
        obj._sprite = pristine.copy()
    obj.x = float(x)
    obj.t = float(_CUR_T)
    return obj


def _ground_furniture(surf, w, scroll, pal, density=1.0):
    """World-anchored ground FIXTURES — a barrel, a cairn, a planter trailing a
    cascading vine, and a sparse bamboo planter. These are part of the street,
    not part of the crowd: FIXED spacing (never density-scaled) so they stay
    pinned to the sidewalk and scroll at world speed, present from t=0. (Scaling
    the period by a per-frame density made the anchors slide/flicker.) `density`
    is accepted but ignored. Clears the bird column; drawn behind the cast."""
    for sx, k in sp._world_xs(scroll, w, 260, x0=14):
        if sp._ground_clear(sx, 10):
            sp._draw_barrel(surf, sx, pal)
    for sx, k in sp._world_xs(scroll, w, 260, x0=118):
        if sp._ground_clear(sx, 12):
            sp._draw_cairn(surf, sx, pal, scale=1.2)
    for sx, k in sp._world_xs(scroll, w, 300, x0=205):
        if sp._ground_clear(sx, 12):
            sp._draw_planter(surf, sx, pal, kind='shrub')
            sp._draw_vine_trail(surf, sx + 11, pal)
    # A single segmented-bamboo planter per stretch — wide period + its own
    # offset keeps the cane idiom present without over-packing the deck.
    for sx, k in sp._world_xs(scroll, w, 360, x0=70):
        if sp._ground_clear(sx, 12):
            sp._draw_planter(surf, sx, pal, kind='bamboo')


# ── grouped scenarios ─────────────────────────────────────────────────────────
#
# Coherent little scenes placed at world-x slots: the bird passes one, then open
# road, then the next. Each scene's contents are seeded by its slot index `k`
# (NOT by `scroll`), so a scene is identical frame-to-frame as it scrolls past —
# world-anchored, no flicker (same idiom as the mountain-ornament fix). Members
# animate in place from the live clock `t`; positions ride the scroll.

_SCENARIO_PERIOD = 460          # world-px between scenes -> ~1 on screen + open road
_SCENE_MARGIN = 200             # wide enough to slide a whole scene in/out smoothly

# ── re-themed cast + hero beats (Chinese market) ──────────────────────────────

def draw_wish_tree(surf, sx, pal, *, t=0.0):
    """A potted WISH-TREE hung with red prayer ribbons — the market's answer to the
    old European wishing well. Gnarled trunk + a tiered canopy in a glazed pot, with
    fluttering red wish-cards; a couple catch a capped warm glint once the sky darks."""
    night = _nightf(pal)
    feet = GROUND_Y - 1
    pot = _mix((150, 96, 70), (60, 70, 100), 0.34 * night)
    pygame.draw.rect(surf, _shade(pot, -20), (sx - 8, feet - 8, 16, 8))
    pygame.draw.rect(surf, pot, (sx - 7, feet - 8, 14, 6))
    pygame.draw.rect(surf, _shade(pot, 18), (sx - 7, feet - 8, 14, 1))
    trunk = _mix((96, 66, 42), (60, 66, 92), 0.30 * night)
    ty0 = feet - 8
    pygame.draw.line(surf, trunk, (sx, ty0), (sx - 1, ty0 - 9), 2)
    pygame.draw.line(surf, trunk, (sx - 1, ty0 - 9), (sx + 1, ty0 - 18), 2)
    fol = _mix((72, 122, 72), (44, 60, 92), 0.42 * night)
    fol_d = _shade(fol, -16)
    cy = ty0 - 22
    for ox, oy, r in ((-6, 4, 6), (6, 4, 6), (0, -2, 8), (0, 6, 7)):
        pygame.draw.circle(surf, fol_d, (sx + ox, cy + oy + 1), r)
        pygame.draw.circle(surf, fol, (sx + ox, cy + oy), r)
    pygame.draw.circle(surf, _shade(fol, 14), (sx - 2, cy - 3), 2)
    rib = _mix((210, 60, 56), (70, 64, 96), 0.40 * night)
    rib_l = _shade(rib, 22)
    for i, (rx, ry) in enumerate(((-7, -2), (5, 0), (-2, 8), (8, 6), (-9, 6))):
        flut = int(round(math.sin(t * 2.2 + i * 1.4) * 1.5))
        x = sx + rx
        y0 = cy + ry
        pygame.draw.line(surf, rib, (x, y0), (x + flut, y0 + 6), 2)
        pygame.draw.line(surf, rib_l, (x, y0), (x + flut, y0 + 2), 1)
    if night > 0.5:
        _glow(surf, sx, cy + 2, pal, radius=11, color=(230, 120, 90), scale=0.5)


def draw_birdcage_stand(surf, sx, pal, *, t=0.0):
    """A market SONGBIRD CAGE on a tall stand — the Chinese-market replacement for
    the grazing flock. A domed bamboo cage with a hopping finch sways gently; a seed
    dish sits at the foot."""
    night = _nightf(pal)
    feet = GROUND_Y - 1
    sway = math.sin(t * 1.6) * 1.0
    pole = _mix((110, 78, 46), (60, 66, 92), 0.30 * night)
    pygame.draw.line(surf, pole, (sx, feet), (sx, feet - 20), 2)
    pygame.draw.line(surf, _shade(pole, -18), (sx + 1, feet), (sx + 1, feet - 20), 1)
    pygame.draw.rect(surf, _shade(pole, -10), (sx - 4, feet - 2, 8, 2))
    cgx = sx + int(round(sway))
    cgy = feet - 32
    bar = _mix((188, 168, 116), (60, 70, 100), 0.42 * night)
    bar_d = _shade(bar, -26)
    pygame.draw.line(surf, pole, (sx, feet - 20), (cgx, cgy + 3), 1)
    pygame.draw.arc(surf, bar, (cgx - 7, cgy, 14, 9), 0.0, math.pi, 2)
    body = pygame.Rect(cgx - 7, cgy + 4, 14, 13)
    pygame.draw.rect(surf, _mix((205, 188, 150), (58, 66, 96), 0.45 * night), body)
    pygame.draw.rect(surf, bar_d, body, 1)
    for bxv in range(cgx - 5, cgx + 6, 3):
        pygame.draw.line(surf, bar_d, (bxv, cgy + 4), (bxv, cgy + 16), 1)
    pygame.draw.line(surf, bar_d, (cgx - 7, cgy + 10), (cgx + 6, cgy + 10), 1)
    hop = int(round(max(0.0, math.sin(t * 5.0)) * 2))
    bird = _retint_person((240, 180, 70), night)
    by = cgy + 14 - hop
    pygame.draw.circle(surf, bird, (cgx, by), 2)
    pygame.draw.circle(surf, _shade(bird, -20), (cgx + 1, by + 1), 1)
    pygame.draw.circle(surf, (40, 30, 20), (cgx + 1, by - 1), 0)
    pygame.draw.ellipse(surf, _mix((150, 140, 120), (60, 70, 100), 0.40 * night),
                        (sx - 5, feet - 3, 10, 3))


def draw_lamplighter(surf, sx, pal, *, t=0.0):
    """A LAMPLIGHTER reaching a long pole up to a street lantern, kindling it at
    dusk — the 'lights coming on' beat. The pole tip carries a capped flame; the
    lantern above blooms a capped warm glow once touched."""
    night = _nightf(pal)
    feet = GROUND_Y - 1
    coat = _retint_person((124, 92, 152), night)
    coat_d = _shade(coat, -18)
    hair = _retint_person((60, 45, 35), night)
    body_y = feet - 11
    _draw_bench_person(surf, sx, body_y, coat, coat_d, hair, night=night)
    leg = _shade(coat_d, -14)
    pygame.draw.line(surf, leg, (sx + 1, body_y + 8), (sx, feet), 1)
    pygame.draw.line(surf, leg, (sx + 4, body_y + 8), (sx + 6, feet), 1)
    px0, py0 = sx + 5, body_y + 1
    px1, py1 = sx + 16, body_y - 16
    pygame.draw.line(surf, _mix((110, 80, 50), (60, 66, 92), 0.30 * night),
                     (px0, py0), (px1, py1), 1)
    flick = int(round(math.sin(t * 8.0)))
    pygame.draw.circle(surf, sp._clamp_night((250, 170, 90))[:3], (px1, py1 - 1 + flick), 1)
    lan = pygame.Rect(px1 - 3, py1 - 9, 7, 8)
    pygame.draw.ellipse(surf, _mix((150, 40, 40), (150, 38, 38), 0.5), lan)
    lit = (sp._clamp_night((250, 120, 90))[:3] if sp._is_dark_sky(pal) else (220, 120, 90))
    pygame.draw.ellipse(surf, lit, lan.inflate(-2, -2))
    _glow(surf, px1, py1 - 5, pal, radius=10, color=(255, 160, 110), scale=0.6)


def draw_market_setup(surf, sx, pal, *, t=0.0):
    """DAWN MARKET SET-UP — stacked produce crates and a vendor hoisting a basket
    overhead as the stalls are raised. The 'morning assembly' beat that opens the day."""
    night = _nightf(pal)
    feet = GROUND_Y - 1
    crate = _mix((150, 110, 66), (60, 70, 100), 0.34 * night)
    for cx, cy, w, h in ((-2, 0, 12, 8), (11, 0, 9, 6), (4, 8, 10, 7)):
        r = pygame.Rect(sx + cx, feet - cy - h, w, h)
        pygame.draw.rect(surf, _shade(crate, -16), r)
        pygame.draw.rect(surf, crate, r.inflate(-2, -2))
        pygame.draw.line(surf, _shade(crate, -24),
                         (r.left, r.centery), (r.right, r.centery), 1)
    shirt = _retint_person((90, 140, 120), night)
    shirt_d = _shade(shirt, -16)
    hair = _retint_person((50, 40, 30), night)
    vx = sx + 24
    body_y = feet - 11
    _draw_bench_person(surf, vx, body_y, shirt, shirt_d, hair, night=night)
    lift = int(round(max(0.0, math.sin(t * 2.0)) * 1))
    bk = _mix((160, 120, 70), (60, 70, 100), 0.34 * night)
    by = body_y - 6 - lift
    pygame.draw.ellipse(surf, _shade(bk, -14), (vx, by, 10, 5))
    pygame.draw.ellipse(surf, bk, (vx + 1, by, 8, 4))
    pygame.draw.line(surf, shirt_d, (vx + 2, body_y + 1), (vx + 1, by + 3), 1)
    pygame.draw.line(surf, shirt_d, (vx + 5, body_y + 1), (vx + 8, by + 3), 1)
    leg = _shade(shirt_d, -12)
    pygame.draw.line(surf, leg, (vx + 1, body_y + 8), (vx + 1, feet), 1)
    pygame.draw.line(surf, leg, (vx + 4, body_y + 8), (vx + 5, feet), 1)


def _scene_market(surf, bx, pal, t, rng):
    """Food/market stall with a songbird-cage stand and kids beside it."""
    draw_kiosk(surf, bx, pal, t=t, openness=0.9)
    draw_birdcage_stand(surf, bx + 84, pal, t=t)
    draw_kids(surf, bx + 152, pal, t=t, n=2)

def _draw_calm_dog(surf, sx, pal, *, t=0.0):
    """The promenade dog at a SLOW amble, flipped to face LEFT — the scroll/travel
    direction — so it reads as walking forward, not moonwalking backward. Reuses
    the live _RunningDog frames; the shared class is left untouched."""
    dog = _stepped(_RunningDog, pal, 30, sx)
    frame = dog._frames[int(t * 2) % 2]                  # slow 2-frame shuffle
    frame = pygame.transform.flip(frame, True, False)    # face the travel direction
    sw, sh = frame.get_size()
    surf.blit(frame, (sx - sw // 2, GROUND_Y - sh + 1))

def _scene_pastoral(surf, bx, pal, t, rng):
    """Wish-tree + a slow dog ambling with the street + a planter."""
    draw_wish_tree(surf, bx, pal, t=t)
    _draw_calm_dog(surf, bx + 66, pal, t=t)
    sp._draw_planter(surf, bx + 122, pal, kind='shrub')

def _scene_lamplighter(surf, bx, pal, t, rng):
    """A lamplighter kindling the street lanterns at dusk + a potted conifer."""
    draw_lamplighter(surf, bx, pal, t=t)
    sp._draw_planter(surf, bx + 40, pal, kind='conifer')

def _scene_dawn_setup(surf, bx, pal, t, rng):
    """Vendors assembling the morning market."""
    draw_market_setup(surf, bx, pal, t=t)


def _scene_bench(surf, bx, pal, t, rng):
    """The temple elder beside a bench with a seated companion."""
    bench = _stepped(_Bench, pal, 20, bx)
    bench._blit_sprite(surf)
    seat_y = (GROUND_Y - 27) + 19            # match _Bench.draw seat geometry
    night = _nightf(pal)
    comp = tuple(_retint_person(c, night) for c in
                 ((215, 85, 100), (175, 50, 70), (80, 50, 30)))
    _draw_bench_person(surf, bx + 8, seat_y - 8, *comp, night=night)
    draw_old_man(surf, bx + 44, pal, t=t, seated_bench=False)

def _scene_stroll(surf, bx, pal, t, rng):
    """A strolling couple + the elder on a slow walk."""
    draw_strollers(surf, bx, pal, t=t)
    draw_old_man(surf, bx + 48, pal, t=t, seated_bench=False)

def _scene_rest(surf, bx, pal, t, rng):
    """A napper on a mat beside a planter."""
    draw_napper(surf, bx, pal, t=t)
    sp._draw_planter(surf, bx + 46, pal, kind='conifer')

def _scene_campfire(surf, bx, pal, t, rng):
    """A campfire with cozy strollers + kids gathered (lit by the drawer at night)."""
    draw_campfire(surf, bx, pal, t=t)
    draw_strollers(surf, bx + 56, pal, t=t)
    draw_kids(surf, bx + 100, pal, t=t, n=2)

def _scenarios(surf, w, scroll, pal, t, roster, x0=40):
    """Place the beat's scene roster at world-x slots, scrolling at world speed."""
    for bx, k in sp._world_xs(scroll, w, _SCENARIO_PERIOD, x0,
                              mult=sp.GROUND_MULT, margin=_SCENE_MARGIN):
        rng = random.Random((k * 0x9E3779B1) & 0xFFFFFFFF)
        roster[k % len(roster)](surf, bx, pal, t, rng)


def phase_day(surf, w, gy, h, scroll, pal, t):
    """DAY · Pastoral Morning. Prayer-flag bunting overhead; pastoral/market
    scenes scroll past. Bright, calm, unlit."""
    global _CUR_PAL
    _CUR_PAL = pal
    _ground_furniture(surf, w, scroll, pal)
    for xl, xr in sp._garland_spans(scroll, w, period=150, x0=20):
        draw_prayer_flags(surf, int(xl), GROUND_Y - 118, int(xr), GROUND_Y - 116, n=5)
    _scenarios(surf, w, scroll, pal, t, (_scene_market, _scene_pastoral), x0=40)


def phase_golden(surf, w, gy, h, scroll, pal, t):
    """GOLDEN HOUR · lamp posts up + a lantern garland; bench/market scenes."""
    global _CUR_PAL
    _CUR_PAL = pal
    _ground_furniture(surf, w, scroll, pal)
    sp._draw_lantern_garland(surf, w, scroll, pal, top_y=GROUND_Y - 96,
                             period=150, sag=22, per_span=2)
    for sx, k in sp._world_xs(scroll, w, 250, x0=20):
        sp._draw_lamp_post(surf, sx, pal, style='ornate', height=96, lantern='red')
    for sx, k in sp._world_xs(scroll, w, 250, x0=160):
        sp._draw_lamp_post(surf, sx, pal, style='ornate', height=90, lantern='gold')
    _scenarios(surf, w, scroll, pal, t, (_scene_bench, _scene_market), x0=70)


def phase_dusk(surf, w, gy, h, scroll, pal, t):
    """DUSK · lamps + fairy lights lighting (gated to the dark sky); rest/stroll
    scenes. Lavender, quieter."""
    global _CUR_PAL
    _CUR_PAL = pal
    _ground_furniture(surf, w, scroll, pal)
    sp._draw_fairy_lights(surf, w, scroll, pal, top_y=GROUND_Y - 92,
                          period=210, sag=26, per_span=5)
    for sx, k in sp._world_xs(scroll, w, 250, x0=24):
        sp._draw_lamp_post(surf, sx, pal, style='ornate', height=94, lantern='red')
    for sx, k in sp._world_xs(scroll, w, 250, x0=158):
        sp._draw_lamp_post(surf, sx, pal, style='ornate', height=88, lantern='glass')
    _scenarios(surf, w, scroll, pal, t, (_scene_rest, _scene_stroll), x0=55)


def phase_night(surf, w, gy, h, scroll, pal, t):
    """NIGHT · Festival. Lantern garland + fairy lights + lamp posts all glowing
    (capped); campfire/market scenes. The payoff."""
    global _CUR_PAL
    _CUR_PAL = pal
    _ground_furniture(surf, w, scroll, pal)
    sp._draw_lantern_garland(surf, w, scroll, pal, top_y=GROUND_Y - 98,
                             period=118, sag=24, per_span=3)
    sp._draw_fairy_lights(surf, w, scroll, pal, top_y=GROUND_Y - 78,
                          period=200, sag=22, per_span=5)
    for sx, k in sp._world_xs(scroll, w, 250, x0=18):
        sp._draw_lamp_post(surf, sx, pal, style='ornate', height=96, lantern='red')
    for sx, k in sp._world_xs(scroll, w, 250, x0=152):
        sp._draw_lamp_post(surf, sx, pal, style='ornate', height=90, lantern='gold')
    _scenarios(surf, w, scroll, pal, t, (_scene_campfire, _scene_market), x0=30)


# (label, painter)
PHASES_R17 = [
    ("DAY · Pastoral Morning", phase_day),
    ("GOLDEN HOUR · Afternoon Promenade", phase_golden),
    ("DUSK · Lamps Lighting", phase_dusk),
    ("NIGHT · Festival", phase_night),
]


# ── live composition: the day-arc DIRECTOR ────────────────────────────────────
#
# Replaces the old 4 interchangeable crossfade beats (which read as an artificial,
# evenly-packed loop) with ONE continuous story of a market street's day: it
# ASSEMBLES at run-start, builds through the day, PEAKS as a night festival, then
# tears down to a near-empty pre-dawn before the next day. Two signals drive it,
# both already in hand: `phase` (the biome day-cycle position) picks the dressing +
# cast vocabulary and the crowd density; `t` (= world.biome_time, 0 at run-start,
# monotonic) ramps the street from empty as the run opens. Dressing is drawn in a
# SINGLE pass (no per-frame double-beat layer) — also cheaper than the old crossfade.

# Crowd-density curve over the day (piecewise-linear keypoints, phase -> 0..1):
# near-empty at dawn/pre-dawn, a daytime bustle, a dip at the golden lull, rising
# through dusk to the NIGHT PEAK, then a fast teardown to the empty pre-dawn.
_POP_KEYS = [
    (0.00, 0.45), (0.18, 0.72), (0.30, 0.58), (0.45, 0.72), (0.60, 0.90),
    (0.70, 1.00), (0.80, 0.92), (0.88, 0.16), (0.93, 0.10), (1.00, 0.45),
]

def _population(phase):
    p = phase % 1.0
    for i in range(len(_POP_KEYS) - 1):
        a, va = _POP_KEYS[i]
        b, vb = _POP_KEYS[i + 1]
        if a <= p <= b:
            f = (p - a) / (b - a) if b > a else 0.0
            return va + (vb - va) * f
    return _POP_KEYS[-1][1]

_FILL_SECONDS = 7.0   # the market "opens" over the first few seconds of a run

def _run_fill(t):
    x = max(0.0, min(1.0, t / _FILL_SECONDS))
    return x * x * (3.0 - 2.0 * x)   # smoothstep: street starts empty, fills in

def _slot_on(k, salt, density):
    """Stable per-slot inclusion gate: hash (slot index, salt) to [0,1) and admit
    the slot iff that fixed threshold is below `density`. Because the threshold is
    keyed to the WORLD slot (not the frame), a slot pops in exactly once as the
    density curve rises and never flickers — and its x never moves."""
    h = ((k * 0x9E3779B1) ^ (salt * 0x85EBCA77)) & 0xFFFF
    return (h / 65535.0) < density

def _roster_for(phase):
    """The cast vocabulary appropriate to the time of day."""
    p = phase % 1.0
    if p >= 0.85 or p < 0.25:          # DAY — morning market
        return (_scene_market, _scene_pastoral)
    if p < 0.40:                       # GOLDEN — afternoon promenade
        return (_scene_bench, _scene_market)
    if p < 0.58:                       # DUSK — quieter, settling in
        return (_scene_rest, _scene_stroll, _scene_bench)
    if p < 0.80:                       # NIGHT — festival
        return (_scene_campfire, _scene_market, _scene_stroll)
    return (_scene_rest,)              # PRE-DAWN — near-empty teardown

def _dressing(surf, w, scroll, pal, phase):
    """Phase-gated street fixtures in one pass (glow follows the palette). Lamps +
    lanterns are installed for the evening and stay as fixtures; the prayer-flag
    bunting is the daytime look."""
    p = phase % 1.0
    if p >= 0.85 or p < 0.28:                                   # daytime bunting
        for xl, xr in sp._garland_spans(scroll, w, period=150, x0=20):
            draw_prayer_flags(surf, int(xl), GROUND_Y - 118,
                              int(xr), GROUND_Y - 116, n=5)
    if 0.20 <= p < 0.92:                                        # lantern garland
        sp._draw_lantern_garland(surf, w, scroll, pal, top_y=GROUND_Y - 97,
                                 period=128, sag=23, per_span=3)
    if 0.20 <= p < 0.93:                                        # lamp posts
        for sx, k in sp._world_xs(scroll, w, 250, x0=18):
            sp._draw_lamp_post(surf, sx, pal, style='ornate', height=96, lantern='red')
        for sx, k in sp._world_xs(scroll, w, 250, x0=152):
            sp._draw_lamp_post(surf, sx, pal, style='ornate', height=90, lantern='gold')
    if 0.40 <= p < 0.86:                                        # festival fairy lights
        sp._draw_fairy_lights(surf, w, scroll, pal, top_y=GROUND_Y - 84,
                              period=205, sag=24, per_span=5)

def _place_scenarios(surf, w, scroll, pal, t, roster, density, x0=40):
    """Place the time-appropriate cast at FIXED world-x slots, THINNED by `density`:
    each slot is admitted only with probability `density` (seeded by slot index so
    it's stable as it scrolls). The spacing is constant — only the per-slot gate
    changes with density — so a figure pops in once instead of sliding when the
    crowd fills in. Off-peak the street is mostly open paving; at night it fills."""
    if density <= 0.03 or not roster:
        return
    for bx, k in sp._world_xs(scroll, w, _SCENARIO_PERIOD, x0,
                              mult=sp.GROUND_MULT, margin=_SCENE_MARGIN):
        r = random.Random((k * 0x9E3779B1) & 0xFFFFFFFF)
        if r.random() > density:        # stable per-slot inclusion -> negative space
            continue
        roster[r.randrange(len(roster))](surf, bx, pal, t, r)

def draw_promenade(surf, scroll, pal, phase, t):
    """Draw the promenade as a living day-arc: fixtures by phase, cast thinned by a
    crowd-density curve, and the whole street filling in from empty at run-start."""
    global _CUR_BUCKET, _CUR_T, _CUR_PAL
    _CUR_BUCKET = _biome.phase_bucket(phase)
    _CUR_T = t
    _CUR_PAL = pal
    density = _population(phase) * _run_fill(t)
    _ground_furniture(surf, W, scroll, pal, density=density)
    _dressing(surf, W, scroll, pal, phase)
    _place_scenarios(surf, W, scroll, pal, t, _roster_for(phase), density)
