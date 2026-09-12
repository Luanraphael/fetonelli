#!/usr/bin/env python3
"""
Rebuilds index.html / v2.html from src/index.src.html by:
  1. injecting the right per-page snippets (tracking pixel, checkout
     URL(s), VTurb VSL, hero headline/subheadline, topbar text, offer
     section(s), VSL-gate script, <body> class),
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
    # v2.html only ("Trilhos de mesa" / "Jogos americanos" categories in
    # src/moldes-v2.html); simply unused -- not missing -- on index.html,
    # which still runs src/moldes-index.html's original flat 5-pair list.
    "__IMG_TRILHO1_MOLDE__": "src/img/trilho1_molde.b64",
    "__IMG_TRILHO1_PRONTO__": "src/img/trilho1_pronto.b64",
    "__IMG_TRILHO2_MOLDE__": "src/img/trilho2_molde.b64",
    "__IMG_TRILHO2_PRONTO__": "src/img/trilho2_pronto.b64",
    "__IMG_TRILHO3_MOLDE__": "src/img/trilho3_molde.b64",
    "__IMG_TRILHO3_PRONTO__": "src/img/trilho3_pronto.b64",
    "__IMG_JOGO1_MOLDE__": "src/img/jogo1_molde.b64",
    "__IMG_JOGO1_PRONTO__": "src/img/jogo1_pronto.b64",
    "__IMG_JOGO2_MOLDE__": "src/img/jogo2_molde.b64",
    "__IMG_JOGO2_PRONTO__": "src/img/jogo2_pronto.b64",
    "__IMG_JOGO3_MOLDE__": "src/img/jogo3_molde.b64",
    "__IMG_JOGO3_PRONTO__": "src/img/jogo3_pronto.b64",
}

# index.html and v2.html run different ad accounts, so each keeps its own
# tracking pixel and its own VTurb VSL (separate video = separate
# view/watch-time metrics per funnel).
#
# The two pages now run genuinely different experiences (as of this
# round of edits):
#   - index.html: the winning A/B setup -- VSL-gated reveal (body class
#     "gated"), single-price offer section, one checkout link.
#   - v2.html: back to "mini VSL + full sales page, always visible"
#     (body class "flat", no gate script), original-era headline +
#     subheadline, a new upper price teaser under the VSL, and a
#     two-tier offer section (R$10 moldes-only vs R$19,90 tudo) with
#     its own pair of checkout links. body class "flat" also hides the
#     old hero-badges list, which the new price teaser replaces.
PAGES = [
    {
        "out": "index.html",
        "body_class": "gated",
        "pixel": "src/pixel-a.html",
        "checkout_url": "https://pay.lowify.com.br/checkout.php?product_id=gODlv2",
        "vsl": "src/vsl-a.html",
        "headline": (
            "Este vídeo é apenas para mulheres que amam "
            '<span class="hl">Mesa Posta<svg class="hl-underline" viewBox="0 0 100 10" '
            'preserveAspectRatio="none" aria-hidden="true"><path d="M0 5 Q 50 10 100 5"/></svg></span> '
            "e sabem que ser Anfitriã vai muito além de pratos e talheres."
        ),
        "subhead": "src/subhead-empty.html",
        "topbar": 'Promoção Válida somente <strong class="topbar-hl">HOJE</strong> 09/09',
        "offer_block": "src/offer-index.html",
        "moldes": "src/moldes-index.html",
        "ident_section": "src/ident-index.html",
        "gate_script": "src/gate-vsl.html",
    },
    {
        "out": "v2.html",
        "body_class": "flat",
        "pixel": "src/pixel-b.html",
        "checkout_url": "https://payfast.greenn.com.br/9tabvy7/offer/NZhZFm?ch_id=143254",  # ticket 19,90 -- also the guarantee-section CTA target
        "checkout_url_10": "https://payfast.greenn.com.br/2tbv3by/offer/Xtm4Rv",
        "checkout_url_19": "https://payfast.greenn.com.br/9tabvy7/offer/NZhZFm?ch_id=143254",
        "vsl": "src/vsl-b.html",
        "headline": (
            "500 Moldes de Mesa Posta na Talagarça para "
            '<span class="hl">Anfitriãs de Sucesso<svg class="hl-underline" viewBox="0 0 100 10" '
            'preserveAspectRatio="none" aria-hidden="true"><path d="M0 5 Q 50 10 100 5"/></svg></span>.'
        ),
        "subhead": "src/subhead-v2.html",
        "topbar": 'Valor promocional válido apenas no dia <strong class="topbar-hl">11/09</strong>',
        "offer_block": "src/offer-v2.html",
        "moldes": "src/moldes-v2.html",
        "ident_section": "src/ident-v2.html",
        "gate_script": "src/gate-none.html",
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

    fragment = _inject(fragment, "__HEADLINE__", page["headline"], exactly=1)

    subhead_data = (ROOT / page["subhead"]).read_text(encoding="utf-8").strip()
    fragment = _inject(fragment, "__SUBHEAD__", subhead_data, exactly=1)

    fragment = _inject(fragment, "__TOPBAR__", page["topbar"], exactly=1)

    vsl_data = (ROOT / page["vsl"]).read_text(encoding="utf-8").strip()
    fragment = _inject(fragment, "__VSL__", vsl_data, exactly=1)

    offer_data = (ROOT / page["offer_block"]).read_text(encoding="utf-8").strip()
    fragment = _inject(fragment, "__OFFER_BLOCK__", offer_data, exactly=2)

    moldes_data = (ROOT / page["moldes"]).read_text(encoding="utf-8").strip()
    fragment = _inject(fragment, "__MOLDES_BLOCK__", moldes_data, exactly=1)

    ident_data = (ROOT / page["ident_section"]).read_text(encoding="utf-8").strip()
    fragment = _inject(fragment, "__IDENT_SECTION__", ident_data, exactly=1)

    gate_rel = page.get("gate_script")
    gate_data = (ROOT / gate_rel).read_text(encoding="utf-8").strip() if gate_rel else ""
    fragment = _inject(fragment, "__GATE_SCRIPT__", gate_data, exactly=1)

    # checkout links: __CHECKOUT__ is the "default" target (the guarantee
    # section button on both pages; also the only checkout token used
    # inside offer-index.html). __CHECKOUT_10__ / __CHECKOUT_19__ only
    # exist inside offer-v2.html, so they're only injected for pages that
    # declare them.
    fragment = _inject(fragment, "__CHECKOUT__", page["checkout_url"])
    if "checkout_url_10" in page:
        fragment = _inject(fragment, "__CHECKOUT_10__", page["checkout_url_10"], exactly=2)
    if "checkout_url_19" in page:
        fragment = _inject(fragment, "__CHECKOUT_19__", page["checkout_url_19"], exactly=2)

    # image tokens are optional per page now: index.html's moldes-index.html
    # and v2.html's moldes-v2.html each only reference a subset of
    # IMG_TOKENS (they don't share the same 5 sousplat pairs, and only
    # moldes-v2.html uses the trilho/jogo tokens), so a token simply not
    # appearing in this page's fragment is expected, not an error.
    for token, rel_path in IMG_TOKENS.items():
        if token not in fragment:
            continue
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
