"""Scratch renderer for the `frost-lich` epic-boss concept (round 1).

An ancient FROZEN sorcerer-king: a gaunt skeletal monarch sealed in tattered
glacial robes, spiked crown, radiating cold light. The boss set's anti-titan —
the tallest, narrowest, most rigidly VERTICAL silhouette, built as an obelisk
column so it can't be confused with the bulky leviathan or a chibi clown.
Headless-safe (SDL_VIDEODRIVER=dummy).

Palette is biased hard to necro TEAL-CYAN on purpose: this is one of two undead
entries, and a sibling specter owns spectral pale-GREEN, so HUE is the only
thing that keeps them apart. Cyan glow carries the figure on a bright day sky;
deep frost-navy holds the silhouette at night while the cyan reads as light.

PROP DECISION (proven with the mirrored pillar-fit thumbnail below): the
signature prop is a SOUL-STANDARD — a tall bone pole topped by a caged glowing
soul-orb with a banner cloth hanging from the crossbar. It is the right prop
because it is already a vertical column, and the caged orb gives a strong, single
NODE: when the standard becomes the scrolling pillar (mirrored top+bottom around
the gap) the two orb-cages meet AT the gap, so the rhythm reads as "shaft → cage
NODE → gap → cage NODE → shaft" — a clean obstacle with the lit eye framing the
opening the bird must thread.
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

# ── locked brief palette (BLUE/teal-biased on purpose) ───────────────────────
TEAL      = (120, 230, 224)   # necro teal-cyan — THE focal glow (NOT green)
TEAL_HOT  = (205, 252, 250)   # hottest soul-core, near-white cyan bloom
TEAL_DIM  = (52, 150, 156)    # teal in shadow / eye-socket fill
BONE       = (228, 222, 200)  # bone ivory — skull + shaft + crown spikes
BONE_DK    = (150, 146, 132)  # bone in occlusion
BONE_HI    = (248, 246, 234)  # bone rim light
NAVY       = (28, 40, 72)      # deep frost-navy shadow — robe core + night hold
NAVY_DK    = (16, 24, 46)      # darkest robe occlusion / under-hem
ROBE_MID   = (44, 78, 112)     # robe mid where cyan ambient grazes the cloth
ROBE_HI    = (78, 140, 168)    # icy robe highlight, leans cyan not white

DAY_BG  = ((150, 205, 232), (96, 168, 214))   # bright sky → cyan glow still pops
NIGHT_BG = ((12, 16, 38), (26, 36, 66))        # dark sky → navy holds, cyan glows


def _lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


def _vgrad(surf, rect, top, bot):
    x, y, w, h = rect
    for i in range(h):
        pygame.draw.line(surf, _lerp(top, bot, i / max(1, h - 1)),
                         (x, y + i), (x + w - 1, y + i))


def _glow(surf, cx, cy, r, color, alpha=150, falloff=1.9):
    """Additive radial bloom — the soul-light reads as LIGHT, not flat paint."""
    g = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
    for rr in range(r, 0, -1):
        t = (rr / r) ** falloff
        a = int(alpha * (1 - t))
        pygame.draw.circle(g, (*color, max(0, a)), (r + 1, r + 1), rr)
    surf.blit(g, (cx - r - 1, cy - r - 1), special_flags=pygame.BLEND_ADD)


# ── soul-orb-in-cage primitive (shared by held prop + pillar node) ───────────

def _soul_cage(surf, cx, cy, r):
    """A glowing cyan soul caged in a bone ribcage-claw. This is the rhythmic
    NODE: bright centre framed by curved bone ribs so it survives both as the
    standard's crowning eye and as the pillar-gap focal when mirrored."""
    # outer cold halo first so ribs sit on top of the bloom
    _glow(surf, cx, cy, int(r * 2.4), TEAL, alpha=120, falloff=2.1)
    # the caged soul-orb: layered cyan core, hottest at centre
    pygame.draw.circle(surf, TEAL_DIM, (cx, cy), r)
    pygame.draw.circle(surf, TEAL, (cx, cy), int(r * 0.78))
    pygame.draw.circle(surf, TEAL_HOT, (cx - 1, cy - 1), int(r * 0.42))
    # four curved bone ribs of the cage — claw-like, meeting at top + bottom
    for side in (-1, 1):
        pygame.draw.lines(surf, BONE, False, [
            (cx, cy - r - 3),
            (cx + side * int(r * 0.95), cy - int(r * 0.4)),
            (cx + side * int(r * 1.0), cy + int(r * 0.4)),
            (cx, cy + r + 3),
        ], 3)
        pygame.draw.lines(surf, BONE_HI, False, [
            (cx, cy - r - 3),
            (cx + side * int(r * 0.6), cy - int(r * 0.45)),
        ], 2)
    # cap knobs where the ribs bind, top and bottom — keeps the node symmetric
    for dy in (-r - 3, r + 3):
        pygame.draw.circle(surf, BONE, (cx, cy + dy), 4)
        pygame.draw.circle(surf, BONE_HI, (cx - 1, cy + dy - 1), 2)


