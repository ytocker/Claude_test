"""SPORE-BURST HOST BODY — zombie-parrot candidate 6 (archetype: cordyceps).

Scratch exploration only; NOT registered in store_skins.BUILDERS, so the live
``skin_zombie`` is untouched. Exposes ``build(frame_idx, tilt_deg) -> Surface``
via store_skins._make_prebuilt_skin, matching the current-skin redraw idiom
(``_build_zombie_redraw``) — a full flat build per wing angle, outlined once.

Read strategy at 40px: the horror is carried by the SILHOUETTE, not by fine
surface detail. Three fat bone-pale mushroom caps ERUPT along the spine ridge —
skull, mid-back, rump — each shoved past the parrot's own contour so the black
cut-out already reads as "something is growing out of this bird". The caps ride
a thin dark stem punched through the skin so they read as breaking the flesh,
not perched like hats. The only saturated accent in the whole sprite is a
luminous cyan-green gill slit under each cap, ranked skull > mid > tail so the
face draws the eye first. Cool teal-grey mycelium spreads FROM those glows so
the veins read as infection, not olive scratches, and a milky clouded dead eye
keeps the face lifeless. Shape + high-chroma glow both survive the downscale
where thin linework would dissolve.
"""
import math
import pygame

from game.store_skins import SPRITE_W, SPRITE_H, _aaellipse, _poly, _make_prebuilt_skin

# Sickly cordyceps-host palette: a desaturated infected olive that has lost all
# healthy parrot chroma, so the only living-looking colour on the bird is the
# fungal glow — exactly the wrong thing to glow, which is what sells the dread.
# Head keeps the lighter olive; the body mass is darkened ~15 units so the head
# reads as a distinct volume instead of merging into one blob.
_HEAD     = (110, 122, 90)         # #6E7A5A lighter head olive (the face mass)
_BODY     = (95, 107, 75)          # #5F6B4B darker body mass, so head pops
_BODY_D   = (55, 62, 44)           # undershadow / internal line
_BODY_H   = (138, 150, 114)        # dry-skin sheen, barely lighter
_BELLY    = (150, 160, 122)        # palest ventral tone
_CAP      = (201, 191, 162)        # #C9BFA2 pale bone-mushroom cap flesh
_CAP_H    = (224, 216, 192)        # cap dome highlight
_CAP_RIM  = (89, 82, 64)           # #595240 darker cap rim / underside / stem
_GLOW     = (140, 242, 208)        # #8CF2D0 spore gill glow — the only hot accent
_VEIN     = (120, 160, 150)        # cool teal-grey mycelium, reads as spread
_WING     = (84, 96, 68)           # wing clearly darker than the lightened body
_WING_D   = (56, 64, 46)
_BEAK     = (176, 162, 118)        # desaturated sickly horn, no fresh yellow


def _spore_wing(angle_deg):
    """A limp, infected wing in the corpse-olive range; kept simple so the flap
    reads as a laboured twitch rather than flight. A dark rim keeps the wing a
    distinct mass over the body, and two mycelium threads creep across it so the
    infection reads even when the wing occludes the back cap."""
    w = pygame.Surface((50, 50), pygame.SRCALPHA)
    pts = [(24, 24), (44, 14), (48, 29), (33, 42), (18, 35)]
    _poly(w, _WING, pts)
    _poly(w, _WING_D, [(24, 24), (33, 42), (18, 35)])
    pygame.draw.polygon(w, _WING_D, pts, 1)       # crisp edge so it never merges
    pygame.draw.line(w, _WING_D, (26, 25), (42, 18), 2)
    pygame.draw.line(w, _BODY_H, (25, 25), (41, 16), 1)
    # Mycelium creep on the wing membrane — two cool threads, not a scribble.
    pygame.draw.line(w, _VEIN, (30, 26), (38, 22), 2)
    pygame.draw.line(w, _VEIN, (29, 32), (35, 36), 2)
    return pygame.transform.rotate(w, angle_deg)


