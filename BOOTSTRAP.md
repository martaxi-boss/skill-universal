# BOOTSTRAP — Motor Ferrari / Skill Universal Ubuntu

**Documento canónico de continuidade do projeto.**
**Atualizado:** 2026-11-02. **Repositório exclusivo:** `martaxi-boss/skill-universal`.
**Ambiente-alvo:** servidor VPS Ubuntu 24.04 LTS (ou versão superior suportada, após certificação).
**Estado atual:** base instalada e testada na VPS; REA/Ruflo instalados com teste CLI; JADX/Ghidra com teste funcional. Catálogo completo e ligação direta Skill → VPS ainda não certificados.

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
