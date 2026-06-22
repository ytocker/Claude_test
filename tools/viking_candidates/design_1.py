"""STORMBEARD — classic raider berserker candidate for the viking redraw.

Scratch exploration only; NOT registered in store_skins.BUILDERS, so the live
``skin_viking`` is untouched.

The shipped viking is a weak helmet+beard lump that the helmet alone has to
carry. STORMBEARD goes the opposite way: it drowns the whole bird in raider
gear so the read survives a 40px shrink the way the shipped ninja does — by
pushing SIGNATURE shapes past the silhouette on three sides at once:

  * two bold horns sweep up-and-out PAST the crown (the unmistakable read),
  * a round wooden shield slung behind the BODY breaks the back outline,
  * a bearded axe is held OUT past the near wing.

Beyond the silhouette-breakers, every region of the bird carries an object so
the costume reads as full-coverage and not a single hat: spangenhelm dome +
nasal bar on the head, a huge split braided beard with two gold rings ballooning
to the chest, a triangular fur shoulder-mantle ringing the neck, a studded
leather belt on the body, and fur boot cuffs on the legs.

The braid is held cool-dark (#3A2A1B) so it separates from the scarlet plumage
the way the ninja crimson separates on black; the iron helm + bright shield
wedge + gold rings/boss are the high-value notes that carry the 40px read.
"""
import math
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly

# Iron helm — bright cool grey so the dome lifts off the scarlet head.
_IRON    = (123, 135, 148)         # #7B8794
_IRON_D  = (74, 82, 94)
_IRON_H  = (196, 204, 216)
# Fur (mantle + boot cuffs) — warm leather-brown ruff.
_FUR     = (90, 70, 50)            # #5A4632
_FUR_D   = (58, 44, 30)
_FUR_H   = (140, 116, 86)
# Braided beard — cool-dark so it reads OFF the scarlet body.
_BEARD   = (58, 42, 27)            # #3A2A1B
_BEARD_D = (36, 26, 17)
_BEARD_H = (96, 76, 52)
# Shield paint wedge — the bright raider red.
_RED     = (192, 57, 43)           # #C0392B
_RED_D   = (132, 36, 28)
_RED_H   = (228, 110, 96)
# Gold — beard-rings + shield boss + belt buckle glints.
_GOLD    = (227, 178, 60)          # #E3B23C
_GOLD_D  = (170, 128, 34)
_GOLD_H  = (255, 232, 150)
# Wood + horn tones for the planked shield and the helm horns.
_WOOD    = (150, 110, 66)
_WOOD_D  = (104, 74, 42)
_HORN    = (232, 222, 198)
_HORN_D  = (176, 162, 132)


