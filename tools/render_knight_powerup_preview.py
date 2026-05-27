"""Preview: the chosen K7 shield (quarterly gules/or) as BOTH the powerup
pickup icon AND the in-game knight's chest shield. EXPLORATION ONLY.

Run:  SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python -m tools.render_knight_powerup_preview
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from tools import render_shield_icon_variants as I
from tools import render_revive_designs as R

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                   "docs", "screenshots", "revive_designs")
os.makedirs(OUT, exist_ok=True)


def main():
    pose = R._Pose(frame_t=1.0, vy=-90, y=300)
    knight = R.render_one("IN-GAME KNIGHT — K7 shield", R.build_knight, pose)

    icon_big = pygame.transform.smoothscale(I._ss(I.NATIVE, I.NATIVE, I.draw_kn_quarterly, 6), (220, 220))
    icon_small = I._ss(I.INSET, I.INSET, I.draw_kn_quarterly, 6)

    gap, panelw = 16, 268
    sheet = pygame.Surface((panelw + gap * 2 + R.W + gap, R.H + gap * 2))
    sheet.fill((16, 18, 26))
    pygame.draw.rect(sheet, (22, 24, 34), (gap, gap, panelw, R.H), border_radius=14)
    pygame.draw.rect(sheet, (60, 66, 86), (gap, gap, panelw, R.H), 2, border_radius=14)
    f1 = pygame.font.SysFont("Arial", 19, bold=True)
    f2 = pygame.font.SysFont("Arial", 14)
    sheet.blit(f1.render("PICKUP ICON  ·  K7", True, (255, 232, 168)), (gap + 18, gap + 16))
    sheet.blit(icon_big, (gap + 24, gap + 56))
    iy = gap + 56 + 220 + 26
    sheet.blit(icon_small, (gap + 24, iy))
    sheet.blit(f2.render("← true pickup size", True, (220, 224, 235)), (gap + 24 + I.INSET + 10, iy + 6))
    sheet.blit(f2.render("quarterly gules & or", True, (220, 224, 235)), (gap + 24, iy + I.INSET + 12))
    sheet.blit(knight, (gap + panelw + gap, gap))
    out = os.path.join(OUT, "knight_K7_preview.png")
    pygame.image.save(sheet, out)
    print(f"saved {out}  ({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    main()
