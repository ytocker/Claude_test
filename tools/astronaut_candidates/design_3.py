"""design_3 STARFARER — the LEGENDARY cosmic/galaxy deep-space explorer.

A deep cosmic-blue/violet suited macaw whose silhouette is built to survive
the 40px downscale as FIVE separable things, in priority order: (1) a bright
hard-edged GLOWING down-visor helmet DOME that owns the read, (2) the cyan/
magenta visor glass, (3) a hard two-value indigo BACK-PACK silhouette with a
single cyan nozzle, (4) a short directional glow DART off the pack (read as a
thruster, never a smear that touches the head), (5) a dark suited body with a
thin lit rim so it doesn't vanish on night sky.

Why the dome wins: at small sizes a soft additive comet smear reads as one
glowing blob, so the helmet shell carries its own hard white/cyan rim-light
arc (a lit sphere edge that survives nearest-downscale) and the aura behind
the head is kept small and dim so it FRAMES the dome instead of swallowing
it. Everything else is subordinated — the torso is ONE cosmic system (nebula
wisp + a few star dots), no sub-pixel panel/seam noise.

Why a full-body recolor + additive bloom (mirrors the dragon/phoenix/disco
shimmer idiom): the cosmic identity has to survive against BOTH a bright day
sky and a dark night sky, so the body is re-plumaged dark cosmic-navy (self-
contrasting on day) while the cyan/magenta glow is laid down with
BLEND_RGB_ADD bloom layers that punch through on night. A thin cyan/violet
rim down the suit edge carries the night read without brightening the whole
suit and killing the day self-contrast. The legendary "tell" is ONE clean
motion: the dart length and a single visor-brightness step ride
``wing_angle_deg`` so the flap reads, not a field of competing twinkles.

Exploration only — wrapped by ``store_skins._make_skin``; NOT registered in
``store_skins.BUILDERS`` and production art is untouched.
"""
import math
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, COMPOSITE_W, COMPOSITE_H, PARROT_DY
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette
from game.parrot import _aaellipse


# ── cosmic palette ───────────────────────────────────────────────────────────
_BODY      = (18, 16, 42)          # #12102A deep cosmic body
_BODY_DK   = (11, 10, 28)
_MID       = (42, 33, 96)          # #2A2160 violet mid
_MID_DK    = (28, 22, 64)
_CYAN      = (63, 224, 255)        # #3FE0FF cyan glow
_CYAN_DK   = (28, 120, 168)
_MAGENTA   = (255, 79, 216)        # #FF4FD8 magenta nebula glow
_MAG_DK    = (150, 36, 124)
_STAR      = (255, 255, 255)       # #FFFFFF stars / visor highlight
_INDIGO    = (24, 20, 70)          # deep visor glass
_INDIGO_DK = (12, 10, 38)


# Full cosmic-suit re-plumage. Body is dark navy/violet so the silhouette
# self-contrasts on a bright sky; the glow accents (laid down separately as
# additive bloom in _paint) carry the night read. Lenses dropped — the
# glowing down-visor owns the face.
_PAL = _pal(
    tail=[(14, 12, 36), (20, 17, 52), (30, 24, 74), (42, 33, 96)],
    tail_line=_INDIGO_DK,
    body_shadow=_BODY_DK,
    body_main=_BODY,
    body_chest=(30, 25, 70),
    body_belly=(22, 19, 54),
    sheen=(120, 130, 220, 60),
    wing_main=(24, 20, 60),
    wing_dark=_BODY_DK,
    wing_tip=(48, 40, 110),
    wing_secondary=None,
    wing_highlight=(96, 86, 180),
    head_shadow=_BODY_DK,
    head_main=_BODY,
    head_cheek=(34, 28, 80),
    head_crown=(40, 33, 96),
    lens_frame=(30, 25, 70),
    lens_body=_INDIGO_DK,
    lens_tint=None,
    lens_glint=None,
    beak_main=(40, 33, 96),
    beak_dark=_INDIGO_DK,
    beak_gloss=(96, 86, 180),
    foot=(30, 25, 70),
)


