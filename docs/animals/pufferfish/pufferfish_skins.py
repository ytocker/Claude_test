"""Candidate PUFFERFISH skins for the ANIMALS Store — round-1 exploration.

Five genuinely different takes on ONE creature: a near-perfect spiky sphere
with tiny fins and a pouty face. The signature 40px tell is the RADIAL
SPIKE-HALO silhouette — a ball of spikes that no current animal owns. The
"flap" is reinterpreted as a comedic inflate PULSE: on the down-pose the body
swells bigger and the spikes flare out long; on the up-pose it deflates a
touch and the spikes pull in — a balloon catching and releasing breath.

Contract (mirrors game/animal_skins.py so the winner lifts straight in):

  * `build_pufferfish_vN(wing_angle_deg) -> pygame.Surface`  one flat frame
    on a 64×84 SRCALPHA canvas, BODY mass centred at (BCX,BCY)=(32,44).
  * a cached `(frame_idx, tilt_deg) -> Surface` getter from
    `_make_prebuilt_skin(build_fn)`.
  * `BUILDERS = {label: getter, ...}` for the review sheet.

Body sits at the base anchor (fairness: collision is a fixed 14px circle at
the body centre, sprite-independent) so the round ball never bloats past a
fair hitbox — the inflate gag is read entirely through the spike halo + a
small body-radius wobble, not a giant creature.

North star: "a skin lives or dies at 40px in motion." Each version leans on
the spike-halo ring + one high-contrast face feature (the pouty lips / wide
eyes) that survives the downscale against bright-day AND night skies.
"""
import math
import pygame

from game import parrot
from game.parrot import (
    SPRITE_W, SPRITE_H, _WING_ANGLES, _add_outline, _aaellipse,
)


# ── tall-canvas constants (match game/animal_skins.py exactly) ───────────────
COMPOSITE_W = SPRITE_W          # 64
COMPOSITE_H = 84                # headroom (pufferfish uses little of it)
DY          = 12

BCX, BCY = 32, 32 + DY          # body centre  → (32, 44)
HCX, HCY = 44, 22 + DY          # head anchor  → (44, 34) — face is high/right
CROWN_Y  = 12 + DY              # top of head  → 24


def _make_prebuilt_skin(build_fn):
    """Cached `(frame_idx, tilt_deg) -> Surface` getter (local copy)."""
    state = {"frames": None, "rot": {}}

    def getter(frame_idx, tilt_deg):
        if state["frames"] is None:
            state["frames"] = [_add_outline(build_fn(a)) for a in _WING_ANGLES]
        frames = state["frames"]
        frame_idx %= len(frames)
        key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
        s = state["rot"].get(key)
        if s is None:
            s = pygame.transform.rotozoom(frames[frame_idx], key[1], 1.0)
            state["rot"][key] = s
        return s

    return getter


