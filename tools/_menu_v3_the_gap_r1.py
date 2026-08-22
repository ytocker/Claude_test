"""menu-v3 concept "THE GAP" — round 1 review sheet.

Standalone renderer: nothing under game/ is touched. The concept stages the
game's OWN world as a held first frame — a pagoda pair splits a gap dead
centre, two more ranks recede behind it, coins emerge from the gap toward
camera, Pip hovers in the bird lane. Every layer is a live call into the
shipped draw modules so the frame is the game, not a painting of it.

Rendered at 1× straight onto the 360×640 virtual canvas. No supersample, no
resample of the composed frame: the Bayer dither in the floor and the 1px
cast outline on Pip are the two textures that a downsample would destroy,
and crispness-match is the whole point of the concept.
"""
from __future__ import annotations

import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

pygame.init()
pygame.display.set_mode((8, 8))

from game import biome, sky_designs, hud, parrot, store_data
from game import foreground, foreground_floor as _floor
from game import foreground_near_lane as _near
from game import foreground_promenade as _pr
from game import pillar_pagodas as _pag
from game.mountains_v14 import draw_mountains_v14, _haze, _mix
from game.draw import draw_cloud
from game.entities import _get_coin_face
from game.config import W, H, GROUND_Y, PARCEL_Y_OFFSET

PHASE = 0.34
SCROLL = 0.0

# The corridor's three ranks. Widths are multiples of PIPE_W(58) — the pagoda
# candidates derive every tier, eave and finial from the rect, so a narrower
# rect draws a genuinely smaller pagoda rather than a scaled bitmap of one.
NEAR_W, MID_W, FAR_W = 116, 41, 26
# All three ranks share one candidate (seed % 11 == 2 -> songyue_sandstone) so
# the funnel reads as ONE corridor receding; the differing seeds still re-roll
# the ornament layer, so they are not clones.
SEED_NEAR, SEED_MID, SEED_FAR = 2, 13, 24

# (seed, width, centres, gap_top, gap_bot, base_y, veil_alpha), back to front.
# Bases lift as the rank recedes because a further pagoda stands on ground
# further up the picture plane; the overlap that produces is the depth cue the
# veil then confirms.
RANKS = (
    (SEED_FAR,  FAR_W,  (150, 210), 260, 340, 582, 155),
    (SEED_MID,  MID_W,  (118, 242), 249, 375, 588, 80),
    (SEED_NEAR, NEAR_W, (18, 342),  250, 430, 598,  0),
)

BIRD_LANE = (48, 188)
PIP_POS = (100, 372)
PIP_SCALE = 1.25
PIP_TILT = 18.0
PIP_FRAME = 1

# Coins EMERGE from the gap toward camera — 7px at the far mouth growing to
# 16px near-frame — so the recession points the eye down onto the CTA instead
# of back up into the vanishing point.
COINS = [(180, 302, 7), (187, 331, 9), (196, 364, 11),
         (200, 402, 13), (196, 448, 16)]

CTA_CENTER = (180, 500)
CHIP_CY = 580
CHIP_W, CHIP_H, CHIP_GAP = 76, 54, 12
CHIP_X0 = 10


