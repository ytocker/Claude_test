"""PAPER PLANE — LOW-tier parcel cosmetic (ENVELOPE redesign, design 5).

The one concept that breaks the rectangular envelope silhouette: a letter
folded mid-flight into an origami dart. The identity is the folded triangular
paper body + the sharp crease lines (spine + wing fold), so those are drawn
boldest. Tucked under Pip at true size the pale wedge needs a colour hook that
lives ON the body, so the sky-blue accent is baked into the keel spine + nose
band rather than spent on a trail the rotozoom eats; the lower wing is dropped
into a darker, cooler fold-shadow so the V-fold survives the downscale, and a
contact drop-shadow separates the dart from Pip's red belly and the night sky.
Because the parcel rotates with Pip's bank (-25°..90°), the dart is kept
compact and centred so it reads as a creased paper wedge at every angle.
"""
import pygame

from game.draw import lerp_color as _lerp_color

PAPER = (237, 237, 230)        # ~#EDEDE6 paper-white
PAPER_HI = (250, 250, 246)     # lit upper wing
FOLD_SHADE = (154, 166, 186)   # ~#9AA6BA cool fold-shadow (lower wing), deeper
CREASE = (136, 147, 164)       # ~#8893A4 crease lines
SKY_ACCENT = (74, 144, 217)    # ~#4A90D9 sky-blue body accent (keel + nose)
SKY_ACCENT_HI = (126, 184, 240)  # lit lip of the keel spine
OUTLINE = (46, 52, 62)         # ~#2E343E dark, reads on bright day sky
KEYLINE = (224, 230, 240)      # cool-white rim — the NIGHT lifeline