# ── the soul-standard prop (tall, vertical, top/bottom mirrorable) ───────────

def _soul_standard(surf, cx, top_y, bot_y, banner=True):
    """A bone pole crowned by a caged soul-orb, banner hanging from a crossbar.
    Built straight + symmetric on purpose so it flips into a clean pillar."""
    cage_r = 16
    cage_cy = top_y + cage_r + 6
    cross_y = cage_cy + cage_r + 14
    # the shaft: a tapering bone column with carved ring segments
    for i in range(top_y + cage_r * 2, bot_y, 6):
        t = (i - top_y) / max(1, bot_y - top_y)
        half = int(_lerp((4, 0, 0), (6, 0, 0), t)[0])  # gentle widen downward
        pygame.draw.line(surf, BONE_DK, (cx - half, i), (cx + half, i), 1)
    pygame.draw.line(surf, BONE, (cx, top_y + cage_r * 2), (cx, bot_y), 6)
    pygame.draw.line(surf, BONE_HI, (cx - 2, top_y + cage_r * 2), (cx - 2, bot_y), 1)
    # carved binding rings down the shaft for vertical rhythm
    for ry in range(cross_y + 20, bot_y, 26):
        pygame.draw.line(surf, BONE_DK, (cx - 5, ry), (cx + 5, ry), 2)
        pygame.draw.line(surf, BONE_HI, (cx - 5, ry - 1), (cx + 5, ry - 1), 1)
    # crossbar holding the banner
    pygame.draw.line(surf, BONE, (cx - 22, cross_y), (cx + 22, cross_y), 4)
    for ex in (-22, 22):
        pygame.draw.circle(surf, BONE, (cx + ex, cross_y), 4)
        pygame.draw.circle(surf, TEAL, (cx + ex, cross_y), 2)  # cold finial light
    if banner:
        # tattered navy banner with a cyan sigil — wind-frozen, ragged hem
        b_top, b_bot, b_w = cross_y + 2, cross_y + 70, 18
        pts = [(cx - b_w, b_top), (cx + b_w, b_top)]
        for k in range(5):
            t = k / 4
            jag = -6 if k % 2 else -2
            pts.append((cx + b_w - int(t * b_w * 2), b_bot + jag))
        pygame.draw.polygon(surf, NAVY, pts)
        pygame.draw.polygon(surf, ROBE_MID, [(cx - b_w, b_top),
                                             (cx - b_w + 5, b_top),
                                             (cx - b_w + 5, b_bot - 6),
                                             (cx - b_w, b_bot - 4)])
        # cold sigil: a downward soul-diamond echoing the caged orb
        sx, sy = cx, (b_top + b_bot) // 2
        pygame.draw.polygon(surf, TEAL_DIM, [(sx, sy - 9), (sx + 7, sy),
                                             (sx, sy + 9), (sx - 7, sy)])
        pygame.draw.polygon(surf, TEAL, [(sx, sy - 5), (sx + 4, sy),
                                         (sx, sy + 5), (sx - 4, sy)], 0)
    # the crowning caged soul drawn last so it sits over everything
    _soul_cage(surf, cx, cage_cy, cage_r)


# ── crown + skull (must read in blackout at 1x) ──────────────────────────────

