# Motor Ferrari — Fase 6: isolamento físico, inventário e auditoria real

**Data:** 05/11/2026. **Estado da fase: PARCIAL / NÃO ENCERRADA.** A correção de código e a release operacional estão certificadas; a atribuição dos pacotes globais e o inventário de órfãos exigem ainda prova adicional. Não misturar o PASS da instalação Ferrari com a certificação de independência de todos os programas do Ubuntu.

## Identidade operacional e política imutável

- Repositório: `martaxi-boss/skill-universal`; aplicação, releases e dependências específicas de projeto em `/srv/projects/skill-universal/`.
- **SHA realmente ativo:** `146145d5ada9c13e368df18727e4dbf4f5807664` — confirmada pela VPS, não inferida do HEAD da PR.
- **Fallback seguro preservado:** `40c0e1cdf31b1fe9589ad8be90e5eac06eec2856` (Fase 5).
- **Não** instalar pacotes Ferrari por APT global, não usar outro diretório de projeto, não inventar coordenador/pontes/Skills. Biblioteca básica do Ubuntu (kernel, loader, libc etc.) continua a ser infraestrutura do sistema e é diferente de uma aplicação instalada globalmente para o Ferrari.
- Nenhum pacote global foi removido, atualizado ou instalado na VPS nesta Fase 6. As dependências e executáveis **testados** resolveram dentro do Ferrari; não estender a conclusão a todos os módulos opcionais que não foram executados.

## Matriz de evidência real

