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
_OS_GREEN    = (46, 125, 79)       # Osiris Nile-green (#2E7D4F) — skin of rebirth
_OS_GREEN_D  = (27, 77, 50)        # green shadow (#1B4D32)
_OS_GREEN_H  = (96, 178, 124)      # green highlight (chest/crown sheen)
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
    tail=[(30, 86, 56), (38, 104, 67), (46, 125, 79), (74, 156, 104)],
    tail_line=_OS_GREEN_D,
    body_shadow=(28, 80, 52),
    body_main=_OS_GREEN,
    body_chest=(72, 150, 100),
    body_belly=(54, 134, 86),
    sheen=(150, 210, 170, 70),
    wing_main=(40, 112, 72),
    wing_dark=_OS_GREEN_D,
    wing_tip=(86, 166, 114),
    wing_secondary=None,
    wing_highlight=_OS_GREEN_H,
    head_shadow=(28, 80, 52),
    head_main=_OS_GREEN,
    head_cheek=(80, 158, 108),
    head_crown=(72, 150, 100),
    lens_frame=(60, 130, 90),
    lens_body=(18, 54, 36),
    lens_tint=None,
    lens_glint=None,
    beak_main=(214, 188, 120),
    beak_dark=(150, 124, 64),
    beak_gloss=(244, 228, 170),
    foot=(30, 86, 56),
)


def _os_base(angle_deg):
    return _build_parrot_with_palette(angle_deg, _OS_BODY, draw_lenses=False)


def _crook_flail(surf):
    """Two short gold staffs crossed in an X over the chest — the signature
    Osiris gesture. Both are tucked entirely inside the body silhouette: the
    crook hooks at its top, the flail trails three short bead-strands, and
    neither tip leaves the footprint or crosses the feet line."""
    BCX, BCY = 32, 52

    # Crook (heka) — leans one way, with a shepherd's hook at its head.
    cx0, cy0 = BCX - 8, BCY + 9          # lower butt, inside the belly
    cx1, cy1 = BCX + 4, BCY - 8          # upper head, below the collar
    pygame.draw.line(surf, _OS_GOLD_D, (cx0, cy0 + 1), (cx1, cy1 + 1), 4)
    pygame.draw.line(surf, _OS_GOLD, (cx0, cy0), (cx1, cy1), 3)
    pygame.draw.line(surf, _OS_GOLD_H, (cx0 + 1, cy0 - 1), (cx1, cy1 - 1), 1)
    # Hook curl at the crook head.
    _poly(surf, _OS_GOLD_D, [(cx1, cy1 + 1), (cx1 + 5, cy1 - 1),
                             (cx1 + 4, cy1 + 4), (cx1, cy1 + 4)])
    _poly(surf, _OS_GOLD, [(cx1, cy1), (cx1 + 4, cy1 - 1),
                           (cx1 + 3, cy1 + 3), (cx1, cy1 + 3)])
    pygame.draw.circle(surf, _OS_GOLD_H, (cx1 + 3, cy1), 1)

    # Flail (nekhakha) — crosses the crook the other way; three short strands.
    fx0, fy0 = BCX + 8, BCY + 9           # lower butt
    fx1, fy1 = BCX - 4, BCY - 8           # upper head
    pygame.draw.line(surf, _OS_GOLD_D, (fx0, fy0 + 1), (fx1, fy1 + 1), 4)
    pygame.draw.line(surf, _OS_GOLD, (fx0, fy0), (fx1, fy1), 3)
    pygame.draw.line(surf, _OS_GOLD_H, (fx0 - 1, fy0 - 1), (fx1, fy1 - 1), 1)
    for dx in (-2, 0, 2):
        pygame.draw.line(surf, _OS_GOLD_D, (fx1, fy1), (fx1 + dx, fy1 - 5), 2)
        pygame.draw.line(surf, _OS_GOLD, (fx1, fy1), (fx1 + dx, fy1 - 4), 1)
        pygame.draw.circle(surf, _OS_GOLD_H, (fx1 + dx, fy1 - 4), 1)

    # Bright bead at the crossing so the X locks visually at 40px.
    pygame.draw.circle(surf, _OS_GOLD_H, (BCX, BCY + 1), 2)
    pygame.draw.circle(surf, _OS_WHITE_H, (BCX - 1, BCY), 1)


def _paint(surf, _a):
    BCX, BCY = 32, 52                     # body centre in composite space

    # ── pale mummy-wrap bands across the lower body ───────────────────────────
    # Thin horizontal strips on the belly so the green reads mummiform-regal
    # without adding mass. Kept inside the footprint and above the feet line.
    for wy, x0, x1 in ((BCY + 4, BCX - 14, BCX + 13),
                       (BCY + 8, BCX - 13, BCX + 12),
                       (BCY + 12, BCX - 11, BCX + 10)):
        pygame.draw.line(surf, _OS_GREEN_D, (x0, wy + 1), (x1, wy + 1), 3)
        pygame.draw.line(surf, _OS_WRAP, (x0, wy), (x1, wy), 2)
        pygame.draw.line(surf, _OS_WRAP_H, (x0 + 1, wy - 1), (x1 - 3, wy - 1), 1)

    # ── slim gold-and-lapis collar arc (neck/chest, inside footprint) ─────────
    cy = BCY - 12
    pygame.draw.line(surf, _OS_GOLD_D, (BCX - 14, cy + 1), (BCX + 13, cy), 4)
    pygame.draw.line(surf, _OS_LAPIS, (BCX - 14, cy), (BCX + 13, cy - 1), 3)
    pygame.draw.line(surf, _OS_GOLD, (BCX - 13, cy - 2), (BCX + 12, cy - 3), 2)
    for bx in range(BCX - 11, BCX + 12, 4):
        pygame.draw.circle(surf, _OS_LAPIS_H, (bx, cy), 1)
    pygame.draw.line(surf, _OS_GOLD_H, (BCX - 10, cy - 3), (BCX + 4, cy - 3), 1)

    # ── crook & flail crossed over the chest (the signature) ──────────────────
    _crook_flail(surf)

    # ── wrapped feet — pale linen caps sitting ON the feet line ───────────────
    for fx in (28, 35):
        pygame.draw.ellipse(surf, _OS_GREEN_D, (fx - 3, HY + 22, 7, 5))
        pygame.draw.ellipse(surf, _OS_WRAP, (fx - 3, HY + 21, 7, 4))
        pygame.draw.line(surf, _OS_WRAP_H, (fx - 2, HY + 21), (fx + 2, HY + 21), 1)

    # ── divine false-beard bar straight down under the chin ───────────────────
    # A crisp vertical tell, kept short so it stays inside the silhouette.
    bx = HX + 4
    _poly(surf, _OS_GREEN_D, [(bx - 3, HY + 5), (bx + 4, HY + 5),
                             (bx + 3, HY + 17), (bx - 2, HY + 17)])
    _poly(surf, _OS_WRAP, [(bx - 2, HY + 5), (bx + 3, HY + 5),
                          (bx + 2, HY + 16), (bx - 1, HY + 16)])
    # Plaited ridges + a gold cap where the beard meets the chin.
    for ry in (HY + 8, HY + 11, HY + 14):
        pygame.draw.line(surf, _OS_WHITE_D, (bx - 2, ry), (bx + 2, ry), 1)
    pygame.draw.line(surf, _OS_GOLD, (bx - 3, HY + 5), (bx + 4, HY + 5), 2)
    pygame.draw.line(surf, _OS_GOLD_H, (bx - 2, HY + 5), (bx + 2, HY + 5), 1)

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
