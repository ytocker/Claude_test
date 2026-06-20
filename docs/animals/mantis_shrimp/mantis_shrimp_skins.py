"""Production MANTIS SHRIMP skin (`skin_mantis_shrimp`) — round-2 build.

Round 1 explored five takes; the art-director picked **v3 DUOTONE BRUISER**
and asked for one ship-ready convergence. This module now exposes the SINGLE
primary production build so it lifts straight into game/animal_skins.py:

  * `build_mantis_shrimp(wing_angle_deg) -> pygame.Surface` on a 64×84
    SRCALPHA canvas; body mass centred at (32,44), head/eye-stalks near
    (44,34) and up into the headroom.
  * `get_mantis_shrimp = _make_prebuilt_skin(build_mantis_shrimp)` — a cached
    `(frame_idx, tilt_deg) -> Surface` getter (4 frames, per-3° rotation
    cache, each house-outlined for the day-sky contour).
  * `BUILDERS = {"skin_mantis_shrimp": get_mantis_shrimp}`.

THE FLAP IS A STRIKE: the raptorial clubs cock BACK on the down-pose
(_WING_ANGLES starts at 50) and PUNCH FORWARD on the up-pose (ends at -40).
`_strike()` maps a wing angle to a 0..1 punch. The lead club crosses PAST the
snout line on the punch and the body recoils a touch, so the haymaker reads at
40px in motion.

Colour is STRUCTURE, not noise: a teal duotone shield carries two bold orange
load-bearing stripes plus one thin banded mid-stripe as a third accent, and
iridescent eye-jewels — controlled technicolor that never breaks the duotone
read. The night biome borrows a faint glow on ONLY the eye-jewels and
club-tips so the bruiser stays bold on dark skies without lighting the body.

North star: "a skin lives or dies at 40px in motion." The 40px tell is the
giant orange double-fist snapping past the snout, the teal/orange striped
shield, and the twin jewel periscopes.
"""
import math
import pygame

from game.parrot import (
    SPRITE_W, SPRITE_H, _WING_ANGLES, _add_outline, _aaellipse,
)


# ── tall-canvas constants (eye-stalks reach up into the headroom) ─────────────
COMPOSITE_W = SPRITE_W          # 64
COMPOSITE_H = 84
DY          = 12

BCX, BCY = 32, 32 + DY          # body centre  → (32, 44)
HCX, HCY = 44, 22 + DY          # head centre  → (44, 34)
CROWN_Y  = 12 + DY              # top of head  → 24


def _make_prebuilt_skin(build_fn):
    """Cached `(frame_idx, tilt_deg) -> Surface` getter — lazy 4-frame build
    + per-(frame, 3°) rotation cache, each frame house-outlined (the 1px dark
    contour the day-sky read needs)."""
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


def _strike(angle_deg):
    """0 = clubs cocked back (down-pose, wing=50), 1 = punched fully forward
    (up-pose, wing=-40). The reverse sense of a flap: lift the bird by
    throwing the punch, so the strike reads on the up-stroke."""
    return 1.0 - (angle_deg + 40) / 90.0


# ═════════════════════════════════════════════════════════════════════════════
# DUOTONE BRUISER palette — teal armoured shield + hot-orange hero.
#   Colour is load-bearing structure: the teal body and TWO bold orange
#   stripes are the read; the thin banded mid-stripe + jewel eyes are the
#   controlled third accent. No rainbow noise.
# ═════════════════════════════════════════════════════════════════════════════
_CARA   = (38, 178, 168)
_CARA_D = (20, 116, 110)
_CARA_H = (138, 236, 224)
_BAND   = (255, 124, 48)            # the two load-bearing orange stripes
_BAND_D = (206, 82, 26)
_BAND_H = (255, 192, 120)
_MID_A  = (255, 214, 70)            # thin banded mid-stripe — third accent
_MID_B  = (90, 210, 240)
_CLUB   = (255, 112, 56)
_CLUB_H = (255, 206, 140)
_CLUB_D = (182, 60, 24)
_CLUB_TIP = (255, 232, 188)         # club striking-face spark (night glow seed)
_STALK  = (36, 18, 58)
_STALK_RIM = (12, 8, 24)
_RIM    = (16, 86, 84)              # in-body dark rim that separates the fists
_EYE_HUE  = (118, 236, 216)
_EYE_HUE2 = (96, 150, 250)          # iridescent shift toward the jewel rim
_GLOW   = (120, 240, 220)


def _glow_dot(surf, cx, cy, r, col):
    """Soft additive halo for the night biome — used ONLY on eye-jewels and
    club-tips so the body stays a flat duotone silhouette."""
    g = pygame.Surface((r * 4, r * 4), pygame.SRCALPHA)
    for rr, a in ((r * 2, 40), (int(r * 1.4), 70), (r, 120)):
        pygame.draw.circle(g, (*col, a), (r * 2, r * 2), rr)
    surf.blit(g, (cx - r * 2, cy - r * 2), special_flags=pygame.BLEND_RGBA_ADD)


