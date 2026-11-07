# Protocolos por domínio do Motor Ferrari

Esta referência complementa a **única Skill Universal**. Uma ferramenta Ubuntu é selecionada por capacidade, disponibilidade e teste; não por popularidade.

| Domínio | Programas possíveis | Tipo de prova necessária |
|---|---|---|
| Websites e aplicações | Vite, Next.js, Playwright, Tailwind | Build, captura no navegador, frontend e backend testados separadamente |
| Imagem e vetores | ImageMagick, libvips, GIMP, Krita, Inkscape | Ficheiro gerado, dimensões, exportação e inspeção |
| Vídeo e áudio | FFmpeg, Kdenlive, OpenShot, Audacity, Faster-Whisper | Codec, duração, saída e requisitos GUI/modelo |
| Documentos/PDF | Pandoc, LibreOffice, Tesseract, OCRmyPDF, Docling, Typst | PDF/DOCX real e leitura do conteúdo renderizado |
| CONSTRUÇÃO, CAD, BIM/IFC e 3D | Blender, OpenSCAD, IfcOpenShell, FreeCAD, LibreCAD, QGIS | Abertura/exportação de modelos e validação de formato/limites estruturais |
| Engenharia reversa autorizada | REA próprio Ferrari, Ghidra, JADX, Apktool 3.0.3, radare2, Binwalk | Executor, versões, proveniência, análise real e artefacto correspondente |
| Dados e automação | DuckDB, Polars, Streamlit, Prefect, Ruflo opcional | Validação de dados e execução tipada real, sem confundir CLI --help com fluxo funcional |
| IA local | ComfyUI CPU, outros só se houver recursos | Modelos presentes e inferência real certificada; não presumir GPU |

Instalação não garante que o programa possa ser controlado pelo Ferrari. O estado real está em BOOTSTRAP.md e na fonte persistente única `engine/catalog.json`, nos executores `engine/ferrari.py` e `engine/tool_runtime.py` e no inventário real devolvido pela Skill (`kind=inventory`). `engine/catalog_registry.py` fornece vistas derivadas, não outro catálogo.

## Roteamento

1. Compreender entrada, objetivo, formato e recursos Ubuntu.
2. Consultar inventário Ferrari real (kind=inventory via Skill ou ferramenta local autorizada).
3. Escolher operação base ou ação tipada; para trabalho composto escolher kind=plan ou engine.orchestrator.
4. Confirmar que o executável, bibliotecas e fornecedores necessários estão instalados; se não estiverem, reportar e propor integração, nunca simular.
5. Validar saída, executores efetivos, erros e relatório ZIP.
6. Se faltar capacidade, analisar licenças de upstream, ferramentas headless, RAM, SSD, GPU e privacidade antes de instalar ou executar.

**Não criar camadas adicionais, Skills paralelas, nem assumir que programas pagos estão disponíveis gratuitamente.** Não utilizar o outro projeto REA da VPS como fallback. Para REA Ferrari, conferir sempre o runtime privado de Node e Apktool.

O plano remoto kind=plan já foi comprovado em [run #41620077416](https://github.com/martaxi-boss/VPS/actions/runs/41620077416); a integração de capacidades específicas continua incremental e deve ser demonstrada por ferramentas reais na VPS.
