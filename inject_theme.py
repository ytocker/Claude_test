#!/usr/bin/env python3
"""
Post-process pygbag's generated build/web/index.html to add the Skybit
chrome (loading splash, themed progress bar, name-entry overlay) and the
JS bridge that connects the WASM-side Python game to the browser
(leaderboard submit/fetch, telemetry log, Web Audio playback).

Contracts the game/Python code depends on (do not change without
updating the corresponding Python callers):

  window.__sk(action, payload)       — see game/leaderboard.py, game/play_log.py
      actions: submit / submit_done / fetch / fetch_done / fetch_error /
               log    / log_done
  window.skyPlay(name, volume)       — see game/audio.py
  window.openNameEntry()             — see game/leaderboard.py
  window._pendingName                — string sentinel, polled at 50 ms by
                                       game/leaderboard.py until != '__pending__'
  window.skybitGameReady             — set true by game/scenes.py first frame
  window.MM.UME                      — set true here on splash dismiss
  __SB_URL__ / __SB_KEY__            — build-time substitutions from env

NAME ENTRY (the redesign):

The previous implementation used <input id="name-input"> and was unfixably
flaky on iOS Safari: every short tap raced SDL's window-level click
listener, the canvas re-grabbed focus, and the soft keyboard dismissed.
Eight patch attempts (canvas-focus override, dialog showModal, mouse/
touch shield at three different phases, canvas inert observer, deferred-
focus removal, max z-index lift) all failed or were reverted.

This rewrite eliminates the underlying contention by removing the
<input> entirely. The name overlay now hosts a 7-column on-screen
virtual keyboard rendered as <button> elements (A-Z + space + ⌫ + ↵ +
SKIP). Tapping a letter appends to a private buffer; ⌫ removes; ↵
submits; SKIP cancels. The iOS soft keyboard is never invoked. SDL's
click listener still fires for canvas clicks (gameplay) but every
overlay click lands on a <button>, which natively absorbs the synthetic-
click race. No focus(), no MutationObserver, no shield IIFEs.
"""
import os
import re
import sys
from pathlib import Path

src = Path("build/web/index.html")
if not src.exists():
    raise SystemExit("build/web/index.html not found — run pygbag first")

html = src.read_text(encoding="utf-8")

_SB_URL = os.environ.get("SUPABASE_URL", "")
_SB_KEY = os.environ.get("SUPABASE_ANON_KEY", "")

# Track how many color/background replacements actually matched. The post-
# write assertions below treat zero matches as a build failure: it almost
# always means pygbag changed its template and the user is about to be
# served the unthemed default progress bar (green rectangle, blue text)
# — observed in production as a stuck-loading state.
_color_subs = 0


def _patch_re(pattern, replacement, html_in):
    global _color_subs
    new, n = re.subn(pattern, replacement, html_in)
    _color_subs += n
    return new


def _patch_str(needle, replacement, html_in):
    global _color_subs
    _color_subs += html_in.count(needle)
    return html_in.replace(needle, replacement)


# ── 1. Patch pygbag's default loader chrome to the Skybit palette ────────────
# These also keep _color_subs > 0 so the post-write assertion fires
# correctly when pygbag's template drifts.
html = _patch_str("background-color:powderblue", "background-color:#0d0820", html)
html = re.sub(
    r'(<canvas\b[^>]*style=["\'])([^"\']*)',
    lambda m: m.group(1) + "background:#0d0820;" + m.group(2),
    html,
)
html = _patch_str('"#7f7f7f"', '"#0d0820"', html)
html = _patch_re(r'\(\s*0\s*,\s*255\s*,\s*0\s*\)',  '(240,192,64)', html)
html = _patch_re(r'\(\s*10\s*,\s*10\s*,\s*10\s*\)', '(20,12,48)',   html)
html = _patch_re(r',\s*True\s*,\s*"blue"\)',        ', True, (240,192,64))', html)
html = _patch_str('"powderblue"',                   '"#0d0820"', html)
html = _patch_str("'powderblue'",                   "'#0d0820'", html)


# ── 2. HTML overlays injected after <body> ───────────────────────────────────
# The decorative twin-mountain SVG appears on both overlays; declare once
# as a Python constant so the same paths render in both places.
_MOUNTAINS_SVG = """\
<svg class="sk-mountains" viewBox="0 0 1440 200" preserveAspectRatio="none"
     xmlns="http://www.w3.org/2000/svg">
  <path d="M0,200 L0,130 L60,70 L120,110 L200,40 L280,90 L360,20
           L440,75 L520,45 L600,100 L680,15 L760,80 L840,35 L920,95
           L1000,50 L1080,85 L1160,25 L1240,90 L1320,55 L1440,70 L1440,200 Z"
        fill="#0e1a0c" opacity="0.95"/>
  <path d="M0,200 L0,155 L80,125 L160,145 L240,108 L320,132 L400,95
           L480,128 L560,105 L640,135 L720,88 L800,120 L880,100 L960,130
           L1040,110 L1120,138 L1200,105 L1280,128 L1360,112 L1440,125 L1440,200 Z"
        fill="#0a1208" opacity="0.75"/>
</svg>
"""

LOADING_HTML = """
<div id="skybit-loading">
  <p class="sk-title">SKYBIT</p>
  <p class="sk-subtitle">Pocket Sky Flyer</p>
  <div class="sk-progress" aria-hidden="true">
    <div id="sk-progress-fill" class="sk-progress-fill"></div>
  </div>
  <p id="sk-status" class="sk-status"></p>
""" + _MOUNTAINS_SVG + """\
</div>
"""

# Virtual keyboard rows. QWERTY layout — what every iPhone / Android
# user already has muscle memory for. Top row 10 letters, middle 9
# (visually offset half a key), bottom 7 letters with SHIFT on the
# left and BACKSPACE on the right (the natural positions on a real
# soft keyboard).
_KBD_ROWS = [
    list("QWERTYUIOP"),
    list("ASDFGHJKL"),
    list("ZXCVBNM"),
]


def _kbd_buttons():
    parts = []

    def _letter(ch):
        return ('<button class="sk-key" data-k="{c}" '
                'aria-label="{c}">{c}</button>').format(c=ch)

    # Row 1: Q-P (10 letters, full width).
    parts.append('<div class="sk-kbd-row">')
    for ch in _KBD_ROWS[0]:
        parts.append(_letter(ch))
    parts.append('</div>')

    # Row 2: A-L (9 letters, half-key inset on each side so it reads
    # as the staggered QWERTY middle row.)
    parts.append('<div class="sk-kbd-row sk-kbd-row-mid">')
    for ch in _KBD_ROWS[1]:
        parts.append(_letter(ch))
    parts.append('</div>')

    # Row 3: SHIFT + Z-M (7 letters) + BACKSPACE. Shift on the left,
    # backspace on the right — same positions as iOS/Android.
    parts.append('<div class="sk-kbd-row">')
    parts.append(
        '<button class="sk-key sk-shift" data-act="shift" '
        'aria-label="shift">&#x21e7;</button>'
    )
    for ch in _KBD_ROWS[2]:
        parts.append(_letter(ch))
    parts.append(
        '<button class="sk-key sk-special sk-back" data-act="back" '
        'aria-label="delete">&#x232b;</button>'
    )
    parts.append('</div>')

    # Row 4: SPACE — full width, like a real spacebar.
    parts.append('<div class="sk-kbd-row">')
    parts.append(
        '<button class="sk-key sk-special sk-space" data-act="space" '
        'aria-label="space">SPACE</button>'
    )
    parts.append('</div>')

    # Row 5: SUBMIT — full width, below the keyboard. SKIP is rendered
    # OUTSIDE the keyboard, pinned to the bottom of the overlay.
    parts.append('<div class="sk-kbd-row">')
    parts.append(
        '<button class="sk-key sk-special sk-enter" data-act="enter" '
        'aria-label="submit">SUBMIT</button>'
    )
    parts.append('</div>')

    return "\n      ".join(parts)


