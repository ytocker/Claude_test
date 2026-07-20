#!/usr/bin/env python3
"""
Name-rendering verification — all 6 cases from the line-break overflow fix.

Exercises the live _draw_confirm from game/store.py with 6 test names, one
per code path, and composes them into a single comparison figure.
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

from PIL import Image
import game.store as store_mod
import game.store_cards as sc
import game.store_data as sd
from game.config import W, H

# ── Test cases ─────────────────────────────────────────────────────────────────

PANELS = [
    {
        "id":    "A",
        "name":  "MUMMY",
        "label": "SHORT · font 33",
        "note":  "5 chars — boosted to f33",
        "flag":  "OK",
    },
    {
        "id":    "B",
        "name":  "MEGA DAD",
        "label": "MED · font-30 guard",
        "note":  "8c / f30=323 / f33=357 — guard fires",
        "flag":  "OK",
    },
    {
        "id":    "C",
        "name":  "TEMPEST CONDOR",
        "label": "LONG · space split",
        "note":  "14c — \"TEMPEST\" / \"CONDOR\"",
        "flag":  "OK",
    },
    {
        "id":    "D",
        "name":  "BASKETBALL",
        "label": "LONG · hyphen",
        "note":  "10c no space — \"BASKE-\" / \"TBALL\"",
        "flag":  "OK",
    },
    {
        "id":    "E",
        "name":  "FLIP-FLOPS",
        "label": "LONG · hyphen (embedded -)",
        "note":  "10c embedded hyphen — \"FLIP-F-\" / \"LOPS\"",
        "flag":  "FIXED",
    },
    {
        "id":    "F",
        "name":  "3D GLASSES",
        "label": "LONG · lopsided split",
        "note":  "10c — \"3D\" / \"GLASSES\"",
        "flag":  "EDGE",
    },
]

# All panels use skin_tempest (epic tier) — hardest test for text contrast.
_SID = "skin_tempest"

# Popup occupies (px, py) to (px+200, py+340) on a W×H screen.
_POP_X = (W - 200) // 2   # 80
_POP_Y = (H - 340) // 2   # 150

# ── Render one popup and return a 200×340 PIL image ───────────────────────────

def _render_panel(name):
    scene = store_mod.StoreScene.__new__(store_mod.StoreScene)
    scene._confirm       = _SID
    scene._confirm_panel = None
    scene.confirm_yes_rect = scene.confirm_no_rect = None
    scene._disp_name = lambda sid, _n=name: _n

    _orig_balance = sd.balance
    sd.balance = lambda: 99999

    surf = pygame.Surface((W, H))
    surf.fill((0, 0, 0))
    scene._draw_confirm(surf)

    sd.balance = _orig_balance

    raw = pygame.image.tostring(surf, "RGB")
    img = Image.frombytes("RGB", (W, H), raw)
    return img.crop((_POP_X, _POP_Y, _POP_X + 200, _POP_Y + 340))

# ── Canvas layout ─────────────────────────────────────────────────────────────

N        = len(PANELS)
PANEL_W  = 200
PANEL_H  = 340
MARGIN   = 18
GAP      = 8
HDR_H    = 36
FOOT_H   = 46

BG       = (8, 8, 20)
CREAM    = (252, 246, 228)
DIM      = (150, 146, 170)
BORDER   = (40, 38, 60)
BADGE_BG = (24, 22, 38)
GREEN    = (80, 210, 120)
YELLOW   = (230, 200, 80)
RED_COL  = (210, 90, 80)

CANVAS_W = MARGIN + N * PANEL_W + (N - 1) * GAP + MARGIN
CANVAS_H = MARGIN + HDR_H + GAP + PANEL_H + FOOT_H + MARGIN

BASE_DIR = os.path.join(os.path.dirname(__file__), "..",
                        "docs", "store_confirm_popup_v4", "long-name")
OUT      = os.path.join(BASE_DIR, "verify.png")

# ── Helpers ───────────────────────────────────────────────────────────────────

def _pil_to_surf(img):
    rgb = img.convert("RGB")
    return pygame.image.fromstring(rgb.tobytes(), rgb.size, "RGB")


def _badge(font, label):
    txt  = font.render(label, True, CREAM)
    ph, pv = 5, 3
    w = txt.get_width() + ph * 2
    h = txt.get_height() + pv * 2
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    s.fill((0, 0, 0, 0))
    pygame.draw.rect(s, (*BADGE_BG, 220), (0, 0, w, h), border_radius=4)
    s.blit(txt, (ph, pv))
    return s

# ── Build canvas ──────────────────────────────────────────────────────────────

canvas = pygame.Surface((CANVAS_W, CANVAS_H))
canvas.fill(BG)

f_hdr   = pygame.font.Font(None, 22)
f_badge = pygame.font.Font(None, 22)
f_lbl   = pygame.font.Font(None, 16)
f_note  = pygame.font.Font(None, 14)

hdr = f_hdr.render(
    "NAME RENDERING VERIFICATION  ·  all 6 cases  ·  live _draw_confirm",
    True, (190, 186, 220))
canvas.blit(hdr, hdr.get_rect(midtop=(CANVAS_W // 2, MARGIN + 6)))

panel_top = MARGIN + HDR_H + GAP

FLAG_COLORS = {"OK": GREEN, "FIXED": GREEN, "EDGE": YELLOW, "BUG": RED_COL}

for i, p in enumerate(PANELS):
    x0   = MARGIN + i * (PANEL_W + GAP)
    img  = _render_panel(p["name"])
    surf = _pil_to_surf(img)
    canvas.blit(surf, (x0, panel_top))

    pygame.draw.rect(canvas, BORDER,
                     (x0 - 1, panel_top - 1, PANEL_W + 2, PANEL_H + 2), width=1)

    badge = _badge(f_badge, p["id"])
    canvas.blit(badge, (x0 + 6, panel_top + 6))

    # Flag chip top-right
    flag_col = FLAG_COLORS.get(p["flag"], DIM)
    fc = f_note.render(p["flag"], True, flag_col)
    canvas.blit(fc, fc.get_rect(topright=(x0 + PANEL_W - 6, panel_top + 9)))

    # Footer
    cx = x0 + PANEL_W // 2
    fy = panel_top + PANEL_H + 5
    lbl  = f_lbl.render(p["label"],  True, CREAM)
    note = f_note.render(p["note"],  True, DIM)
    name = f_note.render(p["name"],  True, (130, 126, 150))
    canvas.blit(lbl,  lbl.get_rect(midtop=(cx, fy)))
    canvas.blit(note, note.get_rect(midtop=(cx, fy + 16)))
    canvas.blit(name, name.get_rect(midtop=(cx, fy + 30)))

    print(f"  {p['id']}  {p['name']:<16}  [{p['flag']}]")

pygame.image.save(canvas, OUT)
w, h = canvas.get_size()
print(f"\nSaved  {OUT}  ({w}×{h})")
