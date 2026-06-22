"""GOLDMANE — fair-haired northman (viking-redesign v5 PALETTE recolor).

Scratch exploration ONLY — never registered in store_skins.BUILDERS; the live
skin_viking is untouched. This is a PLAIN-Viking colour pass over the WINNING
design_4 (FROSTREAVER) STRUCTURE: same 24-slot body re-plumage mechanism, same
KEYLINE-wrapped composite, same horned-helm + braided-beard + round-shield +
bearded-axe kit and coverage — but the ice theme is removed entirely.

De-frosted into a sun-bleached natural northman: sandy tawny-blonde plumage,
polished-iron helm, cream fur mantle, a blonde braided beard ending in plain
tips with one gold ring (no icicle fangs), a plain honey-wood plank shield with
an iron boss + rim and a few gold accents (no frost crystals), bone/metal horn
tips (not frost-white), no brim drip, and metal glints in place of ice flecks.
Plain, not the opulent gold-jarl: tan/blonde, never gilded.

North star (shared with store_skins): "a skin lives or dies at 40px in motion."
The warm sandy body recolour is the loudest read of the tier — a fair Viking —
and the horned helm + beard + shield kit breaks the silhouette top/front/back.
Every object is mass + one bright metal/gold accent so the stack survives the
downscale. The dark warm-brown KEYLINE wrapped round the whole silhouette holds
the value separation against a bright day sky.
"""
import math
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly, _compose
from game.parrot import _add_outline
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette


# ── GOLDMANE palette (brief spec) ────────────────────────────────────────────
BODY      = (201, 168, 106)         # #C9A86A sandy tawny-blonde plumage
BODY_DK   = (154, 126, 72)          # #9A7E48 plumage shadow
CHEST     = (220, 192, 136)         # #DCC088 lighter chest
BELLY     = (184, 152, 88)          # #B89858 belly

HELM      = (144, 152, 164)         # #9098A4 polished iron
HELM_DK   = (90, 96, 108)           # #5A606C iron shadow / line work
HELM_HI   = (220, 226, 234)         # #DCE2EA iron highlight

FUR       = (184, 160, 116)         # #B8A074 cream/tan fur mantle
FUR_HI    = (216, 196, 154)         # #D8C49A fur highlight

BEARD     = (201, 162, 75)          # #C9A24B blonde braid
BEARD_DK  = (154, 122, 52)          # #9A7A34 braid shadow

WOOD      = (196, 154, 82)          # #C49A52 honey shield planks
GOLD      = (227, 178, 60)          # #E3B23C gold accent / beard-ring

# Warm dark-brown outer keyline — the day-read fix carried over from design_4,
# recoloured from the cold #2E4658 to this palette's warm #2E2214 so the sandy
# mass keeps a crisp dark edge against a bright day sky.
KEYLINE   = (46, 34, 20, 235)       # #2E2214 warm dark keyline


# Full sandy-blonde re-plumage of the macaw. Every slot is shifted to warm
# tawny tones; the wing TIP / highlight slots carry a sun-bleached pale edge,
# and the deepest BODY_DK / brown owns the line work so the warm mass still
# holds a crisp edge. Lenses are dropped so the helm + beard own the face.
P_GOLD = _pal(
    tail=[(150, 122, 70), (170, 140, 84), (188, 158, 98), (208, 178, 116)],
    tail_line=(96, 74, 40),
    body_shadow=BODY_DK,
    body_main=BODY,
    body_chest=CHEST,
    body_belly=BELLY,
    sheen=(255, 248, 224, 90),
    wing_main=(186, 154, 92),
    wing_dark=(120, 96, 54),
    wing_tip=(224, 200, 148),           # sun-bleached pale feather tips
    wing_secondary=None,
    wing_highlight=(232, 212, 164),     # crisp warm rim on the wing
    head_shadow=BODY_DK,
    head_main=BODY,
    head_cheek=(218, 190, 132),
    head_crown=(224, 196, 138),
    lens_frame=(150, 122, 70),
    lens_body=(40, 32, 20),
    lens_tint=None,
    lens_glint=None,
    beak_main=(176, 150, 104),          # warm horn beak
    beak_dark=(112, 90, 52),
    beak_gloss=(224, 204, 158),
    foot=(150, 120, 72),
)


def _gold_base(angle_deg):
    # Sandy-blonde bird, no aviators — the helm brow + braided beard own the face.
    return _build_parrot_with_palette(angle_deg, P_GOLD, draw_lenses=False)


# ── costume paint ────────────────────────────────────────────────────────────

