# Ferrari: adaptadores de programas — prova real e fila restante (08/11/2026)

## Auditoria final da segunda vaga — inventário corrigido

- **Release ativa** `cde16ce5debfbd247decac800ce47bfeed36adaa`; **fallback** `a44bebc0018dec38f659a8ed859e92ba0522c365`. [Pré-teste protegido #42497258398](https://github.com/martaxi-boss/VPS/actions/runs/42497258398) **PASS** sem alterar produção; [ativação #42497376684](https://github.com/martaxi-boss/VPS/actions/runs/42497376684) **PASS**, com **525 testes**, 40 ações e 8 serviços, Docling/Valkey reais e leitura da release+rollback.
- A correção da deteção de Docling instalado como *módulo Python* passou o teste de regressão, e a VPS confirmou `FERRARI_PRIVATE_DOCLING_INVENTORY_CALLABLE=PASS`; não foi instalada segunda cópia do programa.
- [Auditoria Skill→GitHub→VPS→ZIP #42497575120](https://github.com/martaxi-boss/VPS/actions/runs/42497575120) **completed**: catálogo universal **173 programas + 279 funções + 3 dependências + 2 fornecedores = 457 entradas**, 73 programas detectados, **50 callable**, **19 installed_unintegrated**, 34 not_detected, 67 candidatos não admitidos e 3 runtimes verificados. O relatório de inventário foi pedido sem *acceptance* específica, pelo que o `quality_gate` é `not_certified`; o próprio JSON e os estados foram lidos e comparados independentemente. Não confundir um inventário válido com certificação semântica de cada programa.
- Skill cliente v1.0.13 é **atualização in-place da identidade workspace original**, não nova Skill. Restantes 19 devem ser integrados só com ações concretas, ou reconhecidos como bibliotecas/serviços usados indiretamente quando houver prova.



## Segunda vaga certificada — Docling e Valkey (08/11/2026)

- **Ferrari ativo:** `a44bebc0018dec38f659a8ed859e92ba0522c365`; fallback imediato `df0ac55dcb93003ea672abaa5deba8ea9e49ebe8`. **Um catálogo:** 173 programas, 279 funções (19 operações + 40 ações + 220 REA), 3 dependências e 2 fornecedores = **457 entradas**, sem duplicar ferramentas ou Python.
- [Precheck VPS #42495918959](https://github.com/martaxi-boss/VPS/actions/runs/42495918959) **PASS:** 524 testes, 40/40 ações, 8/8 serviços, conversão de DOCX sintético em Markdown com Docling privado e prova PING/SET/GET/DEL Valkey em socket UNIX transitório; *não ativou a release*.
- [Ativação VPS #42496077967](https://github.com/martaxi-boss/VPS/actions/runs/42496077967) **PASS:** dois ciclos dos mesmos ensaios reais, readback do release SHA e fallback intacto, 8/8 serviços protegidos.
- [Skill→ZIP Docling #42496314303](https://github.com/martaxi-boss/VPS/actions/runs/42496314303) **PASS:** DOCX original de teste → `docling-extracted.md` com o texto original, `docling-report.json`, SHA256 igual ao Markdown efetivo, `quality_gate=passed`. **Não comprova OCR, PDF complexo nem interpretação perfeita.**
- [Skill→ZIP Valkey #42496444032](https://github.com/martaxi-boss/VPS/actions/runs/42496444032) **PASS:** `valkey-kv-report.json` prova PONG, SET=OK, GET original, DEL=1, GET após DEL vazio e limpeza obrigatória. **Não prova cache em produção, desempenho nem persistência.**
- **Contratos:** `kind=operation`, `operation=docling-docx-markdown` e `input.name=documento.docx` + `input.content_base64` até 2 MB geram Markdown e JSON; `operation=valkey-kv-test` não exige input e devolve apenas JSON. Usar exclusivamente material sintético/autorizado no GitHub público, sem dados pessoais. Dependências permanecem dentro de `/srv/projects/skill-universal`, sem instalações APT.
- **Saldo de integração:** dos 24 programas sem operação direta na auditoria inicial, **5 ganharam ações reais**: LibreCAD, QGIS, Godot, Docling, Valkey. **Restam 19 sem operação direta**, dos quais alguns são dependências ou já trabalham indiretamente via Playwright, REA/Ghidra e Ruflo anfitrião. Não inventar botões/funções duplicados só para reduzir a contagem.

## Primeira vaga — registo histórico anterior (455 entradas)


## Estado certificado — sem multiplicar motores ou catálogos

- **Ferrari ativo na VPS:** `df0ac55dcb93003ea672abaa5deba8ea9e49ebe8`; fallback preservado `46b679f4304454e28a23aa779507af393f0c5258`.
- **Um catálogo universal:** 173 programas, 277 funções (17 operações de base + 40 ações privadas + 220 REA), 3 dependências e 2 fornecedores: **455 entradas**. As 40 ações existentes não foram alteradas.
- **CI código:** [#42494308939](https://github.com/martaxi-boss/skill-universal/actions/runs/42494308939) PASS.
- **Pré-teste real VPS:** [#42494546784](https://github.com/martaxi-boss/VPS/actions/runs/42494546784) PASS; 517 regressões, 40/40 ações, **LibreCAD/QGIS/Godot três operações reais** e 8/8 serviços protegidos. Sem alterar a release ativa.
- **Ativação protegida:** [#42494657940](https://github.com/martaxi-boss/VPS/actions/runs/42494657940) PASS; repetição dos três testes antes e durante ativação, readback de SHA e fallback, 8/8 serviços protegidos.
- **Skill→GitHub→VPS→ZIP independente:** LibreCAD [#42494871444](https://github.com/martaxi-boss/VPS/actions/runs/42494871444) PASS (PDF real de 1 página, Poppler privado, SHA256, quality_gate=passed); Godot [#42494878696](https://github.com/martaxi-boss/VPS/actions/runs/42494878696) PASS (project.godot e main.tscn, motor headless exit 0, technical gate passed); QGIS [#42494978167](https://github.com/martaxi-boss/VPS/actions/runs/42494978167) PASS (GeoJSON MultiPolygon real, native:buffer 5 m, área 5000→6578.316 m², hash e quality_gate=passed).
- A primeira ronda de pré-testes [#42493814551](https://github.com/martaxi-boss/VPS/actions/runs/42493814551) detetou symlink interno AppImage LibreCAD; a segunda [#42494170315](https://github.com/martaxi-boss/VPS/actions/runs/42494170315) identificou o MultiPolygon QGIS. Ambas falharam com produção intacta. As [PR #158](https://github.com/martaxi-boss/skill-universal/pull/158) e [#159](https://github.com/martaxi-boss/skill-universal/pull/159) corrigiram as causas reais sem enfraquecer os limites privados.

## Contratos operacionais integrados

| Programa | Operação Ferrari | Entrada | Saída real e limite |
|---|---|---|---|
| LibreCAD | `librecad-dxf-pdf` | DXF ASCII autorizado até 2 MB | `librecad-drawing.pdf`, `librecad-report.json`; PDF validado com Poppler, não certifica editor GUI |
| QGIS | `qgis-buffer-5m` | Um polígono GeoJSON EPSG:3857 até 2 MB | `qgis-buffer-5m.geojson`, `qgis-buffer-report.json`; compara geometria/área, não certifica mapa cartográfico ou OGR externo |
| Godot | `godot-starter` | Sem ficheiro (gera exemplo próprio) | `project.godot`, `main.tscn`, relatório; parse pelo motor real, não certifica jogo final nem export templates |

São operações no `engine/catalog.json` e `engine/ferrari.py`, com adaptadores privados `engine/program_adapters.py` e o **mesmo** job `kind=operation`. Sem daemon, outra Skill, segundo catálogo, aplicação global nem alteração dos projetos vizinhos. A qualidade editorial/comercial e operações GUI complexas continuam fora destas provas.

## Fila histórica de 21 após primeira vaga — 19 ainda pendentes de operação direta

O inventário original incluía 24 `installed_unintegrated`. Três foram ligados na primeira vaga e Docling/Valkey na segunda. Os restantes **19 não são necessariamente avarias nem precisam todos de botão próprio**: é preciso separar os executores dos componentes de suporte. A próxima ação deverá demonstrar um trabalho útil, produzir artefacto verificável e executar nas dependências privadas, nunca promover um `--version` a certificação.

| Programa | Papel a esclarecer e prova exigida antes de `callable` |
|---|---|
| yt-dlp | Descarga/extracção de media autorizado, com domínio permitido, limites e hash do ficheiro |
| Prometheus | Serviço de métricas: consulta segura, sem iniciar daemon global |
| Valkey | Serviço de cache: operação efémera no socket privado e persistência/limpeza verificadas |
| FreeCAD | CAD 3D: ficheiro STEP válido, conversão/importação e inspeção geométrica |
| Audacity | Edição áudio: efeito exportado e comparativo de sinal, sem GUI residente |
| OBS | Captura local autorizada: vídeo verificável e sem transmissão/streaming inadvertido |
| SolveSpace | CAD paramétrico: modelo/sistema de restrições e saída medida |
| Synfig | Animação: projeto original e render real, sem exportações falsas |
| OpenShot | Vídeo: timeline, render e duração conferida por FFprobe |
| Ghidra | REA já pode invocar funções relacionadas; decidir apenas se justifica rota standalone, com binário de teste autorizado |
| Ruflo | Coordenação por rondas já integrada; **não** confundir com autonomia LLM de agentes sem anfitrião |
| ComfyUI | Workflow local verificado se pesos/modelos livres necessários estiverem disponíveis; zero serviços residentes |
| Next.js | Framework de frontend; demonstração de build e página funcional, não obrigação de comando direto separado |
| Tailwind CSS | Dependência CSS: build de classes no projeto web real |
| Bootstrap | Dependência UI: assets compilados no projeto real |
| Playwright | Suporte ao browser-check já existe; rever papel e classificação antes de duplicar chamadas |
| shadcn/ui | Componentes de UI: integração/compilação de projeto real |
| Docling | Extração estruturada PDF, validação de conteúdo e OCR quando aplicável |
| Streamlit | Projeto/app efémera com screenshots e encerramento do serviço |
| Gradio | Interface efémera com resposta testada e sem daemon sobrevivente |
| Prefect | Workflow/scheduler: DAG em processo efémero, estado e saída verificados |

**Não marcar os 19 restantes como concluídos enquanto não existirem provas específicas e relevantes.** A classificação é *papel técnico*, não autorização para transferir dados privados ou usar redes externas.

## Nota de segurança e rollback

O transporte por GitHub é público; usar apenas entradas sintéticas ou autorizadas sem credenciais. A release é imutável por SHA, executa no projeto `/srv/projects/skill-universal` e tem fallback preservado. A Skill cliente ChatGPT deve atualizar o **mesmo plugin instalado**; não criar nem instalar um plugin com identidade diferente.
