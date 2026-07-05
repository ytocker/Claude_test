"""BAMBOO STEAMER parcel cosmetic (MID tier).

ONE closed dim-sum steamer: three shallow woven bamboo tiers that STEP inward
going up, capped by a separate domed lid whose overhang lip is ASYMMETRIC, with
a compact opaque steam puff above. This is a TALL, narrow stacked tower (~2:3
width:height) — the stack carries the height, the lid is a thin crown — so the
silhouette steps inward and reads as a stacked steamer, never a squat
bucket/barrel. There is no handle and no cloth; it is a closed stack.

Built at 2× then smoothscaled to 22 so the dark keyline, the dark tier SEAMS,
and the lid overhang survive the tiny in-play read and the bird's tilt rotation.
The steam is a small OPAQUE warm-white puff centred above the lid (with a soft
glow halo) so it reads as steam even on the bright day sky and doesn't smear
into a tail when the sprite banks."""
import pygame

SIZE = 22
SS = 44  # 2× supersample; smoothscaled down for a crisp outline at 22px

# DAY palette — pale woven bamboo, darker band shadows, deep rim under the lid.
# Lit faces are pushed ~10% brighter than R2 so the stepped form stays legible
# when the parcel is carried past a dark night pillar.
BAMBOO = (0xE3, 0xC4, 0x84)
BAND_SH = (0xA8, 0x84, 0x42)
SEAM = (0x6A, 0x4C, 0x20)     # dark seam between tiers — the "stacked" cue
SEAM_TOP = (0x4A, 0x32, 0x14)  # deepest seam at the lid/body break only
LID_RIM = (0x7A, 0x5A, 0x28)
HILITE = (0xF6, 0xE8, 0xBE)   # top sheen on each tier + the dome
# Steam is COOL bluish-white so it separates in value AND hue from the warm tan
# tiers — it pops on the day sky and the dark night pillar alike.
STEAM = (0xF4, 0xF9, 0xFF)    # near-white, faintly blue, opaque steam puff
STEAM_CORE = (0xFF, 0xFF, 0xFF)  # hottest highlight on the lobed crown
STEAM_SH = (0xC4, 0xD6, 0xE6)    # cool underside so the puff has volume
STEAM_RIM = (0x32, 0x3C, 0x4E)   # dark micro-halo so the puff survives on light bg
OUTLINE = (0x2C, 0x1C, 0x0E)  # dark high-value edge to hold the silhouette


def _lerp(a, b, t):
    return (round(a[0] + (b[0] - a[0]) * t),
            round(a[1] + (b[1] - a[1]) * t),
            round(a[2] + (b[2] - a[2]) * t))


def _tier(s, cx, cy, half_w, h, soft_seam=True):
    """One shallow woven bamboo tier centred at (cx, cy): dark keyline frame, a
    top-lit weave gradient masked into a soft rounded body, a top sheen line and
    a SEAM at its base so a column of these reads as a stacked tower. The two
    lower seams are kept SUBTLE (1px band-shadow) so three equal dark lines don't
    turn to noise at 1×; only the lid/body break is deepened (drawn by caller)."""
    rect = pygame.Rect(cx - half_w, cy - h // 2, half_w * 2, h)
    # Dark keyline frame baked behind the fill so the edge stays bold at 22px.
    pygame.draw.rect(s, OUTLINE, rect.inflate(3, 3), border_radius=4)

    fill = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    for y in range(rect.h):
        t = y / max(1, rect.h - 1)
        # Light at the top of the tier, sinking to band shadow at its base —
        # the woven-ring shading that makes the stack read as separate drums.
        fill.fill(_lerp(BAMBOO, BAND_SH, t * 0.85) + (255,),
                  pygame.Rect(0, y, rect.w, 1))
    mask = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=3)
    fill.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    s.blit(fill, rect.topleft)

    # Top weave-sheen so each tier catches light along its rim.
    pygame.draw.line(s, HILITE, (rect.x + 3, rect.y + 1),
                     (rect.right - 4, rect.y + 1), 1)
    # Lower tier seams stay a single quiet band-shadow line so the steps read as
    # subtle ledges rather than three competing dark stripes.
    if soft_seam:
        pygame.draw.line(s, BAND_SH, (rect.x + 2, rect.bottom - 1),
                         (rect.right - 3, rect.bottom - 1), 1)
    return rect


