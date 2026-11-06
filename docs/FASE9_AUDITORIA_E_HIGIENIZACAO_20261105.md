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


## Atualização certificada — 06/11/2026, após a F9 original

Esta secção substitui as fotografias históricas acima; não interpretar afirmações antigas de «16/16 APT instalados» como estado atual.

- [Auditoria de consumidores #42223369203](https://github.com/martaxi-boss/VPS/actions/runs/42223369203): 16 pacotes globais iniciais, 8/8 serviços ativos, oito projetos identificados e release Ferrari privada `f1f3b03525adec7018d7d629243e7b0fbb7f5087`.
- [Simulação de remoção #42223857600](https://github.com/martaxi-boss/VPS/actions/runs/42223857600): o APT removeria exatamente `ansible`, `blender`, `calibre`, `darktable`, `gimp`, `kdenlive`, `libreoffice` e `openscad`, sem outros nomes. Os executores privados foram validados pelo motor (não confundir contagem de caminhos à mão com o catálogo real).
- [Backup privado #42225749103](https://github.com/martaxi-boss/VPS/actions/runs/42225749103): oito pacotes originais com versão e SHA256 preservados dentro de `/srv/projects/skill-universal/.runtime/phase9-apt-eight-rollback-20261106`; nenhum pacote removido nesta etapa.
- [Remoção controlada #42225950692](https://github.com/martaxi-boss/VPS/actions/runs/42225950692): **oito pacotes globais efetivamente retirados**, 40 ações Ferrari e 8/8 serviços preservados; sem `apt autoremove` e sem alterações aos outros projetos.
- [Preservação das 12 alterações locais #42226572746](https://github.com/martaxi-boss/VPS/actions/runs/42226572746): seis no PINK IPTV e seis no IPTV VPN Bot; backups dentro do seu próprio Git local. Não foram feitos `git reset`, `merge` nem publicadas diferenças no repositório público.
- [Backup dos legados #42227038594](https://github.com/martaxi-boss/VPS/actions/runs/42227038594) e [remoção #42227814089](https://github.com/martaxi-boss/VPS/actions/runs/42227814089): três raízes externas `/root/.cursor`, `/root/.vscode` e `/home/ubuntu/.local/share/rea-github-transport` eliminadas após verificação de proprietários/processos; arquivo mantido em `/srv/projects/VPS/.runtime/f9-legacy-snapshot-20261106`.
- [Leitura independente final #42228102427](https://github.com/martaxi-boss/VPS/actions/runs/42228102427): **PASS**, 8/8 serviços ativos, oito projetos, oito APT restantes, três resíduos ausentes, Ferrari `f1f3b035` ativo, ambos os projetos com seis alterações locais intactas; 40,08 GiB livres. REA e Ruflo privados detetados.

**Os oito APT restantes**, sem substituição privada certificada, são `yt-dlp`, `librecad`, `qgis`, `audacity`, `obs-studio`, `solvespace`, `synfigstudio` e `openshot-qt`. Não têm consumidores diretos em execução nem referências nos ficheiros textuais pesquisados no momento da leitura; isso não prova ausência de consumidores indiretos, nem autoriza apagar capacidades. Instalar, testar e só depois purgar de modo controlado.

**GitHub/VPS:** nomes das oito pastas coincidem com o inventário esperado. `pink-iptv` e `iptvpn-bot` têm `origin` correspondente ao nome e worktree local alterada (6/6). As outras seis pastas não apresentam todas um Git worktree normal: comprovar proveniência por manifestos/release antes de exigir `git pull` ou alterar serviços. Não enviar patches de produção sensíveis para GitHub público.

**Estado real: F9 PARCIAL, NÃO 100% CONCLUÍDA.** Restam as oito migrações e a reconciliação segura dos projetos; a higienização efetuada está certificada e os backups preservados por projeto.

## Continuação F9 — yt-dlp privado: instalação e transferência local certificadas (06/11/2026)

- [PR #85](https://github.com/martaxi-boss/skill-universal/pull/85), merge `a6e0f04aa0cfcb15c4a8a1d67361d8d4c82334af`: instalador privado, SHA256 fixo da release oficial `yt-dlp_linux` **2026.10.26**, oito testes novos e descoberta de executor isolado no código Ferrari. [CI da release #42231667268](https://github.com/martaxi-boss/skill-universal/actions/runs/42231667268) PASS; 329 testes na CI da PR [#42231240218](https://github.com/martaxi-boss/skill-universal/actions/runs/42231240218).
- [VPS #42232172018](https://github.com/martaxi-boss/VPS/actions/runs/42232172018): instalou com checksum verificado o binário autónomo em `/srv/projects/skill-universal/tools/yt-dlp-2026.10.26/yt-dlp`, 1755 extratores, verificação idempotente, pacote APT global inalterado, 8/8 serviços protegidos e release `f1f3b035...` preservados.
- [VPS #42232550380](https://github.com/martaxi-boss/VPS/actions/runs/42232550380): **PASS de teste funcional** em HTTP local `127.0.0.1`, HTML5 `<video>` e ficheiro sintético MP4; o yt-dlp privado extraiu o URL e descarregou um ficheiro idêntico byte a byte. Isto não certifica todos os sites, autenticação, DRM nem formatos de vídeo reais.
- **Ainda não fazer `apt purge yt-dlp`:** o pacote global continua instalado para recuperação. A referência do novo executável no `tool_runtime.py` está no GitHub, mas a release ativa da VPS continua `f1f3b035...`; ativar e certificar primeiro uma release compatível e auditar as dependências/consumidores do pacote global. A contagem de **oito pacotes APT restantes permanece inalterada**.
- Os outros sete programas (LibreCAD, QGIS, Audacity, OBS Studio, SolveSpace, Synfig e OpenShot) ainda não têm alternativas privadas certificadas. Não declarar F9 encerrada.

## Continuação real — 06/11/2026, após o yt-dlp (estado atualizado)

Esta secção **substitui o estado histórico dos «outros sete ainda sem substituto»**. Distinguir presença de ficheiro, instalação privada, arranque CLI, desenho real, GUI e independência total:

| Programa | Estado privado observado | Prova VPS | Limite |
| --- | --- | --- | --- |
| yt-dlp 2026.10.26 | SHA256, extratores e download HTTP sintético byte-idêntico | [#42232550380](https://github.com/martaxi-boss/VPS/actions/runs/42232550380) | Sites comerciais, DRM e dependências externas não cobertos |
| LibreCAD 2.2.1.6 | AppImage oficial extraído dentro de `tools/`, digest validado (395 MB) | [#42237644608](https://github.com/martaxi-boss/VPS/actions/runs/42237644608) | Interface e edição CAD ainda sem teste funcional |
| Audacity 4.0.2 | AppImage extraído, digest validado (273 MB) | [#42237644608](https://github.com/martaxi-boss/VPS/actions/runs/42237644608) | Áudio, GUI e edição ainda sem teste funcional |
| OpenShot 4.1.1 | AppImage extraído, digest validado (826 MB) | [#42237644608](https://github.com/martaxi-boss/VPS/actions/runs/42237644608) | Edição e renderização de vídeo ainda por testar |
| Synfig Studio 1.5.5 | Type-1 AppImage oficial executável, SHA256 validado (111 MB) | [#42237644608](https://github.com/martaxi-boss/VPS/actions/runs/42237644608) | Formato não suporta o mesmo modo de extração; GUI e independência por certificar |
| OBS Studio 32.2.2 | Pacote oficial Ubuntu 24.04 isolado, 457 MB; conflito de `libobs` global corrigido, `--version` e `libobs` privado **PASS** | [#42244136623](https://github.com/martaxi-boss/VPS/actions/runs/42244136623) | Gravação, cenas, WebSocket, stream e dependências totais não certificados |
| SolveSpace 3.1 | Debian oficial Ubuntu 24.04 SHA256 validado, executável privado (9,8 MB) | [#42240722944](https://github.com/martaxi-boss/VPS/actions/runs/42240722944) | Usa bibliotecas básicas GTK/GL Ubuntu; GUI e CAD real por certificar |
| QGIS 4.2.3 | Conda-forge GPL-2.0-only inteiramente no Ferrari; CLI, catálogo nativo, PyQGIS, bibliotecas GIS privadas **PASS**; 3,1 GB + 1,2 GB em cache/ambiente | [#42244331078](https://github.com/martaxi-boss/VPS/actions/runs/42244331078) | Inicialização integral de providers/GUI encontra `libhdf5_cpp.so.320` opcional em falta; não declarar todo o QGIS verde |

**Teste funcional de geometria 2D sem GPU — PASS:** [VPS #42246944925](https://github.com/martaxi-boss/VPS/actions/runs/42246944925). Python/QgsGeometry privados criaram polígono sintético 100×50 metros, validaram área 5 000 m² e GeoJSON e geraram PNG com Qt/QImage por CPU. Não é projeto legal de arquitetura nem certificação integral de GUI/PDAL. A primeira tentativa [#42245729130](https://github.com/martaxi-boss/VPS/actions/runs/42245729130) corretamente revelou a falha do módulo opcional; a seguinte separou esse módulo da função que já pode ser certificada.

**Integridade operacional e espaço:** oito serviços VPS intactos em todas as provas PASS citadas; última medição após QGIS: aprox. 34 GB disponíveis em disco de 72 GB. Ferramentas e caches instalados somente em `/srv/projects/skill-universal/{tools,.runtime}`. Nenhum dos oito pacotes APT antigos foi removido nesta segunda migração, para preservar o rollback. Testar e simular remoções antes de purgar; nunca `apt autoremove` às cegas.

**Alinhamento GitHub↔VPS:** instaladores/testes/seleção de caminhos privados estão no repositório `martaxi-boss/skill-universal`. A release de código ativa ainda era `f1f3b03525adec7018d7d629243e7b0fbb7f5087` nas últimas provas, embora as ferramentas novas já estejam em `tools/`. Essa diferença **não deve ser descrita como release alinhada** até a versão nova passar `install/vps-isolated-release.sh --check`, ativação com rollback e leitura de verificação. Projetos e alterações locais externos ao Ferrari permanecem fora do âmbito destas modificações.

**Veredito nesta fotografia:** 8/8 programas possuem presença privada verificável; certificação funcional desigual. **A Fase 9 ainda está aberta**, pois faltam prova/isolamento completos de GUI, reconciliação segura dos pacotes globais, higiene de workflows temporários e ativação da release.

## Readback operacional e hygiene — 06/11/2026 (estado posterior às secções anteriores)

- **SolveSpace reparado:** o pacote Ubuntu 24.04 contém duas ligações relativas a recursos provenientes de outros pacotes. A [PR #98](https://github.com/martaxi-boss/skill-universal/pull/98) acrescentou o instalador com SHA256 fixo para `libjs-three` e `unifont`, ambos extraídos apenas para `/srv/projects/skill-universal/tools/solvespace-3.1-ubuntu24/usr/share/`. [Prova real #42250649475](https://github.com/martaxi-boss/VPS/actions/runs/42250649475): verificação de integridade PASS; 6/6 programas gráficos mantiveram o arranque em Xvfb temporário pelo período de observação. Isto **não** certifica funcionalidades de edição, som, vídeo, transmissões ou isolamento completo do Ubuntu. Oito serviços protegidos mantiveram-se ativos.
- **Release Ferrari ativa igual ao código GitHub certificado:** [#42251027341](https://github.com/martaxi-boss/VPS/actions/runs/42251027341) pré-ativação PASS, testes 373, 40/40 executores privados, CAD/3D, Office, Skill→ZIP e pós-ativação PASS. SHA ativo no instante da prova: `0b50e1d403deff8f3ccb421edd0b41c397d66b9b`. Release anterior `f1f3b035...` preservada para rollback. Duas tentativas concorrentes de ativação foram bloqueadas pela proteção contra corrida e pela leitura de SHA diferente; não significam falha da ativação certificada.
- **Skill real após a troca:** [#42251381147](https://github.com/martaxi-boss/VPS/actions/runs/42251381147), pedido `inventory`, `FERRARI_SKILL_JOB_STATUS=completed`, `FERRARI_SKILL_RESPONSE_ZIP=PASS`, `FERRARI_SKILL_END_TO_END=PASS`. Artefacto `ferrari-skill-result-42251381147` publicado no Actions.
- **APT global:** os oito pacotes antigos `audacity`, `librecad`, `obs-studio`, `openshot-qt`, `qgis`, `solvespace`, `synfigstudio` e `yt-dlp` **ainda estão instalados**. [Simulação #42251778630](https://github.com/martaxi-boss/VPS/actions/runs/42251778630) listou precisamente oito operações `Purg` e nenhum outro pacote; não executou purga nem `autoremove`. [Readback #42251655501](https://github.com/martaxi-boss/VPS/actions/runs/42251655501) confirmou SHA ativo e recursos privados. A [auditoria de referências #42252073995](https://github.com/martaxi-boss/VPS/actions/runs/42252073995) não terminou com informação conclusiva para as pastas `VPS`, `fadego`, `pink-iptv` e `telegram-robot-leads`; por isso não há prova suficiente de que se podem eliminar executáveis globais sem risco para outros projetos.
- **Higienização de transporte:** workflows de execução única da F9 e o pedido de inventário já executado foram eliminados da branch principal de `martaxi-boss/VPS` após confirmação dos logs; as execuções e artefactos do GitHub Actions continuam consultáveis. O workflow permanente `Ferrari Skill - authenticated request delivery` não foi modificado.

**Estado de encerramento:** Ferramentas privadas, arranque gráfico 6/6, motor 40/40, planta sintética sem GPU e release/ponte são PASS no âmbito indicado; **F9 mantém pendentes a verificação de consumidores APT, a higienização global segura e as provas funcionais completas dos seis programas gráficos**. Não converter estas provas parciais em classificação 10/10.
