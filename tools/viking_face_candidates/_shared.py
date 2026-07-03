"""Shared base for the Viking FACE + HELD-AXE redesign exploration.

The plain-Viking palettes v1 IRONCLAD (brown) and v2 BLOODAXE (rust-red) are
already SHIP-READY for everything EXCEPT the face and the axe. This module
factors those two builders so a design only has to supply:

    paint_face(surf, wing_angle, P)   # the parrot's Viking face: eye + mustache
                                       # + beard (read clearly as a face)
    paint_axe(surf, wing_angle, P)    # a clearly-HELD bearded axe

and `make_build(paint_face, paint_axe, P)` renders it in either palette. The
frozen base costume (horned spangenhelm, nasal, fur ruff, back round shield,
boot cuffs, body recolour, dark keyline) is reproduced verbatim from v1/v2.

Draw order per frame: back (shield + fur) -> front (helm + boots) ->
paint_face (drawn ON TOP of the helm's lower edge so the eye/mustache are always
visible under the brow) -> paint_axe (drawn LAST so the held axe is never
occluded). Scratch exploration only — nothing here is registered in
store_skins.BUILDERS and the live skin_viking is untouched.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly, _compose
from game.parrot import _add_outline
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette

WHITE = (255, 255, 255)


# ─────────────────────────────────────────────────────────────────────────────
# IRONCLAD (v1) — classic brown raider
# ─────────────────────────────────────────────────────────────────────────────
I_BODY, I_BODY_SHAD = (138, 106, 69), (94, 70, 48)
I_CHEST, I_BELLY = (160, 126, 84), (110, 82, 56)
I_HELM, I_HELM_DK, I_HELM_HI = (126, 134, 148), (74, 80, 96), (198, 206, 218)
I_FUR, I_FUR_HI = (107, 83, 58), (152, 124, 92)
I_BEARD, I_BEARD_HI = (58, 42, 27), (90, 70, 50)
I_BRONZE = (200, 144, 46)
I_SHIELD_RED, I_OAK, I_BONE = (178, 58, 42), (122, 92, 60), (214, 200, 170)
I_KEYLINE = (40, 28, 18, 235)

P_IRON = _pal(
    tail=[(120, 90, 58), (134, 102, 66), (150, 116, 78), (168, 132, 90)],
    tail_line=I_BODY_SHAD, body_shadow=I_BODY_SHAD, body_main=I_BODY,
    body_chest=I_CHEST, body_belly=I_BELLY, sheen=(255, 240, 215, 90),
    wing_main=(128, 98, 64), wing_dark=(86, 64, 42), wing_tip=(170, 134, 90),
    wing_secondary=None, wing_highlight=(184, 150, 104), head_shadow=I_BODY_SHAD,
    head_main=I_BODY, head_cheek=I_CHEST, head_crown=(150, 116, 78),
    lens_frame=(120, 90, 58), lens_body=(40, 30, 20), lens_tint=None,
    lens_glint=None, beak_main=(150, 120, 80), beak_dark=I_BODY_SHAD,
    beak_gloss=(190, 160, 116), foot=(96, 72, 48),
)


def _iron_base(angle_deg):
    return _build_parrot_with_palette(angle_deg, P_IRON, draw_lenses=False)


def _iron_back(surf):
    cy = CROWN_Y
    sx, sy, sr = HX - 26, HY + 11, 13
    pygame.draw.circle(surf, I_BEARD, (sx, sy), sr + 1)
    pygame.draw.circle(surf, I_OAK, (sx, sy), sr)
    pygame.draw.circle(surf, I_SHIELD_RED, (sx, sy), sr - 3)
    for dx in (-7, 0, 7):
        pygame.draw.line(surf, I_BODY_SHAD, (sx + dx, sy - sr + 2), (sx + dx, sy + sr - 2), 1)
    pygame.draw.circle(surf, I_HELM, (sx, sy), sr, 2)
    pygame.draw.circle(surf, I_HELM_DK, (sx, sy), 5)
    pygame.draw.circle(surf, I_HELM, (sx, sy), 4)
    pygame.draw.circle(surf, I_HELM_DK, (sx, sy), 4, 1)
    pygame.draw.circle(surf, I_HELM_HI, (sx - 1, sy - 1), 1)
    ruff_y = HY + 9
    for i in range(-3, 4):
        fx = HX - 1 + i * 5
        r = 5 if i % 2 == 0 else 4
        pygame.draw.circle(surf, I_FUR, (fx, ruff_y + 1), r)
        pygame.draw.circle(surf, I_FUR_HI, (fx, ruff_y), r - 1)
    for i in range(-1, 2):
        pygame.draw.circle(surf, I_FUR_HI, (HX - 1 + i * 5, ruff_y - 1), 1)


def _iron_front(surf):
    cy = CROWN_Y
    for sgn, hx0 in ((-1, HX - 9), (1, HX + 9)):
        tipx = hx0 + sgn * 6
        mid = (hx0 + sgn * 5, cy - 6)
        _poly(surf, I_BEARD, [(hx0 - 4, cy + 2), (hx0 + 4, cy + 2), mid, (tipx + sgn * 2, cy - 16)])
        _poly(surf, I_FUR_HI, [(hx0 + sgn * 3, cy + 1), (hx0 + sgn * 4, cy + 1),
                               (mid[0] + sgn, mid[1] + 1), (tipx + sgn * 2, cy - 15)])
        pygame.draw.circle(surf, I_FUR_HI, (tipx + sgn, cy - 15), 3)
        pygame.draw.circle(surf, I_BONE, (tipx + sgn, cy - 15), 2)
        pygame.draw.circle(surf, I_HELM_HI, (tipx + sgn - 1, cy - 16), 1)
    pygame.draw.ellipse(surf, I_HELM_DK, (HX - 12, cy - 6, 25, 18))
    pygame.draw.ellipse(surf, I_HELM, (HX - 11, cy - 6, 23, 8))
    pygame.draw.line(surf, I_HELM_DK, (HX, cy - 6), (HX, cy + 4), 2)
    pygame.draw.ellipse(surf, I_HELM_HI, (HX - 6, cy - 5, 9, 4))
    pygame.draw.line(surf, I_HELM_DK, (HX - 11, cy + 5), (HX + 12, cy + 4), 4)
    pygame.draw.line(surf, I_HELM, (HX - 11, cy + 4), (HX + 12, cy + 3), 1)
    for rx in (HX - 8, HX - 1, HX + 6):
        pygame.draw.circle(surf, I_BRONZE, (rx, cy + 5), 1)
    pygame.draw.rect(surf, I_HELM_DK, (HX + 1, cy + 4, 3, 11))
    pygame.draw.rect(surf, I_HELM, (HX + 1, cy + 4, 2, 10))
    for fx, fy in ((27, 65), (35, 65)):
        pygame.draw.circle(surf, I_FUR, (fx, fy + 1), 3)
        pygame.draw.circle(surf, I_FUR_HI, (fx, fy), 2)


IRONCLAD = {
    "name": "IRONCLAD", "base_fn": _iron_base, "keyline": I_KEYLINE,
    "back": _iron_back, "front": _iron_front,
    "beard": I_BEARD, "beard_hi": I_BEARD_HI, "ring": I_BRONZE,
    "blade": I_HELM, "blade_dk": I_HELM_DK, "blade_hi": I_HELM_HI,
    "haft": (74, 54, 36), "haft_hi": (124, 94, 62), "white": WHITE,
    "bone": I_BONE, "helm_hi": I_HELM_HI,
    "eye_skin": (236, 222, 198), "eye_pupil": (32, 22, 16), "eye_glint": WHITE,
}


# ─────────────────────────────────────────────────────────────────────────────
# BLOODAXE (v2) — warm rust/red raider
# ─────────────────────────────────────────────────────────────────────────────
B_RUST, B_RUST_DK = (154, 51, 34), (94, 28, 18)
B_RUST_CHEST, B_RUST_BELLY = (182, 84, 58), (122, 40, 24)
B_IRON, B_IRON_DK, B_IRON_HI = (90, 94, 104), (52, 56, 63), (166, 174, 184)
B_RING = (176, 182, 192)
B_FUR, B_FUR_HI = (74, 53, 38), (122, 90, 64)
B_BEARD, B_BEARD_HI = (36, 26, 20), (62, 44, 32)
B_SHIELD_RED, B_BRASS, B_BONE = (110, 20, 16), (199, 154, 58), (214, 198, 168)
B_KEYLINE = (26, 20, 16, 235)

P_BLOOD = _pal(
    tail=[(118, 38, 26), (138, 46, 30), (158, 58, 40), (180, 80, 56)],
    tail_line=B_RUST_DK, body_shadow=(112, 34, 22), body_main=B_RUST,
    body_chest=B_RUST_CHEST, body_belly=B_RUST_BELLY, sheen=(255, 220, 200, 90),
    wing_main=(140, 46, 30), wing_dark=(86, 26, 16), wing_tip=(196, 100, 72),
    wing_secondary=None, wing_highlight=(214, 130, 100), head_shadow=(112, 34, 22),
    head_main=B_RUST, head_cheek=B_RUST_CHEST, head_crown=(168, 64, 44),
    lens_frame=(120, 40, 26), lens_body=(40, 22, 16), lens_tint=None,
    lens_glint=None, beak_main=(196, 150, 96), beak_dark=(120, 84, 44),
    beak_gloss=(228, 200, 150), foot=(120, 78, 44),
)


def _blood_base(angle_deg):
    return _build_parrot_with_palette(angle_deg, P_BLOOD, draw_lenses=False)


def _blood_back(surf):
    sx, sy, sr = HX - 26, HY + 11, 13
    pygame.draw.circle(surf, B_IRON_DK, (sx, sy), sr + 2)
    pygame.draw.circle(surf, B_SHIELD_RED, (sx, sy), sr - 2)
    for dx in (-6, 0, 6):
        pygame.draw.line(surf, B_RUST_DK, (sx + dx, sy - sr + 4), (sx + dx, sy + sr - 4), 1)
    pygame.draw.circle(surf, B_BRASS, (sx, sy - sr + 2), 2)
    pygame.draw.circle(surf, (240, 210, 130), (sx, sy - sr + 2), 1)
    pygame.draw.circle(surf, B_IRON_DK, (sx, sy), 6)
    pygame.draw.circle(surf, B_IRON_HI, (sx, sy), 5)
    pygame.draw.circle(surf, B_IRON_DK, (sx, sy), 5, 1)
    pygame.draw.circle(surf, WHITE, (sx - 1, sy - 1), 1)
    ruff_y = HY + 9
    for i in range(-3, 4):
        fx = HX - 1 + i * 5
        r = 5 if i % 2 == 0 else 4
        pygame.draw.circle(surf, B_BEARD, (fx, ruff_y + 1), r)
        pygame.draw.circle(surf, B_FUR, (fx, ruff_y), r - 1)
    for i in range(-1, 2):
        pygame.draw.circle(surf, B_FUR_HI, (HX - 1 + i * 5, ruff_y - 1), 1)


def _blood_front(surf):
    cy = CROWN_Y
    for sgn, hx0 in ((-1, HX - 9), (1, HX + 9)):
        tipx = hx0 + sgn * 6
        mid = (hx0 + sgn * 5, cy - 6)
        _poly(surf, B_BEARD, [(hx0 - 4, cy + 2), (hx0 + 4, cy + 2), mid, (tipx + sgn * 2, cy - 16)])
        _poly(surf, B_FUR_HI, [(hx0 + sgn * 3, cy + 1), (hx0 + sgn * 4, cy + 1),
                               (mid[0] + sgn, mid[1] + 1), (tipx + sgn * 2, cy - 15)])
        pygame.draw.circle(surf, (170, 152, 120), (tipx + sgn, cy - 15), 3)
        pygame.draw.circle(surf, B_BONE, (tipx + sgn, cy - 15), 2)
        pygame.draw.circle(surf, (244, 234, 210), (tipx + sgn - 1, cy - 16), 1)
    pygame.draw.ellipse(surf, B_IRON_DK, (HX - 12, cy - 6, 25, 18))
    pygame.draw.ellipse(surf, B_IRON, (HX - 11, cy - 6, 23, 8))
    pygame.draw.line(surf, B_IRON_DK, (HX, cy - 6), (HX, cy + 4), 2)
    pygame.draw.ellipse(surf, B_IRON_HI, (HX - 6, cy - 5, 9, 4))
    pygame.draw.line(surf, B_IRON_DK, (HX - 11, cy + 5), (HX + 12, cy + 4), 4)
    pygame.draw.line(surf, B_IRON_HI, (HX - 11, cy + 4), (HX + 12, cy + 3), 1)
    for rx in (HX - 8, HX - 1, HX + 6):
        pygame.draw.circle(surf, B_IRON_HI, (rx, cy + 5), 1)
    pygame.draw.rect(surf, B_IRON_DK, (HX + 1, cy + 4, 3, 11))
    pygame.draw.rect(surf, B_IRON, (HX + 1, cy + 4, 2, 10))
    for fx, fy in ((27, 65), (35, 65)):
        pygame.draw.circle(surf, B_BEARD, (fx, fy + 1), 3)
        pygame.draw.circle(surf, B_FUR_HI, (fx, fy), 2)


BLOODAXE = {
    "name": "BLOODAXE", "base_fn": _blood_base, "keyline": B_KEYLINE,
    "back": _blood_back, "front": _blood_front,
    "beard": B_BEARD, "beard_hi": B_BEARD_HI, "ring": B_RING,
    "blade": B_IRON, "blade_dk": B_IRON_DK, "blade_hi": B_IRON_HI,
    "haft": (94, 56, 32), "haft_hi": (150, 96, 56), "white": WHITE,
    "bone": B_BONE, "helm_hi": B_IRON_HI,
    "eye_skin": (236, 214, 190), "eye_pupil": (28, 18, 14), "eye_glint": WHITE,
}

PALETTES = {"ironclad": IRONCLAD, "bloodaxe": BLOODAXE}


# ─────────────────────────────────────────────────────────────────────────────
def make_build(paint_face, paint_axe, P):
    """Compose the frozen base costume with a design's face + held axe and wrap
    in that palette's keyline, returning a `(frame_idx, tilt_deg) -> Surface`
    getter (same contract as store_skins._make_skin)."""
    def _paint(surf, a):
        P["back"](surf)        # shield + fur ruff (behind/over body)
        P["front"](surf)       # horned helm + nasal + boots (on the head)
        paint_face(surf, a, P)  # eye + mustache + beard, ON TOP of the helm brow
        paint_axe(surf, a, P)   # the held axe, drawn LAST so it's never occluded

    state = {"frames": None, "rot": {}}

    def getter(frame_idx, tilt_deg):
        if state["frames"] is None:
            state["frames"] = [
                _add_outline(_compose(ang, _paint, base_fn=P["base_fn"]),
                             outline_color=P["keyline"])
                for ang in store_skins._WING_ANGLES
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
