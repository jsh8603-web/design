"""Master adapter — profile an existing .pptx to extract design tokens.

Inspired by tristan-mcinnis/pptx-from-layouts-skill/profile.py.

Workflow:
    profile = profile_master("/path/to/company_master.pptx")
    # profile is a dict with: color_scheme, font_scheme, slide_master_dims
    # Save it as JSON, then feed to generate_theme_from_profile() to emit
    # a theme module that plugs into the [data-theme="company"] slot.
"""
from __future__ import annotations
from pathlib import Path
from typing import Optional
import json

from pptx import Presentation
from pptx.oxml.ns import qn


def profile_master(pptx_path: str | Path) -> dict:
    """Extract design tokens from a .pptx master.

    Returns a dict:
        {
          "source": "path/to/master.pptx",
          "color_scheme": { "bg1": "#FFFFFF", "tx1": "#000000",
                            "bg2": "...", "tx2": "...",
                            "accent1": "...", "accent2": "..." },
          "font_scheme": { "major": "Arial", "minor": "Arial" },
          "slide_master_dims": { "width_in": 13.333, "height_in": 7.5 },
          "n_slides": 14,
          "n_masters": 1,
        }
    """
    pptx_path = Path(pptx_path)
    if not pptx_path.exists():
        raise FileNotFoundError(f"PPTX not found: {pptx_path}")

    prs = Presentation(str(pptx_path))

    # ── Color scheme: read from theme XML ──────────────────────────────
    colors = {}
    try:
        master = prs.slide_masters[0]
        # The theme is reachable via the master's part
        for theme_part in master.part.rels.values():
            if "theme" in theme_part.reltype:
                theme_el = theme_part.target_part.element
                clr_scheme = theme_el.find(
                    qn("a:themeElements") + "/" + qn("a:clrScheme")
                )
                if clr_scheme is not None:
                    for child in clr_scheme:
                        # Each child is a:dk1, a:lt1, a:accent1, ..., a:accent6
                        tag = child.tag.split("}")[-1]  # strip namespace
                        # Find a:srgbClr or a:sysClr
                        srgb = child.find(qn("a:srgbClr"))
                        sys_c = child.find(qn("a:sysClr"))
                        if srgb is not None:
                            colors[tag] = "#" + srgb.get("val").upper()
                        elif sys_c is not None:
                            colors[tag] = "#" + (sys_c.get("lastClr") or "000000").upper()
                break
    except Exception:
        pass

    # Map a:lt1/a:dk1 → bg1/tx1 (OOXML convention)
    color_scheme = {
        "bg1": colors.get("lt1", "#FFFFFF"),
        "tx1": colors.get("dk1", "#000000"),
        "bg2": colors.get("lt2", "#F0F0F0"),
        "tx2": colors.get("dk2", "#2C2C2C"),
        "accent1": colors.get("accent1", "#1A2332"),
        "accent2": colors.get("accent2", "#E87722"),
        "accent3": colors.get("accent3", "#2E844A"),
        "accent4": colors.get("accent4", "#C5394A"),
        "accent5": colors.get("accent5", "#666666"),
        "accent6": colors.get("accent6", "#B0B0B0"),
    }

    # ── Font scheme ────────────────────────────────────────────────────
    fonts = {"major": "Pretendard", "minor": "Pretendard"}
    try:
        for theme_part in master.part.rels.values():
            if "theme" in theme_part.reltype:
                theme_el = theme_part.target_part.element
                font_scheme = theme_el.find(
                    qn("a:themeElements") + "/" + qn("a:fontScheme")
                )
                if font_scheme is not None:
                    major = font_scheme.find(
                        qn("a:majorFont") + "/" + qn("a:latin")
                    )
                    minor = font_scheme.find(
                        qn("a:minorFont") + "/" + qn("a:latin")
                    )
                    if major is not None and major.get("typeface"):
                        fonts["major"] = major.get("typeface")
                    if minor is not None and minor.get("typeface"):
                        fonts["minor"] = minor.get("typeface")
                break
    except Exception:
        pass

    # ── Master dimensions ──────────────────────────────────────────────
    dims = {
        "width_in": prs.slide_width / 914400,
        "height_in": prs.slide_height / 914400,
    }

    return {
        "source": str(pptx_path),
        "color_scheme": color_scheme,
        "font_scheme": fonts,
        "slide_master_dims": dims,
        "n_slides": len(prs.slides),
        "n_masters": len(prs.slide_masters),
    }


def write_profile_json(profile: dict, out_path: str | Path) -> Path:
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(profile, fh, ensure_ascii=False, indent=2)
    return out


# ─── CLI ───────────────────────────────────────────────────────────

def main(argv=None):
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        prog="deck_system.adapter.profile",
        description="Profile a .pptx master into design tokens",
    )
    parser.add_argument("pptx_path", help="Source .pptx file")
    parser.add_argument("--output-dir", default="deck_system/tokens/",
                        help="Where to write theme_<name>.py (and profile JSON)")
    parser.add_argument("--name", default="company",
                        help="Theme slot name (default 'company')")
    parser.add_argument("--json-only", action="store_true",
                        help="Only write profile JSON, skip theme module")
    args = parser.parse_args(argv)

    profile = profile_master(args.pptx_path)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / f"_{args.name}_profile.json"
    write_profile_json(profile, json_path)
    print(f"✓ Profile: {json_path}", file=sys.stderr)

    if not args.json_only:
        from deck_system.adapter.theme_from_profile import generate_theme_from_profile
        py_path = out_dir / f"theme_{args.name}.py"
        generate_theme_from_profile(profile, py_path, theme_var_name=args.name.upper())
        print(f"✓ Theme: {py_path}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
