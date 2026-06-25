"""design_4 · AURORA MACAW — LEGENDARY parrot-rarity exploration.

Night sky given wings: a midnight-galaxy Pip haloed by a soft additive ring,
crowned with a green↔magenta nebula crest, trailing flowing aurora ribbons
where the tail-fan was. The legendary tell is the luminous halo PLUS the
silhouette-breaking ribbon tail — a clear tier above the single-zone epics.

Draw order matters: the halo and the ribbon tail must paint BEHIND the body,
so this can't use store_skins._make_skin's body-first `_compose`. Mirroring
the viking-axe pattern, this is a custom getter — back-aura (halo + ribbons)
→ recoloured galaxy body → front overlay (nebula crest, star flecks, rim
light) → house outline → per-(frame, 3°-bucket) rotation cache.

Exploration only — NEVER registered in store_skins.BUILDERS. The aurora is
BAKED into each of the 4 frames (no runtime particle hook); the ribbons sweep
with the wing beat so the flap still reads alive.
"""
import pygame

from game.parrot import _WING_ANGLES, _add_outline
from game.draw import blit_glow, lerp_color
from game.store_skins import (
    COMPOSITE_W, COMPOSITE_H, PARROT_DY, HX, HY, CROWN_Y,
)
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette


# ── palette (brief) ───────────────────────────────────────────────────────────
_INDIGO   = (28, 27, 58)          # #1C1B3A midnight indigo
_GREEN    = (63, 224, 166)        # #3FE0A6 aurora green
_MAGENTA  = (196, 92, 232)        # #C45CE8 aurora magenta
_STARBLU  = (111, 168, 255)       # #6FA8FF star blue
_GLINT    = (255, 255, 255)       # #FFFFFF star glint

# Body re-plumage: a deep midnight-indigo galaxy. The crown/back cool toward
# aurora teal and the belly carries a faint magenta undertone so the bird is
# unmistakably cosmic, not just dark-blue. Lenses keep Pip's aviators but tint
# to aurora teal so the signature shades read on the night palette.
_AURORA_PAL = _pal(
    tail=[(22, 21, 46), (28, 27, 58), (40, 42, 86), (58, 70, 120)],
    tail_line=(16, 15, 34),
    body_shadow=(18, 17, 40),
    body_main=_INDIGO,
    body_chest=(46, 44, 92),
    body_belly=(40, 34, 74),
    sheen=(150, 180, 255, 70),
    wing_main=(32, 32, 70),
    wing_dark=(16, 15, 34),
    wing_tip=(70, 96, 160),
    wing_secondary=None,
    wing_highlight=(96, 150, 220),
    head_shadow=(18, 17, 40),
    head_main=_INDIGO,
    head_cheek=(48, 50, 100),
    head_crown=(40, 56, 104),
    lens_frame=(70, 80, 130),
    lens_body=(10, 12, 28),
    lens_tint=(70, 200, 170, 150),
    lens_glint=(220, 255, 245),
    beak_main=(120, 130, 180),
    beak_dark=(40, 44, 84),
    beak_gloss=(200, 215, 255),
    foot=(60, 64, 110),
)


def _aurora_base(angle_deg):
    return _build_parrot_with_palette(angle_deg, _AURORA_PAL)


# ── shared helpers ────────────────────────────────────────────────────────────

def _aurora_mix(t):
    """Green→star-blue→magenta light band, the aurora's signature ramp."""
    if t < 0.5:
        return lerp_color(_GREEN, _STARBLU, t / 0.5)
    return lerp_color(_STARBLU, _MAGENTA, (t - 0.5) / 0.5)


def _flap_phase(angle_deg):
    """0 on the down-stroke (wing 50°) → 1 on the up-stroke (-40°). The ribbons
    stream long/loose on the up-beat and bunch tight on the down-beat so the
    baked aurora still feels alive across the 4 frames."""
    return 1.0 - (angle_deg + 40) / 90.0


# ── back layer: halo ring + aurora ribbon tail ───────────────────────────────

