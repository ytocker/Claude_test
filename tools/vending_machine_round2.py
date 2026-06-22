"""Round-2 review render for the ARCADE Vending Machine (gachapon) curio.

This round answers the art-director's single dominant note: the globe payload
must read as cheap two-tone GACHAPON CAPSULES (glossy dome over a solid base,
one highlight), NOT faceted rarity gems — the gem language is reserved for real
cosmetics, and the whole gag is "cheap machine, worthless junk".

Carry-forward (locked): the LEAD is V1's freestanding cabinet (tall body,
crowned globe, marquee, chute drawer, dispensed capsule at the foot) grafted
with V5's cleaner crown framing + "CURIOS" nameplate tone. V5's legendary-gem
finial is replaced with a small gold capsule so nothing borrows rarity language.

Rendered ALONE at a true 360 px arcade-card width so it is judged at ship scale.
Preview-only; writes one combined PNG and the generator. Does not touch git.
"""
import os
import math
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from game.store import (
    _vgrad_panel, _drop_shadow, _inset_disc, _gradient_text,
    _coin_glyph, _soft_glow, _gold_rule,
)
from game.hud import _font, _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP, _RED_OUTLINE
from game.draw import lerp_color, rounded_rect

WHITE = (255, 255, 255)
NEAR_BLACK = (8, 8, 14)
_OBS_TOP = (26, 24, 32)
_OBS_BOT = (9, 8, 15)
_BG_STOPS = ((8, 8, 24), (12, 12, 36), (18, 16, 48), (24, 20, 58))

# Toy-bright capsule palette — the junk should feel like cheap plastic prize
# balls against the obsidian, so the gachapon reads colourful, never premium.
CAP_COLORS = [
    ((250, 120, 130), (190, 60, 80)),    # bubblegum
    ((120, 200, 240), (50, 120, 180)),   # sky
    ((255, 210, 110), (200, 140, 30)),   # gold-amber
    ((150, 220, 150), (70, 150, 90)),    # mint
    ((200, 150, 240), (130, 80, 180)),   # lilac
    ((255, 170, 100), (200, 100, 40)),   # tangerine
]


def _seeded(seed):
    """Tiny deterministic LCG so each preview globe is stable across renders."""
    state = [seed * 2654435761 % (2 ** 32) + 1]

    def nxt():
        state[0] = (1103515245 * state[0] + 12345) % (2 ** 31)
        return state[0] / (2 ** 31)
    return nxt


# ── capsule (the gag payload) ────────────────────────────────────────────────

