"""Render the Genie Lamp full activation sequence:
  1. pre   — Pip flying with parcel intact
  2. open  — parcel splits in two; the brass genie lamp emerges between
             the halves with a mauve smoke plume
  3. taken — Pip absorbs the lamp; "GENIE!" gold text floats above
  4. wishes — final standalone frame showing the 3 offer powerups
              spread across the play field ahead of Pip

Frames 2 and 3 are STAGED (the game doesn't actually split the parcel
at runtime — the parcel is permanent). The split is rendered for the
screenshot only: two clipped halves of the live parcel sprite are
drawn shifted apart with the lamp painted in the gap.

Produces 5 PNGs under docs/screenshots/genie_sequence/:
  00_contact_sheet.png — all four frames side-by-side
  01_pre.png           — Pip + parcel intact
  02_open.png          — parcel splits, lamp emerges
  03_taken.png         — lamp absorbed, GENIE! text
  04_wishes.png        — 3 offer powerups spread out

Run from repo root:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python -m tools.render_genie_sequence
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import math
import random
import pygame

pygame.init()
pygame.display.set_mode((360, 640))

from game.config import W, H, GROUND_Y
from game import biome as _biome
from game.draw import (
    get_sky_surface_biome, draw_mountains, draw_cloud, draw_ground,
)
from game.world import World
from game.entities import PowerUp, FloatText, Particle
from game import parrot


OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                       "docs", "screenshots", "genie_sequence")
os.makedirs(OUT_DIR, exist_ok=True)


def render_bg(world, target):
    """Sky / clouds / mountains / ground only — entities composited
    separately so we can stage the parcel split on top."""
    phase = world.biome_phase
    pal = _biome.palette_for_phase(phase)
    buckets = _biome.PHASE_BUCKETS
    bucket_f = (phase % 1.0) * buckets
    a = int(bucket_f) % buckets
    sky = get_sky_surface_biome(W, H, GROUND_Y, pal, a)
    target.blit(sky, (0, 0))
    for bx, by, sc, variant in (
            (40, 80, 0.9, 0), (220, 110, 1.0, 2), (110, 180, 0.8, 3)):
        draw_cloud(target, bx, by, sc, variant=variant)
    draw_mountains(target, world.bg_scroll, GROUND_Y, W,
                   pal["mtn_far"], pal["mtn_near"])
    draw_ground(target, GROUND_Y, W, H, world.bg_scroll,
                pal["ground_top"], pal["ground_mid"], (60, 40, 25))


def draw_split_parcel(target, cx, cy, split_t):
    """Render the standard parcel sprite as two halves shifted apart by
    `split_t` (0 = closed, 1 = wide open). Each half is a clipped copy
    of the live parcel surface so the cut reads as 'parcel opening
    sideways like clamshell halves'. `cx,cy` is the parcel's centre
    when closed. Halves tilt outward so the silhouette reads as
    'opening lid'. The closed parcel sprite is narrower than the open
    halves so the closed silhouette is naturally covered."""
    parcel = parrot.get_parcel("normal")
    pw, ph = parcel.get_size()
    # Scale halves up slightly to make the open silhouette more
    # dramatic than the closed one.
    SCALE = 1.15
    sw, sh = int(pw * SCALE), int(ph * SCALE)
    parcel = pygame.transform.smoothscale(parcel, (sw, sh))
    # Left half — clip the right side
    left = pygame.Surface((sw // 2 + 2, sh), pygame.SRCALPHA)
    left.blit(parcel, (0, 0))
    # Right half — clip the left side
    right = pygame.Surface((sw - sw // 2 + 2, sh), pygame.SRCALPHA)
    right.blit(parcel, (-(sw // 2 - 2), 0))
    # Tilt the halves outward — much more dramatic at full split.
    angle = split_t * 35.0
    left  = pygame.transform.rotate(left,  +angle)
    right = pygame.transform.rotate(right, -angle)
    # Offset each half outward and slightly down (clamshell pivot).
    dx = int(10 + split_t * 22)
    dy = int(split_t * 4)
    target.blit(left,  left.get_rect(center=(cx - dx, cy + dy)))
    target.blit(right, right.get_rect(center=(cx + dx, cy + dy)))
    # Bright sparkle line connecting the two halves (the "magic seam").
    if split_t > 0.3:
        seam_alpha = int(180 * split_t)
        seam = pygame.Surface((int(dx * 2), 6), pygame.SRCALPHA)
        pygame.draw.line(seam, (255, 240, 180, seam_alpha),
                         (0, 3), (seam.get_width() - 1, 3), 2)
        target.blit(seam, seam.get_rect(center=(cx, cy - 2)))


def draw_emerging_lamp(target, cx, cy, t):
    """Paint the genie lamp at (cx, cy) using the standard PowerUp
    genie draw. `t` 0..1 controls the emerge: at 0 the lamp is small
    and dim, at 1 it's at full scale. Smoke wisps trail upward."""
    # First — paint a bright cream/gold halo behind so the lamp pops
    # off the sky no matter the biome palette.
    halo_r = int(28 + 12 * t)
    for r, alpha in ((halo_r, 80), (halo_r - 6, 120), (halo_r - 14, 170)):
        if r <= 0:
            continue
        halo = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(halo, (255, 240, 180, alpha),
                           (r + 2, r + 2), r)
        target.blit(halo, (cx - r - 2, cy - r - 2))
    # Build a temporary PowerUp and draw to a buffer so we can scale.
    # Slightly bigger than in-world so the lamp reads clearly, but
    # not so big it covers Pip in the staged screenshot.
    SCALE = (0.80 + 0.70 * t) * 1.15
    buf = pygame.Surface((96, 96), pygame.SRCALPHA)
    pup = PowerUp(48, 48, kind="genie")
    pup.pulse = 1.2 + t * 1.5
    pup.draw(buf)
    bw, bh = buf.get_size()
    if abs(SCALE - 1.0) > 0.01:
        buf = pygame.transform.smoothscale(
            buf, (max(1, int(bw * SCALE)), max(1, int(bh * SCALE))))
    # Drop shadow so the lamp pops off the bird sprite.
    shadow = pygame.Surface(buf.get_size(), pygame.SRCALPHA)
    shadow.fill((0, 0, 0, 0))
    for sx, sy in ((-1, 1), (1, 1), (0, 2)):
        sh = buf.copy()
        sh.fill((0, 0, 0, 90), special_flags=pygame.BLEND_RGBA_MULT)
        shadow.blit(sh, (sx, sy))
    target.blit(shadow,
                shadow.get_rect(center=(cx, cy)).topleft)
    rect = buf.get_rect(center=(cx, cy))
    target.blit(buf, rect.topleft)
    # Extra smoke wisps spreading upward — bigger + more of them.
    for i in range(int(14 * t)):
        wx = cx + math.sin(i * 0.55 + t * 4) * 26
        wy = cy - 26 - i * 6
        r = max(3, int(8 - i * 0.4))
        a = max(0, 180 - i * 12)
        puff = pygame.Surface((r * 2 + 6, r * 2 + 6), pygame.SRCALPHA)
        pygame.draw.circle(puff, (170, 130, 195, a),
                           (r + 3, r + 3), r)
        target.blit(puff, (int(wx - r - 3), int(wy - r - 3)))


