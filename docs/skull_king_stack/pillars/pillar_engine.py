"""Recipe-driven engine for the Skull-King stacked-skull PILLARS.

Generalizes render_skull_king_stack.render_half: a pillar is an ordered RECIPE of
element tokens (gap-edge -> far end) drawn from the whole skull + ornament
menagerie, with ornaments seated between skulls, plus an optional skewer in one of
several styles. Every element draw + the skewer / bead-collar / sky helpers are
reused from the existing harness so nothing is reinvented. Design-only.

Token grammar (global IDs #1-#36):
  crown:0..5  palm:0..5  r9:0|1  new:<slug>  classic:<slug>  orn:<fn>
"""
import os, sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy"); os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = "/home/user/skybit"
sys.path.insert(0, os.path.join(ROOT, "tools"))
import pygame
import render_skull_king_stack as RK     # loads the element draws + skewer/collar/sky helpers
sk = RK.sk

SS, PIPE_W, R, S_UNIT = RK.SS, RK.PIPE_W, RK.R, RK.S_UNIT

_BEAD_FNS = {"bead_white", "bead_gold", "bead_cyan", "bead_darkblue"}


def _meta(token):
    """Final-px radius + role for one element. Skulls host bead collars + can be the
    lit focal; ornaments are smaller in-line tiers / seam-joints."""
    if token.startswith("orn:"):
        fn = token.split(":", 1)[1]
        if fn in _BEAD_FNS:
            return dict(kind="bead", r=R * 0.30)
        if fn == "gem_thirdeye":
            return dict(kind="gem", r=R * 0.54)
        return dict(kind="ring", r=R * 0.58)        # ornament_necklace
    return dict(kind="skull", r=R * 0.96)


def draw_element(big, token, cx, cy, r_px, lit=False):
    """Dispatch a token to its existing draw fn. r_px is the final-px radius; it is
    converted to the supersampled `big` surface here (r = r_px*SS, s = r_px/12*SS)."""
    r = max(1, int(r_px * SS))
    s = (r_px / 12.0) * SS
    cx, cy = int(cx), int(cy)
    if token.startswith("crown:"):
        RK._crown_skull_straight(big, cx, cy, r, s, lit=lit, idx=int(token.split(":")[1]))
    elif token.startswith("palm:"):
        RK._palm_skull_bare(big, cx, cy, r, s, idx=int(token.split(":")[1]))
    elif token.startswith("r9:"):
        RK._crown_skull_orig(big, cx, cy, r, s, lit=bool(int(token.split(":")[1])))
    elif token.startswith("new:"):
        RK._NEW8[token.split(":", 1)[1]][0](big, cx, cy, r, s, lit)
    elif token.startswith("classic:"):
        RK._CLASSIC8[token.split(":", 1)[1]][0](big, cx, cy, r, s, lit)
    elif token.startswith("orn:"):
        getattr(RK._ORN_MOD, token.split(":", 1)[1])(big, cx, cy, r, s)
    else:
        raise ValueError("unknown element token: " + token)


def _collar(big, cx, y_small):
    """The thin gold-pip bone-bead collar seating one skull on the next (the design's
    tell), at small-coord seam y."""
    sk.bead_strand(big, [(cx - int(R * 0.8 * SS), int(y_small * SS)),
                         (cx + int(R * 0.8 * SS), int(y_small * SS))],
                   int(2.6 * S_UNIT * SS), S_UNIT * SS, gold_every=2)


