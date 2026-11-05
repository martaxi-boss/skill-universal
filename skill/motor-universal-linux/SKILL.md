---
name: motor-universal-linux
description: Skill única de controlo do Motor Ferrari Ubuntu. Para pedidos de criação, programação, web, imagens, vídeo, áudio, PDF, CAD/BIM/3D, dados, engenharia reversa autorizada e automação, usando GitHub autenticado e os executores Ferrari reais na VPS.
---

# Motor Ferrari — Skill Universal

## Identidade e fonte de verdade

**UMA ÚNICA SKILL UNIVERSAL Ferrari; um motor e orquestrador próprios na VPS.** A IA anfitriã interpreta e orienta; o motor seleciona e executa ferramentas. Nunca substituir por Project Leader, pelo REA antigo, Ruflo ou outro coordenador. Não adicionar lógica à ponte SSH.

Ler [BOOTSTRAP canónico](https://github.com/martaxi-boss/skill-universal/blob/main/BOOTSTRAP.md) para o estado atual, instalações e pendências. Se só houver o pacote ZIP, ler references/bootstrap.md; a fonte GitHub prevalece sempre que acessível.

## Estado operacional certificado — 05/11/2026

A fonte de verdade atual é o [BOOTSTRAP do repositório](https://github.com/martaxi-boss/skill-universal/blob/main/BOOTSTRAP.md). Não usar contagens históricas como estado presente. Exigir evidência de GitHub Actions, VPS e ficheiros reais antes de anunciar sucesso.

- **Release instalada e comprovada na VPS:** `87969badbde0a77c2c181bb9605357d51a4a30c0` em `/srv/projects/skill-universal/current`; fallback `62f862cdf9727842546a244a3e4ec19dd8bc82f4` preservado. [VPS #42030605124](https://github.com/martaxi-boss/VPS/actions/runs/42030605124) SUCCESS.
- **Ponto 2 — isolamento das 40 ações tipadas:** 40/40 executores de aplicação testados dentro de `/srv/projects/skill-universal/`, incluindo runtimes privados e fornecedores REA próprios, sem novos pacotes APT globais. [VPS #42030605124](https://github.com/martaxi-boss/VPS/actions/runs/42030605124). Isto não demonstra isolamento de todas as *operações base*.
- **Ponto 3 — capacidades funcionais por domínio:** [matriz e sete pedidos reais](https://github.com/martaxi-boss/skill-universal/blob/main/docs/CERTIFICACAO_FUNCIONAL_PONTO3_20261105.md), com `response.zip`, `report.json.status=completed` e ficheiros verificáveis. Web, documentos/PDF, dados, imagem, áudio/vídeo, CAD/IFC/3D e automação PASS nos casos sintéticos; REA/Android PASS apenas nas chamadas testadas.
- **Inventário novo pela Skill:** [#42034776491](https://github.com/martaxi-boss/VPS/actions/runs/42034776491), 40 ações registadas/invocáveis, 55/56 candidatos Ubuntu identificados (Penpot ausente), 83 programas detetados no inventário alargado. Deteção nunca é certificação funcional.
- **Limites ainda abertos:** `cad-stl` e `blender-house` usaram os executáveis do Ubuntu (`/usr/bin/openscad`, `/usr/bin/blender`) nos testes do ponto 3; ADB sem telemóvel físico; GUI interativa, modelos de ComfyUI, Penpot e funções comerciais do Hopper não estão certificados; 229 nomes MCP do REA não equivalem a 229 funções testadas. Não ocultar estas dependências nem instalar coisas globais para as contornar.
- **Motor privado e histórico (não confundir com versão ativa):** `rea-agents@6.8.0`, Apktool `3.0.3` e Hopper 6.6.1 demo estão documentados. O commit de código funcional histórico `b2869e334d9d68a0c988905e71ce0badec6ba359` e o teste anterior [VPS #41786521407](https://github.com/martaxi-boss/VPS/actions/runs/41786521407) não são a release atualmente ativa.
- **Ponte imutável sem autorização separada:** o validador do pedido na `martaxi-boss/VPS` está pinado em `292aeb7d10eecef8c3ca84760cd579e84e4b97f3`; o SSH existente não deve ser reconfigurado. A arquitetura usa a única Skill Ferrari e o seu orquestrador privado — nunca Project Leader, uma segunda Skill, ou um coordenador na VPS.
- **Entrega ao ChatGPT:** a CI `Motor Universal independent tests` publica o artefacto `ferrari-skill-installable`, que contém `skill.zip`. CI ou atualização do repositório não prova que a Skill instalada na interface ChatGPT já tenha sido substituída; validar essa etapa separadamente.

## Execução com a ponte GitHub existente

1. Compreender resultado, entradas e formato. Consultar references/protocols.md e, para DAGs, references/orchestration.md.
2. Usar o conector GitHub autenticado para ler martaxi-boss/skill-universal e, se houver autorização de escrita, criar um pedido na main de martaxi-boss/VPS. Não presumir SSH local.
3. Ler references/github-bridge.md **antes de qualquer pedido à VPS**. Criar um único JSON novo por chamada em ferrari-requests/job-<identificador-unico>.json; nunca alterar ou reciclar um pedido anterior. Sem segredos ou dados privados no repo público.
4. Tipos: kind=inventory devolve inventário; kind=operation executa uma operação base; kind=invoke uma ação em engine/tool_actions.json (a ponte GitHub ainda valida este tipo contra um catálogo pinado antigo: **não usar `kind=invoke` com as quatro ações Android novas até atualizar de forma autorizada o pin**); kind=auto seleciona um adaptador e já está certificado para Zipalign; kind=plan envia etapas validadas pelo orquestrador já existente; kind=rea-mcp permite chamar o servidor MCP original privado do Ferrari pelo nome das ferramentas, usando tools/list ou tools/call e, se necessário, a referência $input ao ficheiro de entrada. **tools/list e tools/call de ELF/Apktool já foram certificados; testar outros fornecedores/funções conforme o uso real.** Não aceitar texto livre como shell.
5. Verificar commit, run GitHub Actions correspondente, FERRARI_SKILL_JOB_STATUS=completed, FERRARI_SKILL_END_TO_END=PASS, response.zip, report.json e artefactos reais. Se falhar, comunicar erro e não inventar resultados.
6. Para capacidade ausente, avaliar licenças, Ubuntu, CPU/RAM/SSD, versões, dependências e interfaces; integrar **no Ferrari existente** e testar, sem Skill/ponte/camada nova.

As operações base e ações externas reais estão definidas em engine/ferrari.py e engine/tool_actions.json, não neste texto. Distinguir catálogo, binário instalado, adaptador, teste funcional e entrega ao utilizador.

## Independência física — regra obrigatória

Um projeto = uma pasta. Todas as aplicações, executáveis, fornecedores, dependências de aplicação, versões, caches e dados Ferrari devem residir em `/srv/projects/skill-universal/`. É proibido instalar aplicações globalmente para Ferrari, usar executáveis do `PATH`/`/usr/bin` ou reutilizar dependências dos outros projetos. Ferramenta privada em falta significa **bloqueio explícito**, nunca fallback silencioso. O kernel e as bibliotecas fundamentais do Ubuntu são infraestrutura do sistema operativo e não instalações de aplicação.

O ponto 3 provou que as operações base CAD/Blender usaram executáveis globais. Em 05/11, o utilizador apresentou a saída do instalador privado `FERRARI_PRIVATE_CAD_INSTALL=PASS`, com Blender 4.5.15 LTS. **O teste posterior confirmou STL, BLEND, GLB e PNG através dos caminhos privados, com ficheiros reais e assinaturas verificados na captura do utilizador de 05/11, às 14:50 (Lisboa). Isto é prova do teste manual, não do deploy de uma nova release nem de execução pela Skill.** O teste real separado está em `install/vps-private-cad-smoke.sh`: executa OpenSCAD→STL e Blender→BLEND/GLB/PNG **diretamente pelos caminhos privados**; todo o trabalho temporário é criado e apagado em `.runtime/` dentro do Ferrari. Exigir resultados desse script e uma release ativada que use os caminhos privados antes de declarar isolamento operacional completo. Para LibreOffice, o instalador privado de AppImage Standard (distribuição LibreItalia indicada pela The Document Foundation) encontra-se em `install/vps-private-office.sh`. Extrai e testa DOCX→PDF em `.runtime/`, sem instalar aplicações globalmente. **A instalação LibreOffice no servidor continua pendente até um resultado real de `FERRARI_PRIVATE_OFFICE_INSTALL=PASS`; a assinatura criptográfica da fonte não é verificada por este script.** A futura desinstalação inclui parar serviços próprios e retirar agendamentos, ligações e configurações exclusivas sem afetar os restantes projetos.

## Higiene, segurança e expansão

- A limpeza de releases Ferrari em install/ferrari-hygiene.py é limitada a essa árvore e preserva ativo/fallback. Não tocar em sistemas ou outros projetos, nem eliminar o REA Ferrari privado; os REAs legados já foram removidos após auditoria.
- Java/Node/npm/Apktool/REA e dependências de aplicação usadas pelo Ferrari devem apontar a diretórios próprios. As bibliotecas fundamentais do Ubuntu permanecem componentes do sistema operativo; não instalar dependências específicas do Ferrari fora da pasta do projeto nem remover pacotes globais sem auditoria de consumidores.
- Não prometer GPU, modelos locais, API paga gratuita, aplicações GUI headless nem fornecedores do REA ainda não testados.
- Não copiar Skills de terceiros indiscriminadamente. Reutilizar apenas padrões e código licenciado e auditado.
- Fontes: references/github-bridge.md, references/bootstrap.md, references/orchestration.md, references/protocols.md e references/workflows.md; CI e testes no GitHub prevalecem sobre declarações antigas.

**A implantação de uma Skill atualizada na interface ChatGPT exige verificação própria; o facto de o repositório estar atualizado não prova a versão instalada no cliente.**
