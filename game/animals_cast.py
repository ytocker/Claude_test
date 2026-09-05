"""Promenade ANIMALS — a varied dog pool + street critters.

A 9-strong 'dog' pool over one parametric drawer — mostly strays and mongrels
with the odd recognisable house dog, because dog sightings are rare enough that
each one has to read as a fresh animal. Breed lives entirely in the OUTLINE
(proportion + tail + ear + muzzle + ragged-edge attrs: a village dog's give-away
is the broken outline, never the coat colour). Plus a 7-strong 'critter' pool
(sitting cat / pecking hen / pigeon trio / waddling duck / stilt-leg crane /
rooting piglet / long-ear rabbit), each with its own t-driven idle motion.
Sibling to the ped_cast / day_cast / food_stalls families.

Drawn CRISP at native size (no smoothscale). Night cooling toward (54,64,96) with
an extra pull on pale coats so nothing breaches the 150 luma cap — the gold coin
stays the sole brightest element. Pure-Pygame / pygbag-safe.
"""
from __future__ import annotations

import math

import pygame

from game.foreground_props import _mix, _shade, _clamp
from game import foreground_variants as fv

NIGHT_GLOW_CAP = 150
DOG_H = 12      # shoulder height of a 1.0-build dog (~2/3 of an adult, PED_H 18)


