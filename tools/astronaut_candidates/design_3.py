"""design_3 STARFARER — the LEGENDARY cosmic/galaxy deep-space explorer.

A walking galaxy: a deep cosmic-blue/violet suited macaw with a GLOWING
down-visor helmet breaking the crown, an ENERGY THRUSTER on the back
streaming a comet-trail of stars past the tail, a starfield-speckled torso
with a nebula wisp, and a glowing constellation panel on the chest. Cyan
glow seams trace the wing root and legs. The legendary "tell" is motion:
the visor rim pulse, the back star-trail length, and the aura halo all
ride ``wing_angle_deg`` so the skin shimmers with every flap — yet the
STILL frame already reads as an astronaut (dome + visor + back pack +
suited body) at 40px.

Why a full-body recolor + additive bloom (mirrors the dragon/phoenix/disco
shimmer idiom): the cosmic identity has to survive against BOTH a bright day
sky and a dark night sky, so the body is re-plumaged dark cosmic-navy (self-
contrasting on day) while the cyan/magenta glow is laid down with
BLEND_RGB_ADD bloom layers that punch through on night. Neither read leans
on the background.

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
    # The base wing angles run +50..-40 across the flap; remap to 0..1 phase so
    # the trail streams longest and the visor pulses brightest on the downbeat.
    phase = (50 - wing_angle_deg) / 90.0           # 0 on up-flap → 1 on down
    pulse = 0.55 + 0.45 * math.sin(phase * math.pi)

    cx, cy = HX + 1, HY - 2
    r = 14

    # ── ENERGY THRUSTER + comet star-trail (drawn FIRST, behind the body) ──
    # A small dark unit low on the back with a gradient streak + star particles
    # flowing out past the tail; the streak grows with the flap = legendary tell.
    tx, ty = HX - 22, HY + 12                       # thruster mount on the back
    trail_len = 16 + int(14 * phase)
    # Additive comet streak fanning down-left into open sky behind the tail.
    for i in range(6):
        t = i / 5.0
        ex = tx - int(trail_len * t) - 4
        ey = ty + 6 + int(10 * t)
        col = _CYAN if i % 2 == 0 else _MAGENTA
        _bloom(surf, ex, ey, 6 - i // 2, col, int(150 * (1 - t) * pulse))
    # Discrete star particles riding the trail (twinkle scales with the flap).
    for i, (sx, sy, sr) in enumerate(((tx - 9, ty + 9, 2), (tx - 16, ty + 13, 2),
                                      (tx - 23, ty + 16, 1), (tx - 12, ty + 4, 1),
                                      (tx - 20, ty + 7, 1))):
        bright = i % 2 == 0
        if bright or phase > 0.5:
            store_skins._spark(surf, sx, sy, sr + (1 if bright else 0), _STAR)
    # Thruster nozzle glow at the mount.
    _bloom(surf, tx - 2, ty + 4, 7, _CYAN, int(170 * pulse))

    # ── aura halo behind everything on the head (faint, pulses) ──
    _bloom(surf, cx, cy, r + 9, _MID, int(70 + 40 * pulse))
    _bloom(surf, cx, cy, r + 4, (90, 70, 200), int(60 + 50 * pulse))

    # ── thruster body unit (a small dark pack, NOT a metal backpack) ──
    pygame.draw.ellipse(surf, _INDIGO_DK, (tx - 6, ty - 3, 16, 18))
    pygame.draw.ellipse(surf, _MID_DK, (tx - 5, ty - 3, 13, 15))
    pygame.draw.ellipse(surf, _MID, (tx - 3, ty - 2, 8, 7))
    # Glowing vent line + nozzle ring on the pack.
    pygame.draw.line(surf, _CYAN, (tx - 4, ty + 9), (tx + 6, ty + 7), 2)
    pygame.draw.circle(surf, _CYAN, (tx - 2, ty + 6), 2)
    pygame.draw.circle(surf, _STAR, (tx - 2, ty + 6), 1)

    # ── COSMIC TORSO: baked starfield + nebula wisp on the recolored body ──
    body_cx, body_cy = 31, 33
    # Soft nebula wisp (magenta→teal additive patch on the chest).
    _bloom(surf, body_cx + 1, body_cy - 2, 11, _MAGENTA, 60)
    _bloom(surf, body_cx - 3, body_cy + 3, 9, _CYAN, 45)
    # Baked white starfield speckles across the torso (static — the "galaxy").
    for sx, sy, sr in ((25, 27, 1), (33, 24, 1), (38, 31, 1), (22, 36, 1),
                       (30, 39, 1), (36, 38, 1), (27, 32, 1), (41, 27, 1),
                       (24, 41, 1), (34, 30, 1)):
        pygame.draw.circle(surf, _STAR, (sx, sy), sr)
    # A couple of brighter twinkles to lift the field.
    store_skins._spark(surf, 28, 29, 2, _STAR)
    store_skins._spark(surf, 37, 35, 2, _STAR)

    # ── CONSTELLATION chest panel (in place of a button panel) ──
    # 4 star nodes joined by thin glowing lines — a tiny stitched constellation.
    nodes = [(26, 44), (31, 40), (36, 43), (33, 47)]
    for a, b in ((0, 1), (1, 2), (1, 3)):
        pygame.draw.line(surf, _CYAN_DK, nodes[a], nodes[b], 2)
        pygame.draw.line(surf, _CYAN, nodes[a], nodes[b], 1)
    for nx, ny in nodes:
        _bloom(surf, nx, ny, 3, _CYAN, 150)
        pygame.draw.circle(surf, _STAR, (nx, ny), 1)

    # ── LIMB glow seams ──
    # Cyan glow seam along the wing root + a thin glow line down each leg.
    pygame.draw.line(surf, _CYAN_DK, (38, 47), (47, 44), 3)
    pygame.draw.line(surf, _CYAN, (38, 47), (47, 44), 1)
    for lx0, lx1 in ((28, 26), (34, 36)):
        pygame.draw.line(surf, _CYAN, (lx0, 45), (lx1, 49), 1)
    # Star-twinkle at the wingtip (rides the flap so the tip sparkles).
    if phase > 0.35:
        store_skins._spark(surf, 47, 43, 2, _STAR)

    # ── GLOWING DOWN-VISOR HELMET (breaks the crown; owns the face) ──
    # White EVA collar ring behind the dome so the helmet reads as seated.
    pygame.draw.ellipse(surf, (210, 214, 230), (cx - 11, cy + 8, 24, 9))
    pygame.draw.ellipse(surf, (150, 156, 180), (cx - 11, cy + 12, 24, 5))
    # Outer glow ring around the dome (additive — the legendary halo on the head).
    _bloom(surf, cx, cy, r + 5, _CYAN, int(90 + 60 * pulse))

    # Dark dome shell.
    pygame.draw.circle(surf, _INDIGO_DK, (cx, cy), r)
    pygame.draw.circle(surf, _INDIGO, (cx, cy - 1), r - 1)

    # The DOWN visor: a deep-indigo curved glass filling the dome, clipped to a
    # circle so it stays a clean shape. Built on its own layer to clip cleanly.
    visor = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
    vc = r + 2
    pygame.draw.ellipse(visor, (20, 16, 60), (3, 3, r * 2 - 2, r * 2 - 4))
    # Magenta→cyan vertical nebula sheen baked into the glass.
    pygame.draw.ellipse(visor, (60, 30, 110), (5, 6, r * 2 - 6, r - 2))
    clip = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
    pygame.draw.circle(clip, (255, 255, 255, 255), (vc, vc), r - 2)
    visor.blit(clip, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(visor, (cx - vc, cy - vc))

    # Tiny star sparkles twinkling ON the glass.
    pygame.draw.circle(surf, _STAR, (cx - 5, cy - 4), 1)
    pygame.draw.circle(surf, _STAR, (cx + 4, cy + 2), 1)
    if phase > 0.5:
        store_skins._spark(surf, cx + 2, cy - 6, 2, _STAR)

    # Visor RIM glow: cyan-to-magenta rim that PULSES with the flap. Two arcs
    # so the cyan owns the top-left and magenta the lower-right of the curve.
    rim = pygame.Surface((r * 2 + 8, r * 2 + 8), pygame.SRCALPHA)
    rc = r + 4
    pygame.draw.arc(rim, (*_CYAN, int(180 * pulse + 70)),
                    (rc - r, rc - r, r * 2, r * 2),
                    math.radians(30), math.radians(200), 3)
    pygame.draw.arc(rim, (*_MAGENTA, int(180 * pulse + 70)),
                    (rc - r, rc - r, r * 2, r * 2),
                    math.radians(200), math.radians(390), 3)
    surf.blit(rim, (cx - rc, cy - rc), special_flags=pygame.BLEND_RGB_ADD)
    # Additive rim bloom so the pulse glows rather than just brightens a line.
    _bloom(surf, cx - 8, cy - 6, 5, _CYAN, int(120 * pulse))
    _bloom(surf, cx + 8, cy + 4, 5, _MAGENTA, int(120 * pulse))

    # Single crisp specular sweep across the glass — keeps it a sphere.
    pygame.draw.line(surf, (180, 220, 255), (cx - 7, cy - 6), (cx - 2, cy - 9), 2)
    pygame.draw.circle(surf, _STAR, (cx - 6, cy - 8), 1)


build = store_skins._make_skin(_paint, base_fn=_cosmic_base)
