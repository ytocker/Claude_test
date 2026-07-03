"""SPORE-BURST HOST BODY — zombie-parrot candidate 6 (archetype: cordyceps).

Scratch exploration only; NOT registered in store_skins.BUILDERS, so the live
``skin_zombie`` is untouched. Exposes ``build(frame_idx, tilt_deg) -> Surface``
via store_skins._make_prebuilt_skin, matching the current-skin redraw idiom
(``_build_zombie_redraw``) — a full flat build per wing angle, outlined once.

Read strategy at 40px: the horror is carried by the SILHOUETTE, not by fine
surface detail. Three fat bone-pale mushroom caps erupt off the skull, mid-back
and tail base, each protruding PAST the parrot's own contour so the black
cut-out already reads as "something is growing out of this bird". The only
saturated accent in the whole sprite is a luminous cyan-green gill slit under
each cap — three hot dashes that fight the sickly olive body and pop hard when
shrunk. Pale mycelium veins radiate from each cap root to sell the infection
spread, and a single clouded dead eye keeps the face lifeless. Because the tells
are shape + high-chroma glow rather than thin linework, they all survive the
downscale where a subtle texture would dissolve.
"""
import math
import pygame

from game.store_skins import SPRITE_W, SPRITE_H, _aaellipse, _poly, _make_prebuilt_skin

# Sickly cordyceps-host palette: a desaturated infected olive that has lost all
# healthy parrot chroma, so the only living-looking colour on the bird is the
# fungal glow — exactly the wrong thing to glow, which is what sells the dread.
_BODY     = (110, 122, 90)         # #6E7A5A sickly infected olive
_BODY_D   = (59, 66, 48)           # #3B4230 undershadow / internal line
_BODY_H   = (138, 150, 114)        # dry-skin sheen, barely lighter
_BELLY    = (150, 160, 122)        # palest ventral tone
_CAP      = (201, 191, 162)        # #C9BFA2 pale bone-mushroom cap flesh
_CAP_H    = (224, 216, 192)        # cap dome highlight
_CAP_RIM  = (89, 82, 64)           # #59524 0 darker cap rim / underside
_GLOW     = (140, 242, 208)        # #8CF2D0 spore gill glow — the only hot accent
_GLOW_HALO= (140, 242, 208, 70)    # soft bloom around each gill slit
_VEIN     = (169, 181, 140)        # #A9B58C pale grey-green mycelium
_WING     = (96, 108, 78)          # wing a touch darker than the body
_WING_D   = (62, 70, 50)
_BEAK     = (176, 162, 118)        # desaturated sickly horn, no fresh yellow


def _spore_wing(angle_deg):
    """A limp, infected wing in the corpse-olive range; kept simple so the flap
    reads as a laboured twitch rather than flight. A few mycelium threads creep
    across it so the infection reads even when the wing occludes the back cap."""
    w = pygame.Surface((50, 50), pygame.SRCALPHA)
    pts = [(24, 24), (44, 14), (48, 29), (33, 42), (18, 35)]
    _poly(w, _WING, pts)
    _poly(w, _WING_D, [(24, 24), (33, 42), (18, 35)])
    pygame.draw.line(w, _WING_D, (26, 25), (42, 18), 2)
    pygame.draw.line(w, _BODY_H, (25, 25), (41, 16), 1)
    # Mycelium creep on the wing membrane.
    pygame.draw.line(w, _VEIN, (30, 26), (38, 22), 1)
    pygame.draw.line(w, _VEIN, (33, 30), (40, 30), 1)
    pygame.draw.line(w, _VEIN, (28, 32), (34, 36), 1)
    return pygame.transform.rotate(w, angle_deg)


def _veins(surf, cx, cy, spread):
    """Branching mycelium threads radiating from a cap root — the visible spread
    of infection under the skin. ``spread`` is a list of (dx, dy) endpoints so
    each cap can push its veins along the body surface it sits on."""
    for dx, dy in spread:
        ex, ey = cx + dx, cy + dy
        pygame.draw.line(surf, _VEIN, (cx, cy), (ex, ey), 2)
        # A short forked twig off the tip so it branches rather than just spokes.
        pygame.draw.line(surf, _VEIN, (ex, ey),
                         (ex + (2 if dx >= 0 else -2), ey - 2), 1)


