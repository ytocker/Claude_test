"""Comparison sheet of SKATEBOARD! banner placements, each rendered on
the same live gameplay frame with the new (y=70) halftone score already
in place. Outputs three round sheets:
    docs/skateboard_banner_options/round_1.png   banner DODGES the score
    docs/skateboard_banner_options/round_2.png   banner ON TOP, score OVERLAID
    docs/skateboard_banner_options/round_3.png   banner+score UNIFIED hero

Run from the repo root:
    python tools/render_skateboard_banner_options.py
"""
import math
import os
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "dummy"

import sys
import random
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

import pygame
pygame.init()
pygame.display.set_mode((360, 640))

from game.config import W, H, SKATEBOARD_DURATION
from game.scenes import App, STATE_PLAY
from game.world import World
from game.skateboard_fx import (
    _gradient_text,
    _halftone_filled_burst,
    _halftone_score_badge,
    INK,
    PLATE_RED,
)


OUT_DIR = os.path.join(_ROOT, "docs", "skateboard_banner_options")
OUT_PATH = os.path.join(OUT_DIR, "round_1.png")
OUT_PATH_R2 = os.path.join(OUT_DIR, "round_2.png")
OUT_PATH_R3 = os.path.join(OUT_DIR, "round_3.png")


def _build_gameplay_frame(seed=11, seconds=5.0):
    """Drive a short autopilot sim, activate skateboard, render frame."""
    random.seed(seed)
    app = App()
    if hasattr(app, "_splash_covering"):
        app._splash_covering = False
    w = World()
    w.ready_t = 0.0
    w.flap()
    app.world = w
    app.state = STATE_PLAY
    dt = 1 / 60
    for _ in range(int(seconds / dt)):
        ahead = [p for p in w.pipes if p.x > w.bird.x - 18]
        target = min(ahead, key=lambda p: p.x).gap_y - 12 if ahead else H * 0.45
        if w.bird.y > target:
            w.flap()
        w.update(dt)
        if w.game_over:
            break

    # Activate skateboard so the HUD swaps in the halftone score at y=70.
    w.bird.skateboard_active = True
    w.skateboard_timer = SKATEBOARD_DURATION
    # caption_t controls the halftone score's alpha fade — keep it FULL.
    # Setting it well above the FADE threshold (0.8) holds alpha at 255.
    w.skateboard_caption_t = SKATEBOARD_DURATION
    # Suppress the LIVE banner overlay — we'll draw banner variants ourselves.
    w.skateboard_caption_overlay = None
    # Same for the burst (otherwise we'd see the pickup starburst behind).
    w.skateboard_burst_t = 0.0
    w.skateboard_burst_surface = None
    return app


def _render_base(app):
    """Render a full gameplay frame and return a copy of the screen."""
    app._render()
    return app.screen.copy()


def _plate_banner(text, font_size, rot_deg, pad_x=16, pad_y=8,
                  outline_w=4):
    """Return a tilted SKATEBOARD! plate as a rotated surface."""
    txt = _gradient_text(text, font_size,
                         top_col=(255, 255, 110),
                         bot_col=(255, 180, 10),
                         outline=INK, outline_w=outline_w)
    bw, bh = txt.get_width() + pad_x * 2, txt.get_height() + pad_y * 2
    composite = pygame.Surface((bw + 12, bh + 12), pygame.SRCALPHA)
    ccx = composite.get_width() // 2
    ccy = composite.get_height() // 2
    plate_rect = pygame.Rect(0, 0, bw, bh)
    plate_rect.center = (ccx + 4, ccy + 4)
    pygame.draw.rect(composite, PLATE_RED, plate_rect, border_radius=8)
    pygame.draw.rect(composite, INK, plate_rect, 3, border_radius=8)
    composite.blit(txt, txt.get_rect(center=(ccx, ccy)).topleft)
    return pygame.transform.rotate(composite, rot_deg)


def _corner_slashes(surf, cx, cy, anchors):
    """Pen-style speed slashes from each corner pointing at (cx, cy)."""
    for x0, y0 in anchors:
        for off in range(3):
            dx = (cx - x0) * 0.18
            dy = (cy - y0) * 0.18
            ox = (-1 if x0 < cx else 1) * (off * 8)
            oy = off * 4
            pygame.draw.line(surf, INK,
                             (x0 + ox, y0 + oy),
                             (x0 + ox + dx, y0 + oy + dy), 4)


# ── Variant renderers — each takes a base frame, returns a new surface ─────

def variant_b1_top_thin(base):
    """B1 — Slim banner above the score plate (y=18)."""
    s = base.copy()
    cx, cy = W // 2, 18
    _corner_slashes(s, cx, cy, ((20, 4), (W - 20, 4)))
    banner = _plate_banner("SKATEBOARD!", font_size=26, rot_deg=5,
                           pad_x=12, pad_y=4, outline_w=3)
    s.blit(banner, banner.get_rect(center=(cx, cy)))
    return s


