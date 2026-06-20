"""Candidate GRIFFIN skin — round-1 exploration (5 distinct takes).

The griffin tops the late-game ANIMALS tier: an eagle-headed forebody fused to
a tawny lion hindquarter with a tufted tail. The whole job is to read as a
MYTHIC HYBRID at 40px in motion — and to read CLEARLY DISTINCT from the plain
bald-eagle skin that already ships. The eagle alone is "white head + hooked
beak"; the griffin must add the second material: a furred lion rear, a tufted
lion tail, and a visible feather→fur split line. That two-tone material split
IS the 40px tell.

Contract mirrors game/animal_skins.py so the winner lifts straight in:

  * `build_<name>(wing_angle_deg) -> pygame.Surface`  one flat 64×84 frame.
  * a cached `(frame_idx, tilt_deg) -> Surface` getter from
    `_make_prebuilt_skin(build_fn)`.
  * `BUILDERS = {"skin_griffin_v1": ..., ...}` registry at the bottom.

Body mass stays centred at (32,44); head near (44,34); collision is a fixed
14px circle at the body centre, so every variant keeps its lion body anchored
there — the wings/head/tail break the silhouette around that fixed mass.
"""
import math
import pygame

from game import parrot
from game.parrot import (
    SPRITE_W, SPRITE_H, _WING_ANGLES, _add_outline, _aaellipse,
)


# ── tall-canvas constants (headroom for ear-tufts + upswept wings) ───────────
COMPOSITE_W = SPRITE_W          # 64
COMPOSITE_H = 84                # headroom for tufts / raised wings
DY          = 12                # body offset down into the tall canvas

BCX, BCY = 32, 32 + DY          # body centre  → (32, 44)
HCX, HCY = 44, 22 + DY          # head centre  → (44, 34)
CROWN_Y  = 12 + DY              # top of head  → 24


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


# ── tiny shared helpers ──────────────────────────────────────────────────────
def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _flap(angle_deg):
    """0..1 'wing is up' factor. _WING_ANGLES runs 50→-40 (down→up)."""
    return (angle_deg + 40) / 90.0


def _rot_blit(surf, wing, anchor):
    surf.blit(wing, wing.get_rect(center=anchor).topleft)


# Shared griffin palette (varied per-variant where noted).
FUR        = (232, 194, 74)         # #E8C24A tawny lion fur
FUR_D      = (190, 150, 46)
FUR_H      = (250, 224, 132)
WING       = (138, 90, 30)          # #8A5A1E wing feathers
WING_D     = (96, 60, 18)
WING_H     = (186, 132, 64)
HEAD       = (244, 228, 184)        # #F4E4B8 head feathers (pale)
HEAD_WHITE = (248, 248, 244)        # bald-eagle-style white head (some vers.)
HEAD_D     = (208, 188, 138)
BEAK       = (255, 198, 56)         # gold raptor beak
BEAK_D     = (200, 142, 24)
DARK       = (58, 42, 18)           # #3A2A12 beak detail + eye
RIM        = (201, 162, 58)         # #C9A23A rim


# ═════════════════════════════════════════════════════════════════════════════
# Shared raptor wing builder — feathered eagle wing with splayed primaries.
# The wing is the griffin's flight engine; variants pass different proportions.
# ═════════════════════════════════════════════════════════════════════════════
def _griffin_wing(angle_deg, *, span=48, primaries=True, tip_col=WING_D,
                  body_col=WING, hi_col=WING_H):
    w = pygame.Surface((span + 4, 46), pygame.SRCALPHA)
    s = span / 48.0
    pts = [(22, 24), (int(20 + 26 * s), 12), (int(22 + 26 * s), 24),
           (28, 38), (14, 32)]
    pygame.draw.polygon(w, WING_D, pts)
    pygame.draw.polygon(w, body_col,
                        [(22, 24), (int(20 + 24 * s), 14),
                         (int(20 + 24 * s), 26), (24, 34)])
    if primaries:
        for i, (tx, ty) in enumerate(((int(20 + 24 * s), 14),
                                      (int(22 + 25 * s), 19),
                                      (int(20 + 24 * s), 25))):
            pygame.draw.polygon(w, tip_col,
                                [(tx - 4, ty), (tx + 3, ty - 1), (tx - 2, ty + 4)])
    pygame.draw.line(w, hi_col, (23, 25), (int(18 + 24 * s), 17), 1)
    pygame.draw.line(w, hi_col, (24, 30), (int(16 + 22 * s), 24), 1)
    return pygame.transform.rotate(w, angle_deg)


