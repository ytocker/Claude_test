"""GRIM SPROUT — chibi Skybit Death boss, take #1 (the tiny reaper-imp).

A roly-poly knee-high BABY reaper dragging a great-scythe FIVE TIMES his height:
menace through comedy of scale. Drawn in the Skybit chibi house style — FLAT
saturated fills, 1-2px hard ink keylines, the dark-core -> fill -> top-left
sheen triad (ported from `_marotte_ruff`), supersampled then smoothscaled for
crisp AA, with a grown 1px silhouette outline so the imp pops on any sky.

The whole identity is the EXTREME prop-to-body ratio (AD guardrail #1): the
blade dwarfs the imp. The straight SNATH is the tileable vertical PILLAR post;
the curved blade is a detachable GAP-EDGE flourish ONLY, so a top/bottom mirror
reads as one matched obstacle and the blade never bleeds into the tiling body.

Headless review renderer — not shipped. Imports the real game helpers so the
finish matches house style.
"""
import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pygame

from game.draw import _shade_c, lerp_color, blit_glow  # noqa: F401
from game.config import PIPE_W

# ── GRIM SPROUT palette ("candy-poison": orchid-violet + mint) ───────────────
HOOD       = (123,  79, 216)   # #7B4FD8 orchid-violet
HOOD_DK    = ( 78,  46, 150)   # #4E2E96 shade
HOOD_HI    = (169, 140, 242)   # #A98CF2 sheen
MINT       = ( 57, 224, 196)   # #39E0C4 belly / trim
MINT_DK    = _shade_c(MINT, -60)
MINT_HI    = _shade_c(MINT, 55)
BONE       = (255, 243, 194)   # #FFF3C2 claws / teeth / cream-bone
BONE_DK    = _shade_c(BONE, -70)
EYE_GOLD   = (255, 225,  74)   # #FFE14A glow-gold pinprick eyes
WOOD       = (176, 122,  58)   # #B07A3A warm-wood snath
WOOD_DK    = _shade_c(WOOD, -55)
WOOD_HI    = _shade_c(WOOD, 55)
BLADE      = (236, 232, 214)   # bone-flat scythe blade
BLADE_DK   = _shade_c(BLADE, -78)
BLADE_LIT  = (255, 255, 235)   # 1px lit inner cutting edge
INK        = ( 28,  22,  30)   # #1C1620 hard keyline


def _triad_circle(surf, cx, cy, r, col, ss):
    """The house FORM recipe: a dark-core ring, the flat fill, and a ~1/3-radius
    top-left sheen — flat shapes that read sculpted without any gradient. Ported
    straight from `_marotte_ruff` so the imp matches the clown anchor's finish."""
    pygame.draw.circle(surf, _shade_c(col, -55), (int(cx), int(cy)), int(r))
    pygame.draw.circle(surf, col, (int(cx), int(cy)), max(2, int(r - ss)))
    pygame.draw.circle(surf, _shade_c(col, 55),
                       (int(cx - r * 0.32), int(cy - r * 0.32)),
                       max(1, int(r * 0.34)))


def _add_outline(src, outline_color=(28, 22, 30, 235)):
    """Grow a 1px dark outline from the alpha mask so the imp keeps a black-shape
    silhouette on any sky (the parrot `_add_outline` recipe)."""
    w, h = src.get_size()
    pad = 2
    out = pygame.Surface((w + pad * 2, h + pad * 2), pygame.SRCALPHA)
    mask = pygame.mask.from_surface(src, threshold=8)
    sil = mask.to_surface(setcolor=outline_color, unsetcolor=(0, 0, 0, 0))
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1),
                   (-1, -1), (1, -1), (-1, 1), (1, 1)):
        out.blit(sil, (pad + dx, pad + dy))
    out.blit(src, (pad, pad))
    return out


# ── the imp + his oversized scythe ───────────────────────────────────────────

