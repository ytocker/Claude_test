"""CELESTIAL PANDA — design_5 (scratch candidate builder, LEGENDARY).

The spectacle / flex build. The panda mask reads exactly the same at 40px —
round ears, two angled eye patches, a nose — but the black fur is reskinned as
a deep galaxy speckled with stars, the white belly glows with an aurora wash,
and a luminous halo arcs above the crown. The signature that sells "legendary"
at a glance is the pairing the eye can't miss: starfield-black mask + glowing
halo. Everything else (aurora rim-light on the arms, comet wisp off the tail,
free-floating sparkles) is supporting glow that reads as an aura, not as props
competing with the mask.

Geometry follows design_1 / game/animal_skins.py so the fixed collision circle
still lines up: the body mass stays on the base bird's BODY centre, the ears
reach into the tall-canvas headroom, and the halo lives above the crown. The
candidate is rendered in-gameplay by tools/ninja_render.py; nothing here
touches production art.
"""
import math
import random

import pygame

from game import parrot
from game.parrot import SPRITE_W, _WING_ANGLES, _add_outline, _aaellipse

# ── composite + anchors (mirror game/animal_skins.py) ────────────────────────
COMPOSITE_W = 64
COMPOSITE_H = 84
DY = 12
BCX, BCY = 32, 32 + DY          # body centre → (32, 44)
HCX, HCY = 44, 22 + DY          # head centre → (44, 34)
CROWN_Y  = 12 + DY              # top of head → 24

# ── palette ──────────────────────────────────────────────────────────────────
GALAXY_BLACK  = (13, 13, 26)        # #0D0D1A deep indigo-black "fur"
GALAXY_SHADE  = (8, 8, 18)          # slightly deeper void for shadow pooling
GALAXY_HI     = (34, 30, 60)        # faint nebular lift on top of the black
GLOW_WHITE    = (245, 245, 245)     # #F5F5F5 glowing belly white
WHITE_SOFT    = (224, 230, 240)     # cool white shade
VIOLET        = (123, 63, 228)      # #7B3FE4 violet aurora
CYAN          = (25, 224, 255)      # #19E0FF cyan aurora highlight
STAR_CORE     = (255, 243, 196)     # #FFF3C4 warm star / halo core glint
STAR_WHITE    = (255, 255, 255)


def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _rot_blit(surf, wing, anchor):
    surf.blit(wing, wing.get_rect(center=anchor).topleft)


def _starfield(surf, center, rx, ry, seed, n=7):
    """Sprinkle tiny stars inside an elliptical mask of black fur. A fixed seed
    keeps the constellation stable across the 4 wing frames so the speckle does
    not shimmer distractingly while flapping."""
    cx, cy = center
    rng = random.Random(seed)
    for _ in range(n):
        # Rejection-sample to the ellipse interior so stars hug the fur shape.
        ang = rng.uniform(0, math.tau)
        rad = math.sqrt(rng.random())
        sx = int(cx + math.cos(ang) * rad * (rx - 1))
        sy = int(cy + math.sin(ang) * rad * (ry - 1))
        warm = rng.random() < 0.35
        col = STAR_CORE if warm else STAR_WHITE
        if rng.random() < 0.45:
            surf.set_at((sx, sy), col)
        else:
            pygame.draw.circle(surf, col, (sx, sy), 1)


def _aurora_rim(surf, center, rx, ry, top=True):
    """Trace a violet→cyan rim-light along the upper edge of a galaxy mass so
    the black reads as a glowing celestial body, not a flat hole. Drawn as a
    thin double-stroke arc instead of a full outline to keep the lit edge."""
    cx, cy = center
    steps = 22
    start, end = (math.pi, math.tau) if top else (0.0, math.pi)
    for i in range(steps):
        t = i / (steps - 1)
        a = start + (end - start) * t
        px = cx + math.cos(a) * rx
        py = cy + math.sin(a) * ry
        col = VIOLET if t < 0.5 else CYAN
        pygame.draw.circle(surf, (*col, 150), (int(px), int(py)), 1)


def _panda_arm(angle_deg):
    """A galaxy-black arm mass wrapping a wing root. Flapping reads as the
    spirit panda raising its arms. Star-flecked fur + a violet/cyan aurora
    rim-light along the leading edge sells the cosmic skin on the flanks."""
    w = pygame.Surface((44, 44), pygame.SRCALPHA)
    pts = [(22, 22), (40, 17), (41, 30), (24, 38), (13, 31)]
    pygame.draw.polygon(w, GALAXY_BLACK, pts)
    pygame.draw.circle(w, GALAXY_BLACK, (38, 24), 6)        # rounded paw mitt
    pygame.draw.circle(w, GALAXY_HI, (24, 23), 4)           # faint nebular sheen
    # Aurora rim-light along the top arc of the arm mass.
    pygame.draw.line(w, (*VIOLET, 170), (15, 30), (24, 21), 1)
    pygame.draw.line(w, (*CYAN, 170), (24, 21), (39, 19), 1)
    _starfield(w, (28, 26), 13, 9, seed=int(angle_deg) * 17 + 3, n=5)
    # Glowing toe-glints on the paw cap.
    pygame.draw.circle(w, (*CYAN, 220), (39, 23), 1)
    return pygame.transform.rotate(w, angle_deg)


