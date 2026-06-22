"""NEON SEVER — Cyber-Kunoichi candidate for the ninja redraw (LEGENDARY).

Scratch exploration only; NOT registered in store_skins.BUILDERS, so the live
``skin_ninja`` is untouched. This is the futurist outlier of the costume set —
the visual opposite of the feudal black shinobi. Pip becomes a sleek carbon-
black bird traced in electric cyan neon piping, carrying the ONLY light-
emitting straight bar in the roster: a holographic energy ninjato slung up
past the crown, glowing magenta-into-cyan hilt-to-tip.

Read strategy at 40px in motion: the costume can't lean on costume colour the
way the feudal ninja does, so it leans on LIGHT. The energy blade breaks the
egg silhouette corner-to-corner the way a sword-on-the-back must, and the neon
edge-piping + visor + blade are additively bloomed so they pop hardest against
night sky exactly where this skin is meant to live. The still frame already
reads as a tech-ninja (matte mask, visor slit, headband chip, blade); the
wing-keyed pulse just makes the neon breathe so it feels alive in flight.

Layering, back-to-front: energy blade glow halo → blade core bar → carbon
body neon edge-piping → tech face mask → visor band → headband + emblem chip →
forearm/shin neon wrap rings → floating holo-shuriken at the hip. Glow halos
are drawn onto SRCALPHA layers and additively bloomed (BLEND_RGB_ADD) so the
emissive parts read as light, not paint — matching the disco shimmer / astro
visor masking idiom already in store_skins.
"""
import math
import pygame

from game import store_skins, parrot
from game.store_skins import HX, HY, CROWN_Y, COMPOSITE_W, COMPOSITE_H, _poly
from game.draw import lerp_color

# Carbon body + panel shade carry the matte ninja read; the neon trio
# (cyan piping/visor, magenta accent/blade core, hot white core) carries the
# light. Everything emissive is bloomed additively so it reads as glow.
_CARBON   = (10, 11, 16)           # #0A0B10 carbon body
_PANEL    = (21, 23, 31)           # #15171F panel shade (object separation)
_PANEL_H  = (38, 42, 54)           # faint matte sheen so black survives night
_CYAN     = (25, 224, 255)         # #19E0FF cyan neon piping / visor (pulses)
_CYAN_D   = (14, 120, 150)
_MAGENTA  = (255, 45, 155)         # #FF2D9B magenta accent + blade core
_MAGENTA_D = (150, 24, 92)
_HOT      = (234, 251, 255)        # #EAFBFF hot glow core
_CHIP     = (255, 210, 90)         # warm emblem chip — one off-neon spark


