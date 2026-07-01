"""EMBERGLOW — a firefly / lightning-bug take on the ``skin_bee`` redesign.

A dark beetle whose fat lantern abdomen is the hero: it pulses in sync with
the flap so it fires brightest on the down-stroke, the way a real firefly
punches out light on the beat. The read is deliberately two-part — a hard,
dark beetle silhouette carrying a soft glowing lantern — so it never
collapses into a formless glow blob at 40px. The dark charcoal body earns
its own value contrast against the sky; the glow is the tell.

Day sky: the amber lantern against the dark body is the identifier.
Night sky: the bio-green halo makes it unmistakable and lets it own the dark,
while a 1px ember rim on the body keeps the hard silhouette from vanishing
into black — the two-part read only works if the dark body stays visible.

Scratch exploration only — never registered in ``store_skins.BUILDERS``.
"""
import pygame

from game.parrot import _WING_ANGLES, _add_outline, _aaellipse

COMPOSITE_W, COMPOSITE_H = 64, 84
BCX, BCY = 32, 44          # thorax centre
HCX, HCY = 44, 34          # head
CROWN_Y = 24

# EMBERGLOW palette. Charcoal is lifted off pure-black so the beetle reads as
# a solid dark body (not a hole) on a night sky; ember rim-light rescues that
# silhouette against black, amber+warm+hot build the lantern's glow gradient.
CHARCOAL = (34, 28, 30)
EMBER = (122, 46, 18)
AMBER = (255, 176, 32)
CORE_WARM = (255, 246, 200)
CORE_HOT = (255, 255, 255)
BIO_GREEN = (200, 255, 106)
SMOKE = (100, 80, 60, 120)  # translucent buzz-wing brown

# The lantern sits close under the thorax so a short amber neck fuses the two
# into one abdomen — far enough down-left to read as a trailing tail, close
# enough that it never looks like a coin falling away from the beetle.
LANT_CX, LANT_CY = BCX - 7, BCY + 9


def _flap(a):
    return (a + 40) / 90.0


def _strike(a):
    # 1 on the down-stroke (max pulse), 0 at the top of the up-stroke.
    return 1.0 - _flap(a)


def _glow_blit(surf, center, r, color, *, peak=80):
    """Stamp a soft radial glow via additive blending.

    A single SRCALPHA disc is painted as concentric rings — dim at the rim,
    up to ``peak`` alpha at the core — then blitted with BLEND_RGBA_ADD so it
    brightens the sky beneath rather than flatly overpainting it. Additive
    keeps the halo airy instead of a solid coin of colour."""
    d = r * 2 + 2
    g = pygame.Surface((d, d), pygame.SRCALPHA)
    cx = cy = r + 1
    for i in range(r, 0, -1):
        frac = i / r                      # 1 at rim … →0 at core
        a = int(peak * (1.0 - frac) ** 1.4)
        pygame.draw.circle(g, (color[0], color[1], color[2], a), (cx, cy), i)
    surf.blit(g, (int(center[0]) - cx, int(center[1]) - cy),
              special_flags=pygame.BLEND_RGBA_ADD)


