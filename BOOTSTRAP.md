# BOOTSTRAP — Motor Ferrari / Skill Universal Ubuntu

**Estado operacional de referência: 04/11/2026 (UTC).** Este documento é o ponto de entrada atual. Provas antigas e fases substituídas continuam acessíveis no histórico Git e nos relatórios de docs/, mas não são o estado presente. Não promover uma previsão ou um catálogo a certificação.

## 1. Decisão permanente — UMA ÚNICA SKILL

ChatGPT, Codex ou outra IA interpreta o pedido → UMA ÚNICA SKILL UNIVERSAL Ferrari → conector GitHub autenticado → workflow exclusivo Ferrari no repositório martaxi-boss/VPS → SSH existente → Motor Ferrari Ubuntu → orquestrador e ferramentas instaladas → relatório e ZIP.

O motor decide a ferramenta e executa as operações; a IA orienta. O Ferrari tem instalação e runtime próprios, sem coordenador na VPS de outro projeto. Não misturar com Project Leader, Engenharia Reversa antiga, Telegram, FADEGO, PINK IPTV ou outros projetos. Não adicionar Skills, camadas ou pontes paralelas.

**Objetivo:** cobertura progressiva em CONSTRUÇÃO, CAD, BIM/IFC, plantas, 3D, web, software, aplicações, gráficos, vídeo, áudio, documentos, PDF, OCR, dados, mapas, automação e engenharia reversa. Universal descreve a ambição, não significa que todos os domínios estejam certificados.

## 2. Fotografia atual com provas

**Plano faseado dos programas instalados:** [PLANO_INTEGRACAO_55_PROGRAMAS_20261103.md](docs/PLANO_INTEGRACAO_55_PROGRAMAS_20261103.md). O plano acompanha todos os 55 programas inicialmente detetados sem ação direta, por fases e com distinção entre código, instalação e testes reais. Não confundir seleção com certificação.