def _crown(surf, cx, cy, w, s):
    """Spiked iron crown — three tall thorn-spikes + two shoulder spikes, each
    tipped with a cold ember. The spike rhythm is the silhouette read at 1x."""
    base_y = cy
    band_h = int(7 * s)
    half = w // 2
    # crown band
    pygame.draw.rect(surf, NAVY_DK, (cx - half, base_y, w, band_h))
    pygame.draw.rect(surf, ROBE_MID, (cx - half, base_y, w, max(1, band_h - 3)))
    pygame.draw.line(surf, ROBE_HI, (cx - half, base_y + 1), (cx + half, base_y + 1), 1)
    # five upward spikes, tallest at centre — keeps it kingly + asymmetric-free
    offs = [-half + 3, -half // 2, 0, half // 2, half - 3]
    heights = [0.7, 1.05, 1.55, 1.05, 0.7]
    for ox, hf in zip(offs, heights):
        sx = cx + ox
        sh = int(44 * s * hf)
        tip = (sx, base_y - sh)
        pygame.draw.polygon(surf, NAVY_DK, [(sx - int(4 * s), base_y),
                                            (sx + int(4 * s), base_y), tip])
        pygame.draw.polygon(surf, ROBE_MID, [(sx - int(3 * s), base_y),
                                             (sx + int(1 * s), base_y), tip])
        pygame.draw.line(surf, BONE_HI, (sx - int(2 * s), base_y - 2), tip, 1)
        # cold ember at each spike tip — the crown reads as RADIATING cold
        _glow(surf, tip[0], tip[1], int(7 * s), TEAL, alpha=160, falloff=2.0)
        pygame.draw.circle(surf, TEAL_HOT, tip, max(1, int(2 * s)))


def _skull(surf, cx, cy, w, h):
    """Gaunt skull with deep cyan-burning sockets + a bone NOTCH between brows.
    The two glowing sockets are the face read; the notch breaks the dome so the
    head isn't a featureless oval in blackout."""
    half_w, half_h = w // 2, h // 2
    # cranial dome
    pygame.draw.ellipse(surf, BONE_DK, (cx - half_w, cy - half_h, w, h))
    pygame.draw.ellipse(surf, BONE, (cx - half_w + 1, cy - half_h + 1, w - 2, h - 2))
    pygame.draw.ellipse(surf, BONE_HI, (cx - half_w + 2, cy - half_h + 2,
                                        w - 8, h - 10), 1)
    # tapering gaunt jaw — narrow chin so the head leans vertical, not round
    jaw_top = cy + int(half_h * 0.2)
    chin_y = cy + int(half_h * 1.15)
    pygame.draw.polygon(surf, BONE, [
        (cx - int(half_w * 0.78), jaw_top),
        (cx + int(half_w * 0.78), jaw_top),
        (cx + int(half_w * 0.34), chin_y),
        (cx - int(half_w * 0.34), chin_y),
    ])
    pygame.draw.polygon(surf, BONE_DK, [
        (cx - int(half_w * 0.78), jaw_top),
        (cx - int(half_w * 0.34), chin_y),
        (cx - int(half_w * 0.20), chin_y),
        (cx - int(half_w * 0.62), jaw_top),
    ])
    # brow notch — a navy vertical cleft splitting the brow
    pygame.draw.polygon(surf, NAVY_DK, [
        (cx - 2, cy - int(half_h * 0.55)), (cx + 2, cy - int(half_h * 0.55)),
        (cx + 1, cy - int(half_h * 0.05)), (cx - 1, cy - int(half_h * 0.05)),
    ])
    # eye sockets: deep navy hollows holding a burning cyan soul-flame each
    for sx in (-int(half_w * 0.42), int(half_w * 0.42)):
        ex, ey = cx + sx, cy - int(half_h * 0.05)
        pygame.draw.ellipse(surf, NAVY_DK,
                            (ex - 8, ey - 6, 16, 14))
        _glow(surf, ex, ey, 11, TEAL, alpha=175, falloff=1.8)
        pygame.draw.circle(surf, TEAL, (ex, ey + 1), 4)
        pygame.draw.circle(surf, TEAL_HOT, (ex, ey), 2)
    # nasal hollow + clenched teeth line — minimal so it stays clean at 1x
    pygame.draw.polygon(surf, NAVY_DK, [(cx, cy + int(half_h * 0.18)),
                                        (cx - 3, cy + int(half_h * 0.5)),
                                        (cx + 3, cy + int(half_h * 0.5))])
    for tx in range(-7, 8, 4):
        pygame.draw.line(surf, BONE_DK, (cx + tx, jaw_top + 2),
                         (cx + tx, jaw_top + 7), 1)


# ── the full frost-lich figure ───────────────────────────────────────────────

def draw_lich(surf, cx, ground_y, scale=1.0):
    """Assemble the obelisk monarch on a ground line. The whole figure is a tall
    narrow column: robe hem at the ground, robe tapering up to the shoulders,
    skull + crown spiking out the top, soul-standard held to one side as a second
    vertical line echoing the figure."""
    s = scale
    fig_h = int(360 * s)
    top_y = ground_y - fig_h
    # ── the robe column: a clean tapering trapezoid, hem flared at the ground ──
    shoulder_y = top_y + int(fig_h * 0.30)
    hem_y = ground_y
    shoulder_half = int(34 * s)
    hem_half = int(58 * s)
    robe_pts = [
        (cx - shoulder_half, shoulder_y),
        (cx + shoulder_half, shoulder_y),
        (cx + hem_half, hem_y),
        (cx - hem_half, hem_y),
    ]
    # vertical body gradient: cyan-grazed shoulders → navy core → dark hem
    body = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    for yy in range(shoulder_y, hem_y):
        t = (yy - shoulder_y) / max(1, hem_y - shoulder_y)
        col = _lerp(ROBE_MID, NAVY_DK, t ** 0.7)
        # robe half-width at this row (linear taper)
        hw = int(_lerp((shoulder_half, 0, 0), (hem_half, 0, 0), t)[0])
        pygame.draw.line(body, col, (cx - hw, yy), (cx + hw, yy))
    # clip the gradient to the robe polygon
    mask = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), robe_pts)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(body, (0, 0))
    # central cold seam of light down the robe — a single clean cyan line so the
    # robe stays a column instead of crusting into noise at small scale. Kept
    # narrow + low-alpha so it never competes with the caged-orb focal points.
    pygame.draw.line(surf, ROBE_HI, (cx, shoulder_y + 4), (cx, hem_y - 6), 2)
    _glow(surf, cx, shoulder_y + int(fig_h * 0.30), int(22 * s), TEAL,
          alpha=40, falloff=2.6)
    # a few long frost-folds — sparse vertical creases, NOT busy texture
    for fx in (-int(hem_half * 0.55), int(hem_half * 0.55)):
        pygame.draw.line(surf, NAVY_DK,
                         (cx + int(fx * 0.4), shoulder_y + int(20 * s)),
                         (cx + fx, hem_y - 2), 2)
        pygame.draw.line(surf, ROBE_HI,
                         (cx + int(fx * 0.4) - 2, shoulder_y + int(20 * s)),
                         (cx + fx - 2, hem_y - 2), 1)
    # ragged frozen hem — shallow icicle teeth, kept low-frequency
    icic = []
    for k in range(0, 13):
        t = k / 12
        x = cx - hem_half + int(t * hem_half * 2)
        icic.append((x, hem_y + (10 if k % 2 == 0 else 2)))
    icic = [(cx - hem_half, hem_y - 6)] + icic + [(cx + hem_half, hem_y - 6)]
    pygame.draw.polygon(surf, NAVY_DK, icic)
    # ── high collar / mantle framing the skull, sweeping up into spikes ──
    coll = [
        (cx - shoulder_half, shoulder_y + int(8 * s)),
        (cx - int(shoulder_half * 0.5), shoulder_y - int(40 * s)),
        (cx, shoulder_y - int(20 * s)),
        (cx + int(shoulder_half * 0.5), shoulder_y - int(40 * s)),
        (cx + shoulder_half, shoulder_y + int(8 * s)),
    ]
    pygame.draw.polygon(surf, NAVY, coll)
    pygame.draw.lines(surf, ROBE_HI, False, coll[:3], 1)
    # skull seated in the collar
    skull_w, skull_h = int(46 * s), int(54 * s)
    skull_cy = shoulder_y - int(20 * s)
    _skull(surf, cx, skull_cy, skull_w, skull_h)
    # spiked crown above the skull
    _crown(surf, cx, skull_cy - int(skull_h * 0.55), int(skull_w * 1.05), s)
    # ── skeletal arm holding the soul-standard out to the figure's left ──
    hand_x = cx - int(64 * s)
    hand_y = shoulder_y + int(46 * s)
    # bone forearm reaching from the robe to the staff grip
    pygame.draw.line(surf, NAVY, (cx - int(shoulder_half * 0.7), shoulder_y + int(22 * s)),
                     (hand_x, hand_y), int(10 * s))
    pygame.draw.line(surf, BONE, (hand_x, hand_y - int(12 * s)),
                     (hand_x, hand_y + int(10 * s)), int(7 * s))
    for fx in range(-3, 4, 3):  # skeletal fingers gripping the shaft
        pygame.draw.line(surf, BONE, (hand_x + fx, hand_y),
                         (hand_x + fx + 4, hand_y + 6), 2)
    # the standard itself — its own tall vertical line beside the figure
    _soul_standard(surf, hand_x, top_y - int(10 * s), ground_y, banner=True)


