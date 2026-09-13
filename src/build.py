#!/usr/bin/env python3
"""
Rebuilds index.html / v2.html from src/index.src.html by:
  1. injecting the right per-page snippets (tracking pixel, checkout
     URL(s), VTurb VSL, hero headline/subheadline, topbar text, offer
     section(s), moldes/identification/bonus/about/guarantee/FAQ/footer
     blocks, VSL-gate script, <body> class, <html lang>, <title>),
  2. inlining fonts and images as base64 data URIs (the page is fully
     self-contained, with no external requests), then
  3. wrapping the result in a complete, valid HTML5 document (doctype,
     <html lang="...">, <head> with charset + viewport meta, <body>).

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
    # src/moldes-v2.html, also reused translated by src/moldes-latam.html);
    # simply unused, not missing, wherever a page's fragment doesn't
    # reference them.
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
    # index.html (LATAM) only -- new Spanish-localized bonus mockups +
    # main offer mockup, from the "Mockups latam Mesa puesta" folder.
    "__IMG_LATAM_BONUS1__": "src/img/latam_bonus1.b64",
    "__IMG_LATAM_BONUS2__": "src/img/latam_bonus2.b64",
    "__IMG_LATAM_BONUS3__": "src/img/latam_bonus3.b64",
    "__IMG_LATAM_BONUS4__": "src/img/latam_bonus4.b64",
    "__IMG_LATAM_BONUS5__": "src/img/latam_bonus5.b64",
    "__IMG_LATAM_BONUS6__": "src/img/latam_bonus6.b64",
    "__IMG_LATAM_BONUS7__": "src/img/latam_bonus7.b64",
    "__IMG_LATAM_MOCKUPCTA__": "src/img/latam_mockupcta.b64",
}

# images used ONLY inside src/bonus-extra-v2.html (the 2 v2-only extra
# bonuses -- a 3rd one, bonus6.png/"Lista Completa De Materiais", was
# removed for duplicating the existing Bônus 2, so this dict keeps the
# asset filenames bonus7/bonus8 even though the page now labels them
# "Bônus 6"/"Bônus 7"; renaming files just to match display numbers
# isn't worth the churn). Deliberately NOT part of IMG_TOKENS above:
# that dict is applied unconditionally to every page's fragment, but
# these tokens only exist inside a snippet that most pages never
# include, so they're resolved locally, inside bonus-extra-v2.html's
# own text, before it's spliced into the shared fragment (see
# build_page below).
BONUS_EXTRA_IMG_TOKENS = {
    "__IMG_BONUS7__": "src/img/bonus7.b64",
    "__IMG_BONUS8__": "src/img/bonus8.b64",
}

# index.html is now the Spanish-LATAM version of this offer (new VSL,
# single US$10 "Premium" tier, Hotmart checkout, Meta Pixel + UTMIFY +
# UTM tracking, new LATAM mockups) built structurally off of v2.html
# (moldes by category, identification section, bonus section including
# the 2 extra bonuses, "antes/depois" transformation section, "flat"
# body class -- no VSL-gate delay). v2.html itself is UNTOUCHED: every
# section it uses that also exists on index.html now comes from a
# "-shared.html" file that is a byte-for-byte extraction of what used
# to be inline here, so v2.html's rendered output does not change.
PAGES = [
    {
        "out": "index.html",
        "lang": "es-419",
        "title": "+500 Moldes para Mesa Puesta",
        "body_class": "flat",
        "pixel": "src/pixel-latam.html",
        "checkout_url": "https://pay.hotmart.com/Q107588529E?checkoutMode=10",
        "vsl": "src/vsl-latam.html",
        "headline": (
            "500 Moldes de Mesa Puesta en Malla para "
            '<span class="hl">Anfitrionas de Éxito<svg class="hl-underline" viewBox="0 0 100 10" '
            'preserveAspectRatio="none" aria-hidden="true"><path d="M0 5 Q 50 10 100 5"/></svg></span>.'
        ),
        "subhead": "src/subhead-latam.html",
        "topbar": 'Precio promocional válido solo el día <strong class="topbar-hl">13/09</strong>',
        "viewer_suffix": "viendo esto ahora",
        "hero_cta_text": "¡Quiero mis Moldes Ahora!",
        "hero_cta_note": "Acceso liberado al instante, directo a tu WhatsApp y email.",
        "hero_badges": "src/hero-badges-latam.html",
        "offer_block": "src/offer-latam.html",
        "offer_block_2": "src/offer-latam.html",
        "moldes": "src/moldes-latam.html",
        "ident_section": "src/ident-latam.html",
        "composicao_section": "src/composicao-latam.html",
        "bonus_section": "src/bonus-latam.html",
        "about_section": "src/about-latam.html",
        "garantia_section": "src/garantia-latam.html",
        "faq_section": "src/faq-latam.html",
        "footer_section": "src/footer-latam.html",
        "transform_section": "src/transform-latam.html",
        "gate_script": "src/gate-none.html",
    },
    {
        "out": "v2.html",
        "lang": "pt-BR",
        "title": "500 Moldes de Mesa Posta",
        "body_class": "flat",
        "pixel": "src/pixel-b.html",
        "checkout_url": "https://payfast.greenn.com.br/9tabvy7/offer/NZhZFm?ch_id=143254",  # ticket 19,90 -- also the guarantee-section CTA target
        "checkout_url_10": "https://payfast.greenn.com.br/2tbv3by/offer/Xtm4Rv",
        "checkout_url_19": "https://payfast.greenn.com.br/9tabvy7/offer/NZhZFm?ch_id=143254",
        "vsl": "src/vsl-b.html",
        "headline": (
            "500 Moldes de Mesa Posta na Tela para "
            '<span class="hl">Anfitriãs de Sucesso<svg class="hl-underline" viewBox="0 0 100 10" '
            'preserveAspectRatio="none" aria-hidden="true"><path d="M0 5 Q 50 10 100 5"/></svg></span>.'
        ),
        "subhead": "src/subhead-v2.html",
        "topbar": 'Valor promocional válido apenas no dia <strong class="topbar-hl">13/09</strong>',
        "viewer_suffix": "assistindo agora",
        "hero_cta_text": "Quero os moldes agora!",
        "hero_cta_note": "Acesso liberado na hora, direto no WhatsApp e no email.",
        "hero_badges": "src/hero-badges-shared.html",
        "offer_block": "src/offer-v2.html",
        "offer_block_2": "src/offer-v2-second.html",
        "moldes": "src/moldes-v2.html",
        "ident_section": "src/ident-v2.html",
        "composicao_section": "src/composicao-shared.html",
        "bonus_section": "src/bonus-shared.html",
        "about_section": "src/about-shared.html",
        "garantia_section": "src/garantia-shared.html",
        "faq_section": "src/faq-shared.html",
        "footer_section": "src/footer-shared.html",
        "gate_script": "src/gate-none.html",
        "bonus_extra": "src/bonus-extra-v2.html",
        "transform_section": "src/transform-v2.html",
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


def _inject_optional(fragment, token, value):
    """Like _inject, but a token that simply isn't present in this page's
    fragment is fine (not every page's sections reference every optional
    block) -- only replaces it if it's actually there."""
    if token not in fragment:
        return fragment
    return fragment.replace(token, value)


