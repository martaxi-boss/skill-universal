# Bootstrap portátil — Motor Ferrari Ubuntu

**UMA Skill Universal Ferrari**, um motor Ubuntu independente e um orquestrador próprio. Este documento acompanha o ZIP da Skill e resume a fotografia de 04/11/2026. A fonte atual prevalecente é [BOOTSTRAP.md](https://github.com/martaxi-boss/skill-universal/blob/main/BOOTSTRAP.md); não reconstruir o estado a partir das fases antigas.

## Arquitetura e isolamento

ChatGPT/Codex interpreta → uma Skill Universal → GitHub autenticado (martaxi-boss/VPS) → workflow exclusivo → SSH existente → Ferrari Ubuntu → ZIP e relatório. O motor seleciona as ferramentas; REA e Ruflo são componentes opcionais, não coordenadores. Não alterar ligação SSH, Supervisor ou projetos de terceiros.

A instalação física a preservar é **/srv/projects/skill-universal/**, com o alias histórico /home/ubuntu/.local/share/motor-ferrari/ apontando exclusivamente para esse projeto [#41714658308](https://github.com/martaxi-boss/VPS/actions/runs/41714658308). O REA oficial do Ferrari é rea-agents@6.8.0 instalado em .runtime/npm/rea, com Node 22.23.4 privado. Tem ainda Java 25.0.5 privado, Ghidra 12.2 e JADX 1.5.6 independentes, Ghidra 12.1.4 e JADX headless MCP 0.7.1 compatíveis com o REA original, e Apktool 3.0.3 privado. **O REA antigo da VPS é outro projeto**; ainda recebe pedidos pela branch `rea/one-skill-bridge-20261023` e não deve ser removido antes de migrar os consumidores, verificar usos e preparar rollback.

## Evidência recente (04/11/2026 UTC)

- [Ferrari VPS #41786521407](https://github.com/martaxi-boss/VPS/actions/runs/41786521407): **197 testes PASS**, 35 ações, Scribus PDF/SLA e LMMS WAV não silencioso, fornecedores privados REA (Ghidra/JADX), Valkey e higiene Ferrari-only PASS; release **0a1a4c190a7d33752d6dc3f4418ed44735c8a7dd**.
- [Skill inventário #41784949891](https://github.com/martaxi-boss/VPS/actions/runs/41784949891): ZIP com inventário, status completed, 81 programas detetados nos catálogos; 55/56 candidatos Ubuntu encontrados; 34 ações externas naquela fotografia, 35 após instalar LMMS e 12 operações base.
- [REA Ferrari #41654437939](https://github.com/martaxi-boss/VPS/actions/runs/41654437939): ELF e Android com o REA próprio PASS, Apktool 3.0.3 PASS; [Skill REA ELF #41655035184](https://github.com/martaxi-boss/VPS/actions/runs/41655035184) ponta a ponta PASS.
- [DAG remoto #41620077416](https://github.com/martaxi-boss/VPS/actions/runs/41620077416): plano com etapas e ZIP confirmado.
- [Fase 2 Scribus pela Skill #41785658074](https://github.com/martaxi-boss/VPS/actions/runs/41785658074): PDF+SLA real. Calibre, Darktable, Krita e GIMP também validados por ficheiros e ZIP, fechando 5/5. [Fase 3 LMMS pela Skill #41787031335](https://github.com/martaxi-boss/VPS/actions/runs/41787031335): WAV estéreo 44,1 kHz, 3,428 s, com áudio não silencioso. `melt` CLI disponível, vídeo ainda pendente; Synfig CLI não detetado. Aplicações gráficas APT 15/15 instaladas, sem utilização interativa generalizada certificada; Prometheus/Valkey em runtime privado; ComfyUI CPU sem modelos ou inferência comprovada; Penpot apenas preparado, sem Docker.

- [REA comparação MCP #41708905353](https://github.com/martaxi-boss/VPS/actions/runs/41708905353): 229 nomes em ambos os REAs, zero em falta. [REA profundo #41710014556](https://github.com/martaxi-boss/VPS/actions/runs/41710014556): Ghidra ELF e JADX classe Android PASS. [Skill MCP catálogo #41713808747](https://github.com/martaxi-boss/VPS/actions/runs/41713808747) e ferramentas [ELF #41717389118](https://github.com/martaxi-boss/VPS/actions/runs/41717389118), [Apktool #41717684160](https://github.com/martaxi-boss/VPS/actions/runs/41717684160): todos com ZIP e dados reais PASS.

**Programas detetados não são automaticamente testados ou disponíveis pela Skill.** Não declarar 81 ações nem equivalência com o catálogo completo do REA original. CAD, BIM, CONSTRUÇÃO e 3D são domínios progressivos: há casos reais certificados, mas não projetos profissionais completos de qualquer formato.

## Continuar a trabalhar

1. Ler o BOOTSTRAP GitHub e os novos runs da VPS antes de afirmar o estado.
2. Para operações remotas ler references/github-bridge.md; criar um único JSON novo kind=inventory, operation, invoke, auto, plan ou rea-mcp (catálogo e duas funções MCP reais já certificados via Skill; outras funções precisam de testes por caso); conferir run, response.zip, report.json e artefactos.
3. Auditar proveniência Java/Node/Python, pacotes do sistema, binários e serviços, bem como dependências REA e fornecedores, antes de qualquer remoção.
4. Testar Ferrari com recursos do REA antigo inacessíveis sem mexer no legado; certificar Skill→VPS→ZIP e documentar caminhos, backups e recuperação.
5. Integrar ferramentas faltantes só após um caso concreto e teste Ubuntu. Manter uma Skill, sem camadas novas.

O GitHub/VPS é potencialmente público: nunca enviar credenciais ou ficheiros privados por JSON/base64. Uma certificação de cliente exige ainda verificar a versão efetivamente instalada da Skill em ChatGPT.