def _radial_glow(radius, color, max_alpha):
    """A soft circular glow sprite (alpha falling off toward the edge) used for
    the belly aurora and halo bloom. Cached implicitly per call site is cheap
    enough since frames are prebuilt once."""
    d = radius * 2
    g = pygame.Surface((d, d), pygame.SRCALPHA)
    for r in range(radius, 0, -1):
        a = int(max_alpha * (1 - r / radius) ** 1.6)
        pygame.draw.circle(g, (*color, a), (radius, radius), r)
    return g


def build(wing_angle_deg) -> pygame.Surface:
    """Draw one 64×84 SRCALPHA frame of the Celestial Panda (legendary). No
    outline here — the prebuilt getter runs every frame through
    parrot._add_outline."""
    surf = _new()

    # ── trailing comet / aurora wisp off the lower body ──
    # A cyan→violet streak fading downstream so the panda looks like it is
    # gliding through the cosmos. Drawn first so the body overlaps its root.
    wisp = pygame.Surface((40, 22), pygame.SRCALPHA)
    for i in range(8):
        t = i / 7.0
        wx = int(4 + t * 30)
        wy = int(6 + t * 10)
        rad = max(1, int(7 * (1 - t)))
        a = int(150 * (1 - t))
        col = CYAN if t < 0.5 else VIOLET
        pygame.draw.circle(wisp, (*col, a), (wx, wy), rad)
    surf.blit(wisp, (BCX - 30, BCY + 6))

    # ── two galaxy leg stubs hanging under the body ──
    for lx in (BCX - 8, BCX + 8):
        _aaellipse(surf, GALAXY_BLACK, (lx, BCY + 15), 5, 7)
        pygame.draw.circle(surf, GALAXY_BLACK, (lx, BCY + 19), 4)   # rounded foot
        pygame.draw.circle(surf, (*CYAN, 200), (lx - 1, BCY + 21), 1)  # toe-glint

    # ── glowing white belly with an aurora wash ──
    # A radial teal→violet bloom under the white disc makes the belly read as
    # lit-from-within rather than flat paint.
    bloom = _radial_glow(20, CYAN, 110)
    surf.blit(bloom, bloom.get_rect(center=(BCX, BCY)))
    _aaellipse(surf, WHITE_SOFT, (BCX + 1, BCY + 1), 19, 18)
    _aaellipse(surf, GLOW_WHITE, (BCX, BCY), 18, 17)
    # Aurora gradient washing across the belly: concentric tinted ellipses,
    # teal low-left rising to violet, kept translucent so the white still glows.
    aur = pygame.Surface((40, 38), pygame.SRCALPHA)
    _aaellipse(aur, (*CYAN, 70), (16, 26), 13, 9)
    _aaellipse(aur, (*VIOLET, 55), (24, 14), 12, 9)
    _aaellipse(aur, (*GLOW_WHITE, 90), (20, 19), 8, 7)
    surf.blit(aur, (BCX - 20, BCY - 19))

    # ── galaxy shoulder yoke wrapping the upper back ──
    yoke = pygame.Surface((52, 26), pygame.SRCALPHA)
    pygame.draw.ellipse(yoke, GALAXY_BLACK, pygame.Rect(0, 0, 52, 26))
    pygame.draw.ellipse(yoke, (0, 0, 0, 0), pygame.Rect(2, 12, 48, 26))
    _starfield(yoke, (26, 9), 23, 8, seed=91, n=8)
    surf.blit(yoke, (BCX - 26, BCY - 17))

    # ── far arm tucked behind the body ──
    _rot_blit(surf, _panda_arm(wing_angle_deg * 0.5 - 18), (BCX + 9, BCY - 3))

    # ── glowing halo arc above the crown (the legendary flex) ──
    # A bloom + a violet→cyan ring of orbiting star particles arcing over the
    # ears. Drawn before the ears/face so the ears sit in front of it and the
    # halo reads as floating behind-and-above the head.
    halo_glow = _radial_glow(16, STAR_CORE, 90)
    surf.blit(halo_glow, halo_glow.get_rect(center=(HCX, CROWN_Y - 8)))
    for i in range(14):
        t = i / 13.0
        a = math.pi * (0.12 + 0.76 * t)          # upper arc only
        hx = HCX + math.cos(a) * 16
        hy = (CROWN_Y - 6) - math.sin(a) * 7
        col = VIOLET if t < 0.5 else CYAN
        pygame.draw.circle(surf, (*col, 220), (int(hx), int(hy)), 1)
    # A few brighter orbiting star particles riding the halo ring.
    for frac, col in ((0.18, CYAN), (0.5, STAR_CORE), (0.82, VIOLET)):
        a = math.pi * (0.12 + 0.76 * frac)
        hx = HCX + math.cos(a) * 16
        hy = (CROWN_Y - 6) - math.sin(a) * 7
        pygame.draw.circle(surf, (*col, 120), (int(hx), int(hy)), 2)
        surf.set_at((int(hx), int(hy)), STAR_WHITE)

    # ── round galaxy ears past the crown, star-flecked ──
    for ex in (HCX - 9, HCX + 9):
        _aaellipse(surf, GALAXY_BLACK, (ex, CROWN_Y + 1), 6, 6)
        pygame.draw.circle(surf, GALAXY_HI, (ex - 1, CROWN_Y - 1), 2)
        _starfield(surf, (ex, CROWN_Y + 1), 5, 5, seed=ex * 7, n=4)
        # Aurora rim-light catching the top of each ear.
        pygame.draw.arc(surf, (*CYAN, 200),
                        pygame.Rect(ex - 6, CROWN_Y - 5, 12, 12),
                        0.4, 2.2, 1)

    # ── glowing white face disc centred over the head ──
    face_glow = _radial_glow(15, WHITE_SOFT, 70)
    surf.blit(face_glow, face_glow.get_rect(center=(HCX, HCY)))
    _aaellipse(surf, WHITE_SOFT, (HCX + 1, HCY + 1), 13, 13)
    _aaellipse(surf, GLOW_WHITE, (HCX, HCY), 12, 12)

    # ── two galaxy teardrop eye patches, angled down-inward ──
    # Same mask geometry as the classic panda, but each patch gets an aurora
    # rim-glow so the legendary read survives the reskin.
    for sgn in (-1, 1):
        patch = pygame.Surface((20, 24), pygame.SRCALPHA)
        _aaellipse(patch, GALAXY_BLACK, (10, 12), 6, 9)
        _starfield(patch, (10, 12), 5, 8, seed=200 + sgn, n=4)
        # Violet/cyan rim along the outer edge of the patch.
        pygame.draw.arc(patch, (*VIOLET, 200),
                        pygame.Rect(3, 2, 14, 20), 1.4, 3.6, 1)
        patch = pygame.transform.rotate(patch, sgn * 32)
        pcx = HCX + sgn * 5
        _rot_blit(surf, patch, (pcx, HCY - 1))

    # ── eyes that read as bright stars / glowing points ──
    for sgn in (-1, 1):
        ecx = HCX + sgn * 5
        pygame.draw.circle(surf, (*CYAN, 120), (ecx, HCY), 3)   # halo around eye
        pygame.draw.circle(surf, STAR_WHITE, (ecx, HCY - 1), 2) # bright star core
        surf.set_at((ecx, HCY - 1), STAR_CORE)                  # warm twinkle

    # ── little galaxy nose triangle + soft mouth line ──
    nose = [(HCX - 3, HCY + 6), (HCX + 3, HCY + 6), (HCX, HCY + 10)]
    pygame.draw.polygon(surf, GALAXY_BLACK, nose)
    pygame.draw.circle(surf, (*CYAN, 220), (HCX, HCY + 7), 1)   # cool nose glint
    pygame.draw.line(surf, GALAXY_BLACK, (HCX, HCY + 10), (HCX - 3, HCY + 12), 1)
    pygame.draw.line(surf, GALAXY_BLACK, (HCX, HCY + 10), (HCX + 3, HCY + 12), 1)

    # ── two soft aurora cheek glows low on the white face ──
    for sgn in (-1, 1):
        blush = pygame.Surface((10, 8), pygame.SRCALPHA)
        _aaellipse(blush, (*VIOLET, 110), (5, 4), 5, 4)
        surf.blit(blush, (HCX + sgn * 9 - 5, HCY + 5 - 4))

    # ── near arm over the body (the flapping panda arm) ──
    _rot_blit(surf, _panda_arm(wing_angle_deg), (BCX - 5, BCY - 1))

    # ── free-floating sparkle particles around the body (the aura) ──
    for px, py, col, rad in (
        (BCX - 18, BCY - 14, CYAN, 1),
        (BCX + 20, BCY + 4, VIOLET, 1),
        (BCX + 14, BCY - 18, STAR_CORE, 1),
        (BCX - 22, BCY + 10, STAR_WHITE, 1),
    ):
        pygame.draw.circle(surf, (*col, 90), (px, py), rad + 2)   # soft bloom
        # 4-point sparkle so it reads as a twinkling star, not a dot.
        surf.set_at((px, py), STAR_WHITE)
        for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
            surf.set_at((px + dx, py + dy), col)

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


get_skin = _make_prebuilt_skin(build)
