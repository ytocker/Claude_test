"""IRONCLAD — the classic brown raider (viking-palette candidate, v1).

Scratch exploration ONLY — never registered in store_skins.BUILDERS; the live
skin_viking is untouched. This is a PLAIN-Viking recolour of the winning
FROSTREAVER structure (tools/viking_candidates/design_4): same horned
spangenhelm, big beard, fur ruff, back round shield, bearded axe and boot
cuffs — but the ice theme is stripped out entirely and the 24-slot body
palette is re-plumed to warm medium-brown.

De-frost vs FROSTREAVER:
  * Icicle beard fangs  → braided-beard tips capped with bronze beard-rings.
  * Shield frost-crystals → DROPPED (plain oak shield: planks + red field +
    iron boss + iron rim).
  * Horn tips → plain bone/metal, not frost-white.
  * Brim icicle drip → DROPPED. Ice-fleck glints → plain metal/bronze glints.

North star (shared with store_skins): "a skin lives or dies at 40px in motion."
The warm-brown body recolour is the can't-miss default raider; mass + one
bright accent per object survives the downscale. The dark-brown KEYLINE wrap
(the day-read fix carried over from FROSTREAVER) holds the silhouette against
a bright sky — the warm body never owns a dark outer edge on its own.
"""
import math
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly, _compose
from game.parrot import _add_outline
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette


# ── IRONCLAD palette (brief spec) ────────────────────────────────────────────
BODY      = (138, 106, 69)          # #8A6A45 warm medium-brown plumage
BODY_SHAD = (94, 70, 48)            # #5E4630 plumage shadow / line work
CHEST     = (160, 126, 84)          # #A07E54 chest
BELLY     = (110, 82, 56)           # #6E5238 belly

HELM      = (126, 134, 148)         # #7E8694 iron helm
HELM_DK   = (74, 80, 96)            # #4A5060 dark iron
HELM_HI   = (198, 206, 218)         # #C6CEDA iron highlight

FUR       = (107, 83, 58)           # #6B533A warm-brown fur mantle
FUR_HI    = (138, 110, 76)          # #8A6E4C fur highlight

BEARD     = (58, 42, 27)            # #3A2A1B dark-brown beard
BEARD_HI  = (90, 70, 50)            # #5A4632 beard braid highlight

BRONZE    = (200, 144, 46)          # #C8902E bronze rings / rivets / buckle
SHIELD_RED = (178, 58, 42)          # #B23A2A red painted shield field
OAK       = (138, 106, 69)          # #8A6A45 oak shield planks
BONE      = (214, 200, 170)         # plain bone/metal horn tip

# The warm mass dissolves into a bright day sky just like the frost mass did;
# the shipped near-black 1px outline reads thin against mid-brown. A dark-brown
# keyline (#281C12) wrapped around the WHOLE composited silhouette is the single
# biggest day-read fix — BODY_SHAD only ever touches interior line work, so the
# warm outer mass would otherwise have no dark edge against a bright sky.
KEYLINE = (40, 28, 18, 235)         # #281C12 dark-brown outer keyline


# Full warm-brown re-plumage of the macaw. Every slot is shifted to brown; the
# wing TIP / highlight slots carry the lighter chest tone on the feather edge,
# and the deepest BODY_SHAD owns the line work so the warm mass still holds a
# crisp interior edge. Lenses are dropped so the helm brow + beard own the face.
P_IRON = _pal(
    tail=[(120, 90, 58), (134, 102, 66), (150, 116, 78), (168, 132, 90)],
    tail_line=BODY_SHAD,
    body_shadow=BODY_SHAD,
    body_main=BODY,
    body_chest=CHEST,
    body_belly=BELLY,
    sheen=(255, 240, 215, 90),
    wing_main=(128, 98, 64),
    wing_dark=(86, 64, 42),
    wing_tip=(170, 134, 90),
    wing_secondary=None,
    wing_highlight=(184, 150, 104),
    head_shadow=BODY_SHAD,
    head_main=BODY,
    head_cheek=CHEST,
    head_crown=(150, 116, 78),
    lens_frame=(120, 90, 58),
    lens_body=(40, 30, 20),
    lens_tint=None,
    lens_glint=None,
    beak_main=(150, 120, 80),
    beak_dark=BODY_SHAD,
    beak_gloss=(190, 160, 116),
    foot=(96, 72, 48),
)


def _iron_base(angle_deg):
    # Warm-brown bird, no aviators — the helm brow + braided beard own the face.
    return _build_parrot_with_palette(angle_deg, P_IRON, draw_lenses=False)


