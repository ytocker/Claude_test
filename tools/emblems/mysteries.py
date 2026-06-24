"""Bespoke engraved center glyphs for the six amethyst MYSTERIES achievements.

These follow the struck-metal engrave idiom of ``game.achievement_icons``: each
``_glyph_<id>(surf, cx, cy, r, col)`` draws BOLD filled polygons / thick lines /
discs in the passed ``col`` only, so the builder's down-right inset + up-left
sheen passes give every shape the same relief. Glyph footprint is ~22px (the
builder calls them at ``gr = R*0.56``); nothing thinner than ~3px or smaller
than ~5px, since the amethyst well + sparkle ring already do the "rare" work and
fine detail muds at 44px row size.

The Mysteries lean enigmatic — one bold silhouette each. ``made_a_wish`` and
``poisoned`` deliberately share the same genie-lamp base (a granted wish vs a
cursed one) and flip the resolution: three rising wisp-stars vs an enlarged
skull boiling out of the smoke.

This is a render-harness asset under ``tools/`` — it patches the live glyph
table at runtime (see ``render_mysteries.py``) and ships nothing into the game.
"""
from __future__ import annotations

import math

import pygame

# The builder stamps these with a down-right inset shadow in this tone; matching
# the live module lets the shared-lamp skull/wisp accents read as recessed.
_GLYPH_SH = (34, 22, 58)


