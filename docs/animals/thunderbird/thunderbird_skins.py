"""Candidate THUNDERBIRD skins — round-1 exploration (legendary spectacle).

Five genuinely distinct takes on ONE creature: a broad-winged storm raptor
wreathed in storm-cloud feathers, with crackling lightning baked into the
sprite. There is NO live particle system feeding the skin — each frame is a
self-contained sprite, so the glow halo + lightning forks are drawn ON the
sprite, and the "thunderclap" is expressed by varying the lightning across
the 4 wing poses (forks crackle biggest on the down-stroke).

Contract mirrors game/animal_skins.py so the winner lifts straight in:

  * `build_thunderbird_vN(wing_angle_deg) -> pygame.Surface`  one flat frame
    on a 64×84 SRCALPHA canvas; body centred at (32,44), head near (44,34).
  * a cached `(frame_idx, tilt_deg) -> Surface` getter from a local
    `_make_prebuilt_skin(build_fn)`.
  * `BUILDERS = {"skin_thunderbird_v1": get_v1, ...}` registry at the bottom.

North star: "a skin lives or dies at 40px in motion." Each variant leans on
one bold silhouette + one high-contrast signature feature (lightning / glowing
eyes) that survives the downscale and reads against bright-day AND night skies.
The legendary constraint forces restraint: the glow must never bury the bird.
"""
import math
import pygame

from game import parrot
from game.parrot import (
    SPRITE_W, SPRITE_H, _WING_ANGLES, _add_outline, _aaellipse,
)


# ── tall-canvas constants (crest plumes + lightning headroom) ────────────────
COMPOSITE_W = SPRITE_W          # 64
COMPOSITE_H = 84
DY          = 12

BCX, BCY = 32, 32 + DY          # body centre → (32, 44)
HCX, HCY = 44, 22 + DY          # head centre → (44, 34)
CROWN_Y  = 12 + DY              # top of head → 24


def _make_prebuilt_skin(build_fn):
    """Cached `(frame_idx, tilt_deg) -> Surface` getter for build_fn(angle).
    Lazy 4-frame build + per-(frame, 3°) rotation cache, each frame outlined
    with the house silhouette outline."""
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


def _flap(angle_deg):
    """0..1 'wing is up' factor. _WING_ANGLES runs 50→-40 (down→up)."""
    return (angle_deg + 40) / 90.0


def _strike(angle_deg):
    """0..1 'down-stroke' factor — peaks when wings are DOWN (angle 50). The
    thunderclap fires on the down-stroke, so lightning scales with this."""
    return 1.0 - _flap(angle_deg)


def _rot_blit(surf, wing, anchor):
    surf.blit(wing, wing.get_rect(center=anchor).topleft)


# ── shared palette (brief) ───────────────────────────────────────────────────
PLUME    = (58, 74, 107)        # #3A4A6B plumage
PLUME_D  = (26, 34, 56)         # #1A2238 storm shadow
PLUME_H  = (104, 124, 168)      # lifted plume highlight
BOLT     = (255, 225, 77)       # #FFE14D lightning
RIM      = (127, 208, 255)      # #7FD0FF electric rim
FLASH    = (255, 255, 255)      # flash core
# Storm-purple alternate for v3.
PURP     = (84, 70, 130)
PURP_D   = (40, 30, 66)
PURP_H   = (140, 120, 196)
PURP_RIM = (190, 150, 255)


def _glow_halo(surf, center, r, color, *, layers=5, peak=70):
    """A soft radial aura baked into the sprite. Kept restrained (low peak
    alpha, few layers) so the bird silhouette never drowns in glow at 40px."""
    cx, cy = center
    g = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
    gc = (r + 2, r + 2)
    for i in range(layers, 0, -1):
        rr = int(r * i / layers)
        a = int(peak * (1 - (i - 1) / layers))
        pygame.draw.circle(g, (*color, a), gc, rr)
    surf.blit(g, (cx - r - 2, cy - r - 2), special_flags=pygame.BLEND_RGBA_ADD)


def _bolt(surf, pts, *, core=FLASH, glow=BOLT, halo=RIM, w=2):
    """A forked lightning stroke: a wide soft halo, a colored mid, a bright
    core — three passes so the fork reads as 'lit' not just a yellow line."""
    if len(pts) < 2:
        return
    pygame.draw.lines(surf, (*halo, 90), False, pts, w + 4)
    pygame.draw.lines(surf, glow, False, pts, w + 1)
    pygame.draw.lines(surf, core, False, pts, max(1, w - 1))


