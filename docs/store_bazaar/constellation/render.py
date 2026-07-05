"""
STORE bazaar LANDING — concept #1 CONSTELLATION GRAND-BAZAAR (docs prototype).

The souk is woven from the jewel store's own night sky: seven category stalls
are gold-light constellations strung across the indigo nebula in a 2-3-2
horseshoe, joined by thin twinkling constellation lines (the "living
constellation web" signature). Pip the scarlet macaw hosts from a crescent-moon
counter dead-centre bottom. Night variant converges on the SAME indigo+gold
nebula so the screen dissolves straight into the constellation jewel store.

This is a selection-sheet prototype (docs only) — NOT game integration. It
reuses the SS=4 supersample pipeline + every primitive + the palette from the
sibling jewel-store renderer (store_redesign/constellation_hi/render_hi.py): one
1440x2560 device surface, ONE smoothscale down => crisp anti-aliased edges, type
rendered at size*SS resolves razor sharp. Both build targets safe: pure pygame,
no numpy, no desktop/browser-only API.
"""
import os
import sys
import math

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", "..", ".."))
_PRIM = os.path.join(_ROOT, "docs", "store_redesign", "constellation_hi")
for p in (_ROOT, _PRIM):
    if p not in sys.path:
        sys.path.insert(0, p)

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from game import parrot
from game import store_catalog

# Reuse the jewel-store primitives + palette so the bazaar is the SAME store.
from render_hi import (
    SS, DW, DH, m, mf, font,
    multistop_v, vgrad, vgrad_stops, gold_a_fill, soft_glow, drop_shadow,
    gradient_text, plain_text, facet_gem, cabochon, cabochon_glass,
    coin_glyph, bevel_rim, top_sheen, gold_rule, gloss_sweep, title_wordmark,
    _build_static_bg, draw_bg, _glyph_base, _stamp_bold,
    BG_STOPS, NEBULA_GLOW, GOLD, GOLD_PALE, GOLD_DEEP,
    GOLD_A_TOP, GOLD_A_BOT, GOLD_A_RIM_DARK, GOLD_A_RIM_BRIGHT, GOLD_A_NUM,
    RARITY, MYSTERY, NEAR_BLACK, WHITE, lerp_color,
    CARD_RING_BRIGHT, CARD_RING_DEEP, CREAM,
    downscale,
)


BALANCE = 14250


# ── the 7 stalls: group -> (label, preview item) ──────────────────────────────
# Per brief: sid = store_catalog.ids_of_group(group)[0], skipping a free DEFAULT
# if it leads; pick a representative PAID item. None of the groups lead with a
# free default, so [0] is taken directly — except SHADES, whose [0] is the
# deliberate "NO SHADES" non-preview, so the next meaningful paid pick is used
# (a representative shades item, honouring the "skip non-preview" clause).
_GROUP_LABEL = {
    "costume": "COSTUMES",
    "parrot": "PARROTS",
    "animal": "ANIMALS",
    "shoes": "SHOES",
    "hats": "HATS",
    "shades": "SHADES",
    "parcels": "PARCELS",
}
_SHADES_PREVIEW = "skin_shades_round"   # representative paid shades, not NO SHADES


def _preview_id(group):
    ids = store_catalog.ids_of_group(group)
    sid = ids[0]
    if group == "shades" and sid == "skin_shades_none":
        for cand in ids:
            if cand != "skin_shades_none":
                return cand
    return sid


def _rarity_pal(group):
    """Tier hue for a stall's awning/sign, taken from the preview item so the
    constellation matches the jewel-store rarity language."""
    sid = _preview_id(group)
    r = store_catalog.rarity(sid)
    return RARITY.get(r, RARITY["common"])


# ── thumbnail (skin shown on the macaw frame, cropped to its content) ─────────
_thumb_cache = {}


def _preview_surf(sid):
    out = _thumb_cache.get(sid)
    if out is None:
        src = parrot.get_skin_icon(sid) or parrot.get_skin_frame(sid, 1, 0.0)
        bb = src.get_bounding_rect()
        if bb.width > 0 and bb.height > 0:
            src = src.subsurface(bb).copy()
        out = src
        _thumb_cache[sid] = out
    return out


