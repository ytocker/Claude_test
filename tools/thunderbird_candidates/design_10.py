"""THUNDERBIRD candidate — Design 10: LIVE WIRE (scratch exploration).

A snapped high-voltage power line that flies. The bird IS a whipping,
arc-flashing cable — an elongated dark-insulation body reads as a thick wire
run, banded like segmented insulation. The HEAD is the frayed broken end: a
burst of bright radiating filaments where the cable snapped. Wings are whipping
cable-loops, and the chest carries the arc-flash "break" bloom that is the
single brightest point on the skin. High-voltage yellow is the dominant colour.

Scratch-only: this mirrors the animal-skin contract so it can be previewed by
tools/ninja_render.py, but it is NEVER registered in any BUILDERS map and never
touches production art.

North star: "a skin lives or dies at 40px in motion." The tall narrow
insulation ellipse is the tell — a silhouette clearly taller and thinner than a
round bird — and the white-cored arc-flash bloom on the chest is the brightest
speck that survives the downscale, so the eye still reads a live, sparking wire.
"""
import math

import pygame

from game.parrot import _WING_ANGLES, _add_outline, _aaellipse


# ── canvas constants (mirror the thunderbird tall-canvas layout) ─────────────
COMPOSITE_W, COMPOSITE_H = 64, 84
BCX, BCY = 32, 44               # body centre
HCX, HCY = 44, 34               # head centre (the frayed broken end)
CROWN_Y  = 24                   # top of head


# ── palette ──────────────────────────────────────────────────────────────────
ARC_WHITE   = (255, 255, 255)   # arc-flash core / brightest point
HV_YELLOW   = (255, 221, 0)     # high-voltage yellow — dominant colour
LIVE_GOLD   = (245, 163, 0)     # live-gold mid glow
INSUL_DARK  = (43, 38, 32)      # insulation — structure + banding
INSUL_BAND  = (28, 24, 20)      # slightly darker insulation banding ring
MOLTEN      = (255, 85, 0)      # molten spark drips


def _strike(angle_deg):
    """0..1 'overload is peaking' factor. 1 = down-stroke (angle=50), the
    moment the cable-loops whip widest and the chest arc-flash pulses brightest."""
    return 1 - (angle_deg + 40) / 90.0


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


def _bloom(surf, center, r, color, peak):
    """Additive arc-flash bloom. Additive so it reads as emitted light over any
    sky rather than painted haze — the chest break is a genuine light source."""
    cx, cy = center
    g = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
    gc = (r + 2, r + 2)
    layers = 6
    for i in range(layers, 0, -1):
        rr = int(r * i / layers)
        a = int(peak * (1 - (i - 1) / layers))
        pygame.draw.circle(g, (*color, a), gc, rr)
    surf.blit(g, (cx - r - 2, cy - r - 2), special_flags=pygame.BLEND_RGBA_ADD)


def _cable_wing(surf, angle_deg, side):
    """A whipping cable-loop: a thick dark insulation arc that sweeps out from the
    shoulder and curves back, with a thin high-voltage inner glow line tracing it.
    `side` is +1 (far/right) or -1 (near/left). On the down-stroke the loop whips
    wide; on the up-stroke it compresses toward the body."""
    s = _strike(angle_deg)                  # 1 = whip wide (down-stroke)
    root = (BCX + side * 7, BCY - 4)
    reach = 12 + int(round(10 * s))         # loop reach grows with the overload
    drop  = 10 - int(round(8 * s))          # loop rides high on the down-stroke

    # Sample a curved cable path: shoulder → wide bow → curl back to lower body.
    ctrl = (root[0] + side * reach, root[1] - reach + 4)
    endp = (root[0] + side * (reach - 6), root[1] + drop)
    pts = []
    for k in range(9):
        t = k / 8.0
        # Quadratic Bézier for a clean loop sweep.
        x = (1 - t) ** 2 * root[0] + 2 * (1 - t) * t * ctrl[0] + t * t * endp[0]
        y = (1 - t) ** 2 * root[1] + 2 * (1 - t) * t * ctrl[1] + t * t * endp[1]
        pts.append((x, y))

    # Thick dark cable body (survives 40px) then the thin lit inner arc glow.
    inner = HV_YELLOW if s > 0.45 else LIVE_GOLD
    pygame.draw.lines(surf, INSUL_DARK, False, pts, 4)
    pygame.draw.lines(surf, inner, False, pts, 2)
    # A bright bead where the cable is most bent — the current pooling in the loop.
    bx, by = int(pts[4][0]), int(pts[4][1])
    _bloom(surf, (bx, by), 4, HV_YELLOW, peak=int(40 + 40 * s))
    pygame.draw.circle(surf, ARC_WHITE, (bx, by), 1)


