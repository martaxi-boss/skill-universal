# Fase 7 — automação profissional no único motor Ferrari

**Estado: CERTIFICADA no âmbito operacional do DAG privado (05/11/2026).** [Certificado final com provas](CERTIFICACAO_FASE7_20261105.md). A remoção da VPS inteira e hard quotas de CPU/RAM continuam fora do âmbito certificado.

## Arquitetura mantida

- Repositório `martaxi-boss/skill-universal`; instalação física `/srv/projects/skill-universal`, mesmo nome.
- **Um único orquestrador:** `engine/orchestrator.py`; 24 etapas por DAG, paralelismo 1–4. Nenhum Project Leader/coordenador na VPS, nenhum novo daemon, nenhuma Skill adicional, nenhuma obrigação de API paga.
- O protocolo existente `kind=plan` continua a chamar o orquestrador Ferrari e devolver ZIP. Os pedidos e outputs continuam restritos ao Ferrari; não acrescentar execução de comandos SSH arbitrários ao transporte.

## Alterações da Fase 7 — em validação

| Controlo | Comportamento implementado | Limite assumido |
|---|---|---|
| Estado persistente | `journal.json` atómico em cada etapa, `report.json` final, dentro da pasta do job; escritas fsync e substituição atómica | Recuperação limitada ao mesmo diretório de job |
| Idempotência | `job_key` estável rejeita segunda execução não explícita; `resume=True` verifica SHA canónico do DAG e limites | O pedido normal `kind=plan` cria jobs novos; retoma está disponível ao motor/CLI privado |
| Retoma | Valida cada artefacto de etapa concluída; reaproveita o que está íntegro; remove apenas saída parcial do próprio job | Trabalho não concluído pode necessitar ser executado de novo |
| Segurança | Validar nomes, tipos de passos, DAG sem ciclos, sem shell arbitrário; 40 ações tipadas executam apenas CLIs privados; bloqueio a caminhos externos na VPS ativa | Não abrange todas as bibliotecas carregadas dinamicamente por todas as aplicações opcionais |
| Concorrência | Lock de ficheiro local `flock`, impedindo dois processos no mesmo job; 1–4 workers | Paralelismo simultâneo permanece configurável e delimitado |
| Cancelamento | `cancel.request` como ficheiro normal dentro do job; não agenda etapas futuras quando encontrado | Cooperativo; não interrompe imediatamente uma ferramenta em execução |
| Quotas | Máximo de 24 passos, quatro workers, orçamento de tamanho de artefactos e prazo de execução entre waves | **Tempo cooperativo**, sem afirmar limite duro de CPU/RAM por subprocesso |
| Ruflo | Validar o CLI/versão npm privada e execução `--version` sem modelo/API; classificar separadamente a prova de agentes reais | Um CLI que arranca **não** equivale a multiagentes certificados |
| Desinstalação isolada | [Política e checklist sem eliminação](DESINSTALACAO_ISOLADA_FERRARI.md), inventário de referências a Ferrari na configuração de serviços | A eliminação real da árvore fica reservada para ordem explícita e prova de ausência de consumidores externos |

## Portas para certificação

1. CI da branch Fase 7 com novas regressões e regressões existentes **PASS**.
2. Precheck real da nova release na VPS antes de alterar `current`; atuais F6 e fallback preservados.
3. Ativação protegida com SHA exato, rollback se houver falha, ferramentas e dependências apenas dentro de `/srv/projects/skill-universal`.
4. VPS: executar DAG real, guardar checkpoint interrompido, retomar noutro processo privado **sem repetir etapa concluída**, executar DAG com duas tarefas paralelas, obter artefactos, medir memória e tempo, classificar Ruflo.
5. Validar saída ZIP `kind=plan` pela ponte Skill → GitHub → VPS, read-back do SHA, execução sem instalações globais.
6. Auditoria posterior e higienização limitada ao Ferrari, saúde dos serviços de outros projetos mantida.

Os seis critérios receberam provas operacionais: [CI #42097832176](https://github.com/martaxi-boss/skill-universal/actions/runs/42097832176) 274 testes, [precheck #42098462830](https://github.com/martaxi-boss/VPS/actions/runs/42098462830), [ativação #42098645092](https://github.com/martaxi-boss/VPS/actions/runs/42098645092), [DAG retomado noutro processo #42098800995](https://github.com/martaxi-boss/VPS/actions/runs/42098800995), [Skill→ZIP #42099036932](https://github.com/martaxi-boss/VPS/actions/runs/42099036932) e [saúde #42099108182](https://github.com/martaxi-boss/VPS/actions/runs/42099108182) PASS. Ruflo 3.71.0 é CLI opcional e os testes de agentes pagos/gratuitos não foram realizados.

## Programas globais

Os 16 pacotes APT identificados na Fase 6 não são removidos automaticamente: a responsabilidade/consumidores transversais pertencem à Fase 9. Nenhum novo pacote global é permitido para o Ferrari.

## Continuidade

Release VPS ativa: `758e1b435317fa26277b332b75bc47c67910be81`; fallback F6: `146145d5ada9c13e368df18727e4dbf4f5807664`. O orquestrador, os sete venvs, os executores e os resultados permanecem no diretório privado Ferrari. A Fase 8 ainda não foi iniciada.
