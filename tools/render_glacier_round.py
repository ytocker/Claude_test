"""Round sheet for GLACIER MACAW (wave2 design_1) — scratch exploration only.

Renders the candidate in-gameplay so the preview matches how the skin actually
reads in play: DAY + NIGHT gameplay panels, a hero close-up, and the make-or-
break 40px NEAREST truth-reads on both skies. Round 2 adds the north-star proof
the art-director asked for: the SAME bird with the icicle crest digitally
masked (build_no_crest) at 40px on day, to show the body alone holds its
silhouette — plus a measured body-to-sky luminance delta on day sky.

Reuses tools.ninja_render's biome compose; the night panel re-implements its
day compose at a night phase since the harness day panel is pinned to phase 0.0.
"""
from __future__ import annotations
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import importlib
import pygame
pygame.init()

import tools.ninja_render as nr
from game import biome
from game.draw import get_sky_surface_biome, draw_mountains, draw_ground, draw_cloud
from game.entities import Pipe
from game.config import W as GW, H as GH, GROUND_Y
from game.hud import _font, _GOLD_PALE

_mod = importlib.import_module("tools.parrot_wave2_candidates.design_1")
build = _mod.build
build_no_crest = _mod.build_no_crest


def gameplay_panel_phase(source, w, h, phase, *, frame_idx=2, tilt=10.0):
    """ninja_render.gameplay_panel, but at an arbitrary biome phase so we can
    show the same scene on a night sky."""
    scene = pygame.Surface((GW, GH))
    palette = biome.palette_for_phase(phase)
    scene.blit(get_sky_surface_biome(GW, GH, GROUND_Y, palette, 0), (0, 0))
    for bx, by, sc, variant in ((40, 90, 0.9, 0), (200, 130, 1.1, 2), (300, 70, 0.7, 1)):
        draw_cloud(scene, bx, by, sc, variant=variant)
    draw_mountains(scene, 40.0, GROUND_Y, GW, palette['mtn_far'], palette['mtn_near'])
    Pipe(x=12, gap_y=250, gap_h=185).draw(scene, palette)
    Pipe(x=200, gap_y=300, gap_h=170).draw(scene, palette)
    draw_ground(scene, GROUND_Y, GW, GH, 40.0,
                palette['ground_top'], palette['ground_mid'], (60, 40, 25))
    pip_cx, pip_cy = 96, 270
    frame = source(frame_idx, tilt)
    scene.blit(frame, frame.get_rect(center=(pip_cx, pip_cy)))
    crop_h = int(GH * 0.78)
    crop_w = int(crop_h * w / h)
    crop = pygame.Rect(0, 0, crop_w, crop_h)
    crop.center = (pip_cx + 34, pip_cy - 20)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    return pygame.transform.smoothscale(scene.subsurface(crop).copy(), (w, h))


def _tiny40(source, frame_idx=2, tilt=10.0):
    """The bird downscaled to 40px with NEAREST — what survives at thumbnail."""
    frame = source(frame_idx, tilt)
    bb = frame.get_bounding_rect()
    frame = frame.subsurface(bb).copy()
    sw, sh = frame.get_size()
    scale = 40 / max(sw, sh)
    return pygame.transform.scale(
        frame, (max(1, int(sw * scale)), max(1, int(sh * scale))))


