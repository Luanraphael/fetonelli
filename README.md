# Fe Antonella — 500 Moldes de Mesa Posta

Landing page de vendas do acervo de moldes de Mesa Posta (@fe.tonella).

## Estrutura

- **`index.html`** — página final, pronta pra publicar. Um único arquivo HTML autocontido (CSS, fontes e todas as imagens embutidas em base64), sem dependências externas.
- **`src/index.src.html`** — código-fonte editável, com placeholders (`__TOKEN__`) no lugar das fontes/imagens.
- **`src/fonts/`** e **`src/img/`** — fontes (Manrope, Inter) e imagens da página, em base64 (`.b64`).
- **`src/build.py`** — script que substitui os placeholders de `index.src.html` pelos arquivos `.b64` correspondentes e gera o `index.html` final.

## Como editar

1. Edite `src/index.src.html` (ou troque as imagens em `src/img/`, regerando o `.b64` correspondente com `base64 -i arquivo.png -o arquivo.b64`).
2. Rode `python3 src/build.py` a partir da raiz do repositório.
3. Isso regenera `index.html` automaticamente.

## Publicar

`index.html` é estático e autocontido — pode ser hospedado em qualquer lugar (GitHub Pages, Netlify, Vercel) sem build step.
