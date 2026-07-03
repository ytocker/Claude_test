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
floating holo-shuriken at the hip. Glow halos are drawn onto SRCALPHA layers
and additively bloomed (BLEND_RGB_ADD) so the emissive parts read as light,
not paint — matching the disco shimmer / astro visor masking idiom already in
store_skins.

R2 (art-director ITERATE): the round-1 carbon flood let a warm emblem chip
read as a yellow crown dot at 40px and scattered seven sub-2px glow strokes
into an all-over haze that fought the carbon read. This round commits to a
strict two-tone language — CYAN is the suit, MAGENTA is the weapon, and
nothing else — so the silhouette resolves to "dark bird + one bright diagonal
blade + visor slit": (1) the carbon flood is re-applied AFTER the mask draws,
guaranteeing zero base-macaw colour survives; (2) the emblem chip is recolored
hot-white so the only warm pixel on the bird is gone; (3) body neon is one
continuous cyan leading-edge piping run (the forearm/shin rings, shin-ring
magenta and belly seam are deleted); (4) magenta is reserved strictly for the
blade emitter/hilt; (5) the hip holo-shuriken is demoted so it stops reading
as belly damage-glow; (6) the painted (non-additive) cyan core alpha is raised
so the edge holds on the washed-out DAY biome under the house 1px outline.
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
_MAGENTA  = (255, 45, 155)         # #FF2D9B magenta — weapon only (blade/hilt)
_HOT      = (234, 251, 255)        # #EAFBFF hot glow core
# Painted (non-additive) cyan for the piping seam itself — sits ON the carbon
# under the house outline so the edge stays legible on the washed-out DAY sky,
# where the additive bloom alone barely registers. Raised ~15% from R1.
_CYAN_PAINT = (70, 210, 240)


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


