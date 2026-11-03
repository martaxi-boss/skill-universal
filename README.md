# Motor Ferrari — Skill Universal Ubuntu

**Situação verificada em 03/11/2026.** Uma Skill universal, um motor Ubuntu independente e um orquestrador próprio. O ChatGPT/Codex interpreta e orienta; o Ferrari seleciona os executores reais na VPS e devolve ficheiros, ZIP e relatórios. Não confundir com o projeto REA antigo.

**[BOOTSTRAP canónico e pendências](BOOTSTRAP.md)** — única fonte de verdade para a fotografia operacional. Os relatórios antigos em docs/ e o histórico Git são históricos, não o estado corrente.

## Instalação real e provas

Ver [certificação atualizada da Skill Ferrari e decisão de desinstalação do REA FINAL](docs/CERTIFICACAO_REA_MCP_FERRARI_SKILL_20261103.md), com os IDs de execução e os caminhos de projeto certificados.

- **Higiene real da VPS:** [inventário detalhado #41700386577](https://github.com/martaxi-boss/VPS/actions/runs/41700386577) e [limpeza #41701443735](https://github.com/martaxi-boss/VPS/actions/runs/41701443735) PASS. Removida **apenas a cache de downloads npm privada do Ferrari**, com **984 383 488 bytes (~939 MiB)** libertados e ~13,95 GiB livres depois. REA/Ruflo/Apktool e serviços de outros projetos preservados. O workflow temporário de limpeza foi retirado após execução; **dependências Python duplicadas ainda não foram removidas nem declaradas seguras para eliminar**.
- **[VPS #41716562469](https://github.com/martaxi-boss/VPS/actions/runs/41716562469): SUCCESS, 164 testes PASS**, fornecedores REA privados Ghidra/JADX, Valkey e Prometheus privados; release ativa **c5b07ed225299ad80aa2d46c28441d17f281f695**.
- [Skill inventário #41672372249](https://github.com/martaxi-boss/VPS/actions/runs/41672372249): FERRARI_SKILL_END_TO_END=PASS, relatório e ZIP; 81 programas detetados em catálogos combinados, 55 dos 56 candidatos Ubuntu detetados, 25 ações externas.
- [REA próprio + Apktool #41654437939](https://github.com/martaxi-boss/VPS/actions/runs/41654437939): análise ELF e recursos Android, Apktool 3.0.3 privado; [Skill REA ELF #41655035184](https://github.com/martaxi-boss/VPS/actions/runs/41655035184) confirmou pedido e ZIP reais.
- [Plano remoto composto #41620077416](https://github.com/martaxi-boss/VPS/actions/runs/41620077416): orquestração com dependências e artefactos no ZIP.

Estes números não significam que todos os programas detetados tenham ações ou testes funcionais. Em 03/11: 15 aplicações gráficas APT instaladas mas sem interface interativa certificada; ComfyUI CPU sem modelos e sem inferência certificada; Penpot preparado mas ainda sem Docker/Compose funcional.

## Instalações isoladas do Ferrari

- Raiz física: **/srv/projects/skill-universal/**; /home/ubuntu/.local/share/motor-ferrari é um link exclusivo para a mesma pasta [verificação #41714658308](https://github.com/martaxi-boss/VPS/actions/runs/41714658308).
- REA original distribuído por npm: rea-agents@6.8.0 dentro de .runtime/npm/rea; não é o REA do outro projeto.
- Java Temurin 25.0.5, Node.js 22.23.4, Ghidra 12.2, JADX 1.5.6 e Apktool **3.0.3** privados; fornecedores REA também privados: Ghidra 12.1.4 e JADX headless MCP 0.7.1. [Teste funcional profundo #41710014556](https://github.com/martaxi-boss/VPS/actions/runs/41710014556) PASS.
- Ferramentas APT globais Ubuntu pertencem ao sistema: não presumir que são exclusivas do Ferrari nem removê-las ao desinstalar outro projeto.

**O REA antigo ainda não pode ser removido:** os 229 nomes MCP coincidem [#41708905353](https://github.com/martaxi-boss/VPS/actions/runs/41708905353), e a Skill Ferrari já executou as ferramentas reais inspect_elf_notes [#41717389118](https://github.com/martaxi-boss/VPS/actions/runs/41717389118) e inspect_apktool_client [#41717684160](https://github.com/martaxi-boss/VPS/actions/runs/41717684160). Porém, o workflow antigo do REA FINAL continua a receber pedidos; faltam migração, verificação de consumidores e rollback. Não apagar a instalação REA própria do Ferrari.

## Funcionamento

A Skill única está em [skill/motor-universal-linux/](skill/motor-universal-linux/); o motor em engine/ e o instalador em install/. O transporte operacional é feito por um workflow exclusivo no repositório [martaxi-boss/VPS](https://github.com/martaxi-boss/VPS), que envia pedidos autenticados à VPS e recolhe resposta ZIP. O GitHub é transporte, não orquestrador adicional.

Comandos principais dentro da release Ferrari:

- python3 -m engine.ferrari doctor — verificar capacidades.
- python3 -m engine.ferrari tools — inventariar programas detetados.
- python3 -m engine.ferrari actions — inventariar operações disponíveis.
- python3 -m engine.ferrari route 'pedido' --input ficheiro — pré-visualizar seleção.
- python3 -m engine.orchestrator --plan plano.json --workspace pasta --execute — executar DAG validado no ambiente autorizado.

Pela Skill, os pedidos suportados incluem kind=inventory, operation, invoke, auto, plan e **rea-mcp** (tools/list e tools/call diretos sobre o REA original privado). [Contrato GitHub→VPS→ZIP](skill/motor-universal-linux/references/github-bridge.md); [protocolos por domínio](skill/motor-universal-linux/references/protocols.md).

## Segurança, limites e próximos passos

O repositório VPS usado no transporte pode ser público: base64 **não cifra** dados. Não publicar credenciais, documentos privados ou dados pessoais. Não executar instalações ou apagar outros projetos sem autorização; preferir auditorias só de leitura e alterações mínimas verificáveis.

**Prioridades:** terminar a higienização documental e de espaço; auditar proveniência de REA/Java/Node/Python/Ghidra/JADX/Apktool, fornecedores e configurações; testar independência do REA antigo e realizar certificação final; integrar funcionalidades de programas já instalados conforme necessidades reais. Não criar Skills ou camadas adicionais.

Histórico extenso anterior: [README no commit 77f20a96](https://github.com/martaxi-boss/skill-universal/blob/77f20a96a90e507d12cb2579e5c0554e96eed795/README.md) e relatórios em [docs/](docs/).
