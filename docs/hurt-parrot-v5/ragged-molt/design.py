"""
ragged-molt — hurt-parrot concept: falling apart, feather by feather.

The damage is entirely *subtractive plumage*: nothing is added to Pip that he
did not already have. Three wedges are torn out of the wing's trailing edge as
genuine holes, two bare-skin patches show where body feathers have dropped off,
and the smooth crown line is replaced by a ruffled crest of short spikes. The
tail is deliberately untouched — a neighbouring concept owns tail damage, and
keeping the fan intact also keeps the silhouette anchored so the wing's missing
bites read as loss rather than as a differently-shaped bird.

Two constraints drove the implementation more than anything else:

* A hole in the wing is only a hole if sky shows through it. The wing is blitted
  over the body, so cutting the wing polygon alone would just expose red body
  underneath and read as a smudge. The cuts are therefore applied to the finished
  sprite and masked against a wingless rebuild, so a wedge can only remove pixels
  the wing contributed over empty background. That also makes them survive
  `_add_outline`, which rims each notch in dark and sharpens the V at 1x.
* Bare skin has to be a *depression*, not a decal. A flat darker blob reads as
  dirt; the 1-px lighter rim along the top edge gives it a lip, so the eye reads
  the dark field as sunken flesh below missing feathers.

Nothing here imports from `game/` except the healthy reference frame in the
review-sheet block; this file only renders a review sheet.
"""
import math
import os
import sys

os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "offscreen"

sys.path.insert(0, "/home/user/skybit")

import pygame

pygame.init()

SPRITE_W, SPRITE_H = 64, 60

# Compressed downward arc shared by the hurt-parrot concepts — the hurt bird
# never lifts its wing above level again.
_HURT_ANGLES = (10, -5, -20, -35)

# --- palette: the healthy macaw's own colours, nothing new ---
BIRD_RED    = (240,  55,  55)
BIRD_RED_D  = (150,  20,  30)
BIRD_WING   = ( 40, 100, 255)
BIRD_WING_D = ( 20,  55, 170)
BIRD_TIP    = ( 50, 220, 100)
BIRD_BELLY  = (255, 170,  50)
BIRD_BEAK   = (255, 185,   0)
BIRD_BEAK_D = (185, 120,   0)

# Bare skin: a 90-value drop off BIRD_RED so it still reads as flesh-under-
# feathers at 1x rather than as a shadow, plus the lighter lip that turns the
# blob into a dent.
SKIN        = (150,  55,  55)
SKIN_RIM    = (190,  80,  70)

SHADE_BLACK = ( 15,  15,  25)
SHADE_FRAME = (255, 200,  50)
SHADE_GLINT = (255, 255, 255)
SHADE_TINT  = ( 35,  55,  90)

# Wing anchor in sprite space, and the wing surface's own centre — both needed
# to map a wing-local point through the flap rotation into sprite coordinates.
_WING_ANCHOR = (34, 30)
_WING_C      = (25, 25)

# Head ellipse the crest is grown from. Shared so the tufts can't float free of
# the skull when either is nudged.
_HEAD_C, _HEAD_RX, _HEAD_RY = (47, 21), 12, 11

# Trailing (lower-left) edge of the wing polygon, as a polyline. The notches are
# spaced along its arc length so they stay evenly distributed even though the
# two segments differ in length.
_TRAILING = ((48, 28), (34, 46), (14, 44))
_NOTCH_TS = (0.20, 0.48, 0.76)


def _aaellipse(surf, color, center, rx, ry):
    cx, cy = center
    pygame.draw.ellipse(surf, color, (cx - rx, cy - ry, rx * 2, ry * 2))


def _add_outline(src, outline_color=(20, 12, 18, 220)):
    pad = 2
    w, h = src.get_size()
    mask = pygame.mask.from_surface(src, threshold=8)
    sil = mask.to_surface(setcolor=outline_color, unsetcolor=(0, 0, 0, 0))
    out = pygame.Surface((w + pad * 2, h + pad * 2), pygame.SRCALPHA)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == dy == 0:
                continue
            out.blit(sil, (pad + dx, pad + dy))
    out.blit(src, (pad, pad))
    return out


# ── wing ─────────────────────────────────────────────────────────────────────