# ═════════════════════════════════════════════════════════════════════════════
# v1 · CLASSIC STORM-RAPTOR (storm-blue) — broad eagle silhouette, soft
#      cloud-feather plumage, two back-swept curved head plumes (the cultural
#      tell that separates a thunderbird from an eagle), forked lightning
#      crackling off BOTH wingtips, restrained body aura. The "default" reading.
# ═════════════════════════════════════════════════════════════════════════════
def _tb_wing_cloud(angle_deg, sgn):
    """Broad raptor wing with a billowy cloud-feather trailing edge."""
    w = pygame.Surface((52, 46), pygame.SRCALPHA)
    base = [(24, 24), (46, 12), (50, 22), (44, 28), (50, 34),
            (38, 34), (40, 40), (26, 36), (14, 32)]
    pygame.draw.polygon(w, PLUME_D, base)
    pygame.draw.polygon(w, PLUME, [(24, 24), (44, 14), (46, 24), (28, 32),
                                   (16, 30)])
    # Cloud-puff highlights along the leading edge.
    for px, py in ((40, 16), (44, 21), (34, 20)):
        pygame.draw.circle(w, PLUME_H, (px, py), 3)
    pygame.draw.line(w, PLUME_H, (24, 25), (43, 15), 1)
    out = pygame.transform.rotate(w, angle_deg)
    if sgn < 0:
        out = pygame.transform.flip(out, True, False)
    return out


def build_thunderbird_v1(wing_angle_deg):
    surf = _new()
    s = _strike(wing_angle_deg)          # 1 = down-stroke (thunderclap)
    f = _flap(wing_angle_deg)
    spread = (f - 0.5) * 22

    # Restrained body aura — pulses brighter on the down-stroke.
    _glow_halo(surf, (BCX, BCY), 22, RIM, peak=int(36 + 30 * s))

    # Far wing behind.
    _rot_blit(surf, _tb_wing_cloud(20 + spread, +1), (BCX + 16, BCY - 4))

    # Fanned storm-cloud tail.
    pygame.draw.polygon(surf, PLUME_D,
                        [(13, BCY - 4), (2, BCY + 6), (16, BCY + 12)])
    pygame.draw.polygon(surf, PLUME,
                        [(14, BCY - 2), (5, BCY + 5), (16, BCY + 9)])

    # Broad body.
    _aaellipse(surf, PLUME_D, (BCX + 1, BCY + 1), 18, 16)
    _aaellipse(surf, PLUME, (BCX, BCY), 17, 15)
    _aaellipse(surf, PLUME_H, (BCX - 3, BCY - 3), 8, 5)
    # Electric rim-light arc under the belly so the body reads as charged.
    pygame.draw.arc(surf, RIM, (BCX - 16, BCY - 12, 32, 30),
                    math.radians(200), math.radians(340), 2)

    # Head + two back-swept curved plumes (thunderbird crown).
    _aaellipse(surf, PLUME_D, (HCX, HCY + 1), 11, 11)
    _aaellipse(surf, PLUME, (HCX - 1, HCY), 10, 10)
    for sgn, hx in ((-1, HCX - 4), (1, HCX + 3)):
        pygame.draw.polygon(surf, PLUME_D,
                            [(hx, CROWN_Y + 6), (hx - sgn * 6, CROWN_Y - 8),
                             (hx + sgn * 2, CROWN_Y - 6)])
        pygame.draw.polygon(surf, PLUME_H,
                            [(hx + 1, CROWN_Y + 5), (hx - sgn * 5, CROWN_Y - 7),
                             (hx, CROWN_Y - 4)])
    # Glowing storm-blue eye.
    pygame.draw.circle(surf, RIM, (HCX + 1, HCY - 1), 5)
    pygame.draw.circle(surf, FLASH, (HCX + 1, HCY - 1), 3)
    pygame.draw.circle(surf, (30, 60, 110), (HCX + 2, HCY - 1), 1)
    # Hooked beak.
    pygame.draw.polygon(surf, BOLT,
                        [(HCX + 4, HCY - 1), (HCX + 14, HCY + 1),
                         (HCX + 12, HCY + 5), (HCX + 4, HCY + 4)])
    pygame.draw.polygon(surf, (200, 150, 30),
                        [(HCX + 12, HCY + 2), (HCX + 14, HCY + 1),
                         (HCX + 11, HCY + 7)])

    # Near wing (hero).
    near = _tb_wing_cloud(-12 - spread, -1)
    _rot_blit(surf, near, (BCX - 12, BCY + 2))

    # HERO: forked lightning off both wingtips, scaled by the down-stroke.
    if s > 0.05:
        n = 2 + int(s * 4)
        # Left tip fork.
        _bolt(surf, [(15, BCY + 6), (10, BCY + 12 + int(s * 4)),
                     (14, BCY + 13), (8, BCY + 20 + int(s * 6))], w=2)
        # Right tip fork.
        _bolt(surf, [(50, BCY - 2), (55 - int(s * 2), BCY + 6),
                     (51, BCY + 7), (57, BCY + 14 + int(s * 4))], w=2)

    # Talons.
    for fx in (28, 37):
        pygame.draw.line(surf, BOLT, (fx, BCY + 14), (fx, BCY + 18), 2)
    return surf


