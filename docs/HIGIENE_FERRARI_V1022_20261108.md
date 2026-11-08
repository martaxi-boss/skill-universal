# Higienização pontual Ferrari, VPS, GitHub e Skill — 08/11/2026

## Objetivo e limites

Auditoria e reconciliação da MESMA Skill `motor-universal-linux` e do único Ferrari privado. Nenhum programa instalado globalmente, nova ponte SSH, serviço de LLM residente, segundo catálogo, segunda Skill ou alteração a outros projetos. Operações documentadas de forma reprodutível; nenhuma limpeza em massa de branches/release sem prova de dependências e rollback.

## 1 — VPS auditada ao vivo

- [Auditoria existente e segura de sete caches #42530304058](https://github.com/martaxi-boss/VPS/actions/runs/42530304058), iniciada pelo [pedido Owner #416](https://github.com/martaxi-boss/VPS/issues/416): `AUDIT_ONLY`, 7 roots, 0 ficheiros elegíveis, 0 bytes eliminados, `protected_services_unchanged=true`, `health_after=true`, `app_or_database_data_deleted=0`. Não executar `clean` sem candidatos.
- [Inventário novo via ponte autenticada #42530379999](https://github.com/martaxi-boss/VPS/actions/runs/42530379999): `report.json.status=completed`, `response.zip`, `artifacts/inventory.json`, `artifacts/catalog.json`; 173 programas no catálogo, 73 detetados agora, 51 diretamente invocáveis, 55/55 selecionados detetados, 280/280 funções selecionáveis, 40/40 ações disponíveis, 458 entradas, 220 funções REA. `quality_gate=not_certified` em inventário, pois não constitui certificação funcional das 458 entradas.
- A ativação protegida previamente certificada [#42526288787](https://github.com/martaxi-boss/VPS/actions/runs/42526288787) fixou `current=046126279a605d331b95683ece0a26d3c464d0eb`, `fallback=3f0ba44b7d8475a74a63c6010d1e27063c04bf1e` e 8/8 serviços. Esta auditoria não alterou as releases nem reconfirmou por SSH o link `current` neste momento.

## 2 — Ruflo e Ferrari em operação verdadeira

Missão com anfitrião ChatGPT, três papéis efémeros Ruflo, duas tarefas dependentes, revisão por papel diferente e conclusão:

1. [Criar equipa #42529223723](https://github.com/martaxi-boss/VPS/actions/runs/42529223723).
2. [Gerar CAD pela operação privada Ferrari dentro do Ruflo #42529278092](https://github.com/martaxi-boss/VPS/actions/runs/42529278092).
3. [Revisão geométrica com SHA real #42529365806](https://github.com/martaxi-boss/VPS/actions/runs/42529365806).
4. [Chamar `file-mime` no STL aprovado #42529435760](https://github.com/martaxi-boss/VPS/actions/runs/42529435760).
5. [Revisão da detecção MIME #42529508788](https://github.com/martaxi-boss/VPS/actions/runs/42529508788).
6. [Aprovação da IA anfitriã / fecho #42529577832](https://github.com/martaxi-boss/VPS/actions/runs/42529577832).

STL **ASCII** de 46×34×9 mm com 2 furos de 6 mm, malha fechada, 788 triângulos, SHA-256 `3442660252051692b2956c180b7bb16dfe7009ce181c38f734b3cef7a23a9449`. A deteção `text/plain` pelo `file-mime` foi correta para STL ASCII. Duas chamadas Ferrari verificadas e duas aprovações do papel distinto. Revisão por função não implica segundo modelo independente. Nenhuma inferência LLM automática pela VPS; por contrato a IA anfitriã fornece o raciocínio.

## 3 — Higiene do transporte GitHub

[Commit VPS a6011b9](https://github.com/martaxi-boss/VPS/commit/a6011b9fd87a9ed6ddc756b616df50025048a8c4): exatamente 11 pedidos de certificação/inventário já concluídos retirados da árvore `main` numa só revisão. De 159 para 148 envelopes `ferrari-requests` no HEAD. A eliminação do HEAD não apaga o histórico Git, e os runs de prova mantêm os links. O workflow original `Ferrari Skill - authenticated request delivery` continua intacto e rejeita alterações apenas de remoção como trabalhos executáveis.

Branches e outros pedidos antigos permanecem para auditoria individual; não afirmar que 148 pedidos estão todos prontos a apagar. O apagamento de caches foi dispensado por ausência de candidatos.

## 4 — Código, empacotamento e Skill

Fonte Ferrari mantida em `martaxi-boss/skill-universal`. Ajustar versão `1.0.22` no `packaging/motor-ferrari/plugin.json`, `SKILL.md`, referências de bootstrap e ponte, `BOOTSTRAP.md` canónico e README. Substituir nove links `../../docs` / `../../../docs` inválidos quando instalados como plugin por URLs canónicos do GitHub. Preservar todas as nove referências internas existentes e instruções de utilização; não criar skill nova. Distribuir a mesma identidade [Plugin_b62aaa180b308191b124269fd0acbf9d](https://chatgpt.com/plugins/Plugin_b62aaa180b308191b124269fd0acbf9d); confirmar `version` e release após a atualização no ChatGPT.

## Restrições de aceitação

- `Actions success` sozinho não prova execução; exigir `response.zip`, `report.json` e conteúdo real.
- `quality_gate=not_certified` nunca deve ser convertido em `passed` apenas porque o teste de geometria foi aprovado.
- A certificação é de 2 ferramentas ensaiadas, não de 458 entradas completas.
- Preservar release ativa, fallback, serviços, credenciais, tarefas de outros projetos, logs probatórios e histórico Git.
