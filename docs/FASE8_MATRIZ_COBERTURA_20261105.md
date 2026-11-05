# Fase 8 — matriz inicial de cobertura funcional real do Motor Ferrari

**Estado:** auditoria inicial da Fase 8, **não** certificação da fase inteira. Base: código integrado na `main` de `martaxi-boss/skill-universal`, inventário remoto **pós-merge** [VPS #42100973198](https://github.com/martaxi-boss/VPS/actions/runs/42100973198), e provas funcionais [Ponto 3](CERTIFICACAO_FUNCIONAL_PONTO3_20261105.md) + [Fases 6–7](CERTIFICACAO_FASE7_20261105.md).

**Regra permanente:** repositório `martaxi-boss/skill-universal` = pasta exclusiva `/srv/projects/skill-universal/`, sem programas, executores, caches ou dependências de aplicação Ferrari instalados globalmente. Nada de outros projetos, fornecedores partilhados ou novos coordenadores. O Ubuntu conserva as suas bibliotecas de SO.

## Inventário remoto observado (05/11/2026)

| Estado diferente | Quantidade | Interpretação correta |
|---|---:|---|
| Operações base definidas no motor | **12** | Implementação disponível no código, não 12 aplicações distintas |
| Ações tipadas no manifesto | **40** | Registradas e invocáveis com executores privados; cada ação exige teste funcional quando usada |
| Programas selecionados Ubuntu | **56** | Lista de candidatos, não 56 instalações aprovadas |
| Programas selecionados com instalação privada detetada | **47/56** | **29** `callable`, **18** `installed_unintegrated`; presença não é certificação operacional |
| Programas selecionados não detetados em instalação privada | **9/56** | Sem fallback aos binários globais; bloqueados até integração específica |
| Programas no inventário combinado de origens diversas | **108 registos** | Não equivale a 108 ferramentas utilizáveis nem a 108 testes |

A evidência `kind=inventory` terminou com `report.json.status=completed`, `FERRARI_SKILL_END_TO_END=PASS`, `response.zip` verdadeiro e `artifacts/inventory.json`. O motor ativo é a release F7 imutável `758e1b435317fa26277b332b75bc47c67910be81`; `main` contém essa release no histórico, mas não deve ser confundida com o ponteiro `current`.

## Operações base (12)

`web-template`, `svg-poster`, `pdf-text`, `image-resize`, `video-thumbnail`, `apk-decompile`, `binary-strings`, `cad-stl`, `blender-house`, `office-pdf`, `ifc-summary`, `vite-build`

As 12 operações são métodos do motor Ferrari. O catálogo e os testes do Ponto 3 e Fases 6–7 mostram testes representativos de web, vídeo, PDF, CAD/Blender/Office, BIM/IFC, SVG e Android. Exigir artefactos verdadeiros para cada tipo de entrada e saída, não apenas a presença de uma função em código.

## Matriz de ações tipadas (40) e evidências por domínio

| Domínio | Ações tipadas registadas no Ferrari | Provas representativas e limites |
|---|---|---|
| **Android físico** | `android-adb-install-apk` | [Zipalign #42035337944](https://github.com/martaxi-boss/VPS/actions/runs/42035337944). ADB tem executor privado mas instalação em dispositivo real NÃO certificada |
| **Audio** | `ffmpeg-audio-wav`, `lmms-project-wav` | [LMMS/MLT #42030605124](https://github.com/martaxi-boss/VPS/actions/runs/42030605124). PASS de saída WAV sintética via LMMS; cada ação FFmpeg requer resultado próprio |
| **Automação** | `ansible-inventory-json` | [Ansible #42092622311](https://github.com/martaxi-boss/VPS/actions/runs/42092622311), [DAG #42098800995](https://github.com/martaxi-boss/VPS/actions/runs/42098800995). PASS de inventário Ansible e DAG; sem coordenação VPS adicional |
| **Dados** | `jq-format-json`, `duckdb-csv-profile`, `polars-csv-profile` | [DuckDB/Polars #42034750707](https://github.com/martaxi-boss/VPS/actions/runs/42034750707). PASS perfis de CSV reais; sem prometer dashboards de produção |
| **Desenvolvimento** | `file-mime`, `ripgrep-find-text` | [DAG/ZIP #42099036932](https://github.com/martaxi-boss/VPS/actions/runs/42099036932). File/grep: executores privados; prova em produção limitada às ações demonstradas |
| **Diagramas** | `graphviz-dot-svg` | [40 ações privadas #42098462830](https://github.com/martaxi-boss/VPS/actions/runs/42098462830). Ação Graphviz registada; sem teste Graphviz end-to-end específico neste certificado |
| **Engenharia reversa** | `binwalk-scan`, `readelf-header`, `radare2-binary-info`, `objdump-file-header`, `strings-file-extract`, `tshark-pcap-summary`, `apktool-decode-resources`, `rea-elf-notes`, `rea-android-resources`, `android-apksigner-verify`, `android-aapt2-manifest`, `android-zipalign-apk` | [REA/ELF #41717389118](https://github.com/martaxi-boss/VPS/actions/runs/41717389118), [APK #41717684160](https://github.com/martaxi-boss/VPS/actions/runs/41717684160). PASS só nas chamadas concretas; 229 nomes MCP não equivalem a testes |
| **Imagem e design** | `imagemagick-identify`, `vips-image-thumbnail`, `vips-image-inspect`, `imagemagick-webp`, `inkscape-svg-png`, `darktable-jpeg-tiff`, `krita-image-png`, `gimp-png-xcf` | [Imagem #42030605124](https://github.com/martaxi-boss/VPS/actions/runs/42030605124). PASS para os formatos sintéticos descritos no relatório, não GUI integral |
| **Office, OCR, publicação** | `pandoc-md-docx`, `tesseract-ocr`, `pdfinfo-report`, `pdftotext-layout`, `ocrmypdf-searchable-pdf`, `typst-compile-pdf`, `calibre-md-epub`, `scribus-text-publication` | [Pandoc #42034927012](https://github.com/martaxi-boss/VPS/actions/runs/42034927012), [Calibre #42092650850](https://github.com/martaxi-boss/VPS/actions/runs/42092650850), [Office #42098462830](https://github.com/martaxi-boss/VPS/actions/runs/42098462830). PASS para DOCX/EPUB/PDF demonstrados, OCR não universal |
| **Vídeo e media** | `ffprobe-media-info`, `kdenlive-mlt-mp4` | [MLT/Kdenlive #42030605124](https://github.com/martaxi-boss/VPS/actions/runs/42030605124), [vídeo #41992064762](https://github.com/martaxi-boss/VPS/actions/runs/41992064762). PASS em ficheiros H.264/MP4 sintéticos; não GUI OBS |


**Precisão:** nesta matriz a presença de uma ação tipada significa `registada + executor privado`. A coluna da direita apresenta **testes representativos por domínio**; não confirma que *todas* as ações dessa linha tenham sido invocadas com sucesso individualmente. Para cada nova ação usada em produção, exigir entrada, saída, run ID, ZIP e limites publicados.

## Nove candidatos ainda não privados

| Candidato | Tipo de instalação pretendido | Estado |
|---|---|---|
| `ytdlp` | CLI headless | Não detetado privado; não usar global |
| `librecad`, `qgis`, `audacity`, `obs`, `solvespace`, `synfig`, `openshot` | GUI/desktop | Não detetados privadamente; avaliar headless e licenças antes de instalar |
| `penpot` | Upstream externo | Preparado sem Docker operacional; não certificar serviço ou editor |

Ainda por provar fora do catálogo: dispositivo Android físico por ADB, modelos ComfyUI, GUI interativa integral, funcionalidades comerciais Hopper e execução individual de todas as ferramentas REA MCP. Ruflo tem CLI privado e **não** tem certificação de agentes reais/modelos. Nenhum programa pago é obrigatório.

## Ordem operacional desta fase

1. **Usar primeiro provas já existentes:** não repetir testes só para inflacionar números.
2. **Corrigir capacidades realmente solicitadas:** uma de cada vez, com compatibilidade Ubuntu, licença, caminhos privados, necessidade real de recurso e mínimo impacto na VPS.
3. **Teste funcional:** GitHub CI → preflight protegido → VPS real → Skill/GitHub/ZIP → artefacto verificado → inventário novamente.
4. **Higienização em cada grupo:** eliminar apenas ficheiros temporários abandonados e pertencentes ao Ferrari, com confirmação de que não estão a ser usados; preservar ativo e fallback. Não tocar nos 16 APT globais até classificação transversal da Fase 9.

**Fecho da Fase 8:** só quando existir matriz completa `domínio → operação → executor privado → caso real → resultado → limitações`, sem funções fictícias ou fallback silencioso ao Ubuntu global. Este documento inicia essa revisão; **não declara a Fase 8 concluída**.