get_v1 = _make_prebuilt_skin(build_thunderbird_v1)


# ═════════════════════════════════════════════════════════════════════════════
# v2 · SHARP-FEATHER THUNDERHEAD (storm-blue, EYES-FIRST) — angular razor-cut
#      feathers, a single bold zig-zag brow crest, almost no wingtip lightning.
#      The whole spectacle is concentrated in two FIERCE glowing storm-blue
#      eyes + a brow-bolt. Sleekest, most predatory silhouette of the five.
# ═════════════════════════════════════════════════════════════════════════════
def _tb_wing_sharp(angle_deg, sgn):
    """Angular wing with saw-tooth razor primaries — no soft cloud puffs."""
    w = pygame.Surface((54, 44), pygame.SRCALPHA)
    base = [(24, 22), (48, 10), (52, 18), (40, 22), (50, 26),
            (38, 28), (46, 34), (28, 32), (14, 28)]
    pygame.draw.polygon(w, PLUME_D, base)
    pygame.draw.polygon(w, PLUME, [(24, 22), (46, 12), (44, 22), (28, 28),
                                   (16, 26)])
    # Sharp primary tips.
    for tx, ty in ((46, 12), (50, 17), (47, 24)):
        pygame.draw.polygon(w, PLUME_D,
                            [(tx - 4, ty + 1), (tx + 3, ty - 2), (tx - 1, ty + 4)])
    pygame.draw.line(w, RIM, (24, 23), (45, 13), 1)
    out = pygame.transform.rotate(w, angle_deg)
    if sgn < 0:
        out = pygame.transform.flip(out, True, False)
    return out


