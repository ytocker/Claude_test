"""JARL GULLHELM — The Golden King-Jarl  (viking redesign candidate design_2).

Scratch exploration only — NOT registered in store_skins.BUILDERS and it does
NOT touch the live skin_viking. This is the premium "wealthy warlord" tier:
where the shipped viking is rust-iron, this one inverts to GOLD + royal fur —
the warlord who hands out arm-rings.

The silhouette signature is two shapes no other costume owns: a deep wolf/bear
fur RUFF COLLAR flaring WIDE past both shoulders (a soft, dark, lumpy mass that
breaks the egg outline left and right) topped by a gilded crested SPANGENHELM
with a low gold fin-comb running front-to-back over the crown. Hung off that:
a broad blonder braided beard with stacked gold beard-rings, gold arm-ring torcs
at the wing root, a studded belt with an ornate buckle plate, a gold-rimmed
drinking horn at the hip, and a small valknut brooch on the chest.

Objects are layered ALL OVER (head + back + body + limbs) per the contract, and
every gold note is the high-value read that carries 40px — the fur stays dark so
the gold pops off it, mirroring the keepers' "mass + one bright accent" rule.
"""
import math
import pygame

from game import store_skins, parrot
from game.store_skins import HX, HY, CROWN_Y
from game.store_skins import _poly


# ── Palette (brief swatches) ──────────────────────────────────────────────────
GOLD      = (227, 178, 60)         # #E3B23C helm / crest / rings
GOLD_D    = (168, 132, 42)         # #A8842A gold shadow
GOLD_H    = (244, 227, 176)        # #F4E3B0 gold + horn highlight
FUR       = (107, 82, 52)          # #6B5234 wolf/bear fur cloak
FUR_D     = (74, 56, 36)           # deep fur shadow (lump separation)
FUR_H     = (146, 116, 78)         # lifted fur tuft tips
BEARD     = (168, 138, 86)         # blonder braid (lighter than shipped tan)
BEARD_D   = (120, 96, 56)
LEATHER   = (58, 42, 27)           # #3A2A1B belt + horn body + beard root
LEATHER_H = (92, 70, 46)
HORN_BONE = (216, 200, 168)        # pale drinking-horn body
VALK_INK  = (44, 32, 20)           # etched brooch line on the chest


def _fur_lump(surf, cx, cy, rx, ry):
    """A soft fur mass: dark shadow base, mid fill, then a scatter of lighter
    tuft bumps along the rim so it reads as fur, not a smooth pad. Kept dark
    overall so the gold layered on top stays the brightest note at 40px."""
    pygame.draw.ellipse(surf, FUR_D, (cx - rx, cy - ry, rx * 2, ry * 2))
    pygame.draw.ellipse(surf, FUR, (cx - rx + 1, cy - ry + 1, rx * 2 - 2, ry * 2 - 2))
    # Tuft bumps around the lower rim — the lumpy fur silhouette break.
    n = max(5, rx)
    for i in range(n):
        a = math.pi * (0.12 + 0.76 * i / (n - 1))   # lower arc, left->right
        bx = cx + math.cos(a) * rx
        by = cy + math.sin(a) * ry
        pygame.draw.circle(surf, FUR_D, (int(bx), int(by)), 3)
        pygame.draw.circle(surf, FUR, (int(bx), int(by)), 2)
        if i % 2 == 0:
            pygame.draw.circle(surf, FUR_H, (int(bx), int(by - 1)), 1)