NAME_HTML = """
<div id="sk-name-overlay" aria-hidden="true">
""" + _MOUNTAINS_SVG + """\
  <svg class="sk-trophy" viewBox="0 0 60 72"
       xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
    <path d="M10 18 Q 3 18 3 26 Q 3 35 11 36" fill="none"
          stroke="#f0c040" stroke-width="3" stroke-linecap="round"/>
    <path d="M50 18 Q 57 18 57 26 Q 57 35 49 36" fill="none"
          stroke="#f0c040" stroke-width="3" stroke-linecap="round"/>
    <polygon points="9,14 51,14 47,42 13,42"
             fill="#f0c040" stroke="#8c5a08" stroke-width="1.2"/>
    <line x1="14" y1="16" x2="46" y2="16" stroke="#fff8c8" stroke-width="1.2"/>
    <rect x="27" y="42" width="6" height="11"
          fill="#f0c040" stroke="#8c5a08" stroke-width="1"/>
    <rect x="18" y="53" width="24" height="5"
          fill="#f0c040" stroke="#8c5a08" stroke-width="1"/>
    <rect x="14" y="58" width="32" height="5"
          fill="#f0c040" stroke="#8c5a08" stroke-width="1"/>
  </svg>
  <p class="sk-name-title">NEW HIGH SCORE!</p>
  <div class="sk-buf-row">
    <span class="sk-prompt">&gt;</span>
    <span id="sk-buf" aria-live="polite">_ _ _ _ _ _ _ _ _ _</span>
    <span id="sk-counter">0 / 10</span>
  </div>
  <div class="sk-kbd" id="sk-kbd">
      """ + _kbd_buttons() + """
  </div>
  <button id="sk-skip" class="sk-key sk-special" data-act="skip"
          aria-label="skip">SKIP</button>
</div>
"""

html = html.replace("<body>", "<body>\n" + LOADING_HTML + NAME_HTML, 1)


# ── 3. CSS + JS injected before </body> ──────────────────────────────────────
# Single string assembled from concern-scoped fragments below. Each JS
# fragment is its own IIFE that exposes only the documented contract on
# window — the previous monolithic script ran 1500 lines in one closure
# and accumulated eight months of patches.