def build_thunderbird_v2(wing_angle_deg):
    surf = _new()
    s = _strike(wing_angle_deg)
    f = _flap(wing_angle_deg)
    spread = (f - 0.5) * 24

    # Tight aura focused on the HEAD (the eyes own the spectacle here).
    _glow_halo(surf, (HCX, HCY - 1), 14, RIM, peak=int(48 + 36 * s))

    _rot_blit(surf, _tb_wing_sharp(22 + spread, +1), (BCX + 16, BCY - 4))

    # Forked storm tail (jagged).
    pygame.draw.polygon(surf, PLUME_D,
                        [(13, BCY - 6), (1, BCY - 2), (10, BCY + 2),
                         (2, BCY + 8), (15, BCY + 8)])
    pygame.draw.polygon(surf, PLUME,
                        [(14, BCY - 3), (6, BCY), (15, BCY + 5)])

    # Sleek body.
    _aaellipse(surf, PLUME_D, (BCX + 1, BCY + 1), 16, 15)
    _aaellipse(surf, PLUME, (BCX, BCY), 15, 14)
    _aaellipse(surf, PLUME_H, (BCX - 3, BCY - 3), 7, 4)
    # Chevron feather flecks.
    for fx, fy in ((28, 46), (33, 48), (30, 52)):
        pygame.draw.line(surf, PLUME_D, (fx - 2, fy), (fx, fy + 2), 1)
        pygame.draw.line(surf, PLUME_D, (fx, fy + 2), (fx + 2, fy), 1)

    # Head.
    _aaellipse(surf, PLUME_D, (HCX, HCY + 1), 11, 10)
    _aaellipse(surf, PLUME, (HCX - 1, HCY), 10, 9)
    # Single bold zig-zag BROW-BOLT crest (the secondary signal).
    _bolt(surf, [(HCX - 8, HCY - 5), (HCX - 2, CROWN_Y),
                 (HCX + 3, HCY - 8), (HCX + 9, CROWN_Y + 1)], w=2)

    # HERO: two FIERCE glowing eyes (over-sized, white-core, blue halo).
    for dx in (-2, 7):
        pygame.draw.circle(surf, (20, 40, 80), (HCX + dx, HCY), 6)
        pygame.draw.circle(surf, RIM, (HCX + dx, HCY), 5)
        pygame.draw.circle(surf, FLASH, (HCX + dx, HCY - 1), 3)
        pygame.draw.circle(surf, (60, 110, 190), (HCX + dx + 1, HCY), 1)
    # Angry angled brow ridges over the eyes.
    pygame.draw.line(surf, PLUME_D, (HCX - 7, HCY - 5), (HCX - 1, HCY - 3), 2)
    pygame.draw.line(surf, PLUME_D, (HCX + 11, HCY - 5), (HCX + 4, HCY - 3), 2)
    # Short sharp beak.
    pygame.draw.polygon(surf, BOLT,
                        [(HCX + 6, HCY + 3), (HCX + 14, HCY + 4),
                         (HCX + 6, HCY + 7)])

    _rot_blit(surf, _tb_wing_sharp(-14 - spread, -1), (BCX - 13, BCY + 1))

    # Only a faint spark off a single wingtip — eyes carry the tell.
    if s > 0.4:
        _bolt(surf, [(52, BCY), (56, BCY + 6), (53, BCY + 7)], w=1)
    return surf


get_v2 = _make_prebuilt_skin(build_thunderbird_v2)


# ═════════════════════════════════════════════════════════════════════════════
# v3 · FULL-AURA STORM GOD (storm-PURPLE) — the whole body wrapped in a heavy
#      electric aura, lightning webbing forking ACROSS the open wings, a tall
#      fan crest. Most "divine / cosmic" of the five; trades silhouette purity
#      for an enveloping charged field. Purple palette sets it apart hard.
# ═════════════════════════════════════════════════════════════════════════════
def _tb_wing_web(angle_deg, sgn, strike):
    """Wing with lightning veins webbing across the membrane; brighter when
    the down-stroke fires."""
    w = pygame.Surface((54, 48), pygame.SRCALPHA)
    base = [(24, 24), (48, 12), (52, 22), (44, 28), (50, 34),
            (36, 34), (40, 42), (26, 36), (14, 32)]
    pygame.draw.polygon(w, PURP_D, base)
    pygame.draw.polygon(w, PURP, [(24, 24), (46, 14), (47, 24), (28, 32),
                                  (16, 30)])
    pygame.draw.line(w, PURP_H, (24, 25), (45, 15), 1)
    # Lightning veins across the wing — the down-stroke lights them up.
    a = int(120 + 120 * strike)
    veins = [[(24, 24), (34, 22), (40, 28), (50, 22)],
             [(24, 26), (32, 30), (44, 28)]]
    for v in veins:
        pygame.draw.lines(w, (*PURP_RIM, a), False, v, 1)
    if strike > 0.4:
        pygame.draw.lines(w, (*BOLT, a), False,
                          [(24, 24), (36, 24), (44, 30)], 1)
    out = pygame.transform.rotate(w, angle_deg)
    if sgn < 0:
        out = pygame.transform.flip(out, True, False)
    return out


