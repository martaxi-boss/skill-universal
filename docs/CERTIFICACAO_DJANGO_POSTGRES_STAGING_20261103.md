# Lowcost Europa — Django/PostgreSQL PASS e staging bloqueado no runner (03/11/2026)

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
