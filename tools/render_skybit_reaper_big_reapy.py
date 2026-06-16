"""Look-dev sheet for the Skybit Death-boss take #7 — "BIG REAPY".

Death as a GIANT grinning jack-o-skull (~55% of the figure height) perched on a
tiny cloaked body, carrying a bone-bident. The whole identity is the head-mass
inversion of the tiny-imp take: menace by sheer scale, but the big round sockets
+ ember pinpricks on a chibi head tip the read to "delighted puppy," not horror.

House style this obeys (the warren-clown grammar):
  - CHIBI proportions — here the head dominates, tiny weight-shifted body below.
  - FLAT fills + hard 1-2px ink keylines (28,22,30). No within-shape gradients,
    no soft/feathered edges, no bevels, no realistic shading.
  - Form via the triad (`_marotte_ruff`, pillar_staff.py:240): dark-core ring ->
    flat fill -> top-left rim sheen. The giant skull reads sculpted-but-flat.
  - Silhouette POP via a post-pass 1px dark outline grown from the alpha mask
    (parrot `_add_outline`) so the warm bone never flattens against the sky.
  - SUPERSAMPLE then smoothscale.

Prop -> pillar mirror: the bone shaft is the tileable PILLAR BODY (vertebra
bumps = banding); the two-prong fork is a detachable TOP CAP that rides the
gap-edge only, so a top/bottom mirror reads as a clean vertical bone post with a
soul-catcher flourishing INTO the gap (the snath->pillar decision from the seed).

Imports the real game colour/shape kit only; nothing under game/ is touched.
Headless + deterministic.

    SDL_VIDEODRIVER=dummy python tools/render_skybit_reaper_big_reapy.py
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.draw import _shade_c, lerp_color, make_glow_surface
from game.config import PIPE_W


pygame.init()

# ── "ember-bone & ash-blue" palette (take #7) ────────────────────────────────
# Warm-bone DOMINANT (kept warm + bold, never a grey realistic skull), ash-blue
# cloak as the value anchor that holds the silhouette on a warm day sky, ember-
# orange socket-fire as the single glow accent. The dark socket/keyline SHAPE
# must read in grayscale too, so the ember is never the only face cue.
BONE        = (240, 230, 206)   # skull / bone fill
BONE_DK     = (194, 174, 132)   # dark-core ring + jaw shadow seat
BONE_SHEEN  = (255, 247, 224)   # top-left rim sheen
TOOTH       = (250, 244, 224)   # tooth band (a hair brighter than bone)
TOOTH_DK    = (150, 132, 96)    # tooth separators / under-shade

CLOAK       = (55, 72, 94)      # ash-blue-slate body
CLOAK_DK    = (33, 48, 63)      # cloak dark-core / fold grooves
CLOAK_SHEEN = (94, 120, 146)    # cloak top-left rim

EMBER       = (255, 106, 44)    # socket-fire ember glow (outer)
EMBER_HOT   = (255, 194, 61)    # socket-fire inner hot core
BRASS       = (200, 144, 46)    # collar trim / clasp
BRASS_HI    = (255, 224, 150)

INK         = (28, 22, 30)      # the house keyline


def _triad_circle(surf, cx, cy, r, col, *, sheen=True):
    """The house form triad on a circle: dark-core ring -> flat fill -> top-left
    rim sheen. Gives the giant skull sculpted volume while staying flat-shaded."""
    pygame.draw.circle(surf, _shade_c(col, -46), (int(cx), int(cy)), int(r))
    pygame.draw.circle(surf, col, (int(cx), int(cy)), max(1, int(r - max(1, r * 0.06))))
    if sheen:
        pygame.draw.circle(surf, _shade_c(col, 28),
                           (int(cx - r * 0.32), int(cy - r * 0.34)),
                           max(2, int(r * 0.34)))


def _add_outline(src, outline_color=(*INK, 235)):
    """Grow a 1px dark keyline from the alpha mask so the silhouette POPS on any
    sky (the parrot `_add_outline` recipe). Returns a padded surface."""
    w, h = src.get_size()
    pad = 2
    out = pygame.Surface((w + pad * 2, h + pad * 2), pygame.SRCALPHA)
    mask = pygame.mask.from_surface(src, threshold=8)
    sil = mask.to_surface(setcolor=outline_color, unsetcolor=(0, 0, 0, 0))
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1),
                   (-1, -1), (1, -1), (-1, 1), (1, 1)):
        out.blit(sil, (pad + dx, pad + dy))
    out.blit(src, (pad, pad))
    return out


# ── the giant jack-o-skull face ──────────────────────────────────────────────

def _skull_face(surf, cx, cy, r, ss, *, night=False):
    """The colossal jack-o-skull: a big bone cranium with the form triad, two huge
    round sockets with ember pinpricks (the puppy-eyes lever), a small triangular
    nose hole, and a wide flat tooth-row band — a friendly jack-o-grin, NOT a
    horror rictus. All keyed off the cranium radius `r`. `night` pushes the socket
    ember so the eyes read LIT on a dark sky instead of two dead holes."""
    # Cranium dome.
    _triad_circle(surf, cx, cy, r, BONE)

    # Jaw: a rounded trapezoid hung under the dome so the lower face squares off
    # into a chin (a skull, not a plain ball). Drawn with the triad seams by hand.
    jaw_top = cy + r * 0.30
    jaw_bot = cy + r * 1.04
    jaw = [
        (cx - r * 0.74, jaw_top),
        (cx - r * 0.52, jaw_bot),
        (cx + r * 0.52, jaw_bot),
        (cx + r * 0.74, jaw_top),
    ]
    pygame.draw.polygon(surf, _shade_c(BONE, -46),
                        [(int(x), int(y)) for x, y in jaw])
    inset = [(cx - r * 0.68, jaw_top + ss), (cx - r * 0.47, jaw_bot - ss),
             (cx + r * 0.47, jaw_bot - ss), (cx + r * 0.68, jaw_top + ss)]
    pygame.draw.polygon(surf, BONE, [(int(x), int(y)) for x, y in inset])
    # Re-stamp the dome so the jaw seam tucks under the rounded cranium.
    _triad_circle(surf, cx, cy, r, BONE, sheen=True)

    # Cheekbone hollows — two shallow dark scoops high on the lower face so the
    # wide jaw reads as bone, not a beachball. Seated ABOVE the jaw seat (not on
    # the jaw seam) and as a single flat tone so the chin stays one clean shape.
    for s in (-1, 1):
        hr = pygame.Rect(0, 0, int(r * 0.30), int(r * 0.36))
        hr.center = (int(cx + s * r * 0.64), int(cy + r * 0.40))
        pygame.draw.ellipse(surf, _shade_c(BONE, -34), hr)

    # — Eye sockets: BIG round deep-set holes. Big + round on a chibi head is the
    #   whole "excited puppy" tell. Ink cavity, ember underglow, hot pinprick.
    eye_dx = r * 0.40
    eye_dy = -r * 0.06
    sock_r = r * 0.30
    for s in (-1, 1):
        ex, ey = cx + s * eye_dx, cy + eye_dy
        # A soft ember halo behind the socket so the fire reads as glowing from
        # within the bone (additive, kept tight so warm-bone stays dominant).
        glow = make_glow_surface(int(sock_r * 1.7), EMBER, alpha_center=150, falloff=2.0)
        surf.blit(glow, (int(ex - sock_r * 1.7 - 1), int(ey - sock_r * 1.7 - 1)),
                  special_flags=pygame.BLEND_ADD)
        # Deep ink cavity (the grayscale-legible shape — the read survives without
        # the ember colour).
        pygame.draw.circle(surf, INK, (int(ex), int(ey)), int(sock_r))
        pygame.draw.circle(surf, _shade_c(BONE, -52), (int(ex), int(ey)),
                           int(sock_r), max(1, int(2 * ss)))
        # Ember fire pooling in the lower socket, hot core pinprick high + inward
        # (eyes aimed slightly together = eager, cross-eyed-cute, not a cold glare).
        pygame.draw.circle(surf, EMBER, (int(ex), int(ey + sock_r * 0.22)),
                           int(sock_r * 0.52))
        pygame.draw.circle(surf, EMBER_HOT,
                           (int(ex - s * sock_r * 0.18), int(ey - sock_r * 0.04)),
                           max(2, int(sock_r * 0.30)))
        pygame.draw.circle(surf, BONE_SHEEN,
                           (int(ex - s * sock_r * 0.22), int(ey - sock_r * 0.16)),
                           max(1, int(sock_r * 0.13)))
        # A high, bowed-up bone brow-ridge over each socket — lifted, never the
        # angry inner-down V — so the giant face reads delighted/surprised.
        pygame.draw.arc(surf, _shade_c(BONE, -34),
                        (int(ex - sock_r * 1.25), int(ey - sock_r * 1.7),
                         int(sock_r * 2.5), int(sock_r * 1.7)),
                        math.radians(20), math.radians(160), max(2, int(2.2 * ss)))

    # — Nose: a small upturned heart/triangle hole between+below the sockets.
    nose_y = cy + r * 0.34
    nose = [(cx, nose_y - r * 0.10), (cx - r * 0.11, nose_y + r * 0.13),
            (cx + r * 0.11, nose_y + r * 0.13)]
    pygame.draw.polygon(surf, INK, [(int(x), int(y)) for x, y in nose])
    pygame.draw.polygon(surf, _shade_c(BONE, -50),
                        [(int(x), int(y)) for x, y in nose], max(1, int(1.4 * ss)))

    # — The jack-o-grin: FIVE even square teeth on a strongly bowed-UP band, so the
    #   read is a happy pumpkin jack-grin, not a buck-toothed underbite. The deep
    #   dark mouth-seat curves up at the corners; teeth ride that curve so the whole
    #   band visibly SMILES. Even tooth widths kill the "two big bucks" grim read.
    grin_y = cy + r * 0.70
    grin_hw = r * 0.60
    grin_h = r * 0.34
    # Bow amplitude: how far the band lifts at the corners vs centre. Raised ~45%
    # over round 1 so the smile-curve is unmistakable at 1x.
    bow_amp = grin_h * 0.62

    def _bow(x_rel):
        # x_rel in [-1, 1]; 0 at centre (lowest), +-1 at the lifted corners.
        return bow_amp * (x_rel * x_rel)

    # Deep dark mouth-seat: a wide curved smile-band so the gaps between teeth read
    # as one clean dark crescent (the upper edge bows up, lower edge follows).
    seat_top, seat_bot = [], []
    n = 16
    for i in range(n + 1):
        xr = -1.0 + 2.0 * (i / n)
        x = cx + xr * grin_hw
        yt = grin_y - _bow(xr)
        seat_top.append((x, yt))
        seat_bot.append((x, yt + grin_h))
    seat = seat_top + seat_bot[::-1]
    pygame.draw.polygon(surf, INK, [(int(x), int(y)) for x, y in seat])

    # Five even square teeth seated on the smile-curve, snug gaps showing the dark
    # seat between them. Even widths = friendly jack-grin, not an underbite.
    teeth = 5
    gap = grin_hw * 0.10
    tw = (grin_hw * 2.0 - gap * (teeth - 1)) / teeth
    th = grin_h * 0.70
    for i in range(teeth):
        tx = -grin_hw + i * (tw + gap)
        xr = (tx + tw * 0.5) / grin_hw
        ty = grin_y - _bow(xr) + ss
        rect = pygame.Rect(int(cx + tx + ss), int(ty), int(tw - ss), int(th))
        pygame.draw.rect(surf, TOOTH, rect, border_radius=max(1, int(1.6 * ss)))
        pygame.draw.rect(surf, TOOTH_DK, rect, max(1, int(1.4 * ss)),
                         border_radius=max(1, int(1.6 * ss)))
        # Top-left sheen tick on each tooth.
        pygame.draw.line(surf, BONE_SHEEN,
                         (rect.left + ss, rect.top + ss),
                         (rect.left + ss, rect.top + int(th * 0.5)), max(1, int(ss)))


def _cloak_body(surf, cx, neck_y, w, h, ss):
    """The tiny cloaked body under the giant skull: a short triangular poncho-cloak
    with a brass collar clasp, two stub arms, and tiny peeking feet. Deliberately
    small so the head dominates (~55% of the figure). Triad-shaded ash-blue."""
    hem_y = neck_y + h
    # Poncho silhouette — narrow at the neck, flaring to a scalloped-ish hem.
    body = [
        (cx - w * 0.30, neck_y),
        (cx - w * 0.62, neck_y + h * 0.55),
        (cx - w * 0.72, hem_y),
        (cx + w * 0.72, hem_y),
        (cx + w * 0.62, neck_y + h * 0.55),
        (cx + w * 0.30, neck_y),
    ]
    pygame.draw.polygon(surf, CLOAK_DK, [(int(x), int(y)) for x, y in body])
    inner = [(cx - w * 0.26, neck_y + ss), (cx - w * 0.56, neck_y + h * 0.55),
             (cx - w * 0.65, hem_y - ss), (cx + w * 0.65, hem_y - ss),
             (cx + w * 0.56, neck_y + h * 0.55), (cx + w * 0.26, neck_y + ss)]
    pygame.draw.polygon(surf, CLOAK, [(int(x), int(y)) for x, y in inner])
    # Top-left rim sheen down the lit cloak edge.
    pygame.draw.line(surf, CLOAK_SHEEN,
                     (int(cx - w * 0.40), int(neck_y + h * 0.20)),
                     (int(cx - w * 0.60), int(hem_y - ss)), max(2, int(2.0 * ss)))
    # Two fold grooves so the cloth reads draped, not a flat triangle.
    for fx in (-0.18, 0.22):
        pygame.draw.line(surf, CLOAK_DK,
                         (int(cx + fx * w * 0.5), int(neck_y + h * 0.3)),
                         (int(cx + fx * w * 0.9), int(hem_y - ss)), max(1, int(1.6 * ss)))
    # Scalloped hem lobes — hard flat lobes, no feather (house hem grammar).
    lobes = 5
    for i in range(lobes):
        t = (i + 0.5) / lobes
        lx = cx - w * 0.70 + w * 1.40 * t
        lr = w * 0.13
        pygame.draw.circle(surf, CLOAK_DK, (int(lx), int(hem_y)), int(lr))
        pygame.draw.circle(surf, CLOAK, (int(lx), int(hem_y - ss)), int(lr - ss))

    # Brass collar clasp ring at the neck (the trim accent + a value break between
    # warm bone and ash-blue).
    clasp = pygame.Rect(0, 0, int(w * 0.5), int(h * 0.22))
    clasp.center = (int(cx), int(neck_y + h * 0.06))
    pygame.draw.ellipse(surf, _shade_c(BRASS, -50), clasp)
    pygame.draw.ellipse(surf, BRASS, clasp.inflate(-ss * 2, -ss * 2))
    pygame.draw.circle(surf, BRASS_HI, clasp.center, max(1, int(h * 0.05)))

    # Two stub arms poking from under the skull — one braces the bident (drawn by
    # the caller), the other hangs as a little mitt. Tiny + rounded = cute.
    for s, lift in ((-1, 0.0), (1, 0.10)):
        ax = cx + s * w * 0.50
        ay = neck_y + h * 0.30 - h * lift
        pygame.draw.line(surf, CLOAK_DK, (int(cx + s * w * 0.3), int(neck_y + h * 0.2)),
                         (int(ax), int(ay)), max(3, int(5 * ss)))
        pygame.draw.line(surf, CLOAK, (int(cx + s * w * 0.3), int(neck_y + h * 0.2)),
                         (int(ax), int(ay)), max(2, int(3 * ss)))
        # Bone mitt hand.
        _triad_circle(surf, ax, ay, w * 0.12, BONE)

    # Tiny feet peeking under the hem.
    for s in (-1, 1):
        fx = cx + s * w * 0.26
        fr = pygame.Rect(0, 0, int(w * 0.2), int(w * 0.13))
        fr.center = (int(fx), int(hem_y + w * 0.05))
        pygame.draw.ellipse(surf, BONE_DK, fr)
        pygame.draw.ellipse(surf, BONE, fr.inflate(-ss * 2, -ss * 2))


# ── the bone-bident prop (and its pillar-tile components) ─────────────────────

def _bone_shaft(surf, cx, top_y, bot_y, hw, ss):
    """The bone shaft = the tileable PILLAR BODY. A chunky bone post with VERTEBRA
    bumps down its length (the banding that tiles vertically). Triad-shaded so it
    reads round. No fork here — the fork is the detachable top cap."""
    # Core post.
    pygame.draw.rect(surf, BONE_DK, (int(cx - hw), int(top_y), int(2 * hw), int(bot_y - top_y)))
    pygame.draw.rect(surf, BONE, (int(cx - hw + ss), int(top_y),
                                  int(2 * hw - 2 * ss), int(bot_y - top_y)))
    # Lit rail down the top-left edge so the bone reads cylindrical.
    pygame.draw.line(surf, BONE_SHEEN, (int(cx - hw * 0.5), int(top_y)),
                     (int(cx - hw * 0.5), int(bot_y)), max(1, int(1.6 * ss)))
    # Vertebra bumps: evenly spaced knuckle rings, each a small triad-lit lobe pair
    # straddling the post — the repeatable banding that makes the post read as a
    # spine and tiles cleanly at any pillar length.
    band = int(18 * ss)
    y = top_y + band // 2
    while y < bot_y - band * 0.3:
        for s in (-1, 1):
            kx = cx + s * hw * 0.92
            pygame.draw.circle(surf, _shade_c(BONE, -46), (int(kx), int(y)), int(hw * 0.42))
            pygame.draw.circle(surf, BONE, (int(kx), int(y)), max(1, int(hw * 0.34)))
        # A dark groove ring across the post so the vertebra read as segmented.
        pygame.draw.line(surf, BONE_DK, (int(cx - hw), int(y + hw * 0.5)),
                         (int(cx + hw), int(y + hw * 0.5)), max(1, int(1.4 * ss)))
        y += band


def _bone_fork(surf, cx, base_y, hw, ss, *, point_up=True):
    """The two-prong soul-catcher FORK = the detachable PILLAR TOP CAP that rides
    the gap-edge ONLY. Two hooked bone prongs curving in toward a centre gap, with
    a small ember soul-wisp caught between them. Mirrors with the shaft into a clean
    vertical post; the prongs flourish INTO the gap, never bleeding the tiling body.
    `point_up` orients the prongs away from the shaft (toward the gap)."""
    d = -1 if point_up else 1
    prong_len = 30 * ss
    spread = hw * 1.6
    for s in (-1, 1):
        # Each prong: a curved bone tine sweeping out then hooking back inward to a
        # sharp tip, framing the centre gap.
        pts = []
        n = 10
        for i in range(n + 1):
            t = i / n
            px = cx + s * (hw * 0.5 + spread * math.sin(t * math.pi * 0.5))
            py = base_y + d * prong_len * t
            # Hook the tip back toward centre.
            if t > 0.6:
                px -= s * (t - 0.6) * spread * 0.9
            pts.append((px, py))
        # Dark-core stroke then bone fill stroke then sheen — a fat tapering tine.
        for col, wid in ((BONE_DK, 9 * ss), (BONE, 6 * ss), (BONE_SHEEN, 2 * ss)):
            for i in range(len(pts) - 1):
                t = i / (len(pts) - 1)
                w = max(1, int(wid * (1.0 - 0.55 * t)))
                a, b = pts[i], pts[i + 1]
                if col is BONE_SHEEN:
                    a = (a[0] - ss, a[1]); b = (b[0] - ss, b[1])
                pygame.draw.line(surf, col, (int(a[0]), int(a[1])),
                                 (int(b[0]), int(b[1])), w)
        # Sharp ink tip.
        pygame.draw.circle(surf, INK, (int(pts[-1][0]), int(pts[-1][1])), max(1, int(2 * ss)))

    # The caught soul-wisp: an ember teardrop glowing between the prongs at the gap.
    wy = base_y + d * prong_len * 0.55
    glow = make_glow_surface(int(hw * 1.5), EMBER, alpha_center=170, falloff=1.9)
    surf.blit(glow, (int(cx - hw * 1.5 - 1), int(wy - hw * 1.5 - 1)),
              special_flags=pygame.BLEND_ADD)
    pygame.draw.circle(surf, EMBER, (int(cx), int(wy)), max(2, int(hw * 0.55)))
    pygame.draw.circle(surf, EMBER_HOT, (int(cx), int(wy - hw * 0.12)), max(1, int(hw * 0.30)))


def build_big_reapy(scale=1.0, ss=3):
    """The full boss figure on its own transparent surface. Head ~55% of total
    height. Returns an outlined surface and its baseline (feet) y for placement."""
    H = int(260 * scale)
    W = int(150 * scale)
    pad = int(70 * scale)
    surf = pygame.Surface(((W + pad * 2) * ss, (H + pad) * ss), pygame.SRCALPHA)
    cx = (W // 2 + pad) * ss

    # Head occupies the top ~55%. Cranium radius keyed off that head band.
    head_band = int(H * 0.55) * ss
    skull_r = head_band * 0.42
    skull_cy = int(pad * 0.3) * ss + skull_r
    skull_cx = cx

    # Tiny body below the jaw.
    neck_y = skull_cy + skull_r * 1.0
    body_w = W * 0.62 * ss
    body_h = int(H * 0.34) * ss

    # Bident held upright at the figure's right, braced by the stub arm. The shaft
    # runs past the feet; the fork rises above the skull (the soul-catcher overhead).
    bx = cx + W * 0.46 * ss
    bhw = 7 * ss
    fork_base = skull_cy - skull_r * 0.7
    feet_y = neck_y + body_h + W * 0.06 * ss
    _bone_shaft(surf, bx, fork_base, feet_y + 8 * ss, bhw, ss)
    _bone_fork(surf, bx, fork_base, bhw, ss, point_up=True)

    _cloak_body(surf, skull_cx, neck_y, body_w, body_h, ss)
    _skull_face(surf, skull_cx, skull_cy, skull_r, ss)

    # Downscale, then grow the unifying keyline from the alpha mask.
    out_w = int(surf.get_width() / ss)
    out_h = int(surf.get_height() / ss)
    small = pygame.transform.smoothscale(surf, (out_w, out_h))
    return _add_outline(small), feet_y / ss


# ── pillar pair (prop -> pillar mirror proof) ────────────────────────────────

OVERHANG = 12


def _bident_pillar_obstacle(height, ss, *, flip):
    """One bident PILLAR obstacle: the bone shaft fills the post, the fork cap sits
    at the gap end. `flip` makes the top pillar's fork point DOWN into the gap; the
    bottom pillar's fork points UP — proving the prop mirrors top<->bottom into a
    clean vertical bone post with the soul-catcher flourishing into the gap."""
    bw = (PIPE_W + 2 * OVERHANG) * ss
    bh = max(1, int(height)) * ss
    surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
    cx = bw // 2
    hw = 8 * ss
    # The fork cap rides the gap-edge (the bottom of the un-flipped tile); the shaft
    # is the repeatable body filling the rest. Reserve a band for the fork.
    cap_band = int(46 * ss)
    _bone_shaft(surf, cx, 0, bh - cap_band, hw, ss)
    _bone_fork(surf, cx, bh - cap_band, hw, ss, point_up=False)
    out = pygame.transform.smoothscale(surf, (PIPE_W + 2 * OVERHANG, max(1, int(height))))
    out = _add_outline(out)
    if flip:
        out = pygame.transform.flip(out, False, True)
    return out


# ── sheet composition ────────────────────────────────────────────────────────

def _label(surf, font, text, x, y, color=(245, 240, 230)):
    surf.blit(font.render(text, True, (0, 0, 0)), (x + 1, y + 1))
    surf.blit(font.render(text, True, color), (x, y))


def _sky(w, h, top, mid, bot):
    s = pygame.Surface((w, h))
    for i in range(h):
        t = i / max(1, h - 1)
        if t < 0.5:
            c = lerp_color(top, mid, t / 0.5)
        else:
            c = lerp_color(mid, bot, (t - 0.5) / 0.5)
        pygame.draw.line(s, c, (0, i), (w, i))
    return s


def main():
    pygame.font.init()
    font = pygame.font.SysFont("dejavusans", 15, bold=True)
    small = pygame.font.SysFont("dejavusans", 12)

    SW, SH = 1180, 760
    sheet = pygame.Surface((SW, SH))
    sheet.fill((36, 34, 44))
    _label(sheet, font, "BIG REAPY  —  take #7  —  ember-bone & ash-blue  —  round 1", 18, 12)
    _label(sheet, small, "the towering boss-skull: a GIANT jack-o-grin (~55% head) on a tiny cloaked body, carrying a bone-bident soul-catcher",
            18, 32, (200, 196, 210))

    # — Cell A: boss at showcase scale, on a neutral panel.
    panel = pygame.Rect(18, 56, 360, 560)
    pygame.draw.rect(sheet, (52, 50, 62), panel, border_radius=8)
    pygame.draw.rect(sheet, (90, 86, 104), panel, 2, border_radius=8)
    boss, _ = build_big_reapy(scale=1.7, ss=3)
    sheet.blit(boss, (panel.centerx - boss.get_width() // 2,
                      panel.bottom - boss.get_height() - 20))
    _label(sheet, font, "(a) BOSS  showcase scale", panel.x + 8, panel.y + 8)

    # — Cell B: the bident as a tileable PILLAR pair (top cap + repeatable mid).
    panelB = pygame.Rect(394, 56, 360, 560)
    bg = _sky(panelB.w, panelB.h, (40, 110, 200), (90, 170, 230), (170, 220, 245))
    sheet.blit(bg, panelB.topleft)
    pygame.draw.rect(sheet, (90, 86, 104), panelB, 2, border_radius=8)
    # A top + bottom pillar with a gap between — the fork caps face the gap.
    gap_top = panelB.y + 200
    gap_bot = panelB.y + 360
    top_h = gap_top - panelB.y
    bot_h = panelB.bottom - gap_bot
    px = panelB.centerx - (PIPE_W + 2 * OVERHANG) // 2
    top_pillar = _bident_pillar_obstacle(top_h, 3, flip=True)
    bot_pillar = _bident_pillar_obstacle(bot_h, 3, flip=False)
    sheet.blit(top_pillar, (px - 2, panelB.y - 2))
    sheet.blit(bot_pillar, (px - 2, gap_bot - 2))
    _label(sheet, font, "(b) PROP -> PILLAR mirror", panelB.x + 8, panelB.y + 8)
    _label(sheet, small, "shaft = tileable body (vertebra banding)", panelB.x + 8, panelB.y + 28, (20, 20, 30))
    _label(sheet, small, "fork = gap-edge soul-catcher cap", panelB.x + 8, gap_bot + 8, (20, 20, 30))

    # — Cell C: 1x in-game-scale INSET on BOTH day and night skies.
    panelC = pygame.Rect(770, 56, 392, 560)
    pygame.draw.rect(sheet, (52, 50, 62), panelC, border_radius=8)
    pygame.draw.rect(sheet, (90, 86, 104), panelC, 2, border_radius=8)
    _label(sheet, font, "(c) 1x in-game scale  —  day / night legibility", panelC.x + 8, panelC.y + 8)

    boss1x, feet = build_big_reapy(scale=0.66, ss=3)   # ~ scrolling-route size
    day = _sky(180, 250, (40, 110, 200), (90, 170, 230), (170, 220, 245))
    night = _sky(180, 250, (5, 8, 30), (15, 25, 70), (35, 55, 115))
    # A couple of night stars so the dark panel reads as the night sky.
    for sx, sy in ((24, 40), (150, 26), (96, 70), (40, 120), (160, 150), (70, 200)):
        pygame.draw.circle(night, (220, 230, 255), (sx, sy), 1)

    dy = panelC.y + 40
    sheet.blit(day, (panelC.x + 14, dy))
    sheet.blit(night, (panelC.x + 200, dy))
    sheet.blit(boss1x, (panelC.x + 14 + 90 - boss1x.get_width() // 2,
                        dy + 250 - boss1x.get_height() - 6))
    sheet.blit(boss1x, (panelC.x + 200 + 90 - boss1x.get_width() // 2,
                        dy + 250 - boss1x.get_height() - 6))
    _label(sheet, small, "DAY", panelC.x + 14 + 6, dy + 6, (20, 20, 30))
    _label(sheet, small, "NIGHT", panelC.x + 200 + 6, dy + 6, (210, 220, 255))

    # — Grayscale silhouette check (accessibility: face must read without ember).
    gy = dy + 270
    gray = pygame.Surface((boss1x.get_width(), boss1x.get_height()), pygame.SRCALPHA)
    gray.blit(boss1x, (0, 0))
    arr = pygame.surfarray.pixels3d(gray)
    lum = (arr[:, :, 0] * 0.3 + arr[:, :, 1] * 0.59 + arr[:, :, 2] * 0.11).astype("uint8")
    arr[:, :, 0] = lum
    arr[:, :, 1] = lum
    arr[:, :, 2] = lum
    del arr
    gpanel = pygame.Rect(panelC.x + 14, gy, 360, 230)
    pygame.draw.rect(sheet, (120, 120, 128), gpanel, border_radius=6)
    sheet.blit(gray, (gpanel.centerx - gray.get_width() // 2,
                      gpanel.bottom - gray.get_height() - 8))
    _label(sheet, small, "grayscale: dark socket + keyline shape carries the face (no ember reliance)",
            gpanel.x + 6, gpanel.y + 6, (30, 30, 30))

    # — Footer caption: the scary-cute thesis.
    _label(sheet, small,
           "scary-cute: big round sockets + lifted bone brows + a wide square-toothed jack-grin read 'delighted puppy', not horror.",
           18, SH - 124, (210, 206, 220))
    _label(sheet, small,
           "house style: FLAT fills, hard ink keyline grown from the alpha mask, dark-core->fill->top-left-sheen triad, ss=3 -> smoothscale.",
           18, SH - 104, (210, 206, 220))
    _label(sheet, small,
           "prop->pillar: ash-blue cloak + ink keyline hold the silhouette on BOTH skies; warm bone never flattens against the warm day sky.",
           18, SH - 84, (210, 206, 220))

    out_dir = os.path.join(os.path.dirname(__file__), "..", "docs",
                           "skybit_reaper", "big_reapy")
    out_dir = os.path.abspath(out_dir)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_1.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path)


if __name__ == "__main__":
    main()
