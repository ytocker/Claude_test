"""Look-dev: the EVOLVED (late-game, boss-tier) Plum & Lime warren clown.

The early-game warren clown (`JESTERS[-1]` in render_jester_variants — plum
costume, lime trim, gold ruff, four-point belled cap, happy-but-mean grin) is
LOCKED. This sheet explores a LATE-game evolution of the SAME character that
turns up near the finish line: physically larger, meaner, nastier — a boss
escalation, not a new IP. The plum/lime/gold family is pushed sinister (bruised
deep plum, sickly venom-lime, tarnished desaturated gold, blood/bruise accents)
and each of the five concepts gets its OWN menacing silhouette, cap
architecture, costume cut, ruff shape, face menace and looming stance.

Reference shape-language (web): Harlequin's literal demonic ancestry —
Hellequin / Alichino, the Dante's-Inferno demon that drove souls to Hell — so a
"darker, meaner" Plum & Lime is a return to the character's own roots, not an
invented monster. Menace cues pulled from evil-jester / carrion-clown / chasm-
demon design: hunched and elongated vs. hulking and top-heavy, oversized clawed
hands, jagged/horned cap silhouettes, dead pinprick or sunken eyes, exposed
fangs, tattered dagged hems, and bells that read as a threat rather than play.

Clown-ONLY (no staff — that is a separate later cycle). Cell 0 is the CURRENT
clown for direct comparison; cells 1-5 are the five evolved concepts, all drawn
on ONE matched ground line and at a clearly bigger scale so the size jump reads
at a glance. Supersampled 2x then smoothscaled for crisp edges.

    PYTHONPATH=. SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        python tools/render_evolved_clown.py
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.config import W, H
from tools.render_clown_dice import _shade, _poly, RIM
from tools.render_jester_variants import (
    build_jester, cap_four_point, _bell,
)


# ── the evolved Plum & Lime palette family ───────────────────────────────────
# The original hero spec (kept verbatim for the ORIGINAL reference cell).
ORIG = dict(
    dark=(96, 44, 150), light=(132, 218, 116), gold=(250, 205, 72),
    cap_fn=cap_four_point, motif="quartered", collar="scalloped",
    variant="browcock", collar_in_gold=True,
)

# The SAME three hues pushed sinister: the plum bruised down toward a deep
# blackened violet, the lime soured into a sickly venom green-yellow, the gold
# tarnished + desaturated toward dirty brass. These anchor every concept so the
# evolved figures all read as ONE darker grown-up of the hero, never a recolour
# grab-bag. Per-concept accents (blood, bruise, bone) layer on top.
E_PLUM = (58, 24, 92)            # bruised blackened violet (was 96,44,150)
E_PLUM_DK = (34, 14, 56)         # deepest plum, near-black core
E_LIME = (150, 196, 56)          # soured venom lime (was 132,218,116)
E_LIME_DK = (86, 120, 30)
E_GOLD = (182, 150, 64)          # tarnished dirty brass (was 250,205,72)
E_GOLD_DK = (120, 96, 36)
BLOOD = (150, 26, 36)            # blood/wound accent
BRUISE = (84, 40, 120)           # bruise-violet accent
BONE = (224, 214, 188)           # tarnished bone/ivory for fangs + claws
SKIN_PALE = (214, 198, 196)      # sickly ashen greasepaint skin (was 255,209,169)
DEAD_EYE = (196, 30, 44)         # the marotte's blood-pinprick dead eye
SICK_EYE = (196, 224, 96)        # sickly luminous venom-yellow eye


# ── shared evolved-menace primitives ─────────────────────────────────────────
# These build BIGGER, nastier figures from scratch (the hero `build_jester` is
# tuned for the small happy presenter). Each concept composes them into its own
# silhouette so no two share a body.

def _claw_hand(surf, wrist, reach, w, glove, *, fingers=4, spread=0.9,
               curl=0.5, side=1):
    """An oversized GLOVED claw — a heavy palm knuckle + long tapering talon
    digits that hook inward. The hero's round mitt grown into a grasping hand:
    the single loudest "this clown is now a predator" cue. `side` aims the
    splay (negative = fingers fan left), `curl` hooks the talon tips."""
    wx, wy = wrist
    pygame.draw.circle(surf, _shade(glove, -60), (wx, wy), w + 2)
    pygame.draw.circle(surf, glove, (wx, wy), w)
    pygame.draw.circle(surf, RIM, (wx - 2, wy - 2), max(1, w // 3))
    base_a = math.radians(70)
    for i in range(fingers):
        t = i / max(1, fingers - 1) - 0.5
        a = math.pi * 0.5 + side * t * spread + math.radians(28)
        # Three-segment talon hooking toward the tip.
        seg = reach / 3.0
        x0, y0 = wx + math.cos(a) * w, wy + math.sin(a) * w
        a2 = a + side * curl * 0.6
        x1 = x0 + math.cos(a2) * seg
        y1 = y0 + math.sin(a2) * seg
        a3 = a2 + side * curl
        x2 = x1 + math.cos(a3) * seg
        y2 = y1 + math.sin(a3) * seg
        fw = max(2, w // 2)
        pygame.draw.line(surf, _shade(glove, -60), (x0, y0), (x1, y1), fw + 2)
        pygame.draw.line(surf, glove, (x0, y0), (x1, y1), fw)
        pygame.draw.line(surf, _shade(glove, -60), (x1, y1), (x2, y2), fw)
        pygame.draw.line(surf, glove, (x1, y1), (x2, y2), max(1, fw - 1))
        # Tarnished-bone talon claw at the very tip.
        ax = x2 + math.cos(a3) * seg * 0.5
        ay = y2 + math.sin(a3) * seg * 0.5
        nail = [(x2 + math.cos(a3 + 1.6) * fw, y2 + math.sin(a3 + 1.6) * fw),
                (x2 + math.cos(a3 - 1.6) * fw, y2 + math.sin(a3 - 1.6) * fw),
                (ax, ay)]
        pygame.draw.polygon(surf, BONE, [(int(p[0]), int(p[1])) for p in nail])
        pygame.draw.polygon(surf, _shade(BONE, -55),
                            [(int(p[0]), int(p[1])) for p in nail], 1)
        _ = base_a


def _tarnished_bell(surf, x, y, r=5):
    """A dull, cracked version of the hero's lit gold bell — tarnished brass
    with a dark crack so even the jingles read sinister."""
    pygame.draw.circle(surf, E_GOLD_DK, (x, y), r + 1)
    pygame.draw.circle(surf, E_GOLD, (x, y), r)
    pygame.draw.circle(surf, _shade(E_GOLD, 60), (x - 1, y - 1), max(1, r // 3))
    pygame.draw.line(surf, E_GOLD_DK, (x, y - r), (x - 1, y + r), 1)


def _dagged_hem(surf, cx, y, half_w, teeth, col, *, drop=14):
    """A tattered DAGGED hem — a row of long jagged points hanging off the
    tunic bottom (the carrion/demon-rag silhouette), each tipped with a dull
    bell. Replaces the hero's neat scalloped circle hem."""
    n = teeth
    for i in range(n):
        t = i / (n - 1)
        x = cx - half_w + 2 * half_w * t
        nx = cx - half_w + 2 * half_w * (t + 1.0 / (n - 1)) if i < n - 1 else x
        tip = ((x + nx) / 2, y + drop + (4 if i % 2 else 0))
        col2 = col if i % 2 == 0 else _shade(col, -28)
        pygame.draw.polygon(surf, col2,
                            [(int(x), int(y)), (int(nx), int(y)),
                             (int(tip[0]), int(tip[1]))])
        pygame.draw.polygon(surf, _shade(col2, -55),
                            [(int(x), int(y)), (int(nx), int(y)),
                             (int(tip[0]), int(tip[1]))], 1)
        _tarnished_bell(surf, int(tip[0]), int(tip[1]) + 2, r=3)


