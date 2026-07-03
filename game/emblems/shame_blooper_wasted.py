"""
Bespoke engraved center glyphs for the SHAME — Blooper Reel + Wasted Opportunity
(Wall of Shame) medallions, rendered TARNISHED (cracked-pewter anti-trophy).

Same single-colour engrave idiom as ``game.achievement_icons``: each
``_glyph_<id>(surf, cx, cy, r, col)`` lays BOLD filled shapes in the passed
``col`` only (the builder strokes a down-right inset shadow + up-left sheen for
the struck-relief look), with recessed sockets/notches drawn in the shared
engraved-shadow tone ``_SH``. Authored to the ~44px legibility floor: nothing
thinner than ~3px or smaller than ~5px, ONE decisive silhouette per glyph with
the JOKE living in the shape, never a figure-plus-props tangle.

The read per id:
  * bullet_bystander — an hourglass split by a collision-burst: time crawled and
                       you SPLATTED anyway.
  * cursed           — a skull breathing out a genie-wisp: the wish that killed
                       you (SKULL-led, so never the plain poison skull or a lamp).
  * board_to_death   — a skateboard flipped WHEELS-UP with a wipeout star: ate it
                       mid-trick (the skate glyph, inverted).
  * lightning_rod    — one bold bolt striking a scorched feather: zapped off your
                       perch, single strike.
  * party_foul       — a tipped party-popper spraying confetti + a sad down-tick:
                       the Day-Complete party is what got you.
  * rich_reckless    — a horseshoe magnet with a coin escaping, slashed out: the
                       vacuum that caught nothing.
  * coin_blind       — a coin wearing a blindfold band: flew a whole Coin Rush
                       blind to the loot.
  * wish_unspent     — an upright, whole lamp with NO wisp (a slash of absence):
                       grabbed the lamp, died before a wish. Lamp is the WHOLE
                       silhouette, dormant — distinct from cursed's skull and the
                       pillar-led the_49er.
"""
from __future__ import annotations

import math

import pygame

import game.achievement_icons as ai

# Reuse the live module's engraved-shadow tone so recessed sockets/notches match
# the cast-shadow pass the builder stamps around every glyph.
_SH = ai._GLYPH_SH

_glyph_fonts: dict = {}


def _glyph_font(px: int):
    # Mirror ``achievement_icons._glyph_font`` so a `$` coin face matches the
    # Riches family exactly.
    f = _glyph_fonts.get(px)
    if f is None:
        f = pygame.font.SysFont(None, px, bold=True)
        _glyph_fonts[px] = f
    return f


