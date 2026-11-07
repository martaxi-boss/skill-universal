# Ferrari F10 — certificação do catálogo único e higiene final (07/11/2026)

**Fonte única:** `engine/catalog.json` do repositório `martaxi-boss/skill-universal`, 450 registos (173 programas, 272 funções, 3 dependências centrais e 2 fornecedores). As 272 funções incluem 12 operações, 40 ações tipadas e 220 funções REA, sem catálogo REA separado.

## Release e fallback universal
- [Precheck real #42314715020](https://github.com/martaxi-boss/VPS/actions/runs/42314715020) SUCCESS sem mudar a release ativa: 448 testes PASS, 40 ações privadas e provas CAD/Blender/Office/ZIP; 8/8 serviços ativos.
- [Ativação real #42314959728](https://github.com/martaxi-boss/VPS/actions/runs/42314959728) SUCCESS: nova release `205c6f0e970259c79fa2111b6670c2fe1672fb27` ativa, fallback moderno `7bf6dcecf15da26502c5969b5eee54d5e116fc32` preservado, ambos com 450 registos; 448 testes PASS e 8/8 serviços ativos.

## Higiene física do único snapshot antigo 394
- [Primeira prévia #42315141299](https://github.com/martaxi-boss/VPS/actions/runs/42315141299) bloqueou a remoção de `952b0a75ba798471b07053677d53791bd078ed56`, pois continha uma pasta de estado ainda não auditada; não eliminou nada.
- [Auditoria read-only #42315365287](https://github.com/martaxi-boss/VPS/actions/runs/42315365287): essa release de 394 registos só tinha `.runtime` vazia, zero ficheiros, diretórios, symlinks e bytes; sem apontadores nem referências de processos acessíveis.
- [PR Ferrari #133](https://github.com/martaxi-boss/skill-universal/pull/133) acrescentou apenas esse SHA à lista de snapshots com estado vazio comprovado e testes que bloqueiam a exclusão se surgirem novos dados.
- [Segunda prévia #42315656543](https://github.com/martaxi-boss/VPS/actions/runs/42315656543) SUCCESS: única release elegível era o snapshot antigo 394.
- [Aplicação #42315724016](https://github.com/martaxi-boss/VPS/actions/runs/42315724016) SUCCESS: snapshot antigo eliminado, **2 433 024 bytes** libertados, catálogo ativo e fallback preservados, `legacy_catalog_files_in_active=[]`, `other_projects_or_ubuntu_modified=false`, 8/8 serviços ativos.

**Limites:** a limpeza do catálogo e destas releases está certificada; isto não certifica GUI completa, OBS, formatos PDAL opcionais ou dependências transitivas do Ubuntu. O `main` pode avançar com documentação sem que a VPS mude de release; não confundir SHAs. A Skill instalada no ChatGPT requer atualização própria — publicar a fonte ou ZIP não instala automaticamente a nova versão. Não apagar outras Skills/plug-ins sem confirmar a sua identidade.
