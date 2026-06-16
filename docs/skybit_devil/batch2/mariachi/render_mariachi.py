"""
Mariachi — the strumming charro skeleton musician (BATCH 2 / Skeletons).

Round-1 concept renderer. Procedural Pygame, house style: chibi proportions,
flat saturated fills + hard ink keylines, form via the
dark-core -> flat-fill -> top-left rim-sheen TRIAD, silhouette POP via a 1px
outline grown from the alpha mask, supersample -> smoothscale.

Sheet shows the creature AND its prop->pillar mirror (guitarron neck) at both
large and 32px scales, plus the PINNED PALETTE swatches.

Run headless:  SDL_VIDEODRIVER=dummy python render_mariachi.py
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame

pygame.init()

# ── PINNED PALETTE (locked brief, exact hexes) ───────────────────────────────
BONE        = (236, 226, 202)   # warm-bone base
BONE_SHADE  = (180, 162, 124)   # tan-bone shade
RUST        = (186,  62,  48)   # rust-red jacket accent
SILVER      = (208, 210, 216)   # silver botonadura button
OCHRE       = (214, 168,  84)   # ochre sombrero
TURQ        = ( 64, 176, 168)   # turquoise rosette
INK         = ( 28,  22,  22)   # keyline ink
SHEEN       = (252, 244, 222)   # top-left rim sheen

# Derived working tones (kept inside the pinned families).
BONE_CORE   = (158, 142, 108)   # dark-core under bone (deeper than tan shade)
OCHRE_CORE  = (158, 120,  52)   # dark-core under sombrero
OCHRE_SHEEN = (244, 210, 140)   # ochre top-left sheen
RUST_CORE   = (122,  38,  30)   # dark-core under jacket rust
RUST_SHEEN  = (224, 110,  86)   # rust top-left sheen
GUITAR_WOOD = (160,  96,  54)   # guitarron rosewood body
GUITAR_CORE = (104,  60,  34)
GUITAR_SHEEN= (206, 150,  96)
SILVER_SHEEN= (242, 244, 248)
SILVER_CORE = (150, 152, 162)

SS = 4   # supersample factor


# ── geometry / triad helpers ─────────────────────────────────────────────────

def _ell(surf, color, cx, cy, rx, ry):
    pygame.draw.ellipse(surf, color,
                        (int(cx - rx), int(cy - ry), int(rx * 2), int(ry * 2)))


def triad_ellipse(surf, cx, cy, rx, ry, core, fill, sheen, outline=INK):
    """dark-core -> flat-fill -> top-left rim-sheen on an ellipse mass, with a
    hard ink keyline. The triad reads as form without any soft gradient."""
    if outline is not None:
        _ell(surf, outline, cx, cy, rx + SS, ry + SS)
    _ell(surf, core, cx, cy, rx, ry)
    _ell(surf, fill, cx, cy, rx - SS * 0.7, ry - SS * 0.7)
    # Top-left rim sheen: a smaller ellipse pushed up-left.
    _ell(surf, sheen, cx - rx * 0.34, cy - ry * 0.36, rx * 0.5, ry * 0.42)


def triad_poly(surf, pts, core, fill, sheen, outline=INK, sheen_pts=None):
    """Triad on an arbitrary polygon: ink keyline (drawn as a fat stroke), core
    fill, inset fill, then an optional top-left sheen sliver polygon."""
    if outline is not None:
        pygame.draw.polygon(surf, outline, pts)
        pygame.draw.polygon(surf, outline, pts, SS * 2)
    pygame.draw.polygon(surf, core, pts)
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    inset = [(p[0] + (cx - p[0]) * 0.16, p[1] + (cy - p[1]) * 0.16) for p in pts]
    pygame.draw.polygon(surf, fill, inset)
    if sheen_pts:
        pygame.draw.polygon(surf, sheen, sheen_pts)


def grow_outline(surf, color=INK, thickness=1):
    """1px (post-scale) outline grown from the alpha mask — the silhouette POP.
    Run at supersample scale so it survives smoothscale."""
    mask = pygame.mask.from_surface(surf)
    outline_pts = mask.outline()
    if len(outline_pts) > 2:
        pygame.draw.lines(surf, color, True, outline_pts, max(1, thickness * SS))


# ── the creature ─────────────────────────────────────────────────────────────

def draw_mariachi(target_size):
    """Strumming charro calaca: vast circular sombrero disc, grinning
    moustachioed skull, rust charro jacket with silver botonadura, bone legs in a
    mid-zapateado kick, fat round guitarron hugged to the chest."""
    S = target_size * SS
    surf = pygame.Surface((S, S), pygame.SRCALPHA)
    cx = S * 0.5

    # Layout anchors (fractions of S).
    hat_y   = S * 0.30
    head_y  = S * 0.345
    body_y  = S * 0.58
    # ── BONE LEGS mid-dance-kick (drawn first so jacket overlaps the hips) ─────
    hip_y = S * 0.66
    # Planted/stomping leg (player-left), and a kicked-out leg (player-right).
    def bone_limb(p0, p1, p2, w):
        for a, b in ((p0, p1), (p1, p2)):
            pygame.draw.line(surf, INK, a, b, int(w + SS * 1.6))
        for a, b in ((p0, p1), (p1, p2)):
            pygame.draw.line(surf, BONE_SHADE, a, b, int(w))
            pygame.draw.line(surf, BONE, a, b, int(w * 0.5))
        # joint knobs
        for p in (p0, p1, p2):
            triad_ellipse(surf, p[0], p[1], w * 0.62, w * 0.62,
                          BONE_CORE, BONE, SHEEN)

    legw = S * 0.052
    # Planted leg: nearly straight, stomping down.
    bone_limb((cx - S * 0.085, hip_y),
              (cx - S * 0.115, S * 0.80),
              (cx - S * 0.10,  S * 0.94), legw)
    # Kicked leg: bent knee, boot swung out to player-right (zapateado).
    bone_limb((cx + S * 0.085, hip_y),
              (cx + S * 0.185, S * 0.80),
              (cx + S * 0.30,  S * 0.85), legw)
    # Little charro boots (rust toe-caps with silver heel-tap).
    for (bx, by), face in (((cx - S * 0.105, S * 0.95), -1),
                            ((cx + S * 0.315, S * 0.86), 1)):
        triad_ellipse(surf, bx + face * S * 0.018, by, S * 0.052, S * 0.034,
                      RUST_CORE, RUST, RUST_SHEEN)

    # ── CHARRO JACKET torso (short bolero jacket, rust-red) ───────────────────
    jacket = [
        (cx - S * 0.14, body_y - S * 0.05),
        (cx + S * 0.14, body_y - S * 0.05),
        (cx + S * 0.155, hip_y),
        (cx + S * 0.075, hip_y + S * 0.012),
        (cx,             hip_y - S * 0.01),
        (cx - S * 0.075, hip_y + S * 0.012),
        (cx - S * 0.155, hip_y),
    ]
    triad_poly(surf, jacket, RUST_CORE, RUST, RUST_SHEEN,
               sheen_pts=[(cx - S * 0.12, body_y - S * 0.03),
                          (cx - S * 0.02, body_y - S * 0.04),
                          (cx - S * 0.05, body_y + S * 0.06),
                          (cx - S * 0.125, body_y + S * 0.05)])
    # Bone neck/sternum peeking above the jacket lapels.
    triad_ellipse(surf, cx, body_y - S * 0.075, S * 0.05, S * 0.055,
                  BONE_CORE, BONE, SHEEN)

    # ── ROUND GUITARRON hugged to the chest (sits over the lower jacket) ──────
    # Held slightly to player-left + lower so the rust jacket lapels and the
    # botonadura stay visible (the warm-bone/rust/ochre trio must all read).
    gx, gy = cx - S * 0.02, body_y + S * 0.115
    grx, gry = S * 0.155, S * 0.15
    triad_ellipse(surf, gx, gy, grx, gry, GUITAR_CORE, GUITAR_WOOD, GUITAR_SHEEN)
    # Sound hole + turquoise rosette ring.
    triad_ellipse(surf, gx - S * 0.005, gy - S * 0.01, S * 0.058, S * 0.058,
                  (40, 30, 24), (54, 38, 30), (90, 64, 48), outline=None)
    pygame.draw.circle(surf, TURQ, (int(gx - S * 0.005), int(gy - S * 0.01)),
                       int(S * 0.066), int(SS * 1.4))
    pygame.draw.circle(surf, SHEEN, (int(gx - S * 0.005), int(gy - S * 0.01)),
                       int(S * 0.066), int(SS * 0.5))
    # A few strings across the body up to the (off-sheet here) neck stub.
    for k in range(-1, 2):
        sxoff = k * S * 0.018
        pygame.draw.line(surf, BONE,
                         (gx + sxoff, gy - gry * 0.95),
                         (gx + sxoff, gy + S * 0.02), max(1, int(SS * 0.6)))
    # Bone strumming hand resting on the lower body.
    triad_ellipse(surf, gx - S * 0.02, gy + S * 0.075, S * 0.05, S * 0.038,
                  BONE_CORE, BONE, SHEEN)
    for f in range(3):
        fx = gx - S * 0.05 + f * S * 0.022
        pygame.draw.line(surf, INK, (fx, gy + S * 0.07),
                         (fx + S * 0.004, gy + S * 0.125), max(1, int(SS)))
        pygame.draw.line(surf, BONE, (fx, gy + S * 0.07),
                         (fx + S * 0.004, gy + S * 0.125), max(1, int(SS * 0.5)))

    # Botonadura: silver button rows down both jacket sides (charro signature),
    # kept on the outer lapel edges so the guitarron can't occlude them.
    for side in (-1, 1):
        for i in range(3):
            byp = body_y - S * 0.025 + i * S * 0.05
            bxp = cx + side * (S * 0.135 - i * S * 0.004)
            triad_ellipse(surf, bxp, byp, S * 0.02, S * 0.02,
                          SILVER_CORE, SILVER, SILVER_SHEEN)

    # ── SKULL head (small, grinning) ──────────────────────────────────────────
    triad_ellipse(surf, cx, head_y, S * 0.135, S * 0.145,
                  BONE_CORE, BONE, SHEEN)
    # Jaw / cheekbones tuck (slightly narrower lower).
    triad_ellipse(surf, cx, head_y + S * 0.09, S * 0.10, S * 0.062,
                  BONE_CORE, BONE, SHEEN)
    # Eye sockets — Day-of-the-Dead style, with a tiny ochre marigold ring.
    for ex in (cx - S * 0.052, cx + S * 0.052):
        triad_ellipse(surf, ex, head_y - S * 0.01, S * 0.034, S * 0.038,
                      (40, 28, 26), (58, 40, 36), (96, 70, 60), outline=None)
        # marigold petal ring around the socket
        for k in range(8):
            a = k * math.tau / 8
            px = ex + math.cos(a) * S * 0.044
            py = (head_y - S * 0.01) + math.sin(a) * S * 0.05
            pygame.draw.circle(surf, OCHRE, (int(px), int(py)), max(1, int(SS * 1.1)))
        pygame.draw.circle(surf, INK, (int(ex), int(head_y - S * 0.01)),
                           int(S * 0.016))
    # Nose triangle.
    pygame.draw.polygon(surf, (40, 28, 26), [
        (cx, head_y + S * 0.022),
        (cx - S * 0.016, head_y + S * 0.055),
        (cx + S * 0.016, head_y + S * 0.055),
    ])
    # Grinning stitched smile.
    sm_y = head_y + S * 0.082
    pygame.draw.arc(surf, INK,
                    (cx - S * 0.072, sm_y - S * 0.04, S * 0.144, S * 0.08),
                    math.pi * 1.05, math.pi * 1.95, max(1, int(SS * 1.6)))
    for k in range(-3, 4):
        tx = cx + k * S * 0.02
        pygame.draw.line(surf, INK, (tx, sm_y - S * 0.012),
                         (tx, sm_y + S * 0.014), max(1, int(SS)))
    # Curly painted moustache (rust to read warm against bone).
    for side in (-1, 1):
        msx = cx + side * S * 0.02
        pts = [(int(cx), int(head_y + S * 0.06))]
        for t in range(0, 11):
            tt = t / 10.0
            ang = tt * math.pi * 1.5
            mx = msx + side * (S * 0.02 + tt * S * 0.052)
            my = head_y + S * 0.066 + math.sin(ang) * S * 0.018 + tt * S * 0.006
            pts.append((int(mx), int(my)))
        pygame.draw.lines(surf, INK, False, pts, max(2, int(SS * 2.2)))
        pygame.draw.lines(surf, RUST, False, pts, max(1, int(SS * 1.2)))

    # ── VAST CIRCULAR SOMBRERO — flat disc brim (the dominant read) ───────────
    # Wide flat brim disc (distinct from Catrina's plumed couture brim).
    triad_ellipse(surf, cx, hat_y, S * 0.40, S * 0.115,
                  OCHRE_CORE, OCHRE, OCHRE_SHEEN)
    # Embroidered brim band: rust + turquoise stitch ring near the rim edge.
    pygame.draw.ellipse(surf, RUST,
                        (cx - S * 0.36, hat_y - S * 0.092,
                         S * 0.72, S * 0.184), max(2, int(SS * 1.8)))
    pygame.draw.ellipse(surf, TURQ,
                        (cx - S * 0.31, hat_y - S * 0.078,
                         S * 0.62, S * 0.156), max(1, int(SS)))
    # Crown of the hat (cone) seated on the brim.
    crown = [
        (cx - S * 0.115, hat_y - S * 0.015),
        (cx - S * 0.075, hat_y - S * 0.155),
        (cx + S * 0.075, hat_y - S * 0.155),
        (cx + S * 0.115, hat_y - S * 0.015),
    ]
    triad_poly(surf, crown, OCHRE_CORE, OCHRE, OCHRE_SHEEN,
               sheen_pts=[(cx - S * 0.10, hat_y - S * 0.02),
                          (cx - S * 0.06, hat_y - S * 0.145),
                          (cx - S * 0.02, hat_y - S * 0.145),
                          (cx - S * 0.05, hat_y - S * 0.02)])
    # Crown band (rust) + silver concha.
    pygame.draw.line(surf, RUST,
                     (cx - S * 0.10, hat_y - S * 0.03),
                     (cx + S * 0.10, hat_y - S * 0.03), max(2, int(SS * 2)))
    triad_ellipse(surf, cx, hat_y - S * 0.035, S * 0.022, S * 0.022,
                  SILVER_CORE, SILVER, SILVER_SHEEN)

    grow_outline(surf, INK, 1)
    out = pygame.transform.smoothscale(surf, (target_size, target_size))
    return out


# ── the prop -> pillar mirror (guitarron neck) ───────────────────────────────

def draw_pillar(width, height, top_cap=True):
    """Upright guitarron / guitar neck pillar. Fretted neck = repeatable shaft
    body (fret banding); round sound-hole body with a turquoise rosette =
    detachable gap-edge cap. Round body on-axis -> clean vertical mirror."""
    W = width * SS
    H = height * SS
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    cx = W * 0.5

    neck_w = W * 0.34
    # Repeatable fretted-neck shaft.
    neck = pygame.Rect(int(cx - neck_w / 2), 0, int(neck_w), int(H))
    pygame.draw.rect(surf, GUITAR_CORE, neck)
    inner = neck.inflate(-int(SS * 3), 0)
    pygame.draw.rect(surf, GUITAR_WOOD, inner)
    # Top-left sheen stripe on the neck.
    pygame.draw.rect(surf, GUITAR_SHEEN,
                     (int(cx - neck_w / 2 + SS * 2), 0,
                      int(neck_w * 0.26), int(H)))
    # Fret banding (silver) + a thin bone string pair down the centre.
    fret_n = max(4, int(height / 14))
    for i in range(1, fret_n):
        fy = int(H * i / fret_n)
        pygame.draw.line(surf, SILVER,
                         (cx - neck_w / 2, fy), (cx + neck_w / 2, fy),
                         max(1, int(SS)))
        pygame.draw.circle(surf, SILVER_SHEEN,
                           (int(cx), fy), max(1, int(SS * 0.8)))
    for k in (-1, 1):
        pygame.draw.line(surf, BONE,
                         (cx + k * neck_w * 0.14, 0),
                         (cx + k * neck_w * 0.14, H), max(1, int(SS * 0.7)))

    # Gap-edge cap: round resonator body with turquoise rosette.
    if top_cap:
        by = H - W * 0.40
        brx, bry = W * 0.46, W * 0.42
        triad_ellipse(surf, cx, by, brx, bry,
                      GUITAR_CORE, GUITAR_WOOD, GUITAR_SHEEN)
        triad_ellipse(surf, cx, by, W * 0.16, W * 0.16,
                      (40, 30, 24), (54, 38, 30), (90, 64, 48), outline=None)
        pygame.draw.circle(surf, TURQ, (int(cx), int(by)),
                           int(W * 0.20), max(2, int(SS * 1.6)))
        pygame.draw.circle(surf, SHEEN, (int(cx), int(by)),
                           int(W * 0.20), max(1, int(SS * 0.6)))
        # bridge + strings fanning onto the neck
        for k in range(-1, 2):
            pygame.draw.line(surf, BONE,
                             (cx + k * W * 0.05, by + bry * 0.6),
                             (cx + k * neck_w * 0.14, by - bry),
                             max(1, int(SS * 0.7)))

    grow_outline(surf, INK, 1)
    return pygame.transform.smoothscale(surf, (width, height))


# ── sheet composition ─────────────────────────────────────────────────────────

def build_sheet():
    W, H = 880, 660
    sheet = pygame.Surface((W, H))
    sheet.fill((46, 40, 52))   # warm-dark neutral review backdrop

    font = pygame.font.SysFont("arial", 18, bold=True)
    small = pygame.font.SysFont("arial", 13)

    def label(txt, x, y, col=(245, 238, 226)):
        sheet.blit(font.render(txt, True, col), (x, y))

    def caption(txt, x, y, col=(208, 200, 210)):
        sheet.blit(small.render(txt, True, col), (x, y))

    label("MARIACHI — strumming charro skeleton musician", 18, 12,
          (252, 224, 150))
    caption("warm-bone + rust-red + ochre · warm festive (vs Catrina's cool couture)",
            18, 36)

    # Large creature.
    big = draw_mariachi(300)
    sheet.blit(big, (24, 64))
    caption("creature · large", 24, 366)

    # Mid-scale creature for legibility ramp.
    mid = draw_mariachi(150)
    sheet.blit(mid, (350, 64))
    caption("creature · 150px", 350, 222)

    # 32px creature with a 4x zoom of the same so the read is judgeable.
    tiny = draw_mariachi(32)
    sheet.blit(tiny, (350, 252))
    caption("32px", 350, 286)
    zoom = pygame.transform.scale(tiny, (128, 128))
    sheet.blit(zoom, (392, 252))
    caption("32px @4x", 392, 382)

    # Prop -> pillar mirror: a repeatable shaft section mirrored top<->bottom
    # with detachable gap caps (guitarron resonator) facing the gap.
    px = 560
    py = 64
    cap_h = 96
    shaft_h = 150
    big_w = 64
    # Bottom pillar: cap at top (faces gap), shaft below.
    bot_cap = draw_pillar(big_w, cap_h, top_cap=True)
    bot_shaft = draw_pillar(big_w, shaft_h, top_cap=False)
    # Top pillar = vertical mirror.
    top_cap = pygame.transform.flip(bot_cap, False, True)
    top_shaft = pygame.transform.flip(bot_shaft, False, True)

    gap = 70
    # top half (shaft then cap toward the gap)
    sheet.blit(top_shaft, (px, py))
    sheet.blit(top_cap, (px, py + shaft_h))
    # gap
    gap_y = py + shaft_h + cap_h
    # bottom half (cap toward the gap then shaft)
    sheet.blit(bot_cap, (px, gap_y + gap))
    sheet.blit(bot_shaft, (px, gap_y + gap + cap_h))
    caption("prop->pillar mirror", px - 4, py + shaft_h * 2 + cap_h * 2 + gap + 6)
    caption("guitarron neck", px - 4, py + shaft_h * 2 + cap_h * 2 + gap + 22)

    # 32px pillar caps (judge the gap-edge read small).
    tcap = draw_pillar(28, 40, top_cap=True)
    sheet.blit(tcap, (px + 110, py + 20))
    czoom = pygame.transform.scale(tcap, (112, 160))
    sheet.blit(czoom, (px + 150, py + 20))
    caption("cap 28px / @4x", px + 110, py + 188)

    # Palette swatch strip.
    sw_y = H - 70
    swatches = [
        ("bone", BONE), ("tan", BONE_SHADE), ("rust", RUST),
        ("silver", SILVER), ("ochre", OCHRE), ("turq", TURQ),
        ("ink", INK), ("sheen", SHEEN),
    ]
    for i, (nm, col) in enumerate(swatches):
        sx = 24 + i * 96
        pygame.draw.rect(sheet, col, (sx, sw_y, 80, 34))
        pygame.draw.rect(sheet, (20, 18, 22), (sx, sw_y, 80, 34), 2)
        caption(nm, sx + 2, sw_y + 36)

    return sheet


if __name__ == "__main__":
    out = build_sheet()
    dst = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(out, dst)
    print("wrote", dst)
