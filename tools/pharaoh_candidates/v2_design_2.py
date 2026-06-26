"""PHARAOH store-skin exploration — v2 DESIGN 2: KHEPRI, the scarab sun-bearer.

Scratch candidate only. Mirrors the production skin contract via
``store_skins._make_skin`` but is NOT registered in ``store_skins.BUILDERS``.

KHEPRI is a PAINT-OVER: Pip's scarlet face/body stay, and the costume is an
iridescent beetle carapace shell laid ON the back plus a glowing rolled
sun-disk lifted above the brow — beetle-rolling-the-sun, round-on-round. The
premium flex is built into the art: a blue→green→violet elytra sheen with a
bright specular streak, and a sun-disk that draws its bloom OUTSIDE the
silhouette so it stays the brightest sprite on a night sky.

Footprint law: the carapace rides ON the back but stays INSIDE the base bird
footprint (a shell, not a bigger body); nothing crosses the feet line; only
the sun-disk + its bloom rise above CROWN_Y.
"""
import math
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly


# Beetle palette: three near-blue/teal shell values keep the carapace from
# collapsing into one flat tone at 40px, the iridescent highlight is the
# specular streak that sells "shell", and the two gold values are the sun.
_KH_SHADOW   = (22, 38, 59)        # #16263B deep beetle-blue (shell shadow)
_KH_BLUE     = (24, 56, 78)        # blue-zone of the iridescent sheen
_KH_TEAL     = (30, 142, 126)      # #1E8E7E scarab teal (shell body)
_KH_VIOLET   = (74, 52, 110)       # violet-zone of the sheen
_KH_HILITE   = (127, 227, 176)     # #7FE3B0 iridescent specular highlight
_KH_GOLD     = (233, 183, 46)      # #E9B72E sun gold
_KH_GOLD_D   = (170, 124, 26)      # sun gold shadow (gradient base)
_KH_GOLD_RIM = (96, 64, 14)        # deep-amber/seam contour ring for the orb
_KH_AMBER    = (245, 158, 40)      # warm amber midtone for the disk gradient
_KH_CORE     = (255, 241, 184)     # #FFF1B8 sun core (brightest value)
_KH_SEAM     = (12, 22, 36)        # darkest seam between the two wing-cases
_KH_RIM      = (8, 16, 28)         # harder near-black carapace rim (dome edge)
_KH_DARK     = (16, 18, 26)        # near-black foot recolor
# Muted scarlet to paint over the wing edge that borders the shell zone, so
# the eye travels shell→sun, not red→green. Darkened + desaturated from Pip's
# scarlet so the red retreats and the dome's dark rim owns the contrast.
_KH_RED_MUTE = (118, 38, 34)
# Scarlet to reclaim the face from the wide base aviators, and a warm dark
# bronze for a SMALL scarab eye so the only true cool-dark mass is the shell.
_KH_FACE     = (240, 55, 55)        # Pip scarlet (BIRD_RED), to overpaint aviators
_KH_FACE_D   = (216, 48, 48)        # a hair darker for the lower cheek
_KH_EYE_DARK = (46, 30, 22)         # warm dark-brown/bronze eye (not near-black)


def _sun_disk(surf, cx, cy):
    """The rolled sun lifted above the brow — a layered gold→amber→core orb
    ringed by a soft bloom drawn OUTSIDE the body so it luminesces on a night
    sky. The bloom is laid as widening translucent rings on the live surface so
    the outline pass (which traces alpha) wraps the halo, not just the orb,
    and the disk stays the brightest sprite however dark the sky behind it."""
    # Soft bloom: concentric translucent gold rings, faint→none, on a scratch
    # SRCALPHA layer so the additive look survives over both day and night.
    bloom = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    for r, a in ((13, 36), (11, 54), (9, 78), (7, 110)):
        pygame.draw.circle(bloom, (*_KH_CORE, a), (cx, cy), r)
    surf.blit(bloom, (0, 0))

    # Solid orb, layered as a top-lit gradient: gold shadow base, amber mid,
    # gold body, then a small off-centre core so the disk reads round and lit.
    pygame.draw.circle(surf, _KH_GOLD_D, (cx, cy), 7)
    pygame.draw.circle(surf, _KH_AMBER, (cx, cy - 1), 6)
    pygame.draw.circle(surf, _KH_GOLD, (cx, cy - 1), 5)
    pygame.draw.circle(surf, _KH_CORE, (cx - 1, cy - 2), 3)
    pygame.draw.circle(surf, (255, 255, 230), (cx - 2, cy - 3), 1)  # spec hit
    # A thin DARK amber contour ring so the orb keeps a hard edge on a bright
    # day sky too — the glow alone carries it on night, the contour on day.
    pygame.draw.circle(surf, _KH_GOLD_RIM, (cx, cy), 7, 1)


