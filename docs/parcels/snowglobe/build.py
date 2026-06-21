"""SNOWGLOBE parcel cosmetic (PREMIUM — legendary/secret tier).

A glass dome holding a tiny swirling cosmos on a short pedestal: a collectible
miniature universe. At 22px the read is an orb-on-a-pedestal — a glowing DOME
sitting on a stubby gold trapezoid BASE. That sphere-plus-foot silhouette is
radially clean, so it survives the bird's tilt rotation at every bank: the dome
dominates the shape and still reads as a globe even inverted.

Built at 2× (44px) then smoothscaled to 22 so the dark glass outline, the gold
base rim, and the inner star specks survive the tiny read. The NIGHT showpiece
is a BAKED INNER NEBULA — a soft violet→magenta radial gradient filling the dome
with 4-5 bright star dots placed INSIDE the glass (never on the rim, so rotation
can't break them). A single crescent rim highlight sells the curved glass.

Carry context: Pip's red body occludes the TOP of the dome, so the identity
lives in the LOWER/visible half — the glowing violet cosmos + the gold base read
cleanly against Pip's red. The deep-violet interior and warm gold base are both
far from red on the wheel, so the parcel never merges into him."""
import math
import pygame

SIZE = 22
SS = 44  # 2× supersample; smoothscaled down for a crisp glass edge at 22px

# DAY palette — pale glass dome over a deep-violet interior; warm gold base.
GLASS = (0xCF, 0xE3, 0xF2)        # pale cool glass tint
GLASS_HI = (0xEA, 0xF2, 0xFF)     # bright rim/crescent catch-light
INTERIOR = (0x3A, 0x2A, 0x6E)     # deep-violet contained cosmos (day read)
INTERIOR_HI = (0x5B, 0x46, 0x9E)  # lit upper interior
GOLD = (0xE8, 0xB2, 0x3C)         # gold pedestal
GOLD_HI = (0xFB, 0xDF, 0x8E)      # base top sheen
GOLD_D = (0xB0, 0x83, 0x22)       # base underside / rim shadow
STAR = (0xFF, 0xF4, 0xD0)         # warm star specks inside the glass
OUTLINE = (0x16, 0x10, 0x2E)      # dark high-value edge to hold the silhouette

# NIGHT baked nebula — violet core blooming to magenta; bright rim highlight.
NEB_CORE = (0x6A, 0x4F, 0xD0)     # violet heart of the contained cosmos
NEB_EDGE = (0xC7, 0x7F, 0xE8)     # magenta falloff toward the glass
RIM = (0xEA, 0xF2, 0xFF)          # cool glass rim highlight


def _lerp(a, b, t):
    return (round(a[0] + (b[0] - a[0]) * t),
            round(a[1] + (b[1] - a[1]) * t),
            round(a[2] + (b[2] - a[2]) * t))


def _halo(s, cx, cy, R):
    """Soft additive bloom around the dome so the contained cosmos emits light.
    Drawn UNDER the glass — a faint violet aura in daylight that BLOOMS against
    the night sky, the showpiece moment of this legendary parcel."""
    glow = pygame.Surface((R * 2, R * 2), pygame.SRCALPHA)
    for i in range(R, 0, -1):
        t = i / R                       # 1 at the rim, 0 at the core
        col = _lerp(NEB_CORE, NEB_EDGE, t)
        a = int(64 * (1.0 - t) ** 2) + 3
        pygame.draw.circle(glow, col + (a,), (R, R), i)
    s.blit(glow, (cx - R, cy - R), special_flags=pygame.BLEND_RGBA_ADD)


