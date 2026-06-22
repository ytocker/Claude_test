"""Master Beakon — round 2 exploration sheet (elder-macaw sage).

Round 1 verdict ITERATE. The carry-forward locks V2 (perched on a branch,
leaning on a rolled-scroll cane, deadpan half-lidded eye, speech-parchment
headline) as the body, with V3's heavier brow/beak/squint head transplanted
on — but rendered at NATIVE size (V3's smoothscale-up read soft). This sheet
shows TWO genuinely distinct takes:

  (a) the merged V2+V3 LEAD (the recommendation), and
  (b) a tightened V5 temple-banner where the bird is ANCHORED to the banner.

Punch-list fixes folded in here:
  1. Beard rebuilt as ONE cohesive grey wedge mass (2-3 carved seams + forked
     tip), narrower + shorter, sitting UNDER the beak and stopping at the chest
     so it FRAMES the face. Warm under-beard shadow where it meets the chest.
  2. Wing fold matches the in-game macaw's folded-wing read (one over-fold line,
     gold/teal tip TUCKED inside the silhouette — no stray corner chip).
  3. CTA stack: speech-parchment headline + a tight TIPS-FOR-LIFE label + the
     20-coin chip pulled up into one vertical column.
  4. Harder deadpan: half-lidded eyes, raised-brow asymmetry, downward beak
     tilt. Eyes stay OPEN.
  5. No grey stone daises; any seat prop recolored muted indigo/teal so the
     dusty-scarlet body separates from the obsidian card.

Reuses the store's obsidian/gold helpers + the hud gold palette so the
explorations read as the real ARCADE section.
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
AGED_BLUE     = ( 70, 104, 168)   # faded wing blue (matches in-game BIRD_WING, aged)
AGED_BLUE_D   = ( 44,  70, 120)
AGED_BLUE_HI  = (132, 168, 214)
AGED_TEAL     = ( 96, 168, 132)   # muted green primary tip
AGED_GOLD     = (210, 176,  92)   # faded yellow secondary
BEARD_GREY    = (214, 208, 198)   # grizzled wattle-beard mass (lit)
BEARD_MID     = (186, 178, 166)   # mid tone of the wedge
BEARD_SHADE   = (152, 144, 132)   # carved seam shadow
BEARD_WARM    = (150,  82,  72)   # warm under-beard shadow on the chest
BROW_GREY     = (224, 216, 202)   # bushy white eyebrow
BROW_SHADE    = (176, 168, 154)
SKIN_PALE     = (244, 232, 220)   # bare facial patch
SKIN_SHADE    = (214, 196, 184)
BEAK_GOLD     = (228, 178,  70)
BEAK_HI       = (255, 226, 150)
BEAK_DARK     = (176, 124,  40)
BEAK_TIP_D    = (132,  88,  28)
PERCH_WOOD    = (120,  84,  52)
PERCH_WOOD_D  = ( 84,  56,  34)
PERCH_WOOD_HI = (156, 116,  74)
# muted indigo/teal cushion so the scarlet body separates (was two-reds)
CUSHION       = ( 62,  78, 104)
CUSHION_HI    = ( 96, 116, 146)
CUSHION_D     = ( 40,  52,  74)
PARCH_LIGHT   = (242, 226, 190)
PARCH_MID     = (224, 202, 158)
PARCH_SHADE   = (196, 168, 120)
INK           = ( 78,  58,  44)


def _aaellipse(surf, color, center, rx, ry, width=0):
    cx, cy = center
    rect = pygame.Rect(int(cx - rx), int(cy - ry), int(rx * 2), int(ry * 2))
    pygame.draw.ellipse(surf, color, rect, width)


# ── shared Beakon body parts ─────────────────────────────────────────────────

def _beard_wedge(surf, cx, cy, length=20, width=9):
    """ONE cohesive grizzled beard mass — a single filled grey wedge that hangs
    straight under the beak and tapers to a forked tip, FRAMING the face rather
    than caging the chest. 2 carved seams give it volume; a warm shadow under
    the top edge seats it on the chest. cx,cy = top centre (just under chin)."""
    hw = width / 2.0
    fork = max(2.0, length * 0.22)          # depth of the forked notch
    waist = cy + length * 0.55              # the wedge pinches slightly midway
    # warm contact shadow where the beard meets the chest plumage
    pygame.draw.line(surf, BEARD_WARM, (cx - hw - 1, cy + 1),
                     (cx + hw + 1, cy + 1), 3)
    # filled wedge body: shoulders → slight waist → forked V tip
    body = [
        (cx - hw,        cy),
        (cx - hw * 0.82, waist),
        (cx - hw * 0.30, cy + length - fork),   # left prong base
        (cx,             cy + length),          # centre notch (the fork)
        (cx + hw * 0.30, cy + length - fork),   # right prong base
        (cx + hw * 0.82, waist),
        (cx + hw,        cy),
    ]
    pygame.draw.polygon(surf, BEARD_SHADE, [(p[0] + 1, p[1] + 1) for p in body])
    pygame.draw.polygon(surf, BEARD_MID, body)
    # lit left flank of the wedge for roundness
    pygame.draw.polygon(surf, BEARD_GREY, [
        (cx - hw, cy), (cx - hw * 0.82, waist),
        (cx - hw * 0.30, cy + length - fork), (cx - 1, cy + length - 1),
        (cx - 1, cy),
    ])
    # 2 carved seams down the mass (volume, not strings)
    pygame.draw.line(surf, BEARD_SHADE, (cx - hw * 0.45, cy + 2),
                     (cx - hw * 0.18, waist + 2), 1)
    pygame.draw.line(surf, BEARD_SHADE, (cx + hw * 0.45, cy + 2),
                     (cx + hw * 0.18, waist + 2), 1)
    # the central fork notch, darkened so the two prongs read
    pygame.draw.line(surf, BEARD_SHADE, (cx, cy + length - fork + 1),
                     (cx, cy + length), 1)
    # a couple of grizzled wisps off the prong tips
    pygame.draw.line(surf, BEARD_GREY, (cx - hw * 0.30, cy + length - fork),
                     (cx - hw * 0.30 - 1, cy + length - 1), 1)
    pygame.draw.line(surf, BEARD_GREY, (cx + hw * 0.30, cy + length - fork),
                     (cx + hw * 0.30 + 1, cy + length - 1), 1)


def _brow(surf, x0, y0, x1, y1, thick=4, tuft_up=True):
    """A bushy heavy white eyebrow — the guru's signature. tuft_up raises the
    outer end into a quizzical asymmetric arch."""
    pygame.draw.line(surf, BROW_SHADE, (x0, y0 + 1), (x1, y1 + 1), thick)
    pygame.draw.line(surf, BROW_GREY, (x0, y0), (x1, y1), thick - 1)
    # tufts breaking the line
    if tuft_up:
        pygame.draw.line(surf, BROW_GREY, (x1, y1), (x1 + 3, y1 - 4), 2)
        pygame.draw.line(surf, BROW_GREY, (x1 + 2, y1 - 1), (x1 + 5, y1 - 5), 1)
    pygame.draw.line(surf, BROW_GREY, (x0, y0), (x0 - 2, y0 - 2), 2)


def _deadpan_eye(surf, cx, cy):
    """An OPEN but heavy half-lidded eye — the 'I have seen everything and I am
    unimpressed' read. A thick upper lid clips the top of the pupil; the eye is
    never closed (that reads as asleep)."""
    _aaellipse(surf, SKIN_PALE, (cx, cy), 6, 5)
    _aaellipse(surf, SKIN_SHADE, (cx, cy + 2), 6, 3)
    pygame.draw.line(surf, SKIN_SHADE, (cx - 5, cy - 1), (cx + 5, cy - 1), 1)
    # pupil sits low, with a flat heavy upper lid cutting across it
    pygame.draw.circle(surf, (44, 30, 32), (cx + 1, cy + 1), 3)
    pygame.draw.circle(surf, (16, 10, 14), (cx + 1, cy + 1), 3, 1)
    pygame.draw.circle(surf, (255, 255, 255), (cx, cy), 1)        # life glint
    # heavy lid — a fat dark bar across the upper third of the eye
    pygame.draw.line(surf, (96, 70, 64), (cx - 6, cy - 2), (cx + 6, cy - 3), 3)
    pygame.draw.line(surf, (60, 42, 40), (cx - 6, cy - 3), (cx + 6, cy - 4), 1)
    # a tired bag under the eye
    pygame.draw.line(surf, SKIN_SHADE, (cx - 4, cy + 4), (cx + 4, cy + 4), 1)


def _folded_wing(surf, cx, cy, scale=1.0, flip=False):
    """A folded resting wing matching the in-game macaw's read (game/parrot.py):
    vivid faded-blue panel, ONE clean over-fold line, a short yellow secondary
    stripe and a green primary tip — but the bright tip is TUCKED INSIDE the
    silhouette so it never spikes out as a stray corner chip. cx,cy = shoulder.
    flip mirrors it for the near/far wing."""
    s = scale
    sgn = -1 if flip else 1
    def P(dx, dy):
        return (cx + sgn * dx * s, cy + dy * s)
    # silhouette of the folded wing (teardrop, tail end down toward the body)
    pts = [P(0, -9), P(11, -5), P(15, 4), P(9, 13), P(0, 15), P(-4, 6)]
    pygame.draw.polygon(surf, (0, 0, 0, 70), [(p[0] + 1, p[1] + 2) for p in pts])
    pygame.draw.polygon(surf, AGED_BLUE, pts)
    # darker underside fold (the part nearest the body)
    pygame.draw.polygon(surf, AGED_BLUE_D, [P(0, -9), P(0, 15), P(-4, 6)])
    # the macaw stripe — yellow secondary then green primary tip, both kept
    # well INSIDE the silhouette so the bright colours don't break the edge
    pygame.draw.polygon(surf, AGED_GOLD,
                        [P(7, -2), P(12, 1), P(10, 7), P(5, 4)])
    pygame.draw.polygon(surf, AGED_TEAL,
                        [P(10, 2), P(13, 5), P(9, 11), P(7, 7)])
    # ONE clear over-fold line + a faint highlight along the leading edge
    pygame.draw.line(surf, AGED_BLUE_D, P(1, -6), P(12, 2), 2)
    pygame.draw.line(surf, AGED_BLUE_HI, P(0, -8), P(10, -3), 1)
    # two short covert seams (ruffled elder texture, but disciplined)
    pygame.draw.line(surf, AGED_BLUE_D, P(0, 1), P(9, 5), 1)
    pygame.draw.line(surf, AGED_BLUE_D, P(0, 6), P(7, 10), 1)


def _beakon_head(surf, cx, cy, *, beard_len=20, beak_dip=2, big=False):
    """The aged macaw head at NATIVE size: ruffled crown, asymmetric heavy
    brows, bare patch, deadpan half-lidded eye, hooked beak tilted slightly
    DOWN, and the single-wedge beard hanging beneath. `big` nudges a few radii
    up for the lead's bust-scale head without any smoothscale blur."""
    cr = 14 if big else 13          # crown radius
    # ruffled crown — body-red dome with a broken tuft edge
    _aaellipse(surf, AGED_RED_D, (cx + 1, cy + 1), cr, cr - 1)
    _aaellipse(surf, AGED_RED, (cx, cy), cr, cr - 1)
    _aaellipse(surf, AGED_RED_HI, (cx - 3, cy - 6), 7, 4)
    for ang in range(150, 286, 17):  # crown tufts sticking up/back
        a = math.radians(ang)
        ex, ey = cx + math.cos(a) * (cr - 1), cy + math.sin(a) * (cr - 2)
        pygame.draw.line(surf, AGED_RED_D, (ex, ey),
                         (ex + math.cos(a) * 4, ey + math.sin(a) * 4), 2)
    # bare facial patch
    _aaellipse(surf, SKIN_PALE, (cx + 4, cy + 1), 8, 7)
    _aaellipse(surf, SKIN_SHADE, (cx + 4, cy + 4), 8, 3)
    # asymmetric heavy brows: inner brow low + flat, outer raised (quizzical)
    _brow(surf, cx - 1, cy - 4, cx + 9, cy - 7, thick=5, tuft_up=True)
    _deadpan_eye(surf, cx + 4, cy)
    # hooked beak, tilted slightly DOWN (beak_dip) for the unimpressed read
    d = beak_dip
    beak_pts = [(cx + 10, cy + d), (cx + 21, cy + 4 + d),
                (cx + 16, cy + 9 + d), (cx + 9, cy + 5 + d)]
    pygame.draw.polygon(surf, (0, 0, 0, 60),
                        [(p[0] + 1, p[1] + 1) for p in beak_pts])
    pygame.draw.polygon(surf, BEAK_GOLD, beak_pts)
    pygame.draw.polygon(surf, BEAK_DARK, beak_pts, 1)
    # the down-hooked tip darkened, the upper ridge glossed
    pygame.draw.line(surf, BEAK_TIP_D, (cx + 19, cy + 4 + d), (cx + 16, cy + 9 + d), 2)
    pygame.draw.line(surf, BEAK_HI, (cx + 11, cy + 1 + d), (cx + 17, cy + 3 + d), 1)
    pygame.draw.line(surf, BEAK_DARK, (cx + 9, cy + 5 + d), (cx + 16, cy + 6 + d), 1)
    # the single-wedge beard, hanging just under the lower mandible
    _beard_wedge(surf, cx + 4, cy + 9, length=beard_len, width=9)


