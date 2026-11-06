# Ferrari F9 — QGIS nativo certificado, fornecedores opcionais pendentes

**Data:** 06/11/2026. **Escopo:** QGIS 4.2.3 privado no Ferrari Ubuntu, sem GPU ou dados reais.

## Prova real

[GitHub Actions VPS #42304131087](https://github.com/martaxi-boss/VPS/actions/runs/42304131087), artefacto `ferrari-universal-42304131087`: **PASS**; `FERRARI_F9_QGIS_NATIVE_GEOJSON=PASS`, `FERRARI_PROTECTED_SERVICES=8/8_PASS`.

- QGIS `processing.run("native:buffer")` executado num polígono sintético com **100 × 50 m = 5 000 m²** num layer `EPSG:3857`.
- Distância do buffer: **5 metros**, área independente a partir das coordenadas do GeoJSON resultante **6 578,316 m²**.
- `FeatureCollection` com uma única feature, anel exterior fechado, coordenadas numéricas e intervalo de área validado em código Python independente.
- Processo Python do QGIS devolveu **exit code 0**. Artefactos de teste e definições transitórias em `skill-universal/.runtime` removidos no fim.
- `ldd` do `qgis_process`: **211 bibliotecas resolvidas no runtime QGIS privado**, **6 bibliotecas base Ubuntu**, **0 sonames diretamente não resolvidos**. Não é prova de isolamento integral de todas as bibliotecas transitivas.
- Catálogo único `engine/catalog.json` confirmado com **450 entradas**; release `7bf6dcecf15da26502c5969b5eee54d5e116fc32`, fallback `952b0a75ba798471b07053677d53791bd078ed56`. Sem alterações APT, outros projetos ou serviços.

**O que passa exatamente:** processamento nativo QGIS de buffer e exportação GeoJSON verificada por uma rotina independente. **Isto não certifica a leitura por OGR**, edição da GUI, todos os providers ou o QGIS completo.

## Descobertas e tentativas anteriores

- [#42302909933](https://github.com/martaxi-boss/VPS/actions/runs/42302909933): o algoritmo QGIS produziu GeoJSON, mas a verificação tentou chamar `QgsGeometry.fromJson`, API não existente nesta versão → `PARTIAL_BLOCKED`.
- [#42303505063](https://github.com/martaxi-boss/VPS/actions/runs/42303505063): a verificação independente por provider OGR iniciou mas abortou em C++ (`std::bad_alloc`) → `PARTIAL_BLOCKED`, sem afetar serviços ou release.
- Em todas as provas houve avisos de plugins PDAL opcionais `libpdal_plugin_reader_hdf.so` e `libpdal_plugin_reader_icebridge.so` devido à falta de `libhdf5_cpp.so.320`. Esta dependência **não** é indicada como resolvida pela simples leitura de `ldd` no executável principal. Não remover, alterar globalmente ou instalar bibliotecas sem verificar proveniência, ABI e rollback.

## Organização do Ferrari

A prova [Ferrari PR #124](https://github.com/martaxi-boss/skill-universal/pull/124) introduziu a verificação de geometria independente sem carregar o fornecedor opcional instável; [VPS PR #365](https://github.com/martaxi-boss/VPS/pull/365) reutilizou **o mesmo workflow de releases**, com pedido fixo. Não há segundo catálogo, nova Skill, novo coordenador, outro SSH ou instalação fora da pasta Ferrari.

**Próximo bloqueio objetivo:** diagnosticar e corrigir, se possível e com instalador privado reprodutível, o fornecedor PDAL HDF5 opcional e o abort OGR em subprocesso isolado, sem alterar o QGIS que já funciona nas rotas certificadas. Depois certificar CAD, áudio, vídeo, OBS e GUI por operações reais, não apenas arranque. A Fase 9 nominal APT está higienizada; a certificação funcional completa permanece parcial.
