"""LANTERN STREET — main-menu concept, round 1 (docs/menu-v3/lantern-street).

Staged from the LIVE game modules only: the alpine_haze sky, the V14 ridge
bands, two gameplay pagodas used as street gate-towers, the buff running-bond
paving, the promenade + near-lane cast, and the HUD's own pill/panel/outlined
type. Nothing here is invented art — the menu is the game's own world held
still at the moment the lanterns come on.

Everything is drawn at 1x directly onto the 360x640 target. No supersample, no
smoothscale of any world layer or of Pip: crispness match with the run IS the
belief gate, and a low-pass would half-destroy the sky's Bayer dither and bleed
the pagodas' 1px vermilion highlights.

Run: SDL_VIDEODRIVER=dummy python tools/menu_v3_lantern_street.py
"""
from __future__ import annotations

import math
import os
import random
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
pygame.init()
pygame.display.set_mode((360, 640))

from game import biome as _biome                      # noqa: E402
from game import cloud_variants as _clouds            # noqa: E402
from game import foreground as _fg                    # noqa: E402
from game import foreground_floor as _floor           # noqa: E402
from game import foreground_promenade as _pr          # noqa: E402
from game import foreground_props as _sp              # noqa: E402
from game import foreground_zbuffer as _zbuf          # noqa: E402
from game import hud as _hud                          # noqa: E402
from game import mountains_v14 as _mtn                # noqa: E402
from game import parrot as _parrot                    # noqa: E402
from game import pillar_pagodas as _pag               # noqa: E402
from game import sky_designs as _sky                  # noqa: E402
from game import store_data as _store                 # noqa: E402
from game.foreground_zbuffer import TB_CAST, TB_STRUCTURE   # noqa: E402

W, H = 360, 640
GROUND_Y = 595
PHASE = 0.38          # the documented dusk floor: "lamps JUST beginning to glow"
SCROLL = 1021         # hand-picked: lamp posts land at x~131 and x~247
BIOME_T = 200.0       # late enough that the street has fully filled in

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "docs", "menu-v3", "lantern-street")


# ── world ────────────────────────────────────────────────────────────────────

def _palettes():
    pal = _biome.palette_for_phase(PHASE)
    cloud_pal = _sky.active_cloud_palette(PHASE, pal) or pal
    return pal, cloud_pal


def draw_world(surf, pal, cloud_pal):
    """The live background stack, in the live order, at a held scroll."""
    _sky.render_active(surf, W, H, GROUND_Y, pal, PHASE)

    # Two ruyi clouds only. The sunset band is the loudest thing in the frame;
    # a third cloud starts competing with the ridge crowns for the eye.
    _clouds.draw_ruyi_mandala(surf, 286, 118, cloud_pal, 1.0)
    _clouds.draw_cloud_ruyi(surf, 70, 176, cloud_pal, 0.65)

    # ground_y=520 floats the ink-wash bands clear of the street so the horizon
    # glow reads as real distance between the village and the paving.
    _mtn.draw_mountains_v14(surf, SCROLL, 520, W, phase=PHASE)

    _fg.draw_foreground_floor(surf, SCROLL, pal, PHASE)

    # Promenade + the hand-staged vignettes share one z-pass, so the market
    # sorts against the street furniture exactly as it does in play.
    _zbuf.reset()
    _pr.draw_promenade(surf, SCROLL, pal, PHASE, BIOME_T)
    _stage_street(pal)
    _zbuf.flush(surf)

    # Gate-towers after the floor + far lane, before the near lane: the same
    # slot the gameplay pillars occupy.
    _gate_towers(surf, pal)

    _fg.draw_near_lane(surf, SCROLL, pal, PHASE, BIOME_T)

    _high_garland(surf, pal)


def _stage_street(pal):
    """Hand-placed vignettes. The day-arc director thins the afternoon street to
    a 0.255 density, which is right for a run and wrong for a menu — a menu is a
    composed still, so the market beat is placed rather than rolled."""
    rng = random.Random(4021)

    def emit(tier, fn):
        _zbuf.enqueue(GROUND_Y - 1, tier, fn)

    _pr._scene_market(emit, 118, pal, BIOME_T, rng, pick=lambda *_a: 0)
    _pr._scene_bench(emit, 236, pal, BIOME_T, rng, pick=lambda *_a: 1)
    # The lamplighter IS the thesis: he is why the lanterns are coming on.
    emit(TB_CAST, lambda s: _pr.draw_lamplighter(s, 258, pal, t=BIOME_T))
    emit(TB_STRUCTURE, lambda s: _pr.draw_prop_fire(s, 330, pal, t=BIOME_T,
                                                    variant=0))


