"""ONE gallery figure of the CURRENT parcels (the gift Pip carries below him).

Renders every item in the PARCELS store category — the free DEFAULT kraft box
plus each catalog parcel — carried by Pip mid-flight over a real gameplay scene,
in one labelled grid. Pure capture; production art untouched.

    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python tools/render_parcels_gallery.py
"""
import os, sys, pathlib

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "docs" / "parcels"))      # _parcel_lib
sys.path.insert(0, str(ROOT / "docs" / "showcase"))

import pygame
import _parcel_lib as L
from game.config import H, BIRD_X, PARCEL_Y_OFFSET
from game import parrot, store_catalog

# DEFAULT (free kraft box) first, then every catalog parcel in store order.
IDS = [store_catalog.PARCEL_BASE] + store_catalog.ids_of_group("parcels")


def _label(pid):
    if pid == store_catalog.PARCEL_BASE:
        return "DEFAULT", "free"
    return store_catalog.name(pid), f"{store_catalog.cost(pid)}c"


PW, PH = 132, 168
CX, CY = int(BIRD_X), int(H * 0.42 + 6)


def _panel(pid, phase):
    fn = parrot._store_parcel_builders().get(pid)
    if pid == store_catalog.PARCEL_BASE or fn is None:
        # base / fallback: get_parcel resolves the default kraft box
        parrot._store_parcel_builders()[L._TMP_ID] = lambda m="normal": parrot.get_parcel(m, pid)
    else:
        parrot._store_parcel_builders()[L._TMP_ID] = fn
    hud = L.HUD()
    world, base = L._scene(phase)
    frame = L._frame(world, base, hud)
    rect = pygame.Rect(CX - PW // 2, CY - PH // 2, PW, PH)
    return frame.subsurface(rect).copy()


def main():
    pygame.init()
    cols = 6
    rows = (len(IDS) + cols - 1) // cols
    pad, lab_h, title_h = 12, 26, 50
    sheet_w = pad + cols * (PW + pad)
    sheet_h = title_h + rows * (lab_h + PH + pad)
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((22, 24, 30))

    big = pygame.font.SysFont("Arial", 22, bold=True)
    lab = pygame.font.SysFont("Arial", 13, bold=True)
    sub = pygame.font.SysFont("Arial", 11)
    sheet.blit(big.render(f"PARCELS — the gift Pip carries  ({len(IDS)} items, "
                          "mid-flight)", True, (245, 245, 250)),
               (pad, (title_h - 22) // 2))

    for i, pid in enumerate(IDS):
        r, c = divmod(i, cols)
        x = pad + c * (PW + pad)
        y = title_h + r * (lab_h + PH + pad)
        sheet.blit(_panel(pid, L._DAY_PHASE), (x, y + lab_h))
        name, price = _label(pid)
        col = (255, 214, 120) if pid == store_catalog.PARCEL_BASE else (220, 224, 235)
        sheet.blit(lab.render(name, True, col), (x + 2, y))
        sheet.blit(sub.render(price, True, (150, 156, 170)), (x + 2, y + 13))

    out = ROOT / "docs" / "store_redesign" / "parcels" / "parcels_gallery.png"
    pygame.image.save(sheet, str(out))
    print("saved", out, sheet.get_size())


if __name__ == "__main__":
    main()