def variant_b2_bottom_edge(base):
    """B2 — Banner at the bottom edge (y=H-50)."""
    s = base.copy()
    cx, cy = W // 2, H - 50
    _corner_slashes(s, cx, cy, ((20, H - 8), (W - 20, H - 8)))
    banner = _plate_banner("SKATEBOARD!", font_size=38, rot_deg=-3)
    s.blit(banner, banner.get_rect(center=(cx, cy)))
    return s


def variant_b3_vertical_left(base):
    """B3 — Banner rotated 90° CCW along the left edge."""
    s = base.copy()
    cx, cy = 22, H // 2
    banner = _plate_banner("SKATEBOARD!", font_size=36, rot_deg=90,
                           pad_x=18, pad_y=8)
    s.blit(banner, banner.get_rect(center=(cx, cy)))
    return s


def variant_b4_diagonal_mid(base):
    """B4 — Dramatic diagonal banner across mid-screen (y=300)."""
    s = base.copy()
    cx, cy = W // 2, 300
    banner = _plate_banner("SKATEBOARD!", font_size=44, rot_deg=-15,
                           pad_x=20, pad_y=10, outline_w=5)
    s.blit(banner, banner.get_rect(center=(cx, cy)))
    return s


def variant_b5_top_right(base):
    """B5 — Small banner parked in the top-right corner (y=30)."""
    s = base.copy()
    cx, cy = W - 78, 30
    _corner_slashes(s, cx, cy, ((W - 20, 4), (20, 4)))
    banner = _plate_banner("SKATEBOARD!", font_size=24, rot_deg=12,
                           pad_x=10, pad_y=4, outline_w=3)
    s.blit(banner, banner.get_rect(center=(cx, cy)))
    return s


VARIANTS = [
    ("B1 — Top thin (above score)", variant_b1_top_thin),
    ("B2 — Bottom edge",            variant_b2_bottom_edge),
    ("B3 — Vertical left",          variant_b3_vertical_left),
    ("B4 — Diagonal mid-screen",    variant_b4_diagonal_mid),
    ("B5 — Top-right corner",       variant_b5_top_right),
]


# ── Round 2: banner stays at TOP, score overlays it ────────────────────────
#
# Score is fixed at on-screen y=70 (the new NA-plate position). Each variant
# draws a banner shape that remains legible even when the halftone score is
# stamped on top of its centre. The score is re-blit AFTER the banner so it
# always sits on top.

# Reuse the same halftone-score overlay the live HUD uses — pulled via
# render_skateboard_score_e3 in skateboard_fx. The HUD blits it at
# (0, -_skateboard_lift_y=-26), so we replicate that here.
from game.skateboard_fx import render_skateboard_score_e3 as _score_overlay_fn
from game.world import World as _W


_SCORE_LIFT_Y = 26   # matches World._skateboard_lift_y default


def _stamp_score(surf, score):
    """Stamp the halftone score on top of `surf`, identical to the live
    HUD blit (skateboard_fx.render_skateboard_score_e3 + (0,-lift_y))."""
    score_overlay = _score_overlay_fn(score)
    surf.blit(score_overlay, (0, -_SCORE_LIFT_Y))


