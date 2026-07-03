"""In-gameplay comparison of the 5 shoe-placement candidates.

Unlike tools/shoe_placement_sheet.py (bird on a flat sky swatch), this renders
each candidate THROUGH the production bird-draw path into the real showcase
gameplay scene (sky + pillar + ground + coins), so the shoes are judged exactly
as they appear in actual play. For each variant we temporarily swap the shelltoe
builder in parrot's merged skin registry, then reuse the showcase scene + the
render_look() full+zoom framing.

NOT production: only swaps an in-memory registry entry; nothing in game/ changes.
Run:  SDL_VIDEODRIVER=dummy python tools/shoe_placement_ingame.py
"""
import os, sys, pathlib
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

ROOT = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "docs" / "showcase"))
sys.path.insert(0, str(ROOT / "tools"))

from game import parrot, shoe_shelltoe
from game.store_skins import _make_skin
import render_showcase as show
from shoe_placement_sheet import _make_paint, VARIANTS

SHOE_ID = "skin_shoe_shelltoe"


def _variant_getter(kw):
    """A fresh cached skin getter that paints shelltoe at the variant coords."""
    paint = _make_paint(shoe_shelltoe.draw_shoe, kw["back"], kw["front"],
                        stem_len=kw.get("stem_len", 0), far_dim=kw.get("far_dim"))
    return _make_skin(paint)


def main():
    world, base = show.build_scene()
    registry = parrot._store_skin_builders()   # cached dict; mutate in place

    shots = []
    for label, caption, kw in VARIANTS:
        registry[SHOE_ID] = _variant_getter(kw)   # swap shelltoe for this variant
        full, zoom = show.render_look(world, base, SHOE_ID)
        shots.append((label, caption, full, zoom))

    # ── assemble the comparison sheet ────────────────────────────────────────
    full_h = 388
    fscale = full_h / shots[0][2].get_height()
    full_w = int(round(shots[0][2].get_width() * fscale))
    zoom_w = full_w
    zscale = zoom_w / shots[0][3].get_width()
    zoom_h = int(round(shots[0][3].get_height() * zscale))

    COL_W = full_w + 24
    TITLE_H, HDR_H, GAP = 52, 40, 10
    LABEL_H = 26
    W = COL_W * len(shots)
    H = TITLE_H + HDR_H + full_h + GAP + zoom_h + LABEL_H + 16

    BG = (22, 26, 38); INK = (236, 240, 248); SUB = (150, 162, 184)
    ACCENT = (255, 206, 80); RULE = (54, 62, 84)
    FT = pygame.font.SysFont("Arial", 24, bold=True)
    FL = pygame.font.SysFont("Arial", 17, bold=True)
    FC = pygame.font.SysFont("Arial", 13)
    FS = pygame.font.SysFont("Arial", 12)

    sheet = pygame.Surface((W, H)); sheet.fill(BG)
    pygame.draw.rect(sheet, (14, 17, 26), (0, 0, W, TITLE_H))
    t = FT.render("SHOES IN ACTUAL GAMEPLAY — pick one  (shelltoe shown)", True, INK)
    sheet.blit(t, (16, (TITLE_H - t.get_height()) // 2))
    pygame.draw.line(sheet, ACCENT, (0, TITLE_H - 1), (W, TITLE_H - 1), 2)

    for i, (label, caption, full, zoom) in enumerate(shots):
        x0 = i * COL_W
        cx = x0 + COL_W // 2
        if i:
            pygame.draw.line(sheet, RULE, (x0, TITLE_H), (x0, H), 1)
        ls = FL.render(label, True, ACCENT)
        cs = FC.render(caption, True, SUB)
        sheet.blit(ls, (cx - ls.get_width() // 2, TITLE_H + 4))
        sheet.blit(cs, (cx - cs.get_width() // 2, TITLE_H + 24))

        fy = TITLE_H + HDR_H
        fsurf = pygame.transform.smoothscale(full, (full_w, full_h))
        sheet.blit(fsurf, (cx - full_w // 2, fy))

        zy = fy + full_h + GAP
        zsurf = pygame.transform.smoothscale(zoom, (zoom_w, zoom_h))
        sheet.blit(zsurf, (cx - zoom_w // 2, zy))
        zl = FS.render("zoom on the bird", True, SUB)
        sheet.blit(zl, (cx - zl.get_width() // 2, zy + zoom_h + 4))

    out = ROOT / "docs" / "shoes" / "round_2_ingame.png"
    pygame.image.save(sheet, str(out))
    print("WROTE", out, sheet.get_size())


if __name__ == "__main__":
    main()
