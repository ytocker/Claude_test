"""Candidate PAPER PLANE skin — concept NOTEBOOK PAPER — round-1 exploration.

A secret ultra-premium NON-creature flyer: the player's flapping bird becomes
a dart folded from BLUE-RULED schoolyard notebook paper. Faint blue horizontal
rule lines, a vertical RED margin stripe, and a torn spiral-notebook edge. There
are no wings — the 4 base wing poses are reinterpreted as a gentle BANK/FLUTTER:
the dart rolls a few degrees and the nose bobs as it catches air.

Contract (mirrors game/animal_paper_plane.py so this lifts straight into a
standalone production module):

  * `build_<name>(wing_angle_deg) -> pygame.Surface`  draws one flat frame on a
    64×84 SRCALPHA canvas (COMPOSITE_W=64, COMPOSITE_H=84).
  * the craft's mass is centred at the BODY anchor (32, 44) — collision is a
    fixed 14px circle there, so the dart keeps its centre of mass on that point
    regardless of how far the nose reaches.
  * NOSE POINTS RIGHT (forward); the bird faces right.
  * a cached `(frame_idx, tilt_deg) -> Surface` getter from
    `_make_prebuilt_skin(build_fn)`.
  * a label→getter `BUILDERS` registry at the bottom.

North star: "a skin lives or dies at 40px in motion." Each variant leans on ONE
bold triangular dart silhouette + a hard-value FOLD (a bright upper facet and a
distinctly darker under-fold meeting at a crisp keel crease). The signature
notebook tell at 40px is the RED margin stripe + one or two BOLD blue rules
reading as "lined paper"; the finer rules, holes and doodles are HERO texture
that politely vanishes at gameplay scale. A baked 1px self-rim keeps the dart
legible on day AND night skies without leaning on any host outline.
"""
import math
import pygame

from game.parrot import (
    SPRITE_W, _WING_ANGLES, _add_outline, _aaellipse,
)


# ── canvas constants (match game/animal_paper_plane.py) ──────────────────────
COMPOSITE_W = SPRITE_W          # 64
COMPOSITE_H = 84
DY          = 12

BCX, BCY = 32, 32 + DY          # body / mass centre → (32, 44)


# ── shared factory (local copy of _make_prebuilt_skin) ───────────────────────
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


def _self_rim(surf, rim_col):
    """Bake a 1px darker self-rim hugging the WHOLE dart silhouette so it never
    depends on the host outline — stamped UNDER the art so it reads as a clean
    1px lip, no glow halo (glow restraint)."""
    mask = pygame.mask.from_surface(surf, threshold=8)
    rim = mask.to_surface(setcolor=rim_col, unsetcolor=(0, 0, 0, 0))
    out = _new()
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        out.blit(rim, (dx, dy))
    out.blit(surf, (0, 0))
    return out