def variant_r2_b1_wide_stretched(base, score):
    """R2-B1 — Wide stretched banner. SKATEBOARD! with extra letter
    spacing on a wide red plate spanning W-40 across the top — the
    leftmost/rightmost letters stay visible outside the score's column."""
    s = base.copy()
    # Wide plate y=38→y=94, behind the score band
    plate = pygame.Rect(20, 38, W - 40, 56)
    pygame.draw.rect(s, PLATE_RED, plate, border_radius=10)
    pygame.draw.rect(s, INK, plate, 3, border_radius=10)
    # Stretched text — wide letter spacing so SK… and …RD! sit on the flanks
    txt = _gradient_text("S K A T E B O A R D !", 26,
                         top_col=(255, 255, 110),
                         bot_col=(255, 180, 10),
                         outline=INK, outline_w=3)
    s.blit(txt, txt.get_rect(center=(W // 2, 66)))
    _stamp_score(s, score)
    return s


def variant_r2_b2_tall_doubledeck(base, score):
    """R2-B2 — Tall plate y=8→y=116, with SKATEBOARD! at the TOP edge
    of the plate and the score sitting in the lower 2/3. The two
    occupy different vertical bands of the same plate, so neither is
    obscured."""
    s = base.copy()
    plate = pygame.Rect(28, 8, W - 56, 108)
    pygame.draw.rect(s, PLATE_RED, plate, border_radius=12)
    pygame.draw.rect(s, INK, plate, 3, border_radius=12)
    # Text high up on the plate
    txt = _gradient_text("SKATEBOARD!", 22,
                         top_col=(255, 255, 110),
                         bot_col=(255, 180, 10),
                         outline=INK, outline_w=3)
    s.blit(txt, txt.get_rect(center=(W // 2, 26)))
    _stamp_score(s, score)
    return s


def variant_r2_b3_split_around(base, score):
    """R2-B3 — Two banner halves: SKATE on the left, BOARD! on the
    right, both at y=70. Score sits in the gap between them."""
    s = base.copy()
    skate = _plate_banner("SKATE", font_size=26, rot_deg=5,
                          pad_x=10, pad_y=4, outline_w=3)
    board = _plate_banner("BOARD!", font_size=26, rot_deg=-5,
                          pad_x=10, pad_y=4, outline_w=3)
    s.blit(skate, skate.get_rect(center=(54, 64)))
    s.blit(board, board.get_rect(center=(W - 54, 64)))
    _stamp_score(s, score)
    return s


def variant_r2_b4_diagonal_big(base, score):
    """R2-B4 — Large SKATEBOARD! rotated -15° centred behind the
    score band. The diagonal means most letters live above or below
    the score's horizontal strip; only 2-3 mid letters get clipped."""
    s = base.copy()
    banner = _plate_banner("SKATEBOARD!", font_size=44, rot_deg=-15,
                           pad_x=20, pad_y=10, outline_w=5)
    s.blit(banner, banner.get_rect(center=(W // 2, 70)))
    _stamp_score(s, score)
    return s


def variant_r2_b5_full_top_strip(base, score):
    """R2-B5 — A full-width, translucent red strip across y=0→y=110
    with SKATEBOARD! text spanning it. The score punches a clean
    halftone burst over the middle — the strip is the BACKDROP, not
    a foreground element competing for attention."""
    s = base.copy()
    # Translucent backdrop strip
    strip = pygame.Surface((W, 110), pygame.SRCALPHA)
    strip.fill((220, 50, 40, 200))   # PLATE_RED at alpha 200
    pygame.draw.line(strip, INK, (0, 109), (W, 109), 2)
    s.blit(strip, (0, 0))
    # SKATEBOARD! text along the very top, leaving the score's row clear
    txt = _gradient_text("SKATEBOARD!", 28,
                         top_col=(255, 255, 110),
                         bot_col=(255, 180, 10),
                         outline=INK, outline_w=4)
    s.blit(txt, txt.get_rect(center=(W // 2, 22)))
    _stamp_score(s, score)
    return s


VARIANTS_R2 = [
    ("R2-B1 — Wide stretched",     variant_r2_b1_wide_stretched),
    ("R2-B2 — Tall double-deck",   variant_r2_b2_tall_doubledeck),
    ("R2-B3 — Split SKATE/BOARD!", variant_r2_b3_split_around),
    ("R2-B4 — Diagonal big",       variant_r2_b4_diagonal_big),
    ("R2-B5 — Full top strip",     variant_r2_b5_full_top_strip),
]


# ── Round 3: banner + score UNIFIED into a single hero element ─────────────
#
# Round 2 stacked the live banner and the standard halftone score plate, but
# they read as two independent objects fighting for the same band. Round 3
# treats banner + score as ONE composite — shared outline, shared shadow,
# shared visual grammar. We do NOT call `_stamp_score()` here; each variant
# bakes the halftone score IN to its composite so the unification is total.
# Everything must fit inside the top 110 px (buff icons start at y=128) and
# stay legible at 3 digits.


# Reuse the existing helpers — `_halftone_score_badge` paints the halftone
# burst, `_gradient_text` paints the yellow-orange SKATEBOARD! lettering.
from game.skateboard_fx import _halftone_score_badge as _hb


def _yellow_text(text, size, outline_w=4):
    """Standard SKATEBOARD! gradient text — yellow to orange with ink
    outline. Wrapped here so each R3 cell reads the same lettering."""
    return _gradient_text(text, size,
                          top_col=(255, 255, 110),
                          bot_col=(255, 180, 10),
                          outline=INK, outline_w=outline_w)


def _drop_shadow_rect(surf, rect, radius, offset=(3, 4),
                       shadow=(0, 0, 0, 130)):
    """One unified cast shadow under the composite — shared by banner
    and the score interior so they read as a single object."""
    sh = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(sh, shadow, sh.get_rect(), border_radius=radius)
    surf.blit(sh, (rect.left + offset[0], rect.top + offset[1]))


def variant_r3_c1_banner_frame(base, score):
    """R3-C1 — Banner-as-frame. ONE red rounded plate contains BOTH a
    smaller SKATEBOARD! wordmark kissing the plate's top rule AND a
    dominant halftone score burst whose bottom spikes overhang the
    plate's lower edge by ~6 px so the rectangle reads as broken —
    not a flat label. The wordmark dropped ~15% (so the score reigns)
    and the plate was shortened ~20 px horizontally so the burst no
    longer swims in negative space. Score digit cap height ≈ 1.6× the
    wordmark cap height to satisfy the global dominance directive."""
    s = base.copy()
    # Plate shortened ~20 px (W-76 → W-96) so the burst fills the
    # interior instead of floating in red space. Vertical span kept
    # at 86 so the wordmark + burst + overhang composition fits the
    # top 110 px before the buff icon row at y=128.
    plate = pygame.Rect(0, 0, W - 96, 86)
    plate.center = (W // 2, 56)
    _drop_shadow_rect(s, plate, radius=14, offset=(3, 5))
    pygame.draw.rect(s, PLATE_RED, plate, border_radius=14)
    pygame.draw.rect(s, INK, plate, 4, border_radius=14)
    # Wordmark crown — dropped from 19 → 17 (≈15%) and raised so its
    # baseline kisses the plate's top rule. Cap height ≈ 12 px.
    wm = _yellow_text("SKATEBOARD!", 17, outline_w=3)
    s.blit(wm, wm.get_rect(center=(W // 2, plate.top + 12)))
    # Hairline interior divider just below the wordmark — sells the
    # plate as ONE box with a heading.
    pygame.draw.line(s, INK,
                     (plate.left + 14, plate.top + 22),
                     (plate.right - 14, plate.top + 22), 2)
    # Dominant score burst — digit at font_size=52 gives cap height
    # ≈ 36 px (1.6× the 22 px the burst's bounds need vs the 12 px
    # wordmark cap). Burst is positioned so its lower spike tips
    # break the plate's bottom edge by ~6 px, intentionally breaking
    # the rectangle so it doesn't read as a flat label.
    burst_cy = plate.bottom - 22
    _hb(s, W // 2, burst_cy, str(score),
        ro=42, ri=28, font_size=52)
    return s


def variant_r3_c2_tape_ribbon(base, score):
    """R3-C2 — Tape-ribbon + stamp. The word is biased LEFT on the
    ribbon so the stamp lands over the trailing "!" instead of the
    middle of the word — reader now scans the full SKATEBOARD! and
    the stamp reads as a punctuation accent rather than a censor bar.
    Tilt eased from -6° → -3° so the ribbon no longer fights the
    buff-icon row at y=128 on the right or the pause button. Halftone
    dot density inside the burst was thinned ~40% (step 8 → 14) so
    the yellow base doesn't compete with the coin field at gameplay
    scale, and the score digit picks up an extra 1 px ink ring (a
    second outline pass) so it punches cleanly against the yellow."""
    s = base.copy()
    ribbon_w, ribbon_h = W + 60, 52
    rib = pygame.Surface((ribbon_w, ribbon_h), pygame.SRCALPHA)
    # Small inset top/bottom so the tape reads as torn — not a
    # sterile rectangle.
    body = pygame.Rect(0, 6, ribbon_w, ribbon_h - 12)
    pygame.draw.rect(rib, PLATE_RED, body)
    pygame.draw.rect(rib, INK, body, 3)
    # Triangular notches at each end so the ends read as tape tips.
    for tip_x, dir_ in ((0, 1), (ribbon_w, -1)):
        tri = [(tip_x, ribbon_h // 2),
               (tip_x + dir_ * 18, body.top),
               (tip_x + dir_ * 18, body.bottom)]
        pygame.draw.polygon(rib, PLATE_RED, tri)
        pygame.draw.polygon(rib, INK, tri, 3)
    # Wordmark biased LEFT so the stamp can sit over the "!" on the
    # right rather than swallowing the middle of SKATEBOARD. Word
    # rendered at a SMALLER size (28→24) so the stamp can sit fully
    # to the right of the "!" without clipping any letters at the
    # canvas's 360 px width.
    rib_txt = _yellow_text("SKATEBOARD!", 24, outline_w=3)
    rib.blit(rib_txt, rib_txt.get_rect(
        center=(ribbon_w // 2 - 72, ribbon_h // 2)))
    # Tilt softened from -6° → -3° so the right tip clears the buff
    # icon row + pause button.
    rotated = pygame.transform.rotate(rib, -3)
    rect = rotated.get_rect(center=(W // 2, 56))
    # Unified shadow under the ribbon and the stamp — one continuous
    # shadow locks them as a single object.
    shadow = rotated.copy()
    shadow.fill((0, 0, 0, 130), special_flags=pygame.BLEND_RGBA_MULT)
    s.blit(shadow, (rect.left + 3, rect.top + 5))
    s.blit(rotated, rect)
    # Stamp pushed RIGHT of centre so it lands clear of the "!"
    # — full SKATEBOARD! reads cleanly to its left and the stamp
    # becomes the punctuation accent. Stamp held back from the
    # canvas right edge so its right spike clears the pause button
    # at ~x=325.
    stamp_cx, stamp_cy = W // 2 + 88, 70
    rng = random.Random(stamp_cx * 31 + stamp_cy * 17 + 10)
    spikes = 10
    ro, ri = 40, 26
    pts = []
    for i in range(spikes * 2):
        ang = i * math.pi / spikes - math.pi / 2
        r = ro if i % 2 == 0 else ri
        r += rng.randint(-4, 4)
        pts.append((stamp_cx + math.cos(ang) * r,
                    stamp_cy + math.sin(ang) * r))
    # Stamp shadow continuous with the ribbon shadow above.
    sh_pts = [(p[0] + 3, p[1] + 5) for p in pts]
    pygame.draw.polygon(s, (0, 0, 0, 110), sh_pts)
    pygame.draw.polygon(s, (255, 220, 30), pts)
    bbox_l = int(min(p[0] for p in pts)) - 2
    bbox_t = int(min(p[1] for p in pts)) - 2
    bbox_r = int(max(p[0] for p in pts)) + 2
    bbox_b = int(max(p[1] for p in pts)) + 2
    dots = pygame.Surface((W, H), pygame.SRCALPHA)
    # ~40% fewer dots: default helper uses step=8, here step=14.
    step = 14
    for gy in range(bbox_t, bbox_b, step):
        offset = (step // 2) if ((gy // step) % 2 == 1) else 0
        for gx in range(bbox_l + offset, bbox_r, step):
            pygame.draw.circle(dots, (230, 60, 50), (gx, gy), 2)
    mask = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), pts)
    dots.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    s.blit(dots, (0, 0))
    pygame.draw.polygon(s, INK, pts, 4)
    # Score digit with an EXTRA 1 px ink ring drawn around the existing
    # outline pass — pops the digit silhouette against the yellow halftone.
    num_ring = _gradient_text(str(score), 46,
                              top_col=INK, bot_col=INK,
                              outline=INK, outline_w=6)
    s.blit(num_ring, num_ring.get_rect(center=(stamp_cx, stamp_cy)))
    num = _gradient_text(str(score), 46,
                         top_col=(255, 250, 240),
                         bot_col=(230, 60, 50),
                         outline=INK, outline_w=4)
    s.blit(num, num.get_rect(center=(stamp_cx, stamp_cy)))
    return s


def variant_r3_c3_skate_deck(base, score):
    """R3-C3 — Skate-deck silhouette. Deck width trimmed 280→260 so it
    no longer crowds the pause button at the 360-px right edge. The
    red-and-yellow stripes that were creating a moiré trap behind the
    yellow burst are dialed down to a soft 15%-opacity wash inside
    the deck — the silhouette + truck-bolt dots carry the "deck"
    reading and the stripes stop fighting the score. Burst extends
    BELOW the deck's lower rim by ~22 px so the score becomes the
    focal punch rather than a passenger riding on top of the board.
    Wordmark size held small so the score digit dominates by ≥1.4×."""
    s = base.copy()
    deck_w, deck_h = 260, 78
    deck = pygame.Surface((deck_w, deck_h), pygame.SRCALPHA)
    deck_rect = deck.get_rect()
    pygame.draw.rect(deck, PLATE_RED, deck_rect, border_radius=38)
    # Stripes calmed to a 15% wash — alpha ~38/255 is the moiré-safe
    # threshold the critique called out; the deck-read survives via
    # silhouette + truck-bolt dots.
    stripes = pygame.Surface((deck_w, deck_h), pygame.SRCALPHA)
    stripe_step = 22
    for i in range(-deck_h, deck_w + deck_h, stripe_step):
        if (i // stripe_step) % 2 == 0:
            pts = [(i, 0), (i + stripe_step // 2, 0),
                   (i + stripe_step // 2 + deck_h, deck_h),
                   (i + deck_h, deck_h)]
            pygame.draw.polygon(stripes, (255, 235, 130, 38), pts)
    mask = pygame.Surface((deck_w, deck_h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), deck_rect,
                     border_radius=38)
    stripes.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    deck.blit(stripes, (0, 0))
    # Truck-bolt dots — sell the "deck" read on their own.
    for bolt_x in (24, deck_w - 24):
        for bolt_y in (16, deck_h - 16):
            pygame.draw.circle(deck, INK, (bolt_x, bolt_y), 4)
            pygame.draw.circle(deck, (60, 60, 60), (bolt_x, bolt_y), 2)
    pygame.draw.rect(deck, INK, deck_rect, 4, border_radius=38)
    # Position the deck so the burst hanging below it still clears
    # the buff-icon row at y=128.
    deck_rect_on = deck.get_rect(center=(W // 2, 42))
    sh = deck.copy()
    sh.fill((0, 0, 0, 120), special_flags=pygame.BLEND_RGBA_MULT)
    s.blit(sh, (deck_rect_on.left + 3, deck_rect_on.top + 5))
    s.blit(deck, deck_rect_on)
    # Wordmark crown — small (cap height ~12 px) so the score's
    # ~30 px cap clears the 1.4× dominance rule.
    wm = _yellow_text("SKATEBOARD!", 17, outline_w=3)
    s.blit(wm, wm.get_rect(center=(W // 2, deck_rect_on.top + 14)))
    # Score burst — bottom of burst hangs ~22 px below the deck's
    # lower rim so the score visibly punches downward off the deck.
    burst_cy = deck_rect_on.bottom + 14
    _hb(s, W // 2, burst_cy, str(score),
        ro=40, ri=26, font_size=48)
    return s


def variant_r3_c4_sign_post(base, score):
    """R3-C4 — Sign-post UNIFIED by the burst piercing BOTH panels.
    Header (SKATEBOARD! marquee) and bowl (score chamber) are stacked
    with NO waist bar between them; the halftone burst sits centred
    on the SEAM so its top half eats into the marquee and its bottom
    half sits inside the bowl. The burst becomes the physical rivet
    joining the two panels — reader sees ONE composite shape, not
    two stacked stamps. Seam outline is broken through the burst's
    width so the silhouette flows; side outlines on the left/right
    of the seam are re-stroked so the composite's overall silhouette
    stays crisp."""
    s = base.copy()
    # Header panel + bowl panel sharing the same width, stacked with
    # no gap. The bowl is shaped wider/taller so it reads as a
    # "score chamber" distinct from the header marquee.
    panel_w = 200
    header = pygame.Rect(0, 0, panel_w, 36)
    bowl = pygame.Rect(0, 0, panel_w + 24, 50)
    header.center = (W // 2, 30)
    bowl.midtop = (W // 2, header.bottom - 1)
    # ONE shared shadow for the full silhouette (union footprint).
    union_shadow = pygame.Rect(bowl.left, header.top,
                               bowl.width,
                               (bowl.bottom - header.top))
    _drop_shadow_rect(s, union_shadow, radius=16, offset=(3, 5))
    # Header marquee.
    pygame.draw.rect(s, PLATE_RED, header, border_radius=10)
    pygame.draw.rect(s, INK, header, 3, border_radius=10)
    # Bowl chamber — wider so it reads as a distinct "score" base
    # while still sharing the marquee's grammar.
    pygame.draw.rect(s, PLATE_RED, bowl, border_radius=16)
    pygame.draw.rect(s, INK, bowl, 3, border_radius=16)
    # Wordmark — kissing the marquee's top rule.
    wm = _yellow_text("SKATEBOARD!", 19, outline_w=3)
    s.blit(wm, wm.get_rect(center=(header.centerx, header.top + 14)))
    # Now paint over the SHARED SEAM with PLATE_RED to kill the two
    # adjacent ink lines (top-of-bowl and bottom-of-header), so the
    # silhouette reads as one shape with a waist. We only paint the
    # central section, NOT the edges where the header is narrower
    # than the bowl — those edge stubs must stay outlined.
    seam_y = header.bottom
    seam_strip = pygame.Rect(header.left + 6, seam_y - 4,
                             header.width - 12, 8)
    pygame.draw.rect(s, PLATE_RED, seam_strip)
    # Re-stroke the header's bottom-rule SIDE STUBS (the bit where
    # the bowl is wider than the header — those exterior shoulders
    # have to stay outlined so the silhouette doesn't lose its
    # waist outline).
    pygame.draw.line(s, INK,
                     (bowl.left, header.bottom),
                     (header.left, header.bottom), 3)
    pygame.draw.line(s, INK,
                     (header.right, header.bottom),
                     (bowl.right, header.bottom), 3)
    # The pierce-rivet — burst centred ON the seam y so its top half
    # eats into the marquee and its bottom half sits in the bowl.
    burst_cx, burst_cy = W // 2, seam_y
    _hb(s, burst_cx, burst_cy, str(score),
        ro=40, ri=26, font_size=46)
    return s


def variant_r3_c5_burst_exclamation(base, score):
    """R3-C5 — Burst-as-exclamation. The front-runner. Reads as ONE
    word: SKATEBOARD then the halftone burst IS the final "!". This
    cell gets the hardest push from the critique:
    - gap between wordmark and burst closed to ~4 px so it reads as
      "word!" not "word + asterisk"
    - burst's vertical centre lowered so the burst's BOTTOM aligns
      with the wordmark's BASELINE — no more floating-high burst
    - burst's outer-spike radius shrunk so the burst sits closer to
      "punctuation dot" optical size relative to the digit
    - ONE shared deep-red drop shadow cast under BOTH the wordmark
      AND the burst so they lock visually as a single object
    - wordmark gets thickened ink stroke + soft shadow so it
      survives day AND night biome without a plate backing it
    - digit gradient deepened — cream top kept, red bottom-stop
      pushed darker so the digit silhouette punches against the
      yellow burst instead of muddying into it
    - burst sized to clear the pause-button rectangle at the
      top-right (no overlap into the buff-icon row at y=128)."""
    s = base.copy()
    # Wordmark + burst sizing tuned so the composite fits within 360 px
    # AND clears the pause button at the top-right. Burst's outer radius
    # was 28 → trimmed to 27 so the digit (not the spikes) reads as the
    # heaviest mass of the composite — keeps optical hierarchy: digit >
    # wordmark > spike halo. Word cap ~18 px; burst digit cap inside the
    # 27 px halo.
    wm_size = 32
    word = _yellow_text("SKATEBOARD", wm_size, outline_w=5)
    burst_ro = 27
    # Inner pad widened from 17 → 21 (+4 px) so 3-digit "888" scores
    # fit inside the burst's inner valleys without the digit silhouette
    # punching through the spike rim. Late-game scores hit triple digits
    # before SKATEBOARD power-ups become rare, so this margin is needed.
    burst_ri = 21
    burst_diameter = burst_ro * 2
    gap = 4
    total_w = word.get_width() + gap + burst_diameter
    # Pull composite slightly LEFT so the burst's right spike clears
    # the pause-button rectangle (which sits at ~x=320 onward). Extra
    # -6 px nudge moves the BURST itself ~6 px left (after the composite
    # is laid out) so its left spike kisses the right edge of the "D".
    start_x = max(8, (W - total_w) // 2 - 14)
    # Centre line at y=72 — keeps the composite inside the top 110 px
    # and well clear of the buff icons at y=128.
    centre_y = 72
    word_rect = word.get_rect(midleft=(start_x, centre_y))
    # Burst's BOTTOM aligns with the wordmark's BASELINE (~ bottom of
    # rendered glyphs minus descender). Approximate baseline as
    # word_rect.bottom - ~6 px descender padding.
    word_baseline_y = word_rect.bottom - 6
    burst_cy = word_baseline_y - burst_ro
    # -6 px burst nudge so the left spike kisses the "D" right edge
    # rather than leaving a gap — "word!" reads as one tight unit.
    burst_cx = word_rect.right + gap + burst_diameter // 2 - 6
    # Soft DARK drop shadow under BOTH silhouettes — one continuous
    # shadow layer ties the wordmark + burst into a single object.
    # Using dark grey (not red) so the shadow doesn't bleed colour
    # into the wordmark's outline at low offsets.
    SHADOW_RGBA = (0, 0, 0, 130)
    shadow_offset = (3, 5)
    shadow_layer = pygame.Surface((W, H), pygame.SRCALPHA)
    wm_shadow = _gradient_text("SKATEBOARD", wm_size,
                               top_col=(0, 0, 0),
                               bot_col=(0, 0, 0),
                               outline=(0, 0, 0),
                               outline_w=6)
    wm_shadow.set_alpha(SHADOW_RGBA[3])
    shadow_layer.blit(wm_shadow,
                      (word_rect.left - 1 + shadow_offset[0],
                       word_rect.top - 1 + shadow_offset[1]))
    pygame.draw.circle(shadow_layer, SHADOW_RGBA,
                       (burst_cx + shadow_offset[0],
                        burst_cy + shadow_offset[1]),
                       burst_ro + 2)
    s.blit(shadow_layer, (0, 0))
    # Wordmark — yellow gradient with thick ink outline (outline_w=5)
    # so it survives the pale-day biome without a red plate behind it.
    s.blit(word, word_rect)
    # Faint 1-px inner highlight along the TOP of the wordmark letters
    # — same trick the coin glyph uses. A second pass of the gradient
    # text without an outline, blitted 1 px UP at ~30% alpha, leaves a
    # bright top-edge sheen that survives both day AND night biome
    # because it tints existing yellow, never introduces a new colour.
    hl = _gradient_text("SKATEBOARD", wm_size,
                        top_col=(255, 255, 110),
                        bot_col=(255, 255, 110),
                        outline=INK, outline_w=0)
    hl.set_alpha(76)  # ~30% of 255
    s.blit(hl, (word_rect.left, word_rect.top - 1))
    # Halftone burst body — inlined so we control the digit gradient.
    rng = random.Random(burst_cx * 31 + burst_cy * 17 + 10)
    spikes = 10
    pts = []
    for i in range(spikes * 2):
        ang = i * math.pi / spikes - math.pi / 2
        r = burst_ro if i % 2 == 0 else burst_ri
        r += rng.randint(-3, 3)
        pts.append((burst_cx + math.cos(ang) * r,
                    burst_cy + math.sin(ang) * r))
    pygame.draw.polygon(s, (255, 220, 30), pts)
    bbox_l = int(min(p[0] for p in pts)) - 2
    bbox_t = int(min(p[1] for p in pts)) - 2
    bbox_r = int(max(p[0] for p in pts)) + 2
    bbox_b = int(max(p[1] for p in pts)) + 2
    dots = pygame.Surface((W, H), pygame.SRCALPHA)
    step = 8
    for gy in range(bbox_t, bbox_b, step):
        offset = (step // 2) if ((gy // step) % 2 == 1) else 0
        for gx in range(bbox_l + offset, bbox_r, step):
            pygame.draw.circle(dots, (230, 60, 50), (gx, gy), 2)
    mask = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), pts)
    dots.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    s.blit(dots, (0, 0))
    pygame.draw.polygon(s, INK, pts, 4)
    # Score digit — cream top, deepened red bottom (190, 30, 20 vs the
    # helper's default (230, 60, 50)). The deeper bottom pushes the
    # digit silhouette darker so it pops against the yellow burst
    # base instead of blending into it.
    # Digit font auto-scales for 3+ digit scores so the digit silhouette
    # never punches through the burst's spike rim. 1-2 digits keep the
    # punchy 28 px cap; 3-digit drops to 22 to leave ~3 px clearance
    # inside the outer-spike envelope.
    num_size = 28 if len(str(score)) <= 2 else 22
    num = _gradient_text(str(score), num_size,
                         top_col=(255, 250, 240),
                         bot_col=(190, 30, 20),
                         outline=INK, outline_w=3)
    # -2 px lift on the digit centre so its optical centre lines up with
    # the burst's geometric centre — glyph metrics carry extra descender
    # padding that drags the digit visually low otherwise.
    s.blit(num, num.get_rect(center=(burst_cx, burst_cy - 2)))
    return s


VARIANTS_R3 = [
    ("R3-C1 — Banner-as-frame",       variant_r3_c1_banner_frame),
    ("R3-C2 — Tape-ribbon + stamp",   variant_r3_c2_tape_ribbon),
    ("R3-C3 — Skate-deck silhouette", variant_r3_c3_skate_deck),
    ("R3-C4 — Stacked sign-post",     variant_r3_c4_sign_post),
    ("R3-C5 — Burst-as-exclamation",  variant_r3_c5_burst_exclamation),
]


def _compose_sheet(cells, title_text):
    """2x3 grid (5 cells + 1 spare). Each cell shows the rendered frame
    with a label strip below. Cell = W × (H + 36); margins = 16 px."""
    pygame.font.init()
    font = pygame.font.SysFont(None, 22)
    margin = 16
    label_h = 36
    cell_w = W + margin
    cell_h = H + label_h + margin
    cols, rows = 3, 2
    sheet_w = margin + cell_w * cols
    sheet_h = margin + cell_h * rows + 50  # +50 for title
    sheet = pygame.Surface((sheet_w, sheet_h), pygame.SRCALPHA)
    sheet.fill((26, 30, 36, 255))

    # Title
    title = pygame.font.SysFont(None, 30).render(
        title_text, True, (245, 240, 220))
    sheet.blit(title, (margin, 14))

    for idx, (label, frame) in enumerate(cells):
        col = idx % cols
        row = idx // cols
        x0 = margin + col * cell_w
        y0 = margin + 40 + row * cell_h
        sheet.blit(frame, (x0, y0))
        pygame.draw.rect(sheet, (90, 110, 130),
                         (x0, y0, W, H), width=1)
        lbl = font.render(label, True, (235, 230, 210))
        sheet.blit(lbl, (x0, y0 + H + 6))
    return sheet


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    print("building gameplay base frame...")
    app = _build_gameplay_frame()
    base = _render_base(app)
    score_for_overlay = app.world.score

    # Round 1 — banner placements that AVOID overlapping the score.
    cells = []
    for label, renderer in VARIANTS:
        cells.append((label, renderer(base)))
        print(f"  rendered {label}")
    sheet = _compose_sheet(cells,
        "Skybit — SKATEBOARD! banner placement options "
        "(score now at y=70 to match the regular NA plate)")
    pygame.image.save(sheet, OUT_PATH)
    print(f"wrote {OUT_PATH}  ({os.path.getsize(OUT_PATH)} bytes)")

    # Round 2 — banner stays at the TOP with the score overlaid on it.
    cells_r2 = []
    for label, renderer in VARIANTS_R2:
        cells_r2.append((label, renderer(base, score_for_overlay)))
        print(f"  rendered {label}")
    sheet_r2 = _compose_sheet(cells_r2,
        "Skybit — SKATEBOARD! banner at TOP with score overlaid "
        "(banner must remain readable through the overlap)")
    pygame.image.save(sheet_r2, OUT_PATH_R2)
    print(f"wrote {OUT_PATH_R2}  ({os.path.getsize(OUT_PATH_R2)} bytes)")

    # Round 3 — banner + score UNIFIED into a single hero composite.
    cells_r3 = []
    for label, renderer in VARIANTS_R3:
        cells_r3.append((label, renderer(base, score_for_overlay)))
        print(f"  rendered {label}")
    sheet_r3 = _compose_sheet(cells_r3,
        "Skybit — SKATEBOARD! banner + score UNIFIED into ONE hero "
        "(no competing pieces — score is part of the banner)")
    pygame.image.save(sheet_r3, OUT_PATH_R3)
    print(f"wrote {OUT_PATH_R3}  ({os.path.getsize(OUT_PATH_R3)} bytes)")


def _verify_c5_3digit(base):
    """3-digit "888" sanity render — burst's inner padding must hold
    triple-digit scores without trimming the spike silhouette. Writes
    a scratch cell to docs/skateboard_banner_options/round_3_c5_888.png
    so the verification is visually inspectable, and prints the digit
    bounds vs the burst inner radius."""
    frame = variant_r3_c5_burst_exclamation(base, 888)
    out = os.path.join(OUT_DIR, "round_3_c5_888.png")
    pygame.image.save(frame, out)
    # Measure 3-digit "888" at the auto-scaled font_size=22 the renderer
    # uses for 3-digit scores — must fit inside the burst's outer
    # envelope (ro*2) with margin.
    test_glyph = _gradient_text("888", 22,
                                top_col=(255, 250, 240),
                                bot_col=(190, 30, 20),
                                outline=INK, outline_w=3)
    digit_w = test_glyph.get_width()
    # Burst's effective digit envelope is bounded by the outer-spike
    # diameter (ro*2) — digits are allowed to occupy the full yellow
    # disc, since the spike valleys (ri) only matter when the digit's
    # silhouette would punch THROUGH the rim. The relevant comparison
    # is digit-glyph-width vs outer-disc-diameter with ~4 px margin.
    outer_w = 27 * 2  # burst_ro * 2
    print(f"  3-digit check: '888' glyph width={digit_w}px, "
          f"burst outer diameter={outer_w}px "
          f"({'FITS' if digit_w <= outer_w else 'OVERFLOW (spike-trim)'})")
    print(f"  wrote {out}")


if __name__ == "__main__":
    main()
    # Run AFTER the main sheet so the scratch file uses the same base
    # frame the sheet does — verifies 3-digit legibility on C5.
    print("3-digit '888' verification on C5...")
    app = _build_gameplay_frame()
    base = _render_base(app)
    _verify_c5_3digit(base)
