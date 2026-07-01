"""OSIRIS — the green lord of the afterlife (PHARAOH costume, v2 re-roll).

Scratch exploration only — NOT registered in store_skins.BUILDERS.

The set's only FULL BODY RECOLOR: the whole macaw turns Nile-green (skin of
rebirth) via `_os_base`, then `_paint` adds the regalia AFTER the recoloured
base blit. The hero two-value read is a tall white twin-plume Atef crown over
the green body — the pale spike + green body separate it instantly from the
gold pharaoh kings, and the white Atef + gold crook/flail X carry the night
side where the green sinks toward the dark sky.

FOOTPRINT LAW: collision is a fixed ~10px circle, so every BODY element — the
collar arc, the crossed crook & flail, the wrap bands, the false beard — stays
inside the base bird silhouette and nothing drops below the feet line. ONLY the
Atef crown rises above CROWN_Y.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette


# ── palette ──────────────────────────────────────────────────────────────────
# Skybit's pillars, bushes and ground are all WARM yellow-greens. To keep Osiris
# from camouflaging into the foliage, the body is pushed toward a COOLER, DEEPER
# teal-green and dropped in value so it reads darker than every canopy, with a
# near-black outline carved around the whole silhouette as a hard separating edge.
_OS_GREEN    = (28, 102, 88)       # Osiris cool teal-green (#1C6658) — sits below the canopies
_OS_GREEN_D  = (10, 44, 40)        # near-black green outline/shadow (#0A2C28)
_OS_GREEN_H  = (78, 168, 150)      # cool green highlight (chest/crown sheen)
_OS_WHITE    = (242, 239, 230)     # Atef / Hedjet white (#F2EFE6)
_OS_WHITE_D  = (206, 202, 188)     # plume/cone shadow
_OS_WHITE_H  = (255, 255, 250)     # crisp white glint
_OS_GOLD     = (232, 178, 58)      # crook & flail / sun-disk gold (#E8B23A)
_OS_GOLD_H   = (255, 226, 140)     # gold glint
_OS_GOLD_D   = (168, 126, 32)      # gold shadow
_OS_LAPIS    = (39, 64, 139)       # lapis collar (#27408B)
_OS_LAPIS_H  = (96, 128, 210)      # lapis highlight bead
_OS_URAEUS   = (200, 50, 46)       # red uraeus cobra at the crown base
_OS_WRAP     = (224, 218, 200)     # pale mummy-wrap band over the lower body
_OS_WRAP_H   = (244, 240, 228)     # wrap highlight


# Whole-bird Nile-green re-plumage. Every body slot is a green value so the
# recolour reads as one creature; lenses are dropped so the divine face owns
# the head, and the beak goes pale-gold to echo the regalia.
_OS_BODY = _pal(
    tail=[(14, 56, 50), (20, 76, 66), (28, 102, 88), (44, 132, 116)],
    tail_line=_OS_GREEN_D,
    body_shadow=(16, 60, 52),
    body_main=_OS_GREEN,
    body_chest=(40, 128, 112),
    body_belly=(28, 108, 94),
    sheen=(120, 200, 180, 64),
    wing_main=(22, 88, 76),
    wing_dark=_OS_GREEN_D,
    wing_tip=(54, 146, 128),
    wing_secondary=None,
    wing_highlight=_OS_GREEN_H,
    head_shadow=(16, 60, 52),
    head_main=_OS_GREEN,
    head_cheek=(46, 138, 120),
    head_crown=(40, 128, 112),
    lens_frame=(34, 100, 88),
    lens_body=(10, 44, 40),
    lens_tint=None,
    lens_glint=None,
    beak_main=(214, 188, 120),
    beak_dark=(150, 124, 64),
    beak_gloss=(244, 228, 170),
    foot=(16, 60, 52),
)


def _os_base(angle_deg):
    """Recoloured teal-green macaw with a near-black rim carved around its whole
    silhouette. Skybit's pipes/bushes/ground are warm yellow-greens; without a
    hard dark edge a green body butts colour-to-colour against foliage and
    dissolves. The rim is hue-matched (deep teal-black) so it reads as Osiris's
    own shadow, not a sticker outline, and it stacks under the lighter 1px
    outline _make_skin adds so the separating edge never breaks."""
    body = _build_parrot_with_palette(angle_deg, _OS_BODY, draw_lenses=False)
    mask = pygame.mask.from_surface(body, threshold=8)
    rim = mask.to_surface(setcolor=_OS_GREEN_D + (255,),
                          unsetcolor=(0, 0, 0, 0))
    out = pygame.Surface(body.get_size(), pygame.SRCALPHA)
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1),
                   (-1, -1), (1, -1), (-1, 1), (1, 1)):
        out.blit(rim, (dx, dy))
    out.blit(body, (0, 0))
    return out


def _crook_flail(surf):
    """Two BOLD gold bars crossed in an X over the chest — the signature Osiris
    gesture, rebuilt to read at 40px. At that size a shepherd's-hook curl and a
    3-strand flail are sub-pixel mud, so each staff is one fat bar with a bright
    gold core over a dark base. The crossing carries NO centre bead — at 40px the
    bead + both bars fused into a lozenge that read as a diamond, so the bars now
    cross bare and the X stays an X. The butt roots are pushed outward so the
    angle opens up instead of reading vertical, and each upper tip gets a single
    1px gold-highlight cap so the arms taper to a clean point."""
    BCX, BCY = 32, 52

    # Both staffs as fat bars with a dark base and a bright gold core so the X
    # out-values the now-darker teal body and pops as the chest hero.
    def _bar(x0, y0, x1, y1):
        pygame.draw.line(surf, _OS_GREEN_D, (x0, y0 + 1), (x1, y1 + 1), 5)
        pygame.draw.line(surf, _OS_GOLD_D, (x0, y0), (x1, y1), 4)
        pygame.draw.line(surf, _OS_GOLD, (x0, y0), (x1, y1), 3)
        pygame.draw.line(surf, _OS_GOLD_H, (x0, y0 - 1), (x1, y1 - 1), 1)

    # Roots pushed ~2px wider at each butt so the X opens instead of reading
    # vertical. Crook (heka): lower-left butt up to upper-right head.
    cx0, cy0 = BCX - 11, BCY + 9
    cx1, cy1 = BCX + 8, BCY - 8
    # Flail (nekhakha): lower-right butt up to upper-left head.
    fx0, fy0 = BCX + 11, BCY + 9
    fx1, fy1 = BCX - 8, BCY - 8
    _bar(cx0, cy0, cx1, cy1)
    _bar(fx0, fy0, fx1, fy1)

    # One brighter 1px gold cap on each bar's upper tip so the arms taper to a
    # clean point — replaces the old hook-notch + tassel (sub-pixel fringe-mud).
    pygame.draw.circle(surf, _OS_GOLD_H, (cx1, cy1), 1)
    pygame.draw.circle(surf, _OS_GOLD_H, (fx1, fy1), 1)


def _paint(surf, _a):
    BCX, BCY = 32, 52                     # body centre in composite space

    # ── pale mummy-wrap bands across the lower body ───────────────────────────
    # TWO crisp, bold linen bands (was three faint ones — they read as noise at
    # 40px). Each is a pale band over its own dark shadow line so it stays legible
    # after the shrink. Inside the footprint, above the feet line.
    for wy, x0, x1 in ((BCY + 6, BCX - 14, BCX + 13),
                       (BCY + 11, BCX - 12, BCX + 11)):
        pygame.draw.line(surf, _OS_GREEN_D, (x0, wy + 2), (x1, wy + 2), 2)
        pygame.draw.line(surf, _OS_WRAP, (x0, wy), (x1, wy), 3)
        pygame.draw.line(surf, _OS_WRAP_H, (x0 + 1, wy - 1), (x1 - 3, wy - 1), 1)

    # ── slim gold-and-lapis collar arc (neck/chest, inside footprint) ─────────
    cy = BCY - 12
    pygame.draw.line(surf, _OS_GOLD_D, (BCX - 14, cy + 1), (BCX + 13, cy), 4)
    pygame.draw.line(surf, _OS_LAPIS, (BCX - 14, cy), (BCX + 13, cy - 1), 3)
    pygame.draw.line(surf, _OS_GOLD, (BCX - 13, cy - 2), (BCX + 12, cy - 3), 2)
    for bx in range(BCX - 11, BCX + 12, 4):
        pygame.draw.circle(surf, _OS_LAPIS_H, (bx, cy), 1)
    pygame.draw.line(surf, _OS_GOLD_H, (BCX - 10, cy - 3), (BCX + 4, cy - 3), 1)

    # ── continuous gold trim where green meets the collar/wrap zone ───────────
    # A hard, bright separating line just under the collar so the teal body never
    # bleeds edge-to-edge into foliage at the chest break — a second internal
    # "outline" of regalia, framing the top of the crook-and-flail X.
    ty = BCY - 6
    pygame.draw.line(surf, _OS_GOLD_D, (BCX - 15, ty + 1), (BCX + 14, ty), 2)
    pygame.draw.line(surf, _OS_GOLD, (BCX - 15, ty), (BCX + 14, ty - 1), 1)

    # ── crook & flail crossed over the chest (the signature) ──────────────────
    _crook_flail(surf)

    # ── wrapped feet — pale linen caps sitting ON the feet line ───────────────
    for fx in (28, 35):
        pygame.draw.ellipse(surf, _OS_GREEN_D, (fx - 3, HY + 22, 7, 5))
        pygame.draw.ellipse(surf, _OS_WRAP, (fx - 3, HY + 21, 7, 4))
        pygame.draw.line(surf, _OS_WRAP_H, (fx - 2, HY + 21), (fx + 2, HY + 21), 1)

    # ── divine false-beard: bold gold-capped dark bar with a pale plait ───────
    # A vertical chin tell that must survive the shrink, so it's a SOLID dark
    # bar (not a faint sliver) capped by a bright gold band and split by one
    # clear pale plait stripe — three values stacked so it reads at 40px.
    bx = HX + 4
    _poly(surf, _OS_GREEN_D, [(bx - 4, HY + 5), (bx + 4, HY + 5),
                             (bx + 3, HY + 18), (bx - 3, HY + 18)])
    _poly(surf, _OS_GOLD_D, [(bx - 3, HY + 7), (bx + 3, HY + 7),
                            (bx + 2, HY + 17), (bx - 2, HY + 17)])
    # Pale plait running down the centre of the dark bar.
    pygame.draw.line(surf, _OS_WRAP, (bx, HY + 7), (bx, HY + 16), 2)
    pygame.draw.line(surf, _OS_WHITE_H, (bx, HY + 8), (bx, HY + 14), 1)
    # Bright gold cap where the beard meets the chin.
    pygame.draw.line(surf, _OS_GOLD, (bx - 4, HY + 6), (bx + 4, HY + 6), 3)
    pygame.draw.line(surf, _OS_GOLD_H, (bx - 3, HY + 5), (bx + 3, HY + 5), 1)

    # ── ATEF crown (the only thing allowed above CROWN_Y) ─────────────────────
    _atef(surf)


def _atef(surf):
    """The Atef: a tall white Hedjet cone flanked by two curving ostrich plumes,
    with a small gold sun-disk + red uraeus at the base. Tall, clean, symmetric
    — the hero pale spike that reads at 40px on day and night."""
    cy = CROWN_Y                          # crown base sits on the head crown

    # Base band the crown seats on.
    pygame.draw.ellipse(surf, _OS_GOLD_D, (HX - 12, cy + 1, 26, 8))
    pygame.draw.ellipse(surf, _OS_GOLD, (HX - 11, cy + 1, 24, 5))
    pygame.draw.line(surf, _OS_GOLD_H, (HX - 9, cy + 2), (HX + 9, cy + 2), 1)

    # Twin ostrith plumes — tall curving blades, drawn FIRST so the cone laps
    # over their inner roots. Symmetric about the head centre.
    for sgn in (-1, 1):
        rootx = HX + sgn * 7
        tipx = HX + sgn * 14
        outer = [(rootx, cy + 1),
                 (rootx + sgn * 2, cy - 16),
                 (tipx, cy - 30),
                 (tipx + sgn * 2, cy - 24),
                 (rootx + sgn * 6, cy - 10),
                 (rootx + sgn * 4, cy + 1)]
        _poly(surf, _OS_WHITE_D, [(x + sgn, y) for x, y in outer])
        _poly(surf, _OS_WHITE, outer)
        # Central rib + a few barb ticks so the plume reads as a feather.
        pygame.draw.line(surf, _OS_WHITE_D,
                         (rootx + sgn * 2, cy), (tipx, cy - 28), 1)
        pygame.draw.line(surf, _OS_WHITE_H,
                         (rootx + sgn * 1, cy - 2), (tipx - sgn, cy - 26), 1)

    # White Hedjet cone in the centre — the bright vertical the eye locks onto.
    cone = [(HX - 7, cy + 2), (HX + 7, cy + 2),
            (HX + 4, cy - 18), (HX, cy - 26), (HX - 4, cy - 18)]
    _poly(surf, _OS_WHITE_D, [(x + 1, y) for x, y in cone])
    _poly(surf, _OS_WHITE, cone)
    # Bulb at the cone tip (the Hedjet knob) + a left-side highlight ridge.
    pygame.draw.circle(surf, _OS_WHITE_D, (HX, cy - 26), 2)
    pygame.draw.circle(surf, _OS_WHITE_H, (HX - 1, cy - 26), 1)
    pygame.draw.line(surf, _OS_WHITE_H, (HX - 3, cy - 4), (HX - 1, cy - 22), 1)

    # Small gold sun-disk + red uraeus at the cone base — the divine accent.
    pygame.draw.circle(surf, _OS_GOLD_D, (HX, cy + 3), 4)
    pygame.draw.circle(surf, _OS_GOLD, (HX, cy + 3), 3)
    pygame.draw.circle(surf, _OS_GOLD_H, (HX - 1, cy + 2), 1)
    # Uraeus cobra rearing in front of the disk.
    _poly(surf, _OS_URAEUS, [(HX - 2, cy + 5), (HX + 2, cy + 5),
                            (HX + 1, cy - 1), (HX - 1, cy - 1)])
    pygame.draw.circle(surf, _OS_URAEUS, (HX, cy - 2), 2)
    pygame.draw.circle(surf, _OS_GOLD_H, (HX - 1, cy - 2), 1)


build = store_skins._make_skin(_paint, base_fn=_os_base)
