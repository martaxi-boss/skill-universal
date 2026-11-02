# Certificação Ferrari CAD/3D/Office — 2026-11-02

- **GitHub Actions VPS:** [#41540947069 — SUCCESS](https://github.com/martaxi-boss/VPS/actions/runs/41540947069).
- **Release em execução:** `21735c20baa163cded0551144c9f8f7ef8db7431`.
- **SO:** Ubuntu 24.04 x86_64, sem GUI, sem GPU NVIDIA detetada.
- **Blender 4.0.2 APT:** `blender-house` criou `house.blend`, `house.glb`, `house.png`, todos artefactos confirmados, com Cycles CPU e denoising desativado para a compilação Ubuntu.
- **OpenSCAD 2021.01 APT:** `cad-stl` produziu `solid.stl` de uma geometria de teste por CLI.
- **LibreOffice/Pandoc APT:** `office-pdf` converteu DOCX criado por Pandoc em `document.pdf`.
- **Testes gerais:** 48 testes unitários na VPS PASS. REA/Ruflo CLI `--help` PASS; JADX e Ghidra testes funcionais PASS.
- **Evidência adicional:** scripts `install/vps-cad-3d.sh`, `engine/cad_tools.py`, `engine/blender_house.py`.
- **Nota de capacidade:** casa 3D conceptual, não é projeto BIM nem estrutural validado; FreeCAD e restantes fornecedores CAD ainda não certificados. Sem ligação direta da Skill à VPS comprovada.
- **Disco:** 13.61 GiB livres medidos no início da execução, antes de finalizar CAD/3D. É prioritário limpar somente as releases antigas do Ferrari, mantendo a ativa e uma versão de recuperação. Não inferir 56/56 instaladas.
