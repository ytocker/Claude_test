"""NIGHT THUNDER — thunderbird skin candidate (Design 4).

A nocturnal, brooding raptor: a clean dark night-indigo silhouette cracked by
pale static lightning-scar veins, lit by two glowing violet eyes (the 40px
tell). Wings collapse to a dark mass with only an electric-violet rim on the
leading edge, so at 40px the read is "dark raptor with lit eyes + scars", never
a grey smudge. Scars are STATIC (identical every frame) so the bird reads as
scarred, not animated — except a rare quiet flash on the power-flap frame
(frame 0, wing_angle=50) where the scars brighten and halo.

Scratch exploration builder — wrapped by the ninja_render harness, never
registered in store_skins.BUILDERS.
"""
import pygame
import math

from game.parrot import _WING_ANGLES, _add_outline, _aaellipse

COMPOSITE_W, COMPOSITE_H = 64, 84
BCX, BCY = 32, 44
# Head/beak pushed forward for a directional raptor lean.
HCX, HCY = 47, 33
CROWN_Y = 24

# Night-storm palette — grey dropped entirely; the whole bird lives in indigo.
NIGHT_INDIGO  = (23, 16, 41)     # #171029 — darkest body + wing base
VIOLET_SHADOW = (59, 42, 99)     # #3B2A63 — mid violet body cap
ELECTRIC      = (124, 91, 214)   # #7C5BD6 — eyes + wing rim + scar + crest edge
SCAR_PALE     = (231, 220, 255)  # #E7DCFF — hero lightning scars
# A cool 1px cold-highlight (the only "storm grey", never a fill).
COOL_HILITE   = (150, 158, 185)


def _flap(a):
    return (a + 40) / 90.0


def _strike(a):
    return 1.0 - _flap(a)


def _glow_dot(surf, center, radius, color, layers=4, peak=46):
    """Soft additive violet aura — stacked translucent discs so the storm
    haze reads without a hard edge."""
    cx, cy = center
    for i in range(layers, 0, -1):
        r = radius * i / layers
        a = int(peak * (1 - (i - 1) / layers))
        g = pygame.Surface((int(r * 2 + 2), int(r * 2 + 2)), pygame.SRCALPHA)
        pygame.draw.circle(g, (*color, a), (int(r + 1), int(r + 1)), int(r))
        surf.blit(g, (cx - r - 1, cy - r - 1), special_flags=pygame.BLEND_RGBA_ADD)


def _wing(angle_deg, strike):
    """Dark storm wing: a single clean night-indigo silhouette so it collapses
    to a dark mass at 40px, with only an electric-violet rim on the leading
    edge (brighter on the strike) and a 1px cool cold-highlight."""
    w = pygame.Surface((52, 52), pygame.SRCALPHA)

    # One dark indigo plane — no grey, no busy inner planes to muddy the read.
    plane = [(26, 27), (44, 14), (50, 26), (41, 37), (24, 40)]
    pygame.draw.polygon(w, NIGHT_INDIGO, plane)

    # Faint violet-shadow feather hint low on the plane (kept dark, subtle).
    pygame.draw.polygon(w, VIOLET_SHADOW, [(26, 29), (40, 34), (24, 39)])

    # Electric rim-light on the LEADING EDGE only — the wing's whole read.
    rim_a = int(150 + 90 * strike)
    rim = pygame.Surface((52, 52), pygame.SRCALPHA)
    pygame.draw.line(rim, (*ELECTRIC, rim_a), (27, 27), (44, 14), 2)
    pygame.draw.line(rim, (*ELECTRIC, rim_a), (44, 14), (50, 26), 2)
    # A single 1px cool cold-highlight just inside the rim.
    pygame.draw.line(rim, (*COOL_HILITE, 90), (30, 27), (44, 16), 1)
    w.blit(rim, (0, 0))

    return pygame.transform.rotate(w, angle_deg)


def _scar(surf, pts, bright, hero=False):
    """A single hairline lightning-scar polyline. `bright` toggles the quiet
    power-flap flash (higher alpha + paler colour + halo). `hero` forces the
    pale scar colour and a resting alpha high enough to survive at 40px."""
    if bright:
        col, a = SCAR_PALE, 240
    elif hero:
        col, a = SCAR_PALE, 200
    else:
        col, a = ELECTRIC, 200
    scar = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    pygame.draw.lines(scar, (*col, a), False, pts, 1)
    if bright:
        # A faint halo so the flash feels like light, not a repaint.
        glow = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
        pygame.draw.lines(glow, (*ELECTRIC, 80), False, pts, 3)
        surf.blit(glow, (0, 0))
    surf.blit(scar, (0, 0))


