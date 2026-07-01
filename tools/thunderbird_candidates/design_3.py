"""SOLAR WAR CHIEF — golden raptor thunderbird candidate (scratch exploration).

A proud upright raptor crowned by a fanned war-bonnet of upright polygon
feathers and backed by a glowing concentric sun-disc shield that bursts from
behind the shoulders. The wings beat ACROSS the sun, so the radial burst reads
"chief" even at 40px: crown-fan up top, sun-halo behind, warm ember-to-gold
plumage down the chest. Gold-on-warm survives the downscale, and the sun-disc
centre is the single white-hot focal that anchors the read.

Exploration only — nothing here is registered in a live BUILDERS map; the
production thunderbird skin is untouched.
"""
import math
import pygame

from game.parrot import _WING_ANGLES, _add_outline, _aaellipse

COMPOSITE_W, COMPOSITE_H = 64, 84
BCX, BCY = 32, 44          # body centre
HCX, HCY = 44, 34          # head centre
CROWN_Y = 24               # war-bonnet fan root

# Ceremonial solar palette. Ember-brown grounds the shadows so the golds have
# something dark to sing against; white-hot is reserved for the sun core alone.
EMBER   = (122, 46, 16)    # #7A2E10 ember-brown — shadow / feather dividers
SUN_OR  = (232, 100, 26)   # #E8641A sun-orange — mid plumage / outer rings
GOLD    = (255, 176, 33)   # #FFB021 gold — crown feathers / body highlights
FLARE   = (255, 233, 168)  # #FFE9A8 flare-yellow — inner ring / rim light
WHITE_H = (255, 248, 224)  # #FFF8E0 white-hot — sun core / brightest glints
RED_TIP = (198, 44, 24)    # feather-tip red, a shade under sun-orange
BRASS   = (214, 168, 74)   # brass talons
BRASS_D = (150, 110, 44)   # brass shadow
BEAK    = (58, 44, 30)     # dark raptor beak so gold owns the warm-bright


def _flap(a):
    # 0 at the deepest down-stroke (angle -40), 1 at the top up-stroke (50).
    return (a + 40) / 90.0


def _strike(a):
    return 1.0 - _flap(a)


def _sun_disc(surf, cx, cy, strike):
    """Concentric sun-disc shield bursting from behind the shoulders. Nested
    arc rings amber-outer -> white-hot inner, plus radiating rays, so the wings
    beat across a radial burst. The core pulses slightly larger on the
    down-stroke (`strike` -> 1) — the moment the chief drives forward."""
    pulse = 1.0 + 0.14 * strike
    # Soft outer glow halo, painted first so everything sits on warmth.
    for r, a in ((30, 40), (24, 70), (18, 110)):
        glow = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*SUN_OR, a), (r + 1, r + 1), r)
        surf.blit(glow, (cx - r - 1, cy - r - 1))

    # Radiating rays behind the rings — thin ember-gold spokes for the burst.
    for i in range(12):
        ang = math.radians(i * 30 + 15)
        r0, r1 = 15, 27
        p0 = (cx + r0 * math.cos(ang), cy + r0 * math.sin(ang))
        p1 = (cx + r1 * math.cos(ang), cy + r1 * math.sin(ang))
        pygame.draw.line(surf, (*GOLD, 190), p0, p1, 2)

    # Nested rings: outer sun-orange -> gold -> flare, filled disc under.
    pygame.draw.circle(surf, SUN_OR, (cx, cy), 17)
    pygame.draw.circle(surf, EMBER, (cx, cy), 17, 2)
    pygame.draw.circle(surf, GOLD, (cx, cy), 12)
    pygame.draw.circle(surf, FLARE, (cx, cy), int(7 * pulse))
    # White-hot pulsing core.
    pygame.draw.circle(surf, WHITE_H, (cx, cy), int(4 * pulse))


