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

**Estado:** o código em GitHub não demonstra instalação na VPS. Só atualizar esta linha para CERTIFICADO após prova de execução real.
