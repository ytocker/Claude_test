"""
RICHES family — six engraved center glyphs for the GOLD wealth-ladder
achievements (v2 LOCKED spec). Procedural, single-colour engrave idiom shared
with ``game/achievement_icons.py``.

The ladder is read off ONE escalating cue: the CONTAINER that holds the money
grows rung by rung — none -> 3-stack -> drawstring pouch -> tall safe -> crowned
hoard -> the Midas hand turning a coin to gold. The ringed ``$`` dollar coin is
the constant thread woven through every rung (a single ``_coin`` helper, so the
glyph is pixel-identical wherever it appears), and Midas alone carries a
saturated gold gem-spark routed through ``_accent`` so it stays monochrome when
the medal is dormant. No numerals, no sub-5px detail; every shape is a bold
filled disc / polygon / thick line so the read survives at the 44px row size.
"""
from __future__ import annotations

import math
import pygame

# These mirror the host module's engrave hooks. The render harness wires the
# real functions in by importing ``game.achievement_icons`` and copying its
# ``_GLYPH_SH`` / ``_glyph_font`` / ``_accent`` onto this module before stamping,
# so the inset-shadow tone, font cache and dormant-desaturation stay identical to
# the rest of the medallion family rather than being re-implemented here.
_GLYPH_SH = (32, 18, 44)


def _glyph_font(px: int):
    # Replaced at import time by the host module's cached SysFont so the ``$``
    # matches every other coin glyph; this stand-in keeps the file importable
    # on its own.
    return pygame.font.SysFont(None, px, bold=True)


def _accent(lit_col, dormant_col=(170, 162, 150)):
    # Replaced at import time by the host's state-aware accent resolver.
    return lit_col


# ── the constant thread: the ringed ``$`` coin ───────────────────────────────
#
# Lifted verbatim from ``_glyph_coin`` so the dollar token is the SAME object on
# every rung. ``rscale`` shrinks it where several coins must share the box; the
# ring weight tracks the coin radius so a small spilled coin never goes hairline.

def _coin(surf, cx, cy, r, col, rscale=0.66, ring=None):
    rr = max(4, int(r * rscale))
    if ring is None:
        ring = max(3, int(r * rscale / 8 * 12) // 12) if False else max(2, rr // 4)
    pygame.draw.circle(surf, col, (cx, cy), rr, ring)
    f = _glyph_font(int(rr * 1.7))
    g = f.render("$", True, col)
    surf.blit(g, g.get_rect(center=(cx, cy)))


def _crownlet(surf, cx, cy, r, col, w=None):
    # The shared L4 rank crownlet — a 3-point engraved coronet seated on top of
    # a motif. Faint cherry-on-top per spec; the container growth is the real
    # read, so this stays small.
    w = w or max(2, r // 12)
    half = r * 0.46
    base_y = cy
    pts = [
        (cx - half, base_y),
        (cx - half, base_y - r * 0.20),
        (cx - half * 0.5, base_y - r * 0.02),
        (cx, base_y - r * 0.34),
        (cx + half * 0.5, base_y - r * 0.02),
        (cx + half, base_y - r * 0.20),
        (cx + half, base_y),
    ]
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in pts])