def _crown(surf, cx, root_y):
    """Fanned war-bonnet arc of upright polygon feathers radiating from
    CROWN_Y — gold->orange blades, each red-tipped. Odd count so the centre
    feather stands tallest and the fan reads symmetric even downscaled."""
    n = 7
    spread = math.radians(74)                 # total fan angle
    length = 20
    for i in range(n):
        t = i / (n - 1)                       # 0..1 across the fan
        ang = -math.pi / 2 + (t - 0.5) * spread
        # Centre feathers stand taller; outer ones shorter, for a domed fan.
        ln = length * (0.7 + 0.3 * (1 - abs(t - 0.5) * 2))
        tipx = cx + ln * math.cos(ang)
        tipy = root_y + ln * math.sin(ang)
        # Feather body as a slim quill quad from the root to just under the tip.
        perp = ang + math.pi / 2
        halfw = 2.4
        bx, by = cx + 2 * math.cos(ang), root_y + 2 * math.sin(ang)
        near_tipx = cx + (ln - 5) * math.cos(ang)
        near_tipy = root_y + (ln - 5) * math.sin(ang)
        quad = [
            (bx + halfw * math.cos(perp), by + halfw * math.sin(perp)),
            (near_tipx + 1.4 * math.cos(perp), near_tipy + 1.4 * math.sin(perp)),
            (tipx, tipy),
            (near_tipx - 1.4 * math.cos(perp), near_tipy - 1.4 * math.sin(perp)),
            (bx - halfw * math.cos(perp), by - halfw * math.sin(perp)),
        ]
        # Alternate gold / sun-orange for banding across the fan.
        base = GOLD if i % 2 == 0 else SUN_OR
        pygame.draw.polygon(surf, EMBER, quad)      # dark rim for separation
        inner = [
            (bx + (halfw - 1) * math.cos(perp), by + (halfw - 1) * math.sin(perp)),
            (near_tipx, near_tipy),
            (bx - (halfw - 1) * math.cos(perp), by - (halfw - 1) * math.sin(perp)),
        ]
        pygame.draw.polygon(surf, base, inner)
        # Red tip cap.
        pygame.draw.polygon(surf, RED_TIP, [
            (near_tipx + 1.4 * math.cos(perp), near_tipy + 1.4 * math.sin(perp)),
            (tipx, tipy),
            (near_tipx - 1.4 * math.cos(perp), near_tipy - 1.4 * math.sin(perp)),
        ])
    # A gold band across the feather roots binds the fan into one bonnet.
    pygame.draw.arc(surf, GOLD, (cx - 14, root_y - 3, 28, 12), math.pi, 2 * math.pi, 3)
    pygame.draw.arc(surf, EMBER, (cx - 14, root_y - 3, 28, 12), math.pi, 2 * math.pi, 1)


def _wing(cx, cy, angle_deg):
    """Golden raptor wing that beats across the sun. Layered orange->gold
    primaries with dark feather dividers; rotated around its shoulder anchor."""
    w = pygame.Surface((54, 54), pygame.SRCALPHA)
    ax, ay = 26, 28                            # shoulder anchor within surf
    # Drop shadow for depth against the bright sun.
    pygame.draw.polygon(w, (60, 22, 8, 130), [
        (ax, ay), (ax + 24, ay - 12), (ax + 30, ay + 4), (ax + 12, ay + 16),
    ])
    # Main wing plane, sun-orange.
    pygame.draw.polygon(w, SUN_OR, [
        (ax, ay - 1), (ax + 22, ay - 13), (ax + 28, ay + 2), (ax + 10, ay + 14),
    ])
    # Gold leading-edge highlight.
    pygame.draw.polygon(w, GOLD, [
        (ax, ay - 1), (ax + 22, ay - 13), (ax + 24, ay - 6), (ax + 4, ay + 2),
    ])
    # Flare rim light along the top primaries.
    pygame.draw.line(w, FLARE, (ax + 2, ay - 2), (ax + 21, ay - 12), 2)
    # Dark feather-divider texture.
    for dx, dy in ((8, -3), (14, -6), (19, -9)):
        pygame.draw.line(w, EMBER, (ax + dx, ay + 3), (ax + dx + 4, ay - 4), 1)
    # Red-tipped primary tips — the war accent echoing the crown.
    pygame.draw.polygon(w, RED_TIP, [
        (ax + 22, ay - 13), (ax + 28, ay - 8), (ax + 27, ay + 1),
    ])
    return pygame.transform.rotate(w, angle_deg)


