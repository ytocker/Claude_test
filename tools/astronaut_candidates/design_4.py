"""ROCKETEER — retro 1950s raygun-gothic spaceman (LEGENDARY charm candidate).

Scratch exploration only — NOT wired into store_skins.BUILDERS; the live
skin_astronaut stays untouched. This is the FURTHEST-from-realism astronaut: a
chrome-silver bird in a clear fishbowl bubble dome (visor UP, Pip's macaw face
fully visible), topped by a tall bobbing antenna with a glowing ball, and
strapped to a finned retro rocket-pack whose RED tail fins flare out past the
tail with a little flame puffing below.

The raygun-gothic tells — fishbowl + tall antenna + flaring rocket fins + flame
— are pushed OUT past the bird's silhouette so it reads as an old-comic-book
spaceman at 40px, nothing like the modern hard-sphere suits. The antenna wobble
and the flame flicker are keyed off ``wing_angle_deg`` so the look feels alive
on the flap (the same trick the ninja headband flick uses).

Order of read at 40px: silver bird → clear fishbowl with face inside → red
finned rocket flaring past the tail → antenna ball above the dome → flame below.
"""
from __future__ import annotations
import math
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, PARROT_DY, COMPOSITE_W, COMPOSITE_H
from game.parrot import _WING_ANGLES, _aaellipse  # noqa: F401
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette


# ── palette (raygun-gothic chrome + comic-book red/yellow) ────────────────────
SILVER    = (201, 208, 218)        # #C9D0DA chrome silver suit
SILVER_SH = (138, 147, 163)        # #8A93A3 chrome shadow
SILVER_HI = (238, 242, 248)        # near-white chrome specular
RED       = (226, 59, 59)          # #E23B3B fins / cuffs / buttons
RED_D     = (158, 32, 32)          # red shadow
GOLD      = (242, 194, 51)         # #F2C233 antenna tip / flame
GOLD_HI   = (255, 235, 150)        # flame hot core
DARK      = (42, 47, 60)           # #2A2F3C helmet rim / dark accents
GLASS     = (170, 205, 226)        # faint cool tint inside the bubble glass
GLASS_HI  = (240, 250, 255)        # reflection streak on the glass


# Full chrome-silver suit RECOLOR: the whole bird becomes a polished spaceman in
# a metallic pressure suit. Keep the macaw FACE (eye + beak) readable inside the
# bubble, so the head stays a lighter silver and the beak keeps a warm-ish tone
# so it doesn't vanish — lenses dropped, Pip's bare eye owns the face.
P_ROCKET = _pal(
    tail=[(150, 158, 172), (168, 176, 190), (188, 196, 208), (210, 216, 226)],
    tail_line=(96, 103, 118),
    body_shadow=(120, 128, 144), body_main=SILVER,
    body_chest=(220, 226, 234), body_belly=(176, 184, 198),
    sheen=(255, 255, 255, 130),
    wing_main=(168, 176, 190), wing_dark=(108, 116, 132), wing_tip=(224, 230, 238),
    wing_secondary=None, wing_highlight=SILVER_HI,
    head_shadow=(132, 140, 156), head_main=(214, 220, 230),
    head_cheek=(232, 236, 242), head_crown=(238, 242, 248),
    lens_frame=(150, 158, 172), lens_body=(60, 66, 80),
    lens_tint=None, lens_glint=None,
    beak_main=(210, 178, 96), beak_dark=(150, 118, 52), beak_gloss=(244, 222, 160),
    foot=(110, 118, 134),
)


def _rocket_base(angle_deg):
    # Chrome bird, no aviators — the bare macaw eye reads through the fishbowl.
    return _build_parrot_with_palette(angle_deg, P_ROCKET, draw_lenses=False)


def _anim(wing_angle_deg):
    """Map the 4 wing angles (50..-40) to a 0..1 flap phase so the antenna
    wobble and rocket-flame flicker advance together across the cycle."""
    return (50.0 - wing_angle_deg) / 90.0


