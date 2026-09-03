"""Five ways the PROFILE tag can be part of the frame's own silhouette.

The strapped-tag placement read as a satellite: a plate tethered under the
frame by hardware, with sky between the two. Everything here removes the gap
by construction — the tag is either cast into the frame's outline, cut into
its material, or grown out of it. The frame's contour is derived
morphologically from the union of its parts rather than stroked per-shape, so
a swell or a stem cannot leave a seam where two rectangles meet.

    OPTION=D|E|F|G|H python3 tools/menu-design/profile_frame_connected.py
    SHOWCASE=1       python3 tools/menu-design/profile_frame_connected.py
"""
import os
import sys

_ROOT = "/home/user/skybit"
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "tools", "menu-design"))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame                                     # noqa: E402
import profile_frame_variants as PF               # noqa: E402

B = PF.B
_hud = B._hud
GOLD_MID, GOLD_BRIGHT, GOLD_PALE, GOLD_DEEP = (
    B.GOLD_MID, B.GOLD_BRIGHT, B.GOLD_PALE, B.GOLD_DEEP)
W, H = 360, 640

GOLD_SHADE = (86, 60, 16)          # the underside of any gold moulding
RECESS = (52, 34, 14)              # the sunk field the label is cut into
_NBRS = ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1))


# ── silhouette machinery ────────────────────────────────────────────────────
def _erode(src, passes):
    """Morphological erosion by min-blitting the layer over itself in all
    eight directions — pygame.mask has no erode, and doing it in mask space
    would lose the colour the outline is later stroked in."""
    out = src.copy()
    for _ in range(passes):
        step = out.copy()
        for dx, dy in _NBRS:
            out.blit(step, (dx, dy), special_flags=pygame.BLEND_RGBA_MIN)
    return out


