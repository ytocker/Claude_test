"""THUNDERBIRD candidate — Design 6: PLASMA SURGE (scratch exploration).

A plasma-globe bird. There is no solid feathered body: the whole creature IS
electricity. A white-hot nucleus glows electric-yellow, and every "feather" is a
forked lightning bolt radiating outward like the arcs inside a plasma globe
reaching for the glass. Electric yellow is the PRIMARY color, not an accent.

Scratch-only: this mirrors the animal-skin contract so it can be previewed by
tools/ninja_render.py, but it is NEVER registered in any BUILDERS map and never
touches production art.

North star: "a skin lives or dies at 40px in motion." The read here is a spiky
radiating fan — the bolt tips reach far enough (x±26, y±20 from body centre)
that the silhouette is unmistakably a crackling star of electricity, not a blob.
The nucleus is always the single brightest point so depth reads inward.
"""
import math
import random

import pygame

from game.parrot import _WING_ANGLES, _add_outline, _aaellipse


# ── canvas constants (mirror the thunderbird tall-canvas layout) ─────────────
COMPOSITE_W, COMPOSITE_H = 64, 84
BCX, BCY = 32, 44               # body centre
HCX, HCY = 44, 34               # head centre
CROWN_Y  = 24                   # top of head


# ── palette ──────────────────────────────────────────────────────────────────
CORE_WHITE = (255, 255, 255)    # nucleus
ELEC_YEL   = (255, 232, 26)     # electric yellow — PRIMARY
VOLT_GOLD  = (255, 179, 0)      # voltage gold
ARC_AMBER  = (255, 122, 0)      # arc amber rim
ION_VIOLET = (179, 107, 255)    # ion-violet — branch tips only, sparingly


def _flap(angle_deg):
    """0..1 'wing is up' factor. _WING_ANGLES runs 50→-40 (down→up)."""
    return (angle_deg + 40) / 90.0


def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _make_prebuilt_skin(build_fn):
    """Cached `(frame_idx, tilt_deg) -> Surface` getter for build_fn(angle).
    Lazy 4-frame build + per-(frame, 3°) rotation cache, each frame outlined
    with the house silhouette outline. Copied (not imported) to keep this
    scratch file standalone, mirroring animal_thunderbird._make_prebuilt_skin."""
    state = {"frames": None, "rot": {}}

    def getter(frame_idx, tilt_deg):
        if state["frames"] is None:
            state["frames"] = [_add_outline(build_fn(a)) for a in _WING_ANGLES]
        frames = state["frames"]
        frame_idx %= len(frames)
        key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
        s = state["rot"].get(key)
        if s is None:
            s = pygame.transform.rotozoom(frames[frame_idx], key[1], 1.0)
            state["rot"][key] = s
        return s

    return getter


def _radial_glow(surf, center, r, color, peak=60):
    """Soft additive halo blitted UNDER the body — the plasma-globe aura. Kept
    additive so it reads as light, not paint, over any sky."""
    cx, cy = center
    g = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
    gc = (r + 2, r + 2)
    layers = 6
    for i in range(layers, 0, -1):
        rr = int(r * i / layers)
        a = int(peak * (1 - (i - 1) / layers))
        pygame.draw.circle(g, (*color, a), gc, rr)
    surf.blit(g, (cx - r - 2, cy - r - 2), special_flags=pygame.BLEND_RGBA_ADD)