def _scroll(surf, cx, cy, w, h):
    """An unfurled parchment with gold-rimmed rollers. Caller draws the text."""
    rect = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    sh = pygame.Surface((w + 8, h + 8), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 90), sh.get_rect(), border_radius=6)
    surf.blit(sh, (rect.x - 2, rect.y + 3))
    body = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        t = y / max(1, h - 1)
        c = lerp_color(PARCH_LIGHT, PARCH_SHADE, (abs(t - 0.5) * 2) ** 1.6 * 0.7)
        pygame.draw.line(body, c, (0, y), (w, y))
    surf.blit(body, rect.topleft)
    pygame.draw.rect(surf, PARCH_SHADE, rect, 1)
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
    """A 20-coin price chip: dark gold-rimmed pill + coin glyph + amount.
    The coin glyph's gold rim matches the HUD coin (shared `_coin_glyph`)."""
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
    return pill


def _tips_label(surf, cx, cy):
    """The tight 'TIPS FOR LIFE' kicker that sits in the CTA stack above the
    coin chip — a small gold-on-obsidian pill so price + label + bird read as
    one vertical column."""
    f = _font(10, True)
    tw = f.size("TIPS FOR LIFE")[0]
    rect = pygame.Rect(cx - tw // 2 - 8, cy - 9, tw + 16, 18)
    pygame.draw.rect(surf, (22, 18, 32), rect, border_radius=9)
    pygame.draw.rect(surf, (*_GOLD_DEEP, 180), rect, 1, border_radius=9)
    _gradient_text(surf, "TIPS FOR LIFE", f, rect.center, _GOLD_PALE,
                   _GOLD_BRIGHT, shadow=False)


def _card(w, h):
    """An obsidian ARCADE card with a gold-rim header band."""
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    rect = pygame.Rect(0, 0, w, h)
    _drop_shadow(surf, rect, 14)
    surf.blit(_vgrad_panel(w, h, 14, OBS_TOP, OBS_BOT), (0, 0))
    pygame.draw.rect(surf, _GOLD_DEEP, rect, 2, border_radius=14)
    pygame.draw.rect(surf, (*_GOLD_BRIGHT, 90), rect.inflate(-3, -3), 1,
                     border_radius=12)
    hh = 30
    head = _vgrad_panel(w - 8, hh, 9, HEADER_TOP, HEADER_BOT)
    surf.blit(head, (4, 5))
    pygame.draw.rect(surf, (*_GOLD_DEEP, 160), (4, 5, w - 8, hh), 1,
                     border_radius=9)
    _gradient_text(surf, "MASTER BEAKON", _font(15, True),
                   (w // 2, 5 + hh // 2), _GOLD_PALE, _GOLD_BRIGHT,
                   outline=(40, 24, 10))
    return surf, hh


# ── option A — the merged V2 + V3 LEAD ───────────────────────────────────────

def option_lead(w, h):
    """V2 body (perched, leaning on the rolled-scroll cane, talon grip) with
    V3's heavier head transplanted at native bust scale. Speech-parchment
    headline up top; a tight TIPS-FOR-LIFE + 20-coin CTA stack pulled up under
    the branch so price + label + bird form one column. Deadpan pushed."""
    surf, hh = _card(w, h)
    cx = w // 2

    # speech-parchment headline delivering a sample cryptic tip
    pr = _scroll(surf, cx, 5 + hh + 24, w - 34, 34)
    f = _font(9, True)
    for i, ln in enumerate(("Do not pay for things", "you do not understand.")):
        img = f.render(ln, True, INK)
        surf.blit(img, img.get_rect(center=(cx, pr.top + 10 + i * 12)))
    # speech tail pointing down at Beakon
    pygame.draw.polygon(surf, PARCH_MID,
                        [(cx - 6, pr.bottom - 2), (cx + 6, pr.bottom - 2),
                         (cx - 2, pr.bottom + 8)])
    pygame.draw.polygon(surf, PARCH_SHADE,
                        [(cx - 6, pr.bottom - 2), (cx + 6, pr.bottom - 2),
                         (cx - 2, pr.bottom + 8)], 1)

    # worn wooden perch branch, raised so the CTA can tuck under it
    by = h - 78
    pygame.draw.line(surf, PERCH_WOOD_D, (18, by + 3), (w - 18, by + 7), 8)
    pygame.draw.line(surf, PERCH_WOOD, (18, by), (w - 18, by + 4), 7)
    pygame.draw.line(surf, PERCH_WOOD_HI, (22, by - 1), (w - 26, by + 2), 2)
    for kx in range(30, w - 28, 24):
        pygame.draw.circle(surf, PERCH_WOOD_D, (kx, by + 1), 2)

    # body perched with a forward lean
    bx, bcy = cx + 3, by - 30
    _aaellipse(surf, AGED_RED_D, (bx + 1, bcy + 2), 23, 26)
    _aaellipse(surf, AGED_RED, (bx, bcy), 23, 25)
    _aaellipse(surf, AGED_RED_HI, (bx - 6, bcy - 10), 13, 7)
    # chest plumage seams
    for sx in (-7, 0, 7):
        pygame.draw.line(surf, AGED_RED_D, (bx + sx, bcy + 4),
                         (bx + sx + sx // 3, bcy + 20), 1)
    # folded wing on the near side — tip tucked inside, one over-fold line
    _folded_wing(surf, bx - 14, bcy - 2, scale=1.05)

    # gnarled talons gripping the branch
    for fx in (bx - 7, bx + 7):
        pygame.draw.line(surf, BEAK_DARK, (fx, bcy + 20), (fx, by - 1), 3)
        for tx in (-3, 0, 3):
            pygame.draw.line(surf, BEAK_DARK, (fx, by - 1), (fx + tx, by + 4), 2)
        pygame.draw.line(surf, BEAK_TIP_D, (fx, by - 1), (fx - 4, by + 4), 2)

    # rolled scroll leaning as a cane on his right, hand resting on the knob
    cane_x = bx + 23
    pygame.draw.line(surf, PARCH_SHADE, (cane_x + 1, bcy - 2), (cane_x + 6, by - 1), 7)
    pygame.draw.line(surf, PARCH_LIGHT, (cane_x, bcy - 2), (cane_x + 5, by - 1), 5)
    pygame.draw.line(surf, PARCH_SHADE, (cane_x, bcy - 2), (cane_x + 3, by - 1), 1)
    pygame.draw.circle(surf, _GOLD_BRIGHT, (cane_x, bcy - 4), 3)
    pygame.draw.circle(surf, _GOLD_DEEP, (cane_x, bcy - 4), 3, 1)
    # a wing-hand laid over the cane knob (the lean)
    _aaellipse(surf, AGED_RED, (bx + 16, bcy - 1), 7, 6)
    pygame.draw.line(surf, AGED_RED_D, (bx + 13, bcy + 1), (bx + 20, bcy - 2), 1)

    # the transplanted heavy head at native bust scale (no smoothscale)
    _beakon_head(surf, bx, bcy - 22, beard_len=18, beak_dip=2, big=True)

    # CTA stack pulled up under the branch: label then coin chip, one column
    _tips_label(surf, cx, by + 26)
    _coin_chip(surf, cx, by + 52, 20)

    return surf, "LEAD  V2 body + V3 head (native): deadpan lean on scroll-cane, framed wedge-beard, CTA stack"


# ── option B — tightened V5 temple-banner (bird ANCHORED to the banner) ───────

def option_banner(w, h):
    """The fortune-teller temple-banner take, tightened: the tall tips-scroll
    hangs from the header and Beakon is perched ON its bottom roller — wing and
    talon TOUCHING the banner so the two read as one object (round 1 floated
    them apart). Same native head, framed wedge-beard, and deadpan."""
    surf, hh = _card(w, h)

    # tall temple-banner scroll, hung centre-left from just under the header
    sx = w // 2 - 26
    sr = _scroll(surf, sx, 5 + hh + 88, 60, 150)
    f = _font(8, True)
    head = f.render("TIPS FOR LIFE", True, INK)
    surf.blit(head, head.get_rect(center=(sr.centerx, sr.top + 9)))
    pygame.draw.line(surf, PARCH_SHADE, (sr.left + 7, sr.top + 16),
                     (sr.right - 7, sr.top + 16), 1)
    sample = ("Fear the wall", "you fear, not", "the one you", "see.  ~ B")
    for i, ln in enumerate(sample):
        img = f.render(ln, True, INK)
        surf.blit(img, img.get_rect(center=(sr.centerx, sr.top + 30 + i * 13)))
    for i in range(3):  # ruled tail lines below the verse
        y = sr.top + 92 + i * 9
        pygame.draw.line(surf, INK, (sr.left + 9, y), (sr.right - 9, y), 1)

    # CTA: TIPS label is the banner head; the coin chip pins to the banner foot
    _coin_chip(surf, sr.centerx, sr.bottom - 14, 20, scale=0.9)

    # Beakon perched ON the banner's bottom roller, to the right and OVERLAPPING
    # it so wing + talon touch the parchment (anchored, not floated)
    bx, bcy = sr.right + 6, sr.bottom - 44
    # far-side folded wing peeking behind the body, tucked tip
    _folded_wing(surf, bx + 12, bcy + 2, scale=0.9, flip=True)
    _aaellipse(surf, AGED_RED_D, (bx + 1, bcy + 2), 21, 24)
    _aaellipse(surf, AGED_RED, (bx, bcy), 21, 23)
    _aaellipse(surf, AGED_RED_HI, (bx - 5, bcy - 9), 12, 6)
    for sx2 in (-6, 1, 8):
        pygame.draw.line(surf, AGED_RED_D, (bx + sx2, bcy + 3),
                         (bx + sx2, bcy + 18), 1)
    # near folded wing draped toward the banner so it overlaps the parchment
    _folded_wing(surf, bx - 13, bcy, scale=1.0)
    # talons gripping the roller — one foot ON the banner roller (the anchor)
    for fx in (bx - 6, bx + 6):
        pygame.draw.line(surf, BEAK_DARK, (fx, bcy + 18), (fx, bcy + 26), 3)
        for tx in (-3, 0, 3):
            pygame.draw.line(surf, BEAK_DARK, (fx, bcy + 26), (fx + tx, bcy + 30), 2)
    # the native head, longer hermit beard for the fortune-teller read
    _beakon_head(surf, bx, bcy - 20, beard_len=22, beak_dip=2, big=False)

    return surf, "BANNER  Beakon perched ON the tips-banner roller (anchored): native head, hermit wedge-beard"


# ── compose sheet ─────────────────────────────────────────────────────────────

def build():
    CARD_W, CARD_H = 264, 360
    PAD = 34
    LABEL_H = 34
    cols = 2
    sheet_w = PAD + cols * (CARD_W + PAD)
    sheet_h = 56 + CARD_H + LABEL_H + PAD + 40
    sheet = pygame.Surface((sheet_w, sheet_h))
    for y in range(sheet_h):
        c = lerp_color((18, 14, 34), (8, 6, 18), y / sheet_h)
        pygame.draw.line(sheet, c, (0, y), (sheet_w, y))

    title_f = _font(26, True)
    _gradient_text(sheet, "MASTER BEAKON  ·  Tips for Life  ·  round 2",
                   title_f, (sheet_w // 2, 24), _GOLD_PALE, _GOLD_BRIGHT,
                   outline=(40, 24, 10))

    builders = [option_lead, option_banner]
    label_f = _font(13, True)
    for idx, fn in enumerate(builders):
        x = PAD + idx * (CARD_W + PAD)
        y = 56
        card, label = fn(CARD_W, CARD_H)
        sheet.blit(card, (x, y))
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
        ly = y + CARD_H + 8
        for ln in (line1, line2):
            if not ln:
                continue
            img = label_f.render(ln, True, (224, 214, 196))
            sheet.blit(img, img.get_rect(midtop=(x + CARD_W // 2, ly)))
            ly += 15

    # 1× silhouette proof strip: the two heads at true inset-disc/pocket scale
    proof_y = sheet_h - 28
    pf = _font(11, True)
    lbl = pf.render("1x head silhouette proof  ▸", True, (200, 190, 170))
    sheet.blit(lbl, lbl.get_rect(midright=(sheet_w // 2 - 60, proof_y)))
    for i, dip in enumerate((2, 2)):
        hx = sheet_w // 2 - 20 + i * 70
        # a true pocket-scale inset disc with the native head dropped in
        _inset_disc(sheet, hx, proof_y, 22)
        big = (i == 0)
        _beakon_head(sheet, hx - 9, proof_y - 6,
                     beard_len=16, beak_dip=dip, big=big)

    out = "/home/user/skybit/docs/profile/master_beakon/round_2.png"
    pygame.image.save(sheet, out)
    print("wrote", out, sheet.get_size())


if __name__ == "__main__":
    build()
