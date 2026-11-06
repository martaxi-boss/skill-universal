# Ferrari — OpenPencil CLI privado 0.16.0

**Origem oficial:** https://github.com/open-pencil/open-pencil (MIT).
**Pacote fixo:** `@open-pencil/cli@0.16.0`.
**Objetivo:** começar por importação HTML/CSS e exportação SVG/HTML/JSX headless, sem serviço permanente, login ou editor gráfico na VPS.

## Isolamento e utilização

- Projeto único: `/srv/projects/skill-universal/`.
- Node privado: `runtimes/node-22.23.4/bin/node`. O npm utilizado também pertence a esse Node, nunca ao Ubuntu global.
- Pacote CLI e todas as dependências: `.runtime/npm/openpencil/`.
- Instalação atómica em staging na mesma pasta e limpeza dos temporários; recusam-se symlinks externos, destino ocupado ou proprietário incompatível.
- `--check`: verifica presença/versão sem instalar. `--apply`: instalação privada com scripts npm desativados, seguida de prova funcional real antes da ativação.
- Os testes criam um HTML sintético numa pasta temporária Ferrari, importam-no para `.fig`, consultam o documento e exportam SVG e HTML standalone. Apenas `PASS` com ficheiros reais.
- Sem `apt install`, `npm -g`, Docker, serviço web, alteração do SSH ou instalação em outros projetos. Dependências fundamentais do Ubuntu permanecem parte do SO.
- O desenho de um site real (por exemplo Low Cost Europa) é tarefa separada: usar uma cópia autorizada da estrutura e não mexer no serviço sem teste e decisão própria.

## Execução administrativa autorizada pela ponte GitHub

Na VPS, através do transporte GitHub Actions/SSH já autorizado, com o utilizador dono do projeto:

```bash
bash install/vps-openpencil-cli.sh --check
bash install/vps-openpencil-cli.sh --apply
bash install/vps-openpencil-cli.sh --check
```

O script pode ser passado por stdin num workflow Ferrari exclusivo sem alterar `current` nem o validador da Skill. Um run GitHub Actions e logs de import/export são obrigatórios para declarar a instalação certificada.

**Estado 06/11/2026: CERTIFICADO — CLI básica privada na VPS.** A execução [VPS #42144086173](https://github.com/martaxi-boss/VPS/actions/runs/42144086173) aprovou a importação HTML→.fig, exportação de SVG e HTML standalone, verificação exata da versão 0.16.0, auditoria de symlinks e preservação da release `current`. O npm adicionou 142 dependências apenas dentro de `.runtime/npm/openpencil/`; não executou APT/npm globais na VPS.

O código e a deteção em GitHub entraram na main pela [PR #71](https://github.com/martaxi-boss/skill-universal/pull/71), commit `a831a7e605f4efb6cc4561e4d533a10280956e8d`, CI [#42144001926](https://github.com/martaxi-boss/skill-universal/actions/runs/42144001926) PASS. O workflow administrativo de uso único e o pedido foram retirados da main do repositório VPS após certificação. **Histórico:** nessa primeira instalação a release ativa não foi alterada. A integração posterior ficou concluída pela PR #72, sem nova ação tipada, sem editor gráfico permanente e sem mudanças na ponte SSH.


## Fecho do ponto 1 — integração completa (06/11/2026)

- **Código/Skill única:** [PR #72](https://github.com/martaxi-boss/skill-universal/pull/72), commit de release `a266b25e06a9c8acf1fdc940d22b99070cd17ded`; [CI #42145436173](https://github.com/martaxi-boss/skill-universal/actions/runs/42145436173) SUCCESS.
- **Ativação privada:** [VPS #42145587073](https://github.com/martaxi-boss/VPS/actions/runs/42145587073) SUCCESS; **293 testes PASS**, 40/40 ações privadas, OpenPencil real HTML→FIG→SVG/HTML, anterior F7 preservada como fallback. Sem APT global ou alteração de serviços terceiros.
- **Skill→GitHub→VPS→ZIP REAL:** [VPS #42145727316](https://github.com/martaxi-boss/VPS/actions/runs/42145727316) **SUCCESS**, `FERRARI_SKILL_JOB_STATUS=completed` e `FERRARI_SKILL_END_TO_END=PASS`, `response.zip` com quatro artefactos válidos `artifacts/design.fig`, `design.svg`, `design.html` e `design-info.json`. A ponte permaneceu fixada em `292aeb7d10eecef8c3ca84760cd579e84e4b97f3`.
- **Higiene:** workflow administrativo, pedido de ativação e pedido sintético removidos depois da prova, ficando a evidência nos commits e runs. O `current` aponta para a release acima e o fallback anterior permanece disponível.
- **Limite explícito:** o ZIP da Skill única foi gerado e validado, mas a sua instalação/substituição dentro da interface ChatGPT não é comprovada pela CI. OpenPencil CLI não equivale a editor GUI; projetos web existentes, incluindo Low Cost Europa, não foram alterados.
