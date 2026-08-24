"""Day-cast VARIETY EXPANSION — round 3 candidate-sheet generator (SCRATCH).

The shipped day cast (game/day_cast.py: kids 6 / elders 6 / vendors 7) is small
enough that a single market beat can show the same child twice. This round takes
each family to TEN after retiring two weak rows, and every family gains at least
one genuinely NEW pose/stance branch on its shared drawer — not another palette:

  KIDS      4 kept + 6 new = 10.  NEW STANCE `tiptoe` (heels up, both arms
            stretched over a counter edge — a tall thin child, the opposite of
            every crouched/running row). Plus the drawer's own KITE accessory,
            which no shipped row ever used, a trailing RIBBON, a lantern on a
            stick, a school SATCHEL on the back, and side-tail hair.
  ELDERS    4 kept + 6 new = 10.  NEW STANCES `brush` (water-calligrapher bent
            deep over a long brush that reaches the deck ahead, wet strokes
            behind it) and `reading` (an open scroll held wide at the chest —
            a hard horizontal bar across the body). Plus a sword-form elder and
            a back-basket herb gatherer.
  VENDORS   5 kept + 5 new = 10.  NEW POSES `chop` (cleaver up over a board,
            2-beat), `pour` (long-spout pot high, a thread of tea arcing into a
            cup) and `wok` (two hands on a tilted wok, food tossed above it) —
            all upper-body actions, because vendors read chest-up behind a
            counter.

  RETIRES (2 per family, justified in the sheet's cut band): K1, K5 · E1, E4 ·
  V1, V6.

CONSTRAINTS (from the module header): pure pygame.draw.* + Surface, pygbag-safe;
night cools toward (54,64,96) with a hard <=150 luma cap so the gold coin (~230)
stays the sole brightest element — measured on RENDERED pixels in the footer.
Variety must live in the OUTLINE; these figures are 9-17px and colour dies first.
Authored feet-on-base_y, drawn CRISP.

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


# ── shared colour helpers (lifted from game/foreground_props + ped_cast) ───────

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


def _retint(col, night):
    if night <= 0.05:
        return col
    return _mix(col, (54, 64, 96), min(0.55, 0.40 * night + 0.20))


def _cap_luma(col, cap=150.0):
    g = _luma(col)
    if g <= cap:
        return col
    return (_clamp(col[0] * cap / g), _clamp(col[1] * cap / g), _clamp(col[2] * cap / g))


def _knock(col, amount=0.18):
    g = _luma(col)
    desat = _mix(col, (g, g, g), amount * 0.7)
    return _shade(desat, -int(255 * amount * 0.55))


SKIN = {
    "fair":  (236, 198, 156),
    "warm":  (222, 178, 132),
    "tan":   (200, 156, 112),
    "deep":  (168, 124, 86),
    "ruddy": (228, 176, 150),
}


class V:
    def __init__(self, palette, *, pose=(), acc=(), attrs=None, label="", note=""):
        self.palette = palette
        self.pose = frozenset(pose)
        self.accessory = frozenset(acc)
        self.attrs = dict(attrs or {})
        self.label = label
        self.note = note


# ════════════════════════════════════════════════════════════════════════════
# KIDS — shipped drawer + the new tiptoe stance and the new held props
# ════════════════════════════════════════════════════════════════════════════

KID_H = 13


def draw_kid(surf, cx, base_y, v, night, t):
    P, A = v.palette, v.attrs
    pf = lambda c: _cap_luma(_retint(c, night)) if night > 0.05 else c
    skin = pf(SKIN.get(P.get("skin", "warm"), SKIN["warm"]))
    skin_sh = _shade(skin, -26)
    shirt = pf(P["shirt"]); shirt_dk = pf(P.get("shirt_dk", _shade(P["shirt"], -42)))
    pants = pf(P.get("pants", _shade(shirt, -60)))
    hair = pf(P.get("hair", (60, 44, 34)))

    age = A.get("age", 0.6)
    height = 0.62 + 0.38 * age
    total = max(7, int(KID_H * height))
    squat = "squat" in v.pose
    run = "run" in v.pose
    chase = "chase" in v.pose
    carried = "carried" in v.pose
    tiptoe = "tiptoe" in v.pose
    head_bias = 0.10 if squat else 0.0
    head_r = max(2, int(total * (0.34 + head_bias - 0.06 * age)))
    body_h = max(3, int(total * 0.32))
    body_w = max(3, int(total * 0.30))
    ground = int(base_y)
    body_bot = ground - max(2, int(total * 0.30))
    body_y = body_bot - body_h
    hx = cx
    hy = body_y - head_r + 1

    gait = math.sin(t * (2.6 if (run or chase) else 1.7))

    if carried:
        body_y = ground - int(total * 1.4)
        body_bot = body_y + body_h
        hy = body_y - head_r + 1
        ad = pf(P.get("carrier", (96, 84, 110)))
        ad_dk = _shade(ad, -40)
        a_w = max(4, int(KID_H * 0.46))
        pygame.draw.polygon(surf, ad, [
            (cx - a_w, ground), (cx + a_w, ground),
            (cx + a_w - 1, ground - int(KID_H * 0.9)), (cx - a_w + 2, ground - KID_H)])
        pygame.draw.circle(surf, pf(SKIN["tan"]), (cx - 1, ground - KID_H - 2), 3)
        pygame.draw.circle(surf, ad_dk, (cx - 1, ground - KID_H - 3), 3, 1)

    chase_dx = 0
    if squat:
        body_y = ground - body_h - 1
        body_bot = body_y + body_h
        hy = body_y - head_r + 1
        pygame.draw.ellipse(surf, shirt, (cx - body_w, body_y, body_w * 2, body_h + 1))
        pygame.draw.ellipse(surf, shirt_dk, (cx - body_w, body_y, body_w * 2, body_h + 1), 1)
        for sgn in (-1, 1):
            pygame.draw.line(surf, pants, (cx + sgn * body_w * 0.5, body_bot),
                             (cx + sgn * body_w * 1.1, ground), 2)
    elif chase:
        chase_dx = -int(body_w * 0.9)
        body_y = body_y + int(body_h * 0.35)
        body_bot = body_y + body_h
        torso = pygame.Rect(cx + chase_dx - body_w, body_y, int(body_w * 2.4), body_h)
        pygame.draw.ellipse(surf, shirt, torso)
        pygame.draw.ellipse(surf, shirt_dk, torso, 1)
        hy = body_y - head_r + 1
        stride = abs(gait) * body_w * 1.2 + body_w * 0.6
        pygame.draw.line(surf, pants, (cx + chase_dx, body_bot), (cx + chase_dx - stride, ground), 2)
        pygame.draw.line(surf, pants, (cx + chase_dx + body_w * 0.4, body_bot),
                         (cx + chase_dx + stride * 0.7, ground), 2)
    elif tiptoe:
        # NEW STANCE — the child stretches: body lifted off its usual seat, legs
        # dead straight with the heels off the deck and both arms thrown up over a
        # counter edge. Reads as a tall thin exclamation mark, which is the exact
        # opposite of the squat/chase rows and survives the far-lane downscale.
        stretch = 0.5 + 0.5 * math.sin(t * 1.9)
        body_y = ground - int(total * 0.46) - body_h - int(stretch)
        body_bot = body_y + body_h
        hy = body_y - head_r + 1
        pygame.draw.ellipse(surf, shirt, (cx - body_w + 1, body_y, body_w * 2 - 2, body_h + 1))
        pygame.draw.ellipse(surf, shirt_dk, (cx - body_w + 1, body_y, body_w * 2 - 2, body_h + 1), 1)
        for sgn in (-1, 1):
            lx = cx + sgn * body_w * 0.45
            pygame.draw.line(surf, pants, (lx, body_bot), (lx, ground - 1), 2)
            pygame.draw.line(surf, _shade(pants, -22), (lx - 1, ground - 1), (lx + 1, ground), 1)
        for sgn, off in ((-1, 0.0), (1, 0.35)):
            pygame.draw.line(surf, skin, (cx + sgn * body_w * 0.5, body_y + 1),
                             (cx + sgn * body_w * 0.9 - body_w * 0.5,
                              hy - head_r * (1.5 + off * 0.4)), 2)
    else:
        pygame.draw.ellipse(surf, shirt, (cx - body_w, body_y, body_w * 2, body_h + 1))
        pygame.draw.ellipse(surf, shirt_dk, (cx - body_w, body_y, body_w * 2, body_h + 1), 1)
        if not carried:
            swing = gait * body_w * (0.8 if run else 0.4)
            for sgn, sw in ((-1, swing), (1, -swing)):
                fx = cx + sgn * body_w * 0.4 + sw
                pygame.draw.line(surf, pants, (cx + sgn * body_w * 0.4, body_bot), (fx, ground), 2)
        else:
            for sgn in (-1, 1):
                pygame.draw.line(surf, pants, (cx + sgn * body_w * 0.5, body_bot),
                                 (cx + sgn * body_w * 1.0, body_bot + 4), 2)

    if chase:
        hx = cx + chase_dx - int(body_w * 1.0)
        hy = body_y - head_r // 2
    pygame.draw.line(surf, skin_sh, (hx, hy + head_r - 1), (cx + chase_dx, body_y + 1), max(2, head_r // 2))
    pygame.draw.circle(surf, skin, (hx, hy), head_r)
    pygame.draw.circle(surf, skin_sh, (hx, hy), head_r, 1)
    pygame.draw.circle(surf, (38, 26, 20), (hx - head_r // 2, hy), max(1, head_r // 4))

    hairstyle = P.get("hair_style", "bowl")
    if hairstyle == "buns":
        pygame.draw.arc(surf, hair, (hx - head_r, hy - head_r, head_r * 2 + 1, head_r * 2 + 1),
                        math.radians(10), math.radians(170), max(1, head_r // 2))
        for sgn in (-1, 1):
            pygame.draw.circle(surf, hair, (hx + sgn * (head_r + 1), hy - head_r // 2), max(1, head_r // 2))
    elif hairstyle == "tuft":
        pygame.draw.arc(surf, hair, (hx - head_r, hy - head_r, head_r * 2 + 1, head_r * 2 + 1),
                        math.radians(20), math.radians(160), max(1, head_r // 2))
        pygame.draw.circle(surf, hair, (hx, hy - head_r), max(1, head_r // 3))
    elif hairstyle == "sidetails":
        # NEW hair — two tails swinging out past the jaw, so the head silhouette
        # widens at the BOTTOM (buns widen it at the top). A cheap, readable note.
        pygame.draw.circle(surf, hair, (hx, hy - head_r // 3), head_r)
        for sgn in (-1, 1):
            tip = (hx + sgn * (head_r + 2), hy + head_r + 1 + int(gait * 0.8))
            pygame.draw.line(surf, hair, (hx + sgn * head_r, hy - head_r // 3), tip, 2)
            pygame.draw.circle(surf, _shade(hair, -20), tip, 1)
    elif hairstyle == "cap":
        cap = pf(P.get("cap", (210, 90, 80)))
        pygame.draw.circle(surf, cap, (hx, hy - head_r // 3), int(head_r * 1.05))
        pygame.draw.circle(surf, skin, (hx + head_r // 3, hy + head_r // 4), int(head_r * 0.7))
    else:
        pygame.draw.circle(surf, hair, (hx, hy - head_r // 3), head_r)
        pygame.draw.arc(surf, hair, (hx - head_r, hy - head_r, head_r * 2 + 1, head_r * 2 + 1),
                        math.radians(0), math.radians(180), max(1, head_r // 2))

    arm_y = body_y + 1 if not chase else body_y + body_h // 2
    bx = cx + chase_dx
    if chase:
        pygame.draw.line(surf, skin, (bx, arm_y), (bx - body_w * 1.6, arm_y + body_h * 0.3), 2)
    if "point" in v.pose:
        pygame.draw.line(surf, skin, (cx - body_w * 0.4, arm_y), (cx - body_w * 1.7, arm_y - body_h * 0.3), 2)
    if "balloon" in v.accessory:
        bcol = _cap_luma(pf(_knock(P.get("prop", (228, 84, 92)))))
        sx2 = cx + body_w + 2
        pygame.draw.line(surf, (70, 64, 60), (cx + body_w * 0.3, arm_y), (sx2, hy - head_r * 3), 1)
        pygame.draw.circle(surf, bcol, (sx2, hy - head_r * 3 - 2), max(2, int(head_r * 1.2)))
        pygame.draw.circle(surf, _cap_luma(_shade(bcol, 24)), (sx2 - 1, hy - head_r * 3 - 3), max(1, head_r // 2))
    if "kite" in v.accessory:
        kcol = _cap_luma(pf(_knock(P.get("prop", (240, 196, 70)))))
        pygame.draw.line(surf, skin, (cx - body_w * 0.4, arm_y), (cx - body_w * 1.3, arm_y - 2), 2)
        kx, ky = cx + body_w + 4, hy - head_r * 3
        tail = _cap_luma(pf(_knock(P.get("tail", (224, 150, 70)))))
        pygame.draw.line(surf, tail, (cx - body_w * 1.3, arm_y - 2), (kx, ky), 1)
        pygame.draw.polygon(surf, kcol, [(kx, ky - 3), (kx + 3, ky), (kx, ky + 3), (kx - 3, ky)])
        pygame.draw.polygon(surf, _shade(kcol, -34), [(kx, ky - 3), (kx + 3, ky), (kx, ky + 3), (kx - 3, ky)], 1)
    if "stick" in v.accessory:
        scol = pf(P.get("prop", (150, 110, 64)))
        if chase:
            pygame.draw.line(surf, scol, (bx + body_w * 0.4, arm_y), (bx + body_w * 1.8, arm_y - body_h * 0.2), 2)
        else:
            pygame.draw.line(surf, scol, (cx - body_w * 0.4, arm_y), (cx - body_w * 2.4, arm_y - body_h * 0.6), 2)
    if "hoop" in v.accessory:
        hcol = pf(P.get("prop", (150, 110, 64)))
        ring = pygame.Rect(int(bx - body_w * 2.6), int(ground - body_w * 1.6),
                           int(body_w * 1.5), int(body_w * 1.5))
        pygame.draw.ellipse(surf, hcol, ring, 1)
        pygame.draw.line(surf, hcol, (bx, arm_y), (ring.centerx + 1, ring.centery), 1)
    if "candy" in v.accessory:
        ccol = _cap_luma(pf(_knock(P.get("prop", (224, 60, 60)))))
        sx2 = cx - body_w * 0.4
        pygame.draw.line(surf, (150, 120, 70), (sx2, arm_y), (sx2 - 1, hy - head_r * 2), 1)
        for k in range(3):
            pygame.draw.circle(surf, ccol, (int(sx2 - 1), int(hy - head_r * 2 + k * 3)), 2)
    # ── NEW kid props ──
    if "ribbon" in v.accessory:
        # A long wavy streamer trailing BEHIND the runner: a horizontal squiggle
        # twice the child's own width, which is a bigger outline event than any
        # held object could be at 10px.
        rc = _cap_luma(pf(_knock(P.get("prop", (216, 120, 150)))))
        hxr, hyr = cx - body_w * 1.0, arm_y - body_h * 0.5
        pygame.draw.line(surf, skin, (cx - body_w * 0.4, arm_y), (hxr, hyr), 2)
        pts = []
        for k in range(6):
            px = hxr + body_w * (0.6 * k + 0.4)
            py = hyr + math.sin(t * 3.0 + k * 1.1) * (1.2 + 0.35 * k)
            pts.append((px, py))
        pygame.draw.lines(surf, rc, False, pts, 1)
    if "lantern" in v.accessory:
        # Carried FORWARD on a short stick at chest height — deliberately not an
        # overhead sphere, so it never doubles the balloon row's silhouette.
        pc = pf(P.get("stick", (140, 106, 66)))
        lc = _cap_luma(pf(_knock(P.get("prop", (214, 122, 74)))))
        hxp, hyp = cx - body_w * 1.9, arm_y - body_h * 0.7
        pygame.draw.line(surf, skin, (cx - body_w * 0.4, arm_y), (cx - body_w * 1.1, arm_y - 1), 2)
        pygame.draw.line(surf, pc, (cx - body_w * 1.1, arm_y - 1), (hxp, hyp), 1)
        lr = pygame.Rect(int(hxp - 2), int(hyp + 1), 4, 5)
        pygame.draw.ellipse(surf, lc, lr)
        pygame.draw.ellipse(surf, _shade(lc, -40), lr, 1)
        pygame.draw.line(surf, _shade(lc, -50), (lr.left, lr.centery), (lr.right, lr.centery), 1)
    if "satchel" in v.accessory:
        sc = pf(P.get("bag", (146, 122, 86)))
        sr = pygame.Rect(int(cx + body_w * 0.5), int(body_y + body_h * 0.25),
                         int(body_w * 1.2), int(body_h * 1.0))
        pygame.draw.rect(surf, sc, sr, border_radius=1)
        pygame.draw.rect(surf, _shade(sc, -34), sr, 1, border_radius=1)
        pygame.draw.line(surf, _shade(sc, -28), (sr.left, sr.top), (cx - body_w * 0.4, body_y + 1), 1)


# ════════════════════════════════════════════════════════════════════════════
# ELDERS — shipped drawer + the new brush / reading stances and props
# ════════════════════════════════════════════════════════════════════════════

ELDER_H = 17


def draw_elder(surf, cx, base_y, v, night, t):
    P, A = v.palette, v.attrs
    pf = lambda c: _cap_luma(_retint(c, night)) if night > 0.05 else c
    skin = pf(SKIN.get(P.get("skin", "warm"), SKIN["warm"]))
    skin_sh = _shade(skin, -28)
    robe = pf(P["robe"]); robe_dk = pf(P.get("robe_dk", _shade(P["robe"], -42)))
    sash = pf(P.get("sash", _shade(robe, 26)))
    grey = pf(P.get("hair", (210, 208, 200)))
    padded = A.get("padded", False)

    build = A.get("build", 1.0)
    stoop = A.get("stoop", 0.0)
    stance = A.get("stance", "upright")

    total = max(10, int(ELDER_H * A.get("height", 1.0)))
    head_r = max(2, int(total * 0.15))
    torso_h = int(total * 0.42)
    leg_h = max(2, total - torso_h - head_r * 2)
    body_w = max(3, int(total * 0.27 * build))
    ground = int(base_y)
    lean = int(body_w * 1.7 * stoop)

    seated = stance == "seated"
    taichi = stance == "taichi"
    hands_back = stance == "hands_back"
    birds = stance == "birds"
    brush = stance == "brush"
    reading = stance == "reading"

    if seated:
        stool = pf((120, 92, 60))
        sy = ground - leg_h
        pygame.draw.rect(surf, stool, (cx - body_w, sy, body_w * 2, leg_h))
        pygame.draw.rect(surf, _shade(stool, -28), (cx - body_w, sy, body_w * 2, leg_h), 1)
        torso_bot = sy
        torso_top = torso_bot - torso_h
        for sgn in (-1, 1):
            pygame.draw.line(surf, robe_dk, (cx + sgn * body_w * 0.5, torso_bot),
                             (cx + sgn * body_w * 1.2, ground), max(2, body_w // 3))
    else:
        torso_bot = ground - leg_h
        torso_top = torso_bot - torso_h
        if taichi or brush:
            for sgn in (-1, 1):
                pygame.draw.line(surf, robe_dk, (cx + sgn * body_w * 0.4, torso_bot),
                                 (cx + sgn * body_w * 1.5, ground), max(2, body_w // 3))
        else:
            for sgn in (-1, 1):
                pygame.draw.line(surf, robe_dk, (cx + sgn * body_w * 0.3, torso_bot),
                                 (cx + sgn * body_w * 0.3, ground), max(2, body_w // 3))

    torso_top += int(torso_h * 0.5 * stoop)
    head_cy = torso_top - head_r
    hx = cx + lean
    hy = head_cy

    if padded:
        pad = int(body_w * 1.3)
        r = pygame.Rect(cx - pad + lean, torso_top - head_r // 2, pad * 2,
                        (torso_bot - torso_top) + head_r // 2)
        pygame.draw.rect(surf, robe, r, border_radius=max(2, body_w // 5))
        pygame.draw.rect(surf, robe_dk, r, max(2, body_w // 6), border_radius=max(2, body_w // 5))
        fur = pf(P.get("fur", (224, 216, 202)))
        pygame.draw.line(surf, fur, (r.left, r.top), (r.right, r.top), max(2, body_w // 4))
    else:
        sh_w = int(body_w * 0.72); hem_w = int(body_w * (1.4 if not (taichi or brush) else 1.55))
        bot = ground if not seated else torso_bot
        pts = [(cx - sh_w + lean, torso_top), (cx + sh_w + lean, torso_top),
               (cx + hem_w, bot), (cx - hem_w, bot)]
        pygame.draw.polygon(surf, robe, pts)
        pygame.draw.polygon(surf, robe_dk, pts, max(1, body_w // 8))
        sy = torso_top + (torso_bot - torso_top) // 2
        pygame.draw.line(surf, sash, (cx - body_w + lean, sy), (cx + body_w + lean, sy), max(2, body_w // 5))
        if stoop > 0.25:
            pygame.draw.circle(surf, robe_dk, (cx - sh_w + lean + 1, torso_top + 1), max(1, body_w // 4))

    arm_y = torso_top + head_r // 2

    if taichi:
        pygame.draw.line(surf, robe, (cx + lean, arm_y), (cx - body_w * 1.6, arm_y + torso_h * 0.3), max(2, body_w // 4))
        pygame.draw.line(surf, robe, (cx + lean, arm_y + head_r), (cx - body_w * 1.4, arm_y + torso_h * 0.7), max(2, body_w // 4))
        pygame.draw.circle(surf, skin, (int(cx - body_w * 1.6), int(arm_y + torso_h * 0.3)), max(1, body_w // 4))
    elif hands_back:
        pygame.draw.line(surf, robe, (cx + body_w * 0.6 + lean, arm_y),
                         (cx + body_w * 1.5 + lean, arm_y + torso_h * 0.5), max(2, body_w // 4))
        pygame.draw.circle(surf, skin, (int(cx + body_w * 1.5 + lean), int(arm_y + torso_h * 0.5)), max(1, body_w // 4))
    elif birds:
        pygame.draw.line(surf, robe, (cx - body_w * 0.4 + lean, arm_y),
                         (cx - body_w * 1.8, arm_y + torso_h * 0.4), max(2, body_w // 4))
        pygame.draw.circle(surf, skin, (int(cx - body_w * 1.8), int(arm_y + torso_h * 0.4)), max(1, body_w // 4))
        for bx2, by2 in ((cx - body_w * 2.2, ground - 1), (cx - body_w * 1.4, ground)):
            pygame.draw.circle(surf, pf((90, 80, 70)), (int(bx2), int(by2)), 1)
    elif brush:
        # NEW STANCE — water calligraphy. A long brush runs from the low hand all
        # the way to the DECK ahead of the figure, so the silhouette gains a
        # ground-touching diagonal no other elder has; the wet stroke it leaves
        # behind sits on the deck and dries (fades) on a slow cycle.
        bcol = pf(P.get("brush", (126, 96, 62)))
        hxb = cx - body_w * 1.4
        hyb = arm_y + torso_h * 0.45
        tip_x = cx - body_w * 2.9 + math.sin(t * 1.5) * body_w * 0.5
        pygame.draw.line(surf, robe, (cx - body_w * 0.3 + lean, arm_y), (hxb, hyb), max(2, body_w // 4))
        pygame.draw.circle(surf, skin, (int(hxb), int(hyb)), max(1, body_w // 4))
        pygame.draw.line(surf, bcol, (hxb, hyb), (tip_x, ground - 1), max(1, body_w // 5))
        pygame.draw.circle(surf, _shade(bcol, -40), (int(tip_x), int(ground - 1)), 1)
        wet = pf(P.get("wet", (96, 88, 78)))
        for k, wx in enumerate((cx - body_w * 3.4, cx - body_w * 2.2)):
            fade = 0.4 + 0.4 * math.sin(t * 1.1 + k)
            pygame.draw.line(surf, _mix(wet, (140, 130, 112), fade),
                             (wx, ground), (wx + body_w * 0.8, ground), 1)
    elif reading:
        # NEW STANCE — an open scroll held wide at chest height on both hands: a
        # hard horizontal bar across the body, the one elder read that widens the
        # figure instead of extending it.
        sc = _cap_luma(pf(P.get("scroll", (208, 196, 168))))
        sw2 = int(body_w * 2.1)
        sy2 = int(arm_y + torso_h * 0.26)
        for sgn in (-1, 1):
            pygame.draw.line(surf, robe, (cx + sgn * body_w * 0.5 + lean, arm_y),
                             (cx + sgn * sw2 * 0.8, sy2), max(2, body_w // 4))
        r = pygame.Rect(cx - sw2, sy2 - 1, sw2 * 2, max(4, int(torso_h * 0.38)))
        pygame.draw.rect(surf, sc, r)
        pygame.draw.rect(surf, _shade(sc, -46), r, 1)
        for k in range(2):
            pygame.draw.line(surf, _shade(sc, -60), (r.left + 2, r.top + 2 + k * 2),
                             (r.right - 2, r.top + 2 + k * 2), 1)

    pygame.draw.line(surf, skin_sh, (hx, hy + head_r - 1), (hx, torso_top + 1), max(2, head_r // 2))
    pygame.draw.circle(surf, skin, (hx, hy), head_r)
    pygame.draw.circle(surf, skin_sh, (hx, hy), head_r, 1)
    pygame.draw.circle(surf, (40, 28, 22), (hx - head_r // 2, hy - head_r // 6), max(1, head_r // 4))
    if "beard" in v.accessory:
        pygame.draw.polygon(surf, grey, [
            (hx - head_r * 0.6, hy + head_r * 0.3), (hx + head_r * 0.6, hy + head_r * 0.3),
            (hx + head_r * 0.2, hy + head_r * 2.0), (hx - head_r * 0.2, hy + head_r * 2.0)])
        pygame.draw.circle(surf, _shade(grey, -28), (hx, hy + int(head_r * 1.6)), 1)

    head = P.get("head", "bald")
    if head == "bald":
        pygame.draw.arc(surf, grey, (hx - head_r, hy - head_r, head_r * 2 + 1, head_r * 2 + 1),
                        math.radians(190), math.radians(350), max(1, head_r // 2))
    elif head == "bun":
        pygame.draw.circle(surf, grey, (hx, hy - head_r // 2), head_r)
        pygame.draw.circle(surf, _shade(grey, -22), (hx, hy - head_r), max(2, head_r // 2))
    elif head == "cap":
        col = pf(P.get("cap", (120, 96, 70)))
        pygame.draw.circle(surf, col, (hx, hy - head_r // 2), int(head_r * 1.1))
        pygame.draw.circle(surf, skin, (hx, hy + head_r // 4), int(head_r * 0.75))

    if "cane" in v.accessory:
        cane = pf(P.get("cane", (118, 82, 50)))
        tap = int(math.sin(t * 1.3))
        chx = cx + body_w * 1.4 + lean
        pygame.draw.line(surf, cane, (chx, arm_y), (chx + tap, ground), max(2, body_w // 6))
        pygame.draw.line(surf, cane, (chx, arm_y), (chx - 3, arm_y), max(2, body_w // 6))
        pygame.draw.line(surf, robe, (cx + body_w * 0.5 + lean, arm_y), (chx, arm_y), max(2, body_w // 5))
    if "fan" in v.accessory:
        fcol = _cap_luma(pf(P.get("fan", (224, 212, 190))))
        fx = cx - body_w * 1.5 + lean; fy = arm_y - 1
        pygame.draw.line(surf, robe, (cx - body_w * 0.3 + lean, arm_y), (fx, fy), max(2, body_w // 5))
        pygame.draw.polygon(surf, fcol, [(fx, fy), (fx - 4, fy - 4), (fx - 5, fy + 1), (fx - 3, fy + 4)])
        pygame.draw.polygon(surf, _shade(fcol, -40), [(fx, fy), (fx - 4, fy - 4), (fx - 5, fy + 1), (fx - 3, fy + 4)], 1)
    if "birdcage" in v.accessory:
        cage = pf(P.get("cage", (150, 116, 70)))
        cgx = cx + body_w * 1.6 + lean
        pygame.draw.line(surf, robe, (cx + body_w * 0.5 + lean, arm_y), (cgx, arm_y + 1), max(2, body_w // 5))
        cg = pygame.Rect(cgx - 3, arm_y + 2, 7, 9)
        pygame.draw.arc(surf, cage, (cg.left, cg.top - 3, cg.width, 6), math.radians(0), math.radians(180), 1)
        pygame.draw.ellipse(surf, _mix(cage, (40, 35, 30), 0.4), cg)
        for gx in range(cg.left + 1, cg.right, 2):
            pygame.draw.line(surf, cage, (gx, cg.top + 1), (gx, cg.bottom - 1), 1)
        pygame.draw.circle(surf, pf((110, 150, 90)), (cg.centerx, cg.centery + 1), 1)
    if "teacup" in v.accessory:
        tc = _cap_luma(pf(P.get("tea", (228, 222, 210))))
        tx = cx - body_w * 1.2 + lean; ty = arm_y + 1
        pygame.draw.line(surf, robe, (cx - body_w * 0.3 + lean, arm_y), (tx, ty), max(2, body_w // 5))
        pygame.draw.ellipse(surf, tc, (tx - 2, ty - 1, 4, 3))
        pygame.draw.ellipse(surf, _shade(tc, -34), (tx - 2, ty - 1, 4, 3), 1)
    # ── NEW elder props ──
    if "sword" in v.accessory:
        # A straight blade continuing the arm well past the hand: the taichi
        # stance's soft curves get one hard straight edge, which is the whole
        # difference between the two sword/empty-hand rows at 15px.
        bl = _cap_luma(pf(P.get("blade", (168, 176, 184))))
        h0 = (cx - body_w * 1.5, arm_y + torso_h * 0.2)
        tip = (cx - body_w * 3.4, arm_y - torso_h * 0.55 + math.sin(t * 1.4) * 1.5)
        pygame.draw.line(surf, robe, (cx - body_w * 0.3 + lean, arm_y), h0, max(2, body_w // 4))
        pygame.draw.line(surf, bl, h0, tip, 1)
        pygame.draw.line(surf, pf((120, 96, 60)), (h0[0] - 1, h0[1] - 1), (h0[0] + 1, h0[1] + 1), 2)
        tsl = pf(P.get("tassel", (150, 92, 88)))
        pygame.draw.line(surf, tsl, h0, (h0[0] + 2, h0[1] + 3 + math.sin(t * 2.2)), 1)
    if "back_basket" in v.accessory:
        bk = pf(P.get("basket", (166, 126, 76)))
        bwid = int(body_w * 1.25)
        bh = int(torso_h * 1.15)
        br = pygame.Rect(int(cx + body_w * 0.8 + lean), int(torso_top - head_r * 0.8), bwid, bh)
        pygame.draw.polygon(surf, bk, [
            (br.left, br.bottom), (br.right - 1, br.bottom - 1),
            (br.right, br.top + 2), (br.left - 1, br.top)])
        pygame.draw.polygon(surf, _shade(bk, -34), [
            (br.left, br.bottom), (br.right - 1, br.bottom - 1),
            (br.right, br.top + 2), (br.left - 1, br.top)], 1)
        for q in (0.4, 0.75):
            yy = int(br.top + bh * q)
            pygame.draw.line(surf, _shade(bk, -26), (br.left, yy), (br.right - 1, yy), 1)
        grn = pf(P.get("herbs", (104, 128, 92)))
        for gx in (0.25, 0.6):
            pygame.draw.circle(surf, grn, (int(br.left + bwid * gx), br.top), 1)


# ════════════════════════════════════════════════════════════════════════════
# VENDORS — shipped drawer + the new chop / pour / wok actions
# ════════════════════════════════════════════════════════════════════════════

VEND_H = 17


def draw_vendor(surf, cx, base_y, v, night, t):
    P, A = v.palette, v.attrs
    pf = lambda c: _cap_luma(_retint(c, night)) if night > 0.05 else c
    skin = pf(SKIN.get(P.get("skin", "warm"), SKIN["warm"]))
    skin_sh = _shade(skin, -28)
    shirt = pf(P["shirt"]); shirt_dk = pf(P.get("shirt_dk", _shade(P["shirt"], -42)))
    apron = pf(P.get("apron", (206, 196, 176)))
    apron_dk = _shade(apron, -34)
    pants = pf(P.get("pants", (74, 66, 58)))
    hair = pf(P.get("hair", (54, 42, 34)))

    build = A.get("build", 1.05)
    total = max(11, int(VEND_H * A.get("height", 1.0)))
    head_r = max(2, int(total * 0.15))
    torso_h = int(total * 0.46)
    leg_h = max(2, total - torso_h - head_r * 2)
    body_w = max(3, int(total * 0.28 * build))
    ground = int(base_y)
    torso_bot = ground - leg_h
    torso_top = torso_bot - torso_h
    hx = cx; hy = torso_top - head_r
    arm_y = torso_top + head_r // 2
    pose = A.get("pose", "call")

    for sgn in (-1, 1):
        pygame.draw.line(surf, pants, (cx + sgn * body_w * 0.4, torso_bot),
                         (cx + sgn * body_w * 0.4, ground), max(2, body_w // 3))

    heavy = build >= 1.18
    lean = build <= 0.92
    if heavy:
        r = pygame.Rect(int(cx - body_w * 0.92), torso_top, int(body_w * 1.84), torso_h)
        belly = pygame.Rect(int(cx - body_w * 1.18), torso_top + torso_h // 3,
                            int(body_w * 2.36), int(torso_h * 0.7))
        pygame.draw.ellipse(surf, shirt, belly)
        pygame.draw.rect(surf, shirt, r, border_radius=max(2, body_w // 4))
        pygame.draw.ellipse(surf, shirt_dk, belly, 1)
        pygame.draw.rect(surf, shirt_dk, r, max(1, body_w // 8), border_radius=max(2, body_w // 4))
    elif lean:
        pts = [(cx - body_w, torso_top), (cx + body_w, torso_top),
               (int(cx + body_w * 0.6), torso_bot), (int(cx - body_w * 0.6), torso_bot)]
        pygame.draw.polygon(surf, shirt, pts)
        pygame.draw.polygon(surf, shirt_dk, pts, max(1, body_w // 8))
    else:
        r = pygame.Rect(cx - body_w, torso_top, body_w * 2, torso_h)
        pygame.draw.rect(surf, shirt, r, border_radius=max(2, body_w // 4))
        pygame.draw.rect(surf, shirt_dk, r, max(1, body_w // 8), border_radius=max(2, body_w // 4))
    apr = pygame.Rect(cx - body_w * 0.7, torso_top + head_r, body_w * 1.4, torso_h - head_r // 2)
    pygame.draw.rect(surf, apron, apr)
    pygame.draw.rect(surf, apron_dk, apr, 1)
    pygame.draw.line(surf, apron_dk, (cx - body_w * 0.5, torso_top + 1), (apr.left + 1, apr.top), 1)
    pygame.draw.line(surf, apron_dk, (cx + body_w * 0.5, torso_top + 1), (apr.right - 1, apr.top), 1)
    if "rolled" in v.accessory:
        pygame.draw.line(surf, _shade(shirt, 14), (cx - body_w * 0.6, arm_y), (cx - body_w, arm_y + 2), max(2, body_w // 3))
    if "towel" in v.accessory:
        tw = _cap_luma(pf(P.get("towel", (220, 214, 200))))
        pygame.draw.line(surf, tw, (cx + body_w * 0.3, torso_top - 1),
                         (cx + body_w * 0.9, torso_top + torso_h * 0.4), max(2, body_w // 4))

    if pose == "call":
        pygame.draw.line(surf, skin, (cx - body_w * 0.4, arm_y), (hx - head_r, hy + head_r // 2), max(2, body_w // 4))
    elif pose == "weigh":
        pygame.draw.line(surf, shirt, (cx - body_w * 0.4, arm_y), (cx - body_w * 1.5, arm_y - 2), max(2, body_w // 4))
        sx2 = cx - body_w * 1.5
        pygame.draw.line(surf, pf((120, 96, 60)), (sx2, arm_y - 2), (sx2, arm_y - 5), 1)
        for ox in (-3, 3):
            pygame.draw.line(surf, (90, 80, 64), (sx2 + ox, arm_y - 4), (sx2 + ox, arm_y), 1)
            pygame.draw.arc(surf, pf((150, 120, 70)), (sx2 + ox - 2, arm_y - 1, 4, 3), math.radians(180), math.radians(360), 1)
    elif pose == "fan":
        fy = arm_y + int(math.sin(t * 6) * 1)
        pygame.draw.line(surf, shirt, (cx - body_w * 0.4, arm_y), (cx - body_w * 1.4, fy + 2), max(2, body_w // 4))
        pygame.draw.rect(surf, pf((200, 180, 140)), (int(cx - body_w * 1.7), int(fy), 4, 5))
        pygame.draw.rect(surf, pf((140, 110, 70)), (int(cx - body_w * 1.7), int(fy), 4, 5), 1)
    elif pose == "ladle":
        px = cx - body_w * 1.3; py = arm_y + torso_h * 0.6
        for sgn, off in ((-1, 0.0), (1, 0.4)):
            pygame.draw.line(surf, shirt, (cx + sgn * body_w * 0.5, arm_y), (px + off * body_w, py), max(2, body_w // 4))
        pygame.draw.line(surf, pf((150, 120, 70)), (px, py), (px - 2, py + torso_h * 0.4), 1)
        pygame.draw.circle(surf, pf((180, 150, 100)), (int(px - 2), int(py + torso_h * 0.4)), 1)
        pot = pygame.Rect(int(px - body_w * 0.7), int(py + torso_h * 0.3), int(body_w * 1.4), 3)
        pygame.draw.ellipse(surf, pf((110, 92, 70)), pot)
        pygame.draw.ellipse(surf, _shade(pf((110, 92, 70)), -28), pot, 1)
    elif pose == "stack":
        for sgn in (-1, 1):
            pygame.draw.line(surf, shirt, (cx + sgn * body_w * 0.5, arm_y), (cx + sgn * body_w * 0.9, hy), max(2, body_w // 4))
        bk = pf(P.get("basket", (176, 132, 78)))
        for k in range(3):
            br = pygame.Rect(int(cx - body_w * 0.9), int(hy - head_r * 1.3 - k * 4), int(body_w * 1.8), 4)
            pygame.draw.ellipse(surf, bk, br)
            pygame.draw.ellipse(surf, _shade(bk, -30), br, 1)
    elif pose == "sign":
        pygame.draw.line(surf, skin, (cx - body_w * 0.4, arm_y), (cx - body_w * 1.2, arm_y - 1), max(2, body_w // 4))
        if "skewers" in v.accessory:
            for k in range(4):
                pygame.draw.line(surf, pf((150, 120, 70)), (cx - body_w * 1.2 + k, arm_y - 1),
                                 (cx - body_w * 1.6 + k, arm_y - head_r * 2), 1)
                pygame.draw.circle(surf, pf((180, 90, 60)), (int(cx - body_w * 1.6 + k), int(arm_y - head_r * 2)), 1)
        else:
            sg = _cap_luma(pf(_knock(P.get("sign", (168, 78, 70)))))
            sg_hi = _cap_luma(_shade(sg, 26))
            pygame.draw.line(surf, pf((120, 90, 60)), (cx - body_w * 1.2, arm_y - 1), (cx - body_w * 1.2, hy - head_r * 2), 1)
            sr = pygame.Rect(int(cx - body_w * 1.9), int(hy - head_r * 2.6), int(body_w * 1.6), int(head_r * 1.8))
            pygame.draw.rect(surf, sg, sr)
            pygame.draw.rect(surf, _shade(sg, -34), sr, 1)
            pygame.draw.line(surf, sg_hi, (sr.left + 1, sr.centery), (sr.right - 1, sr.centery), 1)
    # ── NEW vendor actions (all upper-body: vendors read chest-up) ──
    elif pose == "chop":
        # 2-beat cleaver: the arm swings from ABOVE the head down to the board, so
        # the figure's topmost point moves by half a head between frames — the
        # loudest motion cue in the family.
        beat = max(0.0, math.sin(t * 5.0))
        hxc = cx - body_w * 1.35
        hyc = arm_y + torso_h * 0.30 - beat * head_r * 3.2
        pygame.draw.line(surf, shirt, (cx - body_w * 0.4, arm_y), (hxc, hyc), max(2, body_w // 4))
        pygame.draw.circle(surf, skin, (int(hxc), int(hyc)), max(1, body_w // 5))
        bl = _cap_luma(pf(P.get("blade", (176, 182, 190))))
        blade = pygame.Rect(int(hxc - body_w * 0.9), int(hyc - 1), max(3, int(body_w * 0.9)), max(2, head_r))
        pygame.draw.rect(surf, bl, blade)
        pygame.draw.rect(surf, _shade(bl, -50), blade, 1)
        board = pf(P.get("board", (146, 116, 76)))
        brd = pygame.Rect(int(cx - body_w * 2.1), int(arm_y + torso_h * 0.62), int(body_w * 1.9), 3)
        pygame.draw.rect(surf, board, brd)
        pygame.draw.rect(surf, _shade(board, -34), brd, 1)
    elif pose == "pour":
        # Long-spout pot held HIGH with a thin thread of tea falling into a cup:
        # a tall arm plus a vertical hairline, unlike any other vendor action.
        lift = math.sin(t * 2.2) * 1.5
        hxp = cx - body_w * 1.25
        hyp = hy + head_r * 0.2 + lift
        pygame.draw.line(surf, shirt, (cx - body_w * 0.4, arm_y), (hxp, hyp), max(2, body_w // 4))
        pot = pf(P.get("pot", (140, 118, 96)))
        pr = pygame.Rect(int(hxp - body_w * 0.6), int(hyp - 1), max(4, int(body_w * 1.1)), max(3, head_r + 1))
        pygame.draw.ellipse(surf, pot, pr)
        pygame.draw.ellipse(surf, _shade(pot, -34), pr, 1)
        spout_tip = (pr.left - body_w * 1.1, pr.centery + 1)
        pygame.draw.line(surf, pot, (pr.left + 1, pr.centery), spout_tip, 1)
        tea = _cap_luma(pf(P.get("tea", (196, 168, 120))))
        cup_y = arm_y + torso_h * 0.66
        pygame.draw.line(surf, tea, spout_tip, (spout_tip[0] - 1, cup_y), 1)
        cup = pygame.Rect(int(spout_tip[0] - 3), int(cup_y), 5, 3)
        pygame.draw.ellipse(surf, _cap_luma(pf((216, 210, 196))), cup)
        pygame.draw.ellipse(surf, (90, 84, 76), cup, 1)
    elif pose == "wok":
        # Both hands on a wide tilted pan with a tossed arc of food above it: the
        # only vendor whose outline is a WIDE ellipse held away from the body.
        toss = math.sin(t * 3.4)
        wx = cx - body_w * 1.5
        wy = arm_y + torso_h * 0.30 + toss
        for sgn, off in ((-1, 0.0), (1, 0.5)):
            pygame.draw.line(surf, shirt, (cx + sgn * body_w * 0.5, arm_y),
                             (wx + off * body_w * 1.6, wy + 1), max(2, body_w // 4))
        pan = pf(P.get("pan", (96, 88, 82)))
        pr = pygame.Rect(int(wx - body_w * 1.0), int(wy - 1), max(6, int(body_w * 2.2)), max(3, head_r + 1))
        pygame.draw.ellipse(surf, pan, pr)
        pygame.draw.ellipse(surf, _shade(pan, -30), pr, 1)
        pygame.draw.line(surf, _shade(pan, 20), (pr.right - 1, pr.centery), (pr.right + body_w * 0.8, pr.centery - 1), 1)
        food = _cap_luma(pf(_knock(P.get("food", (206, 156, 92)))))
        for k in range(3):
            fx = pr.centerx - 2 + k * 2
            fy = pr.top - 2 - abs(math.sin(t * 3.4 + k * 0.7)) * 3
            pygame.draw.circle(surf, food, (int(fx), int(fy)), 1)

    pygame.draw.line(surf, skin_sh, (hx, hy + head_r - 1), (hx, torso_top + 1), max(2, head_r // 2))
    pygame.draw.circle(surf, skin, (hx, hy), head_r)
    pygame.draw.circle(surf, skin_sh, (hx, hy), head_r, 1)
    pygame.draw.circle(surf, (40, 28, 22), (hx - head_r // 2, hy - head_r // 6), max(1, head_r // 4))

    hat = P.get("hat", "none")
    if hat == "conical":
        col = pf(P.get("hat_c", (198, 162, 96))); bw = int(head_r * 2.4)
        pygame.draw.polygon(surf, col, [(hx - bw, hy - head_r * 0.1), (hx, hy - head_r * 1.9), (hx + bw, hy - head_r * 0.1)])
        pygame.draw.polygon(surf, _shade(col, -34), [(hx - bw, hy - head_r * 0.1), (hx, hy - head_r * 1.9), (hx + bw, hy - head_r * 0.1)], 1)
    elif hat == "cloth":
        col = pf(P.get("hat_c", (180, 88, 78)))
        pygame.draw.circle(surf, col, (hx, hy - head_r // 2), int(head_r * 1.1))
        pygame.draw.circle(surf, skin, (hx, hy + head_r // 4), int(head_r * 0.72))
    elif hat == "cap":
        col = pf(P.get("hat_c", (120, 100, 76)))
        cap = pygame.Rect(hx - head_r, hy - int(head_r * 1.5), head_r * 2, int(head_r * 1.3))
        pygame.draw.ellipse(surf, col, cap)
        pygame.draw.line(surf, _shade(col, -24), (hx - head_r, hy - head_r // 2), (hx - head_r - 2, hy - head_r // 3), 2)
    elif hat == "wrap":
        col = pf(P.get("hat_c", (150, 110, 96)))
        pygame.draw.circle(surf, hair, (hx, hy - head_r // 3), head_r)
        band = pygame.Rect(hx - head_r, hy - head_r // 2, head_r * 2, max(2, head_r))
        pygame.draw.ellipse(surf, col, band)
        pygame.draw.circle(surf, _shade(col, -22), (hx + head_r, hy - head_r // 3), max(1, head_r // 2))
    else:
        pygame.draw.circle(surf, hair, (hx, hy - head_r // 3), int(head_r * 0.95))
        pygame.draw.arc(surf, hair, (hx - head_r, hy - head_r, head_r * 2 + 1, head_r * 2 + 1),
                        math.radians(0), math.radians(180), max(1, head_r // 3))


# ════════════════════════════════════════════════════════════════════════════
# THE POOLS — kept rows, new rows, and the retire nominations
# ════════════════════════════════════════════════════════════════════════════

KIDS_KEEP = [
    V(dict(shirt=(90, 165, 220), pants=(58, 52, 56), hair=(46, 36, 30), hair_style="bowl", skin="fair", prop=(150, 110, 64)),
      pose=("chase",), acc=("hoop", "stick"), attrs=dict(age=0.9), label="K2 hoop chase",
      note="KEPT | pose:chase(low lean) | acc:hoop,stick"),
    V(dict(shirt=(250, 200, 70), pants=(70, 56, 48), hair=(40, 32, 28), hair_style="bowl", skin="tan"),
      pose=("squat",), attrs=dict(age=0.55), label="K3 squat play",
      note="KEPT | pose:squat | big head ratio"),
    V(dict(shirt=(120, 200, 130), pants=(64, 58, 50), hair=(50, 40, 32), hair_style="buns", skin="warm", prop=(228, 84, 92)),
      pose=("point",), acc=("balloon",), attrs=dict(age=0.7), label="K4 balloon girl",
      note="KEPT | pose:point | acc:balloon (overhead sphere)"),
    V(dict(shirt=(110, 130, 235), pants=(60, 54, 58), hair=(54, 42, 34), hair_style="bowl", skin="warm", carrier=(96, 84, 110)),
      pose=("carried",), attrs=dict(age=0.2), label="K6 piggyback",
      note="KEPT | pose:carried (rides an adult's back)"),
]

KIDS_NEW = [
    V(dict(shirt=(212, 128, 92), pants=(66, 56, 50), hair=(44, 34, 28), hair_style="bowl", skin="tan"),
      pose=("tiptoe",), attrs=dict(age=0.5), label="K7 tiptoe peek  [NEW STANCE]",
      note="NEW STANCE tiptoe | heels off the deck, legs dead straight, BOTH arms thrown up over a counter — a tall thin figure, the inverse of every crouch/run row"),
    V(dict(shirt=(96, 186, 176), pants=(58, 56, 52), hair=(38, 30, 26), hair_style="tuft", skin="warm", prop=(240, 196, 70), tail=(224, 150, 70)),
      pose=("run",), acc=("kite",), attrs=dict(age=0.8), label="K8 kite runner",
      note="NEW ROW | uses the drawer's KITE branch that NO shipped row ever selected — a high diamond + a long tail line, free variety from existing code"),
    V(dict(shirt=(226, 156, 186), pants=(64, 54, 58), hair=(46, 36, 30), hair_style="sidetails", skin="fair", prop=(216, 120, 150)),
      pose=("run",), acc=("ribbon",), attrs=dict(age=0.65), label="K9 ribbon dancer",
      note="NEW acc ribbon + NEW hair sidetails | a wavy streamer twice the child's width trails behind; the tails widen the head at the JAW (buns widen it on top)"),
    V(dict(shirt=(150, 120, 200), pants=(60, 52, 56), hair=(40, 32, 28), hair_style="bowl", skin="ruddy", prop=(214, 122, 74), stick=(140, 106, 66)),
      acc=("lantern",), attrs=dict(age=0.6), label="K10 lantern on a stick",
      note="NEW acc lantern | held FORWARD on a short stick at chest height, deliberately not overhead so it can never double the balloon row"),
    V(dict(shirt=(120, 158, 108), pants=(62, 56, 48), hair=(52, 40, 32), hair_style="bowl", skin="deep", bag=(146, 122, 86)),
      pose=("run",), acc=("satchel",), attrs=dict(age=0.95), label="K11 satchel runner",
      note="NEW acc satchel | boxy schoolbag squared onto the back + a chest strap: the oldest kid in the pool, a rectangle where the others are round"),
    V(dict(shirt=(232, 176, 96), pants=(68, 58, 50), hair=(44, 34, 28), hair_style="sidetails", skin="warm"),
      pose=("squat",), attrs=dict(age=0.35), label="K12 squat + sidetails",
      note="NEW ROW | second squat, but younger (age0.35) with side-tails — the crouched blob now comes in two clearly different head shapes"),
]

KIDS_CUT = [
    (V(dict(shirt=(235, 95, 90), pants=(74, 60, 52), hair=(58, 44, 36), hair_style="tuft", skin="warm"),
       pose=("run",), attrs=dict(age=0.05), label="K1 toddler run"),
     "its only note is being small — no prop, no stance break; next to K3/K12 it is an anonymous blob, and K8/K9/K11 now carry the running read with real outline events."),
    (V(dict(shirt=(220, 130, 200), pants=(70, 56, 60), hair=(44, 34, 28), hair_style="cap", skin="ruddy", cap=(210, 90, 80), prop=(224, 60, 60)),
       acc=("candy",), attrs=dict(age=0.45), label="K5 candy + cap"),
     "the tanghulu is three 2px dots that vanish in the far lane, leaving the pool's plainest standing body — the weakest outline in the family."),
]

ELDERS_KEEP = [
    V(dict(robe=(86, 96, 140), robe_dk=(52, 60, 100), sash=(200, 188, 150), hair=(208, 206, 198), skin="warm", head="bun"),
      acc=("fan", "beard"), attrs=dict(stance="taichi", height=1.04, build=1.0, fan=(224, 212, 190)),
      label="E2 tai-chi", note="KEPT | stance:taichi | acc:fan,beard"),
    V(dict(robe=(110, 134, 112), robe_dk=(70, 92, 76), sash=(206, 180, 140), hair=(204, 202, 196), skin="tan", head="cap", cap=(120, 96, 70)),
      acc=("birdcage",), attrs=dict(stance="upright", height=1.0, build=1.05, cage=(150, 116, 70)),
      label="E3 birdcage", note="KEPT | stance:upright | acc:birdcage"),
    V(dict(robe=(118, 96, 84), robe_dk=(74, 58, 50), fur=(224, 216, 202), sash=(196, 170, 130), hair=(206, 204, 196), skin="ruddy", head="cap", cap=(110, 90, 66)),
      acc=("teacup", "beard"), attrs=dict(stance="seated", height=0.94, build=1.15, padded=True, tea=(228, 222, 210)),
      label="E5 seated + tea", note="KEPT | stance:seated on a stool | padded"),
    V(dict(robe=(104, 80, 116), robe_dk=(66, 48, 78), sash=(208, 160, 140), hair=(206, 204, 198), skin="deep", head="bun"),
      attrs=dict(stance="birds", height=0.98, build=1.0),
      label="E6 feeding birds", note="KEPT | stance:birds (low palm out, birds peck)"),
]

ELDERS_NEW = [
    V(dict(robe=(96, 110, 118), robe_dk=(58, 72, 80), sash=(184, 180, 156), hair=(210, 208, 200), skin="warm",
           head="bald", brush=(126, 96, 62), wet=(96, 88, 78)),
      acc=("beard",), attrs=dict(stance="brush", height=1.0, build=1.0, stoop=0.30),
      label="E7 water calligrapher  [NEW STANCE]",
      note="NEW STANCE brush | bent deep over a long brush that TOUCHES THE DECK ahead — the only elder whose silhouette reaches the ground away from the feet; wet strokes behind him dry on a slow cycle"),
    V(dict(robe=(126, 108, 92), robe_dk=(82, 68, 56), sash=(196, 182, 152), hair=(208, 206, 198), skin="fair",
           head="cap", cap=(112, 92, 68), scroll=(208, 196, 168)),
      acc=("beard",), attrs=dict(stance="reading", height=1.02, build=1.02),
      label="E8 scroll reader  [NEW STANCE]",
      note="NEW STANCE reading | an open scroll held WIDE on both hands: a hard horizontal bar across the chest — the one elder read that widens rather than extends the figure"),
    V(dict(robe=(92, 108, 96), robe_dk=(56, 72, 62), sash=(190, 184, 150), hair=(206, 204, 198), skin="tan",
           head="bun", blade=(168, 176, 184), tassel=(150, 92, 88)),
      acc=("sword",), attrs=dict(stance="taichi", height=1.06, build=0.96),
      label="E9 sword form",
      note="NEW acc sword | taichi stance + one HARD STRAIGHT edge continuing far past the hand (with a tassel that swings) — soft curves vs a straight line at 15px"),
    V(dict(robe=(120, 116, 88), robe_dk=(78, 76, 56), sash=(190, 176, 138), hair=(204, 202, 196), skin="deep",
           head="cap", cap=(118, 96, 70), basket=(166, 126, 76), herbs=(104, 128, 92), cane=(118, 82, 50)),
      acc=("back_basket", "cane"), attrs=dict(stance="upright", height=0.96, build=1.0, stoop=0.22),
      label="E10 herb gatherer",
      note="NEW acc back_basket | a tall pannier riding on the BACK with herb tufts over its rim; the day cast carried nothing behind the body before"),
    V(dict(robe=(112, 92, 116), robe_dk=(72, 56, 76), sash=(198, 176, 150), hair=(210, 208, 200), skin="warm",
           head="bald", fan=(214, 202, 180)),
      acc=("fan",), attrs=dict(stance="seated", height=0.96, build=1.05),
      label="E11 seated + fan",
      note="ROW | second seated elder, slim build + bald head + fan instead of padded/cap/teacup — the stool row now has two clearly different masses"),
    V(dict(robe=(100, 96, 108), robe_dk=(62, 60, 70), fur=(216, 208, 194), sash=(186, 180, 160), hair=(208, 206, 198),
           skin="fair", head="cap", cap=(106, 88, 70), tea=(224, 218, 206)),
      acc=("teacup", "beard"), attrs=dict(stance="upright", height=0.98, build=1.12, padded=True),
      label="E12 padded upright + tea",
      note="ROW | the padded winter mass on its FEET (E5's padding only ever appeared sitting) — a boxy standing elder for the cold beats"),
]

ELDERS_CUT = [
    (V(dict(robe=(92, 72, 108), robe_dk=(58, 44, 74), sash=(196, 180, 150), hair=(212, 210, 202), skin="fair", head="bald", cane=(118, 82, 50)),
       acc=("beard", "cane"), attrs=dict(stance="stoop", stoop=0.46, height=0.92, build=0.95), label="E1 stoop + cane"),
     "a straight duplicate of ped_cast's A_STOOP cane elders — the adult pool already walks four of this exact construction down the same street."),
    (V(dict(robe=(128, 124, 112), robe_dk=(84, 82, 72), sash=(186, 188, 196), hair=(210, 208, 200), skin="warm", head="bald"),
       acc=("beard",), attrs=dict(stance="hands_back", stoop=0.18, height=1.02, build=0.98), label="E4 hands-behind"),
     "an upright robe with both arms tucked behind it: zero outline breakers, the plainest figure in the whole day cast."),
]

VENDORS_KEEP = [
    V(dict(shirt=(78, 124, 124), shirt_dk=(48, 84, 84), apron=(206, 196, 176), pants=(66, 58, 50), hair=(40, 32, 28), skin="warm", hat="wrap", hat_c=(150, 110, 96)),
      attrs=dict(pose="weigh", height=1.12, build=0.9), label="V2 weighing (lean/tall)",
      note="KEPT | pose:weigh | lean build, head wrap"),
    V(dict(shirt=(158, 128, 78), shirt_dk=(108, 84, 50), apron=(210, 196, 172), pants=(64, 58, 48), hair=(50, 40, 32), skin="deep", hat="cap", hat_c=(120, 100, 76), towel=(220, 214, 200)),
      acc=("rolled", "towel"), attrs=dict(pose="fan", height=0.98, build=1.24), label="V3 fanning grill (heavy)",
      note="KEPT | pose:fan | heavy-set barrel body"),
    V(dict(shirt=(118, 116, 80), shirt_dk=(78, 78, 52), apron=(204, 192, 170), pants=(60, 56, 46), hair=(44, 34, 28), skin="ruddy", hat="none"),
      acc=("rolled",), attrs=dict(pose="ladle", height=1.0, build=1.06), label="V4 ladling (bare-head)",
      note="KEPT | pose:ladle (2-hand downward) | bare head"),
    V(dict(shirt=(100, 108, 124), shirt_dk=(64, 72, 90), apron=(200, 192, 178), pants=(58, 60, 70), hair=(54, 42, 34), skin="warm", hat="conical", hat_c=(184, 150, 88), basket=(176, 132, 78)),
      attrs=dict(pose="stack", height=1.04, build=1.0), label="V5 stacking baskets",
      note="KEPT | pose:stack | conical hat"),
    V(dict(shirt=(140, 104, 130), shirt_dk=(94, 66, 90), apron=(206, 194, 174), pants=(64, 56, 58), hair=(50, 40, 32), skin="fair", hat="cloth", hat_c=(150, 100, 84), sign=(168, 78, 70)),
      attrs=dict(pose="sign", height=1.0, build=1.04), label="V7 sign-board (cooled)",
      note="KEPT | pose:sign | price board cooled + capped <=150"),
]

VENDORS_NEW = [
    V(dict(shirt=(150, 86, 70), shirt_dk=(104, 56, 46), apron=(214, 200, 178), pants=(70, 60, 52), hair=(46, 36, 30),
           skin="tan", hat="wrap", hat_c=(146, 108, 92), blade=(176, 182, 190), board=(146, 116, 76)),
      acc=("rolled",), attrs=dict(pose="chop", height=1.0, build=1.1), label="V8 cleaver chop  [NEW POSE]",
      note="NEW POSE chop | 2-beat: the cleaver swings from ABOVE the head down to the board, so the figure's topmost point moves half a head between frames — the loudest motion cue in the family"),
    V(dict(shirt=(88, 110, 148), shirt_dk=(54, 70, 104), apron=(204, 194, 176), pants=(60, 58, 62), hair=(40, 32, 28),
           skin="fair", hat="cap", hat_c=(112, 96, 74), pot=(140, 118, 96), tea=(196, 168, 120)),
      acc=("towel",), attrs=dict(pose="pour", height=1.04, build=0.98), label="V9 long-spout tea pour  [NEW POSE]",
      note="NEW POSE pour | pot held HIGH beside the head + a hairline thread of tea falling into a cup: a tall arm plus a vertical line, unlike any other action"),
    V(dict(shirt=(126, 92, 84), shirt_dk=(84, 58, 52), apron=(208, 196, 176), pants=(66, 56, 50), hair=(50, 40, 32),
           skin="deep", hat="none", pan=(96, 88, 82), food=(206, 156, 92)),
      acc=("rolled", "towel"), attrs=dict(pose="wok", height=0.98, build=1.16), label="V10 wok toss  [NEW POSE]",
      note="NEW POSE wok | both hands on a WIDE tilted pan held away from the body with food arcing above it — the only vendor whose outline is a broad horizontal ellipse"),
    V(dict(shirt=(112, 128, 96), shirt_dk=(72, 88, 62), apron=(208, 198, 176), pants=(62, 58, 48), hair=(44, 34, 28),
           skin="ruddy", hat="cloth", hat_c=(148, 104, 88)),
      acc=("rolled",), attrs=dict(pose="weigh", height=0.96, build=1.22), label="V11 weighing (heavy)",
      note="ROW | the scale action on a HEAVY body under a cloth hat — V2's read at the opposite end of the build range"),
    V(dict(shirt=(132, 112, 148), shirt_dk=(88, 72, 104), apron=(202, 190, 172), pants=(58, 54, 60), hair=(52, 42, 34),
           skin="warm", hat="none", basket=(186, 168, 132)),
      attrs=dict(pose="stack", height=1.10, build=0.9), label="V12 cloth-bolt stacker (lean)",
      note="ROW | the stack action on a LEAN/TALL bare-headed body with pale cloth bolts instead of baskets — same branch, different mass and cargo"),
]

VENDORS_CUT = [
    (V(dict(shirt=(150, 86, 70), shirt_dk=(104, 56, 46), apron=(214, 200, 178), pants=(70, 60, 52), hair=(46, 36, 30), skin="tan", hat="conical", hat_c=(196, 158, 92)),
       acc=("rolled", "towel"), attrs=dict(pose="call", height=1.0, build=1.08), label="V1 calling"),
     "the whole action is one short arm to the mouth; cropped at the counter it is an apron torso with no outline event at all."),
    (V(dict(shirt=(168, 120, 84), shirt_dk=(114, 78, 54), apron=(208, 198, 178), pants=(70, 60, 50), hair=(40, 32, 28), skin="tan", hat="cap", hat_c=(110, 96, 74)),
       acc=("skewers",), attrs=dict(pose="sign", height=1.0, build=1.05), label="V6 skewers"),
     "four 1px skewers dissolve in the far lane and it shares pose:sign with V7 — so it reads as the sign vendor minus the sign."),
]

FAMILIES = [
    ("KIDS", "kid", KIDS_KEEP, KIDS_NEW, KIDS_CUT),
    ("ELDERS", "elder", ELDERS_KEEP, ELDERS_NEW, ELDERS_CUT),
    ("VENDORS", "vendor", VENDORS_KEEP, VENDORS_NEW, VENDORS_CUT),
]

DRAWERS = {"kid": draw_kid, "elder": draw_elder, "vendor": draw_vendor}


# ════════════════════════════════════════════════════════════════════════════
# SHEET RENDERER
# ════════════════════════════════════════════════════════════════════════════

W = 1300
PAD = 12
BG_DAY = (150, 140, 118)
BG_NIGHT = (40, 46, 70)


def _draw_at(fam, surf, cx, base_y, v, night, t):
    DRAWERS[fam](surf, cx, base_y, v, night, t)


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


def _fig_surface(fam, v, night, t, w=52, h=46):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    _draw_at(fam, s, w // 2, h - 3, v, night, t)
    return s


def _figure_cell(parent, fam, v, x, y, w, h, night):
    is_night = night > 0.5
    bg = BG_NIGHT if is_night else BG_DAY
    cell = pygame.Surface((w, h))
    cell.fill(bg)
    deck = _mix(bg, (0, 0, 0), 0.18)
    base = h - 16
    pygame.draw.rect(cell, deck, (0, base, w, h - base))
    pygame.draw.line(cell, _shade(bg, 24), (0, base), (w, base), 1)

    for i, tt in enumerate((0.15, 0.62)):
        _draw_at(fam, cell, 24 + i * 46, base, v, night, tt)
        _text(cell, f"t{i}", 18 + i * 46, base + 2, 8, _shade(bg, 60))

    nat = _fig_surface(fam, v, night, 0.62)
    far = pygame.transform.scale(nat, (int(nat.get_width() * 0.78), int(nat.get_height() * 0.78)))
    cell.blit(far, (108, base - far.get_height() + 3))
    _text(cell, "FAR .78x", 104, base + 2, 8, _shade(bg, 60))

    zoom = pygame.transform.scale(nat, (nat.get_width() * 3, nat.get_height() * 3))
    zw, zh = zoom.get_size()
    zx, zy = w - zw - 8, 16
    pygame.draw.rect(cell, _shade(bg, -20), (zx - 2, zy - 2, zw + 4, zh + 4))
    cell.blit(zoom, (zx, zy))
    pygame.draw.rect(cell, _shade(bg, 40), (zx - 2, zy - 2, zw + 4, zh + 4), 1)

    _gold_coin(cell, w - 14, h - 12, r=6)
    _text(cell, v.label, 6, 4, 12, (240, 236, 226), bold=True)
    _wrap(cell, v.note, 6, 19, zx - 14)
    parent.blit(cell, (x, y))
    pygame.draw.rect(parent, (70, 74, 90), (x, y, w, h), 1)


def _measure_night_cap():
    night = 0.95
    strip = pygame.Surface((1400, 90))
    strip.fill(BG_NIGHT)
    base = 72
    x = 40
    for _nm, fam, keep, new, _cut in FAMILIES:
        for v in keep + new:
            for tt in (0.0, 0.4, 0.9):
                _draw_at(fam, strip, x, base, v, night, tt)
                x += 22
                if x > 1360:
                    x = 40
            x += 4
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
    cell_w = (W - PAD * 4) // 3
    cell_h = 132
    band_h = 104
    strip_h = 96

    n_new = sum(len(n) for _l, _f, _k, n, _c in FAMILIES)
    new_rows = (n_new + 2) // 3
    head_h = 72
    secA_h = 24 + len(FAMILIES) * (band_h + 6)
    secB_h = 24 + 2 * (16 + new_rows * (cell_h + 6))
    secC_h = 24 + len(FAMILIES) * (86 + 6)
    secD_h = 24 + 2 * (strip_h + 6)
    total_h = head_h + secA_h + secB_h + secC_h + secD_h + PAD * 6 + 24

    sheet = pygame.Surface((W, total_h))
    sheet.fill((26, 28, 38))

    y = PAD
    _text(sheet, "SKYBIT PROMENADE — DAY-CAST VARIETY EXPANSION (round 3): KIDS 6→10 · ELDERS 6→10 · VENDORS 7→10  (17 new rows, 6 retires)",
          PAD, y, 17, (250, 246, 236), bold=True)
    y += 22
    y = _wrap(sheet,
              "Every family gains at least one NEW pose/stance branch on its shared drawer, not just palettes — KIDS: tiptoe (heels up, both arms over a counter). "
              "ELDERS: brush (bent over a long water-calligraphy brush that touches the deck) and reading (an open scroll held wide across the chest). "
              "VENDORS: chop (cleaver from above the head to the board, 2-beat), pour (long-spout pot high + a thread of tea) and wok (a wide tilted pan with food tossed above it). "
              "The remaining new rows re-dress existing branches with new props/hair/builds (kite — a branch no shipped row ever used — ribbon, lantern-on-a-stick, satchel, side-tails, sword, back-basket, cloth bolts). "
              "Two retires per family are nominated below with reasons; the pools land at 10/10/10 after they go.",
              PAD, y, W - PAD * 2, 9, (188, 186, 200))
    y = head_h + PAD

    # ── A. true-size bands per family (kept + new together) ──
    _text(sheet, "A.  TRUE-SIZE BANDS — the pool as it would ship (kept rows then NEW rows), day deck, gold-coin yardstick",
          PAD, y, 13, (240, 220, 150), bold=True)
    y += 22
    for name, fam, keep, new, _cut in FAMILIES:
        row = pygame.Surface((W - PAD * 2, band_h))
        row.fill(BG_DAY)
        deck = _mix(BG_DAY, (0, 0, 0), 0.18)
        base = band_h - 26
        pygame.draw.rect(row, deck, (0, base, W - PAD * 2, 26))
        pygame.draw.line(row, _shade(BG_DAY, 26), (0, base), (W - PAD * 2, base), 1)
        _text(row, f"{name}  ({len(keep)} kept + {len(new)} new = {len(keep) + len(new)})", 6, 4, 11, (58, 48, 38), bold=True)
        _gold_coin(row, W - PAD * 2 - 24, 26)
        _text(row, "coin ref", W - PAD * 2 - 46, 38, 8, _shade(BG_DAY, 50))
        pool = keep + new
        spacing = (W - PAD * 2 - 120) // len(pool)
        for i, v in enumerate(pool):
            cx = 50 + i * spacing
            _draw_at(fam, row, cx, base, v, 0.0, 0.35 + i * 0.41)
            _text(row, v.label.split(" ")[0], cx - 9, base + 2, 8, (70, 58, 46))
            if i >= len(keep):
                _text(row, "NEW", cx - 9, base + 12, 8, (24, 92, 62), bold=True)
        sheet.blit(row, (PAD, y))
        pygame.draw.rect(sheet, (70, 74, 90), (PAD, y, W - PAD * 2, band_h), 1)
        y += band_h + 6

    # ── B. per-new-row detail cells, day then night ──
    _text(sheet, "B.  EVERY NEW ROW — native size across 2 motion frames · FAR 0.78x crisp · 3x zoom · in-cell coin   (DAY block, then NIGHT block)",
          PAD, y, 13, (240, 220, 150), bold=True)
    y += 22
    allnew = [(fam, v) for _l, fam, _k, new, _c in FAMILIES for v in new]
    for is_night in (False, True):
        night = 0.95 if is_night else 0.0
        _text(sheet, "NIGHT  (cooled toward (54,64,96), <=150 luma)" if is_night else "DAY",
              PAD, y, 11, (160, 180, 220) if is_night else (240, 210, 130), bold=True)
        y += 16
        for i, (fam, v) in enumerate(allnew):
            cx = PAD + (i % 3) * (cell_w + PAD)
            _figure_cell(sheet, fam, v, cx, y, cell_w, cell_h, night)
            if i % 3 == 2:
                y += cell_h + 6
        if len(allnew) % 3:
            y += cell_h + 6

    # ── C. cut list ──
    _text(sheet, "C.  RETIRE NOMINATIONS — two per family, each a row whose outline adds nothing the survivors don't already say",
          PAD, y, 13, (240, 150, 140), bold=True)
    y += 22
    for name, fam, _k, _n, cut in FAMILIES:
        cb = pygame.Surface((W - PAD * 2, 86))
        cb.fill((44, 34, 38))
        _text(cb, name, 8, 4, 11, (240, 190, 186), bold=True)
        for i, (v, reason) in enumerate(cut):
            ox = 90 + i * ((W - PAD * 2 - 100) // 2)
            _draw_at(fam, cb, ox, 62, v, 0.0, 0.5 + i * 0.4)
            pygame.draw.line(cb, (216, 96, 92), (ox - 12, 34), (ox + 12, 64), 2)
            pygame.draw.line(cb, (216, 96, 92), (ox + 12, 34), (ox - 12, 64), 2)
            _text(cb, v.label, ox + 22, 22, 10, (240, 206, 202), bold=True)
            _wrap(cb, reason, ox + 22, 36, (W - PAD * 2 - 120) // 2 - 30, 9, (222, 196, 194))
        sheet.blit(cb, (PAD, y))
        pygame.draw.rect(sheet, (120, 74, 78), (PAD, y, W - PAD * 2, 86), 1)
        y += 86 + 6

    # ── D. on-street composite ──
    _text(sheet, "D.  ON-STREET COMPOSITE — all three expanded pools mixed at true size behind a counter line, with the coin yardstick  (DAY then NIGHT)",
          PAD, y, 13, (240, 220, 150), bold=True)
    y += 22
    mix = []
    for name, fam, keep, new, _c in FAMILIES:
        for v in new:
            mix.append((fam, v))
        for v in keep[:2]:
            mix.append((fam, v))
    for is_night in (False, True):
        night = 0.95 if is_night else 0.0
        bg = BG_NIGHT if is_night else BG_DAY
        strip = pygame.Surface((W - PAD * 2, strip_h))
        strip.fill(bg)
        deck = _mix(bg, (0, 0, 0), 0.2)
        base = strip_h - 22
        counter_y = base - 22
        pygame.draw.rect(strip, _mix(bg, (110, 84, 54), 0.5 if not is_night else 0.3),
                         (0, counter_y, W - PAD * 2, 3))
        pygame.draw.rect(strip, deck, (0, base, W - PAD * 2, strip_h - base))
        pygame.draw.line(strip, _shade(bg, 24), (0, base), (W - PAD * 2, base), 1)
        spacing = (W - PAD * 2 - 60) // len(mix)
        for i, (fam, v) in enumerate(mix):
            _draw_at(fam, strip, 34 + i * spacing, base - (i % 3), v, night, 0.3 + i * 0.37)
        _gold_coin(strip, W - PAD * 2 - 18, 20)
        _text(strip, "coin ref", W - PAD * 2 - 44, 32, 8, _shade(bg, 60))
        _text(strip, "NIGHT" if is_night else "DAY", 4, 2, 9,
              (170, 190, 225) if is_night else (60, 50, 40), bold=True)
        sheet.blit(strip, (PAD, y))
        pygame.draw.rect(sheet, (70, 74, 90), (PAD, y, W - PAD * 2, strip_h), 1)
        y += strip_h + 6

    hottest, over = _measure_night_cap()
    coin_l = _luma((255, 232, 150))
    msg = (f"NIGHT-CAP AUDIT (measured on RENDERED pixels, all 30 shipping rows x 3 motion phases): hottest day-cast px luma = {hottest:.0f}  ·  "
           f"px over {NIGHT_GLOW_CAP} = {over}  ·  gold-coin core luma = {coin_l:.0f} (sole brightest).  "
           f"{'PASS — every day-cast px sits under the cap.' if over == 0 else 'FAIL — ' + str(over) + ' px breach the cap.'}")
    _text(sheet, msg, PAD, total_h - 18, 9, (170, 200, 180) if over == 0 else (220, 140, 130))

    out = "/home/user/skybit/docs/sidewalk_overhaul/day_cast/round_3.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("saved", out, sheet.get_size())
    print(f"night-cap: hottest={hottest:.1f} over={over} coin={coin_l:.1f}")


if __name__ == "__main__":
    render()
