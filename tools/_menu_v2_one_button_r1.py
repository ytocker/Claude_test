"""
Main-menu concept `one-button`, round 1 — offline review render.

Thesis: a one-button game gets a one-button menu. START is the ONLY emitting
object on screen (a luminous gold disc); the utilities are dark recessive
"holes", i.e. the visual opposite of a call to action. Pip carries the parcel
and perches on the disc's upper-right arc so mascot + CTA read as ONE lockup.

Colour choices are driven by the measured `alpine_haze` contrast arithmetic:
scarlet alone is NOT phase-proof (1.1-1.6 against sky_bot for ~35% of the
cycle), so every element that must be seen is a TWO-TONE pair whose max leg
clears 3:1 at every keyframe — gold face + deep-scarlet ring on the disc, gold
fill + dark outline on the wordmark and labels.

Renders at four keyframes of the live 15-keyframe cycle, driven honestly off
`biome_time` -> `biome.phase_for_time` -> the same phase the sky, mountains and
foreground already consume. Nothing here is imported by the game; it writes
review PNGs under docs/ only.
"""
import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

pygame.init()
pygame.display.set_mode((360, 640))

from game import biome as _biome
from game import foreground, hud, parrot, sky_designs, store_data
from game.config import GROUND_Y, PARCEL_Y_OFFSET, H, W
from game.draw import draw_cloud, draw_mountains
from game.hud import (_AWSTAR_GOLD, _GOLD_BRIGHT, _GOLD_DEEP, _GOLD_PALE,
                      _coin_icon, _draw_gear, _draw_trophy, _font,
                      _outlined_text)

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "docs", "menu-v2", "one-button")

# The two-tone pair the whole screen is built on (see module docstring).
GOLD_LIT = (252, 214, 110)      # disc face, light side (upper-left)
GOLD_DEEP_FACE = (214, 158, 44)  # disc face, shadow side (lower-right)
SCARLET = (148, 20, 20)          # ring + START caps — the dark leg of the pair
SCARLET_EDGE = (96, 14, 14)
INK = (24, 26, 38)               # utility chips: the "holes"
INK_OUTLINE = (16, 14, 26)
# The shipped `_outlined_text` default outline is _RED_OUTLINE (168,32,16).
# Measured against the alpine_haze sky at the wordmark's height that leg only
# reaches ~2.0 at day/golden while the gold leg reaches ~2.1 — i.e. NEITHER leg
# clears 3:1 and the two-tone pair stops being phase-proof up there. A near-ink
# maroon keeps the same warm family and pushes the dark leg to >=4.8 at the two
# bright phases, so max(fill, outline) >= 3 at every keyframe.
WORDMARK_OUTLINE = (34, 16, 18)

DISC_C = (180, 320)
DISC_D = 158
DISC_R = DISC_D // 2

PIP_SCALE = 1.95
PIP_C = (232, 262)

CHIP_D = 56
PROFILE_D = 64
CHIP_CY = 488
LABEL_CY = 530
LABEL_SIZE = 12

PHASES = [("day", 0.12), ("golden", 0.27), ("plum", 0.47), ("night", 0.70)]

_CLOUD_SLOTS = ((20, 90, 0.9), (180, 140, 1.1), (60, 220, 0.8),
                (230, 60, 0.7), (320, 180, 0.9), (140, 40, 1.0))


# ── measurement ──────────────────────────────────────────────────────────────

