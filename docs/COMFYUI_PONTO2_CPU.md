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
