# Ferrari — catálogo único e reutilização de dependências

**Fonte única de informação sobre ferramentas:** `engine/catalog.json` (schema 2).

## Hierarquia

1. **Skill do ChatGPT:** interpreta a ordem; não executa comandos na VPS nem decide dependências.
2. **Motor Ferrari existente:** `engine/skill_job.py`, `engine/orchestrator.py`, `engine/tool_runtime.py` e `engine/ferrari.py`. Não se instala outro coordenador.
3. **Um catálogo de ferramentas:** regista os programas Ubuntu, candidatos, ações tipadas, origem, fornecedor, licença e dependências partilháveis.
4. **Execução privada:** só caminhos verificados dentro de `/srv/projects/skill-universal`, sem fallback silencioso para programas globais nem partilha com outros projetos.
5. **Verificação por trabalho:** resultado real, logs e artefactos verificáveis; catálogo ou arranque não equivalem a prova funcional.

## Cobertura de dados — não confundir com instalação

| Registo lógico no catálogo | Quantidade | Significado |
| --- | ---: | --- |
| Ferramentas distintas (união sem duplicados) | 176 | Inclui candidatos ainda não instalados |
| Ferramentas da base histórica | 71 | Metadados preservados |
| Candidatos Ubuntu selecionados | 56 | Metadados de compatibilidade, sem assumir instalação |
| Projetos de origem/repositórios | 125 | Descoberta de upstreams, não binários instalados |
| Ações tipadas do Ferrari | 40 | Adaptadores existentes, sem aumentar permissões |
| Fornecedores admitidos sem custo obrigatório | 8 | 2 locais e 6 cloud free-tier, sujeitos a configuração/verificação; 4 fornecedores sem garantia de gratuitidade retirados |
| Runtimes partilhados inicialmente identificados | 3 | Python 3.12, Node 22 e JDK 25; presença e compatibilidade reportadas separadamente |
| Executáveis privados com caminho registado | 22 | Caminhos definidos no mesmo catálogo, sem fallback global |
| Grupos de comandos CLI privados | 26 | Alias e comandos agrupados numa única fonte |
| Descoberta de módulos Python / pacotes npm | 11 / 9 | Inclui `bpy` e OpenPencil; não significa execução certificada |
| Candidatos a contentores privados | 14 | Presença a verificar sem usar contentores alheios |

O REA faz parte deste **mesmo catálogo**, com `tools/list` e `tools/call` pelo adaptador original `engine/rea_mcp.py`. A lista de **229 nomes distintos** foi obtida do REA privado real em [VPS #42269934831](https://github.com/martaxi-boss/VPS/actions/runs/42269934831) e foi registada no **mesmo** `engine/catalog.json` sob `mcp_capabilities.names`. Isto não equivale a 229 executáveis instalados separadamente nem certifica 229 funções. Na VPS, o Ferrari confronta os nomes com o `tools/list` vivo e só marca como disponíveis os que correspondem. Sem REA privado, nenhum é dado como disponível.

## Política de dependências

- Quando dois programas exigem a mesma versão/ABI de uma dependência dentro do Ferrari, ambos devem apontar para **um só registo e caminho** (`requires` → `dependencies[].id`).
- Uma atualização reutiliza a dependência já existente quando for compatível e aprovada.
- Se houver requisitos incompatíveis, a versão específica fica isolada na pasta privada do programa, sem interferir com outros programas ou projetos.
- `shared_dependencies` no inventário indica **presente mas ainda não certificado**, ou **não detetado**, com os programas que referenciam o mesmo runtime.
- **A migração do catálogo não reinstala, move, apaga nem deduplica fisicamente bibliotecas existentes.** Qualquer consolidação física futura exige inventário de versões e ABI e teste de recuperação.

## Evolução

Para adicionar um programa, registar uma única entrada `tools[].id` (ou atualizar a já existente), com a sua origem, licença, compatibilidade Ubuntu, opções de execução e `requires`. Só criar uma nova ação `actions[]` quando houver adaptador seguro e validado; candidatos continuam candidatos. Não editar os ficheiros históricos removidos; o validador impede a sua recriação como fontes concorrentes.

Apenas a release com CI e VPS reais PASS deve ser marcada ativa; alteração no GitHub, por si só, não altera a VPS.


## Vista integral do ÚNICO catálogo — 06/11/2026

- **401 entradas com nomes registados:** 176 programas/identificadores Ferrari + 229 capacidades MCP do REA original. São tipos de entrada diferentes e não 401 binários instalados.
- **Uma única fonte persistente:** engine/catalog.json. Não criar outro inventário fonte, outro catálogo MCP ou outro motor; engine/tool_runtime.py gera a vista de leitura.
- **Ubuntu 24.04 LTS:** programas incompatíveis ou com licença obrigatoriamente paga são recusados; entradas upstream não verificadas continuam explicitamente como candidatas SEM permissão de execução automática. Não inferir compatibilidade do Ubuntu de um README genérico.
- **Fornecedores admitidos:** apenas opções locais livres e candidatos cloud declarados free-tier sem ativação de modalidade paga. Os antigos host-model, huggingface-inference, nvidia-nim-dev e pollinations foram retirados dos fornecedores admitidos porque não havia garantia suficiente de ausência de custo obrigatório. Não são apagados do histórico Git. Nenhum fornecedor cloud é ligado ou cobrado automaticamente.
- **Ações tipadas:** 40 adaptadores existentes continuam a usar este mesmo ficheiro. A escolha automática de ações não passa a executar arbitrariamente as 229 subferramentas do REA: requer contratos de parâmetros corretos e validação específica.
- **Dependências físicas:** só 3 runtimes comuns estão descritos com identificação reutilizável (Python, Node, Java); Python venv, npm, CLI e contentores privados são inspecionados na mesma vista. Isto não significa que as bibliotecas transitivas de todos os programas estejam completamente inventariadas. A lista detalhada de dependências e compatibilidade ABI continua sujeita à reconciliação física; nada foi reinstalado ou eliminado do Ubuntu.
- **Via operacional existente:** pedido {"version":1,"id":"novo-id","kind":"inventory"} através de Skill → GitHub → VPS; após ativar a nova release devolve no mesmo response.zip tanto artifacts/inventory.json como artifacts/catalog.json. O validador pinado de pedidos e o SSH não precisam de novo tipo de pedido nem de alterações.
- **REA vivo:** a vista consulta tools/list de forma só de leitura, sem lançar tools/call nem acionar fornecedores pagos. Reporta "rea_in_sync", "rea_catalog_drift" ou "rea_unavailable"; um nome registado mas não observado não é apresentado como executável.
- **Fase 9:** oito pacotes APT globais antigos permanecem preservados; não fazer purga por semelhança de nomes nem tocar nos projetos independentes.

**Porta de certificação:** PR CI PASS → release protegida na VPS com fallback → pedido real kind=inventory → confirmar 401 entradas, 229 MCP descobertas e 40 ações disponíveis, sem serviços externos afetados. Antes destas três provas, este texto descreve a implementação no GitHub, não a VPS ativa.

**Exclusões comerciais verificadas:** `inspect_jeb_client`, `open_jeb_project`, `list_jeb_units` e `decompile_jeb_item`. O JEB é comercial; estas quatro capacidades do REA permanecem visíveis na fonte REA original, mas NÃO pertencem à seleção admitida pelo Ferrari. O motor recusa chamadas diretas a estes nomes e ignora-os como divergência esperada durante `tools/list`. Isto não altera ou remove a instalação REA existente.
