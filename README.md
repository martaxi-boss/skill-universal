# Motor Ferrari — Skill Universal Ubuntu

**Estado revisto em 05/11/2026.** Uma única Skill e um único motor/orquestrador Ubuntu privado. O ChatGPT ou Codex interpreta pedidos; o Ferrari seleciona os executores reais, trabalha na VPS e devolve um relatório e ZIP. Não confundir com Engenharia Reversa antiga, Project Leader ou os outros projetos.

**[BOOTSTRAP canónico, provas e pendências](BOOTSTRAP.md)** — ponto de verdade atual. Os relatórios de docs/ e commits antigos descrevem datas históricas e não substituem uma auditoria recente.

## Estado confirmado

- **Ferrari Fase 7 ativo na VPS:** release `758e1b435317fa26277b332b75bc47c67910be81`, fallback F6 `146145d5ada9c13e368df18727e4dbf4f5807664`, ambas dentro de `/srv/projects/skill-universal/`. [Ativação #42098645092](https://github.com/martaxi-boss/VPS/actions/runs/42098645092), [DAG persistente #42098800995](https://github.com/martaxi-boss/VPS/actions/runs/42098800995), [Skill→ZIP #42099036932](https://github.com/martaxi-boss/VPS/actions/runs/42099036932) e [saúde #42099108182](https://github.com/martaxi-boss/VPS/actions/runs/42099108182): **PASS**, 40/40 ações privadas. [Certificado F7](docs/CERTIFICACAO_FASE7_20261105.md) e [desinstalação isolada](docs/DESINSTALACAO_ISOLADA_FERRARI.md).

- **Código Ferrari histórico:** commit **b2869e334d9d68a0c988905e71ce0badec6ba359**, anterior às atualizações,  CI [#41922781312](https://github.com/martaxi-boss/skill-universal/actions/runs/41922781312) SUCCESS. Inclui o integrador do Hopper oficial 6.6.1.
- **VPS isolada:** /srv/projects/skill-universal/, com .runtime/, runtimes/, tools/, releases/ e current dentro do projeto. O antigo link /home/ubuntu/.local/share/motor-ferrari foi retirado após migração dos launchers (merge 292aeb7d). A revisão exata de current deve ser lida na VPS.
- **Motor REA próprio:** rea-agents@6.8.0 privado, catálogo de 229 ferramentas MCP, não todas certificadas. Ghidra/JADX/Apktool, Node e Java privados do Ferrari. Hopper 6.6.1 em modo demo tem origem/doctor verificados: [#41921893982](https://github.com/martaxi-boss/VPS/actions/runs/41921893982), [#41922087539](https://github.com/martaxi-boss/VPS/actions/runs/41922087539).
- **Legado:** REA FINAL e Trial antigos removidos e ausência comprovada [#41840478411](https://github.com/martaxi-boss/VPS/actions/runs/41840478411). Preservar o REA privado Ferrari.
- **Entrega real:** [GitHub Actions VPS #41981152670](https://github.com/martaxi-boss/VPS/actions/runs/41981152670) com kind=rea-mcp, status completed, executor Ferrari privado e ZIP. O run posterior [#41981478159](https://github.com/martaxi-boss/VPS/actions/runs/41981478159) apenas confirmou higiene sem tarefa operacional.
- **Contagem operacional anterior:** 40 ações tipadas [#41854771565](https://github.com/martaxi-boss/VPS/actions/runs/41854771565). Não extrapolar para a contagem de hoje nem equiparar a 81 programas detetados historicamente.

## Uma Skill, transporte existente

A Skill está em [skill/motor-universal-linux/](skill/motor-universal-linux/); o motor em engine/ e instaladores em install/. O transporte é o workflow Ferrari existente de martaxi-boss/VPS, por GitHub Actions e SSH, sem coordenador na VPS. O código do validador de pedidos permanece **pinado a 292aeb7d**, anterior à main atual; não alterar essa ponte por conveniência.

O contrato para pedido e resultado está em [references/github-bridge.md](skill/motor-universal-linux/references/github-bridge.md). Inventário, ações tipadas, seleção automática, planos e REA MCP são suportados, mas cada nova capacidade requer testes GitHub, VPS e ZIP reais.

**Pendências concretas:** verificar separadamente a versão instalada da Skill no cliente ChatGPT (o ZIP gerado em CI não atualiza automaticamente a instalação); limites rígidos CPU/RAM e agentes Ruflo com modelos não certificados; classificar consumidores dos 16 pacotes Ubuntu globais e concluir auditoria transversal/desinstalação reversível nas fases 9 e 10. A [PR #43](https://github.com/martaxi-boss/skill-universal/pull/43) permanece assunto independente e só deve ser reavaliada com provas próprias.

**Segurança:** não incluir segredos, ficheiros privados ou dados pessoais em repositórios públicos; base64 não cifra. Nenhuma instalação fora da pasta Ferrari, nenhuma alteração silenciosa à ponte SSH e nenhuma nova Skill paralela.
