# Transporte de pedidos Ferrari: ChatGPT → GitHub → VPS → ZIP

**Repositórios:** motor `martaxi-boss/skill-universal`, ponte `martaxi-boss/VPS`. O workflow dedicado `.github/workflows/ferrari-skill-request.yml` reage na `main` a **um novo ficheiro** `ferrari-requests/job-<identificador>.json`. Esta ponte usa o SSH existente; lógica de execução em `engine/skill_job.py`. Não alterar outros projetos.

## Como chamar

1. Confirmar o conector GitHub autenticado com acesso de escrita a `martaxi-boss/VPS`. Descobrir a operação da ferramenta GitHub compatível com **criar ficheiro** (ex.: `mcp__GitHub__create_file`). Não presumir SSH do cliente.
2. Criar **um único JSON novo por commit**, sem alterar/reutilizar pedidos. O nome do ficheiro precisa corresponder a `ferrari-requests/job-[a-z0-9-]{8,70}.json`.
3. Guardar o SHA do commit. Procurar a execução de workflow `Ferrari Skill - authenticated request delivery` com o mesmo `head_sha` no repositório `VPS`.
4. Confirmar `FERRARI_SKILL_JOB_STATUS=completed`, `FERRARI_SKILL_END_TO_END=PASS` e obter `ferrari-skill-result-<run_id>` pelas ferramentas GitHub de artefactos. O arquivo de GitHub contém `ferrari-response.zip`, que por sua vez contém `report.json` e `artifacts/`.
5. Verificar `status=completed` no relatório e a existência real dos ficheiros. Entregar o ficheiro no chat quando o ambiente permitir; caso contrário, indicar a execução exata.

## Exemplos de formato JSON

Inventário, sem input:

```json
{"version":1,"id":"inventory-20261102-0008","kind":"inventory"}
```

Operação de cartaz SVG:

```json
{"version":1,"id":"poster-20261102-0009","kind":"operation","operation":"svg-poster","title":"Cartaz Ferrari"}
```

Executar uma ação tipada com ficheiro, `file-mime`:

```json
{"version":1,"id":"mime-20261102-0010","kind":"invoke","action":"file-mime","input":{"name":"exemplo.json","content_base64":"e30K"}}
```

Escolha automática de adaptador conforme o pedido:

```json
{"version":1,"id":"auto-20261102-0011","kind":"auto","request":"Converter markdown para docx","input":{"name":"documento.md","content_base64":"IyBOb3ZhIHBhZ2luYQo="}}
```

O valor base64 é o conteúdo do ficheiro e **não é cifragem**. Tamanho atual do ficheiro codificado: entrada até ~2 MB. Operações base: `web-template`, `svg-poster`, `pdf-text`, `image-resize`, `video-thumbnail`, `apk-decompile`, `binary-strings`, `cad-stl`, `blender-house`, `office-pdf`, **`ifc-summary`** (entrada `.ifc`, relatório JSON) e **`vite-build`** (entrada `.zip`, distribuição estática; com Chromium isolado operacional devolve também `browser-check.json` e screenshot PNG). Algumas requerem input. Ações extras constam em `engine/tool_actions.json`. O protocolo remoto atual não suporta DAG arbitrário.

## Certificação web mais recente — 03/11/2026

- [VPS #41560720430](https://github.com/martaxi-boss/VPS/actions/runs/41560720430): SUCCESS, **99 testes PASS**, Chromium headless 156.0.8078.4, Playwright 1.64.1, `FERRARI_VITE_BROWSER_REAL=PASS`.
- [Skill Vite + browser #41560954411](https://github.com/martaxi-boss/VPS/actions/runs/41560954411): SUCCESS, `FERRARI_SKILL_END_TO_END=PASS`, ZIP verificado com HTML, JS, CSS, `browser-check.json` e `browser-screenshot.png` (PNG de 15 875 bytes); JS executado e zero erros.
- Inventário: **23/56** selecionados detetados, 49 programas combinados, **12 operações base** e 21 ações externas. A mesma operação `vite-build` executa o teste web adicional; sem outra Skill.
- Falha inicial [#41560226160](https://github.com/martaxi-boss/VPS/actions/runs/41560226160) corrigida na PR #7: usar o executável headless, não o Chromium completo. A higienização excluiu apenas antigas releases do Ferrari.

Para verificar um site pela Skill, utilizar exatamente o mesmo envelope `kind=operation`, `operation=vite-build` e um `input` ZIP limitado a `index.html`, `src/` e `public/`. Não são aceites scripts de instalação, Vite configs externas nem backend arbitrário. O ZIP de resposta inclui `artifacts/browser-check.json` e `artifacts/browser-screenshot.png` somente quando o navegador esteve operacional.

## Histórico — início de 03/11/2026

- **Motor VPS:** [#41556114851](https://github.com/martaxi-boss/VPS/actions/runs/41556114851) SUCCESS, 87 testes PASS, IfcOpenShell e Vite testados com ficheiros reais.
- **Skill IFC:** [#41556384002](https://github.com/martaxi-boss/VPS/actions/runs/41556384002) SUCCESS, `ifc-report.json` inspecionado (IFC4, 1 projecto e 1 parede).
- **Skill Vite:** [#41556406846](https://github.com/martaxi-boss/VPS/actions/runs/41556406846) SUCCESS, `dist/index.html`, CSS e JavaScript verificados.
- **Skill inventário:** [#41556541593](https://github.com/martaxi-boss/VPS/actions/runs/41556541593) SUCCESS, 22/56 selecionados detetados; 48 em catálogos combinados. Ações externas: 21; operações base: 12.

**As duas operações novas usam o mesmo pedido existente `kind=operation`.** Exemplos de campos: `{"kind":"operation","operation":"ifc-summary","input":{"name":"modelo.ifc","content_base64":"..."}}` e `{"kind":"operation","operation":"vite-build","input":{"name":"site.zip","content_base64":"..."}}`; incluem também `version=1` e `id` único. A origem deve ser não confidencial. Não aceitar ZIP com scripts de instalação, configurações Vite do utilizador ou caminhos fora de `index.html`, `src/` e `public/`.

## Provas e visibilidade

- Deploy motor: [#41546722719](https://github.com/martaxi-boss/VPS/actions/runs/41546722719), 68 testes PASS.
- Cartaz SVG: [#41546901101](https://github.com/martaxi-boss/VPS/actions/runs/41546901101), SUCCESS com ZIP.
- Markdown → DOCX: [#41547060999](https://github.com/martaxi-boss/VPS/actions/runs/41547060999), SUCCESS com ZIP.

Os repositórios são públicos. Certificar a propriedade posteriormente **não** torna privados os commits. Não enviar dados confidenciais neste canal; usar transporte privado se necessário.
