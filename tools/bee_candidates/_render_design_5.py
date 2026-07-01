"""Render the STINGREEL (design_5) hornet candidate to a labeled review sheet:
a hero product-shot, an in-gameplay day crop, an in-gameplay NIGHT crop, and a
40px NEAREST-neighbour truth read (the "lives or dies at 40px" check) on both
day and night sky swatches. Headless only."""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from tools.ninja_render import hero_panel, gameplay_panel, _frame
from tools.bee_candidates.design_5 import build
from game import biome
from game.draw import get_sky_surface_biome
from game.config import W as GW, H as GH, GROUND_Y

OUT = "/home/user/skybit/docs/store_redesign/animal/bee/design_5/round_1.png"


def _font(sz, bold=True):
    return pygame.font.SysFont("Arial", sz, bold=bold)


def _label(surf, text, x, y, sz=18, col=(240, 240, 245)):
    surf.blit(_font(sz).render(text, True, col), (x, y))


def _truth_read(box, *, phase):
    """A 40px NEAREST downscale of the bird on a real sky swatch, then blown
    back up NEAREST so the shrunk pixels are judgeable — the read the player
    actually gets in motion."""
    pal = biome.palette_for_phase(phase)
    sky = get_sky_surface_biome(GW, GH, GROUND_Y, pal, 0)
    swatch = pygame.transform.smoothscale(sky.subsurface((0, 10, 120, 120)).copy(),
                                          (box, box))
    frame = _frame(build, 2, 10.0)
    bb = frame.get_bounding_rect()
    frame = frame.subsurface(bb).copy()
    sw, sh = frame.get_size()
    target = 40
    sc = target / max(sw, sh)
    small = pygame.transform.smoothscale(
        frame, (max(1, int(sw * sc)), max(1, int(sh * sc))))
    swatch.blit(small, small.get_rect(center=(box // 2, box // 2)))
    return pygame.transform.scale(swatch, (box, box))   # NEAREST blow-up


def _frames_strip(box):
    """The four flap frames side by side so the tight wing-buzz arc is legible."""
    strip = pygame.Surface((box * 4, box), pygame.SRCALPHA)
    for i in range(4):
        panel = hero_panel(build, box, frame_idx=i, tilt=0.0, bg=(30, 27, 20))
        strip.blit(panel, (box * i, 0))
    return strip


def main():
    pygame.font.init()
    PAD = 18
    HERO = 300
    GPW = 260
    GPH = 380
    TR = 180
    FS = 120

    W = PAD * 4 + HERO + GPW
    H = 80 + max(HERO, GPH) + PAD + TR + 30 + PAD + FS + 30

    sheet = pygame.Surface((W, H))
    sheet.fill((24, 22, 32))

    _label(sheet, "skin_bee redesign — DESIGN 5: STINGREEL (Giant Hornet, Vespa)",
           PAD, 16, sz=22, col=(255, 255, 255))
    _label(sheet, "Pinched wasp-waist · blocky orange head+thorax · black/amber banded abdomen · stinger · tight wing-buzz",
           PAD, 46, sz=14, col=(170, 175, 190))

    top = 80
    sheet.blit(hero_panel(build, HERO, frame_idx=2, tilt=0.0), (PAD, top))
    _label(sheet, "HERO (detail)", PAD + 6, top + HERO - 26, sz=15)

    gx = PAD * 2 + HERO
    sheet.blit(gameplay_panel(build, GPW, GPH), (gx, top))
    _label(sheet, "GAMEPLAY (day)", gx + 6, top + GPH - 26, sz=15)

    trow = top + max(HERO, GPH) + PAD
    _label(sheet, "40px TRUTH READ (NEAREST) — lives or dies at size:", PAD, trow - 24, sz=15)
    sheet.blit(_truth_read(TR, phase=0.0), (PAD, trow))
    _label(sheet, "day sky", PAD + 6, trow + TR + 4, sz=13, col=(190, 195, 205))
    sheet.blit(_truth_read(TR, phase=0.5), (PAD + TR + PAD, trow))
    _label(sheet, "night sky", PAD + TR + PAD + 6, trow + TR + 4, sz=13, col=(190, 195, 205))

    frow = trow + TR + 30 + PAD
    _label(sheet, "FLAP CYCLE (4 frames — wing-buzz arc):", PAD, frow - 24, sz=15)
    sheet.blit(_frames_strip(FS), (PAD, frow))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    pygame.image.save(sheet, OUT)
    print("saved", OUT, sheet.get_size())


if __name__ == "__main__":
    main()
