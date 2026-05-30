"""HUD: score, hi-score, coin count, power-up timer bar, pause button."""
import math
import os
import random
import pygame

from game.config import W, H, TRIPLE_DURATION, MAGNET_DURATION, MEGAMAGNET_DURATION, SLOWMO_DURATION, KFC_DURATION, GHOST_DURATION, GROW_DURATION, REVERSE_DURATION, SHRINK_DURATION
from game.draw import (
    rounded_rect, rounded_rect_grad, lerp_color,
    UI_SCORE, UI_GOLD, UI_ORANGE, UI_SHADOW, UI_CREAM, UI_RED,
    COIN_GOLD, COIN_DARK,
    WHITE, NEAR_BLACK,
)
from game import parrot
# Run-summary stat-tile icons reuse the actual in-game art so the
# COINS tile shows the spinning coin face the player saw mid-flight.
# (game.powerup_help imports from game.hud — its `_powerup_icon` is
# imported lazily inside draw_stats to avoid the circular import.)
from game.entities import _get_coin_face as _ingame_coin_face
from game.config import COIN_R

_grow_parrot_hud: "pygame.Surface | None" = None

def _get_grow_parrot_hud() -> "pygame.Surface":
    global _grow_parrot_hud
    if _grow_parrot_hud is None:
        src = parrot.FRAMES[1]
        target_w = 16
        ratio = target_w / src.get_width()
        target_h = int(src.get_height() * ratio)
        _grow_parrot_hud = pygame.transform.smoothscale(src, (target_w, target_h))
    return _grow_parrot_hud

# ── Theme palette matching the HTML welcome screen ───────────────────────────
_GOLD_BRIGHT    = (240, 192,  64)   # #f0c040
_GOLD_MUTED     = (216, 184,  85)   # #d8b855
_RED_OUTLINE    = (168,  32,  16)   # #a82010
_ORANGE_BORDER  = (232, 104,  40)   # #e86828
_SCARLET_TOP    = (240,  55,  55)   # #f03737  pill gradient top
_SCARLET_BOT    = (148,  20,  20)   # #941414  pill gradient bottom
# Dim pill colours used by the menu's three CTAs. Tuned so the gradient
# is anchored on _RED_OUTLINE — the rust red that rims the SKYBIT title
# on the same screen — with a brighter highlight above it and a darker
# shade below. The dim path also skips the cream frost overlay (see
# _pill_btn): on a saturated rust gradient the cream tinted the top
# pinkish, which is exactly what made the buttons read as a different
# colour family from the title.
_SCARLET_TOP_DIM = (220,  45,  22)  # #dc2d16  brighter rust (top of grad)
_SCARLET_BOT_DIM = (110,  22,  10)  # #6e160a  darker rust  (bottom of grad)
_SCARLET_SHADOW = ( 60,   8,   8)   # #3c0808  pill text shadow
_GOLD_DEEP      = (180, 130,  20)   # #b48214  inner laurel/ring tone
_GOLD_PALE      = (255, 232, 168)   # #ffe8a8  bright highlight for engraving
_PANEL_DARK     = ( 12,   8,  38)   # deep purple panel
_PANEL_LIGHTER  = ( 26,  18,  62)   # navy gradient stop above PANEL_DARK
_NIGHT_DEEP     = (  6,   1,  21)   # #060115


_fonts: dict = {}


# ── Theme drawing helpers ────────────────────────────────────────────────────

def _outlined_text(surf, txt, center, size, fill=_GOLD_BRIGHT,
                   outline=_RED_OUTLINE, px=3, shadow_offset=(3, 5)):
    """Gold text with red pixel outline — matches the welcome screen title.
    ``shadow_offset=None`` skips the drop shadow for a flat title."""
    f = _font(size, True)
    img = f.render(txt, True, fill)
    out = f.render(txt, True, outline)
    r = img.get_rect(center=center)
    offsets = [(-px, 0), (px, 0), (0, -px), (0, px),
               (-px, -px), (px, -px), (-px, px), (px, px)]
    for ox, oy in offsets:
        surf.blit(out, (r.x + ox, r.y + oy))
    if shadow_offset is not None:
        sh = f.render(txt, True, NEAR_BLACK)
        sh.set_alpha(170)
        surf.blit(sh, (r.x + shadow_offset[0], r.y + shadow_offset[1]))
    surf.blit(img, r.topleft)
    return r


# ── Score numerals match the `main` deployment: a cream face over a 2px
# deep-gold rim (a uniform 8-offset stamp) and a soft near-black drop — one
# clear bright shape that reads over a bright-sky pillar and at night. No
# per-frame supersample (just three small text renders per draw), so it is cheap
# enough to run uncached. Drawn inline in draw_play.
_SCORE_FACE = (252, 244, 220)      # warm-cream digit face (the `main` value)


