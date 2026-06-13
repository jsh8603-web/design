#!/usr/bin/env python3
"""
serve.py — local static preview server for the slides-grab design system.

Many HTML references in this repo use native ES modules (`<script type="module">`)
and `@font-face` with relative `.woff2` paths. Browsers refuse ES-module imports
over the `file://` protocol, so opening those files by double-click shows a blank
slide. Run this tiny server from the PROJECT ROOT instead:

    python serve.py            # serves http://localhost:8000/
    python serve.py --open     # also opens the design-system index in your browser
    python serve.py --port 9000

Then browse to any reference, e.g.:
    http://localhost:8000/mck/slides/index.html
    http://localhost:8000/aesthetics/index.html
    http://localhost:8000/ui_kits/editor/index.html

Stop with Ctrl-C. Pure standard library — no pip install needed.
"""
from __future__ import annotations

import argparse
import http.server
import socketserver
import threading
import webbrowser
from functools import partial
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# A couple of landing pages worth opening first, in priority order.
DEFAULT_OPEN = [
    "mck/slides/index.html",
    "aesthetics/index.html",
    "preview/integration-overview.html",
    "README.md",
]


class Handler(http.server.SimpleHTTPRequestHandler):
    """Static handler with correct MIME types for module JS, fonts and SVG."""

    # SimpleHTTPRequestHandler already knows most types; pin the ones that
    # commonly break ES-module loading and font rendering.
    extensions_map = {
        **http.server.SimpleHTTPRequestHandler.extensions_map,
        ".js": "text/javascript",
        ".mjs": "text/javascript",
        ".css": "text/css",
        ".svg": "image/svg+xml",
        ".woff2": "font/woff2",
        ".woff": "font/woff",
        ".json": "application/json",
        ".webmanifest": "application/manifest+json",
    }

    def end_headers(self):
        # No caching while iterating locally, so edits show on reload.
        self.send_header("Cache-Control", "no-store, max-age=0")
        super().end_headers()

    def log_message(self, fmt, *args):  # quieter console
        if "404" in (fmt % args):
            super().log_message(fmt, *args)


def _first_existing(candidates):
    for rel in candidates:
        if (ROOT / rel).exists():
            return rel
    return ""


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", type=int, default=8000, help="port (default 8000)")
    ap.add_argument("--open", action="store_true",
                    help="open the design-system index in your browser")
    args = ap.parse_args(argv)

    handler = partial(Handler, directory=str(ROOT))
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", args.port), handler) as httpd:
        base = f"http://localhost:{args.port}/"
        print(f"slides-grab design system → {base}")
        print(f"  serving from: {ROOT}")
        landing = _first_existing(DEFAULT_OPEN)
        if landing:
            print(f"  try:          {base}{landing}")
        print("  Ctrl-C to stop.")
        if args.open and landing:
            threading.Timer(0.4, lambda: webbrowser.open(base + landing)).start()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nstopped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
