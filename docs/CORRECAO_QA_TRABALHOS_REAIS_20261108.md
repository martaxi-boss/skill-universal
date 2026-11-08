# Ferrari — Correções de qualidade após trabalhos reais (08/11/2026)

## Estado real após execução — 08/11/2026

**Código ativo na VPS:** release imutável `e83ed6dff335459c0fb3526b56241768dbe3b635`, com `e0509d5370828869479069c99f2eace779960cad` preservada como rollback; o transporte normal também foi pinado na nova release, sem alterações ao SSH.

- **CI da main** [#42481211415](https://github.com/martaxi-boss/skill-universal/actions/runs/42481211415): 486 testes PASS, pacote Skill e plugin criado.
- **Pré-validação na VPS** [#42481365996](https://github.com/martaxi-boss/VPS/actions/runs/42481365996): 486 testes, 40/40 ações privadas, geração/ZIP, 8/8 serviços, `current` inalterado.
- **Ativação protegida** [#42481446381](https://github.com/martaxi-boss/VPS/actions/runs/42481446381): pré-teste repetido, `FERRARI_RELEASE_SWITCH=PASS`, `FERRARI_PREVIOUS_RELEASE_PRESERVED=e0509d...`, nova release verificada e 8/8 serviços PASS.
- **Ruflo-host real com revisão vinculada** [#42481582524](https://github.com/martaxi-boss/VPS/actions/runs/42481582524): codificador com `jq` privado, revisor com o ficheiro anterior, um `quality-review.json` com hash real e `verified_quality_reviews=1`; `report.json.quality_gate.status=passed`, ZIP íntegro e `FERRARI_SKILL_END_TO_END=PASS`.
- **Regressão do vídeo silencioso** [#42481699413](https://github.com/martaxi-boss/VPS/actions/runs/42481699413): repetido o mesmo MLT sintético antigo, áudio AAC existente mas RMS `-200.0 dBFS`; `quality_gate.status=failed`, `report.json.status=failed`. O workflow `FAILURE` é **o resultado esperado**, porque o trabalho com áudio obrigatório foi corretamente recusado; `response.zip` com o MP4 e relatório preservado e verificado.
- **Equipa Ruflo por rondas (uma IA anfitriã)**: início [#42481868939](https://github.com/martaxi-boss/VPS/actions/runs/42481868939), execução jq pelo programador [#42481938798](https://github.com/martaxi-boss/VPS/actions/runs/42481938798), aprovação por revisor com SHA-256 real [#42482023044](https://github.com/martaxi-boss/VPS/actions/runs/42482023044) e conclusão [#42482098501](https://github.com/martaxi-boss/VPS/actions/runs/42482098501). `status=completed`, uma ação privada, uma revisão cruzada e `autonomous_agent_model_calls=0`, sem fingir autonomia LLM.
- **Skill cliente** `motor-universal-linux`: atualização **in-place** v1.0.7 → **v1.0.8**, readback confirmou 12 ficheiros e nova regra de QA; release `pluginrel_6af06ef9b7708191be273a26723421fb`.

Estas provas certificam o **fluxo testado**, não todas as 173 aplicações, todos os formatos, direitos editoriais, GUI ou inferência de modelos independentes. A avaliação final humana ainda é obrigatória para materiais criativos, sites e engenharia.

## Evidências que motivaram a correção

- [VPS Ferrari #42331739216](https://github.com/martaxi-boss/VPS/actions/runs/42331739216): anúncio Low Cost Europa 20 s gerou MP4 tecnicamente válido, com áudio silencioso; o PASS de conversão MLT não garantiu a locução pedida.
- [VPS Ferrari #42383796195](https://github.com/martaxi-boss/VPS/actions/runs/42383796195): importação OpenPencil gerou artefactos, mas não demonstrou navegação nem responsividade.
- [VPS Ferrari #42403761015](https://github.com/martaxi-boss/VPS/actions/runs/42403761015): formato JSON de idiomas registado, mas não validou a deteção geográfica no site vivo.
- [VPS Ferrari #42478910347](https://github.com/martaxi-boss/VPS/actions/runs/42478910347): `ruflo-host` criou papéis/tarefas, executou jq e REA, mas o revisor REA apenas consultou definições, não examinou o ficheiro do programador.
- [VPS Ferrari #42478886941](https://github.com/martaxi-boss/VPS/actions/runs/42478886941): inventário real do catálogo único: 173 programas, 272 interfaces, 3 dependências, 2 fornecedores; instalação ≠ integração ≠ prova de cada função.

## Mudanças na branch de correção

- `engine/quality_gate.py`: aceitação tipada `required_extensions`, `audible_audio` e `browser_evidence`; FFmpeg/ffprobe exclusivamente privados; assinatura PDF/PNG/MP4; material de teste de navegador desktop/móvel. Energia sonora não comprova voz natural, screenshots não provam funcionalidade.
- `engine/skill_job.py`: inclui `quality_gate` no relatório, reprova explicitamente pedidos que falhem os requisitos definidos; ausência de critérios tem estado `not_certified`, não afirma conclusão editorial.
- `engine/ruflo_host.py`: revisão `kind=review` vinculada ao `input_from` de uma tarefa executada, com resumo técnico e SHA-256 do conteúdo verificado. Um papel `reviewer` sem revisão validada continua classificado como registo técnico, não validação funcional. Raciocínio crítico por agentes continua a ser conduzido por uma única IA anfitriã via `kind=ruflo-team` e revisão de papel distinto.
- `engine/tool_runtime.py`: snapshots `INSTALLED_*` recebem `historical_installation_snapshot`, `live_revalidated=false`; não são inventários de executabilidade atual.
- `tests/test_quality_gate.py`: regressões automatizadas para silêncio, áudio presente, artefacto de formato errado, verificação browser e revisão do resultado anterior.
- Correção da identidade do ZIP do plugin: `motor-universal-linux` v1.0.8, mantendo a identidade da instalação existente v1.0.7. Não criar segundo plugin nem alterar a arquitetura do Ferrari.

## Gates necessários antes de afirmar produção atualizada

1. CI do branch candidato e verificação de conteúdo dos ZIPs — PASS.
2. Merge protegido e fixação do commit exato do novo código.
3. Pré-teste de release na VPS pelo mecanismo GitHub Actions já existente, sem APT global, alterações a outras pastas nem novo SSH.
4. Ativação protegida com fallback e verificação de 8/8 serviços.
5. Atualização exata do `ref` do validador da ponte atual para o novo SHA; sem mexer no transporte de SSH.
6. Novo pedido sintético `acceptance` da Skill real → VPS → `response.zip`, demonstrando aceitação e rejeição correta de um resultado.
7. Atualização **in-place** da Skill ChatGPT, com readback do conteúdo e versão instalada.

**Limites:** teste de áudio audível não certifica locução de qualidade nem áudio correto; a IA anfitriã deve ouvir/ver, testar interface, factos comerciais, permissões e objetivos reais. Os 173 programas/272 interfaces não podem ser declarados 100% certificados. Os processos Ruflo não invocam modelos autónomos na VPS: zero chamadas LLM independentes, conforme contrato BOOTSTRAP.
