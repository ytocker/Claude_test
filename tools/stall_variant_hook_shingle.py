"""Stall-front concept `hook-shingle` — the open-air hung market stall.

Thesis: nothing is behind glass. The category name rides a carved timber
shingle swinging from the thatch on two twisted rope drops, and the goods
hang in open air from a brass hook-rail slung under the awning. The read is
a working market: stock on hooks, spare rings and rope on the flanks, one
low golden-hour sun raking in from the upper left.

Installed as a tools-side variant so the exploration never edits the stall
architecture — draw_hut still owns roof/awning/body/deck/stilts; these hooks
only repaint the sign and the goods presentation inside the opening.
"""
import math

import pygame

import game.store_hub as sh
from game.store_hub import (m, font, vgrad, lerp_color, gradient_text,
                            capped_glow, _glyph_base, _group_thumb,
                            _punch_contrast, _rim_light,
                            WOOD_HI, WOOD_MID, WOOD_LO, WOOD_EDGE,
                            STALL_DARK, LABEL_KEY, GOLD, GOLD_PALE, GOLD_DEEP,
                            GOLD_A_TOP, GOLD_A_BOT)


# One low sun, upper-left: every catch light in this concept sits on a
# top/left edge and every shadow is thrown down-right from it.
TILT_SIGN = 2.0
TILT_ITEM = 6.0
PLANK_TOP = (58, 38, 20)
PLANK_BOT = (34, 21, 11)
BRASS_HI = (206, 162, 74)
BRASS_LO = (96, 66, 24)


def _rope(surf, p0, p1, thick, ticks=True):
    """A twisted two-strand rope: a WOOD_MID core with the lay caught on its
    upper-left flank and shaded on its lower-right, plus alternating cross
    ticks so the twist survives the downscale as texture rather than noise."""
    x0, y0 = p0
    x1, y1 = p1
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    nx, ny = -uy, ux
    if nx > 0:
        nx, ny = -nx, -ny
    off = max(1.0, thick / 2.0 - 0.5)
    pygame.draw.line(surf, WOOD_MID, p0, p1, thick)
    pygame.draw.line(surf, WOOD_HI, (x0 + nx * off, y0 + ny * off),
                     (x1 + nx * off, y1 + ny * off), 1)
    pygame.draw.line(surf, WOOD_EDGE, (x0 - nx * off, y0 - ny * off),
                     (x1 - nx * off, y1 - ny * off), 1)
    if not ticks:
        return
    step = max(2.0, thick * 1.6)
    n = int(L / step)
    for i in range(n):
        t = (i + 0.5) * step
        bx, by = x0 + ux * t, y0 + uy * t
        col = WOOD_EDGE if i % 2 else lerp_color(WOOD_HI, WOOD_MID, 0.35)
        pygame.draw.line(surf, col,
                         (bx + nx * off - ux * 0.8, by + ny * off - uy * 0.8),
                         (bx - nx * off + ux * 0.8, by - ny * off + uy * 0.8), 1)


