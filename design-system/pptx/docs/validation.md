# Input validation

Every layout has a `LayoutSchema` (in `builder/validation.py`) defining
which fields are required, what type they should be, and (for collections)
their length bounds. Validation runs inside `PresentationBuilder.add()`
before the spec is buffered, so bad input fails immediately with a clear
error.

## Error classes (`deck_system/errors.py`)

| Class | Raised when |
|-------|-------------|
| `DeckSystemError` | Base — never raised directly |
| `InputValidationError` | Spec field is missing, wrong type, or violates bounds |
| `CJKFontError` | East Asian font enforcement failed |
| `ThemeError` | Theme lookup / palette resolution failed |
| `LayoutOverflowError` | Input exceeds an `experiences.py` constant (e.g. too many donut segments) |
| `ImagePlaceholderError` | The image_placeholder helper could not render |

Each error carries:
- `layout_name` — which layout
- `slide_num` — 1-based index in the buffer (set by `Builder.add()`)
- `message` — short description
- `expected` / `got` — type or shape contract
- `fix` — suggested action
- `example` — working dict

## Example

```python
from deck_system import PresentationBuilder, MODERN, InputValidationError

b = PresentationBuilder(theme=MODERN)
b.add("cover", title="ok")           # slide 1 — fine

try:
    b.add("waterfall")               # slide 2 — missing items
except InputValidationError as e:
    print(e.layout_name)             # "waterfall"
    print(e.slide_num)                # 2
    print(e.expected)                 # "list"
    print(e.fix)                      # "Add `items=…` to your spec."
    print(e.example)                  # {"title": "x", "items": [...]}
```

## Pre-flight (CLI)

`validate` subcommand checks every slide without building:

```bash
python -m deck_system.cli validate examples/q4_review_spec.json
```

Exits 0 if clean, 1 if any errors. Warnings (over-cap lists) are
printed but do not fail.

## Adding a schema

When you register a new layout via `@register("foo")`, also add a
schema entry in `builder/validation.py`:

```python
_baseline("foo",
           _S("items", required=True, type=list, min_length=1, max_length=10),
           _S("unit", type=str),
           example={"title": "x", "items": [{"label": "a", "value": 1}]})
```

The test_robustness.py suite parametrizes over `LAYOUT_SCHEMAS.keys()`,
so the new entry gets ~4 automatic tests for free.