def _ellipse_ring(surf, color, rect, width):
    pygame.draw.ellipse(surf, color, rect, width)


def _rocket_pack(surf, t):
    # ── RETRO ROCKET-PACK on the back ── a rounded silver torpedo cylinder
    # strapped behind the body, with TWO red tail fins flaring out PAST the tail
    # into open sky (the raygun-gothic silhouette tell) + a flickering flame
    # puffing from the nozzle at the bottom. Drawn FIRST so the body sits over
    # the straps and the fins read as poking out behind the bird.
    bx, by = HX - 24, HY + 14          # torpedo centre, behind the back/tail
    # Body cylinder (vertical torpedo) — shadowed left, bright chrome highlight.
    pygame.draw.ellipse(surf, SILVER_SH, (bx - 8, by - 14, 16, 34))
    pygame.draw.ellipse(surf, SILVER, (bx - 7, by - 14, 13, 32))
    pygame.draw.ellipse(surf, SILVER_HI, (bx - 4, by - 11, 4, 22))   # spec streak
    pygame.draw.ellipse(surf, DARK, (bx - 8, by - 16, 16, 8))        # nose cap rim
    pygame.draw.ellipse(surf, RED, (bx - 6, by - 15, 12, 6))         # red nose cap
    pygame.draw.ellipse(surf, GOLD_HI, (bx - 3, by - 15, 3, 3))      # nose glint

    # Two RED tail fins flaring out past the tail (down-left + down-right), each
    # with a dark keyline so they pop off the silver body and the sky.
    fin_l = [(bx - 6, by + 8), (bx - 18, by + 24), (bx - 6, by + 20)]
    fin_r = [(bx + 5, by + 8), (bx + 16, by + 23), (bx + 5, by + 20)]
    for fin in (fin_l, fin_r):
        store_skins._poly(surf, RED_D, [(x, y + 1) for x, y in fin])
        store_skins._poly(surf, RED, fin)
    pygame.draw.line(surf, (255, 150, 150), fin_l[0], fin_l[1], 1)
    pygame.draw.line(surf, (255, 150, 150), fin_r[0], fin_r[1], 1)

    # Nozzle ring at the bottom + a flickering flame puffing below it. The flame
    # SHAPE and reach flicker with the flap (off `t`) so the jetpack feels live.
    nx, ny = bx, by + 20
    pygame.draw.ellipse(surf, DARK, (nx - 6, ny - 2, 12, 6))
    pygame.draw.ellipse(surf, SILVER_SH, (nx - 4, ny - 1, 8, 4))
    flick = math.sin(t * math.tau)            # -1..1 flame breathe
    reach = 9 + int(4 * (0.5 + 0.5 * flick))  # tongue length pulses
    sway = int(2 * flick)
    # Outer red-gold tongue.
    flame_o = [(nx - 5, ny + 2), (nx + 5, ny + 2),
               (nx + 2 + sway, ny + reach), (nx - 2 + sway, ny + reach + 2)]
    store_skins._poly(surf, RED, flame_o)
    # Mid gold tongue.
    flame_m = [(nx - 3, ny + 2), (nx + 3, ny + 2),
               (nx + 1 + sway, ny + reach - 2), (nx - 1 + sway, ny + reach - 1)]
    store_skins._poly(surf, GOLD, flame_m)
    # Hot white core.
    pygame.draw.line(surf, GOLD_HI, (nx, ny + 2),
                     (nx + sway, ny + reach - 4), 2)
    # A couple of flickering spark dots trailing the flame.
    if flick > 0:
        pygame.draw.circle(surf, GOLD, (nx + sway - 2, ny + reach + 3), 1)
        pygame.draw.circle(surf, GOLD_HI, (nx + sway + 2, ny + reach + 1), 1)


