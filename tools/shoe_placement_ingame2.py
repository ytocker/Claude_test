"""Round 2 of in-gameplay shoe-placement candidates.

Per user direction: V1's drop (front y=70 / back y=68, just below the belly
bottom ~y69) is the MAXIMUM distance — nothing hangs lower. These 5 keep that
drop as the floor and explore the OTHER knobs (x-split, size, far-shoe depth, a
minimal 2px ankle nub) so the shoes read as a visible pair without dangling.

Rendered through the production bird-draw path into the real showcase scene.
NOT production. Run:  SDL_VIDEODRIVER=dummy python tools/shoe_placement_ingame2.py
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
from shoe_placement_sheet import _make_paint

SHOE_ID = "skin_shoe_shelltoe"

# Composite space; belly bottom ~y69. Drop capped at V1 (back y68 / front y70).
# Vary split / size / far-shoe depth / a tiny ankle nub — never lower than V1.
VARIANTS = [
    ("N1  V1 BASELINE", "max-drop ref, no stem, narrow",
     dict(back=(17, 68, 17, 11), front=(31, 70, 17, 11), stem_len=0)),
    ("N2  WIDE SPLIT", "same drop, spread apart",
     dict(back=(15, 68, 17, 11), front=(33, 70, 17, 11), stem_len=0)),
    ("N3  SPLIT+DEPTH", "wide + far shoe dimmed/smaller",
     dict(back=(15, 68, 16, 10), front=(33, 70, 18, 11), stem_len=0,
          far_dim=0.78)),
    ("N4  NUB STEM", "tiny 2px ankle, wide split",
     dict(back=(16, 68, 17, 11), front=(32, 70, 17, 11), stem_len=2)),
    ("N5  SIZE BUMP", "chunkier, same max drop",
     dict(back=(15, 68, 19, 12), front=(33, 70, 19, 12), stem_len=0)),
]


def _variant_getter(kw):
    paint = _make_paint(shoe_shelltoe.draw_shoe, kw["back"], kw["front"],
                        stem_len=kw.get("stem_len", 0), far_dim=kw.get("far_dim"))
    return _make_skin(paint)


def main():
    world, base = show.build_scene()
    registry = parrot._store_skin_builders()

    shots = []
    for label, caption, kw in VARIANTS:
        registry[SHOE_ID] = _variant_getter(kw)
        full, zoom = show.render_look(world, base, SHOE_ID)
        shots.append((label, caption, full, zoom))

    full_h = 388
    fscale = full_h / shots[0][2].get_height()
    full_w = int(round(shots[0][2].get_width() * fscale))
    zoom_w = full_w
    zscale = zoom_w / shots[0][3].get_width()
    zoom_h = int(round(shots[0][3].get_height() * zscale))

    COL_W = full_w + 24
    TITLE_H, HDR_H, GAP, LABEL_H = 52, 40, 10, 26
    W = COL_W * len(shots)
    H = TITLE_H + HDR_H + full_h + GAP + zoom_h + LABEL_H + 16

    BG = (22, 26, 38); INK = (236, 240, 248); SUB = (150, 162, 184)
    ACCENT = (255, 206, 80); RULE = (54, 62, 84)
    FT = pygame.font.SysFont("Arial", 23, bold=True)
    FL = pygame.font.SysFont("Arial", 17, bold=True)
    FC = pygame.font.SysFont("Arial", 13)
    FS = pygame.font.SysFont("Arial", 12)

    sheet = pygame.Surface((W, H)); sheet.fill(BG)
    pygame.draw.rect(sheet, (14, 17, 26), (0, 0, W, TITLE_H))
    t = FT.render("SHOES — NEW SET (drop capped at V1)  shelltoe, in gameplay",
                  True, INK)
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
        sheet.blit(pygame.transform.smoothscale(full, (full_w, full_h)),
                   (cx - full_w // 2, fy))
        zy = fy + full_h + GAP
        sheet.blit(pygame.transform.smoothscale(zoom, (zoom_w, zoom_h)),
                   (cx - zoom_w // 2, zy))
        zl = FS.render("zoom on the bird", True, SUB)
        sheet.blit(zl, (cx - zl.get_width() // 2, zy + zoom_h + 4))

    out = ROOT / "docs" / "shoes" / "round_3_ingame.png"
    pygame.image.save(sheet, str(out))
    print("WROTE", out, sheet.get_size())


if __name__ == "__main__":
    main()
