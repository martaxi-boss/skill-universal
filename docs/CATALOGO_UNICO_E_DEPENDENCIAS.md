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
| Ferramentas distintas (união sem duplicados) | 173 | Inclui candidatos ainda não instalados |
| Ferramentas da base histórica | 71 | Metadados preservados |
| Candidatos Ubuntu selecionados | 55 | Metadados de compatibilidade, sem assumir instalação |
| Projetos de origem/repositórios | 122 | Descoberta de upstreams, não binários instalados |
| Ações tipadas do Ferrari | 40 | Adaptadores existentes, sem aumentar permissões |
| Fornecedores open source locais admitidos | 2 | ImageMagick e SVG; seis clouds fechadas retiradas, sem substituição funcional idêntica |
| Runtimes partilhados inicialmente identificados | 3 | Python 3.12, Node 22 e JDK 25; presença e compatibilidade reportadas separadamente |
| Executáveis privados com caminho registado | 22 | Caminhos definidos no mesmo catálogo, sem fallback global |
| Grupos de comandos CLI privados | 26 | Alias e comandos agrupados numa única fonte |
| Descoberta de módulos Python / pacotes npm | 11 / 9 | Inclui `bpy` e OpenPencil; não significa execução certificada |
| Candidatos a contentores privados | 13 | Presença a verificar sem usar contentores alheios |