def _pill_btn(surf, center, text, size=20, alpha=255, wide=False,
              min_width=None, primary=False, dim=False, shadow=True):
    """Scarlet body + gold border + cream text, with drop shadow, top-half
    frosting, gold accent line and (optionally) a gold glow when
    ``primary=True`` — the canonical Pip Scarlet pill from the menu
    mockup (see tools/gen_scarlet_set.py::pill). Returns the rect so
    callers can hit-test clicks. ``min_width`` lets paired buttons
    (SUBMIT + SKIP) share one width regardless of label length.
    ``dim=True`` swaps the bright scarlet gradient for the dimmer
    bordeaux pair so the menu trio sits more quietly in the night-sky
    palette. ``shadow=False`` drops the cast shadow — stacked tightly on
    the menu the offset shade read as a detached smudge under each pill,
    so the trio sits flat on the night sky instead."""
    f = _font(size, True)
    img = f.render(text, True, WHITE)
    pad_x = 64 if wide else 44
    pw = img.get_width() + pad_x
    if min_width is not None:
        pw = max(pw, min_width)
    ph = img.get_height() + 22
    cx, cy = center
    x = cx - pw // 2
    y = cy - ph // 2
    grad_top = _SCARLET_TOP_DIM if dim else _SCARLET_TOP
    grad_bot = _SCARLET_BOT_DIM if dim else _SCARLET_BOT

    # Optional gold halo on the primary action button.
    if primary:
        glow = pygame.Surface((pw + 24, ph + 24), pygame.SRCALPHA)
        for r in range(12, 0, -1):
            a = int(48 * r / 12 / 4)
            pygame.draw.rect(glow, (*_GOLD_BRIGHT, a),
                             (12 - r, 12 - r, pw + r * 2, ph + r * 2),
                             border_radius=(ph + r * 2) // 2)
        surf.blit(glow, (x - 12, y - 12))

    # Drop shadow.
    if shadow:
        sh = pygame.Surface((pw + 4, ph + 4), pygame.SRCALPHA)
        pygame.draw.rect(sh, (0, 0, 0, 90),
                         (0, 0, pw + 4, ph + 4),
                         border_radius=(ph + 4) // 2)
        surf.blit(sh, (x - 2, y + 6))

    # Body: scarlet vertical gradient.
    pill = pygame.Surface((pw, ph), pygame.SRCALPHA)
    for yy in range(ph):
        t = yy / max(1, ph - 1)
        c = lerp_color(grad_top, grad_bot, t)
        pygame.draw.line(pill, c, (0, yy), (pw - 1, yy))

    # Frosting on the top half + bottom darkening on the lower half so the
    # gradient reads as a glossy 3D pill rather than a flat colour ramp.
    # On dim pills the cream tinted the saturated rust gradient pinkish
    # — exactly what made the menu CTAs read as a different colour
    # family from the SKYBIT title outline — so we skip the cream
    # frost there and rely on the gradient alone for top highlight.
    if not dim:
        frost = pygame.Surface((pw, ph), pygame.SRCALPHA)
        for yy in range(ph // 2):
            a = int(50 * (1 - yy / (ph / 2)))
            pygame.draw.line(frost, (255, 245, 220, a), (0, yy), (pw, yy))
        pill.blit(frost, (0, 0))
    bsh = pygame.Surface((pw, ph), pygame.SRCALPHA)
    for yy in range(ph // 2, ph):
        a = int(55 * (yy - ph // 2) / (ph / 2))
        pygame.draw.line(bsh, (0, 0, 0, a), (0, yy), (pw, yy))
    pill.blit(bsh, (0, 0))

    # Clip to a rounded-rect mask.
    mask = pygame.Surface((pw, ph), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, pw, ph),
                     border_radius=ph // 2)
    pill.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    # Gold border + thin gold accent line just inside the top.
    pygame.draw.rect(pill, _GOLD_BRIGHT, (0, 0, pw, ph),
                     width=2, border_radius=ph // 2)
    pygame.draw.line(pill, (*_GOLD_BRIGHT, 110),
                     (ph // 2, 3), (pw - ph // 2, 3), 1)

    pill.set_alpha(alpha)
    surf.blit(pill, (x, y))

    # Label: scarlet shadow then cream face, so the text feels embossed
    # rather than floating on top of the gradient.
    sh_img = f.render(text, True, _SCARLET_SHADOW)
    sh_img.set_alpha(220)
    tr = img.get_rect(center=(cx, cy))
    surf.blit(sh_img, (tr.x + 1, tr.y + 1))
    surf.blit(img, tr)

    return pygame.Rect(x, y, pw, ph)


def _dark_panel(surf, rect, radius=16, alpha=210):
    """Deep-navy panel with a thin gold trim, a gold accent rail just
    under the top edge and a soft drop shadow — the canonical Pip
    Scarlet card treatment shared by every menu / overlay screen.
    Visual reference: tools/gen_scarlet_set.py::card."""
    # Drop shadow under the card.
    sh = pygame.Surface((rect.width + 4, rect.height + 4), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 90),
                     (0, 0, rect.width + 4, rect.height + 4),
                     border_radius=radius)
    surf.blit(sh, (rect.x - 2, rect.y + 4))

    # Body + thin gold border.
    pnl = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(pnl, (*_PANEL_DARK, alpha),
                     (0, 0, rect.width, rect.height),
                     border_radius=radius)
    pygame.draw.rect(pnl, (*_GOLD_BRIGHT, 130),
                     (0, 0, rect.width, rect.height),
                     width=1, border_radius=radius)

    # Gold accent rail just inside the top.
    inset = max(radius - 2, 6)
    rail_w = max(rect.width - inset * 2, 0)
    if rail_w > 0:
        accent = pygame.Surface((rail_w, 2), pygame.SRCALPHA)
        accent.fill((*_GOLD_BRIGHT, 110))
        pnl.blit(accent, (inset, 4))
        pygame.draw.line(pnl, (255, 220, 140, 90),
                         (inset, 2),
                         (rect.width - inset, 2), 1)
    surf.blit(pnl, rect.topleft)


def _volume_panel(surf, rect, radius=14, alpha=235):
    """Heavier emboss treatment for menu stat panels — gradient body
    (_PANEL_LIGHTER → _PANEL_DARK), 2 px gold border, inner top sheen
    + bottom shadow, and a 4-step drop shadow. Used by ``draw_menu`` for
    the BEST + TOP 10 cards so they sit with real volume against the
    scarlet pill buttons above them."""
    # 4-step drop shadow — softer, more diffuse than _dark_panel's.
    sh = pygame.Surface((rect.width + 8, rect.height + 8), pygame.SRCALPHA)
    for k in range(4):
        a = 80 - k * 16
        pygame.draw.rect(sh, (0, 0, 0, a),
                         (k, k * 2, rect.width + 8 - k * 2,
                          rect.height + 8 - k * 2),
                         border_radius=radius)
    surf.blit(sh, (rect.x - 4, rect.y + 2))

    # Gradient body — lighter at top, dark at bottom, fixed alpha.
    pnl = pygame.Surface(rect.size, pygame.SRCALPHA)
    for yy in range(rect.height):
        t = yy / max(1, rect.height - 1)
        r = int(_PANEL_LIGHTER[0] * (1 - t) + _PANEL_DARK[0] * t)
        g = int(_PANEL_LIGHTER[1] * (1 - t) + _PANEL_DARK[1] * t)
        b = int(_PANEL_LIGHTER[2] * (1 - t) + _PANEL_DARK[2] * t)
        pygame.draw.line(pnl, (r, g, b, alpha),
                         (0, yy), (rect.width - 1, yy))
    # Clip to a rounded-rect mask.
    mask = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255),
                     (0, 0, rect.width, rect.height), border_radius=radius)
    pnl.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    # 2 px gold border + inner top sheen + inner bottom shadow.
    pygame.draw.rect(pnl, _GOLD_BRIGHT, (0, 0, rect.width, rect.height),
                     width=2, border_radius=radius)
    pygame.draw.line(pnl, (*_GOLD_PALE, 140),
                     (10, 3), (rect.width - 10, 3), 1)
    pygame.draw.line(pnl, (0, 0, 0, 80),
                     (10, rect.height - 4),
                     (rect.width - 10, rect.height - 4), 1)
    surf.blit(pnl, rect.topleft)


def _draw_overlay_stars(surf, stars, t):
    """Twinkle star field. `stars` = list of (x,y,r,phase) from HUD.__init__."""
    for x, y, r, phase in stars:
        a = int(30 + 200 * (0.5 + 0.5 * math.sin(t * 1.4 + phase)))
        s = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 255, 255, a), (r + 1, r + 1), r)
        surf.blit(s, (x - r - 1, y - r - 1))


# ── Top-10 #1 crown sprite + medal-row gradient helpers ─────────────────────
# Procedural narrow-E3 ("Diamond Trio") crown that perches on the rank-1 row's
# gold badge. Sprite is built once, then cached + blit each frame.

_CROWN_OS = 2  # oversample factor — drawn at 2× target then smoothscaled

_CROWN_GOLD_HI    = (255, 232, 132)
_CROWN_GOLD       = (240, 192,  64)
_CROWN_GOLD_LO    = (188, 138,  28)
_CROWN_GOLD_DEEP  = (110,  72,   8)
_CROWN_OUTLINE    = ( 28,  18,   4)
_CROWN_RUBY       = (220,  40,  50)
_CROWN_RUBY_HI    = (255, 180, 190)
_CROWN_SAPPHIRE   = ( 64, 102, 220)
_CROWN_SAPPHIRE_HI= (172, 200, 255)
_CROWN_WHITE_HI   = (255, 255, 255)
_CROWN_PEARL      = (240, 232, 215)   # warm off-white gem face
_CROWN_PEARL_HI   = (255, 248, 230)   # bright highlight on the pearl gem

# Medal-row vertical gradients used on ranks 1, 2, 3 in draw_leaderboard
_MEDAL_GRADIENTS = {
    1: ((240, 192,  64), (180, 130,  20)),     # gold
    2: ((215, 222, 232), (110, 125, 145)),     # silver
    3: ((215, 150,  85), (125,  74,  28)),     # bronze
}


def _crown_aura(surf, cx, cy, radii, alphas):
    """Soft concentric golden halo behind the crown."""
    for r, a in zip(radii, alphas):
        glow = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.ellipse(glow,
                            (_CROWN_GOLD[0], _CROWN_GOLD[1],
                             _CROWN_GOLD[2], a),
                            (0, 0, r * 2, r * 2))
        surf.blit(glow, (cx - r, cy - r))


def _crown_band(big, s, l, top, r, bot):
    """Gold-gradient band with NEAR_BLACK perimeter outline."""
    pygame.draw.rect(big, _CROWN_OUTLINE,
                     (l - 1, top + s, r - l + 2, bot - top),
                     border_radius=s)
    h = bot - top
    for yy in range(h):
        u = yy / max(1, h - 1)
        col = tuple(int(_CROWN_GOLD_HI[i] * (1 - u) + _CROWN_GOLD_LO[i] * u)
                    for i in range(3))
        pygame.draw.line(big, col + (255,),
                         (l, top + yy), (r - 1, top + yy))
    pygame.draw.rect(big, _CROWN_OUTLINE,
                     (l, top, r - l, bot - top),
                     border_radius=s, width=2 * s)


def _crown_sheen(big, s, band_top, band_bot, band_l, band_r):
    """Single GOLD_HI horizontal stripe ~25 % down the band — metallic glint."""
    y = band_top + (band_bot - band_top) // 4
    pygame.draw.line(big, _CROWN_GOLD_HI,
                     (band_l + 2 * s, y), (band_r - 2 * s, y),
                     max(1, s // 2))


def _crown_outlined_polygon(surf, pts, fill, hi=None):
    """Filled polygon with a NEAR_BLACK outline + optional highlight."""
    pygame.draw.polygon(surf, _CROWN_OUTLINE, pts, max(2, _CROWN_OS * 2))
    pygame.draw.polygon(surf, fill, pts)
    if hi is not None and len(pts) >= 3:
        mid = ((pts[0][0] + pts[1][0]) / 2,
               (pts[0][1] + pts[1][1]) / 2)
        pygame.draw.polygon(surf, hi, [pts[0], pts[1], mid])


def _crown_outlined_gem(surf, cx, cy, r, col, hi):
    """Round cabochon with NEAR_BLACK outline + white highlight."""
    pygame.draw.circle(surf, _CROWN_OUTLINE, (cx, cy + 1), r + 1)
    pygame.draw.circle(surf, col, (cx, cy), r)
    pygame.draw.circle(surf, hi,
                       (cx - max(1, r // 3), cy - max(1, r // 3)),
                       max(1, r // 2))
    pygame.draw.circle(surf, _CROWN_OUTLINE, (cx, cy), r,
                       max(1, _CROWN_OS // 2))


def _crown_with_shadow(img, offset=(2, 2), alpha=110):
    """Composite soft drop shadow under the crown sprite."""
    shadow = img.copy()
    shadow.fill((0, 0, 0), special_flags=pygame.BLEND_RGB_MULT)
    shadow.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
    composite = pygame.Surface(
        (img.get_width() + offset[0], img.get_height() + offset[1]),
        pygame.SRCALPHA)
    composite.blit(shadow, offset)
    composite.blit(img, (0, 0))
    return composite


def _crown_draw_e3_narrow(big, s):
    """Narrow Diamond Trio — 3 peaks with kite-cut sapphire/ruby/sapphire,
    aura behind, sparkles around. Sized for a 24 × 28 bbox so it tucks
    inside the rank-1 gold badge (radius 13)."""
    bw, bh = big.get_width(), big.get_height()
    cx = bw // 2

    _crown_aura(big, cx, bh - 9 * s,
                radii=[9 * s, 6 * s, 4 * s],
                alphas=[40, 65, 95])

    band_h = 6 * s
    band_top = bh - band_h
    band_bot = bh
    band_l = 1 * s
    band_r = bw - 1 * s
    _crown_band(big, s, band_l, band_top, band_r, band_bot)
    _crown_sheen(big, s, band_top, band_bot, band_l, band_r)

    band_cy = (band_top + band_bot) // 2
    _crown_outlined_gem(big, cx, band_cy, int(1.2 * s),
                        _CROWN_RUBY, _CROWN_RUBY_HI)

    # V4 tiered: 3 tall vertical main peaks + 2 shorter outer peaks
    # leaning outward. Gem palette: ruby on the three centre peaks,
    # sapphire on the two outer leaning peaks. Sits inside the original
    # 24×28 bbox so the crown stays the same width as before.
    full_peak_h  = bh - band_h - 5 * s
    short_peak_h = int(full_peak_h * 0.62)
    full_tip_y   = band_top - full_peak_h
    short_tip_y  = band_top - short_peak_h

    def _peak(base_x, tip_x, tip_y, base_pw, gem_half_w, gem_fill, gem_hi):
        l   = (base_x - base_pw, band_top)
        r   = (base_x + base_pw, band_top)
        tip = (tip_x, tip_y)
        _crown_outlined_polygon(big, [tip, l, r],
                                _CROWN_GOLD, _CROWN_GOLD_HI)
        gem_top   = (tip_x, tip_y - int(2.5 * s))
        gem_bot   = (tip_x, tip_y - int(0.3 * s))
        gem_left  = (tip_x - int(gem_half_w * s), tip_y - int(1.4 * s))
        gem_right = (tip_x + int(gem_half_w * s), tip_y - int(1.4 * s))
        _crown_outlined_polygon(big,
                                [gem_top, gem_right, gem_bot, gem_left],
                                gem_fill, gem_hi)
        pygame.draw.line(big, _CROWN_WHITE_HI,
                         (gem_top[0] - 1, gem_top[1] + 1),
                         (gem_top[0] - 1, gem_top[1] + int(1.5 * s)),
                         max(1, s // 2))

    # Gem pattern numbered left-to-right (1..5):
    #   1 sapphire — 2 pearl — 3 ruby — 4 pearl — 5 sapphire
    inner_gems = [
        (_CROWN_PEARL, _CROWN_PEARL_HI),   # peak 2 (left centre)
        (_CROWN_RUBY,  _CROWN_RUBY_HI),    # peak 3 (centre)
        (_CROWN_PEARL, _CROWN_PEARL_HI),   # peak 4 (right centre)
    ]
    # 3 tall vertical centre peaks
    for px, (fill, hi) in zip((cx - 6 * s, cx, cx + 6 * s), inner_gems):
        _peak(px, px, full_tip_y, max(2, int(1.4 * s)), 1.2, fill, hi)

    # 2 outer shorter peaks leaning outward — sapphire gems (peaks 1, 5)
    for sign in (-1, 1):
        base_x = cx + sign * 9 * s
        tip_x  = cx + sign * 11 * s
        _peak(base_x, tip_x, short_tip_y, max(2, int(1.0 * s)), 0.7,
              _CROWN_SAPPHIRE, _CROWN_SAPPHIRE_HI)

    # Tight sparkles around the bbox
    cx_pix = bw // 2
    cy_pix = bh // 2
    for x_frac, y_frac in [(-0.85, -0.55), (0.85, -0.55),
                            (-0.70,  0.25), (0.70,  0.25)]:
        sx = int(cx_pix + x_frac * (bw // 2))
        sy = int(cy_pix + y_frac * (bh // 2))
        sx = max(2, min(bw - 2, sx))
        sy = max(2, min(bh - 2, sy))
        pygame.draw.line(big, _CROWN_WHITE_HI,
                         (sx - int(1.5 * s), sy),
                         (sx + int(1.5 * s), sy),
                         max(1, s // 2))
        pygame.draw.line(big, _CROWN_WHITE_HI,
                         (sx, sy - int(1.5 * s)),
                         (sx, sy + int(1.5 * s)),
                         max(1, s // 2))


_CROWN_SPRITE_CACHE: "pygame.Surface | None" = None
_CROWN_HD_CACHE: "dict[int, pygame.Surface]" = {}


def _get_crown_sprite() -> "pygame.Surface":
    """Build the rank-1 crown sprite once, cache it. Identical every
    frame — no animation, no per-row state."""
    global _CROWN_SPRITE_CACHE
    if _CROWN_SPRITE_CACHE is None:
        bw, bh = 24, 28
        big = pygame.Surface((bw * _CROWN_OS, bh * _CROWN_OS),
                             pygame.SRCALPHA)
        _crown_draw_e3_narrow(big, _CROWN_OS)
        small = pygame.transform.smoothscale(big, (bw, bh))
        _CROWN_SPRITE_CACHE = _crown_with_shadow(small)
    return _CROWN_SPRITE_CACHE


def _get_crown_sprite_hd(S: int) -> "pygame.Surface":
    """HD crown sprite at S × native, cached per scale factor."""
    if S == 1:
        return _get_crown_sprite()
    cached = _CROWN_HD_CACHE.get(S)
    if cached is None:
        bw, bh = 24, 28
        os_factor = _CROWN_OS * S
        big = pygame.Surface((bw * os_factor, bh * os_factor),
                             pygame.SRCALPHA)
        _crown_draw_e3_narrow(big, os_factor)
        small = pygame.transform.smoothscale(big, (bw * S, bh * S))
        cached = _crown_with_shadow(small, offset=(2 * S, 2 * S))
        _CROWN_HD_CACHE[S] = cached
    return cached


def _medal_row_pill(card_w, row_h, row_radius, rank):
    """Render the gold/silver/bronze gradient pill surface for a top-3
    rank. Returns a SRCALPHA surface ready to blit at the row origin."""
    top_col, bot_col = _MEDAL_GRADIENTS[rank]
    pnl = pygame.Surface((card_w, row_h), pygame.SRCALPHA)
    for yy in range(row_h):
        u = yy / max(1, row_h - 1)
        r = int(top_col[0] * (1 - u) + bot_col[0] * u)
        g = int(top_col[1] * (1 - u) + bot_col[1] * u)
        b = int(top_col[2] * (1 - u) + bot_col[2] * u)
        pygame.draw.line(pnl, (r, g, b, 255), (0, yy), (card_w, yy))
    mask = pygame.Surface((card_w, row_h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255),
                     (0, 0, card_w, row_h),
                     border_radius=row_radius)
    pnl.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    pygame.draw.rect(pnl, NEAR_BLACK, (0, 0, card_w, row_h),
                     width=2, border_radius=row_radius)
    return pnl


def _draw_trophy(surf, cx, cy, size):
    """Gold procedural trophy icon. `size` is approximate half-height.
    Drawn fully symmetric about a vertical axis through (cx, cy):
      * Cup widths use the same ±half-width on left & right
      * Handles drawn on a temp surface and mirrored via transform.flip
      * Stem / base / foot use odd widths so they centre exactly
    All sub-element widths/thicknesses scale with ``size`` so the
    silhouette reads as a trophy (cup + handles + base) at any render
    scale — at retina S=2/3, hardcoded 2-3 px features would otherwise
    smoothscale into invisible threads.
    """
    s = int(round(size))
    # Scaled sub-element dimensions
    h_w           = max(5, s // 3)        # handle ear half-width
    arc_thickness = max(2, s // 6)        # handle stroke
    stem_w        = max(3, (s // 6) | 1)  # stem width — odd for centring
    rim_h         = max(1, s // 10)       # cup-rim highlight
    base_h        = max(3, s // 6)        # base height
    foot_h        = max(2, s // 9)        # foot pad height

    pad   = h_w + 2
    g_w   = (s + pad) * 2 + 1   # odd → exact centre column
    g_h   = s * 3 + 6
    g     = pygame.Surface((g_w, g_h), pygame.SRCALPHA)
    gx    = g_w // 2
    gy    = s + 2

    GOLD  = (240, 192,  64, 255)
    DARK  = (140,  90,   8, 255)
    WHITE = (255, 248, 200, 180)

    # ── Cup body — symmetric trapezoid (wider at top) ──────────────────────
    half_top = s
    half_bot = s - 3
    top_y = gy - s + 2
    bot_y = gy + 2
    cup_pts = [
        (gx - half_top, top_y),
        (gx + half_top, top_y),
        (gx + half_bot, bot_y),
        (gx - half_bot, bot_y),
    ]
    # Symmetric drop shadow — grow the silhouette down + on both sides
    cup_shadow = [
        (gx - half_top - 1, top_y + 1),
        (gx + half_top + 1, top_y + 1),
        (gx + half_bot + 1, bot_y + 1),
        (gx - half_bot - 1, bot_y + 1),
    ]
    pygame.draw.polygon(g, DARK, cup_shadow)
    pygame.draw.polygon(g, GOLD, cup_pts)
    # pygame.draw.polygon excludes the right/bottom boundary by convention,
    # which leaves a one-pixel gap on the right slope. Draw the slope as a
    # line explicitly so left/right edges are pixel-symmetric.
    pygame.draw.line(g, GOLD,
                     (gx + half_top, top_y),
                     (gx + half_bot, bot_y), 1)
    pygame.draw.line(g, WHITE,
                     (gx - half_top + 2, top_y + 1),
                     (gx + half_top - 2, top_y + 1), rim_h)

    # ── Handles — draw the left ear once, then horizontal-flip for right ──
    h_h  = max(4, s - 2)
    h_y  = top_y + 2
    ear  = pygame.Surface((h_w, h_h), pygame.SRCALPHA)
    # Left half of an ellipse — gives a nice C-shape opening right
    pygame.draw.arc(ear, GOLD, (0, 0, h_w * 2 - 1, h_h),
                    math.pi * 0.5, math.pi * 1.5, arc_thickness)
    # Mirror about the cup's vertical centre. Left ear ends at gx - half_top;
    # right ear starts at gx + half_top + 1 so the two ears occupy mirrored
    # column ranges.
    left_ear_x  = gx - half_top - h_w + 1
    right_ear_x = gx + half_top
    g.blit(ear, (left_ear_x, h_y))
    g.blit(pygame.transform.flip(ear, True, False),
           (right_ear_x, h_y))

    # ── Stem — odd width, exact centre ────────────────────────────────────
    stem_h  = s // 2
    stem_x  = gx - stem_w // 2
    pygame.draw.rect(g, DARK,  (stem_x - 1, bot_y + 1, stem_w + 2, stem_h + 1))
    pygame.draw.rect(g, GOLD,  (stem_x,     bot_y,     stem_w,     stem_h))

    # ── Base + foot — both odd-width so they centre exactly ───────────────
    base_w = (s - 1) * 2 + 1
    base_x = gx - base_w // 2
    base_y = bot_y + stem_h
    pygame.draw.rect(g, DARK,  (base_x - 1, base_y + 1, base_w + 2, base_h + 1))
    pygame.draw.rect(g, GOLD,  (base_x,     base_y,     base_w,     base_h))

    foot_w = base_w + 2
    foot_x = gx - foot_w // 2
    foot_y = base_y + base_h
    pygame.draw.rect(g, DARK,  (foot_x - 1, foot_y + 1, foot_w + 2, foot_h + 1))
    pygame.draw.rect(g, GOLD,  (foot_x,     foot_y,     foot_w,     foot_h))

    surf.blit(g, (cx - gx, cy - gy))


def _draw_mountain_silhouette(surf, alpha=200):
    """Mountain silhouettes at the bottom — matches the welcome-screen SVG."""
    mtn = pygame.Surface((W, H), pygame.SRCALPHA)
    far = [(0,H),(0,490),(60,420),(120,450),(200,375),(280,430),
           (360,360),(W,400),(W,H)]
    near= [(0,H),(0,530),(80,505),(160,520),(240,490),(320,510),(W,495),(W,H)]
    pygame.draw.polygon(mtn, (14, 26, 12, alpha), far)
    pygame.draw.polygon(mtn, (10, 18,  8, alpha), near)
    surf.blit(mtn, (0, 0))


# Vendored Liberation Sans (metric-compatible Arial replacement) so the
# browser/pygbag build doesn't depend on a system font that isn't there.
_FONT_DIR = os.path.join(os.path.dirname(__file__), "assets")
_FONT_BOLD = os.path.join(_FONT_DIR, "LiberationSans-Bold.ttf")
# LiberationSans-Regular.ttf used to live alongside Bold and back the
# `bold=False` path here, but only two call sites ever passed False
# (a stats-row caption + a name-entry placeholder) and visually they
# read fine in the Bold face. Shipping the Regular file added ~400 KB
# to the WASM bundle for no real gain, so the file was retired and
# `bold=False` now falls through to the Bold ttf.


def _font(size, bold=True):
    k = (size, True)
    f = _fonts.get(k)
    if f is None:
        f = pygame.font.Font(_FONT_BOLD, size)
        _fonts[k] = f
    return f


def _text(surf, txt, center, size=36, color=WHITE, shadow=True):
    f = _font(size, True)
    img = f.render(txt, True, color)
    r = img.get_rect(center=center)
    if shadow:
        sh = f.render(txt, True, NEAR_BLACK)
        sh.set_alpha(170)
        surf.blit(sh, (r.x + 2, r.y + 3))
    surf.blit(img, r.topleft)
    return r


def _coin_icon(surf, cx, cy, r=10):
    # Reuse the cached high-quality coin face from entities so the HUD pill
    # carries the same gradient + bold outline + embossed parrot + specular
    # highlight as the in-world coin.
    from game.entities import _get_coin_face
    face = _get_coin_face()
    target = pygame.transform.smoothscale(face, (r * 2 + 2, r * 2 + 2))
    rect = target.get_rect(center=(cx, cy))
    surf.blit(target, rect.topleft)


# ── Neon-Arcade HUD kit (E2 layout, menu-yellow accent) ──────────────────────
# Shipped from the gameplay-HUD design loop. The score/coins/pause sit on opaque
# softened cut-corner slate plates: an OPAQUE body is the hard value floor that
# keeps the readout legible over a bright-sky brown pillar AND at night — the
# legibility the old translucent pills never had. The accent is the menu's
# SKYBIT yellow (`_GOLD_BRIGHT`) so the HUD reads as one family with the title.
# The power-up timer is a recessed-track energy bar that drains yellow→amber;
# kept a horizontal meter in a dark cool track on purpose so it can never be
# misread as the round gold coin.
_SS = 4  # supersample factor — composite big, smoothscale down for crisp edges
_NA_PAD = 11  # padding baked around each cached plate so its soft glow can bleed

_NA_SLATE    = ( 40,  38,  36)   # warm slate plate body (opaque value floor)
_NA_SLATE_D  = ( 22,  18,  16)
_NA_ACCENT   = _GOLD_BRIGHT       # menu-text yellow: rim + glow + glyphs
_NA_WARM     = ( 96,  64,  36)   # faint sandstone wash low in the score plate
_ENERGY_FULL   = _GOLD_BRIGHT     # timer fill at full charge (yellow)
_ENERGY_FULL_D = (170, 120,  28)
_ENERGY_LOW    = (255, 168,  70)  # draining toward amber
_ENERGY_LOW_D  = (196,  96,  28)
# Timer-bar fill stops — the meter reads its remaining time by colour:
# green when full, yellow at the midpoint, red when nearly out. Each stop is
# a bright core + darker edge for the recessed-track vertical gradient.
_BAR_GREEN   = ( 70, 205,  95);  _BAR_GREEN_D  = ( 38, 140,  60)
_BAR_YELLOW  = (240, 205,  60);  _BAR_YELLOW_D = (180, 145,  30)
_BAR_RED     = (230,  60,  55);  _BAR_RED_D    = (165,  32,  32)

_na_plate_cache: dict = {}
_na_track_cache: dict = {}


def _ss_surf(w, h):
    return pygame.Surface((w * _SS, h * _SS), pygame.SRCALPHA)


def _blit_ss(dst, ss, x, y, w, h):
    dst.blit(pygame.transform.smoothscale(ss, (w, h)), (x, y))


def _vgrad_rounded_ss(surf, w, h, top, bot, radius, alpha=255):
    """Vertical gradient clipped to a rounded rect, drawn onto a SUPERSAMPLED
    `surf` whose pixel size is `_SS` × the given native `w`/`h`."""
    ow, oh, orad = w * _SS, h * _SS, radius * _SS
    body = pygame.Surface((ow, oh), pygame.SRCALPHA)
    for yy in range(oh):
        t = yy / max(1, oh - 1)
        c = lerp_color(top, bot, t)
        pygame.draw.line(body, (*c, alpha), (0, yy), (ow - 1, yy))
    mask = pygame.Surface((ow, oh), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, ow, oh),
                     border_radius=orad)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(body, (0, 0))


def _cut_pts(x, y, w, h, cut):
    """Cut-corner (octagon) outline. The corner faces are softened into a
    chamfer-with-fillet by intersecting with a rounded-rect mask in the plate
    builder, so the silhouette reads friendly-arcade rather than hard bezel."""
    return [
        (x + cut, y), (x + w - cut, y), (x + w, y + cut),
        (x + w, y + h - cut), (x + w - cut, y + h), (x + cut, y + h),
        (x, y + h - cut), (x, y + cut),
    ]


def _na_plate_build(w, h, cut, round_r, accent, top, bot, inner_warm, glow):
    pad = _NA_PAD
    out = pygame.Surface((w + pad * 2, h + pad * 2), pygame.SRCALPHA)
    if glow:
        gpts = _cut_pts(pad, pad, w, h, cut)
        for i in range(5, 0, -1):
            a = int(34 * i / 5 / 5)
            pygame.draw.polygon(out, (*accent, a), gpts, width=i)
    ow, oh = w * _SS, h * _SS
    sspts = [(round(px * _SS), round(py * _SS))
             for px, py in _cut_pts(0, 0, w, h, cut)]
    body = pygame.Surface((ow, oh), pygame.SRCALPHA)
    for yy in range(oh):
        t = yy / max(1, oh - 1)
        c = lerp_color(top, bot, t)
        if inner_warm is not None and t > 0.55:
            c = lerp_color(c, inner_warm, (t - 0.55) / 0.45 * 0.5)
        pygame.draw.line(body, (*c, 255), (0, yy), (ow, yy))
    mask = pygame.Surface((ow, oh), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), sspts)
    if round_r > 0:
        rr = pygame.Surface((ow, oh), pygame.SRCALPHA)
        pygame.draw.rect(rr, (255, 255, 255, 255), (0, 0, ow, oh),
                         border_radius=round_r * _SS)
        mask.blit(rr, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    ss = pygame.Surface((ow, oh), pygame.SRCALPHA)
    ss.blit(body, (0, 0))
    pygame.draw.polygon(ss, (*accent, 255), sspts, width=2 * _SS)
    hi = lerp_color(accent, UI_CREAM, 0.4)
    pygame.draw.line(ss, (*hi, 110), sspts[0], sspts[1], _SS)
    out.blit(pygame.transform.smoothscale(ss, (w, h)), (pad, pad))
    return out


def _na_plate(surf, rect, cut, round_r, accent=_NA_ACCENT,
              top=_NA_SLATE, bot=_NA_SLATE_D, inner_warm=None, glow=True):
    """Blit a (cached) cut-corner slate plate so its body fills `rect`; the
    baked soft glow bleeds into the `_NA_PAD` margin around it."""
    key = (rect.width, rect.height, cut, round_r, accent, top, bot,
           inner_warm, glow)
    out = _na_plate_cache.get(key)
    if out is None:
        out = _na_plate_build(rect.width, rect.height, cut, round_r, accent,
                              top, bot, inner_warm, glow)
        _na_plate_cache[key] = out
    surf.blit(out, (rect.x - _NA_PAD, rect.y - _NA_PAD))


def _na_track_bg(w, h, radius):
    key = (w, h, radius)
    out = _na_track_cache.get(key)
    if out is None:
        ss = _ss_surf(w, h)
        _vgrad_rounded_ss(ss, w, h, (20, 30, 38), (8, 14, 20), radius, alpha=245)
        pygame.draw.rect(ss, (*_NA_ACCENT, 150), (0, 0, w * _SS, h * _SS),
                         width=_SS, border_radius=radius * _SS)
        out = pygame.transform.smoothscale(ss, (w, h))
        _na_track_cache[key] = out
    return out


def _na_energy_bar(surf, rect, frac):
    """Recessed-track energy bar; fill drains green→yellow→red as time runs
    out. A horizontal meter in a dark cool track on purpose, so it never reads
    as a gold coin."""
    radius = rect.height // 2
    surf.blit(_na_track_bg(rect.width, rect.height, radius), (rect.x, rect.y))
    # Two-segment traffic-light map: green at full, through yellow at the
    # midpoint, to red as the meter empties.
    if frac >= 0.5:
        t = (frac - 0.5) / 0.5
        core = lerp_color(_BAR_YELLOW, _BAR_GREEN, t)
        edge = lerp_color(_BAR_YELLOW_D, _BAR_GREEN_D, t)
    else:
        t = frac / 0.5
        core = lerp_color(_BAR_RED, _BAR_YELLOW, t)
        edge = lerp_color(_BAR_RED_D, _BAR_YELLOW_D, t)
    inset = 4
    fillw = int((rect.width - inset * 2) * frac)
    fh = rect.height - inset * 2
    if fillw > 4:
        fill = _ss_surf(fillw, fh)
        _vgrad_rounded_ss(fill, fillw, fh, core, edge, max(1, fh // 2))
        pygame.draw.line(fill, (255, 255, 255, 170), (2 * _SS, 3 * _SS),
                         (fillw * _SS - 2 * _SS, 3 * _SS), _SS)
        _blit_ss(surf, fill, rect.x + inset, rect.y + inset, fillw, fh)


# ── Active-buff emblem family ────────────────────────────────────────────────
# Every active power-up shows a small emblem on the slate plate left of its
# timer bar. The whole set shares one visual language so the buff stack reads as
# a cohesive family: each emblem is supersampled then smoothscaled (crisp arcs
# + real gradient shading at the 32px HUD footprint), lit from one top-left key
# light, carries a uniform dark outline weight, and sits on one soft contact
# shadow. To stay faithful to what the player actually grabs, most kinds blit
# the REAL in-world pickup sprite (via powerup_help._powerup_icon, the same
# renderer the run-summary chips use). The two pickups that turn to mush at HUD
# size — the photographic KFC logo and the text-captioned rail ticket — get a
# purpose-built simplified emblem here, drawn in their in-world palette.

_EMB_OUTLINE = (28, 24, 38)
_EMB_OW = max(2, 3 * _SS // 2)  # ~1.5px at the 32px footprint


def _emb_lerp(a, b, t):
    return a + (b - a) * t


def _emb_mix(c1, c2, t):
    return (int(_emb_lerp(c1[0], c2[0], t)),
            int(_emb_lerp(c1[1], c2[1], t)),
            int(_emb_lerp(c1[2], c2[2], t)))


def _emb_shade(c, f):
    # f<1 darkens, f>1 lightens; clamps to byte range.
    return (max(0, min(255, int(c[0] * f))),
            max(0, min(255, int(c[1] * f))),
            max(0, min(255, int(c[2] * f))))


def _emb_raw(size):
    return pygame.Surface((size * _SS, size * _SS), pygame.SRCALPHA)


def _emb_vgrad_circle(surf, cx, cy, r, top, bottom):
    # Vertical gradient clipped to a circle — a top-lit sphere/disc at SS scale.
    if r <= 0:
        return
    grad = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    for y in range(r * 2):
        t = y / max(1, (r * 2 - 1))
        pygame.draw.line(grad, _emb_mix(top, bottom, t), (0, y), (r * 2, y))
    mask = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (r, r), r)
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(grad, (cx - r, cy - r))


def _emb_vgrad_mask(surf, mask_pts, y0, y1, top, bottom):
    """Vertical gradient clipped to an arbitrary polygon mask."""
    W_, H_ = surf.get_size()
    band = pygame.Surface((W_, H_), pygame.SRCALPHA)
    for y in range(max(0, y0), min(H_, y1)):
        t = (y - y0) / max(1, (y1 - y0))
        pygame.draw.line(band, _emb_mix(top, bottom, t), (0, y), (W_, y))
    mask = pygame.Surface((W_, H_), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), mask_pts)
    band.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(band, (0, 0))


def _emb_key_light(surf, cx, cy, r, strength=64):
    # One shared top-left specular bloom => one light direction across the set.
    if r <= 0:
        return
    hl = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    pygame.draw.circle(hl, (255, 255, 255, strength),
                       (int(r * 0.7), int(r * 0.62)), int(r * 0.55))
    hl = pygame.transform.smoothscale(hl, (r * 2, r * 2))
    mask = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (r, r), r)
    hl.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(hl, (cx - r, cy - r))


def _emb_contact_shadow(out, size):
    # Soft ellipse under the emblem grounds it on the plate — same for all ten.
    sh = pygame.Surface((size, size), pygame.SRCALPHA)
    w = int(size * 0.60)
    h = max(2, int(size * 0.15))
    cx = size // 2
    cy = int(size * 0.87)
    pygame.draw.ellipse(sh, (0, 0, 0, 55), (cx - w // 2, cy - h // 2, w, h))
    out.blit(sh, (0, 0))


def _emb_finish(size, ss):
    """Downsample the SS emblem onto a size×size surface over one contact
    shadow (drawn first so the emblem sits on top)."""
    out = pygame.Surface((size, size), pygame.SRCALPHA)
    _emb_contact_shadow(out, size)
    out.blit(pygame.transform.smoothscale(ss, (size, size)), (0, 0))
    return out


# Palette for the two purpose-built stand-in emblems (kfc + rail). The other
# eight kinds blit the real in-world sprite, so they need no palette here.
_EMB_PAL = {
    "kfc_red": (210, 38, 40), "kfc_red_d": (150, 22, 26),
    "kfc_white": (248, 244, 238), "drum_brown": (190, 122, 60),
    "drum_brown_d": (138, 80, 36), "bone": (245, 238, 224),
    # rail ticket palette, lifted from the in-world rail pickup (entities.py
    # _draw_rail_icon) so the emblem reads as the same sepia locomotive card.
    "rail_sepia": (228, 210, 170), "rail_sepia_d": (196, 176, 134),
    "rail_ink": (30, 25, 20), "rail_cream": (238, 225, 195),
    "rail_frame": (18, 14, 10),
}


def _emb_build_kfc(size):
    ss = _emb_raw(size)
    S = size * _SS
    cx = S // 2
    top_y = int(S * 0.42)
    bot_y = int(S * 0.82)
    half_top = int(S * 0.31)   # FLARED wide at the top (chicken bucket, not box)
    half_bot = int(S * 0.19)
    body = [(cx - half_top, top_y), (cx + half_top, top_y),
            (cx + half_bot, bot_y), (cx - half_bot, bot_y)]
    pygame.draw.polygon(ss, _EMB_PAL["kfc_white"], body)
    for i in range(3):
        t = (i + 0.5) / 3
        xt = _emb_lerp(cx - half_top, cx + half_top, t)
        xb = _emb_lerp(cx - half_bot, cx + half_bot, t)
        pygame.draw.line(ss, _EMB_PAL["kfc_red"], (xt, top_y), (xb, bot_y), int(S * 0.055))
    pygame.draw.polygon(ss, _EMB_OUTLINE, body, _EMB_OW)
    rim_top = top_y - int(S * 0.06)
    rrect = (cx - half_top, rim_top, half_top * 2, int(S * 0.12))
    pygame.draw.ellipse(ss, _EMB_PAL["kfc_red"], rrect)
    pygame.draw.ellipse(ss, _EMB_OUTLINE, rrect, _EMB_OW)
    # ONE drumstick OVERLAPPING the rim => "chicken IN bucket", not a stray dot.
    dx = cx + int(S * 0.05)
    lobe_r = int(S * 0.13)
    dy = rim_top - lobe_r + int(S * 0.05)
    _emb_vgrad_circle(ss, dx, dy, lobe_r, _emb_shade(_EMB_PAL["drum_brown"], 1.25),
                      _EMB_PAL["drum_brown_d"])
    pygame.draw.circle(ss, _EMB_OUTLINE, (dx, dy), lobe_r, _EMB_OW)
    pygame.draw.ellipse(ss, _EMB_OUTLINE, rrect, _EMB_OW)  # rim crosses behind lobe
    bx, by = dx + int(S * 0.05), dy - int(S * 0.11)
    pygame.draw.line(ss, _EMB_PAL["bone"], (dx, dy - int(lobe_r * 0.4)), (bx, by),
                     int(S * 0.05))
    pygame.draw.circle(ss, _EMB_PAL["bone"], (bx, by), max(2, int(S * 0.04)))
    pygame.draw.circle(ss, _EMB_OUTLINE, (bx, by), max(2, int(S * 0.04)),
                       max(2, _EMB_OW - 2))
    _emb_key_light(ss, dx, dy, lobe_r, 55)
    return _emb_finish(size, ss)


def _emb_build_rail(size):
    # Simplified sepia locomotive ticket — evokes the in-world rail pickup
    # (entities.py _draw_rail_icon: a sepia card stamped with a side-view steam
    # engine) without its "TRAIN" caption, which is illegible at HUD size.
    ss = _emb_raw(size)
    S = size * _SS
    # Sepia ticket card with a dark frame + engraved inner border.
    card = pygame.Rect(int(S * 0.10), int(S * 0.20), int(S * 0.80), int(S * 0.60))
    pygame.draw.rect(ss, _EMB_PAL["rail_frame"], card, border_radius=int(S * 0.06))
    inner = card.inflate(-int(S * 0.06), -int(S * 0.06))
    _emb_vgrad_mask(
        ss,
        [inner.topleft, inner.topright, inner.bottomright, inner.bottomleft],
        inner.top, inner.bottom,
        _emb_shade(_EMB_PAL["rail_sepia"], 1.05), _EMB_PAL["rail_sepia_d"])
    pygame.draw.rect(ss, _EMB_PAL["rail_cream"], inner.inflate(-int(S * 0.04),
                     -int(S * 0.04)), max(2, _EMB_OW - 1), border_radius=int(S * 0.04))
    # Side-view steam locomotive, ink-dark on the card.
    ink = _EMB_PAL["rail_ink"]
    base_y = int(S * 0.62)
    boiler = pygame.Rect(int(S * 0.26), int(S * 0.40), int(S * 0.42), int(S * 0.18))
    pygame.draw.rect(ss, ink, boiler, border_radius=int(S * 0.04))
    cab = pygame.Rect(int(S * 0.55), int(S * 0.32), int(S * 0.16), int(S * 0.20))
    pygame.draw.rect(ss, ink, cab, border_radius=int(S * 0.02))
    # Smokestack ahead of the boiler.
    pygame.draw.rect(ss, ink, (int(S * 0.30), int(S * 0.30),
                               int(S * 0.07), int(S * 0.12)))
    pygame.draw.rect(ss, ink, (int(S * 0.28), int(S * 0.28),
                               int(S * 0.11), int(S * 0.04)))
    # Cow-catcher wedge at the front.
    pygame.draw.polygon(ss, ink, [(int(S * 0.26), int(S * 0.50)),
                                  (int(S * 0.26), int(S * 0.58)),
                                  (int(S * 0.18), int(S * 0.58))])
    # Two spoked wheels on a connecting rod.
    wy = base_y
    for wx in (int(S * 0.34), int(S * 0.56)):
        pygame.draw.circle(ss, ink, (wx, wy), int(S * 0.09))
        pygame.draw.circle(ss, _EMB_PAL["rail_cream"], (wx, wy), int(S * 0.09),
                           max(2, _EMB_OW - 1))
        for ang in range(0, 360, 60):
            a = math.radians(ang)
            pygame.draw.line(ss, _EMB_PAL["rail_cream"], (wx, wy),
                             (wx + math.cos(a) * int(S * 0.07),
                              wy + math.sin(a) * int(S * 0.07)), max(1, _EMB_OW - 2))
        pygame.draw.circle(ss, ink, (wx, wy), max(2, int(S * 0.025)))
    pygame.draw.line(ss, ink, (int(S * 0.34), wy), (int(S * 0.56), wy),
                     max(2, _EMB_OW - 1))
    return _emb_finish(size, ss)


# kfc + rail get the purpose-built simplified emblems above; every other kind
# is rendered from its REAL in-world pickup sprite (see _get_buff_emblem).
_EMB_BUILDERS = {
    "kfc": _emb_build_kfc,
    "rail": _emb_build_rail,
}

# Kinds whose in-world pickup downscales cleanly are blitted verbatim from the
# real sprite so the HUD emblem always matches what the player grabbed.
_EMB_FROM_PICKUP = frozenset({
    "triple", "magnet", "megamagnet", "slowmo", "reverse", "ghost",
    "grow", "shrink",
})

# Emblems are static, so render each (kind, size) once and reuse the surface;
# both the supersampled custom draws and the PowerUp.draw() pickup render are
# far too heavy to run per frame.
_buff_emblem_cache: dict = {}
# Lazily bound to powerup_help._powerup_icon — that module imports from hud, so
# we defer the import to first use to dodge the import cycle (same pattern as
# draw_stats' run-summary chips).
_emb_powerup_icon = None


def _emb_from_pickup(kind, size):
    """Render the real in-world pickup sprite, scaled to fill the HUD plate."""
    global _emb_powerup_icon
    if _emb_powerup_icon is None:
        from game.powerup_help import _powerup_icon
        _emb_powerup_icon = _powerup_icon
    emb = pygame.Surface((size, size), pygame.SRCALPHA)
    # The pickups carry their own padding, so draw a touch larger than the plate
    # to match the visual weight of the run-summary chips (icon_size * 1.5).
    _emb_powerup_icon(emb, kind, size // 2, size // 2, int(size * 1.4))
    return emb


def _get_buff_emblem(kind, size):
    key = (kind, size)
    emb = _buff_emblem_cache.get(key)
    if emb is None:
        if kind in _EMB_FROM_PICKUP:
            emb = _emb_from_pickup(kind, size)
        else:
            builder = _EMB_BUILDERS.get(kind)
            if builder is None:
                return None
            emb = builder(size)
        _buff_emblem_cache[key] = emb
    return emb


def _draw_buff_icon(surf, rect, kind):
    """Emblem for an active buff, centered in ``rect`` and cached per
    (kind, size). Most kinds blit the real in-world pickup sprite so the HUD
    matches what the player grabbed; kfc + rail use a legible stand-in drawn
    in their in-world palette (see the module comment above)."""
    size = min(rect.width, rect.height)
    if size <= 0:
        return
    emb = _get_buff_emblem(kind, size)
    if emb is not None:
        surf.blit(emb, emb.get_rect(center=rect.center))


class PauseButton:
    # Cut-corner power tile, top-right — sized and cornered to match the coins
    # plate's INITIAL footprint at the opposite corner (68x38: its 1-digit
    # baseline; same corner kit), vertically aligned, so the two top chips read
    # as a matched pair. Fixed footprint on purpose: the coins plate auto-grows
    # with its digit count, but the pause tile never does. Inset 18 px from the
    # right edge for safe-area margin against notched / rounded web corners; the
    # yellow accent + glow keep it from reading as the quietest tile.
    TILE = pygame.Rect(W - 68 - 18, 14, 68, 38)

    def __init__(self):
        # Hit-test area is the tile generously inflated (~54 px target, well over
        # the 44 px minimum, and survives rounded/notched web-portrait corners);
        # the visible tile is smaller.
        self.rect = PauseButton.TILE.inflate(16, 16)
        self.hover = False

    def contains(self, pos):
        return self.rect.collidepoint(pos)

    def draw(self, surf, paused=False):
        tile = PauseButton.TILE
        _na_plate(surf, tile, cut=7, round_r=8, glow=True)
        cx, cy = tile.center
        if paused:
            pygame.draw.polygon(surf, _NA_ACCENT, [
                (cx - 5, cy - 7),
                (cx - 5, cy + 7),
                (cx + 6, cy),
            ])
        else:
            bw, bh, gap = 5, 17, 4
            for dx in (-gap - bw, gap):
                pygame.draw.rect(surf, _NA_ACCENT,
                                 (cx + dx, cy - bh // 2, bw, bh), border_radius=2)
                pygame.draw.rect(surf, lerp_color(_NA_ACCENT, UI_CREAM, 0.5),
                                 (cx + dx + 1, cy - bh // 2 + 1, max(1, bw - 3), 4))


class HelpButton:
    """Top-left "?" button on the menu. Click opens the power-ups
    explainer (STATE_POWERUPS). Mirrors PauseButton's panel styling so
    the two top-corner buttons feel like a consistent family."""
    def __init__(self):
        self.rect = pygame.Rect(12, 12, 44, 44)

    def contains(self, pos):
        return self.rect.collidepoint(pos)

    def draw(self, surf):
        rounded_rect(surf, self.rect, 10, _PANEL_DARK, 200)
        border = pygame.Surface((self.rect.width, self.rect.height),
                                pygame.SRCALPHA)
        pygame.draw.rect(border, (*_ORANGE_BORDER, 120),
                         (0, 0, self.rect.width, self.rect.height),
                         border_radius=10, width=1)
        surf.blit(border, self.rect.topleft)
        cx, cy = self.rect.center
        # Bold gold "?" with a soft shadow.
        f = _font(28, True)
        sh = f.render("?", True, NEAR_BLACK)
        sh.set_alpha(150)
        surf.blit(sh, sh.get_rect(center=(cx + 1, cy + 2)))
        q = f.render("?", True, _GOLD_BRIGHT)
        surf.blit(q, q.get_rect(center=(cx, cy)))


# ── Run-summary helpers ──────────────────────────────────────────────────────

def _outline_pill_btn(surf, center, text, size=14, alpha=230,
                      min_width=120, pad_x=24, pad_y=12):
    """Secondary CTA — dark navy fill + gold border + gold text. Used
    for MAIN MENU under the primary PLAY AGAIN pill so the hierarchy
    reads cleanly. Returns the rect for hit-testing."""
    f = _font(size, True)
    img = f.render(text, True, _GOLD_BRIGHT)
    pw = max(min_width, img.get_width() + pad_x)
    ph = img.get_height() + pad_y
    cx, cy = center
    x = cx - pw // 2
    y = cy - ph // 2
    body = pygame.Surface((pw, ph), pygame.SRCALPHA)
    pygame.draw.rect(body, (*_PANEL_DARK, 200),
                     (0, 0, pw, ph), border_radius=ph // 2)
    pygame.draw.rect(body, _GOLD_BRIGHT, (0, 0, pw, ph),
                     width=2, border_radius=ph // 2)
    body.set_alpha(alpha)
    surf.blit(body, (x, y))
    surf.blit(img, img.get_rect(center=(cx, cy)))
    return pygame.Rect(x, y, pw, ph)


def _stat_tile_icon(surf, kind, cx, cy, size):
    """Stat-tile icon glyph. ``size`` is the half-extent in pixels.
    Supported kinds: ``time`` (clock face with hands), ``coin`` (real
    in-game coin face, capped at native display size), ``pillar``
    (small stone-column silhouette), ``flap`` (falcon wings pair)."""
    s = size
    if kind == "time":
        pygame.draw.circle(surf, _GOLD_BRIGHT, (cx, cy), s, 2)
        for ang in range(0, 360, 90):
            a = math.radians(ang - 90)
            x1 = cx + math.cos(a) * (s - 2)
            y1 = cy + math.sin(a) * (s - 2)
            x2 = cx + math.cos(a) * (s - 5)
            y2 = cy + math.sin(a) * (s - 5)
            pygame.draw.line(surf, _GOLD_BRIGHT, (x1, y1), (x2, y2), 1)
        ha = math.radians(45 - 90)
        ma = math.radians(160 - 90)
        pygame.draw.line(surf, _GOLD_BRIGHT, (cx, cy),
                         (cx + math.cos(ha) * s * 0.5,
                          cy + math.sin(ha) * s * 0.5), 2)
        pygame.draw.line(surf, _GOLD_BRIGHT, (cx, cy),
                         (cx + math.cos(ma) * s * 0.7,
                          cy + math.sin(ma) * s * 0.7), 2)
        pygame.draw.circle(surf, _GOLD_DEEP, (cx, cy), 2)
    elif kind == "coin":
        face = _ingame_coin_face()
        in_game_d = (COIN_R * 2 + 4)
        target_d = min(int(s * 2.6), in_game_d)
        scaled = pygame.transform.smoothscale(face, (target_d, target_d))
        surf.blit(scaled, scaled.get_rect(center=(cx, cy)))
    elif kind == "pillar":
        w = int(s * 1.0)
        pygame.draw.rect(surf, _GOLD_BRIGHT,
                         (cx - w // 2, cy - s, w, s * 2),
                         border_radius=2)
        pygame.draw.rect(surf, _GOLD_DEEP,
                         (cx - w // 2, cy - s, w, s * 2),
                         width=1, border_radius=2)
        pygame.draw.rect(surf, _GOLD_BRIGHT,
                         (cx - w // 2 - 2, cy - s - 2, w + 4, 4),
                         border_radius=1)
        pygame.draw.rect(surf, _GOLD_DEEP,
                         (cx - w // 2 - 2, cy - s - 2, w + 4, 4),
                         width=1, border_radius=1)
    elif kind == "flap":
        # Falcon wings — slim swept-back pair, tile-tuned (chosen wing
        # variant from docs/run_summary_redesign/wing_options_r9.png).
        for sign in (-1, 1):
            wing_pts = [
                (cx + sign * s * 0.04, cy - s * 0.30),
                (cx + sign * s * 0.30, cy - s * 0.60),
                (cx + sign * s * 0.80, cy - s * 0.62),
                (cx + sign * s * 1.20, cy - s * 0.18),
                (cx + sign * s * 1.35, cy + s * 0.10),
                (cx + sign * s * 1.05, cy + s * 0.20),
                (cx + sign * s * 0.95, cy + s * 0.50),
                (cx + sign * s * 0.65, cy + s * 0.25),
                (cx + sign * s * 0.45, cy + s * 0.35),
                (cx + sign * s * 0.22, cy + s * 0.12),
                (cx + sign * s * 0.04, cy + s * 0.00),
            ]
            pygame.draw.polygon(surf, _GOLD_BRIGHT, wing_pts)
            pygame.draw.polygon(surf, _GOLD_DEEP, wing_pts, 1)
            for sf, tf in [((0.20, -0.42), (1.30, 0.05)),
                           ((0.25, -0.32), (1.05, 0.18)),
                           ((0.30, -0.15), (0.85, 0.40)),
                           ((0.35, -0.00), (0.60, 0.25))]:
                pygame.draw.line(
                    surf, _GOLD_DEEP,
                    (cx + sign * sf[0] * s, cy + sf[1] * s),
                    (cx + sign * tf[0] * s, cy + tf[1] * s), 1)


def _stat_tile_chunky(surf, rect, icon_kind, value, label, subline=None):
    """Single stat tile — beveled navy card with gradient body, gold
    rim, icon at top, large value, optional subline ("61%"), bottom
    label. Auto-shrinks the label one step if it would crowd."""
    # Body — vertical gradient
    body = pygame.Surface(rect.size, pygame.SRCALPHA)
    for yy in range(rect.h):
        t = yy / max(1, rect.h - 1)
        c = lerp_color(_PANEL_LIGHTER, _PANEL_DARK, t)
        pygame.draw.line(body, (*c, 245), (0, yy), (rect.w, yy))
    mask = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255),
                     (0, 0, rect.w, rect.h), border_radius=10)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    pygame.draw.rect(body, (*_GOLD_BRIGHT, 160), (0, 0, rect.w, rect.h),
                     width=1, border_radius=10)
    pygame.draw.line(body, (*_GOLD_PALE, 100),
                     (10, 3), (rect.w - 10, 3), 1)
    surf.blit(body, rect.topleft)
    # Icon
    _stat_tile_icon(surf, icon_kind, rect.centerx, rect.y + 22, size=15)
    # Value
    vf = _font(26, True).render(str(value), True, _GOLD_BRIGHT)
    vs = _font(26, True).render(str(value), True, NEAR_BLACK)
    vs.set_alpha(170)
    vy = rect.y + 52 if subline else rect.y + 58
    vr = vf.get_rect(center=(rect.centerx, vy))
    surf.blit(vs, (vr.x + 1, vr.y + 2))
    surf.blit(vf, vr)
    # Optional subline — bumped from 11pt muted to 13pt bright gold
    # with a near-black shadow so the COINS percentage reads at a
    # glance instead of fading into the tile shading.
    if subline:
        sf = _font(13, True).render(subline, True, _GOLD_BRIGHT)
        ss = _font(13, True).render(subline, True, NEAR_BLACK)
        ss.set_alpha(200)
        sub_center = (rect.centerx, rect.y + 76)
        sr = sf.get_rect(center=sub_center)
        surf.blit(ss, (sr.x + 1, sr.y + 2))
        surf.blit(sf, sr)
    # Label — auto-shrink for the longer captions
    max_label_w = rect.w - 10
    lbl_size = 12
    lf = _font(lbl_size, True).render(label, True, _GOLD_MUTED)
    while lf.get_width() > max_label_w and lbl_size > 10:
        lbl_size -= 1
        lf = _font(lbl_size, True).render(label, True, _GOLD_MUTED)
    lf.set_alpha(230)
    surf.blit(lf, lf.get_rect(center=(rect.centerx, rect.y + rect.h - 12)))


def _score_plaque(surf, rect, score: int, best: int, new_best: bool):
    """Engraved gold-frame plaque with FINAL SCORE caption, massive
    inset score numeral, and a BEST/delta line at the bottom."""
    # Outer gold frame
    pygame.draw.rect(surf, _GOLD_BRIGHT, rect, border_radius=20)
    # Inner darker bevel
    inner = rect.inflate(-8, -8)
    pygame.draw.rect(surf, _GOLD_DEEP, inner, border_radius=16)
    # Engraved face — gradient
    face = inner.inflate(-6, -6)
    grad = pygame.Surface(face.size, pygame.SRCALPHA)
    for yy in range(face.h):
        t = yy / max(1, face.h - 1)
        c = lerp_color(_PANEL_LIGHTER, _NIGHT_DEEP, t)
        pygame.draw.line(grad, (*c, 255), (0, yy), (face.w, yy))
    mask = pygame.Surface(face.size, pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255),
                     (0, 0, face.w, face.h), border_radius=12)
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(grad, face.topleft)
    # Radial light hint upper-left of face
    glow = pygame.Surface(face.size, pygame.SRCALPHA)
    for rr in range(int(face.w * 0.6), 0, -2):
        a = int(18 * (1 - rr / (face.w * 0.6)))
        pygame.draw.circle(glow, (255, 220, 140, a),
                           (int(face.w * 0.35), int(face.h * 0.25)), rr)
    glow.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(glow, face.topleft)
    # FINAL SCORE caption
    sc = _font(15, True).render("F I N A L   S C O R E", True, _GOLD_MUTED)
    sc.set_alpha(230)
    surf.blit(sc, sc.get_rect(center=(rect.centerx, rect.y + 26)))
    # Massive engraved number
    big_num = str(score)
    nf = _font(88, True).render(big_num, True, _GOLD_BRIGHT)
    no = _font(88, True).render(big_num, True, _RED_OUTLINE)
    nsh = _font(88, True).render(big_num, True, NEAR_BLACK)
    deep_inner = _font(88, True).render(big_num, True, _GOLD_DEEP)
    nr = nf.get_rect(center=(rect.centerx, rect.centery + 4))
    px = 4
    for ox in (-px, 0, px):
        for oy in (-px, 0, px):
            if ox or oy:
                surf.blit(no, (nr.x + ox, nr.y + oy))
    nsh.set_alpha(180)
    surf.blit(nsh, (nr.x + 4, nr.y + 6))
    deep_inner.set_alpha(180)
    surf.blit(deep_inner, (nr.x - 1, nr.y - 1))
    surf.blit(nf, nr)
    # Best/delta line
    delta = score - best
    if new_best:
        cmp_text = f"NEW BEST  +{abs(delta)}"
        cmp_color = _GOLD_BRIGHT
    else:
        cmp_text = f"BEST {best}    {delta:+d}"
        cmp_color = _GOLD_MUTED
    cf = _font(13, True).render(cmp_text, True, cmp_color)
    cf.set_alpha(230)
    surf.blit(cf, cf.get_rect(center=(rect.centerx, rect.bottom - 20)))


class HUD:
    def __init__(self):
        self.pause_btn = PauseButton()
        self.help_btn = HelpButton()
        self.title_t = 0.0
        # Cached leaderboard layout (static parts). Rebuilt only when
        # scores / rank / error / pending / target size change.
        self._lb_cache: "pygame.Surface | None" = None
        self._lb_cache_key: tuple = ()
        # Name-entry button rects — populated each frame by draw_name_entry,
        # read by scenes.py click-handling. Pre-init to empty rects so the
        # first click before any draw is harmless.
        self.name_submit_rect = pygame.Rect(0, 0, 0, 0)
        self.name_skip_rect   = pygame.Rect(0, 0, 0, 0)
        # Run-summary button rects — populated by draw_stats each frame
        # so the STATE_STATS click handler in scenes.py can hit-test
        # PLAY AGAIN vs MAIN MENU.
        self.stats_play_again_rect = pygame.Rect(0, 0, 0, 0)
        self.stats_main_menu_rect  = pygame.Rect(0, 0, 0, 0)
        # Precompute star positions for overlay screens (seeded for consistency)
        rng = random.Random(42)
        self._stars = [
            (rng.randint(8, W - 8), rng.randint(8, H - 180),
             rng.choice((1, 1, 1, 2)), rng.uniform(0, 6.28))
            for _ in range(38)
        ]
        # Menu pill hit-test rects — populated each frame by draw_menu, read
        # by scenes.py click-handling. Pre-init to None so a click that
        # arrives before the first menu render falls through harmlessly.
        self.menu_start_rect: "pygame.Rect | None" = None
        self.menu_howto_rect: "pygame.Rect | None" = None
        self.menu_powerups_rect: "pygame.Rect | None" = None
        self.menu_top10_rect: "pygame.Rect | None" = None

    def draw_pause_overlay(self, surf, score: int = 0):
        # Deep blue-purple dim. The current score and coins pills from
        # draw_play sit underneath and read through the dim — no dedicated
        # pause score panel.
        dim = pygame.Surface((W, H), pygame.SRCALPHA)
        dim.fill((6, 2, 28, 165))
        surf.blit(dim, (0, 0))

        # Title in the canonical gold-on-red run-summary treatment; only the
        # original size-pulse animation is dropped so it sits calm.
        cy = H // 2 + 30
        _outlined_text(surf, "PAUSED", (W // 2, cy), size=52, px=3)

        # Same flat dim-scarlet pill as the main-menu CTAs.
        _pill_btn(surf, (W // 2, cy + 72), "TAP TO GAME",
                  size=18, alpha=230, min_width=220, dim=True, shadow=False)

    def draw_menu(self, surf, dt, best: int):
        self.title_t += dt
        # Night-sky tint overlay
        dim = pygame.Surface((W, H), pygame.SRCALPHA)
        dim.fill((6, 1, 21, 110))
        surf.blit(dim, (0, 0))

        _draw_overlay_stars(surf, self._stars, self.title_t)

        # Mountain silhouette belongs to the background, drawn before the
        # foreground UI so the pill / BEST panel / help button sit cleanly
        # on top of it instead of being darkened by the alpha-180 layer.
        _draw_mountain_silhouette(surf, alpha=180)

        # Floating title — sits above the gameplay-opener post-house +
        # Pip composition (cottage top is at y≈208) so the text never
        # crosses the parrot.
        pulse = 1.0 + math.sin(self.title_t * 2.4) * 0.04
        float_y = int(7 * math.sin(self.title_t * 1.8))
        _outlined_text(surf, "SKYBIT", (W // 2, 126 + float_y),
                        size=int(72 * pulse), px=3)

        # Subtitle — same gold-on-red outline as SKYBIT, just smaller and
        # with a tighter pixel outline so it reads as a partner line.
        _outlined_text(surf, "POCKET  SKY  FLYER", (W // 2, 184),
                        size=22, px=2, shadow_offset=(2, 3))

        # Divider
        pygame.draw.line(surf, (*_ORANGE_BORDER, 120),
                         (W // 2 - 70, 208), (W // 2 + 70, 208), 1)

        # Three stacked pill buttons replace the single tap-to-play pill
        # and the corner `?` button. Centres are computed from each pill's
        # actual rendered height so the white space between buttons is
        # even regardless of font metrics; the block is anchored 14 px
        # above the BEST score panel so the bottom pill always clears it.
        def _pill_h(text: str, size: int) -> int:
            return _font(size, True).render(text, True, WHITE).get_height() + 22

        GAP = 12
        h_start = _pill_h("START", 22)
        h_howto = _pill_h("HOW TO PLAY", 18)
        h_power = _pill_h("POWER-UPS", 18)
        y_power = (H - 110) - 14 - h_power // 2
        y_howto = y_power - h_power // 2 - GAP - h_howto // 2
        y_start = y_howto - h_howto // 2 - GAP - h_start // 2

        btn_alpha = int(225 + math.sin(self.title_t * 3.6) * 30)
        # dim=True swaps the bright scarlet for the bordeaux variant so
        # the menu pills sit more quietly in the dark night-sky palette.
        self.menu_start_rect = _pill_btn(
            surf, (W // 2, y_start), "START",
            size=22, alpha=btn_alpha, min_width=220, primary=True, dim=True,
            shadow=False)
        self.menu_howto_rect = _pill_btn(
            surf, (W // 2, y_howto), "HOW TO PLAY",
            size=18, alpha=230, min_width=220, dim=True, shadow=False)
        self.menu_powerups_rect = _pill_btn(
            surf, (W // 2, y_power), "POWER-UPS",
            size=18, alpha=230, min_width=220, dim=True, shadow=False)

        # Twin panels at the bottom: BEST score (left) + TOP 10 trophy
        # (right). Same pill dimensions side-by-side so they read as a
        # pair. The trophy panel is the leaderboard hit-zone — scenes.py
        # routes taps that land inside ``self.menu_top10_rect`` to
        # STATE_LEADERBOARD.
        panel_w = 132
        gap = 8
        total_w = panel_w * 2 + gap
        left_x = (W - total_w) // 2
        cy = H - 86  # vertical centre (matches the previous BEST y)
        lf = _font(13, True)
        vf = _font(24, True)

        # BEST panel (left) — heavier emboss treatment via _volume_panel.
        best_cx = left_x + panel_w // 2
        best_rect = pygame.Rect(left_x, cy - 24, panel_w, 48)
        _volume_panel(surf, best_rect, radius=14)
        lbl = lf.render("B E S T", True, _GOLD_PALE)
        lbl.set_alpha(230)
        surf.blit(lbl, lbl.get_rect(center=(best_cx, cy - 12)))
        val = vf.render(str(best), True, _GOLD_BRIGHT)
        surf.blit(val, val.get_rect(center=(best_cx, cy + 9)))

        # TOP 10 panel (right) — same volume treatment, trophy glyph.
        top_cx = left_x + panel_w + gap + panel_w // 2
        top_rect = pygame.Rect(left_x + panel_w + gap, cy - 24, panel_w, 48)
        _volume_panel(surf, top_rect, radius=14)
        top_lbl = lf.render("T O P  10", True, _GOLD_PALE)
        top_lbl.set_alpha(230)
        surf.blit(top_lbl, top_lbl.get_rect(center=(top_cx, cy - 12)))
        _draw_trophy(surf, top_cx, cy + 6, 9)
        self.menu_top10_rect = top_rect

        # The corner `?` help button is intentionally not drawn here —
        # the POWER-UPS pill above replaces it. HelpButton class itself
        # remains in this file unused so it can be revived without churn
        # if ever needed.

    def draw_play(self, surf, world, best: int, paused: bool = False):
        # ── Score: opaque cut-corner slate plate (the value floor) with a
        # menu-yellow accent edge + soft glow and a faint sandstone wash low in
        # the body. The numerals use the `main` deployment's treatment — a cream
        # face over a 2px deep-gold rim and a soft drop (see _SCORE_FACE) — so
        # the score reads over a bright-sky brown pillar AND at night. Lifted to
        # y=42 to reclaim central-corridor space while staying clear of the
        # bird's ceiling band. Kept drawn while paused so the pause overlay
        # simply dims it.
        score_txt = str(world.score)
        sf = _font(46, True)
        # Key the (cached) plate by digit COUNT — a tabular sample width — so
        # the plate is rebuilt at most once per digit count, not per score.
        sw = max(sf.size("8" * len(score_txt))[0] + 54, 102)
        sp = pygame.Rect((W - sw) // 2, 42, sw, 56)
        _na_plate(surf, sp, cut=9, round_r=9, inner_warm=_NA_WARM, glow=True)
        cf = _font(48, True)
        face = cf.render(score_txt, True, _SCORE_FACE)
        rim  = cf.render(score_txt, True, _GOLD_DEEP)
        sh   = cf.render(score_txt, True, NEAR_BLACK)
        r = face.get_rect(center=sp.center)
        # Uniform 8-offset rim = a constant 2px gold contour around the cream.
        for ox, oy in ((-2, 0), (2, 0), (0, -2), (0, 2),
                       (-2, -2), (2, -2), (-2, 2), (2, 2)):
            surf.blit(rim, (r.x + ox, r.y + oy))
        sh.set_alpha(180)
        surf.blit(sh, (r.x + 2, r.y + 4))
        surf.blit(face, r.topleft)

        # ── Pill alpha fades when bird is near top
        bird_y = world.bird.y
        if bird_y >= 80:
            ui_alpha = 255
        elif bird_y <= 20:
            ui_alpha = 40
        else:
            ui_alpha = int(40 + 215 * (bird_y - 20) / 60)

        # ── Coins plate: same slate cut-corner kit at top-left, auto-grows with
        # count so triple-/quadruple-digit values don't clip. The plate + coin
        # icon + gold count are composited on one surface so the whole element
        # fades together as the bird nears the top edge.
        coin_text = f"x{world.coin_count}"
        cf2 = _font(20, True)
        cw = cf2.size("8" * len(coin_text))[0] + 46
        cp = pygame.Rect(12, 14, cw, 38)
        pad = _NA_PAD
        coin_surf = pygame.Surface((cw + pad * 2, 38 + pad * 2), pygame.SRCALPHA)
        _na_plate(coin_surf, pygame.Rect(pad, pad, cw, 38), cut=7, round_r=8,
                  glow=False)
        _coin_icon(coin_surf, pad + 19, pad + 19, 12)
        tw = cf2.size(coin_text)[0]
        _outlined_text(coin_surf, coin_text, (pad + 36 + tw // 2, pad + 19), 20,
                       fill=UI_GOLD, outline=NEAR_BLACK, px=2, shadow_offset=None)
        coin_surf.set_alpha(ui_alpha)
        surf.blit(coin_surf, (cp.x - pad, cp.y - pad))

        # Pause button
        self.pause_btn.draw(surf, paused=paused)

        # "Get ready" prompt while the pre-start freeze is active.
        if world.ready_t > 0:
            pulse = 0.5 + 0.5 * math.sin(self.title_t * 5)
            alpha = int(180 + 60 * pulse)
            font_big = _font(22, True)
            label = font_big.render("TAP TO FLY", True, WHITE)
            label.set_alpha(alpha)
            lr = label.get_rect(center=(W // 2, 340))
            # dark plate behind for legibility
            plate = pygame.Surface((lr.width + 36, lr.height + 18),
                                   pygame.SRCALPHA)
            pygame.draw.ellipse(plate, (0, 0, 20, 140), plate.get_rect())
            surf.blit(plate, (W // 2 - plate.get_width() // 2,
                              lr.y - 9))
            surf.blit(label, lr.topleft)

        # Active-buff timer bars — every active power-up gets its own
        # progress bar at the top of the screen with the buff's logo on the
        # left. Stacks vertically when multiple are active. Each bar's fill
        # shifts green → yellow → red as its time depletes, so remaining
        # duration reads at a glance from colour alone.
        active = []
        if world.triple_timer > 0:
            active.append(("triple", world.triple_timer, TRIPLE_DURATION))
        if world.magnet_timer > 0:
            active.append(("magnet", world.magnet_timer, MAGNET_DURATION))
        if getattr(world, "megamagnet_timer", 0) > 0:
            active.append(("megamagnet", world.megamagnet_timer, MEGAMAGNET_DURATION))
        if world.slowmo_timer > 0:
            active.append(("slowmo", world.slowmo_timer, SLOWMO_DURATION))
        if world.kfc_timer > 0:
            active.append(("kfc", world.kfc_timer, KFC_DURATION))
        if world.ghost_timer > 0:
            active.append(("ghost", world.ghost_timer, GHOST_DURATION))
        if world.grow_timer > 0:
            active.append(("grow", world.grow_timer, GROW_DURATION))
        if world.reverse_timer > 0:
            active.append(("reverse", world.reverse_timer, REVERSE_DURATION))
        if getattr(world, "shrink_timer", 0) > 0:
            active.append(("shrink", world.shrink_timer, SHRINK_DURATION))
        # Rail intentionally has NO HUD timer bar: it's pillar-budgeted
        # rather than seconds-budgeted, and the on-world track + cart
        # already show the remaining ride at a glance.
        # Lottery is one-shot — the slot-machine reveal overlay carries
        # the result feedback; no HUD bar needed.

        if active:
            icon_size = 32
            bar_w     = 132
            bar_h     = 18
            row_gap   = 8
            row_pitch = icon_size + row_gap
            row_w     = icon_size + 8 + bar_w
            base_x    = (W - row_w) // 2
            top_y     = 110

            for i, (kind, remain, total) in enumerate(active):
                y = top_y + i * row_pitch
                # Icon plate on the left — the slate kit plate with the WARM
                # energy accent so it reads as part of the timer, not the score.
                icon_rect = pygame.Rect(base_x, y, icon_size, icon_size)
                _na_plate(surf, icon_rect, cut=7, round_r=7,
                          accent=_ENERGY_FULL, glow=False)
                # Emblem fills the plate; its own padding + contact shadow give
                # the inset, so no inflate here (the silhouette sits ~24px).
                _draw_buff_icon(surf, icon_rect, kind)

                # Energy bar to the right (drains yellow→amber, recessed track).
                bx = icon_rect.right + 8
                by = y + (icon_size - bar_h) // 2
                frac = max(0.0, min(1.0, remain / total))
                bar = pygame.Rect(bx, by, bar_w, bar_h)
                _na_energy_bar(surf, bar, frac)
                _text(surf, f"{remain:.1f}s", (bar.centerx, bar.centery),
                      size=11, color=UI_CREAM, shadow=True)

        # Float texts
        for ft in world.float_texts:
            ft.draw(surf)

    def draw_stats(self, surf, world, dt, elapsed,
                   best: int = 0, new_best: bool = False,
                   show_prompt: bool = True):
        """Run-summary screen — Trophy Cinema layout. RUN SUMMARY title,
        engraved score plaque, 4 stat tiles (TIME · COINS+% · PILLARS ·
        FLAPS), compact power-up icon strip, PLAY AGAIN primary +
        MAIN MENU secondary buttons. ``show_prompt`` is kept for caller
        compatibility but no longer drives a tap-to-continue prompt —
        the buttons replace that affordance."""
        self.title_t += dt
        dim = pygame.Surface((W, H), pygame.SRCALPHA)
        dim.fill((*_NIGHT_DEEP, 190))
        surf.blit(dim, (0, 0))

        _draw_overlay_stars(surf, self._stars, self.title_t)
        _draw_mountain_silhouette(surf, alpha=160)

        # Title — canonical gold-on-red treatment, same family as SKYBIT
        _outlined_text(surf, "RUN  SUMMARY", (W // 2, 56),
                       size=34, px=3, shadow_offset=(3, 5))

        # Hero score plaque
        plaque = pygame.Rect(18, 104, W - 36, 156)
        _score_plaque(surf, plaque, world.score, best, new_best)

        # Stat tiles (TIME · COINS+% · PILLARS · FLAPS)
        mins = int(world.time_alive) // 60
        secs = int(world.time_alive) % 60
        time_str = f"{mins}:{secs:02d}" if mins else f"{secs}s"
        # "Coins encountered" = coins that left the player's reach.
        # Coins still on screen don't count as missed yet.
        coins_encountered = max(0, world.coins_spawned - len(world.coins))
        coins_pct = (round(world.coin_count / coins_encountered * 100)
                     if coins_encountered > 0 else None)
        coins_sub = f"{coins_pct}%" if coins_pct is not None else None
        tiles = [
            ("time",   time_str,                       "TIME",    None),
            ("coin",   str(world.coin_count),          "COINS",   coins_sub),
            ("pillar", str(world.pillars_passed),      "PILLARS", None),
            ("flap",   str(world.flap_count),          "FLAPS",   None),
        ]
        tile_w = 78
        # Tile height grew from 98 → 104 to give the bigger COINS-%
        # subline (now 13pt bright) breathing room above the label.
        tile_h = 104
        tile_gap = 8
        total_w = len(tiles) * tile_w + (len(tiles) - 1) * tile_gap
        start_x = (W - total_w) // 2
        tile_y = 282
        for i, (kind, val, lbl, sub) in enumerate(tiles):
            r = pygame.Rect(start_x + i * (tile_w + tile_gap), tile_y,
                            tile_w, tile_h)
            _stat_tile_chunky(surf, r, kind, val, lbl, subline=sub)

        # Power-ups row — Variant C "Horizontal Pills": each power-up
        # rendered as a navy gold-bordered chip with [icon | ×N] laid
        # out side-by-side. Strong text legibility and clear visual
        # separation between kinds. When more chips than will fit in
        # one row are picked (rare — 6+ distinct kinds in one run) we
        # wrap to two rows split evenly so the strip stays readable.
        pu = [(k, c) for k, c in world.powerups_picked.items() if c > 0]
        if pu:
            # Lazy import: game.powerup_help imports from game.hud, so
            # we defer this until the first stats-screen render.
            from game.powerup_help import (
                _powerup_icon as _ingame_powerup_icon,
            )
            cap_y = 414
            total_pu = sum(c for _, c in pu)
            # _font already returns the bold face, so toggling bold there
            # is a no-op; set_bold adds synthetic weight on top so the
            # caption reads clearly heavier. Unset right after to leave the
            # cached font untouched for other callers.
            cf = _font(18, True)
            cf.set_bold(True)
            cap = cf.render(
                f"{total_pu}  POWER-UPS USED",
                True, _GOLD_MUTED)
            cf.set_bold(False)
            cap.set_alpha(230)
            surf.blit(cap, cap.get_rect(center=(W // 2, cap_y)))

            chip_h = 40
            icon_size = 30
            chip_radius = chip_h // 2
            pad_l, pad_r = 3, 8
            count_font = _font(16, True)
            chips = []
            for kind, count in pu:
                tf = count_font.render(f"×{count}", True, _GOLD_BRIGHT)
                chip_w = pad_l + icon_size + 2 + tf.get_width() + pad_r
                chips.append((kind, count, chip_w, tf))

            gap = 5
            available = W - 10
            total = sum(c[2] for c in chips) + gap * (len(chips) - 1)
            if total <= available:
                rows = [chips]
                first_row_y = cap_y + 38
            else:
                # Split into two roughly even rows.
                half = (len(chips) + 1) // 2
                rows = [chips[:half], chips[half:]]
                first_row_y = cap_y + 30

            for ri, row_chips in enumerate(rows):
                row_total = (sum(c[2] for c in row_chips)
                             + gap * (len(row_chips) - 1))
                sx = (W - row_total) // 2
                y = first_row_y + ri * (chip_h + 8)
                for kind, count, chip_w, tf in row_chips:
                    # Render the chip body at 2× then smoothscale down so
                    # the rounded corners + gold border are anti-aliased
                    # instead of pixel-stepped.
                    OS = 2
                    ow, oh = chip_w * OS, chip_h * OS
                    o_radius = chip_radius * OS
                    body_big = pygame.Surface((ow, oh), pygame.SRCALPHA)
                    for yy in range(oh):
                        t = yy / max(1, oh - 1)
                        c = lerp_color(_PANEL_LIGHTER, _PANEL_DARK, t)
                        pygame.draw.line(body_big, (*c, 245),
                                         (0, yy), (ow, yy))
                    mask_big = pygame.Surface((ow, oh), pygame.SRCALPHA)
                    pygame.draw.rect(mask_big, (255, 255, 255, 255),
                                     (0, 0, ow, oh),
                                     border_radius=o_radius)
                    body_big.blit(mask_big, (0, 0),
                                  special_flags=pygame.BLEND_RGBA_MIN)
                    pygame.draw.rect(body_big, _GOLD_BRIGHT,
                                     (0, 0, ow, oh),
                                     width=2 * OS, border_radius=o_radius)
                    body = pygame.transform.smoothscale(body_big,
                                                       (chip_w, chip_h))
                    surf.blit(body, (sx, y - chip_h // 2))
                    _ingame_powerup_icon(
                        surf, kind,
                        sx + pad_l + icon_size // 2 + 2, y,
                        int(icon_size * 1.5))
                    surf.blit(tf, tf.get_rect(
                        midright=(sx + chip_w - pad_r, y)))
                    sx += chip_w + gap

        # Buttons — PLAY AGAIN primary, MAIN MENU secondary.
        # Hide button hit rects until the 0.6s reveal gate has elapsed
        # (matches the previous "tap to continue" debounce window so a
        # stray tap from the death event doesn't immediately fire).
        if elapsed >= 0.6:
            self.stats_play_again_rect = _pill_btn(
                surf, (W // 2, 568), "PLAY  AGAIN",
                size=22, alpha=255, min_width=240, primary=True, dim=True,
                shadow=False)
            self.stats_main_menu_rect = _outline_pill_btn(
                surf, (W // 2, 618), "MAIN MENU",
                size=14, min_width=130)
        else:
            self.stats_play_again_rect = pygame.Rect(0, 0, 0, 0)
            self.stats_main_menu_rect = pygame.Rect(0, 0, 0, 0)

    def draw_name_entry(self, surf, dt, buf: str):
        self.title_t += dt
        dim = pygame.Surface((W, H), pygame.SRCALPHA)
        dim.fill((8, 3, 26, 240))
        surf.blit(dim, (0, 0))

        _draw_overlay_stars(surf, self._stars, self.title_t)

        # Trophy above the title — same emblem as the TOP 10 screen.
        _draw_trophy(surf, W // 2, H // 2 - 180, 22)

        # Title — gold + red outline to match the mockup
        _outlined_text(surf, "NEW  HIGH  SCORE!",
                       (W // 2, H // 2 - 130),
                       size=24, px=2, shadow_offset=(2, 3))

        # Divider line under the title (mockup convention).
        pygame.draw.line(surf, (*_GOLD_BRIGHT, 130),
                         (W // 2 - 50, H // 2 - 108),
                         (W // 2 + 50, H // 2 - 108), 1)

        # Engraved nameplate (gold rim + corner rivets + dark navy face)
        # in place of the plain orange-bordered input field.
        fw, fh = 284, 54
        fx, fy = W // 2 - fw // 2, H // 2 - 70
        plate_rect = pygame.Rect(fx, fy, fw, fh)
        pygame.draw.rect(surf, _GOLD_BRIGHT, plate_rect, border_radius=8)
        inner = plate_rect.inflate(-6, -6)
        pygame.draw.rect(surf, _PANEL_DARK, inner, border_radius=6)
        pygame.draw.rect(surf, _GOLD_DEEP, plate_rect,
                         width=2, border_radius=8)
        # Subtle cream highlight just inside the top edge.
        pygame.draw.line(surf, (255, 240, 180),
                         (plate_rect.x + 10, plate_rect.y + 3),
                         (plate_rect.right - 10, plate_rect.y + 3), 1)
        # Four corner rivets.
        for rx, ry in (
            (plate_rect.x + 8, plate_rect.y + 8),
            (plate_rect.right - 8, plate_rect.y + 8),
            (plate_rect.x + 8, plate_rect.bottom - 8),
            (plate_rect.right - 8, plate_rect.bottom - 8),
        ):
            pygame.draw.circle(surf, _GOLD_DEEP, (rx, ry), 3)
            pygame.draw.circle(surf, _GOLD_BRIGHT, (rx, ry), 3, 1)
            pygame.draw.circle(surf, (255, 240, 180), (rx - 1, ry - 1), 1)

        # Typed text — gold with a soft black drop shadow, no cursor.
        tf = _font(26, True)
        if buf:
            sh = tf.render(buf, True, NEAR_BLACK)
            sh.set_alpha(180)
            txt = tf.render(buf, True, _GOLD_BRIGHT)
            tr = txt.get_rect(center=(W // 2, fy + fh // 2))
            surf.blit(sh, (tr.x + 1, tr.y + 2))
            surf.blit(txt, tr)
        else:
            placeholder = _font(18, False).render("TYPE YOUR NAME…",
                                                  True, _GOLD_MUTED)
            placeholder.set_alpha(100)
            surf.blit(placeholder,
                      placeholder.get_rect(center=(W // 2, fy + fh // 2)))

        # Mountain silhouette belongs to the backdrop — drawn before the
        # buttons so SUBMIT / SKIP sit on top of any scenery, never behind it.
        _draw_mountain_silhouette(surf, alpha=160)

        # Paired action buttons — SUBMIT promoted to the primary pill
        # so it carries the gold halo in the mockup.
        self.name_submit_rect = _pill_btn(
            surf, (W // 2, H // 2 + 34), "SUBMIT",
            size=18, alpha=255, min_width=200, primary=True)
        self.name_skip_rect = _pill_btn(
            surf, (W // 2, H // 2 + 92), "SKIP",
            size=18, alpha=255, min_width=200)

    def draw_leaderboard(self, surf, dt, scores: list, player_rank: int,
                         cooldown: float, fetch_error: str = ""):
        # Internally render at 3× supersample so the leaderboard's text
        # and circle edges come out clean on both desktop and mobile.
        # The whole static layout is cached (keyed on scores + rank +
        # error + target surface size); only the animated TAP TO MENU
        # prompt is re-rendered per frame.
        self.title_t += dt
        SCALE = 3
        target_w, target_h = surf.get_size()

        scores_key = tuple((e["name"], e["score"]) for e in scores)
        key = (target_w, target_h, scores_key, player_rank, fetch_error)

        if self._lb_cache_key != key:
            hd_w, hd_h = W * SCALE, H * SCALE
            hd = pygame.Surface((hd_w, hd_h), pygame.SRCALPHA)
            self._render_leaderboard(hd, scores, player_rank,
                                     fetch_error, SCALE)
            if (target_w, target_h) == (hd_w, hd_h):
                self._lb_cache = hd
            else:
                self._lb_cache = pygame.transform.smoothscale(
                    hd, (target_w, target_h))
            self._lb_cache_key = key

        surf.blit(self._lb_cache, (0, 0))

        # TAP TO MENU prompt — pulses every frame, so rendered live on
        # top of the cached static layout. Show whenever the user can
        # dismiss the view (cooldown elapsed) including during loading.
        if cooldown <= 0:
            out_scale = max(1, target_w // W)
            alpha = int(170 + math.sin(self.title_t * 4) * 70)
            f2 = _font(16 * out_scale, True)
            prompt = f2.render("TAP  TO  MENU", True, _GOLD_MUTED)
            prompt.set_alpha(alpha)
            pr = prompt.get_rect(center=(target_w // 2,
                                         target_h - 28 * out_scale))
            surf.blit(prompt, pr.topleft)

    def _render_leaderboard(self, surf, scores: list, player_rank: int,
                            fetch_error: str, S: int):
        """Static leaderboard layout (no TAP TO MENU prompt) at scale S.
        ``surf`` is sized ``(W*S, H*S)``; every coord, font size and
        stroke width is multiplied by ``S``."""
        Ws, Hs = W * S, H * S
        dim = pygame.Surface((Ws, Hs), pygame.SRCALPHA)
        dim.fill((0, 0, 20, 200))
        surf.blit(dim, (0, 0))

        # Header: trophy icon — "TOP 10" — trophy icon
        _outlined_text(surf, "TOP 10", (Ws // 2, 46 * S), size=32 * S,
                       px=3 * S, shadow_offset=(3 * S, 5 * S))
        for side in (-1, 1):
            tx = Ws // 2 + side * 88 * S
            ty = 46 * S
            _draw_trophy(surf, tx, ty, 18 * S)

        card_x, card_w = 14 * S, (W - 28) * S
        # Rows appear immediately at their settled position — the
        # slide-in-from-below animation was removed per design feedback.
        card_y = 88 * S

        n = len(scores)
        if n == 0:
            if fetch_error:
                _text(surf, "Top-10 unavailable",
                      (Ws // 2, card_y + 60 * S),
                      size=18 * S, color=UI_CREAM, shadow=True)
                _text(surf, "Check the browser console",
                      (Ws // 2, card_y + 94 * S),
                      size=12 * S, color=UI_CREAM, shadow=False)
                _text(surf, "(" + fetch_error + ")",
                      (Ws // 2, card_y + 116 * S),
                      size=11 * S, color=UI_CREAM, shadow=False)
            else:
                _text(surf, "No scores yet!",
                      (Ws // 2, card_y + 60 * S),
                      size=18 * S, color=UI_CREAM, shadow=True)
                _text(surf, "Be the first.",
                      (Ws // 2, card_y + 94 * S),
                      size=14 * S, color=UI_CREAM, shadow=False)
        else:
            row_h = 42 * S
            row_gap = 4 * S

            SILVER = (185, 195, 205)
            BRONZE = (185, 125,  55)

            f_badge = _font(13 * S, True)
            f_name  = _font(16 * S, True)
            f_you   = _font(10 * S, True)
            f_score = _font(17 * S, True)

            hd_crown = _get_crown_sprite_hd(S)

            ry = card_y
            for i, entry in enumerate(scores):
                rank = i + 1
                if rank == 1:    badge_col = _GOLD_BRIGHT
                elif rank == 2:  badge_col = SILVER
                elif rank == 3:  badge_col = BRONZE
                else:            badge_col = _GOLD_BRIGHT

                is_player = (i == player_rank)
                row_cy = ry + row_h // 2
                is_medal = rank in _MEDAL_GRADIENTS

                row_rect = pygame.Rect(card_x, ry, card_w, row_h)
                row_radius = row_h // 2
                if is_medal:
                    pnl = _medal_row_pill(card_w, row_h, row_radius, rank)
                else:
                    pnl = pygame.Surface(row_rect.size, pygame.SRCALPHA)
                    pygame.draw.rect(pnl, (*_PANEL_DARK, 220),
                                     (0, 0, card_w, row_h),
                                     border_radius=row_radius)
                    if is_player:
                        pygame.draw.rect(pnl, _GOLD_BRIGHT,
                                         (0, 0, card_w, row_h),
                                         width=3 * S, border_radius=row_radius)
                    else:
                        pygame.draw.rect(pnl, (*_GOLD_BRIGHT, 110),
                                         (0, 0, card_w, row_h),
                                         width=1 * S, border_radius=row_radius)
                surf.blit(pnl, row_rect.topleft)

                badge_cx = card_x + 24 * S
                badge_r = 13 * S
                if rank <= 3:
                    pygame.draw.circle(surf, badge_col,
                                       (badge_cx, row_cy), badge_r)
                    pygame.draw.circle(surf, NEAR_BLACK,
                                       (badge_cx, row_cy), badge_r, 1 * S)
                    num_col = NEAR_BLACK
                else:
                    pygame.draw.circle(surf, badge_col,
                                       (badge_cx, row_cy), badge_r, 2 * S)
                    num_col = _GOLD_BRIGHT
                num_img = f_badge.render(str(rank), True, num_col)
                surf.blit(num_img,
                          num_img.get_rect(center=(badge_cx, row_cy)))

                if rank == 1:
                    c_w, c_h = hd_crown.get_size()
                    surf.blit(hd_crown,
                              (badge_cx - c_w // 2,
                               row_cy - 7 * S - c_h))

                nm = entry["name"][:10]
                if is_medal:
                    name_col = NEAR_BLACK
                else:
                    name_col = _GOLD_BRIGHT if is_player else WHITE
                nm_img = f_name.render(nm, True, name_col)
                nm_x = card_x + 44 * S
                surf.blit(nm_img,
                          (nm_x, row_cy - nm_img.get_height() // 2))

                if is_player:
                    you_img = f_you.render("YOU", True, WHITE)
                    pw = you_img.get_width() + 10 * S
                    ph = you_img.get_height() + 6 * S
                    pxr = nm_x + nm_img.get_width() + 7 * S
                    pyr = row_cy - ph // 2
                    you_pill = pygame.Surface((pw, ph), pygame.SRCALPHA)
                    pygame.draw.rect(you_pill, _SCARLET_TOP,
                                     (0, 0, pw, ph), border_radius=ph // 2)
                    pygame.draw.rect(you_pill, _GOLD_BRIGHT,
                                     (0, 0, pw, ph),
                                     width=1 * S, border_radius=ph // 2)
                    surf.blit(you_pill, (pxr, pyr))
                    surf.blit(you_img, (pxr + 5 * S, pyr + 3 * S))

                score_col = NEAR_BLACK if is_medal else _GOLD_BRIGHT
                sc_img = f_score.render(str(entry["score"]), True, score_col)
                surf.blit(sc_img,
                          (card_x + card_w - 16 * S - sc_img.get_width(),
                           row_cy - sc_img.get_height() // 2))

                ry += row_h + row_gap