def _suit_details(surf):
    # ── minimal suit hardware ── the chest used to stack 3 buttons + a gauge
    # dial + a belt buckle right under the chin, which collapsed at 40px into a
    # red smudge that read as a wound crossing the face line. Cut to ONE small
    # red button placed LOW and off-centre on the belly, well clear of the face,
    # so the chrome torso stays clean and nothing red touches the dome.
    bxp, byp = 26, 45            # low + left of centre, below the face line
    pygame.draw.circle(surf, RED_D, (bxp, byp + 1), 2)
    pygame.draw.circle(surf, RED, (bxp, byp), 2)
    pygame.draw.circle(surf, (255, 170, 170), (bxp - 1, byp - 1), 1)

    # Chunky silver boots with a red sole stripe (over the bare feet).
    for fx in (26, 35):
        pygame.draw.ellipse(surf, SILVER_SH, (fx - 3, 47, 8, 6))
        pygame.draw.ellipse(surf, SILVER, (fx - 3, 46, 7, 5))
        pygame.draw.line(surf, RED, (fx - 3, 52), (fx + 4, 52), 2)


def _cuffs(surf):
    # Red ringed cuff at the wing root so the wing reads as a suited arm.
    wrx, wry = 39, 46
    pygame.draw.line(surf, RED_D, (wrx - 5, wry + 2), (wrx + 7, wry - 2), 5)
    pygame.draw.line(surf, RED, (wrx - 5, wry + 1), (wrx + 7, wry - 3), 3)
    pygame.draw.line(surf, (255, 170, 170), (wrx - 4, wry), (wrx + 5, wry - 3), 1)


def _keyline(surf):
    # Trace a 1px DARK outline around the opaque silhouette by stamping the
    # alpha mask offset in 8 directions under the figure. Cheap, target-agnostic
    # (no per-pixel loop / shader), and identical on desktop + WASM.
    mask = pygame.mask.from_surface(surf, 80)
    outline = mask.to_surface(setcolor=(*DARK, 255), unsetcolor=(0, 0, 0, 0))
    out = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1),
                   (-1, -1), (1, -1), (-1, 1), (1, 1)):
        out.blit(outline, (dx, dy))    # fattened dark silhouette
    out.blit(surf, (0, 0))             # original figure over its own dark ring
    surf.fill((0, 0, 0, 0))
    surf.blit(out, (0, 0))


