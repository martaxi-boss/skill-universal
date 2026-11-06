# Ferrari — ponto 4 / Ruflo: auditoria real, isolamento e decisão

**Data:** 06/11/2026. **Estado: AUDITORIA E FUNÇÕES LOCAIS CERTIFICADAS; MULTIAGENTES/PROVEDOR NÃO CERTIFICADOS.** O Ruflo é um programa *opcional* do Ferrari e **não** substitui `engine/orchestrator.py`, não é autorizado a atuar como coordenador residente, e não cria uma segunda Skill. A aplicação do ChatGPT será atualizada somente no fecho global.

## Instalação real e comandos disponíveis

- [VPS #42186639714](https://github.com/martaxi-boss/VPS/actions/runs/42186639714) **SUCCESS**: `ruflo@3.71.0` instalado somente em `.runtime/npm/ruflo/node_modules/ruflo/`, manifest MIT, binário `bin/ruflo.js`; Node privado `runtimes/node-22.23.4/bin/node`. `--version` e `--help` reais PASS. Release Ferrari `current` continuou `a266b25e06a9c8acf1fdc940d22b99070cd17ded`; sem instalação global.
- [VPS #42186827612](https://github.com/martaxi-boss/VPS/actions/runs/42186827612) **SUCCESS**: ajuda de comandos reais `route`, `policy`, `workflow`, `task`, `agent`, `swarm`, `memory`, `providers`, `config`, `doctor` e `security`, executada apenas com `--help`, HOME/cache/config em pasta descartável na árvore Ferrari. **Listar comandos não certifica a sua execução.**
- As superfícies `ruflo start`, `daemon`, `agent spawn`, `swarm`, `hive-mind` e `autopilot` podem coordenar/executar trabalho ou lançar processos. **Não são rotas autorizadas de produção no Ferrari.** Nenhuma foi iniciada explicitamente nesta auditoria.

## Prova real limitada — sem fornecedor/modelo

[VPS #42187084139](https://github.com/martaxi-boss/VPS/actions/runs/42187084139), workflow **SUCCESS**, num ambiente temporário com limites de cgroup `MemoryMax=1500M`, `CPUQuota=150%`, `TasksMax=128` e timeout:

1. `ruflo route list-agents`: PASS, apresentou 8 **tipos predefinidos** (coder, tester, reviewer, architect, researcher, optimizer, debugger e documenter). **Não** foram lançados oito agentes.
2. `ruflo route task "write unit tests for a synthetic calculator"`: PASS como *cálculo de encaminhamento*, devolveu `Optimizer` com confiança **12,5%** e estado `Exploration: Yes`. Não demonstrou correção da seleção (a sugestão não é claramente adequada), tarefa executada ou qualidade multiagente.
3. `ruflo memory init`, `store`, `retrieve`, `search`, `peek`: PASS no ensaio, gravou/recuperou dados **sintéticos**, com os ficheiros SQLite em pasta temporária do Ferrari. O motor de memória devolveu aviso de múltiplos armazenamentos CLI/MCP; um resultado local não equivale a memória global consistente.
4. **Efeito lateral encontrado:** o `memory store` iniciou automaticamente um **daemon de background**, apesar de não ter sido pedida coordenação. O marcador final do script de teste que dizia `NO_SWARM_DAEMON_OR_AGENT_SPAWN=PASS` **não prova ausência de daemon durante o ensaio** e deve ser desconsiderado nesse ponto. A pasta descartável foi eliminada após o teste.
5. [VPS #42187338181](https://github.com/martaxi-boss/VPS/actions/runs/42187338181), auditoria independente **SUCCESS**: **zero processos identificados como Ruflo** em execução para o utilizador do projeto; zero processos identificados como originados na pasta descartável; nenhum processo foi terminado, nenhum serviço de outro projeto alterado, release `current` preservada.

## Decisão de segurança

**Ruflo fica classificado como `OPCIONAL_LOCAL_VERIFICADO / MULTIAGENTES_NAO_CERTIFICADOS`.** A prova autoriza apenas afirmar que o pacote privado funciona e as funções locais testadas produziram resultados. **Não** autoriza usar a memória Ruflo de forma automática no motor, pois pode iniciar daemon; não autoriza iniciar `start`, `agent spawn`, `swarm`, `autopilot`, subscrever um fornecedor pago, publicar portas, instalar modelos ou interferir com o supervisor passivo.

O Ferrari mantém como único coordenador de trabalhos `engine/orchestrator.py` (DAG e retoma já comprovados em [Fase 7 #42098800995](https://github.com/martaxi-boss/VPS/actions/runs/42098800995)). O catálogo tipado `engine/tool_actions.json` **não inclui ação Ruflo**; não adicionar uma com efeitos laterais sem aprovação e certificação. Os modelos instalados nos pontos 2–3 são de imagem e transcrição, **não** um modelo de linguagem comprovadamente apto à coordenação multiagente. Não há prova de execução de agentes com IA num fornecedor gratuito neste ponto. Esta limitação opcional não bloqueia o motor universal.

**Higiene:** os workflows e pedidos temporários da VPS devem ser retirados após preservar IDs dos runs, mantendo somente o Ruflo privado já existente. Não remover o Ruflo nem apagar outros projetos ou APT globais. Não atribuir um 10/10 global ao Ferrari por esta prova.