def _aurora_back(surf, angle_deg):
    """Every glowing element lives here, BEHIND the outlined bird, so the house
    outline (grown from the bird's alpha mask) never boxes a bloom into its own
    dark-rimmed island. Two passes, both un-outlined:

      1. an ADDITIVE under-glow buffer — gives the halo/crest/ribbons a soft
         lit bloom on dark night skies, where additive shines.
      2. an OPAQUE bright-detail buffer alpha-blitted ON TOP — the ring annulus,
         crest cores and ribbon spines as solid bright pixels with a thin dark
         indigo backing, so they ALSO survive a bright-blue day/dusk sky where
         additive washes out. A legendary has to read on both.

    Contents: the legendary HALO ring framing the head, the NEBULA CREST wisps
    past the crown, and the AURORA RIBBON tail replacing the feather fan."""
    phase = _flap_phase(angle_deg)
    cbx, cby = HX, CROWN_Y + 1                      # crest root, on the crown
    hcx, hcy = HX - 2, HY - 3                       # halo centre, behind head
    crest = ((-7, -20, 0.0), (-1, -26, 0.45), (6, -19, 1.0))
    sway = (phase - 0.5) * 4

    def ribbon_pts(k):
        spread = 4 + k * 5
        reach  = 22 + int(phase * 8)
        sway2  = (1.0 - phase) * 3                  # bunch tighter down-beat
        bx, by = 13, HY + 8 + k * 3
        mid = (bx - reach * 0.55 - sway2, by + 7 + k * 4 + spread * 0.4)
        tip = (bx - reach - sway2, by + 15 + k * 6 + spread)
        return (bx, by), mid, tip, spread

    # ── pass 1: additive under-glow (night) ──────────────────────────────────
    glow = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    blit_glow(glow, hcx, hcy, 21, _STARBLU, alpha=80)
    for dx, dy, t in crest:
        blit_glow(glow, int(cbx + dx + sway), int(cby + dy), 5, _aurora_mix(t), alpha=120)
    for k in range(3):
        (bx, by), mid, tip, _ = ribbon_pts(k)
        blit_glow(glow, int(mid[0]), int(mid[1]), 5, _aurora_mix(k / 2.0), alpha=90)
        blit_glow(glow, int(tip[0]), int(tip[1]), 4, _aurora_mix(k / 2.0), alpha=90)
    surf.blit(glow, (0, 0), special_flags=pygame.BLEND_ADD)

    # ── pass 2: opaque bright detail (day + night) ───────────────────────────
    det = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    _INK = (16, 14, 32)                             # thin dark backing for bright sky

    # Halo ring — the legendary tell. Dark backing ring, then a bright green→
    # magenta annulus + a white inner glint so it reads as a RING on any sky.
    pygame.draw.circle(det, _INK, (hcx, hcy), 17, 3)
    pygame.draw.circle(det, _GREEN, (hcx, hcy), 16, 2)
    pygame.draw.circle(det, _MAGENTA, (hcx, hcy), 16, 1)
    pygame.draw.circle(det, _GLINT, (hcx, hcy), 17, 1)

    # Nebula crest — three bright wisps rising past the crown over a dark hair-
    # line so they hold against a blue sky; glint tips break the crown outline.
    for dx, dy, t in crest:
        col = _aurora_mix(t)
        tipx, tipy = cbx + dx + sway, cby + dy
        ctrl = (cbx + dx * 0.5 + sway * 0.5, cby + dy * 0.5)
        path = [(cbx + dx * 0.25, cby), ctrl, (tipx, tipy)]
        pygame.draw.lines(det, _INK, False, path, 4)
        pygame.draw.lines(det, col, False, path, 2)
        pygame.draw.circle(det, _GLINT, (int(tipx), int(tipy)), 2)

    # Aurora ribbon tail — bright spines over dark backing, each a curtain that
    # sweeps down-back into open sky and ends in a glint; the lower silhouette
    # break that makes the legendary unmistakable in motion.
    for k in range(3):
        (bx, by), mid, tip, spread = ribbon_pts(k)
        col = _aurora_mix(k / 2.0)
        quad = [(bx, by - 4), (bx, by + 4),
                (mid[0], mid[1] + 5), (tip[0], tip[1] + 4),
                (tip[0] - 2, tip[1] - 3), (mid[0], mid[1] - 4)]
        pygame.draw.polygon(det, (*col, 130), quad)
        path = [(bx, by), mid, tip]
        pygame.draw.lines(det, _INK, False, path, 4)
        pygame.draw.lines(det, col, False, path, 2)
        pygame.draw.circle(det, _GLINT, (int(tip[0]), int(tip[1])), 2)

    surf.blit(det, (0, 0))


