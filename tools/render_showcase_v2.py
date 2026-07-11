"""Phase 5 v2 showcase — item-card redesign round 2.

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

# ── layout constants ───────────────────────────────────────────────────────────
PW, PH   = 324, 200        # panel card area (2× card size)
HEADER   = 40              # px above card for title
FOOTER   = 32              # px below card for slug + verdict
MARGIN   = 20
GAP_X    = 8
GAP_Y    = 14
COLS     = 3
ROWS     = 2

BG = (8, 8, 20)
TITLE_COL   = (220, 220, 240)
SLUG_COL    = (180, 180, 210)
VERDICT_COL = (120, 220, 120)
BEFORE_COL  = (180, 160, 120)

TOTAL_W = MARGIN + COLS * PW + (COLS - 1) * GAP_X + MARGIN
TOTAL_H = (MARGIN
           + ROWS * (HEADER + PH + FOOTER)
           + (ROWS - 1) * GAP_Y
           + MARGIN)


def _load_font(size):
    return pygame.font.SysFont("DejaVu Sans", size)


def _render_before():
    card_1x = store_cards.render_card("skin_kitsune", equipped=False, owned=True)
    return pygame.transform.smoothscale(card_1x, (PW, PH))


def _load_concept(path, fn_name, fn_args=(), fn_kwargs=None):
    if fn_kwargs is None:
        fn_kwargs = {}
    mod_name = os.path.basename(path).replace(".py", "")
    spec = importlib.util.spec_from_file_location(mod_name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    card_big = getattr(mod, fn_name)(*fn_args, **fn_kwargs)
    return pygame.transform.smoothscale(card_big, (PW, PH))


def _draw_panel(canvas, card, title, slug, verdict, col, row):
    x0 = MARGIN + col * (PW + GAP_X)
    y0 = MARGIN + row * (HEADER + PH + FOOTER + GAP_Y)

    tfont = _load_font(13)
    title_surf = tfont.render(title, True, TITLE_COL if row or col else BEFORE_COL)
    canvas.blit(title_surf, (x0 + (PW - title_surf.get_width()) // 2,
                              y0 + (HEADER - title_surf.get_height()) // 2))

    canvas.blit(card, (x0, y0 + HEADER))
    pygame.draw.rect(canvas, (50, 50, 80), (x0, y0 + HEADER, PW, PH), 1)

    sfont = _load_font(11)
    slug_s = sfont.render(slug, True, SLUG_COL)
    ver_s  = sfont.render(verdict, True, VERDICT_COL)
    fy = y0 + HEADER + PH + (FOOTER - slug_s.get_height()) // 2
    canvas.blit(slug_s, (x0 + 6, fy))
    canvas.blit(ver_s, (x0 + PW - ver_s.get_width() - 6, fy))


# (path, fn_name, fn_args, fn_kwargs, title, slug, verdict) — row-major
PANELS = [
    (None,                                None,                    (),                       {},               "BEFORE — CONSTELLATION", "current card",     ""),
    ("tools/render_marquee_stripe_v2_r2.py", "build_marquee_card", (),                       {"scaled": False}, "MARQUEE STRIPE",         "marquee-stripe",   "FINAL"),
    ("tools/render_triband_v2_r2.py",        "render_triband",     (),                       {},               "TRIBAND",                "triband",          "FINAL"),
    ("tools/render_lateral_split_v2_r2.py",  "build_card",         (),                       {},               "LATERAL SPLIT",          "lateral-split",    "FINAL"),
    ("tools/render_matte_frame_v2_r2.py",    "build_matte_frame",  ("skin_kitsune",),        {},               "MATTE FRAME",            "matte-frame",      "FINAL"),
    ("tools/render_radial_spotlight_v2_r2.py","render_card",        (),                       {},               "RADIAL SPOTLIGHT",       "radial-spotlight", "FINAL"),
]


def main():
    canvas = pygame.Surface((TOTAL_W, TOTAL_H))
    canvas.fill(BG)

    for idx, (path, fn, fn_args, fn_kwargs, title, slug, verdict) in enumerate(PANELS):
        col = idx % COLS
        row = idx // COLS
        if path is None:
            card = _render_before()
        else:
            card = _load_concept(path, fn, fn_args, fn_kwargs)
        _draw_panel(canvas, card, title, slug, verdict, col, row)

    out = "docs/item_card_redesign_v2/showcase.png"
    pygame.image.save(canvas, out)
    print(f"saved: {out}  size={canvas.get_size()}")

    from PIL import Image
    import os as _os
    img = Image.open(out)
    w, h = img.size
    distinct = len(set(img.getdata()))
    size_bytes = _os.path.getsize(out)
    print(f"PIL: {w}×{h}, {distinct} distinct colors, {size_bytes} bytes")
    assert w > 100 and h > 100, "canvas looks blank"
    assert distinct > 100, "too few colors — likely blank"
    print("validation OK")


if __name__ == "__main__":
    main()
