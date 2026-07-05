"""AUREX — Cursed Gold-Lich Skeleton (skeleton redesign, design_5).

Scratch exploration ONLY — never registered in store_skins.BUILDERS, never
wired into production. The premium showpiece: GILDED GOLD bone is the loudest
mass, two hot violet socket-points burning INSIDE a gold skull, a dark
tattered mantle breaking the silhouette behind the shoulders.

The read order at 40px is, by construction: GOLD SKULL → two violet socket
POINTS → gold crown-band — with the gold skull (not the crown, not the glow)
the brightest legible mass. To guarantee this the rune-fire is contained: the
socket bloom stays INSIDE the socket voids, and the gold dome + rim are redrawn
ON TOP of the socket bloom so the cranium edge and the gold between the sockets
never go pink. All non-socket blooms are gated by a day/night factor so the
gold carries the whole read on the day sky with almost zero glow assist; only
at night does the violet blaze.
"""
from __future__ import annotations
import math
import pygame

from game.store_skins import SPRITE_W, SPRITE_H, _poly, _make_prebuilt_skin
from game.parrot import _aaellipse


# ── AUREX palette ────────────────────────────────────────────────────────────
_AU_GOLD_H  = (255, 226, 122)      # gold bone highlight — BRIGHTEST element
_AU_GOLD    = (224, 162, 30)       # gold bone body — the theme metal
_AU_GOLD_D  = (150, 104, 18)       # gold shadow / under-edge for roundness
_AU_BODY    = (22, 18, 31)         # deep void-violet-black "flesh"
_AU_BODY_D  = (14, 11, 21)         # darker void for the mantle depths
# Mantle pulled to a DARK anchor (value well below the gold, saturation ~halved)
# so the upper silhouette reads as a dark hood SHAPE, not a violet glow — the
# only hot violet on the bird is then the two socket pips (+ night wing trail).
_AU_MANTLE  = (22, 18, 31)         # tattered hood/collar — dark, near-body value
_AU_MANTLE_D = (16, 13, 23)        # #100D17-ish depth
_AU_MANTLE_RIM = (62, 44, 22)      # gold-dark rim framing the hood as attached
_AU_SOCK    = (16, 6, 18)          # socket void behind the rune-fire (near-black)
_AU_RUNE_C  = (179, 136, 255)      # violet rune-fire core  (#B388FF)
_AU_RUNE_M  = (122, 77, 224)       # violet rune-fire mid   (#7A4DE0)

# Module-level night factor: scales ALL non-socket blooms so the gold skeleton
# reads on the day sky with almost no glow assist, and only blazes at night.
# The render harness flips this when it builds the day vs night prebuilt skin.
NIGHT = 1.0


def _add_glow(surf, layer):
    """Composite an additive bloom so violet reads as light, not paint."""
    surf.blit(layer, (0, 0), special_flags=pygame.BLEND_RGB_ADD)


def _socket_bloom(cx, cy, r, intensity=0.7):
    """A TIGHT violet bloom that stays INSIDE the socket — two hot points in a
    gold face, never a face-wide haze. No outer halo ring on purpose."""
    box = r * 4
    g = pygame.Surface((box, box), pygame.SRCALPHA)
    gc = box // 2
    rings = (
        (r * 1.1, (*_AU_RUNE_M, int(70 * intensity))),
        (r * 0.7, (*_AU_RUNE_C, int(150 * intensity))),
        (r * 0.4, (*_AU_RUNE_C, int(230 * intensity))),
    )
    for rad, col in rings:
        pygame.draw.circle(g, col, (gc, gc), max(1, int(rad)))
    return g, (cx - gc, cy - gc)


def _rune_bloom(cx, cy, r, intensity=1.0):
    """A soft round violet bloom for AMBIENT accents (ribs, hood, hoard, wing
    trail) — these are the ones gated by the NIGHT factor."""
    box = r * 4
    g = pygame.Surface((box, box), pygame.SRCALPHA)
    gc = box // 2
    rings = (
        (r * 2.0, (*_AU_RUNE_M, int(40 * intensity))),
        (r * 1.4, (*_AU_RUNE_M, int(70 * intensity))),
        (r * 0.95, (*_AU_RUNE_C, int(120 * intensity))),
        (r * 0.55, (*_AU_RUNE_C, int(210 * intensity))),
    )
    for rad, col in rings:
        pygame.draw.circle(g, col, (gc, gc), int(rad))
    return g, (cx - gc, cy - gc)


