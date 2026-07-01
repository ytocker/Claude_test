"""Static mockup of the UFO colour-picker popup shown after purchase.

Shows the popup over a blurred gameplay background so the art-director can
evaluate it in context. Saves to docs/store_redesign/parcels/ufo/color_picker_mockup.png.
"""
import os, sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame
pygame.init()

import importlib.util

def _load_mod(name):
    path = os.path.join(os.path.dirname(__file__), f"{name}.py")
    spec = importlib.util.spec_from_file_location(name, path)
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

colors_mod = _load_mod("design_3_colors")
shared_mod = _load_mod("_render_shared")

# The 5 purchaseable colourways (not the gold original)
CHOICES = [
    ("SAPPHIRE",   "Blue + Gold",        colors_mod.build_sapphire),
    ("ROSE GOLD",  "Copper + Violet",     colors_mod.build_rose_gold),
    ("OBSIDIAN",   "Black + Orange",      colors_mod.build_obsidian),
    ("JADE",       "Green + Gold",        colors_mod.build_jade),
    ("AMETHYST",   "Purple + Cyan",       colors_mod.build_amethyst),
]

# ── Colours matching existing store modal style ──────────────────────────────
C_BG       = (4,   4,  10)          # game scene bg stand-in
C_SCRIM    = (4,   4,  10, 180)     # semi-transparent overlay
C_PANEL    = (22,  20, 32)          # obsidian panel
C_PANEL_B  = (40,  36, 58)          # panel border
C_GOLD     = (244, 197, 68)         # title gold
C_GOLD_DIM = (180, 140, 40)
C_TEXT     = (220, 216, 230)        # body text
C_SUBTEXT  = (140, 132, 160)        # muted subtitle
C_SWATCH   = (30,  28, 42)         # swatch card bg
C_SEL_BDR  = (255, 215, 60)        # selected border (gold glow)
C_SEL_BG   = (50,  44, 20)         # selected swatch tint
C_CANCEL   = (50,  46, 68)
C_CONFIRM  = (180, 130, 20)
C_CONFIRM_T= (255, 235, 120)
C_CANCEL_T = (180, 172, 200)

W, H = 360, 640

# ── Build the scene background ───────────────────────────────────────────────
from game import biome, parrot
from game.draw import get_sky_surface_biome, draw_mountains, draw_ground, draw_cloud
from game.entities import Pipe
from game.config import GROUND_Y

scene = pygame.Surface((W, H))
palette = biome.palette_for_phase(0.0)
scene.blit(get_sky_surface_biome(W, H, GROUND_Y, palette, 0), (0, 0))
for bx, by, sc, var in ((40, 90, 0.9, 0), (200, 130, 1.1, 2), (300, 70, 0.7, 1)):
    draw_cloud(scene, bx, by, sc, variant=var)
draw_mountains(scene, 40.0, GROUND_Y, W, palette['mtn_far'], palette['mtn_near'])
Pipe(x=12,  gap_y=250, gap_h=185).draw(scene, palette)
Pipe(x=200, gap_y=300, gap_h=170).draw(scene, palette)
draw_ground(scene, GROUND_Y, W, H, 40.0,
            palette['ground_top'], palette['ground_mid'], (60, 40, 25))
# Bird mid-flight
bf = parrot.get_skin_frame("skin_parrot", 2, 10.0)
scene.blit(bf, bf.get_rect(center=(96, 270)))

canvas = scene.copy()

# ── Scrim ────────────────────────────────────────────────────────────────────
scrim = pygame.Surface((W, H), pygame.SRCALPHA)
scrim.fill(C_SCRIM)
canvas.blit(scrim, (0, 0))

# ── Fonts ─────────────────────────────────────────────────────────────────────
F_TITLE  = pygame.font.SysFont("DejaVu Sans", 18, bold=True)
F_SUB    = pygame.font.SysFont("DejaVu Sans", 12)
F_LABEL  = pygame.font.SysFont("DejaVu Sans", 10, bold=True)
F_SEL    = pygame.font.SysFont("DejaVu Sans", 15, bold=True)
F_BTN    = pygame.font.SysFont("DejaVu Sans", 13, bold=True)

# ── Panel ─────────────────────────────────────────────────────────────────────
PW, PH  = 326, 390
px0     = (W - PW) // 2    # 17
py0     = (H - PH) // 2 - 20   # 115
panel_r = pygame.Rect(px0, py0, PW, PH)

pygame.draw.rect(canvas, C_PANEL_B, panel_r, border_radius=20)
pygame.draw.rect(canvas, C_PANEL,
                 panel_r.inflate(-2, -2), border_radius=19)

pcx = px0 + PW // 2

# ── Title + subtitle ──────────────────────────────────────────────────────────
t = F_TITLE.render("MINI UFO", True, C_GOLD)
canvas.blit(t, t.get_rect(centerx=pcx, y=py0 + 18))

sub = F_SUB.render("Choose your colour  —  one-time pick", True, C_SUBTEXT)
canvas.blit(sub, sub.get_rect(centerx=pcx, y=py0 + 42))

