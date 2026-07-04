"""Round-1 exploration for the main-menu PROFILE entry.

Renders five genuinely distinct ways to turn the Profile menu item from a
plain button into a minimal character card that showcases Pip's CURRENT
look (the base parrot drawn by game.entities.Bird) with a small "records
inside" affordance — because Awards folds INTO Profile and a coin Store
(other branch) will let players re-skin Pip.

Every treatment is composited into a real 360x640 menu mock (SKYBIT
title, standing Pip, scarlet START hero, STORE / TOP 10 / SETTINGS chips)
so the panels are judged in context, then tiled into one 5-up sheet.
Reuses the live menu draw helpers + palette from game.hud so the study
looks like the shipped game rather than a stand-in.
"""
import os
import math
import pygame

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

pygame.init()
pygame.display.set_mode((8, 8))

from game.config import W, H
from game import parrot
from game.entities import Bird
from game.draw import WHITE, NEAR_BLACK, lerp_color
from game.hud import (
    _font, _outlined_text, _pill_btn, _volume_panel, _tracked_label,
    _draw_overlay_stars, _draw_mountain_silhouette,
    _draw_trophy, _draw_gear, _coin_icon, _draw_award_star,
    _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP, _RED_OUTLINE, _ORANGE_BORDER,
    _PANEL_DARK, _PANEL_LIGHTER, _AWSTAR_HI, _NIGHT_DEEP,
)

# A representative animation phase: draw_menu pulses the START pill's
# tappability glow at sin(title_t * 3.6); freezing near the crest shows
# each Profile frame carrying that same "tap me" halo at its brightest.
T = 0.55
GLOW = 0.5 + 0.5 * math.sin(T * 3.6)          # 0..1 tap-glow pulse
STARS = [(int(37 * i * 1.7 % W), int(23 + 71 * i * 1.3 % 210),
          1 + (i % 2), i * 0.9) for i in range(26)]


# ── Pip bust ────────────────────────────────────────────────────────────────
# A cropped head+chest of the ACTUAL base parrot, framed inside a soft
# night-sky window so it reads as "a picture of your character" rather
# than a second full-body Pip. Head center sits at sprite (38, 23);
# scaling zooms in and the window bottom crops the body to a bust.
def parrot_bust(w, h, shape="rrect", radius=12, zoom=1.9,
                anchor=(0.52, 0.47)):
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    # Deep-sky backdrop so the portrait window isn't a bald cutout — a
    # vertical navy wash with a warm crown glow behind Pip's head.
    for yy in range(h):
        t = yy / max(1, h - 1)
        surf.fill(lerp_color((30, 26, 74), (10, 6, 34), t),
                  (0, yy, w, 1))
    crown = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.circle(crown, (90, 74, 150, 90),
                       (int(w * anchor[0]), int(h * 0.34)), int(w * 0.55))
    surf.blit(crown, (0, 0))

    src = parrot.get_parrot(1, 0)
    sw, sh = src.get_size()
    scale = w * zoom / sw
    big = pygame.transform.smoothscale(src, (int(sw * scale),
                                             int(sh * scale)))
    bx = int(w * anchor[0] - 38 * scale)
    by = int(h * anchor[1] - 23 * scale)
    surf.blit(big, (bx, by))

    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    if shape == "circle":
        pygame.draw.circle(mask, (255, 255, 255, 255),
                           (w // 2, h // 2), min(w, h) // 2)
    else:
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h),
                         border_radius=radius)
    surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return surf


