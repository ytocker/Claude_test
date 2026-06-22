"""WOADGREEN — Woad-painted forest raider (viking palette pass, design_4 v4).

Scratch exploration ONLY — never registered in store_skins.BUILDERS; the live
skin_viking is untouched. This is a PLAIN-Viking recolour of the design_4
FROSTREAVER structure: the SAME winning geometry (horned spangenhelm, big
braided beard, fur ruff, back round shield, bearded axe, fur boot cuffs) and
the SAME outer-keyline wrapper mechanism (``_woad_skin``), but the ice theme is
stripped out entirely. The macaw is re-plumaged through the 24-slot palette to
mossy olive green-brown — an earthy woodland raider, not a frost one.

De-frost moves vs design_4:
  * icicle beard fangs → plain braided-beard tips with bronze beard-rings;
  * shield frost-crystals dropped → plain round WOODEN shield (green painted
    field + iron boss + iron rim + wood rim);
  * horn TIPS recoloured to plain bone, not frost-white;
  * brim icicle drip dropped; ice flecks recoloured to plain metal glints.

North star (shared with store_skins): "a skin lives or dies at 40px in motion."
The olive body recolour is the loud read; the helm + green shield field carry
the colour story, and the dark green-brown KEYLINE wraps the WHOLE silhouette
so the earthy mass holds its edge against both a day and a night sky.
"""
import math
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly, _compose
from game.parrot import _add_outline
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette


# ── WOADGREEN palette (brief spec) ───────────────────────────────────────────
BODY      = (94, 107, 58)           # #5E6B3A mossy olive plumage
BODY_SHAD = (58, 68, 36)            # #3A4424 olive shadow / line work
BODY_HI   = (118, 132, 74)          # #76844A lit chest
BODY_BELLY= (74, 86, 48)            # #4A5630 deep belly

HELM      = (154, 122, 58)          # #9A7A3A bronze helm
HELM_DK   = (94, 74, 34)            # #5E4A22 bronze shadow
HELM_HI   = (210, 184, 106)         # #D2B86A bronze highlight

FUR       = (90, 70, 50)            # #5A4632 brown fur mantle
FUR_HI    = (122, 96, 68)           # #7A6044 lit fur

BEARD     = (110, 58, 30)           # #6E3A1E auburn beard
BEARD_DK  = (74, 38, 20)            # #4A2614 beard shadow
RING      = (200, 154, 58)          # #C89A3A bronze beard-ring

SHIELD_FLD= (62, 107, 58)           # #3E6B3A green painted shield field
SHIELD_RIM= (110, 82, 56)           # #6E5238 wood shield rim
IRON      = (96, 96, 100)           # iron boss / rim (cool grey)
IRON_DK   = (52, 52, 56)            # iron shadow
IRON_HI   = (176, 178, 184)         # iron highlight / metal glint
BONE      = (212, 200, 168)         # plain bone horn tips

# A plain near-black 1px outline reads thin against an olive mass and goes
# muddy on a dark night sky. A dark green-brown keyline (#22281A) wrapped
# around the WHOLE composited silhouette holds the value separation on both
# day and night — same mechanism as design_4's cold keyline, recoloured.
KEYLINE = (34, 40, 26, 235)         # #22281A dark green-brown outer keyline


# Full olive re-plumage of the macaw. Every slot is shifted to mossy
# green-brown; the chest / belly carry the lit olive, and the deepest olive
# shadow owns the line work so the mass holds a crisp edge. Lenses dropped so
# the bronze helm + brow own the face (matches design_4's no-aviators choice).
P_WOAD = _pal(
    tail=[(70, 80, 44), (84, 96, 52), (100, 112, 62), (118, 130, 74)],
    tail_line=BODY_SHAD,
    body_shadow=BODY_SHAD,
    body_main=BODY,
    body_chest=BODY_HI,
    body_belly=BODY_BELLY,
    sheen=(210, 220, 170, 70),
    wing_main=(86, 98, 54),
    wing_dark=(54, 62, 32),
    wing_tip=(126, 138, 80),
    wing_secondary=None,
    wing_highlight=(140, 152, 92),
    head_shadow=BODY_SHAD,
    head_main=BODY,
    head_cheek=(112, 126, 70),
    head_crown=(120, 134, 76),
    lens_frame=(86, 98, 54),
    lens_body=(40, 46, 30),
    lens_tint=None,
    lens_glint=None,
    beak_main=(150, 130, 78),           # warm horn beak, earthy not frost
    beak_dark=(96, 80, 44),
    beak_gloss=(196, 176, 116),
    foot=(120, 98, 60),
)


