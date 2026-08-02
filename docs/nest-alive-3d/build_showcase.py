"""Phase 5 showcase — alive-nest 3D layering concepts.

Two rows of panels, each 200×355 px:
  Row 1 (parrot IN / alive):  BEFORE + 5 concepts
  Row 2 (parrot OUT / empty): BEFORE + 5 concepts
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
    ('split-shell-rim',   'render.py',    'split-shell-rim'),
    ('woven-stencil-tuck','render_r2.py', 'woven-stencil-tuck'),
    ('loose-twig-veil',   'render_r2.py', 'loose-twig-veil'),
    ('sunken-shadow-well','render_r2.py', 'sunken-shadow-well'),
    ('braided-lip-roll',  'render_r2.py', 'braided-lip-roll'),
]

# Load reference module for draw_slot_before (identical across all concepts)
_ref_mod = _load_module(
    os.path.join(FEATURE_DIR, 'split-shell-rim', 'render.py'), 'ref')

# Build concept modules list (keeps modules alive so garbage collector
# doesn't free their internal state between the two row renders)
concept_mods = []
for slug, script, label in CONCEPTS:
    path = os.path.join(FEATURE_DIR, slug, script)
    concept_mods.append((label, _load_module(path, slug.replace('-', '_'))))

ROW_LABEL_H = 24     # row heading above each row

def _build_row(alive, row_label):
    """Return a Surface of one full row (6 panels side-by-side) + heading."""
    row_w = 6 * PANEL_W + 5 * GAP
    row_h = ROW_LABEL_H + PANEL_H
    row   = pygame.Surface((row_w, row_h))
    row.fill(BG)

    font_row = pygame.font.SysFont('dejavusans', 12, bold=True)
    lbl = font_row.render(row_label, True, TXT_LIGHT)
    row.blit(lbl, (0, (ROW_LABEL_H - lbl.get_height()) // 2))

    x = 0
    # BEFORE panel (today)
    slug_lbl = 'BEFORE' if alive else 'BEFORE (empty)'
    row.blit(
        _make_panel(_ref_mod.draw_slot_before, 'BEFORE',
                    slug_lbl, '(today)', alive=alive),
        (x, ROW_LABEL_H))
    x += PANEL_W + GAP

    for label, mod in concept_mods:
        row.blit(
            _make_panel(mod.draw_slot_after, label, label, 'FINAL', alive=alive),
            (x, ROW_LABEL_H))
        x += PANEL_W + GAP

    return row

row_alive = _build_row(True,  'ROW 1 — parrot IN  (alive)')
row_empty = _build_row(False, 'ROW 2 — parrot OUT (empty)')

ROW_GAP = 16

# ── Composite ────────────────────────────────────────────────────────────────

n   = 6
W   = 2 * MARGIN + n * PANEL_W + (n - 1) * GAP
H   = (2 * MARGIN + HEADER_H
       + row_alive.get_height() + ROW_GAP + row_empty.get_height())

canvas = pygame.Surface((W, H))
canvas.fill(BG)

font_title = pygame.font.SysFont('dejavusans', 14, bold=True)
title = font_title.render(
    'alive-nest 3D layering  —  concept review  (round 2)',
    True, TXT_LIGHT)
canvas.blit(title, (MARGIN, MARGIN + (HEADER_H - title.get_height()) // 2))

y = MARGIN + HEADER_H
canvas.blit(row_alive, (MARGIN, y))
y += row_alive.get_height() + ROW_GAP
canvas.blit(row_empty, (MARGIN, y))

out_path = os.path.join(FEATURE_DIR, 'showcase.png')
pygame.image.save(canvas, out_path)
print(f'saved  {out_path}  {canvas.get_size()}')
pygame.quit()
