# Ferrari — integração progressiva dos 55 programas detetados sem ação direta (03/11/2026)

**Atualização de 05/11/2026 (após este plano histórico):** inventário real da VPS [#41991752006](https://github.com/martaxi-boss/VPS/actions/runs/41991752006) confirmou **55/56 candidatos Ubuntu presentes**, 40 ações invocáveis e Penpot ausente. Vídeo MLT/Kdenlive → MP4 foi **certificado para um projeto sintético** pela Skill em [#41992064762](https://github.com/martaxi-boss/VPS/actions/runs/41992064762), com artefacto H.264 válido e FFprobe PASS. As indicações posteriores nesta página de vídeo pendente descrevem o estado de 03/11 e não anulam esta prova nova.

**Objetivo:** integrar as capacidades dos programas **já presentes** na VPS, dentro da única Skill e motor Ferrari. Cada projeto de outros repositórios mantém diretório e dependências separados. A ligação GitHub Actions → SSH é apenas transporte e não deve ganhar lógica de seleção, regras ou coordenação.

## Linha de base verificada

- [Inventário real da Skill #41728487241](https://github.com/martaxi-boss/VPS/actions/runs/41728487241): 107 entradas no catálogo, 81 detetadas, 25 ações tipadas, 55 programas detetados sem ação direta. Os estados `installed_unintegrated` são observações, não prova de funcionamento completo nem de falta absoluta de uso indireto.
- [Ferrari anterior #41716562469](https://github.com/martaxi-boss/VPS/actions/runs/41716562469): instalação real PASS e 164 testes.
- **Fase 1 — concluída:** 4 ações novas (DuckDB, Polars, Inkscape, Typst), [deploy #41738343314](https://github.com/martaxi-boss/VPS/actions/runs/41738343314) SUCCESS com 175 testes e operações reais; pedidos pela Skill comprovados em [CSV #41738862274](https://github.com/martaxi-boss/VPS/actions/runs/41738862274), [Typst #41738907357](https://github.com/martaxi-boss/VPS/actions/runs/41738907357) e [Inkscape #41739107535](https://github.com/martaxi-boss/VPS/actions/runs/41739107535).
- **Fase 2 — cinco adaptadores certificados (5/5):** [deploy #41785048137](https://github.com/martaxi-boss/VPS/actions/runs/41785048137) SUCCESS, **192 testes**, 34 ações no total; Calibre [#41746523329](https://github.com/martaxi-boss/VPS/actions/runs/41746523329) EPUB, Darktable [#41746819318](https://github.com/martaxi-boss/VPS/actions/runs/41746819318) TIFF, Krita [#41746923061](https://github.com/martaxi-boss/VPS/actions/runs/41746923061) PNG, GIMP [#41747053943](https://github.com/martaxi-boss/VPS/actions/runs/41747053943) XCF e Scribus [#41785658074](https://github.com/martaxi-boss/VPS/actions/runs/41785658074) PDF + SLA. Os cinco passaram na Skill com ZIP real e assinatura de ficheiros verificada. Nenhum ambiente gráfico completo ou servidor novo foi instalado.

- **Fase 3 — vídeo MLT/Kdenlive implementado no código, ainda NÃO certificado na VPS:** [PR #52](https://github.com/martaxi-boss/skill-universal/pull/52), merge `6ef57316234aaeb8dac7e8dde7dbf753ffe4fb4a`; [CI #41829491020](https://github.com/martaxi-boss/skill-universal/actions/runs/41829491020) SUCCESS, 36 ações tipadas no GitHub, incluindo MP4 com validação `ffprobe`. O workflow de deploy Ferrari na VPS continua pinado à release `0a1a4c190a7d33752d6dc3f4418ed44735c8a7dd` (35 ações). A atualização do pin foi bloqueada pela ferramenta, pelo que não existe ainda prova de deploy nem ficheiro MP4 via Skill para esta ação. Não confundir CI de código com certificação real.
- **Fase 3 — áudio iniciado:** [deploy #41786521407](https://github.com/martaxi-boss/VPS/actions/runs/41786521407) SUCCESS, **197 testes PASS**, 35 ações, LMMS `render` para WAV com duas notas sintéticas não silenciosas. A [Skill #41787031335](https://github.com/martaxi-boss/VPS/actions/runs/41787031335) devolveu ZIP, `report.json.status=completed` e WAV de 3,428 segundos, estéreo 44,1 kHz; ficheiro inspecionado. `melt` aceita CLI [#41786910295](https://github.com/martaxi-boss/VPS/actions/runs/41786910295), mas falta certificar vídeo. O inventário [#41786739191](https://github.com/martaxi-boss/VPS/actions/runs/41786739191) não encontrou comando `synfig`, apenas a aplicação gráfica `synfigstudio`; não instalar soluções paralelas para esconder a limitação.

## Fases previstas sem instalações desnecessárias

| Fase | Programas observados, ainda sem ação direta no inventário inicial | Resultado operacional a certificar |
|---|---|---|
| **1 — Dados e documentos vetoriais** | DuckDB, Polars, Inkscape, Typst (4) | CSV→perfil JSON com colunas, tipos, linhas/amostra; SVG→PNG; Typst→PDF, testes reais na VPS |
| **2 — Design e publicação** | GIMP, Krita, Scribus, Darktable, Calibre (5/5 certificados) | EPUB/TIFF/PNG/XCF e Scribus PDF+SLA via Skill PASS, todos ficheiros reais |
| **3 — Áudio e vídeo** | yt-dlp, Kdenlive, Audacity, OBS Studio, LMMS, Synfig, OpenShot (7: LMMS certificado; outros pendentes) | LMMS `.mmp/.mmpz` → WAV real e não silencioso PASS via Skill; `melt` CLI descoberto para fase seguinte, sem exportação vídeo ainda |
| **4 — CAD, mapas e jogos** | FreeCAD, LibreCAD, QGIS, SolveSpace, Godot (5) | Análise/exportação headless de CAD, dados geográficos e scripts/projetos, sem componentes gráficos falsos |
| **5 — Web/frontend** | Next.js, Tailwind, Bootstrap, Playwright, shadcn (5) | Builds e relatórios/validação de projetos de teste na pasta Ferrari; dependências npm próprias |
| **6 — Dados, processamento e IA CPU** | OpenCV, Docling, Streamlit, Gradio, Faster-Whisper, ComfyUI (6) | Operações reais por ambiente Python privado; recursos, modelos CPU e condições de execução documentados |
| **7 — Motores e serviços especializados** | Ghidra 12.2, Ruflo, Prefect, Prometheus, Valkey (5) | Invocação/inspeção real sem iniciar serviços persistentes não autorizados e sem usar fornecedores de outros projetos |
| **8 — Desenvolvimento e infraestrutura** | Git, Python, pip, venv, Node, npm, GCC, Make, cliente PostgreSQL, curl, wget, zip, unzip, Java, GDB, strace, ADB, AAPT (18) | Ações técnicas úteis com entradas específicas e saída auditável, em vez de inventar uma chamada genérica a qualquer shell |

**Total: 55 programas observados, não 55 operações obrigatoriamente distintas.** Uma ferramenta pode já estar integrada indiretamente: por exemplo Ghidra pelo REA ou Blender numa operação base. Não criar ações repetidas só para inflacionar contadores.

## Critérios de passagem por fase

1. Confirmar versão, localização e independência física do executável ou ambiente Python/npm. O binário global do Ubuntu deve ser explicitamente assinalado, nunca descrito como privado.
2. Adicionar apenas adaptadores tipados **ao Ferrari existente** (`engine/tool_actions.json`, `engine/tool_runtime.py`, módulos auxiliares em `engine/`). Não criar outros servidores MCP, Skills, coordenadores ou novas regras na ponte SSH.
3. Testes unitários com entradas sintéticas: seleção da ação correta, recusa de formatos inválidos, saída não vazia, tratamento de erro real e não alteração de outros projetos.
4. Executar no GitHub CI, entregar a release pinada à VPS e fazer um pedido real pela Skill Ferrari. Confirmar `report.json.status=completed` e o ficheiro final dentro do ZIP.
5. Medir o inventário `installed_unintegrated` antes/depois, registar IDs de execução, manter rollback e conservar aplicações que ainda não têm operação headless adequada.
6. **Não confundir** presença, integração implementada e testes PASS. Não remover REA FINAL ou dependências de outros projetos por mera semelhança.

## Pendências separadas da expansão

- A Skill instalada no ChatGPT ainda divulga instruções antigas (68 testes); o BOOTSTRAP canónico no GitHub está na release de 197 testes e 35 adaptadores. O workflow GitHub da Skill está sincronizado com a release atual, mas a descrição instalada da Skill continua desatualizada; atualizar sem criar outra identidade.
- O REA FINAL continua a receber pedidos num workflow próprio; a transição para o REA privado do Ferrari exige confirmação dos consumidores.
- Isolamento absoluto: há executáveis `/usr/bin` partilhados; copiar ou desinstalar APT globais sem uma análise de dependências não produz isolamento seguro.
- Penpot e Docker não foram detetados; ComfyUI está instalado em CPU mas sem modelos. Não apresentar estas funcionalidades como plenamente funcionais.