def _woad_base(angle_deg):
    # Olive forest bird, no aviators — the bronze helm brow + beard own the face.
    return _build_parrot_with_palette(angle_deg, P_WOAD, draw_lenses=False)


# ── costume paint ────────────────────────────────────────────────────────────

def _paint(surf, wing_angle_deg):
    cy = CROWN_Y

    # ── ROUND WOODEN SHIELD on the BACK (drawn first, behind the body) ───────
    # Plain green-painted plank field + iron boss + iron rim + wood rim. No
    # frost crystals — the clean round disc is the woodland raider's shield and
    # its green field carries the colour story past the downscale.
    sx, sy, sr = HX - 26, HY + 11, 13
    pygame.draw.circle(surf, SHIELD_RIM, (sx, sy), sr + 1)     # wood rim
    pygame.draw.circle(surf, SHIELD_FLD, (sx, sy), sr)         # green field
    # Plank seams across the painted face.
    for dx in (-7, 0, 7):
        pygame.draw.line(surf, (48, 84, 46), (sx + dx, sy - sr + 2),
                         (sx + dx, sy + sr - 2), 1)
    # Iron rim band + bright iron boss with a hard glint.
    pygame.draw.circle(surf, IRON, (sx, sy), sr, 2)
    pygame.draw.circle(surf, IRON_DK, (sx, sy), 5)
    pygame.draw.circle(surf, IRON, (sx, sy), 4)
    pygame.draw.circle(surf, IRON_HI, (sx, sy), 4, 1)
    pygame.draw.circle(surf, (235, 236, 240), (sx - 1, sy - 1), 1)

    # ── BROWN WOLF-FUR MANTLE ringing the neck ───────────────────────────────
    # A scalloped brown ruff sitting on the shoulders so the olive body has a
    # warm fur collar bridging head to chest.
    ruff_y = HY + 9
    for i in range(-3, 4):
        fx = HX - 1 + i * 5
        r = 5 if i % 2 == 0 else 4
        pygame.draw.circle(surf, BODY_SHAD, (fx, ruff_y + 1), r)
        pygame.draw.circle(surf, FUR, (fx, ruff_y), r - 1)
    # Lit fur tufts — kept below the helm tips so hierarchy stays
    # helm-tips > boss > fur. Three lit dots, not five (avoids a crowded band).
    for i in range(-1, 2):
        pygame.draw.circle(surf, FUR_HI, (HX - 1 + i * 5, ruff_y - 1), 1)

    # ── AUBURN BRAIDED BEARD with bronze BEARD-RINGS ─────────────────────────
    # Auburn braids hanging under the beak, ending in plain braid tips clasped
    # with bronze rings instead of icicles — the warm, plain Viking read.
    pygame.draw.ellipse(surf, BEARD_DK, (HX - 3, HY + 6, 17, 12))
    pygame.draw.ellipse(surf, BEARD, (HX - 2, HY + 5, 15, 10))
    for bx in (HX + 1, HX + 7):
        pygame.draw.line(surf, BEARD_DK, (bx, HY + 9), (bx, HY + 17), 3)
        pygame.draw.line(surf, BEARD, (bx - 1, HY + 9), (bx - 1, HY + 16), 1)
        # Bronze beard-ring clasping each braid near its tip.
        pygame.draw.line(surf, RING, (bx - 2, HY + 15), (bx + 2, HY + 15), 2)
        pygame.draw.line(surf, HELM_HI, (bx - 2, HY + 15), (bx + 2, HY + 15), 1)
    # Plain braid tips (no ice). A couple of bronze hair-bead glints along it.
    for fx, fy in ((HX, HY + 9), (HX + 5, HY + 11), (HX + 9, HY + 8)):
        pygame.draw.circle(surf, RING, (fx, fy), 1)

    # ── BEARDED AXE in the wing/hand ─────────────────────────────────────────
    # Plain steel head with an iron highlight, hafted low so the blade breaks
    # the lower-front silhouette. Drawn before the helm so the helm reads on top.
    hxr, hyr = HX + 16, HY + 20          # haft top near the wing
    htx, hty = HX + 11, HY + 32          # haft bottom
    pygame.draw.line(surf, (74, 54, 34), (hxr, hyr), (htx, hty), 4)   # wood haft
    pygame.draw.line(surf, (120, 92, 56), (hxr, hyr), (htx, hty), 2)
    # Bearded axe head — a swept crescent off the haft top.
    head = [(hxr - 1, hyr - 4), (hxr + 9, hyr - 6), (hxr + 11, hyr + 4),
            (hxr + 6, hyr + 9), (hxr + 1, hyr + 6)]
    _poly(surf, IRON_DK, head)
    _poly(surf, IRON, [(hxr, hyr - 3), (hxr + 8, hyr - 4), (hxr + 9, hyr + 3),
                       (hxr + 2, hyr + 4)])
    # Bright steel edge glint on the cutting curve (plain metal, not ice).
    pygame.draw.line(surf, IRON_HI, (hxr + 8, hyr - 4), (hxr + 10, hyr + 3), 2)
    pygame.draw.line(surf, (235, 236, 240), (hxr + 9, hyr - 2), (hxr + 10, hyr + 1), 1)

    # ── HORNED SPANGENHELM (bronze) ──────────────────────────────────────────
    # Two horns sweeping up & outward with plain BONE tips, a domed bronze cap
    # and a nasal guard. The bright bronze helm carries the top read while the
    # horns break the crown outline.
    for sgn, hx0 in ((-1, HX - 9), (1, HX + 9)):
        tipx = hx0 + sgn * 6
        mid = (hx0 + sgn * 5, cy - 6)
        # Horn FILL is a dark warm bone-shadow so each horn reads as a solid
        # mass; only the leading edge carries a bone highlight.
        _poly(surf, (88, 74, 52),
              [(hx0 - 4, cy + 2), (hx0 + 4, cy + 2), mid,
               (tipx + sgn * 2, cy - 16)])
        _poly(surf, (158, 142, 108),
              [(hx0 + sgn * 3, cy + 1), (hx0 + sgn * 4, cy + 1),
               (mid[0] + sgn, mid[1] + 1), (tipx + sgn * 2, cy - 15)])
        # Plain bone horn tip — kept bright; the top focal point.
        pygame.draw.circle(surf, (158, 142, 108), (tipx + sgn, cy - 15), 3)
        pygame.draw.circle(surf, BONE, (tipx + sgn, cy - 15), 2)
        pygame.draw.circle(surf, (240, 234, 214), (tipx + sgn - 1, cy - 16), 1)

    # Bronze spangenhelm dome — FILL is the dark bronze so the helm is the
    # biggest mass on the crown; HELM is demoted to a highlight band on top.
    pygame.draw.ellipse(surf, HELM_DK, (HX - 12, cy - 6, 25, 18))
    pygame.draw.ellipse(surf, HELM, (HX - 11, cy - 6, 23, 8))
    # Spangen ridge + a bright bronze highlight band.
    pygame.draw.line(surf, HELM_DK, (HX, cy - 6), (HX, cy + 4), 2)
    pygame.draw.ellipse(surf, HELM_HI, (HX - 6, cy - 5, 9, 4))
    # Riveted brow band the horns root into.
    pygame.draw.line(surf, HELM_DK, (HX - 11, cy + 5), (HX + 12, cy + 4), 4)
    pygame.draw.line(surf, HELM_HI, (HX - 11, cy + 4), (HX + 12, cy + 3), 1)
    for rx in (HX - 8, HX - 1, HX + 6):
        pygame.draw.circle(surf, HELM_HI, (rx, cy + 5), 1)
    # Nasal guard.
    pygame.draw.rect(surf, HELM_DK, (HX + 1, cy + 4, 3, 11))
    pygame.draw.rect(surf, HELM, (HX + 1, cy + 4, 2, 10))

    # ── FUR BOOT CUFFS on the feet (base feet sit at y~65-69 in composite) ───
    for fx, fy in ((27, 65), (35, 65)):
        pygame.draw.circle(surf, BODY_SHAD, (fx, fy + 1), 3)
        pygame.draw.circle(surf, FUR, (fx, fy), 2)


def _woad_skin(paint_fn, base_fn):
    """Like store_skins._make_skin, but wraps the composited silhouette in the
    dark green-brown KEYLINE instead of the shipped near-black 1px outline. The
    olive mass needs a darker, warmer edge to separate from both a day and a
    night sky. Same wrapper mechanism as design_4's _frost_skin, recoloured.
    Scratch-only; production _make_skin is untouched."""
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


build = _woad_skin(_paint, base_fn=_woad_base)
