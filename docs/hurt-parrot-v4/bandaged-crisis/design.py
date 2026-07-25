"""
`bandaged-crisis` — hurt-parrot concept exploration (standalone, not wired in).

V4 of the bloodshot line. V3 told the injury with claw-rake texture, which is
exactly the class of detail that dies at 1x — dark-on-dark cuts on a dark red
breast. So the rake is gone entirely and the whole story is carried by three
pieces of high-contrast *applied* hardware: a temple gauze strip, an adhesive
plaster on the breast, and a tape band across the wing. Off-white on red is the
strongest value pair available in this palette, and the red cross is the one
piece of universal shorthand a player parses before they parse anything else.

The shades escalate to match: the left lens is a full shatter web, not a star,
and the exhaustion is sold by under-eye shadow plus a crown of feather wisps
kicked out of place. Damage now reads as *stuff stuck to the bird* rather than
marks drawn into it, which is the only version that survives the downscale.
"""
import math
import os, sys
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "offscreen"
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()

SPRITE_W, SPRITE_H = 64, 60
_HURT_ANGLES = (10, -5, -20, -35)

SHADE_BLACK = (15, 15, 25)
SHADE_GLINT = (255, 255, 255)
SHADE_TINT  = (35, 55, 90)
SHADE_FRAME = (220, 175, 40)

GAUZE      = (232, 228, 215)
PAD        = (255, 248, 230)
STITCH     = (160, 148, 130)
CROSS      = (210, 30, 30)
# Cracks read as light caught in the fracture — glass chips bright, and the
# bright line is also the only thing that survives the downscale.
CRACK      = (180, 210, 240)
CRACK_WEB  = (140, 170, 200)

WISP_L   = (230,  80,  80)
WISP_C   = (210,  60,  60)
WISP_R   = (220,  70,  70)
WISP_TIP = (240, 130, 130)

# Left lens rides five pixels low and a size larger than its twin: the side that
# took the hit is the side the eye should land on first, and the drop is also
# what clears the shatter web out from under the temple gauze.
LENS_L, LENS_LR = (43, 24), 7
LENS_R, LENS_RR = (56, 19), 6


def _aaellipse(surf, color, center, rx, ry):
    cx, cy = center
    pygame.draw.ellipse(surf, color, (cx - rx, cy - ry, rx * 2, ry * 2))


def _stamp_clipped(surf, layer):
    """Composite a layer only where the sprite already has body. Applied
    hardware — tape, plaster — is drawn in flat world coordinates so it lands
    the same on every frame; clipping is what stops the overhang from becoming
    a floating white chip once the outline pass runs."""
    for x in range(surf.get_width()):
        for y in range(surf.get_height()):
            px = layer.get_at((x, y))
            if px[3] > 8 and surf.get_at((x, y))[3] > 8:
                if px[3] >= 250:
                    surf.set_at((x, y), px)
                else:
                    base = surf.get_at((x, y))
                    a = px[3] / 255.0
                    surf.set_at((x, y), (
                        int(base[0] * (1 - a) + px[0] * a),
                        int(base[1] * (1 - a) + px[1] * a),
                        int(base[2] * (1 - a) + px[2] * a),
                        base[3]))


def _add_outline(src, outline_color=(20, 12, 18, 220)):
    pad = 2
    w, h = src.get_size()
    mask = pygame.mask.from_surface(src, threshold=8)
    sil  = mask.to_surface(setcolor=outline_color, unsetcolor=(0, 0, 0, 0))
    out  = pygame.Surface((w + pad * 2, h + pad * 2), pygame.SRCALPHA)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == dy == 0:
                continue
            out.blit(sil, (pad + dx, pad + dy))
    out.blit(src, (pad, pad))
    return out