def _clip_to_poly(stamp_fn, clip_pts):
    """Run `stamp_fn(tmp)` onto a scratch surface, then keep only the pixels
    inside `clip_pts` — lets us draw rules/holes that stop cleanly at the paper's
    folded facet edge instead of bleeding past the silhouette."""
    tmp = _new()
    stamp_fn(tmp)
    mask_surf = _new()
    pygame.draw.polygon(mask_surf, (255, 255, 255, 255),
                        [(int(x), int(y)) for x, y in clip_pts])
    mask = pygame.mask.from_surface(mask_surf, threshold=8)
    keep = pygame.mask.from_surface(tmp, threshold=1)
    keep = keep.overlap_mask(mask, (0, 0)) if False else keep
    # Intersect by zeroing tmp pixels outside the clip polygon.
    inside = mask.to_surface(setcolor=(255, 255, 255, 255),
                             unsetcolor=(0, 0, 0, 0))
    tmp.blit(inside, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return tmp


# Roll is clamped so the bank-roll "flap" never flattens the dart to a sliver:
# at 3/4 view the under-fold collapses if the craft rolls too far edge-on.
_ROLL_MAX = 5.5


# ═════════════════════════════════════════════════════════════════════════════
# Shared dart geometry. A crisp triangular dart nosing RIGHT, mass centred on
# (BCX, BCY). The top swept edge is a single straight nose→far_tip line so the
# triangular silhouette is unambiguous; the keel crease splits a LIT top facet
# from a darker UNDER-fold.
# ═════════════════════════════════════════════════════════════════════════════
def _dart_pts():
    nose       = (BCX + 25, BCY - 1)
    far_tip    = (BCX - 14, BCY - 13)     # upper trailing corner
    near_tip   = (BCX - 12, BCY + 14)     # lower trailing corner
    centre_back = (BCX - 16, BCY)         # keel meets trailing edge
    return nose, far_tip, near_tip, centre_back


def _build_dart(wing_angle_deg, *, paper, paper_h, under, under_d, crease,
                rim, rule, rule_bold, margin, hero, hero_fn=None):
    """Shared dart renderer. Colours + a hero detail callback are injected so
    each variant restyles ONLY the notebook treatment, not the fold structure.

    `hero_fn(surf, ctx)` draws size-only flourishes (fine rules, holes, doodles)
    given a context dict of banked anchor points.
    """
    surf = _new()
    f = _flutter(wing_angle_deg)
    roll = max(-_ROLL_MAX, min(_ROLL_MAX, f * 5.0))
    bob = -f * 1.3

    nose, far_tip, near_tip, centre_back = _dart_pts()

    def B(pts):
        return _bank(pts, BCX, BCY, roll, bob)

    # ── UNDER-fold first (lower facet, in shadow) ────────────────────────────
    near = B([nose, near_tip, centre_back])
    _poly(surf, under, near)
    _poly(surf, under_d, B([nose, near_tip, (BCX - 5, BCY + 5)]))

    # ── TOP facet (lit upper sheet) ──────────────────────────────────────────
    far = B([nose, far_tip, centre_back])
    _poly(surf, paper, far)
    # Leading-edge highlight at the nose where the top folds meet.
    _poly(surf, paper_h, B([nose, (BCX + 7, BCY - 6), (BCX + 9, BCY - 1)]))

    ctx = {
        "B": B, "nose": nose, "far_tip": far_tip, "near_tip": near_tip,
        "centre_back": centre_back, "far_facet": far, "near_facet": near,
        "rule": rule, "rule_bold": rule_bold, "margin": margin,
        "paper": paper, "under": under, "crease": crease,
    }

    # ── HERO texture (fine rules / holes / doodles) — drawn before the keel so
    #    the crease always overpaints them cleanly.
    if hero and hero_fn is not None:
        hero_fn(surf, ctx)

    # ── HARD keel crease (the fold spine) — 3px hard value break at 40px. ─────
    a, b = B([nose, centre_back])
    pygame.draw.line(surf, crease, (int(a[0]), int(a[1])),
                     (int(b[0]), int(b[1])), 3)

    return _self_rim(surf, rim)


# ═════════════════════════════════════════════════════════════════════════════
# V1 · CLASSIC RULED — bright white loose-leaf, STRAIGHT blue rules running flat
#     across the top facet, RED margin stripe along the KEEL. Spiral punch-holes
#     dot the upper trailing edge. The textbook "lined paper" read.
# ═════════════════════════════════════════════════════════════════════════════
_V1_PAPER   = (248, 248, 244)
_V1_PAPER_H = (255, 255, 252)
_V1_UNDER   = (196, 200, 206)        # shadowed under-sheet (cool grey)
_V1_UNDER_D = (168, 174, 184)
_V1_CREASE  = (120, 126, 138)
_V1_RIM     = (110, 116, 128)
_V1_RULE    = (132, 168, 214)        # faint pencil-blue rule
_V1_RULE_B  = (84, 132, 198)         # one bold rule (load-bearing tell)
_V1_MARGIN  = (220, 70, 72)          # red margin stripe


def _v1_hero(surf, ctx):
    B = ctx["B"]
    # Blue rules running flat across the lit facet, clipped to the facet.
    def _rules(tmp):
        for ry in (BCY - 9, BCY - 5, BCY - 1):
            bold = (ry == BCY - 5)
            col = _V1_RULE_B if bold else _V1_RULE
            p = B([(BCX - 10, ry), (BCX + 18, ry - 2)])
            pygame.draw.line(tmp, col, (int(p[0][0]), int(p[0][1])),
                             (int(p[1][0]), int(p[1][1])), 2 if bold else 1)
    clipped = _clip_to_poly(_rules, ctx["far_facet"])
    surf.blit(clipped, (0, 0))
    # Spiral punch-holes nipped out of the upper trailing edge.
    for hx, hy in B([(BCX - 11, BCY - 11), (BCX - 13, BCY - 6)]):
        pygame.draw.circle(surf, (210, 212, 214), (int(hx), int(hy)), 2)
        pygame.draw.circle(surf, (150, 156, 168), (int(hx), int(hy)), 2, 1)


def build_notebook_v1(wing_angle_deg, hero=False):
    surf = _build_dart(
        wing_angle_deg, paper=_V1_PAPER, paper_h=_V1_PAPER_H,
        under=_V1_UNDER, under_d=_V1_UNDER_D, crease=_V1_CREASE,
        rim=_V1_RIM, rule=_V1_RULE, rule_bold=_V1_RULE_B, margin=_V1_MARGIN,
        hero=hero, hero_fn=_v1_hero)
    # Red margin stripe along the keel — drawn AFTER the rim build so it stays
    # vivid; it is the load-bearing 40px tell, so it lives at every scale.
    f = _flutter(wing_angle_deg)
    roll = max(-_ROLL_MAX, min(_ROLL_MAX, f * 5.0))
    bob = -f * 1.3
    nose, _, _, centre_back = _dart_pts()
    # A stripe sitting just ABOVE the keel on the lit facet.
    pa, pb = _bank([(BCX + 18, BCY - 4), (BCX - 13, BCY - 3)],
                   BCX, BCY, roll, bob)
    pygame.draw.line(surf, _V1_MARGIN, (int(pa[0]), int(pa[1])),
                     (int(pb[0]), int(pb[1])), 2)
    return surf


def build_notebook_v1_hero(wing_angle_deg):
    return build_notebook_v1(wing_angle_deg, hero=True)


# ═════════════════════════════════════════════════════════════════════════════
# V2 · FOLD-FOLLOWING — rules BEND down along the two fold facets (the rules tilt
#     with each facet's slope, selling the 3D paper), RED margin runs along the
#     TOP swept edge. A torn fringe nibbles the trailing edge.
# ═════════════════════════════════════════════════════════════════════════════
_V2_PAPER   = (250, 250, 246)
_V2_PAPER_H = (255, 255, 253)
_V2_UNDER   = (190, 196, 204)
_V2_UNDER_D = (160, 168, 180)
_V2_CREASE  = (114, 122, 136)
_V2_RIM     = (104, 112, 126)
_V2_RULE    = (138, 172, 216)
_V2_RULE_B  = (78, 128, 196)
_V2_MARGIN  = (216, 64, 70)


def _v2_hero(surf, ctx):
    B = ctx["B"]
    # Rules following the LIT facet slope (nose-down toward the trailing far_tip)
    # so they look painted onto a tilted sheet rather than floating.
    def _rules(tmp):
        for i, off in enumerate((-9, -6, -3)):
            bold = (i == 1)
            col = _V2_RULE_B if bold else _V2_RULE
            # Slope matches the top swept edge (nose→far_tip).
            p = B([(BCX + 16, BCY + off + 2), (BCX - 11, BCY + off - 6)])
            pygame.draw.line(tmp, col, (int(p[0][0]), int(p[0][1])),
                             (int(p[1][0]), int(p[1][1])), 2 if bold else 1)
    surf.blit(_clip_to_poly(_rules, ctx["far_facet"]), (0, 0))
    # Rules on the UNDER facet too, sloping the OTHER way, to read as a fold.
    def _under_rules(tmp):
        for off in (4, 8):
            p = B([(BCX + 14, BCY + off - 1), (BCX - 9, BCY + off + 4)])
            pygame.draw.line(tmp, (150, 158, 172),
                             (int(p[0][0]), int(p[0][1])),
                             (int(p[1][0]), int(p[1][1])), 1)
    surf.blit(_clip_to_poly(_under_rules, ctx["near_facet"]), (0, 0))


def build_notebook_v2(wing_angle_deg, hero=False):
    surf = _build_dart(
        wing_angle_deg, paper=_V2_PAPER, paper_h=_V2_PAPER_H,
        under=_V2_UNDER, under_d=_V2_UNDER_D, crease=_V2_CREASE,
        rim=_V2_RIM, rule=_V2_RULE, rule_bold=_V2_RULE_B, margin=_V2_MARGIN,
        hero=hero, hero_fn=_v2_hero)
    f = _flutter(wing_angle_deg)
    roll = max(-_ROLL_MAX, min(_ROLL_MAX, f * 5.0))
    bob = -f * 1.3
    # Red margin along the TOP swept leading edge (nose→far_tip) — the tell.
    pa, pb = _bank([(BCX + 21, BCY - 4), (BCX - 12, BCY - 11)],
                   BCX, BCY, roll, bob)
    pygame.draw.line(surf, _V2_MARGIN, (int(pa[0]), int(pa[1])),
                     (int(pb[0]), int(pb[1])), 2)
    return surf


def build_notebook_v2_hero(wing_angle_deg):
    return build_notebook_v2(wing_angle_deg, hero=True)


# ═════════════════════════════════════════════════════════════════════════════
# V3 · CREAM + BIRO STAR — aged cream paper, fewer but BOLDER rules, RED keel
#     margin, and a tiny blue ball-point STAR doodled on the lit facet as the
#     personality accent. Spiral holes on the keel side.
# ═════════════════════════════════════════════════════════════════════════════
_V3_PAPER   = (244, 236, 212)        # warm cream
_V3_PAPER_H = (252, 247, 228)
_V3_UNDER   = (196, 184, 152)        # warm shadowed under-sheet
_V3_UNDER_D = (168, 156, 124)
_V3_CREASE  = (134, 120, 88)
_V3_RIM     = (124, 110, 80)
_V3_RULE    = (150, 174, 206)
_V3_RULE_B  = (88, 130, 188)
_V3_MARGIN  = (212, 78, 72)
_V3_BIRO    = (54, 96, 174)          # ball-point ink


def _v3_star(surf, cx, cy, r, col):
    """A tiny 5-point biro star outline — schoolyard margin doodle."""
    pts = []
    for k in range(10):
        ang = -math.pi / 2 + k * math.pi / 5
        rad = r if k % 2 == 0 else r * 0.45
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in pts], 1)


