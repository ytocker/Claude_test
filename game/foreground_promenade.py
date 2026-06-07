"""Round-17 LIVING PROMENADE — a day->night ESCALATION of one promenade.

Rounds 14-16 presented the sidewalk dressing as five separate STYLES. The
corrected intent: those are really the SAME promenade with layers stacked on.
So round 17 turns the layers into a gradual time-of-day escalation — each phase
is its own EVENT, sparse by day -> a full festival by night — and POPULATES the
walk with LIVING characters (sheep, dog, kids, an old man, a vendor) so the
world feels inhabited rather than decorated.

Four phase events, escalating:

  DAY    Pastoral morning — planters + prayer-flag bunting + a kiosk just
         opening; sheep flock grazing, a running dog, kids, a wishing well.
         Few/no lights.
  GOLDEN Afternoon promenade — lamp posts up, a lantern garland being strung,
         a busy kiosk; the old man on a bench with a companion, kids, the dog.
         Warm amber, still unlit.
  DUSK   Lamps lighting — lamps + fairy lights JUST beginning to glow, the
         kiosk lantern lit, planters; a couple of strolling figures, a napper.
  NIGHT  Festival — lantern garland + fairy lights + lamp posts all glowing
         (capped), a campfire, the kiosk glowing; a few cozy figures.

Dressing primitives are recombined from sidewalk_props_r15 (lamp posts, lantern
garland, fairy lights, planters); prayer-flag bunting comes from
game.pillar_variants. The KIDS, OLD MAN and KIOSK are net-new here.

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
        # Each kid runs on its own phase so the group reads as alive.
        gait = math.sin(t * 6.0 + i * 1.7)
        lift = -max(0.0, gait) * 1.5  # only the up-swing lifts
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
        # Two stubby running legs, swinging opposite phase.
        leg = _shade(shirt_dk, -18)
        swing = int(round(gait * 2))
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
        gait = math.sin(t * 2.2 + i * 1.1)
        feet_y = GROUND_Y - 1 - int(round(max(0.0, gait) * 0.8))
        body_y = feet_y - 8 - 3
        _draw_bench_person(surf, sx + dx, body_y, shirt, shirt_dk, hair, night=night)
        # Walking legs under the body block.
        leg = _shade(shirt_dk, -16)
        sw = int(round(gait * 2))
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


def _ground_furniture(surf, w, scroll, pal):
    """World-anchored ground props re-added from the source set: a barrel, a
    cairn, and a planter trailing a cascading vine. Low density and clears the
    bird column (sp._ground_clear) so they dress the deck without crowding; drawn
    early in each beat so they sit behind the living cast."""
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


def phase_day(surf, w, gy, h, scroll, pal, t):
    """DAY · Pastoral Morning. Sparse dressing: planters + prayer-flag bunting +
    a kiosk just opening. Living: a grazing sheep flock, a running dog, kids, a
    wishing well. Bright, calm, essentially unlit. The cast is SPREAD across the
    open left-centre deck (x≈90..200) with a clear gap before the pillar base, so
    DAY reads genuinely sparse rather than one brown/white blob at the pillar."""
    global _CUR_PAL
    _CUR_PAL = pal
    _ground_furniture(surf, w, scroll, pal)
    # ONE clean prayer-flag span per period strung high across the promenade.
    for xl, xr in sp._garland_spans(scroll, w, period=150, x0=20):
        draw_prayer_flags(surf, int(xl), GROUND_Y - 118, int(xr), GROUND_Y - 116, n=5)
    # One planter only, anchored to land in the open gap between the dog and the
    # kids (not in the flock), so DAY stays genuinely sparse and uncluttered.
    for sx, k in sp._world_xs(scroll, w, 250, x0=180):
        if sp._ground_clear(sx, 12) and not (84 < sx < 154):
            sp._draw_planter(surf, sx, pal, kind='shrub')
    # Kiosk just opening (low openness) at the far-left clear strip.
    draw_kiosk(surf, 38, pal, t=t, openness=0.2)
    # Living cast, drawn after dressing so they read in front. Staggered across
    # the open deck at distinct x AND depth so silhouettes separate; the flock is
    # pulled left to ~120 (covers ~90..150) and the kids sit at ~196 in a clear
    # gap well before the pillar base at x≈222 — no blob, no crowding the lane.
    well = _stepped(_WishingWell, pal, 20, 58)   # far left, off the open deck
    well.draw(surf)
    draw_flock(surf, 118, pal, t=t, n=3)         # woolly grazing flock, left-centre
    dog = _stepped(_RunningDog, pal, 30, 168)    # dog trotting between flock+kids
    dog.draw(surf)
    draw_kids(surf, 198, pal, t=t, n=2)          # 2 kids playing in the right gap


def phase_golden(surf, w, gy, h, scroll, pal, t):
    """GOLDEN HOUR · Afternoon Promenade. Mid dressing: lamp posts up, a lantern
    garland being strung, a busy kiosk. Living: the old man on a bench with a
    companion, kids, the dog. Warm amber, still unlit."""
    global _CUR_PAL
    _CUR_PAL = pal
    _ground_furniture(surf, w, scroll, pal)
    sp._draw_lantern_garland(surf, w, scroll, pal, top_y=GROUND_Y - 96,
                             period=150, sag=22, per_span=2)
    for sx, k in sp._world_xs(scroll, w, 250, x0=20):
        if sp._post_ok(sx):
            sp._draw_lamp_post(surf, sx, pal, style='ornate', height=96, lantern='red')
    for sx, k in sp._world_xs(scroll, w, 250, x0=160):
        if sp._post_ok(sx):
            sp._draw_lamp_post(surf, sx, pal, style='ornate', height=90, lantern='gold')
    for sx, k in sp._world_xs(scroll, w, 250, x0=185):
        if sp._ground_clear(sx, 12) and not (104 < sx < 132):
            sp._draw_planter(surf, sx, pal, kind='shrub')
    draw_kiosk(surf, 38, pal, t=t, openness=1.0)   # busy, fully open
    # The TEMPLE ELDER is the hero of the golden-hour bench: a clearly stooped,
    # caned, long-bearded figure standing AT the bench in the open mid strip,
    # placed where the bird/coin can't hide him and given the full standing
    # silhouette (stoop + cane to the deck + beard) so he reads at 1×. A
    # bright-shirted companion sits on the bench beside him.
    bench = _stepped(_Bench, pal, 20, 160)
    bench._blit_sprite(surf)
    # Match _Bench.draw: sprite is 42x28, top at GROUND_Y-27, seat at +19.
    seat_y = (GROUND_Y - 27) + 19
    night = _nightf(pal)
    comp = tuple(_retint_person(c, night) for c in
                 ((215, 85, 100), (175, 50, 70), (80, 50, 30)))
    _draw_bench_person(surf, 168, seat_y - 8, *comp, night=night)
    # The standing elder just left of the bench, in the clear gap before it — his
    # cane and stoop read against the open deck, distinct from the round-cap kids.
    draw_old_man(surf, 140, pal, t=t, seated_bench=False)
    dog = _stepped(_RunningDog, pal, 30, 118)
    dog.draw(surf)
    draw_kids(surf, 200, pal, t=t, n=2)


def phase_dusk(surf, w, gy, h, scroll, pal, t):
    """DUSK · Lamps Lighting. Lamps + fairy lights JUST beginning to glow (gated
    to the now-dark sky), the kiosk lantern lit, planters. Living: a couple of
    strolling figures + a napper resting. Lavender, quieter."""
    global _CUR_PAL
    _CUR_PAL = pal
    _ground_furniture(surf, w, scroll, pal)
    sp._draw_fairy_lights(surf, w, scroll, pal, top_y=GROUND_Y - 92,
                          period=210, sag=26, per_span=5)
    for sx, k in sp._world_xs(scroll, w, 250, x0=24):
        if sp._post_ok(sx):
            sp._draw_lamp_post(surf, sx, pal, style='ornate', height=94, lantern='red')
    for sx, k in sp._world_xs(scroll, w, 250, x0=158):
        if sp._post_ok(sx):
            sp._draw_lamp_post(surf, sx, pal, style='ornate', height=88, lantern='glass')
    for sx, k in sp._world_xs(scroll, w, 250, x0=128):
        if sp._ground_clear(sx, 12):
            sp._draw_planter(surf, sx, pal, kind='conifer')
    draw_kiosk(surf, 38, pal, t=t, openness=0.8)
    # The napper rests at far left; the temple elder takes a slow cane-walk in the
    # mid gap (carrying his read into dusk too, per the AD note); a couple stroll
    # just beyond. Capped Z's.
    draw_napper(surf, 86, pal, t=t)
    draw_old_man(surf, 138, pal, t=t, seated_bench=False)
    draw_strollers(surf, 192, pal, t=t)


def phase_night(surf, w, gy, h, scroll, pal, t):
    """NIGHT · Festival. Full festival: lantern garland + fairy lights + lamp
    posts all glowing (capped), a campfire, the kiosk glowing. Living: a few
    cozy figures. The payoff cell."""
    global _CUR_PAL
    _CUR_PAL = pal
    _ground_furniture(surf, w, scroll, pal)
    sp._draw_lantern_garland(surf, w, scroll, pal, top_y=GROUND_Y - 98,
                             period=118, sag=24, per_span=3)
    sp._draw_fairy_lights(surf, w, scroll, pal, top_y=GROUND_Y - 78,
                          period=200, sag=22, per_span=5)
    for sx, k in sp._world_xs(scroll, w, 250, x0=18):
        if sp._post_ok(sx):
            sp._draw_lamp_post(surf, sx, pal, style='ornate', height=96, lantern='red')
    for sx, k in sp._world_xs(scroll, w, 250, x0=152):
        if sp._post_ok(sx):
            sp._draw_lamp_post(surf, sx, pal, style='ornate', height=90, lantern='gold')
    for sx, k in sp._world_xs(scroll, w, 250, x0=192):
        if sp._ground_clear(sx, 12) and not (104 < sx < 138):
            sp._draw_planter(surf, sx, pal, kind='conifer')
    draw_kiosk(surf, 38, pal, t=t, openness=1.0)
    # A campfire warms the mid strip — amber-cored + capped sparks (no white-hot
    # centre), additive halo scaled by the dusk->night intensity.
    draw_campfire(surf, 120, pal, t=t)
    # A couple of cozy figures strolling home near the fire.
    draw_strollers(surf, 170, pal, t=t)


# (label, painter)
PHASES_R17 = [
    ("DAY · Pastoral Morning", phase_day),
    ("GOLDEN HOUR · Afternoon Promenade", phase_golden),
    ("DUSK · Lamps Lighting", phase_dusk),
    ("NIGHT · Festival", phase_night),
]


# ── live composition: phase-window selector with crossfade ────────────────────
#
# The 4 beats were authored as discrete cells. Live, `phase` is continuous, so we
# map each beat to a contiguous arc aligned with the biome sky and crossfade in a
# small band at each boundary so dressing fades in/out rather than popping.

_BEAT_FNS = {"day": phase_day, "golden": phase_golden,
             "dusk": phase_dusk, "night": phase_night}
# (boundary_phase, beat_before, beat_after) — arcs: day[0.85..0.25) golden[0.25..0.43)
# dusk[0.43..0.60) night[0.60..0.85).
_BOUNDS = [(0.25, "day", "golden"), (0.43, "golden", "dusk"),
           (0.60, "dusk", "night"), (0.85, "night", "day")]
_XF_HALF = 0.025

def _beat_mix(phase):
    p = phase % 1.0
    for bp, before, after in _BOUNDS:
        signed = ((p - bp + 0.5) % 1.0) - 0.5    # circular signed distance to bp
        if abs(signed) < _XF_HALF:
            frac = max(0.0, min(1.0, 0.5 + signed / (2 * _XF_HALF)))
            return [(before, 1.0 - frac), (after, frac)]
    if p < 0.25 or p >= 0.85:
        return [("day", 1.0)]
    if p < 0.43:
        return [("golden", 1.0)]
    if p < 0.60:
        return [("dusk", 1.0)]
    return [("night", 1.0)]

def draw_promenade(surf, scroll, pal, phase, t):
    """Draw the promenade dressing + living cast for the live biome `phase`,
    crossfading between adjacent beats near phase boundaries."""
    global _CUR_BUCKET, _CUR_T
    _CUR_BUCKET = _biome.phase_bucket(phase)
    _CUR_T = t
    for name, wgt in _beat_mix(phase):
        fn = _BEAT_FNS[name]
        if wgt >= 0.999:
            fn(surf, W, GROUND_Y, H, scroll, pal, t)
        else:
            layer = pygame.Surface((W, H), pygame.SRCALPHA)
            fn(layer, W, GROUND_Y, H, scroll, pal, t)
            layer.fill((255, 255, 255, int(wgt * 255)),
                       special_flags=pygame.BLEND_RGBA_MULT)
            surf.blit(layer, (0, 0))
