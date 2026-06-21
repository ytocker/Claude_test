"""
Round-3 (FINAL) render harness for the COIN STORE redesign.

The art-director LOCKED the chassis to "B+" and handed a 6-point punch-list.
This script builds the single shippable design at that locked spec — no
sub-variants. It renders ONE full-screen 360x640 store mockup plus a
DETAIL-CALLOUT band: the five distinct rarity reads (common/rare/epic/
legendary/mystery) on shelf-bar AND gem, a grayscale strip proving
value-separation, the unified chip family with the redrawn coin glyph, the
balance header, the tab strip, and the rebuilt cohesive buy-confirm modal.

All visuals are procedural / pygame-only and both-target safe (no desktop- or
browser-only API). Run:  python docs/store_redesign/render_r3.py
"""
from __future__ import annotations

import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import pygame  # noqa: E402

pygame.init()
pygame.font.init()

from game.config import W, H  # noqa: E402
from game.draw import (  # noqa: E402
    rounded_rect, lerp_color, UI_CREAM, NEAR_BLACK, WHITE,
)
from game.hud import (  # noqa: E402
    _font, _draw_overlay_stars,
    _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP, _RED_OUTLINE,
)
from game.powerup_help import _seeded_stars  # noqa: E402
from game import parrot, store_catalog, store_data  # noqa: E402
from game.surprise_box_variants import _draw_qmark  # noqa: E402

store_data.load()

# ── rarity language (PUNCH-LIST 1) ───────────────────────────────────────────
# The four tiers + the mystery state must be unmistakably distinct from EACH
# OTHER by HUE *and* VALUE (colorblind-safe; survives grayscale). Both the
# shelf-bar and the gem pull from the same per-tier triplet so they read as one
# jewel. The "lum" note on each is the perceived grayscale value of the `gem`
# face (Rec.601: 0.299R+0.587G+0.114B) — chosen to ladder cleanly:
#   COMMON   warm-neutral sand   lum ~150  (mid)   hue: warm/amber
#   RARE     cyan-blue           lum ~163  (mid-hi) hue: cool blue
#   EPIC     magenta-purple      lum ~123  (low)    hue: violet
#   LEGENDARY hot orange         lum ~178  (high)   hue: orange  <- standout
#   MYSTERY  cool silver shimmer lum ~205  (top)    hue: neutral, NO tier
# So in grayscale the order epic < common < rare < legendary < mystery gives
# four separable steps + the brightest reserved for the un-tiered mystery.
RARITY = {
    # COMMON: warm-neutral sand (NOT gray) so it reads as a real, lit tier on
    # obsidian. Distinct in hue from mystery's cool silver; mid grayscale value.
    "common":    {"gem": (208, 178, 132), "glow": (196, 162, 110),
                  "deep": (96, 74, 44)},
    # RARE: cyan-leaning blue — pushed cooler/greener so it can never be
    # confused with the neutral silver mystery in hue OR value.
    "rare":      {"gem": (96, 196, 240),  "glow": (64, 172, 230),
                  "deep": (20, 78, 116)},
    # EPIC: deep magenta-violet — the darkest tier value, unmistakably violet.
    "epic":      {"gem": (190, 104, 236), "glow": (170, 78, 232),
                  "deep": (70, 28, 104)},
    # LEGENDARY: hot orange — the brightest tier, the deliberate standout.
    "legendary": {"gem": (255, 168, 56),  "glow": (255, 138, 30),
                  "deep": (132, 64, 10)},
}
# MYSTERY (secret ???): neutral iridescent SILVER shimmer — highest value, no
# saturated hue, so it claims NO tier and never collides with RARE's blue.
MYSTERY = {"gem": (214, 218, 224), "glow": (176, 196, 214),
           "deep": (78, 84, 98)}

_TAB_KEYS = ("common", "rare", "epic", "legendary")

# Five tabs sit comfortably across 360px with even gutters; the right chevron
# signals the rest (SHADES/PARCELS) scroll in — real stores paginate tabs.
_TABS = ("COSTUMES", "PARROTS", "ANIMALS", "SHOES", "HATS")

_STARS = _seeded_stars()

# Obsidian body stops — near-black, subtly top-lit so the panel reads as lit
# from above rather than a flat fill. NEVER tinted by rarity (locked B+).
_OBS_TOP = (26, 24, 32)
_OBS_BOT = (9, 8, 15)


# ── thumbnail cache ──────────────────────────────────────────────────────────
_thumb_cache: dict = {}


def _fit_skin(sid: str, box: int) -> pygame.Surface:
    key = (sid, box)
    cached = _thumb_cache.get(key)
    if cached is not None:
        return cached
    src = parrot.get_skin_icon(sid) or parrot.get_skin_frame(sid, 1, 0.0)
    bb = src.get_bounding_rect()
    if bb.width > 0 and bb.height > 0:
        src = src.subsurface(bb).copy()
    sw, sh = src.get_size()
    scale = box / max(sw, sh)
    out = pygame.transform.smoothscale(
        src, (max(1, int(sw * scale)), max(1, int(sh * scale))))
    _thumb_cache[key] = out
    return out


def _disp_name(sid: str) -> str:
    if sid in (store_catalog.BASE_SKIN, store_catalog.PARCEL_BASE):
        return "DEFAULT"
    return store_catalog.name(sid)


# ── the redrawn coin glyph (PUNCH-LIST 2) ────────────────────────────────────
# ONE clean coin used in the price chip, the balance capsule, and the modal.
# A flat-gold disc with a single soft bevel highlight (top-left) and a simple
# centred "$" notch. Deliberately NO gear/sunburst teeth — those read as muddy
# noise at chip scale. Cached per radius so it stays cheap.
_coin_cache: dict = {}