def truth_read_40(source, bg, frame_idx=2, tilt=10.0):
    tiny = _tiny40(source, frame_idx, tilt)
    box = 64
    panel = pygame.Surface((box, box))
    panel.fill(bg)
    panel.blit(tiny, tiny.get_rect(center=(box // 2, box // 2)))
    return panel


def _rel_lum(c):
    """Relative luminance (sRGB→linear, Rec.709) for the WCAG-style contrast
    ratio the art-director's ~3:1 day-sky target is phrased in."""
    def lin(v):
        v /= 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * lin(c[0]) + 0.7152 * lin(c[1]) + 0.0722 * lin(c[2])


def _contrast(a, b):
    la, lb = _rel_lum(a), _rel_lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def day_body_contrast(bg):
    """Contrast of the dark glacier-shadow ICE vs the day sky on the crest-masked
    40px bird. Measures the darkest *ice* pixel (blue clearly above red, so the
    near-black outline/lens is excluded) — the honest body-fill value delta the
    art-director's ~3:1 day target is about, not the outline cheating the number."""
    tiny = _tiny40(build_no_crest)
    tiny.lock()
    darkest, dlum = None, 99.0
    for yy in range(tiny.get_height()):
        for xx in range(tiny.get_width()):
            r, g, b, a = tiny.get_at((xx, yy))
            if a < 200 or b <= r + 12:      # skip transparent + neutral outline/lens
                continue
            l = _rel_lum((r, g, b))
            if l < dlum:
                dlum, darkest = l, (r, g, b)
    tiny.unlock()
    return _contrast(darkest, bg), darkest


DAY_SKY = (120, 175, 220)
NIGHT_SKY = (28, 30, 70)

# ── layout: two rows ──────────────────────────────────────────────────────────
GP_W, GP_H = 240, 380
TRUTH = 128                       # 64px panel shown 2× so the 40px read is visible
PAD, GUT = 28, 18
TITLE_H, CAP_H, ROW_GAP = 78, 30, 26

# Row 1: day gameplay | night gameplay | hero | 40px day | 40px night
row1 = [("DAY · IN-GAMEPLAY", GP_W), ("NIGHT · IN-GAMEPLAY", GP_W),
        ("HERO CLOSE-UP", GP_H), ("40px DAY", TRUTH), ("40px NIGHT", TRUTH)]
# Row 2: the north-star proof — crest masked, body alone.
row2 = [("CREST MASKED · 40px DAY", TRUTH), ("CREST MASKED · 40px NIGHT", TRUTH)]


def _xs(row):
    out, x = [], PAD
    for _, w in row:
        out.append(x)
        x += w + GUT
    return out, x - GUT + PAD


xs1, w1 = _xs(row1)
xs2, _ = _xs(row2)
sheet_w = w1
row1_h = GP_H
row2_h = TRUTH
sheet_h = TITLE_H + row1_h + CAP_H + ROW_GAP + row2_h + CAP_H + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((16, 18, 28))

title = _font(25, True).render(
    "GLACIER MACAW — EPIC  ·  wave2 design_1  ·  round 2  (R2: day-sky value fix — dark ice gradient + sky rim)",
    True, _GOLD_PALE)
sheet.blit(title, title.get_rect(midtop=(sheet_w // 2, 20)))

cap_font = _font(13, True)
small_font = _font(12, False)
EPIC_COL = (108, 188, 252)
y = TITLE_H

# Row 1.
sheet.blit(gameplay_panel_phase(build, GP_W, GP_H, 0.0), (xs1[0], y))
sheet.blit(gameplay_panel_phase(build, GP_W, GP_H, 0.5), (xs1[1], y))
sheet.blit(nr.hero_panel(build, GP_H, bg=(20, 26, 40)), (xs1[2], y))
for xi, bg in ((3, DAY_SKY), (4, NIGHT_SKY)):
    t = pygame.transform.scale(truth_read_40(build, bg), (TRUTH, TRUTH))
    sheet.blit(t, (xs1[xi], y))
for (label, w), xx in zip(row1, xs1):
    pygame.draw.rect(sheet, EPIC_COL, pygame.Rect(xx - 2, y - 2, w + 4, GP_H + 4), 2)
    sheet.blit(cap_font.render(label, True, (180, 200, 220)), (xx, y + GP_H + 8))

# Row 2 — crest-masked proof + measured day contrast.
y2 = y + GP_H + CAP_H + ROW_GAP
for xi, bg in ((0, DAY_SKY), (1, NIGHT_SKY)):
    t = pygame.transform.scale(truth_read_40(build_no_crest, bg), (TRUTH, TRUTH))
    sheet.blit(t, (xs2[xi], y2))
    pygame.draw.rect(sheet, EPIC_COL, pygame.Rect(xs2[xi] - 2, y2 - 2, TRUTH + 4, TRUTH + 4), 2)
    sheet.blit(cap_font.render(row2[xi][0], True, (180, 200, 220)), (xs2[xi], y2 + TRUTH + 8))

ratio, darkest = day_body_contrast(DAY_SKY)
verdict = "PASS" if ratio >= 3.0 else "LOW"
vcol = (140, 230, 160) if ratio >= 3.0 else (240, 170, 120)
tx = xs2[1] + TRUTH + GUT + 12
lines = [
    ("NORTH-STAR PROOF", _GOLD_PALE),
    ("Crest removed, the body alone must hold its", (190, 200, 215)),
    ("silhouette on day sky. Darkest body pixel of", (190, 200, 215)),
    (f"the 40px masked bird = RGB{darkest}", (190, 200, 215)),
    (f"vs day sky RGB{DAY_SKY}", (190, 200, 215)),
    (f"luminance contrast = {ratio:.2f}:1   ({verdict}, target 3:1)", vcol),
    ("", (0, 0, 0)),
    ("R2 changes: dark glacier-shadow gradient on", (160, 190, 215)),
    ("back+belly + 1px sky rim · crackle thinned ~40%", (160, 190, 215)),
    ("· chest chips → 3 big hard glints · sparkles → 1", (160, 190, 215)),
    ("at tail · jagged 4-spike crest UNCHANGED.", (160, 190, 215)),
]
ly = y2
for txt, col in lines:
    if txt:
        f = _font(15, True) if col is _GOLD_PALE else small_font
        sheet.blit(f.render(txt, True, col), (tx, ly))
    ly += 17

out = os.path.join("docs", "store_redesign", "parrot", "wave2", "design_1", "round_2.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("SAVED", out, sheet.get_size(), "| day body contrast", round(ratio, 2), verdict)
