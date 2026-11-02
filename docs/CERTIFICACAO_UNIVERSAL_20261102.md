# Ferrari — certificação real do catálogo operacional

**Data:** 2 de novembro de 2026. **Ambiente:** VPS Ubuntu 24.04 LTS x86_64.

## Execução final

- **GitHub Actions VPS [#41545170664](https://github.com/martaxi-boss/VPS/actions/runs/41545170664): SUCCESS**.
- **Release ativa real:** `1b7ee15508d5780c3dbf22205ec625c2679348c5`.
- **59 testes unitários na VPS:** PASS (também no GitHub runner).
- **Catálogo:** 56 candidatos Ubuntu, mais entradas auxiliares do catálogo herdado. 45 programas binários detetados no conjunto dos dois catálogos; isto **não** quer dizer 45/56 programas selecionados, nem 45 ações.
- **Adaptadores executáveis:** 12 ações manifestadas e encontradas na VPS: `FERRARI_UNIVERSAL_ACTIONS_AVAILABLE=12`.
- **Execução automática real:** `FERRARI_UNIVERSAL_AUTO_EXECUTION=PASS` — pedido 'Converter markdown para docx' escolheu a ação do Pandoc e produziu um ficheiro DOCX.
- **Execuções multidomínio reais:** Graphviz gerou SVG, Pandoc DOCX, jq JSON formatado e file identificou MIME; o orquestrador executou três passos de ferramentas externas em paralelo/ondas: `FERRARI_UNIVERSAL_ORCHESTRATOR=PASS`.
- **Demais sistemas:** Ghidra/JADX, Blender/OpenSCAD e LibreOffice voltaram a passar os seus smokes funcionais. REA/Ruflo mantêm apenas evidência de arranque CLI, não testes profundos.
- **Higienização:** `FERRARI_ONLY_HYGIENE=PASS`; só remove releases antigas do Ferrari, preservando ativa e versão de recuperação; nenhuma ponte SSH anterior nem outro projeto foi alterado.

## Implementação

- `engine/tool_runtime.py`: inventário real, ações disponíveis, sugestão por intenção/formato, execução tipada e autoexecução quando a escolha é clara.
- `engine/tool_actions.json`: 12 adaptadores de diferentes programas Ubuntu. Novas operações podem ser adicionadas sem mexer no núcleo do orquestrador.
- `engine/orchestrator.py`: passos `operation=tool`, `tool`, `action`, `input` e dependências.
- `install/vps-tool-runtime-smoke.sh`: prova funcional na VPS.
- `python3 -m engine.ferrari tools|actions|route|auto|invoke`: CLI operacional.

## Limitações atuais

O Ferrari não executa automaticamente **qualquer** um dos 56 candidatos: ferramentas sem adaptador constam como `installed_unintegrated` se detetadas. O primeiro estágio de autoexecução escolhe uma ação quando uma correspondência explícita é superior às restantes; em caso de ambiguidade não executa às cegas. Execução de trabalhos complexos, fornecedores externos, BIM/FreeCAD e coordenação real REA/Ruflo requerem interfaces específicas. A ligação **direta** da Skill ChatGPT ao GitHub Actions e a devolução de artefactos ao chat ainda não foi demonstrada. Nenhum fornecedor pago é ativado por estes testes.
