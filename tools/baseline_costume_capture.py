"""Headless baseline-reference capture for the COSTUME store group.

Renders, per item, a STORE shot (the store's own cropped thumbnail on a
store-style card) beside a GAMEPLAY shot (Pip wearing the costume composited
over a real biome background with pillars + ground), so the user can judge
the existing art before deciding what to redesign. Pure capture — touches no
production art. Run headless with SDL_VIDEODRIVER=dummy.
"""
from __future__ import annotations
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
pygame.init()

from game import parrot, biome, store_catalog
from game import store as store_mod
from game.hud import _font, _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP
from game.draw import get_sky_surface_biome, draw_mountains, draw_ground, draw_cloud
from game.entities import Pipe
from game.config import W as GW, H as GH, GROUND_Y

# 15 costume ids in catalog order.
COSTUMES = store_catalog.ids_of_group("costume")

# Representative mid-flight pose: a mid-flap frame, slight downward tilt.
GAME_FRAME_IDX = 2
GAME_TILT = 10.0

fallbacks: list[str] = []


def store_panel(sid: str, box: int) -> pygame.Surface:
    """A store-card-styled panel showing the item exactly as the store renders
    its thumbnail (cropped-to-content via the store's own _fit_skin)."""
    panel = pygame.Surface((box, box), pygame.SRCALPHA)
    # Card chrome modelled on the store's gold-rimmed dark card.
    pygame.draw.rect(panel, (26, 22, 40), panel.get_rect(), border_radius=14)
    pygame.draw.rect(panel, (44, 36, 60), panel.get_rect().inflate(-6, -6),
                     border_radius=11)
    pygame.draw.rect(panel, (*_GOLD_BRIGHT, 200), panel.get_rect(),
                     width=2, border_radius=14)
    thumb = store_mod._fit_skin(sid, int(box * 0.74))
    panel.blit(thumb, thumb.get_rect(center=(box // 2, box // 2)))
    return panel


def gameplay_panel(sid: str, w: int, h: int) -> pygame.Surface:
    """Pip wearing the costume over a real biome scene (sky + clouds +
    mountains + two pillars + ground), reusing the in-game draw helpers."""
    scene = pygame.Surface((GW, GH))

    # Daytime biome so the costumes read against the canonical sky.
    phase = 0.0
    palette = biome.palette_for_phase(phase)
    sky = get_sky_surface_biome(GW, GH, GROUND_Y, palette, 0)
    scene.blit(sky, (0, 0))

    scroll = 40.0
    for i, (bx, by, sc, variant) in enumerate((
            (40, 90, 0.9, 0), (200, 130, 1.1, 2), (300, 70, 0.7, 1))):
        draw_cloud(scene, bx, by, sc, variant=variant)
    draw_mountains(scene, scroll, GROUND_Y, GW,
                   palette['mtn_far'], palette['mtn_near'])

    # Two pillars framing Pip the way the real run does.
    p1 = Pipe(x=200, gap_y=300, gap_h=170)
    p2 = Pipe(x=12, gap_y=250, gap_h=185)
    p2.draw(scene, palette)
    p1.draw(scene, palette)

    draw_ground(scene, GROUND_Y, GW, GH, scroll,
                palette['ground_top'], palette['ground_mid'], (60, 40, 25))

    # Pip mid-flight, at gameplay scale, where the bird actually flies.
    pip_cx, pip_cy = 96, 270
    frame = parrot.get_skin_frame(sid, GAME_FRAME_IDX, GAME_TILT)
    fr = frame.get_rect(center=(pip_cx, pip_cy))
    scene.blit(frame, fr)

    # Crop to a panel-aspect window around Pip so the costume reads large while
    # keeping real gameplay context (pillars + ground band) in shot.
    crop_h = int(GH * 0.78)
    crop_w = int(crop_h * w / h)
    crop = pygame.Rect(0, 0, crop_w, crop_h)
    crop.center = (pip_cx + 34, pip_cy - 20)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    view = scene.subsurface(crop).copy()
    return pygame.transform.smoothscale(view, (w, h))


# Detect skins that silently fell back to the base parrot.
_base_ref = parrot.get_skin_frame(store_catalog.BASE_SKIN, GAME_FRAME_IDX, GAME_TILT)
_base_bytes = pygame.image.tostring(_base_ref, "RGBA")
for sid in COSTUMES:
    fr = parrot.get_skin_frame(sid, GAME_FRAME_IDX, GAME_TILT)
    if fr.get_size() == _base_ref.get_size() and \
            pygame.image.tostring(fr, "RGBA") == _base_bytes:
        fallbacks.append(sid)

# ── grid layout: 3 columns x 5 rows of cells, each = store + gameplay + label ─
COLS, ROWS = 3, 5
STORE_BOX = 210
GAME_W, GAME_H = 200, 356       # keeps the 360x640 aspect of the gameplay shot
PAD = 22
LABEL_H = 54
CELL_W = STORE_BOX + GAME_W + PAD
CELL_H = max(STORE_BOX, GAME_H) + LABEL_H
MARGIN = 34
GUTTER = 32
TITLE_H = 86

sheet_w = MARGIN * 2 + COLS * CELL_W + (COLS - 1) * GUTTER
sheet_h = TITLE_H + MARGIN + ROWS * CELL_H + (ROWS - 1) * GUTTER + MARGIN

sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((18, 16, 28))

title = _font(30, True).render("COSTUME GROUP — BASELINE REFERENCE", True, _GOLD_PALE)
sheet.blit(title, title.get_rect(midtop=(sheet_w // 2, 18)))
sub = _font(14, True).render(
    "store thumbnail  +  in-game mid-flight  (current art, no redesign)",
    True, (170, 160, 190))
sheet.blit(sub, sub.get_rect(midtop=(sheet_w // 2, 48)))

label_font = _font(16, True)
cost_font = _font(13, True)

for idx, sid in enumerate(COSTUMES):
    col = idx % COLS
    row = idx // COLS
    cx = MARGIN + col * (CELL_W + GUTTER)
    cy = TITLE_H + MARGIN + row * (CELL_H + GUTTER)

    # cell backing
    cell_rect = pygame.Rect(cx - 6, cy - 6, CELL_W + 12, CELL_H + 12)
    pygame.draw.rect(sheet, (30, 26, 44), cell_rect, border_radius=10)

    sp = store_panel(sid, STORE_BOX)
    sheet.blit(sp, (cx, cy + (max(STORE_BOX, GAME_H) - STORE_BOX) // 2))

    gp = gameplay_panel(sid, GAME_W, GAME_H)
    gx = cx + STORE_BOX + PAD
    pygame.draw.rect(sheet, (*_GOLD_DEEP, 255),
                     pygame.Rect(gx - 2, cy - 2, GAME_W + 4, GAME_H + 4),
                     width=2, border_radius=4)
    sheet.blit(gp, (gx, cy))

    name = store_catalog.name(sid)
    cost = store_catalog.cost(sid)
    ly = cy + max(STORE_BOX, GAME_H) + 6
    nimg = label_font.render(name, True, _GOLD_PALE)
    sheet.blit(nimg, (cx + 4, ly))
    cimg = cost_font.render(f"{cost} coins", True, (200, 195, 215))
    sheet.blit(cimg, (cx + 4, ly + 20))
    # mini caption for the two panels
    s_cap = cost_font.render("STORE", True, (140, 132, 160))
    g_cap = cost_font.render("IN-GAME", True, (140, 132, 160))
    sheet.blit(s_cap, (cx + STORE_BOX - s_cap.get_width(), ly))
    sheet.blit(g_cap, (gx + GAME_W - g_cap.get_width(), ly))

out_dir = os.path.join("docs", "store_redesign", "costume")
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "baseline.png")
pygame.image.save(sheet, out_path)

print("SAVED", out_path, sheet.get_size())
print("FALLBACKS", fallbacks)
