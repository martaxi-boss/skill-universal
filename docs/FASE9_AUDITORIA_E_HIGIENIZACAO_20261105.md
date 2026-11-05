# Ferrari — Fase 9: auditoria e limpeza parcial (05/11/2026)

**Estado: Fase 9 em curso.** A Fase 8 continua certificada (40/40 ações tipadas); a Fase 9 avalia a organização geral da VPS.

## Evidências reais

- Inventário Ferrari: [#42129972810](https://github.com/martaxi-boss/VPS/actions/runs/42129972810) — 40 ações invocáveis; 47 de 56 candidatos privados detetados.
- Inventário da VPS: [#42130174995](https://github.com/martaxi-boss/VPS/actions/runs/42130174995), [mapeamento #42130589954](https://github.com/martaxi-boss/VPS/actions/runs/42130589954) e [verificação Git/processos #42130942947](https://github.com/martaxi-boss/VPS/actions/runs/42130942947).
- Limpeza de cache autorizada: [#42130786572](https://github.com/martaxi-boss/VPS/actions/runs/42130786572) — 543 ficheiros de cache, **2 613 248 bytes libertados**, zero dados das aplicações eliminados, serviços protegidos inalterados.
- Um processo PM2 abandonado numa release antiga do Ferrari, comprovadamente sem processos-filhos, foi terminado com guardas: [#42131306097](https://github.com/martaxi-boss/VPS/actions/runs/42131306097). O workflow temporário foi retirado depois.
- Pós-verificação independente: [#42131425267](https://github.com/martaxi-boss/VPS/actions/runs/42131425267) — PASS; serviços protegidos ativos, dois PM2 dos robôs preservados, processo abandonado ausente.

- Pós-limpeza da Skill: [#42131769522](https://github.com/martaxi-boss/VPS/actions/runs/42131769522) — execução `kind=inventory`, `report.json.status=completed`, artefacto ZIP validado; **40/40 ações invocáveis e 47/56 candidatos privados detetados**, sem regressão após a higiene.

## Organização

Oito pastas em /srv/projects com nomes correspondentes a repositórios: skill-universal, pink-iptv, fadego, lowcost-europa, telegram-robot-leads, iptvpn-bot, Codex e VPS. Quatro remotos Git foram identificados diretamente; nas outras instalações é necessária confirmação pela cadeia de entrega, pois nem todas são worktrees Git.

A release ativa Ferrari manteve-se no SHA 758e1b435317fa26277b332b75bc47c67910be81, com fallback preservado. O disco tinha aproximadamente 42 GB livres.

## Pendências para fechar Fase 9

1. **16 programas APT globais** encontrados, todos marcados como instalados manualmente. Nenhum removido sem prova de consumidores e impacto nos outros projetos.
2. Reconciliar as versões de GitHub com os deployments da VPS sem promover alterações não testadas.
3. Classificar pequenos resíduos legados fora das pastas, agendamentos e integrações OS, com testes de saúde posteriores.

**Não declarar Fase 9 completa até fechar estes pontos.** Nenhum novo coordenador ou Skill permanente foi criado.
