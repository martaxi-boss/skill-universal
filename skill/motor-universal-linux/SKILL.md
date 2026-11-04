---
name: motor-universal-linux
description: Skill única de controlo do Motor Ferrari Ubuntu. Para pedidos de criação, programação, web, imagens, vídeo, áudio, PDF, CAD/BIM/3D, dados, engenharia reversa autorizada e automação, usando GitHub autenticado e os executores Ferrari reais na VPS.
---

# Motor Ferrari — Skill Universal

## Identidade e fonte de verdade

**UMA ÚNICA SKILL UNIVERSAL Ferrari; um motor e orquestrador próprios na VPS.** A IA anfitriã interpreta e orienta; o motor seleciona e executa ferramentas. Nunca substituir por Project Leader, pelo REA antigo, Ruflo ou outro coordenador. Não adicionar lógica à ponte SSH.

Ler [BOOTSTRAP canónico](https://github.com/martaxi-boss/skill-universal/blob/main/BOOTSTRAP.md) para o estado atual, instalações e pendências. Se só houver o pacote ZIP, ler references/bootstrap.md; a fonte GitHub prevalece sempre que acessível.

## Estado de referência — 04/11/2026

- Release VPS: **0a1a4c190a7d33752d6dc3f4418ed44735c8a7dd**, [deploy #41786521407](https://github.com/martaxi-boss/VPS/actions/runs/41786521407) **197 testes PASS** naquela release de base (35 ações históricas; **40 ações ativas** após atualização dirigida de 04/11/2026), Scribus PDF/SLA e LMMS WAV reais, Ghidra/JADX/Valkey privados PASS, raiz física /srv/projects/skill-universal com alias Ferrari exclusivo.
- [Pedido inventário #41784949891](https://github.com/martaxi-boss/VPS/actions/runs/41784949891) FERRARI_SKILL_END_TO_END=PASS, ZIP confirmado: 81 programas detetados em catálogos, 55/56 selecionados Ubuntu, 34 ações externas no instante dessa consulta (antes do LMMS). A instalação operacional atual tem **40 ações** (36 existentes + 4 Android), validadas pelo inventário real [#41854771565](https://github.com/martaxi-boss/VPS/actions/runs/41854771565). São deteções e ações, não 81 operações certificadas.
- O REA original do Ferrari, rea-agents@6.8.0, reside fisicamente em **/srv/projects/skill-universal/.runtime/npm/rea**, acessível também pelo alias /home/ubuntu/.local/share/motor-ferrari/.runtime/npm/rea. Node 22.23.4, Java 25.0.5, Ghidra 12.2 (programa independente), Ghidra 12.1.4 (fornecedor REA), JADX 1.5.6 (CLI), JADX headless MCP 0.7.1 (fornecedor REA) e Apktool **3.0.3** são privados do Ferrari. ELF e recursos Android passaram em [#41654437939](https://github.com/martaxi-boss/VPS/actions/runs/41654437939) e ELF via Skill em [#41655035184](https://github.com/martaxi-boss/VPS/actions/runs/41655035184).
- **Fase 2 5/5 certificada:** Calibre EPUB, Darktable TIFF, Krita PNG, GIMP XCF e Scribus PDF+SLA; Skill Scribus [#41785658074](https://github.com/martaxi-boss/VPS/actions/runs/41785658074). **Fase 3 iniciada:** LMMS `.mmp/.mmpz` → WAV PCM estéreo real e não silencioso [Skill #41787031335](https://github.com/martaxi-boss/VPS/actions/runs/41787031335). `melt` CLI foi detetado, mas vídeo ainda não está certificado. Aplicações gráficas APT não equivalem a controlo interativo. ComfyUI CPU não tem modelos e inferência certificada; Penpot não está a correr, falta Docker. Outros programas detetados continuam installed_unintegrated.
- [Comparação MCP #41708905353](https://github.com/martaxi-boss/VPS/actions/runs/41708905353): 229 nomes de ferramentas em ambos os REAs, zero em falta, PASS. [Teste profundo #41710014556](https://github.com/martaxi-boss/VPS/actions/runs/41710014556): análise ELF com Ghidra e classe Android com JADX headless MCP, PASS.
- [Skill→REA MCP catálogo #41713808747](https://github.com/martaxi-boss/VPS/actions/runs/41713808747) PASS, [tools/call ELF #41717389118](https://github.com/martaxi-boss/VPS/actions/runs/41717389118) PASS e [tools/call Apktool #41717684160](https://github.com/martaxi-boss/VPS/actions/runs/41717684160) PASS, incluindo `response.zip`, `report.json` e resultados estruturados. **A paridade de 229 nomes NÃO prova as 229 operações.**
- **REA FINAL e REA Trial antigos:** removidos da VPS e ausência validada [#41840478411](https://github.com/martaxi-boss/VPS/actions/runs/41840478411). O REA original privado do Ferrari permanece instalado e independente; nunca o eliminar.
- **Ferrari Android CLI privado (Ubuntu Linux x86_64):** AAPT2 (manifesto compilado), Apksigner (assinatura/certificado), Zipalign (alinhamento) e ADB (instalação no dispositivo quando autorizado) são ações de `engine/tool_actions.json`, com executáveis exclusivamente em `/srv/projects/skill-universal/tools/android-cli-36.0.0/` e dados em `.runtime/android-cli/`. Não recorrer a `/opt/android-sdk`, instalações globais, emuladores ou imagens Android; instalação e testes reais PASS: criação de APK sintética, análise AAPT2, alinhamento Zipalign e assinatura/apksigner [#41854398886](https://github.com/martaxi-boss/VPS/actions/runs/41854398886); ADB CLI/version em Linux, mas **sem teste com dispositivo físico**. Tamanho físico das novas ferramentas: **19 050 496 bytes**, inventário [#41854771565](https://github.com/martaxi-boss/VPS/actions/runs/41854771565). Skill GitHub→VPS→ZIP em linguagem natural por `kind=auto` PASS [#41856969562](https://github.com/martaxi-boss/VPS/actions/runs/41856969562). O Android SDK antigo ainda não foi desinstalado.

## Execução com a ponte GitHub existente

1. Compreender resultado, entradas e formato. Consultar references/protocols.md e, para DAGs, references/orchestration.md.
2. Usar o conector GitHub autenticado para ler martaxi-boss/skill-universal e, se houver autorização de escrita, criar um pedido na main de martaxi-boss/VPS. Não presumir SSH local.
3. Ler references/github-bridge.md **antes de qualquer pedido à VPS**. Criar um único JSON novo por chamada em ferrari-requests/job-<identificador-unico>.json; nunca alterar ou reciclar um pedido anterior. Sem segredos ou dados privados no repo público.
4. Tipos: kind=inventory devolve inventário; kind=operation executa uma operação base; kind=invoke uma ação em engine/tool_actions.json (a ponte GitHub ainda valida este tipo contra um catálogo pinado antigo: **não usar `kind=invoke` com as quatro ações Android novas até atualizar de forma autorizada o pin**); kind=auto seleciona um adaptador e já está certificado para Zipalign; kind=plan envia etapas validadas pelo orquestrador já existente; kind=rea-mcp permite chamar o servidor MCP original privado do Ferrari pelo nome das ferramentas, usando tools/list ou tools/call e, se necessário, a referência $input ao ficheiro de entrada. **tools/list e tools/call de ELF/Apktool já foram certificados; testar outros fornecedores/funções conforme o uso real.** Não aceitar texto livre como shell.
5. Verificar commit, run GitHub Actions correspondente, FERRARI_SKILL_JOB_STATUS=completed, FERRARI_SKILL_END_TO_END=PASS, response.zip, report.json e artefactos reais. Se falhar, comunicar erro e não inventar resultados.
6. Para capacidade ausente, avaliar licenças, Ubuntu, CPU/RAM/SSD, versões, dependências e interfaces; integrar **no Ferrari existente** e testar, sem Skill/ponte/camada nova.

As operações base e ações externas reais estão definidas em engine/ferrari.py e engine/tool_actions.json, não neste texto. Distinguir catálogo, binário instalado, adaptador, teste funcional e entrega ao utilizador.

## Higiene, segurança e expansão

- A limpeza de releases Ferrari em install/ferrari-hygiene.py é limitada a essa árvore e preserva ativo/fallback. Não tocar em sistemas ou outros projetos, nem eliminar o REA anterior automaticamente.
- Java/Node/npm/Apktool/REA usados nas ações Ferrari devem apontar a diretórios próprios; programas globais Ubuntu podem ser partilhados e precisam de análise de proveniência antes de remoções.
- Não prometer GPU, modelos locais, API paga gratuita, aplicações GUI headless nem fornecedores do REA ainda não testados.
- Não copiar Skills de terceiros indiscriminadamente. Reutilizar apenas padrões e código licenciado e auditado.
- Fontes: references/github-bridge.md, references/bootstrap.md, references/orchestration.md, references/protocols.md e references/workflows.md; CI e testes no GitHub prevalecem sobre declarações antigas.

**A implantação de uma Skill atualizada na interface ChatGPT exige verificação própria; o facto de o repositório estar atualizado não prova a versão instalada no cliente.**