def _luma(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


# ── world layers ─────────────────────────────────────────────────────────────

def rank_band(pal, seed, width, centers, gap_top, gap_bot, base_y, veil_a):
    """One receding rank as its own transparent band: a pagoda pair per centre,
    then a flat haze veil masked to the rank's silhouette.

    The veil value is the mountains' own single haze colour, so a receded rank
    lands on the aerial ramp the ridges already use. It is deliberately FLAT and
    silhouette-masked — a vertical alpha ramp would be a gradient painted onto
    objects, and an unmasked rect would fog the sky the coins have to clear."""
    band = pygame.Surface((W, H), pygame.SRCALPHA)
    for i, cx in enumerate(centers):
        x = int(cx - width / 2)
        top = pygame.Rect(x, 0, width, gap_top)
        bot = pygame.Rect(x, gap_bot, width, base_y - gap_bot)
        _pag.draw_pillar_pair(band, top, bot, pal, seed + i * 11, phase=PHASE)
    if veil_a:
        haze = _mix(_haze(pal['mtn_far'], pal['mtn_near']), pal['horizon'], 0.32)
        silhouette = pygame.mask.from_surface(band, threshold=8).to_surface(
            setcolor=(*haze, veil_a), unsetcolor=(0, 0, 0, 0))
        band.blit(silhouette, (0, 0))
    return band


def _near_strip(surf, pal):
    """The near kerb: a second paving plane a hair closer to camera than the
    play floor, stepped one flat value darker so the bottom of the frame has a
    front edge for the near-lane figures to walk on."""
    band = pygame.Surface((W, 22), pygame.SRCALPHA)
    _floor.fg_swatch_buff_running_bond(band, W, 0, 22, SCROLL + 512, pal)
    shade = pygame.Surface((W, 22), pygame.SRCALPHA)
    shade.fill((*_floor._shade(_floor._sandstone(pal), -30), 64))
    band.blit(shade, (0, 0))
    surf.blit(band, (0, 618))
    keyline = _floor._shade(_floor._sandstone(pal), -46)
    pygame.draw.line(surf, keyline, (0, 618), (W - 1, 618), 1)


def _cast(surf, pal):
    """Two near-lane figures only. The energy of this frame is aerial, so the
    civic layer is a scale cue, not a crowd — a promenade would fight the
    funnel it stands under."""
    _pr._CUR_BUCKET = biome.phase_bucket(PHASE)
    _near._scaled_cast(surf, _pr.draw_old_man, 58, pal, 1.55,
                       t=0.4, feet_y=_near.NEAR_GROUND_Y)
    _near._scaled_cast(surf, _pr.draw_vendor, 300, pal, 1.5,
                       t=1.1, feet_y=_near.NEAR_GROUND_Y, flip=True)


def _coins(surf):
    face = _get_coin_face()
    for cx, cy, d in COINS:
        c = pygame.transform.smoothscale(face, (d, d))
        surf.blit(c, c.get_rect(center=(cx, cy)).topleft)


def _pip(surf):
    """Pip at 1.25× through the VECTOR-scaled builder, never a smoothscale of
    the 1× frame: the cast outline is what makes him pop off the pagodas, and
    resampling it turns a hard 1px keyline into a 1.3px smear."""
    skin = store_data.equipped("skin") or "skin_base"
    parcel_id = store_data.equipped("parcel") or "parcel_base"
    if skin in parrot._store_skin_builders():
        body = parrot.get_skin_frame(skin, PIP_FRAME, PIP_TILT)
        path = f"get_skin_frame({skin}) @1x"
    else:
        raw = parrot._build_frame_scaled(parrot._WING_ANGLES[PIP_FRAME], PIP_SCALE)
        body = parrot._add_outline_scaled(raw, PIP_SCALE)
        body = pygame.transform.rotozoom(body, PIP_TILT, 1.0)
        path = f"_build_frame_scaled+_add_outline_scaled @{PIP_SCALE}x"
    x, y = PIP_POS

    # Three flat trail dots, not a blur — this palette has no post pass, so
    # motion is spelled with discrete marks the same way the coin sparkle is.
    for (dx, dy, r, a) in ((-50, 18, 4, 150), (-64, 24, 3, 110), (-76, 29, 2, 75)):
        dot = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(dot, (232, 196, 132, a), (r, r), r)
        surf.blit(dot, (x + dx - r, y + dy - r))

    parcel = parrot._build_parcel_variant(
        parrot._PARCEL_PALETTES["normal"],
        icon_size=int(round(parrot.PARCEL_SIZE * PIP_SCALE))) \
        if parcel_id in (None, "parcel_base") else parrot.get_parcel("normal", parcel_id)
    surf.blit(body, body.get_rect(center=(x, y)).topleft)
    # Parcel goes ON TOP of the body, banked with the tilt — the same order and
    # the same rotated offset the live Bird.draw uses, so it hangs off the belly
    # instead of disappearing behind it.
    off = pygame.math.Vector2(0, PARCEL_Y_OFFSET * PIP_SCALE).rotate(-PIP_TILT)
    prot = pygame.transform.rotate(parcel, PIP_TILT)
    surf.blit(prot, prot.get_rect(center=(x + off.x, y + off.y)).topleft)
    return path, skin, parcel_id, body.get_size()


# ── UI ───────────────────────────────────────────────────────────────────────

def _profile_icon(surf, cx, cy, box):
    """PROFILE wears the LIVE equipped skin — the shipped menu hardcodes
    skin_base here, so a player who bought a costume never sees it on the
    chip that represents them."""
    src = parrot.get_skin_frame_hi(store_data.equipped("skin") or "skin_base")
    bb = src.get_bounding_rect()
    if bb.width and bb.height:
        src = src.subsurface(bb).copy()
    sw, sh = src.get_size()
    s = box / max(sw, sh)
    icon = pygame.transform.smoothscale(src, (max(1, int(sw * s)),
                                              max(1, int(sh * s))))
    surf.blit(icon, icon.get_rect(center=(cx, cy)).topleft)


def _ui(surf):
    rects = {}
    hud._outlined_text(surf, "SKYBIT", (180, 88), 62, px=3, shadow_offset=(3, 5))
    hud._outlined_text(surf, "POCKET  SKY  FLYER", (180, 130), 22, px=2,
                       shadow_offset=(2, 3))
    # shadow=True here (the shipped menu turns it off): that flag exists
    # because the pill used to sit on a flat night dim, where an offset shade
    # read as a detached smudge. On lit stone the cast shadow is what seats it.
    rects["START"] = hud._pill_btn(surf, CTA_CENTER, "START", size=32,
                                   min_width=248, primary=True, dim=True,
                                   shadow=True)

    x = CHIP_X0
    for label in ("PROFILE", "STORE", "TOP 10", "SETTINGS"):
        r = pygame.Rect(x, CHIP_CY - CHIP_H // 2, CHIP_W, CHIP_H)
        hud._volume_panel(surf, r, radius=13)
        if label == "PROFILE":
            _profile_icon(surf, r.centerx, CHIP_CY - 9, 30)
        elif label == "STORE":
            hud._coin_icon(surf, r.centerx, CHIP_CY - 9, 12)
        elif label == "TOP 10":
            hud._draw_trophy(surf, r.centerx, CHIP_CY - 9, 10)
        else:
            hud._draw_gear(surf, r.centerx, CHIP_CY - 9, 12)
        hud._tracked_label(surf, label, (r.centerx, CHIP_CY + 14), 12,
                           color=hud._AWSTAR_HI, track=1, alpha=230)
        rects[label] = r
        x += CHIP_W + CHIP_GAP
    return rects


def build():
    pal = biome.palette_for_phase(PHASE)
    surf = pygame.Surface((W, H))

    sky_designs.render_active(surf, W, H, GROUND_Y, pal, PHASE)
    cloud_pal = sky_designs.active_cloud_palette(PHASE, pal) or pal
    draw_cloud(surf, 300, 150, 1.0, variant=0, palette=cloud_pal)
    draw_mountains_v14(surf, SCROLL, GROUND_Y, W, phase=PHASE)
    foreground.draw_foreground_floor(surf, SCROLL, pal, PHASE)

    for spec in RANKS:
        surf.blit(rank_band(pal, *spec), (0, 0))

    _coins(surf)
    pip_info = _pip(surf)
    _near_strip(surf, pal)
    _cast(surf, pal)
    world = surf.copy()
    rects = _ui(surf)
    return surf, rects, pip_info, world


# ── review sheet ─────────────────────────────────────────────────────────────

SHEET_BG = (30, 28, 36)
SHEET_INK = (226, 220, 208)
SHEET_DIM = (150, 144, 158)


def _label(sheet, txt, pos, size=15, col=SHEET_INK):
    f = hud._font(size, True)
    sheet.blit(f.render(txt, True, col), pos)


def sheet(hero, rects):
    f_w, f_h = 940, 776
    sh = pygame.Surface((f_w, f_h))
    sh.fill(SHEET_BG)
    _label(sh, "menu-v3  concept: THE GAP  -  round 1", (18, 14), 18)
    _label(sh, "the threshold: the first frame of the run, held.  360x640 @ 1x, "
               "zero resample passes", (18, 38), 13, SHEET_DIM)

    sh.blit(hero, (18, 64))
    pygame.draw.rect(sh, (92, 88, 100), (17, 63, W + 2, H + 2), 1)
    _label(sh, "A - 1x hero (pixel-exact game canvas)", (18, 712), 13, SHEET_DIM)

    cx = 18 + W + 26
    _label(sh, "B - 1x detail crops (no scaling)", (cx, 64), 13, SHEET_DIM)
    crops = [("gap mouth + coin recession", pygame.Rect(120, 240, 180, 230)),
             ("Pip 1.25x - vector-scaled outline", pygame.Rect(20, 320, 180, 120)),
             ("chip row + near kerb", pygame.Rect(0, 545, 180, 95))]
    y = 86
    for name, rc in crops:
        sh.blit(hero.subsurface(rc), (cx, y))
        pygame.draw.rect(sh, (92, 88, 100), (cx - 1, y - 1, rc.w + 2, rc.h + 2), 1)
        _label(sh, name, (cx, y + rc.h + 4), 11, SHEET_DIM)
        y += rc.h + 24

    tx = cx + 200
    _label(sh, "C - phone-scale preview", (tx, 64), 13, SHEET_DIM)
    _label(sh, "(0.5x, review only - NOT", (tx, 82), 11, SHEET_DIM)
    _label(sh, " how the art is built)", (tx, 96), 11, SHEET_DIM)
    small = pygame.transform.smoothscale(hero, (W // 2, H // 2))
    sh.blit(small, (tx, 118))
    pygame.draw.rect(sh, (92, 88, 100), (tx - 1, 117, W // 2 + 2, H // 2 + 2), 1)

    ty = 118 + H // 2 + 18
    _label(sh, "tap targets (px, disjoint)", (tx, ty), 12)
    ty += 18
    for k in ("START", "PROFILE", "STORE", "TOP 10", "SETTINGS"):
        r = rects[k]
        _label(sh, f"{k:<9}{r.w}x{r.h} @({r.x},{r.y})", (tx, ty), 11, SHEET_DIM)
        ty += 15
    return sh


def main():
    hero, rects, pip_info, _world = build()
    out_dir = os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "docs", "menu-v3", "the-gap")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "round_1.png")
    pygame.image.save(sheet(hero, rects), path)
    pygame.image.save(hero, os.path.join(out_dir, "_hero_1x.png"))
    print("saved", path)
    print("pip:", pip_info)
    for k, r in rects.items():
        print(f"  target {k}: {r}")


if __name__ == "__main__":
    main()