# Thin divider
pygame.draw.line(canvas, C_PANEL_B, (px0 + 20, py0 + 60), (px0 + PW - 20, py0 + 60))

# ── Swatch row ────────────────────────────────────────────────────────────────
SWATCH_W  = 54
SWATCH_H  = 88    # 66px hero (3×) + 22px label
SWATCH_GAP= 6
PARCEL_Z  = 3     # 3× upscale → 66×66

n_swatches  = len(CHOICES)
row_w       = n_swatches * SWATCH_W + (n_swatches - 1) * SWATCH_GAP
sx0         = pcx - row_w // 2
sy0         = py0 + 72

SELECTED = 0   # mockup: SAPPHIRE selected

for i, (name, desc, build_fn) in enumerate(CHOICES):
    sx  = sx0 + i * (SWATCH_W + SWATCH_GAP)
    sr  = pygame.Rect(sx, sy0, SWATCH_W, SWATCH_H)

    # Card background
    bg_col = C_SEL_BG if i == SELECTED else C_SWATCH
    pygame.draw.rect(canvas, bg_col, sr, border_radius=8)

    # Selected: gold border + glow
    if i == SELECTED:
        for off, alpha in [(3, 30), (2, 60), (1, 140)]:
            glow = pygame.Surface((SWATCH_W + off*2, SWATCH_H + off*2), pygame.SRCALPHA)
            pygame.draw.rect(glow, (*C_SEL_BDR, alpha),
                             pygame.Rect(0, 0, glow.get_width(), glow.get_height()),
                             border_radius=10)
            canvas.blit(glow, (sx - off, sy0 - off))
        pygame.draw.rect(canvas, C_SEL_BDR, sr, 2, border_radius=8)
    else:
        pygame.draw.rect(canvas, C_PANEL_B, sr, 1, border_radius=8)

    # Parcel hero at 3×
    raw = build_fn()
    pw, ph = raw.get_size()
    big = pygame.transform.scale(raw, (pw * PARCEL_Z, ph * PARCEL_Z))
    bw, bh = big.get_size()
    canvas.blit(big, (sx + (SWATCH_W - bw) // 2, sy0 + 4))

    # Short name label
    col = C_GOLD if i == SELECTED else C_SUBTEXT
    lbl = F_LABEL.render(name, True, col)
    canvas.blit(lbl, lbl.get_rect(centerx=sx + SWATCH_W // 2,
                                   y=sy0 + SWATCH_H - 16))

# ── Selected variant detail ────────────────────────────────────────────────────
detail_y = sy0 + SWATCH_H + 14
sel_name, sel_desc, _ = CHOICES[SELECTED]

sn = F_SEL.render(sel_name, True, C_GOLD)
canvas.blit(sn, sn.get_rect(centerx=pcx, y=detail_y))
sd = F_SUB.render(sel_desc, True, C_TEXT)
canvas.blit(sd, sd.get_rect(centerx=pcx, y=detail_y + 22))

# Thin divider
div_y = detail_y + 46
pygame.draw.line(canvas, C_PANEL_B, (px0 + 20, div_y), (px0 + PW - 20, div_y))

# ── Buttons ────────────────────────────────────────────────────────────────────
BTN_W, BTN_H = 130, 42
btn_y = div_y + 14

# CANCEL
cancel_r = pygame.Rect(px0 + 18, btn_y, BTN_W, BTN_H)
pygame.draw.rect(canvas, C_CANCEL, cancel_r, border_radius=10)
pygame.draw.rect(canvas, C_PANEL_B, cancel_r, 1, border_radius=10)
ct = F_BTN.render("CANCEL", True, C_CANCEL_T)
canvas.blit(ct, ct.get_rect(center=cancel_r.center))

# CONFIRM (gold, glowing)
confirm_r = pygame.Rect(px0 + PW - 18 - BTN_W, btn_y, BTN_W, BTN_H)
# Glow aura
for off, alpha in [(4, 20), (2, 50)]:
    ga = pygame.Surface((BTN_W + off*2, BTN_H + off*2), pygame.SRCALPHA)
    pygame.draw.rect(ga, (*C_SEL_BDR, alpha),
                     pygame.Rect(0, 0, ga.get_width(), ga.get_height()),
                     border_radius=12)
    canvas.blit(ga, (confirm_r.x - off, confirm_r.y - off))
pygame.draw.rect(canvas, C_CONFIRM, confirm_r, border_radius=10)
pygame.draw.rect(canvas, C_SEL_BDR, confirm_r, 1, border_radius=10)
cft = F_BTN.render("CONFIRM  ✓", True, C_CONFIRM_T)
canvas.blit(cft, cft.get_rect(center=confirm_r.center))

# ── Save ──────────────────────────────────────────────────────────────────────
out = os.path.join(os.path.dirname(__file__), "..", "..",
                   "docs", "store_redesign", "parcels", "ufo",
                   "color_picker_mockup.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print(f"saved → {out}")
