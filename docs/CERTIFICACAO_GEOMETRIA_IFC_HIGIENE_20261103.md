# Ferrari — Certificação de geometria IFC e higiene, 03/11/2026

## Resultado da fase — PASS

Esta fase **não criou uma nova Skill, operação nem camada de execução**. A operação existente `ifc-summary` foi ampliada no mesmo motor e usa IfcOpenShell `0.9.0.post1`, já instalado em venv próprio.

- **PR #3:** https://github.com/martaxi-boss/skill-universal/pull/3 — geometria medida, seis testes novos e rotação do fallback de limpeza.
- **PR #4:** https://github.com/martaxi-boss/skill-universal/pull/4 — um teste de inventário antigo assumia Vite ausente no host; a simulação foi isolada, sem alterar executores.
- **Release atualmente ativa:** `f7eb9dcbda78a80f127b8981d9361e853672cd62`.
- **CI corrigida:** https://github.com/martaxi-boss/skill-universal/actions/runs/41557940783 — SUCCESS.
- **VPS real:** https://github.com/martaxi-boss/VPS/actions/runs/41558189146 — SUCCESS, **93 testes PASS na VPS**, `FERRARI_IFC_GEOMETRY_REAL=PASS`, `FERRARI_IFC_SEMANTIC_REAL=PASS`, `FERRARI_VITE_BUILD_REAL=PASS`.
- **Skill ponta a ponta:** https://github.com/martaxi-boss/VPS/actions/runs/41558414405 — SUCCESS com `FERRARI_SKILL_JOB_STATUS=completed` e `FERRARI_SKILL_END_TO_END=PASS`, artefacto `artifacts/ifc-report.json` inspecionado.
- **Tentativa inicial:** https://github.com/martaxi-boss/VPS/actions/runs/41557825287 — FAILURE apenas por teste dependente do Vite instalado. Não esconder este histórico.

## Exemplo real verificado pela Skill

O pedido continha um IFC4 público e sintético, com uma parede extrudida. O motor devolveu:

| Métrica | Valor |
|---|---:|
| IfcWall | 1 |
| Geometrias medidas | 1 |
| Elementos sem representação | 0 |
| Erros geométricos | 0 |
| Vértices | 8 |
| Triângulos | 12 |
| Dimensão X | 5,00 m |
| Dimensão Y | 0,20 m |
| Dimensão Z | 3,00 m |
| Limite mínimo mundial | (-2.5, -0.1, 0.0) m |
| Limite máximo mundial | (2.5, 0.1, 3.0) m |

**Escopo exato:** caixas delimitadoras de malha triangulada em coordenadas globais (metres). Distingue `mesh_measured`, `no_representation` e `geometry_error`; em relatórios extensos, declara `truncated` e `sample_limit`. Não calcula volume líquido, resistência estrutural, interseções, IDS, conformidade com regulamentos ou aprovação de projetos. Medição 3D não é certificação BIM completa.

## Higienização efetuada na VPS

A rotina existente `install/ferrari-hygiene.py` foi executada primeiro em preview e depois em `--apply`, **após** os testes funcionais. Não foi criada outra rotina ou ponte.

- **Releases removidas:** `405ae6fdcbabb9be8d81824a713296ae80b2aa04` (tentativa anterior falhada) e `b8a7de8695b16bf064e0796c3cb9276d3a8254ed` (fallback obsoleto).
- **Releases preservadas:** `f7eb9dcbda78a80f127b8981d9361e853672cd62` (ativa) e `29e016885f01c78941c37e4a147e207a1fc62f05` (última anterior certificada, recuperação).
- **Espaço livre adicional real reportado:** `1829462016` bytes, aproximadamente **1,70 GiB**.
- **Espaço livre final da VPS:** **21,61 GiB**.
- `outside_ferrari_touched=false`, `FERRARI_ONLY_HYGIENE=PASS`.
- Ámbito único: `/home/ubuntu/.local/share/motor-ferrari/releases`. Não houve exclusão/alteração de outros projetos, SSH ou Supervisor.

## Próxima fase separada (não declarada executada)

Testes de navegação real de websites compilados com Vite. Avaliar primeiro o navegador/runtime headless compatível com a VPS antes de instalar Playwright ou Chromium e sem converter o Ferrari num coordenador separado. **Não** misturar esta etapa com a certificação IFC atual.

Ver também o [BOOTSTRAP canónico](../BOOTSTRAP.md). Os números de descoberta mantêm-se em **22/56 candidatos Ubuntu detetados**, **48 ferramentas combinadas**, **12 operações base** e **21 ações externas**, sem novas instalações por causa desta fase.