def _build_frame(wing_angle_deg):
    surf = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    strike = _strike(wing_angle_deg)
    # The power-flap frame (angle 50) is the rare quiet flash.
    flash = wing_angle_deg == 50

    # --- Far wing (behind body) ---
    far = _wing(wing_angle_deg * 0.7 - 8, strike)
    fr = far.get_rect(center=(BCX - 9, BCY - 4))
    surf.blit(far, fr)

    # --- Dim violet body aura ---
    _glow_dot(surf, (BCX, BCY + 2), 20, ELECTRIC, layers=4)

    # --- Talons: small electric-violet claws tucked under the body, echoing
    # the eye colour — a tight glow, no hanging blob ---
    _glow_dot(surf, (BCX, BCY + 14), 4, ELECTRIC, layers=3, peak=36)
    for tx in (BCX - 4, BCX, BCX + 4):
        pygame.draw.line(surf, ELECTRIC, (tx, BCY + 11), (tx, BCY + 15), 2)
        pygame.draw.line(surf, ELECTRIC, (tx, BCY + 15), (tx - 1, BCY + 17), 2)
        pygame.draw.line(surf, NIGHT_INDIGO, (tx, BCY + 10), (tx, BCY + 12), 1)

    # --- Body: deep indigo base with a lighter violet cap. Lower ellipse is
    # narrowed and the whole mass leans toward the beak for a raptor wedge ---
    _aaellipse(surf, NIGHT_INDIGO, (BCX + 1, BCY + 2), 16, 17)
    # Lighter violet cap (upper body catches the storm light).
    cap = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    _aaellipse(cap, VIOLET_SHADOW, (BCX + 2, BCY - 3), 14, 11)
    surf.blit(cap, (0, 0))
    # Narrower, forward-set belly so the outline is a forward-lean wedge.
    _aaellipse(surf, NIGHT_INDIGO, (BCX + 1, BCY + 8), 9, 9)

    # --- Static lightning-scar veins branching across the chest. At least one
    # HERO pale scar survives on every frame; the f0 flash brightens them all ---
    _scar(surf, [(BCX - 7, BCY - 4), (BCX - 2, BCY + 1),
                 (BCX - 4, BCY + 5), (BCX + 2, BCY + 10)], flash, hero=True)
    _scar(surf, [(BCX - 2, BCY + 1), (BCX + 5, BCY - 2),
                 (BCX + 4, BCY + 4), (BCX + 9, BCY + 3)], flash)
    _scar(surf, [(BCX + 5, BCY - 2), (BCX + 10, BCY - 6)], flash)

    # --- Dark seam where the NEAR wing meets the chest, so the wing reads as
    # a wing and doesn't merge into the violet body cap at 40px ---
    pygame.draw.line(surf, NIGHT_INDIGO, (BCX - 4, BCY - 8), (BCX + 3, BCY + 4), 1)

    # --- Head: two bold swept crest blades anchored INTO the skull ---
    # Blades start ~4px inside the head ellipse and are broad wedges (not thin
    # spikes) flattened low against the skull, so they never read as antennae.
    # Each is a filled triangle: wide base on the crown, sweeping back to a tip.
    pygame.draw.polygon(surf, VIOLET_SHADOW, [
        (HCX - 2, CROWN_Y + 8), (HCX + 3, CROWN_Y + 3),
        (HCX - 17, CROWN_Y + 1)])
    pygame.draw.polygon(surf, VIOLET_SHADOW, [
        (HCX - 4, CROWN_Y + 9), (HCX + 1, CROWN_Y + 5),
        (HCX - 13, CROWN_Y - 3)])
    # Electric lit edge on each blade's leading (upper) face.
    pygame.draw.line(surf, ELECTRIC, (HCX + 3, CROWN_Y + 3), (HCX - 17, CROWN_Y + 1), 1)
    pygame.draw.line(surf, ELECTRIC, (HCX + 1, CROWN_Y + 5), (HCX - 13, CROWN_Y - 3), 1)

    # Head mass — dark indigo with a violet cap catch.
    _aaellipse(surf, NIGHT_INDIGO, (HCX, HCY), 11, 10)
    hcap = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    _aaellipse(hcap, VIOLET_SHADOW, (HCX + 1, HCY - 3), 9, 6)
    surf.blit(hcap, (0, 0))

    # --- Beak: sharp charcoal hook, predatory, pushed forward with the head ---
    pygame.draw.polygon(surf, (40, 38, 52), [
        (HCX + 9, HCY - 1), (HCX + 18, HCY + 1), (HCX + 9, HCY + 5)])
    pygame.draw.polygon(surf, (26, 24, 36), [
        (HCX + 15, HCY + 1), (HCX + 18, HCY + 1), (HCX + 13, HCY + 5)])

    # --- Brow-ridge: a dark notch above each eye so it reads "predator" ---
    pygame.draw.line(surf, NIGHT_INDIGO, (HCX + 1, HCY - 5), (HCX + 6, HCY - 4), 2)
    pygame.draw.line(surf, NIGHT_INDIGO, (HCX - 7, HCY - 4), (HCX - 2, HCY - 5), 2)

    # --- Glowing violet eyes — the PRIMARY 40px tell, kept bright & exact ---
    for ex, ey in ((HCX + 3, HCY - 1),):
        _glow_dot(surf, (ex, ey), 6, ELECTRIC, layers=3)
        pygame.draw.circle(surf, ELECTRIC, (ex, ey), 4)
        pygame.draw.circle(surf, SCAR_PALE, (ex, ey), 2)
        pygame.draw.circle(surf, (255, 255, 255), (ex - 1, ey - 1), 1)
    # A second smaller eye-glint hint (far eye) to sell two glowing eyes.
    _glow_dot(surf, (HCX - 4, HCY), 4, ELECTRIC, layers=2)
    pygame.draw.circle(surf, ELECTRIC, (HCX - 4, HCY), 2)
    pygame.draw.circle(surf, SCAR_PALE, (HCX - 4, HCY), 1)

    # --- Near wing (in front of body) ---
    near = _wing(wing_angle_deg, strike)
    nr = near.get_rect(center=(BCX - 3, BCY - 2))
    surf.blit(near, nr)

    return surf


_cache = {}


def build(frame_idx: int, tilt_deg: float) -> pygame.Surface:
    angle = _WING_ANGLES[frame_idx % len(_WING_ANGLES)]
    key = (frame_idx % len(_WING_ANGLES), round(tilt_deg / 3) * 3)
    if key not in _cache:
        _cache[key] = pygame.transform.rotozoom(
            _add_outline(_build_frame(angle)), key[1], 1.0)
    return _cache[key]
