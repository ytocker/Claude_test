"""Look-dev sheet for the Skybit BOSS batch-2 LEYAK-EPIC set — concept #1 "KRASUE".

SE-Asian Krasue / penanggalan re-cuted as a sleepy floating SKULL-LANTERN that
dangles its own viscera as a vertical STRING of glowing marsh gut-orbs — the
orb-string IS the pillar. Distinct from the shipped Leyak (ash face + hot-pink
viscera-RIBBON): here the body runs COOL dusk-mauve and the only warm hue is
firefly-gold contained STRICTLY inside 5-6 discrete gut-orbs (body cool / glow
warm). The repeatable pillar body is the evenly-beaded orb-string on a thin
sinew; the gap-edge cap is the creature's OWN form — a single cracked bottom
lantern-orb radiating into the gap.

House style this obeys (warren-clown / Big-Reapy / Leyak grammar), ELEVATED:
  - CHIBI proportions — one oversized floating head, no torso/limbs; the
    orb-string is the body.
  - FLAT saturated fills + hard 1-2px ink keyline (28,22,30). No within-shape
    gradients, no soft/feathered edges, no bevels.
  - Form via the TRIAD: dark-core ring -> flat fill -> top-left rim sheen.
  - Silhouette POP via a 1px ink keyline grown from the alpha mask.
  - EPIC: render LARGE at SS=6, then smoothscale down — crisp at downscale.
    More geometry (membrane veining, inner orb glow-lobes, thin sinew), richer
    triad, stronger make_glow_surface glow than the source.

Accessibility tell: the warm gut-orb STRING shape + cool head vs warm-orb
contrast carry the read independent of hue.

Headless + deterministic.

    SDL_VIDEODRIVER=dummy PYTHONPATH=/home/user/skybit python docs/skybit_devil/batch2/leyak_epic/krasue/render_krasue.py
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.draw import _shade_c, lerp_color, make_glow_surface
from game.config import PIPE_W


pygame.init()

# ── PINNED PALETTE (leyak-epic krasue) — hex-exact from the locked brief ─────
# Body runs COOL dusk-mauve; the ONLY warm hue is firefly-gold contained inside
# the gut-orbs. Body cool / glow warm opens a clean lane vs shipped Ifra's coral
# body and Leyak's hot-pink trail.
BODY        = (150, 128, 150)   # cool dusk-mauve face / skull fill
BODY_DK     = (96, 78, 104)     # deep mauve shade (dark-core ring / hollows)
BODY_SHEEN  = (214, 200, 220)   # lilac top-left rim sheen

SINEW       = (118, 96, 120)    # the thin mauve thread the orbs string onto
SINEW_DK    = (78, 62, 86)

# Firefly-gold — ONLY ever inside the discrete gut-orbs. Never on flesh.
ORB         = (255, 224, 128)   # firefly-gold orb fill
ORB_DK      = (196, 150, 70)    # amber orb shade (dark-core / cracks)
ORB_SHEEN   = (255, 246, 214)   # pale-gold rim sheen
ORB_CORE    = (255, 252, 236)   # the will-o'-the-wisp inner core twinkle

INK         = (28, 22, 30)      # the house keyline (epic-set ink)

# Tooth/jaw reuse a bone-pale cool family so the grin reads skull, not gold.
BONE        = (224, 214, 222)
BONE_DK     = (150, 138, 150)


def _triad_circle(surf, cx, cy, r, col, *, sheen=True, sheen_d=34):
    """House form triad on a circle: dark-core ring -> flat fill -> top-left rim
    sheen. Sculpted volume while staying flat-shaded."""
    pygame.draw.circle(surf, _shade_c(col, -46), (int(cx), int(cy)), int(r))
    pygame.draw.circle(surf, col, (int(cx), int(cy)),
                       max(1, int(r - max(1, r * 0.055))))
    if sheen:
        pygame.draw.circle(surf, _shade_c(col, sheen_d),
                           (int(cx - r * 0.32), int(cy - r * 0.34)),
                           max(2, int(r * 0.34)))


def _add_outline(src, outline_color=(*INK, 235)):
    """Grow a 1px dark keyline from the alpha mask so the silhouette POPS on any
    sky (the parrot _add_outline recipe). Returns a padded surface."""
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


# ── one glowing gut-orb (warm-gold triad sphere; glow strictly inside) ───────

def _gut_orb(surf, cx, cy, r, ss, *, night=False, cracked=False, glow=True):
    """A single luminous marsh gut-orb: an additive warm halo (the ONLY warm
    glow, contained as a discrete orb), a firefly-gold triad sphere on top, an
    inner glow-lobe + a tiny will-o'-the-wisp core twinkle. `cracked` scores a
    dark hairline fracture for the gap-edge bottom lantern-orb (its own form)."""
    if glow:
        # Stronger-than-source halo, but bounded to the orb so the body stays
        # cool — the warm reads as a contained firefly, never a body wash.
        gr = int(r * (2.0 if night else 1.5))
        gl = make_glow_surface(gr, ORB, alpha_center=210 if night else 130,
                               falloff=2.1)
        surf.blit(gl, (int(cx - gr), int(cy - gr)), special_flags=pygame.BLEND_ADD)

    # Warm-gold triad sphere.
    pygame.draw.circle(surf, ORB_DK, (int(cx), int(cy)), int(r))
    pygame.draw.circle(surf, ORB, (int(cx), int(cy)), max(1, int(r * 0.90)))
    # Inner glow-lobe — a brighter offset disc reading as the wisp swelling
    # behind a translucent membrane (elevated detail, still flat-shaded).
    pygame.draw.circle(surf, ORB_SHEEN, (int(cx - r * 0.18), int(cy - r * 0.22)),
                       max(1, int(r * 0.46)))
    if cracked:
        # A dark hairline fracture branching across the membrane — the OWN-form
        # tell that this end-orb is the cracked bottom lantern.
        cw = max(1, int(0.9 * ss))
        a = (cx - r * 0.55, cy - r * 0.30)
        b = (cx - r * 0.05, cy + r * 0.02)
        c = (cx + r * 0.40, cy - r * 0.42)
        d = (cx + r * 0.20, cy + r * 0.50)
        pygame.draw.lines(surf, ORB_DK, False,
                          [(int(x), int(y)) for x, y in (a, b, c)], cw)
        pygame.draw.lines(surf, ORB_DK, False,
                          [(int(x), int(y)) for x, y in (b, d)], cw)
    # Will-o'-the-wisp core twinkle — kept small so it reads as a point, not a
    # second mass competing with the orb itself.
    pygame.draw.circle(surf, ORB_CORE,
                       (int(cx - r * 0.16), int(cy - r * 0.20)),
                       max(1, int(r * 0.22)))


# ── the orb-string (creature viscera + the pillar body) ──────────────────────

def _orb_string(surf, top_x, top_y, length, base_r, ss, *, n_orbs, wave=0.0,
                phase=0.0, end_cracked=False, night=False):
    """The viscera orb-STRING streaming straight DOWN: a thin mauve SINEW thread
    strung with evenly-spaced glowing gut-orbs at a steady cadence (the band that
    TILES top<->bottom for the pillar). `end_cracked` makes the bottom orb the
    cracked lantern-orb gap cap. Orbs shrink gently down the string for depth."""
    def _x_at(t):
        return top_x + wave * base_r * math.sin(t * math.pi * 2.2 + phase) \
            * (0.30 + 0.70 * t)

    # The sinew thread first, so the orbs sit ON it. A thin cool cord with a
    # dark-core seam + a lilac sheen edge — the connective tissue.
    pts = []
    steps = 36
    for i in range(steps + 1):
        t = i / steps
        pts.append((_x_at(t), top_y + length * t))
    ipts = [(int(x), int(y)) for x, y in pts]
    pygame.draw.lines(surf, SINEW_DK, False, ipts, max(2, int(2.6 * ss)))
    pygame.draw.lines(surf, SINEW, False, ipts, max(1, int(1.4 * ss)))

    # Evenly-spaced gut-orbs threaded on the sinew (the repeatable organ band).
    for i in range(n_orbs):
        t = (i + 0.5) / n_orbs
        x = _x_at(t)
        y = top_y + length * t
        r = base_r * (1.0 - 0.30 * t)
        cracked = end_cracked and (i == n_orbs - 1)
        _gut_orb(surf, x, y, r, ss, night=night, cracked=cracked)


# ── the floating skull-lantern head ──────────────────────────────────────────

def _head(surf, cx, cy, r, ss, *, night=False):
    """The oversized floating skull-LANTERN head: a round cool dusk-mauve skull
    with soft membrane veining, big sleepy half-lidded eyes glowing a contained
    gold (the lantern within), a small skull nose-hole, and a gentle bone tusk-
    grin. Scary-CUTE — drowsy, not menacing. `night` lifts the cool body value so
    the head stays a clean LIGHT-mauve blob against dark-blue night biomes."""
    body = _shade_c(BODY, 14) if night else BODY
    body_sheen = _shade_c(BODY_SHEEN, 8) if night else BODY_SHEEN

    # Cranium dome (cool mauve) — slightly squashed wide for a lantern/gourd read.
    _triad_circle(surf, cx, cy, r, body)
    # Lower-cheek bulge so it reads as a head, not a perfect ball.
    cheek = pygame.Rect(0, 0, int(r * 1.84), int(r * 1.48))
    cheek.center = (int(cx), int(cy + r * 0.30))
    pygame.draw.ellipse(surf, _shade_c(body, -46), cheek)
    inner = cheek.inflate(-int(r * 0.14), -int(r * 0.14))
    pygame.draw.ellipse(surf, body, inner)
    _triad_circle(surf, cx, cy, r, body)       # re-seat the dome over the cheek
    # Bright cranium-top sheen cap so the crown catches light on night skies.
    pygame.draw.circle(surf, body_sheen,
                       (int(cx - r * 0.30), int(cy - r * 0.42)),
                       max(2, int(r * 0.30)))

    # Faint membrane veining on the head (elevated detail) — a few thin
    # dark-mauve hairlines fanning from the crown, NOT gore-realistic.
    vein = _shade_c(body, -34)
    for k in (-0.6, -0.2, 0.25, 0.62):
        a0 = math.pi * (0.5 + 0.42 * k)
        x0 = cx + math.cos(a0) * r * 0.30
        y0 = cy - r * 0.10 + math.sin(a0) * r * 0.20
        x1 = cx + math.cos(a0) * r * 0.86
        y1 = cy - r * 0.04 + math.sin(a0) * r * 0.62
        xm = (x0 + x1) * 0.5 + k * r * 0.10
        ym = (y0 + y1) * 0.5
        pygame.draw.lines(surf, vein, False,
                          [(int(x0), int(y0)), (int(xm), int(ym)),
                           (int(x1), int(y1))], max(1, int(0.8 * ss)))

    # — Eyes: big SLEEPY half-lidded sockets glowing a contained gold (the lantern
    #   inside the skull). Deep mauve socket, gold inner glow capped by a heavy
    #   upper lid so it reads drowsy + cute, not a wide menacing stare.
    eye_dx = r * 0.44
    eye_dy = -r * 0.06
    eye_r = r * 0.40
    for s in (-1, 1):
        ex, ey = cx + s * eye_dx, cy + eye_dy
        # Deep-mauve socket recess.
        pygame.draw.circle(surf, BODY_DK, (int(ex), int(ey)), int(eye_r * 1.06))
        # Contained gold glow within the socket (warm only inside the lantern eye).
        gl = make_glow_surface(int(eye_r * 1.5), ORB,
                               alpha_center=150 if night else 110, falloff=2.0)
        surf.blit(gl, (int(ex - eye_r * 1.5), int(ey - eye_r * 1.5)),
                  special_flags=pygame.BLEND_ADD)
        pygame.draw.circle(surf, ORB_DK, (int(ex), int(ey)), int(eye_r * 0.80))
        pygame.draw.circle(surf, ORB, (int(ex), int(ey)), int(eye_r * 0.66))
        pygame.draw.circle(surf, ORB_CORE,
                           (int(ex - eye_r * 0.16), int(ey - eye_r * 0.20)),
                           max(1, int(eye_r * 0.20)))
        # Heavy upper lid (cool body colour) drooping over the top half — the
        # sleepy beat. A filled circle-segment in the body hue.
        lid = pygame.Rect(int(ex - eye_r * 1.15), int(ey - eye_r * 1.25),
                          int(eye_r * 2.3), int(eye_r * 1.45))
        pygame.draw.ellipse(surf, body, lid)
        # A thin dark lash-line under the lid so the half-lid reads crisp.
        pygame.draw.line(surf, BODY_DK,
                         (int(ex - eye_r * 0.92), int(ey - eye_r * 0.10)),
                         (int(ex + eye_r * 0.92), int(ey - eye_r * 0.02)),
                         max(1, int(1.2 * ss)))

    # — Nose: a small dark upside-down heart skull-hole between + below the eyes.
    nose_y = cy + r * 0.30
    nose = [(cx, nose_y + r * 0.12), (cx - r * 0.10, nose_y - r * 0.05),
            (cx + r * 0.10, nose_y - r * 0.05)]
    pygame.draw.polygon(surf, INK, [(int(x), int(y)) for x, y in nose])

    # — Mouth: a gentle bone tusk-grin. A soft dark mouth seat, a row of little
    #   even teeth, two modest up-curling tusks at the corners — sleepy-cute.
    grin_y = cy + r * 0.64
    grin_hw = r * 0.70
    grin_h = r * 0.34
    seat_top, seat_bot = [], []
    n = 16
    for i in range(n + 1):
        xr = -1.0 + 2.0 * (i / n)
        x = cx + xr * grin_hw
        lift = grin_h * 0.50 * (xr * xr)
        seat_top.append((x, grin_y - grin_h * 0.5 + lift))
        seat_bot.append((x, grin_y + grin_h * 0.5 + lift * 0.4))
    seat = seat_top + seat_bot[::-1]
    pygame.draw.polygon(surf, INK, [(int(x), int(y)) for x, y in seat])

    teeth = 6
    gap = grin_hw * 0.12
    tw = (grin_hw * 1.55 - gap * (teeth - 1)) / teeth
    th = grin_h * 0.46
    for i in range(teeth):
        tx = -grin_hw * 0.78 + i * (tw + gap)
        xr = (tx + tw * 0.5) / grin_hw
        ty = grin_y - grin_h * 0.5 + grin_h * 0.50 * (xr * xr) + ss
        rect = pygame.Rect(int(cx + tx + ss * 0.5), int(ty),
                           int(tw - ss * 0.5), int(th))
        pygame.draw.rect(surf, BONE, rect, border_radius=max(1, int(1.2 * ss)))
        pygame.draw.rect(surf, BONE_DK, rect, max(1, int(ss)),
                         border_radius=max(1, int(1.2 * ss)))

    for s in (-1, 1):
        bx = cx + s * grin_hw * 0.84
        by = grin_y + grin_h * 0.08
        tusk = [
            (bx, by),
            (bx + s * grin_hw * 0.14, by - grin_h * 0.85),
            (bx + s * grin_hw * 0.30, by - grin_h * 0.58),
            (bx + s * grin_hw * 0.18, by + grin_h * 0.30),
        ]
        pygame.draw.polygon(surf, BONE_DK, [(int(x), int(y)) for x, y in tusk])
        inner_k = [(bx + s * ss, by - ss),
                   (bx + s * grin_hw * 0.12, by - grin_h * 0.74),
                   (bx + s * grin_hw * 0.24, by - grin_h * 0.50),
                   (bx + s * grin_hw * 0.16, by + grin_h * 0.18)]
        pygame.draw.polygon(surf, BONE, [(int(x), int(y)) for x, y in inner_k])


# ── the whole creature: head + trailing orb-string, on one surface ───────────

def _face_tell(surf, cx, cy, r, ss):
    """A baked LOW-RES face tell (icon gate): two fat gold eye-dots + a single
    dark grin-bar stamped over the detailed face, sized so smoothscale to true
    32px PRESERVES a recognizable sleepy-skull face instead of mushing to a
    speck. Gold eye-dots double as the contained-warm tell at icon scale."""
    eye_dx = r * 0.44
    eye_dy = -r * 0.04
    eye_rr = r * 0.24
    for s in (-1, 1):
        ex, ey = cx + s * eye_dx, cy + eye_dy
        pygame.draw.circle(surf, BODY_DK, (int(ex), int(ey)), int(eye_rr * 1.15))
        pygame.draw.circle(surf, ORB, (int(ex), int(ey)), int(eye_rr))
        pygame.draw.circle(surf, ORB_CORE, (int(ex), int(ey)), int(eye_rr * 0.42))
    gw = r * 0.78
    gy = cy + r * 0.56
    gh = r * 0.18
    top, bot = [], []
    n = 12
    for i in range(n + 1):
        xr = -1.0 + 2.0 * (i / n)
        x = cx + xr * gw
        lift = gh * 1.25 * (xr * xr)
        top.append((x, gy - gh * 0.5 + lift))
        bot.append((x, gy + gh * 0.5 + lift))
    pygame.draw.polygon(surf, INK, [(int(x), int(y)) for x, y in (top + bot[::-1])])


def build_krasue(scale=1.0, ss=6, *, night=False, compact=False):
    """The full creature on its own transparent surface: the floating skull-
    lantern head up top, a viscera ORB-STRING streaming straight down beneath it
    tipped with the cracked bottom lantern-orb. Returns an outlined surface.
    EPIC pipeline: built LARGE at SS=6, smoothscaled down for crisp downscale.

    `compact` is the GAMEPLAY / 32px-icon variant: the HEAD is grown to dominate
    ~55-60% of the vertical budget and the string cut to 3 orbs, so the icon reads
    'sleepy skull on a short orb-string' — never a faint thread + speck. Compact
    also bakes a low-res face tell."""
    head_r = int(46 * scale) * ss
    string_mult = 1.20 if compact else 2.85
    string_len = int(head_r * string_mult)
    n_orbs = 3 if compact else 6
    side_pad = int(24 * scale) * ss        # room for wave + orb halos
    top_pad = int(16 * scale) * ss
    bot_pad = int(24 * scale) * ss         # room for the bottom orb glow halo

    head_cx_off = side_pad + head_r + int(6 * scale) * ss
    head_cy = top_pad + head_r * 1.04

    # The orb-string springs from just under the jaw.
    string_top_y = head_cy + head_r * 1.16
    feet_y = string_top_y + string_len

    W = int(head_cx_off * 2)
    H = int(feet_y + bot_pad)
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    cx = W // 2

    base_r = head_r * 0.30
    _orb_string(surf, cx, string_top_y, string_len, base_r, ss,
                n_orbs=n_orbs, wave=0.6 if compact else 1.0, phase=0.5,
                end_cracked=True, night=night)

    _head(surf, cx, head_cy, head_r, ss, night=night)
    if compact:
        _face_tell(surf, cx, head_cy, head_r, ss)

    out_w = int(surf.get_width() / ss)
    out_h = int(surf.get_height() / ss)
    smallv = pygame.transform.smoothscale(surf, (out_w, out_h))
    return _add_outline(smallv)


# ── pillar pair (prop -> pillar mirror proof) ────────────────────────────────

OVERHANG = 12


def _orb_column(surf, cx, top_y, bot_y, base_r, ss):
    """The repeatable PILLAR BODY: the viscera orb-string as a straight tiling
    shaft — a thin mauve sinew threaded with evenly-spaced gold gut-orbs at a
    steady on-axis cadence (the band that mirrors top<->bottom). Drawn vertical
    (no wave) so it tiles cleanly along the post."""
    length = bot_y - top_y
    # The sinew cord down the axis.
    pygame.draw.line(surf, SINEW_DK, (int(cx), int(top_y)), (int(cx), int(bot_y)),
                     max(2, int(2.8 * ss)))
    pygame.draw.line(surf, SINEW, (int(cx - 0.3 * ss), int(top_y)),
                     (int(cx - 0.3 * ss), int(bot_y)), max(1, int(1.4 * ss)))
    # Evenly-spaced orbs — the organ band that repeats top<->bottom.
    band = base_r * 2.6
    n = max(2, int(length / band))
    band = length / n
    for i in range(n):
        by = top_y + (i + 0.5) * band
        _gut_orb(surf, cx, by, base_r, ss)


def _cracked_cap(surf, cx, cap_base_y, base_r, ss, *, point_up, night=False):
    """The detachable GAP-EDGE CAP, derived from the creature's OWN form: a short
    sinew neck of one small orb, then a big CRACKED bottom lantern-orb hanging at
    the gap edge and radiating gold INTO the gap. `point_up` reaches toward the
    gap (up for a bottom pillar). Sits on-axis so the top<->bottom mirror is
    clean and there is no top-heavy cap (the cap == one larger orb, not a crown)."""
    d = -1 if point_up else 1
    # A short connective neck: one small orb between shaft and the lantern.
    neck_y = cap_base_y + d * base_r * 1.6
    _gut_orb(surf, cx, neck_y, base_r * 0.7, ss, night=night)
    # The big cracked bottom lantern-orb at the gap edge.
    hy = cap_base_y + d * base_r * 4.0
    _gut_orb(surf, cx, hy, base_r * 1.45, ss, night=night, cracked=True)


def _orb_pillar_obstacle(height, ss, *, flip, night=False):
    """One viscera orb-string PILLAR obstacle: the beaded orb-string fills the
    post and the cracked bottom lantern-orb CAP sits at the GAP-facing edge,
    radiating INTO the gap. `flip=True` is the TOP pillar — cap at the bottom
    (gap) edge, reaching DOWN into the gap; `flip=False` is the BOTTOM pillar —
    cap at the TOP (gap) edge, reaching UP. Both mirror the same orb-string body
    into a clean vertical orb-pillar lanterned at the gap."""
    bw = (PIPE_W + 2 * OVERHANG) * ss
    bh = max(1, int(height)) * ss
    surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
    cx = bw // 2
    base_r = 13 * ss
    cap_band = int(56 * ss)
    if flip:
        _orb_column(surf, cx, 0, bh - cap_band, base_r, ss)
        _cracked_cap(surf, cx, bh - cap_band, base_r, ss, point_up=False, night=night)
    else:
        _orb_column(surf, cx, cap_band, bh, base_r, ss)
        _cracked_cap(surf, cx, cap_band, base_r, ss, point_up=True, night=night)
    out = pygame.transform.smoothscale(surf, (PIPE_W + 2 * OVERHANG, max(1, int(height))))
    return _add_outline(out)


# ── sheet composition ────────────────────────────────────────────────────────

def _label(surf, font, text, x, y, color=(245, 240, 230)):
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


def main():
    pygame.font.init()
    font = pygame.font.SysFont("dejavusans", 15, bold=True)
    small = pygame.font.SysFont("dejavusans", 12)

    SW, SH = 1180, 760
    sheet = pygame.Surface((SW, SH))
    sheet.fill((58, 56, 62))          # neutral grey bg
    _label(sheet, font,
            "KRASUE  —  leyak-EPIC #1  —  cool dusk-mauve skull-lantern + warm-gold gut-orb STRING  —  round 1", 18, 12)
    _label(sheet, small,
            "EPIC pipeline: rendered LARGE @ SS=6 then smoothscaled. Body COOL (mauve); firefly-gold confined STRICTLY to discrete gut-orbs. Orb-string IS the pillar.",
            18, 32, (210, 200, 218))

    # — Cell A: BIG hero sprite on a dusk-mauve sky.
    panel = pygame.Rect(18, 56, 360, 580)
    bgA = _sky(panel.w, panel.h, (52, 36, 66), (104, 70, 108), (176, 132, 150))
    sheet.blit(bgA, panel.topleft)
    pygame.draw.rect(sheet, (130, 110, 140), panel, 2, border_radius=8)
    boss = build_krasue(scale=1.9, ss=6)
    sheet.blit(boss, (panel.centerx - boss.get_width() // 2, panel.y + 50))
    _label(sheet, font, "(a) HERO  big @ SS=6", panel.x + 8, panel.y + 8)
    _label(sheet, small, "skull-lantern head + 6 gut-orbs on a thin sinew + cracked end-orb",
           panel.x + 8, panel.y + 28, (232, 222, 238))

    # — Cell B: orb-string as a tileable PILLAR pair @ TRUE obstacle scale (NIGHT),
    #   plus a 2x zoom on the CAP band proving the cracked lantern-orb lights the gap.
    panelB = pygame.Rect(394, 56, 360, 580)
    bg = _sky(panelB.w, panelB.h, (8, 8, 32), (20, 18, 58), (44, 32, 78), stars=True)
    sheet.blit(bg, panelB.topleft)
    pygame.draw.rect(sheet, (130, 110, 140), panelB, 2, border_radius=8)
    _label(sheet, font, "(b) PROP -> PILLAR  @ TRUE scale (NIGHT)", panelB.x + 8, panelB.y + 8)

    pw = PIPE_W + 2 * OVERHANG
    slice_h = 470
    slice_x = panelB.x + 24
    slice_y = panelB.y + 44
    gap_top = 150
    gap_h = 128
    top_h = gap_top
    bot_h = slice_h - gap_top - gap_h
    top_pillar = _orb_pillar_obstacle(top_h, 6, flip=True, night=True)
    bot_pillar = _orb_pillar_obstacle(bot_h, 6, flip=False, night=True)
    sheet.blit(top_pillar, (slice_x - 2, slice_y - 2))
    sheet.blit(bot_pillar, (slice_x - 2, slice_y + gap_top + gap_h - 2))
    pygame.draw.rect(sheet, (210, 196, 222), (slice_x - 4, slice_y - 4, pw + 8, slice_h + 8), 1)
    _label(sheet, small, "1x native (82px): even gut-orb", slice_x - 2, slice_y + slice_h + 6, (225, 215, 232))
    _label(sheet, small, "cadence tiles; cracked end-orb", slice_x - 2, slice_y + slice_h + 22, (255, 236, 196))
    _label(sheet, small, "LANTERNS the gap (mirrored)", slice_x - 2, slice_y + slice_h + 38, (255, 236, 196))

    cap_band = 56
    zw, zh = pw, 170
    zoom_src = pygame.Surface((zw, zh), pygame.SRCALPHA)
    top_anchor = 12
    zoom_src.blit(top_pillar, (-2, -(top_h - cap_band - top_anchor) - 2))
    zoom_gap = zh - 2 * cap_band - 2 * top_anchor
    bot_anchor = top_anchor + cap_band + zoom_gap
    zoom_src.blit(bot_pillar, (-2, bot_anchor - 2))
    zoom = pygame.transform.scale(zoom_src, (zw * 2, zh * 2))
    zx = panelB.x + 178
    zy = panelB.y + 96
    zbg = _sky(zw * 2, zh * 2, (8, 8, 32), (16, 14, 48), (30, 22, 64))
    sheet.blit(zbg, (zx, zy))
    pygame.draw.rect(sheet, (210, 196, 222), (zx - 1, zy - 1, zw * 2 + 2, zh * 2 + 2), 1)
    sheet.blit(zoom, (zx, zy))
    _label(sheet, small, "2x zoom of the CAP band:", zx - 2, zy - 16, (255, 255, 255))
    _label(sheet, small, "cracked bottom lantern-orb", zx - 2, zy + zh * 2 + 6, (255, 236, 196))
    _label(sheet, small, "(creature's own form, on-axis)", zx - 2, zy + zh * 2 + 22, (255, 236, 196))

    # — Cell C: the GAMEPLAY icon (compact, head-dominant) — the TRUE 32px chip on
    #   a day sky AND a night sky to prove legibility, then a 4x audit + grayscale.
    panelC = pygame.Rect(770, 56, 392, 580)
    pygame.draw.rect(sheet, (44, 42, 48), panelC, border_radius=8)
    pygame.draw.rect(sheet, (130, 110, 140), panelC, 2, border_radius=8)
    _label(sheet, font, "(c) GAMEPLAY ICON  —  TRUE 32px legibility", panelC.x + 8, panelC.y + 8)
    _label(sheet, small, "head ~55-60% of the icon / short 3-orb string", panelC.x + 8, panelC.y + 28,
           (232, 222, 238))

    boss1x = build_krasue(scale=0.62, ss=6, compact=True)
    boss1x_n = build_krasue(scale=0.62, ss=6, night=True, compact=True)
    day = _sky(180, 300, (40, 110, 200), (90, 170, 230), (170, 220, 245))
    night = _sky(180, 300, (8, 8, 32), (20, 18, 58), (44, 32, 78), stars=True)

    dy = panelC.y + 46
    sheet.blit(day, (panelC.x + 14, dy))
    sheet.blit(night, (panelC.x + 200, dy))
    sheet.blit(boss1x, (panelC.x + 14 + 90 - boss1x.get_width() // 2, dy + 8))
    sheet.blit(boss1x_n, (panelC.x + 200 + 90 - boss1x_n.get_width() // 2, dy + 8))
    _label(sheet, small, "DAY", panelC.x + 14 + 6, dy + 6, (20, 30, 26))
    _label(sheet, small, "NIGHT", panelC.x + 200 + 6, dy + 6, (255, 236, 196))

    gy = dy + 312
    _label(sheet, small, "TRUE 32px chip on day + night sky (1x, no blow-up):",
           panelC.x + 14, gy - 2, (228, 218, 228))
    icon_src = build_krasue(scale=1.0, ss=6, compact=True)
    target_h = 64
    sc = target_h / icon_src.get_height()
    icon = pygame.transform.smoothscale(
        icon_src, (max(1, int(icon_src.get_width() * sc)), target_h))
    icon32 = pygame.transform.smoothscale(
        icon_src, (max(1, int(icon_src.get_width() * (32 / icon_src.get_height()))), 32))
    swatches = [
        ((40, 110, 200), "day 1x"),
        ((44, 32, 78), "night 1x"),
        ((104, 70, 108), "dusk 1x"),
    ]
    sx = panelC.x + 14
    sw = 86
    for col, lab in swatches:
        chip = pygame.Rect(sx, gy + 16, sw, 84)
        pygame.draw.rect(sheet, col, chip, border_radius=4)
        sheet.blit(icon32, (chip.centerx - icon32.get_width() // 2,
                            chip.centery - icon32.get_height() // 2))
        _label(sheet, small, lab, chip.x + 4, chip.y + 2, (240, 240, 240))
        sx += sw + 10

    chip = pygame.Rect(panelC.x + 14, gy + 112, 86, 84)
    pygame.draw.rect(sheet, (90, 90, 96), chip, border_radius=4)
    sheet.blit(icon32, (chip.centerx - icon32.get_width() // 2,
                        chip.centery - icon32.get_height() // 2))
    sheet.blit(icon, (chip.centerx + 22, chip.centery - icon.get_height() // 2))
    _label(sheet, small, "32 / 64px", chip.x + 4, chip.y + 2, (240, 240, 240))
    blow = pygame.transform.scale(icon32, (icon32.get_width() * 4, icon32.get_height() * 4))
    sheet.blit(blow, (panelC.x + 116, gy + 8))
    _label(sheet, small, "4x blow-up of the 32px icon (face tell baked)",
           panelC.x + 116, gy + 8 + blow.get_height() + 2, (228, 218, 228))

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

    gray = _to_gray(icon)
    chip = pygame.Rect(panelC.x + 290, gy + 112, 86, 84)
    pygame.draw.rect(sheet, (120, 124, 120), chip, border_radius=4)
    sheet.blit(gray, (chip.centerx - gray.get_width() // 2,
                      chip.centery - gray.get_height() // 2))
    _label(sheet, small, "grayscale", chip.x + 4, chip.y + 2, (24, 24, 24))

    # — Footer captions.
    _label(sheet, small,
           "STYLE: flat saturated fills; hard 1-2px ink keyline (28,22,30); dark-core -> flat-fill -> top-left lilac rim-sheen triad; 1px grown outline; chibi; scary-CUTE (sleepy half-lids).",
           18, SH - 84, (205, 196, 214))
    _label(sheet, small,
           "BODY COOL: dusk-mauve face/skull; firefly-gold ONLY inside the gut-orbs (contained warm glow, never on flesh). Membrane veining + inner orb glow-lobes = elevated detail.",
           18, SH - 64, (205, 196, 214))
    _label(sheet, small,
           "PROP->PILLAR: the evenly-beaded gut-orb string tiles as the shaft (thin sinew); the cracked bottom lantern-orb (own form) caps + LIGHTS the gap on-axis. Clean mirror, no top-heavy cap.",
           18, SH - 44, (205, 196, 214))

    out_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(out_dir, "round_1.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path)


if __name__ == "__main__":
    main()
