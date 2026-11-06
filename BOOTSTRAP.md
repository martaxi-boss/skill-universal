# BOOTSTRAP — Motor Ferrari / Skill Universal Ubuntu

**Estado de referência: 05/11/2026 UTC.** Fonte canónica do estado e dos limites; números e versões têm de ser associados à execução que os mediu. Plano de fecho: [fases 5–10](docs/PLANO_FECHO_FERRARI_20261105.md). O resultado de CI não substitui um teste operacional na VPS.

**Estado prevalecente — Fase 7 certificada (05/11):** `current` = `758e1b435317fa26277b332b75bc47c67910be81`; fallback F6 `146145d5ada9c13e368df18727e4dbf4f5807664` (F5 `40c0e1cdf31b1fe9589ad8be90e5eac06eec2856`; histórico `87969badbde0a77c2c181bb9605357d51a4a30c0`). [Certificado F7](docs/CERTIFICACAO_FASE7_20261105.md): 274 testes CI PASS; [DAG VPS #42098800995](https://github.com/martaxi-boss/VPS/actions/runs/42098800995) retoma privada; [Skill→ZIP #42099036932](https://github.com/martaxi-boss/VPS/actions/runs/42099036932) PASS. **40/40 ações, 7/7 venvs, 47/56 candidatos.** CPU/RAM hard e Ruflo multiagentes não certificados; 16 APT globais e remoção transversal ficam F9–F10.

**Fase 8 (05/11): CERTIFICADA 40/40 ações tipadas com prova individual real.** ADB Android físico autorizado `android-adb-install-apk` executou instalação `Success` por GitHub Actions [#42128892714](https://github.com/martaxi-boss/VPS/actions/runs/42128892714); a APK de teste `com.example.empty9patch` foi depois removida com `adb uninstall` → `Success` (prova ConnectBot do proprietário). Não alterou PINK IPTV. [Fecho F8](docs/FASE8_FECHO_20261105.md), [certificado Android](docs/FASE8_CERTIFICACAO_ANDROID_20261105.md), [matriz F8 histórica](docs/FASE8_MATRIZ_COBERTURA_20261105.md). Fase 8 fechada apenas neste âmbito; release ativa F7 e fallback F6 preservados, sem APT global.

**Fase 9 (05/11): EM CURSO — auditoria transversal real, incluindo [simulações APT e comparação de releases #42132313840](docs/FASE9_AUDITORIA_E_HIGIENIZACAO_20261105.md).** [Relatório de auditoria/higiene](docs/FASE9_AUDITORIA_E_HIGIENIZACAO_20261105.md): [inventário Ferrari #42129972810](https://github.com/martaxi-boss/VPS/actions/runs/42129972810), [8 pastas e serviços #42130589954](https://github.com/martaxi-boss/VPS/actions/runs/42130589954), [limpeza segura de 543 caches / 2 613 248 bytes #42130786572](https://github.com/martaxi-boss/VPS/actions/runs/42130786572), [PM2 abandonado sem processos-filhos removido #42131306097](https://github.com/martaxi-boss/VPS/actions/runs/42131306097), [pós-verificação independente #42131425267](https://github.com/martaxi-boss/VPS/actions/runs/42131425267) PASS, mantendo os robôs e serviços protegidos. **Higiene adicional F9 (06/11):** 6 diretórios vazios legados Hopper removidos com 8 serviços protegidos inalterados [#42134483519](https://github.com/martaxi-boss/VPS/actions/runs/42134483519); workflow temporário retirado, workflow original restaurado e testado [#42134629602](https://github.com/martaxi-boss/VPS/actions/runs/42134629602). Smoke Ferrari independente após higiene [#42134719562](https://github.com/martaxi-boss/VPS/actions/runs/42134719562) PASS, 40/40 ações invocáveis, 47/56 programas privados detetados. **Pendentes:** classificação e eventual remoção segura dos 16 pacotes APT globais; as seis alterações locais rastreadas em PINK e as seis no IPTV VPN Bot; confirmação por release da correspondência GitHub↔VPS e classificação de resíduos externos. Não foram removidos pacotes APT nem diretórios de outros projetos. **Não declarar F9 encerrada.**

## 1. Decisão permanente — UMA ÚNICA SKILL

ChatGPT, Codex ou outra IA interpreta → Skill Universal Ferrari → GitHub autenticado → workflow exclusivo em martaxi-boss/VPS → SSH existente → Ferrari Ubuntu → executores privados → relatório e ZIP.

A lógica, seleção e orquestração pertencem ao Ferrari. Não adicionar coordenadores ou Skills paralelas, não reescrever a ponte SSH, não partilhar diretórios, fornecedores ou dependências com PINK IPTV, Engenharia Reversa antiga, Project Leader, Telegram, FADEGO ou Low Cost Europa. O diretório Ferrari tem exatamente o nome do repositório GitHub: **/srv/projects/skill-universal/**.

## 2. Fotografia atual com provas

| Elemento | Prova e âmbito |
|---|---|
| **Release atual — Fase 7 CERTIFICADA no âmbito DAG** | `758e1b435317fa26277b332b75bc47c67910be81`; [ativação VPS #42098645092](https://github.com/martaxi-boss/VPS/actions/runs/42098645092), [DAG #42098800995](https://github.com/martaxi-boss/VPS/actions/runs/42098800995), [CI 274 testes](https://github.com/martaxi-boss/skill-universal/actions/runs/42097832176) PASS |
| **VPS read-back + fallback** | `current` e fallback F6 `146145d5ada9c13e368df18727e4dbf4f5807664` comprovados em [VPS #42098645092](https://github.com/martaxi-boss/VPS/actions/runs/42098645092); [certificado F6](docs/CERTIFICACAO_FASE6_20261105.md) |
| **Inventário depois da correção — 05/11** | [VPS #42011461022](https://github.com/martaxi-boss/VPS/actions/runs/42011461022): 55/56 candidatos detetados, 40 ações; OpenCV identificado numa venv Docling **privada Ferrari**, sem depender da instalação global de Python para a sua deteção. Penpot continua ausente; `report.json` completed e ZIP PASS |
| **Ponto 3 — CERTIFICAÇÃO FUNCIONAL (05/11)** | [Matriz e 7 execuções reais pela Skill](docs/CERTIFICACAO_FUNCIONAL_PONTO3_20261105.md): web/browser, documentos, dados, imagem, áudio/vídeo, CAD/IFC/3D, orquestração e REA/Android, com limites por caso testado; sem certificar automaticamente todas as ferramentas |
| **Ponto 2 — MIGRAÇÃO DOS EXECUTORES CONCLUÍDA (05/11)** | [VPS #42030605124](https://github.com/martaxi-boss/VPS/actions/runs/42030605124) **SUCCESS**: `FERRARI_PRIVATE_EXECUTORS=40/40_PASS`, Python privado DuckDB/Polars, 4 ações Python CLI, documentos, Imagemagick/libvips, Calibre EPUB, Darktable JPEG→TIFF, Krita JPEG→PNG, GIMP XCF, Scribus PDF/SLA, LMMS WAV, MLT→MP4 e Playwright/Vite testados. Executáveis e dependências da aplicação copiados dentro de `/srv/projects/skill-universal/`; **sem instalações APT globais na VPS**. Bibliotecas fundamentais do sistema operativo Ubuntu continuam a existir no SO; 40/40 não certifica funcionalidades opcionais de todas as aplicações |
| **Verificação real da Skill web** | [VPS #41994937194](https://github.com/martaxi-boss/VPS/actions/runs/41994937194): pedido novo `kind=operation`, `vite-build`, Playwright real, `report.json` completed, `response.zip` com browser-check.json, capturas desktop/móvel e HTML: **FERRARI_SKILL_END_TO_END=PASS**. Workflow temporário retirado e workflow de entrega original restaurado byte a byte |
| Transporte por GitHub Actions | O workflow Ferrari no repositório VPS continua **pinado em 292aeb7d10eecef8c3ca84760cd579e84e4b97f3 para seleção/validação do pedido**. Não confundir o pin com o HEAD do motor nem mudar o workflow/SSH sem ordem específica |
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
