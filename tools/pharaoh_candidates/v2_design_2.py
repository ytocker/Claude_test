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
_KH_AMBER    = (245, 158, 40)      # warm amber midtone for the disk gradient
_KH_CORE     = (255, 241, 184)     # #FFF1B8 sun core (brightest value)
_KH_SEAM     = (12, 22, 36)        # darkest seam between the two wing-cases
_KH_DARK     = (16, 18, 26)        # near-black foot recolor


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
    # Crisp gold rim so the orb keeps a hard edge against its own bloom at 40px.
    pygame.draw.circle(surf, _KH_GOLD, (cx, cy), 7, 1)


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
    _poly(surf, _KH_SEAM, shell)                      # dark carapace edge
    inner = [(x - (1 if x < bcx else -1), y) for x, y in shell]
    _poly(surf, _KH_SHADOW, inner)

    # Iridescent zones across the dome: a cool blue crown fading down through
    # scarab teal into a violet hem, each laid as a band so the sheen reads as a
    # gradient, not a flat fill, after the downscale.
    _poly(surf, _KH_VIOLET, [(bcx - 11, bcy + 4), (bcx - 8, bcy + 11),
                             (bcx, bcy + 13), (bcx + 8, bcy + 11),
                             (bcx + 11, bcy + 4), (bcx, bcy + 7)])
    _poly(surf, _KH_TEAL, [(bcx - 11, bcy - 1), (bcx - 11, bcy + 5),
                           (bcx, bcy + 9), (bcx + 11, bcy + 5),
                           (bcx + 11, bcy - 1), (bcx, bcy + 2)])
    _poly(surf, _KH_BLUE, [(bcx - 9, bcy - 8), (bcx - 10, bcy - 1),
                           (bcx, bcy + 3), (bcx + 10, bcy - 1),
                           (bcx + 9, bcy - 8), (bcx, bcy - 9)])

    # Centre seam splitting the two wing-cases — the beetle tell.
    pygame.draw.line(surf, _KH_SEAM, (bcx, bcy - 10), (bcx, bcy + 13), 2)
    pygame.draw.line(surf, _KH_TEAL, (bcx + 1, bcy - 8), (bcx + 1, bcy + 11), 1)

    # Bright specular highlight streak down the LEFT wing-case — the single
    # highest value on the shell that makes the surface read as glossy chitin
    # rather than a matte plate, the iridescent signature at 40px.
    pygame.draw.lines(surf, _KH_HILITE, False,
                      [(bcx - 7, bcy - 7), (bcx - 9, bcy - 1),
                       (bcx - 8, bcy + 6)], 2)
    pygame.draw.line(surf, _KH_CORE, (bcx - 7, bcy - 6), (bcx - 8, bcy - 1), 1)
    # A smaller answering glint on the right wing-case so the dome reads curved.
    pygame.draw.line(surf, _KH_HILITE, (bcx + 6, bcy - 5), (bcx + 7, bcy + 2), 1)

    # Two short punctin rows of teal speckle dots down each case — beetle texture
    # kept sparse so it never muddies the sheen at the downscale.
    for dy in (bcy - 3, bcy + 3, bcy + 8):
        pygame.draw.circle(surf, _KH_SHADOW, (bcx - 5, dy), 1)
        pygame.draw.circle(surf, _KH_SHADOW, (bcx + 5, dy), 1)


def _scarab_crest(surf, cx, cy):
    """A small dark scarab-head plate at the hairline so the beetle theme reaches
    the head — a segmented notch (clypeus) with a teal sheen edge. Sits just
    below CROWN_Y, inside the head, so it never balloons the silhouette."""
    plate = [(cx - 6, cy + 1), (cx + 6, cy + 1), (cx + 4, cy + 5),
             (cx, cy + 6), (cx - 4, cy + 5)]
    _poly(surf, _KH_SEAM, plate)
    _poly(surf, _KH_SHADOW, [(cx - 5, cy + 1), (cx + 5, cy + 1),
                             (cx + 3, cy + 4), (cx - 3, cy + 4)])
    # Three clypeus notches along the front rim — the segmented scarab tell.
    for nx in (cx - 3, cx, cx + 3):
        pygame.draw.line(surf, _KH_SEAM, (nx, cy + 1), (nx, cy + 4), 1)
    pygame.draw.line(surf, _KH_TEAL, (cx - 5, cy + 1), (cx + 5, cy + 1), 1)
    pygame.draw.line(surf, _KH_HILITE, (cx - 4, cy + 1), (cx, cy + 1), 1)


def _paint(surf, _a):
    # Body centre in composite space (parrot body centre (32,32) + PARROT_DY).
    bcx, bcy = 32, 52

    # 1 · Sun-disk first-ish? No — it sits ABOVE everything visually but is
    # painted after the shell so its bloom layer composites over the carapace
    # top cleanly. Draw the shell, collar, crest, feet, then the sun-disk last
    # so the brightest sprite owns the top of the figure.

    # Iridescent scarab carapace domed over the back — the hero shape.
    _elytra_shell(surf, bcx, bcy)

    # Thin gold collar band seating the shell at the neck/chest — one bright arc
    # so the shell reads as worn, kept thin so it never adds body mass.
    pygame.draw.lines(surf, _KH_GOLD_D, False,
                      [(HX - 11, HY + 8), (HX, HY + 11), (HX + 11, HY + 7)], 3)
    pygame.draw.lines(surf, _KH_GOLD, False,
                      [(HX - 11, HY + 7), (HX, HY + 10), (HX + 11, HY + 6)], 2)
    pygame.draw.line(surf, _KH_CORE, (HX - 9, HY + 7), (HX - 1, HY + 9), 1)

    # Optional tiny beetle-leg ticks at the body edge — three short dark legs
    # each side, INSIDE the silhouette, so the bird reads as the beetle's body.
    for ly in (bcy - 2, bcy + 3, bcy + 8):
        pygame.draw.line(surf, _KH_SEAM, (bcx - 12, ly), (bcx - 15, ly + 2), 2)
        pygame.draw.line(surf, _KH_SEAM, (bcx + 12, ly), (bcx + 15, ly + 2), 2)
        pygame.draw.line(surf, _KH_TEAL, (bcx - 12, ly), (bcx - 14, ly + 1), 1)
        pygame.draw.line(surf, _KH_TEAL, (bcx + 12, ly), (bcx + 14, ly + 1), 1)

    # Dark beetle recolor at the feet line — sits ON the feet (~HY+24), never
    # below it, so the silhouette never grows downward.
    for fx in (28, 34):
        pygame.draw.ellipse(surf, _KH_DARK, (fx - 3, HY + 22, 7, 5))
        pygame.draw.line(surf, _KH_TEAL, (fx - 2, HY + 22), (fx + 2, HY + 22), 1)
        for tx in (fx - 2, fx, fx + 2):
            pygame.draw.line(surf, _KH_SEAM, (tx, HY + 25), (tx, HY + 27), 1)

    # Small dark scarab-head plate crest at the hairline — beetle theme on the
    # head, kept inside the head below the crown.
    _scarab_crest(surf, HX, CROWN_Y + 2)

    # Sun-disk last — the rolled sun lifted just above the brow. Its centre is
    # raised above CROWN_Y (the only element allowed up there) and its bloom is
    # drawn OUTSIDE the silhouette so it stays the brightest sprite on night.
    _sun_disk(surf, HX, CROWN_Y - 6)


build = store_skins._make_skin(_paint)
