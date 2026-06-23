"""DESIGN 6 — ARTEMIS: the real next-gen NASA AxEMU (Axiom/Prada) moon suit.

The friendly clear-visor sibling of MOONWALKER. Where MOONWALKER drops the
postcard gold visor, ARTEMIS keeps the helmet a CLEAR bubble dome so Pip's
macaw face beams straight through the glass — the suit is the costume, the
bird is still in there. The instant tell is the official Artemis identity:
a puffy hard-upper-torso white shell + a bubble dome with a real face inside
+ the blue-over-red candy-stripes wrapping the arm and the leg/boot.

Hero silhouette: the BULKIEST of the astronaut siblings — broad rounded
shoulders and a fat bubble helmet, boxier squared-off PLSS past the crown.

Scratch exploration only — wrapped by ``store_skins._make_skin`` and rendered
via ``tools/ninja_render.py``; NOT registered in ``store_skins.BUILDERS`` so
the live ``skin_astronaut`` is untouched.

Lessons baked in from the shipped MOONWALKER / STARLINER siblings (so they
don't get re-flagged):
  (a) the WHOLE white silhouette is wrapped in a continuous #2A2D34 keyline,
      derived as a dilated dark mask under the art, or the puffy white washes
      into the bright day sky at 40px;
  (b) chest detail is held to ONE readable beat — a single control panel with
      a short status pip row — no sub-pixel confetti;
  (c) the bubble helmet is the clean dominant head shape;
  (d) the back PLSS reads as an attached SUBORDINATE block (squared, low-
      contrast, overlapped by the head/body), not a second head;
  (e) the 40px NEAREST read was tuned FIRST on day AND night.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y
from game.parrot import _aaellipse
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette


# ── ARTEMIS palette ──────────────────────────────────────────────────────────
_SUIT      = (243, 245, 250)       # #F3F5FA suit white
_SUIT_SH   = (206, 211, 222)       # cool suit shadow / seam
_SUIT_SH_D = (176, 183, 198)       # deeper crease so the white holds shape
_BLUE      = (28, 63, 168)         # #1C3FA8 Artemis blue
_BLUE_H    = (96, 132, 224)
_RED       = (211, 32, 48)         # #D32030 Artemis red
_RED_H     = (244, 120, 130)
_KEY       = (42, 45, 52)          # #2A2D34 keyline / visor-ring shadow
_PIP       = (39, 208, 176)        # #27D0B0 chest status pip
_CHROME    = (224, 230, 240)       # helmet ring chrome
_WHITE     = (255, 255, 255)

# Warm macaw face tones kept ALIVE inside the suit recolour: the head cheek +
# beak stay scarlet/horn so Pip's face is the highest-contrast read inside the
# clear glass. Everything below the neck is suit-white so the body reads as the
# pressurised shell. Lenses are dropped — the bubble dome owns the head, and the
# eye is painted by hand inside the glass.
_FACE_SCARLET = (214, 54, 44)
_FACE_CHEEK_H = (244, 132, 110)

_AST_PAL = _pal(
    tail=[(206, 211, 222), (218, 222, 230), (230, 233, 240), (242, 244, 248)],
    tail_line=_SUIT_SH_D,
    body_shadow=(196, 202, 214),
    body_main=_SUIT,
    body_chest=(253, 254, 255),
    body_belly=(232, 236, 243),
    sheen=(255, 255, 255, 110),
    wing_main=(228, 232, 240),
    wing_dark=_SUIT_SH,
    wing_tip=(249, 250, 253),
    wing_secondary=None,
    wing_highlight=_WHITE,
    head_shadow=(150, 40, 32),         # warm — the face beams through the glass
    head_main=_FACE_SCARLET,
    head_cheek=_FACE_CHEEK_H,
    head_crown=(196, 50, 42),
    lens_frame=(206, 211, 222),
    lens_body=(150, 40, 32),
    lens_tint=None,
    lens_glint=None,
    beak_main=(232, 198, 96),          # warm horn beak stays visible in the dome
    beak_dark=(150, 96, 30),
    beak_gloss=(252, 232, 150),
    foot=(200, 206, 216),
)


def _white_base(angle_deg):
    # White-suited body + warm macaw face, no aviators — the clear bubble dome
    # owns the head and Pip's face shows through it.
    return _build_parrot_with_palette(angle_deg, _AST_PAL, draw_lenses=False)


def _candy_stripes(surf, x, y, w, *, horiz=True, t=3):
    """The signature Artemis tell: a BLUE band above a RED band. Drawn fat (t px
    each) so both survive 40px. Used on the chest, the upper arm, and the leg."""
    if horiz:
        pygame.draw.rect(surf, _BLUE, (x, y, w, t))
        pygame.draw.rect(surf, _RED, (x, y + t, w, t))
        pygame.draw.line(surf, _BLUE_H, (x, y), (x + w - 1, y), 1)
        pygame.draw.line(surf, _RED_H, (x, y + t), (x + w - 1, y + t), 1)
    else:
        pygame.draw.rect(surf, _BLUE, (x, y, t, w))
        pygame.draw.rect(surf, _RED, (x + t, y, t, w))


def _plss(surf):
    # Squared-off hard WHITE PLSS brick past the crown and out past the back —
    # boxier/cleaner than MOONWALKER's. Drawn FIRST so the head/body overlap its
    # front edge → it reads as worn ON the back, a subordinate block, never a
    # second head. Low internal contrast (suit-shadow only) keeps it quiet next
    # to the bright dome.
    bx, by, bw, bh = HX - 34, CROWN_Y - 7, 23, 46
    pygame.draw.rect(surf, _KEY, (bx - 2, by - 2, bw + 4, bh + 4), border_radius=3)
    pygame.draw.rect(surf, _SUIT_SH, (bx, by, bw, bh), border_radius=2)
    pygame.draw.rect(surf, _SUIT, (bx + 2, by + 2, bw - 4, bh - 4), border_radius=2)
    # Top vent slot — the one hard detail that says "life-support brick".
    pygame.draw.rect(surf, _KEY, (bx + 3, by + 4, bw - 6, 4), border_radius=1)
    pygame.draw.line(surf, _SUIT_SH_D, (bx + bw // 2, by + 11),
                     (bx + bw // 2, by + bh - 4), 2)   # split seam


def _suit_keyline(surf):
    """ONE continuous #2A2D34 keyline around the whole painted bird.

    The puffy white silhouette dissolves into the pale day sky at 40px without
    it; a 1-2px-dilated dark mask of everything drawn so far is stamped BEHIND
    the art so the entire shell carries the same contour weight the helmet ring
    and PLSS already have. (The engine's own 1px near-black outline is too thin
    to hold the white at thumbnail size.)"""
    mask = pygame.mask.from_surface(surf, threshold=12)
    line = mask.to_surface(setcolor=_KEY, unsetcolor=(0, 0, 0, 0))
    key = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1),
                   (-1, -1), (1, -1), (-1, 1), (1, 1),
                   (-2, 0), (2, 0), (0, 2)):
        key.blit(line, (dx, dy))
    key.blit(surf, (0, 0))
    surf.blit(key, (0, 0))


def _paint(surf, wing_angle_deg):
    # ── BACK: squared PLSS brick, drawn first so the body sits in front ───────
    _plss(surf)

    # ── BODY: hard-upper-torso shell — a slightly inflated rounded white mass
    #    over the chest so the silhouette reads PUFFY. One control panel + a
    #    short status-pip row is the single chest beat (no confetti). ──────────
    tcx, tcy = 34, 50
    _aaellipse(surf, _SUIT_SH, (tcx, tcy + 1), 17, 12)      # shell shadow
    _aaellipse(surf, _SUIT, (tcx - 1, tcy), 16, 11)         # inflated shell
    _aaellipse(surf, _WHITE, (tcx - 5, tcy - 5), 7, 3)      # top sheen
    # Rectangular chest control panel — the one readable chest beat.
    px, py = tcx + 1, tcy - 1
    pygame.draw.rect(surf, _KEY, (px - 8, py - 4, 16, 10), border_radius=2)
    pygame.draw.rect(surf, (58, 62, 72), (px - 7, py - 3, 14, 8), border_radius=2)
    # 3 status pips: two cyan/green, one white — the lone glow on the suit.
    pygame.draw.circle(surf, _PIP, (px - 4, py + 1), 2)
    pygame.draw.circle(surf, _PIP, (px + 1, py + 1), 2)
    pygame.draw.circle(surf, _WHITE, (px + 6, py + 1), 1)
    # Fat chest candy-stripe band across the lower shell — the central,
    # always-visible Artemis tell that carries the colour read at 40px.
    _candy_stripes(surf, tcx - 13, tcy + 6, 25, horiz=True, t=3)

    # ── Round mission patch on the near shoulder — a small blue disc with a
    #    white star, the official Artemis crew-patch nod. ──────────────────────
    sx, sy = tcx + 13, tcy - 7
    pygame.draw.circle(surf, _SUIT_SH_D, (sx, sy), 5)
    pygame.draw.circle(surf, _BLUE, (sx, sy), 4)
    store_skins._star5(surf, sx, sy, 3, _WHITE)
    pygame.draw.arc(surf, _RED, (sx - 4, sy - 4, 8, 8), 3.4, 6.0, 1)

    # ── LIMBS: candy-striped leg + white boot with a blue sole line, drawn in
    #    FRONT of the shell so the leg stripe sits clear below the torso ───────
    bx, by, bw, bh = 23, 62, 20, 9
    pygame.draw.rect(surf, _SUIT_SH, (bx, by, bw, bh), border_radius=3)
    pygame.draw.rect(surf, _SUIT, (bx + 1, by, bw - 2, bh - 3), border_radius=3)
    pygame.draw.rect(surf, _BLUE, (bx, by + bh - 3, bw, 3), border_radius=1)  # sole
    pygame.draw.line(surf, _SUIT_SH_D, (bx + bw // 2, by + 1),
                     (bx + bw // 2, by + bh - 3), 2)   # split the two boots
    # Leg candy-stripe wrapping the shin right above the boot.
    _candy_stripes(surf, bx + 1, by - 7, bw - 2, horiz=True, t=3)

    # ── ARM candy-stripe + white glove on the near wing ───────────────────────
    _candy_stripes(surf, 44, 44, 9, horiz=False, t=3)      # upper-arm bands
    pygame.draw.circle(surf, _SUIT_SH, (52, 44), 5)        # glove
    pygame.draw.circle(surf, _SUIT, (52, 43), 4)
    pygame.draw.circle(surf, _SUIT_SH_D, (47, 45), 1)      # cuff seam

    # ── HEAD: fat CLEAR bubble dome — the bulkiest, dominant head shape. Pip's
    #    warm macaw face (already painted by the warm-head palette) beams
    #    through; a thin chrome ring frames the glass and a soft top highlight
    #    sells the dome. The eye is painted INSIDE so the face is the highest-
    #    contrast read within the glass. ──────────────────────────────────────
    cx, cyh = HX + 1, HY - 1
    r = 16
    # EVA neck-rim collar tying dome to the suit shell.
    pygame.draw.ellipse(surf, _KEY, (cx - 13, cyh + 9, 28, 11))
    pygame.draw.ellipse(surf, _SUIT, (cx - 12, cyh + 9, 26, 8))

    # Chrome ring shadow, then a faint glass tint ABOVE the face so the bubble
    # reads as a transparent sphere without hiding the warm macaw underneath.
    pygame.draw.circle(surf, _KEY, (cx, cyh), r + 1)
    pygame.draw.circle(surf, _CHROME, (cx, cyh), r)
    pygame.draw.circle(surf, (220, 228, 240), (cx, cyh), r - 1)
    # Punch a clear window: redraw the warm face inside the glass so it shows
    # through (the dome circles above covered it). A cool wash overlays only the
    # upper third as the glass reflection — the face below stays full-contrast.
    _aaellipse(surf, (150, 40, 32), (cx - 1, cyh + 1), 13, 12)     # face shadow
    _aaellipse(surf, _FACE_SCARLET, (cx - 2, cyh), 12, 11)         # warm face
    _aaellipse(surf, _FACE_CHEEK_H, (cx - 5, cyh + 2), 4, 3)       # cheek
    # Big dark macaw eye — the single highest-contrast read inside the glass.
    pygame.draw.circle(surf, _WHITE, (cx + 3, cyh - 1), 5)
    pygame.draw.circle(surf, (20, 22, 28), (cx + 4, cyh - 1), 4)
    pygame.draw.circle(surf, (90, 140, 220), (cx + 5, cyh), 2)     # iris glint
    pygame.draw.circle(surf, _WHITE, (cx + 3, cyh - 3), 1)
    # Warm horn beak poking forward inside the lower glass.
    beak = [(cx + 8, cyh + 1), (cx + 14, cyh + 4), (cx + 11, cyh + 8),
            (cx + 6, cyh + 6)]
    pygame.draw.polygon(surf, (232, 198, 96), beak)
    pygame.draw.polygon(surf, (150, 96, 30), beak, 1)
    pygame.draw.line(surf, (252, 232, 150), (cx + 8, cyh + 2), (cx + 12, cyh + 4), 1)

    # Glass reflection: a cool translucent sweep on the upper-left of the dome
    # only, so the sphere reads transparent but the face stays the bright read.
    glass = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
    pygame.draw.circle(glass, (210, 226, 245, 95), (r, r), r - 1)
    cut = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
    pygame.draw.circle(cut, (255, 255, 255, 255), (r, r + 9), r - 1)
    glass.blit(cut, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
    surf.blit(glass, (cx - r, cyh - r))

    # Thin chrome helmet ring + a bright top specular hot-spot on the dome.
    pygame.draw.circle(surf, _CHROME, (cx, cyh), r, 2)
    pygame.draw.circle(surf, _KEY, (cx, cyh), r + 1, 1)
    pygame.draw.circle(surf, _WHITE, (cx - 7, cyh - 9), 3)
    pygame.draw.circle(surf, _WHITE, (cx - 5, cyh - 11), 1)
    # Tiny side comms nub on the helmet.
    pygame.draw.circle(surf, _SUIT_SH, (cx - r + 1, cyh + 2), 3)
    pygame.draw.circle(surf, _RED, (cx - r + 1, cyh + 2), 1)

    # ── final pass: ONE continuous dark keyline behind everything ─────────────
    _suit_keyline(surf)


build = store_skins._make_skin(_paint, base_fn=_white_base)
