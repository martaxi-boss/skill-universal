# Ferrari: Ruflo coordenado por UMA inteligência anfitriã

**Data:** 2026-11-06. **Código em integração; a release atual só deve ser promovida depois de PASS real pelo transporte normal.** Uma Skill Universal; nenhuma segunda Skill, fornecedor de IA por agente, coordenador de VPS ou instalação global.

## Contrato estabelecido

1. O ChatGPT (ou, num pedido diferente, Codex, Claude ou outro hospedeiro) **é a única inteligência ativa**. Elabora os papéis e as decisões das etapas. Não há API remota automática desta conversa para programas Ubuntu.
2. A Skill Ferrari transporta um pedido estruturado autorizado por GitHub Actions → SSH existente. O motor da VPS valida o pedido e controla as ferramentas.
3. Ruflo 3.71.0 recebe `swarm_init`, `agent_spawn` (papéis com `model=inherit`), `task_create` com atribuição explícita e `task_complete` após resultado verificado, tudo através do MCP original por stdio.
4. Ferrari executa cada ação com os seus executores privados (`tool_runtime.invoke`) ou REA MCP privado (`rea_mcp.invoke`); nunca cria uma ferramenta do sistema nem usa shell arbitrário.
5. Todos os artefactos, estados temporários e resultados ficam dentro de `/srv/projects/skill-universal/`. O Ruflo termina e é encerrado por `swarm_shutdown`; não há coordenador residente.
6. O anfitrião recebe o relatório com provas e pode iniciar outra ronda inteligente, usando o mesmo modelo. Não se afirma que `agent_execute` fez inferência autónoma nesta execução.

## Certificação real já feita, distinta do deploy permanente

- [#42215555913](https://github.com/martaxi-boss/VPS/actions/runs/42215555913) **PASS:** Ruflo 3.71.0, MCP inicializado e **385 ferramentas registadas**, sessão e HOME descartáveis.
- [#42215973558](https://github.com/martaxi-boss/VPS/actions/runs/42215973558) **PASS:** contratos MCP reais de `swarm_init`, `agent_spawn`, `task_create`, `task_complete` e demais ferramentas verificadas, sem fornecedor.
- [#42216565299](https://github.com/martaxi-boss/VPS/actions/runs/42216565299) **PASS para fluxo assistido pela IA anfitriã:** `swarm_init` iniciou um swarm temporário, criou dois agentes Ruflo (coder e reviewer), criou e atribuiu duas tarefas, Ferrari executou um JSON `jq-format-json` privado e REA MCP `inspect_analysis_settings` privado, registou `task_complete` para ambos, encerrou o swarm, eliminou todos os temporários e confirmou **8/8 serviços protegidos** e **zero coordenadores persistentes**. **Chamadas LLM dentro da VPS: zero**.
- Testes de código e novo `kind=ruflo-host` deverão ser certificados na CI e na release antes de usar em produção.

## Pedido Ferrari proposto: kind=ruflo-host

Exemplo **sintético**, sem segredos, para uma única inteligência anfitriã partilhada:

```json
{
  "version":1,
  "id":"ferrari-roles-qa-20261106",
  "kind":"ruflo-host",
  "host":"ChatGPT",
  "max_parallel":2,
  "roles":[
    {"id":"coder","type":"coder"},
    {"id":"reviewer","type":"reviewer"}
  ],
  "input":{"name":"demo.json","content_base64":"eyJvayI6dHJ1ZX0K"},
  "steps":[
    {"id":"format","role":"coder","kind":"invoke","action":"jq-format-json"},
    {"id":"review","role":"reviewer","kind":"rea-mcp",
      "mcp_requests":[{"method":"tools/call","params":{
        "name":"inspect_analysis_settings","arguments":{}
      }}]}
  ]
}
```

**Segurança:** somente papéis predefinidos (2–4), no máximo duas execuções paralelas, 2–8 tarefas, catálogo tipado, REA MCP já suportado, sem provider keys e sem subagentes autónomos de modelo. O repositório de pedidos GitHub é público: nunca enviar material confidencial. Quotas universais de CPU/RAM ainda precisam de certificação à parte.

## O que ainda NÃO está certificado

- Agentes Ruflo autónomos com chamadas a modelos de IA remotos: o ChatGPT desta conversa não é um endpoint utilizável pelo Ruflo; ativar isso exigiria um transporte de retorno ou um endpoint autorizado, com prova de permissões.
- Colaboração autónoma e memória persistente dos agentes via `agent_execute`; os papéis foram **registados e atribuídos**, mas a decisão inteligente foi providenciada por uma única IA anfitriã.
- Certificação operacional do novo `kind=ruflo-host` pela Skill normal depende de CI, release privada e do pin do validador do transporte atualizado **sem camadas novas**.

**Veredito:** Ruflo como orquestrador de papéis que encaminha trabalho para as ferramentas Ferrari/REA está demonstrado em teste real, sem vários modelos. A operação de longo curso com agentes de IA independentes continua fora do âmbito e não será representada como certificada.