def _v3_hero(surf, ctx):
    B = ctx["B"]
    def _rules(tmp):
        for i, ry in enumerate((BCY - 9, BCY - 4)):
            bold = (i == 1)
            col = _V3_RULE_B if bold else _V3_RULE
            p = B([(BCX - 10, ry), (BCX + 18, ry - 2)])
            pygame.draw.line(tmp, col, (int(p[0][0]), int(p[0][1])),
                             (int(p[1][0]), int(p[1][1])), 2 if bold else 1)
    surf.blit(_clip_to_poly(_rules, ctx["far_facet"]), (0, 0))
    # Biro star doodle up on the lit facet.
    sx, sy = B([(BCX + 4, BCY - 8)])[0]
    _v3_star(surf, sx, sy, 4, _V3_BIRO)
    # Spiral holes on the keel-side trailing edge.
    for hx, hy in B([(BCX - 12, BCY - 9), (BCX - 14, BCY - 4)]):
        pygame.draw.circle(surf, (224, 214, 188), (int(hx), int(hy)), 2)
        pygame.draw.circle(surf, (168, 152, 120), (int(hx), int(hy)), 2, 1)


def build_notebook_v3(wing_angle_deg, hero=False):
    surf = _build_dart(
        wing_angle_deg, paper=_V3_PAPER, paper_h=_V3_PAPER_H,
        under=_V3_UNDER, under_d=_V3_UNDER_D, crease=_V3_CREASE,
        rim=_V3_RIM, rule=_V3_RULE, rule_bold=_V3_RULE_B, margin=_V3_MARGIN,
        hero=hero, hero_fn=_v3_hero)
    f = _flutter(wing_angle_deg)
    roll = max(-_ROLL_MAX, min(_ROLL_MAX, f * 5.0))
    bob = -f * 1.3
    pa, pb = _bank([(BCX + 18, BCY - 4), (BCX - 13, BCY - 3)],
                   BCX, BCY, roll, bob)
    pygame.draw.line(surf, _V3_MARGIN, (int(pa[0]), int(pa[1])),
                     (int(pb[0]), int(pb[1])), 2)
    return surf


