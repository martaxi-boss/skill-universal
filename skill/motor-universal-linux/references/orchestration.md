# Orquestrador e coleções de Skills públicas

Esta é uma **referência da única Skill Universal**, não uma Skill adicional.

## O que foi filtrado

Consultar engine/skillpacks_audit.json e docs/ORQUESTRADOR_SKILLS_GITHUB.md
no repositório skill-universal. Padrões úteis:
- Agent Skills: metadados mínimos + carregamento progressivo;
- Superpowers: clarificar objetivos, planear, testar e rever;
- wshobson/agents: padrões de especialistas sem depender do host;
- Vercel Skills: inventário público, mas não instalar Skills individuais;
- Prefect: opção livre para workflows duráveis depois de instalado e testado.

Não copiar source-available proprietários, não importar hooks das IAs
nem tratar Markdown como uma ferramenta Ubuntu.

## Fluxo do Motor Ferrari

1. Analisar ordem do utilizador com a IA à escolha.
2. Consultar inventário e plano Ferrari. Via ChatGPT, usar `kind=inventory` na ponte GitHub, não presumir SSH direto.
3. Verificar as ferramentas na seleção Ubuntu aprovada.
4. Transformar o pedido num JSON versionado:
   {"version":1,"steps":[{"id":"web","operation":"web-template",
   "layout":"store","title":"A Minha Loja"}]}
5. Validar o DAG em engine.orchestrator.validate_workflow().
6. Visualizar primeiro sem efeitos, depois executar mediante autorização
   através do próprio motor: python3 -m engine.orchestrator --plan ...
   --workspace ... --execute.
7. Entregar artefactos, relatório de sucesso/falha e executor efetivo.
8. Se uma capacidade não existir, não alegar execução. Integrar um novo
   adaptador Linux legítimo, testá-lo e então expor ao orquestrador.

## Limites reais da primeira implementação

O coordenador suporta dependências, paralelismo 1–4, operações tipadas,\nvalidadores e logs. A ponte GitHub→VPS está certificada para operações\nremotas simples. A fonte desta fase integra `kind=plan` no **mesmo**\n`engine.skill_job`, chamando o orquestrador existente, mas a VPS ativa\nainda nao o recebe ate passar CI e instalacao real. Não\nfornece um daemon persistente, retries, checkpoint reexecutável, UI,\nGPU nem contas cloud.
Essas capacidades exigem testes e integração adicionais, de preferência
com Prefect autoalojado quando justificado.

Ruflo/Skilled subagent harnesses são opcionais. O coordenador e as
ferramentas pertencem sempre ao Ferrari, sem reaproveitar Project Leader.
