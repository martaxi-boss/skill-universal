# Certificação Ferrari — Fase 7, orquestração privada e desinstalação isolada

**Data:** 05/11/2026. **VEREDITO: PASS — orquestrador Ferrari e retoma de DAG certificados na VPS, dentro do âmbito executado.** Não é um certificado universal de recursos Linux, nem licença para eliminar pacotes APT globais, nem prova absoluta de remoção sem efeitos colaterais. A Fase 8 não foi iniciada.

## Identidade GitHub ↔ VPS

- Código no repositório `martaxi-boss/skill-universal`; a release é o SHA imutável `758e1b435317fa26277b332b75bc47c67910be81` da branch `phase7/20261105-dag-persistence-private`, incluído na [PR #65](https://github.com/martaxi-boss/skill-universal/pull/65).
- Diretório físico único e com nome igual ao repositório: `/srv/projects/skill-universal`.
- `current` → `/srv/projects/skill-universal/releases/758e1b435317fa26277b332b75bc47c67910be81`.
- Fallback certificado Fase 6 preservado: `146145d5ada9c13e368df18727e4dbf4f5807664`; não remover a release de recuperação.
- Ponte GitHub já existente em `martaxi-boss/VPS`, com pedidos F7 estritamente allowlisted e SHA pinado. Nenhuma alteração ao SSH partilhado ou ao Supervisor.
- A fonte da Fase 6 continua na PR #64 ainda sem merge. Os SHAs de execução estão documentados e são a referência de verdade; não alegar que o SHA de `main` está automaticamente em produção.

## Matriz de provas reais

| Critério | Prova | Veredito |
|---|---|---|
| Código do único orquestrador, regressões, segurança do projeto | [CI Ferrari #42097832176](https://github.com/martaxi-boss/skill-universal/actions/runs/42097832176) e [#42097841955](https://github.com/martaxi-boss/skill-universal/actions/runs/42097841955): **274 testes PASS** | PASS |
| Pré-teste protegido sem mudar a release atual | [VPS #42098462830](https://github.com/martaxi-boss/VPS/actions/runs/42098462830): testes unidade + 40/40 executores, CAD, 3D, Office e DAG, `current` F6 intacto | PASS |
| Ativação só dentro da pasta Ferrari | [VPS #42098645092](https://github.com/martaxi-boss/VPS/actions/runs/42098645092): read-back `current` F7, fallback F6 intacto | PASS |
| DAG persistente e execução de dependências | [VPS #42098800995](https://github.com/martaxi-boss/VPS/actions/runs/42098800995): etapa real `web-template`, interrupção controlada, recomeço em **outro processo Python privado** da etapa `binary-strings` sem repetir a primeira, replay após `completed` sem execução extra | PASS |
| DAG paralelo com artefactos | Mesmo run #42098800995: website, SVG e extração de texto, **3/3 passos**, `max_parallel=2`, artefactos todos dentro do Ferrari | PASS |
| Ligação Skill → GitHub → VPS → ZIP | [VPS #42099036932](https://github.com/martaxi-boss/VPS/actions/runs/42099036932): `kind=plan`, `FERRARI_SKILL_JOB_STATUS=completed`, `FERRARI_SKILL_END_TO_END=PASS` e `response.zip` real com HTML, SVG, TXT e relatório | PASS |
| Controlo de concorrência, falhas e quotas | `flock` por job, `journal.json` atómico e revalidação de artefactos; limites de 24 passos, quatro trabalhadores e tamanho; cancelamento/prazo cooperativos entre ondas, regressões em CI | PASS para controlos testados, **não hard CPU/RAM** |
| Ruflo privado | #42098800995: `ruflo@3.71.0` em `.runtime/npm`, `--version` com Node privado, CLI local PASS | **OPCIONAL**; multiagentes/modelos não certificados |
| Inventário de remoção reversível e isolamento | #42098800995: raiz `skill-universal` correspondente ao GitHub, sem alias antigo, 29 configs de serviços auditadas sem referências ao Ferrari. `unscanned_or_unreadable_possible=true`; não houve desinstalação | **PASS da amostra, INCOMPLETO para garantia universal** |
| Saúde dos restantes serviços | [VPS #42099108182](https://github.com/martaxi-boss/VPS/actions/runs/42099108182), [issue #354](https://github.com/martaxi-boss/VPS/issues/354): `AUDIT_ONLY`, `health_after=true`, `protected_services_unchanged=true`, zero bytes removidos | PASS |

## Tecnologia sem camadas

O motor existente `engine/orchestrator.py` concentra a coordenação de DAGs. Cada job fica fisicamente em pasta própria dentro do Ferrari, com `journal.json`, `report.json` e artefactos. `job_key` imutável exige retoma explícita em caso de repetição; o motor compara o hash do plano, verifica os ficheiros concluídos e não os volta a gerar. Duas execuções concorrentes do mesmo job são bloqueadas por `flock`. Falhas das ferramentas não são mascaradas.

A opção `--resume` do motor e o cancelamento por `cancel.request` estão dentro do Ferrari. Não existe novo coordenador, daemon global, ferramenta paga obrigatória ou armazenamento partilhado com outros projetos.

A Skill publica tarefas `kind=plan` normalmente, criando um job privado novo por pedido. O mecanismo de retoma de um job existente é uma capacidade **local do motor**, demonstrada com processos independentes; não apresentar pedidos GitHub repetidos como se já fizessem replay do mesmo job automaticamente.

## Limites explicitados para não inventar

- O orçamento de artefactos limita os ficheiros verificados, não é um limite rígido de RAM para cada subprocesso. O tempo é verificado entre ondas; um subprocesso bloqueado requer mecanismo adicional de hard timeout. **Não declarar CPU/RAM hard-capped.**
- Ruflo `3.71.0` CLI PASS, mas execução de agentes com modelo gratuito ou autorizado ainda não demonstrada. Trata-se de fornecedor **opcional e não bloqueante**, não de segundo coordenador.
- O relatório de desinstalação é de **pré-avaliação não destrutiva**. A varredura de 29 configurações de serviços foi delimitada e apresentou `unscanned_or_unreadable_possible=true`. É proibido afirmar que eliminar a pasta amanhã é garantidamente neutro sem reinspecionar consumidores, trabalhos em execução e ligações indiretas. [Ver procedimento](DESINSTALACAO_ISOLADA_FERRARI.md).
- Os 16 pacotes APT históricos não pertencem à instalação privada Ferrari e permanecem intactos até à auditoria transversal da Fase 9. Não são removidos para forçar uma métrica artificial de limpeza. Os nove programas ainda sem instalação privada permanecem indisponíveis.

## Decisão de fase

**Fase 7 — funcionamento, persistência, paralelismo, retorno ZIP e alinhamento de release: CERTIFICADOS NO ÂMBITO TESTADO.** A auditoria final da VPS inteira e o ensaio isolado de desinstalação pertencem às fases 9 e 10, respetivamente. A preparação para remover a única pasta está documentada, mas nenhum ficheiro de outros projetos foi removido e **a desinstalação do Ferrari ativo não foi executada**.
