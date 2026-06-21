"""Comparison sheet for the UFO Store skin REDESIGN (5 concepts).

For EACH concept it renders: a hero (~130px), the 40px x3 NEAREST truth test on
BOTH a bright DAY sky and a dark NIGHT sky, and the 4 baked animation frames.
Each concept wraps through the SAME cached-getter pattern the production skin
uses (lazy 4-frame build + _add_outline + per-(frame,3deg) rotozoom tilt cache),
so the 40px truth test matches in-game rendering exactly.

Headless (SDL dummy) so it runs in CI / on the build box:
  SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python docs/animals/ufo_redesign/_render_sheet.py
"""
import os
import sys
import importlib.util
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

# Round number drives the title + output filename. `python _render_sheet.py 2`
# (or SK_ROUND=2) renders round_2.png; defaults to 2 (the current round).
ROUND = int(os.environ.get("SK_ROUND", sys.argv[1] if len(sys.argv) > 1 else "2"))

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from game.parrot import _WING_ANGLES, _add_outline

_here = os.path.dirname(__file__)
spec = importlib.util.spec_from_file_location(
    "ufo_redesign_skins", os.path.join(_here, "ufo_skins.py"))
ufo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ufo)


def _make_prebuilt_skin(build_fn):
    """Mirror of the production factory: lazy 4-frame build (outlined with the
    house silhouette outline) + per-(frame, 3deg) rotation cache. Reproduced
    here so the 40px truth test is rendered exactly as in-game."""
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


getters = [(name, _make_prebuilt_skin(fn)) for name, fn in ufo.CONCEPTS]

# ── palette / layout ─────────────────────────────────────────────────────────
PAD = 18
HERO_PX = 130
GAME_PX = 40
MAG = 3

TEXT = (236, 238, 250)
SUB = (150, 156, 190)
BG_TOP = (10, 11, 24)
BG_BOT = (18, 20, 40)
CARD_BG = (20, 22, 42)
CARD_EDGE = (190, 150, 70)        # gold rim — ultra-premium slot
NAME_COL = (255, 224, 150)

DAY_TOP, DAY_BOT = (90, 170, 230), (170, 220, 245)     # brightest day band
NIGHT_TOP, NIGHT_BOT = (5, 8, 30), (35, 55, 115)

pygame.font.init()
F_TITLE = pygame.font.SysFont("Arial", 30, bold=True)
F_SUB = pygame.font.SysFont("Arial", 14)
F_NAME = pygame.font.SysFont("Arial", 20, bold=True)
F_FEAT = pygame.font.SysFont("Arial", 12)
F_TAG = pygame.font.SysFont("Arial", 11, bold=True)

PITCHES = {
    "CHROME CLASSIC": "mirror-chrome hull + sky-reflection band, cyan dome, white rim chase",
    "EMBER DRIFTER":  "riveted copper plates, amber dome over a throbbing core, ember beam",
    "AURORA GLASS":   "iridescent oil-slick hull, prismatic dome, multicolour rim chase",
    "SCOUT ORB":      "glowing scout drone with a throbbing iris eye + orbiting guard ring",
    "CRYSTAL SHARD":  "faceted amethyst crystal disc, pulsing core lights up the facets",
}

# ── geometry of one concept row ──────────────────────────────────────────────
ROW_H = 196
HERO_W = 168
TRUTH_W = 240            # each of the day/night truth panels
FRAMES_W = 196
ROW_GAP = 14
INNER_PAD = 14

CARD_W = (PAD + INNER_PAD + HERO_W + ROW_GAP + TRUTH_W + ROW_GAP + TRUTH_W
          + ROW_GAP + FRAMES_W + INNER_PAD + PAD)
HEADER_H = 84
SHEET_W = CARD_W
SHEET_H = HEADER_H + (ROW_H + ROW_GAP) * len(getters) + PAD

sheet = pygame.Surface((SHEET_W, SHEET_H))
for y in range(SHEET_H):
    t = y / SHEET_H
    pygame.draw.line(sheet, tuple(int(BG_TOP[i] + (BG_BOT[i] - BG_TOP[i]) * t)
                                  for i in range(3)), (0, y), (SHEET_W, y))

sheet.blit(F_TITLE.render(
    "Skybit — UFO Store Skin REDESIGN (skin_ufo) · Round %d · 5 concepts" % ROUND,
    True, TEXT), (PAD, 14))
sheet.blit(F_SUB.render(
    "Each concept: HERO 130px + 40px NEAREST x3 truth test on BRIGHT DAY and NIGHT + 4 baked "
    "life-cycle frames. No wings — flap = chase / pulse / throb / facet shimmer.",
    True, SUB), (PAD, 48))
sheet.blit(F_SUB.render(
    "3 refined classic saucers (Chrome / Ember / Aurora) + 2 bold takes (Scout Orb / Crystal Shard). "
    "Velocity tilt applied outside via rotozoom; frames drawn upright.",
    True, SUB), (PAD, 66))


def _crop(getter, frame_idx, tilt):
    s = getter(frame_idx, tilt)
    rect = s.get_bounding_rect()
    if rect.w == 0 or rect.h == 0:
        rect = s.get_rect()
    return s.subsurface(rect).copy()


