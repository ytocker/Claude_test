"""Candidate COSMIC JELLY skins for the ANIMALS Store — round-1 exploration.

A LEGENDARY spectacle skin, and the set's only NON-winged creature: a
galaxy-filled translucent jellyfish bell trailing star-streamer tentacles —
a jellyfish made of deep space. Five genuinely different takes on the same
creature (bell shape, nebula colour scheme, tentacle style, translucency,
halo strength), all on the production 64×84 SRCALPHA contract so the winner
lifts straight into game/animal_skins.py.

Contract (mirrors game/animal_skins.py):

  * `build_<name>(wing_angle_deg) -> pygame.Surface`  draws one flat frame.
  * the bell DOME (body mass) is centred at (32,44) = (BCX,BCY); tentacles
    trail DOWN into the lower canvas. Collision is a fixed 14px circle at the
    body centre, so the bell stays anchored there for fairness.
  * there are NO wings: the 4 base wing poses (`_WING_ANGLES = 50,20,-10,-40`,
    down→up) are reinterpreted as the JELLY PULSE — on the down-pose the bell
    CONTRACTS (squashes wide + short) and tentacles bunch; on the up-pose it
    BILLOWS open (tall + narrow) and tentacles stream long. A slow nebula
    drift rotates the internal swirl/stars across the 4 frames.
  * a cached `(frame_idx, tilt_deg) -> Surface` getter from
    `_make_prebuilt_skin(build_fn)`.

Legendary-spectacle constraint: the skin returns ONE static sprite per frame —
there is no live particle system. The nebula glow, stars and stardust are
BAKED into each of the 4 frames; the pulse + drift are expressed purely by
varying the internal swirl/star positions frame to frame. It must still read
as a glowing bell-with-tentacles at 40px.

North star: "a skin lives or dies at 40px in motion." One bold bell
silhouette + one high-contrast signature feature (the swirling nebula inside
the dome) that survives the downscale against bright-day AND night skies.
"""
import math
import random as _random

import pygame

from game import parrot
from game.parrot import (
    SPRITE_W, SPRITE_H, _WING_ANGLES, _add_outline, _aaellipse,
)


# ── tall-canvas constants ────────────────────────────────────────────────────
COMPOSITE_W = SPRITE_W          # 64
COMPOSITE_H = 84                # headroom; tentacles trail into the lower half
DY          = 12

# Body (bell dome) centre in composite space — the collision anchor.
BCX, BCY = 32, 32 + DY          # → (32, 44)


# ── shared factory (local copy of animal_skins._make_prebuilt_skin) ──────────
def _make_prebuilt_skin(build_fn):
    """Cached `(frame_idx, tilt_deg) -> Surface` getter for a full-body
    build_fn(angle). Lazy 4-frame build + per-(frame, 3°) rotation cache,
    each frame outlined with the house silhouette outline."""
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


# ── tiny shared drawing helpers ──────────────────────────────────────────────
def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _rng(seed):
    """Per-frame deterministic RNG so baked star positions twinkle/drift
    across the 4 frames but stay stable within a frame."""
    return _random.Random(seed)


def _pulse(angle_deg):
    """Map a base wing angle to the jelly PULSE phase, 0..1.

    `_WING_ANGLES` runs 50→-40 (down-pose → up-pose). At 0 the bell is
    CONTRACTED (squashed wide+short, tentacles bunched); at 1 it BILLOWS open
    (tall+narrow, tentacles streaming long). This is the non-winged
    reinterpretation of the flap."""
    return (angle_deg + 40) / 90.0


def _frame_idx(angle_deg):
    """Which of the 4 baked frames this angle is — used to drive the slow
    nebula DRIFT (swirl/star offset) so the cosmos appears to rotate even
    though each sprite is static."""
    return _WING_ANGLES.index(angle_deg) if angle_deg in _WING_ANGLES else 0


