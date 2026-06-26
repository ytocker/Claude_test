"""HIKER CANTEEN — vintage scout field-flask parcel cosmetic.

A flattened canvas-OLIVE field canteen carried below Pip. The IDENTITY is the
SILHOUETTE: a wide, squat DISC body (wider than tall — a canteen, never a ball)
sitting under a clearly proud steel NECK and a flat steel screw CAP, with a
leather carry-LOOP arcing OVER the top. "Thing on a stalk above a round body,
hung from a top loop" reads as a canteen at a glance — the cap proud on a neck
and the loop breaking the circle above are what stop the old version reading as
a hand grenade.

22px read tradeoffs (WHY): a real canteen carries stitching, ridges and buckles
that all dissolve at this size, so the body is reduced to ONE bold olive disc
with a single dark stitched SEAM just inside the rim — anything more muddies the
disc under the rotozoom. The body is drawn WIDER than tall (a flattened canteen)
so it never reads as a generic ball and stays distinct from the round coconut
sibling. The cap is a flat WIDE steel disc on a visible neck step (not a knob)
so the metal accent + neck gap survive even banked to 90deg, and the carry-loop
is an arc OVER the cap (not a side ring) because a loop above the silhouette is
the single strongest canteen cue and a loop beside the body reads as a grenade
lever. No rivet — a metal pin on the side reads as a grenade pin. Built on a
44px work surface then smoothscaled to 22 so rim, seam, neck step and loop
antialias cleanly. A baked dark OUTLINE (inflated, drawn first) carries the
shape on bright DAY sky; a warm keyline rim inside is the NIGHT lifeline;
everything is held off the surface edges so the rotozoom never clips the loop.
"""
import pygame

# Tight palette: warm yellow-khaki canvas (vintage scout, not military
# ordnance) with a darker shade for the lower volume, a cool steel cap/neck
# (the grayscale-safe metal accent against the warm olive), a dark leather
# carry strap, a dark outline for day, and a warm keyline for night.
OLIVE = (138, 146,  78)        # warm canvas-khaki body (upper, lit)
OLIVE_SH = ( 96, 102,  52)     # khaki shade — lower body volume
SEAM = ( 78,  82,  44)         # stitched seam just inside the rim
STEEL = (176, 184, 194)        # steel screw cap + neck
STEEL_HI = (220, 226, 234)     # cap top highlight
STEEL_SH = (118, 126, 138)     # cap groove / underside
STRAP = ( 78,  60,  40)        # leather carry strap (over the top)
BUCKLE = (188, 168, 120)       # tiny brass buckle dot on the strap
OUTLINE = ( 40,  44,  26)      # dark, high-value: reads on bright day sky
KEYLINE = (200, 208, 150)      # warm khaki rim — the NIGHT lifeline


