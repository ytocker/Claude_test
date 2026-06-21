"""Scratch mockup: the `corner-rosette` unlock-notice concept.

A single bold "commendation rosette" stamped into the top-right dead corner —
the way a certificate carries a gold-foil seal. A scalloped foil disc with a
short sunburst behind it reads as STRUCK INTO the paper (flat, no ribbon, no
hung medal), so it stays clearly distinct from the medal-rail badge-on-ribbon
language. One always-present object + a "2 EARNED" count-badge — not a stack.

Anchored into the top strip / right margin so it occludes nothing: title,
hero plaque, stat tiles, power-up strip, and buttons all stay clear.

Scratch tooling only; `game/` is untouched.
"""
import os
import math
import pygame

from tools.unlock_notice_common import render_backdrop, demo_ids
from game.achievement_icons import draw_badge
from game.hud import (_font, _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP,
                      _PANEL_DARK, _NIGHT_DEEP)

# Local foil palette tuned to the gold-on-navy "Courier's Commendation" family.
_FOIL_HI   = (255, 240, 188)   # foil crest catching the upper-left light
_FOIL_MID  = (236, 190,  78)   # body gold of the foil
_FOIL_LO   = (168, 116,  28)   # shadowed lower-right of the foil
_FOIL_EDGE = ( 96,  62,  14)   # thin keyline round the seal
_RAY_GOLD  = (252, 214, 120)
_INK_NAVY  = (14, 9, 40)


def _lerp(a, b, t):
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


def _draw_sunburst(surf, cx, cy, r_in, r_out, n, col):
    """A short ring of tapered triangular rays fanned behind the seal — the
    celebratory 'struck commendation' burst, kept low so the seal reads stamped
    into the corner rather than radiating across the protected bands."""
    burst = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    half = math.radians(360 / n * 0.34)   # ray half-width
    for i in range(n):
        a = i * math.tau / n - math.radians(12)
        tip = (cx + math.cos(a) * r_out, cy + math.sin(a) * r_out)
        b1 = (cx + math.cos(a - half) * r_in, cy + math.sin(a - half) * r_in)
        b2 = (cx + math.cos(a + half) * r_in, cy + math.sin(a + half) * r_in)
        # rays facing the upper-left light read brighter — ties the burst to the
        # foil's single light source instead of glowing evenly all round.
        d = (math.cos(a - math.radians(135)) + 1) * 0.5
        rc = _lerp(_FOIL_LO, col, 0.35 + 0.65 * d ** 1.3)
        pygame.draw.polygon(burst, (*rc, 210), [tip, b1, b2])
    surf.blit(burst, (0, 0))


def _draw_scallop_ring(surf, cx, cy, r, n, col):
    """The certificate-seal scalloped edge: a ring of small bumps round the foil
    rim, so the disc reads as a pressed paper seal, not a coin."""
    for i in range(n):
        a = i * math.tau / n
        bx = cx + math.cos(a) * r
        by = cy + math.sin(a) * r
        d = (math.cos(a - math.radians(135)) + 1) * 0.5
        bc = _lerp(_FOIL_LO, col, 0.3 + 0.7 * d ** 1.2)
        pygame.draw.circle(surf, bc, (int(bx), int(by)), max(2, int(r * 0.12)))


