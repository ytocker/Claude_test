"""Red panda — DESIGN 5: CINDER GUARDIAN.

Mythic ember-spirit prestige skin: a tall plumed tail rises like a torch
above an upright, proud body, its rings burning hotter toward a white-hot
tip. The ember at the tip is the light source, so the body's back rim and
the front chest both catch a warm bounce. Self-contained (full body + head
+ upward torch tail) rather than the back-only chassis the other candidates
share, because the rising-tail silhouette and ember lighting need to own the
whole figure.
"""
import math
import pygame

from game.parrot import SPRITE_W, _WING_ANGLES, _add_outline, _aaellipse

COMPOSITE_W = SPRITE_W   # 64
COMPOSITE_H = 84
DY          = 12
BCX, BCY = 32, 32 + DY   # body centre (32, 44)
HCX, HCY = 44, 22 + DY   # head centre (44, 34)
CROWN_Y  = 12 + DY        # 24

# Ember palette — russet body lit from above by the torch tail.
FUR     = (177, 74, 36)    # #B14A24 body
SHADOW  = (92, 36, 16)     # #5C2410 shadow
HILITE  = (255, 179, 71)   # #FFB347 highlight / rim
CREAM   = (255, 233, 194)  # #FFE9C2 mask / standard ring
GLOW    = (255, 106, 26)   # #FF6A1A glow-orange
HOTTIP  = (255, 255, 200)  # #FFFFC8 white-hot tip
EYEDK   = (40, 22, 12)
BELLY   = (140, 56, 28)    # mid russet undertone beneath the bright chest


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


def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _flap(angle_deg):
    """0 = down-pose (tail held highest/brightest), 1 = up-pose (tail tilts)."""
    return (angle_deg + 40) / 90.0


