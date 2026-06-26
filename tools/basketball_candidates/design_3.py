"""THE RETRO '90s — basketball candidate DESIGN 3 of 5 (short-shorts era).

Scratch exploration only; NOT registered in store_skins.BUILDERS, so the live
roster is untouched.

Concept: dress Pip as a throwback hardwood hooper from the short-shorts era, so
the SET reads as five different basketball PEOPLE rather than one recoloured
tank. With the ball shipping separately, the era is carried entirely by gear the
other designs don't have: a PINSTRIPED purple tank with a wide team-wordmark
band, deliberately SHORT shorts (high hem, the opposite of Design 1's baggy
knee shorts), HIGH tube socks with twin hoop stripes on each leg (a rare
lower-leg tell that no other hoops design owns), retro low sneakers, rec-specs /
GOGGLES across the eyes, and a flat-top headband. Pip's scarlet macaw
head/beak/eye stay in the open — the goggles sit over the eyes only and clear
the beak.

At 40px the read, in order of value: (1) the PINSTRIPED tank + wide wordmark
band (pinstripes are the era signature, so they use a 2-value pitch that
survives the downscale like the soccer kit stripes), (2) the GOGGLES reading as
clear-lensed eyewear, not a blindfold, (3) the HIGH tube socks with twin
stripes, then the short shorts + low sneakers. Every kit piece stays INSIDE the
base bird footprint — nothing dangles below the feet line.
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
_RT_GOLD     = (232, 178, 58)        # #E8B23A gold pinstripe
_RT_GOLD_D   = (176, 130, 36)        # gold shadow
_RT_WHITE    = (244, 244, 248)       # #F4F4F8 wordmark / trim / sock
_RT_WHITE_D  = (198, 198, 208)       # white shadow so it reads on light sky
_RT_STRAP    = (26, 28, 34)          # #1A1C22 goggle strap / contour
_RT_LENS     = (188, 214, 232)       # clear goggle lens (cool glass tint)
_RT_LENS_H   = (228, 240, 248)       # lens glint
_RT_ACCENT   = (46, 168, 79)         # #2EA84F retro green accent (sock stripe)
_RT_SHOE     = (244, 244, 248)       # retro low sneaker
_RT_SHOE_D   = (190, 192, 200)       # sneaker shadow / sole


def _paint(surf, _a):
    # Body centre in composite space (parrot body centre (32,32) + PARROT_DY=20).
    BCX, BCY = 32, 52

    # ── SHORT SHORTS first, behind the tank hem ─────────────────────────────────
    # The era tell vs Design 1's baggy knee shorts: a HIGH hem (~BCY+8) so a band
    # of bare-then-socked leg shows below it. Purple cloth with a gold side stripe;
    # shaded off-side gives the shorts form before the tank covers their top edge.
    shorts = [(BCX - 12, BCY + 2), (BCX + 11, BCY + 2),
              (BCX + 12, BCY + 8), (BCX + 1, BCY + 8),
              (BCX, BCY + 6), (BCX - 1, BCY + 8),
              (BCX - 12, BCY + 8)]
    _poly(surf, _RT_JERSEY, shorts)
    _poly(surf, _RT_JERSEY_D, [(BCX - 12, BCY + 2), (BCX - 7, BCY + 2),
                               (BCX - 7, BCY + 8), (BCX - 12, BCY + 8)])
    # Gold side stripes down each thigh — the classic throwback short tell.
    pygame.draw.line(surf, _RT_GOLD, (BCX - 11, BCY + 3), (BCX - 11, BCY + 7), 1)
    pygame.draw.line(surf, _RT_GOLD, (BCX + 10, BCY + 3), (BCX + 11, BCY + 7), 1)

    # ── HIGH TUBE SOCKS with twin hoop stripes — the lower-leg signature ─────────
    # A rare hoops tell and the only design in the set with a lower-leg read.
    # Each leg is a tall white sock pulled high up the calf, shaded on the off
    # face so it reads round, capped by TWO crisp stripe bands (gold + green) near
    # the top — a 2-value band so the stripes survive the downscale. Sits on the
    # feet line (~HY+15..23); nothing drops below it.
    for fx in (27, 35):
        pygame.draw.line(surf, _RT_WHITE_D, (fx + 1, HY + 14), (fx + 1, HY + 23), 5)
        pygame.draw.line(surf, _RT_WHITE, (fx, HY + 14), (fx, HY + 23), 4)
        pygame.draw.line(surf, _RT_WHITE_D, (fx - 2, HY + 14), (fx - 2, HY + 23), 1)
        # Twin hoop stripes near the top (gold over green), each crisped by a
        # dark seam beneath so the two-stripe band can't muddy into one.
        pygame.draw.line(surf, _RT_GOLD, (fx - 2, HY + 15), (fx + 1, HY + 15), 4)
        pygame.draw.line(surf, _RT_ACCENT, (fx - 2, HY + 17), (fx + 1, HY + 17), 4)
        pygame.draw.line(surf, _RT_WHITE_D, (fx - 2, HY + 18), (fx + 1, HY + 18), 1)

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

    # ── WIDE TEAM WORDMARK BAND across the chest ────────────────────────────────
    # The throwback uniform's headline panel: a solid white band knocking back the
    # pinstripes, carrying a blocky chest wordmark so it reads as a named team
    # jersey, not stripe noise. A gold underline crisps it for the downscale.
    bandy = BCY - 1
    pygame.draw.line(surf, _RT_WHITE_D, (BCX - 11, bandy + 1), (BCX + 11, bandy + 1), 6)
    pygame.draw.line(surf, _RT_WHITE, (BCX - 11, bandy - 1), (BCX + 11, bandy - 1), 5)
    pygame.draw.line(surf, _RT_GOLD, (BCX - 11, bandy + 2), (BCX + 11, bandy + 2), 1)
    # Blocky purple wordmark ticks reading as stacked uppercase letters on the band.
    for lx in range(BCX - 9, BCX + 9, 3):
        pygame.draw.line(surf, _RT_JERSEY, (lx, bandy - 2), (lx, bandy), 1)

    # ── FLAT-TOP HEADBAND across the brow ───────────────────────────────────────
    # A retro band that sits flatter/wider than the modern thin brow band: a thick
    # white band with a gold midline hugging the crown, clearing Pip's eye + beak
    # below it. Drawn before the goggles so the strap can ride over it.
    by = CROWN_Y + 5
    pygame.draw.line(surf, _RT_WHITE_D, (HX - 12, by + 1), (HX + 13, by + 1), 7)
    pygame.draw.line(surf, _RT_WHITE, (HX - 12, by - 1), (HX + 13, by - 1), 5)
    pygame.draw.line(surf, _RT_GOLD, (HX - 11, by), (HX + 12, by), 1)
    pygame.draw.line(surf, _RT_WHITE_H if False else _RT_WHITE,
                     (HX - 10, by - 3), (HX + 5, by - 3), 1)

    # ── REC-SPECS / GOGGLES across the eyes (drawn LAST, frontmost) ──────────────
    # The era's iconic eyewear, and it MUST read as goggles, not a blindfold: a
    # CLEAR cool-tinted lens over the eye only (so Pip's eye shows through), a
    # dark rim, and a dark elastic strap looping back over the headband — while
    # the BEAK stays fully in the open below the lens. The lens sits high on the
    # face centred on the eye region, well above the beak.
    ex, ey = HX + 3, HY + 1                # eye-region centre on the macaw head
    # Dark elastic strap wrapping back over the head (the "rec-specs" tell).
    pygame.draw.line(surf, _RT_STRAP, (ex - 9, ey - 2), (HX - 13, CROWN_Y + 7), 2)
    # Single wide lens housing over both eyes — a soft rounded rectangle.
    lens = pygame.Rect(ex - 8, ey - 4, 15, 8)
    pygame.draw.rect(surf, _RT_STRAP, lens, border_radius=4)            # dark rim
    inner = lens.inflate(-3, -3)
    pygame.draw.rect(surf, _RT_LENS, inner, border_radius=3)            # clear lens
    # Bridge tick + a bright diagonal glint so the glass reads as transparent.
    pygame.draw.line(surf, _RT_STRAP, (ex - 1, ey - 3), (ex - 1, ey + 3), 1)
    pygame.draw.line(surf, _RT_LENS_H, (ex - 6, ey + 1), (ex - 3, ey - 2), 1)
    pygame.draw.line(surf, _RT_LENS_H, (ex + 1, ey + 2), (ex + 4, ey - 1), 1)


build = store_skins._make_skin(_paint)