def _elytra_shell(surf, bcx, bcy):
    """The hero: an iridescent scarab elytra shell domed over the back — two
    teardrop wing-cases meeting at a centre seam, with a blue→teal→violet sheen
    and one bright specular streak. Kept INSIDE the body footprint (it rides ON
    the back, it does NOT enlarge the silhouette): the dome top stays below the
    head, the sides stay within the breast, the base stays above the feet."""
    # Domed carapace outline as one rounded shield, slightly back-weighted so it
    # reads as a shell sitting on the spine rather than a frontal bib.
    shell = [(bcx - 12, bcy - 2), (bcx - 13, bcy + 5), (bcx - 9, bcy + 12),
             (bcx, bcy + 14), (bcx + 9, bcy + 12), (bcx + 12, bcy + 5),
             (bcx + 11, bcy - 3), (bcx + 6, bcy - 9), (bcx, bcy - 11),
             (bcx - 6, bcy - 9)]
    # A HARD near-black dome rim is the whole point — it gives the carapace a
    # crisp outline that is NOT the bird's outline, so a clean DOME pops off the
    # scarlet body instead of reading as a green belly. Drawn as a thick filled
    # ring: solid rim plate, then the iridescent fill inset 2px inside it.
    _poly(surf, _KH_RIM, shell)
    inner = [(bcx + (x - bcx) * 0.80, bcy + (y - bcy) * 0.80) for x, y in shell]
    _poly(surf, _KH_SHADOW, inner)

    # Iridescent zones across the dome: a cool blue crown fading down through
    # scarab teal into a violet hem, each laid as a band so the sheen reads as a
    # gradient, not a flat fill, after the downscale. Held inside the dark rim.
    # Violet hem pulled IN from the right rim so no bright cool speck protrudes
    # past the dome edge at the base (the lone fleck that read as noise).
    _poly(surf, _KH_VIOLET, [(bcx - 9, bcy + 4), (bcx - 6, bcy + 9),
                             (bcx, bcy + 10), (bcx + 5, bcy + 8),
                             (bcx + 7, bcy + 4), (bcx, bcy + 6)])
    _poly(surf, _KH_TEAL, [(bcx - 9, bcy - 1), (bcx - 9, bcy + 4),
                           (bcx, bcy + 7), (bcx + 9, bcy + 4),
                           (bcx + 9, bcy - 1), (bcx, bcy + 1)])
    _poly(surf, _KH_BLUE, [(bcx - 8, bcy - 7), (bcx - 8, bcy - 1),
                           (bcx, bcy + 2), (bcx + 8, bcy - 1),
                           (bcx + 8, bcy - 7), (bcx, bcy - 8)])

    # Bright specular highlight streak down the LEFT wing-case — the single
    # highest value on the shell that makes the surface read as glossy chitin
    # rather than a matte plate, the iridescent signature at 40px.
    pygame.draw.lines(surf, _KH_HILITE, False,
                      [(bcx - 6, bcy - 6), (bcx - 7, bcy - 1),
                       (bcx - 6, bcy + 5)], 2)
    pygame.draw.line(surf, _KH_CORE, (bcx - 6, bcy - 5), (bcx - 7, bcy - 1), 1)
    # A smaller answering glint on the right wing-case so the dome reads curved.
    pygame.draw.line(surf, _KH_HILITE, (bcx + 5, bcy - 4), (bcx + 6, bcy + 2), 1)

    # Centre seam LAST and BOLD: a continuous 2px near-black line splitting the
    # dome top to base into two confident wing-cases, flanked by a single 1px
    # teal highlight on the right so the seam survives the 40px downscale as one
    # clean vertical line instead of dissolving into the sheen.
    pygame.draw.line(surf, _KH_SEAM, (bcx, bcy - 9), (bcx, bcy + 12), 2)
    pygame.draw.line(surf, _KH_HILITE, (bcx + 2, bcy - 6), (bcx + 2, bcy + 9), 1)

    # Re-stroke the LOWER dome rim last so the dark base overdraws any cool
    # blue/violet speck that crept past the inset — the base must read as one
    # clean dark dome edge, not noise. A 2px near-black arc along the shell hem.
    pygame.draw.lines(surf, _KH_RIM, False,
                      [(bcx - 13, bcy + 5), (bcx - 9, bcy + 12),
                       (bcx, bcy + 14), (bcx + 9, bcy + 12),
                       (bcx + 12, bcy + 5)], 3)


