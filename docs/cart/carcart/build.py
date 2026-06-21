"""KIDDIE CAR-CART concept — the grocery-store "race car" cart that kids drive.

Identity: a chunky toy CAR body (bubble cabin + long low hood) low to the
ground on two FAT wheels, with a small steel BASKET box riding high at the
rear. Two stacked masses — car in front low, basket behind high — gives a
profile no tall open trolley can mimic. The car nose reads before "shopping",
which is the whole charm.

NO wings, NO live particles. The 4-frame tell is BOUNCING ON SPRINGS: the
whole car body squashes ~2px and rebounds across the four poses (a kid
bouncing the toy), and a tiny round headlight blinks ON at the bottom of the
squash. The read survives grayscale because it lives in the silhouette
deformation, not in colour.

Contract mirrors game/animal_ufo.py: 64x84 SRCALPHA canvas; dominant mass
centred at (BCX,BCY)=(32,44); a 14px collision circle at (32,44); wheels may
extend beyond the body but the car body stays centred. `build(wing_angle_deg)`
returns one flat upright frame (velocity tilt is applied later — bake none).
"""
import pygame

from game.parrot import _aaellipse


# ── canvas + anchors (mirror animal_ufo.py) ──────────────────────────────────
COMPOSITE_W = 64
COMPOSITE_H = 84
DY = 12
BCX, BCY = 32, 32 + DY          # dominant mass centre → (32, 44)


# ── palette ──────────────────────────────────────────────────────────────────
# Candy-red car body is the day hero; cabin glass + wheel keyline carry night.
CAR_RED      = (226, 59, 59)        # #E23B3B candy-red body
CAR_RED_D    = (156, 36, 36)        # #9C2424 shaded lower body / hood
CAR_RED_HI   = (255, 132, 122)      # warm top-edge sheen on the body
CABIN_GLASS  = (191, 228, 242)      # #BFE4F2 bubble-cabin glass
CABIN_GLASS_D= (132, 186, 210)      # lower cabin glass (shaded)
CABIN_GLINT  = (245, 252, 255)      # bright glass specular (carries at night)
BASKET_STEEL = (159, 176, 190)      # #9FB0BE basket box
BASKET_STEEL_D=(108, 126, 142)      # basket shade / underside
BASKET_HI    = (214, 226, 234)      # basket top rail keyline
WHEEL_DARK   = (43, 49, 56)         # #2B3138 tyre
WHEEL_KEY    = (244, 246, 248)      # #F4F6F8 rim keyline (carries both skies)
HUB_RED      = (226, 59, 59)        # toy hubcap centre (echoes the body red)
HEAD_OFF     = (120, 96, 40)        # headlight when unlit (dim amber bulb)
HEAD_ON      = (255, 226, 120)      # headlight blink (lit on the squash)
HEAD_ON_HOT  = (255, 250, 230)      # hot core of the lit headlight
TRIM_DARK    = (70, 30, 30)         # dark seam between car and basket


def _make_prebuilt_skin(build_fn):
    """Local copy of the production getter so this concept stays standalone."""
    from game.parrot import _WING_ANGLES, _add_outline
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


def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _phase(angle_deg):
    """_WING_ANGLES runs 50→20→-10→-40. Map to a 0..3 bounce phase so the
    squash-and-stretch cycles once per wing loop."""
    return int(round((50 - angle_deg) / 30.0)) % 4


# The bounce: a kid pushing the toy down on its springs and rebounding.
#   phase 0  → neutral ride height
#   phase 1  → SQUASH (body 2px shorter + wider, sits lower) → headlight BLINKS
#   phase 2  → neutral
#   phase 3  → STRETCH (body 2px taller + narrower, lifts up)
# Each entry: (vertical squash px, horizontal stretch px, body drop px, lit?)
_BOUNCE = {
    0: (0,  0, 0, False),
    1: (2,  2, 2, True),
    2: (0,  0, 0, False),
    3: (-2, -1, -1, False),
}


def _rounded_rect(surf, color, rect, radius):
    pygame.draw.rect(surf, color, rect, border_radius=radius)


