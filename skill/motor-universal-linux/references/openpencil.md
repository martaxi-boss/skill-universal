# OpenPencil — design HTML através da Skill Ferrari já existente

Usar apenas depois de confirmar no BOOTSTRAP que a release Ferrari ativa contém o modo privado. **Não** criar uma Skill, workflow, bridge ou ação tipada nova. O validador do transporte permanece pinado; a operação existente `web-template` tem um **modo opcional com ficheiro HTML**, sem alterar o comportamento dos pedidos sem `input`.

## Entrada

Enviar `kind=operation`, `operation=web-template`, `layout=store` e `input={name,content_base64}`, onde `name` termina em `.html` ou `.htm` e o conteúdo é HTML completo. Para o transporte via GitHub público, usar somente HTML próprio e não confidencial, com estilos inline, até 600 KB; sem script, iframes, URLs de recursos remotos nem importação de CSS externo. A ponte já limita a entrada total a 2 MB. Não colocar credenciais, código proprietário ou dados pessoais no pedido.

Exemplo de pedido válido, usando HTML sintético (base64 completo gerado da string HTML de teste pelo chamador):

```json
{
  "version": 1,
  "id": "ferrari-openpencil-design-20261106",
  "kind": "operation",
  "operation": "web-template",
  "layout": "store",
  "input": {
    "name": "design.html",
    "content_base64": "PCFkb2N0eXBlIGh0bWw+PGh0bWj48Ym9keT48aDE+RmVycmFyaTwvaDE+PC9ib2R5PjwvaHRtbD4="
  }
}
```

O exemplo em base64 acima ilustra a estrutura: antes de um pedido real, gerar o base64 a partir do HTML completo pretendido. Validar localmente o ficheiro e não publicar conteúdo privado.

## Executor e saída

O Ferrari chama exclusivamente:

- `/srv/projects/skill-universal/runtimes/node-22.23.4/bin/node`
- `/srv/projects/skill-universal/.runtime/npm/openpencil/node_modules/@open-pencil/cli/bin/openpencil.js`

Importa HTML para `artifacts/design.fig`; gera `artifacts/design.svg`, `artifacts/design.html` standalone e `artifacts/design-info.json` com os metadados. Os ficheiros são devolvidos no `response.zip` e devem constar do `report.json` com `status=completed`. Falha fechada em ferramentas, versões ou ficheiros inválidos, sem fallback global, SSH extra ou alterações no servidor do site original.

O OpenPencil **não** melhora automaticamente o design por si só; transforma e exporta a estrutura enviada. Alterações estéticas posteriores podem ser feitas com propostas de CSS/layout, testadas numa cópia e implementadas separadamente no projeto do site.

## Certificação

Antes de anunciar `100%`, exigir GitHub Actions CI, ativação versionada e rollback disponível, pedido novo `ferrari-requests/job-<id>.json`, execução `ferrari-skill-request.yml` existente, estado `completed` e ZIP com `.fig`, `.svg` e `.html`. Não alterar o pin do validador, o SSH nem os outros projetos. A atualização da Skill instalada no cliente ChatGPT precisa de confirmação específica; um novo ZIP de CI não a instala automaticamente.
