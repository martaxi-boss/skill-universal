# Ferrari — Ponto 2 / ComfyUI CPU e modelo privado

**Estado inicial confirmado em 06/11/2026** pela [VPS #42146994521](https://github.com/martaxi-boss/VPS/actions/runs/42146994521): ComfyUI v0.43.0 presente em `/srv/projects/skill-universal/tools/comfyui-v0.43.0`, venv `.runtime/venvs/extended/comfyui` com Torch CPU `2.15.0+cpu`. VPS com 4 CPUs lógicas, ~8 GB RAM, sem swap e 41,57 GiB livres.

## Tentativa inicial — modelo incompatível

Foi inicialmente escolhido **Segmind Tiny-SD** de [Hugging Face](https://huggingface.co/segmind/tiny-sd), variante de segurança [PR #6, commit 3d25de3e8d5aacf94ce91176f204e6d11d120315](https://huggingface.co/segmind/tiny-sd/tree/3d25de3e8d5aacf94ce91176f204e6d11d120315). Licença `creativeml-openrail-m` (gratuita sob condições de uso, não equivalente a domínio público ou ausência de restrições). Esta variante tem UNet reduzida e não foi reconhecida pelo ComfyUI v0.43.0; não foi certificada para gerar imagens.

Na primeira tentativa foram instalados pesos **SafeTensors, SHA256 verificado**, total ~1,06 GB (posteriormente removidos com prova #42149831403): `text_encoder/model.safetensors` (246 MB), `unet/diffusion_pytorch_model.safetensors` (647 MB) e `vae/diffusion_pytorch_model.safetensors` (167 MB). Não descarregar `.bin` / pickle. JSON de configuração por pin de revisão, não confiar em versões flutuantes.

## Layout e execução

- Código já existente: `tools/comfyui-v0.43.0/`
- Python já existente: `.runtime/venvs/extended/comfyui/`
- **Pesos certificados:** `tools/comfyui-v0.43.0/models/diffusers/sd15-fp16-f03de327/` (SD 1.5 padrão, SHA256 verificados); Tiny-SD foi removido por incompatibilidade
- Executável de instalação: `install/vps-comfyui-sd15-fp16-model.py --check|--apply`, via GitHub Actions/SSH administrativo limitado a esta pasta. Instalação atómica; recusar conflitos; limpar apenas staging próprio em caso de falha; sem APT, pip global, novo Docker, serviços públicos ou coordenador.
- Prova de imagem: `install/vps-comfyui-cpu-smoke.py` só dentro de escopo temporário `systemd-run --scope` com limite máximo de 5 GiB RAM e CPU 150%, timeout definido no workflow, sem porta pública. Deve gerar uma PNG de 256×256 com CLIP, KSampler e VAE ComfyUI reais, sem API externa.
- A prova não pode declarar sucesso apenas por existência de ficheiros/modelos; validar PNG, dimensões, metadados e hashes. O modo GUI, GPU, qualidade profissional e tempos reduzidos **não** são certificados por esta prova.
- A release Ferrari `current` e os restantes projetos permanecem intocados. O estado do modelo está na pasta privada Ferrari mesmo que a CI/Skill seja atualizada mais tarde.

## Higiene

Após PASS, remover workflows/pedidos administrativos **temporários** no repositório VPS. Manter a pasta de pesos com proveniência SHA e um relatório mínimo; não remover o runtime ou a release ativa e o seu fallback protegidos. Nunca eliminar pacotes Ubuntu globais, venv de outro projeto ou serviços protegidos durante esta tarefa.

**Estado de conclusão:** GERAÇÃO REAL PASS — [VPS #42149365272](https://github.com/martaxi-boss/VPS/actions/runs/42149365272). Higiene específica PASS — [VPS #42149831403](https://github.com/martaxi-boss/VPS/actions/runs/42149831403). Ver detalhes abaixo.


## Diagnóstico de incompatibilidade e correção (06/11/2026)

- [VPS #42147745661](https://github.com/martaxi-boss/VPS/actions/runs/42147745661): o Tiny-SD foi instalado e os 3 hashes passaram; a primeira prova falhou devido ao uso de `systemd-run --scope --wait`, combinação inválida. Não houve geração de imagem.
- [VPS #42147964610](https://github.com/martaxi-boss/VPS/actions/runs/42147964610): o `--scope` funcionou mas a prova detectou que o parser de argumentos do ComfyUI não tinha sido inicializado, levando à escolha incorreta de CUDA.
- [VPS #42148307043](https://github.com/martaxi-boss/VPS/actions/runs/42148307043): com a correção nativa do modo CPU (PyTorch `+cpu`), verificou-se uma incompatibilidade estrutural genuína: `Could not detect model type` para a UNet Tiny-SD *pruned*. **Não declarar Tiny-SD funcional no ComfyUI 0.43.0.**
- Alternativa de compatibilidade: modelo oficial [Stable Diffusion 1.5](https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5), commit `f03de327dd89b501a01da37fc5240cf4fdba85a1`, pesos UNet padrão, CLIP e VAE em três `.fp16.safetensors` com SHA256 conhecido, total aproximado 2,1 GB. Licença `creativeml-openrail-m` (ver regras de uso). Caminho privado novo `tools/comfyui-v0.43.0/models/diffusers/sd15-fp16-f03de327/` sem alterar o runtime, a release ativa ou outros projetos.
- A prova real reutiliza o **mesmo** ComfyUI e limites de cgroup; requer PNG 256×256, hash real e reporte. Se a memória for insuficiente, **parar sem aumentar as quotas**.
- Após certificação da alternativa, verificar ausência de consumidores e remover os **pesos Tiny-SD sem suporte** dentro da pasta Ferrari com guardas de versão e de hashes, não tocar nos modelos de outros projetos.

**Estado histórico:** Tiny-SD incompatível, substituído por SD 1.5 compatível e certificado. O Tiny-SD foi eliminado após verificações SHA256 e salvaguarda da prova real.

## Prova SD 1.5 — diagnóstico intermédio

- [VPS #42148799862](https://github.com/martaxi-boss/VPS/actions/runs/42148799862): pesos SD 1.5 full UNet fp16, CLIP e VAE **instalados e SHA256 PASS**; ComfyUI reconheceu e carregou o modelo em CPU (`FERRARI_COMFY_ACTUAL_MODEL_LOAD=PASS`), e KSampler concluiu **3/3 steps em cerca de 25 segundos**. O processo foi interrompido durante a descodificação VAE, **sem PNG certificado**; causa exata de terminação não provada (possível limite cgroup, SSH ou VAE). Nenhuma razão para aumentar quotas da VPS.
- A prova final utilizou libertação explícita UNet/CLIP, `comfy.model_management.unload_all_models()` e `VAEDecodeTiled(tile_size=128,overlap=32)` nativa, com indicadores de memória e cgroup preservado em **5 GiB / 150% CPU**. Só considerar PASS com PNG real e hash do resultado.

## Certificação final do ponto 2 — 6 de novembro de 2026

- **Código:** [PR #76](https://github.com/martaxi-boss/skill-universal/pull/76) integrada; código commit `40574f81db501d7abb5621c1ae3d66c7bdab381d`, [CI #42149291836](https://github.com/martaxi-boss/skill-universal/actions/runs/42149291836) SUCCESS.
- **VPS/ComfyUI:** [#42149365272](https://github.com/martaxi-boss/VPS/actions/runs/42149365272) **SUCCESS**. `FERRARI_COMFY_ACTUAL_MODEL_LOAD=PASS`, `FERRARI_COMFY_SAMPLING_COMPLETE=PASS`, `FERRARI_COMFY_IMAGE_REAL=PASS`, `FERRARI_COMFY_POINT2_IMAGE_ARTIFACT_VERIFIED=PASS`. Gerada imagem **PNG RGB de 256×256**, 3 passos KSampler, seed 1337, **91,25 s** totais, imagem real SHA256 `6941da15940f182e95e4b65c4e8fe58b7bf8d67756410efc27df3bb8465b64f9`. A execução validou o PNG no GitHub runner. Nenhum serviço ComfyUI permanente, sem GPU, sem APT/pip global.
- **Modelo final:** SD 1.5 `f03de327dd89b501a01da37fc5240cf4fdba85a1`; três SafeTensors privados de UNet/CLIP/VAE, **2.132.605.510 bytes** (1.719.125.304 + 246.144.864 + 167.335.342) com SHA256 comprovados. Licença CreativeML OpenRAIL-M; respeitar as restrições de uso. Não é um modelo de qualidade publicitária testada nem um pipeline de produção otimizado; três passos geram qualidade apenas de prova.
- **Segurança de recursos:** scope transitório `systemd-run --scope`, `MemoryMax=5G`, `CPUQuota=150%`, `TasksMax=256` e timeout máximo 510 s. `FERRARI_COMFY_AFTER_SAMPLER_CGROUP_MIB=1645.7` após libertar UNet/CLIP. `peak_rss_mib=5325.8` é métrica `ru_maxrss`, não equivalente ao limite de memória de cgroup; não interpretar como falha automática do teto. A VPS mantém **sem swap**, pelo que inferências maiores exigem nova prova de recursos, não pressupor.
- **Higiene real:** [VPS #42149831403](https://github.com/martaxi-boss/VPS/actions/runs/42149831403) **SUCCESS**, recusou apagar qualquer peso antes de revalidar os SHA256 SD15, PNG e TinySD. Depois eliminou apenas os 1.060.296.378 bytes da tentativa TinySD sem suporte e scripts transitórios verificados, mantendo modelo SD15 e imagem do ensaio.
- **Limite do ponto 2:** certificação de instalação + geração real **headless em CPU** na pasta Ferrari, não uma nova ação tipada exposta à Skill no ChatGPT, nem capacidade GPU ou interface gráfica pública. O ChatGPT cliente será atualizado apenas no fecho geral, conforme a decisão do proprietário.
