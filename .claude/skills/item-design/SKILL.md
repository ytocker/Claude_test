---
name: item-design
description: Use when asked to design, redesign, restyle, or "give N looks for" any Skybit store item — a costume/skin/parrot/animal/shoe/hat/shades/parcel in game/store_catalog.py, or any in-game item visual. Brainstorms 5 distinct concepts, runs 5 graphics-designer↔art-director design loops IN PARALLEL, and delivers ONE comparison figure (the original + the 5 designs, each in gameplay) committed to git with a clickable GitHub link in chat. Triggers include "(re)design/restyle the X costume/item", "make 5 new looks for X", "explore designs for the X skin". Do NOT use for non-visual gameplay/code changes.
---

# Item design loop (Skybit)

The standing workflow for designing or restyling any store item. The user wants
it applied **without re-stating the instructions each time** — so when they name
an item to design, run this end to end. The deliverable is always: **5 distinct
designs, explored via parallel design loops, surfaced as ONE comparison figure
vs. the original, committed to git, with a clickable GitHub link in chat.**

The orchestrator (you) runs the loop — subagents can't call each other. Read
`CLAUDE.md` (Design loop + Costume redesign loop sections) for project context.

## 0 · Setup
- Work on the active feature branch (never `main`/`gh-pages`).
- Find the item in `game/store_catalog.py` (its id + name + group, e.g.
  `skin_ninja` / "NINJA"). Locate its CURRENT builder — costumes/parrots/animals
  live in `game/store_skins.py` (or `game/animal_*.py`); shoes/hats/shades in
  `game/<group>_skins.py`. This current art is the ORIGINAL for the comparison.
- Scratch homes (both excluded from the pygbag bundle): builders under
  `tools/<item>_candidates/`, imagery under `docs/store_redesign/<group>/<item>/`.

## 1 · Brainstorm 5 distinct concepts
- **New theme / from-scratch restyle** → delegate to `novelty-designer` for **5
  ranked, buildable concepts**, each layering MULTIPLE themed objects across the
  bird (head + back + body + limbs), each with a name / hero silhouette / object
  list + placement / 3–5 hex palette / distinctness line. Write to
  `docs/store_redesign/<group>/<item>/concepts.md`; numbers map to design_1…5.
- **Pure recolor, or a narrow sub-element refinement** (e.g. just the face/axe) →
  define the 5 directions yourself (skip novelty) — still 5 clearly-distinct
  options. For shared structure, factor a `_shared.py` so each design only writes
  the varying part.

## 2 · Candidates are SCRATCH only
- Each `tools/<item>_candidates/design_N.py` exposes a `build` callable
  `(frame_idx, tilt_deg) -> Surface`, wrapped by `store_skins._make_skin` (or a
  custom compose when draw-order needs it). Body recolors go through
  `dollar_parrot_ghost._build_parrot_with_palette` + `_pal` (see the shipped
  `skin_ninja` `P_NINJA` / `skin_viking` `_VK_PAL`).
- **NEVER** register in `store_skins.BUILDERS`; never touch production art or the
  catalog until the user picks a winner. Procedural art only (no PNG sprites).

## 3 · Five design loops, run IN PARALLEL (batched by phase)
`R1 designers(5) → C1 critics(5) → R2 designers(5)`
- **Cap:** ≤2 designer + ≤1 critic turns per design, ending on a designer
  revision; early-exit a design on `VERDICT: SHIP-READY`; always run ≥1 critique.
  Honor a tighter cap if the user asks (e.g. "max 1 designer / 1 critic").
- **graphics-designer** builds its candidate and renders it in-gameplay via the
  generic harness `tools/ninja_render.py` (`gameplay_panel` + `hero_panel` + a
  40px NEAREST "truth read"; legendaries get a 4-frame filmstrip), saving
  `docs/store_redesign/<group>/<item>/design_N/round_M.png`. It SELF-COMMITS its
  builder + sheet and does **NOT** self-critique.
- **art-director** reviews and returns a critique whose FIRST LINE is exactly
  `VERDICT: SHIP-READY | ITERATE | RE-ROLL`, then a short ranked, buildable punch
  list. Feed each critique back to that design's next designer round.
- **IMPORTANT — execute, don't plan:** prefix graphics-designer briefs with
  "EXECUTE NOW — build, render, commit; do NOT return a plan or wait for
  approval." (They otherwise sometimes stop at a plan.)
- Resume across rounds with FRESH graphics-designer agents that read the
  committed builder (SendMessage isn't available in cloud sessions).
- Launch the 5 agents of each phase in a SINGLE message (parallel). View each
  sheet (or a quick montage) before launching the next phase. The 40px-in-motion
  read is the bar; check day AND night; keep both build targets green.

## 4 · Deliverable — ONE comparison figure + chat link
- Orchestrator writes `tools/render_<item>_compare.py` mirroring
  `tools/render_ninja_redesign_compare.py`: import the ORIGINAL (the live
  registered sid) + the 5 final builders, render each Pip mid-flight over a real
  gameplay biome scene, side by side, labeled `ORIGINAL + DESIGN 1..5`. Save
  `docs/store_redesign/<group>/<item>/final_comparison.png`; commit + push.
- Reply with the **clickable GitHub link**
  `https://github.com/ytocker/skybit/blob/<active-branch>/<path>` + a one-line
  evolution note per design; flag any design that ended without a SHIP-READY
  sign-off. Then ask which design (and palette, if applicable) to take forward.

## 5 · Integration (only after the user picks a winner)
- Port the chosen scratch builder into production under the SAME item id/name
  (e.g. `skin_ninja`/NINJA, `skin_viking`/VIKING). Inline it self-contained
  (production can't import from `tools/`), keep the exported `get_<x>_parrot`
  registered, strip exploration/round references from comments (WHY-only).
- Verify: `SDL_VIDEODRIVER=dummy python -m pytest tests/` green, render check
  `parrot.get_skin_frame("<id>", 2, 10.0)`, regenerate the store figures
  (`tools/capture_store_figures.py`), commit + push, surface the store link.