def build_thunderbird_v3(wing_angle_deg):
    surf = _new()
    s = _strike(wing_angle_deg)
    f = _flap(wing_angle_deg)
    spread = (f - 0.5) * 20

    # HEAVY enveloping aura — two layers, body + a wider field, pulsing.
    _glow_halo(surf, (BCX, BCY), 30, PURP_RIM, peak=int(40 + 30 * s), layers=6)
    _glow_halo(surf, (BCX, BCY), 18, FLASH, peak=int(22 + 22 * s))

    _rot_blit(surf, _tb_wing_web(18 + spread, +1, s), (BCX + 16, BCY - 4))

    # Tail.
    pygame.draw.polygon(surf, PURP_D,
                        [(13, BCY - 4), (2, BCY + 6), (16, BCY + 12)])
    pygame.draw.polygon(surf, PURP,
                        [(14, BCY - 2), (5, BCY + 5), (16, BCY + 9)])

    # Body.
    _aaellipse(surf, PURP_D, (BCX + 1, BCY + 1), 18, 16)
    _aaellipse(surf, PURP, (BCX, BCY), 17, 15)
    _aaellipse(surf, PURP_H, (BCX - 3, BCY - 3), 8, 5)
    # Inner charged core glow on the chest.
    pygame.draw.circle(surf, (*RIM, 160), (BCX - 1, BCY + 2), 6)
    pygame.draw.circle(surf, (*FLASH, 200), (BCX - 1, BCY + 2), 3)

    # Head with a tall FAN crest of upright plumes.
    _aaellipse(surf, PURP_D, (HCX, HCY + 1), 11, 11)
    _aaellipse(surf, PURP, (HCX - 1, HCY), 10, 10)
    for i, dx in enumerate((-7, -3, 1, 5)):
        h = 10 + (2 if i in (1, 2) else 0)
        pygame.draw.polygon(surf, PURP_D,
                            [(HCX + dx - 2, HCY - 6), (HCX + dx, CROWN_Y - (h - 6)),
                             (HCX + dx + 2, HCY - 6)])
        pygame.draw.line(surf, PURP_RIM, (HCX + dx, HCY - 6),
                         (HCX + dx, CROWN_Y - (h - 6)), 1)
    # Glowing eye.
    pygame.draw.circle(surf, PURP_RIM, (HCX + 1, HCY - 1), 5)
    pygame.draw.circle(surf, FLASH, (HCX + 1, HCY - 1), 3)
    # Beak.
    pygame.draw.polygon(surf, BOLT,
                        [(HCX + 4, HCY), (HCX + 13, HCY + 2),
                         (HCX + 11, HCY + 5), (HCX + 4, HCY + 5)])

    near = _tb_wing_web(-16 - spread, -1, s)
    _rot_blit(surf, near, (BCX - 12, BCY + 2))

    # A big jagged fork spanning beneath the body on the heavy down-stroke.
    if s > 0.3:
        _bolt(surf, [(20, BCY + 14), (26, BCY + 18 + int(s * 3)),
                     (32, BCY + 14), (38, BCY + 19 + int(s * 4)),
                     (44, BCY + 14)], core=FLASH, glow=PURP_RIM, halo=BOLT, w=2)
    return surf


get_v3 = _make_prebuilt_skin(build_thunderbird_v3)


# ═════════════════════════════════════════════════════════════════════════════
# v4 · LIGHTNING-SNAKE THUNDERBIRD (Northwest-Coast inspired, storm-blue) —
#      formline-flavoured: a bold ovoid eye, a two-horn crown, and the cultural
#      signature of lightning SNAKES forking DOWN from beneath each wing (the
#      myth's weapon). Most distinct read: lightning hangs below, not at tips.
# ═════════════════════════════════════════════════════════════════════════════
def _tb_wing_formline(angle_deg, sgn):
    """Stylised formline wing — bold rounded leading edge, split U-feathers."""
    w = pygame.Surface((54, 44), pygame.SRCALPHA)
    base = [(24, 22), (48, 12), (52, 22), (38, 30), (40, 36),
            (26, 34), (14, 30)]
    pygame.draw.polygon(w, PLUME_D, base)
    pygame.draw.polygon(w, PLUME, [(24, 22), (46, 14), (48, 22), (30, 30),
                                   (16, 28)])
    # Formline split-U feather marks (rim outlines).
    for ux, uy in ((34, 18), (40, 20), (44, 24)):
        pygame.draw.arc(w, RIM, (ux - 4, uy - 5, 9, 11),
                        math.radians(250), math.radians(110), 2)
    pygame.draw.line(w, PLUME_H, (24, 23), (45, 15), 1)
    out = pygame.transform.rotate(w, angle_deg)
    if sgn < 0:
        out = pygame.transform.flip(out, True, False)
    return out


