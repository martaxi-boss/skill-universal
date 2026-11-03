# BOOTSTRAP — Motor Ferrari / Skill Universal Ubuntu

## Certificação mais recente — 03/11/2026: mobile responsivo e diagnóstico de acessibilidade

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