**Última certificação real do motor:** [deploy #41786521407](https://github.com/martaxi-boss/VPS/actions/runs/41786521407) SUCCESS, **197 testes PASS**, release `0a1a4c190a7d33752d6dc3f4418ed44735c8a7dd`, **35 ações tipadas**. **Fase 2 certificada integralmente pela Skill (cinco programas):** Calibre [#41746523329](https://github.com/martaxi-boss/VPS/actions/runs/41746523329) EPUB, Darktable [#41746819318](https://github.com/martaxi-boss/VPS/actions/runs/41746819318) TIFF, Krita [#41746923061](https://github.com/martaxi-boss/VPS/actions/runs/41746923061) PNG, GIMP [#41747053943](https://github.com/martaxi-boss/VPS/actions/runs/41747053943) XCF e Scribus [#41785658074](https://github.com/martaxi-boss/VPS/actions/runs/41785658074) PDF+SLA — todos `status=completed`, `FERRARI_SKILL_END_TO_END=PASS`, ZIP recuperado e assinatura dos ficheiros confirmada. **Fase 3 iniciada — LMMS WAV certificado:** inventário áudio/vídeo [#41784949891](https://github.com/martaxi-boss/VPS/actions/runs/41784949891), ensaio LMMS original [#41785970458](https://github.com/martaxi-boss/VPS/actions/runs/41785970458) e Skill real [#41787031335](https://github.com/martaxi-boss/VPS/actions/runs/41787031335) SUCCESS com `lmms-render.wav` PCM estéreo 44,1 kHz, 3,428 s, áudio não silencioso e ZIP completo. `melt` CLI responde no [#41786910295](https://github.com/martaxi-boss/VPS/actions/runs/41786910295), mas saída vídeo ainda não certificada; `synfigstudio` GUI detetado e `synfig` CLI ausente no inventário [#41786739191](https://github.com/martaxi-boss/VPS/actions/runs/41786739191). O REA antigo **continua intocado** e não está autorizado a ser apagado.

**Em desenvolvimento (não é release instalada):** o código MLT/Kdenlive→MP4 foi integrado na [PR #52](https://github.com/martaxi-boss/skill-universal/pull/52), commit `6ef57316234aaeb8dac7e8dde7dbf753ffe4fb4a`, com [CI #41829491020](https://github.com/martaxi-boss/skill-universal/actions/runs/41829491020) SUCCESS (36 adaptadores definidos no GitHub). A VPS ainda utiliza a release certificada anterior com 35 ações; o update do pin no workflow GitHub→VPS foi bloqueado pela ferramenta. **Não declarar MLT/MP4 funcional via Skill até deploy e artefacto real.**

**Higiene física Ferrari comprovada, sem remoção de dependências:** [inventário VPS #41700386577](https://github.com/martaxi-boss/VPS/actions/runs/41700386577) mediu o Ferrari em 13 312 897 024 bytes, dos quais 10 453 159 936 bytes em .runtime. A cache npm privada continha 984 383 488 bytes. [Higiene real #41701443735](https://github.com/martaxi-boss/VPS/actions/runs/41701443735) removeu **apenas** .runtime/npm-cache/_cacache, libertando **984 383 488 bytes (~939 MiB)** e deixando **14 984 884 224 bytes (~13,95 GiB) livres**. FERRARI_PRIVATE_NPM_CACHE_HYGIENE=PASS, FERRARI_CACHE_POSTCHECK=PASS e FERRARI_OTHER_SERVICES_UNCHANGED=PASS. REA, Ruflo, Ghidra, Java, Node, Apktool, venvs e serviços de outros projetos foram preservados. O workflow único de limpeza foi retirado do repositório VPS após PASS; mantém-se o workflow normal de inventário somente de leitura. A cache poderá voltar a crescer se forem instalados novos pacotes npm. **A auditoria de duplicações e o desinstalador do REA antigo NÃO estão certificados.**

| Âmbito | Estado demonstrado |
|---|---|
| Release Ferrari na VPS | **0a1a4c190a7d33752d6dc3f4418ed44735c8a7dd**, raiz física /srv/projects/skill-universal |
| Instalação e testes | [VPS #41786521407](https://github.com/martaxi-boss/VPS/actions/runs/41786521407): SUCCESS, **197 testes PASS**, LMMS WAV real, Fase 2 5/5 preservada, Ghidra/JADX e higiene Ferrari PASS |
| Inventário via Skill | [VPS run #41672372249](https://github.com/martaxi-boss/VPS/actions/runs/41672372249): status=completed, FERRARI_SKILL_END_TO_END=PASS; ZIP com inventário |
| Ferramentas | 81 programas detetados nos catálogos combinados; 55/56 candidatos Ubuntu detetados; **35 ações externas tipadas** e 12 operações base |
| Grupos expandidos | 15 aplicações gráficas Ubuntu instaladas; Prometheus e Valkey privados instalados; 14/16 do lote externo instalados |
| REA próprio Ferrari | rea-agents@6.8.0 original privado; **229 nomes MCP** anunciados; tools/list e tools/call reais via Skill com ZIP PASS [#41713808747](https://github.com/martaxi-boss/VPS/actions/runs/41713808747), [#41717389118](https://github.com/martaxi-boss/VPS/actions/runs/41717389118) |
| Apktool | Versão oficial 3.0.3 privada, Java 25.0.5 próprio, construção e descodificação de APK sintético PASS |
| Ghidra/JADX | Ghidra 12.2 e JADX 1.5.6 próprios; fornecedores privados **Ghidra 12.1.4 + JADX headless MCP 0.7.1**, teste profundo [#41710014556](https://github.com/martaxi-boss/VPS/actions/runs/41710014556) PASS |
| Disco livre | **15,36 GiB** no deploy #41716562469; não é uma garantia de espaço permanente |
| Higiene executada no run | FERRARI_ONLY_HYGIENE=PASS; outside_ferrari_touched=false; preservação da release ativa e rollback |

**Leitura obrigatória:** 81 deteções não são 81 ações, 55/56 não significa 55 testes funcionais e uma instalação não equivale a uma tarefa executável pela Skill. As contagens são a fotografia dos runs citados; confirmar de novo após qualquer alteração.

As provas do REA e Apktool estão também em [run #41654437939](https://github.com/martaxi-boss/VPS/actions/runs/41654437939) e a invocação REA ELF Skill→GitHub→VPS→ZIP em [run #41655035184](https://github.com/martaxi-boss/VPS/actions/runs/41655035184). Um plano DAG remoto foi testado com ZIP em [run #41620077416](https://github.com/martaxi-boss/VPS/actions/runs/41620077416).

## 3. Diretórios e isolamento — não apagar

- Diretório **físico** do Ferrari: **/srv/projects/skill-universal/**. O caminho histórico /home/ubuntu/.local/share/motor-ferrari é um **link exclusivo** para essa pasta, comprovado em [#41714658308](https://github.com/martaxi-boss/VPS/actions/runs/41714658308). Preservar ambos enquanto existirem consumidores do alias.
- REA oficial privado Ferrari: /home/ubuntu/.local/share/motor-ferrari/.runtime/npm/rea/; CLI em node_modules/.bin/rea.
- Node privado: /home/ubuntu/.local/share/motor-ferrari/runtimes/node-22.23.4/.
- Java privado: /home/ubuntu/.local/share/motor-ferrari/runtimes/jdk-25.0.5_8/.
- Ghidra/JADX: tools/ghidra-12.2 e tools/jadx-1.5.6 (programas); tools/rea-providers/ghidra-12.1.4 e tools/rea-providers/jadx-headless-mcp-0.7.1-all.jar (fornecedores privados do REA).
- Apktool privado: /home/ubuntu/.local/share/motor-ferrari/tools/apktool-3.0.3/; cache em .runtime/apktool-frameworks/.
- Manter também .runtime/venvs/, .runtime/npm/, .runtime/browsers/, tools/, releases/ e o apontador current.

O REA do Ferrari provém do pacote oficial npm rea-agents@6.8.0; não é uma instalação compartilhada nem um clone do outro projeto REA. Os instaladores verificam versão e caminhos; a execução de REA usa Node, Apktool e diretórios XDG privados do Ferrari. **Isto ainda não prova a proveniência de todos os pacotes e serviços globais Ubuntu.**

O REA antigo de Engenharia Reversa continua intocado. **NÃO autorizar a sua remoção sem auditoria de dependências, isolamento funcional e plano de recuperação.** Não confundir a pasta REA privada listada acima com o projeto anterior.

## 4. O que está instalado mas ainda não equivale a integração

- As 15 aplicações gráficas foram instaladas por APT; sem sessão gráfica na VPS. Execução interativa e integração pelo Ferrari **não certificadas** para todas.
- ComfyUI v0.43.0: instalação CPU sem pesos de modelos, arranque/ajuda verificados; inferência e ação tipada **não certificadas**.
- Penpot 2.18.5: ficheiros Compose preparados; Docker/Compose e contentores funcionais ainda em falta. É o único dos 56 candidatos atualmente não detetado.
- FreeCAD AppImage 1.1.4: instalado, sem teste gráfico completo.
- Next.js, Tailwind, Bootstrap, shadcn, Streamlit, Gradio, Faster-Whisper, Prefect, Docling e Godot: instalação detetada; muitos permanecem sem ação tipada comprovada. DuckDB, Polars e Typst foram integrados e testados na Fase 1.
- Ruflo 3.71.0 é opcional, com CLI --help PASS, não swarm ou fornecedor de modelos certificado.
- Engenharia reversa: **MCP original disponível via kind=rea-mcp** na Skill Ferrari, 229 nomes conhecidos e três chamadas tools/call reais certificadas (ELF notes, Apktool e captura sintética de processo [#41718385142](https://github.com/martaxi-boss/VPS/actions/runs/41718385142)). Os dois fornecedores Ghidra/JADX têm testes profundos PASS; **nem as 229 operações nem todos os seus casos foram certificados individualmente**.

Nenhuma área deve ser anunciada como completamente operacional apenas por constar de inventário ou manifesto.

## 5. Pendências reais, pela ordem adequada

1. **Higienização e proveniência:** medido o uso Ferrari por diretório e limpa a cache npm de downloads (PASS). **Pendente:** auditoria de propriedade e segurança de bibliotecas repetidas entre ComfyUI/Docling, outros ambientes Python e pacotes APT globais, Java, Node, binários, configurações, processos e serviços. Não apagar dependências ativas nem o REA antigo.
2. **REA e fornecedores:** REA original privado, Ghidra/JADX e Apktool agora têm testes reais PASS; catalogo de 229 nomes comparado. **Pendente:** testar as capacidades realmente utilizadas via Skill Ferrari e verificar fornecedores opcionais, sem declarar todas as 229 ferramentas funcionais.
3. **Isolamento:** testar Ferrari com os caminhos/serviços do REA antigo inacessíveis num ambiente controlado, sem tocar no projeto antigo; exigir testes Skill→GitHub→VPS→ZIP PASS.
4. **Capacidades pendentes:** adaptar programas já instalados por necessidade comprovada; preferir linha de comandos/headless antes de adicionar interface gráfica virtual ou Docker pesado. Penpot é opcional até haver recursos e caso de uso concreto.
5. **Entrega:** confirmar a versão realmente instalada da única Skill no cliente, CI, release VPS, artefactos e documentação alinhados.
6. **Certificação de remoção:** documentar caminhos exatos exclusivos do REA antigo, caminhos protegidos, dependências partilhadas, backup/rollback e testes antes/depois. **Não remover sem aprovação explícita do proprietário.**

O âmbito universal completo ainda está **NÃO IMPLEMENTADA** como certificação global: a cobertura é progressiva, por domínio e prova.

## 6. Regras de seleção e continuidade

- Fonte de seleção: engine/ubuntu_selection.json (56 candidatos); runtime real: engine/ferrari.py, engine/tool_runtime.py, engine/tool_actions.json e engine/orchestrator.py. Versões upstream: install/external-release-lock.json e instaladores próprios.
- Estados distintos: DESCOBERTO → compatível Ubuntu → dependências verificadas → INSTALADO_VPS → teste real → adaptador → DISPONIVEL_PELA_SKILL. Só afirmar a etapa efetivamente demonstrada.
- Para cada novo domínio: verificar versão, licença, Ubuntu 24.04, CPU/RAM/SSD/GPU, formato, disponibilidade headless e segurança antes de instalar. Não incorporar fornecedor pago como dependência obrigatória.
- A ponte não decide operações nem contém lógica de negócio. SSH e Supervisor de outros projetos permanecem inalterados.
- Ao retomar, ler este BOOTSTRAP, conferir commits/runs da release atual, executar o menor teste real necessário e atualizar uma fotografia, sem acumular novamente fases históricas no topo.
- Na VPS, a limpeza automatizada existente em install/ferrari-hygiene.py limita-se a releases Ferrari, preserva release ativa e fallback; não a ampliar a outros projetos.

**Caminho alternativo manual, não usado para a instalação operacional:** .github/workflows/deploy-vps.yml contém fases PRECHECK, DEPLOY e INSTALL_HEADLESS. A via real foi o workflow dedicado no repositório VPS. Não executar o workflow alternativo para repetir instalações existentes sem necessidade e autorização.

## 7. Histórico e relatórios

**Auditoria global da VPS / autorização REA (03/11/2026):** [Relatório com provas](docs/AUDITORIA_GLOBAL_VPS_DUPLICADOS_REA_20261103.md). A limpeza adicional de caches em [#41704431188](https://github.com/martaxi-boss/VPS/actions/runs/41704431188) libertou **239 403 008 bytes** sem afetar serviços, somados aos **984 383 488 bytes** da cache Ferrari — total **1 223 786 496 bytes (~1,14 GiB)**. Encontrada duplicação exata de `libtorch_cpu.so` entre ComfyUI e Docling (440 280 512 bytes cada), **preservada** para manter instalações independentes. O diagnóstico anterior [#41705351869](https://github.com/martaxi-boss/VPS/actions/runs/41705351869) foi **corrigido**: Ghidra/JADX PASS no deploy [#41716562469](https://github.com/martaxi-boss/VPS/actions/runs/41716562469). A comparação MCP [#41708905353](https://github.com/martaxi-boss/VPS/actions/runs/41708905353) comprovou **229/229 nomes iguais** e os pedidos Skill→MCP [#41717389118](https://github.com/martaxi-boss/VPS/actions/runs/41717389118) e [#41717684160](https://github.com/martaxi-boss/VPS/actions/runs/41717684160) executaram ferramentas reais. **REA antigo: NO-GO para remoção neste momento; ainda há workflows ativos.** Higienização global de todas as instalações e verificação de todas as dependências **permanecem parciais**, não as marcar verde.

Relatório de higiene física e duplicações: [docs/HIGIENIZACAO_FISICA_FERRARI_VPS_20261103.md](docs/HIGIENIZACAO_FISICA_FERRARI_VPS_20261103.md). Teste real da Skill REA ELF **após** a limpeza [#41701860486](https://github.com/martaxi-boss/VPS/actions/runs/41701860486) — completed, ZIP, executor privado e artefacto confirmados.

As fases anteriores a esta fotografia estão preservadas em [BOOTSTRAP no commit 77f20a96](https://github.com/martaxi-boss/skill-universal/blob/77f20a96a90e507d12cb2579e5c0554e96eed795/BOOTSTRAP.md) e nos relatórios de docs/. Esse histórico é evidência do que ocorreu então, **não é o estado atual**. Ver README.md para a apresentação operacional e skill/motor-universal-linux/ para a Skill única e respetivas referências.