def _coin_glyph(surf, cx, cy, r):
    key = int(r)
    face = _coin_cache.get(key)
    if face is None:
        d = r * 2
        face = pygame.Surface((d + 2, d + 2), pygame.SRCALPHA)
        c = r + 1
        # Flat-gold disc with a single diagonal bevel: the fill ramps from a
        # bright top-left toward a deeper bottom-right along the TL->BR axis, so
        # the coin reads as one lit metal disc (not a sticker, no gear teeth).
        for yy in range(d + 2):
            for xx in range(d + 2):
                dx, dy = xx - c, yy - c
                if dx * dx + dy * dy > r * r:
                    continue
                # diagonal position in [0,1]: 0 at TL edge, 1 at BR edge.
                diag = (dx + dy) / (2 * r) + 0.5
                col = lerp_color((255, 230, 150), (188, 132, 30),
                                 max(0.0, min(1.0, diag)) ** 0.85)
                face.set_at((xx, yy), (*col, 255))
        # thin dark rim keyline so it seats against any chip fill.
        pygame.draw.circle(face, (*_GOLD_DEEP, 230), (c, c), r, 1)
        # single specular bevel arc hugging the top-left edge.
        hl = pygame.Surface((d + 2, d + 2), pygame.SRCALPHA)
        pygame.draw.circle(hl, (255, 250, 220, 220), (c, c),
                           max(1, r - 2), max(1, r // 6))
        for yy in range(d + 2):
            for xx in range(d + 2):
                if (xx - c) + (yy - c) > -r * 0.45:
                    hl.set_at((xx, yy), (0, 0, 0, 0))
        face.blit(hl, (0, 0))
        # simple "$" notch, struck darker so it reads as stamped, not printed.
        sf = _font(max(9, int(r * 1.5)), True)
        sg = sf.render("$", True, (120, 80, 16))
        face.blit(sg, sg.get_rect(center=(c, c)))
        sg2 = sf.render("$", True, (255, 238, 180))
        face.blit(sg2, sg2.get_rect(center=(c, c - 1)))
        _coin_cache[key] = face
    surf.blit(face, face.get_rect(center=(cx, cy)))


# ── premium primitives ───────────────────────────────────────────────────────

def _soft_glow(surf, cx, cy, radius, color, peak_alpha, layers=6):
    """Layered additive bloom. Cheap (no per-pixel) so cards emit light, not
    just an outline. Budget dialled to a strict hierarchy (balance coin
    brightest, then equipped rim, shelf-bar, gem, thumbnail)."""
    for i in range(layers, 0, -1):
        r = int(radius * i / layers)
        a = int(peak_alpha * (1 - (i - 1) / layers) ** 1.7)
        if r <= 0 or a <= 0:
            continue
        g = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(g, (*color, a), (r + 1, r + 1), r)
        surf.blit(g, (cx - r - 1, cy - r - 1), special_flags=pygame.BLEND_ADD)


def _vgrad_panel(w, h, radius, top, bot, alpha=255):
    """Rounded vertical-gradient panel (top brighter), corner-masked."""
    body = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        c = lerp_color(top, bot, y / max(1, h - 1))
        pygame.draw.line(body, (*c, alpha), (0, y), (w - 1, y))
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h),
                     border_radius=radius)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return body


def _drop_shadow(surf, rect, radius, blur=6, alpha=120, dy=4):
    """Soft drop shadow under a card."""
    for i in range(blur, 0, -1):
        a = int(alpha * (i / blur) ** 2 / blur * 2.2)
        if a <= 0:
            continue
        r = pygame.Rect(rect.x - i, rect.y - i + dy,
                        rect.w + 2 * i, rect.h + 2 * i)
        s = pygame.Surface(r.size, pygame.SRCALPHA)
        pygame.draw.rect(s, (0, 0, 0, a), s.get_rect(),
                         border_radius=radius + i)
        surf.blit(s, r.topleft)


def _inset_disc(surf, cx, cy, r, tint=(6, 6, 12)):
    """A clean dark inset disc for the thumbnail — never tinted by rarity."""
    disc = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    for i in range(r, 0, -1):
        f = i / r
        c = lerp_color((30, 28, 40), tint, f ** 1.3)
        pygame.draw.circle(disc, (*c, 255), (r, r), i)
    surf.blit(disc, (cx - r, cy - r))
    ring = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
    pygame.draw.circle(ring, (0, 0, 0, 130), (r + 1, r + 1), r, 2)
    pygame.draw.circle(ring, (*_GOLD_DEEP, 60), (r + 1, r + 1), r - 1, 1)
    surf.blit(ring, (cx - r - 1, cy - r - 1))


def _shelf_bar(surf, rect, tier, intensity=1.0, mystery=False):
    """The rarity SHELF-LIGHT BAR along the card base — an additive horizontal
    gradient strip in the tier colour that glows UP into the body like a museum
    vitrine light. PRIMARY rarity cue. Locked at intensity 1.0 for B+."""
    pal = MYSTERY if mystery else RARITY[tier]
    glow, gem = pal["glow"], pal["gem"]
    bw = rect.w - 28
    bx = rect.x + 14
    by = rect.bottom - 8
    wash_h = int(10 * intensity) + 6
    wash = pygame.Surface((bw, wash_h), pygame.SRCALPHA)
    peak = int(22 * intensity) + 8
    for y in range(wash_h):
        f = 1.0 - y / wash_h
        a = int(peak * f ** 2.6)
        if a <= 0:
            continue
        for seg in range(0, bw, 2):
            hx = abs(seg - bw / 2) / (bw / 2)
            ha = int(a * (1.0 - 0.6 * hx ** 2))
            if ha > 0:
                wash.set_at((seg, wash_h - 1 - y), (*glow, ha))
                if seg + 1 < bw:
                    wash.set_at((seg + 1, wash_h - 1 - y), (*glow, ha))
    surf.blit(wash, (bx, by - wash_h + 3), special_flags=pygame.BLEND_ADD)
    bar = pygame.Rect(bx, by, bw, 3)
    core = pygame.Surface((bw, 3), pygame.SRCALPHA)
    for sx in range(bw):
        hx = abs(sx - bw / 2) / (bw / 2)
        c = lerp_color(lerp_color(gem, WHITE, 0.4), pal["deep"], hx ** 1.4)
        a = int(255 * (1.0 - 0.4 * hx ** 2))
        for sy in range(3):
            core.set_at((sx, sy), (*c, a))
    mask = pygame.Surface((bw, 3), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, bw, 3), border_radius=1)
    core.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(core, bar.topleft)


def _gold_leaf(surf, cx, cy, sx):
    """A tiny two-leaf gold sprig flourish for LEGENDARY cards only (faint)."""
    col = (*_GOLD_DEEP, 170)
    leaf = pygame.Surface((20, 16), pygame.SRCALPHA)
    pygame.draw.line(leaf, col, (10, 14), (10, 3), 1)
    pygame.draw.ellipse(leaf, (*_GOLD_BRIGHT, 150), (4, 4, 7, 9))
    pygame.draw.ellipse(leaf, (*_GOLD_BRIGHT, 150), (10, 5, 7, 9))
    if sx < 0:
        leaf = pygame.transform.flip(leaf, True, False)
    surf.blit(leaf, (cx - 10, cy - 6))


