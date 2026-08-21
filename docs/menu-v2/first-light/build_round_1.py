"""first-light main-menu concept, round 1 (reworked).

Standalone review renderer — imports the live modules read-only and writes
PNGs under docs/menu-v2/first-light/. Nothing here edits game/*.py.
"""
import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, _ROOT)

import pygame

pygame.init()
pygame.display.set_mode((360, 640))

from game import biome as _biome           # noqa: E402
from game import hud, parrot, sky_designs, store_data  # noqa: E402
from game.config import PARCEL_Y_OFFSET, W, H, GROUND_Y  # noqa: E402

OUT = os.path.dirname(os.path.abspath(__file__))

# ── the concept's palette ────────────────────────────────────────────────────
# One rule: gold only ever sits on dark. The landform supplies that dark by
# day, the night sky supplies it after dusk, and the 2px ink rim on the START
# pill supplies it in the one place neither can — where gold crosses bare sky.
GOLD      = (240, 192,  64)
GOLD_PALE = (255, 232, 168)
SCARLET   = (148,  20,  20)
INK       = ( 20,  22,  32)
LAND      = ( 30,  33,  46)
# The second land tone. Sits between the darkest night sky and the brightest
# day sky on purpose, so ONE tone reads as a lit ridge at dawn and as the only
# surviving horizon at night without needing a per-phase variant.
CREST     = (104, 112, 138)

PHASES = [("day", 0.12), ("golden", 0.27), ("plum", 0.47), ("night", 0.70)]

# ── landform ─────────────────────────────────────────────────────────────────
CREST_L, CREST_R = 452.0, 478.0
RIM_H = 3


def crest_y(x):
    """Soft ease from the left shoulder down to the right, with a shallow
    crown under x=180 so the ridge rises to meet START: the button's lower
    half then rests on dark land at every x it spans, which is the whole
    point of putting it here."""
    t = x / float(W)
    ease = t * t * (3.0 - 2.0 * t)
    y = CREST_L + (CREST_R - CREST_L) * ease
    y -= 18.0 * math.exp(-((x - 180.0) / 95.0) ** 2)
    return y


_land_cache = None


def land_surface():
    """Supersampled once and reused — a near-horizontal polygon edge stair-steps
    badly at 1x, and the ridge is the only line in the bottom third."""
    global _land_cache
    if _land_cache is not None:
        return _land_cache
    SS = 3
    big = pygame.Surface((W * SS, H * SS), pygame.SRCALPHA)
    top = [(x, crest_y(x / float(SS)) * SS) for x in range(W * SS + 1)]
    body = top + [(W * SS, H * SS), (0, H * SS)]
    pygame.draw.polygon(big, LAND, body)
    rim = top + [(x, y + RIM_H * SS) for x, y in reversed(top)]
    pygame.draw.polygon(big, CREST, rim)
    _land_cache = pygame.transform.smoothscale(big, (W, H))
    return _land_cache


# ── type ─────────────────────────────────────────────────────────────────────

def outlined_tracked(surf, txt, center, size, track=0, fill=GOLD,
                     outline=INK, px=2):
    """hud._outlined_text's 8-offset stamp, per letter so the wordmark can carry
    tracking. Dark outline instead of the menu's red one: on bare sky the fill
    has no dark to sit on until the outline provides it."""
    f = hud._font(size, True)
    glyphs = [(f.render(ch, True, fill), f.render(ch, True, outline))
              for ch in txt]
    total = sum(g.get_width() for g, _ in glyphs) + track * (len(glyphs) - 1)
    x = center[0] - total // 2
    top = center[1] - glyphs[0][0].get_height() // 2
    offsets = [(-px, 0), (px, 0), (0, -px), (0, px),
               (-px, -px), (px, -px), (-px, px), (px, px)]
    left = x
    for img, out in glyphs:
        for ox, oy in offsets:
            surf.blit(out, (x + ox, top + oy))
        surf.blit(img, (x, top))
        x += img.get_width() + track
    return pygame.Rect(left, top, total, glyphs[0][0].get_height())