def _gild_bone_line(surf, p0, p1, width=3):
    """A gold bone strut: gold body with a thin #FFE27A highlight ridge so the
    metal catches light. Highlight offset 1px toward the upper-left."""
    pygame.draw.line(surf, _AU_GOLD_D, p0, p1, width)
    pygame.draw.line(surf, _AU_GOLD, p0, p1, max(2, width - 1))
    hx0 = (p0[0], p0[1] - 1)
    hx1 = (p1[0], p1[1] - 1)
    pygame.draw.line(surf, _AU_GOLD_H, hx0, hx1, 1)


def _gild_knob(surf, c, r):
    """A gold joint knob with a highlight glint — for wrists and vertebrae."""
    pygame.draw.circle(surf, _AU_GOLD_D, c, r + 1)
    pygame.draw.circle(surf, _AU_GOLD, c, r)
    pygame.draw.circle(surf, _AU_GOLD_H, (c[0] - 1, c[1] - 1), max(1, r - 1))


def _au_wing(angle_deg):
    """Wing as a fan of GOLD finger-bones (phalanges) radiating from a gold
    wrist knob, over a dark void web — with a faint violet rune-glow trailing
    the tips on the swept poses; that trail is NIGHT-gated so the day wing is
    pure gold."""
    w = pygame.Surface((50, 50), pygame.SRCALPHA)

    # Dark void web so the gold finger-bones read as bone, not floating lines.
    web = [(24, 26), (46, 14), (50, 30), (34, 44), (18, 40)]
    _poly(w, _AU_BODY, web)
    pygame.draw.polygon(w, _AU_BODY_D, web, 1)

    # Violet rune-glow trailing the finger-tips (additive), stronger as the
    # wing sweeps up. Gated by NIGHT so it's near-silent on the day sky.
    glow = pygame.Surface((50, 50), pygame.SRCALPHA)
    trail = (0.45 + 0.55 * max(0.0, math.sin(math.radians(angle_deg)))) * NIGHT
    if trail > 0.02:
        for tip in ((47, 16), (49, 24), (42, 40)):
            b, off = _rune_bloom(tip[0], tip[1], 5, intensity=0.7 * trail)
            glow.blit(b, off, special_flags=pygame.BLEND_RGB_ADD)
        _add_glow(w, glow)

    # Gold wrist knob + radiating phalanges to each finger-tip.
    wrist = (25, 28)
    for tip in ((47, 16), (49, 24), (42, 40), (38, 18)):
        _gild_bone_line(w, wrist, tip, 2)
        _gild_knob(w, tip, 2)
    _gild_knob(w, wrist, 3)
    return pygame.transform.rotate(w, angle_deg)


