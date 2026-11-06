# Ferrari — Ponto 3: faster-whisper em CPU

**Objetivo:** reconhecer áudio e gerar TXT/SRT/JSON com o Ferrari instalado no Ubuntu, sem fornecedores pagos, dependências partilhadas, serviços permanentes, GPU, ou alterações ao GitHub–VPS existente.

## Verificação real da VPS — 06/11/2026

[VPS #42169726233](https://github.com/martaxi-boss/VPS/actions/runs/42169726233) **SUCCESS**, inventário somente leitura:

- Projeto privado `/srv/projects/skill-universal/`; release `a266b25e06a9c8acf1fdc940d22b99070cd17ded` ativa (mantida).
- `.runtime/venvs/extended/faster-whisper/`: `faster-whisper==1.2.1`, `ctranslate2==4.8.5`, `av==19.0.2`, `numpy==2.5.4`, `tokenizers==0.23.3`. Python do próprio Ferrari em `runtimes/python3.12/`.
- 4 CPUs lógicas, ~8 GB RAM, sem swap, 39,57 GiB livres. O modelo ainda não estava na pasta do Ferrari.

## Modelo CPU privado

Repositório oficial [Systran/faster-whisper-tiny](https://huggingface.co/Systran/faster-whisper-tiny), língua multilingue (inclui português), **licença MIT**, formato nativo **CTranslate2**, commit imutável `d90ca5fe260221311c53c58e660288d3deb8d356`. `model.bin` SHA256 upstream `dcb76c6586fc06cbdac6dd21f14cfd129cc4cdd9dce19bf4ffa62e59cbe6e6d1`. O reconhecimento em português *não* fica automaticamente certificado por um teste de áudio inglês.

Instalação atómica, somente no Ferrari, em `.runtime/models/faster-whisper-tiny-d90ca5fe/`, quatro ficheiros de dados explicitamente permitidos (model.bin, tokenizer.json, vocabulary.txt, config.json); hashes registados e verificados no manifesto privado `FERRARI_PROVENANCE.json`. Não instalar novamente o faster-whisper nem criar cache noutro diretório. Installer: `install/vps-faster-whisper-tiny-model.py --apply|--check`.

## Prova de áudio real

Teste com amostra JFK FLAC do próprio [SYSTRAN/faster-whisper](https://github.com/SYSTRAN/faster-whisper/blob/2a3a857737d17d974f30d818ebec69ce11929e5c/tests/data/jfk.flac), fixada no commit Git `2a3a857737d17d974f30d818ebec69ce11929e5c` e verificada por Git blob SHA1 `e44b7c13897eae7f78beb220c61fe77429a3961d`, 1.152.693 bytes. O ficheiro de áudio entra somente numa pasta temporária privada que é removida, sem serviços externos de transcrição. `WhisperModel` usa `device='cpu'`, `compute_type='int8'`, `cpu_threads=2`, `num_workers=1` e `local_files_only=True`.

Escopo systemd temporário `MemoryMax=2G`, `CPUQuota=150%`, `TasksMax=128`; timeout definido pelo workflow, sem processo residente. A saída só será marcada **PASS** quando houver texto reconhecível esperado do discurso, língua e tempos válidos, `transcript.txt`, `subtitles.srt`, `report.json` e hashes validados pelo runner GitHub. Testar inglês não certifica automaticamente sotaques, outras línguas, material longo nem qualidade de produção.

## Higienização e proteção

A release `current` fica inalterada. Não alterar os outros projetos nem a ponte, nem criar outra Skill. Apagar workflows e pedidos pontuais de GitHub Actions após a prova, manter modelo privado com proveniência e artefactos verificados, sem remover o motor. Instalação da Skill do ChatGPT só no fecho geral, por decisão do proprietário.

**Estado:** por preencher apenas com a evidência real da VPS; código e testes de CI, sem inferir sucesso do modelo antes da execução.

## Resultados preliminares e correção de compatibilidade

- [VPS #42170272965](https://github.com/martaxi-boss/VPS/actions/runs/42170272965): **modelo privado instalado e verificado**, modelo.bin exato 75.538.270 bytes SHA256 PASS; áudio FLAC público Git blob PASS; `WhisperModel` carregado em CPU. A inferência não chegou a produzir texto: `faster-whisper==1.2.1` chama `av.open(..., metadata_errors='ignore')`, argumento que já não é aceite pelo PyAV privado `av==19.0.2`. Release ativa preservada. Não declarar transcrição concluída com base neste run.
- Correção sem alteração de dependências: usar o próprio PyAV 19 para descodificar o FLAC em PCM mono a 16 kHz, converter para array NumPy float32 e entregar diretamente ao `WhisperModel.transcribe(array)`; este formato de entrada é suportado pelo faster-whisper e contorna o argumento descontinuado. Manter o modelo instalado e não repetir downloads. Guardas de som não silencioso, amostras finitas e pelo menos um segundo de áudio.
- A transcrição, SRT/JSON e limpeza transitória exigem novo run real na VPS e inspeção dos artefactos.
