"""
CONSTELLATION store — GLASS CABOCHON element loop.

The domed glass well that showcases each item's procedural thumbnail. Per the
locked THEME.md recipe: a dark domed glass body (CABO_LO -> CABO_HI), the skin
set INSIDE the well and RIM-LIT so the showcased content out-pops its frame
(fixing the prior inverted hierarchy), a TRUE top-left crescent specular (disc
minus an offset disc — only the lit arc, never a false full ring), a faint
bottom-right refraction arc, an inner vignette, and a thin warm-gold bezel with
a defined edge.

Authored resolution-independently at SS=4 and downscaled once, reusing the
constellation_hi pipeline (m()/font(), draw_bg, soft_glow, the cabochon body +
the _punch_contrast / _rim_light skin treatment). Pure pygame, both targets safe.
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

# Reuse the reference hi-res pipeline directly so this element shares the exact
# palette, supersample, background, primitives and skin-treatment as the rest of
# the store — drift here is what THEME.md forbids.
import importlib.util

_HI = os.path.abspath(os.path.join(_HERE, "..", "..", "constellation_hi", "render_hi.py"))
_spec = importlib.util.spec_from_file_location("_const_hi", _HI)
hi = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(hi)

import pygame
from game import parrot

m = hi.m
font = hi.font
SS, DW, DH = hi.SS, hi.DW, hi.DH
soft_glow = hi.soft_glow
plain_text = hi.plain_text
gradient_text = hi.gradient_text
lerp_color = hi.lerp_color
CABO_LO, CABO_HI = hi.CABO_LO, hi.CABO_HI
GOLD, GOLD_PALE, GOLD_DEEP = hi.GOLD, hi.GOLD_PALE, hi.GOLD_DEEP
NEAR_BLACK, WHITE = hi.NEAR_BLACK, hi.WHITE


# Skins chosen to prove the rim-light treatment across very different art: a
# warm gold-blue macaw, a fiery phoenix, a green-scaled dragon and a pale owl.
PROOF_SKINS = ["skin_bluegold", "skin_phoenix", "skin_dragon", "skin_owl"]


# =============================================================================
# Cabochon — drawn as one self-contained unit so the element can be reviewed in
# isolation. The thumbnail goes IN the well, gets a contrast punch + rim light,
# and the translucent glass dome + bezel land on top of it.
# =============================================================================

def _well_body(r, glass_lo, glass_hi, vignette):
    """The dark domed glass body the skin sits inside: a radial dome (bright-ish
    centre, deepening toward the rim) plus an inner vignette so the content
    settles into the well rather than floating on a flat disc."""
    pad = m(5)
    disc = pygame.Surface((r * 2 + pad * 2, r * 2 + pad * 2), pygame.SRCALPHA)
    c = r + pad
    for i in range(r, 0, -1):
        # gamma <1 keeps a soft lit centre; the rim drops to near-black glass
        col = lerp_color(glass_lo, glass_hi, (i / r) ** 1.28)
        pygame.draw.circle(disc, (*col, 255), (c, c), i)
    vig = pygame.Surface(disc.get_size(), pygame.SRCALPHA)
    for i in range(r, int(r * 0.70), -1):
        t = (i - r * 0.70) / (r * 0.30)
        pygame.draw.circle(vig, (0, 0, 0, int(vignette * t)), (c, c), i, max(1, m(0.8)))
    disc.blit(vig, (0, 0))
    return disc, c


def _crescent_specular(size, c, r, spec_a, spread=0.74):
    """A TRUE top-left crescent: a soft lit disc MINUS an offset disc, so only
    the arc hugging the upper-left rim survives. Never a full ring — that was
    the false-chrome tell the recipe explicitly rules out."""
    spec = pygame.Surface(size, pygame.SRCALPHA)
    sr = int(r * spread)
    pygame.draw.circle(spec, (255, 255, 255, spec_a),
                       (c - int(r * 0.20), c - int(r * 0.20)), sr)
    cut = pygame.Surface(size, pygame.SRCALPHA)
    cut.fill((255, 255, 255, 255))
    pygame.draw.circle(cut, (0, 0, 0, 0),
                       (c + int(r * 0.16), c + int(r * 0.16)), int(r * 0.82))
    spec.blit(cut, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    # keep the crescent strictly inside the dome
    smask = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.circle(smask, (255, 255, 255, 255), (c, c), r - m(2))
    spec.blit(smask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return spec


def draw_cabochon(surf, sid, cx, cy, r, *, glass_lo=CABO_LO, glass_hi=CABO_HI,
                  rim_boost=30, rim_alpha=160, spec_a=86, refract_a=64,
                  vignette=58, bezel=True):
    """One showcase cabochon: domed glass well, the rim-lit skin under glass, a
    true top-left crescent specular, a faint bottom-right refraction arc, inner
    vignette and a thin warm-gold bezel with a defined dark edge."""
    pad = m(5)
    size = (r * 2 + pad * 2, r * 2 + pad * 2)

    # 1) glass body + inner vignette
    disc, c = _well_body(r, glass_lo, glass_hi, vignette)

    # 2) skin set INSIDE the well: contrast-punched + top-left rim-lit so the
    # silhouette out-pops the dark dome. Clipped to the well so nothing spills.
    box = int(r * 1.42)
    src = parrot.get_skin_icon(sid) or parrot.get_skin_frame(sid, 1, 0.0)
    bb = src.get_bounding_rect()
    if bb.width > 0 and bb.height > 0:
        src = src.subsurface(bb).copy()
    sw, sh = src.get_size()
    s = box / max(sw, sh)
    skin = pygame.transform.smoothscale(src, (max(1, int(sw * s)), max(1, int(sh * s))))
    skin = hi._punch_contrast(skin, boost=rim_boost)
    rim = hi._rim_light(skin, alpha=rim_alpha)
    sr = skin.get_rect(center=(c, c))
    skin_layer = pygame.Surface(size, pygame.SRCALPHA)
    skin_layer.blit(rim, sr.topleft, special_flags=pygame.BLEND_ADD)
    skin_layer.blit(skin, sr.topleft)
    clip = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.circle(clip, (255, 255, 255, 255), (c, c), r - m(2))
    skin_layer.blit(clip, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    disc.blit(skin_layer, (0, 0))

    # 3) faint bottom-right refraction arc (a curved shadow inside the dome)
    arc = pygame.Surface(size, pygame.SRCALPHA)
    for k in range(m(6)):
        a = int(refract_a * (1 - k / m(6)))
        pygame.draw.arc(arc, (8, 10, 26, a),
                        (c - r + k, c - r + k, (r - k) * 2, (r - k) * 2),
                        math.radians(248), math.radians(342), max(1, m(1)))
    amask = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.circle(amask, (255, 255, 255, 255), (c, c), r - m(1))
    arc.blit(amask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    disc.blit(arc, (0, 0))

    # 4) true top-left crescent specular (disc minus offset disc) + a low broad
    # sheen bloom so the dome reads polished but still translucent.
    disc.blit(_crescent_specular(size, c, r, spec_a), (0, 0),
              special_flags=pygame.BLEND_ADD)
    bloom = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.circle(bloom, (255, 255, 255, max(0, spec_a // 2)),
                       (c - int(r * 0.32), c - int(r * 0.32)), int(r * 0.42))
    bmask = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.circle(bmask, (255, 255, 255, 255), (c, c), r - m(2))
    bloom.blit(bmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    disc.blit(bloom, (0, 0), special_flags=pygame.BLEND_ADD)

    surf.blit(disc, (cx - c, cy - c))

    # 5) thin warm-gold bezel with a DEFINED edge: dark contact keyline outermost
    # (so nothing melts into the bg), a fine warm-gold rim, an inner pale glint,
    # and a bright glass kiss on the upper-left rim arc only.
    if bezel:
        pygame.draw.circle(surf, (0, 0, 0, 190), (cx, cy), r, max(1, m(1.4)))
        pygame.draw.circle(surf, (172, 138, 66, 230), (cx, cy), r - m(0.9), max(1, m(1.2)))
        pygame.draw.circle(surf, (246, 216, 134, 160), (cx, cy), r - m(1.8), max(1, m(0.7)))
        kiss = pygame.Surface((r * 2 + m(4), r * 2 + m(4)), pygame.SRCALPHA)
        kc = r + m(2)
        pygame.draw.arc(kiss, (255, 255, 255, 130),
                        (kc - r + m(1), kc - r + m(1), r * 2 - m(2), r * 2 - m(2)),
                        math.radians(108), math.radians(192), max(1, m(1)))
        surf.blit(kiss, (cx - kc, cy - kc), special_flags=pygame.BLEND_ADD)


# =============================================================================
# Review sheet
# =============================================================================
VARIANTS = [
    # (label, kwargs) — 2-3 takes on dome depth / specular / rim-light strength.
    ("A  balanced glass", dict(rim_boost=28, rim_alpha=150, spec_a=80,
                               refract_a=60, vignette=54)),
    ("B  deep dome + hot rim", dict(glass_lo=(18, 20, 44), glass_hi=(4, 5, 16),
                                    rim_boost=40, rim_alpha=185, spec_a=98,
                                    refract_a=72, vignette=72)),
    ("C  bright crystal", dict(glass_lo=(30, 33, 64), glass_hi=(9, 11, 30),
                               rim_boost=24, rim_alpha=132, spec_a=120,
                               refract_a=48, vignette=42)),
]


def _panel_label(surf, txt, cx, y, size=13):
    plain_text(surf, txt, font(size), (cx, y), (236, 230, 210),
               shadow_a=170, weight=m(0.7), keyline=(8, 9, 22), kw=m(0.9))


def render():
    hi._build_static_bg()
    surf = pygame.Surface((DW, DH))
    hi.draw_bg(surf)

    gradient_text(surf, "GLASS CABOCHON", font(22), (DW // 2, m(30)),
                  (255, 246, 200), (242, 182, 70), tracking=m(2),
                  keyline=(80, 42, 8), kw=m(1.2), weight=m(1.1))
    plain_text(surf, "domed well  -  rim-lit thumbnail under glass  -  true crescent specular",
               font(10), (DW // 2, m(52)), (196, 200, 224), shadow_a=150, weight=m(0.5))

    # Big hero row: each variant shown at large scale on the same skin so the
    # dome/specular/rim differences read clearly side by side.
    big_r = m(58)
    row_y = m(150)
    cols = len(VARIANTS)
    for i, (label, kw) in enumerate(VARIANTS):
        cx = int(DW * (i + 0.5) / cols)
        soft_glow(surf, cx, row_y, int(big_r * 1.25), (40, 44, 96), 70, layers=8)
        draw_cabochon(surf, "skin_bluegold", cx, row_y, big_r, **kw)
        _panel_label(surf, label, cx, row_y + big_r + m(26), size=12)

    # Proof grid: the winning-feel middle variant (A balanced) across four very
    # different skins so the treatment is proven on varied source art.
    _panel_label(surf, "PROVEN ACROSS SKINS  (variant A)", DW // 2, m(330), size=13)
    prr = m(46)
    pry = m(400)
    pcols = len(PROOF_SKINS)
    for i, sid in enumerate(PROOF_SKINS):
        cx = int(DW * (i + 0.5) / pcols)
        soft_glow(surf, cx, pry, int(prr * 1.25), (40, 44, 96), 60, layers=8)
        draw_cabochon(surf, sid, cx, pry, prr, **VARIANTS[0][1])
        nm = hi._name(sid) if hasattr(hi, "_name") else sid
        _panel_label(surf, nm, cx, pry + prr + m(22), size=10)

    # In-card context: a cabochon at the true card size (R_DISC) next to a hero
    # so the reviewer can confirm it survives the actual grid scale.
    _panel_label(surf, "AT TRUE CARD SCALE  (R_DISC=23)  vs  HERO", DW // 2, m(508), size=12)
    small_r = m(hi.R_DISC)
    sx = int(DW * 0.32)
    sy = m(570)
    soft_glow(surf, sx, sy, int(small_r * 1.4), (40, 44, 96), 60, layers=6)
    draw_cabochon(surf, "skin_phoenix", sx, sy, small_r, **VARIANTS[0][1])
    _panel_label(surf, "card size", sx, sy + small_r + m(16), size=9)

    hx = int(DW * 0.68)
    draw_cabochon(surf, "skin_phoenix", hx, sy, int(small_r * 1.7), **VARIANTS[0][1])
    _panel_label(surf, "hero size", hx, sy + int(small_r * 1.7) + m(16), size=9)

    out = pygame.transform.smoothscale(surf, (DW // SS, DH // SS))
    dst = os.path.join(_HERE, "round_1.png")
    pygame.image.save(out, dst)
    return dst


if __name__ == "__main__":
    pygame.init()
    pygame.display.set_mode((1, 1))
    path = render()
    print("saved", path)
