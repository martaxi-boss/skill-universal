# Ferrari — triagem de instalação e integração de 19 programas (08/11/2026)

## Decisão

**Não reinstalar em massa.** A presença de um executável, um pacote npm ou um
módulo Python não prova que o Ferrari tenha uma operação funcional para esse
programa. Também não justifica criar uma operação falsa por cada biblioteca.

Este registo classifica os **19 programas que no inventário real
[#42497575120](https://github.com/martaxi-boss/VPS/actions/runs/42497575120)
apareceram como `installed_unintegrated`**. O catálogo único mantém
**173 programas, 279 funções, 3 dependências e 2 fornecedores (457 entradas)**.
Esta alteração adiciona apenas informação de triagem aos 19 programas;
**não instala, remove, reconfigura, inicia serviços, introduz funções ou altera
os restantes projetos da VPS**.

| Grupo | Quant. | Programas | Decisão |
|---|---:|---|---|
| Reutilização indireta | 2 | Ruflo, Playwright | Não duplicar operações; confirmar a chamada real pelo fluxo anfitrião/browser quando necessário |
| Backend que exige prova | 1 | Ghidra | Verificar a chamada via REA antes de afirmar integração |
| Dependências de desenvolvimento | 7 | Next.js, Tailwind, Bootstrap, shadcn, Streamlit, Gradio, Prefect | Reutilizar dentro de um projeto/fluxo concreto; não criar ação direta sem necessidade |
| Aplicações GUI opcionais | 6 | FreeCAD, Audacity, OBS, SolveSpace, Synfig, OpenShot | Exigir caso real, display/headless certificado e limites de recursos antes de ligar |
| Execução de modelos opcional | 1 | ComfyUI | Só aceitar tarefas com modelo local, recursos e execução comprovados |
| CLI com futuro adaptador limitado | 2 | yt-dlp, Prometheus | Testar o executável existente; definir posteriormente uma operação útil, delimitada e auditável |

## Prova nova executada na VPS

Pedido autorizado e read-only: [job-ferrari-support-probes-20261108-1641.json](https://github.com/martaxi-boss/VPS/blob/main/ferrari-requests/job-ferrari-support-probes-20261108-1641.json).

[GitHub Actions #42502000597](https://github.com/martaxi-boss/VPS/actions/runs/42502000597)
terminou com sucesso, devolvendo `response.zip` e
`artifacts/runtime-check.json`. Verificações:

- `ytdlp` — `/srv/projects/skill-universal/tools/yt-dlp-2026.10.26/yt-dlp`,
  arranque de `--version`, exit 0, versão `2026.10.26`: PASS.
- `prometheus` — `/srv/projects/skill-universal/tools/ferrari-services/prometheus/usr/bin/prometheus`,
  arranque de `--version`, exit 0, versão `2.45.3+ds`: PASS.

**Limitação explícita:** provas de versão/arranque não são provas de
download, monitorização em serviço, configuração, rede, API, GUI ou de
qualquer operação de utilizador. O campo `integrated_action_certified`
permanece `false` para ambas.

## Implementação de inventário

A classificação reside **exclusivamente no objeto de cada programa em
`engine/catalog.json`**. Não se cria uma segunda fonte de dados.
`engine/tool_runtime.py` junta a política persistida à deteção privada
do anfitrião, gerando o campo `installation_review` e o agregado
`installation_triage`:

- Programa **detetado**: `reuse_private_installation` — não pedir outra instalação.
- Programa **não detetado nesse anfitrião**:
  `evaluate_only_for_requested_workflow` — não fazer instalações automáticas.
- `direct_operation_confirmed` mantém-se falso até haver rota Ferrari
  efetiva; nenhuma classificação é promovida artificialmente a `callable`.

O resultado deve ser validado com testes unitários no CI e, para refletir
esta alteração na VPS, com uma release imutável seguida dos mesmos pré-testes,
ativação protegida e verificação das 8 unidades. **Código no GitHub não é,
por si só, prova de deploy na VPS.**

## Política para próximos trabalhos

1. Prioridade a operações reais de utilizador, com entradas/saídas
   determinadas, limites de tempo e recursos, sem shell arbitrária.
2. Para bibliotecas e frameworks, chamar o programa através do consumidor;
   não adicionar uma rota duplicada só para mudar uma contagem.
3. Para GUI, nunca declarar integração completa com base em `--version`.
4. Não apagar aplicações da VPS unicamente por estarem classificadas como
   opcionais: primeiro apurar consumidores e eventual necessidade futura.
5. Preservar a Skill Ferrari única, o catálogo único, pastas privadas e a
   infraestrutura GitHub Actions → SSH existente, sem mexer nos outros serviços.
