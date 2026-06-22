"""Round-2 refinement sheet for the Crystal Ball curio (Profile ARCADE).

Round 1 explored five takes; the art-director locked ONE carry-forward family:
V3's parchment scroll (dark ink on aged parchment is the only fully legible
prophecy surface at pocket scale) + V1's gold claw stand as the CONSTANT cradle.
This sheet proves that single family across the FOUR live states distinguished
by ORB ENERGY + scroll presence alone — no text gimmicks, no resizing pop.

Locked decisions baked in here:
  * ONE orb radius (_ORB_R) shared by every state — the widget animates between
    states, so the orb must never resize.
  * One cradle (the claw stand) for all four states.
  * The parchment scroll is the only prophecy surface (revealed + mood); both
    carry a pointer-notch up to the orb so the words read as spoken by the ball.
  * States differ by inner energy: idle (dim/slow) · predicting (churn + spark
    ring, no scroll) · revealed (bright clear core + scroll) · mood (murky brown
    + amber rim-arc + cooler-tinted scroll).

Writes the combined sheet only; git is the orchestrator's job.
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
    _vgrad_panel, _drop_shadow, _gradient_text, _soft_glow,
    _gold_rule, _OBS_TOP, _OBS_BOT, _BG_STOPS,
)

# Smoky teal/gold fog hues — deliberately NOT a saturated rarity purple, so the
# orb never competes with the rarity gem language that owns hue meaning.
_FOG_TEAL = (54, 150, 150)
_FOG_TEAL_DK = (16, 54, 60)
_FOG_GOLD = (224, 176, 78)
_FOG_MURK = (96, 70, 40)        # bad-streak murky brown
_FOG_MURK_DK = (40, 28, 16)
_FOG_CLEAR = (150, 214, 196)    # revealed clear/bright
_GLASS_RIM = (208, 226, 224)
_AMBER_RIM = (224, 158, 70)     # mood warning rim-arc on the glass

# ONE radius for the orb in every state — the live widget cross-fades between
# states, so any radius change would read as a jarring "pop". This is the single
# most important constraint of the round.
_ORB_R = 60
_ORB_CY_OFF = 104               # orb centre below the card top, fixed per state

T = 0.62  # frozen "churning" phase used across the sheet for the live look


# ── orb builder ──────────────────────────────────────────────────────────────
def _orb(r, fog_a, fog_b, glow_col, glow_a, t, churn=0.0, reveal=False,
         core_bright=0.0, blob_floor=5, rim_arc=None):
    """A procedural glass sphere on its own SRCALPHA surface.

    Energy is expressed through `churn` (blob count + inner brightness) and
    `core_bright` (0..1 — how settled-and-clear the core reads), NOT through
    radius: `r` is always `_ORB_R`. `rim_arc` paints a thin tinted warning arc
    on the glass (the mood state) so gloom reads as deliberate, never broken.
    """
    d = r * 2
    pad = max(8, r // 3)
    surf = pygame.Surface((d + pad * 2, d + pad * 2), pygame.SRCALPHA)
    cx = cy = r + pad

    # Glass body: a lit, smoky interior (NOT black) that falls off toward the
    # rim so curvature reads. Centre carries the fog tone so the sphere glows
    # from within; only the outer ring darkens to a deep glass edge.
    body_lit = lerp_color(fog_a, fog_b, 0.45)
    body_lit = lerp_color(body_lit, WHITE, 0.10 + 0.10 * core_bright)
    body_edge = lerp_color(fog_b, (8, 12, 16), 0.55)
    for i in range(r, 0, -1):
        f = i / r
        base = lerp_color(body_lit, body_edge, f ** 1.5)
        pygame.draw.circle(surf, (*base, 255), (cx, cy), i)

    # Inner fog: several translucent blobs orbiting on slow, incommensurate
    # periods so the swirl never visibly loops. Clipped to the sphere by a mask.
    fog = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    n_blobs = blob_floor + int(churn * 4)
    for k in range(n_blobs):
        ph = t * (0.5 + 0.18 * k) + k * 2.39996
        orbit = r * (0.18 + 0.30 * ((k * 0.37 + 0.2) % 1.0))
        bx = cx + math.cos(ph) * orbit
        by = cy + math.sin(ph * 0.83 + k) * orbit * 0.8
        br = int(r * (0.34 + 0.20 * ((k * 0.53) % 1.0)))
        col = lerp_color(fog_a, lerp_color(fog_a, WHITE, 0.25),
                         (k / max(1, n_blobs - 1)))
        a = int((40 + 44 * churn) * (0.55 + 0.45 * math.sin(ph * 1.3)))
        for layer in range(3, 0, -1):
            rr = int(br * layer / 3)
            aa = int(a * (1 - (layer - 1) / 3) ** 1.4)
            if rr <= 0 or aa <= 0:
                continue
            g = pygame.Surface((rr * 2 + 2, rr * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(g, (*col, aa), (rr + 1, rr + 1), rr)
            fog.blit(g, (int(bx) - rr - 1, int(by) - rr - 1),
                     special_flags=pygame.BLEND_ADD)

    # Inner glow core — the "energy" of the orb. Dim + small at idle, swelling
    # with churn for predicting, and a settled bright bloom when revealed so the
    # prophecy feels like it surfaced from inside.
    core_r = int(r * (0.22 + 0.16 * churn + 0.16 * core_bright))
    core_a = int(glow_a * (0.45 + 0.55 * churn + 0.4 * core_bright))
    if reveal:
        core_r = int(r * (0.40 + 0.10 * core_bright))
        core_a = min(255, int(glow_a * (1.2 + 0.4 * core_bright)))
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

    # Mood warning rim-arc — a clear amber glint along the BOTTOM of the glass
    # that signals deliberate gloom. Confined to the lower sweep (never a full
    # ring), with a soft additive bloom just inside it so the rim looks lit from
    # the murk rather than drawn on.
    if rim_arc is not None:
        bloom = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        for w_, a in ((4, 60), (3, 110), (2, 200)):
            pygame.draw.arc(bloom, (*rim_arc, a), arc_box, math.radians(214),
                            math.radians(326), w_)
        surf.blit(bloom, (0, 0), special_flags=pygame.BLEND_ADD)

    # Specular highlight cap + a tiny secondary pip (wet-glass read).
    hl = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    hx, hy = cx - int(r * 0.34), cy - int(r * 0.40)
    pygame.draw.circle(hl, (255, 255, 255, 200), (hx, hy), max(2, r // 6))
    pygame.draw.circle(hl, (255, 255, 255, 120), (hx, hy), max(3, r // 4), 1)
    pygame.draw.circle(hl, (255, 255, 255, 230),
                       (cx + int(r * 0.30), cy + int(r * 0.34)), max(1, r // 12))
    for k in range(3, 0, -1):
        rr = max(2, r // 6) + k * 2
        g = pygame.Surface((rr * 2, rr * 2), pygame.SRCALPHA)
        pygame.draw.circle(g, (255, 255, 255, 40), (rr, rr), rr)
        hl.blit(g, (hx - rr, hy - rr), special_flags=pygame.BLEND_ADD)
    surf.blit(hl, (0, 0))
    return surf, (cx, cy)


def _spark_ring(surf, cx, cy, r, t, col):
    """A faint ring of DISCRETE orbiting sparks around the orb — the 'divining'
    tell. Few, well-separated motes on a tilted ellipse standing clear of the
    glass, so it reads as gathered energy in the air, NOT a solid gold hoop. A
    short comet-tail behind each mote sells motion without filling the gaps."""
    n = 6                                       # few + spaced so gaps stay open
    for k in range(n):
        a = t * 1.6 + k * (math.tau / n)
        ex = cx + math.cos(a) * r
        ey = cy + math.sin(a) * r * 0.40 - r * 0.05
        depth = 0.5 + 0.5 * math.sin(a)         # fade motes on the far side
        rad = int(2 + 2 * depth)
        alpha = int(40 + 120 * depth)
        # comet tail (a couple of dimmer trailing dots, not a continuous arc)
        for ti in (1, 2):
            ta = a - ti * 0.16
            tx = cx + math.cos(ta) * r
            ty = cy + math.sin(ta) * r * 0.40 - r * 0.05
            trad = max(1, rad - ti)
            g = pygame.Surface((trad * 2 + 2, trad * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(g, (*col, alpha // (ti + 2)),
                               (trad + 1, trad + 1), trad)
            surf.blit(g, (int(tx) - trad - 1, int(ty) - trad - 1),
                      special_flags=pygame.BLEND_ADD)
        g = pygame.Surface((rad * 2 + 2, rad * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(g, (*col, alpha), (rad + 1, rad + 1), rad)
        surf.blit(g, (int(ex) - rad - 1, int(ey) - rad - 1),
                  special_flags=pygame.BLEND_ADD)


# ── the constant cradle ───────────────────────────────────────────────────────
def _claw_stand(surf, cx, orb_cy, orb_r):
    """A three-prong gold claw foot cradling the orb: two outer talons curling
    UP along the orb's sides (visible past the sphere, so the cradle reads) + a
    central post on a stepped plinth. Pure polygons, gold palette. This is the
    CONSTANT cradle across every state — only the orb + scroll change.

    Geometry is derived from the orb so the talons always hug the same sphere:
    they spring from a plinth below the orb and curl up to grip it at ~45° below
    its equator, where they clear the silhouette.
    """
    deep = _GOLD_DEEP
    base_y = orb_cy + orb_r + 14            # plinth sits just below the sphere
    h = 30
    span = int(orb_r * 1.9)
    # Talons grip the orb where they clear its outline (lower flank), so the
    # curling tips read against the card, not buried under the glass.
    for sgn in (-1, 1):
        x0 = cx + sgn * int(span * 0.14)
        tip_x = cx + sgn * int(orb_r * 0.86)
        tip_y = orb_cy + int(orb_r * 0.62)   # ~45° below equator — clears glass
        pts = [
            (x0, base_y),
            (cx + sgn * int(span * 0.30), base_y - int(h * 0.5)),
            (cx + sgn * int(span * 0.46), base_y - int(h * 0.9)),
            (tip_x, tip_y),                  # talon tip curling up to cradle
            (tip_x - sgn * 4, tip_y + 5),
            (cx + sgn * int(span * 0.34), base_y - int(h * 0.35)),
            (x0 + sgn * 3, base_y + 3),
        ]
        pygame.draw.polygon(surf, _GOLD_BRIGHT, pts)
        pygame.draw.polygon(surf, deep, pts, 1)
        # lit edge up the outer face sells the gold curve
        pygame.draw.line(surf, _GOLD_PALE, (x0, base_y), (tip_x, tip_y), 1)
    # central post peeking between the talons
    pygame.draw.polygon(surf, lerp_color(_GOLD_BRIGHT, deep, 0.35),
                        [(cx - 4, base_y - h + 2), (cx + 4, base_y - h + 2),
                         (cx + 6, base_y + 4), (cx - 6, base_y + 4)])
    # stepped plinth
    rounded_rect(surf, pygame.Rect(cx - span // 2, base_y + 2, span, 8), 4,
                 _GOLD_DEEP)
    rounded_rect(surf, pygame.Rect(cx - span // 2 + 3, base_y + 3, span - 6, 3),
                 1, _GOLD_BRIGHT)


# ── the prophecy surface ──────────────────────────────────────────────────────
def _parchment_scroll(surf, cx, top_y, w, text, orb_cy, tint=0.0):
    """The locked prophecy surface: an aged-parchment scroll with rolled gold
    end-caps and DARK INK body text (the only fully legible read at pocket
    scale). A pointer-notch rises from the scroll toward the orb so the words
    read as spoken by the ball. `tint` (0..1) cools/greys the parchment for the
    mood state. Returns the scroll rect so callers can place captions below it.
    """
    # Height grows to fit wrapped lines so descenders never clip.
    f = _font(11, True)
    lines = _wrap(text, w - 28, f)
    lh = f.get_height() - 1
    sh = max(48, lh * len(lines) + 22)
    scr = pygame.Rect(cx - w // 2, top_y, w, sh)

    # Pointer notch from the top edge of the scroll up toward the orb — a small
    # parchment-tinted triangle so the scroll reads as a speech from the ball.
    paper_top = lerp_color((236, 220, 178), (196, 200, 198), tint)
    notch_h = max(7, (top_y - orb_cy) // 6 + 6)
    pygame.draw.polygon(surf, paper_top,
                        [(cx - 9, scr.y + 2), (cx + 9, scr.y + 2),
                         (cx, scr.y - notch_h)])
    pygame.draw.polygon(surf, _GOLD_DEEP,
                        [(cx - 9, scr.y + 2), (cx + 9, scr.y + 2),
                         (cx, scr.y - notch_h)], 1)

    # Rolled gold end-caps frame the parchment as a scroll.
    for rx in (scr.x - 6, scr.right - 4):
        rounded_rect(surf, pygame.Rect(rx, scr.y - 3, 10, sh + 6), 5,
                     lerp_color(_GOLD_DEEP, NEAR_BLACK, 0.2))
        pygame.draw.rect(surf, _GOLD_BRIGHT,
                         pygame.Rect(rx, scr.y - 3, 10, sh + 6), 1,
                         border_radius=5)
        # a curl shadow on the inner lip so the roll reads as cylindrical
        lip = scr.x + 4 if rx < cx else scr.right - 6
        pygame.draw.line(surf, lerp_color(_GOLD_DEEP, NEAR_BLACK, 0.4),
                         (lip, scr.y), (lip, scr.bottom), 1)

    # Parchment body — warm aged paper, cooled toward grey for the mood state.
    paper_bot = lerp_color((206, 184, 132), (168, 172, 172), tint)
    surf.blit(_vgrad_panel(scr.w, scr.h, 4, paper_top, paper_bot, 255),
              scr.topleft)
    pygame.draw.rect(surf, _GOLD_DEEP, scr, 1)

    # Dark ink, cooled for the mood scroll so the gloom carries to the text too.
    ink = lerp_color((74, 52, 24), (60, 64, 70), tint)
    y0 = scr.centery - lh * len(lines) // 2 + lh // 2
    for i, ln in enumerate(lines):
        img = f.render(ln, True, ink)
        surf.blit(img, img.get_rect(center=(scr.centerx, y0 + i * lh)))
    return scr


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
    """A small PROPHECY ACCURACY readout chip in the unified pill silhouette.
    Contrast tuned for the true 360px tile: pale-gold label on a deep-amber pill
    with a 1px bright rim, legible without zoom."""
    f = _font(9, True)
    lbl = f"PROPHECY ACCURACY  {pct}%"
    timg = f.render(lbl, True, (255, 244, 214))
    w = timg.get_width() + 24
    h = 18
    r = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    surf.blit(_vgrad_panel(w, h, h // 2, (58, 44, 22), (28, 20, 10), 252),
              r.topleft)
    pygame.draw.rect(surf, (*_GOLD_BRIGHT, 200), r, width=1, border_radius=h // 2)
    pygame.draw.circle(surf, _FOG_TEAL, (r.x + 9, cy), 3)
    pygame.draw.circle(surf, _GOLD_PALE, (r.x + 9, cy), 3, 1)
    surf.blit(timg, timg.get_rect(midleft=(r.x + 16, cy)))


def _caption_pill(surf, cx, cy, text, fg, bg_top, bg_bot, rim):
    """A small caption pill (TAP TO DIVINE / DIVINING…). Pill silhouette shared
    with the accuracy chip so the affordance reads as one UI family, with a 1px
    rim for legibility at the true 360px tile width."""
    f = _font(10, True)
    timg = f.render(text, True, fg)
    w = timg.get_width() + 22
    h = 20
    r = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    surf.blit(_vgrad_panel(w, h, h // 2, bg_top, bg_bot, 252), r.topleft)
    pygame.draw.rect(surf, rim, r, width=1, border_radius=h // 2)
    surf.blit(timg, timg.get_rect(center=r.center))


def _wrap(text, max_w, f):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if f.size(trial)[0] <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


# ── the four states (ONE family) ──────────────────────────────────────────────
def state_idle(surf, rect):
    """IDLE — dormant orb. Low blob count, dim teal core, slow drift. No scroll.
    A 'TAP TO DIVINE' caption pill sits BELOW the orb so the affordance is
    legible (not etched in fog)."""
    _arcade_card(surf, rect)
    cx = rect.centerx
    orb_cy = rect.y + _ORB_CY_OFF
    # Dim, orb-hugging bloom — idle should look dormant, never haloed.
    _soft_glow(surf, cx, orb_cy, int(_ORB_R * 0.8), _FOG_TEAL, 20, layers=5)
    orb, _ = _orb(_ORB_R, _FOG_TEAL, _FOG_TEAL_DK, _FOG_GOLD, 80, T,
                  churn=0.0, blob_floor=4)
    surf.blit(orb, orb.get_rect(center=(cx, orb_cy)))
    _claw_stand(surf, cx, orb_cy, _ORB_R)   # talons grip in front of the glass
    _caption_pill(surf, cx, orb_cy + _ORB_R + 44, "TAP TO DIVINE",
                  (255, 244, 214), (40, 34, 26), (20, 16, 12),
                  (*_GOLD_BRIGHT, 170))
    _accuracy_chip(surf, cx, rect.bottom - 20, 91)
    _label(surf, rect, "IDLE")


def state_predicting(surf, rect):
    """PREDICTING — the orb churns: high blob count, swelling gold core, a faint
    orbiting spark ring gathering energy. NO scroll yet. 'DIVINING…' caption."""
    _arcade_card(surf, rect)
    cx = rect.centerx
    orb_cy = rect.y + _ORB_CY_OFF
    # Tight inner bloom only — kept smaller than the orb so it warms the core
    # from within instead of forming a gold ring outside the glass.
    _soft_glow(surf, cx, orb_cy, int(_ORB_R * 0.85), _FOG_GOLD, 26, layers=6)
    _spark_ring(surf, cx, orb_cy, _ORB_R + 16, T, _FOG_GOLD)
    orb, _ = _orb(_ORB_R, _FOG_TEAL, _FOG_TEAL_DK, _FOG_GOLD, 150, T,
                  churn=0.95, blob_floor=6)
    surf.blit(orb, orb.get_rect(center=(cx, orb_cy)))
    _claw_stand(surf, cx, orb_cy, _ORB_R)
    _caption_pill(surf, cx, orb_cy + _ORB_R + 44, "DIVINING…",
                  (255, 236, 188), (52, 40, 18), (30, 22, 10),
                  (*_GOLD_BRIGHT, 210))
    _accuracy_chip(surf, cx, rect.bottom - 20, 91)
    _label(surf, rect, "PREDICTING")


def state_revealed(surf, rect):
    """REVEALED — the orb settles to a bright, clear core; the parchment scroll
    unfurls beneath bearing the full prophecy, a pointer-notch linking it to the
    ball."""
    _arcade_card(surf, rect)
    cx = rect.centerx
    orb_cy = rect.y + _ORB_CY_OFF
    _soft_glow(surf, cx, orb_cy, int(_ORB_R * 0.95), (255, 224, 150), 46,
               layers=6)
    orb, _ = _orb(_ORB_R, _FOG_CLEAR, (20, 60, 56), (255, 232, 170), 170, T,
                  churn=0.25, reveal=True, core_bright=1.0, blob_floor=4)
    surf.blit(orb, orb.get_rect(center=(cx, orb_cy)))
    _claw_stand(surf, cx, orb_cy, _ORB_R)
    _parchment_scroll(surf, cx, orb_cy + _ORB_R + 40, rect.w - 44,
                      "An early, confident death awaits. Around pillar 7.",
                      orb_cy)
    _accuracy_chip(surf, cx, rect.bottom - 18, 91)
    _label(surf, rect, "REVEALED")


def state_mood(surf, rect):
    """MOOD (bad streak) — same family, murky brown fog + a thin amber rim-arc on
    the glass so the gloom reads as deliberate, never broken. The same parchment
    scroll, tinted cooler/greyer, carries the grim prophecy."""
    _arcade_card(surf, rect)
    cx = rect.centerx
    orb_cy = rect.y + _ORB_CY_OFF
    # Tight, dim bloom — gloom should NOT radiate a halo; the orb sits low and
    # contained so the amber rim-glint is the only outward energy tell.
    _soft_glow(surf, cx, orb_cy, int(_ORB_R * 0.7), (120, 80, 40), 26,
               layers=5)
    orb, _ = _orb(_ORB_R, _FOG_MURK, _FOG_MURK_DK, (190, 130, 60), 120, T,
                  churn=0.2, reveal=True, core_bright=0.3, blob_floor=4,
                  rim_arc=_AMBER_RIM)
    surf.blit(orb, orb.get_rect(center=(cx, orb_cy)))
    _claw_stand(surf, cx, orb_cy, _ORB_R)
    scr = _parchment_scroll(surf, cx, orb_cy + _ORB_R + 40, rect.w - 44,
                            "A grim run looms. You falter early — pillar 7.",
                            orb_cy, tint=0.6)
    # Mood tag — amber on a dark pill with a rim, legible at true width.
    _caption_pill(surf, cx, scr.bottom + 16, "MOOD: BAD STREAK",
                  (244, 196, 132), (46, 32, 18), (26, 18, 10),
                  (*_AMBER_RIM, 200))
    _label(surf, rect, "MOOD")


# ── label ─────────────────────────────────────────────────────────────────────
def _label(surf, rect, txt):
    f = _font(13, True)
    img = f.render(txt, True, UI_CREAM)
    bg = pygame.Rect(0, 0, img.get_width() + 18, 22)
    bg.midtop = (rect.centerx, rect.bottom + 12)
    s = pygame.Surface(bg.size, pygame.SRCALPHA)
    rounded_rect(s, s.get_rect(), 10, (8, 8, 16), alpha=210)
    pygame.draw.rect(s, (*_GOLD_DEEP, 160), s.get_rect(), 1, border_radius=10)
    surf.blit(s, bg.topleft)
    surf.blit(img, img.get_rect(center=bg.center))


# ── compose the sheet ─────────────────────────────────────────────────────────
def main():
    margin = 22
    gap = 20
    cols = 4
    rows = 1
    card_w, card_h = W, H            # each tile is a full 360x640 pocket frame
    sheet_w = margin * 2 + card_w * cols + gap * (cols - 1)
    header_h = 76
    sheet_h = margin * 2 + header_h + card_h * rows
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((18, 16, 26))

    _gradient_text(sheet, "CRYSTAL BALL  —  ROUND 2  —  ONE FAMILY, FOUR ENERGY STATES",
                   _font(26, True), (sheet_w // 2, margin + 20),
                   _GOLD_PALE, _GOLD_BRIGHT, shadow=True)
    sub = _font(13, True).render(
        "locked: claw cradle (constant) + parchment scroll (prophecy surface)  ·  "
        "states differ by ORB ENERGY + scroll presence, NOT text  ·  orb radius fixed at "
        f"{_ORB_R}px in every state",
        True, UI_CREAM)
    sheet.blit(sub, sub.get_rect(center=(sheet_w // 2, margin + 48)))

    builders = [state_idle, state_predicting, state_revealed, state_mood]
    for i, fn in enumerate(builders):
        x = margin + i * (card_w + gap)
        y = margin + header_h
        frame = pygame.Surface((card_w, card_h))
        n = len(_BG_STOPS)
        for yy in range(card_h):
            f = yy / (card_h - 1)
            seg = min(n - 2, int(f * (n - 1)))
            local = (f * (n - 1)) - seg
            pygame.draw.line(frame, lerp_color(_BG_STOPS[seg], _BG_STOPS[seg + 1],
                                               local), (0, yy), (card_w - 1, yy))
        card = pygame.Rect(28, 118, card_w - 56, 360)
        fn(frame, card)
        sheet.blit(frame, (x, y))
        pygame.draw.rect(sheet, (60, 54, 70), (x, y, card_w, card_h), 1)

    out_dir = "/home/user/skybit/docs/profile/crystal_ball"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_2.png")
    pygame.image.save(sheet, out_path)
    print("WROTE", out_path, sheet.get_size())


if __name__ == "__main__":
    main()
