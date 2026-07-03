"""CELESTIAL PANDA — design_5 (scratch candidate builder, LEGENDARY).

The spectacle / flex build. The panda mask reads exactly the same at 40px —
round ears, two angled eye patches, a nose — but the fur is reskinned as a deep
galaxy and the white belly glows from within like a lantern. The signature that
sells "legendary" at a glance is a pairing the eye can't miss even at gameplay
scale: a floating cyan-white halo arc hovering ABOVE the crown (a clear sky-gap
under it) over a deep galaxy-indigo body rimmed in violet/cyan aurora light.

Readability was the failure mode of the first pass: a pure-black body collapses
to a muddy blob at 40px against both the day and the night sky, and a halo that
hugs the ears just merges into one lump. So the cosmic hue now lives in the mass
itself (deep indigo-violet, not near-black), the silhouette carries a 1px aurora
rim so it pops off the blue, the belly bleeds a cyan bloom past its own edge, and
the halo floats as a separate bright arc with daylight visible beneath it. Only
3–4 deliberate sparkles sit in the negative space — no body speckle noise that
just turns to mud when shrunk.

Geometry follows design_1 / game/animal_skins.py so the fixed collision circle
still lines up: the body mass stays on the base bird's BODY centre, the ears
reach into the tall-canvas headroom, and the halo lives above the crown. The
candidate is rendered in-gameplay by tools/ninja_render.py; nothing here
touches production art.
"""
import math

import pygame

from game.parrot import _WING_ANGLES, _add_outline, _aaellipse

# ── composite + anchors (mirror game/animal_skins.py) ────────────────────────
COMPOSITE_W = 64
COMPOSITE_H = 84
DY = 12
BCX, BCY = 32, 32 + DY          # body centre → (32, 44)
HCX, HCY = 44, 22 + DY          # head centre → (44, 34)
CROWN_Y  = 12 + DY              # top of head → 24

# ── palette ──────────────────────────────────────────────────────────────────
# Body is deep galaxy-INDIGO, not black: at 40px a near-black mass reads as a
# hole against both skies, so the cosmic hue has to live in the fur itself.
GALAXY_INDIGO = (36, 22, 64)        # #241640 deep galaxy-indigo "fur"
GALAXY_NAVY   = (26, 22, 51)        # #1A1633 cooler navy for back/yoke
GALAXY_SHADE  = (18, 14, 38)        # deeper void for shadow pooling
GALAXY_HI     = (74, 56, 120)       # nebular lift catching the top of a mass
GLOW_WHITE    = (245, 245, 245)     # #F5F5F5 glowing belly/face white
WHITE_SOFT    = (224, 230, 240)     # cool white shade
VIOLET        = (138, 96, 240)      # #8A60F0 violet aurora
CYAN          = (110, 232, 255)     # #6EE8FF cyan aurora highlight (rim/bloom)
CYAN_DEEP     = (25, 224, 255)      # saturated cyan for the brightest glints
STAR_CORE     = (255, 243, 196)     # #FFF3C4 warm star / halo core glint
STAR_WHITE    = (255, 255, 255)


def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _rot_blit(surf, wing, anchor):
    surf.blit(wing, wing.get_rect(center=anchor).topleft)


def _radial_glow(radius, color, max_alpha, falloff=1.6):
    """A soft circular glow sprite (alpha falling off toward the edge) used for
    the belly bloom and halo bloom. Frames are prebuilt once so the per-call
    cost is paid only at skin-build time."""
    d = radius * 2
    g = pygame.Surface((d, d), pygame.SRCALPHA)
    for r in range(radius, 0, -1):
        a = int(max_alpha * (1 - r / radius) ** falloff)
        pygame.draw.circle(g, (*color, a), (radius, radius), r)
    return g


def _aurora_rim(surf, pts, top_violet=VIOLET, bot_cyan=CYAN, alpha=200):
    """Trace a 1px violet→cyan aurora rim-light along an ordered edge path so a
    galaxy mass pops off the blue sky as a lit silhouette instead of a flat
    hole. The colour walks violet (upper) → cyan (lower) across the run."""
    n = len(pts)
    for i in range(n - 1):
        t = i / max(1, n - 2)
        col = top_violet if t < 0.5 else bot_cyan
        pygame.draw.line(surf, (*col, alpha), pts[i], pts[i + 1], 1)