def _pips(surf, cx, cy, r, col, n):
    # L1/L2 rank dots tucked under a motif — faint optional accent only.
    pr = max(2, r // 12)
    span = pr * 3 * (n - 1)
    for i in range(n):
        x = cx - span // 2 + i * pr * 3
        pygame.draw.circle(surf, col, (int(x), int(cy)), pr)


# ── rung 1: coin_25_run — Pocket Change ──────────────────────────────────────

def _glyph_coin_25_run(surf, cx, cy, r, col):
    # ONE ``$`` coin, slightly tilted, with two tiny coin-edge nicks beside it —
    # loose pocket change. The bare coin (no container) is the bottom rung.
    cox, coy = cx - int(r * 0.06), cy - int(r * 0.04)
    _coin(surf, cox, coy, r, col, rscale=0.66)
    # two edge-nick coins peeking from behind, lower-right — "loose change"
    for dx, dy, sc in ((0.50, 0.42, 0.30), (0.66, 0.20, 0.24)):
        nx, ny = cx + int(r * dx), cy + int(r * dy)
        nr = max(4, int(r * sc))
        pygame.draw.circle(surf, _GLYPH_SH, (nx + 1, ny + 1), nr)
        pygame.draw.circle(surf, col, (nx, ny), nr)
        pygame.draw.circle(surf, _GLYPH_SH, (nx, ny), nr, max(1, nr // 3))


# ── rung 2: coin_100_run — Coin Run ──────────────────────────────────────────

def _glyph_coin_100_run(surf, cx, cy, r, col):
    # A short STACK of 3 ``$`` coins — solid overlapping discs climbing up-left,
    # each a thick coin-edge rim with a dark gap between so the COUNT reads, the
    # top one face-on showing the ringed ``$``. Container = a stack. L1 pips.
    cr = int(r * 0.40)               # each coin's radius
    rim = max(3, cr // 3)            # thick struck edge
    # back-to-front: lower-right coin first, climbing up-left
    centres = [
        (cx + int(r * 0.24), cy + int(r * 0.40)),
        (cx, cy + int(r * 0.06)),
        (cx - int(r * 0.24), cy - int(r * 0.30)),   # top, face-on with ``$``
    ]
    for i, (px, py) in enumerate(centres):
        # dark backing disc gives each coin a clean edge against its neighbour
        pygame.draw.circle(surf, _GLYPH_SH, (px, py), cr + max(1, rim // 2))
        pygame.draw.circle(surf, col, (px, py), cr)
        if i < 2:
            # lower coins read edge-on: hollow ring + a single centre score line
            pygame.draw.circle(surf, _GLYPH_SH, (px, py), cr - rim)
            pygame.draw.line(surf, col, (px - cr + rim, py), (px + cr - rim, py),
                             max(2, rim // 2))
    tx, ty = centres[-1]
    _coin(surf, tx, ty, r, col, rscale=0.40)
    _pips(surf, cx, cy + int(r * 0.80), r, col, 1)


# ── rung 3: coins_500_life — Coin Collector ──────────────────────────────────

def _glyph_coins_500_life(surf, cx, cy, r, col):
    # A drawstring COIN POUCH with a ``$`` on its belly and two coins spilling
    # at its foot. Container = a sack. L2 wreath ticks.
    # sack body — a round-bottomed bag, narrowing to a tied neck
    by = cy + int(r * 0.10)
    bw = int(r * 0.78)
    bh = int(r * 0.74)
    body = [
        (cx - int(bw * 0.42), by - int(bh * 0.30)),   # neck left
        (cx - bw, by + int(bh * 0.30)),               # bulge left
        (cx - int(bw * 0.66), by + bh),               # base left
        (cx + int(bw * 0.66), by + bh),               # base right
        (cx + bw, by + int(bh * 0.30)),               # bulge right
        (cx + int(bw * 0.42), by - int(bh * 0.30)),   # neck right
    ]
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in body])
    # cinched neck — a narrow band above the bulge
    neck = pygame.Rect(cx - int(bw * 0.46), by - int(bh * 0.52),
                       int(bw * 0.92), max(4, int(bh * 0.24)))
    pygame.draw.rect(surf, col, neck, border_radius=max(2, r // 12))
    # drawstring tie ears flaring up off the neck
    for sgn in (-1, 1):
        ex = cx + sgn * int(bw * 0.40)
        pygame.draw.line(surf, col, (cx + sgn * int(bw * 0.18), by - int(bh * 0.44)),
                         (ex, by - int(bh * 0.78)), max(3, r // 9))
    # the ``$`` token engraved into the sack's belly (inset, so it reads sunk)
    f = _glyph_font(int(r * 0.78))
    g = f.render("$", True, _GLYPH_SH)
    surf.blit(g, g.get_rect(center=(cx, by + int(bh * 0.42))))
    # two coins spilling at the foot, lower-right
    for dx, dy, sc in ((0.74, 0.86, 0.26), (0.96, 0.66, 0.20)):
        nx, ny = cx + int(r * dx), cy + int(r * dy)
        nr = max(4, int(r * sc))
        pygame.draw.circle(surf, _GLYPH_SH, (nx + 1, ny + 1), nr)
        pygame.draw.circle(surf, col, (nx, ny), nr)
        pygame.draw.circle(surf, _GLYPH_SH, (nx, ny), nr, max(1, nr // 3))


# ── rung 4: coins_5000_life — Coin Vault ─────────────────────────────────────

def _glyph_coins_5000_life(surf, cx, cy, r, col):
    # A TALL SAFE drawn portrait/upright — clearly taller than wide — with a
    # thick bezel door-PORTHOLE (a heavy ringed circular door) and a small dial
    # nub. The TALL aspect + bezel ring separate it from the WIDE-LOW chest.
    bw = int(r * 1.08)       # body width
    bh = int(r * 1.48)       # body height — TALL, clearly > wide
    bx = cx - bw // 2
    bty = cy - int(bh * 0.50)
    body = pygame.Rect(bx, bty, bw, bh)
    pygame.draw.rect(surf, col, body, border_radius=max(3, r // 7))
    # short stubby feet so it stands like a strongbox, not a lid
    fh = max(3, int(r * 0.16))
    for sgn in (-1, 1):
        fx = cx + sgn * int(bw * 0.30)
        pygame.draw.rect(surf, col, (fx - max(2, r // 12), bty + bh,
                                     max(4, r // 6), fh))
    # heavy bezel door-PORTHOLE: a thick ring filling most of the body, drawn
    # in the inset tone so the door reads recessed into the safe face
    dcy = cy + int(r * 0.02)
    dr = int(min(bw, bh) * 0.42)
    pygame.draw.circle(surf, _GLYPH_SH, (cx, dcy), dr)
    pygame.draw.circle(surf, col, (cx, dcy), dr, max(4, r // 7))   # thick bezel
    pygame.draw.circle(surf, _GLYPH_SH, (cx, dcy), max(3, dr // 2))  # inner well
    # combination dial nub at the door's centre + a couple of spoke handles
    pygame.draw.circle(surf, col, (cx, dcy), max(3, int(dr * 0.30)))
    for a in (math.radians(35), math.radians(215)):
        hx = cx + int(math.cos(a) * dr * 0.62)
        hy = dcy + int(math.sin(a) * dr * 0.62)
        pygame.draw.line(surf, col, (cx, dcy), (hx, hy), max(3, r // 11))
    # ``$`` token stamped on the safe's top band so the dollar thread persists
    f = _glyph_font(int(r * 0.42))
    g = f.render("$", True, _GLYPH_SH)
    surf.blit(g, g.get_rect(center=(cx, bty + int(bh * 0.14))))


# ── rung 5: coin_tycoon — Coin Tycoon ────────────────────────────────────────

def _glyph_coin_tycoon(surf, cx, cy, r, col):
    # A treasure HOARD: a mound of stacked coins topped by a face-on ``$`` coin,
    # two arcs of coins flanking it, crowned by the L4 coronet — wealth
    # overflowing. Container = an open pile (no walls; the money spills out).
    base_y = cy + int(r * 0.62)
    # the mound silhouette — a low heaped trapezoid of bullion
    mound = [
        (cx - int(r * 0.92), base_y),
        (cx - int(r * 0.52), base_y - int(r * 0.42)),
        (cx + int(r * 0.52), base_y - int(r * 0.42)),
        (cx + int(r * 0.92), base_y),
    ]
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in mound])
    # two flanking arcs of stacked coins riding the mound's shoulders
    for sgn in (-1, 1):
        for i, (fx, fy, sc) in enumerate((
            (0.66, 0.30, 0.22), (0.40, 0.50, 0.22), (0.18, 0.62, 0.22))):
            nx = cx + sgn * int(r * fx)
            ny = base_y - int(r * fy)
            nr = max(4, int(r * sc))
            pygame.draw.circle(surf, _GLYPH_SH, (nx + 1, ny + 1), nr)
            pygame.draw.circle(surf, col, (nx, ny), nr)
            pygame.draw.circle(surf, _GLYPH_SH, (nx, ny), nr, max(1, nr // 3))
    # the crowning face-on ``$`` coin riding clear above the heap (the constant
    # thread) — a dark backing disc lifts it off the mound so it never merges
    coy = base_y - int(r * 0.74)
    pygame.draw.circle(surf, _GLYPH_SH, (cx, coy), int(r * 0.40) + 2)
    _coin(surf, cx, coy, r, col, rscale=0.40)
    # L4 crownlet seated above the hoard — the wealth is royal now
    _crownlet(surf, cx, cy - int(r * 0.74), r, col)


# ── rung 6: midas — Midas Touch ──────────────────────────────────────────────

def _glyph_midas(surf, cx, cy, r, col):
    # An open PALM (three fat finger-stubs + a thumb, no knuckle detail) beneath
    # a RADIANT ``$`` coin, with a single unlock-only GOLD gem-spark at the
    # fingertip. The HAND is exclusive to Midas — the apex of the wealth ladder:
    # the touch that turns coins to gold.
    # radiant coin riding high, the constant thread, with short emanating rays
    coy = cy - int(r * 0.40)
    cor = int(r * 0.40)
    for i in range(8):
        a = i * math.pi / 4
        x1 = cx + int(math.cos(a) * cor * 1.30)
        y1 = coy + int(math.sin(a) * cor * 1.30)
        x2 = cx + int(math.cos(a) * cor * 1.74)
        y2 = coy + int(math.sin(a) * cor * 1.74)
        pygame.draw.line(surf, col, (x1, y1), (x2, y2), max(2, r // 10))
    _coin(surf, cx, coy, r, col, rscale=0.40)
    # the open palm cupped below, reaching up toward the coin — a rounded heel
    pw = int(r * 0.74)        # palm half-width
    py = cy + int(r * 0.70)   # palm base line
    fy_top = py - int(r * 0.30)
    palm = [
        (cx - pw, fy_top),
        (cx - int(pw * 0.78), py),                   # heel left
        (cx, py + int(r * 0.18)),                    # rounded heel bottom
        (cx + int(pw * 0.78), py),                   # heel right
        (cx + pw, fy_top),
    ]
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in palm])
    # three fat finger-stubs splayed up off the heel toward the coin, each set
    # off by a dark gap so the fingers read as separate stubs, not a paddle
    finger_w = max(6, int(r * 0.24))
    flen = int(r * 0.46)
    for fx in (-0.50, 0.0, 0.50):
        x = cx + int(pw * fx)
        # dark slot between fingers
        pygame.draw.rect(surf, _GLYPH_SH,
                         (x - finger_w // 2 - 2, fy_top - flen,
                          finger_w + 4, flen + 4),
                         border_radius=finger_w // 2 + 2)
        pygame.draw.rect(surf, col, (x - finger_w // 2, fy_top - flen,
                                     finger_w, flen + max(2, r // 12)),
                         border_radius=finger_w // 2)
    # thumb angled out off the right heel (open-hand gesture, reaching the coin)
    thumb_w = max(6, int(r * 0.22))
    pygame.draw.line(surf, col, (cx + int(pw * 0.78), py - int(r * 0.04)),
                     (cx + int(pw * 1.08), fy_top - int(r * 0.18)), thumb_w)
    # single GOLD four-point gem-spark over the middle fingertip — the only
    # saturated accent in the family, desaturating to bronze when dormant
    gx = cx
    gy = fy_top - flen - int(r * 0.10)
    gold = _accent((255, 214, 92))
    sp = max(4, int(r * 0.22))
    pygame.draw.polygon(surf, _GLYPH_SH, [
        (gx, gy - sp - 1), (gx + sp // 2 + 1, gy), (gx, gy + sp + 1),
        (gx - sp // 2 - 1, gy)])
    pygame.draw.polygon(surf, gold, [
        (gx, gy - sp), (gx + sp * 2 // 5, gy),
        (gx, gy + sp), (gx - sp * 2 // 5, gy)])
    pygame.draw.polygon(surf, gold, [
        (gx - sp, gy), (gx, gy - sp * 2 // 5),
        (gx + sp, gy), (gx, gy + sp * 2 // 5)])


GLYPHS = {
    "coin_25_run": _glyph_coin_25_run,
    "coin_100_run": _glyph_coin_100_run,
    "coins_500_life": _glyph_coins_500_life,
    "coins_5000_life": _glyph_coins_5000_life,
    "coin_tycoon": _glyph_coin_tycoon,
    "midas": _glyph_midas,
}
