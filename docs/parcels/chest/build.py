"""TREASURE CHEST parcel cosmetic (HIGH tier).

A gold-banded pirate chest: a wood trunk with a DOMED lid, thick metal corner
BANDS and a centre LOCK plate, with a glint of coins peeking under the lid. The
arched-lid + band-cross + lock is the glyph that carries the "loot" read at
22px — a silhouette no low/mid box shares.

Built at 2× (44px) then smoothscaled to 22 so the dark outline, the gold band
edges and the lock survive the tiny read AND the bird's tilt rotation. The
identity (gold bands + lock + coin glint) is packed into the LOWER/visible half
because Pip and his red body occlude the parcel's top in carry; nothing up top
relies on pure red, which would melt into Pip."""
import pygame

SIZE = 22
SS = 44  # 2× supersample; smoothscaled down for a crisp outline at 22px

# DAY palette — warm wood trunk, bright gold bands/lock, pale gold sheen + coins.
WOOD = (0x7A, 0x4A, 0x22)
WOOD_SH = (0x52, 0x30, 0x14)   # trunk-bottom shade for a rounded body
WOOD_HI = (0xA0, 0x6C, 0x3A)   # lit upper face of the lid dome
GOLD = (0xE8, 0xB2, 0x3C)      # bands + lock plate — the value colour
GOLD_HI = (0xFB, 0xE0, 0x8A)   # band highlight; lifts gold off the wood by day
GOLD_SH = (0xA8, 0x7A, 0x1E)   # band shadow seam so bands read as raised metal
COIN = (0xFF, 0xE9, 0xA0)      # coin-glint dots under the lid
LOCK_GLOW = (0xFF, 0xD6, 0x59) # subtle self-pop on the lock (reads warm at night)
OUTLINE = (0x24, 0x12, 0x08)   # dark high-value edge to hold the silhouette


def _lerp(a, b, t):
    return (round(a[0] + (b[0] - a[0]) * t),
            round(a[1] + (b[1] - a[1]) * t),
            round(a[2] + (b[2] - a[2]) * t))


def _vgrad_rounded(w, h, top, bot, radius):
    """A vertical-gradient fill clipped to a rounded rect — the rounded trunk
    body and the lid dome both lean on this so they read as volume, not flats."""
    fill = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        fill.fill(_lerp(top, bot, y / max(1, h - 1)) + (255,),
                  pygame.Rect(0, y, w, 1))
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(),
                     border_radius=radius)
    fill.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return fill


def build(mode="normal"):  # mode ignored — parcel is mode-agnostic, one surface
    s = pygame.Surface((SS, SS), pygame.SRCALPHA)
    cx = SS // 2

    BODY_W = 34
    bx = cx - BODY_W // 2

    # ── Drop shadow grounds the chest under Pip ──────────────────────────────
    sh = pygame.Surface((BODY_W + 6, 8), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (8, 4, 14, 120), sh.get_rect())
    s.blit(sh, (cx - (BODY_W + 6) // 2, 38))

    # ── Trunk body (lower, visible half) ─────────────────────────────────────
    # The carried parcel shows its bottom most, so the trunk + bands + lock all
    # sit here. Outline frame first, then the rounded wood gradient.
    body = pygame.Rect(bx, 22, BODY_W, 16)
    pygame.draw.rect(s, OUTLINE, body.inflate(4, 4), border_radius=5)
    s.blit(_vgrad_rounded(body.w, body.h, WOOD, WOOD_SH, 4), body.topleft)

    # ── Domed lid (upper, partly occluded in carry) ──────────────────────────
    # A wide arch sitting on the trunk. Its top is what Pip overlaps, so the
    # dome stays plain wood — the gold lives on the bands/lock below it.
    lid = pygame.Rect(bx - 1, 10, BODY_W + 2, 18)
    pygame.draw.ellipse(s, OUTLINE, lid.inflate(4, 4))
    dome_mask = pygame.Surface((lid.w, lid.h), pygame.SRCALPHA)
    pygame.draw.ellipse(dome_mask, (255, 255, 255, 255), dome_mask.get_rect())
    dome = pygame.Surface((lid.w, lid.h), pygame.SRCALPHA)
    for y in range(lid.h):
        dome.fill(_lerp(WOOD_HI, WOOD, y / max(1, lid.h - 1)) + (255,),
                  pygame.Rect(0, y, lid.w, 1))
    dome.blit(dome_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    s.blit(dome, lid.topleft)
    # Clip the dome's bottom half off so it reads as a domed lid, not a ball —
    # paint the trunk's top seam back over the lower arc.
    pygame.draw.rect(s, OUTLINE, (bx - 2, 24, BODY_W + 4, 2))

    # ── Lid band (the horizontal gold strap across the dome's base) ──────────
    lidband = pygame.Rect(bx - 1, 21, BODY_W + 2, 5)
    pygame.draw.rect(s, OUTLINE, lidband.inflate(2, 2), border_radius=2)
    s.blit(_vgrad_rounded(lidband.w, lidband.h, GOLD_HI, GOLD, 2),
           lidband.topleft)
    pygame.draw.line(s, GOLD_SH, (lidband.x + 1, lidband.bottom - 1),
                     (lidband.right - 2, lidband.bottom - 1), 1)

    # ── Coin glints peeking from under the lid seam ──────────────────────────
    # Drawn just below the lid band so they read as loot inside, above the lock.
    for dx, r in ((-9, 2), (8, 2), (-2, 1)):
        pygame.draw.circle(s, OUTLINE, (cx + dx, 28), r + 1)
        pygame.draw.circle(s, COIN, (cx + dx, 28), r)
        pygame.draw.circle(s, (255, 255, 255), (cx + dx - 1, 27), 1)

    # ── Two thick vertical corner bands ──────────────────────────────────────
    # Only two (plus the one horizontal lid band) — three+ verticals mush at
    # 22px. Each is a gold strip with a highlight edge and a shadow seam so it
    # reads as raised metal banding, not a painted stripe.
    for vx in (bx + 4, body.right - 8):
        band = pygame.Rect(vx, 20, 4, body.bottom - 20 + 1)
        pygame.draw.rect(s, OUTLINE, band.inflate(2, 0))
        pygame.draw.rect(s, GOLD, band)
        pygame.draw.line(s, GOLD_HI, (band.x, band.y),
                         (band.x, band.bottom - 1), 1)
        pygame.draw.line(s, GOLD_SH, (band.right - 1, band.y),
                         (band.right - 1, band.bottom - 1), 1)

    # ── Centre LOCK plate ────────────────────────────────────────────────────
    # The single brightest element, dead-centre on the trunk front — the cue
    # that turns "banded box" into "treasure chest". A rounded gold plate with
    # a dark keyhole and a self-glow so it pops by day and at night.
    lock = pygame.Rect(0, 0, 9, 11)
    lock.center = (cx, 32)
    pygame.draw.rect(s, OUTLINE, lock.inflate(3, 3), border_radius=3)
    pygame.draw.rect(s, LOCK_GLOW, lock.inflate(1, 1), border_radius=3)
    s.blit(_vgrad_rounded(lock.w, lock.h, GOLD_HI, GOLD, 3), lock.topleft)
    # Keyhole: dark circle + slot, reads as a lock even when banked.
    pygame.draw.circle(s, OUTLINE, (cx, lock.y + 4), 2)
    pygame.draw.rect(s, OUTLINE, (cx - 1, lock.y + 4, 2, 4))

    return pygame.transform.smoothscale(s, (SIZE, SIZE))