def _paint(surf, wing_angle_deg):
    cy = CROWN_Y

    # ── ROUND WOODEN SHIELD on the BACK (drawn first, behind the body) ───────
    # Plain honey-wood planks + iron boss + iron rim, with a few gold accents.
    # Frost crystals are dropped entirely — the disc is a clean circle so the
    # back outline reads as a solid raider's shield at 40px.
    sx, sy, sr = HX - 26, HY + 11, 13
    pygame.draw.circle(surf, BEARD_DK, (sx, sy), sr + 1)           # dark seat
    pygame.draw.circle(surf, WOOD, (sx, sy), sr)                   # plank face
    # Plank seams across the wood face.
    for dx in (-7, 0, 7):
        pygame.draw.line(surf, BEARD_DK, (sx + dx, sy - sr + 2),
                         (sx + dx, sy + sr - 2), 1)
    # Iron rim ring (was a rime ring) + bright iron boss with a hard glint.
    pygame.draw.circle(surf, HELM, (sx, sy), sr, 2)
    pygame.draw.circle(surf, HELM_DK, (sx, sy), 5)
    pygame.draw.circle(surf, HELM, (sx, sy), 4)
    pygame.draw.circle(surf, HELM_DK, (sx, sy), 4, 1)
    pygame.draw.circle(surf, HELM_HI, (sx - 1, sy - 1), 1)
    # A few gold rivet accents on the rim — the shield's one warm spark.
    for ang in (45, 180, 315):
        rad = math.radians(ang)
        gx = int(sx + (sr - 1) * math.cos(rad))
        gy = int(sy + (sr - 1) * math.sin(rad))
        pygame.draw.circle(surf, GOLD, (gx, gy), 1)

    # ── CREAM-FUR MANTLE ringing the neck ────────────────────────────────────
    # A scalloped tan ruff sitting on the shoulders so the warm body has a
    # cream fur collar bridging head to chest.
    ruff_y = HY + 9
    for i in range(-3, 4):
        fx = HX - 1 + i * 5
        r = 5 if i % 2 == 0 else 4
        pygame.draw.circle(surf, BEARD_DK, (fx, ruff_y + 1), r)
        pygame.draw.circle(surf, FUR, (fx, ruff_y), r - 1)
    # Three fur highlights, kept below the helm tips in brightness so the
    # hierarchy stays helm > shield boss > ruff.
    for i in range(-1, 2):
        pygame.draw.circle(surf, FUR_HI, (HX - 1 + i * 5, ruff_y - 1), 1)

    # ── BLONDE BRAIDED BEARD with PLAIN tips + ONE gold ring ─────────────────
    # Tawny-blonde braids hanging under the beak. Icicle fangs are removed: the
    # braids end in plain rounded tips, and a single gold beard-ring clasps one
    # braid — the beard's one warm accent. Metal glints replace ice flecks.
    pygame.draw.ellipse(surf, BEARD_DK, (HX - 3, HY + 6, 17, 12))
    pygame.draw.ellipse(surf, BEARD, (HX - 2, HY + 5, 15, 10))
    for bx in (HX + 1, HX + 7):
        pygame.draw.line(surf, BEARD_DK, (bx, HY + 9), (bx, HY + 16), 3)
        pygame.draw.line(surf, BEARD, (bx - 1, HY + 9), (bx - 1, HY + 15), 1)
    # Plain rounded braid ends (no icicles) — two fat braid tips.
    for bx in (HX + 1, HX + 7):
        pygame.draw.line(surf, BEARD, (bx, HY + 16), (bx, HY + 22), 3)
        pygame.draw.circle(surf, BEARD_DK, (bx, HY + 22), 2)
        pygame.draw.circle(surf, BEARD, (bx, HY + 22), 1)
    # ONE gold beard-ring clasping the left braid.
    pygame.draw.line(surf, GOLD, (HX, HY + 18), (HX + 2, HY + 18), 3)
    pygame.draw.line(surf, HELM_HI, (HX, HY + 17), (HX + 2, HY + 17), 1)

    # ── BEARDED AXE in the wing/hand ─────────────────────────────────────────
    # Polished-iron head with a warm metal rim-glint, hafted low so the blade
    # breaks the lower-front silhouette. Drawn before the helm so the helm reads
    # on top of the head. (No icicle off the blade.)
    hxr, hyr = HX + 16, HY + 20          # haft top near the wing
    htx, hty = HX + 11, HY + 32          # haft bottom
    pygame.draw.line(surf, BEARD_DK, (hxr, hyr), (htx, hty), 4)   # wood haft
    pygame.draw.line(surf, WOOD, (hxr, hyr), (htx, hty), 2)
    # Bearded axe head — a swept crescent off the haft top.
    head = [(hxr - 1, hyr - 4), (hxr + 9, hyr - 6), (hxr + 11, hyr + 4),
            (hxr + 6, hyr + 9), (hxr + 1, hyr + 6)]
    _poly(surf, HELM_DK, head)
    _poly(surf, HELM, [(hxr, hyr - 3), (hxr + 8, hyr - 4), (hxr + 9, hyr + 3),
                       (hxr + 2, hyr + 4)])
    # Bright iron edge rim-glint on the cutting curve.
    pygame.draw.line(surf, HELM_HI, (hxr + 8, hyr - 4), (hxr + 10, hyr + 3), 2)
    pygame.draw.line(surf, (255, 255, 255), (hxr + 9, hyr - 2), (hxr + 10, hyr + 1), 1)

    # ── POLISHED-IRON HORNED SPANGENHELM ─────────────────────────────────────
    # Two horns sweeping up & outward with plain BONE/metal tips (not frost),
    # a domed iron cap and a nasal guard. The bright helm carries the top read
    # while the horns break the crown outline. No brim drip.
    HORN      = (212, 196, 158)         # warm bone horn body
    HORN_DK   = (150, 130, 92)          # bone shadow / line
    HORN_TIP  = (236, 224, 196)         # plain bone tip (not frost-white)
    for sgn, hx0 in ((-1, HX - 9), (1, HX + 9)):
        tipx = hx0 + sgn * 6
        mid = (hx0 + sgn * 5, cy - 6)
        # Horn FILL is a solid bone mass against sky; leading edge a bright bone
        # sliver. Tips are plain bone, NOT the bright focal point the helm is.
        _poly(surf, HORN_DK,
              [(hx0 - 4, cy + 2), (hx0 + 4, cy + 2), mid,
               (tipx + sgn * 2, cy - 16)])
        _poly(surf, HORN,
              [(hx0 + sgn * 3, cy + 1), (hx0 + sgn * 4, cy + 1),
               (mid[0] + sgn, mid[1] + 1), (tipx + sgn * 2, cy - 15)])
        # Plain bone tip.
        pygame.draw.circle(surf, HORN_DK, (tipx + sgn, cy - 15), 3)
        pygame.draw.circle(surf, HORN_TIP, (tipx + sgn, cy - 15), 2)
        pygame.draw.circle(surf, HELM_HI, (tipx + sgn - 1, cy - 16), 1)

    # Iron spangenhelm dome — HELM_DK fill so the helm is the biggest dark mass
    # on the crown; HELM is a highlight band riding the top of the dome only,
    # and HELM_HI is the single brightest point (the top focal read).
    pygame.draw.ellipse(surf, HELM_DK, (HX - 12, cy - 6, 25, 18))
    pygame.draw.ellipse(surf, HELM, (HX - 11, cy - 6, 23, 8))
    # Spangen ridge + a bright iron highlight band.
    pygame.draw.line(surf, HELM_DK, (HX, cy - 6), (HX, cy + 4), 2)
    pygame.draw.ellipse(surf, HELM_HI, (HX - 6, cy - 5, 9, 4))
    # Riveted brow band the horns root into.
    pygame.draw.line(surf, HELM_DK, (HX - 11, cy + 5), (HX + 12, cy + 4), 4)
    pygame.draw.line(surf, HELM_HI, (HX - 11, cy + 4), (HX + 12, cy + 3), 1)
    for rx in (HX - 8, HX - 1, HX + 6):
        pygame.draw.circle(surf, HELM_HI, (rx, cy + 5), 1)
    # One gold rivet centred on the brow band — a small warm spark on the helm.
    pygame.draw.circle(surf, GOLD, (HX - 1, cy + 5), 1)
    # Nasal guard.
    pygame.draw.rect(surf, HELM_DK, (HX + 1, cy + 4, 3, 11))
    pygame.draw.rect(surf, HELM, (HX + 1, cy + 4, 2, 10))

    # ── FUR BOOT CUFFS on the feet (base feet sit at y~65-69 in composite) ────
    for fx, fy in ((27, 65), (35, 65)):
        pygame.draw.circle(surf, BEARD_DK, (fx, fy + 1), 3)
        pygame.draw.circle(surf, FUR, (fx, fy), 2)


def _gold_skin(paint_fn, base_fn):
    """Like store_skins._make_skin, but wraps the composited silhouette in the
    warm KEYLINE instead of the shipped near-black 1px outline — the design_4
    keyline mechanism kept, recoloured to this palette's dark warm brown so the
    sandy outer mass holds a crisp edge against a bright day sky.
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


build = _gold_skin(_paint, base_fn=_gold_base)
