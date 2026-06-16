"""
Yurei — the trailing-hem white vengeful ghost  [COOL GLOW: BLUE-CYAN HITODAMA]

Review-sheet renderer (headless). Draws the ONE locked concept from
batch2/brainstorm_locked15.md: a pale oval face curtained by long straight
black hair, huge sorrowful droop-eyes, a white burial kimono tapering into a
legless translucent wisp tail, two limp dangling hands palms-down at the
wrists, plus a hovering BLUE-CYAN hitodama soul-flame; mirrored into its
hitodama lantern-pole prop->pillar — all at large + 32px scales on one
labelled sheet.

House grammar followed verbatim: chibi proportions, FLAT saturated fills +
hard ink keylines, form via the dark-core -> flat-fill -> top-left rim-sheen
TRIAD, silhouette POP via a 1px outline grown from the alpha mask,
supersampled then smoothscaled down. PINNED PALETTE hexes are used exactly so
the hitodama stays a distinctly BLUE-CYAN cool glow (never traded with
Kitsune's mint-green), and the mournful FACE-under-hair read keeps it clear of
Hollow's faceless hood.
"""
import os
import math

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame

pygame.init()

# ── PINNED PALETTE (verbatim from the locked brief) ──────────────────────────
KIMONO      = (236, 238, 240)   # pale-white kimono base
KIMONO_SH   = (168, 182, 196)   # cool-blue shade (dark-core)
HAIR        = ( 34,  32,  40)   # ink-black hair accent
HITODAMA    = (120, 206, 232)   # BLUE-CYAN hitodama glow (the blue cool glow)
LAVENDER    = (184, 182, 212)   # faint-lavender rim
SOCKET      = ( 70,  78,  96)   # deep-shadow socket
INK         = ( 26,  28,  34)   # keyline
SHEEN       = (248, 250, 252)   # top-left rim-sheen

# derived working tones (kept inside the pinned families)
HAIR_SH     = ( 18,  16,  24)   # deepest hair core
HAIR_HI     = ( 60,  62,  78)   # cool sheen sliver on the hair
HITO_CORE   = (224, 248, 255)   # white-hot soul-flame core
HITO_DEEP   = ( 56, 150, 200)   # bluer deep edge of the flame
SKIN        = (224, 230, 236)   # faintly cooler-than-kimono pallid face
SKIN_SH     = (176, 190, 206)   # face dark-core hollow
POLE_WOOD   = (150, 140, 132)   # weathered wood lantern-pole (cool-grey neutral)
POLE_SH     = (104,  98,  96)
POLE_HI     = (196, 190, 184)
PAPER       = (228, 232, 236)   # paper lantern-frame panel

SS = 4   # supersample factor


def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


def grow_outline(src, color=INK, grow=1):
    """1px (post-downscale) ink keyline grown from the alpha mask, the way the
    house silhouette-POP works. Done at supersample scale then carried down by
    the smoothscale, so we grow by `grow*SS` here."""
    g = grow * SS
    mask = pygame.mask.from_surface(src)
    out_surf = mask.to_surface(setcolor=(*color, 255), unsetcolor=(0, 0, 0, 0))
    w, h = src.get_size()
    canvas = pygame.Surface((w + 2 * g, h + 2 * g), pygame.SRCALPHA)
    for dx in range(-g, g + 1):
        for dy in range(-g, g + 1):
            if dx * dx + dy * dy <= g * g:
                canvas.blit(out_surf, (g + dx, g + dy))
    canvas.blit(src, (g, g))
    return canvas, g


def radial_glow(radius, color, alpha_center=200, falloff=2.0):
    size = radius * 2 + 2
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    c = radius + 1
    for r in range(radius, 0, -1):
        t = (r / radius) ** falloff
        a = int(alpha_center * (1 - t))
        pygame.draw.circle(s, (*color, max(0, min(255, a))), (c, c), r)
    return s


