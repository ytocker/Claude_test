"""Candidate PAPER-PLANE skin — concept NEWSPRINT / COMIC (round 1).

A secret premium NON-creature flyer: the player's flapping bird becomes a dart
folded from a sheet of NEWSPAPER / COMIC print. There are no wings — the 4 base
wing poses are reinterpreted as a gentle BANK/FLUTTER + nose-bob, exactly like
the production dollar-bill dart it would replace.

Contract (mirrors game/animal_paper_plane.py so the winner lifts straight back
into that standalone module):

  * `build_<name>(wing_angle_deg) -> pygame.Surface`  draws ONE flat frame on a
    64×84 SRCALPHA canvas, mass centred at the BODY anchor (32, 44).
  * NOSE POINTS RIGHT (forward) — the bird faces right, so the dart noses right.
  * a cached `(frame_idx, tilt_deg) -> Surface` getter from a local
    `_make_prebuilt_skin(build_fn)`.
  * `BUILDERS = {"skin_newsprint": get_newsprint, ...}` at the bottom.

North star: "a skin lives or dies at 40px in motion." Newsprint is a trap — a
faithful grey page turns to mush at 40px. So every take leans on the SAME
load-bearing structure as the production dart:

  * a HARD value FOLD: a bright upper facet meets a distinctly darker under-fold
    at a crisp central crease, so the triangular dart silhouette survives,
  * exactly ONE bold high-contrast TELL on the lit facet — a black headline bar,
    a fat halftone-colour panel, a bold word, etc. — over clean light paper, so
    the body never reads as flat grey,
  * column rules / halftone dots kept SUBTLE (hero-scale texture, near-invisible
    noise at 40px — that is intentional),
  * a baked 1px self-rim so the dart holds on day AND night skies with no host
    outline.
"""
import math
import pygame

from game.parrot import SPRITE_W, _WING_ANGLES, _add_outline


# ── canvas constants (match game/animal_paper_plane.py) ──────────────────────
COMPOSITE_W = SPRITE_W          # 64
COMPOSITE_H = 84
DY          = 12
BCX, BCY    = 32, 32 + DY       # body / mass centre → (32, 44)

# Roll is clamped so the bank-roll "flap" never flattens the dart to a sliver:
# at 3/4 view the under-fold collapses if the craft rolls too far edge-on.
_ROLL_MAX = 5.5


# ── shared factory (local copy of animal_paper_plane._make_prebuilt_skin) ────
def _make_prebuilt_skin(build_fn):
    """Cached `(frame_idx, tilt_deg) -> Surface` getter for a full-body
    build_fn(angle). Lazy 4-frame build + per-(frame, 3°) rotation cache,
    each frame outlined with the house silhouette outline."""
    state = {"frames": None, "rot": {}}

    def getter(frame_idx, tilt_deg):
        if state["frames"] is None:
            state["frames"] = [_add_outline(build_fn(a)) for a in _WING_ANGLES]
        frames = state["frames"]
        frame_idx %= len(frames)
        key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
        s = state["rot"].get(key)
        if s is None:
            s = pygame.transform.rotozoom(frames[frame_idx], key[1], 1.0)
            state["rot"][key] = s
        return s

    return getter


def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _flutter(angle_deg):
    """Map a base wing angle (_WING_ANGLES runs 50→-40) to a centred −1..+1
    'catching air' factor. Drives the gentle bank-roll + nose-bob; there are no
    wings, so the flap energy goes entirely into the craft swaying."""
    return ((angle_deg + 40) / 90.0 - 0.5) * 2.0


def _poly(surf, color, pts, width=0):
    pygame.draw.polygon(surf, color, pts, width)


def _bank(pts, cx, cy, roll_deg, bob):
    """Roll a point list a few degrees about (cx, cy) and lift it by `bob`.

    The whole craft pivots about its mass centre so the silhouette banks as one
    rigid folded sheet — the cheapest, most paper-plane-honest read of 'flap'."""
    r = math.radians(roll_deg)
    cos_r, sin_r = math.cos(r), math.sin(r)
    out = []
    for x, y in pts:
        dx, dy = x - cx, y - cy
        out.append((cx + dx * cos_r - dy * sin_r,
                    cy + dx * sin_r + dy * cos_r + bob))
    return out


def _rim(surf, color):
    """Bake a 1px self-rim hugging the painted silhouette, stamped UNDER the art
    so it shows only as a clean lip — the silhouette guarantee on any sky."""
    mask = pygame.mask.from_surface(surf, threshold=8)
    rim = mask.to_surface(setcolor=color, unsetcolor=(0, 0, 0, 0))
    out = _new()
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        out.blit(rim, (dx, dy))
    out.blit(surf, (0, 0))
    return out