def _jewel_eye(surf, cx, cy, r, *, glow):
    """Iridescent compound eye on a thick periscope stalk tip: a teal jewel
    that shifts blue toward the rim, the famous equatorial mid-band of
    ommatidia, a bright specular pixel, and (night only) a soft halo.

    The jewel reads as the head's brightest mass so the twin periscopes carry
    the silhouette on both bright-day and dark-night skies."""
    if glow:
        # Keep the halo tighter than the jewel so the close-set twins stay
        # two distinct periscope lamps, not one goggle band, on night skies.
        _glow_dot(surf, cx, cy, max(2, r - 2), _GLOW)
    # Thin dark seat ring so the jewel pops off any sky (day-contour assist)
    # without bloating into a goggle when the twin eyes sit close.
    pygame.draw.circle(surf, _STALK_RIM, (cx, cy), r + 1, 1)
    # Iridescent body: blue-shifted rim, teal core.
    pygame.draw.circle(surf, _EYE_HUE2, (cx, cy), r)
    pygame.draw.circle(surf, _EYE_HUE, (cx, cy), max(1, r - 1))
    # Equatorial midband of ommatidia (the signature stripe across the eye).
    pygame.draw.line(surf, (250, 252, 250), (cx - r, cy), (cx + r, cy), 1)
    # One hot specular pixel so the eye snaps to attention at 40px.
    pygame.draw.circle(surf, (255, 255, 255), (cx - max(1, r // 3), cy - max(1, r // 3)),
                       max(1, r // 3))


# ═════════════════════════════════════════════════════════════════════════════
# Raptorial club arm — a "boxing-glove" dactyl club on a folded arm.
#   `s` 0..1 cocked→punched. The near (lead) club throws a full haymaker that
#   crosses PAST the snout on the punch; the far (rear) club stays lower and
#   shorter for depth. Both fists carry a dark heel rim so they never merge.
# ═════════════════════════════════════════════════════════════════════════════
def _club_arm(s, *, club_col, club_hi, arm_col, length, club_r, lead,
              glow):
    """One raptorial club arm on its own surface, anchored at the shoulder.

    lead=True  → the hero fist: cocked low+outward (clear of the snout), then
                 punched up+forward crossing the snout line.
    lead=False → the rear fist: damped, kept lower/back for the double-fist
                 read with a sky-gap to the lead club.
    Returns the surface; the caller blits it at the shoulder offset."""
    w = pygame.Surface((44, 36), pygame.SRCALPHA)
    sh = (8, 22)                                  # shoulder pivot

    if lead:
        # Cocked: fist pulled DOWN + OUTWARD so it never occludes the snout.
        # Punched: elbow drives up, fist crosses up past the snout line.
        elbow = (sh[0] + 7 + int(s * 5), sh[1] - 2 - int(s * 8))
        fist  = (sh[0] + 10 + int(s * length),
                 sh[1] + 8 - int(s * 18))
    else:
        # Rear fist: shorter throw, parked low+back for depth.
        elbow = (sh[0] + 6 + int(s * 3), sh[1] + 2 - int(s * 3))
        fist  = (sh[0] + 8 + int(s * length),
                 sh[1] + 10 - int(s * 8))

    # Segmented limb: dark-rimmed so the arm separates from the shield.
    pygame.draw.line(w, _RIM, sh, elbow, 5)
    pygame.draw.line(w, arm_col, sh, elbow, 3)
    pygame.draw.line(w, _RIM, elbow, fist, 5)
    pygame.draw.line(w, arm_col, elbow, fist, 3)
    pygame.draw.circle(w, arm_col, elbow, 2)

    # The dactyl club — a chunky rounded fist with a dark heel rim so the two
    # fists keep a 1px dark separation even when they overlap in depth.
    pygame.draw.circle(w, _STALK_RIM, fist, club_r + 1)
    pygame.draw.circle(w, club_col, fist, club_r)
    pygame.draw.circle(w, club_hi, (fist[0] - 1, fist[1] - 1), max(1, club_r - 2))
    # Striking-face ridge so the club reads as a hammer, not a ball.
    pygame.draw.line(w, _CLUB_D,
                     (fist[0] + club_r - 1, fist[1] - club_r + 1),
                     (fist[0] + club_r - 1, fist[1] + club_r - 1), 1)
    # Hot strike-spark on the leading face (and a night halo on the lead fist).
    pygame.draw.circle(w, _CLUB_TIP, (fist[0] + max(1, club_r - 2), fist[1]), 1)
    if glow and lead:
        _glow_dot(w, fist[0] + club_r - 1, fist[1], max(2, club_r - 3), _CLUB)
    return w


def _segmented_tail(surf, cx, cy, *, count, span):
    """Armoured teal abdomen sweeping back from the body with orange-banded
    plate edges, ending in an orange tail-fan (telson + uropods)."""
    step = span / count
    for i in range(count):
        x = cx - int(i * step)
        rx = 8 - i
        ry = 11 - i
        pygame.draw.ellipse(surf, _CARA_D, (x - rx, cy - ry + 1, rx * 2, ry * 2))
        pygame.draw.ellipse(surf, _CARA, (x - rx, cy - ry, rx * 2, ry * 2))
        pygame.draw.ellipse(surf, _BAND, (x - rx, cy - ry, rx * 2, ry * 2), 1)
    tx = cx - int(span)
    for dy, dx in ((-7, -6), (0, -9), (7, -6)):
        pygame.draw.polygon(surf, _BAND, [
            (tx, cy), (tx + dx, cy + dy), (tx + dx + 3, cy + dy)])
        pygame.draw.polygon(surf, _BAND_D, [
            (tx, cy), (tx + dx, cy + dy), (tx + dx + 3, cy + dy)], 1)


def _build(wing_angle_deg, *, glow):
    surf = _new()
    s = _strike(wing_angle_deg)

    # Body recoils slightly on the punch (shifts back + down) so the haymaker
    # has weight — the whole bruiser rocks with the strike.
    rcx = -int(s * 2)
    rcy = int(s * 1)
    bcx, bcy = BCX + rcx, BCY + rcy
    hcx, hcy = HCX + rcx, HCY + rcy

    # ── REAR fist: parked low+back, behind the shield, for the double-fist
    #    read. Sits clearly below + behind the lead fist (sky-gap between them).
    far = _club_arm(s * 0.6, club_col=_CLUB_D, club_hi=_CLUB,
                    arm_col=_CARA_D, length=8, club_r=6, lead=False, glow=glow)
    surf.blit(far, (hcx - 6, hcy + 9))

    # Segmented abdomen + orange tail-fan.
    _segmented_tail(surf, bcx - 7, bcy + 1, count=3, span=18)

    # ── Carapace shield — broad torpedo body, dark-rimmed for the day contour.
    _aaellipse(surf, _CARA_D, (bcx + 1, bcy + 1), 17, 14)
    _aaellipse(surf, _CARA, (bcx, bcy), 16, 13)
    _aaellipse(surf, _CARA_H, (bcx - 3, bcy - 4), 8, 4)

    # TWO bold orange load-bearing stripes across the shield (duotone signature).
    for off in (-5, 5):
        pygame.draw.line(surf, _BAND_D, (bcx + off - 1, bcy - 11),
                         (bcx + off - 1, bcy + 11), 4)
        pygame.draw.line(surf, _BAND, (bcx + off, bcy - 11),
                         (bcx + off, bcy + 11), 3)
        pygame.draw.line(surf, _BAND_H, (bcx + off, bcy - 9),
                         (bcx + off, bcy - 3), 1)
    # ONE thin banded mid-stripe between them — the controlled third accent
    # (alternating gold/cyan ticks), the only technicolor on the body.
    midx = bcx
    for k, ty in enumerate(range(bcy - 9, bcy + 10, 3)):
        pygame.draw.line(surf, (_MID_A, _MID_B)[k % 2], (midx, ty), (midx, ty + 1), 1)
    # Re-rim so the bands clamp inside the shield silhouette.
    pygame.draw.ellipse(surf, _CARA_D, (bcx - 16, bcy - 13, 32, 26), 1)

    # ── Head.
    _aaellipse(surf, _CARA_D, (hcx, hcy + 1), 11, 10)
    _aaellipse(surf, _CARA, (hcx - 1, hcy), 10, 9)
    _aaellipse(surf, _CARA_H, (hcx - 2, hcy - 3), 4, 2)

    # ── HERO: long widely-spread eye-stalks, thick (3px core + dark rim) so the
    #    twin periscopes read on both skies; jewel tip 2× the stalk width.
    for sgn, ex in ((-1, hcx - 6), (1, hcx + 7)):
        base = (hcx + sgn * 3, hcy - 3)
        tip = (ex + sgn * 4, CROWN_Y - 6 + rcy)
        pygame.draw.line(surf, _STALK_RIM, base, tip, 5)   # dark outline
        pygame.draw.line(surf, _STALK, base, tip, 3)        # 3px stalk core
        _jewel_eye(surf, tip[0], tip[1], 6, glow=glow)      # jewel ≈ 2× stalk

    # ── HERO: OVERSIZED lead club — the haymaker. On the punch it crosses up
    #    PAST the snout line; cocked it sits low+outward, clear of the face.
    near = _club_arm(s, club_col=_CLUB, club_hi=_CLUB_H,
                     arm_col=_CARA_D, length=13, club_r=8, lead=True, glow=glow)
    surf.blit(near, (hcx - 7, hcy + 4))
    return surf


def build_mantis_shrimp(wing_angle_deg):
    """Day/standard build — flat duotone, no body glow (the 1px house outline
    supplies the day-sky contour)."""
    return _build(wing_angle_deg, glow=False)


def build_mantis_shrimp_night(wing_angle_deg):
    """Night-biome build — identical silhouette with a faint glow on ONLY the
    eye-jewels and the lead club-tip. For review parity; the live skin can
    branch on biome phase to swap builds."""
    return _build(wing_angle_deg, glow=True)


get_mantis_shrimp = _make_prebuilt_skin(build_mantis_shrimp)
get_mantis_shrimp_night = _make_prebuilt_skin(build_mantis_shrimp_night)

# Liftable into game/animal_skins.py.
BUILDERS = {"skin_mantis_shrimp": get_mantis_shrimp}
