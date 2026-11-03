# Ferrari — teste funcional de código real Lowcost Europa (03/11/2026)

## Origem e escopo exatos

- Projeto real consultado **somente para leitura**: [martaxi-boss/lowcost-europa](https://github.com/martaxi-boss/lowcost-europa), commit de `main` `388860c6a167686a378b89f4282304bce89c25de`.
- JavaScript original **sem alterar**: `apps/storefront/static/storefront/catalog-explorer.js`, SHA do blob `8497d89fd3c30e5521e8536e60bb71d24b5fb2aa`.
- CSS original **sem alterar**: `apps/storefront/static/storefront/storefront.css`, blob `0a926531d4c5d29c23b4771d1c9083123d24d800`.
- Controlos HTML originais de `apps/storefront/templates/storefront/components/catalog_explorer_controls.html`, blob `2bcfbc59e1c743dbc8b9793f03be278517255e88`. A cópia usada no teste recebeu **só** `data-ferrari-test="button"` no botão «Limpar filtros», sem mudança do repositório original.
- Um *fixture* estático temporário usou **cinco ofertas fictícias** e `src/qa.js` descartável para exercitar as operações do JS real. Não se publicou preço comercial, base de dados, credencial ou produto real. O Ferrari não acedeu ao site público nem ao backend Django.

## Teste inicial: um falso aviso do próprio Ferrari

[GitHub Actions VPS #41600631713](https://github.com/martaxi-boss/VPS/actions/runs/41600631713): `SUCCESS`, pedido `kind=operation`, `vite-build`, `FERRARI_SKILL_END_TO_END=PASS`, ficheiro de evidência aberto e verificado.

- O **JavaScript original da Lowcost passou 17 verificações** executadas no DOM Chromium: inicialização, contagem, pesquisa com acentos, nenhuma correspondência, reset, filtros COMBO/OTHER, limites de orçamento EUR/sem preço, ordenação ascendente e descendente por moedas, controlo de comparação, adicionar até três, impedir quarto, limpar comparação, estado final.
- O motor Ferrari reportou `button_enter=passed`, **`button_space=finding`**. Diagnóstico: o botão original «Limpar filtros» devolve corretamente foco ao campo de pesquisa após Enter, e o verificador do Ferrari testava Space no campo já focado. **Não era um defeito confirmado da Lowcost.**

## Correção Ferrari e repetição rigorosamente igual

A [PR #10](https://github.com/martaxi-boss/skill-universal/pull/10) corrigiu só o teste: `await button.focus()` entre as provas independentes de Enter e Space. Um teste unitário passou a verificar esta sequência. **Nenhum ficheiro da Lowcost foi escrito.**

- **Release Ferrari ativa:** `ec4dc5045a034e3fbbbcfe3477e1641e80714262`.
- **[Deploy real VPS #41601238265](https://github.com/martaxi-boss/VPS/actions/runs/41601238265)**: SUCCESS, **99 testes Python PASS** e `FERRARI_BROWSER_KEYBOARD_REAL=PASS`, `FERRARI_BROWSER_INTERACTIVE_CONTROLS_REAL=PASS`, `FERRARI_VITE_BROWSER_REAL=PASS`, `FERRARI_VITE_RESPONSIVE_REAL=PASS`, `FERRARI_ONLY_HYGIENE=PASS`, `FERRARI_DEPLOY_TRANSPORT=PASS`.
- **[Repetição exata pela Skill #41601466546](https://github.com/martaxi-boss/VPS/actions/runs/41601466546)**: SUCCESS, `FERRARI_SKILL_JOB_STATUS=completed`, `FERRARI_SKILL_END_TO_END=PASS`. Reutilizou-se exatamente o mesmo ZIP de entrada com o código real, sem modificar os cinco ficheiros internos. ZIP de resposta inspecionado: `report.json` status `completed`, `artifacts/vite-build.json` e `artifacts/browser-check.json`, `dist/index.html`, JS/CSS compilados e PNG desktop/móvel.
- Resultado observado: título `Lowcost Europa | Ferrari 17 testes PASS`, `demo_js_ready=yes`, `dom_ready=complete`. Dez controlos focáveis; `Tab`, `Shift+Tab`, `button_enter`, **`button_space`** todos `passed`, `interactions.findings=[]`, `status=clear`. Âncora e formulário `not_requested`, porque não existem neste fixture de catálogo; isto **não** constitui uma falha.
- Desktop CSS 1280×720: screenshot **868 570 bytes**. Móvel CSS 390×844: screenshot **572 046 bytes**, overflow horizontal **0 px**, meta viewport presente, `html lang=pt`. Sem imagens sem alt, botões/links sem nome ou formulários sem rótulo no exemplo; sem erros de consola, erros JS ou pedidos externos. Playwright Chromium headless shell `156.0.8078.4`, Vite `8.3.5`. **Não** foi emulado um dispositivo Android físico.

## Higienização estritamente no Ferrari

Após deploy com PASS, o instalador Ferrari removeu a release obsoleta `0196f37a7610d1f95cd3371652308b7e2244f019` e preservou a atual `ec4dc5045a034e3fbbbcfe3477e1641e80714262` mais o fallback certificado `9277a56b9b57c87b8b4e3dfbba08f4536add3625`. `actual_free_delta_bytes=2539520` (**~2,42 MiB**); `disk_free_after_gib=21.31`; `outside_ferrari_touched=false`.

**Sem novos programas, Skills, operações, SSH, coordenadores, serviços, alterações no projeto Lowcost ou alterações a outros projetos.** Mantêm-se 12 operações base, 21 ações externas, 56 candidatos Ubuntu, 23 detetados nessa seleção e 49 programas em catálogos combinados.

## Limitação e próximo teste útil

**Certificado:** construção estática, código frontend original do catálogo Lowcost, 17 asserções DOM e teclado do botão opt-in num Chromium real isolado, capturas e diagnóstico responsivo. **Não certificado nesta execução:** templates Django processados na íntegra, PostgreSQL, autenticação, exportação/compra, fornecedores externos, staging/produção ao vivo, rede externa ou processos de backend. O projeto já possui `tests/browser/staging-browser-smoke.cjs` e workflows de CI/QA próprios; devem ser executados separadamente quando se pretender certificar a aplicação completa. Esta fase não alterou nem disparou esses workflows.

Consulte o [BOOTSTRAP canónico](../BOOTSTRAP.md) para o estado operacional do Ferrari.
