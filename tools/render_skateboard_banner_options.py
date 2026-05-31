"""Comparison sheet of 5 SKATEBOARD! banner placements, each rendered on
the same live gameplay frame with the new (y=70) halftone score already
in place. Output:
    docs/skateboard_banner_options/round_1.png

Run from the repo root:
    python tools/render_skateboard_banner_options.py
"""
import os
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "dummy"

import sys
import random
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

import pygame
pygame.init()
pygame.display.set_mode((360, 640))

from game.config import W, H, SKATEBOARD_DURATION
from game.scenes import App, STATE_PLAY
from game.world import World
from game.skateboard_fx import _gradient_text, INK, PLATE_RED


OUT_DIR = os.path.join(_ROOT, "docs", "skateboard_banner_options")
OUT_PATH = os.path.join(OUT_DIR, "round_1.png")


def _build_gameplay_frame(seed=11, seconds=5.0):
    """Drive a short autopilot sim, activate skateboard, render frame."""
    random.seed(seed)
    app = App()
    if hasattr(app, "_splash_covering"):
        app._splash_covering = False
    w = World()
    w.ready_t = 0.0
    w.flap()
    app.world = w
    app.state = STATE_PLAY
    dt = 1 / 60
    for _ in range(int(seconds / dt)):
        ahead = [p for p in w.pipes if p.x > w.bird.x - 18]
        target = min(ahead, key=lambda p: p.x).gap_y - 12 if ahead else H * 0.45
        if w.bird.y > target:
            w.flap()
        w.update(dt)
        if w.game_over:
            break

    # Activate skateboard so the HUD swaps in the halftone score at y=70.
    w.bird.skateboard_active = True
    w.skateboard_timer = SKATEBOARD_DURATION
    # caption_t controls the halftone score's alpha fade — keep it FULL.
    # Setting it well above the FADE threshold (0.8) holds alpha at 255.
    w.skateboard_caption_t = SKATEBOARD_DURATION
    # Suppress the LIVE banner overlay — we'll draw banner variants ourselves.
    w.skateboard_caption_overlay = None
    # Same for the burst (otherwise we'd see the pickup starburst behind).
    w.skateboard_burst_t = 0.0
    w.skateboard_burst_surface = None
    return app


def _render_base(app):
    """Render a full gameplay frame and return a copy of the screen."""
    app._render()
    return app.screen.copy()


def _plate_banner(text, font_size, rot_deg, pad_x=16, pad_y=8,
                  outline_w=4):
    """Return a tilted SKATEBOARD! plate as a rotated surface."""
    txt = _gradient_text(text, font_size,
                         top_col=(255, 255, 110),
                         bot_col=(255, 180, 10),
                         outline=INK, outline_w=outline_w)
    bw, bh = txt.get_width() + pad_x * 2, txt.get_height() + pad_y * 2
    composite = pygame.Surface((bw + 12, bh + 12), pygame.SRCALPHA)
    ccx = composite.get_width() // 2
    ccy = composite.get_height() // 2
    plate_rect = pygame.Rect(0, 0, bw, bh)
    plate_rect.center = (ccx + 4, ccy + 4)
    pygame.draw.rect(composite, PLATE_RED, plate_rect, border_radius=8)
    pygame.draw.rect(composite, INK, plate_rect, 3, border_radius=8)
    composite.blit(txt, txt.get_rect(center=(ccx, ccy)).topleft)
    return pygame.transform.rotate(composite, rot_deg)


def _corner_slashes(surf, cx, cy, anchors):
    """Pen-style speed slashes from each corner pointing at (cx, cy)."""
    for x0, y0 in anchors:
        for off in range(3):
            dx = (cx - x0) * 0.18
            dy = (cy - y0) * 0.18
            ox = (-1 if x0 < cx else 1) * (off * 8)
            oy = off * 4
            pygame.draw.line(surf, INK,
                             (x0 + ox, y0 + oy),
                             (x0 + ox + dx, y0 + oy + dy), 4)


# ── Variant renderers — each takes a base frame, returns a new surface ─────