def _build_wing(angle_deg):
    WING   = (30,  70, 180)
    WING_D = (18,  42, 125)
    # Pulled back off the healthy bird's vivid green: the wing is the one large
    # colour field on the sprite, and dropping its chroma lets the white
    # hardware stay the brightest thing in the silhouette.
    TIP    = (40, 185,  80)
    STRIPE = (210, 175,  50)
    HL     = (130, 175, 240)
    w = pygame.Surface((50, 50), pygame.SRCALPHA)
    d = pygame.draw
    d.polygon(w, (0,0,0,100), [(24,26),(46,14),(50,30),(34,44),(18,40)])
    d.polygon(w, WING,        [(24,24),(44,13),(48,28),(32,42),(18,36)])
    d.polygon(w, WING_D,      [(24,24),(32,42),(18,36)])
    d.polygon(w, TIP,         [(44,13),(50,18),(48,28)])
    d.polygon(w, STRIPE,      [(42,18),(48,22),(46,28),(40,24)])
    d.line(w, WING_D,         (26,25),(42,18), 2)
    d.line(w, WING_D,         (28,30),(44,25), 2)
    d.line(w, WING_D,         (30,34),(46,32), 2)
    d.line(w, HL,             (25,25),(41,15), 1)
    # A chunk torn out of the primaries, punched as transparency rather than
    # painted dark so the break survives the outline pass and the 1x downscale.
    d.polygon(w, (0,0,0,0),   [(41,11),(53,17),(47,25),(43,16)])
    return pygame.transform.rotate(w, angle_deg)


def _draw_plaster(surf):
    """Adhesive plaster on the breast. A square of gauze with a purer white pad
    inside it: two values plus a hemmed outline is the smallest arrangement
    that still parses as "sticking plaster" and not "white blob".

    Sits low on the belly and goes on after the wing. Pinned higher on the
    chest and layered under the wing — the anatomically tidier order — the
    downstroke frames swallowed it whole, and a medical mark that exists on
    half the animation is worse than none at all."""
    layer = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    d = pygame.draw
    cx, cy = 26, 38
    d.rect(layer, GAUZE, (cx - 5, cy - 5, 10, 10))
    d.rect(layer, PAD,   (cx - 3, cy - 3,  6,  6))
    d.rect(layer, STITCH, (cx - 5, cy - 5, 10, 10), 1)
    d.line(layer, CROSS, (cx - 2, cy), (cx + 1, cy), 1)
    d.line(layer, CROSS, (cx, cy - 2), (cx, cy + 1), 1)
    _stamp_clipped(surf, layer)


def _draw_wing_tape(surf):
    """Tape band across the wing. Held just off opaque so the covert banding
    tints through and the strip stays bonded to the wing instead of floating
    like a sticker — but no further: over the red body a genuinely translucent
    white curdles to pink and stops reading as tape at all. Kept clear of the
    head lobe, since anything past x~38 in this band is overpainted by the
    skull on the very next call."""
    layer = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    d = pygame.draw
    # Five tall, not four: the hemmed edges eat a row each, and a two-pixel
    # white core is not a tape strip at 1x, it is a scuff.
    x0, y0, w, h = 19, 22, 20, 5
    d.rect(layer, (*GAUZE, 235), (x0, y0, w, h))
    d.line(layer, STITCH, (x0, y0), (x0 + w - 1, y0), 1)
    d.line(layer, STITCH, (x0, y0 + h - 1), (x0 + w - 1, y0 + h - 1), 1)
    _stamp_clipped(surf, layer)


def _draw_head_wisps(surf):
    """Feather wisps kicked off the crown at wrong angles. Hurt is posture as
    much as damage, and a broken crown line is the cheapest posture cue there
    is — it costs three polylines and changes the whole silhouette. Drawn under
    the shades so the frame naturally sits over the roots."""
    d = pygame.draw
    for pts, col in (
        ([(46, 14), (43, 9), (41, 6)], WISP_L),
        ([(47, 13), (47, 8), (48, 5)], WISP_C),
        ([(48, 14), (51, 9), (53, 7)], WISP_R),
    ):
        d.lines(surf, col, False, pts, 2)
        d.line(surf, WISP_TIP, pts[-2], pts[-1], 2)


def _draw_bandage(surf):
    """Gauze taped diagonally across the temple, on top of the shades. Widened
    to 6 px perpendicular and hemmed on both long edges — at V3's 4 px the
    strip lost half its white to the stitching and stopped reading as gauze at
    1x. The cross is the single most legible mark on the sprite, so it gets
    real width rather than the one-pixel scratch it was.

    Clipped to the silhouette: the skull narrows fast above the brow, and drawn
    free the crown end of the strip hung in open sky as a loose white flag. Let
    the head cut it and the same quad instead reads as gauze wrapping over the
    top of the skull, which is what the strip is supposed to be doing."""
    layer = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    d = pygame.draw
    quad = [(33, 21), (39, 10), (50, 12), (44, 23)]
    d.polygon(layer, GAUZE, quad)
    d.line(layer, STITCH, quad[0], quad[1], 2)
    d.line(layer, STITCH, quad[2], quad[3], 2)
    d.line(layer, CROSS, (39, 16), (46, 16), 2)
    d.line(layer, CROSS, (42, 12), (42, 20), 2)
    _stamp_clipped(surf, layer)