# ── Pip ──────────────────────────────────────────────────────────────────────
PIP_POS = (108, 196)
PIP_TILT = 18.0          # nose-up; get_skin_frame rotates CCW-positive
PIP_TARGET = 80          # long edge in px
DRAW_PARCEL = True


def draw_pip(surf):
    store_data.load()
    skin = store_data.equipped("skin") or "skin_base"
    parcel_id = store_data.equipped("parcel") or "parcel_base"
    body = parrot.get_skin_frame(skin, 1, 0.0)
    parcel = parrot.get_parcel("normal", parcel_id)
    k = PIP_TARGET / float(max(body.get_size()))
    bw, bh = body.get_size()
    body = pygame.transform.smoothscale(body, (int(bw * k), int(bh * k)))
    pw, ph = parcel.get_size()
    parcel = pygame.transform.smoothscale(parcel, (int(pw * k), int(ph * k)))

    # Body first, parcel over it — the draw order entities.Bird uses, so the
    # parcel reads as carried rather than tucked behind him.
    off = pygame.math.Vector2(0, PARCEL_Y_OFFSET * k).rotate(-PIP_TILT)
    br = pygame.transform.rotate(body, PIP_TILT)
    rect = br.get_rect(center=PIP_POS)
    surf.blit(br, rect.topleft)
    pr = pygame.transform.rotate(parcel, PIP_TILT)
    if DRAW_PARCEL:
        surf.blit(pr, pr.get_rect(center=(PIP_POS[0] + off.x,
                                          PIP_POS[1] + off.y)).topleft)
    return skin, parcel_id, k, rect.union(
        pr.get_rect(center=(PIP_POS[0] + off.x, PIP_POS[1] + off.y)))


# ── START ────────────────────────────────────────────────────────────────────
START_RECT = pygame.Rect(0, 0, 208, 62)
START_RECT.center = (180, 452)
CAP_W = 26


