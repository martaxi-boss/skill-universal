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

## Auditoria APT por consumidores — 05/11/2026

Execução read-only [VPS #42132313840](https://github.com/martaxi-boss/VPS/actions/runs/42132313840), artefacto `vps-project-inventory.txt` recuperado e inspecionado:

- **16/16 pacotes globais presentes.** O `apt-get -s purge` isolado de cada um devolveu `exit=0` e identificou somente o pacote solicitado como alvo direto da simulação. **Não foi aplicado nenhum `apt purge` real.**
- **Zero processos a executar diretamente os binários globais identificados** no instante da leitura. A ausência de processo não prova ausência de consumidores futuros, dependências indiretas ou tarefas agendadas.
- **3 163 ficheiros de código/configuração de projetos inspecionados** sem referências diretas detetadas aos nomes dos 16 pacotes. A pesquisa foi limitada a certas extensões e 1 200 ficheiros por projeto; `fadego` atingiu esse limite e vários diretórios de dependências/release foram excluídos. Isto não justifica apagar instalações globalmente por si só.
- **8 famílias com alternativa privada já demonstrada no Ferrari:** LibreOffice, Ansible, GIMP, Blender, Kdenlive/MLT, Darktable, OpenSCAD, Calibre (o grau de cobertura funcional de cada alternativa é apenas o dos casos testados).
- **8 famílias sem cópia privada certificada:** yt-dlp, LibreCAD, QGIS, Audacity, OBS Studio, SolveSpace, Synfig Studio e OpenShot. Preservar por agora até integração privada testada.
- **Cautela:** `libreoffice`, `ansible` e outros nomes APT podem ser metapacotes ou depender de pacotes auxiliares; remover só o pacote nominal não equivale a eliminar todos os componentes globais nem a garantir reversibilidade. Fazer plano por pacote completo, com utilizadores e rollback antes de qualquer remoção.

**Árvores externas classificadas, sem eliminação:** `/root/.cursor` (416 ficheiros, ~9,8 MB de conteúdo, última modificação há 54 dias), `/root/.vscode` (1 ficheiro), `/root/.claude-server-commander` (4 ficheiros, ~5,4 MB), `/home/ubuntu/.local/share/rea-github-transport` (1 ficheiro), `/home/ubuntu/.local/share/hopper` (zero ficheiros), `/root/migration-preserved` (17 ficheiros), `/root/migration-20260923` (265 ficheiros). Nenhuma referência direta de processo/cwd/FD encontrada na fotografia da auditoria; **não apagar dados, sessões, histórico ou segredos apenas por ausência de processos**.

## Reconciliação de commits do GitHub — sem alterar produção

Comparação autenticada dos commits locais registados na auditoria da VPS com a `main` dos seus repositórios:

| Projeto | Código/release registado na VPS | GitHub main | Relação de histórico |
|---|---|---|---|
| `pink-iptv` | `ccccaf1eb25ca80936763f7d6a17e4dd00347e8a` | `32f3638d3e02f01558ef86127d865956f5c52e64` | A `main` tem 665 commits posteriores ao HEAD local; é preciso verificar a versão realmente usada pelo serviço |
| `fadego` | `2b3554ec6e075e36041e44178f99535e00961b2f` | `7b2aea337605e145a9b5b3122bed399c48309b95` | A `main` tem 6 commits posteriores à release identificada |
| `iptvpn-bot` | `6d26ea34a5843dae1e3d48e276ad05b54f614d1b` | `a5b4861af910e92763ab435cf8812cb856d4d700` | **Históricos divergentes:** 9 commits exclusivos à `main` e 2 exclusivos ao HEAD local; scripts PM2/deploy entre os ficheiros alterados |

**Decisão:** NO-GO para `git reset --hard`, atualização automática, limpeza de branches ou deploy dos três projetos até confirmar o contrato de release, eventuais alterações locais e testes funcionais. O nome das pastas coincide com os repositórios; isso não demonstra identidade de versões em execução.



## Verificação complementar de versões e guardas (05–06/11/2026)

- [VPS #42133448972](https://github.com/martaxi-boss/VPS/actions/runs/42133448972), auditoria read-only dos diretórios reais e processos systemd: `pink-iptv` está no branch local `builder/android-shell-002`, SHA `ccccaf1e...` e **6 alterações rastreadas locais**; `iptvpn-bot` está no branch `security/iptvpn-bot-secret-vault-001`, SHA `6d26ea34...` e **6 alterações rastreadas locais**. O SHA do bot é idêntico ao HEAD do branch GitHub do mesmo nome, apesar de divergir de `main`. Não confundir divergência de branches com falta de código no GitHub. **Não aplicar pull/reset nem deploy enquanto as alterações locais não forem preservadas e verificadas**.
- Referências de recuperação sem alterações na VPS: [PINK branch `reconcile/vps-working-head-20261105`](https://github.com/martaxi-boss/pink-iptv/tree/reconcile/vps-working-head-20261105) e [IPTV VPN Bot branch `reconcile/vps-installed-20261105`](https://github.com/martaxi-boss/iptvpn-bot/tree/reconcile/vps-installed-20261105). São referências a **commits existentes**, não snapshots das seis alterações ainda não commitadas.
- O processo de limpeza do diretório Hopper antigo executou guardas em [VPS #42133943881](https://github.com/martaxi-boss/VPS/actions/runs/42133943881), que **bloquearam corretamente** com `BLOCKED_OWNER_OR_NONEMPTY`. **Nenhuma remoção comprovada**; a pasta mantém-se preservada. O workflow temporário foi retirado no [commit f9eb11cb](https://github.com/martaxi-boss/VPS/commit/f9eb11cb2a18ac8072186d22536ce84cfc6f2423). Não relaxar as guardas sem novo diagnóstico de propriedade e conteúdo.
- A auditoria permanente da VPS foi reposta exatamente à versão original pré-F9 no [commit c71a85cd](https://github.com/martaxi-boss/VPS/commit/c71a85cdfb1b139e634197131985a326a757f684) e a execução [#42133850727](https://github.com/martaxi-boss/VPS/actions/runs/42133850727) concluiu **SUCCESS**. Nenhum diagnóstico temporário ficou inserido no workflow habitual.

**Estado:** F9 continua aberta; não há prova de desinstalação dos 16 programas globais nem de captura das alterações locais dos projetos. Manter backups de referência e funcionamento dos serviços até reconciliação validada.


## Higienização final do Hopper — 06/11/2026

- O primeiro workflow de limpeza [#42133943881](https://github.com/martaxi-boss/VPS/actions/runs/42133943881) foi corretamente **bloqueado** ao detetar uma pasta raiz não vazia. Não houve remoção nesse teste.
- A auditoria adicional só de leitura [#42134256803](https://github.com/martaxi-boss/VPS/actions/runs/42134256803) provou UID 1000 (`ubuntu`), diretório canónico sem symlink ou mountpoint, **5 diretórios interiores e zero ficheiros**. A razão do bloqueio era existirem subdiretórios vazios.
- A limpeza mínima [#42134483519](https://github.com/martaxi-boss/VPS/actions/runs/42134483519) executou guardas independentes e devolveu `F9_EMPTY_HOPPER_NESTED_DIRECTORIES=5`, `F9_EMPTY_HOPPER=REMOVED`, `F9_PROTECTED_SERVICES_UNCHANGED=8`. Foram removidos **seis diretórios vazios** (pasta raiz e cinco interiores), sem `rm -rf` ou remoção de qualquer ficheiro.
- O workflow temporário de limpeza foi eliminado de `martaxi-boss/VPS` após PASS, no [commit 919a2e37](https://github.com/martaxi-boss/VPS/commit/919a2e37d74e40b7687e46686a44a0b5853c9d9c). O inventário normal foi restituído à versão sem código de diagnóstico no [commit 8b499556](https://github.com/martaxi-boss/VPS/commit/8b4995567499c24847306fc723e43f46f9885cf7).

**Pendências F9 preservadas:** 16 pacotes APT de aplicações ainda globais, dos quais oito sem executor privado certificado; seis alterações locais rastreadas em `pink-iptv` e outras seis em `iptvpn-bot` ainda não preservadas em commits; prova de origem/release para as instalações sem Git worktree. É deliberado não resolver estes problemas com `apt purge` global ou `git reset --hard` sem alternativas, testes de consumidores e rollback. Não declarar a Fase 9 concluída.


## Pós-verificação independente após higiene (06/11/2026)

- [VPS read-only #42134629602](https://github.com/martaxi-boss/VPS/actions/runs/42134629602): workflow original de inventário **SUCCESS** após retirar código de diagnóstico e limpar as seis pastas vazias Hopper; `df -hT /` = **72G total, 30G usados, 42G livres**. Serviços `pink-iptv-backend`, `pink-vpn`, `fadego-staging`, `lowcost-europa`, `pm2-iptvpn-bot`, `pm2-telegram-robot-leads`, `nginx` e `postgresql@16-main` constam entre os ativos.
- [Ferrari Skill → GitHub Actions → VPS → ZIP #42134719562](https://github.com/martaxi-boss/VPS/actions/runs/42134719562): execução **SUCCESS**; `report.json.status=completed`; `artifacts/inventory.json` verificado após descarga. Resultado: **40 ações registadas / 40 invocáveis, 47/56 candidatos privados detetados, 9 não detetados**. Nenhuma regressão de deteção observada após a limpeza.
- **Critério F9 ainda não satisfeito:** programas APT globais de aplicação ainda presentes; alterações locais não commitadas no PINK e IPTV VPN Bot; algumas instalações sem worktree Git exigem prova de proveniência via releases. Nenhum `git reset`, deploy cruzado ou `apt purge` foi executado para contornar o bloqueio.


## Ponto 5 — auditoria de alinhamento e higiene com prova real, 06/11/2026

**Situação:** a parte *Ferrari-only* está consistente; a higienização **transversal da VPS ainda tem bloqueios de propriedade e consumidores**. Não executar `apt purge` ou `git reset --hard` apenas para obter um estado aparentemente verde.

**Evidência operacional atual:**

- [VPS #42200744741](https://github.com/martaxi-boss/VPS/actions/runs/42200744741) — auditoria independente, **SUCCESS**: `current` é a release privada `a266b25e06a9c8acf1fdc940d22b99070cd17ded`; `engine` presente, catálogo com **40 ações**; **8/8 componentes privados específicos conferidos** (OpenPencil, Node, ComfyUI, modelo SD1.5, faster-whisper, modelo tiny, Ruflo e REA); **0 resíduos de teste nas rotas e padrões conhecidos** do Ferrari; **8/8 serviços protegidos ativos**; **39,4 GiB livres**. Não houve escritas na VPS nem reinstalação de dependências.
- [Ferrari Skill #42200976757](https://github.com/martaxi-boss/VPS/actions/runs/42200976757) — workflow **original e inalterado** `ferrari-skill-request.yml`, `FERRARI_SKILL_JOB_STATUS=completed`, `FERRARI_SKILL_RESPONSE_ZIP=PASS`, `FERRARI_SKILL_END_TO_END=PASS`; `response.zip` com `report.json` e `artifacts/inventory.json` inspecionados. Inventário: **40/40 ações invocáveis, 47/56 candidatos selecionados detetados, 9 não detetados**, 59 programas instalados no âmbito do inventário (não confundir com ações); sem regressão observada.
- [Comparação GitHub](https://github.com/martaxi-boss/skill-universal/compare/a266b25e06a9c8acf1fdc940d22b99070cd17ded...3991587fb4f060c4f74af34dfd68f672ab3a87e3): o `main` pré-relatório estava **24 commits à frente** da release ativa; as diferenças eram documentação, referências Skill, novos instaladores/smokes e testes dos pontos 2–4 — **sem alterações aos ficheiros `engine/` nem ao catálogo de 40 ações**. Os modelos dos pontos 2–3 já foram instalados na pasta privada da VPS com prova real. **Não forçar novo deploy** só para coincidir o SHA documental; a correspondência *funcional* está demonstrada, a revisão GitHub e a release instalada continuam deliberadamente identificadas em separado.

**Os 16 pacotes APT globais mantêm-se instalados** na fotografia real #42200744741: `libreoffice`, `ansible`, `yt-dlp`, `gimp`, `blender`, `kdenlive`, `darktable`, `openscad`, `librecad`, `qgis`, `audacity`, `obs-studio`, `solvespace`, `synfigstudio`, `openshot-qt` e `calibre`.

| Classificação baseada nas provas F8/F9 | Pacotes |
| --- | --- |
| 8 famílias **com alternativa privada certificada nos casos testados** | LibreOffice, Ansible, GIMP, Blender, Kdenlive/MLT, Darktable, OpenSCAD, Calibre |
| 8 famílias **sem substituto privado certificado** | yt-dlp, LibreCAD, QGIS, Audacity, OBS Studio, SolveSpace, Synfig, OpenShot |

**Decisão conservadora:** os executores das 40 ações estão privados, mas *não* está comprovado que cada APT global possa ser removido sem afetar outros projetos ou uma função ainda não testada. As oito famílias sem substituto privado **não devem ser apagadas**; nem as outras oito podem ser purgadas sem revisão de consumidores, dependências indiretas, snapshots e rollback. Zero pacotes APT globais removidos neste ponto.

**Resíduos externos:** `/home/ubuntu/.local/share/rea-github-transport` ainda consta como presente; `/root/.cursor` e `/root/.vscode` constam como presentes na leitura do utilizador `ubuntu`. Propriedade/consumidores ainda não comprovados; **não apagar sessões, credenciais, estado antigo ou estruturas de outros projetos**. O antigo link `motor-ferrari` e diretório Hopper não eram visíveis na consulta, o que **não é prova de remoção absoluta**.

**Outros repositórios:** a auditoria anterior identificou seis alterações locais rastreadas no PINK IPTV e seis no IPTV VPN Bot, ainda sem prova de preservação num commit. Este ponto 5 **não alterou** esses projetos nem tentou mudar os seus HEADs, branches, PM2 ou releases. A sua reconciliação é independente e exige snapshot seguro antes de qualquer mudança.

**Higiene deste ponto:** retirar do GitHub, após a prova, apenas o workflow temporário `ferrari-p5-audit-once-20261106.yml` e os dois JSON sintéticos desta auditoria. O workflow normal de pedidos e o pin de SSH permanecem intactos. Não houve resíduos privados conhecidos a remover na VPS. 

**Veredito P5:** alinhamento e isolamento **Ferrari-only verificados**; higiene sem resíduos de ensaio e sem regressões. **Fase 9 transversal ainda não encerrada**, precisamente porque faltam a classificação de consumidores dos 16 APT, um possível resíduo de transporte legado e as alterações locais de projetos alheios. Não confundir prudência com uma certificação de desinstalação ou com 100% da VPS higienizada.
