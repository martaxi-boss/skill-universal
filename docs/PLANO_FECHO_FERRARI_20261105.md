# Ferrari — plano de fecho do motor universal e isolamento total por projeto

**Preparado em 05/11/2026; Fase 5 certificada no próprio dia.** Este documento detalha as **próximas fases 5–10** após os pontos 2 (40 ações tipadas privadas), 3 (certificação por domínio) e 4 (Skill empacotada/ponte testada). Não constitui autorização para operações destrutivas cegas nem prova de deploy; usar o [BOOTSTRAP](../BOOTSTRAP.md) e as execuções reais como fonte de estado.

## Contrato obrigatório, sem exceções de aplicação

1. Um repositório GitHub corresponde a **um diretório de projeto com exatamente o mesmo nome**, por exemplo `martaxi-boss/skill-universal` → `/srv/projects/skill-universal/`. Projetos não partilham diretórios de aplicações, runtimes, caches, credenciais, dados, bibliotecas de aplicação nem fornecedores.
2. Todos os executáveis, bibliotecas específicas, ambientes Python/npm, extensões, modelos, artefactos, staging e temporários **que pertençam ao Ferrari** ficam em `/srv/projects/skill-universal/`. Nenhuma instalação global APT/Snap/npm/pip a favor do Ferrari. Sem fallback silencioso ao `PATH` ou `/usr/bin`; programa privado ausente devolve erro explícito.
3. Ubuntu 24.04 fornece necessariamente kernel, loader e bibliotecas essenciais do SO. Usar estes elementos fundamentais do SO não autoriza a instalar aplicações do Ferrari globalmente. As integrações inevitáveis de serviços (por exemplo registo systemd, Nginx ou PM2, se já existirem) devem ser inventariadas e desfeitas na desinstalação **sem alterar dados de outros projetos**.
4. Ordem executiva: **ChatGPT/Skill única → GitHub autenticado → GitHub Actions e SSH existente → Ferrari → relatório + response.zip**. A ponte continua **transporte**, sem regras, coordenador nem instalação de aplicação. Sem coordenador na VPS; Supervisor passivo só notifica. Ruflo/Prefect não substituem o orquestrador próprio.
5. Cada fase começa com baseline e revisão de consumidores e só termina com **CI PASS + execução VPS real PASS + evidência de saída + higiene Ferrari-only + pós-teste de outros serviços**. Conservar rollback e não adicionar novas camadas.
6. Nunca remover aplicações do Ubuntu, diretórios ou PM2 de outros projetos por parecerem duplicados. Para um pacote global, documentar **quem o instalou, quais processos/serviços o usam e quem ficaria afetado**. Se pertencer apenas ao Ferrari, migrar consumidores Ferrari para o privado, testar, remover o pacote global com rollback e voltar a testar. Se algum outro projeto ainda o usa, isolar primeiro esse projeto; só remover a cópia global após confirmar zero consumidores.

## Linha de base histórica antes da ativação em 05/11

