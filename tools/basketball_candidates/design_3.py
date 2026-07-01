"""THE RETRO '90s — basketball candidate DESIGN 3 of 5 (short-shorts era).

Scratch exploration only; NOT registered in store_skins.BUILDERS, so the live
roster is untouched.

Concept: dress Pip as a throwback hardwood hooper from the short-shorts era, so
the SET reads as five different basketball PEOPLE rather than one recoloured
tank. With the ball shipping separately, the era is carried entirely by gear the
other designs don't have: a PINSTRIPED purple tank with a team-wordmark band
worn LOW on the chest, deliberately SHORT shorts (high, hemmed cut — the
opposite of Design 1's baggy knee shorts), HIGH tube socks with a single bold
gold hoop on each leg (a rare lower-leg tell that no other hoops design owns),
retro low sneakers, and rec-specs SPORTS GOGGLES — two round eye-cups on a
bridge, the era's iconic eyewear. Pip's scarlet macaw head/beak/eye stay in the
open; the goggles own the brow alone, so nothing stacks into a band-on-band
blur.

At 40px the read, in order of value: (1) the PINSTRIPED tank, (2) the GOGGLES
reading as two clear lenses (NOT a visor/sunglasses bar), (3) the SHORT-shorts
hem + the lit thigh gap above the high tube socks, then the single gold sock
hoop + low sneakers. Every kit piece stays INSIDE the base bird footprint —
nothing dangles below the feet line.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly

# Retro hardwood palette. The purple tank is a mid-dark value so the gold
# pinstripes + white wordmark pop on it and it separates from the scarlet head
# above and a bright day sky.
_RT_JERSEY   = (91, 46, 145)         # #5B2E91 retro purple
_RT_JERSEY_D = (62, 30, 100)         # jersey shadow / off-side panel
_RT_JERSEY_H = (124, 74, 184)        # jersey highlight
_RT_GOLD     = (232, 178, 58)        # #E8B23A gold pinstripe / hoop / hem
_RT_GOLD_D   = (176, 130, 36)        # gold shadow / hoop seam
_RT_WHITE    = (244, 244, 248)       # #F4F4F8 wordmark / trim / sock
_RT_WHITE_D  = (198, 198, 208)       # white shadow so it reads on light sky
_RT_THIGH    = (146, 96, 204)        # lit bare-thigh value break above the socks
_RT_RIM      = (38, 40, 48)          # thin goggle rim (1px) — lighter than a bar
_RT_LENS     = (172, 222, 244)       # clear goggle lens (brighter, cooler glass)
_RT_LENS_H   = (236, 250, 255)       # lens glint
_RT_SHOE     = (244, 244, 248)       # retro low sneaker
_RT_SHOE_D   = (190, 192, 200)       # sneaker shadow / sole


def _paint(surf, _a):
    # Body centre in composite space (parrot body centre (32,32) + PARROT_DY=20).
    BCX, BCY = 32, 52

    # ── SHORT SHORTS first, behind the tank hem ─────────────────────────────────
    # The era tell vs Design 1's baggy knee shorts: a HIGH, hemmed cut. The shorts
    # top edge gets a 1px GOLD hem trim, and a lit bare-thigh band sits just above
    # the socks — that value break is what makes the high hem legible at 40px.
    shorts = [(BCX - 12, BCY + 3), (BCX + 11, BCY + 3),
              (BCX + 12, BCY + 8), (BCX + 1, BCY + 8),
              (BCX, BCY + 6), (BCX - 1, BCY + 8),
              (BCX - 12, BCY + 8)]
    _poly(surf, _RT_JERSEY, shorts)
    _poly(surf, _RT_JERSEY_D, [(BCX - 12, BCY + 3), (BCX - 7, BCY + 3),
                               (BCX - 7, BCY + 8), (BCX - 12, BCY + 8)])
    # Visible HEM trim along the shorts top — the titular short-shorts tell.
    pygame.draw.line(surf, _RT_GOLD, (BCX - 12, BCY + 3), (BCX + 11, BCY + 3), 1)
    # Gold side stripes down each thigh — the classic throwback short tell.
    pygame.draw.line(surf, _RT_GOLD, (BCX - 11, BCY + 4), (BCX - 11, BCY + 7), 1)
    pygame.draw.line(surf, _RT_GOLD, (BCX + 10, BCY + 4), (BCX + 11, BCY + 7), 1)

    # ── HIGH TUBE SOCKS with a single bold gold hoop — the lower-leg signature ───
    # A rare hoops tell and the only design in the set with a lower-leg read. Each
    # leg is a tall white sock pulled high up the calf (1px wider than r1 so the
    # hoop sits cleanly on it), shaded on the off face so it reads round, capped by
    # ONE 2px GOLD hoop with a dark seam beneath — one clean hoop beats two muddy
    # thin stripes at 40px. A lit bare-thigh nub above each sock is the value break
    # that sells the short-shorts hem. Sits on the feet line (~HY+15..23).
    for fx in (27, 35):
        # Lit bare thigh just above the sock so the high shorts hem reads.
        pygame.draw.line(surf, _RT_THIGH, (fx, HY + 11), (fx, HY + 13), 4)
        # White sock pillar, 1px wider than r1 (5px lit core + shaded off face).
        pygame.draw.line(surf, _RT_WHITE_D, (fx + 1, HY + 14), (fx + 1, HY + 23), 6)
        pygame.draw.line(surf, _RT_WHITE, (fx - 1, HY + 14), (fx - 1, HY + 23), 5)
        pygame.draw.line(surf, _RT_WHITE_D, (fx - 3, HY + 14), (fx - 3, HY + 23), 1)
        # ONE bold gold hoop near the top, crisped by a dark seam beneath it.
        pygame.draw.line(surf, _RT_GOLD, (fx - 3, HY + 16), (fx + 2, HY + 16), 2)
        pygame.draw.line(surf, _RT_GOLD_D, (fx - 3, HY + 18), (fx + 2, HY + 18), 1)

    # ── RETRO LOW SNEAKERS on the feet line ─────────────────────────────────────
    # Deliberately LOW-cut (vs Design 1's high-tops) to match the era: a slim
    # white shoe with a purple swoosh tick + grey sole, hugging the feet line.
    for fx in (27, 35):
        pygame.draw.rect(surf, _RT_SHOE_D, (fx - 4, HY + 23, 9, 5), border_radius=2)
        pygame.draw.rect(surf, _RT_SHOE, (fx - 4, HY + 22, 9, 4), border_radius=2)
        pygame.draw.line(surf, _RT_JERSEY, (fx - 3, HY + 24), (fx + 3, HY + 23), 1)
        pygame.draw.line(surf, _RT_SHOE_D, (fx - 4, HY + 27), (fx + 5, HY + 27), 1)

    # ── PINSTRIPED TANK over the torso (the era headline) ───────────────────────
    # A sleeveless singlet so it still reads basketball, but the surface is the
    # tell: vertical GOLD pinstripes on the purple cloth, the '90s hardwood
    # signature. Fill → off-side shade → lit near edge gives three values; the
    # pinstripes are clipped to the cloth so they never leak past the contour.
    jersey = [(BCX - 11, BCY - 7), (BCX + 10, BCY - 7),
              (BCX + 13, BCY + 1), (BCX + 12, BCY + 7),
              (BCX - 11, BCY + 7), (BCX - 13, BCY + 1)]
    _poly(surf, _RT_JERSEY, jersey)
    _poly(surf, _RT_JERSEY_D, [(BCX - 13, BCY + 1), (BCX - 9, BCY - 1),
                               (BCX - 8, BCY + 6), (BCX - 11, BCY + 7)])

    # Pinstripes: a fixed 2-value pitch (gold line, ~3px gap) clipped to the
    # cloth. A consistent pitch like the soccer kit stripes is what survives the
    # NEAREST downscale instead of dissolving into noise.
    clip_prev = surf.get_clip()
    surf.set_clip(pygame.Rect(BCX - 13, BCY - 7, 26, 15))
    for sx in range(BCX - 10, BCX + 12, 3):
        pygame.draw.line(surf, _RT_GOLD_D, (sx, BCY - 6), (sx, BCY + 7), 1)
        pygame.draw.line(surf, _RT_GOLD, (sx, BCY - 6), (sx, BCY + 4), 1)
    surf.set_clip(clip_prev)

    # Sleeveless straps + lit near edge so the singlet reads worn, not a bib, and
    # the bare-shoulder cut stays explicit after the pinstripes.
    _poly(surf, _RT_JERSEY, [(BCX - 11, BCY - 7), (BCX - 6, BCY - 10),
                             (BCX - 4, BCY - 6), (BCX - 8, BCY - 3)])  # off strap
    _poly(surf, _RT_JERSEY, [(BCX + 10, BCY - 7), (BCX + 5, BCY - 10),
                             (BCX + 3, BCY - 6), (BCX + 7, BCY - 3)])  # near strap
    pygame.draw.arc(surf, _RT_JERSEY_D, (BCX + 3, BCY - 8, 11, 14), -1.0, 1.4, 1)
    pygame.draw.arc(surf, _RT_JERSEY_D, (BCX - 14, BCY - 8, 11, 14), 1.7, 4.2, 1)
    pygame.draw.line(surf, _RT_JERSEY_H, (BCX + 8, BCY - 5), (BCX + 10, BCY + 5), 1)

    # ── TEAM WORDMARK BAND worn LOW on the chest ────────────────────────────────
    # Moved DOWN off the brow so there's a clear band of purple pinstripe between
    # it and the goggles — the goggles own the brow alone. A solid white panel
    # knocking back the pinstripes, carrying ONE blocky wordmark glyph cluster
    # (not evenly-spaced ticks), with a gold underline crisping it for downscale.
    bandy = BCY + 3
    pygame.draw.line(surf, _RT_WHITE_D, (BCX - 9, bandy + 1), (BCX + 9, bandy + 1), 5)
    pygame.draw.line(surf, _RT_WHITE, (BCX - 9, bandy - 1), (BCX + 9, bandy - 1), 4)
    pygame.draw.line(surf, _RT_GOLD, (BCX - 9, bandy + 2), (BCX + 9, bandy + 2), 1)
    # ONE solid blocky purple glyph cluster centred on the band (a chest logo
    # mass), not a row of evenly-spaced ticks that read as noise.
    pygame.draw.rect(surf, _RT_JERSEY, (BCX - 4, bandy - 2, 9, 3))
    pygame.draw.line(surf, _RT_WHITE, (BCX - 1, bandy - 2), (BCX - 1, bandy), 1)

    # ── REC-SPECS SPORTS GOGGLES across the eyes (drawn LAST, frontmost) ─────────
    # The era's iconic eyewear, and it MUST read as GOGGLES, not a sunglasses bar:
    # TWO distinct round eye-cups joined by a thin bridge, each with only a 1px
    # rim and a bright cool lens so the macaw eye reads THROUGH the clear glass —
    # rec-specs, not shades. A dark elastic strap loops back over the crown. The
    # BEAK stays fully in the open below the lenses. The goggles own the brow with
    # no headband stacked above them.
    ex, ey = HX + 3, HY                     # eye-region centre on the macaw head
    EYE_R = 4                               # eye-cup radius — small + round
    far_c  = (ex - 5, ey)                   # off (far) eye-cup centre
    near_c = (ex + 4, ey)                   # near eye-cup centre (over the macaw eye)
    # Dark elastic strap wrapping back over the head (the rec-specs tell).
    pygame.draw.line(surf, _RT_RIM, (far_c[0] - 3, ey - 2),
                     (HX - 12, CROWN_Y + 8), 2)
    # Thin bridge joining the two cups across the beak base.
    pygame.draw.line(surf, _RT_RIM, (far_c[0] + EYE_R - 1, ey),
                     (near_c[0] - EYE_R + 1, ey), 1)
    for cx, cy in (far_c, near_c):
        # Clear cool lens fill, then a thin 1px rim ring around it.
        pygame.draw.circle(surf, _RT_LENS, (cx, cy), EYE_R)
        pygame.draw.circle(surf, _RT_RIM, (cx, cy), EYE_R, 1)
        # Bright glass glint so the lens reads transparent, not solid.
        pygame.draw.line(surf, _RT_LENS_H, (cx - 2, cy + 1), (cx, cy - 2), 1)
    # A dark pupil dot showing through the near lens sells "eye behind glass".
    pygame.draw.circle(surf, _RT_RIM, (near_c[0] + 1, ey), 1)


build = store_skins._make_skin(_paint)
