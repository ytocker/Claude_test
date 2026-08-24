"""Promenade STREET-ANIMALS VARIETY EXPANSION — round 3 candidate sheet (SCRATCH).

Dog frequency was cut separately, so every sighting now has to be a RARER, FRESHER
look. That means the 5-strong pool has to stop reading as "the same five pets" and
start reading as a village street: mostly strays and mongrels, with the odd
recognisable house dog.

  DOGS 5 → 9.  Four NEW looks, all data rows on the parametric drawer plus a small
  set of new outline enums (village dogs are spitz-ish — wedge head, pointed
  muzzle, erect ears, a tail carried curled over the back OR hanging free — and
  the give-away of a street dog is the RAGGED outline, not its colour):
    D6 scruffy STRAY   — tufted/notched coat edge and a tail hanging almost
                         straight down. The pool's first BROKEN outline. (The
                         half-flopped ear is a 4x-zoom bonus, not the read: it
                         measures 0.97 IoU against a plain prick ear.)
    D7 lean STREET MUTT— tall legs, shallow tucked chest, a SICKLE tail carried
                         up and back; the sighthound-ish frame of a dog that
                         lives on the move.
    D8 CHOW-type       — a thick MANE ruff swallowing the neck so the head end
                         reads as a lion's; tight curl tail, stub muzzle.
    D9 LION-DOG        — a fringed SKIRT COAT that hangs to the deck and hides
                         the legs: a furry loaf with a flat face and a plume over
                         the back. The smallest, roundest thing in the cast.
  RE-DRESSED toward stray: D1 hound and D3 spitz — duller, dustier coats, ragged
  outlines, tails carried lower. D3 also takes a new `ruffcrop` attr: a ruff thick
  over the withers and rubbed flat at the throat, because a tail swap alone left
  only 19% of its outline changed (0.81 IoU vs the shipped spitz) — i.e. a dimmer
  D3 rather than a different dog. With the cropped ruff it measures 0.74.
  (SPOTTED village dog was NOT taken: round 2 cut a spotted mutt precisely because
  spots are interior colour and die at far-lane size.)

  CRITTERS 4 → 7, chosen for maximum silhouette separation:
    C5 CRANE   — a tall vertical: stilt legs + long S-neck + spear bill, ~2x the
                 duck's height. 2-beat: slow neck dip to preen, one leg lifts.
    C6 PIGLET  — a low horizontal tube on stubby legs with a snout disc and a
                 curled tail. 2-beat: root down / lift, tail flick.
    C7 RABBIT  — a compact ball topped by two LONG EARS. 2-beat: nibble bob +
                 ear twitch on a slower cycle.
  GOOSE was passed over on purpose: at 6-10px a goose is a duck with a longer
  neck, which is the same size-only read that got the sparrows cut in round 2.

CONSTRAINTS: pure pygame.draw.* + Surface, pygbag-safe, no numpy/gfxdraw/PIL in
game-bound code. Dogs stay clearly under an adult (PED_H 18); critters 4-12px.
Drawn CRISP at native size. Night cools toward (54,64,96) with the pale-coat
second pull so nothing breaches 150 luma — the gold coin (~230) stays the sole
brightest element, measured on RENDERED pixels in the footer.

Nothing here touches production game files; review-sheet generator only.
"""
from __future__ import annotations

import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1, 1))


# ── shared colour helpers (lifted from foreground_props + ped_cast) ────────────

def _clamp(c):
    return max(0, min(255, int(c)))


def _mix(a, b, t):
    t = max(0.0, min(1.0, t))
    return (_clamp(a[0] + (b[0] - a[0]) * t),
            _clamp(a[1] + (b[1] - a[1]) * t),
            _clamp(a[2] + (b[2] - a[2]) * t))


def _shade(c, d):
    return (_clamp(c[0] + d), _clamp(c[1] + d), _clamp(c[2] + d))


