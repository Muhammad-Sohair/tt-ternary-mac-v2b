# v2b Step 2 — option 1: calibrated LAYERS_RC (owner's choice, 1 Nov)

Sign-off constraints unchanged throughout (`base.sdc`, 0.75 ns max transition, same STA corners).

## 1. Per-layer R and C from sign-off extraction

`tools/slew_probe/fit_layer_rc.py`, on baseline run 40698174384 (same design as v2b run 41295299103).
Every routed signal net ≥ 5 µm (**5,749 nets**, clock nets excluded): per-layer routed length from the final
DEF and via counts, least squares against the net's extracted total wire C and summed resistance (SPEF), per
RC corner. Not the 10 worst nets: the sample is the whole design.

| layer | nets using it | routed µm | C nom (fF/µm) | C min | C max | R nom (Ω/µm) | tech-LEF C / R |
|---|---|---|---|---|---|---|---|
| met1 | 5,178 | 95,464 | 0.1754 | 0.1557 | 0.1855 | 0.905 | 0.085 / 0.893 |
| met2 | 5,501 | 86,533 | 0.1597 | 0.1425 | 0.1861 | 0.901 | 0.078 / 0.893 |
| met3 | 843 | 46,936 | 0.2008 | 0.1777 | 0.2127 | 0.156 | 0.086 / 0.157 |
| met4 | 216 | 9,841 | 0.1795 | 0.1660 | 0.1903 | 0.158 | 0.076 / 0.157 |

Fit quality (nom): C R² 0.996, median error 5.6 %; R R² 1.000. Resistance already matched the tech LEF; only
capacitance was off (2.1–2.4×). Values go into `LAYERS_RC` as pF/µm and kΩ/µm (liberty units; LibreLane's RC
dump confirms 1 µm distance unit), `nom_*`, `min_*`, `max_*`.

## 2. The override takes effect

- LibreLane's `OpenROAD.DumpRCValues` report shows the resizer's per-layer values equal to the fitted ones
  (met1 C 1.754e-4 pF/µm vs tech LEF 8.47e-5).
- Repair's own estimate before post-GRT repair now sees 94 slew violations (it saw 0 with LEF RC).
- **Estimate / extraction** (post-GRT repair output vs final nom SPEF, all 3,610 signal nets with extracted
  wire C > 2 fF; `tools/slew_probe/estimate_caps.*`):

  | extracted wire C | nets | median ratio |
  |---|---|---|
  | > 50 fF | 57 | 0.97 |
  | 20–50 fF | 507 | 1.09 |
  | 10–20 fF | 680 | 1.15 |
  | 2–10 fF | 2,366 | 1.40 |
  | all (total C) | 3,610 | 1.21 |

  Long nets, the ones that set slew, are at ~1.0 (was ~0.4). Short nets are over-estimated (global-route
  length is coarse at that scale), the safe direction.
- Side effects: `li1` and via resistance read 0 in the resizer because `LAYERS_RC`/`VIAS_R` did not list them.
  A replay with `li1` added behaved the same; not yet corrected.

## 3. lrc1 hung; one adjustment (lrc2)

lrc1 (`LAYERS_RC` only, CI 41303043155) hung in post-GRT repair: locally 1 h 27 min of CPU on one thread,
memory 1.8 → 2.4 GB, stuck at iteration 1,000 of 7,484 (the step took 44 s in the baseline). Cancelled.
Replaying only that step on the run's own pre-repair ODB (`tools/slew_probe/replay*`, 10 min cap each):

| replay | violations seen before repair | result |
|---|---|---|
| LEF RC, margin 55 % (control) | 0 | 9 s |
| `LAYERS_RC`, margin 55 % | 94 | hangs at iteration 1,000 |
| `LAYERS_RC` + `li1`, margin 55 % | 94 | hangs at iteration 1,000 |
| `LAYERS_RC`, margin 20 % | 94 | 15 s, 0 violations left (estimated) |

`GRT_DESIGN_REPAIR_MAX_SLEW_PCT` 55 was set earlier to compensate for the underestimate (repair to 0.34 ns);
on realistic loads it never terminates. **The one adjustment: 55 → 20** (lrc2, branch `eval/lrc2`).

## 4. Result: lrc2 (CI 41309116865, identical to the local run)

| metric | baseline 41295299103 | lrc2 41309116865 | A (`signoff-a`) |
|---|---|---|---|
| slew pins max_ss / nom_ss | 122 / 96 | **4 / 0** | 5 / 0 |
| worst slew over limit | +462 ps (28 nets) | +65 ps, 1 net (`f_samp[0]`, driver `_11281_` dfxtp_2, ~590 µm) | +50.5 ps, 1 net |
| max-cap violations | 1 (clock root) | 1 (clock root `clkbuf_0_clk`, 0.237 / 0.2 pF at max_ss) | 0 |
| max-fanout (own limit 8) | 2 | 4 (clock root 16; three buffers at 9) | 2 (clock root 16, one at 9) |
| utilisation | 69.74 % | 71.21 % | 63.8 % |
| timing-repair buffers | 1,260 | 1,280 | — |
| instances | 19,623 | 19,157 | — |
| setup WS (worst, max_ss) | +2.481 ns | +2.312 ns | +4.883 ns |
| hold WS (worst, min_ff) | +0.093 ns | +0.067 ns | +0.103 ns |
| magic DRC / route DRC / LVS / antenna | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 |
| precheck, gate-level test (CI) | pass | pass | pass |

Setup / hold WS at every corner (ns), lrc2: nom_tt 11.49 / 0.284, nom_ss 2.533 / 0.796, nom_ff 13.57 / 0.068,
min_tt 11.61 / 0.282, min_ss 2.745 / 0.788, min_ff 13.65 / 0.067, max_tt 11.33 / 0.286, max_ss 2.312 / 0.804,
max_ff 13.50 / 0.070.

**Not yet at A's standard:** the slew residual is 15 ps worse than A's, and the clock root has a max-cap
violation A did not have. Hold is positive everywhere but lower than A's.
