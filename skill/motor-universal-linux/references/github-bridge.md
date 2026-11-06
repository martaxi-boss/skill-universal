# Ponte Ferrari: ChatGPT → GitHub Actions → VPS → ZIP

**Estado verificado em 06/11/2026, 17h50 UTC:** release Ferrari ativa `7776a34e667d76ae0e980e65449d2b2cc67c2059`, fallback `fe1bb6e7073fdd8a963963909127cde6d570f253` preservado ([ativação VPS #42263466893](https://github.com/martaxi-boss/VPS/actions/runs/42263466893)). O único catálogo é `engine/catalog.json` (176 programas, 40 ações tipadas e, na revisão integral, 220 capacidades MCP REA elegíveis, excluindo 4 JEB comerciais e 5 Hopper demo excluídas com reconciliação dinâmica). A ponte original `martaxi-boss/VPS` continua a validar pedidos com a revisão **pinada** `0b50e1d403deff8f3ccb421edd0b41c397d66b9b` e a executar a release ativa na VPS: [Skill→ZIP #42263667753](https://github.com/martaxi-boss/VPS/actions/runs/42263667753) e [novo inventário #42265187873](https://github.com/martaxi-boss/VPS/actions/runs/42265187873) PASS. O pin histórico `f1f3b03525adec7018d7d629243e7b0fbb7f5087` já não é o do validador. **Não alterar pin/SSH nem confundir GitHub HEAD com release ativa.** Consultar [BOOTSTRAP](https://github.com/martaxi-boss/skill-universal/blob/main/BOOTSTRAP.md).

**Via operacional:** repositório do motor martaxi-boss/skill-universal; repositório de transporte martaxi-boss/VPS; workflow exclusivo .github/workflows/ferrari-skill-request.yml na main. A ponte apenas entrega pedidos e recolhe resultados; a lógica fica no Ferrari (engine/skill_job.py, engine/orchestrator.py). Sem SSH direto no cliente nem regras adicionais no transporte.

## Enviar um pedido

1. Confirmar ligação GitHub autenticada e acesso adequado a martaxi-boss/VPS. A Skill não cria credenciais.
2. Criar **um único ficheiro novo** em ferrari-requests/job-<identificador>.json (identificador [a-z0-9-]{8,70}), um commit por pedido, sem reutilizar o caminho.
3. Esperar pela execução Ferrari correspondente ao commit no GitHub Actions; identificar o run pela referência de commit, não pelo facto de existir um último run.
4. Exigir no log FERRARI_SKILL_JOB_STATUS=completed e FERRARI_SKILL_END_TO_END=PASS; obter o artefacto ferrari-skill-result-<run_id>, verificar response.zip, report.json (status completed) e os ficheiros reais em artifacts/.
5. Se a ligação/execução não for verificável, indicar a limitação; não simular um PASS nem repetir o pedido às cegas.

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

## REA original MCP através da mesma Skill Ferrari

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

No response.zip, confirmar **artifacts/inventory.json** e **artifacts/catalog.json**. Este segundo ficheiro apresenta 396 entradas registadas: 176 programas e 220 funções REA admitidas; 4 JEB comerciais e 5 Hopper demo excluídas, com statuses reais, ações, fornecedores gratuitos e dependências privadas. Os 229 nomes vêm do tools/list realmente obtido na [VPS #42269934831](https://github.com/martaxi-boss/VPS/actions/runs/42269934831); uma entrada não disponível não é executável. Não publicar credenciais, não utilizar providers pagos ou fazer chamadas REA tools/call no mero inventário. O SSH e o validador GitHub não são modificados.
