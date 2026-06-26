"""Red panda — DESIGN 3: AUTUMN MONK.

A serene plush dumpling: head and body merged into one near-perfect sphere
with a giant ringed tail wrapping from behind, around the right, and forward
across the lower body to frame the face. The cozy zen read comes from the
sleepy lid-arcs, a single peanut-shaped cream face-mask, and the layered
sphere shading.

Self-contained scratch builder (not registered in store_skins.BUILDERS).
Exposes ``build`` for tools/ninja_render.py, same contract as the other
red_panda candidates.
"""
import math
import pygame

from game.parrot import SPRITE_W, _WING_ANGLES, _add_outline, _aaellipse

COMPOSITE_W, COMPOSITE_H = 64, 84
DY = 12
BCX, BCY = 32, 44
HCX, HCY = 44, 34
CROWN_Y = 24

# Autumn-monk palette. Warm russet plush with deep AO for the tail-body tuck.
BODY    = (185,  87,  51)   # #B95733 main fur
SHADOW  = (110,  48,  25)   # #6E3019 lower-sphere shade
HIGH    = (232, 154,  94)   # #E89A5E mid-highlight + forehead gloss
CREAM   = (244, 227, 198)   # #F4E3C6 cheeks, tail rings, ear fluff
ACCENT  = ( 51,  35,  26)   # #33231A nose, paws, eye accents
AO      = ( 74,  26,   8)   # #4A1A08 heavy overlap occlusion
RUST    = (150,  64,  34)   # tear-tracks / tail seam (between body & shadow)
CREAM_W = (252, 244, 226)   # brightest ring tip