def _draw_seal(surf, cx, cy, R, badge_id):
    """A struck gold-foil seal: scalloped edge, a domed foil disc lit upper-left,
    a recessed navy well, and the unlocked badge emblem pressed into it."""
    # Scalloped paper-seal edge sits just behind the foil disc.
    _draw_scallop_ring(surf, cx, cy, int(R * 1.0), 22, _FOIL_MID)

    # Domed foil disc — radial-ish shading via stacked circles, light upper-left.
    for i in range(R, 0, -1):
        t = (R - i) / R
        base = _lerp(_FOIL_HI, _FOIL_LO, t)
        pygame.draw.circle(surf, base, (cx, cy), i)
    # Offset specular bloom toward the upper-left to dome the foil.
    bloom = pygame.Surface((R * 2, R * 2), pygame.SRCALPHA)
    for i in range(int(R * 0.62), 0, -1):
        t = i / (R * 0.62)
        pygame.draw.circle(bloom, (*_FOIL_HI, int(120 * (1 - t))),
                           (int(R * 0.78), int(R * 0.74)), i)
    surf.blit(bloom, (cx - R, cy - R))
    pygame.draw.circle(surf, _FOIL_EDGE, (cx, cy), R, max(1, R // 20))

    # Recessed navy well that carries the emblem — a stamped inner field.
    wr = int(R * 0.62)
    pygame.draw.circle(surf, _INK_NAVY, (cx, cy), wr)
    pygame.draw.circle(surf, _FOIL_LO, (cx, cy), wr, max(1, R // 22))
    # The earned emblem, pressed into the well.
    em = int(wr * 1.86)
    draw_badge(surf, badge_id, pygame.Rect(cx - em // 2, cy - em // 2, em, em),
               unlocked=True)


def _draw_count_badge(surf, right_x, ccy, n):
    """A compact dark '2 EARNED' count-pill notched onto the seal's lower-left
    rim — the tally that turns one always-present seal into a counter without a
    second seal. A gold numeral chip + small caption, right-anchored so it never
    drifts over the title lettering or off the screen edge."""
    f_num = _font(16, bold=True)
    f_lbl = _font(11, bold=True)
    num = f_num.render(str(n), True, _NIGHT_DEEP)
    lbl = f_lbl.render("EARNED", True, _GOLD_PALE)
    chip_r = num.get_height() // 2 + 2
    gap = 4
    inner = chip_r * 2 + gap + lbl.get_width()
    pad = 5
    w = inner + pad * 2
    h = chip_r * 2 + 6
    x = right_x - w
    y = ccy - h // 2
    pill = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(pill, (*_PANEL_DARK, 250), pill.get_rect(),
                     border_radius=h // 2)
    pygame.draw.rect(pill, _GOLD_BRIGHT, pill.get_rect(), 2, border_radius=h // 2)
    surf.blit(pill, (x, y))
    # gold numeral chip on the left of the pill
    ccx = x + pad + chip_r
    for i in range(chip_r, 0, -1):
        t = (chip_r - i) / chip_r
        pygame.draw.circle(surf, _lerp(_GOLD_PALE, _GOLD_BRIGHT, t), (ccx, y + h // 2), i)
    pygame.draw.circle(surf, _GOLD_DEEP, (ccx, y + h // 2), chip_r, 1)
    surf.blit(num, num.get_rect(center=(ccx, y + h // 2)))
    surf.blit(lbl, (ccx + chip_r + gap, y + (h - lbl.get_height()) // 2))


def main():
    surf = render_backdrop()
    ids = demo_ids(2)

    # Anchor hard into the top-right dead corner ABOVE the title. The
    # 'RUN SUMMARY' title is centred at y~56 and nearly fills the width, so the
    # only true dead zone is the corner wedge over its right shoulder. Keep the
    # seal compact and high (centre near y24) so its body sits in the y0-40 top
    # strip and only the count-pill drops into the clear right margin beside the
    # plaque corner — occluding none of the protected bands.
    R = 27
    cx = 360 - R - 4
    cy = R - 2

    # Sunburst behind, kept short so rays stay inside the corner wedge.
    _draw_sunburst(surf, cx, cy, int(R * 0.94), int(R * 1.5), 16, _RAY_GOLD)
    _draw_seal(surf, cx, cy, R, ids[0])
    # '2 EARNED' pill in the clear band between the title bottom (~y73) and the
    # plaque top (y104), right-anchored to the edge — a genuine dead strip so it
    # occludes neither the title lettering nor the hero plaque.
    _draw_count_badge(surf, 360 - 6, 90, 2)

    OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "docs", "achievements", "unlock_notice", "corner-rosette")
    os.makedirs(OUT, exist_ok=True)
    out = os.path.join(OUT, "round_1.png")
    pygame.image.save(surf, out)
    print(out)


if __name__ == "__main__":
    main()
