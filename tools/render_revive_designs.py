"""Visual design-exploration round for the "survive one hit / second life"
powerup (currently the fire Phoenix, whose look we're replacing).

Renders 5 candidate looks — each base Pip in a real gameplay frame + a
procedurally-composited accessory — side by side in one labeled image so
we can pick a direction. EXPLORATION ONLY: this tool never touches
game/config.py, world.py, or the powerup effect. It only reads
parrot.get_parrot + the shared gameplay-frame painter and composites
accessories onto a throwaway surface.

Candidates: knight (helm + shield), bubble (force-field), angel
(halo + wings), gold (armored/invincible), aegis (rune shield orb).

Run from repo root:
    SDL_VIDEODRIVER=dummy python -m tools.render_revive_designs
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import math
import pygame
pygame.init()

from game.config import W, H
from game import parrot
# Reuse the full-gameplay-frame painter + world setup from the genie tool.
from tools.render_genie_sizes import render_world, setup_world

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                       "docs", "screenshots", "revive_designs")
os.makedirs(OUT_DIR, exist_ok=True)


# ── helpers ──────────────────────────────────────────────────────────────────
def _blit_ss(surf, sx, sy, w, h, draw_fn, scale=4):
    """Draw `draw_fn(big, scale)` at `scale`× then smoothscale down and blit
    centred at (sx, sy) — gives smooth (anti-aliased) accessory edges."""
    big = pygame.Surface((w * scale, h * scale), pygame.SRCALPHA)
    draw_fn(big, scale)
    small = pygame.transform.smoothscale(big, (w, h))
    surf.blit(small, (int(sx - w / 2), int(sy - h / 2)))


def _reblit_pip(surf, bird):
    """Re-blit Pip's base sprite at his live centre — used to put a glow /
    bubble / gold body BEHIND him after it's painted on the frame."""
    fidx = int(bird.frame_t) % len(parrot.FRAMES)
    img = parrot.get_parrot(fidx, bird.tilt_deg)
    r = img.get_rect(center=(int(bird.x), int(bird.y)))
    surf.blit(img, r.topleft)


def _pip_sprite(bird):
    fidx = int(bird.frame_t) % len(parrot.FRAMES)
    return parrot.get_parrot(fidx, bird.tilt_deg)


def _soft_glow(surf, cx, cy, r, color, layers=5):
    """Concentric translucent circles → a soft radial glow (mirrors the
    phoenix fire-halo idea, recoloured)."""
    g = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
    c = r + 2
    for i in range(layers, 0, -1):
        rr = int(r * i / layers)
        a = int(70 * (1 - (i - 1) / layers))
        pygame.draw.circle(g, (*color, a), (c, c), rr)
    surf.blit(g, (int(cx - c), int(cy - c)))


