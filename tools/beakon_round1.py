"""Master Beakon — round 1 exploration sheet (5 elder-macaw sage takes).

Headless. Reuses the store's obsidian-and-gold card helpers + the hud gold
palette so the explorations read as the real ARCADE section. Beakon is the
game's scarlet macaw aged into a guru: droopy ruffled plumage, heavy brow,
one squinted eye, a long wattle "beard", perched cross-style. Each tile pairs
him with a Scroll of Wisdom and a 20-coin price, varying the silhouette/pose/
expression and the scroll + price presentation.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import math
import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game.store import (
    _vgrad_panel, _drop_shadow, _inset_disc, _gradient_text, _coin_glyph,
    _GOLD_DEEP,
)
from game.hud import _font, _GOLD_BRIGHT, _GOLD_PALE
from game.draw import lerp_color

# Card / obsidian palette (kept consistent with the store cards)
OBS_TOP = (30, 27, 44)
OBS_BOT = (12, 10, 22)
HEADER_TOP = (44, 38, 60)
HEADER_BOT = (24, 20, 36)

# Aged-macaw palette — the game's scarlet/blue macaw, muted and greyed for age.
AGED_RED      = (196,  74,  72)   # dusty scarlet body
AGED_RED_D    = (138,  46,  48)
AGED_RED_HI   = (224, 120, 110)
AGED_BLUE     = ( 70, 104, 168)   # faded wing blue
AGED_BLUE_D   = ( 44,  70, 120)
AGED_TEAL     = ( 96, 168, 132)   # muted green primary tip
AGED_GOLD     = (210, 176,  92)   # faded yellow secondary
BEARD_GREY    = (212, 206, 196)   # grizzled wattle-beard feathers
BEARD_SHADE   = (168, 160, 150)
BROW_GREY     = (196, 188, 176)   # bushy white eyebrow
SKIN_PALE     = (244, 232, 220)   # bare facial patch
BEAK_GOLD     = (228, 178,  70)
BEAK_DARK     = (176, 124,  40)
PERCH_WOOD    = (120,  84,  52)
PERCH_WOOD_D  = ( 84,  56,  34)
PERCH_WOOD_HI = (156, 116,  74)
CUSHION       = (132,  60,  78)
CUSHION_HI    = (176,  96, 112)
CUSHION_D     = ( 92,  40,  56)
PARCH_LIGHT   = (242, 226, 190)
PARCH_MID     = (224, 202, 158)
PARCH_SHADE   = (196, 168, 120)
INK           = ( 78,  58,  44)


def _aaellipse(surf, color, center, rx, ry, width=0):
    cx, cy = center
    rect = pygame.Rect(int(cx - rx), int(cy - ry), int(rx * 2), int(ry * 2))
    pygame.draw.ellipse(surf, color, rect, width)


# ── shared Beakon body parts ─────────────────────────────────────────────────

def _beard(surf, cx, cy, length=16, width=11, strands=5):
    """A long grizzled wattle-beard of drooping feather strands under the chin."""
    for i in range(strands):
        t = (i / max(1, strands - 1)) - 0.5
        x = cx + t * width
        droop = length * (1.0 - 0.5 * abs(t))
        col = BEARD_GREY if i % 2 == 0 else BEARD_SHADE
        pygame.draw.line(surf, BEARD_SHADE, (x, cy), (x + t * 4, cy + droop + 1), 3)
        pygame.draw.line(surf, col, (x, cy), (x + t * 4, cy + droop), 2)
    # a couple of stray wisps at the tip
    pygame.draw.line(surf, BEARD_GREY, (cx, cy + length - 2),
                     (cx + 2, cy + length + 3), 1)


def _brow(surf, x0, y0, x1, y1, thick=4):
    """A bushy heavy white eyebrow — the guru's signature."""
    pygame.draw.line(surf, BEARD_SHADE, (x0, y0 + 1), (x1, y1 + 1), thick)
    pygame.draw.line(surf, BROW_GREY, (x0, y0), (x1, y1), thick - 1)
    # a few tufts breaking the line
    pygame.draw.line(surf, BROW_GREY, (x1, y1), (x1 + 3, y1 - 3), 2)
    pygame.draw.line(surf, BROW_GREY, (x0, y0), (x0 - 2, y0 - 3), 2)


