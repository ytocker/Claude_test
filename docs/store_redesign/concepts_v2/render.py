"""
Coin Store redesign — concepts_v2 selection harness.

Headless (SDL dummy) renderer that draws FIVE genuinely distinct high-end
store concepts, each loyal to Skybit's established visual language (tropical
macaw, warm-gold coins, day/night sky, sandstone pillars, casual-arcade joy),
and composes ONE comparison sheet. Real catalog items + real procedural
thumbnails are used so the explorations look like the shipping game.

This is a SELECTION sheet only — no convergence, no integration. Each concept
is a complete look that could ship: a full 360x640 store screen (a), a
buy-confirmation modal (b), and a 2-3 card detail zoom (c).
"""
import os
import sys
import math

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

# Repo root on the path so we render against the REAL game modules.
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
# Some checkouts nest the package one level down; cover both.
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

# ── a curated 8-card sample spanning all four tiers + secret + free-default ───
# Picked from the real catalog so every concept's grid shows the full rarity
# ladder, an equipped card, and a masked secret card.
SAMPLE_IDS = [
    "skin_bluegold",     # common  (parrot)
    "skin_owl",          # rare    (animal)   -> shown EQUIPPED
    "skin_dragon",       # epic    (animal)
    "skin_kitsune",      # legendary
    "skin_pharaoh",      # common  (costume)
    "skin_phoenix",      # epic
    "skin_aurora_stag",  # legendary
    "skin_ufo",          # secret (masked ???)
]
EQUIPPED_ID = "skin_owl"
SECRET_ID = "skin_ufo"
BALANCE = 14250

# Detail-zoom trio: one common, one epic, one secret so tier + chip + gem read.
DETAIL_IDS = ["skin_pharaoh", "skin_phoenix", "skin_ufo"]


def _cost(sid):
    return store_catalog.cost(sid) if store_catalog.exists(sid) else 0


def _rarity(sid):
    return store_catalog.rarity(sid)