def _lin(c):
    c /= 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(rgb):
    r, g, b = rgb[:3]
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def sample_mean(surf, points):
    acc = [0, 0, 0]
    for x, y in points:
        c = surf.get_at((int(x), int(y)))
        acc[0] += c[0]
        acc[1] += c[1]
        acc[2] += c[2]
    n = len(points)
    return tuple(v // n for v in acc)


def _brightest(surf, rect):
    best_l, best_c = -1.0, (0, 0, 0)
    for yy in range(rect.top, rect.bottom):
        for xx in range(rect.left, rect.right):
            c = surf.get_at((xx, yy))[:3]
            l = luminance(c)
            if l > best_l:
                best_l, best_c = l, c
    return best_c


# ── the disc (built once, blitted) ───────────────────────────────────────────

_disc_cache = {}


def _build_disc():
    """The gold disc: an eccentric value falloff (light upper-left) inside a
    deep-scarlet ring, with START stamped in the same scarlet. A FLAT gold
    circle reads as a record button at thumbnail size, so the falloff is
    load-bearing, not decoration. Supersampled once and cached — the live draw
    path would blit this, never re-rasterise it."""
    if "disc" in _disc_cache:
        return _disc_cache["disc"]
    SS = 3
    R = DISC_R * SS
    size = DISC_R * 2 + 2
    big = pygame.Surface((size * SS, size * SS), pygame.SRCALPHA)
    c = (size * SS) // 2

    # Eccentric value falloff: opaque concentric circles centred on the LIGHT
    # point, largest/deepest first, so each pixel ends up coloured by its
    # distance from the light rather than from the disc centre. Drawn opaque
    # (pygame.draw does not alpha-blend onto SRCALPHA, it overwrites) and then
    # masked back to the disc — no per-pixel work anywhere.
    lx, ly = c - int(R * 0.30), c - int(R * 0.32)
    r_max = int(R * 1.46)
    steps = 128
    for k in range(steps):
        t = k / (steps - 1)
        rad = int(round(r_max * (1.0 - t)))
        if rad <= 0:
            continue
        col = tuple(int(round(a + (b - a) * t))
                    for a, b in zip(GOLD_DEEP_FACE, GOLD_LIT))
        pygame.draw.circle(big, col, (lx, ly), rad)

    mask = pygame.Surface((size * SS, size * SS), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (c, c), R)
    big.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    ring_w = 8 * SS
    pygame.draw.circle(big, SCARLET, (c, c), R, ring_w)
    pygame.draw.circle(big, SCARLET_EDGE, (c, c), R, 2 * SS)

    disc = pygame.transform.smoothscale(big, (size, size))

    # START rendered at final size so the glyph edges never pass through the
    # supersample downscale.
    f = _font(30, True)
    txt, track = "START", 3
    glyphs = [f.render(ch, True, SCARLET) for ch in txt]
    total = sum(g.get_width() for g in glyphs) + track * (len(glyphs) - 1)
    x = size // 2 - total // 2
    # Nudged below the geometric centre: Pip owns the upper-right of the face,
    # so an optically lowered word balances the lockup and clears the parcel.
    top = size // 2 + 11 - glyphs[0].get_height() // 2
    for g in glyphs:
        disc.blit(g, (x, top))
        x += g.get_width() + track

    _disc_cache["disc"] = disc
    return disc


def _build_halo():
    """A whisper-thin warm halo — the only nod to 'the disc emits'. Kept far
    below a shadow tier or a plate: peak alpha 26, no hard edge."""
    if "halo" in _disc_cache:
        return _disc_cache["halo"]
    pad = 18
    size = (DISC_R + pad) * 2
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    c = size // 2
    for k in range(pad, 0, -1):
        a = int(26 * (1.0 - k / pad) ** 1.4) + 1
        pygame.draw.circle(s, (255, 206, 120, a), (c, c), DISC_R + k)
    _disc_cache["halo"] = s
    return s


# ── Pip ──────────────────────────────────────────────────────────────────────

_pip_cache = {}


def _build_pip():
    """Pip at ~128 px WITH the parcel, built from the player's REAL equipped
    skin + parcel (store_data), not a hardcoded base bird. The base macaw goes
    through the vector-scaled builder so the 1.8x blow-up stays crisp; store
    skins have no scaled builder, so those smoothscale from the 68x64 frame."""
    if "pip" in _pip_cache:
        return _pip_cache["pip"]
    store_data.load()
    skin = store_data.equipped("skin") or "skin_base"
    parcel_id = store_data.equipped("parcel")

    angle = parrot._WING_ANGLES[0]      # wing up — the flap that reads as lift
    if skin == "skin_base":
        raw = parrot._build_frame_scaled(angle, PIP_SCALE)
        body = parrot._add_outline_scaled(raw, PIP_SCALE)
    else:
        base = parrot.get_skin_frame(skin, 0, 0.0)
        bw, bh = base.get_size()
        body = pygame.transform.smoothscale(
            base, (int(bw * PIP_SCALE), int(bh * PIP_SCALE)))

    parcel = parrot.get_parcel("normal", parcel_id)
    pw, ph = parcel.get_size()
    parcel = pygame.transform.smoothscale(
        parcel, (int(pw * PIP_SCALE), int(ph * PIP_SCALE)))

    # Same body-centre -> parcel-centre relationship the live bird uses, scaled.
    y_off = int(PARCEL_Y_OFFSET * PIP_SCALE)
    bw, bh = body.get_size()
    pad = parcel.get_height()
    sheet = pygame.Surface((bw, bh + pad), pygame.SRCALPHA)
    sheet.blit(body, (0, 0))
    pr = parcel.get_rect(center=(bw // 2, bh // 2 + y_off))
    sheet.blit(parcel, pr.topleft)
    _pip_cache["pip"] = (sheet, (bw // 2, bh // 2))
    return _pip_cache["pip"]


def _pip_head_icon(diameter):
    """Pip's face, cropped from a 3x build — the PROFILE chip's identity mark."""
    key = ("head", diameter)
    if key in _pip_cache:
        return _pip_cache[key]
    store_data.load()
    skin = store_data.equipped("skin") or "skin_base"
    SS = 3
    if skin == "skin_base":
        src = parrot._add_outline_scaled(
            parrot._build_frame_scaled(parrot._WING_ANGLES[1], float(SS)), float(SS))
    else:
        base = parrot.get_skin_frame(skin, 1, 0.0)
        src = pygame.transform.smoothscale(
            base, (base.get_width() * SS, base.get_height() * SS))
    # Head + beak box in sprite space (head centre ~(47,21), beak tip x=61).
    box = pygame.Rect(33 * SS, 6 * SS, 32 * SS, 32 * SS)
    box = box.clip(src.get_rect())
    head = src.subsurface(box).copy()
    head = pygame.transform.smoothscale(head, (diameter, diameter))
    _pip_cache[key] = head
    return head


# ── labels ───────────────────────────────────────────────────────────────────

def _stamp_label(surf, text, center, size=LABEL_SIZE, track=1,
                 fill=_GOLD_PALE, outline=INK_OUTLINE):
    """Gold caption on a 1 px dark stamp. Bare sky at 12 px needs a two-tone
    construction for the same reason the wordmark does — pale gold alone loses
    to the 196,214,212 day sky."""
    f = _font(size, True)
    glyphs_f = [f.render(ch, True, fill) for ch in text]
    glyphs_o = [f.render(ch, True, outline) for ch in text]
    total = sum(g.get_width() for g in glyphs_f) + track * (len(glyphs_f) - 1)
    x0 = center[0] - total // 2
    top = center[1] - glyphs_f[0].get_height() // 2
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1),
                   (-1, -1), (1, -1), (-1, 1), (1, 1)):
        x = x0
        for g in glyphs_o:
            surf.blit(g, (x + dx, top + dy))
            x += g.get_width() + track
    x = x0
    for g in glyphs_f:
        surf.blit(g, (x, top))
        x += g.get_width() + track
    return pygame.Rect(x0, top, total, glyphs_f[0].get_height())


def label_width(text, size=LABEL_SIZE, track=1):
    f = _font(size, True)
    return sum(f.size(ch)[0] for ch in text) + track * (len(text) - 1)


# ── chips ────────────────────────────────────────────────────────────────────

def chip_layout():
    """Three utilities on one pitch, then a wider gap and a bigger PROFILE:
    the row groups as 3 + 1 (utilities + identity) instead of a four-slot
    dashboard."""
    gap = 23
    lead_gap = 34
    run = CHIP_D * 3 + gap * 2
    total = run + lead_gap + PROFILE_D
    x = (W - total) // 2
    rects = []
    for _ in range(3):
        rects.append(pygame.Rect(x, CHIP_CY - CHIP_D // 2, CHIP_D, CHIP_D))
        x += CHIP_D + gap
    x += lead_gap - gap
    rects.append(pygame.Rect(x, CHIP_CY - PROFILE_D // 2, PROFILE_D, PROFILE_D))
    return rects


def draw_chip(surf, rect, kind):
    r = rect.width // 2
    chip = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.circle(chip, (*INK, 217), (r, r), r)
    # A single warm hairline keeps the hole from dissolving into the night sky
    # — the chip fill and the plum/night sky sit within 1.3:1 of each other.
    rim_a = 205 if kind == "profile" else 170
    pygame.draw.circle(chip, (*_GOLD_DEEP, rim_a), (r, r), r, 1)
    surf.blit(chip, rect.topleft)
    cx, cy = rect.center
    if kind == "coin":
        _coin_icon(surf, cx, cy, 14)
    elif kind == "trophy":
        _draw_trophy(surf, cx, cy, 12)
    elif kind == "gear":
        _draw_gear(surf, cx, cy, 14)
    elif kind == "profile":
        head = _pip_head_icon(rect.width - 16)
        surf.blit(head, head.get_rect(center=(cx, cy)))


# ── frame ────────────────────────────────────────────────────────────────────

def render_background(phase, scroll=40.0):
    surf = pygame.Surface((W, H))
    palette = _biome.palette_for_phase(phase)
    if not sky_designs.render_active(surf, W, H, GROUND_Y, palette, phase):
        raise RuntimeError("alpine_haze sky design is not active")
    cloud_pal = sky_designs.active_cloud_palette(phase, palette) or palette
    for i, (bx, by, sc) in enumerate(_CLOUD_SLOTS):
        ox = ((bx - scroll * (0.04 + 0.02 * i)) % (W + 160)) - 80
        draw_cloud(surf, ox, by, sc, variant=0, palette=cloud_pal)
    draw_mountains(surf, scroll, GROUND_Y, W, phase=phase)
    foreground.draw_foreground_floor(surf, scroll, palette, phase)
    foreground.draw_promenade(surf, scroll, palette, phase, 0.0)
    foreground.draw_near_lane(surf, scroll, palette, phase, 0.0)
    return surf


def render_frame(phase):
    bg = render_background(phase)
    surf = bg.copy()

    _outlined_text(surf, "SKYBIT", (W // 2, 110), size=58, px=3,
                   outline=WORDMARK_OUTLINE, shadow_offset=(2, 4))

    halo = _build_halo()
    surf.blit(halo, halo.get_rect(center=DISC_C))
    disc = _build_disc()
    disc_rect = disc.get_rect(center=DISC_C)
    surf.blit(disc, disc_rect.topleft)

    pip, anchor = _build_pip()
    pip_pos = (PIP_C[0] - anchor[0], PIP_C[1] - anchor[1])
    surf.blit(pip, pip_pos)

    rects = chip_layout()
    kinds = ("coin", "trophy", "gear", "profile")
    labels = ("STORE", "TOP 10", "SETTINGS", "PROFILE")
    for rect, kind, label in zip(rects, kinds, labels):
        draw_chip(surf, rect, kind)
        _stamp_label(surf, label, (rect.centerx, LABEL_CY))

    start_rect = pygame.Rect(0, 0, DISC_D, DISC_D)
    start_rect.center = DISC_C
    return surf, bg, start_rect, rects


# ── review sheet ─────────────────────────────────────────────────────────────

# The shipped menu, for side-by-side reference in the review sheet only.
CURRENT_PNG = os.path.join(REPO, "docs", "main-menu", "current_ingame.png")


def build_sheet(frames):
    pad, gap = 20, 18
    head = 62
    cap = 30
    thumb_col = 150
    current = (pygame.image.load(CURRENT_PNG).convert()
               if os.path.exists(CURRENT_PNG) else None)
    cols = 4 + (1 if current is not None else 0)
    sheet_w = pad * 2 + W * cols + gap * (cols - 1) + thumb_col
    sheet_h = head + H + cap + pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((18, 18, 26))

    f_title = _font(30, True)
    sheet.blit(f_title.render("MAIN MENU v2  —  ONE-BUTTON  —  ROUND 1",
                              True, (245, 226, 178)), (pad, 14))
    f_sub = _font(15, True)
    sheet.blit(f_sub.render(
        "one luminous gold disc + Pip & parcel as one lockup; utilities are dark holes"
        "   ·   alpine_haze, four keyframes, 1x",
        True, (150, 152, 168)), (pad, 44))

    f_cap = _font(16, True)
    x = pad
    if current is not None:
        sheet.blit(current, (x, head))
        pygame.draw.rect(sheet, (70, 70, 88),
                         pygame.Rect(x - 1, head - 1, W + 2, H + 2), 1)
        sheet.blit(f_cap.render("CURRENT  live menu", True, (150, 152, 168)),
                   (x, head + H + 8))
        x += W + gap
    for (name, t), (frame, _bg, _sr, _cr) in zip(PHASES, frames):
        sheet.blit(frame, (x, head))
        pygame.draw.rect(sheet, (70, 70, 88),
                         pygame.Rect(x - 1, head - 1, W + 2, H + 2), 1)
        cap_img = f_cap.render(f"{name.upper()}   t={t:.2f}", True, (208, 196, 168))
        sheet.blit(cap_img, (x, head + H + 8))
        x += W + gap

    tx = pad + W * cols + gap * (cols - 1) + 16
    thumb = pygame.transform.smoothscale(frames[0][0], (90, 160))
    thumb = pygame.transform.grayscale(thumb)
    sheet.blit(f_cap.render("THUMBNAIL", True, (208, 196, 168)), (tx, head))
    sheet.blit(f_cap.render("90x160 grey", True, (150, 152, 168)), (tx, head + 20))
    sheet.blit(thumb, (tx, head + 46))
    pygame.draw.rect(sheet, (70, 70, 88),
                     pygame.Rect(tx - 1, head + 45, 92, 162), 1)

    f_note = _font(13, True)
    notes = [
        "TWO-TONE, phase-proof:",
        " disc = gold face +",
        " deep-scarlet ring",
        " (max leg >= 3.2:1 at",
        " every keyframe)",
        "",
        "Pip 128px, carrying the",
        "parcel, on the disc's",
        "upper-right arc.",
        "",
        "3 utilities + 1 identity,",
        "not a row of four.",
    ]
    ny = head + 226
    for line in notes:
        sheet.blit(f_note.render(line, True, (176, 178, 194)), (tx, ny))
        ny += 17
    return sheet


def main():
    os.makedirs(OUT, exist_ok=True)
    frames = []
    for name, t in PHASES:
        biome_time = t * _biome.CYCLE_SECONDS
        phase = _biome.phase_for_time(biome_time)
        frames.append(render_frame(phase))
        pygame.image.save(frames[-1][0], os.path.join(OUT, f"round_1_{name}.png"))

    sheet = build_sheet(frames)
    pygame.image.save(sheet, os.path.join(OUT, "round_1.png"))

    report(frames)


def report(frames):
    print("\n=== CONTRAST: disc face / scarlet ring vs the sky behind ===")
    print(f"{'phase':8} {'sky behind':>16} {'gold face':>16} {'ring':>14} "
          f"{'face:sky':>9} {'ring:sky':>9} {'max':>6}")
    cx, cy = DISC_C
    face_pts = [(cx - 26, cy - 28), (cx + 22, cy + 24), (cx - 40, cy + 34),
                (cx + 40, cy - 8), (cx, cy - 46)]
    ring_pts = [(cx + int((DISC_R - 4) * math.cos(a)),
                 cy + int((DISC_R - 4) * math.sin(a)))
                for a in (0.0, math.pi * 0.5, math.pi, math.pi * 1.5,
                          math.pi * 0.75, math.pi * 1.25)]
    sky_pts = [(cx + int((DISC_R + 12) * math.cos(a)),
                cy + int((DISC_R + 12) * math.sin(a)))
               for a in (0.0, math.pi * 0.5, math.pi, math.pi * 1.5,
                         math.pi * 0.25, math.pi * 0.75, math.pi * 1.25,
                         math.pi * 1.75)]
    worst = 99.0
    for (name, _t), (frame, bg, _sr, _cr) in zip(PHASES, frames):
        sky = sample_mean(bg, sky_pts)
        face = sample_mean(frame, face_pts)
        ring = sample_mean(frame, ring_pts)
        cf, cr = contrast(face, sky), contrast(ring, sky)
        worst = min(worst, max(cf, cr))
        print(f"{name:8} {str(sky):>16} {str(face):>16} {str(ring):>14} "
              f"{cf:9.2f} {cr:9.2f} {max(cf, cr):6.2f}")
    print(f"worst max(face,ring) across phases: {worst:.2f}  "
          f"({'PASS' if worst >= 3.0 else 'FAIL'} vs the 3.0 non-text floor)")

    print("\n=== CONTRAST: START caps on the disc face / SKYBIT legs vs sky ===")
    WM_FILL, WM_OUT = _GOLD_BRIGHT, WORDMARK_OUTLINE
    word_sky_pts = [(24, 96), (336, 96), (180, 72), (24, 128), (336, 128)]
    for (name, _t), (frame, bg, _sr, _cr) in zip(PHASES, frames):
        face_under = sample_mean(frame, [(118, 330), (118, 322), (120, 340)])
        start_c = contrast(SCARLET, face_under)
        sky_word = sample_mean(bg, word_sky_pts)
        cf, co = contrast(WM_FILL, sky_word), contrast(WM_OUT, sky_word)
        print(f"  {name:8} START {str(SCARLET)} on face {str(face_under):>16} "
              f"= {start_c:5.2f}   |  SKYBIT sky {str(sky_word):>16} "
              f"fill={cf:5.2f} outline={co:5.2f} max={max(cf, co):5.2f}")

    print("\n=== CONTRAST: chip glyph vs its chip fill ===")
    rects = frames[0][3]
    labels = ("STORE", "TOP 10", "SETTINGS", "PROFILE")
    for name, _t in PHASES:
        frame = frames[[p[0] for p in PHASES].index(name)][0]
        row = []
        for rect, label in zip(rects, labels):
            best_c = _brightest(frame, rect.inflate(-10, -10))
            fill_pt = (rect.centerx, rect.bottom - 5)
            fill = frame.get_at(fill_pt)[:3]
            row.append(f"{label}:{contrast(best_c, fill):5.1f}")
        print(f"  {name:8} " + "  ".join(row))

    print("\n=== CONTRAST: the chip as a THREE-leg stack vs the sky behind it ===")
    print("    (dark fill / gold hairline / gold glyph — at least one leg has to")
    print("     carry at every keyframe, same two-tone logic as the disc)")
    rects0 = frames[0][3]
    cap_sky_pts = [(r.centerx, LABEL_CY) for r in rects0]
    for (name, _t), (frame, bg, _sr, _cr) in zip(PHASES, frames):
        chip_sky = sample_mean(bg, [(r.centerx, CHIP_CY) for r in rects0])
        chip_fill = sample_mean(frame, [(r.centerx, r.bottom - 5) for r in rects0])
        rim = sample_mean(frame, [(r.centerx, r.top) for r in rects0]
                          + [(r.centerx, r.bottom - 1) for r in rects0])
        glyph = _brightest(frame, rects0[0].inflate(-10, -10))
        legs = (contrast(chip_fill, chip_sky), contrast(rim, chip_sky),
                contrast(glyph, chip_sky))
        print(f"  {name:8} sky {str(chip_sky):>16}  fill={legs[0]:5.2f}"
              f"  rim={legs[1]:5.2f}  glyph={legs[2]:5.2f}  max={max(legs):5.2f}")
        cap_sky = sample_mean(bg, cap_sky_pts)
        cf, co = contrast(_GOLD_PALE, cap_sky), contrast(INK_OUTLINE, cap_sky)
        print(f"           caption sky {str(cap_sky):>16}  fill={cf:5.2f}"
              f"  outline={co:5.2f}  max={max(cf, co):5.2f}")

    print("\n=== LABEL FIT (12 px bold, track 1) ===")
    spans = []
    for rect, label in zip(rects, labels):
        w = label_width(label)
        spans.append((label, rect.centerx - w // 2, rect.centerx - w // 2 + w))
        print(f"  {label:9} width={w:3d}px  chip={rect.width}px  "
              f"chip-overhang={(w - rect.width) / 2:+5.1f}px/side  "
              f"span x=[{spans[-1][1]},{spans[-1][2]}]")
    for k in range(len(spans) - 1):
        print(f"  gap {spans[k][0]:>8} -> {spans[k + 1][0]:<8} "
              f"= {spans[k + 1][1] - spans[k][2]:3d}px")
    print(f"  left margin={spans[0][1]}px  right margin={W - spans[-1][2]}px  "
          f"cap height={_font(LABEL_SIZE, True).get_height()}px "
          f"(size={LABEL_SIZE} — at or above the 12 px floor)")

    print("\n=== TAP TARGETS ===")
    start = frames[0][2]
    named = [("START", start)] + list(zip(labels, rects))
    for nm, r in named:
        print(f"  {nm:9} {str(r):38} min-side={min(r.width, r.height)}px")
    ok = True
    for i in range(len(named)):
        for j in range(i + 1, len(named)):
            a, b = named[i][1], named[j][1]
            if a.colliderect(b):
                ok = False
                print(f"  OVERLAP {named[i][0]} x {named[j][0]}")
    xs = sorted(named[1:], key=lambda p: p[1].x)
    gaps = [xs[k + 1][1].left - xs[k][1].right for k in range(len(xs) - 1)]
    print(f"  pairwise disjoint: {ok}   horizontal gaps: {gaps}")
    print(f"  lowest painted y (labels): {LABEL_CY + 8}  (< 624 required)")


if __name__ == "__main__":
    main()
