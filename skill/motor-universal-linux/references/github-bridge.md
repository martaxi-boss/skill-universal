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

O valor base64 é o conteúdo do ficheiro e **não é cifragem**. Tamanho atual do ficheiro codificado: entrada até ~2 MB. Operações base: `web-template`, `svg-poster`, `pdf-text`, `image-resize`, `video-thumbnail`, `apk-decompile`, `binary-strings`, `cad-stl`, `blender-house`, `office-pdf`, **`ifc-summary`** (entrada `.ifc`, relatório JSON) e **`vite-build`** (entrada `.zip`, distribuição estática; com Chromium Ferrari operacional devolve `browser-check.json`, `browser-screenshot.png` e `browser-mobile.png`). Algumas requerem input. Ações extras constam em `engine/tool_actions.json`. O protocolo remoto atual não suporta DAG arbitrário.

## Certificação web mais recente — 03/11/2026

- [Motor VPS #41561998389](https://github.com/martaxi-boss/VPS/actions/runs/41561998389): SUCCESS, **99 testes PASS**, `FERRARI_VITE_RESPONSIVE_REAL=PASS` e `FERRARI_BROWSER_A11Y_SPOTCHECK_REAL=PASS`. Sem instalação adicional além do Chromium já presente.
- [Skill Vite desktop/móvel #41562205411](https://github.com/martaxi-boss/VPS/actions/runs/41562205411): SUCCESS, ZIP inspecionado com `browser-check.json`, `browser-screenshot.png` (1280×720), `browser-mobile.png` (390×844) e HTML, CSS e JS compilados. No exemplo: overflow=0 px, HTML `lang=pt`, zero erros da página ou avisos pontuais de etiquetas. **Não** implica certificação WCAG ou emulação de Android.
- **Versão ativa:** `0196f37a7610d1f95cd3371652308b7e2244f019`, anterior certificada `13c439925...` como recuperação. Higienização Ferrari PASS, 2,37 MiB libertados, nenhuma pasta externa alterada.
- **Inventário:** 23/56 candidatos Ubuntu detetados, 49 ferramentas nos catálogos combinados; 12 operações base e 21 ações externas.

**Envelope inalterado:** `{"version":1,"id":"nome-unico","kind":"operation","operation":"vite-build","input":{"name":"site.zip","content_base64":"..."}}`. Enviar só ZIP não confidencial com `index.html`, `src/` e `public/`. O ZIP de resposta inclui `artifacts/browser-mobile.png` e `artifacts/browser-check.json` somente após a execução efetiva do navegador. Se o site apresentar problemas básicos de acessibilidade, o campo `mobile.findings` lista avisos — o motor não corrige automaticamente conteúdo do utilizador.

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
