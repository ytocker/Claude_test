"""Round 1 — turn the ALREADY-STANDING Pip into the menu's Profile entry.

The earlier exploration drew a SEPARATE cropped bust portrait in a top
corner. The owner wants the opposite: the menu already stages Pip
standing at the pickup post-house (drawn live via game.entities.Bird),
so the Profile button should BE that existing diorama — no second parrot.

Five genuinely distinct ways to make the standing Pip read as
"tap me → your Profile", each folding the old Awards cue in as a small
violet "records inside" badge (a tiny trophy, never a gold coin) and
each carrying a PROFILE label:

  1 · FRAMED-IN-PLACE   — a gilded hollow frame + vignette wraps the
                          live diorama; the scene itself becomes the card.
  2 · NAMEPLATE STANDEE — Pip stands on an engraved PROFILE plinth; the
                          whole museum standee is the button.
  3 · SPOTLIGHT RING    — a character-select ground ring + halo under
                          Pip and a floating PROFILE tag.
  4 · TAP BUBBLE        — a rounded "THIS IS YOU / PROFILE" bubble
                          tethered to Pip with a tail pointing at him.
  5 · DASHED HOTSPOT    — a beveled, marching-ants tap-zone around the
                          diorama with a corner-tucked records pip.

Each is composited into a real 360x640 menu mock (SKYBIT hero, the live
standing Pip at the post-house, scarlet START, and a
STORE / TOP 10 / SETTINGS chip row — Awards has folded into Profile).
All five tile on one labeled sheet.
"""
import os
import math
import pygame

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

pygame.init()
pygame.display.set_mode((8, 8))

from game.config import W, H
from game import parrot  # noqa: F401  (ensures the macaw sprite cache is warm)
from game.entities import Bird
from game import intro as _intro
from game.draw import WHITE, lerp_color
from game.hud import (
    _font, _outlined_text, _pill_btn, _volume_panel, _tracked_label,
    _draw_overlay_stars, _draw_mountain_silhouette,
    _draw_trophy, _draw_gear, _draw_award_star, _coin_icon,
    _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP, _RED_OUTLINE, _ORANGE_BORDER,
    _AWSTAR_HI,
)

# Freeze near the crest of the START pill's tappability pulse (draw_menu
# rides it at sin(title_t * 3.6)); every Profile treatment shows the same
# "tap me" halo at its brightest so tappability is judged fairly.
T = 0.55
GLOW = 0.5 + 0.5 * math.sin(T * 3.6)          # 0..1 tap-glow pulse
STARS = [(int(37 * i * 1.7 % W), int(23 + 71 * i * 1.3 % 210),
          1 + (i % 2), i * 0.9) for i in range(26)]

# Mid-value gold between DEEP and BRIGHT — the inner step that turns a
# flat gold edge into a struck, gilded bevel (matches the HUD gold family).
_GOLD_MID = (212, 160, 44)
# Records badge ground: a deep violet so the folded-in Awards cue can
# never read as gold currency and never clash with the scarlet START.
_REC_GROUND = (96, 46, 150)
_REC_GROUND_D = (58, 24, 96)


# ── The live diorama (reused Pip, no second parrot) ──────────────────────────
def diorama_rects():
    """House + standing-Pip footprints at their REAL menu positions, so
    every treatment frames exactly what the running menu draws."""
    house = _intro.get_sprite("skyhouse_post")
    hw, hh = house.get_size()
    hx = int(W * 0.30) - hw // 2
    hy = int(H * 0.42) - hh // 2
    house_r = pygame.Rect(hx, hy, hw, hh)
    # Bird sits at (BIRD_X, H*0.42) ~ (90, 269); its sprite is ~64 px and
    # the parcel hangs a touch below, so extend the footprint downward.
    bird_r = pygame.Rect(90 - 34, int(H * 0.42) - 34, 68, 84)
    return house_r, bird_r, (house, hx, hy)


def draw_diorama(surf):
    """Blit the post-house then the LIVE Bird — the exact menu composition."""
    _house, hx, hy = diorama_rects()[2]
    surf.blit(_house, (hx, hy))
    Bird().draw(surf)