_CSS = """\
<style>
canvas { background: #0d0820 !important; }
body   { background: #0d0820 !important; }

/* ── Loading overlay ─────────────────────────────────────────────────────
   Pinned to the maximum reachable z-index with !important: pygbag has
   shipped templates whose own status div / canvas ended up above
   ours, and the user only sees a stuck unthemed pygbag default. */
#skybit-loading {
    position: fixed !important;
    inset: 0 !important;
    z-index: 2147483647 !important;
    background: linear-gradient(180deg, #060115 0%, #12082a 45%, #0c1022 100%) !important;
    display: flex !important;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    user-select: none;
    overflow: hidden;
    visibility: visible !important;
    opacity: 1;
    -webkit-tap-highlight-color: transparent;
}

/* Twinkling stars (created by JS once the overlay is in DOM). */
.sk-star {
    position: absolute;
    background: #ffffff;
    border-radius: 50%;
    pointer-events: none;
    animation: sk-twinkle var(--dur, 2s) ease-in-out infinite;
    animation-delay: var(--delay, 0s);
}
@keyframes sk-twinkle {
    0%, 100% { opacity: 0.12; transform: scale(1.0); }
    50%       { opacity: 0.95; transform: scale(1.4); }
}

.sk-title {
    font-family: Arial Black, Arial, sans-serif;
    font-size: clamp(54px, 14vw, 90px);
    font-weight: 900;
    letter-spacing: 8px;
    color: #f0c040;
    margin: 0;
    text-shadow:
        -3px  0   0 #a82010,
         3px  0   0 #a82010,
         0   -3px 0 #a82010,
         0    3px 0 #a82010,
         0    9px 8px rgba(0, 0, 0, 0.85);
    animation: sk-float 3.4s ease-in-out infinite;
    pointer-events: none;
    visibility: visible !important;
    opacity: 1 !important;
}
@keyframes sk-float {
    0%, 100% { transform: translateY(0px);   }
    50%       { transform: translateY(-14px); }
}

.sk-subtitle {
    font-family: Arial, sans-serif;
    /* Fixed px, NOT clamp(): the user reports the previous clamp-based
       sizes appeared unchanged on their device. A fixed value makes
       cache-vs-fresh easy to tell from one look — if the subtitle is
       still big, the page is cached. */
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 4px;
    color: #d8b855;
    margin: 8px 0 56px;
    opacity: 0.75;
    text-transform: uppercase;
    pointer-events: none;
}

.sk-cta {
    font-family: Arial Black, Arial, sans-serif;
    font-size: clamp(13px, 3.6vw, 18px);
    font-weight: 900;
    letter-spacing: 4px;
    color: #ffffff;
    background: linear-gradient(180deg, #c84018 0%, #7e1c02 100%);
    border: 2px solid #e86828;
    border-radius: 60px;
    padding: 16px 52px;
    box-shadow:
        0 5px 30px rgba(200, 64, 20, 0.65),
        inset 0 1px 0 rgba(255, 255, 255, 0.18);
    animation: sk-pulse 1.8s ease-in-out infinite;
    pointer-events: none;
    white-space: nowrap;
}
@keyframes sk-pulse {
    0%, 100% { opacity: 0.70; transform: scale(1.00); }
    50%       { opacity: 1.00; transform: scale(1.07); }
}

.sk-progress {
    position: relative;
    width: clamp(180px, 56vw, 340px);
    height: 4px;
    margin: 22px 0 0;
    background: rgba(255, 255, 255, 0.08);
    border-radius: 2px;
    overflow: hidden;
    pointer-events: none;
}
.sk-progress-fill {
    height: 100%;
    width: 0%;
    background: linear-gradient(90deg, #b88a2e 0%, #f0c040 50%, #fff0b0 100%);
    border-radius: inherit;
    transition: width 0.55s cubic-bezier(0.22, 1, 0.36, 1);
    box-shadow: 0 0 10px rgba(240, 192, 64, 0.55);
}
.sk-progress-fill.sk-stalled {
    background: linear-gradient(90deg, #6a3a1a 0%, #a85a2a 100%);
    box-shadow: 0 0 8px rgba(168, 90, 42, 0.45);
    animation: sk-stall 1.6s ease-in-out infinite;
}
@keyframes sk-stall {
    0%, 100% { opacity: 0.55; }
    50%       { opacity: 1.00; }
}

.sk-status {
    font-family: Arial, sans-serif;
    font-size: clamp(11px, 2.6vw, 13px);
    font-weight: 600;
    letter-spacing: 2px;
    color: #d8b855;
    opacity: 0.7;
    margin: 18px 0 0;
    min-height: 1em;
    pointer-events: none;
    text-transform: uppercase;
    text-align: center;
}

.sk-mountains {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    width: 100%;
    pointer-events: none;
}

/* ── Name-entry overlay (virtual keyboard) ──────────────────────────────── */
#sk-name-overlay {
    position: fixed;
    inset: 0;
    z-index: 200;
    background: linear-gradient(180deg, #060115 0%, #12082a 50%, #0c1022 100%);
    display: none;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    font-family: Arial, sans-serif;
    -webkit-tap-highlight-color: transparent;
    padding: 12px;
    box-sizing: border-box;
}
.sk-trophy {
    width: clamp(56px, 14vw, 80px);
    height: auto;
    margin: 0 0 14px;
    filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.6));
    pointer-events: none;
    position: relative;
    z-index: 1;
}
.sk-name-title {
    font-family: Arial Black, Arial, sans-serif;
    font-size: clamp(20px, 5.4vw, 28px);
    font-weight: 900;
    letter-spacing: 2px;
    color: #f0c040;
    margin: 0 0 18px;
    text-shadow:
        -2px  0   0 #a82010,
         2px  0   0 #a82010,
         0   -2px 0 #a82010,
         0    2px 0 #a82010,
         0    7px 10px rgba(0, 0, 0, 0.8);
    pointer-events: none;
    position: relative;
    z-index: 1;
    text-align: center;
}

/* Buffer display: monospace, gold, with placeholder underscores so the
   user can see the slots fill in. */
.sk-buf-row {
    display: flex;
    align-items: baseline;
    gap: 10px;
    margin: 0 0 14px;
    padding: 10px 14px;
    background: rgba(0, 0, 0, 0.35);
    border: 1px solid rgba(232, 104, 40, 0.45);
    border-radius: 10px;
    position: relative;
    z-index: 1;
    max-width: calc(100vw - 24px);
    box-sizing: border-box;
}
.sk-prompt {
    color: #d8b855;
    opacity: 0.65;
    font: 700 18px/1 Arial Black, Arial, sans-serif;
}
#sk-buf {
    color: #f0c040;
    font: 700 clamp(18px, 4.6vw, 22px)/1.1
          ui-monospace, "SF Mono", Menlo, Consolas, monospace;
    letter-spacing: 4px;
    white-space: pre;
    flex: 1 1 auto;
    text-align: left;
}
#sk-counter {
    color: #d8b855;
    opacity: 0.6;
    font: 600 12px Arial, sans-serif;
    letter-spacing: 1px;
    flex: 0 0 auto;
}

/* On-screen keyboard. QWERTY layout, one flex row per keyboard row
   so each row can have a different number of keys and different
   sizing rules (top row has 10, middle has 9, bottom has 7 letters
   plus SHIFT and BACKSPACE) without a single fixed grid forcing
   awkward gaps.

   Apple HIG asks for 44 px minimum tap target; we hit min-height 44 px
   and let width grow with `flex: 1 1 0`. touch-action:manipulation
   suppresses the iOS double-tap-to-zoom delay; user-select:none
   kills the long-press selection callout. */
.sk-kbd {
    display: flex;
    flex-direction: column;
    gap: 6px;
    margin-top: 4px;
    position: relative;
    z-index: 2;
    width: 100%;
    max-width: calc(100vw - 16px);
    box-sizing: border-box;
    padding: 0 4px;
}
.sk-kbd-row {
    display: flex;
    gap: 4px;
    justify-content: center;
    width: 100%;
}
/* Middle row (A-L) is one letter shorter than the top row, so half-
   key padding on each side reproduces the iOS staggered look. */
.sk-kbd-row-mid {
    padding-left: 5%;
    padding-right: 5%;
}
.sk-key {
    flex: 1 1 0;
    min-width: 22px;
    min-height: 44px;
    padding: 0;
    background: linear-gradient(180deg, #1d1240 0%, #0f0828 100%);
    color: #f0c040;
    border: 1px solid #4e2a6a;
    border-radius: 8px;
    font-family: Arial Black, Arial, sans-serif;
    font-size: clamp(13px, 3.2vw, 18px);
    font-weight: 900;
    letter-spacing: 0;
    cursor: pointer;
    user-select: none;
    -webkit-user-select: none;
    -webkit-tap-highlight-color: transparent;
    touch-action: manipulation;
    transition: transform 130ms ease, background 130ms ease;
}
.sk-key:active {
    transform: scale(0.93);
    background: linear-gradient(180deg, #2a1858 0%, #170a3a 100%);
}
.sk-key.sk-special {
    background: linear-gradient(180deg, #c84018 0%, #7e1c02 100%);
    color: #ffffff;
    border-color: #e86828;
    box-shadow:
        0 3px 14px rgba(200, 64, 20, 0.45),
        inset 0 1px 0 rgba(255, 255, 255, 0.18);
}
.sk-key.sk-special:active {
    background: linear-gradient(180deg, #a8300e 0%, #5e1402 100%);
}
/* Shift and backspace are wider than letters on real keyboards
   (~1.5x). They sit on the bottom letter row, flanking Z-M. */
.sk-key.sk-shift, .sk-key.sk-back {
    flex: 1.5 1 0;
    font-size: clamp(15px, 3.8vw, 20px);
}
/* SPACE and SUBMIT each take their own full-width row; flex-grow
   to the row's width and a bit more breathing room with letter-
   spacing so they read as primary actions. */
.sk-key.sk-space {
    flex: 1 1 100%;
    letter-spacing: 4px;
}
.sk-key.sk-enter {
    flex: 1 1 100%;
    letter-spacing: 4px;
    margin-top: 4px;       /* gentle gap between SPACE and SUBMIT */
}

/* Shift state: when #sk-name-overlay carries .sk-caps-on, the next
   letter typed is uppercase and the SHIFT button glows gold. The
   class is removed automatically after the next letter (auto-shift
   off) and on every fresh openNameEntry() the class is re-applied
   so the FIRST character of a new name is always uppercase by
   default — matching mobile-keyboard convention. Letter buttons
   render lowercase when the class is absent so the keyboard
   visually echoes the case the player will get. */
#sk-name-overlay:not(.sk-caps-on) .sk-key[data-k] {
    text-transform: lowercase;
}
#sk-name-overlay.sk-caps-on .sk-key.sk-shift {
    background: linear-gradient(180deg, #f0c040 0%, #b88a2e 100%);
    color: #2a1858;
    border-color: #fff8c8;
    box-shadow:
        0 0 12px rgba(240, 192, 64, 0.55),
        inset 0 1px 0 rgba(255, 255, 255, 0.3);
}

/* SKIP lives outside #sk-kbd and pins to the very bottom of the
   screen, separated from the keyboard so it reads as a different-
   class action. position:absolute against #sk-name-overlay (which
   is position:fixed). */
#sk-skip {
    position: absolute;
    bottom: 14px;
    left: 50%;
    transform: translateX(-50%);
    min-width: 180px;
    padding: 12px 24px;
    letter-spacing: 4px;
    z-index: 3;
}
#sk-skip:active {
    transform: translateX(-50%) scale(0.93);
}
</style>
"""

