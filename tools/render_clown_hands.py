"""Look-dev: ELEVATE the Warren-event jester's HANDS, FEET and STAFF GRIP.

The hero court jester (the `prop_14n` Golden Jester · bell-foot staff leaner)
reads well overall, but two areas still look amateur: the hands are a single
round mitt with a one-line thumb, and the feet are a flat sole + a curled-toe
wedge + bell. This sheet keeps EVERYTHING the approved hero owns — the plotting
contrapposto lean, the head tilt, the costume / collar / cap / face, the
`prop_14n` staff planted beside the figure — and ONLY restyles the hands, the
feet, and the staff-holding pose, across FIVE genuinely distinct hand+feet
languages.

THE POSE (every panel): the lower/near (RIGHT) gloved hand WRAPS the planted
staff shaft — one or two fingers + the thumb cross IN FRONT of the shaft, the
rest of the hand sits behind it, so it reads as truly gripping with the weight
resting (a relaxed showman lean). The raised (LEFT) hand is an OPEN offering
palm with spread fingers, the floating power-up die hovering just above it.

We import the REAL hero scaffolding (build_jester, prop_14n, draw_cupped_die,
JESTERS[-1] spec, the chunky arm/shade kit) and mutate no game state. The new
hand + feet drawing lives here as clean parameterised primitives so a winning
language can later move into render_clown_dice.py untouched. Procedural only —
no PNG sprites. Each panel is supersampled then smoothscaled for crisp edges.

    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy PYTHONPATH=. \
        python tools/render_clown_hands.py
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game import hud
from game.draw import lerp_color

from tools.render_clown_dice import (
    _shade, RIM, VIEW_W, VIEW_H, VIEW_FEET_Y, SS as CLOWN_SS,
)
from tools.render_jester_variants import (
    build_jester, JESTERS, draw_cupped_die, _bell,
)
from tools.render_warren_sword import (
    prop_14n, _grounded_prop_surface, _HIP_DX, _HIP_OFF,
)
from tools.render_warren_mockup import shaped_palette
from tools.render_clown_dice import DAY_PHASE


# The glove cream + its keyline, shared so every hand reads as one material.
GLOVE = (250, 250, 252)
GLOVE_DK = _shade(GLOVE, -58)
GLOVE_MD = _shade(GLOVE, -26)
GLOVE_HI = (255, 255, 255)


# ── shared hand math ─────────────────────────────────────────────────────────
# A hand is built from a PALM mass plus a small number of FINGER capsules. Every
# finger is one thick rounded line (a capsule) with a darker keyline under it and
# a 1px crease toward the tip — finger definition by 2-3 STRONG creases +
# occlusion, never hairline scribbles, so it survives shrinking to gameplay size.

def _finger(surf, base, tip, w, *, crease=True):
    """One rounded finger capsule from knuckle `base` to `tip`, keylined and
    softly creased so it reads as a digit, not a stripe."""
    pygame.draw.line(surf, GLOVE_DK, base, tip, w + 2)
    pygame.draw.line(surf, GLOVE, base, tip, w)
    pygame.draw.circle(surf, GLOVE, tip, w // 2)
    pygame.draw.circle(surf, GLOVE_DK, tip, w // 2, 1)
    # Top-left sheen down the lit edge so the digit reads round.
    pygame.draw.line(surf, GLOVE_HI,
                     (base[0] - 1, base[1] - 1), (tip[0] - 1, tip[1] - 1),
                     max(1, w // 3))
    if crease:
        mx = (base[0] + tip[0]) // 2
        my = (base[1] + tip[1]) // 2
        pygame.draw.line(surf, GLOVE_MD, (mx - w // 3, my), (mx + w // 3, my), 1)


def _palm(surf, cx, cy, rx, ry, *, cuff=None):
    """The rounded palm mass with a soft top-left sheen + dark keyline, and an
    optional cuff colour ring at the wrist so a gauntlet can tie into it."""
    rect = pygame.Rect(cx - rx, cy - ry, rx * 2, ry * 2)
    pygame.draw.ellipse(surf, GLOVE_DK, rect)
    pygame.draw.ellipse(surf, GLOVE, rect.inflate(-2, -2))
    sheen = pygame.Surface((rx, ry), pygame.SRCALPHA)
    pygame.draw.ellipse(sheen, (255, 255, 255, 90), sheen.get_rect())
    surf.blit(sheen, (cx - rx + 1, cy - ry + 1))
    if cuff is not None:
        pygame.draw.arc(surf, cuff, rect.inflate(4, 4),
                        math.pi * 0.75, math.pi * 0.25, 3)


# ── OPEN offering palms (raised hand, die hovering above) ─────────────────────
# Each language presents the same gesture — a palm tipped up toward the die with
# fingers SPREAD and the thumb out to one side — but in its own finger grammar.

def open_hand_anatomical(surf, hand):
    """Four slim separated fingers + an opposed thumb fanned over a slim palm."""
    hx, hy = hand
    _palm(surf, hx, hy, 8, 7)
    for i, ang in enumerate((-58, -30, -6, 18)):
        a = math.radians(ang - 90)
        ln = 15 - abs(i - 1)         # middle pair longest, outer pair shorter
        tip = (hx + int(math.cos(a) * ln), hy + int(math.sin(a) * ln))
        _finger(surf, (hx, hy - 2), tip, 5)
    thumb = (hx - 13, hy + 4)
    _finger(surf, (hx - 4, hy + 3), thumb, 6, crease=False)


def open_hand_toon(surf, hand):
    """Three plump cartoon-mascot fingers + a fat thumb, bold dark seams."""
    hx, hy = hand
    _palm(surf, hx, hy, 9, 8)
    for ang in (-52, -18, 16):
        a = math.radians(ang - 90)
        tip = (hx + int(math.cos(a) * 13), hy + int(math.sin(a) * 13))
        _finger(surf, (hx, hy - 1), tip, 7)
    _finger(surf, (hx - 5, hy + 4), (hx - 14, hy + 6), 8, crease=False)
    # Two bold seam rays splitting the three fingers (the Mickey-glove read).
    for ang in (-35, 0):
        a = math.radians(ang - 90)
        ex = hx + int(math.cos(a) * 11)
        ey = hy + int(math.sin(a) * 11)
        pygame.draw.line(surf, GLOVE_DK, (hx, hy), (ex, ey), 2)


def open_hand_elegant(surf, hand):
    """Long slender courtly fingers tapering off a refined oval palm."""
    hx, hy = hand
    _palm(surf, hx, hy, 7, 8)
    for i, ang in enumerate((-64, -40, -16, 10)):
        a = math.radians(ang - 90)
        ln = 20 - abs(i - 1) * 2     # graceful long taper
        tip = (hx + int(math.cos(a) * ln), hy + int(math.sin(a) * ln))
        _finger(surf, (hx, hy - 2), tip, 4)
        # An extra knuckle crease near the base reads as a poised, articulated
        # finger rather than a stiff stick.
        pygame.draw.circle(surf, GLOVE_MD,
                           (hx + int(math.cos(a) * 5), hy + int(math.sin(a) * 5)),
                           1)
    _finger(surf, (hx - 4, hy + 2), (hx - 16, hy - 2), 5, crease=False)


def open_hand_chunky(surf, hand):
    """The chibi mitt mass KEPT, but carved into real fat fingers by deep grooves."""
    hx, hy = hand
    _palm(surf, hx, hy, 11, 9)
    # Three fat stubs barely clearing the mitt, defined mostly by the grooves
    # between them rather than by length.
    for ang in (-48, -16, 16):
        a = math.radians(ang - 90)
        tip = (hx + int(math.cos(a) * 10), hy + int(math.sin(a) * 10))
        _finger(surf, (hx, hy), tip, 8)
    _finger(surf, (hx - 7, hy + 3), (hx - 15, hy + 2), 9, crease=False)
    # Deep dark grooves carve the single mass into distinct fingers.
    for ang in (-32, 0):
        a = math.radians(ang - 90)
        ex = hx + int(math.cos(a) * 12)
        ey = hy + int(math.sin(a) * 12)
        pygame.draw.line(surf, GLOVE_DK, (hx, hy + 2), (ex, ey), 3)


def open_hand_gauntlet(surf, hand, *, cuff):
    """Articulated fingers rising out of a scalloped belled gauntlet cuff."""
    hx, hy = hand
    # Scalloped cuff lobes hugging the wrist below the palm, tying to the costume.
    for s in (-1, 0, 1):
        lx = hx + s * 7
        pygame.draw.circle(surf, _shade(cuff, -50), (lx, hy + 9), 5)
        pygame.draw.circle(surf, cuff, (lx, hy + 9), 4)
        pygame.draw.circle(surf, _shade(cuff, 60), (lx - 1, hy + 8), 1)
    _bell(surf, hx, hy + 13, r=3)
    _palm(surf, hx, hy, 8, 7)
    for i, ang in enumerate((-56, -28, -2, 22)):
        a = math.radians(ang - 90)
        ln = 14 - abs(i - 1)
        tip = (hx + int(math.cos(a) * ln), hy + int(math.sin(a) * ln))
        _finger(surf, (hx, hy - 1), tip, 5)
    _finger(surf, (hx - 4, hy + 2), (hx - 13, hy + 3), 6, crease=False)


# ── WRAP hands (lower hand gripping the planted staff shaft) ───────────────────
# The grip is drawn in THREE z-passes so the occlusion reads as a real grasp:
#   1. BEHIND: the palm heel + the back knuckles sit behind the shaft.
#   2. (the shaft is already on the layer — drawn by the caller before this.)
#   3. FRONT: 1-2 fingertips + the thumb cross IN FRONT of the shaft.
# `behind=True` paints pass 1; `behind=False` paints pass 3. `shaft_w` is the
# half-width of the shaft so the wrapping digits land ON the wood.

def wrap_anatomical(surf, hand, shaft_w, *, behind):
    hx, hy = hand
    if behind:
        _palm(surf, hx + 3, hy, 8, 7)
        # Back of the four fingers curling over the far side of the shaft.
        for dy in (-6, -1, 4, 9):
            _finger(surf, (hx + 6, hy + dy), (hx - shaft_w + 1, hy + dy), 4)
    else:
        # Two fingertips + the thumb crossing in front, gripping the near face.
        for dy in (-3, 6):
            _finger(surf, (hx + 6, hy + dy), (hx - shaft_w - 2, hy + dy), 4)
        _finger(surf, (hx + 8, hy - 9), (hx - 2, hy - 11), 5, crease=False)


def wrap_toon(surf, hand, shaft_w, *, behind):
    hx, hy = hand
    if behind:
        _palm(surf, hx + 3, hy, 9, 8)
        for dy in (-4, 4, 11):
            _finger(surf, (hx + 7, hy + dy), (hx - shaft_w + 1, hy + dy), 6)
    else:
        for dy in (0, 9):
            _finger(surf, (hx + 7, hy + dy), (hx - shaft_w - 2, hy + dy), 6)
        _finger(surf, (hx + 9, hy - 8), (hx - 3, hy - 11), 7, crease=False)


def wrap_elegant(surf, hand, shaft_w, *, behind):
    hx, hy = hand
    if behind:
        _palm(surf, hx + 4, hy, 7, 8)
        for dy in (-7, -2, 3, 8):
            _finger(surf, (hx + 5, hy + dy), (hx - shaft_w, hy + dy), 3)
    else:
        # A single long elegant index + the thumb cross in front — a light,
        # poised rest rather than a fist.
        _finger(surf, (hx + 6, hy + 1), (hx - shaft_w - 3, hy - 1), 3)
        _finger(surf, (hx + 8, hy - 10), (hx - 3, hy - 13), 4, crease=False)


def wrap_chunky(surf, hand, shaft_w, *, behind):
    hx, hy = hand
    if behind:
        _palm(surf, hx + 3, hy, 11, 9)
        for dy in (-5, 3, 11):
            _finger(surf, (hx + 8, hy + dy), (hx - shaft_w + 1, hy + dy), 8)
    else:
        for dy in (-1, 9):
            _finger(surf, (hx + 8, hy + dy), (hx - shaft_w - 3, hy + dy), 8)
        _finger(surf, (hx + 10, hy - 9), (hx - 3, hy - 12), 9, crease=False)


def wrap_gauntlet(surf, hand, shaft_w, *, behind, cuff):
    hx, hy = hand
    if behind:
        for s in (-1, 0, 1):
            lx = hx + 4 + s * 7
            pygame.draw.circle(surf, _shade(cuff, -50), (lx, hy + 9), 5)
            pygame.draw.circle(surf, cuff, (lx, hy + 9), 4)
        _bell(surf, hx + 4, hy + 13, r=3)
        _palm(surf, hx + 3, hy, 8, 7)
        for dy in (-6, -1, 4, 9):
            _finger(surf, (hx + 6, hy + dy), (hx - shaft_w + 1, hy + dy), 4)
    else:
        for dy in (-3, 6):
            _finger(surf, (hx + 6, hy + dy), (hx - shaft_w - 2, hy + dy), 4)
        _finger(surf, (hx + 8, hy - 9), (hx - 2, hy - 11), 5, crease=False)


# ── refined belled curled-toe jester feet (one per language) ──────────────────
# Every foot keeps the jester identity — a pointed toe that curls up to a bell —
# but is crafted with sole VOLUME, a heel block, and a lit toe-cap so it reads as
# a shaped shoe, not a flat ellipse. The `style` only varies the silhouette
# subtly so the user sees options matched to each hand language.

def jester_foot(surf, cx, feet_y, sep, length, color, toe, *, lean=0,
                style="anatomical"):
    """Both refined curled-toe belled shoes. `style` tweaks proportion: a slim
    elegant last, a plump toon last, a chunky block, or a cuffed gauntlet spat."""
    for s in (-1, 1):
        bx = cx + s * sep + (lean if s > 0 else lean // 2)
        # SOLE: a rounded wedge with real volume — a darker undersole + a lit
        # uppersole so the foot has a top plane catching the key light.
        sole = pygame.Rect(0, 0, length, 15)
        if s < 0:
            sole.topright = (bx + length // 3, feet_y)
        else:
            sole.topleft = (bx - length // 3, feet_y)
        # Heel block at the back so the shoe has a crafted base, not a flat oval.
        heel_x = sole.right - 3 if s < 0 else sole.left + 3
        pygame.draw.ellipse(surf, _shade(color, -70),
                            (heel_x - 5, sole.bottom - 8, 11, 9))
        pygame.draw.ellipse(surf, _shade(color, -60), sole)
        upper = sole.inflate(-3, -4)
        upper.y = sole.y
        pygame.draw.ellipse(surf, color, upper)
        # Lit top plane of the sole (top-left key) so the volume reads.
        cap = pygame.Rect(0, 0, length // 2, 7)
        cap.center = (sole.centerx - s * length // 8, sole.top + 4)
        pygame.draw.ellipse(surf, _shade(color, 40), cap)

        # CURLED TOE sweeping up + out to the bell. Built as a tapering filled
        # spine with a lit front facet so the curl reads volumetric, and a deeper
        # under-curl shadow so it lifts off the sole.
        toe_base = (sole.right - 4, sole.centery) if s > 0 else \
                   (sole.left + 4, sole.centery)
        if style == "elegant":
            reach, rise = 15, 16     # long graceful curl
        elif style == "toon":
            reach, rise = 10, 11
        elif style == "chunky":
            reach, rise = 9, 10      # short fat curl
        elif style == "gauntlet":
            reach, rise = 12, 14
        else:                        # anatomical
            reach, rise = 12, 13
        tipx = toe_base[0] + s * reach
        tipy = toe_base[1] - rise
        curl = [(toe_base[0], toe_base[1] + 5),
                (toe_base[0], toe_base[1] - 5),
                (toe_base[0] + s * reach // 2, toe_base[1] - rise + 3),
                (tipx, tipy),
                (tipx - s * 3, tipy + 5),
                (toe_base[0] + s * reach // 3, toe_base[1] + 3)]
        pygame.draw.polygon(surf, _shade(toe, -30), curl)
        pygame.draw.polygon(surf, toe,
                            [(toe_base[0], toe_base[1] - 5),
                             (toe_base[0] + s * reach // 2, toe_base[1] - rise + 3),
                             (tipx, tipy)])
        pygame.draw.polygon(surf, _shade(toe, -65), curl, 2)
        # Lit toe-cap kiss where the curl meets the sole.
        pygame.draw.circle(surf, _shade(toe, 45),
                           (toe_base[0] + s * 2, toe_base[1] - 2), 2)
        if style == "gauntlet":
            # A small scalloped spat band over the ankle, echoing the cuff.
            for k in (-1, 1):
                pygame.draw.circle(surf, _shade(color, 30),
                                   (sole.centerx + k * 5, sole.top - 4), 3)
        _bell(surf, tipx, tipy, r=3)


# ── the five hand+feet languages ──────────────────────────────────────────────

VERSIONS = [
    ("Anatomical Glove",
     "4 slim fingers + opposed thumb; slim crafted last, long heel curl",
     "anatomical", open_hand_anatomical, wrap_anatomical),
    ("Toon 3-Finger",
     "3 plump fingers + fat thumb, bold seams; plump rounded last",
     "toon", open_hand_toon, wrap_toon),
    ("Elegant Tapered",
     "long slender courtly fingers; long graceful curled-toe last",
     "elegant", open_hand_elegant, wrap_elegant),
    ("Chunky Carved",
     "chibi mitt mass carved by deep grooves into fat fingers; short block last",
     "chunky", open_hand_chunky, wrap_chunky),
    ("Belled Gauntlet",
     "scalloped belled cuff + articulated fingers; matching cuffed spat last",
     "gauntlet", open_hand_gauntlet, wrap_gauntlet),
]


def render_panel(idx, version):
    """ONE hero clown leaning on `prop_14n`, posed exactly like the approved
    hero, but with this version's hand + feet language painted over the figure
    in the correct z-order so the wrap hand truly grips the planted shaft."""
    name, note, style, open_fn, wrap_fn = version
    spec = dict(JESTERS[-1][1])
    spec.pop("no_shadow", None)
    ss = CLOWN_SS
    palette = shaped_palette(DAY_PHASE)
    bw, bh = VIEW_W * ss, VIEW_H * ss
    big = pygame.Surface((bw, bh))

    # Day-clearing sky + a sliver of grass, matching the hero panel exactly.
    ground_y = VIEW_FEET_Y + 4
    g_y = int(ground_y * ss)
    for y in range(g_y):
        t = 0.45 + 0.55 * (y / g_y)
        pygame.draw.line(big, lerp_color(palette['sky_mid'], palette['sky_bot'], t),
                         (0, y), (bw, y))
    for y in range(g_y, bh):
        t = (y - g_y) / max(1, bh - g_y)
        pygame.draw.line(big, lerp_color(palette['ground_top'], palette['ground_mid'], t),
                         (0, y), (bw, y))
    pygame.draw.line(big, _shade(palette['ground_top'], 15), (0, g_y), (bw, g_y))

    layer = pygame.Surface((VIEW_W, VIEW_H), pygame.SRCALPHA)
    jester_cx = VIEW_W // 2 - 10
    feet_y = VIEW_FEET_Y

    die_x = jester_cx - 40
    die_base_y = 34
    hand_up = (die_x + 10, 80)
    cuff = spec["light"]
    build_jester(layer, jester_cx, feet_y, hand_up, **spec)

    # Repaint the FEET over build_jester's default belled shoes with this
    # version's crafted last (same anchor + lean the builder uses).
    jester_foot(layer, jester_cx, feet_y, 15, 24,
                _shade(spec["dark"], -10), _shade(spec["gold"], 10),
                lean=5, style=style)

    # Repaint the raised hand as an OPEN offering palm (build_jester drew a round
    # mitt at hand_up). The die hovers just above it.
    if style == "gauntlet":
        open_hand_gauntlet(layer, hand_up, cuff=cuff)
    else:
        open_fn(layer, hand_up)

    # --- the GROUNDED prop_14n the clown leans on --------------------------
    hip_y = feet_y - _HIP_OFF
    hip_cx = jester_cx + _HIP_DX
    prop_px = 150
    p_ss = 6
    prop, p_w, p_h = _grounded_prop_surface(prop_14n, prop_px, p_ss, w_scale=1.0)
    rot = -7
    rotated = pygame.transform.rotate(prop, rot)
    foot_local = (p_w / 2, p_h - 2)
    cxr, cyr = p_w / 2, p_h / 2
    rad = math.radians(rot)
    dx = foot_local[0] - cxr
    dy = foot_local[1] - cyr
    rfx = cxr + (dx * math.cos(rad) + dy * math.sin(rad))
    rfy = cyr + (-dx * math.sin(rad) + dy * math.cos(rad))
    rfx += (rotated.get_width() - p_w) / 2
    rfy += (rotated.get_height() - p_h) / 2
    plant_x = jester_cx + 30
    plant_y = ground_y - 1
    prop_ox = int(plant_x - rfx)
    prop_oy = int(plant_y - rfy)

    # Grip point on the upper shaft (just below the marotte head).
    grip_frac = 0.32
    grip_local = (p_w / 2, p_h * grip_frac)
    gdx = grip_local[0] - cxr
    gdy = grip_local[1] - cyr
    rgx = cxr + (gdx * math.cos(rad) + gdy * math.sin(rad))
    rgy = cyr + (-gdx * math.sin(rad) + gdy * math.cos(rad))
    rgx += (rotated.get_width() - p_w) / 2
    rgy += (rotated.get_height() - p_h) / 2
    grip_x = prop_ox + rgx
    grip_y = prop_oy + rgy
    grip_hand = (int(grip_x), int(grip_y))
    # Half-width of the shaft on screen (prop_14n shaft is ~7px at ss=1 scale,
    # scaled by the prop's output width vs its authored box width).
    shaft_w = max(4, int(7 * p_w / ((58 + 24))))

    # --- z-ordered grip: arm + back-of-hand BEHIND, shaft, fingers IN FRONT ---
    r_sh = (hip_cx + 25, hip_y - 50)
    light = spec["light"]
    # The forearm reaching toward the grip, drawn as a tapered limb (same kit
    # tone as the figure) so the hand connects to the body.
    mx = (r_sh[0] + grip_hand[0]) // 2
    my = (r_sh[1] + grip_hand[1]) // 2 + 4
    pygame.draw.line(layer, _shade(light, -50), r_sh, (mx, my), 11)
    pygame.draw.line(layer, _shade(light, -50), (mx, my), grip_hand, 9)
    pygame.draw.line(layer, light, r_sh, (mx, my), 8)
    pygame.draw.line(layer, light, (mx, my), grip_hand, 7)
    pygame.draw.circle(layer, _shade(light, 30), (mx, my), 5)

    # Pass 1 — back of the wrapping hand, behind the shaft.
    if style == "gauntlet":
        wrap_gauntlet(layer, grip_hand, shaft_w, behind=True, cuff=cuff)
    else:
        wrap_fn(layer, grip_hand, shaft_w, behind=True)
    # Pass 2 — the planted staff itself.
    layer.blit(rotated, (prop_ox, prop_oy))
    # Pass 3 — fingertips + thumb crossing IN FRONT of the shaft (the grip read).
    if style == "gauntlet":
        wrap_gauntlet(layer, grip_hand, shaft_w, behind=False, cuff=cuff)
    else:
        wrap_fn(layer, grip_hand, shaft_w, behind=False)

    # --- the floating power-up die, presented up high by the open hand --------
    pulse = idx * 1.7 + 2.0
    draw_cupped_die(layer, die_x, die_base_y, pulse, show_inset=False)

    big.blit(pygame.transform.smoothscale(layer, (bw, bh)), (0, 0))
    panel = pygame.transform.smoothscale(big, (VIEW_W, VIEW_H))
    return panel, name, note


def main():
    pygame.init()
    pygame.font.init()

    panels = [render_panel(i, v) for i, v in enumerate(VERSIONS)]

    pad = 18
    head = 92
    gap = 14
    strip = 40
    pw, ph = VIEW_W, VIEW_H
    cols = 5
    sheet_w = pad * 2 + cols * pw + (cols - 1) * gap
    sheet_h = head + strip + ph + pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((26, 28, 36))

    title_f = hud._font(28, True)
    sub_f = hud._font(14, True)
    name_f = hud._font(17, True)
    note_f = hud._font(12, False)
    sheet.blit(title_f.render("Warren Jester — HANDS + FEET + STAFF GRIP",
                              True, (250, 230, 150)), (pad, 14))
    sheet.blit(sub_f.render(
        "Holding prop_14n (Golden Jester); lower hand WRAPS the shaft, "
        "raised hand OPEN under the die", True, (190, 200, 220)), (pad, 48))
    sheet.blit(sub_f.render(
        "Lean, head tilt, costume, collar, cap, face all unchanged — only "
        "hands + feet + grip restyled", True, (150, 165, 190)), (pad, 68))

    for i, (panel, name, note) in enumerate(panels):
        x = pad + i * (pw + gap)
        y = head
        nstrip = pygame.Surface((pw, strip), pygame.SRCALPHA)
        nstrip.fill((18, 20, 28, 230))
        nstrip.blit(name_f.render(f"{i + 1}. {name}", True, (250, 220, 140)),
                    (6, 4))
        # Wrap the note onto a second line so it fits the panel width.
        words = note.split()
        line1, line2 = [], []
        for wd in words:
            if note_f.size(" ".join(line1 + [wd]))[0] < pw - 12:
                line1.append(wd)
            else:
                line2.append(wd)
        nstrip.blit(note_f.render(" ".join(line1), True, (180, 190, 205)),
                    (6, 21))
        if line2:
            nstrip.blit(note_f.render(" ".join(line2), True, (180, 190, 205)),
                        (6, 30))
        sheet.blit(nstrip, (x, y))
        sheet.blit(panel, (x, y + strip))
        pygame.draw.rect(sheet, (60, 64, 78),
                         (x, y, pw, strip + ph), 1)

    out_dir = "/home/user/skybit/docs/warren_clown"
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "round_1.png")
    pygame.image.save(sheet, out)
    print(f"wrote {out}  ({sheet_w}x{sheet_h})")


if __name__ == "__main__":
    main()
