"""Look-dev mockup: 10 NEW Court Jester power-up dice presenters (ROUND 4).

The user loved the Court Jester from the dice-clown sheet for its sly,
"up-to-something / NAUGHTY" read. This sheet explores TEN higher-quality
takes on that ONE archetype — each a large hero jester standing in the day
clearing (sky + grass + the real parrot for scale), presenting a glowing
power-up die. Everything is drawn from pygame primitives; we import the REAL
game helpers (biome palette, glow cache, live parrot) and the chunky body
kit from the dice-clown mockup, and mutate no game state.

THE FIXED POSE (identical on all ten — a hard requirement): the die floats in
the upper-LEFT focal slot, the viewer's-LEFT arm (`cx - …`) is raised
diagonally up presenting an open offering glove that CUPS UNDER the die, and
the viewer's-RIGHT arm (`cx + …`) hangs down with a visible mitt and a slight
outward bow. This MIRRORS the original jester (which raised its right arm to a
die at upper-right). The die's power-up treatment is kept EXACTLY consistent
across all ten: classic d6 pips, gold glow halo (BLEND_ADD), top-left rim
light, gentle bob, orbiting sparkles.

ROUND-4 direction (FACE-ONLY pass; everything below the chin ships unchanged):
  The round-3 face read SAD / PLEADING / WEEPY — the exact opposite of naughty.
  Three shared face-geometry fixes (applied to the one shared recipe so all 10
  update together):
  - FLIPPED BROW TO A REAL SCHEMING "V": the inner corner is now HIGH + pulled
    INWARD to the nose-bridge, the outer corner LOW + out — the hard inverse of
    round-3's inner-low/outer-high "about-to-cry" brow, exaggerated so the angle
    reads at 1x.
  - DELETED EVERY TEAR STREAK + WATERY HIGHLIGHT: the under-eye blush that
    streaked like tears is moved low onto the cheek apple; the glossy tear-dot
    and down-curved watery lower lid are gone. Each eye is now a FLAT half-lidded
    almond — a straight (outer end dipping DOWN) heavy upper lid over white
    sclera, with a dark pupil jammed into the DIE-SIDE corner (sly sidelong
    up-left glance).
  - COMMITTED LOPSIDED UP-SMIRK: the die-side corner is pulled clearly UP + back
    with a hook + cheek dimple, the far corner dropped low — a definite
    asymmetric up-hook, never a symmetric down-curve.
  - COMMITTED plotting BODY LEAN on every figure: die-side shoulder dropped 7px,
    hip cocked hard, weight on the die-side leg, the trailing knee bent.
  - Coxcomb crests ANCHORED to the scalp by a base band; #2/#9 value contrast
    raised so they hold against the day sky; #2's four-point cap splayed out.
  - Every costume lifted to the #6 standard: scalloped/pointed belled collar,
    per-panel costume shading, curled-toe belled shoes, two-tone harlequin
    hose, thumb-divided mitts.
  - Die now CUPPED by the open mitt with a soft contact-glow (no flat grey
    drop-shadow under the floating die).
  - Caps fixed: a true two-eared donkey cap, a not-a-crown belled four-point,
    a single IMPISH (charcoal-plum, soft bell-nub) horned hood.
  - Palettes de-clustered off the purple family toward distinct warm / cool
    families; proportions biased to the shorter rounder chibi build.

Each cell is supersampled 2x then smoothscaled for crisp anti-aliasing.

    PYTHONPATH=. python tools/render_jester_variants.py
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.config import W, H
from game.draw import lerp_color, blit_glow
from game.parrot import get_parrot
from tools.render_warren_mockup import shaped_palette

# Reuse the chunky mascot body kit + the consistent floating-die prop from the
# dice-clown mockup so these jesters read as the SAME family of casual mascots
# and the power-up die is pixel-identical to the approved treatment.
from tools.render_clown_dice import (
    _shade, _poly, _facet_body, _round_head, _nose, _arm, _leg, _shoes,
    _shadow, RIM, WHITE, INK, ROSY,
    DAY_PHASE, SS, VIEW_W, VIEW_H, VIEW_FEET_Y,
    HERO_PIPS, _PIP_LAYOUT,
)


# ── the NAUGHTY face kit (ONE locked recipe on all ten) ──────────────────────
# Round-1 critique: only the teal/magenta tile fully sold the scheming read;
# the rest drifted neutral/surprised/sour. The signature is now a SINGLE recipe
# applied to every jester (the #4 reference), built from the same friendly-but-
# cheeky vocabulary so the read is consistent: scheming "V" brows (inner ends
# DOWN, outer ends UP), half-lidded eyes with both pupils shoved to one side
# (a sidelong glance), and an ASYMMETRIC smirk (one corner higher, slight
# curl — never a symmetric frown or flat line). Variants layer on a single
# cocked brow and a tongue-tip at the smirk corner for variety.

MOUTH = (188, 56, 66)


def _scheme_eye(surf, x, y, *, look):
    """A FLAT half-lidded almond — confident and sly, never droopy or weepy.
    Round-3 still read teary: a curved/down lower lid plus an under-eye streak
    looked like tears. This rebuild is a hard, simple almond: a STRAIGHT (very
    slightly DOWN at the outer end) heavy upper-lid line, a white sclera showing
    below it, and a dark pupil shoved hard into the DIE-SIDE corner for a sly
    sidelong glance up toward the die. NO tear streak, NO glossy watery dot, NO
    up-curving sad lash-arc, NO down-curved watery lower lid. `look` is the
    horizontal pupil shove (negative = toward the upper-left die)."""
    ew, eh = 5, 4  # almond half-extents (a touch flatter than a round eye)
    # White sclera — a low, wide almond. Kept compact so the heavy lid above can
    # cover the top half without the eye ever reading wide/surprised or weepy.
    eye_rect = pygame.Rect(x - ew, y - eh + 3, ew * 2, eh * 2)
    pygame.draw.ellipse(surf, WHITE, eye_rect)
    # Dark pupil jammed into the DIE-SIDE corner (sidelong up-left glance). NO
    # bright watery specular catch at all — round-3's white highlight read as a
    # glossy tear, so the pupil is a flat matte dot only.
    px = x + look
    py = y + 3
    pygame.draw.circle(surf, (40, 36, 54), (px, py), 3)
    pygame.draw.circle(surf, (16, 14, 24), (px, py), 3, 1)
    # FLAT heavy upper lid as a STRAIGHT bar with a slight DOWN-slant AWAY from
    # the die (the lid sits higher on the die-glance side and dips down on the
    # far side) — a hooded, knowing squint, never an up-curving sad lash. Both
    # eyes slant the same screen direction so the sidelong read is consistent.
    hi_side = -1 if look < 0 else 1   # lid rides high on the die-glance side
    lid_hi = (x + hi_side * (ew + 1), y - 1)
    lid_lo = (x - hi_side * (ew + 1), y + 1)  # far end dips DOWN 2px
    pygame.draw.line(surf, INK, lid_hi, lid_lo, 3)


def _cheek(surf, cx, cy, r, *, strong=False):
    """Warm cheek blush discs so the mischief always reads charming, not cold.
    Round-3 placed these high + narrow directly UNDER the inner eye, where they
    read as red TEAR streaks running down the cheek. They are now low, round and
    pushed OUTWARD onto the apple of the cheek (well below the eye/nose line) so
    they read unmistakably as a warm flush, never a tear."""
    for s in (-1, 1):
        a = 190 if strong else 135
        blush = pygame.Surface((14, 10), pygame.SRCALPHA)
        pygame.draw.ellipse(blush, (*ROSY, a), blush.get_rect())
        # Low on the cheek apple and well out toward the head edge.
        surf.blit(blush, (cx + s * (r - 5) - 7, cy + 6))


def naughty_face(surf, cx, hy, hr, *, nose_col=(232, 72, 72), variant="plain"):
    """Paint the ONE locked scheming expression. `variant` only layers small
    extra flavour on top of the shared recipe:
        "plain"   — the base recipe.
        "browcock"— one eyebrow cocked high (oh-really).
        "tongue"  — a tongue-tip poking the smirk corner.
        "tonguecock" — both of the above.
    The whole head (face + cap) is rotated by the caller for the plotting lean,
    so the features always tilt WITH the body rather than floating level."""
    ex = max(6, hr // 2)
    # Pupils glance sidelong toward the die (upper-LEFT) — caught plotting.
    look = -3
    _cheek(surf, cx, hy + 3, hr, strong=variant in ("tongue", "tonguecock"))

    cock_left = variant in ("browcock", "tonguecock")
    for s in (-1, 1):
        exx = cx + s * ex
        _scheme_eye(surf, exx, hy, look=look)
        # REAL scheming "V": the INNER end is HIGH and pulled INWARD toward the
        # nose-bridge; the OUTER end drives LOW and out. This is the hard INVERSE
        # of round-3's inner-low/outer-high "worried / about-to-cry" brow — the
        # single sign-flip that turns weepy into plotting. The inner/outer y-gap
        # is exaggerated (8px) so the down-and-in angle reads even at 1x.
        # Inner end (nose-side, toward centre cx) is HIGH; outer end (temple
        # side) is LOW. For the left eye nose-side is +x, for the right eye it
        # is -x, hence the `-s` / `+s` x-signs.
        inner = (exx - s * 2, hy - 13)       # inner end HIGH + pinched to nose
        outer = (exx + s * 8, hy - 5)        # outer end LOW + out
        cock = cock_left and s < 0
        if cock:
            inner = (inner[0], inner[1] - 4)
            outer = (outer[0], outer[1] - 3)
        pygame.draw.line(surf, INK, inner, outer, 3)
        # A short heavier stub at the inner (high, pinched) end thickens the
        # knitted brow-root so the two inner ends crowd the nose-bridge.
        pygame.draw.line(surf, INK, inner, (inner[0] + s * 2, inner[1] + 2), 3)

    _nose(surf, cx, hy + 6, 6, nose_col)

    # COMMITTED lopsided up-SMIRK. The DIE-SIDE corner (viewer-LEFT, where the
    # eyes are glancing) is pulled clearly UP and BACK; the far corner drops low.
    # Built as a definite asymmetric up-hook (never the round-3 soft symmetric
    # down-curve): the line climbs from the dropped far corner up to the raised
    # die-side corner, then flicks up into a smirk hook.
    hi = (cx - 10, hy + 8)               # raised die-side (LEFT) corner, up/back
    mid = (cx - 1, hy + 13)
    lo = (cx + 9, hy + 14)               # dropped far (RIGHT) corner, flat-low
    pygame.draw.lines(surf, MOUTH, False, [lo, mid, hi], 3)
    # Curl tail flicking UP off the raised die-side corner so the hook reads.
    pygame.draw.line(surf, MOUTH, hi, (hi[0] - 2, hi[1] - 3), 3)
    # Single cheek dimple crease on the RAISED (die-side / LEFT) side only.
    pygame.draw.line(surf, _shade(nose_col, -40), (hi[0] - 3, hi[1] - 1),
                     (hi[0] - 4, hi[1] + 3), 2)

    if variant in ("tongue", "tonguecock"):
        # Tongue tip poking out the raised (die-side / LEFT) smirk corner.
        pygame.draw.ellipse(surf, (236, 120, 130), (hi[0] - 7, hi[1], 8, 7))
        pygame.draw.ellipse(surf, _shade((236, 120, 130), -45),
                            (hi[0] - 7, hi[1], 8, 7), 1)


# ── belled-cap kit ────────────────────────────────────────────────────────────
# The fool's cap is the jester's loudest silhouette cue. Each variation owns a
# distinct cap shape, every one finished with belled tips (a lit specular on
# each bell so they read as gold spheres, not flat discs).

def _bell(surf, x, y, r=4, col=(245, 240, 200)):
    pygame.draw.circle(surf, _shade(col, -55), (x, y), r + 1)
    pygame.draw.circle(surf, col, (x, y), r)
    pygame.draw.circle(surf, _shade(col, 80), (x - 1, y - 1), max(1, r // 2))


def _cap_point(surf, cx, base_y, hr, dx, dy, col, *, span=16):
    """One drooping cap point as a triangle from the head crown to a belled
    tip, with a lit top-left facet + dark keyline."""
    bx, by = cx + dx, base_y + dy
    pts = [(cx - span, base_y + 2), (cx + span, base_y + 2), (bx, by)]
    pygame.draw.polygon(surf, col, pts)
    pygame.draw.polygon(surf, _shade(col, 50),
                        [(cx - span, base_y + 2), (cx + span // 2, base_y + 2),
                         (bx, by)])
    pygame.draw.polygon(surf, _shade(col, -60), pts, 2)
    _bell(surf, bx, by)


def cap_three_point(surf, cx, base_y, hr, cols):
    """Classic drooping three-point belled cap — the reliable jester read."""
    a, b, c = cols[0], cols[1], cols[2]
    _cap_point(surf, cx, base_y, hr, -28, -26, a)
    _cap_point(surf, cx, base_y, hr, 2, -40, b)
    _cap_point(surf, cx, base_y, hr, 30, -24, c)


def cap_four_point(surf, cx, base_y, hr, cols):
    """Four belled points SPLAYED outward so the cluster reads as a floppy fool's
    cap, never an upright king's crown (round-2 #2 still read royal). The two
    outer points flop hard down-and-OUT past the head edges and the two inner
    points lean low and apart — a wide drooping fan, not vertical spikes."""
    a, b, c, _d = cols
    # Outer pair flops WAY out past the head silhouette and drops low; inner pair
    # leans outward too so nothing stands upright in the middle.
    _cap_point(surf, cx, base_y, hr, -42, -6, a, span=14)
    _cap_point(surf, cx, base_y, hr, 42, -4, a, span=14)
    _cap_point(surf, cx, base_y, hr, -16, -28, b, span=14)
    _cap_point(surf, cx, base_y, hr, 16, -26, c, span=14)


def cap_donkey(surf, cx, base_y, hr, cols):
    """A TRUE donkey-ear cap: two tall floppy ears (rounded, drooping outward at
    the tips), not a single cone. A low band ties them to the crown, each ear
    bell-tipped."""
    a, b = cols[0], cols[1]
    # Each ear is a long rounded lobe that bows outward then flops back with a
    # bell — built from a filled polygon spine + a rounded cap so it reads soft
    # and floppy, not as a stiff spike.
    for s, col in ((-1, a), (1, b)):
        tipx, tipy = cx + s * 30, base_y - 50
        spine = [(cx + s * 4, base_y - 2), (cx + s * 16, base_y - 2),
                 (cx + s * 26, base_y - 26), (tipx, tipy),
                 (cx + s * 22, base_y - 44), (cx + s * 10, base_y - 18)]
        pygame.draw.polygon(surf, col, spine)
        pygame.draw.polygon(surf, _shade(col, 45),
                            [(cx + s * 4, base_y - 2),
                             (cx + s * 12, base_y - 14),
                             (cx + s * 10, base_y - 18)])
        pygame.draw.polygon(surf, _shade(col, -60), spine, 2)
        # Soft rounded ear tip + an inner-ear lighter lobe.
        pygame.draw.circle(surf, _shade(col, 30), (tipx, tipy), 5)
        _bell(surf, tipx, tipy, r=3)
    # Low band cap joining the ears across the crown.
    pygame.draw.arc(surf, _shade(a, -20), (cx - 20, base_y - 16, 40, 24),
                    math.pi, math.tau, 5)
    pygame.draw.arc(surf, _shade(a, 35), (cx - 17, base_y - 14, 34, 18),
                    math.pi, math.tau, 2)


def cap_coxcomb(surf, cx, base_y, hr, cols):
    """Rooster-crest coxcomb: a row of scalloped lobes ATTACHED to the scalp by a
    base band along the hairline. Round-2 read as detached floating spheres; now
    a filled base band tucks under the lobes and the rearmost lobe sits BEHIND the
    head crown so the crest reads as growing out of the head, not hovering."""
    a, b = cols[0], cols[1]
    # Base band hugging the crown — a filled wedge along the hairline the lobes
    # all root into, so no lobe floats free of the head.
    band = [(cx - 24, base_y + 2), (cx - 14, base_y - 12),
            (cx + 2, base_y - 16), (cx + 18, base_y - 10),
            (cx + 22, base_y + 2)]
    pygame.draw.polygon(surf, _shade(a, -30), band)
    pygame.draw.polygon(surf, _shade(a, -70), band, 2)
    lobes = [(-22, -14), (-9, -28), (5, -32), (18, -20)]
    for i, (dx, dy) in enumerate(lobes):
        col = a if i % 2 == 0 else b
        bx, by = cx + dx, base_y + dy
        pygame.draw.circle(surf, _shade(col, -55), (bx, by), 9)
        pygame.draw.circle(surf, col, (bx, by), 8)
        pygame.draw.circle(surf, _shade(col, 55), (bx - 2, by - 2), 3)
    _bell(surf, cx + 22, base_y - 12)


def cap_hood(surf, cx, base_y, hr, cols):
    """Curled close hood with a single long forward-curling belled point — a
    real curled-bell hood (one of the featured cap shapes)."""
    a = cols[0]
    pygame.draw.ellipse(surf, _shade(a, -30), (cx - hr - 1, base_y - 18,
                                               hr * 2 + 2, 26))
    pygame.draw.ellipse(surf, a, (cx - hr, base_y - 18, hr * 2, 24))
    pygame.draw.arc(surf, _shade(a, 45), (cx - hr + 3, base_y - 16, hr, 14),
                    math.pi, math.tau, 2)
    # Long forward-curling point sweeping right then dropping a bell.
    pts = [(cx - 6, base_y - 14), (cx + 8, base_y - 16),
           (cx + 30, base_y - 30), (cx + 24, base_y - 14),
           (cx + 10, base_y - 6)]
    pygame.draw.polygon(surf, _shade(a, 20), pts)
    pygame.draw.polygon(surf, _shade(a, -55), pts, 2)
    _bell(surf, cx + 30, base_y - 30)


def cap_imp_hood(surf, cx, base_y, hr, cols):
    """The single surviving horned hood — but IMPISH, not menacing: the horns
    are rounded into soft bell-tipped NUBS (not sharp spikes) and the palette
    is warmed off pure black toward charcoal-plum by the caller. Reads playful-
    devilish, the cheeky kind."""
    a, b = cols[0], cols[1]
    pygame.draw.ellipse(surf, _shade(a, -30), (cx - hr - 1, base_y - 12,
                                               hr * 2 + 2, 20))
    pygame.draw.ellipse(surf, a, (cx - hr, base_y - 12, hr * 2, 18))
    pygame.draw.arc(surf, _shade(a, 40), (cx - hr + 3, base_y - 10, hr, 12),
                    math.pi, math.tau, 2)
    # Short fat rounded nubs that curl gently outward — drawn as stubby lobes
    # plus a soft bell on the tip so they read impish, not horned-menace.
    for s, col in ((-1, a), (1, b)):
        bx, by = cx + s * 18, base_y - 22
        pygame.draw.circle(surf, _shade(col, -45), (cx + s * 13, base_y - 8), 7)
        pygame.draw.circle(surf, col, (cx + s * 13, base_y - 8), 6)
        pygame.draw.circle(surf, _shade(col, -45), (bx, by), 6)
        pygame.draw.circle(surf, col, (bx, by), 5)
        pygame.draw.circle(surf, _shade(col, 55),
                           (cx + s * 11, base_y - 10), 2)
        _bell(surf, bx, by, r=3)


# ── collar kit ────────────────────────────────────────────────────────────────
# Round-1 critique: lift EVERY tile to the costume standard — a scalloped /
# pointed collar with a bell at each point, on all ten. The two collar styles
# below both finish with a bell per point/lobe; the builder gives every jester
# one of them (no bare necks).

def _collar_belled(surf, cx, neck_y, gold, n=5, tilt=0):
    """Drooping POINTED collar: a fan of dagged triangle points hanging off the
    neck, a bell at the tip of each point. `tilt` shears the fan with the body
    lean so the collar hangs with the shoulders, not bolt-level."""
    span = (n - 1) / 2
    for i in range(n):
        s = i - span
        tx = int(cx + s * 13 + tilt * 0.4)
        ty = neck_y + 4 + int(abs(s) * 1.5)  # outer points hang a touch lower
        _poly(surf, gold, [(cx + int(tilt), neck_y), (tx - 6, ty + 15),
                           (tx + 6, ty + 15)], oc=_shade(gold, -60))
        # Lit inner facet per point for the per-panel shaded read.
        _poly(surf, _shade(gold, 45),
              [(cx + int(tilt), neck_y), (tx - 6, ty + 15), (tx, ty + 8)],
              oc=False)
        _bell(surf, tx, ty + 16, r=3, col=(240, 235, 200))


def _collar_scalloped(surf, cx, neck_y, col, r=22, lobes=9, tilt=0):
    """A scalloped ruff-style collar: a row of overlapping lobes ringing the
    neck with lit tops + a small dangling bell at each outer edge. `tilt`
    shears the ruff so it follows the leaning shoulders."""
    for i in range(lobes):
        t = i / (lobes - 1)
        lx = int(cx - r + 2 * r * t + tilt * 0.5)
        ly = int(neck_y + 5 + math.sin(t * math.pi) * -3 + (t - 0.5) * tilt * 0.4)
        rad = 8
        pygame.draw.circle(surf, _shade(col, -50), (lx, ly), rad)
        pygame.draw.circle(surf, col, (lx, ly), rad - 1)
        pygame.draw.circle(surf, _shade(col, 55), (lx - 2, ly - 2), 3)
    for s in (-1, 1):
        _bell(surf, int(cx + s * (r + 2) + tilt * 0.5), neck_y + 8, r=3,
              col=(240, 235, 200))


# ── belled curled-toe jester shoes + thumb-divided mitts ─────────────────────

def _jester_shoes(surf, cx, feet_y, sep, length, color, toe, *, lean=0):
    """Curled-toe pointed jester shoes with a bell on each toe — the costume
    standard on all ten (round-1 had plain shoes). `lean` cocks the stance so
    the weight reads on one leg."""
    for s in (-1, 1):
        bx = cx + s * sep + (lean if s > 0 else lean // 2)
        # Sole as a rounded wedge.
        sole = pygame.Rect(0, 0, length, 14)
        if s < 0:
            sole.topright = (bx + length // 3, feet_y)
        else:
            sole.topleft = (bx - length // 3, feet_y)
        pygame.draw.ellipse(surf, _shade(color, -55), sole)
        pygame.draw.ellipse(surf, color, sole.inflate(-3, -3))
        # Curled pointed toe sweeping up and out, ending in a bell.
        toe_base = (sole.right - 4, sole.centery) if s > 0 else (sole.left + 4,
                                                                 sole.centery)
        tipx = toe_base[0] + s * 11
        tipy = toe_base[1] - 12
        curl = [(toe_base[0], toe_base[1] + 4), (toe_base[0], toe_base[1] - 4),
                (toe_base[0] + s * 7, toe_base[1] - 9), (tipx, tipy)]
        pygame.draw.polygon(surf, toe, curl)
        pygame.draw.polygon(surf, _shade(toe, -55), curl, 2)
        _bell(surf, tipx, tipy, r=3)


def _mitt_thumb(surf, hand, gr, glove, *, side):
    """Add a single thumb-dividing line so the white mitt reads as a hand. The
    `_arm` glove already drew the round mitt; we just carve the thumb."""
    hx, hy = hand
    # Thumb nub on the inner side + a divider line so it reads as fingers-vs-
    # thumb rather than a featureless ball.
    tx = hx - side * (gr - 1)
    pygame.draw.circle(surf, glove, (tx, hy + 1), max(2, gr // 2))
    pygame.draw.circle(surf, _shade(glove, -55), (tx, hy + 1), max(2, gr // 2), 1)
    pygame.draw.line(surf, _shade(glove, -55),
                     (hx - side * gr // 2, hy - gr + 2),
                     (hx - side * gr // 3, hy + gr - 2), 1)


# ── the unified jester builder (fixed pose + plotting lean) ───────────────────
# Every variation funnels through ONE builder so the MIRRORED POSE is literally
# identical across all ten: die upper-LEFT, LEFT arm raised CUPPING the die,
# RIGHT arm hanging down with a bowed mitt. On top of that hard pose, a shared
# "plotting" LEAN breaks the round-1 bolt-upright symmetry: the head tilts ~5°,
# one shoulder drops, the hip cocks, weight rests on one leg.

def build_jester(surf, cx, feet_y, hand_up, *, dark, light, gold,
                 cap_fn, motif, collar, variant, skin=(255, 209, 169),
                 nose_col=(232, 72, 72), imp=False):
    """Draw ONE chunky court jester in the fixed mirrored presenting pose with a
    plotting body lean. `variant` selects the small face flavour layered on the
    shared naughty recipe. `imp` is a spec marker for the single horned-hood
    variant — its impish read is carried by the warmed charcoal-plum palette in
    the spec plus the soft bell-nub `cap_imp_hood`, so it needs no extra branch.

    Build bias: a SHORTER, ROUNDER chibi proportion (round-1 #1/#4 read best
    small; the lanky long-legged tiles were reined in)."""
    _ = imp  # palette/cap already encode the impish read; kept for spec clarity
    # COMMITTED plotting lean (round-2 still read at-attention on most figures).
    # The whole figure shifts weight onto the die-side (LEFT) leg: the hip cocks
    # hard toward the die, the die-side shoulder DROPS 7px, the OTHER hip rides
    # up, the trailing (right) knee bends inward, and the head cocks. This is now
    # a clear contrapposto plot-stance, not a gentle nudge.
    hip_dx = -6          # hip cocked toward the die side (harder than round-2)
    head_tilt = -8       # degrees; head cocks toward the die
    drop = 7             # the die-side (left) shoulder drops a full 7px

    hip_y = feet_y - 84  # shorter build than round-1's 92
    hip_cx = cx + hip_dx

    # Curled-toe belled shoes, weight planted on the LEFT (die-side) leg, the
    # trailing RIGHT foot set back and turned out.
    _jester_shoes(surf, cx, feet_y, 15, 24, _shade(dark, -10),
                  _shade(gold, 10), lean=5)
    # Two-tone HARLEQUIN hose. The weight leg (LEFT) is planted nearly straight
    # under the cocked hip; the trailing (RIGHT) leg sets back with a BENT KNEE
    # (a mid-point kicked inward) so the stance reads as weight-shifted, never a
    # symmetric T. The hip anchors differ in height to sell the cocked pelvis.
    _harlequin_leg(surf, (hip_cx - 9, hip_y + 2), (cx - 12, feet_y - 8), 12,
                   light, dark)
    _harlequin_leg(surf, (hip_cx + 11, hip_y - 2), (cx + 15, feet_y - 8), 11,
                   dark, light, knee=(cx + 4, hip_y + 26))

    neck_y = hip_y - 50
    _draw_costume(surf, hip_cx, hip_y, dark, light, gold, motif, lean=4)

    # POSE — the hard requirement, now with the lean baked in. The LEFT (die-
    # side) shoulder DROPS; its arm reaches up and the open mitt CUPS UNDER the
    # die. The RIGHT arm hangs down with a slight outward BOW so both hands read
    # in silhouette.
    l_sh = (hip_cx - 25, hip_y - 46 + drop)
    r_sh = (hip_cx + 25, hip_y - 50)
    _arm(surf, l_sh, hand_up, 8, dark, up=True)
    # Right arm bows outward to a visible down mitt.
    r_hand = (hip_cx + 34, hip_y - 4)
    _arm(surf, r_sh, r_hand, 8, light)
    _mitt_thumb(surf, r_hand, 7, (250, 250, 252), side=-1)

    # Collar — every jester gets a belled, pointed/scalloped collar (no bare
    # necks), sheared to follow the leaning shoulders.
    if collar == "scalloped":
        _collar_scalloped(surf, hip_cx, neck_y, _shade(light, 10), tilt=4)
    else:
        _collar_belled(surf, hip_cx, neck_y, gold, tilt=4)

    hr = 22
    # The head sits on the neck but tilts toward the die. We draw the head +
    # cap + face onto a small surface and rotate the whole cluster so the tilt
    # is real, not just shoved features. The neck shifts toward the dropped
    # (die-side) shoulder so the head sits OVER the weight leg, not centred.
    head_cx = hip_cx - 4
    hy_center = neck_y - hr
    cap_cols = (dark, light, gold, dark)
    _draw_tilted_head(surf, head_cx, hy_center, hr, skin, cap_fn, cap_cols,
                      variant, nose_col, head_tilt)


def _draw_tilted_head(surf, cx, cy, hr, skin, cap_fn, cap_cols, variant,
                      nose_col, tilt_deg):
    """Compose head + cap + naughty face on a scratch surface and rotate it by
    `tilt_deg` so the whole head cocks with the plotting lean. Drawing onto a
    padded scratch surface keeps the rotation clean and centred on the face."""
    pad = 70
    scratch = pygame.Surface((pad * 2, pad * 2), pygame.SRCALPHA)
    sx, sy = pad, pad
    _round_head(scratch, sx, sy, hr, skin, blush=False)
    # Cap BEFORE the face so droops never cover the eyes.
    cap_fn(scratch, sx, sy - hr, hr, cap_cols)
    naughty_face(scratch, sx, sy, hr, nose_col=nose_col, variant=variant)
    rot = pygame.transform.rotate(scratch, tilt_deg)
    surf.blit(rot, (cx - rot.get_width() // 2, cy - rot.get_height() // 2))


def _harlequin_leg(surf, hip, ankle, w, upper, lower, *, knee=None):
    """One two-tone harlequin leg: an upper band in `upper`, a lower band in
    `lower`, with a rounded cuff + a top-left rim. Replaces round-1's solid
    single-colour stick legs. Pass `knee` to BEND the leg at an explicit joint
    (the trailing weight-shifted leg) instead of running it straight."""
    if knee is not None:
        midx, midy = knee
    else:
        midx = (hip[0] + ankle[0]) // 2
        midy = (hip[1] + ankle[1]) // 2
    pygame.draw.line(surf, _shade(upper, -50), hip, (midx, midy), w + 3)
    pygame.draw.line(surf, _shade(lower, -50), (midx, midy), ankle, w + 3)
    pygame.draw.line(surf, upper, hip, (midx, midy), w)
    pygame.draw.line(surf, lower, (midx, midy), ankle, w)
    # Top-left rim on the planted (upper) band.
    pygame.draw.line(surf, _shade(upper, 35), (hip[0] - 1, hip[1]),
                     (midx - 1, midy), max(1, w // 3))
    # Banding seam ring + ankle cuff.
    pygame.draw.circle(surf, _shade(lower, -30), (midx, midy), w // 2 + 1)
    pygame.draw.circle(surf, _shade(lower, -40), ankle, w // 2 + 2)


def _draw_costume(surf, cx, hip_y, dark, light, gold, motif, *, lean=0):
    """The torso, varied by motif. Every motif now carries per-panel costume
    shading (a darker tone down one side of each panel + a lighter highlight
    strip) via `_facet_body`, plus a faint extra side-shadow band so the round-1
    flat blocks read sculpted. `lean` skews the silhouette slightly."""
    seam = (250, 248, 235)
    top = hip_y - 50
    lx = lean  # shoulder offset from the lean

    def _side_shadow(pts, side):
        """Darken one side of a panel so each panel reads dimensional."""
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
        band = pygame.Surface((maxx - minx + 2, maxy - miny + 2),
                              pygame.SRCALPHA)
        m = pygame.Surface(band.get_size(), pygame.SRCALPHA)
        pygame.draw.polygon(m, (255, 255, 255, 255),
                            [(p[0] - minx, p[1] - miny) for p in pts])
        w = maxx - minx
        if side < 0:
            rect = pygame.Rect(0, 0, w // 3 + 2, maxy - miny + 2)
        else:
            rect = pygame.Rect(w * 2 // 3, 0, w // 3 + 2, maxy - miny + 2)
        pygame.draw.rect(band, (0, 0, 0, 60), rect)
        band.blit(m, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        surf.blit(band, (minx, miny))

    if motif == "split":
        left = [(cx - 28, hip_y + 10), (cx, hip_y + 10),
                (cx + lx, top), (cx - 18 + lx, top)]
        right = [(cx, hip_y + 10), (cx + 28, hip_y + 10),
                 (cx + 18 + lx, top), (cx + lx, top)]
        _facet_body(surf, left, light)
        _side_shadow(left, -1)
        _facet_body(surf, right, dark)
        _side_shadow(right, 1)
        pygame.draw.line(surf, seam, (cx + lx, top + 2), (cx, hip_y + 8), 2)
    elif motif == "quartered":
        midy = (top + hip_y + 10) // 2
        quads = [((cx - 28, hip_y + 10), (cx, hip_y + 10), (cx, midy),
                  (cx - 23, midy), dark, -1),
                 ((cx, hip_y + 10), (cx + 28, hip_y + 10), (cx + 23, midy),
                  (cx, midy), light, 1),
                 ((cx - 23, midy), (cx, midy), (cx + lx, top),
                  (cx - 18 + lx, top), light, -1),
                 ((cx, midy), (cx + 23, midy), (cx + 18 + lx, top),
                  (cx + lx, top), dark, 1)]
        for *pts, col, side in quads:
            _facet_body(surf, list(pts), col)
            _side_shadow(list(pts), side)
        pygame.draw.line(surf, seam, (cx + lx, top + 2), (cx, hip_y + 8), 2)
        pygame.draw.line(surf, seam, (cx - 25, midy), (cx + 25, midy), 2)
    elif motif == "panels":
        base = [(cx - 28, hip_y + 10), (cx + 28, hip_y + 10),
                (cx + 18 + lx, top), (cx - 18 + lx, top)]
        _facet_body(surf, base, dark)
        _side_shadow(base, 1)
        for i in range(-2, 3, 2):
            px = cx + i * 11 + lx // 2
            pygame.draw.polygon(surf, light,
                                [(px - 4, hip_y + 9), (px + 4, hip_y + 9),
                                 (px + 3, top + 1), (px - 3, top + 1)])
            # Highlight strip + shadow edge per stripe panel.
            pygame.draw.line(surf, _shade(light, 45), (px - 3, hip_y + 8),
                             (px - 2, top + 2), 1)
            pygame.draw.line(surf, _shade(light, -45), (px + 3, hip_y + 8),
                             (px + 2, top + 2), 1)
    else:  # "scalloped" hem split body
        left = [(cx - 28, hip_y + 6), (cx, hip_y + 6),
                (cx + lx, top), (cx - 18 + lx, top)]
        right = [(cx, hip_y + 6), (cx + 28, hip_y + 6),
                 (cx + 18 + lx, top), (cx + lx, top)]
        _facet_body(surf, left, dark)
        _side_shadow(left, -1)
        _facet_body(surf, right, light)
        _side_shadow(right, 1)
        pygame.draw.line(surf, seam, (cx + lx, top + 2), (cx, hip_y + 6), 2)
        for i in range(-3, 4):
            hx = cx + i * 8
            col = light if (i + hip_y) % 2 else dark
            pygame.draw.circle(surf, _shade(col, -30), (hx, hip_y + 7), 5)
            pygame.draw.circle(surf, col, (hx, hip_y + 7), 4)
    # Gold belt buttons along the waist on every motif.
    for i in range(7):
        bx = cx - 21 + i * 7
        pygame.draw.circle(surf, _shade(gold, -55), (bx, hip_y + 6), 3)
        pygame.draw.circle(surf, gold, (bx, hip_y + 6), 3)
        pygame.draw.circle(surf, _shade(gold, 70), (bx - 1, hip_y + 5), 1)


# ── the floating power-up DIE (cupped, with a contact-glow) ──────────────────
# Same approved treatment as the clown sheet (pip-die, gold halo, rim light,
# bob, sparkles) but the round-1 flat grey drop-shadow under the die is GONE —
# replaced by a soft warm CONTACT-GLOW so the die reads as magically floating
# just above the cupped offering mitt, not casting a stone shadow in mid-air.

def draw_cupped_die(surf, cx, base_y, pulse, *, show_inset=False):
    cy = int(base_y + math.sin(pulse * 1.1) * 3)
    size = 40

    # Warm gold radial glow halo behind the die.
    glow_r = 42
    blit_glow(surf, cx, cy, glow_r, (255, 205, 85),
              alpha=120 + int(35 * (0.5 + 0.5 * math.sin(pulse * 1.3))))
    blit_glow(surf, cx, cy, glow_r - 16, (255, 245, 200), alpha=120)
    # Soft CONTACT-GLOW just under the die (where the cupped mitt sits) so the
    # float reads as magical levitation, not a dropped object's hard shadow.
    blit_glow(surf, cx, cy + size // 2 + 4, 18, (255, 226, 150),
              alpha=100 + int(40 * (0.5 + 0.5 * math.sin(pulse * 1.3))))

    # Reuse the approved die face but suppress its own baked cast-shadow by
    # drawing onto a scratch and skipping nothing — the face helper draws a
    # shadow; we instead draw the die WITHOUT it by painting over with a clean
    # halo. To keep the prop pixel-consistent we call the shared face drawer on
    # a scratch surface that has no shadow region beneath it.
    _draw_die_face_noshadow(surf, cx, cy, size, pips=HERO_PIPS)

    if show_inset:
        ins = 24
        ix, iy = cx + 40, cy - 36
        for k in range(4):
            t = k / 4
            ax = int(cx + (ix - cx) * t)
            ay = int(cy + (iy - cy) * t) - int(9 * math.sin(t * math.pi))
            pygame.draw.circle(surf, (250, 225, 150), (ax, ay), max(1, 3 - k))
        _draw_die_face_noshadow(surf, ix, iy, ins, number=27,
                                body=(255, 246, 224), pip_col=(190, 70, 40))

    for i in range(4):
        a = i * math.tau / 4 + pulse * 0.4
        rr = 30 + 4 * math.sin(pulse * 0.9 + i)
        sx = int(cx + math.cos(a) * rr)
        sy = int(cy + math.sin(a) * rr * 0.85)
        tw = 0.5 + 0.5 * math.sin(pulse * 2.0 + i * 1.7)
        al = int(110 + 130 * tw)
        sz = 3 + int(2 * tw)
        spark = pygame.Surface((sz * 4, sz * 4), pygame.SRCALPHA)
        c = (255, 244, 200, al)
        pygame.draw.line(spark, c, (sz * 2, 0), (sz * 2, sz * 4), 1)
        pygame.draw.line(spark, c, (0, sz * 2), (sz * 4, sz * 2), 1)
        pygame.draw.circle(spark, (255, 255, 230, al), (sz * 2, sz * 2), sz)
        surf.blit(spark, (sx - sz * 2, sy - sz * 2),
                  special_flags=pygame.BLEND_ADD)


def _draw_die_face_noshadow(surf, cx, cy, size, *, pips=None, number=None,
                            body=(252, 250, 244), pip_col=(44, 40, 58)):
    """The approved die face WITHOUT the flat grey cast-shadow ellipse (the
    contact-glow replaces it). Geometry/pips/rim are otherwise identical to the
    shared `_draw_die_face` so the prop stays pixel-consistent."""
    half = size // 2
    rect = pygame.Rect(cx - half, cy - half, size, size)
    br = size // 5
    pygame.draw.rect(surf, _shade(body, -70), rect, border_radius=br)
    inner = rect.inflate(-3, -3)
    pygame.draw.rect(surf, body, inner, border_radius=br)
    pygame.draw.rect(surf, _shade(body, 28),
                     pygame.Rect(inner.x, inner.y, inner.w, inner.h // 2),
                     border_radius=br)
    pygame.draw.line(surf, RIM, (inner.left + br, inner.top + 1),
                     (inner.right - br, inner.top + 1), 2)
    pygame.draw.line(surf, RIM, (inner.left + 1, inner.top + br),
                     (inner.left + 1, inner.bottom - br), 2)
    pygame.draw.rect(surf, _shade(body, -80), rect, 2, border_radius=br)
    if number is not None:
        f = pygame.font.SysFont(None, int(size * 0.72), bold=True)
        txt = f.render(str(number), True, pip_col)
        surf.blit(txt, (cx - txt.get_width() // 2, cy - txt.get_height() // 2))
    elif pips is not None:
        pr = max(2, size // 8)
        for fx, fy in _PIP_LAYOUT[pips]:
            px = rect.x + int(fx * size)
            py = rect.y + int(fy * size)
            pygame.draw.circle(surf, _shade(pip_col, -25), (px, py), pr)
            pygame.draw.circle(surf, pip_col, (px, py), pr - 1)
            pygame.draw.circle(surf, _shade(pip_col, 130), (px - 1, py - 1), 1)


# ── the ten jester variations ────────────────────────────────────────────────
# Deep two-tone split + gold accents; NO diamonds (those belong to the
# Harlequin). Round-2 rebalances OFF the purple/violet cluster: only ONE pure
# purple remains; the rest spread across distinct warm (ruby/gold, scarlet,
# orange) and cool (teal/cream, ocean, emerald, ice) families so the ten
# thumbnails read distinctly. Each carries the shared naughty recipe + lean;
# `variant` only tweaks the small face flavour (browcock / tongue).

JESTERS = [
    # 1 — classic 3-point, the reliable jester read; warm plum/lime kept as the
    # single purple anchor (shorter chibi build is the proportion north star).
    ("Plum & Lime", dict(
        dark=(96, 44, 150), light=(132, 218, 116), gold=(250, 205, 72),
        cap_fn=cap_three_point, motif="split", collar="belled",
        variant="plain")),
    # 2 — NOT-a-crown floppy four-point; ruby/cream warm family. Round-2 washed
    # out on the day sky, so the ruby is deepened to a darker mid-value and the
    # cream pulled off near-white toward a warm tan so the silhouette survives.
    ("Ruby & Cream", dict(
        dark=(158, 28, 48), light=(228, 206, 168), gold=(238, 186, 64),
        cap_fn=cap_four_point, motif="quartered", collar="scalloped",
        variant="browcock")),
    # 3 — TRUE two-eared donkey cap; royal-blue/gold (cool+warm).
    ("Royal Blue & Gold", dict(
        dark=(40, 78, 168), light=(248, 206, 88), gold=(252, 226, 130),
        cap_fn=cap_donkey, motif="panels", collar="belled",
        variant="plain")),
    # 4 — the NAUGHTY-FACE reference palette: teal/magenta, coxcomb crest.
    ("Teal & Magenta", dict(
        dark=(26, 134, 142), light=(224, 74, 152), gold=(250, 210, 90),
        cap_fn=cap_coxcomb, motif="split", collar="scalloped",
        variant="tongue")),
    # 5 — the single surviving IMPISH horned hood: charcoal-PLUM, soft nubs.
    ("Charcoal-Plum Imp", dict(
        dark=(58, 44, 64), light=(216, 70, 96), gold=(248, 206, 96),
        cap_fn=cap_imp_hood, motif="quartered", collar="belled",
        variant="tonguecock", imp=True)),
    # 6 — the COSTUME-QUALITY reference: violet/orange coxcomb (kept distinct as
    # the one violet, paired with a warm orange to break from #1's purple).
    ("Violet & Orange", dict(
        dark=(120, 58, 178), light=(246, 148, 58), gold=(250, 214, 96),
        cap_fn=cap_coxcomb, motif="panels", collar="scalloped",
        variant="tongue")),
    # 7 — emerald/gold warm-cool, classic 3-point (lifted off round-1 flat).
    ("Emerald & Gold", dict(
        dark=(28, 120, 76), light=(248, 206, 84), gold=(252, 224, 124),
        cap_fn=cap_three_point, motif="scalloped", collar="belled",
        variant="plain")),
    # 8 — wine/teal curled-bell hood (lankier round-1 legs reined in).
    ("Wine & Teal", dict(
        dark=(126, 32, 70), light=(56, 182, 182), gold=(250, 208, 86),
        cap_fn=cap_hood, motif="split", collar="scalloped",
        variant="browcock")),
    # 9 — COOL ice family pulled off the purple cluster: slate/ice four-point.
    # Round-2 washed out on the day sky; the slate is darkened to a deeper navy
    # mid-value and the ice pulled off near-white toward a cooler grey-blue so the
    # silhouette holds its value against the sky.
    ("Slate & Ice", dict(
        dark=(40, 66, 104), light=(176, 204, 226), gold=(244, 200, 78),
        cap_fn=cap_four_point, motif="panels", collar="belled",
        variant="plain")),
    # 10 — warm scarlet/gold three-point (was a 2nd horned hood; recast).
    ("Scarlet & Gold", dict(
        dark=(196, 52, 56), light=(250, 212, 96), gold=(246, 202, 92),
        cap_fn=cap_three_point, motif="quartered", collar="scalloped",
        variant="tongue")),
]


# ── per-cell gameplay scene (mirrored: die upper-LEFT) ───────────────────────

def render_cell(spec, idx, show_inset):
    """One tight day-clearing scene at SS supersample: sky + a sliver of grass
    + cast shadow, the chunky jester filling ~70-80% of the cell, the head-sized
    power-up die in the upper-LEFT focal slot CUPPED by the raised mitt, and the
    real parrot for scale. Returns VIEW_W x VIEW_H."""
    palette = shaped_palette(DAY_PHASE)
    bw, bh = VIEW_W * SS, VIEW_H * SS
    big = pygame.Surface((bw, bh))

    g_y = int(VIEW_FEET_Y * SS) + 6 * SS
    for y in range(g_y):
        t = 0.45 + 0.55 * (y / g_y)
        c = lerp_color(palette['sky_mid'], palette['sky_bot'], t)
        pygame.draw.line(big, c, (0, y), (bw, y))
    for y in range(g_y, bh):
        t = (y - g_y) / max(1, bh - g_y)
        c = lerp_color(palette['ground_top'], palette['ground_mid'], t)
        pygame.draw.line(big, c, (0, y), (bw, y))
    pygame.draw.line(big, _shade(palette['ground_top'], 15), (0, g_y), (bw, g_y))

    hill = pygame.Surface((bw, 30 * SS), pygame.SRCALPHA)
    hc = _shade(palette['ground_mid'], 22)
    for hx, hw, hh in ((40, 90, 18), (130, 110, 22), (185, 80, 16)):
        pygame.draw.ellipse(hill, (*hc, 160),
                            ((hx - hw) * SS, 0, hw * 2 * SS, hh * 2 * SS))
    big.blit(hill, (0, g_y - 14 * SS))
    tuft = _shade(palette['ground_top'], 22)
    rng = __import__('random').Random(idx * 131 + 7)
    for _ in range(10):
        tx = rng.randint(8, VIEW_W - 8) * SS
        ty = g_y + rng.randint(3, max(4, bh // SS - VIEW_FEET_Y - 4)) * SS
        for k in (-3, 0, 3):
            pygame.draw.line(big, tuft, (tx + k * SS, ty),
                             (tx + k * SS, ty - rng.randint(4, 7) * SS),
                             max(1, SS))

    layer = pygame.Surface((VIEW_W, VIEW_H), pygame.SRCALPHA)
    # Figure nudged RIGHT of centre so the die has clear sky in the upper-LEFT
    # to float in, fully off the head silhouette (mirror of the original).
    jester_cx = VIEW_W // 2 + 12
    feet_y = VIEW_FEET_Y
    _shadow(layer, jester_cx, feet_y, 96)

    # The die floats in the clear UPPER-LEFT; the raised LEFT mitt CUPS UNDER it.
    # The hand target sits just below the die so the open palm cradles it and
    # the gap from round-1 closes ("offering", not "pointing near").
    die_x = jester_cx - 66
    die_base_y = 50
    hand_up = (die_x + 6, die_base_y + 26)

    build_jester(layer, jester_cx, feet_y, hand_up, **spec)

    pulse = idx * 1.7 + 2.0
    draw_cupped_die(layer, die_x, die_base_y, pulse, show_inset=show_inset)

    # Real parrot flying in low from the RIGHT for scale, clear of the figure
    # and the upper-left die.
    bird = get_parrot(1, -10)
    bird = pygame.transform.smoothscale(
        bird, (int(bird.get_width() * 0.92), int(bird.get_height() * 0.92)))
    layer.blit(bird, (VIEW_W - 22 - bird.get_width() // 2,
                      (feet_y - 64) - bird.get_height() // 2))

    big.blit(pygame.transform.smoothscale(layer, (bw, bh)), (0, 0))
    return pygame.transform.smoothscale(big, (VIEW_W, VIEW_H))


CAPTIONS = [
    "plum/lime · 3-point cap · V-brow sidelong up-smirk",
    "ruby/cream · SPLAYED 4-point · cocked V-brow smirk",
    "royal-blue/gold · donkey-EAR cap · V-brow up-smirk",
    "teal/magenta · ANCHORED coxcomb · V-brow + tongue",
    "charcoal-plum · IMPISH horned hood · V-brow + tongue",
    "violet/orange · ANCHORED coxcomb · V-brow + tongue",
    "emerald/gold · 3-point cap · V-brow sidelong smirk",
    "wine/teal · curled-bell hood · cocked V-brow smirk",
    "slate/ice · SPLAYED 4-point · V-brow up-smirk",
    "scarlet/gold · 3-point cap · V-brow smirk + tongue",
]


def main():
    pygame.init()
    pygame.font.init()
    pygame.display.set_mode((W, H))

    cols, rows = 5, 2
    sw, sh = int(VIEW_W * 1.88), int(VIEW_H * 1.88)

    PAD = 44
    GAP = 22
    TITLE_H = 92
    CAP_H = 64
    FOOT_H = VIEW_H + 28

    canvas_w = PAD * 2 + cols * sw + (cols - 1) * GAP
    canvas_h = (PAD * 2 + TITLE_H + rows * (sh + CAP_H) + (rows - 1) * GAP
                + FOOT_H)
    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((24, 22, 30))

    f_title = pygame.font.SysFont(None, 70, bold=True)
    f_sub = pygame.font.SysFont(None, 32, bold=True)
    f_cap = pygame.font.SysFont(None, 38, bold=True)
    f_caps = pygame.font.SysFont(None, 28, bold=True)

    title = f_title.render("COURT JESTER — naughty dice presenter (round 4)",
                           True, (250, 240, 210))
    canvas.blit(title, (PAD, PAD - 2))
    sub = f_sub.render(
        "FACE PASS: inner-HIGH/outer-LOW scheming V brows + FLAT sidelong almond "
        "eyes (tear streaks & watery dots removed) + committed lopsided up-smirk "
        "on all 10 · everything below the chin unchanged (ship-ready)",
        True, (190, 195, 205))
    canvas.blit(sub, (PAD, PAD + 50))

    # Show the rolled-result inset in a couple of cells to hint the mechanic.
    inset_cells = {0, 9}

    y0 = PAD + TITLE_H
    template_cell = None
    for i, (name, spec) in enumerate(JESTERS):
        r, c = divmod(i, cols)
        cx = PAD + c * (sw + GAP)
        cy = y0 + r * (sh + CAP_H + GAP)
        cell = render_cell(spec, i, show_inset=(i in inset_cells))
        if i == 3:  # Teal & Magenta — the naughty-face reference; use for inset.
            template_cell = cell
        scaled = pygame.transform.smoothscale(cell, (sw, sh))
        pygame.draw.rect(canvas, (70, 76, 96),
                         pygame.Rect(cx - 1, cy - 1, sw + 2, sh + 2), 1)
        canvas.blit(scaled, (cx, cy))
        cap = f_cap.render(f"{i + 1}. {name}", True, (235, 225, 165))
        canvas.blit(cap, (cx + (sw - cap.get_width()) // 2, cy + sh + 6))
        sub2 = f_caps.render(CAPTIONS[i], True, (190, 196, 206))
        canvas.blit(sub2, (cx + (sw - sub2.get_width()) // 2, cy + sh + 38))

    # ONE 1x legibility inset proving the design reads at in-game scale.
    if template_cell is not None:
        foot_y = y0 + rows * (sh + CAP_H) + (rows - 1) * GAP + 14
        ix = PAD
        pygame.draw.rect(canvas, (70, 76, 96),
                         pygame.Rect(ix - 2, foot_y - 2, VIEW_W + 4,
                                     VIEW_H + 4), 1)
        canvas.blit(template_cell, (ix, foot_y))
        tag = f_cap.render(
            "1x in-game scale (Teal & Magenta) — inner-high V brows + flat "
            "sidelong eyes + lopsided up-smirk read as UP TO SOMETHING; no tears",
            True, (200, 206, 216))
        canvas.blit(tag, (ix + VIEW_W + 24, foot_y + VIEW_H // 2 - 14))

    out_dir = os.path.join("docs", "jester")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_4.png")
    pygame.image.save(canvas, out_path)
    print(f"saved {out_path}  ({canvas_w}x{canvas_h})")


if __name__ == "__main__":
    main()