def build(mode="normal") -> pygame.Surface:
    # Mode-agnostic: one static dart sprite for every Pip skin.
    S = 44
    surf = pygame.Surface((S, S), pygame.SRCALPHA)
    cx, cy = S // 2, S // 2

    # Dart geometry. Nose points right; the body is the classic two-wing paper
    # dart split by a central spine, the lower wing dropped a touch so the V of
    # the two wings reads as folded paper rather than a flat triangle. Kept well
    # inside the 44px field so the rotozoom never clips the nose/tail corners.
    nose = (cx + 15, cy)               # sharp tip
    tail_top = (cx - 14, cy - 11)      # upper trailing corner
    tail_bot = (cx - 14, cy + 12)      # lower trailing corner
    spine_tail = (cx - 11, cy + 2)     # where the keel meets the tail (notch)

    upper = [nose, tail_top, spine_tail]   # top wing (catches light)
    lower = [nose, spine_tail, tail_bot]   # bottom wing (in fold shadow)

    # --- Contact drop-shadow (drawn first, under everything) -----------------
    # A dark, low-alpha copy of the hull offset +1y so the dart separates from
    # Pip's body when carried below him — the cheapest fix for the night melt.
    hull = [nose, tail_top, tail_bot]
    shadow = _inflate_poly(hull, (cx, cy), 1.4)
    pygame.draw.polygon(surf, (10, 12, 18, 120),
                        [(x, y + 2) for x, y in shadow])

    # --- Baked outline (slightly inflated) ----------------------------------
    # The dark silhouette that survives on the (170,220,245) day sky. The lower
    # / tail edge is anchored heavier (~3px) where it meets Pip's red belly and
    # the night sky; the top lead edge stays a crisp 2px.
    out_hull = _inflate_poly(hull, (cx, cy), 2.2)
    pygame.draw.polygon(surf, OUTLINE, out_hull)
    pygame.draw.line(surf, OUTLINE, _ext(nose, spine_tail, 2), spine_tail, 4)
    # Heavy dark anchor along the lower + tail edges.
    o_nose = _inflate_poly([nose], (cx, cy), 2.2)[0]
    o_bot = _inflate_poly([tail_bot], (cx, cy), 2.2)[0]
    o_top = _inflate_poly([tail_top], (cx, cy), 2.2)[0]
    pygame.draw.line(surf, OUTLINE, o_nose, o_bot, 3)      # lower edge, heavy
    pygame.draw.line(surf, OUTLINE, o_bot, o_top, 3)       # tail edge, heavy
    pygame.draw.line(surf, OUTLINE, o_top, o_nose, 2)      # top lead edge, crisp

    # --- Lower wing: deeper cool fold-shadow gradient ------------------------
    # The far wing sits in shade — a vertical cool gradient pushed darker so the
    # crease/fold split survives the downscale instead of flattening to white.
    _grad_poly(surf, lower, FOLD_SHADE, _lerp_color(FOLD_SHADE, OUTLINE, 0.30),
               (cx, cy))

    # --- Upper wing: lit paper-white gradient -------------------------------
    _grad_poly(surf, upper, PAPER_HI, PAPER, (cx, cy))

    # --- Sky-blue keel spine: the colour hook + the crease identity ----------
    # The central fold is stroked in SKY_ACCENT (not grey) so the paper-plane
    # blue lives ON the body and survives true size; a lit lip alongside reads
    # the keel as a pinched edge, and a short blue nose-band points the dart.
    pygame.draw.line(surf, SKY_ACCENT, nose, spine_tail, 2)      # blue keel/spine
    pygame.draw.line(surf, SKY_ACCENT_HI, _off(nose, 0, -1),
                     _off(spine_tail, 0, -1), 1)                 # keel hi-lip
    pygame.draw.line(surf, CREASE, nose, tail_top, 1)           # upper wing fold

    # Blue nose-band: a 2px wedge across the tip so the dart keeps its point and
    # its direction read at shallow bank angles where the white nose vanishes.
    band_a = _lerp(nose, tail_top, 0.18)
    band_b = _lerp(nose, spine_tail, 0.18)
    pygame.draw.line(surf, SKY_ACCENT, band_a, band_b, 2)

    # --- Cool keyline rim INSIDE the outline --------------------------------
    # Traces the lit leading edge so the dart glows on night sky without a
    # per-mode sprite. Only the top edge + spine catch it (where light lands).
    pygame.draw.line(surf, KEYLINE, nose, tail_top, 1)
    pygame.draw.line(surf, KEYLINE, _off(nose, -1, 1), _off(spine_tail, 0, 1), 1)

    return pygame.transform.smoothscale(surf, (22, 22))


# --- helpers ----------------------------------------------------------------

def _off(p, dx, dy):
    return (p[0] + dx, p[1] + dy)


def _lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def _ext(a, b, d):
    # Point d px beyond `a` along the a->b direction (extends the outline keel
    # under the spine so the notch corner stays capped).
    import math
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    return (a[0] - math.cos(ang) * d, a[1] - math.sin(ang) * d)


def _inflate_poly(pts, c, d):
    # Push each vertex `d` px away from the centroid c — a cheap outline-frame
    # that keeps the dart's sharp corners instead of rounding them.
    import math
    out = []
    for x, y in pts:
        vx, vy = x - c[0], y - c[1]
        m = math.hypot(vx, vy) or 1.0
        out.append((x + vx / m * d, y + vy / m * d))
    return out


def _grad_poly(surf, pts, top_col, bot_col, c):
    # Fill a polygon with a vertical gradient by masking a gradient strip to the
    # poly — gives the wings paper shading without per-pixel poly math.
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0, y0 = int(min(xs)), int(min(ys))
    w = int(max(xs)) - x0 + 1
    h = int(max(ys)) - y0 + 1
    if w <= 0 or h <= 0:
        return
    strip = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        t = y / max(1, h - 1)
        strip.fill(_lerp_color(top_col, bot_col, t) + (255,),
                   pygame.Rect(0, y, w, 1))
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255),
                        [(p[0] - x0, p[1] - y0) for p in pts])
    strip.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(strip, (x0, y0))
