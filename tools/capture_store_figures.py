"""Two combined review figures for the COSTUME store category.

  1. store_overview.png  — the real store COSTUMES tab, every page side by side
                           (pixel-faithful App._render captures, composed).
  2. gameplay_items.png  — each costume on Pip mid-flight over a real biome
                           scene, in one labeled grid.

Pure capture, no production art touched. Run headless from repo root:
``SDL_VIDEODRIVER=dummy python tools/capture_store_figures.py``.
"""
from __future__ import annotations
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import sys
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

import pygame
pygame.init()

from game import parrot, biome, store_catalog
from game.scenes import App, STATE_STORE
from game.store import StoreScene
from game.hud import _font, _GOLD_PALE, _GOLD_DEEP
from game.draw import get_sky_surface_biome, draw_mountains, draw_ground, draw_cloud
from game.entities import Pipe
from game.config import W as GW, H as GH, GROUND_Y

OUT_DIR = os.path.join(_ROOT, "docs", "store_redesign", "costume")
os.makedirs(OUT_DIR, exist_ok=True)

COSTUMES = store_catalog.ids_of_group("costume")
GAME_FRAME_IDX = 2
GAME_TILT = 10.0


# ── Figure 1: real store pages, composed ─────────────────────────────────────
def render_store_pages() -> list[pygame.Surface]:
    app = App()
    app._cooldown_t = 0.0
    app._fetch_pending = False
    app.store = StoreScene()
    app.state = STATE_STORE
    app.store.tab = 0          # COSTUMES
    pages = []
    for p in range(app.store.n_pages):
        app.store.page = p
        app.store.update(0.0)
        app._render()
        pages.append(app.screen.copy())
    return pages


def build_store_overview() -> str:
    pages = render_store_pages()
    pw, ph = pages[0].get_size()
    n = len(pages)
    MARGIN, GUTTER, TITLE_H = 30, 26, 70
    sheet_w = MARGIN * 2 + n * pw + (n - 1) * GUTTER
    sheet_h = TITLE_H + MARGIN + ph + MARGIN
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((18, 16, 28))
    title = _font(30, True).render("COSTUMES — STORE TAB (all pages)", True, _GOLD_PALE)
    sheet.blit(title, title.get_rect(midtop=(sheet_w // 2, 20)))
    for i, pg in enumerate(pages):
        x = MARGIN + i * (pw + GUTTER)
        y = TITLE_H + MARGIN
        pygame.draw.rect(sheet, (*_GOLD_DEEP, 255),
                         pygame.Rect(x - 2, y - 2, pw + 4, ph + 4), width=2)
        sheet.blit(pg, (x, y))
        cap = _font(14, True).render(f"PAGE {i + 1} / {n}", True, (180, 172, 200))
        sheet.blit(cap, cap.get_rect(midtop=(x + pw // 2, y + ph + 6)))
    out = os.path.join(OUT_DIR, "store_overview.png")
    pygame.image.save(sheet, out)
    print("SAVED", out, sheet.get_size())
    return out


# ── Figure 2: each costume on Pip in gameplay ────────────────────────────────
def gameplay_panel(sid: str, w: int, h: int) -> pygame.Surface:
    scene = pygame.Surface((GW, GH))
    palette = biome.palette_for_phase(0.0)
    scene.blit(get_sky_surface_biome(GW, GH, GROUND_Y, palette, 0), (0, 0))
    for bx, by, sc, variant in ((40, 90, 0.9, 0), (200, 130, 1.1, 2), (300, 70, 0.7, 1)):
        draw_cloud(scene, bx, by, sc, variant=variant)
    draw_mountains(scene, 40.0, GROUND_Y, GW, palette['mtn_far'], palette['mtn_near'])
    Pipe(x=12, gap_y=250, gap_h=185).draw(scene, palette)
    Pipe(x=200, gap_y=300, gap_h=170).draw(scene, palette)
    draw_ground(scene, GROUND_Y, GW, GH, 40.0,
                palette['ground_top'], palette['ground_mid'], (60, 40, 25))
    pip_cx, pip_cy = 96, 270
    frame = parrot.get_skin_frame(sid, GAME_FRAME_IDX, GAME_TILT)
    scene.blit(frame, frame.get_rect(center=(pip_cx, pip_cy)))
    crop_h = int(GH * 0.78)
    crop_w = int(crop_h * w / h)
    crop = pygame.Rect(0, 0, crop_w, crop_h)
    crop.center = (pip_cx + 34, pip_cy - 20)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    return pygame.transform.smoothscale(scene.subsurface(crop).copy(), (w, h))


def build_gameplay_items() -> str:
    COLS, ROWS = 5, 3
    GW_, GH_ = 196, 348
    LABEL_H, MARGIN, GUTTER, TITLE_H = 50, 34, 28, 78
    CELL_W, CELL_H = GW_, GH_ + LABEL_H
    sheet_w = MARGIN * 2 + COLS * CELL_W + (COLS - 1) * GUTTER
    sheet_h = TITLE_H + MARGIN + ROWS * CELL_H + (ROWS - 1) * GUTTER + MARGIN
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((18, 16, 28))
    title = _font(30, True).render("COSTUMES — ON PIP IN GAMEPLAY", True, _GOLD_PALE)
    sheet.blit(title, title.get_rect(midtop=(sheet_w // 2, 22)))
    label_font, cost_font = _font(16, True), _font(13, True)
    for idx, sid in enumerate(COSTUMES):
        col, row = idx % COLS, idx // COLS
        cx = MARGIN + col * (CELL_W + GUTTER)
        cy = TITLE_H + MARGIN + row * (CELL_H + GUTTER)
        gp = gameplay_panel(sid, GW_, GH_)
        pygame.draw.rect(sheet, (*_GOLD_DEEP, 255),
                         pygame.Rect(cx - 2, cy - 2, GW_ + 4, GH_ + 4), width=2)
        sheet.blit(gp, (cx, cy))
        ly = cy + GH_ + 7
        sheet.blit(label_font.render(store_catalog.name(sid), True, _GOLD_PALE), (cx + 2, ly))
        sheet.blit(cost_font.render(f"{store_catalog.cost(sid)} coins", True,
                                    (200, 195, 215)), (cx + 2, ly + 21))
    out = os.path.join(OUT_DIR, "gameplay_items.png")
    pygame.image.save(sheet, out)
    print("SAVED", out, sheet.get_size())
    return out


if __name__ == "__main__":
    build_store_overview()
    build_gameplay_items()
