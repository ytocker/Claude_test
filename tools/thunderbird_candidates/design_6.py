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
HCX, HCY = 44, 32               # head centre — nudged up so it clears the body
CROWN_Y  = 22                   # top of head (follows the raised head)


# ── palette ──────────────────────────────────────────────────────────────────
CORE_WHITE = (255, 255, 255)    # nucleus
FLASH      = (255, 252, 214)    # hot-white flash (body nucleus only)
ELEC_YEL   = (255, 232, 26)     # electric yellow — PRIMARY
VOLT_GOLD  = (255, 179, 0)      # voltage gold — thin ring only
ARC_AMBER  = (255, 122, 0)      # arc amber — thin rim only
ION_VIOLET = (179, 107, 255)    # ion-violet — branch tips only, sparingly


def _flap(angle_deg):
    """0..1 'wing is up' factor. _WING_ANGLES runs 50→-40 (down→up)."""
    return (angle_deg + 40) / 90.0


def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _make_prebuilt_skin(build_fn):
    """Cached `(frame_idx, tilt_deg) -> Surface` getter for build_fn(angle).

    Outline the BOLTS-ONLY sprite, THEN paint the soft plasma aura on top, so
    the outline mask never sees the low-alpha halo — otherwise `_add_outline`
    stamps a dark egg over the whole 28px glow disc. Copied (not imported) to
    keep this scratch file standalone, mirroring the production prebuilt path."""
    state = {"frames": None, "rot": {}}

    def getter(frame_idx, tilt_deg):
        if state["frames"] is None:
            frames = []
            for idx, a in enumerate(_WING_ANGLES):
                lit = _add_outline(build_fn(idx, a))
                # Aura goes on last, over the outlined bolts. _add_outline pads
                # by 2px, so shift the aura to match the new sprite origin.
                _paint_aura(lit, idx, a, pad=2)
                frames.append(lit)
            state["frames"] = frames
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
    """Soft additive halo — the plasma-globe aura. Additive so it reads as
    light, not paint, over any sky."""
    cx, cy = center
    g = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
    gc = (r + 2, r + 2)
    layers = 6
    for i in range(layers, 0, -1):
        rr = int(r * i / layers)
        a = int(peak * (1 - (i - 1) / layers))
        pygame.draw.circle(g, (*color, a), gc, rr)
    surf.blit(g, (cx - r - 2, cy - r - 2), special_flags=pygame.BLEND_RGBA_ADD)


def _paint_aura(surf, frame_idx, wing_angle_deg, pad=0):
    """The soft plasma aura, painted OVER the outlined bolts so it never trips
    the silhouette mask. Pulses a touch brighter on the down-stroke where the
    fan fans widest. `pad` accounts for the 2px _add_outline border shift."""
    f = _flap(wing_angle_deg)
    # Yellow aura dominates; the white inner bloom is kept small + dim so the
    # additive core doesn't blow out to a white ball over the yellow band.
    _radial_glow(surf, (BCX + pad, BCY + pad), 28, ELEC_YEL, peak=int(66 - 14 * f))
    _radial_glow(surf, (BCX + pad, BCY + pad), 11, CORE_WHITE, peak=24)


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


def _forked_bolt(surf, x0, y0, angle_deg, length, color, tip_color, w0=3,
                 *, whip=1.0):
    """Grow one forked plasma tentacle from (x0,y0) heading at angle_deg. The
    trunk zig-zags outward in 3 segments (thick→thin), throwing ONE short branch
    near the tip. `whip` signs/scales the perpendicular zig-zag so the SAME bolt
    reshapes visibly between frames — a wide splay on the down-stroke, a swept
    inversion on the up-stroke. Only the tip gets a violet dot so the star ends
    in bright points without a violet halo swamping the yellow."""
    a = math.radians(angle_deg)
    ca, sa = math.cos(a), math.sin(a)
    pa = a + math.pi / 2
    cpa, spa = math.cos(pa), math.sin(pa)

    def at(t, off):
        return (x0 + ca * length * t + cpa * off,
                y0 + sa * length * t + spa * off)

    j = length * 0.14 * whip
    p0 = (x0, y0)
    p1 = at(0.36, +j)
    p2 = at(0.68, -j * 0.8)
    p3 = at(1.0, +j * 0.35)              # trunk tip — reaches full length

    _bolt(surf, [p0, p1, p2, p3], color, w=w0)
    pygame.draw.lines(surf, CORE_WHITE, False, [p0, p1], max(1, w0 - 1))

    # One short branch peeling off mid-trunk — its side follows the whip too.
    bt = at(0.92, -j * 1.7)
    _bolt(surf, [p2, bt], VOLT_GOLD, w=max(1, w0 - 2), halo_a=0)

    _spark(surf, p3[0], p3[1], 1, tip_color, bloom=80)
    _spark(surf, bt[0], bt[1], 1, VOLT_GOLD, bloom=70)
    return p3


