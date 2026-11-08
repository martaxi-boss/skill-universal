# BOOTSTRAP — Motor Ferrari / Skill Universal Ubuntu

**Estado 08/11:** Ferrari VPS `e83ed6d` ativo, `e0509d5` fallback; Skill única v1.0.8 atualizada. [QA e provas](docs/CORRECAO_QA_TRABALHOS_REAIS_20261108.md).

**Vozes:** Piper original e Raquel; ver Skill.

## CONTRATO OBRIGATÓRIO — ANFITRIÃO, SUB-ANFITRIÃO RUFLO E SUBAGENTES (07/11/2026)

**REGRA VINCULATIVA / BLOQUEIO DE FECHO FUNCIONAL:** o Ferrari completo DEVE disponibilizar a hierarquia **IA anfitriã (ChatGPT, Codex ou outra autorizada) → Ruflo como sub-anfitrião gestor da equipa → subagentes trabalhadores → motor Ferrari e catálogo único → ferramentas reais → validação pelo anfitrião e entrega**. O Ruflo e os agentes **NÃO SÃO OPCIONAIS NA ARQUITETURA-ALVO**. Não os substituir silenciosamente por execução sem agentes, nem criar outra Skill, segundo motor, coordenador IA residente na VPS ou segundo catálogo. Pedidos simples podem utilizar diretamente uma ação Ferrari; isso não dispensa a equipa na certificação do produto completo.

**PAPÉIS OBRIGATÓRIOS / INTELIGÊNCIA PARTILHADA:** (1) o anfitrião ChatGPT (ou Codex/Claude/outro escolhido) é a **única IA anfitriã partilhada por toda a equipa**; entende a ordem, planeia e disponibiliza raciocínio contextualizado aos diferentes papéis; **não se cria nem paga uma instância/modelo independente por agente**; (2) Ruflo, como sub-anfitrião, cria e gere os agentes especializados, distribui tarefas, recolhe resultados e coordena colaboração e dependências; (3) os agentes devem receber trabalho e orientação inteligente específicos do seu papel a partir da **mesma IA anfitriã** (programador, investigador, revisor, tester, etc.), colaborar através de resultados/feedback entre agentes e usar os executores Ferrari/REA aprovados; (4) o anfitrião revê, corrige e aceita o trabalho final. **Agente especializado com raciocínio assistido pela IA partilhada NÃO significa um novo modelo LLM por agente**. O Ferrari é o único motor de ferramentas; Ruflo gere a equipa.

**ESTADO REAL — PROVA PARCIAL:** **engine/ruflo_host.py** e **kind=ruflo-host** já criam swarm efémero, 2–4 papéis, 2–8 tarefas, até dois trabalhos Ferrari/REA paralelos, registo de conclusão, relatório, shutdown e limpeza. [VPS #42216565299](https://github.com/martaxi-boss/VPS/actions/runs/42216565299) e [Skill→ZIP #42218479317](https://github.com/martaxi-boss/VPS/actions/runs/42218479317) PASS **somente no modo assistido pela IA anfitriã**. O relatório de execução possui **independent_agent_model_calls=0**: não foi demonstrado raciocínio autónomo por subagente. **agent_spawn** e **model=inherit** registam papéis, não provam agentes inteligentes. É proibido confundir esta prova com a implementação completa.

**PORTA DE ACEITAÇÃO OBRIGATÓRIA — ATUALMENTE BLOQUEADA / NÃO CERTIFICADA:** não declarar **«Ferrari completo»**, **«equipa de subagentes operacional»**, **«100%»** ou equivalentes até existir prova ponta a ponta de: **A)** anfitrião ativo com controlo de trabalho e feedback; **B)** Ruflo a organizar subagentes que realmente executam trabalho, não só registos; **C)** cada agente desempenhar trabalho e tomar decisões contextualizadas pelo seu papel usando **raciocínio fornecido pela mesma IA anfitriã ChatGPT**, com registos de ação e resultados Ferrari individualizados; **D)** colaboração real entre agentes (partilha de resultados, revisão crítica e correção/replaneamento) e aceitação final pelo anfitrião; **E)** isolamento Ubuntu, sem fornecedor pago obrigatório, sem alterar outros projetos e sem daemons residuais; **F)** execução real GitHub Actions → VPS → relatório, ZIP, ficheiros e evidências individualizadas. **LIMITAÇÃO DE INTEGRAÇÃO:** a subscrição ChatGPT não é, só por existir, uma API/endereço invocável pela VPS ou pelo Ruflo. A ligação de ida-e-volta anfitrião ChatGPT ↔ tarefas/estados Ruflo precisa de um mecanismo suportado, autorizado e demonstrado em produção, que permita ao anfitrião realizar rondas de raciocínio por papel e devolver decisões aos agentes. O ciclo pode reutilizar **uma única IA anfitriã**, mas não pode fingir que os processos Ruflo chamam o modelo diretamente; **sem contratar APIs/fornecedores obrigatórios**. Não inventar endpoints, sessões, agentes inteligentes, créditos ou assinaturas.

