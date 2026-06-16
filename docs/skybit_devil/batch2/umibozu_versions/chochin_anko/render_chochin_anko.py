"""Look-dev sheet for the Skybit BOSS — "CHOCHIN-ANKO" (Umibozu-versions #1).

The abyssal anglerfish lure-fiend: a deep-sea spin-off off the shipped Umibozu,
but a DISJOINT kind — lure-on-a-stalk, not the jelly-dome. A perpetually-annoyed
oil-black grump-head all jaw and needle-teeth, wagging a single nightlight on a
long illicium stalk. The whole creature reads near-silhouette DARK so the one
glowing esca lure-bulb is the SOLE true focal — the brightest pip on the sheet.

House style this obeys (the elevated "epic" Umibozu-lane grammar):
  - CHIBI proportions — one oversized rounded grump-head dominating; the body is
    almost all maw + the illicium stalk. No torso/limbs.
  - FLAT saturated fills + a hard 1-2px ink keyline. No within-shape gradients,
    no soft/feathered edges, no bevels.
  - Form via the TRIAD: dark-core ring -> flat fill -> top-left rim sheen lobe.
  - Scary-CUTE not grim: a deep grump scowl + cute underbite, the needle-maw
    endless but chibi-blunt; annoyed, never a gore-snarl.
  - Silhouette POP via a 1px ink keyline grown from the alpha mask.
  - EPIC pass: render BIG at SS=5, then smoothscale down for a crisp downscale.

Palette read (pinned in brief): OIL-BLACK body (value-low, near silhouette) so a
single hot-white-peach lure is the only focal. Blood-CORAL is BELLY/GUM ONLY —
never a body wash — so it can't twin sibling Akkorokamui's red lane. Cold-steel
sheen for the top-left rim. The accessibility tell is the dark mass + the lone
warm lure pip, not hue.

Prop -> pillar mirror: the illicium STALK is the pillar. A tileable segmented
filament (knuckle-node per repeat + barbel-feelers) = the repeatable PILLAR BODY;
the glowing esca lure-bulb (~shaft+30%) = the detachable GAP-EDGE CAP that
radiates hot-white-peach INTO the gap. Naturally vertical — clean mirror.

    SDL_VIDEODRIVER=dummy PYTHONPATH=/home/user/skybit \
        python docs/skybit_devil/batch2/umibozu_versions/chochin_anko/render_chochin_anko.py
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.draw import _shade_c, lerp_color, make_glow_surface
from game.config import PIPE_W


pygame.init()

# ── PINNED PALETTE (chochin-anko) ────────────────────────────────────────────
# Oil-black body — the lowest value mass on the sheet so the single lure pip is
# the only true focal. Charcoal shade carves the dark-core rings and hollows.
BODY        = (38, 52, 58)      # oil-black fill (deep cool grey-teal)
BODY_DK     = (22, 32, 38)      # charcoal shade (dark-core ring / hollows)
BODY_DEEP   = (16, 24, 28)      # near-black base (the deepest maw void)
SHEEN       = (150, 170, 176)   # cold-steel rim sheen (top-left lit lobe)

# Blood-CORAL — BELLY + GUM flush ONLY, never a full-body wash (keeps it off
# Akkorokamui's red lane). A contained warm accent inside the maw + low belly.
CORAL       = (196, 86, 72)     # blood-coral gum/belly flush
CORAL_DK    = (132, 48, 44)     # coral dark-core ring

# Hot-white-peach lure glow — the SOLE brightest pip on the whole creature.
LURE        = (255, 224, 168)   # esca lure glow fill
LURE_CORE   = (255, 246, 224)   # hot twinkle core inside the bulb
LURE_DK     = (210, 158, 96)    # lure dark-seat ring

TEETH       = (224, 226, 222)   # needle-teeth (cold near-white, kept tiny)
INK         = (20, 26, 30)      # the house keyline
# Night keyline: a lifted cold-steel rim so the oil-black silhouette survives on
# the midnight-blue sky (dark ink would vanish there); grown 2px on night.
INK_NIGHT   = (172, 198, 204)


def _triad_circle(surf, cx, cy, r, col, *, sheen=True, sheen_d=34, sheen_col=None,
                  sheen_scale=0.30):
    """House form triad on a circle: dark-core ring -> flat fill -> top-left rim
    sheen. Sculpted volume while staying flat-shaded. `sheen_col` overrides the
    sheen so the cold-steel highlight can be used instead of a tinted fill."""
    pygame.draw.circle(surf, _shade_c(col, -16), (int(cx), int(cy)), int(r))
    pygame.draw.circle(surf, col, (int(cx), int(cy)),
                       max(1, int(r - max(1, r * 0.06))))
    if sheen:
        sc = sheen_col if sheen_col is not None else _shade_c(col, sheen_d)
        pygame.draw.circle(surf, sc,
                           (int(cx - r * 0.34), int(cy - r * 0.36)),
                           max(2, int(r * sheen_scale)))


def _add_outline(src, outline_color=(*INK, 235), width=1):
    """Grow a keyline from the alpha mask so the silhouette POPS on any sky (the
    parrot `_add_outline` recipe). On night the keyline is a lifted cold-steel
    tone, not dark ink, AND grown thicker so the dark body edge survives on the
    dark sky by shape. Returns a padded surface."""
    w, h = src.get_size()
    pad = width + 1
    out = pygame.Surface((w + pad * 2, h + pad * 2), pygame.SRCALPHA)
    mask = pygame.mask.from_surface(src, threshold=8)
    sil = mask.to_surface(setcolor=outline_color, unsetcolor=(0, 0, 0, 0))
    offs = [(dx, dy) for dx in range(-width, width + 1)
            for dy in range(-width, width + 1) if (dx, dy) != (0, 0)]
    for dx, dy in offs:
        out.blit(sil, (pad + dx, pad + dy))
    out.blit(src, (pad, pad))
    return out


def _esca(surf, cx, cy, r, ss, *, night=False, glow=True, glow_mult=1.0):
    """The esca LURE-BULB — the SOLE brightest pip. A hot-white-peach disc with a
    dark-seat ring + hot twinkle core, wrapped in a contained radial glow that
    radiates INTO the gap. This is the one warm focal; everything else stays dark
    so the eye lands here first at 32px."""
    if glow:
        gr = int(r * (3.6 if night else 2.7) * glow_mult)
        gl = make_glow_surface(max(1, gr), LURE,
                               alpha_center=210 if night else 150, falloff=2.0)
        surf.blit(gl, (int(cx - gr), int(cy - gr)), special_flags=pygame.BLEND_ADD)
    pygame.draw.circle(surf, LURE_DK, (int(cx), int(cy)), max(1, int(r)))
    pygame.draw.circle(surf, LURE, (int(cx), int(cy)), max(1, int(r * 0.80)))
    pygame.draw.circle(surf, LURE_CORE, (int(cx), int(cy)), max(1, int(r * 0.40)))


def _filament_segment(surf, x0, y0, x1, y1, hw, ss, *, col=BODY, knuckle=False,
                      feelers=0, night=False):
    """One segment of the illicium STALK: a tapering oil-black cord drawn as a
    hard flat triad (dark-core -> fill -> cold-steel sheen stripe). A swollen
    knuckle-NODE optionally sits at the segment join (the per-repeat tell); short
    barbel-FEELERS optionally branch off so the stalk reads organic, not a hose."""
    dx, dy = x1 - x0, y1 - y0
    seg_len = math.hypot(dx, dy) or 1.0
    # Perpendicular unit vector for thickness.
    px, py = -dy / seg_len, dx / seg_len
    quad = [(x0 + px * hw, y0 + py * hw), (x1 + px * hw, y1 + py * hw),
            (x1 - px * hw, y1 - py * hw), (x0 - px * hw, y0 - py * hw)]
    pygame.draw.polygon(surf, _shade_c(col, -16),
                        [(int(x), int(y)) for x, y in quad])
    inner = [(x0 + px * (hw - ss), y0 + py * (hw - ss)),
             (x1 + px * (hw - ss), y1 + py * (hw - ss)),
             (x1 - px * (hw - ss), y1 - py * (hw - ss)),
             (x0 - px * (hw - ss), y0 - py * (hw - ss))]
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in inner])
    # Cold-steel sheen stripe down the lit (top-left) edge of the cord.
    sheen_a = (x0 + px * (hw - ss * 1.4), y0 + py * (hw - ss * 1.4))
    sheen_b = (x1 + px * (hw - ss * 1.4), y1 + py * (hw - ss * 1.4))
    pygame.draw.line(surf, _shade_c(SHEEN, 30 if night else 0),
                     (int(sheen_a[0]), int(sheen_a[1])),
                     (int(sheen_b[0]), int(sheen_b[1])), max(1, int(1.1 * ss)))

    # Barbel-FEELERS: thin tapering whiskers branching off the cord, a couple per
    # marked segment, kept oil-black so they never compete with the lure.
    for k in range(feelers):
        side = -1 if k % 2 == 0 else 1
        t = 0.35 + 0.4 * (k / max(1, feelers - 1) if feelers > 1 else 0.5)
        bx = x0 + dx * t + px * hw * side
        by = y0 + dy * t + py * hw * side
        flen = hw * (2.4 + 0.5 * k)
        droop = hw * 1.1
        ex = bx + px * side * flen * 0.7
        ey = by + abs(dy / seg_len) * flen * 0.5 + droop
        pygame.draw.line(surf, _shade_c(col, -8),
                         (int(bx), int(by)), (int(ex), int(ey)),
                         max(1, int(1.3 * ss)))
        # A tiny dark bead at the feeler tip (a sensory papilla).
        pygame.draw.circle(surf, _shade_c(col, -20), (int(ex), int(ey)),
                           max(1, int(hw * 0.22)))

    # Knuckle-NODE: a swollen triad bead at the join — the per-repeat cadence mark.
    if knuckle:
        _triad_circle(surf, x1, y1, hw * 1.5, col,
                      sheen_col=_shade_c(SHEEN, 26 if night else 0),
                      sheen_scale=0.26)


# ── the illicium stalk (creature spine + pillar body) ────────────────────────

def _illicium(surf, top_x, top_y, length, hw, ss, *, night=False, n_seg=4,
              wave=0.0, phase=0.0, tip_lure=False):
    """The illicium STALK: a segmented oil-black filament running down `length`,
    a swollen knuckle-NODE per segment join + barbel-feelers branching off — the
    repeatable pillar cadence. `wave` lets the creature's stalk drift; the pillar
    passes wave=0 so the shaft tiles straight. `tip_lure` drops an esca at the
    tip (the hero's wagged nightlight)."""
    def _x_at(t):
        return top_x + wave * hw * 2.0 * math.sin(t * math.pi * 1.8 + phase) * (0.2 + 0.8 * t)

    pts = []
    for i in range(n_seg + 1):
        t = i / n_seg
        pts.append((_x_at(t), top_y + length * t, hw * (1.0 - 0.30 * t)))

    for i in range(n_seg):
        x0, y0, w0 = pts[i]
        x1, y1, w1 = pts[i + 1]
        _filament_segment(surf, x0, y0, x1, y1, (w0 + w1) * 0.5, ss,
                           col=BODY if i % 2 == 0 else _shade_c(BODY, -6),
                           knuckle=(i < n_seg - 1),
                           feelers=2 if i % 2 == 0 else 1, night=night)

    if tip_lure:
        ex, ey, ew = pts[-1]
        _esca(surf, ex, ey, max(3, ew * 1.7), ss, night=night)


# ── the perpetually-annoyed grump-head + needle-maw ──────────────────────────

def _head(surf, cx, cy, r, ss, *, night=False, tell=False):
    """The oversized chibi anglerfish grump-head: a rounded oil-black skull, a
    huge underbite maw split low across the face with marching needle-teeth, a
    blood-coral gum/belly flush CONTAINED inside the maw + low jaw, an annoyed
    scowling brow over two small grump-eyes, and the illicium stub rising from the
    pate. Near-silhouette DARK so the lure (not the face) is the only warm focal.
    `tell` bakes a bolder low-res maw + brow for the 32px read."""
    body = _shade_c(BODY, 12) if night else BODY
    sheen = _shade_c(SHEEN, 30) if night else SHEEN

    # Lower jaw bulge first (the heavy underbite) — occluded by the upper skull.
    jaw = pygame.Rect(0, 0, int(r * 1.92), int(r * 1.30))
    jaw.center = (int(cx), int(cy + r * 0.50))
    pygame.draw.ellipse(surf, _shade_c(body, -16), jaw)
    pygame.draw.ellipse(surf, body, jaw.inflate(-int(r * 0.10), -int(r * 0.10)))

    # Upper skull dome triad — a broad rounded grump-head. Sheen suppressed here;
    # one dedicated cold-steel crescent below carries the pate highlight.
    _triad_circle(surf, cx, cy, r * 1.06, body, sheen=False)

    # ONE hard cold-steel rim-sheen crescent on the top-left pate (lit disc minus
    # a body-colored bite so it reads as a single clean crescent, no dent).
    sc_x, sc_y, sc_r = cx - r * 0.36, cy - r * 0.44, r * 0.30
    pygame.draw.circle(surf, _shade_c(sheen, 8), (int(sc_x), int(sc_y)),
                       max(2, int(sc_r)))
    pygame.draw.circle(surf, body,
                       (int(sc_x + sc_r * 0.50), int(sc_y + sc_r * 0.46)),
                       max(2, int(sc_r * 0.86)))

    # — The needle-MAW: a wide upward-curving grin split low across the face. The
    #   deep void is near-black; a blood-coral GUM flush lines it (contained warm,
    #   never a body wash). Two rows of small near-white needle-teeth interlock.
    maw_w = r * 1.46
    maw_y = cy + r * 0.40
    maw_h = r * 0.62
    # Maw void — a fat lens shape (upper arc + lower arc) so the underbite reads.
    top_arc, bot_arc = [], []
    steps = 26
    for i in range(steps + 1):
        t = i / steps
        ax = cx - maw_w + 2 * maw_w * t
        # Upper lip dips slightly (annoyed); lower jaw bows down deep (underbite).
        ay_top = maw_y - math.sin(t * math.pi) * r * 0.05
        ay_bot = maw_y + math.sin(t * math.pi) * maw_h
        top_arc.append((ax, ay_top))
        bot_arc.append((ax, ay_bot))
    maw_poly = top_arc + bot_arc[::-1]
    pygame.draw.polygon(surf, BODY_DEEP, [(int(x), int(y)) for x, y in maw_poly])
    # Blood-coral gum flush hugging the inside rim of the maw (contained accent).
    gum = _shade_c(CORAL, -14) if night else CORAL
    gum_in = []
    for (tx, ty), (bx, by) in zip(top_arc, bot_arc):
        gum_in.append((tx, ty + (by - ty) * 0.30))
    for (tx, ty), (bx, by) in list(zip(top_arc, bot_arc))[::-1]:
        gum_in.append((bx, by - (by - ty) * 0.22))
    pygame.draw.polygon(surf, _shade_c(gum, -34),
                        [(int(x), int(y)) for x, y in gum_in])
    # Re-cut the central void so the coral reads as a rim-lining gum, not a fill.
    inner_void = []
    for (tx, ty), (bx, by) in zip(top_arc, bot_arc):
        inner_void.append((tx, ty + (by - ty) * 0.34))
    for (tx, ty), (bx, by) in list(zip(top_arc, bot_arc))[::-1]:
        inner_void.append((bx, by - (by - ty) * 0.30))
    pygame.draw.polygon(surf, BODY_DEEP,
                        [(int(x), int(y)) for x, y in inner_void])

    # Needle-TEETH: two interlocking rows of small near-white triangles. Kept tiny
    # + cold so they never out-bright the lure — the cute-scary endless maw.
    n_teeth = 9
    for i in range(n_teeth):
        t = (i + 0.5) / n_teeth
        ax = cx - maw_w * 0.86 + 2 * maw_w * 0.86 * t
        ay_top = maw_y - math.sin(t * math.pi) * r * 0.05
        ay_bot = maw_y + math.sin(t * math.pi) * maw_h
        th = (ay_bot - ay_top) * 0.30
        tw = maw_w * 0.07
        # Upper row points DOWN.
        pygame.draw.polygon(surf, TEETH, [
            (int(ax - tw), int(ay_top)), (int(ax + tw), int(ay_top)),
            (int(ax), int(ay_top + th))])
        # Lower row points UP (interlocking, offset).
        if i < n_teeth - 1:
            ax2 = ax + maw_w * 0.86 / n_teeth
            t2 = (i + 1.0) / n_teeth
            ay_bot2 = maw_y + math.sin(t2 * math.pi) * maw_h
            pygame.draw.polygon(surf, _shade_c(TEETH, -18), [
                (int(ax2 - tw), int(ay_bot2)), (int(ax2 + tw), int(ay_bot2)),
                (int(ax2), int(ay_bot2 - th))])

    # — Eyes: two small GRUMP eyes set high + close, half-lidded with a heavy
    #   annoyed top lid. Tiny cold-steel catchlights, no warm (lure owns warm).
    eye_dx = r * 0.40
    eye_y = cy - r * 0.06
    eye_r = r * 0.20
    for s in (-1, 1):
        ex = cx + s * eye_dx
        pygame.draw.circle(surf, BODY_DEEP, (int(ex), int(eye_y)), max(2, int(eye_r)))
        pygame.draw.circle(surf, _shade_c(body, 30),
                           (int(ex), int(eye_y)), max(1, int(eye_r * 0.62)))
        # Heavy annoyed top lid — a dark cap clipping the upper half of the eye.
        lid = pygame.Rect(0, 0, int(eye_r * 2.6), int(eye_r * 2.0))
        lid.center = (int(ex), int(eye_y - eye_r * 1.05))
        pygame.draw.ellipse(surf, body, lid)
        # Cold-steel catchlight glint.
        pygame.draw.circle(surf, SHEEN,
                           (int(ex - eye_r * 0.28), int(eye_y - eye_r * 0.18)),
                           max(1, int(eye_r * 0.22)))

    # — Brow: two steep inward-angled scowl bars (the perpetual deep grump).
    bw = max(2, int(2.2 * ss))
    for s in (-1, 1):
        inner = (cx + s * r * 0.10, eye_y - r * 0.30)
        outer = (cx + s * r * 0.62, eye_y - r * 0.46)
        pygame.draw.line(surf, BODY_DEEP, (int(inner[0]), int(inner[1])),
                         (int(outer[0]), int(outer[1])), bw)

    if tell:
        # Baked low-res tell so the 32px icon keeps a creature read: a bold dark
        # maw bar with two coral gum nicks + a heavy scowl V over two eye-dabs.
        pygame.draw.line(surf, BODY_DEEP, (int(cx - maw_w * 0.8), int(maw_y)),
                         (int(cx + maw_w * 0.8), int(maw_y + maw_h * 0.4)),
                         max(3, int(3.0 * ss)))
        for s in (-1, 1):
            pygame.draw.circle(surf, BODY_DEEP,
                               (int(cx + s * eye_dx), int(eye_y)),
                               max(2, int(eye_r * 1.1)))


# ── the whole creature: grump-head + wagged illicium nightlight ───────────────

def build_chochin(scale=1.0, ss=5, *, night=False, compact=False):
    """The full creature on a transparent surface: the oil-black grump-head with
    its needle-maw, and the illicium stalk arcing up off the pate to dangle the
    glowing esca lure in front of the face — the wagged nightlight. EPIC pass
    renders BIG at SS then smoothscales. `compact` is the gameplay/32px variant:
    head grown to dominate, stalk shortened, a baked low-res tell."""
    head_r = int(46 * scale) * ss
    side_pad = int(20 * scale) * ss
    top_pad = int(18 * scale) * ss
    bot_pad = int(16 * scale) * ss

    # The illicium arcs UP and FORWARD off the pate, then the lure hangs in front
    # of the face. In compact the arc is tucked tighter so the head dominates.
    stalk_len = head_r * (1.6 if compact else 2.3)
    stalk_hw = head_r * 0.16

    # Layout: head sits low-ish; stalk sweeps up and over to the front-left so the
    # lure dangles before the maw. Reserve headroom for the arc + glow.
    head_cx = side_pad + head_r * 1.0
    head_cy = top_pad + stalk_len * 0.66 + head_r * 1.1

    W = int((side_pad + head_r * 2.2) * 1.18)
    H = int(head_cy + head_r * 1.5 + bot_pad)
    surf = pygame.Surface((W, H), pygame.SRCALPHA)

    # Build the arcing stalk as a chain of segments curving from the pate up-over
    # to a lure hanging in front of the face. Drawn BEFORE the head so the pate
    # occludes the stalk root (one continuous body).
    pate = (head_cx + head_r * 0.10, head_cy - head_r * 0.98)
    # Control the arc: up, over to the left-front, then down to the lure point.
    lure_pt = (head_cx - head_r * 0.46, head_cy - head_r * 0.10)
    apex = (head_cx + head_r * 0.30, head_cy - stalk_len)
    arc_pts = []
    n_seg = 5 if compact else 6
    for i in range(n_seg + 1):
        t = i / n_seg
        # Quadratic-ish bezier: pate -> apex -> lure.
        mx = (1 - t) ** 2 * pate[0] + 2 * (1 - t) * t * apex[0] + t ** 2 * lure_pt[0]
        my = (1 - t) ** 2 * pate[1] + 2 * (1 - t) * t * apex[1] + t ** 2 * lure_pt[1]
        hw = stalk_hw * (1.0 - 0.28 * t)
        arc_pts.append((mx, my, hw))
    for i in range(n_seg):
        x0, y0, w0 = arc_pts[i]
        x1, y1, w1 = arc_pts[i + 1]
        _filament_segment(surf, x0, y0, x1, y1, (w0 + w1) * 0.5, ss,
                           col=BODY if i % 2 == 0 else _shade_c(BODY, -6),
                           knuckle=(0 < i < n_seg - 1),
                           feelers=2 if i in (1, 3) else 0, night=night)

    _head(surf, head_cx, head_cy, head_r, ss, night=night, tell=compact)

    # The esca lure LAST + on top — the wagged nightlight, the sole bright pip.
    _esca(surf, lure_pt[0], lure_pt[1], head_r * 0.30, ss, night=night,
          glow_mult=1.05)

    out_w = int(surf.get_width() / ss)
    out_h = int(surf.get_height() / ss)
    smallv = pygame.transform.smoothscale(surf, (out_w, out_h))
    oc = (*INK_NIGHT, 245) if night else (*INK, 235)
    return _add_outline(smallv, outline_color=oc, width=2 if night else 1)


# ── pillar pair (prop -> pillar mirror proof) ────────────────────────────────

OVERHANG = 12


def _illicium_column(surf, cx, top_y, bot_y, span, ss, *, night=False):
    """The repeatable PILLAR BODY: the illicium stalk as a straight tiling shaft —
    a thick central oil-black filament with a swollen knuckle-NODE on a steady
    cadence and barbel-feelers branching off each node. Drawn vertical (no wave)
    so the band tiles cleanly top<->bottom."""
    length = bot_y - top_y
    hw = span * 0.30
    # One knuckle per repeat; cadence scales with length so it tiles to any height.
    n_seg = max(3, int(length / (hw * 4.2)))
    seg_h = length / n_seg
    for i in range(n_seg):
        y0 = top_y + seg_h * i
        y1 = top_y + seg_h * (i + 1)
        _filament_segment(surf, cx, y0, cx, y1, hw, ss,
                           col=BODY if i % 2 == 0 else _shade_c(BODY, -6),
                           knuckle=True, feelers=2, night=night)


def _esca_cap(surf, cx, cap_base_y, span, ss, *, point_up, night=False):
    """The detachable GAP-EDGE CAP: the glowing esca LURE-BULB (~shaft span +30%)
    on a short curved stub of stalk at the gap end, radiating hot-white-peach
    INTO the gap. `point_up` orients the stub so the bulb hangs toward the gap.
    Kept compact so the cap is never top-heavy vs the shaft — and it is the SOLE
    bright pip of the whole pillar."""
    d = -1 if point_up else 1
    hw = span * 0.26
    # A short stub of stalk curving off the shaft end toward the gap, ending in
    # the bulb. The stub is oil-black; only the bulb glows.
    stub_len = span * 1.30          # ~shaft +30%
    bx = cx + span * 0.18           # slight forward offset so the lure dangles
    by = cap_base_y + d * stub_len
    apex = (cx - span * 0.10, cap_base_y + d * stub_len * 0.5)
    pts = []
    n = 4
    for i in range(n + 1):
        t = i / n
        mx = (1 - t) ** 2 * cx + 2 * (1 - t) * t * apex[0] + t ** 2 * bx
        my = (1 - t) ** 2 * cap_base_y + 2 * (1 - t) * t * apex[1] + t ** 2 * by
        pts.append((mx, my, hw * (1.0 - 0.22 * t)))
    for i in range(n):
        x0, y0, w0 = pts[i]
        x1, y1, w1 = pts[i + 1]
        _filament_segment(surf, x0, y0, x1, y1, (w0 + w1) * 0.5, ss,
                           col=BODY, knuckle=(i == n - 2),
                           feelers=2 if i == 1 else 0, night=night)
    # The esca bulb at the stub tip — the warm focal that lanterns the gap.
    _esca(surf, bx, by, span * 0.30, ss, night=night, glow_mult=1.1)


def _illicium_pillar_obstacle(height, ss, *, flip, night=False):
    """One illicium-stalk PILLAR obstacle: the segmented filament fills the post
    and the glowing esca lure-bulb CAPS the GAP-facing edge, radiating INTO the
    gap. `flip=True` is the TOP pillar (cap at the bottom/gap edge, bulb hangs
    DOWN); `flip=False` is the BOTTOM pillar (cap at the top/gap edge, bulb rises
    UP). Both mirror the same stalk body — clean vertical, no top-heavy cap."""
    bw = (PIPE_W + 2 * OVERHANG) * ss
    bh = max(1, int(height)) * ss
    surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
    cx = bw // 2
    span = (PIPE_W - 8) * ss
    cap_band = int(56 * ss)
    if flip:
        _illicium_column(surf, cx, 0, bh - cap_band, span, ss, night=night)
        _esca_cap(surf, cx, bh - cap_band, span, ss, point_up=False, night=night)
    else:
        _illicium_column(surf, cx, cap_band, bh, span, ss, night=night)
        _esca_cap(surf, cx, cap_band, span, ss, point_up=True, night=night)
    out = pygame.transform.smoothscale(surf, (PIPE_W + 2 * OVERHANG, max(1, int(height))))
    oc = (*INK_NIGHT, 245) if night else (*INK, 235)
    return _add_outline(out, outline_color=oc, width=2 if night else 1)


# ── sheet composition ────────────────────────────────────────────────────────

def _label(surf, font, text, x, y, color=(238, 244, 244)):
    surf.blit(font.render(text, True, (0, 0, 0)), (x + 1, y + 1))
    surf.blit(font.render(text, True, color), (x, y))


def _sky(w, h, top, mid, bot, *, stars=False):
    s = pygame.Surface((w, h))
    for i in range(h):
        t = i / max(1, h - 1)
        if t < 0.5:
            c = lerp_color(top, mid, t / 0.5)
        else:
            c = lerp_color(mid, bot, (t - 0.5) / 0.5)
        pygame.draw.line(s, c, (0, i), (w, i))
    if stars:
        import random as _r
        rng = _r.Random(99)
        for _ in range(26):
            sx = rng.randint(0, w - 1)
            sy = rng.randint(0, int(h * 0.7))
            pygame.draw.circle(s, (220, 230, 255), (sx, sy), rng.choice((1, 1, 2)))
    return s


def _to_gray(src):
    g = pygame.Surface(src.get_size(), pygame.SRCALPHA)
    g.blit(src, (0, 0))
    arr = pygame.surfarray.pixels3d(g)
    lum = (arr[:, :, 0] * 0.3 + arr[:, :, 1] * 0.59 + arr[:, :, 2] * 0.11).astype("uint8")
    arr[:, :, 0] = lum
    arr[:, :, 1] = lum
    arr[:, :, 2] = lum
    del arr
    return g


def main():
    pygame.font.init()
    font = pygame.font.SysFont("dejavusans", 15, bold=True)
    small = pygame.font.SysFont("dejavusans", 12)

    SW, SH = 1040, 770
    sheet = pygame.Surface((SW, SH))
    sheet.fill((46, 50, 54))          # neutral grey bg
    _label(sheet, font,
            "CHOCHIN-ANKO  —  Umibozu-versions #1  —  abyssal anglerfish lure-fiend (ANCHOR)  —  round 1", 18, 12)
    _label(sheet, small,
            "Oil-black grump-head + needle-maw (coral GUM only) wagging the esca lure on a segmented illicium stalk. Body near-silhouette DARK; the lure is the SOLE bright pip.",
            18, 32, (200, 214, 218))

    # — Cell A: BIG hero, on an abyssal cool sky.
    panel = pygame.Rect(18, 56, 320, 660)
    bgA = _sky(panel.w, panel.h, (14, 26, 38), (20, 44, 56), (34, 78, 86))
    sheet.blit(bgA, panel.topleft)
    pygame.draw.rect(sheet, (90, 130, 134), panel, 2, border_radius=8)
    hero = build_chochin(scale=1.7, ss=5)
    sheet.blit(hero, (panel.centerx - hero.get_width() // 2, panel.y + 64))
    _label(sheet, font, "(a) HERO  big scale (SS=5)", panel.x + 8, panel.y + 8)
    _label(sheet, small, "annoyed grump + underbite needle-maw + wagged nightlight",
           panel.x + 8, panel.y + 28, (200, 226, 222))

    # — Cell B: illicium as a tileable PILLAR pair at TRUE obstacle scale (night),
    #   plus a 2x zoom on the cap band proving the esca bulb lanterns the gap.
    panelB = pygame.Rect(352, 56, 330, 660)
    bg = _sky(panelB.w, panelB.h, (6, 12, 22), (10, 22, 38), (16, 42, 52), stars=True)
    sheet.blit(bg, panelB.topleft)
    pygame.draw.rect(sheet, (90, 130, 134), panelB, 2, border_radius=8)
    _label(sheet, font, "(b) PILLAR  @ TRUE scale  (NIGHT)", panelB.x + 8, panelB.y + 8)
    _label(sheet, small, "segmented stalk tiles (knuckle-node + feelers) + esca cap (~shaft+30%)",
           panelB.x + 8, panelB.y + 28, (200, 226, 222))

    pw = PIPE_W + 2 * OVERHANG
    slice_h = 540
    slice_x = panelB.x + 22
    slice_y = panelB.y + 50
    gap_top = 178
    gap_h = 132
    top_h = gap_top
    bot_h = slice_h - gap_top - gap_h
    top_pillar = _illicium_pillar_obstacle(top_h, 4, flip=True, night=True)
    bot_pillar = _illicium_pillar_obstacle(bot_h, 4, flip=False, night=True)
    sheet.blit(top_pillar, (slice_x - 2, slice_y - 2))
    sheet.blit(bot_pillar, (slice_x - 2, slice_y + gap_top + gap_h - 2))
    pygame.draw.rect(sheet, (170, 200, 204), (slice_x - 4, slice_y - 4, pw + 8, slice_h + 8), 1)
    _label(sheet, small, "1x native (82px): stalk", slice_x - 2, slice_y + slice_h + 6, (200, 226, 222))
    _label(sheet, small, "tiles; esca lanterns gap", slice_x - 2, slice_y + slice_h + 22, (255, 224, 168))

    # 2x zoom of the cap band — top<->bottom mirror visible.
    cap_band = 56
    zw, zh = pw, 180
    zoom_src = pygame.Surface((zw, zh), pygame.SRCALPHA)
    top_anchor = 14
    zoom_src.blit(top_pillar, (-2, -(top_h - cap_band - top_anchor) - 2))
    zoom_gap = zh - 2 * cap_band - 2 * top_anchor
    bot_anchor = top_anchor + cap_band + zoom_gap
    zoom_src.blit(bot_pillar, (-2, bot_anchor - 2))
    zoom = pygame.transform.scale(zoom_src, (zw * 2, zh * 2))
    zx = panelB.x + 170
    zy = panelB.y + 116
    zbg = _sky(zw * 2, zh * 2, (6, 12, 22), (10, 20, 36), (14, 36, 48))
    sheet.blit(zbg, (zx, zy))
    pygame.draw.rect(sheet, (170, 200, 204), (zx - 1, zy - 1, zw * 2 + 2, zh * 2 + 2), 1)
    sheet.blit(zoom, (zx, zy))
    _label(sheet, small, "2x zoom: esca bulb", zx - 2, zy - 16, (255, 255, 255))
    _label(sheet, small, "mirror top<->bottom", zx - 2, zy + zh * 2 + 6, (255, 224, 168))

    # — Cell C: TRUE 32px gameplay chip on day + night, plus a 4x audit + grayscale.
    panelC = pygame.Rect(696, 56, 326, 660)
    pygame.draw.rect(sheet, (38, 42, 46), panelC, border_radius=8)
    pygame.draw.rect(sheet, (90, 130, 134), panelC, 2, border_radius=8)
    _label(sheet, font, "(c) TRUE 32px gameplay chip", panelC.x + 8, panelC.y + 8)
    _label(sheet, small, "head-dominant compact / day + night sky", panelC.x + 8, panelC.y + 28,
           (200, 226, 222))

    # Compact gameplay creature, day + night, shown at a readable mid scale.
    boss_day = build_chochin(scale=0.6, ss=5, compact=True)
    boss_night = build_chochin(scale=0.6, ss=5, night=True, compact=True)
    day = _sky(150, 300, (60, 140, 215), (110, 185, 235), (180, 222, 246))
    night = _sky(150, 300, (6, 12, 26), (10, 24, 44), (18, 50, 64), stars=True)
    dy = panelC.y + 50
    sheet.blit(day, (panelC.x + 12, dy))
    sheet.blit(night, (panelC.x + 170, dy))
    sheet.blit(boss_day, (panelC.x + 12 + 75 - boss_day.get_width() // 2, dy + 8))
    sheet.blit(boss_night, (panelC.x + 170 + 75 - boss_night.get_width() // 2, dy + 8))
    _label(sheet, small, "DAY", panelC.x + 18, dy + 6, (16, 28, 40))
    _label(sheet, small, "NIGHT", panelC.x + 176, dy + 6, (255, 224, 168))

    # TRUE 32px chips on day + night skies (the gameplay-scale read), then a 4x
    # nearest-neighbour blow-up + grayscale audit.
    gy = dy + 318
    _label(sheet, small, "TRUE 32px chip on day + night sky:", panelC.x + 12, gy - 2,
           (200, 226, 222))
    icon_src = build_chochin(scale=1.0, ss=5, compact=True)
    sc32 = 32 / icon_src.get_height()
    icon32 = pygame.transform.smoothscale(
        icon_src, (max(1, int(icon_src.get_width() * sc32)), 32))

    chips = [
        (_sky(86, 86, (60, 140, 215), (110, 185, 235), (180, 222, 246)), "day"),
        (_sky(86, 86, (6, 12, 26), (10, 24, 44), (18, 50, 64), stars=True), "night"),
    ]
    sx = panelC.x + 12
    for bg_chip, lab in chips:
        chip = pygame.Rect(sx, gy + 16, 86, 86)
        sheet.blit(bg_chip, chip.topleft)
        pygame.draw.rect(sheet, (140, 165, 168), chip, 1, border_radius=4)
        sheet.blit(icon32, (chip.centerx - icon32.get_width() // 2,
                            chip.centery - icon32.get_height() // 2))
        _label(sheet, small, lab, chip.x + 4, chip.y + 2, (240, 244, 244))
        sx += 96

    # 4x blow-up + grayscale of the true-32 chip.
    blow = pygame.transform.scale(icon32, (icon32.get_width() * 4, icon32.get_height() * 4))
    bx = panelC.x + 12
    byy = gy + 118
    pygame.draw.rect(sheet, (58, 62, 66), (bx - 2, byy - 2, blow.get_width() + 4, blow.get_height() + 4),
                     border_radius=4)
    sheet.blit(blow, (bx, byy))
    _label(sheet, small, "4x blow-up of the 32px chip", bx, byy + blow.get_height() + 4,
           (200, 226, 222))

    gray = _to_gray(blow)
    gx = bx + blow.get_width() + 24
    pygame.draw.rect(sheet, (110, 114, 112), (gx - 2, byy - 2, gray.get_width() + 4, gray.get_height() + 4),
                     border_radius=4)
    sheet.blit(gray, (gx, byy))
    _label(sheet, small, "grayscale value check", gx, byy + gray.get_height() + 4, (24, 24, 24))

    # — Footer captions.
    _label(sheet, small,
           "STYLE: flat saturated fills, hard 1-2px ink keyline, dark-core -> flat-fill -> cold-steel rim-sheen triad, 1px grown outline, chibi, scary-CUTE.",
           18, SH - 40, (200, 214, 218))
    _label(sheet, small,
           "PILLAR: the segmented illicium stalk IS the shaft (knuckle-node per repeat + barbel-feelers); the glowing esca lure-bulb (~shaft+30%) caps + lanterns the gap. On-axis mirror, no top-heavy cap.",
           18, SH - 22, (200, 214, 218))

    out_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(out_dir, "round_1.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path)


if __name__ == "__main__":
    main()
