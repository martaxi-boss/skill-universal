# Auditoria ao funcionamento da Skill Universal Ferrari — 19/11/2026

## Veredito

**Operacional nos percursos ensaiados hoje; certificação integral de 100% do catálogo não demonstrada.** Não foi detetada uma avaria no transporte, inventário, execução jq por Ruflo ou compilação web ensaiados. Há limitações de cobertura e melhorias concretas de validação e evidência. Não se atribui uma percentagem artificial.

Auditoria realizada através da instalação original `motor-universal-linux`, do conector GitHub autenticado e da ponte existente GitHub Actions → VPS → response.zip. Os ZIP foram descarregados e abertos nesta conversa. Não houve implantação, atualização de dependências, limpeza de ficheiros da VPS ou alteração da ponte.

## Identidade, código e distribuição

- Metadados da instalação original `Plugin_b62aaa180b308191b124269fd0acbf9d`: versão **1.0.22**, release publicada `pluginrel_6af0f8dcf03081918c35bc2bbf7eb9ec`.
- Código principal auditado: `ec6c3f3479207d0fd721a46f544dc19c7797015d`.
- Validador da ponte fixado em `046126279a605d331b95683ece0a26d3c464d0eb`.
- A comparação Git entre esse pin e o HEAD não encontrou alterações nos módulos engine; as diferenças são documentação, pacote, CI e testes documentais.
- A ponte executa `current` na VPS. Os relatórios desta auditoria não incluem SHA da release executada nem alvo de rollback: a sua identidade exata não foi certificada novamente. O pin do validador não prova, por si só, o alvo de `current`.

## Provas reais de hoje

