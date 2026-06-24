"""Render the NOVA DRIFTER (design_8) astronaut candidate to a labeled review
sheet: a hero product-shot, in-gameplay DAY + NIGHT crops, and the 40px
NEAREST-neighbour truth read (the "lives or dies at 40px" check) on both day
and night sky swatches. Headless only."""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from tools.ninja_render import hero_panel, gameplay_panel, _frame
from tools.astronaut_candidates.design_8 import build
from game import biome
from game.draw import get_sky_surface_biome
from game.config import W as GW, H as GH, GROUND_Y

# The genuinely dark NIGHT keyframe (sky_top ≈ (5,8,30)); phase 0.5 is DUSK
# (lavender) and is NOT a real night truth-read for the all-navy pack + keyline.
NIGHT_PHASE = 0.64375

OUT = "/home/user/skybit/docs/store_redesign/costume/astronaut/design_8/round_3.png"


def _font(sz, bold=True):
    return pygame.font.SysFont("Arial", sz, bold=bold)


def _label(surf, text, x, y, sz=18, col=(240, 240, 245)):
    surf.blit(_font(sz).render(text, True, col), (x, y))


def _truth_read(box, *, phase):
    """A 40px NEAREST downscale of the bird on a real sky swatch, blown back up
    NEAREST so the shrunk pixels are judgeable — the read the player gets in
    motion."""
    pal = biome.palette_for_phase(phase)
    # The sky surface is cached by phase_bucket; passing a literal 0 for every
    # phase collides day + night on one cache entry (day wins) — so the night
    # swatch was secretly the day sky. Key each phase to its real bucket.
    sky = get_sky_surface_biome(GW, GH, GROUND_Y, pal, biome.phase_bucket(phase))
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


def main():
    pygame.font.init()
    PAD = 18
    HERO = 300
    GPW = 240
    GPH = 360
    TR = 170

    W = PAD * 5 + HERO + GPW * 2
    H = 86 + max(HERO, GPH) + PAD + TR + 30 + PAD
    sheet = pygame.Surface((W, H))
    sheet.fill((24, 22, 32))

    _label(sheet, "ASTRONAUT redesign — DESIGN 8: NOVA DRIFTER (NASA MMU free-flyer, chrome mirror visor)",
           PAD, 16, sz=22, col=(255, 255, 255))
    _label(sheet, "Sleek white two-tone · flat CHROME mirror visor + one glint · winged RCS jetpack (flared nozzles) · navy + safety-orange command palette",
           PAD, 48, sz=14, col=(170, 175, 190))

    top = 86
    # Hero product shot.
    sheet.blit(hero_panel(build, HERO, frame_idx=2, tilt=0.0), (PAD, top))
    _label(sheet, "HERO (detail)", PAD + 6, top + HERO - 26, sz=15)

    # Gameplay day + night crops.
    gx = PAD * 2 + HERO
    sheet.blit(gameplay_panel(build, GPW, GPH), (gx, top))
    _label(sheet, "GAMEPLAY (day)", gx + 6, top + GPH - 26, sz=15)

    gx2 = gx + GPW + PAD
    sheet.blit(_night_gameplay(GPW, GPH), (gx2, top))
    _label(sheet, "GAMEPLAY (night)", gx2 + 6, top + GPH - 26, sz=15)

    # Bottom row: 40px NEAREST truth reads, day + night.
    trow = top + max(HERO, GPH) + PAD
    _label(sheet, "40px TRUTH READ (NEAREST) — lives or dies at size:", PAD, trow - 24, sz=15)
    sheet.blit(_truth_read(TR, phase=0.0), (PAD, trow))
    _label(sheet, "day sky", PAD + 6, trow + TR + 4, sz=13, col=(190, 195, 205))
    sheet.blit(_truth_read(TR, phase=NIGHT_PHASE), (PAD + TR + PAD, trow))
    _label(sheet, "night sky", PAD + TR + PAD + 6, trow + TR + 4, sz=13, col=(190, 195, 205))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    pygame.image.save(sheet, OUT)
    print("saved", OUT, sheet.get_size())


def _night_gameplay(w, h):
    """A night-phase variant of ninja_render.gameplay_panel so the bright white
    suit + chrome visor are judged against the dark sky the keyline guards."""
    from game.draw import draw_mountains, draw_ground, draw_cloud
    from game.entities import Pipe
    scene = pygame.Surface((GW, GH))
    palette = biome.palette_for_phase(NIGHT_PHASE)
    scene.blit(get_sky_surface_biome(GW, GH, GROUND_Y, palette,
                                     biome.phase_bucket(NIGHT_PHASE)), (0, 0))
    for bx, by, sc, variant in ((40, 90, 0.9, 0), (200, 130, 1.1, 2), (300, 70, 0.7, 1)):
        draw_cloud(scene, bx, by, sc, variant=variant)
    draw_mountains(scene, 40.0, GROUND_Y, GW, palette['mtn_far'], palette['mtn_near'])
    Pipe(x=12, gap_y=250, gap_h=185).draw(scene, palette)
    Pipe(x=200, gap_y=300, gap_h=170).draw(scene, palette)
    draw_ground(scene, GROUND_Y, GW, GH, 40.0,
                palette['ground_top'], palette['ground_mid'], (60, 40, 25))
    pip_cx, pip_cy = 96, 270
    frame = _frame(build, 2, 10.0)
    scene.blit(frame, frame.get_rect(center=(pip_cx, pip_cy)))
    crop_h = int(GH * 0.78)
    crop_w = int(crop_h * w / h)
    crop = pygame.Rect(0, 0, crop_w, crop_h)
    crop.center = (pip_cx + 34, pip_cy - 20)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    return pygame.transform.smoothscale(scene.subsurface(crop).copy(), (w, h))


if __name__ == "__main__":
    main()