def hitodama(surf, cx, cy, r, with_glow=True):
    """The signature BLUE-CYAN soul-flame: a teardrop flame-bulb with a wispy
    tail flicking up, triad-lit (deep-blue core / cyan fill / white-hot
    top-left sheen) and wrapped in an additive blue-cyan halo. This is the
    single most load-bearing colour cue separating Yurei from Kitsune."""
    U = SS
    if with_glow:
        glow = radial_glow(int(r + 11 * U), HITODAMA, alpha_center=185, falloff=2.1)
        surf.blit(glow, (cx - glow.get_width() // 2, cy - glow.get_height() // 2),
                  special_flags=pygame.BLEND_ADD)
    # teardrop body: round bulb with a flickering tail rising off the top
    body = [
        (cx, cy - int(r * 2.0)),                       # tail tip (rises up)
        (cx - int(r * 0.42), cy - int(r * 0.9)),
        (cx - r, cy - int(r * 0.1)),
        (cx - int(r * 0.78), cy + int(r * 0.78)),
        (cx, cy + r),
        (cx + int(r * 0.78), cy + int(r * 0.78)),
        (cx + r, cy - int(r * 0.1)),
        (cx + int(r * 0.42), cy - int(r * 0.9)),
    ]
    deep = [(x + int(1.5 * U), y + int(1.5 * U)) for (x, y) in body]
    pygame.draw.polygon(surf, HITO_DEEP, deep)
    pygame.draw.polygon(surf, HITODAMA, body)
    # top-left white-hot rim-sheen + inner core spark
    pygame.draw.polygon(surf, HITO_CORE, [
        (cx, cy - int(r * 1.7)),
        (cx - int(r * 0.36), cy - int(r * 0.7)),
        (cx - int(r * 0.6), cy + int(r * 0.1)),
        (cx - int(r * 0.18), cy - int(r * 0.1)),
    ])
    pygame.draw.circle(surf, HITO_CORE, (cx - r // 4, cy - r // 6), int(r * 0.32))
    pygame.draw.circle(surf, SHEEN, (cx - r // 3, cy - r // 4), int(r * 0.14))


# ─────────────────────────────────────────────────────────────────────────────
#  THE CREATURE — built large (supersampled), then outlined + downscaled.
#  Tall, narrow, top-weighted (face+hair) tapering to a legless wisp.
#  Origin frame ~ 150w x 210h (creature units), scaled by SS.
# ─────────────────────────────────────────────────────────────────────────────

def build_yurei(target_h=200):
    """Return a SRCALPHA surface of Yurei at roughly `target_h` px tall (the
    hitodama glow extends a little beyond the body)."""
    U = SS
    W, H = 156 * U, 214 * U
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    cx = W // 2

    def P(pts):
        return [(cx + int(x * U), int(y * U)) for (x, y) in pts]

    # ---- KIMONO BODY + LEGLESS WISP TAIL (drawn first, behind hair/arms) ----
    # White burial kimono: shoulders down to a soft bell, then dissolving into
    # a curling translucent wisp — NO feet, drifts. Mournful narrow taper.
    kimono = P([
        (-30, 70), (-36, 96), (-32, 124), (-40, 150),
        (-28, 168), (-34, 184), (-18, 178),                # wisp lobe (left)
        (-22, 196), (-8, 188), (0, 200),                   # central wisp tongue
        (8, 188), (22, 196), (18, 178),
        (34, 184), (28, 168), (40, 150),                   # wisp lobe (right)
        (32, 124), (36, 96), (30, 70),
    ])
    kimono_shade = [(x + 3 * U, y + 3 * U) for (x, y) in kimono]
    pygame.draw.polygon(s, KIMONO_SH, kimono_shade)
    pygame.draw.polygon(s, KIMONO, kimono)

    # left-over-right burial collar fold (the funerary tell) as a dark-core seam
    pygame.draw.polygon(s, KIMONO_SH, P([
        (-16, 72), (0, 96), (16, 72), (10, 70), (0, 86), (-10, 70),
    ]))
    pygame.draw.polygon(s, lerp(KIMONO_SH, SOCKET, 0.35), P([
        (-12, 74), (0, 94), (4, 90), (-6, 74),
    ]))

    # dark-core valley down the kimono centre (flat triad panel, deepening
    # into the translucent wisp so the bottom reads as fading-out)
    pygame.draw.polygon(s, KIMONO_SH, P([
        (-9, 96), (-15, 140), (-9, 176), (0, 190),
        (9, 176), (15, 140), (9, 96),
    ]))
    # the wisp tail reads translucent: a paler lavender-blue tint pooling low
    wisp_tint = pygame.Surface(s.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(wisp_tint, (*LAVENDER, 120), P([
        (-22, 150), (-30, 170), (-16, 182), (-20, 194),
        (0, 196), (20, 194), (16, 182), (30, 170), (22, 150),
    ]))
    s.blit(wisp_tint, (0, 0))

    # top-left rim-sheen sliver down the kimono's left edge
    pygame.draw.polygon(s, SHEEN, P([
        (-30, 72), (-35, 96), (-31, 124), (-39, 150),
        (-32, 153), (-26, 124), (-29, 96), (-24, 73),
    ]))

    # ---- LIMP DANGLING ARMS + HANDS (palms-down at the wrists) --------------
    # Long flowing kimono sleeves hang from the shoulders; pallid hands droop
    # limp from the wrists, palms-down — the canonical yurei gesture.
    for sx in (-1, 1):
        sleeve = P([
            (sx * 28, 74), (sx * 44, 92), (sx * 46, 124),
            (sx * 38, 146), (sx * 26, 140), (sx * 22, 112), (sx * 22, 84),
        ])
        pygame.draw.polygon(s, KIMONO_SH, [(x + 2 * U, y + 2 * U) for (x, y) in sleeve])
        pygame.draw.polygon(s, KIMONO, sleeve)
        # sleeve-mouth dark-core hollow (where the hand emerges)
        pygame.draw.polygon(s, KIMONO_SH, P([
            (sx * 40, 138), (sx * 46, 124), (sx * 38, 132), (sx * 32, 138),
        ]))
        if sx == -1:
            pygame.draw.polygon(s, SHEEN, P([
                (sx * 28, 76), (sx * 42, 92), (sx * 40, 102),
                (sx * 30, 90), (sx * 26, 80),
            ]))
        # limp hand drooping palm-down from the wrist
        hand = P([
            (sx * 40, 140), (sx * 48, 146), (sx * 50, 160),
            (sx * 44, 168), (sx * 36, 164), (sx * 34, 150),
        ])
        pygame.draw.polygon(s, SKIN_SH, [(x + 2 * U, y + 2 * U) for (x, y) in hand])
        pygame.draw.polygon(s, SKIN, hand)
        # slack drooping fingers
        for fi in range(3):
            fx = sx * (36 + fi * 5)
            pygame.draw.polygon(s, SKIN, P([
                (fx, 162), (fx + sx * 4, 162), (fx + sx * 2, 174 - fi * 2),
            ]))
            pygame.draw.polygon(s, SKIN_SH, P([
                (fx + sx * 2, 162), (fx + sx * 4, 162), (fx + sx * 2, 174 - fi * 2),
            ]))

    # ---- PALE FACE (drawn before hair-curtains so hair frames it) -----------
    # Small oval pallid face, faintly cooler than the kimono.
    face = P([
        (-19, 14), (-21, 30), (-16, 46), (-8, 56), (0, 58),
        (8, 56), (16, 46), (21, 30), (19, 14), (12, 6), (0, 4), (-12, 6),
    ])
    pygame.draw.polygon(s, SKIN_SH, [(x + 2 * U, y + 3 * U) for (x, y) in face])
    pygame.draw.polygon(s, SKIN, face)
    # top-left rim-sheen on the brow
    pygame.draw.polygon(s, SHEEN, P([
        (-18, 14), (-19, 28), (-12, 16), (-2, 8), (-10, 8),
    ]))
    # cheek dark-core hollows (gaunt, sorrowful)
    for sx in (-1, 1):
        pygame.draw.polygon(s, SKIN_SH, P([
            (sx * 16, 36), (sx * 18, 44), (sx * 10, 52), (sx * 9, 42),
        ]))

    # huge sorrowful droop-eyes: deep-shadow sockets sloping down at the outer
    # corners, with a faint blue-cyan ghost-light catch
    for sx in (-1, 1):
        eye_cx = cx + int(sx * 9 * U)
        eye_cy = int(34 * U)
        pygame.draw.polygon(s, SOCKET, [
            (eye_cx - int(sx * 7 * U), eye_cy - int(2 * U)),
            (eye_cx + int(sx * 5 * U), eye_cy - int(4 * U)),
            (eye_cx + int(sx * 6 * U), eye_cy + int(6 * U)),   # droops down/out
            (eye_cx - int(sx * 4 * U), eye_cy + int(7 * U)),
        ])
        # faint cool catch-light low in the socket (wistful, not glaring)
        pygame.draw.circle(s, lerp(HITODAMA, SOCKET, 0.4),
                           (eye_cx, eye_cy + int(2 * U)), int(2.4 * U))
        pygame.draw.circle(s, HITO_CORE,
                           (eye_cx - U, eye_cy + U), max(1, int(1.0 * U)))
    # tiny nose shadow + small downturned mournful mouth
    pygame.draw.polygon(s, SKIN_SH, P([(0, 42), (-3, 48), (3, 48)]))
    pygame.draw.polygon(s, SOCKET, P([
        (-6, 51), (0, 53), (6, 51), (4, 54), (0, 55), (-4, 54),
    ]))

    # ---- LONG STRAIGHT BLACK HAIR-CURTAINS (hard triad panels) --------------
    # Centre-parted, draping straight down BOTH sides past the shoulders,
    # framing (not hiding) the face — the visible-mournful-face read that keeps
    # Yurei distinct from Hollow's faceless hood.
    # crown cap + part
    pygame.draw.polygon(s, HAIR, P([
        (-20, 16), (-22, 2), (-12, -8), (0, -11), (12, -8),
        (22, 2), (20, 16), (10, 6), (0, 4), (-10, 6),
    ]))
    for sx in (-1, 1):
        curtain = P([
            (sx * 20, 8), (sx * 28, 26), (sx * 30, 64),
            (sx * 26, 104), (sx * 22, 134), (sx * 14, 150),
            (sx * 10, 132), (sx * 12, 96), (sx * 14, 56),
            (sx * 13, 30), (sx * 8, 16),
        ])
        # hair dark-core bed
        pygame.draw.polygon(s, HAIR_SH, [(x + 2 * U, y + 2 * U) for (x, y) in curtain])
        pygame.draw.polygon(s, HAIR, curtain)
        # a few straight strand-seams (flat triad grooves, not soft form)
        for k in range(3):
            ox = sx * (14 + k * 5)
            pygame.draw.line(s, HAIR_SH,
                             (cx + int(ox * U), int((20 + k * 4) * U)),
                             (cx + int((ox + sx * 3) * U), int((132 - k * 6) * U)),
                             max(1, int(1.4 * U)))
        # cool top-left sheen sliver on the outer left curtain only
        if sx == -1:
            pygame.draw.polygon(s, HAIR_HI, P([
                (sx * 20, 10), (sx * 27, 28), (sx * 28, 60),
                (sx * 24, 60), (sx * 23, 28), (sx * 17, 12),
            ]))
    # face-framing inner wisps falling over the temples
    for sx in (-1, 1):
        pygame.draw.polygon(s, HAIR, P([
            (sx * 8, 8), (sx * 16, 14), (sx * 14, 40),
            (sx * 9, 58), (sx * 6, 44), (sx * 5, 18),
        ]))

    # ---- HOVERING HITODAMA SOUL-FLAME ---------------------------------------
    # A single blue-cyan soul-flame drifting off the shoulder — the cool focal.
    hitodama(s, cx + int(46 * U), int(70 * U), int(9 * U))
    # a faint secondary ember lower down, near the wisp, to sell the drift
    hitodama(s, cx - int(48 * U), int(120 * U), int(5 * U))

    # ---- ink keyline grown from the alpha mask + downscale ------------------
    outlined, _ = grow_outline(s, INK, grow=1)
    ow, oh = outlined.get_size()
    scale = target_h / oh
    return pygame.transform.smoothscale(
        outlined, (max(1, int(ow * scale)), max(1, int(oh * scale))))


# ─────────────────────────────────────────────────────────────────────────────
#  THE PROP -> PILLAR — hitodama soul-flame LANTERN-POLE.
#  Slim banded wooden pole = repeatable body; a hovering blue-white hitodama
#  soul-flame in a paper frame = gap-edge cap drifting at the gap.
# ─────────────────────────────────────────────────────────────────────────────

def _pole_body(s, cx, P, top_y, bot_y):
    """Repeatable slim banded pole shaft (shared by prop + pillar)."""
    U = SS
    pw = 7
    shaft = [(cx - pw * U, int(top_y * U)), (cx + pw * U, int(top_y * U)),
             (cx + pw * U, int(bot_y * U)), (cx - pw * U, int(bot_y * U))]
    pygame.draw.polygon(s, POLE_SH, [(x + 2 * U, y) for (x, y) in shaft])
    pygame.draw.polygon(s, POLE_WOOD, shaft)
    # top-left sheen column
    pygame.draw.rect(s, POLE_HI,
                     (cx - pw * U, int(top_y * U), int(2.2 * U),
                      int((bot_y - top_y) * U)))
    # slim banding (the repeatable banding for the pillar body)
    for by in range(int(top_y) + 10, int(bot_y), 20):
        pygame.draw.rect(s, POLE_SH,
                         (cx - pw * U, by * U, pw * 2 * U, int(3 * U)))
        pygame.draw.rect(s, POLE_HI,
                         (cx - pw * U, by * U, pw * 2 * U, int(1.0 * U)))


def _lantern_frame(s, cx, ocy, P, glow_dir=1):
    """Paper lantern-frame box holding a blue-cyan hitodama at its heart.
    `glow_dir` flips the flame tail up (+1, prop) or lets the cap hang the
    flame into the gap (-1, pillar) — same construction, mirrored seat."""
    U = SS
    # paper frame: a soft-cornered box with thin wood ribs, glowing from within
    fw, fh = 18, 22
    box = [(cx - fw * U, int((ocy - fh) * U)), (cx + fw * U, int((ocy - fh) * U)),
           (cx + fw * U, int((ocy + fh) * U)), (cx - fw * U, int((ocy + fh) * U))]
    pygame.draw.polygon(s, POLE_SH, [(x + 2 * U, y + 2 * U) for (x, y) in box])
    # paper panels tinted by the soul-flame within
    pygame.draw.polygon(s, lerp(PAPER, HITODAMA, 0.35), box)
    pygame.draw.polygon(s, lerp(PAPER, HITODAMA, 0.12),
                        [(cx - fw * U, int((ocy - fh) * U)),
                         (cx - int(fw * 0.2) * U, int((ocy - fh) * U)),
                         (cx - int(fw * 0.2) * U, int((ocy + fh) * U)),
                         (cx - fw * U, int((ocy + fh) * U))])
    # wood top & bottom caps of the lantern frame
    for yy in (ocy - fh, ocy + fh):
        pygame.draw.rect(s, POLE_WOOD,
                         (cx - int((fw + 3) * U), int(yy * U) - int(2 * U),
                          int((fw + 3) * 2 * U), int(5 * U)))
        pygame.draw.rect(s, POLE_HI,
                         (cx - int((fw + 3) * U), int(yy * U) - int(2 * U),
                          int((fw + 3) * 2 * U), int(1.4 * U)))
    # vertical paper ribs
    for rx in (-9, 0, 9):
        pygame.draw.line(s, POLE_SH,
                         (cx + int(rx * U), int((ocy - fh + 2) * U)),
                         (cx + int(rx * U), int((ocy + fh - 2) * U)),
                         max(1, int(1.2 * U)))
    # the BLUE-CYAN hitodama burning inside the frame
    flame = pygame.Surface(s.get_size(), pygame.SRCALPHA)
    hr = int(8 * U)
    if glow_dir > 0:
        hitodama(flame, cx, int(ocy * U) + int(2 * U), hr)
    else:
        # mirror: flame tail flicks downward into the gap
        tmp = pygame.Surface(s.get_size(), pygame.SRCALPHA)
        hitodama(tmp, cx, flame.get_height() // 2, hr)
        tmp = pygame.transform.flip(tmp, False, True)
        oy = int(ocy * U) - flame.get_height() // 2 - int(2 * U)
        flame.blit(tmp, (0, oy))
    s.blit(flame, (0, 0))


def build_pole(target_h=210):
    """The prop: slim banded wooden lantern-pole topped by a paper-framed
    blue-cyan hitodama soul-flame drifting at the crown."""
    U = SS
    W, H = 64 * U, 232 * U
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    cx = W // 2

    def P(pts):
        return [(cx + int(x * U), int(y * U)) for (x, y) in pts]

    _pole_body(s, cx, P, top_y=56, bot_y=226)
    _lantern_frame(s, cx, ocy=34, P=P, glow_dir=1)

    outlined, _ = grow_outline(s, INK, grow=1)
    ow, oh = outlined.get_size()
    scale = target_h / oh
    return pygame.transform.smoothscale(
        outlined, (max(1, int(ow * scale)), max(1, int(oh * scale))))


def build_pillar(target_h=210):
    """Mirror the pole prop into a clean repeatable PILLAR: the banded pole
    repeats as the body, the paper-framed hitodama lantern is the detachable
    gap-edge cap drifting at the gap. Shown as a top cap so the gap is at the
    bottom (the way Big Reapy's bone-bident mirrors)."""
    U = SS
    W, H = 64 * U, 232 * U
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    cx = W // 2

    def P(pts):
        return [(cx + int(x * U), int(y * U)) for (x, y) in pts]

    # repeatable pole body filling from the top down to the gap line
    _pole_body(s, cx, P, top_y=0, bot_y=170)
    # detachable gap-edge cap at the BOTTOM: paper lantern with the hitodama
    # hanging its flame down into the gap
    _lantern_frame(s, cx, ocy=196, P=P, glow_dir=-1)

    outlined, _ = grow_outline(s, INK, grow=1)
    ow, oh = outlined.get_size()
    scale = target_h / oh
    return pygame.transform.smoothscale(
        outlined, (max(1, int(ow * scale)), max(1, int(oh * scale))))


# ─────────────────────────────────────────────────────────────────────────────
#  SHEET COMPOSITION
# ─────────────────────────────────────────────────────────────────────────────

def main():
    SHEET_W, SHEET_H = 760, 560
    sheet = pygame.Surface((SHEET_W, SHEET_H))
    # neutral-cool review backdrop so the pale-white + blue-cyan read honestly
    for y in range(SHEET_H):
        t = y / SHEET_H
        sheet.fill(lerp((38, 42, 54), (20, 24, 34), t), (0, y, SHEET_W, 1))

    font = pygame.font.SysFont("dejavusans", 18, bold=True)
    small = pygame.font.SysFont("dejavusans", 13)
    tiny = pygame.font.SysFont("dejavusans", 11)

    def label(txt, x, y, f=small, col=(230, 236, 244)):
        sheet.blit(f.render(txt, True, (0, 0, 0)), (x + 1, y + 1))
        sheet.blit(f.render(txt, True, col), (x, y))

    label("YUREI — trailing-hem white vengeful ghost  [COOL GLOW: BLUE-CYAN HITODAMA]",
          16, 12, font)
    label("pale-white kimono + ink-black hair + blue-cyan hitodama  ·  mournful FACE under hair-curtains · limp dangling hands · legless wisp tail",
          16, 36, tiny, (176, 196, 216))

    # large creature
    big = build_yurei(target_h=320)
    bx = 36
    by = 70
    sheet.blit(big, (bx, by))
    label("creature (large)", bx + big.get_width() // 2 - 42, by + big.get_height() + 4)

    # 32px creature: 3x nearest-neighbor zoom + true 32px swatch side by side
    small_creat = build_yurei(target_h=32)
    sy = by + big.get_height() + 26
    zoom = pygame.transform.scale(small_creat,
                                  (small_creat.get_width() * 3,
                                   small_creat.get_height() * 3))
    zx = bx + 8
    sheet.blit(zoom, (zx, sy))
    sheet.blit(small_creat, (zx + zoom.get_width() + 16, sy + zoom.get_height() - 32))
    label("32px read (3x + actual)", zx, sy + zoom.get_height() + 4, tiny)

    # large pole prop
    pole = build_pole(target_h=360)
    stx = 332
    sty = 64
    sheet.blit(pole, (stx, sty))
    label("hitodama lantern-pole (prop)", stx - 18, sty + pole.get_height() + 2, tiny)

    # mirrored pillar
    pill = build_pillar(target_h=360)
    px = 442
    sheet.blit(pill, (px, sty))
    label("-> PILLAR mirror", px - 2, sty + pill.get_height() + 2, tiny)
    label("(repeatable pole +", px - 2, sty + pill.get_height() + 16, tiny,
          (160, 184, 210))
    label(" hitodama gap cap)", px - 2, sty + pill.get_height() + 28, tiny,
          (160, 184, 210))

    # 32px pole + pillar reads
    pole32 = build_pole(target_h=32)
    pill32 = build_pillar(target_h=32)
    z2 = pygame.transform.scale(pole32,
                                (pole32.get_width() * 3, pole32.get_height() * 3))
    z3 = pygame.transform.scale(pill32,
                                (pill32.get_width() * 3, pill32.get_height() * 3))
    zy = 70
    zx2 = 562
    sheet.blit(z2, (zx2, zy))
    sheet.blit(z3, (zx2 + z2.get_width() + 24, zy))
    sheet.blit(pole32, (zx2 + 6, zy + z2.get_height() + 8))
    sheet.blit(pill32, (zx2 + z2.get_width() + 30, zy + z2.get_height() + 8))
    label("32px pole / pillar", zx2, zy + z2.get_height() + 34, tiny)

    # palette swatch strip
    swatches = [
        ("kimono", KIMONO), ("kimono-sh", KIMONO_SH), ("hair", HAIR),
        ("hitodama", HITODAMA), ("lavender", LAVENDER), ("socket", SOCKET),
        ("ink", INK), ("sheen", SHEEN),
    ]
    swx, swy = 562, 360
    for i, (nm, col) in enumerate(swatches):
        ry = swy + i * 22
        pygame.draw.rect(sheet, col, (swx, ry, 26, 18))
        pygame.draw.rect(sheet, (10, 10, 14), (swx, ry, 26, 18), 1)
        label(nm, swx + 32, ry + 3, tiny)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(sheet, out)
    print("saved", out)


if __name__ == "__main__":
    main()