def _squint_eye(surf, cx, cy, closed=False):
    """Either a deadpan squint (a closed crescent) or a half-lidded knowing eye."""
    _aaellipse(surf, SKIN_PALE, (cx, cy), 6, 5)
    pygame.draw.line(surf, (224, 200, 192), (cx - 5, cy - 2), (cx + 5, cy - 2), 1)
    if closed:
        # serene closed crescent
        pygame.draw.arc(surf, (60, 42, 40),
                        (cx - 5, cy - 4, 10, 9), math.radians(200), math.radians(340), 2)
    else:
        # half-lidded knowing pupil under a heavy upper lid
        pygame.draw.circle(surf, (44, 30, 32), (cx + 1, cy + 1), 3)
        pygame.draw.circle(surf, (255, 255, 255), (cx, cy), 1)
        pygame.draw.line(surf, (150, 120, 110), (cx - 5, cy - 1), (cx + 5, cy - 2), 2)


def _aged_wing(surf, cx, cy, droop=True, scale=1.0):
    """A folded, slightly ragged wing in faded macaw blues with a green tip."""
    s = scale
    pts = [(cx - 2*s, cy - 8*s), (cx + 12*s, cy - 4*s), (cx + 16*s, cy + 6*s),
           (cx + 2*s, cy + 14*s), (cx - 6*s, cy + 6*s)]
    pygame.draw.polygon(surf, (0, 0, 0, 70),
                        [(p[0] + 1, p[1] + 2) for p in pts])
    pygame.draw.polygon(surf, AGED_BLUE, pts)
    pygame.draw.polygon(surf, AGED_BLUE_D,
                        [(cx - 2*s, cy - 8*s), (cx + 2*s, cy + 14*s), (cx - 6*s, cy + 6*s)])
    # faded yellow secondary stripe + green primary tip
    pygame.draw.polygon(surf, AGED_GOLD,
                        [(cx + 8*s, cy - 4*s), (cx + 14*s, cy + 1*s),
                         (cx + 12*s, cy + 6*s), (cx + 6*s, cy + 2*s)])
    pygame.draw.polygon(surf, AGED_TEAL,
                        [(cx + 12*s, cy - 4*s), (cx + 17*s, cy + 1*s), (cx + 16*s, cy + 6*s)])
    # ruffled feather divider lines (a few extra for the unkempt elder look)
    for dy in (-3, 1, 5):
        pygame.draw.line(surf, AGED_BLUE_D,
                         (cx, cy + dy*s), (cx + 13*s, cy + dy*s + 2*s), 1)


def _beakon_head(surf, cx, cy, *, eye_closed, brow_lift=0, beard_len=16,
                 beak_open=False):
    """The aged macaw head: ruffled crown, heavy brow, bare patch, squint,
    hooked beak, long beard. cx,cy = head centre."""
    # ruffled crown — body-red dome with broken-up tuft edge
    _aaellipse(surf, AGED_RED_D, (cx + 1, cy + 1), 13, 12)
    _aaellipse(surf, AGED_RED, (cx, cy), 13, 12)
    _aaellipse(surf, AGED_RED_HI, (cx - 3, cy - 6), 7, 4)
    for ang in range(150, 280, 18):  # crown tufts sticking up/back
        a = math.radians(ang)
        ex, ey = cx + math.cos(a) * 12, cy + math.sin(a) * 11
        pygame.draw.line(surf, AGED_RED_D, (ex, ey),
                         (ex + math.cos(a) * 4, ey + math.sin(a) * 4), 2)
    # bare facial patch
    _aaellipse(surf, SKIN_PALE, (cx + 4, cy + 1), 8, 7)
    # heavy brow over the eye
    _brow(surf, cx - 1, cy - 5 - brow_lift, cx + 10, cy - 6, thick=4)
    _squint_eye(surf, cx + 4, cy, closed=eye_closed)
    # hooked beak
    if beak_open:
        beak_pts = [(cx + 10, cy - 1), (cx + 20, cy + 1), (cx + 16, cy + 4), (cx + 9, cy + 3)]
        low = [(cx + 9, cy + 4), (cx + 16, cy + 5), (cx + 12, cy + 8), (cx + 8, cy + 7)]
        pygame.draw.polygon(surf, BEAK_DARK, low)
        pygame.draw.polygon(surf, (40, 20, 24), low, 1)
    else:
        beak_pts = [(cx + 10, cy), (cx + 21, cy + 3), (cx + 17, cy + 8), (cx + 9, cy + 5)]
    pygame.draw.polygon(surf, BEAK_GOLD, beak_pts)
    pygame.draw.polygon(surf, BEAK_DARK, beak_pts, 1)
    pygame.draw.line(surf, (255, 226, 150), (cx + 11, cy + 1), (cx + 17, cy + 3), 1)
    # long grizzled beard under the chin
    _beard(surf, cx + 2, cy + 9, length=beard_len, width=12)