def build_notebook_v3_hero(wing_angle_deg):
    return build_notebook_v3(wing_angle_deg, hero=True)


# ═════════════════════════════════════════════════════════════════════════════
# V4 · GRADED "A+" — crisp white, DENSE fine rules + 2 bold rules, RED keel
#     margin, and a cheeky red "A+" scrawl as the accent. Torn tear-fringe along
#     the bottom trailing edge.
# ═════════════════════════════════════════════════════════════════════════════
_V4_PAPER   = (249, 250, 247)
_V4_PAPER_H = (255, 255, 254)
_V4_UNDER   = (192, 198, 206)
_V4_UNDER_D = (162, 170, 182)
_V4_CREASE  = (116, 124, 138)
_V4_RIM     = (106, 114, 128)
_V4_RULE    = (146, 178, 220)
_V4_RULE_B  = (80, 130, 198)
_V4_MARGIN  = (222, 66, 66)
_V4_INK     = (208, 56, 58)          # red grade scrawl


def _v4_hero(surf, ctx):
    B = ctx["B"]
    def _rules(tmp):
        for ry in (BCY - 10, BCY - 8, BCY - 6, BCY - 4, BCY - 2):
            bold = ry in (BCY - 8, BCY - 4)
            col = _V4_RULE_B if bold else _V4_RULE
            p = B([(BCX - 10, ry), (BCX + 18, ry - 2)])
            pygame.draw.line(tmp, col, (int(p[0][0]), int(p[0][1])),
                             (int(p[1][0]), int(p[1][1])), 2 if bold else 1)
    surf.blit(_clip_to_poly(_rules, ctx["far_facet"]), (0, 0))
    # "A+" scrawl: a chevron A and a small plus, in red ink.
    ax, ay = B([(BCX + 3, BCY - 7)])[0]
    pygame.draw.lines(surf, _V4_INK, False,
                      [(int(ax - 3), int(ay + 3)), (int(ax), int(ay - 3)),
                       (int(ax + 3), int(ay + 3))], 1)
    pygame.draw.line(surf, _V4_INK, (int(ax - 2), int(ay + 1)),
                     (int(ax + 2), int(ay + 1)), 1)
    px, py = B([(BCX + 9, BCY - 7)])[0]
    pygame.draw.line(surf, _V4_INK, (int(px - 2), int(py)),
                     (int(px + 2), int(py)), 1)
    pygame.draw.line(surf, _V4_INK, (int(px), int(py - 2)),
                     (int(px), int(py + 2)), 1)
    # Torn fringe along the lower trailing edge — little notches.
    for nx, ny in B([(BCX - 9, BCY + 9), (BCX - 11, BCY + 5),
                     (BCX - 7, BCY + 12)]):
        pygame.draw.circle(surf, _V4_UNDER_D, (int(nx), int(ny)), 1)


