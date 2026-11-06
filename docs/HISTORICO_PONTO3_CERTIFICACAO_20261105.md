# Arquivo histórico — Ponto 3 Ferrari (05/11/2026)

Esta secção foi retirada do BOOTSTRAP operacional para manter o arquivo de provas compacto. É uma **fotografia histórica antes da certificação ADB física**; as afirmações de ADB pendente foram ultrapassadas por [F8 40/40](FASE8_FECHO_20261105.md). O estado de referência atual está no [BOOTSTRAP](../BOOTSTRAP.md).

### Ponto 3 — certificação por capacidade (05/11/2026)

**Provas integradas:** [VPS #42030605124](https://github.com/martaxi-boss/VPS/actions/runs/42030605124) — execução real de programas dentro do Ferrari e teste Vite/Playwright; [Skill→VPS→ZIP #42034310904](https://github.com/martaxi-boss/VPS/actions/runs/42034310904) — orquestração DAG real concluída, artefactos descarregados e assinaturas verificadas.

| Domínio | Resultado comprovado | Limite da prova |
|---|---|---|
| Web/navegador | **PASS** — Vite build, Playwright real, teclado, controlos, responsividade e inspeção básica de acessibilidade; novo HTML gerado pela Skill | Não certifica backend, autenticação ou produção de qualquer website |
| Documentos/PDF/OCR | **PASS** — Pandoc DOCX, LibreOffice PDF, Typst PDF, extração e PDF pesquisável por OCRmyPDF/Tesseract | Não certifica layout perfeito em documentos arbitrários |
| Dados | **PASS** — DuckDB/Polars em CSV com Python privado, JQ em JSON | Não certifica dados externos nem todos os formatos |
| Imagem/design | **PASS** — Inkscape SVG→PNG, GIMP XCF, Krita PNG, Darktable TIFF, Scribus PDF/SLA | Exportação headless sintética, não sessão GUI interativa completa |
| Áudio/vídeo | **PASS** — LMMS WAV e MLT/Kdenlive MP4, FFmpeg/FFprobe em ficheiros reais | Não certifica projetos de edição complexos nem aceleração GPU |
| CAD/BIM/3D | **PASS** — IFC semântico+geometria, OpenSCAD→STL, Blender→BLEND+GLB+PNG (ficheiros e render verificados) | Modelo 3D conceptual; não projeto de engenharia/obra certificado |
| Automação | **PASS** — DAG com checkpoint, retoma em outro processo, paralelismo e [Skill→ZIP](https://github.com/martaxi-boss/VPS/actions/runs/42099036932), sem outro coordenador | Tempo cooperativo; CPU/RAM hard e agentes Ruflo ainda não certificados |
| REA/Engenharia reversa | **PASS parcial** — REA privado analisou ELF e APK sintético; Ghidra/JADX possuem testes concretos anteriores | 229 nomes MCP não equivalem a 229 ferramentas testadas |
| Android | **PASS parcial** — Apktool 3.0.3 construiu e descodificou APK sintético; ferramentas Android privadas verificadas | ADB e instalação real em telemóvel permanecem sem teste físico |

**CAD/3D privado:** OpenSCAD/Blender e Office tiveram prova privada anterior à ativação [CAD](docs/CAD_PRIVADO_TESTE_MANUAL_20261105.md); o deploy e Skill→ZIP foram concluídos na [Fase 5](docs/CERTIFICACAO_FASE5_20261105.md).

**Limites externos não bloqueantes:** dispositivo Android físico, Penpot sem instalação operacional, ComfyUI sem modelos, GUI totalmente interativa, fornecedores pagos e Hopper em modo de demonstração. Estas capacidades não recebem certificação por associação às ferramentas instaladas.


**Certificadas em casos concretos:** Calibre EPUB, Darktable TIFF, GIMP XCF, Krita PNG, Scribus PDF/SLA (fase 2), LMMS WAV audível (fase 3) e ferramentas de dados/documentos anteriores. Testes reais pela Skill registados no [plano faseado](docs/PLANO_INTEGRACAO_55_PROGRAMAS_20261103.md). REA MCP executou várias chamadas tipadas (ELF, Apktool, captura de processo e doctor), sem demonstrar integralmente as 229 ferramentas.

**Vídeo certificado em caso real:** MLT/Kdenlive → MP4 pela Skill [#41992064762](https://github.com/martaxi-boss/VPS/actions/runs/41992064762), com `response.zip`, MP4 H.264 320×180, 2,005 s, codec áudio AAC e validação `ffprobe`. O teste prova uma composição MLT sintética, não todos os projetos de edição profissional.

**Pendentes de prova de produto final:** aplicações GUI totalmente interativas; ComfyUI CPU sem modelos; Penpot sem Docker operacional; dispositivo físico para ADB; funções pagas da demonstração do Hopper. O branch PR [#43](https://github.com/martaxi-boss/skill-universal/pull/43) permanece aberto e deve ser reavaliado contra as funções Calibre/Darktable já certificadas antes de qualquer merge.

**Ponte pinada:** o validador histórico rejeita kind=invoke de alguns IDs Android introduzidos depois. kind=auto com Zipalign devolveu ZIP real [#41856969562](https://github.com/martaxi-boss/VPS/actions/runs/41856969562). Não corrigir por alterações silenciosas da ligação SSH.

