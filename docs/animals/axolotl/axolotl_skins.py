"""Candidate AXOLOTL skins for the coin Store — round-1 exploration.

Five GENUINELY DIFFERENT takes on one creature: the smiling pink amphibian
with a fan of feathery external gills. The gill-frill halo + dot-eyed grin is
the 40px tell — nothing else in the roster wears a "headdress". The flap is
reinterpreted as a frilled fin-stroke: gills sweep BACK on the down-pose and
BLOOM open on the up-pose, like fronds pulsing through water.

Contract mirrors game/animal_skins.py so the winner lifts straight in:

  * `build_axolotl_v<N>(wing_angle_deg) -> pygame.Surface`  one flat frame on
    a 64×84 SRCALPHA canvas (COMPOSITE_W=64, COMPOSITE_H=84).
  * body mass centred at (32,44); head near (44,34); ~24px top headroom for the
    gill halo; collision is a fixed 14px circle at the body centre.
  * a cached `(frame_idx, tilt_deg) -> Surface` getter via `_make_prebuilt_skin`.
  * a label→getter dict at the bottom for the review sheet.

The five takes differ in SILHOUETTE, not palette tweaks:
  v1 CLASSIC PINK    — six tidy feathery fronds, plump body, tiny dot smile.
  v2 BUSHY CORAL     — dense bushy gill clusters (pom-poms), chunkier body.
  v3 ANTLER LEUCISTIC— bold antler-like branching gills, white morph, wide grin.
  v4 MELANOID DARK   — dark morph, glowing magenta gill cores as the contrast.
  v5 GOLDEN GILD     — gold morph, swept feather-fan gills, sparkle iridophores.
"""
import math
import pygame


# ── tall-canvas constants (mirrors game/animal_skins.py) ─────────────────────
SPRITE_W = 64
COMPOSITE_W = SPRITE_W          # 64
COMPOSITE_H = 84                # headroom for the gill-frill halo
DY          = 12

BCX, BCY = 32, 32 + DY          # body centre  → (32, 44)
HCX, HCY = 44, 22 + DY          # head centre  → (44, 34)
CROWN_Y  = 12 + DY              # top of head  → 24

_WING_ANGLES = (50, 20, -10, -40)


# ── self-contained outline (local copy so the candidate runs standalone) ─────
def _add_outline(src, outline_color=(40, 18, 30, 230)):
    """House silhouette outline: a dark 1px rim grown from the alpha mask so
    the creature reads against bright-day AND night skies."""
    mask = pygame.mask.from_surface(src)
    outline = pygame.Surface(src.get_size(), pygame.SRCALPHA)
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1),
                   (-1, -1), (1, -1), (-1, 1), (1, 1)):
        for px, py in mask.outline():
            outline.set_at((px + dx, py + dy), outline_color)
    outline.blit(src, (0, 0))
    return outline


def _make_prebuilt_skin(build_fn):
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


def _aaellipse(surf, color, center, rx, ry):
    """Filled ellipse with a 1px anti-aliased rim (matches the house helper)."""
    cx, cy = center
    rect = pygame.Rect(cx - rx, cy - ry, rx * 2, ry * 2)
    pygame.draw.ellipse(surf, color, rect)


def _flap(angle_deg):
    """0 = down-pose (gills swept back), 1 = up-pose (gills bloomed open)."""
    return (angle_deg + 40) / 90.0


# ── stubby legs shared treatment, parameterised per version ──────────────────
def _legs(surf, color, *, splay=0):
    """Two little forward limbs + two rear; they paddle out on the up-pose."""
    for fx, sgn in ((BCX - 6, -1), (BCX + 8, 1)):
        ex = fx + sgn * (2 + splay)
        pygame.draw.line(surf, color, (fx, BCY + 11), (ex, BCY + 18), 3)
        # tiny toes
        for t in (-2, 0, 2):
            pygame.draw.line(surf, color, (ex, BCY + 18),
                             (ex + t, BCY + 21), 1)


