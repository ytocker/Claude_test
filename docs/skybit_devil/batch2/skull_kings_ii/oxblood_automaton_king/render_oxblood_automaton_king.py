"""
Round-1 concept renderer for the OXBLOOD AUTOMATON KING — a royal skull-KING of
the Skull-Kings-II brood, rendered as a RIGID BLOCKY HUMANOID MACHINE. Headless
Pygame; ELEVATED pipeline (SS=6 supersample -> smoothscale) so the riveted plate
detail survives the downscale. Clones the sibling regent's house grammar wholesale:
flat triad fill (dark-core -> flat -> top-left sheen), a hard 1-2px ink keyline
(28,22,30), 1px alpha-grown outline, chibi proportions, scary-CUTE. Procedural-
only (no gradients/PNGs).

WHY this reads as a MACHINE, not a bone-lord: the whole figure is boxed —
riveted rectangular copper plates, a square torso, square pauldrons, PEG LEGS,
and CIRCULAR gear-rings at every joint. Two stiff geometric arms with gear-elbows;
no cradle. The de-collider from the sibling Bismuth Prism-Architect (a LIMBLESS
stepped-crystal mass) is the HUMANOID lock: peg legs + square pauldrons + visible
limbs + at least one prominent CIRCULAR gear-ring, so the two never twin.

WHY the heat stays WARM copper: the body is patinated copper-bronze (the dominant
mass); oxblood-lacquer panels are thin rectangular inlays; verdigris is kept to a
FEW thin ticks so the figure never cools toward green (it must NOT twin Malachite).
The single brightest pixel is the BRASS GEAR-EYE — a glowing toothed iris socket —
which owns the focal. Above the head: a brass skull finial on a clockwork
gear-spindle spire (the royal skull-crown tell).

WHY a standalone script under docs/: review art must never enter the shipped
bundle, so it reuses only colour math + the triad/outline helpers, not runtime
sprite modules.
"""
import math
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

# -- PINNED PALETTE (locked brief) --------------------------------------------
# Patinated copper-bronze is the DOMINANT warm mass; everything else is thin.
COPPER     = (178, 120,  78)   # patinated copper-bronze body (dominant fill)
COPPER_D   = (128,  82,  50)   # copper dark-core / recessed plate
COPPER_DD  = ( 92,  58,  36)   # deepest copper hollow (seams, joint gaps)
COPPER_SH  = (224, 168, 116)   # copper top-left rim-sheen
# oxblood-lacquer panel inlays — thin rectangular accents only
OXBLOOD    = (116,  36,  40)
OXBLOOD_BR = (158,  60,  58)
OXBLOOD_D  = ( 78,  24,  28)
# the SINGLE warm focal — the brass gear-eye iris (must stay brightest pixel).
BRASS      = (232, 196, 108)
BRASS_BR   = (252, 230, 168)   # hottest brass core (the brightest pixel)
BRASS_D    = (176, 142,  62)
# verdigris — kept MINIMAL (a few thin oxidation ticks) so body stays warm.
VERD       = (120, 168, 150)
VERD_D     = ( 84, 124, 110)
# dark structural iron (rivets, deep frame shadow)
IRON       = ( 58,  54,  56)
IRON_D     = ( 36,  34,  36)
INK        = ( 28,  22,  30)   # hard ink keyline

BG         = ( 96, 100, 108)   # neutral grey review backdrop
PANEL      = ( 74,  78,  88)
DAY_SKY_T  = (120, 196, 236)
DAY_SKY_B  = (196, 232, 244)
NIGHT_T    = ( 22,  26,  54)
NIGHT_B    = ( 48,  44,  82)
LABEL      = (238, 240, 244)
LABEL_DIM  = (188, 196, 208)


def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return (int(a[0] + (b[0]-a[0])*t),
            int(a[1] + (b[1]-a[1])*t),
            int(a[2] + (b[2]-a[2])*t))


def grow_outline(surf, color, px):
    mask = pygame.mask.from_surface(surf)
    pts = mask.outline()
    if len(pts) < 2:
        return surf
    base = surf.copy()
    ring = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    for (ox, oy) in pts:
        pygame.draw.circle(ring, color, (ox, oy), px)
    ring.blit(base, (0, 0))
    return ring


