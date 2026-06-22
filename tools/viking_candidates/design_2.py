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

    # ── BACK · one CONTINUOUS dark fur cloak draping the whole rear (behind) ───
    # The scarlet leak was the R1 killer: gold-on-red survived behind the helm.
    # Now a single unbroken fur mass climbs up OVER the wing's leading edge and
    # falls down across the entire back into the tail base, so the rear third of
    # the silhouette reads FUR-brown, never red. Drawn first, under everything.
    # First two vertices seat the fur UNDER the helm brow (up+out ~2px) so no
    # red nape gap survives behind the helm; the central fall is dropped lower
    # so the dark mass fully overlaps the down-flap tail tip + underwing.
    cloak = [(HX - 6, HY - 5),            # up over the wing-root / nape (sealed)
             (HX - 18, HY - 3),           # leading edge of the wing, covered
             (HX - 27, HY + 8),           # widest rear bulge
             (HX - 30, HY + 22),
             (HX - 32, HY + 31),          # down OVER the red tail base (kills leak)
             (HX - 22, HY + 34),
             (HX - 12, HY + 31),
             (HX - 4, HY + 26),           # central fall pushed lower over tail tip
             (HX + 3, HY + 18)]
    _poly(surf, FUR_D, cloak)
    _poly(surf, FUR, [(HX - 6, HY - 3), (HX - 16, HY - 1), (HX - 24, HY + 9),
                      (HX - 27, HY + 22), (HX - 28, HY + 30),
                      (HX - 20, HY + 32), (HX - 12, HY + 29),
                      (HX - 5, HY + 24), (HX + 1, HY + 17)])
    # Lumpy tuft rim down the cloak's outer fall so it reads fur, not a smooth pad.
    for k in range(8):
        ty = HY + 2 + k * 4
        tx = HX - 25 - (2 if 2 <= k <= 6 else 0)
        pygame.draw.circle(surf, FUR_D, (tx, ty), 3)
        pygame.draw.circle(surf, FUR_H, (tx - 1, ty - 1), 1)

    # ── WING TIP · fur tuft thrown over the scarlet wing tip (kills rear leak) ─
    # The down-flap wing tip flares to the far rear-left; left bare it was the
    # last scarlet patch behind the gold. A dark fur mass lands on it so the
    # cloak reads as draping right over the wing — the rear stays fur-brown.
    # Raised + widened so it also catches the leading-edge red that rides
    # highest on the up-flap frame (thinnest fur), not just the rest pose.
    _fur_lump(surf, HX - 34, HY + 8, 13, 9)

    # ── TAIL TIP · one fur lump sealing the down-flap tail base (red + blue) ──
    # The macaw's tail tip + underwing dip below the central fall on the down-
    # flap frames; a dark fur lump seated right on the tail base overlaps the
    # last ~6 scarlet + ~6 underwing-blue px across ALL four wing frames.
    _fur_lump(surf, HX - 3, HY + 23, 11, 7)

    # ── NAPE · short fur lump under the helm brow sealing the red nape streak ─
    # Seated a hair higher-left so the nape fur seats fully under the helm brow
    # with no red gap behind it on any frame; the helm dome seals the very top.
    _fur_lump(surf, HX - 13, HY - 5, 9, 6)

    # ── SHOULDERS · wolf/bear RUFF flaring PAST both shoulders (widest point) ──
    # The hero silhouette break: the two flank masses are pushed UP + OUT so the
    # dark fur — not the helm, not the wing — is the WIDEST horizontal extent on
    # both sides at 40px. A lower central swag keeps clear of the beard below.
    _fur_lump(surf, HX - 22, HY + 5, 13, 8)       # near (left) shoulder — widest L
    _fur_lump(surf, HX + 16, HY + 3, 12, 8)       # far (right) shoulder — widest R
    _fur_lump(surf, HX - 1, HY + 14, 10, 6)       # lower central swag (de-crowds buckle)

    # ── FACE · broad blonder braided beard with stacked gold beard-rings ──────
    # A leather chin-root knits the beard to the body, then a wide blonde braid
    # mass, then ONE braid hanging lower clasped by ONE bold gold band — the
    # signature "he can afford gold on his beard" detail (three rings smeared).
    pygame.draw.ellipse(surf, LEATHER, (HX - 3, HY + 7, 17, 7))   # warm root shadow
    pygame.draw.ellipse(surf, BEARD_D, (HX - 4, HY + 5, 18, 12))
    pygame.draw.ellipse(surf, BEARD, (HX - 3, HY + 4, 16, 10))
    # Two braid forks; the near one carries the single gold band.
    _poly(surf, BEARD, [(HX - 1, HY + 11), (HX + 5, HY + 11), (HX + 1, HY + 22)])
    _poly(surf, BEARD_D, [(HX + 4, HY + 11), (HX + 11, HY + 11), (HX + 8, HY + 19)])
    pygame.draw.line(surf, BEARD_D, (HX + 1, HY + 13), (HX, HY + 21), 1)
    pygame.draw.line(surf, BEARD_D, (HX + 7, HY + 13), (HX + 9, HY + 18), 1)
    # ONE bold gold band clasping the near braid, with a single bright rivet.
    pygame.draw.ellipse(surf, GOLD_D, (HX - 2, HY + 16, 8, 4))
    pygame.draw.ellipse(surf, GOLD, (HX - 1, HY + 16, 7, 3))
    pygame.draw.circle(surf, GOLD_H, (HX + 1, HY + 17), 1)

    # ── HEAD · gilded spangenhelm dome with engraved rune-dot brow band ───────
    # Bright gold so the head carries the read; the spangen seam down the front
    # and the riveted band are the gold detail that survives downscale.
    # Dark shadow base runs a hair wider-left so the helm itself seals the last
    # up-flap underwing pixel at its rounded nape edge (no fur poke needed).
    pygame.draw.ellipse(surf, GOLD_D, (HX - 14, cy - 7, 27, 19))
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

    # ── CROWN · gold CREST-COMB raised + gapped off the dome (survives 40px) ──
    # R1: gold ridge fused into the gold dome and read as one blob. Now the comb
    # rises ~2px clear of the dome with a thin dark fur/leather line gapping its
    # base, so the bright ridge separates from the bright bowl. 4 clean teeth.
    comb_base = cy - 7                  # raised above the dome crown
    comb_top = cy - 13
    teeth = [(HX + 8, comb_base),
             (HX + 4, comb_top),
             (HX - 1, comb_base - 1),
             (HX - 5, comb_top),
             (HX - 9, comb_base)]
    _poly(surf, GOLD_D, teeth + [(HX - 9, comb_base + 2), (HX + 8, comb_base + 2)])
    pygame.draw.lines(surf, GOLD, False, teeth, 2)
    pygame.draw.line(surf, GOLD_H, (HX + 4, comb_top), (HX - 5, comb_top), 1)
    # Thin dark separation line at the comb base so it lifts off the dome.
    pygame.draw.line(surf, FUR_D, (HX - 9, comb_base + 2), (HX + 8, comb_base + 1), 1)

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

    # ── HIP · PALE-BONE drinking horn swinging clearly OFF the belt ───────────
    # R1: a dark hooked horn read as a talon. Now a bright BONE body with a gold
    # rim, swung down and OUT past the belt's near edge on a visible strap so it
    # reads as a hung horn, not a claw. Bone value carries it; gold rim is the pop.
    hx0, hy0 = bx - 19, by + 6
    horn = [(hx0 + 4, hy0 - 3), (hx0 - 4, hy0 + 1), (hx0 - 8, hy0 + 11),
            (hx0 - 5, hy0 + 14), (hx0 - 1, hy0 + 6), (hx0 + 6, hy0 + 1)]
    _poly(surf, LEATHER, horn)                                     # thin dark outline
    _poly(surf, HORN_BONE, [(hx0 + 4, hy0 - 2), (hx0 - 3, hy0 + 1),
                            (hx0 - 6, hy0 + 10), (hx0 - 3, hy0 + 12),
                            (hx0, hy0 + 6), (hx0 + 5, hy0 + 1)])
    pygame.draw.line(surf, (240, 230, 208), (hx0 + 2, hy0), (hx0 - 4, hy0 + 9), 1)
    pygame.draw.circle(surf, LEATHER, (hx0 - 6, hy0 + 12), 2)      # pointed cap tip
    # Gold-banded rim at the wide mouth (the bright accent on this object).
    pygame.draw.line(surf, GOLD_D, (hx0 + 4, hy0 - 4), (hx0 + 8, hy0 + 1), 3)
    pygame.draw.line(surf, GOLD, (hx0 + 4, hy0 - 4), (hx0 + 8, hy0), 2)
    pygame.draw.circle(surf, GOLD_H, (hx0 + 6, hy0 - 2), 1)
    # Strap from belt down to the horn mouth so it reads as hung, not floating.
    pygame.draw.line(surf, LEATHER_H, (bx - 13, by), (hx0 + 5, hy0 - 3), 1)

    # ── COLLAR · ONE bold valknut disc on the DARK fur (where it has contrast) ─
    # R1 etched the brooch onto the body where it vanished. Now it's a single
    # bold ~6px gold disc sitting on the deep near-shoulder fur, the one spot
    # the gold genuinely pops — the chest accent the silhouette needed.
    vx, vy = HX - 14, HY + 7
    pygame.draw.circle(surf, GOLD_D, (vx, vy), 6)
    pygame.draw.circle(surf, GOLD, (vx, vy), 5)
    pygame.draw.circle(surf, GOLD_H, (vx - 1, vy - 1), 2)
    for k in range(3):                                            # 3-prong valknut mark
        a = -math.pi / 2 + k * 2 * math.pi / 3
        pygame.draw.line(surf, VALK_INK, (vx, vy),
                         (int(vx + 4 * math.cos(a)), int(vy + 4 * math.sin(a))), 1)

    # ── WING ROOT · ONE bold gold arm-ring torc ──────────────────────────────
    # "The warlord who hands out arm-rings" wears one of his own — a single
    # bolder torc at the wing root rather than two faint stacked rings.
    wrx, wry = 40, HY + 8
    pygame.draw.ellipse(surf, GOLD_D, (wrx - 7, wry, 15, 6))
    pygame.draw.ellipse(surf, GOLD, (wrx - 6, wry + 1, 13, 4))
    pygame.draw.line(surf, GOLD_H, (wrx - 4, wry + 2), (wrx + 4, wry + 2), 1)


build = store_skins._make_skin(_paint)
