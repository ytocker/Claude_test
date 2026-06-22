"""Headless exploration sheet for the ARCADE Vending Machine curio + Junk
Drawer trinkets. Reuses the Store's Obsidian & Gold primitives so the
explorations read like the real screen. Preview-only; writes one combined PNG.
"""
import os
import math
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from game.store import (
    _vgrad_panel, _drop_shadow, _inset_disc, _gem, _gradient_text,
    _coin_glyph, _soft_glow, _gold_rule,
)
from game.hud import _font, _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP, _RED_OUTLINE
from game.draw import lerp_color, rounded_rect

WHITE = (255, 255, 255)
NEAR_BLACK = (8, 8, 14)
_OBS_TOP = (26, 24, 32)
_OBS_BOT = (9, 8, 15)
_BG_STOPS = ((8, 8, 24), (12, 12, 36), (18, 16, 48), (24, 20, 58))

# Cheerful capsule + trinket palette — the "junk" should feel toy-bright against
# the obsidian so the gachapon reads as a colourful prize machine, not furniture.
CAP_COLORS = [
    ((250, 120, 130), (190, 60, 80)),    # bubblegum
    ((120, 200, 240), (50, 120, 180)),   # sky
    ((255, 210, 110), (200, 140, 30)),   # gold-amber
    ((150, 220, 150), (70, 150, 90)),    # mint
    ((200, 150, 240), (130, 80, 180)),   # lilac
    ((255, 170, 100), (200, 100, 40)),   # tangerine
]


# ── capsule globe + capsules ─────────────────────────────────────────────────