def build_notebook_v4(wing_angle_deg, hero=False):
    surf = _build_dart(
        wing_angle_deg, paper=_V4_PAPER, paper_h=_V4_PAPER_H,
        under=_V4_UNDER, under_d=_V4_UNDER_D, crease=_V4_CREASE,
        rim=_V4_RIM, rule=_V4_RULE, rule_bold=_V4_RULE_B, margin=_V4_MARGIN,
        hero=hero, hero_fn=_v4_hero)
    f = _flutter(wing_angle_deg)
    roll = max(-_ROLL_MAX, min(_ROLL_MAX, f * 5.0))
    bob = -f * 1.3
    pa, pb = _bank([(BCX + 18, BCY - 4), (BCX - 13, BCY - 3)],
                   BCX, BCY, roll, bob)
    pygame.draw.line(surf, _V4_MARGIN, (int(pa[0]), int(pa[1])),
                     (int(pb[0]), int(pb[1])), 2)
    return surf


def build_notebook_v4_hero(wing_angle_deg):
    return build_notebook_v4(wing_angle_deg, hero=True)


# ═════════════════════════════════════════════════════════════════════════════
# V5 · BOLD LOOSE-LEAF — the minimal, most legible take: a BOLD red margin stripe
#     + just TWO heavy blue rules carry the whole tell, three binder ring-holes
#     punched along the keel edge. Cleanest fold, off-white loose-leaf. Built to
#     win at 40px where thin rules vanish.
# ═════════════════════════════════════════════════════════════════════════════
_V5_PAPER   = (246, 247, 242)
_V5_PAPER_H = (255, 255, 251)
_V5_UNDER   = (188, 194, 202)
_V5_UNDER_D = (156, 164, 176)
_V5_CREASE  = (108, 116, 130)
_V5_RIM     = (98, 106, 120)
_V5_RULE    = (96, 142, 206)         # both rules are bold here
_V5_RULE_B  = (62, 112, 188)
_V5_MARGIN  = (212, 56, 60)          # vivid bold margin — the hero tell


