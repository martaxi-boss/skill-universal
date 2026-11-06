# Ferrari F9 — certificação real da Skill: CAD 3D, Blender e estado PDAL

**Fotografia real:** 6 de novembro de 2026. **Motor:** único Ferrari `martaxi-boss/skill-universal`. **Transporte:** workflow GitHub Actions existente `Ferrari Skill - authenticated request delivery`, sem criar novas pontes, serviços, catálogos ou Skills.

## OpenSCAD — operação nativa `cad-stl` certificada

[Execução real VPS #42312047260](https://github.com/martaxi-boss/VPS/actions/runs/42312047260): `FERRARI_SKILL_JOB_STATUS=completed`, `FERRARI_SKILL_RESPONSE_ZIP=PASS` e `FERRARI_SKILL_END_TO_END=PASS`. O `report.json` do ZIP devolveu `status=completed`, `operation=cad-stl`, `executor=/srv/projects/skill-universal/tools/openscad/bin/openscad` e artefacto `artifacts/solid.stl`.

A entrada era **original e sintética**: bloco de 60 × 40 × 12 mm com perfuração cilíndrica passante de raio 6 mm, em OpenSCAD. O STL real (31 694 bytes) foi inspecionado de forma independente com trimesh: **208 faces, 104 vértices**, limites `[-30,-20,-6]` a `[30,20,6]`, **malha fechada (`is_watertight=True`)** e volume calculado **27 446,705 mm³**. Isto certifica geração/exportação de **uma** geometria CAD 3D; não significa que qualquer desenho/modelo complexo esteja certificado.

## Blender — operação nativa `blender-house` certificada

[Execução real VPS #42312161892](https://github.com/martaxi-boss/VPS/actions/runs/42312161892): `FERRARI_SKILL_JOB_STATUS=completed` e `FERRARI_SKILL_END_TO_END=PASS`. `report.json` devolveu `status=completed`, `operation=blender-house`, executado por `/srv/projects/skill-universal/tools/blender/blender`. Produziu realmente:

| Ficheiro | Tamanho | Verificação independente |
|---|---:|---|
| `artifacts/house.blend` | 578 223 bytes | Cabeçalho nativo `BLENDER-v405` |
| `artifacts/house.glb` | 9 644 bytes | glTF binário 2.0 válido, **6 geometrias** carregadas em trimesh |
| `artifacts/house.png` | 196 509 bytes | PNG 420 × 300 píxeis validado por Pillow |

A imagem mostra uma casa conceptual criada pelo script de demonstração interno, não um projeto de arquitetura, engenharia ou licenciamento. O render usa Blender CPU privado e não certifica GPU, todas as funcionalidades de modelação, cenas arbitrárias ou desempenho.

## Cad 2D e QGIS — provas complementares

- [LibreCAD privado #42311158545](https://github.com/martaxi-boss/VPS/actions/runs/42311158545): `DXF → PDF` real de uma página, 1 614 bytes, confirmado por Poppler privado, com Xvfb já presente apenas para QA. [Relatório](FASE9_LIBRECAD_DXF_PDF_CERT_20261106.md).
- [QGIS nativo #42304131087](https://github.com/martaxi-boss/VPS/actions/runs/42304131087): `native:buffer` 5 m e exportação GeoJSON de polígono sintético, validação independente de área (5 000 → 6 578,316 m²). [Relatório](FASE9_QGIS_BUFFER_GEOJSON_CERT_20261106.md).
- [Diagnóstico QGIS/GDAL/OGR #42310024834](https://github.com/martaxi-boss/VPS/actions/runs/42310024834): provas **isoladas** GDAL/OGR e QGIS/OGR tiveram sucesso com uma feature GeoJSON; um **outro teste composto** de leitura OGR tinha terminado em `std::bad_alloc` [#42303505063](https://github.com/martaxi-boss/VPS/actions/runs/42303505063). Não confundir o PASS isolado com a certificação de todas as sequências/modes OGR.

## Dependência HDF5 e PDAL — ainda não são formatos certificados

- [HDF5 sidecar privado #42311011076](https://github.com/martaxi-boss/VPS/actions/runs/42311011076): linker privado do ABI `.320` passou, sem alterar o APT do Ubuntu.
- [Carregamento PDAL #42311620021](https://github.com/martaxi-boss/VPS/actions/runs/42311620021): **2 plugins carregados dinamicamente** num subprocesso, inicialização QGIS com sidecar PASS; ambos **não apareceram anunciados** no registo CLI de drivers `pdal` nessa prova. `full_pdal_formats_certified=false`, `gui_certified=false`, `global_apt_changed=false` e `other_projects_changed=false`.
- O carregamento de `.so` e a presença da CLI **não validam leitura real de ficheiros HDF/icebridge**. Precisam de dados sintéticos apropriados, uma invocação pública suportada e prova de resultados para cada formato.

## Higienização, arquitetura e limites

Os dois pedidos CAD/Blender foram enviados como JSONs novos pelo **mesmo** transporte existente da Skill; não houve alteração ao motor ativo, ao catálogo `engine/catalog.json`, a outros projetos ou ao SSH. Os ZIPs dos dois pedidos contêm `report.json` e os artefactos reais. A release e o fallback Ferrari, o inventário de catálogo 450 e os oito serviços protegidos tiveram verificação própria nas provas anteriores [#42301479668](https://github.com/martaxi-boss/VPS/actions/runs/42301479668) e [#42311620021](https://github.com/martaxi-boss/VPS/actions/runs/42311620021); estas **duas** operações da Skill não constituem, por si só, nova auditoria global aos serviços.

**Estado F9:** Cad 2D DXF→PDF, CAD 3D OpenSCAD→STL, Blender→BLEND/GLB/PNG e QGIS native buffer têm **PASS nos casos concretos**. Permanecem pendentes GUI interativa, funções adicionais áudio/vídeo/OBS, formatos PDAL opcionais e certificação de dependências transitivas completas. **Não declarar o Ferrari inteiro 100% certificado.**
