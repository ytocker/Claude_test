"""Comparison figure for the 5 SPORTS BALL parcels — each carried below Pip
mid-flight (DAY top, NIGHT bottom). Pure capture."""
import os, sys, pathlib, importlib.util
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "docs" / "parcels"))
sys.path.insert(0, str(ROOT / "docs" / "showcase"))
import pygame
import _parcel_lib as L
from game.config import H, BIRD_X
from game import parrot
BASE = ROOT / "docs" / "store_redesign" / "parcels" / "sports_balls"
def load(n):
    p = BASE / f"design_{n}" / "build.py"
    s = importlib.util.spec_from_file_location(f"b{n}", p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m.build
VAR = [("SOCCER", 1), ("BASKETBALL", 2), ("TENNIS", 3), ("BASEBALL", 4), ("FOOTBALL", 5)]
PW, PH = 150, 200; CX, CY = int(BIRD_X), int(H * 0.42 + 6)
def panel(fn, phase):
    parrot._store_parcel_builders()[L._TMP_ID] = fn; hud = L.HUD(); w, base = L._scene(phase); fr = L._frame(w, base, hud)
    return fr.subsurface(pygame.Rect(CX - PW // 2, CY - PH // 2, PW, PH)).copy()
pygame.init()
pad, lab_h, title_h = 14, 26, 52
sheet = pygame.Surface((pad + 5 * (PW + pad), title_h + 2 * (lab_h + PH + pad))); sheet.fill((22, 24, 30))
big = pygame.font.SysFont("Arial", 23, bold=True); lab = pygame.font.SysFont("Arial", 14, bold=True); sub = pygame.font.SysFont("Arial", 11)
sheet.blit(big.render("SPORTS BALL parcels — 5 designs (Pip mid-flight)", True, (245, 245, 250)), (pad, (title_h - 23) // 2))
for row, (phase, tag) in enumerate(((L._DAY_PHASE, "DAY"), (L._NIGHT_PHASE, "NIGHT"))):
    y = title_h + row * (lab_h + PH + pad)
    for col, (nm, n) in enumerate(VAR):
        x = pad + col * (PW + pad); sheet.blit(panel(load(n), phase), (x, y + lab_h))
        sheet.blit(lab.render(f"DESIGN {n}", True, (255, 214, 120)), (x + 2, y)); sheet.blit(sub.render(f"{nm} . {tag}", True, (160, 166, 180)), (x + 2, y + 14))
out = BASE / "final_comparison.png"; pygame.image.save(sheet, str(out)); print("saved", out, sheet.get_size())
