"""
Rarity v2 — make RARITY POP on the store item card.

The shipped card treats rarity as a whisper: a small corner gem, a faint aura
behind the dome, a barely-there cabochon ring tint. At 165x99 grid scale you
genuinely cannot tell tiers apart. This sheet explores 4 LOUDER, premium rarity
treatments, each drawn on the REAL assembled card across all 5 tiers
(common -> rare -> epic -> legendary -> mystery), reusing the shipped renderer's
primitives + palette + real thumbnails so the explorations look like the game.

This renderer does NOT mutate the shipped card. It imports render_hi, reuses
draw_card's drawing recipe verbatim, and only swaps the rarity-bearing layers.
Both build targets safe: pure pygame, no numpy, no desktop/browser-only API.
"""
import os
import sys
import math

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
# the shipped renderer lives next door under constellation_hi/
sys.path.insert(0, os.path.join(_ROOT, "docs", "store_redesign", "constellation_hi"))

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

import render_hi as R
from render_hi import (
    m, font, SS,
    lerp_color, lerp_stops, NEAR_BLACK, WHITE,
    vgrad, vgrad_stops, multistop_v, soft_glow, drop_shadow,
    top_sheen, contact_shadow, bevel_rim, gold_rule,
    cabochon, cabochon_glass, facet_gem, blit_thumb,
    plain_text, gradient_text, _glyph_base, _stamp_bold,
    state_chip, draw_const_thread,
    RARITY, MYSTERY, BG_STOPS, NEBULA_GLOW,
    CARD_T, CARD_B, CABO_LO, CABO_HI, CREAM, NAME_COL,
    CARD_RING_DEEP, CARD_RING_BRIGHT, GOLD, GOLD_PALE,
    CARD_W, CARD_H, CARD_RAD, R_DISC, CY_DISC, Y_NAME, Y_CHIP, GEM_R,
    _draw_qmark, _name, _is_secret, _rarity,
)


# ── the 5-tier sample row: one real item per tier + a masked secret ──────────
ROW_IDS = [
    "skin_bluegold",   # common    BLUE MACAW
    "skin_pharaoh",    # rare      PHARAOH
    "skin_dragon",     # epic      DRAGON
    "skin_kitsune",    # legendary KITSUNE
    "skin_ufo",        # legendary, secret -> masked MYSTERY
]
TIER_WORD = {
    "skin_bluegold": "COMMON",
    "skin_pharaoh":  "RARE",
    "skin_dragon":   "EPIC",
    "skin_kitsune":  "LEGENDARY",
    "skin_ufo":      "MYSTERY",
}


def _pal(sid):
    return MYSTERY if _is_secret(sid) else RARITY[_rarity(sid)]


def _legendary(sid):
    """Legendary stays the loudest per canon — extra glow/sheen headroom."""
    return (not _is_secret(sid)) and _rarity(sid) == "legendary"


# =============================================================================
# Shared chassis — the shipped card body, MINUS the rarity-bearing layers.
# Each treatment supplies its own rarity look on top of this identical base so
# the only thing that varies between treatments is the rarity language.
# =============================================================================
def _card_chassis(surf, rect, equipped):
    rad = m(CARD_RAD)
    drop_shadow(surf, rect, rad, blur=m(8), alpha=160, dy=m(4))
    surf.blit(vgrad(rect.w, rect.h, rad, CARD_T, CARD_B, 252, gamma=1.15),
              rect.topleft)
    top_sheen(surf, rect, rad, m(30), peak=62)
    contact_shadow(surf, rect, rad, m(9), alpha=120)
    pygame.draw.rect(surf, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    bevel_rim(surf, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235),
              w=max(1, m(2.0)))


def _inner_tray(surf, rect):
    rad = m(CARD_RAD)
    tray = rect.inflate(-m(7), -m(7))
    trad = rad - m(4)
    pygame.draw.rect(surf, (10, 10, 24, 200), tray.inflate(m(2), m(2)),
                     width=max(1, m(1)), border_radius=trad + m(1))
    pygame.draw.rect(surf, (*CARD_RING_BRIGHT, 90), tray, width=max(1, m(1)),
                     border_radius=trad)


