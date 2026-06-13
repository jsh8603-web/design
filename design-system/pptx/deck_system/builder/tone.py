"""Action title tone validation — noun-form ending required.

Matches the editorial convention in the HTML system README:
    - Action titles use 명사형 종결 (noun-form Korean)
    - Avoid 평서문 (-다) and 합니다체 (-습니다)
    - Max ~40 characters

Violations log a warning to stderr but do NOT block the build.
"""
from __future__ import annotations
import sys


MAX_ACTION_TITLE_CHARS = 40

# Korean sentence-ending markers — these signal a 평서문 / 합니다체 title
# (whereas noun-ending titles end with 명사 or 한자어).
_BAD_ENDINGS = [
    "습니다", "합니다", "있다", "없다",
    "했다", "이다", "된다",
    "하다", "한다",
]


def validate_action_title(title: str) -> list[str]:
    """Return a list of warning strings.  Empty list = passes."""
    warnings: list[str] = []
    stripped = title.rstrip(" .!?")

    if len(stripped) > MAX_ACTION_TITLE_CHARS:
        warnings.append(
            f"Action title is {len(stripped)} chars "
            f"(limit {MAX_ACTION_TITLE_CHARS}): \"{stripped[:30]}…\""
        )

    for ending in _BAD_ENDINGS:
        if stripped.endswith(ending):
            warnings.append(
                f"Action title ends with '{ending}' — use 명사형 종결: "
                f"\"{stripped}\""
            )
            break

    return warnings


def warn_if_violations(title: str) -> None:
    """Print warnings to stderr.  Does not raise."""
    for w in validate_action_title(title):
        print(f"  ⚠  {w}", file=sys.stderr)
