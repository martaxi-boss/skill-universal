# BOOTSTRAP — Motor Ferrari / Skill Universal Ubuntu

**Estado operacional de referência: 03/11/2026 (UTC).** Este documento é o ponto de entrada atual. Provas antigas e fases substituídas continuam acessíveis no histórico Git e nos relatórios de docs/, mas não são o estado presente. Não promover uma previsão ou um catálogo a certificação.

## 1. Decisão permanente — UMA ÚNICA SKILL

ChatGPT, Codex ou outra IA interpreta o pedido → UMA ÚNICA SKILL UNIVERSAL Ferrari → conector GitHub autenticado → workflow exclusivo Ferrari no repositório martaxi-boss/VPS → SSH existente → Motor Ferrari Ubuntu → orquestrador e ferramentas instaladas → relatório e ZIP.

O motor decide a ferramenta e executa as operações; a IA orienta. O Ferrari tem instalação e runtime próprios, sem coordenador na VPS de outro projeto. Não misturar com Project Leader, Engenharia Reversa antiga, Telegram, FADEGO, PINK IPTV ou outros projetos. Não adicionar Skills, camadas ou pontes paralelas.

**Objetivo:** cobertura progressiva em CONSTRUÇÃO, CAD, BIM/IFC, plantas, 3D, web, software, aplicações, gráficos, vídeo, áudio, documentos, PDF, OCR, dados, mapas, automação e engenharia reversa. Universal descreve a ambição, não significa que todos os domínios estejam certificados.

## 2. Fotografia atual com provas

