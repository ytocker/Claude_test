"""THUNDERBIRD candidate — Design 8: CIRCUIT RAPTOR (scratch exploration).

An overloaded printed-circuit-board bird. The body is a dark board substrate;
every "feather" is a copper trace routed in hard 90°/45° steps, joints are
solder pads, and current lights the whole net up. Trace-yellow is the dominant
colour element read against the dark board base, so the silhouette holds a
strong value contrast on a bright day sky.

Scratch-only: this mirrors the animal-skin contract so it can be previewed by
tools/ninja_render.py, but it is NEVER registered in any BUILDERS map and never
touches production art.

North star: "a skin lives or dies at 40px in motion." The dark board polygon +
solid wing panels carry the shape when the thin traces sink below a pixel; the
white-cored solder pads (eye + node dots) stay the brightest points and survive
the downscale, so the bird still reads as a hard-edged geometric raptor.
"""
import math
import random

import pygame

from game.parrot import _WING_ANGLES, _add_outline


# ── canvas constants (mirror the thunderbird tall-canvas layout) ─────────────
COMPOSITE_W, COMPOSITE_H = 64, 84
BCX, BCY = 32, 44               # body centre
# Head pushed forward + up off the body so clear sky opens between the head
# hexagon and the body ellipse — the beak silhouette needs breathing room.
HCX, HCY = 48, 31               # head centre
CROWN_Y  = 21                   # top of head


# ── palette ──────────────────────────────────────────────────────────────────
BOARD_DARK   = (14, 42, 30)     # PCB substrate — dominant structure
TRACE_YEL    = (255, 232, 26)   # copper trace lit — dominant line colour
TRACE_OFF    = (120, 90, 5)     # trace fully unlit — deep gap vs lit yellow
NODE_WHITE   = (255, 255, 255)  # solder-pad core / brightest point (eye only)
SOLDER_GOLD  = (200, 160, 50)   # pad ring / unlit solder / lesser node cores
BEAK_AMBER   = (220, 140, 20)   # hard beak wedge — dimmed off trace-yellow


def _strike(angle_deg):
    """0..1 'current is peaking' factor. 1 = down-stroke (angle=50)."""
    return 1 - (angle_deg + 40) / 90.0


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


def _glow(surf, center, r, color, peak=30):
    """Faint additive bloom under the board — the 'powered up' halo. Additive so
    it reads as emitted light over any sky rather than painted haze."""
    cx, cy = center
    g = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
    gc = (r + 2, r + 2)
    layers = 5
    for i in range(layers, 0, -1):
        rr = int(r * i / layers)
        a = int(peak * (1 - (i - 1) / layers))
        pygame.draw.circle(g, (*color, a), gc, rr)
    surf.blit(g, (cx - r - 2, cy - r - 2), special_flags=pygame.BLEND_RGBA_ADD)


def _trace(surf, pts, color, w=2):
    """A hard-edged copper polyline. No anti-alias smoothing — traces are meant
    to look etched, right-angled, and mechanical, not organic."""
    if len(pts) >= 2:
        pygame.draw.lines(surf, color, False, pts, w)


def _pad(surf, x, y, r, node_c):
    """A solder pad: gold ring, lit-trace fill, gold core. Gold (not white) cores
    everywhere but the eye so nothing competes with the single white eye point —
    the eye must win the value hierarchy at 40px."""
    x, y = int(x), int(y)
    pygame.draw.circle(surf, SOLDER_GOLD, (x, y), r + 1)
    pygame.draw.circle(surf, node_c, (x, y), r)
    pygame.draw.circle(surf, SOLDER_GOLD, (x, y), 1)


def _eye_pad(surf, x, y, node_c):
    """The one pure-white speck on the skin — the solder-pad eye. r=5 pad with an
    r=2 NODE_WHITE core; the only r=2 white anywhere, so it reads as the brightest
    point and anchors the raptor's gaze at 40px."""
    x, y = int(x), int(y)
    pygame.draw.circle(surf, SOLDER_GOLD, (x, y), 5)
    pygame.draw.circle(surf, node_c, (x, y), 4)
    pygame.draw.circle(surf, NODE_WHITE, (x, y), 2)


