"""HUD: score, hi-score, coin count, power-up timer bar, pause button."""
import math
import os
import random
import pygame

from game.config import W, H, TRIPLE_DURATION, MAGNET_DURATION, SLOWMO_DURATION, KFC_DURATION, GHOST_DURATION, GROW_DURATION, REVERSE_DURATION
from game.draw import (
    rounded_rect, rounded_rect_grad, lerp_color,
    UI_SCORE, UI_GOLD, UI_ORANGE, UI_SHADOW, UI_CREAM, UI_RED,
    COIN_GOLD, COIN_DARK,
    WHITE, NEAR_BLACK,
)
from game import parrot
from game.dollar_coin_glyphs import draw_coin_font_bold as _draw_dollar_coin_hud

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
_SCARLET_SHADOW = ( 60,   8,   8)   # #3c0808  pill text shadow
_GOLD_DEEP      = (180, 130,  20)   # #b48214  inner laurel/ring tone
_PANEL_DARK     = ( 12,   8,  38)   # deep purple panel
_NIGHT_DEEP     = (  6,   1,  21)   # #060115


_fonts: dict = {}


# ── Theme drawing helpers ────────────────────────────────────────────────────

def _outlined_text(surf, txt, center, size, fill=_GOLD_BRIGHT,
                   outline=_RED_OUTLINE, px=3, shadow_offset=(3, 5)):
    """Gold text with red pixel outline — matches the welcome screen title."""
    f = _font(size, True)
    img = f.render(txt, True, fill)
    out = f.render(txt, True, outline)
    sh  = f.render(txt, True, NEAR_BLACK)
    r = img.get_rect(center=center)
    offsets = [(-px, 0), (px, 0), (0, -px), (0, px),
               (-px, -px), (px, -px), (-px, px), (px, px)]
    for ox, oy in offsets:
        surf.blit(out, (r.x + ox, r.y + oy))
    sh.set_alpha(170)
    surf.blit(sh, (r.x + shadow_offset[0], r.y + shadow_offset[1]))
    surf.blit(img, r.topleft)
    return r


def _pill_btn(surf, center, text, size=20, alpha=255, wide=False,
              min_width=None, primary=False):
    """Scarlet body + gold border + cream text, with drop shadow, top-half
    frosting, gold accent line and (optionally) a gold glow when
    ``primary=True`` — the canonical Pip Scarlet pill from the menu
    mockup (see tools/gen_scarlet_set.py::pill). Returns the rect so
    callers can hit-test clicks. ``min_width`` lets paired buttons
    (SUBMIT + SKIP) share one width regardless of label length."""
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
    sh = pygame.Surface((pw + 4, ph + 4), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 90),
                     (0, 0, pw + 4, ph + 4),
                     border_radius=(ph + 4) // 2)
    surf.blit(sh, (x - 2, y + 6))

    # Body: scarlet vertical gradient.
    pill = pygame.Surface((pw, ph), pygame.SRCALPHA)
    for yy in range(ph):
        t = yy / max(1, ph - 1)
        c = lerp_color(_SCARLET_TOP, _SCARLET_BOT, t)
        pygame.draw.line(pill, c, (0, yy), (pw - 1, yy))

    # Frosting on the top half + bottom darkening on the lower half so the
    # gradient reads as a glossy 3D pill rather than a flat colour ramp.
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


def _score_emblem(surf, cx, cy, r, label, value):
    """Hero score medallion — circular gold ring with a scarlet accent
    band, dark navy interior, radial laurel ticks, label at top, big
    gold value centred. Ported from tools/gen_scarlet_set.py::
    score_emblem so the pause / stats / game-over screens get the
    same hero treatment as the menu mockup."""
    # Soft drop shadow
    sh = pygame.Surface((r * 2 + 16, r * 2 + 16), pygame.SRCALPHA)
    pygame.draw.circle(sh, (0, 0, 0, 95), (r + 8, r + 8), r + 2)
    surf.blit(sh, (cx - r - 8, cy - r + 4))

    # Dark navy interior
    pygame.draw.circle(surf, _PANEL_DARK, (cx, cy), r)

    # Warm inner radial glow so the medallion feels lit from inside.
    inner_max = max(r - 6, 1)
    glow = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    for rr in range(inner_max, 0, -1):
        a = int(14 * (1 - rr / inner_max))
        pygame.draw.circle(glow, (255, 220, 140, a),
                           (r, r - r // 4), rr)
    surf.blit(glow, (cx - r, cy - r))

    # Thick outer gold ring + slim scarlet accent inside + thin inner gold.
    pygame.draw.circle(surf, _GOLD_BRIGHT, (cx, cy), r, 3)
    pygame.draw.circle(surf, _SCARLET_TOP, (cx, cy), max(r - 4, 1), 2)
    pygame.draw.circle(surf, _GOLD_DEEP,   (cx, cy), max(r - 9, 1), 1)

    # Radial laurel ticks around the outer ring.
    for ang_deg in range(0, 360, 12):
        a = math.radians(ang_deg - 90)
        x1 = cx + math.cos(a) * (r - 1)
        y1 = cy + math.sin(a) * (r - 1)
        x2 = cx + math.cos(a) * (r + 2)
        y2 = cy + math.sin(a) * (r + 2)
        pygame.draw.line(surf, _GOLD_DEEP, (x1, y1), (x2, y2), 1)

    # Label at top, value centred.
    lbl_y = cy - int(r * 0.42)
    lf = _font(13, True).render(label, True, _GOLD_MUTED)
    lf.set_alpha(230)
    surf.blit(lf, lf.get_rect(center=(cx, lbl_y)))

    val_size = max(16, int(r * 0.55))
    vf = _font(val_size, True).render(str(value), True, _GOLD_BRIGHT)
    vs = _font(val_size, True).render(str(value), True, NEAR_BLACK)
    vs.set_alpha(180)
    vr = vf.get_rect(center=(cx, cy + int(r * 0.15)))
    surf.blit(vs, (vr.x + 2, vr.y + 3))
    surf.blit(vf, vr)


def _draw_overlay_stars(surf, stars, t):
    """Twinkle star field. `stars` = list of (x,y,r,phase) from HUD.__init__."""
    for x, y, r, phase in stars:
        a = int(30 + 200 * (0.5 + 0.5 * math.sin(t * 1.4 + phase)))
        s = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 255, 255, a), (r + 1, r + 1), r)
        surf.blit(s, (x - r - 1, y - r - 1))


