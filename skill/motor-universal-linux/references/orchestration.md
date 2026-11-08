# Orquestrador do Motor Ferrari — Fase 7 certificada

Esta referência pertence à **única Skill Universal Ferrari**, não cria outra Skill, agente coordenador, serviço ou dependência. Consultar sempre o [BOOTSTRAP canónico](https://github.com/martaxi-boss/skill-universal/blob/main/BOOTSTRAP.md) e [certificação F7](https://github.com/martaxi-boss/skill-universal/blob/phase7/20261105-dag-persistence-private/docs/CERTIFICACAO_FASE7_20261105.md).

## Instalação e isolamento

- Repositório GitHub `martaxi-boss/skill-universal`; pasta exclusiva da VPS `/srv/projects/skill-universal/`, com mesmo nome.
- `current` certificado na [ativação #42098645092](https://github.com/martaxi-boss/VPS/actions/runs/42098645092): `758e1b435317fa26277b332b75bc47c67910be81`. Fallback F6 preservado `146145d5ada9c13e368df18727e4dbf4f5807664`.
- Todo o código, executores, ambientes Python, npm, REA/Ruflo privados, checkpoints e artefactos Ferrari pertencem à sua árvore. A ponte GitHub Actions/SSH existente só transporta pedidos e respostas; não instalar programas Ferrari globalmente.

## Execução DAG existente

O **único** `engine/orchestrator.py` valida um plano JSON tipado (no máximo **24 etapas** e **4 trabalhadores**) com dependências acíclicas, operações e ferramentas aprovadas, sem shell arbitrário. `kind=plan` usa o mesmo workflow `ferrari-skill-request.yml` existente.

- Plano regular: enviar novo JSON `kind=plan` através da Skill → GitHub → VPS → `response.zip` com `report.json` e artefactos reais. [Prova #42099036932](https://github.com/martaxi-boss/VPS/actions/runs/42099036932): HTML, SVG, texto e relatório PASS.
- Na CLI privada, usar `python3 -m engine.orchestrator --plan plano.json --workspace /srv/projects/skill-universal/.runtime/<pasta> --execute --max-parallel 2` (exemplo de formato; não é instrução para instalação global).
- Jobs com retoma: atribuir `--job-key <id-estavel>`, depois `--resume`, mantendo mesmo plano e limites. `--retry-failed` é explícito para fases com falha. O motor conserva `journal.json` atómico e `report.json` em pasta própria do job.
- Cancelamento: ficheiro regular `cancel.request` na pasta do job; é verificado **entre ondas**. O prazo também é cooperativo, **não** um hard timeout da ferramenta que esteja em execução.
- Artefactos de cada etapa são validados como ficheiros pertencentes à pasta da etapa; links simbólicos e caminhos exteriores são recusados. `flock` evita execução concorrente duplicada do mesmo job. Quotas limitam tamanho de artefactos; **não** foi certificado um limite rígido de CPU/RAM por subprocesso.

O DAG da VPS foi certificado na [execução #42098800995](https://github.com/martaxi-boss/VPS/actions/runs/42098800995): interrupção após a primeira etapa, retoma noutro processo Python privado sem a repetir, replay idempotente e um segundo plano com três etapas. Foram verificados **40/40** executores privados.

## Papel do Ruflo e outras ferramentas

Ruflo `3.71.0` está no npm privado Ferrari e é **sub-anfitrião gestor de papéis e tarefas apenas durante a ronda conduzida pela IA anfitriã** (ChatGPT/Codex/outro autorizado). A equipa `kind=ruflo-team` já completou trabalho real com ferramenta privada, revisão independente, rejeição, correção e aprovação [#42509439220](https://github.com/martaxi-boss/VPS/actions/runs/42509439220). **O único raciocínio vem da IA anfitriã partilhada; agentes com modelos próprios ou LLM autónomo na VPS não são um objetivo nem uma pendência.** Não instalar coordenador permanente, API/modelos por agente ou pressupor fornecimento da API pela subscrição ChatGPT. Prefect é opcional; Ruflo não substitui `engine/orchestrator.py` nem o único catálogo Ferrari.

## Desinstalação e higiene

O utilizador deve poder retirar **a árvore Ferrari** no futuro, mas uma remoção real só é segura depois de verificar registos de serviço, processos e consumidores. A [auditoria F7](https://github.com/martaxi-boss/VPS/actions/runs/42098800995) analisou 29 configurações e não encontrou referências ao Ferrari nessa amostra, que **não foi exaustiva**. O [procedimento de remoção isolada](https://github.com/martaxi-boss/skill-universal/blob/phase7/20261105-dag-persistence-private/docs/DESINSTALACAO_ISOLADA_FERRARI.md) é não destrutivo até autorização explícita. Os pacotes APT históricos pertencem à análise transversal da Fase 9, sem `apt purge` automático.

**Limite de produto:** CI, ações tipadas e testes reais demonstram apenas capacidades e versões executadas; não equivalem a certificação universal de todas as ferramentas, modelos, aplicações GUI ou fornecedor externo.
