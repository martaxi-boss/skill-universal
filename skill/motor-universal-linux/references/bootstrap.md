# Bootstrap portátil — Motor Ferrari Ubuntu

**Referência canónica:** [BOOTSTRAP.md](https://github.com/martaxi-boss/skill-universal/blob/main/BOOTSTRAP.md). Esta cópia é para os ambientes que apenas têm o ZIP da Skill.

## Arquitetura

Uma Skill Universal Ferrari → conector GitHub autenticado → workflow exclusivo Ferrari em `martaxi-boss/VPS` → SSH existente → Motor Ferrari isolado na VPS Ubuntu → resultado ZIP e relatório no GitHub Actions. O ChatGPT interpreta e orienta; a escolha e execução de ferramentas pertence ao motor Ubuntu. Não alterar a ponte SSH existente, o Supervisor ou os outros projetos. REA e Ruflo são apenas componentes opcionais.

## Provas reais de 02/11/2026

- Ferrari na VPS: [deploy #41546722719](https://github.com/martaxi-boss/VPS/actions/runs/41546722719), SUCCESS, 68 testes PASS, release ativa `1ff6e472b5ea4eab95785be224155f400c51aeaa`.
- Ponta a ponta: [SVG #41546901101](https://github.com/martaxi-boss/VPS/actions/runs/41546901101) e [Markdown→DOCX #41547060999](https://github.com/martaxi-boss/VPS/actions/runs/41547060999), SUCCESS, ZIP e ficheiros reais.
- Catálogo: 125 projetos investigados, 56 pré-selecionados Ubuntu, 45 programas detetados nos catálogos combinados (não 45 de 56), 10 operações base e 12 adaptadores tipados.
- REA/Ruflo: instalação CLI verificada; execução profunda pendente. BIM/FreeCAD ainda não certificado. Workflow remoto atende tipos de pedido existentes; não um DAG arbitrário.

## Continuidade

Ler `references/github-bridge.md` quando houver pedido para a VPS. Confirmar a ferramenta real e respetiva ação. Criar um ficheiro novo GitHub por pedido, acompanhar o SHA, identificar o run, confirmar `report.json` e ficheiros, devolvê-los ao utilizador. Para capacidades ainda não integradas, implementar adaptadores em `martaxi-boss/skill-universal`, testar no Ubuntu e registar no bootstrap. Não criar uma nova Skill para cada área.

**Repositório de transporte público:** certificar a propriedade não oculta o conteúdo publicado. Não colocar segredos, dados pessoais ou documentos confidenciais num commit público.
