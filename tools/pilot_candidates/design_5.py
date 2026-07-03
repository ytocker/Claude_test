"""Pilot costume — Design 5: BUSH RUNNER (barnstormer / bush pilot).

Scratch exploration builder wrapped by the store-skin contract, NOT registered
in ``store_skins.BUILDERS``. Exposes ``build`` for the generic ninja_render
harness. The hero read at 40px is round BRASS GOGGLES worn DOWN OVER THE EYES
(the tell that sets it apart from the brow-goggle Ace), a battered soft canvas
flight cap floating clear of the face, a khaki field shirt, and a rolled MAP
cylinder breaking the wing-root silhouette — a scruffy, gear-laden working
pilot on a mission instead of a polished uniform.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import pygame

from game.store_skins import (
    _pal, _build_parrot_with_palette, _make_skin, _poly, HX, HY, CROWN_Y,
)

# ── palette: re-plumage the macaw in warm field khaki ────────────────────────
# Khaki body so the brass goggles + pale map read as high-value marks ON warm
# canvas instead of gold-on-red; the head takes the canvas-cap tone so the soft
# cap welds to the crown, and the beak stays a warm bone so nothing scarlet
# survives the two-tone.
_CAP_CANVAS = (122, 106, 74)        # floppy cap body / head
_CAP_HI     = (138, 122, 84)        # cap dome highlight — lifts cap off the face
_CAP_SHADOW = (92, 78, 54)          # cap creases (deepened)
_CAP_BASE   = (74, 62, 42)          # dark seam where the cap meets the head
_BRASS      = (201, 162, 74)        # goggle rings
_GLASS      = (58, 74, 85)          # tinted lens fill
_KHAKI      = (184, 166, 108)       # base belly tone
_SHIRT      = (176, 162, 100)       # olive-nudged field shirt block
_COLLAR     = (206, 192, 140)       # lit collar line at the shirt neck
_MAP_PAPER  = (231, 219, 184)       # rolled map paper
_MAP_PAPER_H= (242, 232, 206)       # map top glint so the tube reads round
_MAP_CAP    = (201, 190, 150)       # darker rolled-end caps
_MAP_ROUTE  = (184, 92, 56)         # route lines on the map
_LEATHER    = (92, 70, 40)          # harness strap
_BUCKLE     = (232, 200, 96)        # hot buckle brass (hotter than goggles)
_BUCKLE_D   = (74, 52, 24)          # buckle dark border
_RIM        = (58, 48, 32)          # warm-dark body rim vs. sandstone pillars

P_BUSH = _pal(
    tail=[(120, 102, 68), (130, 110, 74), (140, 120, 82), (150, 130, 90)],
    tail_line=(96, 80, 52),
    body_shadow=(110, 90, 60),
    body_main=(150, 130, 90),
    body_chest=(196, 178, 120),
    body_belly=_KHAKI,
    sheen=(236, 224, 190, 55),
    wing_main=(130, 110, 74),
    wing_dark=(100, 84, 56),
    wing_tip=(146, 126, 86),
    wing_secondary=None,
    wing_highlight=(168, 148, 104),
    head_shadow=(92, 78, 54),
    head_main=_CAP_CANVAS,
    head_cheek=(140, 122, 88),
    head_crown=(134, 116, 82),
    lens_frame=(110, 90, 60),
    lens_body=_GLASS,
    lens_tint=None,
    lens_glint=None,
    beak_main=(180, 158, 90),
    beak_dark=(130, 105, 55),
    beak_gloss=(224, 204, 140),
    foot=(110, 90, 60),
)


def _bush_rim_outer(src, color):
    # Stamp a 1px warm-dark ring on the body's OUTER contour: the tan plumage
    # sits at the value of the day-biome sandstone pillars, so without this edge
    # the bird camouflages against them (and vanishes on night sky). Grow the
    # alpha mask 1px, then lay the sprite back so only the contour ring survives.
    out = pygame.Surface(src.get_size(), pygame.SRCALPHA)
    mask = pygame.mask.from_surface(src, threshold=8)
    ring = mask.to_surface(setcolor=color, unsetcolor=(0, 0, 0, 0))
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        out.blit(ring, (dx, dy))
    out.blit(src, (0, 0))
    return out


def _bush_base(angle_deg):
    # Khaki-plumaged bird, no aviators — the brass goggles own the eye cluster;
    # a warm-dark rim keeps the tan body off the tan pillars.
    body = _build_parrot_with_palette(angle_deg, P_BUSH, draw_lenses=False)
    return _bush_rim_outer(body, _RIM)


def _paint_bush(surf, wing_angle_deg):
    # Body centre in composite space (base body centre (32,32) + PARROT_DY=20).
    BCX, BCY = 32, 52

    # ── khaki field shirt block over the chest/belly — an olive-nudged canvas
    # panel so the front reads as a pilot's working shirt (not the default parrot
    # underside) and separates from the sandstone pillars. A lit collar line ties
    # it to the neck.
    pygame.draw.ellipse(surf, _SHIRT, (BCX - 6, BCY + 2, 22, 15))
    pygame.draw.line(surf, _COLLAR, (BCX - 3, BCY + 3), (BCX + 13, BCY - 1), 2)

    # ── rolled map breaking the wing-root silhouette (the concept's signature
    # prop): a pale paper tube capped at both ends with darker rolled ellipses so
    # it reads as a cylinder, two route lines run its length, and the LEFT cap is
    # punched past the body edge so it reads as carried cargo, not body texture.
    mx0, mx1, my = BCX - 20, BCX - 6, BCY + 2      # x12..26, y54
    pygame.draw.rect(surf, _MAP_PAPER, (mx0, my, mx1 - mx0, 6), border_radius=2)
    pygame.draw.line(surf, _MAP_PAPER_H, (mx0 + 1, my + 1), (mx1 - 1, my + 1), 1)
    pygame.draw.ellipse(surf, _MAP_CAP, (mx0 - 2, my, 4, 6))    # left cap breaks edge
    pygame.draw.ellipse(surf, _MAP_CAP, (mx1 - 2, my, 4, 6))    # right rolled end
    pygame.draw.line(surf, _MAP_ROUTE, (mx0 + 2, my + 3), (mx1 - 2, my + 3), 1)
    pygame.draw.line(surf, _MAP_ROUTE, (mx0 + 3, my + 5), (mx1 - 1, my + 5), 1)

    # ── diagonal leather harness strap shoulder-to-hip, crossing the shirt, with
    # one HARD brass buckle at the crossing so the rig reads as working gear.
    pygame.draw.line(surf, _LEATHER, (BCX - 6, BCY - 2), (BCX + 12, BCY + 14), 3)
    bx, by = 37, 60
    pygame.draw.rect(surf, _BUCKLE_D, (bx - 2, by - 2, 5, 5))
    pygame.draw.rect(surf, _BUCKLE, (bx - 1, by - 1, 3, 3))

    # ── battered soft canvas flight cap floating clear of the face: a floppy
    # rounded polygon over the crown, a lighter dome highlight + deepened crease
    # push the cap OFF the head in value, and a dark seam where the cap meets the
    # head reads as the headband so the cap is a distinct shape, not a brown blob.
    cap = [(HX - 10, CROWN_Y + 3), (HX - 5, CROWN_Y - 4), (HX + 6, CROWN_Y - 5),
           (HX + 10, CROWN_Y + 2), (HX + 9, CROWN_Y + 9), (HX - 8, CROWN_Y + 9)]
    _poly(surf, _CAP_CANVAS, cap)
    _poly(surf, _CAP_HI, [(HX - 4, CROWN_Y - 4), (HX + 6, CROWN_Y - 5),
                          (HX + 7, CROWN_Y - 1), (HX - 3, CROWN_Y)])
    pygame.draw.line(surf, _CAP_SHADOW, (HX - 3, CROWN_Y + 3), (HX + 7, CROWN_Y), 1)
    pygame.draw.line(surf, _CAP_BASE, (HX - 9, CROWN_Y + 1), (HX + 9, CROWN_Y), 1)
    pygame.draw.rect(surf, _CAP_SHADOW, (HX + 9, CROWN_Y + 6, 4, 5))   # ear-strap flap

    # ── round goggles worn DOWN OVER THE EYES (hero read + the tell that
    # separates the bush pilot from the brow-goggle Ace) — UNCHANGED from R1: two
    # big tinted lenses in bright brass rings, bridged, each with a white glint,
    # and a strap up to the cap on one side.
    pygame.draw.line(surf, (160, 130, 60), (HX - 4, HY - 4), (HX - 10, CROWN_Y + 8), 1)
    for cx in (HX + 1, HX + 8):
        pygame.draw.circle(surf, _GLASS, (cx, HY - 4), 5)
        pygame.draw.circle(surf, _BRASS, (cx, HY - 4), 5, 2)
        pygame.draw.circle(surf, (255, 255, 255), (cx - 2, HY - 6), 1)
    pygame.draw.line(surf, _BRASS, (HX + 4, HY - 4), (HX + 6, HY - 4), 3)


build = _make_skin(_paint_bush, base_fn=_bush_base)
