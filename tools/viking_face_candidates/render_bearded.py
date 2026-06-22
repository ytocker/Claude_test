"""Render the BEARDED Viking refinement review sheet.

For EACH palette (IRONCLAD then BLOODAXE): a hero zoom (face + carried axe
legible) + an in-gameplay panel + a 40px NEAREST "truth read" of the actual
in-game size. Saved to docs/store_redesign/costume/viking/bearded/round_1.png.
Scratch exploration — no production art is touched.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from tools.ninja_render import hero_panel, gameplay_panel
from tools.viking_face_candidates.bearded import build_ironclad, build_bloodaxe

FONT = pygame.font.SysFont("DejaVu Sans", 18, bold=True)
SUB = pygame.font.SysFont("DejaVu Sans", 13)

HERO = 240
# Keep the gameplay aspect <= GW/(GH*0.78) so the harness crop stays in-bounds.
GP_W, GP_H = 214, 300
PAD = 16
LABEL_H = 30

ROWS = [("IRONCLAD", build_ironclad), ("BLOODAXE", build_bloodaxe)]


def _truth_panel(build):
    """The bird at its true in-game frame size, NEAREST-upscaled 4x so the 40px
    read is judged honestly without smoothing."""
    frame = build(2, 10.0)
    bb = frame.get_bounding_rect()
    if bb.width and bb.height:
        frame = frame.subsurface(bb).copy()
    panel = pygame.Surface((HERO, GP_H), pygame.SRCALPHA)
    panel.fill((30, 28, 40))
    # True size next to the 4x NEAREST blow-up.
    panel.blit(frame, frame.get_rect(center=(56, GP_H // 2 - 30)))
    big = pygame.transform.scale(
        frame, (frame.get_width() * 4, frame.get_height() * 4))
    panel.blit(big, big.get_rect(center=(HERO - 90, GP_H // 2 + 10)))
    panel.blit(SUB.render("native   ->   4x NEAREST", True, (200, 200, 210)),
               (12, GP_H - 26))
    return panel


def main():
    row_h = LABEL_H + GP_H + PAD
    cols = 3
    col_w = max(HERO, GP_W) + PAD
    sheet_w = cols * col_w + PAD
    sheet_h = len(ROWS) * row_h + PAD + 24
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((18, 16, 24))

    sheet.blit(FONT.render(
        "VIKING — BEARDED (regular macaw face + beaded 'stache/beard + back-stowed double-bit axe)",
        True, (240, 236, 230)), (PAD, 6))

    headers = ["HERO ZOOM", "IN-GAMEPLAY", "40px TRUTH READ"]
    for ri, (label, build) in enumerate(ROWS):
        y0 = 30 + ri * row_h
        sheet.blit(FONT.render(label, True, (255, 224, 150)), (PAD, y0))
        panels = [
            hero_panel(build, HERO, tilt=0.0),
            gameplay_panel(build, GP_W, GP_H),
            _truth_panel(build),
        ]
        for ci, panel in enumerate(panels):
            x = PAD + ci * col_w
            y = y0 + LABEL_H
            sheet.blit(SUB.render(headers[ci], True, (170, 170, 185)), (x, y - 16))
            sheet.blit(panel, (x, y))

    out_dir = "/home/user/skybit/docs/store_redesign/costume/viking/bearded"
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "round_1.png")
    pygame.image.save(sheet, out)
    print("saved", out, sheet.get_size())


if __name__ == "__main__":
    main()
