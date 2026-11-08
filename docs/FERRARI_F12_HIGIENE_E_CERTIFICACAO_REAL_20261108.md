# Ferrari F12 — higienização limitada e certificações funcionais reais (08/11/2026)

## Fonte de verdade e integridade

- Motor: [PR #170](https://github.com/martaxi-boss/skill-universal/pull/170), merge SHA `0cbca44be6670617732b22b48782e48ece2351f7`; procedimento único `install/vps-f12-hygiene-and-programs-certify.py`.
- VPS: [PR #406](https://github.com/martaxi-boss/VPS/pull/406); execução controlada pelo workflow Ferrari **existente**, com SSH/fingerprint já fixados, sem nova ponte.
- Release Ferrari preservada: `3f0ba44b7d8475a74a63c6010d1e27063c04bf1e`; rollback `427e1c33c6d10ca8ecd2103861adccd3d552c381`.
- Os dois relatórios originais são descarregáveis nas páginas GitHub Actions (artefactos temporários); devem ser arquivados fora dos artefactos efémeros caso se exija retenção longa.

## Higiene VPS — preview real

[Workflow #42511248400](https://github.com/martaxi-boss/VPS/actions/runs/42511248400): `status=PASS`, `mode=preview`, **8/8 serviços protegidos**.

| Âmbito estritamente auditado | Resultado |
|---|---|
| Cache de downloads npm `.runtime/npm-cache/_cacache` | Ausente, 0 bytes |
| Diretórios privados GUI com identificador de run e cinco marcadores sintéticos | 0 elegíveis |
| Releases ativas removidas | 0 |
| Outputs de utilizadores removidos | 0 |
| Reinstalações APT, alterações a projetos externos | 0 |

**Não foi disparado `apply`**, pois não havia candidatos. Isto não prova que todos os diretórios, caches ou branches da VPS estejam higienizados; apenas comprova os dois âmbitos auditados.

## F12 — provas funcionais de programas já instalados

[Workflow #42511331936](https://github.com/martaxi-boss/VPS/actions/runs/42511331936): `status=PASS`, `mode=certify`, **`passed=2` de `tested=2`**, **8/8 serviços protegidos**, sem mudanças de APT, programas, release ou outros projetos.

### FreeCAD 1.1.4 — headless real

Executor: `/srv/projects/skill-universal/tools/freecad-1.1.4/archive.AppImage`, dentro do Ferrari. Extraiu temporariamente a AppImage e invocou FreeCADCmd no diretório privado de QA. Um sólido paramétrico `Part::Box` de 15 × 20 × 10 mm foi recalculado, verificado com **volume 3 000 mm³**, salvo em **FCStd (2 483 bytes)** e exportado em **STEP (6 854 bytes)**. A integridade do arquivo FCStd e assinatura STEP foram verificadas. Pasta temporária removida automaticamente. **Não certifica GUI interativa nem outros workbenches.**

### yt-dlp 2026.10.26 — transferência real

Executor: `/srv/projects/skill-universal/tools/yt-dlp-2026.10.26/yt-dlp`, privado. FFmpeg Ferrari criou um MP4 sintético de **1 148 bytes**. yt-dlp descarregou-o por HTTP exclusivamente via **127.0.0.1** e a comparação com a origem confirmou **SHA-256 idêntico e tamanho 1 148/1 148 bytes**. Servidor local terminado e pasta temporária removida automaticamente. **Não certifica sites de terceiros, DRM, streams protegidos ou downloads da Internet.**

**Atenção à classificação:** estas são duas **certificações funcionais individuais de CLI**, **não** duas novas operações do catálogo universal. Até haver integração de operações de utilização orientadas pelo anfitrião, ambos continuam no grupo de programas instalados sem adaptador direto. O catálogo mantém **173 programas, 280 funções e 458 entradas**.

## Higienização GitHub

- [PR #43](https://github.com/martaxi-boss/skill-universal/pull/43) fechada sem merge: proposta APT global obsoleta perante a arquitetura privada atual.
- Seis pedidos sintéticos Ruflo concluídos foram retirados da árvore ativa `VPS/ferrari-requests/`, mantendo o histórico Git.
- [PR #407](https://github.com/martaxi-boss/VPS/pull/407) fez limpeza de mais 15 envelopes de QA sintéticos. **Total: 21 ficheiros removidos da árvore ativa**; `ferrari-requests/` ficou com **119 entradas** na inspeção pós-merge. [Validação de deleções sem execução de tarefas #42511558799](https://github.com/martaxi-boss/VPS/actions/runs/42511558799): `SUCCESS`.
- Branches antigos **não foram apagados**: requerem análise individual de merge/proteção e ferramenta de remoção apropriada. A limpeza da árvore ativa **não liberta automaticamente espaço do histórico Git**.

## Próximas certificações, sem falsa autonomia

1. Audacity, OBS, SolveSpace, Synfig e OpenShot: selecionar cada fluxo controlável e comprovar saída útil real, não só `--version` ou arranque Xvfb.
2. Para FreeCAD e yt-dlp, criar operações **apenas quando houver contrato de entrada/saída útil** e testes que justifiquem a admissão ao catálogo único.
3. Auditar órfãos de releases e outras áreas do projeto de forma separada e segura antes de autorizar mais remoções. Sempre proteger `current`, fallback, ferramentas, runtimes, outputs e os 8 serviços.

**Hierarquia:** IA anfitriã única → Ruflo sub-anfitrião efémero → papéis especializados → motor Ferrari e catálogo único. Autonomia LLM sem anfitrião não é requisito.