def _build_frame(wing_angle_deg):
    surf = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    s = _strike(wing_angle_deg)  # firefly pulse: 1 down-stroke … 0 up-stroke

    # --- Legs: three dark pairs splayed under the thorax, drawn first so the
    # body mass overlaps their roots and they read as under-slung limbs.
    for i, (lx, ly) in enumerate(((-6, 5), (-7, 11), (-6, 17))):
        for side in (-1, 1):
            root = (BCX + side * 5, BCY + ly - 8)
            knee = (BCX + side * (10 + i), BCY + ly - 6)
            foot = (BCX + side * (11 + i), BCY + ly)
            pygame.draw.lines(surf, CHARCOAL, False, [root, knee, foot], 2)

    # --- Hindwings: compact smoky buzz-wings behind the elytra. They spread
    # outward on the down-stroke and tuck back on the up-stroke, so the wing
    # motion carries the flap without ballooning into butterfly sails.
    spread = 5 + int(4 * s)
    for side in (-1, 1):
        wing = pygame.Surface((22, 16), pygame.SRCALPHA)
        _aaellipse(wing, SMOKE, (11, 8), 10, 6)
        wing = pygame.transform.rotate(wing, side * (18 - 30 * s))
        wr = wing.get_rect(center=(BCX + side * spread, BCY + 6))
        surf.blit(wing, wr)

    # --- Glow gradient, painted outermost-in so each layer sits crisp on the
    # last: bio-green halo (the night tell) → amber bloom → then the opaque
    # bulb fills on top. The green only truly reads as green over a dark sky —
    # additive over bright day just warms/brightens, which is the correct
    # behaviour, so it never muddies the amber-on-blue day contrast.
    _glow_blit(surf, (LANT_CX, LANT_CY), 22, BIO_GREEN,
               peak=int(70 + 70 * s))
    _glow_blit(surf, (LANT_CX, LANT_CY), 13, AMBER,
               peak=int(90 + 90 * s))

    # --- Amber neck: a short tapered link fusing the thorax underside to the
    # bulb top, so the lantern reads as an abdomen, not a dropped coin. Drawn
    # under both bulb and thorax so those overlap and swallow its raw ends.
    neck = [
        (BCX - 4, BCY + 6),
        (BCX + 2, BCY + 7),
        (LANT_CX + 2, LANT_CY - 6),
        (LANT_CX - 2, LANT_CY - 6),
    ]
    pygame.draw.polygon(surf, AMBER, neck)

    # --- Lantern bulb: stacked concentric ellipses sharing a centre, amber →
    # warm → white-hot, so it stays a soft round bulb rather than a faceted
    # gem. The warm and hot cores swing wide with the pulse: near-amber on the
    # up-stroke, blazing white on the down-stroke.
    _aaellipse(surf, AMBER, (LANT_CX, LANT_CY), 9, 8)
    _aaellipse(surf, CORE_WARM, (LANT_CX, LANT_CY - 1),
               3 + int(3 * s), 2 + int(3 * s))
    if s > 0.5:
        pygame.draw.circle(surf, CORE_HOT, (LANT_CX, LANT_CY - 1),
                           2 + int(2 * s))

    # Peak flare — an extra bloom that only fires past mid-stroke, so the
    # down-stroke frame visibly flashes brighter than the up-stroke one. This
    # is the heartbeat that has to survive even at 40px.
    flare = int(120 * max(0.0, s - 0.5) * 2)
    if flare > 0:
        _glow_blit(surf, (LANT_CX, LANT_CY), 10, CORE_WARM, peak=flare)

    # --- Spark trail: 2-3 amber embers drifting down-left off the bulb, most
    # and brightest on the peak frame, none on the up-stroke — a sparse,
    # premium ember drip, not a firework.
    for i, (sx, sy) in enumerate(((-5, 10), (-9, 16), (-12, 21))):
        if s <= 0.25 * i:
            continue
        a = int(150 * (1.0 - 0.32 * i) * min(1.0, s * 1.3))
        if a <= 0:
            continue
        dot = pygame.Surface((5, 5), pygame.SRCALPHA)
        pygame.draw.circle(dot, (AMBER[0], AMBER[1], AMBER[2], a), (2, 2), 2)
        surf.blit(dot, (LANT_CX + sx - 2, LANT_CY + sy - 2),
                  special_flags=pygame.BLEND_RGBA_ADD)

    # --- Elytra: short ember-brown wing-covers flanking the thorax. They
    # crack open a touch on the down-stroke (the beetle bracing its buzz).
    open_px = int(3 * s)
    for side in (-1, 1):
        ex = BCX + side * (6 + open_px)
        elytron = [
            (ex - side * 2, BCY - 7),
            (ex + side * 6, BCY - 4),
            (ex + side * 6, BCY + 6),
            (ex + side * 2, BCY + 9),
            (ex - side * 3, BCY + 4),
        ]
        pygame.draw.polygon(surf, EMBER, elytron)

    # --- Pronotal shield: an ember plate bridging head and thorax, the
    # firefly's signature warm collar behind the little dark head.
    shield = [
        (BCX - 3, BCY - 8),
        (HCX - 6, HCY + 5),
        (HCX + 4, HCY + 6),
        (BCX + 8, BCY - 6),
    ]
    pygame.draw.polygon(surf, EMBER, shield)

    # --- Thorax: the charcoal body mass, drawn over shield roots and elytra
    # inner edges so it anchors the whole silhouette as one dark block. An
    # ember ellipse offset up-right sits beneath it, leaving a 1px warm rim on
    # the upper-right edge — the only thing that keeps the dark body from
    # vanishing into a black night sky.
    _aaellipse(surf, EMBER, (BCX + 1, BCY - 1), 9, 8)
    _aaellipse(surf, CHARCOAL, (BCX, BCY), 9, 8)

    # --- Head: small dark ellipse up-forward, with two filiform antennae
    # sweeping up and out — the insect tell that keeps it from reading as a
    # bird head. Drawn last so nothing occludes the antennae.
    for side in (-1, 1):
        base = (HCX + side * 2, HCY - 5)
        mid = (HCX + side * 5, HCY - 11)
        tip = (HCX + side * 9, HCY - 15)
        pygame.draw.lines(surf, CHARCOAL, False, [base, mid, tip], 1)
        pygame.draw.circle(surf, CHARCOAL, tip, 1)
    # Same ember-rim trick as the thorax so the head survives on night sky.
    _aaellipse(surf, EMBER, (HCX + 1, HCY - 1), 7, 6)
    _aaellipse(surf, CHARCOAL, (HCX, HCY), 7, 6)
    # An amber glint on the head so the warm lantern colour echoes up top.
    pygame.draw.circle(surf, AMBER, (HCX + 3, HCY - 1), 2)

    return surf


_state = {"frames": None, "rot": {}}


def build(frame_idx: int, tilt_deg: float) -> pygame.Surface:
    if _state["frames"] is None:
        _state["frames"] = [
            _add_outline(_build_frame(a)) for a in _WING_ANGLES]
    idx = frame_idx % len(_WING_ANGLES)
    key = (idx, round(tilt_deg / 3) * 3)
    rot = _state["rot"].get(key)
    if rot is None:
        rot = pygame.transform.rotozoom(_state["frames"][idx], key[1], 1.0)
        _state["rot"][key] = rot
    return rot
