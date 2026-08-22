"""Full in-game screenshots for the crib-length designs — one life spent.

One full-resolution synthetic gameplay frame per design (sky, clouds,
mountains, pillars, ground, flying bird), with the lives row drawn by that
design: slot 0 occupied, slot 1 empty. Scene setup reused from
docs/build_v5_gameplay_showcase.py.
"""
import importlib.util, os, sys
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
os.environ.setdefault('SDL_VIDEODRIVER', 'offscreen')
sys.path.insert(0, '/home/user/skybit')
sys.path.insert(0, '/home/user/skybit/docs/nest-mouth')

import pygame
pygame.init()
import _nestbase as nb

from game.config import W, H, GROUND_Y, BIRD_X, PIPE_W, GAP_START
import game.config as _cfg
if not hasattr(_cfg, 'DAY_EXTRA_SECONDS'):
    _cfg.DAY_EXTRA_SECONDS = 0
from game import biome as _biome
from game.draw import get_sky_surface_biome, draw_mountains, draw_cloud, draw_ground
import game.parrot as parrot
import game.hud as hud

BIRD_Y, BIRD_FRAME, BIRD_TILT = 268, 1, -6.0
BG_SCROLL, PHASE, PIPE_GAP = 420, 0.05, GAP_START
PILLAR_SPECS = [(230, 240), (510, 290)]
NEST_CY, NEST_DX = 73, 40


def _draw_pillar(surf, cx, gap_cy, pal):
    x = cx - PIPE_W // 2
    half_g = PIPE_GAP // 2
    top_h = gap_cy - half_g
    bot_y = gap_cy + half_g
    bot_h = GROUND_Y - bot_y
    stone = pal.get('pipe_stone', (190, 152, 102))
    stone_dk = pal.get('pipe_shadow', (150, 115, 72))
    stone_cap = pal.get('pipe_cap', (210, 175, 125))
    pygame.draw.rect(surf, stone, (x, 0, PIPE_W, top_h))
    pygame.draw.rect(surf, stone_dk, (x, 0, 4, top_h))
    pygame.draw.rect(surf, stone_cap, (x - 3, top_h - 8, PIPE_W + 6, 8))
    if bot_h > 0:
        pygame.draw.rect(surf, stone, (x, bot_y, PIPE_W, bot_h))
        pygame.draw.rect(surf, stone_dk, (x, bot_y, 4, bot_h))
        pygame.draw.rect(surf, stone_cap, (x - 3, bot_y, PIPE_W + 6, 8))


def draw_frame(draw_slot):
    screen = pygame.Surface((W, H))
    pal = _biome.palette_for_phase(PHASE)
    a = int(PHASE * _biome.PHASE_BUCKETS) % _biome.PHASE_BUCKETS
    sky = get_sky_surface_biome(W, H, GROUND_Y, pal, a)
    sky.set_alpha(None)
    screen.blit(sky, (0, 0))
    for i, (bx, by, sc) in enumerate(((20, 90, .9), (180, 140, 1.1), (60, 220, .8),
                                      (230, 60, .7), (320, 180, .9))):
        ox = ((bx - BG_SCROLL * (0.04 + 0.02 * i)) % (W + 160)) - 80
        draw_cloud(screen, ox, by, sc, variant=0, palette=pal)
    draw_mountains(screen, BG_SCROLL, GROUND_Y, W, phase=PHASE)
    draw_ground(screen, GROUND_Y, W, H, BG_SCROLL,
                pal.get('ground_top'), pal.get('ground_mid'))
    for cx, gap_cy in PILLAR_SPECS:
        _draw_pillar(screen, cx, gap_cy, pal)
    sprite = parrot.get_parrot(BIRD_FRAME, BIRD_TILT)
    sw, sh = sprite.get_size()
    screen.blit(sprite, (BIRD_X - sw // 2, BIRD_Y - sh // 2))
    # Lives row: slot 0 occupied, slot 1 empty (one life spent).
    draw_slot(screen, NEST_CY, True)
    scratch = pygame.Surface((W, H), pygame.SRCALPHA)
    draw_slot(scratch, NEST_CY, False)
    screen.blit(scratch, (NEST_DX, 0))
    return screen


def load(slug):
    spec = importlib.util.spec_from_file_location(
        slug.replace('-', '_'), f'/home/user/skybit/docs/nest-mouth/{slug}/render.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    cols = [('CUR', hud._nest_draw_slot)]
    for idl, slug in [('D1', 'classic-seat'), ('L1', 'len-1'), ('L2', 'len-2'),
                      ('L3', 'len-3'), ('L4', 'len-4'), ('L5', 'len-5'),
                      ('D2', 'short-crib')]:
        cols.append((idl, load(slug).draw_slot))
    pygame.font.init()
    idfont = pygame.font.SysFont('monospace', 44, bold=True)
    GAP, M, FOOT = 14, 18, 64
    n = len(cols)
    canvas = pygame.Surface((2 * M + n * W + (n - 1) * GAP, 2 * M + H + FOOT))
    canvas.fill((8, 8, 20))
    for ci, (idl, fn) in enumerate(cols):
        x0 = M + ci * (W + GAP)
        canvas.blit(draw_frame(fn), (x0, M))
        t = idfont.render(idl, True, (255, 220, 120))
        canvas.blit(t, (x0 + W // 2 - t.get_width() // 2, M + H + 10))
    out = 'docs/nest-mouth/showcase_ingame.png'
    pygame.image.save(canvas, out)
    print('saved', canvas.get_size(), '->', out)


if __name__ == '__main__':
    main()
