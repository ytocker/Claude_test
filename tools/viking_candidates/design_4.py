"""FROSTREAVER — Ice-Raider of the North (viking-redesign candidate, design_4).

Scratch exploration ONLY — never registered in store_skins.BUILDERS; the live
skin_viking is untouched. This concept recolours the WHOLE macaw to pale
frost-blue through the 24-slot palette (same mechanism as the shipped ninja's
P_NINJA / disco), then layers a cold raider kit over it: a frost-rimed horned
helm, an icicle-tipped braided beard, a snowy wolf-fur ruff, a round ice-wood
shield with frost crystals on the back, and a frost-bladed bearded axe.

North star (shared with store_skins): "a skin lives or dies at 40px in motion."
The cold body recolour is the loudest read of the standard tier — a literal
frost-raider — and the jagged ice edges (icicle beard, frost-spiked shield rim)
break the lower silhouette so no warm raider can be mistaken for it. Every
object is mass + one bright frost accent so the stack survives the downscale.
"""
import math
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly, _compose
from game.parrot import _add_outline
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette


# ── frost palette (brief spec) ───────────────────────────────────────────────
FROST_BODY = (191, 224, 242)        # #BFE0F2 frost-pale plumage
COLD_WOOD  = (127, 168, 201)        # #7FA8C9 cold helm / shield wood
COLD_SHADE = (62, 91, 114)          # #3E5B72 cold shadow / beard
ICE_WHITE  = (242, 250, 255)        # #F2FAFF icicles / frost glint / fur
ICE_HI     = (199, 233, 255)        # #C7E9FF pale ice highlight

# The frost mass is so pale it dissolves into a bright day sky; the shipped
# near-black 1px outline reads warm and thin against cold blue. A cold mid-dark
# keyline (#2E4658) wrapped around the WHOLE composited silhouette is what holds
# the value separation on day — it is the single biggest day-read fix here.
KEYLINE = (46, 70, 88, 235)         # #2E4658 cold outer keyline


# Full pale-frost re-plumage of the macaw. Every slot is shifted to cold blue;
# the wing TIP / highlight slots carry the white frost-dusting on the feather
# edge, and the deepest cold-shade owns the line work so the pale mass still
# holds a crisp edge on a bright day sky. Lenses are dropped so the frost helm
# + brow own the face (the icicle beard reads better without warm aviators).
P_FROST = _pal(
    tail=[(150, 192, 218), (164, 204, 228), (180, 216, 238), (205, 234, 248)],
    tail_line=COLD_SHADE,
    body_shadow=(78, 116, 146),     # deepened toward COLD_SHADE so the back /
                                    # belly edge separates from a blue day sky
    body_main=FROST_BODY,
    body_chest=(214, 238, 250),
    body_belly=(228, 246, 253),
    sheen=(255, 255, 255, 120),
    wing_main=(160, 200, 226),
    wing_dark=(96, 134, 166),
    wing_tip=ICE_WHITE,                 # white frost-dusting on the leading tips
    wing_secondary=None,
    wing_highlight=ICE_WHITE,           # crisp rimed edge on the wing
    head_shadow=(78, 116, 146),
    head_main=FROST_BODY,
    head_cheek=(216, 240, 251),
    head_crown=(228, 246, 253),
    lens_frame=(150, 188, 214),
    lens_body=(40, 60, 80),
    lens_tint=None,
    lens_glint=None,
    beak_main=(150, 178, 200),          # cold horn so nothing warm survives
    beak_dark=COLD_SHADE,
    beak_gloss=ICE_HI,
    foot=(110, 140, 164),
)


def _frost_base(angle_deg):
    # Pale frost bird, no aviators — the helm brow + icicle beard own the face.
    return _build_parrot_with_palette(angle_deg, P_FROST, draw_lenses=False)


# ── small ice helpers ────────────────────────────────────────────────────────

def _icicle(surf, x, y, length, w=3):
    """A downward ice spike: pale-blue body + a bright white inner glint, with a
    COLD_SHADE edge down ONE side. The single dark edge is what makes the spike
    read as a deliberate triangle (not noise) once it shrinks to 40px — without
    it the pale icicle vanishes into the pale beard."""
    _poly(surf, COLD_SHADE, [(x - w, y), (x + w, y), (x, y + length)])
    _poly(surf, ICE_HI, [(x - w + 1, y), (x + w, y), (x, y + length - 1)])
    _poly(surf, ICE_WHITE, [(x - w + 1, y), (x + max(1, w - 2), y),
                            (x, y + length - 2)])
    pygame.draw.line(surf, ICE_WHITE, (x, y + 1), (x, y + length - 2), 1)


