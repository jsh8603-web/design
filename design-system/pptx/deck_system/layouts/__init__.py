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
