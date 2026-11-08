# Ferrari + Ruflo — Certificação real da chamada CAD direta (08/11/2026)

## Estado operacional certificado

A release ativa do Ferrari foi comutada de `3f0ba44b7d8475a74a63c6010d1e27063c04bf1e` para
`046126279a605d331b95683ece0a26d3c464d0eb`; a release anterior permanece preservada
como fallback. Esta alteração implementa a invocação de operações **base** do catálogo
diretamente dentro das rondas `kind=ruflo-team`, além de `invoke` e `rea-mcp`.
As permissões explícitas dos papéis usam `operation:<id>` (ex.: `operation:cad-stl`),
sem shell arbitrária nem novos adaptadores, motores, Skill, daemons, modelos de agente ou
segundo catálogo. A IA anfitriã ChatGPT planeia e conduz as rondas.

O objetivo é corrigir a limitação identificada nos testes de dashboard e engenharia CAD:
as exportações CAD eram executadas separadamente e os papéis Ruflo apenas coordenavam
e reviam os resultados. **Esta certificação prova a ligação direta na operação `cad-stl`**,
não nas restantes 457 entradas do catálogo.

## Evidências ligadas ao GitHub Actions

| Etapa | Execução VPS | Resultado |
|---|---|---|
| Pré-teste remoto da nova release | [#42526150460](https://github.com/martaxi-boss/VPS/actions/runs/42526150460) | PASS, `current` preservado, 8/8 serviços |
| Ativação protegida | [#42526288787](https://github.com/martaxi-boss/VPS/actions/runs/42526288787) | PASS, release atual `0461262...`, fallback anterior preservado, 8/8 serviços |
| Criar equipa host-led | [#42526523928](https://github.com/martaxi-boss/VPS/actions/runs/42526523928) | PASS, `team_id=ruflo-cad-direct-20261108` |
| Invocar operação real dentro do Ruflo | [#42526587063](https://github.com/martaxi-boss/VPS/actions/runs/42526587063) | PASS, `verified_tool_events[0].catalog_action=operation:cad-stl` |
| Revisão por papel distinto | [#42526667840](https://github.com/martaxi-boss/VPS/actions/runs/42526667840) | PASS, SHA-256 ligado à evidência; tarefa aprovada |
| Fecho por IA anfitriã | [#42526730098](https://github.com/martaxi-boss/VPS/actions/runs/42526730098) | PASS, `ruflo-team-status.status=completed` |

Mudanças auditadas: [motor PR #179](https://github.com/martaxi-boss/skill-universal/pull/179),
[VPS PR #414](https://github.com/martaxi-boss/VPS/pull/414) (apenas modos no deployment protegido
existente) e [VPS PR #415](https://github.com/martaxi-boss/VPS/pull/415)
(alinha apenas o `ref` do validador da ponte já existente).

## Artefacto e medição geométrica independente

A chamada direta do papel `cad-worker` devolveu `artifacts/evidence-1.stl`,
ficheiro binário STL de **61 170 bytes** com SHA-256:

`0c3e483d18ccce5efa19615e61964ec55588ee9045a571e8979221d1e76217d0`

Medição independente dos bytes do STL extraídos do `response.zip`, com `trimesh`:
- dimensões **40 × 30 × 12 mm**, furo central **9,99997 mm**;
- **400 triângulos**, malha fechada, orientação coerente, característica de Euler **0**;
- volume **13 458,20 mm³**, desvio do modelo matemático de **0,0050%**.

O mesmo SHA-256 está no `verified_tool_events`, no `host_inbox` do revisor
e nas provas inspecionadas. A tarefa `produce-cad` foi aprovada pelo papel
distinto `cad-reviewer`. No fecho: **uma chamada de ferramenta verificada,
uma revisão, uma tarefa aprovada, zero modelos LLM autónomos por agente**.

## Contrato operacional para as próximas missões

Após `phase=start`, atribuir ao papel escolhido `actions:["operation:cad-stl"]`
e `input` sintético com `name=part.scad` e `content_base64` (máx. 2 MB).
A ronda `phase=turn` deve usar `turn.kind="operation"`,
`turn.operation="cad-stl"`, `turn.input_from="$input"`, `turn.task`,
`turn.role`, `turn.message` e o número `revision` atual.
É obrigatório recuperar a evidência real, verificar o STL e seus SHA-256,
submeter `phase=turn` com `turn.kind="review"` e `evidence_sha256`
exatamente igual aos hashes fornecidos, só então `phase=finish`.
Para outras operações, confirmar nome no **único** `engine/catalog.json` e
os requisitos de entrada e permissões reais. Nada de nomes inventados,
`shell` livre ou operações sem executor. `kind=operation` neste contexto
é uma ronda Ruflo, não uma nova categoria de catálogo.

## Limites e isolamento

O `quality_gate.status=not_certified` do envelope refere-se à ausência
de política de aceitação automática solicitada, **não** à reprovação da
análise geométrica independente ou do ciclo Ruflo. Não inferir que todas
as operações, ferramentas REA ou aplicações gráficas estão certificadas.
Não há inferência LLM residente na VPS; a IA anfitriã única orienta os
papéis. Os executáveis permanecem em `/srv/projects/skill-universal/`.
A ligação SSH não mudou e os oito serviços protegidos passaram.

A Skill empacotada no ChatGPT pode exigir atualização/instalação própria
para carregar as instruções novas: o GitHub atualizado não comprova
automaticamente a versão da instalação cliente.
