"""BLOWFLY BARON (LEGENDARY) — scratch fly-skin candidate, design_1 (R2).

A jewel-metal bottle-fly whose whole identity is the two enormous GARNET
compound eyes crowning the head — they are the biggest, loudest thing on
the sprite and the first read at 40px. Under them sits a fat iridescent
barrel: a vertical chrome ramp (dark-teal belly → bottle-green midriff →
cyan rim-light on the top edge) with a violet oil-slick sheen on the tail,
two teal segment chevrons, and a spongy labellum mouth-pad (NOT a needle).
The broad fan wings are pushed to ~55% alpha and tucked behind the mass so
they frame the body instead of eating the silhouette.

Scratch exploration only — wrapped by animal_skins._make_prebuilt_skin and
exposed as ``build``; NEVER registered in animal_skins.BUILDERS.
"""
import pygame

# WHY inline fallbacks: this scratch builder must render even if run outside
# the package import path (headless tooling), while preferring the real
# shared factory + canvas constants when the game package is importable.
try:
    from game.animal_skins import (
        BCX, BCY, HCX, HCY, _new, _make_prebuilt_skin, _flap, _rot_blit,
    )
    from game.parrot import _aaellipse
except Exception:  # pragma: no cover - direct-run fallback
    from game.parrot import _WING_ANGLES, _add_outline, _aaellipse
    BCX, BCY, HCX, HCY = 32, 44, 44, 34

    def _new():
        return pygame.Surface((64, 84), pygame.SRCALPHA)

    def _flap(angle_deg):
        return (angle_deg + 40) / 90.0

    def _rot_blit(surf, wing, anchor):
        surf.blit(wing, wing.get_rect(center=anchor).topleft)

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


# ── palette ──────────────────────────────────────────────────────────────────
_BASE   = (18, 59, 52)          # #123B34 dark-teal belly / segment seams
_GREEN  = (47, 168, 114)        # #2FA872 bottle-green midtone
_CYAN   = (124, 246, 200)       # #7CF6C8 cyan rim-light + wing edge
_VIOLET = (185, 140, 255)       # #B98CFF violet tail sheen

# Garnet eye radial ramp (dark jewel core → saturated red rim).
_EYE_CORE = (107, 10, 27)       # #6B0A1B
_EYE_MID  = (139, 14, 35)       # #8B0E23
_EYE_RIM  = (194, 29, 58)       # #C21D3A
_EYE_SEAT = (58, 6, 16)         # contour that seats the cabochon

# Spongy labellum: lighter teal pad against the darker barrel.
_LAB   = (120, 196, 168)
_LAB_H = (176, 232, 214)
_LAB_D = (47, 168, 114)

_BODY_RX, _BODY_RY = 15, 14     # plump barrel half-extents (~15% rounder)


def _ramp(stops, t):
    """Linear colour interp across sorted (t, rgb) stops."""
    t = max(0.0, min(1.0, t))
    for i in range(len(stops) - 1):
        t0, c0 = stops[i]
        t1, c1 = stops[i + 1]
        if t <= t1:
            k = 0.0 if t1 == t0 else (t - t0) / (t1 - t0)
            return tuple(int(c0[j] + (c1[j] - c0[j]) * k) for j in range(3))
    return stops[-1][1]


def _barrel_gradient():
    """Vertical metallic ramp masked to the barrel ellipse: cyan rim-light on
    the top edge, bottle-green body, dark-teal belly — plus a violet oil-slick
    bloom on the lower-right tail. The jewel-saturated LEGENDARY read."""
    w, h = _BODY_RX * 2, _BODY_RY * 2
    # Cyan is a thin rim-light, so it collapses to green fast off the top edge.
    stops = [(0.0, _CYAN), (0.12, _GREEN), (0.6, _GREEN), (1.0, _BASE)]
    g = pygame.Surface((w, h), pygame.SRCALPHA)
    for yy in range(h):
        pygame.draw.line(g, _ramp(stops, yy / (h - 1)), (0, yy), (w, yy))

    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.ellipse(mask, (255, 255, 255, 255), (0, 0, w, h))

    # Violet tail sheen, masked to the barrel so it never leaks past the rim.
    vio = pygame.Surface((w, h), pygame.SRCALPHA)
    _aaellipse(vio, (*_VIOLET, 120), (int(w * 0.70), int(h * 0.74)), 9, 7)
    vio.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    g.blit(vio, (0, 0))

    g.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return g


_BARREL = _barrel_gradient()


