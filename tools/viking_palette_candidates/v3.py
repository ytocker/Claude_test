"""STORMGREY — slate-steel Viking raider (viking-redesign palette candidate, v3).

Scratch exploration ONLY — never registered in store_skins.BUILDERS; the live
skin_viking is untouched. This is the FROSTREAVER (design_4) STRUCTURE recolour:
the full winning geometry/coverage and the KEYLINE-outline wrapper are kept, but
the ice theme is removed entirely and the body is re-plumed through the 24-slot
palette to a NEUTRAL slate-steel grey — a grim stormcloud raider, deliberately
NOT a pale icy powder-blue.

North star (shared with store_skins): "a skin lives or dies at 40px in motion."
The read here is mass + value: a low-saturation mid-dark grey bird under a dark-
steel horned helm, a charcoal fur mantle, a grey-brown braided beard with silver
rings, and a plain round wooden shield with an iron boss + rim. The cool-grey
body stays separated from a blue day sky by the dark charcoal keyline wrapped
around the whole silhouette, the same mechanism the frost variant relied on.

De-frost map vs design_4: icicle beard fangs -> plain braided tips with silver
beard-rings; shield frost-crystals -> dropped (plain plank shield); horn tips ->
bone/metal, not frost-white; brim icicle drip -> dropped; ice flecks -> dropped
or recoloured to plain metal glints. No frosty pale-blue anywhere.
"""
import math
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly, _compose
from game.parrot import _add_outline
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette


# ── STORMGREY material palette (brief spec) ──────────────────────────────────
# Round-2 ITERATE: the v3 body ran cold (R-minus-B ~ -20, an overcast-blue lean
# that risked reading as frost). Warmed toward neutral-warm slate by raising R
# and dropping B so R-minus-B lands ~ +2..+4 — plain iron-grey, not icy. Value
# is held roughly constant so the night read and mass hierarchy are unchanged.
BODY       = (124, 120, 122)        # #7C787A neutral-warm slate plumage
BODY_SHADE = (80, 76, 77)           # #504C4D body shadow / line work
CHEST      = (148, 142, 143)        # #948E8F lighter chest (one value step up)
BELLY      = (102, 98, 99)          # #666263 belly

HELM       = (90, 96, 104)          # #5A6068 dark-steel helm
HELM_DARK  = (52, 56, 62)           # #34383E helm shadow / horn fill mass
HELM_HI    = (184, 192, 202)        # #B8C0CA steel highlight / rivets

FUR        = (62, 66, 74)           # #3E424A charcoal-grey fur mantle
FUR_HI     = (94, 100, 110)         # #5E646E fur highlight

BEARD      = (74, 70, 62)           # #4A463E grey-brown braid
BEARD_DARK = (46, 44, 40)           # #2E2C28 braid shadow
BEARD_RING = (198, 204, 212)        # #C6CCD4 silver beard-ring

# Round-2 ITERATE: against the warmed body the shield field must read as a
# deliberate PAINTED accent, not a hole. Field pushed bluer AND darker so it
# pops cool against the warm body, and the iron rim/boss base is deepened ~12
# value to frame the disc as a hard ring around it.
SHIELD_PLANK = (112, 116, 124)      # #70747C cool steel-grey planks
SHIELD_FIELD = (58, 78, 104)        # #3A4E68 deep painted blue-grey field
IRON         = (40, 44, 50)         # #282C32 deepened iron boss / rim base
IRON_HI      = (172, 180, 190)      # iron highlight

# Frost relied on a cold mid-dark keyline so the pale mass held an edge on day
# sky. Stormgrey is mid-dark already, but the keyline still does the day-read
# work: charcoal #22262C wraps the WHOLE composited silhouette so the cool-grey
# back/belly never melts into a blue sky, and the helm reads as a hard mass.
KEYLINE = (34, 38, 44, 235)         # #22262C charcoal outer keyline


# Full slate-steel re-plumage of the macaw. Every slot is shifted to neutral
# low-saturation grey; the wing TIP / highlight slots carry a cool steel edge
# (not frost-white), and the deepest body-shade owns the line work so the mid
# mass still holds a crisp edge on a bright day sky. Lenses are dropped so the
# helm brow + beard own the face, exactly as the winning structure did.
P_STORM = _pal(
    tail=[(108, 104, 105), (120, 116, 117), (132, 128, 129), (150, 145, 146)],
    tail_line=BODY_SHADE,
    body_shadow=(86, 82, 83),       # warmed with the body; near BODY_SHADE so
                                    # the back/belly edge still holds an edge
    body_main=BODY,
    body_chest=CHEST,
    body_belly=BELLY,
    sheen=(238, 236, 234, 70),      # restrained warm-steel sheen, not icy glint
    # Wing/back kept one hair COOLER and a touch darker than the warmed body so
    # the front chest mass reads forward of the wing without going pale.
    wing_main=(108, 109, 116),
    wing_dark=(66, 66, 72),
    wing_tip=(156, 156, 162),       # cool steel edge on the leading tips
    wing_secondary=None,
    wing_highlight=(166, 166, 172), # crisp steel rim on the wing
    head_shadow=(86, 82, 83),
    head_main=BODY,
    head_cheek=(138, 133, 134),
    head_crown=(148, 143, 144),
    lens_frame=(108, 105, 108),
    lens_body=(44, 42, 43),
    lens_tint=None,
    lens_glint=None,
    beak_main=(128, 124, 122),      # neutral-warm grey horn, matches the body
    beak_dark=BODY_SHADE,
    beak_gloss=(176, 172, 170),
    foot=(104, 100, 99),
)


