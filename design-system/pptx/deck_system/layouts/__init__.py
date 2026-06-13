"""Layout implementations — one function per slide type.

Importing this module triggers @register on every layout.
"""
from . import structure          # noqa: F401
from . import data_table         # noqa: F401
from . import data_special       # noqa: F401  pareto, gauge added v0.2
from . import summary            # noqa: F401
from . import data_chart         # noqa: F401  v0.2
from . import compare            # noqa: F401  v0.2
from . import narrative          # noqa: F401  v0.2
from . import matrix             # noqa: F401  v0.2
from . import process            # noqa: F401  v0.2
from . import org                # noqa: F401  v0.2
from . import v21_additions      # noqa: F401  V2.1: 9 layouts
from . import v22_additions      # noqa: F401  V2.2: 8 layouts
from . import v23_additions      # noqa: F401  V2.3-A: 8 layouts
from . import fpna_charts        # noqa: F401  FP&A handoff charts: bullet
from . import fc_tornado         # noqa: F401
from . import fc_pvm_bridge      # noqa: F401
from . import fc_cohort_heatmap  # noqa: F401
from . import fc_combo           # noqa: F401
from . import fc_driver_tree     # noqa: F401
from . import fc_scatter         # noqa: F401
from . import fc_scenario_summary  # noqa: F401
from . import fc_overlapping_line  # noqa: F401
from . import fc_heatmap         # noqa: F401
from . import fc_treemap         # noqa: F401
from . import fc_breakeven       # noqa: F401
