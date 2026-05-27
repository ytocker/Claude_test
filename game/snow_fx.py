"""Windblown snow that accumulates on Pip during the predawn snow squall.

Chosen design: **W2 "sculpted blanket"** from the tools/sketch_snow_accum.py
exploration. The squall is a tailwind (blows left->right), so snow builds on
Pip's rear/left-facing surfaces first and spreads forward + inward as the storm
grows, keeping his face readable. Real-snow cues: rear end tapers to a point
(no hard wall), a gentle inward pile (not just an outline rim), a bright crest
highlight, and a cool-blue shadowed underside.

Overlays are baked per (frame, load-bucket) onto the native parrot frame using
its own alpha silhouette, then cached — so per-frame cost in Bird.draw is just
a rotozoom + blit (pure pygame, no numpy; WASM-safe). Bird.draw applies the
SAME rotozoom(tilt) the sprite gets, so the snow stays glued to Pip.
"""
from __future__ import annotations

import math

import pygame

from game import parrot

# Snow depth + palette (sprite px; W2 tuning from the sketch).
MAXD = 21.0
CORNICE = 1.6
WHITE = (255, 255, 255)
OFF = (236, 244, 252)
BLUE = (188, 206, 230)           # cool shadowed underside
SHADOW = (150, 168, 198)
_BUCKET = 0.06                    # load quantisation for the cache

_topline_cache: dict = {}
_overlay_cache: dict = {}


def _smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def _cov(xf, load):
    """Rear-first coverage: rear (left) columns snow at low load, the front
    only as the storm builds."""
    thr = 0.55 * xf
    return 0.0 if load <= thr else min(1.0, (load - thr) / (1.0 - thr))


def _topline(frame_idx):
    """First opaque row per column of the native frame (the top silhouette),
    plus the leftmost occupied column. Cached per frame; no numpy."""
    cached = _topline_cache.get(frame_idx)
    if cached is not None:
        return cached
    frame = parrot._get_frames()[frame_idx]
    w, h = frame.get_size()
    mask = pygame.mask.from_surface(frame, 50)
    top = [-1] * w
    x_min = -1
    for x in range(w):
        for y in range(h):
            if mask.get_at((x, y)):
                top[x] = y
                if x_min < 0:
                    x_min = x
                break
    _topline_cache[frame_idx] = (top, x_min, w, h)
    return _topline_cache[frame_idx]


def get_snow_overlay(frame_idx, load):
    """Cached W2 snow overlay (same size as the native frame) for this frame +
    load. Returns None when there's no meaningful snow yet."""
    frame_idx %= len(parrot._get_frames())
    if load <= 0.04:
        return None
    b = round(load / _BUCKET) * _BUCKET
    key = (frame_idx, b)
    cached = _overlay_cache.get(key)
    if cached is not None:
        return cached

    top, x_min, w, h = _topline(frame_idx)
    if x_min < 0:
        _overlay_cache[key] = None
        return None
    ov = pygame.Surface((w, h), pygame.SRCALPHA)
    taper_w = 13.0
    drew = False
    for x in range(w):
        yt = top[x]
        if yt < 0:
            continue
        xf = x / w
        cov = _cov(xf, b)
        if cov <= 0.0:
            continue
        rear = 1.0 - xf
        bulge = math.exp(-((xf - 0.40) / 0.26) ** 2)        # inward hump
        d = MAXD * cov * (0.50 + 0.45 * rear + 0.45 * bulge)
        if xf > 0.60:                                       # thin crown cap (face clear)
            d = min(d, 7.0)
        d *= _smooth((x - x_min) / taper_w)                 # rear-end slope
        if d < 0.6:
            continue
        over = CORNICE * rear * _smooth((x - x_min) / taper_w)
        nb = (math.sin(x * 1.26) + math.sin(x * 0.34)) * 0.25 + 0.5
        y0 = yt - over
        y1 = yt + d + (nb - 0.5) * 2.4
        # W2 sculpted blanket: clean fill + bright crest + cool under-edge.
        pygame.draw.line(ov, (*OFF, 255), (x, int(y0)), (x, int(y1)), 1)
        pygame.draw.line(ov, (*WHITE, 255), (x, int(y0)), (x, int(y0 + d * 0.18)), 1)
        pygame.draw.line(ov, (*BLUE, 255), (x, int(y1 - d * 0.26)), (x, int(y1)), 1)
        drew = True
    if not drew:
        _overlay_cache[key] = None
        return None
    _overlay_cache[key] = ov
    return ov
