# Bootstrap portátil — Motor Ferrari Ubuntu

**Referência canónica e atualizada:** [BOOTSTRAP.md](https://github.com/martaxi-boss/skill-universal/blob/main/BOOTSTRAP.md). Esta cópia serve apenas para ambientes com ZIP da única Skill Ferrari.

## Arquitetura estável

Uma Skill Universal Ferrari → conector GitHub autenticado → workflow exclusivo Ferrari em `martaxi-boss/VPS` → SSH existente → Motor Ferrari isolado na VPS Ubuntu → ZIP e relatório. A IA orienta; o motor e os executores fazem o trabalho. Não alterar ponte SSH, Supervisor ou outros projetos. REA e Ruflo são fornecedores opcionais, não o coordenador.

## Estado comprovado em 03/11/2026

- **Versão ativa:** `f7eb9dcbda78a80f127b8981d9361e853672cd62`.
- **VPS:** [#41558189146](https://github.com/martaxi-boss/VPS/actions/runs/41558189146) SUCCESS com **93 testes PASS** e geometria IFC real PASS.
- **Skill ponta a ponta:** [geometria IFC #41558414405](https://github.com/martaxi-boss/VPS/actions/runs/41558414405) SUCCESS; `report.json` e `ifc-report.json` inspecionados. Parede IFC4: 5 × 0,2 × 3 m, oito vértices e doze triângulos. Provas anteriores: [IFC semântico #41556384002](https://github.com/martaxi-boss/VPS/actions/runs/41556384002), [Vite #41556406846](https://github.com/martaxi-boss/VPS/actions/runs/41556406846) e [inventário #41556541593](https://github.com/martaxi-boss/VPS/actions/runs/41556541593).
- **Inventário real:** 56 candidatos Ubuntu, **22/56 detetados**, 48 ferramentas detetadas no catálogo combinado, **12 operações base**, 21 ações tipadas externas. Ação disponível não implica certificação de todas as funções do programa.
- **IfcOpenShell:** `0.9.0.post1` em venv isolado; `ifc-summary` mantém o mesmo contrato e acrescenta limites globais de malhas trianguladas para elementos com representação, além de identificar ausência de geometria e erros. Não faz validação estrutural, IDS, quantidades líquidas, colisões ou BIM completo.
- **Vite:** `8.3.5` com Node `22.23.4` isolado; `vite-build` aceita ZIP estático permitido e devolve HTML/CSS/JS compilados. Sem backend, sem scripts npm do projeto, sem browser Playwright.
- **Não detetados:** FreeCAD e Playwright; não fingir que estão instalados. REA/Ruflo profundos ainda pendentes.
- **Higienização:** a rotina Ferrari existente removeu duas releases obsoletas, preservou a ativa e a versão anterior certificada `29e016885...`, libertou 1,70 GiB e reportou 21,61 GiB livres. Nenhuma nova Skill, SSH, Supervisor, instalação global ou outro projeto foi alterado.

## Continuidade

Ler `references/github-bridge.md` para os tipos de pedido remotos `kind=inventory|operation|auto|invoke`. Confirmar cada artefacto real e os estados dos logs. Se for necessário ampliar capacidades, implementar e testar dentro de `martaxi-boss/skill-universal`, mantendo uma só Skill.

Os repositórios de transporte são públicos. Base64 não é encriptação: não publicar credenciais nem dados privados. Uma futura confirmação de propriedade não torna os commits privados.
