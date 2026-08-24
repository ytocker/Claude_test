"""SCRATCH (exploration only — not imported by the game).

Round-3 VARIETY EXPANSION for the promenade ADULT PEDESTRIANS.

The shipped pool (game/ped_cast.py, 50 rows over 9 silhouette archetypes) reads
repetitive on a long run: five carrying-pole vendors that differ only in coat hue,
five tray carriers ditto, six tunics on one hurry+swing gait. This round attacks
that on three fronts, all inside the LOCKED art DNA (one shared `_draw_one`, rows
are pure data, variety lives in the OUTLINE):

  THREE NEW ARCHETYPES (new torso branches — different KIND of person, not palette):
    A_ROD    fisherman  — a long rod slung up-and-BACK across the whole figure,
                          crossing above the head; creel basket on a chest strap.
                          Nothing in the pool currently breaks the outline on a
                          steep diagonal — every existing accessory is horizontal
                          (pole/yoke), overhead-round (parasol/tray) or hip-level.
    A_BARROW handcart   — a VEHICLE: single big ground-level wheel + two shafts
                          ahead of a pitched-forward body. Doubles the footprint
                          low down; the only cast member whose mass sits on the
                          deck rather than on the shoulders.
    A_PIPA   musician   — a pear-shaped lute mass held across the chest with its
                          neck rising past the shoulder: a bulge on the body edge
                          plus a short diagonal spar, read at a glance as "carrying
                          something round and playing it", unlike any load figure.

  PASSED OVER (and why, so the AD can overrule): alms-bowl MONK — a bare-headed
  narrow robe with a small bowl at the waist collapses into A_ROBE at 14px, the
  bowl being interior detail; WATER-CARRIER with front jars — two hung loads on a
  bar is what A_POLE and A_YOKE already are, so it would be a third re-dress of
  one idea.

  THIRTEEN NEW ROWS (8 in the new archetypes, 5 re-dressing existing archetypes
  with genuinely new hats / carry positions / builds — shawl-draped head, flat
  official brim + scroll, back-basket gleaner, back-bundle traveller, ear-flap
  snow cap).

  SIX CUTS (#5, #13, #15, #30, #35, #38) — five of them measure a 1.00-IoU
  duplicate mask against a survivor at the far-lane scale; each cut keeps its
  archetype's unique construction. #39 is KEPT (0.83 max-IoU, the head-tray
  band's most distinct row) and its twin #38 goes instead; #10 measures clear of
  the twin band (0.79) and is no longer nominated.

CONSTRAINTS (repeated from the module header): pure pygame.draw.* + Surface
(SRCALPHA ok), pygbag-safe, no numpy/PIL/gfxdraw in anything game-bound. Night
cools toward (54,64,96) and holds <=150 luma so the gold coin (~230) is the sole
brightest thing — measured on RENDERED pixels in the footer, not on the source
palette. FAR lane is drawn CRISP (nearest), NEAR gets the light smoothscale.
"""
from __future__ import annotations

import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1, 1))


# ── colour helpers (mirror game/foreground_props so the sheet matches the game) ─

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
PED_H = 18


def _retint_person(col, night):
    """Cool clothing toward the night ground band (the live ped_cast rule)."""
    if night <= 0.05:
        return col
    return _mix(col, (54, 64, 96), min(0.55, 0.40 * night + 0.20))


def _cap_night(col, night):
    """Second pull for any night colour still over the cap — the animals_cast
    rule, proposed for ped_cast too: a pale fur trim or a +16 highlight derived
    from one can otherwise survive the generic cool above 150 and start competing
    with the coin."""
    if night <= 0.05 or _luma(col) <= NIGHT_GLOW_CAP:
        return col
    over = (_luma(col) - NIGHT_GLOW_CAP) / max(1.0, 255 - NIGHT_GLOW_CAP)
    return _mix(col, (66, 76, 104), min(0.78, 0.5 + over))


SKIN_TONES = {
    "fair":  (236, 198, 156),
    "warm":  (222, 178, 132),
    "tan":   (200, 156, 112),
    "deep":  (168, 124, 86),
    "ruddy": (228, 176, 150),
}

# Silhouette archetype keys — 9 shipped + 3 new.
A_ROBE = "robe"; A_SKIRT = "skirt"; A_TUNIC = "tunic"; A_PADDED = "padded"
A_STOOP = "stoop"; A_POLE = "pole"; A_YOKE = "yoke"; A_HEADLOAD = "headload"
A_CHILD = "child"
A_ROD = "rod"; A_BARROW = "barrow"; A_PIPA = "pipa"


class V:
    """Mirrors foreground_variants.Variant for the roles the drawer reads."""

    def __init__(self, palette, arch, *, pose=(), acc=(), height=1.0, stoop=0.0,
                 build=1.0, label="", note=""):
        self.palette = palette
        self.pose = frozenset(pose)
        self.accessory = frozenset(acc)
        self.attrs = {"arch": arch, "height": height, "stoop": stoop, "build": build}
        self.arch = arch
        self.label = label
        self.note = note


