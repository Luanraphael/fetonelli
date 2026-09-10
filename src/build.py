#!/usr/bin/env python3
"""
Rebuilds index.html / v2.html from src/index.src.html by:
  1. injecting the right per-page snippets (tracking pixel, checkout URL,
     VTurb VSL, hero headline/subheadline, VSL-gate script, <body> class
     -- two ad accounts, two funnels, same base page, each with its own
     tracking, its own video and, on v2, a delayed reveal tied to real
     VSL watch time),
  2. inlining fonts and images as base64 data URIs (the page is fully
     self-contained, with no external requests), then
  3. wrapping the result in a complete, valid HTML5 document (doctype,
     <html lang="pt-BR">, <head> with charset + viewport meta, <body>).

src/index.src.html is kept as a head-less fragment (title + pixel
placeholder + style, then body content) -- that's the format Claude's
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
src/img/, or any of the per-page snippets referenced in PAGES below),
then re-run this script to regenerate both index.html and v2.html.
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

# index.html and v2.html run different ad accounts, so each keeps its own
# tracking pixel, its own checkout link and its own VTurb VSL (separate
# video = separate view/watch-time metrics per funnel). Both pages now
# share the exact same lead experience (this is the A/B winner: the VSL
# retained 40% more engagement gated this way): the same headline, no
# subheadline, and a VSL-gated reveal where the rest of the page + the
# topbar only appear once that page's own VSL reaches 02:10 of real watch
# time (src/gate-vsl.html, shared -- it keys its sessionStorage flag off
# location.pathname so the two pages don't share unlock state).
GATED_HEADLINE = (
    "Este vídeo é apenas para mulheres que amam Mesa Posta e "
    "sabem que ser Anfitriã vai muito além de pratos e talheres."
)

PAGES = [
    {
        "out": "index.html",
        "body_class": "page-v2",
        "pixel": "src/pixel-a.html",
        "checkout_url": "https://pay.lowify.com.br/checkout.php?product_id=gODlv2",
        "vsl": "src/vsl-a.html",
        "headline": GATED_HEADLINE,
        "subhead": "src/subhead-empty.html",
        "gate_script": "src/gate-vsl.html",
    },
    {
        "out": "v2.html",
        "body_class": "page-v2",
        "pixel": "src/pixel-b.html",
        "checkout_url": "https://payfast.greenn.com.br/redirect/314478",
        "vsl": "src/vsl-b.html",
        "headline": GATED_HEADLINE,
        "subhead": "src/subhead-empty.html",
        "gate_script": "src/gate-vsl.html",
    },
]

HEAD_CLOSE_MARKER = "</style>"


def _inject(fragment, token, value, exactly=None):
    count = fragment.count(token)
    if exactly is not None:
        if count != exactly:
            raise SystemExit(f"expected exactly {exactly} occurrence(s) of {token!r}, found {count}")
    elif count < 1:
        raise SystemExit(f"expected at least 1 occurrence of {token!r}, found {count}")
    return fragment.replace(token, value)


def build_page(page):
    out_path = ROOT / page["out"]

    fragment = SRC.read_text(encoding="utf-8")

    pixel_data = (ROOT / page["pixel"]).read_text(encoding="utf-8").strip()
    fragment = _inject(fragment, "__PIXEL__", pixel_data)

    fragment = _inject(fragment, "__CHECKOUT__", page["checkout_url"])

    vsl_data = (ROOT / page["vsl"]).read_text(encoding="utf-8").strip()
    fragment = _inject(fragment, "__VSL__", vsl_data, exactly=1)

    fragment = _inject(fragment, "__HEADLINE__", page["headline"], exactly=1)

    subhead_data = (ROOT / page["subhead"]).read_text(encoding="utf-8").strip()
    fragment = _inject(fragment, "__SUBHEAD__", subhead_data, exactly=1)

    gate_data = (ROOT / page["gate_script"]).read_text(encoding="utf-8").strip()
    fragment = _inject(fragment, "__GATE_SCRIPT__", gate_data, exactly=1)

    for token, rel_path in IMG_TOKENS.items():
        data = (ROOT / rel_path).read_text(encoding="utf-8").strip()
        fragment = _inject(fragment, token, data)

    split_at = fragment.index(HEAD_CLOSE_MARKER) + len(HEAD_CLOSE_MARKER)
    head_part = fragment[:split_at]   # <title>...</title>\n<pixel>\n<style>...</style>
    body_part = fragment[split_at:]   # everything after: topbar, svg sprite, main, footer, scripts

    body_class = page.get("body_class", "")
    body_open_tag = f'<body class="{body_class}">' if body_class else "<body>"

    document = (
        "<!DOCTYPE html>\n"
        '<html lang="pt-BR">\n'
        "<head>\n"
        '<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        f"{head_part}\n"
        "</head>\n"
        f"{body_open_tag}\n"
        f"{body_part.strip()}\n"
        "</body>\n"
        "</html>\n"
    )
    out_path.write_text(document, encoding="utf-8")
    print(f"wrote {out_path} ({len(document):,} bytes)")


def main():
    for page in PAGES:
        build_page(page)


if __name__ == "__main__":
    main()