def _v5_hero(surf, ctx):
    B = ctx["B"]
    # Three binder ring-holes punched along the upper trailing edge.
    for hx, hy in B([(BCX - 11, BCY - 11), (BCX - 13, BCY - 7),
                     (BCX - 14, BCY - 3)]):
        pygame.draw.circle(surf, (208, 212, 216), (int(hx), int(hy)), 2)
        pygame.draw.circle(surf, (140, 148, 162), (int(hx), int(hy)), 2, 1)


def build_notebook_v5(wing_angle_deg, hero=False):
    surf = _build_dart(
        wing_angle_deg, paper=_V5_PAPER, paper_h=_V5_PAPER_H,
        under=_V5_UNDER, under_d=_V5_UNDER_D, crease=_V5_CREASE,
        rim=_V5_RIM, rule=_V5_RULE, rule_bold=_V5_RULE_B, margin=_V5_MARGIN,
        hero=hero, hero_fn=_v5_hero)
    # The two HEAVY blue rules + the bold red margin are load-bearing, so they
    # are drawn at EVERY scale (not gated behind hero) — this is the variant
    # built to survive the 40px downscale.
    f = _flutter(wing_angle_deg)
    roll = max(-_ROLL_MAX, min(_ROLL_MAX, f * 5.0))
    bob = -f * 1.3
    nose, far_tip, near_tip, centre_back = _dart_pts()
    far = _bank([nose, far_tip, centre_back], BCX, BCY, roll, bob)

    def _rules(tmp):
        for ry in (BCY - 9, BCY - 5):
            p = _bank([(BCX - 10, ry), (BCX + 17, ry - 2)],
                      BCX, BCY, roll, bob)
            pygame.draw.line(tmp, _V5_RULE_B, (int(p[0][0]), int(p[0][1])),
                             (int(p[1][0]), int(p[1][1])), 2)
    surf.blit(_clip_to_poly(_rules, far), (0, 0))

    pa, pb = _bank([(BCX + 18, BCY - 2), (BCX - 13, BCY - 1)],
                   BCX, BCY, roll, bob)
    pygame.draw.line(surf, _V5_MARGIN, (int(pa[0]), int(pa[1])),
                     (int(pb[0]), int(pb[1])), 3)
    return surf


def build_notebook_v5_hero(wing_angle_deg):
    return build_notebook_v5(wing_angle_deg, hero=True)


# ─────────────────────────────────────────────────────────────────────────────
# Exploration registry. label → (gameplay getter, hero getter). The sheet uses
# the hero getter for the 130px hero panel and the gameplay getter for the 40px
# truth-test reads.
# ─────────────────────────────────────────────────────────────────────────────
BUILDERS = {
    "skin_notebook_v1": _make_prebuilt_skin(build_notebook_v1),
    "skin_notebook_v2": _make_prebuilt_skin(build_notebook_v2),
    "skin_notebook_v3": _make_prebuilt_skin(build_notebook_v3),
    "skin_notebook_v4": _make_prebuilt_skin(build_notebook_v4),
    "skin_notebook_v5": _make_prebuilt_skin(build_notebook_v5),
}

HERO_BUILDERS = {
    "skin_notebook_v1": _make_prebuilt_skin(build_notebook_v1_hero),
    "skin_notebook_v2": _make_prebuilt_skin(build_notebook_v2_hero),
    "skin_notebook_v3": _make_prebuilt_skin(build_notebook_v3_hero),
    "skin_notebook_v4": _make_prebuilt_skin(build_notebook_v4_hero),
    "skin_notebook_v5": _make_prebuilt_skin(build_notebook_v5_hero),
}
