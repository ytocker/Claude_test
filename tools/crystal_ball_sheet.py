"""Headless exploration sheet for the Crystal Ball curio (Profile ARCADE).

Five distinct takes on a procedural glass-orb fortune curio living on an
obsidian ARCADE card. Reuses the store's Obsidian-&-Gold primitives so the
explorations read in the real product palette. Writes the combined sheet only;
git is the orchestrator's job.
"""
from __future__ import annotations

import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1, 1))

from game.config import W, H  # noqa: E402  (W=360, H=640)
from game.hud import _font, _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP  # noqa: E402
from game.draw import UI_CREAM, NEAR_BLACK, WHITE, lerp_color, rounded_rect  # noqa: E402
from game.store import (  # noqa: E402
    _vgrad_panel, _drop_shadow, _inset_disc, _gem, _gradient_text, _soft_glow,
    _gold_rule, _OBS_TOP, _OBS_BOT, _BG_STOPS,
)

# Smoky teal/gold fog hues — deliberately NOT a saturated rarity purple, so the
# orb never competes with the rarity gem language that owns hue meaning.
_FOG_TEAL = (54, 150, 150)
_FOG_TEAL_DK = (16, 54, 60)
_FOG_GOLD = (224, 176, 78)
_FOG_MURK = (96, 70, 40)        # bad-streak murky brown
_FOG_MURK_DK = (40, 28, 16)
_FOG_CLEAR = (150, 214, 196)    # flying-well clear/bright
_GLASS_RIM = (208, 226, 224)

T = 0.62  # frozen "churning" phase used across the sheet for the live look