def _draw_trophy(surf, cx, cy, size):
    """Gold procedural trophy icon. `size` is approximate half-height.
    Drawn fully symmetric about a vertical axis through (cx, cy):
      * Cup widths use the same ±half-width on left & right
      * Handles drawn on a temp surface and mirrored via transform.flip
      * Stem / base / foot use odd widths so they centre exactly
    """
    s = size
    # Surface big enough for cup (full width 2s) + handle ears + foot overflow.
    pad   = 6
    g_w   = (s + pad) * 2 + 1   # odd → exact centre column
    g_h   = s * 3 + 4
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
                     (gx + half_top - 2, top_y + 1), 1)

    # ── Handles — draw the left ear once, then horizontal-flip for right ──
    h_w  = 5
    h_h  = max(4, s - 2)
    h_y  = top_y + 2
    ear  = pygame.Surface((h_w, h_h), pygame.SRCALPHA)
    # Left half of an ellipse — gives a nice C-shape opening right
    pygame.draw.arc(ear, GOLD, (0, 0, h_w * 2 - 1, h_h),
                    math.pi * 0.5, math.pi * 1.5, 2)
    # Mirror about the cup's vertical centre. Left ear ends at gx - half_top;
    # right ear starts at gx + half_top + 1 so the two ears occupy mirrored
    # column ranges.
    left_ear_x  = gx - half_top - h_w + 1
    right_ear_x = gx + half_top
    g.blit(ear, (left_ear_x, h_y))
    g.blit(pygame.transform.flip(ear, True, False),
           (right_ear_x, h_y))

    # ── Stem — odd width, exact centre ────────────────────────────────────
    stem_w  = 3
    stem_h  = s // 2
    stem_x  = gx - stem_w // 2
    pygame.draw.rect(g, DARK,  (stem_x - 1, bot_y + 1, stem_w + 2, stem_h + 1))
    pygame.draw.rect(g, GOLD,  (stem_x,     bot_y,     stem_w,     stem_h))

    # ── Base + foot — both odd-width so they centre exactly ───────────────
    base_w = (s - 1) * 2 + 1
    base_x = gx - base_w // 2
    base_y = bot_y + stem_h
    pygame.draw.rect(g, DARK,  (base_x - 1, base_y + 1, base_w + 2, 4))
    pygame.draw.rect(g, GOLD,  (base_x,     base_y,     base_w,     3))

    foot_w = base_w + 2
    foot_x = gx - foot_w // 2
    pygame.draw.rect(g, DARK,  (foot_x - 1, base_y + 5, foot_w + 2, 3))
    pygame.draw.rect(g, GOLD,  (foot_x,     base_y + 4, foot_w,     2))

    surf.blit(g, (cx - gx, cy - gy))


