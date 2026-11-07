# Ferrari F11 — prova funcional PDAL LAS real (07/11/2026)

**Execução certificada:** [VPS #42317695882](https://github.com/martaxi-boss/VPS/actions/runs/42317695882) — SUCCESS. **Motor:** Ferrari já ativo em `/srv/projects/skill-universal`. **Catálogo:** único `engine/catalog.json` (450 registos: 173 programas, 272 funções, 3 dependências, 2 fornecedores). Nenhuma alteração de release ou fallback.

## Ensaio controlado

O script [`install/vps-f11-pdal-las-certify.py`](../install/vps-f11-pdal-las-certify.py) criou uma amostra original sintética de **5 pontos** `X,Y,Z` dentro de um diretório temporário na pasta privada `.runtime` do Ferrari. Utilizou o executável PDAL já instalado no prefixo privado QGIS `tools/qgis-4.2.3-condaforge` e as bibliotecas privadas do sidecar HDF5 ABI 320, sem downloads nem instalações.

O pipeline executou a conversão **TXT → LAS → TXT**, usando `readers.text`, `writers.las`, `readers.las` e `writers.text`. Os métodos de leitura, escrita e pipeline são documentados no [manual oficial PDAL](https://pdal.io/en/stable/stages/readers.text.html).

## Evidência observada no report real

| Medição | Resultado |
|---|---|
| Marcador no workflow | `FERRARI_F11_PDAL_LAS_TXT_REAL=PASS` |
| `status` | `pass` |
| `txt_to_las_exit_code` | 0 |
| `las_to_txt_exit_code` | 0 |
| LAS gerado | **327 bytes** |
| Assinatura LAS (verificação independente) | `LASF` |
| Cabeçalho / início dos pontos | 227 / 227 bytes |
| Contagem de pontos no cabeçalho | **5 pontos** |
| Pontos preservados na leitura inversa | **5/5**, coordenadas verificadas |
| Testes específicos do script | 5 PASS |
| Serviços protegidos | 8/8 PASS |
| APT, catálogo, outros projetos modificados | Não |
| Ficheiros sintéticos temporários | Removidos no fim |

[Artefacto oficial da execução](https://github.com/martaxi-boss/VPS/actions/runs/42317695882/artifacts/13551268123) contém o relatório JSON com os campos de prova.

## Limites

Este PASS prova **uma conversão funcional real LAS** no ambiente privado e a respetiva releitura, não todos os formatos PDAL. Os plugins adicionais `readers.hdf` e `readers.icebridge` (Icebridge) foram carregados dinamicamente na F9, mas ainda **não** têm leitura de datasets reais certificada. As aplicações GUI completas e OBS também permanecem pendentes.

O campo diagnóstico `driver_names_in_tail=false` significa apenas que os nomes dos drivers não apareceram no trecho limitado de saída guardado; não invalida os dois pipelines concluídos com código 0 e releitura validada. A release ativa `205c6f0e` e o fallback `7bf6dcec` mantiveram-se inalterados. Não criar outro catálogo, motor ou Skill.