# ─── Telemetry / leaderboard dispatcher (window.__sk) ───────────────────────
# Closure-private state. Recomputes the same SHA-256 chain hash as
# game/_proof.py so a console attacker can't paste a fake events list.
# usedIds blocks trivial replays. The dispatcher is the only window
# global; results are read back via the *_done actions.
_TELEMETRY_JS = """
<script>
(function () {
    var a = "__SB_URL__";
    var b = "__SB_KEY__";

    /* Surface build-time substitution result early so silently-empty
       leaderboard deploys are debuggable from DevTools. */
    try {
        var urlOk = !!(a && a.indexOf('supabase') >= 0 && a.indexOf('__SB_') < 0);
        console.log('[skybit/lb] build-time substitution:',
            'url=', urlOk ? a : '(not substituted: "' + a + '")',
            'key=', (b && b.indexOf('__SB_') < 0)
                ? (b.slice(0, 12) + '… len=' + b.length)
                : '(not substituted)');
    } catch (_) {}

    /* Independent sanity-ping at boot, never used by the game path. Just
       proves whether the Supabase REST endpoint is reachable from this
       origin under the current key. */
    try {
        if (a && b && a.indexOf('__SB_') < 0 && b.indexOf('__SB_') < 0) {
            setTimeout(function () {
                fetch(a + '/rest/v1/scores?select=name,score&order=score.desc&limit=1', {
                    headers: {'apikey': b, 'Authorization': 'Bearer ' + b}
                }).then(function (r) {
                    console.log('[skybit/lb] sanity-ping status:', r.status, r.statusText);
                    return r.ok ? r.json() : r.text();
                }).then(function (body) {
                    console.log('[skybit/lb] sanity-ping body:',
                        typeof body === 'string' ? body.slice(0, 300) : body);
                }).catch(function (e) {
                    console.error('[skybit/lb] sanity-ping network error:',
                                  e && e.message || e);
                });
            }, 500);
        }
    } catch (_) {}

    /* Result slots — closure-private, never on window. Polled via __sk('*_done'). */
    var rSubmit = null;
    var rFetch  = null;
    var rLog    = null;
    var rFetchError = '';

    /* One submit per run_id per page load. */
    var usedIds = (typeof Set === 'function')
        ? new Set()
        : { has: function (k) { return !!this[k]; },
            add: function (k) { this[k] = 1; } };

    function deviceId() {
        try {
            var id = window.localStorage.getItem('skybit_device_id');
            if (id) return id;
            if (window.crypto && window.crypto.randomUUID) {
                id = window.crypto.randomUUID();
            } else {
                id = ('xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx').replace(/[xy]/g, function (c) {
                    var r = Math.random() * 16 | 0;
                    return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
                });
            }
            window.localStorage.setItem('skybit_device_id', id);
            return id;
        } catch (e) {
            return '00000000-0000-4000-8000-000000000000';
        }
    }

    /* Mirrors game/_proof.py's >qIB + 8-byte ASCII kind layout exactly. */
    function packEvent(t, ds, kind) {
        var ms = Math.round(Number(t) * 1000);
        var buf = new ArrayBuffer(21);
        var dv  = new DataView(buf);
        var hi = Math.floor(ms / 0x100000000);
        var lo = ms >>> 0;
        dv.setUint32(0, hi, false);
        dv.setUint32(4, lo, false);
        dv.setUint32(8, (Number(ds) >>> 0), false);
        var k = String(kind);
        dv.setUint8(12, k.length & 0xff);
        var bytes = new Uint8Array(buf, 13, 8);
        for (var i = 0; i < 8; i++) {
            bytes[i] = (i < k.length) ? (k.charCodeAt(i) & 0x7f) : 0;
        }
        return new Uint8Array(buf);
    }
    function concatU8(a8, b8) {
        var out = new Uint8Array(a8.length + b8.length);
        out.set(a8, 0); out.set(b8, a8.length);
        return out;
    }
    function toHex(u8) {
        var s = '';
        for (var i = 0; i < u8.length; i++) {
            var h = u8[i].toString(16);
            s += (h.length < 2 ? '0' : '') + h;
        }
        return s;
    }
    async function chainHex(events) {
        var c = new Uint8Array(32);  /* zero seed, matches Python */
        for (var i = 0; i < events.length; i++) {
            var ev = events[i];
            var packed = packEvent(ev[0], ev[1], ev[2]);
            var input = concatU8(c, packed);
            var digest = await window.crypto.subtle.digest('SHA-256', input);
            c = new Uint8Array(digest);
        }
        return toHex(c);
    }

    async function doSubmit(rawPayload) {
        rSubmit = null;
        try {
            if (!a || !b) { rSubmit = false; return; }
            var payload;
            try {
                payload = (typeof rawPayload === 'string')
                    ? JSON.parse(rawPayload) : rawPayload;
            } catch (e) { rSubmit = false; return; }
            if (!payload || typeof payload !== 'object') { rSubmit = false; return; }
            var rid = String(payload.run_id || '');
            if (!rid || usedIds.has(rid)) { rSubmit = false; return; }
            var events = payload.events;
            if (!events || !events.length) { rSubmit = false; return; }
            var localHex = await chainHex(events);
            if (localHex !== String(payload.chain_hex || '')) { rSubmit = false; return; }
            usedIds.add(rid);
            var r = await fetch(a + '/rest/v1/scores', {
                method: 'POST',
                headers: {
                    'apikey': b,
                    'Authorization': 'Bearer ' + b,
                    'Content-Type': 'application/json',
                    'Prefer': 'return=minimal'
                },
                body: JSON.stringify({
                    name:  String(payload.name),
                    score: Number(payload.score)
                })
            });
            rSubmit = r.ok;
        } catch (e) { rSubmit = false; }
    }

    async function doFetch() {
        rFetch = null;
        rFetchError = '';
        try {
            if (!a || !b) {
                console.error('[skybit/lb] Supabase URL or KEY is empty — leaderboard cannot fetch.',
                              {hasUrl: !!a, hasKey: !!b});
                rFetchError = 'config missing';
                rFetch = []; return;
            }
            /* Wider slice + client-side plausibility filter so an injected
               row with score 999999 doesn't make it onto the visible top-10. */
            var url = a + '/rest/v1/scores?select=name,score&order=score.desc&limit=200';
            var r = await fetch(url, {
                headers: {'apikey': b, 'Authorization': 'Bearer ' + b}
            });
            if (!r.ok) {
                var bodyText = '';
                try { bodyText = await r.text(); } catch (_) {}
                console.error('[skybit/lb] fetch not ok:',
                              r.status, r.statusText, '-', bodyText.slice(0, 200));
                rFetchError = 'http ' + r.status;
                rFetch = []; return;
            }
            var rows = await r.json();
            var filtered = [];
            for (var i = 0; i < rows.length && filtered.length < 10; i++) {
                var row = rows[i];
                var nm = String(row && row.name || '').slice(0, 10);
                var sc = Number(row && row.score);
                if (!isFinite(sc)) continue;
                if (sc < 0 || sc > 10000) continue;
                filtered.push({name: nm, score: sc});
            }
            console.log('[skybit/lb] fetched', rows.length, 'rows;',
                        filtered.length, 'after filter');
            /* 200 + zero rows is the classic "RLS without policy" signature.
               Surface it so the leaderboard scene shows an explicit
               "Top-10 unavailable" instead of a silent empty list. */
            if (rows.length === 0) rFetchError = 'rls or empty';
            rFetch = filtered;
        } catch (e) {
            console.error('[skybit/lb] fetch threw:', e && e.message || e);
            rFetchError = 'network';
            rFetch = [];
        }
    }

    async function doLog(rawPayload) {
        rLog = null;
        try {
            if (!a || !b) { rLog = false; return; }
            var payload;
            try {
                payload = (typeof rawPayload === 'string')
                    ? JSON.parse(rawPayload) : rawPayload;
            } catch (e) { rLog = false; return; }
            if (!payload || typeof payload !== 'object') { rLog = false; return; }
            var body = {
                score:       Number(payload.score),
                duration_s:  Number(payload.duration_s),
                coins:       Number(payload.coins),
                pillars:     Number(payload.pillars),
                near_misses: Number(payload.near_misses),
                powerups:    payload.powerups || {},
                device_id:   deviceId()
            };
            var r = await fetch(a + '/rest/v1/plays', {
                method: 'POST',
                headers: {
                    'apikey': b,
                    'Authorization': 'Bearer ' + b,
                    'Content-Type': 'application/json',
                    'Prefer': 'return=minimal'
                },
                body: JSON.stringify(body)
            });
            rLog = r.ok;
        } catch (e) { rLog = false; }
    }

    function dispatch(action, payload) {
        switch (String(action || '')) {
            case 'submit':       doSubmit(payload); return null;
            case 'submit_done':  return rSubmit;
            case 'fetch':        doFetch();         return null;
            case 'fetch_done':   return rFetch;
            case 'fetch_error':  return rFetchError;
            case 'log':          doLog(payload);    return null;
            case 'log_done':     return rLog;
            default:             return null;
        }
    }

    /* Frozen so a console attacker can't replace the dispatcher and have
       us call into their version later. */
    Object.defineProperty(window, '__sk', {
        value: dispatch, writable: false, configurable: false, enumerable: false
    });
}());
</script>
"""

