"""Design-only mockup: five distinct ways to add PROFILE + STORE entries to
the Skybit main menu. Renders the real menu frame as the base, overlays each
concept, and tiles the five 360x640 frames into a labeled showcase board.

This is a review artifact — nothing here is wired into the live game. It reuses
the genuine HUD vocabulary (pills, volume panels, struck gold glyphs, palette)
so the explorations read like the shipped menu, not a sketch.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import sys
import math
import pygame

# Allow running the file directly from anywhere — the game package lives two
# levels up (repo root), which isn't on sys.path when invoked as a script.
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from game.config import W, H
from game.hud import (
    _pill_btn, _outline_pill_btn, _volume_panel, _tracked_label, _font,
    _draw_award_star, _draw_trophy, _draw_gear,
    _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP, _PANEL_DARK, _PANEL_LIGHTER,
    _NIGHT_DEEP, _AWSTAR_HI, _SCARLET_TOP, _SCARLET_BOT,
)

_SS = 4  # supersample factor for the two new struck-gold glyphs
_GLYPH_GOLD = _GOLD_BRIGHT
_GLYPH_HI = _AWSTAR_HI
_GLYPH_DEEP = _GOLD_DEEP
_GLYPH_RIM = (140, 90, 8)


# ── Base menu frame ─────────────────────────────────────────────────────────
def base_frame():
    from game.scenes import App, STATE_MENU
    app = App()
    app.state = STATE_MENU
    for _ in range(3):
        app.world.update(1 / 60)
    app._render()
    return app.screen.copy()


def erase_zone(frame, rect):
    """Repaint a UI band with the local sky/mountain gradient by sampling a
    clean off-centre column, so a redrawn bottom row sits on real background
    rather than a flat rectangle."""
    col = frame.subsurface(pygame.Rect(18, rect.top, 1, rect.height)).copy()
    frame.blit(pygame.transform.scale(col, (rect.width, rect.height)),
               rect.topleft)


# ── New struck-gold glyphs (Store + Profile), same family as star/trophy/gear ─
def _ss_glyph(box, draw_fn):
    B = box * _SS
    s = pygame.Surface((B, B), pygame.SRCALPHA)
    draw_fn(s, B, _SS)
    return pygame.transform.smoothscale(s, (box, box))


def _draw_cart(surf, cx, cy, size):
    """Shopping cart — the Store glyph. size ~ half-extent in px."""
    box = int(size * 2 + 8)
    g = _ss_glyph(box, _cart_ss)
    surf.blit(g, g.get_rect(center=(cx, cy)))


def _cart_ss(s, B, k):
    gold, hi, deep, rim = _GLYPH_GOLD, _GLYPH_HI, _GLYPH_DEEP, _GLYPH_RIM
    lw = max(2, int(1.6 * k))

    def P(x, y):
        return (x * B, y * B)

    # Handle bar up to the basket lip.
    pygame.draw.line(s, gold, P(0.10, 0.20), P(0.26, 0.20), lw)
    pygame.draw.line(s, gold, P(0.26, 0.20), P(0.34, 0.34), lw)
    # Basket — trapezoid (wider at top), filled deep with a gold rim.
    basket = [P(0.30, 0.34), P(0.84, 0.34), P(0.74, 0.62), P(0.40, 0.62)]
    pygame.draw.polygon(s, deep, basket)
    pygame.draw.polygon(s, gold, basket, lw)
    pygame.draw.line(s, hi, P(0.32, 0.345), P(0.82, 0.345), max(1, k))
    # Two vertical grid ribs inside the basket.
    pygame.draw.line(s, gold, P(0.48, 0.35), P(0.52, 0.61), max(1, k))
    pygame.draw.line(s, gold, P(0.62, 0.35), P(0.63, 0.61), max(1, k))
    # Wheels.
    for wx in (0.46, 0.68):
        pygame.draw.circle(s, gold, P(wx, 0.76), int(0.065 * B))
        pygame.draw.circle(s, deep, P(wx, 0.76), int(0.065 * B), max(1, k))
        pygame.draw.circle(s, hi, (int(wx * B - 0.02 * B), int(0.74 * B)),
                           max(1, int(0.02 * B)))
    # Axle stubs from basket to wheels.
    pygame.draw.line(s, gold, P(0.40, 0.62), P(0.46, 0.72), lw)
    pygame.draw.line(s, gold, P(0.74, 0.62), P(0.68, 0.72), lw)


def _draw_coinstack(surf, cx, cy, size):
    """Stacked coins — alternate Store glyph reading as 'shop / value'."""
    box = int(size * 2 + 8)
    g = _ss_glyph(box, _coinstack_ss)
    surf.blit(g, g.get_rect(center=(cx, cy)))


def _coinstack_ss(s, B, k):
    gold, hi, deep = _GLYPH_GOLD, _GLYPH_HI, _GLYPH_DEEP
    ew, eh = 0.56 * B, 0.20 * B
    cxp = 0.5 * B
    for i, cyp in enumerate((0.66, 0.52, 0.38)):
        yy = cyp * B
        rect = pygame.Rect(int(cxp - ew / 2), int(yy - eh / 2), int(ew), int(eh))
        pygame.draw.ellipse(s, deep,
                            (rect.x, rect.y + int(0.05 * B), rect.w, rect.h))
        pygame.draw.ellipse(s, gold, rect)
        pygame.draw.ellipse(s, hi, rect, max(1, k))
    # A slim gold "$" on the top coin face.
    f = _font(int(0.26 * B), True)
    dollar = f.render("$", True, deep)
    s.blit(dollar, dollar.get_rect(center=(int(cxp), int(0.38 * B))))


def _draw_avatar(surf, cx, cy, size, ring=False):
    """Courier bust — the Profile glyph. ring=True encloses it in an ID disc."""
    box = int(size * 2 + 8)
    g = _ss_glyph(box, lambda s, B, k: _avatar_ss(s, B, k, ring))
    surf.blit(g, g.get_rect(center=(cx, cy)))


def _avatar_ss(s, B, k, ring):
    gold, hi, deep = _GLYPH_GOLD, _GLYPH_HI, _GLYPH_DEEP
    cxp = 0.5 * B
    if ring:
        pygame.draw.circle(s, deep, (int(cxp), int(0.5 * B)), int(0.44 * B))
        pygame.draw.circle(s, gold, (int(cxp), int(0.5 * B)), int(0.44 * B),
                           max(2, int(1.5 * k)))
    # Shoulders — rounded bust.
    shoulders = [(0.24 * B, 0.80 * B), (0.30 * B, 0.62 * B),
                 (0.70 * B, 0.62 * B), (0.76 * B, 0.80 * B)]
    pygame.draw.polygon(s, deep, [(x + k, y + k) for x, y in shoulders])
    pygame.draw.polygon(s, gold, shoulders)
    # Head.
    hy = 0.40 * B
    pygame.draw.circle(s, deep, (int(cxp), int(hy + k)), int(0.16 * B))
    pygame.draw.circle(s, gold, (int(cxp), int(hy)), int(0.16 * B))
    pygame.draw.circle(s, hi, (int(cxp - 0.05 * B), int(hy - 0.05 * B)),
                       int(0.05 * B))


def _draw_crest(surf, cx, cy, size):
    """Courier ID shield crest with a bust inside — Profile as an emblem."""
    box = int(size * 2 + 10)
    g = _ss_glyph(box, _crest_ss)
    surf.blit(g, g.get_rect(center=(cx, cy)))


def _crest_ss(s, B, k):
    gold, hi, deep = _GLYPH_GOLD, _GLYPH_HI, _GLYPH_DEEP

    def P(x, y):
        return (x * B, y * B)

    shield = [P(0.5, 0.10), P(0.84, 0.24), P(0.84, 0.52),
              P(0.5, 0.88), P(0.16, 0.52), P(0.16, 0.24)]
    pygame.draw.polygon(s, (*_PANEL_DARK, 255), shield)
    pygame.draw.polygon(s, gold, shield, max(2, int(1.6 * k)))
    pygame.draw.line(s, hi, P(0.20, 0.25), P(0.5, 0.13), max(1, k))
    # Bust inside the shield.
    cxp = 0.5 * B
    shoulders = [P(0.32, 0.66), P(0.37, 0.54), P(0.63, 0.54), P(0.68, 0.66)]
    pygame.draw.polygon(s, gold, shoulders)
    pygame.draw.circle(s, gold, (int(cxp), int(0.42 * B)), int(0.12 * B))
    pygame.draw.circle(s, deep, (int(cxp), int(0.42 * B)), int(0.12 * B),
                       max(1, k))


def _new_pip(surf, cx, cy):
    """Small scarlet 'NEW' badge — the monetization nudge on Store."""
    f = _font(9, True)
    img = f.render("NEW", True, (255, 250, 240))
    w, h = img.get_width() + 10, img.get_height() + 5
    pill = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(pill, _SCARLET_TOP, (0, 0, w, h), border_radius=h // 2)
    pygame.draw.rect(pill, _GOLD_BRIGHT, (0, 0, w, h), width=1,
                     border_radius=h // 2)
    pill.blit(img, img.get_rect(center=(w // 2, h // 2)))
    surf.blit(pill, pill.get_rect(center=(cx, cy)))


def _chip(surf, rect, kind, label):
    """A utility/nav chip: volume panel + centred glyph + tracked caption,
    matching the shipped AWARDS/TOP 10/SETTINGS trio."""
    _volume_panel(surf, rect, radius=13)
    gy = rect.centery - int(rect.height * 0.14)
    gs = 11 if rect.height < 52 else 12
    if kind == "star":
        _draw_award_star(surf, rect.centerx, gy, gs)
    elif kind == "trophy":
        _draw_trophy(surf, rect.centerx, gy, gs - 1)
    elif kind == "gear":
        _draw_gear(surf, rect.centerx, gy, gs)
    elif kind == "cart":
        _draw_cart(surf, rect.centerx, gy, gs)
    elif kind == "coin":
        _draw_coinstack(surf, rect.centerx, gy, gs)
    elif kind == "avatar":
        _draw_avatar(surf, rect.centerx, gy, gs)
    cap_y = rect.bottom - 10
    _tracked_label(surf, label, (rect.centerx, cap_y), 10,
                   color=_AWSTAR_HI, track=1, alpha=210)


# ── The five concepts ────────────────────────────────────────────────────────
def concept_1(base):
    """Five-chip row — one unified band of five narrower icon-forward chips."""
    f = base.copy()
    band = pygame.Rect(0, 500, W, H - 500)
    erase_zone(f, band)
    cy = H - 74
    tw, gap, th = 64, 6, 58
    total = tw * 5 + gap * 4
    tx = (W - total) // 2
    specs = [("AWARDS", "star"), ("TOP 10", "trophy"), ("PROFILE", "avatar"),
             ("STORE", "cart"), ("SETTINGS", "gear")]
    for label, kind in specs:
        r = pygame.Rect(tx, cy - th // 2, tw, th)
        _chip(f, r, kind, label)
        if kind == "cart":
            _new_pip(f, r.right - 6, r.top + 2)
        tx += tw + gap
    return f


def concept_2(base):
    """Two tiers — wide labeled PROFILE + STORE feature tiles over the utility
    trio, START still the hero above."""
    f = base.copy()
    band = pygame.Rect(0, 470, W, H - 470)
    erase_zone(f, band)

    # Feature tier — two wide tiles with the glyph on the left, label right.
    ftw, fgap, fth = 132, 12, 46
    fy = 496
    fx = (W - (ftw * 2 + fgap)) // 2
    for label, kind, is_store in (("PROFILE", "avatar", False),
                                  ("STORE", "cart", True)):
        r = pygame.Rect(fx, fy - fth // 2, ftw, fth)
        _volume_panel(f, r, radius=14)
        gx = r.x + 26
        if kind == "avatar":
            _draw_avatar(f, gx, r.centery, 14, ring=True)
        else:
            _draw_cart(f, gx, r.centery, 14)
        _tracked_label(f, label, (r.x + 46 + (r.right - (r.x + 46)) // 2,
                                  r.centery), 15, color=_GOLD_PALE, track=1,
                       alpha=235)
        if is_store:
            _new_pip(f, r.right - 4, r.top + 2)
        fx += ftw + fgap

    # Utility trio — unchanged shipped layout.
    cy = H - 70
    tw, gap, th = 84, 8, 50
    tx = (W - (tw * 3 + gap * 2)) // 2
    for label, kind in (("AWARDS", "star"), ("TOP 10", "trophy"),
                        ("SETTINGS", "gear")):
        r = pygame.Rect(tx, cy - th // 2, tw, th)
        _chip(f, r, kind, label)
        tx += tw + gap
    return f


def concept_3(base):
    """Corner icons — PROFILE crest top-left + STORE cart (NEW pip) top-right,
    shipped trio untouched."""
    f = base.copy()

    def corner_badge(cx, cy, kind):
        r = 26
        badge = pygame.Surface((r * 2 + 8, r * 2 + 8), pygame.SRCALPHA)
        c = (r + 4, r + 4)
        for i in range(5, 0, -1):
            pygame.draw.circle(badge, (*_GOLD_BRIGHT, 10 * i),
                               c, r + i)
        pygame.draw.circle(badge, (*_PANEL_DARK, 235), c, r)
        pygame.draw.circle(badge, _GOLD_BRIGHT, c, r, 2)
        f.blit(badge, (cx - c[0], cy - c[1]))

    corner_badge(40, 40, "profile")
    _draw_crest(f, 40, 39, 15)
    _tracked_label(f, "PROFILE", (40, 76), 9, color=_AWSTAR_HI, track=1,
                   alpha=210)

    corner_badge(W - 40, 40, "store")
    _draw_cart(f, W - 40, 41, 14)
    _new_pip(f, W - 40 + 20, 40 - 22)
    _tracked_label(f, "STORE", (W - 40, 76), 9, color=_AWSTAR_HI, track=1,
                   alpha=210)
    return f


def concept_4(base):
    """Profile-hub reorg — a clean PROFILE · STORE · SETTINGS trio; Profile
    absorbs Awards + Leaderboard, so those chips retire."""
    f = base.copy()
    band = pygame.Rect(0, 495, W, H - 495)
    erase_zone(f, band)
    cy = H - 78
    tw, gap, th = 96, 12, 62
    tx = (W - (tw * 3 + gap * 2)) // 2
    for label, kind, is_store in (("PROFILE", "avatar", False),
                                  ("STORE", "cart", True),
                                  ("SETTINGS", "gear", False)):
        r = pygame.Rect(tx, cy - th // 2, tw, th)
        _volume_panel(f, r, radius=14)
        gy = r.centery - int(r.height * 0.12)
        if kind == "avatar":
            _draw_avatar(f, r.centerx, gy, 15, ring=True)
        elif kind == "cart":
            _draw_cart(f, r.centerx, gy, 15)
        else:
            _draw_gear(f, r.centerx, gy, 14)
        _tracked_label(f, label, (r.centerx, r.bottom - 11), 11,
                       color=_AWSTAR_HI, track=1, alpha=215)
        if is_store:
            _new_pip(f, r.right - 8, r.top + 2)
        tx += tw + gap
    return f


def concept_5(base):
    """Store-hero — a bright STORE feature button (coin + NEW), PROFILE as an
    avatar chip, utility trio trimmed to a 4-chip row; START still dominates."""
    f = base.copy()
    band = pygame.Rect(0, 466, W, H - 466)
    erase_zone(f, band)

    # STORE hero — gold outline pill (secondary to START's scarlet) with a
    # coin stack + NEW badge, so monetization is prominent yet not the CTA.
    hero = _outline_pill_btn(f, (W // 2, 500), "STORE", size=17,
                             min_width=176, pad_x=54)
    _draw_coinstack(f, hero.x + 26, hero.centery, 13)
    _new_pip(f, hero.right - 2, hero.top + 1)

    # Bottom row — PROFILE joins a trimmed utility set as four slim chips.
    cy = H - 66
    tw, gap, th = 66, 8, 52
    tx = (W - (tw * 4 + gap * 3)) // 2
    for label, kind in (("PROFILE", "avatar"), ("AWARDS", "star"),
                        ("TOP 10", "trophy"), ("SETTINGS", "gear")):
        r = pygame.Rect(tx, cy - th // 2, tw, th)
        _chip(f, r, kind, label)
        tx += tw + gap
    return f


# ── Showcase board ───────────────────────────────────────────────────────────
_CAPTIONS = [
    ("1  FIVE-CHIP ROW",
     "One unified band of 5 slim icon chips"),
    ("2  TWO TIERS",
     "Wide PROFILE + STORE tiles over the trio"),
    ("3  CORNER ICONS",
     "Crest + cart in the corners, trio untouched"),
    ("4  PROFILE HUB",
     "PROFILE absorbs Awards + Top 10; clean 3-tile"),
    ("5  STORE HERO",
     "Bright STORE button; PROFILE as an avatar chip"),
]


def build_showcase(frames):
    sc = 0.80
    fw, fh = int(W * sc), int(H * sc)
    cap_h = 52
    title_h = 88
    cols, gap, margin = 3, 30, 40
    cell_w, cell_h = fw, fh + cap_h
    rows = 2
    board_w = margin * 2 + cols * cell_w + (cols - 1) * gap
    board_h = title_h + rows * cell_h + (rows - 1) * gap + margin

    board = pygame.Surface((board_w, board_h))
    for y in range(board_h):
        t = y / board_h
        c = (int(10 + 6 * t), int(6 + 4 * t), int(26 + 10 * t))
        pygame.draw.line(board, c, (0, y), (board_w, y))

    tf = _font(34, True)
    title = tf.render("SKYBIT  MAIN MENU  —  PROFILE + STORE  —  5 CONCEPTS",
                      True, _GOLD_PALE)
    board.blit(title, title.get_rect(center=(board_w // 2, 40)))
    sf = _font(16, True)
    sub = sf.render("design-only mockup  ·  round 1  ·  START stays the hero",
                    True, (170, 170, 200))
    board.blit(sub, sub.get_rect(center=(board_w // 2, 70)))

    # Top row: concepts 1-3; bottom row: concepts 4-5 centred.
    layout = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1)]
    for idx, (frame, (row, col)) in enumerate(zip(frames, layout)):
        n_in_row = 3 if row == 0 else 2
        row_w = n_in_row * cell_w + (n_in_row - 1) * gap
        x0 = (board_w - row_w) // 2
        x = x0 + col * (cell_w + gap)
        y = title_h + row * (cell_h + gap)
        scaled = pygame.transform.smoothscale(frame, (fw, fh))
        pygame.draw.rect(board, _GOLD_DEEP, (x - 2, y - 2, fw + 4, fh + 4),
                         border_radius=6)
        board.blit(scaled, (x, y))
        # Caption block.
        head, desc = _CAPTIONS[idx]
        cf = _font(19, True)
        himg = cf.render(head, True, _GOLD_BRIGHT)
        board.blit(himg, (x + 4, y + fh + 8))
        df = _font(14, True)
        dimg = df.render(desc, True, (200, 200, 215))
        board.blit(dimg, (x + 4, y + fh + 30))
    return board


def main():
    pygame.init()
    pygame.display.set_mode((1, 1))
    base = base_frame()
    frames = [concept_1(base), concept_2(base), concept_3(base),
              concept_4(base), concept_5(base)]
    board = build_showcase(frames)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "round_1.png")
    pygame.image.save(board, out)
    print("wrote", out, board.get_size())


if __name__ == "__main__":
    main()