def _build_design5(wing_angle_deg):
    """AUREX gold-lich skeleton. Draw order is deliberate: socket voids + their
    contained bloom go down FIRST, then the gold skull dome/rim is RE-GILDED ON
    TOP so the gold stays the brightest mass and the bloom can never pink the
    cranium. All non-socket blooms scale by the module NIGHT factor."""
    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)

    # ── Mantle layer (BEHIND everything) — a DARK collar/hood behind the head
    #    plus a thin drape, ~25-30% smaller than a full shoulder mass so the
    #    gold ribs + skull dome (not the mantle) define the upper silhouette.
    #    A flat dark SHAPE, no glow: a 1px gold-dark rim frames its leading edge
    #    so it reads as an ATTACHED dark hood around the gold, not a glow cloud.
    mantle = [
        (49, 10),                      # hood peak, tucked just behind the crown
        (57, 17), (57, 28),            # tightened near-shoulder collar
        (51, 36),                      # tattered hem notch
        (45, 30),
        (38, 38),                      # thin tattered drape
        (33, 29),
        (28, 35),                      # far-shoulder tatter (pulled in)
        (31, 23),
        (40, 12),                      # collar sweeping back up to the hood
    ]
    _poly(surf, _AU_MANTLE_D, [(x + 1, y + 1) for x, y in mantle])
    _poly(surf, _AU_MANTLE, mantle)
    # Gold-dark rim along the hood's leading/collar edge (frames the gold).
    pygame.draw.lines(surf, _AU_MANTLE_RIM, False,
                      [(40, 12), (49, 10), (57, 17), (57, 28)], 1)

    # ── Tail — void fan with a gilded leading edge.
    tail = [(2, 26), (17, 24), (23, 36), (12, 42)]
    _poly(surf, _AU_BODY, tail)
    pygame.draw.polygon(surf, _AU_BODY_D, tail, 1)
    _gild_bone_line(surf, (4, 28), (21, 25), 2)

    # ── Body — deep void ellipse (the dark flesh the gold bone sits on).
    _aaellipse(surf, _AU_BODY_D, (33, 33), 19, 14)
    _aaellipse(surf, _AU_BODY, (32, 32), 18, 13)

    # ── Ribcage — gold rib-arcs. A faint violet inner glow (NIGHT-gated, low).
    if NIGHT > 0.02:
        rib_glow = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
        b, off = _rune_bloom(28, 35, 7, intensity=0.15 * NIGHT)
        rib_glow.blit(b, off, special_flags=pygame.BLEND_RGB_ADD)
        _add_glow(surf, rib_glow)
    # Gold vertebra SPINE down the chest centre.
    spine = [(38, 25), (34, 29), (30, 33), (26, 37), (22, 40)]
    for i in range(len(spine) - 1):
        _gild_bone_line(surf, spine[i], spine[i + 1], 2)
    for vx, vy in spine:
        _gild_knob(surf, (vx, vy), 1)
    # Paired gold rib-arcs sweeping off the spine. The wing (center 34,28)
    # covers the upper cluster, so the LOWER ribs are pushed left + down, CLEAR
    # of the wing footprint, drawn at a 3px gold core so they read.
    for rect in ((20, 32, 12, 14), (17, 36, 12, 13), (15, 40, 11, 12)):
        pygame.draw.arc(surf, _AU_GOLD_D, rect,
                        math.radians(195), math.radians(345), 3)
        pygame.draw.arc(surf, _AU_GOLD, rect,
                        math.radians(200), math.radians(340), 2)
    # Upper ribs near the spine (partly under the wing) kept thinner.
    for off_x in (0, 5):
        rect = (24 + off_x, 24, 13, 15)
        pygame.draw.arc(surf, _AU_GOLD_D, rect,
                        math.radians(200), math.radians(340), 2)
        pygame.draw.arc(surf, _AU_GOLD, rect,
                        math.radians(205), math.radians(335), 2)

    # ── Wing — gold finger-bones (drawn over the ribs so it reads as the near
    #    wing) with its NIGHT-gated violet rune-trail.
    wing = _au_wing(wing_angle_deg)
    surf.blit(wing, wing.get_rect(center=(34, 28)).topleft)

    # ── SKULL — built in the order that keeps gold the brightest mass:
    #    1) socket voids + their CONTAINED bloom go down first,
    #    2) then the gold dome / rim / crown is RE-GILDED ON TOP, so the
    #       cranium edge and the gold between the sockets stay unmistakably
    #       gold (never pink).

    # 1a. Socket voids — small near-black holes.
    for sc in ((50, 20), (44, 21)):
        pygame.draw.circle(surf, _AU_SOCK, sc, 3)
    # 1b. Contained socket bloom — TIGHT, stays inside the holes. NOT NIGHT-
    #     gated: the two hot points are the constant "lich" tell day and night,
    #     but small enough that the gold re-gild on top still dominates.
    sock_glow = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    for sc in ((50, 20), (44, 21)):
        b, off = _socket_bloom(sc[0], sc[1], 2, intensity=0.7 + 0.4 * NIGHT)
        sock_glow.blit(b, off, special_flags=pygame.BLEND_RGB_ADD)
    _add_glow(surf, sock_glow)

    # 2a. Gold skull dome RE-GILDED OVER the bloom — this is the brightest mass.
    #     A 1px #16121F keyline sits just outside the dome so the gold edge stays
    #     crisp against bright blue day sky and the silhouette doesn't soften.
    _aaellipse(surf, _AU_BODY, (48, 22), 12, 11)
    _aaellipse(surf, _AU_GOLD_D, (48, 22), 11, 10)
    _aaellipse(surf, _AU_GOLD, (47, 21), 10, 9)
    # Bright metallic sheen crescent on the cranium.
    _aaellipse(surf, _AU_GOLD_H, (44, 17), 5, 3)
    # Jaw / lower-face gold mass below the sockets (gold between + around them).
    _aaellipse(surf, _AU_GOLD_D, (47, 27), 8, 4)
    _aaellipse(surf, _AU_GOLD, (47, 26), 7, 3)

    # 2b. Re-punch the socket holes through the re-gilded face so two clean dark
    #     sockets with hot violet cores read — gold rim all around them.
    for sc in ((50, 20), (44, 21)):
        pygame.draw.circle(surf, _AU_GOLD_D, sc, 4, 1)   # gold socket rim
        pygame.draw.circle(surf, _AU_SOCK, sc, 3)        # dark void
    # 1px violet pip dead-centre — the hard hot point.
    pygame.draw.circle(surf, _AU_RUNE_C, (50, 20), 1)
    pygame.draw.circle(surf, _AU_RUNE_C, (44, 21), 1)
    # A second tiny contained bloom re-blitted OVER the re-punched voids so the
    # cores glow but the surrounding gold stays gold.
    sock_glow2 = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    for sc in ((50, 20), (44, 21)):
        b, off = _socket_bloom(sc[0], sc[1], 2, intensity=0.6 + 0.4 * NIGHT)
        sock_glow2.blit(b, off, special_flags=pygame.BLEND_RGB_ADD)
    _add_glow(surf, sock_glow2)

    # Nose hollow + gold-tooth grin (2px gold teeth so they survive downscale).
    _poly(surf, _AU_SOCK, [(47, 24), (49, 24), (48, 26)])
    for gx in (44, 47, 50):
        pygame.draw.line(surf, _AU_GOLD_H, (gx, 28), (gx, 30), 2)
        pygame.draw.line(surf, _AU_GOLD_D, (gx + 1, 28), (gx + 1, 30), 1)

    # ── Crown-band across the brow — ONE clean gold horizontal band at the
    #    dome-highlight value (#FFE27A) with a 1px DARK under-keyline; the band
    #    is distinct from the dome only by that keyline, so it stays the legible
    #    third read at 40px instead of melting into the cranium.
    pygame.draw.line(surf, _AU_BODY_D, (40, 16), (55, 16), 1)   # dark under-keyline
    pygame.draw.line(surf, _AU_GOLD_H, (40, 14), (55, 14), 2)   # bright gold band
    # Brow coin medallion (the cursed-hoard tell on the head).
    pygame.draw.circle(surf, _AU_BODY_D, (47, 14), 3, 1)
    pygame.draw.circle(surf, _AU_GOLD, (47, 14), 2)
    pygame.draw.circle(surf, _AU_GOLD_H, (46, 13), 1)

    # ── Beak — gold-rimmed bone over a void beak.
    beak = [(55, 21), (61, 24), (58, 28), (52, 26)]
    _poly(surf, _AU_BODY, beak)
    pygame.draw.polygon(surf, _AU_GOLD_D, beak, 3)
    pygame.draw.polygon(surf, _AU_GOLD, beak, 2)

    # ── Leg-bones — gilded struts with knee knobs, each carrying a 1px dark
    #    separation from the body so they don't smear into a bright foot-band.
    for (kx, ky), (fx, fy) in (((28, 44), (27, 49)), ((34, 44), (35, 49))):
        pygame.draw.line(surf, _AU_BODY_D, (kx - 1, ky), (fx - 1, fy), 1)
        _gild_bone_line(surf, (kx, ky), (fx, fy), 2)
        _gild_knob(surf, (kx, ky), 1)

    # ── Cursed hoard — ONE clear gold coin disc at the feet (1px dark keyline,
    #    no pale highlight dots, no glow) so nothing at the feet competes with
    #    the skull for brightness or reads as a speckled band at 40px.
    pygame.draw.circle(surf, _AU_BODY_D, (31, 51), 4)        # dark keyline
    pygame.draw.circle(surf, _AU_GOLD_D, (31, 51), 3)
    pygame.draw.circle(surf, _AU_GOLD, (31, 51), 2)

    return surf


def _make_build(night):
    """Build a prebuilt-skin getter at a fixed NIGHT factor (the render harness
    asks for a near-silent day variant and a blazing night variant)."""
    def _bf(angle, _n=night):
        global NIGHT
        prev = NIGHT
        NIGHT = _n
        try:
            return _build_design5(angle)
        finally:
            NIGHT = prev
    return _make_prebuilt_skin(_bf)


# The scratch candidate the render harness consumes (build(frame_idx, tilt)).
# Default `build` is the night variant (full blaze) for the live-style preview;
# the render sheet uses the explicit day/night variants below.
build = _make_build(1.0)
build_day = _make_build(0.0)
build_night = _make_build(1.0)
