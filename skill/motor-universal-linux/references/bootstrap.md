# Bootstrap portátil — Motor Ferrari Ubuntu

**Fonte de verdade:** [BOOTSTRAP canónico](https://github.com/martaxi-boss/skill-universal/blob/main/BOOTSTRAP.md). Esta cópia é para quando a **única Skill Universal Ferrari** é usada a partir de ZIP.

## Arquitetura

Uma Skill Universal Ferrari → conector GitHub autenticado → workflow **apenas Ferrari** em `martaxi-boss/VPS` → SSH existente → Motor Ferrari independente na VPS Ubuntu → relatório/ficheiros ZIP. A IA interpreta e orienta, o motor executa. REA e Ruflo são ferramentas opcionais, não coordenadores. Não alterar o SSH, Supervisor ou outros projetos.

## Testes complementares de projeto — 03/11/2026

- **Django/PostgreSQL real em CI próprio da Lowcost**: [#41068103444, repetição 2](https://github.com/martaxi-boss/lowcost-europa/actions/runs/41068103444) SUCCESS, **709/709 testes PASS** no commit de `main` `388860c6...`. `check`, `check --deploy`, migrações, Ruff e JavaScript PASS. PostgreSQL 16 temporário, não produção. **Estes não são testes do motor Ferrari**.
- **Staging browser não certificado agora**: [#40664538172, repetição 2](https://github.com/martaxi-boss/lowcost-europa/actions/runs/40664538172) FAIL antes de carregar páginas; runner `ubuntu-latest` disponibilizou Ubuntu 26.04 e Playwright `1.56.1` não suporta instalar Chromium. O PASS histórico `checks=13 errors=0` foi em **28/10/2026** com Ubuntu 24.04, não substitui validação atual. Solução proposta, ainda não aplicada: fixar `runs-on: ubuntu-24.04` no workflow de staging do projeto e executar a versão atual.
- **Ferrari VPS sem alteração:** release `ec4dc5045a034e3fbbbcfe3477e1641e80714262`; nenhum ficheiro ou workflow Lowcost foi modificado. [Relatório canónico desta execução](https://github.com/martaxi-boss/skill-universal/blob/main/docs/CERTIFICACAO_DJANGO_POSTGRES_STAGING_20261103.md).

---

## Última prova real — 03/11/2026: Lowcost Europa

- **Release VPS atual:** `ec4dc5045a034e3fbbbcfe3477e1641e80714262`; deploy [#41601238265](https://github.com/martaxi-boss/VPS/actions/runs/41601238265) SUCCESS, **99 testes PASS**.
- **Teste pela Skill:** [#41601466546](https://github.com/martaxi-boss/VPS/actions/runs/41601466546), SUCCESS; abriu-se ZIP com HTML/JS/CSS originais de catálogo Lowcost Europa (repo commit `388860c6...`) montados num fixture estático com 5 ofertas fictícias. **17 testes DOM PASS**, sem erros; tecla Tab/Shift+Tab, Enter/Space PASS e `interactions.findings=[]`. Desktop 1280×720, viewport móvel 390×844, overflow 0, zero pedidos externos.
- **Defeito de teste Ferrari corrigido:** [PR #10](https://github.com/martaxi-boss/skill-universal/pull/10): repõe foco no botão antes de verificar Space, após Enter ter mudado foco intencionalmente. Teste inicial [#41600631713](https://github.com/martaxi-boss/VPS/actions/runs/41600631713) acusou aviso de Space que não era bug Lowcost.
- **Higiene:** release atual e rollback `9277a56b9...` preservados, remoção exclusiva Ferrari da obsoleta `0196f37a...`; libertados **~2,42 MiB**, livres **21,31 GiB**, `outside_ferrari_touched=false`.
- **Inventário inalterado:** 56 candidatos Ubuntu, 23/56 detetados, 49 programas em catálogo combinado, **12 operações base**, 21 ações externas. Ferramentas BIM/CAD existentes não foram afetadas.
- **Limite:** aplicação Django/PostgreSQL, staging e produção ao vivo **não** testados. Foram usados ficheiros originais de frontend e HTML controlado, não pedidos externos, credenciais ou dados comerciais.
- Referência pormenorizada: [certificação Lowcost Europa](https://github.com/martaxi-boss/skill-universal/blob/main/docs/TESTE_REAL_LOWCOST_EUROPA_20261103.md).

---

## Histórico — Fase 6 (03/11/2026)

- **Release na VPS:** `9277a56b9b57c87b8b4e3dfbba08f4536add3625`.
- **99 testes PASS na VPS:** [#41598711120](https://github.com/martaxi-boss/VPS/actions/runs/41598711120) SUCCESS. `FERRARI_BROWSER_KEYBOARD_REAL=PASS`, `FERRARI_BROWSER_INTERACTIVE_CONTROLS_REAL=PASS`, Vite/Chromium, mobile, acessibilidade HTML pontual e geometria IFC PASS.
- **Skill ponta a ponta:** [#41598946695](https://github.com/martaxi-boss/VPS/actions/runs/41598946695) SUCCESS; ZIP verificado com Vite HTML/CSS/JS, `browser-check.json`, screenshots desktop 1280×720 e mobile CSS 390×844. No site de demonstração: 4 controlos focáveis, `Tab` e `Shift+Tab` PASS, botão por `Enter`/`Space` (contador 2), link e formulário por `Enter` PASS, zero erros e pedidos externos. Não implica que todos os controlos de sites externos funcionem.
- **Ferramentas próprias:** Vite `8.3.5`, Playwright `1.64.1`, Chromium headless `156.0.8078.4`, Node `22.23.4`; IfcOpenShell para IFC.
- **CAD/BIM:** a geometria IFC já foi testada com IfcOpenShell (parede 5 × 0,2 × 3 m na [Skill #41558414405](https://github.com/martaxi-boss/VPS/actions/runs/41558414405)); isso não certifica FreeCAD, projetos CAD completos, segurança estrutural ou análise IDS.
- **Inventário:** 56 candidatos Ubuntu, 23/56 detetados, 49 ferramentas nos catálogos combinados, **12 operações base** e 21 ações externas.
- **Limite operativo:** a operação existente `vite-build` observa foco real com `Tab`/`Shift+Tab`, mas só ativa controlos explicitamente marcados `data-ferrari-test` (`button`, `link`, `form`). Ausentes marcadores, o resultado dessas ações é `not_requested`, não certificação. Não há emulação Android, validação WCAG profunda ou backend.
- **Higienização:** após PASS, removida uma release antiga `13c439925...`, preservadas a ativa e a anterior certificada `0196f37a...`. Libertados **~2,40 MiB**, **21,32 GiB livres**; nenhum projeto externo alterado.
- **Continuidade:** testar num caso web real não confidencial antes de instalar novas ferramentas ou adicionar outros fluxos. Ver [relatório fase 6](https://github.com/martaxi-boss/skill-universal/blob/main/docs/CERTIFICACAO_INTERACOES_TECLADO_20261103.md).

## Continuidade

Usar `references/github-bridge.md` para enviar um JSON novo `kind=operation|invoke|auto|inventory`, confirmar o run e descarregar o ZIP. Para sites estáticos, a mesma operação `vite-build` devolve capturas desktop/móvel, diagnóstico HTML e resultados de foco/ações de teclado opt-in quando o Chromium Ferrari está operacional. As alterações e adaptações são feitas **no Ferrari**, sem segunda Skill ou novas camadas.

Os pedidos são enviados para um repositório público: base64 não é encriptação e não pode conter dados pessoais ou segredos.
