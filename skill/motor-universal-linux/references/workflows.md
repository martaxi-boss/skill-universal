# Níveis de evidência e exemplos Ferrari

Uma **única Skill Universal** orienta pedidos ao Ferrari instalado na VPS Ubuntu. Ver `references/github-bridge.md` e o [BOOTSTRAP canónico](https://github.com/martaxi-boss/skill-universal/blob/main/BOOTSTRAP.md) para o estado real atual.

## Portas de certificação

1. Catálogo: candidato descoberto.
2. Compatibilidade: versão/ferramenta suporta Ubuntu.
3. Instalação: binário ou dependência localizado fisicamente na VPS.
4. Adaptador: operação tipada invocável pelo Ferrari.
5. Prova funcional: entrada e saída reais verificadas.
6. Prova remota: Skill→GitHub→VPS→ZIP com `report.json.status=completed` e artefactos.
7. Independência: executor e dependências de aplicação dentro da pasta Ferrari; prova de consumidores, rollback e compatibilidade.

Não converter uma prova de deteção numa certificação funcional. O alcance de cada prova tem de ser explicitado.

## Provas atuais (05/11/2026)

- **40/40 ações tipadas privadas, release ativa e limpeza Ferrari-only:** [VPS #42030605124](https://github.com/martaxi-boss/VPS/actions/runs/42030605124) PASS, versão `87969badbde0a77c2c181bb9605357d51a4a30c0`.
- **Inventário obtido pela Skill:** [VPS #42034776491](https://github.com/martaxi-boss/VPS/actions/runs/42034776491) PASS, 40 ações, 55/56 candidatos Ubuntu detetados, 83 programas inventariados (não todos operacionais).
- **Capacidades reais:** [matriz completa do ponto 3](https://github.com/martaxi-boss/skill-universal/blob/main/docs/CERTIFICACAO_FUNCIONAL_PONTO3_20261105.md) com sete pedidos novos por Skill: [web/automação #42034399375](https://github.com/martaxi-boss/VPS/actions/runs/42034399375), [REA #42034451772](https://github.com/martaxi-boss/VPS/actions/runs/42034451772), [inventário #42034464263](https://github.com/martaxi-boss/VPS/actions/runs/42034464263), [dados #42034750707](https://github.com/martaxi-boss/VPS/actions/runs/42034750707), [DOCX #42034927012](https://github.com/martaxi-boss/VPS/actions/runs/42034927012), [CAD STL #42035082826](https://github.com/martaxi-boss/VPS/actions/runs/42035082826), [Android #42035337944](https://github.com/martaxi-boss/VPS/actions/runs/42035337944), todos concluídos com provas de ZIP.
- **REEA/Android:** os REAs antigos foram removidos [#41840478411](https://github.com/martaxi-boss/VPS/actions/runs/41840478411), mas o REA 6.8.0 privado Ferrari mantém-se. 229 nomes MCP não significam 229 operações certificadas.

## Limites e decisões

Os executores das **40 ações tipadas** estão privados, mas as *operações base* `cad-stl` e `blender-house` foram verificadas usando `/usr/bin/openscad` e `/usr/bin/blender`. Não declarar isolamento completo dessas duas operações, instalar novas dependências globais, nem apagar as bibliotecas Ubuntu. ADB não foi validado com dispositivo físico. GUI interativa, Penpot, ComfyUI sem modelos e funções pagas do Hopper permanecem sem certificação.

O pacote `skill.zip` publicado pela CI é instalável; validar separadamente se a instância ChatGPT utiliza a versão nova. Erros de transporte, ações canceladas ou ficheiros ausentes não são PASS.
