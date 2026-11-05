# Bootstrap portátil — Motor Ferrari Ubuntu

**Estado certificado em 05/11/2026.** Este ficheiro acompanha **uma Skill Universal Ferrari**, única e independente. O [BOOTSTRAP canónico do GitHub](https://github.com/martaxi-boss/skill-universal/blob/main/BOOTSTRAP.md) e os runs atuais são a fonte de verdade; este resumo não substitui inventário real da VPS.

## Arquitetura e projeto

ChatGPT/Codex interpreta o pedido → Skill Ferrari → GitHub autenticado `martaxi-boss/VPS` → workflow Ferrari existente → SSH existente → `/srv/projects/skill-universal/current` → motor/fornecedores/executores privados → `report.json` e `response.zip`.

Não instalar nada do Ferrari fora de `/srv/projects/skill-universal/`; não misturar pastas, dependências, fornecedores ou versões com PINK IPTV, Project Leader, Telegram, REA legado, FADEGO ou Low Cost Europa. Não criar coordenador na VPS. O Supervisor é passivo. Não alterar ponte SSH, workflow de transporte nem pin sem autorização específica. Componentes fundamentais do Ubuntu não são dependências de aplicação e não devem ser removidos sem auditoria.

**Transporte e código histórico:** o validador do workflow GitHub VPS está pinado em `292aeb7d10eecef8c3ca84760cd579e84e4b97f3`; não alterar SSH nem ponte. O commit antigo `b2869e334d9d68a0c988905e71ce0badec6ba359` foi verificado em CI e [VPS #41786521407](https://github.com/martaxi-boss/VPS/actions/runs/41786521407) certificou uma release anterior. São provas históricas, não a release ativa.

## Prova operacional vigente

- **Ponto 2 (executores privados):** release ativa `87969badbde0a77c2c181bb9605357d51a4a30c0` e fallback `62f862cdf9727842546a244a3e4ec19dd8bc82f4`, verificados [VPS #42030605124](https://github.com/martaxi-boss/VPS/actions/runs/42030605124). Foram certificadas **40/40 ações tipadas** com executores e dependências de aplicação dentro do Ferrari. Essa execução também higienizou 31 releases antigas e 12 pastas temporárias exclusivamente Ferrari, com aproximadamente 905 MB recuperados. Não repetir limpezas sem inventário e backup.
- **Ponto 3 (provas por uso):** [relatório detalhado e 7 execuções reais](https://github.com/martaxi-boss/skill-universal/blob/main/docs/CERTIFICACAO_FUNCIONAL_PONTO3_20261105.md). Web/Playwright, documentos e OCR/PDF, dados DuckDB/Polars, imagem, LMMS/MLT/FFmpeg, CAD/IFC/Blender e orquestração DAG passaram nos casos testados. REA/Android passou apenas nas chamadas concretas descritas na matriz.
- **Inventário mais recente pela Skill:** [VPS #42034776491](https://github.com/martaxi-boss/VPS/actions/runs/42034776491), **40 ações**, **55/56 candidatos Ubuntu detetados** e **83 programas detetados** no inventário alargado. Penpot continua ausente. Catálogo, deteção, instalação, adaptador e execução comprovada são estados distintos.
- **Ferrari/REA privado:** `rea-agents@6.8.0` dentro de `.runtime/npm/rea`, com 229 nomes MCP no catálogo (não 229 execuções testadas); Node/Java, Ghidra/JADX, Apktool 3.0.3, Hopper 6.6.1 demo e ferramentas Android instalados privadamente. Os REAs legados FINAL e Trial foram removidos, com prova [VPS #41840478411](https://github.com/martaxi-boss/VPS/actions/runs/41840478411). Não eliminar o REA privado do Ferrari.
- **Limite remanescente de isolamento das operações base:** testes do ponto 3 confirmaram que `cad-stl` usou `/usr/bin/openscad`; `blender-house` usou `/usr/bin/blender`. Os 40/40 privados referem-se às **ações tipadas**, não a estas operações base. Não declarar isolamento universal nem reinstalar esses executáveis globalmente.
- **Outros limites reais:** ADB sem dispositivo físico; nenhuma validação de toda a GUI interativa, Penpot, modelos/inferência ComfyUI ou funções pagas do Hopper. O catálogo MCP e os 83 programas detetados não estão integralmente certificados.

## Contrato de desinstalação independente

O projeto Ferrari deve guardar programas, ferramentas, bibliotecas de aplicação, fornecedores, caches e dados apenas em `/srv/projects/skill-universal/`. Nunca instalar globalmente via APT para o projeto, procurar programas em `/usr/bin` por fallback ou importar dependências de outro projeto. O Ubuntu básico (kernel, loader, bibliotecas essenciais do sistema operativo) é a base comum inevitável.

Antes de desinstalar: preservar backup, identificar serviços/processos/agendamentos/links específicos do Ferrari, desligar e remover **apenas** esses registos, apagar a pasta do Ferrari quando autorizado e confirmar os restantes projetos. Não remover programas globais antigos sem verificar os seus consumidores. O instalador privado CAD/Blender terminou com `FERRARI_PRIVATE_CAD_INSTALL=PASS` segundo captura apresentada pelo utilizador em 05/11; isto não equivale a certificação final de renderização nem à ativação da release. O teste posterior `install/vps-private-cad-smoke.sh` **PASS** consta da captura apresentada em 05/11 às 14:50, com STL/BLEND/GLB/PNG reais, tamanho e assinaturas. Esse teste usou caminhos privados, mas não ativou uma release GitHub. A Skill→VPS→ZIP depois da ativação e o LibreOffice privado continuam pendentes de provas específicas. Para o último, existe `install/vps-private-office.sh`, instalador de AppImage Standard publicado como método alternativo de LibreOffice; exige teste real DOCX→PDF. Não afirmar versão/assinatura verificadas antes de a execução acontecer.

## Usar a Skill

1. Confirmar o [BOOTSTRAP canónico](https://github.com/martaxi-boss/skill-universal/blob/main/BOOTSTRAP.md) e, quando necessário, pedir inventário novo por `kind=inventory`.
2. Ler `references/github-bridge.md` para criar um pedido **novo**, sem segredos, em `ferrari-requests/job-<id>.json` no repositório VPS. Tipos: `inventory`, `operation`, `invoke`, `auto`, `plan`, `rea-mcp`. Nada de shell arbitrário.
3. Relacionar o commit ao run correto, exigir status `completed`, `FERRARI_SKILL_END_TO_END=PASS` e artefactos reais do ZIP. Não repetir pedidos automaticamente diante de erro.
4. Para uma capacidade nova, avaliar compatibilidade Ubuntu, licença, dependências e recursos; integrar no **mesmo Ferrari**, testar em CI, VPS e Skill→GitHub→VPS→ZIP e documentar limites. Nenhuma Skill ou camada paralela.
5. A CI de `martaxi-boss/skill-universal` publica `ferrari-skill-installable` contendo `skill.zip`. Confirmar a instalação da versão atualizada **no cliente ChatGPT** separadamente: uma aprovação da CI não a instala por si.

Todos os pedidos públicos devem usar ficheiros sintéticos/públicos. Base64 não é encriptação: nunca publicar dados privados, tokens ou documentos do cliente no repositório VPS.
