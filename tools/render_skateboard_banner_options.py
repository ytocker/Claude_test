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
    """R3-C1 — Banner-as-frame. ONE red rounded plate contains BOTH
    the SKATEBOARD! wordmark (along the top edge) AND the halftone
    score burst (interior centre). Single outline, single shadow.
    The frame IS the unifier; the score lives inside it, not on top."""
    s = base.copy()
    # Outer plate sized so the wordmark crowns the top and the score
    # burst (ro≈40) fits comfortably in the interior bowl.
    plate = pygame.Rect(0, 0, W - 36, 96)
    plate.center = (W // 2, 58)
    _drop_shadow_rect(s, plate, radius=14, offset=(3, 5))
    pygame.draw.rect(s, PLATE_RED, plate, border_radius=14)
    pygame.draw.rect(s, INK, plate, 4, border_radius=14)
    # Wordmark along the top crown.
    txt = _yellow_text("SKATEBOARD!", 22, outline_w=3)
    s.blit(txt, txt.get_rect(center=(W // 2, plate.top + 16)))
    # Hairline interior divider (thin ink line under the wordmark) —
    # frames the score chamber so it reads as ONE box with a heading,
    # not as a banner with a foreign sticker on top.
    pygame.draw.line(s, INK,
                     (plate.left + 18, plate.top + 30),
                     (plate.right - 18, plate.top + 30), 2)
    # Halftone score burst inside the lower chamber. The burst still
    # carries the score-vocabulary palette but it sits WITHIN the
    # frame — the frame is the parent.
    _hb(s, W // 2, plate.top + 64, str(score),
        ro=34, ri=22, font_size=30)
    return s


def variant_r3_c2_tape_ribbon(base, score):
    """R3-C2 — Tape-ribbon scroll + score stamp. A diagonal red tape
    runs across the top with SKATEBOARD! lettering; the halftone
    score is the wax-seal stamp pressed onto its centre. They share
    one ink halo — the stamp BREAKS the ribbon's outline so it reads
    as physically attached to it."""
    s = base.copy()
    # Build the ribbon on a sub-surface so we can rotate cleanly.
    ribbon_w, ribbon_h = W + 80, 52
    rib = pygame.Surface((ribbon_w, ribbon_h), pygame.SRCALPHA)
    # Rough deckled top + bottom edges — small notches so it reads
    # as torn tape, not a sterile rectangle.
    body = pygame.Rect(0, 6, ribbon_w, ribbon_h - 12)
    pygame.draw.rect(rib, PLATE_RED, body)
    pygame.draw.rect(rib, INK, body, 3)
    # Triangular notches on each end (the tape ends).
    for tip_x, dir_ in ((0, 1), (ribbon_w, -1)):
        tri = [(tip_x, ribbon_h // 2),
               (tip_x + dir_ * 18, body.top),
               (tip_x + dir_ * 18, body.bottom)]
        pygame.draw.polygon(rib, PLATE_RED, tri)
        pygame.draw.polygon(rib, INK, tri, 3)
    # Wordmark stamped along the ribbon.
    rib_txt = _yellow_text("SKATEBOARD!", 30, outline_w=3)
    rib.blit(rib_txt, rib_txt.get_rect(
        center=(ribbon_w // 2, ribbon_h // 2)))
    rotated = pygame.transform.rotate(rib, -6)
    rect = rotated.get_rect(center=(W // 2, 58))
    # Cast a unified shadow under the ribbon AND the score by blitting
    # the alpha-only ribbon shadow first.
    shadow = rotated.copy()
    shadow.fill((0, 0, 0, 130), special_flags=pygame.BLEND_RGBA_MULT)
    s.blit(shadow, (rect.left + 3, rect.top + 5))
    s.blit(rotated, rect)
    # Wax-seal score stamp — circular burst pressed onto the ribbon
    # centre. Slight upward shift so the stamp clearly OVERLAPS the
    # ribbon outline (the bond between the two).
    _hb(s, W // 2, 70, str(score),
        ro=40, ri=26, font_size=34)
    return s


def variant_r3_c3_skate_deck(base, score):
    """R3-C3 — Skate-deck silhouette. A board-shaped plate (long
    rounded ends) striped in red+yellow racing pattern holds the
    SKATEBOARD! lettering along its top edge and the halftone score
    in its centre — looks like a sticker on the underside of a deck."""
    s = base.copy()
    deck_w, deck_h = W - 32, 100
    deck = pygame.Surface((deck_w, deck_h), pygame.SRCALPHA)
    # Deck silhouette — extra-rounded long ends to evoke a board.
    deck_rect = deck.get_rect()
    pygame.draw.rect(deck, PLATE_RED, deck_rect, border_radius=42)
    # Diagonal racing stripes — masked to the deck silhouette via a
    # second pass that punches stripes through the fill.
    stripes = pygame.Surface((deck_w, deck_h), pygame.SRCALPHA)
    stripe_step = 18
    for i in range(-deck_h, deck_w + deck_h, stripe_step):
        if (i // stripe_step) % 2 == 0:
            pts = [(i, 0), (i + stripe_step // 2, 0),
                   (i + stripe_step // 2 + deck_h, deck_h),
                   (i + deck_h, deck_h)]
            pygame.draw.polygon(stripes, (255, 200, 30, 230), pts)
    # Mask stripes to the deck rounded silhouette.
    mask = pygame.Surface((deck_w, deck_h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), deck_rect,
                     border_radius=42)
    stripes.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    deck.blit(stripes, (0, 0))
    # Outline (drawn LAST so it sits on top of stripes).
    pygame.draw.rect(deck, INK, deck_rect, 4, border_radius=42)
    # Composite onto the main surface with a shadow.
    deck_rect_on = deck.get_rect(center=(W // 2, 58))
    sh = deck.copy()
    sh.fill((0, 0, 0, 120), special_flags=pygame.BLEND_RGBA_MULT)
    s.blit(sh, (deck_rect_on.left + 3, deck_rect_on.top + 5))
    s.blit(deck, deck_rect_on)
    # Wordmark crown.
    txt = _yellow_text("SKATEBOARD!", 22, outline_w=3)
    s.blit(txt, txt.get_rect(center=(W // 2, deck_rect_on.top + 16)))
    # Score burst in the centre of the deck.
    _hb(s, W // 2, deck_rect_on.top + 62, str(score),
        ro=36, ri=22, font_size=32)
    return s


def variant_r3_c4_sign_post(base, score):
    """R3-C4 — Stacked sign-post. Two tiers inside ONE continuous
    outlined silhouette: top tier is a small SKATEBOARD! marquee,
    bottom tier is the halftone score in its bowl. The two tiers
    share an outer outline and a connecting waist — reads as a
    classic scoreboard with a header + a value."""
    s = base.copy()
    # Outer silhouette — narrow header on top, wider score chamber
    # below, joined by a short waist. We approximate with two stacked
    # rounded rects whose outlines we draw together so the bond looks
    # intentional.
    header = pygame.Rect(0, 0, 220, 32)
    body = pygame.Rect(0, 0, 180, 60)
    header.center = (W // 2, 26)
    body.center = (W // 2, header.bottom + 4 + body.height // 2)
    # Unified shadow first.
    _drop_shadow_rect(s, header, radius=8, offset=(3, 4))
    _drop_shadow_rect(s, body, radius=14, offset=(3, 4))
    # Header marquee — red plate with the wordmark.
    pygame.draw.rect(s, PLATE_RED, header, border_radius=8)
    pygame.draw.rect(s, INK, header, 3, border_radius=8)
    txt = _yellow_text("SKATEBOARD!", 20, outline_w=3)
    s.blit(txt, txt.get_rect(center=header.center))
    # Connecting waist — short vertical bar bonds header to body.
    waist = pygame.Rect(0, 0, 60, 8)
    waist.midtop = (W // 2, header.bottom - 1)
    pygame.draw.rect(s, PLATE_RED, waist)
    pygame.draw.rect(s, INK, waist, 3)
    # Score body — red plate (matches the marquee) holding the
    # halftone score burst as the value readout.
    pygame.draw.rect(s, PLATE_RED, body, border_radius=14)
    pygame.draw.rect(s, INK, body, 3, border_radius=14)
    _hb(s, body.centerx, body.centery, str(score),
        ro=24, ri=16, font_size=30)
    return s


def variant_r3_c5_burst_exclamation(base, score):
    """R3-C5 — Burst-as-exclamation. Reads as ONE word: the lettering
    spells "SKATEBOARD" then the halftone score burst IS the final
    "!". The burst's 10-spike silhouette becomes the punctuation, so
    the wordmark and the score live on the same reading line — no
    competing pieces, one flow. We slide the wordmark slightly left
    of centre to make room for the burst on the right."""
    s = base.copy()
    # Render the wordmark WITHOUT the trailing "!" — the burst will
    # be the punctuation. Size tuned so wordmark + burst fit W-12.
    word = _yellow_text("SKATEBOARD", 30, outline_w=4)
    # Compute layout: wordmark left, burst right, ~6 px gap.
    burst_diameter = 60   # ro*2 with a little slack for the spikes.
    gap = 4
    total_w = word.get_width() + gap + burst_diameter
    start_x = (W - total_w) // 2
    word_rect = word.get_rect(midleft=(start_x, 70))
    s.blit(word, word_rect)
    # Halftone score burst as the "!"
    burst_cx = word_rect.right + gap + burst_diameter // 2
    _hb(s, burst_cx, 70, str(score),
        ro=30, ri=18, font_size=26)
    # Subtle ink "i-dot" above the burst — sells the exclamation
    # mark reading by giving the burst a punctuation head.
    pygame.draw.circle(s, INK, (burst_cx, 32), 6)
    pygame.draw.circle(s, (255, 220, 30), (burst_cx, 32), 4)
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


if __name__ == "__main__":
    main()
