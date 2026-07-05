"""
Coin Store redesign — concepts_v3 selection harness (Night Aviary evolutions).

Five distinct evolutions of the chosen NIGHT AVIARY look: same jewel-box DNA
(deep night world, round glass-cabochon thumbnail, faceted rarity gem, warm-gold
coin + balance capsule, unified chip, colourblind-safe 4-tier + mystery rarity),
each shifting the MATERIAL / MOTIF / palette-accent so they read as five different
luxe night jewel-boxes.

This round's job is to FIX the layout defects that plagued the baseline. The
card is rebuilt on a strict three-band grid so the cabochon, the NAME, and the
price/state CHIP never overlap, the corner gem is seated with margin, the header
keeps the title / balance capsule / tab strip in separate vertical lanes, and
the page controls clear both the grid and the BACK pill. Concepts only paint
material into those fixed slots — geometry is shared so spacing stays premium.

Selection sheet only: no convergence, no integration. Procedural pygame, both
build targets safe.
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
_ROOT2 = os.path.abspath(os.path.join(_HERE, "..", ".."))
if _ROOT2 not in sys.path:
    sys.path.insert(0, _ROOT2)

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from game.config import W, H
from game.draw import lerp_color, rounded_rect, UI_CREAM, NEAR_BLACK, WHITE
from game.hud import _font, _draw_overlay_stars, \
    _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP, _RED_OUTLINE
from game.powerup_help import _seeded_stars
from game import parrot
from game import store_catalog
from game.surprise_box_variants import _draw_qmark

# ── curated 8-card sample spanning all four tiers + secret + equipped ─────────
SAMPLE_IDS = [
    "skin_bluegold",     # common      (parrot)
    "skin_owl",          # rare        -> shown EQUIPPED
    "skin_dragon",       # epic
    "skin_kitsune",      # legendary
    "skin_pharaoh",      # rare        (costume)
    "skin_phoenix",      # epic
    "skin_aurora_stag",  # legendary
    "skin_ufo",          # secret (masked ???)
]
EQUIPPED_ID = "skin_owl"
SECRET_ID = "skin_ufo"
BALANCE = 14250

DETAIL_IDS = ["skin_bluegold", "skin_phoenix", "skin_ufo"]


def _cost(sid):
    return store_catalog.cost(sid) if store_catalog.exists(sid) else 0


def _rarity(sid):
    return store_catalog.rarity(sid)


def _name(sid):
    return store_catalog.name(sid) if store_catalog.exists(sid) else "DEFAULT"


def _is_secret(sid):
    try:
        return store_catalog.is_secret(sid)
    except Exception:
        return sid == SECRET_ID


# ── cached thumbnails, cropped-to-content + fit to a box ──────────────────────
_thumb_cache = {}


def thumb(sid, box):
    key = (sid, box)
    out = _thumb_cache.get(key)
    if out is None:
        src = parrot.get_skin_icon(sid) or parrot.get_skin_frame(sid, 1, 0.0)
        bb = src.get_bounding_rect()
        if bb.width > 0 and bb.height > 0:
            src = src.subsurface(bb).copy()
        sw, sh = src.get_size()
        s = box / max(sw, sh)
        out = pygame.transform.smoothscale(
            src, (max(1, int(sw * s)), max(1, int(sh * s))))
        _thumb_cache[key] = out
    return out


# ── shared low-level primitives (pygame-only, both-target safe) ───────────────

def vgrad_rect(w, h, radius, top, bot, alpha=255):
    body = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        c = lerp_color(top, bot, y / max(1, h - 1))
        pygame.draw.line(body, (*c, alpha), (0, y), (w - 1, y))
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h), border_radius=radius)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return body


def hgrad_rect(w, h, radius, left, right, alpha=255):
    body = pygame.Surface((w, h), pygame.SRCALPHA)
    for x in range(w):
        c = lerp_color(left, right, x / max(1, w - 1))
        pygame.draw.line(body, (*c, alpha), (x, 0), (x, h - 1))
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h), border_radius=radius)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return body


def soft_glow(surf, cx, cy, radius, color, peak_alpha, layers=6):
    for i in range(layers, 0, -1):
        r = int(radius * i / layers)
        a = int(peak_alpha * (1 - (i - 1) / layers) ** 1.7)
        if r <= 0 or a <= 0:
            continue
        g = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(g, (*color, a), (r + 1, r + 1), r)
        surf.blit(g, (cx - r - 1, cy - r - 1), special_flags=pygame.BLEND_ADD)


def drop_shadow(surf, rect, radius, blur=6, alpha=120, dy=4):
    for i in range(blur, 0, -1):
        a = int(alpha * (i / blur) ** 2 / blur * 2.2)
        if a <= 0:
            continue
        r = pygame.Rect(rect.x - i, rect.y - i + dy, rect.w + 2 * i, rect.h + 2 * i)
        s = pygame.Surface(r.size, pygame.SRCALPHA)
        pygame.draw.rect(s, (0, 0, 0, a), s.get_rect(), border_radius=radius + i)
        surf.blit(s, r.topleft)


def gradient_text(surf, txt, font_obj, center, top, bot,
                  outline=None, ox_n=2, shadow=True, tracking=0):
    if tracking:
        widths = [font_obj.size(ch)[0] for ch in txt]
        total = sum(widths) + tracking * (len(txt) - 1)
        h = font_obj.get_height()
        strip = pygame.Surface((max(1, total), h), pygame.SRCALPHA)
        x = 0
        for ch, wch in zip(txt, widths):
            strip.blit(font_obj.render(ch, True, WHITE), (x, 0))
            x += wch + tracking
        base = strip
    else:
        base = font_obj.render(txt, True, WHITE)
    w, hh = base.get_size()
    grad = pygame.Surface((w, hh), pygame.SRCALPHA)
    for y in range(hh):
        pygame.draw.line(grad, lerp_color(top, bot, y / max(1, hh - 1)),
                         (0, y), (w, y))
    grad.blit(base, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    r = base.get_rect(center=center)
    if outline:
        out = base.copy()
        out.fill((*outline, 255), special_flags=pygame.BLEND_RGBA_MULT)
        p = ox_n
        for dx, dy in ((-p, 0), (p, 0), (0, -p), (0, p),
                       (-p, -p), (p, -p), (-p, p), (p, p)):
            surf.blit(out, (r.x + dx, r.y + dy))
    if shadow:
        sh = base.copy()
        sh.fill((*NEAR_BLACK, 255), special_flags=pygame.BLEND_RGBA_MULT)
        sh.set_alpha(150)
        surf.blit(sh, (r.x + 1, r.y + 2))
    surf.blit(grad, r.topleft)
    return r


def coin_glyph(surf, cx, cy, r, rim=_GOLD_DEEP):
    d = r * 2
    face = pygame.Surface((d + 2, d + 2), pygame.SRCALPHA)
    c = r + 1
    for yy in range(d + 2):
        for xx in range(d + 2):
            dx, dy = xx - c, yy - c
            if dx * dx + dy * dy > r * r:
                continue
            diag = (dx + dy) / (2 * r) + 0.5
            col = lerp_color((255, 230, 150), (188, 132, 30),
                             max(0.0, min(1.0, diag)) ** 0.85)
            face.set_at((xx, yy), (*col, 255))
    pygame.draw.circle(face, (*rim, 230), (c, c), r, 1)
    if r >= 6:
        sf = _font(max(9, int(r * 1.5)), True)
        sh = sf.render("$", True, (120, 80, 16))
        face.blit(sh, sh.get_rect(center=(c, c)))
        gl = sf.render("$", True, (255, 238, 180))
        face.blit(gl, gl.get_rect(center=(c, c - 1)))
    surf.blit(face, face.get_rect(center=(cx, cy)))


def facet_gem(surf, cx, cy, r, base, deep, mystery=False):
    """Faceted rarity gem — Skybit 4-value diamond cut + specular pip, seated in
    a dark keyline well so it reads on any night ground. The shared secondary
    rarity marker across every concept."""
    seat = pygame.Surface((r * 2 + 8, r * 2 + 8), pygame.SRCALPHA)
    pygame.draw.circle(seat, (0, 0, 0, 150), (r + 4, r + 4), r + 3)
    pygame.draw.circle(seat, (*_GOLD_DEEP, 90), (r + 4, r + 4), r + 3, 1)
    surf.blit(seat, (cx - r - 4, cy - r - 4))
    top, bot = (cx, cy - r), (cx, cy + r)
    left, right = (cx - r, cy), (cx + r, cy)
    ctr = (cx, cy)
    if mystery:
        f1 = lerp_color((196, 214, 226), (214, 202, 224), 0.5)
        hi, mid = lerp_color(f1, WHITE, 0.55), f1
        sh = lerp_color(f1, deep, 0.45)
        dk = lerp_color(deep, NEAR_BLACK, 0.25)
    else:
        hi, mid = lerp_color(base, WHITE, 0.5), base
        sh = lerp_color(base, deep, 0.5)
        dk = lerp_color(deep, NEAR_BLACK, 0.3)
    pygame.draw.polygon(surf, hi, [top, left, ctr])
    pygame.draw.polygon(surf, mid, [top, right, ctr])
    pygame.draw.polygon(surf, sh, [left, bot, ctr])
    pygame.draw.polygon(surf, dk, [right, bot, ctr])
    pygame.draw.polygon(surf, lerp_color(deep, NEAR_BLACK, 0.45),
                        [top, right, bot, left], width=1)
    pr = max(1, r // 4)
    pip = pygame.Surface((pr * 2 + 2, pr * 2 + 2), pygame.SRCALPHA)
    pygame.draw.circle(pip, (255, 255, 255, 245), (pr + 1, pr + 1), pr)
    surf.blit(pip, (cx - pr - r // 3, cy - pr - r // 3), special_flags=pygame.BLEND_ADD)


def chip(surf, cx, cy, text, fg, bg, rim, h=24, coin=False, lock=False,
         rim_w=1):
    """Unified pill chip: gradient body, hairline rim, top sheen, optional
    coin/lock. Returns its rect so callers can prove it clears its neighbours."""
    f = _font(max(12, int(h * 0.56)), True)
    timg = f.render(text, True, fg)
    coin_d = int(h * 0.62)
    pre = (coin_d + 4) if coin else (12 if lock else 0)
    pad = 12
    w = pre + timg.get_width() + pad * 2
    r = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    surf.blit(vgrad_rect(w, h, h // 2, lerp_color(bg, WHITE, 0.18), bg), r.topleft)
    sheen = pygame.Surface((w - 6, h // 2), pygame.SRCALPHA)
    for y in range(h // 2):
        pygame.draw.line(sheen, (255, 255, 255, int(40 * (1 - y / (h // 2)))),
                         (0, y), (w - 6, y))
    sm = pygame.Surface((w - 6, h // 2), pygame.SRCALPHA)
    pygame.draw.rect(sm, (255, 255, 255, 255), sm.get_rect(), border_radius=h // 2)
    sheen.blit(sm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(sheen, (r.x + 3, r.y + 2))
    pygame.draw.rect(surf, rim, r, width=rim_w, border_radius=h // 2)
    x = r.x + pad
    if coin:
        coin_glyph(surf, x + coin_d // 2, cy, coin_d // 2)
        x += coin_d + 4
    elif lock:
        rounded_rect(surf, pygame.Rect(x, cy - 1, 8, 6), 2, fg)
        pygame.draw.arc(surf, fg, (x + 1, cy - 6, 6, 8), 0.2, math.pi - 0.2, 2)
        x += 12
    surf.blit(timg, timg.get_rect(midleft=(x, cy)))
    return r


def metal_rim(surf, rect, radius, deep, bright, w=2):
    pygame.draw.rect(surf, deep, rect, width=w, border_radius=radius)
    pygame.draw.rect(surf, bright, rect.inflate(-w, -w),
                     width=max(1, w // 2), border_radius=max(1, radius - w))


def inner_bevel(surf, rect, radius, light=(255, 245, 220), dark=(0, 0, 0),
                la=90, da=80):
    inset = 3
    brad = max(1, radius - inset)
    for col, alpha, tl in ((light, la, True), (dark, da, False)):
        layer = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(layer, (*col, alpha),
                         (inset, inset, rect.w - 2 * inset, rect.h - 2 * inset),
                         width=2, border_radius=brad)
        mask = pygame.Surface(rect.size, pygame.SRCALPHA)
        tri = ([(0, 0), (rect.w, 0), (0, rect.h)] if tl
               else [(rect.w, 0), (rect.w, rect.h), (0, rect.h)])
        pygame.draw.polygon(mask, (255, 255, 255, 255), tri)
        layer.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        surf.blit(layer, rect.topleft)


def gold_rule(surf, x0, x1, y, gold, peak=170):
    w = x1 - x0
    line = pygame.Surface((w, 3), pygame.SRCALPHA)
    for sx in range(w):
        hx = abs(sx - w / 2) / (w / 2)
        a = int(peak * (1.0 - hx ** 1.6))
        if a <= 0:
            continue
        line.set_at((sx, 1), (*gold, a))
    surf.blit(line, (x0, y - 1))


def cabochon(surf, cx, cy, r, glass_lo=(30, 28, 40), glass_hi=(6, 6, 12),
             ring=_GOLD_DEEP, ring_a=70):
    """Round glass cabochon well: a domed dark glass disc the thumbnail sits
    'under'. Each concept tints glass_lo/hi + the rim metal, so the cabochon
    re-reads (porthole, frost, enamel cell, velvet bezel) while keeping one
    silhouette. Adds a crisp top-left specular so it always reads as DOMED glass."""
    disc = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
    c = r + 2
    for i in range(r, 0, -1):
        col = lerp_color(glass_lo, glass_hi, (i / r) ** 1.3)
        pygame.draw.circle(disc, (*col, 255), (c, c), i)
    # inner shadow ring + thin metal seat
    pygame.draw.circle(disc, (0, 0, 0, 150), (c, c), r, 2)
    pygame.draw.circle(disc, (*ring, ring_a), (c, c), r - 1, 1)
    # specular highlight crescent, upper-left — the glass dome tell
    hl = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
    pygame.draw.circle(hl, (255, 255, 255, 60), (c - r // 3, c - r // 3), max(2, r // 2))
    hm = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
    pygame.draw.circle(hm, (255, 255, 255, 255), (c, c), r - 2)
    hl.blit(hm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    disc.blit(hl, (0, 0))
    surf.blit(disc, (cx - c, cy - c))


def inset_disc(surf, cx, cy, r, tint=(6, 6, 12)):
    cabochon(surf, cx, cy, r, glass_lo=(30, 28, 40), glass_hi=tint)


# ── concept base ──────────────────────────────────────────────────────────────
# Geometry is fixed here so every concept inherits defect-free spacing. The
# card is a STRICT THREE-BAND tile; concepts only paint material into the slots.

TIER_ORDER = ("common", "rare", "epic", "legendary")

# Card metrics — a strict three-band tile so the bands never touch, sized so a
# full 2x4 grid (8 cards) still fits the 360x640 canvas with page + back rows.
#   CABO band : disc centred at CY_DISC, radius R_DISC  (spans 12..52)
#   NAME band : own clear lane at Y_NAME (18px below the disc, never on it)
#   CHIP band : own lane at Y_CHIP (below the name; chip h=20 -> 11px clear)
CARD_W, CARD_H, GAP = 162, 104, 7
R_DISC = 22
CY_DISC = 33          # disc spans 11..55 vertically
Y_NAME = 73           # name centre — 18px clear of disc bottom
Y_CHIP = 92           # chip centre — clear of name; chip h=20 -> top at 82
GEM_R = 7
GRID_TOP = 138        # below the header lane (title/balance/tabs all above)


class Concept:
    NAME = "?"
    DESC = ""
    BG = ((10, 10, 20), (20, 20, 40))
    STARS = True
    star_t = 2.0
    RARITY = {}
    MYSTERY = {"gem": (220, 226, 236), "glow": (188, 206, 228), "deep": (86, 94, 116)}
    GOLD = _GOLD_BRIGHT
    GOLD_PALE = _GOLD_PALE
    GOLD_DEEP = _GOLD_DEEP
    TITLE_TOP = (255, 240, 180)
    TITLE_BOT = (236, 170, 60)
    TITLE_OUT = _RED_OUTLINE
    CREAM = UI_CREAM
    TABS = ("PARROTS", "ANIMALS", "COSTUMES", "PARCELS")
    ACTIVE_TAB = 1
    # concept glass + frame material (overridden)
    GLASS_LO = (30, 28, 44)
    GLASS_HI = (6, 6, 14)
    CABO_LO = (24, 22, 40)
    CABO_HI = (5, 5, 12)
    CABO_RING = _GOLD_DEEP
    FRAME_DEEP = (60, 46, 18)
    FRAME_BRIGHT = _GOLD_BRIGHT
    CARD_T = (40, 36, 70)
    CARD_B = (16, 14, 36)
    NAME_COL = _GOLD_PALE

    def __init__(self):
        self._stars = _seeded_stars()

    # --- background -----------------------------------------------------------
    def bg(self, surf):
        stops = self.BG
        n = len(stops)
        for y in range(H):
            f = y / (H - 1)
            seg = min(n - 2, int(f * (n - 1)))
            local = (f * (n - 1)) - seg
            pygame.draw.line(surf, lerp_color(stops[seg], stops[seg + 1], local),
                             (0, y), (W - 1, y))
        if self.STARS:
            _draw_overlay_stars(surf, self._stars, self.star_t)

    # --- rarity helpers -------------------------------------------------------
    def tier_pal(self, sid, secret):
        if secret:
            return self.MYSTERY
        return self.RARITY[_rarity(sid)]

    # --- chip palette ---------------------------------------------------------
    def chip_colors(self, state):
        return {
            "price": (self.GOLD_PALE, self.GOLD_DEEP, (*self.GOLD, 160)),
            "equip": (self.CREAM, (96, 74, 24), (*self.GOLD, 160)),
            "equipped": ((10, 30, 14), (84, 196, 112), (200, 255, 210)),
            "locked": ((150, 166, 190), (40, 46, 62), (88, 102, 132)),
        }[state]

    def state_chip(self, surf, sid, cx, cy, equipped, secret, h=20):
        if equipped:
            fg, bg, rim = self.chip_colors("equipped")
            return chip(surf, cx, cy, "EQUIPPED", fg, bg, rim, h=h)
        price = _cost(sid)
        if BALANCE >= price:
            fg, bg, rim = self.chip_colors("price")
            return chip(surf, cx, cy, f"{price:,}", fg, bg, rim, h=h, coin=True)
        fg, bg, rim = self.chip_colors("locked")
        return chip(surf, cx, cy, f"{price:,}", fg, bg, rim, h=h, lock=True)

    # --- the SHARED defect-free card --------------------------------------------
    # Subclasses customise look via hooks, never via geometry, so spacing is
    # guaranteed: paint_body, paint_cabo_frame, ornament are the only overrides.
    def paint_body(self, surf, rect, pal, secret):
        """Card backing + bezel. Default: glass panel + metal rim."""
        surf.blit(vgrad_rect(rect.w, rect.h, 16, self.CARD_T, self.CARD_B, 252),
                  rect.topleft)
        sheen = pygame.Surface((rect.w - 12, 16), pygame.SRCALPHA)
        for y in range(16):
            pygame.draw.line(sheen, (255, 255, 255, int(34 * (1 - y / 16))),
                             (0, y), (rect.w - 12, y))
        sm = pygame.Surface((rect.w - 12, 16), pygame.SRCALPHA)
        pygame.draw.rect(sm, (255, 255, 255, 255), sm.get_rect(),
                         border_top_left_radius=12, border_top_right_radius=12)
        sheen.blit(sm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        surf.blit(sheen, (rect.x + 6, rect.y + 4))
        metal_rim(surf, rect, 16, self.FRAME_DEEP, (*self.FRAME_BRIGHT, 180), w=2)

    def paint_cabo(self, surf, cx, cy, pal, secret):
        cabochon(surf, cx, cy, R_DISC, self.CABO_LO, self.CABO_HI,
                 ring=self.CABO_RING)

    def ornament(self, surf, rect, pal, secret):
        """Per-concept signature detail in the SAFE zones only (corners, behind
        cabochon). Must not encroach the name or chip lanes."""
        pass

    def card(self, surf, sid, rect, equipped):
        secret = _is_secret(sid)
        pal = self.tier_pal(sid, secret)
        drop_shadow(surf, rect, 16, blur=6, alpha=150)
        self.paint_body(surf, rect, pal, secret)
        self.ornament(surf, rect, pal, secret)
        # BAND A — cabochon. Aura kept tight to the disc so it never bleeds into
        # the name lane below.
        cx, cy = rect.centerx, rect.y + CY_DISC
        soft_glow(surf, cx, cy, R_DISC + 4, pal["glow"], 64, layers=5)
        self.paint_cabo(surf, cx, cy, pal, secret)
        if secret:
            _draw_qmark(surf, cx, cy, R_DISC + 7, self.CREAM, NEAR_BLACK, thick=2)
            name = "???"
        else:
            t = thumb(sid, R_DISC * 1.7)
            surf.blit(t, t.get_rect(center=(cx, cy)))
            name = _name(sid)
        # corner GEM — seated with margin; never over disc or bezel.
        gx, gy = rect.right - 15, rect.y + 15
        facet_gem(surf, gx, gy, GEM_R, pal["gem"], pal["deep"], mystery=secret)
        # BAND B — NAME in its own clear lane. Auto-fit so long names never
        # collide the card edges (still in their own band vertically).
        self._fit_name(surf, name, rect.centerx, rect.y + Y_NAME, rect.w - 24)
        # BAND C — price / state chip in its own lane.
        self.state_chip(surf, sid, rect.centerx, rect.y + Y_CHIP, equipped, secret)
        if equipped:
            self._equipped_ring(surf, rect)

    def _fit_name(self, surf, name, cx, cy, max_w):
        sz = 14
        f = _font(sz, True)
        while f.size(name)[0] > max_w and sz > 9:
            sz -= 1
            f = _font(sz, True)
        nimg = f.render(name, True, self.NAME_COL)
        nsh = f.render(name, True, NEAR_BLACK); nsh.set_alpha(150)
        nr = nimg.get_rect(center=(cx, cy))
        surf.blit(nsh, (nr.x + 1, nr.y + 1))
        surf.blit(nimg, nr)

    def _equipped_ring(self, surf, rect):
        # Gold ring traces the bezel only — it never reaches into the name lane.
        halo = pygame.Surface((rect.w + 16, rect.h + 16), pygame.SRCALPHA)
        for k in range(4, 0, -1):
            pygame.draw.rect(halo, (*self.GOLD, int(20 * k / 4)),
                             (8 - k, 8 - k, rect.w + 2 * k, rect.h + 2 * k),
                             width=2, border_radius=16 + k)
        surf.blit(halo, (rect.x - 8, rect.y - 8), special_flags=pygame.BLEND_ADD)
        pygame.draw.rect(surf, self.GOLD, rect, width=2, border_radius=16)

    # --- subclasses implement chrome -----------------------------------------
    def header(self, surf):
        raise NotImplementedError

    def back(self, surf):
        back_pill(self, surf)

    def modal(self, surf, sid):
        raise NotImplementedError


# -----------------------------------------------------------------------------
# Shared store composer. Header lives entirely above GRID_TOP; page controls and
# BACK live below the last row with clear gaps — defects 5/6/7 fixed structurally.
# -----------------------------------------------------------------------------

def render_store(concept):
    surf = pygame.Surface((W, H))
    concept.bg(surf)
    concept.header(surf)
    base_x = (W - (CARD_W * 2 + GAP)) // 2
    for idx, sid in enumerate(SAMPLE_IDS):
        x = base_x + (idx % 2) * (CARD_W + GAP)
        y = GRID_TOP + (idx // 2) * (CARD_H + GAP)
        concept.card(surf, sid, pygame.Rect(x, y, CARD_W, CARD_H),
                     sid == EQUIPPED_ID)
    # page controls — placed on their OWN row beneath the grid, above BACK.
    grid_bottom = GRID_TOP + 4 * CARD_H + 3 * GAP
    cy = grid_bottom + 14
    lbl = _font(12, True).render("PAGE  1 / 3", True, concept.GOLD_PALE)
    surf.blit(lbl, lbl.get_rect(center=(W // 2, cy)))
    for gx, glyph in ((base_x + 18, "<"), (base_x + CARD_W * 2 + GAP - 18, ">")):
        r = pygame.Rect(0, 0, 30, 20); r.center = (gx, cy)
        surf.blit(vgrad_rect(r.w, r.h, 11, (44, 34, 20), (24, 18, 10)), r.topleft)
        pygame.draw.rect(surf, (*concept.GOLD, 190), r, width=1, border_radius=11)
        g = _font(15, True).render(glyph, True, concept.GOLD_PALE)
        surf.blit(g, g.get_rect(center=(gx, cy - 1)))
    concept.back(surf)
    return surf


# Shared header: three vertical lanes — TITLE / BALANCE CAPSULE / TAB STRIP —
# spaced so the coin never overlaps the digits or the title, and the underline
# clears the first card row (GRID_TOP = 150).
def header_titlebar(concept, surf, title="STORE", title_y=28,
                    balance_y=66, tab_y=112, tracking=2):
    f = _font(28, True)
    gradient_text(surf, title, f, (W // 2, title_y),
                  concept.TITLE_TOP, concept.TITLE_BOT,
                  outline=concept.TITLE_OUT, tracking=tracking)
    balance_capsule(concept, surf, W // 2, balance_y)
    underline_tabs(concept, surf, tab_y)


def balance_capsule(concept, surf, cx, y, cap_top=(44, 32, 18),
                    cap_bot=(20, 14, 8)):
    # Sized so the coin sits in a dedicated left cell with a real gap before the
    # digits — coin never overlaps the value (defect 5).
    val = f"{BALANCE:,}"
    vf = _font(20, True)
    vw = vf.size(val)[0]
    coin_d, gapc, padl, padr = 22, 12, 12, 16
    w = padl + coin_d + gapc + vw + padr
    cap = pygame.Rect(cx - w // 2, y - 17, w, 34)
    drop_shadow(surf, cap, 17, blur=4, alpha=90)
    surf.blit(vgrad_rect(cap.w, cap.h, 17, cap_top, cap_bot, 252), cap.topleft)
    pygame.draw.rect(surf, (0, 0, 0, 120), cap.inflate(-2, -2), width=1, border_radius=16)
    pygame.draw.rect(surf, (*concept.GOLD, 200), cap, width=1, border_radius=17)
    x = cap.x + padl
    soft_glow(surf, x + coin_d // 2, y, coin_d + 2, (255, 206, 92), 100, layers=5)
    coin_glyph(surf, x + coin_d // 2, y, coin_d // 2)
    x += coin_d + gapc
    gradient_text(surf, val, vf, (x + vw // 2, y), (255, 246, 196), (236, 170, 60))


def underline_tabs(concept, surf, tab_y):
    f = _font(12, True)
    pad, gap = 8, 7
    widths = [f.size(t)[0] + 2 * pad for t in concept.TABS]
    total = sum(widths) + gap * (len(concept.TABS) - 1)
    while total > W - 12 and pad > 4:
        pad -= 1
        gap = max(4, gap - 1)
        widths = [f.size(t)[0] + 2 * pad for t in concept.TABS]
        total = sum(widths) + gap * (len(concept.TABS) - 1)
    x = (W - total) // 2
    track = pygame.Rect(x - 8, tab_y - 13, total + 16, 26)
    ts = pygame.Surface(track.size, pygame.SRCALPHA)
    pygame.draw.rect(ts, (8, 8, 16, 96), ts.get_rect(), border_radius=13)
    surf.blit(ts, track.topleft)
    for i, t in enumerate(concept.TABS):
        w = widths[i]
        active = (i == concept.ACTIVE_TAB)
        col = concept.GOLD_PALE if active else (198, 192, 206)
        timg = f.render(t, True, col)
        if not active:
            timg.set_alpha(205)
        tr = timg.get_rect(center=(x + w // 2, tab_y))
        surf.blit(timg, tr)
        if active:
            ur = pygame.Rect(tr.x - 2, tab_y + 11, tr.w + 4, 3)
            uglow = pygame.Surface((ur.w + 12, 10), pygame.SRCALPHA)
            for gy in range(10):
                pygame.draw.line(uglow, (*concept.GOLD, int(40 * (1 - gy / 10))),
                                 (0, gy), (ur.w + 12, gy))
            surf.blit(uglow, (ur.x - 6, ur.y - 2), special_flags=pygame.BLEND_ADD)
            rounded_rect(surf, ur, 2, concept.GOLD)
        x += w + gap


def back_pill(concept, surf, body_top=(40, 32, 56), body_bot=(22, 16, 38)):
    r = pygame.Rect(0, 0, 160, 34); r.center = (W // 2, H - 22)
    drop_shadow(surf, r, 17, blur=4, alpha=90)
    surf.blit(vgrad_rect(r.w, r.h, 17, body_top, body_bot, 240), r.topleft)
    pygame.draw.rect(surf, (*concept.GOLD, 185), r, width=1, border_radius=17)
    timg = _font(17, True).render("BACK", True, concept.GOLD_PALE)
    surf.blit(timg, timg.get_rect(center=r.center))


# Shared, defect-free buy-confirmation modal. Stage / name / rarity / chip /
# buttons are each in their own vertical lane; the gem is seated in the stage
# corner with margin; secret '?' glyph and '???' label are separated.
def modal_skeleton(concept, surf, sid, panel_top, panel_bot,
                   frame_deep, frame_bright, head_col):
    scrim = pygame.Surface((W, H), pygame.SRCALPHA)
    scrim.fill((4, 4, 10, 185))
    surf.blit(scrim, (0, 0))
    secret = _is_secret(sid)
    tier = _rarity(sid)
    pal = concept.MYSTERY if secret else concept.RARITY[tier]
    pw, ph = 258, 312
    panel = pygame.Rect((W - pw) // 2, (H - ph) // 2, pw, ph)
    drop_shadow(surf, panel, 18, blur=8, alpha=175)
    surf.blit(vgrad_rect(pw, ph, 18, panel_top, panel_bot, 255), panel.topleft)
    metal_rim(surf, panel, 18, frame_deep, frame_bright, w=2)
    inner_bevel(surf, panel, 18, la=70, da=70)
    cx = panel.centerx
    head = _font(13, True).render("CONFIRM PURCHASE", True, head_col)
    surf.blit(head, head.get_rect(center=(cx, panel.y + 26)))
    gold_rule(surf, panel.x + 28, panel.right - 28, panel.y + 44, concept.GOLD)
    # STAGE — the concept cabochon presented large.
    disc_cy = panel.y + 104
    soft_glow(surf, cx, disc_cy, 46, pal["glow"], 78, layers=6)
    cabochon(surf, cx, disc_cy, 42, concept.CABO_LO, concept.CABO_HI,
             ring=concept.CABO_RING)
    if secret:
        _draw_qmark(surf, cx, disc_cy, 54, concept.CREAM, NEAR_BLACK, thick=3)
        name = "???"
    else:
        t = thumb(sid, 72)
        surf.blit(t, t.get_rect(center=(cx, disc_cy)))
        name = _name(sid)
    facet_gem(surf, cx + 40, disc_cy - 38, 8, pal["gem"], pal["deep"], mystery=secret)
    nimg = _font(18, True).render(name, True, concept.GOLD)
    surf.blit(nimg, nimg.get_rect(center=(cx, panel.y + 176)))
    rword = "MYSTERY" if secret else tier.upper()
    rimg = _font(11, True).render(rword, True, pal["gem"])
    surf.blit(rimg, rimg.get_rect(center=(cx, panel.y + 196)))
    price = _cost(sid)
    fg, bg, rim = concept.chip_colors("price")
    chip(surf, cx, panel.y + 222, f"{price:,}", fg, bg, rim, h=28, coin=True)
    # buttons
    bw, bh, gut = 104, 38, 16
    by = panel.bottom - 30
    nx = cx - (bw * 2 + gut) // 2
    cancel = pygame.Rect(nx, by - bh // 2, bw, bh)
    buy = pygame.Rect(nx + bw + gut, by - bh // 2, bw, bh)
    surf.blit(vgrad_rect(bw, bh, bh // 2, (70, 62, 80), (44, 38, 56)), cancel.topleft)
    pygame.draw.rect(surf, (126, 116, 138), cancel, width=1, border_radius=bh // 2)
    ct = _font(14, True).render("CANCEL", True, concept.CREAM)
    surf.blit(ct, ct.get_rect(center=cancel.center))
    bglow = pygame.Surface((bw + 10, bh + 10), pygame.SRCALPHA)
    for k in range(4, 0, -1):
        pygame.draw.rect(bglow, (*concept.GOLD, int(22 * k / 4)),
                         (5 - k, 5 - k, bw + 2 * k, bh + 2 * k),
                         border_radius=bh // 2 + k)
    surf.blit(bglow, (buy.x - 5, buy.y - 5), special_flags=pygame.BLEND_ADD)
    surf.blit(vgrad_rect(bw, bh, bh // 2, lerp_color(concept.GOLD, WHITE, 0.2),
                         concept.GOLD_DEEP), buy.topleft)
    pygame.draw.rect(surf, concept.GOLD_PALE, buy, width=1, border_radius=bh // 2)
    yt = _font(15, True).render("BUY", True, (40, 24, 8))
    surf.blit(yt, yt.get_rect(center=buy.center))


# ── detail-zoom: real-metric cards magnified so spacing can be judged close ────
def render_detail(concept):
    cw, ch, g, pad = CARD_W, CARD_H, 14, 16
    cols = len(DETAIL_IDS)
    strip_w = cw * cols + g * (cols - 1) + pad * 2
    strip_h = ch + pad * 2 + 24
    strip = pygame.Surface((strip_w, strip_h))
    strip.blit(vgrad_rect(strip_w, strip_h, 0, concept.BG[0], concept.BG[-1], 255), (0, 0))
    if concept.STARS:
        _draw_overlay_stars(strip, [(x % strip_w, y % strip_h, r, p)
                                    for (x, y, r, p) in concept._stars[:30]],
                            concept.star_t)
    lbl = _font(12, True).render("CABOCHON  /  NAME  /  CHIP  /  GEM", True, concept.GOLD_PALE)
    strip.blit(lbl, (pad, 6))
    for i, sid in enumerate(DETAIL_IDS):
        x = pad + i * (cw + g)
        y = 24 + pad
        concept.card(strip, sid, pygame.Rect(x, y, cw, ch), sid == EQUIPPED_ID)
    scale = 1.35
    return pygame.transform.smoothscale(
        strip, (int(strip_w * scale), int(strip_h * scale)))


# ── compose the comparison sheet ──────────────────────────────────────────────
def build_sheet():
    from concepts import CONCEPTS
    cols = []
    for concept in CONCEPTS:
        store = render_store(concept)
        modal = render_store(concept)
        concept.modal(modal, "skin_phoenix")
        detail = render_detail(concept)
        cols.append((concept, store, modal, detail))

    pad = 22
    gap_v = 16
    col_w = max(W, max(c[3].get_width() for c in cols))
    label_h = 60
    col_h = label_h + H * 2 + cols[0][3].get_height() + gap_v * 3
    sheet_w = pad + len(cols) * (col_w + pad)
    sheet_h = pad + col_h + pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((18, 16, 24))

    cx = pad
    for concept, store, modal, detail in cols:
        col_cx = cx + col_w // 2
        nm = _font(24, True).render(concept.NAME, True, (255, 236, 180))
        sheet.blit(nm, nm.get_rect(center=(col_cx, pad + 16)))
        ds = _font(13, True).render(concept.DESC, True, (190, 186, 200))
        sheet.blit(ds, ds.get_rect(center=(col_cx, pad + 40)))
        y = pad + label_h
        for img, tag in ((store, "STORE"), (modal, "BUY CONFIRM"),
                         (detail, "DETAIL ZOOM")):
            ix = cx + (col_w - img.get_width()) // 2
            fr = pygame.Rect(ix - 2, y - 2, img.get_width() + 4, img.get_height() + 4)
            pygame.draw.rect(sheet, (60, 56, 70), fr, border_radius=6)
            sheet.blit(img, (ix, y))
            tg = _font(11, True).render(tag, True, (140, 138, 152))
            sheet.blit(tg, (cx + 2, y + img.get_height() + 1))
            y += img.get_height() + gap_v
        cx += col_w + pad

    out = os.path.join(_HERE, "concepts.png")
    pygame.image.save(sheet, out)
    print("saved", out, sheet.get_size())


if __name__ == "__main__":
    build_sheet()
