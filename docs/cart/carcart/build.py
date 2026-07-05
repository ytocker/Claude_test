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
# Candy-red car body is the unambiguous day+night hero. The rear basket is a
# small OPEN-TOPPED carry box kept inside the car's warm colour family (a
# desaturated terracotta, NOT grey) so it stays subordinate to the red but
# never reads as a foreign cargo block — and so it separates cleanly from
# Pip's cool-brown parcel below.
CAR_RED      = (230, 58, 58)        # #E63A3A candy-red body (a touch hotter)
CAR_RED_D    = (156, 36, 36)        # #9C2424 shaded lower body / hood
CAR_RED_HI   = (255, 138, 126)      # warm top-edge sheen on the body
CABIN_GLASS  = (191, 228, 242)      # #BFE4F2 bubble-cabin glass
CABIN_GLASS_D= (132, 186, 210)      # lower cabin glass (shaded)
CABIN_GLINT  = (250, 254, 255)      # bright glass specular (carries at night)
# Terracotta basket: in the red family but desaturated + dimmer so it recedes
# behind the candy-red hero. The OPEN interior is a lighter warm tone so the
# basket reads as a hollow container, not a solid slab; bold staves + a bright
# top rail keyline are the parts that actually survive at 40px.
# One value-step darker than the r3 #B0604A wall: against the bright DAY sky
# this tightens "red leads" so the rear recedes a touch further behind the
# candy-red hero, while staying in the same terracotta hue. On the dark NIGHT
# sky the step is negligible (the rear already read correctly there), so the
# single shared sprite honours the day-only nudge without a per-sky build.
BASKET_BODY  = (162, 86, 66)        # #A25642 terracotta basket wall (warm-red)
BASKET_BODY_D=(126, 64, 50)         # #7E4032 basket shade / floor (dark warm)
BASKET_IN    = (214, 160, 138)      # #D6A08A bright OPEN interior (says hollow)
BASKET_STAVE = (110, 54, 42)        # bold vertical staves (survive at 40px)
BASKET_HI    = (250, 224, 206)      # warm top-rail keyline arcing over the mouth
WHEEL_DARK   = (43, 49, 56)         # #2B3138 tyre
WHEEL_KEY    = (248, 250, 252)      # rim keyline (carries both skies, hot at night)
HUB_RED      = (230, 58, 58)        # toy hubcap centre (echoes the body red)
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