def _star(surf, x, y, rad, color=(255, 255, 255), a=235):
    """A 4-point sparkle: two crossed tapered diamonds + a bright core."""
    s = pygame.Surface((rad * 2 + 4, rad * 2 + 4), pygame.SRCALPHA)
    c = rad + 2
    long_, short_ = rad, max(1, rad // 3)
    pygame.draw.polygon(s, (*color, a),
                        [(c, c - long_), (c + short_, c), (c, c + long_), (c - short_, c)])
    pygame.draw.polygon(s, (*color, a),
                        [(c - long_, c), (c, c - short_), (c + long_, c), (c, c + short_)])
    pygame.draw.circle(s, (255, 255, 255, a), (c, c), max(1, short_))
    surf.blit(s, (int(x - c), int(y - c)))


# ── candidate 1: KNIGHT (helm + kite shield + chest plate) ───────────────────
STEEL_D  = (70, 76, 90)
STEEL    = (150, 158, 170)
STEEL_HI = (210, 216, 228)
STEEL_OL = (34, 38, 48)
HERALD   = (172, 54, 52)
HERALD_HI = (220, 226, 236)


def draw_knight(surf, cx, cy, bird, frame_t):
    # Kite shield BEHIND Pip, flanking the tail (left) side.
    def shield(big, s):
        w, h = big.get_size()
        cxg = w // 2
        pts = [(cxg, int(2 * s)), (int(w - 3 * s), int(h * 0.32)),
               (cxg, int(h - 2 * s)), (int(3 * s), int(h * 0.32))]
        pygame.draw.polygon(big, STEEL_OL, pts)
        inner = [(cxg, int(5 * s)), (int(w - 6 * s), int(h * 0.34)),
                 (cxg, int(h - 5 * s)), (int(6 * s), int(h * 0.34))]
        pygame.draw.polygon(big, HERALD, inner)
        # chevron crest
        pygame.draw.lines(big, HERALD_HI, False,
                          [(int(8 * s), int(h * 0.40)), (cxg, int(h * 0.30)),
                           (int(w - 8 * s), int(h * 0.40))], int(2 * s))
        # centre boss
        pygame.draw.circle(big, STEEL_HI, (cxg, int(h * 0.5)), int(4 * s))
        pygame.draw.circle(big, (255, 255, 255), (cxg - s, int(h * 0.5) - s), int(1.5 * s))
    _blit_ss(surf, cx - 28, cy + 6, 26, 34, shield)
    # Re-blit Pip on top so the shield reads as held behind him.
    _reblit_pip(surf, bird)

    # Chest plate over the lower body, in front.
    def chest(big, s):
        w, h = big.get_size()
        pygame.draw.ellipse(big, STEEL, (int(2 * s), int(2 * s), int(w - 4 * s), int(h - 2 * s)))
        pygame.draw.arc(big, STEEL_HI, (int(4 * s), int(3 * s), int(w - 8 * s), int(h - 4 * s)),
                        math.radians(200), math.radians(340), int(2 * s))
        pygame.draw.circle(big, STEEL_D, (int(w * 0.35), int(h * 0.55)), int(1.6 * s))
        pygame.draw.circle(big, STEEL_D, (int(w * 0.65), int(h * 0.55)), int(1.6 * s))
    _blit_ss(surf, cx - 1, cy + 9, 26, 16, chest)

    # Helm on the head (head centre ≈ (cx+15, cy-9)).
    def helm(big, s):
        w, h = big.get_size()
        cxg = w // 2
        # dome
        pygame.draw.ellipse(big, STEEL_OL, (int(2 * s), int(2 * s), int(w - 4 * s), int(h * 0.82)))
        pygame.draw.ellipse(big, STEEL, (int(4 * s), int(4 * s), int(w - 8 * s), int(h * 0.78 - 2 * s)))
        pygame.draw.ellipse(big, STEEL_HI, (int(7 * s), int(6 * s), int(w * 0.45), int(h * 0.34)))
        # visor band + slit
        vy = int(h * 0.58)
        pygame.draw.rect(big, STEEL_D, (int(5 * s), vy, int(w - 10 * s), int(h * 0.20)))
        pygame.draw.rect(big, (12, 12, 16), (int(7 * s), vy + int(2 * s), int(w - 14 * s), int(3 * s)))
        for bx in range(0, 4):
            x = int(10 * s + bx * (w - 20 * s) / 3)
            pygame.draw.line(big, STEEL_HI, (x, vy), (x, vy + int(h * 0.20)), max(1, int(s // 2)))
        # red crest plume on top
        pygame.draw.polygon(big, (130, 30, 38),
                            [(cxg - int(2 * s), int(3 * s)), (cxg + int(2 * s), int(3 * s)),
                             (cxg + int(5 * s), int(-6 * s)), (cxg, int(-9 * s)),
                             (cxg - int(5 * s), int(-6 * s))])
        pygame.draw.polygon(big, HERALD,
                            [(cxg - int(2 * s), int(2 * s)), (cxg + int(2 * s), int(2 * s)),
                             (cxg + int(3 * s), int(-5 * s)), (cxg - int(3 * s), int(-5 * s))])
    _blit_ss(surf, cx + 15, cy - 13, 30, 30, helm)


# ── candidate 2: FORCE-FIELD BUBBLE ──────────────────────────────────────────
def draw_bubble(surf, cx, cy, bird, frame_t):
    R = 36
    # back: faint fill + back rim, BEHIND Pip
    back = pygame.Surface((R * 2 + 6, R * 2 + 6), pygame.SRCALPHA)
    c = R + 3
    pygame.draw.circle(back, (120, 200, 255, 46), (c, c), R)
    pygame.draw.circle(back, (150, 220, 255, 90), (c, c), R, 2)
    surf.blit(back, (int(cx - c), int(cy - c)))
    _reblit_pip(surf, bird)
    # front: bright rim, specular, iridescence, sparkles, ON TOP
    front = pygame.Surface((R * 2 + 6, R * 2 + 6), pygame.SRCALPHA)
    pygame.draw.circle(front, (190, 235, 255, 150), (c, c), R, 2)
    rect = pygame.Rect(c - R, c - R, R * 2, R * 2)
    pygame.draw.arc(front, (255, 255, 255, 170), rect, math.radians(70), math.radians(160), 3)
    pygame.draw.arc(front, (255, 180, 255, 80), rect.inflate(-6, -6), math.radians(20), math.radians(120), 2)
    pygame.draw.arc(front, (180, 255, 220, 80), rect.inflate(-4, -4), math.radians(200), math.radians(300), 2)
    surf.blit(front, (int(cx - c), int(cy - c)))
    for ang in (60, 150, 250, 330):
        sx = cx + math.cos(math.radians(ang)) * R
        sy = cy + math.sin(math.radians(ang)) * R
        _star(surf, sx, sy, 4, (235, 248, 255))


# ── candidate 3: GUARDIAN ANGEL (halo + wings + glow) ────────────────────────
def draw_angel(surf, cx, cy, bird, frame_t):
    _soft_glow(surf, cx, cy, 40, (255, 250, 210), layers=5)

    # wings behind Pip's body
    def wing(big, s, mirror=False):
        w, h = big.get_size()
        for i, col in enumerate(((210, 215, 230), (235, 238, 248), (252, 252, 255))):
            off = i * 2 * s
            pts = [(int(w * 0.5), int(h - 2 * s)),
                   (int(w - 2 * s - off), int(h * 0.5)),
                   (int(w - 4 * s - off), int(2 * s)),
                   (int(w * 0.55), int(h * 0.4))]
            if mirror:
                pts = [(w - px, py) for (px, py) in pts]
            pygame.draw.polygon(big, col, pts)
    _blit_ss(surf, cx - 16, cy - 8, 22, 30, lambda b, s: wing(b, s, mirror=True))
    _blit_ss(surf, cx + 6, cy - 8, 22, 30, lambda b, s: wing(b, s, mirror=False))
    _reblit_pip(surf, bird)

    # halo above the head
    def halo(big, s):
        w, h = big.get_size()
        pygame.draw.ellipse(big, (255, 240, 170, 90), (int(2 * s), int(2 * s), int(w - 4 * s), int(h - 4 * s)))
        pygame.draw.ellipse(big, (255, 215, 90), (int(3 * s), int(3 * s), int(w - 6 * s), int(h - 6 * s)), int(2.5 * s))
        pygame.draw.ellipse(big, (255, 250, 210), (int(5 * s), int(4 * s), int(w - 10 * s), int(h - 8 * s)), max(1, int(s)))
    _blit_ss(surf, cx + 13, cy - 27, 30, 12, halo)


# ── candidate 4: GOLDEN / ARMORED INVINCIBLE ─────────────────────────────────
def draw_gold(surf, cx, cy, bird, frame_t):
    _soft_glow(surf, cx, cy, 38, (255, 225, 130), layers=4)
    img = _pip_sprite(bird).copy()
    # metallic gold multiply tint (keeps the dark sunglasses dark)
    img.fill((230, 188, 70, 255), special_flags=pygame.BLEND_RGBA_MULT)
    # add a couple of bright shine ellipses
    sh = pygame.Surface(img.get_size(), pygame.SRCALPHA)
    iw, ih = img.get_size()
    pygame.draw.ellipse(sh, (255, 240, 170, 120), (int(iw * 0.48), int(ih * 0.18), int(iw * 0.22), int(ih * 0.16)))
    pygame.draw.ellipse(sh, (255, 235, 160, 90), (int(iw * 0.30), int(ih * 0.46), int(iw * 0.26), int(ih * 0.16)))
    img.blit(sh, (0, 0))
    r = img.get_rect(center=(int(cx), int(cy)))
    surf.blit(img, r.topleft)
    # star shimmer over + around the body
    for (dx, dy, rr) in ((-2, -10, 6), (12, -2, 5), (-14, 6, 4),
                         (6, 12, 5), (20, 14, 4), (-4, 18, 3)):
        _star(surf, cx + dx, cy + dy, rr, (255, 248, 200))


# ── candidate 5: AEGIS / RUNE SHIELD ORB ─────────────────────────────────────
def draw_aegis(surf, cx, cy, bird, frame_t):
    _soft_glow(surf, cx, cy, 36, (90, 180, 255), layers=4)
    _reblit_pip(surf, bird)
    # hexagonal energy plate in FRONT of the chest
    hx, hy, R = cx + 12, cy + 2, 22

    def hexa(big, s):
        w, h = big.get_size()
        cc = (w // 2, h // 2)
        outer = [(cc[0] + int((R - 1) * s * math.cos(math.radians(60 * k - 30))),
                  cc[1] + int((R - 1) * s * math.sin(math.radians(60 * k - 30)))) for k in range(6)]
        fill = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.polygon(fill, (80, 170, 255, 70), outer)
        big.blit(fill, (0, 0))
        pygame.draw.polygon(big, (150, 220, 255, 230), outer, int(2 * s))
        inner = [(cc[0] + int((R - 6) * s * math.cos(math.radians(60 * k - 30))),
                  cc[1] + int((R - 6) * s * math.sin(math.radians(60 * k - 30)))) for k in range(6)]
        pygame.draw.polygon(big, (190, 235, 255, 180), inner, max(1, int(s)))
        # simple glowing runes
        rc = (220, 245, 255)
        pygame.draw.lines(big, rc, False,
                          [(cc[0] - int(6 * s), cc[1] - int(4 * s)), (cc[0], cc[1] - int(9 * s)),
                           (cc[0] + int(6 * s), cc[1] - int(4 * s))], max(1, int(s)))
        pygame.draw.circle(big, rc, cc, int(3 * s), max(1, int(s)))
        pygame.draw.line(big, rc, (cc[0], cc[1] + int(3 * s)), (cc[0], cc[1] + int(8 * s)), max(1, int(s)))
    _blit_ss(surf, hx, hy, R * 2 + 6, R * 2 + 6, hexa)
    _star(surf, hx + R - 4, hy - R + 6, 4, (220, 245, 255))


CANDIDATES = [
    ("knight", "1  KNIGHT (helm + shield)", draw_knight),
    ("bubble", "2  FORCE-FIELD BUBBLE", draw_bubble),
    ("angel",  "3  GUARDIAN ANGEL", draw_angel),
    ("gold",   "4  GOLDEN ARMORED", draw_gold),
    ("aegis",  "5  AEGIS RUNE SHIELD", draw_aegis),
]


def _label(surf, text):
    f = pygame.font.SysFont("Arial", 15, bold=True)
    t = f.render(text, True, (255, 255, 255))
    bg = pygame.Surface((t.get_width() + 14, t.get_height() + 8), pygame.SRCALPHA)
    bg.fill((0, 0, 0, 175))
    surf.blit(bg, (6, H - 32))
    surf.blit(t, (13, H - 28))


def render_candidate(key, label, draw_fn):
    w = setup_world()
    BIRD_Y = H * 0.42
    for _ in range(8):
        w.bird.y = BIRD_Y; w.bird.vy = 0
        w.update(1 / 60.0)
    w.bird.y = BIRD_Y; w.bird.vy = 0
    surf = pygame.Surface((W, H))
    render_world(w, surf)
    draw_fn(surf, int(w.bird.x), int(w.bird.y), w.bird, w.bird.frame_t)
    _label(surf, label)
    return surf


def main():
    frames = []
    for key, label, fn in CANDIDATES:
        fr = render_candidate(key, label, fn)
        pygame.image.save(fr, os.path.join(OUT_DIR, f"revive_{key}.png"))
        frames.append(fr)
    # comparison sheet: 5 across, full-res, so the fine detail stays crisp
    margin = 12
    cols = len(frames)
    sheet = pygame.Surface((W * cols + margin * (cols + 1), H + margin * 2))
    sheet.fill((20, 22, 30))
    for i, fr in enumerate(frames):
        sheet.blit(fr, (margin + i * (W + margin), margin))
    out = os.path.join(OUT_DIR, "revive_designs.png")
    pygame.image.save(sheet, out)
    print(f"saved {out}  ({sheet.get_width()}x{sheet.get_height()})")
    print("per-candidate PNGs in", OUT_DIR)


if __name__ == "__main__":
    main()
