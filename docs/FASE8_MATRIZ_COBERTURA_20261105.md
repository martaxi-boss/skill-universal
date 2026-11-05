# Fase 8 — matriz inicial de cobertura funcional real do Motor Ferrari

**Estado:** Fase 8 em certificação, com **13 testes funcionais novos e individualmente verificados**, **não** certificação da fase inteira. Base: código integrado na `main` de `martaxi-boss/skill-universal`, inventário remoto **pós-merge** [VPS #42100973198](https://github.com/martaxi-boss/VPS/actions/runs/42100973198), e provas funcionais [Ponto 3](CERTIFICACAO_FUNCIONAL_PONTO3_20261105.md) + [Fases 6–7](CERTIFICACAO_FASE7_20261105.md).

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

## Provas funcionais individuais verificadas na Fase 8 (32/40)

Estas **32 ações** foram efetivamente executadas pelo Ferrari privado na VPS, com resultados recuperados e inspecionados dentro de `ferrari-response.zip`. Os restantes 8 IDs continuam registados/privados, mas não recebem certificação individual *nova* por associação. A [base de provas JSON](FASE8_EVIDENCIAS_FUNCIONAIS_20261105.json) cobre os 40 IDs e regista, para cada um, se existe execução individual F8.

| Ação tipada | Executável exclusivo do Ferrari | Prova GitHub Actions | Resultado real verificado |
|---|---|---|---|
| `file-mime` | `/srv/projects/skill-universal/tools/ubuntu-cli/bin/file` | [#42102487995](https://github.com/martaxi-boss/VPS/actions/runs/42102487995) | application/json confirmado |
| `graphviz-dot-svg` | `/srv/projects/skill-universal/tools/ubuntu-cli/bin/dot` | [#42101994176](https://github.com/martaxi-boss/VPS/actions/runs/42101994176) | SVG real renderizado de grafo DOT |
| `imagemagick-identify` | `/srv/projects/skill-universal/tools/ubuntu-cli/bin/identify` | [#42102717541](https://github.com/martaxi-boss/VPS/actions/runs/42102717541) | PNG 960x1200 |
| `tesseract-ocr` | `/srv/projects/skill-universal/tools/ubuntu-cli/bin/tesseract` | [#42102717541](https://github.com/martaxi-boss/VPS/actions/runs/42102717541) | OCR reconheceu NOVIDADE - 2026 e texto do cartaz |
| `ffprobe-media-info` | `/srv/projects/skill-universal/tools/ubuntu-cli/bin/ffprobe` | [#42102960020](https://github.com/martaxi-boss/VPS/actions/runs/42102960020) | entrada e saída WAV de 0.25 segundos reportadas |
| `ffmpeg-audio-wav` | `/srv/projects/skill-universal/tools/ubuntu-cli/bin/ffmpeg` | [#42102960020](https://github.com/martaxi-boss/VPS/actions/runs/42102960020) | WAV PCM válido convertido, duração 0.25 segundos |
| `jq-format-json` | `/srv/projects/skill-universal/tools/ubuntu-cli/bin/jq` | [#42102487995](https://github.com/martaxi-boss/VPS/actions/runs/42102487995) | JSON bem formado com engine=Ferrari |
| `readelf-header` | `/srv/projects/skill-universal/tools/ubuntu-cli/bin/readelf` | [#42103286913](https://github.com/martaxi-boss/VPS/actions/runs/42103286913) | ELF64 relocatable x86-64 identificado |
| `vips-image-thumbnail` | `/srv/projects/skill-universal/tools/ubuntu-cli/bin/vips` | [#42102717541](https://github.com/martaxi-boss/VPS/actions/runs/42102717541) | PNG válido 256x320 |
| `objdump-file-header` | `/srv/projects/skill-universal/tools/ubuntu-cli/bin/objdump` | [#42103286913](https://github.com/martaxi-boss/VPS/actions/runs/42103286913) | formato elf64-x86-64 validado |
| `strings-file-extract` | `/srv/projects/skill-universal/tools/ubuntu-cli/bin/strings` | [#42103286913](https://github.com/martaxi-boss/VPS/actions/runs/42103286913) | marca FERRARI_F8_SAFE_ELF_FIXTURE_2026 extraída |
| `ripgrep-find-text` | `/srv/projects/skill-universal/tools/ubuntu-cli/bin/rg` | [#42102487995](https://github.com/martaxi-boss/VPS/actions/runs/42102487995) | Correspondência de Ferrari na linha 1 |
| `inkscape-svg-png` | `/srv/projects/skill-universal/tools/ubuntu-cli/bin/inkscape` | [#42102717541](https://github.com/martaxi-boss/VPS/actions/runs/42102717541) | PNG válido de 960x1200 proveniente de SVG |

| `pandoc-md-docx` | `/srv/projects/skill-universal/tools/ubuntu-cli/bin/pandoc` | [#42105045224](https://github.com/martaxi-boss/VPS/actions/runs/42105045224) | DOCX real ZIP assinado PK gerado de Markdown sintético |
| `binwalk-scan` | `/srv/projects/skill-universal/tools/ubuntu-cli/bin/binwalk` | [#42104010500](https://github.com/martaxi-boss/VPS/actions/runs/42104010500) | ELF64 sintético identificado; assinaturas de compressão heurísticas não tomadas como prova |
| `pdfinfo-report` | `/srv/projects/skill-universal/tools/ubuntu-cli/bin/pdfinfo` | [#42104494930](https://github.com/martaxi-boss/VPS/actions/runs/42104494930) | PDF sintético: 1 página A4 e versão 1.4 |
| `radare2-binary-info` | `/srv/projects/skill-universal/tools/ubuntu-cli/bin/r2` | [#42104010500](https://github.com/martaxi-boss/VPS/actions/runs/42104010500) | radare2 identificou ELF64 x86-64 e metadados do ficheiro |
| `vips-image-inspect` | `/srv/projects/skill-universal/tools/ubuntu-cli/bin/vipsheader` | [#42104715432](https://github.com/martaxi-boss/VPS/actions/runs/42104715432) | PNG de origem 8x8 e WebP de saída 8x8 reconhecidos em duas invocações |
| `imagemagick-webp` | `/srv/projects/skill-universal/tools/ubuntu-cli/bin/convert` | [#42104715432](https://github.com/martaxi-boss/VPS/actions/runs/42104715432) | WEBP RIFF válido de 8 por 8 píxeis produzido a partir de PNG sintético |
| `pdftotext-layout` | `/srv/projects/skill-universal/tools/ubuntu-cli/bin/pdftotext` | [#42104494930](https://github.com/martaxi-boss/VPS/actions/runs/42104494930) | Texto literal FERRARI FASE 8 PDF TESTE extraído do PDF |
| `tshark-pcap-summary` | `/srv/projects/skill-universal/tools/ubuntu-cli/bin/tshark` | [#42104082188](https://github.com/martaxi-boss/VPS/actions/runs/42104082188) | Resumo TShark indicou um frame no PCAP sintético; não houve captura real de rede |
| `typst-compile-pdf` | `/srv/projects/skill-universal/tools/typst-0.15.1/extracted/typst-x86_64-unknown-linux-musl/typst` | [#42105075709](https://github.com/martaxi-boss/VPS/actions/runs/42105075709) | PDF real assinado %PDF gerado a partir de Typst sintético |
| `duckdb-csv-profile` | `/srv/projects/skill-universal/.runtime/venvs/extended/duckdb/bin/python` | [#42105268489](https://github.com/martaxi-boss/VPS/actions/runs/42105268489) | DuckDB privado 2.0.0: perfil CSV com 3 linhas, duas colunas e amostra correta |
| `polars-csv-profile` | `/srv/projects/skill-universal/.runtime/venvs/extended/polars/bin/python` | [#42105268489](https://github.com/martaxi-boss/VPS/actions/runs/42105268489) | Polars privado 2.1.0: perfil CSV com 3 linhas, duas colunas e amostra correta |
| `calibre-md-epub` | `/srv/projects/skill-universal/tools/ubuntu-cli/bin/ebook-convert` | [#42105045224](https://github.com/martaxi-boss/VPS/actions/runs/42105045224) | EPUB real ZIP assinado PK gerado de Markdown sintético |

| `ansible-inventory-json` | `/srv/projects/skill-universal/tools/ubuntu-cli/bin/ansible-inventory` | [#42106208050](https://github.com/martaxi-boss/VPS/actions/runs/42106208050) | Inventário local sintético; grupo ferrari_test e host localhost identificados |
| `darktable-jpeg-tiff` | `/srv/projects/skill-universal/tools/ubuntu-cli/bin/darktable-cli` | [#42107145362](https://github.com/martaxi-boss/VPS/actions/runs/42107145362) | JPEG sintético válido convertido em TIFF RGB de 16x16 |
| `krita-image-png` | `/srv/projects/skill-universal/tools/ubuntu-cli/bin/krita` | [#42106415524](https://github.com/martaxi-boss/VPS/actions/runs/42106415524) | PNG real 8x8 com assinatura PNG produzido por Krita privado |
| `gimp-png-xcf` | `/srv/projects/skill-universal/tools/ubuntu-cli/bin/gimp-console-2.10` | [#42106415524](https://github.com/martaxi-boss/VPS/actions/runs/42106415524) | Projeto editável XCF com assinatura gimp xcf v01 |
| `scribus-text-publication` | `/srv/projects/skill-universal/tools/ubuntu-cli/bin/scribus` | [#42106673246](https://github.com/martaxi-boss/VPS/actions/runs/42106673246) | Publicação Scribus com PDF real e ficheiro SLA editável |
| `kdenlive-mlt-mp4` | `/srv/projects/skill-universal/tools/ubuntu-cli/bin/melt` | [#42107289996](https://github.com/martaxi-boss/VPS/actions/runs/42107289996) | MP4 real H.264/AAC de 2,005 segundos, 320x180 |
| `android-zipalign-apk` | `/srv/projects/skill-universal/tools/android-cli-36.0.0/build-tools/36.0.0/zipalign` | [#42107489642](https://github.com/martaxi-boss/VPS/actions/runs/42107489642) | ZIP sintético no formato de arquivo APK alinhado e íntegro; não instalável nem assinado |

**Outras provas desta fase:** PDF sintético de uma página → `pdfinfo`, `pdftotext` e operação base `pdf-text`; PNG de 8×8 → WebP via ImageMagick → inspeção privada libvips; Markdown → DOCX Pandoc e EPUB Calibre; Typst → PDF; CSV → perfis DuckDB 2.0.0 e Polars 2.1.0; ELF sintético → Radare2 e Binwalk; PCAP sintético de um frame → TShark. O run CSV [#42105059671](https://github.com/martaxi-boss/VPS/actions/runs/42105059671) foi cancelado antes do trabalho e **não conta**; a prova válida é o reenvio isolado [#42105268489](https://github.com/martaxi-boss/VPS/actions/runs/42105268489). Todos os executáveis observados pertencem à árvore Ferrari.

**Cadeias de produção:** `SVG → Inkscape PNG → {Tesseract OCR, ImageMagick identificar, libvips thumbnail}`; `WAV sintético → FFmpeg WAV → ffprobe` em entrada e saída; `ELF64 sintético não executável → readelf, objdump e strings`; `JSON → file/jq/ripgrep` em três trabalhadores paralelos. Todos os resultados ficaram em `/srv/projects/skill-universal/.runtime/` e nenhum input confidencial foi publicado.

## Oito ações sem nova prova individual F8

Abaixo permanece a distinção entre **execução previamente demonstrada por outro teste** e **teste individual nesta fase**:

| Ação ainda não provada individualmente na F8 | Próxima porta / limite honesto |
|---|---|
| `ocrmypdf-searchable-pdf` | Testar PDF digitalizado sintético, OCR e saída pesquisável, com artefactos reais |
| `apktool-decode-resources` | Requer APK seguro com recursos/manifesto válidos; não usar APKs de utilizadores em GitHub público |
| `rea-elf-notes`, `rea-android-resources` | Existem testes anteriores de REA e MCP, mas estas ações tipadas pedem novos artefactos específicos |
| `lmms-project-wav` | Já houve síntese sonora real na Fase 6, mas não foi repetida nesta ronda da F8 |
| `android-apksigner-verify` | Precisa de APK realmente assinado; alinhamento ZIP não comprova assinatura |
| `android-aapt2-manifest` | Exige APK válido com manifesto binário compilado; não confundir com ZIP genérico |
| `android-adb-install-apk` | Não pode ser certificado sem dispositivo Android físico autorizado; não inventar instalação |

A execução [#42106858184](https://github.com/martaxi-boss/VPS/actions/runs/42106858184) falhou devido a um **JPEG de teste corrompido no envio**; não representa falha do Darktable instalado. Foi refeita com 659 bytes íntegros, e [#42107145362](https://github.com/martaxi-boss/VPS/actions/runs/42107145362) produziu o TIFF verificado. Para `android-zipalign-apk`, a prova é apenas alinhamento de um **ZIP com extensão APK**, não uma aplicação instalável ou assinada.

**Nesta ronda não se adicionaram dependências globais ou serviços à VPS; os testes usaram os executores já privados do Ferrari.** A higiene destrutiva não é necessária para provar funções, e permanece limitada a resíduos próprios com identificação e recuperação.

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
