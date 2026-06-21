"""MESSAGE BOTTLE parcel cosmetic (MID tier).

A corked bottle laid HORIZONTALLY with a rolled cream scroll inside —
adventure mail. The one wide-not-tall object in the PARCELS tab.

Carry-pose geometry is the whole game: the bottle is built with the CORK ON
THE LEFT (down-left tip) and baked with a steep ~63° lean so, slung below Pip,
the cork juts into OPEN SKY instead of vanishing into his belly. That broken
silhouette against the sky is what reads "bottle" rather than "orb". The
long lying-down axis is exaggerated (~17 wide × 9 tall) so it survives the
downscale instead of collapsing to a round lozenge. Built at 2× then
smoothscaled to 22 so the dark outline, the neck pinch and the cork seam hold
at the tiny in-play read and through the bird's tilt rotation.

The parcel sprite is centred on an anchor at Pip's belly-bottom, so a centred
bottle is ~70% eaten by his round body. After the lean the whole bottle is
translated toward the LOWER-LEFT of the canvas (CARRY_DX/DY) so the corked neck
and ~40% of the body clear his silhouette into open sky down-left — the cork
sits on sky, never on his red feathers. A 1px dark contact rim along the wall
that faces up toward Pip separates the held bottle from his chest at 22px."""
import math
import pygame

SIZE = 22
SS = 44  # 2× supersample; smoothscaled down for a crisp outline at 22px

# Baked lean — the bottle lies on a steep down-left diagonal so its long axis
# escapes Pip's round-body silhouette into the open sky off his lower-left flank
# (a purely-vertical bottle hides its belly under him; a flat one tucks fully
# beneath his width — the diagonal is the only pose that shows the long axis AND
# floats the cork in sky). Built lying flat (cork-left = horizontal); a POSITIVE
# screen rotation drops the cork end and lifts the belly, leaving the cork the
# lowest, leftmost point — the broken outline that converts "orb" → "bottle".
LEAN_DEG = 48

# Post-lean translation (SS / 2× pixels): the sprite is centred on an anchor at
# Pip's belly-bottom, so a centred bottle is ~70% eaten by his round body. Nudge
# the whole bottle toward the LOWER-LEFT so the corked neck + ~40% of the body
# clear his lower-left silhouette onto OPEN SKY — the cork lands on sky, not on
# his warm-red feathers. Kept small enough that the long axis never clips the
# canvas edge before the downscale.
CARRY_DX = -6   # left
CARRY_DY = 8    # down

# DAY palette — sea-glass green translucent glass over a lighter core, warm
# cork, cream scroll. Glass wall darkened vs round 1 so the glyph holds against
# the bright upper sky band. Night leans on the cream keyline + faint glow.
GLASS = (0x3E, 0x86, 0x6E)       # deeper sea-glass wall (was 5FA88C — melted on sky)
CORE = (0x86, 0xC4, 0xAA)        # lighter translucent core
SKY_TELL = (0xC9, 0xE8, 0xDC)    # near-sky value sliver low on the belly
GLASS_KEY = (0xE6, 0xFB, 0xF4)   # bright top-edge glass keyline (translucency tell)
CORK = (0xCF, 0x9A, 0x4E)        # warm cork nub, punchier hue
CORK_HI = (0xF0, 0xCE, 0x8E)
CORK_SEAM = (0x5A, 0x3E, 0x1E)   # dark seam ring at the cork→neck join
SCROLL = (0xF6, 0xEC, 0xCE)      # cream rolled paper — the high-value content
SCROLL_SH = (0xCE, 0xBD, 0x93)   # scroll roll shading for the coil read
OUTLINE = (0x10, 0x2A, 0x22)     # dark high-value edge to hold the silhouette


def _lerp(a, b, t):
    return (round(a[0] + (b[0] - a[0]) * t),
            round(a[1] + (b[1] - a[1]) * t),
            round(a[2] + (b[2] - a[2]) * t))