def _draw_sunglasses(surf):
    """Aviator shades, knocked crooked. The left lens rides 3 px low and a size
    wider; the bridge kinks up to meet its twin instead of running level. "Took
    one to the face" told entirely in geometry. Only the right lens keeps its
    glint — one dead lens against one still catching the sun is the read."""
    d = pygame.draw
    d.circle(surf, SHADE_FRAME, LENS_L, LENS_LR + 1)
    d.circle(surf, SHADE_FRAME, LENS_R, LENS_RR + 1)
    d.circle(surf, SHADE_BLACK, LENS_L, LENS_LR)
    d.circle(surf, SHADE_BLACK, LENS_R, LENS_RR)
    for c, r in ((LENS_L, LENS_LR), (LENS_R, LENS_RR)):
        tint = pygame.Surface((r * 2, r), pygame.SRCALPHA)
        d.ellipse(tint, (*SHADE_TINT, 130), tint.get_rect())
        surf.blit(tint, (c[0] - r, c[1] - r + 1))
    d.circle(surf, SHADE_GLINT, (LENS_R[0] - 2, LENS_R[1] - 3), 2)
    d.circle(surf, (255, 255, 255, 200), (LENS_R[0] + 2, LENS_R[1] + 1), 1)
    d.line(surf, SHADE_FRAME, (49, 24), (52, 20), 2)
    d.line(surf, SHADE_FRAME,
           (LENS_L[0] - LENS_LR + 1, LENS_L[1] - LENS_LR + 2),
           (LENS_R[0] + LENS_RR - 1, LENS_R[1] - LENS_RR + 2), 1)


def _lens_clip(surf, layer, center, radius):
    """Fracture lines are clipped to the glass they belong to. Left free they
    ran off the rim and onto the skull, which read as face wounds rather than
    broken glass — and a crack that stops dead at the frame is exactly what
    real shattered glass does."""
    mask = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), center, radius)
    layer.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(layer, (0, 0))


def _draw_cracked_lenses(surf):
    """Left lens shatters, right lens only sympathises. Five uneven radials off
    a single off-centre impact point plus two chords webbing their tips: the
    chords are what turn a starburst into shattered glass, because they imply
    plates of lens that have come apart rather than lines scratched on it."""
    d = pygame.draw
    layer = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    impact = (43, 23)
    for end in ((38, 18), (49, 19), (37, 25), (48, 28), (42, 29)):
        d.line(layer, CRACK, impact, end, 1)
    d.line(layer, CRACK_WEB, (39, 19), (37, 25), 1)
    d.line(layer, CRACK_WEB, (48, 19), (48, 28), 1)
    # Clipped to the rim rather than the glass: a fracture that runs right into
    # the frame is what real shattered glass does, and holding it a pixel short
    # cost the web its outermost — most legible — spans.
    _lens_clip(surf, layer, LENS_L, LENS_LR + 1)

    layer = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    d.line(layer, CRACK, (55, 19), (52, 16), 1)
    d.line(layer, CRACK, (55, 19), (58, 22), 1)
    _lens_clip(surf, layer, LENS_R, LENS_RR)


def _draw_eye_shadow(surf):
    """Exhaustion bag under the cracked lens, hung low enough that half of it
    clears the rim. Entirely behind the glass it just muddied the lens fill;
    breaking below the frame is what turns it into a face reading tired."""
    shadow = pygame.Surface((13, 7), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, (40, 8, 8, 160), shadow.get_rect())
    layer = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    layer.blit(shadow, (37, 28))
    _stamp_clipped(surf, layer)