def _luma(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


NIGHT_GLOW_CAP = 150
DOG_H = 12


def _retint(col, night):
    if night <= 0.05:
        return col
    out = _mix(col, (54, 64, 96), min(0.55, 0.40 * night + 0.20))
    if _luma(out) > NIGHT_GLOW_CAP:
        over = (_luma(out) - NIGHT_GLOW_CAP) / max(1.0, 255 - NIGHT_GLOW_CAP)
        out = _mix(out, (66, 76, 104), min(0.78, 0.5 + over))
    return out


def _hi(c, d, night):
    out = _shade(c, d)
    if night > 0.05 and _luma(out) > NIGHT_GLOW_CAP:
        out = _mix(out, (66, 76, 104), 0.65)
    return out


# ════════════════════════════════════════════════════════════════════════════
# DOGS — the shipped drawer plus the new outline enums this round needs.
#
# attrs: build / leg / length / chest / head / fluffy   (shipped)
#        tail   'low'|'lowpup'|'plume'|'tightcurl'|'stub'|'sickle'|'streetlow'
#        ear    'drop'|'prick'|'bigprick'|'longdrop'|'halfflop'
#        muzzle 'long'|'med'|'short'|'flat'
#        scruffy   ragged tufted outline + a notched ear  (the STRAY tell)
#        mane      thick ruff round the neck              (chow)
#        skirtcoat fringed coat hanging to the deck       (lion-dog)
# ════════════════════════════════════════════════════════════════════════════

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
            (ax - int(sh_h * 0.1) + sway, body_top - int(sh_h * 0.75))], max(3, sh_h // 4))
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
        pts = [(body_left, body_top + body_h // 2), (body_right, body_top + body_h // 2)]
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
        del pts

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
        # One ear up, one folded over at the tip: an ASYMMETRIC head outline. No
        # shipped dog is asymmetric, so this alone separates the stray at a glance.
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
                (ex0, hy - head_r + 1), (hx + head_r + 1, hy - head_r // 3),
                (hx + (head_r if fx_off > 0 else 1) + sway2, tip_y), (ex0 - 1, hy + head_r // 2)])


# ════════════════════════════════════════════════════════════════════════════
# CRITTERS — one shared drawer dispatched by kind; each with its own 2-beat idle
# ════════════════════════════════════════════════════════════════════════════

def draw_critter(surf, cx, base_y, v, night, t):
    kind = v.attrs.get("kind", "hen")
    {"cat": _crit_cat, "hen": _crit_hen, "pigeons": _crit_pigeons, "duck": _crit_duck,
     "crane": _crit_crane, "piglet": _crit_piglet, "rabbit": _crit_rabbit}[kind](
        surf, cx, base_y, v, night, t)


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
        (cx + 3, g - 1), (cx + 5, g - 2), (cx + 5, g - 5), (cx + 3 + flick, g - 6 - max(0, flick))], 2)
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
    """NEW — a tall wading bird: two stilt legs, a small high body, a long S-neck
    and a spear bill, standing about twice the duck's height. It is the only
    VERTICAL critter, so it never competes with the low pecking clumps.
    2-beat: the neck folds down to preen, then unfurls; one leg lifts on the
    slower half of the cycle."""
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
    """NEW — a low horizontal tube on four stubby legs with a blunt snout disc and
    a curl of tail: the widest-for-its-height silhouette in the cast, the exact
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
    """NEW — a compact crouched ball with two LONG upright ears: a tiny body under
    an outsized vertical pair, which nothing else in the cast has. 2-beat: a
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
        # Longer and set wider apart than the first pass: the ears are the ONLY
        # thing separating this from the sitting cat, so the gap between them has
        # to survive the far-lane downscale as a gap.
        tilt = twitch * (1.6 if k else 0.3)
        base_pt = (hx + sgn * 1.5, hy - 2)
        tip = (hx + sgn * 1.5 + tilt, hy - 9 + abs(tilt) * 0.6)
        pygame.draw.line(surf, fur, base_pt, tip, 2)
        pygame.draw.line(surf, ear_in, (base_pt[0], base_pt[1] - 1), (tip[0], tip[1] + 1), 1)
    pygame.draw.circle(surf, (26, 20, 20), (hx - 2, hy - 1), 1)
    pygame.draw.circle(surf, ear_in, (hx - 3, hy + 1), 1)


# ════════════════════════════════════════════════════════════════════════════
# THE POOLS
# ════════════════════════════════════════════════════════════════════════════

class _V:
    def __init__(self, palette, **attrs):
        self.palette = palette
        self.pose = frozenset()
        self.accessory = frozenset()
        self.attrs = dict(attrs)


DOGS = [
    ("D1 stray-dressed HOUND", _V(
        dict(coat=(150, 130, 100), coat_dk=(102, 86, 62), belly=(178, 162, 134)),
        build=1.05, leg=1.15, length=1.30, chest=0.85, head=0.92,
        scruffy=True, tail="streetlow", ear="drop", muzzle="long"),
     "RE-DRESSED | coat dulled (176,150,110)->(150,130,100), tail low->STREETLOW (hangs straight down), ragged/tufted back line | same proportions, now a street dog"),
    ("D2 short-leg DASH", _V(
        dict(coat=(150, 102, 64), coat_dk=(104, 68, 42), belly=(196, 160, 110)),
        build=0.95, leg=0.52, length=1.45, chest=1.05, head=1.0,
        tail="stub", ear="bigprick", muzzle="med"),
     "UNCHANGED (height ceiling benchmark) | corgi/dachshund low-long, stub tail, big ears"),
    ("D3 dusty street SPITZ", _V(
        dict(coat=(184, 178, 164), coat_dk=(128, 122, 110), belly=(196, 190, 178)),
        build=0.80, leg=0.92, length=0.98, chest=1.10, head=0.90,
        fluffy=True, scruffy=True, ruffcrop=True, tail="sickle", ear="prick", muzzle="med"),
     "RE-DRESSED | plume->SICKLE + NEW attr RUFFCROP: the ruff is thick over the withers and rubbed flat at the throat, an asymmetric collar. Tail alone only moved 19% of the outline (0.81 IoU vs the shipped spitz) — with the cropped ruff and 2px tufts it is 0.74, a re-shaped dog rather than a dimmer one"),
    ("D4 stocky SHIBA", _V(
        dict(coat=(196, 130, 74), coat_dk=(140, 86, 46), belly=(228, 206, 172)),
        build=0.98, leg=0.80, length=1.0, chest=1.12, head=0.92,
        fluffy=True, tail="tightcurl", ear="prick", muzzle="short"),
     "UNCHANGED | the one clearly OWNED dog left in the pool — rust coat, tight C-ring tail"),
    ("D5 droopy LONG-EAR PUP", _V(
        dict(coat=(150, 124, 96), coat_dk=(104, 84, 64), belly=(186, 166, 142)),
        build=0.94, leg=0.74, length=1.06, chest=1.02, head=1.10,
        tail="lowpup", ear="longdrop", muzzle="short"),
     "UNCHANGED | ears hang below the jawline and break the head outline"),
    ("D6 scruffy STRAY  [NEW]", _V(
        dict(coat=(132, 122, 108), coat_dk=(88, 82, 74), belly=(158, 148, 132)),
        build=0.92, leg=0.95, length=1.18, chest=0.86, head=0.95,
        scruffy=True, tail="streetlow", ear="halfflop", muzzle="med"),
     "NEW | what actually carries this row is the STREETLOW tail (0.89 IoU vs the same dog with a sabre tail) plus the dust-grey coat and the 2px ragged back (0.91 vs a smooth one). MEASURED: ear:HALFFLOP is sub-pixel at this size — 0.97 IoU against a plain prick ear — so it is a bonus at 4x, not the read"),
    ("D7 lean STREET MUTT  [NEW]", _V(
        dict(coat=(172, 140, 96), coat_dk=(118, 94, 60), belly=(190, 168, 134)),
        build=0.96, leg=1.30, length=1.20, chest=0.72, head=0.86,
        tail="sickle", ear="prick", muzzle="long"),
     "NEW | tail:SICKLE (up + curved back, never touching the loin) + tall legs + the shallowest chest in the pool (0.74) + fine head | a dog built to keep moving"),
    ("D8 CHOW-type  [NEW]", _V(
        dict(coat=(164, 106, 66), coat_dk=(112, 70, 42), belly=(186, 142, 100)),
        build=0.86, leg=0.70, length=0.96, chest=1.22, head=0.95,
        fluffy=True, mane=True, tail="tightcurl", ear="prick", muzzle="short"),
     "NEW | attr MANE — a shaggy ruff drawn BEHIND the head so the whole front end reads as one lion-ish disc; deep chest, short legs, tight curl tail"),
    ("D9 LION-DOG  [NEW]", _V(
        dict(coat=(178, 156, 118), coat_dk=(124, 106, 78), belly=(196, 178, 146)),
        build=0.72, leg=0.45, length=1.0, chest=1.15, head=1.15,
        fluffy=True, skirtcoat=True, tail="plume", ear="drop", muzzle="flat"),
     "NEW | attr SKIRTCOAT — a fringed coat falling to the deck that HIDES THE LEGS (a moving loaf) + flat face + plume over the back | the smallest, roundest animal in the cast | the hem zigzag now FLIPS PHASE with the gait: 21 px change along the bottom edge per cycle, so the coat walks instead of sliding like a dropped sack"),
]

CRITTERS = [
    ("C1 CAT", _V(dict(body=(120, 112, 104), body_dk=(76, 70, 66), accent=(168, 120, 118)), kind="cat"),
     "UNCHANGED | sits upright, tail curled | MOTION: tail-tip flick + ear swivel"),
    ("C2 HEN", _V(dict(body=(204, 190, 170), body_dk=(150, 130, 104), accent=(176, 70, 60)), kind="hen"),
     "UNCHANGED | plump body, comb + wattle | MOTION: peck down-up"),
    ("C3 PIGEONS", _V(dict(body=(142, 144, 154), body_dk=(96, 98, 108), accent=(108, 120, 152)), kind="pigeons"),
     "UNCHANGED | tight clump, one lead bird | MOTION: peck, one hops"),
    ("C4 DUCK", _V(dict(body=(212, 206, 192), body_dk=(150, 140, 120), accent=(96, 120, 96)), kind="duck"),
     "UNCHANGED | boat body, flat bill | MOTION: waddle + head bob"),
    ("C5 CRANE  [NEW]", _V(dict(body=(188, 186, 178), body_dk=(132, 130, 124), accent=(86, 84, 92), crest=(150, 84, 76)), kind="crane"),
     "NEW | the only VERTICAL critter: stilt legs + long S-neck + spear bill, ~2x the duck's height, dark trailing plumes | MOTION: neck folds down to preen then unfurls; one leg lifts on the slow half"),
    ("C6 PIGLET  [NEW]", _V(dict(body=(196, 158, 152), body_dk=(134, 104, 100), accent=(176, 128, 126)), kind="piglet"),
     "NEW [BEAT-GATED: BEAT_MARKET only — it arrives with the produce and must not turn up at dusk with nobody to own it] | the widest-for-its-height silhouette: a low tube on stubby legs, blunt snout disc, curl tail | MOTION: roots the snout down into the deck and lifts, tail flicks off-beat"),
    ("C7 RABBIT  [NEW]", _V(dict(body=(168, 154, 136), body_dk=(114, 104, 92), accent=(166, 128, 124)), kind="rabbit"),
     "NEW | a compact ball under two OUTSIZED upright ears + a bright scut | ears lengthened 1px and set 1px further apart because they are the ONLY separator from the sitting cat: IoU vs C1 drops 0.51 -> 0.45 | MOTION: nibbling head bob, one ear twitching back on a slower cycle"),
]

PASSED = [
    ("SPOTTED village dog", "spots are interior colour and vanish in the far lane — round 2 already cut a spotted mutt for exactly this; a third attempt would repeat the mistake."),
    ("GOOSE", "at 6-10px a goose is a duck with a longer neck — the same size-only read that got the sparrows cut in round 2. The CRANE takes the long-necked slot instead, because its stilt legs make it a different SHAPE, not a different size."),
    ("SPARROW PAIR", "already cut in round 2 (reads as grit next to the pigeon clump); nothing has changed at this scale."),
]


# ════════════════════════════════════════════════════════════════════════════
# SHEET RENDERER (round-2 house style)
# ════════════════════════════════════════════════════════════════════════════

WIDTH = 1240
PAD = 12
BG_DAY = (150, 140, 118)
BG_NIGHT = (40, 46, 70)


def _font(sz, bold=False):
    return pygame.font.SysFont("dejavusans", sz, bold=bold)


def _text(surf, s, x, y, sz=11, col=(228, 224, 214), bold=False):
    surf.blit(_font(sz, bold).render(s, True, col), (x, y))


def _wrap(surf, s, x, y, w, sz=9, col=(206, 202, 192), lh=11):
    fnt = _font(sz)
    line = ""
    for wd in s.split(" "):
        test = (line + " " + wd).strip()
        if fnt.size(test)[0] > w:
            surf.blit(fnt.render(line, True, col), (x, y)); y += lh; line = wd
        else:
            line = test
    if line:
        surf.blit(fnt.render(line, True, col), (x, y)); y += lh
    return y


def _gold_coin(surf, cx, cy, r=8):
    for rr, c in ((r, (150, 110, 30)), (r - 1, (235, 190, 60)), (r - 3, (255, 232, 150))):
        pygame.draw.circle(surf, c, (cx, cy), rr)
    pygame.draw.circle(surf, (180, 140, 50), (cx, cy), r, 1)
    surf.blit(_font(9, True).render("$", True, (150, 100, 20)), (cx - 3, cy - 6))


def _adult_ref(surf, cx, base_y, night):
    """A coarse adult-pedestrian stand-in (PED_H~18) so a dog reads CLEARLY
    smaller than a person and a critter reads tiny."""
    pf = lambda c: _retint(c, night)
    coat = pf((96, 104, 140)); coat_dk = _shade(coat, -40)
    skin = pf((222, 178, 132)); hair = pf((52, 42, 34))
    g = int(base_y)
    head_r = 3; torso_h = 8
    torso_top = g - 5 - torso_h
    for sgn in (-1, 1):
        pygame.draw.line(surf, coat_dk, (cx + sgn * 2, torso_top + torso_h), (cx + sgn * 2, g), 2)
    pygame.draw.polygon(surf, coat, [(cx - 3, torso_top), (cx + 3, torso_top),
                                     (cx + 4, torso_top + torso_h), (cx - 4, torso_top + torso_h)])
    pygame.draw.circle(surf, skin, (cx, torso_top - head_r), head_r)
    pygame.draw.circle(surf, hair, (cx, torso_top - head_r - 1), head_r)


def _cell(parent, name, drawer, v, note, x, y, w, h, night, *, n_frames, fr_t, fr_dx, zoom_pad):
    is_night = night > 0.5
    bg = BG_NIGHT if is_night else BG_DAY
    cell = pygame.Surface((w, h))
    cell.fill(bg)
    deck = _mix(bg, (0, 0, 0), 0.18)
    base = h - 16
    pygame.draw.rect(cell, deck, (0, base, w, h - base))
    pygame.draw.line(cell, _shade(bg, 24), (0, base), (w, base), 1)

    fx0 = 14
    for i in range(n_frames):
        cxp = fx0 + 16 + i * fr_dx
        drawer(cell, cxp, base, v, night, fr_t[i])
        _text(cell, f"t{i}", cxp - 6, base + 2, 8, _shade(bg, 60))
    _text(cell, "TRUE far-lane (anim frames)", fx0, base + 8, 8, _shade(bg, 50))

    SC_W, SC_H = 34, 28
    nat = pygame.Surface((SC_W, SC_H), pygame.SRCALPHA)
    deck_y = SC_H - zoom_pad
    nat.fill((*_mix(bg, (0, 0, 0), 0.18), 120), (0, deck_y, SC_W, SC_H - deck_y))
    drawer(nat, SC_W // 2, deck_y, v, night, fr_t[min(1, n_frames - 1)])
    z = 4
    zoom = pygame.transform.scale(nat, (SC_W * z, SC_H * z))
    zw, zh = zoom.get_size()
    zx, zy = w - zw - 8, 20
    pygame.draw.rect(cell, _shade(bg, -20), (zx - 2, zy - 2, zw + 4, zh + 4))
    cell.blit(zoom, (zx, zy))
    pygame.draw.rect(cell, _shade(bg, 40), (zx - 2, zy - 2, zw + 4, zh + 4), 1)
    _text(cell, "4x zoom (nearest)", zx, zy - 12, 8, _shade(bg, 60))

    _gold_coin(cell, w - 16, h - 12, r=6)
    _text(cell, name, 6, 4, 13, (240, 236, 226), bold=True)
    _wrap(cell, note, 6, 22, zx - 14)

    parent.blit(cell, (x, y))
    pygame.draw.rect(parent, (70, 74, 90), (x, y, w, h), 1)


def _true_band(sheet, y, title, items, drawer, night):
    _text(sheet, title, PAD, y, 13, (240, 220, 150), bold=True)
    y += 22
    band_h = 66
    row = pygame.Surface((WIDTH - PAD * 2, band_h))
    bg = BG_NIGHT if night > 0.5 else BG_DAY
    row.fill(bg)
    deck = _mix(bg, (0, 0, 0), 0.18)
    base = band_h - 14
    pygame.draw.rect(row, deck, (0, base, WIDTH - PAD * 2, 14))
    pygame.draw.line(row, _shade(bg, 26), (0, base), (WIDTH - PAD * 2, base), 1)
    _adult_ref(row, 24, base, night)
    _text(row, "adult", 8, base + 1, 8, (70, 58, 46) if night <= 0.5 else (150, 160, 185))
    _gold_coin(row, WIDTH - PAD * 2 - 20, base - 9)
    _text(row, "coin", WIDTH - PAD * 2 - 38, base + 1, 8, _shade(bg, 50))
    spacing = (WIDTH - PAD * 2 - 150) // len(items)
    for i, (nm, v, _n) in enumerate(items):
        cx = 76 + i * spacing
        drawer(row, cx, base, v, night, 0.4 + i * 0.5)
        _text(row, nm.split(" ")[0], cx - 8, base + 1, 8,
              (70, 58, 46) if night <= 0.5 else (150, 160, 185))
    sheet.blit(row, (PAD, y))
    pygame.draw.rect(sheet, (70, 74, 90), (PAD, y, WIDTH - PAD * 2, band_h), 1)
    return y + band_h + 8


def _alpha_mask(surf, scale=1.0):
    if scale != 1.0:
        surf = pygame.transform.scale(surf, (int(surf.get_width() * scale),
                                             int(surf.get_height() * scale)))
    return {(x, y) for x in range(surf.get_width()) for y in range(surf.get_height())
            if surf.get_at((x, y))[3] > 0}


def _fig(drawer, v, t, scale=1.0):
    s = pygame.Surface((46, 32), pygame.SRCALPHA)
    drawer(s, 23, 28, v, 0.0, t)
    return _alpha_mask(s, scale)


def _iou(a, b):
    return len(a & b) / max(1, len(a | b))


def _measure_outlines():
    """Every distinctness claim on this sheet, re-derived from rendered alpha."""
    by = {nm.split(" ")[0]: v for nm, v, _n in DOGS}
    crit = {nm.split(" ")[0]: v for nm, v, _n in CRITTERS}
    shipped_d3 = _V(dict(coat=(214, 208, 196), coat_dk=(150, 144, 132), belly=(228, 222, 210)),
                    build=0.80, leg=0.92, length=0.98, chest=1.10, head=0.90,
                    fluffy=True, tail="plume", ear="prick", muzzle="med")
    d6 = by["D6"]
    d6_prick = _V(dict(d6.palette), **{**d6.attrs, "ear": "prick"})
    d6_sabre = _V(dict(d6.palette), **{**d6.attrs, "tail": "low"})
    d6_smooth = _V(dict(d6.palette), **{**d6.attrs, "scruffy": False})
    d9 = by["D9"]
    ms = [_fig(draw_dog, d9, i * 0.13) for i in range(24)]
    moving = set().union(*ms) - set.intersection(*ms)
    bot = max(y for _x, y in set().union(*ms))
    return {
        "d3": _iou(_fig(draw_dog, by["D3"], 0.5), _fig(draw_dog, shipped_d3, 0.5)),
        "d6_ear": _iou(_fig(draw_dog, d6, 0.5), _fig(draw_dog, d6_prick, 0.5)),
        "d6_tail": _iou(_fig(draw_dog, d6, 0.5), _fig(draw_dog, d6_sabre, 0.5)),
        "d6_scruff": _iou(_fig(draw_dog, d6, 0.5, 0.78), _fig(draw_dog, d6_smooth, 0.5, 0.78)),
        "d9_hem": len({p for p in moving if p[1] >= bot - 2}),
        "rabbit": _iou(_fig(draw_critter, crit["C7"], 0.5), _fig(draw_critter, crit["C1"], 0.5)),
    }


def _measure_night_cap():
    night = 0.95
    strip = pygame.Surface((1200, 80))
    strip.fill(BG_NIGHT)
    base = 62
    x = 40
    for _nm, v, _n in DOGS:
        for tt in (0.0, 0.5, 1.0):
            draw_dog(strip, x, base, v, night, tt)
            x += 28
            if x > 1160:
                x = 40
        x += 10
    for _nm, v, _n in CRITTERS:
        for tt in (0.0, 0.5, 1.0):
            draw_critter(strip, x, base, v, night, tt)
            x += 22
            if x > 1160:
                x = 40
        x += 10
    hottest = 0.0
    over = 0
    bg_l = _luma(BG_NIGHT)
    for px in range(strip.get_width()):
        for py in range(strip.get_height()):
            c = strip.get_at((px, py))[:3]
            l = _luma(c)
            if abs(l - bg_l) < 1.5:
                continue
            hottest = max(hottest, l)
            if l > NIGHT_GLOW_CAP:
                over += 1
    return hottest, over


def render():
    cell_w = (WIDTH - PAD * 3) // 2
    dog_cell_h = 140
    crit_cell_h = 136

    title_h = 64
    bandA_h = 22 + 66 + 8 + 22 + 66 + 8
    dog_rows = (len(DOGS) + 1) // 2
    crit_rows = (len(CRITTERS) + 1) // 2
    detail_h = (22 + 2 * (18 + dog_rows * (dog_cell_h + 6)) +
                20 + 2 * (18 + crit_rows * (crit_cell_h + 6)))
    passed_h = 26 + len(PASSED) * 13 + 8
    strip_h = 96
    comp_h = 22 + 2 * (strip_h + 6)
    total_h = title_h + bandA_h + detail_h + passed_h + comp_h + PAD * 6 + 40

    sheet = pygame.Surface((WIDTH, total_h))
    sheet.fill((26, 28, 38))

    y = PAD
    _text(sheet, "SKYBIT PROMENADE — STREET ANIMALS VARIETY EXPANSION (round 3): DOGS 5→9 · CRITTERS 4→7",
          PAD, y, 17, (250, 246, 236), bold=True)
    y += 22
    y = _wrap(sheet,
              "Dog sightings are rarer now, so each one has to be a fresher look. FOUR NEW dogs lean stray/village — a scruffy stray with a broken outline and one flopped ear, a lean sickle-tailed street mutt, "
              "a chow-type whose MANE swallows the neck, and a lion-dog whose SKIRT COAT hides its legs — and TWO shipped breeds are re-dressed toward the street (duller coats, ragged edges, tails carried lower). "
              "New outline enums only: tail sickle/streetlow, ear halfflop, muzzle flat, attrs scruffy/mane/skirtcoat. THREE new critters picked for maximum silhouette separation: a VERTICAL crane, a low horizontal PIGLET, "
              "and a RABBIT that is a ball under two outsized ears. Spotted dog / goose / sparrows were passed over — see the PASSED band.",
              PAD, y, WIDTH - PAD * 2, 9, (188, 186, 200))
    y = title_h + PAD

    y = _true_band(sheet, y, "A1.  DOGS — true far-lane size beside an adult stand-in (PED_H~18) and the coin; every dog still reads clearly smaller than a person",
                   DOGS, draw_dog, 0.0)
    y = _true_band(sheet, y, "A2.  CRITTERS — true far-lane size; the crane is the tall one, the piglet the wide one, the rabbit the eared one",
                   CRITTERS, draw_critter, 0.0)

    _text(sheet, "B.  PER-DOG — TRUE far-lane across 2 GAIT frames · 4x zoom (nearest) · in-cell coin · attrs note   (DAY then NIGHT)",
          PAD, y, 13, (240, 220, 150), bold=True)
    y += 20
    for is_night in (False, True):
        night = 0.95 if is_night else 0.0
        _text(sheet, "NIGHT  (cooled <=150, nothing self-lit)" if is_night else "DAY",
              PAD, y, 11, (160, 180, 220) if is_night else (240, 210, 130), bold=True)
        y += 16
        for r in range(dog_rows):
            for c in range(2):
                idx = r * 2 + c
                if idx >= len(DOGS):
                    break
                nm, v, note = DOGS[idx]
                _cell(sheet, nm, draw_dog, v, note, PAD + c * (cell_w + PAD), y, cell_w,
                      dog_cell_h, night, n_frames=2, fr_t=(0.0, 0.52), fr_dx=58, zoom_pad=4)
            y += dog_cell_h + 6
        y += 8

    _text(sheet, "B2.  PER-CRITTER — TRUE far-lane across 3 MOTION frames · 4x zoom · in-cell coin · note   (DAY then NIGHT)",
          PAD, y, 13, (240, 220, 150), bold=True)
    y += 20
    for is_night in (False, True):
        night = 0.95 if is_night else 0.0
        _text(sheet, "NIGHT" if is_night else "DAY", PAD, y, 11,
              (160, 180, 220) if is_night else (240, 210, 130), bold=True)
        y += 16
        for r in range(crit_rows):
            for c in range(2):
                idx = r * 2 + c
                if idx >= len(CRITTERS):
                    break
                nm, v, note = CRITTERS[idx]
                _cell(sheet, nm, draw_critter, v, note, PAD + c * (cell_w + PAD), y, cell_w,
                      crit_cell_h, night, n_frames=3, fr_t=(0.0, 0.55, 1.15), fr_dx=46, zoom_pad=4)
            y += crit_cell_h + 6
        y += 8

    _text(sheet, "C.  PASSED OVER — candidates deliberately not taken (and why), so the call can be overruled with the reasoning visible",
          PAD, y, 13, (240, 150, 140), bold=True)
    y += 20
    pb = pygame.Surface((WIDTH - PAD * 2, len(PASSED) * 13 + 8))
    pb.fill((44, 34, 38))
    yy = 4
    for nm, reason in PASSED:
        _text(pb, f"{nm}  —  {reason}", 8, yy, 9, (224, 198, 196))
        yy += 13
    sheet.blit(pb, (PAD, y))
    pygame.draw.rect(sheet, (120, 74, 78), (PAD, y, WIDTH - PAD * 2, len(PASSED) * 13 + 8), 1)
    y += len(PASSED) * 13 + 8 + 8

    _text(sheet, "D.  ON-STREET COMPOSITE — 9 dogs + 7 critters among adult stand-ins, with the coin yardstick  (DAY then NIGHT)",
          PAD, y, 13, (240, 220, 150), bold=True)
    y += 20
    for is_night in (False, True):
        night = 0.95 if is_night else 0.0
        bg = BG_NIGHT if is_night else BG_DAY
        strip = pygame.Surface((WIDTH - PAD * 2, strip_h))
        strip.fill(bg)
        deck = _mix(bg, (0, 0, 0), 0.2)
        base = strip_h - 14
        pygame.draw.rect(strip, deck, (0, base, WIDTH - PAD * 2, strip_h - base))
        pygame.draw.line(strip, _shade(bg, 24), (0, base), (WIDTH - PAD * 2, base), 1)
        sw = WIDTH - PAD * 2
        seq = []
        for i in range(max(len(DOGS), len(CRITTERS))):
            if i < len(DOGS):
                seq.append(("dog", DOGS[i][1]))
            if i < len(CRITTERS):
                seq.append(("crit", CRITTERS[i][1]))
        step = (sw - 120) // len(seq)
        _adult_ref(strip, 34, base, night)
        for i, (kind, v) in enumerate(seq):
            cxp = 70 + i * step
            if kind == "dog":
                draw_dog(strip, cxp, base, v, night, 0.2 + i * 0.37)
            else:
                draw_critter(strip, cxp, base, v, night, 0.4 + i * 0.41)
            if i in (5, 11):
                _adult_ref(strip, cxp + step // 2, base, night)
        _gold_coin(strip, sw - 18, 18)
        _text(strip, "coin ref", sw - 44, 30, 8, _shade(bg, 60))
        _text(strip, "NIGHT" if is_night else "DAY", 4, 2, 9,
              (170, 190, 225) if is_night else (60, 50, 40), bold=True)
        sheet.blit(strip, (PAD, y))
        pygame.draw.rect(sheet, (70, 74, 90), (PAD, y, WIDTH - PAD * 2, strip_h), 1)
        y += strip_h + 6

    o = _measure_outlines()
    audit = (f"OUTLINE AUDIT (rendered alpha, measured not asserted): D3 vs the SHIPPED spitz = {o['d3']:.2f} — a tail swap alone left it at 0.81, i.e. a dimmer D3; the asymmetrically cropped ruff plus 2px tufts re-shape it.  ·  "
             f"D6 ragged-vs-smooth at FAR 0.78x = {o['d6_scruff']:.2f} (1px tufts measured 0.95 — the downscale was erasing them).  ·  "
             f"D6 streetlow-vs-sabre tail = {o['d6_tail']:.2f} and halfflop-vs-prick ear = {o['d6_ear']:.2f}: the EAR IS SUB-PIXEL at this size, so D6's read is the low tail + dust coat + broken back, not the ear.  ·  "
             f"D9 hem px moving per cycle = {o['d9_hem']} (was 0 — a static zigzag).  ·  rabbit vs cat = {o['rabbit']:.2f}, down from 0.51 on +1px ear length and +1px ear gap.")
    y = _wrap(sheet, audit, PAD, y + 2, WIDTH - PAD * 2, 9, (170, 200, 180))

    hottest, over = _measure_night_cap()
    coin_l = _luma((255, 232, 150))
    msg = (f"NIGHT-CAP AUDIT (measured on RENDERED pixels across motion phases, all 9 dogs + 7 critters): hottest ANIMAL px luma = {hottest:.0f}  ·  "
           f"px over {NIGHT_GLOW_CAP} = {over}  ·  gold-coin core luma = {coin_l:.0f} (sole brightest).  "
           f"{'PASS — all animal px <= cap.' if over == 0 else 'FAIL — ' + str(over) + ' px breach the cap.'}")
    _text(sheet, msg, PAD, total_h - 16, 9, (170, 200, 180) if over == 0 else (220, 140, 130))

    out = "/home/user/skybit/docs/sidewalk_overhaul/animals/round_3.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("saved", out, sheet.get_size())
    print(f"night-cap: hottest={hottest:.1f} over={over} coin={coin_l:.1f}")


if __name__ == "__main__":
    render()
