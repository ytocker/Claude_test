"""DESIGN 8 — NOVA DRIFTER: the sleek propulsive free-flyer (NASA MMU/SAFER).
The showpiece sibling of STARLINER — same near-white two-tone weight, but read
COLD and FAST: a flat CHROME mirror visor (silver, one crisp glint) instead of a
gold faceplate, and a winged RCS JETPACK on the back whose little thruster
NOZZLES flare out past the body like fins — the unmistakable silhouette-breaker
no other astronaut has.

Scratch exploration only — wrapped by ``store_skins._make_skin`` and rendered via
``tools/ninja_render.py``; NOT registered in ``store_skins.BUILDERS`` so the live
``skin_astronaut`` is untouched.

Baked-in 40px lessons: the WHOLE white suit is wrapped in a continuous navy
keyline (``_NAVY``) so it never washes out on the bright day sky; the chrome
visor is ONE clean dome with ONE horizontal glint (no muddy multi-streak); the
jetpack is anchored TIGHT and LOW, overlapped by the body, so the flared nozzles
read as fins ATTACHED to the back while the chrome HELMET still wins the focal
fight — never a second head. ONE accent story only: command navy + safety
orange, a single red commander stripe; no confetti.
"""
import math
import pygame

from game import store_skins
from game.store_skins import (
    HX, HY, CROWN_Y, _poly, COMPOSITE_W, COMPOSITE_H, PARROT_DY,
)
from game.parrot import _aaellipse, _WING_ANGLES, _add_outline
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette


# ── NOVA DRIFTER palette ─────────────────────────────────────────────────────
_SUIT_W    = (244, 246, 251)       # #F4F6FB suit white
_SUIT_SH   = (200, 206, 218)       # cool suit shadow
_NAVY      = (22, 34, 63)          # #16223F command navy (keyline + panels)
_NAVY_H    = (54, 70, 110)         # navy highlight so navy masses read on night
_ORANGE    = (255, 122, 26)        # #FF7A1A safety orange
_ORANGE_H  = (255, 178, 110)
_RED       = (211, 32, 48)         # #D32030 commander red
_CHROME    = (185, 196, 214)       # #B9C4D6 chrome mirror visor
_CHROME_D  = (120, 134, 160)       # mirror shadow / cold underside
_CHROME_H  = (224, 234, 248)       # cool blue-white sheen
_WHITE_HI  = (255, 255, 255)
_NAVY_KEY  = (22, 34, 63, 240)     # opaque navy silhouette outline


# Full near-WHITE suit recolour, same idiom as STARLINER so the whole bird is a
# bright blob the dark sky can't swallow — but the line work is cooler-navy so it
# ties to the command palette. Lenses dropped: the chrome visor owns the face.
P_NOVA = _pal(
    tail=[(212, 218, 230), (224, 229, 239), (234, 238, 246), (244, 246, 251)],
    tail_line=_SUIT_SH,
    body_shadow=(196, 202, 215),
    body_main=_SUIT_W,
    body_chest=(255, 255, 255),
    body_belly=(230, 235, 244),
    sheen=(255, 255, 255, 150),
    wing_main=(226, 231, 241),
    wing_dark=_SUIT_SH,
    wing_tip=(248, 250, 254),
    wing_secondary=None,
    wing_highlight=_WHITE_HI,
    head_shadow=(200, 206, 218),
    head_main=_SUIT_W,
    head_cheek=(248, 250, 254),
    head_crown=(255, 255, 255),
    lens_frame=(200, 206, 218),
    lens_body=_NAVY,
    lens_tint=None,
    lens_glint=None,
    beak_main=(60, 72, 100),
    beak_dark=_NAVY,
    beak_gloss=(140, 150, 172),
    foot=_NAVY,
)


def _white_base(angle_deg):
    # Glossy-white suited bird, no aviators — the chrome mirror visor owns the head.
    return _build_parrot_with_palette(angle_deg, P_NOVA, draw_lenses=False)