def _build_wing(angle_deg):
    """The healthy wing with its trailing edge dropped clear of the body.

    This is not decoration — it is what makes the notches possible. On the
    healthy bird the wing's lower edge tucks *inside* the body ellipse, so a
    wedge cut there would expose red body rather than sky and read as a smear.
    Letting the wing hang loose and unpreened pushes that edge 4-8 px past the
    body contour, which is both on-concept for a moulting bird and the only
    geometry in which a torn notch can actually be a hole. Everything above the
    elbow — leading edge, green primaries, yellow secondary — is untouched.
    """
    w = pygame.Surface((50, 50), pygame.SRCALPHA)
    pygame.draw.polygon(w, (0, 0, 0, 110),
                        [(24, 26), (46, 14), (50, 30), (36, 48), (14, 46)])
    pygame.draw.polygon(w, BIRD_WING,
                        [(24, 24), (44, 13), (48, 28), (34, 46), (14, 44)])
    pygame.draw.polygon(w, BIRD_WING_D, [(24, 24), (34, 46), (14, 44)])
    pygame.draw.polygon(w, BIRD_TIP, [(44, 13), (50, 18), (48, 28)])
    pygame.draw.polygon(w, (255, 200, 60), [(42, 18), (48, 22), (46, 28), (40, 24)])
    pygame.draw.line(w, BIRD_WING_D, (26, 25), (42, 18), 2)
    pygame.draw.line(w, BIRD_WING_D, (28, 30), (44, 25), 2)
    pygame.draw.line(w, BIRD_WING_D, (28, 36), (46, 32), 2)
    # Two long shafts running out into the dropped section, so the extra span
    # reads as separated flight feathers rather than a swollen blue paddle.
    pygame.draw.line(w, BIRD_WING_D, (25, 30), (30, 45), 2)
    pygame.draw.line(w, BIRD_WING_D, (25, 30), (41, 38), 2)
    pygame.draw.line(w, (170, 210, 255), (25, 25), (41, 15), 1)
    return pygame.transform.rotate(w, angle_deg)


def _wing_to_sprite(pt, angle_deg, is_vector=False):
    """Map a wing-local point (or direction) through the flap rotation into
    sprite coordinates. Mirrors what `pygame.transform.rotate` + the centred
    blit do, so notch geometry stays welded to the wing at every angle."""
    th = math.radians(angle_deg)
    cs, sn = math.cos(th), math.sin(th)
    rx = pt[0] if is_vector else pt[0] - _WING_C[0]
    ry = pt[1] if is_vector else pt[1] - _WING_C[1]
    vx = rx * cs + ry * sn
    vy = -rx * sn + ry * cs
    if is_vector:
        return (vx, vy)
    return (_WING_ANCHOR[0] + vx, _WING_ANCHOR[1] + vy)


def _trailing_anchors(angle_deg):
    """Three evenly-spaced points on the wing's trailing edge, each with the
    edge tangent and the outward normal, already in sprite space."""
    segs = []
    total = 0.0
    for a, b in zip(_TRAILING, _TRAILING[1:]):
        length = math.hypot(b[0] - a[0], b[1] - a[1])
        segs.append((a, b, length))
        total += length

    out = []
    for t in _NOTCH_TS:
        want = t * total
        for a, b, length in segs:
            if want <= length or (a, b, length) is segs[-1]:
                f = max(0.0, min(1.0, want / length))
                pt = (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)
                d = ((b[0] - a[0]) / length, (b[1] - a[1]) / length)
                break
            want -= length
        # Outward normal is the tangent turned a quarter turn away from the
        # wing's interior; the sign check keeps it pointing out of the polygon
        # regardless of which segment the anchor landed on.
        n = (d[1], -d[0])
        to_out = (pt[0] - 33, pt[1] - 28)
        if n[0] * to_out[0] + n[1] * to_out[1] < 0:
            n = (-n[0], -n[1])
        out.append((_wing_to_sprite(pt, angle_deg),
                    _wing_to_sprite(d, angle_deg, True),
                    _wing_to_sprite(n, angle_deg, True)))
    return out


def _notch_wedges(angle_deg):
    """Wedge polygons for the three torn notches. Each opens outward past the
    wing's drop shadow so the cut severs the whole edge cleanly, and tapers to
    a point 7 px in — deep enough to bite the outline, far short of severing
    the wing into islands."""
    half, out_push, depth = 3.6, 5.0, 7.0
    wedges = []
    for pt, d, n in _trailing_anchors(angle_deg):
        wedges.append([
            (pt[0] + d[0] * half + n[0] * out_push,
             pt[1] + d[1] * half + n[1] * out_push),
            (pt[0] - d[0] * half + n[0] * out_push,
             pt[1] - d[1] * half + n[1] * out_push),
            (pt[0] - n[0] * depth, pt[1] - n[1] * depth),
        ])
    return wedges


