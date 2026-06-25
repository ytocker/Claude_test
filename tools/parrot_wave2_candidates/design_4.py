"""design_4 · STAINED-GLASS MACAW — LEGENDARY parrot-wave2 exploration.

A cathedral window given wings — but SILHOUETTE FIRST: the bird is the clean
4-frame macaw the epics use (teardrop body, one bold wing, hooked beak, defined
tail), and the stained glass is a SURFACE applied to that silhouette, never a
replacement for it. The reader sees "red bird + jewel crown" in the outline
before a single pane resolves.

Round-2 from-the-studs rebuild of everything below the crest, designed at 40px
first:

  * ONE calm dominant field: the body stays a deep RUBY macaw (a large, readable
    red mass); sapphire/emerald/amber are reserved for a SMALL number of accent
    panes (wing fan + one chest blaze). No equal-saturation confetti.
  * Lead grid + back-light are CLIPPED to the bird's own alpha, so panes and the
    luminosity gradient can never escape the silhouette into a rainbow blob.
  * Coarse panes only at gameplay scale (≥4-5px); the finer rose-window tracery
    is HERO-GATED (detail=True) so it never renders at 40px.
  * Tail = 3 SOLID lancet panes echoing the crest inverted — long pointed
    cathedral panes, one bold colour each, hard lead outline + white pinnacle.
  * Crest WINS the crown: the rose window is demoted to a thin single-colour
    AMBER glow ring sitting BEHIND and LARGER than the crest (concentric, not
    colliding).
  * Aviators thinned to a slim smoky band on the eye line (not a black bar
    bisecting the body).
  * A SINGLE diagonal back-light gradient (bright top-left → deep bottom-right)
    across every pane sells one window lit from one side.

The gothic-arch crest (3 lancets + white pinnacle tips), the jewel palette, and
the black-came-line concept are KEPT — the wave's best legendary tell.

The halo/tail paint BEHIND the body and glow OUTSIDE the house outline, so this
uses a custom getter (aurora/viking pattern), not store_skins._make_skin's
body-first compose. Exploration only — NEVER registered in store_skins.BUILDERS.
"""
import math

import pygame

from game.parrot import _WING_ANGLES, _add_outline
from game.draw import blit_glow, lerp_color
from game.store_skins import (
    COMPOSITE_W, COMPOSITE_H, PARROT_DY, HX, HY, CROWN_Y,
)
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette


# ── palette (brief) ───────────────────────────────────────────────────────────
_RUBY    = (200, 32, 54)           # the dominant body field
_SAPPH   = (31, 95, 196)           # #1F5FC4
_EMERALD = (31, 168, 115)          # #1FA873
_AMBER   = (242, 178, 62)          # #F2B23E
_LEAD    = (21, 19, 26)            # #15131A lead line / dark came
_GLINT   = (255, 250, 235)         # back-light hotspot / pinnacle white

# Lit jewel cores (the brighter top-left of each pane under the back-light).
_RUBY_LIT    = (255, 96, 116)
_SAPPH_LIT   = (110, 170, 252)
_EMERALD_LIT = (110, 232, 182)
_AMBER_LIT   = (255, 226, 158)

# Body re-plumage: a CALM, readable deep-ruby macaw. Unlike round 1 this is NOT
# a per-slot jewel scramble — the whole body is ruby with lead-dark line work,
# so the base bird already reads as "red parrot" before any glass is applied.
# Crown is amber so the gothic crest springs from a warm window-top; the wing is
# a deeper ruby so the sapphire accent panes sit ON it without fighting. Lead
# owns every shadow/line. Lenses dropped here — the slim aviators paint later.
P_GLASS = _pal(
    tail=[_RUBY, (180, 30, 50), (160, 28, 46), (140, 26, 42)],
    tail_line=_LEAD,
    body_shadow=_LEAD,
    body_main=_RUBY,
    body_chest=(228, 60, 78),
    body_belly=(168, 30, 48),
    sheen=(255, 220, 210, 70),
    wing_main=(150, 28, 44),
    wing_dark=_LEAD,
    wing_tip=(210, 60, 76),
    wing_secondary=None,
    wing_highlight=(255, 130, 140),
    head_shadow=_LEAD,
    head_main=_RUBY,
    head_cheek=(255, 110, 124),
    head_crown=(196, 138, 40),       # amber crown → window-top
    lens_frame=(70, 66, 80),
    lens_body=(22, 20, 28),
    lens_tint=(120, 124, 138, 130),
    lens_glint=(228, 230, 238),
    beak_main=(214, 176, 96),
    beak_dark=_LEAD,
    beak_gloss=(248, 226, 168),
    foot=(70, 66, 80),
)


