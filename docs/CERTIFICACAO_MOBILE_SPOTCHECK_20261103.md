# Ferrari — fase 5: viewport móvel e diagnóstico básico de acessibilidade

**Data:** 03/11/2026 · **Estado: PASS, com limites explícitos**

## Integração

A mesma operação `vite-build` usa o Chromium/Playwright já instalado dentro do Ferrari para produzir duas capturas, desktop 1280×720 e viewport CSS móvel 390×844. O mesmo `browser-check.json` passa a reportar largura de overflow, meta viewport, atributo HTML `lang`, títulos semânticos e contagens de imagens sem `alt`, botões/links sem nome e campos sem etiqueta. Encontrar problemas cria **avisos**, não os oculta nem bloqueia automaticamente a compilação. **Não é emulação de Android nem certificação WCAG**.

Não foram instalados programas nem criadas operações, Skills, pontes ou serviços novos. Não houve alterações no SSH ou nos projetos adjacentes.

## Provas exatas

- [PR #8](https://github.com/martaxi-boss/skill-universal/pull/8) integrada em `main`. Commit da release: `0196f37a7610d1f95cd3371652308b7e2244f019`.
- [GitHub CI da PR #41561833247](https://github.com/martaxi-boss/skill-universal/actions/runs/41561833247): **SUCCESS**, 99 testes PASS, Skill ZIP sem erro.
- [Implantação e smoke real VPS #41561998389](https://github.com/martaxi-boss/VPS/actions/runs/41561998389): **SUCCESS**, 99 testes PASS na VPS, marcadores `FERRARI_VITE_RESPONSIVE_REAL=PASS`, `FERRARI_BROWSER_A11Y_SPOTCHECK_REAL=PASS`, `FERRARI_VITE_BROWSER_REAL=PASS`, `FERRARI_IFC_GEOMETRY_REAL=PASS`.
- [Pedido real pela Skill #41562205411](https://github.com/martaxi-boss/VPS/actions/runs/41562205411): **SUCCESS**, `FERRARI_SKILL_JOB_STATUS=completed` e `FERRARI_SKILL_END_TO_END=PASS`. O arquivo foi descarregado e `report.json`, `artifacts/browser-check.json`, capturas PNG e distribuição Vite foram inspecionados.

## Prova observada no site público de demonstração

| Campo | Resultado |
|---|---|
| Browser | Chromium headless shell 156.0.8078.4 |
| Desktop | 1280 × 720; captura `browser-screenshot.png` (62 964 bytes) |
| Móvel | viewport CSS 390 × 844; captura `browser-mobile.png` (56 548 bytes) |
| CSS responsivo | duas colunas desktop → uma coluna móvel, visualmente confirmado |
| Overflow horizontal a 390px | **0 px** |
| JavaScript e DOM | `demo_js_ready=yes`, `dom_ready=complete` |
| Meta viewport / HTML lang | presente / `pt` |
| Headings | 3 |
| Imagens sem alt | 0 |
| Botões sem nome | 0 |
| Links sem nome | 0 |
| Formulários sem label | 0 |
| Avisos do spotcheck | `[]`; estado `clear` |
| Erros JS / consola / pedidos externos | 0 / 0 / 0 |

Estes números são apenas do pequeno site gerado para o teste. O método faz redimensionamento do **viewport CSS** num browser Chromium de desktop, sem simular hardware Android, touch real, leitor de ecrã ou aferir acessibilidade completa de websites.

## Higienização exclusiva do Ferrari

A rotina existente `install/ferrari-hygiene.py` foi executada em preview e `apply`, após os testes:

- **Preservadas:** release atual `0196f37a7610d1f95cd3371652308b7e2244f019` e anterior certificada `13c4399257cd19496f378ad3f15cd1ebe877977b`.
- **Removida:** release antiga `aefd8bb156f95e47c5a90b2a5d96db8d26f94283`.
- **Espaço adicional libertado real:** `2486272` bytes (~**2,37 MiB**).
- **Espaço livre final VPS:** **21,32 GiB**.
- `FERRARI_ONLY_HYGIENE=PASS` e `outside_ferrari_touched=false`.

**Inventário:** 56 candidatos Ubuntu; 23 detetados na seleção; 49 ferramentas nos catálogos combinados; **12 operações base e 21 ações externas** (sem alterações nesta fase).

## Próxima fase delimitada

Caso seja necessário, o próximo incremento será **teste de interação por teclado** com a mesma página e browser, sem adicionar pacotes. Só poderá ser dado como concluído depois de uma nova prova GitHub → VPS → Skill. Outros domínios e projetos continuam intocados.

Consultar [BOOTSTRAP canónico](../BOOTSTRAP.md).
