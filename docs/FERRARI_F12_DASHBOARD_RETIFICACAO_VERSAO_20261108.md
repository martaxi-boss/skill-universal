# Ferrari F12 — retificação auditável da classificação de versão

**Data:** 8 de novembro de 2026  
**Missão:** `f12dash-20261108-7fd2c9` — dashboard comercial, PDF/JSON e revisão Ruflo assistida  
**Natureza:** retificação interpretativa do relatório emitido na conversa, **não** substituição de `report.json`, dos ZIP originais ou de qualquer evidência imutável.

## 1. Erro de classificação corrigido

O prompt inicial dizia `v1.0.16` porque foi elaborado antes da atualização da Skill. **Antes da execução desta missão**, a Skill azul `motor-universal-linux` foi atualizada na **mesma identidade** para **v1.0.20**, e a CI dessa versão terminou com sucesso: [#42518599628](https://github.com/martaxi-boss/skill-universal/actions/runs/42518599628) (554 testes executados; 3 ignorados; 0 falhas; dois pacotes publicados). A versão 1.0.20 da instalação ChatGPT foi confirmada separadamente por metadados do plugin.

**Correção:** a presença de `v1.0.16` na redação histórica do prompt **não constitui uma falha funcional** da versão corrente 1.0.20 e **não deve, por si só, reduzir a classificação da missão**. A versão histórica 1.0.16 não foi objeto de teste retroativo; marcar `NOT_TESTED`/não aplicável à versão atual, sem alegar que foi certificada.

| Dimensão | Classificação retificada | Fundamento |
|---|---|---|
| Missão funcional do dashboard na infraestrutura corrente | **PASS no âmbito ensaiado** | Trabalhos e saídas reais em GitHub Actions/SSH/VPS |
| Skill instalada ao executar a missão | **v1.0.20, confirmada por metadados** | Mesma identidade `motor-universal-linux`; CI aprovada antes do teste |
| Certificação retroativa da Skill v1.0.16 | **NÃO TESTADA / fora do âmbito** | Número antigo no prompt; não se utilizou a release histórica |
| Origem independente da chamada *na interface azul* | **PARTIAL** | A correlação dos pedidos aos commits não é, sozinha, um atestado externo da UI |
| Certificação global de todas as funções do Ferrari | **NOT_CERTIFIED** | O ensaio cobre esta missão, não as 280 funções nem todas as capacidades |
| CI 1.0.20 durante esta missão | **Não repetida; CI prévia PASS** | [#42518599628](https://github.com/martaxi-boss/skill-universal/actions/runs/42518599628) é uma prova separada |

**Veredito correto:** **`PASS_FUNCIONAL` para a missão Ferrari F12 executada**, com **`PARTIAL` apenas para a proveniência externa da interface azul e limites de escopo**. Não usar a simples divergência 1.0.16/1.0.20 para reprovar uma missão funcional.

## 2. Evidências que se mantêm inalteradas

- Inventário real na VPS: [#42519871404](https://github.com/martaxi-boss/VPS/actions/runs/42519871404): 458 entradas, 280 funções e 40 ações disponíveis; prova de disponibilidade, não execução funcional de todas.
- Primeira tentativa web rejeitada: [#42520321477](https://github.com/martaxi-boss/VPS/actions/runs/42520321477): envelope inválido, **bloqueio antes do SSH**. Posterior execução web: [#42520450646](https://github.com/martaxi-boss/VPS/actions/runs/42520450646) — execução SSH/VPS e artefactos reais, com testes desktop/móvel Playwright relatados.
- PDF Typst: [#42520631646](https://github.com/martaxi-boss/VPS/actions/runs/42520631646). JSON jq: [#42520672915](https://github.com/martaxi-boss/VPS/actions/runs/42520672915).
- Revisão adversarial com rejeição expressa dos 390 €: [#42520837803](https://github.com/martaxi-boss/VPS/actions/runs/42520837803); aprovação do valor correto 385 €: [#42521003133](https://github.com/martaxi-boss/VPS/actions/runs/42521003133).
- Encerramento Ruflo: [#42521075287](https://github.com/martaxi-boss/VPS/actions/runs/42521075287), commit `9446e1380bc368b6e04b305bf902f059870c7c08`, artefacto `ferrari-skill-result-42521075287`, três tarefas aprovadas; zero chamadas LLM autónomas por agente.

Valores de referência da missão: **385 €**, **20 unidades**, **8 registos**, categorias **140 € Eletrónica**, **145 € Casa**, **100 € Moda**.

A coordenação Ruflo é **assistida pela IA anfitriã**; a prova não demonstra modelos autónomos na VPS. O dashboard testou navegador Chromium em viewport móvel simulada, não um dispositivo físico. O `quality_gate` genérico do encerramento Ruflo pode permanecer `not_certified` mesmo com revisões concluídas; não o sobrescrever.

## 3. Integridade e imutabilidade da auditoria

As execuções, commits, relatórios `report.json`, artefactos `ferrari-skill-result` e seus hashes históricos devem permanecer **inalterados**. O ZIP original de 32 ficheiros foi anunciado no outro chat com SHA-256:

`19632f79d670ea54f28a1fe18f9f3b0fdc98122ce3afdbd66af83518fb05c1c4`

Esse hash refere-se **exclusivamente ao ZIP original**. Esta retificação é um documento separado: não se deve dizer que o ZIP anterior já inclui este texto, nem reutilizar o hash original como se certificasse um pacote alterado.

**Estado de fecho:** a divergência histórica da versão está esclarecida; a missão funcional não precisa de ser repetida por este motivo. Para fechar a proveniência de interface, será necessária prova correlacionada do pedido direto na Skill azul e seu ID/commit/ZIP, sem inventar atestado da UI.
