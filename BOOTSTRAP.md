# BOOTSTRAP — Motor Ferrari / Skill Universal Ubuntu

**Estado de referência: 05/11/2026 UTC.** Fonte canónica do estado e dos limites; números e versões têm de ser associados à execução que os mediu. O histórico detalhado continua nos relatórios de docs/ e no Git. O resultado de CI não substitui um teste operacional na VPS.

## 1. Decisão permanente — UMA ÚNICA SKILL

ChatGPT, Codex ou outra IA interpreta → Skill Universal Ferrari → GitHub autenticado → workflow exclusivo em martaxi-boss/VPS → SSH existente → Ferrari Ubuntu → executores privados → relatório e ZIP.

A lógica, seleção e orquestração pertencem ao Ferrari. Não adicionar coordenadores ou Skills paralelas, não reescrever a ponte SSH, não partilhar diretórios, fornecedores ou dependências com PINK IPTV, Engenharia Reversa antiga, Project Leader, Telegram, FADEGO ou Low Cost Europa. O diretório Ferrari tem exatamente o nome do repositório GitHub: **/srv/projects/skill-universal/**.

## 2. Fotografia atual com provas

| Elemento | Prova e âmbito |
|---|---|
| Última alteração funcional do motor | **commit b2869e334d9d68a0c988905e71ce0badec6ba359** (antes da atualização documental); CI [#41922781312](https://github.com/martaxi-boss/skill-universal/actions/runs/41922781312) SUCCESS. Inclui integração do Hopper privado |
| **Release ativa comprovada em 05/11** | **047885627e33bfc82f23ef8ee639612d3aab38eb**, ativada em `/srv/projects/skill-universal/current` por [VPS #42011202485](https://github.com/martaxi-boss/VPS/actions/runs/42011202485) após teste real Vite/Playwright PASS. Código apenas dentro de `releases/`, nenhuma instalação APT/global na VPS; release anterior 0ea4b90747b7cd67cffcbee5f1e350b552e1bf0d preservada |
| **Auditoria do isolamento — ponto 2 (05/11)** | [VPS #42011202485](https://github.com/martaxi-boss/VPS/actions/runs/42011202485) examinou 46 208 entradas (até à profundidade configurada), sem symlink para outro projeto, sem atalho legado. **40 ações: 8 executáveis privados; 32 resolvem para binários/intérpretes do sistema**, incluindo Python de venvs. **Isolamento TOTAL não certificado**. Vite/Playwright passaram com HOME/TMPDIR/XDG dentro do projeto. Correções de código e testes [CI #42010826629](https://github.com/martaxi-boss/skill-universal/actions/runs/42010826629) SUCCESS. O workflow de transporte temporário foi removido/restaurado após o teste |
| **Inventário depois da correção — 05/11** | [VPS #42011461022](https://github.com/martaxi-boss/VPS/actions/runs/42011461022): 55/56 candidatos detetados, 40 ações; OpenCV identificado numa venv Docling **privada Ferrari**, sem depender da instalação global de Python para a sua deteção. Penpot continua ausente; `report.json` completed e ZIP PASS |
| **Verificação real da Skill web** | [VPS #41994937194](https://github.com/martaxi-boss/VPS/actions/runs/41994937194): pedido novo `kind=operation`, `vite-build`, Playwright real, `report.json` completed, `response.zip` com browser-check.json, capturas desktop/móvel e HTML: **FERRARI_SKILL_END_TO_END=PASS**. Workflow temporário retirado e workflow de entrega original restaurado byte a byte |
| Transporte por GitHub Actions | O workflow Ferrari no repositório VPS continua **pinado em 292aeb7d10eecef8c3ca84760cd579e84e4b97f3 para seleção/validação do pedido**. Não confundir o pin com o HEAD do motor nem mudar o workflow/SSH sem ordem específica |
| Funcionamento ponta a ponta | [#41981152670](https://github.com/martaxi-boss/VPS/actions/runs/41981152670), de 05/11: pedido real **kind=rea-mcp**, status completed, executor privado e ZIP; FERRARI_SKILL_END_TO_END=PASS |
| Última execução consultada | [#41981478159](https://github.com/martaxi-boss/VPS/actions/runs/41981478159): sucesso de higiene de pedidos, **sem executar motor nem produzir ZIP**; não é uma certificação adicional |
| REA próprio do Ferrari | **rea-agents@6.8.0**, instalado em .runtime/npm/rea, catálogo com **229 nomes MCP**. Catálogo não significa 229 ferramentas certificadas. Chamada ELF real [#41717389118](https://github.com/martaxi-boss/VPS/actions/runs/41717389118) e cenário [#41718385142](https://github.com/martaxi-boss/VPS/actions/runs/41718385142) PASS |
| Hopper privado | **Hopper 6.6.1**, pacote oficial validado e binário isolado em tools/hopper-6.6.1; origem [#41921893982](https://github.com/martaxi-boss/VPS/actions/runs/41921893982), doctor REA [#41922087539](https://github.com/martaxi-boss/VPS/actions/runs/41922087539) PASS. **Versão demo**, sem licença comercial nem certificação de todas as funções |
| Ferramentas Android | Apktool **3.0.3**; AAPT2, Apksigner, Zipalign, ADB dentro de tools/android-cli-36.0.0, APK sintético testado [#41854398886](https://github.com/martaxi-boss/VPS/actions/runs/41854398886). ADB sem dispositivo físico certificado |
| Ações tipadas | Última contagem operacional publicada: **40 ações** [#41854771565](https://github.com/martaxi-boss/VPS/actions/runs/41854771565), em 04/11. Inventário novo em 05/11 confirma as 40 como disponíveis para invocação |
| Inventário real 05/11 | [#41991752006](https://github.com/martaxi-boss/VPS/actions/runs/41991752006): **55 de 56 candidatos Ubuntu detetados**, 40 ações registadas e invocáveis, ZIP com `inventory.json` e `report.json` completed. Único candidato não detetado: Penpot; deteção não implica certificação funcional |
| REAs legados | **REA FINAL e Trial removidos da VPS**; ausência verificada [#41840478411](https://github.com/martaxi-boss/VPS/actions/runs/41840478411). O REA privado do Ferrari permanece e não deve ser apagado |
| Atalho legado | Após a migração dos launchers, **/home/ubuntu/.local/share/motor-ferrari deixou de ser um symlink de trabalho**. O caminho canónico é /srv/projects/skill-universal. O código correspondente foi integrado no merge 292aeb7d; verificar novamente na VPS antes de qualquer nova remoção |

