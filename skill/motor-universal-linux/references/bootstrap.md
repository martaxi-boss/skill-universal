# Bootstrap portátil — Motor Ferrari Ubuntu

**Fonte de verdade:** [BOOTSTRAP canónico](https://github.com/martaxi-boss/skill-universal/blob/main/BOOTSTRAP.md). Esta cópia é para quando a **única Skill Universal Ferrari** é usada a partir de ZIP.

## Arquitetura

Uma Skill Universal Ferrari → conector GitHub autenticado → workflow **apenas Ferrari** em `martaxi-boss/VPS` → SSH existente → Motor Ferrari independente na VPS Ubuntu → relatório/ficheiros ZIP. A IA interpreta e orienta, o motor executa. REA e Ruflo são ferramentas opcionais, não coordenadores. Não alterar o SSH, Supervisor ou outros projetos.

## Estado real certificado — 03/11/2026

- **Release na VPS:** `9277a56b9b57c87b8b4e3dfbba08f4536add3625`.
- **99 testes PASS na VPS:** [#41598711120](https://github.com/martaxi-boss/VPS/actions/runs/41598711120) SUCCESS. `FERRARI_BROWSER_KEYBOARD_REAL=PASS`, `FERRARI_BROWSER_INTERACTIVE_CONTROLS_REAL=PASS`, Vite/Chromium, mobile, acessibilidade HTML pontual e geometria IFC PASS.
- **Skill ponta a ponta:** [#41598946695](https://github.com/martaxi-boss/VPS/actions/runs/41598946695) SUCCESS; ZIP verificado com Vite HTML/CSS/JS, `browser-check.json`, screenshots desktop 1280×720 e mobile CSS 390×844. No site de demonstração: 4 controlos focáveis, `Tab` e `Shift+Tab` PASS, botão por `Enter`/`Space` (contador 2), link e formulário por `Enter` PASS, zero erros e pedidos externos. Não implica que todos os controlos de sites externos funcionem.
- **Ferramentas próprias:** Vite `8.3.5`, Playwright `1.64.1`, Chromium headless `156.0.8078.4`, Node `22.23.4`; IfcOpenShell para IFC.
- **Inventário:** 56 candidatos Ubuntu, 23/56 detetados, 49 ferramentas nos catálogos combinados, **12 operações base** e 21 ações externas.
- **Limite operativo:** a operação existente `vite-build` observa foco real com `Tab`/`Shift+Tab`, mas só ativa controlos explicitamente marcados `data-ferrari-test` (`button`, `link`, `form`). Ausentes marcadores, o resultado dessas ações é `not_requested`, não certificação. Não há emulação Android, validação WCAG profunda ou backend.
- **Higienização:** após PASS, removida uma release antiga `13c439925...`, preservadas a ativa e a anterior certificada `0196f37a...`. Libertados **~2,40 MiB**, **21,32 GiB livres**; nenhum projeto externo alterado.
- **Continuidade:** testar num caso web real não confidencial antes de instalar novas ferramentas ou adicionar outros fluxos. Ver [relatório fase 6](https://github.com/martaxi-boss/skill-universal/blob/main/docs/CERTIFICACAO_INTERACOES_TECLADO_20261103.md).

## Continuidade

Usar `references/github-bridge.md` para enviar um JSON novo `kind=operation|invoke|auto|inventory`, confirmar o run e descarregar o ZIP. Para sites estáticos, a mesma operação `vite-build` devolve capturas desktop/móvel, diagnóstico HTML e resultados de foco/ações de teclado opt-in quando o Chromium Ferrari está operacional. As alterações e adaptações são feitas **no Ferrari**, sem segunda Skill ou novas camadas.

Os pedidos são enviados para um repositório público: base64 não é encriptação e não pode conter dados pessoais ou segredos.
