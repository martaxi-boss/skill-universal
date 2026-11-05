# Ferrari — Fase 8: quatro certificados Android adicionais e bloqueio físico separado

**ATUALIZAÇÃO DE FECHO — 05/11/2026:** a certificação F8 foi concluída **40/40** com instalação real por ADB privado do Ferrari num Android físico autorizado. Execução GitHub Actions [#42128892714](https://github.com/martaxi-boss/VPS/actions/runs/42128892714): `report.json.status=completed`, artefacto `adb-install.txt` com `Performing Streamed Install` e `Success`. A APK pública temporária `com.example.empty9patch` foi posteriormente desinstalada com `Success` em ConnectBot, sem alterar PINK IPTV. [Relatório de fecho](FASE8_FECHO_20261105.md). O texto restante abaixo documenta a **situação histórica anterior à ligação física** e não indica um bloqueio atual.


**Data: 05/11/2026. Estado: 39/40 ações tipadas provadas em execuções individuais reais, F8 NÃO encerrada.** Este certificado é restrito às quatro verificações abaixo e ao âmbito de executor privado. Não certifica instalação Android física, APK de produção, todos os 56 candidatos Ubuntu, interfaces GUI integrais, modelos externos ou todos os fornecedores MCP.

## Casos verificados na VPS e artefactos devolvidos

| Ação | Executável privado em `/srv/projects/skill-universal/` | Execução VPS | Validação do `response.zip` |
|---|---|---|---|
| `android-aapt2-manifest` | `/srv/projects/skill-universal/tools/android-cli-36.0.0/build-tools/36.0.0/aapt2` | [#42113835768](https://github.com/martaxi-boss/VPS/actions/runs/42113835768) | `apk-manifest-tree.txt` — AAPT2 leu manifesto AXML real: package app.hello.jni, minSdk 21, targetSdk 29 |
| `rea-android-resources` | `/srv/projects/skill-universal/.runtime/npm/rea/node_modules/.bin/rea` | [#42113866996](https://github.com/martaxi-boss/VPS/actions/runs/42113866996) | `rea-android-resources.json` — REA/Apktool 3.0.3 extraiu manifesto, SDK 21/29, pacote app.hello.jni, 5 ficheiros; sem strings.xml neste APK |
| `apktool-decode-resources` | `/srv/projects/skill-universal/tools/apktool-3.0.3/bin/apktool` | [#42114077392](https://github.com/martaxi-boss/VPS/actions/runs/42114077392) | `apktool-decoded` — Apktool 3.0.3 devolveu 5 ficheiros reais: manifesto XML, apktool.yml, smali, ELF ARM64 e manifesto AXML |
| `android-apksigner-verify` | `/srv/projects/skill-universal/tools/android-cli-36.0.0/build-tools/36.0.0/apksigner` | [#42114234808](https://github.com/martaxi-boss/VPS/actions/runs/42114234808) | `apk-signature.txt` — Apksigner Verifies: true; assinaturas v1 e v2 verdadeiras, v3/v4 ausentes; certificado Android Debug de teste RSA 1024 |

As quatro execuções terminaram em **SUCCESS** no GitHub Actions, com `report.json.status=completed`, ficheiro real correspondente e executor da árvore privada. Os artefactos foram descarregados e inspecionados, não apenas inferidos pelo código.

## Proveniência e limites da amostra

- Para AAPT2, REA Android e Apktool: `vitalnodo/apksign/fixture/app.unsigned.apk` (2.498 bytes), fixture público de código de demonstração, com AXML binário, DEX e biblioteca ARM64, sem conteúdos privados. O manifesto indica `app.hello.jni`, minSdk 21 e targetSdk 29; não há `res/values/strings.xml`.
- Para Apksigner: `iBotPeaches/Apktool@v3.0.1/brut.apktool/apktool-lib/src/test/resources/issue1157/issue1157.apk` (8.993 bytes), APK de teste com assinatura **v1 e v2 válidas**. Os esquemas v3 e v4 não constam; certificado de teste `Android Debug` RSA 1024. **Não** usar esta chave/assinatura para lançamento ou inferir certificação de segurança de produção.
- A primeira solicitação Apktool [#42113858985](https://github.com/martaxi-boss/VPS/actions/runs/42113858985) foi cancelada na fila GitHub sem prova; novo pedido isolado [#42114077392](https://github.com/martaxi-boss/VPS/actions/runs/42114077392) passou. O cancelamento não conta como falha de ferramenta nem prova de execução.
- `android-adb-install-apk`: ADB privado está detetado no inventário [VPS #42112873578](https://github.com/martaxi-boss/VPS/actions/runs/42112873578), mas **nenhum Android físico autorizado** foi demonstrado como ligado à VPS. Não houve chamada de instalação, nem simulador ou mock apresentado como dispositivo real. O teste real exige autorização e ligação segura do dispositivo.

## Pré-verificação PINK IPTV → ADB privado — 05/11/2026

**Execução real somente leitura:** [VPS #42116353813](https://github.com/martaxi-boss/VPS/actions/runs/42116353813) **SUCCESS**. O diagnóstico autenticado verificou as raízes `/srv/projects/pink-iptv/` e `/srv/projects/skill-universal/`, a presença do executável `tools/android-cli-36.0.0/platform-tools/adb` dentro do Ferrari e a disponibilidade dos serviços `pink-iptv-backend.service` e `pink-vpn.service` (**active**).

A procura na pasta PINK encontrou **2 ficheiros `.apk` acessíveis**; o candidato de modificação mais recente tinha **20 319 870 bytes**, SHA-256 `b734551c57f0ef38d736106f5d5cd9e11b9cc3cc3c277cf1c9d04e1e82aee208`. O comando de enumeração devolveu código 1 (acesso incompleto a alguma subárvore); **não afirmar que são todos os APKs** nem que o candidato é a release final instalada no telemóvel. Nenhum conteúdo foi lido para publicação.

O Ferrari executou `adb devices -l` com a sua cópia privada, estado temporário exclusivo em `skill-universal/.runtime/` e servidor isolado de teste, com pedido de encerramento no fim (sem inspeção independente dos processos após a execução): **código de saída 0, zero dispositivos em estado `device`**. Isto não comprova que nunca exista outro ADB remoto ou USB, apenas que **nenhum Android estava disponível na sessão privada inspecionada**. Não se executou `adb install`; a ação F8 `android-adb-install-apk` mantém-se **SEM CERTIFICAÇÃO INDIVIDUAL**.

O fluxo de teste foi removido após a verificação, no commit [`3e7187d`](https://github.com/martaxi-boss/VPS/commit/3e7187db4b0e44ebbcc5639bbd620d71187e8ae4). O workflow temporário foi removido, não foi configurado serviço ADB persistente nem transferidos ficheiros; o servidor de diagnóstico recebeu um pedido de encerramento sem read-back independente. Como `pink-iptv` é privado e `VPS` é público, e o envelope da Skill limita entradas a 2 MB, não foi publicado nem enviado um APK PINK de 20 MB em JSON/base64. Quando existir dispositivo autorizado e ligação privada, validar a identidade/versão do APK e só então copiar uma amostra de teste para armazenamento temporário privado do Ferrari com checksum, executar a instalação e verificar o resultado sem tocar na aplicação PINK em produção.

## Higiene e continuidade

**Sem deploy ou atualização da release em uso, sem instalação APT global na VPS, sem criar Skill, ponte, coordenador, serviço ou diretório fora do Ferrari.** As execuções escreveram apenas nas pastas de resultados próprias. A release ativa F7 `758e1b435317fa26277b332b75bc47c67910be81` e fallback F6 `146145d5ada9c13e368df18727e4dbf4f5807664` não foram promovidos nem removidos; auditar antes de declarar qualquer limpeza transversal.

**Próxima porta antes de declarar F8 completa:** ligar dispositivo Android físico autorizado, confirmar que a ligação e o APK são seguros e executar `android-adb-install-apk` por pedido Ferrari e confirmar instalação no dispositivo. Na ausência de tal dispositivo, manter honestamente **39/40, 1 hardware bloqueado**, sem avançar com declarações de 40/40.
