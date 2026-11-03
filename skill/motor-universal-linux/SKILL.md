---
name: motor-universal-linux
description: Skill única de controlo do Motor Ferrari Ubuntu. Para pedidos de criação, programação, web, imagens, vídeo, áudio, PDF, CAD/BIM/3D, dados, engenharia reversa autorizada e automação, usando GitHub autenticado e os executores Ferrari reais na VPS.
---

# Motor Ferrari — Skill Universal

## Identidade e fonte de verdade

**UMA ÚNICA SKILL UNIVERSAL Ferrari; um motor e orquestrador próprios na VPS.** A IA anfitriã interpreta e orienta; o motor seleciona e executa ferramentas. Nunca substituir por Project Leader, pelo REA antigo, Ruflo ou outro coordenador. Não adicionar lógica à ponte SSH.

Ler [BOOTSTRAP canónico](https://github.com/martaxi-boss/skill-universal/blob/main/BOOTSTRAP.md) para o estado atual, instalações e pendências. Se só houver o pacote ZIP, ler references/bootstrap.md; a fonte GitHub prevalece sempre que acessível.

## Estado de referência — 03/11/2026

- Release VPS: 6c93a392dfe9a02d7ccfef9d47317c9685976484. [Deploy #41671631900](https://github.com/martaxi-boss/VPS/actions/runs/41671631900) SUCCESS, 139 testes PASS.
- [Pedido inventário #41672372249](https://github.com/martaxi-boss/VPS/actions/runs/41672372249) FERRARI_SKILL_END_TO_END=PASS, ZIP confirmado: 81 programas detetados em catálogos, 55/56 selecionados Ubuntu, 25 ações externas. São deteções, não 81 operações certificadas.
- O REA original do Ferrari, rea-agents@6.8.0, reside em /home/ubuntu/.local/share/motor-ferrari/.runtime/npm/rea. Node 22.23.4, Java 25.0.5, Ghidra 12.2, JADX 1.5.6 e Apktool **3.0.3** são privados do Ferrari. ELF e recursos Android passaram em [#41654437939](https://github.com/martaxi-boss/VPS/actions/runs/41654437939) e ELF via Skill em [#41655035184](https://github.com/martaxi-boss/VPS/actions/runs/41655035184).
- 15 aplicações gráficas instaladas por APT não equivalem a controlo interativo. ComfyUI CPU não tem modelos e inferência certificada; Penpot não está a correr, falta Docker. Outros programas detetados podem continuar installed_unintegrated.
- **Não desinstalar o projeto REA antigo:** ainda faltam auditoria de dependências globais, teste sem acesso ao legado e plano de recuperação. Nunca remover a pasta REA privada do Ferrari.

## Execução com a ponte GitHub existente

1. Compreender resultado, entradas e formato. Consultar references/protocols.md e, para DAGs, references/orchestration.md.
2. Usar o conector GitHub autenticado para ler martaxi-boss/skill-universal e, se houver autorização de escrita, criar um pedido na main de martaxi-boss/VPS. Não presumir SSH local.
3. Ler references/github-bridge.md **antes de qualquer pedido à VPS**. Criar um único JSON novo por chamada em ferrari-requests/job-<identificador-unico>.json; nunca alterar ou reciclar um pedido anterior. Sem segredos ou dados privados no repo público.
4. Tipos: kind=inventory devolve inventário; kind=operation executa uma operação base; kind=invoke uma ação em engine/tool_actions.json; kind=auto seleciona um adaptador; kind=plan envia etapas validadas pelo orquestrador já existente. Não aceitar texto livre como shell.
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
