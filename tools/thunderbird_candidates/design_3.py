"""SOLAR WAR CHIEF — golden raptor thunderbird candidate (scratch exploration).

A proud UPRIGHT raptor whose war-bonnet crown is the topmost element and whose
head + beak + eye are the highest-contrast focal event. Behind the shoulders
sits a small soft-gradient sun HALO — a crescent the bird breaks on every side:
head clears its top, wings sweep past its edge, the tall chest pillar splits its
centre. The halo frames the chief; it never contains him. Ember-brown outlines
give the wing a hard value break against the gold so a real raptor silhouette
reads at 40px, not a "fireball coin."

Exploration only — nothing here is registered in a live BUILDERS map; the
production thunderbird skin is untouched.
"""
import math
import pygame

from game.parrot import _WING_ANGLES, _add_outline, _aaellipse

COMPOSITE_W, COMPOSITE_H = 64, 88
BCX, BCY = 32, 50          # body centre (chest pillar sits low so head clears)
HCX, HCY = 42, 30          # head centre, lifted well above the body mass
CROWN_Y = 18               # war-bonnet fan root — topmost element

# Ceremonial solar palette. Ember-brown grounds the shadows AND rims the wing
# so the golds have a hard dark edge to sing against; white-hot is the eye/beak.
EMBER   = (122, 46, 16)    # #7A2E10 ember-brown — shadow / wing outline
SUN_OR  = (232, 100, 26)   # #E8641A sun-orange — mid plumage
GOLD    = (255, 176, 33)   # #FFB021 gold — crown feathers / body highlights
FLARE   = (255, 233, 168)  # #FFE9A8 flare-yellow — top primaries / rim light
WHITE_H = (255, 248, 224)  # #FFF8E0 white-hot — eye glint / beak edge
RED_TIP = (198, 44, 24)    # feather-tip red, a shade under sun-orange
BRASS   = (214, 168, 74)   # brass talons
BRASS_D = (150, 110, 44)   # brass shadow
BEAK    = (58, 44, 30)     # dark raptor beak so gold owns the warm-bright


def _flap(a):
    # 0 at the deepest down-stroke (angle -40), 1 at the top up-stroke (50).
    return (a + 40) / 90.0


def _strike(a):
    return 1.0 - _flap(a)


def _halo(surf, cx, cy):
    """Soft sun HALO behind the shoulders — a few concentric alpha circles,
    no rings, no spokes. Small (~40% of the R1 disc) and pushed up-and-behind
    so head, wings and chest break its outline. It frames the chief, giving the
    gold plumage warmth to sit on without reading as a coin/power-up burst."""
    # Concentric alpha discs, brightest at the core, fading to a warm bloom.
    for r, rgb, a in (
        (26, SUN_OR, 46),
        (21, SUN_OR, 70),
        (16, GOLD, 100),
        (11, GOLD, 140),
        (7, FLARE, 170),
    ):
        g = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(g, (*rgb, a), (r + 1, r + 1), r)
        surf.blit(g, (cx - r - 1, cy - r - 1))


def _crown(surf, cx, root_y):
    """Tall fanned war-bonnet arc of upright polygon feathers — the identity
    anchor. Gold->orange banded blades, each red-tipped, radiating from CROWN_Y.
    Odd count so the centre feather stands tallest; now taller/more dramatic
    since the smaller halo no longer competes with it."""
    n = 7
    spread = math.radians(80)                 # wider, prouder fan
    length = 26                               # taller now the disc is smaller
    for i in range(n):
        t = i / (n - 1)                       # 0..1 across the fan
        ang = -math.pi / 2 + (t - 0.5) * spread
        # Centre feathers stand tallest; outer ones shorter, for a domed fan.
        ln = length * (0.66 + 0.34 * (1 - abs(t - 0.5) * 2))
        tipx = cx + ln * math.cos(ang)
        tipy = root_y + ln * math.sin(ang)
        perp = ang + math.pi / 2
        halfw = 2.6
        bx, by = cx + 2 * math.cos(ang), root_y + 2 * math.sin(ang)
        near_tipx = cx + (ln - 6) * math.cos(ang)
        near_tipy = root_y + (ln - 6) * math.sin(ang)
        quad = [
            (bx + halfw * math.cos(perp), by + halfw * math.sin(perp)),
            (near_tipx + 1.5 * math.cos(perp), near_tipy + 1.5 * math.sin(perp)),
            (tipx, tipy),
            (near_tipx - 1.5 * math.cos(perp), near_tipy - 1.5 * math.sin(perp)),
            (bx - halfw * math.cos(perp), by - halfw * math.sin(perp)),
        ]
        base = GOLD if i % 2 == 0 else SUN_OR
        pygame.draw.polygon(surf, EMBER, quad)      # dark rim for separation
        inner = [
            (bx + (halfw - 1) * math.cos(perp), by + (halfw - 1) * math.sin(perp)),
            (near_tipx, near_tipy),
            (bx - (halfw - 1) * math.cos(perp), by - (halfw - 1) * math.sin(perp)),
        ]
        pygame.draw.polygon(surf, base, inner)
        # Red tip cap — the war accent echoed on the wing.
        pygame.draw.polygon(surf, RED_TIP, [
            (near_tipx + 1.5 * math.cos(perp), near_tipy + 1.5 * math.sin(perp)),
            (tipx, tipy),
            (near_tipx - 1.5 * math.cos(perp), near_tipy - 1.5 * math.sin(perp)),
        ])
    # A gold band binds the feather roots into one bonnet.
    pygame.draw.arc(surf, GOLD, (cx - 15, root_y - 3, 30, 13), math.pi, 2 * math.pi, 3)
    pygame.draw.arc(surf, EMBER, (cx - 15, root_y - 3, 30, 13), math.pi, 2 * math.pi, 1)