def _glass_base(angle_deg):
    return _build_parrot_with_palette(angle_deg, P_GLASS, draw_lenses=False)


# ── shared helpers ────────────────────────────────────────────────────────────

def _flap_phase(angle_deg):
    """0 on the down-stroke (wing 50°) → 1 on the up-stroke (-40°). The tail
    lancets fan a touch wider on the up-beat so the baked window feels alive."""
    return 1.0 - (angle_deg + 40) / 90.0


def _backlight_alpha(x, y):
    """One consistent diagonal luminosity for the whole window: bright at the
    top-left of the body, deep at the bottom-right. 0..1, so every pane shares
    the SAME light direction — the single cue that sells 'lit from one side'
    instead of a scatter of unrelated glints."""
    t = ((x - 16) + (y - 44)) / 60.0
    return max(0.0, min(1.0, 1.0 - t))


# ── back layer: amber glow ring (demoted halo) + 3 solid tail lancets ─────────

def _lancet_geo(angle_deg):
    """The 3 tail lancets for this flap angle — point lists + tips, shared by
    the additive and opaque passes so they register exactly."""
    fan = 1.0 + _flap_phase(angle_deg) * 0.10
    troot = (16, HY + 8)
    spec = (
        (-38, 31, _SAPPH,   _SAPPH_LIT),
        (-20, 36, _EMERALD, _EMERALD_LIT),
        (-2,  31, _AMBER,   _AMBER_LIT),
    )
    out = []
    for ang_deg, length, jw, lit in spec:
        a = math.radians(150 + ang_deg * fan)            # ≈ down-and-back
        ca, sa = math.cos(a), math.sin(a)
        pa = a + math.pi / 2
        px, py = math.cos(pa) * 4, math.sin(pa) * 4
        tip = (troot[0] + ca * length, troot[1] + sa * length)
        bi = (troot[0] - px, troot[1] - py)
        bo = (troot[0] + px, troot[1] + py)
        mi = (troot[0] + ca * length * 0.62 - px * 0.55,
              troot[1] + sa * length * 0.62 - py * 0.55)
        mo = (troot[0] + ca * length * 0.62 + px * 0.55,
              troot[1] + sa * length * 0.62 + py * 0.55)
        out.append(([bi, mi, tip, mo, bo], tip, troot, jw, lit))
    return out


def _glass_back(surf, angle_deg):
    """Behind the outlined bird, so the house outline never boxes the back-light
    bloom. Two passes:

      1. ADDITIVE light-spill — the amber halo ring's back-glow + a jewel bloom
         under the tail lancets (sells 'lit from behind' on night sky).
      2. OPAQUE detail — the thin amber ring + the 3 solid tail lancets bound by
         black came (carry the read on day sky where additive washes out).

    The halo is now a SINGLE thin amber ring BEHIND and LARGER than the crest so
    the two crown elements read concentric, not colliding — the crest wins, the
    ring just frames it."""
    lancets = _lancet_geo(angle_deg)
    hcx, hcy = HX - 1, HY - 4
    halo_r = 21

    # ── pass 1: additive light-spill (night) ─────────────────────────────────
    glow = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    for i in range(12):
        a = math.radians(i * 30)
        blit_glow(glow, int(hcx + math.cos(a) * halo_r),
                  int(hcy + math.sin(a) * halo_r), 6, _AMBER, alpha=85)
    for poly, tip, _root, jw, lit in lancets:
        blit_glow(glow, int(tip[0]), int(tip[1]), 6, lit, alpha=115)
        blit_glow(glow, int(poly[1][0]), int(poly[1][1]), 5, jw, alpha=90)
    surf.blit(glow, (0, 0), special_flags=pygame.BLEND_ADD)

    # ── pass 2: opaque detail (day + night) ──────────────────────────────────
    det = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)

    # Tail lancets first (lowest), so the body overlaps their roots → they read
    # as tail plumage, not a fan pinned behind. Each: thick lead came, a solid
    # jewel field shrunk inside the came as a rim, a lit spine, a white pinnacle.
    for poly, tip, root, jw, lit in lancets:
        pygame.draw.polygon(det, _LEAD, poly)
        cx = sum(p[0] for p in poly) / len(poly)
        cy = sum(p[1] for p in poly) / len(poly)
        field = [(cx + (x - cx) * 0.74, cy + (y - cy) * 0.80) for x, y in poly]
        pygame.draw.polygon(det, jw, field)
        pygame.draw.line(det, lit, root, (int(tip[0]), int(tip[1])), 2)
        pygame.draw.circle(det, _GLINT, (int(tip[0]), int(tip[1])), 2)

    # Demoted halo — a single thin AMBER band behind+larger than the crest: a
    # dark came under-stroke, the amber ring over it, two lit beads on the flanks
    # where it clears the silhouette (the legendary back-lit tell, kept quiet).
    pygame.draw.circle(det, _LEAD, (hcx, hcy), halo_r, 4)
    pygame.draw.circle(det, _AMBER, (hcx, hcy), halo_r, 2)
    for fa in (math.radians(205), math.radians(335)):
        bx = int(hcx + math.cos(fa) * halo_r)
        by = int(hcy + math.sin(fa) * halo_r)
        pygame.draw.circle(det, _AMBER_LIT, (bx, by), 2)
        pygame.draw.circle(det, _GLINT, (bx, by), 1)

    surf.blit(det, (0, 0))