# ═════════════════════════════════════════════════════════════════════════════
# Gill helpers — each version reinterprets the frond shape, but all bloom on
# the up-pose so the flap reads as a frilled fin-stroke through water.
# ═════════════════════════════════════════════════════════════════════════════
def _feather_frond(surf, base, tip, core_col, fil_col, n=4):
    """One feathery gill stalk: a tapered core with paired filaments — the
    classic axolotl frond. `n` filament pairs along the rachis."""
    bx, by = base
    tx, ty = tip
    pygame.draw.line(surf, core_col, base, tip, 3)
    for i in range(1, n + 1):
        t = i / (n + 1)
        px = bx + (tx - bx) * t
        py = by + (ty - by) * t
        # perpendicular filaments, shrinking toward the tip
        dx, dy = (tx - bx), (ty - by)
        ln = max(1e-3, math.hypot(dx, dy))
        nx, ny = -dy / ln, dx / ln
        fl = (1 - t) * 7 + 2
        pygame.draw.line(surf, fil_col, (px, py),
                         (px + nx * fl, py + ny * fl), 2)
        pygame.draw.line(surf, fil_col, (px, py),
                         (px - nx * fl, py - ny * fl), 2)
    pygame.draw.circle(surf, fil_col, tip, 2)


# ═════════════════════════════════════════════════════════════════════════════
# 1 · CLASSIC PINK — six tidy feathery fronds fanning back, plump body, the
#     canonical pale-pink leucistic look with a tiny dot smile. The default.
# ═════════════════════════════════════════════════════════════════════════════
_AX_BODY   = (255, 200, 221)        # #FFC8DD
_AX_BODY_D = (236, 158, 188)
_AX_BODY_H = (255, 232, 240)        # #FFE8F0 belly highlight
_AX_GILL   = (255, 122, 168)        # #FF7AA8 gill core
_AX_GILL_H = (255, 176, 200)
_AX_FACE   = (90, 42, 62)           # #5A2A3E smile + eye dots


def build_axolotl_v1(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)
    bloom = f               # 0 swept back, 1 bloomed open

    # Six fronds: three each side, sweeping back (down) → out+up (up-pose).
    for sgn in (-1, 1):
        for k, spread in enumerate((-1, 0, 1)):
            base = (HCX - 2, HCY - 6)
            ang = math.radians(
                -90 + sgn * (38 + spread * 18) - (1 - bloom) * sgn * 26)
            ln = 17 - abs(spread) * 2
            tip = (base[0] + math.cos(ang) * ln,
                   base[1] + math.sin(ang) * ln * 1.05)
            _feather_frond(surf, base, tip, _AX_GILL, _AX_GILL_H, n=4)

    # Plump body.
    _aaellipse(surf, _AX_BODY_D, (BCX + 1, BCY + 1), 18, 15)
    _aaellipse(surf, _AX_BODY, (BCX, BCY), 17, 14)
    _aaellipse(surf, _AX_BODY_H, (BCX - 1, BCY + 4), 11, 8)

    # Fat tapering tail off the back.
    pygame.draw.polygon(surf, _AX_BODY_D,
                        [(BCX - 14, BCY - 4), (BCX - 26, BCY),
                         (BCX - 14, BCY + 5)])
    pygame.draw.polygon(surf, _AX_BODY,
                        [(BCX - 14, BCY - 2), (BCX - 22, BCY),
                         (BCX - 14, BCY + 3)])

    _legs(surf, _AX_BODY_D, splay=int(bloom * 3))

    # Head fused to the body (axolotls have no neck).
    _aaellipse(surf, _AX_BODY_D, (HCX, HCY + 1), 13, 12)
    _aaellipse(surf, _AX_BODY, (HCX - 1, HCY), 12, 11)
    _aaellipse(surf, _AX_BODY_H, (HCX - 2, HCY + 3), 6, 4)

    # The permanent smile: two dot eyes + a tiny upturned mouth.
    pygame.draw.circle(surf, _AX_FACE, (HCX - 1, HCY - 1), 2)
    pygame.draw.circle(surf, _AX_FACE, (HCX + 8, HCY - 1), 2)
    pygame.draw.arc(surf, _AX_FACE, (HCX - 1, HCY + 2, 9, 7),
                    math.radians(200), math.radians(340), 2)
    # Rosy cheeks.
    pygame.draw.circle(surf, _AX_GILL_H, (HCX - 3, HCY + 3), 2)
    pygame.draw.circle(surf, _AX_GILL_H, (HCX + 10, HCY + 3), 2)
    return surf


