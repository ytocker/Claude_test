"""WATER BOTTLE — insulated tumbler parcel cosmetic.

A trendy reusable hydro-flask carried upright below Pip. The IDENTITY is the
OPAQUE chunky read: a wide, straight-walled MATTE pastel-teal body (no
see-through water at all), a fat BLACK flip-straw LID capping it, and a small
carry LOOP arching off the top. Those three masses — opaque body / black lid /
loop — are what separate it at a glance from the shipped CLEAR squeeze bottle,
whose tell is a bright internal water line. Here the body is solid colour, so
the contrast is silhouette + the black cap, not a meniscus.

22px read tradeoffs (WHY): the tumbler is wider and squatter than the squeeze
bottle so the chunkier mass reads even before colour, and the body fill is FLAT
matte (one soft vertical shade, no glint streak, no water line) because any
internal detail would just re-read as the clear-bottle water cue we are trying
to avoid. The lid is exaggeratedly tall and BLACK — the grayscale-safe anchor —
sitting as a clearly separate dark cap so body and lid never fuse at the
downscale; a 1px lighter top edge keeps it from looking like a hole. The carry
loop is a thick open arc (drawn as a fat ring minus its lower half) kept small
so it survives rotation as a recognisable handle bump rather than noise. A
single side STICKER dot is the only body detail, placed off-centre so it reads
as a cosmetic sticker and adds asymmetry that helps the eye track the bank.
Drawn on a 44px work surface then smoothscaled to 22 so the loop arc and lid
edges antialias cleanly. A baked dark outline (inflated, drawn first) carries
the shape on bright DAY sky; a cool keyline rim inside is the NIGHT lifeline;
the whole tumbler is held off the surface edges so the gameplay rotozoom never
clips the loop or base.
"""
import math

import pygame

# Tight palette: opaque pastel-teal body with a darker shade for the rounded
# base, a near-black lid (the grayscale-safe anchor + the strongest identity
# cue against the squeeze bottle), a grey loop, and the day/night line colours.
TEAL = ( 92, 201, 192)        # matte pastel-teal body (flat, opaque)
TEAL_SHADE = ( 46, 154, 146)  # darker teal — base + lower-body shading
TEAL_HI = (164, 230, 224)     # soft upper highlight (keeps it from looking dead-flat)
LID = ( 42,  46,  54)         # black flip-straw lid — the eye-magnet / GS anchor
LID_HI = ( 92,  98, 108)      # lid top edge so the cap reads raised, not a hole
LOOP = (106, 114, 126)        # carry loop grey
OUTLINE = ( 21,  48,  46)     # dark, high-value: reads on bright day sky
KEYLINE = (190, 232, 226)     # cool rim — the NIGHT lifeline
STICKER = (244, 246, 250)     # tiny off-centre sticker dot (sole body detail)