# ── glass surface: lead grid + back-light, CLIPPED to the bird's alpha ────────

def _clip_to_mask(surf, mask):
    """Zero every pixel of `surf` outside the bird's alpha mask, so a glass coat
    can never paint past the silhouette."""
    keep = mask.to_surface(setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0))
    surf.blit(keep, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)


def _pane(surf, pts, jewel, lit, *, field=True):
    """One leaded facet bound by a crisp lead came. field=True fills a jewel
    field + a single lit dot toward the top-left (the shared back-light side);
    field=False draws ONLY the came outline (to grid the dominant ruby field
    without recolouring it)."""
    if field:
        pygame.draw.polygon(surf, jewel, pts)
        tlx = min(p[0] for p in pts)
        tly = min(p[1] for p in pts)
        pygame.draw.circle(surf, lit, (int(tlx + 3), int(tly + 3)), 1)
    pygame.draw.polygon(surf, _LEAD, pts, 1)


def _apply_glass_surface(bird, angle_deg, *, detail=False):
    """The stained-glass treatment as a SURFACE over the already-drawn ruby
    body, clipped to the body's own alpha mask so nothing escapes the
    silhouette. Two coats, both masked:

      * a single diagonal back-LIGHT gradient (bright top-left → deep
        bottom-right) so the whole body reads as one window lit from one side;
      * a COARSE lead-came grid (few big panes) + a SMALL number of jewel accent
        panes (sapphire wing fan, one amber chest blaze) — the only non-ruby
        colour, so from across the room it reads 'red bird + jewel accents'.

    `detail=True` adds finer rose-tracery — HERO-ONLY, so the gameplay/40px read
    never sees the fine mosaic that muds out small."""
    mask = pygame.mask.from_surface(bird)
    bb = bird.get_bounding_rect()

    # ── coat 1: one diagonal back-light gradient ─────────────────────────────
    light = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    for yy in range(bb.top, bb.bottom, 2):
        for xx in range(bb.left, bb.right, 2):
            a = _backlight_alpha(xx, yy)
            if a > 0.04:
                light.fill((255, 248, 232, int(70 * a)), pygame.Rect(xx, yy, 2, 2))
    _clip_to_mask(light, mask)
    bird.blit(light, (0, 0))

    grid = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)

    # Sapphire WING accent — 2 big sapphire panes + 1 emerald echoing the wing
    # fan. The dominant non-ruby note; kept cool so it reads as one wing window.
    _pane(grid, [(25, 46), (34, 42), (37, 49), (28, 52)], _SAPPH, _SAPPH_LIT)
    _pane(grid, [(34, 42), (45, 42), (46, 49), (37, 49)], _SAPPH, _SAPPH_LIT)
    _pane(grid, [(28, 52), (37, 49), (43, 53), (33, 56)], _EMERALD, _EMERALD_LIT)

    # ONE amber chest BLAZE — a single bold accent pane on the breast, the warm
    # focal point that draws the eye to the bird's front.
    _pane(grid, [(43, 49), (52, 48), (53, 57), (44, 59)], _AMBER, _AMBER_LIT)

    # COARSE ruby came grid over the rest — a few big lead lines dividing the
    # dominant red field into readable panes WITHOUT recolouring it, so the
    # silhouette never fragments.
    for seg in (
        [(16, 52), (24, 49), (30, 54), (24, 60)],
        [(24, 60), (30, 54), (40, 58), (34, 64)],
        [(44, 59), (53, 57), (52, 64), (43, 64)],
    ):
        _pane(grid, seg, _RUBY, _RUBY_LIT, field=False)

    if detail:
        # HERO-ONLY finer tracery: split the big accent panes with extra came so
        # the close-up shows true rose-window density. NEVER at gameplay/40px.
        for ax, ay, bx2, by2 in (
            (34, 42, 34, 49), (37, 49, 43, 53), (48, 48, 49, 57), (28, 52, 33, 56)
        ):
            pygame.draw.line(grid, _LEAD, (ax, ay), (bx2, by2), 1)
        for cx2, cy2, jw in ((31, 47, _SAPPH_LIT), (40, 45, _SAPPH_LIT),
                             (48, 53, _AMBER_LIT)):
            pygame.draw.circle(grid, jw, (cx2, cy2), 1)

    _clip_to_mask(grid, mask)
    bird.blit(grid, (0, 0))


