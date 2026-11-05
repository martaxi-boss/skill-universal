# Ferrari — CAD/3D privado: evidência do teste manual (05/11/2026)

O proprietário executou na VPS Ubuntu um script do repositório Ferrari em
`/srv/projects/skill-universal/`, apresentado numa captura de ecrã do
ConnectBot datada de **05/11/2026 às 14:50 UTC**.

## Evidência diretamente visível na captura

- `FERRARI_BLENDER_3D_EXPORT=PASS title=Ferrari privado`
- `FERRARI_PRIVATE_ARTIFACT=house.blend SIZE=578223`
- `FERRARI_PRIVATE_ARTIFACT=house.glb SIZE=9644`
- `FERRARI_PRIVATE_ARTIFACT=house.png SIZE=196500`
- `FERRARI_PRIVATE_ARTIFACT=solid.stl SIZE=1449`
- `FERRARI_PRIVATE_BLENDER_3D_FILES=PASS`
- `FERRARI_PRIVATE_CAD_REAL_SMOKE=PASS`
- `FERRARI_SMOKE_ONLY_PRIVATE_RUNTIME=PASS`

Este script executa `tools/blender/blender` e
`tools/openscad/bin/openscad`, verificando que os caminhos resolvidos
ficam sob `/srv/projects/skill-universal/tools/`. O script apaga
automaticamente o seu diretório temporário ao terminar. A captura
demonstra o resultado do script, não uma inspeção independente do estado
atual dos ficheiros após o teste.

## Não certificado por esta prova

- Ativação da nova release no symlink `current` — **não efetuada**.
- Caminho privado para `office-pdf`/LibreOffice — **a validar**.
- Execução ponta a ponta Skill → GitHub Actions → VPS → ZIP **após** ativação.
- Desinstalação/remoção das cópias globais OpenSCAD e Blender, que ainda
  podem ser usadas por outros projetos.
- Ausência de todas as dependências de aplicações globais em qualquer
  outra parte do Ferrari.

Próxima porta: instalação privada/validação real do LibreOffice,
auditoria dos restantes executores e migração controlada da release com
rollback. Não alterar SSH, Supervisor nem outros projetos.
