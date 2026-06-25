"""PAPER PLANE — LOW-tier parcel cosmetic (ENVELOPE redesign, design 5).

The one concept that breaks the rectangular envelope silhouette: a letter
folded mid-flight into an origami dart. The identity is the folded triangular
paper body + the sharp crease lines (spine + wing fold), so those are drawn
boldest; a cool-blue under-shadow gives the paper real fold depth, and a small
dashed flight-path arc trails behind so it reads as "mail IN MOTION", not a
static plane. Because the parcel rotates with Pip's bank (-25°..90°), the dart
is kept compact and centred so it still reads as a creased paper wedge at every
angle — not just nose-up — and never clips under the gameplay rotozoom.
"""
import pygame

from game.draw import lerp_color as _lerp_color

PAPER = (237, 237, 230)        # ~#EDEDE6 paper-white
PAPER_HI = (250, 250, 246)     # lit upper wing
FOLD_SHADE = (194, 203, 216)   # ~#B4BDCB cool fold-shadow (lower wing), lifted
CREASE = (136, 147, 164)       # ~#8893A4 crease lines
SKY_ACCENT = (74, 144, 217)    # ~#4A90D9 dashed flight-path arc
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

    # --- Baked outline (drawn first, slightly inflated) ---------------------
    # The dark silhouette that survives on the (170,220,245) day sky. Inflating
    # the whole dart hull keeps a clean 2px frame around every fold edge.
    hull = [nose, tail_top, tail_bot]
    out_hull = _inflate_poly(hull, (cx, cy), 2.2)
    pygame.draw.polygon(surf, OUTLINE, out_hull)
    pygame.draw.line(surf, OUTLINE, _ext(nose, spine_tail, 2), spine_tail, 4)

    # --- Flight-path arc (drawn BEHIND the dart so it trails the tail) -------
    # A dashed sky-blue arc sweeping up into the tail = mail in motion. Each dash
    # gets a dark halo so the trail survives on bright day AND dark night sky;
    # dashes grow toward the dart so it reads as accelerating, not a static line.
    _dashed_arc(surf, (cx - 21, cy + 8), (cx - 12, cy + 3), SKY_ACCENT, OUTLINE)

    # --- Lower wing: cool fold-shadow gradient ------------------------------
    # The far wing sits in shade — a vertical paper-white->cool gradient sells
    # the crease as a real fold, not a printed line.
    _grad_poly(surf, lower, FOLD_SHADE, _lerp_color(FOLD_SHADE, OUTLINE, 0.25),
               (cx, cy))

    # --- Upper wing: lit paper-white gradient -------------------------------
    _grad_poly(surf, upper, PAPER_HI, PAPER, (cx, cy))

    # --- Crease lines: the identity -----------------------------------------
    # Spine (nose->tail notch) is the central keel fold; the wing crease runs
    # nose->upper-tail to split the top wing. Drawn dark + a thin highlight
    # alongside so each fold reads as a crisp pinched edge even at true size.
    pygame.draw.line(surf, CREASE, nose, spine_tail, 2)          # keel/spine
    pygame.draw.line(surf, PAPER_HI, _off(nose, 0, -1),
                     _off(spine_tail, 0, -1), 1)                 # spine hi-lip
    pygame.draw.line(surf, CREASE, nose, tail_top, 1)            # upper wing fold

    # --- Cool keyline rim INSIDE the outline --------------------------------
    # Traces the lit leading edge so the dart glows on night sky without a
    # per-mode sprite. Only the top edge + spine catch it (where light lands).
    pygame.draw.line(surf, KEYLINE, nose, tail_top, 1)
    pygame.draw.line(surf, KEYLINE, _off(nose, -1, 1), _off(spine_tail, 0, 1), 1)

    return pygame.transform.smoothscale(surf, (22, 22))


# --- helpers ----------------------------------------------------------------

def _off(p, dx, dy):
    return (p[0] + dx, p[1] + dy)


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


def _dashed_arc(surf, a, b, col, halo):
    # Dashes stepping from `a` toward `b` with an upward bow — a motion trail,
    # not a solid line. Each dash gets a dark halo first so the cool-blue trail
    # holds contrast on both skies; dashes grow toward the dart (accelerating).
    import math
    n = 4
    pts = []
    for i in range(n):
        t = i / (n - 1)
        bow = -3.5 * math.sin(t * math.pi)   # gentle upward arc
        x = a[0] + (b[0] - a[0]) * t
        y = a[1] + (b[1] - a[1]) * t + bow
        r = 1 + i // 2                       # 1,1,2,2 — bigger nearer the dart
        pts.append((int(x), int(y), r))
    for x, y, r in pts:
        pygame.draw.circle(surf, halo, (x, y), r + 1)
    for x, y, r in pts:
        pygame.draw.circle(surf, col, (x, y), r)
