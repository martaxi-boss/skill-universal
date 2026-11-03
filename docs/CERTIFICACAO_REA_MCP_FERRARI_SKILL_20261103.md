# Ferrari — certificação do REA original pela Skill e decisão sobre REA FINAL (03/11/2026)

**Estado técnico:** Ferrari independente operacional, com **acesso MCP real verificado** através da Skill única. **REA FINAL antigo: NÃO APAGAR ainda.** Certificar uma operação não prova todas as ferramentas nem migra os pedidos ainda enviados ao projeto anterior.

## Provas de instalação Ferrari (VPS Ubuntu 24.04)

- **Release ativa:** `c5b07ed225299ad80aa2d46c28441d17f281f695`, [deploy #41716562469](https://github.com/martaxi-boss/VPS/actions/runs/41716562469) **SUCCESS**, **164 testes PASS**, Valkey/Prometheus privados instalados, `FERRARI_EXTERNAL_REA_DEPENDENCY=NONE`, `FERRARI_REA_PROVIDER_GHIDRA=PASS`, `FERRARI_REA_PROVIDER_JADX=PASS`, `FERRARI_PRIVATE_REA_ELF_REAL=PASS`, `FERRARI_PRIVATE_REA_ANDROID_REAL=PASS`, `FERRARI_ONLY_HYGIENE=PASS`.
- **Raiz física privada:** `/srv/projects/skill-universal`. O caminho histórico `/home/ubuntu/.local/share/motor-ferrari` é somente um link simbólico **para o mesmo projeto**, como demonstra [diagnóstico #41714658308](https://github.com/martaxi-boss/VPS/actions/runs/41714658308). O código permite exclusivamente este alias; links para outros projetos são rejeitados (PRs [#36](https://github.com/martaxi-boss/skill-universal/pull/36) e [#37](https://github.com/martaxi-boss/skill-universal/pull/37)).
- **Ferramentas próprias, não compartilhadas com REA FINAL:** `rea-agents@6.8.0` original no npm privado do Ferrari, Ghidra 12.1.4 para o REA, Ghidra 12.2 para outros usos, JADX headless MCP 0.7.1, JADX CLI 1.5.6, Apktool 3.0.3, Node 22.23.4, Java 25.0.5.
- **Fornecedor profundo:** [#41710014556](https://github.com/martaxi-boss/VPS/actions/runs/41710014556), análise real de ELF via Ghidra e classe Android sintética via JADX headless MCP, PASS.

## Paridade e execução MCP

1. **Paridade de nomes MCP:** [#41708905353](https://github.com/martaxi-boss/VPS/actions/runs/41708905353), 229 nomes no REA FINAL e 229 nomes no REA privado Ferrari, 0 nomes diferentes. **Não significa 229 implementações validadas nem disponibilidade de todas via Skill.**
2. **Catálogo obtido pela Skill Ferrari:** [#41713808747](https://github.com/martaxi-boss/VPS/actions/runs/41713808747), `kind=rea-mcp` / `tools/list` real, `FERRARI_SKILL_JOB_STATUS=completed`, ZIP com `rea-mcp-result.json` de 229 ferramentas.
3. **Execução MCP real de `inspect_elf_notes`:** [#41717389118](https://github.com/martaxi-boss/VPS/actions/runs/41717389118), `tools/call` num ELF64 sintético de 320 bytes enviado pela Skill. `report.json.status=completed`, `isError` ausente, `structuredContent` válido, SHA-256 `379cd93d02f961ce6e2d9952fb6b2ae3a6ac8d0945e3068181d5379592fa9c67`, GNU build-id exato `112233445566778899aabbccddeeff0011223344`.
4. **Execução MCP real de `inspect_apktool_client`:** [#41717684160](https://github.com/martaxi-boss/VPS/actions/runs/41717684160), `tools/call`, ZIP e relatório `completed`. Resultado structuredContent reconhece fornecedor `apktool`, versão `3.0.3`, caminho privado `.../motor-ferrari/tools/apktool-3.0.3/bin/apktool`.

5. **Captura de processo, função efetivamente chamada pelo projeto antigo:** [#41718385142](https://github.com/martaxi-boss/VPS/actions/runs/41718385142), `tools/call capture_process_scenario` sobre `/usr/bin/printf` (teste sintético), retorno real `exit.code=0`, saída `Ferrari-REA-MCP-process-check`, PTY `node-pty`, limpeza temporária PASS. O REA FINAL possui essa mesma ferramenta no seu último pedido observado; **não executámos na Ferrari os comandos concretos desse pedido antigo**.

**Migração de pedidos MCP sem ponte adicional:** a branch antiga `rea/one-skill-bridge-20261023` recebe JSON com `{request_id,mcp_requests}`; a Skill Ferrari única recebe `{version:1,id,kind:"rea-mcp",mcp_requests}`. As mensagens `tools/list` e `tools/call` podem conservar método, nome e argumentos desde que cumpram o contrato atual e os caminhos de entrada sejam reencaminhados para o workspace privado Ferrari com `$input`. A ferramenta `capture_process_scenario` já passou um cenário benigno. **Não modificar ou redirecionar automaticamente os pedidos antigos enquanto ainda forem usados.**

**As cinco provas são independentes de invocação do REA FINAL**. A Skill usa a ponte GitHub existente (workflow `ferrari-skill-request.yml`), sem novo coordenador, nova Skill ou SSH próprio.

## Higienização e duplicações

- [#41701443735](https://github.com/martaxi-boss/VPS/actions/runs/41701443735): 984 383 488 bytes da cache npm Ferrari removidos, serviços e executores preservados.
- [#41704431188](https://github.com/martaxi-boss/VPS/actions/runs/41704431188): 239 403 008 bytes de caches globais elegíveis removidos, serviços preservados.
- **Total recuperado e medido:** 1 223 786 496 bytes (~1,14 GiB) nessa sequência.
- Duas cópias idênticas `torch/lib/libtorch_cpu.so` em ambientes ComfyUI e Docling (440 280 512 bytes cada) **mantidas** devido a isolamento por ambiente e ausência de prova segura de consolidação.
- **Não foram removidos** o REA FINAL, instalações Python, Android SDK, APT globais, fornecedores de outros projetos ou bases de dados.
- 15 programas GUI APT foram instalados em Ubuntu de forma global; **não são instalações fisicamente contidas na pasta Ferrari**, e não há certificação da utilização GUI completa numa VPS sem sessão gráfica.

## O que impede apagar o REA FINAL antigo

- **Workflow antigo ainda ativo:** branch `rea/one-skill-bridge-20261023` em `martaxi-boss/VPS`; a execução [#41715856540](https://github.com/martaxi-boss/VPS/actions/runs/41715856540) foi um pedido `skill-request:` realmente entregue ao REA FINAL na VPS. A sua ponte `.github/workflows/rea-mcp-transport-20261027.yml` existe nessa branch, distinta do Ferrari.
- **Equivalência funcional insuficiente:** há provas de duas ferramentas MCP e dois provedores profundos, mas não dos 229 fluxos, formatos, fornecedores opcionais ou procedimentos usados pelo outro projeto.
- **Dependência de cliente:** a Skill REA FINAL instalada ou invocada pelo utilizador continua a chamar o workflow antigo. Atualizar o Ferrari no GitHub **não substitui automaticamente** a versão instalada de qualquer Skill no ChatGPT.
- **Remoção segura ainda por certificar:** inventariar todos os caminhos exclusivos do REA antigo, consumidores externos, backups/rollback, testar previamente os casos realmente usados pelo utilizador pela Skill Ferrari, mudar os pedidos para o Ferrari e confirmar ausência de novos pedidos antigos. Só depois retirar a ligação antiga e a sua instalação, com medição do espaço e testes pós-remover.

**Decisão:** `GO` para continuar a utilizar e testar o **REA privado do Ferrari** pela Skill única. `NO-GO` para apagar o **REA FINAL antigo** antes de migrar e cessar pedidos ao seu workflow. Nada do REA FINAL foi modificado ou apagado nesta fase.

## Ponto de continuidade

Manter uma única instalação Ferrari dentro de `/srv/projects/skill-universal`; não misturar bibliotecas, Java, Node, fornecedores ou ferramentas dos outros projetos. O Ferrari tem muitos programas além do REA; a conclusão da engenharia reversa não certifica todos os domínios universais. Conferir execução real e estado de cada capacidade, em vez de assumir que inventário = funcionalidade.
