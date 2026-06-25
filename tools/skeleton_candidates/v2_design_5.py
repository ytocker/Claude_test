"""v2_design_5 — AUREX-MACAW: cursed gold-lich parrot skeleton.

The ``_v2_anatomy`` parrot skeleton (hooked bone beak + long tail) gilded in
gold so the GOLD SKELETON is the single brightest legible mass. Two hot violet
rune-fire socket points burn inside the gold skull; a DARK tattered mantle sits
behind the shoulders (a dark silhouette, value well below the gold — NOT a
violet glow); a gold crown band rides the brow; one clean gold coin sits at the
feet. Scratch only — never registered in ``store_skins.BUILDERS``.

Read order at 40px, by construction: GOLD SKULL + HOOKED BEAK (brightest mass)
→ two hot violet socket points → gold crown band → long gold tail. The violet
is the ONLY hot non-gold colour on the bird and it is confined to the two
sockets; every other bloom is gated by ``NIGHT`` so the gold carries the whole
read on the day sky with almost no glow assist, and only blazes at night.
"""
import pygame

from game.store_skins import _make_prebuilt_skin, _poly
from tools.skeleton_candidates import _v2_anatomy as A


# Gilded bone over a near-black void flesh; the gold bone is the brightest
# element. ``keyline`` is a warm-dark gold rim (#3C2808-ish) so the bright gold
# survives crisp against bright blue day sky without going pale.
P = A.Pal(
    bone=(255, 226, 122), bone_sh=(214, 150, 26), bone_deep=(140, 92, 12),
    body=(20, 17, 13), body_deep=(12, 10, 8), keyline=(48, 32, 8),
    socket=(20, 8, 26), glint=(255, 246, 206),
    # Kill the shared smeary rib arcs by pulling ``rib`` down to the body floor;
    # this design re-draws ~3 clean two-tone rib arcs locally in ``_ribs`` so the
    # torso reads as a few crisp ribs, not gold noise, and the spine stays the
    # brightest vertical.
    rib=(22, 18, 14),
)

# Mantle is a TATTERED dark cape SHAPE, not a void: a torn cloth hem with jagged
# downward points, rimmed on its outer leading edge AND its bottom hem with a 1px
# deep-gold keyline so the dark silhouette holds against the sky instead of
# dissolving into it. Body value is lifted off the floor (≈(34,28,46)) so the
# bottom no longer pools into one dark mass that reads as a hole on the bright
# day sky. Contained behind the shoulders only, shrunk so it never bulges below
# the spine line or competes with the tail's negative space.
_MANTLE   = (34, 28, 46)          # lifted tattered hood body (off the void floor)
_MANTLE_D = (22, 18, 31)          # depth fold behind the points
_MANTLE_RIM = (224, 162, 30)      # deep-gold (#E0A21E) edge keyline
_DEEP_GOLD = (224, 162, 30)       # #E0A21E rib/coin core gold
_TOP_HI   = (255, 226, 122)       # #FFE27A bone/rib top-edge highlight
_VIOLET_C = (184, 120, 255)       # violet rune-fire core  (#B878FF)
_VIOLET_M = (120, 74, 220)        # violet rune-fire mid
_GOLD_H   = (255, 248, 210)       # gold highlight (crown band, coin glint)

# Module-level night factor: scales every NON-socket bloom so the gold skeleton
# carries the day-sky read with near-zero glow, and the violet only blazes at
# night. The two socket pips stay lit day AND night (the constant lich tell),
# but tight enough that the re-gilded gold around them always wins the read.
NIGHT = 1.0


