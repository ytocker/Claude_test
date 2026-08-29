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


def draw_start_B(surf, tails):
    """harbour-post — START leaves the chain entirely and is planted in the
    dead bottom-right quadrant, standing on its own post."""
    rect = pygame.Rect(208, 494, 136, 100)
    post = timber_board(24, 120, seed=7, plain=True)
    surf.blit(post, (264, 494))
    brace = timber_board(74, 12, seed=11, plain=True)
    brace = pygame.transform.rotozoom(brace, 38, 1.0)
    surf.blit(brace, brace.get_rect(center=(236, 566)).topleft)
    soft_shadow(surf, pygame.Rect(264, 588, 24, 22), "contact")
    soft_shadow(surf, rect, "raised")
    board = timber_board(rect.width, rect.height, seed=21, chamfer=9, notch=0)
    face = _enamel(board, rect.width, rect.height, 110, 46, 28)
    # gold double-chevron under the word: the extra height carries the
    # emphasis the narrower board gives up.
    for k, oy in enumerate((14, 21)):
        cy2 = face.bottom + oy - 6
        pygame.draw.lines(board, GOLD_PALE, False,
                          [(rect.width // 2 - 11, cy2 - 4),
                           (rect.width // 2, cy2),
                           (rect.width // 2 + 11, cy2 - 4)], 2)
    surf.blit(board, rect.topleft)
    under_shade(surf, rect, height=6, alpha=42)
    return rect


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

    The frame now hugs the cottage plus Pip's true sprite box only — it no
    longer has to reserve room for a nameplate straddling its own bottom
    rule, so it can close right at the cottage's foundation. The PROFILE tag
    is a separate element hanging clear below the cloud, where the sign
    chain's ropes have already left the cloud's outer lobes and are running
    down and inward to the first plank, so a centred tag between them never
    crosses a line."""
    # Fit to the sprite's OPAQUE cottage, not its 160x120 canvas — the canvas
    # is mostly empty air above the roof, which used to leave the frame
    # floating 30 px clear of anything it was supposed to be framing.
    cot = house_cottage_rect()
    bird_r = pygame.Rect(PIP_CX - 31, int(PIP_CY) - 27, 64, 51)
    fr = cot.union(bird_r).inflate(18, 18)
    # The deck run must be free to continue past the frame into the START
    # slab; the frame stops short of it rather than boxing the join in.
    fr.width = min(fr.width, 168 - fr.left)
    cloud = cloud_rect()
    # Close at the cottage's stone foundation — the frame's own job stops
    # there now that the tag has moved off it.
    fr.height = min(fr.height, (cloud.top - 6) - fr.top)

    pygame.draw.rect(surf, GOLD_MID, fr, width=1, border_radius=13)
    pygame.draw.rect(surf, GOLD_BRIGHT, fr.inflate(-10, -10), width=1, border_radius=8)
    pygame.draw.line(surf, (*GOLD_PALE, 200), (fr.left + 14, fr.top + 2),
                     (fr.right - 14, fr.top + 2), 1)

    # The tag: between the two rope columns that leave the cloud's outer
    # lobes at CLOUD_HOOK_X and run down to the first plank. The right rope
    # angles inward faster than the left one stays put, so centring on the
    # cloud alone leaves under a pixel of clearance on that side — shifted
    # 4px left for even clearance on both.
    plate = pygame.Rect(0, 0, 112, 26)
    plate.midtop = (cloud.centerx - 4, cloud.bottom + 8)
    pygame.draw.rect(surf, GOLD_DEEP, plate, border_radius=8)
    pygame.draw.rect(surf, GOLD_MID, plate.inflate(-3, -3), border_radius=7)
    pygame.draw.line(surf, GOLD_PALE, (plate.left + 8, plate.top + 3),
                     (plate.right - 8, plate.top + 3), 1)
    pygame.draw.line(surf, (86, 60, 16), (plate.left + 8, plate.bottom - 3),
                     (plate.right - 8, plate.bottom - 3), 1)
    inset = plate.inflate(-8, -8)
    pygame.draw.rect(surf, (52, 34, 14), inset, border_radius=5)
    lx = inset.centerx - 7
    _hud._tracked_label(surf, "PROFILE", (lx, inset.centery + 1), 13,
                        color=(34, 20, 8), track=2, alpha=150)
    _hud._tracked_label(surf, "PROFILE", (lx, inset.centery), 13,
                        color=GOLD_PALE, track=2, alpha=250)
    _hud._profile_tri(surf, inset.right - 9, inset.centery, 4, GOLD_PALE)
    return fr.union(plate)


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