def _veins(surf, cx, cy, spread):
    """Two branching mycelium threads radiating from a cap root toward the
    extremities — the visible spread of infection under the skin. Cool teal-grey
    so they read as creeping out of the cyan gill glow, not olive scratches."""
    for dx, dy in spread:
        ex, ey = cx + dx, cy + dy
        pygame.draw.line(surf, _VEIN, (cx, cy), (ex, ey), 2)
        # A short forked twig off the tip so it branches rather than just spokes.
        pygame.draw.line(surf, _VEIN, (ex, ey),
                         (ex + (2 if dx >= 0 else -2), ey - 2), 1)


def _cap(surf, cx, cy, r, pulse, *, reseat_ry=4, gill_scale=1.0, stem_to=None):
    """One fat mushroom cap ERUPTING off the body.

    Technique: draw a full pale ellipse, clear its bottom half, so only the top
    dome survives as a half-cap sitting ABOVE the caller-chosen contour. A dark
    stem is punched down through the skin first so the cap reads as breaking the
    flesh. A darker rim arc seats the dome as a cap edge (not a bump), and one
    thick luminous gill slit is struck across the underside — the hot accent.

    ``reseat_ry`` fills a shallow wedge of flesh under the cap; the upper caps
    use a small value so the dome clears the body outline and breaks the
    silhouette. ``gill_scale`` ranks the glow (skull brightest, tail dimmed).
    ``pulse`` (0..1, keyed to the flap) makes the spores look like they breathe.
    """
    cx, cy = int(cx), int(cy)
    # Stem first, behind the dome: a 2px neck erupting through the skin so the
    # cap reads as growing OUT of the flesh rather than perched on top of it.
    if stem_to is not None:
        pygame.draw.line(surf, _CAP_RIM, (cx, cy + 1), stem_to, 2)
    # Full dome ellipse (slightly squat so it reads mushroom, not ball).
    dome = pygame.Rect(cx - r, cy - r, r * 2, int(r * 1.8))
    pygame.draw.ellipse(surf, _CAP, dome)
    # Dome highlight — upper-left, so the cap catches the sky.
    pygame.draw.ellipse(surf, _CAP_H,
                        pygame.Rect(cx - r + 1, cy - r + 1, r, r))
    # Clear the bottom half so only the top dome survives as a half-cap.
    bottom = pygame.Rect(cx - r - 1, cy, r * 2 + 2, r + 2)
    surf.fill((0, 0, 0, 0), bottom)
    # Shallow flesh re-seat under the cap so its root looks rooted, not floating;
    # upper caps pass a small ry so the dome still clears the body contour.
    if reseat_ry:
        _aaellipse(surf, _BODY, (cx, cy + 2), r + 1, reseat_ry)
    # Darker cap rim arc (2px) along the dome edge so it reads as a cap lip.
    pygame.draw.arc(surf, _CAP_RIM,
                    (cx - r, cy - r, r * 2, int(r * 1.9)),
                    math.radians(8), math.radians(172), 2)
    # Tight cyan bloom under the cap — width r*2.5 (not r*4) so the slit edge
    # stays crisp when shrunk instead of washing into a fog.
    hw, hh = int(r * 2.5), max(4, int(r * 1.2))
    halo = pygame.Surface((hw, hh), pygame.SRCALPHA)
    a = int((70 + int(28 * pulse)) * gill_scale)
    pygame.draw.ellipse(halo, (140, 242, 208, min(255, a)), (0, 0, hw, hh))
    surf.blit(halo, (cx - hw // 2, cy - 1))
    # The gill slit itself: one short thick luminous line across the underside.
    # Skull (gill_scale 1.0) is widest + 3px; the dimmer caps are thinner.
    gw = max(3, int((r - 1) * (0.55 + 0.5 * gill_scale)))
    lw = 3 if gill_scale >= 1.0 else 2
    pygame.draw.line(surf, _GLOW, (cx - gw, cy + 1), (cx + gw, cy + 1), lw)
    # A brighter core pixel so the glow keeps a hot centre when shrunk; the
    # skull gets the biggest core, the tail the smallest, for clear hierarchy.
    core_r = 2 if gill_scale >= 1.0 else 1
    pygame.draw.circle(surf, (200, 255, 236), (cx, cy + 1), core_r)


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

    # Body — darkened mass so the (lighter) head reads as a distinct volume.
    _aaellipse(surf, _BODY_D, (34, 35), 19, 14)
    _aaellipse(surf, _BODY, (32, 32), 19, 14)
    _aaellipse(surf, _BODY_H, (30, 29), 12, 7)
    _aaellipse(surf, _BELLY, (28, 38), 12, 6)

    # RUMP cap (smallest, r=5) — erupts off the top of the lower back so it
    # breaks the back contour rather than hiding under the belly, veins crawling
    # toward the tail. Drawn before the wing so the wing laps over its root.
    _veins(surf, 15, 23, [(-5, 4), (-2, 8)])
    _cap(surf, 15, 23, 5, pulse, reseat_ry=2, gill_scale=0.7, stem_to=(17, 31))

    # Wing (its dark rim keeps it a separate mass over the lightened body).
    wing = _spore_wing(wing_angle_deg)
    surf.blit(wing, wing.get_rect(center=(34, 28)).topleft)

    # MID-BACK cap (r=6) — bursts up off the spine between the wing shoulder and
    # the neck, pushed high so the dome clears the back silhouette; veins spider
    # down the shoulder.
    _veins(surf, 30, 14, [(-6, 6), (4, 7)])
    _cap(surf, 30, 14, 6, pulse, reseat_ry=2, gill_scale=0.85, stem_to=(31, 26))

    # Head (lighter olive than the body so the face is a clean distinct mass).
    _aaellipse(surf, _BODY_D, (48, 23), 12, 11)
    _aaellipse(surf, _HEAD, (47, 21), 12, 11)
    _aaellipse(surf, _BODY_H, (46, 16), 7, 3)

    # SKULL cap (largest, r=8) — the HERO tell, punched straight up off the top
    # of the crown so the silhouette break is unmistakable at 40px. It skips the
    # body re-seat entirely and rides a stem down into the head; veins fan down
    # the face toward the dead eye, tying the growth to the stare.
    _veins(surf, 48, 8, [(6, 9), (-4, 8)])
    _cap(surf, 48, 8, 8, pulse, reseat_ry=0, gill_scale=1.0, stem_to=(48, 20))

    # Dead cloudy eye: a near-black sunken socket, a cold milky grey-white
    # eyeball, and a tiny fungal-dot pupil floating on the milk — a dead stare,
    # NO glint.
    _aaellipse(surf, (18, 20, 16), (50, 20), 5, 4)          # near-black socket
    pygame.draw.circle(surf, (210, 215, 205), (50, 20), 3)  # milky dead eyeball
    pygame.draw.circle(surf, (60, 120, 100), (50, 20), 1)   # fungal dot pupil

    # Beak — a clean sharp horn wedge, slack and desaturated (no fresh yellow).
    beak_pts = [(54, 20), (62, 25), (54, 27)]
    _poly(surf, _BEAK, beak_pts)
    pygame.draw.polygon(surf, _BODY_D, beak_pts, 1)
    pygame.draw.line(surf, _BODY_D, (54, 25), (60, 25), 1)   # slack mouth line

    # Feet — stubby, curled.
    pygame.draw.line(surf, _BODY_D, (28, 45), (26, 49), 2)
    pygame.draw.line(surf, _BODY_D, (34, 45), (36, 49), 2)
    return surf


build = _make_prebuilt_skin(_build)
