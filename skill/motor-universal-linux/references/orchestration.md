# Orquestrador do Motor Ferrari

Esta referência pertence à **única Skill Universal**, não é uma Skill nem um coordenador adicional.

A IA interpreta o pedido; o Ferrari escolhe entre operações base e adaptadores realmente instalados. engine/orchestrator.py valida planos tipados com dependências (DAG), série/paralelo, propagação de falhas, relatório e artefactos. Não executa shell arbitrário vindo de texto livre.

## Execução suportada

- Via CLI Ferrari, construir um plano JSON validado e executar no ambiente autorizado com python3 -m engine.orchestrator --plan plano.json --workspace pasta --execute --max-parallel 2.
- Via Skill do ChatGPT, usar kind=plan no **mesmo** workflow ferrari-skill-request.yml e engine.skill_job. [Teste remoto do plano #41620077416](https://github.com/martaxi-boss/VPS/actions/runs/41620077416) concluiu com ZIP.
- Usar kind=inventory para descobrir binários reais, kind=invoke para adaptadores e kind=operation para operações base. Não equiparar detecção a certificação.

O motor não tem certificação de persistência após reinício, checkpoint/reprise, agendamento automático ou execução de todos os fornecedores REA. Prefect e Ruflo são opcionais; nenhum substitui o orquestrador próprio. ComfyUI CPU não tem modelos validados; sem GPU confirmada, não prometer inferência.

Coleções públicas de Skills servem como referência de procedimentos e licenças, não como binários instalados. Consultar engine/skillpacks_audit.json e docs/ORQUESTRADOR_SKILLS_GITHUB.md antes de qualquer reutilização.
