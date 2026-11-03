# Higienização física e análise de duplicações — Ferrari VPS Ubuntu

**Data da evidência:** 03/11/2026 UTC. **Âmbito:** apenas Motor Ferrari próprio em /home/ubuntu/.local/share/motor-ferrari; análise das instalações globais e de outros projetos somente de leitura.

## Provas reais, não previsões

- [Inventário completo VPS #41700386577](https://github.com/martaxi-boss/VPS/actions/runs/41700386577), SUCCESS: tamanhos por diretório Ferrari e versões principais de venvs privados. Inventário anterior [#41673621836](https://github.com/martaxi-boss/VPS/actions/runs/41673621836) confirma propriedade geral e serviços.
- [Higienização física VPS #41701443735](https://github.com/martaxi-boss/VPS/actions/runs/41701443735), SUCCESS: auditoria prévia, aplicação delimitada, POSTCHECK e estado de serviços comparado.
- [REA privado após limpeza #41701860486](https://github.com/martaxi-boss/VPS/actions/runs/41701860486), SUCCESS: pedido real Skill→GitHub→VPS→ZIP, action rea-elf-notes, status completed, executor privado correto, artefacto rea-elf-notes.json.
- [Motor Ferrari #41671631900](https://github.com/martaxi-boss/VPS/actions/runs/41671631900): release 6c93a392dfe9a02d7ccfef9d47317c9685976484, 139 testes PASS antes desta limpeza.
- Código de limpeza exclusivamente Ferrari: install/ferrari-cache-hygiene.py, integrado na [PR #29](https://github.com/martaxi-boss/skill-universal/pull/29), após **146 testes PASS** em [CI #41700952440](https://github.com/martaxi-boss/skill-universal/actions/runs/41700952440).

## Fotografias de utilização do disco, por diretório

| Diretório do Ferrari | Bytes medidos antes da limpeza |
|---|---:|
| Ferrari completo | 13 312 897 024 |
| .runtime (total) | 10 453 159 936 |
| .runtime/venvs | 6 798 598 144 |
| .runtime/venvs/extended/comfyui | 2 677 559 296 |
| .runtime/venvs/extended/docling | 1 896 730 624 |
| .runtime/npm (programas instalados) | 2 358 177 792 |
| .runtime/npm/ruflo | 1 538 969 600 |
| .runtime/npm/rea | 288 411 648 |
| .runtime/npm-cache (cache, não instalação) | 984 453 120 |
| .runtime/npm-cache/_cacache (elegível) | 984 383 488 |
| .runtime/browsers | 291 356 672 |
| tools (Ghidra, FreeCAD, etc.) | 2 323 968 000 |
| runtimes (Node/Java privados) | 530 395 136 |
| releases (código atual + recuperação) | 5 365 760 |

Os grupos estão aninhados: **não somar linhas filhas às linhas pai**, pois isso duplicaria contabilização.

## Limpeza que foi efetivamente realizada

**Removido apenas:** /home/ubuntu/.local/share/motor-ferrari/.runtime/npm-cache/_cacache (downloads npm reutilizáveis, não programas instalados).

- Espaço livre antes: 14 000 500 736 bytes.
- Espaço livre depois: 14 984 884 224 bytes.
- **Libertados: 984 383 488 bytes (~939 MiB).**
- REA/Node/Java/Apktool/Ruflo preservados e Smoke POSTCHECK PASS.
- Estados dos serviços fadego-staging, lowcost-europa, pink-iptv-backend, pink-vpn e pm2-root comparados sem alteração.
- A limpeza foi feita sem sudo na VPS, pelo utilizador proprietário Ferrari, com verificação de diretórios e symlinks. Nenhum outro projeto foi alvo de limpeza.
- O workflow temporário de manutenção foi removido de martaxi-boss/VPS após SUCCESS: [commit de remoção fcb03a3](https://github.com/martaxi-boss/VPS/commit/fcb03a3f890cd6d4e17e54d2df1afab5dcfc9493).
- A cache npm poderá voltar a crescer quando forem efetuadas novas instalações.

## Dependências repetidas encontradas: PRESERVAR, não eliminar

| Repetição ou instalação paralela | Prova | Tratamento |
|---|---|---|
| PyTorch nos ambientes ComfyUI e Docling | Ambos indicam torch 2.15.0+cpu e possuem ficheiro libtorch_cpu.so de 440 280 512 bytes; a igualdade do conteúdo ainda não foi confirmada por hash | **Preservar ambas as instalações**. Cada venv tem dependências isoladas. A remoção cega quebraria programas |
| NumPy, Pydantic e outras bibliotecas em vários venvs | Inventário de versões mostra repetições entre comfyui, docling, gradio, prefect, streamlit e faster-whisper | Preservar até compatibilidade e dependências comprovadas; eventual consolidação requer novos testes de integração |
| Node global e Node privado Ferrari | /usr/bin/node e runtimes/node-22.23.4; versões independentes | **Preservar Node privado**; o global poderá servir outros serviços |
| Java global e JDK 25 Ferrari | /usr/bin/java e runtimes/jdk-25.0.5_8 | **Preservar JDK 25 privado**; Ghidra/Apktool usam-no |
| Apktool global e Apktool Ferrari 3.0.3 | /usr/bin/apktool e tools/apktool-3.0.3 | **Preservar o privado**; não desinstalar global sem auditoria dos restantes utilizadores |
| REA Ferrari e projetos REA anteriores | REA Ferrari em .runtime/npm/rea; outras árvores separadas na VPS | Preservar tudo até teste integral de independência e plano de remoção |

Existem árvores externas ao Ferrari que ocupam espaço, mas **não foram modificadas nem declaradas lixo**: /home/ubuntu/rea-final-runtime (4 430 053 376 bytes), /home/ubuntu/.local/share/rea-chatgpt-trial (2 529 660 928 bytes) e /opt/android-sdk (14 708 350 976 bytes). É preciso atribuir cada árvore ao respetivo projeto e confirmar processos/utilizadores antes de decidir qualquer remoção.

## Regeneracao e segunda limpeza da cache npm em 2026-11-03

A cache de downloads npm voltou a crescer durante instalacoes/testes posteriores, apesar da limpeza inicial. Foi feita uma segunda limpeza **somente dentro do Ferrari**, ja fisicamente em `/srv/projects/skill-universal`, com a release ativa `c5b07ed225299ad80aa2d46c28441d17f281f695`.

- [Auditoria sem remocao #41722218452](https://github.com/martaxi-boss/VPS/actions/runs/41722218452): 326 848 512 bytes na cache `.runtime/npm-cache/_cacache`, REA/Apktool/Node/Java/Ruflo privados confirmados.
- [Aplicacao #41722397677](https://github.com/martaxi-boss/VPS/actions/runs/41722397677): script `install/ferrari-cache-hygiene.py --apply` executado via REA como utilizador `ubuntu`, codigo interno zero e settlement quiesced.
- **Espaco livre recuperado nesta limpeza: 326 848 512 bytes**. Espaco livre final medido nesta execucao: 16 888 692 736 bytes.
- As dependencias instaladas, venvs, releases e restantes projetos foram preservados.

Esta segunda limpeza e um novo evento apos regeneracao da cache; ao analisar a ocupacao atual do disco, nao somar resultados historicos como se nunca tivesse havido crescimento de cache entre execucoes.

## Estado e próxima ação

- **PASS:** inventário de tamanhos Ferrari; remoção segura da cache npm privada; proteção dos executores Ferrari; teste REA real após limpeza.
- **PARCIAL:** classificação de duplicações entre venvs e software global. Detetadas as principais repetições, mas não houve prova de quais ficheiros podem ser desinstalados sem impacto nem uma auditoria de hashes e dependentes de todos os binários.
- **PENDENTE:** prova de independência integral do REA antigo, fornecedores adicionais e catálogo completo; planos de backup/rollback e autorização de desinstalação do legado.

**Não anunciar higienização profunda de toda a VPS ou remoção do REA antigo como certificadas.** A execução comprovada nesta fase foi delimitada ao Ferrari, com limpeza real e recuperação de espaço mensurável, sem mexer nos outros projetos.
