# Ferrari F9 — LibreCAD privado: DXF → PDF funcional certificado

**Data:** 06/11/2026. **Programa:** LibreCAD 2.2.1.6 no Motor Ferrari Ubuntu, sem GUI interativa.

## Provas reais na VPS

- [Primeiro teste #42310428893](https://github.com/martaxi-boss/VPS/actions/runs/42310428893): `PARTIAL_BLOCKED`; AppImage íntegro, mas `QT_QPA_PLATFORM=offscreen` fez o conversor abortar (`exit=-6`), sem PDF. Falso PASS impedido.
- [Certificação corrigida #42311158545](https://github.com/martaxi-boss/VPS/actions/runs/42311158545): **SUCCESS** no GitHub Actions, relatório `ferrari-universal-report.json` com `status=pass` e `FERRARI_F9_LIBRECAD_REAL=PASS`. O executável foi o `AppRun` privado em `/srv/projects/skill-universal/tools/librecad-2.2.1.6/squashfs-root/`, versão 2.2.1.6. AppImage original (82 846 008 bytes) validado por SHA256 `f2d86e6a40ec684b758c821eff3496a7d36e69f17519cde0b508a66d72c5754c`.
- O ficheiro DXF R12 **sintético** incluía um retângulo 100 × 50 unidades (4 segmentos LINE) e um círculo CIRCLE. O LibreCAD converteu para **PDF real de 1 página, 1 614 bytes**, `converter_exit_code=0`.
- Um programa **independente e privado** (`tools/ubuntu-cli/bin/pdfinfo`, Poppler) confirmou que o documento PDF é válido, com **1 página**; PDF SHA256: `9ef7e725bbb04838438277f1d418e7544d75a73a6046369598e33c87568996c3`.
- Foi usado apenas o Xvfb já presente no Ubuntu como **ecrã virtual transitório de QA**, com `QT_QPA_PLATFORM=xcb`. Não houve instalação de Xvfb ou de dependências APT, não se criou serviço residente e os temporários privados em `skill-universal/.runtime` foram eliminados.
- `engine/catalog.json`: **um só catálogo, 450 entradas**. Release ativa `7bf6dcecf15da26502c5969b5eee54d5e116fc32`, fallback `952b0a75ba798471b07053677d53791bd078ed56`, sem mudanças. **8/8 serviços protegidos PASS**; outros projetos intocados.

## Limite exato da certificação

**PASS** significa que o LibreCAD privado conseguiu converter **o DXF sintético em PDF real**, validado por uma segunda ferramenta privada. **NÃO significa** que estejam certificadas a edição interativa de CAD, todas as variantes DXF/DWG, automação gráfica, exportação SVG/PNG, impressão profissional ou CAD 3D. A ferramenta pode precisar de um servidor X para o seu binário AppImage; o Xvfb preexistente foi usado apenas no ensaio.

## Organização e higiene

O código e os testes estão em [Ferrari PR #127](https://github.com/martaxi-boss/skill-universal/pull/127) e na correção [PR #129](https://github.com/martaxi-boss/skill-universal/pull/129). O transporte usa o **workflow Ferrari existente** do [VPS PR #368](https://github.com/martaxi-boss/VPS/pull/368) e a correção [PR #370](https://github.com/martaxi-boss/VPS/pull/370), sem outro catálogo, Skill, agente, ponte SSH ou projeto. O PR #367 foi encerrado por conflito de merge simultâneo e substituído pelo #368 sem perda de alterações; os seus registos históricos podem permanecer.

**Próxima fronteira F9:** certificar funções reais de áudio/vídeo, OBS, outros formatos CAD e GUI onde aplicável; continuar a testar bibliotecas opcionais isoladas, sem declarar Fase 9 integralmente concluída.
