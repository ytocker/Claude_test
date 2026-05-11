"""5-design picker for the Skybit 3,000-games-played celebration image.

Each variant is a 360x640 portrait PNG (same as the in-game canvas).
Pip is rendered through the existing parrot.* getters and palette comes
from game.draw. Run from the repo root:

    PYTHONPATH=. python tools/render_3k_celebration.py

Output:
    docs/celebrations/3k_games/v1.png    Bucket Cake
    docs/celebrations/3k_games/v2.png    Gold Trophy
    docs/celebrations/3k_games/v3.png    Coin Shower
    docs/celebrations/3k_games/v4.png    Pip Quartet
    docs/celebrations/3k_games/v5.png    Newspaper Headline
    docs/celebrations/3k_games/compare.png   5-column strip with labels
"""
import math
import os
import random
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.config import W, H
from game import parrot
from game import biome as _biome
from game.draw import (
    COIN_GOLD, UI_RED,
    get_sky_surface_biome, draw_cloud,
)
from game.pillar_kfc import _bucket_draw, KFC_RED, KFC_RED_D, KFC_WHITE


# --- Palette / fonts -------------------------------------------------------

OUTLINE       = (24, 12, 6)
GOLD_HI       = (255, 232, 130)
GOLD_LO       = (200, 140, 20)
PAPER_BG      = (244, 232, 200)
PAPER_INK     = (38, 28, 18)
PAPER_RULE    = (120, 96, 56)
TROPHY_GOLD   = (244, 196, 72)
TROPHY_DARK   = (140, 90, 20)
CONFETTI_COLS = ((242, 90, 90), (90, 200, 80), (90, 160, 250),
                 (252, 206, 56), (236, 110, 220), (250, 130, 60))


def _font(size, bold=True):
    fname = "LiberationSans-Bold.ttf" if bold else "LiberationSans-Regular.ttf"
    return pygame.font.Font(os.path.join("game", "assets", fname), size)


# --- Outlined-gradient text helper (mimics FloatText "powerup" style) ------