def _gem(surf, cx, cy, r, tier, t=0.0, inset=True, mystery=False):
    """Faceted rarity gem badge inset in the card corner (PUNCH-LIST 6: now a
    THREE-value cut). Lit top-left facet, mid right facet, a DARKER bottom-right
    SHADOW facet, plus a recovered white specular pip — so the cut catches light
    at 360px instead of reading as a flat 2-tone chevron. Seated in a dark
    keyline well so it reads as inset jewellery. SECONDARY rarity marker."""
    pal = MYSTERY if mystery else RARITY[tier]
    base, glow, deep = pal["gem"], pal["glow"], pal["deep"]
    if inset:
        seat = pygame.Surface((r * 2 + 8, r * 2 + 8), pygame.SRCALPHA)
        pygame.draw.circle(seat, (0, 0, 0, 150), (r + 4, r + 4), r + 3)
        pygame.draw.circle(seat, (*_GOLD_DEEP, 90), (r + 4, r + 4), r + 3, 1)
        surf.blit(seat, (cx - r - 4, cy - r - 4))
    _soft_glow(surf, cx, cy, int(r * 1.5), glow,
               int(70 + 30 * (0.5 + 0.5 * math.sin(t * 3))), layers=4)
    top, bot = (cx, cy - r), (cx, cy + r)
    left, right = (cx - r, cy), (cx + r, cy)
    ctr = (cx, cy)
    if mystery:
        f1 = lerp_color((196, 214, 226), (214, 202, 224), 0.5)
        hi = lerp_color(f1, WHITE, 0.55)        # bright top-left
        mid = f1                                # mid top-right
        sh = lerp_color(f1, deep, 0.45)         # shaded bottom-left
        dk = lerp_color(deep, NEAR_BLACK, 0.25)  # DARKEST bottom-right facet
    else:
        hi = lerp_color(base, WHITE, 0.5)        # bright top-left facet
        mid = base                               # mid top-right facet
        sh = lerp_color(base, deep, 0.5)         # shaded bottom-left facet
        dk = lerp_color(deep, NEAR_BLACK, 0.3)   # DARKEST bottom-right facet
    pygame.draw.polygon(surf, hi, [top, left, ctr])
    pygame.draw.polygon(surf, mid, [top, right, ctr])
    pygame.draw.polygon(surf, sh, [left, bot, ctr])
    pygame.draw.polygon(surf, dk, [right, bot, ctr])
    # crisp girdle keyline around the whole stone.
    pygame.draw.polygon(surf, lerp_color(deep, NEAR_BLACK, 0.45),
                        [top, right, bot, left], width=1)
    # recovered white specular pip on the lit facet so the cut catches light.
    pr = max(1, r // 4)
    pip = pygame.Surface((pr * 2 + 2, pr * 2 + 2), pygame.SRCALPHA)
    pygame.draw.circle(pip, (255, 255, 255, 245), (pr + 1, pr + 1), pr)
    surf.blit(pip, (cx - pr - r // 3, cy - pr - r // 3),
              special_flags=pygame.BLEND_ADD)


# ── unified chip family (PUNCH-LIST 3) ───────────────────────────────────────
# Identical pill silhouette + hairline rim for EVERY state. Only the fill +
# content differ. The can't-afford "locked" chip is pushed DARKER + COOLER
# (slate-blue, not warm gold) so it can never be mistaken for the warm EQUIP
# chip at 360px; the lock glyph stays a confirming (not sole) cue.
_CHIP_STATES = {
    "price":     {"fg": _GOLD_PALE,    "bg": _GOLD_DEEP,     "rim": (*_GOLD_BRIGHT, 150)},
    "equip":     {"fg": UI_CREAM,      "bg": (96, 74, 24),   "rim": (*_GOLD_BRIGHT, 150)},
    "equipped":  {"fg": (10, 30, 14),  "bg": (84, 196, 112), "rim": (200, 255, 210, 200)},
    # locked: dark cool slate-blue — clearly NOT warm gold. Muted, recedes.
    "locked":    {"fg": (150, 166, 190), "bg": (40, 46, 62), "rim": (88, 102, 132, 180)},
}


def _lock_glyph(surf, cx, cy, col):
    """Tiny padlock for the can't-afford chip — body + shackle, ~9px tall."""
    body = pygame.Rect(cx - 4, cy - 1, 8, 6)
    rounded_rect(surf, body, 2, col)
    pygame.draw.arc(surf, col, (cx - 3, cy - 6, 6, 8), 0.2, math.pi - 0.2, 2)
    surf.set_at((cx, cy + 2), (24, 28, 38))


def _chip(surf, cx, cy, text, state, coin=False, h=24, lock=False):
    """The single chip silhouette for all states. Pill body (gradient),
    hairline rim, optional NEW coin glyph or lock, centred on (cx, cy)."""
    sp = _CHIP_STATES[state]
    fsz = max(12, int(h * 0.56))
    f = _font(fsz, True)
    timg = f.render(text, True, sp["fg"])
    coin_d = int(h * 0.62)
    pre_w = (coin_d + 4) if coin else (12 if lock else 0)
    pad = 12
    w = pre_w + timg.get_width() + pad * 2
    chip = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    body = _vgrad_panel(w, h, h // 2, lerp_color(sp["bg"], WHITE, 0.18), sp["bg"])
    surf.blit(body, chip.topleft)
    # subtle top sheen — strength scaled down on the dark locked chip so it
    # stays visibly cooler/flatter than the glossy warm chips.
    sheen_peak = 28 if state == "locked" else 46
    sheen = pygame.Surface((w - 6, h // 2), pygame.SRCALPHA)
    for y in range(h // 2):
        a = int(sheen_peak * (1 - y / (h // 2)))
        pygame.draw.line(sheen, (255, 255, 255, a), (0, y), (w - 6, y))
    smask = pygame.Surface((w - 6, h // 2), pygame.SRCALPHA)
    pygame.draw.rect(smask, (255, 255, 255, 255), smask.get_rect(),
                     border_radius=h // 2)
    sheen.blit(smask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(sheen, (chip.x + 3, chip.y + 2))
    pygame.draw.rect(surf, sp["rim"], chip, width=1, border_radius=h // 2)
    x = chip.x + pad
    if coin:
        _coin_glyph(surf, x + coin_d // 2, cy, coin_d // 2)
        x += coin_d + 4
    elif lock:
        _lock_glyph(surf, x + 4, cy, sp["fg"])
        x += 12
    surf.blit(timg, timg.get_rect(midleft=(x, cy)))
    return chip


def _state_chip(surf, sid, cx, cy, equipped, secret, h=24, force=None):
    if force == "locked":
        price = store_catalog.cost(sid)
        _chip(surf, cx, cy, f"{price:,}", "locked", lock=True, h=h)
        return
    if equipped:
        _chip(surf, cx, cy, "EQUIPPED", "equipped", h=h)
        return
    owned = store_data.is_owned(sid) and not secret
    if owned:
        _chip(surf, cx, cy, "EQUIP", "equip", h=h)
        return
    price = store_catalog.cost(sid)
    afford = store_data.balance() >= price
    if afford:
        _chip(surf, cx, cy, f"{price:,}", "price", coin=True, h=h)
    else:
        _chip(surf, cx, cy, f"{price:,}", "locked", lock=True, h=h)


def _gradient_text(surf, txt, font_obj, center, top, bot, outline=None,
                   shadow=True):
    base = font_obj.render(txt, True, WHITE)
    w, h = base.get_size()
    grad = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        c = lerp_color(top, bot, y / max(1, h - 1))
        pygame.draw.line(grad, c, (0, y), (w, y))
    grad.blit(base, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    r = base.get_rect(center=center)
    if outline:
        out = font_obj.render(txt, True, outline)
        for ox, oy in ((-1, 0), (1, 0), (0, -1), (0, 1),
                       (-1, -1), (1, -1), (-1, 1), (1, 1)):
            surf.blit(out, (r.x + ox, r.y + oy))
    if shadow:
        sh = font_obj.render(txt, True, NEAR_BLACK)
        sh.set_alpha(150)
        surf.blit(sh, (r.x + 1, r.y + 2))
    surf.blit(grad, r.topleft)
    return r


def _gold_rule(surf, x0, x1, y, peak=170):
    """A soft gold GRADIENT rule (PUNCH-LIST 5) — bright at the centre, fading
    to nothing at both ends. Replaces the hard header hairline so dividers match
    the capsule's lit language."""
    w = x1 - x0
    line = pygame.Surface((w, 3), pygame.SRCALPHA)
    for sx in range(w):
        hx = abs(sx - w / 2) / (w / 2)
        a = int(peak * (1.0 - hx ** 1.6))
        if a <= 0:
            continue
        line.set_at((sx, 1), (*_GOLD_BRIGHT, a))
        line.set_at((sx, 0), (*_GOLD_PALE, a // 2))
        line.set_at((sx, 2), (*_GOLD_DEEP, a // 2))
    surf.blit(line, (x0, y - 1))


# ── background ───────────────────────────────────────────────────────────────

def _bg(surf, stops, t=2.0, stars=True, aurora=False):
    h = surf.get_height()
    n = len(stops)
    for y in range(h):
        f = y / max(1, h - 1)
        seg = min(n - 2, int(f * (n - 1)))
        local = (f * (n - 1)) - seg
        c = lerp_color(stops[seg], stops[seg + 1], local)
        pygame.draw.line(surf, c, (0, y), (surf.get_width() - 1, y))
    # Aurora wash OFF by default per the locked B+ spec — the code path is kept
    # so it can be re-enabled, but the shippable store does not use it.
    if aurora:
        for i, (cx, col) in enumerate([(96, (54, 150, 150)),
                                       (264, (120, 92, 200))]):
            _soft_glow(surf, cx, 230 + i * 60, 140, col, 11, layers=6)
    if stars:
        _draw_overlay_stars(surf, _STARS, t)


# ── the locked B+ card ───────────────────────────────────────────────────────

def _card(surf, sid, rect, equipped, secret, t, *, force=None):
    """LOCKED B+ card: obsidian top-lit body (never tinted by rarity), a 2px
    fine gold inner bezel, a rarity SHELF-LIGHT BAR at the base @1.0 (primary
    cue), an inset GEM BADGE in the TOP-RIGHT corner (secondary), the thumbnail
    on a clean dark inset disc, and a full-card gold rim + edge halo when
    equipped."""
    tier = store_catalog.rarity(sid)
    _drop_shadow(surf, rect, 13, blur=6, alpha=140)
    body = _vgrad_panel(rect.w, rect.h, 13, _OBS_TOP, _OBS_BOT, alpha=252)
    surf.blit(body, rect.topleft)

    # Fine 2px gold inner bezel — crisp jeweller line (locked weight).
    inner = rect.inflate(-7, -7)
    pygame.draw.rect(surf, (*_GOLD_DEEP, 210), inner, width=2, border_radius=8)
    sheen = pygame.Surface((rect.w - 10, 16), pygame.SRCALPHA)
    for y in range(16):
        a = int(30 * (1 - y / 16))
        pygame.draw.line(sheen, (255, 255, 255, a), (0, y), (rect.w - 10, y))
    surf.blit(sheen, (rect.x + 5, rect.y + 4))

    # Rarity shelf-light bar (PRIMARY cue) @ locked 1.0 intensity.
    _shelf_bar(surf, rect, tier, intensity=1.0, mystery=secret)

    disc_cy = rect.y + 34
    _inset_disc(surf, rect.centerx, disc_cy, 26)
    if secret:
        _draw_qmark(surf, rect.centerx, disc_cy, 36, UI_CREAM, NEAR_BLACK,
                    thick=2)
        name = "???"
    else:
        th = _fit_skin(sid, 44)
        surf.blit(th, th.get_rect(center=(rect.centerx, disc_cy)))
        name = _disp_name(sid)

    # Legendary-only gold leaf sprig in the TOP-LEFT (opposite the TR gem).
    if tier == "legendary" and not secret:
        _gold_leaf(surf, rect.x + 13, rect.y + 12, 1)

    # Inset gem badge in the TOP-RIGHT corner (locked B+ placement).
    _gem(surf, rect.right - 15, rect.y + 15, 6, tier, t, mystery=secret)

    nimg = _font(13, True).render(name, True, _GOLD_PALE)
    nsh = _font(13, True).render(name, True, NEAR_BLACK)
    nsh.set_alpha(150)
    nr = nimg.get_rect(center=(rect.centerx, rect.y + 62))
    surf.blit(nsh, (nr.x + 1, nr.y + 1))
    surf.blit(nimg, nr)

    _state_chip(surf, sid, rect.centerx, rect.y + 82, equipped, secret,
                force=force)

    if equipped:
        halo = pygame.Surface((rect.w + 16, rect.h + 16), pygame.SRCALPHA)
        for k in range(4, 0, -1):
            a = int(20 * k / 4)
            pygame.draw.rect(halo, (*_GOLD_BRIGHT, a),
                             (8 - k, 8 - k, rect.w + 2 * k, rect.h + 2 * k),
                             width=2, border_radius=13 + k)
        surf.blit(halo, (rect.x - 8, rect.y - 8),
                  special_flags=pygame.BLEND_ADD)
        pygame.draw.rect(surf, lerp_color(_GOLD_BRIGHT, NEAR_BLACK, 0.4), rect,
                         width=2, border_radius=13)
        pygame.draw.rect(surf, _GOLD_BRIGHT, rect.inflate(-2, -2), width=1,
                         border_radius=12)


# ── sample cards (real items spanning all tiers + equipped + secret) ─────────

def _sample_cards():
    cos = sorted(store_catalog.ids_of_group("costume"), key=store_catalog.cost)
    ani = sorted(store_catalog.ids_of_group("animal"), key=store_catalog.cost)
    return [
        (cos[0], True, False, None),       # common, equipped (gold card-rim)
        (cos[3], False, False, None),      # common
        (ani[0], False, False, None),      # rare
        (ani[5], False, False, None),      # rare
        (ani[11], False, False, None),     # epic
        (ani[16], False, False, "locked"),  # epic, forced can't-afford
        (ani[18], False, False, None),     # legendary
        ("skin_ufo", False, True, None),   # secret (mystery)
    ]


# layout (2x4 grid)
_CARD_W = 162
_CARD_H = 100
_GAP = 8
_GRID_TOP = 120


def _grid_rects():
    base_x = (W - (_CARD_W * 2 + _GAP)) // 2
    rects = []
    for idx in range(8):
        col, row = idx % 2, idx // 2
        x = base_x + col * (_CARD_W + _GAP)
        y = _GRID_TOP + row * (_CARD_H + _GAP)
        rects.append(pygame.Rect(x, y, _CARD_W, _CARD_H))
    return base_x, rects


# ── chrome: header, tab strip, page, back ────────────────────────────────────

def _balance_header(surf, cx, y):
    """Luxe recessed gold capsule + gradient-gold digits with the NEW coin
    glyph. The balance coin is the brightest glow on the screen; the + is a
    clear round tappable button."""
    val = "12,480"
    vf = _font(22, True)
    vimg_w = vf.size(val)[0]
    coin_d = 24
    plus_d = 26
    gap_coin = 9
    pad = 14
    inner = coin_d + gap_coin + vimg_w + 12 + plus_d
    w = inner + pad * 2
    cap = pygame.Rect(cx - w // 2, y - 18, w, 36)
    _drop_shadow(surf, cap, 18, blur=4, alpha=90)
    body = _vgrad_panel(cap.w, cap.h, 18, (44, 32, 18), (20, 14, 8), alpha=252)
    surf.blit(body, cap.topleft)
    pygame.draw.rect(surf, (0, 0, 0, 120), cap.inflate(-2, -2), width=1,
                     border_radius=17)
    pygame.draw.rect(surf, (*_GOLD_BRIGHT, 190), cap, width=1, border_radius=18)
    x = cap.x + pad
    _soft_glow(surf, x + coin_d // 2, y, coin_d + 4, (255, 206, 92), 110,
               layers=5)
    _coin_glyph(surf, x + coin_d // 2, y, coin_d // 2)
    x += coin_d + gap_coin
    _gradient_text(surf, val, vf, (x + vimg_w // 2, y),
                   (255, 246, 196), (236, 170, 60), shadow=True)
    x += vimg_w + 12
    addr = pygame.Rect(x, y - plus_d // 2, plus_d, plus_d)
    _soft_glow(surf, addr.centerx, addr.centery, plus_d // 2 + 2,
               (255, 200, 80), 38, layers=3)
    grad = _vgrad_panel(plus_d, plus_d, plus_d // 2,
                        lerp_color(_GOLD_BRIGHT, WHITE, 0.2), _GOLD_DEEP)
    surf.blit(grad, addr.topleft)
    pygame.draw.circle(surf, _GOLD_PALE, addr.center, plus_d // 2, 1)
    pimg = _font(20, True).render("+", True, (40, 24, 8))
    surf.blit(pimg, pimg.get_rect(center=(addr.centerx, addr.centery - 1)))


def _daily_pill(surf):
    f = _font(12, True)
    lbl = f.render("DAILY", True, (28, 18, 8))
    timg = f.render("+50", True, (28, 18, 8))
    w = lbl.get_width() + 6 + timg.get_width() + 22
    r = pygame.Rect(W - 12 - w, 14, w, 24)
    body = _vgrad_panel(r.w, r.h, 11, (255, 215, 120), _GOLD_DEEP, alpha=255)
    surf.blit(body, r.topleft)
    pygame.draw.rect(surf, (*_GOLD_BRIGHT, 200), r, width=1, border_radius=11)
    surf.blit(lbl, lbl.get_rect(midleft=(r.x + 11, r.centery)))
    surf.blit(timg, timg.get_rect(midleft=(r.x + 11 + lbl.get_width() + 6,
                                           r.centery)))


def _title(surf):
    f = _font(28, True)
    out = f.render("STORE", True, _RED_OUTLINE)
    r = f.render("STORE", True, WHITE).get_rect(center=(W // 2, 30))
    for ox, oy in ((-2, 0), (2, 0), (0, -2), (0, 2),
                   (-2, -2), (2, -2), (-2, 2), (2, 2)):
        surf.blit(out, (r.x + ox, r.y + oy))
    sh = f.render("STORE", True, NEAR_BLACK)
    sh.set_alpha(160)
    surf.blit(sh, (r.x + 2, r.y + 3))
    _gradient_text(surf, "STORE", f, (W // 2, 30),
                   (255, 240, 180), (236, 170, 60), shadow=False)


def _header(surf):
    _title(surf)
    _balance_header(surf, W // 2, 66)
    _daily_pill(surf)


def _tabstrip(surf, active, t):
    """ONE consistent active treatment: gold underline + brighter label on
    active, dimmed inactive; even spacing; no pills; a right chevron for the
    overflow tabs."""
    y = 100
    f = _font(11, True)
    n = len(_TABS)
    left, right = 12, W - 24
    cell = (right - left) / n
    for i, lbl in enumerate(_TABS):
        on = (i == active)
        col = _GOLD_BRIGHT if on else (150, 142, 158)
        timg = f.render(lbl, True, col)
        if not on:
            timg.set_alpha(170)
        cxp = int(left + cell * (i + 0.5))
        tr = timg.get_rect(center=(cxp, y))
        surf.blit(timg, tr)
        if on:
            ur = pygame.Rect(tr.x - 2, y + 11, tr.w + 4, 3)
            uglow = pygame.Surface((ur.w + 12, 10), pygame.SRCALPHA)
            for gy in range(10):
                a = int(40 * (1 - gy / 10))
                pygame.draw.line(uglow, (255, 200, 80, a), (0, gy),
                                 (ur.w + 12, gy))
            surf.blit(uglow, (ur.x - 6, ur.y - 2),
                      special_flags=pygame.BLEND_ADD)
            rounded_rect(surf, ur, 2, _GOLD_BRIGHT)
    cx = W - 14
    pts = [(cx - 4, y - 5), (cx + 1, y), (cx - 4, y + 5)]
    pygame.draw.lines(surf, (*_GOLD_PALE, 220), False, pts, 2)


def _page_controls(surf, base_x, page, n_pages):
    w = _CARD_W * 2 + _GAP
    y = _GRID_TOP + 4 * (_CARD_H + _GAP)
    cy = y + 10
    lbl = _font(12, True).render(f"PAGE  {page + 1} / {n_pages}", True,
                                 _GOLD_PALE)
    surf.blit(lbl, lbl.get_rect(center=(base_x + w // 2, cy)))
    for cx, glyph, on in ((base_x + 16, "<", page > 0),
                          (base_x + w - 16, ">", page < n_pages - 1)):
        r = pygame.Rect(0, 0, 30, 22)
        r.center = (cx, cy)
        rounded_rect(surf, r, 11, _GOLD_DEEP if on else (54, 48, 58))
        pygame.draw.rect(surf, _GOLD_BRIGHT if on else (88, 80, 90), r,
                         width=1, border_radius=11)
        g = _font(15, True).render(glyph, True,
                                   _GOLD_PALE if on else (140, 132, 146))
        surf.blit(g, g.get_rect(center=(cx, cy - 1)))


def _back_pill(surf):
    r = pygame.Rect(0, 0, 160, 36)
    r.center = (W // 2, H - 26)
    _drop_shadow(surf, r, 18, blur=4, alpha=90)
    body = _vgrad_panel(r.w, r.h, 18, (40, 32, 56), (22, 16, 38), alpha=240)
    surf.blit(body, r.topleft)
    pygame.draw.rect(surf, (*_GOLD_BRIGHT, 185), r, width=1, border_radius=18)
    timg = _font(18, True).render("BACK", True, _GOLD_PALE)
    surf.blit(timg, timg.get_rect(center=r.center))


# ── full-screen store (locked B+) ────────────────────────────────────────────

def render_store(surf, t=2.0):
    # Aurora OFF (locked B+): the obsidian cards carry the look unaided.
    _bg(surf, [(8, 8, 24), (12, 12, 36), (18, 16, 48), (24, 20, 58)], t,
        aurora=False)
    _header(surf)
    _tabstrip(surf, active=2, t=t)
    base_x, rects = _grid_rects()
    for (sid, eq, sec, force), rect in zip(_sample_cards(), rects):
        _card(surf, sid, rect, eq, sec, t, force=force)
    _page_controls(surf, base_x, 1, 3)
    _back_pill(surf)


# ── detail callouts ──────────────────────────────────────────────────────────

def _rarity_chip_row(surf, ox, oy, w, gem_only=False):
    """The five distinct rarity reads side by side: a shelf-bar swatch with the
    matching gem above it, captioned. gem_only renders just the gem (used by the
    grayscale strip via a separate render+desaturate)."""
    tiers = [("COMMON", "common", False), ("RARE", "rare", False),
             ("EPIC", "epic", False), ("LEGENDARY", "legendary", False),
             ("MYSTERY", None, True)]
    n = len(tiers)
    cell = w // n
    for i, (cap, key, myst) in enumerate(tiers):
        cx = ox + cell * i + cell // 2
        # a mini obsidian tile so the shelf-bar reads on its true ground.
        tile = pygame.Rect(cx - cell // 2 + 6, oy, cell - 12, 70)
        body = _vgrad_panel(tile.w, tile.h, 10, _OBS_TOP, _OBS_BOT)
        surf.blit(body, tile.topleft)
        pygame.draw.rect(surf, (*_GOLD_DEEP, 180), tile.inflate(-6, -6),
                         width=1, border_radius=7)
        _gem(surf, tile.centerx, tile.y + 24, 9,
             key if not myst else "common", mystery=myst)
        _shelf_bar(surf, tile, key if not myst else "common", intensity=1.0,
                   mystery=myst)
        col = (MYSTERY["gem"] if myst else RARITY[key]["gem"])
        lab = _font(11, True).render(cap, True, col)
        surf.blit(lab, lab.get_rect(center=(cx, oy + 84)))


def _big_card(surf, ox, oy, sid, equipped=False, secret=False, scale=1.15,
              label=None, force=None):
    cw, ch = int(_CARD_W * scale), 196
    rect = pygame.Rect(ox, oy, cw, ch)
    tier = store_catalog.rarity(sid)
    _drop_shadow(surf, rect, 18, blur=6, alpha=140)
    body = _vgrad_panel(cw, ch, 18, _OBS_TOP, _OBS_BOT, alpha=252)
    surf.blit(body, rect.topleft)
    inner = rect.inflate(-12, -12)
    pygame.draw.rect(surf, (*_GOLD_DEEP, 215), inner, width=2, border_radius=12)
    sheen = pygame.Surface((cw - 14, 24), pygame.SRCALPHA)
    for y in range(24):
        a = int(32 * (1 - y / 24))
        pygame.draw.line(sheen, (255, 255, 255, a), (0, y), (cw - 14, y))
    surf.blit(sheen, (rect.x + 7, rect.y + 6))
    _shelf_bar(surf, rect, tier, intensity=1.0, mystery=secret)
    disc_r = 42
    disc_cy = rect.y + 16 + disc_r
    _inset_disc(surf, rect.centerx, disc_cy, disc_r)
    if secret:
        _draw_qmark(surf, rect.centerx, disc_cy, 58, UI_CREAM,
                    NEAR_BLACK, thick=3)
        name = "???"
    else:
        th = _fit_skin(sid, 72)
        surf.blit(th, th.get_rect(center=(rect.centerx, disc_cy)))
        name = _disp_name(sid)
    if tier == "legendary" and not secret:
        _gold_leaf(surf, rect.x + 20, rect.y + 20, 1)
    _gem(surf, rect.right - 18, rect.y + 18, 8, tier, mystery=secret)
    nimg = _font(17, True).render(name, True, _GOLD_PALE)
    nsh = _font(17, True).render(name, True, NEAR_BLACK)
    nsh.set_alpha(150)
    nr = nimg.get_rect(center=(rect.centerx, disc_cy + disc_r + 18))
    surf.blit(nsh, (nr.x + 1, nr.y + 1))
    surf.blit(nimg, nr)
    _state_chip(surf, sid, rect.centerx, rect.bottom - 28, equipped,
                secret, h=30, force=force)
    if equipped:
        halo = pygame.Surface((cw + 20, ch + 20), pygame.SRCALPHA)
        for k in range(5, 0, -1):
            a = int(18 * k / 5)
            pygame.draw.rect(halo, (*_GOLD_BRIGHT, a),
                             (10 - k, 10 - k, cw + 2 * k, ch + 2 * k),
                             width=2, border_radius=18 + k)
        surf.blit(halo, (rect.x - 10, rect.y - 10),
                  special_flags=pygame.BLEND_ADD)
        pygame.draw.rect(surf, lerp_color(_GOLD_BRIGHT, NEAR_BLACK, 0.4), rect,
                         width=3, border_radius=18)
        pygame.draw.rect(surf, _GOLD_BRIGHT, rect.inflate(-3, -3), width=1,
                         border_radius=16)
    cap = label or (tier.upper() if not secret else "MYSTERY")
    col = (RARITY[tier]["gem"] if not secret else MYSTERY["gem"])
    lab = _font(13, True).render(cap, True, col)
    surf.blit(lab, lab.get_rect(center=(rect.centerx, rect.bottom + 14)))


def _modal(surf, ox, oy, sid, scrim_w=300, scrim_h=340):
    """Rebuilt buy-confirm modal (PUNCH-LIST 5). The thumbnail disc and its
    rarity shelf strip are now ONE seated element — the strip sits flush under
    the disc with a connecting keyline so they don't read as two floating pills.
    The hard header hairline is replaced by a soft gold GRADIENT rule. New coin
    glyph in the price chip."""
    region = pygame.Rect(ox, oy, scrim_w, scrim_h)
    bg = _vgrad_panel(scrim_w, scrim_h, 0, (16, 14, 44), (26, 18, 58))
    surf.blit(bg, region.topleft)
    scrim = pygame.Surface((scrim_w, scrim_h), pygame.SRCALPHA)
    scrim.fill((4, 4, 10, 180))  # ~70% black
    surf.blit(scrim, region.topleft)

    tier = store_catalog.rarity(sid)
    pw, ph = 244, 278
    panel = pygame.Rect(ox + (scrim_w - pw) // 2, oy + (scrim_h - ph) // 2,
                        pw, ph)
    _drop_shadow(surf, panel, 18, blur=8, alpha=170)
    body = _vgrad_panel(pw, ph, 18, (28, 24, 38), (12, 10, 22), alpha=255)
    surf.blit(body, panel.topleft)
    pygame.draw.rect(surf, lerp_color(_GOLD_BRIGHT, NEAR_BLACK, 0.45), panel,
                     width=2, border_radius=18)
    pygame.draw.rect(surf, (*_GOLD_BRIGHT, 230), panel.inflate(-2, -2), width=1,
                     border_radius=16)

    cx = panel.centerx
    head = _font(13, True).render("CONFIRM PURCHASE", True, _GOLD_PALE)
    surf.blit(head, head.get_rect(center=(cx, panel.y + 22)))
    # soft gold GRADIENT rule under the header (replaces the hard hairline).
    _gold_rule(surf, panel.x + 28, panel.right - 28, panel.y + 38)

    # Connected disc + shelf strip: the disc sits in a dark inset "stage" with
    # the rarity shelf-light bar seated FLUSH at its base, so the two read as a
    # single lit vitrine element rather than two detached pills.
    stage_w = 96
    stage = pygame.Rect(cx - stage_w // 2, panel.y + 52, stage_w, 96)
    spanel = _vgrad_panel(stage.w, stage.h, 12, (18, 16, 26), (8, 7, 14))
    surf.blit(spanel, stage.topleft)
    pygame.draw.rect(surf, (0, 0, 0, 150), stage, width=1, border_radius=12)
    disc_cy = stage.y + 40
    _inset_disc(surf, cx, disc_cy, 38)
    th = _fit_skin(sid, 60)
    surf.blit(th, th.get_rect(center=(cx, disc_cy)))
    # shelf-bar seated at the stage base — same routine as the cards, so the
    # modal speaks the exact shelf-light language (one element, not a stray pill)
    _shelf_bar(surf, stage, tier, intensity=1.0)
    # gem badge seated into the top-right of the stage (matches card placement).
    _gem(surf, stage.right - 4, stage.y + 4, 7, tier)

    nimg = _font(17, True).render(_disp_name(sid), True, _GOLD_BRIGHT)
    surf.blit(nimg, nimg.get_rect(center=(cx, panel.y + 162)))
    rword = _font(11, True).render(tier.upper(), True, RARITY[tier]["gem"])
    surf.blit(rword, rword.get_rect(center=(cx, panel.y + 180)))

    _chip(surf, cx, panel.y + 204, f"{store_catalog.cost(sid):,}", "price",
          coin=True, h=28)

    bw, bh = 100, 38
    gutter = 16
    by = panel.bottom - 30
    total = bw * 2 + gutter
    nx = cx - total // 2
    yx = nx + bw + gutter
    cancel = pygame.Rect(nx, by - bh // 2, bw, bh)
    buy = pygame.Rect(yx, by - bh // 2, bw, bh)
    cb = _vgrad_panel(bw, bh, bh // 2, (70, 62, 80), (44, 38, 56))
    surf.blit(cb, cancel.topleft)
    pygame.draw.rect(surf, (126, 116, 138), cancel, width=1,
                     border_radius=bh // 2)
    ct = _font(14, True).render("CANCEL", True, UI_CREAM)
    surf.blit(ct, ct.get_rect(center=cancel.center))
    bglow2 = pygame.Surface((bw + 10, bh + 10), pygame.SRCALPHA)
    for k in range(4, 0, -1):
        a = int(22 * k / 4)
        pygame.draw.rect(bglow2, (255, 200, 80, a),
                         (5 - k, 5 - k, bw + 2 * k, bh + 2 * k),
                         border_radius=bh // 2 + k)
    surf.blit(bglow2, (buy.x - 5, buy.y - 5), special_flags=pygame.BLEND_ADD)
    yb = _vgrad_panel(bw, bh, bh // 2, lerp_color(_GOLD_BRIGHT, WHITE, 0.2),
                      _GOLD_DEEP)
    surf.blit(yb, buy.topleft)
    pygame.draw.rect(surf, _GOLD_PALE, buy, width=1, border_radius=bh // 2)
    yt = _font(15, True).render("BUY", True, (40, 24, 8))
    surf.blit(yt, yt.get_rect(center=buy.center))


# ── compose the sheet ────────────────────────────────────────────────────────

def _grayscale(src):
    """Rec.601 luma desaturation of a surface — proves the five rarity reads
    separate by VALUE, not just hue (colorblind safety). Pure-pygame via
    PixelArray (no numpy, so it runs on both build targets' tooling)."""
    w, h = src.get_size()
    out = pygame.Surface((w, h))
    out.blit(src, (0, 0))
    px = pygame.PixelArray(out)
    for x in range(w):
        col = px[x]
        for y in range(h):
            rgb = out.unmap_rgb(col[y])
            lum = int(rgb[0] * 0.299 + rgb[1] * 0.587 + rgb[2] * 0.114)
            col[y] = out.map_rgb((lum, lum, lum))
    px.close()
    return out


def main():
    pad = 24
    label_h = 30

    # Left: the single full-screen mockup. Right: the detail-callout band.
    # The band column is taller than the 640px mockup, so the sheet height is
    # driven by the band and the mockup is centred in its column.
    mock_w = W
    band_w = 760
    band_h = 1120
    sheet_w = pad + mock_w + pad + band_w + pad
    sheet_h = label_h + pad + band_h + pad

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((16, 14, 24))

    title = _font(20, True).render(
        "SKYBIT  COIN STORE  —  ROUND 3 (FINAL)  —  locked B+: obsidian + 2px"
        " bezel + shelf-bar@1.0 + TR gem", True, _GOLD_BRIGHT)
    sheet.blit(title, (pad, 6))

    # ── full-screen mockup (centred vertically in the taller column) ──
    screen = pygame.Surface((W, H), pygame.SRCALPHA)
    render_store(screen, t=2.0)
    mx = pad
    my = label_h + pad + (band_h - H) // 2
    pygame.draw.rect(sheet, (40, 36, 54),
                     (mx - 3, my - 3, W + 6, H + 6), border_radius=6)
    sheet.blit(screen, (mx, my))
    lbl = _font(14, True).render("FULL STORE  (locked B+)", True, _GOLD_PALE)
    sheet.blit(lbl, (mx + 2, my - 22))

    # ── detail-callout band ──
    bx = pad + mock_w + pad
    by = label_h + pad
    dlabel = _font(15, True).render("DETAIL CALLOUTS", True, _GOLD_PALE)
    sheet.blit(dlabel, (bx + 2, label_h - 6))

    cos = sorted(store_catalog.ids_of_group("costume"), key=store_catalog.cost)
    ani = sorted(store_catalog.ids_of_group("animal"), key=store_catalog.cost)

    y = by + 6

    # (1) Five distinct rarity reads — shelf-bar + gem, side by side.
    cap = _font(12, True).render(
        "FIVE DISTINCT RARITY READS  (shelf-bar + gem)", True, _GOLD_BRIGHT)
    sheet.blit(cap, (bx, y))
    _rarity_chip_row(sheet, bx, y + 18, band_w - 8)
    y += 18 + 96

    # (2) Grayscale proof strip of the same five — value separation.
    cap = _font(12, True).render(
        "GRAYSCALE PROOF  (separates by VALUE, colorblind-safe)", True,
        (200, 200, 200))
    sheet.blit(cap, (bx, y))
    gs = pygame.Surface((band_w - 8, 96), pygame.SRCALPHA)
    gs.fill((16, 14, 24))
    _rarity_chip_row(gs, 0, 0, band_w - 8)
    sheet.blit(_grayscale(gs), (bx, y + 18))
    y += 18 + 100

    # (3) Unified chip family with the NEW coin glyph.
    cap = _font(12, True).render(
        "UNIFIED CHIPS  (new coin glyph; locked = dark/cool)", True,
        _GOLD_BRIGHT)
    sheet.blit(cap, (bx, y))
    cy = y + 36
    _chip(sheet, bx + 64, cy, "1,200", "price", coin=True, h=30)
    _chip(sheet, bx + 190, cy, "EQUIP", "equip", h=30)
    _chip(sheet, bx + 300, cy, "EQUIPPED", "equipped", h=30)
    _chip(sheet, bx + 430, cy, "9,000", "locked", lock=True, h=30)
    sub = _font(10, True).render(
        "price        equip        equipped        can't-afford (dark cool +"
        " lock)", True, (190, 178, 150))
    sheet.blit(sub, (bx, cy + 22))
    # the coin glyph at three sizes to prove one design scales everywhere.
    _coin_glyph(sheet, bx + 560, cy, 8)
    _coin_glyph(sheet, bx + 585, cy, 11)
    _coin_glyph(sheet, bx + 618, cy, 15)
    cg = _font(10, True).render("one coin glyph", True, (190, 178, 150))
    sheet.blit(cg, cg.get_rect(center=(bx + 590, cy + 24)))
    y += 70

    # (4) balance header + tab strip stacked.
    cap = _font(12, True).render("BALANCE HEADER", True, _GOLD_BRIGHT)
    sheet.blit(cap, (bx, y))
    bsurf = pygame.Surface((360, 56), pygame.SRCALPHA)
    _balance_header(bsurf, 180, 30)
    sheet.blit(bsurf, (bx - 4, y + 18))
    # tab strip beside it.
    cap = _font(12, True).render("TAB STRIP", True, _GOLD_BRIGHT)
    sheet.blit(cap, (bx + 380, y))
    full = pygame.Surface((W, 160), pygame.SRCALPHA)
    full.blit(_vgrad_panel(W, 160, 8, (14, 12, 36), (18, 16, 46)), (0, 0))
    _tabstrip(full, active=2, t=2.0)
    band = full.subsurface(pygame.Rect(0, 84, W, 36)).copy()
    sheet.blit(band, (bx + 376, y + 22))
    y += 78

    # (5) the four rarity tiers + equipped + secret at scale (big cards).
    cap = _font(12, True).render(
        "TIER CARDS  +  EQUIPPED CARD-RIM  +  MYSTERY  +  can't-afford",
        True, _GOLD_BRIGHT)
    sheet.blit(cap, (bx, y))
    cards = [
        (cos[0], False, False, None),       # common
        (ani[0], False, False, None),       # rare
        (ani[11], False, False, None),      # epic
        (ani[18], False, False, None),      # legendary
        (cos[1], True, False, None),        # equipped
        ("skin_ufo", False, True, None),    # secret
        (ani[16], False, False, "locked"),  # can't-afford
    ]
    scale = 0.92
    cw = int(_CARD_W * scale)
    n = len(cards)
    row_gap = (band_w - 8 - n * cw) // (n - 1)
    cx0 = bx
    row_y = y + 22
    for sid, eq, sec, force in cards:
        _big_card(sheet, cx0, row_y, sid, equipped=eq, secret=sec,
                  scale=scale, force=force)
        cx0 += cw + row_gap
    y += 22 + 196 + 26

    # (6) the rebuilt cohesive buy-confirm modal.
    cap = _font(12, True).render(
        "BUY-CONFIRM MODAL  (disc+shelf as one element; soft gold rule)",
        True, _GOLD_BRIGHT)
    sheet.blit(cap, (bx, y))
    _modal(sheet, bx, y + 18, ani[18])

    out = os.path.join(_HERE, "round_3.png")
    pygame.image.save(sheet, out)
    print("saved:", out)
    print("sheet size:", sheet.get_size())


if __name__ == "__main__":
    main()