def _paint(surf, wing_angle_deg):
    cy = CROWN_Y

    # ── BACK · furred cape edge draping down the back (drawn first, behind) ────
    # A tapering dark fur fall off the back-of-shoulder into the tail region so
    # the cloak reads as a full garment, not just a collar.
    cape = [(HX - 20, HY + 2), (HX - 9, HY + 1),
            (HX - 8, HY + 22), (HX - 24, HY + 18)]
    _poly(surf, FUR_D, cape)
    _poly(surf, FUR, [(HX - 19, HY + 3), (HX - 10, HY + 2),
                      (HX - 9, HY + 20), (HX - 22, HY + 17)])
    for k in range(4):
        ty = HY + 6 + k * 4
        pygame.draw.circle(surf, FUR_H, (HX - 21 - k, ty), 1)

    # ── SHOULDERS · luxurious wolf/bear RUFF collar flaring WIDE past both ─────
    # The hero silhouette break. Two big fur lumps thrown well past each shoulder
    # plus a central swag under the beak so the collar reads as one continuous
    # deep ruff wrapping the neck. Dark mass on purpose — gold rides on top.
    _fur_lump(surf, HX - 16, HY + 9, 9, 7)        # near (left) shoulder, flares out
    _fur_lump(surf, HX + 14, HY + 9, 8, 7)        # far (right) shoulder, flares out
    _fur_lump(surf, HX - 1, HY + 12, 11, 6)       # central neck swag

    # ── FACE · broad blonder braided beard with stacked gold beard-rings ──────
    # A leather chin-root knits the beard to the body, then a wide blonde braid
    # mass, then ONE braid hanging lower with three stacked gold rings — the
    # signature "he can afford gold on his beard" detail.
    pygame.draw.ellipse(surf, LEATHER, (HX - 3, HY + 7, 17, 7))   # warm root shadow
    pygame.draw.ellipse(surf, BEARD_D, (HX - 4, HY + 5, 18, 12))
    pygame.draw.ellipse(surf, BEARD, (HX - 3, HY + 4, 16, 10))
    # Two braid forks; the near one carries the gold rings.
    _poly(surf, BEARD, [(HX - 1, HY + 11), (HX + 5, HY + 11), (HX + 1, HY + 22)])
    _poly(surf, BEARD_D, [(HX + 4, HY + 11), (HX + 11, HY + 11), (HX + 8, HY + 19)])
    pygame.draw.line(surf, BEARD_D, (HX + 1, HY + 13), (HX, HY + 21), 1)
    pygame.draw.line(surf, BEARD_D, (HX + 7, HY + 13), (HX + 9, HY + 18), 1)
    # Three stacked gold rings clasping the near braid.
    for j in range(3):
        ry = HY + 14 + j * 3
        pygame.draw.ellipse(surf, GOLD_D, (HX - 2, ry, 7, 3))
        pygame.draw.ellipse(surf, GOLD, (HX - 1, ry, 5, 2))
        pygame.draw.circle(surf, GOLD_H, (HX, ry), 1)

    # ── HEAD · gilded spangenhelm dome with engraved rune-dot brow band ───────
    # Bright gold so the head carries the read; the spangen seam down the front
    # and the riveted band are the gold detail that survives downscale.
    pygame.draw.ellipse(surf, GOLD_D, (HX - 12, cy - 6, 25, 18))
    pygame.draw.ellipse(surf, GOLD, (HX - 11, cy - 6, 23, 15))
    pygame.draw.ellipse(surf, GOLD_H, (HX - 6, cy - 5, 9, 4))     # dome specular
    # Spangen seam riveted down the front of the bowl.
    pygame.draw.line(surf, GOLD_D, (HX, cy - 5), (HX + 1, cy + 4), 2)
    # Engraved brow band with rune-dot etching (dark dots between bright rivets).
    pygame.draw.line(surf, GOLD_D, (HX - 11, cy + 5), (HX + 12, cy + 4), 4)
    pygame.draw.line(surf, GOLD_H, (HX - 11, cy + 4), (HX + 12, cy + 3), 1)
    for rx in (HX - 8, HX - 1, HX + 6):
        pygame.draw.circle(surf, GOLD_H, (rx, cy + 5), 1)          # rivet
    for dx in (HX - 5, HX + 2, HX + 9):
        pygame.draw.circle(surf, LEATHER, (dx, cy + 5), 1)         # rune-dot etch
    # Gold nose-guard (royal, matches the helm).
    pygame.draw.rect(surf, GOLD_D, (HX + 1, cy + 4, 3, 11))
    pygame.draw.rect(surf, GOLD, (HX + 1, cy + 4, 2, 10))
    pygame.draw.line(surf, GOLD_H, (HX + 1, cy + 5), (HX + 1, cy + 12), 1)

    # ── CROWN · low gold CREST-COMB running front-to-back over the helm ───────
    # A shallow fin of gold blades along the midline of the bowl — the second
    # half of the unique silhouette. It rises just above the dome and runs the
    # full front->back length so it breaks the crown outline as a serrated ridge.
    comb_top = cy - 11
    blades = [
        (HX + 9, cy - 3),               # front root (over the brow)
        (HX + 7, comb_top + 2),
        (HX + 3, comb_top - 1),
        (HX, comb_top),
        (HX - 3, comb_top - 1),
        (HX - 7, comb_top + 2),
        (HX - 10, cy - 4),              # back root (toward the nape)
    ]
    base = [(HX + 9, cy - 1), (HX - 10, cy - 2)]
    _poly(surf, GOLD_D, blades + base[::-1])
    # Bright top ridge so the fin reads as gold, not a dark spike row.
    pygame.draw.lines(surf, GOLD, False, blades, 2)
    pygame.draw.lines(surf, GOLD_H, False,
                      [(HX + 6, comb_top + 2), (HX, comb_top - 1),
                       (HX - 6, comb_top + 2)], 1)

    # ── BODY · studded wide belt + ornate gold buckle plate ───────────────────
    bx, by = 30, HY + 14
    pygame.draw.rect(surf, LEATHER, (bx - 16, by, 30, 7))
    pygame.draw.line(surf, LEATHER_H, (bx - 15, by + 1), (bx + 12, by + 1), 1)
    for sx in range(bx - 12, bx + 12, 5):                          # rivet studs
        pygame.draw.circle(surf, GOLD_D, (sx, by + 4), 1)
        pygame.draw.circle(surf, GOLD_H, (sx, by + 3), 1)
    # Ornate gold buckle plate dead-centre on the belt.
    pygame.draw.rect(surf, GOLD_D, (bx - 5, by - 1, 11, 9), border_radius=2)
    pygame.draw.rect(surf, GOLD, (bx - 4, by, 9, 7), border_radius=2)
    pygame.draw.line(surf, GOLD_H, (bx - 3, by + 1), (bx + 3, by + 1), 1)
    pygame.draw.circle(surf, GOLD_D, (bx, by + 3), 2)              # boss centre
    pygame.draw.circle(surf, GOLD_H, (bx - 1, by + 2), 1)

    # ── HIP · drinking horn with a gold-banded rim hanging off the belt ───────
    # A pale curved horn swinging from the near side of the belt — the unique
    # "wealthy warlord" prop, capped with a bright gold rim band.
    hx0, hy0 = bx - 17, by + 3
    horn = [(hx0, hy0 - 2), (hx0 - 6, hy0 + 4), (hx0 - 9, hy0 + 12),
            (hx0 - 6, hy0 + 14), (hx0 - 3, hy0 + 6), (hx0 + 2, hy0 + 2)]
    _poly(surf, LEATHER, horn)
    _poly(surf, HORN_BONE, [(hx0, hy0 - 1), (hx0 - 5, hy0 + 4),
                            (hx0 - 7, hy0 + 11), (hx0 - 4, hy0 + 6),
                            (hx0 + 1, hy0 + 2)])
    pygame.draw.circle(surf, LEATHER, (hx0 - 7, hy0 + 12), 2)      # pointed cap tip
    # Gold-banded rim at the wide mouth (the bright accent on this object).
    pygame.draw.line(surf, GOLD_D, (hx0 - 1, hy0 - 2), (hx0 + 3, hy0 + 3), 3)
    pygame.draw.line(surf, GOLD, (hx0 - 1, hy0 - 2), (hx0 + 3, hy0 + 2), 2)
    pygame.draw.circle(surf, GOLD_H, (hx0 + 1, hy0), 1)
    # Strap from belt to horn so it reads as hung, not floating.
    pygame.draw.line(surf, LEATHER_H, (bx - 13, by + 5), (hx0 - 1, hy0 - 1), 1)

    # ── CHEST · small valknut brooch (three interlocking triangles) ───────────
    vx, vy = bx + 9, by - 6
    pygame.draw.circle(surf, GOLD_D, (vx, vy), 4)                  # brooch disc
    pygame.draw.circle(surf, GOLD, (vx, vy), 3)
    for rot in (-math.pi / 2, -math.pi / 2 + 0.7, -math.pi / 2 - 0.7):
        tri = [(vx + 3 * math.cos(rot + k * 2 * math.pi / 3),
                vy + 3 * math.sin(rot + k * 2 * math.pi / 3)) for k in range(3)]
        pygame.draw.lines(surf, VALK_INK, True, [(int(x), int(y)) for x, y in tri], 1)

    # ── WING ROOT · stacked gold arm-ring torcs ──────────────────────────────
    # Two arm-rings clasped at the wing root — "the warlord who hands out
    # arm-rings" wears his own. Bright gold so the wing reads as adorned.
    wrx, wry = 40, HY + 6
    for j in range(2):
        ry = wry + j * 5
        pygame.draw.ellipse(surf, GOLD_D, (wrx - 6, ry, 13, 5))
        pygame.draw.ellipse(surf, GOLD, (wrx - 5, ry, 11, 4))
        pygame.draw.line(surf, GOLD_H, (wrx - 3, ry + 1), (wrx + 3, ry + 1), 1)

    # ── LEG · matching gold ankle ring above the near foot ────────────────────
    axp, ayp = 28, HY + 24
    pygame.draw.ellipse(surf, GOLD_D, (axp - 4, ayp, 9, 4))
    pygame.draw.ellipse(surf, GOLD, (axp - 3, ayp, 7, 3))
    pygame.draw.circle(surf, GOLD_H, (axp, ayp + 1), 1)


build = store_skins._make_skin(_paint)