def _punch_notches(surf, wingless, angle_deg):
    """Erase the notch wedges from `surf` to alpha 0, but only where the wing is
    the sole contributor. Masking against the wingless rebuild is what stops a
    notch from taking a bite out of the body or the tail — over those, the
    wedge would have exposed red rather than sky and read as a bruise."""
    cut = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    cut.fill((255, 255, 255, 255))
    for pts in _notch_wedges(angle_deg):
        pygame.draw.polygon(cut, (0, 0, 0, 0), [(int(round(x)), int(round(y)))
                                                for x, y in pts])
    keep = pygame.mask.from_surface(wingless, threshold=8).to_surface(
        setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0))
    cut.blit(keep, (0, 0), special_flags=pygame.BLEND_RGBA_MAX)
    surf.blit(cut, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)


# ── bare skin ────────────────────────────────────────────────────────────────

# Two patches on the upper body. Positions are pushed toward the shoulder and
# the flank rather than the mid-back: the wing sweeps across the middle of the
# body at every flap angle, and a patch hidden under it for three frames of four
# is not a patch.
_SKIN_PATCHES = (
    ((38, 25), 5.0, 3.4),
    ((41, 33), 4.4, 3.0),
)


def _draw_skin_patch(surf, center, rx, ry):
    """One bare-skin patch: an irregular blob of exposed flesh with a bright lip
    on its upper edge. The irregularity matters — a clean ellipse reads as a
    painted spot, a wobbled outline reads as a feather boundary."""
    cx, cy = center
    # Wobble amounts are fixed rather than random so the sprite is byte-stable
    # across builds; the pattern is what sells "torn", not the entropy.
    wobble = (1.15, 0.82, 1.20, 0.88, 1.10, 0.80, 1.18, 0.92)
    pts = []
    for i, k in enumerate(wobble):
        a = math.tau * i / len(wobble)
        pts.append((cx + math.cos(a) * rx * k, cy + math.sin(a) * ry * k))
    pygame.draw.polygon(surf, SKIN, [(int(round(x)), int(round(y)))
                                     for x, y in pts])
    # Lip: the upper arc only. Running it all the way round would outline the
    # patch and flatten it back into a sticker.
    rim = [p for p in pts if p[1] <= cy]
    rim.sort(key=lambda p: p[0])
    if len(rim) >= 2:
        pygame.draw.lines(surf, SKIN_RIM, False,
                          [(int(round(x)), int(round(y - 1))) for x, y in rim], 1)


# ── crest ────────────────────────────────────────────────────────────────────

# Five tufts across the crown. Heights are uneven on purpose: a matched row of
# spikes reads as a cockatoo crest (a feature), an uneven one reads as feathers
# standing up wrong (a symptom).
_TUFTS = ((38.5, 6.5), (42.0, 7.5), (45.5, 7.5), (49.0, 6.5), (52.5, 5.0))
_TUFT_HALF = 1.6


def _crown_top(x):
    """Y of the head ellipse's upper edge at `x` — the tufts are seated from it
    so every spike is rooted in the skull instead of hovering over it."""
    k = (x - _HEAD_C[0]) / _HEAD_RX
    k = max(-0.999, min(0.999, k))
    return _HEAD_C[1] - _HEAD_RY * math.sqrt(1.0 - k * k)


def _draw_crest(surf):
    for x, h in _TUFTS:
        base_y = _crown_top(x) + 2.0
        pygame.draw.polygon(surf, BIRD_RED, [
            (int(round(x - _TUFT_HALF)), int(round(base_y))),
            (int(round(x + _TUFT_HALF)), int(round(base_y))),
            (int(round(x)), int(round(base_y - h))),
        ])
        # A darker inner sliver keeps each spike from flooding into its
        # neighbour once the 1-px outline dilates them.
        pygame.draw.line(surf, BIRD_RED_D,
                         (int(round(x)), int(round(base_y))),
                         (int(round(x)), int(round(base_y - h * 0.55))), 1)


# ── face ─────────────────────────────────────────────────────────────────────

