# Auditoria GitHub: pacotes de Skills e Orquestrador Ferrari

Última revisão: 2026-11-02. Projeto exclusivo: martaxi-boss/skill-universal.

## Decisão de arquitetura

**Uma Skill Universal** contém instruções concisas e referências temáticas. O
**Motor Ferrari no Ubuntu** fornece todas as ferramentas e executores. A IA
(ChatGPT, Codex, Cloud ou outra) interpreta o pedido, submete um plano estruturado
e recebe resultados; não usamos os seus programas como executores.

Não descarregar e juntar centenas de diretórios SKILL.md como se fossem software
Ubuntu. A maioria oferece textos de procedimento específicos de um modelo/host,
não ferramentas executáveis nem licenças para produtos pagos. Reutilizar ideias
e padrões, com atribuição quando aplicável; só copiar código após verificar
individualmente a licença e o comportamento do script.

## Comparação de 9 fontes públicas

| Repositório | Licença e formato | Adaptação Ferrari |
|---|---|---|
| [obra/superpowers](https://github.com/obra/superpowers) | MIT, várias Skills e hooks | Padrões de requisitos, TDD e revisão; não instalar os hooks |
| [agentskills/agentskills](https://github.com/agentskills/agentskills) | Código Apache 2.0, documentação CC BY 4.0 | Manter um SKILL.md com referências carregadas conforme a tarefa |
| [wshobson/agents](https://github.com/wshobson/agents) | MIT, agentes e plugins para vários clientes | Consultar padrões de validação e engenharia; não importar tool permissions ou wrappers |
| [vercel-labs/skills](https://github.com/vercel-labs/skills) | MIT, CLI Node >= 22.20 | Catálogo de pesquisa opcional; instalação de várias Skills não necessária |
| [anthropics/skills](https://github.com/anthropics/skills) | Licenças por diretório; alguns documentos são apenas source-available | Estudar exemplos livres; **não** copiar os módulos documentais proprietários |
| [VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents) | MIT; papéis de agentes | Referência de papéis, sem runtime Claude |
| [ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills) | Índice de terceiros; licenças heterogéneas | Descoberta apenas, cada projeto precisa de auditoria |
| [travisvn/awesome-claude-skills](https://github.com/travisvn/awesome-claude-skills) | Índice de terceiros, licença por entrada | Descoberta, não instalar pacotes às cegas |
| [openai/skills](https://github.com/openai/skills) | Histórico; README marca o repositório como descontinuado | Não utilizar como fonte principal de atualizações |

Dados da pesquisa, estrelas e notas ficam no
[registo de auditoria](../engine/skillpacks_audit.json).
**Estrelas são popularidade, não certificação de compatibilidade, segurança
ou direitos de utilização.**

## Orquestradores auditados

| Motor | Licença | Papel recomendado | Ubuntu |
|---|---|---|---|
| [Prefect](https://github.com/PrefectHQ/prefect) | Apache 2.0 | Motor adicional para workflows persistentes, agendas, retries, monitorização | Python >= 3.11, servidor OSS autoalojável; sem obrigatoriedade de cloud paga |
| [LangGraph](https://github.com/langchain-ai/langgraph) | MIT | Fluxos agentivos com estado; plugável a IA existente | Biblioteca Python, dependências e modelos a validar |
| [CrewAI](https://github.com/crewAIInc/crewAI) | MIT | Fluxos entre agentes; só quando necessário | Python, fornecedor/modelo de IA configurado à parte |
| [Ruflo](https://github.com/ruvnet/ruflo) | MIT | Harness especializado e swarms opcionais | Node/npm, componentes Claude/Codex são específicos de cliente; CLI/MCP a auditar |
| [Dagster](https://github.com/dagster-io/dagster) | Apache 2.0 | Data pipelines especializados | Não usar como núcleo universal de ferramentas |
| [Apache Airflow](https://github.com/apache/airflow) | Apache 2.0 | Agendamento pesado de pipelines | Servidor e dependências desproporcionados para pequenas tarefas |

**Seleção:** o coordenador Ferrari usa Python padrão e o motor já existente.
Prefect é a prioridade para futura persistência e agendação em Ubuntu. Ruflo
mantém-se módulo opcional, sem substituir o Ferrari nem exigir Claude/Codex
como executores. Não instalar dois coordenadores concorrentes por defeito.

## Orquestrador local realmente implementado

Código: [engine/orchestrator.py](../engine/orchestrator.py).
O plano é JSON e só permite as operações tipadas de
[engine/ferrari.py](../engine/ferrari.py).
Oferece:
- análise de dependências (DAG) e rejeição de ciclos;
- verificação dos nomes de operações, inputs e IDs de tarefas;
- simulação (dry-run) por defeito, **sem escrita no disco**;
- execução independente do anfitrião IA, **apenas em Ubuntu**;
- paralelismo limitado a 1–4 operações e dependências em série;
- registo por execução, lista de artefactos, sucessos e falhas;
- sem execução de comandos shell arbitrários ou APIs pagas;
- erros reais reportados sem simular ferramentas ausentes.

Comandos:

    python3 -m engine.orchestrator --plan examples/ferrari-workflow.json --workspace /tmp/ferrari-work
    python3 -m engine.orchestrator --plan examples/ferrari-workflow.json --workspace /tmp/ferrari-work --execute --max-parallel 2

O segundo comando cria artefactos. Não o executar na VPS até haver diagnóstico,
ambiente isolado e autorização para implantação. As execuções no GitHub Actions
usam um runner descartável, não a VPS do utilizador.

## Pendências para classificar como profissional em produção

- Revalidar Python, Node, Java, versões do REA, Ruflo/Prefect, RAM, SSD, GPU e
  CPU **na VPS real Ubuntu**.
- Instalar apenas softwares aprovados no manifesto
  [engine/ubuntu_selection.json](../engine/ubuntu_selection.json).
- Testar casos reais por domínio: websites full-stack, Ghidra/REA/JADX,
  criativos profissionais, vídeo, OCR/documentos, CAD, gestão de dados.
- Melhorar persistência/reprise após interrupção, backups, cancelamento,
  limites de recursos por trabalho, monitorização e disponibilidade do MCP.
- Certificar as integrações entre a Skill em cada IA e a **mesma** VPS.

Sem estas evidências não existe motor a 100% instalado ou certificado.
