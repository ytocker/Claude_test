"""colours-up — START as a deep-swallowtail signal flag on a jack-staff.

Fork of tools/menu-design/launch_perch_start.py (VARIANT=B, the approved
base). Everything above the flag is the base verbatim — `timber_board`,
`draw_signchain` and the three plank signs are untouched code paths, so the
planks are identical by construction rather than by hand-matching.

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
    dead bottom-right quadrant, with the chain's last rope mooring to it."""
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
    # The chain's right tail runs down and ties off on the post head.
    ring = (214, 500)
    rope(surf, tails[1], ring, sag=7, width=3)
    _iron_ring(surf, *ring, r=6)
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




# ─────────────────────────────────────────────────────────────────────────────
# CONCEPT: `colours-up` — the launch flag
#
# A deep-swallowtail signal flag bent onto the halyard the sign chain has
# become, flying from a short jack-staff in the dead bottom-right quadrant.
# The chain does not merely end near START; it reeves through the masthead
# block and the flag's luff is where it terminates.
#
# Everything below replaces what `draw_start_B` drew. The three plank signs,
# the cloud, the chain above SETTINGS and Pip are untouched.
# ─────────────────────────────────────────────────────────────────────────────

def _mix(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


RIPPLE = float(os.environ.get("RIPPLE", "0.0"))
MODE = os.environ.get("MODE", "flag")          # "flag" | "base"

# Cloth palette. Every value is a measured luma against a START-quadrant
# backdrop that is L36 by day and L21 at night: the flag is a LIGHT figure at
# both poles, so it needs ONE keyline, not a two-step contour. The floor is
# L70 for any large mass — the first pass' trough (12,86,98) L65.3 and hoist
# band (14,74,84) L57.2 both sat under it and are lifted here.
CLOTH_FIELD   = ( 20, 132, 146)     # L100.1
CLOTH_CREST   = ( 58, 178, 190)     # L143.5
CLOTH_TROUGH  = ( 16, 104, 116)     # L 79.1
CLOTH_REVERSE = ( 18,  96, 108)     # L 74.0  — hoist band + the curled sliver
# The type's drop-shadow is a dark CLOTH value, not the planks' brown keyline:
# on teal it has to read as the word casting into the weave, not as a second
# outline colour arriving from another material.
CLOTH_SHADOW  = ( 10,  52,  60)

# Mast / flag geometry, all screen coords.
MAST_TRUCK_Y = 516
MAST_FOOT_Y  = 608
BLOCK        = (202, 526)           # <= the y532 masthead ceiling
FLAG_RECT    = pygame.Rect(204, 532, 140, 82)
TAP_RECT     = pygame.Rect(196, 528, 150, 86)
HOIST_X, FLY_X = 204, 344
BAND_X       = 218                  # hoist band runs 204..218
NOTCH_X, NOTCH_Y = 318, 570         # swallowtail vertex -> a 26px bite
TIP_UP, TIP_LO = 550, 600
WAVE_AMP, WAVE_LAMBDA, WAVE_SPEED = 4.0, 70.0, 1.6
WORD_C = (268, 570)

# The flag is composited in its own local frame so the warp, the mask and the
# gold border can all be resolved before anything touches the screen.
FOX, FOY = 202, 528
FW, FH = 146, 92


def _luma(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def _smooth(t):
    t = min(1.0, max(0.0, t))
    return t * t * (3 - 2 * t)


def _seg(x, x0, y0, x1, y1):
    return y0 + (y1 - y0) * _smooth((x - x0) / (x1 - x0))


def _top_base(x):
    """Rises from the hoist, then FALLS again over the last third — the fly is
    curled, so the long edges are not parallel even with the ripple frozen.

    Sitting 4px lower than the concept's numbers, because those were quoted
    with the ripple frozen: base y532 plus the brief's own +-4 wave puts cloth
    at y528, which is 2.4px ABOVE SETTINGS' bottom edge y530.4 and outside the
    published Rect(204,532,...). At +4 the warped envelope closes exactly on it.
    """
    return _seg(x, 204, 542, 290, 536) if x <= 290 else _seg(x, 290, 536, 344, 550)


def _bot_base(x):
    """Two px higher than quoted, for the mirror-image reason: base y612 plus
    the +-4 wave reached y616, past the published rect's bottom edge y614."""
    return _seg(x, 204, 604, 300, 610) if x <= 300 else _seg(x, 300, 610, 344, 600)


def _luff_taper(x):
    """The head and tack cringles are seized to the halyard, so the cloth
    cannot flap at the luff — the wave has to be born a little out from it."""
    return _smooth((x - HOIST_X) / 40.0)


def _wave(x, t):
    ph = 2 * math.pi * (x - HOIST_X) / WAVE_LAMBDA - t * WAVE_SPEED
    return WAVE_AMP * math.sin(ph) * _luff_taper(x)


def _wave_slope(x, t):
    """Normalised local surface normal, -1 (trough) .. +1 (crest)."""
    ph = 2 * math.pi * (x - HOIST_X) / WAVE_LAMBDA - t * WAVE_SPEED
    return max(-1.0, min(1.0, -math.cos(ph) * _luff_taper(x)))


def _cloth_edges(x, t):
    """(top, bottom, tail_upper, tail_lower) at screen x. Past the notch the
    cloth is split in two by the swallowtail and the middle is sky."""
    d = _wave(x, t)
    top, bot = _top_base(x) + d, _bot_base(x) + d
    if x <= NOTCH_X:
        return top, bot, None, None
    u = (x - NOTCH_X) / (FLY_X - NOTCH_X)
    return (top, bot,
            NOTCH_Y + (TIP_UP - NOTCH_Y) * u + d,
            NOTCH_Y + (TIP_LO - NOTCH_Y) * u + d)


def _outline(t, step=2):
    """The warped silhouette as one closed loop — top edge out to the upper
    fly tip, in to the notch vertex, out to the lower tip, bottom edge home."""
    pts = []
    x = float(HOIST_X)
    while x < FLY_X:
        pts.append((x, _top_base(x) + _wave(x, t)))
        x += step
    d_fly = _wave(FLY_X, t)
    pts.append((FLY_X, _top_base(FLY_X) + d_fly))
    pts.append((NOTCH_X, NOTCH_Y + _wave(NOTCH_X, t)))
    pts.append((FLY_X, TIP_LO + d_fly))
    x = float(FLY_X)
    while x > HOIST_X:
        pts.append((x, _bot_base(x) + _wave(x, t)))
        x -= step
    pts.append((HOIST_X, _bot_base(HOIST_X) + _wave(HOIST_X, t)))
    return pts


# Form-shading is a cached multiply ramp, not a per-pixel computation: one
# vertical line plus one scaled strip per column is ~280 ops a frame, the same
# cost class as the 14-quad scheme, but with a CONTINUOUS edge. Fourteen 10px
# quads step the outline by up to 2px every 10px, and a 2px gold border broken
# by 2px steps is the same broken-stroke failure the type warp was refused for.
_ramp_cache = {}


def _ramp(h, lo):
    key = (h, lo)
    strip = _ramp_cache.get(key)
    if strip is None:
        strip = pygame.Surface((1, max(1, h)), pygame.SRCALPHA)
        for y in range(max(1, h)):
            k = int(round(255 * (1.0 - (1.0 - lo) * (y / max(1, h - 1)))))
            strip.set_at((0, y), (k, k, k, 255))
        _ramp_cache[key] = strip
    return strip


_sheen_cache = {}


def _sheen(w, h, peak):
    key = (w, h, peak)
    s = _sheen_cache.get(key)
    if s is None:
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        for y in range(h):
            pygame.draw.line(s, (255, 255, 255, int(peak * (1 - y / h) ** 2.4)),
                             (0, y), (w, y))
        _sheen_cache[key] = s
    return s


_word_cache = {}


def _word_surface():
    """START, rendered FLAT exactly once.

    The warp never touches the type. Sampling the word through the cloth
    column-by-column stair-steps the horizontal strokes of S, T, A and R at
    1px granularity, and a 3px stroke broken by 1px steps reads as a BROKEN
    stroke on a phone. The word rides the cloth as one rigid object instead:
    a whole-word integer y-offset plus a <=2deg tilt off the local normal.
    """
    if "w" in _word_cache:
        return _word_cache["w"]
    s = pygame.Surface((104, 36), pygame.SRCALPHA)
    _hud._tracked_label(s, "START", (52, 19), 24, color=CLOTH_SHADOW, track=2, alpha=150)
    _hud._tracked_label(s, "START", (52, 17), 24, color=GOLD_PALE, track=2, alpha=255)
    _word_cache["w"] = s
    return s


def _column(cloth, x, y0, y1, base, lo):
    y0i, y1i = int(round(y0)), int(round(y1))
    h = y1i - y0i
    if h <= 0:
        return
    lx = x - FOX
    pygame.draw.line(cloth, base, (lx, y0i - FOY), (lx, y1i - 1 - FOY))
    cloth.blit(_ramp(h, lo), (lx, y0i - FOY),
               special_flags=pygame.BLEND_RGBA_MULT)


def _build_cloth(t):
    """The warped flag on its own surface: field, form-shading, the reverse
    sliver at the curl, the hoist band, grommets, type and the gold border."""
    cloth = pygame.Surface((FW, FH), pygame.SRCALPHA)

    for x in range(HOIST_X, FLY_X):
        top, bot, tail_u, tail_l = _cloth_edges(x + 0.5, t)
        s = _wave_slope(x + 0.5, t)
        if x < BAND_X:
            # The doubled hoist band starts only 4 luma clear of the L70 floor,
            # so it gets a shallower ramp than the field or its own underside
            # would be the one part of the flag that drops out at night.
            base, lo = CLOTH_REVERSE, 0.99
        else:
            base = _mix(CLOTH_FIELD, CLOTH_CREST, s) if s >= 0 else \
                _mix(CLOTH_FIELD, CLOTH_TROUGH, -s)
            lo = 0.95
        base = tuple(min(255, int(round(c * 1.05))) for c in base)
        if tail_u is None:
            _column(cloth, x, top, bot, base, lo)
        else:
            _column(cloth, x, top, tail_u, base, lo)
            _column(cloth, x, tail_l, bot, base, lo)

    mask = pygame.Surface((FW, FH), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255),
                        [(px - FOX, py - FOY) for px, py in _outline(t)])

    # One top-down sheen so the cloth catches light as a single surface rather
    # than as 140 independent columns. NOT `store_cards.gloss_sweep`: that
    # helper blits its ramp with BLEND_ADD, which adds the source's full 255
    # RGB irrespective of the alpha ramp, and saturated this L100 teal to flat
    # white. Same curve, blended normally.
    cloth.blit(_sheen(FW, FH, 46), (0, 0))
    cloth.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    # The fly rolls over: a sliver of the REVERSE side, which is what makes the
    # top and bottom edges read as belonging to a curved sheet at 1x.
    for x in range(300, FLY_X):
        top, _b, tail_u, _tl = _cloth_edges(x + 0.5, t)
        limit = tail_u if tail_u is not None else top + 8
        y0 = int(round(top))
        y1 = int(round(min(top + 6.0 * _smooth((x - 300) / 26.0), limit)))
        lx = x - FOX
        for y in range(y0, y1):
            ly = y - FOY
            if 0 <= lx < FW and 0 <= ly < FH and cloth.get_at((lx, ly))[3] > 200:
                cloth.set_at((lx, ly), CLOTH_REVERSE)
        if y1 > y0 and 0 <= y1 - FOY - 1 < FH and cloth.get_at((lx, y1 - FOY - 1))[3] > 200:
            cloth.set_at((lx, y1 - FOY - 1), _mix(CLOTH_CREST, (255, 255, 255), 0.3))

    # Luff seam: the doubled tabling the grommets are punched through.
    pygame.draw.line(cloth, _mix(CLOTH_REVERSE, CLOTH_CREST, 0.45),
                     (BAND_X - FOX, 541 - FOY), (BAND_X - FOX, 603 - FOY), 1)
    for gy in (550, 573, 596):
        nail(cloth, 210 - FOX, gy - FOY, 3)

    word = _word_surface()
    dy = int(round(_wave(WORD_C[0], t)))
    rot = pygame.transform.rotozoom(word, -2.0 * _wave_slope(WORD_C[0], t), 1.0)
    cloth.blit(rot, rot.get_rect(
        center=(WORD_C[0] - FOX, WORD_C[1] + dy - FOY)).topleft)

    pts = [(px - FOX, py - FOY) for px, py in _outline(t)]
    # Stroked wide then re-clipped: a width-1 stroke rasterises differently
    # from the polygon fill along these diagonals, the same disagreement
    # `timber_board` handles this way.
    pygame.draw.polygon(cloth, GOLD_BRIGHT, pts, 3)
    cloth.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return cloth, mask


def _cleat(surf, cx, cy):
    """Timber cleat on the mast's left face — the fall has to belay somewhere,
    and the coil hanging off it is the only slack rope on the screen."""
    pad = timber_board(16, 7, seed=13, plain=True)
    surf.blit(pad, (cx - 8, cy - 3))
    for sgn in (-1, 1):
        pygame.draw.line(surf, T_EDGE, (cx, cy + 1), (cx + sgn * 8, cy - 4), 3)
        pygame.draw.line(surf, IRON, (cx, cy), (cx + sgn * 8, cy - 5), 2)
        pygame.draw.circle(surf, IRON_HI, (cx + sgn * 7, cy - 5), 1)
    for ex, ey, ew, eh in ((cx - 9, cy + 3, 18, 14), (cx - 6, cy + 12, 13, 11)):
        pygame.draw.ellipse(surf, ROPE_D, (ex, ey, ew, eh), 3)
        pygame.draw.ellipse(surf, ROPE, (ex + 1, ey + 1, ew - 2, eh - 2), 1)


def draw_start_coloursup(surf, tails):
    """colours-up — the chain's last rope stops being a mooring line and
    becomes a HALYARD: it reeves through the masthead block and the flag's
    luff is where the whole chain terminates. The swallowtail is the planks'
    V-notch rendered in cloth; the luff grommets are the plank nails.

    It is also the only soft, moving thing on a screen of timber, iron and
    rope, which is how the eye finds the thumb target without being told.
    """
    # Shrouds first: thin diagonals in place of the old fat timber brace, so
    # the corner is held down by lines rather than filled with lumber.
    for ex, ey in ((172, 614), (228, 616)):
        rope(surf, (201, 534), (ex, ey), sag=1, width=2)
        _iron_ring(surf, ex, ey, 3)

    step = timber_board(20, 10, seed=17, plain=True)
    step.fill((176, 176, 176, 255), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(step, (190, 602))

    mast = timber_board(8, MAST_FOOT_Y - MAST_TRUCK_Y, seed=7, plain=True)
    # Raked away from SETTINGS. A jack-staff, not a topmast: the truck stays
    # low enough that the cloth hangs entirely BELOW SETTINGS' bottom edge,
    # which is the only reason START is still the lowest control.
    mast = pygame.transform.rotozoom(mast, -4.0, 1.0)
    mr = mast.get_rect(center=(203, (MAST_TRUCK_Y + MAST_FOOT_Y) // 2))
    soft_shadow(surf, mr, "low", mask=mast)
    surf.blit(mast, mr.topleft)

    # The halyard: SETTINGS' right tail -> the masthead block -> the fall.
    rope(surf, tails[1], BLOCK, sag=6, width=3)
    _iron_ring(surf, *BLOCK, r=5)
    rope(surf, (198, 528), (192, 584), sag=2, width=3)

    cloth, mask = _build_cloth(RIPPLE)
    soft_shadow(surf, pygame.Rect(FOX, FOY, FW, FH), "raised", mask=mask)
    surf.blit(cloth, (FOX, FOY))

    # Head cringle: the flag is BENT ON to the halyard, not hung near it.
    pygame.draw.line(surf, ROPE_D, (203, 529), (208, 540), 3)
    pygame.draw.line(surf, ROPE, (203, 529), (208, 540), 1)

    _cleat(surf, 192, 586)
    return TAP_RECT


# ── Rendering ────────────────────────────────────────────────────────────────

def render_frame(phase, ripple, mode="flag"):
    global RIPPLE
    RIPPLE = ripple
    app = App()
    app._cooldown_t = 0.0
    app._fetch_pending = False
    app.state = STATE_MENU
    app.world = World()
    for _ in range(40):
        app.world.world_idle_tick(1 / 60)
    app.world.biome_time = phase * _biome.CYCLE_SECONDS
    app.world.weather.wetness = 0.0
    app.world.bird.frame_t = 0.0
    app.world.bird.x = PIP_CX
    app.world.bird.y = PIP_CY

    pal = _biome.palette_for_phase(phase)
    # Opaque, like the real display surface:  punches its sheave
    # hole with a (0,0,0,0) circle, which on a per-pixel-alpha target would
    # cut a real hole through the frame instead of reading as iron.
    surf = pygame.Surface((W, H))
    app.screen = surf
    app._draw_background(surf)
    foreground.draw_near_lane(surf, app.world.bg_scroll, pal, 0.0,
                              app.world.biome_time)

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
    surf.blit(house, (hx, hy))
    before = surf.copy()
    app.world.bird.draw(surf)
    pip = _bbox_diff(before, surf)
    chain = draw_signchain(surf)
    tails = chain.pop("_tails")
    if mode == "flag":
        draw_start_coloursup(surf, tails)
    elif mode == "base":
        draw_start_B(surf, tails)
    draw_profile_frame(surf)

    _hud._outlined_text(surf, "SKYBIT", (W // 2, 112), size=72, px=3,
                        shadow_offset=(2, 3))
    _hud._outlined_text(surf, "POCKET  SKY  FLYER", (W // 2, 168),
                        size=20, px=2, shadow_offset=(1, 2))
    return surf.copy(), pip


def _bbox_diff(a, b, tol=6):
    """Byte-for-byte the base script's Pip gate: the LUMA of the difference,
    thresholded — so the number published here is directly comparable to the
    one the base tool prints on its own render."""
    from PIL import Image, ImageChops
    ia = Image.frombytes("RGB", a.get_size(), pygame.image.tostring(a, "RGB"))
    ib = Image.frombytes("RGB", b.get_size(), pygame.image.tostring(b, "RGB"))
    box = ImageChops.difference(ia, ib).convert("L").point(
        lambda v: 255 if v > tol else 0).getbbox()
    return (box[0], box[1], box[2] - 1, box[3] - 1)


# ── Review sheet ─────────────────────────────────────────────────────────────
# Every panel is rendered in its OWN process. `foreground.draw_near_lane` and
# the sprite caches consume the global RNG lazily, so an in-process batch would
# give panel 2 a different ground band from panel 1 — and would stop the render
# being byte-comparable to a fresh run of the base tool.

SHEET_BG = (18, 20, 26)
SHEET_FG = (232, 236, 244)
SHEET_DIM = (150, 158, 172)


def _sheet_font(size, bold=False):
    return pygame.font.SysFont("dejavusans", size, bold=bold)


def _label(surf, text, x, y, size=15, color=SHEET_FG, bold=True):
    surf.blit(_sheet_font(size, bold).render(text, True, color), (x, y))


def _frame(mode, phase, ripple):
    """One panel, from a fresh interpreter."""
    import subprocess, tempfile
    p = os.path.join(tempfile.gettempdir(),
                     f"_cu_{mode}_{phase}_{ripple}.png")
    subprocess.run([sys.executable, os.path.abspath(__file__)],
                   env={**os.environ, "PYTHONHASHSEED": "0", "FRAME": mode,
                        "PHASE": str(phase), "RIPPLE": str(ripple), "OUT": p},
                   check=True, capture_output=True)
    return pygame.image.load(p)


def _greyscale(src):
    import numpy as np
    out = pygame.Surface(src.get_size())
    a = pygame.surfarray.array3d(src).astype(float)
    l = 0.299 * a[:, :, 0] + 0.587 * a[:, :, 1] + 0.114 * a[:, :, 2]
    pygame.surfarray.blit_array(out, np.dstack([l, l, l]).astype("uint8"))
    return out


def _crop(src, rect, scale=1):
    sub = src.subsurface(rect).copy()
    if scale != 1:
        sub = pygame.transform.scale(sub, (rect.width * scale, rect.height * scale))
    return sub


def _panel(sheet, img, x, y, title, sub=None, tcol=SHEET_FG):
    _label(sheet, title, x, y, 14, tcol)
    if sub:
        _label(sheet, sub, x + _sheet_font(14, True).size(title)[0] + 10, y + 1,
               12, SHEET_DIM, False)
    sheet.blit(img, (x, y + 20))
    pygame.draw.rect(sheet, (64, 70, 84),
                     (x - 1, y + 19, img.get_width() + 2, img.get_height() + 2), 1)
    return y + 20 + img.get_height()


def build_sheet(out_path):
    ph = [_frame("flag", p, 0.0) for p in (0.0, 0.20, 0.45, 0.65)]
    sway = [_frame("flag", 0.20, t) for t in (0.0, 1.3, 2.6)]
    base_b = _frame("base", 0.20, 0.0)
    quad = pygame.Rect(180, 468, 180, 172)

    MARG, GAP, LBL = 26, 16, 20
    content_w = 4 * W + 3 * GAP
    sheet_w = content_w + MARG * 2
    sheet_h = 82 + (LBL + H) + 40 + (LBL + H) + 40 + (LBL + H) + 46 + MARG
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill(SHEET_BG)
    _label(sheet, "colours-up  —  the launch flag        ROUND 1", MARG, 20, 25)
    _label(sheet, "START-as-one-object.  Base: tools/menu-design/launch_perch_start.py VARIANT=B.  "
                  "360x640 virtual canvas.  Every panel is 1x unless a panel says otherwise.",
           MARG, 52, 14, SHEET_DIM, False)

    y = 82
    names = ("dawn", "day", "dusk", "night")
    for i, p in enumerate((0.0, 0.20, 0.45, 0.65)):
        _panel(sheet, ph[i], MARG + i * (W + GAP), y,
               f"1x   PHASE {p:.2f}  ({names[i]})")

    y += LBL + H + 40
    x = MARG
    _panel(sheet, _greyscale(ph[1]), x, y, "GREYSCALE of the PHASE 0.20 frame")
    x += W + GAP
    _panel(sheet, base_b, x, y, "APPROVED BASE B", "reference — VARIANT=B PHASE=0.20", (198, 206, 220))
    x += W + GAP
    _panel(sheet, _crop(ph[1], quad), x, y, "START QUADRANT 1x", "x180-360 y468-640")
    _label(sheet, "the same quadrant at night (PHASE 0.65), 1x", x, y + 20 + quad.height + 12, 13, SHEET_DIM, False)
    sheet.blit(_crop(ph[3], quad), (x, y + 20 + quad.height + 32))
    pygame.draw.rect(sheet, (64, 70, 84),
                     (x - 1, y + 19 + quad.height + 32, quad.width + 2, quad.height + 2), 1)
    x += quad.width + GAP
    _panel(sheet, _crop(ph[1], quad, 3), x, y, "DETAIL 3x",
           "construction only — never a play size", (198, 206, 220))

    y += LBL + H + 40
    _label(sheet, "SWAY — the only concept on this screen that moves. Same frame, three points of the ripple cycle.",
           MARG, y, 16)
    for i, t in enumerate((0.0, 1.3, 2.6)):
        _panel(sheet, sway[i], MARG + i * (W + GAP), y + 8, f"1x   wave phase t = {t:.1f}s")
    x = MARG + 3 * (W + GAP)
    _label(sheet, "the same three, quadrant only, 1x", x, y + 8, 14)
    for i in range(3):
        sheet.blit(_crop(sway[i], quad), (x, y + 28 + i * (quad.height + 8)))
        pygame.draw.rect(sheet, (64, 70, 84),
                         (x - 1, y + 27 + i * (quad.height + 8), quad.width + 2, quad.height + 2), 1)

    y += LBL + H + 40
    _label(sheet,
           "flag Rect(204,532,140,82)   tap Rect(196,528,150,86)   masthead block y526   swallowtail bite 26px   "
           "START 24px track+2 = 88px on a 100px field, 6px each side",
           MARG, y + 2, 14, SHEET_DIM, False)
    _label(sheet,
           "teal field L100.1 / crest L143.5 / trough L79.1 / hoist band L74.0 against a backdrop of L36.6 day and "
           "L21.0 night — no cloth body below L74 at either pole.",
           MARG, y + 22, 14, SHEET_DIM, False)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    pygame.image.save(sheet, out_path)
    print("saved", out_path, sheet.get_size())


if __name__ == "__main__":
    _out = os.environ.get("OUT") or os.path.join(
        _ROOT, "docs", "main-menu", "harbour-post", "colours-up", "round_1.png")
    _mode = os.environ.get("FRAME")
    if _mode:
        _s, _p = render_frame(PHASE, RIPPLE, _mode)
        os.makedirs(os.path.dirname(_out), exist_ok=True)
        pygame.image.save(_s, _out)
    else:
        build_sheet(_out)
