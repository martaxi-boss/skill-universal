# Fase 7 — automação profissional no único motor Ferrari

**Estado: candidato sob certificação, não concluído enquanto a execução VPS não demonstrar o fluxo.**

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

Não declarar estes passos concluídos antes de existirem os IDs e resultados GitHub Actions correspondentes.

## Programas globais

Os 16 pacotes APT identificados na Fase 6 não são removidos automaticamente: a responsabilidade/consumidores transversais pertencem à Fase 9. Nenhum novo pacote global é permitido para o Ferrari.

## Continuidade

O registo de certificação será atualizado com os commits concretos, ID de execução, SHA realmente instalado, testes e bloqueios reais. A Fase 8 não começa automaticamente por ter um CI verde.