# ── front overlay: gothic-arch crest + slim aviators ─────────────────────────

def _glass_front(bird, angle_deg):
    """Crisp opaque detail painted OVER the glassed body and INSIDE the mask:
    the hero gothic-arch crest past the crown and the slim re-tinted aviators.
    (Soft back-light lives in _glass_back to dodge the outline.)"""
    # Gothic-arch CREST — KEPT: three tall pointed lancets rising past the crown
    # like a window top, lead-edged, ruby/sapphire/emerald left→right, white
    # pinnacle tips. Centre tallest. The wave's best legendary tell, untouched.
    base_y = CROWN_Y + 2
    pygame.draw.line(bird, _LEAD, (HX - 11, base_y), (HX + 11, base_y - 2), 3)
    for dx, h, jw, lit in (
        (-8, 13, _RUBY, _RUBY_LIT),
        (0, 19, _SAPPH, _SAPPH_LIT),
        (8, 13, _EMERALD, _EMERALD_LIT),
    ):
        bx = HX + dx
        ty = base_y - h
        pts = [(bx - 4, base_y), (bx - 4, ty + 5), (bx, ty),
               (bx + 4, ty + 5), (bx + 4, base_y)]
        pygame.draw.polygon(bird, jw, pts)
        pygame.draw.polygon(bird, _LEAD, pts, 1)
        pygame.draw.line(bird, lit, (bx, ty + 3), (bx, base_y - 2), 1)
        pygame.draw.circle(bird, _GLINT, (bx, ty + 1), 2)     # white pinnacle tip

    # Slim SMOKY aviators — ~40% thinner than the baked lenses, lifted to a slim
    # band on the eye line only, so at 40px they read as a thin shade line, not a
    # black bar bisecting the body. Two short smoky lenses + a thin bridge.
    ex, ey = HX + 3, HY - 3
    for lx in (ex - 5, ex + 4):
        pygame.draw.ellipse(bird, (28, 26, 34), (lx - 4, ey - 2, 8, 5))
        pygame.draw.ellipse(bird, (120, 124, 138), (lx - 3, ey - 1, 6, 2))
    pygame.draw.line(bird, (40, 38, 48), (ex - 1, ey), (ex, ey), 2)
    pygame.draw.circle(bird, _GLINT, (ex - 6, ey - 1), 1)     # single bright glint
    # A sharp came line on the beak so the directional hooked beak stays crisp.
    pygame.draw.line(bird, _LEAD, (HX + 8, HY + 1), (HX + 13, HY + 4), 1)


# ── custom compose + getter (halo/tail need a back layer) ─────────────────────

def _make_getter(detail):
    """back layer (amber ring + 3 lancets) → ruby body → glass surface (clipped)
    → front (crest, slim aviators) → house outline → per-(frame, 3°) rotation
    cache. `detail` gates the hero-only fine tracery."""
    state = {"frames": None, "rot": {}}

    def _flat(wing_angle):
        # Outline the OPAQUE bird alone (so the faint additive back-light isn't
        # boxed by the dark rim), then lay the back layer UNDER it. The outline
        # pads by 2px; the back surface is padded to match so the bird stays
        # centred for the rotation maths.
        bird = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
        bird.blit(_glass_base(wing_angle), (0, PARROT_DY))
        _apply_glass_surface(bird, wing_angle, detail=detail)
        _glass_front(bird, wing_angle)
        bird = _add_outline(bird)

        full = pygame.Surface(bird.get_size(), pygame.SRCALPHA)
        pad = (bird.get_width() - COMPOSITE_W) // 2
        back = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
        _glass_back(back, wing_angle)
        full.blit(back, (pad, pad))
        full.blit(bird, (0, 0))
        return full

    def getter(frame_idx, tilt_deg):
        if state["frames"] is None:
            state["frames"] = [_flat(a) for a in _WING_ANGLES]
        frames = state["frames"]
        frame_idx %= len(frames)
        key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
        s = state["rot"].get(key)
        if s is None:
            s = pygame.transform.rotozoom(frames[frame_idx], key[1], 1.0)
            state["rot"][key] = s
        return s

    return getter


# Gameplay/40px build: coarse panes only. `build_hero` adds the fine tracery
# that would mud out at small sizes, so the close-up can show true density.
build = _make_getter(detail=False)
build_hero = _make_getter(detail=True)