def _mantle(surf, angle_deg, P):
    """A TATTERED dark cape behind the shoulders — a torn cloth hem (3-4 jagged
    downward points) in #16121F, NOT a black void. Its outer leading edge carries
    a 1px deep-gold (#E0A21E) keyline so the dark shape holds against the night
    sky instead of reading as a hole. Contained to the upper-right shoulder/nape
    block: it never crosses the spine line (back at y>=33) or the tail, so the
    gold skull/spine/tail own the read and the mantle is a quiet cape behind."""
    # Collar peak tucked behind the crown, down the nape, then a torn hem of
    # three triangular points; the leftmost point stops short of the back so the
    # spine + tail stay clear of the cape. The hem points are raised ~2-3px and
    # the collar tightened (shoulder edge pulled in from y23→y21) so the cape is a
    # collar-and-hem HINT behind the shoulders, not a slab bulging below the
    # spine line — it must not compete with the tail's negative space.
    drape = [
        (40, 10),                       # collar peak behind the crown
        (48, 15), (48, 21),             # tighter near-shoulder collar edge
        (44, 27), (43, 22),             # point 1 (tatter, raised) + notch
        (38, 28), (37, 23),             # point 2 (raised) + notch
        (33, 27), (32, 22),             # point 3 (innermost, raised) + notch
        (30, 16),                       # nape rise back up to the collar
    ]
    _poly(surf, _MANTLE_D, [(x + 1, y + 1) for x, y in drape])
    _poly(surf, _MANTLE, drape)
    # Deep-gold keyline along BOTH the outer leading edge (collar) AND the bottom
    # hem (the tatter tips) so the cape's lower boundary carries an edge instead
    # of dissolving into the sky as a dark hole; the inner notches stay unlit dark
    # so the points still read as torn cloth.
    pygame.draw.lines(surf, _MANTLE_RIM, False,
                      [(30, 16), (40, 10), (48, 15), (48, 21), (44, 27)], 1)
    pygame.draw.lines(surf, _MANTLE_RIM, False,
                      [(44, 27), (38, 28), (33, 27)], 1)


def _ribs(surf):
    """Three CLEAN rib arcs on the chest (the shared smeary rib pass is killed via
    P.rib): each is a deep-gold (#E0A21E) core stroke with a single #FFE27A
    top-edge highlight, separated by 1px #16121F gaps so they read as discrete
    ribs, not a gold smear. Hung off the sternum BELOW the spine line so the
    continuous spine stays the brightest vertical (skull→tail tracks clean)."""
    import math as _m
    # (rect, start_deg, end_deg) for the three sweeping ribs, descending the chest
    # forward of the wing; arcs open downward off the sternum.
    arcs = [
        ((25, 28, 13, 11), 22, 150),
        ((23, 33, 13, 11), 26, 154),
        ((21, 38, 13, 11), 30, 158),
    ]
    for (rx, ry, rw, rh), a0, a1 in arcs:
        rect = (rx, ry, rw, rh)
        # 1px dark gap-rim under the core keeps neighbouring ribs from fusing.
        pygame.draw.arc(surf, _MANTLE, (rx, ry + 1, rw, rh),
                        _m.radians(a0), _m.radians(a1), 2)
        pygame.draw.arc(surf, _DEEP_GOLD, rect,
                        _m.radians(a0), _m.radians(a1), 2)
        pygame.draw.arc(surf, _TOP_HI, (rx, ry - 1, rw, rh),
                        _m.radians(a0 + 8), _m.radians(a1 - 8), 1)


def _socket_bloom(cx, cy, r, intensity):
    """A TIGHT violet bloom that stays INSIDE the socket — a hot point in a gold
    face, never a face-wide haze (no outer halo ring)."""
    box = max(2, r * 4)
    g = pygame.Surface((box, box), pygame.SRCALPHA)
    gc = box // 2
    for rad, a in (
        (r * 1.1, 72), (r * 0.7, 160), (r * 0.4, 235),
    ):
        col = (*_VIOLET_M, min(255, int(a * intensity))) if rad > r else \
              (*_VIOLET_C, min(255, int(a * intensity)))
        pygame.draw.circle(g, col, (gc, gc), max(1, int(rad)))
    return g, (cx - gc, cy - gc)