def _clip_dots(surf, color, region_pts, x0, y0, x1, y1, step, r):
    """Stamp a Ben-Day halftone dot grid, clipped to a polygon region via a
    temp surface masked by the region. Hero-scale texture; near-invisible noise
    at 40px by design."""
    tmp = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    yy = y0
    row = 0
    while yy <= y1:
        xx = x0 + (step // 2 if row % 2 else 0)
        while xx <= x1:
            pygame.draw.circle(tmp, color, (int(xx), int(yy)), r)
            xx += step
        yy += step
        row += 1
    # Clip to the facet polygon so dots never spill past the fold/edge.
    clip = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    pygame.draw.polygon(clip, (255, 255, 255, 255), region_pts)
    tmp.blit(clip, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(tmp, (0, 0))


# Shared dart geometry. Top swept edge runs nose→far_tip as one straight line so
# the triangular dart silhouette is unambiguous; the nose is a tight point well
# past the mass centre. Identical across all five takes — only the SURFACE
# treatment of the facets changes.
def _geometry(roll, bob):
    nose       = (BCX + 25, BCY - 1)
    far_tip    = (BCX - 14, BCY - 13)
    near_tip   = (BCX - 12, BCY + 14)
    centre_back = (BCX - 16, BCY)
    far  = _bank([nose, far_tip, centre_back], BCX, BCY, roll, bob)   # lit top
    near = _bank([nose, near_tip, centre_back], BCX, BCY, roll, bob)  # under
    crease = _bank([nose, centre_back], BCX, BCY, roll, bob)
    return far, near, crease, (nose, far_tip, near_tip, centre_back)


def _base_fold(surf, far, near, crease, top_col, under_col, under_deep,
               crease_col, hi_col, nose, roll, bob):
    """Lay down the shared hard-fold value structure: dark under-fold, lit top
    facet, nose highlight, hard central crease. The per-take TELL is painted on
    top of the returned lit facet."""
    _poly(surf, under_col, near)
    _poly(surf, under_deep, _bank([nose, (BCX - 12, BCY + 14), (BCX - 5, BCY + 5)],
                                  BCX, BCY, roll, bob))
    _poly(surf, top_col, far)
    _poly(surf, hi_col, _bank([nose, (BCX + 7, BCY - 6), (BCX + 9, BCY - 1)],
                              BCX, BCY, roll, bob))
    a, b = crease
    pygame.draw.line(surf, crease_col, (int(a[0]), int(a[1])),
                     (int(b[0]), int(b[1])), 3)


def _columns(surf, region_pts, lines, col, roll, bob):
    """Faint vertical column rules on the lit facet — newsprint texture that
    deliberately fades to nothing at gameplay scale."""
    clip = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    tmp = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    for (x, y0, y1) in lines:
        p = _bank([(x, y0), (x, y1)], BCX, BCY, roll, bob)
        pygame.draw.line(tmp, col, (int(p[0][0]), int(p[0][1])),
                         (int(p[1][0]), int(p[1][1])), 1)
    pygame.draw.polygon(clip, (255, 255, 255, 255), region_pts)
    tmp.blit(clip, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(tmp, (0, 0))


# ═════════════════════════════════════════════════════════════════════════════
# V1 · CLASSIC GREY BROADSHEET — light newsprint paper, faint column rules, and
# a BOLD BLACK HEADLINE BAR slammed across the lit facet as the load-bearing
# tell. The black bar over pale grey is the whole read at 40px.
# ═════════════════════════════════════════════════════════════════════════════
_BS_TOP    = (224, 222, 214)        # lit upper facet — light newsprint
_BS_TOP_H  = (242, 241, 236)        # nose highlight
_BS_UNDER  = (150, 148, 140)        # shadowed under-fold (hard value break)
_BS_UNDER_D = (118, 116, 108)
_BS_CREASE = (74, 73, 68)
_BS_RIM    = (52, 51, 47)
_BS_INK    = (28, 27, 24)           # headline ink black
_BS_COL    = (176, 174, 166)        # faint column rules


def build_newsprint_v1(wing_angle_deg):
    surf = _new()
    f = _flutter(wing_angle_deg)
    roll = max(-_ROLL_MAX, min(_ROLL_MAX, f * 5.0))
    bob = -f * 1.3
    far, near, crease, _ = _geometry(roll, bob)
    nose = far[0]
    _base_fold(surf, far, near, crease, _BS_TOP, _BS_UNDER, _BS_UNDER_D,
               _BS_CREASE, _BS_TOP_H, nose, roll, bob)

    # Faint column rules on the lit facet (newsprint texture, fades at 40px).
    _columns(surf, far, [(BCX - 6, BCY - 11, BCY - 1), (BCX + 2, BCY - 10, BCY - 1),
                         (BCX + 10, BCY - 8, BCY - 2)], _BS_COL, roll, bob)

    # ── THE TELL: a bold black headline bar across the lit facet ──
    bar = _bank([(BCX - 11, BCY - 9), (BCX + 13, BCY - 5),
                 (BCX + 13, BCY - 2), (BCX - 11, BCY - 6)], BCX, BCY, roll, bob)
    _poly(surf, _BS_INK, bar)
    # A second thinner sub-head bar beneath it doubles the print rhythm at hero.
    sub = _bank([(BCX - 9, BCY - 3), (BCX + 5, BCY - 1),
                 (BCX + 5, BCY + 1), (BCX - 9, BCY - 1)], BCX, BCY, roll, bob)
    _poly(surf, (60, 58, 54), sub)
    return _rim(surf, _BS_RIM)


# ═════════════════════════════════════════════════════════════════════════════
# V2 · TABLOID — one screaming bold word ("WOW") in fat black caps fills the lit
# facet. The chunky letterforms ARE the tell; the silhouette stays the dart.
# ═════════════════════════════════════════════════════════════════════════════
_TB_TOP    = (236, 232, 222)        # bright tabloid stock
_TB_TOP_H  = (250, 248, 242)
_TB_UNDER  = (158, 150, 138)
_TB_UNDER_D = (124, 118, 108)
_TB_CREASE = (78, 74, 66)
_TB_RIM    = (54, 50, 44)
_TB_INK    = (24, 22, 20)
_TB_RED    = (196, 40, 36)          # tabloid masthead red (tiny accent)


def _glyph(surf, ch, x, y, h, col, roll, bob):
    """A few fat block capitals drawn from rectangles/strokes so the headline
    word survives as bold ink mass even when the letters blur at 40px."""
    w = h - 1
    th = max(2, h // 3)             # stroke thickness — keep glyphs HEAVY
    def bar(x0, y0, x1, y1):
        p = _bank([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], BCX, BCY, roll, bob)
        _poly(surf, col, p)
    if ch == "W":
        bar(x, y, x + th, y + h)
        bar(x + w - th, y, x + w, y + h)
        bar(x + th, y + h - th, x + w - th, y + h)       # valley floor
        bar(x + (w - th) // 2, y + h // 2, x + (w + th) // 2 - 0, y + h)
    elif ch == "O":
        bar(x, y, x + th, y + h)
        bar(x + w - th, y, x + w, y + h)
        bar(x, y, x + w, y + th)
        bar(x, y + h - th, x + w, y + h)
    elif ch == "!":
        bar(x + w // 2 - th // 2, y, x + w // 2 + th // 2 + 1, y + h - th - 1)
        bar(x + w // 2 - th // 2, y + h - th, x + w // 2 + th // 2 + 1, y + h)


def build_newsprint_v2(wing_angle_deg):
    surf = _new()
    f = _flutter(wing_angle_deg)
    roll = max(-_ROLL_MAX, min(_ROLL_MAX, f * 5.0))
    bob = -f * 1.3
    far, near, crease, _ = _geometry(roll, bob)
    nose = far[0]
    _base_fold(surf, far, near, crease, _TB_TOP, _TB_UNDER, _TB_UNDER_D,
               _TB_CREASE, _TB_TOP_H, nose, roll, bob)

    # Thin red masthead rule above the word — a vintage-tabloid accent.
    rule = _bank([(BCX - 12, BCY - 11), (BCX + 9, BCY - 7),
                  (BCX + 9, BCY - 6), (BCX - 12, BCY - 10)], BCX, BCY, roll, bob)
    _poly(surf, _TB_RED, rule)

    # ── THE TELL: the screaming word "WOW" in fat black caps ──
    _glyph(surf, "W", BCX - 11, BCY - 6, 8, _TB_INK, roll, bob)
    _glyph(surf, "O", BCX - 2, BCY - 5, 8, _TB_INK, roll, bob)
    _glyph(surf, "W", BCX + 6, BCY - 4, 8, _TB_INK, roll, bob)
    return _rim(surf, _TB_RIM)


# ═════════════════════════════════════════════════════════════════════════════
# V3 · SUNDAY COMIC — the lit facet carries a fat halftone-DOT field in CMYK
# yellow, and a small black "POW!" burst panel slammed on top is the bold tell.
# Colour + black star = the most pop-art, most premium read.
# ═════════════════════════════════════════════════════════════════════════════
_CM_TOP    = (240, 238, 228)        # bright comic newsprint
_CM_TOP_H  = (252, 250, 244)
_CM_UNDER  = (160, 152, 136)
_CM_UNDER_D = (126, 118, 104)
_CM_CREASE = (74, 70, 60)
_CM_RIM    = (50, 46, 40)
_CM_DOT    = (250, 206, 70)         # Ben-Day yellow halftone
_CM_DOT_R  = (228, 96, 96)          # a second dot colour (magenta-ish)
_CM_INK    = (24, 22, 20)
_CM_BURST  = (224, 52, 48)          # POW burst red fill


def build_newsprint_v3(wing_angle_deg):
    surf = _new()
    f = _flutter(wing_angle_deg)
    roll = max(-_ROLL_MAX, min(_ROLL_MAX, f * 5.0))
    bob = -f * 1.3
    far, near, crease, _ = _geometry(roll, bob)
    nose = far[0]
    _base_fold(surf, far, near, crease, _CM_TOP, _CM_UNDER, _CM_UNDER_D,
               _CM_CREASE, _CM_TOP_H, nose, roll, bob)

    # Halftone dot field across the lit facet — the comic-print texture.
    far_dots = _bank([(BCX + 22, BCY - 1), (BCX - 13, BCY - 12),
                      (BCX - 15, BCY)], BCX, BCY, roll, bob)
    _clip_dots(surf, _CM_DOT, far_dots, BCX - 12, BCY - 11, BCX + 18, BCY - 1, 4, 2)
    _clip_dots(surf, _CM_DOT_R, far_dots, BCX - 10, BCY - 9, BCX + 14, BCY - 2, 6, 1)

    # ── THE TELL: a small black-outlined red starburst "POW" panel ──
    cx, cy = _bank([(BCX - 1, BCY - 6)], BCX, BCY, roll, bob)[0]
    burst = []
    for i in range(10):
        ang = math.radians(i * 36 - 90)
        rr = 8 if i % 2 == 0 else 4
        burst.append((cx + math.cos(ang) * rr, cy + math.sin(ang) * rr * 0.8))
    _poly(surf, _CM_INK, burst)
    inner = [(cx + (p[0] - cx) * 0.78, cy + (p[1] - cy) * 0.78) for p in burst]
    _poly(surf, _CM_BURST, inner)
    # A bright core so the star holds a hard centre highlight at downscale.
    pygame.draw.circle(surf, (252, 244, 220), (int(cx), int(cy - 1)), 2)
    return _rim(surf, _CM_RIM)


# ═════════════════════════════════════════════════════════════════════════════
# V4 · SEPIA / AGED NEWSPAPER — warm tea-stained antique stock, faint columns,
# and an OLD-STYLE black headline block with a dark-brown rule beneath. Vintage,
# warmer than V1; the black block still does the heavy lifting at 40px.
# ═════════════════════════════════════════════════════════════════════════════
_SP_TOP    = (222, 200, 158)        # aged sepia stock
_SP_TOP_H  = (240, 222, 184)
_SP_UNDER  = (150, 122, 84)         # tea-stained shadow under-fold
_SP_UNDER_D = (120, 94, 60)
_SP_CREASE = (84, 62, 38)
_SP_RIM    = (66, 48, 30)
_SP_INK    = (40, 28, 18)           # aged ink (warm near-black)
_SP_COL    = (188, 162, 120)
_SP_RULE   = (110, 78, 44)


def build_newsprint_v4(wing_angle_deg):
    surf = _new()
    f = _flutter(wing_angle_deg)
    roll = max(-_ROLL_MAX, min(_ROLL_MAX, f * 5.0))
    bob = -f * 1.3
    far, near, crease, _ = _geometry(roll, bob)
    nose = far[0]
    _base_fold(surf, far, near, crease, _SP_TOP, _SP_UNDER, _SP_UNDER_D,
               _SP_CREASE, _SP_TOP_H, nose, roll, bob)

    # Faint columns + a warm foxing speckle for the aged feel (hero texture).
    _columns(surf, far, [(BCX - 5, BCY - 11, BCY - 1), (BCX + 4, BCY - 10, BCY - 1),
                         (BCX + 11, BCY - 8, BCY - 2)], _SP_COL, roll, bob)
    for fx, fy in ((BCX - 8, BCY - 8), (BCX + 6, BCY - 9), (BCX + 12, BCY - 4),
                   (BCX - 3, BCY - 10)):
        p = _bank([(fx, fy)], BCX, BCY, roll, bob)[0]
        pygame.draw.circle(surf, (164, 132, 88), (int(p[0]), int(p[1])), 1)

    # ── THE TELL: an old-style black headline block + a brown rule beneath ──
    block = _bank([(BCX - 11, BCY - 9), (BCX + 12, BCY - 5),
                   (BCX + 12, BCY - 1), (BCX - 11, BCY - 5)], BCX, BCY, roll, bob)
    _poly(surf, _SP_INK, block)
    rule = _bank([(BCX - 10, BCY + 1), (BCX + 9, BCY + 3),
                  (BCX + 9, BCY + 4), (BCX - 10, BCY + 2)], BCX, BCY, roll, bob)
    _poly(surf, _SP_RULE, rule)
    return _rim(surf, _SP_RIM)


# ═════════════════════════════════════════════════════════════════════════════
# V5 · CROSSWORD GRID — the lit facet is a clean crossword panel: a bold black
# grid of squares with a few INKED-BLACK cells. The high-contrast black/white
# checker is the tell; it stays a crisp graphic mark at 40px.
# ═════════════════════════════════════════════════════════════════════════════
_XW_TOP    = (238, 236, 228)        # bright puzzle-page stock
_XW_TOP_H  = (250, 249, 244)
_XW_UNDER  = (154, 150, 140)
_XW_UNDER_D = (120, 116, 108)
_XW_CREASE = (74, 72, 66)
_XW_RIM    = (50, 48, 44)
_XW_INK    = (26, 25, 22)
_XW_LINE   = (90, 88, 82)


def build_newsprint_v5(wing_angle_deg):
    surf = _new()
    f = _flutter(wing_angle_deg)
    roll = max(-_ROLL_MAX, min(_ROLL_MAX, f * 5.0))
    bob = -f * 1.3
    far, near, crease, _ = _geometry(roll, bob)
    nose = far[0]
    _base_fold(surf, far, near, crease, _XW_TOP, _XW_UNDER, _XW_UNDER_D,
               _XW_CREASE, _XW_TOP_H, nose, roll, bob)

    # ── THE TELL: a crossword grid with a few inked cells ──
    # A 3x3 cell block on the lit facet. Inked cells give the bold black mass
    # that survives downscale; grid lines give the puzzle read at hero.
    ox, oy = BCX - 10, BCY - 11
    cell = 5
    inked = {(0, 0), (1, 1), (2, 0), (1, 2)}     # checker of solid-black cells
    for gy in range(3):
        for gx in range(3):
            x0 = ox + gx * cell
            y0 = oy + gy * cell + gx          # slight skew so it sits on the facet
            quad = _bank([(x0, y0), (x0 + cell, y0),
                          (x0 + cell, y0 + cell), (x0, y0 + cell)],
                         BCX, BCY, roll, bob)
            if (gx, gy) in inked:
                _poly(surf, _XW_INK, quad)
            else:
                _poly(surf, _XW_LINE, quad, 1)
    return _rim(surf, _XW_RIM)


# ── getters + label→getter registry ──────────────────────────────────────────
get_newsprint_v1 = _make_prebuilt_skin(build_newsprint_v1)
get_newsprint_v2 = _make_prebuilt_skin(build_newsprint_v2)
get_newsprint_v3 = _make_prebuilt_skin(build_newsprint_v3)
get_newsprint_v4 = _make_prebuilt_skin(build_newsprint_v4)
get_newsprint_v5 = _make_prebuilt_skin(build_newsprint_v5)

# Label → getter for the review sheet.
VARIANTS = {
    "V1 · BROADSHEET  (black headline bar)": get_newsprint_v1,
    "V2 · TABLOID  (\"WOW\" caps)":          get_newsprint_v2,
    "V3 · SUNDAY COMIC  (halftone + POW)":   get_newsprint_v3,
    "V4 · SEPIA  (aged headline block)":     get_newsprint_v4,
    "V5 · CROSSWORD  (inked grid)":          get_newsprint_v5,
}

# Production registry (the winner lifts back into game/animal_paper_plane.py).
BUILDERS = {"skin_newsprint": get_newsprint_v1}