O REA faz parte deste **mesmo catálogo**, com `tools/list` e `tools/call` pelo adaptador original `engine/rea_mcp.py`. A lista de **229 nomes distintos** foi obtida do REA privado real em [VPS #42269934831](https://github.com/martaxi-boss/VPS/actions/runs/42269934831). Foram admitidos **220 nomes** no **mesmo** `engine/catalog.json` sob `mcp_capabilities.names`. As nove funções proprietárias/demo restantes foram **eliminadas inteiramente do catálogo Ferrari**, incluindo a antiga lista de bloqueio nominal. O servidor REA original não é alterado, mas a interface do Ferrari devolve somente as 220 funções autorizadas, tanto no inventário como em `tools/list`; `tools/call` só aceita estas 220. Isto não equivale a 229 executáveis instalados separadamente nem certifica 220 funções. Na VPS, o Ferrari confronta os nomes com o `tools/list` vivo e só marca como disponíveis os que correspondem. Sem REA privado, nenhum é dado como disponível.

## Política de dependências

- Quando dois programas exigem a mesma versão/ABI de uma dependência dentro do Ferrari, ambos devem apontar para **um só registo e caminho** (`requires` → `dependencies[].id`).
- Uma atualização reutiliza a dependência já existente quando for compatível e aprovada.
- Se houver requisitos incompatíveis, a versão específica fica isolada na pasta privada do programa, sem interferir com outros programas ou projetos.
- `shared_dependencies` no inventário indica **presente mas ainda não certificado**, ou **não detetado**, com os programas que referenciam o mesmo runtime.
- **A migração do catálogo não reinstala, move, apaga nem deduplica fisicamente bibliotecas existentes.** Qualquer consolidação física futura exige inventário de versões e ABI e teste de recuperação.

## Evolução

Para adicionar um programa, registar uma única entrada `tools[].id` (ou atualizar a já existente), com a sua origem, licença, compatibilidade Ubuntu, opções de execução e `requires`. Só criar uma nova ação `actions[]` quando houver adaptador seguro e validado; candidatos continuam candidatos. Não editar os ficheiros históricos removidos; o validador impede a sua recriação como fontes concorrentes.

Apenas a release com CI e VPS reais PASS deve ser marcada ativa; alteração no GitHub, por si só, não altera a VPS.


## Vista integral do ÚNICO catálogo — 06/11/2026 (revisão GitHub, VPS por atualizar)

- **393 entradas com nomes registados no GitHub:** 173 programas/identificadores Ferrari + 220 capacidades MCP do REA (de 229 anunciadas; nove não admitidas). São tipos de entrada diferentes e não 393 binários instalados. O Penpot, candidato não instalado, foi retirado por decisão do proprietário; o OpenPencil privado continua registado e integrado.
- **Uma única fonte persistente:** engine/catalog.json. Não criar outro inventário fonte, outro catálogo MCP ou outro motor; engine/tool_runtime.py gera a vista de leitura.
- **Ubuntu 24.04 LTS:** programas incompatíveis ou com licença obrigatoriamente paga são recusados; entradas upstream não verificadas continuam explicitamente como candidatas SEM permissão de execução automática. Não inferir compatibilidade do Ubuntu de um README genérico.
- **Fornecedores admitidos:** só ImageMagick local (open source) e SVG local (built-in). Seis serviços cloud fechados, embora com tier gratuito, foram retirados por não possuírem substitutos livres integralmente equivalentes. Nenhum fornecedor cloud faz parte do catálogo ativo. As entradas de `nmap` (licença NPSL e substituto Naabu não equivalente em funcionalidades) e `vscode` (distribuição Microsoft não equivalente a Code-OSS/VSCodium) também foram retiradas. Mantêm-se ferramentas originalmente open source como Ghidra, JADX e AOSP. As nove operações externas não admitidas foram excluídas do catálogo Ferrari, sem lista nominal residual; não estão selecionáveis.
- **Ações tipadas:** 40 adaptadores existentes continuam a usar este mesmo ficheiro. A escolha automática de ações não passa a executar arbitrariamente as 220 subferramentas admitidas do REA: requer contratos de parâmetros corretos e validação específica.
- **Dependências físicas:** só 3 runtimes comuns estão descritos com identificação reutilizável (Python, Node, Java); Python venv, npm, CLI e contentores privados são inspecionados na mesma vista. Isto não significa que as bibliotecas transitivas de todos os programas estejam completamente inventariadas. A lista detalhada de dependências e compatibilidade ABI continua sujeita à reconciliação física; nada foi reinstalado ou eliminado do Ubuntu.
- **Via operacional existente:** pedido {"version":1,"id":"novo-id","kind":"inventory"} através de Skill → GitHub → VPS; após ativar a nova release devolve no mesmo response.zip tanto artifacts/inventory.json como artifacts/catalog.json. O validador pinado de pedidos e o SSH não precisam de novo tipo de pedido nem de alterações.
- **REA vivo:** a vista consulta tools/list de forma só de leitura, sem lançar tools/call nem acionar fornecedores pagos. Reporta "rea_in_sync", "rea_catalog_drift" ou "rea_unavailable"; um nome registado mas não observado não é apresentado como executável.
- **Fase 9:** oito pacotes APT globais antigos permanecem preservados; não fazer purga por semelhança de nomes nem tocar nos projetos independentes.

**Certificação de catálogo 394 na VPS; remoção nominal PR #109 ainda só no GitHub:** [PR #105](https://github.com/martaxi-boss/skill-universal/pull/105) e [PR #106](https://github.com/martaxi-boss/skill-universal/pull/106) integradas; [VPS #42276080241](https://github.com/martaxi-boss/VPS/actions/runs/42276080241) ativou release privada com rollback e 8/8 serviços; [Skill→ZIP #42276249154](https://github.com/martaxi-boss/VPS/actions/runs/42276249154) devolveu 396 entradas na versão anterior, 220 MCP observadas, 229 anunciadas, 9 bloqueadas, 40 ações disponíveis e ImageMagick/SVG locais ativados. **Não é certificação de 396 operações:** apenas três runtimes centrais têm entradas de dependências partilhadas; bibliotecas transitivas e Fase 9 continuam pendentes.

**Sem catálogo de exclusões — GitHub PR #109, CI PASS; VPS pendente:** as nove funções comerciais/demo foram removidas do ficheiro `engine/catalog.json` e da lista pública `tools/list` que o Ferrari apresenta. Não podem ser chamadas por `tools/call`, que usa uma lista estrita das 220 capacidades aprovadas. A origem REA pode continuar a anunciá-las internamente; não modificámos o código do autor nem desinstalámos o REA. As contagens brutas de descoberta são apenas informação de auditoria.

**Nova política (06/11/2026):** a revisão do catálogo com 393 entradas requer CI e readback na VPS antes de ser declarada ativa. As 69 candidatas originais não foram certificadas ou eliminadas em massa por ausência de evidência; apenas os dois casos acima foram removidos, ficando 67 candidatas. Não remover programas instalados nem dependências sem auditoria de consumidores.

**Prova da release anterior (394 entradas):** a [VPS #42282896608](https://github.com/martaxi-boss/VPS/actions/runs/42282896608) tem 394 entradas, 40 ações e dois fornecedores locais e mantém a release `952b0a75ba798471b07053677d53791bd078ed56`. A remoção completa das nove referências nominais e a filtragem direta de `tools/list` foram validadas na [CI #42283957948](https://github.com/martaxi-boss/skill-universal/actions/runs/42283957948), revisão GitHub `ca723ad82043075e82ee790d0c2dcafd5badcbee`; **falta deploy protegido** para afirmar que a VPS também possui a filtragem.

**Decisão Penpot → OpenPencil (06/11/2026):** o Penpot foi retirado do único catálogo por ser uma candidatura pesada a serviço com contentores, não instalada na VPS. O OpenPencil já está integrado no próprio Ferrari, sem instalação do Penpot. No inventário real anterior à revisão ([VPS #42286932312](https://github.com/martaxi-boss/VPS/actions/runs/42286932312)), a seleção original indicou 55/56 presentes e apenas o Penpot em falta. A seleção revista no GitHub passa a 55; a verificação 55/55 da **nova release** depende da sua ativação e readback na VPS.
