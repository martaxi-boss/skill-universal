# Auditoria de duplicações, limpeza global da VPS e decisão REA — 03/11/2026

**Âmbito da auditoria:** VPS Ubuntu, com análise das principais instalações e dos dois motores REA. **Não é uma certificação de equivalência integral.** Todos os valores e estados são snapshots de workflows reais identificados abaixo.

## Evidências auditáveis

- [Inventário global e cruzamento de instalações #41704276899](https://github.com/martaxi-boss/VPS/actions/runs/41704276899) — SUCCESS: diretórios, pacotes, dependências, hashes de bibliotecas, referências em configurações e processos.
- [Inventário e fornecedores REA #41704976569](https://github.com/martaxi-boss/VPS/actions/runs/41704976569) — SUCCESS: árvores vendor/optional, tentativa de comparação MCP e diagnósticos REA.
- [Diagnóstico detalhado do REA Ferrari #41705351869](https://github.com/martaxi-boss/VPS/actions/runs/41705351869) — SUCCESS de transporte; resultado funcional do doctor REA foi **healthy=false**.
- [Higienização global por procedimento pré-existente #41704431188](https://github.com/martaxi-boss/VPS/actions/runs/41704431188), [issue #317 encerrada](https://github.com/martaxi-boss/VPS/issues/317) — relatório CLEANED, **239 403 008 bytes de espaço adicional**; 2 915 ficheiros de cache elegíveis, 7 raízes auditadas; serviços inalterados, zero dados de aplicações ou sessões apagados.
- [Higiene Ferrari anterior #41701443735](https://github.com/martaxi-boss/VPS/actions/runs/41701443735) — **984 383 488 bytes** libertados da cache npm privada; REA/Ruflo/Java/Node/Apktool preservados.
- [REA real Ferrari após cache hygiene #41701860486](https://github.com/martaxi-boss/VPS/actions/runs/41701860486) — SUCCESS, ação rea-elf-notes via Skill e ZIP.
- [REA FINAL em uso #41704932726](https://github.com/martaxi-boss/VPS/actions/runs/41704932726) — execução do outro motor no mesmo dia. **Não se pode assumir que está desativado.**

## Duplicações e dimensões

| Instalação | Bytes usados | Classificação |
|---|---:|---|
| Ferrari integral, snapshot anterior à limpeza | 13 312 897 024 | **Preservar**; inclui os filhos abaixo |
| Ferrari .runtime/venvs/extended/comfyui | 2 677 559 296 | Ativo para possível ComfyUI; preservar |
| Ferrari .runtime/venvs/extended/docling | 1 896 730 624 | Pacotes de Docling; preservar |
| Ferrari .runtime/npm/ruflo | 1 538 969 600 | Ruflo privado; preservar |
| Ferrari .runtime/npm/rea | 288 411 648 | REA privado Ferrari; preservar |
| REA FINAL em /home/ubuntu/rea-final-runtime | 4 430 053 376 | Projeto independente **ainda utilizado** |
| REA chatgpt-trial em .local/share/rea-chatgpt-trial | 2 529 660 928 | Projeto distinto; proprietário/uso ainda por certificar |
| Fonte REA upstream em /home/ubuntu/rea-original-upstream-680 | 184 299 520 | Dados do projeto REA, não remover com Ferrari |
| Evidências REA upstream em /home/ubuntu/rea-original-upstream-680-evidence | 511 508 480 | Evidências, preservar sem validação de retenção |
| Android SDK global /opt/android-sdk | 14 708 350 976 | **Partilhável/uso por testar; não remover** |
| Gradle cache root /root/.gradle/caches | 1 517 600 768 | Cache de builds Android, não eliminar automaticamente |
| Android AVD root /root/.android/avd | 2 267 357 184 | Ambiente virtual Android, não considerar lixo |

**Duplicação por conteúdo confirmada:** duas cópias de `torch/lib/libtorch_cpu.so`, uma em ComfyUI e outra em Docling, com **440 280 512 bytes** cada, SHA-256 igual `afe839bc112b41f97b82776675a0fc44425f7d755c58db700fe75efee0a36170`, inodes distintos. **Não eliminar nem transformar em hardlinks**: o utilizador exige instalações independentes por projeto e venv.

Outras sobreposições com finalidades distintas: Java global Ubuntu vs JDK 25 privado Ferrari, Node.js global vs Node 22.23.4 Ferrari, Apktool global vs Apktool 3.0.3 privado, Ghidra 12.1.4 da árvore REA trial vs Ghidra 12.2 Ferrari e dependências Python/NPM de diferentes projetos. APT global não é instalação exclusiva de um só projeto. Não é possível determinar responsabilidade ou ausência de dependentes apenas por nomes/versões parecidos.

## Fornecedores REA — bloqueadores observados

No teste [#41705351869](https://github.com/martaxi-boss/VPS/actions/runs/41705351869):

- `rea doctor --provider ghidra --json` no REA privado Ferrari: saída JSON válida, processo com código 1, `healthy=false`.
- `ghidra`, `ghidra-platform`, `ghidra-architecture`, `ghidra-installation`, `ghidra-headless`, `ghidra-native_decompiler`, `ghidra-java` → `ok=true`.
- `ghidra-version` → **false**; `jadx` → **false**; `hopper-version`, `ida-registration`, `kuna-installation` → false (fornecedores opcionais/comerciais não obrigatórios).
- `rea providers --json` e `rea capabilities --json` produziram JSON com saída bem-sucedida.
- Os executáveis MCP do REA FINAL e Ferrari **arrancaram e permaneceram vivos no teste inicial**. A tentativa de `initialize/tools/list` não recolheu um catálogo comparável, devido a erro ou timeout da rotina de prova. Não concluir que os MCP estão avariados, mas também **não atribuir paridade de ferramentas**.
- O Ferrari expõe, na ponte Skill, **duas ações REA** certificadas (ELF e recursos Android), não um substituto demonstrado de todas as funções MCP do outro motor.

## Higienização realizada e limites

**Remoções reais nesta sequência:** só a cache npm privada Ferrari (984 383 488 bytes) e caches globais com mais de 24h de uma allowlist de sete raízes e guardas de segurança (239 403 008 bytes de ganho medido). **Total conjunto medido: 1 223 786 496 bytes (~1,14 GiB)**. O estado dos serviços foi preservado, sem apagar aplicações, dados, backups, chaves, fontes, repos, bibliotecas em uso, Android SDK, bases de dados ou o REA anterior.

As inspeções em `/etc/systemd/system`, `/etc/cron.d`, `/etc/supervisor/conf.d` e dumps PM2 não encontraram referências por texto aos diretórios selecionados do REA; não equivale a ausência de consumidores dinâmicos via GitHub Actions, e há workflows REA em execução no mesmo dia. A auditoria de ficheiros de grande dimensão por comparação universal de hash ou testes de dependência completos dos pacotes APT não pôde ser concluída; **não declarar higienização integral verde**.

## Decisão sobre a remoção do outro REA

**NO-GO: remoção do REA FINAL / de qualquer árvore REA anterior ainda não certificada.** A independência física do REA privado Ferrari e o teste ELF posterior PASS são necessários, mas não suficientes. O outro motor continua acessível em GitHub Actions, o doctor interno REA Ferrari dá `healthy=false` e não existe paridade MCP certificada.

Para autorizar uma remoção seletiva depois: (1) identificar exatamente qual a instalação REA antiga a desativar; (2) testar `rea doctor` e reconhecimento de JADX/Ghidra privados; (3) comparar ferramentas MCP e fornecedores reais, executar amostras ELF, APK/Smali, binários nativos e outras funções efetivamente utilizadas; (4) certificar o Ferrari em ambiente sem dependência das árvores antigas; (5) desativar as chamadas antigas e confirmar rollback/backup antes de qualquer eliminação; (6) fazer plano de remoção apenas dos caminhos exclusivos, sem tocar em APT globais nem outros projetos.

**Nada do REA antigo foi desinstalado.** O workflow de inventário voltou à versão compacta após os testes. As provas completas persistem nos GitHub Actions ligados acima.