def build(mode="normal") -> pygame.Surface:
    # Mode-agnostic: one static tumbler sprite for every Pip skin.
    S = 44
    surf = pygame.Surface((S, S), pygame.SRCALPHA)
    cx = S // 2

    # Tumbler geometry. WIDE straight side walls + squat proportions so the
    # chunky insulated mass reads distinct from the tall thin squeeze bottle.
    # Held off the surface edges so the gameplay rotozoom never clips loop/base.
    BW = 22                       # body width (chunky, wider than the squeeze bottle)
    body_top = 14                 # top of the body wall (just under the lid)
    body_bot = 39                 # rounded base
    body_rect = pygame.Rect(cx - BW // 2, body_top, BW, body_bot - body_top)
    body_rad = 5                  # base corners round; top stays square under the lid

    # Lid: a fat black flip-straw cap, slightly NARROWER than the body so a
    # shoulder step reads. Tall so it stays a clear separate mass when banked.
    LW, LH = 16, 10
    lid_rect = pygame.Rect(cx - LW // 2, body_top - LH + 1, LW, LH)

    # Carry loop: a thick open arc rising off the lid top with daylight between
    # it and the cap, so it reads as a distinct handle rather than fusing with
    # the black lid. Centred above the lid, biased high.
    loop_cx = cx
    loop_r = 6                    # outer radius of the loop arc
    loop_cy = lid_rect.y - 4      # arc centre sits above the lid (opens a gap)

    # --- Baked dark outline (drawn first, slightly inflated) for the DAY read.
    # Loop outline first (a fat dark arc; lid covers nothing of it, gap stays open).
    pygame.draw.arc(surf, OUTLINE,
                    pygame.Rect(loop_cx - loop_r - 1, loop_cy - loop_r - 1,
                                (loop_r + 1) * 2, (loop_r + 1) * 2),
                    math.radians(15), math.radians(165), 5)
    # Outline backing for the two posts so the grey reads on bright day sky.
    pygame.draw.line(surf, OUTLINE, (loop_cx - loop_r + 1, loop_cy),
                     (loop_cx - loop_r + 1, lid_rect.y + 1), 4)
    pygame.draw.line(surf, OUTLINE, (loop_cx + loop_r - 1, loop_cy),
                     (loop_cx + loop_r - 1, lid_rect.y + 1), 4)
    pygame.draw.rect(surf, OUTLINE, lid_rect.inflate(4, 4), border_radius=3)
    pygame.draw.rect(surf, OUTLINE, body_rect.inflate(4, 4),
                     border_radius=body_rad + 2,
                     border_top_left_radius=2, border_top_right_radius=2)

    # --- Carry LOOP: grey open arc with an OPEN gap to the lid so it reads as a
    # handle, not part of the cap. Drawn thick so it survives the downscale.
    pygame.draw.arc(surf, LOOP,
                    pygame.Rect(loop_cx - loop_r, loop_cy - loop_r,
                                loop_r * 2, loop_r * 2),
                    math.radians(18), math.radians(162), 3)
    # Two short grey posts dropping from the arc ends to the lid, so the loop
    # visibly attaches to the cap rather than floating.
    pygame.draw.line(surf, LOOP, (loop_cx - loop_r + 1, loop_cy),
                     (loop_cx - loop_r + 1, lid_rect.y + 1), 2)
    pygame.draw.line(surf, LOOP, (loop_cx + loop_r - 1, loop_cy),
                     (loop_cx + loop_r - 1, lid_rect.y + 1), 2)

    # --- BODY: opaque matte teal on its own alpha surface so the straight-walled
    # base-rounded shape composites cleanly, then blitted in one piece. A gentle
    # top->bottom shade gives volume WITHOUT any water-line / glint that would
    # re-read as the clear squeeze bottle.
    body = pygame.Surface((body_rect.w, body_rect.h), pygame.SRCALPHA)
    for y in range(body_rect.h):
        t = y / max(1, body_rect.h - 1)
        # Highlight near the top, settling into the base shade at the bottom.
        if t < 0.55:
            tt = t / 0.55
            c = (
                int(TEAL_HI[0] + (TEAL[0] - TEAL_HI[0]) * tt),
                int(TEAL_HI[1] + (TEAL[1] - TEAL_HI[1]) * tt),
                int(TEAL_HI[2] + (TEAL[2] - TEAL_HI[2]) * tt),
            )
        else:
            tt = (t - 0.55) / 0.45
            c = (
                int(TEAL[0] + (TEAL_SHADE[0] - TEAL[0]) * tt),
                int(TEAL[1] + (TEAL_SHADE[1] - TEAL[1]) * tt),
                int(TEAL[2] + (TEAL_SHADE[2] - TEAL[2]) * tt),
            )
        body.fill(c + (255,), pygame.Rect(0, y, body_rect.w, 1))
    # Mask to a chunky shape: base corners round, top stays square (lid sits on it).
    mask = pygame.Surface((body_rect.w, body_rect.h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(),
                     border_radius=body_rad, border_top_left_radius=1,
                     border_top_right_radius=1)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(body, body_rect.topleft)

    # --- A soft vertical edge-shade down the right side so the cylinder reads as
    # round, not a flat tile (kept dark/teal, never a bright glint).
    pygame.draw.line(surf, TEAL_SHADE,
                     (body_rect.right - 3, body_rect.y + 3),
                     (body_rect.right - 3, body_rect.bottom - 4), 2)

    # --- Side STICKER: the sole body detail, a small off-centre dot so it reads
    # as a cosmetic sticker and the asymmetry helps track the bank.
    pygame.draw.circle(surf, STICKER,
                       (body_rect.x + 7, body_rect.centery + 1), 2)

    # --- LID: fat black cap. A lighter top edge keeps it reading as a raised
    # flip lid rather than a void, and a hard groove at the lid/body join seats it.
    pygame.draw.rect(surf, LID, lid_rect, border_radius=3)
    pygame.draw.line(surf, LID_HI,
                     (lid_rect.x + 2, lid_rect.y + 1),
                     (lid_rect.right - 3, lid_rect.y + 1), 1)
    # Hard lid/body groove so the lid clearly screws/flips onto the body.
    pygame.draw.line(surf, OUTLINE,
                     (lid_rect.x, lid_rect.bottom - 1),
                     (lid_rect.right - 1, lid_rect.bottom - 1), 1)

    # --- Cool keyline rim INSIDE the outline — the NIGHT lifeline that glows on
    # dark sky while staying subtle on day. Traces the body wall + lid.
    pygame.draw.rect(surf, KEYLINE, body_rect, width=1, border_radius=body_rad,
                     border_top_left_radius=1, border_top_right_radius=1)
    pygame.draw.rect(surf, KEYLINE, lid_rect, width=1, border_radius=3)

    return pygame.transform.smoothscale(surf, (22, 22))
