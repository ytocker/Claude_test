"""AUREX — Cursed Gold-Lich Skeleton (skeleton redesign, design_5).

Scratch exploration ONLY — never registered in store_skins.BUILDERS, never
wired into production. The premium showpiece: gilded gold bone over a deep
void-violet body, a dark tattered mantle breaking the silhouette behind the
shoulders, and violet rune-fire blazing in the eye sockets.

The gold reads as the brightest, highest-contrast element (highlight #FFE27A
over body #E0A21E) so the skeleton survives the 40px downscale; the violet
rune-fire is rendered as an additive bloom on its own SRCALPHA layer and
BLEND_RGB_ADD-blitted so it blazes on the night sky without muddying the gold
on the day sky. Bone strokes are 2px minimum.
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
_AU_MANTLE  = (28, 22, 40)         # tattered hood/collar (a touch above body)
_AU_MANTLE_D = (16, 12, 26)
_AU_SOCK    = (10, 6, 18)          # socket void behind the rune-fire
_AU_RUNE_C  = (179, 136, 255)      # violet rune-fire core  (#B388FF)
_AU_RUNE_M  = (122, 77, 224)       # violet rune-fire mid   (#7A4DE0)


def _add_glow(surf, layer):
    """Composite an additive bloom layer so violet rune-fire reads as light,
    not paint — blazes on the night sky, stays gentle on the bright day sky."""
    surf.blit(layer, (0, 0), special_flags=pygame.BLEND_RGB_ADD)


def _rune_bloom(cx, cy, r, intensity=1.0):
    """A soft round violet bloom (returns its own SRCALPHA tile to ADD-blit).
    Layered rings fade from the bright #B388FF core out through #7A4DE0."""
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
    the tips on the swept poses so the flap clatters with necromantic light."""
    w = pygame.Surface((50, 50), pygame.SRCALPHA)

    # Dark void web so the gold finger-bones read as bone, not floating lines.
    web = [(24, 26), (46, 14), (50, 30), (34, 44), (18, 40)]
    _poly(w, _AU_BODY, web)
    pygame.draw.polygon(w, _AU_BODY_D, web, 1)

    # Violet rune-glow trailing the finger-tips (additive) — stronger as the
    # wing sweeps up (the "flap" energy). Drawn before the bones so the bone
    # edges sit crisp on top of the bloom.
    glow = pygame.Surface((50, 50), pygame.SRCALPHA)
    trail = 0.45 + 0.55 * max(0.0, math.sin(math.radians(angle_deg)))
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
    """AUREX gold-lich skeleton: dark mantle (behind), void body + gold tail,
    gold finger-bone wing, gold ribcage + spine, gilded rune-eyed skull with a
    coin crown-band and gold-tooth grin, gold legs over a small coin hoard."""
    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)

    # ── Mantle layer (BEHIND everything) — a dark tattered hood rising past the
    #    crown and draping behind the shoulders; the lich silhouette anchor.
    mantle = [
        (50, 8),                       # hood peak rising past the crown
        (60, 16), (60, 30),            # near shoulder drape
        (54, 40),                      # tattered hem notch
        (47, 32),
        (38, 42),                      # tattered hem notch
        (33, 30),
        (24, 40),                      # far shoulder tatter
        (28, 22),
        (40, 10),                      # collar sweeping back up to the hood
    ]
    _poly(surf, _AU_MANTLE_D, [(x + 1, y + 1) for x, y in mantle])
    _poly(surf, _AU_MANTLE, mantle)
    # Faint violet inner rim where the hood frames the skull (cursed light).
    inner_glow = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    b, off = _rune_bloom(48, 18, 9, intensity=0.35)
    inner_glow.blit(b, off, special_flags=pygame.BLEND_RGB_ADD)
    _add_glow(surf, inner_glow)

    # ── Tail — void fan with a gilded leading edge.
    tail = [(2, 26), (17, 24), (23, 36), (12, 42)]
    _poly(surf, _AU_BODY, tail)
    pygame.draw.polygon(surf, _AU_BODY_D, tail, 1)
    _gild_bone_line(surf, (4, 28), (21, 25), 2)

    # ── Body — deep void ellipse (the dark flesh the gold bone sits on).
    _aaellipse(surf, _AU_BODY_D, (33, 33), 19, 14)
    _aaellipse(surf, _AU_BODY, (32, 32), 18, 13)

    # ── Ribcage — gold rib-arcs with a faint violet inner glow between them.
    rib_glow = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    b, off = _rune_bloom(30, 33, 8, intensity=0.30)
    rib_glow.blit(b, off, special_flags=pygame.BLEND_RGB_ADD)
    _add_glow(surf, rib_glow)
    # Gold vertebra SPINE down the chest centre.
    spine = [(38, 25), (34, 29), (30, 33), (26, 37), (22, 40)]
    for i in range(len(spine) - 1):
        _gild_bone_line(surf, spine[i], spine[i + 1], 2)
    for vx, vy in spine:
        _gild_knob(surf, (vx, vy), 1)
    # Paired gold rib-arcs sweeping off the spine.
    for off_x in (-5, 0, 5):
        rect = (24 + off_x, 24, 13, 16)
        pygame.draw.arc(surf, _AU_GOLD_D, rect,
                        math.radians(200), math.radians(340), 3)
        pygame.draw.arc(surf, _AU_GOLD, rect,
                        math.radians(200), math.radians(340), 2)
        pygame.draw.arc(surf, _AU_GOLD_H, (rect[0], rect[1] - 1, rect[2], rect[3]),
                        math.radians(205), math.radians(330), 1)

    # ── Wing — gold finger-bones (drawn over the ribs so it reads as the near
    #    wing) with its violet rune-trail.
    wing = _au_wing(wing_angle_deg)
    surf.blit(wing, wing.get_rect(center=(34, 28)).topleft)

    # ── Skull base — gilded gold dome at the head anchor.
    _aaellipse(surf, _AU_GOLD_D, (48, 22), 11, 10)
    _aaellipse(surf, _AU_GOLD, (47, 21), 10, 9)
    # Top-left metallic highlight crescent for the gilded sheen.
    _aaellipse(surf, _AU_GOLD_H, (44, 17), 5, 3)
    # Jaw shadow + gold-tooth grin line below the sockets.
    _aaellipse(surf, _AU_GOLD_D, (47, 26), 6, 3)

    # ── Eye sockets — void holes filled with violet rune-fire (additive bloom).
    pygame.draw.circle(surf, _AU_SOCK, (50, 20), 3)
    pygame.draw.circle(surf, _AU_SOCK, (44, 21), 3)
    sock_glow = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    for sc in ((50, 20), (44, 21)):
        b, off = _rune_bloom(sc[0], sc[1], 4, intensity=1.0)
        sock_glow.blit(b, off, special_flags=pygame.BLEND_RGB_ADD)
    _add_glow(surf, sock_glow)
    # Bright rune pips dead-centre of each socket (the hard light source).
    pygame.draw.circle(surf, _AU_RUNE_C, (50, 20), 1)
    pygame.draw.circle(surf, _AU_RUNE_C, (44, 21), 1)
    # 1–2 tiny violet rune glyphs flanking the sockets (the hero tell).
    pygame.draw.line(surf, _AU_RUNE_C, (53, 17), (53, 21), 1)
    pygame.draw.line(surf, _AU_RUNE_C, (52, 19), (54, 19), 1)   # a "+" rune
    pygame.draw.line(surf, _AU_RUNE_C, (41, 18), (40, 22), 1)   # a slash rune

    # Nose hollow + gold-tooth grin (2px gold teeth so they survive downscale).
    _poly(surf, _AU_SOCK, [(47, 24), (49, 24), (48, 26)])
    for gx in (44, 47, 50):
        pygame.draw.line(surf, _AU_GOLD_H, (gx, 28), (gx, 30), 2)
        pygame.draw.line(surf, _AU_GOLD_D, (gx + 1, 28), (gx + 1, 30), 1)

    # ── Crown-band / coin across the brow — a gold band with a coin medallion.
    pygame.draw.line(surf, _AU_GOLD_D, (40, 15), (54, 15), 3)
    pygame.draw.line(surf, _AU_GOLD, (40, 14), (54, 14), 2)
    pygame.draw.line(surf, _AU_GOLD_H, (41, 13), (53, 13), 1)
    # Brow coin medallion (the cursed-hoard tell on the head).
    pygame.draw.circle(surf, _AU_GOLD_D, (47, 14), 3)
    pygame.draw.circle(surf, _AU_GOLD, (47, 14), 2)
    pygame.draw.circle(surf, _AU_GOLD_H, (46, 13), 1)

    # ── Beak — gold-rimmed bone over a void beak.
    beak = [(55, 21), (61, 24), (58, 28), (52, 26)]
    _poly(surf, _AU_BODY, beak)
    pygame.draw.polygon(surf, _AU_GOLD_D, beak, 3)
    pygame.draw.polygon(surf, _AU_GOLD, beak, 2)

    # ── Leg-bones — gilded struts with knee knobs.
    _gild_bone_line(surf, (28, 44), (27, 49), 2)
    _gild_bone_line(surf, (34, 44), (35, 49), 2)
    _gild_knob(surf, (28, 44), 1)
    _gild_knob(surf, (34, 44), 1)

    # ── Cursed hoard — a couple of gold coins / small treasure at the feet.
    for cx, cy, rr in ((25, 51, 3), (31, 52, 2), (37, 51, 3)):
        pygame.draw.circle(surf, _AU_GOLD_D, (cx, cy), rr)
        pygame.draw.circle(surf, _AU_GOLD, (cx, cy), max(1, rr - 1))
        pygame.draw.circle(surf, _AU_GOLD_H, (cx - 1, cy - 1), 1)
    # A faint warm glint where the hoard catches the rune-light.
    hoard_glow = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    b, off = _rune_bloom(31, 51, 5, intensity=0.25)
    hoard_glow.blit(b, off, special_flags=pygame.BLEND_RGB_ADD)
    _add_glow(surf, hoard_glow)

    return surf


# The scratch candidate the render harness consumes (build(frame_idx, tilt)).
build = _make_prebuilt_skin(_build_design5)