def render_bird(world, target):
    """Pip on top of the scene."""
    world.bird.draw(target, flipped=False)


def render_powerups(world, target):
    for m in world.powerups:
        m.draw(target)


def render_floats_particles(world, target):
    for p in world.particles:
        p.draw(target)
    for t in world.float_texts:
        t.draw(target)


def save(surf, name, label=None):
    out = surf.copy()
    if label:
        font = pygame.font.SysFont("Arial", 14, bold=True)
        img = font.render(label, True, (255, 255, 255))
        bg = pygame.Surface((img.get_width() + 12, img.get_height() + 6),
                            pygame.SRCALPHA)
        bg.fill((0, 0, 0, 150))
        out.blit(bg, (6, 6))
        out.blit(img, (12, 9))
    path = os.path.join(OUT_DIR, name)
    pygame.image.save(out, path)
    print(f"  saved {path}")
    return out


def make_contact_sheet(frames, name):
    margin = 10
    sw = (W * 3) // 4
    sh = (H * 3) // 4
    total_w = sw * len(frames) + margin * (len(frames) + 1)
    total_h = sh + margin * 2
    sheet = pygame.Surface((total_w, total_h))
    sheet.fill((24, 22, 36))
    for i, fr in enumerate(frames):
        small = pygame.transform.smoothscale(fr, (sw, sh))
        sheet.blit(small, (margin + i * (sw + margin), margin))
    path = os.path.join(OUT_DIR, name)
    pygame.image.save(sheet, path)
    print(f"  saved {path}")


def setup_world():
    random.seed(11)
    w = World()
    w.ready_t = 0
    w.score = 600  # unlock all genie offer kinds
    # Daytime phase so the sky is bright and the lamp brass reads.
    w.biome_time = _biome.CYCLE_SECONDS * 0.08
    return w


def parcel_world_pos(world):
    """Return the (x, y) the parcel is drawn at on the current bird."""
    from game.config import PARCEL_Y_OFFSET
    # Match world.py's parcel-collision math: offset rotated by tilt.
    tilt = world.bird.tilt_deg
    off = pygame.math.Vector2(0, PARCEL_Y_OFFSET).rotate(-tilt)
    return world.bird.x + off.x, world.bird.y + off.y