def _carbon_flood(surf):
    """Flood the whole macaw silhouette to flat matte carbon, clamped to its
    own alpha so the transparent margin is untouched. A flat carbon fill is
    BLEND_RGBA_MIN'd against the sprite's silhouette mask (white inside,
    transparent outside) then blitted opaque over the bird, so every base
    macaw pixel — body red, crown highlight, the red→yellow tail, the bare
    eye — is replaced. Called BEFORE the neon so glows sit on carbon, and
    AGAIN after the matte face panels so no base colour can survive."""
    carbon = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    carbon.fill((*_CARBON, 255))
    sil = pygame.mask.from_surface(surf, 8).to_surface(
        setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0))
    carbon.blit(sil, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(carbon, (0, 0))


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
    _carbon_flood(surf)
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
    # White-hot core line, but the tip itself flares CYAN, not white: a bright
    # white tip dot right above the crown re-read as a second light source on the
    # head at 40px (the "white-head blob"). The tip's hero colour is the cyan
    # blade glow (bigger bloom); the white is dimmed and un-bloomed so it only
    # sharpens the very point instead of clustering with the visor/emblem whites.
    pygame.draw.line(glow, (*_HOT, 230), (gx, gy), hi, 1)
    _glow_dot(glow, _CYAN, (int(hi[0]), int(hi[1])), 4, A_BL)
    pygame.draw.circle(glow, (*_HOT, 150), (int(hi[0]), int(hi[1])), 1)

    # Square energy guard (tsuba) at the emitter, glowing hot-white edged.
    guard = [
        (gx + px * 5, gy + py * 5), (gx - px * 5, gy - py * 5),
        (gx - px * 5 + ux * 3, gy - py * 5 + uy * 3),
        (gx + px * 5 + ux * 3, gy + py * 5 + uy * 3),
    ]
    _poly(surf, _CARBON, guard)
    pygame.draw.line(glow, (*_HOT, 220), (gx + px * 5, gy + py * 5),
                     (gx - px * 5, gy - py * 5), 2)

    # ── TECH FACE MASK: matte-black hard-panel mask over the head, paneled so
    #    it reads as a helmet rather than cloth. Drawn over the head FIRST, then
    #    a guaranteed re-flood (below) re-darkens any base-macaw pixel the mask
    #    didn't reach — the crown highlight + bare eye that survived in R1 — so
    #    the brightest non-neon mass at 40px can never be a warm dot.
    pygame.draw.ellipse(surf, _PANEL, (HX - 13, CROWN_Y - 1, 26, 25))
    pygame.draw.ellipse(surf, _CARBON, (HX - 12, CROWN_Y, 24, 23))
    # Lower-face respirator panel across the beak base.
    fold = [(HX - 10, HY + 4), (HX + 12, HY + 2),
            (HX + 12, HY + 10), (HX - 9, HY + 11)]
    _poly(surf, _PANEL, fold)
    _poly(surf, _CARBON, [(HX - 9, HY + 5), (HX + 11, HY + 3),
                          (HX + 11, HY + 9), (HX - 8, HY + 10)])

    # GUARANTEED FULL-BODY CARBON KILL: re-flood the whole silhouette to carbon
    # now that the matte panels are down, so zero base-macaw colour can survive
    # anywhere on the bird at 40px. The matte sheen + panel breaks are repainted
    # on TOP of this pass so the carbon mass still reads as faceted, not a void.
    _carbon_flood(surf)
    pygame.draw.ellipse(surf, _PANEL, (20, 46, 18, 6))      # body sheen
    pygame.draw.ellipse(surf, _PANEL_H, (24, 47, 8, 3))
    pygame.draw.line(surf, _PANEL_H, (HX - 9, HY + 1), (HX + 11, HY - 1), 1)
    pygame.draw.line(surf, _PANEL_H, (HX - 6, CROWN_Y + 3), (HX - 6, HY + 6), 1)
    for vy_ in (HY + 6, HY + 8):                            # respirator vents
        pygame.draw.line(surf, _PANEL_H, (HX + 2, vy_), (HX + 9, vy_ - 1), 1)

    # ── CARBON BODY EDGE-PIPING: ONE continuous cyan neon seam tracing the
    #    leading body edge — the single line that lifts the matte silhouette off
    #    the sky so it reads as light-lined, not a hole. Two-tone law: cyan is
    #    the suit, magenta is reserved for the weapon, so there is exactly one
    #    cyan run on the body and no stippled rings/seams to haze the carbon.
    #    A raised-alpha PAINTED core under the additive bloom holds the edge on
    #    the washed-out day sky where the bloom alone barely registers.
    chest = [(HX - 4, HY + 8), (24, 44), (17, 53), (22, 62)]
    pygame.draw.lines(surf, _CYAN_PAINT, False, chest, 2)
    _glow_line(glow, _CYAN, chest[0], chest[1], 1, A_CY)
    pygame.draw.lines(glow, (*_CYAN, A_CY), False, chest, 1)

    # ── NEON VISOR BAND: a single horizontal cyan slit across the eyes — the
    #    face's hero light. Hot-white inner core so it reads as an emitter.
    vy = HY - 1
    pygame.draw.rect(surf, (4, 5, 8), (HX - 7, vy - 3, 21, 7), border_radius=3)
    # PAINTED cyan core under the bloom so the slit is the brightest CYAN feature
    # on the face and resolves as a horizontal line at 40px — the two-tone
    # promise that the face's hero light is unmistakably cyan, not white.
    pygame.draw.line(surf, _CYAN, (HX - 5, vy), (HX + 12, vy), 2)
    _glow_line(glow, _CYAN, (HX - 5, vy), (HX + 12, vy), 3, A_CY)
    # The inner core line stays CYAN (was white-hot): a white core re-clustered
    # with the other head whites into a blob. A faint white pinpoint only.
    pygame.draw.line(glow, (*_CYAN, A_CY), (HX - 4, vy), (HX + 11, vy), 1)
    # Two brighter CYAN nodes in the slit so it reads as a sensor visor, not a
    # bar — cyan, not white, so the visor wins the face read.
    _glow_dot(glow, _CYAN, (HX + 1, vy), 1, 245)
    _glow_dot(glow, _CYAN, (HX + 9, vy), 1, 245)

    # ── HEADBAND + EMBLEM CHIP: thin carbon band over the mask with a small
    #    glowing emblem chip front-centre. DEMOTED to a small CYAN node (was
    #    hot-white): a loud white chip on the crown simply re-created the warm
    #    crown dot it replaced, now in white, stacking with the visor/blade-tip
    #    whites into a head blob. As a dim cyan node it folds into the suit's
    #    two-tone instead of fighting the visor for the face's hero light, and
    #    the carbon head stays dark with one cyan slit.
    by = CROWN_Y + 3
    pygame.draw.line(surf, _CARBON, (HX - 12, by + 1), (HX + 12, by - 1), 4)
    pygame.draw.line(surf, _PANEL, (HX - 12, by), (HX + 12, by - 2), 2)
    pygame.draw.line(surf, _PANEL_H, (HX - 10, by - 1), (HX + 4, by - 2), 1)
    _glow_dot(glow, _CYAN, (HX, by - 1), 1, int(90 + 40 * throb))
    pygame.draw.circle(surf, _CYAN_PAINT, (HX, by - 1), 1)

    # ── FLOATING HOLO-SHURIKEN at the hip: a glowing ring-star spinning with
    #    the beat — a holographic projectile orbiting Pip. DEMOTED this round:
    #    its R1 aura (r5, hot) read as belly damage-glow and competed with the
    #    blade. Aura tightened to r3 at lower alpha so it stays a small accent
    #    and the blade + visor carry the silhouette. All-cyan (weapon-magenta
    #    is reserved for the blade).
    sxc, syc = 17, 56
    spin = math.radians(wing_angle_deg * 4)
    _glow_dot(glow, _CYAN, (sxc, syc), 3, int(70 + 45 * throb))   # holo aura
    # Four-point ring-star: outer points + an inner ring, hot-white edged.
    A_SH = int(A_CY * 0.7)
    for k in range(4):
        a = spin + k * math.pi / 2
        ox, oy = sxc + 5 * math.cos(a), syc + 5 * math.sin(a)
        ix, iy = sxc + 2 * math.cos(a + math.pi / 4), syc + 2 * math.sin(a + math.pi / 4)
        pygame.draw.line(glow, (*_CYAN, A_SH), (sxc, syc), (ox, oy), 1)
        pygame.draw.line(glow, (*_HOT, A_SH), (ix, iy), (ox, oy), 1)
    pygame.draw.circle(glow, (*_HOT, A_SH), (sxc, syc), 2, 1)

    # Additively bloom every emissive layer at once so overlaps brighten and
    # the neon reads as emitted light against the dark sky it's tuned for.
    surf.blit(glow, (0, 0), special_flags=pygame.BLEND_RGB_ADD)


build = store_skins._make_skin(_paint, base_fn=parrot._build_frame_bare)
