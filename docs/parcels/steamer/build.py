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
BAMBOO = (0xD8, 0xB8, 0x77)
BAND_SH = (0xA0, 0x7C, 0x3C)
SEAM = (0x6A, 0x4C, 0x20)     # dark seam between tiers — the "stacked" cue
LID_RIM = (0x7A, 0x5A, 0x28)
HILITE = (0xEF, 0xDF, 0xB4)   # top sheen on each tier + the dome
STEAM = (0xFB, 0xF6, 0xEA)    # near-white opaque steam puff
STEAM_GLOW = (0xF0, 0xE4, 0xC8)  # warm halo so the puff blooms at night
OUTLINE = (0x2C, 0x1C, 0x0E)  # dark high-value edge to hold the silhouette


def _lerp(a, b, t):
    return (round(a[0] + (b[0] - a[0]) * t),
            round(a[1] + (b[1] - a[1]) * t),
            round(a[2] + (b[2] - a[2]) * t))


def _tier(s, cx, cy, half_w, h):
    """One shallow woven bamboo tier centred at (cx, cy): dark keyline frame, a
    top-lit weave gradient masked into a soft rounded body, a top sheen line and
    a dark SEAM at its base so a column of these reads as a stacked tower."""
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
    # Dark band SEAM at the base — the horizontal stripe between tiers.
    pygame.draw.line(s, SEAM, (rect.x + 1, rect.bottom - 1),
                     (rect.right - 2, rect.bottom - 1), 2)
    return rect


def build(mode="normal"):  # mode ignored — parcel is mode-agnostic, one surface
    s = pygame.Surface((SS, SS), pygame.SRCALPHA)
    cx = SS // 2

    # --- Steam first so the tower bakes over its base: a compact OPAQUE puff
    # above the lid with a soft warm halo, so it reads as steam on day AND night
    # and stays a short bloom (not a tail) when the sprite banks.
    steam_y = 5
    halo = pygame.Surface((16, 14), pygame.SRCALPHA)
    pygame.draw.circle(halo, STEAM_GLOW + (90,), (8, 7), 7)
    pygame.draw.circle(halo, STEAM_GLOW + (60,), (8, 7), 5)
    s.blit(halo, (cx - 8, steam_y - 4))
    # Two overlapping opaque blobs — a small billow, clearly above the lid.
    pygame.draw.circle(s, STEAM, (cx - 1, steam_y + 2), 3)
    pygame.draw.circle(s, STEAM, (cx + 2, steam_y), 2)
    pygame.draw.circle(s, HILITE, (cx - 2, steam_y + 1), 1)

    # --- Three stacked tiers that STEP inward going up. Heights biased into the
    # STACK (not the lid); each upper tier is ~2px narrower per side so the
    # silhouette tapers in and never reads as one straight tub.
    base_cy = 36
    tier_h = 7
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
    # Dark seam where the lid lip meets the top tier — the overhang shadow.
    pygame.draw.line(s, SEAM, (rim.x + 1, rim.bottom - 1),
                     (rim.right - 2, rim.bottom - 1), 1)

    # Shallow dome cap sitting on the rim; offset its centre slightly so the
    # sheen + overhang stay asymmetric and the lid never mirrors into a slab.
    dome_w = lid_hw * 2 - 4
    dome_h = 9
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

    return pygame.transform.smoothscale(s, (SIZE, SIZE))