def _storm_base(angle_deg):
    # Slate bird, no aviators — the helm brow + braided beard own the face.
    return _build_parrot_with_palette(angle_deg, P_STORM, draw_lenses=False)


# ── costume paint ────────────────────────────────────────────────────────────

def _paint(surf, wing_angle_deg):
    cy = CROWN_Y

    # ── ROUND WOODEN SHIELD on the BACK (drawn first, behind the body) ───────
    # Plain planks + a muted blue-grey painted field + iron boss + iron rim.
    # No frost crystals — the round disc itself, broken only by the boss, is the
    # back read at 40px. Same position/radius as the winning structure.
    sx, sy, sr = HX - 26, HY + 11, 13
    pygame.draw.circle(surf, IRON, (sx, sy), sr + 1)              # iron rim base
    pygame.draw.circle(surf, SHIELD_PLANK, (sx, sy), sr)         # plank face
    # Muted blue-grey painted central field (the shield's only colour accent).
    pygame.draw.circle(surf, SHIELD_FIELD, (sx, sy), sr - 4)
    # Plank seams across the face.
    for dx in (-7, 0, 7):
        pygame.draw.line(surf, IRON, (sx + dx, sy - sr + 2),
                         (sx + dx, sy + sr - 2), 1)
    # Iron rim ring + studded iron boss with a hard metal glint.
    pygame.draw.circle(surf, IRON, (sx, sy), sr, 2)
    pygame.draw.circle(surf, IRON_HI, (sx, sy), sr, 1)
    pygame.draw.circle(surf, IRON, (sx, sy), 5)
    pygame.draw.circle(surf, IRON_HI, (sx, sy), 4)
    pygame.draw.circle(surf, IRON, (sx, sy), 4, 1)
    pygame.draw.circle(surf, (220, 226, 234), (sx - 1, sy - 1), 1)

    # ── CHARCOAL WOLF-FUR MANTLE ringing the neck ────────────────────────────
    # A scalloped charcoal ruff on the shoulders so the slate body has a darker
    # fur collar bridging head to chest. Recoloured from snowy white to charcoal
    # so the helm steel stays the brightest point, not the ruff.
    ruff_y = HY + 9
    for i in range(-3, 4):
        fx = HX - 1 + i * 5
        r = 5 if i % 2 == 0 else 4
        pygame.draw.circle(surf, BEARD_DARK, (fx, ruff_y + 1), r)
        pygame.draw.circle(surf, FUR, (fx, ruff_y), r - 1)
    # Three muted fur-highlight dots, not five — keeps the band quiet under the
    # helm so hierarchy stays helm > shield boss > ruff.
    for i in range(-1, 2):
        pygame.draw.circle(surf, FUR_HI, (HX - 1 + i * 5, ruff_y - 1), 1)

    # ── GREY-BROWN BRAIDED BEARD with SILVER BEARD-RINGS ─────────────────────
    # Plain braided ends bound with silver rings instead of icicle fangs. The
    # braid mass still breaks the lower outline, but reads as woven hair, warm-
    # grey not frosty.
    pygame.draw.ellipse(surf, BEARD_DARK, (HX - 3, HY + 6, 17, 12))
    pygame.draw.ellipse(surf, BEARD, (HX - 2, HY + 5, 15, 10))
    for bx in (HX + 1, HX + 7):
        pygame.draw.line(surf, BEARD_DARK, (bx, HY + 9), (bx, HY + 16), 3)
        pygame.draw.line(surf, BEARD, (bx - 1, HY + 9), (bx - 1, HY + 15), 1)
    # Silver beard-rings binding each braid near its tip (the icicle replacement
    # — a deliberate countable shape at 40px, plain metal not ice).
    for bx in (HX + 1, HX + 7):
        pygame.draw.line(surf, BEARD_RING, (bx - 2, HY + 14), (bx + 1, HY + 14), 2)
        pygame.draw.circle(surf, BEARD_RING, (bx, HY + 17), 1)
    pygame.draw.line(surf, (224, 228, 234), (HX, HY + 14), (HX + 1, HY + 14), 1)

    # ── STEEL BEARDED AXE in the wing/hand ───────────────────────────────────
    # Plain dark-steel head with a cool metal edge-glint (not ice), hafted low
    # so the blade breaks the lower-front silhouette. Drawn before the helm.
    hxr, hyr = HX + 16, HY + 20          # haft top near the wing
    htx, hty = HX + 11, HY + 32          # haft bottom
    pygame.draw.line(surf, BEARD_DARK, (hxr, hyr), (htx, hty), 4)   # dark haft
    pygame.draw.line(surf, BEARD, (hxr, hyr), (htx, hty), 2)
    # Bearded axe head — a swept crescent off the haft top.
    head = [(hxr - 1, hyr - 4), (hxr + 9, hyr - 6), (hxr + 11, hyr + 4),
            (hxr + 6, hyr + 9), (hxr + 1, hyr + 6)]
    _poly(surf, HELM_DARK, head)
    _poly(surf, HELM, [(hxr, hyr - 3), (hxr + 8, hyr - 4), (hxr + 9, hyr + 3),
                       (hxr + 2, hyr + 4)])
    # Bright steel edge rim-glint on the cutting curve.
    pygame.draw.line(surf, HELM_HI, (hxr + 8, hyr - 4), (hxr + 10, hyr + 3), 2)
    pygame.draw.line(surf, (220, 226, 234), (hxr + 9, hyr - 2), (hxr + 10, hyr + 1), 1)

    # ── DARK-STEEL HORNED SPANGENHELM ────────────────────────────────────────
    # Two horns sweeping up & outward with plain bone/metal tips, a domed cap,
    # brow band and nasal guard. The steel helm carries the top read; the horn
    # tips break the crown outline as deliberate points (not frost-white).
    for sgn, hx0 in ((-1, HX - 9), (1, HX + 9)):
        tipx = hx0 + sgn * 6
        mid = (hx0 + sgn * 5, cy - 6)
        # Horn FILL is the dark HELM_DARK so each horn reads as a solid mass
        # against blue sky; only the leading edge carries a steel sliver.
        _poly(surf, HELM_DARK,
              [(hx0 - 4, cy + 2), (hx0 + 4, cy + 2), mid,
               (tipx + sgn * 2, cy - 16)])
        _poly(surf, HELM,
              [(hx0 + sgn * 3, cy + 1), (hx0 + sgn * 4, cy + 1),
               (mid[0] + sgn, mid[1] + 1), (tipx + sgn * 2, cy - 15)])
        # Plain bone/metal horn tip — a steel point, not a frost glint.
        pygame.draw.circle(surf, HELM, (tipx + sgn, cy - 15), 3)
        pygame.draw.circle(surf, HELM_HI, (tipx + sgn, cy - 15), 2)
        pygame.draw.circle(surf, (220, 226, 234), (tipx + sgn - 1, cy - 16), 1)

    # Dark-steel spangenhelm dome — FILL is HELM_DARK so the helm is the biggest
    # dark mass on the crown; HELM is demoted to a highlight band on the top.
    pygame.draw.ellipse(surf, HELM_DARK, (HX - 12, cy - 6, 25, 18))
    pygame.draw.ellipse(surf, HELM, (HX - 11, cy - 6, 23, 8))
    # Spangen ridge + a steel highlight band.
    pygame.draw.line(surf, HELM_DARK, (HX, cy - 6), (HX, cy + 4), 2)
    pygame.draw.ellipse(surf, HELM_HI, (HX - 6, cy - 5, 9, 4))
    # Riveted brow band the horns root into.
    pygame.draw.line(surf, HELM_DARK, (HX - 11, cy + 5), (HX + 12, cy + 4), 4)
    pygame.draw.line(surf, HELM_HI, (HX - 11, cy + 4), (HX + 12, cy + 3), 1)
    for rx in (HX - 8, HX - 1, HX + 6):
        pygame.draw.circle(surf, HELM_HI, (rx, cy + 5), 1)
    # Nasal guard.
    pygame.draw.rect(surf, HELM_DARK, (HX + 1, cy + 4, 3, 11))
    pygame.draw.rect(surf, HELM, (HX + 1, cy + 4, 2, 10))

    # ── FUR BOOT CUFFS on the feet (base feet sit at y~65-69 in composite) ───
    for fx, fy in ((27, 65), (35, 65)):
        pygame.draw.circle(surf, BEARD_DARK, (fx, fy + 1), 3)
        pygame.draw.circle(surf, FUR, (fx, fy), 2)


def _storm_skin(paint_fn, base_fn):
    """Like store_skins._make_skin, but wraps the composited silhouette in the
    charcoal KEYLINE instead of the shipped near-black 1px outline — the same
    wrapper mechanism the FROSTREAVER structure used for its day read, kept
    intact and recoloured to this palette's dark keyline. Scratch-only;
    production _make_skin is untouched."""
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


build = _storm_skin(_paint, base_fn=_storm_base)
