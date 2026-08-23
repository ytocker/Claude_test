"""
`corrupted` — hurt-parrot concept exploration (standalone, not wired in).

The premise is that the *sprite* is damaged, not the bird. The frame is built
healthy, then one horizontal scan band across the chest is torn sideways with
the RGB channels pulled apart, and the single aviator lens is displaced a few
pixels off its socket with a cyan ghost left behind at the true position.
Damage therefore reads as a rendering failure — the one hurt language that
can't be mistaken for a decal stuck on a parrot.

Round 2 rebuilds the corruption to survive rotation. The bird tilts +-40 deg
in play, so any stripe that owns a large share of the sprite stops reading as
a scanline and starts reading as a diagonal paint stroke. The corruption is
therefore rationed: ONE band, blended at ~40% so the body form shows straight
through it, clipped inside the silhouette and short of the beak, plus a single
displaced-eye artifact. Two small tells that stay legible at any angle beat six
large ones that only work at 0 deg.

Everything is procedural; numpy is used only as a fast pixel-array shim over
pygame.surfarray, which ships with pygame on both build targets.
"""
import os

os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "offscreen"

import numpy as np
import pygame

pygame.init()

SPRITE_W, SPRITE_H = 64, 60
_HURT_ANGLES = (10, -5, -20, -35)
_FRAME_MAP = {10: 0, -5: 1, -20: 2, -35: 3}

# Uneven per-frame displacement is what sells "unstable signal" — an equal
# shift every frame would read as a deliberate static pattern instead.
_SHIFTS = (10, 8, 12, 6)

CYAN = (38, 240, 220)
GHOST_CYAN = (0, 220, 200)
MAGENTA = (255, 0, 160)

# One band only, sat on the chest/wing junction: the most legible tear position
# and the only place a horizontal artifact still reads as a scanline once the
# sprite is rotated. Everything right of BAND_X_MAX is off limits so the beak —
# the silhouette cue that says "bird" — is never touched.
_BAND = (27, 34)
BAND_X_MAX = 48

# Tear opacity. Full pixel replacement erased the body underneath; at ~40% the
# displaced data reads as interference laid over an intact parrot.
_TEAR_ALPHA = 102
_TEAR_ADD = 0.16

EYE_ANCHOR = (46, 20)
EYE_SHIFT = 4
EYE_ECHO_SHIFT = 5


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