def _build_frame(wing_angle_deg):
    surf = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    strike = _strike(wing_angle_deg)

    # ── Sun-disc shield first: it bursts from behind the shoulders so the body
    # and wings layer over it. Centred a touch above/behind the body centre.
    _sun_disc(surf, BCX + 2, BCY - 6, strike)

    # ── Body: fiery ember->gold vertical gradient plumage. Painted as stacked
    # ellipses from ember base up to a gold chest so the chest glows.
    _aaellipse(surf, EMBER, (BCX + 1, BCY + 2), 15, 18)      # shadow base
    _aaellipse(surf, SUN_OR, (BCX, BCY), 14, 17)             # body mid
    _aaellipse(surf, GOLD, (BCX - 1, BCY - 4), 11, 11)       # lit chest
    _aaellipse(surf, FLARE, (BCX - 2, BCY - 7), 7, 5)        # chest flare
    # Dark feather-divider lines for plumage texture.
    for dy in (-2, 3, 8):
        pygame.draw.line(surf, EMBER, (BCX - 9, BCY + dy),
                         (BCX + 9, BCY + dy + 1), 1)
    # Belly warm underglow so the bottom doesn't go muddy at 40px.
    _aaellipse(surf, SUN_OR, (BCX - 3, BCY + 10), 8, 5)

    # ── Wing (dynamic), drawn over the body, beating across the sun.
    wing = _wing(BCX, BCY, wing_angle_deg)
    wr = wing.get_rect(center=(BCX + 4, BCY - 4))
    surf.blit(wing, wr.topleft)

    # ── Talons gripping a radiant ember, below the body.
    tal_y = BCY + 15
    for fx in (BCX - 6, BCX, BCX + 6):
        pygame.draw.line(surf, BRASS_D, (fx, tal_y - 2), (fx, tal_y + 5), 3)
        pygame.draw.line(surf, BRASS, (fx, tal_y - 2), (fx, tal_y + 5), 1)
        pygame.draw.circle(surf, BRASS, (fx, tal_y + 5), 2)
        pygame.draw.circle(surf, BRASS_D, (fx, tal_y + 5), 2, 1)
    # The gripped radiant ember — tiny glowing core between the talons.
    emb = pygame.Surface((16, 16), pygame.SRCALPHA)
    pygame.draw.circle(emb, (*SUN_OR, 120), (8, 8), 7)
    pygame.draw.circle(emb, (*FLARE, 200), (8, 8), 4)
    pygame.draw.circle(emb, WHITE_H, (8, 8), 2)
    surf.blit(emb, (BCX - 8, tal_y - 1))

    # ── Head: golden raptor head over the shoulders.
    _aaellipse(surf, EMBER, (HCX + 1, HCY + 1), 11, 11)      # head shadow
    _aaellipse(surf, GOLD, (HCX, HCY), 10, 10)               # head base
    _aaellipse(surf, FLARE, (HCX - 2, HCY - 3), 5, 4)        # crown sheen
    _aaellipse(surf, SUN_OR, (HCX - 4, HCY + 4), 4, 3)       # cheek warmth

    # ── War-bonnet crown fan radiating from CROWN_Y, over the head crown.
    _crown(surf, HCX, CROWN_Y)

    # Fierce raptor eye — dark with a white-hot glint so the face reads alive.
    pygame.draw.circle(surf, WHITE_H, (HCX + 3, HCY - 1), 4)
    pygame.draw.circle(surf, BEAK, (HCX + 4, HCY - 1), 3)
    pygame.draw.circle(surf, (12, 8, 6), (HCX + 4, HCY - 1), 2)
    pygame.draw.circle(surf, WHITE_H, (HCX + 3, HCY - 2), 1)
    # Bold gold brow ridge — the raptor scowl.
    pygame.draw.line(surf, EMBER, (HCX - 3, HCY - 4), (HCX + 7, HCY - 3), 2)

    # ── Beak: hooked raptor beak with a gold gloss.
    beak = [(HCX + 7, HCY), (HCX + 15, HCY + 2), (HCX + 11, HCY + 6),
            (HCX + 6, HCY + 4)]
    pygame.draw.polygon(surf, BEAK, beak)
    pygame.draw.polygon(surf, (30, 22, 14), beak, 1)
    pygame.draw.line(surf, GOLD, (HCX + 7, HCY + 1), (HCX + 13, HCY + 2), 1)

    return surf


_cache = {}


def build(frame_idx: int, tilt_deg: float) -> pygame.Surface:
    angle = _WING_ANGLES[frame_idx % len(_WING_ANGLES)]
    key = (frame_idx % len(_WING_ANGLES), round(tilt_deg / 3) * 3)
    if key not in _cache:
        _cache[key] = pygame.transform.rotozoom(
            _add_outline(_build_frame(angle)), key[1], 1.0)
    return _cache[key]