def _draw_sunglasses(surf, cx, cy):
    r = 6
    left, right = (cx - 4, cy), (cx + 6, cy - 1)
    for c in (left, right):
        pygame.draw.circle(surf, SHADE_FRAME, c, r + 1)
        pygame.draw.circle(surf, SHADE_BLACK, c, r)
    tint = pygame.Surface((r * 2, r), pygame.SRCALPHA)
    pygame.draw.ellipse(tint, (*SHADE_TINT, 130), tint.get_rect())
    surf.blit(tint, (left[0] - r, left[1] - r + 1))
    surf.blit(tint, (right[0] - r, right[1] - r + 1))
    pygame.draw.circle(surf, SHADE_GLINT, (left[0] - 2, left[1] - 2), 2)
    pygame.draw.circle(surf, SHADE_GLINT, (right[0] - 2, right[1] - 3), 2)
    pygame.draw.line(surf, SHADE_FRAME,
                     (left[0] + r, left[1]), (right[0] - r, right[1]), 2)
    pygame.draw.line(surf, SHADE_FRAME,
                     (left[0] - r + 1, left[1] - r + 2),
                     (right[0] + r - 1, right[1] - r + 2), 1)


# ── frame ────────────────────────────────────────────────────────────────────

def _build_hurt_frame(wing_angle_deg, *, with_wing=True):
    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    d = pygame.draw

    # Tail — untouched. Scorched-afterburn owns tail damage; here the intact fan
    # is the control that makes the wing's missing bites measurable by eye.
    for i, c in enumerate([(200, 30, 40), (240, 95, 40),
                           (255, 160, 55), (255, 220, 80)]):
        d.polygon(surf, c, [(2 + i * 3, 26 + i * 2), (14 + i, 24 + i),
                            (20 + i, 30 + i * 2), (6 + i * 3, 36 + i * 2)])
    d.line(surf, BIRD_RED_D, (4, 27), (18, 31), 1)
    d.line(surf, BIRD_RED_D, (6, 33), (20, 35), 1)

    _aaellipse(surf, (120, 20, 25), (34, 35), 19, 14)
    _aaellipse(surf, BIRD_RED,      (32, 32), 19, 14)
    _aaellipse(surf, (255, 100, 100), (30, 29), 13, 8)
    _aaellipse(surf, BIRD_BELLY,    (28, 38), 12, 6)

    # Sheen stays, but only on the front of the breast — the moulting shoulder
    # behind it should not look glossy.
    sheen = pygame.Surface((20, 6), pygame.SRCALPHA)
    pygame.draw.ellipse(sheen, (255, 230, 230, 160), sheen.get_rect())
    surf.blit(sheen, (20, 21))

    for center, rx, ry in _SKIN_PATCHES:
        _draw_skin_patch(surf, center, rx, ry)

    if with_wing:
        wing = _build_wing(wing_angle_deg)
        surf.blit(wing, wing.get_rect(center=_WING_ANCHOR).topleft)

    _aaellipse(surf, (150, 15, 20), (48, 23), 12, 11)
    _aaellipse(surf, BIRD_RED, _HEAD_C, _HEAD_RX, _HEAD_RY)
    _aaellipse(surf, (255, 130, 130), (44, 24), 4, 3)
    # No crown highlight: the smooth gloss band is exactly the "well-groomed"
    # cue the crest is meant to replace.
    _draw_crest(surf)

    _draw_sunglasses(surf, 50, 20)

    beak_pts = [(55, 21), (61, 24), (58, 28), (52, 26)]
    d.polygon(surf, BIRD_BEAK, beak_pts)
    d.polygon(surf, BIRD_BEAK_D, beak_pts, 1)
    d.line(surf, (255, 230, 150), (55, 22), (59, 24), 1)
    d.line(surf, BIRD_BEAK_D, (52, 24), (58, 25), 1)

    d.line(surf, BIRD_BEAK_D, (28, 45), (26, 49), 2)
    d.line(surf, BIRD_BEAK_D, (34, 45), (36, 49), 2)

    if with_wing:
        _punch_notches(surf, _build_hurt_frame(wing_angle_deg, with_wing=False),
                       wing_angle_deg)
    return surf


# ── review sheet ─────────────────────────────────────────────────────────────

def _strip(frames, scale, gap, bg=(8, 8, 20)):
    fw, fh = frames[0].get_size()
    s = pygame.Surface((len(frames) * fw * scale + (len(frames) - 1) * gap,
                        fh * scale))
    s.fill(bg)
    for i, f in enumerate(frames):
        s.blit(pygame.transform.scale(f, (fw * scale, fh * scale)),
               (i * (fw * scale + gap), 0))
    return s