def _paint(surf, wing_angle_deg):
    # The held axe lifts a touch with the wing beat so the raider feels alive;
    # base wing angles run negative on the downbeat, so this nudges the haft.
    swing = int(round(wing_angle_deg * 0.10))

    # ── round wooden shield slung across the BACK (drawn FIRST so the body sits
    #    in front and only the disc's back half breaks the silhouette behind the
    #    bird). Planked wood + iron rim + a bright red painted wedge + an iron
    #    boss dome dead-centre — the back-disc half of the hero read.
    scx, scy = HX - 26, HY + 16     # behind/below the body, out past the back
    sr = 16
    pygame.draw.circle(surf, _IRON_D, (scx, scy), sr + 1)        # iron rim base
    pygame.draw.circle(surf, _WOOD, (scx, scy), sr)              # plank field
    pygame.draw.circle(surf, _WOOD_D, (scx, scy), sr, 1)
    # Bright painted wedge so the disc carries colour at 40px, not just brown.
    _poly(surf, _RED, [(scx, scy), (scx - sr, scy - 6), (scx - sr, scy + 9),
                       (scx - 4, scy + sr)])
    _poly(surf, _RED_H, [(scx - 5, scy - 2), (scx - sr + 2, scy - 4),
                         (scx - sr + 2, scy + 2)])
    # Radial plank seams so the wood reads as a shield, not a flat coin.
    for ang in range(0, 360, 45):
        a = math.radians(ang)
        pygame.draw.line(surf, _WOOD_D, (scx, scy),
                         (scx + (sr - 1) * math.cos(a),
                          scy + (sr - 1) * math.sin(a)), 1)
    pygame.draw.circle(surf, _IRON, (scx, scy), sr, 2)           # bright iron rim
    pygame.draw.circle(surf, _IRON_H, (scx, scy), sr, 1)
    # Iron boss dome centre, with a gold rivet glint — the disc's hero pop.
    pygame.draw.circle(surf, _IRON_D, (scx, scy), 5)
    pygame.draw.circle(surf, _IRON, (scx, scy), 4)
    pygame.draw.circle(surf, _GOLD, (scx, scy), 2)
    pygame.draw.circle(surf, _GOLD_H, (scx - 1, scy - 1), 1)

    # ── bearded axe held OUT past the near wing (drawn under the body edge at the
    #    haft, blade sweeping forward-down past the wing tip). Wooden haft + a
    #    hooked single-blade iron head — the third silhouette-breaker.
    hx0, hy0 = HX + 6, CROWN_Y - 8 + swing   # haft top, up past the crown
    hx1, hy1 = 40, HY + 24                    # haft foot, down past the wing
    pygame.draw.line(surf, _WOOD_D, (hx0, hy0), (hx1, hy1), 4)
    pygame.draw.line(surf, _WOOD, (hx0, hy0), (hx1, hy1), 2)
    pygame.draw.line(surf, _FUR_H, (hx0, hy0 + 1), (hx1, hy1 - 1), 1)
    # Iron axe head near the top of the haft: a bearded (hooked) single blade.
    axx, axy = HX + 12, CROWN_Y - 2 + swing
    head = [(axx - 4, axy - 6), (axx + 9, axy - 4), (axx + 11, axy + 3),
            (axx + 7, axy + 10), (axx + 1, axy + 7), (axx - 3, axy + 2)]
    _poly(surf, _IRON_D, head)
    inner = [(axx - 2, axy - 4), (axx + 7, axy - 2), (axx + 8, axy + 3),
             (axx + 5, axy + 7), (axx + 1, axy + 4)]
    _poly(surf, _IRON, inner)
    # Bright honed edge along the hooked blade so the steel reads at 40px.
    pygame.draw.lines(surf, _IRON_H, False,
                      [(axx + 9, axy - 3), (axx + 11, axy + 3),
                       (axx + 7, axy + 9)], 2)
    pygame.draw.circle(surf, _GOLD, (axx - 1, axy + 1), 2)       # haft langet

    # ── triangular fur shoulder-mantle ringing the neck/shoulders (drawn before
    #    the head so the head + beard sit in front, but the ruff breaks the upper
    #    body outline on both sides). A ring of fur tufts.
    mcx, mcy = HX - 6, HY + 12
    pygame.draw.ellipse(surf, _FUR_D, (mcx - 18, mcy - 5, 34, 18))
    pygame.draw.ellipse(surf, _FUR, (mcx - 17, mcy - 5, 32, 15))
    for i in range(-4, 5):
        tx = mcx + i * 4
        ty = mcy + 8 + (abs(i) % 2) * 2
        _poly(surf, _FUR, [(tx - 3, mcy + 2), (tx + 3, mcy + 2), (tx, ty)])
        _poly(surf, _FUR_D, [(tx - 1, mcy + 4), (tx + 2, mcy + 4),
                             (tx, ty - 1)])
    # A couple of bright fur tips so the ruff doesn't read as a dark slab.
    for i in (-3, 0, 3):
        pygame.draw.line(surf, _FUR_H, (mcx + i * 4, mcy + 2),
                         (mcx + i * 4, mcy + 6), 1)

    # ── studded leather belt across the body with a square gold buckle.
    bcx, bcy = 31, 54
    pygame.draw.line(surf, _FUR_D, (bcx - 16, bcy - 2), (bcx + 14, bcy - 5), 5)
    pygame.draw.line(surf, _FUR, (bcx - 16, bcy - 3), (bcx + 14, bcy - 6), 3)
    for sx in range(-13, 13, 5):
        pygame.draw.circle(surf, _GOLD_D, (bcx + sx, bcy - 3 - sx // 12), 1)
    pygame.draw.rect(surf, _GOLD_D, (bcx - 4, bcy - 7, 8, 8))
    pygame.draw.rect(surf, _GOLD, (bcx - 3, bcy - 6, 6, 6))
    pygame.draw.rect(surf, _FUR_D, (bcx - 1, bcy - 4, 2, 2))     # buckle tongue
    pygame.draw.line(surf, _GOLD_H, (bcx - 3, bcy - 6), (bcx + 2, bcy - 6), 1)

    # ── fur boot cuffs on the legs (the base feet poke below the body ~y 65).
    for fx in (27, 36):
        pygame.draw.ellipse(surf, _FUR_D, (fx - 4, 62, 9, 6))
        pygame.draw.ellipse(surf, _FUR, (fx - 4, 61, 8, 5))
        pygame.draw.line(surf, _FUR_H, (fx - 3, 62), (fx + 2, 62), 1)

    # ── huge split braided beard ballooning from the beak-base to the chest
    #    (drawn after the mantle so it overlaps it, before the helm so the helm's
    #    brow band caps it). Cool-dark mass so it separates from the scarlet.
    pygame.draw.ellipse(surf, _BEARD_D, (HX - 5, HY + 3, 20, 15))
    pygame.draw.ellipse(surf, _BEARD, (HX - 4, HY + 2, 18, 13))
    # Three fat braids hanging off the mass, each tapering to a tip.
    braids = ((HX - 1, 5), (HX + 6, 7), (HX + 11, 4))
    for bx, blen in braids:
        for j in range(blen):
            yy = HY + 12 + j * 2
            r = 3 if j < blen - 1 else 2
            col = _BEARD if j % 2 == 0 else _BEARD_D
            pygame.draw.circle(surf, col, (bx, yy), r)
        pygame.draw.line(surf, _BEARD_H, (bx - 1, HY + 12),
                         (bx - 1, HY + 12 + blen), 1)
    # Two gold beard-rings clamping the two longest braids near their ends.
    for bx, by in ((HX + 6, HY + 22), (HX - 1, HY + 20)):
        pygame.draw.circle(surf, _GOLD_D, (bx, by), 3)
        pygame.draw.circle(surf, _GOLD, (bx, by), 3, 1)
        pygame.draw.circle(surf, _GOLD_H, (bx - 1, by - 1), 1)

    # ── two big curved horns sweeping up-and-OUT past the crown (drawn before
    #    the dome so their roots tuck under the helm rim). The strongest single
    #    read — a horn-pair breaking the top of the silhouette.
    for sgn in (-1, 1):
        rootx = HX + sgn * 9
        rooty = CROWN_Y + 2
        midx = rootx + sgn * 9
        midy = CROWN_Y - 8
        tipx = rootx + sgn * 7
        tipy = CROWN_Y - 19
        # Tapering curved horn body: root → out-mid → up-tip.
        outer = [(rootx - sgn * 4, rooty + 2), (rootx + sgn * 5, rooty - 1),
                 (midx + sgn * 2, midy + 1), (tipx + sgn, tipy)]
        pygame.draw.lines(surf, _HORN_D, False, outer, 6)
        pygame.draw.lines(surf, _HORN, False, outer, 4)
        # Bright wide tip cap so the point survives the downscale.
        pygame.draw.circle(surf, _HORN, (tipx + sgn, tipy), 2)
        pygame.draw.circle(surf, _HORN_H if False else _IRON_H,
                           (tipx + sgn - 1, tipy - 1), 1)
        # A growth-ridge near the root so the horn reads as bone, not a tusk bar.
        pygame.draw.line(surf, _HORN_D, (rootx + sgn * 4, rooty - 1),
                         (rootx + sgn * 6, rooty - 3), 1)

    # ── iron spangenhelm dome (riveted half-dome) over the crown.
    pygame.draw.ellipse(surf, _IRON_D, (HX - 13, CROWN_Y - 7, 27, 20))
    pygame.draw.ellipse(surf, _IRON, (HX - 12, CROWN_Y - 7, 25, 17))
    # Bright dome highlight so the helm carries the read off the scarlet head.
    pygame.draw.ellipse(surf, _IRON_H, (HX - 7, CROWN_Y - 6, 10, 5))
    # Central ridge band of the spangen (riveted strips meeting at the apex).
    pygame.draw.line(surf, _IRON_D, (HX, CROWN_Y - 6), (HX, CROWN_Y + 5), 2)
    pygame.draw.line(surf, _IRON_H, (HX - 1, CROWN_Y - 6), (HX - 1, CROWN_Y), 1)
    # Riveted brow band capping the horn roots + the beard top.
    pygame.draw.line(surf, _IRON_D, (HX - 12, CROWN_Y + 5),
                     (HX + 13, CROWN_Y + 4), 4)
    pygame.draw.line(surf, _IRON_H, (HX - 12, CROWN_Y + 4),
                     (HX + 13, CROWN_Y + 3), 1)
    for rx in (HX - 9, HX - 2, HX + 6, HX + 11):
        pygame.draw.circle(surf, _IRON_H, (rx, CROWN_Y + 5), 1)
        pygame.draw.circle(surf, _IRON_D, (rx, CROWN_Y + 5), 1, 1)

    # ── short nasal bar down the brow (between the eyes) so the face reads as a
    #    helmeted raider, not a bird wearing a cap.
    pygame.draw.rect(surf, _IRON_D, (HX + 2, CROWN_Y + 4, 3, 11))
    pygame.draw.rect(surf, _IRON, (HX + 2, CROWN_Y + 4, 2, 10))
    pygame.draw.line(surf, _IRON_H, (HX + 2, CROWN_Y + 5),
                     (HX + 2, CROWN_Y + 12), 1)


build = store_skins._make_skin(_paint)
