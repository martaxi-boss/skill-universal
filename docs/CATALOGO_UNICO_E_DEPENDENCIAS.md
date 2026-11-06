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
| Fornecedores declarados | 12 | Serviços locais e cloud, sem assumir configuração |
| Runtimes partilhados inicialmente identificados | 3 | Python 3.12, Node 22 e JDK 25; presença e compatibilidade reportadas separadamente |
| Executáveis privados com caminho registado | 22 | Caminhos definidos no mesmo catálogo, sem fallback global |
| Grupos de comandos CLI privados | 26 | Alias e comandos agrupados numa única fonte |
| Descoberta de módulos Python / pacotes npm | 11 / 9 | Inclui `bpy` e OpenPencil; não significa execução certificada |
| Candidatos a contentores privados | 14 | Presença a verificar sem usar contentores alheios |

O REA faz parte deste **mesmo catálogo**, com `tools/list` e `tools/call` pelo adaptador original `engine/rea_mcp.py`. As subferramentas MCP são descobertas em tempo de execução; **não** se declaram 229 instalações locais fictícias nem se cria um segundo catálogo ou coordenador.

## Política de dependências

- Quando dois programas exigem a mesma versão/ABI de uma dependência dentro do Ferrari, ambos devem apontar para **um só registo e caminho** (`requires` → `dependencies[].id`).
- Uma atualização reutiliza a dependência já existente quando for compatível e aprovada.
- Se houver requisitos incompatíveis, a versão específica fica isolada na pasta privada do programa, sem interferir com outros programas ou projetos.
- `shared_dependencies` no inventário indica **presente mas ainda não certificado**, ou **não detetado**, com os programas que referenciam o mesmo runtime.
- **A migração do catálogo não reinstala, move, apaga nem deduplica fisicamente bibliotecas existentes.** Qualquer consolidação física futura exige inventário de versões e ABI e teste de recuperação.

## Evolução

Para adicionar um programa, registar uma única entrada `tools[].id` (ou atualizar a já existente), com a sua origem, licença, compatibilidade Ubuntu, opções de execução e `requires`. Só criar uma nova ação `actions[]` quando houver adaptador seguro e validado; candidatos continuam candidatos. Não editar os ficheiros históricos removidos; o validador impede a sua recriação como fontes concorrentes.

Apenas a release com CI e VPS reais PASS deve ser marcada ativa; alteração no GitHub, por si só, não altera a VPS.
