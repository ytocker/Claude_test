"""SMOKE PHANTOM — Mystic Shadow-Clone Ninja (LEGENDARY showpiece candidate).

Scratch exploration only — NOT wired into store_skins.BUILDERS; the live
skin_ninja stays untouched. Pip mid-teleport: a hard-edged black shinobi whose
upper head/body stays a crisp silhouette against the day sky while ONLY the
tail/lower body dissolves into a curling violet smoke plume. He is trailed by a
single deliberate violet-tinted shadow-clone (the doubled-outline signature),
wears a single glowing horizontal eye-slit, and carries a steel ninjato slung
across the back with its hilt-knob poking above the crown.

The spectacle is keyed off ``wing_angle_deg`` so the smoke breathes, the clone
drifts and the violet rim pulses — earning the legendary tier — but the read is
carried by the cool-steel blade + black silhouette so it survives even with the
violet desaturated. Order of read at 40px: masked figure → glowing slit eye →
sword on the back → dissolving into smoke.
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
STEEL    = (74, 80, 100)           # ninjato blade body (cool, off the violet)
STEEL_H  = (185, 192, 214)         # bright steel edge so the blade reads at 40px

# Smoke must never climb above this y so the head/upper body stays hard-edged
# shinobi-black against the bright day sky (the "it's a ninja, not a blob" line).
SMOKE_CAP_Y = HY + 14


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
        rad = r if i % 2 == 0 else r * 0.40
        a = spin + i * math.pi / 4
        pts.append((cx + rad * math.cos(a), cy + rad * math.sin(a)))
    pygame.draw.polygon(layer, (*color, alpha), pts)
    pygame.draw.circle(layer, (*SHADOW, alpha), (int(cx), int(cy)),
                       max(1, r // 3))


def _paint(surf, wing_angle_deg):
    t = _anim(wing_angle_deg)
    breathe = math.sin(t * math.tau)             # -1..1, drives drift/pulse
    pulse = 0.5 + 0.5 * math.sin(t * math.tau)   # 0..1 glow strength

    # The bird as drawn so far — captured so the smoke/clone/aura layers can sit
    # BEHIND it while we still build through _make_skin's paint hook.
    bird = surf.copy()

    # ── 1 · single shadow-clone silhouette (the doubled-outline signature) ──
    # One deliberate after-image offset back/up-left and tinted violet (NOT grey)
    # so it reads as a teleport double at gameplay scale, not a smudge. Offset
    # and fade swing with the flap so Pip looks mid-step rather than just blurred.
    clone_mask = pygame.mask.from_surface(bird, 8)
    cdx = -15 - int(3 * pulse)
    cdy = -4 + int(2 * breathe)
    clone = clone_mask.to_surface(
        setcolor=(*GLOW, 58), unsetcolor=(0, 0, 0, 0))
    surf.blit(clone, (cdx, cdy))

    # ── 2 · smoke plume swallowing ONLY the lower body / tail ──────────────
    # Every lobe centre sits at/below SMOKE_CAP_Y, and a hard cut clears any
    # alpha that creeps above it, so the upper silhouette stays crisp black.
    smoke = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    drift = int(3 * breathe)
    _smoke_lobe(smoke, HX - 22, HY + 26, 18, 11, SMOKE_D, 155)
    _smoke_lobe(smoke, HX - 32 + drift, HY + 22, 12, 9, SMOKE_D, 135)
    _smoke_lobe(smoke, HX - 14, HY + 30, 13, 9, SMOKE_M, 125)
    _smoke_lobe(smoke, HX - 28 - drift, HY + 28, 9, 7, SMOKE_M, 115)
    # Rising highlight wisps (the part that pulses brightest) — kept low so they
    # curl off the tail, not over the head.
    wisp_a = int(120 + 80 * pulse)
    _smoke_lobe(smoke, HX - 34 + drift, HY + 16, 6, 6, SMOKE_H, wisp_a)
    _smoke_lobe(smoke, HX - 20, HY + 38, 7, 5, SMOKE_H, wisp_a - 30)
    _smoke_lobe(smoke, HX - 39 - drift, HY + 22, 4, 5, SMOKE_H, wisp_a - 50)
    # Hard cap: zero the alpha above SMOKE_CAP_Y so the head never goes hazy.
    smoke.fill((0, 0, 0, 0), (0, 0, COMPOSITE_W, SMOKE_CAP_Y),
               special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(smoke, (0, 0))

    # ── 3 · violet aura behind the head so the phantom self-illuminates ────
    aura = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    ar = 13 + int(3 * pulse)
    pygame.draw.circle(aura, (*GLOW, int(55 + 35 * pulse)), (HX, HY - 1), ar)
    pygame.draw.circle(aura, (*SMOKE_H, int(30 + 22 * pulse)),
                       (HX, HY - 1), ar - 4)
    surf.blit(aura, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    # Re-stamp the real bird on top of smoke + clone + aura → crisp silhouette.
    surf.blit(bird, (0, 0))

    # Faint cool rim along the crown / back of the head so the masked figure's
    # top edge stays separated from the violet smoke — carries the silhouette
    # read even when the violet hue is desaturated.
    pygame.draw.line(surf, SMOKE_H, (HX - 8, CROWN_Y + 1),
                     (HX + 8, CROWN_Y - 1), 1)

    # ── 4 · ninjato slung across the back (cool steel — carries the read) ──
    # Steeper diagonal from below the tail up past the crown, bright steel edge
    # + a full-length violet/hot rim, and a hilt-knob clearly ABOVE the crown.
    bx0, by0 = HX - 20, HY + 14            # lower (tail) end
    bx1, by1 = HX + 10, CROWN_Y - 11       # upper (above crown) end
    pygame.draw.line(surf, (18, 20, 28), (bx0, by0), (bx1, by1), 6)   # shadow
    pygame.draw.line(surf, STEEL, (bx0, by0), (bx1, by1), 4)          # body
    pygame.draw.line(surf, STEEL_H, (bx0 + 1, by0 - 1),
                     (bx1 + 1, by1 - 1), 2)                            # bright edge
    # Full-length animated violet/hot rim running the leading blade edge.
    rim = (int(GLOW[0]), int(GLOW[1]), min(255, GLOW[2] + 20))
    pygame.draw.line(surf, rim, (bx0 + 2, by0 - 2), (bx1 + 2, by1 - 2), 1)
    pygame.draw.line(surf, CORE, (bx1 - 4, by1 + 5), (bx1 + 1, by1 - 1), 1)
    # Square tsuba (guard) + wrapped tsuka with a clear knob poking above crown.
    pygame.draw.rect(surf, (16, 16, 24), (bx1 - 4, by1, 6, 4))
    pygame.draw.rect(surf, GLOW, (bx1 - 3, by1 + 1, 4, 2))
    pygame.draw.line(surf, (20, 22, 30), (bx1, by1), (bx1 + 6, by1 - 7), 4)
    pygame.draw.circle(surf, STEEL_H, (bx1 + 6, by1 - 7), 2)          # pommel knob
    pygame.draw.circle(surf, CORE, (bx1 + 6, by1 - 7), 1)

    # ── 5 · head wrap + headband with the single glowing eye-slit ──────────
    # Slim black face wrap fold across the lower face (hard-edged, no smoke).
    store_skins._poly(surf, SHADOW,
                      [(HX - 9, HY + 3), (HX + 13, HY + 1),
                       (HX + 12, HY + 9), (HX - 8, HY + 10)])
    store_skins._poly(surf, SHADOW_H,
                      [(HX - 8, HY + 3), (HX + 6, HY + 2),
                       (HX + 5, HY + 5), (HX - 7, HY + 6)])
    # SINGLE horizontal eye-slit: dark recess + one violet glow bar (floored so
    # the face never blinks out) + one hot-core glint near the leading (front) end.
    pygame.draw.rect(surf, (6, 6, 10), (HX - 5, HY - 2, 18, 5), border_radius=2)
    slit_glow = pygame.Surface((24, 11), pygame.SRCALPHA)
    slit_a = int(170 + 70 * pulse)
    pygame.draw.rect(slit_glow, (*GLOW, slit_a), (3, 3, 17, 4), border_radius=2)
    surf.blit(slit_glow, (HX - 8, HY - 5), special_flags=pygame.BLEND_RGBA_ADD)
    pygame.draw.circle(surf, CORE, (HX + 9, HY), 2)                   # leading glint

    # Headband over the crown; tails flick to the RIGHT (front) so they read
    # against the sky, NOT into the violet smoke on the left.
    by = CROWN_Y - 1
    pygame.draw.line(surf, (8, 8, 14), (HX - 11, by + 1), (HX + 12, by - 1), 5)
    pygame.draw.line(surf, SHADOW, (HX - 11, by), (HX + 12, by - 2), 3)
    pygame.draw.line(surf, GLOW, (HX - 8, by - 1), (HX + 8, by - 2), 1)
    flick = int(4 * breathe)
    for off, w in ((0, 3), (4, 2)):
        pygame.draw.line(surf, SHADOW, (HX + 11, by + off - 1),
                         (HX + 22, by + off + 4 + flick), w)
    pygame.draw.line(surf, GLOW, (HX + 12, by),
                     (HX + 21, by + 4 + flick), 1)

    # ── 6 · ONE readable shuriken in clear upper-left space ────────────────
    spin = t * math.tau
    sx, sy = HX - 30, HY - 14
    wob = 2 * math.sin(t * math.tau)
    orbit = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    _shuriken(orbit, sx + wob, sy - wob, 5, spin, STEEL_H, 230)
    pygame.draw.circle(orbit, (*CORE, 230), (int(sx + wob), int(sy - wob)), 1)
    surf.blit(orbit, (0, 0))


build = store_skins._make_skin(_paint, base_fn=_phantom_base)
