# Ferrari — Certificação CAD/BIM IFC + Vite (03/11/2026)

## Estado definitivo desta fase

- **Motor instalado na VPS Ubuntu 24.04:** `29e016885f01c78941c37e4a147e207a1fc62f05`.
- **PR de implementação:** [#2](https://github.com/martaxi-boss/skill-universal/pull/2), integrada no `main`.
- **CI Ubuntu:** [#41555850276](https://github.com/martaxi-boss/skill-universal/actions/runs/41555850276), SUCCESS, **87 testes unitários PASS**.
- **Entrega e execução real na VPS:** [#41556114851](https://github.com/martaxi-boss/VPS/actions/runs/41556114851), SUCCESS, **87 testes PASS**, `FERRARI_IFC_SEMANTIC_REAL=PASS`, `FERRARI_VITE_BUILD_REAL=PASS`, `FERRARI_PROFESSIONAL_INVENTORY=PASS`.
- **Skill → GitHub → VPS → ZIP, IFC:** [#41556384002](https://github.com/martaxi-boss/VPS/actions/runs/41556384002), SUCCESS, `FERRARI_SKILL_END_TO_END=PASS`; extraídos `report.json` e `artifacts/ifc-report.json`, com `status=completed`, esquema IFC4 e duas entidades: `IfcProject` e `IfcWall`.
- **Skill → GitHub → VPS → ZIP, Vite:** [#41556406846](https://github.com/martaxi-boss/VPS/actions/runs/41556406846), SUCCESS, `FERRARI_SKILL_END_TO_END=PASS`; extraídos `report.json`, `artifacts/vite-build.json`, `artifacts/dist/index.html`, um CSS e um JS compilados.
- **Skill, inventário atualizado:** [#41556541593](https://github.com/martaxi-boss/VPS/actions/runs/41556541593), SUCCESS, ZIP com `inventory.json` e `status=completed`.

## Instalações e isolamento

| Programa | Versão comprovada | Localização | Operação |
|---|---|---|---|
| IfcOpenShell | `0.9.0.post1` | `~/.local/share/motor-ferrari/.runtime/venvs/bim` | `ifc-summary` |
| Vite | `8.3.5` | `~/.local/share/motor-ferrari/.runtime/npm/vite` | `vite-build` |
| Node.js isolado | `22.23.4` | `~/.local/share/motor-ferrari/runtimes/node-22.23.4` | executor do Vite |

IfcOpenShell instalado em `venv` próprio sem modificar Python global. Vite instalado via npm isolado com scripts de instalação desativados e sem executar scripts/configurações recebidas do projeto. Nenhuma ponte SSH ou Supervisor de outros projetos foi alterada; apenas os SHA das duas referências Ferrari no repositório VPS foram avançados à nova versão.

## Números exatos do inventário (na VPS, após as duas instalações)

| Medida | Antes | Depois |
|---|---:|---:|
| Seleção Ubuntu | 56 | 56 |
| Candidatos selecionados detetados | 21 | **22** |
| Candidatos não detetados | 35 | **34** |
| Ferramentas detetadas no catálogo combinado | 46 | **48** |
| Ações tipadas do catálogo externo | 21 | 21 |
| Operações base Ferrari | 10 | **12** |

O IfcOpenShell entra no **catálogo auxiliar**, não aumenta a shortlist de 56; o Vite é o **novo selecionado** encontrado. Portanto 22/56 e 48 combinados são números diferentes e corretos.

## Limites de cobertura (não inventar certificação)

**`ifc-summary`:** lê o esquema e entidades de um IFC, devolve contagens, projeto, hash e versão do parser. Não valida geometria, quantidades da obra, cálculo estrutural, compatibilidade integral, normas, IDS, colisões ou assinatura profissional.

**`vite-build`:** compila projetos web estáticos de entrada ZIP até 2 MB, com estrutura permitida `index.html`, `src/` e `public/`. Extrai até 120 ficheiros e 6 MB descomprimidos. Não executa npm scripts do projeto, plugins externos, `vite.config.js` do utilizador, código de backend, testes browser Playwright ou compilação arbitrária de repos existentes.

**Não instalados/sem nova certificação:** FreeCAD, Playwright, infra de contentores, validações estruturais e BIM/IFC profissional avançado. Vite e IfcOpenShell funcionais não significam que todas as outras ferramentas catalogadas já estejam prontas.

## Continuar sem perder o contexto

A fonte de verdade é `BOOTSTRAP.md` e esta prova. Próximos incrementos separados e mediante necessidade real: IFC com geometria, IDs/quantidades e testes profissionais; aplicações web com testes de browser e builds de frameworks, sem instalar indiscriminadamente FreeCAD/GUI/daemons. Utilizar a **mesma Skill Ferrari**, sem criar outra.