# ── front overlay: nebula crest, star flecks, rim light ──────────────────────

def _aurora_front(surf, angle_deg):
    """Painted OVER the body and INSIDE the masked layer, so only crisp opaque
    detail belongs here (soft glow lives in _aurora_back to dodge the outline):
    an aurora rim-light along the lit back edge, and small white star flecks
    across the midnight plumage. These survive the downscale as hard pixels."""
    # Aurora rim-light tracing the back/crown silhouette edge — a thin cool
    # band so the indigo body never reads as a flat void against night.
    pygame.draw.lines(surf, _STARBLU, False,
                      [(HX - 11, CROWN_Y + 2), (HX - 4, CROWN_Y - 1),
                       (HX + 5, CROWN_Y), (HX + 11, HY - 3)], 1)
    pygame.draw.lines(surf, _GREEN, False,
                      [(20, 40), (26, 36), (34, 35), (43, 38)], 1)

    # Star flecks across the midnight plumage — a fixed scatter (NOT random, so
    # frames are stable) of small white/blue twinkles, each a dot + a tiny cross
    # so it reads as a star. Kept off the face so the eyes stay clean.
    stars = (
        (26, 50, 1, _GLINT),
        (22, 44, 1, _STARBLU),
        (31, 56, 1, _GLINT),
        (38, 52, 1, _STARBLU),
        (19, 38, 1, _GLINT),
        (34, 46, 1, _STARBLU),
        (45, 32, 1, _GLINT),
    )
    for sx, sy, r, col in stars:
        pygame.draw.circle(surf, col, (sx, sy), r)
        if col is _GLINT:                  # only the brightest get a twinkle cross
            pygame.draw.line(surf, (*col, 160), (sx - 2, sy), (sx + 2, sy), 1)
            pygame.draw.line(surf, (*col, 160), (sx, sy - 2), (sx, sy + 2), 1)


# ── custom compose + getter (halo/ribbons need a back layer) ──────────────────

def _aurora_getter():
    """back aura (halo + ribbons) → galaxy body → front nebula/stars/rim →
    house outline, then the per-(frame, 3°-bucket) rotation cache shared by
    every store skin."""
    state = {"frames": None, "rot": {}}

    def _flat(wing_angle):
        # The house outline is grown from the alpha mask, so the faint additive
        # halo + ribbons must NOT be part of the masked layer — else the dark
        # rim would wrap the glow and kill it. So outline the OPAQUE bird (body
        # + front overlay) alone, then lay the soft back-aura UNDER it. The
        # outline pads by 2px; the aura surface is padded to match before the
        # under-blit so the bird stays centred for the rotation maths.
        bird = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
        bird.blit(_aurora_base(wing_angle), (0, PARROT_DY))
        _aurora_front(bird, wing_angle)
        bird = _add_outline(bird)

        aura = pygame.Surface(bird.get_size(), pygame.SRCALPHA)
        pad = (bird.get_width() - COMPOSITE_W) // 2
        back = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
        _aurora_back(back, wing_angle)
        aura.blit(back, (pad, pad))
        aura.blit(bird, (0, 0))
        return aura

    def getter(frame_idx, tilt_deg):
        if state["frames"] is None:
            state["frames"] = [_flat(a) for a in _WING_ANGLES]
        frames = state["frames"]
        frame_idx %= len(frames)
        key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
        s = state["rot"].get(key)
        if s is None:
            s = pygame.transform.rotozoom(frames[frame_idx], key[1], 1.0)
            state["rot"][key] = s
        return s

    return getter


build = _aurora_getter()