def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _eye(surf, cx, cy, r, *, iris=(58, 42, 18), white=(255, 250, 240),
         glint=True):
    pygame.draw.circle(surf, white, (cx, cy), r)
    pygame.draw.circle(surf, iris, (cx + max(1, r // 4), cy), max(2, r - 2))
    if glint:
        pygame.draw.circle(surf, (255, 255, 255), (cx - r // 3, cy - r // 3),
                           max(1, r // 3))


def _flap(angle_deg):
    """0..1 'wing is up' factor. _WING_ANGLES runs 50 (down) → -40 (up)."""
    return (angle_deg + 40) / 90.0


def _inflate(angle_deg):
    """Comedic pulse: 1.0 fully INFLATED on the down-pose, ~0.0 deflated on
    the up-pose. The down-stroke is the puff (body swells, spikes flare)."""
    return 1.0 - _flap(angle_deg)


def _spike_ring(surf, cx, cy, r_in, length, n, col_d, col, start=0.0,
                width_deg=None, taper=0.55, tip_col=None):
    """Draw a radial halo of triangular spikes around (cx,cy).

    Each spike is a filled triangle rooted on the body circle of radius r_in,
    pointing outward `length` px. Two-tone: a dark flank (col_d) under a
    lighter face (col) so the ring reads as volume, not a flat starburst.
    The whole ring is what survives the 40px downscale — it is THE tell."""
    if width_deg is None:
        width_deg = (360.0 / n) * taper
    half = math.radians(width_deg) * 0.5
    for i in range(n):
        a = start + (2 * math.pi) * i / n
        bx, by = math.cos(a), math.sin(a)
        # Base corners on the body rim, tip out along the radius.
        l_a, r_a = a - half, a + half
        p_l = (cx + math.cos(l_a) * r_in, cy + math.sin(l_a) * r_in)
        p_r = (cx + math.cos(r_a) * r_in, cy + math.sin(r_a) * r_in)
        tip = (cx + bx * (r_in + length), cy + by * (r_in + length))
        # Dark flank slightly offset down-right for a cheap drop-shadow read.
        pygame.draw.polygon(surf, col_d,
                            [(p_l[0] + 0.6, p_l[1] + 0.8),
                             (p_r[0] + 0.6, p_r[1] + 0.8),
                             (tip[0] + 0.6, tip[1] + 0.8)])
        pygame.draw.polygon(surf, col, [p_l, p_r, tip])
        if tip_col is not None:
            pygame.draw.circle(surf, tip_col, (int(tip[0]), int(tip[1])), 1)


def _fin(angle_deg, sgn, base, scale=1.0):
    """Tiny waving pectoral fin (the pufferfish flap). `base` is the body
    colour tuple; flips for the far side. Fans a little with the stroke."""
    w = pygame.Surface((24, 22), pygame.SRCALPHA)
    fan = (angle_deg + 40) / 90.0           # 0..1
    spread = 3 + int(fan * 4)
    pts = [(4, 11), (20, 11 - spread), (22, 11), (20, 11 + spread)]
    pygame.draw.polygon(w, base[1], pts)
    pygame.draw.polygon(w, base[0], pts, 1)
    # Two fin rays for a little life.
    pygame.draw.line(w, base[0], (6, 11), (20, 11 - spread + 1), 1)
    pygame.draw.line(w, base[0], (6, 11), (20, 11 + spread - 1), 1)
    if scale != 1.0:
        w = pygame.transform.smoothscale(
            w, (max(1, int(24 * scale)), max(1, int(22 * scale))))
    if sgn < 0:
        w = pygame.transform.flip(w, True, False)
    return w


def _rot_blit(surf, wing, anchor):
    surf.blit(wing, wing.get_rect(center=anchor).topleft)


# ═════════════════════════════════════════════════════════════════════════════
# V1 · CLASSIC YELLOW PUFF — the canonical golden balloon. Dense medium spikes
#     all round, a round body, a cute pouty O-mouth, big friendly eyes. The
#     "default" everyone pictures. Flap = clean inflate/deflate pulse.
# ═════════════════════════════════════════════════════════════════════════════
_V1_BODY   = (246, 196, 83)
_V1_BODY_D = (214, 158, 48)
_V1_BODY_H = (255, 230, 150)
_V1_BELLY  = (255, 241, 201)
_V1_SPIKE  = (201, 138, 30)
_V1_SPIKE_D = (160, 104, 20)
_V1_DARK   = (58, 42, 18)


def build_pufferfish_v1(wing_angle_deg):
    surf = _new()
    inf = _inflate(wing_angle_deg)
    r = 15 + int(inf * 2)                    # body swells on the puff
    spk = 6 + int(inf * 4)                   # spikes flare out
    cx, cy = BCX, BCY

    # Tiny tail fin peeking out the back.
    _rot_blit(surf, _fin(wing_angle_deg, +1, (_V1_SPIKE_D, _V1_BODY_D)),
              (cx - r - 5, cy + 3))

    # HERO halo: dense ring of spikes, drawn under the body so roots tuck in.
    _spike_ring(surf, cx, cy, r - 2, spk, 18, _V1_SPIKE_D, _V1_SPIKE,
                start=0.18, taper=0.62)

    # Round body.
    _aaellipse(surf, _V1_BODY_D, (cx + 1, cy + 1), r, r)
    _aaellipse(surf, _V1_BODY, (cx, cy), r - 1, r - 1)
    _aaellipse(surf, _V1_BELLY, (cx - 1, cy + 4), r - 6, r - 7)
    _aaellipse(surf, _V1_BODY_H, (cx - 5, cy - 6), 5, 4)
    # Light belly spots.
    for sx, sy in ((30, 50), (35, 52), (28, 47)):
        pygame.draw.circle(surf, _V1_BODY_D, (sx, sy), 1)

    # Side pectoral fin waving.
    _rot_blit(surf, _fin(wing_angle_deg, -1, (_V1_SPIKE_D, _V1_BODY_H),
                         scale=0.9), (cx + r - 2, cy + 2))

    # Face: wide eyes + pouty O lips.
    _eye(surf, HCX - 3, HCY + 2, 4, iris=_V1_DARK)
    _eye(surf, HCX + 5, HCY + 2, 4, iris=_V1_DARK)
    # Pouty O mouth — the signature face feature.
    pygame.draw.circle(surf, _V1_DARK, (HCX + 1, HCY + 9), 3)
    pygame.draw.circle(surf, (120, 60, 60), (HCX + 1, HCY + 9), 2)
    # Little blush.
    pygame.draw.circle(surf, (255, 170, 120), (HCX - 6, HCY + 7), 2)
    pygame.draw.circle(surf, (255, 170, 120), (HCX + 8, HCY + 7), 2)
    return surf


get_pufferfish_v1 = _make_prebuilt_skin(build_pufferfish_v1)


# ═════════════════════════════════════════════════════════════════════════════
# V2 · GRUMPY PORCUPINEFISH — brown, LONG sparse spikes (true porcupinefish),
#     a slightly teardrop body, heavy angry brow + frown. The dangerous-but-cute
#     one. The long spikes own the silhouette; the scowl is the face tell.
# ═════════════════════════════════════════════════════════════════════════════
_V2_BODY   = (180, 132, 84)
_V2_BODY_D = (138, 96, 56)
_V2_BODY_H = (216, 176, 128)
_V2_BELLY  = (236, 214, 178)
_V2_SPIKE  = (104, 72, 40)
_V2_SPIKE_D = (74, 50, 28)
_V2_DARK   = (44, 30, 16)


def build_pufferfish_v2(wing_angle_deg):
    surf = _new()
    inf = _inflate(wing_angle_deg)
    r = 14 + int(inf * 2)
    spk = 9 + int(inf * 5)                   # long, dramatic spikes
    cx, cy = BCX, BCY + 1

    _rot_blit(surf, _fin(wing_angle_deg, +1, (_V2_SPIKE_D, _V2_BODY_D)),
              (cx - r - 6, cy + 2))

    # HERO halo: FEWER, LONGER spikes — the porcupinefish read.
    _spike_ring(surf, cx, cy, r - 2, spk, 12, _V2_SPIKE_D, _V2_SPIKE,
                start=0.0, taper=0.5, tip_col=_V2_DARK)

    # Slightly teardrop body (wider at bottom).
    _aaellipse(surf, _V2_BODY_D, (cx + 1, cy + 2), r, r + 1)
    _aaellipse(surf, _V2_BODY, (cx, cy + 1), r - 1, r)
    _aaellipse(surf, _V2_BELLY, (cx - 1, cy + 5), r - 6, r - 6)
    _aaellipse(surf, _V2_BODY_H, (cx - 5, cy - 5), 5, 3)
    # Mottled spots.
    for sx, sy in ((28, 40), (34, 38), (30, 50), (36, 48), (26, 46)):
        pygame.draw.circle(surf, _V2_SPIKE_D, (sx, sy), 1)

    _rot_blit(surf, _fin(wing_angle_deg, -1, (_V2_SPIKE_D, _V2_BODY_H),
                         scale=0.9), (cx + r - 1, cy + 1))

    # GRUMPY face: heavy brows angled down to the centre + frown.
    _eye(surf, HCX - 3, HCY + 3, 4, iris=_V2_DARK)
    _eye(surf, HCX + 5, HCY + 3, 4, iris=_V2_DARK)
    pygame.draw.line(surf, _V2_DARK, (HCX - 7, HCY - 2), (HCX - 1, HCY + 1), 2)
    pygame.draw.line(surf, _V2_DARK, (HCX + 9, HCY - 2), (HCX + 3, HCY + 1), 2)
    # Down-curved frown.
    pygame.draw.arc(surf, _V2_DARK, (HCX - 4, HCY + 10, 10, 8),
                    math.radians(20), math.radians(160), 2)
    return surf


get_pufferfish_v2 = _make_prebuilt_skin(build_pufferfish_v2)


# ═════════════════════════════════════════════════════════════════════════════
# V3 · SPOTTED TROPICAL — teal-spotted guineafowl-puffer palette over a warm
#     base, short stubby spikes (almost bumps) so the SPOTS carry the read, a
#     cute closed-eye happy face. The colourful, friendly variant.
# ═════════════════════════════════════════════════════════════════════════════
_V3_BODY   = (74, 150, 150)
_V3_BODY_D = (44, 110, 112)
_V3_BODY_H = (130, 200, 196)
_V3_BELLY  = (224, 244, 240)
_V3_SPIKE  = (40, 96, 100)
_V3_SPIKE_D = (28, 72, 76)
_V3_SPOT   = (250, 248, 240)
_V3_DARK   = (20, 40, 44)


def build_pufferfish_v3(wing_angle_deg):
    surf = _new()
    inf = _inflate(wing_angle_deg)
    r = 15 + int(inf * 2)
    spk = 3 + int(inf * 3)                   # short stubby bumps
    cx, cy = BCX, BCY

    _rot_blit(surf, _fin(wing_angle_deg, +1, (_V3_SPIKE_D, _V3_BODY_D)),
              (cx - r - 4, cy + 3))

    # Stubby spike halo: many, short — a bumpy rim, not a starburst.
    _spike_ring(surf, cx, cy, r - 1, spk, 24, _V3_SPIKE_D, _V3_SPIKE,
                start=0.1, taper=0.7)

    # Round body.
    _aaellipse(surf, _V3_BODY_D, (cx + 1, cy + 1), r, r)
    _aaellipse(surf, _V3_BODY, (cx, cy), r - 1, r - 1)
    _aaellipse(surf, _V3_BELLY, (cx - 1, cy + 5), r - 6, r - 7)
    _aaellipse(surf, _V3_BODY_H, (cx - 5, cy - 6), 5, 4)
    # SIGNATURE: scattered white spots over the upper body (the read).
    for sx, sy, sr in ((26, 38, 2), (33, 36, 2), (38, 41, 1), (24, 44, 1),
                       (30, 46, 2), (37, 49, 1), (27, 50, 1), (32, 41, 1)):
        pygame.draw.circle(surf, _V3_SPOT, (sx, sy), sr)

    _rot_blit(surf, _fin(wing_angle_deg, -1, (_V3_SPIKE_D, _V3_BODY_H),
                         scale=0.9), (cx + r - 2, cy + 2))

    # Happy closed-eye face: two upward arcs + a small smile.
    pygame.draw.arc(surf, _V3_DARK, (HCX - 7, HCY, 7, 7),
                    math.radians(20), math.radians(160), 2)
    pygame.draw.arc(surf, _V3_DARK, (HCX + 1, HCY, 7, 7),
                    math.radians(20), math.radians(160), 2)
    pygame.draw.arc(surf, _V3_DARK, (HCX - 3, HCY + 6, 9, 7),
                    math.radians(200), math.radians(340), 2)
    pygame.draw.circle(surf, (255, 150, 120), (HCX - 7, HCY + 7), 2)
    pygame.draw.circle(surf, (255, 150, 120), (HCX + 9, HCY + 7), 2)
    return surf


get_pufferfish_v3 = _make_prebuilt_skin(build_pufferfish_v3)


# ═════════════════════════════════════════════════════════════════════════════
# V4 · STAR-BURST PUFF — maximum drama: a perfectly symmetric dense halo of
#     SHARP needle spikes radiating like a sea-urchin star, two-tone tipped, on
#     a bright yellow ball with tiny startled eyes. The boldest 40px silhouette.
#     The flap genuinely PULSES the whole star bigger/smaller.
# ═════════════════════════════════════════════════════════════════════════════
_V4_BODY   = (248, 200, 72)
_V4_BODY_D = (212, 154, 40)
_V4_BODY_H = (255, 234, 150)
_V4_BELLY  = (255, 244, 206)
_V4_SPIKE  = (236, 168, 40)
_V4_SPIKE_D = (190, 120, 24)
_V4_TIP    = (255, 240, 190)
_V4_DARK   = (52, 36, 14)


def build_pufferfish_v4(wing_angle_deg):
    surf = _new()
    inf = _inflate(wing_angle_deg)
    r = 14 + int(inf * 2)
    spk = 7 + int(inf * 6)                    # big pulse range
    cx, cy = BCX, BCY

    # Two staggered rings (offset half a step) for a denser urchin star — the
    # bright tip dots keep the needle points alive after the downscale.
    _spike_ring(surf, cx, cy, r - 1, spk, 16, _V4_SPIKE_D, _V4_SPIKE,
                start=0.0, taper=0.42, tip_col=_V4_TIP)
    _spike_ring(surf, cx, cy, r - 3, spk - 2, 16,
                _V4_SPIKE_D, _V4_BODY_H, start=math.pi / 16, taper=0.38)

    # Bright ball.
    _aaellipse(surf, _V4_BODY_D, (cx + 1, cy + 1), r, r)
    _aaellipse(surf, _V4_BODY, (cx, cy), r - 1, r - 1)
    _aaellipse(surf, _V4_BELLY, (cx - 1, cy + 4), r - 6, r - 7)
    _aaellipse(surf, _V4_BODY_H, (cx - 5, cy - 6), 6, 4)

    # Startled little dot eyes + a tiny O of surprise.
    _eye(surf, HCX - 3, HCY + 2, 4, iris=_V4_DARK)
    _eye(surf, HCX + 5, HCY + 2, 4, iris=_V4_DARK)
    pygame.draw.circle(surf, _V4_DARK, (HCX + 1, HCY + 9), 2)
    pygame.draw.circle(surf, (255, 170, 120), (HCX - 6, HCY + 7), 2)
    pygame.draw.circle(surf, (255, 170, 120), (HCX + 8, HCY + 7), 2)
    return surf


get_pufferfish_v4 = _make_prebuilt_skin(build_pufferfish_v4)


# ═════════════════════════════════════════════════════════════════════════════
# V5 · DEFLATED-CHEEK BLOWFISH — the gag-forward one: a big puffed cheek bulge
#     to one side, asymmetric so it reads as MID-BLOW, fewer soft spikes, huge
#     pouty kissy lips, half-lidded sleepy eyes. The comedic personality pick.
# ═════════════════════════════════════════════════════════════════════════════
_V5_BODY   = (244, 188, 96)
_V5_BODY_D = (208, 148, 56)
_V5_BODY_H = (255, 226, 156)
_V5_BELLY  = (255, 238, 198)
_V5_SPIKE  = (196, 132, 36)
_V5_SPIKE_D = (158, 100, 24)
_V5_LIP    = (224, 110, 96)
_V5_LIP_D  = (170, 70, 60)
_V5_DARK   = (58, 40, 18)


def build_pufferfish_v5(wing_angle_deg):
    surf = _new()
    inf = _inflate(wing_angle_deg)
    r = 14 + int(inf * 2)
    spk = 5 + int(inf * 4)
    cx, cy = BCX - 1, BCY

    _rot_blit(surf, _fin(wing_angle_deg, +1, (_V5_SPIKE_D, _V5_BODY_D)),
              (cx - r - 5, cy + 3))

    # Soft moderate spike halo.
    _spike_ring(surf, cx, cy, r - 2, spk, 16, _V5_SPIKE_D, _V5_SPIKE,
                start=0.2, taper=0.6)

    # Body with an extra puffed CHEEK bulge toward the face (asymmetric blow).
    _aaellipse(surf, _V5_BODY_D, (cx + 1, cy + 1), r, r)
    _aaellipse(surf, _V5_BODY, (cx, cy), r - 1, r - 1)
    # Cheek bulge — a second overlapping circle pushing toward the mouth.
    _aaellipse(surf, _V5_BODY_D, (cx + r - 4, cy + 4), 8, 7)
    _aaellipse(surf, _V5_BODY, (cx + r - 5, cy + 3), 7, 6)
    _aaellipse(surf, _V5_BODY_H, (cx + r - 7, cy + 1), 3, 2)
    _aaellipse(surf, _V5_BELLY, (cx - 2, cy + 5), r - 7, r - 7)
    _aaellipse(surf, _V5_BODY_H, (cx - 5, cy - 6), 5, 4)

    _rot_blit(surf, _fin(wing_angle_deg, -1, (_V5_SPIKE_D, _V5_BODY_H),
                         scale=0.85), (cx + r - 2, cy - 2))

    # Sleepy half-lidded eyes (a flat lid line over each).
    _eye(surf, HCX - 4, HCY + 2, 4, iris=_V5_DARK)
    _eye(surf, HCX + 4, HCY + 2, 4, iris=_V5_DARK)
    pygame.draw.line(surf, _V5_DARK, (HCX - 8, HCY), (HCX - 1, HCY), 2)
    pygame.draw.line(surf, _V5_DARK, (HCX + 1, HCY), (HCX + 8, HCY), 2)
    # HUGE pouty kissy lips — the gag tell, jutting forward off the cheek.
    pygame.draw.ellipse(surf, _V5_LIP_D, (HCX + 1, HCY + 6, 12, 9))
    pygame.draw.ellipse(surf, _V5_LIP, (HCX + 2, HCY + 6, 11, 7))
    pygame.draw.line(surf, _V5_LIP_D, (HCX + 3, HCY + 10),
                     (HCX + 12, HCY + 10), 1)
    pygame.draw.circle(surf, (255, 200, 200), (HCX + 5, HCY + 8), 1)
    return surf


get_pufferfish_v5 = _make_prebuilt_skin(build_pufferfish_v5)


# ─────────────────────────────────────────────────────────────────────────────
# Review registry: label → getter.
# ─────────────────────────────────────────────────────────────────────────────
BUILDERS = {
    "V1 · CLASSIC YELLOW":   get_pufferfish_v1,
    "V2 · GRUMPY PORCUPINE": get_pufferfish_v2,
    "V3 · SPOTTED TROPICAL": get_pufferfish_v3,
    "V4 · STAR-BURST":       get_pufferfish_v4,
    "V5 · KISSY BLOWFISH":   get_pufferfish_v5,
}

# 40px-tell summary for each version (used by the review sheet).
TELLS = {
    "V1 · CLASSIC YELLOW":   "dense spike halo + pouty O on a golden ball",
    "V2 · GRUMPY PORCUPINE": "long sparse spikes + angry scowl, brown",
    "V3 · SPOTTED TROPICAL": "teal ball, white spots + bumpy rim",
    "V4 · STAR-BURST":       "symmetric urchin needle-star, max pulse",
    "V5 · KISSY BLOWFISH":   "asymmetric cheek bulge + huge kissy lips",
}
