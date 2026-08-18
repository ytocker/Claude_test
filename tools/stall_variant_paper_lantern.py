"""Stall-front concept `paper-lantern` — a backlit paper valance + a floor andon.

Design thesis: the stall is a night-market paper shop. The SIGN is a full-width
washi valance strung across the roof front — DARK resist-dyed letters on lit
paper (noren/kanban language), so the type reads by value inversion instead of
by adding another gold glare to a scene that already has one. The ITEM sits in
the open front of a grounded paper floor lantern (andon): a three-quarter shell,
never a box, whose warm paper back is one value step darker than the valance so
the hero — front-lit from the same low upper-left sun — stays the brightest
thing in the stall.

Value ladder is the whole concept, so it is enforced numerically:
    hero highlight  >  valance paper  >  lantern paper  >  stall interior
There is exactly ONE key light (low golden-hour sun, upper-left); every shadow
falls down-right, and the only glow in the scene is a capped bleed BEHIND the
valance that sells paper translucency without becoming a second key.

Tools-side exploration module: it installs itself onto the store_hub hook seam
and never touches the stall architecture (roof/awning/body/deck/stilts are
already drawn by draw_hut when these hooks fire).
"""
import pygame

import game.store_hub as sh
from game.store_hub import (
    m, font, vgrad, lerp_color, capped_glow, gradient_text,
    _glyph_base, _punch_contrast, _rim_light, _group_thumb,
    GOLD, GOLD_PALE, WOOD_HI, WOOD_MID, WOOD_LO, WOOD_EDGE,
    LABEL_KEY, STALL_DARK,
)


# Washi ladder. The valance is the brighter paper (it is backlit by sky), the
# lantern shell one step down (it only catches the sun), so the hero can sit
# above both without needing a rim hot enough to look like a second lamp.
PAPER_HI = (206, 168, 112)
PAPER_LO = (176, 136, 86)
LANT_HI = (186, 150, 100)
LANT_LO = (150, 116, 74)

# Resist-dyed ink: warm dark brown, deliberately NOT black and NOT gold — gold
# type here would compete with the balance capsule and the lagoon glitter.
INK = lerp_color(LABEL_KEY, WOOD_EDGE, 0.5)
CORD = (196, 168, 124)
FLANK_SHADE = lerp_color(WOOD_LO, STALL_DARK, 0.35)


def _px(v, scale, lo=1):
    """Logical px -> device px at this hut's scale, floored so hairlines survive."""
    return max(lo, int(m(v) * scale))


def _top_round(w, h, rad, top, bot):
    """Vertical gradient panel with only its TOP corners rounded — a paper shell
    stretched over a frame reads as square where it meets the floor."""
    body = vgrad(w, h, 0, top, bot)
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h),
                     border_top_left_radius=rad, border_top_right_radius=rad)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return body


