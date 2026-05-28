"""Dead-Pip variants for the on-death cross-fade overlay.

Mirrors `dollar_parrot_ghost`'s shape: palettes built with `_pal` + per-
variant builders that compose `_build_parrot_with_palette` with an
optional pre-body aura and integrated eye treatment (X-strokes / hollow
sockets / glowing pupils) drawn into the body surface in palette colours.

Three palettes ship side-by-side so the user can compare in-game via the
F8 dev-cycle key:
  E. NIGHT-VAPOR DARK    — ship lead, glowing toxic pupils + faint aura
  B. CHARTREUSE ECTOPLASM — hot yellow hollow sockets, shared aura
  C. WITHERED BRUISE     — eggplant + chartreuse, slim X-strokes

E's aura scales with the cross-fade `t` so the bird never reads
"haunted while still alive" during the early fade frames.
"""
import pygame

from game.parrot import SPRITE_W, SPRITE_H, _WING_ANGLES, _add_outline
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette
from game.draw import blit_glow


LENS_L = (46, 20)
LENS_R = (56, 19)
TOXIC_AURA = (90, 220, 80)


# ── PALETTE E — NIGHT-VAPOR DARK (ship lead) ────────────────────────────────

P_NIGHTVAPOR = _pal(
    tail=[(28, 35, 30), (40, 50, 40), (55, 70, 50), (70, 90, 55)],
    tail_line=(15, 22, 18),
    body_shadow=(12, 18, 18),
    body_main=(40, 55, 45),
    body_chest=(60, 80, 55),
    body_belly=(85, 110, 70),
    sheen=(160, 200, 120, 90),
    wing_main=(30, 25, 55),
    wing_dark=(12, 10, 28),
    wing_tip=(70, 95, 50),
    wing_secondary=None,
    wing_highlight=(160, 200, 110),
    head_shadow=(15, 22, 22),
    head_main=(45, 60, 50),
    head_cheek=(65, 85, 60),
    head_crown=(80, 105, 70),
    lens_frame=(120, 170, 60),
    lens_body=(8, 12, 8),
    lens_tint=None,
    lens_glint=None,
    beak_main=(85, 95, 60),
    beak_dark=(35, 40, 25),
    beak_gloss=(160, 190, 110),
    foot=(20, 28, 22),
)


def build_nightvapor_dead(angle_deg, aura_scale=1.0):
    out = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    aura_alpha = max(0, min(255, int(110 * aura_scale)))
    if aura_alpha > 0:
        blit_glow(out, 32, 30, 24, TOXIC_AURA, alpha=aura_alpha)
    body = _build_parrot_with_palette(angle_deg, P_NIGHTVAPOR)
    out.blit(body, (0, 0))
    for ex, ey in (LENS_L, LENS_R):
        blit_glow(out, ex, ey, 5, (180, 230, 80), alpha=220)
        pygame.draw.circle(out, (210, 245, 110), (ex, ey), 2)
        pygame.draw.circle(out, (245, 255, 200), (ex - 1, ey - 1), 1)
    return out


# ── PALETTE B — CHARTREUSE ECTOPLASM (alternate) ────────────────────────────

P_CHARTREUSE = _pal(
    tail=[(110, 140, 25), (150, 175, 35), (185, 205, 50), (215, 225, 75)],
    tail_line=(70, 90, 20),
    body_shadow=(85, 105, 25),
    body_main=(190, 220, 70),
    body_chest=(210, 230, 95),
    body_belly=(225, 235, 130),
    sheen=(245, 250, 180, 120),
    wing_main=(140, 165, 35),
    wing_dark=(65, 85, 15),
    wing_tip=(210, 225, 70),
    wing_secondary=(230, 235, 110),
    wing_highlight=(240, 240, 160),
    head_shadow=(90, 110, 30),
    head_main=(195, 220, 75),
    head_cheek=(215, 230, 100),
    head_crown=(225, 235, 130),
    lens_frame=(70, 90, 20),
    lens_body=(10, 18, 8),
    lens_tint=None,
    lens_glint=None,
    beak_main=(190, 180, 60),
    beak_dark=(105, 95, 20),
    beak_gloss=(230, 225, 140),
    foot=(70, 85, 20),
)


def build_chartreuse_dead(angle_deg, aura_scale=1.0):
    out = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    aura_alpha = max(0, min(255, int(110 * aura_scale)))
    if aura_alpha > 0:
        blit_glow(out, 32, 30, 24, TOXIC_AURA, alpha=aura_alpha)
    body = _build_parrot_with_palette(angle_deg, P_CHARTREUSE)
    for cx, cy in (LENS_L, LENS_R):
        pygame.draw.circle(body, (5, 10, 5), (cx, cy), 3)
        pygame.draw.line(body, (45, 60, 20), (cx - 2, cy - 2), (cx + 2, cy - 2), 1)
    out.blit(body, (0, 0))
    return out


# ── PALETTE C — WITHERED BRUISE (alternate) ─────────────────────────────────

def _dim(rgb, k=0.85):
    return tuple(max(0, min(255, int(c * k))) for c in rgb)


P_BRUISE = _pal(
    tail=[(80, 50, 95), (110, 75, 105), (155, 145, 90), (190, 200, 100)],
    tail_line=(50, 28, 65),
    body_shadow=(55, 30, 75),
    body_main=(110, 90, 110),
    body_chest=_dim((150, 145, 105)),
    body_belly=_dim((180, 190, 110)),
    sheen=(200, 200, 140, 80),
    wing_main=(70, 45, 90),
    wing_dark=(35, 18, 55),
    wing_tip=(160, 170, 80),
    wing_secondary=(195, 200, 95),
    wing_highlight=(215, 220, 130),
    head_shadow=(60, 35, 80),
    head_main=(115, 95, 115),
    head_cheek=(150, 140, 105),
    head_crown=(175, 185, 110),
    lens_frame=(95, 60, 115),
    lens_body=(170, 180, 100),
    lens_tint=None,
    lens_glint=None,
    beak_main=(135, 120, 80),
    beak_dark=(60, 40, 30),
    beak_gloss=(190, 185, 120),
    foot=(50, 28, 65),
)


def build_bruise_dead(angle_deg, aura_scale=1.0):
    body = _build_parrot_with_palette(angle_deg, P_BRUISE)
    x_ink = (95, 60, 115)
    for cx, cy in (LENS_L, LENS_R):
        pygame.draw.line(body, x_ink, (cx - 3, cy - 3), (cx + 3, cy + 3), 1)
        pygame.draw.line(body, x_ink, (cx - 3, cy + 3), (cx + 3, cy - 3), 1)
    return body


# ── Registry ────────────────────────────────────────────────────────────────

PALETTE_KEYS = ("E", "B", "C")

PALETTE_LABELS = {
    "E": "NIGHT-VAPOR",
    "B": "CHARTREUSE ECTOPLASM",
    "C": "WITHERED BRUISE",
}

_BUILDERS = {
    "E": build_nightvapor_dead,
    "B": build_chartreuse_dead,
    "C": build_bruise_dead,
}


def build_dead_variant_frames(palette_key, aura_scale=1.0):
    """4 outlined dead-Pip frames (one per wing angle) for a given palette."""
    build_fn = _BUILDERS[palette_key]
    return [_add_outline(build_fn(a, aura_scale=aura_scale)) for a in _WING_ANGLES]