# ── Shared cues ──────────────────────────────────────────────────────────────
def tap_glow(surf, rect, shape="rrect", radius=16, strength=1.0):
    """Gold halo whose alpha rides the START-pill sin(t*3.6) pulse so the
    treatment reads as tappable chrome, not passive scenery."""
    pad = 14
    glow = pygame.Surface((rect.width + pad * 2, rect.height + pad * 2),
                          pygame.SRCALPHA)
    for k in range(pad, 0, -1):
        a = int(strength * (48 + 40 * GLOW) * k / pad / 3.6)
        gr = pygame.Rect(pad - k, pad - k,
                         rect.width + k * 2, rect.height + k * 2)
        if shape == "ellipse":
            pygame.draw.ellipse(glow, (*_GOLD_BRIGHT, a), gr)
        else:
            pygame.draw.rect(glow, (*_GOLD_BRIGHT, a), gr,
                             border_radius=radius + k)
    surf.blit(glow, (rect.x - pad, rect.y - pad))


def records_badge(surf, cx, cy, kind="trophy"):
    """The folded-in Awards cue: a violet chip with a tiny trophy/star +
    count. Deliberately NOT a gold roundel — a distinct shape AND colour
    so it reads as 'records inside', never as a coin / currency counter."""
    w, hh = 30, 17
    r = pygame.Rect(int(cx - w / 2), int(cy - hh / 2), w, hh)
    sh = pygame.Surface((w + 4, hh + 4), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 130), sh.get_rect(), border_radius=8)
    surf.blit(sh, (r.x - 1, r.y + 1))
    pygame.draw.rect(surf, _REC_GROUND_D, r, border_radius=8)
    pygame.draw.rect(surf, _REC_GROUND, r.inflate(-2, -2), border_radius=7)
    pygame.draw.rect(surf, _GOLD_BRIGHT, r, width=1, border_radius=8)
    if kind == "star":
        _draw_award_star(surf, r.left + 9, r.centery, 6)
    else:
        _draw_trophy(surf, r.left + 9, r.centery, 5)
    f = _font(11, True)
    img = f.render("3", True, _GOLD_PALE)
    surf.blit(img, img.get_rect(center=(r.right - 8, r.centery)))


