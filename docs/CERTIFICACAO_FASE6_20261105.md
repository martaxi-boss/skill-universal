# Certificação final da Fase 6 — Ferrari / Skill Universal Ubuntu

**Data da prova final:** 05/11/2026. **VEREDITO: PASS — isolamento físico do projeto Ferrari certificado no âmbito observado.** Fase 6 de isolamento do Ferrari encerrada. O presente certificado **não** é uma certificação 100% de toda a VPS, nem converte programas globais do Ubuntu em dependências do Ferrari.

## Instalação e correspondência GitHub ↔ VPS

- **Repositório canónico:** `martaxi-boss/skill-universal`. **Diretório real:** `/srv/projects/skill-universal/`. Motor, releases, runtimes Python/Node/Java, executores externos, venvs, npm, ferramentas e caches específicas pertencem a essa pasta.
- **Release `current` comprovada:** `146145d5ada9c13e368df18727e4dbf4f5807664`.
- **Fallback preservado:** `40c0e1cdf31b1fe9589ad8be90e5eac06eec2856`. As duas releases anteriores `87969badbde0a77c2c181bb9605357d51a4a30c0` e `62f862cdf9727842546a244a3e4ec19dd8bc82f4` foram removidas depois de pré-visualização e confirmação de não utilização; não confundir estes SHA com o fallback atual.
- **Branch certificada GitHub:** `isolation/20261105-private-executors-only`, PR [#64](https://github.com/martaxi-boss/skill-universal/pull/64) mantida **draft/sem merge**. O SHA da release VPS é intencionalmente imutável; as auditorias, scripts de migração e documentação posteriores são versionados no mesmo repositório e invocados por SHA fixo através do workflow já existente em `martaxi-boss/VPS`.
- Nenhum coordenador novo na VPS, nenhuma instalação por APT global para o Ferrari, nenhum novo fornecedor partilhado, nenhum ajuste ao SSH nem ao Supervisor.

## Matriz de certificação real

| Requisito | Evidência | Resultado |
|---|---|---|
| CI fonte e regressões da Fase 6 | Ferrari [#42091895647](https://github.com/martaxi-boss/skill-universal/actions/runs/42091895647) e [#42091906947](https://github.com/martaxi-boss/skill-universal/actions/runs/42091906947), `fa832a71b7164e5163b89d14ee757bdba3b96f72` | **255 testes PASS**, sem enfraquecer bloqueios |
| Release privada e rollback | VPS [pré-teste #42078448805](https://github.com/martaxi-boss/VPS/actions/runs/42078448805), [ativação #42078597765](https://github.com/martaxi-boss/VPS/actions/runs/42078597765), [certificação de rollback F5 #42068780199](https://github.com/martaxi-boss/VPS/actions/runs/42068780199) | **PASS**, release F6 ativa, F5 intacta |
| 40 ações tipadas, runtimes e 47/56 candidatos privados detetados | [Skill → GitHub → VPS → ZIP #42092496058](https://github.com/martaxi-boss/VPS/actions/runs/42092496058), `report.json.status=completed` + `artifacts/inventory.json` | **PASS:** 40/40 ações privadas, Python/Node/Java privados e 47/56 selecionados detetados |
| Bibliotecas dinâmicas dos executores ELF | [Auditoria de 33 executáveis #42079545679](https://github.com/martaxi-boss/VPS/actions/runs/42079545679) | **PASS no âmbito amostrado:** 1 447 resoluções privadas, 13 Ubuntu base, 0 bibliotecas de aplicação externas ou em falta |
| Higiene de releases e temporários | [Preview #42087327564](https://github.com/martaxi-boss/VPS/actions/runs/42087327564) → [apply #42087599243](https://github.com/martaxi-boss/VPS/actions/runs/42087599243) | **PASS:** duas releases antigas excluídas, **2 719 744 bytes adicionais livres medidos**, 0 diretórios temporários elegíveis, atual/fallback preservados |
| Sete ambientes Python usam somente runtime privado | [Preview #42089682145](https://github.com/martaxi-boss/VPS/actions/runs/42089682145) → [apply #42089823880](https://github.com/martaxi-boss/VPS/actions/runs/42089823880) | **PASS:** **21 symlinks + 7 configurações** ajustados, **7/7** ambientes arrancaram e confirmaram `prefix`, `base_prefix` e interpretador dentro do Ferrari |
| Quatro scripts Python e 13 links obsoletos | [Preview válida #42092208327](https://github.com/martaxi-boss/VPS/actions/runs/42092208327) → [apply #42092331962](https://github.com/martaxi-boss/VPS/actions/runs/42092331962) | **PASS:** quatro shebangs apontam para o Python privado, incluindo opções originais; treze ligações **já quebradas** de recursos opcionais Ferrari removidas, restantes ficheiros preservados |
| Varrimento profundo integral dos diretórios Ferrari escolhidos | [VPS #42088052659, **tentativa 3**](https://github.com/martaxi-boss/VPS/actions/runs/42088052659), JSON pós-limpeza | **PASS:** **315 441 entradas**, **436 symlinks**, **0 externos**, **0 quebrados**, **0 para Python global**, **4 shebangs para Python privado**. `complete_under_budget=true` |
| Provas funcionais de programas com shebang alterado | [Ansible inventário JSON #42092622311](https://github.com/martaxi-boss/VPS/actions/runs/42092622311), [Calibre Markdown→EPUB #42092650850](https://github.com/martaxi-boss/VPS/actions/runs/42092650850) | **PASS:** ambas as ações concluídas com `response.zip`; `hosts.json` e EPUB verdadeiros devolvidos |
| Saúde dos serviços após a fase | [VPS #42092526699](https://github.com/martaxi-boss/VPS/actions/runs/42092526699), [issue #352](https://github.com/martaxi-boss/VPS/issues/352) | **PASS:** `AUDIT_ONLY`, `protected_services_unchanged=true`, `health_after=true`, sem cache elegível ou dados de aplicações eliminados |
| Ausência de atalho legado Ferrari | Auditoria privada #42088052659 | **PASS:** `historical_alias=absent` |

Os scripts de intervenção foram fixados por SHA no workflow de administração Ferrari em `martaxi-boss/VPS`, com pedidos explícitos de pré-visualização e aplicação, verificação `current` antes/depois e fallback obrigatório. A migração dos venvs e a correção de links mantêm metadados de recuperação na própria `.runtime/`. Os resultados dos comandos GitHub não substituem a evidência operacional: os IDs acima incluem os testes reais.

## Limites e responsabilidade de limpeza da VPS

**Dezasseis programas APT globais continuam presentes no Ubuntu**: `ansible-core`, `audacity`, `blender`, `calibre`, `darktable`, `gimp`, `kdenlive`, `librecad`, `libreoffice-common`, `obs-studio`, `openscad`, `openshot-qt`, `qgis`, `solvespace`, `synfigstudio` e `yt-dlp`. O inventário `dpkg-query` atribuiu o pacote de cada executável, mas **não provou o consumidor ou proprietário exclusivo da instalação**. Por isso, não foram desinstalados; isso não constitui dependência operacional das 40 ações privadas Ferrari e não compromete o isolamento acima. Classificar e, se seguro, eliminar globalmente estes pacotes pertence à **Fase 9 — auditoria transversal de toda a VPS**, sem alterar por acidente PINK, Telegram, FADEGO, Low Cost, Project Leader ou os serviços base.

**Nove candidatos selecionados não foram detetados em instalação privada**: `ytdlp`, `librecad`, `qgis`, `audacity`, `obs`, `solvespace`, `synfig`, `openshot` e `penpot`. São declarados indisponíveis no Ferrari; integração funcional futura é matéria da Fase 8, não uma razão para recorrer silenciosamente aos binários globais.

As 315 441 entradas correspondem aos diretórios privados Ferrari cobertos pelo auditor. Não são uma varredura de todos os ficheiros do Ubuntu nem uma prova de execução completa das 56 ferramentas ou de todos os plugins opcionais. Linux mantém necessariamente kernel, loader, shell e bibliotecas fundamentais do SO. O inventário geral de `/opt` já esteve incompleto, por isso **a VPS inteira não recebe a classificação 100% limpa**; isso fica na Fase 9.

## Decisão

**Fase 6 = CERTIFICADA, PASS no âmbito de isolamento e higienização do próprio Ferrari.** Todos os executores certificados, os 7 venvs, os 4 launchers corrigidos, a varredura total das raízes Ferrari selecionadas, a resposta da Skill, o fallback e a saúde pós-limpeza passaram. **A Fase 7 ainda não foi iniciada.** A manutenção dos 16 APT globais é uma reserva explícita de segurança e pertence ao trabalho transversal da Fase 9, não uma autorização para instalações fora da pasta Ferrari.