def _ribbon_banner(surf, cx, cy, text, w=120):
    """Hexagonal gold-cloth banner with notched ends + scarlet hairline
    trim — ported from tools/gen_scarlet_set.py::ribbon_banner so the
    game-over NEW BEST! readout uses the mockup's hero badge instead
    of plain pulsing text."""
    h = 26
    notch = 10
    x = cx - w // 2
    y = cy - h // 2
    body_pts = [
        (x + notch, y),
        (x + w - notch, y),
        (x + w, y + h // 2),
        (x + w - notch, y + h),
        (x + notch, y + h),
        (x, y + h // 2),
    ]
    pygame.draw.polygon(surf, _GOLD_BRIGHT, body_pts)
    pygame.draw.polygon(surf, _GOLD_DEEP, body_pts, 2)
    pygame.draw.line(surf, _SCARLET_BOT,
                     (x + notch, y + 3),
                     (x + w - notch, y + 3), 1)
    pygame.draw.line(surf, _SCARLET_BOT,
                     (x + notch, y + h - 4),
                     (x + w - notch, y + h - 4), 1)
    tf = _font(13, True).render(text, True, NEAR_BLACK)
    surf.blit(tf, tf.get_rect(center=(cx, cy)))


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
_FONT_REG  = os.path.join(_FONT_DIR, "LiberationSans-Regular.ttf")


def _font(size, bold=True):
    k = (size, bold)
    f = _fonts.get(k)
    if f is None:
        path = _FONT_BOLD if bold else _FONT_REG
        f = pygame.font.Font(path, size)
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


def _draw_buff_icon(surf, rect, kind):
    """Tiny 20x20-ish icon for an active buff. Matches in-world sprites."""
    cx, cy = rect.center
    if kind == "grow":
        # Mini velvet witch-hat: tall conical wine cone + slim ivory stem +
        # cream-butter spots. Mirrors the in-world powerup at HUD scale.
        # Cone outline (dark wine) + body
        cone_outline = [
            (cx,     cy - 8),   # peak
            (cx + 6, cy + 2),
            (cx + 7, cy + 4),
            (cx - 7, cy + 4),
            (cx - 6, cy + 2),
        ]
        cone_body = [
            (cx,     cy - 7),
            (cx + 5, cy + 2),
            (cx + 6, cy + 4),
            (cx - 6, cy + 4),
            (cx - 5, cy + 2),
        ]
        pygame.draw.polygon(surf, ( 60, 15, 25), cone_outline)
        pygame.draw.polygon(surf, (125, 30, 45), cone_body)
        # Pink highlight stripe down the left side of the cone
        pygame.draw.polygon(surf, (180, 60, 75), [
            (cx,     cy - 6),
            (cx - 2, cy - 1),
            (cx - 3, cy + 3),
            (cx - 1, cy + 3),
            (cx,     cy - 1),
        ])
        # Cream spots scattered down the cone
        pygame.draw.circle(surf, (255, 235, 175), (cx,     cy - 4), 1)
        pygame.draw.circle(surf, (255, 235, 175), (cx + 2, cy + 0), 1)
        pygame.draw.circle(surf, (255, 235, 175), (cx - 1, cy + 3), 1)
        # Slim ivory stem with a tiny bulb at the bottom
        pygame.draw.polygon(surf, (245, 230, 200), [
            (cx - 2, cy + 4),
            (cx + 2, cy + 4),
            (cx + 3, cy + 8),
            (cx + 1, cy + 9),
            (cx - 1, cy + 9),
            (cx - 2, cy + 8),
        ])
        pygame.draw.line(surf, (255, 250, 230),
                         (cx - 1, cy + 5), (cx - 1, cy + 8), 1)
    elif kind == "magnet":
        # Polished horseshoe magnet — rendered at 2× on a scratch surface
        # so the arc smooths under `smoothscale`. Has a dark silhouette
        # outline, a vertical red gradient flesh, and steel-tipped poles
        # at the bottom with tiny field-line sparks above the prongs.
        OUTLINE = ( 38,   8,  16)
        RED_TOP = (245,  78,  64)   # sunlit upper arc
        RED_MID = (215,  38,  46)
        RED_BOT = (150,  16,  26)   # deep base of the legs
        STEEL_LT = (220, 226, 240)
        STEEL_DK = (108, 116, 138)
        FIELD    = (255, 230, 130)  # warm spark colour for the field hint

        SX = SY = 40                # 2× scratch
        m = pygame.Surface((SX, SY), pygame.SRCALPHA)

        # Outer silhouette in OUTLINE: top arc (filled circle) + leg slab.
        pygame.draw.circle(m, OUTLINE, (20, 18), 14)
        pygame.draw.rect(m, OUTLINE, (6, 18, 28, 18))

        # Red flesh — vertical gradient column-by-column under a circle mask.
        red_layer = pygame.Surface((SX, SY), pygame.SRCALPHA)
        for y in range(40):
            if y <= 18:
                col = lerp_color(RED_TOP, RED_MID, max(0.0, y / 18.0))
            else:
                col = lerp_color(RED_MID, RED_BOT, (y - 18) / 18.0)
            pygame.draw.line(red_layer, col, (0, y), (SX - 1, y))
        # Mask the gradient to the inset silhouette.
        mask = pygame.Surface((SX, SY), pygame.SRCALPHA)
        pygame.draw.circle(mask, (255, 255, 255, 255), (20, 18), 12)
        pygame.draw.rect(mask, (255, 255, 255, 255), (8, 18, 24, 16))
        red_layer.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        m.blit(red_layer, (0, 0))

        # Carve the U cavity through OUTLINE + RED in one pass (alpha=0
        # writes "fully transparent" on SRCALPHA surfaces).
        pygame.draw.circle(m, (0, 0, 0, 0), (20, 18), 8)
        pygame.draw.rect(m, (0, 0, 0, 0), (12, 18, 16, 18))

        # Steel pole tips at the bottom of each leg.
        for lx in (6, 22):
            pygame.draw.rect(m, OUTLINE,  (lx, 30, 12, 6))
            pygame.draw.rect(m, STEEL_DK, (lx + 1, 31, 10, 4))
            pygame.draw.rect(m, STEEL_LT, (lx + 1, 31, 10, 1))

        # Sun glint along the upper-outer arc and a tiny highlight on the
        # left pole face — sells the metallic feel after smoothscale.
        pygame.draw.line(m, RED_TOP, (10, 12), (15,  6), 2)
        pygame.draw.line(m, STEEL_LT, (8, 32), (8, 35), 1)

        # Two faint magnetic-pull sparks above the poles.
        pygame.draw.line(m, FIELD, ( 8, 36), ( 6, 38), 1)
        pygame.draw.line(m, FIELD, (32, 36), (34, 38), 1)

        icon = pygame.transform.smoothscale(m, (rect.w, rect.h))
        surf.blit(icon, rect.topleft)
    elif kind == "slowmo":
        # Tiny clock face on SRCALPHA scratch
        r = 7
        D = r * 2 + 2
        mc = pygame.Surface((D, D), pygame.SRCALPHA)
        cc = (D // 2, D // 2)
        pygame.draw.circle(mc, (130, 65, 190, 255), cc, r)       # bezel
        pygame.draw.circle(mc, (42, 10, 70, 255), cc, r - 1)     # face
        # 4 major ticks
        for i in range(4):
            ang = math.pi / 2 * i - math.pi / 2
            x1 = cc[0] + math.cos(ang) * (r - 1)
            y1 = cc[1] + math.sin(ang) * (r - 1)
            x2 = cc[0] + math.cos(ang) * (r - 3)
            y2 = cc[1] + math.sin(ang) * (r - 3)
            pygame.draw.line(mc, (220, 190, 255, 230), (int(x1), int(y1)), (int(x2), int(y2)), 1)
        # Hour hand ~10 o'clock
        ha = math.pi * 2 * 10 / 12 - math.pi / 2
        pygame.draw.line(mc, (250, 225, 255, 255), cc,
                         (int(cc[0] + math.cos(ha) * 3), int(cc[1] + math.sin(ha) * 3)), 2)
        # Minute hand ~12 o'clock
        ma = -math.pi / 2
        pygame.draw.line(mc, (200, 155, 255, 255), cc,
                         (int(cc[0] + math.cos(ma) * 5), int(cc[1] + math.sin(ma) * 5)), 1)
        # Center dot
        pygame.draw.circle(mc, (255, 240, 255, 255), cc, 1)
        surf.blit(mc, (cx - D // 2, cy - D // 2))
    elif kind == "kfc":
        # Tiny red KFC bucket
        bw = 6
        bh = 7
        pts = [(cx - bw, cy - bh), (cx + bw, cy - bh),
               (cx + bw - 2, cy + bh), (cx - bw + 2, cy + bh)]
        pygame.draw.polygon(surf, (200, 18, 18), pts)
        pygame.draw.line(surf, WHITE,
                         (cx - bw + 1, cy), (cx + bw - 1, cy), 1)
        pygame.draw.rect(surf, (220, 35, 22),
                         (cx - bw - 1, cy - bh - 2, (bw + 1) * 2, 3),
                         border_radius=1)
    elif kind == "ghost":
        # Mini classic ghost: rounded head + straight sides + 3-bump skirt
        GW, GH = 20, 24
        gcx, gcy, hr = 10, 8, 8
        body_y2 = 16
        DARK_G = (32,  52, 120, 255)
        BODY_G = (205, 228, 255, 235)
        skirt   = [(1, body_y2), (4, GH-2), (8, body_y2+3),
                   (gcx, GH-2), (12, body_y2+3), (16, GH-2), (GW-1, body_y2)]
        skirt_o = [(0, body_y2), (4, GH-1), (7, body_y2+3),
                   (gcx, GH-1), (13, body_y2+3), (16, GH-1), (GW, body_y2)]
        mg = pygame.Surface((GW, GH), pygame.SRCALPHA)
        pygame.draw.circle(mg, DARK_G, (gcx, gcy), hr + 1)
        pygame.draw.rect(mg, DARK_G, (0, gcy, GW, body_y2 - gcy + 1))
        pygame.draw.polygon(mg, DARK_G, skirt_o)
        pygame.draw.circle(mg, BODY_G, (gcx, gcy), hr)
        pygame.draw.rect(mg, BODY_G, (1, gcy, GW - 2, body_y2 - gcy))
        pygame.draw.polygon(mg, BODY_G, skirt)
        for ex in (gcx - 3, gcx + 3):
            pygame.draw.circle(mg, (252, 254, 255, 255), (ex, gcy - 1), 3)
            pygame.draw.circle(mg, (50, 110, 220, 255),  (ex + 1, gcy), 2)
        surf.blit(mg, (cx - gcx, cy - gcy - 2))
    elif kind == "triple":
        # Gold coin with $ glyph — matches the in-world triple power-up icon.
        from game.config import POWERUP_R
        native = POWERUP_R * 2
        icon = pygame.Surface((native, native), pygame.SRCALPHA)
        _draw_dollar_coin_hud(icon, native // 2, native // 2, pulse=0.0)
        scaled = pygame.transform.smoothscale(icon, (20, 20))
        surf.blit(scaled, (cx - 10, cy - 10))
    elif kind == "reverse":
        # Reuse the cached high-resolution disc + arrows from the world
        # pickup, scaled to fit the badge slot.
        from game.entities import _get_reverse_icon
        diameter = min(rect.width, rect.height) - 2
        icon = _get_reverse_icon(diameter)
        surf.blit(icon, (cx - icon.get_width() // 2,
                         cy - icon.get_height() // 2))


class PauseButton:
    def __init__(self):
        self.rect = pygame.Rect(W - 56, 12, 44, 44)
        self.hover = False

    def contains(self, pos):
        return self.rect.collidepoint(pos)

    def draw(self, surf, paused=False):
        rounded_rect(surf, self.rect, 10, _PANEL_DARK, 200)
        # Orange border ring
        border = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(border, (*_ORANGE_BORDER, 120), (0, 0, self.rect.width,
                         self.rect.height), border_radius=10, width=1)
        surf.blit(border, self.rect.topleft)
        cx, cy = self.rect.center
        if paused:
            pygame.draw.polygon(surf, _GOLD_BRIGHT, [
                (cx - 7, cy - 10),
                (cx - 7, cy + 10),
                (cx + 9, cy),
            ])
        else:
            pygame.draw.rect(surf, _GOLD_BRIGHT, (cx - 8, cy - 9, 5, 18), border_radius=2)
            pygame.draw.rect(surf, _GOLD_BRIGHT, (cx + 3, cy - 9, 5, 18), border_radius=2)


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


class HUD:
    def __init__(self):
        self.pause_btn = PauseButton()
        self.help_btn = HelpButton()
        self.title_t = 0.0
        # Name-entry button rects — populated each frame by draw_name_entry,
        # read by scenes.py click-handling. Pre-init to empty rects so the
        # first click before any draw is harmless.
        self.name_submit_rect = pygame.Rect(0, 0, 0, 0)
        self.name_skip_rect   = pygame.Rect(0, 0, 0, 0)
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
        self.title_t += 1 / 60
        # Deep blue-purple dim
        dim = pygame.Surface((W, H), pygame.SRCALPHA)
        dim.fill((6, 2, 28, 165))
        surf.blit(dim, (0, 0))

        # Hero score medallion at the top so the player keeps a clear
        # read on the current run while paused (mockup convention).
        if score > 0:
            _score_emblem(surf, W // 2, 130, 44,
                          "S C O R E", str(score))

        cy = H // 2 + 30
        pulse = 1.0 + math.sin(self.title_t * 2.6) * 0.04
        _outlined_text(surf, "PAUSED", (W // 2, cy),
                        size=int(52 * pulse), px=3)

        alpha = int(150 + math.sin(self.title_t * 3.6) * 90)
        _pill_btn(surf, (W // 2, cy + 72), "TAP · P · ESC", size=16, alpha=alpha)

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
        _outlined_text(surf, "POCKET SKY FLYER", (W // 2, 184),
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
        h_start = _pill_h("TAP TO START", 22)
        h_howto = _pill_h("HOW TO PLAY", 18)
        h_power = _pill_h("POWER-UPS", 18)
        y_power = (H - 110) - 14 - h_power // 2
        y_howto = y_power - h_power // 2 - GAP - h_howto // 2
        y_start = y_howto - h_howto // 2 - GAP - h_start // 2

        btn_alpha = int(225 + math.sin(self.title_t * 3.6) * 30)
        self.menu_start_rect = _pill_btn(
            surf, (W // 2, y_start), "TAP TO START",
            size=22, alpha=btn_alpha, min_width=220, primary=True)
        self.menu_howto_rect = _pill_btn(
            surf, (W // 2, y_howto), "HOW TO PLAY",
            size=18, alpha=230, min_width=220)
        self.menu_powerups_rect = _pill_btn(
            surf, (W // 2, y_power), "POWER-UPS",
            size=18, alpha=230, min_width=220)

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
        lf = _font(12, False)
        vf = _font(22, True)

        # BEST panel (left)
        best_cx = left_x + panel_w // 2
        best_rect = pygame.Rect(left_x, cy - 24, panel_w, 48)
        _dark_panel(surf, best_rect, radius=14, alpha=190)
        lbl = lf.render("B E S T", True, _GOLD_MUTED)
        lbl.set_alpha(180)
        surf.blit(lbl, lbl.get_rect(center=(best_cx, cy - 12)))
        val = vf.render(str(best), True, _GOLD_BRIGHT)
        surf.blit(val, val.get_rect(center=(best_cx, cy + 8)))

        # TOP 10 panel (right) — clickable trophy button
        top_cx = left_x + panel_w + gap + panel_w // 2
        top_rect = pygame.Rect(left_x + panel_w + gap, cy - 24, panel_w, 48)
        _dark_panel(surf, top_rect, radius=14, alpha=190)
        top_lbl = lf.render("T O P  10", True, _GOLD_MUTED)
        top_lbl.set_alpha(180)
        surf.blit(top_lbl, top_lbl.get_rect(center=(top_cx, cy - 12)))
        _draw_trophy(surf, top_cx, cy + 10, 9)
        self.menu_top10_rect = top_rect

        # The corner `?` help button is intentionally not drawn here —
        # the POWER-UPS pill above replaces it. HelpButton class itself
        # remains in this file unused so it can be revived without churn
        # if ever needed.

    def draw_play(self, surf, world, best: int, paused: bool = False):
        # ── Score: centered, styled dark pill backdrop. Suppressed when
        # paused — the pause overlay shows the same number on its hero
        # medallion, and we don't want both reading at once.
        if not paused:
            score_txt = str(world.score)
            cf = _font(48, True)
            img = cf.render(score_txt, True, WHITE)
            out = cf.render(score_txt, True, _GOLD_BRIGHT)
            sh  = cf.render(score_txt, True, NEAR_BLACK)
            r = img.get_rect(center=(W // 2, 72))
            back_w = max(r.width + 52, 80)
            back_h = r.height + 16
            back = pygame.Surface((back_w, back_h), pygame.SRCALPHA)
            pygame.draw.rect(back, (*_PANEL_DARK, 140), (0, 0, back_w, back_h),
                             border_radius=back_h // 2)
            pygame.draw.rect(back, (*_ORANGE_BORDER, 60), (0, 0, back_w, back_h),
                             border_radius=back_h // 2, width=1)
            surf.blit(back, (W // 2 - back_w // 2, r.y - 8))
            for ox, oy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
                surf.blit(out, (r.x + ox, r.y + oy))
            sh.set_alpha(160)
            surf.blit(sh, (r.x + 2, r.y + 3))
            surf.blit(img, r.topleft)

        # ── Pill alpha fades when bird is near top
        bird_y = world.bird.y
        if bird_y >= 80:
            ui_alpha = 255
        elif bird_y <= 20:
            ui_alpha = 40
        else:
            ui_alpha = int(40 + 215 * (bird_y - 20) / 60)

        # BEST pill — dark panel with orange border
        hi_pill = pygame.Surface((96, 36), pygame.SRCALPHA)
        pygame.draw.rect(hi_pill, (*_PANEL_DARK, 210), (0, 0, 96, 36), border_radius=10)
        pygame.draw.rect(hi_pill, (*_ORANGE_BORDER, 80), (0, 0, 96, 36),
                         border_radius=10, width=1)
        # Trophy icon — same procedural gold trophy used elsewhere in the
        # leaderboard / theme; replaces the previous star-stub emblem.
        _draw_trophy(hi_pill, 18, 18, 8)
        bf = _font(11, False)
        bl = bf.render("BEST", True, _GOLD_MUTED)
        hi_pill.blit(bl, bl.get_rect(center=(60, 11)))
        vf = _font(15, True)
        vl = vf.render(str(best), True, _GOLD_BRIGHT)
        hi_pill.blit(vl, vl.get_rect(center=(60, 25)))
        hi_pill.set_alpha(ui_alpha)
        surf.blit(hi_pill, (10, 14))

        # Coin pill
        cc_pill = pygame.Surface((90, 36), pygame.SRCALPHA)
        pygame.draw.rect(cc_pill, (*_PANEL_DARK, 190), (0, 0, 90, 36), border_radius=10)
        pygame.draw.rect(cc_pill, (*_ORANGE_BORDER, 70), (0, 0, 90, 36),
                         border_radius=10, width=1)
        _coin_icon(cc_pill, 18, 18, 10)
        _text(cc_pill, f"x{world.coin_count}", (56, 18),
              size=18, color=_GOLD_BRIGHT, shadow=False)
        cc_pill.set_alpha(ui_alpha)
        surf.blit(cc_pill, (W - 158, 14))

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
        # left. Stacks vertically when multiple are active. Each bar uses
        # the same gold → orange → red gradient as time depletes, and the
        # whole row pulses with a red ring in the final 25 % of duration.
        active = []
        if world.triple_timer > 0:
            active.append(("triple", world.triple_timer, TRIPLE_DURATION))
        if world.magnet_timer > 0:
            active.append(("magnet", world.magnet_timer, MAGNET_DURATION))
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

        if active:
            icon_size = 24
            bar_w     = 132
            bar_h     = 12
            row_gap   = 6
            row_pitch = max(icon_size, bar_h) + row_gap
            row_w     = icon_size + 6 + bar_w
            base_x    = (W - row_w) // 2
            top_y     = 128

            for i, (kind, remain, total) in enumerate(active):
                y = top_y + i * row_pitch
                # Icon plate on the left
                icon_rect = pygame.Rect(base_x, y - (icon_size - bar_h) // 2,
                                        icon_size, icon_size)
                rounded_rect(surf, icon_rect, 6, (15, 25, 60), 200)
                _draw_buff_icon(surf, icon_rect.inflate(-4, -4), kind)

                # Bar to the right of the icon
                bx = icon_rect.right + 6
                by = y
                frac = max(0.0, min(1.0, remain / total))
                track = pygame.Rect(bx - 2, by, bar_w + 4, bar_h)
                rounded_rect(surf, track, 6, (20, 25, 50), 200)
                # Gold → orange → red as remaining time decreases
                if frac > 0.5:
                    fill_lo, fill_hi = UI_ORANGE, UI_GOLD
                elif frac > 0.25:
                    t = (frac - 0.25) / 0.25
                    fill_lo = lerp_color(UI_RED, UI_ORANGE, t)
                    fill_hi = lerp_color(UI_ORANGE, UI_GOLD, t)
                else:
                    fill_lo = (180, 20, 20)
                    fill_hi = UI_RED
                fill = pygame.Rect(bx, by + 2, int(bar_w * frac), bar_h - 4)
                if fill.width > 0:
                    rounded_rect_grad(surf, fill, 4, fill_hi, fill_lo)
                # Time-remaining text inside the bar
                _text(surf, f"{remain:.1f}s",
                      (bx + bar_w // 2, by + bar_h // 2),
                      size=11, color=UI_CREAM, shadow=True)
                # Low-time pulse ring around the row when critical
                if frac < 0.25:
                    pulse = 0.5 + 0.5 * math.sin(self.title_t * 14)
                    ring_a = int(140 * pulse)
                    ring = pygame.Surface((bar_w + 10, bar_h + 6), pygame.SRCALPHA)
                    pygame.draw.rect(ring, (*UI_RED, ring_a), ring.get_rect(),
                                     border_radius=8, width=2)
                    surf.blit(ring, (bx - 5, by - 3))

        # Float texts
        for ft in world.float_texts:
            ft.draw(surf)

    def draw_stats(self, surf, world, dt, elapsed, show_prompt: bool = True):
        self.title_t += dt
        dim = pygame.Surface((W, H), pygame.SRCALPHA)
        dim.fill((6, 1, 21, 190))
        surf.blit(dim, (0, 0))

        _draw_overlay_stars(surf, self._stars, self.title_t)
        # Mountain silhouette belongs to the backdrop — drawn here so the
        # score / stats cards layer on top instead of being clipped.
        _draw_mountain_silhouette(surf, alpha=160)

        # Slide-in animation from below
        slide_t = max(0.0, min(1.0, elapsed / 0.35))
        e = slide_t * slide_t * (3 - 2 * slide_t)
        card_y = int(58 + (1.0 - e) * 60)

        # Header — gold with red outline (matches the TOP 10 / WELCOME styling)
        _outlined_text(surf, "RUN SUMMARY", (W // 2, card_y - 4),
                        size=24, px=2, shadow_offset=(2, 3))

        # Hero score medallion in place of the rectangular score block —
        # sized to match the run-summary mockup proportionally (mockup
        # uses r=72*SCALE on a 720-wide canvas; live canvas is 360 wide
        # so the equivalent is r≈68).
        _score_emblem(surf, W // 2, card_y + 82, 68,
                      "S C O R E", str(world.score))

        # Stats card
        mins = int(world.time_alive) // 60
        secs = int(world.time_alive) % 60
        time_str = f"{mins}:{secs:02d}" if mins else f"{secs}s"
        rows = [
            ("Time alive",     time_str),
            ("Coins",          str(world.coin_count)),
            ("Pillars cleared", str(world.pillars_passed)),
            ("Power-ups",      str(sum(world.powerups_picked.values()))),
            ("Near misses",    str(world.near_misses)),
        ]

        row_h = 32
        card_rect = pygame.Rect(18, card_y + 162, W - 36, len(rows) * row_h + 20)
        _dark_panel(surf, card_rect, radius=16, alpha=210)

        ry = card_rect.y + 14
        for i, (label, value) in enumerate(rows):
            if i > 0:
                div = pygame.Surface((card_rect.width - 24, 1), pygame.SRCALPHA)
                div.fill((*_ORANGE_BORDER, 35))
                surf.blit(div, (card_rect.x + 12, ry - 4))
            # Per-character red-outline styling on every label and value —
            # same writing style as the TOP 10 / RUN SUMMARY headers, just
            # smaller. _outlined_text takes a centre point, so compute one
            # from the desired left/right anchor.
            kf = _font(13, True)
            klbl = kf.render(label.upper(), True, _GOLD_BRIGHT)
            kl_center = (card_rect.x + 16 + klbl.get_width() // 2, ry + klbl.get_height() // 2)
            _outlined_text(surf, label.upper(), kl_center,
                           size=13, px=1, shadow_offset=(1, 2))
            vf = _font(15, True)
            vimg = vf.render(value, True, _GOLD_BRIGHT)
            vr_center = (card_rect.right - 16 - vimg.get_width() // 2, ry + vimg.get_height() // 2)
            _outlined_text(surf, value, vr_center,
                           size=15, px=1, shadow_offset=(1, 2))
            ry += row_h

        # Tap-to-continue prompt — also outlined (gold + red) so every line
        # on the screen shares the same writing style.
        if elapsed >= 0.6 and show_prompt:
            alpha = max(80, min(255, int(150 + math.sin(self.title_t * 4) * 90)))
            # Render the outlined text onto a temp surface so we can apply
            # the pulsing alpha to the whole stack at once.
            tmp_w, tmp_h = 280, 36
            tmp = pygame.Surface((tmp_w, tmp_h), pygame.SRCALPHA)
            _outlined_text(tmp, "TAP TO CONTINUE",
                           (tmp_w // 2, tmp_h // 2),
                           size=18, px=2, shadow_offset=(2, 3))
            tmp.set_alpha(alpha)
            surf.blit(tmp, tmp.get_rect(center=(W // 2, H - 50)))

    def draw_gameover(self, surf, dt, score: int, new_best: bool):
        self.title_t += dt
        dim = pygame.Surface((W, H), pygame.SRCALPHA)
        dim.fill((6, 1, 21, 195))
        surf.blit(dim, (0, 0))

        _draw_overlay_stars(surf, self._stars, self.title_t)

        if score > 0:
            # "GAME OVER" with red outline
            pulse_go = 1.0 + math.sin(self.title_t * 3.0) * 0.03
            _outlined_text(surf, "GAME  OVER", (W // 2, 100),
                            size=int(38 * pulse_go), px=3)

            # Decorative divider
            pygame.draw.line(surf, (*_ORANGE_BORDER, 140),
                             (W // 2 - 80, 128), (W // 2 + 80, 128), 1)

            # Hero score medallion with a subtle gold sparkle ring so the
            # final score reads as the celebratory anchor of the screen.
            emblem_cx, emblem_cy, emblem_r = W // 2, 240, 56
            for i in range(20):
                ang = i * (2 * math.pi / 20) + math.pi / 20
                d = emblem_r + 22
                ex = emblem_cx + math.cos(ang) * d
                ey = emblem_cy + math.sin(ang) * d
                a = max(0, min(255, int(120 +
                    100 * math.sin(self.title_t * 3 + i * 0.6))))
                spark = pygame.Surface((6, 6), pygame.SRCALPHA)
                pygame.draw.line(spark, (*_GOLD_BRIGHT, a), (3, 0), (3, 5))
                pygame.draw.line(spark, (*_GOLD_BRIGHT, a), (0, 3), (5, 3))
                surf.blit(spark, (int(ex) - 3, int(ey) - 3))
            _score_emblem(surf, emblem_cx, emblem_cy, emblem_r,
                          "S C O R E", str(score))

            if new_best:
                # NEW BEST! sits between title and medallion as a
                # hexagonal ribbon banner (mockup convention). A small
                # gold sparkle burst pulses around it for celebration.
                nb_cy = 160
                for i in range(8):
                    ang = (i / 8) * math.pi * 2 + self.title_t * 2
                    r = 70 + 4 * math.sin(self.title_t * 5 + i)
                    dx, dy = math.cos(ang) * r, math.sin(ang) * r
                    a = max(0, min(255, int(100 + 120 * math.sin(self.title_t * 4 + i * 0.8))))
                    s = pygame.Surface((4, 4), pygame.SRCALPHA)
                    pygame.draw.circle(s, (*_GOLD_BRIGHT, a), (2, 2), 2)
                    surf.blit(s, (W // 2 + int(dx) - 2, nb_cy + int(dy) - 2))
                _ribbon_banner(surf, W // 2, nb_cy, "NEW  BEST !", w=130)
        else:
            pulse = 1.0 + math.sin(self.title_t * 4) * 0.05
            _outlined_text(surf, "TRY  AGAIN!", (W // 2, H // 2 - 30),
                            size=int(30 * pulse), fill=UI_ORANGE,
                            outline=_RED_OUTLINE, px=2)

        # Mountains first so the pill sits cleanly on top.
        _draw_mountain_silhouette(surf, alpha=160)
        # TAP TO RETRY pill — solid alpha + primary halo so it carries
        # the mockup's hero treatment instead of pulsing low.
        _pill_btn(surf, (W // 2, H - 56), "TAP TO RETRY",
                  size=19, alpha=255, min_width=220, primary=True)

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
        self.title_t += dt
        dim = pygame.Surface((W, H), pygame.SRCALPHA)
        dim.fill((0, 0, 20, 200))
        surf.blit(dim, (0, 0))

        # Header: trophy icon — "TOP 10" — trophy icon
        _outlined_text(surf, "TOP 10", (W // 2, 46), size=32, px=3)
        for side in (-1, 1):
            tx = W // 2 + side * 88
            ty = 46
            _draw_trophy(surf, tx, ty, 18)

        card_x, card_w = 14, W - 28

        # Slide-in from below (title_t reset to 0 on state entry)
        slide_t = min(1.0, self.title_t / 0.4)
        e = slide_t * slide_t * (3 - 2 * slide_t)
        card_y = int(88 + (1.0 - e) * 80)

        n = len(scores)
        if n == 0:
            # Two cases (the player only reaches this view once the
            # fetch has resolved, so there's no in-flight state):
            #   * fetch_error — Supabase/RLS/network call failed
            #   * neither — table is genuinely empty (brand-new database)
            if fetch_error:
                _text(surf, "Top-10 unavailable", (W // 2, card_y + 60),
                      size=18, color=UI_CREAM, shadow=True)
                _text(surf, "Check the browser console", (W // 2, card_y + 94),
                      size=12, color=UI_CREAM, shadow=False)
                _text(surf, "(" + fetch_error + ")", (W // 2, card_y + 116),
                      size=11, color=UI_CREAM, shadow=False)
            else:
                _text(surf, "No scores yet!", (W // 2, card_y + 60),
                      size=18, color=UI_CREAM, shadow=True)
                _text(surf, "Be the first.", (W // 2, card_y + 94),
                      size=14, color=UI_CREAM, shadow=False)
        else:
            # Each row is its own rounded pill with gold trim — matches
            # the leaderboard mockup. Player's row gets a thick gold
            # halo and a red "YOU" badge next to the name.
            row_h = 42
            row_gap = 4

            SILVER    = (185, 195, 205)
            BRONZE    = (185, 125,  55)

            f_badge = _font(13, True)
            f_name  = _font(16, True)
            f_you   = _font(10, True)
            f_score = _font(17, True)

            ry = card_y
            for i, entry in enumerate(scores):
                rank = i + 1
                if rank == 1:
                    badge_col = _GOLD_BRIGHT
                elif rank == 2:
                    badge_col = SILVER
                elif rank == 3:
                    badge_col = BRONZE
                else:
                    badge_col = _GOLD_BRIGHT  # outline-only for 4-10

                is_player = (i == player_rank)
                row_cy = ry + row_h // 2

                # Row pill: dark navy fill with a thin gold border. The
                # player's row gets a thicker, brighter gold halo so it
                # reads as the highlighted entry.
                row_rect = pygame.Rect(card_x, ry, card_w, row_h)
                row_radius = row_h // 2
                pnl = pygame.Surface(row_rect.size, pygame.SRCALPHA)
                pygame.draw.rect(pnl, (*_PANEL_DARK, 220),
                                 (0, 0, card_w, row_h),
                                 border_radius=row_radius)
                if is_player:
                    pygame.draw.rect(pnl, _GOLD_BRIGHT,
                                     (0, 0, card_w, row_h),
                                     width=3, border_radius=row_radius)
                else:
                    pygame.draw.rect(pnl, (*_GOLD_BRIGHT, 110),
                                     (0, 0, card_w, row_h),
                                     width=1, border_radius=row_radius)
                surf.blit(pnl, row_rect.topleft)

                # Rank badge: solid metallic disc for the top 3, gold
                # outline-only ring for ranks 4-10 (per mockup).
                badge_cx = card_x + 24
                if rank <= 3:
                    pygame.draw.circle(surf, badge_col, (badge_cx, row_cy), 13)
                    pygame.draw.circle(surf, NEAR_BLACK,
                                       (badge_cx, row_cy), 13, 1)
                    num_col = NEAR_BLACK
                else:
                    pygame.draw.circle(surf, badge_col,
                                       (badge_cx, row_cy), 13, 2)
                    num_col = _GOLD_BRIGHT
                num_img = f_badge.render(str(rank), True, num_col)
                surf.blit(num_img,
                          num_img.get_rect(center=(badge_cx, row_cy)))

                nm = entry["name"][:10]
                name_col = _GOLD_BRIGHT if is_player else WHITE
                nm_img = f_name.render(nm, True, name_col)
                nm_x = card_x + 44
                surf.blit(nm_img,
                          (nm_x, row_cy - nm_img.get_height() // 2))

                # "YOU" red badge next to the player's name, mockup-style.
                if is_player:
                    you_img = f_you.render("YOU", True, WHITE)
                    pw = you_img.get_width() + 10
                    ph = you_img.get_height() + 6
                    pxr = nm_x + nm_img.get_width() + 7
                    pyr = row_cy - ph // 2
                    you_pill = pygame.Surface((pw, ph), pygame.SRCALPHA)
                    pygame.draw.rect(you_pill, _SCARLET_TOP,
                                     (0, 0, pw, ph), border_radius=ph // 2)
                    pygame.draw.rect(you_pill, _GOLD_BRIGHT,
                                     (0, 0, pw, ph),
                                     width=1, border_radius=ph // 2)
                    surf.blit(you_pill, (pxr, pyr))
                    surf.blit(you_img, (pxr + 5, pyr + 3))

                # Score is always gold for readability against the
                # uniform dark row.
                sc_img = f_score.render(str(entry["score"]), True, _GOLD_BRIGHT)
                surf.blit(sc_img,
                          (card_x + card_w - 16 - sc_img.get_width(),
                           row_cy - sc_img.get_height() // 2))

                ry += row_h + row_gap

        if cooldown <= 0:
            alpha = int(170 + math.sin(self.title_t * 4) * 70)
            f2 = _font(16, True)
            prompt = f2.render("TAP  TO  MENU", True, _GOLD_MUTED)
            prompt.set_alpha(alpha)
            pr = prompt.get_rect(center=(W // 2, H - 28))
            surf.blit(prompt, pr.topleft)
