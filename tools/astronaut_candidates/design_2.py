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
_GLASS_LIT  = (214, 230, 244, 120)  # lighter core behind the face → dark-on-light
_GLASS_RIM  = (224, 240, 252)       # bright dome rim
_BEAK       = (255, 196, 64)        # saturated horn-yellow beak inside the dome
_PATCH_BLUE = (38, 78, 150)         # mission-patch field
_STAR       = (255, 232, 150)       # patch star + visor band


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
    # ── WHITE survival pack on the BACK, drawn FIRST so the body sits in front
    #    and it reads as a separate mass bulging behind the shoulder. Pushed a
    #    couple px FURTHER into open sky (sky-side edge clear of the body) and
    #    wrapped in a hard DARK keyline so it holds as its own block on BOTH
    #    biomes instead of washing into the orange/white.
    px0, py0 = HX - 27, HY - 5
    pygame.draw.rect(surf, _DARK, (px0 - 1, py0 - 1, 18, 25), border_radius=7)
    pygame.draw.rect(surf, _WHITE_D, (px0, py0, 16, 23), border_radius=6)
    pygame.draw.rect(surf, _WHITE, (px0 + 1, py0 + 1, 13, 20), border_radius=5)
    pygame.draw.rect(surf, _GRAY_H, (px0 + 2, py0 + 2, 4, 17), border_radius=3)
    # Two pack straps arcing over the shoulder onto the chest.
    pygame.draw.line(surf, _WHITE_D, (px0 + 12, py0 + 4), (HX - 2, HY + 9), 4)
    pygame.draw.line(surf, _WHITE, (px0 + 12, py0 + 4), (HX - 2, HY + 9), 2)
    pygame.draw.line(surf, _WHITE_D, (px0 + 13, py0 + 13), (HX + 2, HY + 13), 4)
    pygame.draw.line(surf, _WHITE, (px0 + 13, py0 + 13), (HX + 2, HY + 13), 2)

    # ── BODY suit detail (over the orange base): ONLY the WHITE vertical chest
    #    zip — the belly segment rings + comms dot + zip-stitch dots were chest
    #    confetti that turned to noise at 40px, so they're cut. Body centre is
    #    ~(32, 52) in composite space.
    bcx, bcy = 32, 52
    pygame.draw.line(surf, _WHITE_D, (bcx + 1, bcy - 11), (bcx + 1, bcy + 9), 3)
    pygame.draw.line(surf, _WHITE, (bcx, bcy - 11), (bcx, bcy + 9), 1)

    # ── CHEST mission patch: a single FLAT coloured disc with one bright star —
    #    the double ring + connector dot read as a smear when shrunk, so it's a
    #    clean badge now.
    mx, my = bcx + 6, bcy - 5
    pygame.draw.circle(surf, _DARK, (mx, my), 5)
    pygame.draw.circle(surf, _PATCH_BLUE, (mx, my), 4)
    store_skins._star5(surf, mx, my, 3, _STAR)

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
    # LIGHTEN the glass directly behind the face so the dark eye/beak read as
    # dark-on-light, not gray-on-gray — a brighter inner core under the upper
    # sphere. Clip both fills to the upper sphere so the open port shows the bird.
    pygame.draw.circle(dome, _GLASS_LIT, (r + 2, r), r - 3)
    cut = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
    pygame.draw.rect(cut, (255, 255, 255, 255), (0, 0, r * 2 + 4, r + 6))
    dome.blit(cut, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(dome, (cx - r - 2, cy - r - 2))

    # Repaint the bare friendly macaw eye INSIDE the glass, ENLARGED so the face
    # is the brightest highest-contrast thing in the dome: pure-white sclera +
    # dark pupil = the unmistakable focal point at 40px.
    ex, ey = HX + 3, HY - 2
    _aaellipse(surf, (255, 255, 255), (ex, ey), 6, 6)
    pygame.draw.circle(surf, (20, 16, 22), (ex + 1, ey), 4)
    pygame.draw.circle(surf, (4, 3, 6), (ex + 1, ey), 4, 1)
    pygame.draw.circle(surf, (255, 255, 255), (ex - 1, ey - 1), 1)
    # 2px saturated horn-yellow beak so the friendly face reads as a beaked bird.
    pygame.draw.line(surf, _BEAK, (HX + 7, HY + 1), (HX + 13, HY + 2), 2)

    # Thin DARK outer keyline so the glass sphere holds its circle against the
    # bright day sky, then the bright crisp inner rim + the single shine arc.
    pygame.draw.circle(surf, _DARK, (cx, cy), r + 1, 1)
    pygame.draw.circle(surf, _GLASS_RIM, (cx, cy), r, 2)
    pygame.draw.arc(surf, (255, 255, 255), (cx - r + 3, cy - r + 3, r, r),
                    math.radians(60), math.radians(160), 2)

    # #1 FIX: a hard DARK shadow line under the dome's lower rim so the bubble
    # does NOT merge with the white neck ring below it into one mushy blob —
    # this is the seam that separates the two white-ish masses at 40px.
    pygame.draw.arc(surf, _DARK, (cx - r, cy - r + 1, r * 2, r * 2),
                    math.radians(200), math.radians(340), 2)

    # The flipped-UP visor: ONE thick gold band standing clearly ABOVE the dome
    # crown, detached, with a dark sliver under it — reads as "visor raised",
    # not a fried-egg halo of thin strokes crushed onto the glass.
    vb = (cx - r + 2, cy - r - 6, (r - 2) * 2, r)
    pygame.draw.arc(surf, _DARK, vb, math.radians(30), math.radians(150), 2)
    pygame.draw.arc(surf, _ORANGE_D, (vb[0], vb[1] - 2, vb[2], vb[3]),
                    math.radians(28), math.radians(152), 5)
    pygame.draw.arc(surf, _STAR, (vb[0], vb[1] - 2, vb[2], vb[3]),
                    math.radians(32), math.radians(148), 3)


build = store_skins._make_skin(_paint, base_fn=_orange_base)
