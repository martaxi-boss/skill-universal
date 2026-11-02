## Ponte Ferrari Skill ↔ VPS — certificada em 02/11/2026

Execução #41546722719: 68 testes na VPS PASS; #41546901101 SVG em ZIP PASS; #41547060999 Markdown→DOCX via Pandoc automaticamente em ZIP PASS. A Skill pode solicitar via conector GitHub um ficheiro novo `martaxi-boss/VPS/ferrari-requests/job-*.json`, com `version=1`, `id`, `kind=operation|auto|invoke|inventory` e campos adequados. Workflow Ferrari exclusivo encaminha e recolhe ZIP de resultados (sem alterar ponte SSH existente). **Os pedidos GitHub são públicos**. Usar apenas dados não sensíveis; ligar GitHub e instalar a Skill atualizada para a utilizar no cliente.

# Última prova: catálogo operacional na VPS

Execução GitHub Actions VPS [#41545170664](https://github.com/martaxi-boss/VPS/actions/runs/41545170664) SUCCESS. 59 testes PASS, 12 ações instaladas, 45 programas detetados nos catálogos combinados. O comando `auto` selecionou e executou Pandoc a partir de pedido em linguagem natural para DOCX real. Ferramentas de catálogo sem adaptador não são automaticamente executáveis. Consultar BOOTSTRAP canónico no repositório para estado e limitações.

# Atualização: catálogo operacional multidomínio do Ferrari

O catálogo tem 56 candidatos Ubuntu. Em separado, `engine/tool_runtime.py` deteta a presença efetiva dos executáveis na VPS e consulta `engine/tool_actions.json`, que contém 12 ações tipadas nas áreas documentos, diagramas, multimédia, imagens, dados, identificação de ficheiros e engenharia reversa. Os comandos Ferrari são `tools`, `actions`, `route` e `invoke`. A seleção não é certificação: só declarar PASS depois de testes reais no Ubuntu, com outputs. REA/Ruflo não são o centro do Ferrari e a sua integração profunda continua pendente.

A invocação tipada também é aceite pelo orquestrador em `operation=tool`, especificando `tool`, `action`, `input`. Nenhum pedido livre é executado como shell. A ligação direta Skill→VPS exige um transporte autenticado, ainda por confirmar.

---

# Bootstrap permanente — Motor Ferrari Ubuntu

Documento canónico no repositório: [BOOTSTRAP.md](https://github.com/martaxi-boss/skill-universal/blob/main/BOOTSTRAP.md). Este resumo também acompanha o ZIP da única Skill, para que a visão permaneça disponível mesmo fora do checkout GitHub.

## Compromisso de arquitetura

**Uma Skill universal** (ChatGPT, Codex ou outra IA) → ligação autorizada → **um Motor Ferrari isolado em VPS Ubuntu** → **orquestrador próprio** → programas livres Linux instalados, com fornecedores e dependências verificadas → artefactos e logs. Não reutilizar serviços ou coordenadores de outros projetos.

**Objetivo de cobertura:** desenvolvimento web e aplicações, jogos, criação de imagens, vídeo, áudio, documentos e PDFs, automação, dados, engenharia reversa autorizada, **desenho técnico, projetos de construção, arquitetura, plantas 2D, CAD, BIM/IFC, modelação e renderização 3D**, entre outras áreas. Cada nova capacidade alarga o Ferrari: nunca criar uma Skill adicional.

## Estado real registado em 2026-11-02

- 125 candidatos GitHub pesquisados; 56 pré-selecionados para Ubuntu.
- 34 pacotes APT identificados numa runner Ubuntu 24.04; 22 candidatos exigem instalação Linux externa; **nenhum desses números prova instalação na VPS**.
- Dez operações tipadas no motor (as últimas três exigem prova real de instalação CAD/Office na VPS): website HTML, cartaz SVG, PDF para texto, redimensionar imagem, miniatura de vídeo, descompilação de APK, strings binárias, STL via OpenSCAD, casa conceptual 3D via Blender, DOCX/ODT/PPTX/XLSX para PDF via LibreOffice.
- Orquestrador DAG com pré-visualização, série/paralelo e relatórios, sem recuperação persistente.
- Skill e MCP preparados, mas **não existe evidência de ligação ponta a ponta à VPS nem de ferramentas certificadas nela**.
- Projetos de construção, BIM/IFC, CAD e modelação/renderização 3D profissionais **ainda não têm adaptadores completos certificados**.

## Regras inegociáveis de continuidade

1. Não dizer que a Skill faz tudo nem que programas estão disponíveis só por constarem no catálogo.
2. Escolher ferramenta Ubuntu livre e profissional: licença, manutenção, release e fornecedor legítimo, arquitetura, dependências, RAM/disco/CPU/GPU, teste e adapter próprio.
3. Respeitar as fases: descoberto → filtrado para Ubuntu → dependências confirmadas → instalado na VPS → testado funcionalmente → adaptador integrado → disponível pela Skill.
4. Não importar automaticamente pacotes GitHub de Skills; avaliar código/licença e aproveitar apenas padrões úteis na mesma Skill.
5. Não tocar noutros repositórios/projetos, nem misturar instalações. Não instalar versões pirateadas como alternativas gratuitas.
6. Não alterar a VPS durante pesquisa. O workflow tem fases manuais `PRECHECK`, `DEPLOY`, `INSTALL_HEADLESS` e precisa de SSH real.
7. Antes de avançar, consultar sempre o BOOTSTRAP canónico, o `engine/ubuntu_selection.json`, as sete operações de `engine/ferrari.py`, os testes e os logs da VPS; atualizar o estado apenas com provas.

**Objetivo final:** um motor suficientemente extensível para executar uma grande variedade de pedidos, com resultados profissionais verificáveis, mas sem promessas mágicas ou certificação falsa.