# ── pillar-fit proof: the standard mirrored into a top+bottom pillar pair ────

def draw_pillar_fit(surf, cx, top, bot, gap_cy, gap_h):
    """Prove the soul-standard becomes a clean scrolling pillar when mirrored
    around the gap. Top pillar grows DOWN to the gap, bottom grows UP, and the
    caged soul-orb sits as the NODE on each side framing the opening."""
    gap_top = gap_cy - gap_h // 2
    gap_bot = gap_cy + gap_h // 2
    # top pillar: shaft from screen-top down to its cage node at the gap edge
    cage_r = 14
    top_cage_cy = gap_top - cage_r - 4
    pygame.draw.line(surf, BONE, (cx, top), (cx, top_cage_cy - cage_r), 7)
    for ry in range(top + 16, top_cage_cy - cage_r, 24):
        pygame.draw.line(surf, BONE_DK, (cx - 5, ry), (cx + 5, ry), 2)
    _soul_cage(surf, cx, top_cage_cy, cage_r)
    # bottom pillar: mirror — cage node at the gap, shaft running to screen-bot
    bot_cage_cy = gap_bot + cage_r + 4
    pygame.draw.line(surf, BONE, (cx, bot_cage_cy + cage_r), (cx, bot), 7)
    for ry in range(bot_cage_cy + cage_r + 8, bot, 24):
        pygame.draw.line(surf, BONE_DK, (cx - 5, ry), (cx + 5, ry), 2)
    _soul_cage(surf, cx, bot_cage_cy, cage_r)