def _panda_arm(angle_deg):
    """A galaxy-indigo arm mass wrapping a wing root. Flapping reads as the
    spirit panda raising its arms. A violet→cyan aurora rim along the leading
    edge sells the cosmic skin on the flanks and keeps the limb off the sky."""
    w = pygame.Surface((44, 44), pygame.SRCALPHA)
    pts = [(22, 22), (40, 17), (41, 30), (24, 38), (13, 31)]
    pygame.draw.polygon(w, GALAXY_INDIGO, pts)
    pygame.draw.circle(w, GALAXY_INDIGO, (38, 24), 6)      # rounded paw mitt
    pygame.draw.circle(w, GALAXY_HI, (24, 23), 4)          # faint nebular sheen
    # Aurora rim-light along the lit leading arc of the arm mass.
    _aurora_rim(w, [(15, 31), (18, 24), (24, 20), (32, 18), (40, 18), (42, 24)])
    # Glowing toe-glint on the paw cap.
    pygame.draw.circle(w, (*CYAN_DEEP, 230), (39, 23), 1)
    return pygame.transform.rotate(w, angle_deg)


def build(wing_angle_deg) -> pygame.Surface:
    """Draw one 64×84 SRCALPHA frame of the Celestial Panda (legendary). No
    outline here — the prebuilt getter runs every frame through
    parrot._add_outline."""
    surf = _new()

    # ── aurora tail FUSED to the lower body contour ──
    # A hairline teal→transparent gradient that traces the lower-rear edge of the
    # body with NO gap to the mass (its root sits right on the belly edge), so it
    # extends the silhouette downstream instead of floating as a detached blob.
    # Drawn first → the body/legs overlap its root and it reads as growing out of
    # the fur. Radii shrink fast so it tapers to a thread, never a wing-mass.
    for i in range(8):
        t = i / 7.0
        # Hug the lower contour: start on the belly edge, sweep down-and-back.
        tx = int(BCX - 14 - t * 13)
        ty = int(BCY + 9 + t * 9)
        rad = max(1, int(4 * (1 - t) ** 1.3))
        col = CYAN if t < 0.4 else VIOLET
        pygame.draw.circle(surf, (*col, int(125 * (1 - t) ** 1.2)), (tx, ty), rad)

    # ── two galaxy leg stubs hanging under the body ──
    for lx in (BCX - 8, BCX + 8):
        _aaellipse(surf, GALAXY_INDIGO, (lx, BCY + 15), 5, 7)
        pygame.draw.circle(surf, GALAXY_INDIGO, (lx, BCY + 19), 4)   # rounded foot
        pygame.draw.circle(surf, (*CYAN_DEEP, 210), (lx - 1, BCY + 21), 1)  # toe-glint

    # ── glowing white belly that EMITS light (a lantern, not a patch) ──
    # Light only reads as emission against a DARK surround, so the body mass is
    # darkened in a ring just OUTSIDE the glow first: a deep-void indigo collar
    # framing the belly. The bright cyan bloom then has something to push off of,
    # instead of fading into the mid-indigo body and reading as a flat patch.
    _aaellipse(surf, GALAXY_SHADE, (BCX, BCY + 1), 24, 23)
    _aaellipse(surf, GALAXY_NAVY, (BCX, BCY), 22, 21)
    # An outer cyan bloom bleeds a few px PAST the white disc edge so the belly
    # reads as a light source. The bloom is wider than the disc on purpose.
    belly_bloom = _radial_glow(26, CYAN, 135, falloff=2.0)
    surf.blit(belly_bloom, belly_bloom.get_rect(center=(BCX, BCY)))
    _aaellipse(surf, WHITE_SOFT, (BCX + 1, BCY + 1), 19, 18)
    _aaellipse(surf, GLOW_WHITE, (BCX, BCY), 18, 17)
    # Aurora wash inside the disc: teal low-left rising to violet, translucent so
    # the white still glows. A bright core keeps the centre reading as emitting.
    aur = pygame.Surface((40, 38), pygame.SRCALPHA)
    _aaellipse(aur, (*CYAN, 70), (16, 26), 13, 9)
    _aaellipse(aur, (*VIOLET, 55), (24, 14), 12, 9)
    _aaellipse(aur, (*GLOW_WHITE, 110), (20, 19), 8, 7)
    surf.blit(aur, (BCX - 20, BCY - 19))

    # ── galaxy shoulder yoke wrapping the upper back ──
    yoke = pygame.Surface((52, 26), pygame.SRCALPHA)
    pygame.draw.ellipse(yoke, GALAXY_NAVY, pygame.Rect(0, 0, 52, 26))
    pygame.draw.ellipse(yoke, (0, 0, 0, 0), pygame.Rect(2, 12, 48, 26))
    surf.blit(yoke, (BCX - 26, BCY - 17))
    # Aurora rim catching the crest of the yoke so the back edge pops off sky.
    _aurora_rim(surf, [(BCX - 22, BCY - 6), (BCX - 12, BCY - 13),
                       (BCX, BCY - 16), (BCX + 12, BCY - 13),
                       (BCX + 22, BCY - 6)], alpha=170)

    # ── far arm tucked behind the body ──
    _rot_blit(surf, _panda_arm(wing_angle_deg * 0.5 - 18), (BCX + 9, BCY - 3))

    # ── FLOATING OPEN halo RING above the crown (the legendary flex) ──
    # C2 dealbreaker fix: the old apex-bloom + chunky bar, sitting over the dark
    # head, read as a solid Victorian top-hat cap. The halo is now drawn as a
    # genuinely OPEN ring — only the arc stroke and a bloom that hugs the stroke,
    # so the interior stays fully transparent and the sky shows clean through the
    # centre. A bright crescent (upper arc only) is used because a full 40px ring
    # goes too faint; the float gap to the ears stays clear.
    HALO_CY = CROWN_Y - 13             # arc centre, a clear ~4px sky-gap to ears
    HALO_RX, HALO_RY = 17, 8           # halo radii (wide oval, seen near-on)
    crest_pts = []                     # the visible upper crescent, apex-bright
    for i in range(41):
        t = i / 40.0
        a = math.pi * (0.06 + 0.88 * t)             # upper arc only (open ring)
        hx = HCX + math.cos(a) * HALO_RX
        hy = HALO_CY - math.sin(a) * HALO_RY
        apex = 1.0 - abs(t - 0.5) * 1.05            # brightest at the apex
        crest_pts.append((hx, hy, max(0.0, apex)))
    # Bloom pass: soft cyan glow traced ALONG the stroke only (never a filled
    # disc), so the ring glows but its inside stays open sky.
    for hx, hy, apex in crest_pts:
        if apex <= 0:
            continue
        pygame.draw.circle(surf, (*CYAN, int(70 * apex)), (int(hx), int(hy)), 3)
    for hx, hy, apex in crest_pts:
        if apex <= 0.04:
            continue
        pygame.draw.circle(surf, (*CYAN, int(150 * apex)), (int(hx), int(hy)), 2)
    # Crisp 1–2px bright cyan-white arc core — the actual ring stroke.
    for hx, hy, apex in crest_pts:
        if apex <= 0.04:
            continue
        col = (235, 250, 255, int(235 * apex + 20))
        surf.set_at((int(hx), int(hy)), col)
        if apex > 0.45:                              # thicken just the apex to 2px
            surf.set_at((int(hx), int(hy) + 1), (200, 240, 255, int(180 * apex)))

    # ── round galaxy ears past the crown ──
    # No body speckle here — at 40px it just turns to noise. Each ear carries a
    # nebular highlight + an aurora rim so the shape stays legible.
    for ex in (HCX - 9, HCX + 9):
        _aaellipse(surf, GALAXY_INDIGO, (ex, CROWN_Y + 1), 6, 6)
        pygame.draw.circle(surf, GALAXY_HI, (ex - 1, CROWN_Y - 1), 2)
        pygame.draw.arc(surf, (*CYAN, 210),
                        pygame.Rect(ex - 6, CROWN_Y - 5, 12, 12), 0.4, 2.4, 1)
        pygame.draw.arc(surf, (*VIOLET, 150),
                        pygame.Rect(ex - 6, CROWN_Y - 5, 12, 12), 2.4, 3.4, 1)

    # ── glowing white face disc centred over the head ──
    face_glow = _radial_glow(15, WHITE_SOFT, 70)
    surf.blit(face_glow, face_glow.get_rect(center=(HCX, HCY)))
    _aaellipse(surf, WHITE_SOFT, (HCX + 1, HCY + 1), 13, 13)
    _aaellipse(surf, GLOW_WHITE, (HCX, HCY), 12, 12)

    # ── two galaxy teardrop eye patches, angled down-inward ──
    # Same mask geometry as the classic panda; each patch gets an aurora rim so
    # the legendary read survives the reskin without speckle noise.
    for sgn in (-1, 1):
        patch = pygame.Surface((20, 24), pygame.SRCALPHA)
        _aaellipse(patch, GALAXY_INDIGO, (10, 12), 6, 9)
        pygame.draw.arc(patch, (*VIOLET, 210),
                        pygame.Rect(3, 2, 14, 20), 1.4, 3.6, 1)
        patch = pygame.transform.rotate(patch, sgn * 32)
        pcx = HCX + sgn * 5
        _rot_blit(surf, patch, (pcx, HCY - 1))

    # ── self-lit eyes: glowing cyan points that survive the dark down-flaps ──
    # C2: the face must never vanish in f2/f3, so each eye carries a constant
    # cyan self-glow (a soft halo + a saturated 1px cyan core) on TOP of the
    # white star, anchoring the charming face even when the body sinks dark.
    for sgn in (-1, 1):
        ecx = HCX + sgn * 5
        pygame.draw.circle(surf, (*CYAN, 150), (ecx, HCY), 4)        # outer eye glow
        pygame.draw.circle(surf, (*CYAN_DEEP, 220), (ecx, HCY), 2)   # bright cyan core
        pygame.draw.circle(surf, STAR_WHITE, (ecx, HCY - 1), 2)      # white star core
        surf.set_at((ecx, HCY - 1), STAR_CORE)                       # warm twinkle
        surf.set_at((ecx + sgn, HCY), (*CYAN_DEEP, 255))             # self-lit glint

    # ── little galaxy nose triangle + soft mouth line ──
    nose = [(HCX - 3, HCY + 6), (HCX + 3, HCY + 6), (HCX, HCY + 10)]
    pygame.draw.polygon(surf, GALAXY_INDIGO, nose)
    pygame.draw.circle(surf, (*CYAN_DEEP, 230), (HCX, HCY + 7), 1)  # cool nose glint
    pygame.draw.line(surf, GALAXY_INDIGO, (HCX, HCY + 10), (HCX - 3, HCY + 12), 1)
    pygame.draw.line(surf, GALAXY_INDIGO, (HCX, HCY + 10), (HCX + 3, HCY + 12), 1)

    # ── two soft aurora cheek glows low on the white face ──
    for sgn in (-1, 1):
        blush = pygame.Surface((10, 8), pygame.SRCALPHA)
        _aaellipse(blush, (*VIOLET, 110), (5, 4), 5, 4)
        surf.blit(blush, (HCX + sgn * 9 - 5, HCY + 5 - 4))

    # ── near arm over the body (the flapping panda arm) ──
    _rot_blit(surf, _panda_arm(wing_angle_deg), (BCX - 5, BCY - 1))

    # ── 3 deliberate sparkles in the negative space around crown/halo ──
    # Two value tiers only: these are the brightest marks on the sprite, sat in
    # empty sky around the halo (never on the body, where they'd vanish). Each
    # is a 3×3 cross with a soft bloom so it reads as an intentional twinkle.
    for px, py, col in (
        (HCX - 20, CROWN_Y - 8, CYAN),       # upper-left of halo
        (HCX + 20, CROWN_Y - 4, STAR_CORE),  # upper-right of halo
        (HCX + 13, CROWN_Y + 9, VIOLET),     # lower-right negative space
    ):
        pygame.draw.circle(surf, (*col, 90), (px, py), 3)        # soft bloom
        surf.set_at((px, py), STAR_WHITE)
        for dx, dy in ((-2, 0), (-1, 0), (1, 0), (2, 0),
                       (0, -2), (0, -1), (0, 1), (0, 2)):
            surf.set_at((px + dx, py + dy), (*col, 255))

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
