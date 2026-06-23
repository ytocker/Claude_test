"""PUMPKIN SUIT — orange Apollo/launch-entry astronaut candidate for the
ASTRONAUT redraw.

Scratch exploration only; NOT registered in store_skins.BUILDERS, so the live
``skin_astronaut`` is untouched.

The live astronaut reads as a cool blue-steel EVA helmet on the scarlet bird.
This concept goes the OTHER way for maximum sky contrast and a distinct
identity: the cheerful "ready for launch" rookie in a full bright-ORANGE
pressure suit — the only warm/orange skin in the roster, unmistakable next to
a white EVA.

The body is re-plumaged solid launch-orange through the 24-slot palette system
(the way the ninja/viking/disco skins recolour the whole macaw), so the suit
is REAL fabric, not a few orange patches on a scarlet bird. The friendly macaw
face stays VISIBLE: the helmet is a CLEAR fishbowl dome with the visor UP, so
Pip's eye + beak read clearly inside the glass (only one curved white shine arc
on the dome), seated on a fat WHITE pressure-neck ring that separates the
orange body from the clear bubble.

At 40px the read is, in order: (1) a warm orange bird-shaped mass — the only
orange in the sky; (2) the white neck-ring + white survival pack breaking the
shoulder line so it's clearly suited, not painted; (3) the clear dome with the
friendly face inside; (4) the white chest zip + mission patch as the suit
detail. Objects are layered ALL OVER — head dome, neck ring, back pack, chest
zip + patch + comms dot, belly segment rings, glove wingtips, boot feet, wing
stripe — each held to mass + one accent so the stack survives the downscale.
"""
import math
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, PARROT_DY, _poly
from game.parrot import _aaellipse
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette


# Launch-orange suit family. The body floods to suit-orange with a deep orange
# shadow for form; the white slots (ring/pack/zip) carry the high-value read,
# gray slots are the gloves/segments, and dark navy is the visor-glass tint and
# the boots — the only near-black, so nothing reads as a void on night sky.
_ORANGE     = (242, 106, 27)        # #F26A1B suit orange
_ORANGE_D   = (194, 78, 15)         # #C24E0F orange shadow
_ORANGE_H   = (255, 150, 80)        # lifted highlight plane
_WHITE      = (242, 244, 248)       # #F2F4F8 neck-ring / pack / zip
_WHITE_D    = (196, 202, 214)       # white shadow so stacked whites separate
_GRAY       = (154, 161, 173)       # #9AA1AD gloves / segment rings
_GRAY_D     = (104, 110, 122)
_GRAY_H     = (206, 211, 220)
_DARK       = (30, 35, 48)          # #1E2330 visor-glass tint / boots
_GLASS      = (150, 178, 205, 90)   # clear fishbowl fill (translucent)
_GLASS_RIM  = (224, 240, 252)       # bright dome rim
_PATCH_BLUE = (38, 78, 150)         # mission-patch field
_PATCH_RED  = (206, 64, 40)         # patch ring
_STAR       = (255, 232, 150)       # patch star + comms glint
_COMMS      = (188, 194, 204)       # silver comms connector


# Full launch-orange re-plumage of the macaw. The beak stays warm horn so the
# friendly face reads inside the dome; the foot is darkened toward the boot
# tone. Lenses are dropped — the bare macaw eye is painted back on inside the
# helmet in _paint so the face stays the cheerful rookie, not a goggled pilot.
_PUMPKIN_PAL = _pal(
    tail=[(168, 64, 14), (190, 76, 18), (214, 92, 26), (240, 112, 40)],
    tail_line=(120, 46, 10),
    body_shadow=(150, 58, 12),
    body_main=_ORANGE,
    body_chest=(255, 138, 64),
    body_belly=(214, 92, 26),
    sheen=(255, 220, 180, 90),
    wing_main=(214, 92, 24),
    wing_dark=(150, 58, 12),
    wing_tip=(255, 150, 88),
    wing_secondary=None,
    wing_highlight=(255, 178, 120),
    head_shadow=(150, 58, 12),
    head_main=_ORANGE,
    head_cheek=(255, 138, 70),
    head_crown=(255, 150, 80),
    lens_frame=(150, 58, 12),
    lens_body=(120, 46, 10),
    lens_tint=None,
    lens_glint=None,
    beak_main=(255, 196, 92),
    beak_dark=(176, 116, 40),
    beak_gloss=(255, 238, 180),
    foot=(60, 64, 78),
)