def _gate_towers(surf, pal):
    """Two gameplay pagodas re-used as the street's gate-towers — the
    proscenium that makes this a composed frame instead of a screenshot.
    Different seeds so the variants read as two different buildings; the top
    rect is zero-height so only the ground-standing half is drawn."""
    for x, seed in ((14, 5), (276, 24)):     # 5 -> toji, 24 % 11 -> songyue
        _pag.draw_pillar_pair(surf,
                              pygame.Rect(x, 0, 72, 0),
                              pygame.Rect(x, 300, 72, GROUND_Y - 300),
                              pal, seed, phase=PHASE, pillar_index=3)


def _high_garland(surf, pal):
    """One lantern strand slung between the gate-tower shoulders. It closes the
    top of the proscenium and repeats the street's own garland an octave up."""
    pts = _sp._catenary_pts(-8, 368, 300, 30, 22)
    rope = _sp._mix((62, 52, 44), (40, 44, 60), 0.3 * _sp._nightf(pal))
    pygame.draw.lines(surf, rope, False,
                      [(int(x), int(y)) for x, y in pts], 1)
    for j in range(7):
        t = (j + 0.5) / 7
        bx, by = _sp._span_point(-8, 368, 300, 30, t)
        _sp._draw_lantern_head(surf, int(bx), int(by), pal,
                               color=('red', 'gold')[j % 2], scale=0.62,
                               glow_radius=8, glow_alpha=54)


# ── Pip ──────────────────────────────────────────────────────────────────────

PIP_SCALE = 1.3
PIP_FEET_Y = 594
PIP_CX = 112
_RIM_WARM = (246, 196, 120)      # lantern-side rim; luma 202, under the 220 cap


