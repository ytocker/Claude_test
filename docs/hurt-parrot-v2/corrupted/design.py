"""
`corrupted` — hurt-parrot concept exploration (standalone, not wired in).

The premise is that the *sprite* is damaged, not the bird. Rather than paint
injury onto a healthy macaw, the frame is built and then destroyed: horizontal
scan bands are torn sideways with the RGB channels pulled apart, the eyes are
overwritten by raw bitmap artifacts (a white no-data void and a black dead
block), and the beak leaves a ghost echo where the blit landed twice. Damage is
therefore readable as a rendering failure — the one hurt language that can't be
mistaken for a decal stuck on a parrot.

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

CYAN = (0, 240, 220)
MAGENTA = (255, 0, 160)
VOID = (255, 255, 255)
DEAD = (5, 5, 5)

# Bands are placed to bisect the three silhouette masses (head/shoulder, mid
# body under the wing, belly) so no single mass survives intact.
_BANDS = ((12, 19), (27, 34), (43, 50))


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


def _apply_glitch_bands(surf, shift):
    """Tear three horizontal bands sideways with the colour channels separated.

    The alpha channel is displaced along with the pixels, so the *silhouette*
    breaks too — that is the part that survives the 1x downscale and the later
    outline pass. Red leads and blue lags the green shift by 3 px, which is
    real chromatic aberration rather than a fringe painted on afterwards.
    """
    rgb = pygame.surfarray.array3d(surf).astype(np.uint8)
    alpha = pygame.surfarray.array_alpha(surf).astype(np.uint8)

    for r0, r1 in _BANDS:
        band_rgb = rgb[:, r0:r1 + 1, :]
        band_a = alpha[:, r0:r1 + 1]
        for chan, lag in ((0, 3), (1, 0), (2, -3)):
            band_rgb[:, :, chan] = np.roll(band_rgb[:, :, chan], shift + lag, axis=0)
        rgb[:, r0:r1 + 1, :] = band_rgb
        alpha[:, r0:r1 + 1] = np.roll(band_a, shift, axis=0)

    # blit_array only accepts a matching-format surface, so the RGB plane is
    # staged on a plain surface and the recovered alpha is stamped back on.
    plane = pygame.Surface((SPRITE_W, SPRITE_H))
    pygame.surfarray.blit_array(plane, rgb)
    out = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    out.blit(plane, (0, 0))
    pygame.surfarray.pixels_alpha(out)[:] = alpha

    # The fringe lines run the full frame width, past the bird's edges: the
    # corruption belongs to the render target, not to the parrot.
    for r0, r1 in _BANDS:
        pygame.draw.line(out, CYAN, (0, r0), (SPRITE_W - 1, r0), 1)
        pygame.draw.line(out, MAGENTA, (0, r1), (SPRITE_W - 1, r1), 1)
    return out


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


def _build_hurt_frame(wing_angle_deg):
    fidx = _FRAME_MAP.get(int(round(wing_angle_deg)), 0)
    shift = _SHIFTS[fidx]

    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    d = pygame.draw

    BODY = (190, 42, 42)
    BODY_SH = (130, 20, 20)
    CHEST = (230, 88, 88)
    BELLY = (235, 155, 42)
    BEAK = (240, 170, 0)
    BEAK_D = (190, 125, 0)

    # Palette sits a step off the healthy macaw's — the flatter, slightly
    # washed reds read as a badly re-encoded texture before any glitch lands.
    for i, tc in enumerate(((188, 28, 36), (225, 88, 36),
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

    _aaellipse(surf, (138, 18, 20), (48, 23), 12, 11)
    _aaellipse(surf, BODY, (47, 21), 12, 11)
    _aaellipse(surf, (235, 110, 110), (44, 24), 4, 3)
    _aaellipse(surf, (235, 158, 158), (46, 16), 7, 3)

    beak_pts = [(55, 21), (61, 24), (58, 28), (52, 26)]
    d.polygon(surf, BEAK, beak_pts)
    d.polygon(surf, BEAK_D, beak_pts, 1)
    d.line(surf, (255, 220, 140), (55, 22), (59, 24), 1)

    d.line(surf, BEAK_D, (28, 45), (26, 49), 2)
    d.line(surf, BEAK_D, (34, 45), (36, 49), 2)

    surf = _apply_glitch_bands(surf, shift)

    # Ghost beak. A straight +10 px echo would fall off a 64 px frame and read
    # as nothing, so the duplicate lands down-right instead: same displacement
    # magnitude, but it hangs clear of the head where the doubling is legible.
    echo = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    ghost = [(x + 3, y + 9) for x, y in beak_pts]
    d.polygon(echo, (*BEAK, 160), ghost)
    d.polygon(echo, (*CYAN, 160), ghost, 1)
    surf.blit(echo, (0, 0))

    # Eyes are stamped after the tear so they stay pinned while the head slides
    # out from under them — the face is the one place the corruption must be
    # unambiguous, so both are raw blocks rather than anything eye-shaped.
    d.circle(surf, VOID, (46, 20), 7)
    d.rect(surf, DEAD, (50, 13, 12, 12))

    d.line(surf, CYAN, (5, 8), (13, 8), 1)
    d.line(surf, MAGENTA, (45, 52), (53, 52), 1)
    for y in range(5, 56, 2):
        surf.set_at((52, y), DEAD)

    return surf


def _sky_patch(w, h):
    """Stand-in for the in-game sky, so the 1x read can be judged in context."""
    s = pygame.Surface((w, h))
    for y in range(h):
        t = y / max(1, h - 1)
        s.fill((int(96 + 60 * t), int(158 + 50 * t), int(214 + 24 * t)),
               (0, y, w, 1))
    return s


if __name__ == "__main__":
    OUT_DIR = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(OUT_DIR, exist_ok=True)

    frames = [_add_outline(_build_hurt_frame(a)) for a in _HURT_ANGLES]
    fw, fh = frames[0].get_size()
    scale, margin, gap, label_h = 4, 20, 8, 30

    canvas_w = margin * 2 + len(frames) * fw * scale + (len(frames) - 1) * gap
    row2_h = fh * 2 + 12
    canvas_h = (margin + label_h + gap + fh * scale + gap + label_h
                + gap + row2_h + margin)
    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((8, 8, 20))

    try:
        font = pygame.font.SysFont("dejavusans", 16)
        small = pygame.font.SysFont("dejavusans", 13)
    except Exception:
        font = pygame.font.Font(None, 16)
        small = pygame.font.Font(None, 14)

    lbl = font.render("corrupted — round 1  |  4x flap cycle", True, (220, 220, 240))
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

    out_path = os.path.join(OUT_DIR, "round_1.png")
    pygame.image.save(canvas, out_path)
    print(f"Saved {canvas_w}x{canvas_h} -> {out_path}")
