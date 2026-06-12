"""Look-dev mockup for the "Dice Clown" pre-warren clearing concept.

Before a Pagoda Warren route the parrot reaches a CLEARING WITH NO PAGODAS:
a large, charming, casual-game-friendly CLOWN stands on the ground, with a
DICE that reads as a POWER-UP floating above it — taking the dice rolls the
route length. This script renders ONE candidate sheet of 10 distinct clown
archetypes, each shown exactly as it would appear in gameplay (day sky +
clearing ground, drop-shadowed clown on the ground, glowing/sparkling
floating die, and the real parrot flying in from the left for scale).

Everything is drawn from pygame primitives — no PNG sprites. We import only
the REAL game helpers (sky/ground from the warren mockup, the biome palette,
the glow cache, and the live parrot sprite) and mutate no game state. Each
cell is supersampled at 2x then smoothscaled down for crisp anti-aliasing.

    PYTHONPATH=. python tools/render_clown_dice.py
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.config import W, H, GROUND_Y
from game.biome import palette_for_phase
from game.draw import lerp_color, blit_glow
from game.parrot import get_parrot
from tools.render_warren_mockup import shaped_palette


# Day phase for the clearing — matches the warren mockup's DAY column so the
# sheet reads as the same world a beat before the corridor.
DAY_PHASE = 0.05

# Supersample factor: draw each cell at SS x then smoothscale down so every
# curved clown edge and pip is anti-aliased.
SS = 2


# ── small colour helpers (local — never touch game state) ────────────────────

def _shade(c, d):
    return (max(0, min(255, int(c[0] + d))),
            max(0, min(255, int(c[1] + d))),
            max(0, min(255, int(c[2] + d))))


def _outline_ellipse(surf, color, rect, oc=None, w=1):
    """Filled ellipse + 1px darker keyline — the parrot's silhouette-clarity
    convention so a clown reads cleanly against the sky."""
    pygame.draw.ellipse(surf, color, rect)
    pygame.draw.ellipse(surf, oc or _shade(color, -70), rect, w)


def _poly(surf, color, pts, oc=None, w=1):
    pygame.draw.polygon(surf, color, pts)
    if oc is not False:
        pygame.draw.polygon(surf, oc or _shade(color, -70), pts, w)


# Shared ink / accent constants in the parrot family.
INK = (28, 22, 30)
WHITE = (250, 248, 244)
ROSY = (255, 150, 150)


# ── clown body kit ───────────────────────────────────────────────────────────
# Every clown is composited from the same primitive vocabulary so the ten read
# as ONE family of casual-cute characters that differ in silhouette, palette,
# hat and costume — not ten recolours. Coordinates are in the clown's own local
# space; `feet_y` is where the boots meet the ground and the body grows up.

def _shadow(surf, cx, feet_y, w, alpha=95):
    """Soft drop shadow ellipse at the feet — grounds the figure."""
    sh = pygame.Surface((w, w // 3 + 4), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (20, 18, 26, alpha), sh.get_rect())
    surf.blit(sh, (cx - w // 2, feet_y - 4))


def _boots(surf, cx, feet_y, sep, length, color, toe=None):
    """Big rounded clown shoes splayed left/right — the casual-cute footprint."""
    toe = toe or _shade(color, 30)
    for s in (-1, 1):
        bx = cx + s * sep
        shoe = pygame.Rect(0, 0, length, 13)
        if s < 0:
            shoe.topright = (bx + length // 3, feet_y)
        else:
            shoe.topleft = (bx - length // 3, feet_y)
        pygame.draw.ellipse(surf, color, shoe)
        pygame.draw.ellipse(surf, _shade(color, -60), shoe, 2)
        # Lit toe-cap so the rounded shoe catches light.
        cap = pygame.Rect(0, 0, length // 2, 7)
        cap.center = (shoe.centerx + s * length // 5, shoe.top + 4)
        pygame.draw.ellipse(surf, toe, cap)
        # Ankle joining the leg.
        pygame.draw.line(surf, _shade(color, -40),
                         (bx, feet_y - 8), (bx, feet_y - 1), 4)


def _legs(surf, cx, hip_y, feet_y, sep, color, stripe=None):
    """Two tapered legs from hips to ankles, optional vertical stripe tights."""
    for s in (-1, 1):
        ax = cx + s * sep
        hx = cx + s * (sep - 3)
        pygame.draw.line(surf, _shade(color, -45), (hx, hip_y), (ax, feet_y - 7), 9)
        pygame.draw.line(surf, color, (hx, hip_y), (ax, feet_y - 7), 6)
        if stripe is not None:
            pygame.draw.line(surf, stripe, (hx, hip_y + 2), (ax, feet_y - 9), 2)


def _round_head(surf, cx, cy, r, skin, *, blush=True, white_face=False):
    """Round friendly head. Whiteface clowns get a chalk-white base instead of
    skin. Always rosy-cheeked + a 1px keyline for casual-cute warmth."""
    base = WHITE if white_face else skin
    _outline_ellipse(surf, base, (cx - r, cy - r, r * 2, r * 2),
                     oc=_shade(base, -55), w=2)
    # Top sheen.
    sheen = pygame.Surface((r, r), pygame.SRCALPHA)
    pygame.draw.ellipse(sheen, (255, 255, 255, 60), sheen.get_rect())
    surf.blit(sheen, (cx - r + 2, cy - r + 2))
    if blush:
        for s in (-1, 1):
            pygame.draw.ellipse(surf, ROSY,
                                (cx + s * (r - 7) - 4, cy + 1, 8, 6))


def _eyes(surf, cx, cy, r, *, happy=True, sad=False, color=INK):
    """Friendly eyes. happy=upturned smile-eyes; sad=downturned for Pierrot."""
    ex = max(4, r // 2 - 1)
    for s in (-1, 1):
        px = cx + s * ex
        if sad:
            pygame.draw.circle(surf, color, (px, cy), 3)
            pygame.draw.circle(surf, WHITE, (px - 1, cy - 1), 1)
        elif happy:
            pygame.draw.arc(surf, color,
                            (px - 4, cy - 2, 8, 7), math.pi, math.tau, 2)
        else:
            pygame.draw.circle(surf, WHITE, (px, cy), 3)
            pygame.draw.circle(surf, color, (px, cy + 1), 2)


def _nose(surf, cx, cy, r, color=(230, 50, 50), highlight=True):
    """The signature ball nose."""
    pygame.draw.circle(surf, _shade(color, -55), (cx, cy), r + 1, 1)
    pygame.draw.circle(surf, color, (cx, cy), r)
    if highlight:
        pygame.draw.circle(surf, _shade(color, 90), (cx - r // 2, cy - r // 2),
                           max(1, r // 3))


def _smile(surf, cx, cy, w, color=(200, 60, 70), lips=True):
    """Big warm grin — an upward arc with a lighter inner mouth."""
    rect = (cx - w // 2, cy - w // 3, w, int(w * 0.8))
    pygame.draw.arc(surf, color, rect, math.pi * 1.05, math.tau * 0.97, 3)
    if lips:
        pygame.draw.arc(surf, _shade(color, 80), rect,
                        math.pi * 1.1, math.tau * 0.95, 1)


def _ruff(surf, cx, cy, r, color, lobes=9):
    """Ruffled neck collar — a ring of overlapping scallops."""
    for i in range(lobes):
        a = i * math.tau / lobes
        lx = cx + math.cos(a) * r
        ly = cy + math.sin(a) * r * 0.55
        rad = r // 3 + 2
        pygame.draw.circle(surf, _shade(color, -45), (int(lx), int(ly)), rad)
        pygame.draw.circle(surf, color, (int(lx), int(ly)), rad - 1)
    pygame.draw.circle(surf, _shade(color, 35), (cx, cy), r // 2)
    pygame.draw.circle(surf, _shade(color, -30), (cx, cy), r // 2, 1)


def _pompoms(surf, cx, top_y, bot_y, color, n=3):
    """Vertical row of costume pom-pom buttons."""
    for i in range(n):
        t = i / max(1, n - 1)
        py = int(top_y + (bot_y - top_y) * t)
        pygame.draw.circle(surf, _shade(color, -50), (cx, py), 4)
        pygame.draw.circle(surf, color, (cx, py), 3)
        pygame.draw.circle(surf, _shade(color, 70), (cx - 1, py - 1), 1)


# ── the floating power-up DIE ─────────────────────────────────────────────────
# Drawn with the REAL power-up conventions: warm gold radial glow halo via the
# cached glow surface (BLEND_ADD), a bobbing rounded-square die body, classic
# d6 pips OR a 2-digit roll number, and a ring of pulsing sparkle twinkles.

_PIP_LAYOUT = {
    1: [(0.5, 0.5)],
    2: [(0.28, 0.28), (0.72, 0.72)],
    3: [(0.26, 0.26), (0.5, 0.5), (0.74, 0.74)],
    4: [(0.28, 0.28), (0.72, 0.28), (0.28, 0.72), (0.72, 0.72)],
    5: [(0.26, 0.26), (0.74, 0.26), (0.5, 0.5), (0.26, 0.74), (0.74, 0.74)],
    6: [(0.28, 0.24), (0.72, 0.24), (0.28, 0.5), (0.72, 0.5),
        (0.28, 0.76), (0.72, 0.76)],
}


def _draw_die_face(surf, cx, cy, size, *, pips=None, number=None,
                   body=(252, 250, 244), pip_col=(40, 36, 52)):
    """A single rounded-square die face. `pips` draws the d6 dot layout;
    `number` draws a 2-digit roll to hint the route-length mechanic."""
    half = size // 2
    rect = pygame.Rect(cx - half, cy - half, size, size)
    # Soft cast shadow under the die for float.
    sh = pygame.Surface((size + 6, size // 2), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (20, 16, 30, 70), sh.get_rect())
    surf.blit(sh, (cx - half - 3, cy + half - 2))
    # Body with a top-down sheen gradient baked via two stacked rounded rects.
    pygame.draw.rect(surf, _shade(body, -60), rect, border_radius=size // 5)
    inner = rect.inflate(-3, -3)
    pygame.draw.rect(surf, body, inner, border_radius=size // 5)
    pygame.draw.rect(surf, _shade(body, 25),
                     pygame.Rect(inner.x, inner.y, inner.w, inner.h // 2),
                     border_radius=size // 6)
    pygame.draw.rect(surf, _shade(body, -70), rect, 2, border_radius=size // 5)
    if number is not None:
        f = pygame.font.SysFont(None, int(size * 0.7), bold=True)
        txt = f.render(str(number), True, pip_col)
        surf.blit(txt, (cx - txt.get_width() // 2, cy - txt.get_height() // 2))
    elif pips is not None:
        pr = max(2, size // 9)
        for fx, fy in _PIP_LAYOUT[pips]:
            px = rect.x + int(fx * size)
            py = rect.y + int(fy * size)
            pygame.draw.circle(surf, _shade(pip_col, -25), (px, py), pr)
            pygame.draw.circle(surf, pip_col, (px, py), pr - 1)
            pygame.draw.circle(surf, _shade(pip_col, 120), (px - 1, py - 1), 1)


def draw_floating_die(surf, cx, base_y, pulse, *, number=None, pips=5):
    """The complete power-up read: gold glow halo + bobbing die + sparkles.

    `pulse` is a free-running phase (seconds-like) so the die bobs and the
    sparkles twinkle deterministically. One cell in the sheet shows a 2-digit
    `number` to hint the roll mechanic; the rest show classic pips."""
    cy = int(base_y + math.sin(pulse * 1.1) * 3)
    size = 30

    # Warm gold radial glow halo behind the die (BLEND_ADD via the glow cache).
    glow_r = 34
    blit_glow(surf, cx, cy, glow_r, (255, 210, 90),
              alpha=130 + int(30 * (0.5 + 0.5 * math.sin(pulse * 1.3))))
    blit_glow(surf, cx, cy, glow_r - 12, (255, 245, 200), alpha=120)

    _draw_die_face(surf, cx, cy, size, pips=pips, number=number)

    # Sparkle twinkles orbiting the die — Coin sparkle style: small pulsing
    # 4-point stars at staggered phases.
    for i in range(8):
        a = i * math.tau / 8 + pulse * 0.35
        rr = 26 + 4 * math.sin(pulse * 0.9 + i)
        sx = int(cx + math.cos(a) * rr)
        sy = int(cy + math.sin(a) * rr * 0.85)
        tw = 0.5 + 0.5 * math.sin(pulse * 2.0 + i * 1.7)
        al = int(90 + 140 * tw)
        sz = 2 + int(2 * tw)
        spark = pygame.Surface((sz * 4, sz * 4), pygame.SRCALPHA)
        c = (255, 244, 200, al)
        pygame.draw.line(spark, c, (sz * 2, 0), (sz * 2, sz * 4), 1)
        pygame.draw.line(spark, c, (0, sz * 2), (sz * 4, sz * 2), 1)
        pygame.draw.circle(spark, (255, 255, 230, al), (sz * 2, sz * 2), sz)
        surf.blit(spark, (sx - sz * 2, sy - sz * 2),
                  special_flags=pygame.BLEND_ADD)


# ── the ten clowns ────────────────────────────────────────────────────────────
# Each draws ONE clown standing on the ground at (cx, feet_y). The brief target
# is ~180-220px tall at game scale; all ten share the boots/legs/head kit but
# own a distinct silhouette via hat, collar, costume mass and palette.

def clown_whiteface(surf, cx, feet_y):
    """Elegant noble whiteface: chalk face, tall blue cone hat, huge red ruff."""
    hip_y = feet_y - 78
    _boots(surf, cx, feet_y, 14, 26, (40, 60, 150))
    _legs(surf, cx, hip_y, feet_y, 9, (235, 235, 240))
    # Elegant tapered tunic.
    _poly(surf, (210, 40, 60),
          [(cx - 24, hip_y + 6), (cx + 24, hip_y + 6),
           (cx + 16, hip_y - 46), (cx - 16, hip_y - 46)])
    _pompoms(surf, cx, hip_y - 40, hip_y, (250, 240, 120), 4)
    neck_y = hip_y - 46
    _ruff(surf, cx, neck_y, 22, (235, 235, 245), lobes=11)
    hr = 19
    hy = neck_y - hr - 6
    _round_head(surf, cx, hy, hr, None, white_face=True)
    _eyes(surf, cx, hy - 2, hr, happy=True)
    # Delicate red star accents over the eyes (whiteface signature).
    for s in (-1, 1):
        pygame.draw.circle(surf, (210, 40, 60), (cx + s * 9, hy - 9), 2)
    _nose(surf, cx, hy + 4, 4, (220, 70, 90))
    _smile(surf, cx, hy + 9, 16, (200, 50, 70))
    # Tall blue cone hat with gold band.
    tip = (cx + 6, hy - hr - 40)
    _poly(surf, (40, 70, 175),
          [(cx - 15, hy - hr + 2), (cx + 15, hy - hr + 2), tip])
    pygame.draw.line(surf, (250, 230, 110),
                     (cx - 13, hy - hr - 4), (cx + 13, hy - hr - 4), 3)
    pygame.draw.circle(surf, (250, 240, 130), tip, 4)


def clown_auguste(surf, cx, feet_y):
    """Classic Auguste: flesh face, big red ball nose, baggy mismatched suit,
    tiny hat, oversized bow tie."""
    hip_y = feet_y - 70
    _boots(surf, cx, feet_y, 17, 32, (180, 60, 50))
    _legs(surf, cx, hip_y, feet_y, 11, (90, 140, 210))
    # Oversized baggy jacket — a big rounded trapezoid for the comic bulk.
    _poly(surf, (60, 120, 190),
          [(cx - 30, hip_y + 8), (cx + 30, hip_y + 8),
           (cx + 20, hip_y - 40), (cx - 20, hip_y - 40)])
    # Mismatched green lapels.
    _poly(surf, (90, 180, 90),
          [(cx - 18, hip_y - 38), (cx - 4, hip_y - 38), (cx - 10, hip_y - 8)],
          oc=False)
    _poly(surf, (90, 180, 90),
          [(cx + 18, hip_y - 38), (cx + 4, hip_y - 38), (cx + 10, hip_y - 8)],
          oc=False)
    _pompoms(surf, cx, hip_y - 32, hip_y - 2, (250, 230, 80), 3)
    neck_y = hip_y - 40
    # Oversized polka-dot bow tie.
    for s in (-1, 1):
        _poly(surf, (240, 80, 70),
              [(cx, neck_y), (cx + s * 16, neck_y - 8),
               (cx + s * 16, neck_y + 8)])
    pygame.draw.circle(surf, (250, 230, 80), (cx, neck_y), 4)
    hr = 21
    hy = neck_y - hr
    _round_head(surf, cx, hy, hr, (255, 205, 165))
    # White eye + mouth patches (Auguste signature).
    for s in (-1, 1):
        pygame.draw.ellipse(surf, WHITE, (cx + s * 9 - 6, hy - 9, 12, 11))
    _eyes(surf, cx, hy - 3, hr, happy=False)
    _nose(surf, cx, hy + 4, 8, (235, 40, 40))
    pygame.draw.ellipse(surf, WHITE, (cx - 12, hy + 9, 24, 12))
    _smile(surf, cx, hy + 10, 20, (210, 60, 70))
    # Tiny derby hat tilted.
    pygame.draw.ellipse(surf, (70, 60, 60), (cx - 12, hy - hr - 2, 24, 6))
    pygame.draw.rect(surf, (70, 60, 60), (cx - 7, hy - hr - 10, 14, 9),
                     border_radius=3)
    pygame.draw.circle(surf, (240, 90, 80), (cx + 8, hy - hr - 6), 3)


def clown_tramp(surf, cx, feet_y):
    """Charming-sad hobo tramp: patched tattered coat, battered bowler,
    white-around-mouth, stubble shading."""
    hip_y = feet_y - 72
    _boots(surf, cx, feet_y, 14, 28, (70, 55, 45))
    _legs(surf, cx, hip_y, feet_y, 10, (95, 80, 65))
    # Tattered patched coat — uneven ragged hem.
    _poly(surf, (110, 92, 72),
          [(cx - 26, hip_y + 10), (cx - 18, hip_y + 2), (cx - 6, hip_y + 10),
           (cx + 8, hip_y + 1), (cx + 22, hip_y + 9), (cx + 26, hip_y + 6),
           (cx + 18, hip_y - 42), (cx - 18, hip_y - 42)])
    # Coloured patches.
    for px, py, pc in (((cx - 12), hip_y - 20, (180, 90, 80)),
                       ((cx + 10), hip_y - 8, (90, 120, 150)),
                       ((cx + 2), hip_y - 28, (150, 140, 80))):
        pygame.draw.rect(surf, pc, (px - 5, py - 5, 10, 10))
        pygame.draw.rect(surf, _shade(pc, -50), (px - 5, py - 5, 10, 10), 1)
    neck_y = hip_y - 42
    # Loose collar.
    _poly(surf, (140, 120, 95), [(cx - 14, neck_y - 2), (cx + 14, neck_y - 2),
                                 (cx, neck_y + 8)], oc=False)
    hr = 19
    hy = neck_y - hr + 2
    _round_head(surf, cx, hy, hr, (225, 180, 150))
    # 5-o'clock stubble shading on the lower face.
    stub = pygame.Surface((hr * 2, hr), pygame.SRCALPHA)
    pygame.draw.ellipse(stub, (70, 55, 50, 70), stub.get_rect())
    surf.blit(stub, (cx - hr, hy + 2))
    _eyes(surf, cx, hy - 3, hr, happy=True)
    _nose(surf, cx, hy + 3, 6, (210, 110, 90))
    # Big white mouth-patch — the tramp's signature.
    pygame.draw.ellipse(surf, WHITE, (cx - 13, hy + 6, 26, 14))
    _smile(surf, cx, hy + 11, 18, (170, 70, 70))
    # Battered bowler with a dent.
    pygame.draw.ellipse(surf, (55, 48, 42), (cx - 16, hy - hr, 32, 7))
    pygame.draw.rect(surf, (62, 54, 48), (cx - 10, hy - hr - 11, 20, 12),
                     border_radius=5)
    pygame.draw.line(surf, (40, 34, 30), (cx - 4, hy - hr - 9),
                     (cx + 3, hy - hr - 6), 2)


def clown_pierrot(surf, cx, feet_y):
    """Soft sad Pierrot: loose white silk, big black-button placket, skullcap,
    single blue teardrop."""
    hip_y = feet_y - 80
    _boots(surf, cx, feet_y, 11, 22, (235, 235, 240))
    _legs(surf, cx, hip_y, feet_y, 8, (245, 245, 250))
    # Loose flowing silk smock — wide soft bell.
    _poly(surf, (244, 244, 250),
          [(cx - 30, hip_y + 12), (cx + 30, hip_y + 12),
           (cx + 14, hip_y - 44), (cx - 14, hip_y - 44)],
          oc=_shade((244, 244, 250), -45))
    # Big black buttons down the placket.
    for i in range(3):
        by = hip_y - 32 + i * 14
        pygame.draw.circle(surf, (40, 40, 55), (cx, by), 4)
    neck_y = hip_y - 44
    _ruff(surf, cx, neck_y, 20, (250, 250, 255), lobes=12)
    hr = 19
    hy = neck_y - hr - 4
    _round_head(surf, cx, hy, hr, None, white_face=True, blush=False)
    _eyes(surf, cx, hy - 2, hr, happy=False, sad=True)
    # Single blue teardrop — the Pierrot signature, gentle not creepy.
    pygame.draw.circle(surf, (90, 160, 230), (cx - 8, hy + 5), 2)
    pygame.draw.polygon(surf, (90, 160, 230),
                        [(cx - 9, hy + 3), (cx - 7, hy + 3), (cx - 8, hy + 6)])
    _nose(surf, cx, hy + 4, 4, (210, 120, 150))
    # Soft small frown-turned-gentle smile.
    pygame.draw.arc(surf, (170, 110, 130), (cx - 8, hy + 8, 16, 8),
                    math.pi * 1.1, math.tau * 0.95, 2)
    # Black skullcap.
    pygame.draw.ellipse(surf, (45, 45, 60), (cx - hr, hy - hr - 2, hr * 2, hr))
    pygame.draw.ellipse(surf, _shade((45, 45, 60), 30),
                        (cx - hr + 3, hy - hr, hr, hr // 2))


def clown_harlequin(surf, cx, feet_y):
    """Mischievous Harlequin: tight diamond-patch motley, felt hat, half-mask."""
    hip_y = feet_y - 78
    diamonds = [(210, 50, 70), (250, 200, 60), (60, 140, 170), (90, 170, 90)]

    def _motley(rect):
        """Fill a rect with a tight diamond-patch grid clipped to the body."""
        clip = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
        step = 11
        for row in range(-1, rect.h // step + 2):
            for col in range(-1, rect.w // step + 2):
                dx = col * step + (step // 2 if row % 2 else 0)
                dy = row * step
                c = diamonds[(row + col) % len(diamonds)]
                pygame.draw.polygon(clip, c, [
                    (dx, dy - step // 2), (dx + step // 2, dy),
                    (dx, dy + step // 2), (dx - step // 2, dy)])
        return clip, rect

    _boots(surf, cx, feet_y, 13, 24, (40, 40, 55))
    _legs(surf, cx, hip_y, feet_y, 9, (210, 50, 70), stripe=(250, 200, 60))
    # Tight motley torso.
    body_rect = pygame.Rect(cx - 19, hip_y - 46, 38, 56)
    motley, _ = _motley(body_rect)
    bmask = pygame.Surface(body_rect.size, pygame.SRCALPHA)
    _poly(bmask, (255, 255, 255),
          [(0, body_rect.h), (body_rect.w, body_rect.h),
           (body_rect.w - 6, 0), (6, 0)], oc=False)
    motley.blit(bmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(motley, body_rect.topleft)
    pygame.draw.polygon(surf, INK,
                        [(cx - 19, hip_y + 10), (cx + 19, hip_y + 10),
                         (cx + 13, hip_y - 46), (cx - 13, hip_y - 46)], 1)
    neck_y = hip_y - 46
    _ruff(surf, cx, neck_y, 16, (250, 245, 230), lobes=10)
    hr = 18
    hy = neck_y - hr - 2
    _round_head(surf, cx, hy, hr, (255, 210, 170))
    # Black half-mask over the upper face — mischievous, not scary.
    pygame.draw.ellipse(surf, (35, 35, 50), (cx - hr + 1, hy - 8, hr * 2 - 2, 13))
    for s in (-1, 1):
        pygame.draw.circle(surf, WHITE, (cx + s * 8, hy - 2), 3)
        pygame.draw.circle(surf, INK, (cx + s * 8 + s, hy - 1), 1)
    _nose(surf, cx, hy + 5, 5, (235, 90, 90))
    pygame.draw.arc(surf, (180, 70, 80), (cx - 8, hy + 7, 16, 9),
                    math.pi * 1.05, math.tau * 0.97, 2)
    # Felt bicorne hat with a feather.
    pygame.draw.polygon(surf, (90, 40, 110),
                        [(cx - 16, hy - hr + 3), (cx + 16, hy - hr + 3),
                         (cx + 8, hy - hr - 10), (cx - 8, hy - hr - 10)])
    pygame.draw.polygon(surf, _shade((90, 40, 110), -50),
                        [(cx - 16, hy - hr + 3), (cx + 16, hy - hr + 3),
                         (cx + 8, hy - hr - 10), (cx - 8, hy - hr - 10)], 1)
    pygame.draw.line(surf, (250, 220, 90), (cx + 6, hy - hr - 8),
                     (cx + 16, hy - hr - 18), 2)


def clown_jester(surf, cx, feet_y):
    """Court jester: three-point belled fool's cap, two-tone tights,
    mismatched bright tunic."""
    hip_y = feet_y - 76
    PURPLE, GREEN, GOLD = (120, 60, 170), (70, 165, 95), (250, 205, 70)
    _boots(surf, cx, feet_y, 12, 22, (200, 60, 70), toe=(250, 210, 100))
    # Two-tone harlequin tights (split down the middle).
    pygame.draw.line(surf, _shade(PURPLE, -45), (cx - 6, hip_y),
                     (cx - 11, feet_y - 7), 8)
    pygame.draw.line(surf, PURPLE, (cx - 6, hip_y), (cx - 11, feet_y - 7), 6)
    pygame.draw.line(surf, _shade(GREEN, -45), (cx + 6, hip_y),
                     (cx + 11, feet_y - 7), 8)
    pygame.draw.line(surf, GREEN, (cx + 6, hip_y), (cx + 11, feet_y - 7), 6)
    # Mismatched split tunic — left purple, right green, scalloped hem.
    _poly(surf, PURPLE, [(cx - 22, hip_y + 8), (cx, hip_y + 8),
                         (cx, hip_y - 44), (cx - 15, hip_y - 44)])
    _poly(surf, GREEN, [(cx, hip_y + 8), (cx + 22, hip_y + 8),
                        (cx + 15, hip_y - 44), (cx, hip_y - 44)])
    # Scalloped belt line.
    for i in range(6):
        bx = cx - 18 + i * 7
        pygame.draw.circle(surf, GOLD, (bx, hip_y + 5), 3)
    neck_y = hip_y - 44
    # Three-point belled collar.
    for s in (-1, 0, 1):
        tx = cx + s * 13
        _poly(surf, GOLD, [(cx, neck_y), (tx - 5, neck_y + 14),
                           (tx + 5, neck_y + 14)], oc=_shade(GOLD, -60))
        pygame.draw.circle(surf, (240, 235, 200), (tx, neck_y + 15), 3)
    hr = 18
    hy = neck_y - hr
    _round_head(surf, cx, hy, hr, (255, 208, 168))
    _eyes(surf, cx, hy - 2, hr, happy=True)
    _nose(surf, cx, hy + 4, 5, (230, 70, 70))
    _smile(surf, cx, hy + 9, 16, (195, 60, 70))
    # Three-point fool's cap with bells.
    for s, col in ((-1, PURPLE), (0, GOLD), (1, GREEN)):
        bx = cx + s * 13
        _poly(surf, col, [(cx - 14, hy - hr + 2), (cx + 14, hy - hr + 2),
                          (bx, hy - hr - 22)], oc=_shade(col, -55))
        pygame.draw.circle(surf, (245, 240, 200), (bx, hy - hr - 22), 3)


def clown_ringmaster(surf, cx, feet_y):
    """Circus-host showman: top hat, red tailcoat, big gold bow tie,
    white jodhpurs + black boots."""
    hip_y = feet_y - 74
    RED, GOLD = (190, 40, 50), (240, 200, 90)
    _boots(surf, cx, feet_y, 13, 22, (35, 32, 40))
    _legs(surf, cx, hip_y, feet_y, 10, (245, 240, 235))
    # Red tailcoat — body plus two tails hanging below the hip.
    _poly(surf, RED, [(cx - 22, hip_y + 4), (cx + 22, hip_y + 4),
                      (cx + 16, hip_y - 44), (cx - 16, hip_y - 44)])
    for s in (-1, 1):
        _poly(surf, _shade(RED, -25),
              [(cx + s * 6, hip_y + 2), (cx + s * 20, hip_y + 4),
               (cx + s * 16, hip_y + 22), (cx + s * 8, hip_y + 18)])
    # Gold double-breasted button rows.
    for i in range(3):
        for s in (-1, 1):
            pygame.draw.circle(surf, GOLD, (cx + s * 7, hip_y - 32 + i * 12), 3)
    # White waistcoat V.
    _poly(surf, (245, 240, 232),
          [(cx - 9, hip_y - 40), (cx + 9, hip_y - 40), (cx, hip_y - 8)],
          oc=_shade((245, 240, 232), -50))
    neck_y = hip_y - 42
    # Big gold bow tie.
    for s in (-1, 1):
        _poly(surf, GOLD, [(cx, neck_y), (cx + s * 13, neck_y - 7),
                           (cx + s * 13, neck_y + 7)])
    pygame.draw.circle(surf, _shade(GOLD, -50), (cx, neck_y), 3)
    hr = 18
    hy = neck_y - hr
    _round_head(surf, cx, hy, hr, (255, 206, 166))
    _eyes(surf, cx, hy - 2, hr, happy=True)
    # Curled showman moustache.
    pygame.draw.arc(surf, (90, 60, 40), (cx - 9, hy + 4, 9, 7), 0, math.pi, 2)
    pygame.draw.arc(surf, (90, 60, 40), (cx, hy + 4, 9, 7), 0, math.pi, 2)
    _nose(surf, cx, hy + 3, 4, (225, 110, 110))
    _smile(surf, cx, hy + 10, 12, (180, 70, 70))
    # Tall black top hat with red band.
    pygame.draw.ellipse(surf, (30, 28, 36), (cx - 17, hy - hr - 1, 34, 8))
    pygame.draw.rect(surf, (35, 32, 42), (cx - 12, hy - hr - 24, 24, 24),
                     border_radius=3)
    pygame.draw.rect(surf, RED, (cx - 12, hy - hr - 7, 24, 5))
    pygame.draw.rect(surf, _shade((35, 32, 42), 40),
                     (cx - 10, hy - hr - 22, 5, 18))


def clown_mascot(surf, cx, feet_y):
    """Max casual-cute mascot: round chibi proportions, rosy cheeks, holding
    a balloon on a string."""
    hip_y = feet_y - 58
    BODY = (95, 185, 220)
    _boots(surf, cx, feet_y, 12, 22, (250, 210, 90))
    # Stubby legs.
    for s in (-1, 1):
        pygame.draw.line(surf, BODY, (cx + s * 7, hip_y + 4),
                         (cx + s * 9, feet_y - 7), 9)
    # Big round belly-body (chibi).
    _outline_ellipse(surf, BODY, (cx - 26, hip_y - 38, 52, 50),
                     oc=_shade(BODY, -55), w=2)
    pygame.draw.ellipse(surf, (245, 250, 252), (cx - 15, hip_y - 18, 30, 28))
    _pompoms(surf, cx, hip_y - 26, hip_y + 2, (240, 100, 110), 3)
    # Stubby arm holding a balloon string.
    pygame.draw.line(surf, BODY, (cx + 22, hip_y - 28), (cx + 34, hip_y - 40), 7)
    pygame.draw.line(surf, (230, 230, 235), (cx + 34, hip_y - 40),
                     (cx + 40, hip_y - 78), 1)
    # Balloon.
    _outline_ellipse(surf, (235, 80, 95), (cx + 30, hip_y - 100, 22, 26),
                     oc=_shade((235, 80, 95), -55))
    pygame.draw.ellipse(surf, (255, 180, 185), (cx + 35, hip_y - 96, 7, 8))
    pygame.draw.polygon(surf, (235, 80, 95),
                        [(cx + 39, hip_y - 76), (cx + 43, hip_y - 76),
                         (cx + 41, hip_y - 72)])
    hr = 23
    hy = hip_y - 38 - hr + 6
    _round_head(surf, cx, hy, hr, (255, 222, 190))
    _eyes(surf, cx, hy - 1, hr, happy=False)
    # Extra-big sparkly pupils for max cute.
    for s in (-1, 1):
        pygame.draw.circle(surf, WHITE, (cx + s * 10, hy - 1), 5)
        pygame.draw.circle(surf, (50, 45, 65), (cx + s * 10, hy + 1), 3)
        pygame.draw.circle(surf, WHITE, (cx + s * 10 - 1, hy - 2), 1)
    _nose(surf, cx, hy + 6, 5, (240, 120, 120))
    _smile(surf, cx, hy + 11, 16, (210, 90, 100))
    # Tiny party cone hat.
    _poly(surf, (250, 200, 80),
          [(cx - 9, hy - hr + 3), (cx + 9, hy - hr + 3), (cx, hy - hr - 16)])
    pygame.draw.circle(surf, (240, 100, 110), (cx, hy - hr - 16), 3)


def clown_rainbow(surf, cx, feet_y):
    """Classic party clown: red/yellow/blue suit, rainbow wig, pom-pom buttons,
    huge floppy shoes."""
    hip_y = feet_y - 70
    _boots(surf, cx, feet_y, 18, 38, (220, 40, 50), toe=(250, 220, 90))
    _legs(surf, cx, hip_y, feet_y, 12, (240, 200, 60))
    # Bright blue jumpsuit body.
    _poly(surf, (60, 110, 210),
          [(cx - 26, hip_y + 8), (cx + 26, hip_y + 8),
           (cx + 16, hip_y - 42), (cx - 16, hip_y - 42)])
    # Big rainbow pom-pom buttons.
    btn_cols = [(230, 50, 60), (250, 210, 70), (90, 190, 100), (230, 50, 60)]
    for i, c in enumerate(btn_cols):
        by = hip_y - 34 + i * 12
        pygame.draw.circle(surf, _shade(c, -50), (cx, by), 6)
        pygame.draw.circle(surf, c, (cx, by), 5)
        pygame.draw.circle(surf, _shade(c, 80), (cx - 2, by - 2), 2)
    neck_y = hip_y - 42
    _ruff(surf, cx, neck_y, 22, (250, 210, 70), lobes=11)
    hr = 19
    hy = neck_y - hr - 4
    _round_head(surf, cx, hy, hr, (255, 226, 200))
    # Rainbow wig — fluffy tufts of red/orange/yellow flanking a bald pate.
    wig = [(220, 60, 60), (245, 150, 60), (250, 215, 70),
           (90, 180, 100), (70, 130, 220)]
    for s in (-1, 1):
        for j, wc in enumerate(wig):
            wx = cx + s * (hr + 1 + j * 3)
            wy = hy - 2 + (j - 2) * 4
            pygame.draw.circle(surf, _shade(wc, -40), (wx, wy), 6)
            pygame.draw.circle(surf, wc, (wx, wy), 5)
    _eyes(surf, cx, hy - 2, hr, happy=True)
    # Arched red brows.
    for s in (-1, 1):
        pygame.draw.arc(surf, (210, 60, 70),
                        (cx + s * 9 - 5, hy - 9, 10, 7), 0, math.pi, 2)
    _nose(surf, cx, hy + 4, 8, (235, 45, 45))
    pygame.draw.ellipse(surf, WHITE, (cx - 12, hy + 9, 24, 12))
    _smile(surf, cx, hy + 10, 20, (215, 55, 65))


def clown_windup(surf, cx, feet_y):
    """Quirky wind-up tin clown: riveted metal panels, wind key on the back,
    painted smile, antenna-ball hat — charming retro toy, not scary."""
    hip_y = feet_y - 68
    TIN = (150, 175, 195)
    TIN_D = (95, 120, 145)
    RED, GOLD = (210, 70, 70), (235, 200, 90)
    _boots(surf, cx, feet_y, 13, 22, TIN_D, toe=(190, 205, 220))
    # Riveted metal legs.
    for s in (-1, 1):
        pygame.draw.line(surf, TIN_D, (cx + s * 8, hip_y + 2),
                         (cx + s * 10, feet_y - 7), 8)
        pygame.draw.line(surf, TIN, (cx + s * 8, hip_y + 2),
                         (cx + s * 10, feet_y - 7), 5)
    # Boxy riveted torso panel.
    body = pygame.Rect(cx - 20, hip_y - 44, 40, 52)
    pygame.draw.rect(surf, TIN, body, border_radius=6)
    pygame.draw.rect(surf, TIN_D, body, 2, border_radius=6)
    # Vertical tin sheen.
    pygame.draw.rect(surf, _shade(TIN, 40),
                     (body.x + 4, body.y + 4, 8, body.h - 8), border_radius=4)
    # Rivets around the panel edge.
    for fx, fy in ((0.12, 0.1), (0.88, 0.1), (0.12, 0.9), (0.88, 0.9),
                   (0.5, 0.1), (0.5, 0.9)):
        rx = body.x + int(fx * body.w)
        ry = body.y + int(fy * body.h)
        pygame.draw.circle(surf, TIN_D, (rx, ry), 2)
        pygame.draw.circle(surf, _shade(TIN, 60), (rx - 1, ry - 1), 1)
    # Painted red chest gear-button + dial.
    pygame.draw.circle(surf, RED, (cx, hip_y - 18), 7)
    pygame.draw.circle(surf, _shade(RED, -60), (cx, hip_y - 18), 7, 2)
    pygame.draw.circle(surf, GOLD, (cx, hip_y - 18), 2)
    # Wind-up key peeking from the side.
    pygame.draw.line(surf, GOLD, (cx + 20, hip_y - 26), (cx + 30, hip_y - 26), 3)
    pygame.draw.circle(surf, GOLD, (cx + 32, hip_y - 26), 5, 2)
    pygame.draw.circle(surf, GOLD, (cx + 28, hip_y - 26), 5, 2)
    neck_y = hip_y - 44
    # Bolt neck.
    pygame.draw.rect(surf, TIN_D, (cx - 5, neck_y - 2, 10, 6))
    hr = 18
    hy = neck_y - hr
    # Round tin head.
    _outline_ellipse(surf, _shade(TIN, 15), (cx - hr, hy - hr, hr * 2, hr * 2),
                     oc=TIN_D, w=2)
    pygame.draw.ellipse(surf, _shade(TIN, 55), (cx - hr + 3, hy - hr + 3, 9, 9))
    # Painted round eyes + rosy cheek circles.
    for s in (-1, 1):
        pygame.draw.circle(surf, (40, 45, 60), (cx + s * 7, hy - 2), 3)
        pygame.draw.circle(surf, WHITE, (cx + s * 7 - 1, hy - 3), 1)
        pygame.draw.circle(surf, (240, 130, 130), (cx + s * 11, hy + 4), 3)
    _nose(surf, cx, hy + 3, 5, RED)
    # Painted curved smile.
    pygame.draw.arc(surf, (60, 65, 80), (cx - 8, hy + 5, 16, 9),
                    math.pi * 1.05, math.tau * 0.97, 2)
    # Antenna with a red ball — the toy signature.
    pygame.draw.line(surf, TIN_D, (cx, hy - hr), (cx, hy - hr - 9), 2)
    pygame.draw.circle(surf, RED, (cx, hy - hr - 11), 4)
    pygame.draw.circle(surf, _shade(RED, 90), (cx - 1, hy - hr - 12), 1)


CLOWNS = [
    ("Whiteface", clown_whiteface),
    ("Auguste", clown_auguste),
    ("Tramp / Hobo", clown_tramp),
    ("Pierrot", clown_pierrot),
    ("Harlequin", clown_harlequin),
    ("Court Jester", clown_jester),
    ("Ringmaster", clown_ringmaster),
    ("Cute Mascot", clown_mascot),
    ("Rainbow Party", clown_rainbow),
    ("Wind-up Tin", clown_windup),
]


# ── per-cell gameplay scene ──────────────────────────────────────────────────

def render_cell(draw_clown, idx):
    """One full-canvas gameplay scene (W x H) at SS supersample: day sky +
    clearing ground (no pagodas), the drop-shadowed clown standing on the
    ground, the floating power-up die above it, and the real parrot flying in
    from the left for scale. Returned at native W x H (already downscaled)."""
    palette = shaped_palette(DAY_PHASE)
    big = pygame.Surface((W * SS, H * SS))
    # draw_sky_ground hard-codes the horizon at the native GROUND_Y, so on the
    # supersampled canvas we paint the same sky/ground keys with the seam scaled
    # to GROUND_Y * SS — same palette, just stretched cleanly to the SS surface.
    g_y = GROUND_Y * SS
    for y in range(g_y):
        t = y / g_y
        if t < 0.5:
            c = lerp_color(palette['sky_top'], palette['sky_mid'], t * 2)
        else:
            c = lerp_color(palette['sky_mid'], palette['sky_bot'], (t - 0.5) * 2)
        pygame.draw.line(big, c, (0, y), (W * SS, y))
    for y in range(g_y, H * SS):
        t = (y - g_y) / max(1, H * SS - g_y)
        c = lerp_color(palette['ground_top'], palette['ground_mid'], t)
        pygame.draw.line(big, c, (0, y), (W * SS, y))
    pygame.draw.line(big, palette['ground_top'], (0, g_y), (W * SS, g_y))

    # A few distant soft hills + scattered grass tufts so the clearing reads as
    # an open space (no pagodas), not an empty void.
    hill = pygame.Surface((W * SS, 60 * SS), pygame.SRCALPHA)
    hc = _shade(palette['ground_mid'], 25)
    for hx, hw, hh in ((60, 140, 34), (200, 170, 44), (320, 130, 28)):
        pygame.draw.ellipse(hill, (*hc, 150),
                            ((hx - hw) * SS, 0, hw * 2 * SS, hh * 2 * SS))
    big.blit(hill, (0, g_y - 26 * SS))
    tuft = _shade(palette['ground_top'], 20)
    rng = __import__('random').Random(idx * 131 + 7)
    for _ in range(14):
        tx = rng.randint(8, W - 8) * SS
        ty = g_y + rng.randint(6, 36) * SS
        for k in (-3, 0, 3):
            pygame.draw.line(big, tuft, (tx + k * SS, ty),
                             (tx + k * SS, ty - rng.randint(5, 9) * SS),
                             max(1, SS))

    # Work on a 1x logical layer for the figure + die + parrot, then blit it
    # scaled — keeps the clown-kit coordinates simple and AA-clean.
    layer = pygame.Surface((W, H), pygame.SRCALPHA)
    clown_cx = W // 2 + 12
    feet_y = GROUND_Y - 2
    _shadow(layer, clown_cx, feet_y, 78)
    draw_clown(layer, clown_cx, feet_y)

    # Floating power-up die above the clown's head/hands. One cell shows the
    # 2-digit roll number to hint the route-length mechanic; rest show pips.
    die_x = clown_cx
    die_base_y = feet_y - 200
    pulse = idx * 1.7 + 2.0
    if idx == 4:
        draw_floating_die(layer, die_x, die_base_y, pulse, number=27)
    else:
        draw_floating_die(layer, die_x, die_base_y, pulse,
                          pips=[5, 3, 6, 2, 5, 4, 6, 5, 3, 2][idx])

    # Real parrot flying in from the left at mid-height for scale/context.
    tilt = 10
    bird = get_parrot(1, tilt)
    bird = pygame.transform.smoothscale(
        bird, (int(bird.get_width() * 1.15), int(bird.get_height() * 1.15)))
    layer.blit(bird, (44 - bird.get_width() // 2,
                      (feet_y - 150) - bird.get_height() // 2))

    big.blit(pygame.transform.smoothscale(layer, (W * SS, H * SS)), (0, 0))
    return pygame.transform.smoothscale(big, (W, H))


def main():
    pygame.init()
    pygame.font.init()
    pygame.display.set_mode((W, H))

    cols, rows = 5, 2
    CW, CH = W, H
    SCALE = 0.52
    sw, sh = int(CW * SCALE), int(CH * SCALE)

    PAD = 26
    GAP = 14
    TITLE_H = 56
    CAP_H = 26

    canvas_w = PAD * 2 + cols * sw + (cols - 1) * GAP
    canvas_h = PAD * 2 + TITLE_H + rows * (sh + CAP_H) + (rows - 1) * GAP
    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((24, 22, 30))

    f_title = pygame.font.SysFont(None, 42, bold=True)
    f_sub = pygame.font.SysFont(None, 22, bold=True)
    f_cap = pygame.font.SysFont(None, 24, bold=True)

    title = f_title.render("DICE CLOWN — pre-warren designs", True,
                           (250, 240, 210))
    canvas.blit(title, (PAD, PAD - 2))
    sub = f_sub.render(
        "clearing before the Pagoda Warren · take the floating die to roll the "
        "route length · 10 archetypes",
        True, (190, 195, 205))
    canvas.blit(sub, (PAD, PAD + 30))

    y0 = PAD + TITLE_H
    for i, (name, fn) in enumerate(CLOWNS):
        r, c = divmod(i, cols)
        cx = PAD + c * (sw + GAP)
        cy = y0 + r * (sh + CAP_H + GAP)
        cell = render_cell(fn, i)
        scaled = pygame.transform.smoothscale(cell, (sw, sh))
        pygame.draw.rect(canvas, (70, 76, 96),
                         pygame.Rect(cx - 1, cy - 1, sw + 2, sh + 2), 1)
        canvas.blit(scaled, (cx, cy))
        cap = f_cap.render(f"{i + 1}. {name}", True, (235, 225, 165))
        canvas.blit(cap, (cx + (sw - cap.get_width()) // 2, cy + sh + 4))

    out_dir = os.path.join("docs", "clown_dice")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_1.png")
    pygame.image.save(canvas, out_path)
    print(f"saved {out_path}  ({canvas_w}x{canvas_h})")


if __name__ == "__main__":
    main()
