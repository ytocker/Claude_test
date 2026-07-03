"""
CONSTELLATION store — HEADER element exploration (wordmark + balance capsule).

The header is the top chrome of the store: the "STORE" gold wordmark and the
coin-balance capsule. Both are authored resolution-independently and rendered at
SS=4, then smoothscaled once to the logical target — the same crispness lever the
shared pipeline mandates. We import the reference pipeline (render_hi) so palette,
fonts, glow caches, bevel/sheen helpers and the night-sky background are byte-for-
byte the same as the rest of the screen; this element can NEVER drift from the
locked theme because it draws with the theme's own primitives.

Three wordmark treatments + one refined capsule are shown on the shared bg at a
large, SS-crisp scale so the art-director can judge the bevel quality and the
wordmark<->capsule vertical rhythm. Pure pygame, both build targets safe.
"""
import os
import sys
import math

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", "..", "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

# Reuse the locked pipeline wholesale — same SS, palette, fonts and primitives.
_REF = os.path.abspath(os.path.join(_HERE, "..", "..", "constellation_hi"))
if _REF not in sys.path:
    sys.path.insert(0, _REF)
import render_hi as R
from render_hi import (
    m, mf, font, SS, _glyph_base, _stamp_bold, vgrad, multistop_v, soft_glow,
    drop_shadow, gradient_text, plain_text, coin_glyph, bevel_rim, top_sheen,
    contact_shadow, gold_rule, gloss_sweep, _build_static_bg, draw_bg,
    BG_STOPS, NEBULA_GLOW, GOLD, GOLD_PALE, GOLD_DEEP,
)
from game.draw import lerp_color, NEAR_BLACK, WHITE

BALANCE = 14250


# =============================================================================
# Wordmark treatments — three genuinely different bevel approaches, all "clean
# gold bevel, single specular sweep, soft contact shadow" per the brief (no
# chunky faux-3D extrude).
# =============================================================================