def _tail_feather(pts, damaged=False):
    """Tail feathers run root-right, tip-left. A damaged one is snapped short
    and kicked off-axis so the fan's clean outline breaks — silhouette damage
    survives the 1x downscale where any painted-on detail would not."""
    if not damaged:
        return pts
    root = ((pts[1][0] + pts[2][0]) / 2.0, (pts[1][1] + pts[2][1]) / 2.0)
    a = math.radians(18)
    ca, sa = math.cos(a), math.sin(a)
    out = []
    for i, (x, y) in enumerate(pts):
        if i in (0, 3):
            dx, dy = root[0] - x, root[1] - y
            L = max(1e-3, math.hypot(dx, dy))
            x, y = x + dx / L * 8.0, y + dy / L * 8.0
        vx, vy = x - root[0], y - root[1]
        out.append((root[0] + vx * ca - vy * sa, root[1] + vx * sa + vy * ca))
    return out


def _build_hurt_frame(wing_angle_deg):
    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    d = pygame.draw

    BODY    = (205,  28,  28)
    BODY_SH = (130,  12,  12)
    CHEST   = (235,  80,  80)
    BELLY   = (215, 140,  45)
    BEAK    = (235, 168,   0)
    BEAK_LO = (205, 138,   0)
    BEAK_D  = (140,  92,   0)

    for i, c in enumerate(((180, 25, 35), (190, 70, 30),
                           (210, 130, 40), (230, 195, 65))):
        pts = [
            (2 + i * 3, 26 + i * 2), (14 + i, 24 + i),
            (20 + i, 30 + i * 2), (6 + i * 3, 36 + i * 2),
        ]
        d.polygon(surf, c, _tail_feather(pts, damaged=(i == 1)))
    d.line(surf, BODY_SH, (4, 27), (18, 31), 1)
    d.line(surf, BODY_SH, (6, 33), (20, 35), 1)

    _aaellipse(surf, BODY_SH, (34, 35), 19, 14)
    _aaellipse(surf, BODY,    (32, 32), 19, 14)
    _aaellipse(surf, CHEST,   (30, 29), 13,  8)
    _aaellipse(surf, BELLY,   (28, 38), 12,  6)

    sheen = pygame.Surface((28, 6), pygame.SRCALPHA)
    d.ellipse(sheen, (205, 150, 150, 120), sheen.get_rect())
    surf.blit(sheen, (22, 21))

    wing = _build_wing(wing_angle_deg)
    surf.blit(wing, wing.get_rect(center=(34, 28)).topleft)

    _draw_wing_tape(surf)
    _draw_plaster(surf)

    # Head hangs 1 px lower than the healthy build — small in absolute terms,
    # but it breaks the proud upward line of the original silhouette.
    _aaellipse(surf, (155, 15, 20), (48, 24), 12, 11)
    _aaellipse(surf, BODY,          (47, 22), 12, 11)
    _aaellipse(surf, (200, 90, 90), (44, 24),  4,  3)
    _aaellipse(surf, (230, 140, 140), (46, 17),  7,  3)

    _draw_head_wisps(surf)
    _draw_sunglasses(surf)
    _draw_cracked_lenses(surf)
    _draw_eye_shadow(surf)
    _draw_bandage(surf)

    # Beak parted only ~2 px, and the lower mandible tucked up under the upper.
    # Dropping it further left a spur hanging off the chin that made the bird
    # read as some other species entirely.
    upper = [(55, 21), (61, 24), (58, 26), (52, 25)]
    lower = [(52, 26), (58, 27), (59, 30), (54, 31)]
    d.polygon(surf, BEAK,    upper)
    d.polygon(surf, BEAK_D,  upper, 1)
    d.polygon(surf, BEAK_LO, lower)
    d.polygon(surf, BEAK_D,  lower, 1)
    d.line(surf, (255, 220, 100), (55, 22), (59, 24), 1)

    d.line(surf, BEAK_D, (28, 45), (26, 49), 2)
    d.line(surf, BEAK_D, (34, 45), (36, 49), 2)

    return surf


def _count(frame, pred, box=None):
    """Counts are box-scoped on purpose. A whole-sprite tally of "white pixels"
    passes happily while one of the three bandages is being overpainted by the
    wing — each mark has to be proved present in its own region."""
    x0, y0, x1, y1 = box or (0, 0, SPRITE_W, SPRITE_H)
    n = 0
    for x in range(x0, min(x1, SPRITE_W)):
        for y in range(y0, min(y1, SPRITE_H)):
            r, g, b, a = frame.get_at((x, y))
            if a > 8 and pred(r, g, b):
                n += 1
    return n