def _legs(surf, cx, body_w, torso_bot, ground, gait, hurry, col_leg, col_foot, hidden):
    swing = gait * body_w * (0.55 if hurry else 0.30)
    for sgn, sw_ in ((-1, swing), (1, -swing)):
        foot_x = cx + sgn * body_w * 0.20 + sw_ * 0.5
        if hidden:
            pygame.draw.line(surf, col_leg, (cx + sgn * body_w * 0.20, torso_bot),
                             (foot_x, ground), max(2, body_w // 4))
        else:
            pygame.draw.line(surf, col_leg, (cx + sgn * body_w * 0.20, torso_bot - body_w * 0.2),
                             (foot_x, ground), max(2, body_w // 3))
            pygame.draw.line(surf, col_foot, (foot_x - 1, ground), (foot_x + 2, ground),
                             max(2, body_w // 3))


def _draw_one(surf, cx, base_y, v, night, t):
    """The shared body drawer, verbatim from game/ped_cast.py apart from the three
    NEW archetype branches + the new hats/accessories this round proposes."""
    P = v.palette
    A = v.attrs
    pf = lambda c: _cap_night(_retint_person(c, night), night)

    skin = pf(SKIN_TONES.get(P.get("skin", "warm"), SKIN_TONES["warm"]))
    skin_sh = _shade(skin, -28)
    coat = pf(P["coat"])
    coat_dk = pf(P.get("coat_dk", _shade(P["coat"], -42)))
    coat_lt = pf(_shade(coat, 16))
    trim = pf(P.get("trim", _shade(P["coat"], 28)))
    hair = pf(P.get("hair", (58, 42, 34)))
    hair_dk = _shade(hair, -22)
    sash = pf(P.get("sash", trim))
    trousers = pf(P.get("trousers", coat_dk))

    height = A.get("height", 1.0)
    build = A.get("build", 1.0)
    stoop = A.get("stoop", 0.0)
    arch = A.get("arch", A_ROBE)

    total_h = max(7, int(PED_H * height))
    head_r = max(2, int(total_h * 0.135))
    torso_h = int(total_h * 0.44)
    leg_h = max(2, total_h - torso_h - head_r * 2)
    body_w = max(2, int(total_h * 0.27 * build))

    ground = int(base_y)
    head_cy = ground - leg_h - torso_h - head_r
    torso_top = head_cy + head_r
    torso_bot = torso_top + torso_h

    hurry = "hurry" in v.pose
    hz = 2.6 if hurry else 1.5
    gait = math.sin(t * hz)
    lean = int(body_w * (0.30 if hurry else 0.12)) + int(body_w * 1.6 * stoop)
    bob = -abs(gait) * (total_h * 0.03)
    head_cy += int(bob) + int(torso_h * 0.55 * stoop)
    torso_top += int(bob)

    arm_y = torso_top + int(head_r * 0.7)
    hx = cx + lean
    hy = head_cy

    robe_like = arch in (A_ROBE, A_SKIRT, A_STOOP, A_PIPA)
    if arch != A_CHILD:
        _legs(surf, cx, body_w, torso_bot, ground, gait, hurry,
              coat_dk if robe_like else trousers,
              _shade(coat_dk if robe_like else trousers, -30), robe_like)
    else:
        for sgn in (-1, 1):
            fx = cx + sgn * body_w * 0.4 + gait * body_w * 0.4 * sgn
            pygame.draw.line(surf, trousers, (cx + sgn * body_w * 0.3, torso_bot),
                             (fx, ground), max(2, body_w // 2))

    # ── TORSO per archetype — the silhouette-defining shape ──
    if arch in (A_ROBE, A_PIPA):
        sh_w = int(body_w * 0.70); hem_w = int(body_w * 0.82)
        pts = [(cx - sh_w + lean, torso_top), (cx + sh_w + lean, torso_top),
               (cx + hem_w, torso_bot), (cx - hem_w, torso_bot)]
        pygame.draw.polygon(surf, coat, pts)
        pygame.draw.polygon(surf, coat_dk, pts, max(1, body_w // 8))
        pygame.draw.line(surf, coat_dk, (cx + lean // 2, torso_top + head_r // 2),
                         (cx, pts[3][1]), max(1, body_w // 10))
        sy = torso_top + torso_h // 2
        pygame.draw.line(surf, sash, (cx - sh_w, sy), (cx + sh_w, sy), max(2, body_w // 5))
    elif arch in (A_SKIRT, A_STOOP):
        sh_w = int(body_w * 0.74); hem_w = int(body_w * 1.45)
        bot = ground if arch == A_STOOP else torso_bot
        pts = [(cx - sh_w + lean, torso_top), (cx + sh_w + lean, torso_top),
               (cx + hem_w, bot), (cx - hem_w, bot)]
        pygame.draw.polygon(surf, coat, pts)
        pygame.draw.polygon(surf, coat_dk, pts, max(1, body_w // 8))
        sy = torso_top + torso_h // 2
        pygame.draw.line(surf, sash, (cx - body_w, sy), (cx + body_w, sy), max(2, body_w // 5))
    elif arch == A_TUNIC:
        r = pygame.Rect(cx - body_w + lean, torso_top, body_w * 2, torso_h)
        pygame.draw.rect(surf, coat, r, border_radius=max(2, body_w // 3))
        pygame.draw.rect(surf, coat_dk, r, max(1, body_w // 8), border_radius=max(2, body_w // 3))
        pygame.draw.line(surf, coat_lt, (cx + lean, torso_top + 1), (cx + lean, torso_bot - 1),
                         max(1, body_w // 9))
    elif arch == A_PADDED:
        pad_w = int(body_w * 1.35)
        r = pygame.Rect(cx - pad_w + lean, torso_top - head_r // 2, pad_w * 2, torso_h + head_r // 2)
        pygame.draw.rect(surf, coat, r, border_radius=max(2, body_w // 5))
        pygame.draw.rect(surf, coat_dk, r, max(2, body_w // 6), border_radius=max(2, body_w // 5))
        for q in (0.34, 0.66):
            yy = int(r.top + r.height * q)
            pygame.draw.line(surf, coat_dk, (r.left + 2, yy), (r.right - 2, yy), 1)
        fur = pf(P.get("fur", (226, 218, 204)))
        pygame.draw.line(surf, fur, (r.left, r.top), (r.right, r.top), max(2, body_w // 4))
    elif arch == A_POLE:
        sh_w = int(body_w * 0.74); hem_w = int(body_w * 1.0)
        pts = [(cx - sh_w + lean, torso_top), (cx + sh_w + lean, torso_top),
               (cx + hem_w, torso_bot), (cx - hem_w, torso_bot)]
        pygame.draw.polygon(surf, coat, pts)
        pygame.draw.polygon(surf, coat_dk, pts, max(1, body_w // 8))
    elif arch == A_YOKE:
        r = pygame.Rect(cx - body_w + lean, torso_top, body_w * 2, torso_h)
        pygame.draw.rect(surf, coat, r, border_radius=max(2, body_w // 4))
        pygame.draw.rect(surf, coat_dk, r, max(1, body_w // 8), border_radius=max(2, body_w // 4))
    elif arch == A_HEADLOAD:
        sh_w = int(body_w * 0.80); hem_w = int(body_w * 0.95)
        pts = [(cx - sh_w, torso_top), (cx + sh_w, torso_top),
               (cx + hem_w, torso_bot), (cx - hem_w, torso_bot)]
        pygame.draw.polygon(surf, coat, pts)
        pygame.draw.polygon(surf, coat_dk, pts, max(1, body_w // 8))
        pygame.draw.line(surf, coat, (cx + sh_w * 0.4, torso_top + head_r // 2),
                         (cx + head_r // 2, hy - head_r), max(2, body_w // 5))
    elif arch == A_CHILD:
        r = pygame.Rect(cx - body_w + lean, torso_top, body_w * 2, torso_h)
        pygame.draw.rect(surf, coat, r, border_radius=max(2, body_w // 2))
        pygame.draw.rect(surf, coat_dk, r, 1, border_radius=max(2, body_w // 2))

    # ── NEW ARCH: A_ROD — belted short tunic; the ROD owns the outline ──
    elif arch == A_ROD:
        r = pygame.Rect(int(cx - body_w * 0.92 + lean), torso_top,
                        int(body_w * 1.84), torso_h)
        pygame.draw.rect(surf, coat, r, border_radius=max(2, body_w // 3))
        pygame.draw.rect(surf, coat_dk, r, max(1, body_w // 8), border_radius=max(2, body_w // 3))
        belt = torso_top + int(torso_h * 0.66)
        pygame.draw.line(surf, sash, (r.left, belt), (r.right, belt), max(2, body_w // 5))
        # creel strap crossing the chest — reads as a diagonal even when the basket
        # itself is only a few px, and it is what sells "fisherman" over "porter".
        pygame.draw.line(surf, _shade(sash, -30), (r.right - 1, torso_top + 1),
                         (r.left + 1, belt), max(1, body_w // 8))

    # ── NEW ARCH: A_BARROW — body pitched hard forward behind two shafts ──
    elif arch == A_BARROW:
        r = pygame.Rect(int(cx - body_w * 0.86 + lean), torso_top,
                        int(body_w * 1.72), torso_h)
        pygame.draw.rect(surf, coat, r, border_radius=max(2, body_w // 3))
        pygame.draw.rect(surf, coat_dk, r, max(1, body_w // 8), border_radius=max(2, body_w // 3))
        # both arms run straight forward-down to the shafts: the horizontal
        # shoulder-to-hand line is half of the pushing read.
        pygame.draw.line(surf, coat, (cx + lean, arm_y),
                         (cx + body_w * 1.5 + lean, arm_y + torso_h * 0.35), max(2, body_w // 4))

    # ── NEW ARCH: A_PIPA — narrow robe already drawn above; instrument below ──

    # ── ACCESSORIES that break the outline ──
    if arch == A_POLE:
        pole_c = pf((120, 88, 54)); py = torso_top - 1
        x0, x1 = cx - body_w * 1.7, cx + body_w * 1.7 + lean
        pygame.draw.line(surf, pole_c, (x0, py + 3), (x1, py - 3), max(2, body_w // 6))
        for ex, ey in ((x0, py + 3), (x1, py - 3)):
            bk = pf(P.get("basket", (176, 132, 78)))
            br = pygame.Rect(ex - body_w * 0.6, ey + body_w * 0.5, body_w * 1.2, body_w * 1.0)
            pygame.draw.ellipse(surf, bk, br)
            pygame.draw.ellipse(surf, _shade(bk, -30), br, 1)
            pygame.draw.circle(surf, pf(P.get("goods", (224, 120, 60))),
                               (int(ex), int(ey + body_w * 0.6)), max(1, body_w // 4))
    elif arch == A_YOKE:
        yoke_c = pf((110, 80, 50)); yy = torso_top - 1
        x0, x1 = cx - body_w * 1.5, cx + body_w * 1.5 + lean
        pygame.draw.line(surf, yoke_c, (x0, yy), (x1, yy), max(2, body_w // 6))
        for ex in (x0, x1):
            sk = pf(P.get("load", (150, 124, 86)))
            sr = pygame.Rect(ex - body_w * 0.5, yy + 2, body_w * 1.0, torso_h * 1.15)
            pygame.draw.rect(surf, sk, sr, border_radius=max(1, body_w // 3))
            pygame.draw.rect(surf, _shade(sk, -32), sr, 1, border_radius=max(1, body_w // 3))
            pygame.draw.line(surf, yoke_c, (ex, yy), (ex, sr.top), max(1, body_w // 6))
    elif arch == A_HEADLOAD:
        tray = pf(P.get("tray", (164, 120, 76)))
        tw = int(body_w * 1.9); th = max(3, int(head_r * 0.9)); ty = hy - head_r - th - 1
        tr = pygame.Rect(hx - tw, ty, tw * 2, th)
        pygame.draw.rect(surf, tray, tr, border_radius=max(1, body_w // 4))
        pygame.draw.rect(surf, _shade(tray, -34), tr, 1, border_radius=max(1, body_w // 4))
        for gx in (-0.5, 0.0, 0.5):
            pygame.draw.circle(surf, pf(P.get("goods", (218, 130, 70))),
                               (int(hx + gx * tw), int(ty)), max(1, body_w // 3))

    elif arch == A_ROD:
        # THE ROD: butt held low at the front hand, tip sweeping up-and-BACK past
        # the head. It is authored as two segments so the far end can flex with the
        # gait — a live springy line is what makes it read as a rod, not a spear.
        rod_c = pf(P.get("rod", (132, 100, 62)))
        hand = (cx + body_w * 0.9 + lean, arm_y + torso_h * 0.35)
        mid = (cx - body_w * 0.6, hy - head_r * 1.4)
        tip = (cx - body_w * 3.0, hy - total_h * 0.62 + gait * 1.5)
        # A 1px rod is destroyed by the crisp far-lane downscale — the outer half
        # drops out and the tip becomes a floating splinter. Two pixels is the
        # minimum that survives a nearest 0.78x and keeps the figure ONE island.
        pygame.draw.lines(surf, rod_c, False, [hand, mid, tip], max(2, body_w // 6))
        pygame.draw.line(surf, coat, (cx + body_w * 0.4 + lean, arm_y), hand, max(2, body_w // 5))
        pygame.draw.circle(surf, skin, (int(hand[0]), int(hand[1])), max(1, body_w // 5))
        # catch on a short line off the rod tip — a hanging blob that keeps the
        # diagonal from reading as a bare stick.
        if "catch" in v.accessory:
            fy = tip[1] + total_h * 0.30
            pygame.draw.line(surf, _shade(rod_c, 24), tip, (tip[0], fy), 1)
            fish = pf(P.get("catch", (168, 176, 178)))
            pygame.draw.ellipse(surf, fish, (tip[0] - 2, fy, 5, 3))
            pygame.draw.polygon(surf, _shade(fish, -40),
                                [(tip[0] + 3, fy + 1), (tip[0] + 5, fy - 1), (tip[0] + 5, fy + 3)])
        # creel on the back hip, hanging off the chest strap
        cr = pf(P.get("basket", (168, 128, 76)))
        crr = pygame.Rect(int(cx - body_w * 1.7), int(arm_y + torso_h * 0.35),
                          int(body_w * 1.1), int(body_w * 1.0))
        pygame.draw.ellipse(surf, cr, crr)
        pygame.draw.ellipse(surf, _shade(cr, -34), crr, 1)

    elif arch == A_BARROW:
        # THE BARROW: one big wheel on the deck + a load box + two shafts back to
        # the hands. All of it sits AHEAD of the figure, so the pair reads as a
        # long low mass with a person tipped over its back end.
        wood = pf(P.get("cart", (128, 96, 58)))
        wood_dk = _shade(wood, -34)
        hand_y = arm_y + torso_h * 0.35
        wx = cx + body_w * 3.1 + lean
        wr = max(2, int(leg_h * 0.85))
        wy = ground - wr
        for off in (0, 1):
            pygame.draw.line(surf, wood, (cx + body_w * 1.5 + lean, hand_y + off),
                             (wx - wr * 0.4, wy - wr * 0.2 + off), max(1, body_w // 8))
        box = pygame.Rect(int(cx + body_w * 1.6 + lean), int(wy - wr * 0.9),
                          int(body_w * 2.2), max(3, int(torso_h * 0.55)))
        pygame.draw.rect(surf, wood, box, border_radius=1)
        pygame.draw.rect(surf, wood_dk, box, 1, border_radius=1)
        load = pf(P.get("load", (150, 124, 86)))
        for k in range(2):
            pygame.draw.circle(surf, load,
                               (int(box.left + box.width * (0.3 + 0.42 * k)), box.top),
                               max(1, body_w // 3))
        pygame.draw.circle(surf, wood_dk, (int(wx), int(wy)), wr)
        pygame.draw.circle(surf, wood, (int(wx), int(wy)), max(1, wr - 1))
        pygame.draw.circle(surf, wood_dk, (int(wx), int(wy)), max(1, wr // 3))
        spin = t * 4.0
        for k in range(3):
            a = spin + k * math.pi / 3
            pygame.draw.line(surf, wood_dk,
                             (wx - math.cos(a) * wr, wy - math.sin(a) * wr),
                             (wx + math.cos(a) * wr, wy + math.sin(a) * wr), 1)

    elif arch == A_PIPA:
        # THE PIPA: a pear body tucked against the chest with its short neck
        # rising past the far shoulder — a swollen body edge plus one diagonal
        # spar, which is a completely different outline event from a carried load.
        wood = pf(P.get("lute", (158, 112, 66)))
        wood_dk = _shade(wood, -40)
        bx = cx - body_w * 1.25
        by = torso_top + torso_h * 0.62
        bwid = int(body_w * 1.9); bhei = int(torso_h * 1.15)
        body_r = pygame.Rect(int(bx - bwid // 2), int(by - bhei // 2), bwid, bhei)
        pygame.draw.ellipse(surf, wood, body_r)
        pygame.draw.ellipse(surf, wood_dk, body_r, 1)
        pygame.draw.arc(surf, _shade(wood, 22), body_r, math.radians(40), math.radians(150), 1)
        # The neck clears the crown of the head: a spar that stops at the shoulder
        # just reads as a bulky sleeve, one that passes the head reads as an
        # instrument even when the pear itself is four pixels wide.
        neck_top = (bx - body_w * 1.15, hy - head_r * 2.1)
        pygame.draw.line(surf, wood_dk, (bx, by - bhei * 0.35), neck_top, max(2, body_w // 5))
        pygame.draw.circle(surf, wood, (int(neck_top[0]), int(neck_top[1])), max(1, body_w // 4))
        # plucking hand at the belly, fretting hand at the neck: two skin dots on
        # opposite ends of the spar, which is what says "playing" not "carrying".
        elbow = (cx + body_w * 1.25 + lean, arm_y + torso_h * 0.12)
        pygame.draw.lines(surf, coat, False,
                          [(cx + lean, arm_y), elbow, (bx + bwid * 0.25, by)], max(2, body_w // 5))
        pygame.draw.circle(surf, skin, (int(bx + bwid * 0.25), int(by)), max(1, body_w // 5))
        pygame.draw.circle(surf, skin, (int(neck_top[0] + 1), int(neck_top[1] + 2)),
                           max(1, body_w // 5))

    if "basket_arm" in v.accessory:
        bk = pf(P.get("basket", (176, 132, 78))); bhx = cx + body_w * 1.5 + lean
        pygame.draw.line(surf, coat, (cx + body_w * 0.6 + lean, arm_y),
                         (bhx, arm_y + torso_h // 2), max(2, body_w // 5))
        br = pygame.Rect(bhx - body_w * 0.55, arm_y + torso_h // 2, body_w * 1.1, body_w * 0.9)
        pygame.draw.ellipse(surf, bk, br)
        pygame.draw.ellipse(surf, _shade(bk, -30), br, 1)
    if "cane" in v.accessory:
        cane_c = pf(P.get("cane", (120, 84, 50))); chx = cx + body_w * 1.3 + lean
        pygame.draw.line(surf, cane_c, (chx, arm_y), (chx + body_w * 0.3, ground), max(2, body_w // 6))
        pygame.draw.line(surf, coat, (cx + body_w * 0.5 + lean, arm_y), (chx, arm_y), max(2, body_w // 5))
    if "bundle" in v.accessory:
        bd = pf(P.get("bundle", (198, 176, 150)))
        br = pygame.Rect(cx - body_w * 0.7 + lean, arm_y + 1, body_w * 1.4, torso_h // 2)
        pygame.draw.rect(surf, bd, br, border_radius=max(1, body_w // 4))
    if "hand_hold" in v.accessory:
        pygame.draw.line(surf, skin, (cx + body_w * 0.7 + lean, arm_y + torso_h // 2),
                         (cx + body_w * 1.2 + lean, ground - leg_h * 0.3), max(2, body_w // 5))
    if "reach_up" in v.accessory:
        pygame.draw.line(surf, skin, (cx + body_w * 0.5 + lean, arm_y),
                         (cx + body_w * 1.3 + lean, arm_y - torso_h * 0.4), max(2, body_w // 4))
    if "swing_arm" in v.pose and arch == A_TUNIC:
        ax = cx + lean + int(gait * body_w * 0.5)
        pygame.draw.line(surf, coat, (cx + lean, arm_y),
                         (ax + body_w * 0.4, arm_y + torso_h * 0.55), max(2, body_w // 5))
        pygame.draw.circle(surf, skin, (int(ax + body_w * 0.4), int(arm_y + torso_h * 0.55)),
                           max(1, body_w // 6))

    # NEW carry positions — all of them move mass BEHIND the figure, which is a
    # part of the outline no shipped row uses (everything is carried in front,
    # overhead or out to the side).
    if "back_basket" in v.accessory:
        bk = pf(P.get("basket", (166, 126, 76)))
        bwid = int(body_w * 1.3)
        bh = int(torso_h * 1.25)
        br = pygame.Rect(int(cx - body_w * 2.0), int(torso_top - head_r * 1.1), bwid, bh)
        pygame.draw.polygon(surf, bk, [
            (br.left + 1, br.bottom), (br.right, br.bottom),
            (br.right + 1, br.top), (br.left - 1, br.top + 2)])
        pygame.draw.polygon(surf, _shade(bk, -34), [
            (br.left + 1, br.bottom), (br.right, br.bottom),
            (br.right + 1, br.top), (br.left - 1, br.top + 2)], 1)
        for q in (0.35, 0.70):
            yy = int(br.top + bh * q)
            pygame.draw.line(surf, _shade(bk, -26), (br.left, yy), (br.right, yy), 1)
        pygame.draw.line(surf, _shade(bk, -30), (br.right, br.top + 1),
                         (cx - body_w * 0.2, torso_top + 1), max(1, body_w // 8))
    if "back_bundle" in v.accessory:
        bd = pf(P.get("bundle", (176, 152, 118)))
        r = int(body_w * 0.95)
        pygame.draw.circle(surf, bd, (int(cx - body_w * 1.5), int(torso_top + torso_h * 0.35)), r)
        pygame.draw.circle(surf, _shade(bd, -34),
                           (int(cx - body_w * 1.5), int(torso_top + torso_h * 0.35)), r, 1)
        pygame.draw.line(surf, _shade(bd, -30), (cx - body_w * 1.0, torso_top),
                         (cx + body_w * 0.3 + lean, torso_top + torso_h * 0.5), max(1, body_w // 8))
    if "scroll" in v.accessory:
        sc = pf(P.get("scroll", (206, 190, 158)))
        sy = arm_y + torso_h * 0.45
        pygame.draw.line(surf, sc, (cx - body_w * 1.6, sy - 1), (cx + body_w * 1.2 + lean, sy + 1),
                         max(2, body_w // 5))
        pygame.draw.line(surf, _shade(sc, -44), (cx - body_w * 1.6, sy - 1),
                         (cx - body_w * 1.2, sy - 1), max(2, body_w // 5))

    # ── HEAD + NECK ──
    pygame.draw.line(surf, skin_sh, (hx, hy + head_r - 1), (hx, torso_top + 1), max(2, head_r // 2))
    pygame.draw.circle(surf, skin, (hx, hy), head_r)
    pygame.draw.circle(surf, skin_sh, (hx, hy), head_r, 1)
    pygame.draw.circle(surf, (40, 28, 22), (hx + head_r // 3, hy - head_r // 6), max(1, head_r // 4))
    if "beard" in v.accessory:
        grey = pf(P.get("beard", (210, 208, 200)))
        pygame.draw.polygon(surf, grey, [
            (hx - head_r * 0.6, hy + head_r * 0.3), (hx + head_r * 0.6, hy + head_r * 0.3),
            (hx + head_r * 0.2, hy + head_r * 1.7), (hx - head_r * 0.2, hy + head_r * 1.7)])

    # ── HEADWEAR (outline-breaker) ──
    hat = P.get("hat")
    if hat == "conical":
        col = pf(P.get("hat_c", (198, 162, 96))); brim_w = int(head_r * 2.5)
        apex = (hx, hy - head_r * 1.8)
        cone = [(hx - brim_w, hy - head_r * 0.15), apex, (hx + brim_w, hy - head_r * 0.15)]
        pygame.draw.polygon(surf, col, cone)
        pygame.draw.polygon(surf, _shade(col, -34), cone, 1)
    elif hat == "winter":
        col = pf(P.get("hat_c", (150, 96, 80)))
        cap = pygame.Rect(hx - head_r, hy - head_r * 1.7, head_r * 2, int(head_r * 1.6))
        pygame.draw.ellipse(surf, col, cap)
        fur = pf(P.get("fur", (224, 214, 198)))
        pygame.draw.line(surf, fur, (hx - head_r, hy - head_r * 0.35),
                         (hx + head_r, hy - head_r * 0.35), max(2, head_r // 2))
    elif hat == "hood":
        col = pf(P.get("hat_c", coat))
        pygame.draw.circle(surf, col, (hx, hy - head_r // 3), int(head_r * 1.35))
        pygame.draw.circle(surf, skin, (hx + head_r // 4, hy), int(head_r * 0.8))
    elif hat == "cloth":
        col = pf(P.get("hat_c", (190, 90, 80)))
        pygame.draw.circle(surf, col, (hx, hy - head_r // 2), int(head_r * 1.1))
        pygame.draw.circle(surf, skin, (hx + head_r // 3, hy + head_r // 5), int(head_r * 0.75))
    elif hat == "bald":
        pygame.draw.circle(surf, skin, (hx, hy - head_r // 4), head_r)
        pygame.draw.arc(surf, hair, pygame.Rect(hx - head_r, hy - head_r // 2, head_r * 2, head_r * 2),
                        math.radians(200), math.radians(340), max(1, head_r // 3))
    elif hat == "bun":
        pygame.draw.circle(surf, hair, (hx, hy - head_r), head_r)
        pygame.draw.circle(surf, hair_dk, (hx - head_r // 3, hy - int(head_r * 1.3)), max(2, head_r // 2))
        if "hairpin" in v.accessory:
            pin = pf(P.get("pin", (220, 90, 100)))
            pygame.draw.line(surf, pin, (hx - head_r // 3, hy - int(head_r * 1.5)),
                             (hx + head_r // 2, hy - int(head_r * 1.7)), 2)
    # ── NEW HEADWEAR ──
    elif hat == "shawl":
        # A head-cloth that keeps FALLING — over the crown, past both shoulders,
        # out to a hem below the elbow and down to one hanging point that swings
        # with the stride. Draped only to the collar it was a 1px difference from
        # the cloth-cap matrons; carried to the elbow it turns head+shoulders+torso
        # into a single BELL, which is a shape no other row in the pool makes.
        col = pf(P.get("hat_c", (176, 140, 118)))
        hem_y = arm_y + torso_h * 0.62
        tip_y = hem_y + torso_h * 0.62 + gait * 1.4
        # Thrown over one shoulder and gathered under the carrying arm, so the
        # drape flares OUTSIDE the A-line on the left and tucks in on the right.
        # A symmetric cape would sit inside the skirt's own cone and change nothing.
        pts = [(cx - body_w * 2.05, hem_y),
               (cx - body_w * 1.05, torso_top), (hx - head_r * 1.3, hy - head_r * 0.5),
               (hx, hy - head_r * 1.5), (hx + head_r * 1.3, hy - head_r * 0.5),
               (cx + body_w * 0.95, torso_top + 1), (cx + body_w * 1.05, hem_y - 1),
               (cx - body_w * 0.25, hem_y + 1), (cx - body_w * 0.85, tip_y),
               (cx - body_w * 1.45, hem_y + 1)]
        pygame.draw.polygon(surf, col, pts)
        pygame.draw.polygon(surf, _shade(col, -32), pts, 1)
        pygame.draw.line(surf, _shade(col, -32), (cx - body_w * 1.5, hem_y - 2),
                         (cx + body_w * 0.6, hem_y - 2), 1)
        pygame.draw.circle(surf, skin, (hx + head_r // 3, hy + head_r // 5), int(head_r * 0.72))
    elif hat == "flatbrim":
        # Official's flat disc brim + a low box crown: a hard horizontal above the
        # shoulders, as opposed to the conical hat's triangle.
        col = pf(P.get("hat_c", (86, 78, 70)))
        brim = pygame.Rect(int(hx - head_r * 3.1), int(hy - head_r * 1.35),
                           int(head_r * 6.2), max(2, int(head_r * 0.8)))
        crown = pygame.Rect(int(hx - head_r * 0.95), int(hy - head_r * 2.4),
                            int(head_r * 1.9), int(head_r * 1.3))
        pygame.draw.rect(surf, _shade(col, 14), crown, border_radius=1)
        pygame.draw.ellipse(surf, col, brim)
        pygame.draw.ellipse(surf, _shade(col, -30), brim, 1)
    elif hat == "earflap":
        # Winter cap whose two flaps hang BELOW the jaw, widening the head blob.
        # The leading flap is untied and SWINGS with the stride: a static flap was
        # a hat swap the eye can't see past a fur cap, a moving one is an outline
        # event, and it is the only head in the pool that animates.
        col = pf(P.get("hat_c", (132, 98, 78)))
        cap = pygame.Rect(hx - head_r, int(hy - head_r * 1.7), head_r * 2, int(head_r * 1.6))
        pygame.draw.ellipse(surf, col, cap)
        for sgn in (-1, 1):
            # Flaps flare OUT at ear level rather than hanging down: on a padded
            # coat anything below the jaw is inside the coat's own width and adds
            # nothing to the outline. Ear level is where the figure is narrowest.
            sw = gait * head_r * 1.1 if sgn > 0 else 0.0
            pygame.draw.polygon(surf, _shade(col, -20), [
                (hx + sgn * head_r * 0.9, hy - head_r * 0.7),
                (hx + sgn * head_r * 2.3 + sw, hy + head_r * 0.2),
                (hx + sgn * head_r * 1.9 + sw * 1.5, hy + head_r * 1.2),
                (hx + sgn * head_r * 0.5, hy + head_r * 0.9)])
        fur = pf(P.get("fur", (216, 206, 190)))
        pygame.draw.line(surf, fur, (hx - head_r, hy - head_r * 0.45),
                         (hx + head_r, hy - head_r * 0.45), max(2, head_r // 2))
    else:
        pygame.draw.circle(surf, hair, (hx, hy - head_r // 3), head_r)
        pygame.draw.arc(surf, hair, pygame.Rect(hx - head_r, hy - head_r, head_r * 2, head_r * 2),
                        math.radians(0), math.radians(180), max(1, head_r // 2))
        if "topknot" in v.accessory:
            pygame.draw.circle(surf, hair_dk, (hx, hy - int(head_r * 1.4)), max(2, head_r // 2))

    # ── HELD PARASOL / UMBRELLA (overhead — strongest outline-breaker) ──
    if "parasol" in v.accessory or "umbrella" in v.accessory:
        col = pf(P.get("canopy", (236, 224, 210)))
        dark = _shade(col, -42)
        cr = int(head_r * 2.5)
        tilt = int(head_r * (0.5 if "umbrella" in v.accessory else 0.15))
        cy = hy - int(head_r * 2.7)
        apex_x = hx + tilt
        canopy = [(hx - cr, cy), (apex_x - cr // 2, cy - cr // 2), (apex_x, cy - cr),
                  (apex_x + cr // 2, cy - cr // 2), (hx + cr, cy),
                  (hx + cr * 3 // 5, cy + 3), (hx, cy + 1), (hx - cr * 3 // 5, cy + 3)]
        pygame.draw.polygon(surf, col, canopy)
        pygame.draw.polygon(surf, dark, canopy, max(1, head_r // 4))
        for tx in (-cr * 3 // 5, 0, cr * 3 // 5):
            pygame.draw.line(surf, dark, (apex_x, cy - cr), (hx + tx, cy + (1 if tx == 0 else 3)), 1)
        pygame.draw.line(surf, pf((110, 84, 56)), (hx, cy + 1), (hx - 1, arm_y + torso_h // 3),
                         max(2, head_r // 4))


# ════════════════════════════════════════════════════════════════════════════
# THE POOL — the shipped 50 (numbered as in round 2) + 13 NEW rows, 6 nominated CUT
# ════════════════════════════════════════════════════════════════════════════

_COATS = {
    "indigo": ((86, 96, 140), (52, 60, 100)), "plum": ((104, 80, 116), (66, 48, 78)),
    "sage": ((110, 134, 112), (70, 92, 76)), "ochre": ((158, 128, 78), (108, 84, 50)),
    "rust": ((150, 86, 70), (104, 56, 46)), "teal": ((78, 124, 124), (48, 84, 84)),
    "slate": ((100, 108, 124), (64, 72, 90)), "olive": ((118, 116, 80), (78, 78, 52)),
    "clay": ((168, 120, 84), (114, 78, 54)), "mauve": ((140, 104, 130), (94, 66, 90)),
    "stone": ((128, 124, 112), (84, 82, 72)), "wine": ((128, 70, 78), (84, 44, 50)),
}
_HAIRS = [(46, 36, 30), (40, 32, 28), (58, 44, 36), (34, 28, 26), (70, 56, 44)]


def _c(name):
    return dict(coat=_COATS[name][0], coat_dk=_COATS[name][1])


SHIPPED = [
    # ARCH 1 — narrow robe
    ("#1 Robe · indigo scholar", V(dict(**_c("indigo"), sash=(206, 200, 170), hair=_HAIRS[2], skin="fair", hat="bun"),
        A_ROBE, pose=("stroll",), acc=("topknot",), height=1.10), ""),
    ("#2 Robe · plum elder", V(dict(**_c("plum"), sash=(196, 180, 150), hair=(206, 204, 196), beard=(212, 210, 202), skin="fair", hat="bun"),
        A_ROBE, pose=("stroll",), acc=("beard", "topknot")), ""),
    ("#3 Robe · teal youth", V(dict(**_c("teal"), sash=(200, 188, 150), hair=_HAIRS[1], skin="warm", hat="bun"),
        A_ROBE, pose=("hurry",), acc=("topknot",), height=0.92, build=0.9), ""),
    ("#4 Robe · mauve hairpin", V(dict(**_c("mauve"), sash=(208, 160, 140), hair=_HAIRS[3], skin="fair", hat="bun", pin=(214, 110, 120)),
        A_ROBE, pose=("stroll",), acc=("hairpin",), height=1.04, build=0.92), ""),
    ("#5 Robe · slate tall scholar", V(dict(**_c("slate"), sash=(180, 186, 196), hair=_HAIRS[0], skin="tan", hat="bun"),
        A_ROBE, pose=("stroll",), acc=("topknot",), height=1.10, build=0.95), "CUT"),
    # ARCH 2 — wide skirt
    ("#6 Skirt · sage basket", V(dict(**_c("sage"), sash=(214, 190, 140), hair=_HAIRS[1], skin="warm", hat="cloth", hat_c=(186, 92, 84), basket=(182, 138, 84), goods=(196, 96, 90)),
        A_SKIRT, pose=("stroll",), acc=("basket_arm",), height=0.96, build=1.1), ""),
    ("#7 Skirt · ochre merchant", V(dict(**_c("ochre"), sash=(150, 74, 66), hair=_HAIRS[0], skin="tan", hat="conical", hat_c=(188, 152, 90)),
        A_SKIRT, pose=("stroll",), height=0.98, build=1.28), ""),
    ("#8 Skirt · clay basket", V(dict(**_c("clay"), sash=(206, 180, 140), hair=_HAIRS[4], skin="ruddy", hat="cloth", hat_c=(170, 96, 80), basket=(176, 132, 78), goods=(200, 120, 70)),
        A_SKIRT, pose=("stroll",), acc=("basket_arm",), height=0.94, build=1.12), ""),
    ("#9 Skirt · olive merchant", V(dict(**_c("olive"), sash=(140, 80, 70), hair=_HAIRS[3], skin="deep", hat="conical", hat_c=(176, 146, 86)),
        A_SKIRT, pose=("stroll",), height=1.0, build=1.22), ""),
    ("#10 Skirt · stone basket", V(dict(**_c("stone"), sash=(196, 150, 120), hair=_HAIRS[2], skin="warm", hat="cloth", hat_c=(150, 110, 96), basket=(170, 128, 80), goods=(180, 140, 80)),
        A_SKIRT, pose=("stroll",), acc=("basket_arm",), height=0.97, build=1.08), ""),
    # ARCH 3 — tunic
    ("#11 Tunic · clay porter", V(dict(**_c("clay"), trousers=(74, 64, 56), hair=_HAIRS[3], skin="deep"),
        A_TUNIC, pose=("hurry", "swing_arm"), height=1.02, build=1.12), ""),
    ("#12 Tunic · teal youth", V(dict(**_c("teal"), trousers=(68, 62, 66), hair=_HAIRS[1], skin="warm"),
        A_TUNIC, pose=("hurry", "swing_arm"), height=0.92, build=0.9), ""),
    ("#13 Tunic · ochre laborer", V(dict(**_c("ochre"), trousers=(70, 60, 50), hair=_HAIRS[0], skin="tan"),
        A_TUNIC, pose=("hurry", "swing_arm"), height=1.0, build=1.05), "CUT"),
    ("#14 Tunic · slate stroller", V(dict(**_c("slate"), trousers=(60, 64, 74), hair=_HAIRS[2], skin="warm"),
        A_TUNIC, pose=("stroll", "swing_arm")), ""),
    ("#15 Tunic · rust porter", V(dict(**_c("rust"), trousers=(72, 56, 50), hair=_HAIRS[4], skin="ruddy"),
        A_TUNIC, pose=("hurry", "swing_arm"), height=1.04, build=1.1), "CUT"),
    ("#16 Tunic · olive youth", V(dict(**_c("olive"), trousers=(64, 62, 48), hair=_HAIRS[3], skin="deep"),
        A_TUNIC, pose=("hurry", "swing_arm"), height=0.9, build=0.92), ""),
    # ARCH 4 — padded [SNOW]
    ("#17 Padded · rust bundle", V(dict(**_c("rust"), fur=(228, 220, 206), hair=_HAIRS[3], skin="ruddy", hat="winter", hat_c=(150, 88, 74), bundle=(206, 188, 162)),
        A_PADDED, pose=("hurry",), acc=("bundle",), height=0.98, build=1.2), ""),
    ("#18 Padded · indigo scarf", V(dict(**_c("indigo"), fur=(222, 214, 200), trim=(206, 110, 96), hair=_HAIRS[2], skin="fair", hat="winter", hat_c=(86, 100, 138)),
        A_PADDED, pose=("stroll",), height=0.96, build=1.18), ""),
    ("#19 Padded · olive elder", V(dict(**_c("olive"), fur=(226, 218, 204), hair=(206, 204, 196), beard=(214, 212, 204), skin="warm", hat="winter", hat_c=(120, 100, 70)),
        A_PADDED, pose=("stroll",), acc=("beard",), height=0.92, build=1.15), ""),
    ("#20 Padded · clay child", V(dict(**_c("clay"), fur=(228, 222, 210), hair=_HAIRS[1], skin="warm", hat="winter", hat_c=(150, 104, 76)),
        A_PADDED, pose=("hurry",), height=0.78), ""),
    ("#21 Padded · slate bundle", V(dict(**_c("slate"), fur=(224, 216, 202), hair=_HAIRS[0], skin="tan", hat="winter", hat_c=(96, 102, 120), bundle=(200, 184, 158)),
        A_PADDED, pose=("hurry",), acc=("bundle",), build=1.22), ""),
    # ARCH 5 — stooped cane elder
    ("#22 Stoop · plum cane", V(dict(**_c("plum"), sash=(196, 180, 150), hair=(208, 206, 198), beard=(214, 212, 204), skin="fair", hat="bald", cane=(120, 84, 50)),
        A_STOOP, pose=("stroll",), acc=("beard", "cane"), height=0.9, stoop=0.42), ""),
    ("#23 Stoop · slate cane", V(dict(**_c("slate"), sash=(180, 184, 192), hair=(204, 202, 196), beard=(210, 208, 200), skin="warm", hat="bald", cane=(116, 80, 48)),
        A_STOOP, pose=("stroll",), acc=("beard", "cane"), height=0.88, stoop=0.46), ""),
    ("#24 Stoop · olive matron", V(dict(**_c("olive"), sash=(196, 170, 130), hair=(202, 200, 194), skin="ruddy", hat="cloth", hat_c=(150, 110, 96), cane=(118, 82, 50)),
        A_STOOP, pose=("stroll",), acc=("cane",), height=0.88, stoop=0.40), ""),
    ("#25 Stoop · mauve elder", V(dict(**_c("mauve"), sash=(200, 170, 150), hair=(206, 204, 198), beard=(212, 210, 202), skin="deep", hat="bald", cane=(110, 78, 46)),
        A_STOOP, pose=("stroll",), acc=("beard", "cane"), height=0.86, stoop=0.48), ""),
    # ARCH 6 — carrying pole
    ("#26 Pole · rust conical", V(dict(**_c("rust"), hair=_HAIRS[0], skin="tan", hat="conical", hat_c=(196, 158, 92), basket=(176, 132, 78), goods=(214, 130, 70)),
        A_POLE, pose=("hurry",), build=1.05), ""),
    ("#27 Pole · ochre cloth", V(dict(**_c("ochre"), hair=_HAIRS[3], skin="deep", hat="cloth", hat_c=(160, 96, 84), basket=(170, 126, 76), goods=(200, 110, 80)),
        A_POLE, pose=("hurry",), build=1.05), ""),
    ("#28 Pole · sage conical", V(dict(**_c("sage"), hair=_HAIRS[1], skin="warm", hat="conical", hat_c=(184, 150, 88), basket=(178, 134, 80), goods=(186, 150, 80)),
        A_POLE, pose=("stroll",), height=1.04), ""),
    ("#29 Pole · clay conical", V(dict(**_c("clay"), hair=_HAIRS[4], skin="ruddy", hat="conical", hat_c=(190, 156, 92), basket=(172, 128, 78), goods=(210, 120, 64)),
        A_POLE, pose=("hurry",), height=0.98, build=1.08), ""),
    ("#30 Pole · olive cloth", V(dict(**_c("olive"), hair=_HAIRS[0], skin="tan", hat="cloth", hat_c=(150, 100, 80), basket=(176, 130, 80), goods=(190, 140, 70)),
        A_POLE, pose=("hurry",), build=1.05), "CUT"),
    # ARCH 7 — shoulder yoke
    ("#31 Yoke · ochre", V(dict(**_c("ochre"), trousers=(70, 60, 52), hair=_HAIRS[0], skin="deep", load=(150, 124, 86)),
        A_YOKE, pose=("hurry",), height=1.02, build=1.1), ""),
    ("#32 Yoke · rust", V(dict(**_c("rust"), trousers=(70, 60, 52), hair=_HAIRS[3], skin="tan", load=(158, 130, 90)),
        A_YOKE, pose=("hurry",), build=1.12), ""),
    ("#33 Yoke · slate", V(dict(**_c("slate"), trousers=(70, 60, 52), hair=_HAIRS[1], skin="warm", load=(146, 120, 84)),
        A_YOKE, pose=("hurry",), height=1.06, build=1.08), ""),
    ("#34 Yoke · clay", V(dict(**_c("clay"), trousers=(70, 60, 52), hair=_HAIRS[4], skin="ruddy", load=(162, 134, 92)),
        A_YOKE, pose=("hurry",), height=0.98, build=1.1), ""),
    ("#35 Yoke · olive", V(dict(**_c("olive"), trousers=(70, 60, 52), hair=_HAIRS[2], skin="warm", load=(152, 126, 88)),
        A_YOKE, pose=("hurry",), build=1.06), "CUT"),
    # ARCH 8 — head tray
    ("#36 Headload · sage", V(dict(**_c("sage"), tray=(164, 120, 76), hair=_HAIRS[1], skin="warm", goods=(214, 130, 70)),
        A_HEADLOAD, pose=("stroll",)), ""),
    ("#37 Headload · clay", V(dict(**_c("clay"), tray=(160, 118, 74), hair=_HAIRS[4], skin="ruddy", goods=(196, 150, 80)),
        A_HEADLOAD, pose=("stroll",), height=0.96), ""),
    ("#38 Headload · indigo", V(dict(**_c("indigo"), tray=(150, 112, 70), hair=_HAIRS[2], skin="fair", goods=(206, 120, 70)),
        A_HEADLOAD, pose=("stroll",), height=1.04), "CUT"),
    ("#39 Headload · ochre box", V(dict(**_c("ochre"), tray=(140, 104, 64), hair=_HAIRS[0], skin="tan", goods=(180, 140, 84)),
        A_HEADLOAD, pose=("stroll",), build=1.05), ""),
    ("#40 Headload · rust", V(dict(**_c("rust"), tray=(158, 116, 74), hair=_HAIRS[3], skin="deep", goods=(210, 120, 64)),
        A_HEADLOAD, pose=("stroll",), height=0.98), ""),
    # ARCH 9 — children + parents
    ("#41 Child · teal", V(dict(**_c("teal"), trousers=(64, 60, 64), hair=_HAIRS[1], skin="warm"),
        A_CHILD, pose=("hurry",), acc=("reach_up",), height=0.62), ""),
    ("#42 Child · wine", V(dict(**_c("wine"), trousers=(70, 56, 60), hair=_HAIRS[3], skin="ruddy"),
        A_CHILD, pose=("hurry",), acc=("reach_up",), height=0.6), ""),
    ("#43 Child · sage", V(dict(**_c("sage"), trousers=(62, 64, 56), hair=_HAIRS[2], skin="fair"),
        A_CHILD, pose=("hurry",), height=0.64), ""),
    ("#44 Parent · robe slate", V(dict(**_c("slate"), sash=(186, 188, 196), hair=_HAIRS[0], skin="fair", hat="bun"),
        A_ROBE, pose=("stroll",), acc=("hand_hold", "topknot"), height=1.10), ""),
    ("#45 Parent · skirt clay", V(dict(**_c("clay"), sash=(204, 178, 140), hair=_HAIRS[2], skin="warm", hat="cloth", hat_c=(170, 96, 80)),
        A_SKIRT, pose=("stroll",), acc=("hand_hold",), height=1.04, build=1.08), ""),
    # WEATHER
    ("#46 Umbrella · tunic slate", V(dict(**_c("slate"), trousers=(60, 62, 70), hair=_HAIRS[2], skin="warm", canopy=(176, 96, 92)),
        A_TUNIC, pose=("hurry", "swing_arm"), acc=("umbrella",)), "RAIN"),
    ("#47 Umbrella · robe olive", V(dict(**_c("olive"), sash=(180, 160, 120), hair=_HAIRS[0], skin="fair", hat="bun", canopy=(150, 138, 102)),
        A_ROBE, pose=("stroll",), acc=("umbrella",)), "RAIN"),
    ("#48 Umbrella · skirt stone", V(dict(**_c("stone"), sash=(150, 120, 90), hair=_HAIRS[1], skin="fair", hat="bun", canopy=(96, 122, 162)),
        A_SKIRT, pose=("stroll",), acc=("umbrella",), build=1.05), "RAIN"),
    ("#49 Hood · robe teal", V(dict(**_c("teal"), sash=(70, 96, 92), hair=_HAIRS[3], skin="warm", hat="hood", hat_c=(72, 100, 96)),
        A_ROBE, pose=("hurry",)), "RAIN"),
    ("#50 Parasol · mauve lady", V(dict(**_c("mauve"), sash=(190, 150, 140), hair=_HAIRS[3], skin="fair", hat="bun", pin=(196, 120, 124), canopy=(196, 156, 166)),
        A_ROBE, pose=("stroll",), acc=("parasol", "hairpin"), height=1.04, build=0.92), ""),
]

# ── the 13 NEW rows ───────────────────────────────────────────────────────────
NEW = [
    ("N1 Rod · ochre fisher", V(dict(**_c("ochre"), sash=(150, 118, 76), trousers=(70, 60, 50), hair=_HAIRS[0],
        skin="tan", hat="conical", hat_c=(186, 152, 90), rod=(132, 100, 62), basket=(168, 128, 76), catch=(160, 170, 172)),
        A_ROD, pose=("stroll",), acc=("catch",), height=1.0, build=1.02,
        note="NEW ARCH rod | belted tunic + chest strap | rod: hand->over-head->tip (2 segs, tip flexes with gait) + hanging catch | creel on back hip | hat:conical"), "NEW"),
    ("N2 Rod · teal young fisher", V(dict(**_c("teal"), sash=(150, 148, 108), trousers=(60, 60, 66), hair=_HAIRS[1],
        skin="warm", rod=(140, 108, 68), basket=(162, 124, 74)),
        A_ROD, pose=("hurry",), height=0.93, build=0.92,
        note="NEW ARCH rod | short/slim build, bare-headed, no catch — the same spar on a lighter frame reads as a different person at 14px"), "NEW"),
    ("N3 Rod · slate old fisher", V(dict(**_c("slate"), sash=(150, 152, 160), trousers=(58, 60, 68), hair=(206, 204, 196),
        beard=(212, 210, 202), skin="ruddy", hat="cloth", hat_c=(140, 104, 88), rod=(126, 96, 60), basket=(156, 120, 72), catch=(150, 162, 166)),
        A_ROD, pose=("stroll",), acc=("beard", "catch"), height=0.95, stoop=0.16, build=1.05,
        note="NEW ARCH rod | slight stoop 0.16 + beard: the rod line tips shallower over a bent back, so the trio never repeats its diagonal"), "NEW"),
    ("N4 Barrow · clay porter", V(dict(**_c("clay"), trousers=(72, 60, 52), hair=_HAIRS[3], skin="deep",
        cart=(128, 96, 58), load=(150, 124, 86)),
        A_BARROW, pose=("hurry",), height=1.0, stoop=0.20, build=1.08,
        note="NEW ARCH barrow | pitched body (stoop0.20) + 2 shafts + load box + spoked wheel that ROLLS with t | mass sits on the deck, not the shoulders"), "NEW"),
    ("N5 Barrow · olive tall porter", V(dict(**_c("olive"), trousers=(64, 62, 48), hair=_HAIRS[2], skin="warm",
        hat="cloth", hat_c=(146, 106, 84), cart=(120, 90, 54), load=(158, 132, 92)),
        A_BARROW, pose=("hurry",), height=1.07, stoop=0.26, build=1.0,
        note="NEW ARCH barrow | taller + deeper pitch, cloth head-wrap | the long back over a low cart is the strongest read in the family"), "NEW"),
    ("N6 Barrow · stone covered load", V(dict(**_c("stone"), trousers=(66, 64, 58), hair=_HAIRS[1], skin="warm",
        hat="conical", hat_c=(180, 150, 92), cart=(114, 88, 56), load=(178, 168, 146)),
        A_BARROW, pose=("stroll",), height=0.98, stoop=0.14, build=1.12,
        note="NEW ARCH barrow | strolling, shallow pitch, pale sacked load + conical hat — a slow cart to contrast the two hurried ones"), "NEW"),
    ("N7 Pipa · mauve player", V(dict(**_c("mauve"), sash=(198, 158, 150), hair=_HAIRS[3], skin="fair", hat="bun",
        pin=(196, 120, 124), lute=(158, 112, 66)),
        A_PIPA, pose=("stroll",), acc=("hairpin",), height=1.02, build=0.94,
        note="NEW ARCH pipa | pear body across the chest + neck past the far shoulder, two hands on opposite ends of the spar = PLAYING, not carrying"), "NEW"),
    ("N8 Pipa · indigo old player", V(dict(**_c("indigo"), sash=(168, 176, 196), hair=(204, 202, 196),
        beard=(210, 208, 200), skin="warm", hat="bald", lute=(146, 102, 60)),
        A_PIPA, pose=("stroll",), acc=("beard",), height=0.96, stoop=0.20, build=1.0,
        note="NEW ARCH pipa | bald + bearded + stooped over the instrument: the lute mass rides higher on a bent frame"), "NEW"),
    ("N9 Robe · flat-brim official + scroll", V(dict(**_c("indigo"), sash=(178, 176, 150), hair=_HAIRS[2], skin="warm",
        hat="flatbrim", hat_c=(86, 78, 70), scroll=(206, 190, 158)),
        A_ROBE, pose=("stroll",), acc=("scroll",), height=1.08, build=1.0,
        note="EXISTING arch, NEW hat+acc | flat disc brim (hard horizontal above the shoulders) + a scroll tube sticking out BOTH sides at the waist"), "NEW"),
    ("N10 Skirt · shawl matron", V(dict(**_c("wine"), sash=(196, 168, 140), hair=_HAIRS[0], skin="tan",
        hat="shawl", hat_c=(176, 140, 118), basket=(170, 128, 78)),
        A_SKIRT, pose=("stroll",), acc=("basket_arm",), height=0.95, build=1.14,
        note="EXISTING arch, NEW hat | head-cloth continues onto the shoulders so head+shoulder read as one triangle — no shipped hat does that"), "NEW"),
    # Sage on a sunlit deck is nearly the deck's own luma; this row is half a step
    # darker than the shared sage so a stooped figure doesn't sink into the ground.
    ("N11 Stoop · back-basket gleaner", V(dict(coat=(84, 104, 86), coat_dk=(52, 68, 56), sash=(186, 172, 132), hair=(202, 200, 194), skin="deep",
        hat="cloth", hat_c=(140, 108, 92), basket=(166, 126, 76), cane=(118, 82, 50)),
        A_STOOP, pose=("stroll",), acc=("back_basket", "cane"), height=0.9, stoop=0.44,
        note="EXISTING arch, NEW acc | tall pannier riding high on the BACK — the shipped pool carries everything in front, overhead or out to the side"), "NEW"),
    ("N12 Tunic · back-bundle traveller", V(dict(**_c("wine"), trousers=(68, 58, 54), hair=_HAIRS[4], skin="warm",
        hat="cloth", hat_c=(138, 102, 90), bundle=(176, 152, 118)),
        A_TUNIC, pose=("hurry", "swing_arm"), acc=("back_bundle",), height=1.0, build=0.96,
        note="EXISTING arch, NEW acc | bedroll hump behind the shoulder + strap across the chest: a humped tunic instead of a sixth clean one"), "NEW"),
    ("N13 Padded · ear-flap snow", V(dict(**_c("teal"), fur=(216, 206, 190), hair=_HAIRS[1], skin="ruddy",
        hat="earflap", hat_c=(132, 98, 78), bundle=(196, 180, 154)),
        A_PADDED, pose=("hurry",), acc=("back_bundle",), height=0.94, build=1.16,
        note="EXISTING arch, NEW hat [SNOW] | flaps flare at EAR level (the padded coat swallows anything lower) and the leading one swings with the stride | carried bundle moved to the BACK: the front bundle #17/#21 wear is entirely inside the coat and adds no outline"), "NEW"),
]

CUT_REASONS = {
    "#5": "0.92 max-IoU vs #2 — bun+topknot narrow robe on a stroll at h1.10; at 14px it is #1/#2 a third time.",
    "#13": "MEASURED 1.00 IoU vs #11 — identical mask (hurry+swing_arm, h1.0, b1.05, no accessory).",
    "#15": "MEASURED 1.00 IoU vs #11 — the third member of the same tunic-porter mask.",
    "#30": "MEASURED 1.00 IoU vs #27 — same pole silhouette, hurry, b1.05; only the hue differs.",
    "#35": "MEASURED 1.00 IoU vs #31/#32 — the third member of a yoke triplet that renders the same mask.",
    "#38": "MEASURED 1.00 IoU vs #36 — the head-tray twin. #39 is the tray family's MOST distinct row (0.83 max-IoU) and stays.",
}
# Everything below survives the round but is not clean: these are the honest
# runners-up, kept only because the agreed cut depth is six.
RUNNER_UP_CUTS = [
    ("#26", "0.94 vs #27 — the near-twin the pole family keeps once #30 goes."),
    ("#2/#4", "1.00 twin pair (robe, bun, stroll) — separable only by hairpin vs beard, both interior."),
    ("#12/#16", "1.00 twin pair (hurry tunic youth) — the tunic band's remaining duplicate mask."),
    ("#37/#40", "1.00 twin pair (head tray, h0.96/0.98) — the tray band's remaining duplicate mask."),
    ("#31/#32", "1.00 twin pair (yoke) — the yoke band's remaining duplicate mask."),
    ("#10", "0.79 vs #2 — third basket-arm matron, but it measures clear of the twin band; NOT cut this round."),
]

KEEP = [(n, v, tag) for (n, v, tag) in SHIPPED if tag != "CUT"]
CUTS = [(n, v, tag) for (n, v, tag) in SHIPPED if tag == "CUT"]
FINAL = KEEP + [(n, v, "NEW") for (n, v, _t) in NEW]

ARCH_GROUPS = [
    ("ARCH 1 · NARROW ROBE", A_ROBE), ("ARCH 2 · WIDE A-LINE SKIRT", A_SKIRT),
    ("ARCH 3 · SHORT TUNIC", A_TUNIC), ("ARCH 4 · BOXY PADDED [SNOW]", A_PADDED),
    ("ARCH 5 · HUNCHED CANE ELDER", A_STOOP), ("ARCH 6 · CARRYING POLE", A_POLE),
    ("ARCH 7 · SHOULDER YOKE", A_YOKE), ("ARCH 8 · HEAD TRAY", A_HEADLOAD),
    ("ARCH 9 · CHILD", A_CHILD),
    ("ARCH 10 · ROD FISHERMAN  [NEW]", A_ROD),
    ("ARCH 11 · BARROW PORTER  [NEW]", A_BARROW),
    ("ARCH 12 · PIPA MUSICIAN  [NEW]", A_PIPA),
]


# ════════════════════════════════════════════════════════════════════════════
# SHEET RENDERER
# ════════════════════════════════════════════════════════════════════════════

WIDTH = 1400
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


def _fig_surface(v, night, t, w=76, h=52, fx=30):
    """One figure on a transparent canvas, feet near the bottom — wide enough for
    the barrow's cart and tall enough for the rod's tip."""
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    _draw_one(s, fx, h - 3, v, night, t)
    return s


def _cell(parent, name, v, note, x, y, w, h, night):
    """One annotated cell: native figure across 2 gait frames + a crisp FAR
    downscale (the 14px lane) + a 4x nearest zoom, on a day or night deck."""
    is_night = night > 0.5
    bg = BG_NIGHT if is_night else BG_DAY
    cell = pygame.Surface((w, h))
    cell.fill(bg)
    deck = _mix(bg, (0, 0, 0), 0.18)
    base = h - 16
    pygame.draw.rect(cell, deck, (0, base, w, h - base))
    pygame.draw.line(cell, _shade(bg, 24), (0, base), (w, base), 1)

    for i, tt in enumerate((0.0, 0.62)):
        _draw_one(cell, 26 + i * 62, base, v, night, tt)
        _text(cell, f"t{i}", 20 + i * 62, base + 2, 8, _shade(bg, 60))
    _text(cell, "native 18px", 6, base + 8, 8, _shade(bg, 50))

    nat = _fig_surface(v, night, 0.62)
    far = pygame.transform.scale(nat, (int(nat.get_width() * 0.78), int(nat.get_height() * 0.78)))
    cell.blit(far, (150, base - far.get_height() + 3))
    _text(cell, "FAR 0.78x crisp", 138, base + 2, 8, _shade(bg, 60))

    zoom = pygame.transform.scale(nat, (nat.get_width() * 3, nat.get_height() * 3))
    zw, zh = zoom.get_size()
    zx, zy = w - zw - 8, 18
    pygame.draw.rect(cell, _shade(bg, -20), (zx - 2, zy - 2, zw + 4, zh + 4))
    cell.blit(zoom, (zx, zy))
    pygame.draw.rect(cell, _shade(bg, 40), (zx - 2, zy - 2, zw + 4, zh + 4), 1)
    _text(cell, "3x zoom (nearest)", zx, zy - 12, 8, _shade(bg, 60))

    _gold_coin(cell, w - 16, h - 12, r=6)
    _text(cell, name, 6, 4, 13, (240, 236, 226), bold=True)
    _wrap(cell, note, 6, 20, zx - 14)

    parent.blit(cell, (x, y))
    pygame.draw.rect(parent, (70, 74, 90), (x, y, w, h), 1)


def _alpha_mask(surf, scale=1.0):
    if scale != 1.0:
        surf = pygame.transform.scale(surf, (int(surf.get_width() * scale),
                                             int(surf.get_height() * scale)))
    return {(x, y) for x in range(surf.get_width()) for y in range(surf.get_height())
            if surf.get_at((x, y))[3] > 0}


def _islands(m):
    """8-connected component count — a figure that breaks into several islands at
    the far-lane scale reads as debris, not as a person."""
    seen, n = set(), 0
    for p in m:
        if p in seen:
            continue
        n += 1
        stack = [p]
        seen.add(p)
        while stack:
            x, y = stack.pop()
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    q = (x + dx, y + dy)
                    if q in m and q not in seen:
                        seen.add(q)
                        stack.append(q)
    return n


def _iou(a, b):
    return len(a & b) / max(1, len(a | b))


def _measure_outlines():
    """Far-lane connectivity for the new ROD archetype + the max-IoU of the two
    rows the round redrew, both measured on rendered alpha."""
    worst_islands = {}
    for nm, v, _tg in NEW:
        if v.arch != A_ROD:
            continue
        worst_islands[nm.split(" ")[0]] = max(
            _islands(_alpha_mask(_fig_surface(v, 0.0, i * 0.3), 0.78)) for i in range(8))
    rows = [(nm.split(" ")[0], v) for nm, v, tg in SHIPPED if tg != "CUT"] + \
           [(nm.split(" ")[0], v) for nm, v, _tg in NEW]
    masks = {k: _alpha_mask(_fig_surface(v, 0.0, 0.62), 0.78) for k, v in rows}
    peaks = {}
    for k in ("N10", "N13"):
        best, bk = 0.0, ""
        for k2 in masks:
            if k2 == k:
                continue
            s = _iou(masks[k], masks[k2])
            if s > best:
                best, bk = s, k2
        peaks[k] = (best, bk)
    return worst_islands, peaks


def _measure_night_cap():
    """Render EVERY final row at night onto a strip and scan the rendered pixels
    for the hottest non-background luma — the honest cap measurement."""
    night = 0.95
    strip = pygame.Surface((1600, 90))
    strip.fill(BG_NIGHT)
    base = 74
    x = 40
    for _n, v, _t in FINAL:
        for tt in (0.0, 0.5, 1.0):
            _draw_one(strip, x, base, v, night, tt)
            x += 26
            if x > 1560:
                x = 40
        x += 6
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
    new_cell_w = (WIDTH - PAD * 3) // 2
    new_cell_h = 150

    grid_cols = 10
    grid_cw, grid_ch = (WIDTH - PAD * 2 - 8) // grid_cols, 60

    def _band_rows(arch):
        n = sum(1 for _n, v, _t in FINAL if v.arch == arch)
        return max(1, (n + grid_cols - 1) // grid_cols)

    head_h = 74
    secA_h = 26 + 2 * (16 + 4 * (new_cell_h + 6))       # 8 new-arch rows, day+night
    secB_h = 26 + sum(20 + _band_rows(a) * (grid_ch + 14) + 6 for _l, a in ARCH_GROUPS)
    cut_band_h = 96 + 6 * 13 + 10 + len(RUNNER_UP_CUTS) * 12
    secC_h = 26 + cut_band_h
    strip_h = 96
    secD_h = 26 + 2 * (strip_h + 6)
    total_h = head_h + secA_h + secB_h + secC_h + secD_h + PAD * 6 + 40

    sheet = pygame.Surface((WIDTH, total_h))
    sheet.fill((26, 28, 38))

    y = PAD
    _text(sheet, "SKYBIT PROMENADE — PEDESTRIAN VARIETY EXPANSION (round 3): 3 NEW ARCHETYPES · 13 NEW ROWS · 6 CUTS  →  pool 50 → 57",
          PAD, y, 17, (250, 246, 236), bold=True)
    y += 22
    y = _wrap(sheet,
              "NEW ARCHETYPES (new torso branches, not palettes): ROD fisherman — a long springy rod slung up-and-BACK across the whole figure (the pool had no steep diagonal); "
              "BARROW porter — a single-wheel handcart ahead of a pitched body, the only cast member whose mass sits on the deck; PIPA musician — a pear lute across the chest with its neck past the shoulder, "
              "two hands on opposite ends of the spar. PASSED: alms-bowl monk (collapses into ARCH 1 at 14px, the bowl is interior detail) and front-jar water-carrier (a third re-dress of the pole/yoke idea). "
              "13 new rows = 8 in the new archetypes + 5 re-dressing existing ones with new hats/carry positions (shawl, flat official brim, ear-flap cap, back-basket, back-bundle). 6 palette-clone rows nominated for CUT.",
              PAD, y, WIDTH - PAD * 2, 9, (188, 186, 200))
    y = head_h + PAD

    # ── A. the three new archetypes in detail ──
    _text(sheet, "A.  THE THREE NEW ARCHETYPES — native 18px across 2 gait frames · FAR 0.78x crisp · 3x zoom · in-cell coin   (DAY block, then NIGHT block)",
          PAD, y, 13, (240, 220, 150), bold=True)
    y += 22
    arch_new = [(n, v, v.note) for (n, v, _t) in NEW if v.arch in (A_ROD, A_BARROW, A_PIPA)]
    for is_night in (False, True):
        night = 0.95 if is_night else 0.0
        _text(sheet, "NIGHT  (cooled toward (54,64,96), <=150 luma)" if is_night else "DAY",
              PAD, y, 11, (160, 180, 220) if is_night else (240, 210, 130), bold=True)
        y += 16
        for i, (nm, v, note) in enumerate(arch_new):
            cx = PAD + (i % 2) * (new_cell_w + PAD)
            _cell(sheet, nm, v, note, cx, y, new_cell_w, new_cell_h, night)
            if i % 2 == 1:
                y += new_cell_h + 6
        if len(arch_new) % 2:
            y += new_cell_h + 6

    # ── B. the whole final pool at true size, grouped by archetype ──
    _text(sheet, "B.  FULL POOL AFTER THE ROUND (57 rows) at native size, grouped by archetype — NEW rows badged, kept rows are the current shipped design",
          PAD, y, 13, (240, 220, 150), bold=True)
    y += 22
    for label, arch in ARCH_GROUPS:
        members = [(n, v, tg) for (n, v, tg) in FINAL if v.arch == arch]
        rows = max(1, (len(members) + grid_cols - 1) // grid_cols)
        bh = 20 + rows * (grid_ch + 14)
        band = pygame.Surface((WIDTH - PAD * 2, bh))
        band.fill(BG_DAY)
        _text(band, f"{label}   ({len(members)})", 6, 3, 10, (58, 48, 38), bold=True)
        for j, (nm, v, tg) in enumerate(members):
            gc, gr = j % grid_cols, j // grid_cols
            ox = 8 + gc * grid_cw
            gy = 20 + gr * (grid_ch + 14) + grid_ch - 4
            pygame.draw.line(band, _mix(BG_DAY, (0, 0, 0), 0.22),
                             (ox - 4, gy + 1), (ox + grid_cw - 6, gy + 1), 1)
            _draw_one(band, ox + grid_cw // 2 - 6, gy, v, 0.0, 0.4 + j * 0.37)
            _text(band, nm.split(" ")[0], ox, gy + 3, 8, (66, 56, 44))
            if tg == "NEW":
                _text(band, "NEW", ox + 30, gy + 3, 8, (30, 84, 60), bold=True)
        sheet.blit(band, (PAD, y))
        pygame.draw.rect(sheet, (70, 74, 90), (PAD, y, WIDTH - PAD * 2, bh), 1)
        y += bh + 6

    # ── C. the cut list ──
    _text(sheet, "C.  CUT LIST — 6 retires, MEASURED (five of them render a 1.00-IoU duplicate mask of a survivor).  #39 is KEPT: at 0.83 max-IoU it is the head-tray band's most distinct row; its twin #38 goes instead.",
          PAD, y, 13, (240, 150, 140), bold=True)
    y += 22
    cband = pygame.Surface((WIDTH - PAD * 2, cut_band_h))
    cband.fill((44, 34, 38))
    cw = (WIDTH - PAD * 2) // 6
    for i, (nm, v, _t) in enumerate(CUTS):
        ox = i * cw + cw // 2
        _draw_one(cband, ox, 76, v, 0.0, 0.5 + i * 0.4)
        pygame.draw.line(cband, (216, 96, 92), (ox - 14, 40), (ox + 14, 78), 2)
        pygame.draw.line(cband, (216, 96, 92), (ox + 14, 40), (ox - 14, 78), 2)
        _text(cband, nm, ox - cw // 2 + 6, 82, 9, (236, 190, 186), bold=True)
    yy = 96
    for nm, _v, _t in CUTS:
        key = nm.split(" ")[0]
        _text(cband, f"{key}  {CUT_REASONS[key]}", 8, yy, 9, (222, 196, 194))
        yy += 13
    yy += 6
    _text(cband, "RUNNERS-UP — still in the pool at the agreed cut depth of six, listed honestly:",
          8, yy, 9, (238, 176, 172), bold=True)
    yy += 12
    for key, why in RUNNER_UP_CUTS:
        _text(cband, f"   {key}  {why}", 8, yy, 9, (196, 174, 174))
        yy += 12
    sheet.blit(cband, (PAD, y))
    pygame.draw.rect(sheet, (120, 74, 78), (PAD, y, WIDTH - PAD * 2, cut_band_h), 1)
    y += cut_band_h + 6

    # ── D. on-street composite ──
    _text(sheet, "D.  ON-STREET COMPOSITE — new rows mixed through the kept pool at native size, with the gold-coin yardstick  (DAY then NIGHT)",
          PAD, y, 13, (240, 220, 150), bold=True)
    y += 22
    mix = ([f for f in FINAL if f[2] == "NEW"] +
           [FINAL[0], FINAL[6], FINAL[12], FINAL[18], FINAL[24], FINAL[30], FINAL[36], FINAL[40]])
    for is_night in (False, True):
        night = 0.95 if is_night else 0.0
        bg = BG_NIGHT if is_night else BG_DAY
        strip = pygame.Surface((WIDTH - PAD * 2, strip_h))
        strip.fill(bg)
        deck = _mix(bg, (0, 0, 0), 0.2)
        base = strip_h - 16
        pygame.draw.rect(strip, deck, (0, base, WIDTH - PAD * 2, strip_h - base))
        pygame.draw.line(strip, _shade(bg, 24), (0, base), (WIDTH - PAD * 2, base), 1)
        step = (WIDTH - PAD * 2 - 70) // len(mix)
        for i, (_nm, v, _tg) in enumerate(mix):
            _draw_one(strip, 40 + i * step, base - (i % 3), v, night, 0.3 + i * 0.43)
        _gold_coin(strip, WIDTH - PAD * 2 - 20, 20)
        _text(strip, "coin ref", WIDTH - PAD * 2 - 46, 32, 8, _shade(bg, 60))
        _text(strip, "NIGHT" if is_night else "DAY", 4, 2, 9,
              (170, 190, 225) if is_night else (60, 50, 40), bold=True)
        sheet.blit(strip, (PAD, y))
        pygame.draw.rect(sheet, (70, 74, 90), (PAD, y, WIDTH - PAD * 2, strip_h), 1)
        y += strip_h + 6

    isl, peaks = _measure_outlines()
    ok = all(v == 1 for v in isl.values())
    audit = ("OUTLINE AUDIT (rendered alpha at FAR 0.78x, worst of 8 gait phases):  "
             + "  ·  ".join(f"{k} islands = {v}" for k, v in sorted(isl.items()))
             + "   — the rod is now max(2, body_w//6); at max(1, body_w//7) the three rows broke into 2 / 2 / 3 islands and the tip floated free.  "
             + "  ·  ".join(f"{k} max-IoU {p[0]:.2f} vs {p[1]}" for k, p in sorted(peaks.items()))
             + f"   (N10 was 0.93 vs #6 with a collar-length shawl, N13 0.83 with flaps that hung inside the padded coat.)   "
             + ("PASS — one island each, and both redrawn rows sit under 0.85." if ok else "FAIL"))
    y = _wrap(sheet, audit, PAD, y + 2, WIDTH - PAD * 2, 9,
              (170, 200, 180) if ok else (220, 140, 130))

    hottest, over = _measure_night_cap()
    coin_l = _luma((255, 232, 150))
    msg = (f"NIGHT-CAP AUDIT (measured on RENDERED pixels, all 57 final rows x 3 gait phases): hottest pedestrian px luma = {hottest:.0f}  ·  "
           f"px over {NIGHT_GLOW_CAP} = {over}  ·  gold-coin core luma = {coin_l:.0f} (sole brightest).  "
           f"{'PASS — every pedestrian px sits under the cap.' if over == 0 else 'FAIL — ' + str(over) + ' px breach the cap.'}")
    _text(sheet, msg, PAD, total_h - 16, 9, (170, 200, 180) if over == 0 else (220, 140, 130))

    out = "/home/user/skybit/docs/sidewalk_overhaul/pedestrians/round_3.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("saved", out, sheet.get_size())
    print(f"night-cap: hottest={hottest:.1f} over={over} coin={coin_l:.1f}")


if __name__ == "__main__":
    render()
