---
name: motor-universal-linux
description: Skill única para comandar o Motor Ferrari Ubuntu independente. Usar em tarefas de websites e layouts, programação, engenharia reversa autorizada, imagens, criativos, vídeo, áudio, documentos, dados, automação e orquestração profissional de fluxos Ubuntu; a IA anfitriã apenas interpreta e organiza, e as ferramentas são as do motor Linux.
---

# Motor Ferrari — Skill Universal

## Estado certificado na VPS

A execução GitHub Actions VPS [#41545170664](https://github.com/martaxi-boss/VPS/actions/runs/41545170664) terminou SUCCESS com 59 testes na VPS, 12 adaptadores disponíveis e execução automática Markdown→DOCX via Pandoc. Inventário real de 45 programas nos catálogos combinados: NÃO interpretar como 45 dos 56 candidatos nem como 45 ações. A ponte Skill→VPS e o funcionamento real profundo de REA/Ruflo permanecem por demonstrar.

## Bootstrap permanente do projeto

**Ler primeiro** o ficheiro canónico `BOOTSTRAP.md` deste repositório; se estiver a utilizar apenas o ZIP da Skill, ler `references/bootstrap.md`. Esta decisão prevalece sobre ideias vagas de expansão: **uma só Skill, um só Motor Ferrari isolado em Ubuntu, um orquestrador próprio e ferramentas instaladas/testadas antes de serem anunciadas como disponíveis**. O objetivo é cobrir todas as áreas possíveis progressivamente, incluindo **projetos de construção, plantas 2D, arquitetura, BIM/IFC e modelação 3D**, mas hoje **não está tudo implementado**. Nunca confundir os 56 candidatos Ubuntu com ferramentas certificadas na VPS.


A inteligência artificial (ChatGPT, Codex, Cloud, ou outra) apenas interpreta e organiza pedidos. As ferramentas e execução pertencem ao Motor Ferrari independente instalado no Ubuntu. Não reutilizar outros repositórios nem programas proprietários dos anfitriões.

## Operação

1. Compreender a tarefa, os ficheiros de entrada e o resultado pedido.
2. Verificar a ligação autenticada ao motor (CLI, MCP do projeto ou workflow autorizado). A Skill não proporciona acesso SSH automaticamente.
3. Pedir ao motor o diagnóstico e o plano: `python3 -m engine.ferrari doctor` e `python3 -m engine.ferrari plan 'pedido'`. Ler `engine/ferrari_registry.json`, `engine/ferrari_expansion.json` e `engine/catalog.json`; os dois registos novos totalizam 125 candidatos GitHub.
4. **Filtragem obrigatória:** ler `engine/ubuntu_selection.json` e usar apenas os projetos selecionados. Os 125 itens de `engine/ferrari_registry.json` + `engine/ferrari_expansion.json` são inventário de investigação, **não** autorização para instalar. Exigir prova oficial de Linux e, antes da VPS, prova de pacote Ubuntu 24.04 ou instalação Linux oficial. Cada fornecedor requer licença livre confirmada, versões e recursos compatíveis.
5. Escolher ferramentas Ubuntu gratuitas e realmente instaladas. Confirmar formato, dependências, licença e recursos; não presumir acesso grátis ilimitado a APIs.
6. **Inventário real e ações dinâmicas:** consultar `python3 -m engine.ferrari tools` e `python3 -m engine.ferrari actions` na VPS para distinguir 56 candidatos, executores realmente encontrados e ações que já têm adaptador. Para escolher por pedido e formato: `python3 -m engine.ferrari route 'pedido' --input /ficheiro` (pré-visualização); para selecionar e executar uma única ação com correspondência clara: `python3 -m engine.ferrari auto 'pedido' --input /ficheiro --output /pasta --execute` (sem `--execute`, apenas pré-visualização; empates não executam); para executar uma ação escolhida manualmente: `python3 -m engine.ferrari invoke --action pandoc-md-docx --input /ficheiro.md --output /pasta`. Para trabalhos compostos o orquestrador aceita passos `{"operation":"tool","tool":"pandoc","action":"pandoc-md-docx","input":"/ficheiro.md"}`; adaptações ficam em `engine/tool_actions.json`, sem alterar o orquestrador para cada nova ação. Não confundir binário detetado com ação executável; não anunciar capacidades sem teste real na VPS.
7. Usar apenas os executores locais realmente disponíveis: web-template, svg-poster, pdf-text, image-resize, video-thumbnail, apk-decompile, binary-strings; a partir da entrega de novembro também **cad-stl** (OpenSCAD), **blender-house** (modelo conceptual 3D com ficheiros BLEND/GLB/PNG) e **office-pdf** (LibreOffice). Antes de declarar as três últimas utilizáveis na VPS, exigir o log real do workflow CAD/3D com PASS. O modelo da casa não substitui um projeto de engenharia. Nunca executar texto livre do pedido como shell.
8. Se faltar ferramenta livre ou fornecedor, consultar `ferrari_alternatives` para um produto comercial conhecido e `ferrari_discover` para procurar alternativas licenciadas no GitHub. Avaliar licença, Linux/Ubuntu, arquitetura, dependências, RAM, GPU, manutenção e risco antes de instalar; NUNCA executar o código de um repositório encontrado apenas porque tem muitas estrelas. Implementar e testar o adaptador neste projeto; dizer o que falta.
9. Em websites, escolher automaticamente o layout adequado: landing, store (loja), portfolio (portefólio) ou dashboard (painel). O comando Ferrari aceita --layout com estes valores. São templates estáticos sem backend, pagamentos ou autenticação reais.
10. Devolver ficheiros, testes, evidência do executor real e lacunas. Não declarar 100% com base em catálogo ou simulação.

## Orquestrador profissional (obrigatório para tarefas compostas)

Usar **o coordenador independente do Motor Ferrari**, nunca o coordenador do ChatGPT/Codex ou de projetos antigos. Para tarefas com vários passos:

1. Preparar o plano JSON `{"version":1,"steps":[...]}` com `id`, `operation`, `depends_on`, `input_from`, `title` e `layout` quando aplicável. Cada operação tem de estar implementada em `engine.ferrari.OPS`.
2. Validar com `engine.orchestrator.validate_workflow` e apresentar a simulação: `python3 -m engine.orchestrator --plan examples/ferrari-workflow.json --workspace /caminho/trabalho`. Sem `--execute` o comando não escreve ficheiros.
3. Executar mediante autorização usando `--execute --max-parallel 2` ou a ferramenta MCP `ferrari_orchestrate` com `execute=true`. A execução depende da ponte autenticada e da instalação real no Ubuntu.
4. O motor gere dependências, paralelismo e resultados de cada etapa, devolvendo `report.json` e os artefactos. **Não afirmar recuperação após reinício ou retries automáticos**: ainda não foram implementados.
5. Prefect (Apache-2.0) é candidato para persistência e agendamento local, Ruflo (MIT) para coordenação de agentes especializados, LangGraph (MIT) para estados agentivos. Todos são módulos **opcionais**, apenas se verdadeiramente instalados e certificados. Nenhum substitui o núcleo Ferrari.

## Coleções GitHub de Skills

Usar uma **Skill única** com referências internas, não instalar em série Skills de outros autores. A auditoria `engine/skillpacks_audit.json` verifica coleções como Superpowers (MIT), wshobson/agents (MIT), Vercel Skills (MIT), Agent Skills (Apache-2.0), Anthropic Skills (licença por pasta) e OpenAI Skills (descontinuado). Selecionar metodologias reutilizáveis, atribuir origens e nunca importar automaticamente scripts, hooks, prompts de fornecedor pago ou módulos com licenças proprietárias.

Consultar `references/protocols.md` para escolher ferramentas por domínio e respetivos testes. Consultar `references/orchestration.md` para escolher fluxos, integrar conhecimento sem múltiplas Skills e executar o coordenador. A documentação completa está em `docs/ORQUESTRADOR_SKILLS_GITHUB.md`.

## Domínios

Web: Next.js, Astro, Vite, Tailwind, shadcn/ui, Playwright; engenharia reversa: REA independente, Ghidra, JADX, Apktool, Rizin, radare2, Binwalk; criativos: GIMP, Krita, Inkscape, Blender, Scribus, ImageMagick; vídeo: FFmpeg, Kdenlive; documentos: LibreOffice, Pandoc, Tesseract, OCRmyPDF, Typst; motores opcionais: Ruflo, LangGraph, ComfyUI, Ollama conforme recursos do Ubuntu.

Engenharia reversa legítima de compatibilidade é possível, mas não transforma software pago num fornecedor livre. Não obter ou distribuir cracks, cópias adulteradas ou contornos de licenças comerciais; escolher implementações abertas independentes. Exemplo: Photoshop -> GIMP/Krita; Illustrator -> Inkscape/Penpot; Premiere -> Kdenlive/FFmpeg; Acrobat -> LibreOffice/OCRmyPDF.

Comandos opcionais do motor: `python3 -m engine.ferrari discover 'linux open source CAD' --min-stars 100`, `python3 -m engine.ferrari alternatives 'Adobe Creative Cloud'`.  Nenhuma procura instala binários ou concede acesso à VPS.

Documentação e critérios de certificação: docs/FERRARI.md no repositório do motor e references/workflows.md neste pacote Skill.

## Política de qualidade e implantação

- Uma Skill pessoal, com seleção por tipo de tarefa; não exigir outra Skill nem ferramentas proprietárias dos anfitriões.
- Não recomendar repositórios arquivados, binários não verificados, licenças duvidosas ou sistemas sem prova de execução Linux. As estrelas são critério secundário.
- Para REA, exigir Node.js na gama documentada; Ghidra atual exige JDK 25, não confundir com JDK 21 do Ubuntu.
- Distinguir ferramentas CLI/headless, aplicações que exigem interface gráfica, motores que requerem GPU ou grandes pesos, e fornecedores cloud sujeitos a quotas. Nunca fingir GPU ou API grátis ilimitada.
- Instalação APT, AppImage, npm, Python venv ou contentores só após diagnóstico do Ubuntu real, validação de versão, hash/release/licença e teste funcional; não tocar na VPS durante a filtragem.
- Em caso de solução comercial paga: procurar alternativas livres e implementações independentes compatíveis. Não aceitar cracks ou licenças contornadas como fornecedores gratuitos.
- Referência: `docs/SELECAO_UBUNTU.md`; os níveis são catálogo -> Ubuntu documentado -> pacote detectado -> instalado -> teste real -> utilização confirmada via Skill.
