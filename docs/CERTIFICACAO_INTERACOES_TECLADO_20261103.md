# Ferrari — certificação da fase 6: teclado e controlos interativos (03/11/2026)

## Estado e provas

**Motor Ferrari ativo na VPS Ubuntu:** `9277a56b9b57c87b8b4e3dfbba08f4536add3625`, [PR #9](https://github.com/martaxi-boss/skill-universal/pull/9) integrada em main.

- [CI GitHub #41598406165](https://github.com/martaxi-boss/skill-universal/actions/runs/41598406165): SUCCESS, **99 testes Python PASS**, Skill ZIP sem erros.
- [CI da PR #41598460475](https://github.com/martaxi-boss/skill-universal/actions/runs/41598460475): SUCCESS.
- **[Execução real VPS #41598711120](https://github.com/martaxi-boss/VPS/actions/runs/41598711120): SUCCESS**, **99 testes PASS na VPS**, `FERRARI_BROWSER_KEYBOARD_REAL=PASS`, `FERRARI_BROWSER_INTERACTIVE_CONTROLS_REAL=PASS`, `FERRARI_VITE_BROWSER_REAL=PASS`, `FERRARI_VITE_RESPONSIVE_REAL=PASS`, `FERRARI_BROWSER_A11Y_SPOTCHECK_REAL=PASS`, `FERRARI_IFC_GEOMETRY_REAL=PASS` e `FERRARI_DEPLOY_TRANSPORT=PASS`.
- **[Pedido real pela Skill #41598946695](https://github.com/martaxi-boss/VPS/actions/runs/41598946695): SUCCESS**, `FERRARI_SKILL_JOB_STATUS=completed`, `FERRARI_SKILL_END_TO_END=PASS`; o ZIP foi transferido e o `ferrari-response.zip` interno foi aberto/validado. Relatório `status=completed`, `vite-build`.

## Provas em navegador real

Firefox, emulação Android e instalações adicionais **não** foram necessários. A mesma operação `vite-build` compilou um pequeno site sintético e abriu-o no Playwright/Chromium headless 156.0.8078.4, já isolado no Ferrari. O relatório `artifacts/browser-check.json` devolveu:

| Campo | Evidência |
|---|---|
| `interactions.focusable_count` | **4** |
| `tab_forward` | passed |
| `shift_tab_back` | passed |
| `button_enter` | passed |
| `button_space` | passed |
| `link_enter` | passed; âncora local `#resultado` |
| `form_enter` | passed; submissão controlada com `preventDefault()` |
| `interactions.findings` | `[]` |
| Estado JS/DOM | `demo_js_ready=yes`, `dom_ready=complete` |
| Erros de consola, de página, pedidos externos | **0 / 0 / 0** |
| Captura desktop | `browser-screenshot.png` — **51 916 bytes**, viewport 1280×720 |
| Captura móvel | `browser-mobile.png` — **52 507 bytes**, viewport CSS 390×844 |
| Overflow horizontal a 390px | **0 px** |
| Spotcheck de acessibilidade HTML | clear, sem avisos no exemplo |
| Vite | `8.3.5`, ZIP com `dist/index.html`, JS e CSS reais |

Na captura móvel real, o contador indica **2** e o formulário mostra **“Recebido: Ferrari fase 6”**. Ambos os PNGs foram extraídos e visualizados, e os checks dos ficheiros ZIP passaram. Este resultado foi demonstrado com quatro controlos intencionalmente incluídos no site de teste; **não constitui prova do funcionamento de todos os botões, links e formulários de qualquer projeto**.

**Âmbito e precaução sem camadas:** o Ferrari percorre o foco com `Tab` e `Shift+Tab`; a ativação por `Enter`/`Space` só ocorre em controlos que tenham atributos explícitos `data-ferrari-test="button"`, `data-ferrari-test="link"` ou `data-ferrari-test="form"`. Na ausência destes marcadores, o relatório indica `not_requested`; o motor não aciona operações arbitrárias em sites alheios. Nenhum servidor permanente ou ponte adicional foi criado.

## Higienização após PASS

Reutilização exclusiva do instalador existente `install/ferrari-hygiene.py` na execução VPS #41598711120, com preview e `--apply`:

- **Release atual preservada:** `9277a56b9b57c87b8b4e3dfbba08f4536add3625`.
- **Fallback certificado preservado:** `0196f37a7610d1f95cd3371652308b7e2244f019` (fase 5).
- **Release obsoleta removida:** `13c4399257cd19496f378ad3f15cd1ebe877977b`.
- **Espaço efetivamente libertado:** **2 519 040 bytes (~2,40 MiB)**, **21,32 GiB livres** no final.
- `outside_ferrari_touched=false` e `FERRARI_ONLY_HYGIENE=PASS`.

**Ferramentas/inventário não alargados:** 56 candidatos Ubuntu, 23 encontrados dentro da seleção, 49 programas no catálogo combinado, 12 operações base e 21 ações externas. **Não** foram instalados programas, criadas Skills, operações, coordenadores ou alterados SSH, Supervisor e outros projetos.

## Continuidade

O próximo passo não é uma nova camada. Deve ser usar o mesmo motor em **um projeto web concreto**, com um fluxo funcional específico e dados não confidenciais, expandindo a cobertura de testes somente quando houver um caso real. Consultar o [BOOTSTRAP](../BOOTSTRAP.md).
