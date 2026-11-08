# Ferrari — funcionalidade real de regras Prometheus (08/11/2026)

## Resultados verificados

- Motor `martaxi-boss/skill-universal`, [PR #167](https://github.com/martaxi-boss/skill-universal/pull/167) integrada; SHA `3f0ba44b7d8475a74a63c6010d1e27063c04bf1e`.
- [CI #42507144652](https://github.com/martaxi-boss/skill-universal/actions/runs/42507144652) e [PR CI #42507148200](https://github.com/martaxi-boss/skill-universal/actions/runs/42507148200): PASS; testes de inputs inválidos, fuga de projeto, ausência de shell, limite temporal e rollback.
- [Pré-teste privado VPS #42507407090](https://github.com/martaxi-boss/VPS/actions/runs/42507407090): 532 regressões PASS, 40/40 ações, parsing real `promtool check rules` sobre regras sintéticas (`FERRARI_PRIVATE_PROMETHEUS_RULES_REAL=PASS`), versão ativa mantida, 8/8 serviços.
- [Ativação protegida VPS #42507525402](https://github.com/martaxi-boss/VPS/actions/runs/42507525402): repetição dos testes, `FERRARI_RELEASE_SWITCH=PASS`, versão ativa confirmada `3f0ba44b...`, fallback `427e1c33...`, `FERRARI_PROMRULES_ACTIVE_51_CALLABLE=PASS`, oito serviços ativos e zero reinstalações.
- Ponte Skill original alinhada em [PR VPS #405](https://github.com/martaxi-boss/VPS/pull/405); conexão SSH e identidade de host inalteradas.

## Único catálogo

173 programas + 280 funções (20 operações + 40 ações + 220 REA) + 3 dependências + 2 fornecedores = **458 entradas** no único `engine/catalog.json`. **51 callable**, **18 instalados sem operação direta**. Prometheus deixa de ser contado como suporte sem operação direta; yt-dlp permanece nessa classificação. Nenhuma função artificial foi criada para bibliotecas/frameworks.

## Contrato novo e verificável

```json
{
  "version": 1,
  "id": "promrules-demo-20261108",
  "kind": "operation",
  "operation": "prometheus-rule-check",
  "input": {
    "name": "synthetic-rules.yml",
    "content_base64": "Z3JvdXBzOgogIC0gbmFtZTogZmVycmFyaV9zeW50aGV0aWMKICAgIHJ1bGVzOgogICAgICAtIHJlY29yZDogZmVycmFyaV9zeW50aGV0aWNfbWV0cmljCiAgICAgICAgZXhwcjogdmVjdG9yKDEpCg=="
  },
  "acceptance": { "required_extensions": [".txt", ".json"] }
}
```

Entrada: `.yml`/`.yaml` UTF-8 até 64 KB, enviada como base64 apenas se sintética/não confidencial no repositório GitHub público. Execução: binário existente privado `tools/ferrari-services/prometheus/usr/bin/promtool`, argumentos fixos `check rules`, sem shell arbitrária, sem acesso à rede nem inicialização de serviço. Saídas: `promtool-check.txt` e `prometheus-rules-report.json` com contagem validada e SHA-256. Ficheiro inválido, executável ausente e fuga da pasta Ferrari interrompem a execução; não se promove `completed` por mera presença do binário.

**Limites:** esta operação valida regras de gravação/alertas enquanto sintaxe e expressões aceites pelo promtool. Não atesta scraping/ingestão de métricas, alertas entregues, disponibilidade de HTTP API, GUI, desempenho, ou um serviço Prometheus persistente. Também não certifica interfaces GUI de outros programas nem autonomia LLM dos agentes Ruflo. O Ruflo assistido por anfitrião foi certificado em [#42506220568](https://github.com/martaxi-boss/VPS/actions/runs/42506220568); autonomia dos agentes sem anfitrião não é comprovada.

## Estado operacional

O Ferrari reside exclusivamente em `/srv/projects/skill-universal`, conserva o fallback e mantém as oito unidades protegidas. A publicação de nova Skill ChatGPT exige atualização **da mesma identidade** e confirmação da versão; código/CI não implica instalação no cliente.
