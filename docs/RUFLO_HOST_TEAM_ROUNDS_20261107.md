# Ferrari — equipa Ruflo com uma IA anfitriã partilhada (07/11/2026)

## Objetivo e âmbito

Implementação **no motor Ferrari existente**, sem segundo catálogo, Skill, coordenador permanente, servidor de modelos na VPS ou alterações aos projetos vizinhos.

A IA anfitriã (ChatGPT, Codex, Claude ou outro anfitrião autorizado) **fornece as decisões por rondas**. O motor não faz chamadas a LLM, não recebe uma API automaticamente por causa da subscrição ChatGPT e **não afirma agentes de inferência autónoma**. O Ruflo original MCP 3.71 cria, atribui e encerra agentes/tarefas por ronda. O Ferrari conserva o estado do trabalho e despacha apenas ferramentas tipadas privadas.

**Ficheiros implementados:** engine/agent_team.py (contrato e máquina de estados), engine/skill_job.py (novo tipo de pedido), tests/test_agent_team.py (regressões). Mantém-se engine/ruflo_host.py e a operação histórica kind=ruflo-host, sem regressão.

## Estrutura: especializações disponíveis versus agentes ativos

- Papéis recomendados por projeto: arquiteto, programador, testador, revisor, com investigador/depurador/otimizador/documentador quando necessário.
- A ficha por papel contém missão/competências e uma lista **explícita de ações Ferrari autorizadas**. Os tipos Ruflo adicionais podem ser indicados por nome e precisam de passar a validação real do Ruflo; não assumir que todos os tipos anunciados estão instalados.
- Uma equipa iniciada pode ter **2–8 papéis ativos** e **1–24 tarefas**. São limites de segurança da sessão, **não** um catálogo truncado de especializações disponíveis. Cada tarefa tem dono, revisor diferente, objetivo e dependências; são rejeitadas dependências circulares.
- A execução inteligente por anfitrião é sequencial por ronda. O motor Ferrari tem capacidades anteriores de paralelismo; **esta implementação não certifica dois turnos inteligentes simultâneos**.

## Protocolo de rondas (versão 1)

Todos os exemplos seguintes utilizam a Skill única; para a ponte de produção, ver o estado de ativação mais abaixo. Nunca colocar código confidencial, credenciais ou dados pessoais em pedidos enviados para repositórios públicos.

### 1. Criar equipa, plano e memória local privada

Exemplo sintético, com entrada JSON fictícia. Cada nova chamada deve usar um id de pedido diferente; team_id identifica a mesma sessão local.

~~~json
{
  "version": 1,
  "id": "team-create-001",
  "kind": "ruflo-team",
  "phase": "start",
  "team_id": "example-work-001",
  "host": "ChatGPT",
  "mission": "Formatar e verificar um JSON sintético",
  "roles": [
    {"id": "arq", "type": "architect", "actions": []},
    {"id": "coder", "type": "coder", "actions": ["jq-format-json"]},
    {"id": "tester", "type": "tester", "actions": ["jq-format-json"]},
    {"id": "reviewer", "type": "reviewer", "actions": []}
  ],
  "tasks": [
    {"id": "design", "role": "arq", "reviewer": "reviewer",
     "goal": "Definir critérios de aceitação", "depends_on": []},
    {"id": "code", "role": "coder", "reviewer": "reviewer",
     "goal": "Formatar o JSON com ferramenta Ferrari", "depends_on": ["design"]},
    {"id": "test", "role": "tester", "reviewer": "reviewer",
     "goal": "Verificar o JSON obtido", "depends_on": ["code"]}
  ],
  "input": {"name": "data.json", "content_base64": "eyJvayI6dHJ1ZX0K"}
}
~~~

O Ruflo inicia um swarm efémero com os papéis solicitados e confirma a capacidade de os criar; encerra o swarm. O Ferrari guarda um journal privado e devolve host_inbox com tarefas prontas, a ficha contextual do agente e o número de revisão.

### 2. O anfitrião fornece raciocínio por papel, não uma API na VPS

O anfitrião lê host_inbox, raciocina com o contexto do agente e envia uma decisão estruturada. Exemplo de submissão de plano pelo arquiteto:

~~~json
{"version":1,"id":"team-plan-001","kind":"ruflo-team",
 "phase":"turn","team_id":"example-work-001","revision":0,
 "turn":{"task":"design","role":"arq","kind":"submit",
         "message":"Plano concreto e critérios de aceitação verificáveis."}}
~~~

A tarefa fica **awaiting_review**, não aprovada. O anfitrião entra agora no contexto do agente revisor e verifica o plano. Envia:

~~~json
{"version":1,"id":"team-review-001","kind":"ruflo-team",
 "phase":"turn","team_id":"example-work-001","revision":1,
 "turn":{"task":"design","role":"reviewer","kind":"review",
         "message":"Os critérios de aceitação estão completos.",
         "verdict":"approved",
         "evidence_sha256":["0000000000000000000000000000000000000000000000000000000000000000"]}}
~~~

**O SHA256 acima é apenas um marcador sintético de 64 dígitos; substituí-lo obrigatoriamente pelo hash REAL do `host_inbox.evidence` devolvido após a submissão.** Se for diferente, a revisão falha. O Ruflo regista a atribuição à função indicada e o Ferrari só liberta as dependências após a revisão por papel diferente. O anfitrião e a ficha da tarefa têm responsabilidade por verificar o conteúdo; o motor **não consegue provar por si só que a avaliação textual é inteligente ou correta**.

### 3. Executar uma ferramenta real e passar os resultados

Depois de aprovar design, code fica disponível. O anfitrião pode enviar:

~~~json
{"version":1,"id":"team-work-001","kind":"ruflo-team",
 "phase":"turn","team_id":"example-work-001","revision":2,
 "turn":{"task":"code","role":"coder","kind":"invoke",
         "message":"Formatar JSON com a ferramenta Ferrari autorizada.",
         "action":"jq-format-json","input_from":"$input"}}
~~~

O motor executa tool_runtime.invoke sobre ficheiro privado, valida a confirmação, verifica que os artefactos não saíram da pasta da tarefa e guarda o SHA-256 e tamanho. O revisor inspeciona resultados e aprova ou pede alterações. Para a tarefa test, input_from pode ser code **apenas quando code estiver aprovada**. O resultado aparece em response.zip com o relatório e as provas desse turno.

### 4. Rejeitar, corrigir, recuperar e fechar

- Uma revisão com verdict=changes_requested devolve a tarefa ao responsável. O anfitrião pode enviar outra submissão; o histórico conserva rejeições e correções.
- Em erro na ferramenta, a tarefa passa a failed e não é repetida automaticamente. O anfitrião pode enviar phase=recover com revision, task, reason e acknowledge_risk=true **após inspecionar efeitos e reconhecer o risco de duplicação**.
- phase=status devolve apenas fotografia de leitura (sem executor/LLM); revision impede repetir decisões obsoletas.
- phase=finish exige todas as tarefas aprovadas por papel distinto, ao menos **uma tarefa aprovada com artefactos produzidos por executor Ferrari real**, SHA-256 ainda válido e uma aprovação final explícita do anfitrião. Uma simples descrição textual não satisfaz a certificação.

O estado fica apenas dentro de /srv/projects/skill-universal/.runtime/ruflo-team-sessions/<team_id>/, com journal atómico e bloqueio exclusivo. Não se instala daemon; os swarms Ruflo abrem e fecham em cada ronda. O journal guarda continuidade entre esses swarms.

## Segurança, proveniência e veracidade

- Só ações explicitamente aprovadas em engine/catalog.json ou REA MCP validado podem executar; cada papel dispõe de allowlist; **sem shell arbitrário**.
- Não existe chave de IA nem modelo por agente; independent_agent_model_calls = 0 por definição da execução assistida. Um nome de agente, agent_spawn ou model=inherit **não é prova de inferência**.
- Os ficheiros antigos são revalidados por hash antes da revisão e antes da aprovação final; **cada aprovação tem de apresentar os SHA256 exatos dos ficheiros observados**. Symlinks e caminhos fora da sessão são rejeitados.
- Um revisor lógico diferente do executor **não equivale a uma segunda IA independente**: é mais uma ronda de raciocínio da mesma IA, com critérios de revisão distintos.
- GitHub do utilizador e repositório VPS são públicos; só dados sintéticos/não confidenciais são elegíveis por esta ponte. A persistência na VPS privada **não torna privados commits públicos**.