# The bounce: a kid pushing the toy down on its springs and rebounding. The
# whole CAR body travels vertically against a FIXED ground gap, so the read is
# a clear 4-beat compress→rebound — not a wobble. The bounce now lives almost
# entirely in VERTICAL travel (+4 drop / −3 lift) so the toy-car SILHOUETTE
# survives every frame; HULL-WIDTH squash is capped at +2px (was +4) so the
# cabin bubble never crushes out of shape. A small WHEEL-SPREAD on the squash
# carries the "compressed springs" beat instead of crushing the hull. The
# basket rides at a FIXED height (it does NOT swing) so its mass never reads as
# wobble.
#   phase 0  → neutral ride height
#   phase 1  → SQUASH  (body sits LOW into the springs, wheels spread) → blink
#   phase 2  → neutral (rebounding up through ride height)
#   phase 3  → STRETCH (body taller + a hair narrower, LIFTS off the ground)
# Each entry:
#   (vertical squash px, horizontal stretch px, body drop px, wheel spread px, lit?)
_BOUNCE = {
    0: (0,   0,  0, 0, False),
    1: (3,   2,  4, 2, True),
    2: (0,   0,  0, 0, False),
    3: (-2, -1, -3, 0, False),
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
    sq_v, st_h, drop, spread, lit = _BOUNCE[ph]

    # Ground line the wheels sit on — fixed, so the bounce reads against it.
    ground_y = BCY + 17

    # ── REAR BASKET (small OPEN-TOPPED carry box behind the cabin) ────────────
    # At 40px fine weave blurs into a warm BUNDLE/SACK, so the rear leans on the
    # ONE cue that survives downscale: a clear open MOUTH. The top edge is a
    # concave ELLIPSE — a dark interior-shadow rim along the back lip with a
    # lighter interior pocket dropping below it — so the eye reads DOWN INTO the
    # box. Two bold FRONT-face staves + a silhouette rim-lip overhang carry the
    # "basket, not sack" read; interior detail is deliberately minimal. It rides
    # at a FIXED height (no swing) so its mass never reads as wobble, and its
    # desaturated terracotta keeps it subordinate to the candy-red hero while
    # separating from Pip's parcel.
    bx = BCX + 8                       # basket tucked to the rear-right
    b_top = BCY - 11                   # rim of the open mouth
    b_bot = BCY + 2                    # short box (secondary, smaller)
    b_top_w, b_bot_w = 11, 9           # gentle taper (real basket walls)
    basket_pts = [
        (bx - b_top_w, b_top), (bx + b_top_w, b_top),
        (bx + b_bot_w, b_bot), (bx - b_bot_w, b_bot),
    ]
    # outer wall (front-facing terracotta)
    pygame.draw.polygon(surf, BASKET_BODY, basket_pts)
    # OPEN MOUTH — the single change that flips bundle→basket. The interior
    # pocket is a lighter warm ellipse dropped BELOW a dark back-lip shadow rim,
    # so the rim reads as a concave opening the eye looks down into, not a domed
    # top. Drawn dark-rim-first then the bright pocket nested inside it.
    mouth_cy = b_top + 3               # pocket sits below the back lip
    mouth_rx = b_top_w - 2
    # dark interior-shadow rim hugging the BACK lip (the far wall in shadow)
    _aaellipse(surf, BASKET_BODY_D, (bx, b_top + 1), mouth_rx, 3)
    # lighter interior pocket dropping below the rim → "look down into the box"
    _aaellipse(surf, BASKET_IN, (bx, mouth_cy), mouth_rx - 1, 3)
    # dark floor crescent so the pocket bottoms out in shadow (depth read)
    _aaellipse(surf, BASKET_BODY_D, (bx, mouth_cy + 2), mouth_rx - 2, 2)
    # TWO bold FRONT-face staves — 2px, full-height, on the front wall where
    # they catch the most pixels and hold high contrast against the terracotta.
    # Two (not three) stays legible across the ~10px curve instead of becoming
    # noise. They start BELOW the open mouth so they don't fill the pocket.
    for fx in (-5, 5):
        x0 = bx + fx
        x1 = bx + int(fx * 0.78)
        pygame.draw.line(surf, BASKET_STAVE, (x0, mouth_cy + 2), (x1, b_bot - 1), 2)
    # BRIGHT front-lip keyline along the near rim — the bright edge of the mouth
    # that the eye reads as the front wall of the opening (not a flat lid).
    pygame.draw.line(surf, BASKET_HI,
                     (bx - b_top_w, b_top + 1), (bx + b_top_w, b_top + 1), 2)
    # SILHOUETTE NOTCH — a 2px dark rim-lip overhang where the back wall meets the
    # arc-rail, breaking the smooth top-back corner so the OUTLINE itself carries
    # the basket read (silhouette cues survive scale; interior cues don't).
    pygame.draw.line(surf, TRIM_DARK,
                     (bx + b_top_w - 1, b_top - 2), (bx + b_top_w + 1, b_top), 2)
    pygame.draw.line(surf, TRIM_DARK,
                     (bx + b_top_w - 1, b_top), (bx + b_top_w - 1, b_top + 3), 2)
    # a short handle nub off the back rail at a FIXED angle (no swing → no fake
    # wobble); just enough to say "push here" in the car's warm family.
    pygame.draw.line(surf, BASKET_STAVE,
                     (bx + b_top_w - 1, b_top), (bx + b_top_w + 3, b_top - 4), 2)
    pygame.draw.line(surf, BASKET_HI,
                     (bx + b_top_w - 1, b_top - 1), (bx + b_top_w + 3, b_top - 5), 1)

    # ── CAR BODY (long low hood + tail, FRONT and LOW) ───────────────────────
    # The dominant mass, centred at (BCX,BCY). It carries the full bounce: a
    # squash widens + shortens it and drops it toward the ground. Lifted a hair
    # vs r1 so a clean unbroken lower-centre RED shelf sits above Pip's parcel.
    cx = BCX - 6                       # car pushed forward (left = nose)
    body_cy = BCY + 2 + drop           # lifted 2px → leaves room for the parcel
    half_w = 24 + st_h                 # long body; width squash capped at +2px
    half_h = 9 - sq_v                  # low body; flattens slightly on squash
    nose_x = cx - half_w               # front bumper (left)
    tail_x = cx + half_w - 4           # rear, tucks under the basket

    # Long rounded car body — a capsule-ish hull: low, wide, rounded ends.
    body_rect = pygame.Rect(nose_x, body_cy - half_h, (tail_x - nose_x), half_h * 2)
    _rounded_rect(surf, CAR_RED, body_rect, half_h)
    # CLEAN lower-centre RED shelf: a solid red band runs the full width of the
    # hull's underside in candy-red (NOT a dark shade) so the parcel composited
    # just below reads as distinct cargo UNDER an unbroken red car, never fused.
    shelf_rect = pygame.Rect(nose_x + 2, body_cy + half_h - 5,
                             (tail_x - nose_x) - 4, 5)
    _rounded_rect(surf, CAR_RED, shelf_rect, 2)
    # a thin darker hairline ABOVE the shelf for a chunky-toy lower edge — kept
    # off the very bottom so the shelf's silhouette stays a solid red block.
    pygame.draw.line(surf, CAR_RED_D,
                     (nose_x + 4, body_cy + half_h - 5),
                     (tail_x - 5, body_cy + half_h - 5), 1)
    # Raised hood scoop at the nose (front of the toy car) — a small red bump.
    _aaellipse(surf, CAR_RED, (nose_x + 8, body_cy - half_h + 1), 8, 5)
    # warm top-edge sheen (a stripe of highlight along the upper hull)
    pygame.draw.line(surf, CAR_RED_HI,
                     (nose_x + 6, body_cy - half_h + 1),
                     (tail_x - 6, body_cy - half_h + 1), 2)
    # front bumper keyline so the nose reads as a hard chrome lip
    pygame.draw.line(surf, WHEEL_KEY,
                     (nose_x + 1, body_cy - 2), (nose_x + 1, body_cy + 4), 2)
    # short dark seam where the car body meets the basket — kept high on the
    # hull so it does NOT break the lower-centre red shelf.
    pygame.draw.line(surf, TRIM_DARK,
                     (cx + half_w - 8, body_cy - half_h),
                     (cx + half_w - 8, body_cy + half_h - 6), 2)

    # ── BUBBLE CABIN (rounded glass dome over the front of the car) ───────────
    # A clear half-bubble windshield — the "kid sits here" read. It rides on
    # the squashing body, so it dips and rises with the bounce.
    cab_cx = cx - 5
    cab_cy = body_cy - half_h - 2
    # PROTECT the bubble: the dome keeps a near-constant radius across all four
    # frames (at most a 1px flatten on the deepest squash) so it never vanishes
    # — the bounce is carried by the body's vertical travel, not by crushing the
    # cabin. Without this the squash frame stopped reading as the same toy car.
    cab_rx, cab_ry = 12, 9 - min(sq_v, 1)
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
    # On the squash beat the wheels SPREAD apart (front forward, rear back) so the
    # "springs compressed, weight settling" beat reads through the stance instead
    # of through a crushed hull.
    front_wx = nose_x + 9 - spread
    rear_wx = cx + half_w - 9 + spread
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
