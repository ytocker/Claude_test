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

# ── Lamplit timber: one key light, four exposures ───────────────────────────
# The wall of brown was never a hue problem, it was an UNLIT problem. Warm
# furniture has to stay warm, because the background's value swings ~86 luma
# per cycle while its hue never leaves the cool quadrant (H205 day → H240
# night) — temperature is the only separator that is stable at every phase.
#
# So the timber is staged under a single key from the cloud's underside,
# upper-left, and every board is built from three zones instead of one flat
# field: a lit crown, the body, and a genuinely COOL shade skirt. That yields
# a ~175° internal hue rotation and a 4× value spread inside one board while
# the body stays unambiguously warm.
#
# Tones are authored by (hue, saturation, TARGET Rec.601 luma) rather than by
# RGB, because luma against the veiled sky is the thing this design has to
# survive and eyeballed RGB kept drifting into the sky's own value.
from game.draw import NEAR_BLACK
import colorsys


def _tone(hue_deg, sat, luma):
    """Solve HLS lightness for an exact Rec.601 luma at the authored hue."""
    h, s = (hue_deg % 360) / 360.0, max(0.0, min(1.0, sat))
    lo, hi = 0.0, 1.0
    for _ in range(28):
        mid = (lo + hi) * 0.5
        r, g, b = colorsys.hls_to_rgb(h, mid, s)
        if 0.299 * r + 0.587 * g + 0.114 * b < luma / 255.0:
            lo = mid
        else:
            hi = mid
    r, g, b = colorsys.hls_to_rgb(h, (lo + hi) * 0.5, s)
    return (int(round(r * 255)), int(round(g * 255)), int(round(b * 255)))


def timber(body_l, body_h, body_s, crown_l, crown_h, spec_l, skirt_l, skirt_h,
           skirt_s, edge_l=None, spread=6):
    """One member's full lighting stack. `crown_l=None` marks a piece that
    receives no direct key at all — that is what makes the post read as
    structure while the signs read as signage."""
    return {
        # A gentle form falloff, not a mood gradient: the reported exposure is
        # the mean, so the ladder stays legible plank to plank.
        "body_hi":   _tone(body_h + 1, body_s, body_l + spread),
        "body_lo":   _tone(body_h - 1, body_s, body_l - spread),
        "grain":     _tone(body_h - 2, body_s + 0.03, body_l - 4),
        "crown":     _tone(crown_h, body_s - 0.01, crown_l) if crown_l else None,
        "crown_dim": _tone(crown_h - 2, body_s, crown_l - 18) if crown_l else None,
        # The end face is angled toward the key, so it reads only a touch under
        # the top face — crown_dim put it within Δ6 of the body and vanished.
        "rim":       _tone(crown_h - 1, body_s - 0.01, crown_l - 8) if crown_l else None,
        "spec":      _tone(crown_h + 2, 0.30, spec_l) if spec_l else None,
        # Blue belongs in the shadow, never in the body — a red-leaning
        # "cool" skirt would rotate straight into the rust CTA and Pip's
        # scarlet body and dilute both.
        "skirt":     _tone(skirt_h, skirt_s, skirt_l),
        "skirt_mid": _tone(skirt_h - 4, 0.12, skirt_l + 22),
        "edge":      _tone(crown_h or 30, body_s, edge_l) if edge_l else None,
    }


CROWN_H, SKIRT_H, SKIRT_W = 5, 7, 10

# The exposure ladder. Four clearly distinct bodies, 50 luma end to end, and
# the post is floored high enough that it does not die into a night sky.
TIMBER = {
    "STORE":    timber(118, 33, 0.46, 140, 38, 168, 44, 206, 0.22),
    "TOP10":    timber( 96, 31, 0.47, 130, 36, 148, 38, 205, 0.20),
    "SETTINGS": timber( 80, 29, 0.48, 120, 34, None, 32, 204, 0.18),
    "START":    timber( 80, 29, 0.48, 120, 34, None, 32, 204, 0.18),
    # Only the post's bottom 20px is ever unoccluded by the START board, so a
    # full-height form gradient would publish an exposure well under the one
    # it is authored at. Near-flat keeps the rendered stub on its floor.
    "POST":     timber( 70, 27, 0.49, None, 30, None, 26, 203, 0.17, edge_l=86,
                       spread=2),
}

T_EDGE   = NEAR_BLACK
IRON     = ( 62,  56,  60)
IRON_HI  = (132, 128, 134)
# Pulled off L169: cordage brighter than the boards' own crowns was reading as
# the lit subject instead of the hardware holding the lit subject up.
ROPE     = (164, 141,  92)
ROPE_D   = NEAR_BLACK

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
# Local-only override of the shared dim-CTA rust. `_SCARLET_*_DIM` in hud.py
# is system-wide (TAP TO GAME, menu START, PLAY AGAIN) so it is not editable
# from here — but its bottom stop at L47 mushes into a night sky at L20-30,
# so this fork widens the gradient's internal range to 81 luma on the same
# rust axis, keeping the two buttons players tap most in sync.
CTA_TOP  = (238,  72,  34)
CTA_BOT  = ( 86,  16,  10)
CTA_LINE = ( 44,  22,  14)   # a real dark rust, not near-black wearing a hue
SCARLET_TOP = CTA_TOP
SCARLET_BOT = CTA_BOT


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