## Estado de certificação — produção e limites reais (07/11/2026)

A implementação `kind=ruflo-team` está **ativa na VPS**, na release Ferrari privada `e0509d5370828869479069c99f2eace779960cad`, com rollback preservado em `205c6f0e970259c79fa2111b6670c2fe1672fb27`. O validador do transporte normal GitHub Actions em `martaxi-boss/VPS` foi atualizado para este SHA, **sem modificar a ligação SSH nem acrescentar outro motor**.

**Certificação de ativação e execução Ruflo real:** [VPS #42325589374](https://github.com/martaxi-boss/VPS/actions/runs/42325589374) — 474 testes de regressão, 40/40 ações privadas, Ruflo MCP 3.71 com **4 papéis reais**, 3 tarefas, **2 chamadas reais à ferramenta privada jq**, **3 revisões por papel distinto**, SHA-256 validado, ZIP de resultados, 8/8 serviços protegidos após ativação, ficheiros QA descartáveis eliminados. A primeira tentativa [#42325394291](https://github.com/martaxi-boss/VPS/actions/runs/42325394291) falhou no caminho Python do programa de certificação e **reverteu automaticamente** para a release anterior; o erro de entrada do certificado foi corrigido antes da execução PASS.

**Certificação pela ponte normal com anfitrião ChatGPT a fornecer raciocínio por rondas:** sessão sintética `team-chatgpt-20261107`, início [#42325836453](https://github.com/martaxi-boss/VPS/actions/runs/42325836453), plano do Arquiteto [#42325915028](https://github.com/martaxi-boss/VPS/actions/runs/42325915028), revisão [#42325995770](https://github.com/martaxi-boss/VPS/actions/runs/42325995770), Programador com saída jq real [#42326078050](https://github.com/martaxi-boss/VPS/actions/runs/42326078050), revisão [#42326165794](https://github.com/martaxi-boss/VPS/actions/runs/42326165794), Testador repetindo jq no resultado aprovado [#42326222742](https://github.com/martaxi-boss/VPS/actions/runs/42326222742), revisão [#42326294271](https://github.com/martaxi-boss/VPS/actions/runs/42326294271), aceitação final [#42326357951](https://github.com/martaxi-boss/VPS/actions/runs/42326357951). Todos os passos passaram. A missão terminou com `status=completed`, **3 tarefas aprovadas, 2 execuções reais de ferramenta e 3 revisões**, dois ficheiros JSON válidos com `ok=true` e SHA-256 idêntico `12b34da73b0c67a0319e6eddbd3582af66e3b558b4d44e4a6860e0cec20d726f`.

**Limites importantes, sem encobrir:** o **mesmo ChatGPT anfitrião fez as decisões por papéis nas rondas da conversa**. Os quatro agentes são papéis Ruflo efetivamente registados e atribuídos, não quatro modelos separados nem quatro inteligências independentes. **Zero chamadas automáticas LLM pela VPS**, sem endpoint ChatGPT que permita continuar a raciocinar depois da sessão. É uma **coordenação real assistida e certificada**, não autonomia de subagentes baseada em modelos. Um mock não certifica Ruflo real: essa distinção foi resolvida com os ensaios VPS acima, mas testes sintéticos por si só não provam inferência autónoma. Uma futura integração automática ChatGPT/Codex requer autorização e certificação separadas.

**Higienização:** os pedidos sintéticos e modos temporários de ativação foram retirados da árvore de produção do repositório VPS após preservar os IDs Actions; a ponte Ferrari permanente com o pin novo mantém-se. O journal privado da missão final permanece dentro da pasta Ferrari para continuidade/verificação; os temporários do teste de instalação foram eliminados. Não reutilizar ou reemitir os nomes dos pedidos já processados; permanecem no histórico Git.

**Veredito:** `ruflo-team` no Ferrari e **ChatGPT → Skill/GitHub → Ruflo MCP → ferramentas privadas Ferrari → revisão cruzada → ZIP** estão **certificados no âmbito assistido**. **Equipa autónoma com raciocínio LLM sem anfitrião presente = NÃO CERTIFICADA.**
