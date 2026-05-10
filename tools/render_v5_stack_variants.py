"""V5 Crispy Skyscraper - 5 layer-composition variants (picker).

Round-1 V5 was bun_top / fillet / cheese / lettuce / fillet / bun_bot
with a toothpick skewer through the gap. This picker explores 5
distinct layer compositions while keeping the basic stacked-sandwich
silhouette + gap-piercing skewer.

5 variants:
  v5_stack1 Classic Combo  bun_top / fillet / cheese / lettuce / fillet
                           / bun_bot - the cleanest, simplest tower.
                           Red cellophane frill on the toothpick skewer.
  v5_stack2 Bacon Crunch   bun_top / fillet / bacon / cheese / onion-
                           ring / lettuce / fillet / bun_bot. Heavier,
                           crunchier. Gold frill on the skewer.
  v5_stack3 BBQ Pickle     bun_top / fillet / BBQ-sauce drip / pickle /
                           cheese / fillet / bun_bot. BBQ-brown frill.
  v5_stack4 Spicy Pepper   bun_top / fillet / jalapeno / pepper-jack
                           / crispy-onion-strings / fillet / bun_bot.
                           Hot-red frill.
  v5_stack5 Veggie Tower   bun_top / lettuce / tomato / cheese /
                           cucumber / fillet / bun_bot. Lightest stack;
                           lettuce-green frill.

Picker only - no game/ files modified.
"""
import contextlib
import math
import random

import pygame
import pygame.gfxdraw as gfx

from game import entities as gent
from game import pillar_variants as gpv


# ----- Cartoon palette ------------------------------------------------------

# Bun
BUN_HI    = (252, 226, 178)
BUN_MID   = (232, 192, 130)
BUN_LO    = (188, 142,  78)

# Fried fillet crust
CRUST_HI  = (250, 212, 118)
CRUST_MID = (224, 162,  62)
CRUST_LO  = (148,  84,  20)
CRUMB     = (255, 232, 168)

# Cheese
CHEESE_HI = (255, 220, 110)
CHEESE    = (252, 184,  60)
CHEESE_LO = (190, 132,  30)

# Pepper jack
PJ_HI  = (250, 158,  82)
PJ_MID = (218, 110,  44)
PJ_LO  = (162,  60,  18)

# Lettuce
LETTUCE_HI  = (140, 200,  78)
LETTUCE_MID = ( 86, 158,  64)
LETTUCE_LO  = ( 52, 106,  40)

# Bacon
BACON_HI  = (240, 156, 104)
BACON_MID = (192,  78,  56)
BACON_FAT = (252, 224, 196)

# Onion (ring + crispy strings)
ONION_HI    = (252, 222, 162)
ONION_MID   = (224, 168,  78)

# Pickle
PICKLE_HI   = (174, 220, 110)
PICKLE_MID  = (106, 162,  62)
PICKLE_LO   = ( 56, 102,  36)

# Tomato
TOMATO_HI = (242, 110,  86)
TOMATO_MID = (208,  62,  46)
TOMATO_LO  = (142,  28,  18)
TOMATO_SEED = (252, 232, 196)

# Cucumber
CUC_HI   = (220, 240, 188)
CUC_MID  = (160, 206, 132)
CUC_LO   = ( 88, 138,  78)
CUC_SEED = (244, 244, 220)

# Jalapeno
JAL_HI = (180, 230, 110)
JAL_MID = (118, 180,  72)
JAL_LO  = ( 60, 116,  44)

# BBQ
BBQ_HI = (164,  72,  32)
BBQ_MID = (118,  46,  20)
BBQ_LO  = ( 78,  28,  10)

# Skewer
WOOD_HI     = (230, 192, 132)
WOOD_LO     = (162, 116,  62)
KFC_RED     = (212,  34,  34)
KFC_GOLD    = (242, 196,  72)

OUTLINE = ( 38,  22,  10)
SHADOW  = ( 22,  14,   8)


# ----- Utility primitives ---------------------------------------------------

def _shade(c, d):
    return (max(0, min(255, c[0] + d)),
            max(0, min(255, c[1] + d)),
            max(0, min(255, c[2] + d)))