def _paint(surf, wing_angle_deg):
    # Body centre in composite space (parrot body centre (32,32) + PARROT_DY).
    BCX, BCY = 32, 52

    # The base wing angles run negative-on-downbeat; a small signed share drives
    # faint thruster glints so the jets puff on the flap (additive over the sky).
    thrust = max(0.0, -wing_angle_deg) / 22.0     # 0 at rest, →~1 on a hard downbeat

    # ── BACK: squared white RCS JETPACK, drawn FIRST so the body silhouette
    #    overlaps its inner edge → it reads worn ON the back, not beside the head.
    #    Anchored LOW and TIGHT to the shoulder; the flared NOZZLES poke past the
    #    back/side like fins (the outline-breaker), but the slab top sits well
    #    below the crown so the chrome helmet stays the largest+highest mass.
    pkx, pky = BCX - 12, BCY + 2          # back-shoulder anchor, low + tucked in
    # Squared maneuvering-unit slab: a clean white box, slightly canted so the
    # back corner is higher (a worn pack), never a vertical bar mirroring the head.
    pack = [(pkx - 6, pky - 7), (pkx + 5, pky - 9), (pkx + 8, pky + 2),
            (pkx + 7, pky + 12), (pkx - 5, pky + 13), (pkx - 7, pky + 3)]
    _poly(surf, _SUIT_SH, [(x, y + 1) for x, y in pack])   # soft underside
    _poly(surf, _SUIT_W, pack)
    pygame.draw.polygon(surf, _NAVY, pack, 1)              # navy keyline on the pack
    # Navy control panel band low on the slab (keeps the dark mass small + low).
    _poly(surf, _NAVY, [(pkx - 4, pky + 6), (pkx + 6, pky + 6),
                        (pkx + 5, pky + 11), (pkx - 4, pky + 11)])
    pygame.draw.line(surf, _ORANGE, (pkx - 2, pky + 8), (pkx + 3, pky + 8), 1)
    pygame.draw.line(surf, _NAVY_H, (pkx - 4, pky - 5), (pkx + 5, pky - 7), 1)
    # Two side hand-controller arms hinting at the pack edges (MMU tell).
    pygame.draw.line(surf, _NAVY, (pkx - 6, pky - 1), (pkx - 10, pky + 2), 2)
    pygame.draw.line(surf, _NAVY, (pkx + 7, pky + 4), (pkx + 11, pky + 7), 2)
    pygame.draw.circle(surf, _ORANGE, (pkx - 10, pky + 2), 1)

    # Flared thruster NOZZLES at the pack corners/sides — short navy cones whose
    # mouths flare OUT past the silhouette like fins. This is the unmistakable
    # free-flyer tell; faint additive jet glints puff from the mouths on a flap.
    nozzles = [
        (pkx - 8, pky - 6, -1, -1),   # upper-back corner
        (pkx - 9, pky + 11, -1,  1),  # lower-back corner
        (pkx + 9, pky + 12,  1,  1),  # lower-front, flares past the body side
        (pkx + 10, pky - 4,  1, -1),  # upper-front
    ]
    for nx, ny, sx, sy in nozzles:
        mouth = (nx + sx * 4, ny + sy * 3)
        # Short cone: a navy trapezoid widening to the flared mouth.
        cone = [(nx - sy * 2, ny + sx * 2), (nx + sy * 2, ny - sx * 2),
                (mouth[0] + sy * 3, mouth[1] - sx * 3),
                (mouth[0] - sy * 3, mouth[1] + sx * 3)]
        _poly(surf, _NAVY, cone)
        pygame.draw.line(surf, _CHROME_D, (nx, ny), mouth, 1)   # bright bore line
        # Faint thruster glint on the downbeat — additive so it puffs on the sky.
        if thrust > 0.05:
            a = int(120 * thrust)
            glow = pygame.Surface((9, 9), pygame.SRCALPHA)
            pygame.draw.circle(glow, (255, 200, 120, a), (4, 4), 4)
            pygame.draw.circle(glow, (255, 240, 200, min(255, a + 60)), (4, 4), 2)
            surf.blit(glow, (mouth[0] + sy * 3 - 4, mouth[1] + sx * 3 - 4),
                      special_flags=pygame.BLEND_RGBA_ADD)

    # ── BODY: NAVY shoulder yoke band across the upper chest — the one body panel
    #    that survives at 40px — plus a single RED commander stripe down the near
    #    arm. White stays clean below so the suit reads glossy and uncluttered.
    yoke = [(BCX - 14, BCY - 7), (BCX - 4, BCY - 12), (BCX + 9, BCY - 11),
            (BCX + 15, BCY - 5), (BCX + 9, BCY - 5), (BCX - 2, BCY - 7),
            (BCX - 11, BCY - 3)]
    _poly(surf, _NAVY, yoke)
    pygame.draw.line(surf, _NAVY_H, (BCX - 11, BCY - 6), (BCX + 11, BCY - 8), 1)
    # Red commander stripe running down the near (right) arm/wing root.
    pygame.draw.line(surf, _RED, (BCX + 9, BCY - 9), (BCX + 16, BCY - 3), 3)
    pygame.draw.line(surf, (255, 120, 130), (BCX + 10, BCY - 9), (BCX + 15, BCY - 4), 1)

    # ── CHEST: compact navy controller module with an ORANGE toggle + blue pips —
    #    the command-deck accent, kept off the face so the visor read stays pure.
    mx, my = BCX + 1, BCY + 2
    pygame.draw.rect(surf, _NAVY, (mx - 6, my - 3, 13, 9), border_radius=2)
    pygame.draw.rect(surf, _NAVY_H, (mx - 6, my - 3, 13, 9), 1, border_radius=2)
    pygame.draw.rect(surf, _ORANGE, (mx - 4, my - 1, 4, 3))           # orange toggle
    pygame.draw.circle(surf, _CHROME_H, (mx + 3, my), 1)             # blue-white pips
    pygame.draw.circle(surf, _CHROME_H, (mx + 5, my + 3), 1)
    pygame.draw.circle(surf, _ORANGE_H, (mx - 3, my + 4), 1)

    # ── LIMBS: navy gloves + boots with thin ORANGE cuff rings — the command
    #    palette reaches every extremity without adding a new colour.
    pygame.draw.line(surf, _NAVY, (BCX + 4, BCY - 6), (BCX + 14, BCY - 9), 2)
    pygame.draw.circle(surf, _NAVY, (BCX + 16, BCY - 4), 3)           # wingtip glove
    pygame.draw.circle(surf, _ORANGE, (BCX + 14, BCY - 6), 1)        # cuff ring
    pygame.draw.circle(surf, _WHITE_HI, (BCX + 15, BCY - 5), 1)
    for fx in (BCX - 6, BCX):                                         # boots
        pygame.draw.line(surf, _NAVY, (fx, BCY + 13), (fx - 1, BCY + 17), 3)
        pygame.draw.circle(surf, _NAVY, (fx - 1, BCY + 17), 2)
        pygame.draw.circle(surf, _ORANGE, (fx, BCY + 13), 1)         # orange cuff ring

    # ── HEAD: white helmet shell, navy collar, an orange comms-cap stripe over the
    #    crown, then the flat CHROME MIRROR visor (the cold, polished focal mass).
    hcx, hcy = HX + 1, HY - 1
    # Navy collar ring behind/under the dome so the helmet seats on the suit.
    pygame.draw.ellipse(surf, _NAVY, (hcx - 12, hcy + 7, 26, 10))
    pygame.draw.ellipse(surf, _NAVY_H, (hcx - 10, hcy + 8, 22, 4))
    # Thin white helmet shell hugging the head, with a crisp navy rim so the shell
    # separates from the white body (the outline pass only edges the outer
    # silhouette, so this internal rim carries the read at size).
    pygame.draw.ellipse(surf, _NAVY,   (hcx - 14, hcy - 14, 29, 27))
    pygame.draw.ellipse(surf, _SUIT_W, (hcx - 13, hcy - 13, 27, 25))
    pygame.draw.ellipse(surf, _NAVY,   (hcx - 13, hcy - 13, 27, 25), 1)
    # Safety-orange comms-cap stripe arcing over the crown — the one warm note up
    # top, well above the visor so it never muddies the mirror.
    pygame.draw.lines(surf, _ORANGE, False,
                      [(hcx - 9, hcy - 11), (hcx - 1, hcy - 14), (hcx + 8, hcy - 10)], 2)
    pygame.draw.lines(surf, _ORANGE_H, False,
                      [(hcx - 7, hcy - 12), (hcx - 1, hcy - 13)], 1)

    # Flat CHROME MIRROR visor — a clean silver dome filling the lower-front of the
    # shell with a cool blue-white sheen and ONE crisp horizontal glint. Mirror,
    # not glass: the value runs light chrome up top → cold steel at the chin, so it
    # reads polished/reflective and colder than a gold faceplate.
    vx, vy = hcx + 1, hcy + 2
    visor = [(vx - 12, vy - 5), (vx - 6, vy - 8), (vx + 8, vy - 8),
             (vx + 12, vy - 2), (vx + 9, vy + 7), (vx - 6, vy + 8),
             (vx - 11, vy + 2)]
    _poly(surf, _NAVY, [(x, y + 1) for x, y in visor])    # hard navy underline edge
    _poly(surf, _CHROME_D, visor)
    # Upper sheen band (lighter chrome) so the mirror reads convex + polished.
    _poly(surf, _CHROME, [(vx - 11, vy - 4), (vx - 5, vy - 7), (vx + 7, vy - 7),
                          (vx + 10, vy - 1), (vx + 4, vy + 1), (vx - 8, vy + 1)])
    _poly(surf, _CHROME_H, [(vx - 9, vy - 6), (vx - 1, vy - 7), (vx + 4, vy - 6),
                            (vx - 2, vy - 3), (vx - 8, vy - 3)])
    # ONE crisp horizontal glint line across the mirror — the single sheen read.
    pygame.draw.line(surf, _WHITE_HI, (vx - 8, vy - 1), (vx + 6, vy - 2), 2)
    pygame.draw.line(surf, _CHROME_H, (vx - 9, vy + 2), (vx + 4, vy + 1), 1)
    # Navy visor frame so the chrome stays a clean readable shape, not a smear.
    pygame.draw.polygon(surf, _NAVY, visor, 1)
    # Small navy chin/comms wedge under the mirror (no orange near the face).
    _poly(surf, _NAVY, [(vx - 4, vy + 7), (vx + 6, vy + 6),
                        (vx + 3, vy + 11), (vx - 2, vy + 11)])


def _build():
    # Same cached flat-build + per-(frame, 3°) rotation cache as _make_skin, but
    # the silhouette is wrapped in the NAVY keyline so the white suit holds a
    # crisp edge on the bright day sky instead of washing out.
    state = {"frames": None, "rot": {}}

    def _flat(wing_angle):
        comp = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
        comp.blit(_white_base(wing_angle), (0, PARROT_DY))
        _paint(comp, wing_angle)
        return _add_outline(comp, outline_color=_NAVY_KEY)

    def getter(frame_idx, tilt_deg):
        if state["frames"] is None:
            state["frames"] = [_flat(a) for a in _WING_ANGLES]
        frames = state["frames"]
        frame_idx %= len(frames)
        key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
        s = state["rot"].get(key)
        if s is None:
            s = pygame.transform.rotozoom(frames[frame_idx], key[1], 1.0)
            state["rot"][key] = s
        return s

    return getter


build = _build()