# ─── Web Audio bridge (window.skyPlay) ──────────────────────────────────────
# Same OGG files game/audio.py would play through pygame.mixer natively;
# inject_theme.py copies them into build/web/sounds/ at the bottom of this
# script so they're fetchable by the same name. AudioBuffers are decoded
# once and cached. The shared AudioContext is exposed as
# window.__skyResumeCtx so the loading dismiss handler can unlock it on
# the user's real first gesture.
_AUDIO_JS = """
<script>
(function () {
    var _ctx = null;
    var _cache = {};      /* name → AudioBuffer */
    var _pending = {};    /* name → Promise<AudioBuffer> */

    function getCtx() {
        if (!_ctx) _ctx = new (window.AudioContext || window.webkitAudioContext)();
        if (_ctx.state === 'suspended') _ctx.resume();
        return _ctx;
    }
    /* Loading module calls this on every gesture — keeps a single
       AudioContext alive across the splash dismiss and the game itself. */
    window.__skyResumeCtx = function () { try { getCtx(); } catch (_) {} };

    function loadSnd(name) {
        if (_cache[name])    return Promise.resolve(_cache[name]);
        if (_pending[name])  return _pending[name];
        var ac = getCtx();
        var p = fetch('sounds/' + name + '.ogg')
            .then(function (r) { return r.arrayBuffer(); })
            .then(function (b) { return ac.decodeAudioData(b); })
            .then(function (buf) { _cache[name] = buf; delete _pending[name]; return buf; })
            .catch(function (e) { delete _pending[name]; throw e; });
        _pending[name] = p;
        return p;
    }

    window.skyPlay = function (name, volume) {
        loadSnd(name).then(function (buf) {
            var ac = getCtx();
            var src = ac.createBufferSource();
            src.buffer = buf;
            var g = ac.createGain();
            g.gain.value = (volume === undefined ? 1.0 : volume);
            src.connect(g); g.connect(ac.destination);
            src.start();
        }).catch(function (e) {
            if (!window._skyLoggedFail) {
                window._skyLoggedFail = true;
                console.warn('skyPlay failed for ' + name + ':', e);
            }
        });
    };
}());
</script>
"""