def build(mode="normal") -> pygame.Surface:
    # Mode-agnostic: one static canteen sprite for every Pip skin.
    S = 44
    surf = pygame.Surface((S, S), pygame.SRCALPHA)
    cx = S // 2

    # Body: a flat DISC, decidedly wider than tall, so the canteen profile is
    # unmistakable even when banked. Dropped low to leave clear room for the
    # neck step, cap and the carry-loop above, all held off the edges.
    BW, BH = 31, 22               # flattened ellipse: wider-than-tall canteen
    body_cy = 30
    body_rect = pygame.Rect(cx - BW // 2, body_cy - BH // 2, BW, BH)

    # Neck: a PROUD steel step — a 3px gap of steel between the olive rim and
    # the cap so the cap clearly sits on a bottle-neck stalk (the anti-grenade
    # cue). Tapers narrower toward the top (~9 -> 7).
    NW_BOT, NW_TOP, NH = 9, 7, 6
    neck_top = body_rect.top - NH + 1
    neck_poly = [
        (cx - NW_BOT // 2, body_rect.top),
        (cx + NW_BOT // 2, body_rect.top),
        (cx + NW_TOP // 2, neck_top),
        (cx - NW_TOP // 2, neck_top),
    ]

    # Cap: a flat WIDE steel screw lid spanning most of the neck shoulder, with
    # a hard flat top edge — a disc lid, not a knob/fuze.
    CW, CH = 17, 6
    cap_rect = pygame.Rect(cx - CW // 2, neck_top - CH + 1, CW, CH)

    # Carry-LOOP: a leather strap arc OVER the cap, anchored on the two cap
    # shoulders, breaking the circle above the silhouette — the strongest
    # canteen cue and the thing that separates it from a grenade.
    import math
    loop_l = (cap_rect.left + 2, cap_rect.top)
    loop_r = (cap_rect.right - 3, cap_rect.top)
    loop_apex_y = cap_rect.top - 8

    def _strap_arc(color, width):
        # A round carry-loop: the top half of an ellipse spanning the cap
        # shoulders, rising to an apex above the cap with an OPEN underside so
        # the hole reads as a loop you'd clip onto a pack — not a tall cap.
        cxl = (loop_l[0] + loop_r[0]) / 2
        rx = (loop_r[0] - loop_l[0]) / 2
        ry = loop_l[1] - loop_apex_y
        steps = 16
        pts = []
        for i in range(steps + 1):
            # 180deg -> 0deg sweeps left shoulder up over the apex to the right.
            a = math.pi - math.pi * (i / steps)
            pts.append((cxl + rx * math.cos(a), loop_l[1] - ry * math.sin(a)))
        pygame.draw.lines(surf, color, False, pts, width)

    # --- Baked dark OUTLINE (drawn first, slightly inflated) for the DAY read.
    pygame.draw.ellipse(surf, OUTLINE, body_rect.inflate(4, 4))
    pygame.draw.polygon(surf, OUTLINE, [
        (neck_poly[0][0] - 2, neck_poly[0][1]),
        (neck_poly[1][0] + 2, neck_poly[1][1]),
        (neck_poly[2][0] + 2, neck_poly[2][1] - 1),
        (neck_poly[3][0] - 2, neck_poly[3][1] - 1),
    ])
    pygame.draw.rect(surf, OUTLINE, cap_rect.inflate(4, 4), border_radius=2)
    _strap_arc(OUTLINE, 6)

    # --- Carry-LOOP body: leather arc over the cap (drawn over its outline).
    _strap_arc(STRAP, 3)
    # Tiny brass buckle dot where the strap meets the right cap shoulder — the
    # only hardware accent, ON the strap (not a side rivet that would read as a
    # grenade pin).
    pygame.draw.circle(surf, BUCKLE, (loop_r[0], loop_r[1]), 1)

    # --- BODY: olive disc with a vertical shade so it reads as a round volume.
    body = pygame.Surface((body_rect.w, body_rect.h), pygame.SRCALPHA)
    for y in range(body_rect.h):
        t = y / max(1, body_rect.h - 1)
        c = (
            int(OLIVE[0] + (OLIVE_SH[0] - OLIVE[0]) * t),
            int(OLIVE[1] + (OLIVE_SH[1] - OLIVE[1]) * t),
            int(OLIVE[2] + (OLIVE_SH[2] - OLIVE[2]) * t),
        )
        body.fill(c + (255,), pygame.Rect(0, y, body_rect.w, 1))
    mask = pygame.Surface((body_rect.w, body_rect.h), pygame.SRCALPHA)
    pygame.draw.ellipse(mask, (255, 255, 255, 255), mask.get_rect())
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(body, body_rect.topleft)

    # --- Stitched SEAM: one dark ring just inside the rim — the canvas-canteen
    # cue. A single inset ellipse, no more, so the disc stays clean at 22px.
    seam_rect = body_rect.inflate(-7, -6)
    pygame.draw.ellipse(surf, SEAM, seam_rect, width=1)

    # --- Soft top-left sheen on the disc so it reads as a curved canvas volume.
    pygame.draw.ellipse(surf, OLIVE,
                        pygame.Rect(body_rect.x + 4, body_rect.y + 3, 10, 6))

    # --- NECK fill (steel, the proud step between body and cap).
    pygame.draw.polygon(surf, STEEL, neck_poly)
    # Dark groove where the neck meets the body rim — sells the neck step.
    pygame.draw.line(surf, OUTLINE,
                     (cx - NW_BOT // 2, body_rect.top),
                     (cx + NW_BOT // 2, body_rect.top), 1)

    # --- CAP: flat WIDE steel screw lid — a hard flat top edge + a dark groove
    # at the cap/neck join so it reads as a screw-on lid, not a knob.
    pygame.draw.rect(surf, STEEL, cap_rect, border_radius=1)
    pygame.draw.line(surf, STEEL_HI,
                     (cap_rect.x + 2, cap_rect.y + 1),
                     (cap_rect.right - 3, cap_rect.y + 1), 1)
    pygame.draw.line(surf, STEEL_SH,
                     (cap_rect.x + 1, cap_rect.bottom - 1),
                     (cap_rect.right - 2, cap_rect.bottom - 1), 1)
    # Hard cap/neck groove — a dark line so the lid screws on.
    pygame.draw.line(surf, OUTLINE,
                     (cap_rect.x, cap_rect.bottom),
                     (cap_rect.right - 1, cap_rect.bottom), 1)

    # --- Warm keyline rim INSIDE the outline — the NIGHT lifeline that glows on
    # dark sky while staying subtle on day. Traces the disc + cap.
    pygame.draw.ellipse(surf, KEYLINE, body_rect, width=1)
    pygame.draw.rect(surf, KEYLINE, cap_rect, width=1, border_radius=1)

    return pygame.transform.smoothscale(surf, (22, 22))