def _apply_glitch_band(surf, shift):
    """Tear ONE chest band sideways with the colour channels separated.

    The tear is composited *over* the untouched sprite instead of replacing it,
    and the alpha channel is left alone entirely — the silhouette stays a clean
    parrot, which is what keeps the read honest once the bird is rotated. Red
    leads and blue lags the green shift by 3 px, which is real chromatic
    aberration rather than a fringe painted on afterwards. The roll happens
    inside the x < BAND_X_MAX slice so nothing can wrap onto the beak.
    """
    r0, r1 = _BAND
    rgb = pygame.surfarray.array3d(surf).astype(np.uint8)
    alpha = pygame.surfarray.array_alpha(surf)

    band = rgb[:BAND_X_MAX, r0:r1 + 1, :].copy()
    for chan, lag in ((0, 3), (1, 0), (2, -3)):
        band[:, :, chan] = np.roll(band[:, :, chan], shift + lag, axis=0)

    tear = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    trgb = pygame.surfarray.pixels3d(tear)
    ta = pygame.surfarray.pixels_alpha(tear)
    trgb[:BAND_X_MAX, r0:r1 + 1, :] = band
    # Masking the tear by the *host* alpha is what keeps the corruption inside
    # the bird: displaced data never sprays out into the sky.
    ta[:BAND_X_MAX, r0:r1 + 1] = np.where(
        alpha[:BAND_X_MAX, r0:r1 + 1] > 8, _TEAR_ALPHA, 0).astype(np.uint8)
    del trgb, ta

    surf.blit(tear, (0, 0))

    glow = tear.copy()
    grgb = pygame.surfarray.pixels3d(glow)
    grgb[:] = (grgb.astype(np.float32) * _TEAR_ADD).astype(np.uint8)
    del grgb
    surf.blit(glow, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    # Only 2 px of the whole sprite carry full-contrast corruption colour, so
    # the fringe can stay saturated without swamping the macaw palette.
    for x in range(BAND_X_MAX):
        if alpha[x, r0] > 8:
            surf.set_at((x, r0), CYAN)
        if alpha[x, r1] > 8:
            surf.set_at((x, r1), MAGENTA)
    # Hard vertical nick where the tear stops: real datamosh has a clip edge,
    # and it doubles as the visual promise that nothing reaches the beak.
    for y in range(r0, r1 + 1):
        if alpha[BAND_X_MAX - 1, y] > 8:
            surf.set_at((BAND_X_MAX - 1, y), CYAN)
    return surf


def _build_wing(angle_deg):
    WING = (35, 85, 210)
    WING_D = (18, 45, 145)
    TIP = (45, 200, 90)
    STRIPE = (240, 185, 50)
    HL = (155, 198, 248)
    w = pygame.Surface((50, 50), pygame.SRCALPHA)
    d = pygame.draw
    d.polygon(w, (0, 0, 0, 110), [(24, 26), (46, 14), (50, 30), (34, 44), (18, 40)])
    d.polygon(w, WING, [(24, 24), (44, 13), (48, 28), (32, 42), (18, 36)])
    d.polygon(w, WING_D, [(24, 24), (32, 42), (18, 36)])
    d.polygon(w, TIP, [(44, 13), (50, 18), (48, 28)])
    d.polygon(w, STRIPE, [(42, 18), (48, 22), (46, 28), (40, 24)])
    d.line(w, WING_D, (26, 25), (42, 18), 2)
    d.line(w, WING_D, (28, 30), (44, 25), 2)
    d.line(w, WING_D, (30, 34), (46, 32), 2)
    d.line(w, HL, (25, 25), (41, 15), 1)
    return pygame.transform.rotate(w, angle_deg)


def _build_lens(r=6):
    """A single aviator lens on its own surface, so it can be displaced whole."""
    size = r * 2 + 3
    lens = pygame.Surface((size, size), pygame.SRCALPHA)
    c = (r + 1, r + 1)
    pygame.draw.circle(lens, (255, 200, 50), c, r)
    pygame.draw.circle(lens, (16, 16, 22), c, r - 1)
    tint = pygame.Surface((r * 2 - 2, r - 1), pygame.SRCALPHA)
    pygame.draw.ellipse(tint, (35, 55, 90, 150), tint.get_rect())
    lens.blit(tint, (c[0] - r + 1, c[1] - r + 2))
    pygame.draw.circle(lens, (255, 255, 255), (c[0] - 2, c[1] - 2), 2)
    pygame.draw.circle(lens, (255, 255, 255, 200), (c[0] + 2, c[1] + 2), 1)
    return lens


def _draw_displaced_eye(surf):
    """The one face artifact: the lens has slid right off its own socket.

    Read order left-to-right is empty socket -> cyan outline of where the lens
    should be -> the lens itself -> a cyan trailing sliver. That is the whole
    grammar of a horizontal pixel shift, delivered in about 200 px, and it
    survives rotation because it is a compact cluster rather than a stripe.
    """
    ax, ay = EYE_ANCHOR
    lens = _build_lens()
    off = lens.get_width() // 2

    # Dark socket first: the lens took its pixels with it and left a hole.
    pygame.draw.circle(surf, (26, 14, 18), (ax, ay), 5)

    ghost = pygame.Surface(lens.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(ghost, (*GHOST_CYAN, 190), (off, off), 5, 1)
    surf.blit(ghost, (ax - off, ay - off))

    # Cyan-tinted duplicate of the eye content one step further right than the
    # lens itself, so only a trailing sliver survives — a smear, not a twin.
    echo = lens.copy()
    echo.fill((0, 210, 200, 90), special_flags=pygame.BLEND_RGBA_MULT)
    echo.set_alpha(72)
    surf.blit(echo, (ax - off + EYE_ECHO_SHIFT, ay - off))

    surf.blit(lens, (ax - off + EYE_SHIFT, ay - off))


def _build_hurt_frame(wing_angle_deg):
    fidx = _FRAME_MAP.get(int(round(wing_angle_deg)), 0)
    shift = _SHIFTS[fidx]

    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    d = pygame.draw

    BODY = (190, 42, 42)
    BODY_SH = (162, 26, 26)
    CHEST = (232, 70, 64)
    BELLY = (234, 76, 36)
    BEAK = (240, 170, 0)
    BEAK_D = (190, 125, 0)

    # Palette sits a step off the healthy macaw's — the flatter, slightly
    # washed reds read as a badly re-encoded texture before any glitch lands.
    for i, tc in enumerate(((196, 30, 34), (224, 70, 34),
                            (242, 152, 48), (248, 212, 74))):
        d.polygon(surf, tc, [
            (2 + i * 3, 26 + i * 2), (14 + i, 24 + i),
            (20 + i, 30 + i * 2), (6 + i * 3, 36 + i * 2),
        ])
    d.line(surf, BODY_SH, (4, 27), (18, 31), 1)
    d.line(surf, BODY_SH, (6, 33), (20, 35), 1)

    _aaellipse(surf, BODY_SH, (34, 35), 19, 14)
    _aaellipse(surf, BODY, (32, 32), 19, 14)
    _aaellipse(surf, CHEST, (30, 29), 13, 8)
    _aaellipse(surf, BELLY, (28, 38), 12, 6)

    wing = _build_wing(wing_angle_deg)
    surf.blit(wing, wing.get_rect(center=(34, 28)).topleft)

    _aaellipse(surf, (164, 24, 26), (48, 23), 12, 11)
    _aaellipse(surf, BODY, (47, 21), 12, 11)
    _aaellipse(surf, (236, 96, 88), (44, 24), 4, 3)
    _aaellipse(surf, (235, 158, 158), (46, 16), 7, 3)

    beak_pts = [(55, 21), (61, 24), (58, 28), (52, 26)]
    d.polygon(surf, BEAK, beak_pts)
    d.polygon(surf, BEAK_D, beak_pts, 1)
    d.line(surf, (255, 220, 140), (55, 22), (59, 24), 1)

    d.line(surf, BEAK_D, (28, 45), (26, 49), 2)
    d.line(surf, BEAK_D, (34, 45), (36, 49), 2)

    surf = _apply_glitch_band(surf, shift)

    # Stamped after the tear so the artifact stays pinned to the face; the eye
    # is the one place the corruption has to be unambiguous at 1x.
    _draw_displaced_eye(surf)

    return surf


def _sky_patch(w, h):
    """Stand-in for the in-game sky, so the 1x read can be judged in context."""
    s = pygame.Surface((w, h))
    for y in range(h):
        t = y / max(1, h - 1)
        s.fill((int(96 + 60 * t), int(158 + 50 * t), int(214 + 24 * t)),
               (0, y, w, 1))
    return s


def _count(surf, pred):
    a = pygame.surfarray.array3d(surf).astype(np.int16)
    al = pygame.surfarray.array_alpha(surf)
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    return int(np.count_nonzero(pred(r, g, b) & (al > 8)))


if __name__ == "__main__":
    OUT_DIR = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(OUT_DIR, exist_ok=True)

    raw = [_build_hurt_frame(a) for a in _HURT_ANGLES]
    frames = [_add_outline(f) for f in raw]
    fw, fh = frames[0].get_size()
    scale, margin, gap, label_h = 4, 20, 8, 30

    tilts = (-41, 0, 27)
    tscale = 3
    tile_w = int((fw ** 2 + fh ** 2) ** 0.5) + 4

    canvas_w = margin * 2 + len(frames) * fw * scale + (len(frames) - 1) * gap
    row2_h = fh * 2 + 12
    row3_h = tile_w * tscale
    canvas_h = (margin + label_h + gap + fh * scale + gap + label_h
                + gap + row2_h + gap + label_h + gap + row3_h + margin)
    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((8, 8, 20))

    try:
        font = pygame.font.SysFont("dejavusans", 16)
        small = pygame.font.SysFont("dejavusans", 13)
    except Exception:
        font = pygame.font.Font(None, 16)
        small = pygame.font.Font(None, 14)

    lbl = font.render("corrupted — round 2  |  4x flap cycle", True, (220, 220, 240))
    canvas.blit(lbl, (margin, margin + (label_h - lbl.get_height()) // 2))

    top = margin + label_h + gap
    for i, frame in enumerate(frames):
        canvas.blit(pygame.transform.scale(frame, (fw * scale, fh * scale)),
                    (margin + i * (fw * scale + gap), top))

    y2 = top + fh * scale + gap
    lbl2 = font.render("scale check — 2x and 1x over sky", True, (220, 220, 240))
    canvas.blit(lbl2, (margin, y2 + (label_h - lbl2.get_height()) // 2))

    y3 = y2 + label_h + gap
    patch = _sky_patch(canvas_w - margin * 2, row2_h)
    canvas.blit(patch, (margin, y3))
    x = margin + 10
    for frame in frames:
        canvas.blit(pygame.transform.scale(frame, (fw * 2, fh * 2)), (x, y3 + 6))
        x += fw * 2 + gap
    x += 24
    for frame in frames:
        canvas.blit(frame, (x, y3 + 6 + fh // 2))
        x += fw + gap
    canvas.blit(small.render("2x", True, (24, 40, 70)), (margin + 10, y3 + 2))

    y4 = y3 + row2_h + gap
    lbl3 = font.render("TILT CHECK — frame 0 at the game's dive/climb angles",
                       True, (255, 210, 120))
    canvas.blit(lbl3, (margin, y4 + (label_h - lbl3.get_height()) // 2))

    y5 = y4 + label_h + gap
    tx = margin
    for ang in tilts:
        rot = pygame.transform.rotate(frames[0], ang)
        tile = pygame.Surface((tile_w, tile_w), pygame.SRCALPHA)
        tile.blit(rot, rot.get_rect(center=(tile_w // 2, tile_w // 2)))
        canvas.blit(pygame.transform.scale(tile, (tile_w * tscale, tile_w * tscale)),
                    (tx, y5))
        canvas.blit(small.render(f"{ang:+d}°", True, (200, 200, 220)),
                    (tx + 4, y5 + 4))
        tx += tile_w * tscale + gap
    # 1x row of the same tilts: the angles have to survive the size they ship at.
    for ang in tilts:
        rot = pygame.transform.rotate(frames[0], ang)
        canvas.blit(rot, (tx, y5 + row3_h // 2 - rot.get_height() // 2))
        tx += rot.get_width() + gap

    out_path = os.path.join(OUT_DIR, "round_2.png")
    pygame.image.save(canvas, out_path)
    print(f"Saved {canvas_w}x{canvas_h} -> {out_path}")

    probe = raw[0]
    print("bird-red   :", _count(probe, lambda r, g, b: (r > 150) & (g < 80)))
    print("cyan fringe:", _count(probe, lambda r, g, b: (r < 50) & (g > 180) & (b > 150)))
    print("ghost eye  :", _count(probe, lambda r, g, b: (r < 30) & (g > 150) & (b > 150)))