# ─── Loading splash + watchdog state machine ────────────────────────────────
# 1. Decorates the splash with twinkling stars.
# 2. Polls window.MM (set by pygbag's runtime when Pyodide is up). Until
#    then, animates the progress bar on a 1-exp(-t/τ) curve so the user
#    sees motion even on slow networks.
# 3. After 8 s without boot: shows "Loading… Ns".
# 4. After 25 s without boot: swaps the CTA to "TAP TO RELOAD" and
#    cache-busts on tap (?_skb=<ts>).
# 5. On dismiss: unlocks audio (window.__skyResumeCtx), sets MM.UME=true,
#    dispatches a click on canvas (pygbag listens for it to wake the
#    interpreter), then waits for window.skybitGameReady (set by
#    game/scenes.py first frame) before fading the overlay.
# `pygbagReady` token here is also what the post-write assertion checks for.
_LOADING_JS = """
<script>
(function () {
    /* Boot diagnostics — confirm overlay reached the DOM. */
    try {
        var ovProbe = document.getElementById('skybit-loading');
        console.log('[skybit/boot] overlay in DOM:', !!ovProbe,
            ovProbe ? '(z-index=' + getComputedStyle(ovProbe).zIndex +
                      ', display=' + getComputedStyle(ovProbe).display + ')' : '');
    } catch (_) {}

    var ov = document.getElementById('skybit-loading');
    if (!ov) return;

    /* 75 twinkling stars. Same params as the previous implementation. */
    for (var i = 0; i < 75; i++) {
        var s = document.createElement('div');
        s.className = 'sk-star';
        var sz = (Math.random() * 2.5 + 0.7).toFixed(1);
        s.style.cssText =
            'width:' + sz + 'px;height:' + sz + 'px;' +
            'top:'  + (Math.random() * 90).toFixed(1) + '%;' +
            'left:' + (Math.random() * 100).toFixed(1) + '%;' +
            '--dur:'   + (Math.random() * 3 + 1.3).toFixed(1) + 's;' +
            '--delay:' + (Math.random() * 4).toFixed(1) + 's;';
        ov.insertBefore(s, ov.firstChild);
    }

    var btn    = document.getElementById('sk-cta');
    var status = document.getElementById('sk-status');
    var fill   = document.getElementById('sk-progress-fill');

    var BTN_READY  = 'TAP  ·  CLICK  ·  SPACE';
    var BTN_LOAD   = 'LOADING…';
    var BTN_RELOAD = 'TAP TO RELOAD';
    var STALL_MS   = 25000;
    var INFO_MS    =  8000;
    /* 1-exp(-t/τ) climbs fast then asymptotes. Reaches ~63% at 6 s,
       ~86% at 12 s, ~95% at 18 s. We never let it hit 100% from time
       alone — only a real window.MM detection snaps it there. */
    var ASYMPTOTE  = 0.92;
    var TAU_MS     = 6000;
    var t0 = Date.now();
    var pygbagReady = false;
    var stalled = false;
    var dismissed = false;

    if (btn) btn.textContent = BTN_LOAD;

    function isReady() {
        try { return typeof window.MM !== 'undefined' && window.MM !== null; }
        catch (_) { return false; }
    }
    function setFill(pct) {
        if (!fill) return;
        if (pct < 0)   pct = 0;
        if (pct > 100) pct = 100;
        fill.style.width = pct.toFixed(2) + '%';
    }

    var pollId = setInterval(function () {
        if (isReady() && !pygbagReady) {
            pygbagReady = true;
            stalled = false;
            if (btn)    btn.textContent    = BTN_READY;
            if (status) status.textContent = '';
            if (fill)   fill.classList.remove('sk-stalled');
            setFill(100);
            /* Auto-boot: no tap required. dismiss() is idempotent. */
            dismiss();
            return;
        }
        if (pygbagReady) return;
        var elapsed = Date.now() - t0;
        var pct = ASYMPTOTE * (1 - Math.exp(-elapsed / TAU_MS)) * 100;
        setFill(pct);
        if (elapsed >= STALL_MS && !stalled) {
            stalled = true;
            if (btn)    btn.textContent    = BTN_RELOAD;
            if (status) status.textContent = 'Loading is stuck. Tap to reload.';
            if (fill)   fill.classList.add('sk-stalled');
        } else if (elapsed >= INFO_MS && status && !stalled) {
            status.textContent = 'Loading… ' + Math.floor(elapsed / 1000) + 's';
        }
    }, 250);

    function reloadBust() {
        clearInterval(pollId);
        try {
            var u = new URL(window.location.href);
            u.searchParams.set('_skb', String(Date.now()));
            window.location.replace(u.toString());
        } catch (_) {
            window.location.reload();
        }
    }

    function pulseBtn() {
        if (!btn) return;
        btn.style.transition = 'transform 120ms ease';
        btn.style.transform  = 'scale(0.93)';
        setTimeout(function () { btn.style.transform = ''; }, 130);
    }

    function dismiss() {
        /* Unlock the shared AudioContext on every gesture, even pre-ready
           pulses — no harm in early resume. */
        if (typeof window.__skyResumeCtx === 'function') {
            try { window.__skyResumeCtx(); } catch (_) {}
        }
        if (stalled)        { reloadBust(); return; }
        if (!pygbagReady)   { pulseBtn();   return; }
        if (dismissed) return;
        dismissed = true;

        clearInterval(pollId);
        try { if (window.MM) window.MM.UME = true; } catch (_) {}
        var cv = document.getElementById('canvas');
        if (cv) {
            try {
                cv.dispatchEvent(new MouseEvent('click', {
                    bubbles: true, cancelable: true
                }));
            } catch (_) {}
        }
        ov.removeEventListener('click',      dismiss);
        ov.removeEventListener('touchstart', dismiss);
        ov.removeEventListener('touchend',   dismiss);

        /* Stay visible over the canvas while pygbag mounts the App and
           game/scenes.py renders its first frame. Pointer-events:none so
           subsequent taps reach the canvas behind us during this hold. */
        if (btn)    btn.textContent    = 'STARTING…';
        if (status) status.textContent = '';
        ov.style.pointerEvents = 'none';

        function fade() {
            ov.style.transition = 'opacity 0.45s ease';
            ov.style.opacity    = '0';
            setTimeout(function () { ov.style.display = 'none'; }, 480);
        }
        var holdT0 = Date.now();
        var holdId = setInterval(function () {
            if (window.skybitGameReady === true ||
                Date.now() - holdT0 > 12000) {
                clearInterval(holdId);
                fade();
            }
        }, 16);
    }
    ov.addEventListener('click',      dismiss);
    ov.addEventListener('touchstart', dismiss);
    ov.addEventListener('touchend',   dismiss);
}());
</script>
"""