get_axolotl_v1 = _make_prebuilt_skin(build_axolotl_v1)


# ═════════════════════════════════════════════════════════════════════════════
# 2 · BUSHY CORAL — gills are dense bushy pom-pom clusters instead of tidy
#     fronds; chunkier rounder body; a slightly open happy mouth. Reads as a
#     fluffy coral halo at 40px.
# ═════════════════════════════════════════════════════════════════════════════
_BC_BODY   = (255, 190, 210)
_BC_BODY_D = (232, 146, 178)
_BC_BODY_H = (255, 228, 238)
_BC_GILL   = (255, 96, 142)
_BC_GILL_H = (255, 154, 186)
_BC_FACE   = (84, 36, 56)


def _bush(surf, cx, cy, r, core, hi):
    """A bushy gill cluster: overlapping blobs reading as a feathery pom-pom."""
    for ox, oy, rr in ((0, 0, r), (-r // 2, -1, r - 2), (r // 2, -1, r - 2),
                       (0, -r // 2, r - 2)):
        pygame.draw.circle(surf, core, (int(cx + ox), int(cy + oy)), rr)
    pygame.draw.circle(surf, hi, (int(cx - 1), int(cy - 2)), max(1, r // 2))


def build_axolotl_v2(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)
    bloom = f

    # Three bushy clusters per side; they spread apart + rise on the up-pose.
    for sgn in (-1, 1):
        for k, spread in enumerate((0, 1, 2)):
            ang = math.radians(-90 + sgn * (30 + spread * 22)
                               - (1 - bloom) * sgn * 22)
            dist = 13 + bloom * 3
            cx = HCX - 2 + math.cos(ang) * dist
            cy = HCY - 6 + math.sin(ang) * dist
            _bush(surf, cx, cy, 5 - spread // 2, _BC_GILL, _BC_GILL_H)

    # Chunkier rounder body.
    _aaellipse(surf, _BC_BODY_D, (BCX + 1, BCY + 1), 19, 17)
    _aaellipse(surf, _BC_BODY, (BCX, BCY), 18, 16)
    _aaellipse(surf, _BC_BODY_H, (BCX - 1, BCY + 4), 12, 9)

    pygame.draw.polygon(surf, _BC_BODY_D,
                        [(BCX - 15, BCY - 5), (BCX - 27, BCY + 1),
                         (BCX - 15, BCY + 6)])
    pygame.draw.polygon(surf, _BC_BODY,
                        [(BCX - 15, BCY - 3), (BCX - 23, BCY + 1),
                         (BCX - 15, BCY + 4)])

    _legs(surf, _BC_BODY_D, splay=int(bloom * 3))

    _aaellipse(surf, _BC_BODY_D, (HCX, HCY + 1), 14, 13)
    _aaellipse(surf, _BC_BODY, (HCX - 1, HCY), 13, 12)
    _aaellipse(surf, _BC_BODY_H, (HCX - 2, HCY + 3), 7, 5)

    # Big happy open mouth.
    pygame.draw.circle(surf, _BC_FACE, (HCX - 2, HCY - 1), 2)
    pygame.draw.circle(surf, _BC_FACE, (HCX + 8, HCY - 1), 2)
    pygame.draw.ellipse(surf, _BC_FACE, (HCX, HCY + 4, 8, 5))
    pygame.draw.circle(surf, (255, 120, 150), (HCX + 4, HCY + 6), 2)  # tongue
    pygame.draw.circle(surf, _BC_GILL_H, (HCX - 4, HCY + 3), 3)
    pygame.draw.circle(surf, _BC_GILL_H, (HCX + 11, HCY + 3), 3)
    return surf


get_axolotl_v2 = _make_prebuilt_skin(build_axolotl_v2)


# ═════════════════════════════════════════════════════════════════════════════
# 3 · ANTLER LEUCISTIC — gills branch like bold ANTLERS (forking stalks) rather
#     than soft feathers; a crisp white/cream leucistic morph with a wide grin.
#     The branching antler-crown is the strongest "headdress" silhouette.
# ═════════════════════════════════════════════════════════════════════════════
_AL_BODY   = (248, 240, 244)        # leucistic near-white
_AL_BODY_D = (212, 198, 210)
_AL_BODY_H = (255, 255, 255)
_AL_GILL   = (255, 110, 150)
_AL_GILL_H = (255, 168, 192)
_AL_FACE   = (74, 40, 56)


def _antler(surf, base, ang, length, depth, core, hi):
    """A forking antler-gill: a stalk that splits into two tined branches,
    recursively, for a bold branching crown."""
    bx, by = base
    tx = bx + math.cos(ang) * length
    ty = by + math.sin(ang) * length
    pygame.draw.line(surf, core, (bx, by), (tx, ty), max(2, depth))
    if depth <= 1:
        pygame.draw.circle(surf, hi, (int(tx), int(ty)), 2)
        return
    for da in (-0.5, 0.5):
        _antler(surf, (tx, ty), ang + da, length * 0.7, depth - 1, core, hi)


def build_axolotl_v3(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)
    bloom = f

    # Three antler-stalks per side; spread wider on the up-pose.
    for sgn in (-1, 1):
        for spread in (-1, 0, 1):
            ang = math.radians(-90 + sgn * (32 + spread * 20)
                               - (1 - bloom) * sgn * 24)
            _antler(surf, (HCX - 2, HCY - 7), ang, 9 + (1 - abs(spread)) * 2,
                    3, _AL_GILL, _AL_GILL_H)

    _aaellipse(surf, _AL_BODY_D, (BCX + 1, BCY + 1), 18, 15)
    _aaellipse(surf, _AL_BODY, (BCX, BCY), 17, 14)
    _aaellipse(surf, _AL_BODY_H, (BCX - 1, BCY + 4), 11, 8)

    pygame.draw.polygon(surf, _AL_BODY_D,
                        [(BCX - 14, BCY - 4), (BCX - 26, BCY),
                         (BCX - 14, BCY + 5)])
    pygame.draw.polygon(surf, _AL_BODY,
                        [(BCX - 14, BCY - 2), (BCX - 22, BCY),
                         (BCX - 14, BCY + 3)])

    _legs(surf, _AL_BODY_D, splay=int(bloom * 3))

    _aaellipse(surf, _AL_BODY_D, (HCX, HCY + 1), 13, 12)
    _aaellipse(surf, _AL_BODY, (HCX - 1, HCY), 12, 11)
    _aaellipse(surf, _AL_BODY_H, (HCX - 2, HCY + 3), 6, 4)

    # Wide cheerful grin.
    pygame.draw.circle(surf, _AL_FACE, (HCX - 1, HCY - 1), 2)
    pygame.draw.circle(surf, _AL_FACE, (HCX + 8, HCY - 1), 2)
    pygame.draw.arc(surf, _AL_FACE, (HCX - 3, HCY + 1, 13, 9),
                    math.radians(195), math.radians(345), 3)
    pygame.draw.circle(surf, _AL_GILL_H, (HCX - 3, HCY + 4), 2)
    pygame.draw.circle(surf, _AL_GILL_H, (HCX + 10, HCY + 4), 2)
    return surf


get_axolotl_v3 = _make_prebuilt_skin(build_axolotl_v3)


# ═════════════════════════════════════════════════════════════════════════════
# 4 · MELANOID DARK — a dark slate/charcoal morph where the contrast is carried
#     entirely by GLOWING magenta gill cores + bright eyes against the night-
#     reading dark body. The "stealth" axolotl: silhouette + neon frill.
# ═════════════════════════════════════════════════════════════════════════════
_MD_BODY   = (78, 64, 92)           # desaturated dark plum
_MD_BODY_D = (52, 42, 66)
_MD_BODY_H = (118, 100, 138)
_MD_GILL   = (255, 64, 150)         # neon magenta core
_MD_GILL_H = (255, 150, 210)
_MD_GLOW   = (255, 96, 170)
_MD_FACE   = (250, 244, 250)        # bright eyes pop on the dark face


def build_axolotl_v4(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)
    bloom = f

    # Soft glow halo behind the gills (additive-ish, low alpha).
    glow = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    _aaellipse(glow, (*_MD_GLOW, 60), (HCX - 1, HCY - 8), 18, 16)
    surf.blit(glow, (0, 0))

    # Six bright fronds; on the dark body they are the whole signature.
    for sgn in (-1, 1):
        for spread in (-1, 0, 1):
            base = (HCX - 2, HCY - 6)
            ang = math.radians(-90 + sgn * (36 + spread * 18)
                               - (1 - bloom) * sgn * 26)
            ln = 17 - abs(spread) * 2
            tip = (base[0] + math.cos(ang) * ln,
                   base[1] + math.sin(ang) * ln * 1.05)
            _feather_frond(surf, base, tip, _MD_GILL, _MD_GILL_H, n=4)

    _aaellipse(surf, _MD_BODY_D, (BCX + 1, BCY + 1), 18, 15)
    _aaellipse(surf, _MD_BODY, (BCX, BCY), 17, 14)
    _aaellipse(surf, _MD_BODY_H, (BCX - 2, BCY - 2), 8, 5)

    pygame.draw.polygon(surf, _MD_BODY_D,
                        [(BCX - 14, BCY - 4), (BCX - 26, BCY),
                         (BCX - 14, BCY + 5)])
    pygame.draw.polygon(surf, _MD_BODY,
                        [(BCX - 14, BCY - 2), (BCX - 22, BCY),
                         (BCX - 14, BCY + 3)])

    _legs(surf, _MD_BODY_D, splay=int(bloom * 3))

    _aaellipse(surf, _MD_BODY_D, (HCX, HCY + 1), 13, 12)
    _aaellipse(surf, _MD_BODY, (HCX - 1, HCY), 12, 11)
    _aaellipse(surf, _MD_BODY_H, (HCX - 3, HCY - 2), 5, 3)

    # Big bright eyes carry the read on the dark face.
    for ex in (HCX - 1, HCX + 8):
        pygame.draw.circle(surf, _MD_FACE, (ex, HCY - 1), 3)
        pygame.draw.circle(surf, (30, 24, 40), (ex + 1, HCY - 1), 1)
    pygame.draw.arc(surf, _MD_GILL_H, (HCX - 1, HCY + 2, 9, 7),
                    math.radians(200), math.radians(340), 2)
    return surf


get_axolotl_v4 = _make_prebuilt_skin(build_axolotl_v4)


# ═════════════════════════════════════════════════════════════════════════════
# 5 · GOLDEN GILD — a golden-albino morph: warm gold body with reflective
#     iridophore sparkles, and the gills drawn as a SWEPT FEATHER-FAN (a single
#     broad fan per side, like a fin) rather than discrete stalks. Premium glow.
# ═════════════════════════════════════════════════════════════════════════════
_GG_BODY   = (255, 214, 120)        # warm gold
_GG_BODY_D = (228, 168, 70)
_GG_BODY_H = (255, 244, 196)
_GG_GILL   = (255, 150, 96)         # coral-orange fan
_GG_GILL_D = (228, 110, 70)
_GG_GILL_H = (255, 206, 150)
_GG_FACE   = (90, 54, 30)


def _fan(surf, cx, cy, ang0, spread, n, length, core, dark, hi):
    """A broad swept feather-fan: n fronds radiating through `spread` radians
    around `ang0`, drawn dark→core→highlight for a finny ridge."""
    for col, off in ((dark, 1.0), (core, 0.85), (hi, 0.5)):
        for i in range(n):
            t = i / (n - 1) - 0.5
            ang = ang0 + t * spread
            ln = length * off * (1 - abs(t) * 0.3)
            tx = cx + math.cos(ang) * ln
            ty = cy + math.sin(ang) * ln
            pygame.draw.line(surf, col, (cx, cy), (tx, ty),
                             3 if off > 0.9 else 2)


def build_axolotl_v5(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)
    bloom = f

    # One broad fan per side; the fan's spread WIDENS on the up-pose (bloom).
    spread = math.radians(46 + bloom * 26)
    for sgn in (-1, 1):
        ang0 = math.radians(-90 + sgn * (30 - (1 - bloom) * 16))
        _fan(surf, HCX - 2, HCY - 6, ang0, spread, 4, 17,
             _GG_GILL, _GG_GILL_D, _GG_GILL_H)

    _aaellipse(surf, _GG_BODY_D, (BCX + 1, BCY + 1), 18, 15)
    _aaellipse(surf, _GG_BODY, (BCX, BCY), 17, 14)
    _aaellipse(surf, _GG_BODY_H, (BCX - 1, BCY + 4), 11, 8)
    # Iridophore sparkles — the gold-morph tell.
    for sx, sy in ((26, 46), (34, 50), (38, 42), (22, 44), (30, 54)):
        pygame.draw.circle(surf, _GG_BODY_H, (sx, sy), 1)

    pygame.draw.polygon(surf, _GG_BODY_D,
                        [(BCX - 14, BCY - 4), (BCX - 26, BCY),
                         (BCX - 14, BCY + 5)])
    pygame.draw.polygon(surf, _GG_BODY,
                        [(BCX - 14, BCY - 2), (BCX - 22, BCY),
                         (BCX - 14, BCY + 3)])

    _legs(surf, _GG_BODY_D, splay=int(bloom * 3))

    _aaellipse(surf, _GG_BODY_D, (HCX, HCY + 1), 13, 12)
    _aaellipse(surf, _GG_BODY, (HCX - 1, HCY), 12, 11)
    _aaellipse(surf, _GG_BODY_H, (HCX - 2, HCY + 3), 6, 4)

    pygame.draw.circle(surf, _GG_FACE, (HCX - 1, HCY - 1), 2)
    pygame.draw.circle(surf, _GG_FACE, (HCX + 8, HCY - 1), 2)
    # glint in each eye for the reflective gold morph
    pygame.draw.circle(surf, (255, 255, 240), (HCX - 2, HCY - 2), 1)
    pygame.draw.circle(surf, (255, 255, 240), (HCX + 7, HCY - 2), 1)
    pygame.draw.arc(surf, _GG_FACE, (HCX - 1, HCY + 2, 9, 7),
                    math.radians(200), math.radians(340), 2)
    pygame.draw.circle(surf, _GG_GILL_H, (HCX - 3, HCY + 3), 2)
    pygame.draw.circle(surf, _GG_GILL_H, (HCX + 10, HCY + 3), 2)
    return surf


get_axolotl_v5 = _make_prebuilt_skin(build_axolotl_v5)


# ── label → getter (for the review sheet) ────────────────────────────────────
VARIANTS = {
    "v1 CLASSIC PINK":     get_axolotl_v1,
    "v2 BUSHY CORAL":      get_axolotl_v2,
    "v3 ANTLER LEUCISTIC": get_axolotl_v3,
    "v4 MELANOID DARK":    get_axolotl_v4,
    "v5 GOLDEN GILD":      get_axolotl_v5,
}

FEATURES = {
    "v1 CLASSIC PINK":     "6 feathery fronds + dot smile",
    "v2 BUSHY CORAL":      "bushy pom-pom gill halo + open grin",
    "v3 ANTLER LEUCISTIC": "branching antler crown + wide grin",
    "v4 MELANOID DARK":    "neon magenta frill on dark body",
    "v5 GOLDEN GILD":      "swept gold feather-fan + sparkles",
}