def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _tail_arc(surf, tcx, tcy, r, a0, a1, steps, width,
              core=BODY, rim=SHADOW, ring_ts=(), ring_r=5,
              fringe=False, fringe_dir=1):
    """Lay a thick plush tube along a circular arc and stamp concentric
    cream scarf-bands at the given arc fractions. ``ring_ts`` are 0..1
    positions along the arc where a cream disc is centred; ``ring_r`` sets
    band thickness. The tube core is kept darker than the body so the wrap
    reads as one continuous mass against the sphere."""
    span = a1 - a0

    # Seam undercoat so the tube has a soft dark core where bands sit.
    for i in range(steps + 1):
        a = a0 + span * (i / steps)
        pygame.draw.circle(surf, rim,
                           (int(tcx + math.cos(a) * r),
                            int(tcy + math.sin(a) * r)), width)
    # Russet body of the tube, inset so the rim reads as an outer shade edge.
    for i in range(steps + 1):
        a = a0 + span * (i / steps)
        cx = int(tcx + math.cos(a) * r)
        cy = int(tcy + math.sin(a) * r)
        pygame.draw.circle(surf, core, (cx, cy), max(1, width - 2))
        # Inner-lit top of the tube — a thin highlight chasing the curl.
        hx = int(tcx + math.cos(a) * (r - width * 0.4))
        hy = int(tcy + math.sin(a) * (r - width * 0.4))
        pygame.draw.circle(surf, HIGH, (hx, hy), max(1, width // 3))

    # Cream scarf-bands wrapped around the tube as short fat arcs.
    half = math.radians(13)
    bsteps = 7
    for rt in ring_ts:
        a_cen = a0 + span * rt
        for i in range(bsteps + 1):
            a = a_cen - half + 2 * half * (i / bsteps)
            px = int(tcx + math.cos(a) * r)
            py = int(tcy + math.sin(a) * r)
            pygame.draw.circle(surf, RUST,  (px, py), ring_r + 1)
            pygame.draw.circle(surf, CREAM, (px, py), ring_r)
            # Tiny gloss on the band crown for the plush sheen.
            gx = int(tcx + math.cos(a) * (r - ring_r * 0.5))
            gy = int(tcy + math.sin(a) * (r - ring_r * 0.5))
            pygame.draw.circle(surf, CREAM_W, (gx, gy), max(1, ring_r // 3))

    # Velvet fur fringe — short strokes flicking off the outer tube edge.
    if fringe:
        for i in range(0, steps + 1, 2):
            a = a0 + span * (i / steps)
            ox = math.cos(a)
            oy = math.sin(a)
            bx = tcx + ox * (r + width - 1)
            by = tcy + oy * (r + width - 1)
            ex = bx + ox * (2.6 * fringe_dir)
            ey = by + oy * (2.6 * fringe_dir)
            pygame.draw.line(surf, RUST, (int(bx), int(by)), (int(ex), int(ey)), 1)


def _ear(surf, cx, cy, flip):
    """Small low rounded triangular ear with cream inner fluff."""
    w = 7
    h = 8
    tip = (cx, cy - h)
    base_l = (cx - w // 2, cy + 2)
    base_r = (cx + w // 2, cy + 2)
    pygame.draw.polygon(surf, SHADOW, [tip, base_l, base_r])
    pygame.draw.polygon(surf, BODY,
                        [(cx, cy - h + 1),
                         (cx - w // 2 + 1, cy + 1),
                         (cx + w // 2 - 1, cy + 1)])
    # Cream inner fluff offset toward the head centre.
    inset = -flip
    pygame.draw.polygon(surf, CREAM,
                        [(cx + inset, cy - h + 3),
                         (cx - 2 + inset, cy),
                         (cx + 2 + inset, cy)])


def build_autumn_monk(wing_angle_deg):
    """One plush-sphere frame. ``wing_angle_deg`` (from _WING_ANGLES) only
    nudges the tail tip — up-poses perk the tip, down-poses droop it — so the
    contemplative dumpling barely breathes between frames."""
    surf = _new()

    # Map the wing angle to a small tail-tip lift: +up, -down.
    perk = wing_angle_deg / 50.0          # ~+1 fully up, ~-0.8 fully down
    tip_dy = int(round(-perk * 3))        # tip rises on up-pose

    bx, by = BCX, BCY - 4                 # sphere centre (32, 40)
    R = 19

    # --- (1) TAIL BEHIND --------------------------------------------------
    # Comes off the lower-right of the sphere, sweeps up the right side and
    # arcs over behind the head. Drawn first so the body sits in front of it.
    _tail_arc(surf, bx + 1, by + 4, 23,
              math.radians(78), math.radians(-118),
              steps=30, width=11,
              core=(140, 55, 28),
              ring_ts=(0.40, 0.78), ring_r=7,
              fringe=False)

    # --- BODY / HEAD SPHERE (4-layer radial shade) -----------------------
    # Shadow base, offset down-right for the light-from-upper-left read.
    _aaellipse(surf, SHADOW, (bx + 3, by + 4), R + 1, R + 1)
    # Deep AO crescent where the front tail will tuck across the lower body.
    _aaellipse(surf, AO,     (bx + 2, by + 9), R - 2, R - 6)
    # Main plush body.
    _aaellipse(surf, BODY,   (bx, by, ), R, R)
    # Mid-highlight breast, tightened to top-centre of the sphere.
    _aaellipse(surf, HIGH,   (bx - 2, by - 6), 8, 5)
    # Subtle forehead gloss — a single small bright dot, not a stray patch.
    pygame.draw.circle(surf, CREAM_W, (bx - 3, by - 10), 3)

    # Ears — low and rounded, sitting on the upper sphere.
    _ear(surf, bx - 9, CROWN_Y + 2, flip=-1)
    _ear(surf, bx + 9, CROWN_Y + 2, flip=1)

    # --- FACE -------------------------------------------------------------
    # One peanut-shaped cream mask: two overlapping ellipses fuse into a
    # single wide cheeks+muzzle field that reads cleanly at thumbnail size.
    _aaellipse(surf, CREAM, (bx - 4, by + 1), 9, 8)
    _aaellipse(surf, CREAM, (bx + 4, by + 1), 9, 8)

    # Sleepy eyes — one drooping dark lid-arc per side with a single gleam.
    for ex in (bx - 6, bx + 6):
        pygame.draw.arc(surf, ACCENT,
                        pygame.Rect(ex - 4, by - 6, 8, 6),
                        math.radians(200), math.radians(340), 3)
        pygame.draw.circle(surf, CREAM_W, (ex + 1, by - 1), 1)

    # Small dark nose with a gentle gloss, centred on the muzzle band.
    _aaellipse(surf, ACCENT, (bx, by + 1), 3, 2)
    pygame.draw.circle(surf, HIGH, (bx - 1, by), 1)
    # Gentle little smile.
    pygame.draw.arc(surf, ACCENT,
                    pygame.Rect(bx - 4, by + 1, 8, 7),
                    math.radians(200), math.radians(340), 2)

    # --- PAWS -------------------------------------------------------------
    # Two small dark paw-dots peeking below the body sphere.
    _aaellipse(surf, ACCENT, (bx - 6, by + R - 2), 3, 2)
    _aaellipse(surf, ACCENT, (bx + 6, by + R - 2), 3, 2)

    # --- (2) TAIL FRONT WRAP (drawn LAST, over the lower body) ------------
    # From the body's 3-o'clock, curling DOWN and across the bottom with the
    # cream-ringed tip pointing inward — this is the framing hero element.
    # AO smear first so the wrap reads as resting in front of the belly.
    _aaellipse(surf, AO, (bx + 2, by + R - 1), R - 4, 5)

    # Tip droop/perk rides the pose via the arc's end angle and tip_dy.
    end_a = math.radians(212 + (-perk * 6))
    _tail_arc(surf, bx, by + 4 + tip_dy, 21,
              math.radians(8), end_a,
              steps=24, width=10,
              core=(140, 55, 28),
              ring_ts=(0.45, 0.85), ring_r=7,
              fringe=False)

    # Bright cream-ringed terminal tip resting near the front-bottom centre.
    a = end_a
    tx = int(bx + math.cos(a) * 21)
    ty = int(by + 4 + tip_dy + math.sin(a) * 21)
    pygame.draw.circle(surf, RUST,    (tx, ty), 9)
    pygame.draw.circle(surf, CREAM_W, (tx, ty), 8)
    pygame.draw.circle(surf, CREAM,   (tx + 1, ty + 1), 4)

    return surf


def _make_prebuilt_skin(build_fn):
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


build = _make_prebuilt_skin(build_autumn_monk)