def _cap(surf, cx, cy, r, pulse):
    """One fat mushroom cap erupting off the body.

    Technique: draw a full pale ellipse, then overpaint its BOTTOM half with the
    body colour so only the top dome survives as a half-cap. A darker rim arc
    seats the dome so it reads as a cap edge (not a bump), and a single thick
    luminous gill slit is struck across the underside — the hot accent. The cap
    is positioned by the caller so its dome clears the parrot's own contour.

    ``pulse`` (0..1, keyed to the flap) nudges the gill glow brightness so the
    spores look like they breathe.
    """
    cx, cy = int(cx), int(cy)
    # Full dome ellipse (slightly squat so it reads mushroom, not ball).
    dome = pygame.Rect(cx - r, cy - r, r * 2, int(r * 1.8))
    pygame.draw.ellipse(surf, _CAP, dome)
    # Dome highlight — upper-left, so the cap catches the sky.
    pygame.draw.ellipse(surf, _CAP_H,
                        pygame.Rect(cx - r + 1, cy - r + 1, r, r))
    # Overpaint the bottom half back to body colour -> half-dome cap.
    bottom = pygame.Rect(cx - r - 1, cy, r * 2 + 2, r + 2)
    surf.fill((0, 0, 0, 0), bottom)   # clear so a semi-transparent glow can sit
    # Re-seat the body directly under the cap so it looks rooted in the flesh.
    _aaellipse(surf, _BODY, (cx, cy + 3), r + 1, 4)
    # Darker cap rim arc (2px) along the dome edge so it reads as a cap lip.
    pygame.draw.arc(surf, _CAP_RIM,
                    (cx - r, cy - r, r * 2, int(r * 1.9)),
                    math.radians(8), math.radians(172), 2)
    # Soft cyan bloom under the cap, then the hot gill slit over it.
    halo = pygame.Surface((r * 4, r * 2), pygame.SRCALPHA)
    a = 60 + int(30 * pulse)
    pygame.draw.ellipse(halo, (140, 242, 208, a),
                        (0, 0, r * 4, r * 2))
    surf.blit(halo, (cx - r * 2, cy - 1))
    # The gill slit itself: one short thick luminous line across the underside.
    gw = max(4, r - 1)
    pygame.draw.line(surf, _GLOW, (cx - gw, cy + 1), (cx + gw, cy + 1), 3)
    # A brighter core pixel so the glow has a hot centre when shrunk.
    pygame.draw.circle(surf, (200, 255, 236), (cx, cy + 1), 1)


def _build(wing_angle_deg):
    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)

    # Flap phase drives a slow spore "breath" on the gill glow.
    t = (wing_angle_deg + 40) / 90.0                 # 0 (down) .. 1 (up)
    pulse = 0.5 + 0.5 * math.sin(t * math.pi)

    # Tail — short infected-olive wedges.
    for i, c in enumerate([_BODY_D, _BODY, _BODY_H, _BELLY]):
        pts = [(2 + i * 3, 26 + i * 2), (14 + i, 24 + i),
               (20 + i, 30 + i * 2), (6 + i * 3, 36 + i * 2)]
        _poly(surf, c, pts)

    # Body.
    _aaellipse(surf, _BODY_D, (34, 35), 19, 14)
    _aaellipse(surf, _BODY, (32, 32), 19, 14)
    _aaellipse(surf, _BODY_H, (30, 29), 13, 8)
    _aaellipse(surf, _BELLY, (28, 38), 12, 6)

    # TAIL-BASE cap (smallest, r=5) — erupts off the lower-back contour, veins
    # crawling forward into the belly. Drawn before the wing so the wing can lap
    # over its root, keeping it read as growing FROM the body.
    _veins(surf, 18, 40, [(-4, 3), (3, 4), (6, -1)])
    _cap(surf, 17, 39, 5, pulse)

    # Wing.
    wing = _spore_wing(wing_angle_deg)
    surf.blit(wing, wing.get_rect(center=(34, 28)).topleft)

    # MID-BACK cap (r=6) — bursts up off the top-back silhouette between the
    # wing shoulder and the neck, its veins spidering down the shoulder.
    _veins(surf, 30, 20, [(-5, 4), (4, 5), (-2, 7)])
    _cap(surf, 30, 19, 6, pulse)

    # Head.
    _aaellipse(surf, _BODY_D, (48, 23), 12, 11)
    _aaellipse(surf, _BODY, (47, 21), 12, 11)
    _aaellipse(surf, _BODY_H, (46, 16), 7, 3)

    # SKULL cap (largest, r=8) — the hero tell, punching straight up off the top
    # of the head so the crown silhouette is unmistakably broken. Veins fan down
    # the face toward the eye, tying the growth to the dead stare.
    _veins(surf, 48, 12, [(-6, 3), (5, 4), (2, 8)])
    _cap(surf, 48, 11, 8, pulse)

    # Dead cloudy eye: a dark sunken socket with a tiny fungal-dot pupil (two
    # concentric muted grey-green fills) and NO glint — glassy, clouded, gone.
    _aaellipse(surf, _BODY_D, (50, 20), 5, 4)          # sunken socket shadow
    pygame.draw.circle(surf, (40, 46, 34), (50, 20), 4)  # dark clouded eyeball
    pygame.draw.circle(surf, (96, 110, 82), (50, 20), 2)  # milky fungal iris
    pygame.draw.circle(surf, (60, 74, 54), (50, 20), 1)   # dead dot pupil

    # Beak — desaturated sickly horn, slack.
    beak_pts = [(55, 21), (61, 24), (58, 28), (52, 26)]
    _poly(surf, _BEAK, beak_pts)
    pygame.draw.polygon(surf, _BODY_D, beak_pts, 1)
    pygame.draw.line(surf, _BODY_D, (52, 26), (58, 27), 1)   # slack mouth line

    # Feet — stubby, curled.
    pygame.draw.line(surf, _BODY_D, (28, 45), (26, 49), 2)
    pygame.draw.line(surf, _BODY_D, (34, 45), (36, 49), 2)
    return surf


build = _make_prebuilt_skin(_build)