def tap_glow(surf, rect, shape="rrect", radius=14, strength=1.0):
    """Gentle gold halo whose alpha rides the START-pill pulse, so the
    Profile card reads as tappable chrome rather than passive scenery."""
    pad = 12
    glow = pygame.Surface((rect.width + pad * 2, rect.height + pad * 2),
                          pygame.SRCALPHA)
    for k in range(pad, 0, -1):
        a = int(strength * (46 + 30 * GLOW) * k / pad / 3.4)
        gr = pygame.Rect(pad - k, pad - k,
                         rect.width + k * 2, rect.height + k * 2)
        if shape == "circle":
            pygame.draw.circle(glow, (*_GOLD_BRIGHT, a), glow.get_rect().center,
                               rect.width // 2 + k)
        else:
            pygame.draw.rect(glow, (*_GOLD_BRIGHT, a), gr,
                             border_radius=radius + k)
    surf.blit(glow, (rect.x - pad, rect.y - pad))


def records_pip(surf, cx, cy, count="3"):
    """Small 'records inside' badge — a gold star token with a count so
    the folded-in Awards stay discoverable from the Profile card."""
    r = 12
    pygame.draw.circle(surf, (0, 0, 0, 120), (cx + 1, cy + 2), r + 1)
    pygame.draw.circle(surf, _GOLD_DEEP, (cx, cy), r)
    pygame.draw.circle(surf, _GOLD_BRIGHT, (cx, cy), r - 2)
    _draw_award_star(surf, cx - 4, cy, 6)
    f = _font(11, True)
    img = f.render(count, True, NEAR_BLACK)
    surf.blit(img, img.get_rect(center=(cx + 5, cy)))


# ── Shared menu mock ─────────────────────────────────────────────────────────
def menu_base():
    """The live menu minus its bottom trio: night sky, mountains, SKYBIT
    hero, standing Pip, START. Each concept overlays its own Profile card
    plus the STORE / TOP 10 / SETTINGS chip row."""
    surf = pygame.Surface((W, H)).convert_alpha()
    # Day-sky base so the night tint reads correctly, like the live menu.
    for yy in range(H):
        t = yy / (H - 1)
        surf.fill(lerp_color((90, 150, 205), (196, 168, 150), t), (0, yy, W, 1))
    dim = pygame.Surface((W, H), pygame.SRCALPHA)
    dim.fill((6, 1, 21, 150))
    surf.blit(dim, (0, 0))
    _draw_overlay_stars(surf, STARS, T)
    _draw_mountain_silhouette(surf, alpha=180)

    # Standing Pip mid-left, exactly where the menu parks him.
    Bird().draw(surf)

    pulse = 1.0 + math.sin(T * 2.4) * 0.04
    _outlined_text(surf, "SKYBIT", (W // 2, 126), size=int(72 * pulse), px=3)
    _outlined_text(surf, "POCKET  SKY  FLYER", (W // 2, 184),
                   size=22, px=2, shadow_offset=(2, 3))
    pygame.draw.line(surf, (*_ORANGE_BORDER, 120),
                     (W // 2 - 70, 208), (W // 2 + 70, 208), 1)

    btn_alpha = int(225 + math.sin(T * 3.6) * 30)
    _pill_btn(surf, (W // 2, 430), "START", size=24, alpha=btn_alpha,
              min_width=240, primary=True, dim=True, shadow=False)
    return surf


def bottom_chips(surf):
    """STORE · TOP 10 · SETTINGS — Awards has folded into Profile, so the
    freed slot becomes STORE (Pip's re-skin shop). Reuses the shipped
    chip language (_volume_panel body + icon + tracked caption)."""
    cy = H - 86
    tile_w, tgap, tile_h = 84, 8, 54
    tx = (W - (tile_w * 3 + tgap * 2)) // 2
    for label, kind in (("STORE", "coin"), ("TOP 10", "trophy"),
                        ("SETTINGS", "gear")):
        r = pygame.Rect(tx, cy - tile_h // 2, tile_w, tile_h)
        _volume_panel(surf, r, radius=13)
        if kind == "coin":
            _coin_icon(surf, r.centerx, cy - 5, 12)
        elif kind == "trophy":
            _draw_trophy(surf, r.centerx, cy - 5, 10)
        else:
            _draw_gear(surf, r.centerx, cy - 5, 12)
        _tracked_label(surf, label, (r.centerx, cy + 15), 10,
                       color=_AWSTAR_HI, track=1, alpha=210)
        tx += tile_w + tgap


def tri(surf, cx, cy, size, color):
    """Right-pointing chevron — the vendored font has no ▸ glyph, so the
    'tap through' cue is drawn."""
    pygame.draw.polygon(surf, color, [(cx - size // 2, cy - size),
                                      (cx + size // 2, cy),
                                      (cx - size // 2, cy + size)])


# Every treatment lives in the clear strip ABOVE the SKYBIT title (top
# y=86), so a corner character-card never crosses the wordmark — the
# genuinely "unused top corner" the tester called for.

# ── Concept 1 — Framed portrait card ─────────────────────────────────────────
# A bust in an ornate double-gold frame with corner studs and an engraved
# nameplate — the literal "portrait of your character" idiom.
def concept_framed(surf):
    fr = pygame.Rect(12, 6, 82, 76)
    tap_glow(surf, fr, radius=13)
    sh = pygame.Surface((fr.w + 8, fr.h + 8), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 110), sh.get_rect(), border_radius=15)
    surf.blit(sh, (fr.x - 3, fr.y + 4))
    pygame.draw.rect(surf, _GOLD_DEEP, fr, border_radius=13)
    pygame.draw.rect(surf, _GOLD_BRIGHT, fr.inflate(-4, -4), width=3,
                     border_radius=11)
    # Portrait window with the bust.
    win = pygame.Rect(fr.x + 8, fr.y + 8, fr.w - 16, 44)
    bust = parrot_bust(win.w, win.h, radius=7, zoom=2.0, anchor=(0.52, 0.5))
    surf.blit(bust, win.topleft)
    pygame.draw.rect(surf, _GOLD_DEEP, win, width=2, border_radius=7)
    for cx, cy in ((fr.left + 8, fr.top + 8), (fr.right - 8, fr.top + 8)):
        pygame.draw.circle(surf, _GOLD_PALE, (cx, cy), 3)
        pygame.draw.circle(surf, _GOLD_DEEP, (cx, cy), 3, 1)
    # Engraved nameplate along the frame foot.
    plate = pygame.Rect(fr.left + 7, win.bottom + 3, fr.w - 14, 14)
    pygame.draw.rect(surf, (18, 12, 40), plate, border_radius=5)
    pygame.draw.rect(surf, _GOLD_DEEP, plate, width=1, border_radius=5)
    _tracked_label(surf, "PROFILE", plate.center, 10, color=_GOLD_PALE,
                   track=2, alpha=240)
    records_pip(surf, fr.right - 1, fr.top - 1)


# ── Concept 2 — Pedestal / spotlight ─────────────────────────────────────────
# Pip staged on a lit plinth under a soft spotlight cone — a museum /
# hall-of-fame framing that says "here is your character, on show".
def concept_pedestal(surf):
    stage = pygame.Rect(8, 4, 104, 78)
    tap_glow(surf, stage, radius=16, strength=0.85)
    pnl = pygame.Surface(stage.size, pygame.SRCALPHA)
    pygame.draw.rect(pnl, (12, 8, 40, 226), pnl.get_rect(), border_radius=16)
    pygame.draw.rect(pnl, (*_GOLD_BRIGHT, 130), pnl.get_rect(), width=1,
                     border_radius=16)
    surf.blit(pnl, stage.topleft)
    cx = stage.centerx
    # Spotlight cone widening from an apex above onto the plinth.
    cone = pygame.Surface(stage.size, pygame.SRCALPHA)
    pygame.draw.polygon(cone, (255, 240, 190, 48),
                        [(stage.w // 2, 4), (20, stage.h - 20),
                         (stage.w - 20, stage.h - 20)])
    pygame.draw.polygon(cone, (255, 245, 205, 32),
                        [(stage.w // 2, 4), (32, stage.h - 22),
                         (stage.w - 32, stage.h - 22)])
    surf.blit(cone, stage.topleft)
    # Bust (circular, no hard frame — the stage IS the frame).
    bd = 46
    bust = parrot_bust(bd, bd, shape="circle", zoom=1.7, anchor=(0.5, 0.5))
    surf.blit(bust, (cx - bd // 2, stage.top + 8))
    # Plinth: elliptical top + short body + engraved face.
    py = stage.top + 52
    pygame.draw.ellipse(surf, _GOLD_DEEP, (cx - 34, py, 68, 12))
    pygame.draw.ellipse(surf, _GOLD_BRIGHT, (cx - 34, py, 68, 12), 2)
    face = pygame.Rect(cx - 32, py + 5, 64, 18)
    pygame.draw.rect(surf, (20, 14, 46), face, border_bottom_left_radius=6,
                     border_bottom_right_radius=6)
    pygame.draw.rect(surf, _GOLD_DEEP, face, width=1,
                     border_bottom_left_radius=6, border_bottom_right_radius=6)
    _tracked_label(surf, "PROFILE", (cx, face.centery), 10,
                   color=_GOLD_PALE, track=1, alpha=240)
    records_pip(surf, stage.right - 3, stage.top + 3)


# ── Concept 3 — Courier ID badge ─────────────────────────────────────────────
# Pip's delivery-courier ID: lanyard clip, a mugshot window, a name line
# and a RECORDS row — leans all the way into the ID-card idiom.
def concept_id_badge(surf):
    card = pygame.Rect(12, 14, 118, 68)
    tap_glow(surf, card, radius=11)
    # Lanyard clip poking out of the top edge.
    clip = pygame.Rect(card.centerx - 9, card.top - 10, 18, 14)
    pygame.draw.rect(surf, (70, 74, 86), clip, border_radius=4)
    pygame.draw.rect(surf, (150, 156, 170), clip, width=1, border_radius=4)
    pygame.draw.circle(surf, (18, 14, 30), (clip.centerx, clip.top + 4), 3)
    # Card body — pale ID stock with a scarlet header band.
    pygame.draw.rect(surf, (232, 226, 214), card, border_radius=10)
    pygame.draw.rect(surf, _GOLD_DEEP, card, width=2, border_radius=10)
    hdr = pygame.Rect(card.x, card.y, card.w, 18)
    head = pygame.Surface(hdr.size, pygame.SRCALPHA)
    pygame.draw.rect(head, (200, 40, 34), head.get_rect(),
                     border_top_left_radius=10, border_top_right_radius=10)
    surf.blit(head, hdr.topleft)
    _tracked_label(surf, "PROFILE", (hdr.centerx, hdr.centery), 10,
                   color=(255, 244, 224), track=2, alpha=255)
    # Mugshot window, left; text column, right.
    win = pygame.Rect(card.x + 7, hdr.bottom + 6, 40, 38)
    bust = parrot_bust(win.w, win.h, radius=5, zoom=1.9, anchor=(0.52, 0.5))
    surf.blit(bust, win.topleft)
    pygame.draw.rect(surf, (120, 96, 60), win, width=2, border_radius=5)
    tx = win.right + 8
    _tracked_label(surf, "PIP", (tx + 18, hdr.bottom + 12), 13,
                   color=(40, 30, 24), track=1, alpha=255)
    _tracked_label(surf, "COURIER", (tx + 18, hdr.bottom + 24), 8,
                   color=(120, 96, 70), track=1, alpha=255)
    # RECORDS row with a mini trophy + count + chevron — folded-in Awards.
    rr = pygame.Rect(tx - 2, hdr.bottom + 30, 58, 14)
    pygame.draw.rect(surf, (210, 200, 184), rr, border_radius=5)
    _draw_trophy(surf, rr.left + 8, rr.centery, 4)
    _tracked_label(surf, "3 AWARDS", (rr.centerx + 4, rr.centery), 8,
                   color=(40, 30, 24), track=0, alpha=255)
    tri(surf, rr.right - 6, rr.centery, 4, (120, 96, 70))


# ── Concept 4 — Circular avatar medallion ────────────────────────────────────
# A struck-coin roundel: gold ring, Pip bust inside, a PROFILE banner and
# a records pip — echoes the game's own coin language.
def concept_medallion(surf):
    cx, cy, R = 52, 42, 36
    ring_rect = pygame.Rect(cx - R, cy - R, R * 2, R * 2)
    tap_glow(surf, ring_rect, shape="circle", radius=R, strength=1.1)
    pygame.draw.circle(surf, (0, 0, 0, 120), (cx + 1, cy + 3), R + 2)
    pygame.draw.circle(surf, _GOLD_DEEP, (cx, cy), R)
    pygame.draw.circle(surf, _GOLD_BRIGHT, (cx, cy), R - 3)
    pygame.draw.circle(surf, _GOLD_PALE, (cx, cy), R - 3, 2)
    pygame.draw.circle(surf, _GOLD_DEEP, (cx, cy), R - 10)
    # Beaded rim — the coin-milling detail.
    for i in range(24):
        a = i / 24 * math.tau
        pygame.draw.circle(surf, _GOLD_PALE,
                           (int(cx + (R - 1.5) * math.cos(a)),
                            int(cy + (R - 1.5) * math.sin(a))), 1)
    bd = (R - 10) * 2
    bust = parrot_bust(bd, bd, shape="circle", zoom=1.7, anchor=(0.5, 0.5))
    surf.blit(bust, (cx - bd // 2, cy - bd // 2))
    # PROFILE banner slung across the roundel foot.
    ban = pygame.Rect(cx - 40, cy + R - 10, 80, 18)
    pygame.draw.rect(surf, (168, 34, 30), ban, border_radius=6)
    pygame.draw.rect(surf, _GOLD_BRIGHT, ban, width=1, border_radius=6)
    pygame.draw.polygon(surf, (120, 20, 18),
                        [(ban.left, ban.top), (ban.left - 7, ban.top),
                         (ban.left, ban.centery)])
    pygame.draw.polygon(surf, (120, 20, 18),
                        [(ban.right, ban.top), (ban.right + 7, ban.top),
                         (ban.right, ban.centery)])
    _tracked_label(surf, "PROFILE", ban.center, 10, color=(255, 244, 224),
                   track=2, alpha=255)
    records_pip(surf, cx + R - 4, cy - R + 6)


# ── Concept 5 — Clean tile with coin hint ────────────────────────────────────
# The restrained take: a wide chip carrying a thumbnail bust, PROFILE, and
# a subordinate coin "customize" hint — closest to the shipped chip family.
def concept_clean_tile(surf):
    tile = pygame.Rect(12, 12, 182, 58)
    tap_glow(surf, tile, radius=14, strength=0.8)
    _volume_panel(surf, tile, radius=14)
    # Round bust thumbnail on the left, ringed like an avatar.
    bd = 44
    bx, by = tile.x + 8, tile.centery - bd // 2
    pygame.draw.circle(surf, _GOLD_BRIGHT, (bx + bd // 2, by + bd // 2),
                       bd // 2 + 2)
    bust = parrot_bust(bd, bd, shape="circle", zoom=1.7, anchor=(0.5, 0.5))
    surf.blit(bust, (bx, by))
    lx = bx + bd + 12
    _tracked_label(surf, "PROFILE", (lx + 40, tile.y + 20), 14,
                   color=_GOLD_PALE, track=2, alpha=240)
    # Subordinate customize hint: coin glyph + label, quiet enough to read
    # as a secondary affordance under the name.
    _coin_icon(surf, lx + 8, tile.y + 40, 7)
    _tracked_label(surf, "CUSTOMIZE", (lx + 62, tile.y + 40), 9,
                   color=(206, 186, 150), track=1, alpha=210)
    tri(surf, tile.right - 16, tile.centery, 7, _GOLD_PALE)
    records_pip(surf, tile.right - 12, tile.top - 1)


CONCEPTS = [
    ("1 · FRAMED PORTRAIT", concept_framed),
    ("2 · PEDESTAL SPOTLIGHT", concept_pedestal),
    ("3 · COURIER ID BADGE", concept_id_badge),
    ("4 · AVATAR MEDALLION", concept_medallion),
    ("5 · CLEAN TILE + COIN", concept_clean_tile),
]


def build_panel(draw_fn):
    surf = menu_base()
    draw_fn(surf)
    bottom_chips(surf)
    return surf


def main():
    pad, gap, hdr = 16, 14, 44
    cols = len(CONCEPTS)
    sheet_w = pad * 2 + cols * W + (cols - 1) * gap
    sheet_h = pad * 2 + hdr + H
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((22, 18, 34))

    title_f = _font(26, True)
    t = title_f.render("SKYBIT · Profile menu-entry concepts — Round 1",
                       True, (240, 224, 180))
    sheet.blit(t, (pad, 10))

    lab_f = _font(18, True)
    x = pad
    for label, fn in CONCEPTS:
        panel = build_panel(fn)
        y = pad + hdr
        pygame.draw.rect(sheet, (8, 5, 20),
                         (x - 2, y - 2, W + 4, H + 4))
        sheet.blit(panel, (x, y))
        li = lab_f.render(label, True, (250, 236, 190))
        sheet.blit(li, li.get_rect(midtop=(x + W // 2, pad + 16)))
        x += W + gap

    out = os.path.join(os.path.dirname(__file__), "round_1.png")
    pygame.image.save(sheet, out)
    print("saved", out, sheet.get_size())


if __name__ == "__main__":
    main()
