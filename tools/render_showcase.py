"""Phase 5 showcase — item-card redesign.

Composites BEFORE + 5 round-2 concept cards into a single labeled gallery image.
Layout: 2 rows × 3 panels, each card at 2× (324×200), with header + footer.
Never displays, views, or reads PNGs — PIL validation only.
"""
import os
import sys
import importlib.util

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from game import store_cards
from game.animal_kitsune import build_kitsune, build_kitsune_aura

# ── layout constants ───────────────────────────────────────────────────────────
PW, PH   = 324, 200        # panel card area (2× card size)
HEADER   = 40              # px above card for title
FOOTER   = 32              # px below card for slug + verdict
MARGIN   = 20
GAP_X    = 8               # horizontal gap between panels
GAP_Y    = 14              # vertical gap between rows
COLS     = 3
ROWS     = 2

BG = (8, 8, 20)
TITLE_COL   = (220, 220, 240)
SLUG_COL    = (180, 180, 210)
VERDICT_COL = (120, 220, 120)    # green for FINAL
BEFORE_COL  = (180, 160, 120)    # warm for BEFORE

TOTAL_W = MARGIN + COLS * PW + (COLS - 1) * GAP_X + MARGIN
TOTAL_H = (MARGIN
           + ROWS * (HEADER + PH + FOOTER)
           + (ROWS - 1) * GAP_Y
           + MARGIN)


def _load_font(size):
    return pygame.font.SysFont("DejaVu Sans", size)


def _render_before():
    """Render the live kitsune card from store_cards and smoothscale to 2×."""
    card_1x = store_cards.render_card("skin_kitsune", equipped=False, owned=True)
    return pygame.transform.smoothscale(card_1x, (PW, PH))


def _load_concept(path, fn_name):
    """Import a render script by path and call its build/render function."""
    mod_name = os.path.basename(path).replace(".py", "")
    spec = importlib.util.spec_from_file_location(mod_name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    card_big = getattr(mod, fn_name)()
    return pygame.transform.smoothscale(card_big, (PW, PH))


def _draw_panel(canvas, card, title, slug, verdict, col, row):
    x0 = MARGIN + col * (PW + GAP_X)
    y0 = MARGIN + row * (HEADER + PH + FOOTER + GAP_Y)

    # header
    tfont = _load_font(13)
    title_surf = tfont.render(title, True, TITLE_COL if row or col else BEFORE_COL)
    canvas.blit(title_surf, (x0 + (PW - title_surf.get_width()) // 2,
                              y0 + (HEADER - title_surf.get_height()) // 2))

    # card
    canvas.blit(card, (x0, y0 + HEADER))

    # thin border around card
    pygame.draw.rect(canvas, (50, 50, 80),
                     (x0, y0 + HEADER, PW, PH), 1)

    # footer: slug + verdict
    sfont = _load_font(11)
    slug_s = sfont.render(slug, True, SLUG_COL)
    ver_s  = sfont.render(verdict, True, VERDICT_COL)
    fy = y0 + HEADER + PH + (FOOTER - slug_s.get_height()) // 2
    canvas.blit(slug_s, (x0 + 6, fy))
    canvas.blit(ver_s, (x0 + PW - ver_s.get_width() - 6, fy))


PANELS = [
    # (path, fn, title, slug, verdict) — row-major order
    (None,                                      None,          "BEFORE — CONSTELLATION",   "current card",      ""),
    ("tools/render_torn_reveal_r2.py",          "render_torn_reveal",  "TORN REVEAL",      "torn-reveal",       "FINAL"),
    ("tools/render_gemstone_core_r2.py",        "build_card",  "GEMSTONE CORE",            "gemstone-core",     "FINAL"),
    ("tools/render_specimen_jar_r2.py",         "build_card",  "SPECIMEN JAR",             "specimen-jar",      "FINAL"),
    ("tools/render_depth_gate_r2.py",           "render_big",  "DEPTH GATE",               "depth-gate",        "FINAL"),
    ("tools/render_constellation_window_r2.py", "build_card",  "CONSTELLATION WINDOW",     "constellation-window", "FINAL"),
]


def main():
    canvas = pygame.Surface((TOTAL_W, TOTAL_H))
    canvas.fill(BG)

    for idx, (path, fn, title, slug, verdict) in enumerate(PANELS):
        col = idx % COLS
        row = idx // COLS
        if path is None:
            card = _render_before()
        else:
            card = _load_concept(path, fn)
        _draw_panel(canvas, card, title, slug, verdict, col, row)

    out = "docs/item_card_redesign/showcase.png"
    pygame.image.save(canvas, out)
    print(f"saved: {out}  size={canvas.get_size()}")

    # PIL validation — never display
    from PIL import Image
    img = Image.open(out)
    arr = img.load()
    w, h = img.size
    distinct = len(set(img.getdata()))
    import os as _os
    size_bytes = _os.path.getsize(out)
    print(f"PIL: {w}×{h}, {distinct} distinct colors, {size_bytes} bytes")
    assert w > 100 and h > 100, "canvas looks blank"
    assert distinct > 100, "too few colors — likely blank"
    print("validation OK")


if __name__ == "__main__":
    main()
