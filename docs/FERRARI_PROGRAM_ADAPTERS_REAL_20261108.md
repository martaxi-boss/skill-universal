# Ferrari: adaptadores de programas — prova real e fila restante (08/11/2026)

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

## Fila de trabalho — restantes 21 instalados sem adaptador direto

O inventário original incluía 24 `installed_unintegrated`. Três passam a chamar estas operações reais. Os restantes **21 não são necessariamente avarias nem precisam todos de botão próprio**: é preciso separar os executores dos componentes de suporte. A próxima ação deverá demonstrar um trabalho útil, produzir artefacto verificável e executar nas dependências privadas, nunca promover um `--version` a certificação.

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

**Não marcar os 21 como concluídos enquanto não existirem provas equivalentes às três acima.** A classificação é *papel técnico*, não autorização para transferir dados privados ou usar redes externas.

## Nota de segurança e rollback

O transporte por GitHub é público; usar apenas entradas sintéticas ou autorizadas sem credenciais. A release é imutável por SHA, executa no projeto `/srv/projects/skill-universal` e tem fallback preservado. A Skill cliente ChatGPT deve atualizar o **mesmo plugin instalado**; não criar nem instalar um plugin com identidade diferente.