def _bolt(surf, pts, color, w=2, *, halo_a=42):
    """A forked lightning stroke: one restrained soft halo pass then a crisp
    core line. The halo alpha is kept low so bolts read as distinct forks, not
    a fuzzy cloud — the crisp yellow core is what carries the spiky silhouette."""
    if len(pts) < 2:
        return
    if halo_a:
        halo = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
        pygame.draw.lines(halo, (*color, halo_a), False, pts, w + 3)
        surf.blit(halo, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    pygame.draw.lines(surf, color, False, pts, w)


def _spark(surf, x, y, r, color, bloom=110):
    """A bright point-discharge with a tight additive bloom — a stray plasma
    spark. Bloom is kept small so many sparks don't merge into a cloud-puff."""
    b = r + 2
    g = pygame.Surface((b * 2, b * 2), pygame.SRCALPHA)
    pygame.draw.circle(g, (*color, bloom), (b, b), b)
    pygame.draw.circle(g, (*CORE_WHITE, 220), (b, b), max(1, r))
    surf.blit(g, (int(x - b), int(y - b)), special_flags=pygame.BLEND_RGBA_ADD)


def _forked_bolt(surf, x0, y0, angle_deg, length, color, tip_color, w0=3):
    """Grow one forked plasma tentacle from (x0,y0) heading at angle_deg. The
    trunk zig-zags outward in 3 segments (thick→thin), throwing ONE short branch
    near the tip. The trunk is drawn crisp electric-yellow so the fan reads as
    distinct spikes; only the very tip gets a small violet-tinted glow dot so
    the star ends in bright points without a violet halo swamping the yellow."""
    a = math.radians(angle_deg)
    ca, sa = math.cos(a), math.sin(a)
    # Perpendicular jitter axis for the zig-zag crackle.
    pa = a + math.pi / 2
    cpa, spa = math.cos(pa), math.sin(pa)

    def at(t, off):
        return (x0 + ca * length * t + cpa * off,
                y0 + sa * length * t + spa * off)

    j = length * 0.14
    p0 = (x0, y0)
    p1 = at(0.36, +j)
    p2 = at(0.68, -j * 0.8)
    p3 = at(1.0, +j * 0.35)              # trunk tip — reaches full length

    # Trunk: crisp yellow core with a hot-white inner near the root for depth.
    _bolt(surf, [p0, p1, p2, p3], color, w=w0)
    pygame.draw.lines(surf, CORE_WHITE, False, [p0, p1], max(1, w0 - 1))

    # One short branch peeling off mid-trunk — thin, no halo, ends near the tip.
    bt = at(0.92, -j * 1.7)
    _bolt(surf, [p2, bt], VOLT_GOLD, w=max(1, w0 - 2), halo_a=0)

    # Bright terminals — the spiky star points (violet only as a tiny tip dot).
    _spark(surf, p3[0], p3[1], 1, tip_color, bloom=80)
    _spark(surf, bt[0], bt[1], 1, VOLT_GOLD, bloom=70)
    return p3


def _build_frame(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)             # 0 = down-stroke, 1 = up-stroke
    random.seed(wing_angle_deg)           # deterministic-per-frame sparks

    # Plasma aura under everything — pulses a touch brighter on the down-stroke
    # when the fan fans widest.
    _radial_glow(surf, (BCX, BCY), 28, ELEC_YEL, peak=int(66 - 14 * f))
    _radial_glow(surf, (BCX, BCY), 16, CORE_WHITE, peak=40)

    ox, oy = BCX - 2, BCY - 4              # bolt origin near core

    # WING BOLTS — the radiating "feathers". On the down-stroke the fan spreads
    # WIDE and low; on the up-stroke it sweeps back and up. Angles are in screen
    # space (0°=right, 90°=down). We fan a set on each side of the body.
    # spread scales the angular width; sweep rotates the whole fan upward as the
    # wing lifts so the crackle visibly animates frame-to-frame.
    spread = 1.0 - 0.35 * f               # widest when wings down
    sweep  = -34 * f                      # fan rotates up as wings lift

    right_dirs = [(-10, 30), (16, 30), (42, 28), (68, 24)]
    left_dirs  = [(190, 30), (164, 30), (138, 28), (112, 24)]
    for base_ang, ln in right_dirs:
        ang = 32 + (base_ang - 32) * spread + sweep
        _forked_bolt(surf, ox + 4, oy + 2, ang, ln, ELEC_YEL, ION_VIOLET, w0=3)
    for base_ang, ln in left_dirs:
        ang = 148 + (base_ang - 148) * spread - sweep
        _forked_bolt(surf, ox - 4, oy + 2, ang, ln, ELEC_YEL, ION_VIOLET, w0=3)

    # TAIL — 2–3 trailing bolts diverging down-left from the body.
    for ang, ln in ((214, 20), (232, 24), (250, 18)):
        _forked_bolt(surf, ox - 2, oy + 8, ang, ln, VOLT_GOLD, ARC_AMBER, w0=2)

    # BODY CORE — stacked circles: amber rim → voltage gold → electric yellow →
    # white nucleus. NO solid bird body, just the glowing plasma ball.
    _aaellipse(surf, ARC_AMBER,  (BCX, BCY), 13, 12)
    _aaellipse(surf, VOLT_GOLD,  (BCX, BCY), 11, 10)
    _aaellipse(surf, ELEC_YEL,   (BCX, BCY), 8, 8)
    _aaellipse(surf, CORE_WHITE, (BCX - 1, BCY - 1), 4, 4)
    pygame.draw.circle(surf, ELEC_YEL, (BCX + 3, BCY + 3), 2)   # faint inner dot

    # TALONS — two tiny bright arc-hooks below the core.
    for tx in (BCX - 6, BCX + 4):
        _bolt(surf, [(tx, BCY + 10), (tx + 2, BCY + 15), (tx - 2, BCY + 17)],
              ELEC_YEL, w=2)

    # HEAD — a small white-hot ball with an electric-yellow corona.
    _aaellipse(surf, VOLT_GOLD,  (HCX, HCY), 7, 7)
    _aaellipse(surf, ELEC_YEL,   (HCX, HCY), 5, 5)
    _aaellipse(surf, CORE_WHITE, (HCX, HCY), 3, 3)
    # Two spark-eyes — bright pinpoints.
    _spark(surf, HCX + 3, HCY - 1, 1, CORE_WHITE)
    _spark(surf, HCX - 2, HCY - 1, 1, ELEC_YEL)

    # CREST — 3 thin bolt zig-zags rising off the crown, brightest at the tips.
    crest_base = [(HCX - 5, CROWN_Y + 4), (HCX, CROWN_Y + 2), (HCX + 5, CROWN_Y + 4)]
    for i, (cx, cy) in enumerate(crest_base):
        tip = (cx + (i - 1) * 3, CROWN_Y - 10 - i % 2 * 2)
        mid = ((cx + tip[0]) // 2 + (2 if i % 2 else -2), (cy + tip[1]) // 2)
        _bolt(surf, [(cx, cy), mid, tip], ELEC_YEL, w=2)
        _spark(surf, tip[0], tip[1], 1, CORE_WHITE)

    # STRAY SPARKS — 3 deterministic-per-frame floaters for crackle life, kept
    # tight-bloom so they punctuate the gaps rather than fogging the fan.
    for _ in range(3):
        sx = BCX + random.randint(-22, 22)
        sy = BCY + random.randint(-20, 18)
        _spark(surf, sx, sy, 1,
               random.choice((CORE_WHITE, ELEC_YEL, ION_VIOLET)), bloom=55)

    return surf


build = _make_prebuilt_skin(_build_frame)
