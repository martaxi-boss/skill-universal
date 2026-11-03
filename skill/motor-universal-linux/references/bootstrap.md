# Bootstrap portátil — Motor Ferrari Ubuntu

**UMA Skill Universal Ferrari**, um motor Ubuntu independente e um orquestrador próprio. Este documento acompanha o ZIP da Skill e resume a fotografia de 03/11/2026. A fonte atual prevalecente é [BOOTSTRAP.md](https://github.com/martaxi-boss/skill-universal/blob/main/BOOTSTRAP.md); não reconstruir o estado a partir das fases antigas.

## Arquitetura e isolamento

ChatGPT/Codex interpreta → uma Skill Universal → GitHub autenticado (martaxi-boss/VPS) → workflow exclusivo → SSH existente → Ferrari Ubuntu → ZIP e relatório. O motor seleciona as ferramentas; REA e Ruflo são componentes opcionais, não coordenadores. Não alterar ligação SSH, Supervisor ou projetos de terceiros.

A instalação a preservar é /home/ubuntu/.local/share/motor-ferrari/. O REA oficial do Ferrari é rea-agents@6.8.0 instalado em .runtime/npm/rea, com Node 22.23.4 privado. Tem ainda Java 25.0.5 privado, Ghidra 12.2, JADX 1.5.6 e Apktool 3.0.3 privado. **O REA antigo da VPS é outro projeto**; não o remover até provar independência funcional, proveniência e rollback.

## Evidência recente (03/11/2026 UTC)

- [Ferrari VPS #41671631900](https://github.com/martaxi-boss/VPS/actions/runs/41671631900): 139 testes PASS, deploy e higiene Ferrari-only PASS; release 6c93a392dfe9a02d7ccfef9d47317c9685976484.
- [Skill inventário #41672372249](https://github.com/martaxi-boss/VPS/actions/runs/41672372249): ZIP com inventário, status completed, 81 programas detetados nos catálogos; 55/56 candidatos Ubuntu encontrados; 25 ações externas e 12 operações base.
- [REA Ferrari #41654437939](https://github.com/martaxi-boss/VPS/actions/runs/41654437939): ELF e Android com o REA próprio PASS, Apktool 3.0.3 PASS; [Skill REA ELF #41655035184](https://github.com/martaxi-boss/VPS/actions/runs/41655035184) ponta a ponta PASS.
- [DAG remoto #41620077416](https://github.com/martaxi-boss/VPS/actions/runs/41620077416): plano com etapas e ZIP confirmado.
- Aplicações gráficas APT 15/15 instaladas, sem utilização interativa certificada; Prometheus/Valkey em runtime privado; ComfyUI CPU sem modelos ou inferência comprovada; Penpot apenas preparado, sem Docker.

**Programas detetados não são automaticamente testados ou disponíveis pela Skill.** Não declarar 81 ações nem equivalência com o catálogo completo do REA original. CAD, BIM, CONSTRUÇÃO e 3D são domínios progressivos: há casos reais certificados, mas não projetos profissionais completos de qualquer formato.

## Continuar a trabalhar

1. Ler o BOOTSTRAP GitHub e os novos runs da VPS antes de afirmar o estado.
2. Para operações remotas ler references/github-bridge.md; criar um único JSON novo kind=inventory, operation, invoke, auto ou plan; conferir run, response.zip, report.json e artefactos.
3. Auditar proveniência Java/Node/Python, pacotes do sistema, binários e serviços, bem como dependências REA e fornecedores, antes de qualquer remoção.
4. Testar Ferrari com recursos do REA antigo inacessíveis sem mexer no legado; certificar Skill→VPS→ZIP e documentar caminhos, backups e recuperação.
5. Integrar ferramentas faltantes só após um caso concreto e teste Ubuntu. Manter uma Skill, sem camadas novas.

O GitHub/VPS é potencialmente público: nunca enviar credenciais ou ficheiros privados por JSON/base64. Uma certificação de cliente exige ainda verificar a versão efetivamente instalada da Skill em ChatGPT.
