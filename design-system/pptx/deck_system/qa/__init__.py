"""QA + Auto-fix pipeline.

Inspired by likaku/qa.py + review.py.  Three modules:
  experiences  — hard-won constants
  checks       — 9 per-slide + 1 global check
  autofix      — 4-stage pipeline (brief → QA → fix → gate)
"""
from .experiences import *  # noqa: F401, F403
from .checks import QAReport, run_qa
from .autofix import AutofixPipeline, run_autofix

__all__ = ["QAReport", "run_qa", "AutofixPipeline", "run_autofix"]
