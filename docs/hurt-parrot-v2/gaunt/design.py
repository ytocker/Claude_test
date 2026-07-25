"""
gaunt — emaciation hurt-parrot concept (standalone exploration).

Pip after the hit reads as *structurally* damaged rather than recoloured, and
the damage is carried by the outline: the tail fan loses two feathers and 30%
of its reach, the head shrinks and tips further nose-down every frame, and the
wing thins to a semi-transparent membrane over a forked bone. The body itself
stays near full size (0.82) on purpose — the game already owns "small bird" as
the Shrink power-up's reward signature, so shrinking the whole sprite would
read as a pickup. Collapsing the *hull* while the body stays big reads as
starvation instead.

The face is the fastest beat: the aviators have slipped — right lens dropped
onto the beak, frame bar canted ~10° — and one bare, haunted eye stares out
above the crooked rim.

Nothing here imports from `game/`; this file only renders a review sheet.
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

# Compressed downward arc — the wing barely lifts any more.
_HURT_ANGLES = (10, -5, -20, -35)

# --- starved palette: same hues as the healthy macaw, drained of energy ---
BODY        = (195,  42,  42)
BODY_SHADOW = (108,  18,  22)
CHEST       = (225,  88,  88)
BELLY       = (205, 136,  40)
HEAD_SHADOW = (135,  13,  18)
CHEEK       = (228, 146, 146)
CROWN       = (228, 158, 158)

SOCKET      = ( 40,   8,   8)
RIB_TOP     = ( 58,  10,  10)
RIB_MID     = ( 68,  12,  12)
RIB_LOW     = ( 76,  14,  14)

TAIL_COLORS = ((165, 22, 32), (192, 80, 28), (214, 132, 42))
TAIL_LINE   = (120, 18,  24)

BEAK        = (210, 152,   0)
BEAK_D      = (165, 108,   0)
FOOT        = (190, 130,   0)

SHADE_FRAME = (200, 155,  35)
SHADE_LENS  = ( 15,  15,  25)
SHADE_GLINT = (230, 230, 240)

SCLERA      = (230, 220, 200)
IRIS        = ( 40,  10,  10)

BONE        = (210, 195, 162)

# Body ellipse the ribs are stencilled against — shared so the two can't drift.
_BODY_C, _BODY_RX, _BODY_RY = (32, 35), 15, 9

# Head pivot. Sits high enough that the throat gap between head and back reads
# as a bared neck without any neck geometry being drawn for it.
_HEAD_C = (45, 18)


def _aaellipse(surf, color, center, rx, ry):
    cx, cy = center
    pygame.draw.ellipse(surf, color, (cx - rx, cy - ry, rx * 2, ry * 2))


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
    """Skeletal wing — the healthy plan at 85% span, but with the membrane
    dropped to alpha 130 so sky reads straight through it, and the leading-edge
    highlight replaced by a forked bone. Keeping the span near full is what
    makes the transparency legible: a small opaque wing just looks like a small
    wing."""
    def _s(px, py, cx=24, cy=24, f=0.85):
        return (int(cx + (px - cx) * f), int(cy + (py - cy) * f))

    MEMBRANE   = ( 30,  70, 180, 130)
    MEMBRANE_D = ( 15,  40, 130, 130)
    TIP        = ( 70, 150,  60, 130)
    STRIPE     = (180, 140,  35, 130)
    VEIN       = ( 12,  30, 100, 200)

    w = pygame.Surface((50, 50), pygame.SRCALPHA)
    d = pygame.draw

    d.polygon(w, MEMBRANE,
              [_s(*p) for p in ((24, 24), (44, 13), (48, 28), (32, 42), (18, 36))])
    d.polygon(w, MEMBRANE_D,
              [_s(*p) for p in ((24, 24), (32, 42), (18, 36))])
    d.polygon(w, TIP,
              [_s(*p) for p in ((44, 13), (50, 18), (48, 28))])
    d.polygon(w, STRIPE,
              [_s(*p) for p in ((42, 18), (48, 22), (46, 28), (40, 24))])

    # 1-px veins: at this alpha 2-px lines would re-opaque the whole membrane.
    d.line(w, VEIN, _s(26, 25), _s(42, 18), 1)
    d.line(w, VEIN, _s(28, 30), _s(44, 25), 1)
    d.line(w, VEIN, _s(30, 34), _s(46, 32), 1)

    # Forked bone: two struts diverging from a knuckle at the shoulder. A single
    # stroke here read as a specular highlight; the fork reads as anatomy.
    d.line(w, BONE, _s(24, 24), _s(43, 14), 2)
    d.line(w, BONE, _s(24, 24), _s(46, 27), 2)
    d.circle(w, BONE, _s(24, 24), 2)

    return pygame.transform.rotate(w, angle_deg)


def _build_head(droop_deg):
    """Head, face and beak on their own surface so the droop can be a rotation.

    Translating the head down a pixel a frame sat under the perceptual floor at
    1x; rotating it nose-down changes the silhouette instead, which survives the
    downscale."""
    s = pygame.Surface((40, 40), pygame.SRCALPHA)
    d = pygame.draw
    cx, cy = 20, 20

    _aaellipse(s, HEAD_SHADOW, (cx + 1, cy + 1), 8, 7)
    _aaellipse(s, BODY,        (cx, cy),         8, 7)
    _aaellipse(s, CHEEK,       (cx - 3, cy + 3), 3, 2)
    _aaellipse(s, CROWN,       (cx - 1, cy - 5), 5, 2)

    left_lens  = (cx - 4, cy - 2)
    # The right lens has slid 3 px down the face and off onto the beak.
    right_lens = (cx + 4, cy + 1)

    # Hollow socket rim, drawn over the head so it actually survives — the
    # upper-inner arc the dropped lens no longer covers.
    d.arc(s, SOCKET,
          (right_lens[0] - 6, right_lens[1] - 6, 12, 12), 1.0, 3.1, 2)

    # One bare eye above the crooked rim. This single detail does more of the
    # "not okay" work than any amount of anatomy below it.
    _aaellipse(s, SCLERA, (cx + 2, cy - 5), 4, 3)
    d.circle(s, IRIS,     (cx + 3, cy - 5), 2)
    d.circle(s, (10, 4, 4), (cx + 3, cy - 5), 1)

    beak_pts = [(cx + 6, cy), (cx + 10, cy + 2), (cx + 8, cy + 6), (cx + 3, cy + 4)]
    d.polygon(s, BEAK,   beak_pts)
    d.polygon(s, BEAK_D, beak_pts, 1)

    # Glasses last so the fallen lens sits *over* the beak — that overlap is the
    # whole "they slipped" read.
    for lens in (left_lens, right_lens):
        d.circle(s, SHADE_FRAME, lens, 5)
        d.circle(s, SHADE_LENS,  lens, 4)
    d.circle(s, SHADE_GLINT, (left_lens[0] - 2, left_lens[1] - 2), 1)
    # Frame bar canted ~10°, the giveaway that nothing is sitting straight.
    d.line(s, SHADE_FRAME, (cx - 9, cy - 6), (cx + 7, cy - 3), 1)
    # Temple arm hanging loose off the face.
    d.line(s, SHADE_FRAME, (cx - 8, cy - 3), (cx - 12, cy), 1)

    if droop_deg:
        s = pygame.transform.rotate(s, -droop_deg)
    return s


def _build_hurt_frame(wing_angle_deg):
    frame_map = {10: 0, -5: 1, -20: 2, -35: 3}
    fidx      = frame_map.get(int(round(wing_angle_deg)), 0)

    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    d    = pygame.draw

    # --- TAIL (3 feathers, reach pulled in 30% about the rump) ---
    # The fan is where the hull loses most of its width; cutting it is what
    # takes the silhouette from 61 px to the high 40s without shrinking the bird
    # into the Shrink power-up's visual territory.
    def _t(px, py):
        return (20 + (px - 20) * 0.66, py + 4)

    for i, c in enumerate(TAIL_COLORS):
        d.polygon(surf, c, [
            _t(2 + i * 3, 26 + i * 2), _t(14 + i, 24 + i),
            _t(20 + i, 30 + i * 2), _t(6 + i * 3, 36 + i * 2),
        ])
    d.line(surf, TAIL_LINE, _t(4, 27), _t(18, 31), 1)
    d.line(surf, TAIL_LINE, _t(6, 33), _t(20, 35), 1)

    # --- BODY (0.82 of healthy — deliberately NOT the 0.6 Shrink signature) ---
    _aaellipse(surf, BODY_SHADOW, (_BODY_C[0] + 1, _BODY_C[1] + 2), _BODY_RX, _BODY_RY)
    _aaellipse(surf, BODY,        _BODY_C,                          _BODY_RX, _BODY_RY)
    _aaellipse(surf, CHEST,       (30, 32), 11, 6)
    _aaellipse(surf, BELLY,       (28, 41), 10, 5)

    # --- RIBS ---
    # Three bands at a 5-px pitch. Four at 3 px moiréd into a grey smear once
    # the sprite was downscaled to 1x; three at 5 px stay countable. Drawn on
    # their own layer and min-blended against a body-shaped stencil so the wider
    # bands can't float outside the silhouette.
    ribs = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    for (rcx, rcy, rrx, rc) in ((37, 30, 8, RIB_TOP),
                                (36, 35, 7, RIB_MID),
                                (35, 40, 6, RIB_LOW)):
        d.arc(ribs, rc, (rcx - rrx, rcy - 4, rrx * 2, 8),
              math.radians(200), math.radians(340), 1)
    stencil = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    _aaellipse(stencil, (255, 255, 255, 255), _BODY_C, _BODY_RX, _BODY_RY)
    ribs.blit(stencil, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(ribs, (0, 0))

    # --- WING ---
    # Seated low and back of the shoulder so the head can't eat the membrane.
    wing = _build_wing(wing_angle_deg)
    surf.blit(wing, wing.get_rect(center=(24, 25)).topleft)

    # --- HEAD (8° further nose-down each frame) ---
    head = _build_head(fidx * 8)
    surf.blit(head, head.get_rect(center=_HEAD_C).topleft)

    # --- FEET ---
    # Toes keep their healthy reach while the legs start higher up the emptier
    # body, so they read as spindly rather than as detached strokes.
    d.line(surf, FOOT, (28, 43), (26, 50), 2)
    d.line(surf, FOOT, (34, 43), (36, 50), 2)

    return surf


if __name__ == "__main__":
    OUT_DIR = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(OUT_DIR, exist_ok=True)

    raw    = [_build_hurt_frame(a) for a in _HURT_ANGLES]
    frames = [_add_outline(f) for f in raw]
    fw, fh = frames[0].get_size()
    scale  = 4
    margin, gap, label_h = 20, 8, 30

    canvas_w = margin + len(frames) * fw * scale + (len(frames) - 1) * gap + margin
    canvas_h = margin + label_h + gap + fh * scale + margin
    canvas   = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((8, 8, 20))

    try:
        font = pygame.font.SysFont("dejavusans", 16)
    except Exception:
        font = pygame.font.Font(None, 16)
    lbl = font.render("gaunt — round 2", True, (220, 220, 240))
    canvas.blit(lbl, (margin, margin + (label_h - lbl.get_height()) // 2))

    for i, frame in enumerate(frames):
        big = pygame.transform.scale(frame, (fw * scale, fh * scale))
        canvas.blit(big, (margin + i * (fw * scale + gap), margin + label_h + gap))

    pygame.image.save(canvas, os.path.join(OUT_DIR, "round_2.png"))

    # --- verification ---
    for i, f in enumerate(raw):
        opaque = 0
        minx, maxx = 999, -1
        ribpx = 0
        for x in range(SPRITE_W):
            for y in range(SPRITE_H):
                r, g, b, a = f.get_at((x, y))
                if a > 0:
                    opaque += 1
                    minx, maxx = min(minx, x), max(maxx, x)
                    if 55 < r < 80 and g < 20:
                        ribpx += 1
        nowing = _build_hurt_frame(_HURT_ANGLES[i])
        # diff against a wingless rebuild to count what the membrane actually
        # contributes after the head and body have had their turn
        wing_px = 0
        bare = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
        bare.blit(f, (0, 0))
        print(f"frame {i}: opaque={opaque}  width={maxx - minx + 1}  ribpx={ribpx}")

    # wing visibility measured by rebuilding each frame without the wing blit
    import types
    src_wing = _build_wing
    for i, ang in enumerate(_HURT_ANGLES):
        globals()['_build_wing'] = lambda a: pygame.Surface((1, 1), pygame.SRCALPHA)
        no_w = _build_hurt_frame(ang)
        globals()['_build_wing'] = src_wing
        with_w = _build_hurt_frame(ang)
        diff = sum(1 for x in range(SPRITE_W) for y in range(SPRITE_H)
                   if with_w.get_at((x, y)) != no_w.get_at((x, y)))
        print(f"frame {i}: visible wing px={diff}")

    print(f"Saved round_2.png {canvas_w}x{canvas_h}")
