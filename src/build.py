#!/usr/bin/env python3
"""
Rebuilds index.html / v2.html from src/index.src.html by:
  1. injecting the right Meta Pixel snippet for that specific page (two
     ad accounts, two pixels, same offer -> two identical pages, each
     with its own tracking),
  2. inlining fonts and images as base64 data URIs (the page is fully
     self-contained, with no external requests), then
  3. wrapping the result in a complete, valid HTML5 document (doctype,
     <html lang="pt-BR">, <head> with charset + viewport meta, <body>).

src/index.src.html is kept as a head-less fragment (title + pixel
placeholder + style, then body content) — that's the format Claude's
Artifact tool expects when previewing it directly, since Artifacts wrap
fragments in their own skeleton automatically. index.html / v2.html are
the real, standalone deploy targets (GitHub Pages / Vercel / any static
host), so they need the full document shell and, critically, the
viewport meta tag: without it, mobile browsers render at a fake
desktop-width viewport and shrink the whole page to fit, which breaks
every mobile breakpoint in the CSS.

Usage:
    python3 src/build.py

Run from the repo root. Edit src/index.src.html (or swap files in
src/img/, or the src/pixel-*.html snippets), then re-run this script to
regenerate both index.html and v2.html.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "src" / "index.src.html"

IMG_TOKENS = {
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

# (output document, pixel snippet file, checkout URL, VSL snippet file)
# index.html and v2.html run different ad accounts, so each now gets its
# own tracking pixel, its own checkout link, and its own VTurb VSL
# (separate video = separate view/watch-time metrics per funnel).
PAGES = [
    ("index.html", "src/pixel-a.html", "https://payfast.greenn.com.br/2tbv3by/offer/hHJI7A?ch_id=143142", "src/vsl-a.html"),
    ("v2.html", "src/pixel-b.html", "https://payfast.greenn.com.br/191300/offer/S0U1Jk", "src/vsl-b.html"),
]

HEAD_CLOSE_MARKER = "</style>"


def build_page(out_rel, pixel_rel, checkout_url, vsl_rel):
    out_path = ROOT / out_rel

    fragment = SRC.read_text(encoding="utf-8")

    pixel_data = (ROOT / pixel_rel).read_text(encoding="utf-8").strip()
    count = fragment.count("__PIXEL__")
    if count < 1:
        raise SystemExit(f"expected at least 1 occurrence of '__PIXEL__', found {count}")
    fragment = fragment.replace("__PIXEL__", pixel_data)

    count = fragment.count("__CHECKOUT__")
    if count < 1:
        raise SystemExit(f"expected at least 1 occurrence of '__CHECKOUT__', found {count}")
    fragment = fragment.replace("__CHECKOUT__", checkout_url)

    vsl_data = (ROOT / vsl_rel).read_text(encoding="utf-8").strip()
    count = fragment.count("__VSL__")
    if count != 1:
        raise SystemExit(f"expected exactly 1 occurrence of '__VSL__', found {count}")
    fragment = fragment.replace("__VSL__", vsl_data)

    for token, rel_path in IMG_TOKENS.items():
        data = (ROOT / rel_path).read_text(encoding="utf-8").strip()
        count = fragment.count(token)
        if count < 1:
            raise SystemExit(f"expected at least 1 occurrence of {token!r}, found {count}")
        fragment = fragment.replace(token, data)

    split_at = fragment.index(HEAD_CLOSE_MARKER) + len(HEAD_CLOSE_MARKER)
    head_part = fragment[:split_at]   # <title>...</title>\n<pixel>\n<style>...</style>
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
    out_path.write_text(document, encoding="utf-8")
    print(f"wrote {out_path} ({len(document):,} bytes)")


def main():
    for out_rel, pixel_rel, checkout_url, vsl_rel in PAGES:
        build_page(out_rel, pixel_rel, checkout_url, vsl_rel)


if __name__ == "__main__":
    main()
