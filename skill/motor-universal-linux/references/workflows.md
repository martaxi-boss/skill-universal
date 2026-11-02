# Fluxos e graus de comprovação do Ferrari

O ZIP contém instruções e não credenciais. **A ligação remota foi certificada para tarefas suportadas**, pelas execuções [#41546901101](https://github.com/martaxi-boss/VPS/actions/runs/41546901101) e [#41547060999](https://github.com/martaxi-boss/VPS/actions/runs/41547060999). Usar `references/github-bridge.md` para chamadas do ChatGPT à VPS.

## Estados

1. Catálogo: programa descoberto.
2. Ubuntu: instalação candidata compatível.
3. Binário: realmente detetado na VPS.
4. Adaptador: operação invocável pelo Ferrari.
5. Certificação: teste funcional PASS com ficheiro válido.
6. Remoto: chamada GitHub→VPS→ZIP confirmada para a tarefa.

Certificar observa se funciona; não é requisito para um binário aparecer no catálogo e ser descoberto. Uma certificação antiga não comprova versões novas.

## Exemplos

- Cartaz: `kind=operation`, `operation=svg-poster` → SVG verdadeiro (PASS).
- Markdown → Word: `kind=auto`, `request=Converter markdown para docx`, ficheiro `.md` codificado em base64 → Pandoc → DOCX (PASS).
- Inventário: `kind=inventory` → JSON sobre as ferramentas detetadas no momento, não lista de certificados.
- Loja web: `operation=web-template`, `layout=store` → template estático, não pagamentos reais.
- BIM ou tarefa complexa: confirmar dependências e adaptadores; sem prova real não declarar concluído.

O protocolo remoto atual não transporta automaticamente um DAG arbitrário; esse recurso requer uma extensão própria no Ferrari.
