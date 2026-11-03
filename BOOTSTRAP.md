# BOOTSTRAP — Motor Ferrari / Skill Universal Ubuntu

## Fase 08 — 03/11/2026: Apktool instalado e ligado ao Ferrari

- **Integração sem nova camada:** [PR #17](https://github.com/martaxi-boss/skill-universal/pull/17) integrada na `main` como `54bb60eb594a6ba315098bfc76852f965ff3154e`. A ação tipada `apktool-decode-resources` utiliza o binário **Apktool 2.7.0** já instalado (`/usr/bin/apktool`), através do mesmo `engine/tool_runtime.py`, para descodificar APKs em diretórios com manifesto, recursos e Smali. **JADX** continua a executar a operação base `apk-decompile` independentemente. A mesma Skill inclui os ficheiros de diretório no ZIP, sem servidor ou coordenador novo.
- **CI:** [#41630397156](https://github.com/martaxi-boss/skill-universal/actions/runs/41630397156) **SUCCESS, 111/111 testes PASS**, incluindo contrato Apktool, seleção por extensão, verificação de diretório e empacotamento ZIP da Skill.
- **VPS REAL:** [deploy #41630731184](https://github.com/martaxi-boss/VPS/actions/runs/41630731184) **SUCCESS, 111 testes PASS**, `FERRARI_APKTOOL_REAL=PASS`: o próprio Apktool construiu um APK inofensivo local para o smoke e, através da ação do Ferrari, descodificou `AndroidManifest.xml`, `res/values/strings.xml`, `smali/com/ferrari/Smoke.smali` e `apktool.yml`; conteúdo verificado. `FERRARI_PROFESSIONAL_INVENTORY=PASS` e `FERRARI_DEPLOY_TRANSPORT=PASS`.
- **Skill inventário pós-instalação:** a referência de release no workflow Ferrari de pedidos foi atualizada **apenas no SHA**, commit [`459f8289`](https://github.com/martaxi-boss/VPS/commit/459f8289fd9892263c4598d33e3631c05ce6bdbf). Pedido de inventário real [`58ea6862`](https://github.com/martaxi-boss/VPS/commit/58ea6862f598ce44640baa7afaa55bfb055e5852) concluiu em [GitHub Actions #41631048154](https://github.com/martaxi-boss/VPS/actions/runs/41631048154): `FERRARI_SKILL_END_TO_END=PASS`, `report.json.status=completed`, ZIP lido, `inventory.json` confirmou **23 ações disponíveis**, **49 programas detectados em catálogos combinados**, **23/56 selecionados detetados**, **33/56 não detetados**. A entrada `apktool` passou a `installed=true,status=callable,actions=[apktool-decode-resources]`. **Este pedido remoto foi de inventário**; a descodificação funcional do APK foi demonstrada no *smoke* real da VPS, não por um pedido `kind=invoke` remoto.
- **Higienização Ferrari:** [#41630731184](https://github.com/martaxi-boss/VPS/actions/runs/41630731184), `FERRARI_ONLY_HYGIENE=PASS`, **2 637 824 bytes (~2,52 MiB)** libertados; preservadas a release ativa `54bb60eb...` e a de recuperação `9277a56b...`; **21,30 GiB livres**; `outside_ferrari_touched=false`. Nenhuma modificação ao SSH, Supervisor, REA independente ou outros projetos.
- **Próximo candidato funcional:** ferramentas detetadas mas sem adaptador próprio incluem OpenCV, yt-dlp, Ghidra, REA e Ruflo, entre outras. Selecionar uma de cada vez e testar com entradas reais; não confundir deteção com execução ou instalar tudo indiscriminadamente. A Skill efetivamente instalada na interface ChatGPT ainda **não foi certificada** como sincronizada com o ZIP da última release.

---


## Estado operacional confirmado — 03/11/2026: programas, OCR e orquestrador

- **Release activa Ubuntu VPS:** `5a4c881c0a76ecbbdfdc04af9239ef4a70cf0084`; [deploy Ferrari #41624775327](https://github.com/martaxi-boss/VPS/actions/runs/41624775327) **SUCCESS**, **107/107 testes PASS** na VPS. A versão anterior `9277a56b9b57c87b8b4e3dfbba08f4536add3625` foi preservada para rollback. Higienização Ferrari **PASS**, **5 263 360 bytes libertados (~5,02 MiB)**, **21,31 GiB livres** e `outside_ferrari_touched=false`.
- **Inventário real da VPS:** [Skill #41622654033](https://github.com/martaxi-boss/VPS/actions/runs/41622654033) gerou `inventory.json` confirmado; fotografia anterior à nova ação: 56 candidatos Ubuntu, **23 detetados**, 33 não detetados, 49 ferramentas detectadas nos catálogos combinados, 21 ações externas. **Na nova release**, o deploy confirmou **22 ações externas disponíveis** (`FERRARI_UNIVERSAL_ACTIONS_AVAILABLE=22`) e 49 ferramentas nos catálogos combinados, mantendo 23/56 e 33/56. **Programas detetados não implicam adaptador funcional ou certificação profunda**.
- **OCRmyPDF ligado sem nova instalação:** [PR #15](https://github.com/martaxi-boss/skill-universal/pull/15) acrescentou o adaptador `ocrmypdf-searchable-pdf` ao **mesmo** manifesto Ferrari; [PR #16](https://github.com/martaxi-boss/skill-universal/pull/16) corrigiu exclusivamente o contador estático do smoke BIM/web. Deploy final [#41624775327](https://github.com/martaxi-boss/VPS/actions/runs/41624775327) comprovou **`FERRARI_OCRMYPDF_REAL=PASS`**: PDF original só com imagem → PDF com texto pesquisável; verificou `pdftotext` antes e depois, sem novos fornecedores, SSH ou serviços.
- **Skill composta real:** [#41620077416](https://github.com/martaxi-boss/VPS/actions/runs/41620077416) **SUCCESS**: `kind=plan` com site HTML e extração de strings, ZIP/relatórios verificados, `FERRARI_SKILL_END_TO_END=PASS`. Orquestrador é o Ferrari existente, sem camadas novas.
- **OCR antigo encerrado com diagnóstico:** pedido original `78a92882` falhou em [#41609966814](https://github.com/martaxi-boss/VPS/actions/runs/41609966814) devido a PNG corrompido (`libpng: IDAT incorrect data check`), **não** devido à dependência Tesseract. Novo pedido [`df137c07`](https://github.com/martaxi-boss/VPS/commit/df137c0777bc7afd28da6df1edc21333d4d052fc) executou via Skill duas etapas dependentes: [run #41625566079](https://github.com/martaxi-boss/VPS/actions/runs/41625566079) **SUCCESS**, `FERRARI_SKILL_JOB_STATUS=completed`, `FERRARI_SKILL_END_TO_END=PASS`; ZIP real lido: `recognized.txt` continha exatamente `FERRARI OCR 2026\\n` e `matches.txt` continha `1:FERRARI OCR 2026\\n`; relatório `failed={}`, `blocked=[]`.
- **Ainda não 100%:** REA/Ruflo apenas teste de arranque da CLI (help-only); parte das 33 ferramentas candidatas não está detectada. A fotografia do inventário demonstra detecção, não execução integral. A Skill instalada na interface ChatGPT **não foi certificada como sincronizada** com o novo ZIP; o repositório canónico e os workflows Ferrari estão actualizados.
- **Ponte e projectos externos preservados:** apenas a referência da release dos workflows próprios Ferrari em `martaxi-boss/VPS` foi actualizada; o SSH, o Supervisor, REA independente e os outros projectos não foram modificados nesta fase.

---


## Histórico da Fase 07 - 03/11/2026: integração DAG (posteriormente certificada acima)

- **Código:** [PR #14](https://github.com/martaxi-boss/skill-universal/pull/14) integrada por squash no commit `143ee613dc365e80804a579edc5faef37d38a372`. Integrado **no mesmo** `engine.skill_job` o pedido `kind=plan`, delegando para `engine.orchestrator` existente; sem Skill, coordenador, servidor ou ponte adicional.
- **CI real:** [GitHub Actions #41619456511](https://github.com/martaxi-boss/skill-universal/actions/runs/41619456511) **SUCCESS, 105/105 testes PASS**, incluindo 6 testes novos de cadeia de etapas, ZIP de artefactos, `$input` e falha de executor. Gerado artefacto `ferrari-skill-installable` com o pacote da **mesma Skill**.
- **Ponte Ferrari inalterada em funcionamento:** no repositório `martaxi-boss/VPS`, a alteração [`ed2fa685`](https://github.com/martaxi-boss/VPS/commit/ed2fa685e2e0a2aa1c58df96273d3e013772fd31) substituiu **apenas 3 referências exatas da release** em `.github/workflows/ferrari-independent-vps-delivery.yml`; [`5f825f84`](https://github.com/martaxi-boss/VPS/commit/5f825f848055c9b8b2b9ea5fc3720688a69e8724) substituiu **apenas uma referência exata** em `.github/workflows/ferrari-skill-request.yml`. Nenhuma alteração ao SSH, lógica da ponte, Supervisor ou projetos externos.
- **Pendente de prova operacional na VPS:** a alteração ao workflow Ferrari de entrega em `VPS/main` foi enviada, mas o conector GitHub disponível neste ChatGPT **não lista runs de push** por SHA (ferramenta filtra eventos PR). Não foi obtido ainda o ID do deploy nem confirmação de `FERRARI_DEPLOY_TRANSPORT=PASS`, release ativa ou relatório de higienização. **Não declarar deployment bem-sucedido** apenas com commit ou CI de PR.
- **Pedido real de duas etapas já enviado:** [`beed919c`](https://github.com/martaxi-boss/VPS/commit/beed919c50f540e912b048e1bf46e4c2173ecaf8), `ferrari-requests/job-20261103-plan-105pass-82b5.json` com `kind=plan`, `web-template` seguido de `binary-strings` por `depends_on`/`input_from`; entrada apenas de texto sintético não confidencial. **PENDENTE:** o conector não devolve `run_id` de push. Confirmar instalação da release 143ee613, `FERRARI_SKILL_JOB_STATUS=completed`, `FERRARI_SKILL_END_TO_END=PASS` e os ficheiros do ZIP antes de declarar E2E PASS. Higienização restringida ao Ferrari; preservar rollback. A instalação da nova Skill na interface ChatGPT não está confirmada.
- **OCR anterior:** o pedido `78a92882` continua por certificar remotamente, sem duplicação automática, e não deve ser confundido com a nova funcionalidade de planos.

---


## Histórico do teste OCR inicial - 03/11/2026 (falha corrigida e certificada acima)

- Pedido unico enviado pela ponte Ferrari existente em `martaxi-boss/VPS`: commit [`78a92882`](https://github.com/martaxi-boss/VPS/commit/78a92882c10ebcde7b20db065b617b60708ceb71), ficheiro `ferrari-requests/job-20261103-ocr-70e12df0b.json`, `kind=invoke`, acao `tesseract-ocr` e imagem sintetica `ferrari-test.png` sem dados privados.
- VPS: o deploy certificado [`#41601238265`](https://github.com/martaxi-boss/VPS/actions/runs/41601238265) regista Tesseract `5.3.4-1build5` instalado em `/usr/bin/tesseract`. Isto prova instalacao, **nao** o resultado do pedido de OCR.
- Entrada validada separadamente em teste **local**: imagem PNG 490x96 (1 bit); Tesseract reconheceu `FERRARI OCR 2026`. Esta verificacao local nao substitui a execucao na VPS.
- **PENDENTE**: encontrar o `GitHub Actions run_id` do push do commit acima, examinar logs e `ferrari-skill-result-<run_id>`, confirmar `report.json` com `status=completed` e texto real em `artifacts/recognized.txt`. O conector disponivel devolve apenas runs associados a PR quando se pesquisa pelo commit, pelo que lista vazia **nao** prova que o push falhou ou passou. Nao declarar certificacao remota sem o resultado.
- Rota: **nao repetir automaticamente o pedido, nao criar Skill/camada/ponte, nao alterar SSH nem outros projetos**. Apos comprovar a resposta, registar PASS/FAIL com ID e executar higienizacao somente no ambito Ferrari, preservando a release certificada e rollback.

---

## Certificação final de staging — 03/11/2026: Lowcost Europa (PR #186)

**Bloqueio resolvido em GitHub Actions, sem alterar o website nem o motor Ferrari.** [PR #186 da Lowcost](https://github.com/martaxi-boss/lowcost-europa/pull/186) integrada na `main`, commit `0a1707e534d127ebd1f0f3f3cf6542ffaa5431b1`. Única alteração funcional: no workflow de QA existente, fixou-se `runs-on: ubuntu-24.04` (antes `ubuntu-latest`, que no dia 03/11 usou Ubuntu 26.04, incompatível com Playwright 1.56.1). Mantiveram-se a versão Playwright e o script de browser, acrescentando apenas triggers CI para alterações do próprio workflow ou do script.

**Verificação real após integração (commit da main):** [staging browser #41605911458](https://github.com/martaxi-boss/lowcost-europa/actions/runs/41605911458) **SUCCESS**, artefacto `lowcost-staging-browser-qa` descarregado e `result.json` lido: `status=PASS`, **15 verificações PASS, 0 erros, 0 avisos**. Inclui 7 páginas em desktop (1440 × 900) + 7 em mobile emulado (390 × 844) e HTTP público (robots `Disallow: /`, JS imagens HTTP 200, painel anónimo HTTP 302). **14 screenshots PNG**, todas as páginas sem overflow horizontal; verificações públicas de fotografias, filtros, comparação e menu móvel passaram. É um teste real de staging público de leitura/GUI, sem login, POST, compras ou seguir `/go/`. Não comprova dispositivo Android real nem fluxos autenticados de produção.

**Outras provas pós-merge:** [CI #41605911466](https://github.com/martaxi-boss/lowcost-europa/actions/runs/41605911466) **SUCCESS, 709/709 testes Django PASS** em PostgreSQL 16 temporário, migrações/Ruff/testes JS PASS; [audit #41605911500](https://github.com/martaxi-boss/lowcost-europa/actions/runs/41605911500) SUCCESS. Pré-merge: [browser #41605493764](https://github.com/martaxi-boss/lowcost-europa/actions/runs/41605493764) PASS e [CI #41605493789](https://github.com/martaxi-boss/lowcost-europa/actions/runs/41605493789) PASS. O erro histórico [#40664538172 tentativa 2](https://github.com/martaxi-boss/lowcost-europa/actions/runs/40664538172) era de instalação Chromium no runner, não um defeito demonstrado da aplicação.

**Ferrari inalterado:** VPS release `ec4dc5045a034e3fbbbcfe3477e1641e80714262`, rollback `9277a56b9b57c87b8b4e3dfbba08f4536add3625`; nenhum motor, SSH, Supervisor, outra Skill, serviço ou ferramenta foi alterado. Backend e staging testados pelos workflows existentes da Lowcost, não pela operação `vite-build` do Ferrari. [Certificação e histórico completos](docs/CERTIFICACAO_DJANGO_POSTGRES_STAGING_20261103.md).

---

## Histórico pré-correção — 03/11/2026: Django/PostgreSQL PASS; staging bloqueado pelo runner

**Backend real do projeto Lowcost Europa, via o CI existente, sem modificar repositório:** [run #41068103444, tentativa 2](https://github.com/martaxi-boss/lowcost-europa/actions/runs/41068103444) **SUCCESS** no commit atual `388860c6a167686a378b89f4282304bce89c25de`. Ambiente temporário PostgreSQL 16 no GitHub Actions, `Django check`, `check --deploy`, verificação de migrações, `Ruff` e testes de JS PASS; **709/709 testes Django PASS**, migrações aplicadas à base isolada. Isto não verifica a produção.

**Staging não certificado nesta tentativa:** [run #40664538172, tentativa 2](https://github.com/martaxi-boss/lowcost-europa/actions/runs/40664538172), FAIL **antes do navegador**. O `ubuntu-latest` passou a Ubuntu 26.04; o Playwright `1.56.1` rejeitou instalar o Chromium (`does not support chromium on ubuntu26.04-x64`). Sem screenshots/JSON novos, não há evidência atual do site. A tentativa 1, em **28/10/2026** num runner Ubuntu 24.04, tinha `BROWSER_QA_RESULT=PASS checks=13 errors=0`; prova histórica apenas, feita com script anterior. A repetição também tentou uma limpeza histórica de branch já inexistente (HTTP 422), sem alteração da main.

**Próxima correção mínima proposta, ainda não realizada:** em `martaxi-boss/lowcost-europa/.github/workflows/staging-browser-qa.yml`, fixar `runs-on: ubuntu-24.04` (ou atualizar Playwright após compatibilidade demonstrada) e lançar manualmente o workflow da main para testar desktop/móvel, fotografias, catálogo, navegação e respostas HTTP. O conector atual permite voltar a executar jobs mas não `workflow_dispatch`; o teste desta conversa não alterou esse workflow nem os dados e não garante que staging esteja a funcionar.

**Ferrari inalterado:** release VPS `ec4dc5045a034e3fbbbcfe3477e1641e80714262` e fallback `9277a56b9b57c87b8b4e3dfbba08f4536add3625`. O teste Django foi executado pelo CI do projeto, não pelo `vite-build` do Ferrari. Mantêm-se as [17/17 verificações do JS/CSS real da Lowcost](docs/TESTE_REAL_LOWCOST_EUROPA_20261103.md) para frontend local, sem confundir com testes de backend ou staging. [Relatório e logs](docs/CERTIFICACAO_DJANGO_POSTGRES_STAGING_20261103.md).

---

## Histórico — 03/11/2026: Lowcost Europa, código frontend real

**Ferrari ativo na VPS:** release `ec4dc5045a034e3fbbbcfe3477e1641e80714262`, [PR #10](https://github.com/martaxi-boss/skill-universal/pull/10) integrada. [Deploy real VPS #41601238265](https://github.com/martaxi-boss/VPS/actions/runs/41601238265) **SUCCESS, 99 testes PASS**, com `FERRARI_BROWSER_KEYBOARD_REAL=PASS`, `FERRARI_BROWSER_INTERACTIVE_CONTROLS_REAL=PASS`, Vite/Chromium e vista móvel PASS.

**Teste novo com código real, sem escrever na Lowcost:** fonte [martaxi-boss/lowcost-europa](https://github.com/martaxi-boss/lowcost-europa), commit `388860c6a167686a378b89f4282304bce89c25de`; usados o **JavaScript `catalog-explorer.js` e CSS `storefront.css` originais** e a cópia dos controlos HTML, com cinco ofertas fictícias num fixture estático. O Chromium real testou **17/17 comportamentos PASS**: pesquisa com acentos, filtros de equipamento/preço, ordenação de moedas, comparar até três, não aceitar quarta, limpar filtros/comparação. Zero erros JS, consola ou pedidos externos; captura desktop 1280×720 **868 570 bytes** e móvel CSS 390×844 **572 046 bytes**, zero overflow, spotcheck HTML sem avisos.

**Incidente corrigido com prova:** [primeiro pedido da Skill #41600631713](https://github.com/martaxi-boss/VPS/actions/runs/41600631713) obteve 17 PASS mas `button_space=finding`: o botão verdadeiro «Limpar filtros» move foco para a pesquisa após Enter; Ferrari testava Space no campo errado. Foi corrigido apenas `engine/browser_check.js` para refocar o botão entre as duas provas independentes. **[Repetição exata da Skill #41601466546](https://github.com/martaxi-boss/VPS/actions/runs/41601466546) SUCCESS**, `FERRARI_SKILL_JOB_STATUS=completed`, `FERRARI_SKILL_END_TO_END=PASS`, ZIP conferido: `Tab`, `Shift+Tab`, Enter e Space PASS, **`interactions.findings=[]`**. Links/formulários no fixture não testados (`not_requested`). Estes resultados não provam funcionamento Django/PostgreSQL, staging, produção, compras, integrações nem aplicação completa.

**Higienização Ferrari PASS:** removida só a release antiga `0196f37a...`, preservadas a ativa `ec4dc5045...` e a anterior certificada `9277a56b9...`. Espaço libertado **2 539 520 bytes (~2,42 MiB)**; **21,31 GiB livres**; `outside_ferrari_touched=false`. Nenhum outro projeto foi modificado, nem SSH, Supervisor, nova Skill, operação, camada, coordenador ou novo programa instalado. Catálogos estáveis: 56 candidatos Ubuntu, 23 detetados, 49 combinados; 12 operações base e 21 ações externas. [Relatório e evidências detalhados](docs/TESTE_REAL_LOWCOST_EUROPA_20261103.md).

**Próximo passo:** quando for necessário validar a aplicação Lowcost completa, usar os workflows de CI/Django/PostgreSQL e o browser QA de staging que já existem no próprio projeto; não confundir esta prova estática com backend ou produção.

---

## Histórico — 03/11/2026: Fase 6, teclado e controlos reais

**Ferrari ativo na VPS Ubuntu:** release `9277a56b9b57c87b8b4e3dfbba08f4536add3625`. [PR #9](https://github.com/martaxi-boss/skill-universal/pull/9) integrada; [CI #41598406165](https://github.com/martaxi-boss/skill-universal/actions/runs/41598406165) e [CI PR #41598460475](https://github.com/martaxi-boss/skill-universal/actions/runs/41598460475) SUCCESS. **[Deploy VPS #41598711120](https://github.com/martaxi-boss/VPS/actions/runs/41598711120)** SUCCESS, **99 testes PASS na VPS**, marcadores `FERRARI_BROWSER_KEYBOARD_REAL=PASS`, `FERRARI_BROWSER_INTERACTIVE_CONTROLS_REAL=PASS`, Vite/Chromium real, viewport responsivo, spotcheck HTML e geometria IFC todos PASS.

**Prova por pedido real da Skill:** [#41598946695](https://github.com/martaxi-boss/VPS/actions/runs/41598946695) SUCCESS, `FERRARI_SKILL_END_TO_END=PASS`; ZIP aberto, relatório `status=completed` e ficheiros reais conferidos. Chromium 156.0.8078.4 executou `Tab`, `Shift+Tab`, botão `Enter` e `Espaço`, âncora `Enter` e formulário `Enter` — **6 verificações PASS** em 4 controlos focáveis. O contador visual indicou 2 ativações e o formulário mostrou «Recebido: Ferrari fase 6». Capturas PNG desktop **51 916 bytes** e móvel **52 507 bytes**; zero overflow a 390 px, erros JS ou pedidos externos.

**Implementação mínima, sem nova operação:** a verificação de foco é observacional. **Somente** controlos marcados `data-ferrari-test` são acionados por teclado; sites sem marcadores devolvem `not_requested` para esses controlos e não se afirma que todos os botões de um projeto funcionam. Mantidas uma única Skill, as 12 operações base e 21 ações externas tipadas. Inventário: 56 candidatos Ubuntu; **23/56 detetados**; 49 programas em catálogos combinados. Nenhuma instalação extra, camada nova, serviço, nova ponte ou alteração de SSH.

**Higienização real Ferrari:** após testes PASS, removida a release obsoleta `13c4399257cd19496f378ad3f15cd1ebe877977b`, preservadas a ativa `9277a56b9...` e a anterior certificada `0196f37a...` para recuperação. Espaço libertado: **2 519 040 bytes (~2,40 MiB)**; **21,32 GiB** livres; `outside_ferrari_touched=false`. Certificação detalhada: [docs/CERTIFICACAO_INTERACOES_TECLADO_20261103.md](docs/CERTIFICACAO_INTERACOES_TECLADO_20261103.md). **Próxima fase:** testar um fluxo específico de um projeto web concreto, sem instalar indiscriminadamente aplicações nem criar camadas.

---

## Histórico — 03/11/2026: mobile responsivo e diagnóstico de acessibilidade

**Release atual Ferrari:** `0196f37a7610d1f95cd3371652308b7e2244f019`. [PR #8](https://github.com/martaxi-boss/skill-universal/pull/8) integrada. [CI da PR #41561833247](https://github.com/martaxi-boss/skill-universal/actions/runs/41561833247) SUCCESS, 99 testes PASS. [Entrega VPS #41561998389](https://github.com/martaxi-boss/VPS/actions/runs/41561998389) SUCCESS, **99 testes PASS na VPS**; `FERRARI_VITE_RESPONSIVE_REAL=PASS`, `FERRARI_BROWSER_A11Y_SPOTCHECK_REAL=PASS`, `FERRARI_VITE_BROWSER_REAL=PASS` e IFC geometria PASS.

**Skill ponta a ponta:** [pedido #41562205411](https://github.com/martaxi-boss/VPS/actions/runs/41562205411) SUCCESS com `FERRARI_SKILL_JOB_STATUS=completed` e `FERRARI_SKILL_END_TO_END=PASS`; ZIP aberto e verificado com site Vite compilado, duas capturas e JSON. Desktop 1280×720 (PNG 62 964 bytes); viewport CSS móvel 390×844 (PNG 56 548 bytes); a grelha passou de duas colunas para uma, sem overflow horizontal (0 px). JavaScript ativo, zero erros de consola e página, zero pedidos externos. Meta viewport presente, HTML `lang=pt`, três headings; zero imagens sem alt, botões/links sem nome e campos sem label no exemplo.

**Sem camadas:** a mesma operação `vite-build` passou a emitir `browser-mobile.png` e dados `mobile` em `browser-check.json`, sem novas ferramentas, operações, Skills ou serviços. Avisos básicos de acessibilidade são informativos; **não** equivalem a certificação WCAG, emulação Android nem testes de um sistema completo.

**Higienização real:** após PASS, a rotina Ferrari existente removeu `aefd8bb156f95e47c5a90b2a5d96db8d26f94283`, preservando `0196f37a...` ativa e `13c439925...` como fallback. Libertou **2 486 272 bytes (~2,37 MiB)**; **21,32 GiB** livres no fim. `outside_ferrari_touched=false`: SSH, Supervisor e outros projetos intocados.

**Inventário real estável:** 56 candidatos Ubuntu, **23/56 detetados**, 49 ferramentas nos catálogos combinados, **12 operações base** e **21 ações externas**. Relatório com evidências e limites: [docs/CERTIFICACAO_MOBILE_SPOTCHECK_20261103.md](docs/CERTIFICACAO_MOBILE_SPOTCHECK_20261103.md). **Próxima fase separada:** interação por teclado no mesmo navegador se necessária; não criar camadas nem instalar programas sem necessidade.

---

## Histórico — 03/11/2026: Vite testado no Chromium real + higienização

**Release ativa Ferrari:** `13c4399257cd19496f378ad3f15cd1ebe877977b`. [Deploy real VPS #41560720430](https://github.com/martaxi-boss/VPS/actions/runs/41560720430) SUCCESS, **99 testes PASS na VPS** e `FERRARI_VITE_BROWSER_REAL=PASS` (manteve `FERRARI_IFC_GEOMETRY_REAL=PASS`). [Pedido real pela Skill #41560954411](https://github.com/martaxi-boss/VPS/actions/runs/41560954411) SUCCESS com `FERRARI_SKILL_END_TO_END=PASS`; ZIP inspecionado com `dist/index.html`, JavaScript, CSS, `browser-check.json` e **`browser-screenshot.png` de 15 875 bytes**. Browser: Chromium headless shell `156.0.8078.4`, Playwright `1.64.1`, Node `22.23.4` e Vite `8.3.5` isolados no Ferrari; JavaScript executado (`demo_js_ready=yes`), `dom_ready=complete`, zero erros de consola/página e zero pedidos externos.

**Progresso sem camadas:** a sondagem VPS [#41559647734](https://github.com/martaxi-boss/VPS/actions/runs/41559647734) encontrou ausência de navegador nos caminhos sondados. A PR [#5](https://github.com/martaxi-boss/skill-universal/pull/5) acrescentou observação read-only; a PR [#6](https://github.com/martaxi-boss/skill-universal/pull/6) ampliou a operação **já existente `vite-build`**, sem criar outra operação nem Skill; a PR [#7](https://github.com/martaxi-boss/skill-universal/pull/7) corrigiu o caminho do headless shell após a falha real [#41560226160](https://github.com/martaxi-boss/VPS/actions/runs/41560226160). O instalador do navegador é exclusivo Ferrari e não altera Node global, SSH, serviços ou os outros projetos.

**Inventário real após a instalação:** 56 candidatos Ubuntu selecionados, **23/56 detetados**, **49 ferramentas nos catálogos combinados**, **12 operações base** e **21 ações externas tipadas**. Detetado **não** equivale a funcionalidade completa certificada. Testado: construir e renderizar site estático pequeno, não backend, pagamentos, autenticação, testes de acessibilidade ou aplicações complexas.

**Higienização após testes:** `FERRARI_ONLY_HYGIENE=PASS` em preview e apply. Duas releases antigas removidas (incluindo a tentativa de Chromium falhada), mantendo apenas `13c439925...` ativa e `aefd8bb156...` como fallback já testado. Espaço efetivamente libertado **4 988 928 bytes (~4,76 MiB)**; **21,32 GiB** livres no final; `outside_ferrari_touched=false`. Ver [certificação detalhada](docs/CERTIFICACAO_BROWSER_VITE_20261103.md). **Próxima fase separada:** verificação responsiva, acessibilidade e navegação por browser sobre casos reais, sem instalações desnecessárias.

---

## Histórico — 03/11/2026: geometria IFC e higienização

**Estado ativo certificado:** Ferrari release `f7eb9dcbda78a80f127b8981d9361e853672cd62`; [execução VPS #41558189146](https://github.com/martaxi-boss/VPS/actions/runs/41558189146) **SUCCESS**, **93 testes PASS na VPS**, `FERRARI_IFC_GEOMETRY_REAL=PASS`, `FERRARI_VITE_BUILD_REAL=PASS`. [Pedido real via Skill #41558414405](https://github.com/martaxi-boss/VPS/actions/runs/41558414405) **SUCCESS**, `FERRARI_SKILL_END_TO_END=PASS`; o ZIP foi aberto e `artifacts/ifc-report.json` confirmado com `IFC4`, 1 `IfcWall`, 8 vértices, 12 triângulos e dimensões medidas **5 × 0,2 × 3 metros**, sem erros geométricos. O relatório é de limites triangulados, não validação de segurança, volumes líquidos, colisões nem IDS.

**Atualizações sem camadas:** a operação `ifc-summary` foi estendida no leitor existente (PR [#3](https://github.com/martaxi-boss/skill-universal/pull/3)); a PR [#4](https://github.com/martaxi-boss/skill-universal/pull/4) corrigiu um teste que dependia indevidamente de Vite ausente. A primeira entrega [#41557825287](https://github.com/martaxi-boss/VPS/actions/runs/41557825287) falhou apenas nesse teste; a seguinte passou na íntegra. Não foram criadas operações, Skills, pontes, serviços ou dependências novas.

**Higienização real:** no deploy bem-sucedido, a rotina Ferrari própria removeu `405ae6fdcbabb9be8d81824a713296ae80b2aa04` (release de tentativa falhada) e `b8a7de8695b16bf064e0796c3cb9276d3a8254ed` (fallback obsoleto). Preservou somente a ativa `f7eb9dcb...` e a última anterior aprovada `29e016885...`. Espaço recuperado: **1 829 462 016 bytes (~1,70 GiB)**; livre final **21,61 GiB**. `outside_ferrari_touched=false`, sem modificar SSH, Supervisor ou outros projetos.

**Inventário estável:** 56 candidatos Ubuntu, 22 detetados dessa seleção, 48 programas detetados nos catálogos combinados, 12 operações base, 21 ações externas. **Próxima fase separada:** testes web em navegador real; primeiro validar capacidade headless da VPS sem instalar indiscriminadamente aplicações gráficas. Ver [relatório detalhado da fase](docs/CERTIFICACAO_GEOMETRIA_IFC_HIGIENE_20261103.md).

---

## Histórico — 03/11/2026: IFC e Vite funcionais

**Release ativa na VPS:** `29e016885f01c78941c37e4a147e207a1fc62f05`. [Instalação real #41556114851](https://github.com/martaxi-boss/VPS/actions/runs/41556114851) SUCCESS, **87 testes PASS na VPS** e marcadores `FERRARI_IFC_SEMANTIC_REAL=PASS`, `FERRARI_VITE_BUILD_REAL=PASS`. PR [#2](https://github.com/martaxi-boss/skill-universal/pull/2) integrada. IfcOpenShell `0.9.0.post1` no virtualenv independente do Ferrari, Vite `8.3.5` no npm próprio e Node `22.23.4` isolado. Nenhum SSH, Supervisor, programa global ou outro projeto alterado.

**Ponta a ponta da Skill com ficheiros reais:** [IFC #41556384002](https://github.com/martaxi-boss/VPS/actions/runs/41556384002) SUCCESS — `ifc-report.json` confirmou IFC4, `IfcProject=1`, `IfcWall=1`; [Vite #41556406846](https://github.com/martaxi-boss/VPS/actions/runs/41556406846) SUCCESS — `dist/index.html` e CSS/JS gerados. Em ambos, `FERRARI_SKILL_JOB_STATUS=completed`, `FERRARI_SKILL_END_TO_END=PASS` e ZIP verificado. [Inventário Skill #41556541593](https://github.com/martaxi-boss/VPS/actions/runs/41556541593) SUCCESS.

**Inventário atual medido:** 56 selecionados Ubuntu, **22/56 detetados**, 34 não detetados, **48 programas detetados nos catálogos combinados**; 12 operações base do Ferrari, 21 ações externas tipadas (sem alterar o seu catálogo). As novas operações são `ifc-summary` e `vite-build`. IfcOpenShell é entrada auxiliar, e Vite é o novo selecionado encontrado; não contar IfcOpenShell como 23.º da shortlist. **Limites:** inventário semântico IFC não substitui validação geométrica/estrutural/IDS; build Vite certificou projeto web estático pequeno, não Next.js, backend nem browser Playwright. FreeCAD e Playwright continuam não detetados.

**Referência desta fase:** [docs/CERTIFICACAO_IFC_VITE_20261103.md](docs/CERTIFICACAO_IFC_VITE_20261103.md). **A única Skill Ferrari continua válida** pelo mesmo protocolo `kind=operation` e o mesmo transporte. Não criar uma nova Skill nem instalar indiscriminadamente aplicações gráficas, serviços ou contentores.

---

## Histórico — 03/11/2026: Python, npm, contentores

**Estado atual certificado:** Motor Ferrari `1b3e232969c89801e8a0680d8ea751a536a53ce5` instalado na VPS Ubuntu, [entrega #41554557002](https://github.com/martaxi-boss/VPS/actions/runs/41554557002) SUCCESS com **79 testes PASS na VPS**. O [pedido real pela Skill #41554751046](https://github.com/martaxi-boss/VPS/actions/runs/41554751046) terminou `FERRARI_SKILL_END_TO_END=PASS` e devolveu `inventory.json` dentro de ZIP. CI do motor [#41554507978](https://github.com/martaxi-boss/skill-universal/actions/runs/41554507978) SUCCESS. A PR #1 foi integrada.

**Inventário medido:** 56 candidatos Ubuntu, 21 ações externas definidas e disponíveis, 21/56 candidatos detetados; 46 ferramentas detetadas nos catálogos combinados. O novo relatório reconhece OpenCV como módulo Python `cv2`, encontra o manifesto npm isolado do Ruflo e informa que Docker e Podman **não** foram encontrados. FreeCAD, IfcOpenShell, Next.js, Vite e Playwright ainda não estão detetados. A expansão desta fase aperfeiçoou **descoberta**, não instalou novos executores por esse motivo nem certificou BIM/IFC.

**Isolamento:** atualização dos SHA de versão apenas nos dois workflows Ferrari do repositório VPS; instruções SSH e outros projetos inalterados. A única Skill Ferrari existente continua utilizável com o mesmo contrato de pedidos.

**Próxima prioridade:** testar e integrar IFC profissional com IfcOpenShell isolado, de acordo com disponibilidade Ubuntu/Python e licença; desenvolver testes/build web com Node.js já instalado; só considerar FreeCAD headless, Vite/Playwright e contentores quando um caso concreto exigir. Não instalar indiscriminadamente GUIs, serviços ou modelos. Ver [certificação desta fase](docs/CERTIFICACAO_ECOSISTEMAS_20261103.md) e [detalhes da descoberta](docs/DESCOBERTA_ECOSISTEMAS_20261103.md).

---

**Documento canónico de continuidade do projeto.**
**Atualizado:** 2026-11-03. **Repositório exclusivo:** `martaxi-boss/skill-universal`.
**Ambiente-alvo:** servidor VPS Ubuntu 24.04 LTS (ou versão superior suportada, após certificação).
**Estado atual:** base instalada e testada na VPS; REA/Ruflo com teste CLI e JADX/Ghidra com teste funcional. A ligação direta Skill → VPS está certificada para operações implementadas; catálogo completo e execução arbitrária ainda não estão certificados.

## Skill diretamente ligada ao Motor Ferrari na VPS — 02/11/2026

**Certificação real:** [instalação #41546722719](https://github.com/martaxi-boss/VPS/actions/runs/41546722719) SUCCESS com **68 testes PASS na VPS**. Release ativa `1ff6e472b5ea4eab95785be224155f400c51aeaa`. **Dois pedidos reais completos** via conector GitHub → workflow dedicado → SSH existente → motor Ferrari → ZIP de resultados: [SVG #41546901101](https://github.com/martaxi-boss/VPS/actions/runs/41546901101) SUCCESS e [Markdown→DOCX automático #41547060999](https://github.com/martaxi-boss/VPS/actions/runs/41547060999) SUCCESS. Report e ficheiros comprovados pela extração do artefacto. Ver [relatório da ponte](docs/CERTIFICACAO_SKILL_VPS_20261102.md). **Não foram alteradas as pontes/workflows antigos, nem outros projetos.** A Skill ZIP atualizada precisa de estar instalada/selecionada no cliente e o conector GitHub precisa de estar autorizado. Repositórios públicos: **não enviar pedidos sensíveis**.

## Última prova real — Motor Ferrari universal (02/11/2026)

**GitHub Actions VPS [#41545170664](https://github.com/martaxi-boss/VPS/actions/runs/41545170664): SUCCESS.** Release `1b7ee15508d5780c3dbf22205ec625c2679348c5` ativa; **59 testes na VPS PASS**; 12 ações tipadas disponíveis em 45 programas detetados nos catálogos combinados (não 45/56). **Pedido natural → seleção automática → Pandoc → DOCX real: PASS**. Graphviz/JQ/file e fluxo multiexecutor PASS. Consultar [certificação universal](docs/CERTIFICACAO_UNIVERSAL_20261102.md). Mantêm-se pendentes a integração profunda REA/Ruflo, os restantes programas sem adaptador e a ligação direta Skill → VPS.

## Certificação real do catálogo operacional — 02/11/2026

**Execução GitHub Actions VPS [#41544817563](https://github.com/martaxi-boss/VPS/actions/runs/41544817563): SUCCESS.** Release `14c72563b654593f4d54f4977fe6fc83cfc4c87a` passou **57 testes** na VPS, inventário dinâmico e seleção de ferramentas PASS, 12 ações externas disponíveis, **45 programas detetados no catálogo combinado** (56 candidatos + ferramentas auxiliares; não são 45/56). O Ferrari executou Graphviz, Pandoc, jq e file, com resultados reais e fluxo orquestrado de 3 ferramentas. A nova operação `auto` acrescentada depois deste teste só será dada como certificada quando for provada numa execução posterior.

## Nova fase — motor de catálogo operacional (implementação)

O código acrescentou `engine/tool_runtime.py` e `engine/tool_actions.json`: **12 adaptadores de execução tipada** para diversas áreas, com `tools`, `actions`, `route`, `invoke` e passos `operation=tool` no orquestrador. O estado real de cada programa é verificado na VPS no momento do pedido; apenas os programas com adaptador têm ações executáveis. O catálogo de 56 candidatos **não** equivale a 56 executores instalados ou certificados. Até haver execução GitHub Actions na VPS, isto é implementação no GitHub e não prova de execução real. A ponte SSH existente mantém-se transporte; não modificar outros projetos.

## Fecho da fase CAD/3D/Office + limpeza — 2026-11-02

- **Entrega real na VPS:** GitHub Actions [#41541318347](https://github.com/martaxi-boss/VPS/actions/runs/41541318347) **SUCCESS**.
- **Versão ativa:** `d7708a825797cc40b8726b32cbe00673929f3e4c`; segunda versão de recuperação `b8a7de8695b16bf064e0796c3cb9276d3a8254ed`.
- **Testes na VPS:** 49 unitários PASS; operações `cad-stl`, `blender-house`, `office-pdf` exportaram realmente STL, BLEND, GLB, PNG e PDF, todos confirmados. REA/Ruflo testes CLI, JADX/Ghidra testes funcionais anteriores e desta release PASS.
- **Higienização EXCLUSIVAMENTE Ferrari:** 8 releases desatualizadas removidas, 7 318 695 936 bytes de espaço livre adicional (**~6,82 GiB**); espaço livre final **20,42 GiB**. Nenhuma pasta fora de Ferrari alterada por esta limpeza.
- **Still pending:** 56/56 shortlist certificada, fornecedores/modelos opcionais, execução real profunda REA/Ruflo, adaptação de FreeCAD/BIМ/IFC e ligação direta ChatGPT Skill -> Ferrari motor. Não declarar plataforma profissional ilimitada.

## CAD/3D/Office — instalado e testado em 02/11/2026

**GitHub Actions VPS #41540947069: SUCCESS.** Blender 4.0.2, OpenSCAD 2021.01 e LibreOffice foram executados na VPS. Modelos `solid.stl`, `house.blend`, `house.glb`, `house.png` e `document.pdf` gerados com confirmação. **48 testes PASS na VPS.** Release: `21735c20baa163cded0551144c9f8f7ef8db7431`. A limpeza segura de antigas releases é um trabalho separado e limitado ao próprio Ferrari.

## Expansão profissional em curso: CAD/3D/Office (histórico pré-certificação)

Operações novas no código: `cad-stl` (exportar modelo OpenSCAD → STL), `blender-house` (casa conceptual → BLEND, GLB e PNG CPU) e `office-pdf` (documentos Office → PDF). **O suporte só se considera operacional na VPS após execução real e log de certificação.** Manter separada a certificação prévia do motor base.

## Instalação real — prova mais recente de 02/11/2026

**GitHub Actions VPS #41538472015: SUCCESS.** Release `b8a7de8695b16bf064e0796c3cb9276d3a8254ed` instalado em `/home/ubuntu/.local/share/motor-ferrari/current`. **41 testes na VPS PASS**; orquestrador executou fluxo real HTML/SVG/strings. **JADX 1.5.6 passou na descompilação de Java; Ghidra 12.2 analisou /usr/bin/true com Java 25 isolado.** REA 6.8.0 e Ruflo 3.71.0 instalados e CLIs iniciadas (`--help`), mas sem certificação funcional profunda. Os 56 candidatos não equivalem a 56 programas instalados; ainda falta ligação direta da Skill.

Consultar [relatório da implantação real](docs/RELATORIO_REAL_VPS_20261102.md) antes de alterar o motor. **A secção histórica abaixo descreve o estado de pré-instalação e não prevalece sobre esta prova.**


## 1. Decisão central — não perder o objetivo

Desenvolver **UMA ÚNICA SKILL PESSOAL PROFISSIONAL**, para a pessoa pedir qualquer trabalho técnico, criativo, documental ou operacional, sem trocar de Skill por domínio.

O objetivo da Skill é proporcionar **amplitude progressiva**: CAD, desenhos de construção, arquitetura, BIM/IFC, 3D, vídeo, imagem, áudio, web, software, apps, PDF, documentos, dados, geoespacial, automação e engenharia reversa autorizada. **Isto define o âmbito a construir, NÃO declara que tudo já está implementado.** Nenhuma Skill garante, por si só, fazer literalmente tudo; cada capacidade necessita de ferramentas, dependências, dados, recursos físicos, adaptadores e testes.

Arquitetura definitiva:

```text
ChatGPT / Codex / outra IA (interpretação, planeamento e instruções)
            ↓
        UMA SKILL UNIVERSAL
            ↓
    ligação real e autenticada
            ↓
  MOTOR FERRARI INDEPENDENTE — VPS Ubuntu
            ├── ORQUESTRADOR PROFISSIONAL próprio
            ├── catálogo + seleção Ubuntu + verificação de instalação
            ├── programas, bibliotecas e fornecedores Linux licenciados
            ├── adaptadores tipados e ferramentas realmente executáveis
            └── testes, evidências, artefactos, logs e relatórios
            ↓
  resultado entregue à IA e ao utilizador
```

A **Skill** orienta; o **orquestrador** distribui operações; o **motor e os programas instalados na VPS** fazem a execução. Um nome no catálogo não é um programa instalado, e um programa instalado não é automaticamente utilizável pela Skill.

**Nunca misturar** o Ferrari com Project Leader, REA de outros projetos, Telegram, FADEGO, PINK IPTV ou outro repositório. Se REA ou Ruflo for necessário, instalar uma instância **independente**, no próprio Ferrari.

## 2. Registo anterior à instalação (histórico, substituído pelo relatório real de 02/11)

| Componente | Situação confirmada |
|---|---|
| Uma Skill (`skill/motor-universal-linux/SKILL.md`) | Criada; instruções, referências, contrato do motor |
| Catálogo GitHub | 125 candidatos investigados, **não instalados por este facto** |
| `engine/ubuntu_selection.json` | 56 ferramentas pré-selecionadas com evidência Linux/Ubuntu |
| Pacotes APT | 34 têm nomes de pacotes disponíveis em runner Ubuntu 24.04; **não significa instalados na VPS** |
| Ferramentas com instalação Linux externa | 22 candidatos sujeitos a versões, dependências, licenças e testes na VPS |
| Verificação de licenças ainda aberta | Scribus, OpenSCAD, LibreCAD, Audacity, OpenShot e Inkscape no manifesto atual; rever individualmente |
| Motor executor (`engine/ferrari.py`) | **7 operações tipadas**, com testes de software em runner Ubuntu |
| Orquestrador (`engine/orchestrator.py`) | DAG, dependências, preview, série/paralelo e logs; sem serviço persistente/recovery |
| MCP (`integrations/mcp_server.py`) | Ponte stdio criada, mas **sem ligação ponta-a-ponta à VPS comprovada** |
| Workflow `.github/workflows/deploy-vps.yml` | PRECHECK, DEPLOY, INSTALL_HEADLESS preparados; **não executados contra a VPS nesta auditoria** |
| Instalações/certificações da VPS | **NÃO CONFIRMADAS: 0 ferramentas certificadas na VPS pela evidência deste projeto** |
| Capacidade profissional universal completa | **NÃO IMPLEMENTADA; objetivo e roteiro, não conquista** |

Os testes GitHub Actions `ubuntu-24.04` confirmam apenas o que correram na máquina de testes. Um `PASS` de CI não certifica instalações, dispositivos, fornecedores ou resultados **da VPS do utilizador**.

As **sete operações implementadas** atualmente:
1. `web-template` — página HTML estática (landing, store, portfolio, dashboard);
2. `svg-poster` — criativo SVG simples;
3. `pdf-text` — extração de texto via `pdftotext`;
4. `image-resize` — redimensionamento via ImageMagick `convert`;
5. `video-thumbnail` — miniatura por FFmpeg;
6. `apk-decompile` — APK/DEX/JAR via JADX instalado;
7. `binary-strings` — cadeias de texto via `strings`.

Estas **não equivalem** a geradores profissionais de projetos completos, CAD, BIM, renderização 3D, vídeo cinematográfico ou aplicações full-stack.

## 3. Áreas obrigatórias — cobertura a desenvolver

| Área do utilizador | Programas/alternativas Ubuntu a avaliar | Estado da integração |
|---|---|---|
| Construção e projetos de edifícios | FreeCAD (incl. ferramentas BIM), LibreCAD, OpenSCAD, Blender, QGIS | **Ainda sem executor completo** |
| Arquitetura e BIM | FreeCAD; avaliar IfcOpenShell/Bonsai, IFC, ferramentas de desenho técnico Linux | **Pesquisa e certificação adicionais** |
| Desenhos e modelos 3D | Blender, FreeCAD, OpenSCAD, Solvespace | **Ainda sem adapter/render 3D profissional testado** |
| CAD 2D, plantas, cortes, cotas | LibreCAD, FreeCAD, exportações DXF/IFC/STEP conforme suporte real | **Pendentes testes de formato e precisão** |
| Imagem e design | Krita, GIMP, Inkscape, ImageMagick, libvips, Penpot | **Principalmente catálogo/integração pendente** |
| Vídeo e animação | FFmpeg, Kdenlive, OBS, Synfig, Blender | **Só miniaturas FFmpeg implementadas** |
| Áudio | Audacity, LMMS, faster-whisper | **Ainda sem executor áudio completo** |
| Websites, aplicações e jogos | Next.js, Vite, Playwright, Godot; testar compilação, backend e export | **Templates estáticos; stack completo pendente** |
| PDF, escritório, OCR | LibreOffice, Pandoc, Docling, Tesseract, OCRmyPDF, Typst | **Extração simples implementada; resto pendente** |
| Dados, mapas e análise | DuckDB, Polars, Streamlit, QGIS | **Adaptadores pendentes** |
| Engenharia reversa autorizada | REA independente, Ghidra, JADX, Apktool, Binwalk, radare2 | **Adapter JADX previsto; motores externos por instalar** |
| Automação e coordenação | Ferrari DAG próprio; Prefect opcional, Ruflo opcional | **DAG básico; persistência e monitorização pendentes** |
| IA local e criativos avançados | ComfyUI e modelos compatíveis se houver RAM/GPU suficiente; serviços gratuitos sujeitos a quotas | **Não prometer IA fotorealista em VPS sem recursos/modelos** |

Para obras e engenharia estrutural: produzir ficheiros técnicos e modelos **não substitui** verificação por profissionais habilitados, normas locais ou aprovação de projetos; não alegar validação estrutural não realizada.

Para cada nova área sem capacidade real: selecionar um programa livre com suporte Ubuntu, instalar e comprovar, implementar adaptador, testar com projeto real e só então marcar **UTILIZÁVEL**. Não criar uma Skill nova.

## 4. Regras de seleção obrigatórias

1. **Ubuntu primeiro.** Confirmar suporte Linux/Ubuntu 24.04, arquitetura da VPS, versão, origem oficial e manutenção. Se uma opção não trabalha no Ubuntu, procurar substituto de qualidade que trabalhe.
2. **Qualidade em vez de quantidade.** Selecionar software profissional e mantido, com formatos úteis e integração real. Estrelas GitHub são indicador secundário; evitar listas de lixo.
3. **Custo/licença.** Preferir licenças livres e programas realmente gratuitos para o uso pretendido. Avaliar licença de cada componente, modelo, plugin e distribuição. Não contar versões pirateadas, cracks nem chaves ilegítimas como fornecedores grátis.
4. **Dependências e fornecedores.** Distinguir programas locais, bibliotecas, modelos, fornecedores web/API e conectores. Registar Java, Node, Python, GPU, espaço, interfaces GUI e credenciais quando exigidas.
5. **Isolamento.** Ferrari tem a sua instalação, bibliotecas, versões, dados e diretórios próprios na VPS. Não modificar nem partilhar silenciosamente instalações com outros projetos.
6. **Apenas execução verificada.** Qualquer candidato deve cumprir os estados `DESCOBERTO -> FILTRADO_UBUNTU -> DEPENDENCIAS_CONFIRMADAS -> INSTALADO_VPS -> TESTADO_FUNCIONAL -> ADAPTADOR_INTEGRADO -> DISPONIVEL_PELA_SKILL`. Não saltar etapas.
7. **Orquestrador independente.** O núcleo do Ferrari decide ferramentas e fluxo, executa tarefas suportadas, recolhe artefactos, logs, erros e resultados; plugins de agentes são opcionais, não o coordenador principal.
8. **Não instalar ferramentas só por estarem num pacote de Skills.** Skills GitHub fornecem instruções, exemplos e processos; só aproveitar o que for útil, compatível e legalmente reutilizável numa Skill única.
9. **Sem prometer 100%.** Comunicar separadamente: preparado, disponível no Ubuntu, instalado na VPS, testado, integrado e realmente executável pelo utilizador.
10. **Sem alterar a VPS durante auditorias de catálogo.** Só executar instalação depois de diagnóstico real, seleção e confirmação da fase.

Fontes de verdade:
- `engine/ubuntu_selection.json` — seleção e evidência;
- `engine/ferrari.py` — operações realmente disponíveis;
- `engine/orchestrator.py` — capacidades reais de coordenação;
- `install/external-release-lock.json` — versões upstream externas;
- `docs/SELECAO_UBUNTU.md` e `docs/ORQUESTRADOR_SKILLS_GITHUB.md` — pesquisa e licenças;
- `docs/INSTALACAO_VPS.md` — procedimento real de instalação.

## 5. Ordem de execução — próximos trabalhos

- [x] Criar uma Skill única, catálogo, pré-seleção Ubuntu e núcleo de execução de base.
- [x] Criar orquestrador inicial, MCP stdio e workflow GitHub Actions manual.
- [x] Realizar testes básicos no runner Ubuntu 24.04, **sem confundir com a VPS**.
- [ ] Executar `PRECHECK` na VPS real; registar log, recursos CPU/RAM/SSD, versões e utilizador SSH.
- [ ] Instalar fonte independente pelo `DEPLOY`; confirmar commit, isolamento, `doctor` e testes no próprio servidor.
- [ ] Instalar seleção APT adequada (`INSTALL_HEADLESS`), verificar dependências e testes reais.
- [ ] Instalar motores externos (REA, Ghidra, JADX e outros necessários) com versões fixas, checksums e provas por ferramenta.
- [ ] Certificar cada categoria GUI/headless/GPU e fechar revisões de licença/fornecedor.
- [ ] Implementar adaptadores reais para **construção/CAD/BIM/3D**, incluindo criação, abertura e exportação de um modelo e/ou planta verificáveis.
- [ ] Implementar adaptadores restantes para imagem, vídeo, áudio, documentos, web/app, dados, mapas e automação.
- [ ] Testar persistência, recuperação, cancelamento, logs e integração do orquestrador com ferramentas externas.
- [ ] Certificar fluxo **IA -> Skill -> VPS -> orquestrador -> programa -> ficheiro -> resposta**, a partir da ligação real de cada cliente.
- [ ] Publicar matriz final de capacidades por domínio com casos de teste, resultados e limitações documentadas.

**Critério de conclusão:** não basta instalar pacotes; todas as capacidades anunciadas têm de produzir resultados comprováveis no ambiente Ubuntu real e ser utilizáveis a partir da mesma Skill. O objetivo é uma plataforma ampla e extensível, não uma promessa impossível de capacidade infinita.

## 6. Regras de continuidade em qualquer chat

Ao retomar:
1. **Ler primeiro `BOOTSTRAP.md`** e o estado real do repositório. Não recomeçar a arquitetura nem criar Skills alternativas.
2. Verificar último commit/CI e logs reais da VPS; distinguir ausência de prova de funcionamento.
3. Escolher a próxima tarefa pendente do capítulo 5, sem inventar que já foi executada.
4. Não mudar pressupostos, licenças, versões, coordenador nem projeto sem pedido explícito.
5. Atualizar este ficheiro **apenas após resultados comprovados**, mantendo o histórico de estado e a lista de pendências.
6. Quando a necessidade for uma nova área, **alargar o mesmo Ferrari**, não desviar para outro motor.

**Resumo permanente:** UMA Skill Universal + UM Motor Ferrari independente na VPS Ubuntu + UM Orquestrador próprio + ferramentas profissionais realmente instaladas, testadas e integradas. **Hoje o projeto tem uma base funcional e seleção prévia, mas não tem tudo implementado nem a VPS certificada.**

## 7. Auditoria e delivery GitHub — execução em 2026-11-02

- **Commit de auditoria/instalador:** `fa48826df447176afc2356efd66d4808c736f47c`.
- **CI no Ubuntu 24.04:** [run #41534293244](https://github.com/martaxi-boss/skill-universal/actions/runs/41534293244) — `success`; teste de código, registo, dependências APT no runner e regras de segurança do workflow passaram.
- **PRECHECK VPS real:** [run #41534293085](https://github.com/martaxi-boss/skill-universal/actions/runs/41534293085) — `failure` **por falta de credenciais GitHub `MOTOR_SSH_*`**. Passo SSH falhou antes de qualquer conexão. `Read-only VPS Ubuntu preflight` foi `skipped`.
- **Instalação na VPS:** não iniciada. **Não há nova evidência de compatibilidade do hardware da VPS nem de software instalado nela.**
- **Próximo desbloqueio necessário:** configurar os secrets SSH exclusivos deste repositório (ou ambiente `vps-motor-universal`) e executar manualmente `PRECHECK`; só após um PRECHECK PASS decidir `DEPLOY` e `INSTALL_HEADLESS`. Não colocar a chave privada nem os seus valores em ficheiros ou na conversa.
- **Verificações oficiais externas:** Ubuntu 24.04 (noble) tem pacote `nodejs` 18.19.1 nos repositórios padrão; REA 6.8.0 requer Node >=22.23.4 na série 22 / >=24.22.1 na série 24 / >=26.12.1; Ghidra 12.2 exige JDK 25. O instalador Ferrari evita alterar o Node.js global e não tenta instalar Ghidra/REA até existir ambiente isolado compatível.

**Delivery atual:** pronto para diagnóstico na VPS após configuração SSH; não pronto para declarar que todas as 56 ferramentas trabalham na VPS.
