# Ponte Ferrari: ChatGPT → GitHub Actions → VPS → ZIP

**Estado verificado em 07/11/2026:** o Ferrari usa **um catálogo universal** de 450 registos (173 programas, 272 funções — incluindo 220 funções REA —, 3 dependências centrais e 2 fornecedores). A [ativação #42314959728](https://github.com/martaxi-boss/VPS/actions/runs/42314959728) certificou a release `205c6f0e970259c79fa2111b6670c2fe1672fb27` com fallback universal `7bf6dcecf15da26502c5969b5eee54d5e116fc32`; a [higiene #42315724016](https://github.com/martaxi-boss/VPS/actions/runs/42315724016) removeu a revisão antiga de 394 registos, preservando 8/8 serviços. O [inventário posterior #42316041466](https://github.com/martaxi-boss/VPS/actions/runs/42316041466) terminou com `status=completed` e `response.zip` válido. Validador de pedidos `0b50e1d403deff8f3ccb421edd0b41c397d66b9b` mantido; não confundir transporte REA com catálogo separado. [BOOTSTRAP](https://github.com/martaxi-boss/skill-universal/blob/main/BOOTSTRAP.md).

**Via operacional:** repositório do motor martaxi-boss/skill-universal; repositório de transporte martaxi-boss/VPS; workflow exclusivo .github/workflows/ferrari-skill-request.yml na main. A ponte apenas entrega pedidos e recolhe resultados; a lógica fica no Ferrari (engine/skill_job.py, engine/orchestrator.py). Sem SSH direto no cliente nem regras adicionais no transporte.

## Enviar um pedido

1. Confirmar ligação GitHub autenticada e acesso adequado a martaxi-boss/VPS. A Skill não cria credenciais.
2. Criar **um único ficheiro novo** em ferrari-requests/job-<identificador>.json (identificador [a-z0-9-]{8,70}), um commit por pedido, sem reutilizar o caminho.
3. Esperar pela execução Ferrari correspondente ao commit no GitHub Actions; identificar o run pela referência de commit, não pelo facto de existir um último run.
4. Exigir no log FERRARI_SKILL_JOB_STATUS=completed e FERRARI_SKILL_END_TO_END=PASS; obter o artefacto ferrari-skill-result-<run_id>, verificar response.zip, report.json (status completed) e os ficheiros reais em artifacts/.
5. Se a ligação/execução não for verificável, indicar a limitação; não simular um PASS nem repetir o pedido às cegas.

## Futuro modo ruflo-team — exigir ativação certificada antes de enviar

`engine/agent_team.py` implementa agora `kind=ruflo-team` com `phase=start|turn|status|recover|finish`, `team_id`, journal privado, fichas de papel, tarefas com revisor distinto, allowlists de ferramentas do catálogo e decisões da mesma IA anfitriã por várias rondas. [Contrato](https://github.com/martaxi-boss/skill-universal/blob/main/docs/RUFLO_HOST_TEAM_ROUNDS_20261107.md). O código não faz chamadas LLM na VPS.

**NÃO ENVIAR ESSE TIPO AINDA:** a release VPS e o validador pinado do workflow não incluem `ruflo-team`. Após CI verde, requer deploy isolado com fallback, atualização mínima do pin de validação (sem alterar SSH), verificação real Ruflo/REA, resposta ZIP e oito serviços saudáveis. O modo anterior `ruflo-host` mantém-se inalterado.

## Contrato JSON — versão 1

Todos os exemplos exigem um nome de ficheiro **novo** no diretório ferrari-requests/. Os exemplos servem apenas como formato, não como comandos que executam automaticamente.

Inventário sem input:

    {"version":1,"id":"inventory-20261103-0001","kind":"inventory"}

Uma operação base:

    {"version":1,"id":"poster-20261103-0002","kind":"operation","operation":"svg-poster","title":"Cartaz Ferrari"}

Invocar uma ação externa:

    {"version":1,"id":"mime-20261103-0003","kind":"invoke","action":"file-mime","input":{"name":"exemplo.json","content_base64":"e30K"}}

Seleção automática por pedido e entrada:

    {"version":1,"id":"auto-20261103-0004","kind":"auto","request":"Converter markdown para docx","input":{"name":"documento.md","content_base64":"IyBOb3ZhIHBhZ2luYQo="}}

Plano com duas etapas dependentes, processado pelo orquestrador **Ferrari já existente**:

    {"version":1,"id":"plan-20261103-0005","kind":"plan","max_parallel":2,"plan":{"version":1,"steps":[{"id":"site","operation":"web-template","layout":"store","title":"Montra Ferrari"},{"id":"analise","operation":"binary-strings","depends_on":["site"],"input_from":"site"}]}}

Um plano com ficheiro de entrada pode usar input codificado de topo e "$input" no passo apropriado; para consumir um resultado anterior, depends_on e input_from. Não aceitar caminhos absolutos da VPS ou scripts arbitrários vindos do utilizador.

**A versão com kind=plan está demonstrada remotamente:** [run #41620077416](https://github.com/martaxi-boss/VPS/actions/runs/41620077416). Para operações simples, ver [Skill #41672372249](https://github.com/martaxi-boss/VPS/actions/runs/41672372249), inventário com ZIP PASS. Consultar engine/ferrari.py e engine/catalog.json para capacidades exatas, em vez de uma lista de ações antiga neste documento.

## Funções REA dentro do único catálogo universal do Ferrari

O REA é um executor como os restantes: as funções autorizadas de `rea-agents@6.8.0` aparecem na mesma lista `functions[]` que as operações de todos os outros programas, e na vista integral `unified_catalog().entries[]` com as dependências e fornecedores. `kind=rea-mcp` mantém-se apenas como protocolo técnico de invocação, não como segundo catálogo ou motor.

A release histórica Ferrari **0a1a4c190a7d33752d6dc3f4418ed44735c8a7dd** passou 197 testes [#41786521407](https://github.com/martaxi-boss/VPS/actions/runs/41786521407). A release ativa atual deve ser lida na VPS, sem presumir que é esse commit. A Skill mantém suporte certificado a pedidos `kind=rea-mcp`, encaminhando `tools/list` e `tools/call` diretamente para o REA original privado, sem usar o projeto REA antigo ou outra Skill. [Catálogo real #41713808747](https://github.com/martaxi-boss/VPS/actions/runs/41713808747), [ELF #41717389118](https://github.com/martaxi-boss/VPS/actions/runs/41717389118) e [Apktool #41717684160](https://github.com/martaxi-boss/VPS/actions/runs/41717684160) — todos PASS com ZIP. Os nomes disponíveis são descobertos no servidor original; **não existe uma lista fixa de duas funções**. O fluxo e o ZIP mantêm-se iguais.

Exemplo de inventário do REA original:

```json
{"version":1,"id":"ferrari-rea-list-20261103-001","kind":"rea-mcp","mcp_requests":[{"method":"tools/list"}]}
```

Exemplo de chamada de uma ferramenta **após consultar o nome e contrato em tools/list** (usar apenas para ficheiros do próprio utilizador, sem segredos no repositório público):

```json
{"version":1,"id":"ferrari-rea-apktool-20261103-002","kind":"rea-mcp","mcp_requests":[{"method":"tools/call","params":{"name":"inspect_apktool_client","arguments":{}}}]}
```

O exemplo `inspect_apktool_client` foi **executado realmente** em [#41717684160](https://github.com/martaxi-boss/VPS/actions/runs/41717684160). Para ferramentas com entrada binária, incluir `input` com ficheiro **completo** codificado em base64, e usar `$input` no argumento de caminho que o schema da ferramenta pedir; o Ferrari resolve essa referência para a sua pasta privada. Não enviar um prefixo ELF incompleto como exemplo de ficheiro real. O REA executa com Node, Ghidra 12.1.4, JDK25, JADX headless MCP 0.7.1 e Apktool 3.0.3 privados.

A comparação histórica dos dois REAs encontrou **229 nomes iguais**, certificada em [#41708905353](https://github.com/martaxi-boss/VPS/actions/runs/41708905353); a execução profunda de Ghidra e JADX passou em [#41710014556](https://github.com/martaxi-boss/VPS/actions/runs/41710014556). **A chamada por kind=rea-mcp já foi certificada ponta a ponta para `tools/list`, `inspect_elf_notes` e `inspect_apktool_client`.** Isso não prova todas as 229 operações, nem prova as 229 operações. Os REAs antigos FINAL e Trial foram posteriormente removidos com ausência comprovada [#41840478411](https://github.com/martaxi-boss/VPS/actions/runs/41840478411); preservar o REA original privado do Ferrari.

## Engenharia reversa do Ferrari

- REA: CLI oficial rea-agents@6.8.0 em /srv/projects/skill-universal/.runtime/npm/rea/node_modules/.bin/rea; duas ações tipadas reais, rea-elf-notes e rea-android-resources. [VPS #41654437939](https://github.com/martaxi-boss/VPS/actions/runs/41654437939) PASS e [Skill REA ELF #41655035184](https://github.com/martaxi-boss/VPS/actions/runs/41655035184) PASS.
- Apktool oficial 3.0.3 privado Ferrari; ação apktool-decode-resources com ficheiro .apk produz diretório com manifesto, recursos e Smali quando presentes. Teste funcional na VPS [#41671631900](https://github.com/martaxi-boss/VPS/actions/runs/41671631900) PASS; **a invocação remota de um APK específico pela Skill ainda não está certificada**.
- Não usar o REA antigo ou programas globais como substitutos do REA/Apktool privados; os fornecedores essenciais Ghidra e JADX têm testes PASS, mas fornecedores opcionais e 229 operações não têm cobertura integral.

## Verificações web e privacidade

vite-build usa ZIP de projeto estático suportado e pode gerar dist/, capturas desktop/móvel e browser-check.json. Ativações de controlos requerem marcadores data-ferrari-test; sem eles reportar not_requested, não alegar que todos os botões passaram.

O repositório VPS é público: base64 não é encriptação. **Nunca publicar segredos, documentos pessoais ou APKs privados neste transporte**; escolher outro canal antes de enviar dados confidenciais. A propriedade do repositório não altera a publicidade do histórico.

## Trabalho Ruflo com a mesma IA anfitriã — apenas após release/validador certificados

`kind=ruflo-host` usa a mesma ponte GitHub existente e recebe `host`, `roles`, `steps`, opcional `input` e `max_parallel` até 2. O Ferrari regista papéis/tarefas no Ruflo MCP por stdio, executa ações privadas do seu catálogo ou REA MCP e devolve `ruflo-host-report.json` mais os ficheiros produzidos. Nunca criar uma Skill ou coordenador adicionais. **Os papéis não fazem inferência LLM na VPS; a IA anfitriã única fornece as decisões.** Para o contrato e exemplo sintético consultar `docs/RUFLO_SINGLE_HOST_CERT_20261106.md` no projeto. Não enviar segredos pelo repositório público.

**Certificação após ativação:** [VPS #42218479317](https://github.com/martaxi-boss/VPS/actions/runs/42218479317) — `kind=ruflo-host` pela ponte normal, duas funções reais (jq e REA), `response.zip`, agentes registados, tarefas completadas e swarm efémero encerrado. O pin do validador foi atualizado sem reconfigurar SSH nem criar outra ponte.


## Catálogo universal via inventário já existente

Após CI, deploy e prova ponta a ponta da revisão unificada, utilizar apenas o pedido que já está autorizado pelo validador pinado:

    {"version":1,"id":"catalogo-integral-20261106","kind":"inventory"}

No `response.zip`, confirmar **`artifacts/inventory.json`** e **`artifacts/catalog.json`**. Este último é uma vista do **catálogo único de 450 registos** (173 programas + 272 funções + 3 dependências + 2 fornecedores), incluindo as 220 funções REA autorizadas. Os 229 nomes MCP anunciados pelo REA original foram observados anteriormente na [VPS #42269934831](https://github.com/martaxi-boss/VPS/actions/runs/42269934831); 229 anunciados não significam 229 funções REA admitidas nem 229 testes funcionais. Uma entrada sem executor não é automaticamente executável. Não publicar segredos nem modificar SSH ou validador.
