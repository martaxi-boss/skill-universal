# Certificação da Fase 6 — Ferrari (05/11/2026)

**Veredito formal: PASS OPERACIONAL / NO-GO PARA FECHO INTEGRAL DA FASE 6.**

Esta certificação distingue resultados executados e comprovados de requisitos ainda sem evidência. A Fase 7 **não foi iniciada nem autorizada**. Uma execução GitHub Actions com código concluído não equivale, por si só, a prova de todos os recursos internos da VPS.

## Ambiente verificado

- Projeto: `martaxi-boss/skill-universal`, instalado exclusivamente como projeto em `/srv/projects/skill-universal`.
- Release operacional confirmada de novo pela VPS: `146145d5ada9c13e368df18727e4dbf4f5807664`.
- Release anterior preservada para fallback: `40c0e1cdf31b1fe9589ad8be90e5eac06eec2856`.
- GitHub PR [#64](https://github.com/martaxi-boss/skill-universal/pull/64) continua **draft**, sem merge. O código publicado na PR depois do deploy inclui testes e auditoria, não uma segunda ativação em produção.

## Matriz de certificação

| Requisito | Evidência real | Resultado |
|---|---|---|
| Regressão e regras de isolamento no GitHub | Ferrari [#42083633239](https://github.com/martaxi-boss/skill-universal/actions/runs/42083633239) e [#42083646367](https://github.com/martaxi-boss/skill-universal/actions/runs/42083646367), última execução CI **245 testes PASS** | **PASS CI** |
| Ações privadas e inventário fresco da Skill | [VPS #42083666378](https://github.com/martaxi-boss/VPS/actions/runs/42083666378), `FERRARI_SKILL_JOB_STATUS=completed`, `FERRARI_SKILL_RESPONSE_ZIP=PASS`, `FERRARI_SKILL_END_TO_END=PASS`; ZIP analisado com `report.json.status=completed` e `artifacts/inventory.json` | **PASS: 40/40 ações invocáveis, 47/56 programas selecionados detetados** |
| Correção real da descoberta CAD/Office | No inventário real #42083666378: Blender em `tools/blender/blender`; OpenSCAD em `tools/openscad/bin/openscad`; LibreOffice em `tools/libreoffice/program/soffice` | **PASS para estes 3 executores** |
| Teste funcional protegido da release em produção | [VPS #42078448805](https://github.com/martaxi-boss/VPS/actions/runs/42078448805) (precheck: 241 testes/40 ações/CAD/Office/ZIP), [#42078597765](https://github.com/martaxi-boss/VPS/actions/runs/42078597765) (ativação e fallback); [#42079545679](https://github.com/martaxi-boss/VPS/actions/runs/42079545679) (read-back) | **PASS** |
| Dependências ELF ligadas | [VPS #42079545679](https://github.com/martaxi-boss/VPS/actions/runs/42079545679): 33 binários ELF amostrados, 1 447 resoluções de bibliotecas dentro Ferrari, 13 do Ubuntu base, zero bibliotecas externas ou em falta **nessa amostra** | **PASS amostral; não prova plugins e shebangs indiretos** |
| Inventário físico vivo da VPS e serviços | [VPS #42044862915, tentativa 2](https://github.com/martaxi-boss/VPS/actions/runs/42044862915) de 05/11 às 18:25 UTC; artefacto read-only `vps-project-inventory-42044862915` | **PASS da recolha**, release correta e serviços principais em execução; inventário `/opt` marcado `INCOMPLETE` |
| Auditoria de saúde/higiene posterior | [VPS #42084337560](https://github.com/martaxi-boss/VPS/actions/runs/42084337560), [issue #343](https://github.com/martaxi-boss/VPS/issues/343): `AUDIT_ONLY`, `health_after=true`, `protected_services_unchanged=true`, 7 raízes de caches verificadas, 0 elegíveis e 0 removidas, diferença de espaço de 0 bytes | **PASS sem alteração dos serviços** |
| Atribuição de instalações globais e remoção dos exclusivos | Inventário vivo #42044862915 ainda mostra as 16 aplicações globais; nenhuma prova suficiente de instalação exclusiva ou ausência de consumidores em todos os serviços | **PENDENTE — NÃO ELIMINAR** |
| Auditoria integral dos links/interpretadores e órfãos Ferrari | Novas verificações read-only em `install/vps-phase6-certify.py`; quatro regressões locais novas passaram no CI #42083633239. **O novo auditor ainda não foi executado na VPS**: não confundir validação do código com execução remota | **PENDENTE de prova física** |

## Dezasseis aplicações globais ainda existentes

As versões APT do Ubuntu foram confirmadas na fotografia atual, não são automaticamente uma instalação do Ferrari e não devem ser confundidas com as cópias executáveis privadas do motor:

`ansible`, `audacity`, `blender`, `calibre`, `darktable`, `gimp`, `kdenlive`, `librecad`, `libreoffice`, `obs-studio`, `openscad`, `openshot-qt`, `qgis`, `solvespace`, `synfigstudio` e `yt-dlp`.

Não foram identificados todos os seus consumidores ou a responsabilidade original pela instalação. Ausência de um processo numa fotografia pontual não comprova ausência de uso por tarefas agendadas, projetos independentes, serviços que arrancam sob pedido ou outras ferramentas. Por isso **zero pacotes APT removidos**. Os nove candidatos da shortlist ainda sem presença privada não são apresentados como operacionais no Ferrari.

## Segurança dos restantes projetos

O inventário vivo manteve em execução serviços nomeados `fadego-staging`, `lowcost-europa`, `pink-iptv-backend`, `pink-vpn`, `pm2-iptvpn-bot`, `pm2-telegram-robot-leads`, `nginx` e `postgresql@16-main`, além de serviços Ubuntu. A auditoria de saúde posterior confirmou que **os serviços protegidos permaneceram inalterados**. Esta confirmação não é uma prova funcional individual de todas as funcionalidades de cada aplicação.

O inventário de `/opt` ficou **INCOMPLETE**. Não afirmar que todas as referências externas, binários soltos, symlinks, scripts e dados órfãos foram encontrados. O script de auditoria profunda foi criado dentro do projeto Ferrari e testado em CI, mas **não foi executado nem instalado na VPS**.

## Critério de passagem e decisão

Para certificar formalmente o **fecho integral** da Fase 6, falta produzir prova VPS de: (1) varrimento das symlinks/interpretadores `PATH`, bibliotecas e plugins para os executores realmente usados, com resultados e limites; (2) inventário completo dos caminhos potencialmente Ferrari fora da pasta, incluindo `/opt`; (3) atribuição dos 16 pacotes globais por proprietário e consumidor e eliminação *somente* dos exclusivamente residuais cuja remoção seja comprovadamente segura; (4) pós-teste real 40/40 + Skill→ZIP, fallback e saúde dos serviços após quaisquer alterações.

**Decisão responsável em 05/11/2026: Fase 6 ainda não certificada como concluída.** O núcleo de isolamento e execução é certificado, mas o fecho completo é **NO-GO**, sem avanço para a Fase 7. Não aceitar 100%, 10/10, nem desinstalações globais por inferência. Nenhum outro projeto foi alterado por esta certificação.