def build_fly_wing(wing_angle_deg):
    """Broad translucent fan wing, receded behind the mass: ~55% alpha pearl
    membrane, pearlescent CYAN leading edge, exactly three clean thick veins
    (no cross-hatch), far edge tucked inward. Returned pre-rotated."""
    w = pygame.Surface((40, 32), pygame.SRCALPHA)
    memb = (176, 232, 214, 140)                 # ~55% alpha, sky reads through
    _aaellipse(w, memb, (22, 15), 14, 9)        # broad ovate blade
    pygame.draw.polygon(w, memb, [(6, 24), (18, 12), (23, 22)])  # thorax taper
    # Pearlescent cyan leading edge (tucked inward vs. the membrane).
    pygame.draw.ellipse(w, (*_CYAN, 165), (9, 6, 27, 18), 1)
    # Exactly three splayed veins from the wing root.
    for tx, ty in ((32, 10), (34, 16), (29, 23)):
        pygame.draw.line(w, (*_CYAN, 120), (9, 20), (tx, ty), 2)
    return pygame.transform.rotate(w, wing_angle_deg)


def _eye_dome(surf, cx, cy, r):
    """HERO garnet compound eye: radial jewel ramp (dark core → saturated
    #C21D3A rim) + a dark seating contour + a hot-white upper-left specular.
    The single loudest cue — sized to dominate the head at 40px."""
    for rr in range(r, 0, -1):
        pygame.draw.circle(
            surf, _ramp([(0.0, _EYE_CORE), (0.5, _EYE_MID), (1.0, _EYE_RIM)],
                        rr / r), (cx, cy), rr)
    pygame.draw.circle(surf, _EYE_SEAT, (cx, cy), r, 1)
    gx, gy = cx - int(r * 0.42), cy - int(r * 0.42)
    pygame.draw.circle(surf, (255, 255, 255), (gx, gy), 3)
    pygame.draw.circle(surf, (255, 224, 232), (gx + 2, gy + 2), 1)


def build_fly_baron(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)                 # 1 = wings up, 0 = wings down
    up = 18 + f * 34                          # wings sweep higher on the up-beat

    # ── Wings FRAME behind the mass (drawn first): far wing mirrored, near
    #    wing splayed the other way; both subordinate to body + eyes. ──
    far = pygame.transform.flip(build_fly_wing(up), True, False)
    _rot_blit(surf, far, (BCX - 7, BCY - 6))
    _rot_blit(surf, build_fly_wing(up), (BCX + 8, BCY - 6))

    # Faint cyan bloom for night-sky legibility (kept thin so it never
    # thickens the silhouette).
    glow = _new()
    for pad, a in ((3, 30), (1, 66)):
        pygame.draw.ellipse(
            glow, (*_CYAN, a),
            (BCX - _BODY_RX - pad, BCY - _BODY_RY - pad,
             _BODY_RX * 2 + pad * 2, _BODY_RY * 2 + pad * 2), 1)
    surf.blit(glow, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    # Chrome barrel abdomen (vertical metallic ramp + violet tail sheen).
    surf.blit(_BARREL, (BCX - _BODY_RX, BCY - _BODY_RY))
    # Cyan rim-light stroke hugging the top edge to sell the metal.
    pygame.draw.arc(surf, _CYAN,
                    (BCX - _BODY_RX + 2, BCY - _BODY_RY, _BODY_RX * 2 - 4, 14),
                    0.5, 2.64, 2)

    # Two clean darker-teal segment chevrons across the lower barrel.
    for yy in (BCY + 3, BCY + 9):
        pygame.draw.lines(surf, _BASE, False,
                          [(BCX - 10, yy - 2), (BCX, yy + 2),
                           (BCX + 10, yy - 2)], 2)

    # Small green thorax bridge tucked behind the eyes (joins eyes to barrel).
    _aaellipse(surf, _GREEN, (HCX, HCY + 2), 10, 7)

    # ── HERO: two enormous garnet eyes crowning the head, meeting at centre. ──
    _eye_dome(surf, 37, 31, 13)
    _eye_dome(surf, 51, 31, 13)

    # Spongy labellum mouth-pad below the eyes — rounded sponge, grooved, in
    # front of the face so it reads as a pad, never a needle.
    _aaellipse(surf, _LAB, (44, 46), 5, 4)
    _aaellipse(surf, _LAB_H, (44, 45), 4, 3)
    for gx in (42, 44, 46):
        pygame.draw.line(surf, _LAB_D, (gx, 44), (gx, 48), 1)
    return surf


build = _make_prebuilt_skin(build_fly_baron)
