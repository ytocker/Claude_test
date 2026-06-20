"""Candidate FLYING TOASTER store skin — round-1 exploration (5 variants).

A secret ultra-premium ABSURD flyer: the player's flapping bird becomes a
chrome toaster with little wings — the classic After Dark gag. Each variant
is a full-body build that animates over the 4 base wing poses
(`parrot._WING_ANGLES`) and is rotated by the bird's dive/climb tilt by the
shared getter factory.

Contract (mirrors game/animal_skins.py so the winner lifts straight into a
production game/animal_toaster.py later):

  * `build_toaster_vN(wing_angle_deg) -> pygame.Surface`  draws one flat frame
    on a 64×84 SRCALPHA canvas.
  * a cached `(frame_idx, tilt_deg) -> Surface` getter from a local
    `_make_prebuilt_skin(build_fn)`.

Why the geometry sits where it does: collision is a fixed 14px circle at the
BODY centre (32,44), independent of the sprite, so the toaster body mass stays
on the base bird's body anchor for fairness — no oversized appliances.

North star: "a skin lives or dives at 40px in motion." Every variant leans on
ONE bold silhouette — a chrome appliance box — plus the high-contrast tell:
two gold toast slices jutting from the top slot, with little flapping wings.
That gold-toast-on-chrome contrast is the colour pop that must survive the
downscale on day AND night.
"""
import math
import pygame

from game import parrot
from game.parrot import (
    SPRITE_W, SPRITE_H, _WING_ANGLES, _add_outline, _aaellipse,
)


# ── tall-canvas constants (toast pops above the body, wings swing wide) ───────
COMPOSITE_W = SPRITE_W          # 64
COMPOSITE_H = 84                # headroom for popping toast + wing arcs
DY          = 12                # body offset down into the tall canvas

# Toaster body centre at the base bird body anchor → (32, 44).
BCX, BCY = 32, 32 + DY
# Top of the chrome body (where the slot + toast live).
TOP_Y    = BCY - 14


# ── shared factory (local copy of animal_skins._make_prebuilt_skin) ──────────
def _make_prebuilt_skin(build_fn):
    """Cached `(frame_idx, tilt_deg) -> Surface` getter for a full-body
    build_fn(angle). Lazy 4-frame build + per-(frame, 3°) rotation cache,
    each frame outlined with the house silhouette outline."""
    state = {"frames": None, "rot": {}}

    def getter(frame_idx, tilt_deg):
        if state["frames"] is None:
            state["frames"] = [_add_outline(build_fn(a)) for a in _WING_ANGLES]
        frames = state["frames"]
        frame_idx %= len(frames)
        key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
        s = state["rot"].get(key)
        if s is None:
            s = pygame.transform.rotozoom(frames[frame_idx], key[1], 1.0)
            state["rot"][key] = s
        return s

    return getter


# ── tiny shared drawing helpers ──────────────────────────────────────────────
def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _flap(angle_deg):
    """Map a wing angle to a 0..1 'wing is up' factor. _WING_ANGLES runs
    50→-40, so this drives the wing spread and the toast bob (mid-pop)."""
    return (angle_deg + 40) / 90.0


def _rot_blit(surf, wing, anchor):
    surf.blit(wing, wing.get_rect(center=anchor).topleft)