def build_thunderbird_v4(wing_angle_deg):
    surf = _new()
    s = _strike(wing_angle_deg)
    f = _flap(wing_angle_deg)
    spread = (f - 0.5) * 20

    _glow_halo(surf, (BCX, BCY), 22, RIM, peak=int(34 + 26 * s))

    _rot_blit(surf, _tb_wing_formline(20 + spread, +1), (BCX + 16, BCY - 4))

    # Bold blocky formline tail.
    pygame.draw.polygon(surf, PLUME_D,
                        [(13, BCY - 5), (1, BCY - 1), (3, BCY + 9),
                         (16, BCY + 11)])
    pygame.draw.polygon(surf, PLUME,
                        [(13, BCY - 2), (5, BCY + 1), (6, BCY + 7),
                         (15, BCY + 8)])
    pygame.draw.line(surf, RIM, (6, BCY + 1), (6, BCY + 7), 1)

    # Body.
    _aaellipse(surf, PLUME_D, (BCX + 1, BCY + 1), 18, 16)
    _aaellipse(surf, PLUME, (BCX, BCY), 17, 15)
    _aaellipse(surf, PLUME_H, (BCX - 3, BCY - 3), 8, 5)
    # Formline split-U chest mark.
    pygame.draw.arc(surf, RIM, (BCX - 8, BCY - 4, 16, 18),
                    math.radians(200), math.radians(340), 2)

    # Head with a bold TWO-HORN crown (curled, formline).
    _aaellipse(surf, PLUME_D, (HCX, HCY + 1), 11, 11)
    _aaellipse(surf, PLUME, (HCX - 1, HCY), 10, 10)
    for sgn, hx in ((-1, HCX - 4), (1, HCX + 3)):
        pygame.draw.polygon(surf, PLUME_D,
                            [(hx, CROWN_Y + 6), (hx - sgn * 2, CROWN_Y - 9),
                             (hx + sgn * 5, CROWN_Y - 5), (hx + sgn * 3, CROWN_Y)])
        pygame.draw.line(surf, RIM, (hx, CROWN_Y + 4),
                         (hx - sgn * 2, CROWN_Y - 8), 1)
    # HERO secondary: bold formline ovoid eye.
    pygame.draw.ellipse(surf, FLASH, (HCX - 4, HCY - 4, 11, 8))
    pygame.draw.ellipse(surf, (20, 30, 56), (HCX - 4, HCY - 4, 11, 8), 1)
    pygame.draw.circle(surf, RIM, (HCX + 1, HCY), 3)
    pygame.draw.circle(surf, (20, 30, 56), (HCX + 1, HCY), 2)
    # Beak.
    pygame.draw.polygon(surf, BOLT,
                        [(HCX + 5, HCY), (HCX + 14, HCY + 2),
                         (HCX + 12, HCY + 6), (HCX + 5, HCY + 5)])

    _rot_blit(surf, _tb_wing_formline(-14 - spread, -1), (BCX - 13, BCY + 1))

    # HERO: lightning SNAKES hanging DOWN from beneath both wings — the tell.
    if s > 0.05:
        drop = int(s * 8)
        _bolt(surf, [(18, BCY + 8), (15, BCY + 14), (19, BCY + 16),
                     (14, BCY + 22 + drop)], w=2)
        _bolt(surf, [(48, BCY + 6), (52, BCY + 12), (48, BCY + 14),
                     (53, BCY + 20 + drop)], w=2)
    return surf


get_v4 = _make_prebuilt_skin(build_thunderbird_v4)


# ═════════════════════════════════════════════════════════════════════════════
# v5 · WHITE-FLASH STRIKE (high-contrast storm-blue + flash-core) — the most
#      dramatic thunderclap beat: on the DOWN-stroke a massive white-core fork
#      fires straight down BETWEEN the wings; cloud-feathers compress on the
#      up-pose. A vertical jagged mohawk crest. Built to be unmistakable at 40px
#      via raw white-on-dark contrast, not colour.
# ═════════════════════════════════════════════════════════════════════════════
def _tb_wing_compress(angle_deg, sgn, flap):
    """Wing whose billowy cloud trailing-edge COMPRESSES (puffs shrink) on the
    up-pose, giving the wingbeat a 'gathering then clap' feel."""
    w = pygame.Surface((52, 46), pygame.SRCALPHA)
    puff = 1.0 - flap * 0.5               # smaller puffs when wings are up
    base = [(24, 24), (46, 12), (50, 22), (44, 28), (50, 34),
            (38, 34), (40, 40), (26, 36), (14, 32)]
    pygame.draw.polygon(w, PLUME_D, base)
    pygame.draw.polygon(w, PLUME, [(24, 24), (44, 14), (46, 24), (28, 32),
                                   (16, 30)])
    for px, py in ((40, 16), (44, 21), (34, 20), (38, 36)):
        pygame.draw.circle(w, PLUME_H, (px, py), max(1, int(3 * puff)))
    pygame.draw.line(w, RIM, (24, 25), (43, 15), 1)
    out = pygame.transform.rotate(w, angle_deg)
    if sgn < 0:
        out = pygame.transform.flip(out, True, False)
    return out


