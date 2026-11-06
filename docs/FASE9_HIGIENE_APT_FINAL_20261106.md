# Ferrari — Fecho da higienização APT nominal e limites da Fase 9

Data da fotografia: **6 de novembro de 2026**, VPS Ubuntu 24.04.

## Resultado operacional verificado

O Ferrari conserva **um só catálogo persistente**, `engine/catalog.json`, com 173 programas, 272 interfaces de função (as 220 REA na mesma lista), 3 dependências centrais declaradas e 2 fornecedores: **450 registos de tipos diferentes**. A release ativa é `7bf6dcecf15da26502c5969b5eee54d5e116fc32`, com fallback `952b0a75ba798471b07053677d53791bd078ed56`. [Prova de ativação #42294843737](https://github.com/martaxi-boss/VPS/actions/runs/42294843737) e [inventário da Skill #42297678715](https://github.com/martaxi-boss/VPS/actions/runs/42297678715) PASS: 55/55 programas Ubuntu da seleção detetados, 272/272 interfaces selecionáveis e 40/40 ações disponíveis.

### Os oito APT restantes da auditoria anterior

Nomes observados antes: `yt-dlp`, `librecad`, `qgis`, `audacity`, `obs-studio`, `solvespace`, `synfigstudio` e `openshot-qt`.

- [Auditoria real #42299686585](https://github.com/martaxi-boss/VPS/actions/runs/42299686585): inspecionou a seleção dos oito APT, executou `apt-get -s purge` **sem eliminar**, percorreu sem erros os diretórios de código/configuração dos **sete projetos independentes** (incluindo ficheiros grandes do FADEGO) e não encontrou referências aos nomes pesquisados. Os oito APT já constavam como não instalados; a simulação já não propôs uma remoção de oito pacotes, precisamente porque estavam ausentes. A auditoria assinalou explicitamente que a certificação de GUI/dependências é incompleta.
- [Segunda opinião independente #42300665770](https://github.com/martaxi-boss/VPS/actions/runs/42300665770): `dpkg -s` e `dpkg-query -W` concordaram para **8/8 nomes**. **Instalados: 0/8.** O artefacto JSON confirma `apt_changes=0`, `file_changes=0`, `other_projects_modified=false`, os 8 serviços ativos, a release e o fallback.
- Os **outros oito programas globais iniciais** (Ansible, Blender, Calibre, Darktable, GIMP, Kdenlive, LibreOffice, OpenSCAD) foram removidos e testados anteriormente em [#42225950692](https://github.com/martaxi-boss/VPS/actions/runs/42225950692). Esta é uma prova histórica de remoção, não uma nova segunda leitura simultânea dos dezasseis nomes.

**Conclusão restrita:** não existe nada a purgar nos **oito nomes finais** conforme a leitura da VPS de 06/11; nenhuma purga foi executada para produzir esse resultado. As verificações não estabelecem a data ou a autoria da sua remoção anterior. Não fazer `apt autoremove` nem purgar bibliotecas do Ubuntu apenas por semelhança de nomes.

## Higiene do catálogo e releases

O GitHub e a release ativa não contêm segundo catálogo REA ou ficheiros JSON de catálogo antigos. O leitor `engine/catalog_registry.py` constrói vistas efémeras do **mesmo** `engine/catalog.json`. [Higiene #42295330408](https://github.com/martaxi-boss/VPS/actions/runs/42295330408) eliminou uma release sem estado; [segunda limpeza #42297182419](https://github.com/martaxi-boss/VPS/actions/runs/42297182419) retirou nove cópias antigas auditadas após prova de pastas `.runtime` vazias [#42296172655](https://github.com/martaxi-boss/VPS/actions/runs/42296172655), libertando 19,25 MB adicionais. A release atual, fallback, runtimes e 8/8 serviços permaneceram intactos. [Inventário final #42297678715](https://github.com/martaxi-boss/VPS/actions/runs/42297678715) PASS.

## Limites que impedem declarar o Ferrari funcionalmente 100%

- **GUI e edição real:** arranque de seis aplicações em Xvfb temporário foi observado; não equivale a certificar desenho/edição/som/vídeo/gravação/transmissões. Há ensaios sintéticos 2D CAD e QGIS certificados nos âmbitos citados no [relatório F9 original](FASE9_AUDITORIA_E_HIGIENIZACAO_20261105.md), mas não todos os formatos/funções.
- **QGIS/provedores opcionais:** a presença privada foi testada, porém o histórico identificou uma biblioteca opcional HDF5 em falta numa rota de inicialização. Não declarar todos os fornecedores ou modos GUI verdes.
- **Dependências transitivas do Ubuntu:** as três dependências centrais do catálogo não são inventário exaustivo de todas as bibliotecas; a ausência dos nomes APT de topo não autoriza remoção de pacotes auxiliares do sistema.
- **Outros projetos:** versões, worktrees e alterações locais do PINK e do IPTV VPN Bot já foram preservadas em auditorias anteriores; não fazer reset/deploy cruzado para simular alinhamento.
- **Skill instalada no ChatGPT:** GitHub e pacote ZIP atualizado não provam que a cópia atualmente instalada no cliente tenha sido substituída.

**Veredito:** **higienização de catálogo, snapshots Ferrari e oito nomes APT finais verificada**, motor universal operacional; **certificação funcional exaustiva de todas as ferramentas e higiene de bibliotecas globais transitivas ainda não certificadas**. Sem afirmação de 100%, sem falsos PASS e sem alterações nos outros projetos.
