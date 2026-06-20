"""Candidate CHAMELEON skins for the ANIMALS Store — round-1 exploration.

ONE creature, five genuinely different takes. The brief's canonical chameleon
silhouette: a curled-tail lizard with a tall head-casque and an independent
turret eye, animated over the 4 base wing poses (`parrot._WING_ANGLES`).

A chameleon has no wings. The "flap" is reinterpreted per version as the
creature's signature MOOD-SHIFT SHIMMER — the body's colour band slides across
the 4 frames so the live skin reads as colour-changing in motion — plus a
tongue that flicks out on the up-pose as the flap accent. Each version explores
a different coil tightness, casque shape, colour-banding scheme, turret size,
and tongue expression so these are five explorations, not five tweaks.

Contract mirrors game/animal_skins.py so the winner lifts straight in:
  * `build_<name>(wing_angle_deg) -> pygame.Surface` draws one flat frame on a
    64×84 SRCALPHA canvas; body mass centred at (32,44), head near (44,34).
  * `get_<name> = _make_prebuilt_skin(build_<name>)` cached getter.
  * `BUILDERS` registry at the bottom.

North star: "a skin lives or dies at 40px in motion." Every version leans on
the spiral-coiled tail + one swivelled turret eye as the 40px tell.
"""
import math
import pygame

from game import parrot
from game.parrot import (
    SPRITE_W, SPRITE_H, _WING_ANGLES, _add_outline, _aaellipse,
)


# ── tall-canvas constants (headroom is for the casque, not a crest) ───────────
COMPOSITE_W = SPRITE_W          # 64
COMPOSITE_H = 84
DY          = 12

BCX, BCY = 32, 32 + DY          # body centre  → (32, 44)
HCX, HCY = 44, 22 + DY          # head centre  → (44, 34)
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


