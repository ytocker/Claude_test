"""launch-perch main-menu concept — geometry-fix re-render (day phase only).

Standalone. Touches no game/*.py file. The whole composition is re-derived
around the ONE fixed anchor the live menu cannot move: Pip is the real
`world.bird` entity, blitted CENTERED on (BIRD_X=90, H*0.42=268.8), and a
fresh Bird respawns there the instant START is tapped. Everything timber
(perch deck, START slab, hanging signposts) is derived from that point.
"""
import os
import math
import random

os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "dummy"

import sys
_ROOT = "/home/user/skybit"
sys.path.insert(0, _ROOT)

import pygame
pygame.init()

from game.config import W, H, BIRD_X, GROUND_Y
from game import biome as _biome
from game import foreground
from game import intro as _intro
from game import hud as _hud
from game.scenes import App, STATE_MENU
from game.world import World

VARIANT = os.environ.get("VARIANT", "B")
POSE = os.environ.get("POSE", "rest")
BEST_SCORE = int(os.environ.get("BEST", "47"))

# Rotated silhouettes of the three frozen boards, kept so the bell's hang rope
# can be subtracted out of them before it lands: the line has to leave the
# SETTINGS tail without repainting one pixel of the approved artwork.
PLANK_SPRITES = []
PHASE = float(os.environ.get("PHASE", "0.0"))
OUT = os.environ.get("OUT") or os.path.join(
    _ROOT, "docs", "main-menu", "launch-perch", f"start_{VARIANT}.png")

# ── The immovable anchor ────────────────────────────────────────────────────
PIP_CX = BIRD_X            # 90
PIP_CY = H * 0.42          # 268.8
PIP_FEET = 290             # opaque bottom of the 68x64 macaw sprite at this centre
BEAM_TOP = 291             # top face of the perch beam = 1 px under his feet
BEAM_H = 22
BEAM_BOT = BEAM_TOP + BEAM_H
BEAM_RIGHT = 182          # runs past the START slab's left edge, so the slab
                          # (drawn later) swallows the end = the visual join

# ── Timber / iron palette ───────────────────────────────────────────────────
T_HI     = (188, 138,  78)
T_LIT    = (150,  99,  53)
T_MID    = (112,  70,  38)
T_DARK   = ( 68,  40,  22)
T_SHADOW = ( 38,  22,  12)
# Softer edge tone for lips/outlines/grain. T_SHADOW is near-black and, at the
# 2px widths these were drawn at, made every board look ink-outlined.
T_EDGE   = ( 60,  36,  20)
IRON     = ( 62,  56,  60)
IRON_HI  = (132, 128, 134)
ROPE     = (198, 166, 106)
ROPE_D   = (128,  96,  52)

# ── Shadow system ───────────────────────────────────────────────────────────
# Every element used to invent its own hand-tuned shadow, which is why they
# read as pasted-on: several sat at 43-47% opacity (Material's darkest umbra
# is 20%) and all of them were near-black against a bright cyan sky.
#
# SH_TINT is derived from the day sky (~(41,116,142)) rather than being
# neutral black, so a shadow reads as "less light reached here" instead of as
# a grey shape laid over the artwork.
SH_TINT = (14, 38, 52)

# Three elevation tiers, reused everywhere. (contact_a, ambient_a, dy, spread)
# Budget follows Material: umbra .20 (=51), penumbra .14, ambient .12 (=31).
SH_TIERS = {
    "contact": (44, 24, 1, 3),   # things resting on the plank
    "low":     (40, 22, 2, 4),   # the hanging sign planks
    "raised":  (50, 28, 2, 5),   # the START slab — the one primary control
}


def soft_shadow(surf, shape, tier, mask=None):
    """Material-style stacked pair: a tight contact shadow plus a wider
    ambient one that actually falls off, instead of a single hard-edged slab.

    `shape` is a Rect; `mask` optionally supplies a silhouette to shadow
    (for rotated boards) instead of a rounded rectangle.
    """
    contact_a, ambient_a, dy, spread = SH_TIERS[tier]
    pad = spread + 2
    w, h = shape.width + pad * 2, shape.height + pad * 2
    layer = pygame.Surface((w, h), pygame.SRCALPHA)

    if mask is not None:
        # Silhouette shadow: stamp the mask a few times, fading outward, so
        # the edge dissolves rather than ending abruptly.
        for k in range(spread, 0, -1):
            a = int(ambient_a * (k / spread) * 0.5)
            tinted = mask.copy()
            tinted.fill((*SH_TINT, a), special_flags=pygame.BLEND_RGBA_MULT)
            for ox, oy in ((-k, 0), (k, 0), (0, -k), (0, k)):
                layer.blit(tinted, (pad + ox, pad + oy + dy))
        tinted = mask.copy()
        tinted.fill((*SH_TINT, contact_a), special_flags=pygame.BLEND_RGBA_MULT)
        layer.blit(tinted, (pad, pad + dy))
    else:
        # Ambient: concentric rounded rects fading out from the shape edge.
        for k in range(spread, 0, -1):
            a = int(ambient_a * (1.0 - (k - 1) / max(1, spread)))
            r = pygame.Rect(pad - k, pad - k + dy,
                            shape.width + k * 2, shape.height + k * 2)
            pygame.draw.rect(layer, (*SH_TINT, a), r,
                             border_radius=8 + k)
        pygame.draw.rect(layer, (*SH_TINT, contact_a),
                         pygame.Rect(pad, pad + dy, shape.width, shape.height),
                         border_radius=8)

    surf.blit(layer, (shape.x - pad, shape.y - pad))


def under_shade(surf, rect, height=4, alpha=46, radius=0):
    """Under-edge self-shading: the object's own underside catching less
    light. This is what actually sells 3D form for something floating against
    open sky, where a projected cast shadow is physically impossible.
    """
    layer = pygame.Surface((rect.width, height), pygame.SRCALPHA)
    for y in range(height):
        a = int(alpha * (1.0 - y / max(1, height)))
        pygame.draw.line(layer, (*SH_TINT, a), (0, y), (rect.width, y))
    surf.blit(layer, (rect.x, rect.bottom - height))

GOLD_BRIGHT = _hud._GOLD_BRIGHT
GOLD_MID    = _hud._GOLD_MID
GOLD_DEEP   = _hud._GOLD_DEEP
GOLD_PALE   = _hud._GOLD_PALE
SCARLET_TOP = _hud._SCARLET_TOP
SCARLET_BOT = _hud._SCARLET_BOT