def _wordmark_body(txt, f, tracking, bold, top_stop, mid_stop, bot_stop):
    """Shared core: a faux-bold white master + a vertical gold gradient mapped
    over the GLYPH's true cap->baseline extent (so the bright crown sits at the
    caps, not in the padding). Returns (gradient_surface, base_master, rect_size,
    bounding_box). Caller composites shadow/keyline/specular around it."""
    base = _glyph_base(txt, f, tracking)
    base = _stamp_bold(base, bold)
    w, hh = base.get_size()
    bb = base.get_bounding_rect()
    top_y, gh = bb.y, max(1, bb.h)
    grad = pygame.Surface((w, hh), pygame.SRCALPHA)
    for y in range(hh):
        t = max(0.0, min(1.0, (y - top_y) / gh))
        if t < 0.5:
            c = lerp_color(top_stop, mid_stop, t / 0.5)
        else:
            c = lerp_color(mid_stop, bot_stop, (t - 0.5) / 0.5)
        pygame.draw.line(grad, c, (0, y), (w, y))
    body = base.copy()
    body.blit(grad, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return body, base, (w, hh), (top_y, gh)


def _contact_shadow_glyph(surf, base, r, soft=True):
    """One soft contact shadow under a glyph (multi-offset falloff, not a hard
    drop). Top-left light => shadow drops down + slightly right."""
    steps = ((m(3), 55), (m(2), 85), (m(1), 120)) if soft else ((m(1), 130),)
    for k, a in steps:
        sh = base.copy()
        sh.fill((5, 3, 12, 255), special_flags=pygame.BLEND_RGBA_MULT)
        sh.set_alpha(a)
        surf.blit(sh, (r.x + m(0.4), r.y + k + m(2)))


def _keyline_glyph(surf, base, r, color, px, steps=12):
    """A tight dark contour ring around the glyph so the gold edge reads crisp
    against the night sky (the theme's 'defined edge' rule)."""
    kl = base.copy()
    kl.fill((*color, 255), special_flags=pygame.BLEND_RGBA_MULT)
    for i in range(steps):
        ang = 360 * i / steps
        dx = int(round(px * math.cos(math.radians(ang))))
        dy = int(round(px * math.sin(math.radians(ang))))
        surf.blit(kl, (r.x + dx, r.y + dy))


def _cap_specular(surf, base, r, top_y, gh, frac=0.07, peak=46):
    """A single thin specular band hugging the cap edge only — the polished-
    bevel crown tell. Clipped to the glyph silhouette, low alpha (not a white
    cap)."""
    w, hh = base.get_size()
    spec = pygame.Surface((w, hh), pygame.SRCALPHA)
    glint = max(1, int(gh * frac))
    for i in range(glint):
        a = int(peak * (1 - i / glint) ** 1.5)
        pygame.draw.line(spec, (255, 246, 210, a), (0, top_y + i), (w, top_y + i))
    sm = base.copy()
    sm.fill((255, 255, 255, 255), special_flags=pygame.BLEND_RGBA_MULT)
    spec.blit(sm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(spec, r.topleft, special_flags=pygame.BLEND_ADD)


def wordmark_A(surf, txt, center, size, tracking):
    """A — CLEAN ROYAL BEVEL (the brief's baseline, refined).
    One warm-gold gradient body, a fine dark keyline, a single cap-edge specular
    glint, and a soft contact shadow. Stroke weight is even, no extrude. This is
    the safe, premium casual-mobile gold wordmark."""
    f = font(size)
    body, base, (w, hh), (top_y, gh) = _wordmark_body(
        txt, f, tracking, m(1.3),
        (252, 210, 118), (242, 180, 78), (188, 118, 32))
    r = base.get_rect(center=center)
    _contact_shadow_glyph(surf, base, r)
    _keyline_glyph(surf, base, r, (78, 40, 8), m(1.7))
    surf.blit(body, r.topleft)
    _cap_specular(surf, base, r, top_y, gh)
    return r


def wordmark_B(surf, txt, center, size, tracking):
    """B — RIMMED EMBOSS (a touch more depth, still clean).
    Adds a thin dark interior bottom shadow for a raised-plate read, a hairline
    outer rust rim (theme's red-outline accent) hugging the dark keyline, and a
    top-left CONTOUR emboss (lit silhouette minus body) that lights only the
    protruding rim — never the flat cap bars — so it stays crisp, not washed."""
    f = font(size)
    body, base, (w, hh), (top_y, gh) = _wordmark_body(
        txt, f, tracking, m(1.4),
        (248, 200, 108), (236, 172, 70), (172, 104, 24))
    r = base.get_rect(center=center)
    _contact_shadow_glyph(surf, base, r)
    # hairline rust outer rim then the dark keyline inside it (defined edge)
    rust = base.copy()
    rust.fill((150, 44, 18, 255), special_flags=pygame.BLEND_RGBA_MULT)
    for i in range(12):
        ang = 360 * i / 12
        dx = int(round(m(2.4) * math.cos(math.radians(ang))))
        dy = int(round(m(2.4) * math.sin(math.radians(ang))))
        surf.blit(rust, (r.x + dx, r.y + dy))
    _keyline_glyph(surf, base, r, (72, 34, 6), m(1.5))
    # dark interior bottom shadow: the body nudged DOWN, dim, clipped to silhouette
    dk = base.copy()
    dk.fill((120, 70, 18, 255), special_flags=pygame.BLEND_RGBA_MULT)
    dk.set_alpha(150)
    surf.blit(dk, (r.x, r.y + m(1.4)))
    surf.blit(body, r.topleft)
    # bright top-left CONTOUR emboss (the lit raised edge): the silhouette nudged
    # up-left, MINUS the body = only the protruding top-left rim survives. This
    # lights the contour, never flat cap bars — so STORE's flat-topped letters
    # never wash to white blocks (the pipeline's known failure mode).
    off = max(1, m(0.7))
    rim = pygame.Surface((w, hh), pygame.SRCALPHA)
    lit = base.copy()
    lit.fill((255, 244, 210, 255), special_flags=pygame.BLEND_RGBA_MULT)
    rim.blit(lit, (-off, -off))
    cut = base.copy()
    cut.fill((255, 255, 255, 255), special_flags=pygame.BLEND_RGBA_MULT)
    rim.blit(cut, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
    rim.set_alpha(170)
    surf.blit(rim, r.topleft, special_flags=pygame.BLEND_ADD)
    return r


def wordmark_C(surf, txt, center, size, tracking):
    """C — BEVEL + CONSTELLATION FLOURISH (the 'tasteful flourish' option).
    The clean bevel of A, plus a small constellation motif: a tapered gold
    hairline arcing over the word with three node stars (echoing the bg
    constellation language), and two tiny sparkles flanking the word. The type
    stays clean; the flourish is the only added decoration so it doesn't read
    busy."""
    r = wordmark_A(surf, txt, center, size, tracking)
    # a gentle constellation arc above the caps with node stars
    cx = center[0]
    top = r.top - m(7)
    span = r.width * 0.62
    nodes = []
    for t in (-1.0, -0.45, 0.15, 0.7, 1.0):
        nx = cx + t * span / 2
        ny = top - math.cos(t * 1.1) * m(5)
        nodes.append((int(nx), int(ny)))
    # tapered hairline through the nodes (fades at both ends like the bg threads)
    for i, (a, b) in enumerate(zip(nodes, nodes[1:])):
        seg_a = 150 - abs(i - 1.5) * 24
        pygame.draw.line(surf, (218, 188, 122, max(40, int(seg_a))),
                         a, b, max(1, m(0.9)))
    # node stars: small glow + crisp core, brightest in the middle
    for i, (nx, ny) in enumerate(nodes):
        bright = 1.0 - abs(i - 2) / 3.0
        soft_glow(surf, nx, ny, m(3.2), (255, 226, 160), int(70 + 70 * bright), layers=4)
        pygame.draw.circle(surf, (255, 236, 184, 235), (nx, ny),
                           max(1, int(m(1.0 + 0.7 * bright))))
    # two 4-point sparkles flanking the word, on the baseline-ish line
    for sx in (r.left - m(13), r.right + m(13)):
        sy = center[1]
        L = m(4.5)
        soft_glow(surf, sx, sy, m(3.5), (255, 240, 200), 90, layers=4)
        for dx, dy in ((L, 0), (0, L)):
            pygame.draw.line(surf, (255, 246, 214, 220), (sx - dx, sy - dy),
                             (sx + dx, sy + dy), max(1, m(0.8)))
    return r


# =============================================================================
# Balance capsule — recessed jewel-gold capsule, coin in its OWN cell, clear gap,
# then a LOUD gradient-gold number. Defined edge (dark keyline + bright bevel).
# =============================================================================

def balance_capsule(surf, cx, y, value=BALANCE, coin_size=28, num_size=25,
                    divider=True):
    """The money read. A recessed deep-amber capsule (so the bright number and
    coin sit IN a jewel well, not on a flat pill), with: a guaranteed gap between
    a beveled coin cell and the first digit (enforced in device px so it survives
    downscale), an optional faint gold cell divider, a loud faux-bold gradient-
    gold number with a dark keyline, a crisp dark outer keyline UNDER a bright
    top-left bevel (the theme's defined edge), and a single top gloss sweep."""
    val = f"{value:,}"
    vf = font(num_size)
    vw = _glyph_base(val, vf, 0).get_width() + m(2)        # account for faux-bold
    coin_d = m(coin_size)
    gapc = m(18)                                           # coin -> first digit
    padl, padr = m(16), m(22)
    w = padl + coin_d + gapc + vw + padr
    h = m(44)
    cap = pygame.Rect(cx - w // 2, y - h // 2, w, h)

    drop_shadow(surf, cap, h // 2, blur=m(7), alpha=140, dy=m(3))
    # recessed deep-amber body (top-darker so it reads as a sunken well)
    surf.blit(vgrad(cap.w, cap.h, h // 2, (60, 44, 22), (24, 16, 8), 255, gamma=1.12),
              cap.topleft)
    top_sheen(surf, cap, h // 2, m(16), peak=52)
    contact_shadow(surf, cap, h // 2, m(6), alpha=120)
    # defined edge: dark contact keyline UNDER a bright top-left bevel
    pygame.draw.rect(surf, (0, 0, 0, 205), cap, width=max(1, m(1.9)),
                     border_radius=h // 2)
    bevel_rim(surf, cap, h // 2, lerp_color(GOLD, NEAR_BLACK, 0.42),
              (*GOLD_PALE, 245), w=max(1, m(1.9)))

    x = cap.x + padl
    coin_cx = x + coin_d // 2
    # coin in its own cell: a soft seat glow + the beveled coin
    soft_glow(surf, coin_cx, y, coin_d, (255, 206, 92), 120, layers=6)
    coin_glyph(surf, coin_cx, y, coin_d // 2)
    x += coin_d + gapc
    if divider:
        # a faint warm-gold cell divider between the coin cell and the number,
        # set just left of the digits (does NOT touch the first digit)
        dvx = coin_cx + coin_d // 2 + gapc // 2
        dv = pygame.Surface((max(1, m(1.4)), h - m(18)), pygame.SRCALPHA)
        for yy in range(dv.get_height()):
            d = abs(yy - dv.get_height() / 2) / (dv.get_height() / 2)
            a = int(120 * (1 - d ** 1.5))
            dv.fill((232, 196, 120, a), (0, yy, dv.get_width(), 1))
        surf.blit(dv, (dvx - dv.get_width() // 2, y - dv.get_height() // 2))
    # the LOUD gradient-gold number
    gradient_text(surf, val, vf, (x + vw // 2, y), (255, 250, 214), (240, 178, 66),
                  weight=m(1.0), keyline=(96, 56, 12), kw=m(1.3), shadow=True)
    return cap


# =============================================================================
# Compose the exploration sheet
# =============================================================================
TILE_W, TILE_H = 360, 188
COLS, ROWS = 2, 2


def _tile_device(label, draw_fn):
    """One labeled tile rendered at SS on the shared night-sky bg."""
    dw, dh = m(TILE_W), m(TILE_H)
    surf = pygame.Surface((dw, dh))
    # reuse the shared bg, cropped to the tile (so every tile is the real canvas)
    bg = pygame.Surface((R.DW, R.DH))
    draw_bg(bg)
    surf.blit(bg, (0, 0), pygame.Rect(0, 0, dw, dh))
    # faint top legibility band like the live header
    band = pygame.Surface((dw, m(60)), pygame.SRCALPHA)
    for yy in range(m(60)):
        a = int(110 * (1 - yy / m(60)) ** 1.2)
        pygame.draw.line(band, (16, 16, 48, a), (0, yy), (dw, yy))
    surf.blit(band, (0, 0))
    draw_fn(surf, dw, dh)
    # tile caption (bottom-left), muted
    plain_text(surf, label, font(10), (m(8) + _glyph_base(label, font(10), 0).get_width() // 2,
                                       dh - m(12)),
               (210, 200, 170), shadow_a=150, weight=m(0.6))
    # tile keyline so the grid reads as separate cells
    pygame.draw.rect(surf, (*GOLD, 50), (0, 0, dw, dh), width=max(1, m(1)))
    return surf


def _draw_A(surf, dw, dh):
    wordmark_A(surf, "STORE", (dw // 2, m(40)), 34, tracking=m(4))
    balance_capsule(surf, dw // 2, m(108))


def _draw_B(surf, dw, dh):
    wordmark_B(surf, "STORE", (dw // 2, m(40)), 34, tracking=m(4))
    balance_capsule(surf, dw // 2, m(108))


def _draw_C(surf, dw, dh):
    wordmark_C(surf, "STORE", (dw // 2, m(44)), 34, tracking=m(4))
    balance_capsule(surf, dw // 2, m(112))


def _draw_capsule_zoom(surf, dw, dh):
    """A close look at the capsule alone (large), so the coin/gap/number and the
    edge finish can be judged in isolation."""
    plain_text(surf, "BALANCE CAPSULE — coin cell  /  gap  /  loud number  /  defined edge",
               font(9), (dw // 2, m(16)), GOLD_PALE, shadow_a=130, weight=m(0.6),
               keyline=(10, 10, 24), kw=m(0.6))
    balance_capsule(surf, dw // 2, m(70), coin_size=34, num_size=30)
    # a smaller instance to show it holds up at the live header size
    balance_capsule(surf, dw // 2, m(132), coin_size=28, num_size=25)


def build_sheet():
    _build_static_bg()
    tiles = [
        ("A  CLEAN ROYAL BEVEL", _draw_A),
        ("B  RIMMED EMBOSS + GLOSS", _draw_B),
        ("C  BEVEL + CONSTELLATION FLOURISH", _draw_C),
        ("CAPSULE (zoom)", _draw_capsule_zoom),
    ]
    gap = m(10)
    pad = m(14)
    title_h = m(40)
    tw, th = m(TILE_W), m(TILE_H)
    sheet_w = pad * 2 + tw * COLS + gap * (COLS - 1)
    sheet_h = pad * 2 + title_h + th * ROWS + gap * (ROWS - 1)
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.blit(multistop_v(sheet_w, sheet_h, BG_STOPS), (0, 0))
    soft_glow(sheet, sheet_w // 2, sheet_h // 2, m(260), NEBULA_GLOW, 45, layers=8)
    gradient_text(sheet, "STORE HEADER — WORDMARK + BALANCE CAPSULE",
                  font(14), (sheet_w // 2, pad + title_h // 2 - m(2)),
                  (255, 250, 214), (240, 178, 66), weight=m(0.8),
                  keyline=(96, 56, 12), kw=m(1.0), shadow=True)
    for i, (label, fn) in enumerate(tiles):
        c, rrow = i % COLS, i // COLS
        x = pad + c * (tw + gap)
        yy = pad + title_h + rrow * (th + gap)
        sheet.blit(_tile_device(label, fn), (x, yy))
    return sheet


def main():
    sheet = build_sheet()
    # one smoothscale down — the SS crispness lever, identical to the pipeline
    sw, sh = sheet.get_size()
    out = pygame.transform.smoothscale(sheet, (sw // SS, sh // SS))
    path = os.path.join(_HERE, "round_1.png")
    pygame.image.save(out, path)
    print("saved", path, "size", out.get_size())


if __name__ == "__main__":
    main()
