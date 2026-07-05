"""Round 1 — refine the chosen FRAMED-IN-PLACE Profile entry.

The owner picked the framed-in-place finalist (a gilded frame drawn
AROUND the already-standing Pip so the live menu diorama becomes a
tappable character card) but flagged two things: the gold perimeter is
TOO THICK — it should read like a delicate jewel edge, not a lead box —
and the PROFILE label wants to be a little BIGGER for legibility.

This sheet explores FIVE genuinely distinct treatments of a SUBTLE
frame, all sharing the fixed guidelines (live Pip is the button — no
second parrot; PROFILE stays GOLD since scarlet is reserved for START;
a small violet records badge tucks into a top interior corner; the
sin(T*3.6) START-pill pulse drives a soft tap-glow):

  1 · HAIRLINE DOUBLE-RULE  two fine engraved gold lines with an air gap,
                            PROFILE on a slim bottom cartouche.
  2 · CORNER BRACKETS       only gilded L-brackets at the four corners
                            (open sides), airy + modern; PROFILE on a
                            bridging bottom tab.
  3 · INSET MATTE + RIM     a soft dark inner mat with one bright hairline
                            rim; PROFILE ENGRAVED into the mat's lower band.
  4 · ROUNDED THIN BEZEL    a slim rounded bezel (chip-family radius) with
                            a top rim-light + an integrated bottom rail.
  5 · NAMEPLATE-FORWARD     the frame drops to a whisper (faint vignette +
                            a single deep hairline); a prominent beveled
                            PROFILE nameplate does the card work.

Each is composited into a full 360x640 menu mock, and a TRUE 1x proof
crop of every card confirms the (now lighter) frame weight and the
(now larger) PROFILE label read at native scale.
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
from game.draw import lerp_color
from game.hud import (
    _font, _outlined_text, _pill_btn, _volume_panel, _tracked_label,
    _draw_overlay_stars, _draw_mountain_silhouette,
    _draw_trophy, _draw_gear, _coin_icon,
    _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP, _ORANGE_BORDER, _AWSTAR_HI,
)

# Freeze near the crest of the START pill's tappability pulse (draw_menu
# rides it at sin(title_t * 3.6)) so every card shows its tap-glow halo at
# the same brightness and tappability is judged fairly.
T = 0.55
GLOW = 0.5 + 0.5 * math.sin(T * 3.6)          # 0..1 tap-glow pulse
STARS = [(int(37 * i * 1.7 % W), int(23 + 71 * i * 1.3 % 210),
          1 + (i % 2), i * 0.9) for i in range(26)]

# Mid-value gold — the inner step that turns a flat edge into a struck
# bevel (matches the HUD gold family).
_GOLD_MID = (212, 160, 44)
# Records badge ground: a deep violet so the folded-in Awards cue can
# never read as gold currency and never clash with the scarlet START.
_REC_GROUND = (96, 46, 150)
_REC_GROUND_D = (58, 24, 96)

# The PROFILE label is bumped up from the round-2 size 11 so it stays
# legible even as the surrounding gilding thins to a jewel edge.
_LABEL_SIZE = 13


# ── The live diorama (reused Pip, no second parrot) ──────────────────────────
def diorama_rects():
    """House + standing-Pip footprints at their REAL menu positions, so
    every treatment frames exactly what the running menu draws."""
    house = _intro.get_sprite("skyhouse_post")
    hw, hh = house.get_size()
    hx = int(W * 0.30) - hw // 2
    hy = int(H * 0.42) - hh // 2
    house_r = pygame.Rect(hx, hy, hw, hh)
    bird_r = pygame.Rect(90 - 34, int(H * 0.42) - 34, 68, 84)
    return house_r, bird_r, (house, hx, hy)


def draw_diorama(surf):
    """Blit the post-house then the LIVE Bird — the exact menu composition."""
    _house, hx, hy = diorama_rects()[2]
    surf.blit(_house, (hx, hy))
    Bird().draw(surf)


def dio_region(pad=12):
    house_r, bird_r, _ = diorama_rects()
    return house_r.union(bird_r).inflate(pad * 2, pad * 2)


# ── Shared cues ──────────────────────────────────────────────────────────────
def tap_glow(surf, rect, radius=16, strength=1.0):
    """Gold halo whose alpha rides the START-pill sin(t*3.6) pulse so the
    card reads as tappable chrome, not passive scenery."""
    pad = 14
    glow = pygame.Surface((rect.width + pad * 2, rect.height + pad * 2),
                          pygame.SRCALPHA)
    for k in range(pad, 0, -1):
        a = int(strength * (48 + 40 * GLOW) * k / pad / 3.6)
        gr = pygame.Rect(pad - k, pad - k,
                         rect.width + k * 2, rect.height + k * 2)
        pygame.draw.rect(glow, (*_GOLD_BRIGHT, a), gr, border_radius=radius + k)
    surf.blit(glow, (rect.x - pad, rect.y - pad))


def subtle_vignette(surf, fr, alpha=70, inset=6, radius=16):
    """Dim a narrow band AROUND the card then punch the interior back to
    clear, so the eye is pulled to the diorama-as-card WITHOUT dimming Pip
    or bleeding onto the wordmark / START (band is clipped to the card)."""
    band_top = fr.top - 12
    band_h = fr.height + 24
    vig = pygame.Surface((W, band_h), pygame.SRCALPHA)
    vig.fill((4, 2, 16, alpha))
    pygame.draw.rect(vig, (0, 0, 0, 0),
                     fr.inflate(-inset, -inset).move(0, -band_top),
                     border_radius=radius)
    surf.blit(vig, (0, band_top))


def records_badge(surf, cx, cy):
    """The folded-in Awards cue: a violet chip with a legible gold trophy
    and a small superscript count — a distinct shape AND colour so it reads
    as 'records inside', never as a coin."""
    w, hh = 33, 18
    r = pygame.Rect(int(cx - w / 2), int(cy - hh / 2), w, hh)
    sh = pygame.Surface((w + 4, hh + 4), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 135), sh.get_rect(), border_radius=8)
    surf.blit(sh, (r.x - 1, r.y + 2))
    pygame.draw.rect(surf, _REC_GROUND_D, r, border_radius=8)
    pygame.draw.rect(surf, _REC_GROUND, r.inflate(-2, -2), border_radius=7)
    pygame.draw.rect(surf, _GOLD_BRIGHT, r, width=1, border_radius=8)
    _draw_trophy(surf, r.left + 12, r.centery + 1, 7)
    f = _font(10, True)
    img = f.render("3", True, _GOLD_PALE)
    surf.blit(img, img.get_rect(center=(r.right - 8, r.top + 6)))


def tri(surf, cx, cy, size, color):
    """Right-pointing chevron 'tap through' cue — the vendored font has no
    such glyph, so it is a small filled triangle."""
    pygame.draw.polygon(surf, color, [(cx - size // 2, cy - size),
                                      (cx + size // 2, cy),
                                      (cx - size // 2, cy + size)])


def profile_label(surf, plate, dark_engrave=False):
    """PROFILE (gold, bumped size) + a tap chevron, centred on a rail; when
    engraved directly onto a dark mat, a 1px dark shadow sinks the letters."""
    lx = plate.centerx - 7
    if dark_engrave:
        _tracked_label(surf, "PROFILE", (lx, plate.centery + 1), _LABEL_SIZE,
                       color=(20, 10, 4), track=2, alpha=200)
    _tracked_label(surf, "PROFILE", (lx, plate.centery), _LABEL_SIZE,
                   color=_GOLD_PALE, track=2, alpha=250)
    tri(surf, plate.right - 9, plate.centery, 4, _GOLD_PALE)


# ── Option 1 — HAIRLINE DOUBLE-RULE ──────────────────────────────────────────
# Two fine gold lines with a small air gap read as a delicate engraved
# border; PROFILE rides a slim rounded cartouche on the bottom rule.
def opt_hairline(surf):
    fr = dio_region(pad=12)
    fr.height += 16
    subtle_vignette(surf, fr, alpha=78, inset=6, radius=14)
    tap_glow(surf, fr, radius=15, strength=0.9)

    pygame.draw.rect(surf, _GOLD_MID, fr, width=1, border_radius=14)
    pygame.draw.rect(surf, _GOLD_BRIGHT, fr.inflate(-7, -7), width=1,
                     border_radius=10)
    # A single pale top rim between the rules sells 'engraved' over 'drawn'.
    pygame.draw.line(surf, (*_GOLD_PALE, 200), (fr.left + 16, fr.top + 2),
                     (fr.right - 16, fr.top + 2), 1)

    plate = pygame.Rect(fr.centerx - 58, fr.bottom - 20, 116, 19)
    pygame.draw.rect(surf, (16, 10, 34), plate, border_radius=9)
    pygame.draw.rect(surf, _GOLD_MID, plate, width=1, border_radius=9)
    profile_label(surf, plate)
    records_badge(surf, fr.right - 27, fr.top + 16)


# ── Option 2 — CORNER BRACKETS ───────────────────────────────────────────────
# Only gilded L-brackets clip the four corners; the sides stay open for an
# airy, modern viewfinder look. PROFILE rides a tab bridging the open base.
def opt_brackets(surf):
    fr = dio_region(pad=13)
    fr.height += 16
    subtle_vignette(surf, fr, alpha=66, inset=2, radius=12)
    tap_glow(surf, fr, radius=13, strength=0.9)

    arm, th = 22, 3
    corners = ((fr.left, fr.top, 1, 1), (fr.right, fr.top, -1, 1),
               (fr.left, fr.bottom, 1, -1), (fr.right, fr.bottom, -1, -1))
    for x, y, sx, sy in corners:
        # Deep foot first, bright cap over it — a struck two-tone bracket.
        for col, off in ((_GOLD_DEEP, 1), (_GOLD_BRIGHT, 0)):
            pygame.draw.line(surf, col, (x, y + off * sy),
                             (x + arm * sx, y + off * sy), th)
            pygame.draw.line(surf, col, (x + off * sx, y),
                             (x + off * sx, y + arm * sy), th)
        pygame.draw.circle(surf, _GOLD_PALE, (x, y), 2)

    tab = pygame.Rect(fr.centerx - 52, fr.bottom - 10, 104, 20)
    sh = pygame.Surface((tab.w + 4, tab.h + 4), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 120), sh.get_rect(), border_radius=9)
    surf.blit(sh, (tab.x - 2, tab.y + 1))
    pygame.draw.rect(surf, (20, 12, 38), tab, border_radius=9)
    pygame.draw.rect(surf, _GOLD_BRIGHT, tab, width=1, border_radius=9)
    profile_label(surf, tab)
    records_badge(surf, fr.right - 30, fr.top + 18)


# ── Option 3 — INSET MATTE + THIN RIM ────────────────────────────────────────
# A soft translucent dark mat borders the interior with a single bright
# hairline rim; PROFILE is ENGRAVED straight into the mat's lower band —
# no separate plate — so the card feels like a matted museum print.
def opt_matte(surf):
    fr = dio_region(pad=13)
    fr.height += 18
    subtle_vignette(surf, fr, alpha=58, inset=6, radius=16)
    tap_glow(surf, fr, radius=16, strength=0.9)

    mat = pygame.Surface((fr.w, fr.h), pygame.SRCALPHA)
    pygame.draw.rect(mat, (10, 6, 26, 165), mat.get_rect(), border_radius=15)
    # Punch the interior so Pip shows through un-dimmed; the remaining band
    # is the mat. The bottom band is left taller for the engraved label.
    interior = mat.get_rect().inflate(-24, -26)
    interior.height -= 8
    interior.top -= 4
    pygame.draw.rect(mat, (0, 0, 0, 0), interior, border_radius=8)
    surf.blit(mat, fr.topleft)

    pygame.draw.rect(surf, _GOLD_BRIGHT, fr, width=1, border_radius=15)
    pygame.draw.line(surf, (*_GOLD_PALE, 150), (fr.left + 16, fr.top + 1),
                     (fr.right - 16, fr.top + 1), 1)

    band = pygame.Rect(fr.left, fr.bottom - 20, fr.w, 20)
    profile_label(surf, band, dark_engrave=True)
    records_badge(surf, fr.right - 28, fr.top + 17)


# ── Option 4 — ROUNDED THIN BEZEL ────────────────────────────────────────────
# A slim rounded bezel (chip-family radius) with a deep base, one bright
# rim and a top rim-light; an integrated dark bottom rail carries PROFILE.
def opt_bezel(surf):
    fr = dio_region(pad=12)
    fr.height += 20
    subtle_vignette(surf, fr, alpha=68, inset=6, radius=17)
    tap_glow(surf, fr, radius=17, strength=0.95)

    pygame.draw.rect(surf, _GOLD_DEEP, fr, width=3, border_radius=16)
    pygame.draw.rect(surf, _GOLD_BRIGHT, fr.inflate(-1, -1), width=1,
                     border_radius=16)
    pygame.draw.line(surf, _GOLD_PALE, (fr.left + 18, fr.top + 2),
                     (fr.right - 18, fr.top + 2), 2)

    rail = pygame.Rect(fr.left + 3, fr.bottom - 22, fr.w - 6, 19)
    rl = pygame.Surface((rail.w, rail.h), pygame.SRCALPHA)
    pygame.draw.rect(rl, (14, 9, 32, 232), rl.get_rect(),
                     border_bottom_left_radius=13, border_bottom_right_radius=13)
    surf.blit(rl, rail.topleft)
    pygame.draw.line(surf, (*_GOLD_MID, 200), (rail.left + 8, rail.top),
                     (rail.right - 8, rail.top), 1)
    profile_label(surf, rail)
    records_badge(surf, fr.right - 27, fr.top + 17)


# ── Option 5 — NAMEPLATE-FORWARD ─────────────────────────────────────────────
# The frame drops to a whisper — a faint vignette plus a single deep
# hairline — and a prominent beveled brass PROFILE nameplate does the
# 'this is a card' work on its own.
def opt_nameplate(surf):
    fr = dio_region(pad=11)
    fr.height += 22
    subtle_vignette(surf, fr, alpha=54, inset=8, radius=14)
    tap_glow(surf, fr, radius=14, strength=0.8)

    pygame.draw.rect(surf, (*_GOLD_DEEP, 210), fr, width=1, border_radius=13)

    plate = pygame.Rect(fr.centerx - 63, fr.bottom - 25, 126, 23)
    sh = pygame.Surface((plate.w + 6, plate.h + 6), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 140), sh.get_rect(), border_radius=8)
    surf.blit(sh, (plate.x - 3, plate.y + 2))
    pygame.draw.rect(surf, _GOLD_DEEP, plate, border_radius=7)
    pygame.draw.rect(surf, _GOLD_MID, plate.inflate(-3, -3), border_radius=6)
    pygame.draw.line(surf, _GOLD_PALE, (plate.left + 8, plate.top + 3),
                     (plate.right - 8, plate.top + 3), 1)
    pygame.draw.line(surf, (60, 40, 6), (plate.left + 8, plate.bottom - 3),
                     (plate.right - 8, plate.bottom - 3), 1)
    inset = plate.inflate(-8, -8)
    pygame.draw.rect(surf, (30, 18, 8), inset, border_radius=4)
    profile_label(surf, inset, dark_engrave=True)
    records_badge(surf, fr.right - 26, fr.top + 16)


# ── Shared menu mock ─────────────────────────────────────────────────────────
def menu_base():
    surf = pygame.Surface((W, H)).convert_alpha()
    for yy in range(H):
        t = yy / (H - 1)
        surf.fill(lerp_color((90, 150, 205), (196, 168, 150), t), (0, yy, W, 1))
    dim = pygame.Surface((W, H), pygame.SRCALPHA)
    dim.fill((6, 1, 21, 150))
    surf.blit(dim, (0, 0))
    _draw_overlay_stars(surf, STARS, T)
    _draw_mountain_silhouette(surf, alpha=180)

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
    """STORE · TOP 10 · SETTINGS — Awards has folded into Profile."""
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


# ── Assembly ─────────────────────────────────────────────────────────────────
OPTIONS = [
    ("1 · HAIRLINE DOUBLE-RULE", opt_hairline),
    ("2 · CORNER BRACKETS", opt_brackets),
    ("3 · INSET MATTE + RIM", opt_matte),
    ("4 · ROUNDED THIN BEZEL", opt_bezel),
    ("5 · NAMEPLATE-FORWARD", opt_nameplate),
]

# Card region cropped for the true-1x proof strips — from just below the
# subtitle down through the card, so frame weight + label read at native scale.
PROOF = pygame.Rect(4, 168, 212, 200)


def build_panel(over_fn):
    surf = menu_base()
    over_fn(surf)
    bottom_chips(surf)
    return surf


def main():
    pad, gap = 20, 22
    hdr = 66
    lab = 30
    proof_gap = 22
    proof_lab = 26
    proof_h = PROOF.height
    n = len(OPTIONS)

    sheet_w = pad * 2 + n * W + (n - 1) * gap
    sheet_h = (pad + hdr + H + lab + proof_gap
               + proof_lab + proof_h + pad)

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((22, 18, 34))

    title_f = _font(26, True)
    sub_f = _font(15, True)
    sheet.blit(title_f.render(
        "SKYBIT · Profile FRAME REFINE — Round 1 · five subtler-frame treatments",
        True, (240, 224, 180)), (pad, 12))
    sheet.blit(sub_f.render(
        "Owner asks: THINNER jewel-edge frame + a BIGGER PROFILE label · live "
        "Pip IS the button · PROFILE stays GOLD · violet records badge inside "
        "· sin(T·3.6) tap-glow",
        True, (198, 186, 158)), (pad, 40))

    lab_f = _font(18, True)
    proof_f = _font(14, True)

    panels = []
    x = pad
    y = pad + hdr
    for label, over_fn in OPTIONS:
        panel = build_panel(over_fn)
        panels.append((label, panel, x))
        pygame.draw.rect(sheet, (8, 5, 20), (x - 2, y - 2, W + 4, H + 4))
        sheet.blit(panel, (x, y))
        li = lab_f.render(label, True, (250, 236, 190))
        sheet.blit(li, li.get_rect(midtop=(x + W // 2, y + H + 6)))
        x += W + gap

    py = y + H + lab + proof_gap + proof_lab
    for label, panel, px in panels:
        crop = panel.subsurface(PROOF).copy()
        cx = px + (W - PROOF.width) // 2
        pygame.draw.rect(sheet, (40, 30, 58),
                         (cx - 2, py - 2, PROOF.width + 4, proof_h + 4))
        sheet.blit(crop, (cx, py))
        pl = proof_f.render("TRUE 1× — " + label.split("·")[0].strip(),
                            True, (232, 214, 168))
        sheet.blit(pl, pl.get_rect(midbottom=(cx + PROOF.width // 2, py - 6)))

    out = os.path.join(os.path.dirname(__file__), "round_1.png")
    pygame.image.save(sheet, out)
    print("saved", out, sheet.get_size())


if __name__ == "__main__":
    main()