def _mix(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def _grad_fill(surf, rect, top, bot):
    x, y, w, h = rect
    for i in range(h):
        t = i / max(1, h - 1)
        c = (int(top[0] + (bot[0] - top[0]) * t),
             int(top[1] + (bot[1] - top[1]) * t),
             int(top[2] + (bot[2] - top[2]) * t))
        pygame.draw.line(surf, c, (x, y + i), (x + w - 1, y + i))


def _board_points(w, h, chamfer=5, notch=5):
    """Chamfered corners + a shallow V bitten out of each end face — the
    rustic hand-cut sign silhouette, not a plain rectangle."""
    return [
        (chamfer, 0), (w - chamfer, 0), (w, chamfer),
        (w - notch, h * 0.5), (w, h - chamfer), (w - chamfer, h),
        (chamfer, h), (0, h - chamfer), (notch, h * 0.5), (0, chamfer),
    ]


def timber_board(w, h, seed=0, chamfer=5, notch=5, plain=False):
    """One planed board: lit-from-above gradient, drifting grain, a knot or
    two, chamfer highlights and a hard shadow lip along the bottom."""
    rnd = random.Random(seed)
    w, h = int(w), int(h)
    body = pygame.Surface((w, h), pygame.SRCALPHA)
    _grad_fill(body, (0, 0, w, h), T_LIT, T_DARK)

    for _ in range(max(3, h // 5)):
        gy = rnd.uniform(h * 0.12, h * 0.9)
        col = T_MID if rnd.random() < 0.6 else T_EDGE
        pts = []
        for gx in range(0, w + 6, 6):
            pts.append((gx, gy + math.sin(gx * 0.05 + seed) * 1.4
                        + rnd.uniform(-0.5, 0.5)))
        if len(pts) > 1:
            pygame.draw.lines(body, col, False, pts, 1)

    for _ in range(1 if w < 90 else 2):
        kx = rnd.uniform(w * 0.15, w * 0.85)
        ky = rnd.uniform(h * 0.3, h * 0.7)
        kr = rnd.uniform(2.0, 3.2)
        pygame.draw.ellipse(body, T_EDGE,
                            (kx - kr, ky - kr * 0.72, kr * 2, kr * 1.45))
        pygame.draw.ellipse(body, T_MID,
                            (kx - kr * 1.9, ky - kr * 1.3, kr * 3.8, kr * 2.6), 1)

    # Chamfer catches the light on top, drops to near-black under the lip.
    pygame.draw.line(body, T_HI, (chamfer, 1), (w - chamfer, 1), 2)
    pygame.draw.line(body, (200, 156, 96), (chamfer + 2, 0), (w - chamfer - 2, 0), 1)
    pygame.draw.line(body, T_EDGE, (chamfer, h - 1), (w - chamfer, h - 1), 1)

    if plain:
        pygame.draw.rect(body, T_EDGE, (0, 0, w, h), 1)
        return body

    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pts = _board_points(w, h, chamfer, notch)
    pygame.draw.polygon(mask, (255, 255, 255, 255), pts)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    pygame.draw.polygon(body, T_EDGE, pts, 1)
    return body


def nail(surf, x, y, r=3):
    pygame.draw.circle(surf, T_EDGE, (int(x), int(y + 1)), max(1, r - 1))
    pygame.draw.circle(surf, IRON, (int(x), int(y)), r)
    pygame.draw.circle(surf, IRON_HI, (int(x - r * 0.3), int(y - r * 0.35)),
                       max(1, r - 2))


def rope(surf, p0, p1, sag=6, width=3):
    """Hand-laid rope: a sagging catenary in two tones so the twist reads."""
    x0, y0 = p0
    x1, y1 = p1
    pts = []
    for i in range(13):
        t = i / 12
        pts.append((x0 + (x1 - x0) * t,
                    y0 + (y1 - y0) * t + math.sin(math.pi * t) * sag))
    pygame.draw.lines(surf, ROPE_D, False, pts, width + 1)
    pygame.draw.lines(surf, ROPE, False, pts, max(1, width - 1))


def draw_perch_beam(surf):
    """The plank Pip is standing on. Its top face is pinned to his feet and it
    runs dead straight — off-canvas to the left, and to the right until it
    buries itself in the START slab. One timber, one eyeline: perch → plank →
    button. No kink, because the kink is what let the thesis go soft."""
    beam = timber_board(BEAM_RIGHT + 16, BEAM_H, seed=3, plain=True)
    surf.blit(beam, (-16, BEAM_TOP))
    # The beam floats against open sky, so a projected cast shadow has nothing
    # to fall on — it just reads as a dark duplicate. Its mass comes instead
    # from its own underside catching less light.
    under_shade(surf, pygame.Rect(-16, BEAM_TOP, BEAM_RIGHT + 16, BEAM_H),
                height=5, alpha=44)
    # Top face: a thin lit sliver so the beam reads as a walkable surface.
    pygame.draw.line(surf, (206, 162, 100), (-16, BEAM_TOP),
                     (BEAM_RIGHT, BEAM_TOP), 2)
    for nx in (8, 60, 118, 168):
        nail(surf, nx, BEAM_TOP + 6, 3)
        nail(surf, nx, BEAM_BOT - 7, 3)

    # Cantilever braces under the deck — the perch has to be held up by
    # something, and they fill the sky under the plank on both sides.
    brace = timber_board(104, 13, seed=11, plain=True)
    brace = pygame.transform.rotozoom(brace, -46, 1.0)
    surf.blit(brace, brace.get_rect(center=(24, BEAM_BOT + 44)).topleft)
    nail(surf, 58, BEAM_BOT + 4, 3)


def draw_start_slab(surf):
    """START as a mounted signboard, not a floating pill: timber carcass,
    iron corner straps, scarlet enamel face. The perch plank dies into its
    left flank so the platform and the button read as one object."""
    slab = pygame.Rect(160, 262, 172, 90)

    # The primary control earns the most elevation of anything on screen, but
    # "most" is still small: a tight contact shadow plus a soft ambient falloff
    # that hugs the slab, rather than a +6px hard-edged slab of near-black.
    soft_shadow(surf, slab, "raised")

    carcass = timber_board(slab.width, slab.height, seed=21, chamfer=9, notch=0)
    surf.blit(carcass, slab.topleft)
    under_shade(surf, slab, height=6, alpha=42)

    face = slab.inflate(-20, -22)
    _grad_fill(surf, (face.x, face.y, face.width, face.height),
               SCARLET_TOP, SCARLET_BOT)
    frost = pygame.Surface((face.width, face.height // 2), pygame.SRCALPHA)
    frost.fill((255, 255, 255, 34))
    surf.blit(frost, face.topleft)
    pygame.draw.rect(surf, GOLD_BRIGHT, face, 2)
    pygame.draw.rect(surf, T_EDGE, face.inflate(3, 3), 1)
    pygame.draw.line(surf, (*GOLD_PALE, 150), (face.left + 8, face.top + 5),
                     (face.right - 8, face.top + 5), 1)

    for cx, cy in ((slab.left + 9, slab.top + 9), (slab.right - 9, slab.top + 9),
                   (slab.left + 9, slab.bottom - 9), (slab.right - 9, slab.bottom - 9)):
        pygame.draw.circle(surf, IRON, (cx, cy), 5)
        pygame.draw.circle(surf, IRON_HI, (cx - 1, cy - 2), 2)

    f = _hud._font(34, True)
    txt = "START"
    img = f.render(txt, True, (255, 244, 222))
    r = img.get_rect(center=(face.centerx, face.centery - 1))
    # A 3px fully-opaque halo made the word look bolted on. 1px keeps the
    # cream legible against the enamel without ringing it in ink.
    out = f.render(txt, True, (108, 20, 14))
    out.set_alpha(190)
    for ox, oy in ((-1, 0), (1, 0), (0, -1), (0, 1), (1, 1)):
        surf.blit(out, (r.x + ox, r.y + oy))
    surf.blit(img, r.topleft)
    return slab


def draw_signposts(surf, slab):
    """Three hand-cut boards swinging off the START carcass — the secondary
    menu as a signpost chain, each hung a couple of degrees off true."""
    rows = [("STORE", "coin", (240, 402), -3.0),
            ("TOP 10", "trophy", (226, 460), 2.4),
            ("SETTINGS", "gear", (242, 518), -1.6)]
    # Sized to the longest label, not picked by eye. Each board has a V-notch
    # bitten out of its end face at h*0.5 — exactly the label's own centre
    # line — so the usable right edge is (bw - NOTCH), not bw. At the old 152
    # the SETTINGS text ran 3px PAST that edge; the icon occupies out to ~44,
    # so fitting 99px of text with ~10px padding either side needs bw >= 170.
    bw, bh = 172, 40
    CHAMFER, NOTCH = 6, 7
    ICON_RIGHT = 44                 # coin/trophy/gear drawn at x=30, r<=12
    # Centre the label in the space between the icon and the notched edge.
    # The old hardcoded "+22" approximated this but did not track bw.
    LABEL_CX = (ICON_RIGHT + (bw - NOTCH)) // 2

    anchors = [(slab.centerx - 46, slab.bottom - 4),
               (slab.centerx + 46, slab.bottom - 4)]

    for label, kind, (cx, cy), ang in rows:
        rad = math.radians(-ang)
        for sgn, apt in zip((-1, 1), anchors):
            ox = sgn * (bw * 0.36)
            hx = cx + ox * math.cos(rad)
            hy = cy + ox * math.sin(rad) - bh * 0.5
            rope(surf, apt, (hx, hy), sag=5, width=3)
            pygame.draw.circle(surf, IRON, (int(hx), int(hy)), 3)

        board = timber_board(bw, bh, seed=hash(label) % 997,
                             chamfer=CHAMFER, notch=NOTCH)
        if kind == "coin":
            _hud._coin_icon(board, 30, bh // 2, 12)
        elif kind == "trophy":
            _hud._draw_trophy(board, 30, bh // 2, 10)
        else:
            _hud._draw_gear(board, 30, bh // 2, 12)
        _hud._tracked_label(board, label, (LABEL_CX, bh // 2 + 1), 17,
                            color=(46, 26, 14), track=2, alpha=120)
        _hud._tracked_label(board, label, (LABEL_CX, bh // 2 - 1), 17,
                            color=GOLD_PALE, track=2, alpha=250)
        rot = pygame.transform.rotozoom(board, ang, 1.0)
        rr = rot.get_rect(center=(cx, cy))
        # Silhouette shadow through the shared system: dy 5 -> 2 and alpha
        # 120 -> 40, with a fading edge instead of a hard offset copy.
        soft_shadow(surf, rr, "low", mask=rot)
        surf.blit(rot, rr.topleft)

        # Next board hangs off this one's shoulders.
        anchors = [(cx - bw * 0.34 * math.cos(rad),
                    cy - bw * 0.34 * math.sin(rad) + bh * 0.42),
                   (cx + bw * 0.34 * math.cos(rad),
                    cy + bw * 0.34 * math.sin(rad) + bh * 0.42)]


# ── The cloud, and the chain that hangs from it ──────────────────────────────
# skyhouse_post is a cottage on a cloud (intro._build_skyhouse). Blitted at
# (28, 208) the cloud lands at screen x 28-188, y 296-322 — visible top y~299
# under the house, y~302 under the porch, base y~321. Those are measured off
# the sprite's own alpha, not guessed; CLOUD_* below is re-derived at runtime
# so it can never drift from the art.
CLOUD_ANCHOR_Y = 316          # just inside the cloud's lower mass
CLOUD_HOOK_X = (42, 174)      # the cloud's outer lobes, clear of the nameplate
CLOUD_HOOK_C = (42, 132)      # C hangs START off the outer lobe, so the
                              # chain moves inboard and the two lines never cross


def cloud_rect():
    """Screen bbox of the cloud lobes inside the blitted sprite."""
    house = _intro.get_sprite("skyhouse_post")
    hx, hy = house_topleft()
    # The cloud occupies sprite rows 88+; above that is cottage/porch.
    sub = house.subsurface(pygame.Rect(0, 88, house.get_width(),
                                       house.get_height() - 88))
    bb = pygame.mask.from_surface(sub, threshold=8).get_bounding_rects()
    r = bb[0]
    for extra in bb[1:]:
        r = r.union(extra)
    return pygame.Rect(hx + r.x, hy + 88 + r.y, r.width, r.height)


def draw_signchain(surf):
    """The whole menu hangs from Pip's cloud.

    The boards were previously slung off the underside of a separately mounted
    START signboard, which put the primary control ABOVE all three utilities —
    the reach inversion this effort spent a round removing. Hanging the chain
    from the cloud fixes both things at once: the ropes now leave the object
    Pip actually stands on, and START becomes the last and largest rung, so it
    ends up lowest and nearest the thumb.
    """
    cloud = cloud_rect()
    # 44, not 40: at a shallow hang angle the rotated bounding box barely
    # grows, and a 40px board at -1.6 deg published a 46px tap rect — under
    # the 48dp floor. 44 clears it at every angle in the chain.
    bw, bh = 172, 44
    CHAMFER, NOTCH = 6, 7
    ICON_RIGHT = 44
    LABEL_CX = (ICON_RIGHT + (bw - NOTCH)) // 2

    # START has left the chain. Three rungs only — a fourth board directly
    # under three identical ones is most of what read as "disproportionate".
    dx = -10 if VARIANT in ("B", "C") else 0   # clear the right-hand START
    rows = [("STORE", "coin", (112 + dx, 386), -3.0, bw, bh),
            ("TOP 10", "trophy", (118 + dx, 446), 2.4, bw, bh),
            ("SETTINGS", "gear", (110 + dx, 506), -1.6, bw, bh)]

    # Ropes leave the cloud itself, not a plank. Anchors are clamped into the
    # cloud's measured silhouette so they can never end up hanging in open sky
    # beside it if the sprite ever changes.
    hooks = CLOUD_HOOK_C if VARIANT == 'C' else CLOUD_HOOK_X
    anchors = [(min(max(x, cloud.left + 14), cloud.right - 14), CLOUD_ANCHOR_Y)
               for x in hooks]

    rects = {}
    for label, kind, (cx, cy), ang, w, h in rows:
        rad = math.radians(-ang)
        for sgn, apt in zip((-1, 1), anchors):
            ox = sgn * (w * 0.36)
            hx = cx + ox * math.cos(rad)
            hy = cy + ox * math.sin(rad) - h * 0.5
            rope(surf, apt, (hx, hy), sag=5, width=3)
            pygame.draw.circle(surf, IRON, (int(hx), int(hy)), 3)

        if label == "START":
            board = _start_board(w, h)
        else:
            board = timber_board(w, h, seed=hash(label) % 997,
                                 chamfer=CHAMFER, notch=NOTCH)
            if kind == "coin":
                _hud._coin_icon(board, 30, h // 2, 12)
            elif kind == "trophy":
                _hud._draw_trophy(board, 30, h // 2, 10)
            else:
                _hud._draw_gear(board, 30, h // 2, 12)
            _hud._tracked_label(board, label, (LABEL_CX, h // 2 + 1), 17,
                                color=(46, 26, 14), track=2, alpha=120)
            _hud._tracked_label(board, label, (LABEL_CX, h // 2 - 1), 17,
                                color=GOLD_PALE, track=2, alpha=250)

        rot = pygame.transform.rotozoom(board, ang, 1.0)
        rr = rot.get_rect(center=(cx, cy))
        soft_shadow(surf, rr, "raised" if label == "START" else "low", mask=rot)
        surf.blit(rot, rr.topleft)
        PLANK_SPRITES.append((rot, rr.topleft))
        rects[label] = rr

        anchors = [(cx - w * 0.34 * math.cos(rad),
                    cy - w * 0.34 * math.sin(rad) + h * 0.42),
                   (cx + w * 0.34 * math.cos(rad),
                    cy + w * 0.34 * math.sin(rad) + h * 0.42)]
    rects["_tails"] = anchors
    return rects


def _start_board(w, h):
    """The chain's bottom rung: the same timber carcass as its siblings, but
    larger and carrying the scarlet enamel face, so it reads as one of the
    boards rather than a pill that wandered into a signpost."""
    board = timber_board(w, h, seed=21, chamfer=9, notch=0)
    face = pygame.Rect(0, 0, w - 26, h - 22)
    face.center = (w // 2, h // 2)
    _grad_fill(board, (face.x, face.y, face.width, face.height),
               SCARLET_TOP, SCARLET_BOT)
    frost = pygame.Surface((face.width, face.height // 2), pygame.SRCALPHA)
    frost.fill((255, 255, 255, 34))
    board.blit(frost, face.topleft)
    pygame.draw.rect(board, GOLD_BRIGHT, face, 2)
    pygame.draw.rect(board, T_EDGE, face.inflate(3, 3), 1)
    pygame.draw.line(board, (*GOLD_PALE, 150), (face.left + 8, face.top + 5),
                     (face.right - 8, face.top + 5), 1)
    for cx2, cy2 in ((7, 7), (w - 7, 7), (7, h - 7), (w - 7, h - 7)):
        pygame.draw.circle(board, IRON, (cx2, cy2), 5)
        pygame.draw.circle(board, IRON_HI, (cx2 - 1, cy2 - 2), 2)

    f = _hud._font(34, True)
    img = f.render("START", True, (255, 244, 222))
    r = img.get_rect(center=(face.centerx, face.centery - 1))
    out = f.render("START", True, (108, 20, 14))
    out.set_alpha(190)
    for ox, oy in ((-1, 0), (1, 0), (0, -1), (0, 1), (1, 1)):
        board.blit(out, (r.x + ox, r.y + oy))
    board.blit(img, r.topleft)
    return board


# ── START, three placements ──────────────────────────────────────────────────
# Diagnosis these answer: the body's ink centroid sat at x113 while the title
# spine is x180 — two vertical axes that disagree — under four near-identical
# horizontal bands at 60px pitch. Each variant moves START out of that column.
# All three also TERMINATE the chain (it used to just stop) and introduce one
# small non-rectangular iron note, so the bottom isn't a fifth parallel edge.

def _enamel(board, w, h, fw, fh, size, word="START"):
    face = pygame.Rect(0, 0, fw, fh); face.center = (w // 2, h // 2)
    _grad_fill(board, (face.x, face.y, face.width, face.height),
               SCARLET_TOP, SCARLET_BOT)
    frost = pygame.Surface((face.width, face.height // 2), pygame.SRCALPHA)
    frost.fill((255, 255, 255, 34)); board.blit(frost, face.topleft)
    pygame.draw.rect(board, GOLD_BRIGHT, face, 2)
    pygame.draw.rect(board, T_EDGE, face.inflate(3, 3), 1)
    pygame.draw.line(board, (*GOLD_PALE, 150), (face.left + 8, face.top + 5),
                     (face.right - 8, face.top + 5), 1)
    f = _hud._font(size, True)
    img = f.render(word, True, (255, 244, 222))
    r = img.get_rect(center=(face.centerx, face.centery - 1))
    out = f.render(word, True, (108, 20, 14)); out.set_alpha(190)
    for ox, oy in ((-1, 0), (1, 0), (0, -1), (0, 1), (1, 1)):
        board.blit(out, (r.x + ox, r.y + oy))
    board.blit(img, r.topleft)
    return face


def _best_tag(surf, cx, cy, best):
    """`best` is handed to hud.draw_menu and never drawn — the player's high
    score is absent from the shipped menu entirely. A small tag surfaces it in
    the empty band the deleted post used to occupy."""
    w, h = 104, 24
    tag = timber_board(w, h, seed=5, chamfer=4, notch=0)
    txt = f"BEST {best}" if best else "BEST  -"
    _hud._tracked_label(tag, txt, (w // 2, h // 2 + 1), 12,
                        color=(46, 26, 14), track=2, alpha=120)
    _hud._tracked_label(tag, txt, (w // 2, h // 2 - 1), 12,
                        color=GOLD_PALE, track=2, alpha=240)
    r = tag.get_rect(center=(cx, cy))
    soft_shadow(surf, r, "low", mask=tag)
    surf.blit(tag, r.topleft)


def _iron_ring(surf, cx, cy, r=6):
    """The one non-rectangular note in the bottom band."""
    pygame.draw.circle(surf, T_EDGE, (cx, cy), r + 1)
    pygame.draw.circle(surf, IRON, (cx, cy), r)
    pygame.draw.circle(surf, (*IRON_HI, 255), (cx - 1, cy - 2), max(1, r - 4))
    pygame.draw.circle(surf, (0, 0, 0, 0), (cx, cy), max(1, r - 3))


def draw_start_A(surf, tails):
    """ground-gate — START stops hanging and stands: a level, planted trestle
    spanning the canvas, giving the composition a floor instead of a tail."""
    rect = pygame.Rect(24, 546, 312, 60)
    for px_ in (58, 298):                       # posts into the ground band
        post = timber_board(20, 74, seed=7, plain=True)
        surf.blit(post, (px_ - 10, 546))
        soft_shadow(surf, pygame.Rect(px_ - 10, 600, 20, 20), "contact")
    soft_shadow(surf, rect, "raised")
    board = timber_board(rect.width, rect.height, seed=21, chamfer=9, notch=0)
    _enamel(board, rect.width, rect.height, 200, 40, 34)
    surf.blit(board, rect.topleft)
    under_shade(surf, rect, height=6, alpha=42)
    for bx in (44, 76, 284, 316):
        nail(surf, bx, 576, 3)
    # Moor the chain to the gate's top rail — 3 rungs plus a terminus.
    for (tx, ty), gx in zip(tails, (76, 248)):
        rope(surf, (tx, ty), (gx, rect.top + 3), sag=4, width=3)
        _iron_ring(surf, gx, rect.top + 3, 5)
    return rect


# ── ring-out — the harbour bell ──────────────────────────────────────────────
# The chain's last rope stops being a mooring line and becomes the bell's
# hanger: cloud -> STORE -> TOP 10 -> SETTINGS -> bell. The planks hang; this is
# what they hang toward. Control and sign are the same object because the flared
# skirt IS the type field, and the thing you pull is the thing that rings it.

BELL_CX   = 258      # load-bearing: it is what puts the lip's left edge at
                     # x192, the 5px that keeps the tap rect off SETTINGS' x187
BELL_TOP  = 542
BELL_BOT  = 603
BOW_TOP   = 594      # sound bow: the thick struck band, brightest of the cast
CROWN     = (258, 532)

# One cache canvas holds crown canons, cast body and clapper so the whole load
# swings as a unit; the ring it hangs from stays fixed to the rope.
BODY_ORG  = (188, 524)
BODY_SIZE = (144, 92)
CROWN_LOCAL = (CROWN[0] - BODY_ORG[0], CROWN[1] - BODY_ORG[1])

# Bronze, not the timber family: the object has to be a light figure against a
# quadrant measured at L36 day / L21 night, and it has to sit >=123deg of hue
# off the menu's gold and rust. Every stop below is >=L77.
BR_LIT    = ( 76, 170, 158)
BR_BODY   = ( 40, 120, 116)
BR_DEEP   = ( 34,  96,  94)
BR_MIDLIT = ( 52, 140, 132)
BR_LIP    = ( 96, 196, 180)
VERDIGRIS = (150, 222, 206)
TYPE_GOLD = (255, 232, 168)
# The shipped IRON is L57 - fine ringed by lit timber, invisible hanging in
# open air down here. The clapper gets a lifted iron with IRON as its core.
IRON_LIFT = (126, 120, 128)

CAP_HW, CAP_RISE = 20.0, 2.5
SCALLOPS, SCALLOP_BITE = 5, 4.0


def _half_w(y):
    """The cast profile in half-widths: flattened dome shoulder, concave waist,
    then a flare that opens EARLY so the word has skirt to stand on well before
    the sound bow, and a sound bow slightly proud of the skirt above it."""
    if y <= 551:
        t = max(0.0, (y - BELL_TOP) / 9.0)
        return (40.0 + 14.0 * t ** 0.55) * 0.5
    if y <= 562:
        t = (y - 551) / 11.0
        return (54.0 + 10.0 * t ** 1.6) * 0.5
    if y <= BOW_TOP:
        return (64.0 + 66.0 * ((y - 562) / 32.0) ** 0.45) * 0.5
    t = min(1.0, (y - BOW_TOP) / 9.0)
    return (130.0 + 2.0 * t) * 0.5


def _cap_y(x):
    return BELL_TOP - CAP_RISE * (1.0 - ((x - BELL_CX) / CAP_HW) ** 2)


def _bell_points():
    """One closed polygon, crown cap to lip. No rectangle anywhere in it."""
    pts = [(BELL_CX - CAP_HW + i * 2.0, _cap_y(BELL_CX - CAP_HW + i * 2.0))
           for i in range(21)]
    pts += [(BELL_CX + _half_w(y), y) for y in range(BELL_TOP, BELL_BOT + 1)]
    pts += [(BELL_CX - _half_w(y), y) for y in range(BELL_BOT, BELL_TOP - 1, -1)]
    return pts


def _local(pts):
    return [(x - BODY_ORG[0], y - BODY_ORG[1]) for x, y in pts]


def _grad_stops(surf, rect, stops):
    """Multi-stop vertical ramp. Two stops could not carry a bell: the form
    needs a lit shoulder, a shaded waist and a re-lit skirt in one run."""
    x, y, w, h = rect
    for i in range(h):
        t = i / max(1, h - 1)
        c = stops[-1][1]
        for k in range(len(stops) - 1):
            t0, c0 = stops[k]
            t1, c1 = stops[k + 1]
            if t <= t1 or k == len(stops) - 2:
                u = 0.0 if t1 <= t0 else min(1.0, max(0.0, (t - t0) / (t1 - t0)))
                c = _mix(c0, c1, u)
                break
        pygame.draw.line(surf, c, (x, y + i), (x + w - 1, y + i))


_arc_glyphs = {}


def _arc_glyph(ch, size, ang, color):
    key = (ch, size, round(ang, 2), color)
    img = _arc_glyphs.get(key)
    if img is None:
        img = _hud._font(size, True).render(ch, True, color)
        if abs(ang) > 0.01:
            img = pygame.transform.rotozoom(img, ang, 1.0)
        _arc_glyphs[key] = img
    return img


def _arc_label(surf, text, center, size, track, angles, dys, color, alpha=255):
    """`hud._tracked_label` with each glyph turned to its own tangent. Advance
    is taken from the UNROTATED glyph widths so the run still measures the same
    tracked width the flat helper would give — the type budget is sized on it.
    """
    f = _hud._font(size, True)
    flats = [f.render(ch, True, color) for ch in text]
    total = sum(g.get_width() for g in flats) + track * (len(flats) - 1)
    x = center[0] - total / 2.0
    for ch, flat, ang, dy in zip(text, flats, angles, dys):
        img = _arc_glyph(ch, size, ang, color)
        img.set_alpha(alpha)
        surf.blit(img, img.get_rect(center=(int(round(x + flat.get_width() / 2.0)),
                                            int(round(center[1] + dy)))))
        x += flat.get_width() + track
    return total


# Sagitta 2px with the centre LOWEST: the near rim of a bell's mouth dips at the
# centre, so the word sits in a shallow valley. The per-glyph lean is signed to
# that same tangent (pygame's positive angle is counter-clockwise), which is why
# it runs negative-to-positive rather than the other way about.
TYPE_ANGLES = (-3.0, -1.5, 0.0, 1.5, 3.0)
TYPE_DYS    = (0.0, 1.2, 2.0, 1.2, 0.0)


def _bell_body():
    """The cast body, cached: gradient, reeding, speculars, scalloped lip, one
    bright keyline on the lit arris, and the word struck into the skirt."""
    w, h = BODY_SIZE
    body = pygame.Surface((w, h), pygame.SRCALPHA)
    top_l, bot_l = BELL_TOP - BODY_ORG[1], BELL_BOT - BODY_ORG[1]

    _grad_stops(body, (0, top_l - 3, w, (bot_l - top_l) + 4),
                [(0.00, BR_LIT), (0.25, BR_BODY), (0.50, BR_DEEP),
                 (0.80, BR_MIDLIT), (1.00, BR_LIP)])

    # Speculars before the silhouette clip, so a band can be authored in screen
    # columns and let the profile decide how much of it survives.
    #
    # Premultiplied on purpose. pygame's BLEND_ADD is BLEND_RGB_ADD: it ignores
    # the source alpha and adds the raw channels, so the (255,255,255,a) sweep
    # `store_cards.gloss_sweep` builds adds a flat 255 and takes the whole cast
    # to L255 (measured). The falloff shape is that helper's - eased over the
    # full height, bright at the crown - carried on a premultiplied layer so the
    # amount actually lands.
    spec = pygame.Surface((w, h), pygame.SRCALPHA)
    for sy in range(BELL_TOP - 2, BELL_BOT + 1):
        v = min(1.0, max(0.0, (sy - BELL_TOP) / float(BELL_BOT - BELL_TOP)))
        sheen = 14 * (1.0 - v) ** 2.4
        hw = _half_w(sy)
        for sx in range(int(BELL_CX - hw) - 1, int(BELL_CX + hw) + 2):
            a = sheen
            tint = (1.0, 1.0, 0.96)
            if 238 <= sx < 248:
                a += 52 * math.sin(math.pi * (sx - 238 + 0.5) / 10.0) ** 1.4 \
                     * (1.0 - v) ** 1.4
            elif 300 <= sx < 312:
                cool = 26 * math.sin(math.pi * (sx - 300 + 0.5) / 12.0) ** 1.4 \
                       * v ** 1.6
                if cool > a:
                    tint = (0.74, 0.94, 1.0)
                a += cool
            if a > 1.5:
                a = min(96.0, a)
                spec.set_at((sx - BODY_ORG[0], sy - BODY_ORG[1]),
                            (int(a * tint[0]), int(a * tint[1]), int(a * tint[2]),
                             int(a)))
    body.blit(spec, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    # Two incised reeds. Shadow on the upper facet, verdigris catch on the lower
    # one — cut INTO the casting, which is the opposite stacking from a raised
    # bead and the only way a 2px line reads as depth at this size.
    for ry in (566, 571):
        hw = _half_w(ry) - 3
        pygame.draw.line(body, BR_DEEP,
                         (BELL_CX - hw - BODY_ORG[0], ry - BODY_ORG[1]),
                         (BELL_CX + hw - BODY_ORG[0], ry - BODY_ORG[1]), 1)
        pygame.draw.line(body, VERDIGRIS,
                         (BELL_CX - hw - BODY_ORG[0], ry + 1 - BODY_ORG[1]),
                         (BELL_CX + hw - BODY_ORG[0], ry + 1 - BODY_ORG[1]), 1)

    # The wire above the sound bow — the moulding that tells the eye where the
    # casting thickens. Low alpha on purpose: full strength reads as a rule.
    wire = pygame.Surface((w, h), pygame.SRCALPHA)
    hw = _half_w(BOW_TOP) - 2
    pygame.draw.line(wire, (*BR_LIP, 120),
                     (BELL_CX - hw - BODY_ORG[0], BOW_TOP - BODY_ORG[1]),
                     (BELL_CX + hw - BODY_ORG[0], BOW_TOP - BODY_ORG[1]), 1)
    body.blit(wire, (0, 0))

    _strike_word(body)

    # Silhouette clip: polygon minus five scallops. Same scratch-mask +
    # BLEND_RGBA_MIN pattern `timber_board` uses, so nothing here needs numpy.
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), _local(_bell_points()))
    # Cut as sampled arcs rather than ellipse rects: an integer ellipse rect
    # cannot land five equal bites on a 132px lip, and the asymmetry it leaves
    # is exactly the kind of thing only a 1x thumbnail shows.
    pitch = 132.0 / SCALLOPS
    for i in range(SCALLOPS):
        x0 = 192 + pitch * i - BODY_ORG[0]
        base = BELL_BOT - BODY_ORG[1] + 1
        cut = [(x0 + pitch * (k / 12.0),
                base - SCALLOP_BITE * math.sin(math.pi * k / 12.0))
               for k in range(13)]
        cut += [(x0 + pitch, base + 6), (x0, base + 6)]
        pygame.draw.polygon(mask, (0, 0, 0, 0), cut)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    # ONE keyline, and a bright one: this quadrant never goes light, so a second
    # dark contour would be a step the screen never needs.
    arris = [(BELL_CX + 10 - i, _cap_y(BELL_CX + 10 - i)) for i in range(31)]
    arris += [(BELL_CX - _half_w(y), y) for y in range(BELL_TOP, BELL_BOT + 1)]
    pygame.draw.lines(body, VERDIGRIS, False, _local(arris), 1)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    _canons(body)
    _clapper(body)
    return body


def _strike_word(body):
    """START struck across the skirt: a dark twin one pixel down under a
    gold-pale face, so the word belongs to the casting rather than sitting on
    a painted panel."""
    cx = BELL_CX - BODY_ORG[0]
    cy = 585 - BODY_ORG[1]
    _arc_label(body, "START", (cx, cy + 1), 26, 2, TYPE_ANGLES, TYPE_DYS,
               BR_DEEP, alpha=235)
    _arc_label(body, "START", (cx, cy), 26, 2, TYPE_ANGLES, TYPE_DYS,
               TYPE_GOLD, alpha=255)


def _canons(body):
    """Two cast loops from the crown down onto the shoulder. Bronze, not iron —
    on a real bell they are part of the same pour as the body."""
    for sx, bow in ((250, -3), (266, 3)):
        pts = []
        for i in range(9):
            t = i / 8.0
            pts.append((sx + bow * math.sin(math.pi * t) - BODY_ORG[0],
                        532 + 10 * t - BODY_ORG[1]))
        pygame.draw.lines(body, BR_DEEP, False, pts, 4)
        pygame.draw.lines(body, BR_BODY, False, pts, 2)
        pygame.draw.lines(body, VERDIGRIS, False,
                          [(px - 1, py) for px, py in pts[:6]], 1)


def _clapper(body):
    """Iron pear hanging in the mouth. The centre scallop is what lets it be
    seen at all — the bite in the lip is why the bell reads as hollow."""
    ox, oy = BODY_ORG
    pygame.draw.line(body, (52, 46, 52), (258 - ox, 597 - oy), (258 - ox, 605 - oy), 3)
    pygame.draw.line(body, IRON_LIFT, (257 - ox, 597 - oy), (257 - ox, 605 - oy), 1)
    pygame.draw.ellipse(body, (46, 40, 46),
                        pygame.Rect(251 - ox, 602 - oy, 14, 9))
    pygame.draw.ellipse(body, IRON_LIFT,
                        pygame.Rect(252 - ox, 603 - oy, 12, 7))
    pygame.draw.circle(body, (196, 192, 200), (255 - ox, 605 - oy), 2)
    pygame.draw.circle(body, (30, 26, 30), (259 - ox, 608 - oy), 2)


def _monkeys_fist(surf, cx, cy, r=6):
    """A monkey's fist on the lanyard end. The chain hangs; this is the one
    thing on the screen shaped like something a hand is meant to close on."""
    pygame.draw.circle(surf, ROPE_D, (cx, cy), r)
    pygame.draw.circle(surf, ROPE, (cx, cy), r - 1)
    for k in (-3, 0, 3):
        pygame.draw.arc(surf, ROPE_D,
                        pygame.Rect(cx - r + 1, cy - r + 1 + k, r * 2 - 2, r * 2 - 2),
                        0.5, 2.7, 1)
    pygame.draw.arc(surf, ROPE_D, pygame.Rect(cx - 3, cy - r, 6, r * 2), -1.4, 1.4, 1)
    pygame.draw.circle(surf, (232, 206, 152), (cx - 2, cy - 2), 1)


def _ring_arcs(surf, t):
    """Two expanding bronze arcs off the lip on tap — the sound, drawn."""
    layer = pygame.Surface((W, H), pygame.SRCALPHA)
    for k, lead in enumerate((0.0, 0.35)):
        u = t - lead
        if not 0.0 < u < 1.0:
            continue
        rr = 70 + 44 * u
        a = int(150 * (1.0 - u) ** 1.6)
        # Flattened hard and centred high on purpose: at 0.42 the lower sweep
        # of the arc crossed y628, four pixels under the composition's y624
        # floor.
        pts = [(BELL_CX + rr * math.cos(math.radians(ang)),
                596 + rr * 0.26 * math.sin(math.radians(ang)))
               for ang in range(-46, 47, 6)]
        for sgn in (-1, 1):
            pygame.draw.lines(layer, (*VERDIGRIS, a), False,
                              [(BELL_CX + sgn * (px - BELL_CX), py) for px, py in pts],
                              2 if k == 0 else 1)
    surf.blit(layer, (0, 0))


def _ringout_report(surf_before, surf_after, rot, rr):
    """Numeric self-check. The whole risk in this concept is a thumbnail risk,
    so every claim it makes about width, clearance and value is measured off the
    rendered pixels rather than off the construction numbers."""
    import PIL.Image, PIL.ImageChops
    m = pygame.mask.from_surface(rot, 8)
    bb = m.get_bounding_rects()
    r = bb[0]
    for o in bb[1:]:
        r = r.union(o)
    print(f"  BELL body bbox  x[{rr.x+r.x}..{rr.x+r.right-1}] "
          f"y[{rr.y+r.y}..{rr.y+r.bottom-1}]")
    for y in (542, 551, 562, 575, 584, 593, 594, 603):
        ly = y - rr.y
        xs = [x for x in range(rot.get_width()) if m.get_at((x, ly))] if 0 <= ly < rot.get_height() else []
        if xs:
            print(f"    row y={y}: x{rr.x+xs[0]}..{rr.x+xs[-1]}  w={xs[-1]-xs[0]+1}"
                  f"  (profile w={2*_half_w(y):.1f})")

    ink = pygame.Surface(BODY_SIZE, pygame.SRCALPHA)
    _strike_word(ink)
    ib = pygame.mask.from_surface(ink, 8).get_bounding_rects()
    q = ib[0]
    for o in ib[1:]:
        q = q.union(o)
    tx0, tx1 = BODY_ORG[0] + q.x, BODY_ORG[0] + q.right - 1
    ty0, ty1 = BODY_ORG[1] + q.y, BODY_ORG[1] + q.bottom - 1
    print(f"  TYPE ink bbox   x[{tx0}..{tx1}] y[{ty0}..{ty1}]  "
          f"run={q.width}px  height={q.height}px")
    for y in (ty0, 575, ty1):
        hw = _half_w(y)
        print(f"    at y={y}: skirt w={2*hw:.1f} (x{BELL_CX-hw:.1f}..{BELL_CX+hw:.1f})"
              f"  clear L={tx0-(BELL_CX-hw):.1f} R={(BELL_CX+hw)-tx1:.1f}")

    def _lum(c):
        return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]

    print("  CAST row profile (median body luma / leftmost keyline pixel):")
    for y in range(542, 604, 4):
        ly = y - rr.y
        cols = [x for x in range(rot.get_width()) if m.get_at((x, ly))]
        if not cols:
            continue
        lums = sorted(_lum(rot.get_at((x, ly))) for x in cols)
        kl = rot.get_at((cols[0], ly))
        print(f"    y={y}: median L{lums[len(lums)//2]:6.1f}  "
              f"min L{lums[0]:6.1f}  max L{lums[-1]:6.1f}   "
              f"keyline px rgb{tuple(kl)[:3]} L{_lum(kl):6.1f}")

    before = pygame.image.tostring(surf_before, "RGB")
    after = pygame.image.tostring(surf_after, "RGB")
    ia = PIL.Image.frombytes("RGB", (W, H), before)
    ib2 = PIL.Image.frombytes("RGB", (W, H), after)
    d = PIL.ImageChops.difference(ia, ib2).convert("L").point(lambda v: 255 if v > 2 else 0)
    print(f"  RING-OUT drawn bbox (all furniture): {d.getbbox()}")
    d2 = d.crop((190, 0, W, H))
    bb2 = d2.getbbox()
    print(f"  RING-OUT drawn bbox (x>=190, i.e. the control): "
          f"{(bb2[0]+190, bb2[1], bb2[2]+190, bb2[3]) if bb2 else None}")


_body_cache = {}


def _hang_angle():
    return {"rest": 0.0, "sway": 1.5, "tap": 8.0}.get(POSE, 0.0)


def draw_start_B(surf, tails):
    """ring-out — START is a cast-bronze harbour bell on the chain's last rope,
    the word struck across its flared skirt and a hemp lanyard dropping to a
    monkey's fist at thumb height.

    The timber post, the diagonal brace and the mooring ring are gone with it:
    a bell cannot hang from a rope arriving out of a cloud AND stand on a
    planted post, and nothing here is planted.
    """
    snap = surf.copy() if os.environ.get("MEASURE") else None
    body = _body_cache.get("body")
    if body is None:
        body = _body_cache["body"] = _bell_body()

    ang = _hang_angle()
    rot = pygame.transform.rotozoom(body, ang, 1.0) if ang else body
    if ang:
        # Swing about the crown ring, not the sprite centre: the ring is the
        # fixed point, the load is what moves under it.
        th = math.radians(ang)
        cx0, cy0 = BODY_SIZE[0] / 2.0, BODY_SIZE[1] / 2.0
        dx, dy = CROWN_LOCAL[0] - cx0, CROWN_LOCAL[1] - cy0
        qx = rot.get_width() / 2.0 + dx * math.cos(th) + dy * math.sin(th)
        qy = rot.get_height() / 2.0 - dx * math.sin(th) + dy * math.cos(th)
        topleft = (int(round(CROWN[0] - qx)), int(round(CROWN[1] - qy)))
    else:
        topleft = BODY_ORG

    rr = rot.get_rect(topleft=topleft)
    soft_shadow(surf, rr, "raised", mask=rot)

    # The hang rope leaves the SETTINGS tail, so it is cut out of the frozen
    # boards before it lands: the line reads as tied off behind the plank and
    # not one plank pixel is repainted.
    line = pygame.Surface((W, H), pygame.SRCALPHA)
    # Six pixels of drop over ninety-nine of run proves nothing on its own; the
    # sag is what says the far end is carrying a load.
    rope(line, tails[1], CROWN, sag=10, width=3)
    for sprite, pos in PLANK_SPRITES:
        line.blit(sprite, pos, special_flags=pygame.BLEND_RGBA_SUB)
    surf.blit(line, (0, 0))

    surf.blit(rot, rr.topleft)
    _iron_ring(surf, CROWN[0], CROWN[1], r=5)

    eye = (258, 610)
    rope(surf, eye, (278, 617), sag=4, width=3)
    _monkeys_fist(surf, 278, 617, 6)

    if POSE == "tap":
        _ring_arcs(surf, 0.45)

    # Was on the post head at (276,610), which is now the knot. Out of the
    # bell's x192 left edge entirely.
    _best_tag(surf, 96, 566, BEST_SCORE)
    if snap is not None:
        _ringout_report(snap, surf, rot, rr)
    return pygame.Rect(192, 526, 132, 97)


def draw_start_C(surf, tails):
    """long-drop — the cloud carries two loads: the utilities on a short chain,
    and START alone on its own long tackle down the empty right side."""
    cloud = cloud_rect()
    rect = pygame.Rect(196, 486, 150, 86)
    hook = (min(cloud.right - 14, 174), CLOUD_ANCHOR_Y)
    board = timber_board(rect.width, rect.height, seed=21, chamfer=9, notch=0)
    _enamel(board, rect.width, rect.height, 124, 44, 30)
    rot = pygame.transform.rotozoom(board, 4.0, 1.0)
    rr = rot.get_rect(center=rect.center)
    for sgn in (-1, 1):
        hx = rect.centerx + sgn * rect.width * 0.34
        hy = rect.top + 4
        rope(surf, hook, (hx, hy), sag=9, width=3)
        _iron_ring(surf, int(hx), int(hy), 5)
    soft_shadow(surf, rr, "raised", mask=rot)
    surf.blit(rot, rr.topleft)
    # A mooring line stakes the corner so the board doesn't read as swinging off.
    rope(surf, (rr.centerx + 40, rr.bottom - 6), (300, 595), sag=5, width=3)
    _iron_ring(surf, 300, 595, 5)
    return rr


def house_topleft():
    house = _intro.get_sprite("skyhouse_post")
    return (int(W * 0.30) - house.get_width() // 2,
            int(H * 0.42) - house.get_height() // 2)


def house_cottage_rect():
    """Screen-space box of the cottage MASS only (its right-hand deck run is
    excluded — that timber carries on into the sign and shouldn't drag the
    frame with it)."""
    house = _intro.get_sprite("skyhouse_post")
    hx, hy = house_topleft()
    sub = house.subsurface(pygame.Rect(0, 0, 100, BEAM_TOP - hy))
    rects = pygame.mask.from_surface(sub, 8).get_bounding_rects()
    r = rects[0]
    for o in rects[1:]:
        r = r.union(o)
    return pygame.Rect(hx + r.x, hy + r.y, r.width, r.height)


def draw_profile_frame(surf):
    """The jewel-frame-on-Pip treatment, keyed to the cloud.

    It bounds the cottage plus Pip's true sprite box and closes on the cloud's
    measured base, so the frame reads as enclosing the whole floating island —
    cottage, bird and cloud — which is also the object the sign chain hangs
    from. The nameplate rides the cloud rather than a timber face."""
    # Fit to the sprite's OPAQUE cottage, not its 160x120 canvas — the canvas
    # is mostly empty air above the roof, which used to leave the frame
    # floating 30 px clear of anything it was supposed to be framing.
    cot = house_cottage_rect()
    bird_r = pygame.Rect(PIP_CX - 31, int(PIP_CY) - 27, 64, 51)
    fr = cot.union(bird_r).inflate(24, 24)
    # The deck run must be free to continue past the frame into the START
    # slab; the frame stops short of it rather than boxing the join in.
    cloud = cloud_rect()
    # Close at the cottage's stone foundation, not the cloud's base. A 22px
    # nameplate on a 26px cloud buries it; ending here leaves the cloud
    # floating free below the frame, which is what the chain hangs from.
    fr.width = min(fr.width, 168 - fr.left)
    fr.height = (cloud.top - 2) - fr.top

    pad = 14
    glow = pygame.Surface((fr.width + pad * 2, fr.height + pad * 2), pygame.SRCALPHA)
    for k in range(pad, 0, -1):
        a = int(0.9 * 74 * k / pad / 3.6)
        pygame.draw.rect(glow, (*GOLD_BRIGHT, a),
                         (pad - k, pad - k, fr.width + k * 2, fr.height + k * 2),
                         border_radius=15 + k)
    surf.blit(glow, (fr.x - pad, fr.y - pad))

    pygame.draw.rect(surf, GOLD_MID, fr, width=1, border_radius=14)
    pygame.draw.rect(surf, GOLD_BRIGHT, fr.inflate(-12, -12), width=1, border_radius=9)
    pygame.draw.line(surf, (*GOLD_PALE, 200), (fr.left + 16, fr.top + 2),
                     (fr.right - 16, fr.top + 2), 1)

    plate = pygame.Rect(0, 0, 112, 22)
    # Straddle the frame's lower rule, so it reads as bolted to the base of
    # the house rather than laid across the cloud.
    plate.center = (fr.centerx, fr.bottom)
    pygame.draw.rect(surf, GOLD_DEEP, plate, border_radius=7)
    pygame.draw.rect(surf, GOLD_MID, plate.inflate(-3, -3), border_radius=6)
    pygame.draw.line(surf, GOLD_PALE, (plate.left + 8, plate.top + 3),
                     (plate.right - 8, plate.top + 3), 1)
    pygame.draw.line(surf, (86, 60, 16), (plate.left + 8, plate.bottom - 3),
                     (plate.right - 8, plate.bottom - 3), 1)
    inset = plate.inflate(-8, -8)
    pygame.draw.rect(surf, (52, 34, 14), inset, border_radius=4)
    lx = inset.centerx - 7
    _hud._tracked_label(surf, "PROFILE", (lx, inset.centery + 1), 13,
                        color=(34, 20, 8), track=2, alpha=150)
    _hud._tracked_label(surf, "PROFILE", (lx, inset.centery), 13,
                        color=GOLD_PALE, track=2, alpha=250)
    _hud._profile_tri(surf, inset.right - 9, inset.centery, 4, GOLD_PALE)
    return fr


def _verify_pip(before, after):
    """Pass/fail gate: the pixels bird.draw() actually touched must be
    centred on the respawn point, or the menu pops the moment START is hit."""
    from PIL import Image, ImageChops
    # Scratch comparison frames: keep them out of the repo — these
    # scripts live under tools/ now, not in a throwaway directory.
    import tempfile
    tmp = tempfile.gettempdir()
    pa, pb = os.path.join(tmp, "_a.png"), os.path.join(tmp, "_b.png")
    pygame.image.save(before, pa)
    pygame.image.save(after, pb)
    ia = Image.open(pa).convert("RGB")
    ib = Image.open(pb).convert("RGB")
    box = ImageChops.difference(ia, ib).convert("L").point(
        lambda v: 255 if v > 6 else 0).getbbox()
    x0, y0, x1, y1 = box[0], box[1], box[2] - 1, box[3] - 1
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    print(f"  PIP bbox x[{x0}..{x1}] y[{y0}..{y1}]  centre=({cx:.1f}, {cy:.1f})"
          f"  target=(90.0, 268.8)  delta=({cx - 90:.1f}, {cy - 268.8:.1f})")
    print(f"  PIP feet (bbox bottom) y={y1}   beam top y={BEAM_TOP}")


def main():
    app = App()
    app._cooldown_t = 0.0
    app._fetch_pending = False
    app.state = STATE_MENU
    app.world = World()
    for _ in range(40):
        app.world.world_idle_tick(1 / 60)
    # Day phase, dead-on: idle ticks advance biome_time, so wind it back.
    app.world.biome_time = PHASE * _biome.CYCLE_SECONDS
    app.world.weather.wetness = 0.0
    app.world.bird.frame_t = 0.0
    app.world.bird.x = PIP_CX
    app.world.bird.y = PIP_CY

    pal = _biome.palette_for_phase(PHASE)
    surf = app.screen
    app._draw_background(surf)
    foreground.draw_near_lane(surf, app.world.bg_scroll, pal, 0.0,
                              app.world.biome_time)

    # Shipping menu compositing stack, verbatim from hud.draw_menu: the
    # night-sky veil, the twinkle field, then the silhouette. The old mock
    # substituted a hand-rolled vignette here, which left the sky ~80 luma
    # brighter than the real screen and mistuned every palette judged on it.
    dim = pygame.Surface((W, H), pygame.SRCALPHA)
    dim.fill((6, 1, 21, 110))
    surf.blit(dim, (0, 0))

    rng = random.Random(42)
    stars = [(rng.randint(8, W - 8), rng.randint(8, H - 180),
              rng.choice((1, 1, 1, 2)), rng.uniform(0, 6.28))
             for _ in range(38)]
    _hud._draw_overlay_stars(surf, stars, 0.0)
    _hud._draw_mountain_silhouette(surf, alpha=180)

    house = _intro.get_sprite("skyhouse_post")
    hx = int(W * 0.30) - house.get_width() // 2
    hy = int(H * 0.42) - house.get_height() // 2
    # Full sprite: the cottage sits on its own cloud, exactly as the intro
    # leaves it. The old build cropped at row 83, which threw the cloud, the
    # porch deck and the stone foundation away and put a timber beam in the
    # hole. The cloud is the thing Pip arrives on, so it is what the menu
    # hangs from.
    surf.blit(house, (hx, hy))
    before = surf.copy()
    app.world.bird.draw(surf)
    _verify_pip(before, surf)
    _chain = draw_signchain(surf)
    _tails = _chain.pop("_tails")
    if not os.environ.get("NOSTART"):
        {"A": draw_start_A, "B": draw_start_B, "C": draw_start_C}[VARIANT](surf, _tails)
    draw_profile_frame(surf)

    _hud._outlined_text(surf, "SKYBIT", (W // 2, 112), size=72, px=3,
                        shadow_offset=(2, 3))
    _hud._outlined_text(surf, "POCKET  SKY  FLYER", (W // 2, 168),
                        size=20, px=2, shadow_offset=(1, 2))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    pygame.image.save(surf, OUT)
    print("saved", OUT)


main()