# ─── Name-entry overlay (virtual keyboard) ──────────────────────────────────
# No <input>, no .focus(), no key shields, no MutationObservers. Click
# delegation on the keyboard grid maps each <button> to an action via
# data-act / data-k attributes. window.openNameEntry shows the overlay
# and resets _pendingName; any close path (back to skip / enter) writes
# the result string and hides the overlay. Python polls _pendingName.
_NAME_ENTRY_JS = """
<script>
(function () {
    var MAX = 10;
    var _buf = '';
    var _starsAdded = false;
    /* Auto-shift: ON for the first character of a fresh name (so the
       opening letter is capital), then auto-OFF after one tap.
       Player can re-enable manually via the SHIFT key for any later
       capital. Same convention as iOS / Android soft keyboards. */
    var _shiftOn = true;

    /* Pre-resolve DOM refs — these elements are in the static HTML. */
    function el(id) { return document.getElementById(id); }
    function applyShiftClass() {
        var ov = el('sk-name-overlay');
        if (!ov) return;
        if (_shiftOn) ov.classList.add('sk-caps-on');
        else          ov.classList.remove('sk-caps-on');
    }

    function render() {
        var ov = el('sk-name-overlay');
        if (!ov) return;
        var bufEl = el('sk-buf');
        var ctEl  = el('sk-counter');
        if (bufEl) {
            var slots = '';
            for (var i = 0; i < MAX; i++) {
                slots += (i < _buf.length ? _buf.charAt(i) : '_');
                if (i < MAX - 1) slots += ' ';
            }
            bufEl.textContent = slots;
        }
        if (ctEl) ctEl.textContent = _buf.length + ' / ' + MAX;
    }

    function close(value) {
        var ov = el('sk-name-overlay');
        if (ov) {
            ov.style.display = 'none';
            ov.setAttribute('aria-hidden', 'true');
        }
        window._pendingName = value;
    }

    /* Public, called by Python (game/leaderboard.py) when player qualifies. */
    window.openNameEntry = function () {
        var ov = el('sk-name-overlay');
        if (!ov) return;
        _buf = '';
        _shiftOn = true;          /* first letter is capital by default */
        applyShiftClass();
        render();
        window._pendingName = '__pending__';
        ov.setAttribute('aria-hidden', 'false');

        /* Inject the same twinkling-star layer used on the loading splash,
           one-shot. Identical look, gated on a flag so re-opens don't
           double up. */
        if (!_starsAdded) {
            _starsAdded = true;
            for (var i = 0; i < 40; i++) {
                var s = document.createElement('div');
                s.className = 'sk-star';
                var sz = (Math.random() * 2.2 + 0.6).toFixed(1);
                s.style.cssText =
                    'width:' + sz + 'px;height:' + sz + 'px;' +
                    'top:'  + (Math.random() * 90).toFixed(1)  + '%;' +
                    'left:' + (Math.random() * 100).toFixed(1) + '%;' +
                    '--dur:'   + (Math.random() * 3 + 1.3).toFixed(1) + 's;' +
                    '--delay:' + (Math.random() * 4).toFixed(1) + 's;';
                ov.insertBefore(s, ov.firstChild);
            }
        }

        ov.style.display = 'flex';
    };

    /* One delegated click handler for every key. Bubble-phase, no
       preventDefault, no stopPropagation — SDL gets the click and
       does whatever it wants with the canvas; the keyboard buttons
       are simple <button> elements which natively absorb the
       synthetic-click race that broke the previous input element. */
    function onKbdClick(e) {
        var t = e.target.closest && e.target.closest('.sk-key');
        if (!t) return;
        var act = t.getAttribute('data-act');
        var k   = t.getAttribute('data-k');
        if (act === 'back') {
            if (_buf.length > 0) {
                _buf = _buf.slice(0, -1);
                render();
                if (typeof window.skyPlay === 'function') {
                    try { window.skyPlay('button', 0.4); } catch (_) {}
                }
            }
            return;
        }
        if (act === 'space') {
            if (_buf.length < MAX) {
                _buf += ' ';
                render();
            }
            return;
        }
        if (act === 'skip') {
            close('__skip__');
            return;
        }
        if (act === 'shift') {
            _shiftOn = !_shiftOn;
            applyShiftClass();
            return;
        }
        if (act === 'enter') {
            var v = _buf.replace(/\\s+$/, '').replace(/^\\s+/, '');
            close(v.length > 0 ? v : '__skip__');
            return;
        }
        if (k && _buf.length < MAX) {
            _buf += _shiftOn ? k : k.toLowerCase();
            if (_shiftOn) {
                /* Auto-shift off after one capital, matching mobile
                   keyboard convention. The player re-taps SHIFT for
                   any later capitals. */
                _shiftOn = false;
                applyShiftClass();
            }
            render();
            if (typeof window.skyPlay === 'function') {
                try { window.skyPlay('button', 0.4); } catch (_) {}
            }
        }
    }

    function attach() {
        /* Listen on the overlay (parent of both #sk-kbd and #sk-skip)
           so the same delegated handler routes letter / action / SKIP
           clicks via .closest('.sk-key'). */
        var ov = el('sk-name-overlay');
        if (ov) ov.addEventListener('click', onKbdClick);
    }
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', attach);
    } else {
        attach();
    }

    /* Initialise the sentinel so Python's first poll, if it lands before
       the overlay was opened, sees a deterministic value. */
    if (typeof window._pendingName !== 'string') {
        window._pendingName = '__pending__';
    }
}());
</script>
"""

# ─── Screen Wake Lock (keep mobile screens from auto-dimming) ───────────────
# The intro is now ~21 s of fully passive playback (the only required input
# is a tap to skip). Without input, both Android and iOS dim the screen
# after their respective idle thresholds, which players read as "the
# screen is fading on its own".
#
# Modern path: the standard Wake Lock API. Supported in Chrome (Android)
# 84+, Safari (iOS) 16.4+, and most desktop browsers. Some browsers refuse
# the request before any user gesture, so we also acquire on the first
# click/touch (the same gesture that dismisses our splash).
#
# Older iOS / iPadOS path (< 16.4): no Wake Lock API. The standard fallback
# is the "NoSleep" trick — play a 1-second muted, looping, in-line video.
# Browsers count active media playback as "user activity" and keep the
# screen awake while the video is playing. The data-URI below is a tiny
# (~330-byte base64) silent black MP4 — small enough to ship inline and
# big enough that AVFoundation accepts it.
_WAKE_LOCK_JS = r"""
<script>
(function () {
    var _wakeLock = null;
    var _video = null;
    var _videoStarted = false;
    /* MIT-licensed tiny silent MP4 from the NoSleep.js project (Rich Tibbett),
       used as a fallback wake-lock technique for browsers without the
       standard Wake Lock API (notably iOS Safari < 16.4). */
    var TINY_MP4 = 'data:video/mp4;base64,AAAAHGZ0eXBpc29tAAACAGlzb21pc28ybXA0MQAAAAhmcmVlAAAGF21kYXTeBAAAbGliZmFhYyAxLjI4AABCAJMgBDIARwAAArEGBf//rdxF6b3m2Ui3lizYINkj7u94MjY0IC0gY29yZSAxNDIgcjIgOTU2YzhkOCAtIEguMjY0L01QRUctNCBBVkMgY29kZWMgLSBDb3B5bGVmdCAyMDAzLTIwMTQgLSBodHRwOi8vd3d3LnZpZGVvbGFuLm9yZy94MjY0Lmh0bWwgLSBvcHRpb25zOiBjYWJhYz0wIHJlZj0zIGRlYmxvY2s9MTowOjAgYW5hbHlzZT0weDE6MHgxMTEgbWU9aGV4IHN1Ym1lPTcgcHN5PTEgcHN5X3JkPTEuMDA6MC4wMCBtaXhlZF9yZWY9MSBtZV9yYW5nZT0xNiBjaHJvbWFfbWU9MSB0cmVsbGlzPTEgOHg4ZGN0PTAgY3FtPTAgZGVhZHpvbmU9MjEsMTEgZmFzdF9wc2tpcD0xIGNocm9tYV9xcF9vZmZzZXQ9LTIgdGhyZWFkcz02IGxvb2thaGVhZF90aHJlYWRzPTEgc2xpY2VkX3RocmVhZHM9MCBucj0wIGRlY2ltYXRlPTEgaW50ZXJsYWNlZD0wIGJsdXJheV9jb21wYXQ9MCBjb25zdHJhaW5lZF9pbnRyYT0wIGJmcmFtZXM9MCB3ZWlnaHRwPTAga2V5aW50PTI1MCBrZXlpbnRfbWluPTI1IHNjZW5lY3V0PTQwIGludHJhX3JlZnJlc2g9MCByY19sb29rYWhlYWQ9NDAgcmM9Y3JmIG1idHJlZT0xIGNyZj0yMy4wIHFjb21wPTAuNjAgcXBtaW49MCBxcG1heD02OSBxcHN0ZXA9NCB2YnZfbWF4cmF0ZT03NjggdmJ2X2J1ZnNpemU9MzAwMCBjcmZfbWF4PTAuMCBuYWxfaHJkPW5vbmUgZmlsbGVyPTAgaXBfcmF0aW89MS40MCBhcT0xOjEuMDCAAAAAVliIQL//8m+P5OXfBeLGOfKE3xkODvFZuBflHv/+VwJIta6cbpIo4ABLoKBaYrCIIgQDb//7vKy1QO+v/h9PXsjwlaWWdNpUq/rCqcgmZG/Pn2QKEgFRAAAAAVQZqsj//8GHv/5lT5IL7p5gAa//AGT1OZsIRAOaAB22wAEABAQAEAAAAAFRBnsh//4j8/EokHpKtzSQAGuv/wDF8yT24eAAAAAAFLAA';

    function tryAcquire() {
        if (!('wakeLock' in navigator)) {
            startVideoFallback();
            return;
        }
        if (_wakeLock !== null) return;
        navigator.wakeLock.request('screen').then(function (lock) {
            _wakeLock = lock;
            lock.addEventListener('release', function () {
                _wakeLock = null;
            });
        }).catch(function () {
            /* Refused (no user gesture, denied permission, etc.). The
               first-interaction listener below will retry. */
        });
    }

    function startVideoFallback() {
        if (_videoStarted) return;
        _videoStarted = true;
        _video = document.createElement('video');
        _video.setAttribute('playsinline', '');
        _video.setAttribute('muted', '');
        _video.setAttribute('autoplay', '');
        _video.setAttribute('loop', '');
        _video.muted = true;
        _video.src = TINY_MP4;
        _video.style.cssText =
            'position:fixed;top:0;left:0;width:1px;height:1px;' +
            'opacity:0;pointer-events:none;z-index:-1;';
        document.body.appendChild(_video);
        var p = _video.play();
        if (p && typeof p.catch === 'function') {
            p.catch(function () {
                /* Autoplay blocked — will retry on first user gesture. */
            });
        }
    }

    function onFirstInteract() {
        tryAcquire();
        if (_video && _video.paused) {
            _video.play().catch(function () {});
        }
        document.removeEventListener('click', onFirstInteract);
        document.removeEventListener('touchstart', onFirstInteract);
    }
    document.addEventListener('click', onFirstInteract, { passive: true });
    document.addEventListener('touchstart', onFirstInteract, { passive: true });

    /* Try right away — works on Chrome/Android and most desktop browsers
       without needing a user gesture. */
    tryAcquire();

    /* Re-acquire when the tab returns to the foreground; the OS releases
       the lock when the page is hidden. */
    document.addEventListener('visibilitychange', function () {
        if (document.visibilityState === 'visible') {
            tryAcquire();
            if (_video && _video.paused) {
                _video.play().catch(function () {});
            }
        }
    });
}());
</script>
"""