def _ring_dollar(surf, cx, cy, r, col, rr):
    # The in-game `$` coin read, matching ``_glyph_coin``: a bold ring with a
    # struck `$` centred in it, so a coin here is unmistakably the wealth coin.
    pygame.draw.circle(surf, col, (cx, cy), rr, max(3, r // 8))
    f = _glyph_font(int(rr * 1.7))
    g = f.render("$", True, col)
    surf.blit(g, g.get_rect(center=(cx, cy)))


def _glyph_bullet_bystander(surf, cx, cy, r, col):
    # An hourglass (Slow-Mo) shattered by a collision-burst at its waist — time
    # crawled and you SPLATTED anyway. The bold bowtie glass reads as "slow"; the
    # jagged crack driven through the pinch plus the radiating impact spikes are
    # the crash the slowdown never saved you from.
    w = int(r * 0.60)                     # half-width at the caps
    h = int(r * 0.74)                     # half-height to a cap plate
    capw = max(4, int(r * 0.16))
    # top + bottom cap plates so the glass reads as a framed hourglass
    for sy in (cy - h, cy + h - capw):
        pygame.draw.rect(surf, col, (cx - w, sy, w * 2, capw),
                         border_radius=max(1, r // 16))
    # the two glass bulbs as a filled bowtie meeting at the waist — bold so it
    # survives at 44px, unlike a thin outline.
    inset = capw
    pygame.draw.polygon(surf, col, [
        (cx - w + inset, cy - h + capw), (cx + w - inset, cy - h + capw), (cx, cy)])
    pygame.draw.polygon(surf, col, [
        (cx - w + inset, cy + h - capw), (cx + w - inset, cy + h - capw), (cx, cy)])
    # a jagged crack driven down through the waist, engraved in the shadow tone.
    pygame.draw.lines(surf, _SH, False, [
        (cx - int(r * 0.20), cy - int(r * 0.42)),
        (cx + int(r * 0.06), cy - int(r * 0.10)),
        (cx - int(r * 0.08), cy + int(r * 0.06)),
        (cx + int(r * 0.16), cy + int(r * 0.44)),
    ], max(3, r // 11))
    # impact spikes bursting out of the waist beyond the glass — the "splat".
    for a in (math.radians(160), math.radians(200), math.radians(-20),
              math.radians(20)):
        ex = cx + int(math.cos(a) * r * 0.92)
        ey = cy + int(math.sin(a) * r * 0.30)
        pygame.draw.line(surf, col, (cx, cy), (ex, ey), max(2, r // 13))


def _glyph_cursed(surf, cx, cy, r, col):
    # A skull breathing out a genie-wisp of poison vapour — the wish that KILLED
    # you. The skull LEADS (round cranium + jaw + dark sockets) so it never reads
    # as the plain poison skull or a lamp; the curling wisp rising off its crown
    # is the cursed genie-breath that seals the joke.
    sk = cy + int(r * 0.30)               # skull pushed low so the wisp has sky
    cr = int(r * 0.50)
    pygame.draw.circle(surf, col, (cx, sk), cr)
    jaw = pygame.Rect(cx - int(cr * 0.58), sk + int(cr * 0.46),
                      int(cr * 1.16), int(cr * 0.66))
    pygame.draw.rect(surf, col, jaw, border_radius=max(2, r // 10))
    # two dark eye sockets + a nasal notch, all in the engraved shadow tone
    for dx in (-0.44, 0.44):
        pygame.draw.circle(surf, _SH, (cx + int(dx * cr), sk - int(cr * 0.12)),
                           max(3, r // 8))
    pygame.draw.polygon(surf, _SH, [
        (cx, sk + int(cr * 0.14)),
        (cx - int(cr * 0.20), sk + int(cr * 0.48)),
        (cx + int(cr * 0.20), sk + int(cr * 0.48)),
    ])
    # the genie-wisp: an S of thick curling strokes rising off the crown into a
    # small vapour puff — the breath of the fatal wish.
    top = sk - cr
    pygame.draw.lines(surf, col, False, [
        (cx + int(r * 0.02), top),
        (cx - int(r * 0.22), top - int(r * 0.26)),
        (cx + int(r * 0.18), top - int(r * 0.52)),
        (cx - int(r * 0.10), top - int(r * 0.78)),
    ], max(3, r // 11))
    for px, py, pr in ((-0.16, -0.86, 0.12), (0.06, -0.96, 0.16)):
        pygame.draw.circle(surf, col, (cx + int(r * px), top + int(r * py)),
                           max(3, int(r * pr)))


def _glyph_board_to_death(surf, cx, cy, r, col):
    # A skateboard flipped WHEELS-UP mid-wipeout, with a tumble impact-star — you
    # ate it doing a trick. Inverting the live skate glyph (wheels ABOVE the deck,
    # kick-tails pointing DOWN) is the whole read: a board that landed upside-down.
    th = max(4, int(r * 0.18))
    yk = cy + int(r * 0.14)               # deck line, low so wheels ride up-top
    # concave deck with kick-tails, now dipping DOWN at the ends (flipped).
    deck = [
        (cx - r * 0.78, yk + r * 0.30),   # left kick-tail (down)
        (cx - r * 0.52, yk),
        (cx + r * 0.52, yk),
        (cx + r * 0.78, yk + r * 0.30),   # right kick-tail (down)
        (cx + r * 0.78, yk + r * 0.30 - th),
        (cx + r * 0.52, yk - th),
        (cx - r * 0.52, yk - th),
        (cx - r * 0.78, yk + r * 0.30 - th),
    ]
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in deck])
    # two wheels ABOVE the deck — the cue that the board is belly-up.
    wr = max(5, int(r * 0.22))
    wy = yk - th - int(wr * 0.7)
    for dx in (-0.42, 0.42):
        pygame.draw.circle(surf, _SH, (int(cx + dx * r), wy), wr)
        pygame.draw.circle(surf, col, (int(cx + dx * r), wy), max(1, wr // 3))
    # a wipeout tumble-star bursting at the lower-left where the rider hit.
    sx, sy = cx - int(r * 0.50), cy + int(r * 0.56)
    for a in range(8):
        ang = a * math.pi / 4
        ln = r * (0.30 if a % 2 == 0 else 0.16)
        pygame.draw.line(surf, col, (sx, sy),
                         (sx + int(math.cos(ang) * ln), sy + int(math.sin(ang) * ln)),
                         max(2, r // 13))


def _glyph_lightning_rod(surf, cx, cy, r, col):
    # One bold lightning bolt striking down onto a scorched feather — zapped clean
    # off your perch. A single jagged bolt plunging into a singed feather, with
    # scorch-marks radiating from the contact, reads as a direct hit at 44px.
    # the bolt: a filled zigzag falling from the top toward the feather.
    bolt = [
        (cx + int(r * 0.10), cy - int(r * 0.92)),
        (cx - int(r * 0.30), cy - int(r * 0.14)),
        (cx - int(r * 0.02), cy - int(r * 0.14)),
        (cx - int(r * 0.24), cy + int(r * 0.30)),
        (cx + int(r * 0.34), cy - int(r * 0.34)),
        (cx + int(r * 0.06), cy - int(r * 0.34)),
        (cx + int(r * 0.34), cy - int(r * 0.92)),
    ]
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in bolt])
    # the struck feather lying low, tilted, with an engraved rachis — the perch
    # you got knocked from.
    fcx, fcy = cx - int(r * 0.06), cy + int(r * 0.56)
    fw, fh = int(r * 0.86), int(r * 0.34)
    fr = pygame.Rect(fcx - fw // 2, fcy - fh // 2, fw, fh)
    pygame.draw.ellipse(surf, col, fr)
    pygame.draw.line(surf, _SH, (fcx - int(fw * 0.42), fcy + int(fh * 0.16)),
                     (fcx + int(fw * 0.42), fcy - int(fh * 0.16)), max(2, r // 13))
    # scorch-burst radiating from the strike point where bolt meets feather.
    ix, iy = cx - int(r * 0.16), cy + int(r * 0.34)
    for a in (math.radians(210), math.radians(250), math.radians(290),
              math.radians(330)):
        pygame.draw.line(surf, col, (ix, iy),
                         (ix + int(math.cos(a) * r * 0.30),
                          iy + int(math.sin(a) * r * 0.30)), max(2, r // 13))


def _glyph_party_foul(surf, cx, cy, r, col):
    # A party-popper knocked on its side spraying confetti, with a sad down-tick —
    # the Day-Complete celebration is exactly what killed you. The tipped cone +
    # confetti fan carries the joke; the little down-arrow mocks the "win".
    # cone lying tilted, apex lower-left, open mouth up-right.
    ang = math.radians(-32)
    ca, sa = math.cos(ang), math.sin(ang)
    acx, acy = cx - int(r * 0.30), cy + int(r * 0.26)   # apex

    def rot(px, py):
        return (acx + int(px * ca - py * sa), acy + int(px * sa + py * ca))

    mouth_l = rot(r * 0.98, -r * 0.40)
    mouth_r = rot(r * 0.98, r * 0.40)
    pygame.draw.polygon(surf, col, [(acx, acy), mouth_l, mouth_r])
    # mouth rim so the open end reads as where confetti erupts.
    pygame.draw.line(surf, col, mouth_l, mouth_r, max(3, r // 12))
    # confetti bits + streamers fanning out of the mouth, up and to the right.
    mouth_c = rot(r * 0.98, 0)
    for da, ln, bit in ((-0.55, 0.72, True), (-0.18, 0.94, False),
                        (0.18, 0.80, True), (0.52, 0.58, False)):
        fa = ang + da
        ex = mouth_c[0] + int(math.cos(fa) * r * ln)
        ey = mouth_c[1] + int(math.sin(fa) * r * ln)
        if bit:
            pygame.draw.circle(surf, col, (ex, ey), max(3, int(r * 0.10)))
        else:
            mx = mouth_c[0] + int(math.cos(fa) * r * ln * 0.5)
            my = mouth_c[1] + int(math.sin(fa) * r * ln * 0.5)
            pygame.draw.line(surf, col, (mx, my), (ex, ey), max(2, r // 13))
    # sad down-tick under the cone — the party mocking the death.
    sx = cx - int(r * 0.10)
    sy = cy + int(r * 0.62)
    aw = max(3, r // 12)
    pygame.draw.line(surf, col, (sx, sy), (sx, sy + int(r * 0.28)), aw)
    pygame.draw.lines(surf, col, False, [
        (sx - int(r * 0.15), sy + int(r * 0.12)),
        (sx, sy + int(r * 0.34)),
        (sx + int(r * 0.15), sy + int(r * 0.12)),
    ], aw)


def _glyph_rich_reckless(surf, cx, cy, r, col):
    # A horseshoe magnet that grabbed NOTHING: a coin escapes past it, struck
    # through with a bold slash. The chunky U-magnet on the left + the crossed-out
    # fleeing coin on the right is the "vacuum that caught nothing" read; kept pure
    # single-colour (bands engraved in the shadow tone) so it stays monochrome.
    mcx = cx - int(r * 0.34)              # magnet column, shifted left
    rr = int(r * 0.44)
    leg_w = max(6, int(r * 0.26))
    bar = max(6, int(r * 0.28))
    top = cy - int(r * 0.44)
    # arched top of the U, opening to the RIGHT toward the escaping coin.
    arc_rect = pygame.Rect(mcx - rr, top, rr * 2, rr * 2)
    pygame.draw.arc(surf, col, arc_rect, math.radians(96), math.radians(264), bar)
    # the two straight legs reaching right (poles), one high one low.
    for sgn in (-1, 1):
        ly = cy + sgn * rr - leg_w // 2
        pygame.draw.rect(surf, col, (mcx, ly, int(r * 0.42), leg_w))
        # banded pole-tip engraved in the shadow tone — reads as a magnet pole.
        pygame.draw.rect(surf, _SH, (mcx + int(r * 0.30), ly, max(3, r // 9), leg_w))
    # the coin escaping to the right, ring + `$`, then slashed out — not grabbed.
    coin_cx = cx + int(r * 0.48)
    crr = int(r * 0.38)
    _ring_dollar(surf, coin_cx, cy, r, col, crr)
    sl = int(crr * 1.5)
    pygame.draw.line(surf, col, (coin_cx - sl, cy + sl), (coin_cx + sl, cy - sl),
                     max(3, r // 10))


def _glyph_coin_blind(surf, cx, cy, r, col):
    # A `$` coin wearing a blindfold band — flew a whole Coin Rush half-blind and
    # grabbed nothing. The bold coin ring with a thick band strapped across its
    # face (knot + trailing tie-tails to one side) is the read: blind to the loot.
    rr = int(r * 0.60)
    pygame.draw.circle(surf, col, (cx, cy), rr, max(3, r // 8))
    # `$` peeking above the band so the coin reads as the wealth coin.
    f = _glyph_font(int(rr * 1.2))
    g = f.render("$", True, col)
    surf.blit(g, g.get_rect(center=(cx, cy - int(rr * 0.46))))
    # the blindfold band strapped across the coin's lower-middle (eye level).
    band_h = max(6, int(r * 0.30))
    band_y = cy + int(r * 0.02)
    pygame.draw.rect(surf, col, (cx - rr - int(r * 0.10), band_y - band_h // 2,
                                 (rr + int(r * 0.10)) * 2, band_h),
                     border_radius=max(1, r // 14))
    # a small dark seam so the band reads as fabric, not a bar.
    pygame.draw.line(surf, _SH, (cx - rr, band_y), (cx + rr, band_y), max(2, r // 16))
    # knot + two trailing tie-tails off the right edge — clearly a blindfold.
    kx = cx + rr + int(r * 0.06)
    pygame.draw.circle(surf, col, (kx, band_y), max(3, int(r * 0.12)))
    for sgn in (-1, 1):
        pygame.draw.line(surf, col, (kx, band_y),
                         (kx + int(r * 0.24), band_y + sgn * int(r * 0.22)),
                         max(2, r // 13))


def _glyph_wish_unspent(surf, cx, cy, r, col):
    # An upright, whole genie lamp with NO wisp — a slash marking the ABSENCE
    # where the smoke should rise: you grabbed the lamp and died before a wish.
    # The lamp is the WHOLE silhouette here (body + spout + handle + lid knob),
    # dormant — distinct from cursed's skull and the pillar-led the_49er.
    lcy = cy + int(r * 0.20)
    # fat lamp body low-centre.
    bw, bh = int(r * 1.10), int(r * 0.62)
    pygame.draw.ellipse(surf, col, (cx - bw // 2, lcy - bh // 2, bw, bh))
    # spout flicking up to the LEFT — the classic Aladdin lamp read.
    pygame.draw.polygon(surf, col, [
        (cx - int(r * 0.36), lcy - int(r * 0.08)),
        (cx - int(r * 0.92), lcy - int(r * 0.44)),
        (cx - int(r * 0.34), lcy + int(r * 0.14)),
    ])
    # C-handle looping off the right.
    hr = pygame.Rect(cx + int(r * 0.30), lcy - int(r * 0.30),
                     int(r * 0.46), int(r * 0.58))
    pygame.draw.arc(surf, col, hr, math.radians(-70), math.radians(120),
                    max(3, r // 10))
    # lid knob on top so the dome reads as a lidded vessel.
    pygame.draw.circle(surf, col, (cx + int(r * 0.04), lcy - int(bh * 0.52)),
                       max(3, int(r * 0.11)))
    # the ABSENCE: a bold slash across the empty air above the spout where a wisp
    # would curl — the wish that never came out. A "no-smoke" strike.
    wx, wy = cx - int(r * 0.42), cy - int(r * 0.56)
    d = int(r * 0.26)
    pygame.draw.line(surf, col, (wx - d, wy - d), (wx + d, wy + d), max(3, r // 10))


GLYPHS = {
    "bullet_bystander": _glyph_bullet_bystander,
    "cursed": _glyph_cursed,
    "board_to_death": _glyph_board_to_death,
    "lightning_rod": _glyph_lightning_rod,
    "party_foul": _glyph_party_foul,
    "rich_reckless": _glyph_rich_reckless,
    "coin_blind": _glyph_coin_blind,
    "wish_unspent": _glyph_wish_unspent,
}