def _steam(s, cx, top_y, lid_w):
    """One BOLD lobed steam puff pinned above the lid, baked into the same
    surface as the tower so it travels with the lid through rotation. It is sized
    ~1.3× the lid width with a CLEAR gap above the dome, drawn in a COOL bluish
    white so it separates from the warm tan tiers in both hue and value, and
    wrapped in a 1px dark micro-halo so its silhouette survives on light AND dark
    skies (the grayscale read leans on this rim, not on hue)."""
    pw = max(12, round(lid_w * 1.32))    # puff ~1.3× the lid width — bold, not wispy
    ph = round(pw * 0.58)                 # a wide low billow, sized to fit the headroom
    # Float the puff a clear gap above the dome crown; clamp so the bold puff
    # always fits inside the sprite surface even after the gap is reserved.
    gap = 2
    py = max(1, top_y - gap - ph)
    cy = py + ph // 2
    # Lobed cloud profile: a wide low belly plus two stacked crown bumps, sized
    # relative to the puff so it stays one readable billow rather than fine wisps.
    r0 = ph * 0.40
    lobes = (
        (cx,                  cy + ph * 0.14, r0 * 1.18),   # broad belly
        (cx - pw * 0.26,      cy - ph * 0.02, r0 * 0.92),   # left shoulder
        (cx + pw * 0.27,      cy + ph * 0.02, r0 * 0.96),   # right shoulder
        (cx - pw * 0.05,      cy - ph * 0.26, r0 * 0.86),   # crown bump
    )
    # Dark micro-halo first — slightly inflated lobes so a thin rim of it peeks
    # out under the bright fill on every side, holding the shape on light bg.
    for lx, ly, lr in lobes:
        pygame.draw.circle(s, STEAM_RIM, (round(lx), round(ly)), round(lr + 1.4))
    # Cool shaded body so the puff has volume against the sky.
    for lx, ly, lr in lobes:
        pygame.draw.circle(s, STEAM_SH, (round(lx), round(ly)), round(lr))
    # Bright lit fill, nudged up-left toward the light so a cool shadow crescent
    # stays along the lower-right edge — gives the billow real form, not a disc.
    for lx, ly, lr in lobes:
        pygame.draw.circle(s, STEAM, (round(lx - 0.8), round(ly - 1.0)),
                           round(lr * 0.86))
    # Hot core highlight on the crown.
    pygame.draw.circle(s, STEAM_CORE, (round(cx - pw * 0.06), round(cy - ph * 0.24)),
                       max(2, round(r0 * 0.5)))


def build(mode="normal"):  # mode ignored — parcel is mode-agnostic, one surface
    s = pygame.Surface((SS, SS), pygame.SRCALPHA)
    cx = SS // 2

    # --- Three stacked tiers that STEP inward going up. Heights biased into the
    # STACK (not the lid); each upper tier is ~2px narrower per side so the
    # silhouette tapers in and never reads as one straight tub.
    base_cy = 39   # sit the stack low so there is headroom for a bold steam puff
    tier_h = 6
    bottom_hw = 12   # widest tier half-width
    tiers = []
    for i in range(3):
        cy = base_cy - i * (tier_h - 1)   # 1px overlap so seams sit tight
        hw = bottom_hw - i * 2            # step inward going up
        tiers.append((cy, hw))
    # Draw bottom-up so each tier's keyline overlaps the one below cleanly.
    top_cy, top_hw = None, None
    for cy, hw in tiers:
        r = _tier(s, cx, cy, hw, tier_h)
        top_cy, top_hw = r.y, hw

    # --- Domed LID — a thin rim band + a shallow cap, its own crown over the
    # top tier with an ASYMMETRIC overhang lip so the 90° bank never flattens it
    # into a symmetric crate slab.
    lid_hw = top_hw + 2              # overhang past the top tier
    rim_y = top_cy - 1
    rim_h = 4
    rim = pygame.Rect(cx - lid_hw, rim_y - rim_h, lid_hw * 2, rim_h)
    # Nudge the rim left so the overhang reads asymmetric, not a centred slab.
    rim.x -= 1
    pygame.draw.rect(s, OUTLINE, rim.inflate(3, 3), border_radius=3)
    rimfill = pygame.Surface((rim.w, rim.h), pygame.SRCALPHA)
    for y in range(rim.h):
        rimfill.fill(_lerp(BAMBOO, LID_RIM, y / max(1, rim.h - 1)) + (255,),
                     pygame.Rect(0, y, rim.w, 1))
    s.blit(rimfill, rim.topleft)
    # DEEPEST seam of the whole prop where the lid lip meets the body — this is
    # the one break that has to read at 1×, so it is darker and 2px proud while
    # the inter-tier steps stay subtle.
    pygame.draw.line(s, SEAM_TOP, (rim.x + 1, rim.bottom - 1),
                     (rim.right - 2, rim.bottom - 1), 2)

    # Shallow dome cap sitting on the rim; offset its centre slightly so the
    # sheen + overhang stay asymmetric and the lid never mirrors into a slab.
    dome_w = lid_hw * 2 - 4
    dome_h = 8
    dome = pygame.Rect(rim.x + 1, rim.y - dome_h + 2, dome_w, dome_h)
    pygame.draw.ellipse(s, OUTLINE, dome.inflate(2, 2))
    capmask = pygame.Surface((dome.w, dome.h), pygame.SRCALPHA)
    pygame.draw.ellipse(capmask, (255, 255, 255, 255), capmask.get_rect())
    cap = pygame.Surface((dome.w, dome.h), pygame.SRCALPHA)
    for y in range(dome.h):
        cap.fill(_lerp(HILITE, BAND_SH, y / max(1, dome.h - 1)) + (255,),
                 pygame.Rect(0, y, dome.w, 1))
    cap.blit(capmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    s.blit(cap, dome.topleft)
    # Dome sheen + a tiny centre knob so the lid reads as a lid, not a tier.
    pygame.draw.arc(s, HILITE, dome.inflate(-3, -2), 0.6, 2.5, 2)
    knob = (dome.centerx, dome.y + 2)
    pygame.draw.circle(s, LID_RIM, knob, 2)
    pygame.draw.circle(s, OUTLINE, knob, 2, 1)

    # --- Steam LAST, pinned to the dome crown with a clear gap, baked into the
    # same surface so it rotates as one with the lid and never detaches on tilt.
    _steam(s, dome.centerx, dome.y, lid_hw * 2)

    return pygame.transform.smoothscale(s, (SIZE, SIZE))