def triad_blob(surf, color, pts, sheen_pts=None, core_pts=None, outline=True, ow=2):
    """Flat fill + optional dark-core + top-left rim-sheen + ink keyline."""
    if outline:
        pygame.draw.polygon(surf, INK, pts)
    pygame.draw.polygon(surf, color, pts)
    if core_pts:
        pygame.draw.polygon(surf, lerp(color, INK, 0.42), core_pts)
    if sheen_pts:
        pygame.draw.polygon(surf, lerp(color, (255, 255, 255), 0.4), sheen_pts)
    if outline:
        pygame.draw.polygon(surf, INK, pts, ow)


def triad_circle(surf, color, c, r, ow=2, sheen=True, core=True):
    pygame.draw.circle(surf, INK, c, r + max(1, ow // 2))
    pygame.draw.circle(surf, color, c, r)
    if core:
        pygame.draw.circle(surf, lerp(color, INK, 0.4),
                           (c[0] + int(r * 0.28), c[1] + int(r * 0.30)),
                           int(r * 0.74))
        pygame.draw.circle(surf, color, c, int(r * 0.82))
    if sheen:
        pygame.draw.circle(surf, lerp(color, (255, 255, 255), 0.45),
                           (c[0] - int(r * 0.38), c[1] - int(r * 0.40)),
                           max(1, int(r * 0.26)))
    pygame.draw.circle(surf, INK, c, r, ow)


def rivet_plate(surf, x, y, w, h, color, s, rivets=True, inlay=False):
    """A riveted rectangular copper plate — the machine's building block. WHY a
    boxed rect with corner rivet pips: the blocky-humanoid silhouette is built
    from stacked plates, and the rivet dots read as 'worked metal' at hero scale
    while dissolving cleanly at 32px. `inlay` swaps the fill to oxblood lacquer."""
    fill = OXBLOOD if inlay else color
    core = OXBLOOD_D if inlay else lerp(color, INK, 0.40)
    sh = OXBLOOD_BR if inlay else lerp(color, (255, 255, 255), 0.40)
    rect = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
    triad_blob(surf, fill, rect,
               core_pts=[(x + w * 0.40, y + h * 0.42), (x + w, y + h * 0.30),
                         (x + w, y + h), (x + w * 0.40, y + h)],
               sheen_pts=[(x, y), (x + w * 0.55, y), (x + w * 0.30, y + h * 0.40),
                          (x, y + h * 0.50)],
               ow=max(1, int(1.3 * s)))
    if rivets:
        rr = max(1, int(1.6 * s))
        for rx in (x + w * 0.13, x + w * 0.87):
            for ry in (y + h * 0.16, y + h * 0.84):
                pygame.draw.circle(surf, IRON_D, (int(rx), int(ry)), rr + max(1, int(0.6 * s)))
                pygame.draw.circle(surf, lerp(color, (255, 255, 255), 0.25),
                                   (int(rx - rr * 0.3), int(ry - rr * 0.3)), rr)


def gear_ring(surf, cx, cy, r, s, teeth=10, color=COPPER, hub=True):
    """A prominent CIRCULAR toothed gear-ring — the de-collider from the sibling
    Bismuth's angular facets. WHY drawn as a notched disc with a dark hub: the
    round teeth read unmistakably as a cog at hero scale, and the circular
    silhouette stays legible (a clean dark ring) at 32px against any sky."""
    # toothed outer rim built as a star-ish polygon (alternating r / r*1.18)
    pts = []
    n = teeth * 2
    for k in range(n):
        a = math.radians(k * (360.0 / n))
        rr = r * (1.20 if k % 2 == 0 else 0.98)
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    pygame.draw.polygon(surf, INK, pts)
    pygame.draw.polygon(surf, lerp(color, INK, 0.30), pts)
    # flat disc face
    triad_circle(surf, color, (cx, cy), int(r * 0.92), ow=max(1, int(1.3 * s)),
                 core=False)
    if hub:
        # dark recessed hub with a bright bolt pip
        pygame.draw.circle(surf, COPPER_DD, (cx, cy), max(2, int(r * 0.36)))
        pygame.draw.circle(surf, INK, (cx, cy), max(2, int(r * 0.36)), max(1, int(1.0 * s)))
        pygame.draw.circle(surf, BRASS, (cx, cy), max(1, int(r * 0.18)))
        pygame.draw.circle(surf, BRASS_BR,
                           (cx - int(r * 0.07), cy - int(r * 0.08)), max(1, int(r * 0.09)))


def verd_ticks(surf, x, y, w, s, n=3):
    """A FEW thin verdigris oxidation ticks. WHY kept tiny + sparse: verdigris is
    a seasoning, not a mass — too much cools the copper toward green and twins
    the Malachite king. These are 1px green flecks riding a seam only."""
    for k in range(n):
        tx = x + (k + 0.5) * (w / n)
        pygame.draw.line(surf, VERD, (int(tx), int(y)), (int(tx), int(y + 2 * s)),
                         max(1, int(1.0 * s)))


def peg_leg(surf, hip, s, sgn):
    """A stiff square-shouldered PEG LEG — a boxed thigh plate tapering to a
    tapered peg foot, with a gear-ring at the hip. WHY a peg (not a bone limb):
    pegs lock the silhouette as a rigid machine and read clean against the sky."""
    hx, hy = hip
    thigh_w = int(13 * s)
    thigh_h = int(26 * s)
    rivet_plate(surf, hx - thigh_w // 2, hy, thigh_w, thigh_h, COPPER, s)
    # tapered peg shank below the thigh plate
    peg_top = hy + thigh_h
    peg = [(hx - int(6 * s), peg_top), (hx + int(6 * s), peg_top),
           (hx + int(4 * s), peg_top + int(22 * s)),
           (hx - int(4 * s), peg_top + int(22 * s))]
    triad_blob(surf, COPPER, peg,
               sheen_pts=[(hx - int(6 * s), peg_top), (hx - int(2 * s), peg_top),
                          (hx - int(2 * s), peg_top + int(22 * s)),
                          (hx - int(4 * s), peg_top + int(22 * s))],
               ow=max(1, int(1.2 * s)))
    # blocky foot pad
    foot = [(hx - int(9 * s), peg_top + int(22 * s)),
            (hx + int(10 * s), peg_top + int(22 * s)),
            (hx + int(10 * s), peg_top + int(30 * s)),
            (hx - int(9 * s), peg_top + int(30 * s))]
    triad_blob(surf, COPPER_D, foot, ow=max(1, int(1.2 * s)))
    # gear-ring at the hip (joint tell)
    gear_ring(surf, hx, hy, int(7 * s), s, teeth=8)


# -- the brass skull finial on a clockwork gear-spindle spire (royal crown) ----
def skull_spire(surf, cx, base_y, r, s):
    """A small brass SKULL finial atop a clockwork gear-spindle rising from the
    head — the royal skull-KING crown tell. WHY a thin vertical spindle with two
    stacked mini gears and a tiny skull cap: it gives a single above-head royal
    silhouette point that survives 32px (a small dark spike + a brass dot), and
    it reads mechanical (gears) not bony, so the king stays a machine."""
    # the spindle column rising from the crown
    spindle_h = int(r * 2.6)
    sx0 = cx - int(2.0 * s)
    sx1 = cx + int(2.0 * s)
    spire_top = base_y - spindle_h
    triad_blob(surf, BRASS_D,
               [(sx0, base_y), (sx1, base_y), (sx1, spire_top), (sx0, spire_top)],
               ow=max(1, int(1.0 * s)))
    # two stacked clockwork mini-gears riding the spindle
    for k, gy in enumerate((base_y - int(r * 0.8), base_y - int(r * 1.7))):
        gear_ring(surf, cx, int(gy), int(r * 0.42), s, teeth=7, color=BRASS, hub=False)
    # the brass skull finial cap
    skr = int(r * 0.62)
    sky = spire_top - int(skr * 0.4)
    triad_circle(surf, BRASS, (cx, sky), skr, ow=max(1, int(1.2 * s)), core=False)
    # two ink sockets so the finial reads as a skull
    for sg in (-1, 1):
        pygame.draw.circle(surf, INK,
                           (cx + sg * int(skr * 0.38), sky + int(skr * 0.02)),
                           max(1, int(skr * 0.26)))
    # stub jaw + bright pip so it stays brass + scary-cute
    pygame.draw.line(surf, IRON_D, (cx - int(skr * 0.34), sky + int(skr * 0.50)),
                     (cx + int(skr * 0.34), sky + int(skr * 0.52)), max(1, int(1.0 * s)))
    pygame.draw.circle(surf, BRASS_BR, (cx - int(skr * 0.3), sky - int(skr * 0.3)),
                       max(1, int(skr * 0.24)))


# -- the rigid blocky humanoid machine-king -----------------------------------
def draw_automaton(surf, cx, cy, s):
    head_c = (cx, cy - int(34 * s))
    hr = int(20 * s)
    torso_y = cy - int(8 * s)

    # === PEG LEGS (behind torso) ============================================
    for sg in (-1, 1):
        peg_leg(surf, (cx + sg * int(15 * s), cy + int(26 * s)), s, sg)

    # === SQUARE BOXY TORSO ===================================================
    tw = int(46 * s)
    th = int(40 * s)
    tx = cx - tw // 2
    rivet_plate(surf, tx, torso_y, tw, th, COPPER, s)
    # a central oxblood-lacquer chest inlay panel (thin rectangular accent)
    rivet_plate(surf, cx - int(11 * s), torso_y + int(8 * s),
                int(22 * s), int(22 * s), COPPER, s, rivets=False, inlay=True)
    # a small brass boiler-bolt centred on the oxblood panel
    triad_circle(surf, BRASS, (cx, torso_y + int(19 * s)), int(4 * s),
                 ow=max(1, int(1.0 * s)), core=False)
    # a few thin verdigris ticks along the bottom seam (minimal, warm-safe)
    verd_ticks(surf, tx + int(4 * s), torso_y + th - int(2 * s), tw - int(8 * s), s, n=4)
    # waist gear-ring (joint between torso and pelvis block)
    gear_ring(surf, cx, torso_y + th, int(8 * s), s, teeth=9)

    # === SQUARE PAULDRONS + STIFF GEOMETRIC ARMS (gear-elbows) ===============
    arm_th = int(11 * s)
    for sg in (-1, 1):
        # square pauldron plate capping the shoulder
        pw = int(16 * s)
        px = cx + sg * int(22 * s) - pw // 2
        py = torso_y - int(2 * s)
        rivet_plate(surf, px, py, pw, int(15 * s), COPPER, s)
        # shoulder gear-ring
        sh_c = (cx + sg * int(22 * s), torso_y + int(13 * s))
        # upper-arm boxed plate (straight down)
        ua_x = sh_c[0] - sg * 0 - arm_th // 2
        rivet_plate(surf, sh_c[0] - arm_th // 2, sh_c[1], arm_th, int(18 * s),
                    COPPER, s, rivets=False)
        # gear-elbow
        elbow = (sh_c[0], sh_c[1] + int(18 * s))
        gear_ring(surf, elbow[0], elbow[1], int(6 * s), s, teeth=8)
        # forearm boxed plate angling inward to the hip (stiff, geometric)
        fa_top = elbow
        fa_bot = (cx + sg * int(14 * s), torso_y + th - int(2 * s))
        dx, dy = fa_bot[0] - fa_top[0], fa_bot[1] - fa_top[1]
        L = max(1.0, math.hypot(dx, dy))
        nx, ny = -dy / L * arm_th * 0.42, dx / L * arm_th * 0.42
        fa = [(fa_top[0] + nx, fa_top[1] + ny), (fa_bot[0] + nx, fa_bot[1] + ny),
              (fa_bot[0] - nx, fa_bot[1] - ny), (fa_top[0] - nx, fa_top[1] - ny)]
        triad_blob(surf, COPPER, fa,
                   sheen_pts=[(fa_top[0] + nx, fa_top[1] + ny),
                              (fa_bot[0] + nx, fa_bot[1] + ny),
                              (fa_bot[0] + nx * 0.3, fa_bot[1] + ny * 0.3),
                              (fa_top[0] + nx * 0.3, fa_top[1] + ny * 0.3)],
                   ow=max(1, int(1.2 * s)))
        # blocky three-finger claw hand
        hand = [(fa_bot[0] - sg * int(5 * s), fa_bot[1]),
                (fa_bot[0] + sg * int(6 * s), fa_bot[1]),
                (fa_bot[0] + sg * int(5 * s), fa_bot[1] + int(9 * s)),
                (fa_bot[0] - sg * int(4 * s), fa_bot[1] + int(9 * s))]
        triad_blob(surf, COPPER_D, hand, ow=max(1, int(1.1 * s)))
        # shoulder gear-ring drawn last so it caps the joint cleanly
        gear_ring(surf, sh_c[0], sh_c[1], int(7 * s), s, teeth=9)

    # === SQUARE MACHINE SKULL HEAD ===========================================
    hw = int(40 * s)
    hx = head_c[0] - hw // 2
    hy = head_c[1] - int(18 * s)
    rivet_plate(surf, hx, hy, hw, int(36 * s), COPPER, s)
    # a thin oxblood brow band across the top of the face plate
    rivet_plate(surf, hx + int(3 * s), hy + int(3 * s), hw - int(6 * s), int(6 * s),
                COPPER, s, rivets=False, inlay=True)
    # the BRASS GEAR-EYE — the single focal. a toothed iris socket, glowing.
    eye_c = (head_c[0], head_c[1] + int(4 * s))
    eye_r = int(11 * s)
    # dark recessed socket box
    pygame.draw.circle(surf, INK, eye_c, eye_r + max(1, int(1.4 * s)))
    pygame.draw.circle(surf, COPPER_DD, eye_c, eye_r)
    # toothed brass iris ring (a tiny gear inside the eye)
    gear_ring(surf, eye_c[0], eye_c[1], int(eye_r * 0.74), s, teeth=10,
              color=BRASS, hub=False)
    # glowing brass pupil + the brightest pip
    pygame.draw.circle(surf, BRASS, eye_c, int(eye_r * 0.40))
    pygame.draw.circle(surf, BRASS_BR, (eye_c[0] - int(eye_r * 0.16),
                                        eye_c[1] - int(eye_r * 0.18)),
                       max(2, int(eye_r * 0.26)))
    # a small dark riveted jaw vent under the eye (mouth grille)
    grille_y = head_c[1] + int(15 * s)
    pygame.draw.rect(surf, IRON_D,
                     (head_c[0] - int(9 * s), grille_y, int(18 * s), int(5 * s)))
    pygame.draw.rect(surf, INK,
                     (head_c[0] - int(9 * s), grille_y, int(18 * s), int(5 * s)),
                     max(1, int(1.0 * s)))
    for k in range(-2, 3):
        gx = head_c[0] + int(k * 4 * s)
        pygame.draw.line(surf, COPPER_DD, (gx, grille_y),
                         (gx, grille_y + int(5 * s)), max(1, int(1.0 * s)))
    # neck gear-ring between head and torso
    gear_ring(surf, head_c[0], hy + int(36 * s), int(6 * s), s, teeth=8)

    # === ABOVE-HEAD royal CROWN — brass skull on clockwork gear-spire =========
    skull_spire(surf, head_c[0], hy + int(1 * s), int(13 * s), s)


# -- the boxed copper-column -> pillar mirror ---------------------------------
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """A stacked riveted copper-plate column with periodic gear-ring lashings —
    a direct continuation of the king's torso plates + joint gears. WHY this
    tiles cleanly: each segment is a boxed plate pair cinched by a gear-ring, and
    the gap-cap fans into a small machine-head crowned by a brass gear-eye + a
    skull-spire stub (the creature-derived gap edge, mirrored top<->bottom)."""
    shaft_w = int(20 * s)
    pygame.draw.rect(surf, IRON_D, (cx - int(4 * s), top, int(8 * s), bot - top))

    pitch = int(30 * s)
    cap_room = int(46 * s)
    if cap == "bottom":
        b0, b1 = top + int(10 * s), bot - cap_room
    else:
        b0, b1 = top + cap_room, bot - int(10 * s)
    y = b0
    while y <= b1:
        # a boxed copper plate segment
        rivet_plate(surf, cx - shaft_w // 2, int(y - pitch * 0.42),
                    shaft_w, int(pitch * 0.78), COPPER, s)
        # a thin oxblood inlay stripe down the centre of the plate
        rivet_plate(surf, cx - int(4 * s), int(y - pitch * 0.30),
                    int(8 * s), int(pitch * 0.54), COPPER, s, rivets=False, inlay=True)
        verd_ticks(surf, cx - shaft_w * 0.4, int(y + pitch * 0.30),
                   shaft_w * 0.8, s, n=3)
        # a gear-ring lashing cinching the segment joint
        gear_ring(surf, cx, int(y + pitch * 0.40), int(8 * s), s, teeth=9)
        y += pitch

    cap_y = (bot - int(30 * s)) if cap == "bottom" else (top + int(30 * s))
    fan_dir = -1 if cap == "bottom" else 1
    # the gap-cap machine-head block
    head_h = int(26 * s)
    hy = cap_y - (head_h if fan_dir < 0 else 0)
    rivet_plate(surf, cx - int(17 * s), hy, int(34 * s), head_h, COPPER, s)
    # a brass gear-eye on the cap (the creature focal echoed at the gap edge)
    eye_c = (cx, hy + head_h // 2)
    pygame.draw.circle(surf, INK, eye_c, int(8 * s))
    pygame.draw.circle(surf, COPPER_DD, eye_c, int(7 * s))
    gear_ring(surf, eye_c[0], eye_c[1], int(5 * s), s, teeth=9, color=BRASS, hub=False)
    pygame.draw.circle(surf, BRASS_BR, eye_c, int(3 * s))
    # a small skull-spire stub pointing into the gap
    spr_base = hy if fan_dir < 0 else hy + head_h
    sp = [(cx - int(3 * s), spr_base),
          (cx + int(3 * s), spr_base),
          (cx + int(2 * s), spr_base + fan_dir * int(12 * s)),
          (cx - int(2 * s), spr_base + fan_dir * int(12 * s))]
    triad_blob(surf, BRASS_D, sp, ow=max(1, int(1.0 * s)))
    triad_circle(surf, BRASS, (cx, spr_base + fan_dir * int(15 * s)), int(5 * s),
                 ow=max(1, int(1.0 * s)), core=False)


# -- compose the review sheet -------------------------------------------------
SS = 6


def vgrad(surf, rect, top_col, bot_col):
    x, y, w, h = rect
    for j in range(h):
        pygame.draw.line(surf, lerp(top_col, bot_col, j / max(1, h - 1)),
                         (x, y + j), (x + w, y + j))


def load_fonts():
    """FONT is five levels up from this script; SysFont fallback if missing."""
    base = os.path.dirname(os.path.abspath(__file__))
    fp = os.path.join(base, "..", "..", "..", "..", "..",
                      "game", "assets", "LiberationSans-Bold.ttf")
    try:
        return (pygame.font.Font(fp, 30), pygame.font.Font(fp, 17),
                pygame.font.Font(fp, 12))
    except Exception:
        return (pygame.font.SysFont("DejaVu Sans", 30, bold=True),
                pygame.font.SysFont("DejaVu Sans", 17, bold=True),
                pygame.font.SysFont("DejaVu Sans", 12))


def render_hero():
    big = pygame.Surface((360 * SS, 470 * SS), pygame.SRCALPHA)
    draw_automaton(big, 180 * SS, 250 * SS, 1.78 * SS)
    small = pygame.transform.smoothscale(big, (360, 470))
    return grow_outline(small, INK + (255,), 1)


def main():
    W, H = 1180, 820
    font_big, font, font_sm = load_fonts()

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    pygame.draw.rect(sheet, PANEL, (0, 0, W, 56))
    sheet.blit(font_big.render("OXBLOOD AUTOMATON KING", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "Skull-Kings-II  ·  rigid BLOCKY humanoid machine · riveted copper plates + peg legs + square pauldrons · "
        "circular GEAR-RINGS at joints · brass gear-eye focal · skull-on-gear-spire crown · round 1",
        True, LABEL_DIM), (360, 26))

    # === (a) BIG HERO =========================================================
    hero = render_hero()
    sheet.blit(hero, (14, 92))
    sheet.blit(font.render("Creature - hero", True, LABEL), (110, 566))
    sheet.blit(font_sm.render("Boxy copper machine: square torso + pauldrons, PEG LEGS, two stiff geometric", True, LABEL_DIM), (14, 590))
    sheet.blit(font_sm.render("arms w/ gear-elbows. Circular GEAR-RINGS at every joint (the de-collider).", True, LABEL_DIM), (14, 606))
    sheet.blit(font_sm.render("Brass GEAR-EYE = single focal; brass skull on a clockwork gear-spindle spire above.", True, LABEL_DIM), (14, 622))

    # === (b) PILLAR assembled - mirrored ======================================
    pcx = 470
    top_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(top_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="bottom")
    top_seg = grow_outline(pygame.transform.smoothscale(top_big, (150, 250)), INK + (255,), 1)
    sheet.blit(top_seg, (pcx, 86))
    bot_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(bot_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="top")
    bot_seg = grow_outline(pygame.transform.smoothscale(bot_big, (150, 250)), INK + (255,), 1)
    sheet.blit(bot_seg, (pcx, 86 + 250 + 96))
    pygame.draw.rect(sheet, (60, 64, 72), (pcx + 8, 86 + 250, 134, 96))
    sheet.blit(font_sm.render("GAP", True, LABEL_DIM), (pcx + 56, 86 + 250 + 40))
    sheet.blit(font.render("Pillar - copper plate column", True, LABEL), (pcx - 4, 690))
    sheet.blit(font_sm.render("stacked riveted plates + oxblood inlay stripe,", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("gear-ring lashings; gap-cap machine-head w/", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("gear-eye + skull-spire (mirrored top<->bottom)", True, LABEL_DIM), (pcx - 4, 746))

    # === (c) TRUE 32px chips on day + night sky + SILHOUETTE proof =============
    panel_x = 660
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 560))
    sheet.blit(font.render("True 32px gameplay-scale chip", True, LABEL), (panel_x + 16, 96))

    def chip32(night=False):
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_automaton(big, 48 * SS, 52 * SS, (32 / 124.0) * SS)
        small = pygame.transform.smoothscale(big, (96, 96))
        # WHY a warm brass-tinted rim on night (not a cool one): the copper mass
        # dims into a dark night sky; a thin warm halo carries the silhouette
        # while keeping the body warm and the brass eye the brightest point.
        if night:
            base = grow_outline(small, BRASS_D + (255,), 2)
            return grow_outline(base, INK + (200,), 1)
        return grow_outline(small, INK + (255,), 1)

    day_chip = chip32(night=False)
    night_chip = chip32(night=True)

    day_y = 128
    vgrad(sheet, (panel_x + 20, day_y, 150, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, day_y, 150, 150), 1)
    sheet.blit(day_chip, (panel_x + 20 + 27, day_y + 27))
    sheet.blit(font_sm.render("32px on day sky", True, LABEL), (panel_x + 20, day_y + 156))

    night_y = day_y + 184
    vgrad(sheet, (panel_x + 20, night_y, 150, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, night_y, 150, 150), 1)
    sheet.blit(night_chip, (panel_x + 20 + 27 - 1, night_y + 27 - 1))
    sheet.blit(font_sm.render("32px on night sky (brass rim)", True, LABEL_DIM), (panel_x + 20, night_y + 156))

    # silhouette proof - blacked-out hero so the blocky machine read is checked
    def silhouette():
        big = pygame.Surface((150 * SS, 200 * SS), pygame.SRCALPHA)
        draw_automaton(big, 75 * SS, 96 * SS, 1.28 * SS)
        small = pygame.transform.smoothscale(big, (150, 200))
        mask = pygame.mask.from_surface(small)
        sil = pygame.Surface((150, 200), pygame.SRCALPHA)
        solid = mask.to_surface(setcolor=(18, 18, 20, 255), unsetcolor=(0, 0, 0, 0))
        sil.blit(solid, (0, 0))
        return sil

    sil_x = panel_x + 196
    pygame.draw.rect(sheet, (210, 212, 216), (sil_x, day_y, 150, 200))
    pygame.draw.rect(sheet, INK, (sil_x, day_y, 150, 200), 1)
    sheet.blit(silhouette(), (sil_x, day_y))
    sheet.blit(font_sm.render("silhouette proof", True, LABEL_DIM), (sil_x, day_y + 204))
    sheet.blit(font_sm.render("(blocky humanoid + spire)", True, LABEL_DIM), (sil_x, day_y + 220))

    def pillar_chip32():
        big = pygame.Surface((44 * SS, 130 * SS), pygame.SRCALPHA)
        draw_pillar(big, 22 * SS, 2 * SS, 128 * SS, 0.34 * SS, cap="bottom")
        small = pygame.transform.smoothscale(big, (44, 130))
        return grow_outline(small, INK + (255,), 1)

    pc = pillar_chip32()
    px2 = sil_x + 168
    vgrad(sheet, (px2, day_y, 56, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (px2, day_y, 56, 150), 1)
    sheet.blit(pc, (px2 + 6, day_y + 10))
    vgrad(sheet, (px2, night_y, 56, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (px2, night_y, 56, 150), 1)
    sheet.blit(pc, (px2 + 6, night_y + 10))
    sheet.blit(font_sm.render("pillar", True, LABEL_DIM), (px2 + 4, day_y - 16))
    sheet.blit(font_sm.render("gap-cap", True, LABEL_DIM), (px2 - 2, night_y - 16))

    # palette swatches
    sheet.blit(font.render("Pinned palette", True, LABEL), (panel_x + 16, 510))
    swatches = [
        (COPPER, "patinated copper"), (COPPER_D, "copper shade"),
        (OXBLOOD, "oxblood lacquer"), (OXBLOOD_BR, "oxblood lit"),
        (BRASS, "brass gear-eye"), (BRASS_BR, "brass hot core"),
        (VERD, "verdigris tick"), (IRON, "iron rivet"),
        (COPPER_SH, "copper sheen"), (INK, "ink keyline"),
    ]
    sxp, syp = panel_x + 16, 538
    for i, (c, name) in enumerate(swatches):
        col, row = i % 2, i // 2
        rx = sxp + col * 188
        ry = syp + row * 24
        pygame.draw.rect(sheet, INK, (rx - 1, ry - 1, 20, 20))
        pygame.draw.rect(sheet, c, (rx, ry, 18, 18))
        sheet.blit(font_sm.render(name, True, LABEL), (rx + 26, ry + 3))

    pygame.draw.rect(sheet, PANEL, (14, 770, W - 28, 40))
    sheet.blit(font_sm.render(
        "RIGID BLOCKY HUMANOID MACHINE: peg legs + square pauldrons + circular GEAR-RINGS (vs Bismuth's limbless angular crystal).  "
        "WARM copper dominant mass; oxblood = thin inlays; verdigris = a FEW ticks only.  Brass gear-eye = single brightest pixel.  "
        "SS=6 supersample -> smoothscale · procedural-only.",
        True, LABEL_DIM), (26, 783))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(sheet, out)
    print("wrote", out)
    self_check()


def self_check():
    """Verify the brass gear-eye owns the single brightest pixel and that the
    body stays WARM (copper) — count warm copper pixels vs cool verdigris pixels;
    verdigris must be a tiny fraction so the figure never twins Malachite."""
    surf = pygame.Surface((400, 520), pygame.SRCALPHA)
    draw_automaton(surf, 200, 260, 2.0)
    px = pygame.surfarray.pixels3d(surf)
    a = pygame.surfarray.pixels_alpha(surf)
    w, h = surf.get_size()
    best_lum, best_xy = -1, (0, 0)
    warm_n, cool_n = 0, 0
    for x in range(0, w, 2):
        for yy in range(0, h, 2):
            if a[x, yy] < 40:
                continue
            r, g, b = int(px[x, yy][0]), int(px[x, yy][1]), int(px[x, yy][2])
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            if lum > best_lum:
                best_lum, best_xy = lum, (x, yy)
            # warm: red-dominant copper/brass/oxblood
            if r > g and r > b and r > 90:
                warm_n += 1
            # cool: green-dominant verdigris
            if g > r and g > b and g > 90:
                cool_n += 1
    bx, by = best_xy
    r, g, b = int(px[bx, by][0]), int(px[bx, by][1]), int(px[bx, by][2])
    # brass-core hue: very bright, warm, red>=green>blue-ish
    is_brass = (r > 220 and g > 180 and b < 200 and r >= b)
    del px, a
    print("self-check: brightest pixel @", best_xy, "rgb", (r, g, b),
          "lum %.0f" % best_lum, "-> brass-core?", is_brass)
    print("self-check: warm px ~%d  vs cool px ~%d  -> cool fraction %.3f (must be small)"
          % (warm_n, cool_n, cool_n / max(1, warm_n + cool_n)))


if __name__ == "__main__":
    main()