# ── costume paint ────────────────────────────────────────────────────────────

def _paint(surf, wing_angle_deg):
    cy = CROWN_Y

    # ── ROUND OAK SHIELD on the BACK (drawn first, behind the body) ──────────
    # Plain oak planks with a RED painted field, an iron boss and an iron rim.
    # No frost crystals — the clean round disc is the plain raider's back read.
    sx, sy, sr = HX - 26, HY + 11, 13
    pygame.draw.circle(surf, BEARD, (sx, sy), sr + 1)           # dark rim base
    pygame.draw.circle(surf, OAK, (sx, sy), sr)                 # oak ground
    pygame.draw.circle(surf, SHIELD_RED, (sx, sy), sr - 3)      # red field
    # Plank seams across the face (read across both oak border and red field).
    for dx in (-7, 0, 7):
        pygame.draw.line(surf, BODY_SHAD, (sx + dx, sy - sr + 2),
                         (sx + dx, sy + sr - 2), 1)
    # Iron rim ring + iron boss with a hard highlight glint.
    pygame.draw.circle(surf, HELM, (sx, sy), sr, 2)
    pygame.draw.circle(surf, HELM_DK, (sx, sy), 5)
    pygame.draw.circle(surf, HELM, (sx, sy), 4)
    pygame.draw.circle(surf, HELM_DK, (sx, sy), 4, 1)
    pygame.draw.circle(surf, HELM_HI, (sx - 1, sy - 1), 1)

    # ── WARM-WOLF FUR MANTLE ringing the neck (fur ruff) ─────────────────────
    # A scalloped brown ruff on the shoulders so the warm body has a fur collar
    # bridging head to chest. FUR shadow under, FUR_HI on top.
    ruff_y = HY + 9
    for i in range(-3, 4):
        fx = HX - 1 + i * 5
        r = 5 if i % 2 == 0 else 4
        pygame.draw.circle(surf, FUR, (fx, ruff_y + 1), r)
        pygame.draw.circle(surf, FUR_HI, (fx, ruff_y), r - 1)
    # Ruff tops sit at FUR_HI, not the brightest tone, so the HELM TIP/boss stay
    # the brightest points — hierarchy is iron highlights > bronze > fur.
    for i in range(-1, 2):
        pygame.draw.circle(surf, FUR_HI, (HX - 1 + i * 5, ruff_y - 1), 1)

    # ── DARK-BROWN BRAIDED BEARD with BRONZE BEARD-RINGS ─────────────────────
    # Plain braided beard hanging under the beak; each braid tip is capped with
    # a small bronze ring instead of an icicle. The two fat braids break the
    # lower outline — plain raider geometry, no ice.
    pygame.draw.ellipse(surf, BEARD, (HX - 3, HY + 6, 17, 12))
    pygame.draw.ellipse(surf, BEARD_HI, (HX - 2, HY + 5, 15, 10))
    pygame.draw.ellipse(surf, BEARD, (HX - 2, HY + 8, 15, 8))      # under-shade
    for bx in (HX + 1, HX + 7):
        # Braid shaft with a lighter twist highlight down one side.
        pygame.draw.line(surf, BEARD, (bx, HY + 9), (bx, HY + 18), 3)
        pygame.draw.line(surf, BEARD_HI, (bx - 1, HY + 9), (bx - 1, HY + 17), 1)
        # Bronze beard-ring clasping each braid near its end.
        pygame.draw.line(surf, BRONZE, (bx - 2, HY + 16), (bx + 2, HY + 16), 2)
        pygame.draw.line(surf, HELM_HI, (bx - 1, HY + 16), (bx, HY + 16), 1)

    # ── IRON BEARDED AXE in the wing/hand ────────────────────────────────────
    # Plain iron head with a bright edge glint, hafted low so the blade breaks
    # the lower-front silhouette. Drawn before the helm so the helm reads on top.
    hxr, hyr = HX + 16, HY + 20          # haft top near the wing
    htx, hty = HX + 11, HY + 32          # haft bottom
    pygame.draw.line(surf, BEARD, (hxr, hyr), (htx, hty), 4)        # wood haft
    pygame.draw.line(surf, FUR_HI, (hxr, hyr), (htx, hty), 2)
    # Bearded axe head — a swept crescent off the haft top.
    head = [(hxr - 1, hyr - 4), (hxr + 9, hyr - 6), (hxr + 11, hyr + 4),
            (hxr + 6, hyr + 9), (hxr + 1, hyr + 6)]
    _poly(surf, HELM_DK, head)
    _poly(surf, HELM, [(hxr, hyr - 3), (hxr + 8, hyr - 4), (hxr + 9, hyr + 3),
                       (hxr + 2, hyr + 4)])
    # Bright iron edge rim-glint on the cutting curve.
    pygame.draw.line(surf, HELM_HI, (hxr + 8, hyr - 4), (hxr + 10, hyr + 3), 2)
    pygame.draw.line(surf, (255, 255, 255), (hxr + 9, hyr - 2), (hxr + 10, hyr + 1), 1)

    # ── IRON HORNED SPANGENHELM ──────────────────────────────────────────────
    # Two horns sweeping up & outward with plain bone/metal tips, a domed iron
    # cap and a nasal guard. The bright iron carries the top read; the horns
    # break the crown outline.
    for sgn, hx0 in ((-1, HX - 9), (1, HX + 9)):
        tipx = hx0 + sgn * 6
        mid = (hx0 + sgn * 5, cy - 6)
        # Horn FILL is the dark BEARD brown so each horn reads as a solid mass
        # against sky; only the leading edge carries a FUR_HI sliver.
        _poly(surf, BEARD,
              [(hx0 - 4, cy + 2), (hx0 + 4, cy + 2), mid,
               (tipx + sgn * 2, cy - 16)])
        _poly(surf, FUR_HI,
              [(hx0 + sgn * 3, cy + 1), (hx0 + sgn * 4, cy + 1),
               (mid[0] + sgn, mid[1] + 1), (tipx + sgn * 2, cy - 15)])
        # Plain bone/metal horn tip — a small pale cap, not frost-white.
        pygame.draw.circle(surf, FUR_HI, (tipx + sgn, cy - 15), 3)
        pygame.draw.circle(surf, BONE, (tipx + sgn, cy - 15), 2)
        pygame.draw.circle(surf, HELM_HI, (tipx + sgn - 1, cy - 16), 1)

    # Iron spangenhelm dome — FILL is HELM_DK so the helm is the biggest dark
    # mass on the crown; HELM rides the top of the dome as a highlight band.
    pygame.draw.ellipse(surf, HELM_DK, (HX - 12, cy - 6, 25, 18))
    pygame.draw.ellipse(surf, HELM, (HX - 11, cy - 6, 23, 8))
    # Spangen ridge + a bright iron highlight band.
    pygame.draw.line(surf, HELM_DK, (HX, cy - 6), (HX, cy + 4), 2)
    pygame.draw.ellipse(surf, HELM_HI, (HX - 6, cy - 5, 9, 4))
    # Riveted brow band the horns root into, with BRONZE rivets.
    pygame.draw.line(surf, HELM_DK, (HX - 11, cy + 5), (HX + 12, cy + 4), 4)
    pygame.draw.line(surf, HELM, (HX - 11, cy + 4), (HX + 12, cy + 3), 1)
    for rx in (HX - 8, HX - 1, HX + 6):
        pygame.draw.circle(surf, BRONZE, (rx, cy + 5), 1)
    # Nasal guard.
    pygame.draw.rect(surf, HELM_DK, (HX + 1, cy + 4, 3, 11))
    pygame.draw.rect(surf, HELM, (HX + 1, cy + 4, 2, 10))

    # ── FUR BOOT CUFFS on the feet (base feet sit at y~65-69 in composite) ───
    for fx, fy in ((27, 65), (35, 65)):
        pygame.draw.circle(surf, FUR, (fx, fy + 1), 3)
        pygame.draw.circle(surf, FUR_HI, (fx, fy), 2)


def _iron_skin(paint_fn, base_fn):
    """Like store_skins._make_skin, but wraps the composited silhouette in the
    dark-brown KEYLINE instead of the shipped near-black 1px outline (carried
    over from FROSTREAVER's _frost_skin: the warm outer mass needs a dark edge
    against a bright sky). Scratch-only; production _make_skin is untouched."""
    state = {"frames": None, "rot": {}}

    def getter(frame_idx, tilt_deg):
        if state["frames"] is None:
            state["frames"] = [
                _add_outline(_compose(a, paint_fn, base_fn=base_fn),
                             outline_color=KEYLINE)
                for a in store_skins._WING_ANGLES
            ]
        frames = state["frames"]
        frame_idx %= len(frames)
        key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
        s = state["rot"].get(key)
        if s is None:
            s = pygame.transform.rotozoom(frames[frame_idx], key[1], 1.0)
            state["rot"][key] = s
        return s

    return getter


build = _iron_skin(_paint, base_fn=_iron_base)