def _wing(cx, cy, angle_deg):
    """Golden raptor wing with a HARD ember-brown leading edge so it reads
    against the gold halo, and a long reach so the tip sweeps clearly past the
    disc from below-body (down-stroke) to above-head (up-stroke)."""
    w = pygame.Surface((84, 84), pygame.SRCALPHA)
    ax, ay = 40, 42                            # shoulder anchor within surf
    # Long swept primary silhouette — reaches far past the shoulder so the tip
    # clearly breaks the halo edge on every frame and sweeps a wide beat arc.
    tip = (ax + 44, ay - 18)                    # far primary tip
    trail = (ax + 24, ay + 22)                  # trailing secondary
    plane = [(ax - 2, ay - 2), tip, (ax + 46, ay + 2), trail]
    # Drop shadow for depth against the bright halo.
    pygame.draw.polygon(w, (60, 22, 8, 130),
                        [(x + 2, y + 3) for x, y in plane])
    # Main wing plane, sun-orange.
    pygame.draw.polygon(w, SUN_OR, plane)
    # Gold body of the wing — the lit upper surface.
    pygame.draw.polygon(w, GOLD, [(ax - 2, ay - 2), tip,
                                  (ax + 30, ay - 4), (ax + 4, ay + 8)])
    # FLARE lift on the top primaries so the leading feathers pop against sky.
    pygame.draw.polygon(w, FLARE, [(ax, ay - 3), tip, (ax + 24, ay - 10)])
    # Dark feather-divider texture fanning out across the primaries.
    for f in (0.4, 0.58, 0.76):
        px = ax + (tip[0] - ax) * f
        py = ay + (tip[1] - ay) * f
        pygame.draw.line(w, EMBER, (px + 1, py + 8), (px + 4, py - 2), 1)
    # HARD ember-brown leading edge — the value break that saves the read.
    pygame.draw.line(w, EMBER, (ax - 2, ay - 2), tip, 3)
    pygame.draw.line(w, EMBER, tip, (ax + 46, ay + 2), 3)
    # Red-tipped outermost primary — war accent echoing the crown.
    pygame.draw.polygon(w, RED_TIP, [tip, (ax + 46, ay + 2), (ax + 42, ay + 6)])
    return pygame.transform.rotate(w, angle_deg)


