"""CLI — V2.3-B with subcommands.

Commands:
    build SPEC -o OUT [--theme THEME] [--qa-report PATH] [--auto-fix]
    list-layouts [--category CAT]
    show-schema LAYOUT
    validate SPEC                # validate only, do not build
    themes
    init [OUTPUT_DIR]
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

from deck_system.builder import PresentationBuilder
from deck_system.builder.spec_normalizer import load_spec
from deck_system.builder.validation import LAYOUT_SCHEMAS, validate_layout_input
from deck_system.builder.registry import all_names
from deck_system.tokens import get_theme, THEMES
from deck_system.errors import DeckSystemError, InputValidationError


def _cmd_build(args) -> int:
    spec = load_spec(args.spec)
    theme = get_theme(args.theme)
    b = PresentationBuilder(theme=theme)
    if isinstance(spec, list):
        b.add_specs(spec)
    elif isinstance(spec, dict) and "slides" in spec:
        b.add_specs(spec["slides"])
    elif isinstance(spec, dict):
        b.add_spec(spec)
    else:
        raise InputValidationError(message=f"Bad spec shape: {type(spec).__name__}")
    if args.auto_fix:
        from deck_system.qa import run_autofix  # noqa: F401
        result = b.run_autofix(max_rounds=args.max_rounds)
        print(f"✓ Autofix: {len(result.actions)} actions / "
              f"{result.rounds} rounds", file=sys.stderr)
    out = b.save(args.output, qa_report_path=args.qa_report)
    print(f"✓ Saved: {out}", file=sys.stderr)
    return 0


def _cmd_list_layouts(args) -> int:
    names = all_names()
    if args.category:
        names = [n for n in names if args.category in n]
    for n in names:
        print(n)
    print(f"\nTotal: {len(names)}", file=sys.stderr)
    return 0


def _cmd_show_schema(args) -> int:
    schema = LAYOUT_SCHEMAS.get(args.layout)
    if schema is None:
        print(f"No schema registered for: {args.layout}", file=sys.stderr)
        print("Available layouts:", file=sys.stderr)
        for n in sorted(LAYOUT_SCHEMAS.keys()):
            print(f"  {n}", file=sys.stderr)
        return 2
    print(f"Layout: {schema.layout_name}")
    print("Fields:")
    for f in schema.fields:
        req = "REQUIRED" if f.required else "optional"
        bounds = ""
        if f.min_length:
            bounds += f" min={f.min_length}"
        if f.max_length is not None:
            bounds += f" max={f.max_length}"
        type_name = (
            " | ".join(t.__name__ for t in f.type) if isinstance(f.type, tuple)
            else (f.type.__name__ if f.type else "any")
        )
        print(f"  {f.name}: {type_name} ({req}){bounds}")
    if schema.examples:
        print("\nExample:")
        print(json.dumps(schema.examples[0], ensure_ascii=False, indent=2))
    return 0


def _cmd_validate(args) -> int:
    spec = load_spec(args.spec)
    if isinstance(spec, dict) and "slides" in spec:
        slides = spec["slides"]
    elif isinstance(spec, list):
        slides = spec
    else:
        slides = [spec]
    issues = 0
    for i, sl in enumerate(slides, 1):
        sl_copy = dict(sl)
        layout = sl_copy.pop("type", None)
        if not layout:
            print(f"  Slide {i}: no `type` field", file=sys.stderr)
            issues += 1
            continue
        try:
            _, warnings = validate_layout_input(layout, sl_copy)
            for w in warnings:
                print(f"  Slide {i} [{layout}] WARN: {w}", file=sys.stderr)
        except InputValidationError as e:
            print(f"  Slide {i} [{layout}] ERROR: {e.message}", file=sys.stderr)
            if e.expected:
                print(f"    Expected: {e.expected}", file=sys.stderr)
            if e.fix:
                print(f"    Fix: {e.fix}", file=sys.stderr)
            issues += 1
    print(f"\n{len(slides)} slides, {issues} issues", file=sys.stderr)
    return 1 if issues else 0


def _cmd_themes(args) -> int:
    seen = set()
    for name, theme in THEMES.items():
        canon = name.replace("-", "_")
        if id(theme) in seen:
            continue
        seen.add(id(theme))
        p = theme.palette
        print(f"{canon:12s} primary={p.primary} accent={p.accent}  "
              f"surface_inverse={p.surface_inverse}")
    return 0


def _cmd_init(args) -> int:
    out_dir = Path(args.output_dir or "fpna_deck_project")
    out_dir.mkdir(parents=True, exist_ok=True)
    template = {
        "deck_meta": {"theme": "modern"},
        "slides": [
            {"type": "cover", "title": "Q4 사업 리뷰",
             "subtitle": "FY26", "author": "FP&A", "date": "FY26.Q2"},
            {"type": "dark_navy_summary", "title": "x",
             "body": "Bottom line statement"},
            {"type": "closing", "title": "Thanks"},
        ],
    }
    spec_path = out_dir / "deck.json"
    spec_path.write_text(json.dumps(template, ensure_ascii=False, indent=2),
                          encoding="utf-8")
    print(f"✓ Wrote starter template: {spec_path}", file=sys.stderr)
    print(f"  Run: python -m deck_system.cli build {spec_path} -o out.pptx",
          file=sys.stderr)
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="fpna-deck")
    sub = parser.add_subparsers(dest="cmd")

    p_build = sub.add_parser("build", help="Render a .pptx from a JSON spec")
    p_build.add_argument("spec")
    p_build.add_argument("-o", "--output", required=True)
    p_build.add_argument("--theme", default="modern")
    p_build.add_argument("--qa-report", default=None)
    p_build.add_argument("--auto-fix", action="store_true")
    p_build.add_argument("--max-rounds", type=int, default=3)

    p_list = sub.add_parser("list-layouts", help="List registered layouts")
    p_list.add_argument("--category", default=None)

    p_show = sub.add_parser("show-schema", help="Print a layout's input schema")
    p_show.add_argument("layout")

    p_val = sub.add_parser("validate", help="Validate a spec without building")
    p_val.add_argument("spec")

    sub.add_parser("themes", help="List available themes")

    p_init = sub.add_parser("init", help="Write a starter spec template")
    p_init.add_argument("output_dir", nargs="?", default=None)

    # Legacy single-command form (no subcommand): treat as build
    parser.add_argument("--spec", default=None)
    parser.add_argument("-o", "--output", default=None)
    parser.add_argument("--theme", default="modern")
    parser.add_argument("--qa-report", default=None)
    parser.add_argument("--auto-fix", action="store_true")
    parser.add_argument("--max-rounds", type=int, default=3)

    args = parser.parse_args(argv)

    handlers = {
        "build": _cmd_build, "list-layouts": _cmd_list_layouts,
        "show-schema": _cmd_show_schema, "validate": _cmd_validate,
        "themes": _cmd_themes, "init": _cmd_init,
    }
    try:
        if args.cmd in handlers:
            return handlers[args.cmd](args)
        if args.spec and args.output:
            args.spec = args.spec
            return _cmd_build(args)
        parser.print_help()
        return 0
    except DeckSystemError as e:
        print(f"\n❌ {e}\n", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