def _eye(surf, cx, cy, r, *, iris=(28, 30, 40), white=(250, 250, 245)):
    """A friendly googly eye: white sclera, dark iris, top-left glint."""
    pygame.draw.circle(surf, white, (cx, cy), r)
    pygame.draw.circle(surf, iris, (cx + max(1, r // 4), cy), max(2, r - 2))
    pygame.draw.circle(surf, (255, 255, 255), (cx - r // 3, cy - r // 3),
                       max(1, r // 3))


def _toast(surf, cx, top_y, w, h, *, gold, gold_d, gold_h, crust, butter=False):
    """One slice of toast: warm-gold body, darker crust rim, a bright top
    bevel, optional butter glint. The gold-on-chrome contrast is the whole
    skin's colour tell, so the crust rim is what keeps the slice legible at
    40px when the body around it goes mirror-grey."""
    half = w // 2
    # Rounded bread top (two shoulders + a domed crown).
    pts = [
        (cx - half, top_y + h),
        (cx - half, top_y + 5),
        (cx - half + 2, top_y + 1),
        (cx - 2, top_y),
        (cx + 2, top_y),
        (cx + half - 2, top_y + 1),
        (cx + half, top_y + 5),
        (cx + half, top_y + h),
    ]
    pygame.draw.polygon(surf, crust, pts)
    inner = [(x - (1 if x < cx else -1) if abs(x - cx) > 2 else x,
              y + 1) for x, y in pts]
    pygame.draw.polygon(surf, gold, inner)
    # Bright top bevel sells the "fresh out of the toaster" sheen.
    pygame.draw.line(surf, gold_h, (cx - half + 3, top_y + 3),
                     (cx + half - 3, top_y + 3), 2)
    # Crust outline reinforces the slice edge for the downscale.
    pygame.draw.polygon(surf, gold_d, pts, 1)
    if butter:
        pygame.draw.circle(surf, (255, 236, 150), (cx, top_y + h // 2 + 1), 2)


def _chrome_body(surf, cx, cy, hw, hh, *, base, dark, light, top_hi,
                 corner=6):
    """A rounded-rect appliance body shaded for metal: a bright top band, a
    mid base, and a dark underbelly. The bright-top / dark-bottom split is the
    cheapest, most reliable 'this is shiny metal' cue at gameplay size."""
    rect = pygame.Rect(cx - hw, cy - hh, hw * 2, hh * 2)
    # Dark underbody first (full box), then the lit body inset from the bottom.
    pygame.draw.rect(surf, dark, rect, border_radius=corner)
    lit = pygame.Rect(cx - hw, cy - hh, hw * 2, int(hh * 1.5))
    pygame.draw.rect(surf, base, lit, border_radius=corner)
    # Bright top highlight band (the mirror catch-light).
    hi = pygame.Rect(cx - hw + 2, cy - hh + 2, hw * 2 - 4, hh)
    pygame.draw.rect(surf, light, hi, border_radius=corner)
    pygame.draw.line(surf, top_hi, (cx - hw + corner, cy - hh + 2),
                     (cx + hw - corner, cy - hh + 2), 2)
    # A vertical specular streak — the classic curved-chrome reflection.
    streak = pygame.Surface((4, hh * 2 - 4), pygame.SRCALPHA)
    streak.fill((*top_hi, 120))
    surf.blit(streak, (cx - hw // 2, cy - hh + 2))
    pygame.draw.rect(surf, dark, rect, 1, border_radius=corner)


# ═════════════════════════════════════════════════════════════════════════════
# V1 · AFTER DARK CLASSIC — mirror-chrome 2-slot toaster, white feathered bird
#     wings, 2 gold toast mid-pop, side lever + dial. The pure homage, no face.
#     40px tell: chrome box + 2 gold slices + white wing-span. Day/night: the
#     white wings + gold toast carry both.
# ═════════════════════════════════════════════════════════════════════════════
_C1_BASE = (176, 184, 196)
_C1_DARK = (96, 104, 120)
_C1_LITE = (214, 222, 232)
_C1_HI   = (248, 252, 255)
_C1_GOLD = (236, 176, 78)
_C1_GLDD = (176, 116, 42)
_C1_GLDH = (255, 222, 140)
_C1_CRST = (150, 92, 36)
_C1_WING = (250, 250, 248)
_C1_WINGD = (196, 204, 216)
_C1_WINGH = (255, 255, 255)


def _feather_wing(angle_deg, sgn, base, dark, light, scale=1.0):
    """A little feathered bird wing — three rounded primary feathers fanning
    out. The white feather span is the After Dark signature, so it reads as
    BIRD wings, not appliance flaps."""
    w = pygame.Surface((40, 36), pygame.SRCALPHA)
    # Three overlapping feather lobes.
    for i, (lx, ly, lw, lh) in enumerate(
            ((10, 16, 13, 8), (18, 12, 13, 8), (26, 10, 12, 7))):
        _aaellipse(w, dark, (lx + 1, ly + 1), lw, lh)
        _aaellipse(w, base, (lx, ly), lw, lh)
    # Bright leading edge along the top of the fan.
    pygame.draw.line(w, light, (10, 12), (32, 7), 2)
    # Shoulder root.
    _aaellipse(w, base, (10, 18), 6, 7)
    if scale != 1.0:
        sz = (max(1, int(40 * scale)), max(1, int(36 * scale)))
        w = pygame.transform.smoothscale(w, sz)
    out = pygame.transform.rotate(w, angle_deg)
    if sgn < 0:
        out = pygame.transform.flip(out, True, False)
    return out


def build_toaster_v1(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)
    spread = (f - 0.5) * 30          # wings sweep up/down symmetrically
    bob = int((f - 0.5) * 5)         # toast bobs as if mid-pop

    # Far wing (behind body), opposite phase for depth.
    _rot_blit(surf, _feather_wing(18 + spread, +1, _C1_WING, _C1_WINGD,
                                  _C1_WINGH), (BCX + 18, BCY - 6))

    # Two gold toast slices jutting from the slot (drawn before the body top
    # so the slot lip overlaps their base).
    _toast(surf, BCX - 6, TOP_Y - 9 - bob, 13, 16, gold=_C1_GOLD,
           gold_d=_C1_GLDD, gold_h=_C1_GLDH, crust=_C1_CRST)
    _toast(surf, BCX + 8, TOP_Y - 7 + bob, 13, 16, gold=_C1_GOLD,
           gold_d=_C1_GLDD, gold_h=_C1_GLDH, crust=_C1_CRST)

    # Chrome body.
    _chrome_body(surf, BCX, BCY, 18, 15, base=_C1_BASE, dark=_C1_DARK,
                 light=_C1_LITE, top_hi=_C1_HI)
    # Dark slot across the top, with the toast rising out of it.
    pygame.draw.rect(surf, (40, 44, 54),
                     (BCX - 15, TOP_Y - 1, 30, 4), border_radius=2)
    pygame.draw.line(surf, _C1_HI, (BCX - 14, TOP_Y - 1), (BCX + 14, TOP_Y - 1), 1)

    # Side lever (chrome knob on a stem) + round dial.
    pygame.draw.line(surf, _C1_DARK, (BCX + 18, BCY - 4), (BCX + 22, BCY - 4), 3)
    pygame.draw.circle(surf, _C1_LITE, (BCX + 23, BCY - 4), 3)
    pygame.draw.circle(surf, _C1_DARK, (BCX + 23, BCY - 4), 3, 1)
    pygame.draw.circle(surf, _C1_DARK, (BCX - 8, BCY + 7), 4)
    pygame.draw.circle(surf, _C1_LITE, (BCX - 8, BCY + 7), 4, 1)
    pygame.draw.line(surf, _C1_HI, (BCX - 8, BCY + 7), (BCX - 6, BCY + 5), 1)

    # Little chrome feet.
    for fx in (BCX - 11, BCX + 11):
        pygame.draw.rect(surf, _C1_DARK, (fx - 2, BCY + 14, 4, 4),
                         border_radius=1)

    # Near wing (over the body) — the hero white feather span.
    _rot_blit(surf, _feather_wing(-12 - spread, -1, _C1_WING, _C1_WINGD,
                                  _C1_WINGH), (BCX - 16, BCY))
    return surf


get_toaster_v1 = _make_prebuilt_skin(build_toaster_v1)


# ═════════════════════════════════════════════════════════════════════════════
# V2 · CREAM RETRO DINER — 1950s cream enamel body with a chrome base + chrome
#     trim, a chubby googly-eyed FACE on the front, 2 gold toast, little angel
#     wings. 40px tell: warm-cream box + gold toast + the two big eyes.
# ═════════════════════════════════════════════════════════════════════════════
_C2_CREAM = (244, 230, 198)
_C2_CRMD  = (206, 184, 142)
_C2_CRMH  = (255, 248, 226)
_C2_CHRM  = (190, 198, 210)
_C2_CHRMD = (120, 128, 144)
_C2_CHRMH = (245, 250, 255)
_C2_GOLD  = (240, 182, 84)
_C2_GLDD  = (182, 120, 44)
_C2_GLDH  = (255, 226, 146)
_C2_CRST  = (156, 96, 38)
_C2_WING  = (255, 252, 244)
_C2_WINGD = (214, 220, 226)
_C2_TEAL  = (90, 188, 188)        # period accent stripe


def _angel_wing(angle_deg, sgn, base, dark, scale=1.0):
    """A small rounded ANGEL wing — a soft scalloped half-fan. Reads cuter /
    more 'magical appliance' than the feathered bird wing of v1."""
    w = pygame.Surface((34, 32), pygame.SRCALPHA)
    body = [(8, 18), (14, 8), (24, 6), (30, 12), (26, 18), (30, 22),
            (20, 22), (12, 24)]
    pygame.draw.polygon(w, dark, [(x + 1, y + 1) for x, y in body])
    pygame.draw.polygon(w, base, body)
    # Scalloped lower edge — three little feather bumps.
    for bx in (14, 20, 26):
        pygame.draw.circle(w, base, (bx, 22), 3)
        pygame.draw.circle(w, dark, (bx, 22), 3, 1)
    pygame.draw.line(w, (255, 255, 255), (12, 16), (28, 9), 1)
    if scale != 1.0:
        sz = (max(1, int(34 * scale)), max(1, int(32 * scale)))
        w = pygame.transform.smoothscale(w, sz)
    out = pygame.transform.rotate(w, angle_deg)
    if sgn < 0:
        out = pygame.transform.flip(out, True, False)
    return out


def build_toaster_v2(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)
    spread = (f - 0.5) * 26
    bob = int((f - 0.5) * 5)

    _rot_blit(surf, _angel_wing(16 + spread, +1, _C2_WING, _C2_WINGD),
              (BCX + 17, BCY - 4))

    # Two toast slices.
    _toast(surf, BCX - 6, TOP_Y - 8 - bob, 13, 15, gold=_C2_GOLD,
           gold_d=_C2_GLDD, gold_h=_C2_GLDH, crust=_C2_CRST, butter=True)
    _toast(surf, BCX + 8, TOP_Y - 6 + bob, 13, 15, gold=_C2_GOLD,
           gold_d=_C2_GLDD, gold_h=_C2_GLDH, crust=_C2_CRST)

    # Cream enamel body (warm, slightly taller dome) on a chrome plinth.
    _chrome_body(surf, BCX, BCY + 8, 18, 8, base=_C2_CHRM, dark=_C2_CHRMD,
                 light=_C2_CHRMH, top_hi=_C2_CHRMH, corner=5)
    _chrome_body(surf, BCX, BCY - 1, 17, 13, base=_C2_CREAM, dark=_C2_CRMD,
                 light=_C2_CRMH, top_hi=_C2_CRMH, corner=8)
    # Period teal pinstripe across the cream.
    pygame.draw.line(surf, _C2_TEAL, (BCX - 15, BCY + 4), (BCX + 15, BCY + 4), 2)

    # Dark slot.
    pygame.draw.rect(surf, (44, 40, 46), (BCX - 14, TOP_Y, 28, 4),
                     border_radius=2)

    # Chrome lever on the side.
    pygame.draw.line(surf, _C2_CHRMD, (BCX + 17, BCY - 3), (BCX + 21, BCY - 3), 3)
    pygame.draw.circle(surf, _C2_CHRMH, (BCX + 22, BCY - 3), 3)

    # ── HERO FACE: two big googly eyes + rosy cheeks + a little smile ──
    _eye(surf, BCX - 5, BCY - 1, 5)
    _eye(surf, BCX + 6, BCY - 1, 5)
    for ckx in (BCX - 9, BCX + 10):
        pygame.draw.circle(surf, (255, 168, 158), (ckx, BCY + 4), 3)
    pygame.draw.arc(surf, (150, 96, 60),
                    (BCX - 5, BCY + 2, 12, 8), math.radians(200),
                    math.radians(340), 2)

    # Chrome feet.
    for fx in (BCX - 11, BCX + 11):
        pygame.draw.rect(surf, _C2_CHRMD, (fx - 2, BCY + 15, 4, 4),
                         border_radius=1)

    _rot_blit(surf, _angel_wing(-12 - spread, -1, _C2_WING, _C2_WINGD),
              (BCX - 16, BCY))
    return surf


get_toaster_v2 = _make_prebuilt_skin(build_toaster_v2)


# ═════════════════════════════════════════════════════════════════════════════
# V3 · COPPER STEAMPUNK — warm hammered-copper body, brass lever + dial + slot
#     trim, a SINGLE tall toast popping HIGH (caught mid-pop), mechanical
#     bronze-feathered wings. 40px tell: copper box + one tall gold slice +
#     brass glints. Rich warm metal reads beautifully on a night sky.
# ═════════════════════════════════════════════════════════════════════════════
_C3_BASE = (196, 116, 70)
_C3_DARK = (120, 62, 36)
_C3_LITE = (236, 168, 112)
_C3_HI   = (255, 214, 168)
_C3_BRSS = (224, 178, 84)
_C3_BRSD = (158, 116, 40)
_C3_BRSH = (255, 230, 150)
_C3_GOLD = (240, 188, 92)
_C3_GLDD = (176, 116, 46)
_C3_GLDH = (255, 230, 156)
_C3_CRST = (150, 92, 40)
_C3_WING = (208, 140, 92)
_C3_WINGD = (140, 80, 48)
_C3_WINGH = (244, 196, 144)


def build_toaster_v3(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)
    spread = (f - 0.5) * 30
    bob = int((f - 0.5) * 6)          # the tall single slice bobs more

    _rot_blit(surf, _feather_wing(18 + spread, +1, _C3_WING, _C3_WINGD,
                                  _C3_WINGH), (BCX + 18, BCY - 6))

    # ── HERO: a single TALL toast popping high out of the slot ──
    _toast(surf, BCX, TOP_Y - 18 - bob, 15, 22, gold=_C3_GOLD,
           gold_d=_C3_GLDD, gold_h=_C3_GLDH, crust=_C3_CRST, butter=True)
    # Little steam curls rising off the hot slice (kept tiny so they survive).
    for sx, sy in ((BCX - 4, TOP_Y - 22), (BCX + 4, TOP_Y - 24)):
        pygame.draw.circle(surf, (255, 240, 220, 120) if False else
                           (236, 224, 210), (sx, sy - bob), 1)

    # Copper body.
    _chrome_body(surf, BCX, BCY, 18, 15, base=_C3_BASE, dark=_C3_DARK,
                 light=_C3_LITE, top_hi=_C3_HI)
    # Hammered-copper dimples.
    for dx, dy in ((BCX - 9, BCY + 6), (BCX, BCY + 8), (BCX + 9, BCY + 5),
                   (BCX - 5, BCY + 10), (BCX + 5, BCY + 10)):
        pygame.draw.circle(surf, _C3_DARK, (dx, dy), 1)

    # Brass slot trim.
    pygame.draw.rect(surf, _C3_BRSD, (BCX - 15, TOP_Y - 1, 30, 5),
                     border_radius=2)
    pygame.draw.rect(surf, (38, 30, 26), (BCX - 13, TOP_Y, 26, 3),
                     border_radius=1)
    pygame.draw.line(surf, _C3_BRSH, (BCX - 14, TOP_Y - 1), (BCX + 14, TOP_Y - 1), 1)

    # Brass lever + big riveted dial.
    pygame.draw.line(surf, _C3_BRSD, (BCX + 18, BCY - 5), (BCX + 22, BCY - 5), 3)
    pygame.draw.circle(surf, _C3_BRSS, (BCX + 23, BCY - 5), 3)
    pygame.draw.circle(surf, _C3_BRSD, (BCX + 23, BCY - 5), 3, 1)
    pygame.draw.circle(surf, _C3_BRSS, (BCX - 8, BCY + 6), 5)
    pygame.draw.circle(surf, _C3_BRSD, (BCX - 8, BCY + 6), 5, 1)
    for a in range(0, 360, 60):
        ex = BCX - 8 + int(4 * math.cos(math.radians(a)))
        ey = BCY + 6 + int(4 * math.sin(math.radians(a)))
        pygame.draw.line(surf, _C3_BRSD, (BCX - 8, BCY + 6), (ex, ey), 1)
    pygame.draw.circle(surf, _C3_BRSH, (BCX - 9, BCY + 5), 1)

    # Riveted feet.
    for fx in (BCX - 11, BCX + 11):
        pygame.draw.rect(surf, _C3_BRSD, (fx - 2, BCY + 14, 4, 4),
                         border_radius=1)
        pygame.draw.circle(surf, _C3_BRSH, (fx, BCY + 16), 1)

    _rot_blit(surf, _feather_wing(-12 - spread, -1, _C3_WING, _C3_WINGD,
                                  _C3_WINGH), (BCX - 16, BCY))
    return surf


get_toaster_v3 = _make_prebuilt_skin(build_toaster_v3)


# ═════════════════════════════════════════════════════════════════════════════
# V4 · MINT KAWAII — pastel-mint appliance body, BIG googly eyes, rosy cheeks,
#     a tiny halo of fluffy white angel wings, 2 bobbing toast. Max-cute take.
#     40px tell: soft mint box + gold toast + the big shiny eyes. Pops on night.
# ═════════════════════════════════════════════════════════════════════════════
_C4_MINT  = (158, 224, 200)
_C4_MNTD  = (96, 178, 154)
_C4_MNTH  = (210, 248, 232)
_C4_TRIM  = (236, 244, 244)
_C4_TRMD  = (170, 190, 196)
_C4_GOLD  = (242, 188, 90)
_C4_GLDD  = (184, 124, 48)
_C4_GLDH  = (255, 228, 150)
_C4_CRST  = (158, 100, 42)
_C4_WING  = (255, 255, 255)
_C4_WINGD = (210, 224, 226)
_C4_CHEEK = (255, 158, 162)


def build_toaster_v4(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)
    spread = (f - 0.5) * 28
    bob = int((f - 0.5) * 5)

    _rot_blit(surf, _angel_wing(20 + spread, +1, _C4_WING, _C4_WINGD, scale=0.95),
              (BCX + 16, BCY - 5))

    # Two cheerful toast slices.
    _toast(surf, BCX - 6, TOP_Y - 8 - bob, 13, 15, gold=_C4_GOLD,
           gold_d=_C4_GLDD, gold_h=_C4_GLDH, crust=_C4_CRST, butter=True)
    _toast(surf, BCX + 8, TOP_Y - 6 + bob, 13, 15, gold=_C4_GOLD,
           gold_d=_C4_GLDD, gold_h=_C4_GLDH, crust=_C4_CRST, butter=True)

    # Soft rounded mint body (extra-round corners read as a friendly blob).
    _chrome_body(surf, BCX, BCY, 18, 15, base=_C4_MINT, dark=_C4_MNTD,
                 light=_C4_MNTH, top_hi=_C4_MNTH, corner=9)
    # White trim band at the base.
    pygame.draw.rect(surf, _C4_TRIM, (BCX - 17, BCY + 9, 34, 5),
                     border_radius=3)
    pygame.draw.rect(surf, _C4_TRMD, (BCX - 17, BCY + 9, 34, 5), 1,
                     border_radius=3)

    # Slot.
    pygame.draw.rect(surf, (54, 70, 64), (BCX - 14, TOP_Y, 28, 4),
                     border_radius=2)

    # ── HERO FACE: oversized shiny eyes + big rosy cheeks + tiny smile ──
    _eye(surf, BCX - 6, BCY - 2, 6)
    _eye(surf, BCX + 6, BCY - 2, 6)
    for ckx in (BCX - 11, BCX + 11):
        pygame.draw.circle(surf, _C4_CHEEK, (ckx, BCY + 4), 3)
    pygame.draw.arc(surf, (120, 80, 60),
                    (BCX - 4, BCY + 3, 10, 7), math.radians(205),
                    math.radians(335), 2)

    # Little pastel lever bead.
    pygame.draw.line(surf, _C4_TRMD, (BCX + 18, BCY - 2), (BCX + 21, BCY - 2), 3)
    pygame.draw.circle(surf, (255, 184, 196), (BCX + 22, BCY - 2), 3)

    # Stubby feet.
    for fx in (BCX - 11, BCX + 11):
        pygame.draw.rect(surf, _C4_TRMD, (fx - 2, BCY + 14, 4, 4),
                         border_radius=2)

    _rot_blit(surf, _angel_wing(-14 - spread, -1, _C4_WING, _C4_WINGD,
                                scale=0.95), (BCX - 15, BCY))
    return surf


get_toaster_v4 = _make_prebuilt_skin(build_toaster_v4)


# ═════════════════════════════════════════════════════════════════════════════
# V5 · NOIR CHROME — sleek modern matte-black + chrome toaster, a glowing slot,
#     2 gold toast, sharp swept modern wings (steel-feather). Premium, minimal.
#     40px tell: black-and-chrome box + the glowing gold slot/toast. The black
#     body pops on a DAY sky; the chrome + glow pops at NIGHT.
# ═════════════════════════════════════════════════════════════════════════════
_C5_BLK  = (52, 56, 66)
_C5_BLKD = (28, 30, 38)
_C5_BLKH = (96, 102, 116)
_C5_CHRM = (200, 208, 220)
_C5_CHRD = (120, 128, 142)
_C5_CHRH = (250, 254, 255)
_C5_GOLD = (244, 190, 92)
_C5_GLDD = (180, 120, 48)
_C5_GLDH = (255, 230, 150)
_C5_CRST = (150, 92, 40)
_C5_GLOW = (255, 150, 60)         # the hot heating-element glow in the slot
_C5_WING = (206, 214, 226)
_C5_WINGD = (118, 126, 140)
_C5_WINGH = (252, 255, 255)


def _steel_wing(angle_deg, sgn, scale=1.0):
    """A sharp swept modern wing — three angular steel feathers. Reads more
    'aero / premium gadget' than the soft retro fans."""
    w = pygame.Surface((42, 34), pygame.SRCALPHA)
    for i, (x0, y0) in enumerate(((10, 18), (10, 16), (10, 14))):
        tipx = 24 + i * 5
        tipy = 14 - i * 3
        pygame.draw.polygon(w, _C5_WINGD,
                            [(x0, y0 + 1), (tipx + 1, tipy + 1),
                             (tipx - 3, tipy + 6)])
        pygame.draw.polygon(w, _C5_WING,
                            [(x0, y0), (tipx, tipy), (tipx - 4, tipy + 5)])
    pygame.draw.line(w, _C5_WINGH, (10, 14), (33, 5), 1)
    if scale != 1.0:
        sz = (max(1, int(42 * scale)), max(1, int(34 * scale)))
        w = pygame.transform.smoothscale(w, sz)
    out = pygame.transform.rotate(w, angle_deg)
    if sgn < 0:
        out = pygame.transform.flip(out, True, False)
    return out


def build_toaster_v5(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)
    spread = (f - 0.5) * 32
    bob = int((f - 0.5) * 5)

    _rot_blit(surf, _steel_wing(16 + spread, +1), (BCX + 18, BCY - 5))

    # Two toast slices.
    _toast(surf, BCX - 6, TOP_Y - 8 - bob, 13, 15, gold=_C5_GOLD,
           gold_d=_C5_GLDD, gold_h=_C5_GLDH, crust=_C5_CRST)
    _toast(surf, BCX + 8, TOP_Y - 6 + bob, 13, 15, gold=_C5_GOLD,
           gold_d=_C5_GLDD, gold_h=_C5_GLDH, crust=_C5_CRST)

    # Matte-black body with a chrome base rail.
    _chrome_body(surf, BCX, BCY, 18, 15, base=_C5_BLK, dark=_C5_BLKD,
                 light=_C5_BLKH, top_hi=_C5_BLKH, corner=5)
    # Chrome top cap + base rail give the two-tone black/chrome read.
    pygame.draw.rect(surf, _C5_CHRM, (BCX - 17, BCY + 9, 34, 5),
                     border_radius=2)
    pygame.draw.rect(surf, _C5_CHRD, (BCX - 17, BCY + 9, 34, 5), 1,
                     border_radius=2)
    pygame.draw.line(surf, _C5_CHRH, (BCX - 15, BCY + 10), (BCX + 15, BCY + 10), 1)

    # Glowing slot — a hot orange element line under the dark slot mouth.
    pygame.draw.rect(surf, _C5_CHRD, (BCX - 15, TOP_Y - 1, 30, 6),
                     border_radius=2)
    pygame.draw.rect(surf, (24, 24, 28), (BCX - 13, TOP_Y, 26, 4),
                     border_radius=1)
    pygame.draw.line(surf, _C5_GLOW, (BCX - 12, TOP_Y + 2), (BCX + 12, TOP_Y + 2), 2)
    pygame.draw.line(surf, _C5_CHRH, (BCX - 14, TOP_Y - 1), (BCX + 14, TOP_Y - 1), 1)

    # Minimal chrome lever + a thin LED dial.
    pygame.draw.line(surf, _C5_CHRD, (BCX + 18, BCY - 3), (BCX + 22, BCY - 3), 3)
    pygame.draw.circle(surf, _C5_CHRM, (BCX + 23, BCY - 3), 3)
    pygame.draw.circle(surf, _C5_GLOW, (BCX - 8, BCY + 5), 2)
    pygame.draw.circle(surf, _C5_CHRD, (BCX - 8, BCY + 5), 3, 1)

    # Chrome feet.
    for fx in (BCX - 11, BCX + 11):
        pygame.draw.rect(surf, _C5_CHRD, (fx - 2, BCY + 14, 4, 4),
                         border_radius=1)

    _rot_blit(surf, _steel_wing(-12 - spread, -1), (BCX - 16, BCY))
    return surf


get_toaster_v5 = _make_prebuilt_skin(build_toaster_v5)


# ─────────────────────────────────────────────────────────────────────────────
# Round-1 candidate registry (label → getter). Production lift uses only the
# winning build under the key "skin_toaster".
# ─────────────────────────────────────────────────────────────────────────────
BUILDERS = {
    "v1 · After Dark Classic (chrome)": get_toaster_v1,
    "v2 · Cream Retro Diner (face)":    get_toaster_v2,
    "v3 · Copper Steampunk (1 toast)":  get_toaster_v3,
    "v4 · Mint Kawaii (face)":          get_toaster_v4,
    "v5 · Noir Chrome (modern)":        get_toaster_v5,
}