def _rim_light(body, outlined, pad):
    """A flat 1px warm edge painted INTO Pip's own alpha mask, offset toward the
    lantern. Deliberately not additive and not a halo — Pip is lit by the
    street, he is not an emitter, and an ADD pass would make him one."""
    w, h = body.get_size()
    mask = pygame.mask.from_surface(body, threshold=8)
    solid = mask.to_surface(setcolor=(255, 255, 255, 255),
                            unsetcolor=(0, 0, 0, 0))
    # Shifted AWAY from the light, then inverted: what survives is the 1px
    # sliver of silhouette that faces the lantern.
    shifted = pygame.Surface((w, h), pygame.SRCALPHA)
    shifted.blit(solid, (-1, 1))
    inv = pygame.Surface((w, h), pygame.SRCALPHA)
    inv.fill((255, 255, 255, 255))
    inv.blit(shifted, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
    inv.fill((255, 255, 255, 0), special_flags=pygame.BLEND_RGBA_MAX)
    edge = solid.copy()
    edge.blit(inv, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    rim = pygame.Surface((w, h), pygame.SRCALPHA)
    rim.fill((*_RIM_WARM, 255))
    rim.blit(edge, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    outlined.blit(rim, (pad, pad))


def build_pip():
    """Pip at hero scale through the VECTOR-scaled path (the one get_grow_parrot
    uses), never smoothscale: a filtered downscale would smear his 1px cast
    outline into a ~1.3px blur while the in-run Pip keeps a hard one, and the
    hard cast is what holds him off the busy street."""
    skin = _store.equipped("skin") or "skin_base"
    parcel_id = _store.equipped("parcel") or "parcel_base"
    if skin == "skin_base":
        # -10deg is the settled wing: a held standing pose, not a flap frame.
        body = _parrot._build_frame_scaled(-10, PIP_SCALE)
        pad = max(1, int(round(PIP_SCALE))) + 1
        sprite = _parrot._add_outline_scaled(body, PIP_SCALE)
        _rim_light(body, sprite, pad)
    else:
        # Store skins own their whole render; keep them 1:1 rather than resample.
        sprite = _parrot.get_skin_frame(skin, 2, 0.0)
    parcel = _parrot.get_parcel("normal", parcel_id)
    return sprite, parcel


def draw_pip(surf):
    sprite, parcel = build_pip()
    sw, sh = sprite.get_size()
    # Feet sit at sprite-y 49 of the 60px source, plus the outline pad.
    top = PIP_FEET_Y - int(round(49 * PIP_SCALE)) - max(1, int(round(PIP_SCALE))) - 1
    left = PIP_CX - sw // 2
    surf.blit(sprite, (left, top))
    cx = left + sw // 2
    cy = top + int(round(30 * PIP_SCALE))
    pr = parcel.get_rect(center=(cx - 2, cy + int(round(12 * PIP_SCALE))))
    surf.blit(parcel, pr.topleft)
    return pygame.Rect(left, top, sw, sh), pr


# ── UI ───────────────────────────────────────────────────────────────────────

CHIP_W, CHIP_H, CHIP_GAP, CHIP_CY = 76, 54, 12, 430
START_CY = 497
START_MIN_W = 244


def _chip_icon_profile(surf, cx, cy):
    """The PROFILE icon is the LIVE equipped skin, not a hardcoded base parrot."""
    hi = _parrot.get_skin_frame_hi(_store.equipped("skin") or "skin_base")
    w, h = hi.get_size()
    k = min(26 / w, 24 / h)
    thumb = pygame.transform.smoothscale(hi, (max(1, int(w * k)),
                                              max(1, int(h * k))))
    surf.blit(thumb, thumb.get_rect(center=(cx, cy)))


def draw_ui(surf, t=0.0):
    rects = {}
    _hud._outlined_text(surf, "SKYBIT", (W // 2, 92), size=64, px=3)
    _hud._outlined_text(surf, "POCKET  SKY  FLYER", (W // 2, 134),
                        size=20, px=2, shadow_offset=(2, 3))

    x = 10
    for label, kind in (("PROFILE", "pip"), ("STORE", "coin"),
                        ("TOP 10", "trophy"), ("SETTINGS", "gear")):
        r = pygame.Rect(x, CHIP_CY - CHIP_H // 2, CHIP_W, CHIP_H)
        _hud._volume_panel(surf, r, radius=13)
        icy = CHIP_CY - 7
        if kind == "pip":
            _chip_icon_profile(surf, r.centerx, icy)
        elif kind == "coin":
            _hud._coin_icon(surf, r.centerx, icy, 12)
        elif kind == "trophy":
            _hud._draw_trophy(surf, r.centerx, icy, 10)
        else:
            _hud._draw_gear(surf, r.centerx, icy, 12)
        _hud._tracked_label(surf, label, (r.centerx, CHIP_CY + 16), 12,
                            color=_hud._AWSTAR_HI, track=1, alpha=225)
        rects[label] = r
        x += CHIP_W + CHIP_GAP

    rects["START"] = _hud._pill_btn(surf, (W // 2, START_CY), "START",
                                    size=30, min_width=START_MIN_W,
                                    primary=True, dim=True, shadow=True)
    return rects


# ── the current shipped menu, for the A/B panel ──────────────────────────────

def draw_current_ui(surf):
    dim = pygame.Surface((W, H), pygame.SRCALPHA)
    dim.fill((6, 1, 21, 110))
    surf.blit(dim, (0, 0))
    stars = [(random.Random(i * 97).randint(0, W - 1),
              random.Random(i * 131).randint(0, 260),
              random.Random(i * 17).choice((1, 1, 2)), i * 0.7)
             for i in range(40)]
    _hud._draw_overlay_stars(surf, stars, 0.0)
    _hud._draw_mountain_silhouette(surf, alpha=180)
    _hud._outlined_text(surf, "SKYBIT", (W // 2, 126), size=72, px=3)
    _hud._outlined_text(surf, "POCKET  SKY  FLYER", (W // 2, 184),
                        size=22, px=2, shadow_offset=(2, 3))
    pygame.draw.line(surf, (*_hud._ORANGE_BORDER, 120),
                     (W // 2 - 70, 208), (W // 2 + 70, 208), 1)
    _hud._pill_btn(surf, (W // 2, 430), "START", size=24, alpha=240,
                   min_width=240, primary=True, dim=True, shadow=False)
    cy = H - 86
    tw, tg, th = 84, 8, 54
    tx = (W - (tw * 3 + tg * 2)) // 2
    for label, kind in (("STORE", "coin"), ("TOP 10", "trophy"),
                        ("SETTINGS", "gear")):
        r = pygame.Rect(tx, cy - th // 2, tw, th)
        _hud._volume_panel(surf, r, radius=13)
        if kind == "coin":
            _hud._coin_icon(surf, r.centerx, cy - 5, 12)
        elif kind == "trophy":
            _hud._draw_trophy(surf, r.centerx, cy - 5, 10)
        else:
            _hud._draw_gear(surf, r.centerx, cy - 5, 12)
        _hud._tracked_label(surf, label, (r.centerx, cy + 15), 10,
                            color=_hud._AWSTAR_HI, track=1, alpha=210)
        tx += tw + tg


def render_menu(with_ui=True, current=False):
    surf = pygame.Surface((W, H))
    pal, cloud_pal = _palettes()
    draw_world(surf, pal, cloud_pal)
    if current:
        draw_current_ui(surf)
        return surf, {}, None, None
    pip_rect, parcel_rect = draw_pip(surf)
    rects = draw_ui(surf) if with_ui else {}
    return surf, rects, pip_rect, parcel_rect


# ── review sheet ─────────────────────────────────────────────────────────────

def _label(sheet, txt, pos, size=17, col=(238, 232, 214)):
    f = pygame.font.Font(_hud._FONT_BOLD, size)
    img = f.render(txt, True, col)
    sh = f.render(txt, True, (10, 8, 20))
    sheet.blit(sh, (pos[0] + 1, pos[1] + 2))
    sheet.blit(img, pos)
    return img.get_width()


def build_sheet(new_surf, cur_surf):
    zoom_w = 300
    sw, sh = 16 + 360 + 24 + 360 + 24 + zoom_w + 16, 44 + 640 + 44
    sheet = pygame.Surface((sw, sh))
    for y in range(sh):
        t = y / (sh - 1)
        sheet.fill((int(22 + 10 * t), int(18 + 8 * t), int(34 + 12 * t)),
                   pygame.Rect(0, y, sw, 1))
    _label(sheet, "SKYBIT MAIN MENU  /  menu-v3  /  concept: LANTERN STREET  /  round 1",
           (16, 12), 19)
    ax, bx = 16, 16 + 360 + 24
    sheet.blit(cur_surf, (ax, 44))
    sheet.blit(new_surf, (bx, 44))
    pygame.draw.rect(sheet, (90, 78, 64), (ax - 1, 43, 362, 642), 1)
    pygame.draw.rect(sheet, (240, 192, 64), (bx - 1, 43, 362, 642), 1)
    _label(sheet, "CURRENT  (shipped menu)", (ax, 44 + 640 + 10), 15,
           (196, 190, 178))
    _label(sheet, "LANTERN STREET  round 1  -  phase 0.38, 1x native",
           (bx, 44 + 640 + 10), 15, (240, 192, 64))

    zx = bx + 360 + 24
    _label(sheet, "DETAIL  (2x nearest, no filtering)", (zx, 48), 15,
           (196, 190, 178))
    y = 72
    for cap, rect in (("Pip 1.3x + parcel + rim", pygame.Rect(52, 528, 100, 76)),
                      ("START capsule on street", pygame.Rect(48, 462, 264, 72)),
                      ("chips: PROFILE = live skin", pygame.Rect(6, 398, 180, 64)),
                      ("gate-tower + garland", pygame.Rect(258, 286, 100, 120))):
        crop = pygame.Surface(rect.size)
        crop.blit(new_surf, (0, 0), rect)
        big = pygame.transform.scale(crop, (rect.width * 2, rect.height * 2))
        scale = min(zoom_w / big.get_width(), 1.0)
        if scale < 1.0:
            big = pygame.transform.scale(
                big, (int(big.get_width() * scale), int(big.get_height() * scale)))
        _label(sheet, cap, (zx, y), 13, (222, 214, 198))
        sheet.blit(big, (zx, y + 18))
        pygame.draw.rect(sheet, (90, 78, 64),
                         (zx - 1, y + 17, big.get_width() + 2,
                          big.get_height() + 2), 1)
        y += big.get_height() + 34
    return sheet


def main():
    random.seed(7)
    cur, _r, _p, _q = render_menu(current=True)
    _sp._LATCH.clear()
    _sp._LATCH_SEEN.clear()
    random.seed(7)
    new, rects, pip_rect, parcel_rect = render_menu()
    os.makedirs(OUT_DIR, exist_ok=True)
    pygame.image.save(new, os.path.join(OUT_DIR, "_menu_1x.png"))
    sheet = build_sheet(new, cur)
    out = os.path.join(OUT_DIR, "round_1.png")
    pygame.image.save(sheet, out)
    print("wrote", out, sheet.get_size())
    print("tap targets:")
    for k, r in rects.items():
        print("   ", k, tuple(r))
    print("pip", tuple(pip_rect), "parcel", tuple(parcel_rect))


if __name__ == "__main__":
    main()
