# Ferrari — descoberta Python, npm e contentores (03/11/2026)

## Âmbito desta alteração

O inventário `engine.tool_runtime.inventory()` passa a consultar
`engine.runtime_discovery.discover()`, mantendo o catálogo existente de
56 candidatos Ubuntu e 21 ações externas. Não instala programas, não altera
o SSH, não toca nos outros projetos e não executa código de pacotes
descobertos.

- **Python:** usa `find_spec` para o interpretador atual, sem importação de
  módulos de terceiros. Também procura a existência de módulos em pastas
  limitadas de ambientes virtuais **pertencentes ao Ferrari**, incluindo
  `.runtime/venvs/<ambiente>`. Regista OpenCV e outras bibliotecas, além dos
  candidatos profissionais opcionais `ifcopenshell` (BIM/IFC) e `bpy`
  (Blender Python). Existência de ficheiros não demonstra execução.
- **npm:** verifica `package.json` de pacotes conhecidos em
  `.runtime/npm` do Ferrari e em caminhos npm globais do sistema. Exemplos:
  Next.js, Vite, Tailwind, Playwright, Ruflo e REA. Não executa scripts npm,
  não percorre aplicações dos restantes projetos.
- **Contentores:** verifica `docker` e `podman` com o comando `ps` apenas
  sobre contentores que tenham a etiqueta
  `org.motor-ferrari.managed=true`. Para atribuir uma ferramenta, exige
  `org.motor-ferrari.tool=<id>` conhecido. Nunca enumera todos os
  contentores ou imagens da VPS. Se o daemon não responder, regista
  `probe=unavailable`; não inventa instalações.

## Como ler os resultados

`installed=true` significa que houve um **sinal de presença**:
executável, módulo, manifesto npm ou contentor etiquetado. O campo
`detection` diz qual. O estado `installed_unintegrated` não significa
ferramenta invocável. `callable` apenas indica adaptador/ operação base
registada e executável detetado; a certificação funcional de cada operação
continua a exigir teste real.

`ecosystems` no inventário inclui informação adicional sobre os três meios,
incluindo ferramentas como IfcOpenShell ainda fora da shortlist de 56.
A contagem de ferramentas detetadas pode aumentar sem instalar nada, porque
antes não eram observadas nalguns ambientes.

## Validação requerida

1. Testar no Ubuntu runner com os novos unitários, sem alterar software
   instalado.
2. Implantar a versão validada através do processo Ferrari existente.
3. Enviar novo pedido `kind=inventory` pela Skill e analisar
   `ecosystems.python`, `ecosystems.npm` e `ecosystems.containers`.
4. Para CAD/BIM/IFC, executar um exemplo real num executor instalado antes
   de declarar o formato IFC/STEP certificado.
5. Para desenvolvimento web, testar criação de projeto, build e browser
   apenas num workspace Ferrari isolado, antes de declarar profissional.

**Não é uma certificação funcional dos novos fornecedores.** A VPS é a
fonte final para instalações e execução; os caminhos de sistemas globais não
são licenciamentos nem autorizações de uso.