def _eye(surf, cx, cy, r, *, iris=(20, 22, 30), white=(250, 250, 245),
         glint=True):
    pygame.draw.circle(surf, white, (cx, cy), r)
    pygame.draw.circle(surf, iris, (cx + max(1, r // 4), cy), max(2, r - 2))
    if glint:
        pygame.draw.circle(surf, (255, 255, 255), (cx - r // 3, cy - r // 3),
                           max(1, r // 3))


def _flap(angle_deg):
    """0..1 'up' factor. _WING_ANGLES runs 50→-40 (down→up)."""
    return (angle_deg + 40) / 90.0


def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _turret_eye(surf, cx, cy, r, body_d, body, *, look=0.0, iris=(28, 40, 26)):
    """The signature swivel-turret: a cone-shaped scaly mound capped by a small
    pivoting pupil aperture. `look` (-1..1) swings the pupil so the eye reads as
    independently aimed — the comic 40px tell."""
    # Cone mound rising off the head, ringed with scale bands.
    pygame.draw.circle(surf, body_d, (cx, cy), r)
    pygame.draw.circle(surf, body, (cx, cy), r - 1)
    for rr in (r - 1, r - 3):
        if rr > 0:
            pygame.draw.circle(surf, body_d, (cx, cy), rr, 1)
    # Small dark aperture with a swivelled pupil + bright glint.
    px = cx + int(look * (r - 3))
    py = cy
    pygame.draw.circle(surf, (250, 248, 240), (cx, cy), max(2, r - 4))
    pygame.draw.circle(surf, iris, (px, py), max(1, r - 5))
    pygame.draw.circle(surf, (255, 255, 255), (px - 1, py - 1), 1)


def _coil_tail(surf, cx, cy, turns, r0, dr, col, col_h, width=3, start=0.0):
    """A spiral-coiled prehensile tail drawn as a shrinking arc spiral from an
    outer anchor inward. The tight inward curl is the unmistakable silhouette."""
    pts = []
    steps = int(turns * 14)
    for i in range(steps + 1):
        t = i / steps
        ang = start + t * turns * 2 * math.pi
        rad = r0 - dr * t
        pts.append((cx + math.cos(ang) * rad, cy + math.sin(ang) * rad))
    if len(pts) >= 2:
        pygame.draw.lines(surf, col, False, pts, width)
        # A thin highlight on the outer half sells the rounded scaly tube.
        pygame.draw.lines(surf, col_h, False, pts[:max(2, len(pts) // 2)],
                          max(1, width - 2))


# ═════════════════════════════════════════════════════════════════════════════
# V1 · RAINBOW PRISM — the showpiece colour-changer. A full ROYGBIV band sweeps
#     across the body and slides one stop per frame (the mood-shift shimmer made
#     literal). Tall scalloped casque, big turret, classic tight coil.
# ═════════════════════════════════════════════════════════════════════════════
_V1_RAINBOW = [(255, 92, 120), (255, 168, 60), (255, 214, 63),
               (91, 200, 91), (63, 160, 224), (150, 110, 230)]
_V1_BODY_D  = (40, 70, 48)
_V1_CASQUE  = (255, 210, 63)
_V1_CASQUE_D = (214, 150, 30)


def build_chameleon_v1(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)
    shift = int(round(f * 3))                 # band slides per frame

    # Tight spiral tail curling under the body (the 40px silhouette tell).
    _coil_tail(surf, 13, BCY + 11, 1.6, 10, 8, _V1_BODY_D, (150, 220, 160),
               width=4, start=math.radians(20))

    # Body: a rounded lizard mass, drawn as vertical rainbow bands that slide.
    bx0, bx1 = BCX - 17, BCX + 14
    nb = len(_V1_RAINBOW)
    bw = (bx1 - bx0) / nb
    body_rect = pygame.Rect(bx0, BCY - 14, bx1 - bx0, 28)
    band_surf = pygame.Surface((bx1 - bx0, 28), pygame.SRCALPHA)
    for i in range(nb):
        col = _V1_RAINBOW[(i + shift) % nb]
        pygame.draw.rect(band_surf, col, (int(i * bw), 0, int(bw) + 1, 28))
    mask = pygame.Surface((bx1 - bx0, 28), pygame.SRCALPHA)
    pygame.draw.ellipse(mask, (255, 255, 255, 255), mask.get_rect())
    band_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(band_surf, body_rect.topleft)
    pygame.draw.ellipse(surf, _V1_BODY_D, body_rect, 1)
    # Belly crest of tiny saw-teeth (chameleon tell) along the underside.
    for tx in range(bx0 + 4, bx1 - 2, 4):
        pygame.draw.polygon(surf, _V1_BODY_D,
                            [(tx, BCY + 11), (tx + 2, BCY + 11), (tx + 1, BCY + 15)])

    # Stubby gripping foot (zygodactyl pincer) under the body.
    for fx in (28, 36):
        pygame.draw.line(surf, _V1_BODY_D, (fx, BCY + 11), (fx, BCY + 16), 3)
        pygame.draw.circle(surf, _V1_RAINBOW[(2 + shift) % nb], (fx, BCY + 16), 2)

    # Head sweeping up into a tall scalloped casque.
    _aaellipse(surf, _V1_BODY_D, (HCX, HCY + 1), 11, 10)
    band = _V1_RAINBOW[(shift) % nb]
    _aaellipse(surf, band, (HCX - 1, HCY), 10, 9)
    # Casque: tall fin rising off the back of the skull, scalloped edge.
    casque = [(HCX - 6, HCY - 6), (HCX - 9, CROWN_Y - 1),
              (HCX - 2, CROWN_Y - 4), (HCX + 4, CROWN_Y),
              (HCX + 7, HCY - 4)]
    pygame.draw.polygon(surf, _V1_CASQUE, casque)
    pygame.draw.polygon(surf, _V1_CASQUE_D, casque, 1)
    for sx in (HCX - 6, HCX - 2, HCX + 2):
        pygame.draw.line(surf, _V1_CASQUE_D, (sx, CROWN_Y + 2), (sx + 1, HCY - 4), 1)

    # Big swivel turret eye — looks UP on the up-pose.
    _turret_eye(surf, HCX + 2, HCY - 2, 6, _V1_BODY_D, _V1_CASQUE,
                look=(f - 0.5) * 1.6)

    # Snout + tongue flick out on the up-pose (flap accent).
    pygame.draw.polygon(surf, band,
                        [(HCX + 7, HCY + 1), (HCX + 13, HCY + 2),
                         (HCX + 12, HCY + 6), (HCX + 7, HCY + 6)])
    pygame.draw.line(surf, _V1_BODY_D, (HCX + 8, HCY + 5), (HCX + 12, HCY + 5), 1)
    if f > 0.55:
        tl = int((f - 0.55) * 36)
        pygame.draw.line(surf, (255, 120, 150), (HCX + 12, HCY + 4),
                         (HCX + 12 + tl, HCY + 2), 2)
        pygame.draw.circle(surf, (255, 80, 120), (HCX + 12 + tl, HCY + 2), 3)
    return surf


get_chameleon_v1 = _make_prebuilt_skin(build_chameleon_v1)


# ═════════════════════════════════════════════════════════════════════════════
# V2 · NEON FLUSH — two-tone gradient mood-shifter on the brief palette: a green
#     base that FLUSHES through a hot-pink band into a cool blue as it tilts. The
#     gradient direction rotates per frame. Sleek low casque, slim coil, cone-eye.
# ═════════════════════════════════════════════════════════════════════════════
_V2_BASE  = (91, 200, 91)
_V2_FLUSH = (255, 92, 168)
_V2_COOL  = (63, 160, 224)
_V2_D     = (34, 90, 60)
_V2_CREST = (255, 210, 63)


def build_chameleon_v2(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)

    # Slim, looser coil sweeping low behind the body.
    _coil_tail(surf, 12, BCY + 12, 1.3, 11, 9, _V2_D, (140, 230, 160),
               width=4, start=math.radians(-10))

    # Body as a left→right gradient that shifts hue with the flap: base→flush
    # on the down-stroke, flush→cool on the up-stroke.
    bx0, bx1 = BCX - 16, BCX + 14
    w = bx1 - bx0
    if f < 0.5:
        ca, cb = _V2_BASE, _V2_FLUSH
        tt = f / 0.5
    else:
        ca, cb = _V2_FLUSH, _V2_COOL
        tt = (f - 0.5) / 0.5
    grad = pygame.Surface((w, 28), pygame.SRCALPHA)
    for x in range(w):
        t = (x / w) * 0.6 + tt * 0.4         # rotating gradient phase
        grad.fill((*_lerp(ca, cb, min(1.0, t)), 255), (x, 0, 1, 28))
    mask = pygame.Surface((w, 28), pygame.SRCALPHA)
    pygame.draw.ellipse(mask, (255, 255, 255, 255), mask.get_rect())
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(grad, (bx0, BCY - 14))
    pygame.draw.ellipse(surf, _V2_D, (bx0, BCY - 14, w, 28), 1)
    # Lateral mid-line stripe (real chameleons have one).
    pygame.draw.line(surf, (255, 255, 255), (bx0 + 4, BCY), (bx1 - 4, BCY - 1), 1)

    for fx in (28, 36):
        pygame.draw.line(surf, _V2_D, (fx, BCY + 11), (fx, BCY + 16), 3)
        pygame.draw.circle(surf, _V2_FLUSH, (fx, BCY + 16), 2)

    # Head with a LOW sleek casque (sail along the skull, not a tall fin).
    _aaellipse(surf, _V2_D, (HCX, HCY + 1), 11, 10)
    head_col = _lerp(_V2_BASE, _V2_FLUSH, f)
    _aaellipse(surf, head_col, (HCX - 1, HCY), 10, 9)
    casque = [(HCX - 7, HCY - 5), (HCX - 4, HCY - 9),
              (HCX + 6, HCY - 8), (HCX + 8, HCY - 3)]
    pygame.draw.polygon(surf, _V2_CREST, casque)
    pygame.draw.polygon(surf, _V2_D, casque, 1)

    # Compact cone turret, swivelling.
    _turret_eye(surf, HCX + 2, HCY - 2, 5, _V2_D, head_col,
                look=(f - 0.5) * 1.6, iris=(20, 30, 50))

    # Snout + tongue.
    pygame.draw.polygon(surf, head_col,
                        [(HCX + 8, HCY + 1), (HCX + 13, HCY + 2),
                         (HCX + 12, HCY + 6), (HCX + 8, HCY + 6)])
    if f > 0.55:
        tl = int((f - 0.55) * 38)
        pygame.draw.line(surf, _V2_FLUSH, (HCX + 12, HCY + 4),
                         (HCX + 12 + tl, HCY + 1), 2)
        pygame.draw.circle(surf, (255, 60, 140), (HCX + 12 + tl, HCY + 1), 3)
    return surf


get_chameleon_v2 = _make_prebuilt_skin(build_chameleon_v2)


# ═════════════════════════════════════════════════════════════════════════════
# V3 · SPOTTED PANTHER — a panther-chameleon look: bold blocky colour PATCHES
#     (not a smooth gradient) over a teal base, with white vertical bars. The
#     patch colours cycle per frame (mood spots). Big triangular casque, fat
#     tight coil, huge characterful turret. The most "reptile-textured" take.
# ═════════════════════════════════════════════════════════════════════════════
_V3_BASE   = (40, 150, 150)
_V3_BASE_D = (24, 100, 104)
_V3_SPOTS  = [(255, 92, 120), (255, 200, 60), (150, 110, 230), (255, 130, 60)]
_V3_BAR    = (230, 245, 245)
_V3_CASQUE = (255, 200, 60)


def build_chameleon_v3(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)
    shift = int(round(f * 3))

    # Fat, very tight coil (3 close turns) — the chunkiest spiral of the set.
    _coil_tail(surf, 13, BCY + 11, 2.2, 9, 7, _V3_BASE_D, (120, 220, 220),
               width=4, start=math.radians(0))

    # Teal body.
    _aaellipse(surf, _V3_BASE_D, (BCX, BCY + 1), 17, 14)
    _aaellipse(surf, _V3_BASE, (BCX - 1, BCY), 16, 13)
    # White vertical bars (panther-chameleon banding).
    for bx in (BCX - 9, BCX - 2, BCX + 5):
        pygame.draw.line(surf, _V3_BAR, (bx, BCY - 11), (bx, BCY + 11), 2)
    # Bold mood-spots that cycle colour per frame.
    spots = [(-10, -4), (-3, 4), (4, -5), (9, 3), (1, -2)]
    for i, (sx, sy) in enumerate(spots):
        col = _V3_SPOTS[(i + shift) % len(_V3_SPOTS)]
        pygame.draw.circle(surf, col, (BCX + sx, BCY + sy), 3)
        pygame.draw.circle(surf, _V3_BASE_D, (BCX + sx, BCY + sy), 3, 1)
    pygame.draw.ellipse(surf, _V3_BASE_D, (BCX - 17, BCY - 14, 33, 27), 1)

    for fx in (28, 36):
        pygame.draw.line(surf, _V3_BASE_D, (fx, BCY + 12), (fx, BCY + 16), 3)
        pygame.draw.circle(surf, _V3_SPOTS[shift % 4], (fx, BCY + 16), 2)

    # Head + tall TRIANGULAR casque (a sharp horn-like fin).
    _aaellipse(surf, _V3_BASE_D, (HCX, HCY + 1), 11, 10)
    _aaellipse(surf, _V3_BASE, (HCX - 1, HCY), 10, 9)
    casque = [(HCX - 5, HCY - 5), (HCX - 8, CROWN_Y),
              (HCX + 2, CROWN_Y - 5), (HCX + 7, HCY - 4)]
    pygame.draw.polygon(surf, _V3_CASQUE, casque)
    pygame.draw.polygon(surf, _V3_BASE_D, casque, 1)
    pygame.draw.line(surf, _V3_BASE_D, (HCX - 3, HCY - 5),
                     (HCX - 5, CROWN_Y + 1), 1)

    # HUGE characterful turret eye.
    _turret_eye(surf, HCX + 1, HCY - 2, 7, _V3_BASE_D, _V3_BASE,
                look=(f - 0.5) * 1.7, iris=(28, 36, 30))

    pygame.draw.polygon(surf, _V3_BASE,
                        [(HCX + 7, HCY + 1), (HCX + 13, HCY + 2),
                         (HCX + 12, HCY + 6), (HCX + 7, HCY + 6)])
    if f > 0.55:
        tl = int((f - 0.55) * 34)
        pygame.draw.line(surf, (255, 92, 120), (HCX + 12, HCY + 4),
                         (HCX + 12 + tl, HCY + 2), 2)
        pygame.draw.circle(surf, (255, 60, 100), (HCX + 12 + tl, HCY + 2), 3)
    return surf


get_chameleon_v3 = _make_prebuilt_skin(build_chameleon_v3)


# ═════════════════════════════════════════════════════════════════════════════
# V4 · VEILED CASQUE — the Yemen/veiled chameleon: a dramatically TALL helmet
#     casque is the hero, with diagonal candy-stripe banding (green/yellow) that
#     scrolls per frame. Modest turret. A regal, top-heavy silhouette where the
#     casque — not the coil — is the dominant break-the-sky tell.
# ═════════════════════════════════════════════════════════════════════════════
_V4_GREEN  = (80, 190, 96)
_V4_GREEN_D = (40, 120, 64)
_V4_GOLD   = (255, 210, 63)
_V4_BAND   = (255, 150, 60)


def build_chameleon_v4(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)
    scroll = f * 6                            # diagonal stripes scroll per frame

    # Moderate coil low and to the rear.
    _coil_tail(surf, 13, BCY + 12, 1.5, 10, 8, _V4_GREEN_D, (160, 240, 170),
               width=4, start=math.radians(10))

    # Body with diagonal candy stripes that scroll (the colour-shift read).
    bx0, bx1 = BCX - 16, BCX + 14
    w = bx1 - bx0
    body = pygame.Surface((w, 28), pygame.SRCALPHA)
    for x in range(w):
        for y in range(28):
            phase = (x + y + scroll) % 12
            body.set_at((x, y), (_V4_GOLD if phase < 6 else _V4_GREEN))
    mask = pygame.Surface((w, 28), pygame.SRCALPHA)
    pygame.draw.ellipse(mask, (255, 255, 255, 255), mask.get_rect())
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(body, (bx0, BCY - 14))
    pygame.draw.ellipse(surf, _V4_GREEN_D, (bx0, BCY - 14, w, 28), 1)

    for fx in (28, 36):
        pygame.draw.line(surf, _V4_GREEN_D, (fx, BCY + 11), (fx, BCY + 16), 3)
        pygame.draw.circle(surf, _V4_BAND, (fx, BCY + 16), 2)

    # Head.
    _aaellipse(surf, _V4_GREEN_D, (HCX, HCY + 2), 10, 9)
    _aaellipse(surf, _V4_GREEN, (HCX - 1, HCY + 1), 9, 8)

    # ── HERO: the dramatically tall VEILED casque helmet ──
    casque = [(HCX - 6, HCY - 3), (HCX - 7, CROWN_Y - 4),
              (HCX, CROWN_Y - 8), (HCX + 8, CROWN_Y - 2),
              (HCX + 9, HCY - 2)]
    pygame.draw.polygon(surf, _V4_GOLD, casque)
    pygame.draw.polygon(surf, _V4_GREEN_D, casque, 1)
    # Ridge stripes climbing the helmet.
    for i in range(4):
        x0 = HCX - 5 + i * 4
        pygame.draw.line(surf, _V4_GREEN_D, (x0, HCY - 3),
                         (x0 - 1, CROWN_Y - 4), 1)
    # Bright leading edge so the tall helmet survives the downscale.
    pygame.draw.line(surf, (255, 244, 180), (HCX + 8, CROWN_Y - 2),
                     (HCX + 9, HCY - 2), 2)

    _turret_eye(surf, HCX + 2, HCY - 1, 5, _V4_GREEN_D, _V4_GREEN,
                look=(f - 0.5) * 1.5)

    pygame.draw.polygon(surf, _V4_GREEN,
                        [(HCX + 8, HCY + 2), (HCX + 13, HCY + 3),
                         (HCX + 12, HCY + 6), (HCX + 8, HCY + 6)])
    if f > 0.55:
        tl = int((f - 0.55) * 34)
        pygame.draw.line(surf, _V4_BAND, (HCX + 12, HCY + 4),
                         (HCX + 12 + tl, HCY + 3), 2)
        pygame.draw.circle(surf, (255, 100, 60), (HCX + 12 + tl, HCY + 3), 3)
    return surf


get_chameleon_v4 = _make_prebuilt_skin(build_chameleon_v4)


# ═════════════════════════════════════════════════════════════════════════════
# V5 · CHIBI BUBBLE — a rounded, baby-cute take: a near-circular body, an
#     OVERSIZED single turret eye dominating the face (Pascal-from-Tangled
#     energy), a tiny stub casque, and a loose single-loop tail. Body does a
#     soft two-colour pulse (mint↔coral) per frame. Maximal silhouette economy.
# ═════════════════════════════════════════════════════════════════════════════
_V5_MINT   = (108, 216, 150)
_V5_CORAL  = (255, 130, 140)
_V5_MINT_D = (46, 150, 100)
_V5_CHEEK  = (255, 170, 175)
_V5_STUB   = (255, 210, 63)


def build_chameleon_v5(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)
    body_col = _lerp(_V5_MINT, _V5_CORAL, f)        # soft mood pulse
    body_d = _lerp(_V5_MINT_D, (200, 80, 96), f)

    # Loose single-loop tail with a clear open curl (reads at 40px as a comma).
    _coil_tail(surf, 13, BCY + 11, 1.0, 12, 8, body_d, (190, 255, 210),
               width=5, start=math.radians(-20))

    # Near-circular chibi body.
    _aaellipse(surf, body_d, (BCX, BCY + 1), 16, 15)
    _aaellipse(surf, body_col, (BCX - 1, BCY), 15, 14)
    _aaellipse(surf, _lerp(body_col, (255, 255, 255), 0.3),
               (BCX - 4, BCY - 4), 7, 5)
    # A couple of mood-dots that pulse opposite the body for contrast.
    for sx, sy in ((-7, 3), (2, 6), (7, -2)):
        pygame.draw.circle(surf, _lerp(_V5_CORAL, _V5_MINT, f),
                           (BCX + sx, BCY + sy), 2)

    for fx in (28, 36):
        pygame.draw.line(surf, body_d, (fx, BCY + 12), (fx, BCY + 16), 3)
        pygame.draw.circle(surf, _V5_CORAL, (fx, BCY + 16), 2)

    # Tiny head merging into the body with a stub casque.
    _aaellipse(surf, body_d, (HCX, HCY + 2), 10, 9)
    _aaellipse(surf, body_col, (HCX - 1, HCY + 1), 9, 8)
    stub = [(HCX - 3, HCY - 4), (HCX, CROWN_Y + 4),
            (HCX + 5, CROWN_Y + 5), (HCX + 5, HCY - 3)]
    pygame.draw.polygon(surf, _V5_STUB, stub)
    pygame.draw.polygon(surf, body_d, stub, 1)
    # Rosy cheek.
    pygame.draw.circle(surf, _V5_CHEEK, (HCX - 3, HCY + 4), 3)

    # ── HERO: ONE oversized turret eye dominating the face ──
    _turret_eye(surf, HCX + 2, HCY - 1, 8, body_d, body_col,
                look=(f - 0.5) * 1.8, iris=(30, 36, 32))

    # Wide smiley snout.
    pygame.draw.polygon(surf, body_col,
                        [(HCX + 7, HCY + 2), (HCX + 13, HCY + 3),
                         (HCX + 12, HCY + 7), (HCX + 7, HCY + 7)])
    pygame.draw.arc(surf, body_d, (HCX + 6, HCY + 2, 8, 7),
                    math.radians(200), math.radians(340), 1)
    if f > 0.55:
        tl = int((f - 0.55) * 40)
        pygame.draw.line(surf, _V5_CORAL, (HCX + 12, HCY + 5),
                         (HCX + 12 + tl, HCY + 3), 2)
        pygame.draw.circle(surf, (255, 90, 110), (HCX + 12 + tl, HCY + 3), 3)
    return surf


get_chameleon_v5 = _make_prebuilt_skin(build_chameleon_v5)


# ─────────────────────────────────────────────────────────────────────────────
# Candidate registry: label → getter.
# ─────────────────────────────────────────────────────────────────────────────
BUILDERS = {
    "v1 · Rainbow Prism":  get_chameleon_v1,
    "v2 · Neon Flush":     get_chameleon_v2,
    "v3 · Spotted Panther": get_chameleon_v3,
    "v4 · Veiled Casque":  get_chameleon_v4,
    "v5 · Chibi Bubble":   get_chameleon_v5,
}
