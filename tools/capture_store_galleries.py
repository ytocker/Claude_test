"""Per-category STORE catalog gallery figures — one PNG per store tab.

For each of the 7 store groups, builds ONE figure where every catalog item is a
tile pairing its **real store card** (top, via the live ``StoreScene._draw_card``)
with the item **on Pip in a real gameplay scene** (bottom, via the shared
``ninja_render`` recipe). A visual reference catalog: store look ↔ on-the-bird look.

Secret items are REVEALED (granted in a throwaway wallet so their cards show the
real art, not ``???``) and tagged SECRET. Parcels — a separate slot carried below
the bird, not a skin — get a small composite builder so the gameplay panel shows
Pip actually carrying the parcel.

Pure capture; no production art or game logic touched. Run headless from repo root:
``SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python tools/capture_store_galleries.py``.
"""
from __future__ import annotations
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import sys
import math
import tempfile
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

import pygame
pygame.init()

from game import parrot, store_catalog, store_data
from game.store import StoreScene, _CARD_W, _CARD_H
from game.config import PARCEL_Y_OFFSET
from game.hud import _font, _GOLD_PALE, _GOLD_DEEP, _GOLD_BRIGHT
from tools.ninja_render import gameplay_panel

OUT_DIR = os.path.join(_ROOT, "docs", "store_gallery")
os.makedirs(OUT_DIR, exist_ok=True)

GROUPS = [("costume", "COSTUMES"), ("parrot", "PARROTS"), ("animal", "ANIMALS"),
          ("shoes", "SHOES"), ("hats", "HATS"), ("shades", "SHADES"),
          ("parcels", "PARCELS")]
_BASE_IDS = (store_catalog.BASE_SKIN, store_catalog.PARCEL_BASE)

# Tile geometry: store card (162×100) above a gameplay panel + a label strip.
GP_W, GP_H = _CARD_W, 268
CARD_GAP, LABEL_H = 9, 48
TILE_W = _CARD_W
TILE_H = _CARD_H + CARD_GAP + GP_H + LABEL_H
COLS = 5
MARGIN, GUTTER, TITLE_H = 30, 24, 74
BG = (18, 16, 28)

# Tier label colours — hue+value separable, matching the store's rarity language.
_TIER_COL = {"common": (208, 178, 132), "rare": (96, 196, 240),
             "epic": (190, 104, 236), "legendary": (255, 168, 56)}


def _setup_revealed_wallet():
    """Point the wallet at a throwaway file so we can grant every item (revealing
    secret cards) without touching the player's real save. Returns the original
    STORE_FILE + temp path so the caller can restore it."""
    orig = store_data.STORE_FILE
    tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
    tmp.close()
    os.unlink(tmp.name)  # start from default state, no file yet
    store_data.STORE_FILE = tmp.name
    store_data._reset_for_test()
    store_data.load()
    return orig, tmp.name


def _restore_wallet(orig, tmp_path):
    store_data.STORE_FILE = orig
    store_data._reset_for_test()
    try:
        os.unlink(tmp_path)
    except OSError:
        pass


def _parcel_builder(pid: str):
    """A ``(frame_idx, tilt) -> Surface`` source that draws the base macaw with
    parcel ``pid`` slung below it, mirroring entities.Bird.draw's parcel placement
    (offset PARCEL_Y_OFFSET below centre, rotated + counter-rotated by tilt). The
    canvas is padded symmetrically so the BIRD stays centred (the parcel hangs into
    the lower pad) and gameplay_panel's centre-blit lands Pip where skins land."""
    def build(frame_idx: int, tilt: float) -> pygame.Surface:
        bird = parrot.get_skin_frame(store_catalog.BASE_SKIN, frame_idx, tilt)
        parcel = parrot.get_parcel("normal", pid)
        parcel_rot = pygame.transform.rotate(parcel, tilt)
        offset = pygame.math.Vector2(0, PARCEL_Y_OFFSET).rotate(-tilt)
        bw, bh = bird.get_size()
        pad = int(PARCEL_Y_OFFSET) + parcel_rot.get_height()
        canvas = pygame.Surface((bw, bh + 2 * pad), pygame.SRCALPHA)
        canvas.blit(bird, (0, pad))
        cx, cy = bw / 2, pad + bh / 2
        canvas.blit(parcel_rot,
                    parcel_rot.get_rect(center=(cx + offset.x, cy + offset.y)))
        return canvas
    return build


