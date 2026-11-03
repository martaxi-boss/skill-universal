# Bootstrap portátil — Motor Ferrari Ubuntu

**Referência canónica e atualizada:** [BOOTSTRAP.md](https://github.com/martaxi-boss/skill-universal/blob/main/BOOTSTRAP.md). Esta cópia serve apenas para ambientes com ZIP da única Skill Ferrari.

## Arquitetura estável

Uma Skill Ferrari → conector GitHub autenticado → workflow exclusivo Ferrari em `martaxi-boss/VPS` → SSH existente → Motor Ferrari isolado na VPS Ubuntu → ZIP e relatório. A IA orienta; o motor e os executores fazem o trabalho. Não alterar ponte SSH, Supervisor ou outros projetos. REA e Ruflo são fornecedores opcionais, não o coordenador.

## Estado comprovado em 03/11/2026

- **Versão ativa:** `29e016885f01c78941c37e4a147e207a1fc62f05`.
- **VPS:** [#41556114851](https://github.com/martaxi-boss/VPS/actions/runs/41556114851) SUCCESS com **87 testes PASS** e dois testes funcionais novos PASS.
- **Skill ponta a ponta:** [IFC #41556384002](https://github.com/martaxi-boss/VPS/actions/runs/41556384002), [Vite #41556406846](https://github.com/martaxi-boss/VPS/actions/runs/41556406846) e [inventário #41556541593](https://github.com/martaxi-boss/VPS/actions/runs/41556541593), SUCCESS. Os ZIPs, `report.json` e artefactos foram inspecionados.
- **Inventário real:** 56 candidatos Ubuntu, **22/56 detetados**, 48 ferramentas detetadas no catálogo combinado, **12 operações base**, 21 ações tipadas externas. Ação disponível não implica certificação de todas as funções do programa.
- **IfcOpenShell:** `0.9.0.post1` em venv isolado; `ifc-summary` aceita `.ifc` e devolve esquema, entidades, projeto e hash. Não faz validação estrutural, geométrica, IDS ou BIM completo.
- **Vite:** `8.3.5` com Node `22.23.4` isolado; `vite-build` aceita ZIP estático permitido e devolve HTML/CSS/JS compilados. Sem backend, sem scripts npm do projeto, sem browser Playwright.
- **Não detetados:** FreeCAD e Playwright; não fingir que estão instalados. REA/Ruflo profundos ainda pendentes.
- **Isolamento:** nenhuma nova Skill, SSH, Supervisor, instalação global ou outro projeto alterado. As versões dos workflows próprios Ferrari apontam para a release ativa.

## Continuidade

Ler `references/github-bridge.md` para os tipos de pedido remotos `kind=inventory|operation|auto|invoke`. Confirmar cada artefacto real e os estados dos logs. Se for necessário ampliar capacidades, implementar e testar dentro de `martaxi-boss/skill-universal`, mantendo uma só Skill.

Os repositórios de transporte são públicos. Base64 não é encriptação: não publicar credenciais nem dados privados. Uma futura confirmação de propriedade não torna os commits privados.
