"""BLOODAXE — the warm rust/red raider (viking-palette candidate, v2).

Scratch exploration ONLY — never registered in store_skins.BUILDERS; the live
skin_viking is untouched. This is a PLAIN-Viking recolour pass over the winning
FROSTREAVER (design_4) STRUCTURE: same horned spangenhelm, big braided beard,
fur ruff, back round shield, bearded axe, boot cuffs and the same dark outer
KEYLINE wrapper that fixed the day read. The ice theme is removed entirely —
beard fangs become braided tips with iron rings, the shield loses its frost
crystals for a plain wooden round shield, horn tips go bone/metal, and every
material is recoloured to a warm rusty-red raider.

North star (shared with store_skins): "a skin lives or dies at 40px in motion."
The rusty-auburn body is the loud read of the tier; the dark-iron helm carries
the top, the deep-red painted shield owns the back, and the near-black beard
anchors the lower silhouette. Every object is mass + one bright accent so the
stack survives the downscale.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly, _compose
from game.parrot import _add_outline
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette


# ── BLOODAXE palette (warm rust/red raider) ──────────────────────────────────
RUST_BODY  = (154, 51, 34)          # #9A3322 rusty auburn-red plumage
RUST_DARK  = (94, 28, 18)           # #5E1C12 deep plumage shadow / line work
RUST_CHEST = (182, 84, 58)          # #B6543A lit chest
RUST_BELLY = (122, 40, 24)          # #7A2818 belly

IRON       = (90, 94, 104)          # #5A5E68 dark-iron helm
IRON_DARK  = (52, 56, 63)           # #34383F iron shadow / boss / rim
IRON_HI    = (166, 174, 184)        # #A6AEB8 iron highlight / beard-rings
RING_IRON  = (176, 182, 192)        # #B0B6C0 bright iron beard-rings

FUR        = (74, 53, 38)           # #4A3526 dark-brown fur mantle
FUR_HI     = (122, 90, 64)          # #7A5A40 fur highlight, nudged ~10% so the
                                    # ruff keeps one readable tuft-line above the
                                    # near-black beard on a dark night sky

BEARD      = (36, 26, 20)           # #241A14 near-black braided beard
BEARD_HI   = (62, 44, 32)           # #3E2C20 braid highlight

SHIELD_RED = (110, 20, 16)          # #6E1410 deep-red field, dropped a full
                                    # value step below the body red so the disc
                                    # reads as the DARKEST of the three reds at
                                    # 40px (body mid > shield dark > iron pip).
                                    # Darkened, never brightened — brightening
                                    # would pull the disc toward fry-mode orange.
BRASS      = (199, 154, 58)         # #C79A3A brass studs
BONE       = (214, 198, 168)        # warm bone horn tip

# The shipped near-black 1px outline reads thin against the warm rust mass on a
# bright day sky; a slightly-warmer near-black keyline (#1A1410) wrapped around
# the WHOLE composited silhouette holds the value separation on day — same
# mechanism the frost wrapper used, just recoloured to this palette.
KEYLINE = (26, 20, 16, 235)         # #1A1410 near-black outer keyline


# Full rusty-red re-plumage of the macaw. Every slot is shifted to warm auburn;
# the deepest RUST_DARK owns the line work so the body still holds a crisp edge,
# and the chest/belly carry the lit warmth. Lenses are dropped so the helm brow
# + beard own the face (matching the winning structure).
P_BLOOD = _pal(
    tail=[(118, 38, 26), (138, 46, 30), (158, 58, 40), (180, 80, 56)],
    tail_line=RUST_DARK,
    body_shadow=(112, 34, 22),      # deepened so back / belly edge separates
                                    # from a bright day sky
    body_main=RUST_BODY,
    body_chest=RUST_CHEST,
    body_belly=RUST_BELLY,
    sheen=(255, 220, 200, 90),
    wing_main=(140, 46, 30),
    wing_dark=(86, 26, 16),
    wing_tip=(196, 100, 72),            # warm lit leading tips
    wing_secondary=None,
    wing_highlight=(214, 130, 100),     # warm rim on the wing edge
    head_shadow=(112, 34, 22),
    head_main=RUST_BODY,
    head_cheek=RUST_CHEST,
    head_crown=(168, 64, 44),
    lens_frame=(120, 40, 26),
    lens_body=(40, 22, 16),
    lens_tint=None,
    lens_glint=None,
    beak_main=(196, 150, 96),           # warm horn beak
    beak_dark=(120, 84, 44),
    beak_gloss=(228, 200, 150),
    foot=(120, 78, 44),
)


def _blood_base(angle_deg):
    # Rusty-red bird, no aviators — the helm brow + beard own the face.
    return _build_parrot_with_palette(angle_deg, P_BLOOD, draw_lenses=False)


# ── costume paint ────────────────────────────────────────────────────────────

def _paint(surf, wing_angle_deg):
    cy = CROWN_Y

    # ── ROUND WOODEN SHIELD on the BACK (drawn first, behind the body) ───────
    # Deep-red painted plank field + iron boss + iron rim + brass studs. No
    # frost crystals — a plain raider's round shield reading at 40px by its
    # red disc, dark rim and bright boss.
    sx, sy, sr = HX - 26, HY + 11, 13
    # A solid 2-3px IRON_DARK rim base, then the red field inset by 2px, so a
    # proud dark ring (not a 1px line) frames the disc and survives the
    # downscale — the dark frame is what keeps the shield from melting into the
    # rust body at 40px.
    pygame.draw.circle(surf, IRON_DARK, (sx, sy), sr + 2)      # proud iron rim
    pygame.draw.circle(surf, SHIELD_RED, (sx, sy), sr - 2)     # red painted field
    # Plank seams across the painted face.
    for dx in (-6, 0, 6):
        pygame.draw.line(surf, RUST_DARK, (sx + dx, sy - sr + 4),
                         (sx + dx, sy + sr - 4), 1)
    # A SINGLE brass stud at the top of the boss — at 40px the four-stud ring
    # blurred into an orange fringe that read as a halo, so the metal accent is
    # carried by the boss plus this one deliberate dot.
    pygame.draw.circle(surf, BRASS, (sx, sy - sr + 2), 2)
    pygame.draw.circle(surf, (240, 210, 130), (sx, sy - sr + 2), 1)
    # Bright iron boss, bumped ~1px so the pip is the brightest read of the disc
    # — keep the hard white glint.
    pygame.draw.circle(surf, IRON_DARK, (sx, sy), 6)
    pygame.draw.circle(surf, IRON_HI, (sx, sy), 5)
    pygame.draw.circle(surf, IRON_DARK, (sx, sy), 5, 1)
    pygame.draw.circle(surf, (255, 255, 255), (sx - 1, sy - 1), 1)

    # ── DARK-BROWN FUR MANTLE ringing the neck ───────────────────────────────
    # A scalloped brown fur ruff on the shoulders so the warm body has a fur
    # collar bridging head to chest.
    ruff_y = HY + 9
    for i in range(-3, 4):
        fx = HX - 1 + i * 5
        r = 5 if i % 2 == 0 else 4
        pygame.draw.circle(surf, BEARD, (fx, ruff_y + 1), r)
        pygame.draw.circle(surf, FUR, (fx, ruff_y), r - 1)
    # Fur tops sit at FUR_HI (not the brightest point) so the HELM owns the top:
    # hierarchy is helm dome > shield boss > fur. Three highlight tufts, not
    # five, so the band doesn't crowd the eye on bright frames.
    for i in range(-1, 2):
        pygame.draw.circle(surf, FUR_HI, (HX - 1 + i * 5, ruff_y - 1), 1)

    # ── NEAR-BLACK BRAIDED BEARD with IRON BEARD-RINGS ───────────────────────
    # Dark braids hanging under the beak, tipped with iron rings + plain braid
    # ends instead of icicles. The two heavy braids break the lower outline —
    # plain raider beard geometry.
    pygame.draw.ellipse(surf, BEARD, (HX - 3, HY + 6, 17, 12))
    pygame.draw.ellipse(surf, BEARD_HI, (HX - 2, HY + 5, 15, 10))
    for bx in (HX + 1, HX + 7):
        pygame.draw.line(surf, BEARD, (bx, HY + 9), (bx, HY + 18), 3)
        pygame.draw.line(surf, BEARD_HI, (bx - 1, HY + 9), (bx - 1, HY + 16), 1)
        # Iron beard-ring clamped near the braid end, then a tapered braid tip.
        pygame.draw.rect(surf, RING_IRON, (bx - 2, HY + 16, 5, 2))
        pygame.draw.rect(surf, IRON_DARK, (bx - 2, HY + 16, 5, 2), 1)
        pygame.draw.line(surf, BEARD, (bx, HY + 18), (bx, HY + 21), 2)
        pygame.draw.circle(surf, RING_IRON, (bx, HY + 16), 1)

    # ── BEARDED AXE in the wing/hand ─────────────────────────────────────────
    # Dark-iron head with a warm steel highlight, hafted low so the blade breaks
    # the lower-front silhouette. Drawn before the helm so the helm reads on top
    # of the head.
    hxr, hyr = HX + 16, HY + 20          # haft top near the wing
    htx, hty = HX + 11, HY + 32          # haft bottom
    pygame.draw.line(surf, RUST_DARK, (hxr, hyr), (htx, hty), 4)   # wood haft
    pygame.draw.line(surf, (150, 96, 56), (hxr, hyr), (htx, hty), 2)
    # Bearded axe head — a swept crescent off the haft top.
    head = [(hxr - 1, hyr - 4), (hxr + 9, hyr - 6), (hxr + 11, hyr + 4),
            (hxr + 6, hyr + 9), (hxr + 1, hyr + 6)]
    _poly(surf, IRON_DARK, head)
    _poly(surf, IRON, [(hxr, hyr - 3), (hxr + 8, hyr - 4), (hxr + 9, hyr + 3),
                       (hxr + 2, hyr + 4)])
    # Bright steel edge on the cutting curve.
    pygame.draw.line(surf, IRON_HI, (hxr + 8, hyr - 4), (hxr + 10, hyr + 3), 2)
    pygame.draw.line(surf, (255, 255, 255), (hxr + 9, hyr - 2), (hxr + 10, hyr + 1), 1)

    # ── IRON HORNED SPANGENHELM ──────────────────────────────────────────────
    # Two horns sweeping up & outward with plain bone/metal tips, a domed iron
    # cap and a nasal guard. The bright dome carries the top read while the
    # horns break the crown outline.
    for sgn, hx0 in ((-1, HX - 9), (1, HX + 9)):
        tipx = hx0 + sgn * 6
        mid = (hx0 + sgn * 5, cy - 6)
        # Horn FILL is the dark BEARD tone so each horn reads as a solid mass
        # against sky; only the leading edge carries a bone sliver.
        _poly(surf, BEARD,
              [(hx0 - 4, cy + 2), (hx0 + 4, cy + 2), mid,
               (tipx + sgn * 2, cy - 16)])
        _poly(surf, FUR_HI,
              [(hx0 + sgn * 3, cy + 1), (hx0 + sgn * 4, cy + 1),
               (mid[0] + sgn, mid[1] + 1), (tipx + sgn * 2, cy - 15)])
        # Plain bone/metal horn tip — kept bright as a top focal point.
        pygame.draw.circle(surf, (170, 152, 120), (tipx + sgn, cy - 15), 3)
        pygame.draw.circle(surf, BONE, (tipx + sgn, cy - 15), 2)
        pygame.draw.circle(surf, (244, 234, 210), (tipx + sgn - 1, cy - 16), 1)

    # Iron spangenhelm dome — FILL at IRON_DARK so the helm is the biggest dark
    # mass on the crown; IRON is demoted to a highlight band riding the top.
    pygame.draw.ellipse(surf, IRON_DARK, (HX - 12, cy - 6, 25, 18))
    pygame.draw.ellipse(surf, IRON, (HX - 11, cy - 6, 23, 8))
    # Spangen ridge + a pale iron highlight band.
    pygame.draw.line(surf, IRON_DARK, (HX, cy - 6), (HX, cy + 4), 2)
    pygame.draw.ellipse(surf, IRON_HI, (HX - 6, cy - 5, 9, 4))
    # Riveted brow band the horns root into.
    pygame.draw.line(surf, IRON_DARK, (HX - 11, cy + 5), (HX + 12, cy + 4), 4)
    pygame.draw.line(surf, IRON_HI, (HX - 11, cy + 4), (HX + 12, cy + 3), 1)
    for rx in (HX - 8, HX - 1, HX + 6):
        pygame.draw.circle(surf, IRON_HI, (rx, cy + 5), 1)
    # Nasal guard.
    pygame.draw.rect(surf, IRON_DARK, (HX + 1, cy + 4, 3, 11))
    pygame.draw.rect(surf, IRON, (HX + 1, cy + 4, 2, 10))

    # ── FUR BOOT CUFFS on the feet (base feet sit at y~65-69 in composite) ───
    for fx, fy in ((27, 65), (35, 65)):
        pygame.draw.circle(surf, BEARD, (fx, fy + 1), 3)
        pygame.draw.circle(surf, FUR_HI, (fx, fy), 2)


def _blood_skin(paint_fn, base_fn):
    """Like store_skins._make_skin, but wraps the composited silhouette in the
    near-black KEYLINE instead of the shipped 1px outline — the same wrapper
    mechanism design_4 used for its day-read fix, recoloured to this palette's
    near-black. Scratch-only; production _make_skin is untouched."""
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


build = _blood_skin(_paint, base_fn=_blood_base)