def _orange_base(angle_deg):
    # Orange suited bird with no aviators — the clear dome owns the head and the
    # bare macaw eye is repainted inside it so the face stays friendly.
    return _build_parrot_with_palette(angle_deg, _PUMPKIN_PAL, draw_lenses=False)


def _paint(surf, _a):
    # ── WHITE survival/parachute pack on the BACK, above + behind the shoulders
    #    (drawn FIRST so the body sits in front of it and it reads as a pack
    #    bulging out behind). Rounded squarish, softer than a hard EVA PLSS so it
    #    stays distinct from the white-EVA skin. Sky-side edge breaks the back
    #    silhouette into open sky.
    px0, py0 = HX - 24, HY - 4
    pygame.draw.rect(surf, _WHITE_D, (px0 - 1, py0 - 1, 18, 24), border_radius=7)
    pygame.draw.rect(surf, _WHITE, (px0, py0, 16, 22), border_radius=6)
    pygame.draw.rect(surf, _GRAY_H, (px0 + 2, py0 + 2, 5, 18), border_radius=3)
    # Two pack straps arcing over the shoulder onto the chest.
    pygame.draw.line(surf, _WHITE_D, (px0 + 12, py0 + 3), (HX - 2, HY + 9), 4)
    pygame.draw.line(surf, _WHITE, (px0 + 12, py0 + 3), (HX - 2, HY + 9), 2)
    pygame.draw.line(surf, _WHITE_D, (px0 + 13, py0 + 12), (HX + 2, HY + 13), 4)
    pygame.draw.line(surf, _WHITE, (px0 + 13, py0 + 12), (HX + 2, HY + 13), 2)

    # ── BODY suit detail (over the orange base): a WHITE vertical zip line down
    #    the chest centre + gray segment rings at the belly. Body centre is
    #    ~(32, 52) in composite space.
    bcx, bcy = 32, 52
    # Vertical chest zip.
    pygame.draw.line(surf, _WHITE_D, (bcx + 1, bcy - 11), (bcx + 1, bcy + 9), 3)
    pygame.draw.line(surf, _WHITE, (bcx, bcy - 11), (bcx, bcy + 9), 1)
    for ty in (bcy - 8, bcy - 3, bcy + 2, bcy + 7):
        pygame.draw.circle(surf, _GRAY_D, (bcx, ty), 1)
    # Two gray segment rings curving across the lower belly (suit joints).
    for ry in (bcy + 4, bcy + 8):
        pygame.draw.arc(surf, _GRAY_D, (bcx - 15, ry - 4, 30, 12),
                        math.radians(205), math.radians(335), 3)
        pygame.draw.arc(surf, _GRAY, (bcx - 15, ry - 4, 30, 12),
                        math.radians(205), math.radians(335), 1)

    # ── CHEST mission patch: a small round NASA-ish badge with a tiny star on
    #    the upper chest, plus a short silver comms-connector dot beside it.
    mx, my = bcx + 6, bcy - 6
    pygame.draw.circle(surf, _PATCH_RED, (mx, my), 5)
    pygame.draw.circle(surf, _PATCH_BLUE, (mx, my), 4)
    store_skins._star5(surf, mx, my, 3, _STAR)
    pygame.draw.circle(surf, (255, 255, 255), (mx - 1, my - 1), 1)
    # Silver comms-connector dot just below the patch.
    pygame.draw.circle(surf, _COMMS, (mx - 7, my + 3), 2)
    pygame.draw.circle(surf, _STAR, (mx - 8, my + 2), 1)

    # ── LIMBS: gray/silver gloves at the wingtips, black boots on the feet, a
    #    thin gray stripe on the wing root. Wing root ~(40, 47); the visible
    #    wingtip swings near (50, 44); feet are at ~(26, 49) and (36, 49).
    pygame.draw.line(surf, _GRAY_D, (37, 49), (44, 46), 4)   # wing-root stripe
    pygame.draw.line(surf, _GRAY, (37, 48), (44, 45), 2)
    pygame.draw.circle(surf, _GRAY_D, (50, 45), 3)           # glove cuff
    pygame.draw.circle(surf, _GRAY, (50, 44), 2)
    pygame.draw.circle(surf, _GRAY_H, (49, 43), 1)
    for fx in (26, 36):                                      # boots
        pygame.draw.line(surf, _DARK, (fx, 64), (fx + (fx - 31) // 5, 69), 4)
        pygame.draw.line(surf, _GRAY_D, (fx, 67), (fx + (fx - 31) // 4 + 2, 68), 3)

    # ── WHITE pressure-neck ring: a fat collar separating the orange body from
    #    the clear dome. Drawn before the dome so the dome seats on top of it.
    cx, cy = HX + 1, HY - 1
    pygame.draw.ellipse(surf, _WHITE_D, (cx - 14, cy + 7, 28, 12))
    pygame.draw.ellipse(surf, _WHITE, (cx - 13, cy + 7, 26, 9))
    pygame.draw.ellipse(surf, _GRAY_H, (cx - 11, cy + 8, 22, 3))
    # Two locking-latch nubs on the ring so it reads as a hard pressure seal.
    pygame.draw.circle(surf, _GRAY_D, (cx - 10, cy + 12), 2)
    pygame.draw.circle(surf, _GRAY_D, (cx + 10, cy + 12), 2)

    # ── CLEAR fishbowl helmet, visor UP — a glass dome over the head so Pip's
    #    eye + beak read CLEARLY inside. Translucent fill + one bright rim + one
    #    curved white shine arc; nothing opaque covers the face.
    r = 16
    dome = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
    pygame.draw.circle(dome, _GLASS, (r + 2, r + 2), r)
    # Clip the fill to the upper sphere so the open face-port shows the bird.
    cut = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
    pygame.draw.rect(cut, (255, 255, 255, 255), (0, 0, r * 2 + 4, r + 6))
    dome.blit(cut, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(dome, (cx - r - 2, cy - r - 2))

    # Repaint the bare friendly macaw eye INSIDE the glass so the face stays the
    # cheerful rookie (the base dropped lenses). Matches the macaw eye idiom.
    ex, ey = HX + 3, HY - 2
    _aaellipse(surf, (250, 246, 240), (ex, ey), 5, 5)
    pygame.draw.circle(surf, (32, 26, 30), (ex + 1, ey), 3)
    pygame.draw.circle(surf, (12, 9, 12), (ex + 1, ey), 3, 1)
    pygame.draw.circle(surf, (255, 255, 255), (ex, ey - 1), 1)

    # Bright crisp dome rim (reads the sphere at 40px) + the single curved shine.
    pygame.draw.circle(surf, _GLASS_RIM, (cx, cy), r, 2)
    pygame.draw.arc(surf, (255, 255, 255), (cx - r + 3, cy - r + 3, r, r),
                    math.radians(60), math.radians(160), 2)

    # The flipped-UP visor: a thin gold-tint shell standing above the crown so
    # it reads as "visor raised", not a band across the glass.
    pygame.draw.arc(surf, _ORANGE_D, (cx - r, cy - r - 7, r * 2, r + 4),
                    math.radians(20), math.radians(160), 4)
    pygame.draw.arc(surf, _STAR, (cx - r, cy - r - 7, r * 2, r + 4),
                    math.radians(25), math.radians(155), 2)

    # ── Antenna stub on the dome side — a short white stalk + one bright tip so
    #    the headgear breaks the crown outline into open sky.
    pygame.draw.line(surf, _WHITE, (cx + 12, cy - 9), (cx + 17, cy - 15), 2)
    pygame.draw.circle(surf, _PATCH_RED, (cx + 17, cy - 15), 2)
    pygame.draw.circle(surf, (255, 200, 190), (cx + 16, cy - 16), 1)


build = store_skins._make_skin(_paint, base_fn=_orange_base)
