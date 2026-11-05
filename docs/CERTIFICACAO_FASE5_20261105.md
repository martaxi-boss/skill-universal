# Certificação operacional Ferrari — Fase 5

**Data:** 05/11/2026 UTC. **Estado: FASE 5 CERTIFICADA no âmbito da ativação isolada e rollback ensaiado em cópia.**

## Identidade operacional

- Repositório GitHub: `martaxi-boss/skill-universal`.
- Diretório único de aplicação na VPS: `/srv/projects/skill-universal/`.
- Release de produção confirmada com read-back SSH: `40c0e1cdf31b1fe9589ad8be90e5eac06eec2856`.
- Fallback preservado e existência comprovada em VPS: `87969badbde0a77c2c181bb9605357d51a4a30c0`.
- Script de ativação/rollback testado no host: `install/vps-isolated-release.sh`, Git blob `e64669da13afd55dce3f0d6c368aa17ebec2561c` (hash do conteúdo real verificado antes de extrair as funções de recuperação).
- O HEAD da PR poderá avançar com novos testes/documentos, **sem mudar automaticamente o SHA ativo na VPS**.

## Matriz de provas obrigatórias

| Porta | Evidência real | Resultado |
|---|---|---|
| CI corrigido no candidato de produção | Ferrari Actions [#42065905669](https://github.com/martaxi-boss/skill-universal/actions/runs/42065905669), [#42065915973](https://github.com/martaxi-boss/skill-universal/actions/runs/42065915973) | SUCCESS |
| CI com novo teste isolado de rollback e hash exato | Ferrari Actions [#42068518899](https://github.com/martaxi-boss/skill-universal/actions/runs/42068518899), [#42068530678](https://github.com/martaxi-boss/skill-universal/actions/runs/42068530678) | SUCCESS |
| Pré-check real na VPS | VPS Actions [#42066226440](https://github.com/martaxi-boss/VPS/actions/runs/42066226440) | PASS; 232 regressões; 40/40 ações privadas; OpenSCAD→STL, Blender→BLEND/GLB/PNG, LibreOffice→PDF, Skill→response.zip; `current` não alterado |
| Ativação protegida + leitura de `current` | VPS Actions [#42066363098](https://github.com/martaxi-boss/VPS/actions/runs/42066363098) | `FERRARI_PRIVATE_ACTIVE_RELEASE=PASS`, `FERRARI_PHASE5_ACTIVATION=PASS`; SHA exato ativo, fallback preservado |
| Pedido real da Skill via GitHub→VPS→ZIP | VPS Actions [#42066521890](https://github.com/martaxi-boss/VPS/actions/runs/42066521890) | `FERRARI_SKILL_JOB_STATUS=completed`, `FERRARI_SKILL_END_TO_END=PASS`; artefacto `ferrari-skill-result-42066521890` (ID 13435055490) com `report.json` e `inventory.json` |
| Recuperação perante falha, em cópia física isolada na VPS | VPS Actions [#42068780199](https://github.com/martaxi-boss/VPS/actions/runs/42068780199) | 3/3 testes PASS; `FERRARI_PHASE5_ROLLBACK_INJECTED_FAILURE=PASS`, `FERRARI_PHASE5_PRODUCTION_UNCHANGED=PASS`, `FERRARI_PHASE5_FALLBACK_INTACT=PASS`, `FERRARI_PHASE5_ROLLBACK_CERTIFIED=PASS` |
| Verificação de higiene/saúde | VPS Actions [#42066853562](https://github.com/martaxi-boss/VPS/actions/runs/42066853562) | `AUDIT_ONLY`, `health_after=true`, `protected_services_unchanged=true`, `eligible_files=0`, nenhuma remoção |

## Método do ensaio de rollback

O teste `tests/test_phase5_isolated_rollback.py` lê diretamente o script **da release em execução** na VPS e valida o hash Git do seu conteúdo. Extrai sem alterações a função `cleanup()` (incluindo o `trap cleanup EXIT`) e o bloco de troca atómica `current`. Simula, sob `/srv/projects/skill-universal/.runtime/`, três cenários sobre uma **árvore fictícia** com releases anteriores e candidatas:

1. Falha antes da troca: symlink anterior continua inalterado.
2. Falha deliberada **após a troca**: o mesmo código de rollback do Ferrari restitui a release anterior, com retorno de erro preservado.
3. Ativação sem falha: o candidato permanece ativo **apenas na árvore fictícia**.

O teste verifica também remoção de temporários próprios, inexistência de links de transição residuais e preservação de ficheiros sentinela. O workflow compara `current` de produção antes e depois e exige o SHA original. **Não foi provocada falha na produção**, nem ativado novamente o Ferrari real para ensaiar a reversão.

## Limites e próxima etapa

- **Fase 5 encerrada:** ativação, 40/40 caminhos privados dos adaptadores, saídas reais CAD/Office, pós-teste de transporte/ZIP, fallback, ensaio isolado de rollback, higiene e pós-saúde.
- **Fase 6 ainda não iniciada:** inventariar dependências indiretas, instalações globais e consumidores; a contagem de candidatos detetados em inventários antigos incluiu programas globais. 40/40 ações invocáveis não prova que todas as funcionalidades de cada ferramenta passaram em ensaios reais.
- **Fases seguintes não certificadas:** automação Ruflo, funcionalidades opcionais, remoção completa de resíduos globais, independência de todos os outros projetos, unificação/atualização da Skill instalada e ensaio completo de desinstalação.
- A PR [#64](https://github.com/martaxi-boss/skill-universal/pull/64) pode continuar aberta sem merge até a integração/fecho planeado; a release ativa não necessita de novo deploy para registar esta certificação.
- Nenhum programa de aplicação foi instalado globalmente na VPS durante a fase. Não remover pacotes nem tocar em serviços de outros projetos sem auditoria de consumidores.

**Decisão:** **FASE 5 = CERTIFICADA (PASS)**. A continuação para a Fase 6 exige ordem própria; esta certificação não a executa.
