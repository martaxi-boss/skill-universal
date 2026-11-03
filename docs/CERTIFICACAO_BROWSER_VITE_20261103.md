# Motor Ferrari — certificação da fase web com Chromium real (03/11/2026)

## Estado certificado

**Motor Ferrari release ativo na VPS:** `13c4399257cd19496f378ad3f15cd1ebe877977b`.

**Provas reais:**
- [Sondagem read-only pela Skill #41559647734](https://github.com/martaxi-boss/VPS/actions/runs/41559647734) — SUCCESS. Não havia Chromium nem Firefox no PATH ou cache Ferrari. A sondagem foi incorporada sem criar operação ou camada.
- [PR #5 — deteção limitada de navegadores](https://github.com/martaxi-boss/skill-universal/pull/5).
- [PR #6 — extensão de `vite-build` com Chromium headless](https://github.com/martaxi-boss/skill-universal/pull/6).
- [Entrega inicial #41560226160](https://github.com/martaxi-boss/VPS/actions/runs/41560226160) — FAILURE após baixar o navegador, por conferir o executável de Chromium completo em vez do headless shell. A falha foi registada e corrigida, não escondida.
- [PR #7 — correção mínima do caminho do shell](https://github.com/martaxi-boss/skill-universal/pull/7).
- [CI corrigida #41560479616](https://github.com/martaxi-boss/skill-universal/actions/runs/41560479616) — SUCCESS, **99 testes PASS** e pacote da Skill verificado.
- **[VPS #41560720430](https://github.com/martaxi-boss/VPS/actions/runs/41560720430)** — SUCCESS, **99 testes PASS na VPS**, `FERRARI_BROWSER_INSTALL=PASS_FERRARI_ONLY_NO_SYSTEM_PACKAGES`, `FERRARI_VITE_BROWSER_REAL=PASS`, `FERRARI_IFC_GEOMETRY_REAL=PASS` e `FERRARI_ONLY_HYGIENE=PASS`.
- **[Pedido real pela Skill #41560954411](https://github.com/martaxi-boss/VPS/actions/runs/41560954411)** — SUCCESS, `FERRARI_SKILL_JOB_STATUS=completed`, `FERRARI_SKILL_END_TO_END=PASS`, ZIP com ficheiros de produção e screenshot.

## Ferramentas e resultados (medidos)

| Ferramenta | Versão/prova | Local próprio Ferrari |
|---|---|---|
| Vite | 8.3.5 | `~/.local/share/motor-ferrari/.runtime/npm/vite` |
| Node.js | 22.23.4 | `~/.local/share/motor-ferrari/runtimes/node-22.23.4` |
| Playwright | 1.64.1 | `~/.local/share/motor-ferrari/.runtime/npm/playwright` |
| Chromium headless shell | 156.0.8078.4; revisão 1248 | `~/.local/share/motor-ferrari/.runtime/browsers` |

O instalador adicional usou apenas o runtime Ferrari, sem `sudo`, `apt`, Snap, serviço persistente ou Node global. A instalação do browser descarrega apenas o headless shell e o FFmpeg auxiliar incluído pelo próprio Playwright. O teste é executado diretamente no `vite-build` existente — **continuam a ser 12 operações base, sem nova Skill nem orquestrador**.

**Inventário final VPS:** 56 candidatos Ubuntu, **23/56 detetados**, **49 ferramentas nos catálogos combinados**, **21 ações externas**.

### Prova direta de navegador

O ZIP público de demonstração continha `index.html`, `src/main.js` e `src/style.css`. Na VPS, o Ferrari compilou-o com Vite, abriu os ficheiros resultantes num Chromium headless através de Playwright e devolveu:

- `artifacts/dist/index.html`, CSS e JavaScript compilados;
- `artifacts/browser-screenshot.png` com **15 875 bytes**, PNG real;
- `artifacts/browser-check.json`: `status=passed`, `browser_version=156.0.8078.4`, viewport `1280×720`, `dom_ready=complete` e `demo_js_ready=yes`;
- `artifacts/vite-build.json`: `browser_test.status=passed`;
- zero erros de consola/JavaScript e zero pedidos a servidores externos.

O navegador recebe ficheiros estáticos por uma rota virtual local, sem criar servidor nem serviço. Todas as requisições fora da origem de teste são bloqueadas; ficheiros de outro projeto não são publicados. **Este teste certifica uma compilação frontend pequena, não autenticação, backend, pagamentos, acessibilidade ou navegação completa de uma aplicação complexa.**

## Higienização VPS

Após os testes PASS, foi reutilizada **a rotina Ferrari já existente** `install/ferrari-hygiene.py`, em preview e depois apply:

- **Ativa preservada:** `13c4399257cd19496f378ad3f15cd1ebe877977b`.
- **Fallback preservado:** `aefd8bb156f95e47c5a90b2a5d96db8d26f94283` (96 testes PASS na fase de deteção).
- **Releases antigas removidas:** `f7eb9dcbda78a80f127b8981d9361e853672cd62` e `0cf745c3a4d05464949f917ea035f8e8388fd0eb` (tentativa de browser falhada).
- **Espaço adicional efetivamente livre:** **4 988 928 bytes (~4,76 MiB)**.
- **Espaço livre final:** **21,32 GiB**.
- `outside_ferrari_touched=false`: sem limpeza fora de `~/.local/share/motor-ferrari/releases`.

## Continuidade e limites

Uma única Skill Ferrari; lógica no repositório `martaxi-boss/skill-universal`; GitHub Actions/SSH continuam somente transporte. **Próxima fase possível, separada:** testes de navegação mais completos, responsividade e acessibilidade com casos concretos; não instalar frameworks ou expandir indiscriminadamente. Outros candidatos não detetados permanecem não certificados.

Consultar [BOOTSTRAP canónico](../BOOTSTRAP.md). As declarações acima são baseadas nos runs e ZIPs indicados, não apenas no catálogo.