def tri(surf, cx, cy, size, color):
    """Right-pointing chevron — the vendored font has no such glyph, so
    the 'tap through' cue is a small filled triangle."""
    pygame.draw.polygon(surf, color, [(cx - size // 2, cy - size),
                                      (cx + size // 2, cy),
                                      (cx - size // 2, cy + size)])


def profile_tag(surf, cx, cy, w=92, fill=(168, 34, 30), text=(255, 244, 224)):
    """A scarlet PROFILE ▸ chip — the shared tappable label used by the
    spotlight + bubble treatments."""
    r = pygame.Rect(int(cx - w / 2), int(cy - 10), w, 20)
    sh = pygame.Surface((w + 4, 24), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 120), sh.get_rect(), border_radius=8)
    surf.blit(sh, (r.x - 2, r.y + 2))
    pygame.draw.rect(surf, fill, r, border_radius=8)
    pygame.draw.rect(surf, _GOLD_BRIGHT, r, width=1, border_radius=8)
    _tracked_label(surf, "PROFILE", (r.centerx - 5, r.centery), 11,
                   color=text, track=2, alpha=255)
    tri(surf, r.right - 8, r.centery, 4, _GOLD_PALE)
    return r


# ── Shared menu mock ─────────────────────────────────────────────────────────
def menu_base(under_fn=None):
    """The live menu: night sky, mountains, SKYBIT hero, the standing Pip
    at the post-house, and START. `under_fn` paints treatment art that
    must sit BEHIND Pip (ground rings, plinths) before the diorama."""
    surf = pygame.Surface((W, H)).convert_alpha()
    for yy in range(H):
        t = yy / (H - 1)
        surf.fill(lerp_color((90, 150, 205), (196, 168, 150), t), (0, yy, W, 1))
    dim = pygame.Surface((W, H), pygame.SRCALPHA)
    dim.fill((6, 1, 21, 150))
    surf.blit(dim, (0, 0))
    _draw_overlay_stars(surf, STARS, T)
    _draw_mountain_silhouette(surf, alpha=180)

    if under_fn is not None:
        under_fn(surf)

    draw_diorama(surf)

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
    freed slot becomes STORE (Pip's re-skin shop)."""
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


def dio_region(pad=14):
    house_r, bird_r, _ = diorama_rects()
    return house_r.union(bird_r).inflate(pad * 2, pad * 2)


# ── Concept 1 — FRAMED-IN-PLACE ──────────────────────────────────────────────
# A gilded HOLLOW frame wraps the live diorama and a soft vignette dims
# everything outside it, so the standing-Pip scene itself becomes the
# character card. A PROFILE nameplate rides the bottom rail; the frame
# body pulses the tap-glow; a violet records badge tucks at the top-right.
def concept_framed(surf):
    fr = dio_region(pad=12)
    fr.height += 14                       # room for the nameplate rail

    # Vignette: dim a band AROUND the card, then punch the frame interior
    # back to clear so the eye is pulled to the diorama-as-card. Clipped to
    # the card's vertical band so the SKYBIT wordmark + START stay fully lit.
    band_top = fr.top - 12
    band_h = fr.height + 24
    vig = pygame.Surface((W, band_h), pygame.SRCALPHA)
    vig.fill((4, 2, 16, 92))
    pygame.draw.rect(vig, (0, 0, 0, 0),
                     fr.inflate(-6, -6).move(0, -band_top),
                     border_radius=16)
    surf.blit(vig, (0, band_top))

    tap_glow(surf, fr, radius=18, strength=1.05)
    sh = pygame.Surface((fr.w + 12, fr.h + 12), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 120), sh.get_rect(), border_radius=20)
    surf.blit(sh, (fr.x - 4, fr.y + 5))

    # Hollow beveled gilding — nested rect BORDERS (interior stays clear so
    # the live Pip shows through): deep base → mid step → bright bevel, with
    # a pale top rim-light and a dark press-bevel foot.
    pygame.draw.rect(surf, _GOLD_DEEP, fr, width=11, border_radius=18)
    pygame.draw.rect(surf, _GOLD_MID, fr.inflate(-6, -6), width=6,
                     border_radius=15)
    pygame.draw.rect(surf, _GOLD_BRIGHT, fr.inflate(-11, -11), width=2,
                     border_radius=12)
    pygame.draw.line(surf, _GOLD_PALE, (fr.left + 12, fr.top + 3),
                     (fr.right - 12, fr.top + 3), 2)
    pygame.draw.line(surf, _GOLD_DEEP, (fr.left + 12, fr.bottom - 3),
                     (fr.right - 12, fr.bottom - 3), 2)

    for cx, cy in ((fr.left + 10, fr.top + 10), (fr.right - 10, fr.top + 10),
                   (fr.left + 10, fr.bottom - 10),
                   (fr.right - 10, fr.bottom - 10)):
        pygame.draw.circle(surf, _GOLD_PALE, (cx, cy), 3)
        pygame.draw.circle(surf, _GOLD_DEEP, (cx, cy), 3, 1)

    # Engraved PROFILE nameplate on the bottom rail (label + tap chevron).
    plate = pygame.Rect(fr.centerx - 52, fr.bottom - 20, 104, 17)
    pygame.draw.rect(surf, (18, 12, 40), plate, border_radius=6)
    pygame.draw.rect(surf, _GOLD_DEEP, plate, width=1, border_radius=6)
    _tracked_label(surf, "PROFILE", (plate.centerx - 6, plate.centery), 11,
                   color=_GOLD_PALE, track=2, alpha=245)
    tri(surf, plate.right - 8, plate.centery, 4, _GOLD_PALE)

    records_badge(surf, fr.right - 2, fr.top - 2)


# ── Concept 2 — NAMEPLATE STANDEE ────────────────────────────────────────────
# Pip keeps standing exactly where he is, but now on a museum plinth: a
# 3D brass box slid under his feet with an engraved PROFILE plaque on its
# front face. The whole standee (diorama + plinth) is the button — a soft
# tap-glow rings the base and a records plaque tucks at the plinth corner.
def _standee_under(surf):
    reg = dio_region(pad=8)
    # Feet land around the house base; seat the plinth just under them.
    top = reg.bottom - 6
    pw, ph = 118, 30
    px = reg.centerx - pw // 2
    plinth = pygame.Rect(px, top, pw, ph)
    tap_glow(surf, plinth.inflate(10, 6), radius=12, strength=0.9)

    # Top face (parallelogram) reads the plinth as a solid block Pip stands on.
    depth = 9
    top_face = [(plinth.left, plinth.top),
                (plinth.right, plinth.top),
                (plinth.right - depth, plinth.top - depth),
                (plinth.left + depth, plinth.top - depth)]
    pygame.draw.polygon(surf, _GOLD_MID, top_face)
    pygame.draw.polygon(surf, _GOLD_DEEP, top_face, 1)
    # Front face — the plaque body, gilded with a top sheen + foot shadow.
    pygame.draw.rect(surf, _GOLD_DEEP, plinth, border_radius=4)
    pygame.draw.rect(surf, _GOLD_MID, plinth.inflate(-4, -4), border_radius=3)
    pygame.draw.line(surf, _GOLD_PALE, (plinth.left + 5, plinth.top + 3),
                     (plinth.right - 5, plinth.top + 3), 1)
    pygame.draw.line(surf, (60, 40, 6), (plinth.left + 5, plinth.bottom - 3),
                     (plinth.right - 5, plinth.bottom - 3), 1)

    # Engraved PROFILE — dark inset so it reads as stamped brass.
    inset = plinth.inflate(-14, -12)
    pygame.draw.rect(surf, (52, 34, 8), inset, border_radius=3)
    _tracked_label(surf, "PROFILE", (inset.centerx - 5, inset.centery), 12,
                   color=_GOLD_PALE, track=3, alpha=255)
    tri(surf, inset.right - 7, inset.centery, 4, _GOLD_PALE)

    records_badge(surf, plinth.right - 2, plinth.top - 3)


def concept_standee(surf):
    pass  # all art is behind Pip; drawn by _standee_under


# ── Concept 3 — SPOTLIGHT / SELECT RING ──────────────────────────────────────
# The character-select idiom: a glowing ground selection-ring + soft halo
# under Pip's feet and left/right select arrows, plus a floating PROFILE ▸
# tag above him. Reads instantly as "this character is selectable".
def _spotlight_under(surf):
    reg = dio_region(pad=6)
    cx = reg.centerx
    cy = reg.bottom - 4                     # ground line at Pip's feet
    rw, rh = 84, 26

    # Soft upward halo cone so Pip looks lit from the stage floor.
    halo = pygame.Surface((rw * 2, reg.height + 20), pygame.SRCALPHA)
    for k in range(rw, 0, -3):
        a = int((30 + 26 * GLOW) * k / rw / 5)
        pygame.draw.ellipse(halo, (*_GOLD_BRIGHT, a),
                            (rw - k, halo.get_height() - k // 2 - rh,
                             k * 2, rh))
    surf.blit(halo, (cx - rw, cy - halo.get_height() + rh))

    # Selection ring — filled glow disc + a bright ellipse rim that pulses.
    disc = pygame.Surface((rw + 20, rh + 20), pygame.SRCALPHA)
    pygame.draw.ellipse(disc, (*_GOLD_MID, 70),
                        (10, 10, rw, rh))
    surf.blit(disc, (cx - rw // 2 - 10, cy - rh // 2 - 10))
    ring = pygame.Rect(cx - rw // 2, cy - rh // 2, rw, rh)
    pygame.draw.ellipse(surf, (*_GOLD_BRIGHT, int(180 + 60 * GLOW)), ring, 3)
    pygame.draw.ellipse(surf, (*_GOLD_PALE, 150), ring.inflate(-8, -8), 1)

    # Left / right character-select arrows hugging the ring.
    for sgn in (-1, 1):
        ax = cx + sgn * (rw // 2 + 12)
        pts = [(ax, cy - 6), (ax, cy + 6), (ax + sgn * 8, cy)]
        pygame.draw.polygon(surf, (*_GOLD_BRIGHT, 220), pts)
        pygame.draw.polygon(surf, _GOLD_DEEP, pts, 1)


def concept_spotlight(surf):
    reg = dio_region(pad=6)
    # Float the tag between the subtitle band and Pip's head so it clears
    # the wordmark above and the diorama below.
    tag_y = reg.top + 18
    profile_tag(surf, reg.centerx, tag_y, w=96)
    records_badge(surf, reg.centerx + 60, tag_y, kind="star")


# ── Concept 4 — TAP BUBBLE ───────────────────────────────────────────────────
# A rounded call-out bubble tethered to Pip with a tail pointing right at
# him: "THIS IS YOU" over a PROFILE ▸ row. The pointer + second-person
# copy make the standing bird unmistakably the tappable target.
def concept_bubble(surf):
    reg = dio_region(pad=6)
    bw, bh = 128, 58
    bx = reg.right - 6
    # Seat the bubble below the subtitle band so it never covers the wordmark.
    by = reg.top + 8
    bub = pygame.Rect(bx, by, bw, bh)

    # Tail toward Pip (down-left) drawn first so the panel rim laps its base.
    anchor = (reg.centerx + 18, reg.centery)
    tail = [(bub.left + 10, bub.bottom - 12),
            (bub.left + 30, bub.bottom - 6), anchor]
    sh = pygame.Surface((bw + 12, bh + 16), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 120), sh.get_rect(), border_radius=14)
    surf.blit(sh, (bub.x - 4, bub.y + 5))
    pygame.draw.polygon(surf, (0, 0, 0, 120),
                        [(p[0] - 2, p[1] + 3) for p in tail])
    pygame.draw.polygon(surf, (26, 18, 50), tail)

    tap_glow(surf, bub, radius=14, strength=0.8)
    _volume_panel(surf, bub, radius=14)
    pygame.draw.polygon(surf, (26, 18, 50), tail)
    pygame.draw.line(surf, _GOLD_DEEP, tail[0], tail[2], 1)
    pygame.draw.line(surf, _GOLD_DEEP, tail[1], tail[2], 1)

    _tracked_label(surf, "THIS IS YOU", (bub.centerx, bub.top + 15), 11,
                   color=WHITE, track=1, alpha=235)
    pygame.draw.line(surf, (*_GOLD_DEEP, 160),
                     (bub.left + 14, bub.top + 26),
                     (bub.right - 14, bub.top + 26), 1)
    profile_tag(surf, bub.centerx, bub.bottom - 15, w=104)

    records_badge(surf, bub.right - 2, bub.top - 2)


# ── Concept 5 — DASHED HOTSPOT / PRESS-STATE ─────────────────────────────────
# A beveled interactive tap-zone: a rounded, subtly dashed marching-ants
# border rings the diorama with a faint pressed-state tint + inner
# highlight, a PROFILE ▸ tab clipped to the bottom edge, and the records
# pip corner-tucked. Borrows the OS "this whole region is one button" idiom.
def _dashed_rrect(surf, rect, color, radius=16, dash=8, gap=6, width=2):
    """Marching-ants along a rounded rect's four straight edges (corners
    left open, which reads as dashes turning the bend)."""
    x0, y0, x1, y1 = (rect.left + radius, rect.top, rect.right - radius,
                      rect.top)
    edges = [
        ((rect.left + radius, rect.top), (rect.right - radius, rect.top)),
        ((rect.right, rect.top + radius), (rect.right, rect.bottom - radius)),
        ((rect.right - radius, rect.bottom),
         (rect.left + radius, rect.bottom)),
        ((rect.left, rect.bottom - radius), (rect.left, rect.top + radius)),
    ]
    for (ax, ay), (bx, by) in edges:
        dx, dy = bx - ax, by - ay
        length = math.hypot(dx, dy)
        if length == 0:
            continue
        ux, uy = dx / length, dy / length
        d = 0.0
        while d < length:
            e = min(d + dash, length)
            pygame.draw.line(surf, color,
                             (ax + ux * d, ay + uy * d),
                             (ax + ux * e, ay + uy * e), width)
            d += dash + gap
    # Rounded corner ticks so the ring doesn't look broken at the bends.
    for cx, cy, a0, a1 in (
        (rect.left + radius, rect.top + radius, 90, 180),
        (rect.right - radius, rect.top + radius, 0, 90),
        (rect.right - radius, rect.bottom - radius, 270, 360),
        (rect.left + radius, rect.bottom - radius, 180, 270),
    ):
        pygame.draw.arc(surf, color,
                        (cx - radius, cy - radius, radius * 2, radius * 2),
                        math.radians(a0), math.radians(a1), width)


def concept_hotspot(surf):
    reg = dio_region(pad=12)

    tap_glow(surf, reg, radius=18, strength=0.85)
    # Pressed-state fill + inner bevel: a faint warm tint inside the zone,
    # a bright top-left highlight and a dark bottom-right shadow so the
    # whole region reads as one raised, tappable button.
    fill = pygame.Surface(reg.size, pygame.SRCALPHA)
    fill.fill((255, 214, 120, 26))
    surf.blit(fill, reg.topleft)
    pygame.draw.line(surf, (*_GOLD_PALE, 120),
                     (reg.left + 16, reg.top + 2),
                     (reg.right - 16, reg.top + 2), 2)
    pygame.draw.line(surf, (0, 0, 0, 90),
                     (reg.left + 16, reg.bottom - 2),
                     (reg.right - 16, reg.bottom - 2), 2)

    # Solid inner keyline + the dashed marching-ants ring on top.
    pygame.draw.rect(surf, (*_GOLD_DEEP, 150), reg, width=1, border_radius=18)
    _dashed_rrect(surf, reg, _GOLD_BRIGHT, radius=18, dash=9, gap=6, width=2)

    # PROFILE ▸ tab clipped to the bottom edge (a hotspot's action label).
    tab = pygame.Rect(reg.centerx - 48, reg.bottom - 9, 96, 18)
    pygame.draw.rect(surf, (168, 34, 30), tab, border_radius=6)
    pygame.draw.rect(surf, _GOLD_BRIGHT, tab, width=1, border_radius=6)
    _tracked_label(surf, "PROFILE", (tab.centerx - 5, tab.centery), 11,
                   color=(255, 244, 224), track=2, alpha=255)
    tri(surf, tab.right - 8, tab.centery, 4, _GOLD_PALE)

    records_badge(surf, reg.right - 4, reg.top - 2)


# ── Assembly ─────────────────────────────────────────────────────────────────
CONCEPTS = [
    ("1 · FRAMED-IN-PLACE", None, concept_framed),
    ("2 · NAMEPLATE STANDEE", _standee_under, concept_standee),
    ("3 · SPOTLIGHT RING", _spotlight_under, concept_spotlight),
    ("4 · TAP BUBBLE", None, concept_bubble),
    ("5 · DASHED HOTSPOT", None, concept_hotspot),
]


def build_panel(under_fn, over_fn):
    surf = menu_base(under_fn)
    over_fn(surf)
    bottom_chips(surf)
    return surf


def main():
    pad, gap, hdr = 18, 16, 54
    foot = 34                                  # room for the per-panel labels
    cols = len(CONCEPTS)
    sheet_w = pad * 2 + cols * W + (cols - 1) * gap
    sheet_h = pad + hdr + H + foot

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((22, 18, 34))

    title_f = _font(26, True)
    sub_f = _font(15, True)
    t = title_f.render(
        "SKYBIT · Profile menu-entry — Round 1 · the standing Pip IS the button",
        True, (240, 224, 180))
    sheet.blit(t, (pad, 10))
    s = sub_f.render(
        "Five distinct treatments of the ALREADY-drawn Pip diorama "
        "(no second parrot) · violet records badge · PROFILE label · "
        "sin(T·3.6) tap-glow",
        True, (198, 186, 158))
    sheet.blit(s, (pad, 38))

    lab_f = _font(18, True)
    x = pad
    y = pad + hdr
    for label, under_fn, over_fn in CONCEPTS:
        panel = build_panel(under_fn, over_fn)
        pygame.draw.rect(sheet, (8, 5, 20), (x - 2, y - 2, W + 4, H + 4))
        sheet.blit(panel, (x, y))
        li = lab_f.render(label, True, (250, 236, 190))
        sheet.blit(li, li.get_rect(midtop=(x + W // 2, y + H + 6)))
        x += W + gap

    out = os.path.join(os.path.dirname(__file__), "round_1.png")
    pygame.image.save(sheet, out)
    print("saved", out, sheet.get_size())


if __name__ == "__main__":
    main()