def smooth(getter, frame_idx, tilt, target_px):
    crop = _crop(getter, frame_idx, tilt)
    longest = max(crop.get_width(), crop.get_height())
    f = target_px / longest
    return pygame.transform.smoothscale(
        crop, (max(1, int(crop.get_width() * f)), max(1, int(crop.get_height() * f))))


def nearest40(getter, frame_idx, tilt):
    small = smooth(getter, frame_idx, tilt, GAME_PX)
    return pygame.transform.scale(small, (small.get_width() * MAG, small.get_height() * MAG))


def sky_patch(w, h, top, bot, seed):
    s = pygame.Surface((w, h))
    for y in range(h):
        t = y / h
        s.fill(tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)),
               pygame.Rect(0, y, w, 1))
    if top[0] < 40:
        r = random.Random(seed)
        for _ in range(int(w * h / 320)):
            p = (r.randint(0, w - 1), r.randint(0, h - 1))
            b = r.randint(120, 220)
            pygame.draw.circle(s, (b, b, min(255, b + 25)), p, 1)
    return s


for idx, (name, getter) in enumerate(getters):
    cy = HEADER_H + idx * (ROW_H + ROW_GAP)
    card = pygame.Rect(PAD, cy, CARD_W - 2 * PAD, ROW_H)
    pygame.draw.rect(sheet, CARD_BG, card, border_radius=14)
    pygame.draw.rect(sheet, CARD_EDGE, card, 2, border_radius=14)

    sheet.blit(F_NAME.render("%d. %s" % (idx + 1, name), True, NAME_COL),
               (card.x + INNER_PAD, cy + 8))
    sheet.blit(F_FEAT.render(PITCHES[name], True, SUB), (card.x + INNER_PAD, cy + 34))

    panel_y = cy + 52
    panel_h = ROW_H - 64
    x = card.x + INNER_PAD

    # HERO 130px on a split day/night background
    hp = pygame.Rect(x, panel_y, HERO_W, panel_h)
    half = hp.w // 2
    sheet.blit(sky_patch(half, hp.h, DAY_TOP, DAY_BOT, 1), (hp.x, hp.y))
    sheet.blit(sky_patch(hp.w - half, hp.h, NIGHT_TOP, NIGHT_BOT, 100 + idx),
               (hp.x + half, hp.y))
    pygame.draw.rect(sheet, (60, 64, 110), hp, 1, border_radius=8)
    hero = smooth(getter, 0, 0, HERO_PX)
    sheet.blit(hero, hero.get_rect(center=hp.center))
    sheet.blit(F_TAG.render("HERO 130px  (day | night)", True, TEXT), (hp.x + 6, hp.bottom - 16))
    x = hp.right + ROW_GAP

    # DAY truth test: frames 0·1·2·3 + dive, 40px NEAREST x3
    for which, (top, bot, lbl, seed) in enumerate((
            (DAY_TOP, DAY_BOT, "DAY · 40px x3 — frames 0·1·2·3 | dive", None),
            (NIGHT_TOP, NIGHT_BOT, "NIGHT · 40px x3 — frames 0·1·2·3 | dive", 200 + idx))):
        tp = pygame.Rect(x, panel_y, TRUTH_W, panel_h)
        sheet.blit(sky_patch(tp.w, tp.h, top, bot, seed or 0), (tp.x, tp.y))
        pygame.draw.rect(sheet, (60, 64, 110), tp, 1, border_radius=8)
        step = tp.w // 5
        midy = tp.y + (tp.h - 16) // 2
        for fi in range(4):
            n = nearest40(getter, fi, 0)
            sheet.blit(n, n.get_rect(center=(tp.x + step // 2 + fi * step, midy)))
        nd = nearest40(getter, 1, -28)
        sheet.blit(nd, nd.get_rect(center=(tp.x + step // 2 + 4 * step, midy)))
        fg = TEXT if seed else (30, 36, 54)
        sheet.blit(F_TAG.render(lbl, True, fg), (tp.x + 6, tp.bottom - 16))
        x = tp.right + ROW_GAP

    # 4 baked frames (clean smooth) on a neutral strip to read the life cycle
    fp = pygame.Rect(x, panel_y, FRAMES_W, panel_h)
    sheet.blit(sky_patch(fp.w, fp.h, (40, 44, 70), (24, 26, 50), 0), (fp.x, fp.y))
    pygame.draw.rect(sheet, (60, 64, 110), fp, 1, border_radius=8)
    fstep = fp.w // 4
    fmidy = fp.y + (fp.h - 16) // 2
    for fi in range(4):
        fr = smooth(getter, fi, 0, 56)
        sheet.blit(fr, fr.get_rect(center=(fp.x + fstep // 2 + fi * fstep, fmidy)))
    sheet.blit(F_TAG.render("4 baked frames (life cycle)", True, TEXT), (fp.x + 6, fp.bottom - 16))


out_path = os.path.join(_here, "round_%d.png" % ROUND)
pygame.image.save(sheet, out_path)
print("wrote", out_path, sheet.get_size())
