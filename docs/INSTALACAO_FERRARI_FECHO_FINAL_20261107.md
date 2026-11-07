# Ferrari — fecho definitivo da instalação principal (07/11/2026)

## Resultado

**Instalação e higiene concluídas na VPS:** [aceitação final #42318822376](https://github.com/martaxi-boss/VPS/actions/runs/42318822376) — GitHub Actions `SUCCESS`, `FERRARI_FINAL_INSTALLATION_ACCEPTANCE=PASS`, `FERRARI_FINAL_PROTECTED_WORKFLOW=PASS`.

**Projeto isolado:** `/srv/projects/skill-universal/`. **Fonte:** `martaxi-boss/skill-universal`. **Release operacional:** `205c6f0e970259c79fa2111b6670c2fe1672fb27`; **fallback moderno:** `7bf6dcecf15da26502c5969b5eee54d5e116fc32`. Ambos contêm o mesmo catálogo universal de 450 entradas.

| Prova medida | Resultado |
|---|---|
| Catálogo persistente único `engine/catalog.json` | 450 registos |
| Programas / funções / dependências / fornecedores | 173 / 272 / 3 / 2 |
| Funções REA na mesma lista | 220 |
| Programas Ubuntu selecionados detetados | **55/55** |
| Ações integradas executáveis | **40/40** |
| Programas detetados no inventário | **69 programas** |
| Manifestos antigos no ativo e fallback | **0** |
| Release antiga com catálogo de 394 entradas | **Eliminada** |
| Oito pacotes globais antigos | **0 instalados** |
| Oito serviços protegidos | **8/8 ativos** |
| Alterações ao catálogo, APT e projetos alheios no ensaio | **Nenhuma** |

A remoção de 394 registos e 2 433 024 bytes tinha sido certificada em [#42315724016](https://github.com/martaxi-boss/VPS/actions/runs/42315724016). A auditoria final confirmou que essa release antiga já não está na pasta `releases`. Não foram necessárias reinstalações.

## OBS e capacidades opcionais — não confundir com instalação

OBS Studio **32.2.2 está presente e responde corretamente a `--version`** a partir do launcher privado. O teste isolado tentou iniciar uma gravação local **apenas de um canvas vazio**, sob Xvfb, sem captar câmara, ecrã, microfone ou transmitir. **Não foi gerado um ficheiro de vídeo** (`recording_files_created=0`, `obs_local_recording_certified=false`). Por isso, a gravação OBS permanece **não certificada**. Os ficheiros de ensaio temporários foram eliminados.

O teste não equivale à certificação de interface interativa, formatos PDAL opcionais (HDF/Icebridge), bibliotecas transitivas de todas as 173 entradas ou qualquer projeto de produção. Esses são testes funcionais sob pedido, **não impedimentos à instalação Ferrari principal já certificada**. A prova PDAL TXT→LAS→TXT encontra-se em [#42317695882](https://github.com/martaxi-boss/VPS/actions/runs/42317695882), sem necessidade de nova instalação.

## Alinhamento e entrega

- **Um motor, um catálogo, uma fonte de Skill no repositório.** A integração REA faz parte do mesmo catálogo; não recriar catálogos, motores, coordenadores ou pontes.
- **VPS e GitHub alinhados quanto ao conteúdo operacional.** É normal o `main` avançar com testes e documentação depois do SHA imutável da release ativa; isso não é uma instalação duplicada.
- A Skill instalada no **ChatGPT não foi substituída automaticamente**. A versão mais recente é empacotada pela CI do repositório, mas a ligação atual não disponibilizou um ID de plugin elegível para atualização direta. Não criar um plugin duplicado.
- Os relatórios F9–F11 e os commits históricos ficam como auditoria, **não** como instalações nem catálogos antigos.

**Decisão:** encerrar a instalação principal como CONCLUÍDA. Qualquer futuro pedido de editar/gravar em aplicação GUI é trabalho funcional da aplicação, com prova própria, sem reabrir a instalação geral do Ferrari.