def _scroll(surf, cx, cy, w, h, tip_lines=None, rolled=False):
    """An unfurled parchment with gold-rimmed rollers. Optional sample wisdom
    rendered as faint ruled ink lines (real text is drawn separately by caller)."""
    rect = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    # drop shadow
    sh = pygame.Surface((w + 8, h + 8), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 90), sh.get_rect(), border_radius=6)
    surf.blit(sh, (rect.x - 2, rect.y + 3))
    # parchment body with a subtle vertical aging gradient
    body = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        t = y / max(1, h - 1)
        c = lerp_color(PARCH_LIGHT, PARCH_SHADE, (abs(t - 0.5) * 2) ** 1.6 * 0.7)
        pygame.draw.line(body, c, (0, y), (w, y))
    surf.blit(body, rect.topleft)
    pygame.draw.rect(surf, PARCH_SHADE, rect, 1)
    # gold-rim rollers top + bottom
    for ry in (rect.top, rect.bottom - 4):
        roller = pygame.Rect(rect.x - 4, ry - 1, w + 8, 6)
        pygame.draw.rect(surf, PERCH_WOOD_D, roller, border_radius=3)
        pygame.draw.rect(surf, _GOLD_DEEP, roller, 1, border_radius=3)
        pygame.draw.circle(surf, _GOLD_BRIGHT, (roller.left + 1, roller.centery), 2)
        pygame.draw.circle(surf, _GOLD_BRIGHT, (roller.right - 1, roller.centery), 2)
        pygame.draw.line(surf, _GOLD_PALE, (roller.left + 4, ry),
                         (roller.right - 4, ry), 1)
    return rect


