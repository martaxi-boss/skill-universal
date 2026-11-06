# Ferrari — Fase 10: certificação técnica e pendências finais (06/11/2026)

**Estado: certificação técnica parcial PASS; Fase 10 não encerrada nem classificação 10/10.**

## Provas técnicas

- [CI #42135954104](https://github.com/martaxi-boss/skill-universal/actions/runs/42135954104) **SUCCESS: 285 testes PASS**, incluindo três novos ensaios de isolamento de desinstalação em cópias temporárias independentes: (i) eliminar apenas uma cópia do Ferrari preserva ficheiros de sete outros projetos, (ii) um link do Ferrari para dependência de outro projeto bloqueia a remoção e (iii) uma raiz Ferrari que seja symlink é recusada. O ensaio usa TemporaryDirectory de GitHub runner, não apaga o Ferrari ativo.
- CI empacotou a **única Skill** `motor-universal-linux` em `skill.zip` (artefacto `ferrari-skill-installable`), com `SKILL.md`, 5 referências e `agents/openai.yaml`. Arquivo verificado e SHA-256 do skill.zip: `428cae558fc6d14bf61791c6dd85a75bb2c94a7177b3d3d4a0729158954716e6` (19 592 bytes). Atualização no GitHub ou ZIP **não prova** que a Skill instalada no ChatGPT tenha sido atualizada.
- [Pedido de operação real #42135993341](https://github.com/martaxi-boss/VPS/actions/runs/42135993341) **SUCCESS**, `kind=operation`, `svg-poster`, `FERRARI_SKILL_END_TO_END=PASS`, `report.json.status=completed` e ficheiro real `artifacts/creative/poster.svg` (1680 bytes).
- [Pedido de ação tipada real #42136014343](https://github.com/martaxi-boss/VPS/actions/runs/42136014343) **SUCCESS**, `kind=invoke`, `file-mime` com JSON público, `FERRARI_SKILL_END_TO_END=PASS`, `report.json.status=completed` e `artifacts/mime.txt` (`application/json`).
- [Inventário F9 pós-limpeza #42134719562](https://github.com/martaxi-boss/VPS/actions/runs/42134719562) **SUCCESS**, release ativa `758e1b435317fa26277b332b75bc47c67910be81`, 40 ações invocáveis, 47/56 candidatos privados detetados, fallback F6 preservado. [Auditoria VPS #42134629602](https://github.com/martaxi-boss/VPS/actions/runs/42134629602) PASS, serviços protegidos ativos.
- [F8 Android físico #42128892714](https://github.com/martaxi-boss/VPS/actions/runs/42128892714) **PASS**, 40/40 ações tipadas com prova individual real; APK pública instalada e removida sem alterar PINK IPTV.

## Limites factuais

1. O ensaio de desinstalação é **não destrutivo e em cópia isolada**. Não demonstra desinstalação do Ferrari na VPS real, que permanece operativo. A auditoria read-only F7 [#42098800995](https://github.com/martaxi-boss/VPS/actions/runs/42098800995) registou zero hooks Ferrari nos registos amostrados; não é prova universal de ausência de consumidores indiretos.
2. Fase 9 transversal ainda aberta: **16 pacotes APT globais**, sem titularidade exclusiva demonstrada para remover; **9/56 candidatos privados não detetados**; diferenças de commits e alterações locais rastreadas em PINK IPTV e IPTV VPN Bot. Não houve `apt purge` de aplicações, `git reset` ou deploy forçado em projetos de terceiros.
3. Instalação efetiva da **versão atualizada da única Skill na interface do ChatGPT não verificada**. Não criar Skill paralela para forçar um PASS.
4. Ruflo com CLI opcional, agentes e fornecedores de modelo não certificados; quotas duras CPU/RAM, GPU, GUI integral, Penpot e funcionalidades licenciadas permanecem fora do âmbito certificado.

## Decisão de fecho

**PASS técnico para CI e dois percursos reais Skill→VPS→ZIP.** Não declarar *Fase 9 e Fase 10 100% completas* nem atribuir 10/10 até os bloqueios acima serem resolvidos com autorização/evidência. O Ferrari ativo e os outros serviços permanecem preservados. Fonte canónica: [BOOTSTRAP](../BOOTSTRAP.md).