def build_page(page):
    out_path = ROOT / page["out"]

    fragment = SRC.read_text(encoding="utf-8")

    fragment = _inject(fragment, "__TITLE__", page["title"], exactly=1)

    pixel_data = (ROOT / page["pixel"]).read_text(encoding="utf-8").strip()
    fragment = _inject(fragment, "__PIXEL__", pixel_data)

    fragment = _inject(fragment, "__HEADLINE__", page["headline"], exactly=1)

    subhead_data = (ROOT / page["subhead"]).read_text(encoding="utf-8").strip()
    fragment = _inject(fragment, "__SUBHEAD__", subhead_data, exactly=1)

    fragment = _inject(fragment, "__TOPBAR__", page["topbar"], exactly=1)

    fragment = _inject(fragment, "__VIEWER_SUFFIX__", page["viewer_suffix"], exactly=1)
    fragment = _inject(fragment, "__HERO_CTA_TEXT__", page["hero_cta_text"], exactly=1)
    fragment = _inject(fragment, "__HERO_CTA_NOTE__", page["hero_cta_note"], exactly=1)

    hero_badges_data = (ROOT / page["hero_badges"]).read_text(encoding="utf-8").strip()
    fragment = _inject(fragment, "__HERO_BADGES__", hero_badges_data, exactly=1)

    vsl_data = (ROOT / page["vsl"]).read_text(encoding="utf-8").strip()
    fragment = _inject(fragment, "__VSL__", vsl_data, exactly=1)

    # __OFFER_BLOCK__ (before "Quem sou eu") and __OFFER_BLOCK_2__ (after
    # the guarantee) are separate tokens so each page can show different
    # content in each spot: index.html (LATAM) repeats the same single
    # Premium offer in both; v2.html shows both tiers first, then only
    # the R$19,90 tier again.
    offer_data = (ROOT / page["offer_block"]).read_text(encoding="utf-8").strip()
    fragment = _inject(fragment, "__OFFER_BLOCK__", offer_data, exactly=1)

    offer_data_2 = (ROOT / page["offer_block_2"]).read_text(encoding="utf-8").strip()
    fragment = _inject(fragment, "__OFFER_BLOCK_2__", offer_data_2, exactly=1)

    moldes_data = (ROOT / page["moldes"]).read_text(encoding="utf-8").strip()
    fragment = _inject(fragment, "__MOLDES_BLOCK__", moldes_data, exactly=1)

    ident_data = (ROOT / page["ident_section"]).read_text(encoding="utf-8").strip()
    fragment = _inject(fragment, "__IDENT_SECTION__", ident_data, exactly=1)

    composicao_data = (ROOT / page["composicao_section"]).read_text(encoding="utf-8").strip()
    fragment = _inject(fragment, "__COMPOSICAO_SECTION__", composicao_data, exactly=1)

    bonus_section_data = (ROOT / page["bonus_section"]).read_text(encoding="utf-8").strip()
    fragment = _inject(fragment, "__BONUS_SECTION__", bonus_section_data, exactly=1)

    about_data = (ROOT / page["about_section"]).read_text(encoding="utf-8").strip()
    fragment = _inject(fragment, "__ABOUT_SECTION__", about_data, exactly=1)

    garantia_data = (ROOT / page["garantia_section"]).read_text(encoding="utf-8").strip()
    fragment = _inject(fragment, "__GARANTIA_SECTION__", garantia_data, exactly=1)

    faq_data = (ROOT / page["faq_section"]).read_text(encoding="utf-8").strip()
    fragment = _inject(fragment, "__FAQ_SECTION__", faq_data, exactly=1)

    footer_data = (ROOT / page["footer_section"]).read_text(encoding="utf-8").strip()
    fragment = _inject(fragment, "__FOOTER_SECTION__", footer_data, exactly=1)

    gate_rel = page.get("gate_script")
    gate_data = (ROOT / gate_rel).read_text(encoding="utf-8").strip() if gate_rel else ""
    fragment = _inject(fragment, "__GATE_SCRIPT__", gate_data, exactly=1)

    # __BONUS_EXTRA__ (2 extra bonus cards inside src/bonus-shared.html,
    # v2.html only -- src/bonus-latam.html has no such token, its 7 bonus
    # cards are all written out directly) and __TRANSFORM_SECTION__ (the
    # "antes/depois" section) are both optional per page.
    bonus_extra_rel = page.get("bonus_extra")
    if bonus_extra_rel:
        bonus_extra_data = (ROOT / bonus_extra_rel).read_text(encoding="utf-8").strip()
        for token, rel_path in BONUS_EXTRA_IMG_TOKENS.items():
            img_data = (ROOT / rel_path).read_text(encoding="utf-8").strip()
            bonus_extra_data = _inject(bonus_extra_data, token, img_data, exactly=1)
    else:
        bonus_extra_data = ""
    fragment = _inject_optional(fragment, "__BONUS_EXTRA__", bonus_extra_data)

    transform_rel = page.get("transform_section")
    transform_data = (ROOT / transform_rel).read_text(encoding="utf-8").strip() if transform_rel else ""
    fragment = _inject(fragment, "__TRANSFORM_SECTION__", transform_data, exactly=1)

    # checkout links: __CHECKOUT__ is the "default" target (the guarantee
    # section button on both pages; also the only checkout token used
    # inside offer-latam.html, on both its slots). __CHECKOUT_10__ /
    # __CHECKOUT_19__ only exist inside offer-v2.html / offer-v2-second.html,
    # so they're only injected for pages that declare them. __CHECKOUT_10__
    # appears once (the basic tier only shows in the first offer block);
    # __CHECKOUT_19__ appears twice (the featured tier shows in both offer
    # blocks, plus once more for index.html/LATAM's two offer_block slots).
    fragment = _inject(fragment, "__CHECKOUT__", page["checkout_url"])
    if "checkout_url_10" in page:
        fragment = _inject(fragment, "__CHECKOUT_10__", page["checkout_url_10"], exactly=1)
    if "checkout_url_19" in page:
        fragment = _inject(fragment, "__CHECKOUT_19__", page["checkout_url_19"], exactly=2)

    # image tokens are optional per page: different pages' moldes/bonus
    # blocks each only reference a subset of IMG_TOKENS, so a token simply
    # not appearing in this page's fragment is expected, not an error.
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
    lang = page.get("lang", "pt-BR")

    document = (
        "<!DOCTYPE html>\n"
        f'<html lang="{lang}">\n'
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
