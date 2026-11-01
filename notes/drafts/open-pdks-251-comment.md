# DRAFT — not posted. Comment for fossi-foundation/open-pdks#251

Target: https://github.com/fossi-foundation/open-pdks/issues/251 ("New RCX tables show significant increase
in parasitic capacitances", open since 2022-04-08). Related: #250 (removed `LAYERS_RC`/`VIAS_RC` from the
sky130 flow config, 2022). The owner decides whether to post. Nothing below has been sent anywhere.

Checked before drafting (1 Nov 2026): no LibreLane, Tiny Tapeout (`tt-support-tools`, `tt-gds-action`),
OpenROAD or chipfoundry/openlane2 issue covers this; LibreLane #996 ("Unit Clarity") is related but about
units only.

---

A data point from 2026, in case it helps settle this: the gap is still there with LibreLane 3.0.14
(OpenROAD 2026-02-17, open_pdks sky130A `8afc8346`), and in our design it was the whole reason post-route
max-slew violations survived design repair.

**Setup.** Tiny Tapeout SKY 26d template, 3x2 tiles, ~19k instances, 50 MHz, sky130_fd_sc_hd. Flow as
shipped: no `LAYERS_RC`, so `set_rc.tcl` falls back to `set_wire_rc` over met1–met5 from the nominal tech LEF
for all corners. Sign-off uses the OpenRCX `spef_extractor` rules per corner.

**What the resizer sees vs sign-off.** Re-running the flow's own steps in the 3.0.14 container on the CI run:
post-GRT `repair_design`'s estimate (`estimate_parasitics -global_routing`) shows 0 max-slew violations at
max_ss; sign-off STA on the RCX SPEFs shows 122. On the 10 worst nets the global-route length is equal to or
longer than the routed length, but the estimated wire capacitance is 2.0–2.6× lower than extracted, at the
same corner. It is the per-µm capacitance, not the length.

**Per-layer capacitance, least squares over 5,749 routed signal nets** (C_net = Σ c_layer × L_layer + c_via ×
n_via against the extracted total wire C; R² 0.996). fF/µm:

| layer | tech LEF (area×w + 2×edge) | fitted, nom | fitted, min | fitted, max | ORFS sky130hd `setRC.tcl` |
|---|---|---|---|---|---|
| met1 | 0.085 | 0.175 | 0.156 | 0.186 | 0.172 |
| met2 | 0.078 | 0.160 | 0.143 | 0.186 | 0.136 |
| met3 | 0.086 | 0.201 | 0.178 | 0.213 | 0.215 |
| met4 | 0.076 | 0.180 | 0.166 | 0.190 | 0.148 |

The same fit on resistance matches the tech LEF within ~1 % (met1 0.905 vs 0.893 Ω/µm), so only capacitance
is off. Our fitted values agree with ORFS's correlated sky130hd values (ORFS overrides the TLEF with
`set_layer_rc`), and are ~2.1–2.4× the TLEF, consistent with the 2–3× reported at the top of this issue.

**With the fitted values as design-level `LAYERS_RC`:** estimate / extraction on 3,610 nets became 0.97–1.09
for nets above 20 fF (was ~0.4), and post-route max-slew pins at max_ss went from 122 to 4 (one net). One
side effect worth knowing: with realistic capacitance, a large `GRT_DESIGN_REPAIR_MAX_SLEW_PCT` (55 %, which
we had raised to compensate for the underestimate) made post-GRT `repair_design` stop progressing (single
thread, >1.5 h, memory growing); 20 % finished in 15 s. Designs that tuned margins around the old estimate may
need to lower them if defaults change.

Fit script and probes: https://github.com/Muhammad-Sohair/tt-ternary-mac-v2b/tree/main/tools/slew_probe
(notes/v2b_01 and v2b_02 have the full data). Happy to run the fit on other designs if it would help choose
default `LAYERS_RC` values for sky130A.
