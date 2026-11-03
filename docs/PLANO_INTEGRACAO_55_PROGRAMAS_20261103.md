# Ferrari — integração progressiva dos 55 programas detetados sem ação direta (03/11/2026)

**Objetivo:** integrar as capacidades dos programas **já presentes** na VPS, dentro da única Skill e motor Ferrari. Cada projeto de outros repositórios mantém diretório e dependências separados. A ligação GitHub Actions → SSH é apenas transporte e não deve ganhar lógica de seleção, regras ou coordenação.

## Linha de base verificada

- [Inventário real da Skill #41728487241](https://github.com/martaxi-boss/VPS/actions/runs/41728487241): 107 entradas no catálogo, 81 detetadas, 25 ações tipadas, 55 programas detetados sem ação direta. Os estados `installed_unintegrated` são observações, não prova de funcionamento completo nem de falta absoluta de uso indireto.
- [Ferrari anterior #41716562469](https://github.com/martaxi-boss/VPS/actions/runs/41716562469): instalação real PASS e 164 testes.
- **Fase 1 — código integrado na main:** [PR #39](https://github.com/martaxi-boss/skill-universal/pull/39) com 4 ações novas, [CI #41735059679](https://github.com/martaxi-boss/skill-universal/actions/runs/41735059679) SUCCESS, 172 testes. [Deploy #41735337190](https://github.com/martaxi-boss/VPS/actions/runs/41735337190) iniciado para validar na VPS. **Não declarar a fase funcional até prova real dos resultados.**

## Fases previstas sem instalações desnecessárias

| Fase | Programas observados, ainda sem ação direta no inventário inicial | Resultado operacional a certificar |
|---|---|---|
| **1 — Dados e documentos vetoriais** | DuckDB, Polars, Inkscape, Typst (4) | CSV→perfil JSON com colunas, tipos, linhas/amostra; SVG→PNG; Typst→PDF, testes reais na VPS |
| **2 — Design e publicação** | GIMP, Krita, Scribus, Darktable, Calibre (5) | Exportação/conversão ou metadados comprovados no Ubuntu, sem assumir que GUI funciona sem ecrã |
| **3 — Áudio e vídeo** | yt-dlp, Kdenlive, Audacity, OBS Studio, LMMS, Synfig, OpenShot (7) | Processamento local e verificação de duração, codecs e ficheiro final; serviços GUI por certificar |
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

- A Skill instalada no ChatGPT ainda divulga instruções antigas (68 testes); a versão canónica no GitHub já descreve a release de 164 testes e a integração MCP. Atualizar a instalação sem perder a identidade da Skill.
- O REA FINAL continua a receber pedidos num workflow próprio; a transição para o REA privado do Ferrari exige confirmação dos consumidores.
- Isolamento absoluto: há executáveis `/usr/bin` partilhados; copiar ou desinstalar APT globais sem uma análise de dependências não produz isolamento seguro.
- Penpot e Docker não foram detetados; ComfyUI está instalado em CPU mas sem modelos. Não apresentar estas funcionalidades como plenamente funcionais.