def _lamp(surf, cx, cy, r, col):
    """The genie-lamp body shared by ``made_a_wish`` and ``poisoned`` — a teapot
    silhouette pulled down into the lower box so the spout-smoke has room to
    resolve above it. A round bowl, an up-curled spout to the right, a knob lid
    and a handle-loop to the left; a base foot grounds it as a lamp, not a pot."""
    by = cy + int(r * 0.30)                       # lamp body centre, sunk low
    bw, bh = int(r * 1.04), int(r * 0.56)
    pygame.draw.ellipse(surf, col, (cx - bw // 2, by - bh // 2, bw, bh))
    # Spout: a stubby up-flicked nozzle on the right where the smoke issues.
    pygame.draw.polygon(surf, col, [
        (cx + int(r * 0.34), by - int(r * 0.06)),
        (cx + int(r * 0.78), by - int(r * 0.30)),
        (cx + int(r * 0.66), by - int(r * 0.02)),
        (cx + int(r * 0.40), by + int(r * 0.16)),
    ])
    # Handle loop on the left — a thick open arc reading as a grab handle.
    pygame.draw.arc(surf, col, (cx - int(r * 0.86), by - int(r * 0.26),
                               int(r * 0.46), int(r * 0.52)),
                    math.radians(40), math.radians(320), max(3, r // 9))
    # Lid knob crowning the bowl so the dome reads as a lid, not a ball.
    pygame.draw.circle(surf, col, (cx - int(r * 0.04), by - int(bh * 0.62)),
                       max(3, r // 9))
    # Flat foot grounds the lamp.
    pygame.draw.rect(surf, col, (cx - int(r * 0.32), by + bh // 2 - max(2, r // 14),
                                 int(r * 0.64), max(3, r // 9)),
                     border_radius=max(1, r // 16))


def _glyph_made_a_wish(surf, cx, cy, r, col):
    # Granted wish: the lamp with THREE wisp-stars rising from the spout, the
    # tallest curling like a question to keep it enigmatic. Count = 3 carries the
    # "three wishes" read; the stars climb up-right out of the nozzle.
    _lamp(surf, cx, cy, r, col)
    sx = cx + int(r * 0.62)                        # smoke origin, above the spout
    sy = cy - int(r * 0.06)
    # A thin smoke column curling up so the stars read as issuing from the lamp.
    pygame.draw.arc(surf, col, (sx - int(r * 0.30), sy - int(r * 0.96),
                               int(r * 0.60), int(r * 0.96)),
                    math.radians(-70), math.radians(150), max(2, r // 12))
    # Three four-point wisp-stars stepping up the column, smallest at the lamp.
    stars = [
        (sx - int(r * 0.02), sy - int(r * 0.30), 0.16),
        (sx - int(r * 0.26), sy - int(r * 0.62), 0.20),
        (sx + int(r * 0.04), sy - int(r * 0.96), 0.26),
    ]
    for px, py, sc in stars:
        sr = r * sc
        pygame.draw.polygon(surf, col, [
            (px, py - sr), (px + sr * 0.28, py - sr * 0.28),
            (px + sr, py), (px + sr * 0.28, py + sr * 0.28),
            (px, py + sr), (px - sr * 0.28, py + sr * 0.28),
            (px - sr, py), (px - sr * 0.28, py - sr * 0.28),
        ])


def _glyph_poisoned(surf, cx, cy, r, col):
    # Cursed wish: the SAME lamp, but the smoke boils up into an ENLARGED skull —
    # the nasty surprise. The skull dominates the upper half so the read flips
    # entirely from the three delicate wisps of ``made_a_wish``.
    _lamp(surf, cx, cy, r, col)
    sx = cx + int(r * 0.60)
    sy = cy - int(r * 0.04)
    # Two short smoke curls feeding up from the spout into the skull's jaw.
    pygame.draw.arc(surf, col, (sx - int(r * 0.34), sy - int(r * 0.52),
                               int(r * 0.50), int(r * 0.56)),
                    math.radians(-60), math.radians(120), max(3, r // 11))
    # Skull, enlarged and centred over the lamp's shoulder.
    skx = cx - int(r * 0.06)
    sky = cy - int(r * 0.56)
    cr = int(r * 0.50)                             # big cranium
    pygame.draw.circle(surf, col, (skx, sky), cr)
    # Squared jaw block below the cranium.
    pygame.draw.rect(surf, col, (skx - int(cr * 0.62), sky + int(cr * 0.42),
                                 int(cr * 1.24), int(cr * 0.62)),
                     border_radius=max(2, r // 12))
    # Two deep eye sockets + a nasal notch, recessed in the shadow tone.
    er = max(3, int(cr * 0.34))
    for dx in (-0.42, 0.42):
        pygame.draw.circle(surf, _GLYPH_SH, (skx + int(cr * dx), sky - int(cr * 0.08)), er)
    pygame.draw.polygon(surf, _GLYPH_SH, [
        (skx, sky + int(cr * 0.30)),
        (skx - max(2, int(cr * 0.16)), sky + int(cr * 0.58)),
        (skx + max(2, int(cr * 0.16)), sky + int(cr * 0.58)),
    ])
    # Two tooth gaps notched into the jaw so it reads as a grin, not a chin.
    for dx in (-int(cr * 0.22), int(cr * 0.22)):
        pygame.draw.line(surf, _GLYPH_SH, (skx + dx, sky + int(cr * 0.46)),
                         (skx + dx, sky + int(cr * 0.96)), max(2, r // 14))


def _glyph_knighted(surf, cx, cy, r, col):
    # Survived under a knight's guard: an upright sword + a bold shield behind a
    # great-helm — a guardian read, not just a helmet. The sword's cross-guard
    # makes a subtle ``+``. The helm is offset right and the shield offset left
    # so the trio reads as three distinct elements, not one fused blob, even at
    # 44px row size.
    hx = cx + int(r * 0.20)                        # helm centre, nudged right
    # Sword behind the helm: a bold vertical blade rising up the right.
    blade_w = max(4, int(r * 0.18))
    pygame.draw.rect(surf, col, (hx - blade_w // 2, cy - int(r * 0.96),
                                 blade_w, int(r * 0.86)))
    pygame.draw.circle(surf, col, (hx, cy - int(r * 0.96)), max(3, r // 8))
    # Cross-guard — a bold horizontal bar making the + with the blade.
    pygame.draw.rect(surf, col, (hx - int(r * 0.40), cy - int(r * 0.52),
                                 int(r * 0.80), max(4, r // 7)),
                     border_radius=max(1, r // 16))
    # A bold heater shield to the LEFT, clearly clear of the helm so it survives
    # at row size — a wide flat top tapering to a point.
    pygame.draw.polygon(surf, col, [
        (cx - int(r * 0.92), cy - int(r * 0.34)),
        (cx - int(r * 0.18), cy - int(r * 0.34)),
        (cx - int(r * 0.18), cy + int(r * 0.22)),
        (cx - int(r * 0.55), cy + int(r * 0.66)),
        (cx - int(r * 0.92), cy + int(r * 0.22)),
    ])
    # A recessed boss-cross on the shield so it reads as heraldry, not a slab.
    scx = cx - int(r * 0.55)
    pygame.draw.line(surf, _GLYPH_SH, (scx, cy - int(r * 0.22)),
                     (scx, cy + int(r * 0.40)), max(2, r // 13))
    pygame.draw.line(surf, _GLYPH_SH, (scx - int(r * 0.22), cy + int(r * 0.04)),
                     (scx + int(r * 0.22), cy + int(r * 0.04)), max(2, r // 13))
    # The great-helm, dominant, sitting over the sword's lower half.
    helm = pygame.Rect(int(hx - r * 0.40), int(cy - r * 0.18),
                       int(r * 0.80), int(r * 0.92))
    pygame.draw.rect(surf, col, helm, border_radius=max(3, r // 5))
    # Visor slit, recessed.
    pygame.draw.rect(surf, _GLYPH_SH, (int(hx - r * 0.32), int(cy + r * 0.18),
                                       int(r * 0.64), max(4, r // 7)),
                     border_radius=max(1, r // 14))
    # A breath-hole cross notched below the slit so it reads as a helm face.
    pygame.draw.line(surf, _GLYPH_SH, (hx, int(cy + r * 0.40)),
                     (hx, int(cy + r * 0.66)), max(2, r // 14))


def _glyph_treasure_hunter(surf, cx, cy, r, col):
    # X marks the spot: an open chest, lid ajar, an engraved X across the lid.
    # No gem-spark (per v2 lock) — the chest + tilted-open lid + X is the read.
    bx0, by0 = cx - int(r * 0.66), cy + int(r * 0.04)
    bw, bh = int(r * 1.32), int(r * 0.62)
    # Chest body — a wide low box.
    pygame.draw.rect(surf, col, (bx0, by0, bw, bh), border_radius=max(2, r // 10))
    # Dark mouth where the lid lifts away, so the chest reads as OPEN.
    pygame.draw.rect(surf, _GLYPH_SH, (bx0 + max(2, r // 12), by0 + max(2, r // 14),
                                       bw - max(4, r // 6), int(r * 0.18)),
                     border_radius=max(1, r // 16))
    # Lid — a tilted bar hinged at the back-right, swung open up-left so it sits
    # ajar above the body rather than flush.
    hinge = (cx + int(r * 0.62), cy - int(r * 0.04))
    lift = (cx - int(r * 0.66), cy - int(r * 0.46))
    th = max(4, int(r * 0.26))
    ang = math.atan2(lift[1] - hinge[1], lift[0] - hinge[0])
    nx, ny = -math.sin(ang), math.cos(ang)
    lid = [
        (hinge[0], hinge[1]),
        (lift[0], lift[1]),
        (lift[0] + nx * th, lift[1] + ny * th),
        (hinge[0] + nx * th, hinge[1] + ny * th),
    ]
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in lid])
    # Engraved X across the lid face, recessed in the shadow tone.
    lcx = (hinge[0] + lift[0]) // 2 + int(nx * th * 0.5)
    lcy = (hinge[1] + lift[1]) // 2 + int(ny * th * 0.5)
    xr = int(r * 0.34)
    xw = max(3, r // 9)                             # bolder so the X survives 44px
    pygame.draw.line(surf, _GLYPH_SH, (lcx - xr, lcy - int(xr * 0.55)),
                     (lcx + xr, lcy + int(xr * 0.55)), xw)
    pygame.draw.line(surf, _GLYPH_SH, (lcx - xr, lcy + int(xr * 0.55)),
                     (lcx + xr, lcy - int(xr * 0.55)), xw)
    # A clasp nub on the chest front so the body reads as a chest.
    pygame.draw.rect(surf, _GLYPH_SH, (cx - max(3, r // 11), by0 + int(bh * 0.46),
                                       max(6, r // 5), int(bh * 0.42)),
                     border_radius=max(1, r // 16))


def _glyph_jackpot(surf, cx, cy, r, col):
    # Jackpot: the slot-WINDOW frame is the dominant read (per v2 lock — rely on
    # frame + tone, not legible symbols). A bold rounded cabinet window with two
    # vertical reel-dividers and THREE matched dots in a row; a burst-star peeks
    # behind one top corner so it reads as a win.
    fw, fh = int(r * 1.5), int(r * 1.04)
    fx, fy = cx - fw // 2, cy - fh // 2
    # Burst-star behind the upper-right, signalling the top-tier win.
    bsx, bsy = cx + int(r * 0.6), cy - int(r * 0.58)
    bsr = r * 0.42
    pygame.draw.polygon(surf, col, [
        (bsx, bsy - bsr), (bsx + bsr * 0.3, bsy - bsr * 0.3),
        (bsx + bsr, bsy), (bsx + bsr * 0.3, bsy + bsr * 0.3),
        (bsx, bsy + bsr), (bsx - bsr * 0.3, bsy + bsr * 0.3),
        (bsx - bsr, bsy), (bsx - bsr * 0.3, bsy - bsr * 0.3),
    ])
    # The window frame — a thick rounded border with a recessed dark interior.
    bw = max(4, int(r * 0.20))
    pygame.draw.rect(surf, col, (fx, fy, fw, fh), border_radius=max(3, r // 5))
    pygame.draw.rect(surf, _GLYPH_SH, (fx + bw, fy + bw, fw - bw * 2, fh - bw * 2),
                     border_radius=max(2, r // 8))
    # Two reel-dividers splitting the window into three bays.
    for f in (1 / 3, 2 / 3):
        dx = fx + int(fw * f)
        pygame.draw.line(surf, col, (dx, fy + bw), (dx, fy + fh - bw), max(2, r // 14))
    # Three matched bold dots, one per bay, on the centre line.
    dot_r = max(3, int(r * 0.16))
    for f in (1 / 6, 1 / 2, 5 / 6):
        pygame.draw.circle(surf, col, (fx + int(fw * f), cy), dot_r)


def _glyph_rail_rider(surf, cx, cy, r, col):
    # Off the rails: a mine-cart LEAPING off a HARD-SNAPPED rail end. The rail
    # runs in low from the left to a clean angular break, past which a short
    # stub bends sharply DOWN — a crisp jagged snap with an open angular gap, not
    # feathered shards. The cart is flung UP-AND-OFF the break, tilted nose-up
    # with a motion-arc trailing, so "leaping off / airborne" is the whole read
    # and it can't be mistaken for Skater's carts sitting flat ON the rail.
    rw = max(4, int(r * 0.18))
    # Intact rail coming in nearly level from the lower-left to the break point.
    x0, y0 = cx - int(r * 0.90), cy + int(r * 0.52)
    bx, by = cx - int(r * 0.10), cy + int(r * 0.40)   # the break point
    pygame.draw.line(surf, col, (x0, y0), (bx, by), rw)
    # Two cross-ties under the intact rail so it reads as track.
    for f in (0.3, 0.66):
        tx = x0 + (bx - x0) * f
        ty = y0 + (by - y0) * f
        pygame.draw.line(surf, col, (int(tx), int(ty + r * 0.04)),
                         (int(tx), int(ty + r * 0.26)), max(2, r // 13))
    # Jagged snapped tip on the standing rail — a small notch at the break.
    pygame.draw.polygon(surf, col, [
        (bx, by - rw),
        (bx + int(r * 0.12), by - int(r * 0.02)),
        (bx, by + rw),
        (bx - int(r * 0.06), by),
    ])
    # The snapped-off stub bent HARD downward past an open angular gap — it
    # starts beyond a clear gap and drops steeply, the broken end pointing down.
    gx, gy = bx + int(r * 0.26), by + int(r * 0.06)   # stub starts after a gap
    ex, ey = gx + int(r * 0.16), gy + int(r * 0.58)   # bent sharply down
    pygame.draw.line(surf, col, (gx, gy), (ex, ey), rw)
    # Jagged broken tip on the stub's upper (gap-facing) end.
    pygame.draw.polygon(surf, col, [
        (gx - int(r * 0.10), gy - int(r * 0.02)),
        (gx + int(r * 0.06), gy - int(r * 0.06)),
        (gx + int(r * 0.04), gy + int(r * 0.10)),
    ])
    # Motion-arc sweeping the cart up off the break — the launch trail.
    pygame.draw.arc(surf, col, (cx - int(r * 0.22), cy - int(r * 0.66),
                               int(r * 0.96), int(r * 0.78)),
                    math.radians(205), math.radians(345), max(3, r // 12))
    # The cart — an open tub, flung up and tilted nose-up, clear of the rail.
    ccx, ccy = cx + int(r * 0.40), cy - int(r * 0.34)
    tilt = math.radians(-30)
    ct, st = math.cos(tilt), math.sin(tilt)

    def _rot(dx, dy):
        return (int(ccx + dx * ct - dy * st), int(ccy + dx * st + dy * ct))

    tub = [_rot(-r * 0.42, -r * 0.08), _rot(r * 0.42, -r * 0.08),
           _rot(r * 0.32, r * 0.34), _rot(-r * 0.32, r * 0.34)]
    pygame.draw.polygon(surf, col, tub)
    # Hollow the tub so it reads as an open cart, not a solid block.
    inner = [_rot(-r * 0.30, -r * 0.20), _rot(r * 0.30, -r * 0.20),
             _rot(r * 0.22, r * 0.16), _rot(-r * 0.22, r * 0.16)]
    pygame.draw.polygon(surf, _GLYPH_SH, inner)
    # Two cart-wheels under the tub (airborne, so no track contact).
    for dx in (-r * 0.26, r * 0.26):
        wc = _rot(dx, r * 0.46)
        pygame.draw.circle(surf, col, wc, max(3, int(r * 0.14)))
        pygame.draw.circle(surf, _GLYPH_SH, wc, max(1, int(r * 0.05)))


GLYPHS = {
    "made_a_wish": _glyph_made_a_wish,
    "knighted": _glyph_knighted,
    "treasure_hunter": _glyph_treasure_hunter,
    "jackpot": _glyph_jackpot,
    "rail_rider": _glyph_rail_rider,
    "poisoned": _glyph_poisoned,
}