def _capsule(surf, cx, cy, r, top_col, bot_col, t_angle=0.0):
    """A cheap two-tone gachapon capsule: a GLOSSY clear-tinted dome over a flat
    SOLID coloured base, split by a crisp equator seam, with ONE soft specular.

    The split is deliberately hard-edged (full top half lit, full bottom half a
    plain solid) so it reads as moulded plastic — the opposite of a faceted gem,
    which is the whole point of this note."""
    pad = 3
    cap = pygame.Surface((r * 2 + pad * 2, r * 2 + pad * 2), pygame.SRCALPHA)
    c = r + pad

    # Bottom half — one flat solid colour, the "base" of the capsule.
    base_rect = pygame.Rect(c - r, c, 2 * r, r)
    pygame.draw.rect(cap, (*bot_col, 255), base_rect)
    # Round the bottom corners so the base is a true hemisphere, not a box.
    pygame.draw.circle(cap, (*bot_col, 255), (c, c), r)
    floor = pygame.Surface((r * 2 + pad * 2, r * 2 + pad * 2), pygame.SRCALPHA)
    pygame.draw.rect(floor, (255, 255, 255, 255), (0, 0, r * 2 + pad * 2, c))
    cap.blit(floor, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    # Subtle base shading so the solid half has a touch of volume (still flat-ish).
    pygame.draw.circle(cap, (*lerp_color(bot_col, NEAR_BLACK, 0.35), 110),
                       (c, c + int(r * 0.45)), int(r * 0.7))

    # Top half — the glossy clear-plastic dome: a lighter tint of the same hue,
    # brightening toward the crown so it catches light as one smooth dome.
    dome_top = lerp_color(top_col, WHITE, 0.55)
    for yy in range(c - r, c):
        f = (yy - (c - r)) / max(1, r)            # 0 at crown → 1 at seam
        col = lerp_color(dome_top, top_col, f)
        half = int(math.sqrt(max(0, r * r - (yy - c) ** 2)))
        if half > 0:
            pygame.draw.line(cap, (*col, 255), (c - half, yy), (c + half, yy))

    # Crisp equator seam — the moulding line that sells "two-piece capsule".
    seam = lerp_color(bot_col, NEAR_BLACK, 0.45)
    pygame.draw.line(cap, (*seam, 230), (c - r + 1, c), (c + r - 1, c), 2)
    # Thin outer keyline to seat it cleanly on any background.
    pygame.draw.circle(cap, (*lerp_color(bot_col, NEAR_BLACK, 0.55), 230),
                       (c, c), r, 1)

    # ONE soft specular pip on the dome — a single glossy highlight, no facets.
    hl = pygame.Surface((cap.get_width(), cap.get_height()), pygame.SRCALPHA)
    pygame.draw.ellipse(hl, (255, 255, 255, 200),
                        (c - int(r * 0.62), c - int(r * 0.74),
                         max(2, int(r * 0.45)), max(2, int(r * 0.62))))
    cap.blit(hl, (0, 0))

    if t_angle:
        cap = pygame.transform.rotate(cap, t_angle)
    surf.blit(cap, cap.get_rect(center=(cx, cy)))


def _globe(surf, cx, cy, r, n_caps=14, seed=0):
    """A glass dome packed with capsules: a dark cool inner well, a settled pile
    of fewer / chunkier capsules (so each reads), then glass sheen + gold rim."""
    rnd = _seeded(seed)
    # Inner glass well (cool, recessed) — gives the capsules something to sit in.
    well = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
    for i in range(r, 0, -1):
        col = lerp_color((44, 48, 66), (12, 14, 24), (i / r) ** 1.2)
        pygame.draw.circle(well, (*col, 255), (r + 1, r + 1), i)
    surf.blit(well, (cx - r - 1, cy - r - 1))

    # Capsule pile — larger capsules, biased downward so it looks settled.
    caps = []
    for _ in range(n_caps):
        a = rnd() * math.tau
        rad = (rnd() ** 0.5) * (r - 12)
        px = cx + math.cos(a) * rad
        py = cy + math.sin(a) * rad * 0.55 + (r - rad) * 0.16
        cr = int(11 + rnd() * 4)
        col = CAP_COLORS[int(rnd() * len(CAP_COLORS)) % len(CAP_COLORS)]
        caps.append((py, px, cr, col, (rnd() - 0.5) * 50))
    for py, px, cr, col, ang in sorted(caps):
        _capsule(surf, int(px), int(py), cr, col[0], col[1], ang)

    # Glass sheen — one soft crescent of light across the upper dome.
    sheen = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
    pygame.draw.ellipse(sheen, (255, 255, 255, 55),
                        (int(r * 0.3), int(r * 0.16), int(r * 1.0), int(r * 0.66)))
    pygame.draw.ellipse(sheen, (255, 255, 255, 0),
                        (int(r * 0.45), int(r * 0.34), int(r * 0.8), int(r * 0.5)))
    mask = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (r + 1, r + 1), r)
    sheen.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(sheen, (cx - r - 1, cy - r - 1))

    # Gold rim ring (V5's cleaner framing).
    pygame.draw.circle(surf, (*_GOLD_DEEP, 230), (cx, cy), r, 3)
    pygame.draw.circle(surf, (*_GOLD_BRIGHT, 235), (cx, cy), r - 2, 1)


def _gold_capsule_finial(surf, cx, cy, r=10):
    """Replaces V5's legendary-gem finial: a tiny GOLD capsule on a stub, so the
    crown stays celebratory without borrowing the reserved rarity-gem language."""
    _soft_glow(surf, cx, cy, r + 7, (236, 196, 104), 46, layers=4)
    # Stub neck into the crown.
    pygame.draw.rect(surf, (*_GOLD_DEEP, 230), (cx - 2, cy, 4, r), border_radius=2)
    _capsule(surf, cx, cy, r, (255, 226, 150), (188, 132, 36), 0.0)
    pygame.draw.circle(surf, (*_GOLD_BRIGHT, 230), (cx, cy), r, 1)