def _build_frame(frame_idx, wing_angle_deg):
    """Bolts + cores only — NO aura (the aura is painted after outlining).

    `frame_idx` drives both the RNG seed and the bolt-whip sign so the four
    frames are genuinely different poses, not jitter of one pose."""
    surf = _new()
    f = _flap(wing_angle_deg)             # 0 = down-stroke, 1 = up-stroke
    random.seed(frame_idx)                # deterministic-per-frame sparks

    ox, oy = BCX - 2, BCY - 4             # bolt origin near core

    # Per-frame whip: alternate the zig-zag sign each frame so bolts visibly
    # snap side-to-side, and scale the magnitude by stroke phase (widest on the
    # down-stroke, tightest/swept on the up-stroke).
    whip = (1.0 if frame_idx % 2 == 0 else -1.0) * (1.0 - 0.45 * f)

    # WING BOLTS — the radiating "feathers". On the down-stroke the fan spreads
    # WIDE and low; on the up-stroke it sweeps back and up.
    spread = 1.0 - 0.35 * f               # widest when wings down
    sweep  = -34 * f                      # fan rotates up as wings lift

    right_dirs = [(-10, 30), (16, 30), (42, 28), (68, 24)]
    left_dirs  = [(190, 30), (164, 30), (138, 28), (112, 24)]
    for base_ang, ln in right_dirs:
        ang = 32 + (base_ang - 32) * spread + sweep
        _forked_bolt(surf, ox + 4, oy + 2, ang, ln, ELEC_YEL, ION_VIOLET,
                     w0=3, whip=whip)
    for base_ang, ln in left_dirs:
        ang = 148 + (base_ang - 148) * spread - sweep
        _forked_bolt(surf, ox - 4, oy + 2, ang, ln, ELEC_YEL, ION_VIOLET,
                     w0=3, whip=-whip)

    # TAIL — trailing bolts diverging down-left, whipping with the frame.
    for ang, ln in ((214, 20), (232, 24), (250, 18)):
        _forked_bolt(surf, ox - 2, oy + 8, ang, ln, VOLT_GOLD, ARC_AMBER,
                     w0=2, whip=whip)

    # BODY CORE — yellow is PRIMARY: amber + gold are 1px rims only, the big
    # readable band is electric yellow, capped by a hot-white flash nucleus.
    pygame.draw.circle(surf, ARC_AMBER, (BCX, BCY), 12, 1)   # 1px amber rim
    pygame.draw.circle(surf, VOLT_GOLD, (BCX, BCY), 11, 1)   # 1px gold ring
    _aaellipse(surf, ELEC_YEL, (BCX, BCY), 9, 9)             # yellow midtone
    _aaellipse(surf, FLASH,    (BCX - 1, BCY - 1), 4, 4)     # white flash core
    pygame.draw.circle(surf, ELEC_YEL, (BCX + 3, BCY + 3), 2)

    # TALONS — a clear forked bolt-pair: two mirrored downward strokes, thick
    # enough to read at 40px as claws, not stray crackle.
    for sgn in (-1, 1):
        tx = BCX + sgn * 4
        _bolt(surf, [(tx, BCY + 9), (tx + sgn * 3, BCY + 17)], ELEC_YEL,
              w=2, halo_a=0)
        _spark(surf, tx + sgn * 3, BCY + 17, 1, ELEC_YEL, bloom=55)

    # HEAD — clearly subordinate: NO pure-white core, just a small yellow ball
    # with a thin gold rim, sitting above the body so it never reads as a
    # snowman second-ball.
    pygame.draw.circle(surf, VOLT_GOLD, (HCX, HCY), 6, 1)   # 1px gold rim
    _aaellipse(surf, ELEC_YEL, (HCX, HCY), 4, 4)
    _spark(surf, HCX, HCY - 1, 1, ELEC_YEL, bloom=60)       # glow, not a core
    # Two spark-eyes — bright pinpoints keep the "face" legible.
    _spark(surf, HCX + 2, HCY, 1, CORE_WHITE, bloom=45)
    _spark(surf, HCX - 2, HCY, 1, ELEC_YEL, bloom=45)

    # CREST — 3 thin bolt zig-zags rising off the crown, brightest at the tips.
    crest_base = [(HCX - 5, CROWN_Y + 4), (HCX, CROWN_Y + 2), (HCX + 5, CROWN_Y + 4)]
    for i, (cx, cy) in enumerate(crest_base):
        # Crest tips also lean with the whip so the crown crackles per-frame.
        lean = (2 if frame_idx % 2 else -2)
        tip = (cx + (i - 1) * 3 + lean, CROWN_Y - 10 - i % 2 * 2)
        mid = ((cx + tip[0]) // 2 + lean, (cy + tip[1]) // 2)
        _bolt(surf, [(cx, cy), mid, tip], ELEC_YEL, w=2)
        _spark(surf, tip[0], tip[1], 1, CORE_WHITE)

    # STRAY SPARKS — deterministic-per-frame floaters for crackle life. The
    # frame-index seed places them in clearly different spots each frame.
    for _ in range(3):
        sx = BCX + random.randint(-22, 22)
        sy = BCY + random.randint(-20, 18)
        _spark(surf, sx, sy, 1,
               random.choice((CORE_WHITE, ELEC_YEL, ION_VIOLET)), bloom=55)

    return surf


build = _make_prebuilt_skin(_build_frame)
