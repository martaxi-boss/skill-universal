# Motor Ferrari — propriedade e desinstalação sem efeitos colaterais

**Diretório exclusivo na VPS:** `/srv/projects/skill-universal/`.

**Repositório correspondente:** `martaxi-boss/skill-universal`. O nome da pasta coincide com o nome do repositório. A aplicação, os seus executores, versões do motor, Python/Node/Java próprios, virtualenvs, npm, cache e artefactos de trabalho têm de ficar **dentro dessa árvore**. Bibliotecas fundamentais do próprio Ubuntu não pertencem ao Ferrari e não devem ser desinstaladas.

## Inventário de propriedade

| Recurso | Local / política | Desinstalação Ferrari |
|---|---|---|
| Código versionado, `current` e fallback | `/srv/projects/skill-universal/releases`, `current` | Pertencem ao Ferrari |
| CLIs, aplicações CAD, Office, engenharia reversa | `/srv/projects/skill-universal/tools` | Pertencem ao Ferrari |
| Python/Node/JDK privados | `/srv/projects/skill-universal/runtimes` | Pertencem ao Ferrari |
| Ambientes Python, npm/REA/Ruflo, browsers, trabalhos, caches | `/srv/projects/skill-universal/.runtime` | Pertencem ao Ferrari; verificar backups/dados antes de eliminar |
| Ponte GitHub Actions → VPS | Repositório GitHub separado `martaxi-boss/VPS` | **Não** pertence ao sistema de ficheiros do Ferrari; desativar apenas os gatilhos Ferrari antes de desinstalar |
| SSH, GitHub Actions, Supervisor passivo, Nginx, PostgreSQL e PM2 de outros projetos | Ubuntu e respetivos projetos independentes | **Nunca remover nem alterar** como efeito da desinstalação Ferrari |
| Pacotes APT globais históricos | `/usr`, `/opt` ou base Ubuntu | **Nunca remover automaticamente**: outros consumidores podem existir. Atribuição é tarefa transversal da Fase 9 |

## Ensaio de desinstalação, sem apagar produção

1. Confirmar por Actions a release ativa, o fallback e o SHA do GitHub correspondente. Não confundir `main`, branch de preparação e SHA realmente instalado.
2. Consultar a auditoria **read-only** de registos `systemd`, cron, Nginx e Supervisor e a lista de processos. Investigar cada referência à pasta Ferrari antes de a apagar. A varredura é delimitada, portanto ausência de referência não comprova ausência universal de consumidores.
3. Identificar e guardar externamente os **dados próprios que devam ser retidos** (relatórios, resultados, configurações e evidências) por decisão explícita do proprietário. Backups não devem transformar-se numa dependência partilhada de outros projetos.
4. Desativar os *triggers* exclusivos Ferrari no repositório `martaxi-boss/VPS` e impedir novos pedidos dirigidos ao motor; deixar os workflows e segredos de outros projetos intocados.
5. Verificar inexistência de processos Ferrari em execução e consumidores externos ao projeto. Se houver dependentes, **bloquear a desinstalação** e corrigir a referência no seu projeto de origem, independentemente.
6. Só numa desinstalação futura explicitamente autorizada, retirar a **única árvore Ferrari** depois de uma confirmação final do proprietário. Não executar `apt purge` em lote, nem eliminar `/usr`, `/opt`, `/home/ubuntu` ou outras pastas de projetos.
7. Confirmar após a remoção que PINK, FADEGO, Low Cost, robôs Telegram, Project Leader e serviços base mantêm os seus próprios diretórios, estado e saúde. Se houver regressão, recuperar o backup do Ferrari e reverter apenas alterações Ferrari.

**Estado da Fase 7:** esta é uma política e preparação de remoção **não destrutiva**. Não se executou desinstalação na VPS. O certificado real desta fase anexará o inventário de registos externos e identificará eventuais bloqueios; não promete remoção sem impacto se houver referências externas ainda não classificadas.

**Regras:** uma Skill Ferrari, um motor, um orquestrador existente; sem coordenador na VPS, sem instalações globais Ferrari, sem dependências entre projetos, sem novos fornecedores pagos obrigatórios.
