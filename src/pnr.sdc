# PnR-only constraints: LibreLane's base SDC with a tighter max transition.
# Signoff STA reads signoff.sdc (base SDC only, 0.75 ns), so sign-off numbers are not affected.
# With LAYERS_RC calibrated against sign-off extraction (notes/v2b_02), repair's slew estimate is
# realistic; 0.65 ns (13 % below the 0.75 ns limit) leaves margin for the remaining estimate spread
# without over-buffering. The repair steps' own slew margins still apply on top.
source $::env(SCRIPTS_DIR)/base.sdc
set_max_transition 0.65 [current_design]