def _luma(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def _retint(col, night):
    """Cool toward the night ground band (matches ped_cast._retint_person), with a
    second stronger pull on any PALE coat still above the cap — so a near-white
    coat (+ its highlight) can never out-glow the gold coin at night."""
    if night <= 0.05:
        return col
    out = _mix(col, (78, 88, 118), min(0.38, 0.28 * night + 0.14))
    if _luma(out) > NIGHT_GLOW_CAP:
        over = (_luma(out) - NIGHT_GLOW_CAP) / max(1.0, 255 - NIGHT_GLOW_CAP)
        out = _mix(out, (66, 76, 104), min(0.78, 0.5 + over))
    return out


def _hi(c, d, night):
    """A highlight d above c, but clamped under the night cap so _shade can't push
    a pale night coat past the coin."""
    out = _shade(c, d)
    if night > 0.05 and _luma(out) > NIGHT_GLOW_CAP:
        out = _mix(out, (66, 76, 104), 0.65)
    return out


# ── DOGS — one shared drawer; breed = the OUTLINE. Feet on base_y, facing LEFT ──

def draw_dog(surf, cx, base_y, v, night, t):
    P, A = v.palette, v.attrs
    pf = lambda c: _retint(c, night)
    coat = pf(P["coat"])
    coat_dk = pf(P.get("coat_dk", _shade(P["coat"], -40)))
    coat_lt = _hi(coat, 16, night)
    belly = pf(P.get("belly", _shade(P["coat"], 22)))
    nose_c = pf((40, 32, 30))

    build = A.get("build", 1.0)
    legf = A.get("leg", 1.0)
    lengthf = A.get("length", 1.0)
    chestf = A.get("chest", 1.0)
    headf = A.get("head", 1.0)
    fluffy = A.get("fluffy", False)
    scruffy = A.get("scruffy", False)
    ruffcrop = A.get("ruffcrop", False)
    mane = A.get("mane", False)
    skirtcoat = A.get("skirtcoat", False)
    tail = A.get("tail", "low")
    ear = A.get("ear", "drop")
    muzzle = A.get("muzzle", "med")

    sh_h = max(8, int(DOG_H * build))
    leg_h = max(2, int(sh_h * 0.40 * legf))
    body_h = max(5, int((sh_h - leg_h) * 0.92 * chestf))
    body_w = max(9, int(sh_h * 1.15 * lengthf))
    head_r = max(3, int(sh_h * 0.27 * headf))

    ground = int(base_y)
    body_top0 = ground - leg_h - body_h
    body_left = cx - body_w // 2
    body_right = cx + body_w // 2
    body_cy0 = body_top0 + body_h // 2

    gait = math.sin(t * 6.0)
    bob = int(round(abs(gait) * (sh_h * 0.05)))
    body_top = body_top0 - bob
    body_cy = body_cy0 - bob

    leg_col = coat_dk
    paw = _shade(coat_dk, -16)
    fx_front = body_left + max(2, body_w // 5)
    fx_rear = body_right - max(2, body_w // 5)
    swing = gait * max(1.5, body_w * 0.11)
    lw = max(2, sh_h // 6)
    for fx, ph in ((fx_front, 1), (fx_rear, -1)):
        for off, s in ((0, ph), (2, -ph)):
            sw = swing * s
            top_y = body_cy + body_h // 5
            foot_x = int(fx + off + sw)
            pygame.draw.line(surf, leg_col, (fx + off, top_y), (foot_x, ground), lw)
            pygame.draw.line(surf, paw, (foot_x - 1, ground), (foot_x + 1, ground), lw)

    tx = body_right - 1
    sway = int(round(gait * 1.4))
    tcol = coat
    tw = max(2, sh_h // 5)
    if tail == "low":
        pygame.draw.lines(surf, tcol, False, [
            (tx - 1, body_cy), (tx + int(sh_h * 0.55), body_cy + int(sh_h * 0.22)),
            (tx + int(sh_h * 0.80), body_cy + int(sh_h * 0.60) + sway)], tw)
        pygame.draw.lines(surf, coat_dk, False, [
            (tx - 1, body_cy), (tx + int(sh_h * 0.55), body_cy + int(sh_h * 0.22)),
            (tx + int(sh_h * 0.80), body_cy + int(sh_h * 0.60) + sway)], 1)
    elif tail == "streetlow":
        # A tail hung almost straight DOWN off the rump — the universal "this dog
        # is not anybody's pet" read, and the cheapest way to re-dress a shipped
        # breed as a stray without touching its proportions.
        pygame.draw.lines(surf, tcol, False, [
            (tx - 1, body_cy + 1), (tx + int(sh_h * 0.22), body_cy + int(sh_h * 0.45)),
            (tx + int(sh_h * 0.14) + sway, body_cy + int(sh_h * 0.85))], max(2, sh_h // 6))
        pygame.draw.circle(surf, coat_dk,
                           (tx + int(sh_h * 0.14) + sway, body_cy + int(sh_h * 0.85)), 1)
    elif tail == "sickle":
        # Carried up and curved back over the loin but NOT touching it — reads
        # between the hound's sabre and the spitz's tight ring.
        pygame.draw.lines(surf, tcol, False, [
            (tx - 1, body_cy), (tx + int(sh_h * 0.5), body_cy - int(sh_h * 0.25)),
            (tx + int(sh_h * 0.42), body_top - int(sh_h * 0.45) + sway)], max(2, sh_h // 6))
        pygame.draw.circle(surf, coat_lt,
                           (tx + int(sh_h * 0.42), body_top - int(sh_h * 0.45) + sway), 1)
    elif tail == "lowpup":
        pygame.draw.lines(surf, tcol, False, [
            (tx - 1, body_cy), (tx + int(sh_h * 0.32), body_cy + int(sh_h * 0.20)),
            (tx + int(sh_h * 0.38), body_cy + sway)], tw)
    elif tail == "plume":
        ax, ay = tx - 1, body_cy
        pygame.draw.lines(surf, tcol, False, [
            (ax, ay), (ax + int(sh_h * 0.45), body_top - int(sh_h * 0.1)),
            (ax + int(sh_h * 0.3), body_top - int(sh_h * 0.55)),
            (ax - int(sh_h * 0.1) + sway, body_top - int(sh_h * 0.75))],
            max(3, sh_h // 4))
        pygame.draw.lines(surf, coat_lt, False, [
            (ax + int(sh_h * 0.45), body_top - int(sh_h * 0.1)),
            (ax + int(sh_h * 0.3), body_top - int(sh_h * 0.55))], 1)
    elif tail == "tightcurl":
        cxr, cyr = tx - 1, body_top - 1
        rr = max(2, int(sh_h * 0.26))
        pygame.draw.arc(surf, tcol, (cxr - rr, cyr - rr, rr * 2, rr * 2),
                        math.radians(-60), math.radians(250), max(2, sh_h // 5))
        pygame.draw.arc(surf, coat_lt, (cxr - rr, cyr - rr, rr * 2, rr * 2),
                        math.radians(20), math.radians(160), 1)
    elif tail == "stub":
        pygame.draw.line(surf, tcol, (tx - 1, body_cy), (tx + 2 + sway, body_top - 1), max(2, sh_h // 4))

    body_rect = pygame.Rect(body_left, body_top, body_w, body_h)
    pygame.draw.ellipse(surf, coat, body_rect)
    pygame.draw.ellipse(surf, coat_dk, body_rect, 1)
    pygame.draw.arc(surf, belly, body_rect, math.radians(200), math.radians(340), 1)
    pygame.draw.arc(surf, coat_lt, body_rect, math.radians(35), math.radians(145), 1)
    if fluffy:
        for bxp in range(body_left + 2, body_right - 1, 2):
            pygame.draw.circle(surf, coat_lt, (bxp, body_top + 1), 1)
    if scruffy:
        # RAGGED OUTLINE: alternating tufts standing off the back line and a torn
        # hip. Colour says nothing at 10px, but a broken edge says "stray" instantly
        # — and it survives the crisp far-lane downscale because it IS the outline.
        # 2px wide: a 1px tuft is the first thing a nearest downscale throws away,
        # which left the far lane with a smooth back and no stray read at all.
        for k, bxp in enumerate(range(body_left + 2, body_right - 1, 3)):
            up = 1 + (k % 2)
            pygame.draw.line(surf, coat_dk, (bxp, body_top + 1), (bxp - 1, body_top - up), 2)
        pygame.draw.line(surf, coat_dk, (body_right - 2, body_cy),
                         (body_right + 1, body_cy + 2), 2)
        pygame.draw.line(surf, coat_dk, (body_left + 2, body_top + body_h - 2),
                         (body_left, body_top + body_h + 1), 2)
    if ruffcrop:
        # A stray's ruff wears away unevenly — thick over the withers, rubbed back
        # to the skin on the throat side. The flat-bottomed, back-heavy collar is
        # an ASYMMETRIC outline event, which is what stops a re-dressed breed from
        # reading as nothing more than the same dog in a duller colour.
        rr = max(3, int(head_r * 1.35))
        rx = body_left + max(1, head_r // 2)
        ry = body_top + max(1, int(body_h * 0.30))
        collar = [(rx - rr * 0.55, ry - rr * 0.85), (rx + rr * 0.85, ry - rr * 0.75),
                  (rx + rr * 0.75, ry + rr * 0.25), (rx - rr * 0.15, ry + rr * 0.35),
                  (rx - rr * 0.95, ry - rr * 0.05)]
        pygame.draw.polygon(surf, _mix(coat, belly, 0.30), collar)
        pygame.draw.polygon(surf, coat_dk, collar, 1)
        for k in range(3):
            sx0 = rx - rr * 0.45 + rr * 0.5 * k
            pygame.draw.line(surf, coat_dk, (sx0, ry - rr * 0.8),
                             (sx0 + 1, ry - rr * 1.35), 2)
    if skirtcoat:
        # A fringed coat falling to the deck: the legs disappear and the dog reads
        # as a moving loaf. Nothing else in the pool loses its legs.
        hem = ground - max(1, leg_h // 4)
        skirt = [(body_right, body_top + body_h // 2)]
        step = max(2, body_w // 6)
        xx = body_right
        k = 0
        # The fringe alternates phase with the stride: without it a legless coat
        # slides along like a dropped sack instead of walking under its own fur.
        wob = 1 if gait > 0 else 0
        while xx > body_left:
            skirt.append((xx, hem - ((k + wob) % 2)))
            xx -= step
            k += 1
        skirt.append((body_left, body_top + body_h // 2))
        pygame.draw.polygon(surf, coat, skirt)
        pygame.draw.lines(surf, coat_dk, False, skirt[1:-1], 1)

    hx = body_left - max(1, int(head_r * 0.3))
    hy = body_top + max(1, int(body_h * 0.1)) - max(1, int(sh_h * 0.18))
    pygame.draw.polygon(surf, coat, [
        (body_left + head_r, body_top), (body_left + 1, body_top + body_h - 1),
        (hx, hy + head_r), (hx - 1, hy - head_r // 2)])
    if fluffy:
        pygame.draw.circle(surf, coat_lt, (body_left + 1, body_cy), max(2, head_r - 1))
    if mane:
        # The ruff is drawn BEFORE the head so the head sits inside it: the whole
        # front end becomes one big shaggy disc, which is the chow read in two
        # dozen pixels.
        mr = max(3, int(head_r * 1.5))
        pygame.draw.circle(surf, _mix(coat, belly, 0.35), (hx + head_r // 2, hy + 1), mr)
        for k in range(8):
            a = k * math.pi / 4
            pygame.draw.line(surf, coat_dk,
                             (hx + head_r // 2 + math.cos(a) * (mr - 1), hy + 1 + math.sin(a) * (mr - 1)),
                             (hx + head_r // 2 + math.cos(a) * (mr + 1), hy + 1 + math.sin(a) * (mr + 1)), 1)
    pygame.draw.circle(surf, coat, (hx, hy), head_r)
    pygame.draw.circle(surf, coat_dk, (hx, hy), head_r, 1)

    if muzzle == "long":
        mlen = int(head_r * 1.4); mh = max(2, head_r - 1)
    elif muzzle == "short":
        mlen = max(2, int(head_r * 0.6)); mh = max(2, head_r)
    elif muzzle == "flat":
        mlen = 1; mh = max(2, head_r)
    else:
        mlen = max(3, int(head_r * 1.0)); mh = max(2, head_r - 1)
    mx = hx - head_r // 2 - mlen
    pygame.draw.polygon(surf, coat, [
        (hx - head_r // 3, hy - mh // 2), (mx, hy - 1),
        (mx, hy + 1), (hx - head_r // 3, hy + mh // 2 + 1)])
    pygame.draw.circle(surf, nose_c, (mx, hy), 1)
    pygame.draw.circle(surf, (28, 22, 20), (hx - head_r // 3, hy - head_r // 3), 1)

    if ear == "prick":
        pygame.draw.polygon(surf, coat_dk, [
            (hx + 1, hy - head_r), (hx + head_r + 1, hy - head_r - 2), (hx + head_r, hy - head_r // 3)])
    elif ear == "bigprick":
        pygame.draw.polygon(surf, coat_dk, [
            (hx, hy - head_r), (hx + head_r, hy - int(head_r * 2.2)), (hx + head_r + 1, hy - head_r // 3)])
        pygame.draw.polygon(surf, _mix(coat, belly, 0.5), [
            (hx + 1, hy - head_r), (hx + head_r - 1, hy - int(head_r * 1.7)), (hx + head_r, hy - head_r // 2)])
    elif ear == "drop":
        pygame.draw.polygon(surf, coat_dk, [
            (hx + head_r // 2, hy - head_r + 1), (hx + head_r + 1, hy - head_r // 2), (hx + head_r - 1, hy + head_r)])
    elif ear == "halfflop":
        # One ear up, one folded over at the tip: an asymmetric head outline.
        # Sub-pixel at street size (a 4x-zoom bonus, not the read) — the stray is
        # carried by its hung tail, dust coat and ragged back line.
        pygame.draw.polygon(surf, coat_dk, [
            (hx, hy - head_r), (hx + head_r - 1, hy - int(head_r * 1.9)), (hx + head_r, hy - head_r // 3)])
        pygame.draw.polygon(surf, _shade(coat_dk, -14), [
            (hx + head_r * 0.6, hy - head_r), (hx + head_r * 1.6, hy - int(head_r * 1.3)),
            (hx + head_r * 0.9, hy - int(head_r * 0.2))])
        pygame.draw.line(surf, _shade(coat_dk, -22),
                         (hx + head_r * 1.6, hy - int(head_r * 1.3)),
                         (hx + head_r * 2.0, hy - int(head_r * 0.6)), 1)
    elif ear == "longdrop":
        sway2 = int(round(gait * 0.8))
        for depth, fx_off, shade in ((2.7, 1, 0), (2.4, -1, -16)):
            ex0 = hx + (head_r // 2 if fx_off > 0 else -head_r // 3)
            tip_y = hy + int(head_r * depth)
            pygame.draw.polygon(surf, _shade(coat_dk, shade), [
                (ex0, hy - head_r + 1),
                (hx + head_r + 1, hy - head_r // 3),
                (hx + (head_r if fx_off > 0 else 1) + sway2, tip_y),
                (ex0 - 1, hy + head_r // 2)])


# ── CRITTERS — one shared drawer dispatched by kind; each its own motion ───────

def draw_critter(surf, cx, base_y, v, night, t):
    kind = v.attrs.get("kind", "hen")
    {"cat": _crit_cat, "hen": _crit_hen, "pigeons": _crit_pigeons,
     "duck": _crit_duck, "crane": _crit_crane, "piglet": _crit_piglet,
     "rabbit": _crit_rabbit}[kind](surf, cx, base_y, v, night, t)


def _crit_cat(surf, cx, base_y, v, night, t):
    pf = lambda c: _retint(c, night)
    P = v.palette
    fur = pf(P.get("body", (120, 112, 104)))
    fur_dk = pf(P.get("body_dk", _shade(P["body"], -34)))
    fur_lt = _hi(fur, 18, night)
    ear_in = pf(P.get("accent", (150, 110, 110)))
    g = int(base_y)
    body_h = 7
    body = pygame.Rect(cx - 3, g - body_h, 6, body_h)
    pygame.draw.ellipse(surf, fur, body)
    pygame.draw.ellipse(surf, fur_dk, body, 1)
    pygame.draw.ellipse(surf, fur, (cx - 4, g - 3, 8, 3))
    hx, hy = cx - 1, g - body_h - 1
    pygame.draw.circle(surf, fur, (hx, hy), 3)
    pygame.draw.circle(surf, fur_dk, (hx, hy), 3, 1)
    swiv = int(round(math.sin(t * 1.3) * 1))
    for ex in (-2, 2):
        pygame.draw.polygon(surf, fur, [
            (hx + ex, hy - 1), (hx + ex + (1 if ex < 0 else -1), hy - 4 + (swiv if ex > 0 else 0)),
            (hx + ex + (2 if ex < 0 else -2), hy - 1)])
        pygame.draw.line(surf, ear_in, (hx + ex, hy - 1), (hx + ex + (1 if ex < 0 else -1), hy - 3), 1)
    pygame.draw.circle(surf, (40, 70, 50), (hx - 1, hy), 1)
    pygame.draw.circle(surf, fur_lt, (hx - 2, hy + 1), 1)
    flick = int(round(math.sin(t * 2.2) * 2))
    pygame.draw.lines(surf, fur, False, [
        (cx + 3, g - 1), (cx + 5, g - 2), (cx + 5, g - 5),
        (cx + 3 + flick, g - 6 - max(0, flick))], 2)
    pygame.draw.circle(surf, fur_dk, (cx + 3 + flick, g - 6 - max(0, flick)), 1)


def _crit_hen(surf, cx, base_y, v, night, t):
    pf = lambda c: _retint(c, night)
    P = v.palette
    body = pf(P.get("body", (200, 188, 170)))
    body_dk = pf(P.get("body_dk", _shade(P["body"], -38)))
    body_lt = _hi(body, 16, night)
    comb = pf(P.get("accent", (176, 70, 60)))
    beak = pf((196, 158, 80))
    leg = pf((176, 140, 88))
    g = int(base_y)
    peck = max(0.0, math.sin(t * 3.2))
    bw, bh = 8, 6
    by = g - bh - 1
    pygame.draw.ellipse(surf, body, (cx - bw // 2, by, bw, bh))
    pygame.draw.ellipse(surf, body_dk, (cx - bw // 2, by, bw, bh), 1)
    pygame.draw.arc(surf, body_lt, (cx - bw // 2, by, bw, bh), math.radians(40), math.radians(150), 1)
    pygame.draw.polygon(surf, body_dk, [
        (cx + bw // 2 - 1, by + 1), (cx + bw // 2 + 3, by - 3), (cx + bw // 2 + 2, by + 2)])
    pygame.draw.polygon(surf, body, [
        (cx + bw // 2 - 1, by + 1), (cx + bw // 2 + 2, by - 1), (cx + bw // 2, by + 3)])
    for lx in (cx - 1, cx + 2):
        pygame.draw.line(surf, leg, (lx, by + bh - 1), (lx, g), 1)
        pygame.draw.line(surf, leg, (lx - 1, g), (lx + 1, g), 1)
    hx0, hy0 = cx - bw // 2, by
    hx = hx0 - 1 - int(peck * 1)
    hy = hy0 - 2 + int(peck * 5)
    pygame.draw.line(surf, body, (hx0, by + 1), (hx, hy), 2)
    pygame.draw.circle(surf, body, (hx, hy), 2)
    pygame.draw.circle(surf, comb, (hx, hy - 2), 1)
    pygame.draw.circle(surf, comb, (hx - 1, hy + 1), 1)
    pygame.draw.polygon(surf, beak, [(hx - 2, hy), (hx - 4, hy), (hx - 2, hy + 1)])
    pygame.draw.circle(surf, (24, 18, 16), (hx - 1, hy - 1), 1)


def _crit_pigeons(surf, cx, base_y, v, night, t):
    pf = lambda c: _retint(c, night)
    P = v.palette
    body = pf(P.get("body", (140, 142, 152)))
    body_dk = pf(P.get("body_dk", _shade(P["body"], -34)))
    neck = pf(P.get("accent", (110, 120, 150)))
    beak = pf((120, 110, 110))
    g = int(base_y)
    specs = ((-3, 0.0, False, True), (3, 0.6, True, False), (6, 1.1, False, False))
    for dx, ph, hops, lead in specs:
        bx = cx + dx
        peck = max(0.0, math.sin(t * 3.0 + ph * 6))
        hop = max(0.0, math.sin(t * 1.6 + ph * 6)) if hops else 0.0
        lift = int(hop * 4)
        gb = g - lift
        bw, bh = (7, 5) if lead else (5, 4)
        by = gb - bh - 1
        pygame.draw.ellipse(surf, body, (bx - bw // 2, by, bw, bh))
        pygame.draw.ellipse(surf, body_dk, (bx - bw // 2, by, bw, bh), 1)
        pygame.draw.line(surf, body_dk, (bx + bw // 2 - 1, by + 1), (bx + bw // 2 + 2, by + 2), 1)
        if lift <= 0:
            for lx in (bx - 1, bx + 1):
                pygame.draw.line(surf, beak, (lx, by + bh - 1), (lx, g), 1)
        hr = 2 if lead else 1
        hx = bx - bw // 2 - int(peck * 1)
        hy = by - 1 + int(peck * 3)
        pygame.draw.line(surf, neck, (bx - bw // 2 + 1, by + 1), (hx, hy), 2)
        pygame.draw.circle(surf, body, (hx, hy), hr)
        pygame.draw.polygon(surf, beak, [(hx - hr, hy), (hx - hr - 1, hy), (hx - hr, hy + 1)])
        pygame.draw.circle(surf, (24, 20, 22), (hx - 1, hy - 1), 1)
    for sx in (cx - 2, cx + 4):
        pygame.draw.circle(surf, pf((150, 130, 90)), (sx, g), 1)


def _crit_duck(surf, cx, base_y, v, night, t):
    pf = lambda c: _retint(c, night)
    P = v.palette
    body = pf(P.get("body", (210, 204, 190)))
    body_dk = pf(P.get("body_dk", _shade(P["body"], -36)))
    body_lt = _hi(body, 16, night)
    head_c = pf(P.get("accent", (96, 120, 96)))
    bill = pf((196, 168, 90))
    foot = pf((200, 150, 80))
    g = int(base_y)
    waddle = math.sin(t * 3.4)
    rock = int(round(waddle * 1))
    bobh = int(round(math.sin(t * 3.4 + 1.2) * 1))
    bw, bh = 9, 4
    by = g - bh - 1
    pygame.draw.ellipse(surf, body, (cx - bw // 2, by, bw, bh))
    pygame.draw.ellipse(surf, body_dk, (cx - bw // 2, by, bw, bh), 1)
    pygame.draw.arc(surf, body_lt, (cx - bw // 2, by, bw, bh), math.radians(30), math.radians(150), 1)
    pygame.draw.polygon(surf, body, [
        (cx + bw // 2 - 1, by + 1), (cx + bw // 2 + 2, by - 2), (cx + bw // 2, by + 2)])
    for lx, phase in ((cx - 1, 0), (cx + 2, math.pi)):
        step = int(round(math.sin(t * 3.4 + phase) * 1))
        pygame.draw.line(surf, foot, (lx, by + bh - 1), (lx + step, g), 1)
        pygame.draw.line(surf, foot, (lx + step - 1, g), (lx + step + 1, g), 1)
    hx = cx - bw // 2 - 1 + rock
    hy = by - 3 + bobh
    pygame.draw.line(surf, head_c, (cx - bw // 2 + 1, by + 1), (hx, hy), 2)
    pygame.draw.circle(surf, head_c, (hx, hy), 2)
    pygame.draw.polygon(surf, bill, [(hx - 2, hy), (hx - 4, hy - 1), (hx - 4, hy + 1), (hx - 2, hy + 1)])
    pygame.draw.circle(surf, (22, 20, 18), (hx - 1, hy - 1), 1)


def _crit_crane(surf, cx, base_y, v, night, t):
    """A tall wading bird: two stilt legs, a small high body, a long S-neck and a
    spear bill, standing about twice the duck's height. It is the only VERTICAL
    critter, so it never competes with the low pecking clumps. 2-beat: the neck
    folds down to preen, then unfurls; one leg lifts on the slower half."""
    pf = lambda c: _retint(c, night)
    P = v.palette
    body = pf(P.get("body", (188, 186, 178)))
    body_dk = pf(P.get("body_dk", _shade(P["body"], -40)))
    dark = pf(P.get("accent", (86, 84, 92)))
    bill = pf((178, 150, 92))
    leg = pf((120, 110, 96))
    g = int(base_y)
    dip = max(0.0, math.sin(t * 1.7))
    lift = max(0.0, math.sin(t * 0.9 + 1.4))
    body_h = 5
    by = g - 11
    for k, lx in enumerate((cx - 1, cx + 2)):
        foot_y = g - (2 if (k == 1 and lift > 0.75) else 0)
        knee_y = by + body_h + 2
        pygame.draw.line(surf, leg, (lx, by + body_h - 1), (lx, knee_y), 1)
        pygame.draw.line(surf, leg, (lx, knee_y), (lx + (1 if k else -1), foot_y), 1)
        if foot_y >= g:
            pygame.draw.line(surf, leg, (lx - 1, g), (lx + 1, g), 1)
    bw = 8
    pygame.draw.ellipse(surf, body, (cx - bw // 2, by, bw, body_h))
    pygame.draw.ellipse(surf, body_dk, (cx - bw // 2, by, bw, body_h), 1)
    pygame.draw.polygon(surf, dark, [
        (cx + bw // 2 - 1, by + 1), (cx + bw // 2 + 3, by + 4), (cx + bw // 2 - 1, by + body_h)])
    nx = cx - bw // 2 + 1
    if dip > 0.6:
        hx, hy = nx - 2, by + 2
        pygame.draw.lines(surf, dark, False, [(nx, by + 1), (nx - 3, by - 1), (hx, hy)], 1)
    else:
        hx, hy = nx - 2, by - 7
        pygame.draw.lines(surf, dark, False, [(nx, by + 1), (nx + 1, by - 4), (hx, hy)], 1)
    pygame.draw.circle(surf, body, (int(hx), int(hy)), 2)
    pygame.draw.circle(surf, dark, (int(hx), int(hy)), 2, 1)
    pygame.draw.line(surf, bill, (hx - 1, hy), (hx - 5, hy + (1 if dip > 0.6 else 0)), 1)
    pygame.draw.circle(surf, (24, 20, 18), (int(hx - 1), int(hy - 1)), 1)
    pygame.draw.circle(surf, pf(P.get("crest", (150, 84, 76))), (int(hx + 1), int(hy - 2)), 1)


def _crit_piglet(surf, cx, base_y, v, night, t):
    """A low horizontal tube on four stubby legs with a blunt snout disc and a
    curl of tail: the widest-for-its-height silhouette in the cast, the exact
    opposite of the crane. 2-beat: the snout roots down into the deck and lifts,
    tail flicking on the off-beat."""
    pf = lambda c: _retint(c, night)
    P = v.palette
    body = pf(P.get("body", (196, 158, 152)))
    body_dk = pf(P.get("body_dk", _shade(P["body"], -40)))
    body_lt = _hi(body, 14, night)
    snout = pf(P.get("accent", (176, 128, 126)))
    g = int(base_y)
    root = max(0.0, math.sin(t * 2.6))
    bw, bh = 13, 5
    by = g - bh - 1
    pygame.draw.ellipse(surf, body, (cx - bw // 2, by, bw, bh))
    pygame.draw.ellipse(surf, body_dk, (cx - bw // 2, by, bw, bh), 1)
    pygame.draw.arc(surf, body_lt, (cx - bw // 2, by, bw, bh), math.radians(35), math.radians(150), 1)
    for k, lx in enumerate((cx - bw // 2 + 2, cx - bw // 2 + 3, cx + bw // 2 - 3, cx + bw // 2 - 2)):
        step = int(round(math.sin(t * 2.6 + k) * 0.6))
        pygame.draw.line(surf, body_dk, (lx, by + bh - 1), (lx + step, g), 2)
    curl = math.sin(t * 2.6 + 1.0)
    tx = cx + bw // 2 - 1
    pygame.draw.arc(surf, body, (tx - 1, by - 2, 5, 5),
                    math.radians(-40 + curl * 25), math.radians(210 + curl * 25), 1)
    hx = cx - bw // 2 - 1
    hy = by + 1 + int(root * 2)
    pygame.draw.circle(surf, body, (hx, hy), 3)
    pygame.draw.circle(surf, body_dk, (hx, hy), 3, 1)
    for sgn in (-1, 1):
        pygame.draw.polygon(surf, body_dk, [
            (hx + 1, hy - 2), (hx + 2 + sgn, hy - 4), (hx + 3, hy - 1)])
    sx = hx - 3
    pygame.draw.ellipse(surf, snout, (sx - 1, hy - 1, 3, 3))
    pygame.draw.circle(surf, _shade(snout, -46), (sx, hy), 1)
    pygame.draw.circle(surf, (26, 20, 20), (hx - 1, hy - 2), 1)


def _crit_rabbit(surf, cx, base_y, v, night, t):
    """A compact crouched ball with two LONG upright ears: a tiny body under an
    outsized vertical pair, which nothing else in the cast has. 2-beat: a
    nibbling head bob, with one ear twitching back on a slower cycle."""
    pf = lambda c: _retint(c, night)
    P = v.palette
    fur = pf(P.get("body", (168, 154, 136)))
    fur_dk = pf(P.get("body_dk", _shade(P["body"], -38)))
    fur_lt = _hi(fur, 14, night)
    ear_in = pf(P.get("accent", (166, 128, 124)))
    g = int(base_y)
    nib = max(0.0, math.sin(t * 4.2))
    twitch = math.sin(t * 1.1)
    bw, bh = 7, 5
    by = g - bh
    pygame.draw.ellipse(surf, fur, (cx - bw // 2, by, bw, bh))
    pygame.draw.ellipse(surf, fur_dk, (cx - bw // 2, by, bw, bh), 1)
    pygame.draw.arc(surf, fur_lt, (cx - bw // 2, by, bw, bh), math.radians(40), math.radians(150), 1)
    pygame.draw.circle(surf, fur_lt, (cx + bw // 2 - 1, g - 2), 2)
    pygame.draw.circle(surf, fur_dk, (cx + bw // 2 - 1, g - 2), 2, 1)
    hx = cx - 2
    hy = by - 1 + int(nib * 1.5)
    pygame.draw.circle(surf, fur, (hx, hy), 3)
    pygame.draw.circle(surf, fur_dk, (hx, hy), 3, 1)
    for k, sgn in enumerate((-1, 1)):
        # Long and set wide apart: the ears are the ONLY thing separating this
        # from the sitting cat, so the gap between them has to survive the
        # far-lane downscale as a gap.
        tilt = twitch * (1.6 if k else 0.3)
        base_pt = (hx + sgn * 1.5, hy - 2)
        tip = (hx + sgn * 1.5 + tilt, hy - 9 + abs(tilt) * 0.6)
        pygame.draw.line(surf, fur, base_pt, tip, 2)
        pygame.draw.line(surf, ear_in, (base_pt[0], base_pt[1] - 1), (tip[0], tip[1] + 1), 1)
    pygame.draw.circle(surf, (26, 20, 20), (hx - 2, hy - 1), 1)
    pygame.draw.circle(surf, ear_in, (hx - 3, hy + 1), 1)


# ── pools → foreground_variants rows ──────────────────────────────────────────

def _V(palette, **attrs):
    return fv.Variant(palette=palette, attrs=dict(attrs))


def _build_dogs():
    # The first five keep their pool order (scene code addresses them by index);
    # D1 and D3 are re-dressed toward stray IN PLACE, the four new looks append.
    return [
        _V(dict(coat=(150, 130, 100), coat_dk=(102, 86, 62), belly=(178, 162, 134)),
           build=1.05, leg=1.15, length=1.30, chest=0.85, head=0.92, scruffy=True,
           tail="streetlow", ear="drop", muzzle="long"),
        _V(dict(coat=(150, 102, 64), coat_dk=(104, 68, 42), belly=(196, 160, 110)),
           build=0.95, leg=0.52, length=1.45, chest=1.05, head=1.0, tail="stub", ear="bigprick", muzzle="med"),
        _V(dict(coat=(184, 178, 164), coat_dk=(128, 122, 110), belly=(196, 190, 178)),
           build=0.80, leg=0.92, length=0.98, chest=1.10, head=0.90, fluffy=True, scruffy=True,
           ruffcrop=True, tail="sickle", ear="prick", muzzle="med"),
        _V(dict(coat=(196, 130, 74), coat_dk=(140, 86, 46), belly=(228, 206, 172)),
           build=0.98, leg=0.80, length=1.0, chest=1.12, head=0.92, fluffy=True, tail="tightcurl", ear="prick", muzzle="short"),
        _V(dict(coat=(150, 124, 96), coat_dk=(104, 84, 64), belly=(186, 166, 142)),
           build=0.94, leg=0.74, length=1.06, chest=1.02, head=1.10, tail="lowpup", ear="longdrop", muzzle="short"),
        _V(dict(coat=(132, 122, 108), coat_dk=(88, 82, 74), belly=(158, 148, 132)),
           build=0.92, leg=0.95, length=1.18, chest=0.86, head=0.95, scruffy=True,
           tail="streetlow", ear="halfflop", muzzle="med"),
        _V(dict(coat=(172, 140, 96), coat_dk=(118, 94, 60), belly=(190, 168, 134)),
           build=0.96, leg=1.30, length=1.20, chest=0.72, head=0.86, tail="sickle", ear="prick", muzzle="long"),
        _V(dict(coat=(164, 106, 66), coat_dk=(112, 70, 42), belly=(186, 142, 100)),
           build=0.86, leg=0.70, length=0.96, chest=1.22, head=0.95, fluffy=True, mane=True,
           tail="tightcurl", ear="prick", muzzle="short"),
        _V(dict(coat=(178, 156, 118), coat_dk=(124, 106, 78), belly=(196, 178, 146)),
           build=0.72, leg=0.45, length=1.0, chest=1.15, head=1.15, fluffy=True, skirtcoat=True,
           tail="plume", ear="drop", muzzle="flat"),
    ]


def _build_critters():
    return [
        _V(dict(body=(120, 112, 104), body_dk=(76, 70, 66), accent=(168, 120, 118)), kind="cat"),
        _V(dict(body=(204, 190, 170), body_dk=(150, 130, 104), accent=(176, 70, 60)), kind="hen"),
        _V(dict(body=(142, 144, 154), body_dk=(96, 98, 108), accent=(108, 120, 152)), kind="pigeons"),
        _V(dict(body=(212, 206, 192), body_dk=(150, 140, 120), accent=(96, 120, 96)), kind="duck"),
        _V(dict(body=(188, 186, 178), body_dk=(132, 130, 124), accent=(86, 84, 92), crest=(150, 84, 76)), kind="crane"),
        # The piglet arrives with the produce: scenes only offer it on the market
        # beat, so it never turns up at dusk with nobody to own it.
        _V(dict(body=(196, 158, 152), body_dk=(134, 104, 100), accent=(176, 128, 126)), kind="piglet"),
        _V(dict(body=(168, 154, 136), body_dk=(114, 104, 92), accent=(166, 128, 124)), kind="rabbit"),
    ]


_CRITTER_KINDS = ("cat", "hen", "pigeons", "duck", "crane", "piglet", "rabbit")


def critter_index(kind):
    """Pool index of a critter by kind, so scenes can place a specific animal."""
    return _CRITTER_KINDS.index(kind)


fv.register("dog", _build_dogs())
fv.register("critter", _build_critters())