def _skewer_thread(big, cx, centres, point_y, point_dir, style):
    """The skewer drawn ON TOP: a rod nub at each inter-element seam + a styled tip
    jutting into the gap. Reuses RK._rod_seg / RK._SK_HW and the ornament module."""
    s = S_UNIT * SS
    cx = int(cx)
    seams = [(centres[i] + centres[i + 1]) / 2.0 for i in range(len(centres) - 1)]
    if centres:
        seams.append(centres[-1] - point_dir * (R * 0.95))     # tail past the far element

    if style == "ring-washer":
        for ym in seams[:-1]:
            RK._ORN_MOD.ornament_necklace(big, cx, int(ym * SS), int(R * 0.40 * SS), (R * 0.40 / 12.0) * SS)
        RK._rod_seg(big, cx, (point_y + point_dir * 2) * SS, (point_y + point_dir * 22) * SS)
        return

    for ym in seams:
        RK._rod_seg(big, cx, (ym - 7) * SS, (ym + 7) * SS)
    if style == "beaded":
        for ym in seams[:-1]:
            sk.bead_strand(big, [(cx, int((ym - 5) * SS)), (cx, int((ym + 5) * SS))],
                           int(3.0 * s), s, gold_every=2)

    # the tip at the gap end
    if style == "gem-tip":
        RK._ORN_MOD.gem_thirdeye(big, cx, int((point_y + point_dir * 16) * SS),
                                 int(R * 0.50 * SS), (R * 0.50 / 12.0) * SS)
        return
    hw = RK._SK_HW
    tip = (point_y + point_dir * 26) * SS
    base = (point_y + point_dir * 2) * SS
    barb = int(11 * SS)
    pts = [(cx, tip), (cx - hw - barb, base + point_dir * int(9 * SS)),
           (cx - hw, base), (cx + hw, base),
           (cx + hw + barb, base + point_dir * int(9 * SS))]
    sk.triad_blob(big, sk.BONE, [(int(x), int(y)) for x, y in pts], ow=max(1, int(1.4 * s)))
    gold = sk.GOLD_BR if style == "gold" else sk.GOLD
    pygame.draw.line(big, gold, (cx, int(base)), (cx, int(tip)), max(1, int(1.8 * s)))
    pygame.draw.circle(big, sk.GOLD_BR, (cx, int(tip)), max(1, int(2.2 * s)))


def render_pillar_half(H, *, cap, recipe, with_skewer=False, skewer_style="bone", focal_lit=True):
    """One pillar half. cap='bottom' -> TOP pillar (gap below); cap='top' -> BOTTOM
    pillar (gap above). The recipe runs gap-edge -> far end; element 0 is the focal
    skull at the gap. Returns a 58xH outline-grown surface."""
    big = pygame.Surface((PIPE_W * SS, H * SS), pygame.SRCALPHA)
    cx = PIPE_W * SS // 2
    metas = [_meta(t) for t in recipe]
    margin = int(R * 1.05)
    if cap == "bottom":
        focal_y, step, point_dir, gap_edge_y = H - margin, -1, +1, H * SS
    else:
        focal_y, step, point_dir, gap_edge_y = margin, +1, -1, 0

    centres = [focal_y]
    for i in range(1, len(recipe)):
        spacing = (metas[i - 1]["r"] + metas[i]["r"]) * 0.84
        centres.append(centres[-1] + step * spacing)

    if with_skewer:
        RK._rod_seg(big, cx, gap_edge_y, int(centres[-1] * SS))     # shaft behind everything

    # far -> near so nearer elements overlap on top toward the gap
    for i in reversed(range(len(recipe))):
        if i > 0 and metas[i]["kind"] == "skull" and metas[i - 1]["kind"] == "skull":
            _collar(big, cx, (centres[i] + centres[i - 1]) / 2.0)
        lit = (i == 0 and focal_lit and metas[i]["kind"] == "skull")
        draw_element(big, recipe[i], cx, centres[i] * SS, metas[i]["r"], lit=lit)

    if with_skewer:
        _skewer_thread(big, cx, centres, focal_y, point_dir, skewer_style)

    return sk.grow_outline(pygame.transform.smoothscale(big, (PIPE_W, H)), sk.INK + (255,), 1)


def render_pair(recipe, *, with_skewer=False, skewer_style="bone",
                night=False, half_h=190, gap=150, pad=12):
    """A full top+bottom pillar pair framing the gap, composited on sky."""
    top = render_pillar_half(half_h, cap="bottom", recipe=recipe,
                             with_skewer=with_skewer, skewer_style=skewer_style)
    bot = render_pillar_half(half_h, cap="top", recipe=recipe,
                             with_skewer=with_skewer, skewer_style=skewer_style)
    H = half_h * 2 + gap
    panel = RK._sky(PIPE_W + pad * 2, H, night=night)
    panel.blit(top, (pad, 0))
    panel.blit(bot, (pad, half_h + gap))
    return panel
