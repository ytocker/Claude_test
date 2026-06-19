"""Recipe-driven engine for the Skull-King stacked-skull PILLARS.

Generalizes render_skull_king_stack.render_half: a pillar is an ordered RECIPE of
element tokens (gap-edge -> far end) drawn from the whole skull + ornament
menagerie, with ornaments seated between skulls, plus an optional skewer in one of
five styles. Every element draw + the skewer / bead-collar / sky helpers are reused
from the existing harness so nothing is reinvented. Design-only.

Token grammar (global IDs #1-#36):
  crown:0..5  palm:0..5  r9:0|1  new:<slug>  classic:<slug>  orn:<fn>
Skewer styles: plain | gem-tip | ring-washer | barbed | strand
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


# ── skewer styles ──────────────────────────────────────────────────────────────
def _rod_plain(big, cx, ya, yb):
    """A plain DARK bone rod (no gold marrow) — the crude spit; darker value so the
    low-contrast 'plain' pillar still holds its column against a bright sky."""
    s = S_UNIT * SS
    hw = RK._SK_HW
    y, h = int(min(ya, yb)), int(abs(yb - ya))
    pygame.draw.rect(big, sk.INK, (cx - hw - int(1.4 * s), y, 2 * (hw + int(1.4 * s)), h))
    pygame.draw.rect(big, sk.BONE_D, (cx - hw, y, 2 * hw, h))
    pygame.draw.rect(big, sk.BONE_SH, (cx - hw, y, max(1, int(1.6 * s)), h))


def _skewer_bg(big, cx, y0, y1, style):
    """The shaft drawn BEHIND the stack (shows in the gaps between tiers)."""
    cx = int(cx)
    if style == "plain":
        _rod_plain(big, cx, y0, y1)
    elif style == "strand":
        s = S_UNIT * SS; hw = max(1, int(2.4 * s))      # thin dark rod, hidden by the strand
        y, h = int(min(y0, y1)), int(abs(y1 - y0))
        pygame.draw.rect(big, sk.INK, (cx - hw, y, 2 * hw, h))
    else:
        RK._rod_seg(big, cx, y0, y1)                     # bone + gold marrow


def _barbed_point(big, cx, base, tip, point_dir, long=False):
    s = S_UNIT * SS; hw = RK._SK_HW
    barb = int((15 if long else 11) * SS)
    spread = int((13 if long else 9) * SS)
    pts = [(cx, tip), (cx - hw - barb, base + point_dir * spread),
           (cx - hw, base), (cx + hw, base),
           (cx + hw + barb, base + point_dir * spread)]
    sk.triad_blob(big, sk.BONE, [(int(x), int(y)) for x, y in pts], ow=max(1, int(1.4 * s)))
    pygame.draw.line(big, sk.GOLD, (cx, int(base)), (cx, int(tip)), max(1, int(1.8 * s)))
    pygame.draw.circle(big, sk.GOLD_BR, (cx, int(tip)), max(1, int(2.2 * s)))
    if long:                                             # recurved second barbs partway up
        mid = (base + tip) // 2
        for sgn in (-1, 1):
            pygame.draw.polygon(big, sk.BONE,
                                [(cx + sgn * hw, mid),
                                 (cx + sgn * (hw + int(9 * SS)), mid + point_dir * int(7 * SS)),
                                 (cx + sgn * hw, mid + point_dir * int(5 * SS))])


def _skewer_thread(big, cx, centres, point_y, point_dir, style):
    """Drawn ON TOP of the stack: a nub at each inter-element seam + a styled tip
    jutting into the gap. Five mutually-distinct seam/tip silhouettes."""
    s = S_UNIT * SS
    cx = int(cx)
    seams = [(centres[i] + centres[i + 1]) / 2.0 for i in range(len(centres) - 1)]
    if centres:
        seams.append(centres[-1] - point_dir * (R * 0.95))     # tail past the far element
    base = (point_y + point_dir * 2) * SS
    tip = (point_y + point_dir * 26) * SS

    if style == "strand":                                # rod hidden under a chunky bead run
        ya, yb = point_y * SS, centres[-1] * SS
        n = max(2, int(abs(yb - ya) / (7 * SS)))
        pts = [(cx, ya + (yb - ya) * k / n) for k in range(n + 1)]
        sk.bead_strand(big, pts, int(3.8 * s), s, gold_every=2)
        sk.triad_circle(big, sk.BEAD, (cx, int(tip)), max(2, int(4.2 * s)), ow=max(1, int(1.0 * s)), core=False)
        return

    if style == "ring-washer":                           # flat ring-eye discs at each seam
        for ym in seams[:-1]:
            RK._ORN_MOD.ornament_necklace(big, cx, int(ym * SS), int(R * 0.40 * SS), (R * 0.40 / 12.0) * SS)
        RK._rod_seg(big, cx, base, (point_y + point_dir * 22) * SS)
        return

    rod = _rod_plain if style == "plain" else RK._rod_seg
    for ym in seams:
        rod(big, cx, (ym - 7) * SS, (ym + 7) * SS)

    if style == "plain":                                 # white beads on the rod, blunt knob tip
        for ym in seams[:-1]:
            sk.bead_strand(big, [(cx, int((ym - 5) * SS)), (cx, int((ym + 5) * SS))],
                           int(3.0 * s), s, gold_every=99)
        sk.triad_circle(big, sk.BEAD, (cx, int((point_y + point_dir * 14) * SS)),
                        max(2, int(3.4 * s)), ow=max(1, int(1.0 * s)), core=False)
    elif style == "gem-tip":                             # gold-cored rod + clean gem point (no barb)
        RK._ORN_MOD.gem_thirdeye(big, cx, int((point_y + point_dir * 16) * SS),
                                 int(R * 0.50 * SS), (R * 0.50 / 12.0) * SS)
    elif style == "barbed":                              # long recurved harpoon (owns all barbs)
        _barbed_point(big, cx, base, (point_y + point_dir * 34) * SS, point_dir, long=True)
    else:
        _barbed_point(big, cx, base, tip, point_dir, long=False)


def render_pillar_half(H, *, cap, recipe, with_skewer=False, skewer_style="plain",
                       focal_lit=True, collar=True, lean=0.0):
    """One pillar half. cap='bottom' -> TOP pillar (gap below); cap='top' -> BOTTOM
    pillar (gap above). The recipe runs gap-edge -> far end; element 0 is the focal
    skull at the gap. `collar` toggles bead seam-collars (off = blocks butt, masonry).
    `lean` (in skull-radii) jitters elements alternately left/right for an off-axis
    broken-stack look. Returns a 58xH outline-grown surface."""
    big = pygame.Surface((PIPE_W * SS, H * SS), pygame.SRCALPHA)
    cx0 = PIPE_W * SS // 2
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

    def ex(i):                                           # per-element x (lean jitter; focal stays centred)
        return cx0 + (0 if i == 0 else int(lean * R * SS) * (1 if i % 2 else -1))

    if with_skewer:
        _skewer_bg(big, cx0, gap_edge_y, int(centres[-1] * SS), skewer_style)

    for i in reversed(range(len(recipe))):               # far -> near so nearer overlaps toward the gap
        if collar and i > 0 and metas[i]["kind"] == "skull" and metas[i - 1]["kind"] == "skull":
            _collar(big, (ex(i) + ex(i - 1)) // 2, (centres[i] + centres[i - 1]) / 2.0)
        lit = (i == 0 and focal_lit and metas[i]["kind"] == "skull")
        draw_element(big, recipe[i], ex(i), centres[i] * SS, metas[i]["r"], lit=lit)

    if with_skewer:
        _skewer_thread(big, cx0, centres, focal_y, point_dir, skewer_style)

    return sk.grow_outline(pygame.transform.smoothscale(big, (PIPE_W, H)), sk.INK + (255,), 1)


def render_pair(recipe, *, with_skewer=False, skewer_style="plain", collar=True, lean=0.0,
                night=False, half_h=190, gap=150, pad=12):
    """A full top+bottom pillar pair framing the gap, composited on sky."""
    top = render_pillar_half(half_h, cap="bottom", recipe=recipe, with_skewer=with_skewer,
                             skewer_style=skewer_style, collar=collar, lean=lean)
    bot = render_pillar_half(half_h, cap="top", recipe=recipe, with_skewer=with_skewer,
                             skewer_style=skewer_style, collar=collar, lean=lean)
    H = half_h * 2 + gap
    panel = RK._sky(PIPE_W + pad * 2, H, night=night)
    panel.blit(top, (pad, 0))
    panel.blit(bot, (pad, half_h + gap))
    return panel
