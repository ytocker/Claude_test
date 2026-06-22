"""SMOKE PHANTOM — Mystic Shadow-Clone Ninja (LEGENDARY showpiece candidate).

Scratch exploration only — NOT wired into store_skins.BUILDERS; the live
skin_ninja stays untouched. Pip mid-teleport: a black shinobi whose lower
body dissolves into a curling violet smoke plume, trailed by two faint
after-image clone silhouettes (the doubled outline is the signature) with a
few shuriken orbiting in the haze and a soft animated eye-slit glow.

The spectacle is keyed off ``wing_angle_deg`` so the smoke breathes, the
clones drift, and the violet rim-light pulses — earning the legendary tier
while the still frame already reads as a wrapped ninja from the eye-slit,
headband and back-blade.
"""
from __future__ import annotations
import math
import pygame

from game import store_skins, parrot
from game.store_skins import HX, HY, CROWN_Y, PARROT_DY, COMPOSITE_W, COMPOSITE_H
from game.parrot import _WING_ANGLES  # noqa: F401
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette


# ── palette ──────────────────────────────────────────────────────────────────
SHADOW   = (12, 13, 20)            # #0C0D14 shinobi body
SHADOW_H = (34, 30, 52)            # faint cloth fold lift so the black isn't flat
SMOKE_D  = (43, 24, 64)            # #2B1840 smoke base
SMOKE_M  = (96, 56, 150)           # mid violet
SMOKE_H  = (185, 140, 255)         # #B98CFF smoke highlight
GLOW     = (123, 63, 228)          # #7B3FE4 violet glow / eye / blade rim
CORE     = (233, 221, 255)         # #E9DDFF hot core glint
STEEL    = (70, 74, 92)            # ninjato blade body (cool, off the violet)
STEEL_H  = (150, 156, 178)


# Black shadow body so Pip reads as a shinobi the instant smoke is stripped.
P_PHANTOM = _pal(
    tail=[(10, 11, 18), (12, 13, 20), (16, 16, 26), (20, 20, 32)],
    tail_line=(6, 6, 12),
    body_shadow=(8, 9, 14), body_main=SHADOW,
    body_chest=(20, 20, 30), body_belly=(16, 16, 26),
    sheen=(150, 120, 220, 70),
    wing_main=(15, 15, 24), wing_dark=(8, 8, 14), wing_tip=(40, 30, 64),
    wing_secondary=None, wing_highlight=(70, 55, 110),
    head_shadow=(8, 9, 14), head_main=SHADOW,
    head_cheek=(22, 20, 34), head_crown=(26, 24, 40),
    lens_frame=(60, 40, 90), lens_body=(8, 8, 14),
    lens_tint=(80, 50, 130, 120), lens_glint=CORE,
    beak_main=(30, 28, 40), beak_dark=(14, 13, 20), beak_gloss=(70, 64, 96),
    foot=(24, 22, 34),
)


def _phantom_base(angle_deg):
    return _build_parrot_with_palette(angle_deg, P_PHANTOM)


def _anim(wing_angle_deg):
    """Map the 4 wing angles (50..-40) to a 0..1 teleport phase so smoke,
    clone offset and glow all advance together across the flap cycle."""
    return (50.0 - wing_angle_deg) / 90.0


def _smoke_lobe(layer, cx, cy, rx, ry, color, alpha):
    """One soft filled smoke puff (a few stacked translucent ellipses give the
    curling, volumetric read instead of a hard blob)."""
    for k, scl in enumerate((1.0, 0.72, 0.46)):
        a = int(alpha * (0.5 + 0.25 * k))
        pygame.draw.ellipse(
            layer, (*color, a),
            (cx - rx * scl, cy - ry * scl, rx * 2 * scl, ry * 2 * scl))