def main():
    surf = pygame.Surface((W, H))
    frames = []

    # ── Frame 1: pre — Pip + parcel intact ────────────────────────
    w = setup_world()
    render_bg(w, surf)
    render_bird(w, surf)
    frames.append(save(surf, "01_pre.png",
                       "1: Pip flying with parcel"))

    # ── Frame 2: open — parcel splits, lamp emerges between halves ──
    w = setup_world()
    surf2 = pygame.Surface((W, H))
    render_bg(w, surf2)
    # Re-draw Pip but suppress the parcel — easiest hack: draw to a
    # surface, then paint the split parcel + lamp on top so they read
    # as replacing the parcel. Tricky bit: the default Bird.draw will
    # still draw the parcel. So we draw the bird first then composite
    # the split layer on top.
    render_bird(w, surf2)
    px, py = parcel_world_pos(w)
    # Cover the original parcel with a transparent rect so the split
    # version reads cleanly. Actually the split halves naturally cover
    # the closed parcel since they sit slightly above its centre line
    # — but to be safe we'll erase a small disc first.
    erase = pygame.Surface((38, 28), pygame.SRCALPHA)
    erase.fill((0, 0, 0, 0))
    # Re-draw the sky bit under the parcel area to "erase" the original
    sky_strip = pygame.Surface((40, 30), pygame.SRCALPHA)
    sky_strip.blit(surf2, (-int(px - 20), -int(py - 12)))
    # Actually simpler: just paint the split halves OVER the closed
    # parcel — the open silhouette is wider than the closed one so
    # the closed sprite sits hidden underneath.
    draw_split_parcel(surf2, int(px + 22), int(py + 4), split_t=1.0)
    # Lamp rises UP-AND-FORWARD from the parcel split so it doesn't
    # overlap Pip's body. Forward (+x) so Pip is clearly on the LEFT
    # of the lamp; up (-y) so the lamp sits above the open halves.
    draw_emerging_lamp(surf2, int(px + 26), int(py - 14), t=1.0)
    frames.append(save(surf2, "02_open.png",
                       "2: Parcel splits → genie lamp emerges"))

    # ── Frame 3: taken — lamp absorbed, GENIE! text, mauve puff ──
    w = setup_world()
    surf3 = pygame.Surface((W, H))
    render_bg(w, surf3)
    render_bird(w, surf3)
    # Small puff over Pip + lamp tracking upward into him.
    px, py = parcel_world_pos(w)
    draw_emerging_lamp(surf3, int(px), int(py - 14), t=0.4)
    # Burst of brass particles around Pip's chest
    for ang in range(0, 360, 24):
        r = pygame.Rect(0, 0, 5, 5)
        x = w.bird.x + math.cos(math.radians(ang)) * 16
        y = w.bird.y + math.sin(math.radians(ang)) * 16
        r.center = (int(x), int(y))
        pygame.draw.circle(surf3, (250, 215, 130), r.center, 3)
        pygame.draw.circle(surf3, (185, 130, 45), r.center, 2)
    # GENIE! text
    txt = FloatText(
        "GENIE!", w.bird.x, w.bird.y - 30, (250, 215, 130),
        size=30, life=1.3, vy=-32, style="powerup",
    )
    txt.update(0.25)  # mid-flight
    txt.draw(surf3)
    frames.append(save(surf3, "03_taken.png",
                       "3: Pip absorbs the lamp — GENIE!"))

    # ── Frame 4: wishes — 3 offers spread across the field ────────
    w = setup_world()
    w._activate_genie(PowerUp(w.bird.x, w.bird.y, kind="genie"))
    # The third offer spawns slightly off-screen-right (canvas is
    # 360 wide; furthest offer is at x=bird.x+200+2*60). Tick world
    # scroll for ~1s so it drifts into view — same path it'd take
    # during real gameplay.
    for _ in range(70):
        for m in w.powerups:
            if getattr(m, "is_genie_offer", False):
                m.x -= 160.0 / 60   # scroll speed at base, approximate
                m.update(1 / 60)
    # Advance the GENIE! text past its full lifetime so it's gone and
    # the topmost offer (which sits where the text was) is visible.
    for t in w.float_texts:
        t.update(2.0)
    w.float_texts = [t for t in w.float_texts if t.alive()]
    print("  Offer positions / kinds for wishes frame (after scroll):")
    for m in w.powerups:
        if getattr(m, "is_genie_offer", False):
            print(f"    {m.kind:12s} at ({m.x:.0f}, {m.y:.0f})")
    surf4 = pygame.Surface((W, H))
    render_bg(w, surf4)
    render_powerups(w, surf4)
    render_floats_particles(w, surf4)
    render_bird(w, surf4)
    frames.append(save(surf4, "04_wishes.png",
                       "4: 3 unique offers spread — pick one!"))

    # Contact sheet
    make_contact_sheet(frames, "00_contact_sheet.png")
    print("\nDone. Output in:", OUT_DIR)


if __name__ == "__main__":
    main()