def build(mode="normal"):  # mode ignored — parcel is mode-agnostic, one surface
    s = pygame.Surface((SS, SS), pygame.SRCALPHA)
    cx = SS // 2

    # Layout (2× space): dome sphere riding a short gold pedestal. Centred a
    # touch high so the visible LOWER half — lower cosmos + gold base — carries
    # the read where Pip's body doesn't occlude it.
    orb_cy = 20
    orb_r = 13            # dome/sphere radius

    # ---- NIGHT HALO first, baked UNDER the dome so the cosmos looks luminous.
    _halo(s, cx, orb_cy, 20)

    # ---- GLASS DOME outline — a full sphere; the dark high-value edge holds the
    # orb silhouette against both skies and keeps the round read after rotation.
    pygame.draw.circle(s, OUTLINE, (cx, orb_cy), orb_r + 2)

    # ---- CONTAINED COSMOS — a soft radial nebula filling the sphere. Painted as
    # concentric rings (violet core → magenta toward the glass) so the interior
    # reads as a tiny swirling universe rather than a flat disc, clipped to the
    # orb by a circular mask so it stays inside the glass.
    cosmos = pygame.Surface((orb_r * 2, orb_r * 2), pygame.SRCALPHA)
    ccx = orb_r
    for i in range(orb_r, 0, -1):
        t = i / orb_r                   # 1 at glass wall, 0 at core
        # Bias the lit heart slightly UP so the lower glass reads a touch darker
        # (sphere shading) while the cosmos still glows from within.
        base = _lerp(NEB_CORE, NEB_EDGE, t)
        # Blend toward the day INTERIOR violet so it never looks washed out in
        # daylight, but keeps the baked nebula's bloom for the night read.
        col = _lerp(base, INTERIOR, 0.30 * t)
        pygame.draw.circle(cosmos, col + (255,), (ccx, ccx - 1), i)
    mask = pygame.Surface((orb_r * 2, orb_r * 2), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (ccx, ccx), orb_r)
    cosmos.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    s.blit(cosmos, (cx - orb_r, orb_cy - orb_r))

    # ---- A faint darker lower crescent inside the glass — bottom-of-sphere
    # shadow so the orb reads as a 3D ball, not a flat coin, after rotation.
    shade = pygame.Surface((orb_r * 2, orb_r * 2), pygame.SRCALPHA)
    pygame.draw.circle(shade, (*OUTLINE, 90), (orb_r, orb_r + 3), orb_r)
    shmask = pygame.Surface((orb_r * 2, orb_r * 2), pygame.SRCALPHA)
    pygame.draw.circle(shmask, (255, 255, 255, 255), (orb_r, orb_r), orb_r - 1)
    shade.blit(shmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    s.blit(shade, (cx - orb_r, orb_cy - orb_r))

    # ---- STAR DOTS — warm specks scattered INSIDE the cosmos (kept well within
    # the rim so rotation can never strand one on the glass edge). A bright core
    # dot + a faint twinkle ring makes them read as stars, not noise. Placed in
    # the central + lower zone so they survive Pip's top occlusion.
    stars = ((cx - 4, orb_cy - 2, 2), (cx + 5, orb_cy + 1, 1),
             (cx - 1, orb_cy + 5, 2), (cx + 2, orb_cy - 5, 1),
             (cx - 6, orb_cy + 4, 1))
    for sx, sy, rad in stars:
        if rad >= 2:
            pygame.draw.circle(s, (*STAR, 70), (sx, sy), rad + 2)
        pygame.draw.circle(s, STAR, (sx, sy), rad)

    # ---- CRESCENT RIM HIGHLIGHT — a thin bright arc on the upper-left glass.
    # This single curved catch-light is what sells "glass dome" over "ball".
    pygame.draw.arc(s, GLASS_HI,
                    pygame.Rect(cx - orb_r, orb_cy - orb_r,
                                orb_r * 2, orb_r * 2),
                    math.radians(70), math.radians(165), 2)
    # A cooler secondary glass tint just inside the rim, all the way round, so
    # the edge reads as transparent glass catching the sky.
    pygame.draw.circle(s, (*GLASS, 60), (cx, orb_cy), orb_r, 1)

    # ---- GOLD PEDESTAL — a short trapezoid foot. The high-contrast warm base is
    # the keyline that separates the globe from Pip's red and anchors the
    # orb-on-a-pedestal read. Drawn after the dome so it sits crisply below it.
    base_top_y = orb_cy + orb_r - 2
    top_hw = 9
    bot_hw = 12
    base_h = 6
    foot = [(cx - top_hw, base_top_y), (cx + top_hw, base_top_y),
            (cx + bot_hw, base_top_y + base_h),
            (cx - bot_hw, base_top_y + base_h)]
    out_foot = [(cx - top_hw - 2, base_top_y - 1),
                (cx + top_hw + 2, base_top_y - 1),
                (cx + bot_hw + 2, base_top_y + base_h + 2),
                (cx - bot_hw - 2, base_top_y + base_h + 2)]
    pygame.draw.polygon(s, OUTLINE, out_foot)
    # Vertical gold gradient on the trapezoid for a turned-wood/metal foot feel.
    for ry in range(base_h):
        t = ry / max(1, base_h - 1)
        col = _lerp(GOLD, GOLD_D, t)
        hw = top_hw + (bot_hw - top_hw) * (ry / base_h)
        y = base_top_y + ry
        pygame.draw.line(s, col, (cx - hw, y), (cx + hw, y), 1)
    # Top sheen + a small lip where the glass meets the base.
    pygame.draw.line(s, GOLD_HI, (cx - top_hw + 1, base_top_y),
                     (cx + top_hw - 1, base_top_y), 1)
    pygame.draw.line(s, GOLD_D, (cx - bot_hw + 1, base_top_y + base_h - 1),
                     (cx + bot_hw - 1, base_top_y + base_h - 1), 1)

    return pygame.transform.smoothscale(s, (SIZE, SIZE))
