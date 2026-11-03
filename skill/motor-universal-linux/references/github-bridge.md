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

Plano com etapas dependentes, usando o **orquestrador Ferrari que ja existe**, sem Skill nem ponte nova (disponivel somente quando a release com suporte `kind=plan` estiver implantada e certificada):

```json
{"version":1,"id":"plan-20261103-001","kind":"plan","max_parallel":2,"plan":{"version":1,"steps":[{"id":"site","operation":"web-template","layout":"store","title":"Montra Ferrari"},{"id":"analise","operation":"binary-strings","depends_on":["site"],"input_from":"site"}]}}
```

Para um plano que recebe um unico ficheiro, usar o `input` base64 de topo e `"input":"$input"` no passo correspondente; para consumir resultado de passo anterior usar `depends_on` e `input_from`. O Ferrari valida e executa o plano diretamente no motor, devolvendo artefactos de cada passo e relatorio do orquestrador no ZIP. **Nao passar caminhos absolutos/relativos da VPS no plano remoto.** Se um passo falhar o resultado nao pode ser declarado PASS. O CI isolado, por si, nao certifica a ligacao remota.

O valor base64 é o conteúdo do ficheiro e **não é cifragem**. Tamanho atual do ficheiro codificado: entrada até ~2 MB. Operações base: `web-template`, `svg-poster`, `pdf-text`, `image-resize`, `video-thumbnail`, `apk-decompile`, `binary-strings`, `cad-stl`, `blender-house`, `office-pdf`, **`ifc-summary`** (entrada `.ifc`, relatório JSON) e **`vite-build`** (entrada `.zip`, distribuição estática; com Chromium Ferrari operacional devolve `browser-check.json` com testes de teclado opt-in, `browser-screenshot.png` e `browser-mobile.png`). Algumas requerem input. Ações extras constam em `engine/tool_actions.json`. A release atualmente instalada na VPS ainda nao suporta DAG remoto. O novo `kind=plan` desta fase deve ser usado apenas depois de testes CI, entrega na VPS e teste fim-a-fim confirmados.

## Certificação web mais recente — 03/11/2026

- [Ferrari VPS #41598711120](https://github.com/martaxi-boss/VPS/actions/runs/41598711120): SUCCESS, **99 testes PASS**, `FERRARI_BROWSER_KEYBOARD_REAL=PASS`, `FERRARI_BROWSER_INTERACTIVE_CONTROLS_REAL=PASS`; Vite, Chromium, mobile, HTML spotcheck e IFC mantiveram PASS.
- [Skill `vite-build` #41598946695](https://github.com/martaxi-boss/VPS/actions/runs/41598946695): SUCCESS e `FERRARI_SKILL_END_TO_END=PASS`. ZIP aberto com `report.json`, HTML/CSS/JS e `artifacts/browser-check.json`, `artifacts/browser-screenshot.png` (51 916 bytes), `artifacts/browser-mobile.png` (52 507 bytes). Chromium real testou 4 elementos focáveis, Tab, Shift+Tab, botão Enter/Espaço, link e formulário Enter — todos PASS no exemplo.
- **Versão atual VPS:** `9277a56b9b57c87b8b4e3dfbba08f4536add3625`. Higienização preservou a anterior certificada `0196f37a...` e removeu outra release antiga, libertando 2,40 MiB, sem tocar em projetos externos.
- **Inventário estável:** 23/56 candidatos Ubuntu detetados, 49 programas combinados, **12 operações base**, 21 ações externas. Sem programa, Skill, operação ou ponte nova.

**Envelope inalterado:** `{"version":1,"id":"id-unico","kind":"operation","operation":"vite-build","input":{"name":"site.zip","content_base64":"..."}}`. Só ZIP não confidencial com `index.html`, `src/` e `public/`, sem scripts de instalação ou config Vite externa. O relatório `artifacts/browser-check.json` inclui `interactions`: foco `Tab`/`Shift+Tab` e ações com `Enter`/`Space` apenas quando o site declara `data-ferrari-test="button"`, `"link"` e `"form"`. Sem marcadores os campos dizem `not_requested` — **nunca afirmar que todos os botões de um site foram testados**. O motor não executa ações arbitrárias em produção.

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
