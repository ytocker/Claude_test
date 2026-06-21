# GENIE FLASK — Round 3 (HIGH tier)

Round 2 verdict was ITERATE: the hero/upright briolette read (KEEP), but the
CARRIED read failed — the gold collar + blue body camouflaged into Pip (blue
body vs his blue belly; collar merging with his gold foot), the chevron point
rounded off under tilt, and the stopper merged with the collar into one gold
lump. Round 3 fixes the carry read while keeping the faceted briolette
silhouette, the double-edged gold collar, and the night inner glow.

## What changed (all four critique notes)

1. **Separated from Pip.** Two moves. (a) The whole gem is shifted OUTBOARD —
   down-LEFT of sprite centre (`cx = SS//2 - 3`, `dy = +3`) — so the body and
   point clear Pip's foot/belly and the gold band pokes out below his foot as
   a held object, not fused to him. (b) A dark CONTACT-SHADOW RIM is now
   stamped around the whole silhouette (fattest toward the lower-left where it
   meets Pip), giving a 1px dark gap so the flask never bleeds into his blue
   belly or gold foot — and a 1px LIT-GLASS BEVEL runs the upper-left edge so
   the gem still separates where it touches Pip's *dark* wing shadow (a
   near-black rim alone vanished into him there).

2. **Chevron apex stays SHARP under tilt.** The base now converges to a
   single-pixel APEX (`(cx+1, pt_y-1) → (cx, pt_y) → (cx-1, pt_y-1)`) instead
   of a 2px flat tip, and the point's spine + facet seams converge on it. At
   −25/0/30/60/90° the tilt rows keep an angular gem tip — no reversion to a
   rounded blue blob.

3. **Body hue pushed OFF Pip's blue.** The wall is re-hued from royal sapphire
   to a deeper VIOLET-sapphire: core `#2A2CA8`, lit plane `#524CD6`, shaded
   `#16166E`. Even the LIT plane stays darker and more purple than Pip's wing
   blue (`#2864FF`), so the flask no longer camouflages against his belly/wing
   — the night frame, where the old blue vanished into him, now reads clearly.
   The inner glow tint follows to violet (`#B0A8FF`).

4. **Neck NOTCH added.** A dark notch line sits between the gold stopper and the
   neck so the stopper reads as a separate dome over a waist, not one gold lump
   merged with the collar. The hero crop shows the readable stopper / notch /
   body / band stack.

KEPT: the briolette silhouette (flat shoulders + chevron point), the gold
collar ringed dark on BOTH edges, the night inner glow, the gem weighted to the
lower/visible half.

## Carry-scale read (the verdict)

- **Flask separates from Pip — DAY:** YES. Below his foot a clean gold band +
  violet faceted apex pokes out, ringed in dark, distinct from his blue wing.
- **Flask separates from Pip — NIGHT:** YES. The violet body + gold band + dark
  rim hold against BOTH the dark purple sky and Pip's royal-blue belly; it no
  longer melts into him as it did in Round 2.
- **Chevron stays sharp under tilt:** YES. Day and night tilt rows
  (−25/0/30/60/90°) keep an angular faceted gem with a pointed apex and a
  gold band at every bank angle; the grayscale row still reads as an angular
  pointed gem, not a round bottle.

## Structure

Gold band pulled down to `waist_y ≈ 33/44` so it lands in the bottom slice that
clears Pip's foot; apex at `pt_y ≈ 45/44-relative` is the lowest point. Stopper
+ neck notch crown the top where Pip crops in. Built at 2× then smoothscaled to
22px so the apex and band survive the in-play size + tilt.