def _harlequin_torso(surf, cx, top_y, bot_y, half_top, half_bot, dark, light,
                     *, lean=0, diamonds=True):
    """A tapering diamond-patched torso (the commedia harlequin's true lozenge
    motif, evolved bruised). `lean` shears the top toward the looming side."""
    quad = [(cx - half_bot, bot_y), (cx + half_bot, bot_y),
            (cx + half_top + lean, top_y), (cx - half_top + lean, top_y)]
    pygame.draw.polygon(surf, dark, quad)
    pygame.draw.polygon(surf, _shade(dark, -60), quad, 2)
    if diamonds:
        # A staggered lozenge field clipped to the torso, alternating bruised
        # plum / venom lime — the harlequin patchwork as a sickly bruise grid.
        prev = surf.get_clip()
        minx = min(p[0] for p in quad)
        maxx = max(p[0] for p in quad)
        surf.set_clip(pygame.Rect(int(minx), int(top_y),
                                  int(maxx - minx) + 1,
                                  int(bot_y - top_y) + 1).clip(prev))
        d = 18
        rows = int((bot_y - top_y) / d) + 2
        cols = int((2 * half_bot) / d) + 3
        for r in range(rows):
            for c in range(cols):
                offs = (d // 2) if r % 2 else 0
                px = cx - half_bot + c * d - d + offs
                py = top_y + r * d
                if (r + c) % 2 == 0:
                    continue
                lo = [(px, py - d // 2), (px + d // 2, py),
                      (px, py + d // 2), (px - d // 2, py)]
                pygame.draw.polygon(surf, light, lo)
                pygame.draw.polygon(surf, _shade(light, -45), lo, 1)
        surf.set_clip(prev)
    # A lit left rim + a bruise smear down the right so the barrel reads round.
    pygame.draw.line(surf, _shade(dark, 50),
                     (cx - half_top + lean + 2, top_y + 3),
                     (cx - half_bot + 2, bot_y - 3), 3)
    smear = pygame.Surface((int(half_bot), int(bot_y - top_y)), pygame.SRCALPHA)
    pygame.draw.ellipse(smear, (*BRUISE, 70), smear.get_rect())
    surf.blit(smear, (int(cx + half_bot * 0.1), int(top_y + 4)))


def _evolved_head(surf, cx, cy, hr, *, eye="dead", mouth="fangs", gaunt=False,
                  tilt=0):
    """A bigger, sicklier version of the hero head: ashen greasepaint skin,
    sunken/dead or glowing-sick eyes, heavy jagged brows, and an exposed-fang
    leer instead of the happy grin. `gaunt` hollows the cheeks; `tilt` cocks
    the whole head. Drawn onto a scratch surface so the tilt is real."""
    pad = hr * 3
    sc = pygame.Surface((pad * 2, pad * 2), pygame.SRCALPHA)
    sx, sy = pad, pad
    # Ashen head with a dark keyline + a hollow under-eye / cheek shadow.
    pygame.draw.circle(sc, _shade(SKIN_PALE, -55), (sx, sy), hr + 2)
    pygame.draw.circle(sc, SKIN_PALE, (sx, sy), hr)
    if gaunt:
        for s in (-1, 1):
            hollow = pygame.Surface((hr, hr), pygame.SRCALPHA)
            pygame.draw.ellipse(hollow, (40, 20, 40, 90), hollow.get_rect())
            sc.blit(hollow, (sx + s * hr // 2 - hr // 2, sy - hr // 4))
    pygame.draw.circle(sc, _shade(SKIN_PALE, -55), (sx, sy), hr, 2)
    ex = max(7, hr // 2)
    ey = sy - hr // 6
    for s in (-1, 1):
        exx = sx + s * ex
        # Sunken socket shadow behind every eye.
        sock = pygame.Surface((ex, ex), pygame.SRCALPHA)
        pygame.draw.ellipse(sock, (28, 12, 30, 130), sock.get_rect())
        sc.blit(sock, (exx - ex // 2, ey - ex // 2))
        if eye == "dead":
            # Blood-pinprick dead eye in a wide pale socket — vacant + cold.
            pygame.draw.circle(sc, (236, 230, 222), (exx, ey), max(3, hr // 5))
            pygame.draw.circle(sc, DEAD_EYE, (exx, ey), max(1, hr // 12))
        elif eye == "sick":
            # A luminous sickly venom-yellow eye with a slit pupil — glowing.
            pygame.draw.circle(sc, _shade(SICK_EYE, -40), (exx, ey),
                               max(3, hr // 4) + 1)
            pygame.draw.circle(sc, SICK_EYE, (exx, ey), max(3, hr // 4))
            pygame.draw.ellipse(sc, (20, 16, 10),
                                (exx - 1, ey - hr // 4, 3, hr // 2))
        else:  # "leer" — small black bead jammed to the inner corner, sidelong
            pygame.draw.circle(sc, (236, 230, 222), (exx, ey), max(3, hr // 5))
            pygame.draw.circle(sc, (16, 12, 20),
                               (exx - s * (hr // 8), ey), max(2, hr // 9))
        # Heavy jagged brow knitting DOWN toward the nose — the anger "V" the
        # hero deliberately never had. This is the inversion that signals menace.
        inner = (exx - s * (hr // 6), ey - hr // 3)
        outer = (exx + s * (ex // 2 + 3), ey - hr // 2)
        pygame.draw.line(sc, _shade(SKIN_PALE, -120), inner, outer,
                         max(2, hr // 7))
    # A small dull plum nose (the red ball gone bruise-dark, shrunk + sinister).
    pygame.draw.circle(sc, _shade(BLOOD, -30), (sx, sy + hr // 5), max(3, hr // 6))
    pygame.draw.circle(sc, BLOOD, (sx, sy + hr // 5), max(2, hr // 7))
    # MOUTH — an exposed fanged leer or a wide jagged maw.
    my = sy + hr // 2
    if mouth == "fangs":
        # A wide dark maw with a full row of jagged fangs top + bottom.
        mw = int(hr * 0.7)
        maw = pygame.Rect(sx - mw, my - 2, mw * 2, hr // 2)
        pygame.draw.ellipse(sc, (40, 8, 14), maw)
        n = 7
        for i in range(n):
            t = i / (n - 1)
            tx = sx - mw + 2 * mw * t
            # Top fangs point down, bottom fangs point up — interlocking grin.
            pygame.draw.polygon(sc, BONE, [(int(tx - 4), maw.top),
                                           (int(tx + 4), maw.top),
                                           (int(tx), maw.top + hr // 4)])
            pygame.draw.polygon(sc, _shade(BONE, -60),
                                [(int(tx - 4), maw.top),
                                 (int(tx + 4), maw.top),
                                 (int(tx), maw.top + hr // 4)], 1)
        pygame.draw.ellipse(sc, _shade(BLOOD, -40), maw, 2)
    elif mouth == "grin":
        # A long crescent grin curling UP into the cheeks (a too-wide smile)
        # with two long corner fangs — the Glasgow-smile menace read.
        mw = int(hr * 0.85)
        lip = []
        for k in range(15):
            t = k / 14.0
            lx = sx - mw + 2 * mw * t
            ly = my + (1.0 - (2.0 * t - 1.0) ** 2) * (-hr * 0.55)
            lip.append((int(lx), int(ly)))
        pygame.draw.lines(sc, (40, 8, 14), False, lip, max(3, hr // 8))
        for s in (-1, 1):
            fx = sx + s * mw
            pygame.draw.polygon(sc, BONE, [(fx - 3, my - 2), (fx + 3, my - 2),
                                           (fx + s * 1, my + hr // 4)])
        # A blood crack at each corner extending the grin up the cheek.
        for s in (-1, 1):
            pygame.draw.line(sc, BLOOD, (sx + s * mw, my),
                             (sx + s * (mw + hr // 4), my - hr // 4), 2)
    else:  # "smirk" — one corner hooked up, the other flat: a cold knowing leer
        mw = int(hr * 0.7)
        pygame.draw.line(sc, (40, 8, 14), (sx - mw, my + hr // 6),
                         (sx + mw, my - hr // 4), max(3, hr // 8))
        # one corner fang
        fx = sx + mw
        pygame.draw.polygon(sc, BONE, [(fx - 4, my - hr // 4),
                                       (fx + 2, my - hr // 4),
                                       (fx - 1, my)])
        pygame.draw.line(sc, BLOOD, (sx - mw, my + hr // 6),
                         (sx - mw - hr // 5, my + hr // 6 + 3), 2)
    rot = pygame.transform.rotate(sc, tilt)
    surf.blit(rot, (cx - rot.get_width() // 2, cy - rot.get_height() // 2))


# ── evolved cap architectures (each concept owns one) ────────────────────────

def cap_gaunt_droop(surf, cx, base_y, hr, cols):
    """Three impossibly LONG limp points drooping like dead snakes, each ending
    in a heavy tarnished bell — the hero's jaunty 3-point cap gone wilted +
    sinister."""
    a, b, c = cols
    for dx, dy, col, span in ((-4, -8, a, 14), (-30, 34, b, 12),
                              (34, 30, c, 12)):
        bx, by = cx + dx, base_y + dy
        # A long S-curving limp lobe via a spine polygon.
        pts = [(cx - span, base_y + 2), (cx + span, base_y + 2),
               (bx + span // 2, (base_y + by) // 2 - 6),
               (bx, by), (bx - span // 2, (base_y + by) // 2 + 2)]
        pygame.draw.polygon(surf, col, pts)
        pygame.draw.polygon(surf, _shade(col, -60), pts, 2)
        _tarnished_bell(surf, bx, by, r=5)


def cap_brute_crown(surf, cx, base_y, hr, cols):
    """Four heavy splayed points pulled into a low, broad, top-heavy crown that
    flops out past the wide skull — the hero's four-point cap bloated into a
    brutish slab silhouette."""
    a, b, c, _d = cols
    for dx, dy, col in ((-hr - 18, 6, a), (hr + 18, 8, a),
                        (-hr // 2, -22, b), (hr // 2, -20, c)):
        bx, by = cx + dx, base_y + dy
        span = 22
        pts = [(cx - span, base_y + 2), (cx + span, base_y + 2), (bx, by)]
        pygame.draw.polygon(surf, col, pts)
        pygame.draw.polygon(surf, _shade(col, 45),
                            [(cx - span, base_y + 2), (cx, base_y + 2),
                             (bx, by)])
        pygame.draw.polygon(surf, _shade(col, -60), pts, 2)
        _tarnished_bell(surf, bx, by, r=6)


def cap_horns(surf, cx, base_y, hr, cols):
    """The impish horned hood grown into two long SHARP back-curving horns +
    a low jagged crest band — the Hellequin demon read made literal."""
    a, b = cols[0], cols[1]
    # Low hood band hugging the skull.
    pygame.draw.ellipse(surf, _shade(a, -30),
                        (cx - hr - 2, base_y - 8, hr * 2 + 4, 22))
    for s, col in ((-1, a), (1, b)):
        # A long horn sweeping up then curling BACK to a sharp bone tip.
        bx0 = cx + s * (hr - 4)
        pts = [(bx0, base_y + 4), (bx0 + s * 6, base_y - 22),
               (bx0 + s * 2, base_y - 48), (bx0 - s * 10, base_y - 62),
               (bx0 - s * 18, base_y - 50), (bx0 - s * 6, base_y - 30),
               (bx0 - s * 12, base_y + 2)]
        pygame.draw.polygon(surf, col, pts)
        pygame.draw.polygon(surf, _shade(col, -65), pts, 2)
        # Bone horn-tip.
        tip = (bx0 - s * 10, base_y - 62)
        pygame.draw.circle(surf, BONE, tip, 4)
        pygame.draw.circle(surf, _shade(BONE, -55), tip, 4, 1)
    # A small jagged crest of teeth between the horns.
    for i in range(-1, 2):
        bx = cx + i * 9
        pygame.draw.polygon(surf, _shade(a, 20),
                            [(bx - 5, base_y - 4), (bx + 5, base_y - 4),
                             (bx, base_y - 18)])


def cap_carrion_crest(surf, cx, base_y, hr, cols):
    """A jagged carrion COXCOMB: a row of tall ragged spikes along the crown
    like a vulture's torn crest, rooted in a dark band, tipped with dull bells
    on the tallest few."""
    a, b = cols[0], cols[1]
    band = [(cx - hr, base_y + 4), (cx - hr // 2, base_y - 10),
            (cx + 2, base_y - 14), (cx + hr // 2, base_y - 8),
            (cx + hr, base_y + 4)]
    pygame.draw.polygon(surf, _shade(a, -30), band)
    pygame.draw.polygon(surf, _shade(a, -70), band, 2)
    spikes = [(-hr + 4, -16, 18), (-hr // 2, -34, 26), (-4, -42, 30),
              (hr // 2 - 2, -32, 24), (hr - 4, -14, 16)]
    for i, (dx, dy, hgt) in enumerate(spikes):
        col = a if i % 2 == 0 else b
        bx, by = cx + dx, base_y + dy
        pts = [(bx - 7, base_y - 4), (bx + 7, base_y - 4), (bx, by)]
        pygame.draw.polygon(surf, col, pts)
        pygame.draw.polygon(surf, _shade(col, 40),
                            [(bx - 7, base_y - 4), (bx, base_y - 4), (bx, by)])
        pygame.draw.polygon(surf, _shade(col, -60), pts, 2)
        if i in (1, 2, 3):
            _tarnished_bell(surf, bx, by, r=4)


def cap_puppet_ears(surf, cx, base_y, hr, cols):
    """Two heavy DONKEY-ear lobes drooping outward like dead horns, plus a tall
    central spike — a regal-grotesque puppeteer's cap. Bigger + droopier than
    the hero's, every tip a dull bell."""
    a, b, c = cols[0], cols[1], cols[2]
    # Central tall spike.
    sp = [(cx - 12, base_y + 2), (cx + 12, base_y + 2), (cx + 2, base_y - 54)]
    pygame.draw.polygon(surf, b, sp)
    pygame.draw.polygon(surf, _shade(b, -60), sp, 2)
    _tarnished_bell(surf, cx + 2, base_y - 54, r=5)
    for s, col in ((-1, a), (1, c)):
        tipx, tipy = cx + s * (hr + 16), base_y + 30
        spine = [(cx + s * 6, base_y), (cx + s * 22, base_y - 4),
                 (cx + s * (hr + 10), base_y - 18), (tipx, tipy),
                 (cx + s * (hr + 2), base_y + 4), (cx + s * 14, base_y + 10)]
        pygame.draw.polygon(surf, col, spine)
        pygame.draw.polygon(surf, _shade(col, -60), spine, 2)
        _tarnished_bell(surf, tipx, tipy, r=5)


# ── the FIVE evolved concepts (each its own builder + stance) ────────────────

def concept_gaunt_stalker(surf, cx, feet_y):
    """1. GAUNT STALKER — emaciated, towering, hunched forward; long limp cap;
    narrow tapering diamond torso; one long claw reaching DOWN at the viewer."""
    hip_y = feet_y - 120
    # Long thin legs, weight forward, knees slightly bent inward.
    for s, col in ((-1, E_PLUM), (1, E_LIME_DK)):
        hip = (cx + s * 9, hip_y)
        knee = (cx + s * 16, hip_y + 56)
        ankle = (cx + s * 7, feet_y - 6)
        for a, b in ((hip, knee), (knee, ankle)):
            pygame.draw.line(surf, _shade(col, -55), a, b, 12)
            pygame.draw.line(surf, col, a, b, 9)
        # Long curled-toe shoe.
        toe = [(ankle[0] - 14, feet_y), (ankle[0] + 14, feet_y),
               (ankle[0] + 22, feet_y - 4), (ankle[0] + 18, feet_y - 12)]
        pygame.draw.polygon(surf, E_PLUM_DK, toe)
        _tarnished_bell(surf, ankle[0] + 18, feet_y - 12, r=4)
    # Narrow tall torso leaning forward.
    _harlequin_torso(surf, cx, hip_y - 88, hip_y + 6, 16, 24,
                     E_PLUM, E_LIME, lean=-10)
    _dagged_hem(surf, cx, hip_y + 4, 24, 6, E_PLUM, drop=16)
    neck_y = hip_y - 84
    # A tattered narrow ruff drooping forward.
    for i in range(7):
        t = i / 6
        lx = int(cx - 22 + 44 * t)
        ly = int(neck_y + 6 + math.sin(t * math.pi) * 4)
        pygame.draw.polygon(surf, E_GOLD,
                            [(cx, neck_y), (lx - 5, ly + 10), (lx + 5, ly + 10)])
        pygame.draw.polygon(surf, _shade(E_GOLD, -60),
                            [(cx, neck_y), (lx - 5, ly + 10), (lx + 5, ly + 10)], 1)
    # Long left arm reaching DOWN-forward with an open claw; right arm tucked.
    sh_l = (cx - 22, neck_y + 6)
    wrist_l = (cx - 40, hip_y + 20)
    pygame.draw.line(surf, _shade(E_PLUM, -55), sh_l, wrist_l, 13)
    pygame.draw.line(surf, E_PLUM, sh_l, wrist_l, 10)
    sh_r = (cx + 22, neck_y + 4)
    wrist_r = (cx + 30, hip_y - 6)
    pygame.draw.line(surf, _shade(E_LIME_DK, -55), sh_r, wrist_r, 12)
    pygame.draw.line(surf, E_LIME_DK, sh_r, wrist_r, 9)
    _claw_hand(surf, wrist_r, 16, 8, (236, 236, 240), side=1, curl=0.7)
    _claw_hand(surf, wrist_l, 26, 9, (236, 236, 240), side=-1, curl=0.8)
    # Head thrust forward + down on a long neck, hollow gaunt cheeks, smirk.
    head_cx, head_cy, hr = cx - 14, neck_y - 18, 22
    pygame.draw.line(surf, _shade(SKIN_PALE, -50), (cx, neck_y),
                     (head_cx, head_cy + hr), 11)
    cap_gaunt_droop(surf, head_cx, head_cy - hr + 8, hr,
                    (E_PLUM, E_LIME_DK, E_GOLD))
    _evolved_head(surf, head_cx, head_cy, hr, eye="smirk" if False else "dead",
                  mouth="smirk", gaunt=True, tilt=12)


def concept_hulking_brute(surf, cx, feet_y):
    """2. HULKING BRUTE — massive, top-heavy, squat low stance; broad slab
    crown; barrel diamond torso; both fists planted wide, knuckles forward."""
    hip_y = feet_y - 96
    # Short thick legs splayed wide in a low power stance.
    for s in (-1, 1):
        col = E_PLUM if s < 0 else E_LIME_DK
        hip = (cx + s * 22, hip_y)
        ankle = (cx + s * 34, feet_y - 8)
        pygame.draw.line(surf, _shade(col, -55), hip, ankle, 20)
        pygame.draw.line(surf, col, hip, ankle, 16)
        shoe = pygame.Rect(0, 0, 40, 20)
        shoe.center = (ankle[0] + s * 6, feet_y - 2)
        pygame.draw.ellipse(surf, E_PLUM_DK, shoe)
        pygame.draw.ellipse(surf, _shade(E_PLUM_DK, 30), shoe.inflate(-6, -8))
        _tarnished_bell(surf, shoe.centerx + s * 18, shoe.top, r=4)
    # Huge barrel torso, widest at the chest (top-heavy).
    _harlequin_torso(surf, cx, hip_y - 86, hip_y + 8, 52, 36,
                     E_PLUM, E_LIME)
    _dagged_hem(surf, cx, hip_y + 6, 36, 9, E_PLUM, drop=12)
    neck_y = hip_y - 82
    # A massive scalloped ruff (the hero's ruff bloated, tarnished).
    for i in range(13):
        t = i / 12
        lx = int(cx - 52 + 104 * t)
        ly = int(neck_y + 6 + math.sin(t * math.pi) * -4)
        pygame.draw.circle(surf, E_GOLD_DK, (lx, ly), 11)
        pygame.draw.circle(surf, E_GOLD, (lx, ly), 9)
        pygame.draw.circle(surf, _shade(E_GOLD, 60), (lx - 3, ly - 3), 3)
    # Both arms spread wide, heavy, ending in big planted claw-fists.
    for s in (-1, 1):
        col = E_LIME_DK if s < 0 else E_PLUM
        sh = (cx + s * 46, neck_y + 10)
        elbow = (cx + s * 70, neck_y + 50)
        wrist = (cx + s * 60, hip_y + 4)
        for a, b in ((sh, elbow), (elbow, wrist)):
            pygame.draw.line(surf, _shade(col, -55), a, b, 22)
            pygame.draw.line(surf, col, a, b, 18)
        _claw_hand(surf, wrist, 18, 12, (236, 236, 240), side=s, curl=0.5)
    # Tiny head sunk between massive shoulders — a wide fanged maw.
    head_cx, head_cy, hr = cx, neck_y - 8, 24
    cap_brute_crown(surf, head_cx, head_cy - hr + 8, hr,
                    (E_PLUM, E_LIME, E_GOLD, E_PLUM))
    _evolved_head(surf, head_cx, head_cy, hr, eye="dead", mouth="fangs",
                  tilt=-3)


def concept_horned_imp(surf, cx, feet_y):
    """3. HORNED IMP-LORD — tall lean devil; long back-curving horns; lithe
    diamond suit; one claw raised in a beckoning curl; luminous sick eyes."""
    hip_y = feet_y - 116
    for s, col in ((-1, E_LIME_DK), (1, E_PLUM)):
        hip = (cx + s * 11, hip_y)
        knee = (cx + s * 18, hip_y + 50)
        ankle = (cx + s * 10, feet_y - 6)
        for a, b in ((hip, knee), (knee, ankle)):
            pygame.draw.line(surf, _shade(col, -55), a, b, 13)
            pygame.draw.line(surf, col, a, b, 10)
        toe = [(ankle[0] - 12, feet_y), (ankle[0] + 16, feet_y),
               (ankle[0] + 24, feet_y - 10)]
        pygame.draw.polygon(surf, E_PLUM_DK, toe)
        _tarnished_bell(surf, ankle[0] + 24, feet_y - 10, r=4)
    _harlequin_torso(surf, cx, hip_y - 80, hip_y + 4, 22, 26, E_PLUM, E_LIME)
    _dagged_hem(surf, cx, hip_y + 2, 26, 7, E_PLUM, drop=14)
    neck_y = hip_y - 76
    # A pointed dagged collar (sharp lime points, not soft scallops).
    for i in range(9):
        t = i / 8
        lx = int(cx - 30 + 60 * t)
        ly = int(neck_y + 4 + abs(t - 0.5) * 10)
        pygame.draw.polygon(surf, E_LIME,
                            [(cx, neck_y - 2), (lx - 5, ly + 12), (lx + 5, ly + 12)])
        pygame.draw.polygon(surf, _shade(E_LIME, -55),
                            [(cx, neck_y - 2), (lx - 5, ly + 12), (lx + 5, ly + 12)], 1)
        _tarnished_bell(surf, lx, ly + 13, r=3)
    # Left arm raised high, claw curling in a "come here" beckon; right hangs.
    sh_l = (cx - 24, neck_y + 8)
    elbow_l = (cx - 42, neck_y - 18)
    wrist_l = (cx - 30, neck_y - 48)
    for a, b in ((sh_l, elbow_l), (elbow_l, wrist_l)):
        pygame.draw.line(surf, _shade(E_PLUM, -55), a, b, 13)
        pygame.draw.line(surf, E_PLUM, a, b, 10)
    _claw_hand(surf, wrist_l, 18, 8, (236, 236, 240), side=-1, curl=1.1)
    sh_r = (cx + 24, neck_y + 8)
    wrist_r = (cx + 34, hip_y - 8)
    pygame.draw.line(surf, _shade(E_LIME_DK, -55), sh_r, wrist_r, 12)
    pygame.draw.line(surf, E_LIME_DK, sh_r, wrist_r, 9)
    _claw_hand(surf, wrist_r, 16, 8, (236, 236, 240), side=1, curl=0.7)
    head_cx, head_cy, hr = cx + 2, neck_y - 22, 23
    cap_horns(surf, head_cx, head_cy - hr + 10, hr, (E_PLUM, E_PLUM_DK))
    _evolved_head(surf, head_cx, head_cy, hr, eye="sick", mouth="grin",
                  tilt=-8)


def concept_carrion(surf, cx, feet_y):
    """4. CARRION COXCOMB — vulture-hunched; raised hunched shoulders; head
    thrust low + forward; ragged crest; tattered dagged everything; smirk."""
    hip_y = feet_y - 108
    for s, col in ((-1, E_PLUM), (1, E_LIME_DK)):
        hip = (cx + s * 12, hip_y)
        knee = (cx + s * 20, hip_y + 50)
        ankle = (cx + s * 14, feet_y - 6)
        for a, b in ((hip, knee), (knee, ankle)):
            pygame.draw.line(surf, _shade(col, -55), a, b, 14)
            pygame.draw.line(surf, col, a, b, 11)
        toe = [(ankle[0] - 13, feet_y), (ankle[0] + 18, feet_y),
               (ankle[0] + 26, feet_y - 9)]
        pygame.draw.polygon(surf, E_PLUM_DK, toe)
        _tarnished_bell(surf, ankle[0] + 26, feet_y - 9, r=4)
    # Torso hunched: top sheared hard forward, shoulders raised toward the ears.
    _harlequin_torso(surf, cx, hip_y - 78, hip_y + 4, 26, 30, E_PLUM, E_LIME,
                     lean=-14)
    _dagged_hem(surf, cx, hip_y + 2, 30, 8, E_PLUM, drop=18)
    neck_y = hip_y - 74
    # A lopsided tattered ruff hanging forward off the hunch.
    for i in range(9):
        t = i / 8
        lx = int(cx - 30 + 60 * t)
        ly = int(neck_y + 8 + math.sin(t * math.pi) * 5 + 4)
        col = E_GOLD if i % 2 else E_GOLD_DK
        pygame.draw.polygon(surf, col,
                            [(cx - 6, neck_y), (lx - 6, ly + 12), (lx + 4, ly + 14)])
        pygame.draw.polygon(surf, _shade(col, -60),
                            [(cx - 6, neck_y), (lx - 6, ly + 12), (lx + 4, ly + 14)], 1)
    # Raised hunched shoulders; long arms dangling forward with hooked claws.
    for s in (-1, 1):
        col = E_LIME_DK if s < 0 else E_PLUM
        sh = (cx + s * 34, neck_y - 6)             # raised toward the ears
        elbow = (cx + s * 40, neck_y + 40)
        wrist = (cx + s * 22, hip_y + 18)          # dangling forward + in
        for a, b in ((sh, elbow), (elbow, wrist)):
            pygame.draw.line(surf, _shade(col, -55), a, b, 15)
            pygame.draw.line(surf, col, a, b, 11)
        _claw_hand(surf, wrist, 18, 8, (236, 236, 240), side=s, curl=0.9)
    # Head thrust LOW + forward off the hunch (vulture peer), tilted, smirking.
    head_cx, head_cy, hr = cx - 18, neck_y + 2, 21
    pygame.draw.line(surf, _shade(SKIN_PALE, -50), (cx - 4, neck_y),
                     (head_cx + 6, head_cy), 12)
    cap_carrion_crest(surf, head_cx, head_cy - hr + 6, hr, (E_PLUM, E_LIME))
    _evolved_head(surf, head_cx, head_cy, hr, eye="dead", mouth="smirk",
                  gaunt=True, tilt=18)


def concept_puppeteer(surf, cx, feet_y):
    """5. RINGMASTER PUPPETEER — towering, regal, arms flung WIDE + up in a
    grand grotesque flourish; donkey-eared spiked cap; broad diamond robe;
    the widest, most theatrically menacing silhouette; too-wide grin."""
    hip_y = feet_y - 124
    for s, col in ((-1, E_PLUM), (1, E_LIME_DK)):
        hip = (cx + s * 14, hip_y)
        ankle = (cx + s * 16, feet_y - 8)
        pygame.draw.line(surf, _shade(col, -55), hip, ankle, 16)
        pygame.draw.line(surf, col, hip, ankle, 13)
        toe = [(ankle[0] - 15, feet_y), (ankle[0] + 20, feet_y),
               (ankle[0] + 30, feet_y - 14), (ankle[0] + 24, feet_y - 22)]
        pygame.draw.polygon(surf, E_PLUM_DK, toe)
        _tarnished_bell(surf, ankle[0] + 24, feet_y - 22, r=5)
    # A long broad robe-torso flaring at the hem (regal silhouette).
    _harlequin_torso(surf, cx, hip_y - 92, hip_y + 8, 30, 42, E_PLUM, E_LIME)
    _dagged_hem(surf, cx, hip_y + 6, 42, 9, E_PLUM, drop=20)
    neck_y = hip_y - 88
    # A grand wide scalloped + dagged double ruff.
    for i in range(15):
        t = i / 14
        lx = int(cx - 56 + 112 * t)
        ly = int(neck_y + 6 + math.sin(t * math.pi) * -5)
        pygame.draw.circle(surf, E_GOLD_DK, (lx, ly), 10)
        pygame.draw.circle(surf, E_GOLD, (lx, ly), 8)
        pygame.draw.circle(surf, _shade(E_GOLD, 60), (lx - 2, ly - 2), 3)
    # Arms flung WIDE and UP in a grand flourish, both claws spread skyward.
    for s in (-1, 1):
        col = E_LIME_DK if s < 0 else E_PLUM
        sh = (cx + s * 30, neck_y + 8)
        elbow = (cx + s * 58, neck_y - 6)
        wrist = (cx + s * 80, neck_y - 40)
        for a, b in ((sh, elbow), (elbow, wrist)):
            pygame.draw.line(surf, _shade(col, -55), a, b, 16)
            pygame.draw.line(surf, col, a, b, 12)
        # A trailing dagged sleeve hanging off the upper arm.
        drape = [(sh[0], sh[1]), (elbow[0], elbow[1]),
                 (elbow[0] - s * 6, elbow[1] + 26),
                 ((sh[0] + elbow[0]) // 2, (sh[1] + elbow[1]) // 2 + 30)]
        pygame.draw.polygon(surf, _shade(col, -25), drape)
        pygame.draw.polygon(surf, _shade(col, -60), drape, 1)
        _claw_hand(surf, wrist, 20, 9, (236, 236, 240), side=s, curl=0.9)
    # Tall head held high + back, a too-wide corner-cracked grin.
    head_cx, head_cy, hr = cx, neck_y - 24, 24
    cap_puppet_ears(surf, head_cx, head_cy - hr + 8, hr,
                    (E_PLUM, E_LIME, E_LIME_DK))
    _evolved_head(surf, head_cx, head_cy, hr, eye="dead", mouth="grin",
                  tilt=0)


# ── the original reference (clown-only, from build_jester) ───────────────────

def concept_original(surf, cx, feet_y):
    """Cell 0: the CURRENT hero clown, drawn clown-only (no staff) with the same
    presenting body so the size + menace jump to the evolved cells reads."""
    # A neutral down-forward hand so the figure stands alone without a die.
    hand_up = (cx - 30, feet_y - 92)
    build_jester(surf, cx, feet_y, hand_up, **ORIG)


# ── the combined sheet ───────────────────────────────────────────────────────

CONCEPTS = [
    ("ORIGINAL — Plum & Lime (locked)", concept_original),
    ("1. GAUNT STALKER", concept_gaunt_stalker),
    ("2. HULKING BRUTE", concept_hulking_brute),
    ("3. HORNED IMP-LORD", concept_horned_imp),
    ("4. CARRION COXCOMB", concept_carrion),
    ("5. RINGMASTER PUPPETEER", concept_puppeteer),
]

# Sub-captions describing each concept's distinct read.
SUBS = [
    "the early-game clown, clown-only · for scale + menace comparison",
    "emaciated · hunched fwd · limp 3-droop cap · claw reaches DOWN · dead-eye smirk",
    "top-heavy slab · low power stance · broad crown · fists planted · fanged maw",
    "lean devil · long back-curving HORNS · beckoning claw · luminous sick eyes",
    "vulture-hunched · raised shoulders · head thrust low · ragged crest · tatters",
    "towering · arms flung WIDE+up · donkey-ear spike cap · too-wide cracked grin",
]


def _wrap(font, text, max_w):
    """Greedy word-wrap `text` to lines no wider than `max_w` px."""
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if font.size(t)[0] <= max_w or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def main():
    pygame.init()
    pygame.font.init()
    pygame.display.set_mode((W, H))

    # Each concept is drawn at NATIVE px on a tile (the concept geometry uses
    # absolute offsets), then smoothscaled UP to the display cell so the figures
    # read large + crisp on the sheet (the earlier supersample only enlarged the
    # backdrop, so the downscale was shrinking every figure to half-size).
    FIG_W, FIG_H = 260, 360
    GROUND_Y = FIG_H - 36          # ONE matched ground line across every cell
    FIGSCALE = 1.6
    CELL_W, CELL_H = int(FIG_W * FIGSCALE), int(FIG_H * FIGSCALE)
    cols, rows = 3, 2
    PAD, GAP = 46, 26

    f_title = pygame.font.SysFont(None, 56, bold=True)
    f_sub = pygame.font.SysFont(None, 28, bold=True)
    f_cap = pygame.font.SysFont(None, 36, bold=True)
    f_caps = pygame.font.SysFont(None, 25, bold=True)

    canvas_w = PAD * 2 + cols * CELL_W + (cols - 1) * GAP
    inner_w = canvas_w - 2 * PAD

    title_lines = _wrap(
        f_title, "EVOLVED WARREN CLOWN — late-game boss escalation (round 1)",
        inner_w)
    sub_lines = _wrap(
        f_sub, "The SAME Plum & Lime character grown larger / meaner / nastier: "
        "bruised plum, venom lime, tarnished gold + blood & bruise accents. Five "
        "distinct menacing silhouettes on ONE matched ground line. No staff "
        "(separate cycle).", inner_w)
    # Per-cell sub-captions wrapped to the cell width.
    sub_wrapped = [_wrap(f_caps, s, CELL_W - 10) for s in SUBS]
    max_sub_lines = max(len(x) for x in sub_wrapped)

    th = f_title.get_height() + 2
    sh_ = f_sub.get_height() + 2
    TITLE_H = len(title_lines) * th + 10 + len(sub_lines) * sh_ + 18
    CAP_H = 8 + f_cap.get_height() + 4 + max_sub_lines * (f_caps.get_height() + 1) + 12
    canvas_h = PAD * 2 + TITLE_H + rows * (CELL_H + CAP_H) + (rows - 1) * GAP

    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((92, 92, 100))      # neutral mid-tone background per the brief

    yy = PAD
    for ln in title_lines:
        canvas.blit(f_title.render(ln, True, (244, 238, 224)), (PAD, yy))
        yy += th
    yy += 8
    for ln in sub_lines:
        canvas.blit(f_sub.render(ln, True, (210, 212, 218)), (PAD, yy))
        yy += sh_

    y0 = PAD + TITLE_H
    for i, (name, fn) in enumerate(CONCEPTS):
        r, c = divmod(i, cols)
        cx = PAD + c * (CELL_W + GAP)
        cy = y0 + r * (CELL_H + CAP_H + GAP)

        # Native figure tile: gradient backdrop + matched floor + contact shadow.
        tile = pygame.Surface((FIG_W, FIG_H))
        for yyf in range(FIG_H):
            t = yyf / FIG_H
            col = (int(104 - 20 * t), int(104 - 20 * t), int(112 - 18 * t))
            pygame.draw.line(tile, col, (0, yyf), (FIG_W, yyf))
        pygame.draw.rect(tile, (70, 68, 78), (0, GROUND_Y, FIG_W, FIG_H - GROUND_Y))
        pygame.draw.line(tile, (120, 118, 128), (0, GROUND_Y), (FIG_W, GROUND_Y), 2)
        shsurf = pygame.Surface((FIG_W, 22), pygame.SRCALPHA)
        pygame.draw.ellipse(shsurf, (20, 18, 26, 120), (FIG_W // 2 - 70, 0, 140, 22))
        tile.blit(shsurf, (0, GROUND_Y - 8))

        fn(tile, FIG_W // 2, GROUND_Y)

        scaled = pygame.transform.smoothscale(tile, (CELL_W, CELL_H))
        frame = (236, 196, 90) if i == 0 else (60, 58, 70)
        pygame.draw.rect(canvas, frame,
                         pygame.Rect(cx - 2, cy - 2, CELL_W + 4, CELL_H + 4), 3)
        canvas.blit(scaled, (cx, cy))

        cap = f_cap.render(name, True,
                           (244, 224, 150) if i == 0 else (236, 230, 220))
        canvas.blit(cap, (cx + (CELL_W - cap.get_width()) // 2, cy + CELL_H + 8))
        ly = cy + CELL_H + 8 + f_cap.get_height() + 4
        for ln in sub_wrapped[i]:
            s2 = f_caps.render(ln, True, (198, 200, 208))
            canvas.blit(s2, (cx + (CELL_W - s2.get_width()) // 2, ly))
            ly += f_caps.get_height() + 1

    out_dir = os.path.join("docs", "evolved_clown")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_1.png")
    pygame.image.save(canvas, out_path)
    print(f"saved {out_path}  ({canvas_w}x{canvas_h})")


if __name__ == "__main__":
    main()