if __name__ == "__main__":
    from game.parrot import _build_frame as _healthy_frame

    OUT_DIR = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(OUT_DIR, exist_ok=True)

    raw = [_build_hurt_frame(a) for a in _HURT_ANGLES]
    hurt = [_add_outline(f) for f in raw]
    healthy = [_add_outline(_healthy_frame(a)) for a in (20, 0, -20, -40)]

    fw, fh = hurt[0].get_size()

    try:
        font = pygame.font.SysFont("dejavusans", 17)
        small = pygame.font.SysFont("dejavusans", 12)
    except Exception:
        font = pygame.font.Font(None, 17)
        small = pygame.font.Font(None, 12)

    row_hurt = _strip(hurt, 4, 8)
    row_healthy = _strip(healthy, 4, 8)
    row_detail = _strip([hurt[1]], 8, 0)

    margin, label_h, row_gap = 20, 24, 14
    canvas_w = margin * 2 + max(row_hurt.get_width(),
                                row_detail.get_width() + 220)
    canvas_h = (margin + 28
                + label_h + row_hurt.get_height() + row_gap
                + label_h + row_healthy.get_height() + row_gap
                + label_h + fh + row_gap
                + label_h + row_detail.get_height() + margin)
    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((8, 8, 20))

    def _title(text, y, f=small, col=(190, 190, 215)):
        canvas.blit(f.render(text, True, col), (margin, y))

    y = margin
    _title("ragged-molt — round 1  ·  falling apart, feather by feather", y,
           font, (235, 235, 250))
    y += 28

    _title("hurt (4x)  —  3 torn wing notches · 2 bare-skin patches · ruffled crest", y)
    y += label_h
    canvas.blit(row_hurt, (margin, y))
    y += row_hurt.get_height() + row_gap

    _title("healthy reference (4x)", y)
    y += label_h
    canvas.blit(row_healthy, (margin, y))
    y += row_healthy.get_height() + row_gap

    _title("1x game scale — hurt strip, then healthy", y)
    y += label_h
    for i, frame in enumerate(hurt + healthy):
        canvas.blit(frame, (margin + i * (fw + 6), y))
    y += fh + row_gap

    _title("frame 1 at 8x — notch / patch / crest detail", y)
    y += label_h
    canvas.blit(row_detail, (margin, y))

    out_path = os.path.join(OUT_DIR, "round_1.png")
    pygame.image.save(canvas, out_path)

    # The bare 4-frame strip at 1x on the review background, exactly as the
    # brief specifies it, kept alongside the annotated sheet.
    pygame.image.save(_strip(hurt, 1, 0), os.path.join(OUT_DIR, "strip_1x.png"))

    # --- verification (printed, not asserted) ---
    for i, a in enumerate(_HURT_ANGLES):
        frame = raw[i]
        wingless = _build_hurt_frame(a, with_wing=False)
        no_notch = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
        no_notch.blit(frame, (0, 0))

        skin_px = crest_px = notch_px = 0
        for x in range(SPRITE_W):
            for py in range(SPRITE_H):
                r, g, b, al = frame.get_at((x, py))
                if al > 8 and 130 <= r <= 170 and g < 80 and b < 90:
                    skin_px += 1
                # True crest pixels: opaque and OUTSIDE the head ellipse, so the
                # skull's own red can't inflate the count.
                if al > 8 and py < _HEAD_C[1]:
                    k = ((x - _HEAD_C[0]) / _HEAD_RX) ** 2 + \
                        ((py - _HEAD_C[1]) / _HEAD_RY) ** 2
                    if k > 1.0 and abs(r - BIRD_RED[0]) < 40 and g < 110 and 35 <= x <= 58:
                        crest_px += 1

        # Notch transparency is the exact set of pixels the punch removed: any
        # pixel transparent in the finished frame but opaque in a wedge-free
        # rebuild of the same composite.
        probe = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
        probe.blit(wingless, (0, 0))
        w_rot = _build_wing(a)
        probe.blit(w_rot, w_rot.get_rect(center=_WING_ANCHOR).topleft)
        for x in range(SPRITE_W):
            for py in range(SPRITE_H):
                if frame.get_at((x, py))[3] < 8 and probe.get_at((x, py))[3] > 8:
                    notch_px += 1

        print(f"frame {i} (angle {a:>4}): skin={skin_px:>3}  crest={crest_px:>3}  "
              f"notch_alpha0={notch_px:>3}")

    print(f"Saved round_1.png {canvas_w}x{canvas_h}")