def build(wing_angle_deg):
    """One upright KIDDIE CAR-CART frame on the 64x84 canvas.

    Draw order back→front so the silhouette layers cleanly: basket (rear,
    high) → car body squash mass (front, low) → bubble cabin → wheels (fat,
    sit on the ground line) → headlight blink. The whole car+cabin mass
    deforms with the bounce so the tell survives grayscale."""
    surf = _new()
    ph = _phase(wing_angle_deg)
    sq_v, st_h, drop, lit = _BOUNCE[ph]

    # Ground line the wheels sit on — fixed, so the bounce reads against it.
    ground_y = BCY + 17

    # ── REAR BASKET (steel box riding HIGH at the back) ──────────────────────
    # A small rectangular box, tapered like a real wire basket (wider at top),
    # sitting up and behind the car. It does NOT bounce as hard as the car —
    # half the drop — so the two stacked masses read as separate.
    b_drop = drop // 2
    bx = BCX + 6                       # basket centred to the rear-right
    b_top = BCY - 16 + b_drop
    b_bot = BCY + 4 + b_drop
    b_top_w, b_bot_w = 18, 14          # tapered: wider rim than floor
    basket_pts = [
        (bx - b_top_w, b_top), (bx + b_top_w, b_top),
        (bx + b_bot_w, b_bot), (bx - b_bot_w, b_bot),
    ]
    pygame.draw.polygon(surf, BASKET_STEEL, basket_pts)
    # shaded lower half of the box for volume
    pygame.draw.polygon(surf, BASKET_STEEL_D, [
        (bx - b_bot_w - 1, b_bot - 6), (bx + b_bot_w + 1, b_bot - 6),
        (bx + b_bot_w, b_bot), (bx - b_bot_w, b_bot),
    ])
    # wire-mesh hint: two vertical + one horizontal seam (cheap, reads at 40px)
    for fx in (-9, 0, 9):
        pygame.draw.line(surf, BASKET_STEEL_D,
                         (bx + fx, b_top + 2), (bx + int(fx * 0.78), b_bot - 1), 1)
    pygame.draw.line(surf, BASKET_STEEL_D,
                     (bx - b_top_w + 2, (b_top + b_bot) // 2),
                     (bx + b_top_w - 2, (b_top + b_bot) // 2), 1)
    # bright top rail keyline — holds the basket rim against a dark night sky
    pygame.draw.line(surf, BASKET_HI,
                     (bx - b_top_w, b_top), (bx + b_top_w, b_top), 2)
    # a short handle bar poking up off the back rail (the "you push here" tell)
    pygame.draw.line(surf, BASKET_STEEL_D,
                     (bx + b_top_w - 1, b_top + 1), (bx + b_top_w + 4, b_top - 4), 3)
    pygame.draw.line(surf, BASKET_HI,
                     (bx + b_top_w - 1, b_top), (bx + b_top_w + 4, b_top - 5), 1)

    # ── CAR BODY (long low hood + tail, FRONT and LOW) ───────────────────────
    # The dominant mass, centred at (BCX,BCY). It carries the full bounce: a
    # squash widens + shortens it and drops it toward the ground.
    cx = BCX - 6                       # car pushed forward (left = nose)
    body_cy = BCY + 4 + drop
    half_w = 24 + st_h                 # long body; stretches wider on squash
    half_h = 9 - sq_v                  # low body; flattens on squash
    nose_x = cx - half_w               # front bumper (left)
    tail_x = cx + half_w - 4           # rear, tucks under the basket

    # Long rounded car body — a capsule-ish hull: low, wide, rounded ends.
    body_rect = pygame.Rect(nose_x, body_cy - half_h, (tail_x - nose_x), half_h * 2)
    _rounded_rect(surf, CAR_RED, body_rect, half_h)
    # Hood/lower shade — the bottom third in the darker red for a chunky toy look.
    shade_rect = pygame.Rect(nose_x + 1, body_cy + half_h - 6,
                             (tail_x - nose_x) - 2, 6)
    _rounded_rect(surf, CAR_RED_D, shade_rect, 3)
    # Raised hood scoop at the nose (front of the toy car) — a small red bump.
    _aaellipse(surf, CAR_RED, (nose_x + 8, body_cy - half_h + 1), 8, 5)
    # warm top-edge sheen (a stripe of highlight along the upper hull)
    pygame.draw.line(surf, CAR_RED_HI,
                     (nose_x + 6, body_cy - half_h + 1),
                     (tail_x - 6, body_cy - half_h + 1), 2)
    # front bumper keyline so the nose reads as a hard chrome lip
    pygame.draw.line(surf, WHEEL_KEY,
                     (nose_x + 1, body_cy - 2), (nose_x + 1, body_cy + 4), 2)
    # dark seam where the car body meets the basket behind it
    pygame.draw.line(surf, TRIM_DARK,
                     (cx + half_w - 8, body_cy - half_h),
                     (cx + half_w - 8, body_cy + half_h), 2)

    # ── BUBBLE CABIN (rounded glass dome over the front of the car) ───────────
    # A clear half-bubble windshield — the "kid sits here" read. It rides on
    # the squashing body, so it dips and rises with the bounce.
    cab_cx = cx - 5
    cab_cy = body_cy - half_h - 2
    cab_rx, cab_ry = 12, 9 - sq_v       # cabin flattens slightly on squash too
    # red cabin frame (a thin red ring under the glass) for the toy-car pillar
    _aaellipse(surf, CAR_RED_D, (cab_cx, cab_cy + 1), cab_rx + 1, cab_ry + 1)
    _aaellipse(surf, CABIN_GLASS, (cab_cx, cab_cy), cab_rx, cab_ry)
    # lower glass shade gives the bubble volume
    _aaellipse(surf, CABIN_GLASS_D, (cab_cx, cab_cy + 3), cab_rx - 2, cab_ry - 3)
    # red roof cap across the top of the bubble (so it's clearly a CAR cabin)
    pygame.draw.arc(surf, CAR_RED,
                    pygame.Rect(cab_cx - cab_rx, cab_cy - cab_ry,
                                cab_rx * 2, cab_ry * 2),
                    0.5, 2.64, 3)
    # bright specular glint high-left on the glass — the night carry highlight
    _aaellipse(surf, CABIN_GLINT, (cab_cx - 4, cab_cy - 3), 3, 2)
    pygame.draw.circle(surf, CABIN_GLINT, (cab_cx + 3, cab_cy + 1), 1)
    # cabin keyline rim across the top so the bubble survives a bright day sky
    pygame.draw.arc(surf, WHEEL_KEY,
                    pygame.Rect(cab_cx - cab_rx, cab_cy - cab_ry,
                                cab_rx * 2, cab_ry * 2),
                    0.6, 2.55, 1)

    # ── FAT WHEELS (two chunky toy wheels on the ground line) ─────────────────
    # Big, low, with a bright keyline rim and a red hubcap — the toy-car read.
    # They sit on the fixed ground_y, so when the body squashes DOWN toward
    # them, the springs read as compressed.
    wheel_r = 9
    front_wx = nose_x + 9
    rear_wx = cx + half_w - 9
    for wx in (front_wx, rear_wx):
        # tyre
        pygame.draw.circle(surf, WHEEL_DARK, (wx, ground_y), wheel_r)
        # bright outer keyline rim (carries on both skies + grayscale)
        pygame.draw.circle(surf, WHEEL_KEY, (wx, ground_y), wheel_r, 2)
        # red toy hubcap + a white pin so the wheel reads as a spinning toy rim
        pygame.draw.circle(surf, HUB_RED, (wx, ground_y), 4)
        pygame.draw.circle(surf, WHEEL_KEY, (wx, ground_y), 4, 1)
        pygame.draw.circle(surf, WHEEL_KEY, (wx, ground_y - 1), 1)
        # tiny wheel-arch shadow tucked under the body
        pygame.draw.arc(surf, CAR_RED_D,
                        pygame.Rect(wx - wheel_r - 1, ground_y - wheel_r - 4,
                                    (wheel_r + 1) * 2, (wheel_r + 1) * 2),
                        0.4, 2.74, 2)

    # ── HEADLIGHT (blinks ON at the bottom of the squash) ─────────────────────
    # A tiny round bulb on the front bumper. Off = a dim amber dot; on = a hot
    # blink with a soft additive halo (blooms most at night). The blink lands
    # on the squash so "down-bounce → flash" reads as one beat.
    hl = (nose_x + 3, body_cy)
    if lit:
        halo = pygame.Surface((16, 16), pygame.SRCALPHA)
        for i, a in ((6, 70), (4, 110), (2, 180)):
            pygame.draw.circle(halo, (*HEAD_ON, a), (8, 8), i)
        surf.blit(halo, (hl[0] - 8, hl[1] - 8), special_flags=pygame.BLEND_RGBA_ADD)
        pygame.draw.circle(surf, HEAD_ON, hl, 3)
        pygame.draw.circle(surf, HEAD_ON_HOT, hl, 2)
    else:
        pygame.draw.circle(surf, HEAD_OFF, hl, 3)
        pygame.draw.circle(surf, WHEEL_KEY, hl, 3, 1)

    return surf


# ── canonical getter + registry (mirrors animal_ufo.py) ───────────────────────
get_carcart = _make_prebuilt_skin(build)

BUILDERS = {"skin_carcart": get_carcart}
