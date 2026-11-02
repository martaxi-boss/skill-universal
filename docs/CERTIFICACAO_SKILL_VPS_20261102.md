# Certificação real da ponte da Skill Ferrari → VPS

**Data:** 2 de novembro de 2026. **Motores:** Ferrrari independente no Ubuntu 24.04, sem alterar o SSH partilhado.

## Entrega e testes da VPS

- **GitHub Actions [#41546722719](https://github.com/martaxi-boss/VPS/actions/runs/41546722719): SUCCESS**. Instalada a release `1ff6e472b5ea4eab95785be224155f400c51aeaa` do Motor Ferrari; **68 testes unitários PASS na VPS**, juntamente com os testes existentes CAD/3D/Office, Ghidra, programas externos.
- Foi criado apenas um novo workflow dedicado Ferrari, `martaxi-boss/VPS/.github/workflows/ferrari-skill-request.yml`, que reutiliza o segredo SSH existente e a mesma impressão digital do host. Nenhum dos outros workflows/Supervisor ou motores independentes foi alterado.
- O pedido é um ficheiro JSON novo criado pelo **conector GitHub autenticado** em `martaxi-boss/VPS/ferrari-requests/job-*.json`. Um evento `push` no ramo `main` chama GitHub Actions; `engine.skill_request_pick` valida o ficheiro e o transporte SSH copia para a VPS. A lógica de execução está exclusivamente em `engine.skill_job`. Cada execução devolve `response.zip` com `report.json` e `artifacts/`, publicado como artefacto da execução.

## Testes reais ponta a ponta

1. **[GitHub Actions #41546901101](https://github.com/martaxi-boss/VPS/actions/runs/41546901101) SUCCESS:** pedido simples `kind=operation`, operação `svg-poster`; na VPS `FERRARI_SKILL_JOB_STATUS=completed`; artefacto `ferrari-skill-result-41546901101` descarregado e inspecionado: ZIP interno contém `report.json` e `artifacts/creative/poster.svg`.
2. **[GitHub Actions #41547060999](https://github.com/martaxi-boss/VPS/actions/runs/41547060999) SUCCESS:** pedido `kind=auto`, conteúdo Markdown base64 não confidencial e instrução `Converter markdown para docx`. O Ferrari escolheu realmente `/usr/bin/pandoc`, gerou `artifacts/document.docx`, devolveu ZIP e `report.json` com `status=completed`. Ficheiro DOCX descarregado, extraído e verificado.

**Estado:** funcionamento ponta-a-ponta demonstrado para tarefas suportadas. A Skill tem instruções para o conector GitHub; para utilização no chat é necessário instalar/carregar o ZIP atualizado da Skill e ter GitHub ligado. Não confundir esta integração com integração profunda REA/Ruflo, BIM/FreeCAD, automação de *todas* as 56 ferramentas ou acesso a serviços pagos.

## Privacidade e limites de transporte

**Ambos os repositórios GitHub são públicos.** O pedido JSON fica visível publicamente e base64 não oculta informação. Os testes usaram exclusivamente conteúdo fictício. Nunca enviar neste canal segredos, dados privados ou documentos confidenciais; é necessário transporte privado para esses casos. Os ZIP de resultados ficam disponíveis nos artefactos de GitHub Actions pelo período configurado. O motor não permite comandos shell arbitrários enviados no pedido. A ponte serve exclusivamente para transporte e seleção do ficheiro de trabalho, não guarda lógica de ferramentas.
