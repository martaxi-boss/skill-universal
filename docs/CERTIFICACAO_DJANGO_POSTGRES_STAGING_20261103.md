# Lowcost Europa — Django/PostgreSQL e staging certificados (03/11/2026)

## Resultado final após correção mínima

- [PR #186 Lowcost Europa](https://github.com/martaxi-boss/lowcost-europa/pull/186) integrada em `main` (`0a1707e534d127ebd1f0f3f3cf6542ffaa5431b1`). Único workflow alterado: `.github/workflows/staging-browser-qa.yml`, fixa o runner em Ubuntu 24.04, compatível com Playwright `1.56.1`, e executa browser QA em PR/push quando o workflow ou script mudam. Sem alterações ao código da montra, backend ou produção.
- **Staging pós-merge** [GitHub Actions #41605911458](https://github.com/martaxi-boss/lowcost-europa/actions/runs/41605911458) SUCCESS. ZIP original de `lowcost-staging-browser-qa` inspecionado: `result.json` com `status=PASS`, `checks=15`, `errors=[]`, `warnings=[]`. Foram verificadas 7 páginas em desktop (1440x900) e 7 em mobile emulado (390x844) e 1 controlo HTTP. **14 PNG reais e zero overflow horizontal** nas páginas. Inclui homepage, 5 páginas de categorias e pesquisa, menu móvel, filtro/ordenar/comparar ofertas, imagem de fornecedor/fallback, robots `Disallow: /`, estáticos HTTP 200 e redirecionamento do painel anónimo HTTP 302.
- **CI pós-merge** [#41605911466](https://github.com/martaxi-boss/lowcost-europa/actions/runs/41605911466) SUCCESS: PostgreSQL 16 isolado, check, check --deploy, migrações, Ruff, testes JS e **709 testes Django PASS**. [Auditoria #41605911500](https://github.com/martaxi-boss/lowcost-europa/actions/runs/41605911500) SUCCESS.
- **CI de PR** [staging #41605493764](https://github.com/martaxi-boss/lowcost-europa/actions/runs/41605493764), [Django #41605493789](https://github.com/martaxi-boss/lowcost-europa/actions/runs/41605493789) e [audit #41605493709](https://github.com/martaxi-boss/lowcost-europa/actions/runs/41605493709): todos SUCCESS, antes do merge. O mesmo `result.json` de staging da PR reportou 15 PASS, 0 erros, 0 avisos.
- **Limites:** o browser QA é de leitura e usa Playwright Chromium, com mobile emulado (não Android físico). Não executa compras, autenticados, APIs de fornecedor nem verifica serviços em produção. Django/PostgreSQL foi executado em CI com DB temporária e não leu dados da produção. Ferrari não executou o backend; coordenou registo de evidências existentes.

## Histórico anterior à correção



## Âmbito e premissas

Repositório consultado e testado sem alteração de ficheiros: [`martaxi-boss/lowcost-europa`](https://github.com/martaxi-boss/lowcost-europa), commit `388860c6a167686a378b89f4282304bce89c25de` de `main`. Não se acedeu à base de dados de produção, não se executaram POSTs nem se fizeram compras. Foram relançados **jobs existentes do GitHub Actions**; este teste backend não foi executado pelo processo `vite-build` do Ferrari, que não oferece backend Django/PostgreSQL.

## Django e PostgreSQL 16 — aprovado

**[CI #41068103444, tentativa 2](https://github.com/martaxi-boss/lowcost-europa/actions/runs/41068103444)**: executada novamente em 03/11/2026, `SUCCESS`, mesmo commit `388860c6...`. Utilizou PostgreSQL 16 isolado, temporário, no GitHub Actions. Logs e passos inspecionados:

- `python manage.py check` — PASS, zero problemas.
- `python manage.py check --deploy` — PASS (é verificação de configurações, **não** um deploy real).
- `python manage.py makemigrations --check --dry-run` — PASS, `No changes detected`.
- `ruff check .` — PASS, `All checks passed!`.
- JavaScript: sintaxe de `product-images.js` e `catalog-explorer.js`, e respetivos testes Node — PASS.
- `python manage.py migrate --noinput` — PASS, migrações incluindo catálogo até `0020_externalmetricssnapshot`.
- `python manage.py test` — **709 testes executados, 709 PASS** em 21,295 segundos.

Não é prova de produção ou disponibilidade pública. Main permaneceu no mesmo commit.

## Staging browser QA — não certificado hoje

**[Staging browser QA #40664538172, tentativa 2](https://github.com/martaxi-boss/lowcost-europa/actions/runs/40664538172)**: relançado em 03/11/2026, **FAIL**, na etapa `Install Playwright Chromium`, **antes** de executar qualquer teste de página.

Evidência literal do erro dos logs:

```text
Image: ubuntu-26.04
Cannot install dependencies for ubuntu26.04-x64 with Playwright 1.56.1!
Error: ERROR: Playwright does not support chromium on ubuntu26.04-x64
```

O workflow usa `runs-on: ubuntu-latest` e `playwright@1.56.1`; no momento do teste, `ubuntu-latest` foi resolvido para Ubuntu 26.04, incompatível com a instalação desta versão do Chromium. **Não se pode atribuir a falha ao site**, porque ele nem chegou a ser aberto. Nenhum screenshot/resultado JSON novo foi criado. O artefacto `lowcost-staging-browser-qa` associado ao run data de **28/10/2026**, não desta repetição, e não pode servir como nova prova.

**Histórico, não atual:** a tentativa 1 do mesmo run em 28/10/2026 usou **Ubuntu 24.04**, conseguiu instalar Playwright/Chromium e obteve `BROWSER_QA_RESULT=PASS checks=13 errors=0`. Esse script mais antigo não incluía todos os testes do explorador de catálogo nem a página de pesquisa presentes em `tests/browser/staging-browser-smoke.cjs` na `main` atual. Não confundir a certificação histórica com validação atual.

**Falha secundária do workflow histórico:** o job `clean_ephemeral_branch` tentou apagar `ops/lowcost-staging-browser-qa-20261028` (branch de 28/10), já inexistente; GitHub respondeu `HTTP 422 Reference does not exist`. A tentativa não removeu nem alterou a branch `main`.

## Desbloqueio mínimo recomendado

No repositório Lowcost Europa, em `.github/workflows/staging-browser-qa.yml`, **fixar o runner compatível**:

```yaml
jobs:
  public-browser:
    runs-on: ubuntu-24.04
```

Manter as verificações e o Playwright existentes. Depois, executar via `workflow_dispatch` a versão de `main` atual. Inspecionar `BROWSER_QA_RESULT`, provas desktop/mobile, endpoints de saúde/robots/segurança, exploração dos filtros e painel, e relatórios JSON. Alternativamente, atualizar a versão Playwright para uma comprovadamente compatível com Ubuntu 26.04, testando dependências primeiro.

**Alteração ainda não aplicada**: o pedido atual foi uma verificação, e nenhum ficheiro de Lowcost Europa ou workflow foi modificado. O acesso daqui permite voltar a executar jobs existentes mas não inclui um comando de `workflow_dispatch` para iniciar a versão atual de um workflow manual. O site externo também não ficou acessível a partir deste ambiente para executar navegador local, pelo que **o estado atual do staging permanece por certificar**.

## Continuidade Ferrari

A anterior [certificação de frontend original Lowcost](TESTE_REAL_LOWCOST_EUROPA_20261103.md) permanece válida para o código estático local (17/17 verificações DOM PASS, teclado e capturas), mas não prova Django/produção. Release Ferrari VPS permanece `ec4dc5045a034e3fbbbcfe3477e1641e80714262` com rollback `9277a56b9b57c87b8b4e3dfbba08f4536add3625`. Estes novos testes usaram a infraestrutura de CI do próprio projeto e **não** alteraram o motor, a ponte SSH nem os outros projetos.
