# Ferrari — catálogo único e reutilização de dependências

**Fonte persistente ÚNICA de todo o Ferrari:** `engine/catalog.json` (schema 2 + `functions_schema=1`). O índice universal de leitura `entries[]` contém todos os tipos de registo juntos, incluindo REA sem catálogo separado.

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

O REA faz parte deste **mesmo catálogo**, com `tools/list` e `tools/call` pelo adaptador original `engine/rea_mcp.py`. A lista de **229 nomes distintos** foi obtida do REA privado real em [VPS #42269934831](https://github.com/martaxi-boss/VPS/actions/runs/42269934831). Foram admitidas **220 funções REA** como registos individuais na **mesma lista universal `functions[]`** que contém as funções de todos os outros programas. `mcp_capabilities` guarda somente metadados do transporte REA, sem lista própria de nomes. As interfaces legadas `tools/list` e `tools/call` recebem uma vista de leitura derivada deste catálogo único. As nove funções proprietárias/demo restantes foram **eliminadas inteiramente do catálogo Ferrari**, incluindo a antiga lista de bloqueio nominal. O servidor REA original não é alterado, mas a interface do Ferrari devolve somente as 220 funções autorizadas, tanto no inventário como em `tools/list`; `tools/call` só aceita estas 220. Isto não equivale a 229 executáveis instalados separadamente nem certifica 220 funções. Na VPS, o Ferrari confronta os nomes com o `tools/list` vivo e só marca como disponíveis os que correspondem. Sem REA privado, nenhum é dado como disponível.

## Política de dependências

- Quando dois programas exigem a mesma versão/ABI de uma dependência dentro do Ferrari, ambos devem apontar para **um só registo e caminho** (`requires` → `dependencies[].id`).
- Uma atualização reutiliza a dependência já existente quando for compatível e aprovada.
- Se houver requisitos incompatíveis, a versão específica fica isolada na pasta privada do programa, sem interferir com outros programas ou projetos.
- `shared_dependencies` no inventário indica **presente mas ainda não certificado**, ou **não detetado**, com os programas que referenciam o mesmo runtime.
- **A migração do catálogo não reinstala, move, apaga nem deduplica fisicamente bibliotecas existentes.** Qualquer consolidação física futura exige inventário de versões e ABI e teste de recuperação.

## Evolução

Para adicionar um programa, registar ou atualizar a única entrada `tools[].id` no `engine/catalog.json` e, quando existir um adaptador seguro e testado, registar a respetiva interface em `functions[]` do mesmo ficheiro. As vistas `actions[]`, `mcp_capabilities.names` e `base_operations` são derivadas em memória pelo leitor de compatibilidade, nunca catálogos persistentes adicionais. Candidatos continuam candidatos até verificação.

Apenas a release com CI e VPS reais PASS deve ser marcada ativa; alteração no GitHub, por si só, não altera a VPS.

**Estrutura canónica nova (revisão GitHub):** programas `tools[]` (173), funções `functions[]` (272 incluindo REA), dependências `dependencies[]` (3) e fornecedores `providers[]` (2) estão no mesmo ficheiro físico, sob o mesmo motor. A vista `unified_catalog().entries[]` apresenta **450 registos combinados de tipos diferentes**. Não somar estes números como 450 funcionalidades, programas ou testes certificados. `catalog_registry.read_catalog()` reconstrói exclusivamente em memória as interfaces de compatibilidade antigas; não grava outro manifesto nem cria segundo catálogo. Os executores continuam privados do Ferrari.


## Vista integral do ÚNICO catálogo — 06/11/2026 (revisões anteriores identificadas)

- **Fotografia histórica anterior ao catálogo completo:** os 393 nomes registados representavam 173 programas + 220 capacidades REA. O catálogo **atual** já agrega as 52 interfaces base/tipadas na lista `functions[]`, mais três dependências e dois fornecedores, totalizando **450 registos distintos**. Penpot permanece excluído, OpenPencil incluído.
- **Uma única fonte persistente:** engine/catalog.json. Não criar outro inventário fonte, outro catálogo MCP ou outro motor; engine/tool_runtime.py gera a vista de leitura.
- **Ubuntu 24.04 LTS:** programas incompatíveis ou com licença obrigatoriamente paga são recusados; entradas upstream não verificadas continuam explicitamente como candidatas SEM permissão de execução automática. Não inferir compatibilidade do Ubuntu de um README genérico.
- **Fornecedores admitidos:** só ImageMagick local (open source) e SVG local (built-in). Seis serviços cloud fechados, embora com tier gratuito, foram retirados por não possuírem substitutos livres integralmente equivalentes. Nenhum fornecedor cloud faz parte do catálogo ativo. As entradas de `nmap` (licença NPSL e substituto Naabu não equivalente em funcionalidades) e `vscode` (distribuição Microsoft não equivalente a Code-OSS/VSCodium) também foram retiradas. Mantêm-se ferramentas originalmente open source como Ghidra, JADX e AOSP. As nove operações externas não admitidas foram excluídas do catálogo Ferrari, sem lista nominal residual; não estão selecionáveis.
- **Ações tipadas:** 40 adaptadores existentes continuam a usar este mesmo ficheiro. A escolha automática de ações não passa a executar arbitrariamente as 220 subferramentas admitidas do REA: requer contratos de parâmetros corretos e validação específica.
- **Dependências físicas:** só 3 runtimes comuns estão descritos com identificação reutilizável (Python, Node, Java); Python venv, npm, CLI e contentores privados são inspecionados na mesma vista. Isto não significa que as bibliotecas transitivas de todos os programas estejam completamente inventariadas. A lista detalhada de dependências e compatibilidade ABI continua sujeita à reconciliação física; nada foi reinstalado ou eliminado do Ubuntu.
- **Via operacional existente, confirmada:** `kind=inventory` executado via Skill → GitHub → VPS na [execução real #42297678715](https://github.com/martaxi-boss/VPS/actions/runs/42297678715), com `report.json.status=completed` e `response.zip` contendo `artifacts/inventory.json` e `artifacts/catalog.json`. Nenhum novo tipo de pedido, validador ou SSH.
- **REA vivo:** a vista consulta tools/list de forma só de leitura, sem lançar tools/call nem acionar fornecedores pagos. Reporta "rea_in_sync", "rea_catalog_drift" ou "rea_unavailable"; um nome registado mas não observado não é apresentado como executável.
- **Fase 9 — estado atual de 06/11:** os oito pacotes globais finais foram verificados ausentes em [#42299686585](https://github.com/martaxi-boss/VPS/actions/runs/42299686585) e [#42300665770](https://github.com/martaxi-boss/VPS/actions/runs/42300665770); já não há nada a purgar nesses oito nomes. Os oito da fase anterior tinham sido removidos em #42225950692. Continuam por avaliar bibliotecas transitivas e funcionalidades GUI; não remover indiscriminadamente dependências do Ubuntu.

**Histórico anterior à ativação universal (catálogo 394 e 396):** [PR #105](https://github.com/martaxi-boss/skill-universal/pull/105) e [PR #106](https://github.com/martaxi-boss/skill-universal/pull/106) integradas; [VPS #42276080241](https://github.com/martaxi-boss/VPS/actions/runs/42276080241) ativou release privada com rollback e 8/8 serviços; [Skill→ZIP #42276249154](https://github.com/martaxi-boss/VPS/actions/runs/42276249154) devolveu 396 entradas na versão anterior, 220 MCP observadas, 229 anunciadas, 9 bloqueadas, 40 ações disponíveis e ImageMagick/SVG locais ativados. **Não é certificação de 396 operações:** apenas três runtimes centrais têm entradas de dependências partilhadas; bibliotecas transitivas e Fase 9 continuam pendentes.

**Histórico da aprovação e filtragem REA — PR #109, as nove funções comerciais/demo foram removidas do ficheiro `engine/catalog.json` e da lista pública `tools/list` que o Ferrari apresenta. Não podem ser chamadas por `tools/call`, que usa uma lista estrita das 220 capacidades aprovadas. A origem REA pode continuar a anunciá-las internamente; não modificámos o código do autor nem desinstalámos o REA. As contagens brutas de descoberta são apenas informação de auditoria.

**Política histórica de seleção (06/11/2026):** a revisão do catálogo com 393 entradas requer CI e readback na VPS antes de ser declarada ativa. As 69 candidatas originais não foram certificadas ou eliminadas em massa por ausência de evidência; apenas os dois casos acima foram removidos, ficando 67 candidatas. Não remover programas instalados nem dependências sem auditoria de consumidores.

**Prova histórica da release anterior (394 entradas):** a [VPS #42282896608](https://github.com/martaxi-boss/VPS/actions/runs/42282896608) tem 394 entradas, 40 ações e dois fornecedores locais e mantém a release `952b0a75ba798471b07053677d53791bd078ed56`. A remoção completa das nove referências nominais e a filtragem direta de `tools/list` foram validadas na [CI #42283957948](https://github.com/martaxi-boss/skill-universal/actions/runs/42283957948), revisão GitHub `ca723ad82043075e82ee790d0c2dcafd5badcbee`; **falta deploy protegido** para afirmar que a VPS também possui a filtragem.

**Decisão Penpot → OpenPencil (06/11/2026):**

## Catálogo universal efetivo — revisão de 06/11/2026

Esta revisão unifica **todo o catálogo**, não apenas as funções. Existe somente uma origem persistente: `engine/catalog.json`. Os executores continuam a usar o mesmo motor Ferrari. O REA não possui lista de funções independente; todas as suas capacidades aprovadas são registos de `functions[]` com `program: rea`, tal como as funções do FFmpeg, Blender, OpenPencil e restantes aplicações usam o identificador do respetivo executor.

A vista principal `unified_catalog().entries[]` combina **programas + funções + dependências + fornecedores**. Os campos `kind`, `category`, `program`, `status`, `installed` e `selectable` (quando aplicáveis) permitem filtrar qualquer tipo de registo sem criar outro catálogo por tema. Os subcampos `functions`, `actions` e `rea` do relatório são vistas derivadas ou diagnósticos de compatibilidade, nunca fontes persistentes alternativas.

A matriz canónica atual é: **173 programas, 272 interfaces de função (12 operações base, 40 adaptadores tipados, 220 capacidades MCP do REA), 3 runtimes comuns declarados e 2 fornecedores locais = 450 registos de catálogo.** Alguns programas têm operações nativas ainda não integradas; não são ficticiamente contabilizadas como funções Ferrarri disponíveis. A presença, instalação, capacidade de execução e certificação são níveis distintos.

A migração do JSON para `functions[]` foi de metadados e leitura. A [implantação protegida #42294843737](https://github.com/martaxi-boss/VPS/actions/runs/42294843737) ativou a revisão com rollback, e a [prova da Skill #42297678715](https://github.com/martaxi-boss/VPS/actions/runs/42297678715) confirmou as 450 entradas após a higiene. A ponte de pedidos, SSH, Supervisor e outros projetos mantiveram-se sem alterações.

## Higienização física pós-ativação — Ferrari isolado

**Higiene física comprovada em 06/11/2026:** [#42295330408](https://github.com/martaxi-boss/VPS/actions/runs/42295330408) removeu uma release obsoleta; [pré-visualização #42297058254](https://github.com/martaxi-boss/VPS/actions/runs/42297058254) identificou nove cópias com `.runtime` vazia, cuja inexistência de dados foi confirmada pela [auditoria profunda #42296172655](https://github.com/martaxi-boss/VPS/actions/runs/42296172655); [aplicação #42297182419](https://github.com/martaxi-boss/VPS/actions/runs/42297182419) eliminou as nove (19 251 200 bytes libertados), preservando `current`, fallback e 8/8 serviços protegidos. [Inventário pós-limpeza #42297678715](https://github.com/martaxi-boss/VPS/actions/runs/42297678715) confirmou novamente o catálogo universal e as ações disponíveis. O histórico GitHub permanece como prova, **não** como outro catálogo operacional.

O GitHub conserva o histórico dos commits antigos, mas o código operacional usa apenas `engine/catalog.json`. O ficheiro `engine/catalog_registry.py` é **leitor do mesmo catálogo**, não um segundo catálogo. Ficheiros obsoletos como `engine/tool_actions.json`, `engine/ubuntu_selection.json`, `engine/providers.json`, `engine/ferrari_registry.json` e `engine/ferrari_expansion.json` não podem ressurgir na release atual.

O procedimento `install/vps-universal-catalog-hygiene.py` faz **auditoria somente de leitura por defeito**. Só aceita remoção com `--apply` e com o SHA exato da release ativa, SHA distinto do fallback, catálogo de 450 registos (incluindo as 272 funções no mesmo `functions[]`), caminhos reais sem escapes e presença do código anterior de recuperação. A eliminação abrange **somente snapshots antigos, imutáveis e reconhecidos** em `/srv/projects/skill-universal/releases/<sha>`, sem referências nos processos ou apontadores do projeto. Preserva automaticamente `current`, o fallback indicado, diretórios desconhecidos, releases com dados próprios, `tools/`, `runtimes/`, `.runtime/`, trabalhos, segredos e outros projetos. Não elimina nada da raiz Ubuntu, pacotes APT, serviços, SSH nem dependências compartilhadas com outros projetos.

**Ordem obrigatória:** (1) CI e testes da nova release; (2) verificação read-only da VPS; (3) ativação protegida com rollback; (4) inventário real e artefactos `response.zip` confirmando 450 registos; (5) pré-visualização com lista de candidatos; (6) limpeza apenas das releases identificadas como seguras; (7) novo inventário e verificação dos serviços protegidos. Se qualquer condição falhar, **não eliminar**. O histórico GitHub não é apagado, para manter rastreabilidade e rollback.

## Fecho F10 — 07/11/2026

A [ativação #42314959728](https://github.com/martaxi-boss/VPS/actions/runs/42314959728) promoveu a release `205c6f0e` com fallback `7bf6dcec` (ambas 450). [Primeira prévia #42315141299](https://github.com/martaxi-boss/VPS/actions/runs/42315141299) bloqueou por uma pasta de estado não classificada. [Auditoria read-only #42315365287](https://github.com/martaxi-boss/VPS/actions/runs/42315365287) confirmou `.runtime` vazia. [Nova prévia #42315656543](https://github.com/martaxi-boss/VPS/actions/runs/42315656543) e [limpeza #42315724016](https://github.com/martaxi-boss/VPS/actions/runs/42315724016) PASS: só o snapshot 394 foi apagado; 2 433 024 bytes libertados; 8/8 serviços ativos. [Relatório](FASE10_CATALOGO_HIGIENE_FINAL_20261107.md).