# =============================================================================
# SIGN — the backlit washi valance.
# =============================================================================
def _sign(surf, ctx):
    cx = ctx["cx"]
    body_top = ctx["body_top"]
    scale = ctx["scale"]
    half_w, eave = ctx["half_w"], ctx["eave"]
    label = ctx["label"]

    pw = _px(96, scale)
    ph = _px(17, scale)
    bottom = body_top - _px(2, scale)
    # A 1px keyline authored at SS only survives the single downscale if it lands
    # on a WHOLE target pixel, so the panel's horizontal edges are snapped to even
    # device rows. Odd rows split each keyline across two output rows and halve it.
    bottom -= bottom % 2
    ph += ph % 2
    rect = pygame.Rect(cx - pw // 2, bottom - ph, pw, ph)

    # Translucency, not illumination: a low capped bleed BEHIND the paper, kept
    # above the awning seam and a whole hut-body away from the hero, so the
    # valance looks lit THROUGH rather than lit ON.
    for k in range(5):
        gx = rect.left + int(pw * (k + 0.5) / 5)
        capped_glow(surf, gx, rect.centery, _px(14, scale, 6), GOLD, 20, layers=8)

    # The valance hangs proud of the thatch, so its shadow is clipped to the
    # roof triangle — a cast shadow floating on open sky would break the light.
    roof = [(cx - half_w - eave, body_top), (cx + half_w + eave, body_top),
            (cx, ctx["roof_apex_y"])]
    off = _px(2, scale)
    shadow = pygame.Surface(rect.size, pygame.SRCALPHA)
    shadow.fill((14, 8, 4, 96))
    cast = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    cast.blit(shadow, (rect.x + off, rect.y + off))
    mask = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), roof)
    cast.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(cast, (0, 0))

    paper = vgrad(pw, ph, 0, PAPER_HI, PAPER_LO)
    # Backlight falls off toward the battens: the ends darken, so the panel has
    # ONE bright centre that the type sits in and the ends read as structure.
    fall = pygame.Surface((pw, ph), pygame.SRCALPHA)
    for x in range(pw):
        d = abs(x - (pw - 1) / 2) / ((pw - 1) / 2)
        v = 255 - int(46 * d ** 2.1)
        pygame.draw.line(fall, (v, v, v, 255), (x, 0), (x, ph))
    paper.blit(fall, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(paper, rect.topleft)

    # A hairline is authored in LOGICAL px and must survive the one downscale, so
    # keylines are m(1) flat rather than scale-shrunk into a half-pixel ghost.
    hair = max(1, m(1))
    key = pygame.Surface((pw, ph), pygame.SRCALPHA)
    pygame.draw.rect(key, (*GOLD_PALE, 200), (0, 0, pw, hair))
    pygame.draw.rect(key, (*GOLD_PALE, 200), (0, ph - hair, pw, hair))
    surf.blit(key, rect.topleft)

    # Bamboo batten pair closing the ends + the hairline top rail they carry:
    # the paper visibly HANGS from something rather than floating.
    bw = _px(2.5, scale, 2)
    bx = _px(47, scale)
    # the rail clears the gold keyline rather than overwriting it, or the top
    # edge loses half its value and the panel stops reading as bound at the top
    rail_y = rect.top + hair + 1
    pygame.draw.line(surf, WOOD_MID, (cx - bx, rail_y), (cx + bx, rail_y), hair)
    pygame.draw.line(surf, lerp_color(WOOD_HI, PAPER_HI, 0.3),
                     (cx - bx, rail_y - 1), (cx + bx, rail_y - 1), 1)
    for sgn in (-1, 1):
        x0 = cx + sgn * bx - bw // 2
        surf.blit(vgrad(bw, ph, 0, WOOD_MID, WOOD_LO), (x0, rect.top))
        pygame.draw.line(surf, WOOD_HI, (x0, rect.top), (x0, rect.bottom - 1), 1)
        pygame.draw.line(surf, WOOD_EDGE, (x0 + bw - 1, rect.top),
                         (x0 + bw - 1, rect.bottom - 1), 1)

    f = font(11 * scale)
    base = _glyph_base(label, f, m(0.6))
    tr = base.get_rect(center=(cx, rect.centery + max(1, hair // 2)))
    ink_sh = base.copy()
    ink_sh.fill((*lerp_color(PAPER_LO, INK, 0.55), 255),
                special_flags=pygame.BLEND_RGBA_MULT)
    ink_sh.set_alpha(90)
    surf.blit(ink_sh, (tr.x + hair, tr.y + hair))
    gradient_text(surf, label, f, tr.center,
                  lerp_color(INK, WOOD_LO, 0.18), INK,
                  weight=0, shadow=False, tracking=m(0.6))

    # One dyed lozenge centres each flank of paper so the slack either side of a
    # short word reads as composed margin, not as a sign that is simply too wide.
    lz = _px(2, scale, 2)
    fx = int((tr.width / 2 + bx - bw / 2) / 2)
    for sgn in (-1, 1):
        lx = cx + sgn * fx
        pygame.draw.polygon(surf, INK, [(lx, rect.centery - lz),
                                        (lx + lz, rect.centery),
                                        (lx, rect.centery + lz),
                                        (lx - lz, rect.centery)])


# =============================================================================
# ITEM — the grounded paper floor lantern (andon) the hero stands inside.
# =============================================================================
def _geom(ctx):
    """Every lantern part hangs off ONE metric set so the shell, the shadow it
    receives and the hero that casts it can never drift apart."""
    cx, deck_y, scale = ctx["cx"], ctx["deck_y"], ctx["scale"]
    sill = deck_y - m(8)
    pw, ph = _px(46, scale), _px(33, scale)
    foot_h = _px(3, scale, 2)
    return dict(
        cx=cx, scale=scale, sill=sill, foot_h=foot_h,
        awn_b=ctx["body_top"] + int(m(15) * scale),
        panel=pygame.Rect(cx - pw // 2, sill - foot_h - ph, pw, ph),
        fw=_px(5, scale, 3), hair=max(1, m(0.8)),
        box=int(m(30) * scale), base=deck_y - m(10),
    )


def _front_light(img, warm=(255, 216, 162), peak=52, ambient=18):
    """The ONE key, applied to the hero as a DIRECTIONAL additive ramp that is
    hottest at the upper-left and falls to ambient at the lower-right.

    A flat _punch_contrast alone lifts the whole silhouette evenly, which reads
    as a washed sticker AND still loses to warm paper at the shadow side; a
    directional ramp buys the same average lift while keeping modelling, so the
    hero sits IN the lantern's light instead of being pasted over it."""
    w, h = img.get_size()
    out = img.copy()
    for y in range(h):
        ty = y / max(1, h - 1)
        for x in range(w):
            r, g, b, a = out.get_at((x, y))
            if a == 0:
                continue
            t = max(0.0, 1.0 - (x / max(1, w - 1) * 0.55 + ty * 0.45))
            k = (ambient + peak * t ** 1.15) / 255.0
            out.set_at((x, y), (min(255, int(r + warm[0] * k)),
                                min(255, int(g + warm[1] * k)),
                                min(255, int(b + warm[2] * k)), a))
    return out


def _lantern(surf, ctx):
    cx, scale = ctx["cx"], ctx["scale"]
    g = _geom(ctx)
    sill, awn_b, panel = g["sill"], g["awn_b"], g["panel"]
    pw, ph = panel.w, panel.h
    fw, hair = g["fw"], g["hair"]

    # The ~22px of opening either side of the shell is answered with STRUCTURE:
    # two bamboo uprights the lantern paper is strung between. They are the dark
    # rests that let lit paper + hero read as one bright centre.
    ux = _px(38, scale)
    uw = _px(3.2, scale, 3)
    for sgn in (-1, 1):
        x0 = cx + sgn * ux - uw // 2
        col = pygame.Rect(x0, awn_b, uw, sill - awn_b)
        if sgn < 0:
            surf.blit(vgrad(uw, col.h, 0, WOOD_MID, WOOD_LO), col.topleft)
            pygame.draw.line(surf, WOOD_HI, (x0, col.top), (x0, col.bottom - 1), 1)
            # the one key grazes the near upright's upper third and dies out
            wedge = pygame.Surface((uw, col.h), pygame.SRCALPHA)
            for y in range(int(col.h * 0.55)):
                a = int(80 * (1 - y / (col.h * 0.55)) ** 1.5)
                pygame.draw.line(wedge, (255, 206, 150, a), (0, y), (uw, y))
            surf.blit(wedge, col.topleft)
        else:
            surf.blit(vgrad(uw, col.h, 0, lerp_color(WOOD_LO, STALL_DARK, 0.55),
                            STALL_DARK), col.topleft)
        pygame.draw.line(surf, WOOD_EDGE, (x0 + uw - 1, col.top),
                         (x0 + uw - 1, col.bottom - 1), 1)

    for f in (0.20, 0.50, 0.80):
        cy = int(panel.top + panel.h * f)
        for sgn in (-1, 1):
            x0 = cx + sgn * ux
            inner = x0 - sgn * uw // 2
            edge = cx + sgn * (pw // 2 + fw)
            pygame.draw.line(surf, (*CORD, 150), (inner, cy), (edge, cy), hair)
            for k in (-1, 1):
                pygame.draw.line(surf, (*CORD, 200),
                                 (x0 - uw // 2 - 1, cy + k * hair),
                                 (x0 + uw // 2 + 1, cy + k * hair), 1)

    # Warmth seat only — a capped bleed behind the shell so the lantern separates
    # from STALL_DARK. It sits BEHIND the paper, so it never lifts the hero, and
    # it is clipped to the opening so it cannot wash over the deck lip or the
    # side posts, which are hard walls of the stall architecture.
    in_half = ctx["half_w"] - m(8)
    old_clip = surf.get_clip()
    surf.set_clip(pygame.Rect(cx - in_half, awn_b, in_half * 2, sill - awn_b))
    capped_glow(surf, cx, panel.centery, int(pw * 0.62), GOLD, 22, layers=8)
    surf.set_clip(old_clip)

    for sgn in (-1, 1):
        ex = cx + sgn * pw // 2
        lean = _px(1.5, scale, 1)
        pygame.draw.polygon(surf, FLANK_SHADE, [
            (ex, panel.top + _px(2, scale)),
            (ex + sgn * fw, panel.top + _px(2, scale) + lean),
            (ex + sgn * fw, panel.bottom + lean),
            (ex, panel.bottom)])
        pygame.draw.line(surf, lerp_color(FLANK_SHADE, WOOD_HI, 0.35 if sgn < 0 else 0.10),
                         (ex + sgn * fw, panel.top + _px(2, scale) + lean),
                         (ex + sgn * fw, panel.bottom + lean), 1)

    surf.blit(_top_round(pw, ph, _px(6, scale, 3), LANT_HI, LANT_LO), panel.topleft)
    for k in range(1, 5):
        ry = panel.top + int(panel.h * k / 5)
        rib = pygame.Surface((pw, hair), pygame.SRCALPHA)
        rib.fill((*lerp_color(LANT_LO, WOOD_EDGE, 0.45), 140))
        surf.blit(rib, (panel.left, ry))
    pygame.draw.line(surf, lerp_color(LANT_HI, WOOD_EDGE, 0.30),
                     (panel.right - 1, panel.top + _px(6, scale, 3)),
                     (panel.right - 1, panel.bottom - 1), hair)

    foot = pygame.Rect(panel.left - _px(2, scale), sill - g["foot_h"],
                       pw + _px(4, scale), g["foot_h"])
    surf.blit(vgrad(foot.w, foot.h, 0, WOOD_HI, WOOD_LO), foot.topleft)
    pygame.draw.line(surf, WOOD_EDGE, (foot.left, foot.bottom - 1),
                     (foot.right - 1, foot.bottom - 1), 1)
    for sgn in (-1, 1):
        rx = cx + sgn * (pw // 2 - _px(4, scale))
        pygame.draw.line(surf, lerp_color(WOOD_LO, WOOD_EDGE, 0.5),
                         (rx, foot.top), (rx, foot.bottom - 1), 1)


def _hero(surf, ctx):
    g = _geom(ctx)
    scale, panel = g["scale"], g["panel"]

    src, _lb = _group_thumb(ctx["group"])
    w, h = src.get_size()
    s = g["box"] / max(w, h)
    img = pygame.transform.smoothscale(src, (max(1, int(w * s)), max(1, int(h * s))))
    img = _punch_contrast(img, boost=40)
    img = _front_light(img)
    r = img.get_rect(midbottom=(g["cx"], g["base"]))

    # The hero stands IN FRONT of lit paper, so the key must throw its shadow
    # ONTO that paper — down-right, clipped to the shell. Without it the item
    # reads as a silhouette cut out of a lantern; with it the paper is a lit
    # ground the item is planted on. This is the whole concept's load-bearing
    # beat, so it is measured, not eyeballed.
    sil = img.copy()
    sil.fill((8, 5, 3, 255), special_flags=pygame.BLEND_RGBA_MULT)
    step = _px(1.1, scale, 1)
    old_clip = surf.get_clip()
    surf.set_clip(pygame.Rect(panel.left, panel.top,
                              panel.w + g["fw"], panel.h + g["foot_h"]))
    for k, a in ((1, 76), (2, 58), (3, 42), (4, 26), (5, 14)):
        sil.set_alpha(a)
        surf.blit(sil, (r.x + k * step, r.y + k * step))
    surf.set_clip(old_clip)

    # Contact shadow: cast down-RIGHT across the lantern floor and onto the
    # sill, so the item is planted by the same sun that lights it.
    ao = pygame.Surface((int(r.width * 1.45), _px(7, scale, 4)), pygame.SRCALPHA)
    for i in range(4):
        a = int(120 * (1 - i / 4))
        pygame.draw.ellipse(ao, (12, 8, 4, a),
                            (i * 2, i, ao.get_width() - i * 4, ao.get_height() - i * 2))
    surf.blit(ao, (r.centerx - ao.get_width() // 2 + _px(3, scale),
                   r.bottom - ao.get_height() // 2))

    surf.blit(_rim_light(img), r.topleft, special_flags=pygame.BLEND_ADD)
    surf.blit(img, r.topleft)


def _item(surf, ctx):
    _lantern(surf, ctx)
    _hero(surf, ctx)


def install():
    sh.STALL_SIGN_HOOK = _sign
    sh.STALL_ITEM_HOOK = _item