**Higiene física Ferrari comprovada, sem remoção de dependências:** [inventário VPS #41700386577](https://github.com/martaxi-boss/VPS/actions/runs/41700386577) mediu o Ferrari em 13 312 897 024 bytes, dos quais 10 453 159 936 bytes em .runtime. A cache npm privada continha 984 383 488 bytes. [Higiene real #41701443735](https://github.com/martaxi-boss/VPS/actions/runs/41701443735) removeu **apenas** .runtime/npm-cache/_cacache, libertando **984 383 488 bytes (~939 MiB)** e deixando **14 984 884 224 bytes (~13,95 GiB) livres**. FERRARI_PRIVATE_NPM_CACHE_HYGIENE=PASS, FERRARI_CACHE_POSTCHECK=PASS e FERRARI_OTHER_SERVICES_UNCHANGED=PASS. REA, Ruflo, Ghidra, Java, Node, Apktool, venvs e serviços de outros projetos foram preservados. O workflow único de limpeza foi retirado do repositório VPS após PASS; mantém-se o workflow normal de inventário somente de leitura. A cache poderá voltar a crescer se forem instalados novos pacotes npm. **A auditoria de duplicações e o desinstalador do REA antigo NÃO estão certificados.**

| Âmbito | Estado demonstrado |
|---|---|
| Release Ferrari na VPS | 6c93a392dfe9a02d7ccfef9d47317c9685976484 |
| Instalação e testes | [VPS run #41671631900](https://github.com/martaxi-boss/VPS/actions/runs/41671631900): SUCCESS; 139 testes PASS; FERRARI_DEPLOY_TRANSPORT=PASS |
| Inventário via Skill | [VPS run #41672372249](https://github.com/martaxi-boss/VPS/actions/runs/41672372249): status=completed, FERRARI_SKILL_END_TO_END=PASS; ZIP com inventário |
| Ferramentas | 81 programas detetados nos catálogos combinados; 55/56 candidatos Ubuntu detetados; 25 ações externas tipadas e 12 operações base |
| Grupos expandidos | 15 aplicações gráficas Ubuntu instaladas; Prometheus e Valkey privados instalados; 14/16 do lote externo instalados |
| REA próprio Ferrari | rea-agents 6.8.0 via npm próprio: CLI disponível e duas ações reais certificadas (ELF e recursos Android) |
| Apktool | Versão oficial 3.0.3 privada, Java 25.0.5 próprio, construção e descodificação de APK sintético PASS |
| Ghidra/JADX | Ghidra 12.2 em modo headless PASS; JADX 1.5.6 com saída Java PASS |
| Disco livre | ~13,95 GiB após higiene #41701443735; ~9,79 GiB era uma fotografia anterior (#41671631900) |
| Higiene executada no run | FERRARI_ONLY_HYGIENE=PASS; outside_ferrari_touched=false; preservação da release ativa e rollback |

**Leitura obrigatória:** 81 deteções não são 81 ações, 55/56 não significa 55 testes funcionais e uma instalação não equivale a uma tarefa executável pela Skill. As contagens são a fotografia dos runs citados; confirmar de novo após qualquer alteração.

As provas do REA e Apktool estão também em [run #41654437939](https://github.com/martaxi-boss/VPS/actions/runs/41654437939) e a invocação REA ELF Skill→GitHub→VPS→ZIP em [run #41655035184](https://github.com/martaxi-boss/VPS/actions/runs/41655035184). Um plano DAG remoto foi testado com ZIP em [run #41620077416](https://github.com/martaxi-boss/VPS/actions/runs/41620077416).

## 3. Diretórios e isolamento — não apagar

- Diretório principal a preservar: /home/ubuntu/.local/share/motor-ferrari/.
- REA oficial privado Ferrari: /home/ubuntu/.local/share/motor-ferrari/.runtime/npm/rea/; CLI em node_modules/.bin/rea.
- Node privado: /home/ubuntu/.local/share/motor-ferrari/runtimes/node-22.23.4/.
- Java privado: /home/ubuntu/.local/share/motor-ferrari/runtimes/jdk-25.0.5_8/.
- Ghidra/JADX: /home/ubuntu/.local/share/motor-ferrari/tools/ghidra-12.2/ e tools/jadx-1.5.6/.
- Apktool privado: /home/ubuntu/.local/share/motor-ferrari/tools/apktool-3.0.3/; cache em .runtime/apktool-frameworks/.
- Manter também .runtime/venvs/, .runtime/npm/, .runtime/browsers/, tools/, releases/ e o apontador current.

O REA do Ferrari provém do pacote oficial npm rea-agents@6.8.0; não é uma instalação compartilhada nem um clone do outro projeto REA. Os instaladores verificam versão e caminhos; a execução de REA usa Node, Apktool e diretórios XDG privados do Ferrari. **Isto ainda não prova a proveniência de todos os pacotes e serviços globais Ubuntu.**

O REA antigo de Engenharia Reversa continua intocado. **NÃO autorizar a sua remoção sem auditoria de dependências, isolamento funcional e plano de recuperação.** Não confundir a pasta REA privada listada acima com o projeto anterior.

## 4. O que está instalado mas ainda não equivale a integração

- As 15 aplicações gráficas foram instaladas por APT; sem sessão gráfica na VPS. Execução interativa e integração pelo Ferrari **não certificadas** para todas.
- ComfyUI v0.43.0: instalação CPU sem pesos de modelos, arranque/ajuda verificados; inferência e ação tipada **não certificadas**.
- Penpot 2.18.5: ficheiros Compose preparados; Docker/Compose e contentores funcionais ainda em falta. É o único dos 56 candidatos atualmente não detetado.
- FreeCAD AppImage 1.1.4: instalado, sem teste gráfico completo.
- Next.js, Tailwind, Bootstrap, shadcn, DuckDB, Polars, Streamlit, Gradio, Faster-Whisper, Prefect, Docling, Typst e Godot: instalação detetada; muitos permanecem sem ação tipada comprovada.
- Ruflo 3.71.0 é opcional, com CLI --help PASS, não swarm ou fornecedor de modelos certificado.
- Engenharia reversa: duas ações do REA estão integradas, mas nem todo o catálogo MCP e os fornecedores profundos foram testados.

Nenhuma área deve ser anunciada como completamente operacional apenas por constar de inventário ou manifesto.

## 5. Pendências reais, pela ordem adequada

1. **Higienização e proveniência:** medido o uso Ferrari por diretório e limpa a cache npm de downloads (PASS). **Pendente:** auditoria de propriedade e segurança de bibliotecas repetidas entre ComfyUI/Docling, outros ambientes Python e pacotes APT globais, Java, Node, binários, configurações, processos e serviços. Não apagar dependências ativas nem o REA antigo.
2. **REA e fornecedores:** auditar dependências efetivas do pacote npm, disponibilidade de fornecedores Linux e integração REA→Ghidra/Apktool/JADX quando aplicável; testar funções essenciais com ficheiros reais. Não declarar equivalência integral com o REA antigo com base em duas ações.
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

As fases anteriores a esta fotografia estão preservadas em [BOOTSTRAP no commit 77f20a96](https://github.com/martaxi-boss/skill-universal/blob/77f20a96a90e507d12cb2579e5c0554e96eed795/BOOTSTRAP.md) e nos relatórios de docs/. Esse histórico é evidência do que ocorreu então, **não é o estado atual**. Ver README.md para a apresentação operacional e skill/motor-universal-linux/ para a Skill única e respetivas referências.
