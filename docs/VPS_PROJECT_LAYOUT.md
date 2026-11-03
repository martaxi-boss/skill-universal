# Ferrari — mapa de instalacao isolada Ubuntu VPS

**GitHub:** `martaxi-boss/skill-universal` (Motor Ferrari).
**Leitura e alteracao real:** 03-11-2026 via motor REA FINAL. Prova: [GitHub Actions #41714161162](https://github.com/martaxi-boss/VPS/actions/runs/41714161162).

## Pasta do projeto

**Diretorio fisico:** `/srv/projects/skill-universal/` — 13 517 766 656 bytes verificados na movimentacao.

Estrutura e responsabilidades:
- `releases/` — codigo das versoes instaladas;
- `current` — symlink relativo para `releases/5dfd2fc4da0869230b8fe7f838ea0f95a33b9afe` (nao depende do caminho antigo);
- `.runtime/venvs/` — Python e dependencias privadas dos fornecedores Ferrari;
- `.runtime/npm/` — pacotes Node e ferramentas privadas;
- `.runtime/browsers/` — motores de browser isolados;
- `tools/` — programas especializados exclusivos;
- `runtimes/` — versoes isoladas de Node, Java e outros runtimes.

O antigo `/home/ubuntu/.local/share/motor-ferrari` passou a ser apenas uma **ligacao temporaria** para o diretorio canonico. O motor Ferrari foi importado com sucesso a partir do caminho novo pelo utilizador proprietario `ubuntu`. Os servicos principais e os dois robos Telegram nao mudaram de estado. **A mudanca de nome nao libertou espaco em disco**, por ser dentro do mesmo filesystem.

## O que ainda falta certificar

1. Scripts e workflows de instalacao/deploy anteriores ainda podem escrever no caminho antigo. Atualizar o destino e validar um deploy controlado antes de remover a ligacao de compatibilidade.
2. Componentes APT globais do Ubuntu e outras ferramentas fora desta pasta continuam instalados no sistema. A migracao acima **nao prova que Ferrari funcione totalmente sem essas dependencias**; essas dependencias devem ser identificadas e substituidas por runtimes do projeto quando aplicavel.
3. Nao duplicar o runtime REA FINAL, Codex, Android SDK ou programas de outros projetos apenas por terem nomes de ferramentas semelhantes. Verificar propriedade e instalacao independente antes de mexer.
4. A desinstalacao por apagamento de uma unica pasta **nao esta certificada** ate provar que nao existem scripts, dados, credenciais ou servicos exclusivos fora da raiz.

## Limpeza

A cache npm do Ferrari ja tinha sido higienizada numa etapa anterior, documentada em `docs/HIGIENIZACAO_FISICA_FERRARI_VPS_20261103.md`. Nao apagar ferramentas, venvs, releases ativas ou fornecedores por terem pacotes repetidos: isolamento de projetos implica dependencias privadas separadas.

Esta pagina e um mapa de estado real e nao substitui os procedimentos de instalacao existentes.