def _runes(surf, angle_deg, P):
    """On-top theme: the contained violet socket fire (the ONLY hot violet on the
    bird), a gold crown band across the brow, and one clean gold coin disc at the
    feet. The gold dome/socket-rim from the anatomy already sit under this; we
    re-punch the socket void + drop the hot pip so the gold all around stays gold
    and only the two cores glow."""
    # Three clean two-tone rib arcs on the chest (shared smear killed via P.rib),
    # then re-assert the spine as the single brightest vertical over them so the
    # eye tracks an unbroken skull→tail backbone past the ribs.
    _ribs(surf)
    spine_path = [(41, 24), (37, 27), (33, 30), (28, 33), (23, 35), (18, 35)]
    pygame.draw.lines(surf, P.keyline, False, spine_path, 3)
    pygame.draw.lines(surf, _TOP_HI, False, spine_path, 1)
    for vx, vy in spine_path:
        pygame.draw.circle(surf, _TOP_HI, (vx, vy), 1)

    # Re-gild a crisp dark socket rim around the anatomy's eye socket so the
    # violet core reads as fire inside a GOLD ring, not a smear on the cheek.
    sock = (45, 16)
    pygame.draw.circle(surf, P.bone_deep, sock, 4, 1)   # gold-dark rim
    pygame.draw.circle(surf, (16, 6, 20), sock, 3)      # dark void
    pygame.draw.circle(surf, _VIOLET_C, sock, 1)        # hard hot pip

    # The contained socket bloom — lit day AND night (constant lich tell), but
    # tight; a touch hotter at night. Additive so it reads as light, not paint.
    glow = pygame.Surface((A.SPRITE_W, A.SPRITE_H), pygame.SRCALPHA)
    b, off = _socket_bloom(sock[0], sock[1], 2, intensity=0.65 + 0.45 * NIGHT)
    glow.blit(b, off, special_flags=pygame.BLEND_RGB_ADD)
    surf.blit(glow, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    # Gold crown band across the brow — one clean gold horizontal band at the
    # dome-highlight value with a thin DARK under-keyline so it stays the third
    # legible read at 40px instead of melting into the cranium. A small brow
    # coin medallion (the cursed-hoard tell on the head).
    pygame.draw.line(surf, P.body_deep, (39, 11), (53, 11), 1)   # dark under-key
    pygame.draw.line(surf, _GOLD_H,     (39, 9),  (53, 9),  2)   # bright band
    pygame.draw.circle(surf, P.body_deep, (46, 9), 3, 1)
    pygame.draw.circle(surf, P.bone, (46, 9), 2)
    pygame.draw.circle(surf, _GOLD_H, (45, 8), 1)

    # ONE clean round gold coin disc at the feet — unmistakably a coin, not a
    # bone nub: solid #E0A21E fill inside a 1px #16121F keyline, with a #FFE27A
    # upper-left rim-light arc matching the bone/rib highlight direction.
    import math as _m
    coin = (30, 53)
    pygame.draw.circle(surf, _MANTLE, coin, 4)            # 1px dark keyline
    pygame.draw.circle(surf, _DEEP_GOLD, coin, 3)         # solid gold fill
    pygame.draw.arc(surf, _TOP_HI, (coin[0] - 3, coin[1] - 3, 6, 6),
                    _m.radians(60), _m.radians(200), 1)   # upper-left rim-light


def _build(wing_angle_deg):
    return A.build_skeleton(wing_angle_deg, P, pre=_mantle, post=_runes,
                            socket_fill=(40, 16, 56))


def _make_build(night):
    """Build a prebuilt-skin getter at a fixed NIGHT factor (the render harness
    asks for a near-silent day variant and a blazing night variant)."""
    def _bf(angle, _n=night):
        global NIGHT
        prev = NIGHT
        NIGHT = _n
        try:
            return _build(angle)
        finally:
            NIGHT = prev
    return _make_prebuilt_skin(_bf)


# Default `build` is the night variant (full blaze) for the live-style preview;
# the render sheet uses the explicit day/night variants below.
build = _make_build(1.0)
build_day = _make_build(0.0)
build_night = _make_build(1.0)