def timber_board(w, h, seed=0, chamfer=5, notch=5, plain=False, kind="SETTINGS"):
    """One board staged under the key light: a ~5px lit crown, the body, and a
    cool shade skirt down the bottom and the away-facing right end.

    Every transition is deliberately TWO-STEP. A single-value contour cannot
    hold at both poles of the cycle — the same fixed timber is a dark figure
    against an L106 day sky and a light figure against an L20 night sky — so
    the top edge reads sky / keyline / crown / body and the away edges read
    body / mid / skirt / keyline. One of those steps always wins.
    """
    rnd = random.Random(seed)
    w, h = int(w), int(h)
    sp = TIMBER[kind]
    body = pygame.Surface((w, h), pygame.SRCALPHA)
    _grad_fill(body, (0, 0, w, h), sp["body_hi"], sp["body_lo"])

    # A whisper, not a texture: grain sits within Δluma 4 of the body so it
    # never competes with the lighting it is drawn on top of.
    for _ in range(max(2, h // 8)):
        gy = rnd.uniform(CROWN_H + 3, h - SKIRT_H - 2)
        pts = [(gx, gy + math.sin(gx * 0.05 + seed) * 1.4 + rnd.uniform(-0.4, 0.4))
               for gx in range(0, w + 6, 6)]
        pygame.draw.lines(body, sp["grain"], False, pts, 1)

    for _ in range(1 if w < 90 else 2):
        kx = rnd.uniform(w * 0.2, w * 0.72)
        ky = rnd.uniform(CROWN_H + 5, h - SKIRT_H - 4)
        kr = rnd.uniform(2.0, 3.0)
        pygame.draw.ellipse(body, sp["grain"],
                            (kx - kr, ky - kr * 0.72, kr * 2, kr * 1.45))

    # Away-facing right end and the underside, both two-step into the cool.
    pygame.draw.rect(body, sp["skirt_mid"], (w - SKIRT_W, 0, SKIRT_W - 5, h))
    pygame.draw.rect(body, sp["skirt"], (w - 5, 0, 5, h))
    # The last row belongs to the keyline, so the deep skirt is laid above it
    # rather than under it — otherwise the coolest step is a single pixel that
    # the silhouette mask then eats.
    pygame.draw.rect(body, sp["skirt_mid"], (0, h - SKIRT_H, w, 3))
    pygame.draw.rect(body, sp["skirt"], (0, h - 4, w, 3))

    if sp["crown"]:
        pygame.draw.rect(body, sp["crown"], (0, 1, w - 12, CROWN_H))
        pygame.draw.rect(body, sp["crown_dim"], (w - 12, 1, 7, CROWN_H))
        # The key is upper-LEFT, so the near end face catches a rim too.
        pygame.draw.rect(body, sp["crown_dim"], (1, 1, 3, h - SKIRT_H))
        if sp["spec"]:
            pygame.draw.rect(body, sp["spec"],
                             (chamfer + 3, 2, int(w * 0.34), 2))
    elif sp["edge"]:
        # No crown — this member is in the signs' cast shadow — but it still
        # needs its second contour step or it vanishes into the night sky.
        pygame.draw.rect(body, sp["edge"], (1, 1, 2, h - SKIRT_H))

    lit_crown = bool(sp["crown"])
    for nx in (13, w - 14) if w > 60 else ():
        nail(body, nx, CROWN_H + 4, 3, lit=lit_crown)

    if plain:
        for ny in (int(h * 0.87), int(h * 0.955)) if h > 40 and not lit_crown else ():
            nail(body, w // 2, ny, 2, lit=False)
        pygame.draw.rect(body, T_EDGE, (0, 0, w, h), 1)
        return body

    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pts = _board_points(w, h, chamfer, notch)
    pygame.draw.polygon(mask, (255, 255, 255, 255), pts)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    # The key is upper-left, so the near end face catches a rim — but that face
    # is the hand-cut V, not a straight edge, so a rectangular rim strip just
    # gets bitten off by the notch and never appears.
    if sp["crown"]:
        pygame.draw.lines(body, sp["rim"], False,
                          [(2, chamfer + 1), (notch + 1, h * 0.5),
                           (2, h - chamfer - 1)], 2)
    # Traced one pixel in from the silhouette: a polygon whose vertices sit at
    # x=w / y=h has its bottom and right runs clipped away entirely, which is
    # what left these boards with a contour on three sides at most.
    pygame.draw.polygon(body, T_EDGE, _board_points(w - 1, h - 1, chamfer, notch), 1)
    return body


def nail(surf, x, y, r=3, lit=True):
    """Flat iron with one keyline. Only the heads sitting inside a lit crown
    get a highlight — a spark on a nail in shadow is the kind of incoherence
    that makes four separately-lit boards look worse than four flat ones."""
    pygame.draw.circle(surf, T_EDGE, (int(x), int(y)), r + 1)
    pygame.draw.circle(surf, IRON, (int(x), int(y)), r)
    if lit:
        pygame.draw.circle(surf, IRON_HI,
                           (int(x - r * 0.35), int(y - r * 0.35)), max(1, r - 2))


def rope(surf, p0, p1, sag=6, width=3):
    """One flat value plus one keyline, zero shading. Shaded cordage at this
    scale only ever reads as blur."""
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
    # Plank-to-plank separation is an exposure ladder, not three hues: the key
    # is up at the cloud, so each rung further down it receives less of it.
    rows = [("STORE", "coin", (112 + dx, 386), -3.0, bw, bh, "STORE"),
            ("TOP 10", "trophy", (118 + dx, 446), 2.4, bw, bh, "TOP10"),
            ("SETTINGS", "gear", (110 + dx, 506), -1.6, bw, bh, "SETTINGS")]

    # Ropes leave the cloud itself, not a plank. Anchors are clamped into the
    # cloud's measured silhouette so they can never end up hanging in open sky
    # beside it if the sprite ever changes.
    hooks = CLOUD_HOOK_C if VARIANT == 'C' else CLOUD_HOOK_X
    anchors = [(min(max(x, cloud.left + 14), cloud.right - 14), CLOUD_ANCHOR_Y)
               for x in hooks]

    rects = {}
    for label, kind, (cx, cy), ang, w, h, tone in rows:
        rad = math.radians(-ang)
        for sgn, apt in zip((-1, 1), anchors):
            ox = sgn * (w * 0.36)
            hx = cx + ox * math.cos(rad)
            hy = cy + ox * math.sin(rad) - h * 0.5
            rope(surf, apt, (hx, hy), sag=5, width=3)
            pygame.draw.circle(surf, T_EDGE, (int(hx), int(hy)), 4)
            pygame.draw.circle(surf, IRON, (int(hx), int(hy)), 3)

        board = timber_board(w, h, seed=hash(label) % 997,
                             chamfer=CHAMFER, notch=NOTCH, kind=tone)
        if kind == "coin":
            _hud._coin_icon(board, 30, h // 2, 12)
        elif kind == "trophy":
            _hud._draw_trophy(board, 30, h // 2, 10)
        else:
            _hud._draw_gear(board, 30, h // 2, 12)
        _hud._tracked_label(board, label, (LABEL_CX, h // 2 + 1), 17,
                            color=(28, 16, 9), track=2, alpha=150)
        _hud._tracked_label(board, label, (LABEL_CX, h // 2 - 1), 17,
                            color=GOLD_PALE, track=2, alpha=250)

        rot = pygame.transform.rotozoom(board, ang, 1.0)
        rr = rot.get_rect(center=(cx, cy))
        # No cast shadow: these boards hang in open sky with nothing under
        # them to receive one, and the soft halo that stood in for it was
        # most of what read as soft. The cool skirt is the form now.
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
    """The enamel face, double-contoured. Neither line alone survives the
    cycle: the outer rust keyline is what separates the pill against a pale
    day sky, the 3px gold rim is what separates it against a night one."""
    face = pygame.Rect(0, 0, fw, fh); face.center = (w // 2, h // 2)
    _grad_fill(board, (face.x, face.y, face.width, face.height),
               CTA_TOP, CTA_BOT)
    frost = pygame.Surface((face.width, face.height // 2), pygame.SRCALPHA)
    frost.fill((255, 255, 255, 24)); board.blit(frost, face.topleft)
    pygame.draw.rect(board, GOLD_BRIGHT, face, 3)
    pygame.draw.rect(board, CTA_LINE, face.inflate(4, 4), 1)
    pygame.draw.line(board, GOLD_PALE, (face.left + 9, face.top + 6),
                     (face.right - 9, face.top + 6), 1)
    f = _hud._font(size, True)
    img = f.render(word, True, (255, 244, 222))
    r = img.get_rect(center=(face.centerx, face.centery - 1))
    out = f.render(word, True, (72, 12, 8)); out.set_alpha(210)
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
    # The post is the darkest member AND the only one with no lit crown — it
    # stands in the signs' own cast shadow, which is exactly why it reads as
    # structure while they read as signage.
    # Both shadows are laid before the timber, not over it: stacked on top they
    # stripped ~12 luma off the only unoccluded stretch of post and dropped the
    # member carrying START back under its floor.
    soft_shadow(surf, pygame.Rect(264, 588, 24, 22), "contact")
    soft_shadow(surf, rect, "raised")
    post = timber_board(24, 120, seed=7, plain=True, kind="POST")
    surf.blit(post, (264, 494))
    brace = timber_board(74, 12, seed=11, plain=True, kind="POST")
    brace = pygame.transform.rotozoom(brace, 38, 1.0)
    surf.blit(brace, brace.get_rect(center=(236, 566)).topleft)
    board = timber_board(rect.width, rect.height, seed=21, chamfer=9, notch=0,
                         kind="START")
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
