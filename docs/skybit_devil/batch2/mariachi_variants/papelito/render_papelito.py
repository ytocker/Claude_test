"""
Papelito — a calaca built from PAPEL PICADO, perforated tissue-paper bunting
given a body (MARIACHI-lineage warm-skeleton family, concept D).

LEAD FACET: CALACA DECORATION. The creature is nothing but festival decoration
that woke up — a flat scalloped cut-paper sheet strung from a bunting line, with
a skull face PUNCHED as negative space out of the sheet-top (sky shows THROUGH
the sockets). The punched-out face IS the anatomy; the fluttering banner IS the
body. Deliberately the LEAST bony body in the family — flat and papery where
every other take is volumetric bone.

House style: chibi proportions, FLAT saturated fills + hard 1-2px ink keylines,
form via a TRIAD — but here, to PROTECT THE FLATNESS, the triad reads strictly
as front-sheet / back-sheet shadow / top-edge sheen (NO volumetric bone, NO
rounded rim-light dome anywhere). Silhouette POP via a 1px outline grown from
the alpha mask; supersample SS=4 -> smoothscale.

Negative-space punchwork is real here: the skull face, the stamped star/flower
perforations, and the pinked scalloped hem are all CUT THROUGH the sheet so the
backdrop shows through — that is the whole gag and it must hold at 32px.

Sheet shows the creature AND its prop->pillar mirror (bunting string + cut-paper
marigold-rosette cap) at large + 32px scales, a pure-black silhouette panel, a
sky-through-sockets verification panel, and the PINNED PALETTE swatches.

Run headless:  SDL_VIDEODRIVER=dummy python render_papelito.py
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame

pygame.init()

# ── PINNED PALETTE (locked brief D, exact hexes) ─────────────────────────────
CREAM       = (246, 238, 222)   # paper-cream sheet base — HERO body mass
MARIGOLD    = (244, 150,  44)   # marigold-orange flag
PINK        = (232,  96, 150)   # papel-pink flag
MASA        = (226, 182,  80)   # masa-gold flag
TURQ        = ( 56, 168, 168)   # turquoise flag — the SINGLE cool note
CORD        = (190,  60,  50)   # rust-red bunting cord
INK         = ( 28,  22,  26)   # keyline ink
SHEEN       = (252, 246, 232)   # top-left rim sheen

# Derived working tones, all kept inside the pinned families. For Papelito the
# "dark-core" of the triad is a BACK-SHEET SHADOW (a flat darker copy of the same
# hue offset down-right), never a rounded bone core — this keeps every mass
# reading as a flat sheet of paper with a sheet behind it, not a 3D volume.
CREAM_BACK  = (206, 196, 176)   # cream back-sheet shadow (flat, offset)
CREAM_SHEEN = (252, 247, 236)   # cream top-edge catch
MARI_BACK   = (196, 110,  28)
PINK_BACK   = (188,  66, 112)
MASA_BACK   = (184, 142,  52)
TURQ_BACK   = ( 34, 122, 124)
SKY_HOLE    = (  0,   0,   0, 0)   # true cut-through (alpha) for punched holes

SS = 4   # supersample factor


# ── helpers ──────────────────────────────────────────────────────────────────

def _poly(surf, color, pts):
    pygame.draw.polygon(surf, color, [(int(x), int(y)) for x, y in pts])


def paper_sheet(surf, pts, fill, back, sheen, outline=INK,
                shadow_dx=None, shadow_dy=None, sheen_band=None):
    """A flat cut-paper sheet via the protected-flat triad:
      back-sheet shadow (flat darker copy offset down-right)
        -> flat front fill
          -> a thin top-edge sheen band (a CATCH on the paper lip, never a dome).
    Read is "front sheet over its own shadow", deliberately NON-volumetric."""
    if shadow_dx is None:
        shadow_dx = SS * 2.4
    if shadow_dy is None:
        shadow_dy = SS * 2.4
    # Back-sheet shadow: same silhouette, offset, flat darker hue.
    _poly(surf, back, [(x + shadow_dx, y + shadow_dy) for x, y in pts])
    # Hard ink keyline (fat stroke at SS scale so 1-2px survives smoothscale).
    if outline is not None:
        _poly(surf, outline, pts)
        pygame.draw.polygon(surf, outline, [(int(x), int(y)) for x, y in pts],
                            int(SS * 1.4))
    # Flat front fill, inset just inside the keyline.
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    inset = [(p[0] + (cx - p[0]) * 0.05, p[1] + (cy - p[1]) * 0.05) for p in pts]
    _poly(surf, fill, inset)
    # Top-edge sheen band: a flat sliver hugging the upper edge only.
    if sheen_band:
        _poly(surf, sheen, sheen_band)


def punch(surf, draw_fn):
    """Stamp a TRUE cut-through hole: render the punch shape to a scratch alpha
    surface, then blit it with BLEND_RGBA_MULT so the sheet alpha is zeroed where
    the punch is opaque — the backdrop then shows THROUGH the sheet (the whole
    papel-picado gag). draw_fn(scratch) draws the punch in opaque WHITE; we invert
    it to a multiply mask."""
    W, H = surf.get_size()
    scratch = pygame.Surface((W, H), pygame.SRCALPHA)
    scratch.fill((255, 255, 255, 255))
    hole = pygame.Surface((W, H), pygame.SRCALPHA)
    draw_fn(hole)                       # punch shapes drawn opaque
    # Where hole is opaque, drive the multiply mask to alpha 0.
    inv = pygame.Surface((W, H), pygame.SRCALPHA)
    inv.fill((255, 255, 255, 255))
    inv.blit(hole, (0, 0))
    # Build a mask that is white(opaque)=keep, and where hole exists -> alpha 0.
    m = pygame.mask.from_surface(hole)
    mult = m.to_surface(setcolor=(255, 255, 255, 0), unsetcolor=(255, 255, 255, 255))
    surf.blit(mult, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)


def grow_outline(surf, color=INK, thickness=1):
    """1px (post-scale) outline grown from the alpha mask — the silhouette POP.
    Run at supersample scale so it survives smoothscale. Because Papelito has
    punched interior holes, the mask outline traces the OUTER edge; interior
    cuts keep their own keylines drawn at punch time."""
    mask = pygame.mask.from_surface(surf)
    for pts in mask.outline(every=2), :
        if len(pts) > 2:
            pygame.draw.lines(surf, color, True, pts, max(1, thickness * SS))


# ── the creature ─────────────────────────────────────────────────────────────

def draw_papelito(target_size):
    """A papel-picado banner-spirit: a scalloped rectangular cream paper SHEET
    (pinked zig-zag hem) strung from an arc of triangular bunting flags, a skull
    face PUNCHED into the sheet-top (sky-through sockets), stamped star/flower
    perforations across the body, and tiny paper-strip arms."""
    S = target_size * SS
    surf = pygame.Surface((S, S), pygame.SRCALPHA)
    cx = S * 0.5

    # Layout. The dominant read is a tall flat sheet; the bunting arc crowns it.
    bunt_y  = S * 0.115         # bunting cord arc height
    sheet_t = S * 0.215         # sheet top edge
    sheet_b = S * 0.80          # sheet bottom (before pinked hem)
    sheet_w = S * 0.30          # half-width of the main sheet

    # ── BUNTING STRING: a rust cord arc with stacked triangular papel flags ────
    # Drawn first so the sheet hangs from it. The cord bows in a shallow catenary.
    cord_pts = []
    for i in range(31):
        t = i / 30.0
        x = S * 0.10 + t * S * 0.80
        y = bunt_y + math.sin(t * math.pi) * S * 0.018 * -1 + (1 - math.sin(t * math.pi)) * S * 0.04
        cord_pts.append((x, y))
    pygame.draw.lines(surf, INK, False, [(int(x), int(y)) for x, y in cord_pts],
                      max(2, int(SS * 1.8)))
    pygame.draw.lines(surf, CORD, False, [(int(x), int(y)) for x, y in cord_pts],
                      max(1, int(SS * 1.0)))

    # Triangular bunting flags hanging off the cord — the rainbow paper read.
    flag_cols = [MARIGOLD, PINK, MASA, TURQ, PINK, MARIGOLD, MASA]
    flag_back = [MARI_BACK, PINK_BACK, MASA_BACK, TURQ_BACK, PINK_BACK,
                 MARI_BACK, MASA_BACK]
    nfl = len(flag_cols)
    for i in range(nfl):
        # sample along the cord
        ct = (i + 0.5) / nfl
        cidx = int(ct * (len(cord_pts) - 1))
        ax, ay = cord_pts[cidx]
        fw = S * 0.05          # flag half-width
        fh = S * 0.085         # flag drop
        tri = [(ax - fw, ay), (ax + fw, ay), (ax, ay + fh)]
        paper_sheet(surf, tri, flag_cols[i], flag_back[i], SHEEN,
                    shadow_dx=SS * 1.6, shadow_dy=SS * 1.6,
                    sheen_band=[(ax - fw, ay), (ax - fw * 0.2, ay),
                                (ax - fw * 0.45, ay + fh * 0.4)])
        # tiny punched dot in each flag — papel-picado perforation, holds the read.
        def _flagdot(h, ax=ax, ay=ay, fh=fh):
            pygame.draw.circle(h, (255, 255, 255, 255),
                               (int(ax), int(ay + fh * 0.42)), int(S * 0.012))
        punch(surf, _flagdot)

    # ── PAPER-STRIP ARMS: thin folded cut-paper streamers off the sheet sides ──
    # Kept as flat zig-zag strips (accordion-folded paper), never bone limbs.
    for side in (-1, 1):
        ax0 = cx + side * sheet_w * 0.96
        ay0 = S * 0.50
        strip = [(ax0, ay0)]
        for k in range(1, 5):
            strip.append((ax0 + side * S * (0.045 * k),
                          ay0 + (S * 0.03 if k % 2 else -S * 0.005) + k * S * 0.012))
        # draw as a folded ribbon: alternating marigold / pink segments
        for k in range(len(strip) - 1):
            seg_col = MARIGOLD if k % 2 == 0 else PINK
            seg_bk = MARI_BACK if k % 2 == 0 else PINK_BACK
            a = strip[k]
            b = strip[k + 1]
            quad = [(a[0], a[1] - S * 0.022), (b[0], b[1] - S * 0.018),
                    (b[0], b[1] + S * 0.018), (a[0], a[1] + S * 0.022)]
            paper_sheet(surf, quad, seg_col, seg_bk, SHEEN,
                        shadow_dx=SS * 1.2, shadow_dy=SS * 1.4, sheen_band=None)

    # ── MAIN PAPEL SHEET (the body) — a tall scalloped rectangle ──────────────
    # Pinked / scalloped BOTTOM hem built as a zig-zag run of points so the
    # silhouette bottom reads as torn festival paper, not a flat block.
    n_scal = 7
    body = [(cx - sheet_w, sheet_t), (cx + sheet_w, sheet_t),
            (cx + sheet_w, sheet_b)]
    for i in range(n_scal + 1):
        t = i / n_scal
        x = cx + sheet_w - t * (2 * sheet_w)
        # alternate down-point (pinked V) and up-notch
        dip = S * 0.055 if i % 2 == 0 else S * 0.018
        body.append((x, sheet_b + dip))
    body.append((cx - sheet_w, sheet_b))
    paper_sheet(surf, body, CREAM, CREAM_BACK, CREAM_SHEEN,
                shadow_dx=SS * 2.6, shadow_dy=SS * 2.6,
                sheen_band=[(cx - sheet_w, sheet_t),
                            (cx - sheet_w * 0.3, sheet_t),
                            (cx - sheet_w * 0.5, sheet_t + S * 0.05),
                            (cx - sheet_w, sheet_t + S * 0.06)])

    # A folded crease line down the sheet (paper fold) — flat ink tick, adds the
    # "tissue paper that's been folded" tell without volume.
    pygame.draw.line(surf, CREAM_BACK,
                     (int(cx + sheet_w * 0.0), int(sheet_t + S * 0.02)),
                     (int(cx + sheet_w * 0.0), int(sheet_b)),
                     max(1, int(SS * 0.8)))

    # ── PUNCHED SKULL FACE (negative space — sky shows THROUGH) ───────────────
    # The skull is CUT OUT of the sheet-top. Eye sockets + nose + a grin row are
    # all true holes; this negative-space face IS the anatomy. Must hold at 32px,
    # so the two sockets are the biggest, boldest cuts.
    face_y = sheet_t + S * 0.165

    def _skullcut(h):
        # Eye sockets — big bold cut ovals (the dominant 32px tell).
        for ex in (cx - S * 0.085, cx + S * 0.085):
            pygame.draw.ellipse(h, (255, 255, 255, 255),
                                (int(ex - S * 0.058), int(face_y - S * 0.052),
                                 int(S * 0.116), int(S * 0.108)))
        # Nose — punched inverted heart / triangle.
        pygame.draw.polygon(h, (255, 255, 255, 255), [
            (int(cx), int(face_y + S * 0.10)),
            (int(cx - S * 0.026), int(face_y + S * 0.05)),
            (int(cx + S * 0.026), int(face_y + S * 0.05)),
        ])
        # Grin row — a run of punched teeth gaps (the cut between teeth).
        gy = face_y + S * 0.135
        pygame.draw.arc(h, (255, 255, 255, 255),
                        (int(cx - S * 0.10), int(gy - S * 0.05),
                         int(S * 0.20), int(S * 0.115)),
                        math.pi * 1.02, math.pi * 1.98, max(2, int(SS * 2.2)))
        for k in range(-3, 4):
            tx = cx + k * S * 0.028
            pygame.draw.line(h, (255, 255, 255, 255),
                             (int(tx), int(gy - S * 0.018)),
                             (int(tx), int(gy + S * 0.026)), max(2, int(SS * 1.6)))

    punch(surf, _skullcut)

    # Ink keylines AROUND the punched cuts so the holes read crisp against any
    # backdrop — drawn as hollow strokes that hug the cut edges (the cut is alpha,
    # the keyline is the dark paper lip around it).
    for ex in (cx - S * 0.085, cx + S * 0.085):
        pygame.draw.ellipse(surf, INK,
                            (int(ex - S * 0.058 - SS), int(face_y - S * 0.052 - SS),
                             int(S * 0.116 + SS * 2), int(S * 0.108 + SS * 2)),
                            max(1, int(SS * 1.2)))
    # Tiny ink lash-ticks at socket corners — scary-CUTE festival paint.
    for ex, sgn in ((cx - S * 0.085, -1), (cx + S * 0.085, 1)):
        for k in range(3):
            a = -0.5 + k * 0.45
            sx = ex + sgn * S * 0.058 * math.cos(a)
            sy = face_y - S * 0.01 + S * 0.06 * math.sin(a)
            pygame.draw.line(surf, INK, (int(sx), int(sy)),
                             (int(sx + sgn * S * 0.022), int(sy + S * 0.006)),
                             max(1, int(SS * 0.9)))

    # ── STAMPED PERFORATIONS across the body (papel-picado cutwork) ───────────
    # Star + flower + dot punches in the lower sheet. These reinforce CALACA
    # DECORATION as the lead facet — the cutwork is the signature. Kept below the
    # face so the face stays the dominant cut at 32px.
    def _bodycuts(h):
        # central flower (5 petals) under the chin
        fcx, fcy = cx, sheet_t + S * 0.38
        for k in range(5):
            a = k * math.tau / 5 - math.pi / 2
            px = fcx + math.cos(a) * S * 0.045
            py = fcy + math.sin(a) * S * 0.045
            pygame.draw.circle(h, (255, 255, 255, 255),
                               (int(px), int(py)), int(S * 0.022))
        pygame.draw.circle(h, (255, 255, 255, 255),
                           (int(fcx), int(fcy)), int(S * 0.02))
        # two small 4-point stars flanking
        for sx in (cx - S * 0.16, cx + S * 0.16):
            sy = sheet_t + S * 0.40
            star = []
            for k in range(8):
                a = k * math.tau / 8 - math.pi / 2
                r = S * 0.04 if k % 2 == 0 else S * 0.015
                star.append((sx + math.cos(a) * r, sy + math.sin(a) * r))
            pygame.draw.polygon(h, (255, 255, 255, 255),
                                [(int(x), int(y)) for x, y in star])
        # row of small dots above the hem (papel-picado border)
        for k in range(-3, 4):
            dx = cx + k * S * 0.07
            pygame.draw.circle(h, (255, 255, 255, 255),
                               (int(dx), int(sheet_t + S * 0.52)), int(S * 0.013))

    punch(surf, _bodycuts)

    # Faint ink rings around the larger cutwork so the perforations stay legible.
    pygame.draw.circle(surf, INK, (int(cx), int(sheet_t + S * 0.38)),
                       int(S * 0.072), max(1, int(SS * 0.7)))

    grow_outline(surf, INK, 1)
    return pygame.transform.smoothscale(surf, (target_size, target_size))


# ── the prop -> pillar mirror (bunting string + marigold-rosette cap) ─────────

def draw_pillar(width, height, top_cap=True):
    """Bunting string / flagpole pillar. A banner cord strung with stacked
    papel-picado flags = repeatable shaft body (each flag a band); a larger
    cut-paper marigold-rosette medallion = detachable gap-edge cap. On-axis flags
    + a round radial rosette read naturally vertical and symmetric (mirror clean).
    Cap sized ~shaft +35% so it stays balanced at the gap line."""
    W = width * SS
    H = height * SS
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    cx = W * 0.5

    # Repeatable SHAFT: a vertical rust cord with paper flags stacked down it,
    # each flag a band — the shaft tiles seamlessly.
    pygame.draw.line(surf, INK, (cx, 0), (cx, H), max(2, int(SS * 2.2)))
    pygame.draw.line(surf, CORD, (cx, 0), (cx, H), max(1, int(SS * 1.2)))

    band_h = W * 0.62
    flag_cols = [MARIGOLD, PINK, MASA, TURQ]
    flag_back = [MARI_BACK, PINK_BACK, MASA_BACK, TURQ_BACK]
    n = max(2, int(H / band_h))
    fw = W * 0.30
    for i in range(n):
        fy = i * band_h + band_h * 0.1
        ci = i % len(flag_cols)
        # alternate flags left/right of the cord so the shaft reads as a strung line
        tri = [(cx - fw, fy), (cx + fw, fy), (cx, fy + band_h * 0.78)]
        paper_sheet(surf, tri, flag_cols[ci], flag_back[ci], SHEEN,
                    shadow_dx=SS * 1.4, shadow_dy=SS * 1.4,
                    sheen_band=[(cx - fw, fy), (cx - fw * 0.2, fy),
                                (cx - fw * 0.4, fy + band_h * 0.35)])
        # punched dot per flag — keeps the cut-paper read on the shaft
        def _d(h, fy=fy, band_h=band_h):
            pygame.draw.circle(h, (255, 255, 255, 255),
                               (int(cx), int(fy + band_h * 0.38)), int(W * 0.07))
        punch(surf, _d)

    # Gap-edge CAP: a round cut-paper MARIGOLD ROSETTE medallion, radial + on-axis.
    if top_cap:
        rr = W * 0.42       # ~shaft (flag half-width) +35%
        ry = H - rr - W * 0.10
        # layered petal rosette: outer marigold ring, inner masa-gold, pink center
        for ring, (col, bk, rad) in enumerate((
                (MARIGOLD, MARI_BACK, rr),
                (MASA, MASA_BACK, rr * 0.66),
                (PINK, PINK_BACK, rr * 0.36))):
            npet = 12 if ring == 0 else 10
            pts = []
            for k in range(npet * 2):
                a = k * math.tau / (npet * 2)
                r = rad if k % 2 == 0 else rad * 0.72
                pts.append((cx + math.cos(a) * r, ry + math.sin(a) * r))
            paper_sheet(surf, pts, col, bk, SHEEN,
                        shadow_dx=SS * 1.6, shadow_dy=SS * 1.6, sheen_band=None)
        # punched ring of holes around the rosette (papel-picado) + center cut
        def _rosecuts(h, rr=rr, ry=ry):
            for k in range(8):
                a = k * math.tau / 8
                px = cx + math.cos(a) * rr * 0.5
                py = ry + math.sin(a) * rr * 0.5
                pygame.draw.circle(h, (255, 255, 255, 255),
                                   (int(px), int(py)), int(rr * 0.085))
            pygame.draw.circle(h, (255, 255, 255, 255),
                               (int(cx), int(ry)), int(rr * 0.13))
        punch(surf, _rosecuts)
        pygame.draw.circle(surf, INK, (int(cx), int(ry)),
                           int(rr * 0.13 + SS), max(1, int(SS * 0.9)))

    grow_outline(surf, INK, 1)
    return pygame.transform.smoothscale(surf, (width, height))


# ── pure-black silhouette read (accessibility / outline test) ─────────────────

def draw_silhouette(target_size):
    """Flatten the creature to a pure-black mask — proves the signature reads in
    the outline alone: scalloped paper rectangle + bunting arc + punched skull
    sockets cut clean through (the holes stay holes in the mask)."""
    rgba = draw_papelito(target_size)
    mask = pygame.mask.from_surface(rgba)
    surf = mask.to_surface(setcolor=(18, 16, 20, 255), unsetcolor=(0, 0, 0, 0))
    out = pygame.Surface((target_size, target_size), pygame.SRCALPHA)
    out.blit(surf, (0, 0))
    return out


# ── sheet composition ─────────────────────────────────────────────────────────

def build_sheet():
    W, H = 1000, 720
    sheet = pygame.Surface((W, H))
    sheet.fill((46, 40, 52))   # warm-dark neutral review backdrop

    font = pygame.font.SysFont("arial", 18, bold=True)
    small = pygame.font.SysFont("arial", 13)

    def label(txt, x, y, col=(245, 238, 226)):
        sheet.blit(font.render(txt, True, col), (x, y))

    def caption(txt, x, y, col=(208, 200, 210)):
        sheet.blit(small.render(txt, True, col), (x, y))

    label("PAPELITO — papel-picado banner-spirit  ·  round 1", 18, 12,
          (252, 224, 150))
    caption("LEAD FACET: CALACA DECORATION — punched cut-paper skull, the only "
            "flat non-bone body in the family", 18, 36)

    # Large creature.
    big = draw_papelito(300)
    sheet.blit(big, (24, 60))
    caption("creature · large (300px)", 24, 364)

    # Mid-scale legibility ramp.
    mid = draw_papelito(150)
    sheet.blit(mid, (352, 60))
    caption("creature · 150px", 352, 214)

    # 32px creature + 4x zoom.
    tiny = draw_papelito(32)
    sheet.blit(tiny, (352, 240))
    caption("32px", 352, 274)
    zoom = pygame.transform.scale(tiny, (128, 128))
    sheet.blit(zoom, (392, 240))
    caption("32px @4x", 392, 372)

    # Pure-black silhouette read (creature scale + 32px@4x) — the AD ship test.
    sil_big = draw_silhouette(150)
    sheet.blit(sil_big, (24, 408))
    caption("silhouette · 150px", 24, 562)
    caption("read: scalloped paper sheet,", 24, 578)
    caption("bunting arc, punched skull cuts", 24, 594)
    sil_tiny = draw_silhouette(32)
    sil_zoom = pygame.transform.scale(sil_tiny, (128, 128))
    sheet.blit(sil_zoom, (200, 408))
    caption("silhouette 32px @4x", 200, 540)

    # SKY-THROUGH-SOCKETS verification — the whole gag is the cuts being TRUE
    # holes, so render the creature over a sky gradient and confirm the backdrop
    # shows through the punched skull + perforations at 32px and large.
    panel_x = 352
    for yy in range(160):
        t = yy / 160.0
        top, bot = (120, 188, 232), (78, 132, 198)   # day-sky blue
        col = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        pygame.draw.line(sheet, col, (panel_x, 408 + yy), (panel_x + 160, 408 + yy))
    pygame.draw.rect(sheet, (24, 20, 26), (panel_x, 408, 160, 160), 2)
    sheet.blit(pygame.transform.scale(draw_papelito(150), (150, 150)),
               (panel_x + 5, 410))
    caption("sky shows THROUGH the cuts", panel_x, 570)
    caption("(punched skull = negative space)", panel_x, 586)

    sky2_x = 352
    for yy in range(64):
        t = yy / 64.0
        top, bot = (120, 188, 232), (78, 132, 198)
        col = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        pygame.draw.line(sheet, col, (sky2_x + 168, 408 + yy),
                         (sky2_x + 168 + 64, 408 + yy))
    pygame.draw.rect(sheet, (24, 20, 26), (sky2_x + 168, 408, 64, 64), 2)
    sheet.blit(pygame.transform.scale(draw_papelito(32), (64, 64)),
               (sky2_x + 168, 408))
    caption("32px on sky", sky2_x + 168, 474)
    caption("cuts hold", sky2_x + 168, 490)

    # Prop -> pillar mirror (bunting string + marigold-rosette cap).
    px = 600
    py = 60
    cap_h = 84
    shaft_h = 150
    big_w = 70
    bot_cap = draw_pillar(big_w, cap_h, top_cap=True)
    bot_shaft = draw_pillar(big_w, shaft_h, top_cap=False)
    top_cap = pygame.transform.flip(bot_cap, False, True)
    top_shaft = pygame.transform.flip(bot_shaft, False, True)

    gap = 60
    sheet.blit(top_shaft, (px, py))
    sheet.blit(top_cap, (px, py + shaft_h))
    gap_y = py + shaft_h + cap_h
    sheet.blit(bot_cap, (px, gap_y + gap))
    sheet.blit(bot_shaft, (px, gap_y + gap + cap_h))
    caption("prop->pillar mirror", px - 4, py + shaft_h * 2 + cap_h * 2 + gap + 8)
    caption("bunting string + marigold rosette cap", px - 4,
            py + shaft_h * 2 + cap_h * 2 + gap + 24)

    # 32px pillar cap (judge the gap-edge read small).
    tcap = draw_pillar(30, 42, top_cap=True)
    sheet.blit(tcap, (px + 140, py + 20))
    czoom = pygame.transform.scale(tcap, (120, 168))
    sheet.blit(czoom, (px + 185, py + 20))
    caption("cap 30px / @4x", px + 140, py + 196)
    caption("rosette cap ~shaft +35%", px + 140, py + 212)

    # Palette swatch strip.
    sw_y = H - 54
    swatches = [
        ("cream", CREAM), ("marigold", MARIGOLD), ("pink", PINK),
        ("masa", MASA), ("turq", TURQ), ("cord", CORD),
        ("ink", INK), ("sheen", SHEEN),
    ]
    for i, (nm, col) in enumerate(swatches):
        sx = 420 + i * 72
        pygame.draw.rect(sheet, col, (sx, sw_y, 60, 30))
        pygame.draw.rect(sheet, (20, 18, 22), (sx, sw_y, 60, 30), 2)
        caption(nm, sx + 2, sw_y + 32)

    return sheet


if __name__ == "__main__":
    out = build_sheet()
    dst = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(out, dst)
    print("wrote", dst)