def variant_b1_top_thin(base):
    """B1 — Slim banner above the score plate (y=18)."""
    s = base.copy()
    cx, cy = W // 2, 18
    _corner_slashes(s, cx, cy, ((20, 4), (W - 20, 4)))
    banner = _plate_banner("SKATEBOARD!", font_size=26, rot_deg=5,
                           pad_x=12, pad_y=4, outline_w=3)
    s.blit(banner, banner.get_rect(center=(cx, cy)))
    return s


def variant_b2_bottom_edge(base):
    """B2 — Banner at the bottom edge (y=H-50)."""
    s = base.copy()
    cx, cy = W // 2, H - 50
    _corner_slashes(s, cx, cy, ((20, H - 8), (W - 20, H - 8)))
    banner = _plate_banner("SKATEBOARD!", font_size=38, rot_deg=-3)
    s.blit(banner, banner.get_rect(center=(cx, cy)))
    return s


def variant_b3_vertical_left(base):
    """B3 — Banner rotated 90° CCW along the left edge."""
    s = base.copy()
    cx, cy = 22, H // 2
    banner = _plate_banner("SKATEBOARD!", font_size=36, rot_deg=90,
                           pad_x=18, pad_y=8)
    s.blit(banner, banner.get_rect(center=(cx, cy)))
    return s


def variant_b4_diagonal_mid(base):
    """B4 — Dramatic diagonal banner across mid-screen (y=300)."""
    s = base.copy()
    cx, cy = W // 2, 300
    banner = _plate_banner("SKATEBOARD!", font_size=44, rot_deg=-15,
                           pad_x=20, pad_y=10, outline_w=5)
    s.blit(banner, banner.get_rect(center=(cx, cy)))
    return s


def variant_b5_top_right(base):
    """B5 — Small banner parked in the top-right corner (y=30)."""
    s = base.copy()
    cx, cy = W - 78, 30
    _corner_slashes(s, cx, cy, ((W - 20, 4), (20, 4)))
    banner = _plate_banner("SKATEBOARD!", font_size=24, rot_deg=12,
                           pad_x=10, pad_y=4, outline_w=3)
    s.blit(banner, banner.get_rect(center=(cx, cy)))
    return s


VARIANTS = [
    ("B1 — Top thin (above score)", variant_b1_top_thin),
    ("B2 — Bottom edge",            variant_b2_bottom_edge),
    ("B3 — Vertical left",          variant_b3_vertical_left),
    ("B4 — Diagonal mid-screen",    variant_b4_diagonal_mid),
    ("B5 — Top-right corner",       variant_b5_top_right),
]


def _compose_sheet(cells):
    """2x3 grid (5 cells + 1 spare). Each cell shows the rendered frame
    with a label strip below. Cell = W × (H + 36); margins = 16 px."""
    pygame.font.init()
    font = pygame.font.SysFont(None, 22)
    margin = 16
    label_h = 36
    cell_w = W + margin
    cell_h = H + label_h + margin
    cols, rows = 3, 2
    sheet_w = margin + cell_w * cols
    sheet_h = margin + cell_h * rows + 50  # +50 for title
    sheet = pygame.Surface((sheet_w, sheet_h), pygame.SRCALPHA)
    sheet.fill((26, 30, 36, 255))

    # Title
    title = pygame.font.SysFont(None, 30).render(
        "Skybit — SKATEBOARD! banner placement options "
        "(score now at y=70 to match the regular NA plate)",
        True, (245, 240, 220))
    sheet.blit(title, (margin, 14))

    for idx, (label, frame) in enumerate(cells):
        col = idx % cols
        row = idx // cols
        x0 = margin + col * cell_w
        y0 = margin + 40 + row * cell_h
        sheet.blit(frame, (x0, y0))
        pygame.draw.rect(sheet, (90, 110, 130),
                         (x0, y0, W, H), width=1)
        lbl = font.render(label, True, (235, 230, 210))
        sheet.blit(lbl, (x0, y0 + H + 6))
    return sheet


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    print("building gameplay base frame...")
    app = _build_gameplay_frame()
    base = _render_base(app)

    cells = []
    for label, renderer in VARIANTS:
        cells.append((label, renderer(base)))
        print(f"  rendered {label}")

    sheet = _compose_sheet(cells)
    pygame.image.save(sheet, OUT_PATH)
    print(f"wrote {OUT_PATH}  ({os.path.getsize(OUT_PATH)} bytes)")


if __name__ == "__main__":
    main()