def draw_big_text(surf, text, center, size, *, fill=COIN_GOLD,
                  outline=OUTLINE, outline_w=4, shadow=True,
                  sparkles=0):
    """Bold text with a thick outline + vertical gradient + drop shadow."""
    font = _font(size, bold=True)
    text_surf = font.render(text, True, fill)
    tw, th = text_surf.get_size()
    cx, cy = center

    # Outline: 8-direction offset blits of a dark-coloured render.
    outline_surf = font.render(text, True, outline)
    layer = pygame.Surface((tw + outline_w * 4, th + outline_w * 4),
                           pygame.SRCALPHA)
    for dx in range(-outline_w, outline_w + 1):
        for dy in range(-outline_w, outline_w + 1):
            if dx * dx + dy * dy <= outline_w * outline_w:
                layer.blit(outline_surf,
                           (outline_w * 2 + dx, outline_w * 2 + dy))

    # Fill body. (Skip the vertical gradient overlay - it was leaking
    # semi-transparent white into the empty area of the text-surface
    # bounding box and producing a faint rectangle behind the headline.)
    layer.blit(text_surf, (outline_w * 2, outline_w * 2))

    # Drop shadow
    if shadow:
        sh = pygame.Surface(layer.get_size(), pygame.SRCALPHA)
        sh.fill((0, 0, 0, 0))
        dark = font.render(text, True, (0, 0, 0))
        dark.set_alpha(140)
        sh.blit(dark, (outline_w * 2 + 2, outline_w * 2 + 3))
        surf.blit(sh, (cx - layer.get_width() // 2,
                        cy - layer.get_height() // 2))

    rect = layer.get_rect(center=(cx, cy))
    surf.blit(layer, rect.topleft)

    # Sparkle dots scattered around the bounding box
    if sparkles:
        rng = random.Random(hash(text) & 0xffff)
        for _ in range(sparkles):
            sx = rng.randint(rect.left - 6, rect.right + 6)
            sy = rng.randint(rect.top - 6, rect.bottom + 6)
            r = rng.randint(2, 4)
            pygame.draw.circle(surf, OUTLINE, (sx, sy), r + 1)
            pygame.draw.circle(surf, GOLD_HI, (sx, sy), r)
            pygame.draw.circle(surf, (255, 255, 255), (sx - 1, sy - 1),
                               max(1, r - 2))
    return rect


def draw_tagline(surf, text, y, size=20, color=(255, 255, 255)):
    font = _font(size, bold=True)
    # Subtle outline
    out = font.render(text, True, OUTLINE)
    fill = font.render(text, True, color)
    cx = W // 2
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            surf.blit(out, (cx - out.get_width() // 2 + dx,
                              y + dy))
    surf.blit(fill, (cx - fill.get_width() // 2, y))


# --- Backgrounds -----------------------------------------------------------

def night_sky(phase=0.05):
    """Calm dusk biome background - same as in-game phase 0.05 (very night)."""
    buckets = _biome.PHASE_BUCKETS
    pal = _biome.palette_for_phase(phase)
    sky = get_sky_surface_biome(W, H, H, pal, int(phase * buckets))
    return sky, pal


def starfield(surf, n=60, seed=7):
    rng = random.Random(seed)
    for _ in range(n):
        x = rng.randint(0, W - 1)
        y = rng.randint(0, int(H * 0.7))
        r = rng.choice((1, 1, 1, 2))
        a = rng.randint(120, 255)
        c = (255, 255, 255, a)
        s = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(s, c, (r + 1, r + 1), r)
        surf.blit(s, (x, y))


def confetti(surf, n=80, seed=11):
    rng = random.Random(seed)
    for _ in range(n):
        x = rng.randint(0, W - 1)
        y = rng.randint(0, H - 1)
        col = rng.choice(CONFETTI_COLS)
        w = rng.choice((3, 4, 5))
        h = rng.choice((6, 7, 8))
        ang = rng.uniform(-60, 60)
        piece = pygame.Surface((w + 2, h + 2), pygame.SRCALPHA)
        pygame.draw.rect(piece, OUTLINE,
                          pygame.Rect(0, 0, w + 2, h + 2), border_radius=2)
        pygame.draw.rect(piece, col,
                          pygame.Rect(1, 1, w, h), border_radius=2)
        rot = pygame.transform.rotate(piece, ang)
        surf.blit(rot, (x - rot.get_width() // 2,
                          y - rot.get_height() // 2))


def starburst(surf, cx, cy, r_outer, r_inner, color, *, points=12):
    """Radiating starburst behind a focal point - sun-rays effect."""
    pts = []
    for i in range(points * 2):
        a = i * math.pi / points - math.pi / 2
        rr = r_outer if i % 2 == 0 else r_inner
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    pygame.draw.polygon(surf, color, pts)


# --- V1 Bucket Cake --------------------------------------------------------

def draw_v1(surf):
    sky, pal = night_sky(0.08)
    surf.blit(sky, (0, 0))
    starfield(surf, n=40, seed=1)

    # Big bucket "cake" centered, taking up most of the lower half.
    bucket_w = 240
    bucket_h = 280
    bucket_rect = pygame.Rect((W - bucket_w) // 2,
                              H - bucket_h - 70,
                              bucket_w, bucket_h)
    _bucket_draw(surf, bucket_rect, label_text="3000", n_stripes=6)

    # Candle on top: a slim white stick + golden flame
    rim_y = bucket_rect.top
    cand = pygame.Rect(W // 2 - 6, rim_y - 56, 12, 36)
    pygame.draw.rect(surf, OUTLINE, cand.inflate(2, 2), border_radius=3)
    pygame.draw.rect(surf, KFC_WHITE, cand, border_radius=3)
    # Wick
    pygame.draw.line(surf, OUTLINE, (cand.centerx, cand.top - 2),
                     (cand.centerx, cand.top - 6), 2)
    # Flame
    flame = [(cand.centerx, cand.top - 22),
             (cand.centerx - 7, cand.top - 6),
             (cand.centerx, cand.top - 2),
             (cand.centerx + 7, cand.top - 6)]
    pygame.draw.polygon(surf, (180, 50, 20), flame)
    inner = [(cand.centerx, cand.top - 16),
             (cand.centerx - 4, cand.top - 6),
             (cand.centerx, cand.top - 2),
             (cand.centerx + 4, cand.top - 6)]
    pygame.draw.polygon(surf, (250, 180, 30), inner)
    pygame.draw.polygon(surf, (255, 250, 200),
                        [(cand.centerx, cand.top - 11),
                         (cand.centerx - 2, cand.top - 5),
                         (cand.centerx, cand.top - 2),
                         (cand.centerx + 2, cand.top - 5)])

    # Pip on top of the cake, standing slightly to the right of the candle
    pip = parrot.get_parrot(1, 0)
    surf.blit(pip, (W // 2 + 8, rim_y - pip.get_height() + 18))

    # Confetti rain (above the cake, falling)
    confetti(surf, n=60, seed=3)

    # Headline + tagline
    draw_big_text(surf, "3,000", (W // 2, 78), size=72,
                  fill=COIN_GOLD, outline_w=5, sparkles=10)
    draw_tagline(surf, "GAMES PLAYED!", 132, size=24,
                 color=(255, 240, 200))
    draw_tagline(surf, "Next bucket's on you.", H - 38, size=18,
                 color=(255, 230, 200))


# --- V2 Gold Trophy --------------------------------------------------------

def draw_v2(surf):
    sky, pal = night_sky(0.62)   # warm dusk
    surf.blit(sky, (0, 0))

    # Starburst behind the trophy
    starburst(surf, W // 2, H // 2 - 20, 220, 90,
              (255, 220, 110), points=14)
    starburst(surf, W // 2, H // 2 - 20, 180, 60,
              (255, 240, 160), points=10)

    # Trophy cup body
    cx, cy = W // 2, H // 2 + 70
    cup_w, cup_h = 180, 130
    cup = pygame.Rect(cx - cup_w // 2, cy - cup_h, cup_w, cup_h)
    pygame.draw.rect(surf, OUTLINE, cup.inflate(6, 6),
                     border_radius=int(cup_h * 0.45))
    pygame.draw.rect(surf, TROPHY_DARK, cup.inflate(3, 3),
                     border_radius=int(cup_h * 0.45))
    pygame.draw.rect(surf, TROPHY_GOLD, cup,
                     border_radius=int(cup_h * 0.45))
    # Cup highlight stripe
    hl = pygame.Rect(cup.x + 14, cup.y + 14, 18, cup.height - 28)
    pygame.draw.rect(surf, GOLD_HI, hl, border_radius=8)
    # Engraved "3000" on the cup
    fnt = _font(40, bold=True)
    eng_dark = fnt.render("3000", True, TROPHY_DARK)
    eng_hi = fnt.render("3000", True, GOLD_HI)
    surf.blit(eng_dark, (cx - eng_dark.get_width() // 2 + 1,
                          cy - cup_h // 2 - eng_dark.get_height() // 2 + 1))
    surf.blit(eng_hi, (cx - eng_hi.get_width() // 2,
                        cy - cup_h // 2 - eng_hi.get_height() // 2 - 1))
    # Handles
    for sgn in (-1, 1):
        hx = cx + sgn * (cup_w // 2 + 4)
        hr = pygame.Rect(hx - 18 if sgn == -1 else hx - 2,
                          cup.y + 14, 30, 56)
        pygame.draw.ellipse(surf, OUTLINE, hr.inflate(6, 6))
        pygame.draw.ellipse(surf, TROPHY_GOLD, hr)
        # Cut out inner to make it a ring
        inner = hr.inflate(-14, -22)
        pygame.draw.ellipse(surf, sky.get_at((cx, cy))[:3], inner)
    # Stem
    stem = pygame.Rect(cx - 18, cy, 36, 36)
    pygame.draw.rect(surf, OUTLINE, stem.inflate(4, 4))
    pygame.draw.rect(surf, TROPHY_GOLD, stem)
    # Base
    base = pygame.Rect(cx - 70, cy + 36, 140, 28)
    pygame.draw.rect(surf, OUTLINE, base.inflate(4, 4), border_radius=4)
    pygame.draw.rect(surf, TROPHY_DARK, base.inflate(2, 2), border_radius=4)
    pygame.draw.rect(surf, TROPHY_GOLD, base, border_radius=4)

    # Pip with $ hat perched on top of the cup rim
    pip = parrot.get_hat_parrot(1, -8)
    surf.blit(pip, (cx - pip.get_width() // 2,
                    cup.top - pip.get_height() + 8))

    # Sparkles around the trophy
    rng = random.Random(42)
    for _ in range(12):
        sx = rng.randint(40, W - 40)
        sy = rng.randint(80, H - 110)
        r = rng.randint(2, 5)
        pygame.draw.circle(surf, OUTLINE, (sx, sy), r + 1)
        pygame.draw.circle(surf, GOLD_HI, (sx, sy), r)
        pygame.draw.circle(surf, (255, 255, 255), (sx - 1, sy - 1),
                           max(1, r - 2))

    # Headline
    draw_big_text(surf, "ACHIEVEMENT", (W // 2, 64), size=32,
                  fill=COIN_GOLD, outline_w=3, sparkles=0)
    draw_big_text(surf, "3,000 GAMES", (W // 2, 112), size=44,
                  fill=COIN_GOLD, outline_w=4, sparkles=8)

    # Tagline
    draw_tagline(surf, "Now do 5K.", H - 38, size=22,
                 color=(255, 255, 255))


# --- V3 Coin Shower --------------------------------------------------------

def draw_v3(surf):
    sky, pal = night_sky(0.30)
    surf.blit(sky, (0, 0))

    # Diagonal coin cascade - draw lots of gold coins behind Pip
    rng = random.Random(13)
    for _ in range(45):
        cx = rng.randint(-20, W + 20)
        cy = rng.randint(-20, H + 20)
        # Bias coins along diagonal: top-right to bottom-left
        diag_offset = (cx - cy) // 5
        cy += diag_offset
        r = rng.randint(8, 16)
        # Coin outline + body + shine
        pygame.draw.circle(surf, OUTLINE, (cx, cy), r + 1)
        pygame.draw.circle(surf, GOLD_LO, (cx, cy), r)
        pygame.draw.circle(surf, COIN_GOLD, (cx, cy), r - 1)
        pygame.draw.circle(surf, GOLD_HI, (cx - r // 3, cy - r // 3),
                            max(1, r // 3))

    # Pip in flap-pose, tilted upward, large + centered
    pip = parrot.get_parrot(0, 12)
    pip2 = pygame.transform.scale(pip,
                                  (pip.get_width() * 2,
                                   pip.get_height() * 2))
    surf.blit(pip2, ((W - pip2.get_width()) // 2,
                       H // 2 - pip2.get_height() // 2 + 30))

    # Big foreground headline
    draw_big_text(surf, "3,000!", (W // 2, 100), size=84,
                  fill=COIN_GOLD, outline_w=6, sparkles=14)
    draw_tagline(surf, "GAMES PLAYED", 168, size=22,
                 color=(255, 240, 200))
    draw_tagline(surf, "Can't stop. Won't stop.", H - 64, size=22,
                 color=(255, 255, 255))
    draw_tagline(surf, "One more run?", H - 36, size=18,
                 color=(255, 220, 160))


# --- V4 Pip Quartet --------------------------------------------------------

def draw_v4(surf):
    sky, pal = night_sky(0.50)
    surf.blit(sky, (0, 0))
    starfield(surf, n=50, seed=4)

    # 2x2 grid of Pip variants centered
    variants = [
        ("PIP",   parrot.get_parrot(1, -6)),
        ("KFC",   parrot.get_fried_parrot(1, -6)),
        ("GHOST", parrot.get_ghost_parrot(1, -6)),
        ("HAT",   parrot.get_hat_parrot(1, -6)),
    ]
    cell_w, cell_h = 140, 132
    grid_x = (W - cell_w * 2 - 10) // 2
    grid_y = 188
    for i, (name, img) in enumerate(variants):
        col = i % 2
        row = i // 2
        x = grid_x + col * (cell_w + 10)
        y = grid_y + row * (cell_h + 10)
        cell = pygame.Rect(x, y, cell_w, cell_h)
        pygame.draw.rect(surf, OUTLINE, cell.inflate(4, 4), border_radius=10)
        pygame.draw.rect(surf, (28, 38, 80), cell.inflate(2, 2),
                         border_radius=10)
        pygame.draw.rect(surf, (50, 70, 130), cell, border_radius=10)
        surf.blit(img, (cell.centerx - img.get_width() // 2,
                          cell.centery - img.get_height() // 2 - 6))
        lbl_fnt = _font(16, bold=True)
        lbl = lbl_fnt.render(name, True, COIN_GOLD)
        lbl_o = lbl_fnt.render(name, True, OUTLINE)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    surf.blit(lbl_o, (cell.centerx - lbl.get_width() // 2 + dx,
                                       cell.bottom - 22 + dy))
        surf.blit(lbl, (cell.centerx - lbl.get_width() // 2,
                          cell.bottom - 22))

    # Headline at top
    draw_big_text(surf, "3,000", (W // 2, 70), size=72,
                  fill=COIN_GOLD, outline_w=5, sparkles=12)
    draw_tagline(surf, "GAMES! THANK YOU!", 124, size=22,
                 color=(255, 240, 200))

    # Tagline at bottom
    draw_tagline(surf, "Dodge. Dip. Dive.", H - 62, size=20,
                 color=(255, 255, 255))
    draw_tagline(surf, "Your turn.", H - 34, size=22,
                 color=(255, 220, 160))


# --- V5 Newspaper Headline -------------------------------------------------

def draw_v5(surf):
    # Paper background
    surf.fill(PAPER_BG)
    # Paper grain - faint dots
    rng = random.Random(99)
    for _ in range(400):
        x = rng.randint(0, W - 1)
        y = rng.randint(0, H - 1)
        s = pygame.Surface((2, 2), pygame.SRCALPHA)
        s.fill((180, 160, 110, 40))
        surf.blit(s, (x, y))
    # Edge shadow vignette
    for i in range(8):
        a = 16 - i * 2
        if a <= 0:
            break
        pygame.draw.rect(surf, (60, 40, 10, a),
                         pygame.Rect(i, i, W - i * 2, H - i * 2),
                         width=1)

    # Masthead
    mast_fnt = _font(34, bold=True)
    txt = mast_fnt.render("SKYBIT TIMES", True, PAPER_INK)
    surf.blit(txt, (W // 2 - txt.get_width() // 2, 20))
    # Decorative double rules
    pygame.draw.line(surf, PAPER_RULE, (18, 60), (W - 18, 60), 2)
    pygame.draw.line(surf, PAPER_RULE, (18, 66), (W - 18, 66), 1)
    # Issue line
    iss_fnt = _font(12, bold=False)
    iss = iss_fnt.render("VOL. 1 | ISSUE 3000 | TODAY", True, PAPER_RULE)
    surf.blit(iss, (W // 2 - iss.get_width() // 2, 70))
    pygame.draw.line(surf, PAPER_RULE, (18, 88), (W - 18, 88), 1)

    # Big headline
    hd_fnt = _font(46, bold=True)
    for line, y in (("PIP HITS", 110), ("3,000!", 168)):
        out = hd_fnt.render(line, True, PAPER_INK)
        surf.blit(out, (W // 2 - out.get_width() // 2, y))

    # Subheadline
    sub_fnt = _font(16, bold=True)
    sub = sub_fnt.render("Scarlet macaw breaks four-figure barrier",
                         True, PAPER_INK)
    surf.blit(sub, (W // 2 - sub.get_width() // 2, 226))
    sub2 = sub_fnt.render("(again) - city in disbelief", True, PAPER_INK)
    surf.blit(sub2, (W // 2 - sub2.get_width() // 2, 246))

    # Photo frame with Pip portrait
    photo = pygame.Rect((W - 200) // 2, 278, 200, 200)
    pygame.draw.rect(surf, PAPER_INK, photo.inflate(6, 6))
    pygame.draw.rect(surf, (245, 235, 205), photo)
    # Sky inside photo
    photo_sky_pal = _biome.palette_for_phase(0.50)
    photo_sky = get_sky_surface_biome(photo.width, photo.height,
                                       photo.height, photo_sky_pal,
                                       int(0.50 * _biome.PHASE_BUCKETS))
    surf.blit(photo_sky, (photo.x, photo.y))
    # Pip in the photo, slightly enlarged
    pip = parrot.get_parrot(2, -4)
    pip_b = pygame.transform.scale(pip,
                                   (int(pip.get_width() * 1.6),
                                    int(pip.get_height() * 1.6)))
    surf.blit(pip_b, (photo.centerx - pip_b.get_width() // 2,
                       photo.centery - pip_b.get_height() // 2 + 6))
    # Caption under photo
    cap_fnt = _font(11, bold=False)
    cap = cap_fnt.render("PICTURED: Pip, mid-flap. Photo: STAFF.",
                          True, PAPER_RULE)
    surf.blit(cap, (W // 2 - cap.get_width() // 2, photo.bottom + 6))

    # Body / taunt
    body_fnt = _font(18, bold=True)
    body = body_fnt.render("Can YOU help him reach 5K?", True, PAPER_INK)
    surf.blit(body, (W // 2 - body.get_width() // 2, photo.bottom + 30))
    quote_fnt = _font(13, bold=False)
    q = quote_fnt.render('"Just one more run." - eyewitness',
                          True, PAPER_RULE)
    surf.blit(q, (W // 2 - q.get_width() // 2, photo.bottom + 56))


# --- Variant registry + main -----------------------------------------------

VARIANTS = (
    ("v1", "V1 Bucket Cake",        draw_v1),
    ("v2", "V2 Gold Trophy",        draw_v2),
    ("v3", "V3 Coin Shower",        draw_v3),
    ("v4", "V4 Pip Quartet",        draw_v4),
    ("v5", "V5 Newspaper Headline", draw_v5),
)


def main():
    random.seed(42)
    pygame.init()
    pygame.font.init()

    screen = pygame.display.set_mode((W, H))
    out_dir = os.path.join("docs", "celebrations", "3k_games")
    os.makedirs(out_dir, exist_ok=True)

    frames = {}
    for key, label, fn in VARIANTS:
        screen.fill((0, 0, 0))
        fn(screen)
        frames[key] = screen.copy()
        path = os.path.join(out_dir, f"{key}.png")
        pygame.image.save(screen, path)
        print(f"saved {path}  ({label})")

    # 5-column compare strip
    GAP, LABEL_H, PAD = 14, 30, 18
    cell_w, cell_h = W, H
    canvas_w = cell_w * len(VARIANTS) + GAP * (len(VARIANTS) - 1) + PAD * 2
    canvas_h = cell_h + LABEL_H + PAD * 2
    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((230, 232, 235))
    label_font = pygame.font.SysFont(None, 22, bold=True)
    for i, (key, label, _) in enumerate(VARIANTS):
        x = PAD + i * (cell_w + GAP)
        y = PAD
        pygame.draw.rect(canvas, (60, 70, 100),
                         pygame.Rect(x - 1, y - 1, cell_w + 2, cell_h + 2),
                         width=1)
        canvas.blit(frames[key], (x, y))
        lbl = label_font.render(label, True, (30, 35, 55))
        canvas.blit(lbl, (x + (cell_w - lbl.get_width()) // 2,
                          y + cell_h + 8))
    out_path = os.path.join(out_dir, "compare.png")
    pygame.image.save(canvas, out_path)
    print(f"saved {out_path}  {canvas.get_size()}")


if __name__ == "__main__":
    sys.exit(main() or 0)