# ── controls ─────────────────────────────────────────────────────────────────

def _coin_slot(surf, cx, cy, w=18):
    """A recessed gold coin slot with a dark mouth."""
    plate = pygame.Rect(cx - w // 2 - 5, cy - 11, w + 10, 22)
    surf.blit(_vgrad_panel(plate.w, plate.h, 5,
                           lerp_color(_GOLD_BRIGHT, WHITE, 0.2), _GOLD_DEEP),
              plate.topleft)
    pygame.draw.rect(surf, (*_GOLD_DEEP, 230), plate, width=1, border_radius=5)
    pygame.draw.rect(surf, (4, 4, 8), (cx - w // 2, cy - 5, w, 10),
                     border_radius=3)
    pygame.draw.rect(surf, (*_GOLD_PALE, 130), (cx - w // 2, cy - 5, w, 2),
                     border_radius=2)


def _crank(surf, cx, cy, r=14):
    """The turn crank: a gold disc, a dark hub, a knob arm."""
    _soft_glow(surf, cx, cy, r + 7, (236, 190, 96), 44, layers=4)
    disc = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
    for i in range(r, 0, -1):
        col = lerp_color((255, 226, 150), (170, 118, 28), (i / r) ** 0.8)
        pygame.draw.circle(disc, (*col, 255), (r + 1, r + 1), i)
    surf.blit(disc, (cx - r - 1, cy - r - 1))
    pygame.draw.circle(surf, (*_GOLD_DEEP, 230), (cx, cy), r, 1)
    kx, ky = cx + int(r * 0.55), cy - int(r * 0.55)
    pygame.draw.line(surf, (40, 28, 8), (cx, cy), (kx, ky), 4)
    pygame.draw.circle(surf, (30, 22, 8), (cx, cy), 4)
    pygame.draw.circle(surf, (60, 44, 16), (kx, ky), 5)
    pygame.draw.circle(surf, (*_GOLD_PALE, 220), (kx - 1, ky - 1), 2)


def _price_tag(surf, cx, cy, scale=1.0):
    """A small "5 + coin" price tag pill."""
    h = int(26 * scale)
    f = _font(max(12, int(15 * scale)), True)
    timg = f.render("5", True, (28, 18, 8))
    coin_d = int(h * 0.7)
    w = 12 + coin_d + 4 + timg.get_width() + 12
    tag = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    surf.blit(_vgrad_panel(w, h, h // 2, (255, 215, 120), _GOLD_DEEP), tag.topleft)
    pygame.draw.rect(surf, (*_GOLD_BRIGHT, 220), tag, width=1, border_radius=h // 2)
    x = tag.x + 12
    _coin_glyph(surf, x + coin_d // 2, cy, coin_d // 2)
    x += coin_d + 4
    surf.blit(timg, timg.get_rect(midleft=(x, cy)))


def _chute(surf, rect, with_capsule=True, cap_col=None):
    """A dark dispense chute with a gold lip and (optionally) a capsule in it."""
    surf.blit(_vgrad_panel(rect.w, rect.h, 8, (16, 14, 22), (4, 4, 8)),
              rect.topleft)
    pygame.draw.rect(surf, (0, 0, 0, 200), rect, width=1, border_radius=8)
    lip = pygame.Rect(rect.x + 8, rect.y - 3, rect.w - 16, 6)
    surf.blit(_vgrad_panel(lip.w, lip.h, 3,
                           lerp_color(_GOLD_BRIGHT, WHITE, 0.2), _GOLD_DEEP),
              lip.topleft)
    if with_capsule:
        col = cap_col or CAP_COLORS[0]
        _soft_glow(surf, rect.centerx, rect.centery + 4, 18, col[0], 64, layers=4)
        _capsule(surf, rect.centerx, rect.centery + 4, 16, col[0], col[1], -12)


def _marquee(surf, rect, text):
    """Gold marquee plate. A coin-slot glyph flanks the word so the label still
    reads at card scale even when the letterforms get small — the art-director
    flagged the bare text as muddy, so we icon-ify it."""
    surf.blit(_vgrad_panel(rect.w, rect.h, rect.h // 2,
                           lerp_color(_GOLD_BRIGHT, WHITE, 0.2), _GOLD_DEEP),
              rect.topleft)
    pygame.draw.rect(surf, (*_GOLD_DEEP, 235), rect, width=2,
                     border_radius=rect.h // 2)
    f = _font(max(12, rect.h - 9), True)
    img = f.render(text, True, (38, 24, 8))
    gap = 10
    glyph_r = (rect.h - 12) // 2
    total = glyph_r * 2 + gap + img.get_width() + gap + glyph_r * 2
    x0 = rect.centerx - total // 2
    cy = rect.centery
    # Left + right little capsule glyphs as bookends.
    _capsule(surf, x0 + glyph_r, cy, glyph_r, CAP_COLORS[0][0], CAP_COLORS[0][1])
    _capsule(surf, rect.centerx + total // 2 - glyph_r, cy, glyph_r,
             CAP_COLORS[1][0], CAP_COLORS[1][1])
    surf.blit(img, img.get_rect(center=(rect.centerx, cy)))


# ── trinkets (each ~24-32 px, drawn centred at cx,cy) ─────────────────────────

def _t_duck(surf, cx, cy):
    body = (255, 214, 64)
    shade = (214, 168, 30)
    pygame.draw.ellipse(surf, shade, (cx - 11, cy + 1, 22, 11))
    pygame.draw.ellipse(surf, body, (cx - 11, cy - 1, 22, 11))
    pygame.draw.circle(surf, body, (cx + 7, cy - 6), 6)
    pygame.draw.circle(surf, shade, (cx + 9, cy - 4), 6, 0)
    pygame.draw.circle(surf, body, (cx + 7, cy - 7), 6)
    pygame.draw.polygon(surf, (250, 140, 40),
                        [(cx + 12, cy - 6), (cx + 18, cy - 5), (cx + 12, cy - 3)])
    pygame.draw.circle(surf, (20, 20, 24), (cx + 8, cy - 8), 1)
    pygame.draw.arc(surf, shade, (cx - 6, cy - 4, 12, 10), 0.3, 2.6, 2)


def _t_fry(surf, cx, cy):
    """A single sad fry. Cut RIDGES down the length + a high-contrast sad face
    keep it unmistakably a fry, not a plain capsule, at 24 px (AD note)."""
    fry = (246, 200, 98)
    edge = (190, 144, 56)
    r = pygame.Rect(cx - 5, cy - 13, 10, 26)
    rounded_rect(surf, r, 3, fry)
    pygame.draw.rect(surf, edge, r, width=1, border_radius=3)
    # Cut ridges — the carved facets that make it a chip, not a pill.
    for rx in (cx - 2, cx + 1):
        pygame.draw.line(surf, (208, 158, 64), (rx, cy - 10), (rx, cy + 9), 1)
    pygame.draw.line(surf, (255, 234, 174), (cx - 3, cy - 10), (cx - 3, cy + 9), 1)
    # Salt fleck for read.
    pygame.draw.circle(surf, (255, 250, 235), (cx + 3, cy - 8), 1)
    # Sad face — bold, legible at small size.
    pygame.draw.circle(surf, (36, 26, 14), (cx - 2, cy - 1), 2)
    pygame.draw.circle(surf, (36, 26, 14), (cx + 3, cy - 1), 2)
    pygame.draw.circle(surf, (255, 255, 255), (cx - 2, cy - 2), 1)
    pygame.draw.circle(surf, (255, 255, 255), (cx + 3, cy - 2), 1)
    pygame.draw.arc(surf, (36, 26, 14), (cx - 4, cy + 4, 9, 6), 3.4, 6.0, 2)


def _t_eye(surf, cx, cy):
    """Googly eye. The pupil is ringed dark + given a bold black core so it holds
    contrast against the white sclera on the dark socket (AD note)."""
    pygame.draw.circle(surf, (248, 248, 250), (cx, cy), 11)
    pygame.draw.circle(surf, (150, 150, 160), (cx, cy), 11, 1)
    # Dark surround ring lifts pupil contrast where it overlaps the bright white.
    pygame.draw.circle(surf, (12, 12, 18), (cx + 3, cy + 3), 6)
    pygame.draw.circle(surf, (0, 0, 0), (cx + 3, cy + 3), 5)
    pygame.draw.circle(surf, (255, 255, 255), (cx + 1, cy + 1), 2)


def _t_clip(surf, cx, cy):
    """A clean bent-wire paperclip silhouette — two nested looped wires only, no
    cross-bar that could read as a magnifier (AD note)."""
    col = (210, 216, 226)
    dk = (150, 156, 168)
    # Outer loop.
    rounded_rect(surf, pygame.Rect(cx - 7, cy - 12, 14, 24), 7, None) if False else None
    pygame.draw.rect(surf, col, (cx - 7, cy - 12, 14, 24), width=2, border_radius=7)
    # Inner loop, offset down so the two wires nest like a real clip.
    pygame.draw.rect(surf, col, (cx - 4, cy - 6, 9, 16), width=2, border_radius=5)
    # Top hairpin that joins the loops (the clip's hook), kept simple.
    pygame.draw.line(surf, col, (cx - 4, cy - 6), (cx - 4, cy - 12), 2)
    pygame.draw.line(surf, dk, (cx + 5, cy + 9), (cx + 5, cy + 6), 2)


def _t_ribbon(surf, cx, cy):
    blue = (90, 150, 220)
    dk = (50, 100, 170)
    pygame.draw.circle(surf, (240, 220, 110), (cx, cy - 4), 7)
    for k in range(8):
        a = k * math.tau / 8
        x = cx + math.cos(a) * 8
        y = cy - 4 + math.sin(a) * 8
        pygame.draw.line(surf, dk, (cx, cy - 4), (x, y), 3)
    pygame.draw.circle(surf, blue, (cx, cy - 4), 5)
    pygame.draw.circle(surf, (220, 230, 245), (cx - 1, cy - 5), 1)
    pygame.draw.polygon(surf, blue, [(cx - 5, cy + 2), (cx - 8, cy + 13), (cx - 1, cy + 8)])
    pygame.draw.polygon(surf, dk, [(cx + 5, cy + 2), (cx + 8, cy + 13), (cx + 1, cy + 8)])


def _t_gerald(surf, cx, cy):
    """Gerald — a tiny sandstone-pillar figurine with a face."""
    sand = (216, 176, 116)
    dk = (170, 130, 78)
    r = pygame.Rect(cx - 8, cy - 13, 16, 26)
    rounded_rect(surf, r, 3, sand)
    pygame.draw.rect(surf, dk, r, width=1, border_radius=3)
    pygame.draw.rect(surf, dk, (cx - 10, cy - 13, 20, 4), border_radius=2)
    pygame.draw.rect(surf, dk, (cx - 10, cy + 9, 20, 4), border_radius=2)
    pygame.draw.line(surf, dk, (cx - 6, cy - 2), (cx + 6, cy - 2), 1)
    pygame.draw.circle(surf, (40, 30, 20), (cx - 3, cy + 2), 1)
    pygame.draw.circle(surf, (40, 30, 20), (cx + 3, cy + 2), 1)
    pygame.draw.arc(surf, (40, 30, 20), (cx - 3, cy + 3, 6, 4), 3.5, 5.9, 1)


def _t_moth(surf, cx, cy):
    """A drab moth. Wings nudged lighter than round 1 with a crisp dark edge so
    the silhouette doesn't muddy into the socket (AD note)."""
    wing = (205, 194, 174)
    wing_dk = (150, 138, 116)
    edge = (96, 86, 70)
    body = (78, 66, 52)
    pts_l = [(cx, cy - 7), (cx - 12, cy - 9), (cx - 13, cy + 1),
             (cx - 7, cy + 8), (cx, cy + 4)]
    pts_r = [(cx, cy - 7), (cx + 12, cy - 9), (cx + 13, cy + 1),
             (cx + 7, cy + 8), (cx, cy + 4)]
    for pts in (pts_l, pts_r):
        pygame.draw.polygon(surf, wing, pts)
        pygame.draw.polygon(surf, edge, pts, 1)
    # Lower hindwings, slightly darker for two-tone wing read.
    pygame.draw.polygon(surf, wing_dk, [(cx, cy + 2), (cx - 7, cy + 9),
                                        (cx - 2, cy + 11)])
    pygame.draw.polygon(surf, wing_dk, [(cx, cy + 2), (cx + 7, cy + 9),
                                        (cx + 2, cy + 11)])
    pygame.draw.circle(surf, (60, 42, 32), (cx - 6, cy - 3), 2)  # eyespots
    pygame.draw.circle(surf, (60, 42, 32), (cx + 6, cy - 3), 2)
    pygame.draw.ellipse(surf, body, (cx - 2, cy - 9, 5, 18))     # furry body
    pygame.draw.line(surf, edge, (cx - 1, cy - 9), (cx - 4, cy - 13), 1)
    pygame.draw.line(surf, edge, (cx + 1, cy - 9), (cx + 4, cy - 13), 1)


TRINKETS = [
    ("DUCK", _t_duck), ("FRY", _t_fry), ("EYE", _t_eye), ("CLIP", _t_clip),
    ("RIBBON", _t_ribbon), ("GERALD", _t_gerald), ("MOTH", _t_moth),
]


def _junk_shelf(surf, x, y, w):
    """The JUNK DRAWER shelf: an obsidian ledge with a gold label and the trinket
    row standing in dark inset sockets on a thin gold rail."""
    h = 70
    shelf = pygame.Rect(x, y, w, h)
    _drop_shadow(surf, shelf, 12, blur=5, alpha=120)
    surf.blit(_vgrad_panel(shelf.w, shelf.h, 12, _OBS_TOP, _OBS_BOT, 252),
              shelf.topleft)
    pygame.draw.rect(surf, (*_GOLD_DEEP, 200), shelf.inflate(-6, -6), width=1,
                     border_radius=9)
    pygame.draw.rect(surf, (*_GOLD_BRIGHT, 150), shelf, width=1, border_radius=12)
    hdr = _font(12, True).render("JUNK  DRAWER", True, _GOLD_PALE)
    surf.blit(hdr, (x + 14, y + 7))
    rail_y = y + h - 15
    _gold_rule(surf, x + 14, x + w - 14, rail_y + 9, peak=120)
    slot_w = (w - 28) / len(TRINKETS)
    for i, (label, fn) in enumerate(TRINKETS):
        tcx = int(x + 14 + slot_w * (i + 0.5))
        tcy = y + 34
        _inset_disc(surf, tcx, tcy, 16, tint=(10, 10, 16))
        fn(surf, tcx, tcy)
        lab = _font(8, True).render(label, True, _GOLD_PALE)
        lab.set_alpha(205)
        surf.blit(lab, lab.get_rect(center=(tcx, rail_y + 5)))


# ── the LEAD machine (V1 body + V5 framing) ──────────────────────────────────

def machine_lead(surf, x, y, w, h, seed=1):
    """V1 freestanding cabinet grafted with V5's crown framing + CURIOS plate.

    Tall obsidian body, a crowned capsule globe up top, an icon-ified marquee, a
    slot+crank control row over a CURIOS nameplate, and a wide chute drawer at
    the foot with the dispensed capsule — the joke landing."""
    body = pygame.Rect(x, y, w, h)
    _drop_shadow(surf, body, 20, blur=8, alpha=160)
    surf.blit(_vgrad_panel(body.w, body.h, 20, _OBS_TOP, _OBS_BOT, 252),
              body.topleft)
    pygame.draw.rect(surf, (*_GOLD_DEEP, 215), body.inflate(-10, -10), width=2,
                     border_radius=15)
    pygame.draw.rect(surf, (*_GOLD_BRIGHT, 165), body, width=1, border_radius=20)
    cx = body.centerx

    # Crown shoulders (V5 framing): a rounded gold-edged cap behind the globe.
    gr = w // 2 - 22
    gcy = y + gr + 30
    crown = pygame.Rect(cx - gr - 8, y + 14, (gr + 8) * 2, gr + 26)
    surf.blit(_vgrad_panel(crown.w, crown.h, 18, (34, 30, 42), (16, 14, 24), 230),
              crown.topleft)
    pygame.draw.rect(surf, (*_GOLD_DEEP, 200), crown, width=1, border_radius=18)
    # Gold capsule finial replaces the legendary-gem finial.
    _gold_capsule_finial(surf, cx, y + 6, r=9)

    _globe(surf, cx, gcy, gr, n_caps=13, seed=seed)

    # Icon-ified marquee.
    my = gcy + gr + 14
    _marquee(surf, pygame.Rect(x + 18, my, w - 36, 26), "GACHA")

    # Control row.
    py = my + 42
    _coin_slot(surf, cx - 34, py)
    _crank(surf, cx + 34, py, r=15)
    _price_tag(surf, cx, py + 2, scale=0.9)

    # CURIOS nameplate (V5 tone).
    plate = pygame.Rect(cx - 56, py + 30, 112, 22)
    surf.blit(_vgrad_panel(plate.w, plate.h, 6, (40, 32, 18), (20, 14, 8)),
              plate.topleft)
    pygame.draw.rect(surf, (*_GOLD_BRIGHT, 200), plate, width=1, border_radius=6)
    _gradient_text(surf, "CURIOS", _font(13, True), plate.center,
                   (255, 240, 180), (236, 170, 60), shadow=True)

    # Chute drawer + the dispensed capsule (the joke landing).
    chute = pygame.Rect(x + 24, body.bottom - 50, w - 48, 38)
    _chute(surf, chute, with_capsule=True,
           cap_col=CAP_COLORS[seed % len(CAP_COLORS)])


# ── compose the sheet ────────────────────────────────────────────────────────

def _bg(surf, rect):
    n = len(_BG_STOPS)
    for yy in range(rect.h):
        f = yy / max(1, rect.h - 1)
        seg = min(n - 2, int(f * (n - 1)))
        local = (f * (n - 1)) - seg
        pygame.draw.line(surf, lerp_color(_BG_STOPS[seg], _BG_STOPS[seg + 1], local),
                         (rect.x, rect.y + yy), (rect.right, rect.y + yy))


def main():
    # Judge at SHIP scale: one true 360 px arcade card, plus a capsule-swatch
    # strip so the AD can read the re-drawn payload in isolation.
    CARD_W = 360
    pad = 16
    card_h = 560
    swatch_h = 96
    sheet_w = CARD_W + pad * 2
    sheet_h = 44 + card_h + pad + swatch_h + pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((6, 6, 14))

    _gradient_text(sheet, "VENDING MACHINE  —  ROUND 2  (360 px)",
                   _font(18, True), (sheet_w // 2, 20),
                   (255, 240, 180), (236, 170, 60), outline=_RED_OUTLINE)

    # The lead card at true 360 px width.
    card = pygame.Rect(pad, 40, CARD_W, card_h)
    _bg(sheet, card)
    pygame.draw.rect(sheet, (*_GOLD_DEEP, 130), card, width=1, border_radius=12)

    mw, mh = 200, 372
    mx = card.centerx - mw // 2
    my = card.y + 16
    machine_lead(sheet, mx, my, mw, mh, seed=3)

    # Junk drawer along the card bottom at true width.
    _junk_shelf(sheet, card.x + 14, card.bottom - 86, CARD_W - 28)

    # Capsule swatch strip — isolate the re-drawn payload for the AD.
    sw = pygame.Rect(pad, card.bottom + pad, CARD_W, swatch_h)
    _bg(sheet, sw)
    pygame.draw.rect(sheet, (*_GOLD_DEEP, 130), sw, width=1, border_radius=12)
    lab = _font(11, True).render("CAPSULE PAYLOAD  (two-tone, glossy dome)",
                                 True, _GOLD_PALE)
    sheet.blit(lab, (sw.x + 12, sw.y + 8))
    n = len(CAP_COLORS)
    step = (sw.w - 40) / n
    for i, (top, bot) in enumerate(CAP_COLORS):
        scx = int(sw.x + 24 + step * (i + 0.5))
        scy = sw.y + 58
        _inset_disc(sheet, scx, scy, 22, tint=(12, 12, 18))
        _capsule(sheet, scx, scy, 17, top, bot, (i - 2.5) * 14)

    out_dir = "docs/profile/vending_machine"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_2.png")
    pygame.image.save(sheet, out_path)
    print("WROTE", os.path.abspath(out_path), sheet.get_size())


if __name__ == "__main__":
    main()
