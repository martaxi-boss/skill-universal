# Ferrari — Fase 8: quatro certificados Android adicionais e bloqueio físico separado

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

## Higiene e continuidade

**Sem deploy ou atualização da release em uso, sem instalação APT global na VPS, sem criar Skill, ponte, coordenador, serviço ou diretório fora do Ferrari.** As execuções escreveram apenas nas pastas de resultados próprias. A release ativa F7 `758e1b435317fa26277b332b75bc47c67910be81` e fallback F6 `146145d5ada9c13e368df18727e4dbf4f5807664` não foram promovidos nem removidos; auditar antes de declarar qualquer limpeza transversal.

**Próxima porta antes de declarar F8 completa:** ligar dispositivo Android físico autorizado, confirmar que a ligação e o APK são seguros e executar `android-adb-install-apk` por pedido Ferrari e confirmar instalação no dispositivo. Na ausência de tal dispositivo, manter honestamente **39/40, 1 hardware bloqueado**, sem avançar com declarações de 40/40.
