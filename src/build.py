#!/usr/bin/env python3
"""
Rebuilds index.html from src/index.src.html by:
  1. inlining fonts and images as base64 data URIs (the page is fully
     self-contained, with no external requests), then
  2. wrapping the result in a complete, valid HTML5 document (doctype,
     <html lang="pt-BR">, <head> with charset + viewport meta, <body>).

src/index.src.html is kept as a head-less fragment (title + style, then
body content) — that's the format Claude's Artifact tool expects when
previewing it directly, since Artifacts wrap fragments in their own
skeleton automatically. index.html is the real, standalone deploy target
(GitHub Pages / Vercel / any static host), so it needs the full document
shell and, critically, the viewport meta tag: without it, mobile browsers
render at a fake desktop-width viewport and shrink the whole page to fit,
which breaks every mobile breakpoint in the CSS.

Usage:
    python3 src/build.py

Run from the repo root. Edit src/index.src.html (or swap files in
src/img/), then re-run this script to regenerate index.html.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "src" / "index.src.html"
OUT = ROOT / "index.html"

TOKENS = {
    "__INTER_B64__": "src/fonts/inter-latin.b64",
    "__MANROPE_B64__": "src/fonts/manrope-latin.b64",
    "__IMG_PERFIL__": "src/img/perfil.b64",
    "__IMG_MOCKUPCTA__": "src/img/mockupcta.b64",
    "__IMG_MOLDE1__": "src/img/molde1.b64",
    "__IMG_MOLDE2__": "src/img/molde2.b64",
    "__IMG_MOLDE3__": "src/img/molde3.b64",
    "__IMG_MOLDE4__": "src/img/molde4.b64",
    "__IMG_MOLDE5__": "src/img/molde5.b64",
    "__IMG_SOUSPLAT1__": "src/img/sousplat1.b64",
    "__IMG_SOUSPLAT2__": "src/img/sousplat2.b64",
    "__IMG_SOUSPLAT3__": "src/img/sousplat3.b64",
    "__IMG_SOUSPLAT4__": "src/img/sousplat4.b64",
    "__IMG_SOUSPLAT5__": "src/img/sousplat5.b64",
    "__IMG_BONUS1__": "src/img/bonus1.b64",
    "__IMG_BONUS2__": "src/img/bonus2.b64",
    "__IMG_BONUS3__": "src/img/bonus3.b64",
    "__IMG_BONUS4__": "src/img/bonus4.b64",
    "__IMG_BONUS5__": "src/img/bonus5.b64",
}

HEAD_CLOSE_MARKER = "</style>"


def main():
    fragment = SRC.read_text(encoding="utf-8")
    for token, rel_path in TOKENS.items():
        data = (ROOT / rel_path).read_text(encoding="utf-8").strip()
        count = fragment.count(token)
        if count < 1:
            raise SystemExit(f"expected at least 1 occurrence of {token!r}, found {count}")
        fragment = fragment.replace(token, data)

    split_at = fragment.index(HEAD_CLOSE_MARKER) + len(HEAD_CLOSE_MARKER)
    head_part = fragment[:split_at]   # <title>...</title>\n<style>...</style>
    body_part = fragment[split_at:]   # everything after: svg sprite, main, footer, script

    document = (
        "<!DOCTYPE html>\n"
        '<html lang="pt-BR">\n'
        "<head>\n"
        '<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        f"{head_part}\n"
        "</head>\n"
        "<body>\n"
        f"{body_part.strip()}\n"
        "</body>\n"
        "</html>\n"
    )
    OUT.write_text(document, encoding="utf-8")
    print(f"wrote {OUT} ({len(document):,} bytes)")


if __name__ == "__main__":
    main()