# ── orb builder ──────────────────────────────────────────────────────────────
def _orb(r, fog_a, fog_b, glow_col, glow_a, t, churn=0.0, reveal=False):
    """A procedural glass sphere on its own SRCALPHA surface.

    Layered translucent fog blobs drifting on `t`, a dark glass falloff toward
    the rim (so it reads as a sphere, not a flat disc), a crisp specular cap and
    a soft lower bounce-light. `churn` (0..1) lifts inner brightness + blob count
    for the "predicting" state; `reveal` punches a bright core for the moment a
    prophecy surfaces.
    """
    d = r * 2
    pad = max(8, r // 3)
    surf = pygame.Surface((d + pad * 2, d + pad * 2), pygame.SRCALPHA)
    cx = cy = r + pad

    # Glass body: a lit, smoky interior (NOT black) that falls off toward the
    # rim so curvature reads. Centre carries the fog tone so the sphere glows
    # from within; only the outer ring darkens to a deep glass edge.
    body_lit = lerp_color(fog_a, fog_b, 0.45)
    body_lit = lerp_color(body_lit, WHITE, 0.10)
    body_edge = lerp_color(fog_b, (8, 12, 16), 0.55)
    for i in range(r, 0, -1):
        f = i / r
        base = lerp_color(body_lit, body_edge, f ** 1.5)
        pygame.draw.circle(surf, (*base, 255), (cx, cy), i)

    # Inner fog: several translucent blobs orbiting on slow, incommensurate
    # periods so the swirl never visibly loops. Clipped to the sphere by a mask.
    fog = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    n_blobs = 5 + int(churn * 3)
    for k in range(n_blobs):
        ph = t * (0.5 + 0.18 * k) + k * 2.39996
        orbit = r * (0.18 + 0.30 * ((k * 0.37 + 0.2) % 1.0))
        bx = cx + math.cos(ph) * orbit
        by = cy + math.sin(ph * 0.83 + k) * orbit * 0.8
        br = int(r * (0.34 + 0.20 * ((k * 0.53) % 1.0)))
        col = lerp_color(fog_a, lerp_color(fog_a, WHITE, 0.25),
                         (k / max(1, n_blobs - 1)))
        a = int((58 + 34 * churn) * (0.55 + 0.45 * math.sin(ph * 1.3)))
        for layer in range(3, 0, -1):
            rr = int(br * layer / 3)
            aa = int(a * (1 - (layer - 1) / 3) ** 1.4)
            if rr <= 0 or aa <= 0:
                continue
            g = pygame.Surface((rr * 2 + 2, rr * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(g, (*col, aa), (rr + 1, rr + 1), rr)
            fog.blit(g, (int(bx) - rr - 1, int(by) - rr - 1),
                     special_flags=pygame.BLEND_ADD)

    # Inner glow core — the "energy" of the orb; swells with churn, blooms on
    # reveal so the prophecy feels like it surfaces from inside.
    core_r = int(r * (0.30 + 0.18 * churn))
    core_a = int(glow_a * (0.6 + 0.7 * churn))
    if reveal:
        core_r = int(r * 0.5)
        core_a = min(255, int(glow_a * 1.5))
    for layer in range(6, 0, -1):
        rr = int(core_r * layer / 6) + 2
        aa = int(core_a * (1 - (layer - 1) / 6) ** 1.8)
        g = pygame.Surface((rr * 2 + 2, rr * 2 + 2), pygame.SRCALPHA)
        cy_off = int(r * 0.06 * math.sin(t * 0.7))
        pygame.draw.circle(g, (*glow_col, aa), (rr + 1, rr + 1), rr)
        fog.blit(g, (cx - rr - 1, cy + cy_off - rr - 1),
                 special_flags=pygame.BLEND_ADD)

    mask = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (cx, cy), r - 1)
    fog.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(fog, (0, 0))

    # Glass shell: a thin cool keyline all round + a bright glassy rim arc at the
    # top-left and a warm bounce arc at the lower-right. Kept thin so it reads as
    # a refractive glass edge, never a solid metal ring.
    pygame.draw.circle(surf, (*_GLASS_RIM, 55), (cx, cy), r, 1)
    arc_box = pygame.Rect(cx - r + 2, cy - r + 2, d - 4, d - 4)
    pygame.draw.arc(surf, (*WHITE, 170), arc_box, math.radians(70),
                    math.radians(150), 2)
    pygame.draw.arc(surf, (*_FOG_GOLD, 80), arc_box, math.radians(255),
                    math.radians(320), 2)

    # Specular highlight cap + a tiny secondary pip (wet-glass read).
    hl = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    hx, hy = cx - int(r * 0.34), cy - int(r * 0.40)
    pygame.draw.circle(hl, (255, 255, 255, 200), (hx, hy), max(2, r // 6))
    pygame.draw.circle(hl, (255, 255, 255, 120), (hx, hy), max(3, r // 4), 1)
    pygame.draw.circle(hl, (255, 255, 255, 230),
                       (cx + int(r * 0.30), cy + int(r * 0.34)), max(1, r // 12))
    # Soften the highlight cap so it's a glow, not a hard dot.
    for k in range(3, 0, -1):
        rr = max(2, r // 6) + k * 2
        g = pygame.Surface((rr * 2, rr * 2), pygame.SRCALPHA)
        pygame.draw.circle(g, (255, 255, 255, 40), (rr, rr), rr)
        hl.blit(g, (hx - rr, hy - rr), special_flags=pygame.BLEND_ADD)
    surf.blit(hl, (0, 0))
    return surf, (cx, cy)


def _claw_stand(surf, cx, base_y, span, h):
    """A small three-prong gold claw foot cradling the orb: two outer talons
    curling up + a central post on a stepped plinth. Pure polygons, gold palette.
    """
    deep = _GOLD_DEEP
    for sgn in (-1, 1):
        x0 = cx + sgn * int(span * 0.16)
        tip_x = cx + sgn * int(span * 0.5)
        pts = [
            (x0, base_y - h),
            (cx + sgn * int(span * 0.30), base_y - int(h * 0.45)),
            (tip_x, base_y - int(h * 0.78)),     # talon tip curling up to cradle
            (tip_x - sgn * 3, base_y - int(h * 0.5)),
            (cx + sgn * int(span * 0.28), base_y - int(h * 0.2)),
            (x0 + sgn * 2, base_y),
        ]
        pygame.draw.polygon(surf, _GOLD_BRIGHT, pts)
        pygame.draw.polygon(surf, deep, pts, 1)
        # lit edge down the inner face
        pygame.draw.line(surf, _GOLD_PALE, pts[0], (x0 + sgn * 2, base_y), 1)
    # central post
    pygame.draw.polygon(surf, lerp_color(_GOLD_BRIGHT, deep, 0.3),
                        [(cx - 4, base_y - h + 4), (cx + 4, base_y - h + 4),
                         (cx + 6, base_y), (cx - 6, base_y)])
    # stepped plinth
    rounded_rect(surf, pygame.Rect(cx - span // 2, base_y, span, 7), 3, _GOLD_DEEP)
    rounded_rect(surf, pygame.Rect(cx - span // 2 + 2, base_y + 1, span - 4, 3),
                 1, _GOLD_BRIGHT)


def _cushion_stand(surf, cx, base_y, span, h):
    """An obsidian/gold ring cushion the orb rests in (alternative to the claw):
    a tufted ellipse with a gold piping rim and a dark recessed seat."""
    cush = pygame.Rect(cx - span // 2, base_y - h, span, h * 2)
    pygame.draw.ellipse(surf, (24, 20, 30), cush)
    pygame.draw.ellipse(surf, _GOLD_DEEP, cush, 2)
    inner = cush.inflate(-span // 4, -h)
    pygame.draw.ellipse(surf, (12, 10, 18), inner)
    pygame.draw.ellipse(surf, (*_GOLD_BRIGHT, 160),
                        pygame.Rect(cush.x + 4, cush.y + 2, span - 8, 4))


# ── shared ARCADE card chrome ────────────────────────────────────────────────
def _arcade_card(surf, rect, title="CRYSTAL BALL"):
    """Obsidian ARCADE card with a gold-rim header band — the home the orb sits
    on. Matches the store/profile card body + bezel so it reads as one product."""
    _drop_shadow(surf, rect, 16, blur=6, alpha=150)
    surf.blit(_vgrad_panel(rect.w, rect.h, 16, _OBS_TOP, _OBS_BOT, 254),
              rect.topleft)
    pygame.draw.rect(surf, (*_GOLD_DEEP, 210), rect.inflate(-7, -7), width=2,
                     border_radius=11)
    pygame.draw.rect(surf, (*_GOLD_BRIGHT, 150), rect, width=1, border_radius=16)
    # header band
    sheen = pygame.Surface((rect.w - 12, 18), pygame.SRCALPHA)
    for y in range(18):
        pygame.draw.line(sheen, (255, 255, 255, int(26 * (1 - y / 18))),
                         (0, y), (rect.w - 12, y))
    surf.blit(sheen, (rect.x + 6, rect.y + 5))
    hf = _font(13, True)
    _gradient_text(surf, title, hf, (rect.centerx, rect.y + 16),
                   _GOLD_PALE, _GOLD_BRIGHT, shadow=True)
    _gold_rule(surf, rect.x + 22, rect.right - 22, rect.y + 30)


def _accuracy_chip(surf, cx, cy, pct=91):
    """A small PROPHECY ACCURACY readout chip in the unified pill silhouette."""
    f = _font(9, True)
    lbl = f"PROPHECY ACCURACY  {pct}%"
    timg = f.render(lbl, True, _GOLD_PALE)
    w = timg.get_width() + 22
    h = 18
    r = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    surf.blit(_vgrad_panel(w, h, h // 2, (44, 34, 20), (22, 16, 9), 252),
              r.topleft)
    pygame.draw.rect(surf, (*_GOLD_BRIGHT, 170), r, width=1, border_radius=h // 2)
    # tiny crystal-eye glyph at the left
    pygame.draw.circle(surf, _FOG_TEAL, (r.x + 9, cy), 3)
    pygame.draw.circle(surf, _GOLD_PALE, (r.x + 9, cy), 3, 1)
    surf.blit(timg, timg.get_rect(midleft=(r.x + 16, cy)))


def _prophecy_banner(surf, rect, text, accent=_GOLD_BRIGHT):
    """A speech-banner prophecy card: an obsidian ribbon with a notched left
    flag, gold piping and gradient-gold text, with a small pointer up to the orb.
    """
    # pointer notch
    pcx = rect.centerx
    pygame.draw.polygon(surf, _OBS_TOP,
                        [(pcx - 8, rect.y + 1), (pcx + 8, rect.y + 1),
                         (pcx, rect.y - 8)])
    surf.blit(_vgrad_panel(rect.w, rect.h, 9, (30, 26, 36), (14, 12, 22), 252),
              rect.topleft)
    pygame.draw.rect(surf, (*accent, 180), rect, width=1, border_radius=9)
    pygame.draw.polygon(surf, (*accent, 180),
                        [(pcx - 8, rect.y + 1), (pcx + 8, rect.y + 1),
                         (pcx, rect.y - 8)], 1)
    _wrap_text(surf, text, rect.inflate(-18, -10), 11, _GOLD_PALE, accent)


def _wrap_text(surf, text, rect, size, top, bot):
    """Center-wrapped gradient-gold prophecy text inside `rect`."""
    f = _font(size, True)
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if f.size(trial)[0] <= rect.w:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    lh = f.get_height() - 1
    total = lh * len(lines)
    y0 = rect.centery - total // 2 + lh // 2
    for i, ln in enumerate(lines):
        _gradient_text(surf, ln, f, (rect.centerx, y0 + i * lh), top, bot,
                       shadow=True)


# ── the five versions ────────────────────────────────────────────────────────
def v1_idle_claw(surf, rect):
    """V1 — Claw stand + speech-banner. IDLE state. Classic crystal-ball read:
    a teal/gold orb dormant in a gold claw foot, a quiet accuracy chip, no
    prophecy yet (a 'TAP TO DIVINE' invite hovers in the fog)."""
    _arcade_card(surf, rect, "CRYSTAL BALL")
    cx = rect.centerx
    orb_r = 54
    orb_cy = rect.y + 112
    _soft_glow(surf, cx, orb_cy, int(orb_r * 1.25), _FOG_TEAL, 34, layers=5)
    orb, (ox, oy) = _orb(orb_r, _FOG_TEAL, _FOG_TEAL_DK, _FOG_GOLD, 120, T,
                         churn=0.0)
    _claw_stand(surf, cx, orb_cy + orb_r - 6, orb_r + 24, 26)
    surf.blit(orb, orb.get_rect(center=(cx, orb_cy)))
    inv = _font(10, True).render("TAP TO DIVINE", True, _GOLD_PALE)
    inv.set_alpha(150)
    surf.blit(inv, inv.get_rect(center=(cx, orb_cy + 4)))
    _accuracy_chip(surf, cx, rect.bottom - 22, 91)
    _label(surf, rect, "V1  claw + banner / IDLE")


def v2_predicting_cushion(surf, rect):
    """V2 — Cushion seat + etched-in-fog. PREDICTING state. The orb churns
    brighter, inner glow building, a faint half-formed line etched in the fog
    ('...pillar 7...'), cushion ring instead of a claw."""
    _arcade_card(surf, rect, "CRYSTAL BALL")
    cx = rect.centerx
    orb_r = 54
    orb_cy = rect.y + 112
    _soft_glow(surf, cx, orb_cy, int(orb_r * 1.35), _FOG_GOLD, 56, layers=6)
    _cushion_stand(surf, cx, orb_cy + orb_r - 2, orb_r + 30, 14)
    orb, (ox, oy) = _orb(orb_r, _FOG_TEAL, _FOG_TEAL_DK, _FOG_GOLD, 150, T,
                         churn=0.9)
    surf.blit(orb, orb.get_rect(center=(cx, orb_cy)))
    # half-etched words surfacing
    ef = _font(11, True)
    for txt, dy, a in (("the future", -10, 90), ("stirs...", 12, 130)):
        timg = ef.render(txt, True, _GOLD_PALE)
        timg.set_alpha(a)
        surf.blit(timg, timg.get_rect(center=(cx, orb_cy + dy)))
    pred = _font(9, True).render("DIVINING…", True, _FOG_GOLD)
    surf.blit(pred, pred.get_rect(center=(cx, orb_cy + orb_r + 22)))
    _accuracy_chip(surf, cx, rect.bottom - 22, 91)
    _label(surf, rect, "V2  cushion + etched-fog / PREDICTING")


def v3_reveal_scroll(surf, rect):
    """V3 — Claw stand + unfurled scroll. REVEALED state. The orb has settled to
    a bright clear core; a small aged-gold scroll unfurls beneath bearing the
    prophecy text. The most 'fortune-teller' presentation."""
    _arcade_card(surf, rect, "CRYSTAL BALL")
    cx = rect.centerx
    orb_r = 46
    orb_cy = rect.y + 88
    _soft_glow(surf, cx, orb_cy, int(orb_r * 1.25), (255, 224, 150), 56, layers=6)
    orb, _ = _orb(orb_r, _FOG_CLEAR, (20, 60, 56), (255, 232, 170), 170, T,
                  churn=0.3, reveal=True)
    _claw_stand(surf, cx, orb_cy + orb_r - 4, orb_r + 22, 22)
    surf.blit(orb, orb.get_rect(center=(cx, orb_cy)))
    # scroll
    sw, sh = rect.w - 40, 56
    scr = pygame.Rect(cx - sw // 2, orb_cy + orb_r + 26, sw, sh)
    for rx in (scr.x - 6, scr.right - 4):  # rolled end caps
        rounded_rect(surf, pygame.Rect(rx, scr.y - 3, 10, sh + 6), 5,
                     lerp_color(_GOLD_DEEP, NEAR_BLACK, 0.2))
        pygame.draw.rect(surf, _GOLD_BRIGHT,
                         pygame.Rect(rx, scr.y - 3, 10, sh + 6), 1,
                         border_radius=5)
    surf.blit(_vgrad_panel(scr.w, scr.h, 4, (236, 220, 178), (206, 184, 132),
                           255), scr.topleft)
    pygame.draw.rect(surf, _GOLD_DEEP, scr, 1)
    _wrap_text_dark(surf, "An early, confident death awaits. Around pillar 7.",
                    scr.inflate(-14, -8), 11)
    _accuracy_chip(surf, cx, rect.bottom - 22, 91)
    _label(surf, rect, "V3  claw + scroll / REVEALED")


def v4_reveal_murky(surf, rect):
    """V4 — Mood-tint variant. REVEALED on a BAD STREAK: the fog goes murky
    brown, the glow sickly, and the prophecy banner takes a warning-amber rim.
    Same speech-banner presentation as V1 so the mood tint is the only change."""
    _arcade_card(surf, rect, "CRYSTAL BALL")
    cx = rect.centerx
    orb_r = 48
    orb_cy = rect.y + 90
    _soft_glow(surf, cx, orb_cy, int(orb_r * 1.2), (150, 100, 50), 40, layers=5)
    orb, _ = _orb(orb_r, _FOG_MURK, _FOG_MURK_DK, (190, 130, 60), 120, T,
                  churn=0.2, reveal=True)
    _claw_stand(surf, cx, orb_cy + orb_r - 4, orb_r + 22, 22)
    surf.blit(orb, orb.get_rect(center=(cx, orb_cy)))
    ban = pygame.Rect(cx - (rect.w - 36) // 2, orb_cy + orb_r + 24,
                      rect.w - 36, 52)
    _prophecy_banner(surf, ban, "A grim run looms. You will falter early — pillar 7.",
                     accent=(214, 150, 60))
    # mood tag
    tag = _font(8, True).render("MOOD: BAD STREAK", True, (200, 150, 90))
    surf.blit(tag, tag.get_rect(center=(cx, ban.bottom + 12)))
    _accuracy_chip(surf, cx, rect.bottom - 18, 91)
    _label(surf, rect, "V4  murky mood-tint / REVEALED")


def v5_etched_minimal(surf, rect):
    """V5 — Etched-in-fog minimal + gem-foot. REVEALED with the prophecy written
    DIRECTLY in the swirling fog (no external card), the orb seated on a single
    faceted gem foot. The cleanest, most 'magic' read — text lives in the glass."""
    _arcade_card(surf, rect, "CRYSTAL BALL")
    cx = rect.centerx
    orb_r = 62
    orb_cy = rect.y + 116
    _soft_glow(surf, cx, orb_cy, int(orb_r * 1.2), _FOG_TEAL, 42, layers=6)
    orb, (ox, oy) = _orb(orb_r, _FOG_TEAL, _FOG_TEAL_DK, _FOG_GOLD, 130, T,
                         churn=0.5, reveal=True)
    # gem foot (reuse the rarity gem primitive as a base jewel)
    _gem(surf, cx, orb_cy + orb_r + 12, 9, "legendary", T, inset=True)
    surf.blit(orb, orb.get_rect(center=(cx, orb_cy)))
    # prophecy etched in fog: faint outline + bright fill so it floats in glass
    _etched(surf, "An early, confident", (cx, orb_cy - 18), 11)
    _etched(surf, "death awaits.", (cx, orb_cy - 2), 11)
    _etched(surf, "Around pillar 7.", (cx, orb_cy + 16), 11)
    _accuracy_chip(surf, cx, rect.bottom - 20, 91)
    _label(surf, rect, "V5  etched-in-fog + gem foot / REVEALED")


# ── small text helpers ───────────────────────────────────────────────────────
def _etched(surf, txt, center, size):
    f = _font(size, True)
    out = f.render(txt, True, (8, 22, 24))
    r = f.render(txt, True, WHITE).get_rect(center=center)
    for ox, oy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        surf.blit(out, (r.x + ox, r.y + oy))
    _gradient_text(surf, txt, f, center, _GOLD_PALE, _FOG_GOLD, shadow=False)


def _wrap_text_dark(surf, text, rect, size):
    """Dark ink on the parchment scroll (not gold-on-dark)."""
    f = _font(size, True)
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if f.size(trial)[0] <= rect.w:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    lh = f.get_height() - 1
    y0 = rect.centery - lh * len(lines) // 2 + lh // 2
    for i, ln in enumerate(lines):
        img = f.render(ln, True, (74, 52, 24))
        surf.blit(img, img.get_rect(center=(rect.centerx, y0 + i * lh)))


def _label(surf, rect, txt):
    f = _font(12, True)
    img = f.render(txt, True, UI_CREAM)
    bg = pygame.Rect(0, 0, img.get_width() + 16, 20)
    bg.midtop = (rect.centerx, rect.bottom + 12)
    s = pygame.Surface(bg.size, pygame.SRCALPHA)
    rounded_rect(s, s.get_rect(), 9, (8, 8, 16), alpha=210)
    pygame.draw.rect(s, (*_GOLD_DEEP, 160), s.get_rect(), 1, border_radius=9)
    surf.blit(s, bg.topleft)
    surf.blit(img, img.get_rect(center=bg.center))


# ── compose the sheet ────────────────────────────────────────────────────────
def main():
    margin = 22
    gap = 20
    cols = 3
    rows = 2
    card_w, card_h = W, H            # each tile is a full 360x640 pocket frame
    sheet_w = margin * 2 + card_w * cols + gap * (cols - 1)
    header_h = 70
    sheet_h = margin * 2 + header_h + card_h * rows + gap * (rows - 1)
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((18, 16, 26))

    # sheet header
    _gradient_text(sheet, "CRYSTAL BALL  —  PROFILE ARCADE CURIO  —  ROUND 1",
                   _font(26, True), (sheet_w // 2, margin + 20),
                   _GOLD_PALE, _GOLD_BRIGHT, shadow=True)
    sub = _font(13, True).render(
        "obsidian & gold  ·  procedural glass orb + swirling teal/gold fog  ·  states: idle / predicting / revealed / mood-tint",
        True, UI_CREAM)
    sheet.blit(sub, sub.get_rect(center=(sheet_w // 2, margin + 46)))

    builders = [v1_idle_claw, v2_predicting_cushion, v3_reveal_scroll,
                v4_reveal_murky, v5_etched_minimal]
    for i, fn in enumerate(builders):
        col = i % cols
        row = i // cols
        x = margin + col * (card_w + gap)
        y = margin + header_h + row * (card_h + gap)
        frame = pygame.Surface((card_w, card_h))
        # frame background = the real profile night-sky gradient
        n = len(_BG_STOPS)
        for yy in range(card_h):
            f = yy / (card_h - 1)
            seg = min(n - 2, int(f * (n - 1)))
            local = (f * (n - 1)) - seg
            pygame.draw.line(frame, lerp_color(_BG_STOPS[seg], _BG_STOPS[seg + 1],
                                               local), (0, yy), (card_w - 1, yy))
        card = pygame.Rect(28, 110, card_w - 56, 348)
        fn(frame, card)
        sheet.blit(frame, (x, y))
        pygame.draw.rect(sheet, (60, 54, 70), (x, y, card_w, card_h), 1)

    out_dir = "/home/user/skybit/docs/profile/crystal_ball"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_1.png")
    pygame.image.save(sheet, out_path)
    print("WROTE", out_path, sheet.get_size())


if __name__ == "__main__":
    main()
