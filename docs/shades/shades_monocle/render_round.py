"""Preview sheet for MONOCLE (shades_monocle) — self-contained, no game imports.

Left: product shot at eye_w=96 on neutral grey. Right: the in-game read at
eye_w=22 over a ~24px scarlet head (Pip) with a dark eye dot BEHIND the amber
lens, shown native and at ~7x zoom so the "framed circle, not a coin/bubble"
read is judged big. Headless (SDL dummy).

Run:  SDL_VIDEODRIVER=dummy python docs/shades/shades_monocle/render_round.py
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1, 1))

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from draw import draw_shades  # noqa: E402

_SCARLET = (214, 38, 36)
_EYE     = (28, 22, 24)


def head_with_specs(eye_w, head_r):
    """Scarlet head with a dark eye dot, then the monocle over it — the dark
    eye sitting behind the amber lens proves the rim reads as a frame."""
    pad = int(eye_w * 0.95)
    size = head_r * 2 + pad * 2
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    cx = cy = size // 2
    pygame.draw.circle(s, _SCARLET, (cx, cy), head_r)
    # Eye dot under the near lens (front toward beak at facing=1).
    ex = cx + int(eye_w * 0.23)
    pygame.draw.circle(s, _EYE, (ex, cy), max(2, int(head_r * 0.22)))
    pygame.draw.circle(s, (255, 255, 255), (ex - 1, cy - 1),
                       max(1, int(head_r * 0.07)))
    draw_shades(s, cx, cy, eye_w, 1)
    return s


def product(eye_w, c=176):
    s = pygame.Surface((c, c), pygame.SRCALPHA)
    draw_shades(s, c // 2, c // 2, eye_w, 1)
    return s


def main():
    pygame.font.init()
    title = pygame.font.SysFont("Arial", 18, bold=True)
    small = pygame.font.SysFont("Arial", 13, bold=True)
    tiny  = pygame.font.SysFont("Arial", 11)

    W, H = 720, 320
    sheet = pygame.Surface((W, H))
    sheet.fill((118, 122, 130))
    sheet.blit(title.render(
        "SKYBIT — SHADES · MONOCLE · heavy gold rim, amber glass, solid chain",
        True, (20, 22, 28)), (24, 14))

    # Product shot on neutral grey.
    prod = product(96)
    prect = pygame.Rect(36, 60, 176, 176)
    pygame.draw.rect(sheet, (138, 142, 150), prect, border_radius=10)
    sheet.blit(prod, prod.get_rect(center=prect.center).topleft)
    sheet.blit(small.render("product · eye_w=96", True, (20, 22, 28)),
               (prect.left, prect.bottom + 6))

    # On-Pip native @ eye_w=22 over a ~24px scarlet head.
    pip = head_with_specs(22, 12)
    nrect = pygame.Rect(prect.right + 40, 84, 110, 130)
    pygame.draw.rect(sheet, (138, 142, 150), nrect, border_radius=10)
    sheet.blit(pip, pip.get_rect(center=nrect.center).topleft)
    sheet.blit(small.render("in-game · 22px", True, (20, 22, 28)),
               (nrect.left + 6, nrect.bottom + 6))

    # ~7x zoom of the on-Pip head so the frame read is judged big.
    Z = 7
    zoom = pygame.transform.scale(
        pip, (pip.get_width() * Z, pip.get_height() * Z))
    zrect = pygame.Rect(nrect.right + 36, 60, 230, 200)
    pygame.draw.rect(sheet, (138, 142, 150), zrect, border_radius=10)
    sheet.set_clip(zrect)
    sheet.blit(zoom, zoom.get_rect(center=zrect.center).topleft)
    sheet.set_clip(None)
    pygame.draw.rect(sheet, (90, 94, 102), zrect, 1, border_radius=10)
    sheet.blit(tiny.render("~7x zoom — dark eye behind amber lens, framed", True,
                           (20, 22, 28)), (zrect.left, zrect.bottom + 6))

    out_path = os.path.join(_HERE, "round_2.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path, sheet.get_size())


if __name__ == "__main__":
    main()