def _build_frame(wing_angle_deg):
    surf = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)

    # ── HALO first: small, pushed UP-AND-BEHIND the shoulders so its crescent
    # shows above the shoulder while the body, head and wings break its outline.
    _halo(surf, BCX + 5, BCY - 20)

    # ── BODY: a VERTICAL ember->gold chest PILLAR (taller than wide, upright
    # raptor posture). Stacked ellipses climb from an ember base to a gold-hot
    # chest so it reads as a standing pillar splitting the halo, not a ball.
    _aaellipse(surf, EMBER, (BCX + 1, BCY + 3), 12, 20)     # tall shadow base
    _aaellipse(surf, SUN_OR, (BCX, BCY), 11, 18)            # body mid, tall
    _aaellipse(surf, GOLD, (BCX - 1, BCY - 4), 8, 13)       # lit chest column
    _aaellipse(surf, FLARE, (BCX - 2, BCY - 6), 5, 8)       # chest flare stripe
    # Dark feather-divider lines across the chest for plumage texture.
    for dy in (-4, 1, 6, 11):
        pygame.draw.line(surf, EMBER, (BCX - 7, BCY + dy),
                         (BCX + 7, BCY + dy + 1), 1)
    # Belly warm underglow so the bottom doesn't go muddy at 40px.
    _aaellipse(surf, SUN_OR, (BCX - 2, BCY + 13), 6, 5)

    # ── WING (dynamic), over the body, sweeping across and PAST the halo edge.
    wing = _wing(BCX, BCY, wing_angle_deg)
    wr = wing.get_rect(center=(BCX + 5, BCY - 8))
    surf.blit(wing, wr.topleft)

    # ── Talons gripping a radiant ember, below the body.
    tal_y = BCY + 18
    for fx in (BCX - 6, BCX, BCX + 6):
        pygame.draw.line(surf, BRASS_D, (fx, tal_y - 2), (fx, tal_y + 5), 3)
        pygame.draw.line(surf, BRASS, (fx, tal_y - 2), (fx, tal_y + 5), 1)
        pygame.draw.circle(surf, BRASS, (fx, tal_y + 5), 2)
        pygame.draw.circle(surf, BRASS_D, (fx, tal_y + 5), 2, 1)
    emb = pygame.Surface((16, 16), pygame.SRCALPHA)
    pygame.draw.circle(emb, (*SUN_OR, 120), (8, 8), 7)
    pygame.draw.circle(emb, (*FLARE, 200), (8, 8), 4)
    pygame.draw.circle(emb, WHITE_H, (8, 8), 2)
    surf.blit(emb, (BCX - 8, tal_y - 1))

    # ── HEAD: enlarged golden raptor head, lifted well clear of the body mass
    # so it silhouettes against sky above the pillar. The FOCAL point.
    _aaellipse(surf, EMBER, (HCX + 1, HCY + 1), 12, 12)     # head shadow
    _aaellipse(surf, GOLD, (HCX, HCY), 11, 11)              # head base
    _aaellipse(surf, FLARE, (HCX - 3, HCY - 3), 5, 4)       # crown sheen
    _aaellipse(surf, SUN_OR, (HCX - 4, HCY + 5), 4, 3)      # cheek warmth

    # ── War-bonnet crown fan — topmost element, drawn over the head crown.
    _crown(surf, HCX, CROWN_Y)

    # ── FIERCE EYE — the highest-contrast event: large white-hot glint ring
    # around a black pupil, so it reads alive and sharp at 40px.
    pygame.draw.circle(surf, WHITE_H, (HCX + 3, HCY - 1), 5)
    pygame.draw.circle(surf, BEAK, (HCX + 4, HCY - 1), 4)
    pygame.draw.circle(surf, (12, 8, 6), (HCX + 4, HCY - 1), 2)
    pygame.draw.circle(surf, WHITE_H, (HCX + 2, HCY - 3), 2)   # big catchlight
    # Bold ember brow ridge — the raptor scowl over the eye.
    pygame.draw.line(surf, EMBER, (HCX - 4, HCY - 5), (HCX + 8, HCY - 4), 2)

    # ── BEAK: hooked raptor beak with a FLARE rim on the top edge so it
    # silhouettes against sky — highest-contrast with the eye.
    beak = [(HCX + 8, HCY), (HCX + 17, HCY + 2), (HCX + 12, HCY + 7),
            (HCX + 7, HCY + 4)]
    pygame.draw.polygon(surf, BEAK, beak)
    pygame.draw.polygon(surf, (30, 22, 14), beak, 1)
    pygame.draw.line(surf, FLARE, (HCX + 8, HCY), (HCX + 17, HCY + 2), 1)  # top rim
    pygame.draw.line(surf, GOLD, (HCX + 8, HCY + 2), (HCX + 14, HCY + 3), 1)

    return surf


_cache = {}


def build(frame_idx: int, tilt_deg: float) -> pygame.Surface:
    angle = _WING_ANGLES[frame_idx % len(_WING_ANGLES)]
    key = (frame_idx % len(_WING_ANGLES), round(tilt_deg / 3) * 3)
    if key not in _cache:
        _cache[key] = pygame.transform.rotozoom(
            _add_outline(_build_frame(angle)), key[1], 1.0)
    return _cache[key]