def union_outline(shape_fn, colour, thick=2):
    """One continuous rule around the UNION of every shape shape_fn fills.

    Stroking each rectangle separately is what makes a fused plate read as two
    stacked objects: the shared edge gets drawn twice and shows up as a seam.
    Filling the union and subtracting its own erosion can only ever produce
    the outer boundary, so overlapping parts weld silently.
    """
    full = pygame.Surface((W, H), pygame.SRCALPHA)
    shape_fn(full, colour)
    full.blit(_erode(full, thick), (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
    return full


def _body(surf, rect, radius=9, clip_top=None):
    """Solid moulding face: gold with a lit top lip and a shaded lower one."""
    lay = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.rect(lay, GOLD_MID, rect, border_radius=radius)
    top = pygame.Rect(rect.x, rect.y, rect.width, max(1, rect.height // 2))
    sh = pygame.Surface(top.size, pygame.SRCALPHA)
    sh.fill((255, 236, 196, 26))
    lay.blit(sh, top.topleft)
    # Blit an area, not a clip: the tablet's top edge must never appear inside
    # the sight opening or the fusion instantly reads as one plate laid over
    # another object.
    if clip_top is None:
        surf.blit(lay, (0, 0))
    else:
        area = pygame.Rect(0, clip_top, W, H - clip_top)
        surf.blit(lay, area.topleft, area)


def _label(surf, rect, size=12, track=2, tri=True):
    """The sunk label field, identical in every option so the comparison is
    about the join and not about the lettering."""
    pygame.draw.rect(surf, RECESS, rect, border_radius=5)
    pygame.draw.line(surf, (28, 17, 6), (rect.left + 4, rect.top + 1),
                     (rect.right - 4, rect.top + 1), 1)
    pygame.draw.line(surf, (120, 88, 34), (rect.left + 4, rect.bottom - 1),
                     (rect.right - 4, rect.bottom - 1), 1)
    cx = rect.centerx - (6 if tri else 0)
    _hud._tracked_label(surf, "PROFILE", (cx, rect.centery + 1), size,
                        color=(24, 14, 5), track=track, alpha=170)
    _hud._tracked_label(surf, "PROFILE", (cx, rect.centery), size,
                        color=GOLD_PALE, track=track, alpha=250)
    if tri:
        _hud._profile_tri(surf, rect.right - 8, rect.centery, 4, GOLD_PALE)


def _sight(surf, rect, radius, skip=None):
    """Inner sight rule. `skip` blanks the span a stem passes through, so the
    bright line stops at the stem's shoulders instead of ruling across it."""
    lay = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.rect(lay, GOLD_BRIGHT, rect, width=1, border_radius=radius)
    pygame.draw.line(lay, (*GOLD_PALE, 210), (rect.left + 12, rect.top + 1),
                     (rect.right - 12, rect.top + 1), 1)
    if skip:
        cut = pygame.Surface(skip.size, pygame.SRCALPHA)
        cut.fill((255, 255, 255, 255))
        lay.blit(cut, skip.topleft, special_flags=pygame.BLEND_RGBA_SUB)
    surf.blit(lay, (0, 0))


# ── D · keystone-swell ──────────────────────────────────────────────────────
D_FR = pygame.Rect(23, 198, 145, 112)      # x23..167  y198..309
D_PL = pygame.Rect(50, 302, 100, 32)       # x50..149  y302..333


def draw_D_keystone(surf):
    """keystone-swell — the bottom rail simply gets deeper over its middle
    run. The tablet has no border of its own: the rail's outer rule walks down
    its left shoulder, round the bottom, and back up onto the rail, so the two
    share one unbroken contour and the sight edge stays straight above it."""
    def shapes(s, c):
        pygame.draw.rect(s, c, D_FR, border_radius=13)
        pygame.draw.rect(s, c, D_PL, border_radius=9)

    _body(surf, D_PL, 9, clip_top=D_FR.bottom - 2)
    surf.blit(union_outline(shapes, GOLD_MID, 2), (0, 0))
    _sight(surf, D_FR.inflate(-8, -8), 8)
    pygame.draw.line(surf, GOLD_PALE, (D_PL.left + 10, D_PL.top + 9),
                     (D_PL.right - 10, D_PL.top + 9), 1)
    pygame.draw.line(surf, GOLD_SHADE, (D_PL.left + 10, D_PL.bottom - 3),
                     (D_PL.right - 10, D_PL.bottom - 3), 1)
    _label(surf, pygame.Rect(56, 313, 88, 16))
    return D_FR.union(D_PL)


# ── E · mortise-let-in ──────────────────────────────────────────────────────
E_FR = pygame.Rect(23, 198, 145, 111)      # x23..167  y198..308
E_PL = pygame.Rect(50, 301, 100, 33)       # x50..149  y301..333
E_BAR = 6                                  # cast-bar member depth


def draw_E_mortise(surf):
    """mortise-let-in — a solid cast bar frame with a socket chopped clean
    through its bottom rail. The tablet drops into the socket flush with the
    rail's inner face and hangs out below it, and the rail's cut cheeks are
    chamfered onto the tablet's sides, so the frame reads as holding the
    tablet rather than carrying it."""
    inner = E_FR.inflate(-E_BAR * 2, -E_BAR * 2)
    sock = pygame.Rect(E_PL.left, E_FR.bottom - E_BAR, E_PL.width, E_BAR)

    def shapes(s, c):
        pygame.draw.rect(s, c, E_FR, border_radius=12)
        pygame.draw.rect(s, c, E_PL, border_radius=8)

    _body(surf, E_PL, 8, clip_top=inner.bottom)
    bar = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.rect(bar, GOLD_MID, E_FR, border_radius=12)
    hole = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.rect(hole, (255, 255, 255, 255), inner, border_radius=7)
    pygame.draw.rect(hole, (255, 255, 255, 255), sock)
    bar.blit(hole, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
    lit = pygame.Surface((E_FR.width, 4), pygame.SRCALPHA)
    lit.fill((255, 240, 200, 40))
    bar.blit(lit, E_FR.topleft)
    surf.blit(bar, (0, 0))

    # Chamfered cheeks: the cut faces of the rail bevelling onto the tenon.
    for sx, sgn in ((E_PL.left, -1), (E_PL.right - 1, 1)):
        pygame.draw.polygon(surf, GOLD_BRIGHT, [
            (sx, E_FR.bottom - E_BAR), (sx + sgn * 5, E_FR.bottom - E_BAR),
            (sx, E_FR.bottom - 1)])
        pygame.draw.line(surf, (46, 30, 10), (sx, E_FR.bottom - E_BAR),
                         (sx, E_FR.bottom - 1), 1)
    surf.blit(union_outline(shapes, GOLD_MID, 1), (0, 0))
    pygame.draw.line(surf, GOLD_SHADE, (E_PL.left + 10, E_PL.bottom - 3),
                     (E_PL.right - 10, E_PL.bottom - 3), 1)
    _label(surf, pygame.Rect(56, 311, 88, 16))
    return E_FR.union(E_PL)


# ── F · stem-flare ──────────────────────────────────────────────────────────
F_FR = pygame.Rect(23, 198, 145, 110)      # x23..167  y198..307
F_PL = pygame.Rect(50, 322, 100, 28)       # x50..149  y322..349
F_NECK = [(84, 299), (116, 299), (112, 316), (122, 324), (78, 324), (88, 316)]


def draw_F_stem(surf):
    """stem-flare — the rail pinches into a short neck at its centre and the
    neck flares straight out into the tablet. Nothing crosses anything: it is
    one poured length of gold that happens to widen twice, and it carries the
    tablet down clear of the cloud without a rail to straddle."""
    def shapes(s, c):
        pygame.draw.rect(s, c, F_FR, border_radius=13)
        pygame.draw.polygon(s, c, F_NECK)
        pygame.draw.rect(s, c, F_PL, border_radius=9)

    fill = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.polygon(fill, GOLD_MID, F_NECK)
    area = pygame.Rect(0, 303, W, H - 303)
    surf.blit(fill, area.topleft, area)
    pygame.draw.line(surf, GOLD_PALE, (92, 305), (92, 318), 1)
    pygame.draw.line(surf, GOLD_SHADE, (108, 305), (108, 318), 1)
    _body(surf, F_PL, 9)
    surf.blit(union_outline(shapes, GOLD_MID, 2), (0, 0))
    # The sight rule stops at the stem's shoulders; ruling straight across it
    # would draw the very seam this option exists to avoid.
    _sight(surf, F_FR.inflate(-8, -8), 8, skip=pygame.Rect(83, 300, 34, 8))
    pygame.draw.line(surf, GOLD_PALE, (F_PL.left + 10, F_PL.top + 3),
                     (F_PL.right - 10, F_PL.top + 3), 1)
    pygame.draw.line(surf, GOLD_SHADE, (F_PL.left + 10, F_PL.bottom - 3),
                     (F_PL.right - 10, F_PL.bottom - 3), 1)
    _label(surf, pygame.Rect(56, 328, 88, 16))
    return F_FR.union(F_PL)


# ── G · deep-rail-inlay ─────────────────────────────────────────────────────
G_FR = pygame.Rect(23, 186, 145, 124)      # x23..167  y186..309
G_OPEN = pygame.Rect(29, 213, 133, 91)     # x29..161  y213..303


def draw_G_deeprail(surf):
    """deep-rail-inlay — there is no tag. The frame is a broad-moulding
    portrait frame whose top rail is deep enough to carry the label, and the
    label is sunk straight into that rail. The silhouette is one closed
    rounded rectangle, so the question of how the tag attaches never arises."""
    lay = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.rect(lay, GOLD_MID, G_FR, border_radius=14)
    grad = pygame.Surface((G_FR.width, G_FR.height), pygame.SRCALPHA)
    for i in range(G_FR.height):
        a = int(34 - 60 * i / G_FR.height)
        grad.fill((255, 240, 202, max(0, a)), (0, i, G_FR.width, 1))
    lay.blit(grad, G_FR.topleft)
    shade = pygame.Surface((G_FR.width, G_FR.height), pygame.SRCALPHA)
    for i in range(G_FR.height):
        a = int(-14 + 52 * i / G_FR.height)
        shade.fill((40, 24, 6, max(0, a)), (0, i, G_FR.width, 1))
    lay.blit(shade, G_FR.topleft)
    hole = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.rect(hole, (255, 255, 255, 255), G_OPEN, border_radius=8)
    lay.blit(hole, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
    surf.blit(lay, (0, 0))

    pygame.draw.rect(surf, GOLD_MID, G_FR, width=1, border_radius=14)
    pygame.draw.line(surf, (*GOLD_PALE, 220), (G_FR.left + 16, G_FR.top + 1),
                     (G_FR.right - 16, G_FR.top + 1), 1)
    pygame.draw.rect(surf, GOLD_SHADE, G_OPEN, width=1, border_radius=8)
    pygame.draw.line(surf, GOLD_BRIGHT, (G_OPEN.left + 10, G_OPEN.bottom),
                     (G_OPEN.right - 10, G_OPEN.bottom), 1)
    _label(surf, pygame.Rect(51, 191, 88, 16))
    return G_FR


# ── H · apron-step ──────────────────────────────────────────────────────────
H_FR = pygame.Rect(23, 198, 138, 110)      # x23..160  y198..307
H_AP = pygame.Rect(54, 296, 107, 40)       # x54..160  y296..335


def draw_H_apron(surf):
    """apron-step — the bottom rail is thin on the left and simply steps
    deeper for its right-hand run, and the label is engraved into that deeper
    run. The step's far end IS the frame's own bottom-right corner, so the
    band cannot detach: it has no free edge of its own."""
    def shapes(s, c):
        pygame.draw.rect(s, c, H_FR, border_radius=13)
        pygame.draw.rect(s, c, H_AP, border_radius=13)

    _body(surf, H_AP, 13, clip_top=H_FR.bottom - 2)
    surf.blit(union_outline(shapes, GOLD_MID, 2), (0, 0))
    _sight(surf, H_FR.inflate(-8, -8), 8)
    pygame.draw.line(surf, GOLD_PALE, (H_AP.left + 12, H_FR.bottom + 2),
                     (H_AP.right - 10, H_FR.bottom + 2), 1)
    pygame.draw.line(surf, GOLD_SHADE, (H_AP.left + 12, H_AP.bottom - 3),
                     (H_AP.right - 10, H_AP.bottom - 3), 1)
    _label(surf, pygame.Rect(62, 310, 88, 16))
    return H_FR.union(H_AP)


OPTIONS = {
    "current":  (PF.B.draw_profile_frame, "current (buggy)",
                 "REFERENCE — rail clips Pip's feet; tag floats free, no join",
                 pygame.Rect(18, 276, 154, 62)),
    "D": (draw_D_keystone, "keystone-swell",
          "the rail deepens over its middle run INTO the tablet - one contour",
          pygame.Rect(18, 288, 154, 62)),
    "E": (draw_E_mortise, "mortise-let-in",
          "a socket chopped through a cast bar rail; tablet let in flush",
          pygame.Rect(18, 288, 154, 62)),
    "F": (draw_F_stem, "stem-flare",
          "rail pinches to a neck and flares out into the tablet - one pour",
          pygame.Rect(18, 292, 154, 62)),
    "G": (draw_G_deeprail, "deep-rail-inlay",
          "no tag at all - the label is sunk into the frame's own top rail",
          pygame.Rect(18, 178, 154, 62)),
    "H": (draw_H_apron, "apron-step",
          "the rail steps deeper and that step becomes the label band",
          pygame.Rect(18, 288, 154, 62)),
}
ORDER = ["current", "D", "E", "F", "G", "H"]


CELL_W, PANEL_H, DET_H, CAP_H = 380, 640, 124, 60
CELL_H = 10 + PANEL_H + 8 + DET_H + 8 + CAP_H
COLS = 3


def _sheet_font(size, bold=False):
    f = pygame.font.Font(None, size)
    f.set_bold(bold)
    return f


def build_showcase(path, phase=0.20):
    import profile_frame_verify as V
    pygame.font.init()
    pip = V.pip_points()
    ropes = V.rope_points()
    polys = V.rope_polylines()

    rows = (len(ORDER) + COLS - 1) // COLS
    sheet = pygame.Surface((CELL_W * COLS, 64 + CELL_H * rows))
    sheet.fill((17, 15, 26))
    f_head = _sheet_font(30, True)
    f_slug = _sheet_font(26, True)
    f_body = _sheet_font(21)
    f_num = _sheet_font(19)
    sheet.blit(f_head.render(
        "SKYBIT menu — how the PROFILE tag JOINS the frame", True,
        (255, 226, 160)), (18, 14))
    sheet.blit(f_body.render(
        "1x, PHASE 0.20. Every option below makes the tag part of the frame's "
        "own silhouette — no straps, no gap. Clearances are measured off Pip's "
        "drawn mask and the ropes' own polyline, not bounding boxes.",
        True, (176, 172, 196)), (18, 42))

    for i, key in enumerate(ORDER):
        fn, slug, thesis, crop = OPTIONS[key]
        panel, _ = PF.build(phase, fn)
        gold = V.gold_points(fn)
        gp = V.min_gap(pip, gold)
        gr = V.min_gap(ropes, gold)

        cx = (i % COLS) * CELL_W
        cy = 64 + (i // COLS) * CELL_H
        accent = (150, 96, 96) if key == "current" else (208, 168, 92)
        pygame.draw.rect(sheet, (30, 27, 42), (cx + 4, cy + 4,
                                               CELL_W - 8, CELL_H - 8))
        sheet.blit(panel, (cx + 10, cy + 10))
        pygame.draw.rect(sheet, accent, (cx + 10, cy + 10, 360, PANEL_H), 1)
        pygame.draw.rect(sheet, (86, 74, 52), (cx + 10 + crop.x, cy + 10 + crop.y,
                                               crop.width, crop.height), 1)

        det = pygame.transform.scale(panel.subsurface(crop),
                                     (crop.width * 2, crop.height * 2))
        dx = cx + (CELL_W - det.get_width()) // 2
        dy = cy + 10 + PANEL_H + 8
        sheet.blit(det, (dx, dy))
        pygame.draw.rect(sheet, (86, 74, 52),
                         (dx, dy, det.get_width(), det.get_height()), 1)
        sheet.blit(f_num.render("junction, 2x", True, (128, 122, 148)),
                   (dx + 4, dy + det.get_height() + 2))

        ty = dy + det.get_height() + 20
        sheet.blit(f_slug.render(f"{key} · {slug}", True, accent), (cx + 14, ty))
        sheet.blit(f_body.render(thesis, True, (222, 218, 236)), (cx + 14, ty + 21))
        ok = "OK" if gp >= 6 else "CLIPS PIP"
        y_probe = 316 if key != "G" else 300
        row = gold[gold[:, 1] == y_probe]
        rope_note = "no gold at rope depth"
        if len(row):
            lr = V.rope_x_at(polys[0], y_probe)
            if lr is not None:
                rope_note = f"L-rope gap {row[:,0].min() - (lr + 2):+.0f}px @y{y_probe}"
        sheet.blit(f_num.render(
            f"Pip silhouette {gp:+.0f}px ({ok})   rope mask {gr:+.0f}px   "
            f"{rope_note}", True,
            (140, 210, 150) if gp >= 6 else (226, 128, 128)), (cx + 14, ty + 40))

    os.makedirs(os.path.dirname(path), exist_ok=True)
    pygame.image.save(sheet, path)
    print("saved", path, sheet.get_size())


if __name__ == "__main__":
    if os.environ.get("SHOWCASE"):
        build_showcase(os.path.join(
            _ROOT, "docs", "main-menu", "harbour-post", "profile-frame",
            "connected_showcase.png"))
    else:
        which = os.environ.get("OPTION", "D")
        surf, fr = PF.build(float(os.environ.get("PHASE", "0.20")),
                            OPTIONS[which][0])
        out = os.environ.get("OUT", f"/tmp/_pfc_{which}.png")
        pygame.image.save(surf, out)
        print("saved", out, fr)