def _tail_tuft(surf, x, y, size, fur, fur_d, tuft_col):
    """Lion tail: a thin furred whip ending in a dark bushy tuft. The tuft is
    the chimera's back-end tell, so it must be a chunky blob that survives 40px."""
    pygame.draw.line(surf, fur_d, (x + 6, y - 2), (x - 4, y + size), 3)
    pygame.draw.line(surf, fur, (x + 6, y - 2), (x - 4, y + size), 2)
    # Bushy tuft — a clutch of short strokes radiating from the tip.
    tx, ty = x - 4, y + size
    pygame.draw.circle(surf, tuft_col, (tx, ty), max(3, size // 4))
    for ang in (-50, -20, 15, 45, 80):
        ex = tx + int(math.cos(math.radians(ang + 200)) * (size // 3 + 3))
        ey = ty + int(math.sin(math.radians(ang + 200)) * (size // 3 + 3))
        pygame.draw.line(surf, tuft_col, (tx, ty), (ex, ey), 2)


def _ear_tufts(surf, hx, crown, fur, fur_d):
    """Two small feather/fur ear-tufts breaking the crown — a griffin grace
    note, kept short so the beak stays the dominant head read."""
    for sgn, ex in ((-1, hx - 6), (1, hx + 5)):
        pygame.draw.polygon(surf, fur_d,
                            [(ex, crown + 5), (ex + sgn * 2, crown - 4),
                             (ex + sgn * 4, crown + 4)])
        pygame.draw.line(surf, fur, (ex + sgn * 1, crown + 4),
                         (ex + sgn * 2, crown - 3), 1)


def _hooked_beak(surf, hx, hy, *, length=14):
    """Gold hooked raptor beak — the front-end eagle tell."""
    pygame.draw.polygon(surf, BEAK,
                        [(hx + 4, hy - 2), (hx + length, hy + 1),
                         (hx + length - 2, hy + 6), (hx + 4, hy + 5)])
    pygame.draw.polygon(surf, BEAK_D,
                        [(hx + length - 3, hy + 3), (hx + length, hy + 1),
                         (hx + length - 3, hy + 8)])
    pygame.draw.polygon(surf, DARK,
                        [(hx + 4, hy - 2), (hx + length, hy + 1),
                         (hx + length - 2, hy + 6), (hx + 4, hy + 5)], 1)
    pygame.draw.line(surf, (255, 235, 160), (hx + 5, hy), (hx + length - 3, hy + 2), 1)


def _raptor_eye(surf, hx, hy, *, brow=True, brow_col=None, fierce=True):
    if brow:
        bc = brow_col if brow_col else (150, 110, 40)
        if fierce:
            pygame.draw.polygon(surf, bc,
                                [(hx - 6, hy - 4), (hx + 6, hy - 6),
                                 (hx + 6, hy - 3), (hx - 5, hy - 1)])
        else:
            pygame.draw.line(surf, bc, (hx - 5, hy - 4), (hx + 6, hy - 5), 2)
    pygame.draw.circle(surf, (255, 220, 120), (hx + 2, hy - 1), 4)
    pygame.draw.circle(surf, DARK, (hx + 3, hy - 1), 2)
    pygame.draw.circle(surf, (255, 255, 255), (hx + 1, hy - 2), 1)


# ═════════════════════════════════════════════════════════════════════════════
# V1 · HERALDIC REGAL — white eagle head, a CLEAN diagonal feather→fur split
#     across the body, modest ear-tufts, a large tufted lion tail. The textbook
#     griffin. 40px tell: pale-head + white wing band over a tawny lion rear,
#     split by a crisp diagonal seam.
# ═════════════════════════════════════════════════════════════════════════════
def build_griffin_v1(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)

    # Far wing behind, damped.
    _rot_blit(surf, _griffin_wing(wing_angle_deg * 0.5 - 16, span=46),
              (BCX + 9, BCY - 2))

    # ── Lion hindquarter (tawny fur) — the body mass, anchored at centre. ──
    _aaellipse(surf, FUR_D, (BCX + 1, BCY + 1), 18, 16)
    _aaellipse(surf, FUR, (BCX, BCY), 17, 15)
    # Haunch swirl on the rear (lion thigh).
    _aaellipse(surf, FUR_H, (BCX - 8, BCY + 2), 7, 8)
    pygame.draw.arc(surf, FUR_D, (BCX - 14, BCY - 6, 16, 18),
                    math.radians(40), math.radians(220), 2)

    # ── Feathered eagle forebody — pale, over the front half of the body. ──
    # The crisp diagonal seam is the material split (the chimera tell).
    chest = [(BCX + 2, BCY - 15), (BCX + 18, BCY - 8), (BCX + 17, BCY + 12),
             (BCX - 2, BCY + 14), (BCX - 6, BCY - 2)]
    pygame.draw.polygon(surf, HEAD_D, chest)
    pygame.draw.polygon(surf, HEAD_WHITE,
                        [(BCX + 2, BCY - 13), (BCX + 16, BCY - 7),
                         (BCX + 15, BCY + 8), (BCX - 2, BCY + 8)])
    # Scalloped feather seam.
    for sy in (BCY - 6, BCY, BCY + 6):
        pygame.draw.line(surf, HEAD_D, (BCX - 5, sy - 2), (BCX + 2, sy), 1)

    # Lion tufted tail sweeping out the rear-low.
    _tail_tuft(surf, 14, BCY + 4, 14, FUR, FUR_D, WING_D)

    # ── White eagle head ──
    _aaellipse(surf, HEAD_D, (HCX, HCY + 1), 12, 12)
    _aaellipse(surf, HEAD_WHITE, (HCX - 1, HCY), 11, 11)
    _ear_tufts(surf, HCX, CROWN_Y, HEAD, HEAD_D)
    _raptor_eye(surf, HCX, HCY, fierce=True)
    _hooked_beak(surf, HCX, HCY, length=15)

    # Near wing — the hero raptor wing.
    _rot_blit(surf, _griffin_wing(wing_angle_deg, span=48), (BCX - 5, BCY))

    # Lion fore-paw (front leg, furred).
    for fx in (28, 37):
        pygame.draw.line(surf, FUR_D, (fx, BCY + 14), (fx, BCY + 18), 2)
        pygame.draw.circle(surf, BEAK_D, (fx, BCY + 18), 1)
    return surf


# ═════════════════════════════════════════════════════════════════════════════
# V2 · FIERCE GOLDEN RAPTOR — golden head (NO white), heavy angled brow, a wide
#     aggressive open wing-span, a tighter compact lion body, a smaller flicking
#     tail tuft. 40px tell: all-gold raptor front over a darker tawny rear with
#     splayed open wings — pure predator.
# ═════════════════════════════════════════════════════════════════════════════
_V2_FUR    = (214, 168, 56)
_V2_FUR_D  = (168, 124, 36)
_V2_HEAD   = (246, 214, 110)        # rich gold head feathers
_V2_HEAD_D = (210, 168, 64)


def build_griffin_v2(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)
    spread = (f - 0.5) * 18          # wings beat WIDE on the powerful upstroke

    # Far wing — wide span, opens with the flap.
    _rot_blit(surf, _griffin_wing(wing_angle_deg * 0.6 + spread - 14, span=52),
              (BCX + 11, BCY - 3))

    # Compact lion body (tighter than v1 so the wings dominate).
    _aaellipse(surf, _V2_FUR_D, (BCX + 1, BCY + 1), 16, 14)
    _aaellipse(surf, _V2_FUR, (BCX, BCY), 15, 13)
    _aaellipse(surf, FUR_H, (BCX - 7, BCY + 1), 6, 7)

    # Feathered chest patch — gold over the front, soft seam.
    pygame.draw.polygon(surf, _V2_HEAD_D,
                        [(BCX + 2, BCY - 12), (BCX + 16, BCY - 6),
                         (BCX + 15, BCY + 10), (BCX - 2, BCY + 11), (BCX - 4, BCY - 2)])
    pygame.draw.polygon(surf, _V2_HEAD,
                        [(BCX + 3, BCY - 10), (BCX + 14, BCY - 5),
                         (BCX + 13, BCY + 6), (BCX, BCY + 7)])

    # Small flicking lion tail tuft (smaller than v1).
    _tail_tuft(surf, 16, BCY + 2, 10, _V2_FUR, _V2_FUR_D, WING_D)

    # ── Golden eagle head with a fierce heavy brow ──
    _aaellipse(surf, _V2_HEAD_D, (HCX, HCY + 1), 12, 12)
    _aaellipse(surf, _V2_HEAD, (HCX - 1, HCY), 11, 11)
    # Crown feather flecks for the gold head.
    for fx, fy in ((HCX - 4, HCY - 6), (HCX, HCY - 7), (HCX + 4, HCY - 6)):
        pygame.draw.line(surf, _V2_HEAD_D, (fx, fy), (fx, fy + 3), 1)
    _ear_tufts(surf, HCX, CROWN_Y, _V2_HEAD, _V2_HEAD_D)
    _raptor_eye(surf, HCX, HCY, brow_col=(120, 80, 24), fierce=True)
    _hooked_beak(surf, HCX, HCY, length=16)

    # Near wing — the hero, opens wide on the flap.
    _rot_blit(surf, _griffin_wing(wing_angle_deg - spread, span=54),
              (BCX - 6, BCY))

    for fx in (28, 37):
        pygame.draw.line(surf, _V2_FUR_D, (fx, BCY + 13), (fx, BCY + 17), 2)
        pygame.draw.circle(surf, BEAK_D, (fx, BCY + 17), 1)
    return surf


# ═════════════════════════════════════════════════════════════════════════════
# V3 · MANED TWO-TONE STACK — a BOLD near-vertical split: pale feathered front
#     half / tawny furred rear half, joined by a dark LION MANE ruff at the neck.
#     White head, big bushy upcurling tail. 40px tell: the vertical feather|fur
#     seam + the mane ruff collar where eagle meets lion.
# ═════════════════════════════════════════════════════════════════════════════
_V3_MANE   = (150, 96, 30)          # darker mane ruff
_V3_MANE_D = (110, 68, 18)


def build_griffin_v3(wing_angle_deg):
    surf = _new()

    _rot_blit(surf, _griffin_wing(wing_angle_deg * 0.5 - 16, span=46),
              (BCX + 9, BCY - 2))

    # Lion rear (left) tawny fur.
    _aaellipse(surf, FUR_D, (BCX + 1, BCY + 1), 18, 16)
    _aaellipse(surf, FUR, (BCX, BCY), 17, 15)
    _aaellipse(surf, FUR_H, (BCX - 9, BCY + 1), 7, 8)

    # Feathered front (right) — pale, a near-vertical seam down the middle.
    pygame.draw.polygon(surf, HEAD_D,
                        [(BCX, BCY - 16), (BCX + 18, BCY - 9),
                         (BCX + 18, BCY + 13), (BCX + 1, BCY + 15)])
    pygame.draw.polygon(surf, HEAD_WHITE,
                        [(BCX + 2, BCY - 13), (BCX + 16, BCY - 7),
                         (BCX + 16, BCY + 10), (BCX + 3, BCY + 11)])
    # Vertical seam feather ticks.
    for sy in (BCY - 8, BCY - 2, BCY + 4, BCY + 10):
        pygame.draw.line(surf, HEAD_D, (BCX, sy), (BCX + 3, sy + 1), 1)

    # ── HERO collar: a dark LION MANE ruff at the neck join (eagle→lion). ──
    mane_cx, mane_cy = BCX + 5, BCY - 10
    for ang in range(-60, 130, 22):
        ex = mane_cx + int(math.cos(math.radians(ang)) * 11)
        ey = mane_cy + int(math.sin(math.radians(ang)) * 10)
        pygame.draw.line(surf, _V3_MANE_D, (mane_cx, mane_cy), (ex, ey), 3)
    for ang in range(-60, 130, 22):
        ex = mane_cx + int(math.cos(math.radians(ang)) * 9)
        ey = mane_cy + int(math.sin(math.radians(ang)) * 8)
        pygame.draw.line(surf, _V3_MANE, (mane_cx, mane_cy), (ex, ey), 2)
    _aaellipse(surf, _V3_MANE, (mane_cx, mane_cy), 5, 5)

    # Big bushy tail curling UP behind the lion rear.
    _tail_tuft(surf, 13, BCY - 2, 16, FUR, FUR_D, _V3_MANE_D)

    # White eagle head sitting above the mane.
    _aaellipse(surf, HEAD_D, (HCX, HCY + 1), 11, 11)
    _aaellipse(surf, HEAD_WHITE, (HCX - 1, HCY), 10, 10)
    _ear_tufts(surf, HCX, CROWN_Y, HEAD, HEAD_D)
    _raptor_eye(surf, HCX, HCY, fierce=False)
    _hooked_beak(surf, HCX, HCY, length=14)

    _rot_blit(surf, _griffin_wing(wing_angle_deg, span=48), (BCX - 5, BCY))

    for fx in (28, 37):
        pygame.draw.line(surf, FUR_D, (fx, BCY + 14), (fx, BCY + 18), 2)
    return surf


# ═════════════════════════════════════════════════════════════════════════════
# V4 · SOARING WIDE-WING — the flight read: ENORMOUS swept eagle wings dominate,
#     a compact lion rear tucked beneath, white head thrust forward. The flap is
#     a big slow raptor cadence (wings sweep from deep-down to high-up); the
#     tail-tuft flicks on the up-pose. 40px tell: huge wingspan + the tucked
#     two-tone body between them.
# ═════════════════════════════════════════════════════════════════════════════
def build_griffin_v4(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)
    # Big symmetric raptor beat: both wings swing through a wide arc.
    beat = (f - 0.5) * 30

    # Far wing — huge, sweeps opposite for depth.
    _rot_blit(surf, _griffin_wing(28 + beat, span=58), (BCX + 14, BCY - 5))

    # Compact lion body tucked low between the wings.
    _aaellipse(surf, FUR_D, (BCX + 1, BCY + 2), 15, 13)
    _aaellipse(surf, FUR, (BCX, BCY + 1), 14, 12)
    _aaellipse(surf, FUR_H, (BCX - 7, BCY + 2), 6, 6)

    # Feathered front patch — pale, diagonal seam.
    pygame.draw.polygon(surf, HEAD_D,
                        [(BCX + 2, BCY - 10), (BCX + 15, BCY - 4),
                         (BCX + 14, BCY + 9), (BCX - 1, BCY + 11), (BCX - 3, BCY)])
    pygame.draw.polygon(surf, HEAD_WHITE,
                        [(BCX + 3, BCY - 8), (BCX + 13, BCY - 3),
                         (BCX + 12, BCY + 5), (BCX + 1, BCY + 6)])

    # Tail tuft flicks UP harder on the up-pose (f→1).
    flick = int(f * 6)
    _tail_tuft(surf, 14, BCY + 2 - flick, 12, FUR, FUR_D, WING_D)

    # White eagle head thrust forward.
    _aaellipse(surf, HEAD_D, (HCX, HCY + 1), 11, 11)
    _aaellipse(surf, HEAD_WHITE, (HCX - 1, HCY), 10, 10)
    _ear_tufts(surf, HCX, CROWN_Y, HEAD, HEAD_D)
    _raptor_eye(surf, HCX, HCY, fierce=True)
    _hooked_beak(surf, HCX, HCY, length=15)

    # Near wing — the hero, enormous, swings through the big beat.
    _rot_blit(surf, _griffin_wing(-28 - beat, span=60), (BCX - 10, BCY))

    for fx in (29, 37):
        pygame.draw.line(surf, FUR_D, (fx, BCY + 12), (fx, BCY + 16), 2)
    return surf


# ═════════════════════════════════════════════════════════════════════════════
# V5 · CUB CHIBI GRIFFIN — round, friendly, casual-arcade charm: a big-headed
#     warm-gold cub with fluffy pale head feathers, tiny round ear-tufts, a
#     short stubby beak, and an OVERSIZED fluffy tail tuft. The split is soft
#     (feather front / fur rear) but the silhouette is cute. 40px tell: big pale
#     head + giant fluffy tuft on a round golden body.
# ═════════════════════════════════════════════════════════════════════════════
_V5_FUR    = (244, 206, 96)         # warm bright cub gold
_V5_FUR_D  = (206, 162, 56)
_V5_FUR_H  = (255, 234, 156)
_V5_HEAD   = (250, 238, 204)        # creamy fluffy head


def build_griffin_v5(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)

    _rot_blit(surf, _griffin_wing(wing_angle_deg * 0.5 - 14, span=44,
                                  body_col=(170, 120, 50), hi_col=(214, 168, 92)),
              (BCX + 8, BCY - 1))

    # Plump round cub body.
    _aaellipse(surf, _V5_FUR_D, (BCX + 1, BCY + 1), 17, 16)
    _aaellipse(surf, _V5_FUR, (BCX, BCY), 16, 15)
    _aaellipse(surf, _V5_FUR_H, (BCX - 5, BCY - 3), 8, 6)

    # Soft fluffy feathered belly patch (front), creamy.
    _aaellipse(surf, _V5_HEAD, (BCX + 6, BCY + 2), 9, 10)
    for sy in (BCY - 4, BCY + 2, BCY + 8):
        pygame.draw.line(surf, HEAD_D, (BCX - 2, sy), (BCX + 1, sy + 1), 1)

    # OVERSIZED fluffy tail tuft — the cute back-end signature.
    bob = int(f * 4)
    tx, ty = 12, BCY + 2 - bob
    pygame.draw.line(surf, _V5_FUR_D, (BCX - 13, BCY + 2), (tx, ty), 3)
    pygame.draw.circle(surf, _V5_FUR_D, (tx, ty), 8)
    pygame.draw.circle(surf, _V5_FUR, (tx, ty), 6)
    pygame.draw.circle(surf, _V5_FUR_H, (tx - 2, ty - 2), 3)

    # Big friendly head.
    _aaellipse(surf, HEAD_D, (HCX, HCY + 1), 13, 13)
    _aaellipse(surf, _V5_HEAD, (HCX - 1, HCY), 12, 12)
    # Tiny round ear-tufts.
    for sgn, ex in ((-1, HCX - 7), (1, HCX + 6)):
        pygame.draw.circle(surf, HEAD_D, (ex, CROWN_Y + 2), 3)
        pygame.draw.circle(surf, _V5_HEAD, (ex - sgn, CROWN_Y + 1), 2)
    # Big friendly eyes (cute, not fierce).
    pygame.draw.circle(surf, (255, 255, 255), (HCX, HCY - 1), 5)
    pygame.draw.circle(surf, DARK, (HCX + 1, HCY - 1), 3)
    pygame.draw.circle(surf, (255, 255, 255), (HCX - 1, HCY - 2), 1)
    # Short stubby gold beak.
    pygame.draw.polygon(surf, BEAK,
                        [(HCX + 5, HCY + 2), (HCX + 12, HCY + 4),
                         (HCX + 9, HCY + 8), (HCX + 5, HCY + 6)])
    pygame.draw.polygon(surf, BEAK_D,
                        [(HCX + 9, HCY + 4), (HCX + 12, HCY + 4),
                         (HCX + 9, HCY + 8)])
    pygame.draw.polygon(surf, DARK,
                        [(HCX + 5, HCY + 2), (HCX + 12, HCY + 4),
                         (HCX + 9, HCY + 8), (HCX + 5, HCY + 6)], 1)

    _rot_blit(surf, _griffin_wing(wing_angle_deg, span=46,
                                  body_col=(190, 138, 60), hi_col=(238, 196, 120)),
              (BCX - 4, BCY))

    for fx in (29, 37):
        pygame.draw.line(surf, _V5_FUR_D, (fx, BCY + 15), (fx, BCY + 19), 2)
    return surf


# ─────────────────────────────────────────────────────────────────────────────
BUILDERS = {
    "skin_griffin_v1": _make_prebuilt_skin(build_griffin_v1),
    "skin_griffin_v2": _make_prebuilt_skin(build_griffin_v2),
    "skin_griffin_v3": _make_prebuilt_skin(build_griffin_v3),
    "skin_griffin_v4": _make_prebuilt_skin(build_griffin_v4),
    "skin_griffin_v5": _make_prebuilt_skin(build_griffin_v5),
}
