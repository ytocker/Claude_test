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
    rib=(224, 162, 30),
)

# Mantle pulled to a DARK anchor (#16121F) with saturation ~halved so the upper
# silhouette reads as a dark hood SHAPE, never a violet glow; its only framing
# is a thin gold-dark rim so it reads as ATTACHED behind the gold, not a cloud.
_MANTLE   = (22, 18, 31)          # #16121F-family tattered hood, near-body value
_MANTLE_D = (15, 12, 22)          # depth fold
_MANTLE_RIM = (74, 54, 18)        # gold-dark collar rim framing the hood
_VIOLET_C = (184, 120, 255)       # violet rune-fire core  (#B878FF)
_VIOLET_M = (120, 74, 220)        # violet rune-fire mid
_GOLD_H   = (255, 248, 210)       # gold highlight (crown band, coin glint)

# Module-level night factor: scales every NON-socket bloom so the gold skeleton
# carries the day-sky read with near-zero glow, and the violet only blazes at
# night. The two socket pips stay lit day AND night (the constant lich tell),
# but tight enough that the re-gilded gold around them always wins the read.
NIGHT = 1.0


def _mantle(surf, angle_deg, P):
    """A DARK tattered mantle behind the shoulders only — a flat dark SHAPE that
    breaks the silhouette, kept small (near-shoulder collar + one thin drape) and
    well below the gold value so the gold skull/ribs define the upper read. A
    1px gold-dark rim along the leading edge frames it as an attached hood."""
    drape = [
        (40, 11),            # collar peak tucked behind the crown
        (47, 16), (47, 27),  # tight near-shoulder collar
        (41, 35),            # tattered hem notch
        (35, 28),
        (29, 36),            # one thin tattered drape
        (24, 28),            # far-shoulder tatter, pulled in
        (27, 19),
    ]
    _poly(surf, _MANTLE_D, [(x + 1, y + 1) for x, y in drape])
    _poly(surf, _MANTLE, drape)
    pygame.draw.lines(surf, _MANTLE_RIM, False,
                      [(27, 19), (40, 11), (47, 16), (47, 27)], 1)


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

    # ONE clean gold coin disc at the feet (dark keyline, single glint, no
    # speckle) so nothing at the feet competes with the skull or reads as noise.
    pygame.draw.circle(surf, P.body_deep, (30, 53), 4)
    pygame.draw.circle(surf, P.bone_deep, (30, 53), 3)
    pygame.draw.circle(surf, P.bone, (30, 53), 2)
    pygame.draw.circle(surf, _GOLD_H, (29, 52), 1)


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
