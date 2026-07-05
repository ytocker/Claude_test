"""Height ladder based on V1 (in gameplay).

Per user direction: V1 is the LOWEST (max drop); the other versions sit higher
(more tucked toward the body). All keep V1's exact treatment (pure drop, no
stem, same size/split) and vary ONLY the vertical position, in 2px steps from V1
up toward the original tucked spot — so the choice is purely "how high".

Rendered through the production bird-draw path into the real showcase scene.
NOT production. Run:  SDL_VIDEODRIVER=dummy python tools/shoe_placement_ingame3.py
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

# V1 = back(17,68) front(31,70) is the LOWEST. Step up 2px per version (same
# size 17x11 + same x-split + no stem). Higher = more tucked toward the belly.
def _ladder(step):
    return dict(back=(17, 68 - step, 17, 11), front=(31, 70 - step, 17, 11),
                stem_len=0)

VARIANTS = [
    ("H1  V1 (LOWEST)", "max drop, clears belly most", _ladder(0)),
    ("H2  1 STEP UP", "2px higher", _ladder(2)),
    ("H3  2 STEPS UP", "4px higher", _ladder(4)),
    ("H4  3 STEPS UP", "6px higher", _ladder(6)),
    ("H5  4 STEPS UP", "8px higher (most tucked)", _ladder(8)),
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
    t = FT.render("SHOES — HEIGHT LADDER (V1 lowest, others tucked higher)",
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

    out = ROOT / "docs" / "shoes" / "round_4_heightladder.png"
    pygame.image.save(sheet, str(out))
    print("WROTE", out, sheet.get_size())


if __name__ == "__main__":
    main()