def build_thunderbird_v5(wing_angle_deg):
    surf = _new()
    s = _strike(wing_angle_deg)
    f = _flap(wing_angle_deg)
    spread = (f - 0.5) * 22

    # Aura flares hard ONLY on the strike, near-dark on the up-pose — the
    # high-contrast on/off pulse IS the thunderclap.
    _glow_halo(surf, (BCX, BCY + 4), 24, RIM, peak=int(20 + 50 * s))
    if s > 0.5:
        _glow_halo(surf, (BCX, BCY + 8), 16, FLASH, peak=int(40 * s))

    _rot_blit(surf, _tb_wing_compress(22 + spread, +1, f), (BCX + 16, BCY - 4))

    # Tail.
    pygame.draw.polygon(surf, PLUME_D,
                        [(13, BCY - 4), (2, BCY + 6), (16, BCY + 12)])
    pygame.draw.polygon(surf, PLUME,
                        [(14, BCY - 2), (5, BCY + 5), (16, BCY + 9)])

    # Body.
    _aaellipse(surf, PLUME_D, (BCX + 1, BCY + 1), 18, 16)
    _aaellipse(surf, PLUME, (BCX, BCY), 17, 15)
    _aaellipse(surf, PLUME_H, (BCX - 3, BCY - 3), 8, 5)

    # Head with a vertical jagged MOHAWK crest (zig-zag spine of plumes).
    _aaellipse(surf, PLUME_D, (HCX, HCY + 1), 11, 11)
    _aaellipse(surf, PLUME, (HCX - 1, HCY), 10, 10)
    mohawk = [(HCX - 6, HCY - 4), (HCX - 4, CROWN_Y),
              (HCX - 1, HCY - 6), (HCX + 1, CROWN_Y - 2),
              (HCX + 4, HCY - 5), (HCX + 5, CROWN_Y + 1)]
    pygame.draw.polygon(surf, PLUME_D, mohawk + [(HCX + 4, HCY - 3),
                                                 (HCX - 5, HCY - 3)])
    pygame.draw.lines(surf, RIM, False, mohawk, 1)
    # Glowing eye.
    pygame.draw.circle(surf, RIM, (HCX + 1, HCY - 1), 5)
    pygame.draw.circle(surf, FLASH, (HCX + 1, HCY - 1), 3)
    # Beak.
    pygame.draw.polygon(surf, BOLT,
                        [(HCX + 4, HCY - 1), (HCX + 14, HCY + 1),
                         (HCX + 12, HCY + 5), (HCX + 4, HCY + 4)])

    near = _tb_wing_compress(-14 - spread, -1, f)
    _rot_blit(surf, near, (BCX - 12, BCY + 2))

    # HERO: a massive white-core fork firing straight DOWN between the wings on
    # the down-stroke — the single boldest 40px tell of all five.
    if s > 0.25:
        ln = int(s * 14)
        _bolt(surf, [(BCX + 2, BCY + 10), (BCX - 4, BCY + 18),
                     (BCX + 3, BCY + 20), (BCX - 3, BCY + 28),
                     (BCX + 2, BCY + 30 + ln)],
              core=FLASH, glow=BOLT, halo=RIM, w=3)
        # A small branch fork for crackle.
        _bolt(surf, [(BCX + 3, BCY + 20), (BCX + 9, BCY + 24 + ln // 2)], w=1)
    return surf


get_v5 = _make_prebuilt_skin(build_thunderbird_v5)


# ─────────────────────────────────────────────────────────────────────────────
BUILDERS = {
    "skin_thunderbird_v1": get_v1,
    "skin_thunderbird_v2": get_v2,
    "skin_thunderbird_v3": get_v3,
    "skin_thunderbird_v4": get_v4,
    "skin_thunderbird_v5": get_v5,
}
