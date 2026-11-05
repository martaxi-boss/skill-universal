# Ferrari — Ponto 3: certificação funcional por capacidade (05/11/2026)

## Âmbito
Certificação representativa por domínio do **Motor Ferrari único**, na VPS Ubuntu, usando pedidos reais **ChatGPT → GitHub Actions → VPS → Ferrari → \`response.zip\`** e recuperando provas anteriores. O teste do ponto 2 [#42030605124](https://github.com/martaxi-boss/VPS/actions/runs/42030605124) já tinha instalado/validado **40/40 executores das ações tipadas em pastas Ferrari** e mantido ativa a release \`87969badbde0a77c2c181bb9605357d51a4a30c0\`.

Os novos pedidos continham exclusivamente entradas sintéticas e públicas. Não foram instaladas dependências globais, não se alteraram outros projetos, o SSH, o Supervisor, nem se criaram outras Skills ou coordenadores. Cada novo pedido bem-sucedido devolveu \`report.json.status=completed\`, os artefactos concretos e os marcadores \`FERRARI_SKILL_RESPONSE_ZIP=PASS\` e \`FERRARI_SKILL_END_TO_END=PASS\`.

## Matriz de prova real por domínio

| Capacidade | Provas e resultados verificados | Estado no caso testado |
|---|---|---|
| **Web e browser** | [#42034399375](https://github.com/martaxi-boss/VPS/actions/runs/42034399375) produziu \`site/index.html\` num plano composto; [#41994937194](https://github.com/martaxi-boss/VPS/actions/runs/41994937194) abriu Vite num Playwright real, guardou relatório/screenshot desktop e móvel | **PASS** na página e browser sintéticos |
| **Documentos e PDFs** | [#42034927012](https://github.com/martaxi-boss/VPS/actions/runs/42034927012) — \`kind=auto\`, Markdown → DOCX real via \`/srv/projects/skill-universal/tools/ubuntu-cli/bin/pandoc\`; OCRmyPDF, Calibre EPUB e outras operações documentais demonstradas em [#42030605124](https://github.com/martaxi-boss/VPS/actions/runs/42030605124) | **PASS** nos formatos testados |
| **Dados e análise** | [#42034750707](https://github.com/martaxi-boss/VPS/actions/runs/42034750707) — plano paralelo DuckDB e Polars sobre o mesmo CSV, dois ficheiros \`*-profile.json\` e relatório de execução | **PASS** |
| **Imagem e design** | [#42034399375](https://github.com/martaxi-boss/VPS/actions/runs/42034399375) — SVG real; [#42030605124](https://github.com/martaxi-boss/VPS/actions/runs/42030605124) — GIMP XCF, Krita PNG, Darktable TIFF, Scribus e bibliotecas de imagem | **PASS** nos casos testados |
| **Áudio e vídeo** | [#42030605124](https://github.com/martaxi-boss/VPS/actions/runs/42030605124) — LMMS → WAV e MLT/Kdenlive → MP4 com teste real; [#41992064762](https://github.com/martaxi-boss/VPS/actions/runs/41992064762) — vídeo H.264/AAC com inspeção ffprobe via Skill | **PASS** nos ficheiros sintéticos |
| **CAD, BIM e 3D** | [#42035082826](https://github.com/martaxi-boss/VPS/actions/runs/42035082826) — OpenSCAD \`.scad\` → \`solid.stl\` real; [#41558189146](https://github.com/martaxi-boss/VPS/actions/runs/41558189146) — geometria e semântica IFC de parede sintética; [#41540947069](https://github.com/martaxi-boss/VPS/actions/runs/41540947069) — Blender \`.blend\`, \`.glb\`, PNG | **PASS** no âmbito de protótipo, não na engenharia estrutural |
| **Automação e orquestração** | [#42034399375](https://github.com/martaxi-boss/VPS/actions/runs/42034399375) — um DAG do Ferrari executou \`web-template\` e \`svg-poster\` em paralelo e \`binary-strings\` depois da página; [#42034750707](https://github.com/martaxi-boss/VPS/actions/runs/42034750707) — duas ferramentas de dados em paralelo | **PASS** em planos finitos |
| **REA e Android** | [#42034451772](https://github.com/martaxi-boss/VPS/actions/runs/42034451772) — \`kind=rea-mcp\` \`tools/list\`, \`rea-mcp-result.json\` e ZIP; [#42035337944](https://github.com/martaxi-boss/VPS/actions/runs/42035337944) — APK ZIP sintético → \`aligned.apk\` usando Zipalign privado; ELF real por MCP [#41717389118](https://github.com/martaxi-boss/VPS/actions/runs/41717389118) e Apktool privado [#41717684160](https://github.com/martaxi-boss/VPS/actions/runs/41717684160) | **PASS** nestas chamadas, não no catálogo completo |

**Inventário novo:** [#42034464263](https://github.com/martaxi-boss/VPS/actions/runs/42034464263) — pedido \`kind=inventory\` concluiu e devolveu \`inventory.json\` pela Skill. O último inventário quantitativo previamente inspecionado [#41991752006](https://github.com/martaxi-boss/VPS/actions/runs/41991752006) tinha 55/56 candidatos Ubuntu detetados e 40 ações; contagem de presença **não** equivale a certificação de 55 programas.

## Precisão, limites e exceções

- **7 pedidos novos completaram com SUCCESS, report completed e ZIP real**: #42034399375, #42034451772, #42034464263, #42034750707, #42034927012, #42035082826 e #42035337944.
- **Três pedidos de teste foram cancelados na fila**, sem serem provas de falha da funcionalidade: #42034413247 (dados), #42034426569 (DOCX) e #42034439875 (CAD). Os três foram submetidos novamente, de forma sequencial, e passaram, nos IDs indicados na matriz.
- O pedido CAD \`#42035082826\` confirmou que a operação base \`cad-stl\` usou \`/usr/bin/openscad\`. **É funcional mas usa um executável Ubuntu do sistema.** A certificação 40/40 do ponto 2 refere-se às **40 ações tipadas** e não certifica isolamento dos executores de todas as operações base. Esta diferença é registada explicitamente; não altera retroativamente a release operacional nem autoriza instalação global.
- BIM IFC demonstrou geometria e contagens de elementos numa peça sintética, **não** dimensionamento estrutural, verificação de regulamentos, FreeCAD ou garantia técnica de construção.
- Não houve prova de GUI interativa completa, modelos GPU/ComfyUI, Penpot/Docker, funcionalidades comerciais do Hopper, utilização de dispositivo Android físico via ADB, ou testes individuais às 229 ferramentas MCP. A consulta do catálogo REA **não** é certificação de 229 operações.
- Os testes não incluíram sistemas de produção, contas reais, pagamentos, fornecedores pagos, serviços de terceiros nem informações privadas.
- **Resultado:** ponto 3 **concluído quanto à certificação representativa por capacidade**, com a matriz de provas acima. Cobertura universal de todas as aplicações e opções **não declarada**.

## Organização
As provas são runs/ZIPs GitHub e este relatório do repositório Ferrari. Pedidos de teste usam ficheiros sintéticos e a infraestrutura Ferrari já existente. Nenhum novo gestor, Skill, ponte SSH ou instalador geral foi criado.
