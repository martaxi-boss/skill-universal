# Bootstrap portátil — Motor Ferrari Ubuntu

**UMA Skill Universal Ferrari**, um motor Ubuntu independente e um orquestrador próprio. Este documento acompanha o ZIP da Skill e resume a fotografia verificada em 05/11/2026. A fonte atual prevalecente é [BOOTSTRAP.md](https://github.com/martaxi-boss/skill-universal/blob/main/BOOTSTRAP.md); não reconstruir o estado a partir das fases antigas.

## Arquitetura e isolamento

ChatGPT/Codex interpreta → uma Skill Universal → GitHub autenticado (martaxi-boss/VPS) → workflow exclusivo → SSH existente → Ferrari Ubuntu → ZIP e relatório. O motor seleciona as ferramentas; REA e Ruflo são componentes opcionais, não coordenadores. Não alterar ligação SSH, Supervisor ou projetos de terceiros.

A instalação física a preservar é **/srv/projects/skill-universal/**, com a ligação histórica /home/ubuntu/.local/share/motor-ferrari/ retirada após migração dos launchers (merge Ferrari 292aeb7d). O REA oficial do Ferrari é rea-agents@6.8.0 instalado em .runtime/npm/rea, com Node 22.23.4 privado. Tem ainda Java 25.0.5 privado, Ghidra 12.2 e JADX 1.5.6 independentes, Ghidra 12.1.4 e JADX headless MCP 0.7.1 compatíveis com o REA original, e Apktool 3.0.3 privado. **Os dois REAs antigos (REA FINAL e Trial) foram removidos da VPS** e a ausência validada em [#41840478411](https://github.com/martaxi-boss/VPS/actions/runs/41840478411). O REA privado do Ferrari continua e deve permanecer dentro deste projeto.

## Sincronia real — 05/11/2026

- **Código Ferrari verificado antes da atualização documental:** b2869e334d9d68a0c988905e71ce0badec6ba359; [CI #41922781312](https://github.com/martaxi-boss/skill-universal/actions/runs/41922781312) PASS. **Ponte VPS:** usa ainda a revisão pinada 292aeb7d10eecef8c3ca84760cd579e84e4b97f3 para validar pedidos; não é prova de que current na VPS corresponda ao HEAD GitHub.
- **Hopper 6.6.1 privado e oficial:** tools/hopper-6.6.1, assinatura e origem verificadas [#41921893982](https://github.com/martaxi-boss/VPS/actions/runs/41921893982), REA doctor [#41922087539](https://github.com/martaxi-boss/VPS/actions/runs/41922087539) PASS. **Demo sem licença comercial**; não declarar exportação/depuração ou análise completa certificada.
- **Pedido real REA:** [#41981152670](https://github.com/martaxi-boss/VPS/actions/runs/41981152670) status completed e ZIP PASS. [#41981478159](https://github.com/martaxi-boss/VPS/actions/runs/41981478159) foi apenas higiene do workflow, sem motor executado.

## Certificação adicional — 05/11/2026

- Inventário real [#41991752006](https://github.com/martaxi-boss/VPS/actions/runs/41991752006): 55/56 candidatos Ubuntu encontrados, 40 ações invocáveis, Penpot não detetado.
- Vídeo real [#41992064762](https://github.com/martaxi-boss/VPS/actions/runs/41992064762): MLT/Kdenlive → MP4 através de kind=auto, H.264 320×180, 2,005 s, áudio AAC, FFprobe PASS. Certificação limitada ao projeto sintético testado.

## Atualização operacional — Android CLI privado, 04/11/2026

- O Ferrari tem agora **40 ações tipadas operacionais** no motor instalado; quatro novas: `android-apksigner-verify`, `android-aapt2-manifest`, `android-zipalign-apk`, `android-adb-install-apk`. O código passou CI na main [#41853671359](https://github.com/martaxi-boss/skill-universal/actions/runs/41853671359), e os quatro binários Android foram instalados de forma **privada em /srv/projects/skill-universal/tools/android-cli-36.0.0/**, com estado em `.runtime/android-cli/`.
- Medição real de ferramentas privadas: **19 050 496 bytes**, sem emuladores, imagens Android ou instalação global; versões Ubuntu/Linux comprovadas [#41854771565](https://github.com/martaxi-boss/VPS/actions/runs/41854771565) e [#41855114605](https://github.com/martaxi-boss/VPS/actions/runs/41855114605). **Apktool 3.0.3** continua atualizado.
- APK de teste **real** construída com Apktool, manifesto inspecionado com AAPT2, alinhada com Zipalign, assinada e verificada com Apksigner: PASS [#41854398886](https://github.com/martaxi-boss/VPS/actions/runs/41854398886). ADB respondeu ao comando de versão, mas **não houve instalação em telemóvel físico**.
- Fluxo **Skill→GitHub Actions→Ferrari→Zipalign→ZIP devolvido** por `kind=auto` PASS [#41856969562](https://github.com/martaxi-boss/VPS/actions/runs/41856969562). A ponte continua a usar validação pinada histórica e rejeita `kind=invoke` com os quatro IDs novos; **não alterar a ponte sem autorização**. O motor trata corretamente `kind=auto`.
- O SDK Android antigo, instalado fisicamente em `/srv/projects/android-sdk`, continua presente (aproximadamente **17,82 GB**) e pertence à limpeza futura após apurar todos os consumidores, particularmente testes do PINK IPTV. **Não foi eliminado nesta fase.**

## Evidência recente (04/11/2026 UTC)

- [Ferrari VPS #41786521407](https://github.com/martaxi-boss/VPS/actions/runs/41786521407): **197 testes PASS**, 35 ações, Scribus PDF/SLA e LMMS WAV não silencioso, fornecedores privados REA (Ghidra/JADX), Valkey e higiene Ferrari-only PASS; release **0a1a4c190a7d33752d6dc3f4418ed44735c8a7dd**.
- [Skill inventário #41784949891](https://github.com/martaxi-boss/VPS/actions/runs/41784949891): ZIP com inventário, status completed, 81 programas detetados nos catálogos; 55/56 candidatos Ubuntu encontrados; 34 ações externas naquela fotografia, 35 após instalar LMMS e 12 operações base.
- [REA Ferrari #41654437939](https://github.com/martaxi-boss/VPS/actions/runs/41654437939): ELF e Android com o REA próprio PASS, Apktool 3.0.3 PASS; [Skill REA ELF #41655035184](https://github.com/martaxi-boss/VPS/actions/runs/41655035184) ponta a ponta PASS.
- [DAG remoto #41620077416](https://github.com/martaxi-boss/VPS/actions/runs/41620077416): plano com etapas e ZIP confirmado.
- [Fase 2 Scribus pela Skill #41785658074](https://github.com/martaxi-boss/VPS/actions/runs/41785658074): PDF+SLA real. Calibre, Darktable, Krita e GIMP também validados por ficheiros e ZIP, fechando 5/5. [Fase 3 LMMS pela Skill #41787031335](https://github.com/martaxi-boss/VPS/actions/runs/41787031335): WAV estéreo 44,1 kHz, 3,428 s, com áudio não silencioso. MLT/Kdenlive → MP4 sintético executado e validado via Skill [#41992064762](https://github.com/martaxi-boss/VPS/actions/runs/41992064762); Synfig CLI não detetado. Aplicações gráficas APT 15/15 instaladas, sem utilização interativa generalizada certificada; Prometheus/Valkey em runtime privado; ComfyUI CPU sem modelos ou inferência comprovada; Penpot apenas preparado, sem Docker.

- [REA comparação MCP #41708905353](https://github.com/martaxi-boss/VPS/actions/runs/41708905353): 229 nomes em ambos os REAs, zero em falta. [REA profundo #41710014556](https://github.com/martaxi-boss/VPS/actions/runs/41710014556): Ghidra ELF e JADX classe Android PASS. [Skill MCP catálogo #41713808747](https://github.com/martaxi-boss/VPS/actions/runs/41713808747) e ferramentas [ELF #41717389118](https://github.com/martaxi-boss/VPS/actions/runs/41717389118), [Apktool #41717684160](https://github.com/martaxi-boss/VPS/actions/runs/41717684160): todos com ZIP e dados reais PASS.

**Programas detetados não são automaticamente testados ou disponíveis pela Skill.** Não declarar 81 ações nem equivalência com o catálogo completo do REA original. CAD, BIM, CONSTRUÇÃO e 3D são domínios progressivos: há casos reais certificados, mas não projetos profissionais completos de qualquer formato.

## Continuar a trabalhar

1. Ler o BOOTSTRAP GitHub e os novos runs da VPS antes de afirmar o estado.
2. Para operações remotas ler references/github-bridge.md; criar um único JSON novo kind=inventory, operation, invoke, auto, plan ou rea-mcp (catálogo e duas funções MCP reais já certificados via Skill; outras funções precisam de testes por caso); conferir run, response.zip, report.json e artefactos.
3. Auditar proveniência Java/Node/Python, pacotes do sistema, binários e serviços, bem como dependências REA e fornecedores, antes de qualquer remoção.
4. Confirmar que já não há dependências nos caminhos dos REAs antigos removidos; auditar runtime Ferrari isolado, certificar Skill→VPS→ZIP e documentar caminhos, backups e recuperação.
5. Integrar ferramentas faltantes só após um caso concreto e teste Ubuntu. Manter uma Skill, sem camadas novas.

O GitHub/VPS é potencialmente público: nunca enviar credenciais ou ficheiros privados por JSON/base64. Uma certificação de cliente exige ainda verificar a versão efetivamente instalada da Skill em ChatGPT.
