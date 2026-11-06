# BOOTSTRAP — Motor Ferrari / Skill Universal Ubuntu

**06/11/2026 — CATÁLOGO UNIVERSAL ATIVO E HIGIENE VPS CERTIFICADA.** Uma única fonte `engine/catalog.json` no Ferrari: **173 programas + 272 interfaces de função (12 base + 40 ações + 220 REA) + 3 dependências centrais + 2 fornecedores locais = 450 registos**; nenhuma origem REA separada. Release ativa na VPS `7bf6dcecf15da26502c5969b5eee54d5e116fc32`, fallback privado `952b0a75ba798471b07053677d53791bd078ed56`. [Ativação #42294843737](https://github.com/martaxi-boss/VPS/actions/runs/42294843737) PASS (40/40 ações, 8/8 serviços), [inventário pós-limpeza #42297678715](https://github.com/martaxi-boss/VPS/actions/runs/42297678715) PASS (450, 272/272 selecionáveis, 55/55 programas Ubuntu selecionados detetados). [Higiene inicial #42295330408](https://github.com/martaxi-boss/VPS/actions/runs/42295330408) retirou uma release antiga; [segunda higiene #42297182419](https://github.com/martaxi-boss/VPS/actions/runs/42297182419) retirou outras **9**, com 19 251 200 bytes libertados nessa execução e rollback preservado. Nenhum catálogo legado dentro da release ativa. **Fase 9 ainda incompleta:** oito pacotes APT globais preservados, dependências transitivas e funções não integradas por certificar; a Skill instalada no ChatGPT não é atualizada automaticamente. [Política](docs/CATALOGO_UNICO_E_DEPENDENCIAS.md).

**Ponto 1 — OpenPencil (prova histórica de 06/11):** release `a266b25e06a9c8acf1fdc940d22b99070cd17ded` estava ativa naquela prova; [Skill→ZIP #42145727316](https://github.com/martaxi-boss/VPS/actions/runs/42145727316) FIG/SVG/HTML PASS. Cliente ChatGPT atualiza-se no fecho geral.

**Ponto 2 — ComfyUI CPU (06/11):** [PNG real #42149365272](https://github.com/martaxi-boss/VPS/actions/runs/42149365272) 256×256 PASS; [higiene #42149831403](https://github.com/martaxi-boss/VPS/actions/runs/42149831403) retirou TinySD incompatível. [Prova](docs/COMFYUI_PONTO2_CPU.md).

**Ponto 3 — faster-whisper CPU (06/11):** [ASR #42170510453](https://github.com/martaxi-boss/VPS/actions/runs/42170510453) áudio inglês 11 s → TXT/SRT/JSON PASS em 2,24 s, tiny MIT privado. [Prova](docs/FASTER_WHISPER_PONTO3_CPU.md).

**Ponto 4 — Ruflo (06/11):** CLI MIT 3.71 privado [#42186639714](https://github.com/martaxi-boss/VPS/actions/runs/42186639714) PASS; rota/memória local [#42187084139](https://github.com/martaxi-boss/VPS/actions/runs/42187084139) PASS, mas memória iniciou daemon; [auditoria #42187338181](https://github.com/martaxi-boss/VPS/actions/runs/42187338181) confirmou zero processos Ruflo ativos. **Multiagentes NÃO certificados; Ruflo opcional**, sem segundo coordenador. [Detalhes](docs/RUFLO_PONTO4_20261106.md).

**Histórico F7 (05/11):** releases `758e1b435317fa26277b332b75bc47c67910be81` (F7), `146145d5ada9c13e368df18727e4dbf4f5807664` (F6), `87969badbde0a77c2c181bb9605357d51a4a30c0` (histórico). Provas arquivadas em Git e docs.

**Fase 8 (05/11): CERTIFICADA 40/40 ações.** ADB Android físico testou instalar e remover APK sintética [#42128892714](https://github.com/martaxi-boss/VPS/actions/runs/42128892714) PASS, sem tocar em PINK. [Fecho F8](docs/FASE8_FECHO_20261105.md); sem APT global.

**Ponto 5 / Fase 9 — NÃO FECHADA:** [APT #42225950692](https://github.com/martaxi-boss/VPS/actions/runs/42225950692) removeu oito pacotes antigos; **oito restantes preservados**. Os executores estão privados, com testes GUI parciais [#42250649475](https://github.com/martaxi-boss/VPS/actions/runs/42250649475) e [QGIS #42246944925](https://github.com/martaxi-boss/VPS/actions/runs/42246944925). [Auditoria #42254557374](https://github.com/martaxi-boss/VPS/actions/runs/42254557374) ainda não autoriza purga global. Alterações PINK/bot preservadas #42226572746. [F9](docs/FASE9_AUDITORIA_E_HIGIENIZACAO_20261105.md).

**F9 ainda NÃO encerrada:** [APT #42225950692](https://github.com/martaxi-boss/VPS/actions/runs/42225950692) removeu 8 pacotes antigos; 8 restantes preservados. [Simulação #42251778630](https://github.com/martaxi-boss/VPS/actions/runs/42251778630) prevê remover só esses 8; [auditoria de referências #42252073995](https://github.com/martaxi-boss/VPS/actions/runs/42252073995) ficou incompleta em quatro pastas, impedindo uma purga segura. Edição CAD, áudio, vídeo, cenas OBS e GUI/provedores QGIS ainda exigem testes específicos. Outras pastas da VPS não foram modificadas; alterações locais PINK/bot preservadas [#42226572746](https://github.com/martaxi-boss/VPS/actions/runs/42226572746). [Relatório e limites](docs/FASE9_AUDITORIA_E_HIGIENIZACAO_20261105.md).

**Ponto 6 / Fase 10 — técnica PASS, fecho condicionado.** [VPS #42207839068](https://github.com/martaxi-boss/VPS/actions/runs/42207839068) 40 ações, 8/8 serviços, fallback F7, sem coordenador Ruflo. [Skill→ZIP #42207928270](https://github.com/martaxi-boss/VPS/actions/runs/42207928270) PASS. F9 e reconciliação de releases continuam abertas; sem certificação administrativa 10/10. [Detalhes](docs/FASE10_CERTIFICACAO_FINAL_20261106.md).


**Ponto 7 — Ruflo assistido (histórico):** [#42216565299](https://github.com/martaxi-boss/VPS/actions/runs/42216565299) registou dois papéis, duas tarefas e executou jq/REA privados; [Skill→ZIP #42218479317](https://github.com/martaxi-boss/VPS/actions/runs/42218479317) PASS na release anterior `f1f3b03525adec7018d7d629243e7b0fbb7f5087`. Inferência LLM autónoma não certificada; sem segundo coordenador. [Contrato](docs/RUFLO_SINGLE_HOST_CERT_20261106.md).

## 1. Decisão permanente — UMA ÚNICA SKILL

ChatGPT, Codex ou outra IA interpreta → Skill Universal Ferrari → GitHub autenticado → workflow exclusivo em martaxi-boss/VPS → SSH existente → Ferrari Ubuntu → executores privados → relatório e ZIP.

A lógica, seleção e orquestração pertencem ao Ferrari. Não adicionar coordenadores ou Skills paralelas, não reescrever a ponte SSH, não partilhar diretórios, fornecedores ou dependências com PINK IPTV, Engenharia Reversa antiga, Project Leader, Telegram, FADEGO ou Low Cost Europa. O diretório Ferrari tem exatamente o nome do repositório GitHub: **/srv/projects/skill-universal/**.

## 2. Fotografia atual com provas

| Elemento | Prova e âmbito |
|---|---|
| **Release Ruflo histórica** | `f1f3b03525adec7018d7d629243e7b0fbb7f5087` anterior; atual `7776a34e667d76ae0e980e65449d2b2cc67c2059` (#42263466893). |
| **Fallback preservado** | release F7 anterior `758e1b435317fa26277b332b75bc47c67910be81`; retorno testado pelo mecanismo de rollback protegido, sem comutação de retorno nesta implantação |
| **Inventário depois da correção — 05/11** | [VPS #42011461022](https://github.com/martaxi-boss/VPS/actions/runs/42011461022): 55/56 candidatos detetados, 40 ações; OpenCV identificado numa venv Docling **privada Ferrari**, sem depender da instalação global de Python para a sua deteção. Penpot continua ausente; `report.json` completed e ZIP PASS |
| **Ponto 3 — CERTIFICAÇÃO FUNCIONAL (05/11)** | [Matriz e 7 execuções reais pela Skill](docs/CERTIFICACAO_FUNCIONAL_PONTO3_20261105.md): web/browser, documentos, dados, imagem, áudio/vídeo, CAD/IFC/3D, orquestração e REA/Android, com limites por caso testado; sem certificar automaticamente todas as ferramentas |
| **Ponto 2 — MIGRAÇÃO DOS EXECUTORES CONCLUÍDA (05/11)** | [VPS #42030605124](https://github.com/martaxi-boss/VPS/actions/runs/42030605124) **SUCCESS**: `FERRARI_PRIVATE_EXECUTORS=40/40_PASS`, Python privado DuckDB/Polars, 4 ações Python CLI, documentos, Imagemagick/libvips, Calibre EPUB, Darktable JPEG→TIFF, Krita JPEG→PNG, GIMP XCF, Scribus PDF/SLA, LMMS WAV, MLT→MP4 e Playwright/Vite testados. Executáveis e dependências da aplicação copiados dentro de `/srv/projects/skill-universal/`; **sem instalações APT globais na VPS**. Bibliotecas fundamentais do sistema operativo Ubuntu continuam a existir no SO; 40/40 não certifica funcionalidades opcionais de todas as aplicações |
| **Verificação real da Skill web** | [VPS #41994937194](https://github.com/martaxi-boss/VPS/actions/runs/41994937194): pedido novo `kind=operation`, `vite-build`, Playwright real, `report.json` completed, `response.zip` com browser-check.json, capturas desktop/móvel e HTML: **FERRARI_SKILL_END_TO_END=PASS**. Workflow temporário retirado e workflow de entrega original restaurado byte a byte |
| Transporte por GitHub Actions | Validador no workflow original VPS **pinado em `0b50e1d403deff8f3ccb421edd0b41c397d66b9b`**; executa a release `current`. [Skill #42263667753](https://github.com/martaxi-boss/VPS/actions/runs/42263667753) e [#42265187873](https://github.com/martaxi-boss/VPS/actions/runs/42265187873) PASS; SSH inalterado. |
| Funcionamento ponta a ponta | [#41981152670](https://github.com/martaxi-boss/VPS/actions/runs/41981152670), de 05/11: pedido real **kind=rea-mcp**, status completed, executor privado e ZIP; FERRARI_SKILL_END_TO_END=PASS |
| **Última execução de deploy e higienização** | [VPS #42030605124](https://github.com/martaxi-boss/VPS/actions/runs/42030605124) **SUCCESS**, release ativada e limpeza só do Ferrari: **31 releases antigas** e **12 diretórios de testes temporários** removidos; **905244672 bytes** de espaço livre ganhos; **43,47 GiB livres** após limpeza; cache npm já ausente (0 bytes ganhos nesse passo). `FERRARI_ONLY_HYGIENE=PASS`, `FERRARI_PRIVATE_NPM_CACHE_HYGIENE=PASS`, `FERRARI_RELEASE_AND_HYGIENE=PASS`. Nenhum outro projeto alterado |
| REA próprio do Ferrari | **rea-agents@6.8.0**, instalado em .runtime/npm/rea, catálogo com **229 nomes MCP**. Catálogo não significa 229 ferramentas certificadas. Chamada ELF real [#41717389118](https://github.com/martaxi-boss/VPS/actions/runs/41717389118) e cenário [#41718385142](https://github.com/martaxi-boss/VPS/actions/runs/41718385142) PASS |
| Hopper privado | **Hopper 6.6.1**, pacote oficial validado e binário isolado em tools/hopper-6.6.1; origem [#41921893982](https://github.com/martaxi-boss/VPS/actions/runs/41921893982), doctor REA [#41922087539](https://github.com/martaxi-boss/VPS/actions/runs/41922087539) PASS. **Versão demo**, sem licença comercial nem certificação de todas as funções |
| Ferramentas Android | Apktool **3.0.3**; AAPT2, Apksigner, Zipalign, ADB dentro de tools/android-cli-36.0.0, APK sintético testado [#41854398886](https://github.com/martaxi-boss/VPS/actions/runs/41854398886). ADB sem dispositivo físico certificado |
| REAs legados | **REA FINAL e Trial removidos da VPS**; ausência verificada [#41840478411](https://github.com/martaxi-boss/VPS/actions/runs/41840478411). O REA privado do Ferrari permanece e não deve ser apagado |
| Atalho legado | Após a migração dos launchers, **/home/ubuntu/.local/share/motor-ferrari deixou de ser um symlink de trabalho**. O caminho canónico é /srv/projects/skill-universal. O código correspondente foi integrado no merge 292aeb7d; verificar novamente na VPS antes de qualquer nova remoção |

**Base histórica que continua válida enquanto evidência daquela data, não como estado atual:** [#41716562469](https://github.com/martaxi-boss/VPS/actions/runs/41716562469) (164 testes), [#41672372249](https://github.com/martaxi-boss/VPS/actions/runs/41672372249) (inventário inicial), [#41786521407](https://github.com/martaxi-boss/VPS/actions/runs/41786521407) (197 testes, release histórica 0a1a4c..., 35 ações). Inventários anteriores registaram 81 programas detetados e 55/56 candidatos Ubuntu. Nenhuma destas contagens certifica 81 programas funcionais.

**Ponto 2 fechado com teste na VPS e limpeza comprovada em 05/11/2026.**

## 3. Estrutura e independência física

- **/srv/projects/skill-universal/current**: ligação para a release ativa dentro de releases/. A SHA efetivamente ativa deve ser confirmada num inventário real, não inferida a partir do HEAD do GitHub.
- **.runtime/**: ambientes Python, npm, caches, resultados, pedidos e dados do motor, exclusivamente Ferrari.
- **runtimes/**: Node 22.23.4 e Java 25.0.5 privados.
- **tools/**: Ghidra 12.2, JADX 1.5.6, Apktool 3.0.3, fornecedores privados Ghidra/JADX do REA, Android CLI, Hopper 6.6.1 e outros executores verificados.
- **releases/**: versões do motor; preservar release atual e fallback, sem deletar em lote.
- A auditoria de base [#42011202485](https://github.com/martaxi-boss/VPS/actions/runs/42011202485) encontrou 32 ações a resolver os executores fora do Ferrari. **A migração foi concluída em 05/11: 40/40 executores apontam para caminhos dentro do Ferrari**, com testes funcionais reais e Python DuckDB/Polars privado [#42030605124](https://github.com/martaxi-boss/VPS/actions/runs/42030605124). A independência diz respeito às dependências específicas da aplicação, não à eliminação das bibliotecas fundamentais do Ubuntu; funcionalidades opcionais não testadas mantêm limites próprios.
- **Requisito cumprido nas 40 ações do Ferrari em 05/11:** executáveis e dependências de aplicação empacotados em `tools/`, `runtimes/` e `.runtime/`, com testes reais antes da ativação. Não fazer instalações APT globais na VPS; preservar o Ubuntu base, não apagar pacotes partilhados nem criar outro motor. Aplicações opcionais ou funcionalidades não testadas continuam sujeitas a validação quando forem necessárias.

**NÃO autorizar** eliminação de diretórios, dependências, versões fallback, dados, serviços ou pacotes de outros projetos por semelhança de nomes. Duplicação de dependências privadas entre projetos pode ser intencional para garantir isolamento.

## 4. Capacidades e limites observados

**Limite do ponto 3:** o CAD STL [#42035082826](https://github.com/martaxi-boss/VPS/actions/runs/42035082826) usou `/usr/bin/openscad`; o 40/40 privado do ponto 2 abrangia as **ações tipadas**, não todas as operações base. Detalhes no relatório.

### Ponto 3 — capacidades demonstradas

Web/Playwright, documentos/PDF/OCR, dados, imagem, áudio/vídeo, CAD/BIM/3D, automação e REA foram testados em casos concretos, sempre com limites de formatos e fornecedores. A tabela detalhada e os testes históricos estão arquivados em [Histórico Ponto 3](docs/HISTORICO_PONTO3_CERTIFICACAO_20261105.md) e nas [provas funcionais](docs/CERTIFICACAO_FUNCIONAL_PONTO3_20261105.md). **Desde 05/11/2026, a instalação ADB em Android físico está também certificada na Fase 8** [#42128892714](https://github.com/martaxi-boss/VPS/actions/runs/42128892714). A certificação 40/40 refere-se às ações tipadas, não a todas as funções GUI, programas opcionais, modelos, GPU, quotas CPU/RAM ou todas as ferramentas REA MCP.

## 4-A. Âmbito universal e portas de passagem

O objetivo progressivo continua a incluir **CONSTRUÇÃO, CAD, BIM/IFC, 3D, web, aplicações, gráficos, vídeo, áudio, documentos, mapas e engenharia reversa autorizada**. Cobertura transversal ainda **NÃO IMPLEMENTADA** como certificação global: não confundir catálogo com resultado entregue.

Estados que a seleção deve distinguir: DESCOBERTO → compatível com Ubuntu → dependências verificadas → **INSTALADO_VPS** → adaptador tipado → teste real → **DISPONIVEL_PELA_SKILL**. Apenas certificar cada fase com evidência correspondente.

O workflow manual de deploy do repositório Ferrari mantém as fases **PRECHECK, DEPLOY e INSTALL_HEADLESS**; a via operacional já existente usa o workflow exclusivo do repositório VPS. Não executar deploy/instalação manual para repetir componentes funcionais ou contornar portas de segurança.

## 5. Pendências prioritárias

1. **Sincronia de estado:** aferir por pedido de inventário somente de leitura a release realmente ativa, número atual de ações e executores privados; comparar com GitHub e com o pin do validador.
2. **Entrega da única Skill:** atualizar e validar SKILL.md e referências portáteis; empacotar skill.zip; verificar separadamente se a versão nova foi instalada no ChatGPT. Repo atualizado não prova cliente atualizado.
3. **Higienização segura:** classificar binários, venvs, APT globais, fornecedores e resíduos por propriedade; eliminar apenas ficheiros exclusivos com prova e rollback, sem mexer em projetos alheios.
4. **Capacidades restantes:** adicionar adaptadores tipados ao Ferrari existente por necessidade real, provar em CI, VPS e pedido Skill→GitHub→VPS→ZIP. Não criar camadas nem fornecedores pagos obrigatórios.
5. **Ausência de legado:** depois da remoção dos REAs antigos, confirmar que rotinas e documentação não os referenciam como instalações ativas; preservar o REA privado.

Não declarar cobertura universal de todas as tarefas, fornecedores e formatos sem testes ponta a ponta.

## 6. Execução, segurança e recuperação

- Os tipos aceites pela Skill são **inventory, operation, invoke, auto, plan e rea-mcp**. Consultar [references/github-bridge.md](skill/motor-universal-linux/references/github-bridge.md) antes de emitir um pedido.
- Criar apenas JSON de pedido novo, sem segredos ou dados pessoais em repositório público; base64 não é encriptação. Identificar run pelo commit correspondente e exigir response.zip, report.json, status completed e ficheiros reais.
- Na VPS, usar o Ferrari e SSH existentes, sem comandos arbitrários enviados em pedidos e sem instalar fora de /srv/projects/skill-universal. O workflow manual de deploy não deve repetir instalações existentes por defeito.
- Preservar sempre checkpoints e fallback antes de qualquer alteração com impacto operacional.
- Relatórios antigos em [docs/](docs/) permanecem evidência histórica. Este BOOTSTRAP, o código e os runs atuais governam o presente.
