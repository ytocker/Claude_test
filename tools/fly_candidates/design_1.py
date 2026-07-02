"""BLOWFLY BARON (LEGENDARY) — scratch fly-skin candidate, design_1 (R3).

A jewel-metal bottle-fly whose whole identity is the two enormous SCARLET
compound eyes crowning a fat iridescent barrel. The eyes are the loudest,
first read at 40px — their brightest surviving pixel is deliberately hot
crimson so the NEAREST downscale can never let a green rim win the sample.
Under them sits a plump chrome barrel: a vertical metallic ramp (bright
bottle-green body → lifted teal belly → cyan rim-light on the top edge) with
a violet oil-slick sheen on the tail, two teal segment chevrons, and a
single spongy labellum pad (one rounded lobe, warm dark teal — NOT twin
prongs that read as fangs). Broad pearl-cyan fan wings sit behind the mass.

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
# WHY lifted mids: the green→teal barrel and cyan rim both collapse toward
# black under a 40px NEAREST downscale, so the midtone value is pushed ~20%
# so the fat barrel silhouette + metallic identity survive small.
_BASE   = (30, 96, 80)          # #1E6050 lifted teal belly / segment seams
_GREEN  = (77, 200, 138)        # #4DC88A bright bottle-green midtone
_CYAN   = (140, 250, 208)       # #8CFAD0 cyan rim-light + wing edge
_VIOLET = (190, 146, 255)       # #BE92FF violet tail sheen

# Compound eye radial ramp. WHY hot core: the brightest surviving pixel at
# 40px MUST be red, so the whole disc stays saturated crimson (no dark core
# that lets an adjacent green pixel win the NEAREST sample) with a hot
# scarlet centre grading only to a still-red rim for cabochon roundness.
_EYE_CORE = (216, 32, 58)       # #D8203A hot scarlet-crimson centre
_EYE_MID  = (196, 28, 52)       # #C41C34
_EYE_RIM  = (162, 22, 44)       # #A2162C still unmistakably red at the edge
_EYE_SEAT = (86, 10, 24)        # deep-red seating contour (never green)

# Spongy labellum: ONE rounded lobe in warm dark teal so it reads as a soft
# pad, never white fangs/teeth.
_LAB   = (58, 96, 88)           # #3A6058
_LAB_H = (86, 132, 120)         # subtle warm top sheen (not white)
_LAB_D = (34, 62, 56)           # under-shadow groove

_BODY_RX, _BODY_RY = 16, 16     # plump barrel half-extents — as massive as
                                # the two-eye cluster, so eyes crown a fat body


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
    the top edge, bright bottle-green body, lifted teal belly — plus a violet
    oil-slick bloom on the lower-right tail. The jewel-saturated LEGENDARY
    read, tuned so the fat barrel never sinks to black at 40px."""
    w, h = _BODY_RX * 2, _BODY_RY * 2
    # Cyan is a thin rim-light; the body holds green far down before the belly.
    stops = [(0.0, _CYAN), (0.14, _GREEN), (0.66, _GREEN), (1.0, _BASE)]
    g = pygame.Surface((w, h), pygame.SRCALPHA)
    for yy in range(h):
        pygame.draw.line(g, _ramp(stops, yy / (h - 1)), (0, yy), (w, yy))

    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.ellipse(mask, (255, 255, 255, 255), (0, 0, w, h))

    # Violet tail sheen, masked to the barrel so it never leaks past the rim.
    vio = pygame.Surface((w, h), pygame.SRCALPHA)
    _aaellipse(vio, (*_VIOLET, 120), (int(w * 0.70), int(h * 0.74)), 10, 8)
    vio.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    g.blit(vio, (0, 0))

    g.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return g


_BARREL = _barrel_gradient()


def build_fly_wing(wing_angle_deg):
    """Broad translucent fan wing sitting behind the mass: pearl membrane with
    a THICK bright pearlescent-cyan leading edge so the stubby fanned wing
    still reads behind the eyes at 40px, plus three clean splayed veins.
    Returned pre-rotated."""
    w = pygame.Surface((40, 32), pygame.SRCALPHA)
    memb = (188, 240, 222, 172)                 # brighter/denser so it survives
    _aaellipse(w, memb, (22, 15), 14, 9)        # broad ovate blade
    pygame.draw.polygon(w, memb, [(6, 24), (18, 12), (23, 22)])  # thorax taper
    # THICK pearlescent cyan leading edge — the cue that keeps the wing legible.
    pygame.draw.ellipse(w, (*_CYAN, 235), (9, 6, 27, 18), 2)
    # Exactly three splayed veins from the wing root.
    for tx, ty in ((32, 10), (34, 16), (29, 23)):
        pygame.draw.line(w, (*_CYAN, 165), (9, 20), (tx, ty), 2)
    return pygame.transform.rotate(w, wing_angle_deg)


def _eye_dome(surf, cx, cy, r):
    """HERO compound eye: a fully saturated crimson cabochon (hot scarlet
    centre → still-red rim) seated by a deep-red contour, with a SMALL warm
    specular so the red always wins the 40px NEAREST sample. No green anywhere
    on the disc."""
    for rr in range(r, 0, -1):
        pygame.draw.circle(
            surf, _ramp([(0.0, _EYE_CORE), (0.55, _EYE_MID), (1.0, _EYE_RIM)],
                        rr / r), (cx, cy), rr)
    pygame.draw.circle(surf, _EYE_SEAT, (cx, cy), r, 1)
    # Tiny warm specular — small enough not to crowd the red at 40px.
    gx, gy = cx - int(r * 0.40), cy - int(r * 0.40)
    pygame.draw.circle(surf, (255, 236, 240), (gx, gy), 2)


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
                    (BCX - _BODY_RX + 2, BCY - _BODY_RY, _BODY_RX * 2 - 4, 15),
                    0.5, 2.64, 2)

    # Two clean darker-teal segment chevrons across the lower barrel.
    for yy in (BCY + 4, BCY + 10):
        pygame.draw.lines(surf, _BASE, False,
                          [(BCX - 11, yy - 2), (BCX, yy + 2),
                           (BCX + 11, yy - 2)], 2)

    # Small green thorax bridge tucked BEHIND + below the eyes (joins the eye
    # cluster to the barrel). Kept low and matched to the barrel green so no
    # stray green ring pokes out around the crimson eyes at 40px.
    _aaellipse(surf, _GREEN, (HCX, HCY + 5), 9, 6)

    # ── HERO: two enormous crimson eyes crowning the head, meeting at centre. ──
    _eye_dome(surf, 37, 31, 13)
    _eye_dome(surf, 51, 31, 13)

    # Spongy labellum mouth-pad below the eyes — a SINGLE rounded warm-teal
    # lobe (one soft pad, no twin prongs) so it never reads as fangs/teeth.
    _aaellipse(surf, _LAB_D, (44, 47), 6, 4)      # under-shadow seats the pad
    _aaellipse(surf, _LAB, (44, 46), 5, 4)        # the single sponge lobe
    _aaellipse(surf, _LAB_H, (44, 45), 3, 2)      # subtle warm sheen (not white)
    return surf


build = _make_prebuilt_skin(build_fly_baron)
