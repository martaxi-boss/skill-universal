# Ferrari — fecho verificável de QA web e diagnósticos (08/11/2026)

## Fonte de verdade operacional

- **Motor único**: repositório `martaxi-boss/skill-universal`, um único `engine/catalog.json` com 173 programas, 272 interfaces de funções, 3 dependências e 2 fornecedores (450 registos). Ter um registo de programa **não** implica ter um adaptador integrado.
- **Release ativa na VPS Ubuntu**: `bf7f75f171d95b22635c00fc9c5150926c7a1ee8` em `/srv/projects/skill-universal/current`; release anterior `c97441f629c758aed8954a6075e6774eb5dd967c` preservada como rollback.
- **CI GitHub**: [`#42486951803`](https://github.com/martaxi-boss/skill-universal/actions/runs/42486951803), SUCCESS.
- **VPS pré-teste**: [`#42487063192`](https://github.com/martaxi-boss/VPS/actions/runs/42487063192), SUCCESS; 501 testes, 40/40 executores, 8/8 serviços protegidos; sem ativar durante o pré-teste.
- **VPS ativação protegida**: [`#42487157833`](https://github.com/martaxi-boss/VPS/actions/runs/42487157833), SUCCESS; repetiu 501 testes, 40/40 executores, 8/8 serviços; confirmou `FERRARI_PRIVATE_RELEASE_ACTIVE=bf7f75f...`, switch PASS e rollback preservado.
- **Ponte única**: workflow existente `martaxi-boss/VPS/.github/workflows/ferrari-skill-request.yml` tem `ref` pinado ao mesmo SHA da release ativa. Sem troca do SSH nem serviço permanente.
- **Skill ChatGPT**: `motor-universal-linux` v1.0.9, atualizada **na mesma identidade**; não criar uma segunda Skill. O código de QA fica no motor, sem novo tipo de pedido nem catálogo.

## Ponta a ponta — caso válido

[GitHub Actions VPS `#42487501805`](https://github.com/martaxi-boss/VPS/actions/runs/42487501805), SUCCESS. Pedido `kind=operation`, `operation=vite-build`, `acceptance.browser_evidence=true`, ZIP de website com dois links internos. O `response.zip` real foi aberto e verificado: `report.json.status=completed`, `quality_gate.status=passed`, `artifacts/browser-check.json`, duas capturas PNG, `artifacts/dist/index.html`, `artifacts/dist/sobre.html`, `vite-build.json`. Integridade ZIP: PASS.

O relatório Playwright regista `navigation.links_total=2`, `internal_files_verified=1`, `fragments_verified=1`, `navigation.findings=[]`, `mobile.horizontal_overflow_px=0`, sem erros de página/consola. Isto certifica **este caso de frontend estático**, não um site de produção.

## Ponta a ponta — caso inválido, rejeição intencional

[GitHub Actions VPS `#42487495200`](https://github.com/martaxi-boss/VPS/actions/runs/42487495200), **FAILURE esperado por QA**, e não por falha de instalação. Pedido idêntico, mas o HTML continha um link de menu com `href="#"`.

O `response.zip` produzido pela Skill foi descarregado e validado com ZIP sem membros corrompidos:
- `report.json`: `status=failed` e erro informativo `Ferrari executor failed: FERRARI_BROWSER_CHECK_FAILED=Browser quality gate failed_navigation: Non-functional link destination: #`.
- `artifacts/browser-check.json`: `status=failed_navigation`, `navigation.status=findings` e `findings=["Non-functional link destination: #"]`.
- `artifacts/browser-screenshot.png` e `artifacts/browser-mobile.png`: capturas reais, ambas presentes e não vazias.
- `report.json.diagnostic_artifacts`: lista estrita das três evidências acima. Nenhum conteúdo arbitrário de entrada, segredos ou ficheiros externos é arquivado como prova de falha.

**Correção comprovada:** antes a execução recusava o link, mas o ZIP de erro não trazia o relatório. Agora a falha é explicitamente recusada, documentada e inspecionável.

## Cobertura e limitações

A verificação web é local, com Chromium Playwright privado e rede externa bloqueada. Inspeciona nomes acessíveis, teclado, viewport mobile, erros do browser e links internos por leitura. **Não clica em ações reais de terceiros** nem comprova backend, checkout, geolocalização, rotas SPA dinâmicas, links externos, conformidade WCAG integral ou qualidade editorial. Rotas SPA não comprovadas não recebem aprovação falsa.

Outras limitações gerais do Ferrari permanecem separadas desta prova: ASR para voz/narração comercial no vídeo, ferramentas instaladas sem adaptador, testes de fluxos GUI/OBS e autonomia LLM de subagentes Ruflo sem anfitrião ativo. Um teste de versão de programa não equivale a cobertura funcional integral. Nenhuma destas limitações foi artificialmente marcada como PASS.

## Organização

Todo o código e dependências Ferrari permanecem sob `/srv/projects/skill-universal`. A ponte GitHub/VPS não recebe catálogo, motor, orquestrador, agentes nem lógica de qualidade. Históricos de releases anteriores no BOOTSTRAP são informações **datadas** e não se sobrepõem a este estado verificado.