def _glow_line(layer, color, a, b, w, alpha):
    """Soft additive stroke for neon edge-glow: a fat faint pass under a
    thinner brighter pass, drawn onto an additive layer so overlaps bloom."""
    pygame.draw.line(layer, (*color, alpha // 3), a, b, w + 4)
    pygame.draw.line(layer, (*color, alpha // 2), a, b, w + 2)
    pygame.draw.line(layer, (*color, alpha), a, b, w)


def _glow_dot(layer, color, c, r, alpha):
    pygame.draw.circle(layer, (*color, alpha // 3), c, r + 3)
    pygame.draw.circle(layer, (*color, alpha // 2), c, r + 1)
    pygame.draw.circle(layer, (*color, alpha), c, r)


def _paint(surf, wing_angle_deg):
    # Neon pulse keyed off the wing beat so the light visibly breathes in
    # flight; the base wing angles span 50..-40, normalised to a 0..1 throb
    # that never fully dims (still frame must already read as lit neon).
    throb = 0.62 + 0.38 * (0.5 + 0.5 * math.sin(math.radians(wing_angle_deg * 3)))
    A_CY = int(150 + 105 * throb)       # cyan piping/visor alpha
    A_BL = int(170 + 85 * throb)        # blade core alpha
    # One shared additive bloom layer for every emissive element, blitted last
    # with BLEND_RGB_ADD so stacked glows brighten instead of paint over.
    glow = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)

    # ── CARBON RE-SKIN: the whole scarlet macaw underneath is flooded to matte
    #    carbon-black so the costume reads as a black bird lit by neon, not the
    #    default bird wearing accents. The body's own gradient is replaced by a
    #    flat carbon fill clamped to the silhouette (mask-min keeps it off the
    #    transparent margin), with a faint top sheen so the black survives night
    #    sky. Drawn before any neon so every glowing edge sits ON the carbon.
    carbon = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    carbon.fill((*_CARBON, 255))
    sil = pygame.mask.from_surface(surf, 8).to_surface(
        setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0))
    carbon.blit(sil, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(carbon, (0, 0))
    # Matte body sheen + a panel break so the carbon mass isn't a flat void.
    pygame.draw.ellipse(surf, _PANEL, (20, 46, 18, 6))
    pygame.draw.ellipse(surf, _PANEL_H, (24, 47, 8, 3))
    # Dark beak stays readable as a separate carbon facet.
    pygame.draw.polygon(surf, _PANEL, [(55, 41), (61, 44), (58, 48), (52, 46)], 1)

    # ── ENERGY NINJATO slung corner-to-corner (drawn FIRST so the body/head
    #    mask the mid-section and only the glowing ends poke out — the hero
    #    silhouette-breaker, and the only light-emitting straight bar in the
    #    set). Beam runs from below-left of the tail up past the crown.
    lo = (HX - 31, HY + 27)        # beam butt, out past the tail
    hi = (HX + 19, CROWN_Y - 18)   # blade tip, up past the crown
    dx, dy = hi[0] - lo[0], hi[1] - lo[1]
    blen = math.hypot(dx, dy)
    ux, uy = dx / blen, dy / blen
    px, py = -uy, ux               # perpendicular, for the guard

    # The guard splits emitter (magenta hilt, lower) from blade (cyan, upper).
    gx = lo[0] + ux * (blen * 0.40)
    gy = lo[1] + uy * (blen * 0.40)
    # Hilt half: dark matte grip with a magenta emitter core (hot at the base).
    pygame.draw.line(surf, _PANEL, lo, (gx, gy), 5)
    pygame.draw.line(surf, _CARBON, lo, (gx, gy), 3)
    _glow_line(glow, _MAGENTA, lo, (gx, gy), 2, A_BL)
    _glow_dot(glow, _MAGENTA, (int(lo[0]), int(lo[1])), 3, A_BL)   # emitter pommel
    _glow_dot(glow, _HOT, (int(lo[0]), int(lo[1])), 1, 240)
    # Blade half: a hard hologram beam, magenta-into-cyan up its length, with a
    # white-hot core line so the bar reads as light even before the bloom.
    steps = 9
    for i in range(steps):
        t0 = i / steps
        t1 = (i + 1) / steps
        ax = gx + (hi[0] - gx) * t0
        ay = gy + (hi[1] - gy) * t0
        bx = gx + (hi[0] - gx) * t1
        by = gy + (hi[1] - gy) * t1
        col = lerp_color(_MAGENTA, _CYAN, t0)
        _glow_line(glow, col, (ax, ay), (bx, by), 3, A_BL)
    # White-hot core + a brighter flaring tip.
    pygame.draw.line(glow, (*_HOT, 230), (gx, gy), hi, 1)
    _glow_dot(glow, _CYAN, (int(hi[0]), int(hi[1])), 3, A_BL)
    _glow_dot(glow, _HOT, (int(hi[0]), int(hi[1])), 1, 250)

    # Square energy guard (tsuba) at the emitter, glowing hot-white edged.
    guard = [
        (gx + px * 5, gy + py * 5), (gx - px * 5, gy - py * 5),
        (gx - px * 5 + ux * 3, gy - py * 5 + uy * 3),
        (gx + px * 5 + ux * 3, gy + py * 5 + uy * 3),
    ]
    _poly(surf, _CARBON, guard)
    pygame.draw.line(glow, (*_HOT, 220), (gx + px * 5, gy + py * 5),
                     (gx - px * 5, gy - py * 5), 2)

    # ── CARBON BODY EDGE-PIPING: trace a cyan neon seam along the leading body
    #    edge + wing edge so the matte black silhouette reads as light-lined,
    #    not a hole. Body centre ~(32, 52), head centre at (HX, HY).
    chest = [(HX - 4, HY + 8), (24, 44), (17, 53), (22, 62)]
    pygame.draw.lines(surf, _PANEL, False, chest, 3)
    _glow_line(glow, _CYAN, chest[0], chest[1], 1, A_CY)
    pygame.draw.lines(glow, (*_CYAN, A_CY), False, chest, 1)
    # Wing trailing-edge seam — a short diagonal off the wing root.
    we_a, we_b = (40, 44), (52, 38)
    _glow_line(glow, _CYAN, we_a, we_b, 1, A_CY)
    # A magenta belly seam so the second neon shows below the cyan.
    bs_a, bs_b = (20, 58), (33, 60)
    _glow_line(glow, _MAGENTA, bs_a, bs_b, 1, int(A_CY * 0.8))

    # ── TECH FACE MASK: matte-black hard-panel mask over the head, paneled so
    #    it reads as a helmet rather than cloth. Sits below the visor.
    pygame.draw.ellipse(surf, _PANEL, (HX - 13, CROWN_Y - 1, 26, 25))
    pygame.draw.ellipse(surf, _CARBON, (HX - 12, CROWN_Y, 24, 23))
    # Panel break lines (matte sheen) — the hard-surface read.
    pygame.draw.line(surf, _PANEL_H, (HX - 9, HY + 1), (HX + 11, HY - 1), 1)
    pygame.draw.line(surf, _PANEL_H, (HX - 6, CROWN_Y + 3), (HX - 6, HY + 6), 1)
    # Lower-face respirator panel across the beak base, with two vent slits.
    fold = [(HX - 10, HY + 4), (HX + 12, HY + 2),
            (HX + 12, HY + 10), (HX - 9, HY + 11)]
    _poly(surf, _PANEL, fold)
    _poly(surf, _CARBON, [(HX - 9, HY + 5), (HX + 11, HY + 3),
                          (HX + 11, HY + 9), (HX - 8, HY + 10)])
    for vy in (HY + 6, HY + 8):
        pygame.draw.line(surf, _PANEL_H, (HX + 2, vy), (HX + 9, vy - 1), 1)

    # ── NEON VISOR BAND: a single horizontal cyan slit across the eyes — the
    #    face's hero light. Hot-white inner core so it reads as an emitter.
    vy = HY - 1
    pygame.draw.rect(surf, (4, 5, 8), (HX - 7, vy - 3, 21, 7), border_radius=3)
    _glow_line(glow, _CYAN, (HX - 5, vy), (HX + 12, vy), 2, A_CY)
    pygame.draw.line(glow, (*_HOT, int(A_CY * 0.9)), (HX - 4, vy), (HX + 11, vy), 1)
    # Two brighter nodes in the slit so it reads as a sensor visor, not a bar.
    _glow_dot(glow, _HOT, (HX + 1, vy), 1, 230)
    _glow_dot(glow, _HOT, (HX + 9, vy), 1, 230)

    # ── HEADBAND + EMBLEM CHIP: thin carbon band over the mask with a small
    #    glowing emblem chip front-centre (the one warm off-neon spark).
    by = CROWN_Y + 3
    pygame.draw.line(surf, _CARBON, (HX - 12, by + 1), (HX + 12, by - 1), 4)
    pygame.draw.line(surf, _PANEL, (HX - 12, by), (HX + 12, by - 2), 2)
    pygame.draw.line(surf, _PANEL_H, (HX - 10, by - 1), (HX + 4, by - 2), 1)
    _glow_dot(glow, _CHIP, (HX, by - 1), 2, int(180 + 60 * throb))
    pygame.draw.circle(surf, _HOT, (HX, by - 1), 1)

    # ── NEON WRAP RINGS: thin glowing cyan rings banding the forearm (wing
    #    root) and shin — the tech-wrap detail that ties the limbs to the suit.
    for rx0, ry0, rx1, ry1 in ((38, 47, 46, 45), (39, 50, 47, 48)):
        _glow_line(glow, _CYAN, (rx0, ry0), (rx1, ry1), 1, int(A_CY * 0.85))
    # Shin ring on the near foot tuck (carbon tabi below it).
    for fx0, fy0, fx1, fy1 in ((25, 65, 23, 70), (34, 65, 36, 70)):
        pygame.draw.line(surf, _CARBON, (fx0, fy0), (fx1, fy1), 3)
    _glow_line(glow, _MAGENTA, (24, 66), (28, 66), 1, int(A_CY * 0.8))
    _glow_line(glow, _MAGENTA, (33, 66), (37, 66), 1, int(A_CY * 0.8))

    # ── FLOATING HOLO-SHURIKEN at the hip: a glowing ring-star spinning with
    #    the beat — a holographic projectile orbiting Pip. Spin keyed to the
    #    wing angle so it rotates as he flaps.
    sxc, syc = 17, 56
    spin = math.radians(wing_angle_deg * 4)
    _glow_dot(glow, _CYAN, (sxc, syc), 5, int(110 + 70 * throb))   # holo aura
    # Four-point ring-star: outer points + an inner ring, hot-white edged.
    for k in range(4):
        a = spin + k * math.pi / 2
        ox, oy = sxc + 6 * math.cos(a), syc + 6 * math.sin(a)
        ix, iy = sxc + 2 * math.cos(a + math.pi / 4), syc + 2 * math.sin(a + math.pi / 4)
        pygame.draw.line(glow, (*_CYAN, A_CY), (sxc, syc), (ox, oy), 2)
        pygame.draw.line(glow, (*_HOT, A_CY), (ix, iy), (ox, oy), 1)
    pygame.draw.circle(glow, (*_HOT, A_CY), (sxc, syc), 2, 1)

    # Additively bloom every emissive layer at once so overlaps brighten and
    # the neon reads as emitted light against the dark sky it's tuned for.
    surf.blit(glow, (0, 0), special_flags=pygame.BLEND_RGB_ADD)


build = store_skins._make_skin(_paint, base_fn=parrot._build_frame_bare)