**Base histórica que continua válida enquanto evidência daquela data, não como estado atual:** [#41716562469](https://github.com/martaxi-boss/VPS/actions/runs/41716562469) (164 testes), [#41672372249](https://github.com/martaxi-boss/VPS/actions/runs/41672372249) (inventário inicial), [#41786521407](https://github.com/martaxi-boss/VPS/actions/runs/41786521407) (197 testes, release histórica 0a1a4c..., 35 ações). Inventários anteriores registaram 81 programas detetados e 55/56 candidatos Ubuntu. Nenhuma destas contagens certifica 81 programas funcionais.

## 3. Estrutura e independência física

- **/srv/projects/skill-universal/current**: ligação para a release ativa dentro de releases/. A SHA efetivamente ativa deve ser confirmada num inventário real, não inferida a partir do HEAD do GitHub.
- **.runtime/**: ambientes Python, npm, caches, resultados, pedidos e dados do motor, exclusivamente Ferrari.
- **runtimes/**: Node 22.23.4 e Java 25.0.5 privados.
- **tools/**: Ghidra 12.2, JADX 1.5.6, Apktool 3.0.3, fornecedores privados Ghidra/JADX do REA, Android CLI, Hopper 6.6.1 e outros executores verificados.
- **releases/**: versões do motor; preservar release atual e fallback, sem deletar em lote.
- A auditoria [#42011202485](https://github.com/martaxi-boss/VPS/actions/runs/42011202485) confirmou **32 de 40 ações a resolver executáveis/intérpretes fora da pasta Ferrari**. Isso inclui programas APT em `/usr/bin` e duas ações DuckDB/Polars com Python de venvs ligado ao intérprete do Ubuntu. Não confundir zero symlinks entre projetos com isolamento físico total.
- Para cumprir o requisito estrito do proprietário, é necessário migrar/empacotar os executáveis e dependências de terceiros dentro de `tools/` e `.runtime/` **sem perder as 40 ações**; testar individualmente antes de abandonar os caminhos do sistema. Não reinstalar globalmente, não apagar pacotes partilhados nem criar outro motor.

**NÃO autorizar** eliminação de diretórios, dependências, versões fallback, dados, serviços ou pacotes de outros projetos por semelhança de nomes. Duplicação de dependências privadas entre projetos pode ser intencional para garantir isolamento.

## 4. Capacidades e limites observados

**Certificadas em casos concretos:** Calibre EPUB, Darktable TIFF, GIMP XCF, Krita PNG, Scribus PDF/SLA (fase 2), LMMS WAV audível (fase 3) e ferramentas de dados/documentos anteriores. Testes reais pela Skill registados no [plano faseado](docs/PLANO_INTEGRACAO_55_PROGRAMAS_20261103.md). REA MCP executou várias chamadas tipadas (ELF, Apktool, captura de processo e doctor), sem demonstrar integralmente as 229 ferramentas.

**Vídeo certificado em caso real:** MLT/Kdenlive → MP4 pela Skill [#41992064762](https://github.com/martaxi-boss/VPS/actions/runs/41992064762), com `response.zip`, MP4 H.264 320×180, 2,005 s, codec áudio AAC e validação `ffprobe`. O teste prova uma composição MLT sintética, não todos os projetos de edição profissional.

**Pendentes de prova de produto final:** aplicações GUI totalmente interativas; ComfyUI CPU sem modelos; Penpot sem Docker operacional; dispositivo físico para ADB; funções pagas da demonstração do Hopper. O branch PR [#43](https://github.com/martaxi-boss/skill-universal/pull/43) permanece aberto e deve ser reavaliado contra as funções Calibre/Darktable já certificadas antes de qualquer merge.

**Ponte pinada:** o validador histórico rejeita kind=invoke de alguns IDs Android introduzidos depois. kind=auto com Zipalign devolveu ZIP real [#41856969562](https://github.com/martaxi-boss/VPS/actions/runs/41856969562). Não corrigir por alterações silenciosas da ligação SSH.

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