def _eye(surf, cx, cy, r):
    # Warm ember-lit rim around the eye — the torch above catches the lids.
    pygame.draw.circle(surf, GLOW, (cx, cy), r + 1)
    pygame.draw.circle(surf, (255, 250, 244), (cx, cy), r)
    pygame.draw.circle(surf, EYEDK, (cx + max(1, r // 4), cy), max(2, r - 1))
    pygame.draw.circle(surf, (255, 255, 255), (cx - r // 3, cy - r // 3),
                       max(1, r // 3))
    # Dark brow-mask arc above the eye — thickens the eye-stripe region so the
    # red-panda face pattern reads as a distinct dark mask at 40px.
    pygame.draw.arc(surf, SHADOW, pygame.Rect(cx - 4, cy - 4, 8, 6),
                    math.radians(20), math.radians(160), 2)


def build_cinder_guardian(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)
    down = 1.0 - f   # 1 at down-pose (tail highest), 0 at up-pose

    # ---- Tail centre-line: rises from the rump up-left to a torch tip. ----
    # Up-pose tilts the tip a touch further left; down-pose holds it high.
    root = (20.0, 49.0)
    tip  = (10.0 - f * 1.5, 14.0 + f * 1.0)
    ctrl = (10.0 - f * 1.5, 30.0)   # quadratic control bows the plume slightly

    n = 12
    pts = []
    for i in range(n):
        t = i / (n - 1)
        omt = 1.0 - t
        x = omt * omt * root[0] + 2 * omt * t * ctrl[0] + t * t * tip[0]
        y = omt * omt * root[1] + 2 * omt * t * ctrl[1] + t * t * tip[1]
        pts.append((x, y))

    # Russet plume tube — overlapping circles, width tapering 9 -> 5.
    for i, (x, y) in enumerate(pts):
        t = i / (n - 1)
        w = 9 - int(round(t * 4))
        # Dark seam underlay on the lower/right edge for volume.
        pygame.draw.circle(surf, SHADOW, (int(x + 1), int(y + 1)), max(2, w - 1))
        pygame.draw.circle(surf, FUR, (int(x), int(y)), w)

    # Rings as the hero: WIDE full-width bands so the tail reads as a striped
    # torch (red-panda + fire), not a russet tube with dots. Spacer SHADOW
    # rings between the bright bands give the alternating banded silhouette.
    # rr overhangs the plume by 1-2px on purpose. Bottom cream -> hot top.
    ring_ramp = [
        (4,  CREAM,           7),   # full-width cream band, lower tail
        (6,  (255, 214, 130), 7),   # warm yellow band
        (8,  (255, 196,  80), 6),   # hot orange-yellow band
        (10, HOTTIP,          6),   # white-hot band near terminal
    ]
    for idx, col, rr in ring_ramp:
        x, y = pts[idx]
        # Dark spacer halo so each bright band separates from its neighbour.
        pygame.draw.circle(surf, SHADOW, (int(x), int(y)), rr + 1)
        pygame.draw.circle(surf, col, (int(x), int(y)), rr)

    # Baked bright rind on the top 3 bands — an opaque hot rim on the inner
    # (tip-facing) side so the torch reads even on a bright daytime sky where
    # additive glow washes out.
    for idx, col, rr in ring_ramp[-3:]:
        x, y = pts[idx]
        pygame.draw.circle(surf, HOTTIP, (int(x), int(y - 1)), rr - 1)

    # Small additive ember kiss only at the very tip — keeps a live spark
    # without a broad multi-ring halo that blows out on dark sky.
    glow_boost = int(round(down * 3))
    glow = pygame.Surface((32, 32), pygame.SRCALPHA)
    gcx = gcy = 16
    for rr, a in ((9 + glow_boost, 55), (5, 110)):
        pygame.draw.circle(glow, (255, 120, 20, a), (gcx, gcy), rr)
    surf.blit(glow, (int(pts[11][0]) - gcx, int(pts[11][1]) - gcy),
              special_flags=pygame.BLEND_RGBA_ADD)

    # White-hot terminal tip + ember sparks lifting off it. Capped at 3px so
    # it does not bloom out against a night-biome sky.
    tx, ty = int(pts[11][0]), int(pts[11][1])
    pygame.draw.circle(surf, HOTTIP, (tx, ty), 3)
    pygame.draw.circle(surf, (255, 255, 255), (tx, ty - 1), 2)
    for dx, dy in ((-4, -3), (3, -5), (-2, -6)):
        pygame.draw.circle(surf, (255, 160, 40), (tx + dx, ty + dy), 1)

    # ---- Body: stately, slightly slimmer than wide, 3-layer shading. ----
    bcx, bcy = BCX + 2, BCY + 2
    _aaellipse(surf, SHADOW, (bcx + 1, bcy + 2), 13, 14)
    _aaellipse(surf, FUR,    (bcx, bcy),         12, 13)
    # Two-tone split: a large cream front panel is the whole forward-facing
    # surface, so the dark-back / cream-front read survives at 40px. The mid
    # russet belly core sits between them as a transition undertone.
    _aaellipse(surf, BELLY, (bcx, bcy + 4), 10, 11)   # widened belly core
    _aaellipse(surf, CREAM, (bcx - 1, bcy + 3), 10, 11)  # forward chest blaze

    # Back/top rim-light — thin warm line, lit by the torch above.
    pygame.draw.arc(surf, HILITE, (bcx - 13, bcy - 14, 22, 22),
                    math.radians(40), math.radians(160), 2)
    # Chest rim-light arc — ember bounce on the lower front.
    pygame.draw.arc(surf, (255, 140, 40), (BCX - 2, BCY, 12, 16),
                    math.radians(200), math.radians(340), 2)

    # ---- Head: balanced, held slightly proud/high, bold cream mask. ----
    hcx, hcy = HCX, HCY - 1
    _aaellipse(surf, SHADOW, (hcx + 1, hcy + 1), 11, 11)
    _aaellipse(surf, FUR,    (hcx, hcy),         10, 10)

    # Ears with lit tips (torch catches the very top of each ear).
    for ex, sgn in ((hcx - 8, -1), (hcx + 8, +1)):
        pygame.draw.circle(surf, SHADOW, (ex, CROWN_Y + 4), 6)
        pygame.draw.circle(surf, FUR, (ex, CROWN_Y + 4), 5)
        pygame.draw.circle(surf, CREAM, (ex + sgn, CROWN_Y + 5), 3)
        # Lit ear-tip highlight.
        pygame.draw.circle(surf, HILITE, (ex, CROWN_Y), 2)

    # Bold cream mask — two cheek lobes plus a central blaze.
    _aaellipse(surf, CREAM, (hcx - 5, hcy + 2), 6, 7)
    _aaellipse(surf, CREAM, (hcx + 6, hcy + 2), 6, 7)
    _aaellipse(surf, CREAM, (hcx, hcy + 3), 4, 7)
    for dx in (-6, 7):
        pygame.draw.line(surf, SHADOW, (hcx + dx, hcy - 4),
                         (hcx + dx + (1 if dx > 0 else -1), hcy + 4), 2)

    _eye(surf, hcx - 4, hcy, 3)
    _eye(surf, hcx + 6, hcy, 3)

    # Prominent nose + muzzle line — enlarged so it anchors the dark mask.
    pygame.draw.circle(surf, EYEDK, (hcx + 1, hcy + 6), 4)
    pygame.draw.circle(surf, (90, 50, 40), (hcx, hcy + 5), 1)
    pygame.draw.line(surf, EYEDK, (hcx + 1, hcy + 8), (hcx + 1, hcy + 10), 1)

    return surf


build = _make_prebuilt_skin(build_cinder_guardian)