| Etapa | Execução / âmbito comprovado | Resultado |
|---|---|---|
| Inventário de entrada Skill→GitHub→VPS→ZIP | [VPS #42076476856](https://github.com/martaxi-boss/VPS/actions/runs/42076476856) | PASS: 40 ações, **44/56** detetados; omissão indevida de Blender/OpenSCAD/LibreOffice privados |
| CI do candidato com correções | Ferrari [#42078107669](https://github.com/martaxi-boss/skill-universal/actions/runs/42078107669) e [#42078118322](https://github.com/martaxi-boss/skill-universal/actions/runs/42078118322) | SUCCESS: deteção CAD/Office privada, eliminação da descoberta global no catálogo antigo, travessia por symlinks bloqueada, testes de regressão |
| Auditoria física antes da migração | [VPS #42077855068](https://github.com/martaxi-boss/VPS/actions/runs/42077855068) | PASS: 40 ações privadas, runtimes próprios, 16 aplicações globais presentes; amostragem de consumidores insuficiente para permitir desinstalação |
| Precheck candidato sem trocar `current` | [VPS #42078448805](https://github.com/martaxi-boss/VPS/actions/runs/42078448805) | PASS: **241 regressões**, 40/40, OpenSCAD STL, Blender BLEND/GLB/PNG, LibreOffice PDF, Skill→ZIP; `current` preservado |
| Ativação protegida | [VPS #42078597765](https://github.com/martaxi-boss/VPS/actions/runs/42078597765) | PASS: SHA Fase 6 ativo, anterior conservado para rollback; 241 testes e 40/40 privados |
| Inventário real após ativação pela Skill | [VPS #42078887152](https://github.com/martaxi-boss/VPS/actions/runs/42078887152) | SUCCESS: `report.json.status=completed`, ZIP real, **47/56 privados detetados**, **40/40** ações |
| Reauditoria dinâmica preliminar | [VPS #42078973023](https://github.com/martaxi-boss/VPS/actions/runs/42078973023) | PASS: 13 ELF amostrados, 417 resoluções privadas, 12 SO base, 1 `libutil` do próprio Ubuntu posteriormente classificada como base |
| Auditoria dinâmica alargada | [VPS #42079545679](https://github.com/martaxi-boss/VPS/actions/runs/42079545679) | PASS: **33 executáveis ELF**, **1 447 bibliotecas resolvidas dentro Ferrari**, **13 do Ubuntu base**, **0 bibliotecas ausentes**, **0 dependências externas por classificar nesta amostra** |
| Saúde/higiene após release | [VPS #42079801582](https://github.com/martaxi-boss/VPS/actions/runs/42079801582), [issue #342](https://github.com/martaxi-boss/VPS/issues/342) | PASS: `AUDIT_ONLY`, 7 locais de cache verificados, 0 elegíveis, **0 removidos**, `protected_services_unchanged=true`, `health_after=true`; espaço livre variou -131 072 bytes durante observação, sem remoção |

## Correções aplicadas na release Ferrari

- `engine/tool_runtime.py`: três executores de base de CAD/Office passam a ser inventariados pelo mesmo caminho **privado** que é realmente invocado; outros executores privados deixam de aceitar links cujo caminho real escapa ao projeto.
- `engine/core.py`: o catálogo histórico, as alternativas e inspeção estática deixam de considerar um binário de `/usr/bin` como ferramenta Ferrari. Inspeção ELF e tipo de ficheiro requerem executores privados ou assinalam indisponibilidade.
- `engine/runtime_discovery.py`: deteção Python/venv, npm e browser ignora origens externas mesmo quando há symlinks intermédios.
- `tests/test_phase6_isolation.py`: 6 casos de regressão novos; fixture antiga de CLI privada ajustada para provar contenção física.
- `install/vps-phase6-audit.py`: **apenas diagnóstico**, executado por SSH existente através do workflow Ferrari. A versão do script usada na auditoria alargada está no ramo após a release ativa; não foi instalada como código da release de produção.

## Ferramentas ainda não detetadas como privadas

**9/56 em falta na shortlist privada:** `ytdlp`, `librecad`, `qgis`, `audacity`, `obs`, `solvespace`, `synfig`, `openshot`, `penpot`.

Apenas o facto de uma cópia existir em `/usr/bin` não a torna dependência Ferrari e **não autoriza** o fallback ao sistema. Se for necessário integrar uma destas capacidades, criar primeiro fornecedor/execução dentro da pasta Ferrari e certificar saída real; caso contrário, classificá-la como indisponível. Penpot não foi detetado nem como aplicação global nesta auditoria de 16 nomes.

## Dezasseis aplicações globais — classificação responsável

A presença global foi confirmada para estes 16 candidatos históricos, **mas não foi comprovado que pertençam exclusivamente ao Ferrari**:

| Também detetado no Ferrari privado | Só aplicação global detetada (sem equivalente privado identificado na shortlist) |
|---|---|
| `libreoffice`, `ansible`, `gimp`, `blender`, `kdenlive`, `darktable`, `openscad`, `calibre` | `ytdlp`, `librecad`, `qgis`, `audacity`, `obs`, `solvespace`, `synfig`, `openshot` |

A fotografia de processos conseguiu ler apenas **3 processos** em `/proc/*/exe` e não encontrou programas da lista ativos nesse momento. **Isto não prova ausência de consumidores**. Nenhum item pode ser eliminado até haver mapeamento de pacote/instalador, serviços, consumidores, dependências e ensaio reversível. A classificação de propriedade de recursos partilhados e noutros projetos também faz parte da Fase 9, mas uma eventual remoção futura do Ferrari não pode depender destes pacotes.

## Limitações da prova e porta de saída em falta

1. O `ldd` cobriu 33 binários ELF privados selecionados, com as bibliotecas transitivas observadas no ambiente privado. **Não certifica** bibliotecas carregadas dinamicamente por plugins ou linguagens interpretadas, Python/npm de todos os fornecedores, ficheiros/dados fora das pastas amostradas, nem todos os 56 candidatos.
2. A verificação dos symlinks foi limitada a diretórios superiores Ferrari selecionados: `sampled_symlinks=0` não equivale a uma auditoria recursiva completa de links e órfãos.
3. Os 16 programas globalmente disponíveis e quaisquer consumidores não foram totalmente atribuídos. A segurança dos outros projetos foi monitorizada, mas o pós-teste não prova a separação física de cada projeto.
4. Para encerrar **integralmente** a Fase 6: auditar proprietários/consumidores de aplicações globais, todos os caminhos indiretos (shebangs, `PATH`, `LD_LIBRARY_PATH`, plugins e links relevantes), corrigir qualquer dependência Ferrari fora da pasta, eliminar apenas resíduos comprovadamente exclusivos e órfãos, preservar o Ubuntu base e voltar a certificar 40/40 + Skill→ZIP + saúde.

**Decisão:** **Fase 6 — progresso técnico certificado e release operacional PASS; fecho integral pendente**. Não iniciar Fase 7 automaticamente nem declarar 10/10. PR [#64](https://github.com/martaxi-boss/skill-universal/pull/64) permanece draft e sem merge para `main`.