| Ensaio | Resultado e âmbito | Prova |
|---|---|---|
| Inventário | completed; ZIP íntegro; catálogo e inventário JSON lidos | [44625656145](https://github.com/martaxi-boss/VPS/actions/runs/44625656145) |
| Ruflo: criação | 2 papéis distintos, tarefa e permissões explícitas; revisão 0 | [44625843890](https://github.com/martaxi-boss/VPS/actions/runs/44625843890) |
| Ruflo: ferramenta | jq privado executado; JSON de 65 bytes conservou os três campos da entrada | [44626026023](https://github.com/martaxi-boss/VPS/actions/runs/44626026023) |
| Ruflo: revisão | Conteúdo e SHA-256 recalculados; papel revisor aprovou | [44626184277](https://github.com/martaxi-boss/VPS/actions/runs/44626184277) |
| Ruflo: fecho | completed, revisão 3, 1 chamada real e 1 revisão registada | [44626329164](https://github.com/martaxi-boss/VPS/actions/runs/44626329164) |
| Programas de suporte | 5/5 probes privados de arranque PASS: yt-dlp, QGIS, Godot, Prometheus e Valkey; não certifica funções completas | [44626411103](https://github.com/martaxi-boss/VPS/actions/runs/44626411103) |
| Web/Vite/Playwright | completed e quality_gate=passed; HTML, relatório e duas capturas reais inspecionados | [44626265139](https://github.com/martaxi-boss/VPS/actions/runs/44626265139) |

O JSON revisto contém exatamente `{"ok":true,"projeto":"Ferrari","data":"2026-11-19"}`. Hash dos bytes formatados: `9a4edd6e09c6b7b9524a6fb6742da28ac3ef9347fc07071e162878b04c84d189`.

A equipa Ruflo foi conduzida pela mesma IA anfitriã em rondas. Não foram usados modelos autónomos na VPS. Zero chamadas LLM por agente corresponde ao contrato existente, não a um defeito.

O inventário e as rondas Ruflo reportam `quality_gate=not_certified`; não foram apresentados como PASS desse gate. A revisão de conteúdo e hash é evidência separada. O ensaio web pediu aceitação explícita e obteve PASS.

## Inventário atual

| Medida | Resultado |
|---|---:|
| Programas catalogados | 173 |
| Programas detetados | 73 |
| Selecionados detetados | 55/55 |
| Ações registadas e disponíveis | 40/40 |
| Programas classificados callable | 51 |
| Funções selecionáveis | 280 |
| Funções REA sincronizadas | 220 |
| Entradas totais do catálogo | 458 |
| Runtimes privados com execução mínima PASS | 3/3 |

Python, Node e Java executaram os probes mínimos do inventário. Todos os caminhos de programas reportados apontam à pasta Ferrari. Isto não constitui auditoria completa de bibliotecas transitivas ou prova funcional de todas as ações.

Os 18 programas classificados `installed_unintegrated` incluem dependências, aplicações opcionais e integrações indiretas: yt-dlp, FreeCAD, Audacity, OBS, SolveSpace, Synfig, OpenShot, Ghidra, Ruflo, ComfyUI, Next.js, Tailwind, Bootstrap, Playwright, shadcn, Streamlit, Gradio e Prefect. Essa classificação não significa que estejam todos avariados: Ruflo e Playwright foram usados com sucesso nesta auditoria através de integrações indiretas. Alguns programas têm provas funcionais históricas específicas, sem ação direta no catálogo.

Os blocos `expansion` estão corretamente marcados como fotografia histórica, `live_revalidated=false`. Não se usaram antigas marcas INSTALLED_APT como prova de instalação atual.

## Web: o que foi efetivamente verificado

Página sintética, compilada na VPS; Chromium com viewport 1280×720 e depois 390×844. Capturas abertas e revistas: texto legível, sem cortes ou transbordo horizontal. Relatório sem erros de consola/página ou pedidos externos bloqueados; metadados de viewport presentes; destino do único link de âncora encontrado.

Não houve teste de site publicado, checkout, backend, geolocalização, dispositivo Android físico ou navegação comercial.

**Limitação reproduzida:** com apenas um elemento focável e sem controlos opt-in, o relatório devolveu `interactions.status=clear` e gate PASS, embora Tab/Shift+Tab tenham ficado `not_tested` e ativação de links/botões/formulários `not_requested`. PASS significa que os critérios atuais foram cumpridos; não comprova que todos os controlos foram acionados.

## Achados e prioridades

1. **QA funcional parcial — prioridade média.** Distinguir explicitamente testes aprovados, não executados e não aplicáveis; quando o pedido exigir interação, exigir evidência dos controlos relevantes. O atual gate web não garante isso só por estar verde.
2. **Validação antecipada incompleta — prioridade baixa.** O primeiro pedido web desta auditoria foi enviado por mim sem o ZIP de entrada exigido. O validador aceitou o envelope e só a execução na VPS devolveu `Missing input`. Corrigi a chamada com um ZIP sintético e o ensaio passou. Não é uma falha de compilação; a melhoria é rejeitar essa ausência antes de transportar o pedido.
3. **Fila GitHub não equivale a FIFO — atenção operacional.** O primeiro probe de programas de suporte ficou cancelado enquanto aguardava, quando chegou outro pedido ao mesmo grupo concurrency. A configuração conserva apenas um pending; `cancel-in-progress=false` não garante preservar todos os pendentes. Evitar enviar vários pedidos em espera e conferir sempre commit/run. O pedido cancelado não foi tratado como teste executado.
4. **Proveniência de execução — melhoria de auditabilidade.** Incluir em cada relatório SHA da release efetivamente executada e, num diagnóstico autorizado, os alvos current/rollback. Nesta auditoria não se inferiu essa informação a partir da documentação.
5. **Documentação longa com estados históricos misturados — prioridade baixa.** A fonte principal e a Skill têm blocos antigos com números/releases diferentes. Consolidar estado atual numa secção e remeter o histórico para relatórios datados reduz o risco de uma IA selecionar informação antiga.

## Regressões e limites do ambiente de teste

A [CI mais recente do HEAD](https://github.com/martaxi-boss/skill-universal/actions/runs/42530716941), de 08/11, passou: **559 testes, 3 ignorados**. Essa é evidência histórica da suíte no Ubuntu, não uma nova execução completa na VPS hoje.

Nesta conversa, o contentor é Debian 13, sem a instalação privada Ferrari. Uma tentativa da suíte completa teve 559 testes, 7 falhas, 22 erros e 4 ignorados; os resultados incluem bloqueios explícitos de SO, executores privados ausentes e espaço em disco insuficiente num teste de instalador. Não se classificaram esses resultados como falhas da VPS nem se alterou o sistema para os esconder.

Os subconjuntos locais de contrato efetivamente repetidos passaram: equipa Ruflo (11), anfitrião Ruflo (5), runtimes (6) e seleção de pedidos (3). Utilizam isolamento/mocks onde definido pelos testes e não substituem as provas reais da VPS acima.

## Limites de certificação

Não se reexecutaram hoje as 40 ações nem as 220 funções REA individualmente, todos os formatos CAD/media/documentos, GUI completa, gravação OBS nativa, edição automatizada Audacity, licenças comerciais, testes de carga, saúde dos outros serviços ou recuperação efetiva de rollback.

**Conclusão:** o percurso central ensaiado funciona e entrega ficheiros reais. O catálogo integral continua a exigir certificação por capacidade, e as melhorias acima impedem tratar um PASS técnico parcial como garantia de 100% do produto.