def _reface(surf):
    """Reclaim the head from the base aviators and stamp ONE small warm scarab
    eye. The base bird wears wide black aviators; at 40px that dark horizontal
    band reads as a duck's dark crown and steals the head from Pip's scarlet.
    We overpaint the aviator footprint with scarlet so the SCARLET face owns the
    head, then place a single narrow warm dark-BRONZE eye — ~30% narrower than
    the band and pulled off near-black — so the only true cool-dark mass left in
    the whole sprite is the shell dome below."""
    ecx, ecy = 50, 40  # base aviator centre in composite space

    # Overpaint the aviator band with scarlet, keyed to the body's own alpha so
    # the silhouette never grows (no scarlet bleeds onto open sky). A filled
    # scratch patch covering the lens span, masked to the existing head.
    head_mask = pygame.mask.from_surface(surf)
    patch = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.ellipse(patch, _KH_FACE, (ecx - 9, ecy - 8, 22, 16))
    pygame.draw.ellipse(patch, _KH_FACE_D, (ecx - 9, ecy + 1, 22, 8))
    patch.blit(head_mask.to_surface(setcolor=(255, 255, 255, 255),
                                    unsetcolor=(0, 0, 0, 0)),
               (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(patch, (0, 0))

    # ONE narrow warm-bronze eye where the near lens was — ~30% of the band's
    # width, warm dark-brown so it never reads as a cool dark crown mass.
    pygame.draw.ellipse(surf, _KH_EYE_DARK, (ecx + 1, ecy - 3, 7, 6))
    pygame.draw.ellipse(surf, _KH_SEAM, (ecx + 2, ecy - 2, 5, 4))
    pygame.draw.circle(surf, (255, 240, 210), (ecx + 3, ecy - 1), 1)  # life glint


def _scarab_notch(surf, cx, cy):
    """ONE bold dark notch directly under the sun-disk — the segmented scarab
    clypeus reduced to a single confident mark. The old fussy multi-tooth plate
    became noise at 40px; a lone triangular notch reads as the beetle's brow
    and frames the disk above it instead of competing with it."""
    notch = [(cx - 4, cy), (cx + 4, cy), (cx, cy + 4)]
    _poly(surf, _KH_SEAM, notch)
    pygame.draw.line(surf, _KH_TEAL, (cx - 4, cy), (cx + 4, cy), 1)


def _paint(surf, _a):
    # Body centre in composite space (parrot body centre (32,32) + PARROT_DY).
    bcx, bcy = 32, 52

    # 1 · Sun-disk first-ish? No — it sits ABOVE everything visually but is
    # painted after the shell so its bloom layer composites over the carapace
    # top cleanly. Draw the shell, collar, notch, feet, then the sun-disk last
    # so the brightest sprite owns the top of the figure.

    # Quiet the scarlet wing/breast where it borders the shell zone BEFORE the
    # shell lands, so the eye reads shell→sun, not red→green. The mute is laid
    # by MULTIPLY-darkening only the pixels already opaque under the dome's
    # border ring — drawn on a scratch layer keyed to the body's alpha so it
    # darkens existing red without painting red onto empty sky (no footprint
    # growth). The dome then lands inside this quieted ring.
    body_mask = pygame.mask.from_surface(surf)
    ring = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    # Lower-left vertices pushed further out + alpha dropped to ~210 so the loud
    # scarlet sweep under the dome's left flank is darkened; the sun-disk must be
    # the unambiguous brightest WARM element, not this corner of red.
    _poly(ring, (*_KH_RED_MUTE, 210),
          [(bcx - 15, bcy - 3), (bcx - 18, bcy + 11), (bcx - 13, bcy + 18),
           (bcx, bcy + 17), (bcx + 11, bcy + 16), (bcx + 16, bcy + 9),
           (bcx + 15, bcy - 4), (bcx + 8, bcy - 11), (bcx, bcy - 13),
           (bcx - 8, bcy - 11)])
    # Keep the mute only where the body already is, so transparent sky is never
    # tinted and the silhouette cannot grow.
    ring.blit(body_mask.to_surface(setcolor=(255, 255, 255, 255),
                                   unsetcolor=(0, 0, 0, 0)),
              (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(ring, (0, 0))

    # Reclaim the head from the base aviators: scarlet face + ONE small warm
    # bronze eye, so the SCARLET head owns the read and the shell dome is the
    # only true cool-dark mass in the sprite.
    _reface(surf)

    # Iridescent scarab carapace domed over the back — the hero shape.
    _elytra_shell(surf, bcx, bcy)

    # Thin gold collar band seating the shell at the neck/chest — one bright arc
    # so the shell reads as worn, kept thin so it never adds body mass.
    pygame.draw.lines(surf, _KH_GOLD_D, False,
                      [(HX - 11, HY + 8), (HX, HY + 11), (HX + 11, HY + 7)], 3)
    pygame.draw.lines(surf, _KH_GOLD, False,
                      [(HX - 11, HY + 7), (HX, HY + 10), (HX + 11, HY + 6)], 2)
    pygame.draw.line(surf, _KH_CORE, (HX - 9, HY + 7), (HX - 1, HY + 9), 1)

    # Feet: a plain dark recolor only — the old beetle-leg ticks and foot
    # speckles read as noise at 40px and muddied the silhouette, so the feet are
    # now a quiet near-black mass that sits ON the feet line, never below it.
    for fx in (28, 34):
        pygame.draw.ellipse(surf, _KH_DARK, (fx - 3, HY + 22, 7, 5))

    # ONE bold dark notch directly under the sun-disk — the beetle brow, kept
    # inside the head below the crown. Replaces the fussy segmented crest.
    _scarab_notch(surf, HX, CROWN_Y + 1)

    # Sun-disk last — the rolled sun lifted CLEAR above the brow. Raised so a
    # visible band of sky sits between the orb and the head: the two stacked
    # circles must read as a beetle rolling a SEPARATE ball, not one blob. Its
    # bloom is drawn OUTSIDE the silhouette so it stays the brightest sprite.
    _sun_disk(surf, HX, CROWN_Y - 9)


build = store_skins._make_skin(_paint)