def _name(sid):
    return store_catalog.name(sid) if store_catalog.exists(sid) else "DEFAULT"


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
    """Rounded vertical-gradient panel (store-convention arg order:
    w, h, radius, top, bot, alpha)."""
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
    """Vertical-gradient text with optional pixel outline + drop shadow.
    `tracking` adds inter-letter spacing (renders glyph-by-glyph) for the
    refined display-type look the brief asks for."""
    if tracking:
        # Measure total width with tracking.
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
    """Skybit's flat-gold coin: diagonal-bevel disc + stamped '$'. The single
    coin used everywhere (chip, balance, modal), per the locked spec."""
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
    """Faceted rarity gem — the Skybit 4-value diamond cut + specular pip,
    seated in a dark keyline well. Reused across concepts (the shared rarity
    SECONDARY marker), so the family stays coherent."""
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
    coin/lock. Each concept passes its own fg/bg/rim so the chip family adapts
    to its palette while keeping one silhouette."""
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


# ── concept colour systems ────────────────────────────────────────────────────
# Each concept owns its own background, frame material, and per-tier rarity
# triplet (gem/glow/deep). Tiers ladder by HUE *and* VALUE (colourblind-safe)
# inside every concept's own palette world.

LABELS = {}  # concept_key -> (name, descriptor)


# Helper for a bevelled metal frame rim (used by several concepts).
def metal_rim(surf, rect, radius, deep, bright, w=2):
    pygame.draw.rect(surf, deep, rect, width=w, border_radius=radius)
    pygame.draw.rect(surf, bright, rect.inflate(-w, -w),
                     width=max(1, w // 2), border_radius=max(1, radius - w))


def inner_bevel(surf, rect, radius, light=(255, 245, 220), dark=(0, 0, 0),
                la=90, da=80):
    """Diagonal-split inner bevel: pale top-left, dark bottom-right — sells the
    raised tile across every concept."""
    inset = 3
    band = pygame.Rect(rect.x + inset, rect.y + inset,
                       rect.w - 2 * inset, rect.h - 2 * inset)
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


# =============================================================================
# Each concept is a class with:
#   bg(surf)               — full-screen background
#   RARITY[tier]           — {gem, glow, deep}
#   chip_colors(state)     — fg/bg/rim per chip state
#   card(surf, sid, rect, equipped) — one grid card
#   header(surf)           — title + balance + tabs (drawn by render_store)
#   modal(surf, sid)       — buy-confirmation
# A thin base provides the parts that are genuinely shared.
# =============================================================================

TIER_ORDER = ("common", "rare", "epic", "legendary")


class Concept:
    NAME = "?"
    DESC = ""
    BG = ((10, 10, 20), (20, 20, 40))
    STARS = True
    star_t = 2.0
    # rarity: per-tier gem / glow / deep
    RARITY = {}
    MYSTERY = {"gem": (214, 218, 224), "glow": (176, 196, 214), "deep": (78, 84, 98)}
    # palette accents
    GOLD = _GOLD_BRIGHT
    GOLD_PALE = _GOLD_PALE
    GOLD_DEEP = _GOLD_DEEP
    TITLE_TOP = (255, 240, 180)
    TITLE_BOT = (236, 170, 60)
    TITLE_OUT = _RED_OUTLINE
    CREAM = UI_CREAM
    TABS = ("PARROTS", "ANIMALS", "COSTUMES", "PARCELS")
    ACTIVE_TAB = 1

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
        # default warm-gold family; concepts override.
        return {
            "price": (self.GOLD_PALE, self.GOLD_DEEP, (*self.GOLD, 160)),
            "equip": (self.CREAM, (96, 74, 24), (*self.GOLD, 160)),
            "equipped": ((10, 30, 14), (84, 196, 112), (200, 255, 210)),
            "locked": ((150, 166, 190), (40, 46, 62), (88, 102, 132)),
        }[state]

    def state_chip(self, surf, sid, cx, cy, equipped, secret, h=24):
        if equipped:
            fg, bg, rim = self.chip_colors("equipped")
            chip(surf, cx, cy, "EQUIPPED", fg, bg, rim, h=h)
            return
        price = _cost(sid)
        if BALANCE >= price:
            fg, bg, rim = self.chip_colors("price")
            chip(surf, cx, cy, f"{price:,}", fg, bg, rim, h=h, coin=True)
        else:
            fg, bg, rim = self.chip_colors("locked")
            chip(surf, cx, cy, f"{price:,}", fg, bg, rim, h=h, lock=True)

    # --- subclasses implement these ------------------------------------------
    def card(self, surf, sid, rect, equipped):
        raise NotImplementedError

    def header(self, surf):
        raise NotImplementedError

    def modal(self, surf, sid):
        raise NotImplementedError

    def detail_card(self, surf, sid, rect):
        # Default: reuse the grid card at a larger size.
        self.card(surf, sid, rect, sid == EQUIPPED_ID)


# -----------------------------------------------------------------------------
# Generic store-screen composer used by every concept. It lays out the header,
# the 2x4 grid (the concept draws each card), the page controls, and BACK; the
# concept supplies the chrome look.
# -----------------------------------------------------------------------------
CARD_W, CARD_H, GAP, GRID_TOP = 162, 100, 8, 132


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
    # page controls
    cy = GRID_TOP + 4 * (CARD_H + GAP) + 4
    lbl = _font(12, True).render("PAGE  1 / 3", True, concept.GOLD_PALE)
    surf.blit(lbl, lbl.get_rect(center=(W // 2, cy)))
    for gx, glyph in ((base_x + 16, "<"), (base_x + CARD_W * 2 + GAP - 16, ">")):
        r = pygame.Rect(0, 0, 30, 22); r.center = (gx, cy)
        surf.blit(vgrad_rect(r.w, r.h, 11, (44, 34, 20), (24, 18, 10)), r.topleft)
        pygame.draw.rect(surf, (*concept.GOLD, 190), r, width=1, border_radius=11)
        g = _font(15, True).render(glyph, True, concept.GOLD_PALE)
        surf.blit(g, g.get_rect(center=(gx, cy - 1)))
    # BACK
    concept.back(surf)
    return surf


# A shared header layout (title + balance capsule + underline tabs). Concepts
# call this with their own colours, or override header() entirely for a
# distinct structural motif.
def header_titlebar(concept, surf, title="STORE", tab_y=110, balance_y=64):
    # title
    f = _font(28, True)
    gradient_text(surf, title, f, (W // 2, 30),
                  concept.TITLE_TOP, concept.TITLE_BOT,
                  outline=concept.TITLE_OUT, tracking=2)
    # balance capsule
    balance_capsule(concept, surf, W // 2, balance_y)
    # tabs
    underline_tabs(concept, surf, tab_y)


def balance_capsule(concept, surf, cx, y, cap_top=(44, 32, 18),
                    cap_bot=(20, 14, 8)):
    val = f"{BALANCE:,}"
    vf = _font(22, True)
    vw = vf.size(val)[0]
    coin_d, gapc, pad = 24, 9, 16
    w = coin_d + gapc + vw + pad * 2
    cap = pygame.Rect(cx - w // 2, y - 18, w, 36)
    drop_shadow(surf, cap, 18, blur=4, alpha=90)
    surf.blit(vgrad_rect(cap.w, cap.h, 18, cap_top, cap_bot, 252), cap.topleft)
    pygame.draw.rect(surf, (0, 0, 0, 120), cap.inflate(-2, -2), width=1, border_radius=17)
    pygame.draw.rect(surf, (*concept.GOLD, 200), cap, width=1, border_radius=18)
    x = cap.x + pad
    soft_glow(surf, x + coin_d // 2, y, coin_d + 4, (255, 206, 92), 110, layers=5)
    coin_glyph(surf, x + coin_d // 2, y, coin_d // 2)
    x += coin_d + gapc
    gradient_text(surf, val, vf, (x + vw // 2, y), (255, 246, 196), (236, 170, 60))


def underline_tabs(concept, surf, tab_y):
    f = _font(12, True)
    # Fit the strip to the canvas: shrink padding so all tabs read in full
    # (no clipped edge labels) at 360px.
    pad, gap = 8, 7
    widths = [f.size(t)[0] + 2 * pad for t in concept.TABS]
    total = sum(widths) + gap * (len(concept.TABS) - 1)
    while total > W - 12 and pad > 4:
        pad -= 1
        gap = max(4, gap - 1)
        widths = [f.size(t)[0] + 2 * pad for t in concept.TABS]
        total = sum(widths) + gap * (len(concept.TABS) - 1)
    x = (W - total) // 2
    # Faint dark track behind the whole strip so labels stay legible on any
    # concept background (bright sky, busy stone, glass).
    track = pygame.Rect(x - 8, tab_y - 12, total + 16, 24)
    ts = pygame.Surface(track.size, pygame.SRCALPHA)
    pygame.draw.rect(ts, (8, 8, 16, 90), ts.get_rect(), border_radius=12)
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
            ur = pygame.Rect(tr.x - 2, tab_y + 10, tr.w + 4, 3)
            uglow = pygame.Surface((ur.w + 12, 10), pygame.SRCALPHA)
            for gy in range(10):
                pygame.draw.line(uglow, (*concept.GOLD, int(40 * (1 - gy / 10))),
                                 (0, gy), (ur.w + 12, gy))
            surf.blit(uglow, (ur.x - 6, ur.y - 2), special_flags=pygame.BLEND_ADD)
            rounded_rect(surf, ur, 2, concept.GOLD)
        x += w + gap


def back_pill(concept, surf, body_top=(40, 32, 56), body_bot=(22, 16, 38)):
    r = pygame.Rect(0, 0, 160, 36); r.center = (W // 2, H - 26)
    drop_shadow(surf, r, 18, blur=4, alpha=90)
    surf.blit(vgrad_rect(r.w, r.h, 18, body_top, body_bot, 240), r.topleft)
    pygame.draw.rect(surf, (*concept.GOLD, 185), r, width=1, border_radius=18)
    timg = _font(18, True).render("BACK", True, concept.GOLD_PALE)
    surf.blit(timg, timg.get_rect(center=r.center))


# A shared, beautiful modal skeleton; the concept tints the chrome.
def modal_skeleton(concept, surf, sid, panel_top, panel_bot,
                   frame_deep, frame_bright, stage_top, stage_bot,
                   head_col):
    scrim = pygame.Surface((W, H), pygame.SRCALPHA)
    scrim.fill((4, 4, 10, 180))
    surf.blit(scrim, (0, 0))
    secret = sid == SECRET_ID
    tier = _rarity(sid)
    pal = concept.MYSTERY if secret else concept.RARITY[tier]
    pw, ph = 256, 300
    panel = pygame.Rect((W - pw) // 2, (H - ph) // 2, pw, ph)
    drop_shadow(surf, panel, 18, blur=8, alpha=170)
    surf.blit(vgrad_rect(pw, ph, 18, panel_top, panel_bot, 255), panel.topleft)
    metal_rim(surf, panel, 18, frame_deep, frame_bright, w=2)
    inner_bevel(surf, panel, 18)
    cx = panel.centerx
    head = _font(13, True).render("CONFIRM PURCHASE", True, head_col)
    surf.blit(head, head.get_rect(center=(cx, panel.y + 24)))
    # soft gold rule
    gold_rule(surf, panel.x + 28, panel.right - 28, panel.y + 40, concept.GOLD)
    # stage
    stage = pygame.Rect(cx - 50, panel.y + 54, 100, 100)
    surf.blit(vgrad_rect(stage.w, stage.h, 12, stage_top, stage_bot), stage.topleft)
    pygame.draw.rect(surf, (0, 0, 0, 150), stage, width=1, border_radius=12)
    disc_cy = stage.y + 42
    soft_glow(surf, cx, disc_cy, 40, pal["glow"], 70, layers=5)
    inset_disc(surf, cx, disc_cy, 38)
    if secret:
        _draw_qmark(surf, cx, disc_cy, 50, concept.CREAM, NEAR_BLACK, thick=3)
        name = "???"
    else:
        t = thumb(sid, 64)
        surf.blit(t, t.get_rect(center=(cx, disc_cy)))
        name = _name(sid)
    facet_gem(surf, stage.right - 6, stage.y + 6, 7, pal["gem"], pal["deep"],
              mystery=secret)
    nimg = _font(17, True).render(name, True, concept.GOLD)
    surf.blit(nimg, nimg.get_rect(center=(cx, panel.y + 170)))
    rword = "MYSTERY" if secret else tier.upper()
    rcol = pal["gem"]
    rimg = _font(11, True).render(rword, True, rcol)
    surf.blit(rimg, rimg.get_rect(center=(cx, panel.y + 188)))
    price = _cost(sid)
    fg, bg, rim = concept.chip_colors("price")
    chip(surf, cx, panel.y + 212, f"{price:,}", fg, bg, rim, h=28, coin=True)
    # buttons
    bw, bh, gut = 102, 38, 16
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


def inset_disc(surf, cx, cy, r, tint=(6, 6, 12)):
    disc = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
    for i in range(r, 0, -1):
        c = lerp_color((30, 28, 40), tint, (i / r) ** 1.3)
        pygame.draw.circle(disc, (*c, 255), (r + 1, r + 1), i)
    pygame.draw.circle(disc, (0, 0, 0, 130), (r + 1, r + 1), r, 2)
    pygame.draw.circle(disc, (*_GOLD_DEEP, 60), (r + 1, r + 1), r - 1, 1)
    surf.blit(disc, (cx - r - 1, cy - r - 1))


# ── detail-zoom: render a trio of cards at the real metrics, then magnify ─────
# We draw the cards at their true 162x100 size (so every offset, gem, chip and
# gold rule is pixel-identical to the live store) onto a concept-tinted strip,
# then upscale the whole strip so the small stuff can be judged up close.
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
    lbl = _font(12, True).render("RARITY  /  CHIP  /  GEM  DETAIL", True, concept.GOLD_PALE)
    strip.blit(lbl, (pad, 6))
    for i, sid in enumerate(DETAIL_IDS):
        x = pad + i * (cw + g)
        y = 24 + pad
        concept.card(strip, sid, pygame.Rect(x, y, cw, ch), sid == EQUIPPED_ID)
    # magnify ~1.4x so the detail reads up close while staying crisp-ish
    scale = 1.4
    return pygame.transform.smoothscale(
        strip, (int(strip_w * scale), int(strip_h * scale)))


# ── compose the comparison sheet ──────────────────────────────────────────────
def build_sheet():
    from concepts import CONCEPTS  # imported here to avoid an import cycle
    cols = []
    for concept in CONCEPTS:
        store = render_store(concept)
        modal = render_store(concept)
        concept.modal(modal, "skin_phoenix")  # epic buy-confirm
        detail = render_detail(concept)
        cols.append((concept, store, modal, detail))

    # Layout: each column = label + store(360) + modal(360) + detail.
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
        # column name + descriptor
        nm = _font(24, True).render(concept.NAME, True, (255, 236, 180))
        sheet.blit(nm, nm.get_rect(center=(col_cx, pad + 16)))
        ds = _font(13, True).render(concept.DESC, True, (190, 186, 200))
        sheet.blit(ds, ds.get_rect(center=(col_cx, pad + 40)))
        y = pad + label_h
        for img, tag in ((store, "STORE"), (modal, "BUY CONFIRM"),
                         (detail, "DETAIL ZOOM")):
            ix = cx + (col_w - img.get_width()) // 2
            # subtle frame around each screenshot
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