def _wing_panel(surf, angle_deg, side, pad_lit):
    """A flat angular copper-clad wing panel with parallel traces routed root→tip.
    `side` is +1 (far/right) or -1 (near/left). The panel vertices swing with the
    flap so the four frames animate a clear up/down stroke, and the near wing is
    drawn larger to sit in front. A 1px yellow polygon edge silhouettes the hard
    geometric panel boundary against sky — that's what separates a circuit wing
    from a feathered one. `pad_lit(idx)` sequences current root→tip along traces."""
    f = _flap(angle_deg)
    # Wing lifts (tip rises) as the flap angle climbs toward the up-stroke.
    lift = int(round(18 * (1 - f)))         # tip drops on down-stroke
    root_x = BCX + side * 6
    root_y = BCY - 2
    reach = 20 if side < 0 else 15          # near wing reaches further
    span  = 15 if side < 0 else 11
    tipx = root_x + side * reach
    tipy = root_y - span + lift
    midx = root_x + side * (reach // 2)
    midy = root_y - span - 3 + lift // 2    # a kink so the panel is faceted
    # Board-dark panel: root notch → mid facet → tip → lower edge back to root.
    poly = [
        (root_x, root_y - 5),
        (midx, midy),
        (tipx, tipy),
        (tipx - side * 4, tipy + 8),
        (root_x, root_y + 5),
    ]
    pygame.draw.polygon(surf, BOARD_DARK, poly)
    pygame.draw.polygon(surf, TRACE_YEL, poly, 1)
    # Three parallel copper traces from the root out toward the tip, each ending
    # in a pad indexed 0(root)→2(tip). The pulse lights them in sequence so the
    # eye reads current travelling outward across the flap cycle.
    for k in range(3):
        oy = (k - 1) * 4
        r0 = (root_x, root_y + oy)
        # 45° dog-leg then straight to a point along the leading edge.
        knee = (root_x + side * (reach // 2), root_y + oy - (1 - k) * 2)
        t = (tipx - side * 2, tipy + 3 + k * 3)
        trace_c = TRACE_YEL if pad_lit(k) else TRACE_OFF
        _trace(surf, [r0, knee, t], trace_c, w=2)
        _pad(surf, t[0], t[1], 2, trace_c)


def _build_frame(wing_angle_deg):
    surf = _new()
    s = _strike(wing_angle_deg)
    # Node brightness pulses with the down-stroke — current peaks as the wing
    # drives down, dims as it recovers on the up-stroke.
    node_c = TRACE_YEL if s > 0.5 else TRACE_DIM
    random.seed(wing_angle_deg)             # deterministic-per-frame sparks

    # Powered halo — brighter on the down-stroke surge.
    _glow(surf, (BCX, BCY), 30, TRACE_YEL, peak=int(30 + 14 * s))

    # FAR wing first (drawn behind the body).
    _wing_panel(surf, wing_angle_deg, +1, node_c)

    # TAIL — a bus of three parallel traces running down-left off the lower body,
    # terminated in pads so the "signal" clearly exits the board.
    tbx, tby = BCX - 2, BCY + 12
    for k in range(3):
        ox = (k - 1) * 3
        end = (tbx - 12 + k * 2, tby + 16)
        _trace(surf, [(tbx + ox, tby), (tbx + ox - 4, tby + 8), end], node_c, w=2)
        _pad(surf, end[0], end[1], 1, node_c)

    # BODY — dark board substrate ellipse. Hard value block that carries the
    # silhouette at 40px once the traces thin out.
    body = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    pygame.draw.ellipse(body, BOARD_DARK, (BCX - 16, BCY - 14, 32, 28))
    surf.blit(body, (0, 0))

    # BODY TRACES — a central vertical bus with symmetric 90°/45° branches and a
    # solder pad at every junction. This is the dominant yellow read on the body.
    top = (BCX, BCY - 12)
    bot = (BCX, BCY + 12)
    _trace(surf, [top, bot], node_c, w=2)
    junctions = [BCY - 8, BCY - 2, BCY + 4]
    for i, jy in enumerate(junctions):
        reach = 9 - i * 2
        # Right branch: straight then 45° kick down; left branch mirrored up.
        _trace(surf, [(BCX, jy), (BCX + reach, jy), (BCX + reach + 3, jy + 3)],
               node_c, w=2)
        _trace(surf, [(BCX, jy), (BCX - reach, jy), (BCX - reach - 3, jy - 3)],
               node_c, w=2)
        _pad(surf, BCX, jy, 2, node_c)
        _pad(surf, BCX + reach + 3, jy + 3, 1, node_c)
        _pad(surf, BCX - reach - 3, jy - 3, 1, node_c)
    # One SIGNAL-GREEN accent trace only — a diagonal via across the board.
    _trace(surf, [(BCX - 8, BCY + 6), (BCX - 2, BCY), (BCX + 6, BCY - 6)],
           SIGNAL_GREEN, w=1)
    _pad(surf, top[0], top[1], 2, node_c)
    _pad(surf, bot[0], bot[1], 2, node_c)

    # TALONS — two right-angle bracket polylines (⌐ and ¬) hanging below the body.
    _trace(surf, [(BCX - 7, BCY + 12), (BCX - 7, BCY + 17), (BCX - 3, BCY + 17)],
           node_c, w=2)
    _trace(surf, [(BCX + 7, BCY + 12), (BCX + 7, BCY + 17), (BCX + 3, BCY + 17)],
           node_c, w=2)

    # HEAD — a hard faceted hexagon of board-dark. Not round: the raptor read is
    # angular and machined.
    head = [
        (HCX - 6, HCY - 2),
        (HCX - 3, HCY - 8),
        (HCX + 5, HCY - 7),
        (HCX + 8, HCY),
        (HCX + 4, HCY + 7),
        (HCX - 4, HCY + 6),
    ]
    pygame.draw.polygon(surf, BOARD_DARK, head)
    # A short trace linking head net to body net so the board reads continuous.
    _trace(surf, [(HCX - 4, HCY + 4), (BCX + 6, BCY - 6)], node_c, w=1)

    # BEAK — a hard amber triangular wedge off the head's forward facet.
    pygame.draw.polygon(surf, BEAK_AMBER,
                        [(HCX + 8, HCY - 1), (HCX + 15, HCY + 2), (HCX + 8, HCY + 4)])

    # EYE — one bright round solder pad. The single strongest white point.
    _pad(surf, HCX + 2, HCY - 1, 4, node_c)

    # CREST — two straight antenna-traces rising off the crown to bright nodes.
    for cx0, dx in ((HCX - 3, -3), (HCX + 2, 2)):
        tip = (cx0 + dx, CROWN_Y - 4)
        _trace(surf, [(cx0, CROWN_Y + 6), tip], node_c, w=2)
        pygame.draw.circle(surf, SOLDER_GOLD, tip, 3)
        pygame.draw.circle(surf, node_c, tip, 2)
        pygame.draw.circle(surf, NODE_WHITE, tip, 1)

    # NEAR wing last (in front of the body).
    _wing_panel(surf, wing_angle_deg, -1, node_c)

    # STRAY SPARKS — two deterministic-per-frame drifting current dots for life.
    for _ in range(2):
        sx = BCX + random.randint(-20, 20)
        sy = BCY + random.randint(-16, 16)
        _glow(surf, (sx, sy), 4, TRACE_YEL, peak=90)
        pygame.draw.circle(surf, NODE_WHITE, (sx, sy), 1)

    return surf


build = _make_prebuilt_skin(_build_frame)