**ESTADOS DISTINTOS:** a **instalação principal** passou em [#42318822376](https://github.com/martaxi-boss/VPS/actions/runs/42318822376); o **modo Ruflo assistido por um anfitrião com revisões reais** passou em #42325589374 e #42326357951. A **inteligência automática e autonomia dos subagentes fora da sessão do anfitrião continuam PENDENTES / NÃO CERTIFICADAS**. É obrigatório distinguir estas provas; nenhum PASS técnico autoriza chamar completa à autonomia.

**FONTE DE VERDADE OBRIGATÓRIA PARA TODAS AS RESPOSTAS/ALTERAÇÕES:** ler primeiro ESTE **BOOTSTRAP.md** na branch principal do repositório **martaxi-boss/skill-universal**; depois confirmar a realidade no código **engine/skill_job.py**, **engine/ruflo_host.py**, **engine/orchestrator.py**, no **engine/catalog.json** e nas provas de GitHub Actions/VPS. Os documentos de docs/ são históricos e datados; referências portáteis e Skills instaladas podem estar desatualizadas. Não importar hierarquias de outros projetos nem completar lacunas com suposições. Quando houver divergência, assinalar e corrigir, sem inventar trabalho executado. **Nenhuma hierarquia, coordenador ou componente de outro projeto integra este contrato Ferrari.**

**Ponto 8 — Ruflo assistido REAL na VPS (07/11, produção certificada):** `engine/agent_team.py`/`kind=ruflo-team` implementa papéis, tarefas dependentes, permissões do catálogo único, journal privado, rondas da mesma IA anfitriã, revisão por outro papel, SHA-256 e correção/retoma. Release ativa `e0509d5370828869479069c99f2eace779960cad`; fallback `205c6f0e970259c79fa2111b6670c2fe1672fb27`. [VPS #42325589374](https://github.com/martaxi-boss/VPS/actions/runs/42325589374) PASS: 4 agentes Ruflo MCP reais, 2 ferramentas jq, 3 revisões, hashes, 8/8 serviços; [ChatGPT→GitHub→VPS→ZIP #42326357951](https://github.com/martaxi-boss/VPS/actions/runs/42326357951) PASS: 3 tarefas aprovadas, `completed`. validador pinado atualizado e verificado pelo transporte. **Rondas guiadas pelo ChatGPT, zero chamadas LLM automáticas na VPS; autonomia externa NÃO certificada.** [Contrato e provas](docs/RUFLO_HOST_TEAM_ROUNDS_20261107.md).

**07/11/2026 — INSTALAÇÃO PRINCIPAL FERRARI FECHADA E CERTIFICADA NA VPS (NÃO é fecho funcional da equipa de agentes).** Um só `engine/catalog.json`: **173 programas, 272 funções (220 REA), 3 dependências, 2 fornecedores = 450 registos**. Ativo `205c6f0e970259c79fa2111b6670c2fe1672fb27`, fallback `7bf6dcecf15da26502c5969b5eee54d5e116fc32`; [ativação #42314959728](https://github.com/martaxi-boss/VPS/actions/runs/42314959728) PASS; [higiene #42315724016](https://github.com/martaxi-boss/VPS/actions/runs/42315724016) removeu a release 394 (2 433 024 bytes); [inventário anterior #42297678715](https://github.com/martaxi-boss/VPS/actions/runs/42297678715). **[Aceitação final #42318822376](https://github.com/martaxi-boss/VPS/actions/runs/42318822376) PASS:** 55/55 selecionados, 40/40 ações, 69 programas detetados, zero dos 8 APT legados, zero manifestos antigos e 8/8 serviços. OBS privado 32.2.2 responde, mas gravação GUI não certificada; formatos opcionais PDAL e cobertura GUI exaustiva ficam fora do fecho da instalação. Skill instalada no ChatGPT requer atualização independente. [Relatório final](docs/INSTALACAO_FERRARI_FECHO_FINAL_20261107.md).

**Ponto 1 — OpenPencil (prova histórica de 06/11):** release `a266b25e06a9c8acf1fdc940d22b99070cd17ded` estava ativa naquela prova; [Skill→ZIP #42145727316](https://github.com/martaxi-boss/VPS/actions/runs/42145727316) FIG/SVG/HTML PASS. Cliente ChatGPT atualiza-se no fecho geral.

**Ponto 2 — ComfyUI CPU (06/11):** [PNG real #42149365272](https://github.com/martaxi-boss/VPS/actions/runs/42149365272) 256×256 PASS; [higiene #42149831403](https://github.com/martaxi-boss/VPS/actions/runs/42149831403) retirou TinySD incompatível. [Prova](docs/COMFYUI_PONTO2_CPU.md).

**Ponto 3 — faster-whisper CPU (06/11):** [ASR #42170510453](https://github.com/martaxi-boss/VPS/actions/runs/42170510453) áudio inglês 11 s → TXT/SRT/JSON PASS em 2,24 s, tiny MIT privado. [Prova](docs/FASTER_WHISPER_PONTO3_CPU.md).

**Ponto 4 — Ruflo (06/11):** CLI MIT 3.71 privado [#42186639714](https://github.com/martaxi-boss/VPS/actions/runs/42186639714) PASS; rota/memória local [#42187084139](https://github.com/martaxi-boss/VPS/actions/runs/42187084139) PASS, mas memória iniciou daemon; [auditoria #42187338181](https://github.com/martaxi-boss/VPS/actions/runs/42187338181) confirmou zero processos Ruflo ativos. **Subagentes inteligentes NÃO certificados; Ruflo é OBRIGATÓRIO na arquitetura-alvo de agentes e não constitui coordenador IA residente na VPS**. [Detalhes](docs/RUFLO_PONTO4_20261106.md).

**Histórico F7 (05/11):** releases `758e1b435317fa26277b332b75bc47c67910be81` (F7), `146145d5ada9c13e368df18727e4dbf4f5807664` (F6), `87969badbde0a77c2c181bb9605357d51a4a30c0` (histórico). Provas arquivadas em Git e docs.

**Fase 8 (05/11): CERTIFICADA 40/40 ações.** ADB Android físico testou instalar e remover APK sintética [#42128892714](https://github.com/martaxi-boss/VPS/actions/runs/42128892714) PASS, sem tocar em PINK. [Fecho F8](docs/FASE8_FECHO_20261105.md); sem APT global.

**Fase 9 / limpeza APT nominal — CONCLUÍDA na fotografia de 06/11:** [primeira remoção #42225950692](https://github.com/martaxi-boss/VPS/actions/runs/42225950692) eliminou oito aplicações globais. A [auditoria posterior #42299686585](https://github.com/martaxi-boss/VPS/actions/runs/42299686585) encontrou os outros oito APT **não instalados**, sem referências nos sete projetos e com 8/8 serviços ativos. [Confirmação independente #42300665770](https://github.com/martaxi-boss/VPS/actions/runs/42300665770): `dpkg -s` e `dpkg-query -W` concordam, **0/8 instalados**, sem purga executada. [Relatório](docs/FASE9_HIGIENE_APT_FINAL_20261106.md).

**F9 — testes reais PASS:** [QGIS #42304131087](https://github.com/martaxi-boss/VPS/actions/runs/42304131087), [LibreCAD #42311158545](https://github.com/martaxi-boss/VPS/actions/runs/42311158545), [OpenSCAD #42312047260](https://github.com/martaxi-boss/VPS/actions/runs/42312047260), [Blender #42312161892](https://github.com/martaxi-boss/VPS/actions/runs/42312161892). HDF5 privado e 2 plugins PDAL carregados [#42311620021](https://github.com/martaxi-boss/VPS/actions/runs/42311620021), mas formatos opcionais não certificados. APT nominal higienizado; GUI, áudio/vídeo e bibliotecas transitivas pendentes. [Provas](docs/FASE9_CAD3D_BLENDER_PDAL_SKILL_20261106.md).

**F11 — PDAL LAS funcional certificado:** [VPS #42317695882](https://github.com/martaxi-boss/VPS/actions/runs/42317695882) PASS: TXT→LAS→TXT, 5 pontos, cabeçalho LAS de 327 bytes e coordenadas revalidadas, 8/8 serviços. Não certifica HDF/Icebridge nem todos os formatos PDAL. [Relatório F11](docs/FASE11_PDAL_LAS_REAL_20261107.md).


**Ponto 7 — Ruflo assistido (prova parcial da equipa obrigatória):** [#42216565299](https://github.com/martaxi-boss/VPS/actions/runs/42216565299) registou dois papéis, duas tarefas e executou jq/REA privados; [Skill→ZIP #42218479317](https://github.com/martaxi-boss/VPS/actions/runs/42218479317) PASS na release anterior `f1f3b03525adec7018d7d629243e7b0fbb7f5087`. Inferência LLM autónoma não certificada; sem segundo coordenador. [Contrato](docs/RUFLO_SINGLE_HOST_CERT_20261106.md).

## 1. Decisão permanente — UMA ÚNICA SKILL

ChatGPT, Codex ou outra IA interpreta → Skill Universal Ferrari → GitHub autenticado → workflow exclusivo em martaxi-boss/VPS → SSH existente → Ferrari Ubuntu → executores privados → relatório e ZIP.

A seleção e execução das ferramentas pertencem ao Ferrari. O Ruflo é o **sub-anfitrião obrigatório da equipa na arquitetura final**, não um segundo motor ou coordenador residente; a porta de aceitação no topo deste BOOTSTRAP continua vinculativa. Não adicionar coordenadores ou Skills paralelas, não reescrever a ponte SSH, não partilhar diretórios, fornecedores ou dependências com outros projetos. O diretório Ferrari tem exatamente o nome do repositório GitHub: **/srv/projects/skill-universal/**.

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

1. **BLOQUEIO FUNCIONAL DA EQUIPA:** implementar e provar o circuito anfitrião → Ruflo sub-anfitrião → subagentes com raciocínio por papel partilhando uma IA anfitriã → colaboração real → ferramentas Ferrari/REA → revisão e entrega. Estado: **OBRIGATÓRIO, NÃO CERTIFICADO**; papéis registados não bastam.
2. **Sincronia de estado:** aferir por pedido de inventário somente de leitura a release realmente ativa, número atual de ações e executores privados; comparar com GitHub e com o pin do validador.
3. **Entrega da única Skill:** atualizar e validar SKILL.md e referências portáteis; empacotar skill.zip; verificar separadamente se a versão nova foi instalada no ChatGPT. Repo atualizado não prova cliente atualizado.
4. **Higienização segura:** classificar binários, venvs, APT globais, fornecedores e resíduos por propriedade; eliminar apenas ficheiros exclusivos com prova e rollback, sem mexer em projetos alheios.
5. **Capacidades restantes:** adicionar adaptadores tipados ao Ferrari existente por necessidade real, provar em CI, VPS e pedido Skill→GitHub→VPS→ZIP. Não criar camadas nem fornecedores pagos obrigatórios.
6. **Ausência de legado:** depois da remoção dos REAs antigos, confirmar que rotinas e documentação não os referenciam como instalações ativas; preservar o REA privado.

Não declarar cobertura universal de todas as tarefas, fornecedores e formatos sem testes ponta a ponta.

## 6. Execução, segurança e recuperação

- Os tipos implementados no executor são **inventory, operation, invoke, auto, plan, rea-mcp e ruflo-host**; a Skill instalada no ChatGPT pode continuar desatualizada. Consultar [references/github-bridge.md](skill/motor-universal-linux/references/github-bridge.md) antes de emitir um pedido.
- Criar apenas JSON de pedido novo, sem segredos ou dados pessoais em repositório público; base64 não é encriptação. Identificar run pelo commit correspondente e exigir response.zip, report.json, status completed e ficheiros reais.
- Na VPS, usar o Ferrari e SSH existentes, sem comandos arbitrários enviados em pedidos e sem instalar fora de /srv/projects/skill-universal. O workflow manual de deploy não deve repetir instalações existentes por defeito.
- Preservar sempre checkpoints e fallback antes de qualquer alteração com impacto operacional.
- Relatórios antigos em [docs/](docs/) permanecem evidência histórica. Este BOOTSTRAP, o código e os runs atuais governam o presente.
