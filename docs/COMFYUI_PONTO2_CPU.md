# Ferrari — Ponto 2 / ComfyUI CPU e modelo privado

**Estado inicial confirmado em 06/11/2026** pela [VPS #42146994521](https://github.com/martaxi-boss/VPS/actions/runs/42146994521): ComfyUI v0.43.0 presente em `/srv/projects/skill-universal/tools/comfyui-v0.43.0`, venv `.runtime/venvs/extended/comfyui` com Torch CPU `2.15.0+cpu`. VPS com 4 CPUs lógicas, ~8 GB RAM, sem swap e 41,57 GiB livres.

## Decisão de modelo

Escolhido **Segmind Tiny-SD** de [Hugging Face](https://huggingface.co/segmind/tiny-sd), variante de segurança [PR #6, commit 3d25de3e8d5aacf94ce91176f204e6d11d120315](https://huggingface.co/segmind/tiny-sd/tree/3d25de3e8d5aacf94ce91176f204e6d11d120315). Licença `creativeml-openrail-m` (gratuita sob condições de uso, não equivalente a domínio público ou ausência de restrições). O modelo é experimental e não substitui modelos grandes em qualidade.

Pesos privados, todos **SafeTensors, SHA256 verificado**, total ~1,06 GB: `text_encoder/model.safetensors` (246 MB), `unet/diffusion_pytorch_model.safetensors` (647 MB) e `vae/diffusion_pytorch_model.safetensors` (167 MB). Não descarregar `.bin` / pickle. JSON de configuração por pin de revisão, não confiar em versões flutuantes.

## Layout e execução

- Código já existente: `tools/comfyui-v0.43.0/`
- Python já existente: `.runtime/venvs/extended/comfyui/`
- Pesos novos: `tools/comfyui-v0.43.0/models/diffusers/segmind-tiny-sd-3d25de3/`
- Executável de instalação: `install/vps-comfyui-cpu-model.py --check|--apply`, via GitHub Actions/SSH administrativo limitado a esta pasta. Instalação atómica; recusar conflitos; limpar apenas staging próprio em caso de falha; sem APT, pip global, novo Docker, serviços públicos ou coordenador.
- Prova de imagem: `install/vps-comfyui-cpu-smoke.py` só dentro de escopo temporário `systemd-run --scope` com limite máximo de 5 GiB RAM e CPU 150%, timeout definido no workflow, sem porta pública. Deve gerar uma PNG de 256×256 com CLIP, KSampler e VAE ComfyUI reais, sem API externa.
- A prova não pode declarar sucesso apenas por existência de ficheiros/modelos; validar PNG, dimensões, metadados e hashes. O modo GUI, GPU, qualidade profissional e tempos reduzidos **não** são certificados por esta prova.
- A release Ferrari `current` e os restantes projetos permanecem intocados. O estado do modelo está na pasta privada Ferrari mesmo que a CI/Skill seja atualizada mais tarde.

## Higiene

Depois de PASS, remover workflows/pedidos administrativos **temporários** no repositório VPS. Manter a pasta de pesos com proveniência SHA e um relatório mínimo; não remover o runtime ou a release F7 protegida. Nunca eliminar pacotes Ubuntu globais, venv de outro projeto ou serviços protegidos durante esta tarefa.

**Estado de conclusão:** por registar após resultado de instalação e inferência real na VPS; conservar este limite no BOOTSTRAP.


## Diagnóstico de incompatibilidade e correção (06/11/2026)

- [VPS #42147745661](https://github.com/martaxi-boss/VPS/actions/runs/42147745661): o Tiny-SD foi instalado e os 3 hashes passaram; a primeira prova falhou devido ao uso de `systemd-run --scope --wait`, combinação inválida. Não houve geração de imagem.
- [VPS #42147964610](https://github.com/martaxi-boss/VPS/actions/runs/42147964610): o `--scope` funcionou mas a prova detectou que o parser de argumentos do ComfyUI não tinha sido inicializado, levando à escolha incorreta de CUDA.
- [VPS #42148307043](https://github.com/martaxi-boss/VPS/actions/runs/42148307043): com a correção nativa do modo CPU (PyTorch `+cpu`), verificou-se uma incompatibilidade estrutural genuína: `Could not detect model type` para a UNet Tiny-SD *pruned*. **Não declarar Tiny-SD funcional no ComfyUI 0.43.0.**
- Alternativa de compatibilidade: modelo oficial [Stable Diffusion 1.5](https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5), commit `f03de327dd89b501a01da37fc5240cf4fdba85a1`, pesos UNet padrão, CLIP e VAE em três `.fp16.safetensors` com SHA256 conhecido, total aproximado 2,1 GB. Licença `creativeml-openrail-m` (ver regras de uso). Caminho privado novo `tools/comfyui-v0.43.0/models/diffusers/sd15-fp16-f03de327/` sem alterar o runtime, a release ativa ou outros projetos.
- A prova real reutiliza o **mesmo** ComfyUI e limites de cgroup; requer PNG 256×256, hash real e reporte. Se a memória for insuficiente, **parar sem aumentar as quotas**.
- Após certificação da alternativa, verificar ausência de consumidores e remover os **pesos Tiny-SD sem suporte** dentro da pasta Ferrari com guardas de versão e de hashes, não tocar nos modelos de outros projetos.

**Estado:** modelo Tiny-SD verificado mas incompatível; SD 1.5 em preparação. Nenhuma certificação de geração real por ComfyUI até um novo run com PNG válido.

## Prova SD 1.5 — diagnóstico intermédio

- [VPS #42148799862](https://github.com/martaxi-boss/VPS/actions/runs/42148799862): pesos SD 1.5 full UNet fp16, CLIP e VAE **instalados e SHA256 PASS**; ComfyUI reconheceu e carregou o modelo em CPU (`FERRARI_COMFY_ACTUAL_MODEL_LOAD=PASS`), e KSampler concluiu **3/3 steps em cerca de 25 segundos**. O processo foi interrompido durante a descodificação VAE, **sem PNG certificado**; causa exata de terminação não provada (possível limite cgroup, SSH ou VAE). Nenhuma razão para aumentar quotas da VPS.
- A próxima prova usa libertação explícita UNet/CLIP, `comfy.model_management.unload_all_models()` e `VAEDecodeTiled(tile_size=128,overlap=32)` nativa, com indicadores de memória e cgroup preservado em **5 GiB / 150% CPU**. Só considerar PASS com PNG real e hash do resultado.