INJECTION = _CSS + _TELEMETRY_JS + _AUDIO_JS + _LOADING_JS + _NAME_ENTRY_JS + _WAKE_LOCK_JS

html = html.replace("</body>", INJECTION + "</body>", 1)
html = html.replace("__SB_URL__", _SB_URL)
html = html.replace("__SB_KEY__", _SB_KEY)

src.write_text(html, encoding="utf-8")


# ── 4. Post-write assertions ────────────────────────────────────────────────
# These guard against silent template drift in pygbag: the
# .replace("<body>", ...) and re.subn(...) calls all no-op if pygbag's
# template changes shape, the file is written unchanged, and the deploy
# happily ships the unthemed default. Fail loudly so the previous good
# deploy is retained.
_problems = []
if "skybit-loading" not in html:
    _problems.append(
        "OVERLAY HTML (id=skybit-loading) was not injected — pygbag's HTML "
        "probably no longer contains a literal '<body>' tag. inject_theme.py "
        "needs updating to match pygbag's new template."
    )
if "pygbagReady" not in html:
    _problems.append(
        "Watchdog state machine (pygbagReady) was not injected — pygbag's "
        "HTML probably no longer contains a literal '</body>' tag."
    )
if _color_subs == 0:
    _problems.append(
        "None of the loading-bar color replacements matched — pygbag has "
        "almost certainly changed its loader template. Users will see the "
        "unthemed green/blue default progress bar."
    )
if "powderblue" in html:
    _problems.append(
        "'powderblue' still present in output — background-color "
        "replacements did not run as expected."
    )
# NOTE: we used to check `if "<input" in html.split("</body>")[0]` here as
# a belt-and-braces guard for the name-entry redesign. Removed because
# pygbag's own template ships an <input> for SDL/Emscripten keyboard
# glue, and our assertion would reject every build. The functional
# invariant ("our name-entry HTML has no input") is verified at the
# source level (NAME_HTML constant) and via headless-browser smoke,
# not against the post-injection runtime html.
if _problems:
    print("✗ inject_theme.py post-write assertions failed:", file=sys.stderr)
    for p in _problems:
        print("  - " + p, file=sys.stderr)
    print(
        "Aborting non-zero so the previous good deploy is retained.",
        file=sys.stderr,
    )
    raise SystemExit(1)

print("✓ Skybit theme injected into build/web/index.html")
print(f"  ({_color_subs} color replacements matched)")
if _SB_URL and _SB_KEY:
    print(f"✓ Supabase URL set: {_SB_URL[:40]}...")
elif _SB_URL or _SB_KEY:
    missing = "SUPABASE_ANON_KEY" if _SB_URL else "SUPABASE_URL"
    print(
        f"✗ {missing} is missing while the other Supabase env var is set. "
        "Both must be configured as repository secrets for the leaderboard "
        "to work. Aborting.",
        file=sys.stderr,
    )
    raise SystemExit(1)
else:
    print(
        "⚠⚠⚠ SUPABASE_URL and SUPABASE_ANON_KEY are both missing.\n"
        "    The leaderboard will be EMPTY in the deployed site.\n"
        "    Set them as repository secrets at:\n"
        "      Settings → Secrets and variables → Actions → New repository secret\n"
        "    Build is continuing because some deploys (e.g. local previews) "
        "intentionally\n"
        "    skip the leaderboard, but production deploys MUST set these."
    )


# ── 5. Copy CC0 sound files to build/web/sounds/ for browser fetch ──────────
# Native pygame.mixer reads them from game/assets/sounds/. The browser
# can't reach into the bundled APK, so window.skyPlay fetches them by
# relative path under the deployed site root.
import shutil
_SND_SRC = Path("game/assets/sounds")
_SND_DST = Path("build/web/sounds")
if _SND_SRC.exists():
    _SND_DST.mkdir(parents=True, exist_ok=True)
    n_copied = 0
    for ogg in _SND_SRC.glob("*.ogg"):
        shutil.copy(ogg, _SND_DST / ogg.name)
        n_copied += 1
    print(f"✓ Copied {n_copied} sound files → build/web/sounds/")
else:
    print(f"⚠ {_SND_SRC} not found — browser will play no sounds")