def _plank(label, bw, bh, scale):
    """The carved name shingle as its own surface so the whole board — face,
    chamfer, keyline, catch light and gilt type — rotates as one object."""
    ch = max(2, int(m(3) * scale))
    poly = [(0, 0), (bw - 1, 0), (bw - 1, bh - 1 - ch), (bw - 1 - ch, bh - 1),
            (ch, bh - 1), (0, bh - 1 - ch)]
    plank = pygame.Surface((bw, bh), pygame.SRCALPHA)
    plank.blit(vgrad(bw, bh, 0, PLANK_TOP, PLANK_BOT), (0, 0))

    grain = pygame.Surface((bw, bh), pygame.SRCALPHA)
    for i, fy in enumerate((0.22, 0.46, 0.74)):
        gy = int(bh * fy)
        a = 46 if i != 1 else 30
        pygame.draw.line(grain, (24, 14, 6, a), (int(bw * 0.06), gy),
                         (int(bw * 0.94), gy + (1 if i % 2 else 0)), 1)
    plank.blit(grain, (0, 0))

    # the chamfer is the one face the low sun cannot reach, so it reads as a
    # bevelled edge rather than a painted stripe
    cb = max(2, int(m(2.5) * scale))
    bev = pygame.Surface((bw, cb), pygame.SRCALPHA)
    for y in range(cb):
        a = int(150 * (y / max(1, cb - 1)) ** 0.7)
        pygame.draw.line(bev, (16, 9, 4, a), (0, y), (bw, y))
    plank.blit(bev, (0, bh - cb))

    mask = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), poly)
    plank.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    f = font(11 * scale)
    base = _glyph_base(label, f, m(0.6))
    ink = base.get_bounding_rect()
    cy = bh // 2 + (base.get_height() // 2 - ink.centery)
    gradient_text(plank, label, f, (bw // 2, cy), GOLD_A_TOP, GOLD_A_BOT,
                  weight=m(1.0 * scale), keyline=LABEL_KEY, kw=m(1.0),
                  shadow=False, tracking=m(0.6))

    kw = max(1, int(m(1.2) * scale))
    pygame.draw.polygon(plank, WOOD_EDGE, poly, kw)
    lit = pygame.Surface((bw, bh), pygame.SRCALPHA)
    lw = max(1, int(m(1.0) * scale))
    pygame.draw.line(lit, (*WOOD_HI, 210), (kw, kw), (bw - 1 - kw, kw), lw)
    pygame.draw.line(lit, (*WOOD_HI, 150), (kw, kw), (kw, bh - 1 - ch), lw)
    plank.blit(lit, (0, 0))
    return plank


def sign_hook(surf, ctx):
    """Hang the carved shingle from the thatch: two rope drops seated in gilt
    eyes, a soft shadow thrown down-right onto the roof, and the board itself
    canted 2 degrees so it reads as swinging, not glued to the gable."""
    cx = ctx["cx"]
    scale = ctx["scale"]
    body_top = ctx["body_top"]
    half_w, eave = ctx["half_w"], ctx["eave"]
    roof_h = body_top - ctx["roof_apex_y"]
    span = half_w + eave

    f = font(11 * scale)
    tw = _glyph_base(ctx["label"], f, m(0.6)).get_width()
    bw = tw + 2 * int(m(8) * scale)
    top_y = body_top - int(m(16) * scale)
    bot_y = body_top - int(m(2) * scale)
    bh = bot_y - top_y

    plank = _plank(ctx["label"], bw, bh, scale)
    rot = pygame.transform.rotate(plank, TILT_SIGN)
    # seat the board by its TILTED envelope so the cant can never drop a
    # corner across the awning seam the sign must stay above
    rect = rot.get_rect()
    rect.centerx = cx
    rect.bottom = bot_y - max(1, int(m(0.5) * scale))
    c = rect.center

    th = math.radians(TILT_SIGN)
    cos_t, sin_t = math.cos(th), math.sin(th)

    def edge_pt(u):
        dy = -bh / 2.0
        return (c[0] + u * cos_t + dy * sin_t, c[1] - u * sin_t + dy * cos_t)

    def rake_y(px):
        return body_top - roof_h * (1.0 - min(1.0, abs(px - cx) / span))

    # the gable narrows as it rises, so the outermost hang points the brief
    # asks for leave the rope with no visible length at all; walk the drops
    # inboard only until each rope reads as a rope.
    u_max = bw / 2.0 - m(6) * scale
    min_drop = int(m(8) * scale)
    u = u_max
    while u > bw * 0.16:
        pl, pr = edge_pt(-u), edge_pt(u)
        if min(pl[1] - rake_y(pl[0]), pr[1] - rake_y(pr[0])) >= min_drop:
            break
        u -= 1.0

    rope_t = max(m(1.5), int(m(1.7) * scale))
    eye_r = max(2, int(m(1.6) * scale))
    for s in (-1, 1):
        p = edge_pt(s * u)
        ay = rake_y(p[0])
        anchor = (p[0], ay + eye_r * 0.4)
        _rope(surf, anchor, p, rope_t)
        pygame.draw.circle(surf, (14, 8, 4), (int(anchor[0]), int(ay)), eye_r + 1)
        pygame.draw.circle(surf, GOLD_DEEP, (int(anchor[0]), int(ay)), eye_r, 1)

    sil = rot.copy()
    sil.fill((0, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)
    d = max(2, int(m(2) * scale))
    shs = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    sil.set_alpha(90)
    shs.blit(sil, (rect.x + d, rect.y + d))
    sil.set_alpha(40)
    shs.blit(sil, (rect.x + d + 1, rect.y + d + 2))
    # the board overhangs the rake, so clip its cast shadow to the thatch —
    # a shadow floating on open sky would flatten the whole gable
    roof = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(roof, (255, 255, 255, 255),
                        [(cx - span, body_top), (cx + span, body_top),
                         (cx, ctx["roof_apex_y"])])
    shs.blit(roof, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(shs, (0, 0))
    surf.blit(rot, rect.topleft)


def _back_wall(inner, w, h):
    """Stall interior as a lit box: warm timber gloom in the sun-side upper
    left falling to near-black in the shaded lower right."""
    inner.blit(vgrad(w, h, 0, lerp_color(WOOD_MID, STALL_DARK, 0.55),
                     STALL_DARK), (0, 0))
    ramp = pygame.Surface((w, h), pygame.SRCALPHA)
    for x in range(w):
        a = int(150 * (x / max(1, w - 1)) ** 1.15)
        pygame.draw.line(ramp, (*STALL_DARK, a), (x, 0), (x, h))
    inner.blit(ramp, (0, 0))


def _sun_shaft(inner, w, h, die_x):
    """A soft slab of low sun entering the top-left of the opening and dying
    out before it reaches the goods — the item stays the brightest thing."""
    shaft = pygame.Surface((w, h), pygame.SRCALPHA)
    pts = [(w * 0.00, 0), (w * 0.30, 0), (w * 0.56, h * 0.78), (w * 0.24, h * 0.78)]
    cxp = sum(p[0] for p in pts) / 4.0
    cyp = sum(p[1] for p in pts) / 4.0
    layers = 5
    for k in range(layers):
        s = 1.0 - k * 0.07
        poly = [(cxp + (px - cxp) * s, cyp + (py - cyp) * s) for px, py in pts]
        lay = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.polygon(lay, (*GOLD_PALE, 40 // layers + 1), poly)
        shaft.blit(lay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    fade = pygame.Surface((w, h), pygame.SRCALPHA)
    for x in range(w):
        t = min(1.0, max(0.0, (x - die_x * 0.45) / max(1.0, die_x * 0.55)))
        pygame.draw.line(fade, (255, 255, 255, int(255 * (1.0 - t) ** 1.2)),
                         (x, 0), (x, h))
    vf = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        a = int(255 * (1.0 - (y / max(1, h - 1)) ** 1.5))
        pygame.draw.line(vf, (255, 255, 255, a), (0, y), (w, y))
    fade.blit(vf, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    shaft.blit(fade, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    inner.blit(shaft, (0, 0))


def _sill(inner, w, h, scale):
    """The counter board at the foot of the opening. Without it the stall has
    no floor for the goods to hang OVER, and a contact shadow thrown onto
    STALL_DARK is a shadow nobody can see."""
    sh_h = max(4, int(m(5) * scale))
    top = h - sh_h
    inner.blit(vgrad(w, sh_h, 0, lerp_color(WOOD_MID, WOOD_LO, 0.45),
                     WOOD_EDGE), (0, top))
    lip = pygame.Surface((w, 1), pygame.SRCALPHA)
    for x in range(w):
        lip.set_at((x, 0), (*WOOD_HI, int(190 * (1.0 - x / max(1, w - 1)) ** 1.2)))
    inner.blit(lip, (0, top))
    # blitted, not drawn: pygame.draw would WRITE alpha 120 into the wall and
    # punch a translucent slot through the stall interior
    ao = pygame.Surface((w, 1), pygame.SRCALPHA)
    ao.fill((0, 0, 0, 120))
    inner.blit(ao, (0, top - 1))
    return top


def _hook(inner, x, y, r, col, lit):
    """A bare J-hook hanging off the rail — near-silhouette, but given the same
    upper-left catch as everything else so it reads as an object in the gloom
    rather than a smudge."""
    tk = max(2, r // 2)
    pygame.draw.line(inner, col, (x, y), (x, y + r), tk)
    pygame.draw.arc(inner, col, (x - r, y + r - r // 2, r * 2, r * 2),
                    math.radians(200), math.radians(350), tk)
    pygame.draw.line(inner, lit, (x - tk // 2 - 1, y), (x - tk // 2 - 1, y + r), 1)


def item_hook(surf, ctx):
    """Goods in open air: a brass hook-rail lashed post-to-post, the hero
    hanging from a rope loop and gilt ring on the centre hook, and working
    stock (a coiled hank, a spare ring, two bare hooks) filling the flanks."""
    cx, deck_y = ctx["cx"], ctx["deck_y"]
    scale, group = ctx["scale"], ctx["group"]
    half_w, body_top = ctx["half_w"], ctx["body_top"]

    ol = cx - (half_w - m(8))
    ot = body_top + int(m(15) * scale)
    w = 2 * (half_w - m(8))
    h = (deck_y - m(8)) - ot
    inner = pygame.Surface((w, h), pygame.SRCALPHA)

    # ---- goods first, as geometry only: the lighting behind them keys off
    # where the hero actually lands.
    src, _lb = _group_thumb(group)
    sw, shh = src.get_size()
    box = int(m(40) * scale)
    s = box / max(sw, shh)
    img = pygame.transform.smoothscale(
        src, (max(1, int(sw * s)), max(1, int(shh * s))))
    img = _punch_contrast(img)
    img = pygame.transform.rotate(img, TILT_ITEM)
    irect = img.get_rect()
    irect.centerx = w // 2
    irect.bottom = (deck_y - m(11)) - ot

    _back_wall(inner, w, h)
    _sun_shaft(inner, w, h, max(4, irect.left))
    sill_top = _sill(inner, w, h, scale)

    rail_y = (body_top + int(m(16) * scale)) - ot
    rt = max(m(1.6), int(m(1.8) * scale))
    shs = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.line(shs, (0, 0, 0, 90), (0, rail_y + rt + 1),
                     (w, rail_y + rt + 2), max(1, rt - 1))
    inner.blit(shs, (0, 0))
    rail = pygame.Rect(0, rail_y, w, rt)
    inner.blit(vgrad(w, rt, 0, BRASS_HI, BRASS_LO), rail.topleft)
    # one light means the rail cannot be a uniform bright bar across the whole
    # opening — it burns brass at the sun end and sinks to gloom at the other,
    # which also keeps it from out-shouting the goods in a squint
    fall = pygame.Surface((w, rt), pygame.SRCALPHA)
    for x in range(w):
        a = int(130 * (x / max(1, w - 1)) ** 0.9)
        pygame.draw.line(fall, (*STALL_DARK, a), (x, 0), (x, rt))
    inner.blit(fall, rail.topleft)
    cat = pygame.Surface((w, 1), pygame.SRCALPHA)
    for x in range(w):
        a = int(150 * (1.0 - x / max(1, w - 1)) ** 1.6)
        cat.set_at((x, 0), (*GOLD_PALE, a))
    inner.blit(cat, (0, rail_y))

    # cord lashings at the post inner faces — the rail has to be tied to
    # something or it reads as a floating line
    lash = max(1, int(m(1.3) * scale))
    for side in (0, 1):
        for k in range(3):
            lx = (k * lash * 2 + lash) if side == 0 else (w - 1 - k * lash * 2 - lash)
            pygame.draw.line(inner, lerp_color(WOOD_MID, WOOD_LO, 0.3),
                             (lx, rail_y - lash - 1), (lx + 1, rail_y + rt + lash + 1),
                             lash)
            pygame.draw.line(inner, WOOD_EDGE, (lx + lash // 2, rail_y - lash - 1),
                             (lx + 1 + lash // 2, rail_y + rt + lash + 1), 1)

    # ---- flank stock. The sun side is bright enough to silhouette against,
    # the shade side is not — so the left flank goes DARKER than its wall and
    # the right flank goes lighter. Same tone family either way, both still
    # well under the hero.
    lit = lerp_color(WOOD_HI, WOOD_MID, 0.4)
    left_c = lerp_color(WOOD_EDGE, STALL_DARK, 0.25)
    right_c = lerp_color(WOOD_LO, WOOD_MID, 0.45)
    hx = w // 2 - int(m(32) * scale)
    rr = max(3, int(m(4.5) * scale))
    ring_w = max(1, int(m(1.2) * scale))
    pygame.draw.circle(inner, left_c, (hx, rail_y + rr + 1), rr, ring_w)
    pygame.draw.arc(inner, lit,
                    (hx - rr, rail_y + 1, rr * 2, rr * 2),
                    math.radians(60), math.radians(170), 1)
    hank_y = rail_y + rr * 2 + 2
    hank_r = max(4, int(m(6) * scale))
    for k in range(3):
        band = (hx - hank_r, hank_y + k * max(2, hank_r // 3),
                hank_r * 2, max(3, hank_r))
        pygame.draw.ellipse(inner, left_c, band, max(1, int(m(1.0) * scale)))
        pygame.draw.arc(inner, lit, band, math.radians(60), math.radians(160), 1)
    for dxs in (int(m(26) * scale), int(m(36) * scale)):
        _hook(inner, w // 2 + dxs, rail_y + rt, max(3, int(m(3.5) * scale)),
              right_c, lerp_color(WOOD_LO, WOOD_MID, 0.5))

    # ---- hero: capped glow only, so the gold bloom can never white out
    capped_glow(inner, irect.centerx, irect.centery + int(m(2) * scale),
                int(m(21) * scale), GOLD, 30, layers=9)

    # contact shadow on the sill, thrown down-right, sold as floating stock
    sh_s = pygame.Surface((w, h), pygame.SRCALPHA)
    ex = irect.centerx + int(m(3) * scale)
    ey = max(irect.bottom + max(2, int(m(1.5) * scale)), sill_top + 2)
    # widest/faintest ring FIRST: pygame.draw writes alpha rather than
    # compositing it, so an inner-out loop would leave only the faint pass
    for k in range(3, -1, -1):
        a = int(100 * (1 - k / 4.0))
        rx = int(irect.w * 0.40) + k * 2
        ry = max(2, int(m(1.6) * scale)) + k
        pygame.draw.ellipse(sh_s, (0, 0, 0, a), (ex - rx, ey - ry, rx * 2, ry * 2))
    inner.blit(sh_s, (0, 0))

    inner.blit(_rim_light(img), irect.topleft, special_flags=pygame.BLEND_ADD)
    inner.blit(img, irect.topleft)

    # ---- hanging hardware last: a square opening this shallow lets a tall
    # item's shoulder reach the rail, and a ring swallowed by the goods stops
    # reading as a hang at all — so the ring clasps in FRONT, on the centre
    # hook just left of the item's balance point, and the cord only shows
    # where the goods actually leave room for it.
    ax = irect.centerx - int(irect.w * 0.10)
    ay = irect.bottom
    col = max(0, min(img.get_width() - 1, ax - irect.left))
    for yy in range(irect.h):
        if img.get_at((col, yy))[3] > 24:
            ay = irect.top + yy
            break
    ring_r = max(3, int(m(3.2) * scale))
    ring_c = (ax, rail_y + rt // 2)
    cord_top = ring_c[1] + ring_r - 1
    if ay - cord_top > max(2, int(m(1.5) * scale)):
        _rope(inner, (ring_c[0], cord_top), (ax, ay + 2),
              max(m(1.5), int(m(1.6) * scale)), ticks=False)
    pygame.draw.circle(inner, (12, 8, 4), ring_c, ring_r + 1,
                       max(1, int(m(1.6) * scale)))
    pygame.draw.circle(inner, GOLD_PALE, ring_c, ring_r,
                       max(1, int(m(1.3) * scale)))
    pygame.draw.arc(inner, GOLD_DEEP,
                    (ring_c[0] - ring_r, ring_c[1] - ring_r, ring_r * 2, ring_r * 2),
                    math.radians(200), math.radians(340),
                    max(1, int(m(1.0) * scale)))
    surf.blit(inner, (ol, ot))


def install():
    sh.STALL_SIGN_HOOK = sign_hook
    sh.STALL_ITEM_HOOK = item_hook