def _shuriken(layer, cx, cy, r, spin, color, alpha):
    """4-point throwing star, spun by `spin` radians, with a hole core."""
    pts = []
    for i in range(8):
        rad = r if i % 2 == 0 else r * 0.36
        a = spin + i * math.pi / 4
        pts.append((cx + rad * math.cos(a), cy + rad * math.sin(a)))
    pygame.draw.polygon(layer, (*color, alpha), pts)
    pygame.draw.circle(layer, (*SHADOW, alpha), (int(cx), int(cy)),
                       max(1, r // 3))


def _paint(surf, wing_angle_deg):
    t = _anim(wing_angle_deg)
    breathe = math.sin(t * math.tau)             # -1..1, drives drift/pulse
    pulse = 0.5 + 0.5 * math.sin(t * math.tau)   # 0..1 glow strength

    # The bird as drawn so far — captured so the smoke/clone layers can sit
    # BEHIND it while we still build through _make_skin's paint hook.
    bird = surf.copy()

    # ── 1 · after-image clone silhouettes (the doubled-outline signature) ──
    # Two ghost copies of the bird, offset back/up-left and tinted violet, the
    # trailing one fainter. Offset and fade swing with the flap so Pip looks
    # mid-teleport rather than just blurred.
    clone_mask = pygame.mask.from_surface(bird, 8)
    for i, (dx, dy, base_a) in enumerate((
            (-7 - int(3 * pulse), -2, 86),
            (-13 - int(5 * pulse), -4, 46))):
        tint = clone_mask.to_surface(
            setcolor=(*GLOW, base_a), unsetcolor=(0, 0, 0, 0))
        # A touch of hot core on the leading clone's edge keeps it from muddying.
        surf.blit(tint, (dx, dy + int(2 * breathe)))

    # ── 2 · smoke plume swallowing the lower body / tail ──────────────────
    smoke = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    drift = int(3 * breathe)
    # Big base cloud under the belly + tail, then lighter curls rising off it.
    _smoke_lobe(smoke, HX - 22, HY + 24, 18, 12, SMOKE_D, 150)
    _smoke_lobe(smoke, HX - 30 + drift, HY + 18, 12, 9, SMOKE_D, 130)
    _smoke_lobe(smoke, HX - 14, HY + 28, 13, 10, SMOKE_M, 120)
    _smoke_lobe(smoke, HX - 26 - drift, HY + 26, 9, 7, SMOKE_M, 110)
    # Rising highlight wisps (the part that pulses brightest).
    wisp_a = int(120 + 80 * pulse)
    _smoke_lobe(smoke, HX - 33 + drift, HY + 9, 6, 7, SMOKE_H, wisp_a)
    _smoke_lobe(smoke, HX - 20, HY + 36, 7, 5, SMOKE_H, wisp_a - 30)
    _smoke_lobe(smoke, HX - 38 - drift, HY + 16, 4, 5, SMOKE_H, wisp_a - 50)
    surf.blit(smoke, (0, 0))

    # ── 3 · violet aura behind the head so the phantom self-illuminates ────
    aura = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    ar = 14 + int(3 * pulse)
    pygame.draw.circle(aura, (*GLOW, int(60 + 40 * pulse)), (HX, HY - 1), ar)
    pygame.draw.circle(aura, (*SMOKE_H, int(35 + 25 * pulse)),
                       (HX, HY - 1), ar - 4)
    surf.blit(aura, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    # Re-stamp the real bird on top of smoke + clones + aura.
    surf.blit(bird, (0, 0))

    # ── 4 · ninjato slung across the back, blade catching a violet rim ─────
    g = STEEL
    # Scabbard/blade bar from below the tail up past the crown.
    pygame.draw.line(surf, (20, 22, 30), (HX - 18, HY + 12),
                     (HX + 6, CROWN_Y - 8), 5)
    pygame.draw.line(surf, g, (HX - 18, HY + 12), (HX + 6, CROWN_Y - 8), 3)
    pygame.draw.line(surf, STEEL_H, (HX - 16, HY + 10),
                     (HX + 5, CROWN_Y - 7), 1)
    # Animated violet rim-light running the blade edge.
    rim = (int(GLOW[0]), int(GLOW[1]), int(min(255, GLOW[2] + 20)))
    pygame.draw.line(surf, rim, (HX - 13, HY + 9),
                     (HX + 5, CROWN_Y - 6), 1)
    # Wrapped handle (tsuka) poking above the crown + a small square guard.
    pygame.draw.line(surf, (16, 16, 24), (HX + 4, CROWN_Y - 5),
                     (HX + 9, CROWN_Y - 12), 4)
    pygame.draw.rect(surf, GLOW, (HX + 1, CROWN_Y - 6, 5, 3))
    for hy in range(CROWN_Y - 12, CROWN_Y - 6, 2):
        pygame.draw.line(surf, SMOKE_H, (HX + 4, hy), (HX + 8, hy - 2), 1)

    # ── 5 · head wrap + headband with the glowing eye-slit (the up-top read) ─
    # Slim black face wrap fold across the lower face.
    store_skins._poly(surf, SHADOW,
                      [(HX - 9, HY + 3), (HX + 13, HY + 1),
                       (HX + 12, HY + 9), (HX - 8, HY + 10)])
    store_skins._poly(surf, SHADOW_H,
                      [(HX - 8, HY + 3), (HX + 6, HY + 2),
                       (HX + 5, HY + 5), (HX - 7, HY + 6)])
    # Eye-slit: dark recess + an animated violet glow bar + hot core glint.
    pygame.draw.rect(surf, (6, 6, 10), (HX - 5, HY - 2, 18, 6),
                     border_radius=3)
    slit_glow = pygame.Surface((24, 12), pygame.SRCALPHA)
    pygame.draw.rect(slit_glow, (*GLOW, int(150 + 90 * pulse)),
                     (3, 3, 18, 6), border_radius=3)
    surf.blit(slit_glow, (HX - 8, HY - 5),
              special_flags=pygame.BLEND_RGBA_ADD)
    pygame.draw.circle(surf, CORE, (HX, HY + 1), 2)
    pygame.draw.circle(surf, CORE, (HX + 8, HY), 2)
    pygame.draw.circle(surf, GLOW, (HX + 4, HY + 1), 1)

    # Headband over the crown with two trailing tails that flick on the flap.
    by = CROWN_Y + 1
    pygame.draw.line(surf, (8, 8, 14), (HX - 12, by + 1), (HX + 12, by - 1), 5)
    pygame.draw.line(surf, SHADOW, (HX - 12, by), (HX + 12, by - 2), 3)
    pygame.draw.line(surf, GLOW, (HX - 10, by - 1), (HX + 6, by - 2), 1)
    flick = int(4 * breathe)
    for off, w in ((0, 3), (4, 2)):
        pygame.draw.line(surf, SHADOW, (HX - 11, by + off),
                         (HX - 24, by + off + 5 + flick), w)
    pygame.draw.line(surf, GLOW, (HX - 12, by + 1),
                     (HX - 22, by + 5 + flick), 1)

    # ── 6 · shuriken orbiting in the smoke (drawn last so they read crisp) ─
    spin = t * math.tau
    orbit = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    for i, (ox, oy, r, ph) in enumerate((
            (HX - 28, HY + 6, 4, 0.0),
            (HX - 20, HY + 34, 3, 2.1),
            (HX - 36, HY + 24, 3, 4.0))):
        wob = 2 * math.sin(t * math.tau + ph)
        a = int(150 + 70 * math.sin(t * math.tau + ph))
        a = max(70, min(220, a))
        _shuriken(orbit, ox + wob, oy - wob, r, spin + ph, STEEL_H, a)
        # Tiny violet glint so the steel reads in the violet haze.
        pygame.draw.circle(orbit, (*CORE, a),
                           (int(ox + wob), int(oy - wob)), 1)
    surf.blit(orbit, (0, 0))


build = store_skins._make_skin(_paint, base_fn=_phantom_base)
