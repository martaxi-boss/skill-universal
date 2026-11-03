# Certificação — descoberta de ecossistemas Ferrari, 03/11/2026

## Identificação e provas

- **Versão do motor instalada:** `1b3e232969c89801e8a0680d8ea751a536a53ce5`.
- **Código e testes Ubuntu:** [#41554507978](https://github.com/martaxi-boss/skill-universal/actions/runs/41554507978) SUCCESS.
- **Instalação real na VPS:** [#41554557002](https://github.com/martaxi-boss/VPS/actions/runs/41554557002) SUCCESS, **79 testes PASS na VPS**, smoke multidomínio e orquestração PASS.
- **Pedido real de inventário pela Skill:** [#41554751046](https://github.com/martaxi-boss/VPS/actions/runs/41554751046) SUCCESS. Marcadores `FERRARI_SKILL_REQUEST_PICK=PASS`, `FERRARI_SKILL_JOB_STATUS=completed`, `FERRARI_SKILL_RESPONSE_ZIP=PASS` e `FERRARI_SKILL_END_TO_END=PASS`. O ZIP contém `report.json` e `artifacts/inventory.json`.
- **Comparação:** inventário anterior da Skill [#41551865840](https://github.com/martaxi-boss/VPS/actions/runs/41551865840).

## Contagens reais — antes e depois

| Medida | Anterior | Agora |
|---|---:|---:|
| Candidatos Ubuntu selecionados | 56 | 56 |
| Ações externas definidas | 21 | 21 |
| Ações externas detetadas como invocáveis | 21 | 21 |
| Selecionados detetados | 21 | 21 |
| Selecionados sem sinal de presença | 35 | 35 |
| Programas detetados no catálogo combinado | 46 | 46 |

**A melhoria é de cobertura e precisão da descoberta, não de instalações nem certificações adicionais.**

## Evidência por ecossistema

- **Python:** `cv2`/OpenCV identificado no interpretador da VPS pelo mecanismo `module_spec_not_imported`, em `/usr/lib/python3/dist-packages`. Não foi declarado teste funcional novo de OpenCV. O inventário inclui agora a procura de módulos em virtualenvs Ferrari, bem como `ifcopenshell` e `bpy`, mas nenhum destes últimos foi detetado.
- **npm:** manifesto `ruflo/package.json` encontrado em `/home/ubuntu/.local/share/motor-ferrari/.runtime/npm/ruflo/node_modules`. Presença confirmada; o teste profundo de orquestração Ruflo continua pendente. Next.js, Vite, Tailwind e Playwright não foram detetados.
- **Contentores:** nem `docker` nem `podman` foram encontrados no PATH da VPS. Nenhum contentor etiquetado como Ferrari foi identificado. A descoberta não enumera contentores de outros projetos.
- **CAD/3D:** Blender e OpenSCAD foram detetados com operações base. FreeCAD não foi detetado. Não foi demonstrado trabalho profissional BIM/IFC ou validação de modelos IFC.
- **Desenvolvimento:** Node.js, npm, Python e Git foram detetados como executáveis, mas não possuem ainda adaptadores tipados de construção/testes profissionais no Ferrari. Não confundir uma CLI presente com o produto completo disponível na Skill.

## Isolamento e limites

A nova descoberta é de leitura. Não introduziu serviços, contentores, dependências externas ou aplicações gráficas. As únicas alterações à infraestrutura de entrega foram as referências à nova versão nos dois workflows **exclusivos Ferrari** no repositório VPS; o SSH, os segredos, a impressão digital e as instruções da ponte permaneceram inalterados. A instalação da release usou o instalador Ferrari já existente.

## Próximas prioridades (ainda por executar/certificar)

1. **CAD/BIM:** verificar compatibilidade e licença de IfcOpenShell para a versão Python/Ubuntu da VPS. Instalar isoladamente só após confirmação técnica; implementar leitura/validação IFC com modelo real, preservando OpenSCAD/Blender. Avaliar FreeCAD headless sem instalar desktop por rotina.
2. **Desenvolvimento:** começar pelo Node.js instalado para validação/build de um pequeno projeto isolado e, só se necessário, integrar Vite/Playwright com dependências e testes reais.
3. **Contentores:** a ausência de Docker/Podman **não é uma avaria** nem autorização para instalar um daemon. Introduzir somente quando um pedido precisar de execução em contentores e o isolamento estiver definido.
4. **Certificação:** continuar a separar descoberta, adaptador, testes unitários, testes na VPS e entrega pela Skill.

Referência de implementação: [documentação técnica](DESCOBERTA_ECOSISTEMAS_20261103.md). Não alterar a ponte SSH nem o supervisor de outros projetos.