# ── compose the review sheet ─────────────────────────────────────────────────

def main():
    pygame.init()
    W, H = 760, 720
    sheet = pygame.Surface((W, H))
    sheet.fill((18, 22, 40))
    font = pygame.font.SysFont("dejavusans", 17, bold=True)
    small = pygame.font.SysFont("dejavusans", 13)

    # two boss panels side by side: DAY (left) and NIGHT (right)
    panel_w, panel_h = 300, 470
    ground_y = 430
    for i, (label, bg) in enumerate([("DAY", DAY_BG), ("NIGHT", NIGHT_BG)]):
        px = 30 + i * (panel_w + 24)
        panel = pygame.Surface((panel_w, panel_h))
        _vgrad(panel, (0, 0, panel_w, panel_h), bg[0], bg[1])
        # cold ground line + frost mist so the figure stands ON something
        gcol = _lerp(bg[1], NAVY, 0.5)
        _vgrad(panel, (0, ground_y, panel_w, panel_h - ground_y),
               _lerp(gcol, NAVY, 0.3), NAVY_DK)
        pygame.draw.line(panel, _lerp(TEAL, gcol, 0.6),
                         (0, ground_y), (panel_w, ground_y), 2)
        draw_lich(panel, panel_w // 2 + 22, ground_y, scale=1.0)
        sheet.blit(panel, (px, 56))
        tag = font.render(label, True, TEAL_HOT)
        sheet.blit(tag, (px + 10, 60))

    # pillar-fit thumbnail (far right): mirrored standard → vertical pillar pair
    th_w, th_h = 110, 470
    thx = 30 + 2 * (panel_w + 24)
    if thx + th_w > W:
        th_w = W - thx - 20
    thumb = pygame.Surface((th_w, th_h))
    _vgrad(thumb, (0, 0, th_w, th_h), NIGHT_BG[0], NIGHT_BG[1])
    draw_pillar_fit(thumb, th_w // 2, 0, th_h, th_h // 2, 150)
    sheet.blit(thumb, (thx, 56))

    # titles + captions
    title = font.render("FROST-LICH  —  epic boss  —  round 1", True, BONE_HI)
    sheet.blit(title, (30, 18))
    cap1 = small.render("Skull + spiked crown read in blackout; cyan soul-light, NOT green.",
                        True, (200, 210, 225))
    sheet.blit(cap1, (30, H - 40))
    cap2 = small.render("Right: soul-standard mirrors into a pillar pair, caged orb-NODE at the gap.",
                        True, (200, 210, 225))
    sheet.blit(cap2, (30, H - 22))
    thtag = small.render("PILLAR-FIT", True, TEAL_HOT)
    sheet.blit(thtag, (thx + 4, 60))

    out = os.path.join(os.path.dirname(__file__), "..",
                       "docs", "epic_boss", "frost-lich", "round_1.png")
    out = os.path.abspath(out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("saved", out)


if __name__ == "__main__":
    main()