def build(mode="normal"):  # mode ignored — parcel is mode-agnostic, one surface
    s = pygame.Surface((SS, SS), pygame.SRCALPHA)
    cy = SS // 2

    # ---- Silhouette as one closed polygon, built CORK→BELLY (left→right) so
    # the cork tip is the leftmost point. Proportions exaggerated horizontal:
    # the belly is wide and only moderately tall (the lying-down vessel axis).
    cork_l = 3           # cork tip (leftmost — juts into open sky once leaned)
    neck_l = 8           # cork meets the neck
    neck_r = 13          # neck meets the shoulder
    belly_l = 16         # shoulder pinch into the round belly
    belly_r = 41         # rounded belly end (rightmost)
    belly_hh = 9         # belly half-height — wide-not-tall (~17×9 at carry)
    neck_hh = 5          # BEEFED-UP neck half-height so it survives 22px
    cork_hh = 6          # cork slightly proud of the neck

    # Glass body outline silhouette — neck on the LEFT, big rounded belly right.
    glass_poly = [
        (neck_l, cy - neck_hh),
        (neck_r, cy - neck_hh),
        (belly_l, cy - belly_hh + 2),
        (belly_l + 6, cy - belly_hh),
        (belly_r - 7, cy - belly_hh),
        (belly_r - 2, cy - belly_hh + 3),
        (belly_r, cy),
        (belly_r - 2, cy + belly_hh - 3),
        (belly_r - 7, cy + belly_hh),
        (belly_l + 6, cy + belly_hh),
        (belly_l, cy + belly_hh - 2),
        (neck_r, cy + neck_hh),
        (neck_l, cy + neck_hh),
    ]

    # Dark outline pass — draw the silhouette fat first, fill sits inside it.
    pygame.draw.polygon(s, OUTLINE, glass_poly)
    # Round the belly cap so the right end never reads as a flat box.
    pygame.draw.circle(s, OUTLINE, (belly_r - belly_hh, cy), belly_hh)

    # ---- Glass fill — horizontal-banded core→wall so the round belly reads as
    # a cylinder lit down its spine. Masked into the silhouette.
    fill = pygame.Surface((SS, SS), pygame.SRCALPHA)
    pygame.draw.polygon(fill, (255, 255, 255, 255), glass_poly)
    pygame.draw.circle(fill, (255, 255, 255, 255),
                       (belly_r - belly_hh, cy), belly_hh)
    glass = pygame.Surface((SS, SS), pygame.SRCALPHA)
    for y in range(cy - belly_hh, cy + belly_hh + 1):
        t = (y - cy) / belly_hh              # -1 top, 0 spine, +1 bottom wall
        if t < 0:                            # upper wall — lit toward the core
            col = _lerp(CORE, GLASS, min(1.0, -t))
            a = 240
        else:                                # lower belly — let a sky-value
            col = _lerp(CORE, SKY_TELL, t)   # sliver glow through for the
            a = 210 if t > 0.55 else 240     # translucency tell at 22px
        glass.fill(col + (a,), pygame.Rect(0, y, SS, 1))
    glass.blit(fill, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    s.blit(glass, (0, 0))

    # ---- Rolled SCROLL inside the belly — the cream content that names this a
    # message bottle. A horizontal capsule with two coil end-caps. Cream is the
    # brightest value on the sprite so it carries the read day and night.
    sc_l, sc_r = belly_l + 4, belly_r - 5
    sc_hh = 5
    scroll_rect = pygame.Rect(sc_l, cy - sc_hh, sc_r - sc_l, sc_hh * 2)
    pygame.draw.rect(s, _lerp(SCROLL, SCROLL_SH, 0.3), scroll_rect,
                     border_radius=sc_hh)
    # Lit upper half of the parchment.
    pygame.draw.rect(s, SCROLL,
                     pygame.Rect(sc_l, cy - sc_hh, sc_r - sc_l, sc_hh),
                     border_radius=sc_hh)
    # Two rolled coils at the ends — concentric arcs sell "rolled paper".
    for ex in (sc_l + 2, sc_r - 2):
        pygame.draw.circle(s, SCROLL, (ex, cy), sc_hh)
        pygame.draw.circle(s, SCROLL_SH, (ex, cy), sc_hh, 1)
        pygame.draw.circle(s, _lerp(SCROLL_SH, OUTLINE, 0.4), (ex, cy), 2, 1)
    # A couple of writing ticks on the parchment face for "a message".
    pygame.draw.line(s, _lerp(SCROLL_SH, OUTLINE, 0.5),
                     (sc_l + 6, cy - 1), (sc_r - 6, cy - 1), 1)
    pygame.draw.line(s, _lerp(SCROLL_SH, OUTLINE, 0.5),
                     (sc_l + 6, cy + 2), (sc_r - 8, cy + 2), 1)

    # ---- CORK nub — warm plug capping the neck on the LEFT. Bigger + warmer
    # than round 1 with a dark seam so it stays a distinct cap, never smearing
    # into the neck. It's the iconic tell and the first thing to vanish.
    cork = pygame.Rect(cork_l, cy - cork_hh, neck_l - cork_l + 3, cork_hh * 2)
    pygame.draw.rect(s, OUTLINE, cork.inflate(2, 2), border_radius=3)
    pygame.draw.rect(s, CORK, cork, border_radius=3)
    pygame.draw.line(s, CORK_HI, (cork.x + 1, cork.y + 1),
                     (cork.right - 1, cork.y + 1), 2)
    # Dark seam ring where cork meets the glass lip — keeps the two separate.
    pygame.draw.line(s, CORK_SEAM, (neck_l + 1, cy - neck_hh - 1),
                     (neck_l + 1, cy + neck_hh + 1), 2)

    # ---- Glass KEYLINE — a bright translucency tell along the top edge of the
    # belly that survives the downscale (a thin specular rim, not a dab).
    pygame.draw.line(s, GLASS_KEY + (235,),
                     (belly_l + 4, cy - belly_hh + 2),
                     (belly_r - 6, cy - belly_hh + 2), 2)
    pygame.draw.line(s, (255, 255, 255, 170),
                     (belly_l + 5, cy - belly_hh + 1),
                     (belly_l + 11, cy - belly_hh + 1), 1)

    # ---- Contact rim — a 1px-at-22 (2px-at-SS) dark line along the wall that,
    # once leaned, faces UP toward Pip. It separates the held bottle from his
    # chest so the object reads as carried, not fused — and holds against both
    # the warm-red day body and the darker night body. The top wall + belly cap
    # are the edges that rotate up toward him under the steep lean.
    pygame.draw.line(s, OUTLINE, (neck_r, cy - neck_hh),
                     (belly_l + 6, cy - belly_hh), 2)
    pygame.draw.line(s, OUTLINE, (belly_l + 6, cy - belly_hh),
                     (belly_r - 7, cy - belly_hh), 2)
    pygame.draw.arc(s, OUTLINE,
                    pygame.Rect(belly_r - 2 * belly_hh, cy - belly_hh,
                                2 * belly_hh, 2 * belly_hh),
                    -math.pi / 2.2, math.pi / 2.2, 2)

    # ---- Bake the lean so the carried bottle lies on a steep diagonal with the
    # cork tip lowest, then nudge it toward the lower-left so the corked neck and
    # ~40% of the body clear Pip's silhouette into open sky below-left of him.
    # Composite on a roomy surface first so the diagonal long axis never clips,
    # then crop back to SS centred on the shifted bottle centre.
    leaned = pygame.transform.rotozoom(s, LEAN_DEG, 1.0)
    pad = SS // 2
    big = pygame.Surface((SS + 2 * pad, SS + 2 * pad), pygame.SRCALPHA)
    bc = (big.get_width() // 2 + CARRY_DX, big.get_height() // 2 + CARRY_DY)
    big.blit(leaned, leaned.get_rect(center=bc))
    out = big.subsurface(
        pygame.Rect(pad, pad, SS, SS)).copy()
    return pygame.transform.smoothscale(out, (SIZE, SIZE))
