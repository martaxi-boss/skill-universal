# Motor Ferrari — Skill Universal Ubuntu

**Estado revisto em 05/11/2026.** Uma única Skill e um único motor/orquestrador Ubuntu privado. O ChatGPT ou Codex interpreta pedidos; o Ferrari seleciona os executores reais, trabalha na VPS e devolve um relatório e ZIP. Não confundir com Engenharia Reversa antiga, Project Leader ou os outros projetos.

**[BOOTSTRAP canónico, provas e pendências](BOOTSTRAP.md)** — ponto de verdade atual. Os relatórios de docs/ e commits antigos descrevem datas históricas e não substituem uma auditoria recente.

## Estado confirmado

- **GitHub:** main **b2869e334d9d68a0c988905e71ce0badec6ba359**, CI [#41922781312](https://github.com/martaxi-boss/skill-universal/actions/runs/41922781312) SUCCESS. Inclui o integrador do Hopper oficial 6.6.1.
- **VPS isolada:** /srv/projects/skill-universal/, com .runtime/, runtimes/, tools/, releases/ e current dentro do projeto. O antigo link /home/ubuntu/.local/share/motor-ferrari foi retirado após migração dos launchers (merge 292aeb7d). A revisão exata de current deve ser lida na VPS.
- **Motor REA próprio:** rea-agents@6.8.0 privado, catálogo de 229 ferramentas MCP, não todas certificadas. Ghidra/JADX/Apktool, Node e Java privados do Ferrari. Hopper 6.6.1 em modo demo tem origem/doctor verificados: [#41921893982](https://github.com/martaxi-boss/VPS/actions/runs/41921893982), [#41922087539](https://github.com/martaxi-boss/VPS/actions/runs/41922087539).
- **Legado:** REA FINAL e Trial antigos removidos e ausência comprovada [#41840478411](https://github.com/martaxi-boss/VPS/actions/runs/41840478411). Preservar o REA privado Ferrari.
- **Entrega real:** [GitHub Actions VPS #41981152670](https://github.com/martaxi-boss/VPS/actions/runs/41981152670) com kind=rea-mcp, status completed, executor Ferrari privado e ZIP. O run posterior [#41981478159](https://github.com/martaxi-boss/VPS/actions/runs/41981478159) apenas confirmou higiene sem tarefa operacional.
- **Contagem operacional anterior:** 40 ações tipadas [#41854771565](https://github.com/martaxi-boss/VPS/actions/runs/41854771565). Não extrapolar para a contagem de hoje nem equiparar a 81 programas detetados historicamente.

## Uma Skill, transporte existente

A Skill está em [skill/motor-universal-linux/](skill/motor-universal-linux/); o motor em engine/ e instaladores em install/. O transporte é o workflow Ferrari existente de martaxi-boss/VPS, por GitHub Actions e SSH, sem coordenador na VPS. O código do validador de pedidos permanece **pinado a 292aeb7d**, anterior à main atual; não alterar essa ponte por conveniência.

O contrato para pedido e resultado está em [references/github-bridge.md](skill/motor-universal-linux/references/github-bridge.md). Inventário, ações tipadas, seleção automática, planos e REA MCP são suportados, mas cada nova capacidade requer testes GitHub, VPS e ZIP reais.

**Pendências concretas:** confirmar release ativa e ferramentas por inventário read-only; alinhar pacote Skill e versão instalada no cliente; certificar vídeo MP4 e outros executores por caso de uso; auditar dependências globais sem desinstalar componentes partilhados ou afetar projetos independentes. A [PR #43](https://github.com/martaxi-boss/skill-universal/pull/43) deve ser reavaliada, porque Calibre e Darktable já tiveram provas independentes de funcionamento.

**Segurança:** não incluir segredos, ficheiros privados ou dados pessoais em repositórios públicos; base64 não cifra. Nenhuma instalação fora da pasta Ferrari, nenhuma alteração silenciosa à ponte SSH e nenhuma nova Skill paralela.