def _frayed_head(surf, s):
    """The broken cable end: radiating bright filaments bursting from the head
    centre, a spark-eye, and a hard arc-flash wedge for the 'mouth'. No round
    head, no traditional beak — this is where the wire snapped."""
    # A soft halo so the frayed end reads as a hot break even when filaments thin.
    # Kept below the chest bloom so the chest stays the single brightest point.
    _bloom(surf, (HCX, HCY), 10, LIVE_GOLD, peak=int(24 + 16 * s))

    # 6 short radiating filaments, each a dark-cored strand with a lit outer glow
    # so it holds a thick enough line at 40px.
    n = 6
    for i in range(n):
        ang = (-40 + i * (200 / (n - 1))) * math.pi / 180.0   # fan up-and-out
        length = 9 + (i % 2) * 3
        ex = HCX + math.cos(ang) * length
        ey = HCY - math.sin(ang) * length
        pygame.draw.line(surf, INSUL_DARK, (HCX, HCY), (ex, ey), 3)
        pygame.draw.line(surf, HV_YELLOW, (HCX, HCY), (ex, ey), 2)
        pygame.draw.circle(surf, ARC_WHITE, (int(ex), int(ey)), 1)

    # The 'mouth': a hard arc-flash wedge stabbing forward off the break.
    pygame.draw.polygon(surf, HV_YELLOW,
                        [(HCX + 8, HCY + 1), (HCX + 15, HCY + 4), (HCX + 8, HCY + 6)])
    pygame.draw.polygon(surf, ARC_WHITE,
                        [(HCX + 8, HCY + 2), (HCX + 12, HCY + 4), (HCX + 8, HCY + 5)])

    # Spark-eye — bright yellow bead with a white-hot core; the head's anchor point.
    pygame.draw.circle(surf, HV_YELLOW, (HCX - 1, HCY - 2), 3)
    pygame.draw.circle(surf, ARC_WHITE, (HCX - 1, HCY - 2), 1)


def _build_frame(wing_angle_deg):
    surf = _new()
    s = _strike(wing_angle_deg)              # 1 on the down-stroke overload

    # FAR wing first (behind the body).
    _cable_wing(surf, wing_angle_deg, +1)

    # TAIL — a long trailing wire end sweeping down-left off the lower body, with
    # a small sparking terminus so the broken run clearly continues past the body.
    troot = (BCX - 3, BCY + 10)
    ttip  = (BCX - 18, BCY + 32)
    tmid  = (BCX - 8, BCY + 22)
    pygame.draw.lines(surf, INSUL_DARK, False, [troot, tmid, ttip], 4)
    pygame.draw.lines(surf, HV_YELLOW, False, [troot, tmid, ttip], 2)
    pygame.draw.polygon(surf, HV_YELLOW,
                        [(ttip[0], ttip[1] - 3), (ttip[0] - 4, ttip[1] + 2),
                         (ttip[0] + 2, ttip[1] + 3)])
    pygame.draw.circle(surf, ARC_WHITE, ttip, 1)

    # BODY — a tall, narrow insulation ellipse. This elongated form is the whole
    # tell: clearly taller and thinner than a round bird, so the "thick cable"
    # read survives the 40px downscale.
    body = _new()
    _aaellipse(body, INSUL_DARK, (BCX, BCY), 10, 20)
    # Banding rings — segmented insulation. Thin darker lines at ~6px intervals.
    for by in range(BCY - 12, BCY + 15, 6):
        half = int(math.sqrt(max(0.0, 1 - ((by - BCY) / 20.0) ** 2)) * 10)
        if half > 2:
            pygame.draw.line(body, INSUL_BAND, (BCX - half, by), (BCX + half, by), 2)
    surf.blit(body, (0, 0))

    # TALONS — two hook-clamp L-brackets hanging off the lower body, dark with
    # yellow glow tips (the line-worker's clamps still gripping the dead wire).
    for sx in (-1, 1):
        bx = BCX + sx * 5
        pygame.draw.lines(surf, INSUL_DARK, False,
                          [(bx, BCY + 16), (bx, BCY + 21), (bx - sx * 4, BCY + 21)], 3)
        pygame.draw.circle(surf, HV_YELLOW, (bx - sx * 4, BCY + 21), 2)
        pygame.draw.circle(surf, ARC_WHITE, (bx - sx * 4, BCY + 21), 1)

    # HEAD — the frayed broken cable end.
    _frayed_head(surf, s)

    # NEAR wing last (in front of the body).
    _cable_wing(surf, wing_angle_deg, -1)

    # CHEST ARC-FLASH — the "break". The single brightest point: a tight yellow
    # bloom ringing a hard white core. Peaks are kept low so the additive light
    # stays a concentrated hotspot and never washes out the dark cable body — the
    # elongated insulation silhouette has to survive the bloom, not drown in it.
    chest = (BCX + 2, BCY - 8)
    _bloom(surf, chest, 13, HV_YELLOW, peak=int(28 + 22 * s))
    _bloom(surf, chest, 7, ARC_WHITE, peak=int(40 + 30 * s))
    pygame.draw.circle(surf, ARC_WHITE, chest, 2)

    # MOLTEN SPARK DRIPS — 4 falling drops below the bird, positions drifting per
    # frame (indexed off the wing angle) so the sparks visibly rain as it flaps.
    fi = _WING_ANGLES.index(wing_angle_deg) if wing_angle_deg in _WING_ANGLES else 0
    drips = [(BCX - 6, 2, 0), (BCX + 8, 2, 5), (BCX - 12, 1, 10), (BCX + 3, 1, 3)]
    for dx, dr, phase in drips:
        dy = BCY + 24 + ((fi * 6 + phase) % 20)
        _bloom(surf, (dx, dy), 3, MOLTEN, peak=90)
        pygame.draw.circle(surf, HV_YELLOW, (dx, dy), dr)

    return surf


build = _make_prebuilt_skin(_build_frame)