def _capsule(surf, cx, cy, r, top_col, bot_col, t_angle=0.0):
    """A two-tone gachapon capsule: clear-ish top dome over a coloured base,
    a seam line, and a glossy specular pip. Rotated by t_angle for variety."""
    cap = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
    c = r + 2
    # Coloured lower hemisphere.
    pygame.draw.circle(cap, (*bot_col, 255), (c, c), r)
    # Lit upper hemisphere — the clear-plastic half catches more light.
    for yy in range(c - r, c):
        f = (yy - (c - r)) / max(1, r)
        col = lerp_color(lerp_color(top_col, WHITE, 0.5), top_col, f)
        half = int(math.sqrt(max(0, r * r - (yy - c) ** 2)))
        if half > 0:
            pygame.draw.line(cap, (*col, 235), (c - half, yy), (c + half, yy))
    # Seam across the equator.
    pygame.draw.line(cap, (*lerp_color(bot_col, NEAR_BLACK, 0.4), 200),
                     (c - r + 1, c), (c + r - 1, c), 1)
    pygame.draw.circle(cap, (*lerp_color(bot_col, NEAR_BLACK, 0.5), 230),
                       (c, c), r, 1)
    # Specular highlight.
    hl = pygame.Surface((r, r), pygame.SRCALPHA)
    pygame.draw.ellipse(hl, (255, 255, 255, 180),
                        (0, 0, max(2, r // 2), max(2, int(r * 0.7))))
    cap.blit(hl, (c - int(r * 0.55), c - int(r * 0.78)))
    if t_angle:
        cap = pygame.transform.rotate(cap, t_angle)
    surf.blit(cap, cap.get_rect(center=(cx, cy)))


def _globe(surf, cx, cy, r, n_caps=18, seed=0):
    """A glass dome packed with capsules: dark inner well, a settled pile of
    capsules, then a glass sheen + gold rim ring over the top."""
    rng_caps = []
    rnd = _seeded(seed)
    # Inner glass well (slightly cool, recessed).
    well = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
    for i in range(r, 0, -1):
        col = lerp_color((40, 44, 60), (12, 14, 24), (i / r) ** 1.2)
        pygame.draw.circle(well, (*col, 255), (r + 1, r + 1), i)
    surf.blit(well, (cx - r - 1, cy - r - 1))
    # Capsule pile — denser toward the bottom, like settled balls.
    prev_clip = surf.get_clip()
    clip = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
    for _ in range(n_caps):
        a = rnd() * math.tau
        rad = (rnd() ** 0.5) * (r - 8)
        px = cx + math.cos(a) * rad
        # Bias capsules downward so the pile settles.
        py = cy + math.sin(a) * rad * 0.55 + (r - rad) * 0.18
        cr = int(8 + rnd() * 3)
        col = CAP_COLORS[int(rnd() * len(CAP_COLORS)) % len(CAP_COLORS)]
        rng_caps.append((py, px, cr, col, (rnd() - 0.5) * 60))
    for py, px, cr, col, ang in sorted(rng_caps):
        _capsule(surf, int(px), int(py), cr, col[0], col[1], ang)
    surf.set_clip(prev_clip)
    # Glass sheen — a soft crescent of light across the dome.
    sheen = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
    pygame.draw.ellipse(sheen, (255, 255, 255, 60),
                        (int(r * 0.3), int(r * 0.18), int(r * 1.0), int(r * 0.7)))
    pygame.draw.ellipse(sheen, (255, 255, 255, 0),
                        (int(r * 0.45), int(r * 0.35), int(r * 0.8), int(r * 0.55)))
    mask = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (r + 1, r + 1), r)
    sheen.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(sheen, (cx - r - 1, cy - r - 1))
    # Gold rim ring.
    pygame.draw.circle(surf, (*_GOLD_DEEP, 220), (cx, cy), r, 3)
    pygame.draw.circle(surf, (*_GOLD_BRIGHT, 230), (cx, cy), r - 2, 1)


def _seeded(seed):
    """Tiny deterministic LCG so each preview globe is stable across renders."""
    state = [seed * 2654435761 % (2 ** 32) + 1]

    def nxt():
        state[0] = (1103515245 * state[0] + 12345) % (2 ** 31)
        return state[0] / (2 ** 31)
    return nxt


def _coin_slot(surf, cx, cy, w=14):
    """A recessed gold coin slot with a dark mouth."""
    plate = pygame.Rect(cx - w // 2 - 4, cy - 9, w + 8, 18)
    surf.blit(_vgrad_panel(plate.w, plate.h, 4,
                           lerp_color(_GOLD_BRIGHT, WHITE, 0.2), _GOLD_DEEP),
              plate.topleft)
    pygame.draw.rect(surf, (*_GOLD_DEEP, 230), plate, width=1, border_radius=4)
    pygame.draw.rect(surf, (4, 4, 8), (cx - w // 2, cy - 4, w, 8),
                     border_radius=3)
    pygame.draw.rect(surf, (*_GOLD_PALE, 120), (cx - w // 2, cy - 4, w, 2),
                     border_radius=2)


def _crank(surf, cx, cy, r=11):
    """The turn crank: a gold disc, a dark hub, a knob arm, and an arrow hint."""
    _soft_glow(surf, cx, cy, r + 6, (236, 190, 96), 40, layers=4)
    disc = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
    for i in range(r, 0, -1):
        col = lerp_color((255, 226, 150), (170, 118, 28), (i / r) ** 0.8)
        pygame.draw.circle(disc, (*col, 255), (r + 1, r + 1), i)
    surf.blit(disc, (cx - r - 1, cy - r - 1))
    pygame.draw.circle(surf, (*_GOLD_DEEP, 230), (cx, cy), r, 1)
    # Knob arm + handle.
    kx, ky = cx + int(r * 0.55), cy - int(r * 0.55)
    pygame.draw.line(surf, (40, 28, 8), (cx, cy), (kx, ky), 3)
    pygame.draw.circle(surf, (30, 22, 8), (cx, cy), 3)
    pygame.draw.circle(surf, (60, 44, 16), (kx, ky), 4)
    pygame.draw.circle(surf, (*_GOLD_PALE, 220), (kx - 1, ky - 1), 1)


def _price_tag(surf, cx, cy, scale=1.0):
    """A small "5 + coin" price tag pill."""
    h = int(22 * scale)
    f = _font(max(11, int(13 * scale)), True)
    timg = f.render("5", True, (28, 18, 8))
    coin_d = int(h * 0.7)
    w = 10 + coin_d + 3 + timg.get_width() + 10
    tag = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    surf.blit(_vgrad_panel(w, h, h // 2, (255, 215, 120), _GOLD_DEEP), tag.topleft)
    pygame.draw.rect(surf, (*_GOLD_BRIGHT, 220), tag, width=1, border_radius=h // 2)
    x = tag.x + 10
    _coin_glyph(surf, x + coin_d // 2, cy, coin_d // 2)
    x += coin_d + 3
    surf.blit(timg, timg.get_rect(midleft=(x, cy)))


def _chute(surf, rect, with_capsule=True, cap_col=None):
    """A dark dispense chute with a gold lip and (optionally) a capsule in it."""
    surf.blit(_vgrad_panel(rect.w, rect.h, 8, (16, 14, 22), (4, 4, 8)),
              rect.topleft)
    pygame.draw.rect(surf, (0, 0, 0, 200), rect, width=1, border_radius=8)
    # Gold lip across the top opening.
    lip = pygame.Rect(rect.x + 6, rect.y - 3, rect.w - 12, 6)
    surf.blit(_vgrad_panel(lip.w, lip.h, 3,
                           lerp_color(_GOLD_BRIGHT, WHITE, 0.2), _GOLD_DEEP),
              lip.topleft)
    if with_capsule:
        col = cap_col or CAP_COLORS[0]
        _soft_glow(surf, rect.centerx, rect.centery + 4, 16, col[0], 60, layers=4)
        _capsule(surf, rect.centerx, rect.centery + 4, 13, col[0], col[1], -12)


# ── trinkets (each ~24-32 px, drawn centred at cx,cy) ─────────────────────────

def _t_duck(surf, cx, cy):
    body = (255, 214, 64)
    shade = (214, 168, 30)
    pygame.draw.ellipse(surf, shade, (cx - 11, cy + 1, 22, 11))
    pygame.draw.ellipse(surf, body, (cx - 11, cy - 1, 22, 11))   # body
    pygame.draw.circle(surf, body, (cx + 7, cy - 6), 6)          # head
    pygame.draw.circle(surf, shade, (cx + 9, cy - 4), 6, 0)
    pygame.draw.circle(surf, body, (cx + 7, cy - 7), 6)
    pygame.draw.polygon(surf, (250, 140, 40),
                        [(cx + 12, cy - 6), (cx + 18, cy - 5), (cx + 12, cy - 3)])  # bill
    pygame.draw.circle(surf, (20, 20, 24), (cx + 8, cy - 8), 1)  # eye
    pygame.draw.arc(surf, shade, (cx - 6, cy - 4, 12, 10), 0.3, 2.6, 2)  # wing


def _t_fry(surf, cx, cy):
    fry = (244, 198, 96)
    edge = (196, 150, 60)
    r = pygame.Rect(cx - 4, cy - 12, 8, 24)
    rounded_rect(surf, r, 3, fry)
    pygame.draw.rect(surf, edge, r, width=1, border_radius=3)
    pygame.draw.line(surf, (255, 232, 170), (cx - 1, cy - 9), (cx - 1, cy + 8), 1)
    # A sad little face.
    pygame.draw.circle(surf, (40, 30, 16), (cx - 2, cy - 3), 1)
    pygame.draw.circle(surf, (40, 30, 16), (cx + 2, cy - 3), 1)
    pygame.draw.arc(surf, (40, 30, 16), (cx - 3, cy + 2, 6, 5), 3.5, 5.9, 1)  # frown


def _t_eye(surf, cx, cy):
    pygame.draw.circle(surf, (245, 245, 248), (cx, cy), 11)
    pygame.draw.circle(surf, (180, 180, 188), (cx, cy), 11, 1)
    # Googly pupil offset, with a glassy highlight.
    pygame.draw.circle(surf, (20, 20, 26), (cx + 3, cy + 3), 5)
    pygame.draw.circle(surf, (255, 255, 255), (cx + 1, cy + 1), 2)


def _t_clip(surf, cx, cy):
    col = (200, 206, 216)
    # A bent paperclip — two nested rounded rects of wire, with a kink.
    pygame.draw.rect(surf, col, (cx - 7, cy - 11, 14, 22), width=2, border_radius=6)
    pygame.draw.rect(surf, col, (cx - 3, cy - 7, 10, 14), width=2, border_radius=5)
    pygame.draw.line(surf, (150, 156, 168), (cx - 7, cy + 8), (cx - 13, cy + 13), 2)  # bend


def _t_ribbon(surf, cx, cy):
    blue = (90, 150, 220)
    dk = (50, 100, 170)
    pygame.draw.circle(surf, (240, 220, 110), (cx, cy - 4), 7)  # rosette
    for k in range(8):
        a = k * math.tau / 8
        x = cx + math.cos(a) * 8
        y = cy - 4 + math.sin(a) * 8
        pygame.draw.line(surf, dk, (cx, cy - 4), (x, y), 3)
    pygame.draw.circle(surf, blue, (cx, cy - 4), 5)
    pygame.draw.circle(surf, (220, 230, 245), (cx - 1, cy - 5), 1)
    pygame.draw.polygon(surf, blue, [(cx - 5, cy + 2), (cx - 8, cy + 13), (cx - 1, cy + 8)])  # tails
    pygame.draw.polygon(surf, dk, [(cx + 5, cy + 2), (cx + 8, cy + 13), (cx + 1, cy + 8)])


def _t_gerald(surf, cx, cy):
    """Gerald — a tiny sandstone-pillar figurine with a face."""
    sand = (216, 176, 116)
    dk = (170, 130, 78)
    r = pygame.Rect(cx - 8, cy - 13, 16, 26)
    rounded_rect(surf, r, 3, sand)
    pygame.draw.rect(surf, dk, r, width=1, border_radius=3)
    # Capital + base bands.
    pygame.draw.rect(surf, dk, (cx - 10, cy - 13, 20, 4), border_radius=2)
    pygame.draw.rect(surf, dk, (cx - 10, cy + 9, 20, 4), border_radius=2)
    # Brick lines + face.
    pygame.draw.line(surf, dk, (cx - 6, cy - 2), (cx + 6, cy - 2), 1)
    pygame.draw.circle(surf, (40, 30, 20), (cx - 3, cy + 2), 1)
    pygame.draw.circle(surf, (40, 30, 20), (cx + 3, cy + 2), 1)
    pygame.draw.arc(surf, (40, 30, 20), (cx - 3, cy + 3, 6, 4), 3.5, 5.9, 1)


def _t_moth(surf, cx, cy):
    wing = (180, 168, 150)
    dk = (130, 116, 96)
    body = (90, 78, 64)
    for sx in (-1, 1):
        pygame.draw.ellipse(surf, wing, (cx + sx * 2 - (sx > 0) * 12, cy - 8, 11, 10))
        pygame.draw.ellipse(surf, dk, (cx + sx * 2 - (sx > 0) * 12, cy - 8, 11, 10), 1)
        pygame.draw.ellipse(surf, wing, (cx + sx * 3 - (sx > 0) * 11, cy, 9, 8))
    pygame.draw.circle(surf, (60, 40, 30), (cx - 6, cy - 4), 2)  # eyespot
    pygame.draw.circle(surf, (60, 40, 30), (cx + 6, cy - 4), 2)
    pygame.draw.ellipse(surf, body, (cx - 2, cy - 9, 4, 18))  # furry body
    pygame.draw.line(surf, dk, (cx - 1, cy - 9), (cx - 4, cy - 13), 1)  # antennae
    pygame.draw.line(surf, dk, (cx + 1, cy - 9), (cx + 4, cy - 13), 1)


TRINKETS = [
    ("DUCK", _t_duck), ("FRY", _t_fry), ("EYE", _t_eye), ("CLIP", _t_clip),
    ("RIBBON", _t_ribbon), ("GERALD", _t_gerald), ("MOTH", _t_moth),
]


def _junk_shelf(surf, x, y, w, compact=False):
    """The JUNK DRAWER shelf: an obsidian ledge with gold label and the
    trinket row standing on a thin gold rail."""
    h = 64 if not compact else 58
    shelf = pygame.Rect(x, y, w, h)
    _drop_shadow(surf, shelf, 12, blur=5, alpha=120)
    surf.blit(_vgrad_panel(shelf.w, shelf.h, 12, _OBS_TOP, _OBS_BOT, 252),
              shelf.topleft)
    pygame.draw.rect(surf, (*_GOLD_DEEP, 200), shelf.inflate(-6, -6), width=1,
                     border_radius=9)
    pygame.draw.rect(surf, (*_GOLD_BRIGHT, 150), shelf, width=1, border_radius=12)
    # Header.
    hdr = _font(11, True).render("JUNK  DRAWER", True, _GOLD_PALE)
    surf.blit(hdr, (x + 12, y + 6))
    # Trinket rail.
    rail_y = y + h - 14
    _gold_rule(surf, x + 12, x + w - 12, rail_y + 8, peak=120)
    slot_w = (w - 24) / len(TRINKETS)
    for i, (label, fn) in enumerate(TRINKETS):
        tcx = int(x + 12 + slot_w * (i + 0.5))
        tcy = y + 30
        # Each trinket sits on a little dark inset socket so it reads as filed.
        _inset_disc(surf, tcx, tcy, 15, tint=(10, 10, 16))
        fn(surf, tcx, tcy)
        lab = _font(8, True).render(label, True, _GOLD_PALE)
        lab.set_alpha(200)
        surf.blit(lab, lab.get_rect(center=(tcx, rail_y + 4)))


# ── machine silhouettes (5 versions) ─────────────────────────────────────────

def _machine_label(surf, rect, lines):
    """A gold marquee/name plate banner across a machine body."""
    surf.blit(_vgrad_panel(rect.w, rect.h, rect.h // 2,
                           lerp_color(_GOLD_BRIGHT, WHITE, 0.18), _GOLD_DEEP),
              rect.topleft)
    pygame.draw.rect(surf, (*_GOLD_DEEP, 230), rect, width=1,
                     border_radius=rect.h // 2)
    f = _font(max(9, rect.h - 8), True)
    img = f.render(lines, True, (40, 26, 8))
    surf.blit(img, img.get_rect(center=rect.center))


def machine_freestanding(surf, x, y, w, h, seed):
    """V1 — Freestanding cabinet: tall obsidian body, globe up top inside a
    rounded crown, marquee, slot+crank panel, wide chute drawer at the foot."""
    body = pygame.Rect(x, y, w, h)
    _drop_shadow(surf, body, 18, blur=7, alpha=150)
    surf.blit(_vgrad_panel(body.w, body.h, 18, _OBS_TOP, _OBS_BOT, 252),
              body.topleft)
    pygame.draw.rect(surf, (*_GOLD_DEEP, 210), body.inflate(-8, -8), width=2,
                     border_radius=13)
    pygame.draw.rect(surf, (*_GOLD_BRIGHT, 160), body, width=1, border_radius=18)
    cx = body.centerx
    gr = w // 2 - 14
    gcy = y + gr + 16
    _globe(surf, cx, gcy, gr, n_caps=20, seed=seed)
    my = gcy + gr + 12
    _machine_label(surf, pygame.Rect(x + 14, my, w - 28, 20), "GACHA")
    # Control panel: slot left, crank right.
    py = my + 34
    _coin_slot(surf, cx - 18, py)
    _crank(surf, cx + 20, py)
    _price_tag(surf, cx, py + 26)
    # Chute drawer.
    chute = pygame.Rect(x + 18, body.bottom - 40, w - 36, 30)
    _chute(surf, chute, with_capsule=True, cap_col=CAP_COLORS[seed % len(CAP_COLORS)])


def machine_countertop(surf, x, y, w, h, seed):
    """V2 — Countertop globe: a fat sphere globe dominating, on a short gold-
    ringed pedestal base holding slot, crank, and a front capsule cup."""
    cx = x + w // 2
    gr = w // 2 - 10
    gcy = y + gr + 8
    _globe(surf, cx, gcy, gr, n_caps=22, seed=seed)
    _price_tag(surf, x + w - 22, y + 16)
    # Pedestal base.
    base = pygame.Rect(x + 6, gcy + gr - 6, w - 12, h - (gcy + gr - 6 - y))
    _drop_shadow(surf, base, 14, blur=6, alpha=140)
    surf.blit(_vgrad_panel(base.w, base.h, 14, _OBS_TOP, _OBS_BOT, 252),
              base.topleft)
    pygame.draw.rect(surf, (*_GOLD_DEEP, 210), base.inflate(-6, -6), width=2,
                     border_radius=10)
    pygame.draw.rect(surf, (*_GOLD_BRIGHT, 160), base, width=1, border_radius=14)
    # Gold collar where globe meets base.
    pygame.draw.circle(surf, (*_GOLD_BRIGHT, 200), (cx, gcy + gr - 4), gr - 6, 3)
    _coin_slot(surf, cx - 22, base.y + 22)
    _crank(surf, cx + 24, base.y + 22)
    # Front capsule cup.
    cup = pygame.Rect(cx - 22, base.bottom - 30, 44, 22)
    _chute(surf, cup, with_capsule=True, cap_col=CAP_COLORS[(seed + 2) % len(CAP_COLORS)])


def machine_twin(surf, x, y, w, h, seed):
    """V3 — Slim twin-tier tower: a domed (half-sphere) globe top under a gold
    arch, a glass capsule column showing a falling capsule mid-dispense, slot +
    crank, and a glowing chute catching the prize."""
    body = pygame.Rect(x, y, w, h)
    _drop_shadow(surf, body, 16, blur=7, alpha=150)
    surf.blit(_vgrad_panel(body.w, body.h, 16, _OBS_TOP, _OBS_BOT, 252),
              body.topleft)
    pygame.draw.rect(surf, (*_GOLD_DEEP, 210), body.inflate(-8, -8), width=2,
                     border_radius=11)
    pygame.draw.rect(surf, (*_GOLD_BRIGHT, 160), body, width=1, border_radius=16)
    cx = body.centerx
    gr = w // 2 - 12
    gcy = y + gr + 14
    _globe(surf, cx, gcy, gr, n_caps=16, seed=seed)
    # Dispense column — a vertical glass tube showing the action.
    col = pygame.Rect(cx - 12, gcy + gr - 2, 24, 54)
    surf.blit(_vgrad_panel(col.w, col.h, 10, (30, 34, 48), (12, 14, 24)),
              col.topleft)
    pygame.draw.rect(surf, (*_GOLD_DEEP, 180), col, width=1, border_radius=10)
    pygame.draw.rect(surf, (255, 255, 255, 50), (col.x + 3, col.y + 3, 5, col.h - 6),
                     border_radius=3)
    # The capsule frozen mid-fall, with a motion trail.
    fc = CAP_COLORS[(seed + 1) % len(CAP_COLORS)]
    for k, dy in enumerate((-16, -8, 0)):
        a = 70 + k * 60
        s = pygame.Surface((24, 24), pygame.SRCALPHA)
        _capsule(s, 12, 12, 9, fc[0], fc[1], 18)
        s.set_alpha(a)
        surf.blit(s, s.get_rect(center=(col.centerx, col.centery + dy)))
    # Slot + crank flank the column.
    _coin_slot(surf, x + 18, gcy + gr + 18)
    _crank(surf, body.right - 20, gcy + gr + 18)
    _price_tag(surf, x + 22, gcy + gr + 42, scale=0.9)
    # Glowing catch chute.
    chute = pygame.Rect(cx - 22, body.bottom - 36, 44, 26)
    _chute(surf, chute, with_capsule=False)


def machine_wide_window(surf, x, y, w, h, seed):
    """V4 — Wide arcade cabinet: a broad rounded body with a big rectangular
    capsule WINDOW (caps behind glass) instead of a sphere, a marquee header,
    a centred jumbo crank, and twin chutes."""
    body = pygame.Rect(x, y, w, h)
    _drop_shadow(surf, body, 18, blur=7, alpha=150)
    surf.blit(_vgrad_panel(body.w, body.h, 16, _OBS_TOP, _OBS_BOT, 252),
              body.topleft)
    pygame.draw.rect(surf, (*_GOLD_DEEP, 210), body.inflate(-8, -8), width=2,
                     border_radius=11)
    pygame.draw.rect(surf, (*_GOLD_BRIGHT, 160), body, width=1, border_radius=16)
    cx = body.centerx
    # Marquee.
    _machine_label(surf, pygame.Rect(x + 16, y + 10, w - 32, 18), "PRIZES")
    # Capsule window.
    win = pygame.Rect(x + 16, y + 34, w - 32, 70)
    surf.blit(_vgrad_panel(win.w, win.h, 10, (34, 38, 54), (14, 16, 26)),
              win.topleft)
    rnd = _seeded(seed)
    for _ in range(20):
        px = win.x + 10 + rnd() * (win.w - 20)
        py = win.y + 10 + rnd() * (win.h - 20)
        col = CAP_COLORS[int(rnd() * len(CAP_COLORS)) % len(CAP_COLORS)]
        _capsule(surf, int(px), int(py), 9, col[0], col[1], (rnd() - 0.5) * 70)
    # Glass reflection streak + gold frame.
    refl = pygame.Surface((win.w, win.h), pygame.SRCALPHA)
    pygame.draw.polygon(refl, (255, 255, 255, 40),
                        [(0, 0), (28, 0), (0, win.h)])
    surf.blit(refl, win.topleft)
    pygame.draw.rect(surf, (*_GOLD_BRIGHT, 200), win, width=2, border_radius=10)
    # Controls.
    py = win.bottom + 20
    _coin_slot(surf, cx - 30, py)
    _crank(surf, cx, py, r=13)
    _price_tag(surf, cx + 34, py, scale=0.85)
    # Twin chutes.
    cw = (w - 48) // 2
    ch1 = pygame.Rect(x + 16, body.bottom - 36, cw, 26)
    ch2 = pygame.Rect(body.right - 16 - cw, body.bottom - 36, cw, 26)
    _chute(surf, ch1, with_capsule=True, cap_col=CAP_COLORS[seed % len(CAP_COLORS)])
    _chute(surf, ch2, with_capsule=False)


def machine_jewel(surf, x, y, w, h, seed):
    """V5 — Jewel-crown boutique: a premium globe crowned with a faceted rarity
    gem finial, a slim ornate body, an engraved nameplate, a side-mounted crank
    on a gold rosette, and a single hero chute with a glowing capsule."""
    body = pygame.Rect(x + 8, y + 16, w - 16, h - 16)
    _drop_shadow(surf, body, 16, blur=7, alpha=150)
    surf.blit(_vgrad_panel(body.w, body.h, 18, _OBS_TOP, _OBS_BOT, 252),
              body.topleft)
    pygame.draw.rect(surf, (*_GOLD_DEEP, 210), body.inflate(-8, -8), width=2,
                     border_radius=13)
    pygame.draw.rect(surf, (*_GOLD_BRIGHT, 170), body, width=1, border_radius=18)
    cx = body.centerx
    gr = w // 2 - 18
    gcy = y + gr + 26
    _globe(surf, cx, gcy, gr, n_caps=18, seed=seed)
    # Gem finial crown on top.
    _gem(surf, cx, y + 12, 9, "legendary", 0.0)
    # Engraved nameplate.
    plate = pygame.Rect(cx - 40, gcy + gr + 6, 80, 18)
    surf.blit(_vgrad_panel(plate.w, plate.h, 5, (40, 32, 18), (20, 14, 8)),
              plate.topleft)
    pygame.draw.rect(surf, (*_GOLD_BRIGHT, 200), plate, width=1, border_radius=5)
    _gradient_text(surf, "CURIOS", _font(11, True), plate.center,
                   (255, 240, 180), (236, 170, 60), shadow=True)
    # Side crank on a rosette + slot.
    _coin_slot(surf, cx, gcy + gr + 36)
    _crank(surf, body.right - 16, gcy + gr + 28, r=12)
    _price_tag(surf, x + 26, gcy + gr + 36, scale=0.85)
    # Hero chute with a glowing capsule.
    chute = pygame.Rect(cx - 24, body.bottom - 40, 48, 30)
    _chute(surf, chute, with_capsule=True,
           cap_col=CAP_COLORS[(seed + 3) % len(CAP_COLORS)])


# ── compose the sheet ────────────────────────────────────────────────────────

def _bg(surf, rect):
    n = len(_BG_STOPS)
    for yy in range(rect.h):
        f = yy / max(1, rect.h - 1)
        seg = min(n - 2, int(f * (n - 1)))
        local = (f * (n - 1)) - seg
        pygame.draw.line(surf, lerp_color(_BG_STOPS[seg], _BG_STOPS[seg + 1], local),
                         (rect.x, rect.y + yy), (rect.right, rect.y + yy))


MACHINES = [
    ("V1  FREESTANDING CABINET", machine_freestanding, (160, 300)),
    ("V2  COUNTERTOP GLOBE", machine_countertop, (170, 280)),
    ("V3  TWIN-TIER + DISPENSE", machine_twin, (150, 300)),
    ("V4  WIDE WINDOW ARCADE", machine_wide_window, (190, 300)),
    ("V5  JEWEL-CROWN BOUTIQUE", machine_jewel, (160, 300)),
]


def main():
    cols, rows = 3, 2
    tile_w, tile_h = 300, 400
    pad = 14
    sheet_w = cols * tile_w + pad * (cols + 1)
    sheet_h = rows * tile_h + pad * (rows + 1) + 36
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((6, 6, 14))

    # Title.
    _gradient_text(sheet, "ARCADE  —  VENDING MACHINE  +  JUNK DRAWER",
                   _font(20, True), (sheet_w // 2, 22),
                   (255, 240, 180), (236, 170, 60), outline=_RED_OUTLINE)

    tiles = []
    for i in range(5):
        c = i % cols
        r = i // cols
        tx = pad + c * (tile_w + pad)
        ty = 36 + pad + r * (tile_h + pad)
        tiles.append((tx, ty))
    # 6th tile = trinket showcase.
    tiles.append((pad + 2 * (tile_w + pad), 36 + pad + 1 * (tile_h + pad)))

    for idx, (label, fn, (mw, mh)) in enumerate(MACHINES):
        tx, ty = tiles[idx]
        tile = pygame.Rect(tx, ty, tile_w, tile_h)
        _bg(sheet, tile)
        pygame.draw.rect(sheet, (*_GOLD_DEEP, 120), tile, width=1, border_radius=10)
        # Label.
        lab = _font(13, True).render(label, True, _GOLD_PALE)
        sheet.blit(lab, lab.get_rect(midtop=(tile.centerx, ty + 8)))
        # Machine, centred upper area.
        mx = tile.centerx - mw // 2
        my = ty + 34
        fn(sheet, mx, my, mw, mh, seed=idx + 1)
        # Junk shelf along the bottom of each tile (compact).
        _junk_shelf(sheet, tx + 10, ty + tile_h - 70, tile_w - 20, compact=True)

    # 6th tile — big trinket showcase.
    tx, ty = tiles[5]
    tile = pygame.Rect(tx, ty, tile_w, tile_h)
    _bg(sheet, tile)
    pygame.draw.rect(sheet, (*_GOLD_DEEP, 120), tile, width=1, border_radius=10)
    lab = _font(13, True).render("TRINKETS  —  JUNK DRAWER", True, _GOLD_PALE)
    sheet.blit(lab, lab.get_rect(midtop=(tile.centerx, ty + 8)))
    # Big zoomed trinkets in a 2-col list with names, then the shelf.
    zoom_y = ty + 44
    for i, (name, fn) in enumerate(TRINKETS):
        c = i % 2
        rr = i // 2
        zcx = tx + 60 + c * 150
        zcy = zoom_y + 32 + rr * 56
        _inset_disc(sheet, zcx, zcy, 22, tint=(12, 12, 18))
        # Draw at 1.5x by rendering to a scratch and scaling.
        scratch = pygame.Surface((48, 48), pygame.SRCALPHA)
        fn(scratch, 24, 24)
        scratch = pygame.transform.smoothscale(scratch, (62, 62))
        sheet.blit(scratch, scratch.get_rect(center=(zcx, zcy)))
        nm = _font(11, True).render(name.title(), True, _GOLD_PALE)
        sheet.blit(nm, nm.get_rect(midleft=(zcx + 30, zcy)))
    _junk_shelf(sheet, tx + 10, ty + tile_h - 70, tile_w - 20, compact=True)

    out_dir = "docs/profile/vending_machine"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_1.png")
    pygame.image.save(sheet, out_path)
    print("WROTE", os.path.abspath(out_path), sheet.get_size())


if __name__ == "__main__":
    main()