def _frost_crystal(surf, x, y, r):
    """A jagged outward ice shard growing off a rim (silhouette-breaker)."""
    pts = [(x, y - r), (x + r // 2, y - r // 3), (x + r, y),
           (x + r // 3, y + r // 3), (x, y + r), (x - r // 3, y + r // 3),
           (x - r, y), (x - r // 2, y - r // 3)]
    _poly(surf, ICE_HI, pts)
    pygame.draw.circle(surf, ICE_WHITE, (x, y), max(1, r // 3))


# ── costume paint ────────────────────────────────────────────────────────────

def _paint(surf, wing_angle_deg):
    cy = CROWN_Y

    # ── ROUND ICE-SHIELD on the BACK (drawn first, behind the body) ──────────
    # Pale ice-wood planks + iron boss, with jagged frost crystals growing off
    # the rim so the back outline reads as a frozen raider's shield at 40px.
    sx, sy, sr = HX - 26, HY + 11, 13
    # Frost crystals on the rim BEHIND the disc so they poke past the edge.
    # Only four, on clean diagonals — each then survives the downscale as a
    # deliberate spike instead of an even fringe that blurs into a fat halo.
    for ang in (45, 135, 225, 315):
        rad = math.radians(ang)
        cxp = int(sx + (sr + 2) * math.cos(rad))
        cyp = int(sy + (sr + 2) * math.sin(rad))
        _frost_crystal(surf, cxp, cyp, 5)
    pygame.draw.circle(surf, COLD_SHADE, (sx, sy), sr + 1)
    pygame.draw.circle(surf, COLD_WOOD, (sx, sy), sr)
    # Plank seams across the ice-wood face.
    for dx in (-7, 0, 7):
        pygame.draw.line(surf, COLD_SHADE, (sx + dx, sy - sr + 2),
                         (sx + dx, sy + sr - 2), 1)
    # Rime ring + bright iron boss with a hard glint.
    pygame.draw.circle(surf, ICE_HI, (sx, sy), sr, 2)
    pygame.draw.circle(surf, COLD_SHADE, (sx, sy), 5)
    pygame.draw.circle(surf, ICE_WHITE, (sx, sy), 4)
    pygame.draw.circle(surf, COLD_SHADE, (sx, sy), 4, 1)
    pygame.draw.circle(surf, (255, 255, 255), (sx - 1, sy - 1), 1)

    # ── WINTER-WOLF FUR MANTLE ringing the neck (snowy ruff) ─────────────────
    # A scalloped white ruff sitting on the shoulders so the cold body has a
    # bright fur collar bridging head to chest.
    ruff_y = HY + 9
    for i in range(-3, 4):
        fx = HX - 1 + i * 5
        r = 5 if i % 2 == 0 else 4
        pygame.draw.circle(surf, COLD_SHADE, (fx, ruff_y + 1), r)
        pygame.draw.circle(surf, ICE_WHITE, (fx, ruff_y), r - 1)
    # Ruff tops sit at ICE_WHITE, not pure white, so the HELM TIPS stay the
    # single brightest point — hierarchy is helm tips > shield boss > ruff.
    for i in range(-2, 3):
        pygame.draw.circle(surf, ICE_WHITE, (HX - 1 + i * 5, ruff_y - 1), 1)

    # ── FROSTED BRAIDED BEARD with ICICLE ends ───────────────────────────────
    # Pale grey-blue braids hanging under the beak, tipped with icicles instead
    # of beard-rings; ice flecks glitter along it. The icicles break the lower
    # outline — unique geometry no warm raider has.
    pygame.draw.ellipse(surf, COLD_SHADE, (HX - 3, HY + 6, 17, 12))
    pygame.draw.ellipse(surf, (168, 196, 216), (HX - 2, HY + 5, 15, 10))
    for bx in (HX + 1, HX + 7):
        pygame.draw.line(surf, COLD_SHADE, (bx, HY + 9), (bx, HY + 16), 3)
        pygame.draw.line(surf, ICE_HI, (bx - 1, HY + 9), (bx - 1, HY + 15), 1)
    # Two long, fat icicles instead of three short ones — fewer + longer reads
    # as deliberate ice fangs, not a noisy fringe, after the 40px shrink.
    _icicle(surf, HX + 1, HY + 16, 9, w=3)
    _icicle(surf, HX + 7, HY + 16, 8, w=3)
    for fx, fy in ((HX, HY + 9), (HX + 5, HY + 11), (HX + 9, HY + 8)):
        pygame.draw.circle(surf, (255, 255, 255), (fx, fy), 1)

    # ── FROST-BLADED BEARDED AXE in the wing/hand ────────────────────────────
    # Pale steel head with a faint cold-blue rim-glint, hafted low so the blade
    # breaks the lower-front silhouette. Drawn before the helm so the helm reads
    # on top of the head.
    hxr, hyr = HX + 14, HY + 18          # haft top near the wing
    htx, hty = HX + 9, HY + 30           # haft bottom
    pygame.draw.line(surf, COLD_SHADE, (hxr, hyr), (htx, hty), 4)
    pygame.draw.line(surf, (150, 178, 200), (hxr, hyr), (htx, hty), 2)
    # Bearded axe head — a swept crescent off the haft top.
    head = [(hxr - 1, hyr - 4), (hxr + 9, hyr - 6), (hxr + 11, hyr + 4),
            (hxr + 6, hyr + 9), (hxr + 1, hyr + 6)]
    _poly(surf, COLD_SHADE, head)
    _poly(surf, ICE_HI, [(hxr, hyr - 3), (hxr + 8, hyr - 4), (hxr + 9, hyr + 3),
                         (hxr + 2, hyr + 4)])
    # Bright cold-blue edge rim-glint on the cutting curve.
    pygame.draw.line(surf, ICE_WHITE, (hxr + 8, hyr - 4), (hxr + 10, hyr + 3), 2)
    pygame.draw.line(surf, (255, 255, 255), (hxr + 9, hyr - 2), (hxr + 10, hyr + 1), 1)
    _icicle(surf, hxr + 9, hyr + 5, 4, w=2)   # icicle hanging off the blade

    # ── STEEL-BLUE HORNED SPANGENHELM ────────────────────────────────────────
    # Two rimed horns sweeping up & outward, frost-white tips with a few icicle
    # drips off the brim, a domed cap and a nasal guard. The bright helm carries
    # the top read while the frost tips break the crown outline.
    for sgn, hx0 in ((-1, HX - 9), (1, HX + 9)):
        tipx = hx0 + sgn * 6
        mid = (hx0 + sgn * 5, cy - 6)
        # Horn FILL is the dark COLD_SHADE so each horn reads as a solid mass
        # against blue sky; only the leading edge carries an ICE_HI sliver.
        _poly(surf, COLD_SHADE,
              [(hx0 - 4, cy + 2), (hx0 + 4, cy + 2), mid,
               (tipx + sgn * 2, cy - 16)])
        _poly(surf, ICE_HI,
              [(hx0 + sgn * 3, cy + 1), (hx0 + sgn * 4, cy + 1),
               (mid[0] + sgn, mid[1] + 1), (tipx + sgn * 2, cy - 15)])
        # White frost tip — kept bright; this is the top focal point.
        pygame.draw.circle(surf, ICE_HI, (tipx + sgn, cy - 15), 3)
        pygame.draw.circle(surf, ICE_WHITE, (tipx + sgn, cy - 15), 2)
        pygame.draw.circle(surf, (255, 255, 255), (tipx + sgn - 1, cy - 16), 1)

    # Steel-blue spangenhelm dome — FILL darkened to COLD_SHADE so the helm is
    # the biggest dark mass on the crown; COLD_WOOD is demoted to a highlight
    # band riding the top of the dome only.
    pygame.draw.ellipse(surf, COLD_SHADE, (HX - 12, cy - 6, 25, 18))
    pygame.draw.ellipse(surf, COLD_WOOD, (HX - 11, cy - 6, 23, 8))
    # Spangen ridge + a pale ice highlight band.
    pygame.draw.line(surf, COLD_SHADE, (HX, cy - 6), (HX, cy + 4), 2)
    pygame.draw.ellipse(surf, ICE_HI, (HX - 6, cy - 5, 9, 4))
    # Riveted brow band the horns root into.
    pygame.draw.line(surf, COLD_SHADE, (HX - 11, cy + 5), (HX + 12, cy + 4), 4)
    pygame.draw.line(surf, ICE_HI, (HX - 11, cy + 4), (HX + 12, cy + 3), 1)
    for rx in (HX - 8, HX - 1, HX + 6):
        pygame.draw.circle(surf, ICE_WHITE, (rx, cy + 5), 1)
    # Nasal guard.
    pygame.draw.rect(surf, COLD_SHADE, (HX + 1, cy + 4, 3, 11))
    pygame.draw.rect(surf, (150, 178, 200), (HX + 1, cy + 4, 2, 10))
    # One icicle drip off the brim — a single deliberate spike, not a fringe
    # competing with the beard fangs and shield crystals for the eye.
    _icicle(surf, HX + 9, cy + 6, 6, w=2)

    # ── FUR BOOT CUFFS on the feet (base feet sit at y~65-69 in composite) ───
    for fx, fy in ((27, 65), (35, 65)):
        pygame.draw.circle(surf, COLD_SHADE, (fx, fy + 1), 3)
        pygame.draw.circle(surf, ICE_WHITE, (fx, fy), 2)


def _frost_skin(paint_fn, base_fn):
    """Like store_skins._make_skin, but wraps the composited silhouette in the
    cold KEYLINE instead of the shipped near-black 1px outline. The wrap is the
    day-read fix: COLD_SHADE only ever touched interior line work, so the pale
    outer mass never had a dark edge against a bright sky — this gives it one.
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


build = _frost_skin(_paint, base_fn=_frost_base)