- Motor em produção **última confirmação explícita:** release `87969badbde0a77c2c181bb9605357d51a4a30c0` em `current` na auditoria VPS [#42044862915](https://github.com/martaxi-boss/VPS/actions/runs/42044862915), 14:25 UTC. Não há prova de ativação posterior; verificar de novo antes de mudar.
- Candidato isolado em PR [#64](https://github.com/martaxi-boss/skill-universal/pull/64), SHA `eb2398c0b52b71f24abd39acdefbc67d3d13ff12`, CI [#42055880677](https://github.com/martaxi-boss/skill-universal/actions/runs/42055880677) **SUCCESS**, mas **sem confirmação de deploy/merge**.
- Último inventário executado via Skill [VPS #42058163720](https://github.com/martaxi-boss/VPS/actions/runs/42058163720), **SUCCESS**: **40 ações invocáveis**, **83/108 programas detetados**, **55/56 candidatos** (Penpot ausente). Presença/invocabilidade não certifica todas as funcionalidades.
- **16 entradas da seleção de 56 ainda detetadas em caminhos globais**: `libreoffice`, `ansible`, `ytdlp`, `gimp`, `blender`, `kdenlive`, `darktable`, `openscad`, `librecad`, `qgis`, `audacity`, `obs`, `solvespace`, `synfig`, `openshot`, `calibre`. O inventário *prioriza deteção global em alguns casos*, apesar de existirem ferramentas privadas; corrigir descoberta e provar os executáveis realmente utilizados, não deduzir por `command -v`.
- Outras 16 entradas auxiliares globais, fora da seleção de 56, aparecem como `installed_unintegrated` (Git, Python, pip, venv, Node, npm, GCC, Make, cliente PostgreSQL, curl, wget, unzip, zip, Java, GDB, strace). Classificar cada uma como **componente SO/administrativo**, **outro projeto**, **Ferrari** ou **sem consumidor** antes de qualquer limpeza. Não apagar o Ubuntu base.
- O proprietário comprovou execução manual com caminhos privados de **Blender 4.5.15 LTS/OpenSCAD** (STL, BLEND, GLB, PNG) e **LibreOffice 24.2.7.2** (DOCX→PDF), em 05/11. [CAD](CAD_PRIVADO_TESTE_MANUAL_20261105.md) e [LibreOffice](CERTIFICACAO_LIBREOFFICE_PRIVADO_20261105.md). `javaldx` continua sem certificação Java; não bloqueou PDF.
- Ruflo está no npm privado Ferrari, detetado como **instalado sem ação tipada**, mas funções multiagente, fornecedor de modelo e persistência **não certificados**. O instalador fixa `ruflo@3.71.0`; essa versão requer leitura real do manifest no host antes de declarar que é a instalada. O DAG nativo Ferrari já tem provas de execução.

## Fase 5 — CERTIFICADA (PASS, 05/11/2026)

**Prova de fecho:** [certificado operacional](CERTIFICACAO_FASE5_20261105.md), com CI Ferrari [#42068518899](https://github.com/martaxi-boss/skill-universal/actions/runs/42068518899) e [#42068530678](https://github.com/martaxi-boss/skill-universal/actions/runs/42068530678), precheck VPS [#42066226440](https://github.com/martaxi-boss/VPS/actions/runs/42066226440), ativação real [#42066363098](https://github.com/martaxi-boss/VPS/actions/runs/42066363098), Skill→ZIP [#42066521890](https://github.com/martaxi-boss/VPS/actions/runs/42066521890), fault-injection do rollback em cópia privada na VPS [#42068780199](https://github.com/martaxi-boss/VPS/actions/runs/42068780199) e auditoria de saúde [#42066853562](https://github.com/martaxi-boss/VPS/actions/runs/42066853562), todos **PASS/SUCCESS**. Release ativa `40c0e1cdf31b1fe9589ad8be90e5eac06eec2856`; fallback `87969badbde0a77c2c181bb9605357d51a4a30c0`. Rollback ensaiado **numa cópia**, sem introduzir falha na produção. Fase 6 ainda não iniciada.

## Fase 5 — procedimento executado (histórico)

**Trabalho:** ler `current` e fallback por execução GitHub Actions **somente de leitura**; comparar SHA, `main`, PR #64, a Skill portátil e os executáveis reais. Executar `install/vps-isolated-release.sh` com `--check` na VPS através de um **caminho autorizado do workflow existente**, sem pedir comandos ConnectBot ao proprietário. O script candidato verifica o código, 40 ações, CAD 3D, Office e um `response.zip`; corrigir qualquer incompatibilidade antes de mudar `current`. Usar a forma de deploy autenticada existente, sem alterar fingerprint/credenciais nem enfiar comandos genéricos de root na ponte.

**Ativar só após o check PASS**, guardar o symlink anterior e o fallback; executar também pós-teste pela Skill→VPS→ZIP. **Higiene da fase:** eliminar apenas staging e temporários próprios Ferrari, e antigos artefactos versionados comprovadamente descartáveis, depois de preservar fallback; nada global.

**Fechada quando:** novo SHA em `current` lido diretamente da VPS; `FERRARI_PRIVATE_ACTIVE_RELEASE=PASS`, 40/40 caminhos privados, STL/BLEND/GLB/PNG/PDF real, `report.json.status=completed` e resposta ZIP; rollback real testado; serviços dos outros projetos inalterados.

## Fase 6 — independência física integral dos executáveis e dependências

**Fase 6 CERTIFICADA — PASS no âmbito Ferrari (05/11/2026).** [Certificado e provas](CERTIFICACAO_FASE6_20261105.md). [CI Ferrari #42091895647](https://github.com/martaxi-boss/skill-universal/actions/runs/42091895647) **255 testes PASS**; [VPS #42088052659, tentativa 3](https://github.com/martaxi-boss/VPS/actions/runs/42088052659): **315 441 entradas privadas, 436 symlinks, zero externos, zero quebrados, zero Python global**; **40/40 ações**, **7/7 venvs privados**, **47/56** candidatos detetados. Higiene comprovada: [releases antigas #42087599243](https://github.com/martaxi-boss/VPS/actions/runs/42087599243), [Python privado #42089823880](https://github.com/martaxi-boss/VPS/actions/runs/42089823880), [quatro launchers e 13 links antigos #42092331962](https://github.com/martaxi-boss/VPS/actions/runs/42092331962). [Skill/ZIP #42092496058](https://github.com/martaxi-boss/VPS/actions/runs/42092496058) e [saúde #42092526699](https://github.com/martaxi-boss/VPS/actions/runs/42092526699) PASS. Os **16 pacotes APT globais continuam no Ubuntu**, sem uso como executores Ferrari; atribuição/limpeza transversal fica na Fase 9 após prova de consumidores. Nove candidatos de capacidade ainda não estão privados (Fase 8).

**Trabalho:** rever **todas** as operações base, 40 ações tipadas, runtimes Python/Node/Java, instaladores legados, subprocessos, bibliotecas dinâmicas e invocações indiretas. Corrigir a deteção que ainda aponta para 16 caminhos globais; utilizar versões privadas compatíveis dentro de `tools/`, `runtimes/`, `.runtime/`, ou bloquear capacidades sem executor privado. Verificar `realpath`, `ldd`/bibliotecas de aplicação, shebangs, `PATH`, `LD_LIBRARY_PATH`, caches e symlinks, impedindo sair do projeto. Aplicações com integração OS essencial ou específica de hardware devem indicar a dependência claramente.

**Higiene da fase:** para cada pacote global que se conclua ser **exclusivamente residual do Ferrari**, comprovar consumidores nulos e remover pelo procedimento adequado, medindo diferença de espaço e fazendo verificação pós-operação. Itens de outro projeto só serão alterados após migração **independente desse projeto**, jamais como efeito lateral do Ferrari. Eliminar ficheiros Ferrari dispersos, atalhos mortos, scripts temporários e configurações exclusivas fora da pasta, sem apagar componentes do SO.

**Fechada quando:** relatório exaustivo dos executores **realmente chamados**, zero dependências de aplicação Ferrari fora de `/srv/projects/skill-universal/`; nenhum fallback global; zero ficheiros Ferrari órfãos; sem regressões nos outros serviços. Itens globais legitimamente comuns são classificados como SO/outros projetos, não declarados falsamente privados.

## Fase 7 — automação profissional e papel do Ruflo

**CERTIFICADA no âmbito DAG privado (05/11/2026)** — [certificado F7](CERTIFICACAO_FASE7_20261105.md). [CI #42097832176](https://github.com/martaxi-boss/skill-universal/actions/runs/42097832176): **274 testes PASS**. [Ativação VPS #42098645092](https://github.com/martaxi-boss/VPS/actions/runs/42098645092): release `758e1b435317fa26277b332b75bc47c67910be81`, fallback F6 preservado. [DAG #42098800995](https://github.com/martaxi-boss/VPS/actions/runs/42098800995): checkpoint, retoma em segundo processo sem repetição, ondas paralelas, `ruflo@3.71.0` CLI local opcional. [Skill→ZIP #42099036932](https://github.com/martaxi-boss/VPS/actions/runs/42099036932) PASS. [Saúde #42099108182](https://github.com/martaxi-boss/VPS/actions/runs/42099108182) PASS. **Hard quotas CPU/RAM ainda sem prova**; eliminação segura da pasta do projeto exige auditoria transversal e ensaio não destrutivo (F9–F10).

**Trabalho:** manter **um único orquestrador Ferrari** (`engine/orchestrator.py`; DAG até 24 etapas, paralelismo até 4). Certificar isolamento de jobs, propagação de erros, cancelamento, quotas/limites de CPU/RAM/tempo, idempotência, logs e retoma após interrupção. Se for necessária recorrência, agendamento/monitorização ficam dentro do Ferrari e da infraestrutura autorizada, sem iniciar coordenador ou daemon adicional global.

**Ruflo:** validar a versão exata e a integridade do npm privado, executar um caso **real** de agentes com modelo/fornecedor gratuito ou já legitimamente autorizado, medir logs, memória e resultados. Só acrescentar adaptador tipado quando houver utilidade; se exigir fornecedor ou arquitetura incompatível, classificar `OPCIONAL_NAO_CERTIFICADO` sem bloquear o orquestrador. Prefect igualmente opcional e não concorrente. **Higiene:** remover só testes/artefactos Ruflo Ferrari desnecessários, nunca pacotes de outros projetos.

**Fechada quando:** DAG completo e reprise persistente demonstrados na VPS com ZIP; Ruflo classificado de forma factual (integrado/certificado ou opcional bloqueado com causa); nenhum segundo coordenador nem assinatura paga obrigatória.

## Fase 8 — completar cobertura funcional por necessidades reais

**Trabalho:** relacionar as capacidades originais — web/full-stack, apps, imagem, vídeo, áudio, Office/OCR, CAD/BIM/IFC/3D, cartografia, dados, segurança/engenharia reversa legítima, automação — com **um caso real representativo**, entrada e saída. Reaproveitar as certificações do Ponto 3 sem as repetir desnecessariamente. Para ferramentas detetadas mas `installed_unintegrated`, decidir se precisam de adaptação ou se são dependências indiretas; não inflacionar contagens. REA tem 229 nomes MCP mas não 229 operações certificadas; continuar cobertura prioritária dos fornecedores quando fizer sentido.

**Limites explícitos não escondidos:** Penpot ausente; ComfyUI CPU sem modelos certificados; Hopper demo sem licença comercial; GUI interativa total, GPU e ADB físico ainda sem prova. Integrar apenas quando for compatível e houver recursos/licença; não prometer cobertura absoluta de hardware/fornecedores indisponíveis. **Higiene após cada grupo:** apagar dependências/protótipos abandonados pertencentes ao Ferrari e guardar provas GitHub Actions/VPS/ZIP.

**Fechada quando:** matriz domínio→operação→executável privado→resultado real→limite publicado; nenhum botão falso ou capacidade anunciada que não funcione.

## Fase 9 — auditoria, alinhamento GitHub/VPS e higienização de toda a VPS

**Trabalho:** inventariar diretórios de projetos e a correspondência GitHub/repositório, owners, dependências, processos/PM2, systemd, Nginx, containers, caches, symlinks, portas, agendamentos e dados. Em cada instalação com repositório, o nome da pasta deve coincidir com o repositório. Encontrar ficheiros/pacotes soltos e determinar a propriedade. Os programas e dependências específicas de cada projeto devem permanecer **unicamente dentro desse projeto**; sem partilhas cruzadas.

**Higiene:** migrar item a item os recursos atribuídos e ainda em uso, confirmar o arranque independente, remover resíduos órfãos e registar espaço libertado. Não executar `apt purge` em lote, `rm -rf` sobre pastas não identificadas, desinstalar Ubuntu base, eliminar dados/secrets/credenciais, nem afetar os robôs Telegram, PINK, FADEGO, Low Cost Europa ou Project Leader. Componentes de serviços de base são marcados como integrações do SO com propriedade e remoção explícitas, não fingir que não existem.

**Fechada quando:** matriz GitHub ↔ diretório ↔ serviço ↔ recursos ↔ proprietário ↔ teste de saúde para **cada projeto existente**, sem instalações específicas soltas, sem recursos órfãos não classificados, e pós-teste comprovando que os projetos continuam operacionais.

## Fase 10 — certificação final, Skill e desinstalação reversível

**Trabalho:** merge apenas do código certificado para `main`; sincronizar a **mesma** Skill Universal, empacotar `skill.zip` e verificar a versão instalada no cliente ChatGPT (não confundir CI/repositório com instalação na interface). Certificar vários pedidos desde o ChatGPT por GitHub Actions→SSH existente→Ferrari→ZIP, com relatórios e dados reais, erros reais e rollback comprovado.

**Ensaio de desinstalação NÃO destrutivo:** em cópia ou ambiente isolado, identificar/remover artefactos Ferrari e confirmar que não deixa dependências de aplicação fora do seu diretório, nem rompe os outros projetos. Na VPS real, não apagar o Ferrari ativo para demonstrar a capacidade de remoção. Registar exacto inventário de entradas/saídas e procedimento de uninstall reproduzível; remover hooks de serviços do Ferrari se existirem, mantendo Ubuntu e terceiros.

**Fechada quando:** Skill atual única instalada/verificada; toda a matriz de testes e isolamento verde; instalação/atualização/rollback/desinstalação ensaiada com evidências; higiene final concluída sem afetar outros projetos; BOOTSTRAP e documentação alinhados com SHA de produção e IDs de Actions.

## Regras executivas para evitar repetição de ConnectBot

- O proprietário dá ordens **aqui no ChatGPT**. A execução usa o GitHub autenticado e workflows existentes; não lhe pedir para colar blocos no telemóvel por rotina.
- O workflow existente `ferrari-skill-request.yml` aceita apenas os tipos `inventory`, `operation`, `invoke`, `auto`, `plan` e `rea-mcp`; **não** é um executor administrativo genérico. Para deploy/limpeza, usar um caminho autorizado de administração GitHub Actions, com revisão, âmbito mínimo, registo e rollback, mantendo o SSH existente intocado. Se não houver tal caminho autorizado ou a ferramenta bloquear, não improvisar SSH nem anunciar conclusão.
- Em cada fase: inventário → ação mínima → testes reais → limpeza do próprio projeto → reauditoria → atualizar BOOTSTRAP e anexar run IDs. Não abrir novas Skills, camadas, pontes ou orquestradores.

## Estado resumido

- **Confirmado:** instalação funcional e CI do Ferrari; 40 ações; DAG e provas reais em múltiplos domínios; Skill→GitHub→VPS→ZIP; Blender/OpenSCAD/LibreOffice privados testados pelo proprietário; higienização Ferrari anterior e caches VPS auditados.
- **Fase 6 Ferrari concluída e certificada:** executores e runtimes de aplicação isolados na própria pasta, sem fallback global; GitHub/VPS e fallback alinhados. **Seguintes tarefas, ainda não iniciadas:** automação/Ruflo (Fase 7), capacidades não integradas (Fase 8), atribuição e eventual remoção segura dos 16 APT globais e restante VPS (Fase 9), merge/Skill cliente/ensaio de uninstall (Fase 10).
- **Não declarar 10/10 por antecedência:** só depois dos critérios objetivos das fases 5–10.
