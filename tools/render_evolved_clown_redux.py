"""Look-dev: the LATE-GAME EVOLVED warren clown — boss escalation (REDUX r1).

ONE figure, SIX cells, all on a single shared ground line:
  cell 0  the FAITHFUL CURRENT clown (Plum & Lime FINAL), clown-only, no die/staff
  cells 1-5  five GROUND-UP boss escalations of the SAME warren jester lineage —
             nastier, meaner, FUNNIER, grandiose and physically LARGER.

The DOCTRINE this sheet obeys: the five evolved bosses are five separate
designs, not one shown five ways. They differ in KIND across concept,
silhouette, construction and shape language. There is NO shared figure/body
builder among them — each boss owns its own builder + primitives. Only the
low-level paint helpers (`_shade`, `_bell`, a gradient line) are shared, which
is allowed. Quick proof of the five silhouettes (the blackout test):

  1 COLOSSUS   wide bottom-heavy TRIANGLE (huge coat-skirt + plumed mitre)
  2 PUPPETEER  tall gaunt VERTICAL stick (stilt legs + drooping spire bundle)
  3 GLUTTON    a single dominant CIRCLE orb (belly is the whole body)
  4 SPIDER     a radial STAR/BURST (six arms fanned off a diamond carapace)
  5 JANUS      an asymmetric SPLIT with a billowing banner SAIL behind it

Evolved palette across all five (the lineage GROWN, soured + tarnished):
  bruised deep plum, soured venom lime, tarnished dirty gold, blood/bruise
  accents. Each boss is drawn at native K-scale (geometry multiplied by K) and
  blit 1:1 — no smoothscale upscale — so faces stay crisp.

    PYTHONPATH=. python tools/render_evolved_clown_redux.py
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

# Cell 0 reproduces the REAL current clown verbatim through the shipped builder.
from tools.render_jester_variants import build_jester, JESTERS
from tools.render_clown_dice import _shade


# ── evolved lineage palette (the Plum & Lime jester GROWN + soured) ──────────
# Deeper bruised plum, a soured venom lime, tarnished dirty gold, blood/bruise
# accents. Shared across the five bosses so they read as ONE evolved family even
# though their silhouettes diverge hard.
PLUM_DEEP   = (58, 24, 78)      # bruised deep plum (the body north-star dark)
PLUM_DARK   = (40, 16, 56)      # near-black plum for shadow cores / keylines
PLUM_BRUISE = (96, 38, 110)     # lifted plum highlight / facet
VENOM       = (150, 196, 60)    # soured venom lime (the loud accent)
VENOM_DEEP  = (96, 132, 36)     # shaded venom
VENOM_LIT   = (196, 228, 110)   # lit venom edge
GOLD        = (196, 158, 54)    # tarnished dirty gold
GOLD_LIT    = (236, 204, 110)   # lit gold facet
GOLD_DARK   = (120, 92, 28)     # gold shadow / keyline
BLOOD       = (158, 30, 42)     # blood / bruise accent (maw, wounds, tongue)
BLOOD_DARK  = (96, 14, 26)
BONE        = (236, 226, 198)   # aged ivory teeth / bone
SKIN        = (214, 196, 176)   # greyed sickly clown skin (was warm peach)
SKIN_SHADE  = (150, 132, 120)
INK         = (18, 12, 22)
EYE_GLINT   = (210, 248, 120)   # venom-lit eye glint (the one bright cue)
WHITE       = (240, 240, 232)    # sclera / eye-white

GROUND_COL  = (74, 96, 52)      # matched ground band under all six
GROUND_LIT  = (104, 132, 74)
BG_TOP      = (96, 92, 110)     # neutral mid-tone backdrop, slightly cool
BG_BOT      = (78, 74, 92)


# ── shared LOW-LEVEL paint helpers (allowed — not a figure builder) ──────────

def _grad_v(surf, rect, top, bot):
    """Vertical gradient fill into a rect (shared primitive)."""
    x, y, w, h = rect
    for i in range(h):
        t = i / max(1, h - 1)
        c = (int(top[0] + (bot[0] - top[0]) * t),
             int(top[1] + (bot[1] - top[1]) * t),
             int(top[2] + (bot[2] - top[2]) * t))
        pygame.draw.line(surf, c, (x, y + i), (x + w, y + i))


def _bell(surf, x, y, r, col=GOLD):
    """A tarnished gold bell sphere with a lit cap + a dark base nub."""
    pygame.draw.circle(surf, GOLD_DARK, (int(x), int(y)), r + 1)
    pygame.draw.circle(surf, col, (int(x), int(y)), r)
    pygame.draw.circle(surf, GOLD_LIT, (int(x - r // 2), int(y - r // 2)),
                       max(1, r // 2))
    pygame.draw.line(surf, GOLD_DARK, (x - r // 2, y + r - 1),
                     (x + r // 2, y + r - 1), 1)


def _glint(surf, x, y, r):
    """The single bright eye-glint cue every boss face must carry, so the face
    holds at small size."""
    pygame.draw.circle(surf, EYE_GLINT, (int(x), int(y)), r)
    pygame.draw.circle(surf, (255, 255, 240), (int(x), int(y)), max(1, r // 2))


def _bruise(surf, x, y, rx, ry, alpha=90):
    """A soft bruise/blood blotch (bruised-lineage skin damage), alpha-blended."""
    s = pygame.Surface((rx * 2 + 2, ry * 2 + 2), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (*BLOOD, alpha), s.get_rect())
    surf.blit(s, (int(x - rx), int(y - ry)))


# ─────────────────────────────────────────────────────────────────────────────
# BOSS 1 — THE RINGMASTER COLOSSUS
# Thesis: a towering BAROQUE circus-ringmaster boss — a wide bottom-heavy
# triangle dominated by a colossal dagged tailcoat-skirt and an immense
# plume-crested mitre fused to the jester cap; arms flung wide in a "BEHOLD!"
# showman flare. Construction: stacked trapezoidal dagged coat panels (its own
# skirt builder), epaulet shoulder shelves, a tall plumed mitre. NOTHING shared
# with the other four builders.
# ─────────────────────────────────────────────────────────────────────────────

def build_colossus(surf, cx, feet_y, K):
    s = K
    # The grand triangular coat-skirt: a wide dagged hem sweeping up to narrow
    # shoulders — drawn as its OWN trapezoid + a row of hanging dagges.
    hem_y = feet_y - 6 * s
    skirt_w = 96 * s
    shoulder_w = 52 * s
    waist_y = feet_y - 96 * s
    skirt = [(cx - shoulder_w, waist_y), (cx + shoulder_w, waist_y),
             (cx + skirt_w, hem_y), (cx - skirt_w, hem_y)]
    pygame.draw.polygon(surf, PLUM_DEEP, skirt)
    # Sculpt: lit left facet + dark right.
    pygame.draw.polygon(surf, PLUM_BRUISE,
                        [(cx - shoulder_w, waist_y), (cx - 6 * s, waist_y),
                         (cx - 30 * s, hem_y), (cx - skirt_w, hem_y)])
    pygame.draw.polygon(surf, PLUM_DARK,
                        [(cx + 14 * s, waist_y), (cx + shoulder_w, waist_y),
                         (cx + skirt_w, hem_y), (cx + 40 * s, hem_y)])
    pygame.draw.polygon(surf, PLUM_DARK, skirt, 2 * s)
    # A venom centre-placket running up the coat with gold frog-buttons.
    pygame.draw.polygon(surf, VENOM_DEEP,
                        [(cx - 10 * s, waist_y), (cx + 10 * s, waist_y),
                         (cx + 16 * s, hem_y), (cx - 16 * s, hem_y)])
    pygame.draw.polygon(surf, VENOM,
                        [(cx - 8 * s, waist_y), (cx + 4 * s, waist_y),
                         (cx + 8 * s, hem_y), (cx - 12 * s, hem_y)])
    for i in range(5):
        by = waist_y + (hem_y - waist_y) * (i + 0.5) / 5
        _bell(surf, cx - s, by, 3 * s)
    # Dagged hem: a row of hanging venom-tipped triangles along the bottom.
    n = 9
    for i in range(n):
        t0 = i / n
        t1 = (i + 1) / n
        x0 = cx - skirt_w + 2 * skirt_w * t0
        x1 = cx - skirt_w + 2 * skirt_w * t1
        mid = (x0 + x1) / 2
        col = VENOM if i % 2 else GOLD
        dag = [(x0, hem_y - 2 * s), (x1, hem_y - 2 * s), (mid, hem_y + 12 * s)]
        pygame.draw.polygon(surf, col, dag)
        pygame.draw.polygon(surf, _shade(col, -60), dag, s)
        _bell(surf, mid, hem_y + 12 * s, 2 * s)

    # Two stout legs just peeking below the skirt in harlequin hose.
    for sgn, col in ((-1, VENOM), (1, PLUM_BRUISE)):
        lx = cx + sgn * 26 * s
        pygame.draw.line(surf, _shade(col, -50), (lx, hem_y), (lx, feet_y - 4 * s),
                         9 * s)
        pygame.draw.line(surf, col, (lx, hem_y), (lx, feet_y - 4 * s), 6 * s)
    # Big curled-toe boots planted wide.
    for sgn in (-1, 1):
        bx = cx + sgn * 26 * s
        boot = pygame.Rect(0, 0, 26 * s, 12 * s)
        boot.center = (bx + sgn * 6 * s, feet_y - 2 * s)
        pygame.draw.ellipse(surf, PLUM_DARK, boot)
        pygame.draw.ellipse(surf, PLUM_DEEP, boot.inflate(-3 * s, -3 * s))
        tip = (bx + sgn * 20 * s, feet_y - 2 * s)
        curl = [(bx + sgn * 12 * s, feet_y + 3 * s),
                (bx + sgn * 12 * s, feet_y - 7 * s), tip]
        pygame.draw.polygon(surf, GOLD, curl)
        _bell(surf, tip[0], tip[1] - 2 * s, 3 * s)

    # Shoulder shelf / epaulets: broad ornamental gold shelves the arms hang off.
    for sgn in (-1, 1):
        shx = cx + sgn * shoulder_w
        ep = [(cx + sgn * 18 * s, waist_y - 2 * s),
              (shx + sgn * 18 * s, waist_y - 6 * s),
              (shx + sgn * 14 * s, waist_y + 14 * s),
              (cx + sgn * 16 * s, waist_y + 12 * s)]
        pygame.draw.polygon(surf, GOLD, ep)
        pygame.draw.polygon(surf, GOLD_DARK, ep, s)
        # Bullion fringe under the epaulet.
        for k in range(4):
            fx = shx + sgn * (4 + k * 4) * s
            pygame.draw.line(surf, GOLD_LIT, (fx, waist_y + 12 * s),
                             (fx, waist_y + 20 * s), max(1, s))

    # Arms flung wide + UP in the grandiose BEHOLD flare, ending in gauntlets.
    sh_y = waist_y + 2 * s
    for sgn, hand_up in ((-1, (cx - 78 * s, waist_y - 40 * s)),
                         (1, (cx + 78 * s, waist_y - 44 * s))):
        sh = (cx + sgn * (shoulder_w - 6 * s), sh_y)
        elbow = (cx + sgn * 70 * s, waist_y - 8 * s)
        pygame.draw.line(surf, PLUM_DARK, sh, elbow, 11 * s)
        pygame.draw.line(surf, PLUM_DEEP, sh, elbow, 8 * s)
        pygame.draw.line(surf, PLUM_DARK, elbow, hand_up, 9 * s)
        pygame.draw.line(surf, PLUM_DEEP, elbow, hand_up, 6 * s)
        # Flared venom cuff + a big gold gauntlet fist presenting upward.
        pygame.draw.circle(surf, VENOM_DEEP, elbow, 7 * s)
        pygame.draw.circle(surf, GOLD_DARK, hand_up, 9 * s)
        pygame.draw.circle(surf, GOLD, hand_up, 8 * s)
        pygame.draw.circle(surf, GOLD_LIT, (hand_up[0] - 2 * s, hand_up[1] - 2 * s),
                           3 * s)

    # A grand layered ruff between the shoulders.
    neck_y = waist_y - 6 * s
    for i in range(11):
        t = i / 10
        rx = cx + int((-1 + 2 * t) * 30 * s)
        ry = neck_y + int(math.sin(t * math.pi) * -4 * s)
        pygame.draw.circle(surf, GOLD_DARK, (rx, ry), 7 * s)
        pygame.draw.circle(surf, GOLD, (rx, ry), 6 * s)
        pygame.draw.circle(surf, GOLD_LIT, (rx - 2 * s, ry - 2 * s), 2 * s)

    # HEAD — broad sneering ringmaster face.
    hr = 22 * s
    hy = neck_y - hr - 2 * s
    pygame.draw.circle(surf, SKIN_SHADE, (cx, hy), hr + s)
    pygame.draw.circle(surf, SKIN, (cx, hy), hr)
    _bruise(surf, cx + 12 * s, hy + 6 * s, 7 * s, 5 * s, 70)
    _colossus_face(surf, cx, hy, hr, s)

    # The IMMENSE plumed mitre — a tall pointed hat fused with two flung jester
    # horns, crowned by an extravagant feather plume. This is the grandiosity.
    cap_base = hy - hr + 4 * s
    mitre = [(cx - 20 * s, cap_base), (cx + 20 * s, cap_base),
             (cx + 8 * s, cap_base - 52 * s), (cx - 8 * s, cap_base - 52 * s)]
    pygame.draw.polygon(surf, PLUM_DEEP, mitre)
    pygame.draw.polygon(surf, PLUM_BRUISE,
                        [(cx - 20 * s, cap_base), (cx - 4 * s, cap_base),
                         (cx - 8 * s, cap_base - 52 * s)])
    pygame.draw.polygon(surf, PLUM_DARK, mitre, 2 * s)
    # Venom chevron band across the mitre.
    pygame.draw.polygon(surf, VENOM,
                        [(cx - 18 * s, cap_base - 14 * s),
                         (cx + 18 * s, cap_base - 14 * s),
                         (cx + 16 * s, cap_base - 24 * s),
                         (cx - 16 * s, cap_base - 24 * s)])
    # Two flung jester horns off the mitre sides, each belled.
    for sgn in (-1, 1):
        tip = (cx + sgn * 40 * s, cap_base - 30 * s)
        horn = [(cx + sgn * 14 * s, cap_base - 8 * s),
                (cx + sgn * 18 * s, cap_base - 22 * s), tip]
        pygame.draw.polygon(surf, GOLD, horn)
        pygame.draw.polygon(surf, GOLD_DARK, horn, s)
        _bell(surf, tip[0], tip[1], 3 * s)
    # Extravagant feather plume bursting from the mitre peak.
    peak = (cx, cap_base - 52 * s)
    for k, ang in enumerate((-0.5, -0.15, 0.2, 0.55)):
        col = VENOM if k % 2 else GOLD
        tipx = peak[0] + math.sin(ang) * 34 * s
        tipy = peak[1] - 30 * s + abs(ang) * 8 * s
        plume = [(peak[0] - 3 * s, peak[1]), (peak[0] + 3 * s, peak[1]),
                 ((peak[0] + tipx) / 2 + 5 * s, (peak[1] + tipy) / 2),
                 (tipx, tipy),
                 ((peak[0] + tipx) / 2 - 4 * s, (peak[1] + tipy) / 2)]
        pygame.draw.polygon(surf, col, plume)
        pygame.draw.polygon(surf, _shade(col, -55), plume, s)
    pygame.draw.circle(surf, GOLD_DARK, peak, 4 * s)
    pygame.draw.circle(surf, GOLD, peak, 3 * s)


def _colossus_face(surf, cx, hy, hr, s):
    # Heavy sunken brow shelf — a hard dark bar (macro shape that reads small).
    pygame.draw.polygon(surf, PLUM_DARK,
                        [(cx - 15 * s, hy - 5 * s), (cx + 15 * s, hy - 5 * s),
                         (cx + 12 * s, hy + 2 * s), (cx - 12 * s, hy + 2 * s)])
    for sgn in (-1, 1):
        ex = cx + sgn * 8 * s
        # Glaring eye — narrow venom slit under the shelf.
        pygame.draw.ellipse(surf, INK, (ex - 5 * s, hy, 10 * s, 8 * s))
        _glint(surf, ex - sgn * 1 * s, hy + 3 * s, 3 * s)
        # Curled showman moustache flourish.
    pygame.draw.circle(surf, BLOOD, (cx, hy + 9 * s), 4 * s)  # red nose, smaller
    pygame.draw.circle(surf, _shade(BLOOD, 70), (cx - s, hy + 8 * s), 2 * s)
    # A wide grinning sneer with a moustache curling over it + one fang.
    grin = pygame.Rect(cx - 14 * s, hy + 12 * s, 28 * s, 12 * s)
    pygame.draw.arc(surf, BLOOD_DARK, grin, math.pi, math.tau, 3 * s)
    teeth_y = hy + 16 * s
    pygame.draw.polygon(surf, BONE,
                        [(cx - 12 * s, teeth_y), (cx + 12 * s, teeth_y),
                         (cx + 9 * s, teeth_y + 4 * s), (cx - 9 * s, teeth_y + 4 * s)])
    for tx in range(-2, 3):
        gx = cx + tx * 5 * s
        pygame.draw.line(surf, BLOOD_DARK, (gx, teeth_y), (gx, teeth_y + 4 * s), s)
    # One fang.
    pygame.draw.polygon(surf, BONE, [(cx - 9 * s, teeth_y + 4 * s),
                                     (cx - 5 * s, teeth_y + 4 * s),
                                     (cx - 7 * s, teeth_y + 9 * s)])
    # Up-curled gold moustache over the lip.
    for sgn in (-1, 1):
        pygame.draw.arc(surf, GOLD_DARK,
                        (cx + sgn * 2 * s - 12 * s, hy + 9 * s, 24 * s, 12 * s),
                        (math.pi * 1.1 if sgn < 0 else math.tau * 0.0),
                        (math.tau if sgn < 0 else math.pi * 0.9), 3 * s)


# ─────────────────────────────────────────────────────────────────────────────
# BOSS 2 — THE PUPPETEER ABOVE
# Thesis: a long, looming MARIONETTE-MASTER — impossibly tall + gaunt, on
# stilt-thin bird legs, with dangling control-strings off clawed hands and a
# drooping bundle of cap-spires collapsing over the skull. Construction: an
# elongated stick-and-knob limb spine (its OWN segmented limb builder), a
# drooping spire-bundle cap, hanging string filaments + a crossbar control.
# Tall thin VERTICAL silhouette — the opposite of boss 1's wide triangle.
# ─────────────────────────────────────────────────────────────────────────────

def _stick_limb(surf, pts, w, col):
    """A gaunt segmented limb: thin shafts with knobby joints (puppeteer's OWN
    limb primitive — bones-on-strings read, not the chunky tapered arm)."""
    for i in range(len(pts) - 1):
        pygame.draw.line(surf, _shade(col, -60), pts[i], pts[i + 1], w + 2)
        pygame.draw.line(surf, col, pts[i], pts[i + 1], w)
    for p in pts:
        pygame.draw.circle(surf, _shade(col, -50), p, w // 2 + 2)
        pygame.draw.circle(surf, col, p, w // 2 + 1)
        pygame.draw.circle(surf, _shade(col, 40), (p[0] - 1, p[1] - 1), max(1, w // 3))


def build_puppeteer(surf, cx, feet_y, K):
    s = K
    # Stilt-thin bird legs splayed to a narrow stance — long bones + knee knobs.
    hip_y = feet_y - 130 * s
    for sgn in (-1, 1):
        ankle = (cx + sgn * 16 * s, feet_y - 6 * s)
        knee = (cx + sgn * 22 * s, feet_y - 64 * s)
        hip = (cx + sgn * 8 * s, hip_y)
        _stick_limb(surf, [hip, knee, ankle], 6 * s,
                    VENOM if sgn < 0 else PLUM_BRUISE)
        # Long pointed slipper foot, curled, belled.
        toe = (ankle[0] + sgn * 18 * s, ankle[1] - 8 * s)
        foot = [(ankle[0] - sgn * 4 * s, ankle[1] + 4 * s),
                (ankle[0] - sgn * 4 * s, ankle[1] - 5 * s), toe]
        pygame.draw.polygon(surf, PLUM_DEEP, foot)
        pygame.draw.polygon(surf, PLUM_DARK, foot, s)
        _bell(surf, toe[0], toe[1], 3 * s)

    # A long lean torso — a narrow tapering column, not a chunky block.
    torso = [(cx - 14 * s, hip_y + 4 * s), (cx + 14 * s, hip_y + 4 * s),
             (cx + 10 * s, hip_y - 70 * s), (cx - 10 * s, hip_y - 70 * s)]
    pygame.draw.polygon(surf, PLUM_DEEP, torso)
    pygame.draw.polygon(surf, PLUM_BRUISE,
                        [(cx - 14 * s, hip_y + 4 * s), (cx - 4 * s, hip_y + 4 * s),
                         (cx - 4 * s, hip_y - 70 * s), (cx - 10 * s, hip_y - 70 * s)])
    pygame.draw.polygon(surf, PLUM_DARK, torso, 2 * s)
    # Venom rib-lacing chevrons down the gaunt torso (skeletal cage read).
    for i in range(5):
        ry = hip_y - 6 * s - i * 14 * s
        wv = (12 - i) * s
        pygame.draw.line(surf, VENOM, (cx - wv, ry), (cx, ry + 4 * s), 2 * s)
        pygame.draw.line(surf, VENOM, (cx, ry + 4 * s), (cx + wv, ry), 2 * s)
    shoulder_y = hip_y - 70 * s

    # Long spidery arms reaching DOWN-and-OUT, ending in clawed hands that hold
    # the marionette control crossbar; strings dangle from the claws.
    for sgn in (-1, 1):
        sh = (cx + sgn * 10 * s, shoulder_y + 4 * s)
        elbow = (cx + sgn * 40 * s, shoulder_y + 30 * s)
        wrist = (cx + sgn * 34 * s, shoulder_y + 64 * s)
        _stick_limb(surf, [sh, elbow, wrist], 5 * s,
                    PLUM_BRUISE if sgn < 0 else VENOM)
        # Clawed three-finger hand.
        for f in (-1, 0, 1):
            fx = wrist[0] + sgn * 2 * s + f * 4 * s
            pygame.draw.line(surf, GOLD_DARK, wrist,
                             (fx, wrist[1] + 12 * s), 2 * s)
            pygame.draw.circle(surf, GOLD, (fx, wrist[1] + 12 * s), 2 * s)
        # Dangling control strings from each claw down past the feet.
        for f in (-1, 1):
            sx = wrist[0] + f * 4 * s
            pygame.draw.line(surf, (210, 206, 190),
                             (sx, wrist[1] + 12 * s), (sx + f * 2 * s, feet_y - 8 * s), 1)

    # A small marionette control crossbar gripped between the hands — the
    # gleeful "I pull the strings" gag prop.
    bar_y = shoulder_y + 70 * s
    pygame.draw.line(surf, GOLD_DARK, (cx - 28 * s, bar_y), (cx + 28 * s, bar_y), 4 * s)
    pygame.draw.line(surf, GOLD, (cx - 28 * s, bar_y), (cx + 28 * s, bar_y), 2 * s)

    # A tall narrow heraldic collar — a thin ruff of long dagged points.
    neck_y = shoulder_y - 2 * s
    for i in range(7):
        t = (i - 3) / 3
        tx = cx + int(t * 18 * s)
        pygame.draw.polygon(surf, GOLD,
                            [(cx, neck_y - 6 * s), (tx - 4 * s, neck_y + 10 * s),
                             (tx + 4 * s, neck_y + 10 * s)])
        pygame.draw.polygon(surf, GOLD_DARK,
                            [(cx, neck_y - 6 * s), (tx - 4 * s, neck_y + 10 * s),
                             (tx + 4 * s, neck_y + 10 * s)], s)
        _bell(surf, tx, neck_y + 11 * s, 2 * s)

    # HEAD — long gaunt skull, hollow-cheeked.
    hr = 18 * s
    hy = neck_y - hr - 8 * s
    head = pygame.Rect(0, 0, hr * 2, int(hr * 2.4))
    head.center = (cx, hy)
    pygame.draw.ellipse(surf, SKIN_SHADE, head.inflate(2 * s, 2 * s))
    pygame.draw.ellipse(surf, SKIN, head)
    # Hollow cheek shadows (gaunt).
    _bruise(surf, cx - 12 * s, hy + 4 * s, 5 * s, 9 * s, 60)
    _bruise(surf, cx + 12 * s, hy + 4 * s, 5 * s, 9 * s, 60)
    _puppeteer_face(surf, cx, hy, hr, s)

    # Drooping spire-bundle cap: a fan of long limp spires flopping over the
    # skull like dead branches, each belled. Grandiose-decrepit, not perky.
    cap_y = hy - int(hr * 1.2)
    for sgn, dx, dy, col in ((-1, -34, 18, VENOM), (-1, -20, -10, PLUM_BRUISE),
                             (0, 0, -34, GOLD), (1, 22, -8, VENOM),
                             (1, 36, 16, PLUM_BRUISE)):
        tip = (cx + dx * s, cap_y + dy * s)
        spire = [(cx - 8 * s, cap_y + 4 * s), (cx + 8 * s, cap_y + 4 * s), tip]
        pygame.draw.polygon(surf, col, spire)
        pygame.draw.polygon(surf, _shade(col, -55), spire, s)
        _bell(surf, tip[0], tip[1], 3 * s)


def _puppeteer_face(surf, cx, hy, hr, s):
    # Deep sunken eye sockets — dark hollows with a single venom pinprick glint.
    for sgn in (-1, 1):
        ex = cx + sgn * 8 * s
        pygame.draw.ellipse(surf, INK, (ex - 6 * s, hy - 6 * s, 12 * s, 11 * s))
        _glint(surf, ex - sgn * 2 * s, hy - 2 * s, 2 * s)
        # Sharp arched-up cruel brow over each socket.
        pygame.draw.line(surf, PLUM_DARK, (ex - 6 * s, hy - 4 * s),
                         (ex + sgn * 7 * s, hy - 9 * s), 3 * s)
    # Small mean red nose.
    pygame.draw.circle(surf, BLOOD, (cx, hy + 5 * s), 3 * s)
    pygame.draw.circle(surf, _shade(BLOOD, 70), (cx - s, hy + 4 * s), s)
    # A long stitched ear-to-ear grin — a thin gleeful slash with cross-stitches.
    gy = hy + 14 * s
    pygame.draw.arc(surf, BLOOD_DARK, (cx - 14 * s, gy - 6 * s, 28 * s, 16 * s),
                    math.pi * 0.05, math.pi * 0.95, 3 * s)
    for k in range(-3, 4):
        sx = cx + k * 4 * s
        sy = gy + int(abs(k) * 0.6 * s)
        pygame.draw.line(surf, INK, (sx, sy - 4 * s), (sx, sy + 4 * s), s)


# ─────────────────────────────────────────────────────────────────────────────
# BOSS 3 — THE BLOATED GLUTTON KING
# Thesis: a gross, near-SPHERICAL bouncing fat-jester — ONE enormous belly orb
# IS the whole body, with tiny vestigial limbs, a squashed wide grin splitting
# the lower sphere, and a sagging belt of bells girdling the gut. Construction:
# a single dominant circle (its OWN orb builder), bilateral bell-fringe belt,
# stubby radial nub-limbs, a tiny crown perched on top. Round bottom-heavy
# silhouette — nothing like the other four.
# ─────────────────────────────────────────────────────────────────────────────

def build_glutton(surf, cx, feet_y, K):
    s = K
    R = 74 * s                     # the colossal belly radius (the whole body)
    bcy = feet_y - R - 4 * s       # belly centre

    # Tiny stubby legs poking out the bottom of the gut.
    for sgn in (-1, 1):
        lx = cx + sgn * 22 * s
        pygame.draw.line(surf, _shade(VENOM, -50), (lx, bcy + R - 10 * s),
                         (lx + sgn * 4 * s, feet_y - 6 * s), 11 * s)
        pygame.draw.line(surf, VENOM, (lx, bcy + R - 10 * s),
                         (lx + sgn * 4 * s, feet_y - 6 * s), 8 * s)
        # Squashed bell-toe bootie.
        boot = pygame.Rect(0, 0, 22 * s, 11 * s)
        boot.center = (lx + sgn * 8 * s, feet_y - 3 * s)
        pygame.draw.ellipse(surf, PLUM_DARK, boot)
        pygame.draw.ellipse(surf, PLUM_DEEP, boot.inflate(-3 * s, -2 * s))
        _bell(surf, boot.centerx + sgn * 11 * s, boot.centery - 2 * s, 3 * s)

    # THE GUT — a single huge plum sphere, harlequin-quartered, with stretched
    # diamond panels that read as a too-tight costume bursting at the seams.
    pygame.draw.circle(surf, PLUM_DARK, (cx, bcy), R + 2 * s)
    pygame.draw.circle(surf, PLUM_DEEP, (cx, bcy), R)
    # Quartered colour split painted as clipped wedges.
    quad = pygame.Surface((R * 2 + 4 * s, R * 2 + 4 * s), pygame.SRCALPHA)
    qc = (R + 2 * s, R + 2 * s)
    pygame.draw.polygon(quad, (*VENOM_DEEP, 255),
                        [qc, (qc[0] + R + 2 * s, qc[1] - R - 2 * s),
                         (qc[0] + R + 2 * s, qc[1])])
    pygame.draw.polygon(quad, (*VENOM_DEEP, 255),
                        [qc, (qc[0] - R - 2 * s, qc[1] + R + 2 * s),
                         (qc[0] - R - 2 * s, qc[1])])
    mask = pygame.Surface(quad.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), qc, R)
    quad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(quad, (cx - R - 2 * s, bcy - R - 2 * s))
    # Top-left sheen on the bulging gut.
    sheen = pygame.Surface((R, R), pygame.SRCALPHA)
    pygame.draw.ellipse(sheen, (255, 255, 255, 60), sheen.get_rect())
    surf.blit(sheen, (cx - R + 6 * s, bcy - R + 6 * s))
    # Stretched gold diamond buttons straining in a row down the centre.
    for i in range(4):
        dy = bcy - 30 * s + i * 22 * s
        dw = 7 * s
        pygame.draw.polygon(surf, GOLD,
                            [(cx, dy - dw), (cx + dw, dy), (cx, dy + dw), (cx - dw, dy)])
        pygame.draw.polygon(surf, GOLD_DARK,
                            [(cx, dy - dw), (cx + dw, dy), (cx, dy + dw), (cx - dw, dy)], s)
    # Straining seam-stitch lines arcing over the belly (about to burst).
    for off in (-1, 1):
        pygame.draw.arc(surf, BONE,
                        (cx - R + 10 * s, bcy - R // 2 + off * 6 * s,
                         R * 2 - 20 * s, R), math.pi * 0.15, math.pi * 0.85, s)

    # The SAGGING BELT OF BELLS girdling the widest part of the gut.
    belt_y = bcy + 8 * s
    pygame.draw.arc(surf, GOLD_DARK, (cx - R, belt_y - 8 * s, R * 2, 30 * s),
                    math.pi * 0.08, math.pi * 0.92, 6 * s)
    pygame.draw.arc(surf, GOLD, (cx - R, belt_y - 8 * s, R * 2, 30 * s),
                    math.pi * 0.08, math.pi * 0.92, 3 * s)
    for i in range(7):
        t = i / 6
        bx = cx - R + 12 * s + (R * 2 - 24 * s) * t
        by = belt_y + int(math.sin(t * math.pi) * 14 * s) + 8 * s
        _bell(surf, bx, by, 4 * s)

    # Tiny vestigial arms — one tucked greedily on the gut, one raised with a
    # gnawed bone (the GLUTTON gag). Stubby, dwarfed by the belly.
    # Left tiny arm resting on belly.
    pygame.draw.line(surf, _shade(PLUM_BRUISE, -50),
                     (cx - R + 14 * s, bcy - 8 * s), (cx - R + 30 * s, bcy + 6 * s), 9 * s)
    pygame.draw.line(surf, PLUM_BRUISE,
                     (cx - R + 14 * s, bcy - 8 * s), (cx - R + 30 * s, bcy + 6 * s), 6 * s)
    pygame.draw.circle(surf, GOLD, (cx - R + 30 * s, bcy + 6 * s), 6 * s)
    # Right tiny arm raised waving a gnawed drumstick bone.
    rh = (cx + R - 2 * s, bcy - 30 * s)
    pygame.draw.line(surf, _shade(PLUM_BRUISE, -50),
                     (cx + R - 16 * s, bcy - 6 * s), rh, 9 * s)
    pygame.draw.line(surf, PLUM_BRUISE, (cx + R - 16 * s, bcy - 6 * s), rh, 6 * s)
    pygame.draw.circle(surf, GOLD, rh, 6 * s)
    # Gnawed bone in the fist.
    pygame.draw.line(surf, BONE, (rh[0] - 2 * s, rh[1] + 2 * s),
                     (rh[0] + 12 * s, rh[1] - 12 * s), 4 * s)
    pygame.draw.circle(surf, BONE, (rh[0] + 12 * s, rh[1] - 12 * s), 4 * s)
    pygame.draw.circle(surf, BONE, (rh[0] - 2 * s, rh[1] + 2 * s), 3 * s)

    # Small head squashed down INTO the gut (chinless, gluttonous), with a tiny
    # too-small crown jester-cap perched comically on top.
    hr = 22 * s
    hy = bcy - R - hr + 14 * s
    pygame.draw.circle(surf, SKIN_SHADE, (cx, hy), hr + s)
    pygame.draw.circle(surf, SKIN, (cx, hy), hr)
    # Multiple chins merging into the gut.
    for c in range(2):
        pygame.draw.arc(surf, SKIN_SHADE,
                        (cx - hr + 4 * s, hy + 6 * s + c * 6 * s, hr * 2 - 8 * s, 16 * s),
                        math.pi * 0.1, math.pi * 0.9, 2 * s)
    _glutton_face(surf, cx, hy, hr, s)
    # Comically TINY three-point cap perched on the crown.
    cap_y = hy - hr + 2 * s
    for sgn, dx, dy, col in ((-1, -14, -16, VENOM), (0, 0, -22, GOLD),
                             (1, 14, -16, PLUM_BRUISE)):
        tip = (cx + dx * s, cap_y + dy * s)
        pygame.draw.polygon(surf, col,
                            [(cx - 9 * s, cap_y + 2 * s), (cx + 9 * s, cap_y + 2 * s), tip])
        pygame.draw.polygon(surf, _shade(col, -55),
                            [(cx - 9 * s, cap_y + 2 * s), (cx + 9 * s, cap_y + 2 * s), tip], s)
        _bell(surf, tip[0], tip[1], 2 * s)


def _glutton_face(surf, cx, hy, hr, s):
    # Greedy half-closed gleeful eyes — fat happy squints with a hungry glint.
    for sgn in (-1, 1):
        ex = cx + sgn * 9 * s
        pygame.draw.ellipse(surf, WHITE, (ex - 6 * s, hy - 4 * s, 12 * s, 9 * s))
        pygame.draw.circle(surf, INK, (ex + sgn * 2 * s, hy + s), 3 * s)
        _glint(surf, ex + sgn * 1 * s, hy - s, 2 * s)
        # Heavy fatty upper lid drooping over (greedy squint).
        pygame.draw.arc(surf, SKIN_SHADE, (ex - 7 * s, hy - 7 * s, 14 * s, 12 * s),
                        math.pi * 0.05, math.pi * 0.95, 3 * s)
    pygame.draw.circle(surf, BLOOD, (cx, hy + 5 * s), 5 * s)
    pygame.draw.circle(surf, _shade(BLOOD, 80), (cx - 2 * s, hy + 3 * s), 2 * s)
    # A HUGE wide-open gluttonous grin splitting the lower face — tongue lolling.
    mouth = pygame.Rect(cx - 16 * s, hy + 10 * s, 32 * s, 18 * s)
    pygame.draw.ellipse(surf, BLOOD_DARK, mouth)
    pygame.draw.ellipse(surf, INK, mouth, 2 * s)
    # Lolling tongue.
    pygame.draw.ellipse(surf, BLOOD, (cx - 6 * s, hy + 18 * s, 16 * s, 12 * s))
    pygame.draw.line(surf, BLOOD_DARK, (cx + 2 * s, hy + 19 * s),
                     (cx + 2 * s, hy + 28 * s), s)
    # Upper teeth row + one fat fang.
    pygame.draw.polygon(surf, BONE,
                        [(cx - 14 * s, hy + 11 * s), (cx + 14 * s, hy + 11 * s),
                         (cx + 12 * s, hy + 15 * s), (cx - 12 * s, hy + 15 * s)])
    pygame.draw.polygon(surf, BONE, [(cx - 9 * s, hy + 15 * s),
                                     (cx - 4 * s, hy + 15 * s),
                                     (cx - 6 * s, hy + 22 * s)])


# ─────────────────────────────────────────────────────────────────────────────
# BOSS 4 — THE SPIDER-FOOL (MANY-ARMED HARLEQUIN)
# Thesis: a demonic commedia HARLEQUIN with SIX arms fanned like a peacock /
# spider off a diamond-lattice segmented carapace torso, crowned by a sharp
# horned cap-mask. Construction: a radial multi-arm fan (its OWN radial-arm
# builder), a diamond-tiled insectile carapace, segmented sharp shape language.
# A STAR/BURST silhouette — radial, not the columnar/round/triangle others.
# ─────────────────────────────────────────────────────────────────────────────

def build_spider(surf, cx, feet_y, K):
    s = K
    core_y = feet_y - 96 * s        # the carapace centre
    # Two sharp insect legs planted, but the silhouette star is the ARMS.
    for sgn in (-1, 1):
        hip = (cx + sgn * 12 * s, core_y + 30 * s)
        knee = (cx + sgn * 30 * s, feet_y - 40 * s)
        ankle = (cx + sgn * 18 * s, feet_y - 6 * s)
        for a, b in ((hip, knee), (knee, ankle)):
            pygame.draw.line(surf, PLUM_DARK, a, b, 8 * s)
            pygame.draw.line(surf, PLUM_DEEP, a, b, 5 * s)
        pygame.draw.circle(surf, VENOM_DEEP, knee, 4 * s)
        # Sharp pointed harlequin foot.
        toe = (ankle[0] + sgn * 14 * s, ankle[1] - 6 * s)
        pygame.draw.polygon(surf, PLUM_DEEP,
                            [(ankle[0], ankle[1] + 4 * s),
                             (ankle[0], ankle[1] - 4 * s), toe])
        _bell(surf, toe[0], toe[1], 2 * s)

    # SIX radial arms fanned out in a burst — three per side, each a segmented
    # spider limb ending in a clawed gold mitt. The fan IS the silhouette.
    arm_specs = [(-150, 78), (-118, 92), (-92, 70),
                 (-30, 78), (-62, 92), (-88, 70)]
    # angles measured in degrees; left set sweeps up-left, right mirrored.
    for i, (deg, length) in enumerate(arm_specs):
        sgn = -1 if i < 3 else 1
        base_deg = deg if sgn < 0 else (180 - deg)
        ang = math.radians(base_deg)
        sh = (cx + sgn * 6 * s, core_y - 10 * s + (i % 3) * 14 * s)
        elbow = (sh[0] + math.cos(ang) * length * 0.55 * s,
                 sh[1] - math.sin(ang) * length * 0.55 * s)
        hand = (sh[0] + math.cos(ang) * length * s,
                sh[1] - math.sin(ang) * length * s)
        col = VENOM if i % 2 else PLUM_BRUISE
        pygame.draw.line(surf, _shade(col, -55), sh, elbow, 6 * s)
        pygame.draw.line(surf, _shade(col, -55), elbow, hand, 5 * s)
        pygame.draw.line(surf, col, sh, elbow, 4 * s)
        pygame.draw.line(surf, col, elbow, hand, 3 * s)
        pygame.draw.circle(surf, VENOM_DEEP, (int(elbow[0]), int(elbow[1])), 3 * s)
        # Clawed gold mitt.
        pygame.draw.circle(surf, GOLD_DARK, (int(hand[0]), int(hand[1])), 5 * s)
        pygame.draw.circle(surf, GOLD, (int(hand[0]), int(hand[1])), 4 * s)
        for f in (-0.4, 0, 0.4):
            cx2 = hand[0] + math.cos(ang + f) * 8 * s
            cy2 = hand[1] - math.sin(ang + f) * 8 * s
            pygame.draw.line(surf, INK, (int(hand[0]), int(hand[1])),
                             (int(cx2), int(cy2)), 2 * s)

    # The DIAMOND-LATTICE carapace: a segmented angular torso plate built from a
    # tessellated harlequin diamond grid (its own tiling), reading insectile.
    cw, ch = 34 * s, 60 * s
    plate = [(cx, core_y - ch), (cx + cw, core_y - ch // 3),
             (cx + cw - 6 * s, core_y + ch // 2), (cx, core_y + ch // 2 + 8 * s),
             (cx - cw + 6 * s, core_y + ch // 2), (cx - cw, core_y - ch // 3)]
    pygame.draw.polygon(surf, PLUM_DARK, plate)
    # Tessellated diamonds clipped to the plate.
    tile = pygame.Surface((cw * 2 + 2, ch * 2 + 2), pygame.SRCALPHA)
    ox, oy = cw, ch
    d = 11 * s
    for row in range(-1, 7):
        for coli in range(-3, 4):
            dx = ox + coli * d + (d // 2 if row % 2 else 0)
            dy = oy + row * d - ch + ch // 3
            col = VENOM if (row + coli) % 2 else PLUM_BRUISE
            pygame.draw.polygon(tile, (*col, 255),
                                [(dx, dy - d // 2 + 1), (dx + d // 2 - 1, dy),
                                 (dx, dy + d // 2 - 1), (dx - d // 2 + 1, dy)])
    mask = pygame.Surface(tile.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255),
                        [(p[0] - cx + ox, p[1] - core_y + oy) for p in plate])
    tile.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(tile, (cx - ox, core_y - oy))
    pygame.draw.polygon(surf, PLUM_DARK, plate, 2 * s)
    # Segment ridge lines across the carapace (insect plates).
    for sy in range(-2, 3):
        ry = core_y + sy * 12 * s
        half = int(cw * (1 - abs(sy) * 0.12))
        pygame.draw.line(surf, GOLD_DARK, (cx - half, ry), (cx + half, ry), s)
    # A gold gorget collar at the throat.
    pygame.draw.arc(surf, GOLD, (cx - 20 * s, core_y - ch - 6 * s, 40 * s, 22 * s),
                    math.pi, math.tau, 5 * s)

    # HEAD — a sharp angular horned mask-head (diamond-shaped, not round).
    hr = 20 * s
    hy = core_y - ch - hr + 4 * s
    head = [(cx, hy - hr - 2 * s), (cx + hr, hy), (cx, hy + hr + 4 * s),
            (cx - hr, hy)]
    pygame.draw.polygon(surf, SKIN_SHADE, head)
    pygame.draw.polygon(surf, SKIN,
                        [(cx, hy - hr), (cx + hr - 2 * s, hy),
                         (cx, hy + hr + 2 * s), (cx - hr + 2 * s, hy)])
    _bruise(surf, cx, hy + 8 * s, 8 * s, 5 * s, 60)
    _spider_face(surf, cx, hy, hr, s)
    # Sharp horned cap-mask: two long swept-back horns + a central spike, belled.
    cap_y = hy - hr + 2 * s
    for sgn, dx, dy in ((-1, -28, -26), (0, 0, -40), (1, 28, -26)):
        tip = (cx + dx * s, cap_y + dy * s)
        horn = [(cx - 7 * s, cap_y), (cx + 7 * s, cap_y), tip]
        col = GOLD if dx == 0 else (VENOM if sgn < 0 else PLUM_BRUISE)
        pygame.draw.polygon(surf, col, horn)
        pygame.draw.polygon(surf, _shade(col, -60), horn, s)
        _bell(surf, tip[0], tip[1], 2 * s)


def _spider_face(surf, cx, hy, hr, s):
    # FOUR small spider eyes in two rows — venom glints in the dark, plus a
    # bigger pair for the read. Macro shape: a sharp dark brow chevron.
    pygame.draw.polygon(surf, PLUM_DARK,
                        [(cx - 12 * s, hy - 4 * s), (cx, hy - 8 * s),
                         (cx + 12 * s, hy - 4 * s), (cx, hy - 2 * s)])
    for sgn in (-1, 1):
        ex = cx + sgn * 7 * s
        pygame.draw.ellipse(surf, INK, (ex - 5 * s, hy - s, 10 * s, 8 * s))
        _glint(surf, ex, hy + 2 * s, 3 * s)
        # A smaller upper eye pair (the extra spider eyes).
        pygame.draw.circle(surf, INK, (cx + sgn * 4 * s, hy - 6 * s), 2 * s)
        pygame.draw.circle(surf, EYE_GLINT, (cx + sgn * 4 * s, hy - 7 * s), s)
    pygame.draw.circle(surf, BLOOD, (cx, hy + 6 * s), 3 * s)
    # A sharp toothy chevron grin (angular to match the diamond head).
    pygame.draw.polygon(surf, BLOOD_DARK,
                        [(cx - 12 * s, hy + 10 * s), (cx + 12 * s, hy + 10 * s),
                         (cx, hy + 18 * s)])
    pygame.draw.polygon(surf, BONE,
                        [(cx - 11 * s, hy + 10 * s), (cx + 11 * s, hy + 10 * s),
                         (cx, hy + 16 * s)])
    for tx in range(-3, 4):
        gx = cx + tx * 3 * s
        pygame.draw.line(surf, BLOOD_DARK, (gx, hy + 10 * s),
                         (cx, hy + 16 * s), s)


# ─────────────────────────────────────────────────────────────────────────────
# BOSS 5 — THE JANUS HERALD (TWO-FACED MARQUEE)
# Thesis: a grandiose theatrical herald SPLIT down the middle into comedy &
# tragedy halves, a billowing banner-cape SAIL ballooning behind, a single
# DOUBLE-faced head (one half a wide grin, the other a weeping snarl) held high
# on a flared heraldic mantle. Construction: a vertical mirror-split body with a
# MISMATCHED bilateral face (its own split-face builder) + a sweeping banner
# sail. An asymmetric split silhouette with a cape — unlike any other.
# ─────────────────────────────────────────────────────────────────────────────

def build_janus(surf, cx, feet_y, K):
    s = K
    hip_y = feet_y - 92 * s
    top_y = hip_y - 78 * s

    # The billowing BANNER-CAPE SAIL behind — a great curved flag ballooning to
    # one side, the marquee grandeur. Drawn FIRST so the body sits in front.
    sail = [(cx + 6 * s, top_y - 6 * s),
            (cx + 90 * s, top_y + 6 * s),
            (cx + 110 * s, hip_y - 10 * s),
            (cx + 96 * s, hip_y + 40 * s),
            (cx + 64 * s, hip_y + 50 * s),
            (cx + 30 * s, hip_y + 30 * s)]
    pygame.draw.polygon(surf, BLOOD_DARK, sail)
    pygame.draw.polygon(surf, BLOOD,
                        [(cx + 6 * s, top_y - 6 * s), (cx + 60 * s, top_y),
                         (cx + 70 * s, hip_y), (cx + 30 * s, hip_y + 30 * s)])
    pygame.draw.polygon(surf, PLUM_DARK, sail, 2 * s)
    # Gold tassel fringe along the sail's trailing (right) edge.
    for k in range(6):
        t = k / 5
        fx = int((110 - (110 - 64) * t) * s)
        fy = int((hip_y - 10 * s) + (hip_y + 50 * s - (hip_y - 10 * s)) * t)
        _bell(surf, cx + fx, fy, 2 * s)
    # A venom heraldic emblem (a jester-skull motif) on the banner.
    em = (cx + 56 * s, hip_y - 2 * s)
    pygame.draw.circle(surf, VENOM, em, 12 * s)
    pygame.draw.circle(surf, VENOM_DEEP, em, 12 * s, s)
    pygame.draw.circle(surf, INK, (em[0] - 4 * s, em[1] - 2 * s), 2 * s)
    pygame.draw.circle(surf, INK, (em[0] + 4 * s, em[1] - 2 * s), 2 * s)
    pygame.draw.arc(surf, INK, (em[0] - 6 * s, em[1] + 2 * s, 12 * s, 8 * s),
                    math.pi, math.tau, 2 * s)

    # The body: a vertical MIRROR-SPLIT robe — comedy (venom/gold, bright) on the
    # viewer-LEFT half, tragedy (deep plum/blood, dark) on the right half. Each
    # half is its OWN tall panel meeting at the centre seam.
    left_half = [(cx, hip_y + 14 * s), (cx, top_y),
                 (cx - 30 * s, top_y + 6 * s), (cx - 40 * s, hip_y + 14 * s)]
    right_half = [(cx, hip_y + 14 * s), (cx, top_y),
                  (cx + 30 * s, top_y + 6 * s), (cx + 40 * s, hip_y + 14 * s)]
    pygame.draw.polygon(surf, VENOM_DEEP, left_half)
    pygame.draw.polygon(surf, VENOM,
                        [(cx - 4 * s, top_y + 2 * s), (cx - 26 * s, top_y + 6 * s),
                         (cx - 32 * s, hip_y + 10 * s), (cx - 6 * s, hip_y + 12 * s)])
    pygame.draw.polygon(surf, PLUM_DARK, right_half)
    pygame.draw.polygon(surf, PLUM_DEEP,
                        [(cx + 4 * s, top_y + 2 * s), (cx + 26 * s, top_y + 6 * s),
                         (cx + 32 * s, hip_y + 10 * s), (cx + 6 * s, hip_y + 12 * s)])
    # Contrasting accents per half: gold dots on the bright half, bone teardrop
    # tears stitched down the dark half.
    for i in range(3):
        dy = top_y + 20 * s + i * 22 * s
        pygame.draw.circle(surf, GOLD, (cx - 18 * s, dy), 4 * s)
        pygame.draw.circle(surf, GOLD_DARK, (cx - 18 * s, dy), 4 * s, s)
        # tragedy tear.
        pygame.draw.polygon(surf, (170, 190, 210),
                            [(cx + 18 * s, dy - 4 * s), (cx + 22 * s, dy + 2 * s),
                             (cx + 14 * s, dy + 2 * s)])
    pygame.draw.line(surf, BONE, (cx, top_y), (cx, hip_y + 14 * s), 2 * s)
    pygame.draw.polygon(surf, INK, left_half, 2 * s)
    pygame.draw.polygon(surf, INK, right_half, 2 * s)

    # Legs — harlequin, each matching its half's mood.
    for sgn, col in ((-1, VENOM), (1, PLUM_BRUISE)):
        lx = cx + sgn * 18 * s
        pygame.draw.line(surf, _shade(col, -50), (lx, hip_y + 10 * s),
                         (lx + sgn * 4 * s, feet_y - 6 * s), 11 * s)
        pygame.draw.line(surf, col, (lx, hip_y + 10 * s),
                         (lx + sgn * 4 * s, feet_y - 6 * s), 8 * s)
        boot = pygame.Rect(0, 0, 22 * s, 11 * s)
        boot.center = (lx + sgn * 8 * s, feet_y - 3 * s)
        pygame.draw.ellipse(surf, PLUM_DARK, boot)
        pygame.draw.ellipse(surf, PLUM_DEEP, boot.inflate(-3 * s, -2 * s))
        _bell(surf, boot.centerx + sgn * 11 * s, boot.centery - 2 * s, 3 * s)

    # One arm raised high holding a herald's trumpet/sceptre flourish; the other
    # planted on the hip — theatrical proclamation.
    # Raised left arm.
    sh_l = (cx - 24 * s, top_y + 12 * s)
    hand_l = (cx - 58 * s, top_y - 34 * s)
    pygame.draw.line(surf, VENOM_DEEP, sh_l, hand_l, 9 * s)
    pygame.draw.line(surf, VENOM, sh_l, hand_l, 6 * s)
    pygame.draw.circle(surf, GOLD, hand_l, 6 * s)
    # A flared herald trumpet held aloft.
    pygame.draw.line(surf, GOLD, hand_l, (hand_l[0] - 4 * s, hand_l[1] - 26 * s), 4 * s)
    pygame.draw.polygon(surf, GOLD,
                        [(hand_l[0] - 10 * s, hand_l[1] - 38 * s),
                         (hand_l[0] + 2 * s, hand_l[1] - 38 * s),
                         (hand_l[0] - 4 * s, hand_l[1] - 26 * s)])
    pygame.draw.polygon(surf, GOLD_DARK,
                        [(hand_l[0] - 10 * s, hand_l[1] - 38 * s),
                         (hand_l[0] + 2 * s, hand_l[1] - 38 * s),
                         (hand_l[0] - 4 * s, hand_l[1] - 26 * s)], s)
    # Right arm planted on hip.
    sh_r = (cx + 24 * s, top_y + 12 * s)
    hand_r = (cx + 38 * s, hip_y - 6 * s)
    pygame.draw.line(surf, PLUM_DARK, sh_r, (cx + 40 * s, top_y + 36 * s), 9 * s)
    pygame.draw.line(surf, PLUM_DEEP, sh_r, (cx + 40 * s, top_y + 36 * s), 6 * s)
    pygame.draw.line(surf, PLUM_DARK, (cx + 40 * s, top_y + 36 * s), hand_r, 8 * s)
    pygame.draw.line(surf, PLUM_DEEP, (cx + 40 * s, top_y + 36 * s), hand_r, 5 * s)
    pygame.draw.circle(surf, (240, 240, 244), hand_r, 6 * s)

    # A grand FLARED heraldic mantle/collar — a wide split wing-collar framing
    # the double face, mismatched per side.
    neck_y = top_y + 2 * s
    for sgn, col in ((-1, GOLD), (1, PLUM_DEEP)):
        wing = [(cx, neck_y - 6 * s), (cx + sgn * 34 * s, neck_y - 18 * s),
                (cx + sgn * 30 * s, neck_y + 10 * s), (cx + sgn * 6 * s, neck_y + 8 * s)]
        pygame.draw.polygon(surf, col, wing)
        pygame.draw.polygon(surf, _shade(col, -60), wing, 2 * s)
        _bell(surf, cx + sgn * 32 * s, neck_y - 16 * s, 3 * s)

    # HEAD — ONE head, the DOUBLE FACE: split vertically, comedy half + tragedy
    # half. The macro split + one bright glint per half holds at small size.
    hr = 23 * s
    hy = neck_y - hr - 4 * s
    pygame.draw.circle(surf, SKIN_SHADE, (cx, hy), hr + s)
    # Left (comedy) half painted on warm-lit skin; right (tragedy) half greyed.
    pygame.draw.polygon(surf, SKIN,
                        [(cx, hy - hr), (cx, hy + hr),
                         (cx - hr, hy + hr), (cx - hr, hy - hr)],)
    pygame.draw.circle(surf, SKIN, (cx, hy), hr)
    grey = pygame.Surface((hr * 2 + 2, hr * 2 + 2), pygame.SRCALPHA)
    pygame.draw.polygon(grey, (60, 64, 78, 120),
                        [(hr, 0), (hr * 2, 0), (hr * 2, hr * 2), (hr, hr * 2)])
    cmask = pygame.Surface(grey.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(cmask, (255, 255, 255, 255), (hr, hr), hr)
    grey.blit(cmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(grey, (cx - hr, hy - hr))
    pygame.draw.line(surf, INK, (cx, hy - hr), (cx, hy + hr), 2 * s)
    pygame.draw.circle(surf, SKIN_SHADE, (cx, hy), hr, 2 * s)
    _janus_face(surf, cx, hy, hr, s)
    # Split crown: a tall comedy spike on the bright side, a drooping tragedy
    # spire on the dark side, asymmetric.
    cap_y = hy - hr + 2 * s
    # Comedy spike (left) — tall, perky.
    lt = (cx - 26 * s, cap_y - 36 * s)
    pygame.draw.polygon(surf, VENOM, [(cx - 12 * s, cap_y), (cx - s, cap_y - 4 * s), lt])
    pygame.draw.polygon(surf, VENOM_DEEP, [(cx - 12 * s, cap_y), (cx - s, cap_y - 4 * s), lt], s)
    _bell(surf, lt[0], lt[1], 3 * s)
    # Tragedy spire (right) — drooping, heavy.
    rt = (cx + 30 * s, cap_y - 6 * s)
    pygame.draw.polygon(surf, PLUM_DEEP, [(cx + s, cap_y - 4 * s), (cx + 12 * s, cap_y), rt])
    pygame.draw.polygon(surf, PLUM_DARK, [(cx + s, cap_y - 4 * s), (cx + 12 * s, cap_y), rt], s)
    _bell(surf, rt[0], rt[1], 3 * s)
    # A central gold spike between them.
    ct = (cx + 2 * s, cap_y - 30 * s)
    pygame.draw.polygon(surf, GOLD, [(cx - 6 * s, cap_y - 2 * s), (cx + 8 * s, cap_y - 2 * s), ct])
    _bell(surf, ct[0], ct[1], 2 * s)


def _janus_face(surf, cx, hy, hr, s):
    # LEFT (comedy) half — bright wide grin, raised cheery brow, bright eye.
    pygame.draw.line(surf, PLUM_DARK, (cx - 16 * s, hy - 6 * s),
                     (cx - 4 * s, hy - 9 * s), 3 * s)  # raised brow
    pygame.draw.ellipse(surf, WHITE, (cx - 14 * s, hy - 4 * s, 10 * s, 9 * s))
    pygame.draw.circle(surf, INK, (cx - 9 * s, hy + s), 3 * s)
    _glint(surf, cx - 10 * s, hy - s, 2 * s)
    # comedy grin: big upturned half.
    pygame.draw.arc(surf, BLOOD, (cx - 18 * s, hy + 6 * s, 22 * s, 18 * s),
                    math.pi * 0.5, math.pi * 1.0, 3 * s)
    pygame.draw.polygon(surf, BONE,
                        [(cx - 14 * s, hy + 12 * s), (cx - s, hy + 13 * s),
                         (cx - 2 * s, hy + 16 * s), (cx - 13 * s, hy + 16 * s)])

    # RIGHT (tragedy) half — downturned snarl, furrowed-down brow, weeping eye.
    pygame.draw.line(surf, INK, (cx + 4 * s, hy - 9 * s),
                     (cx + 16 * s, hy - 4 * s), 3 * s)  # angry/sad down brow
    pygame.draw.ellipse(surf, (220, 224, 230), (cx + 4 * s, hy - 4 * s, 10 * s, 9 * s))
    pygame.draw.circle(surf, INK, (cx + 9 * s, hy + 2 * s), 3 * s)
    _glint(surf, cx + 8 * s, hy, 2 * s)
    # A blue tear running down the tragedy cheek.
    pygame.draw.polygon(surf, (150, 180, 210),
                        [(cx + 9 * s, hy + 6 * s), (cx + 11 * s, hy + 14 * s),
                         (cx + 7 * s, hy + 14 * s)])
    # tragedy snarl: downturned half with a fang.
    pygame.draw.arc(surf, BLOOD_DARK, (cx + s, hy + 10 * s, 22 * s, 20 * s),
                    math.pi * 1.0, math.pi * 1.5, 3 * s)
    pygame.draw.polygon(surf, BONE, [(cx + 4 * s, hy + 12 * s),
                                     (cx + 8 * s, hy + 12 * s),
                                     (cx + 6 * s, hy + 18 * s)])

    # A shared blood nose straddling the seam.
    pygame.draw.circle(surf, BLOOD, (cx, hy + 6 * s), 4 * s)
    pygame.draw.circle(surf, _shade(BLOOD, 80), (cx - s, hy + 4 * s), 2 * s)


# ─────────────────────────────────────────────────────────────────────────────
# Cell 0 — the FAITHFUL CURRENT clown, reproduced verbatim via the shipped
# builder (NO die, NO staff).
# ─────────────────────────────────────────────────────────────────────────────

def build_current(surf, cx, feet_y):
    spec = dict(JESTERS[-1][1])      # "Plum & Lime — FINAL"
    spec.pop("no_shadow", None)
    hand_up = (cx - 60, feet_y - 156)   # the true up-left point pose
    build_jester(surf, cx, feet_y, hand_up, **spec)


# ─────────────────────────────────────────────────────────────────────────────
# Sheet composition — six cells on ONE shared ground line.
# ─────────────────────────────────────────────────────────────────────────────

BOSSES = [
    ("THE RINGMASTER COLOSSUS", build_colossus,
     "baroque circus-ringmaster - wide TRIANGLE, plumed mitre, BEHOLD flare"),
    ("THE PUPPETEER ABOVE", build_puppeteer,
     "gaunt marionette-master - TALL stilt legs, drooping spires, strings"),
    ("THE BLOATED GLUTTON KING", build_glutton,
     "spherical fat-jester - ONE belly ORB, bell-belt, gnawed bone"),
    ("THE SPIDER-FOOL", build_spider,
     "six-armed harlequin demon - radial BURST, diamond carapace, horns"),
    ("THE JANUS HERALD", build_janus,
     "two-faced marquee herald - SPLIT body, banner sail, double face"),
]


def _wrap(text, font, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if font.size(trial)[0] <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def render_cell(idx, builder, K, current=False):
    """Each cell is drawn at native K-scale onto its OWN surface, then blit 1:1
    (no smoothscale upscale) so faces stay crisp. The shared ground line sits at
    a fixed fraction so all six align across the sheet."""
    cw, ch = 300, 470
    surf = pygame.Surface((cw, ch))
    _grad_v(surf, (0, 0, cw, ch), BG_TOP, BG_BOT)
    # Shared ground band.
    g_y = ch - 40
    _grad_v(surf, (0, g_y, cw, ch - g_y), GROUND_LIT, GROUND_COL)
    pygame.draw.line(surf, _shade(GROUND_LIT, 30), (0, g_y), (cw, g_y), 2)
    # Soft cast shadow under the figure.
    sh = pygame.Surface((140, 26), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (10, 8, 16, 120), sh.get_rect())
    surf.blit(sh, (cw // 2 - 70, g_y - 12))

    feet_y = g_y - 2
    cx = cw // 2
    if current:
        build_current(surf, cx, feet_y)
    else:
        builder(surf, cx, feet_y, K)
    return surf


def main():
    pygame.init()
    pygame.font.init()
    pygame.display.set_mode((360, 640))

    # Cell 0 renders at the shipped builder's native scale (~feet-to-cap ~200px);
    # the five bosses render LARGER via K so the size jump reads on one ground
    # line. K=2 gives crisp native geometry at roughly 1.4-1.6x the original.
    K = 2

    cols, rows = 3, 2
    cw, ch = 300, 470
    PAD = 40
    GAP = 18
    CAP_H = 116

    f_title = pygame.font.SysFont(None, 48, bold=True)
    f_sub = pygame.font.SysFont(None, 28, bold=True)
    f_cap = pygame.font.SysFont(None, 30, bold=True)
    f_desc = pygame.font.SysFont(None, 26, bold=True)

    canvas_w = PAD * 2 + cols * cw + (cols - 1) * GAP

    # Title + sub wrapped to the canvas width so nothing clips/overflows.
    title_lines = _wrap("EVOLVED WARREN CLOWN - boss escalation (redux r1)",
                        f_title, canvas_w - PAD * 2)
    sub_lines = _wrap(
        "Cell 0 = the faithful CURRENT Plum & Lime jester (clown-only). "
        "Cells 1-5 = five GROUND-UP boss escalations - bigger, meaner, "
        "funnier, grandiose - in the soured/bruised evolved lineage palette. "
        "Five distinct silhouettes: triangle / column / orb / radial burst / "
        "split-with-sail.", f_sub, canvas_w - PAD * 2)
    TITLE_H = len(title_lines) * (f_title.get_height() + 2) + 10 \
        + len(sub_lines) * 26 + 14

    canvas_h = PAD * 2 + TITLE_H + rows * (ch + CAP_H) + (rows - 1) * GAP
    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((30, 28, 38))

    yy = PAD - 2
    for line in title_lines:
        canvas.blit(f_title.render(line, True, (236, 224, 196)), (PAD, yy))
        yy += f_title.get_height() + 2
    yy += 8
    for line in sub_lines:
        canvas.blit(f_sub.render(line, True, (188, 192, 204)), (PAD, yy))
        yy += 26

    cells = []
    cells.append(("0. ORIGINAL (current)", render_cell(0, None, K, current=True),
                  "Plum & Lime FINAL - chunky chibi jester, 4-point belled cap, "
                  "gold ruff, quartered body, harlequin legs, grin+fang"))
    for i, (name, builder, desc) in enumerate(BOSSES, start=1):
        cells.append((f"{i}. {name}", render_cell(i, builder, K), desc))

    y0 = PAD + TITLE_H
    for i, (name, cell, desc) in enumerate(cells):
        r, c = divmod(i, cols)
        x = PAD + c * (cw + GAP)
        y = y0 + r * (ch + CAP_H + GAP)
        pygame.draw.rect(canvas, (66, 72, 92),
                         pygame.Rect(x - 1, y - 1, cw + 2, ch + 2), 1)
        canvas.blit(cell, (x, y))
        cy = y + ch + 6
        for line in _wrap(name, f_cap, cw - 6):
            cap = f_cap.render(line, True, (234, 224, 168))
            canvas.blit(cap, (x + (cw - cap.get_width()) // 2, cy))
            cy += f_cap.get_height()
        cy += 4
        for line in _wrap(desc, f_desc, cw - 8):
            ds = f_desc.render(line, True, (186, 192, 204))
            canvas.blit(ds, (x + (cw - ds.get_width()) // 2, cy))
            cy += 22

    out_dir = os.path.join("docs", "evolved_clown")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "redux_round_1.png")
    pygame.image.save(canvas, out_path)
    print(f"saved {out_path}  ({canvas_w}x{canvas_h})")


if __name__ == "__main__":
    main()
