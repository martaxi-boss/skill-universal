# Ferrari F14 — Fecho auditável de quatro aplicações GUI (08/11/2026)

**Estado final da fase: auditoria concluída com provas reais individuais, sem declarar sucesso para capacidades não exercitadas.** Até à data, **três aplicações têm um fluxo funcional real certificado** (SolveSpace, Synfig e OBS com finalização FFmpeg); **Audacity 4.0.2 permanece sem edição automatizada certificada**. GUI interativa completa destas aplicações não foi certificada.

## Fontes imutáveis

- [Ferrari PR #175](https://github.com/martaxi-boss/skill-universal/pull/175): código de ensaio inicial `install/vps-f14-final-optional-gui-certify.py`, CI push e PR PASS.
- [VPS #42515392261](https://github.com/martaxi-boss/VPS/actions/runs/42515392261): **audit_complete**, 4 ferramentas avaliadas, **2 PASS / 2 not_certified** no primeiro ensaio. Artefacto ZIP `ferrari-universal-42515392261`.
- [Ferrari PR #176](https://github.com/martaxi-boss/skill-universal/pull/176), [VPS #42516027816](https://github.com/martaxi-boss/VPS/actions/runs/42516027816): prova OBS com 398 fotogramas descodificados, mas MKV incompleto — corretamente *não suficiente* para afirmar um vídeo finalizado.
- [Ferrari PR #177](https://github.com/martaxi-boss/skill-universal/pull/177), [VPS #42516534292](https://github.com/martaxi-boss/VPS/actions/runs/42516534292): **PASS final** do fluxo OBS → FFmpeg privado → MP4 integralmente verificável. Artefacto `ferrari-universal-42516534292`.

## Classificação por programa

| Programa privado | Resultado funcional efetivamente provado | Limite explícito |
|---|---|---|
| **SolveSpace 3.1** | **PASS**: CLI privada abriu fixture pública `.slvs` (4 832 bytes) e exportou SVG real (2 242 bytes; SHA-256 `fa6981ba28771bc2d917dd1e54afd41c1c14f6d8260c626146bf63ec9fdff3ee`) | Não equivale a GUI integral ou todos os constrangimentos de CAD |
| **Synfig 1.5.5** | **PASS**: `.sif` animado e dois PNG reais de 505 e 607 bytes, hashes SHA-256 distintos `2c161d269ca18d10fc1a3fb816c79c1b84d708447f70499b3269aaaabfb94b14` e `44aa1aad653f47b6b0cac8d26e83323a0dedcc223d9943867ec51158e61423fd` | Não valida toda a interface nem projetos complexos |
| **OBS 32.2.2 + FFmpeg privado** | **PASS** para um fluxo de vídeo de canvas inteiramente sintético: MKV fonte com 398 frames legíveis, seguido de MP4 final **46 185 bytes, 400 frames, 13,333333 s, 320×180**, FFprobe sem erros e SHA-256 `0c170035a8ca4e98ca2ef7d5b9e9269f17d717e78416bbfad8aa15258e0bb50e` | O **MKV nativo OBS não ficou finalizado**; o workflow de pós-processamento com FFmpeg é necessário. Não certifica streaming, câmara, microfone, captura do ecrã ou toda a GUI |
| **Audacity 4.0.2** | **NOT_CERTIFIED** para edição automatizada nesta arquitetura: a versão privada existe, mas não dispõe do mecanismo de macros/script-pipe utilizado em versões anteriores | Não declarar uma API inexistente ou substituir silenciosamente a versão. Edição manual GUI não foi testada |

**OBS — prova de qualidade do artefacto final:** a gravação sintética original criou MKV com cerca de 9,9 MB, mas o FFprobe indicou `File ended prematurely` e ausência de duração. Em vez de aceitar falsamente os 398 frames como vídeo final, o Ferrari descodificou o fluxo com o FFmpeg privado já instalado, produziu um **novo MP4 finalizado** e o submeteu novamente ao FFprobe. O ficheiro MP4 contém um stream de vídeo, 400 frames descodificáveis, duração positiva e cabeçalho MP4 válido. O SHA-256 acima pertence **ao MP4 final**, não ao MKV inicial. Os ficheiros sintéticos foram eliminados ao fim da execução; o artefacto GitHub contém os relatórios JSON verificáveis, não os vídeos originais.

## Integridade da VPS e do catálogo

- Release ativa: `3f0ba44b7d8475a74a63c6010d1e27063c04bf1e`.
- Fallback: `427e1c33c6d10ca8ecd2103861adccd3d552c381`.
- 8/8 serviços protegidos antes/depois, **sem instalação APT, sem alteração de outros projetos, sem ficheiros QA permanentes e sem coordenador na VPS**.
- Catálogo universal **173 programas, 280 funções, 458 entradas**; estas certificações **não** adicionam operações falsas e a classificação de suporte/callable não é inflacionada.
- A IA anfitriã continua a orientar Ruflo e os papéis especializados, sem um modelo LLM adicional por agente.

## Limites do fecho

**F14 está concluída como fase de auditoria, não como aprovação integral das interfaces gráficas.** O trabalho comprovado é o indicado por programa e por formato. O Audacity 4.0.2 necessita de uma via de automação realmente suportada ou QA GUI interativa; não se considera defeito de instalação nem se autoriza downgrade. A gravação nativa OBS precisa de finalização correta se for exigida sem pós-processamento. Não apagar releases/rollback nem outros repositórios como parte deste relatório.

O F12/13 previamente certificado mantém-se válido: [FreeCAD + yt-dlp #42511331936](https://github.com/martaxi-boss/VPS/actions/runs/42511331936), [OpenShot real #42513141634](https://github.com/martaxi-boss/VPS/actions/runs/42513141634), [inventário pós-F13 #42513747602](https://github.com/martaxi-boss/VPS/actions/runs/42513747602).
