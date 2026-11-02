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

O valor base64 é o conteúdo do ficheiro e **não é cifragem**. Tamanho atual do ficheiro codificado: entrada até ~2 MB. Operações base: `web-template`, `svg-poster`, `pdf-text`, `image-resize`, `video-thumbnail`, `apk-decompile`, `binary-strings`, `cad-stl`, `blender-house`, `office-pdf`; algumas requerem input. Ações extras constam em `engine/tool_actions.json`. O protocolo remoto atual não suporta DAG arbitrário.

## Provas e visibilidade

- Deploy motor: [#41546722719](https://github.com/martaxi-boss/VPS/actions/runs/41546722719), 68 testes PASS.
- Cartaz SVG: [#41546901101](https://github.com/martaxi-boss/VPS/actions/runs/41546901101), SUCCESS com ZIP.
- Markdown → DOCX: [#41547060999](https://github.com/martaxi-boss/VPS/actions/runs/41547060999), SUCCESS com ZIP.

Os repositórios são públicos. Certificar a propriedade posteriormente **não** torna privados os commits. Não enviar dados confidenciais neste canal; usar transporte privado se necessário.
