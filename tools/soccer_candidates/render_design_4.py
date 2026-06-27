"""Soccer v4 D4 THE REFEREE — round 1 review sheet.

This v4 makes the jersey read as CLOTHING via four shirt-construction
elements (V-neck collar, white sleeve edges, dual rim-lights, centre placket).
The black kit's NIGHT read is the risk, so the sheet pairs a clean hero shot
and an in-gameplay day-biome crop with a 40px truth read split across a day and
a night swatch — the rim-lights and props are judged against the dark sky.

Headless: SDL_VIDEODRIVER=dummy python -m tools.soccer_candidates.render_design_4
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from tools import ninja_render
from tools.soccer_candidates.design_4 import build

OUT = "docs/store_redesign/costume/soccer/design_4/round_1.png"
TITLE = "DESIGN 4 — THE REFEREE (Soccer)  round 1"


def _label(surf, text, x, y, size=18, color=(236, 238, 246)):
    font = pygame.font.SysFont("arial", size, bold=True)
    surf.blit(font.render(text, True, color), (x, y))


def _hero_nearest(box):
    """Crisp NEAREST magnify of the bird on a flat panel so the reviewer judges
    the actual drawn shirt-construction pixels (V-neck stitch, sleeve cuff,
    placket seam, whistle glint, card edge) without smoothscale blur."""
    panel = pygame.Surface((box, box), pygame.SRCALPHA)
    pygame.draw.rect(panel, (22, 20, 32), panel.get_rect(), border_radius=14)
    frame = build(ninja_render.FRAME_IDX, 0.0)
    bb = frame.get_bounding_rect()
    frame = frame.subsurface(bb).copy()
    sw, sh = frame.get_size()
    scale = max(1, int((box * 0.82) / max(sw, sh)))
    frame = pygame.transform.scale(frame, (sw * scale, sh * scale))
    panel.blit(frame, frame.get_rect(center=(box // 2, box // 2)))
    return panel


def _truth_read(box):
    """The 40px-in-motion test: NEAREST-shrink to a ~40px bird then magnify 3x,
    on a day and a night swatch. The black kit's night read is the risk, so the
    dual rim-lights + props are judged against the dark sky beside the day."""
    frame = build(ninja_render.FRAME_IDX, ninja_render.TILT)
    bb = frame.get_bounding_rect()
    frame = frame.subsurface(bb).copy()
    sw, sh = frame.get_size()
    scale = 40.0 / max(sw, sh)
    small = pygame.transform.scale(
        frame, (max(1, int(sw * scale)), max(1, int(sh * scale))))
    panel = pygame.Surface((box, box))
    panel.fill((30, 28, 40))
    half = box // 2
    pygame.draw.rect(panel, (150, 200, 235), (0, 0, half, box))        # day sky
    pygame.draw.rect(panel, (16, 18, 34), (half, 0, box - half, box))  # night sky
    for ox in (half // 2, half + half // 2):
        tile = pygame.Surface((48, 48), pygame.SRCALPHA)
        tile.blit(small, small.get_rect(center=(24, 24)))
        big = pygame.transform.scale(tile, (48 * 3, 48 * 3))
        panel.blit(big, big.get_rect(center=(ox, box // 2 + 8)))
    return panel


def main():
    box = 360
    hero = _hero_nearest(box)
    gameplay = ninja_render.gameplay_panel(build, 260, 420)
    truth = _truth_read(box)

    pad = 18
    head = 56
    cap = 30
    widths = [box, 260, box]
    W = pad * (len(widths) + 1) + sum(widths)
    H = head + max(box, 420) + cap + pad
    sheet = pygame.Surface((W, H))
    sheet.fill((18, 17, 26))
    _label(sheet, TITLE, pad, 16, size=22)

    xs = []
    x = pad
    for w in widths:
        xs.append(x)
        x += w + pad
    y = head
    for x, panel in zip(xs, (hero, gameplay, truth)):
        sheet.blit(panel, (x, y))
    for x, name in zip(xs, ("HERO (NEAREST 3x)", "IN-GAMEPLAY (day biome)",
                            "40px TRUTH READ  (day | night, 3x)")):
        _label(sheet, name, x, y + 420 + 6, size=15, color=(190, 194, 210))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    pygame.image.save(sheet, OUT)
    print("saved", OUT, sheet.get_size())


if __name__ == "__main__":
    main()