def build_grim_sprout(scale=1.0, ss=3):
    """Render the imp + great-scythe onto a tight transparent surface, then add a
    grown outline. Coordinates are in supersampled space; the body is sized small
    and the scythe DELIBERATELY tall so the prop-to-body ratio stays extreme.

    Returns a smoothscaled surface whose width fits the splayed blade."""
    # Body box. The imp himself is short + fat; the scythe runs far above him and
    # the great blade sweeps wide LEFT, so the surface is tall AND wide enough to
    # hold the whole crescent in-frame. The imp sits low-right.
    BW = int(240 * scale * ss)
    BH = int(330 * scale * ss)
    s = pygame.Surface((BW, BH), pygame.SRCALPHA)

    # Imp anchored low and right; the snath leans across him, blade sweeping left.
    body_cx = int(BW * 0.66)
    feet_y = int(BH * 0.93)
    hood_r = int(36 * scale * ss)              # head ~ 40% of the (short) body
    belly_r = int(26 * scale * ss)

    # ── 1. THE GREAT-SCYTHE (drawn first so the imp's mitts overlap the snath) ──
    # Snath leans from the imp's grip up to a HIGH socket, leaving headroom above
    # for the blade crescent — the snath alone is TALLER than the whole imp, and
    # the blade dwarfs him again on top of that (AD guardrail #1: extreme ratio).
    snath_top = (int(BW * 0.52), int(BH * 0.22))
    snath_bot = (int(BW * 0.78), feet_y + int(6 * scale * ss))
    sw = int(8 * scale * ss)
    pygame.draw.line(s, WOOD_DK, snath_top, snath_bot, sw + max(2, int(3 * ss)))
    pygame.draw.line(s, WOOD, snath_top, snath_bot, sw)
    # A top-left lit edge running the pole (offset perpendicular to its lean).
    dx, dy = snath_bot[0] - snath_top[0], snath_bot[1] - snath_top[1]
    plen = math.hypot(dx, dy) or 1
    nx, ny = -dy / plen, dx / plen            # pole normal
    off = int(2 * scale * ss)
    pygame.draw.line(s, WOOD_HI,
                     (snath_top[0] - off * 0 - nx * off, snath_top[1] - ny * off),
                     (snath_bot[0] - nx * off, snath_bot[1] - ny * off),
                     max(1, int(2 * ss)))
    # Banded grip wraps where his mitts will close — also the pillar-banding cue.
    for t in (0.42, 0.55):
        bxp = int(snath_top[0] + dx * t)
        byp = int(snath_top[1] + dy * t)
        pygame.draw.circle(s, WOOD_DK, (bxp, byp), max(3, int(6 * scale * ss)))
        pygame.draw.circle(s, BONE, (bxp, byp), max(2, int(4 * scale * ss)))
        pygame.draw.circle(s, BONE_DK, (bxp, byp), max(2, int(4 * scale * ss)),
                           max(1, int(ss)))

    # The BLADE: a great curved bone hook arcing UP + ACROSS from the snath top —
    # the canonical scythe crescent, sized big so it dwarfs the imp. Bone-flat
    # with a 1px lit inner edge; ink-keyed so it holds on a bright day sky.
    bx, by = snath_top[0], snath_top[1] + int(6 * scale * ss)
    outer, inner = [], []
    span = int(96 * scale * ss)
    rise = int(70 * scale * ss)
    for i in range(24):
        t = i / 23.0
        ax = bx - int(span * t)                # sweeps LEFT, away from the imp
        ay = by - int(rise * math.sin(t * math.pi * 0.92))
        thick = (1 - t) * int(20 * scale * ss) + int(3 * scale * ss)
        outer.append((ax, ay - thick))         # blunt spine (back of blade)
        inner.append((ax, ay))                 # cutting edge
    blade = outer + list(reversed(inner))
    pygame.draw.polygon(s, BLADE, blade)
    pygame.draw.polygon(s, INK, blade, max(2, int(2.4 * ss)))
    pygame.draw.lines(s, BLADE_DK, False, outer, max(1, int(2 * ss)))  # spine shade
    pygame.draw.lines(s, BLADE_LIT, False, inner, max(1, int(1.6 * ss)))  # lit edge
    # Socket collar where the blade meets the snath top (mint trim to tie palette).
    _triad_circle(s, bx, by, int(8 * scale * ss), MINT, ss)
    pygame.draw.circle(s, INK, (int(bx), int(by)), int(8 * scale * ss), max(1, int(ss)))

    # ── 2. STUB FEET poking out the bottom (drawn before the belly drape) ───────
    for fs, fx_off in ((-1, -16), (1, 14)):
        fx = body_cx + int(fx_off * scale * ss)
        fy = feet_y
        fr = int(11 * scale * ss)
        _triad_circle(s, fx, fy, fr, HOOD, ss)
        # 3 ink claw-lines splaying off the front of each pebble foot.
        for k in (-1, 0, 1):
            ca = math.radians(90 + k * 26)
            cx2 = fx + math.cos(ca) * fr * 0.6
            cy2 = fy + fr * 0.7
            tip = (cx2 + math.cos(ca) * fr * 0.8, cy2 + fr * 0.7)
            pygame.draw.line(s, BONE, (int(cx2), int(cy2)),
                             (int(tip[0]), int(tip[1])), max(2, int(2.4 * ss)))
            pygame.draw.line(s, BONE_DK, (int(cx2), int(cy2)),
                             (int(tip[0]), int(tip[1])), max(1, int(ss)))

    # ── 3. BELLY NUB (mint) overlapping under the hood ──────────────────────────
    belly_cy = feet_y - belly_r - int(6 * scale * ss)
    _triad_circle(s, body_cx, belly_cy, belly_r, MINT, ss)

    # ── 4. THE HOOD — one big orchid lobe drooping to a long curl-tip ───────────
    hood_cy = belly_cy - belly_r - int(2 * scale * ss)
    # Build the droopy hood as a teardrop: a big circle + a swept curl tip lobe.
    _triad_circle(s, body_cx, hood_cy, hood_r, HOOD, ss)
    # The droop curl: a tapering swept tail off the hood's upper-left, flopping
    # forward over the face — the "too-big-for-him" hood read.
    curl = []
    cseg = 16
    for i in range(cseg):
        t = i / (cseg - 1)
        ang = math.radians(150 - t * 130)
        rr = hood_r * (1.0 - 0.55 * t)
        ccx = body_cx + math.cos(ang) * (hood_r * 0.5 + t * hood_r * 0.9)
        ccy = hood_cy - hood_r * 0.7 - t * hood_r * 0.2 + math.sin(t * math.pi) * hood_r * 0.25
        curl.append((ccx, ccy, rr * 0.42))
    for (ccx, ccy, rr) in curl:
        pygame.draw.circle(s, HOOD_DK, (int(ccx), int(ccy)), max(2, int(rr)))
    for (ccx, ccy, rr) in curl:
        pygame.draw.circle(s, HOOD, (int(ccx), int(ccy)), max(2, int(rr - ss)))
    # Tiny mint pom-bobble at the very curl-tip (charming, ties palette up top).
    ttx, tty, _ = curl[-1]
    _triad_circle(s, ttx, tty, int(6 * scale * ss), MINT, ss)

    # ── 5. THE FACE — flat dark crescent mouth-shadow, gold pinprick eyes, fang ─
    # The hood face cavity: a flat dark crescent (no feathering) low on the lobe.
    fcx, fcy = body_cx, hood_cy + int(8 * scale * ss)
    cav_r = int(hood_r * 0.66)
    cav = pygame.Surface((cav_r * 2 + 4, cav_r * 2 + 4), pygame.SRCALPHA)
    pygame.draw.circle(cav, INK, (cav_r + 2, cav_r + 2), cav_r)
    # Crop the top off so it reads as a hood-shadow crescent, not a full hole.
    pygame.draw.rect(cav, (0, 0, 0, 0), (0, 0, cav_r * 2 + 4, int(cav_r * 0.7)))
    s.blit(cav, (int(fcx - cav_r - 2), int(fcy - cav_r - 2)))
    # Two glowing gold pinprick eyes — add-glow first so the dark socket read still
    # carries in grayscale (AD accessibility note), then the bright gold dot.
    for es in (-1, 1):
        ex = int(fcx + es * cav_r * 0.42)
        ey = int(fcy + cav_r * 0.10)
        blit_glow(s, ex, ey, int(7 * scale * ss), EYE_GOLD, 150)
    for es in (-1, 1):
        ex = int(fcx + es * cav_r * 0.42)
        ey = int(fcy + cav_r * 0.10)
        pygame.draw.circle(s, EYE_GOLD, (ex, ey), max(2, int(3.2 * scale * ss)))
        pygame.draw.circle(s, (255, 255, 255), (ex - int(ss), ey - int(ss)),
                           max(1, int(1.2 * scale * ss)))
    # One oversized cream FANG poking UP over the hood-shadow lip — the scary-cute
    # signature beat. Drawn as a small triangle straddling the crescent's lower rim.
    fangx = fcx + int(cav_r * 0.12)
    fangy = fcy + int(cav_r * 0.46)
    fang_w = int(5 * scale * ss)
    fang_h = int(11 * scale * ss)
    fang = [(fangx - fang_w, fangy), (fangx + fang_w, fangy),
            (fangx + int(fang_w * 0.3), fangy - fang_h)]
    pygame.draw.polygon(s, BONE, fang)
    pygame.draw.polygon(s, BONE_DK, fang, max(1, int(ss)))

    # ── 6. STUB MITT ARMS — one UP gripping the snath, one bracing it LOW ───────
    # Upper mitt closes on the upper grip-band; lower mitt braces near the foot.
    up_grip = (int(snath_top[0] + dx * 0.42), int(snath_top[1] + dy * 0.42))
    lo_grip = (int(snath_top[0] + dx * 0.78), int(snath_top[1] + dy * 0.78))
    # Sleeve stubs from the hood-base toward each grip (short fat orchid arms).
    sh_l = (body_cx - int(20 * scale * ss), belly_cy - int(4 * scale * ss))
    sh_r = (body_cx + int(18 * scale * ss), belly_cy + int(2 * scale * ss))
    pygame.draw.line(s, HOOD_DK, sh_l, up_grip, int(13 * scale * ss))
    pygame.draw.line(s, HOOD, sh_l, up_grip, int(10 * scale * ss))
    pygame.draw.line(s, HOOD_DK, sh_r, lo_grip, int(13 * scale * ss))
    pygame.draw.line(s, HOOD, sh_r, lo_grip, int(10 * scale * ss))
    # Cream mitt hands closing on the snath (round, with a thumb nub).
    for grip in (up_grip, lo_grip):
        _triad_circle(s, grip[0], grip[1], int(9 * scale * ss), BONE, ss)
        pygame.draw.circle(s, INK, grip, int(9 * scale * ss), max(1, int(ss)))

    s = _add_outline(s)
    # Supersample down for crisp AA. Final display size ~ the build / ss.
    fw = max(1, s.get_width() // ss)
    fh = max(1, s.get_height() // ss)
    return pygame.transform.smoothscale(s, (fw, fh))


# ── prop -> pillar mirror: the snath is a tileable vertical post ─────────────

def draw_snath_pillar_cap(surf, cx, top, bot, w, ss, *, flip):
    """The TOP CAP pier: the snath post runs the full height, the curved blade
    rides the GAP-EDGE (inner end) ONLY as a hooked crescent flourishing INTO the
    gap. `flip=True` draws the bottom pier as a vertical mirror so a top/bottom
    pair reads as one matched obstacle. The blade is detachable to the gap-edge so
    the repeatable mid-post (below) tiles cleanly with no blade in it."""
    work = surf
    if flip:
        # Render into a scratch surface flipped vertically so the same blade math
        # lands at the bottom pier's gap-edge.
        h = surf.get_height()
        tmp = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        draw_snath_pillar_cap(tmp, cx, h - bot, h - top, w, ss, flip=False)
        surf.blit(pygame.transform.flip(tmp, False, True), (0, 0))
        return

    # Full-height bone-banded wood post, dark-cored + top-left lit edge.
    pygame.draw.line(work, WOOD_DK, (cx, top), (cx, bot), w + max(2, int(3 * ss)))
    pygame.draw.line(work, WOOD, (cx, top), (cx, bot), w)
    pygame.draw.line(work, WOOD_HI, (cx - int(2 * ss), top), (cx - int(2 * ss), bot),
                     max(1, int(2 * ss)))
    # Binding collars band the post (mint + bone) so it reads as a worked snath.
    span = bot - top
    for fr in (0.30, 0.62):
        cy = int(top + span * fr)
        _triad_circle(work, cx, cy, max(4, int(7 * ss)), MINT, ss)
        pygame.draw.circle(work, INK, (cx, cy), max(4, int(7 * ss)), max(1, int(ss)))

    # GAP-EDGE blade flourish at the inner (here TOP) end ONLY.
    gap_y = top
    outer, inner = [], []
    bspan = int(60 * ss)
    brise = int(46 * ss)
    for i in range(22):
        t = i / 21.0
        ax = cx - int(bspan * t)
        ay = gap_y - int(brise * math.sin(t * math.pi * 0.92))
        thick = (1 - t) * int(14 * ss) + int(3 * ss)
        outer.append((ax, ay - thick))
        inner.append((ax, ay))
    blade = outer + list(reversed(inner))
    pygame.draw.polygon(work, BLADE, blade)
    pygame.draw.polygon(work, INK, blade, max(2, int(2.2 * ss)))
    pygame.draw.lines(work, BLADE_LIT, False, inner, max(1, int(1.4 * ss)))
    _triad_circle(work, cx, gap_y + int(4 * ss), max(4, int(6 * ss)), MINT, ss)


def draw_snath_pillar_mid(surf, cx, top, bot, w, ss):
    """The REPEATABLE MID segment: pure banded post, NO blade — proves the body
    tiles cleanly because the blade is a detachable gap-flourish."""
    pygame.draw.line(surf, WOOD_DK, (cx, top), (cx, bot), w + max(2, int(3 * ss)))
    pygame.draw.line(surf, WOOD, (cx, top), (cx, bot), w)
    pygame.draw.line(surf, WOOD_HI, (cx - int(2 * ss), top), (cx - int(2 * ss), bot),
                     max(1, int(2 * ss)))
    span = bot - top
    for fr in (0.22, 0.5, 0.78):
        cy = int(top + span * fr)
        _triad_circle(surf, cx, cy, max(4, int(7 * ss)), MINT, ss)
        pygame.draw.circle(surf, INK, (cx, cy), max(4, int(7 * ss)), max(1, int(ss)))


# ── sheet composition ────────────────────────────────────────────────────────

def _sky_panel(w, h, night):
    """The game's real biome day/night keyframes, so legibility is judged on the
    actual backdrop the boss must read on."""
    surf = pygame.Surface((w, h))
    if night:
        top, bot = (5, 8, 30), (35, 55, 115)
    else:
        top, bot = (40, 110, 200), (170, 220, 245)
    for y in range(h):
        pygame.draw.line(surf, lerp_color(top, bot, y / h), (0, y), (w, y))
    return surf


def _label(surf, font, text, x, y):
    sh = font.render(text, True, (0, 0, 0))
    surf.blit(sh, (x + 1, y + 1))
    surf.blit(font.render(text, True, (255, 255, 255)), (x, y))


def main():
    pygame.init()
    ss = 3
    SHEET_W, SHEET_H = 920, 730
    sheet = pygame.Surface((SHEET_W, SHEET_H))
    sheet.fill((46, 40, 58))                       # neutral plum-grey board
    font = pygame.font.SysFont("dejavusans", 17, bold=True)
    fbig = pygame.font.SysFont("dejavusans", 22, bold=True)

    _label(sheet, fbig, "GRIM SPROUT  -  baby reaper-imp (take #1)", 20, 14)

    # (a) Showcase boss on a neutral panel.
    panel_w, panel_h = 360, 620
    panel = pygame.Surface((panel_w, panel_h))
    panel.fill((64, 56, 80))
    pygame.draw.rect(panel, (90, 80, 110), panel.get_rect(), 3)
    boss = build_grim_sprout(scale=1.6, ss=ss)
    panel.blit(boss, (panel_w // 2 - boss.get_width() // 2,
                      panel_h // 2 - boss.get_height() // 2 + 10))
    sheet.blit(panel, (20, 52))
    _label(sheet, font, "(a) showcase  -  blade dwarfs the imp", 24, 60)

    # (b) prop -> pillar mirror: a tall vertical PILLAR pair (top cap + repeatable
    # mid) proving the snath tiles and the blade stays at the gap-edge.
    pil_w, pil_h = 190, 594
    pil = pygame.Surface((pil_w * ss, pil_h * ss), pygame.SRCALPHA)
    pil.fill((40, 36, 52))
    pcx = pil_w * ss // 2
    post_w = int(PIPE_W * 0.42 * ss)
    gap_top = int(pil_h * 0.5 * ss)                # where the top pier ends (gap)
    gap_bot = int(pil_h * 0.62 * ss)               # where the bottom pier starts
    # Top cap pier: post from sheet-top down to the gap, blade at the gap-edge.
    draw_snath_pillar_cap(pil, pcx, int(0.04 * pil_h * ss), gap_top, post_w, ss,
                          flip=False)
    # A repeatable MID band marker (no blade) just above the cap's gap to show the
    # tiling body, plus the bottom mirror pier.
    draw_snath_pillar_cap(pil, pcx, gap_bot, int(0.96 * pil_h * ss), post_w, ss,
                          flip=True)
    pil = pygame.transform.smoothscale(pil, (pil_w, pil_h))
    sheet.blit(pil, (400, 78))
    _label(sheet, font, "(b) snath -> PILLAR pair", 404, 58)
    _label(sheet, font, "blade = gap-edge only", 404, 702)

    # A standalone repeatable-MID strip beside it, proving the body tiles cleanly.
    mid_w, mid_h = 90, 594
    mid = pygame.Surface((mid_w * ss, mid_h * ss), pygame.SRCALPHA)
    mid.fill((40, 36, 52))
    draw_snath_pillar_mid(mid, mid_w * ss // 2, 0, mid_h * ss, post_w, ss)
    mid = pygame.transform.smoothscale(mid, (mid_w, mid_h))
    sheet.blit(mid, (612, 78))
    _label(sheet, font, "(b') repeat MID", 616, 702)

    # (c) 1x in-game-scale insets on day + night sky, proving legibility.
    inset_w, inset_h = 140, 250
    small_boss = build_grim_sprout(scale=0.72, ss=ss)
    for i, night in enumerate((False, True)):
        sky = _sky_panel(inset_w, inset_h, night)
        sky.blit(small_boss, (inset_w // 2 - small_boss.get_width() // 2,
                              inset_h // 2 - small_boss.get_height() // 2 + 8))
        pygame.draw.rect(sky, (20, 16, 24), sky.get_rect(), 2)
        x = 730
        y = 80 + i * 300
        sheet.blit(sky, (x, y))
        _label(sheet, font, "(c) 1x  " + ("NIGHT" if night else "DAY"),
               x + 2, y - 20)

    out_dir = os.path.join(os.path.dirname(__file__), "..", "docs",
                           "skybit_reaper", "grim_sprout")
    out_dir = os.path.abspath(out_dir)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_1.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path)


if __name__ == "__main__":
    main()