def _draw_tile(sheet, scene, group, sid, tx, ty):
    is_base = sid in _BASE_IDS
    secret = store_catalog.is_secret(sid)

    # ── store card (revealed, since everything is granted) ──
    scene._draw_card(sheet, sid, pygame.Rect(tx, ty, _CARD_W, _CARD_H))

    # ── gameplay panel: Pip wearing/carrying the item ──
    source = _parcel_builder(sid) if group == "parcels" else sid
    gp = gameplay_panel(source, GP_W, GP_H)
    gy = ty + _CARD_H + CARD_GAP
    pygame.draw.rect(sheet, (*_GOLD_DEEP, 255),
                     pygame.Rect(tx - 2, gy - 2, GP_W + 4, GP_H + 4), width=2)
    sheet.blit(gp, (tx, gy))

    # ── labels: NAME · price · tier (+ SECRET tag) ──
    ly = gy + GP_H + 7
    name = scene._disp_name(sid)
    sheet.blit(_font(15, True).render(name, True, _GOLD_PALE), (tx + 2, ly))
    if is_base:
        sheet.blit(_font(12, True).render("FREE — DEFAULT", True, (190, 186, 206)),
                   (tx + 2, ly + 20))
    else:
        sheet.blit(_font(12, True).render(f"{store_catalog.cost(sid)} coins", True,
                                          (200, 195, 215)), (tx + 2, ly + 20))
        tier = store_catalog.rarity(sid)
        tcol = _TIER_COL.get(tier, (200, 195, 215))
        timg = _font(11, True).render(tier.upper(), True, tcol)
        sheet.blit(timg, (tx + GP_W - timg.get_width() - 2, ly + 21))
    if secret:
        tag = _font(11, True).render("★ SECRET", True, (255, 214, 140))
        sheet.blit(tag, (tx + GP_W - tag.get_width() - 2, ly + 1))


def build_category_figure(scene, group, label) -> str:
    ids = scene._lists[group]
    n = len(ids)
    rows = math.ceil(n / COLS)
    sheet_w = MARGIN * 2 + COLS * TILE_W + (COLS - 1) * GUTTER
    sheet_h = TITLE_H + MARGIN + rows * TILE_H + (rows - 1) * GUTTER + MARGIN
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill(BG)
    pygame.draw.line(sheet, (*_GOLD_DEEP, 255), (MARGIN, 12), (sheet_w - MARGIN, 12), 3)
    title = _font(30, True).render(
        f"{label} — STORE CARD + ON PIP IN GAMEPLAY  ({n})", True, _GOLD_PALE)
    sheet.blit(title, title.get_rect(midtop=(sheet_w // 2, 26)))

    for idx, sid in enumerate(ids):
        col, row = idx % COLS, idx // COLS
        tx = MARGIN + col * (TILE_W + GUTTER)
        ty = TITLE_H + MARGIN + row * (TILE_H + GUTTER)
        _draw_tile(sheet, scene, group, sid, tx, ty)

    out = os.path.join(OUT_DIR, f"{group}.png")
    pygame.image.save(sheet, out)
    print("SAVED", out, sheet.get_size())
    return out


def main():
    orig, tmp_path = _setup_revealed_wallet()
    try:
        scene = StoreScene()
        for g, _label in GROUPS:
            for sid in scene._lists[g]:
                store_data.grant(sid)  # reveal every card (base grants no-op)
        for g, label in GROUPS:
            build_category_figure(scene, g, label)
    finally:
        _restore_wallet(orig, tmp_path)


if __name__ == "__main__":
    main()