def _cosmic_base(angle_deg):
    return _build_parrot_with_palette(angle_deg, _PAL, draw_lenses=False)


# ── additive-bloom helper ─────────────────────────────────────────────────────

def _bloom(surf, cx, cy, radius, color, alpha):
    """Soft additive glow disc (mirrors draw.blit_glow's BLEND_ADD idiom but
    self-contained so the candidate has no extra import surface). Drawn with
    BLEND_RGB_ADD so cyan/magenta light add together and punch on night sky."""
    if radius < 1:
        return
    g = pygame.Surface((radius * 2 + 2, radius * 2 + 2), pygame.SRCALPHA)
    steps = max(3, radius // 2)
    for i in range(steps, 0, -1):
        a = int(alpha * (i / steps) ** 2)
        r = int(radius * i / steps)
        pygame.draw.circle(g, (*color, a), (radius + 1, radius + 1), r)
    surf.blit(g, (cx - radius - 1, cy - radius - 1),
              special_flags=pygame.BLEND_RGB_ADD)


def _paint(surf, wing_angle_deg):
    # The base wing angles run +50..-40 across the flap; remap to 0..1 phase.
    # ONE animation system: the dart grows with phase and the visor steps up
    # one brightness notch on the downbeat — no competing per-element twinkles.
    phase = (50 - wing_angle_deg) / 90.0           # 0 on up-flap → 1 on down
    pulse = 0.55 + 0.45 * math.sin(phase * math.pi)

    cx, cy = HX + 1, HY - 2
    r = 14

    # ── BACK-PACK + thruster DART (drawn FIRST, behind the body) ──
    # The pack is a HARD two-value indigo silhouette (structure, not glow) so
    # the back element survives downscale even on the up-flap when the dart is
    # short. A single tight directional dart streams off the nozzle — 3 discs,
    # low alpha, short — a separable thruster tell that never touches the head.
    tx, ty = HX - 22, HY + 12                       # pack mount on the back
    # Tight directional glow dart (start ~10 → grow to ~18 with the flap).
    dart_len = 10 + int(8 * phase)
    for i in range(3):
        t = i / 2.0
        ex = tx - 6 - int(dart_len * t)
        ey = ty + 7 + int(7 * t)
        _bloom(surf, ex, ey, 5 - i, _CYAN, int(90 * (1 - 0.4 * t)))

    # ── aura halo behind the head — SMALL + DIM so it FRAMES the dome ──
    _bloom(surf, cx, cy, r + 3, (90, 70, 200), int(40 + 30 * pulse))

    # Hard two-value indigo pack silhouette (no soft ellipse glow).
    pygame.draw.ellipse(surf, _INDIGO_DK, (tx - 6, ty - 3, 16, 18))
    pygame.draw.ellipse(surf, _MID_DK, (tx - 4, ty - 1, 11, 13))
    # ONE bright cyan nozzle dot — the single hard glow tell on the pack.
    pygame.draw.circle(surf, _CYAN, (tx - 2, ty + 7), 2)
    pygame.draw.circle(surf, _STAR, (tx - 2, ty + 7), 1)

    # ── NIGHT-SURVIVAL rim on the suit body ──
    # One thin cyan/violet rim down the back + belly edge so the navy body
    # doesn't vanish on a dark sky / dark pillars — without brightening the
    # whole suit (which would kill the day self-contrast).
    _RIM = (96, 86, 180)
    pygame.draw.lines(surf, _RIM, False,
                      [(24, 30), (22, 37), (24, 44), (29, 48)], 1)   # back edge
    pygame.draw.lines(surf, _RIM, False,
                      [(40, 31), (43, 38), (40, 45)], 1)             # belly edge

    # ── COSMIC TORSO: ONE system — nebula wisp + a few brightest stars ──
    body_cx, body_cy = 31, 33
    _bloom(surf, body_cx + 1, body_cy - 2, 10, _MAGENTA, 55)
    _bloom(surf, body_cx - 3, body_cy + 3, 8, _CYAN, 42)
    # Only the 3–4 brightest star dots survive 40px; the dense field is cut.
    for sx, sy in ((27, 30), (34, 28), (30, 39), (38, 35)):
        pygame.draw.circle(surf, _STAR, (sx, sy), 1)
    store_skins._spark(surf, 31, 33, 2, _STAR)

    # ── GLOWING DOWN-VISOR HELMET (the brightest, biggest, hardest shape) ──
    # White EVA collar ring behind the dome so the helmet reads as seated.
    pygame.draw.ellipse(surf, (210, 214, 230), (cx - 11, cy + 8, 24, 9))
    pygame.draw.ellipse(surf, (150, 156, 180), (cx - 11, cy + 12, 24, 5))

    # Dark dome shell.
    pygame.draw.circle(surf, _INDIGO_DK, (cx, cy), r)
    pygame.draw.circle(surf, _INDIGO, (cx, cy - 1), r - 1)

    # HARD lit edge on the DOME SHELL itself: a 2px bright cyan/white rim-light
    # arc on the top-left. This is the read that survives the downscale — the
    # sphere keeps a crisp lit edge instead of dissolving into the aura.
    shell = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
    sc = r + 2
    pygame.draw.arc(shell, (215, 245, 255), (sc - r, sc - r, r * 2, r * 2),
                    math.radians(95), math.radians(195), 2)
    pygame.draw.arc(shell, (*_CYAN, 200), (sc - r, sc - r, r * 2, r * 2),
                    math.radians(85), math.radians(205), 2)
    surf.blit(shell, (cx - sc, cy - sc))

    # The DOWN visor: a deep-indigo curved glass filling the dome, clipped to a
    # circle so it stays a clean shape. Built on its own layer to clip cleanly.
    visor = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
    vc = r + 2
    pygame.draw.ellipse(visor, (20, 16, 60), (3, 3, r * 2 - 2, r * 2 - 4))
    # Magenta→cyan vertical nebula sheen baked into the glass.
    pygame.draw.ellipse(visor, (60, 30, 110), (5, 6, r * 2 - 6, r - 2))
    clip = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
    pygame.draw.circle(clip, (255, 255, 255, 255), (vc, vc), r - 3)
    visor.blit(clip, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(visor, (cx - vc, cy - vc))

    # Two star sparkles on the glass (kept minimal — no flap twinkle here).
    pygame.draw.circle(surf, _STAR, (cx - 5, cy - 4), 1)
    pygame.draw.circle(surf, _STAR, (cx + 4, cy + 2), 1)

    # Visor RIM glow: cyan top-left, magenta lower-right, with ONE clean
    # brightness step on the downbeat (the single visor animation).
    rim = pygame.Surface((r * 2 + 8, r * 2 + 8), pygame.SRCALPHA)
    rc = r + 4
    step = 70 if phase > 0.5 else 0                 # one discrete brightness notch
    pygame.draw.arc(rim, (*_CYAN, 170 + step),
                    (rc - r, rc - r, r * 2, r * 2),
                    math.radians(30), math.radians(200), 3)
    pygame.draw.arc(rim, (*_MAGENTA, 170 + step),
                    (rc - r, rc - r, r * 2, r * 2),
                    math.radians(200), math.radians(390), 3)
    surf.blit(rim, (cx - rc, cy - rc), special_flags=pygame.BLEND_RGB_ADD)
    # Additive rim bloom so the cyan+magenta read as light, not just lines.
    _bloom(surf, cx - 8, cy - 6, 5, _CYAN, 110 + step // 2)
    _bloom(surf, cx + 8, cy + 4, 5, _MAGENTA, 110 + step // 2)

    # Single crisp specular sweep across the glass — keeps it a sphere.
    pygame.draw.line(surf, (180, 220, 255), (cx - 7, cy - 6), (cx - 2, cy - 9), 2)
    pygame.draw.circle(surf, _STAR, (cx - 6, cy - 8), 1)


build = store_skins._make_skin(_paint, base_fn=_cosmic_base)
