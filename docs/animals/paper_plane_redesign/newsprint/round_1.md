# Paper Plane redesign — NEWSPRINT / COMIC · Round 1

Secret premium paper-plane skin reimagined as a dart folded from a sheet of
newspaper / comic print, replacing the production dollar-bill dart. All five
takes keep the production CONTRACT exactly:

- `build_<name>(wing_angle_deg) -> 64×84 SRCALPHA`, mass centred (32,44).
- **Nose points RIGHT** (forward).
- No wings — the 4 wing poses drive a clamped bank-roll + nose-bob (`_ROLL_MAX = 5.5`).
- Baked 1px self-rim so the dart holds on day AND night with no host outline.

## The trap, and the shared structure that beats it

Faithful newsprint is light grey — it turns to mush at 40px. So every take reuses
the production dart's load-bearing structure and changes only the SURFACE
treatment of the facets:

1. a **hard value FOLD** — bright upper facet vs. distinctly darker under-fold
   meeting at a crisp 3px central crease, so the triangular dart silhouette
   survives;
2. exactly **ONE bold high-contrast TELL** on the lit facet over clean light
   paper, so the body never reads flat grey;
3. column rules / halftone dots kept subtle (hero texture, intentional near-noise
   at 40px).

## The five sub-takes

- **V1 · BROADSHEET** — light grey newsprint, faint column rules, and a bold
  black **headline bar** (plus a thinner sub-head) slammed across the lit facet.
  The black-over-grey bar is the entire 40px read. The most classic, restrained.
- **V2 · TABLOID** — bright stock with a thin red masthead rule and one screaming
  word **"WOW"** in fat block capitals drawn from heavy strokes so the letters
  stay bold ink mass even when they blur small.
- **V3 · SUNDAY COMIC** — Ben-Day **halftone dot** field (CMYK yellow + a magenta
  dot pass) clipped to the lit facet, topped by a small black-outlined red
  **"POW!" starburst** with a bright core. The most pop-art / premium read.
- **V4 · SEPIA** — warm tea-stained antique stock with faint columns and foxing
  speckle, plus an old-style black **headline block** over a brown rule. Vintage,
  warmer than V1; the black block still carries 40px.
- **V5 · CROSSWORD** — a clean 3×3 **crossword grid** on the lit facet with a
  checker of solid inked cells. The black/white checker is a crisp graphic mark
  that survives downscale.

## Review sheet

`round_1.png` (592×1260): each take at 130px hero + 40px NEAREST-x3 (level /
dive) on a **day** sky and a **night** sky, so the day-and-night legibility of
the single bold tell is the front-and-centre judgement.

Render: `python docs/animals/paper_plane_redesign/newsprint/_render_sheet.py`

Procedural only; both build targets stay green (no platform-specific calls).
Nothing wired into `game/` — awaiting art-director critique.
