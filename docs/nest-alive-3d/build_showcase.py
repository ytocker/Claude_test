"""Phase 5 showcase — alive-nest 3D layering concepts.

One BEFORE panel + five concept AFTER panels, each 200×355 px.
Crop: Rect(8, 15, 46, 74) in the native 70×100 draw surface at cy=73,
scaled to 200×323 content area + 32 px slug/verdict footer.
"""
import os, sys, math, importlib.util
os.environ.setdefault('SDL_VIDEODRIVER', 'offscreen')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
sys.path.insert(0, '/home/user/skybit')
import pygame
pygame.init()

FEATURE_DIR = os.path.dirname(os.path.abspath(__file__))
SKY       = (136, 183, 197)
BG        = (8,   8,  20)
TXT_LIGHT = (210, 205, 190)
TXT_GOLD  = (255, 214, 120)
TXT_DIM   = (140, 135, 125)

PANEL_W   = 200
PANEL_H   = 355
FOOTER_H  = 32
CONTENT_H = PANEL_H - FOOTER_H          # 323

# Native draw surface and the crop that maps to 200×323
NATIVE_W  = 70
NATIVE_H  = 100
NEST_CY   = 73
CROP      = pygame.Rect(8, 15, 46, 74)  # approx. bird-head → weave bottom

GAP       = 8
MARGIN    = 20
HEADER_H  = 40


def _load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _render_native(draw_fn, cy=NEST_CY, alive=True):
    s = pygame.Surface((NATIVE_W, NATIVE_H))
    s.fill(SKY)
    draw_fn(s, cy, alive)
    return s


def _make_panel(draw_fn, slug, footer_line1, footer_line2=None, alive=True):
    native   = _render_native(draw_fn, alive=alive)
    cropped  = native.subsurface(CROP).copy()
    content  = pygame.transform.scale(cropped, (PANEL_W, CONTENT_H))

    panel = pygame.Surface((PANEL_W, PANEL_H))
    panel.fill(BG)
    panel.blit(content, (0, 0))

    # Separator between content and footer
    pygame.draw.line(panel, (40, 40, 55),
                     (0, CONTENT_H), (PANEL_W - 1, CONTENT_H))

    font_lg = pygame.font.SysFont('dejavusans', 11, bold=True)
    font_sm = pygame.font.SysFont('dejavusans', 10)

    t1 = font_lg.render(footer_line1, True, TXT_GOLD)
    panel.blit(t1, ((PANEL_W - t1.get_width()) // 2, CONTENT_H + 5))
    if footer_line2:
        t2 = font_sm.render(footer_line2, True, TXT_DIM)
        panel.blit(t2, ((PANEL_W - t2.get_width()) // 2, CONTENT_H + 19))

    return panel


# ── Load all concept modules ──────────────────────────────────────────────────

CONCEPTS = [
    ('split-shell-rim',   'render.py',    'split-shell-rim',    'FINAL'),
    ('woven-stencil-tuck','render_r2.py', 'woven-stencil-tuck', 'FINAL'),
    ('loose-twig-veil',   'render_r2.py', 'loose-twig-veil',    'FINAL'),
    ('sunken-shadow-well','render_r2.py', 'sunken-shadow-well', 'FINAL'),
    ('braided-lip-roll',  'render_r2.py', 'braided-lip-roll',   'FINAL'),
]

# Load reference module for draw_slot_before (any concept works; they're identical)
_ref_mod = _load_module(
    os.path.join(FEATURE_DIR, 'split-shell-rim', 'render.py'), 'ref')

panels = []

# BEFORE panel
panels.append(_make_panel(
    _ref_mod.draw_slot_before, 'before', 'BEFORE', '(today / alive)'))

# Concept panels
for slug, script, label, verdict in CONCEPTS:
    path = os.path.join(FEATURE_DIR, slug, script)
    mod  = _load_module(path, slug.replace('-', '_'))
    panels.append(_make_panel(mod.draw_slot_after, slug, label, verdict))

# ── Composite ────────────────────────────────────────────────────────────────

n   = len(panels)                              # 6
W   = 2 * MARGIN + n * PANEL_W + (n - 1) * GAP
H   = 2 * MARGIN + HEADER_H + PANEL_H

canvas = pygame.Surface((W, H))
canvas.fill(BG)

font_title = pygame.font.SysFont('dejavusans', 14, bold=True)
title = font_title.render(
    'alive-nest 3D layering  —  concept review  (round 2)',
    True, TXT_LIGHT)
canvas.blit(title, (MARGIN, MARGIN + (HEADER_H - title.get_height()) // 2))

x_off = MARGIN
y_off = MARGIN + HEADER_H
for p in panels:
    canvas.blit(p, (x_off, y_off))
    x_off += PANEL_W + GAP

out_path = os.path.join(FEATURE_DIR, 'showcase.png')
pygame.image.save(canvas, out_path)
print(f'saved  {out_path}  {canvas.get_size()}')
pygame.quit()