def _strip(frames, scale, gap, bg):
    fw, fh = frames[0].get_size()
    w = len(frames) * fw * scale + (len(frames) - 1) * gap
    s = pygame.Surface((w, fh * scale))
    s.fill(bg)
    for i, f in enumerate(frames):
        s.blit(pygame.transform.scale(f, (fw * scale, fh * scale)),
               (i * (fw * scale + gap), 0))
    return s


if __name__ == "__main__":
    OUT_DIR = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(OUT_DIR, exist_ok=True)

    raw    = [_build_hurt_frame(a) for a in _HURT_ANGLES]
    frames = [_add_outline(f) for f in raw]

    is_gauze  = lambda r, g, b: 220 < r < 245 and 215 < g < 235 and 200 < b < 225
    is_pad    = lambda r, g, b: (r, g, b) in (GAUZE, PAD, STITCH)
    is_crack  = lambda r, g, b: r < 200 and g > 160 and b > 180
    is_wisp   = lambda r, g, b: (r, g, b) in (WISP_L, WISP_C, WISP_R)

    gauze_a  = min(_count(f, is_gauze, (32,  8, 56, 26)) for f in raw)
    plaster  = min(_count(f, is_pad,   (18, 30, 36, 48)) for f in raw)
    tape     = min(_count(f, is_gauze, (16, 20, 40, 30)) for f in raw)
    crack_px = min(_count(f, is_crack, (32, 12, 56, 36)) for f in raw)
    wisp_px  = min(_count(f, is_wisp,  ( 0,  0, 64, 15)) for f in raw)

    assert gauze_a  >= 40, f"Temple bandage too faint: {gauze_a}"
    assert plaster  >= 20, f"Chest plaster missing: {plaster}"
    assert tape     >= 20, f"Wing tape missing: {tape}"
    assert crack_px >= 25, f"Cracks invisible: {crack_px}"
    assert wisp_px  >=  6, f"Head wisps missing: {wisp_px}"

    NIGHT, DAY = (8, 8, 20), (100, 160, 220)
    margin, gap = 20, 10
    row1  = _strip(frames, 4, gap, NIGHT)
    row2  = _strip(frames, 2, gap, NIGHT)
    row3a = _strip(frames, 1, gap, DAY)
    row3b = _strip(frames, 1, gap, (5, 8, 30))

    label_h, pad3 = 30, 12
    canvas_w = margin * 2 + max(row1.get_width(), row2.get_width())
    canvas_h = (margin + row1.get_height() + gap + row2.get_height() + gap +
                row3a.get_height() + pad3 * 2 + label_h + margin)
    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill(NIGHT)

    canvas.blit(row1, (margin, margin))
    y = margin + row1.get_height() + gap
    canvas.blit(row2, (margin, y))
    y += row2.get_height() + gap

    # Day and night side by side at shipping size: the whole point of the white
    # hardware and the ice-blue cracks is that they hold on both backgrounds.
    for i, (panel, bg) in enumerate(((row3a, DAY), (row3b, (5, 8, 30)))):
        px = margin + i * (panel.get_width() + pad3 * 2 + gap * 2)
        pygame.draw.rect(canvas, bg, (px, y, panel.get_width() + pad3 * 2,
                                      panel.get_height() + pad3 * 2))
        canvas.blit(panel, (px + pad3, y + pad3))
    y += row3a.get_height() + pad3 * 2

    try:
        font  = pygame.font.SysFont("dejavusans", 17)
        small = pygame.font.SysFont("dejavusans", 12)
    except Exception:
        font = small = pygame.font.Font(None, 17)
    canvas.blit(small.render("1x on day sky", True, (10, 20, 40)),
                (margin + pad3, y - pad3 + 1))
    canvas.blit(small.render("1x on night sky", True, (200, 205, 230)),
                (margin + row3a.get_width() + pad3 * 3 + gap * 2, y - pad3 + 1))
    lbl = font.render("bandaged-crisis — round 1   (4x / 2x / 1x day + night)",
                      True, (225, 225, 245))
    canvas.blit(lbl, (margin, canvas_h - margin - lbl.get_height() + 4))

    out_path = os.path.join(OUT_DIR, "round_1.png")
    pygame.image.save(canvas, out_path)
    print(f"Saved {canvas_w}x{canvas_h} -> {out_path}")
    print(f"gauze_A={gauze_a}  plaster={plaster}  tape={tape}  "
          f"cracks={crack_px}  wisps={wisp_px}")
