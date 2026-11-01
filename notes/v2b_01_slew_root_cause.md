# v2b Step 1 — why B's slew violations survive repair (root cause)

Found 1 Nov 2026, 11 days before the 12 Nov gate. Method: the CI's own flow re-run locally, then the same
nets compared in repair's view and in the sign-off view. Diagnosis only; no fix has been tried.

## Tooling (gate rule 2)

Docker Desktop was not touched (no factory reset). The WSL2 Ubuntu 26.04 distro on this PC already runs
its own Docker engine, so `ghcr.io/librelane/librelane:3.0.14` was pulled there. Its LibreLane and OpenROAD
are the CI's builds byte for byte (same Nix store paths: `8y4m6wgn…-python3-3.13.9-env`, OpenROAD
2026-02-17), and the PDK is the CI's `8afc8346…` enabled with the image's `ciel`. Mounting the run and the
PDK at the CI's own paths lets LibreLane's Tcl run unmodified. Setup took about an hour.

`tools/slew_probe/probe.tcl` loads a run exactly as LibreLane's OpenROAD steps do (nine corners, base.sdc,
`set_rc.tcl`, `grt.tcl`) and reports in three views:

| mode | database | parasitics | what it shows |
|---|---|---|---|
| `pre` | input of post-GRT repair (step 39) | `estimate_parasitics -global_routing` | what repair saw before repairing |
| `grt` | output of post-GRT repair (step 41) | same estimate | what repair saw when it finished |
| `rcx` | final | the sign-off SPEFs | what sign-off STA sees |

Run: B base run 40698174384 (identical to v2b run 41295299103). **The `rcx` view reproduces CI's sign-off
exactly: 122 slew + 1 cap violations at max_ss, 96 + 1 at nom_ss.**

## Correction to notes/v2_05_b

v2_05 says post-GRT repair "reports 0 violations remaining". That was my misreading: the `Remaining`
column of `repair_design -verbose` counts down the nets still to visit (7401, 6401, … 0), not violations.
The flow never prints a slew count after repair. The measured equivalent is below: repair's own view at
the end shows 0 violations, so the conclusion (repair believes it is done) holds, now on evidence.

## Finding 1 (main cause): repair's wire capacitance is 2.0–2.8× too low per µm

| view | max_ss slew violations | nom_ss slew violations |
|---|---|---|
| `pre` (repair's view, before) | 0 | 0 |
| `grt` (repair's view, after) | 0 | 0 |
| `rcx` (sign-off) | 122 (+1 cap) | 96 (+1 cap) |

The ten worst nets, repair's estimate vs extraction at the same (nominal-RC) corner:

| driver | global-route length (µm) | routed length (µm) | estimated wire C (pF) | extracted wire C, nom (pF) | estimate (fF/µm) | extracted (fF/µm) |
|---|---|---|---|---|---|---|
| `_08422_/Y` | 207 | 162 | 0.0152 | 0.0340 | 0.073 | 0.209 |
| `_05646_/Y` | 338 | 275 | 0.0260 | 0.0566 | 0.077 | 0.206 |
| `_07447_/X` | 228 | 234 | 0.0198 | 0.0482 | 0.087 | 0.206 |
| `_11281_/Q` | 642 | 589 | 0.0485 | 0.0995 | 0.076 | 0.169 |
| `_07210_/X` | 255 | 252 | 0.0214 | 0.0434 | 0.084 | 0.172 |
| `_07528_/Y` | 117 | 110 | 0.0103 | 0.0235 | 0.088 | 0.214 |
| `_09423_/Y` | 269 | 227 | 0.0209 | 0.0445 | 0.078 | 0.196 |
| `_10503_/Y` | 214 | 194 | 0.0169 | 0.0400 | 0.079 | 0.206 |
| `_09114_/Y` | 276 | 223 | 0.0190 | 0.0400 | 0.069 | 0.179 |
| `_07179_/X` | 228 | 226 | 0.0199 | 0.0413 | 0.087 | 0.183 |

- **Route length is not the cause.** The global route is as long as, or longer than, the final route on
  every net (`_03411_`: 207 vs 162 µm).
- **The per-µm capacitance is.** LibreLane sets no per-corner `LAYERS_RC` for this PDK, so `set_rc.tcl`
  runs `set_wire_rc -signal -layers met1 met2 met3 met4 met5` with no `-corner`: one value for all nine
  corners, from the nominal tech LEF. Its capacitance per µm is area × width + 2 × edge:

  | layer | area C (pF/µm²) | edge C (pF/µm) | width (µm) | C per µm (fF/µm) |
  |---|---|---|---|---|
  | met1 | 2.578e-5 | 4.057e-5 | 0.14 | 0.085 |
  | met2 | 1.694e-5 | 3.776e-5 | 0.14 | 0.078 |
  | met3 | 1.237e-5 | 4.099e-5 | 0.30 | 0.086 |
  | met4 | 8.415e-6 | 3.668e-5 | 0.30 | 0.076 |
  | met5 | 6.321e-6 | 3.885e-5 | 1.60 | 0.088 |

  That is ~0.08 fF/µm, exactly what the estimate shows; extraction of the routed nets gives 0.17–0.21 fF/µm.
  The LEF model is an isolated wire; why extraction is ~2.5× higher (neighbour coupling in a routing grid at
  53–70 % usage is the obvious candidate) is **[UNVERIFIED]**: not separated out yet.
- **Corner is a minor term.** Extracted max-corner C is only 2–10 % above nominal (`max/est` 2.07–2.57 vs
  `nom/est` 2.03–2.43). The single nominal RC for all corners is not what breaks B.
- **Effect on the worst net:** `_08422_` (nand4_1) driving 0.0152 pF in repair's view has 0.60 ns slew at
  max_ss: legal, so it is left alone. With the extracted 0.0362 pF it is 1.21 ns.

## Finding 2 (contributes): post-GRT repair downsizes drivers on its optimistic view

Comparing the netlist before (step 37) and after (step 41) post-GRT repair: 24 cells were resized, **21 of
them down**. 3 of the 29 drivers that violate at sign-off were downsized there, including the worst:
`_08422_` nand4_2 → nand4_1 (repair's estimated slew 0.38 → 0.60 ns, still legal in its view),
`_07528_` a221oi_4 → a221oi_2, `_06036_` nor2_2 → nor2_1. The other 26 were not touched because the
estimate said they were fine. Why repair_design downsizes here is not yet read from the OpenROAD source
([UNKNOWN]); with a correct capacitance it would not have found the smaller cell legal.

## Why A got away with it and B does not

Same flow, same model error. B's 8 rows on 1.5× the area make the dot-product and decoder nets
100–600 µm long; at the real ~0.2 fF/µm, a `_2` gate on 200 µm is over 0.75 ns at ss, at the modelled
~0.08 fF/µm it is not. A's nets are shorter (2x2, 4 rows), so the same factor left one net over. A's
per-µm ratio has not been measured ([UNVERIFIED]; A's repo is not touched, its logs can be probed read-only).

## Gate status

| gate | date | status |
|---|---|---|
| root cause identified | 12 Nov 2026 | **identified 1 Nov**: findings 1 and 2 |
| B fully signed off | 22 Nov 2026 | not started: fix not yet chosen |