def _coin_chip(surf, cx, cy, amount=20, scale=1.0):
    """A 20-coin price chip: dark gold-rimmed pill + coin glyph + amount."""
    f = _font(int(13 * scale), True)
    txt = str(amount)
    tw = f.size(txt)[0]
    r = int(9 * scale)
    pad = int(7 * scale)
    pill_w = r * 2 + tw + pad * 2 + int(4 * scale)
    pill_h = r * 2 + int(6 * scale)
    pill = pygame.Rect(cx - pill_w // 2, cy - pill_h // 2, pill_w, pill_h)
    chip = pygame.Surface((pill_w, pill_h), pygame.SRCALPHA)
    for y in range(pill_h):
        c = lerp_color((52, 40, 24), (28, 20, 12), y / pill_h)
        pygame.draw.line(chip, (*c, 235), (0, y), (pill_w, y))
    mask = pygame.Surface((pill_w, pill_h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(),
                     border_radius=pill_h // 2)
    chip.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(chip, pill.topleft)
    pygame.draw.rect(surf, _GOLD_DEEP, pill, 1, border_radius=pill_h // 2)
    _coin_glyph(surf, pill.left + r + int(3 * scale), pill.centery, r)
    img = f.render(txt, True, _GOLD_PALE)
    surf.blit(img, img.get_rect(midleft=(pill.left + r * 2 + int(6 * scale),
                                         pill.centery)))


def _card(w, h):
    """An obsidian ARCADE card with a gold-rim header band."""
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    rect = pygame.Rect(0, 0, w, h)
    _drop_shadow(surf, rect, 14)
    surf.blit(_vgrad_panel(w, h, 14, OBS_TOP, OBS_BOT), (0, 0))
    pygame.draw.rect(surf, _GOLD_DEEP, rect, 2, border_radius=14)
    pygame.draw.rect(surf, (*_GOLD_BRIGHT, 90), rect.inflate(-3, -3), 1,
                     border_radius=12)
    # header band
    hh = 30
    head = _vgrad_panel(w - 8, hh, 9, HEADER_TOP, HEADER_BOT)
    surf.blit(head, (4, 5))
    pygame.draw.rect(surf, (*_GOLD_DEEP, 160), (4, 5, w - 8, hh), 1,
                     border_radius=9)
    _gradient_text(surf, "MASTER BEAKON", _font(15, True),
                   (w // 2, 5 + hh // 2), _GOLD_PALE, _GOLD_BRIGHT,
                   outline=(40, 24, 10))
    return surf, hh


def _stage_disc(surf, cx, cy, r):
    _inset_disc(surf, cx, cy, r)
    # faint radial aura behind him so he reads as enthroned in wisdom
    aura = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    for i in range(6):
        rr = int(r * (1 - i / 8))
        pygame.draw.circle(aura, (*_GOLD_BRIGHT, 6), (r, r), rr, 2)
    surf.blit(aura, (cx - r, cy - r))


# ── the five versions ─────────────────────────────────────────────────────────

def version_1(w, h):
    """Lotus master on a meditation cushion, scroll across his lap, price chip
    below. Eyes serenely closed — the classic guru."""
    surf, hh = _card(w, h)
    cx = w // 2
    disc_cy = 5 + hh + 64
    _stage_disc(surf, cx, disc_cy, 60)
    # meditation cushion
    pygame.draw.ellipse(surf, CUSHION_D, (cx - 42, disc_cy + 30, 84, 26))
    pygame.draw.ellipse(surf, CUSHION, (cx - 40, disc_cy + 26, 80, 24))
    pygame.draw.ellipse(surf, CUSHION_HI, (cx - 30, disc_cy + 28, 40, 8))
    for tx in range(cx - 34, cx + 34, 12):  # tuft seams
        pygame.draw.line(surf, CUSHION_D, (tx, disc_cy + 30), (tx, disc_cy + 50), 1)
    pygame.draw.circle(surf, _GOLD_BRIGHT, (cx, disc_cy + 38), 2)  # button
    # body (plump, sitting)
    bx, by = cx, disc_cy + 16
    _aaellipse(surf, AGED_RED_D, (bx + 1, by + 2), 26, 23)
    _aaellipse(surf, AGED_RED, (bx, by), 26, 22)
    _aaellipse(surf, AGED_RED_HI, (bx - 6, by - 8), 14, 8)
    _aged_wing(surf, bx - 18, by - 2)
    _aged_wing(surf, bx + 8, by - 2)  # near wing wrapped forward
    # crossed feet peeking under the scroll
    for fx in (bx - 9, bx + 9):
        pygame.draw.line(surf, BEAK_DARK, (fx, by + 18), (fx + (3 if fx > bx else -3), by + 22), 3)
    # scroll resting across the lap
    _scroll(surf, bx, by + 12, 64, 22)
    f = _font(8, True)
    for i, ln in enumerate(("Tip XLII", "~~~~~~~~")):
        img = f.render(ln, True, INK)
        surf.blit(img, img.get_rect(center=(bx, by + 7 + i * 8)))
    # head sits above the body
    _beakon_head(surf, bx, by - 20, eye_closed=True, beard_len=18)
    # price chip
    _coin_chip(surf, cx, h - 22, 20)
    f2 = _font(9, True)
    sub = f2.render("TIPS FOR LIFE", True, _GOLD_PALE)
    surf.blit(sub, sub.get_rect(center=(cx, h - 40)))
    return surf, "V1 Lotus master on cushion, closed-eye serene, scroll across lap, 20-coin chip below"


def version_2(w, h):
    """Perched on a worn branch, leaning on the scroll like a cane; a speech-
    parchment above delivers a sample cryptic tip. Deadpan half-lidded eye."""
    surf, hh = _card(w, h)
    cx = w // 2
    # speech-parchment banner up top with a real sample tip
    pr = _scroll(surf, cx, 5 + hh + 26, w - 30, 36)
    f = _font(9, True)
    for i, ln in enumerate(("Do not pay for things", "you do not understand.")):
        img = f.render(ln, True, INK)
        surf.blit(img, img.get_rect(center=(cx, pr.top + 11 + i * 12)))
    # little tail connecting parchment to Beakon
    pygame.draw.polygon(surf, PARCH_MID,
                        [(cx - 6, pr.bottom - 2), (cx + 6, pr.bottom - 2), (cx - 2, pr.bottom + 8)])
    # worn wooden perch branch
    by = h - 40
    pygame.draw.line(surf, PERCH_WOOD_D, (16, by + 3), (w - 16, by + 7), 8)
    pygame.draw.line(surf, PERCH_WOOD, (16, by), (w - 16, by + 4), 7)
    pygame.draw.line(surf, PERCH_WOOD_HI, (20, by - 1), (w - 24, by + 2), 2)
    for kx in range(28, w - 28, 22):  # bark knots
        pygame.draw.circle(surf, PERCH_WOOD_D, (kx, by + 1), 2)
    # body perched, slight forward lean
    bx, bcy = cx + 4, by - 24
    _aaellipse(surf, AGED_RED_D, (bx + 1, bcy + 2), 22, 24)
    _aaellipse(surf, AGED_RED, (bx, bcy), 22, 23)
    _aaellipse(surf, AGED_RED_HI, (bx - 5, bcy - 9), 12, 7)
    _aged_wing(surf, bx - 16, bcy)
    # gnarled talons gripping the branch
    for fx in (bx - 6, bx + 6):
        pygame.draw.line(surf, BEAK_DARK, (fx, bcy + 18), (fx, by - 2), 3)
        for tx in (-3, 0, 3):
            pygame.draw.line(surf, BEAK_DARK, (fx, by - 2), (fx + tx, by + 3), 2)
    # rolled scroll as a leaning cane on his right
    cane_x = bx + 22
    pygame.draw.line(surf, PARCH_SHADE, (cane_x + 1, bcy - 4), (cane_x + 6, by - 2), 7)
    pygame.draw.line(surf, PARCH_LIGHT, (cane_x, bcy - 4), (cane_x + 5, by - 2), 5)
    pygame.draw.circle(surf, _GOLD_BRIGHT, (cane_x, bcy - 6), 3)
    pygame.draw.circle(surf, _GOLD_DEEP, (cane_x, bcy - 6), 3, 1)
    _beakon_head(surf, bx, bcy - 20, eye_closed=False, beard_len=16)
    # price chip on the perch
    _coin_chip(surf, cx, h - 16, 20)
    return surf, "V2 Perched on branch leaning on rolled-scroll cane, speech-parchment tip above, deadpan eye"


def version_3(w, h):
    """Bust-style portrait: a large, dignified close-up of Beakon's head and
    shoulders filling the disc, an unfurled scroll beside him, price chip in a
    corner. Maximum 'wise face' read."""
    surf, hh = _card(w, h)
    cx = w // 2
    disc_cy = 5 + hh + 70
    _stage_disc(surf, cx - 16, disc_cy, 66)
    # shoulders / chest filling the bottom of the disc
    bx, bcy = cx - 16, disc_cy + 34
    _aaellipse(surf, AGED_RED_D, (bx, bcy + 2), 34, 22)
    _aaellipse(surf, AGED_RED, (bx, bcy), 33, 21)
    _aged_wing(surf, bx - 26, bcy - 4, scale=1.1)
    _aged_wing(surf, bx + 16, bcy - 4, scale=1.1)
    # big head, drawn at ~1.6x by manual scaling of the helper geometry
    big = pygame.Surface((120, 120), pygame.SRCALPHA)
    _beakon_head(big, 50, 50, eye_closed=False, beard_len=22, brow_lift=2)
    big = pygame.transform.smoothscale(big, (180, 180))
    surf.blit(big, big.get_rect(center=(bx + 4, bcy - 38)))
    # unfurled scroll beside him on the right
    sr = _scroll(surf, w - 34, disc_cy + 6, 50, 60)
    f = _font(8, True)
    for i in range(5):
        y = sr.top + 12 + i * 9
        pygame.draw.line(surf, INK, (sr.left + 8, y), (sr.right - 8, y), 1)
    title = f.render("TIPS", True, INK)
    surf.blit(title, title.get_rect(center=(sr.centerx, sr.top + 6)))
    # price chip bottom-left corner
    _coin_chip(surf, 36, h - 18, 20, scale=0.95)
    return surf, "V3 Dignified bust close-up, max wise-face read, unfurled scroll beside, corner price chip"


def version_4(w, h):
    """Throned cross-legged on a stone meditation dais, an open scroll held up
    in one wing-hand presenting the price, the other raised in a teaching mudra.
    Speech-parchment ribbon banner under the header reads 'TIPS FOR LIFE'."""
    surf, hh = _card(w, h)
    cx = w // 2
    # ribbon banner under header
    bw = w - 40
    ribbon = pygame.Rect(cx - bw // 2, 5 + hh + 4, bw, 18)
    pygame.draw.rect(surf, PERCH_WOOD_D, ribbon, border_radius=4)
    pygame.draw.rect(surf, _GOLD_DEEP, ribbon, 1, border_radius=4)
    _gradient_text(surf, "TIPS FOR LIFE", _font(11, True), ribbon.center,
                   _GOLD_PALE, _GOLD_BRIGHT, shadow=False)
    disc_cy = 5 + hh + 86
    _stage_disc(surf, cx, disc_cy, 60)
    # stone dais
    dais = pygame.Rect(cx - 46, disc_cy + 30, 92, 22)
    pygame.draw.rect(surf, (52, 48, 60), dais, border_radius=4)
    pygame.draw.rect(surf, (74, 70, 84), dais.inflate(-4, -10).move(0, -4),
                     border_radius=3)
    pygame.draw.line(surf, (96, 92, 108), (dais.left + 4, dais.top + 2),
                     (dais.right - 4, dais.top + 2), 1)
    # body cross-legged
    bx, by = cx, disc_cy + 14
    _aaellipse(surf, AGED_RED_D, (bx + 1, by + 2), 25, 22)
    _aaellipse(surf, AGED_RED, (bx, by), 25, 21)
    _aaellipse(surf, AGED_RED_HI, (bx - 6, by - 8), 13, 7)
    # crossed legs / feet on the dais
    pygame.draw.arc(surf, BEAK_DARK, (bx - 20, by + 12, 40, 18),
                    math.radians(200), math.radians(340), 4)
    for fx in (bx - 12, bx + 12):
        pygame.draw.circle(surf, BEAK_GOLD, (fx, by + 20), 3)
        pygame.draw.circle(surf, BEAK_DARK, (fx, by + 20), 3, 1)
    # left wing raised in a teaching mudra
    _aged_wing(surf, bx - 24, by - 10, scale=0.9)
    pygame.draw.circle(surf, AGED_RED, (bx - 26, by - 18), 4)  # raised tip "ok" gesture
    pygame.draw.circle(surf, _GOLD_BRIGHT, (bx - 26, by - 18), 5, 1)
    # right wing holds up a small open scroll showing the price
    sr = _scroll(surf, bx + 26, by - 6, 34, 30)
    _beakon_head(surf, bx, by - 19, eye_closed=True, beard_len=18)
    # price drawn on the held scroll via a coin chip overlapping it
    _coin_chip(surf, sr.centerx, sr.centery, 20, scale=0.78)
    return surf, "V4 Throned cross-legged on stone dais, teaching mudra + held price-scroll, 'TIPS FOR LIFE' ribbon"


def version_5(w, h):
    """Profile/side-on hermit silhouette: Beakon faces left in meditation,
    very long beard, a tall unfurled scroll hanging beside him like a temple
    banner with sample tips, price tag pinned to the scroll bottom. Most
    'fortune-teller booth' of the set."""
    surf, hh = _card(w, h)
    cx = w // 2
    # tall temple-banner scroll on the left
    sr = _scroll(surf, 40, 5 + hh + 78, 56, 116)
    f = _font(8, True)
    head = f.render("TIPS FOR LIFE", True, INK)
    surf.blit(head, head.get_rect(center=(sr.centerx, sr.top + 8)))
    pygame.draw.line(surf, PARCH_SHADE, (sr.left + 6, sr.top + 14),
                     (sr.right - 6, sr.top + 14), 1)
    sample = ("Fear the wall", "you fear, not", "the one you", "see. ~ B")
    for i, ln in enumerate(sample):
        img = f.render(ln, True, INK)
        surf.blit(img, img.get_rect(center=(sr.centerx, sr.top + 26 + i * 12)))
    for i in range(3):  # ruled tail lines
        y = sr.top + 80 + i * 9
        pygame.draw.line(surf, INK, (sr.left + 8, y), (sr.right - 8, y), 1)
    # price tag pinned to scroll bottom
    _coin_chip(surf, sr.centerx, sr.bottom - 12, 20, scale=0.85)
    # Beakon in profile on the right, on a small worn perch stump
    px, py = w - 60, h - 46
    pygame.draw.rect(surf, PERCH_WOOD_D, (px - 16, py, 32, 18), border_radius=3)
    pygame.draw.rect(surf, PERCH_WOOD, (px - 16, py - 2, 32, 8), border_radius=3)
    pygame.draw.line(surf, PERCH_WOOD_HI, (px - 12, py - 1), (px + 12, py - 1), 1)
    bx, bcy = px, py - 26
    _aaellipse(surf, AGED_RED_D, (bx + 1, bcy + 2), 21, 23)
    _aaellipse(surf, AGED_RED, (bx, bcy), 21, 22)
    _aaellipse(surf, AGED_RED_HI, (bx - 5, bcy - 9), 11, 6)
    _aged_wing(surf, bx - 16, bcy, scale=0.95)
    for fx in (bx - 5, bx + 5):  # talons on stump
        pygame.draw.line(surf, BEAK_DARK, (fx, bcy + 18), (fx, py - 1), 3)
    # head, extra-long beard for the hermit read
    _beakon_head(surf, bx, bcy - 18, eye_closed=True, beard_len=26)
    return surf, "V5 Fortune-teller booth: profile hermit on stump beside a tall temple-banner scroll of tips + pinned price"


# ── compose sheet ─────────────────────────────────────────────────────────────

def build():
    CARD_W, CARD_H = 240, 300
    PAD = 26
    LABEL_H = 30
    cols, rows = 3, 2
    sheet_w = PAD + cols * (CARD_W + PAD)
    sheet_h = PAD + rows * (CARD_H + LABEL_H + PAD) + 40
    sheet = pygame.Surface((sheet_w, sheet_h))
    # backdrop: a soft night-purple wash like the profile background
    for y in range(sheet_h):
        c = lerp_color((18, 14, 34), (8, 6, 18), y / sheet_h)
        pygame.draw.line(sheet, c, (0, y), (sheet_w, y))

    title_f = _font(26, True)
    _gradient_text(sheet, "MASTER BEAKON  ·  Tips for Life  ·  round 1",
                   title_f, (sheet_w // 2, 22), _GOLD_PALE, _GOLD_BRIGHT,
                   outline=(40, 24, 10))

    builders = [version_1, version_2, version_3, version_4, version_5]
    label_f = _font(13, True)
    for idx, fn in enumerate(builders):
        col = idx % cols
        row = idx // cols
        x = PAD + col * (CARD_W + PAD)
        y = 40 + PAD + row * (CARD_H + LABEL_H + PAD)
        card, label = fn(CARD_W, CARD_H)
        sheet.blit(card, (x, y))
        # wrap label to two lines if long
        words = label.split(" ")
        line1, line2 = label, ""
        if label_f.size(label)[0] > CARD_W:
            mid = len(words) // 2
            for split in range(mid, len(words)):
                if label_f.size(" ".join(words[:split]))[0] > CARD_W - 10:
                    line1 = " ".join(words[:split])
                    line2 = " ".join(words[split:])
                    break
            else:
                line1, line2 = " ".join(words[:mid]), " ".join(words[mid:])
        ly = y + CARD_H + 6
        for ln in (line1, line2):
            if not ln:
                continue
            img = label_f.render(ln, True, (224, 214, 196))
            sheet.blit(img, img.get_rect(midtop=(x + CARD_W // 2, ly)))
            ly += 14

    out = "/home/user/skybit/docs/profile/master_beakon/round_1.png"
    pygame.image.save(sheet, out)
    print("wrote", out, sheet.get_size())


if __name__ == "__main__":
    build()
