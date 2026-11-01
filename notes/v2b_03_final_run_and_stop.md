# v2b Step 3 — the final run, and B stops for SKY 26d

**Decision (owner's rule, applied 1 Nov 2026): B stops for this shuttle.** The final run cleared the clock
violations but its data-net slew is far worse than A's. A (`tt-ternary-mac-v2`, `signoff-a`) remains the
only submission. B's tiles are not bought.

## The final run (owner's option 2 on top of lrc2)

Branch `eval/final`, CI 41316591374. Changes on top of lrc2 (calibrated `LAYERS_RC`, post-GRT repair margin
20 %):

- `src/pnr.sdc`: `base.sdc` plus `set_max_transition 0.65` (13 % below the 0.75 ns limit), used by PnR only.
  `src/signoff.sdc` is `base.sdc` unchanged; `SIGNOFF_SDC_FILE` points to it, so sign-off STA is unchanged.
- `CTS_DISTANCE_BETWEEN_BUFFERS` 70 µm, the fix that cleared A's clock-root fanout in its clean-up run.

The local copy of the run was stopped in detailed routing after 1 h (CI is the record; lrc2 local and CI
were identical).

## Against lrc2

| metric | baseline 41295299103 | lrc2 41309116865 | **final 41316591374** | A |
|---|---|---|---|---|
| slew pins max_ss / nom_ss | 122 / 96 | 4 / 0 | **60 / 33** | 5 / 0 |
| slew driver nets max_ss | 28 | 1 | **13** | 1 |
| worst over limit, max_ss | +462 ps | +65 ps (`f_samp[0]`) | **+2,105 ps** (`_00145_`, a21oi_2 into 0.151 pF) | +50.5 ps |
| worst over limit, nom_ss | +398 ps | none | +18 ps (8 nets) | none |
| clock root `clkbuf_0_clk` fanout | 16 | 16 | **2** | 16 |
| clock root cap, max_ss (limit 0.2 pF) | 0.24 | 0.237 (violation) | **0.017** | < 0.2 |
| clock root slew, max_ss | — | 0.369 ns | 0.066 ns | 0.294 ns |
| max-cap violations | 1 (clock root) | 1 (clock root) | 1 (**data** net `_08826_/Y`, 0.141 / 0.128 pF) | 0 |
| max-fanout (own limit 8) | 2 | 4 | 2 (two buffers at 9) | 2 |
| latency skew, max_ss | — | 0.507 ns | 0.512 ns | 0.200 ns |
| clock insertion delay max, max_ss | — | 1.655 ns | 2.072 ns | 1.382 ns |
| setup WS (worst) | +2.481 | +2.312 | **+1.180** | +4.883 |
| hold WS (worst) | +0.093 | +0.067 | +0.090 | +0.103 |
| utilisation | 69.74 % | 71.21 % | 73.45 % | 63.8 % |
| timing-repair buffers | 1,260 | 1,280 | 1,490 | — |
| clock buffers / inverters | — | 118 / 5 | 121 / 6 | — |
| wirelength (µm) | 253,170 | 258,432 | 286,916 | — |
| magic DRC / route DRC / LVS / antenna | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | 0 |
| precheck, gate-level test (CI) | pass | pass | pass | pass |

Skew and hold at every corner (ns), final run (latency skew / hold WS / setup WS):
nom_tt 0.284 / 0.298 / 10.93, nom_ss 0.496 / 0.849 / 1.474, nom_ff 0.196 / 0.096 / 13.21,
min_tt 0.274 / 0.289 / 11.08, min_ss 0.480 / 0.830 / 1.743, min_ff 0.188 / 0.090 / 13.31,
max_tt 0.295 / 0.308 / 10.76, max_ss 0.512 / 0.866 / 1.180, max_ff 0.205 / 0.103 / 13.13.
lrc2 for comparison: max_ss 0.507 / 0.804 / 2.312, worst hold 0.067 (min_ff). Setup and hold are met at every
corner in both.

## Decision rule (owner, 1 Nov)

| condition | final run | met? |
|---|---|---|
| clock violations cleared | root fanout 16 → 2, root cap 0.237 → 0.017 pF; the remaining cap violation is a data net | **yes** |
| slew no worse than A (one data net, max_ss only, ~50 ps) | 13 nets at max_ss, 8 at nom_ss, worst +2.1 ns | **no** |

→ **B stops for this shuttle.** No gate-level/mutation sign-off work is started.

## What the final run shows (v3 input)

- **The CTS fix works in B too**: the root drives 2 instead of 16 and its cap violation is gone. It costs
  insertion delay (max 1.66 → 2.07 ns at max_ss) and 1.1 ns of setup slack.
- **The new slew violators are mostly long single-load nets**, several driven by hold buffers
  (`hold1126`, `hold1255`, `hold1401/1402`: buf_2 into 0.10–0.15 pF, fan-out 1) and fan-out buffers into
  0.08–0.16 pF; the worst is a21oi_2 into 0.151 pF. 0.15 pF at ~0.2 fF/µm is ~750 µm of wire for a single
  load. Wirelength rose 11 % (258k → 287k µm) and detailed routing took several times longer than lrc2.
  Why these nets became long (placement of the hold/fan-out buffers after the deeper clock tree, or routing
  detours at 73 % utilisation) is **[UNVERIFIED]**: not probed.
- **lrc2 alone was close**: one data net 15 ps worse than A, and the clock-root cap violation. A v3 attempt
  should start from lrc2 and fix only the clock root, not tighten the PnR slew limit at the same time; the two
  changes here were confounded in one run by the owner's one-run budget.
- **The root cause and its fix stand**: `LAYERS_RC` calibrated from extraction makes repair's estimate
  match sign-off (notes/v2b_01, v2b_02). Upstream status and the draft comment: `notes/drafts/`.

## Gates

| gate | date | status |
|---|---|---|
| root cause identified | 12 Nov 2026 | **met 1 Nov** |
| B fully signed off | 22 Nov 2026 | **not reached: B stopped 1 Nov by the owner's decision rule** |