def _equipped_frame(surf, rect):
    rad = m(CARD_RAD)
    halo = pygame.Surface((rect.w + m(16), rect.h + m(16)), pygame.SRCALPHA)
    for k in range(5, 0, -1):
        pygame.draw.rect(halo, (*GOLD, int(20 * k / 5)),
                         (m(8) - k * m(1), m(8) - k * m(1),
                          rect.w + 2 * k * m(1), rect.h + 2 * k * m(1)),
                         width=max(1, m(1.4)), border_radius=rad + k * m(1))
    surf.blit(halo, (rect.x - m(8), rect.y - m(8)), special_flags=pygame.BLEND_ADD)
    pygame.draw.rect(surf, CARD_RING_DEEP, rect, width=max(1, m(3)), border_radius=rad)
    lip = rect.inflate(-m(2), -m(2))
    pygame.draw.rect(surf, GOLD, lip, width=max(1, m(2)), border_radius=rad - m(1))


def _cabochon_stack(surf, sid, rect, pal, aura_a=32, ring_a=0, ring_col=None,
                    ring_w=2.4):
    """The glass dome + rim-lit hero, optionally with a bold tier-coloured aura
    and a crisp coloured ring (treatment B). Returns the masked/real name."""
    cx, cy = rect.centerx, rect.y + m(CY_DISC)
    soft_glow(surf, cx, cy, m(R_DISC + 3), pal["glow"], aura_a, layers=8)
    cabochon(surf, cx, cy, m(R_DISC), CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    if _is_secret(sid):
        _draw_qmark(surf, cx, cy, m(R_DISC + 6), CREAM, NEAR_BLACK, thick=m(2))
        name = "???"
    else:
        blit_thumb(surf, sid, cx, cy, m(R_DISC) * 1.5)
        name = _name(sid)
    cabochon_glass(surf, cx, cy, m(R_DISC), tint=pal["gem"])
    # bold tier ring sits OUTSIDE the gold bezel so it doesn't fight the glass
    if ring_a and ring_col:
        rr = m(R_DISC) + m(3)
        pygame.draw.circle(surf, (0, 0, 0, 150), (cx, cy), rr + m(0.6),
                           max(1, m(ring_w + 0.8)))
        pygame.draw.circle(surf, (*ring_col, ring_a), (cx, cy), rr,
                           max(1, m(ring_w)))
        # a bright top-left arc kiss so the ring reads jewelled, not printed
        edge = pygame.Surface((rr * 2 + m(6), rr * 2 + m(6)), pygame.SRCALPHA)
        ec = rr + m(3)
        lit = lerp_color(ring_col, WHITE, 0.5)
        pygame.draw.arc(edge, (*lit, 230),
                        (ec - rr, ec - rr, rr * 2, rr * 2),
                        math.radians(110), math.radians(205), max(1, m(ring_w)))
        surf.blit(edge, (cx - ec, cy - ec), special_flags=pygame.BLEND_ADD)
    return name


# =============================================================================
# TREATMENT 1 — RARITY NAMEPLATE
# The item NAME sits on a tier-coloured gradient plate (gem -> deep ramp) with a
# crisp gold keyline + a small uppercase TIER LABEL. Rarity is READ, not guessed.
# =============================================================================
def draw_card_nameplate(surf, sid, rect, equipped):
    pal = _pal(sid)
    _card_chassis(surf, rect, equipped)
    _inner_tray(surf, rect)
    cx = rect.centerx
    gx, gy = rect.right - m(17), rect.y + m(17)

    name = _cabochon_stack(surf, sid, rect, pal, aura_a=30)
    facet_gem(surf, gx, gy, m(GEM_R), pal["gem"], pal["deep"],
              mystery=_is_secret(sid))

    # the rarity NAMEPLATE: a rounded tier-gradient plate seated in its own lane
    # between the dome and the chip, gem(top) -> deep(bottom) so the tier hue is
    # unmistakable, with a gold keyline (lane-3 card gold) + a faux-bold tier word
    # stamped above the name. Lane is held above the chip so nothing overlaps.
    plate_w = rect.w - m(18)
    plate_h = m(31)
    plate = pygame.Rect(cx - plate_w // 2, rect.y + m(51), plate_w, plate_h)
    prad = m(9)
    drop_shadow(surf, plate, prad, blur=m(3), alpha=110, dy=m(2))
    top = lerp_color(pal["gem"], pal["glow"], 0.3)
    bot = lerp_color(pal["deep"], NEAR_BLACK, 0.18)
    surf.blit(vgrad_stops(plate.w, plate.h, prad,
                          [(0.0, top), (0.5, pal["glow"]), (1.0, bot)],
                          255, gamma=1.1), plate.topleft)
    top_sheen(surf, plate, prad, m(11), peak=70)
    contact_shadow(surf, plate, prad, m(3), alpha=70)
    pygame.draw.rect(surf, (4, 5, 16), plate, width=max(1, m(1.6)),
                     border_radius=prad)
    bevel_rim(surf, plate, prad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 230),
              w=max(1, m(1.3)))
    # tier word — small uppercase, dark on the bright top band, tracked; a thin
    # gold divider separates the tier label lane from the name lane.
    tier = TIER_WORD[sid]
    plain_text(surf, tier, font(7.5), (cx, plate.y + m(8)), (14, 12, 26),
               shadow_a=0, tracking=m(1.4), weight=m(0.7))
    gold_rule(surf, plate.x + m(10), plate.right - m(10), plate.y + m(14),
              CARD_RING_BRIGHT, peak=130, thick=m(0.8))
    # the name in cream with a tight dark keyline so it pops on the colour plate
    _name_on(surf, name, cx, plate.y + m(23), plate_w - m(14))
    R.state_chip(surf, sid, cx, rect.y + m(91), equipped, _is_secret(sid),
                 m(20))
    if equipped:
        _equipped_frame(surf, rect)


def _name_on(surf, name, cx, cy, max_w):
    sz = 13.5
    f = font(sz)
    while _glyph_base(name, f, 0).get_width() > max_w and sz > 9:
        sz -= 0.5
        f = font(sz)
    plain_text(surf, name, f, (cx, cy), (250, 248, 240), shadow_a=160,
               weight=m(0.9), keyline=(6, 6, 16), kw=m(1.0))


# =============================================================================
# TREATMENT 2 — RARITY HALO + RING
# A bold, defined tier glow + a crisp coloured ring around the glass dome, so the
# cabochon is HALOED in the tier colour. The corner gem + name lane stay. Rarity
# pops from the hero's frame instead of a printed label.
# =============================================================================
def draw_card_halo(surf, sid, rect, equipped):
    pal = _pal(sid)
    _card_chassis(surf, rect, equipped)
    _inner_tray(surf, rect)
    cx, cy = rect.centerx, rect.y + m(CY_DISC)
    gx, gy = rect.right - m(17), rect.y + m(17)

    # a BOLD tier halo BEHIND the dome (much stronger than the shipped whisper),
    # legendary gets the loudest peak per canon.
    peak = 150 if _legendary(sid) else 120
    soft_glow(surf, cx, cy, m(R_DISC + 12), pal["glow"], peak, layers=12)
    # the crisp coloured ring rides the dome rim
    name = _cabochon_stack(surf, sid, rect, pal, aura_a=0,
                           ring_a=255, ring_col=pal["gem"], ring_w=2.6)
    facet_gem(surf, gx, gy, m(GEM_R), pal["gem"], pal["deep"],
              mystery=_is_secret(sid))
    # small tier tag pill below the dome so the halo's hue gets a name (premium
    # legibility — colour alone never carries meaning).
    _tier_tag(surf, sid, cx, rect.y + m(46), pal)
    R.fit_name(surf, name, cx, rect.y + m(Y_NAME), rect.w - m(26))
    R.state_chip(surf, sid, cx, rect.y + m(Y_CHIP), equipped, _is_secret(sid),
                 m(21))
    if equipped:
        _equipped_frame(surf, rect)


def _tier_tag(surf, sid, cx, cy, pal):
    """A tiny tier-coloured chip naming the halo's hue."""
    tier = TIER_WORD[sid]
    f = font(7.5)
    tw = _glyph_base(tier, f, m(1.0)).get_width()
    pad = m(7)
    w, h = tw + pad * 2, m(13)
    r = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    rad = h // 2
    surf.blit(vgrad(r.w, r.h, rad, lerp_color(pal["gem"], pal["glow"], 0.4),
                    lerp_color(pal["deep"], NEAR_BLACK, 0.1), 255), r.topleft)
    pygame.draw.rect(surf, (4, 5, 16), r, width=max(1, m(1.1)), border_radius=rad)
    pygame.draw.rect(surf, (*CARD_RING_BRIGHT, 150), r.inflate(-m(1.1), -m(1.1)),
                     width=max(1, m(0.7)), border_radius=rad)
    plain_text(surf, tier, f, (cx, cy - m(0.5)), (16, 14, 28), shadow_a=0,
               tracking=m(1.0), weight=m(0.6))


# =============================================================================
# TREATMENT 3 — RARITY FRAME
# The whole ticket is "framed" by rarity: a tier-coloured TOP ACCENT BAR with the
# tier word, tier-tinted corner brackets, and a tier-tinted inner bezel line. The
# obsidian body + gold edge survive; rarity wraps the card.
# =============================================================================
def draw_card_frame(surf, sid, rect, equipped):
    pal = _pal(sid)
    _card_chassis(surf, rect, equipped)
    rad = m(CARD_RAD)

    # tier-tinted inner bezel line replacing the neutral gold tray line, so the
    # frame itself carries the tier hue.
    tray = rect.inflate(-m(7), -m(7))
    trad = rad - m(4)
    pygame.draw.rect(surf, (10, 10, 24, 200), tray.inflate(m(2), m(2)),
                     width=max(1, m(1)), border_radius=trad + m(1))
    ring_col = lerp_color(pal["gem"], pal["glow"], 0.3)
    pygame.draw.rect(surf, (*ring_col, 220), tray, width=max(1, m(1.5)),
                     border_radius=trad)
    # soft tier wash bleeding in from the frame edge (premium tint, not a fill)
    wash = pygame.Surface(rect.size, pygame.SRCALPHA)
    for i in range(m(10)):
        a = int(40 * (1 - i / m(10)) ** 1.6)
        pygame.draw.rect(wash, (*pal["glow"], a),
                         (i, i, rect.w - 2 * i, rect.h - 2 * i),
                         width=max(1, m(1)), border_radius=rad - i)
    surf.blit(wash, rect.topleft, special_flags=pygame.BLEND_ADD)

    # the TOP ACCENT BAR: a tier-gradient strip across the card head, gold-keyed,
    # carrying the tier word. This is the loud, instantly-scannable rarity read.
    bar_h = m(17)
    bar = pygame.Rect(rect.x + m(5), rect.y + m(5), rect.w - m(10), bar_h)
    brad = bar_h // 2
    top = lerp_color(pal["gem"], WHITE, 0.12)
    bot = lerp_color(pal["deep"], NEAR_BLACK, 0.12)
    surf.blit(vgrad_stops(bar.w, bar.h, brad,
                          [(0.0, top), (0.55, pal["glow"]), (1.0, bot)], 255,
                          gamma=1.08), bar.topleft)
    top_sheen(surf, bar, brad, m(7), peak=72)
    pygame.draw.rect(surf, (4, 5, 16), bar, width=max(1, m(1.2)),
                     border_radius=brad)
    pygame.draw.rect(surf, (*CARD_RING_BRIGHT, 170), bar.inflate(-m(1.2), -m(1.2)),
                     width=max(1, m(0.7)), border_radius=brad)
    plain_text(surf, TIER_WORD[sid], font(8.5), bar.center, (14, 12, 26),
               shadow_a=0, tracking=m(1.6), weight=m(0.7))

    # tier-tinted corner brackets (top-left + bottom-right read the light source)
    _corner_brackets(surf, rect, pal)

    # dome shifted DOWN to clear the accent bar, gem in the OTHER free corner
    cx = rect.centerx
    cy = rect.y + m(CY_DISC) + m(8)
    soft_glow(surf, cx, cy, m(R_DISC + 3), pal["glow"], 36, layers=8)
    cabochon(surf, cx, cy, m(R_DISC), CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    if _is_secret(sid):
        _draw_qmark(surf, cx, cy, m(R_DISC + 6), CREAM, NEAR_BLACK, thick=m(2))
        name = "???"
    else:
        blit_thumb(surf, sid, cx, cy, m(R_DISC) * 1.5)
        name = _name(sid)
    cabochon_glass(surf, cx, cy, m(R_DISC), tint=pal["gem"])
    facet_gem(surf, rect.x + m(17), cy, m(GEM_R - 1), pal["gem"], pal["deep"],
              mystery=_is_secret(sid))

    R.fit_name(surf, name, cx, rect.y + m(Y_NAME) + m(3), rect.w - m(26))
    R.state_chip(surf, sid, cx, rect.y + m(Y_CHIP) + m(1), equipped,
                 _is_secret(sid), m(20))
    if equipped:
        _equipped_frame(surf, rect)


def _corner_brackets(surf, rect, pal):
    rad = m(CARD_RAD)
    L = m(20)
    inset = m(4)
    lit = lerp_color(pal["gem"], WHITE, 0.4)
    dk = lerp_color(pal["deep"], NEAR_BLACK, 0.2)
    th = max(1, m(2.2))
    # top-left (lit) and bottom-right (shaded) brackets following the radius
    for (corner, col) in (("tl", lit), ("br", dk)):
        s = pygame.Surface(rect.size, pygame.SRCALPHA)
        if corner == "tl":
            pygame.draw.line(s, (*col, 230), (inset + rad - m(4), inset),
                             (inset + L, inset), th)
            pygame.draw.line(s, (*col, 230), (inset, inset + rad - m(4)),
                             (inset, inset + L), th)
            pygame.draw.arc(s, (*col, 230),
                            (inset, inset, m(20), m(20)),
                            math.radians(90), math.radians(180), th)
        else:
            x1 = rect.w - inset
            y1 = rect.h - inset
            pygame.draw.line(s, (*col, 220), (x1 - rad + m(4), y1),
                             (x1 - L, y1), th)
            pygame.draw.line(s, (*col, 220), (x1, y1 - rad + m(4)),
                             (x1, y1 - L), th)
            pygame.draw.arc(s, (*col, 220),
                            (x1 - m(20), y1 - m(20), m(20), m(20)),
                            math.radians(270), math.radians(360), th)
        surf.blit(s, rect.topleft)


# =============================================================================
# TREATMENT 4 — RADIANT GEM CREST
# The gem is promoted to a real crest: a larger faceted gem with a tier-coloured
# RADIANT SUNRAY burst behind it + a rarity RIBBON banner under it. The gem
# becomes the hero's badge of rank.
# =============================================================================
def draw_card_crest(surf, sid, rect, equipped):
    pal = _pal(sid)
    _card_chassis(surf, rect, equipped)
    _inner_tray(surf, rect)
    cx = rect.centerx
    name = _cabochon_stack(surf, sid, rect, pal, aura_a=30)

    # the crest sits in the top-right corner: a compact radiant tier burst behind
    # a larger faceted gem. The burst is masked to the card so it never bleeds out
    # and is kept tight so it haloes the gem without crowding the dome.
    gx, gy = rect.right - m(19), rect.y + m(19)
    _radiant_burst(surf, rect, gx, gy, m(GEM_R + 6), pal,
                   loud=_legendary(sid))
    facet_gem(surf, gx, gy, m(GEM_R + 3), pal["gem"], pal["deep"],
              mystery=_is_secret(sid))

    # the rarity RIBBON: a small tier-coloured banner with notched ends in its own
    # lane, carrying the tier word; the item name sits below it, the chip below
    # that — each lane clear of the next.
    _ribbon(surf, sid, cx, rect.y + m(55), rect.w - m(34), pal)
    _name_on(surf, name, cx, rect.y + m(70), rect.w - m(26))
    R.state_chip(surf, sid, cx, rect.y + m(88), equipped,
                 _is_secret(sid), m(20))
    if equipped:
        _equipped_frame(surf, rect)


def _radiant_burst(surf, rect, cx, cy, r, pal, loud=False):
    """A tier-coloured sunray burst behind the crest gem, masked to the card."""
    rad = m(CARD_RAD)
    burst = pygame.Surface(rect.size, pygame.SRCALPHA)
    bx, by = cx - rect.x, cy - rect.y
    n = 12
    peak = 185 if loud else 135
    long_r = r * (1.85 if loud else 1.65)
    for i in range(n):
        a0 = 2 * math.pi * i / n
        wedge = math.pi / n * 0.62
        col = pal["glow"] if i % 2 == 0 else lerp_color(pal["gem"], WHITE, 0.2)
        al = int(peak * (0.62 if i % 2 else 1.0))
        p0 = (bx + r * 0.5 * math.cos(a0), by + r * 0.5 * math.sin(a0))
        p1 = (bx + long_r * math.cos(a0 - wedge),
              by + long_r * math.sin(a0 - wedge))
        p2 = (bx + long_r * math.cos(a0 + wedge),
              by + long_r * math.sin(a0 + wedge))
        pygame.draw.polygon(burst, (*col, al), [p0, p1, p2])
    # soft central bloom + a faint dark vignette so rays don't read flat
    soft_glow(burst, bx, by, int(r * 1.4), pal["glow"], peak, layers=8)
    # mask the burst to the card body so it stops at the bevel
    mask = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(),
                     border_radius=rad)
    burst.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(burst, rect.topleft, special_flags=pygame.BLEND_ADD)


def _ribbon(surf, sid, cx, cy, max_w, pal):
    """A tier-coloured banner with notched ends carrying the tier word."""
    tier = TIER_WORD[sid]
    f = font(8.5)
    tw = _glyph_base(tier, f, m(1.4)).get_width()
    pad = m(12)
    w = min(max_w, tw + pad * 2)
    h = m(15)
    notch = m(5)
    x0, y0 = cx - w // 2, cy - h // 2
    top = lerp_color(pal["gem"], WHITE, 0.1)
    bot = lerp_color(pal["deep"], NEAR_BLACK, 0.05)
    # build the ribbon body as a gradient surface, clipped to a notched polygon
    body = vgrad_stops(w, h, 0, [(0.0, top), (0.5, pal["glow"]), (1.0, bot)],
                       255, gamma=1.08)
    poly = [(notch, 0), (w - notch, 0), (w, h // 2), (w - notch, h),
            (notch, h), (0, h // 2)]
    pmask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(pmask, (255, 255, 255, 255), poly)
    body.blit(pmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    # drop shadow under the banner
    sh = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(sh, (0, 0, 0, 120), poly)
    surf.blit(sh, (x0, y0 + m(2)))
    surf.blit(body, (x0, y0))
    # gold keyline around the notched silhouette (lane-3 card gold)
    abspoly = [(x0 + px, y0 + py) for px, py in poly]
    pygame.draw.polygon(surf, (4, 5, 16), abspoly, width=max(1, m(1.4)))
    pygame.draw.polygon(surf, (*CARD_RING_BRIGHT, 200),
                        [(x0 + px, y0 + py + m(0.6)) for px, py in poly][:3]
                        + [(x0 + poly[5][0], y0 + poly[5][1] + m(0.6))],
                        width=max(1, m(0.8)))
    # small top sheen along the upper edge
    plain_text(surf, tier, f, (cx, cy), (14, 12, 26), shadow_a=0,
               tracking=m(1.4), weight=m(0.7))


# =============================================================================
# the shipped (CURRENT) card, for the top reference row
# =============================================================================
def draw_card_current(surf, sid, rect, equipped):
    R.draw_card(surf, sid, rect, equipped)


# =============================================================================
# Sheet composition
# =============================================================================
TREATMENTS = [
    ("CURRENT  (shipped — too subtle)", draw_card_current),
    ("1  RARITY NAMEPLATE", draw_card_nameplate),
    ("2  RARITY HALO + RING", draw_card_halo),
    ("3  RARITY FRAME", draw_card_frame),
    ("4  RADIANT GEM CREST", draw_card_crest),
]


def _row_device(label, fn):
    """One treatment: a label + the card drawn across all 5 tiers on the bg."""
    pad = m(16)
    lab_h = m(26)
    gap = m(10)
    n = len(ROW_IDS)
    w = pad * 2 + n * m(CARD_W) + (n - 1) * gap
    h = lab_h + m(CARD_H) + pad
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    surf.blit(multistop_v(w, h, BG_STOPS), (0, 0))
    soft_glow(surf, w // 2, h // 2, m(150), NEBULA_GLOW, 30, layers=8)
    plain_text(surf, label, font(13), (pad + m(2) + _label_off(label), m(15)),
               GOLD_PALE, shadow_a=140, weight=m(0.9),
               keyline=(10, 10, 24), kw=m(0.8))
    for i, sid in enumerate(ROW_IDS):
        x = pad + i * (m(CARD_W) + gap)
        y = lab_h
        fn(surf, sid, pygame.Rect(x, y, m(CARD_W), m(CARD_H)), equipped=False)
    return surf


def _label_off(label):
    f = font(13)
    return _glyph_base(label, f, 0).get_width() // 2


def _gray_strip_device(width):
    """A small grayscale proof: each treatment's 5 tiers desaturated, to show
    the tiers still separate by VALUE (colourblind-safe), not hue alone."""
    cell = m(40)
    gap = m(6)
    pad = m(14)
    title_h = m(22)               # the sheet's own header lane
    row_label_h = m(15)           # the per-treatment label above its swatches
    tier_label_h = m(15)          # the tier word under each swatch
    row_pitch = row_label_h + cell + tier_label_h + m(10)
    n = len(ROW_IDS)
    row_w = n * cell + (n - 1) * gap
    treats = TREATMENTS[1:]        # skip CURRENT in the value proof
    h = pad * 2 + title_h + len(treats) * row_pitch
    surf = pygame.Surface((width, h), pygame.SRCALPHA)
    surf.fill((18, 18, 22))
    plain_text(surf, "GREYSCALE VALUE PROOF — tiers still separate without hue",
               font(11), (width // 2, pad + m(6)), (220, 220, 224), shadow_a=0,
               weight=m(0.8))
    # each treatment reduces its card's tier surface to ONE representative colour
    # so the proof shows the value the player actually scans (the plate fill, the
    # halo glow, the frame line, the crest gem).
    treat_rarity_cols = {
        "1  RARITY NAMEPLATE": lambda pal: lerp_color(pal["glow"], pal["deep"], 0.5),
        "2  RARITY HALO + RING": lambda pal: pal["glow"],
        "3  RARITY FRAME": lambda pal: lerp_color(pal["gem"], pal["glow"], 0.3),
        "4  RADIANT GEM CREST": lambda pal: pal["gem"],
    }
    y = pad + title_h
    x0 = (width - row_w) // 2
    for label, _fn in treats:
        plain_text(surf, label, font(9), (width // 2, y + row_label_h // 2),
                   (210, 210, 214), shadow_a=0, weight=m(0.7))
        sy = y + row_label_h
        getter = treat_rarity_cols[label]
        for i, sid in enumerate(ROW_IDS):
            pal = _pal(sid)
            col = getter(pal)
            # ITU-R BT.601 luma so the value read matches perception
            lum = int(0.299 * col[0] + 0.587 * col[1] + 0.114 * col[2])
            x = x0 + i * (cell + gap)
            r = pygame.Rect(x, sy, cell, cell)
            pygame.draw.rect(surf, (lum, lum, lum), r, border_radius=m(4))
            pygame.draw.rect(surf, (60, 60, 64), r, width=max(1, m(1)),
                             border_radius=m(4))
            plain_text(surf, TIER_WORD[sid][:4], font(7),
                       (r.centerx, r.bottom + tier_label_h // 2 + m(1)),
                       (170, 170, 174), shadow_a=0, weight=m(0.5))
        y += row_pitch
    return surf


def main():
    R._build_static_bg()
    rows = [_row_device(lab, fn) for lab, fn in TREATMENTS]
    sheet_w = max(r.get_width() for r in rows)
    gray = _gray_strip_device(sheet_w)
    title_h = m(40)
    total_h = title_h + sum(r.get_height() for r in rows) + m(10) + gray.get_height()
    dev = pygame.Surface((sheet_w, total_h))
    dev.fill((10, 10, 26))
    plain_text(dev, "SKYBIT STORE — RARITY v2  (much-more-noticeable, premium, all 5 tiers)",
               font(15), (sheet_w // 2, m(20)), (255, 232, 170), shadow_a=150,
               weight=m(1.0), keyline=(20, 12, 4), kw=m(1.0))
    y = title_h
    for r in rows:
        dev.blit(r, ((sheet_w - r.get_width()) // 2, y))
        y += r.get_height()
    y += m(10)
    dev.blit(gray, ((sheet_w - gray.get_width()) // 2, y))
    # ONE smoothscale down (the crispness lever)
    out = pygame.transform.smoothscale(
        dev, (dev.get_width() // SS, dev.get_height() // SS))
    path = os.path.join(_HERE, "rarity_options.png")
    pygame.image.save(out, path)
    print("saved", path, out.get_size())


if __name__ == "__main__":
    main()