def _aa_filled_circle(surf, cx, cy, r, color):
    cx, cy, r = int(cx), int(cy), int(r)
    if r < 1:
        return
    gfx.filled_circle(surf, cx, cy, r, color)
    gfx.aacircle(surf, cx, cy, r, color)


def draw_sesame(surf, rect, n=8, seed=0):
    """Tear-drop sesame seeds on the top half of a bun."""
    rng = random.Random(seed * 17 + 91)
    for _ in range(n):
        x = rng.randint(rect.x + 4, rect.right - 4)
        y = rng.randint(rect.y + 3, rect.y + max(4, rect.height // 3))
        pygame.draw.ellipse(surf, OUTLINE,
                            pygame.Rect(x - 2, y - 1, 4, 3))
        pygame.draw.ellipse(surf, (250, 234, 196),
                            pygame.Rect(x - 1, y - 1, 3, 2))


# ----- Layer drawers --------------------------------------------------------

LAYER_BUN_TOP    = 'bun_top'
LAYER_BUN_BOT    = 'bun_bot'
LAYER_FILLET     = 'fillet'
LAYER_CHEESE     = 'cheese'
LAYER_PEPPERJACK = 'pepperjack'
LAYER_LETTUCE    = 'lettuce'
LAYER_BACON      = 'bacon'
LAYER_ONION_RING = 'onion_ring'
LAYER_CRISPY_ONION = 'crispy_onion'
LAYER_PICKLE     = 'pickle'
LAYER_BBQ        = 'bbq'
LAYER_TOMATO     = 'tomato'
LAYER_CUCUMBER   = 'cucumber'
LAYER_JALAPENO   = 'jalapeno'

LAYER_HEIGHTS = {
    LAYER_BUN_TOP:     30,
    LAYER_BUN_BOT:     20,
    LAYER_FILLET:      28,
    LAYER_CHEESE:      12,
    LAYER_PEPPERJACK:  12,
    LAYER_LETTUCE:     14,
    LAYER_BACON:       10,
    LAYER_ONION_RING:  16,
    LAYER_CRISPY_ONION: 10,
    LAYER_PICKLE:      12,
    LAYER_BBQ:          6,
    LAYER_TOMATO:      10,
    LAYER_CUCUMBER:    10,
    LAYER_JALAPENO:     8,
}


def _draw_layer(surf, rect, kind, *, seed=0, flat_top=False):
    x, y, w, h = rect
    if h < 4:
        return
    if kind == LAYER_BUN_TOP:
        r = pygame.Rect(x - 2, y, w + 4, h)
        if flat_top:
            rad_kwargs = dict(border_top_left_radius=0,
                              border_top_right_radius=0,
                              border_bottom_left_radius=int(h * 0.7),
                              border_bottom_right_radius=int(h * 0.7))
        else:
            rad_kwargs = dict(border_radius=int(h * 0.7))
        pygame.draw.rect(surf, OUTLINE, r.inflate(4, 4), **rad_kwargs)
        pygame.draw.rect(surf, BUN_LO, r.inflate(2, 2), **rad_kwargs)
        pygame.draw.rect(surf, BUN_MID, r, **rad_kwargs)
        hl = pygame.Rect(r.x + 4, r.y + 3, r.width - 8,
                         max(3, int(h * 0.40)))
        pygame.draw.rect(surf, BUN_HI, hl, border_radius=int(hl.height * 0.8))
        if not flat_top:
            draw_sesame(surf, r, n=8, seed=seed + y)

    elif kind == LAYER_BUN_BOT:
        r = pygame.Rect(x - 2, y, w + 4, h)
        pygame.draw.rect(surf, OUTLINE, r.inflate(4, 4),
                         border_radius=int(h * 0.6))
        pygame.draw.rect(surf, BUN_LO, r.inflate(2, 2),
                         border_radius=int(h * 0.6))
        pygame.draw.rect(surf, BUN_MID, r, border_radius=int(h * 0.6))

    elif kind == LAYER_FILLET:
        r = pygame.Rect(x - 6, y, w + 12, h)
        pts = []
        n = 12
        for i in range(n + 1):
            u = i / n
            wave = math.sin(u * math.pi * 3 + seed) * 2
            pts.append((r.x + u * r.width, r.y + wave))
        for i in range(n + 1):
            u = (n - i) / n
            wave = math.sin(u * math.pi * 3 + seed + 1) * 2
            pts.append((r.x + u * r.width, r.bottom - wave))
        pygame.draw.polygon(surf, OUTLINE, pts)
        pygame.draw.polygon(surf, CRUST_LO, [(p[0], p[1] + 1) for p in pts])
        pygame.draw.polygon(surf, CRUST_MID, [(p[0], p[1] + 2) for p in pts])
        rng = random.Random(seed + y * 7)
        for _ in range(int(r.width * h / 18)):
            bx = rng.randint(r.x + 4, r.right - 4)
            by = rng.randint(r.y + 2, r.bottom - 2)
            _aa_filled_circle(surf, bx, by, 1, CRUMB)
        hl = pygame.Rect(r.x + 6, r.y + 2, r.width - 12, max(2, h // 3))
        pygame.draw.rect(surf, CRUST_HI, hl, border_radius=h // 4)

    elif kind == LAYER_CHEESE:
        r = pygame.Rect(x - 6, y, w + 12, h)
        pygame.draw.rect(surf, OUTLINE, r.inflate(4, 4), border_radius=4)
        pygame.draw.rect(surf, CHEESE_LO, r.inflate(2, 2), border_radius=3)
        pygame.draw.rect(surf, CHEESE, r, border_radius=3)
        # Drippy cheese tongues at the edges
        for sx in (r.x + 8, r.right - 12):
            pts = [(sx, r.bottom),
                   (sx + 4, r.bottom + 6),
                   (sx + 8, r.bottom)]
            pygame.draw.polygon(surf, OUTLINE,
                                [(p[0], p[1] + 1) for p in pts])
            pygame.draw.polygon(surf, CHEESE, pts)

    elif kind == LAYER_PEPPERJACK:
        r = pygame.Rect(x - 6, y, w + 12, h)
        pygame.draw.rect(surf, OUTLINE, r.inflate(4, 4), border_radius=4)
        pygame.draw.rect(surf, PJ_LO, r.inflate(2, 2), border_radius=3)
        pygame.draw.rect(surf, PJ_MID, r, border_radius=3)
        # Pepper specks
        rng = random.Random(seed + y)
        for _ in range(8):
            sx = rng.randint(r.x + 3, r.right - 3)
            sy = rng.randint(r.y + 2, r.bottom - 2)
            _aa_filled_circle(surf, sx, sy, 1, JAL_MID)
        # Drippy tongues
        for sx in (r.x + 8, r.right - 12):
            pts = [(sx, r.bottom),
                   (sx + 4, r.bottom + 5),
                   (sx + 8, r.bottom)]
            pygame.draw.polygon(surf, OUTLINE,
                                [(p[0], p[1] + 1) for p in pts])
            pygame.draw.polygon(surf, PJ_HI, pts)

    elif kind == LAYER_LETTUCE:
        r = pygame.Rect(x - 8, y - 2, w + 16, h + 4)
        pygame.draw.rect(surf, OUTLINE, r.inflate(2, 2), border_radius=3)
        pygame.draw.rect(surf, LETTUCE_LO, r, border_radius=3)
        n_bumps = max(5, r.width // 7)
        for i in range(n_bumps):
            bx = int(r.x + (i + 0.5) * r.width / n_bumps)
            for by, rr in ((r.y, 4), (r.bottom, 3)):
                _aa_filled_circle(surf, bx, by, rr, OUTLINE)
                _aa_filled_circle(surf, bx, by, max(1, rr - 1), LETTUCE_MID)
                _aa_filled_circle(surf, bx - 1, by - 1, max(1, rr - 2),
                                  LETTUCE_HI)

    elif kind == LAYER_BACON:
        r = pygame.Rect(x - 4, y, w + 8, h)
        pygame.draw.rect(surf, OUTLINE, r.inflate(2, 2), border_radius=2)
        pygame.draw.rect(surf, BACON_MID, r, border_radius=2)
        m = pygame.Rect(r.x, r.centery - 1, r.width, 2)
        pygame.draw.rect(surf, BACON_FAT, m)
        pygame.draw.rect(surf, BACON_HI,
                         pygame.Rect(r.x + 2, r.y + 1, r.width - 4, 2))
        for sx in range(r.x + 4, r.right - 4, 8):
            _aa_filled_circle(surf, sx, r.bottom, 2, OUTLINE)
            _aa_filled_circle(surf, sx, r.bottom, 1, BACON_HI)

    elif kind == LAYER_ONION_RING:
        r = pygame.Rect(x - 6, y, w + 12, h)
        ring_r = max(4, h // 2)
        for sx in (r.x + ring_r + 2, r.right - ring_r - 2):
            pygame.draw.circle(surf, OUTLINE, (sx, r.centery + 1), ring_r + 1)
            pygame.draw.circle(surf, CRUST_LO, (sx, r.centery), ring_r)
            pygame.draw.circle(surf, CRUST_MID, (sx, r.centery), ring_r)
            inner = max(2, ring_r // 2)
            pygame.draw.circle(surf, OUTLINE, (sx, r.centery), inner + 1)
            pygame.draw.circle(surf, ONION_MID, (sx, r.centery), inner)
            pygame.draw.circle(surf, ONION_HI, (sx - 1, r.centery - 1),
                               max(1, inner - 1))

    elif kind == LAYER_CRISPY_ONION:
        r = pygame.Rect(x - 6, y, w + 12, h)
        # Tangle of golden curly strings - draw multiple curved arcs
        rng = random.Random(seed + y * 11)
        n_curls = max(6, r.width // 6)
        for _ in range(n_curls):
            cx = rng.randint(r.x + 2, r.right - 2)
            cy = rng.randint(r.y + 1, r.bottom - 1)
            length = rng.randint(4, 7)
            tilt = rng.uniform(0, math.pi)
            x2 = cx + int(math.cos(tilt) * length)
            y2 = cy + int(math.sin(tilt) * length)
            pygame.draw.line(surf, OUTLINE, (cx, cy), (x2, y2), 3)
            pygame.draw.line(surf, CRUST_MID, (cx, cy), (x2, y2), 2)
            pygame.draw.line(surf, CRUST_HI, (cx, cy), (x2, y2), 1)

    elif kind == LAYER_PICKLE:
        r = pygame.Rect(x - 6, y, w + 12, h)
        pickle_r = max(4, h // 2)
        for sx in (r.x + pickle_r + 2, r.centerx, r.right - pickle_r - 2):
            pygame.draw.circle(surf, OUTLINE, (sx, r.centery + 1), pickle_r + 1)
            pygame.draw.circle(surf, PICKLE_LO, (sx, r.centery), pickle_r)
            pygame.draw.circle(surf, PICKLE_MID, (sx - 1, r.centery - 1),
                               max(2, pickle_r - 2))
            rng = random.Random(sx * 7 + r.centery)
            for _ in range(3):
                xs = sx + rng.randint(-pickle_r // 2, pickle_r // 2)
                ys = r.centery + rng.randint(-pickle_r // 2, pickle_r // 2)
                _aa_filled_circle(surf, xs, ys, 1, PICKLE_HI)

    elif kind == LAYER_BBQ:
        r = pygame.Rect(x - 8, y, w + 16, h)
        pygame.draw.rect(surf, OUTLINE, r.inflate(2, 2), border_radius=3)
        pygame.draw.rect(surf, BBQ_LO, r, border_radius=3)
        pygame.draw.rect(surf, BBQ_MID,
                         pygame.Rect(r.x + 2, r.y + 1, r.width - 4,
                                     max(1, h - 2)),
                         border_radius=2)
        pygame.draw.rect(surf, BBQ_HI,
                         pygame.Rect(r.x + 4, r.y + 1, max(2, r.width // 4), 1))
        # Drippy tongues at edges
        for sx in (r.x + 8, r.right - 12):
            pts = [(sx, r.bottom), (sx + 4, r.bottom + 6), (sx + 8, r.bottom)]
            pygame.draw.polygon(surf, OUTLINE,
                                [(p[0], p[1] + 1) for p in pts])
            pygame.draw.polygon(surf, BBQ_MID, pts)

    elif kind == LAYER_TOMATO:
        r = pygame.Rect(x - 6, y, w + 12, h)
        pygame.draw.rect(surf, OUTLINE, r.inflate(4, 4), border_radius=4)
        pygame.draw.rect(surf, TOMATO_LO, r.inflate(2, 2), border_radius=3)
        pygame.draw.rect(surf, TOMATO_MID, r, border_radius=3)
        pygame.draw.rect(surf, TOMATO_HI,
                         pygame.Rect(r.x + 4, r.y + 1, r.width - 8,
                                     max(1, h // 3)),
                         border_radius=2)
        # Tomato seeds
        rng = random.Random(seed + y * 9)
        for _ in range(5):
            sx = rng.randint(r.x + 4, r.right - 4)
            sy = rng.randint(r.y + 2, r.bottom - 2)
            pygame.draw.ellipse(surf, OUTLINE,
                                pygame.Rect(sx - 2, sy - 1, 4, 3))
            pygame.draw.ellipse(surf, TOMATO_SEED,
                                pygame.Rect(sx - 1, sy - 1, 3, 2))

    elif kind == LAYER_CUCUMBER:
        r = pygame.Rect(x - 4, y, w + 8, h)
        pygame.draw.rect(surf, OUTLINE, r.inflate(2, 2), border_radius=4)
        pygame.draw.rect(surf, CUC_LO, r.inflate(0, 0), border_radius=3)
        pygame.draw.rect(surf, CUC_MID,
                         pygame.Rect(r.x + 2, r.y + 1, r.width - 4,
                                     max(1, h - 2)),
                         border_radius=3)
        pygame.draw.rect(surf, CUC_HI,
                         pygame.Rect(r.x + 4, r.y + 1, r.width - 8,
                                     max(1, h // 3)),
                         border_radius=2)
        rng = random.Random(seed + y * 13)
        for _ in range(4):
            sx = rng.randint(r.x + 4, r.right - 4)
            sy = rng.randint(r.y + 2, r.bottom - 2)
            _aa_filled_circle(surf, sx, sy, 1, CUC_SEED)

    elif kind == LAYER_JALAPENO:
        r = pygame.Rect(x - 6, y, w + 12, h)
        # Several small jalapeno slices
        slice_r = max(3, h // 2)
        n_slices = max(4, r.width // 10)
        for i in range(n_slices):
            sx = int(r.x + 3 + (i + 0.5) * (r.width - 6) / n_slices)
            sy = r.centery
            pygame.draw.circle(surf, OUTLINE, (sx, sy + 1), slice_r + 1)
            pygame.draw.circle(surf, JAL_LO, (sx, sy), slice_r)
            pygame.draw.circle(surf, JAL_MID, (sx - 1, sy - 1),
                               max(2, slice_r - 1))
            _aa_filled_circle(surf, sx - 1, sy - 1, 1, JAL_HI)


# ----- Toothpick skewer -----------------------------------------------------

def _draw_skewer(surf, rect, *, frill_color=KFC_RED):
    """Toothpick skewer running through the centre of the BOTTOM pillar
    (we draw it from above the rect into the gap, and below). The
    cellophane frill at the top is the only colored accent that varies
    between variants."""
    pick_x = rect.centerx
    pick_top = rect.top - 18
    pick_bot = rect.top + min(rect.height - 4, 90)
    pygame.draw.line(surf, OUTLINE, (pick_x, pick_top), (pick_x, pick_bot), 4)
    pygame.draw.line(surf, WOOD_HI, (pick_x, pick_top + 1),
                     (pick_x, pick_bot - 1), 2)
    frill = [(pick_x - 7, pick_top - 2),
             (pick_x + 7, pick_top - 6),
             (pick_x, pick_top + 2)]
    pygame.draw.polygon(surf, OUTLINE, [(p[0], p[1] + 1) for p in frill])
    pygame.draw.polygon(surf, frill_color, frill)


# ----- Stack rendering ------------------------------------------------------

def _stack_layers(surf, rect, sequence, *, gap_side='bottom', seed=0,
                  flat_top_first=False):
    x, y, w, h = rect
    if gap_side == 'top':
        seq = list(reversed(sequence))
    else:
        seq = list(sequence)
    cy = y
    i = 0
    while cy < y + h:
        kind = seq[i % len(seq)]
        lh = LAYER_HEIGHTS[kind]
        r = pygame.Rect(x, cy, w, min(lh, y + h - cy))
        # Only the very FIRST layer drawn on top pillar gets flat_top to
        # connect to the ceiling.
        is_first = (i == 0 and gap_side == 'bottom')
        _draw_layer(surf, r, kind, seed=seed,
                    flat_top=(is_first and flat_top_first))
        cy += lh
        i += 1


def _make_v5_drawer(sequence, frill_color):
    def _draw(surf, top_rect, bot_rect, palette, seed):
        _stack_layers(surf, top_rect, sequence, gap_side='bottom', seed=seed,
                      flat_top_first=True)
        _stack_layers(surf, bot_rect, sequence, gap_side='top', seed=seed)
        _draw_skewer(surf, bot_rect, frill_color=frill_color)
    return _draw


# ----- Variant sequences ----------------------------------------------------

SEQ_CLASSIC = (LAYER_BUN_TOP, LAYER_FILLET, LAYER_CHEESE,
               LAYER_LETTUCE, LAYER_FILLET, LAYER_BUN_BOT)

SEQ_BACON = (LAYER_BUN_TOP, LAYER_FILLET, LAYER_BACON, LAYER_CHEESE,
             LAYER_ONION_RING, LAYER_LETTUCE, LAYER_FILLET, LAYER_BUN_BOT)

SEQ_BBQ_PICKLE = (LAYER_BUN_TOP, LAYER_FILLET, LAYER_BBQ, LAYER_PICKLE,
                  LAYER_CHEESE, LAYER_FILLET, LAYER_BUN_BOT)

SEQ_SPICY = (LAYER_BUN_TOP, LAYER_FILLET, LAYER_JALAPENO,
             LAYER_PEPPERJACK, LAYER_CRISPY_ONION,
             LAYER_FILLET, LAYER_BUN_BOT)

SEQ_VEGGIE = (LAYER_BUN_TOP, LAYER_LETTUCE, LAYER_TOMATO, LAYER_CHEESE,
              LAYER_CUCUMBER, LAYER_FILLET, LAYER_BUN_BOT)


draw_v5_stack1 = _make_v5_drawer(SEQ_CLASSIC,    KFC_RED)
draw_v5_stack2 = _make_v5_drawer(SEQ_BACON,      KFC_GOLD)
draw_v5_stack3 = _make_v5_drawer(SEQ_BBQ_PICKLE, BBQ_HI)
draw_v5_stack4 = _make_v5_drawer(SEQ_SPICY,      (240, 82, 50))
draw_v5_stack5 = _make_v5_drawer(SEQ_VEGGIE,     LETTUCE_HI)


V5_STACK_VARIANTS = {
    'v5_stack1': ("V5-stack1 Classic Combo", draw_v5_stack1),
    'v5_stack2': ("V5-stack2 Bacon Crunch",  draw_v5_stack2),
    'v5_stack3': ("V5-stack3 BBQ Pickle",    draw_v5_stack3),
    'v5_stack4': ("V5-stack4 Spicy Pepper",  draw_v5_stack4),
    'v5_stack5': ("V5-stack5 Veggie Tower",  draw_v5_stack5),
}


@contextlib.contextmanager
def install_variant(key: str):
    """Monkey-patch draw_pillar_pair so every pillar uses the chosen V5
    skyscraper variant. Patches BOTH game.pillar_variants AND
    game.entities (the import binding in entities.py is what Pipe.draw
    actually calls)."""
    if key not in V5_STACK_VARIANTS:
        raise ValueError(f"unknown V5 stack variant {key!r}; valid: "
                         f"{sorted(V5_STACK_VARIANTS)}")
    _, fn = V5_STACK_VARIANTS[key]
    saved = []

    def _patch(module, attr, replacement):
        saved.append((module, attr, getattr(module, attr)))
        setattr(module, attr, replacement)

    _patch(gpv,  'draw_pillar_pair', fn)
    _patch(gent, 'draw_pillar_pair', fn)
    try:
        yield
    finally:
        for module, attr, orig in reversed(saved):
            setattr(module, attr, orig)