def _glow_blob(surf, cx, cy, r, color, layers=4, peak=120):
    """A baked soft radial glow — concentric translucent rings, brightest at
    the core. The legendary halo with no live particle system."""
    for i in range(layers, 0, -1):
        a = int(peak * (i / layers) ** 2)
        rr = int(r * i / layers)
        if rr <= 0:
            continue
        g = pygame.Surface((rr * 2 + 2, rr * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(g, (*color, a), (rr + 1, rr + 1), rr)
        surf.blit(g, (cx - rr - 1, cy - rr - 1),
                  special_flags=pygame.BLEND_RGBA_ADD)


def _star(surf, cx, cy, r, color=(255, 255, 255)):
    """A baked twinkle: bright dot + a faint cross sparkle for the big ones."""
    pygame.draw.circle(surf, color, (cx, cy), r)
    if r >= 2:
        pygame.draw.line(surf, (*color, 150), (cx - r - 1, cy), (cx + r + 1, cy), 1)
        pygame.draw.line(surf, (*color, 150), (cx, cy - r - 1), (cx, cy + r + 1), 1)


def _swirl(surf, cx, cy, rx, ry, phase, colors, arms=2, steps=22):
    """A baked spiral-galaxy swirl inside the bell: `arms` log-spiral arcs of
    fading dots, rotated by `phase` (radians) so successive frames look like
    the nebula slowly turns. Drawn additively so it glows over the void."""
    for arm in range(arms):
        a0 = phase + arm * (2 * math.pi / arms)
        col = colors[arm % len(colors)]
        for s in range(steps):
            t = s / steps
            ang = a0 + t * 3.0                       # ~1.5 turns per arm
            rad = 1.0 + t * 1.0                      # log-ish outward spiral
            x = cx + math.cos(ang) * rx * rad * 0.5
            y = cy + math.sin(ang) * ry * rad * 0.5
            a = int(200 * (1.0 - t))
            dot = max(1, int(2.4 * (1.0 - t * 0.6)))
            g = pygame.Surface((dot * 2 + 2, dot * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(g, (*col, a), (dot + 1, dot + 1), dot)
            surf.blit(g, (int(x) - dot - 1, int(y) - dot - 1),
                      special_flags=pygame.BLEND_RGBA_ADD)


# ── shared palette (the brief's cosmic set) ──────────────────────────────────
VOID     = (26, 10, 51)         # #1A0A33
VIOLET   = (122, 60, 255)       # #7A3CFF
CYAN     = (60, 200, 255)       # #3CC8FF
PINK     = (255, 107, 208)      # #FF6BD0
WHITE    = (255, 255, 255)
GOLD     = (255, 214, 120)
AURORA   = (90, 255, 190)       # mint-green aurora accent
DEEP     = (14, 6, 34)


# ═════════════════════════════════════════════════════════════════════════════
# V1 · CLASSIC DOME — moon-jelly low dome, violet/cyan nebula, a 2-arm spiral
#     galaxy swirling inside, 5 long constellation-dot tentacles. Translucent
#     bell rim catches a cyan light. The textbook "jellyfish made of space."
#     40px tell: the round violet dome with a bright cyan swirl + dotted streamers.
# ═════════════════════════════════════════════════════════════════════════════
def build_cosmic_jelly_v1(wing_angle_deg):
    surf = _new()
    p = _pulse(wing_angle_deg)
    fi = _frame_idx(wing_angle_deg)
    drift = fi * (math.pi / 6)                       # slow nebula rotation

    # Pulse: contracted = wide+short, billowed = tall+narrow.
    rx = int(20 - p * 4)
    ry = int(13 + p * 5)
    rim_y = BCY + ry - 4

    # Outer halo so the legendary glow reads before the bell does.
    _glow_blob(surf, BCX, BCY, 24, VIOLET, layers=5, peak=70)

    # Bell body: void core with a translucent violet shell.
    _aaellipse(surf, (*VIOLET, 130), (BCX, BCY), rx + 1, ry + 1)
    _aaellipse(surf, (*VOID, 235), (BCX, BCY), rx, ry)
    # Bright translucent crown highlight (the gelatinous dome catching light).
    _aaellipse(surf, (*CYAN, 90), (BCX - 3, BCY - ry // 2), rx // 2, ry // 3)

    # Internal nebula: cyan/violet 2-arm spiral, drifting per frame.
    _swirl(surf, BCX, BCY - 1, rx, ry, drift, (CYAN, VIOLET), arms=2)
    # A few baked stars scattered in the dome, jittered by frame for twinkle.
    rng = _rng(fi * 11 + 1)
    for _ in range(7):
        ang = rng.uniform(0, 2 * math.pi)
        d = rng.uniform(0.2, 0.85)
        sx = int(BCX + math.cos(ang) * rx * d)
        sy = int(BCY + math.sin(ang) * ry * d)
        _star(surf, sx, sy, rng.choice([1, 1, 2]),
              rng.choice([WHITE, CYAN, PINK]))

    # Scalloped bell rim (moon-jelly fringe) catching cyan rim-light.
    for i in range(-rx, rx + 1, 4):
        pygame.draw.circle(surf, (*CYAN, 160), (BCX + i, rim_y), 2)

    # 5 long constellation-dot tentacles streaming down; longer when billowed.
    length = int(20 + p * 8)
    for k, tx0 in enumerate((-13, -6, 0, 7, 14)):
        _tentacle_dots(surf, BCX + tx0, rim_y, length, k, fi, p,
                       (WHITE, CYAN, VIOLET))
    return surf


# ═════════════════════════════════════════════════════════════════════════════
# V2 · ONION BULLET — a tall onion/bullet bell (deep-sea siphonophore feel),
#     PINK/GOLD nebula scheme, a dense star-cluster core instead of a spiral,
#     3 thick ribbon tentacles with gold star-nodes. Solid, jewel-like bell.
#     40px tell: the tall pink teardrop dome with a glowing gold heart.
# ═════════════════════════════════════════════════════════════════════════════
def build_cosmic_jelly_v2(wing_angle_deg):
    surf = _new()
    p = _pulse(wing_angle_deg)
    fi = _frame_idx(wing_angle_deg)
    drift = fi * (math.pi / 5)

    # Tall onion bell: narrow + tall when billowed, fatter + shorter contracted.
    rx = int(15 - p * 2)
    ry = int(17 + p * 4)
    top_y = BCY - ry - 3
    rim_y = BCY + ry - 5

    _glow_blob(surf, BCX, BCY, 23, PINK, layers=5, peak=64)

    # Onion silhouette: an ellipse body with a drawn-up pointed crown.
    pts = [(BCX - rx, BCY + 2), (BCX - rx + 1, BCY - ry + 2),
           (BCX - rx // 3, top_y), (BCX, top_y - 2),
           (BCX + rx // 3, top_y), (BCX + rx - 1, BCY - ry + 2),
           (BCX + rx, BCY + 2)]
    pygame.draw.polygon(surf, (*PINK, 150), pts)
    _aaellipse(surf, (*PINK, 150), (BCX, BCY + 2), rx, ry - 6)
    _aaellipse(surf, (*DEEP, 230), (BCX, BCY), rx - 2, ry - 2)
    # Pointed-crown void fill so the onion tip stays dark/translucent.
    pygame.draw.polygon(surf, (*DEEP, 220),
                        [(BCX - rx // 3, top_y + 4), (BCX, top_y),
                         (BCX + rx // 3, top_y + 4), (BCX, BCY)])

    # Dense star-cluster heart (gold), not a spiral.
    _glow_blob(surf, BCX, BCY + 1, 8, GOLD, layers=4, peak=150)
    rng = _rng(fi * 17 + 3)
    for _ in range(12):
        ang = rng.uniform(0, 2 * math.pi) + drift
        d = rng.uniform(0.0, 0.9)
        sx = int(BCX + math.cos(ang) * (rx - 3) * d)
        sy = int(BCY + math.sin(ang) * (ry - 5) * d)
        _star(surf, sx, sy, rng.choice([1, 1, 2]),
              rng.choice([WHITE, GOLD, PINK]))
    # Bright gold core star.
    _star(surf, BCX, BCY + 1, 2, GOLD)

    # Glassy crown highlight.
    _aaellipse(surf, (*WHITE, 80), (BCX - 2, BCY - ry + 4), 3, 5)

    # 3 thick ribbon tentacles with gold star-nodes.
    length = int(22 + p * 8)
    for k, tx0 in enumerate((-8, 0, 8)):
        _tentacle_ribbon(surf, BCX + tx0, rim_y, length, k, fi, p,
                         PINK, GOLD)
    return surf


# ═════════════════════════════════════════════════════════════════════════════
# V3 · MUSHROOM AURORA — a flat, wide mushroom-jelly bell, AURORA scheme
#     (mint-green + cyan + violet), an aurora-band gradient sweeping across the
#     dome instead of a point swirl, MANY (8) fine hair-thin tentacles. The
#     most translucent, "ghostly veil" read. 40px tell: the wide flat cap with
#     a horizontal green-cyan aurora ribbon.
# ═════════════════════════════════════════════════════════════════════════════
def build_cosmic_jelly_v3(wing_angle_deg):
    surf = _new()
    p = _pulse(wing_angle_deg)
    fi = _frame_idx(wing_angle_deg)
    drift = fi * 0.9

    # Flat wide mushroom: very wide + flat contracted, a bit taller billowed.
    rx = int(23 - p * 3)
    ry = int(10 + p * 4)
    rim_y = BCY + ry - 2

    _glow_blob(surf, BCX, BCY, 25, AURORA, layers=5, peak=58)

    # Translucent flat cap (low alpha — ghostly veil).
    _aaellipse(surf, (*AURORA, 70), (BCX, BCY), rx + 1, ry + 1)
    _aaellipse(surf, (*VOID, 170), (BCX, BCY), rx, ry)

    # Aurora band: layered horizontal arcs (green→cyan→violet) sweeping the
    # dome, phase-shifted per frame so the curtain appears to ripple.
    band_cols = (AURORA, CYAN, VIOLET)
    clip = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    for bi, col in enumerate(band_cols):
        yb = BCY - 4 + bi * 4
        pts = []
        for xx in range(BCX - rx, BCX + rx + 1, 2):
            t = (xx - (BCX - rx)) / (2 * rx)
            wob = math.sin(t * math.pi * 2 + drift + bi) * 3
            pts.append((xx, int(yb + wob)))
        if len(pts) >= 2:
            pygame.draw.lines(clip, (*col, 150), False, pts, 3)
    # Mask the band to the dome ellipse so it reads as light INSIDE the jelly.
    mask = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    _aaellipse(mask, (255, 255, 255, 255), (BCX, BCY), rx, ry)
    clip.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(clip, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    # Sparse drifting stars.
    rng = _rng(fi * 23 + 5)
    for _ in range(6):
        ang = rng.uniform(0, 2 * math.pi)
        d = rng.uniform(0.2, 0.9)
        sx = int(BCX + math.cos(ang) * rx * d)
        sy = int(BCY + math.sin(ang) * ry * d)
        _star(surf, sx, sy, rng.choice([1, 1, 2]),
              rng.choice([WHITE, AURORA, CYAN]))

    # Bright rim arc (top crown catching aurora light).
    pygame.draw.arc(surf, (*AURORA, 200),
                    (BCX - rx, BCY - ry, rx * 2, ry * 2),
                    math.radians(20), math.radians(160), 2)

    # 8 fine hair tentacles, very long when billowed — ghostly veil.
    length = int(24 + p * 9)
    spread = list(range(-rx + 3, rx - 2, max(3, (2 * rx - 5) // 7)))
    for k, tx0 in enumerate(spread):
        _tentacle_hair(surf, BCX + tx0, rim_y, length, k, fi, p,
                       (AURORA, CYAN, WHITE))
    return surf


# ═════════════════════════════════════════════════════════════════════════════
# V4 · SOLID VOID-CORE — a near-opaque, bold-silhouette dome (the most
#     gameplay-robust read): deep void body with a HARD bright nebula swirl and
#     a strong violet halo. 6 medium tentacles whose dots form clean
#     constellation lines (joined). The "reads at 40px from a mile" version.
#     40px tell: a solid dark bell with one searing cyan-pink swirl + a thick halo.
# ═════════════════════════════════════════════════════════════════════════════
def build_cosmic_jelly_v4(wing_angle_deg):
    surf = _new()
    p = _pulse(wing_angle_deg)
    fi = _frame_idx(wing_angle_deg)
    drift = fi * (math.pi / 4)

    rx = int(19 - p * 3)
    ry = int(14 + p * 4)
    rim_y = BCY + ry - 4

    # Strong legendary halo — thicker than the others.
    _glow_blob(surf, BCX, BCY, 27, VIOLET, layers=6, peak=95)

    # Near-opaque bell so the silhouette is rock-solid at distance.
    _aaellipse(surf, (*VIOLET, 220), (BCX, BCY), rx + 1, ry + 1)
    _aaellipse(surf, (*VOID, 255), (BCX, BCY), rx, ry)
    # Inner shade ring for volume.
    pygame.draw.arc(surf, (*VIOLET, 180),
                    (BCX - rx, BCY - ry, rx * 2, ry * 2),
                    math.radians(200), math.radians(340), 2)

    # HARD high-contrast swirl: thick 2-arm spiral, bright cyan + pink.
    _swirl(surf, BCX, BCY, rx, ry, drift, (CYAN, PINK), arms=2, steps=26)
    # A searing white core where the arms meet.
    _glow_blob(surf, BCX, BCY, 5, WHITE, layers=3, peak=200)
    _star(surf, BCX, BCY, 2, WHITE)

    # A handful of bright stars on the swirl path.
    rng = _rng(fi * 29 + 7)
    for _ in range(5):
        ang = rng.uniform(0, 2 * math.pi)
        d = rng.uniform(0.4, 0.9)
        sx = int(BCX + math.cos(ang) * rx * d)
        sy = int(BCY + math.sin(ang) * ry * d)
        _star(surf, sx, sy, 2, rng.choice([WHITE, CYAN, PINK]))

    # Glassy crown glint.
    _aaellipse(surf, (*WHITE, 70), (BCX - 4, BCY - ry + 3), 3, 4)

    # 6 medium constellation tentacles — dots JOINED with faint lines so they
    # read as star-lines, not loose dust, even when small.
    length = int(18 + p * 7)
    for k, tx0 in enumerate((-14, -9, -3, 3, 9, 14)):
        _tentacle_constellation(surf, BCX + tx0, rim_y, length, k, fi, p,
                                (CYAN, PINK, WHITE))
    return surf


# ═════════════════════════════════════════════════════════════════════════════
# V5 · CROWN COMET — a domed bell crowned with a bright STAR-DIADEM (3 spike
#     stars breaking the silhouette top) + a full violet/cyan/pink tri-colour
#     nebula, and 4 long comet-tail tentacles that taper to glowing points
#     (stardust trails). The most "spectacle / regal legendary" read.
#     40px tell: the bright star-crown above a tri-colour swirling dome.
# ═════════════════════════════════════════════════════════════════════════════
def build_cosmic_jelly_v5(wing_angle_deg):
    surf = _new()
    p = _pulse(wing_angle_deg)
    fi = _frame_idx(wing_angle_deg)
    drift = fi * (math.pi / 6)

    rx = int(20 - p * 3)
    ry = int(13 + p * 4)
    top_y = BCY - ry
    rim_y = BCY + ry - 4

    _glow_blob(surf, BCX, BCY, 25, VIOLET, layers=5, peak=78)

    # Bell: translucent violet shell, void core.
    _aaellipse(surf, (*VIOLET, 150), (BCX, BCY), rx + 1, ry + 1)
    _aaellipse(surf, (*VOID, 230), (BCX, BCY), rx, ry)

    # Tri-colour nebula: a 3-arm spiral (violet/cyan/pink) for a richer cosmos.
    _swirl(surf, BCX, BCY, rx, ry, drift, (VIOLET, CYAN, PINK),
           arms=3, steps=20)

    # Scattered stars.
    rng = _rng(fi * 31 + 9)
    for _ in range(8):
        ang = rng.uniform(0, 2 * math.pi)
        d = rng.uniform(0.2, 0.85)
        sx = int(BCX + math.cos(ang) * rx * d)
        sy = int(BCY + math.sin(ang) * ry * d)
        _star(surf, sx, sy, rng.choice([1, 1, 2]),
              rng.choice([WHITE, CYAN, PINK, VIOLET]))

    # ── HERO: a STAR-DIADEM crowning the dome — 3 bright spike-stars breaking
    #    the top silhouette, the regal legendary tell. Centre tallest.
    crown = ((BCX - 9, top_y + 1, 7), (BCX, top_y - 5, 10), (BCX + 9, top_y + 1, 7))
    for cx, cy, h in crown:
        # Glow + 4-point sparkle star.
        _glow_blob(surf, cx, cy, 5, GOLD, layers=3, peak=130)
        pygame.draw.polygon(surf, WHITE,
                            [(cx, cy - h // 2), (cx + 2, cy), (cx, cy + h // 2),
                             (cx - 2, cy)])
        pygame.draw.polygon(surf, (*GOLD, 220),
                            [(cx - h // 2, cy), (cx, cy + 2), (cx + h // 2, cy),
                             (cx, cy - 2)])
        pygame.draw.circle(surf, WHITE, (cx, cy), 1)

    # Crown rim-light.
    pygame.draw.arc(surf, (*CYAN, 180),
                    (BCX - rx, BCY - ry, rx * 2, ry * 2),
                    math.radians(20), math.radians(160), 2)

    # 4 long comet-tail tentacles tapering to glowing stardust points.
    length = int(24 + p * 9)
    for k, tx0 in enumerate((-12, -4, 4, 12)):
        _tentacle_comet(surf, BCX + tx0, rim_y, length, k, fi, p,
                        (VIOLET, CYAN, PINK))
    return surf


# ── tentacle styles (one per variant family; all trail DOWN from the rim) ────
def _wave_x(base_x, j, length, k, fi, p):
    """Horizontal offset of a trailing tentacle point at depth fraction `j`
    (0=rim, 1=tip). Tentacles sway with a sine whose phase shifts per frame
    (drift) and whose amplitude grows when the bell BILLOWS (p high) — the
    'trailing stardust on each pulse' read."""
    amp = 1.5 + p * 2.5 + (k % 3)
    phase = fi * 0.8 + k * 1.3
    return base_x + int(math.sin(j * 3.2 + phase) * amp * j)


def _tentacle_dots(surf, x0, y0, length, k, fi, p, cols):
    """V1: a loose string of constellation dots, spaced, fading toward the tip."""
    n = length // 3
    for s in range(n):
        j = s / max(1, n - 1)
        x = _wave_x(x0, j, length, k, fi, p)
        y = y0 + int(j * length)
        a = int(220 * (1 - j * 0.6))
        col = cols[s % len(cols)]
        r = 2 if s % 3 == 0 else 1
        g = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(g, (*col, a), (r + 1, r + 1), r)
        surf.blit(g, (x - r - 1, y - r - 1), special_flags=pygame.BLEND_RGBA_ADD)


def _tentacle_ribbon(surf, x0, y0, length, k, fi, p, edge, node):
    """V2: a thick translucent ribbon with bright star-nodes along it."""
    pts = []
    n = length // 2
    for s in range(n + 1):
        j = s / n
        pts.append((_wave_x(x0, j, length, k, fi, p), y0 + int(j * length)))
    if len(pts) >= 2:
        pygame.draw.lines(surf, (*edge, 120), False, pts, 3)
        pygame.draw.lines(surf, (*edge, 200), False, pts, 1)
    for s in range(0, n + 1, 4):
        x, y = pts[s]
        _star(surf, x, y, 1 if s else 2, node)


def _tentacle_hair(surf, x0, y0, length, k, fi, p, cols):
    """V3: a single fine hair-line with a faint glow + sparse twinkles."""
    pts = []
    n = length // 2
    for s in range(n + 1):
        j = s / n
        pts.append((_wave_x(x0, j, length, k, fi, p), y0 + int(j * length)))
    col = cols[k % len(cols)]
    if len(pts) >= 2:
        pygame.draw.lines(surf, (*col, 110), False, pts, 1)
    for s in range(2, n, 4):
        x, y = pts[s]
        a = int(200 * (1 - s / n))
        g = pygame.Surface((4, 4), pygame.SRCALPHA)
        pygame.draw.circle(g, (*WHITE, a), (2, 2), 1)
        surf.blit(g, (x - 2, y - 2), special_flags=pygame.BLEND_RGBA_ADD)


def _tentacle_constellation(surf, x0, y0, length, k, fi, p, cols):
    """V4: dots JOINED by a faint line so they read as a star-line even small."""
    pts = []
    n = length // 4
    for s in range(n + 1):
        j = s / n
        pts.append((_wave_x(x0, j, length, k, fi, p), y0 + int(j * length)))
    if len(pts) >= 2:
        pygame.draw.lines(surf, (*cols[0], 90), False, pts, 1)
    for s, (x, y) in enumerate(pts):
        col = cols[s % len(cols)]
        r = 2 if s % 2 == 0 else 1
        g = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(g, (*col, 230), (r + 1, r + 1), r)
        surf.blit(g, (x - r - 1, y - r - 1), special_flags=pygame.BLEND_RGBA_ADD)


def _tentacle_comet(surf, x0, y0, length, k, fi, p, cols):
    """V5: a tapering comet tail — a fading glow stripe ending in a bright
    stardust point (the 'stardust trail on each pulse')."""
    pts = []
    n = length // 2
    for s in range(n + 1):
        j = s / n
        pts.append((_wave_x(x0, j, length, k, fi, p), y0 + int(j * length)))
    col = cols[k % len(cols)]
    # Tapering tail: thicker near rim, fading to the tip.
    for s in range(len(pts) - 1):
        j = s / n
        w = max(1, int(3 * (1 - j)))
        a = int(180 * (1 - j * 0.5))
        seg = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
        pygame.draw.line(seg, (*col, a), pts[s], pts[s + 1], w)
        surf.blit(seg, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    # Bright stardust tip.
    tx, ty = pts[-1]
    _glow_blob(surf, tx, ty, 4, col, layers=3, peak=160)
    _star(surf, tx, ty, 2, WHITE)


# ─────────────────────────────────────────────────────────────────────────────
# Candidate registry (label → getter). Each wrapped with the local factory.
# ─────────────────────────────────────────────────────────────────────────────
BUILDERS = {
    "v1_classic_dome":   _make_prebuilt_skin(build_cosmic_jelly_v1),
    "v2_onion_bullet":   _make_prebuilt_skin(build_cosmic_jelly_v2),
    "v3_mushroom_aurora": _make_prebuilt_skin(build_cosmic_jelly_v3),
    "v4_solid_voidcore": _make_prebuilt_skin(build_cosmic_jelly_v4),
    "v5_crown_comet":    _make_prebuilt_skin(build_cosmic_jelly_v5),
}