def _fishbowl(surf, t):
    # ── tall clear FISHBOWL helmet (visor UP) over the head ── Pip's macaw face
    # stays fully visible inside; a bright CHROME RIM RING at the base seats it
    # on the suit, a single bold reflection streak crosses the glass, and a
    # bobbing ANTENNA with a glowing ball pokes up past the dome.
    cx, cy = HX + 1, HY - 1
    r = 16

    # ── FACE READ FIRST ── the chrome recolor erased Pip's eye, leaving a blank
    # grey head behind blank grey glass: the dome read as a featureless blob at
    # 40px. Fix it BEFORE the glass goes on. The macaw eye/beak live on the
    # lower-right of the head (native (50,20)/(52..61,21..28) → composite here).
    # 1) Brighten the head VALUE directly behind the face so it lifts off the
    #    cool glass tint and the dark eye has something pale to sit on.
    eye_x, eye_y = HX + 4, HY - 1          # ≈ (51, 40) — where the lens used to be
    _aaellipse(surf, (236, 240, 247), (HX + 2, HY), 8, 7)
    # 2) Punch a bold dark eye + bright catch-light: the single highest-contrast
    #    mark in the dome, so the face is unmistakably the thing you read.
    pygame.draw.circle(surf, (24, 26, 34), (eye_x, eye_y), 3)
    pygame.draw.circle(surf, (8, 9, 13), (eye_x, eye_y), 2)
    pygame.draw.circle(surf, GLASS_HI, (eye_x - 1, eye_y - 1), 1)

    # Faint cool glass tint behind the face, but punched OUT around the eye so
    # the tint never greys-down the one mark that carries the read.
    glass = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    pygame.draw.circle(glass, (*GLASS, 55), (cx, cy - 1), r - 1)
    pygame.draw.circle(glass, (0, 0, 0, 0), (eye_x, eye_y), 5)   # clear over face
    surf.blit(glass, (0, 0))

    # Bold reflection streak across the upper-left glass — the "it's a bubble"
    # tell, kept up and LEFT so it never crosses the face on the right.
    arc = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    pygame.draw.line(arc, (*GLASS_HI, 150), (cx - 9, cy - 8), (cx - 3, cy - 12), 3)
    pygame.draw.line(arc, (*GLASS_HI, 110), (cx - 11, cy - 2), (cx - 6, cy - 9), 2)
    surf.blit(arc, (0, 0))

    # Crisp bright glass outline ring (drawn over the face edges, open at the
    # bottom where the rim seats it) so the dome reads as a hard bubble at 40px.
    pygame.draw.arc(surf, GLASS_HI, (cx - r, cy - r, r * 2, r * 2),
                    math.radians(20), math.radians(200), 2)
    pygame.draw.arc(surf, GLASS, (cx - r, cy - r, r * 2, r * 2),
                    math.radians(200), math.radians(340), 1)

    # ── ONE bright rim band at the neck seal ── previously a dark base ellipse +
    # silver band + two rivets stacked into three competing grey shapes by the
    # antenna root. Collapse to a single bright silver band on a thin dark seat
    # so the dome cleanly "sits" on the suit without visual clutter.
    pygame.draw.ellipse(surf, DARK, (cx - 12, cy + 10, 25, 6))
    pygame.draw.ellipse(surf, SILVER_HI, (cx - 11, cy + 9, 23, 4))

    # ── bobbing ANTENNA with a glowing ball tip, poking past the dome ──
    # The stalk angle + tip position WOBBLE with the flap so it springs/bounces.
    wob = math.sin(t * math.tau)
    base = (cx + 7, cy - 13)            # rooted on the upper-right of the dome
    mid = (cx + 9 + int(2 * wob), cy - 20)
    tip = (cx + 11 + int(4 * wob), cy - 27 - int(2 * (0.5 + 0.5 * wob)))
    pygame.draw.line(surf, DARK, base, mid, 3)
    pygame.draw.line(surf, SILVER, base, mid, 2)
    pygame.draw.line(surf, DARK, mid, tip, 3)
    pygame.draw.line(surf, SILVER, mid, tip, 2)
    # Glowing gold ball tip with an additive halo so it pulses on the flap.
    glow = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    ga = int(70 + 60 * (0.5 + 0.5 * wob))
    pygame.draw.circle(glow, (*GOLD, ga), tip, 5)
    surf.blit(glow, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    pygame.draw.circle(surf, GOLD, tip, 3)
    pygame.draw.circle(surf, GOLD_HI, (tip[0] - 1, tip[1] - 1), 1)


def _paint(surf, wing_angle_deg):
    t = _anim(wing_angle_deg)

    # Rocket-pack sits BEHIND the bird, so capture the body and re-stamp it over
    # the pack — the fins + flame poke out past the tail while the straps hide.
    bird = surf.copy()
    surf.fill((0, 0, 0, 0))
    _rocket_pack(surf, t)
    surf.blit(bird, (0, 0))

    # ── 1px dark keyline around the body + dome OUTER silhouette ── the silver
    # suit and clear dome washed straight into the pale day sky (the red fins
    # already pop because they carry a keyline). Trace the bird's alpha edge in
    # DARK so the whole chrome figure reads as a crisp shape on any background.
    _keyline(surf)

    # Suit hardware over the body, cuffs on the wing root, then the fishbowl on
    # top of the (now silver) head so the face shows through the glass.
    _suit_details(surf)
    _cuffs(surf)
    _fishbowl(surf, t)


build = store_skins._make_skin(_paint, base_fn=_rocket_base)