def draw_start(surf):
    r = START_RECT
    rad = r.height // 2
    pygame.draw.rect(surf, INK, r.inflate(6, 6), border_radius=rad + 3)
    pygame.draw.rect(surf, GOLD, r, border_radius=rad)
    clip = surf.get_clip()
    for cap in (pygame.Rect(r.left, r.top, CAP_W, r.height),
                pygame.Rect(r.right - CAP_W, r.top, CAP_W, r.height)):
        surf.set_clip(cap)
        pygame.draw.rect(surf, SCARLET, r, border_radius=rad)
        surf.set_clip(clip)
    pygame.draw.rect(surf, GOLD_PALE, r.inflate(-11, -11), width=1,
                     border_radius=rad - 5)
    f = hud._font(25, True)
    track = 3
    glyphs = [f.render(ch, True, SCARLET) for ch in "START"]
    total = sum(g.get_width() for g in glyphs) + track * (len(glyphs) - 1)
    x = r.centerx - total // 2
    for g in glyphs:
        surf.blit(g, (x, r.centery - g.get_height() // 2))
        x += g.get_width() + track
    return r


# ── glyph row + PROFILE ──────────────────────────────────────────────────────
GLYPH_Y = 526
GLYPH_XS = (96, 180, 264)
LABELS = ("STORE", "TOP 10", "SETTINGS")
LABEL_SIZE = 12
LABEL_Y = 558


def draw_nav(surf):
    rects = []
    for x, label, kind in zip(GLYPH_XS, LABELS, ("coin", "trophy", "gear")):
        if kind == "coin":
            hud._coin_icon(surf, x, GLYPH_Y, 23)
        elif kind == "trophy":
            hud._draw_trophy(surf, x, GLYPH_Y, 15)
        else:
            hud._draw_gear(surf, x, GLYPH_Y, 23)
        hud._tracked_label(surf, label, (x, LABEL_Y), LABEL_SIZE,
                           color=GOLD, track=1, alpha=255)
        rects.append(pygame.Rect(x - 24, GLYPH_Y - 24, 48, 64))
    return rects


PROFILE_NAME = "PIP"
PROFILE_RECT = pygame.Rect(0, 0, 132, 48)
PROFILE_RECT.center = (180, 596)


def draw_profile(surf):
    f = hud._font(17, True)
    img = f.render(PROFILE_NAME, True, GOLD)
    tri_gap = 12
    total = img.get_width() + tri_gap + 8
    x = 180 - total // 2
    surf.blit(img, (x, 596 - img.get_height() // 2))
    hud._profile_tri(surf, x + img.get_width() + tri_gap, 596, 5, GOLD)
    return PROFILE_RECT


# ── frame ────────────────────────────────────────────────────────────────────

def sky_only(phase):
    s = pygame.Surface((W, H))
    sky_designs.render_active(s, W, H, GROUND_Y, _biome.palette_for_phase(phase),
                              phase)
    return s


def render_frame(phase):
    surf = sky_only(phase)
    surf.blit(land_surface(), (0, 0))
    outlined_tracked(surf, "SKYBIT", (180, 84), 34, track=8)
    info = draw_pip(surf)
    draw_start(surf)
    draw_nav(surf)
    draw_profile(surf)
    return surf, info


# ── contrast maths ───────────────────────────────────────────────────────────

def _lin(c):
    c /= 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def lum(rgb):
    r, g, b = (_lin(v) for v in rgb[:3])
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def cr(a, b):
    la, lb = lum(a) + 0.05, lum(b) + 0.05
    return round(max(la, lb) / min(la, lb), 2)


def main():
    os.makedirs(OUT, exist_ok=True)
    frames = {}
    info = None
    for name, t in PHASES:
        f, info = render_frame(t)
        frames[name] = f
        pygame.image.save(f, os.path.join(OUT, "round_1_%s.png" % name))

    # ── review sheet ────────────────────────────────────────────────────────
    gap, pad, head = 22, 26, 84
    sw = pad * 2 + W * 4 + gap * 3
    sh = head + 26 + H + 30 + 210
    sheet = pygame.Surface((sw, sh))
    sheet.fill((18, 18, 24))
    hud._font(30, True)
    t = hud._font(30, True).render(
        "FIRST LIGHT — main menu, round 1 (reworked)", True, GOLD)
    sheet.blit(t, (pad, 22))
    sub = hud._font(16, True).render(
        "gold only ever sits on dark  ·  two-tone landform  ·  gold START  ·  "
        "labelled glyphs  ·  alpine_haze phases", True, (198, 198, 210))
    sheet.blit(sub, (pad, 56))
    x = pad
    for name, ph in PHASES:
        lab = hud._font(17, True).render("%s   t=%.2f" % (name.upper(), ph),
                                         True, (232, 226, 210))
        sheet.blit(lab, (x, head + 4))
        sheet.blit(frames[name], (x, head + 26))
        pygame.draw.rect(sheet, (70, 70, 84),
                         pygame.Rect(x - 1, head + 25, W + 2, H + 2), 1)
        x += W + gap

    ty = head + 26 + H + 30
    thumb = pygame.transform.grayscale(
        pygame.transform.smoothscale(frames["day"], (90, 160)))
    sheet.blit(thumb, (pad, ty))
    pygame.draw.rect(sheet, (70, 70, 84), pygame.Rect(pad - 1, ty - 1, 92, 162), 1)
    cap = hud._font(15, True).render(
        "90x160 greyscale thumbnail (day) — squint test", True, (198, 198, 210))
    sheet.blit(cap, (pad, ty + 168))

    notes = [
        "START is gold on dark (8.4:1 on the landform), with a 2px ink rim so it",
        "also survives the stretch of pill that crosses bare sky.",
        "The crest rim is the second land tone: at night it is the only thing",
        "keeping the horizon alive (2.7:1 against the night sky).",
        "Glyphs carry 11px gold labels — TOP 10 has no universal mark.",
    ]
    ny = ty
    for line in notes:
        sheet.blit(hud._font(16, True).render(line, True, (222, 216, 200)),
                   (pad + 130, ny))
        ny += 26
    pygame.image.save(sheet, os.path.join(OUT, "round_1.png"))

    # ── verification ────────────────────────────────────────────────────────
    print("\n== SKY / LAND / CREST ==")
    print("phase   sky_bot@crest      land:sky  crest:sky  crest:land")
    for name, ph in PHASES:
        s = sky_only(ph)
        cy = int(crest_y(180))
        sky = s.get_at((180, cy - 8))[:3]
        print("%-7s %-18s %8.2f %10.2f %11.2f" % (
            name, str(tuple(sky)), cr(LAND, sky), cr(CREST, sky),
            cr(CREST, LAND)))

    print("\n== GOLD / INK / SCARLET vs sky at the START pill ==")
    print("phase   sky@pill           gold:sky  ink:sky  gold:land  scarlet:gold")
    for name, ph in PHASES:
        s = sky_only(ph)
        sky = s.get_at((180, START_RECT.top + 6))[:3]
        print("%-7s %-18s %8.2f %8.2f %10.2f %13.2f" % (
            name, str(tuple(sky)), cr(GOLD, sky), cr(INK, sky), cr(GOLD, LAND),
            cr(SCARLET, GOLD)))

    print("\n== GOLD vs sky at the wordmark (y=84) ==")
    for name, ph in PHASES:
        s = sky_only(ph)
        sky = s.get_at((180, 84))[:3]
        print("  %-7s sky=%-18s gold:sky=%.2f  ink:sky=%.2f" % (
            name, str(tuple(sky)), cr(GOLD, sky), cr(INK, sky)))

    print("\n== LABEL FIT (12px, track=1) ==")
    f = hud._font(LABEL_SIZE, True)
    for x, label in zip(GLYPH_XS, LABELS):
        w = sum(f.size(ch)[0] for ch in label) + (len(label) - 1)
        print("  %-9s width=%3dpx  half=%4.1f  clear of neighbour target edge "
              "at 60px: %s" % (label, w, w / 2, w / 2 < 60))

    print("\n== TAP RECTS ==")
    surf = pygame.Surface((W, H))
    rects = [("START", START_RECT)]
    rects += [(l, pygame.Rect(x - 24, GLYPH_Y - 24, 48, 64))
              for x, l in zip(GLYPH_XS, LABELS)]
    rects.append(("PROFILE", PROFILE_RECT))
    for name, r in rects:
        print("  %-9s %s  w=%d h=%d" % (name, tuple(r), r.width, r.height))
    ok = True
    for i in range(len(rects)):
        for j in range(i + 1, len(rects)):
            if rects[i][1].colliderect(rects[j][1]):
                ok = False
                print("  OVERLAP", rects[i][0], rects[j][0])
    print("  pairwise disjoint:", ok)
    print("  all >= 48dp:", all(r.width >= 48 and r.height >= 48
                                for _, r in rects))
    print("  lowest edge:", max(r.bottom for _, r in rects), "(limit 624)")

    print("\n== THUMBNAIL BAND LUMINANCE (90x160 greyscale) ==")
    for name, _ph in PHASES:
        th = pygame.transform.grayscale(
            pygame.transform.smoothscale(frames[name], (90, 160)))
        bands = []
        for y0, y1, tag in ((0, 40, "sky-top"), (40, 105, "sky-low"),
                            (105, 118, "ridge"), (118, 160, "land")):
            vals = [th.get_at((xx, yy))[0]
                    for yy in range(y0, y1, 2) for xx in range(0, 90, 3)]
            bands.append("%s=%d" % (tag, sum(vals) // len(vals)))
        print("  %-7s %s" % (name, "  ".join(bands)))

    global DRAW_PARCEL
    DRAW_PARCEL = False
    bare, _ = render_frame(0.12)
    DRAW_PARCEL = True
    withp = frames["day"]
    seen = sum(1 for yy in range(140, 260) for xx in range(50, 175)
               if bare.get_at((xx, yy))[:3] != withp.get_at((xx, yy))[:3])
    print("\n== PARCEL VISIBILITY ==")
    print("  parcel pixels not occluded by Pip: %d" % seen)

    skin, parcel_id, k, prect = info
    print("\n== PIP ==")
    print("  skin=%s parcel=%s scale=%.2f sprite_rect=%s (%dx%d)"
          % (skin, parcel_id, k, tuple(prect), prect.width, prect.height))


main()
