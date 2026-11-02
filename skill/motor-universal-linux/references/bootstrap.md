# Bootstrap permanente — Motor Ferrari Ubuntu

Documento canónico no repositório: [BOOTSTRAP.md](https://github.com/martaxi-boss/skill-universal/blob/main/BOOTSTRAP.md). Este resumo também acompanha o ZIP da única Skill, para que a visão permaneça disponível mesmo fora do checkout GitHub.

## Compromisso de arquitetura

**Uma Skill universal** (ChatGPT, Codex ou outra IA) → ligação autorizada → **um Motor Ferrari isolado em VPS Ubuntu** → **orquestrador próprio** → programas livres Linux instalados, com fornecedores e dependências verificadas → artefactos e logs. Não reutilizar serviços ou coordenadores de outros projetos.

**Objetivo de cobertura:** desenvolvimento web e aplicações, jogos, criação de imagens, vídeo, áudio, documentos e PDFs, automação, dados, engenharia reversa autorizada, **desenho técnico, projetos de construção, arquitetura, plantas 2D, CAD, BIM/IFC, modelação e renderização 3D**, entre outras áreas. Cada nova capacidade alarga o Ferrari: nunca criar uma Skill adicional.

## Estado real registado em 2026-11-02

- 125 candidatos GitHub pesquisados; 56 pré-selecionados para Ubuntu.
- 34 pacotes APT identificados numa runner Ubuntu 24.04; 22 candidatos exigem instalação Linux externa; **nenhum desses números prova instalação na VPS**.
- Sete operações tipadas no motor: website HTML, cartaz SVG, PDF para texto, redimensionar imagem, miniatura de vídeo, descompilação de APK, strings binárias.
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