def blit_preview(surf, sid, cx, cy, box):
    """Scale the cropped preview into a box, add a crisp top-left rim light so it
    pops off the dark dome, and a soft tier-tinted contact glow under it."""
    src = _preview_surf(sid)
    sw, sh = src.get_size()
    s = box / max(sw, sh)
    img = pygame.transform.smoothscale(
        src, (max(1, int(sw * s)), max(1, int(sh * s))))
    # flat additive brighten so mids/highlights gain range against the near-black
    # well (no invented detail; alpha untouched so the silhouette edge stays clean)
    img = img.copy()
    img.fill((26, 26, 26, 0), special_flags=pygame.BLEND_RGB_ADD)
    r = img.get_rect(center=(cx, cy))
    # crisp top-left rim contour
    off = max(1, m(0.6))
    rim = pygame.Surface(img.get_size(), pygame.SRCALPHA)
    sil = img.copy()
    sil.fill((255, 248, 220, 255), special_flags=pygame.BLEND_RGBA_MULT)
    rim.blit(sil, (-off, -off))
    cut = img.copy()
    cut.fill((255, 255, 255, 255), special_flags=pygame.BLEND_RGBA_MULT)
    rim.blit(cut, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
    rim.set_alpha(170)
    surf.blit(rim, r.topleft, special_flags=pygame.BLEND_ADD)
    surf.blit(img, r.topleft)


# ── constellation glyph sign (the "joined-dot" category mark per stall) ───────
# Each stall carries a tiny dot-and-line constellation that names its category
# symbolically — the souk's signs ARE constellations. Authored at logical px.
_SIGNS = {
    # wardrobe / cape silhouette
    "costume": ([(0, -7), (-5, -2), (-4, 6), (4, 6), (5, -2), (0, -7), (0, 6)],
                "chain"),
    # perch ring of star-dots
    "parrot": ([(-6, 4), (-2, -5), (4, -4), (6, 4), (1, 6), (-6, 4)], "chain"),
    # paw print: 1 pad + 4 toes
    "animal": ([(0, 4)], "dots_paw"),
    # boot traced in dots
    "shoes": ([(-5, -6), (-5, 4), (5, 4), (6, 1), (-1, 1), (-1, -6), (-5, -6)],
              "chain"),
    # crown / top-hat constellation
    "hats": ([(-7, 5), (-5, -2), (-2, 4), (0, -6), (2, 4), (5, -2), (7, 5),
              (-7, 5)], "chain"),
    # twin lens cabochons (mirrors Pip's aviators)
    "shades": ([(-4, 0)], "shades"),
    # wrapped gift: 4 corner stars + ribbon arc
    "parcels": ([(-6, -5), (6, -5), (6, 5), (-6, 5), (-6, -5)], "gift"),
}


def draw_sign(surf, group, cx, cy, scale, pal):
    """The stall's joined-dot constellation sign — gold thread + node stars +
    soft glow, so the sign reads as a real constellation, not an icon."""
    pts, kind = _SIGNS[group]
    gold = (255, 230, 168)

    def P(p):
        return (int(cx + p[0] * scale), int(cy + p[1] * scale))

    layer = pygame.Surface((DW, DH), pygame.SRCALPHA)
    if kind in ("chain", "gift"):
        ap = [P(p) for p in pts]
        for a, b in zip(ap, ap[1:]):
            pygame.draw.line(layer, (*gold, 150), a, b, max(1, m(0.9)))
        if kind == "gift":
            # ribbon arc + vertical tie
            pygame.draw.line(layer, (*gold, 150), P((0, -5)), P((0, 5)),
                             max(1, m(0.9)))
            pygame.draw.line(layer, (*gold, 150), P((-6, 0)), P((6, 0)),
                             max(1, m(0.9)))
        nodes = pts
    elif kind == "dots_paw":
        nodes = [(0, 5), (-5, -1), (-2, -6), (2, -6), (5, -1)]
        # main pad slightly larger handled by node size below
    elif kind == "shades":
        # twin lens cabochons connected by a bridge
        for sx in (-1, 1):
            lc = P((sx * 5, 0))
            pygame.draw.circle(layer, (*pal["gem"], 220), lc, max(2, int(m(3.4))))
            pygame.draw.circle(layer, (255, 255, 255, 230), lc,
                               max(1, int(m(3.4))), max(1, m(0.8)))
            soft_glow(layer, lc[0], lc[1], m(4), pal["glow"], 130, layers=5)
        pygame.draw.line(layer, (*gold, 200), P((-2, 0)), P((2, 0)), max(1, m(1.0)))
        surf.blit(layer, (0, 0), special_flags=pygame.BLEND_ADD)
        return
    else:
        nodes = pts

    for p in nodes:
        x, y = P(p)
        soft_glow(layer, x, y, m(3.2), gold, 120, layers=5)
        pygame.draw.circle(layer, (255, 246, 214, 240), (x, y), max(1, m(1.2)))
    surf.blit(layer, (0, 0), special_flags=pygame.BLEND_ADD)


# ── the awning-tile stall (one shared template; sign + preview vary) ──────────
STALL_W, STALL_H = 96, 116
AWN_H = 26                                   # faceted awning band height
RAD = 16


def draw_stall(surf, group, cx, cy, mystery=False):
    """One faceted-awning constellation stall: a domed dark tile under a
    gem-faceted scalloped awning, a glass cabochon cradling the REAL preview,
    its constellation sign, and a thick gold-keyline category label."""
    pal = MYSTERY if mystery else _rarity_pal(group)
    sid = _preview_id(group)
    w, h = m(STALL_W), m(STALL_H)
    rect = pygame.Rect(int(cx - w / 2), int(cy - h / 2), w, h)
    rad = m(RAD)

    # depth: soft drop shadow so the stall floats above the nebula
    drop_shadow(surf, rect, rad, blur=m(7), alpha=150, dy=m(4))

    # tile body — deep indigo glass, slightly tier-warmed at the foot
    body_t = (26, 28, 64)
    body_b = (10, 11, 32)
    surf.blit(vgrad(w, h, rad, body_t, body_b, 250, gamma=1.15), rect.topleft)
    top_sheen(surf, rect, rad, m(20), peak=46)

    # tier-tinted soft inner aura behind the cabochon so each stall owns a hue
    soft_glow(surf, rect.centerx, rect.y + m(AWN_H + 28), m(22), pal["glow"], 26,
              layers=8)

    # ── faceted gem awning: a scalloped gradient band with crown facets ───────
    aw_top = rect.y
    aw_h = m(AWN_H)
    scallop = 6
    seg = w / scallop
    awn = pygame.Surface((w, aw_h + m(8)), pygame.SRCALPHA)
    top_c = lerp_color(pal["gem"], WHITE, 0.18)
    mid_c = pal["glow"]
    bot_c = lerp_color(pal["deep"], NEAR_BLACK, 0.05)
    band = vgrad_stops(w, aw_h, 0,
                       [(0.0, top_c), (0.55, mid_c), (1.0, bot_c)], 255, gamma=1.05)
    # scalloped lower edge mask (gem-facet swags)
    mask = pygame.Surface((w, aw_h + m(8)), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, aw_h - m(3)),
                     border_top_left_radius=rad, border_top_right_radius=rad)
    for i in range(scallop):
        sx = int(i * seg)
        pygame.draw.polygon(mask, (255, 255, 255, 255),
                            [(sx, aw_h - m(4)), (sx + seg / 2, aw_h + m(5)),
                             (sx + seg, aw_h - m(4))])
    awn.blit(band, (0, 0))
    awn.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(awn, (rect.x, aw_top))
    # crown-facet hairlines down the awning so it reads jewel-cut, not flat cloth
    for i in range(1, scallop):
        fx = int(rect.x + i * seg)
        pygame.draw.line(surf, (*lerp_color(pal["deep"], NEAR_BLACK, 0.3), 170),
                         (fx, aw_top + m(2)), (fx, aw_top + aw_h - m(2)),
                         max(1, m(0.7)))
    # bright awning lip + dark keyline under it
    pygame.draw.line(surf, (*lerp_color(top_c, WHITE, 0.4), 220),
                     (rect.x + m(4), aw_top + m(2)), (rect.right - m(4), aw_top + m(2)),
                     max(1, m(1.0)))

    # constellation SIGN hangs just under the awning
    draw_sign(surf, group, rect.centerx, aw_top + aw_h + m(16), m(1.0), pal)

    # ── glass cabochon cradling the REAL preview thumbnail ───────────────────
    disc_cy = rect.y + m(AWN_H + 46)
    R = m(24)
    soft_glow(surf, rect.centerx, disc_cy, R + m(3), pal["glow"], 28, layers=8)
    cabochon(surf, rect.centerx, disc_cy, R, (22, 24, 50), (6, 7, 20),
             ring=pal["gem"], ring_a=50)
    if mystery:
        from game.surprise_box_variants import _draw_qmark
        _draw_qmark(surf, rect.centerx, disc_cy, R + m(6), CREAM, NEAR_BLACK,
                    thick=m(3))
    else:
        blit_preview(surf, sid, rect.centerx, disc_cy, R * 1.62)
    cabochon_glass(surf, rect.centerx, disc_cy, R, tint=pal["gem"])

    # ── category label on a thick gold-keyline plate ─────────────────────────
    label = _GROUP_LABEL[group]
    plate_y = rect.bottom - m(15)
    f = font(12.5)
    lw = _glyph_base(label, f, m(0.6)).get_width() + m(2)
    pw = min(w - m(8), lw + m(18))
    plate = pygame.Rect(int(rect.centerx - pw / 2), int(plate_y - m(11)),
                        int(pw), m(22))
    surf.blit(vgrad(plate.w, plate.h, plate.h // 2, (18, 16, 40), (8, 8, 22), 235),
              plate.topleft)
    pygame.draw.rect(surf, (0, 0, 0, 200), plate, width=max(1, m(1.4)),
                     border_radius=plate.h // 2)
    bevel_rim(surf, plate, plate.h // 2, CARD_RING_DEEP,
              (*CARD_RING_BRIGHT, 220), w=max(1, m(1.2)))
    gradient_text(surf, label, f, plate.center, (255, 246, 206), (236, 178, 70),
                  tracking=m(0.6), weight=m(1.0), keyline=(40, 26, 6), kw=m(1.0),
                  shadow=True)

    # crisp dark outer keyline UNDER a bright tier bevel so the stall edge is
    # clearly defined against the nebula
    pygame.draw.rect(surf, (4, 5, 16), rect, width=max(1, m(1.8)),
                     border_radius=rad)
    bevel_rim(surf, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 200),
              w=max(1, m(1.6)))
    # tier corner gem set into the top-right awning so the rarity reads from afar
    facet_gem(surf, rect.right - m(13), rect.y + m(13), m(6.5),
              pal["gem"], pal["deep"], mystery=mystery)

    return (rect.centerx, aw_top + m(3))      # the awning node the web links to


# ── the 2-3-2 horseshoe layout + the living constellation web ─────────────────
# 7 stall centres on a gentle dome hugging the upper two-thirds. Authored in
# logical px; a 2 (high corners) - 3 (middle band) - 2 (lower flanks) arc.
STALL_SLOTS = [
    ("hats",     58, 192),     # high-left corner
    ("parrot",  302, 192),     # high-right corner
    ("costume",  57, 322),     # middle band, left flank
    ("parcels", 180, 286),     # middle band, centre crown (mystery hero, raised)
    ("animal",  303, 322),     # middle band, right flank
    ("shoes",    95, 446),     # lower-left flank
    ("shades",  265, 446),     # lower-right flank
]
# the web links: indices into STALL_SLOTS forming one connected sky-figure
# (<=14 link-lines per the concept's clutter budget)
WEB_LINKS = [
    (0, 2), (2, 3), (3, 4), (4, 1), (0, 3), (1, 3),
    (2, 5), (4, 6), (5, 3), (6, 3),
]


def draw_web(surf, nodes):
    """The SIGNATURE: thin gold constellation lines linking the 7 stall awnings
    into ONE sky-figure, with twinkling node stars at each junction. Tapered
    stacked strokes + soft glow so the web reads as deliberate, never a stray
    hairline; kept sparse to stay legible at 360px."""
    web = pygame.Surface((DW, DH), pygame.SRCALPHA)
    for ai, bi in WEB_LINKS:
        a, b = nodes[ai], nodes[bi]
        # tapered stacked strokes: a wide soft halo under a crisp bright core so
        # the thread reads as a deliberate glowing constellation link.
        for wth, al in ((m(3.2), 50), (m(1.8), 120), (m(0.8), 235)):
            pygame.draw.line(web, (236, 206, 138, al), a, b, max(1, int(wth)))
        # a travelling spark mid-link so the web feels alive (twinkle)
        sx = int((a[0] + b[0]) / 2)
        sy = int((a[1] + b[1]) / 2)
        soft_glow(web, sx, sy, m(3.4), (255, 240, 184), 130, layers=5)
        pygame.draw.circle(web, (255, 250, 224, 230), (sx, sy), max(1, m(1.0)))
    for x, y in nodes:
        soft_glow(web, x, y, m(6), (255, 232, 172), 180, layers=6)
        pygame.draw.circle(web, (255, 252, 230, 250), (x, y), max(1, m(2.4)))
        pygame.draw.circle(web, (255, 226, 150, 255), (x, y), max(1, m(1.4)))
        # 4-point sparkle cross on each awning node
        L = m(4)
        pygame.draw.line(web, (255, 244, 200, 200), (x - L, y), (x + L, y),
                         max(1, m(0.8)))
        pygame.draw.line(web, (255, 244, 200, 200), (x, y - L), (x, y + L),
                         max(1, m(0.8)))
    surf.blit(web, (0, 0), special_flags=pygame.BLEND_ADD)


# ── Pip the star-merchant at the crescent-moon counter ────────────────────────
def draw_pip_counter(surf):
    """Pip (scarlet macaw + gold aviators) hosting from a low crescent-moon
    counter, dead-centre bottom: Pip rises ABOVE a glowing gold crescent ledge
    that cradles him, the real get_parrot frame scaled up with two aviator
    lens-glints + one wing-up welcome read, and a soft welcome glow — the warm
    anchor that pulls the eye to the centre of the dome."""
    cx = DW // 2
    moon_cy = DH - m(36)                 # the crescent's geometric centre, low

    # ── the crescent-moon COUNTER ────────────────────────────────────────────
    # A gold disc with an offset disc subtracted from its UPPER-FRONT so a warm
    # crescent CRADLE survives — a C-moon opening upward, its two horns curling
    # up at the ends. Pip stands in the cradle; the dark nebula shows through the
    # carved interior so the shape reads unmistakably as a crescent, not a disc.
    cres_r = m(82)
    cut_r = m(64)
    cut_dy = m(22)                       # cut disc pushed UP => bottom crescent
    pad = m(18)
    sz = cres_r * 2 + pad * 2
    cm = pygame.Surface((sz, sz), pygame.SRCALPHA)
    c = cres_r + pad
    # gold crescent gradient (bright outer rim deepening inward).
    moon = pygame.Surface((cres_r * 2, cres_r * 2), pygame.SRCALPHA)
    for i in range(cres_r, 0, -1):
        f = i / cres_r
        col = lerp_color((150, 100, 28), (255, 232, 150), f ** 0.6)
        pygame.draw.circle(moon, (*col, 255), (cres_r, cres_r), i)
    cm.blit(moon, (c - cres_r, c - cres_r))
    # carve the upper interior away => only the bottom crescent ledge remains.
    cut = pygame.Surface(cm.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(cut, (255, 255, 255, 255), (c, c - cut_dy), cut_r)
    cm.blit(cut, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
    soft_glow(surf, cx, moon_cy, m(98), (250, 206, 120), 46, layers=10)
    surf.blit(cm, (cx - c, moon_cy - c))
    # the dark indigo COUNTER FACE filling the carved cradle, so Pip stands
    # against a deep well (not a bright bowl) and the crescent reads as a C-moon.
    face = pygame.Surface(cm.get_size(), pygame.SRCALPHA)
    for i in range(cut_r, 0, -1):
        f = i / cut_r
        col = lerp_color((10, 11, 30), (26, 24, 58), 1 - f)
        pygame.draw.circle(face, (*col, 255), (c, c - cut_dy), i)
    # clip the face to the moon disc so it doesn't spill past the rim at the top
    fclip = pygame.Surface(cm.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(fclip, (255, 255, 255, 255), (c, c), cres_r - m(4))
    face.blit(fclip, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(face, (cx - c, moon_cy - c))
    # bright lit lip on the crescent's inner (upper) edge + dark outer keyline,
    # both masked to the surviving crescent so they trace only the moon.
    keep = pygame.Surface(cm.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(keep, (255, 255, 255, 255), (c, c), cres_r)
    pygame.draw.circle(keep, (0, 0, 0, 0), (c, c - cut_dy), cut_r)
    rim = pygame.Surface(cm.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(rim, (255, 252, 224, 235), (c, c - cut_dy), cut_r,
                       max(1, m(2.4)))                    # inner lit lip
    pygame.draw.circle(rim, (70, 42, 10, 230), (c, c), cres_r, max(1, m(2.2)))  # outer keyline
    rim.blit(keep, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(rim, (cx - c, moon_cy - c))

    # the crescent's two upper horns catch a sharp gold spark
    for hx, hy in _crescent_horns(cx, moon_cy, cres_r, cut_r, cut_dy):
        soft_glow(surf, hx, hy, m(4.5), (255, 242, 192), 150, layers=5)
        pygame.draw.circle(surf, (255, 252, 230, 245), (hx, hy), max(1, m(1.8)))

    # ── Pip, scaled up, rising from the cradle ───────────────────────────────
    pip = parrot.get_parrot(1, 0.0)
    pw, ph = pip.get_size()
    scale = m(70) / max(pw, ph)
    pip_big = pygame.transform.smoothscale(
        pip, (max(1, int(pw * scale)), max(1, int(ph * scale))))
    bh = int(ph * scale)
    pip_cy = moon_cy - cut_dy - m(6)     # nestled in the crescent's cradle
    pr = pip_big.get_rect(center=(cx, pip_cy))
    # soft welcome glow behind Pip — kept low so it warms Pip without washing
    # the dark counter face to cream.
    soft_glow(surf, cx, pip_cy, m(30), (255, 222, 150), 24, layers=8)
    # contact shadow where Pip meets the cradle ledge
    cs = pygame.Surface((int(pw * scale * 0.9), m(9)), pygame.SRCALPHA)
    pygame.draw.ellipse(cs, (40, 24, 6, 150), cs.get_rect())
    surf.blit(cs, (pr.centerx - cs.get_width() // 2, pr.bottom - m(8)))
    surf.blit(pip_big, pr.topleft)
    # two gold aviator lens-glints (Pip's signature throws light)
    for gx in (cx - int(m(8)), cx + int(m(3))):
        gy = pr.y + int(bh * 0.40)
        soft_glow(surf, gx, gy, m(3.2), (255, 246, 210), 150, layers=4)
        pygame.draw.circle(surf, (255, 255, 240, 230), (gx, gy), max(1, m(1.0)))


def _crescent_horns(cx, cy, R, cut_r, cut_dy):
    """The two points where the carved crescent's edges meet (its horns) — the
    intersection of the outer disc (R, centred at cy) and the cut disc (cut_r,
    centred cut_dy above cy). Both centres lie on the vertical axis, so the
    intersection is symmetric about cx."""
    d = float(cut_dy) or 1.0
    a = (R * R - cut_r * cut_r + d * d) / (2 * d)   # distance from outer centre
    yy = cy - a
    half = max(0.0, R * R - a * a)
    hx = math.sqrt(half)
    return [(int(cx - hx), int(yy)), (int(cx + hx), int(yy))]


# ── header ────────────────────────────────────────────────────────────────────
def draw_header(surf):
    # darkening band behind the title lane for legibility
    band = pygame.Surface((DW, m(100)), pygame.SRCALPHA)
    for y in range(m(100)):
        a = int(120 * (1 - y / m(100)) ** 1.2)
        pygame.draw.line(band, (14, 14, 44, a), (0, y), (DW, y))
    surf.blit(band, (0, 0))
    # screen frame hairline
    pygame.draw.rect(surf, (*GOLD, 60), (m(3), m(3), DW - m(6), DH - m(6)),
                     width=max(1, m(1)), border_radius=m(12))
    # TITLE — standard Skybit gold-on-red menu wordmark
    title_wordmark(surf, "STORE", (DW // 2, m(26)), 30, tracking=m(4))
    balance_capsule(surf, DW - m(70), m(70))
    # "tap a stall" hint, left of the capsule lane
    hint_capsule(surf, m(96), m(70))


def hint_capsule(surf, cx, y):
    """A subtle recessed hint pill: 'TAP A STALL' in muted cream-gold."""
    f = font(10.5)
    txt = "TAP A STALL"
    tw = _glyph_base(txt, f, m(0.8)).get_width()
    w = tw + m(26)
    h = m(26)
    r = pygame.Rect(int(cx - w / 2), int(y - h / 2), w, h)
    surf.blit(vgrad(w, h, h // 2, (20, 20, 46, 180)[:3], (10, 10, 28), 200),
              r.topleft)
    pygame.draw.rect(surf, (0, 0, 0, 160), r, width=max(1, m(1.2)),
                     border_radius=h // 2)
    pygame.draw.rect(surf, (*GOLD, 70), r.inflate(-m(1.2), -m(1.2)),
                     width=max(1, m(1)), border_radius=h // 2)
    # a tiny finger/spark dot at the head
    soft_glow(surf, r.x + m(13), y, m(3), (255, 230, 168), 120, layers=4)
    pygame.draw.circle(surf, (255, 246, 214, 230), (r.x + m(13), y), max(1, m(1.4)))
    plain_text(surf, txt, f, (r.centerx + m(6), y), (208, 200, 176),
               shadow_a=140, tracking=m(0.8), weight=m(0.7),
               keyline=(8, 8, 20), kw=m(0.7))


def balance_capsule(surf, cx, y):
    """Jewel-grade recessed gold capsule with the REAL in-game coin + a loud
    gradient-gold balance number (the same money-screen treatment as the jewel
    store)."""
    val = f"{BALANCE:,}"
    vf = font(20)
    vw = _glyph_base(val, vf, 0).get_width() + m(2)
    coin_d, gapc, padl, padr = m(24), m(12), m(12), m(16)
    w = padl + coin_d + gapc + vw + padr
    h = m(38)
    cap = pygame.Rect(int(cx - w / 2), int(y - h / 2), w, h)
    # clamp inside the frame
    if cap.right > DW - m(8):
        cap.x = DW - m(8) - cap.w
    drop_shadow(surf, cap, h // 2, blur=m(5), alpha=130, dy=m(3))
    surf.blit(vgrad(cap.w, cap.h, h // 2, (58, 42, 22), (22, 15, 8), 255, gamma=1.1),
              cap.topleft)
    top_sheen(surf, cap, h // 2, m(14), peak=50)
    pygame.draw.rect(surf, (0, 0, 0, 200), cap, width=max(1, m(1.6)),
                     border_radius=h // 2)
    bevel_rim(surf, cap, h // 2, lerp_color(GOLD, NEAR_BLACK, 0.4),
              (*GOLD_PALE, 240), w=max(1, m(1.6)))
    x = cap.x + padl
    soft_glow(surf, x + coin_d // 2, cap.centery, int(coin_d * 0.40),
              (255, 206, 92), 42, layers=6)
    coin_glyph(surf, x + coin_d // 2, cap.centery, coin_d // 2)
    x += coin_d + gapc
    gradient_text(surf, val, vf, (x + vw // 2, cap.centery), GOLD_A_TOP, GOLD_A_BOT,
                  weight=m(1.0), keyline=(96, 56, 12), kw=m(1.1), shadow=True)


# ── compose ───────────────────────────────────────────────────────────────────
def draw_dome_label(surf):
    """A small gold rule + sub-title under the header so the dome reads as a
    'GRAND BAZAAR', tying the souk name to the constellation theme."""
    y = m(96)
    gold_rule(surf, m(46), DW - m(46), y, GOLD, peak=150, thick=m(1.1))
    plain_text(surf, "GRAND  BAZAAR  OF  STARS", font(11),
               (DW // 2, y + m(13)), (236, 214, 150), shadow_a=140,
               tracking=m(2.0), weight=m(0.8), keyline=(10, 10, 24), kw=m(0.8))


def render_device():
    surf = pygame.Surface((DW, DH))
    draw_bg(surf)
    draw_header(surf)
    draw_dome_label(surf)

    # draw the web FIRST (behind the stalls) using the awning-node anchors, then
    # the stalls on top so the threads tuck under each awning lip.
    nodes = []
    centers = []
    for group, lx, ly in STALL_SLOTS:
        cx = int(mf(lx))
        cy = int(mf(ly))
        centers.append((group, cx, cy))
        # the web links to the awning crest (top centre of each stall)
        nodes.append((cx, int(cy - m(STALL_H) / 2 + m(3))))
    draw_web(surf, nodes)

    for group, cx, cy in centers:
        draw_stall(surf, group, cx, cy, mystery=(group == "parcels"))

    draw_pip_counter(surf)
    return surf


def main():
    _build_static_bg()
    dev = render_device()
    pygame.image.save(downscale(dev, 1), os.path.join(_HERE, "round_1.png"))
    pygame.image.save(downscale(dev, 2), os.path.join(_HERE, "round_1@2x.png"))
    print("SS =", SS, "device =", DW, "x", DH)
    print("saved round_1.png (360x640) + round_1@2x.png (720x1280)")


if __name__ == "__main__":
    main()
