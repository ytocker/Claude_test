"""Render the ATLASWING (design_5) Atlas-moth candidate to a labeled review
sheet: a hero product-shot, an in-gameplay day crop, a 40px NEAREST-neighbour
truth read (the "lives or dies at 40px" check) across 3 poses on BOTH day and
night sky, and the 4-frame flap strip so the wing arc is judgeable. Headless."""
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

OUT = "/home/user/skybit/docs/store_redesign/animal/bee/design_5/round_2.png"

# Real, DISTINCT skies for the truth read: bright DAY vs genuinely dark NIGHT.
# (R1 rendered both on the same blue because get_sky_surface_biome caches by the
# phase-bucket arg and both panels passed bucket 0.)
DAY_PHASE = 0.0
NIGHT_PHASE = 0.64375   # the NIGHT keyframe — sky_top (5,8,30), truly dark

# Three poses across the flap cycle so the truth read exposes whether the
# hooked-wing silhouette survives BOTH the shrink and the wing animation.
TRUTH_POSES = (0, 2, 3)


def _font(sz, bold=True):
    return pygame.font.SysFont("Arial", sz, bold=bold)


def _label(surf, text, x, y, sz=18, col=(240, 240, 245)):
    surf.blit(_font(sz).render(text, True, col), (x, y))


def _truth_swatch(box, phase, frame_idx):
    """A 40px NEAREST downscale of one pose on a real sky swatch, blown back up
    NEAREST so the shrunk pixels are judgeable — the read the player gets. The
    translucent windows must show a hint of sky through them at this size."""
    pal = biome.palette_for_phase(phase)
    # Bucket the sky by phase so day and night get separate cache entries — the
    # R1 bug was passing bucket 0 for both, which reused the day surface.
    sky = get_sky_surface_biome(GW, GH, GROUND_Y, pal, biome.phase_bucket(phase))
    swatch = pygame.transform.smoothscale(
        sky.subsurface((0, 10, 120, 120)).copy(), (box, box))
    frame = _frame(build, frame_idx, 10.0)
    bb = frame.get_bounding_rect()
    frame = frame.subsurface(bb).copy()
    sw, sh = frame.get_size()
    sc = 40 / max(sw, sh)
    small = pygame.transform.smoothscale(
        frame, (max(1, int(sw * sc)), max(1, int(sh * sc))))
    swatch.blit(small, small.get_rect(center=(box // 2, box // 2)))
    return pygame.transform.scale(swatch, (box, box))   # NEAREST blow-up


def _frames_strip(box):
    """The four flap frames side by side so the wing arc is legible."""
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
    TR = 100
    FS = 120

    row_top = HERO + PAD + GPW
    row_truth = TR * 6 + PAD
    row_strip = FS * 4
    content_w = max(row_top, row_truth, row_strip)

    W = PAD * 2 + content_w
    H = 80 + max(HERO, GPH) + PAD + 24 + TR + 22 + PAD + 24 + FS + PAD

    sheet = pygame.Surface((W, H))
    sheet.fill((24, 22, 32))

    _label(sheet, "skin_bee redesign — DESIGN 5: ATLASWING (Atlas Moth, Attacus atlas) — R2",
           PAD, 16, sz=22, col=(255, 255, 255))
    _label(sheet, "WIDE flat-topped wings (notch closed) · sideways hooked apexes · eye-dot on cream · one bold window/wing · wide maroon margin · recessive body knob",
           PAD, 46, sz=13, col=(170, 175, 190))

    top = 80
    sheet.blit(hero_panel(build, HERO, frame_idx=2, tilt=0.0), (PAD, top))
    _label(sheet, "HERO (detail)", PAD + 6, top + HERO - 26, sz=15)

    gx = PAD + HERO + PAD
    sheet.blit(gameplay_panel(build, GPW, GPH), (gx, top))
    _label(sheet, "GAMEPLAY (day)", gx + 6, top + GPH - 26, sz=15)

    trow = top + max(HERO, GPH) + PAD + 24
    _label(sheet, "40px TRUTH READ (NEAREST) — 3 poses per sky, lives or dies at size:",
           PAD, trow - 24, sz=15)
    for i, fi in enumerate(TRUTH_POSES):
        sheet.blit(_truth_swatch(TR, DAY_PHASE, fi), (PAD + i * TR, trow))
    night_x = PAD + 3 * TR + PAD
    for i, fi in enumerate(TRUTH_POSES):
        sheet.blit(_truth_swatch(TR, NIGHT_PHASE, fi), (night_x + i * TR, trow))
    _label(sheet, "day sky", PAD + 6, trow + TR + 2, sz=13, col=(190, 195, 205))
    _label(sheet, "night sky", night_x + 6, trow + TR + 2, sz=13, col=(190, 195, 205))

    frow = trow + TR + 22 + PAD + 24
    _label(sheet, "FLAP CYCLE (4 frames — wing arc):", PAD, frow - 24, sz=15)
    sheet.blit(_frames_strip(FS), (PAD, frow))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    pygame.image.save(sheet, OUT)
    print("saved", OUT, sheet.get_size())


if __name__ == "__main__":
    main()
