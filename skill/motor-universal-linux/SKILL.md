---
name: motor-universal-linux
description: Skill única para comandar o Motor Ferrari Ubuntu independente. Usar em tarefas de websites e layouts, programação, engenharia reversa autorizada, imagens, criativos, vídeo, áudio, documentos, dados, automação e orquestração profissional de fluxos Ubuntu; a IA anfitriã apenas interpreta e organiza, e as ferramentas são as do motor Linux.
---

# Motor Ferrari — Skill Universal

## Ligacao OCRmyPDF proposta — 03/11/2026 (certificacao ainda em curso)

O programa `ocrmypdf` ja estava instalado na VPS Ubuntu, mas o inventario da Skill [#41622654033](https://github.com/martaxi-boss/VPS/actions/runs/41622654033) detetou-o como `installed_unintegrated`. Esta alteracao **nao instala outro programa**: acrescenta a acao `ocrmypdf-searchable-pdf` ao manifesto do mesmo Ferrari para converter **PDFs digitalizados** em PDFs pesquisaveis. A entrada remota e um PDF nao confidencial com `kind=invoke`, `action=ocrmypdf-searchable-pdf` e `input` em base64. A acao deve ser anunciada como funcional apenas depois de CI, deploy e teste real da VPS com texto extraido do PDF resultante. Nao cria Skill adicional nem altera SSH ou Supervisor.


## Atualização de certificação externa — 03/11/2026

O teste real de staging da Lowcost Europa, **feito pelo workflow do próprio projeto** e não pelo motor Ferrari, passou depois de corrigir apenas `runs-on: ubuntu-24.04` na [PR #186](https://github.com/martaxi-boss/lowcost-europa/pull/186). [Staging pós-merge #41605911458](https://github.com/martaxi-boss/lowcost-europa/actions/runs/41605911458): ZIP/JSON verificados, **15 checks PASS, 0 errors, 0 warnings**, 14 PNG desktop/mobile; [Django/PostgreSQL #41605911466](https://github.com/martaxi-boss/lowcost-europa/actions/runs/41605911466): **709 testes PASS**, [audit #41605911500](https://github.com/martaxi-boss/lowcost-europa/actions/runs/41605911500) SUCCESS. Fonte: [BOOTSTRAP](https://github.com/martaxi-boss/skill-universal/blob/main/BOOTSTRAP.md). Não confundir prova de staging/CI com operação `vite-build` do Ferrari nem com certificação da produção. Ferrari VPS e ponte SSH inalterados.

## Histórico — situação comprovada do Ferrari em 03/11/2026

**Ferrari VPS:** versão ativa `ec4dc5045a034e3fbbbcfe3477e1641e80714262`. [Instalação real #41601238265](https://github.com/martaxi-boss/VPS/actions/runs/41601238265) SUCCESS com **99 testes PASS**, browser Chromium, teclado, mobile e IFC. Um caso fora do exemplo inicial usou o **JS e CSS originais do catálogo do projeto Lowcost Europa** (`martaxi-boss/lowcost-europa`, main `388860c6...`) sem alterar esse repositório. [Pedido pela Skill #41601466546](https://github.com/martaxi-boss/VPS/actions/runs/41601466546) SUCCESS; ZIP validado com relatório `status=completed`, 17 verificações reais de frontend PASS, capturas desktop/móvel, zero erros e pedidos externos. `Tab`, `Shift+Tab`, botão real «Limpar filtros» por Enter e Space PASS, `interactions.findings=[]`. Os 17 checks são sobre dados de teste estáticos, não sobre uma execução Django/produção.

**Correção com causa identificada:** [PR #10](https://github.com/martaxi-boss/skill-universal/pull/10) evita falso aviso de Space quando o próprio botão foca o campo de pesquisa após Enter. A mesma operação `vite-build` e o mesmo Chromium `156.0.8078.4` foram mantidos; testes de teclado com ativação apenas de controlos `data-ferrari-test`. O motor não deve declarar links, formulários ou outros botões `passed` quando não foram pedidos; a resposta usa `not_requested`.

**Inventário:** 56 candidatos Ubuntu, **23/56 detetados**, 49 programas nos catálogos combinados, **12 operações base**, 21 ações externas; Vite `8.3.5`, Playwright `1.64.1`, Node isolado `22.23.4`; IfcOpenShell em testes IFC. Nem os controlos do Linux nem os programas externos se tornam todos certificados por estes testes de frontend.

**Higienização Ferrari:** release ativa `ec4dc5045...` e fallback certificado `9277a56b9...` preservados, release antiga `0196f37a...` apagada só dentro do Ferrari; **2 539 520 bytes libertados (~2,42 MiB)**, **21,31 GiB** livres; `outside_ferrari_touched=false`.

**Fontes de verdade:** [BOOTSTRAP canónico](https://github.com/martaxi-boss/skill-universal/blob/main/BOOTSTRAP.md) e [evidência de teste real Lowcost Europa](https://github.com/martaxi-boss/skill-universal/blob/main/docs/TESTE_REAL_LOWCOST_EUROPA_20261103.md). A Skill continua única e o transporte GitHub/SSH não mudou; fonte de projetos não confidencial apenas. O teste estático não valida Django, PostgreSQL, compras, staging/produção, nem certificação WCAG.

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
7. Utilizar as **12 operações base certificadas conforme evidência**, incluindo web-template, svg-poster, pdf-text, image-resize, video-thumbnail, apk-decompile, binary-strings, cad-stl, blender-house, office-pdf, **ifc-summary** (ficheiro `.ifc` → relatório de entidades) e **vite-build** (ZIP com `index.html` e `src/` → `dist/`). As duas últimas passaram testes reais na VPS e pela Skill em 03/11. Os executores mantêm âmbito limitado: IFC sem certificação geométrica/estrutural, Vite sem backend ou browser automatizado. As **21 ações externas** continuam separadas no manifesto. Nunca executar texto livre do pedido como shell.
8. Se faltar ferramenta livre ou fornecedor, consultar `ferrari_alternatives` para um produto comercial conhecido e `ferrari_discover` para procurar alternativas licenciadas no GitHub. Avaliar licença, Linux/Ubuntu, arquitetura, dependências, RAM, GPU, manutenção e risco antes de instalar; NUNCA executar o código de um repositório encontrado apenas porque tem muitas estrelas. Implementar e testar o adaptador neste projeto; dizer o que falta.
9. Em websites, escolher automaticamente o layout adequado: landing, store (loja), portfolio (portefólio) ou dashboard (painel). O comando Ferrari aceita --layout com estes valores. São templates estáticos sem backend, pagamentos ou autenticação reais.
10. Devolver ficheiros, testes, evidência do executor real e lacunas. Não declarar 100% com base em catálogo ou simulação.

## Estado real certificado da ponte

**GitHub Actions #41556114851 SUCCESS (87 testes na VPS)**; pedidos reais pela Skill: **IFC #41556384002 PASS**, **Vite #41556406846 PASS** e **inventário #41556541593 PASS**, todos com ZIP, relatórios e artefactos inspecionados. O transporte das operações implementadas está comprovado, não de qualquer pedido arbitrário nem de execução livre de um DAG. REA/Ruflo profundos e demais capacidades não testadas continuam pendentes. Exige conector GitHub autenticado; nunca enviar dados sensíveis em repositórios públicos.

## Ligação Skill → GitHub Actions → VPS (pedido remoto)

**Referência operativa:** ler primeiro `references/github-bridge.md` para formatos JSON exatos, limites atuais, estados e recolha do ZIP. O protocolo já foi testado nas execuções acima; não o confundir com suporte de todas as tarefas possíveis.

A ligação operacional da Skill usa o conector GitHub autenticado e a ponte **exclusiva Ferrari** `.github/workflows/ferrari-skill-request.yml` de `martaxi-boss/VPS`. Não alterar a ponte SSH já existente nem outros projetos. O GitHub Actions apenas transporta o pedido e recolhe o ZIP; `engine.skill_job` do Ferrari valida, escolhe ferramentas e executa na VPS. A prova end-to-end deve ser verificada no ID real da execução antes de declarar que está operacional.

1. Confirmar ligação GitHub com permissão de escrita em `martaxi-boss/VPS` e leitura em `martaxi-boss/skill-universal`. Não presumir que a Skill, por si, cria uma sessão SSH.
2. Para pedir trabalho, criar **um novo ficheiro** `ferrari-requests/job-<identificador-unico>.json` na branch `main` de `martaxi-boss/VPS` usando a operação autenticada `mcp__GitHub__create_file` (ferramenta de GitHub, nunca shell). Exemplo de conteúdo: `{"version":1,"id":"skill-demo-001","kind":"operation","operation":"svg-poster","title":"Cartaz de teste Ferrari"}`. Outros tipos: `kind=inventory`; `kind=auto` (texto `request` + `input` com `name` e `content_base64`); `kind=invoke` (campo `action` + `input`); `kind=operation` com `operation` já implementada. Após certificação e implantação da release desta fase, também `kind=plan` com o campo `plan` pode chamar diretamente o orquestrador Ferrari já existente, sem alterar a ponte. Os nomes das ações disponíveis são descobertos no motor.
3. **Cuidado: ambos os repositórios são públicos.** O conteúdo do novo ficheiro JSON fica público no histórico GitHub, incluindo dados codificados em base64. Nunca colocar chaves, segredos, dados pessoais, documentação privada ou ficheiros sensíveis neste transporte. Para esse tipo de pedido é preciso uma via privada antes de executar.
4. Consultar os GitHub Actions de `martaxi-boss/VPS` e identificar a execução `Ferrari Skill - authenticated request delivery` associada ao commit de criação do pedido. Confirmar os logs e `FERRARI_SKILL_END_TO_END=PASS`. Obter o artefacto `ferrari-skill-result-<run_id>` pelo conector `mcp__GitHub__fetch_workflow_run_artifacts` / `mcp__GitHub__download_workflow_artifact` e disponibilizar o ZIP ou o link da execução ao utilizador.
5. O ZIP contém `report.json` e ficheiros produzidos em `artifacts/`. Não declarar sucesso só porque o workflow arrancou; confirmar `status=completed` e artefactos existentes. Para um pedido novo, gerar sempre um caminho JSON novo, nunca modificar um pedido anterior. O transporte não altera os restantes projetos.

## Orquestrador profissional (obrigatório para tarefas compostas)

Usar **o coordenador independente do Motor Ferrari**, nunca o coordenador do ChatGPT/Codex ou de projetos antigos. Para tarefas com vários passos:

1. Preparar o plano JSON `{"version":1,"steps":[...]}` com `id`, `operation`, `depends_on`, `input_from`, `title` e `layout` quando aplicável. Cada operação base tem de estar implementada em `engine.ferrari.OPS`; passos `operation=tool` exigem `tool` e `action` do manifesto. **Na VPS atualmente certificada, o remoto só tem `kind=operation|invoke|auto|inventory`.** A nova fonte adiciona `kind=plan` ao mesmo `engine.skill_job` para chamar o orquestrador atual, com `plan` versionado, `max_parallel` de 1 a 4, dependências e entrada `$input` opcional. **Não declarar funcionamento remoto até a alteração passar CI, ser instalada e devolver um ZIP real**.
2. Validar com `engine.orchestrator.validate_workflow` e apresentar a simulação: `python3 -m engine.orchestrator --plan examples/ferrari-workflow.json --workspace /caminho/trabalho`. Sem `--execute` o comando não escreve ficheiros.
3. Executar mediante autorização usando `--execute --max-parallel 2` ou a ferramenta MCP `ferrari_orchestrate` com `execute=true`. O orquestrador já é real na VPS. O envio direto pela Skill exige a nova release `kind=plan` implantada; até haver prova remota de execução e retorno do ZIP, usar os tipos anteriores.
4. O motor gere dependências, paralelismo e resultados de cada etapa, devolvendo `report.json` e os artefactos. **Não afirmar recuperação após reinício ou retries automáticos**: ainda não foram implementados.
5. Prefect (Apache-2.0) é candidato para persistência e agendamento local, Ruflo (MIT) para coordenação de agentes especializados, LangGraph (MIT) para estados agentivos. Todos são módulos **opcionais**, apenas se verdadeiramente instalados e certificados. Nenhum substitui o núcleo Ferrari.

## Coleções GitHub de Skills

Usar uma **Skill única** com referências internas, não instalar em série Skills de outros autores. A auditoria `engine/skillpacks_audit.json` verifica coleções como Superpowers (MIT), wshobson/agents (MIT), Vercel Skills (MIT), Agent Skills (Apache-2.0), Anthropic Skills (licença por pasta) e OpenAI Skills (descontinuado). Selecionar metodologias reutilizáveis, atribuir origens e nunca importar automaticamente scripts, hooks, prompts de fornecedor pago ou módulos com licenças proprietárias.

Consultar `references/protocols.md` para escolher ferramentas por domínio e respetivos testes. Consultar `references/orchestration.md` para escolher fluxos, integrar conhecimento sem múltiplas Skills e executar o coordenador. A documentação completa está em `docs/ORQUESTRADOR_SKILLS_GITHUB.md`.

## Domínios

Web: Next.js, Astro, Vite, Tailwind, shadcn/ui, Playwright; engenharia reversa: REA independente, Ghidra, JADX, Apktool, Rizin, radare2, Binwalk; criativos: GIMP, Krita, Inkscape, Blender, Scribus, ImageMagick; vídeo: FFmpeg, Kdenlive; documentos: LibreOffice, Pandoc, Tesseract, OCRmyPDF, Typst; motores opcionais: Ruflo, LangGraph, ComfyUI, Ollama conforme recursos do Ubuntu.

Engenharia reversa legítima de compatibilidade é possível, mas não transforma software pago num fornecedor livre. Não obter ou distribuir cracks, cópias adulteradas ou contornos de licenças comerciais; escolher implementações abertas independentes. Exemplo: Photoshop -> GIMP/Krita; Illustrator -> Inkscape/Penpot; Premiere -> Kdenlive/FFmpeg; Acrobat -> LibreOffice/OCRmyPDF.

Comandos opcionais do motor: `python3 -m engine.ferrari discover 'linux open source CAD' --min-stars 100`, `python3 -m engine.ferrari alternatives 'Adobe Creative Cloud'`.  Nenhuma procura instala binários ou concede acesso à VPS.

Documentação e critérios de certificação: docs/FERRARI.md no repositório do motor, `references/workflows.md` e `references/github-bridge.md` neste pacote Skill.

## Política de qualidade e implantação

- Uma Skill pessoal, com seleção por tipo de tarefa; não exigir outra Skill nem ferramentas proprietárias dos anfitriões.
- Não recomendar repositórios arquivados, binários não verificados, licenças duvidosas ou sistemas sem prova de execução Linux. As estrelas são critério secundário.
- Para REA, exigir Node.js na gama documentada; Ghidra atual exige JDK 25, não confundir com JDK 21 do Ubuntu.
- Distinguir ferramentas CLI/headless, aplicações que exigem interface gráfica, motores que requerem GPU ou grandes pesos, e fornecedores cloud sujeitos a quotas. Nunca fingir GPU ou API grátis ilimitada.
- Instalação APT, AppImage, npm, Python venv ou contentores só após diagnóstico do Ubuntu real, validação de versão, hash/release/licença e teste funcional; não tocar na VPS durante a filtragem.
- Em caso de solução comercial paga: procurar alternativas livres e implementações independentes compatíveis. Não aceitar cracks ou licenças contornadas como fornecedores gratuitos.
- Referência: `docs/SELECAO_UBUNTU.md`; os níveis são catálogo -> Ubuntu documentado -> pacote detectado -> instalado -> teste real -> utilização confirmada via Skill.
